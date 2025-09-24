"""Pytest 全局配置和 Fixture 定义"""
import pytest
import sys
import re
import time
import threading
import os
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Playwright, Browser, BrowserContext, Page
import allure
import logging

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 常量定义
REPORTS_DIR = Path('reports')

from config.env_config import config_manager, PLAYWRIGHT_CONFIG
from utils.logger_config import logger_config
from utils.screenshot_helper import ScreenshotHelper

# 预编译正则表达式以提高性能 - 支持二级目录
_SUBDIR_PATTERN = re.compile(r'(?:^|[/\\])tests[/\\]([^/\\]+(?:[/\\][^/\\]+)?)[/\\]')
_NODEID_PATTERN = re.compile(r'tests[/\\]([^/\\]+(?:[/\\][^/\\]+)?)[/\\]')

# 获取日志记录器
logger = logging.getLogger(__name__)

# 初始化日志配置
logger_config.setup_logger(
    level="INFO",
    console_output=True,
    file_output=True
)


def pytest_configure(config):
    """pytest配置钩子 - 在测试运行前设置报告目录"""
    
    # 创建固定的报告目录和子目录
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / 'allure-results').mkdir(exist_ok=True)
    (REPORTS_DIR / 'allure-report').mkdir(exist_ok=True)
    (REPORTS_DIR / 'screenshots').mkdir(exist_ok=True)
    (REPORTS_DIR / 'videos').mkdir(exist_ok=True)
    
    # 将报告目录路径存储到配置中
    config._reports_dir = REPORTS_DIR
    
    # 设置Allure报告目录
    allure_results_dir = str(REPORTS_DIR / 'allure-results')
    if not hasattr(config.option, 'allure_report_dir') or not config.option.allure_report_dir:
        config.option.allure_report_dir = allure_results_dir
    
    # 设置alluredir选项（Allure插件使用的主要配置）
    if not hasattr(config.option, 'alluredir') or not config.option.alluredir:
        config.option.alluredir = allure_results_dir
    
    # 为了兼容性，仍然添加到addopts（主要用于非并行模式）
    try:
        config.addinivalue_line('addopts', f'--alluredir={allure_results_dir}')
    except Exception as e:
        logger.warning(f"Failed to add to addopts: {e}")
    
    logger.info(f"测试开始时间: {datetime.now()}")
    logger.info(f"当前报告目录: {REPORTS_DIR}")
    logger.info(f"浏览器: {PLAYWRIGHT_CONFIG['default_browser']}")
    logger.info(f"无头模式: {PLAYWRIGHT_CONFIG['browser_config']['headless']}")
    logger.info("-" * 50)


def pytest_unconfigure(config):
    """Pytest 清理钩子"""
    _ = config  # 标记参数已知但未使用
    logger.info(f"测试结束时间: {datetime.now()}")


