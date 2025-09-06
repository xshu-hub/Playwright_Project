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

from config.playwright_config import PLAYWRIGHT_CONFIG
from config.env_config import config_manager
from utils.logger_config import logger_config
from utils.screenshot_helper import ScreenshotHelper

# 禁用loguru日志以避免I/O错误
# logger_config.setup_logger()


# 全局变量存储当前会话目录
current_session_dir = None

def pytest_configure(config):
    """pytest配置钩子 - 在测试运行前设置报告目录"""
    global current_session_dir
    import os
    
    # 检查是否为worker进程
    if hasattr(config, 'workerinput'):
        # Worker进程：从环境变量或最新目录获取会话目录
        session_dir_env = os.environ.get('PYTEST_SESSION_DIR')
        if session_dir_env:
            current_session_dir = Path(session_dir_env)
            config._current_session_dir = current_session_dir
            
            # 为worker进程设置Allure配置
            allure_results_dir = str(current_session_dir / 'allure-results')
            config.option.alluredir = allure_results_dir
            config.option.allure_report_dir = allure_results_dir
        else:
            # 查找最新的会话目录
            reports_dir = Path('reports')
            if reports_dir.exists():
                session_dirs = [d for d in reports_dir.iterdir() if d.is_dir() and d.name.startswith('test_session_')]
                if session_dirs:
                    current_session_dir = max(session_dirs, key=lambda x: x.stat().st_mtime)
                    config._current_session_dir = current_session_dir
                    
                    # 为worker进程设置Allure配置
                    allure_results_dir = str(current_session_dir / 'allure-results')
                    config.option.alluredir = allure_results_dir
                    config.option.allure_report_dir = allure_results_dir
        return
    
    # 生成基于时间戳的报告目录名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_session_dir = Path('reports') / f'test_session_{timestamp}'
    current_session_dir = test_session_dir
    
    # 创建主报告目录和子目录
    test_session_dir.mkdir(parents=True, exist_ok=True)
    (test_session_dir / 'allure-results').mkdir(exist_ok=True)
    (test_session_dir / 'allure-report').mkdir(exist_ok=True)
    (test_session_dir / 'screenshots').mkdir(exist_ok=True)
    (test_session_dir / 'videos').mkdir(exist_ok=True)
    (test_session_dir / 'html').mkdir(exist_ok=True)
    
    # 将当前会话目录路径存储到配置和环境变量中
    config._current_session_dir = test_session_dir
    import os
    os.environ['PYTEST_SESSION_DIR'] = str(test_session_dir)
    
    # 动态设置报告路径
    # 直接设置Allure报告目录（兼容pytest-xdist）
    allure_results_dir = str(test_session_dir / 'allure-results')
    if not hasattr(config.option, 'allure_report_dir') or not config.option.allure_report_dir:
        config.option.allure_report_dir = allure_results_dir
    
    # 设置alluredir选项（Allure插件使用的主要配置）
    if not hasattr(config.option, 'alluredir') or not config.option.alluredir:
        config.option.alluredir = allure_results_dir
    
    # 设置HTML报告路径
    html_report_path = str(test_session_dir / 'html' / 'report.html')
    if not hasattr(config.option, 'htmlpath') or not config.option.htmlpath:
        config.option.htmlpath = html_report_path
    
    # 设置self_contained_html选项
    if not hasattr(config.option, 'self_contained_html'):
        config.option.self_contained_html = True
    
    # 为了兼容性，仍然添加到addopts（主要用于非并行模式）
    try:
        config.addinivalue_line('addopts', f'--alluredir={allure_results_dir}')
        config.addinivalue_line('addopts', f'--html={html_report_path}')
        config.addinivalue_line('addopts', '--self-contained-html')
    except Exception as e:
        print(f"Warning: Failed to add to addopts: {e}")
    
    print(f"测试开始时间: {datetime.now()}")
    print(f"当前测试会话目录: {test_session_dir}")
    print(f"浏览器: {PLAYWRIGHT_CONFIG['default_browser']}")
    print(f"无头模式: {PLAYWRIGHT_CONFIG['browser_config']['headless']}")
    print("-" * 50)


