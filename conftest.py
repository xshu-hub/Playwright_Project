"""Pytest 全局配置和 Fixture 定义"""
import pytest
import os
import sys
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Playwright, Browser, BrowserContext, Page
import allure
# from loguru import logger

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.env_config import config_manager, PLAYWRIGHT_CONFIG
from utils.logger_config import logger_config
from utils.screenshot_helper import ScreenshotHelper
import logging

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
    
    # 固定使用reports目录
    reports_dir = Path('reports')
    
    # 创建固定的报告目录和子目录
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / 'allure-results').mkdir(exist_ok=True)
    (reports_dir / 'allure-report').mkdir(exist_ok=True)
    (reports_dir / 'screenshots').mkdir(exist_ok=True)
    (reports_dir / 'videos').mkdir(exist_ok=True)
    
    # 将报告目录路径存储到配置中
    config._reports_dir = reports_dir
    
    # 设置Allure报告目录
    allure_results_dir = str(reports_dir / 'allure-results')
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
    logger.info(f"当前报告目录: {reports_dir}")
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
    # 固定使用reports目录
    reports_dir = Path('reports')
    
    # 获取动态配置并设置视频录制路径
    context_config = PLAYWRIGHT_CONFIG['context_config'].copy()
    
    # 根据env_config.py的配置决定是否启用视频录制
    if config_manager.config.video_record:
        context_config['record_video_dir'] = str(reports_dir / 'videos')
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
    # 固定使用reports目录
    return ScreenshotHelper(page, "reports/screenshots")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试报告钩子 - 安全的失败截图和视频处理"""
    _ = call  # 标记参数已知但未使用
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        # 获取页面对象
        page = None
        if hasattr(item, 'funcargs'):
            page = item.funcargs.get('page')
        
        if rep.failed:
            logger.error(f"测试失败: {item.nodeid}")
            
            # 安全地处理截图和视频，添加线程安全机制
            try:
                if page and hasattr(page, 'is_closed') and not page.is_closed():
                    # 快速截图 - 添加超时控制
                    try:
                        import time
                        import threading
                        
                        # 使用锁确保线程安全
                        screenshot_lock = getattr(pytest_runtest_makereport, '_screenshot_lock', None)
                        if screenshot_lock is None:
                            screenshot_lock = threading.Lock()
                            pytest_runtest_makereport._screenshot_lock = screenshot_lock
                        
                        with screenshot_lock:
                            start_time = time.time()
                            
                            # 固定使用reports目录
                            reports_dir = Path('reports')
                            screenshot_path = reports_dir / 'screenshots' / f"{item.nodeid.replace('::', '_').replace('/', '_')}_failure.png"
                            
                            # 使用超时控制截图
                            if hasattr(page, 'screenshot'):
                                page.screenshot(path=screenshot_path, timeout=3000)  # 3秒超时
                                logger.info(f"失败截图已保存: {screenshot_path}")
                                
                                # 添加到Allure报告
                                try:
                                    import allure
                                    allure.attach.file(screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
                                except Exception as e:
                                    logger.warning(f"Allure截图附件添加失败: {e}")
                                    
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


@pytest.fixture(autouse=True)
def test_logger(request):
    """自动记录测试开始和结束，并处理视频清理"""
    from loguru import logger
    test_name = request.node.name
    
    # 从测试路径中动态提取子目录名称
    test_path = request.node.nodeid
    subdir_name = None
    
    # 动态获取测试子包名称
    import re
    # 匹配 tests/test_xxx/ 格式的路径
    match = re.search(r'tests[/\\](test_\w+)[/\\]', test_path)
    if match:
        subdir_name = match.group(1)
    else:
        # 如果没有匹配到子目录，尝试从文件路径中提取
        # 匹配 test_xxx.py 格式的文件名
        file_match = re.search(r'(test_\w+)\.py', test_path)
        if file_match:
            # 检查是否在tests目录的子目录中
            path_parts = test_path.replace('\\', '/').split('/')
            if 'tests' in path_parts:
                tests_index = path_parts.index('tests')
                if tests_index + 1 < len(path_parts):
                    potential_subdir = path_parts[tests_index + 1]
                    if potential_subdir.startswith('test_'):
                        subdir_name = potential_subdir
    
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
        
        # 处理失败测试的视频 - 添加到Allure报告
        if hasattr(request.node, '_video_for_allure') and request.node._video_for_allure:
            try:
                # 获取页面对象
                page = None
                if hasattr(request.node, 'funcargs'):
                    page = request.node.funcargs.get('page')
                
                if page and hasattr(page, 'video') and page.video:
                    import time
                    import os
                    
                    # 等待视频文件写入完成
                    time.sleep(1)
                    
                    try:
                        video_path = page.video.path()
                        if video_path and os.path.exists(video_path):
                            with open(video_path, 'rb') as video_file:
                                allure.attach(
                                    video_file.read(),
                                    name=f"失败测试视频_{test_name}",
                                    attachment_type=allure.attachment_type.WEBM
                                )
                            logger.info(f"视频已添加到Allure报告: {video_path}")
                    except Exception as e:
                        logger.error(f"添加视频到Allure报告失败: {e}")
                        
            except Exception as e:
                logger.error(f"视频Allure处理过程出错: {e}")
        
        # 清理通过测试的视频文件
        elif hasattr(request.node, '_video_should_be_deleted') and request.node._video_should_be_deleted:
            try:
                # 获取页面对象
                page = None
                if hasattr(request.node, 'funcargs'):
                    page = request.node.funcargs.get('page')
                
                if page and hasattr(page, 'video') and page.video:
                    import asyncio
                    import os
                    import time
                    
                    # 等待一小段时间确保视频文件已写入
                    time.sleep(0.5)
                    
                    try:
                        video_path = page.video.path()
                        if video_path and os.path.exists(video_path):
                            os.remove(video_path)
                            logger.info(f"已删除通过测试的视频文件: {video_path}")
                    except Exception as e:
                        logger.error(f"删除视频文件失败: {e}")
                        
            except Exception as e:
                logger.error(f"视频清理过程出错: {e}")
    
    request.addfinalizer(fin)