@pytest.fixture(scope="session")
def playwright():
    """Playwright 实例 Fixture"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright: Playwright):
    """浏览器实例 Fixture"""
    browser_type = getattr(playwright, PLAYWRIGHT_CONFIG['default_browser'])
    browser = browser_type.launch(**PLAYWRIGHT_CONFIG['browser_config'])
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser, request):
    """浏览器上下文 Fixture - 使用固定reports目录"""
    # 获取动态配置并设置视频录制路径
    context_config = PLAYWRIGHT_CONFIG['context_config'].copy()
    
    # 根据env_config.py的配置决定是否启用视频录制
    if config_manager.config.video_record:
        context_config['record_video_dir'] = str(REPORTS_DIR / 'videos')
    else:
        context_config['record_video_dir'] = None
    
    context = browser.new_context(**context_config)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext):
    """页面实例 Fixture"""
    page = context.new_page()
    
    # 设置页面配置
    page.set_default_navigation_timeout(PLAYWRIGHT_CONFIG['page_config']['default_navigation_timeout'])
    page.set_default_timeout(PLAYWRIGHT_CONFIG['page_config']['default_timeout'])
    
    yield page
    page.close()


@pytest.fixture(scope="function")
def screenshot_helper(page: Page):
    """截图助手 Fixture"""
    return ScreenshotHelper(page, str(REPORTS_DIR / "screenshots"))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试报告钩子 - 安全的失败截图和视频处理"""
    _ = call  # 标记参数已知但未使用
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        # 获取页面对象
        page = _get_page_from_item(item)
        
        if rep.failed:
            logger.error(f"测试失败: {item.nodeid}")
            
            # 安全地处理截图和视频，添加线程安全机制
            try:
                if page and hasattr(page, 'is_closed') and not page.is_closed():
                    # 快速截图 - 添加超时控制
                    try:
                        # 使用锁确保线程安全
                        screenshot_lock = getattr(pytest_runtest_makereport, '_screenshot_lock', None)
                        if screenshot_lock is None:
                            screenshot_lock = threading.Lock()
                            pytest_runtest_makereport._screenshot_lock = screenshot_lock
                        
                        with screenshot_lock:
                            start_time = time.time()
                            
                            # 生成时间戳
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            
                            # 提取测试用例名（去掉路径和类名，只保留方法名）
                            test_case_name = item.name
                            
                            # 使用新的命名格式：failed_测试用例名_时间戳
                            screenshot_filename = f"failed_{test_case_name}_{timestamp}.png"
                            screenshot_path = REPORTS_DIR / 'screenshots' / screenshot_filename
                            
                            # 确保截图目录存在
                            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            # 使用超时控制截图
                            if hasattr(page, 'screenshot'):
                                page.screenshot(path=screenshot_path, timeout=3000)  # 3秒超时
                                logger.info(f"失败截图已保存: {screenshot_path}")
                                
                                # 添加到Allure报告
                                try:
                                    allure.attach.file(screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
                                except Exception as e:
                                    logger.warning(f"Allure截图附件添加失败: {e}")
                            else:
                                logger.warning("页面对象不支持截图功能")
                                    
                            elapsed = time.time() - start_time
                            logger.debug(f"截图处理耗时: {elapsed:.2f}秒")
                        
                    except Exception as e:
                        logger.error(f"截图处理失败: {e}")
                    
                    # 视频处理 - 失败时保留视频并添加到Allure报告
                    try:
                        if hasattr(page, 'video') and page.video:
                            logger.info("测试失败，视频将被保留")
                            # 标记视频需要添加到Allure报告
                            if not hasattr(item, '_video_for_allure'):
                                item._video_for_allure = True
                                logger.info("视频将添加到Allure报告")
                    except Exception as e:
                        logger.warning(f"视频处理警告: {e}")
                        
            except Exception as e:
                logger.error(f"失败处理钩子异常: {e}")
                # 确保异常不会阻塞测试流程
                pass
        
        else:
            logger.info(f"测试通过: {item.nodeid}")
            
            # 测试通过时删除视频文件以节省空间
            try:
                if page and hasattr(page, 'video') and page.video:
                    # 标记视频为待删除（在上下文关闭后删除）
                    if not hasattr(item, '_video_should_be_deleted'):
                        item._video_should_be_deleted = True
            except Exception as e:
                logger.warning(f"视频删除标记失败: {e}")


def _get_page_from_item(item):
    """从测试项中安全获取页面对象的辅助函数"""
    if hasattr(item, 'funcargs'):
        return item.funcargs.get('page')
    return None


def _handle_video_for_allure(page, test_name, logger):
    """处理失败测试的视频并添加到Allure报告"""
    if not page or not hasattr(page, 'video') or not page.video:
        return
    
    try:
        # 等待视频文件写入完成
        time.sleep(1)
        
        video_path = page.video.path()
        if video_path and os.path.exists(video_path):
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 使用新的命名格式：failed_测试用例名_时间戳
            new_video_name = f"failed_{test_name}_{timestamp}.webm"
            video_dir = Path(video_path).parent
            new_video_path = video_dir / new_video_name
            
            # 重命名视频文件
            try:
                os.rename(video_path, new_video_path)
                logger.info(f"视频文件已重命名为: {new_video_path}")
                video_path = new_video_path
            except Exception as e:
                logger.warning(f"视频文件重命名失败，使用原名称: {e}")
            
            with open(video_path, 'rb') as video_file:
                allure.attach(
                    video_file.read(),
                    name=f"失败测试视频_{test_name}",
                    attachment_type=allure.attachment_type.WEBM
                )
            logger.info(f"视频已添加到Allure报告: {video_path}")
        else:
            logger.warning(f"视频文件不存在或路径无效: {video_path}")
    except Exception as e:
        logger.error(f"添加视频到Allure报告失败: {e}")


def _cleanup_passed_test_video(page, logger):
    """清理通过测试的视频文件"""
    if not page or not hasattr(page, 'video') or not page.video:
        return
    
    try:
        # 等待一小段时间确保视频文件已写入
        time.sleep(0.5)
        
        video_path = page.video.path()
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
            logger.info(f"已删除通过测试的视频文件: {video_path}")
        else:
            logger.debug(f"视频文件不存在，无需删除: {video_path}")
    except Exception as e:
        logger.error(f"删除视频文件失败: {e}")
@pytest.fixture(autouse=True)
def test_logger(request):
    """自动记录测试开始和结束，并处理视频清理"""
    from loguru import logger
    test_name = request.node.name
    
    # 从测试路径中动态提取子目录名称 - 使用预编译的正则表达式
    test_path = request.node.nodeid
    subdir_name = None
    
    # 使用预编译的正则表达式匹配 tests/ 后面的子目录名称
    # 支持任意命名的子目录，不限制于特定格式
    # 确保匹配的是真正的tests目录（前面是路径分隔符或开头）
    match = _SUBDIR_PATTERN.search(test_path)
    if match:
        subdir_name = match.group(1)
    
    # 设置测试上下文，让所有日志都能路由到正确的子目录
    if subdir_name:
        logger_config.set_test_context(subdir_name)
        subdir_logger = logger_config.get_subdir_logger(subdir_name)
        subdir_logger.info(f"开始执行测试: {test_name}")
    
    # 记录测试开始
    logger_config.log_test_start(test_name)
    logger.info(f"开始执行测试: {test_name}")
    
    def fin():
        # 记录测试结束
        test_result = "PASSED"
        if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
            test_result = "FAILED"
        elif hasattr(request.node, 'rep_call') and request.node.rep_call.skipped:
            test_result = "SKIPPED"
            
        # 使用子目录logger记录测试结束
        if subdir_name:
            end_subdir_logger = logger_config.get_subdir_logger(subdir_name)
            end_subdir_logger.info(f"测试执行完成: {test_name} - {test_result}")
        
        logger_config.log_test_end(test_name, test_result)
        logger.info(f"测试执行完成: {test_name}")
        
        # 清除测试上下文
        if subdir_name:
            logger_config.clear_test_context()
        
        # 获取页面对象
        page = _get_page_from_item(request.node)
        
        # 处理失败测试的视频 - 添加到Allure报告
        if hasattr(request.node, '_video_for_allure') and request.node._video_for_allure:
            try:
                _handle_video_for_allure(page, test_name, logger)
            except Exception as e:
                logger.error(f"视频Allure处理过程出错: {e}")
        
        # 清理通过测试的视频文件
        elif hasattr(request.node, '_video_should_be_deleted') and request.node._video_should_be_deleted:
            try:
                _cleanup_passed_test_video(page, logger)
            except Exception as e:
                logger.error(f"视频清理过程出错: {e}")
    
    request.addfinalizer(fin)