def pytest_unconfigure(config):
    """Pytest 清理钩子"""
    print(f"测试结束时间: {datetime.now()}")


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
    """浏览器上下文 Fixture - 使用动态会话目录"""
    # 获取当前会话目录
    global current_session_dir
    session_dir = current_session_dir if current_session_dir else Path('reports')
    
    # 复制原始配置并更新视频录制路径
    context_config = PLAYWRIGHT_CONFIG['context_config'].copy()
    if 'record_video_dir' in context_config and context_config['record_video_dir']:
        context_config['record_video_dir'] = str(session_dir / 'videos')
    
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
    # 获取当前会话目录
    session_dir = os.environ.get('PYTEST_SESSION_DIR', 'reports')
    return ScreenshotHelper(page, f"{session_dir}/screenshots")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试报告钩子 - 安全的失败截图和视频处理"""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        # 获取页面对象
        page = None
        if hasattr(item, 'funcargs'):
            page = item.funcargs.get('page')
        
        if rep.failed:
            print(f"测试失败: {item.nodeid}")
            
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
                            
                            # 获取当前会话目录
                            global current_session_dir
                            session_dir = current_session_dir if current_session_dir else Path('reports')
                            screenshot_path = session_dir / 'screenshots' / f"{item.nodeid.replace('::', '_').replace('/', '_')}_failure.png"
                            
                            # 使用超时控制截图
                            if hasattr(page, 'screenshot'):
                                page.screenshot(path=screenshot_path, timeout=3000)  # 3秒超时
                                print(f"失败截图已保存: {screenshot_path}")
                                
                                # 添加到Allure报告
                                try:
                                    import allure
                                    allure.attach.file(screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
                                except Exception as e:
                                    print(f"Allure截图附件添加失败: {e}")
                                    
                            elapsed = time.time() - start_time
                            print(f"截图处理耗时: {elapsed:.2f}秒")
                        
                    except Exception as e:
                        print(f"截图处理失败: {e}")
                    
                    # 视频处理 - 失败时保留视频并添加到Allure报告
                    try:
                        if hasattr(page, 'video') and page.video:
                            print("测试失败，视频将被保留")
                            # 标记视频需要添加到Allure报告
                            if not hasattr(item, '_video_for_allure'):
                                item._video_for_allure = True
                                print("视频将添加到Allure报告")
                    except Exception as e:
                        print(f"视频处理警告: {e}")
                        
            except Exception as e:
                print(f"失败处理钩子异常: {e}")
                # 确保异常不会阻塞测试流程
                pass
        
        else:
            print(f"测试通过: {item.nodeid}")
            
            # 测试通过时删除视频文件以节省空间
            try:
                if page and hasattr(page, 'video') and page.video:
                    # 标记视频为待删除（在上下文关闭后删除）
                    if not hasattr(item, '_video_should_be_deleted'):
                        item._video_should_be_deleted = True
            except Exception as e:
                print(f"视频删除标记失败: {e}")


@pytest.fixture(autouse=True)
def test_logger(request):
    """自动记录测试开始和结束，并处理视频清理"""
    test_name = request.node.name
    print(f"开始执行测试: {test_name}")
    
    def fin():
        print(f"测试执行完成: {test_name}")
        
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
                            print(f"视频已添加到Allure报告: {video_path}")
                    except Exception as e:
                        print(f"添加视频到Allure报告失败: {e}")
                        
            except Exception as e:
                print(f"视频Allure处理过程出错: {e}")
        
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
                            print(f"已删除通过测试的视频文件: {video_path}")
                    except Exception as e:
                        print(f"删除视频文件失败: {e}")
                        
            except Exception as e:
                print(f"视频清理过程出错: {e}")
    
    request.addfinalizer(fin)