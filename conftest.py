"""简化的Pytest全局配置和Fixture定义"""
import pytest
import sys
import os
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Playwright, Browser, BrowserContext, Page
import allure

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 常量定义
REPORTS_DIR = Path('reports')

from config.env_config import config_manager, PLAYWRIGHT_CONFIG
from utils.logger_config import logger_config
from utils.screenshot_helper import ScreenshotHelper
from utils.video_helper import VideoHelper

# 初始化日志配置
logger_config.setup_logger(
    level="INFO",
    console_output=True,
    file_output=True
)


def pytest_configure(config):
    """pytest配置钩子 - 在测试运行前设置报告目录"""
    # 创建报告目录
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / 'allure-results').mkdir(exist_ok=True)
    (REPORTS_DIR / 'screenshots').mkdir(exist_ok=True)
    (REPORTS_DIR / 'videos').mkdir(exist_ok=True)
    
    # 设置Allure报告目录
    allure_results_dir = str(REPORTS_DIR / 'allure-results')
    if not hasattr(config.option, 'alluredir') or not config.option.alluredir:
        config.option.alluredir = allure_results_dir
    
    print(f"测试开始时间: {datetime.now()}")
    print(f"报告目录: {REPORTS_DIR}")


def pytest_unconfigure(config):
    """Pytest清理钩子"""
    print(f"测试结束时间: {datetime.now()}")


@pytest.fixture(scope="session")
def playwright():
    """Playwright实例Fixture"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright: Playwright):
    """浏览器实例Fixture"""
    browser_type = getattr(playwright, PLAYWRIGHT_CONFIG['default_browser'])
    browser = browser_type.launch(**PLAYWRIGHT_CONFIG['browser_config'])
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser):
    """浏览器上下文Fixture"""
    context_config = PLAYWRIGHT_CONFIG['context_config'].copy()
    
    # 根据配置决定是否启用视频录制
    if config_manager.config.video_record:
        context_config['record_video_dir'] = str(REPORTS_DIR / 'videos')
    
    context = browser.new_context(**context_config)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext):
    """页面实例Fixture"""
    page = context.new_page()
    
    # 设置页面超时
    page.set_default_navigation_timeout(PLAYWRIGHT_CONFIG['page_config']['default_navigation_timeout'])
    page.set_default_timeout(PLAYWRIGHT_CONFIG['page_config']['default_timeout'])
    
    yield page
    page.close()


@pytest.fixture(scope="function")
def screenshot_helper(page: Page):
    """截图助手Fixture"""
    return ScreenshotHelper(page, str(REPORTS_DIR / "screenshots"))


@pytest.fixture(scope="function")
def video_helper():
    """视频助手Fixture"""
    return VideoHelper(str(REPORTS_DIR / "videos"))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试报告钩子 - 处理失败截图和视频"""
    outcome = yield
    rep = outcome.get_result()
    # 将各阶段测试结果对象保存到 item，供其他钩子/fin 函数使用
    try:
        setattr(item, f"rep_{rep.when}", rep)
    except Exception:
        pass
    
    if rep.when == "call":
        page = _get_page_from_item(item)
        
        if rep.failed and page and not page.is_closed():
            # 失败截图
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_filename = f"failed_{item.name}_{timestamp}.png"
                screenshot_path = REPORTS_DIR / 'screenshots' / screenshot_filename
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                
                page.screenshot(path=screenshot_path, timeout=3000)
                print(f"失败截图已保存: {screenshot_path}")
                
                # 添加到Allure报告
                try:
                    allure.attach.file(screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
                except Exception:
                    pass
                    
            except Exception as e:
                print(f"截图失败: {e}")
            
            # 标记视频需要保留
            if hasattr(page, 'video') and page.video:
                item._video_for_allure = True
        
        elif not rep.failed and page and hasattr(page, 'video') and page.video:
            # 测试通过时标记视频待删除
            item._video_should_be_deleted = True


def _get_page_from_item(item):
    """从测试项中获取页面对象"""
    if hasattr(item, 'funcargs'):
        return item.funcargs.get('page')
    return None


@pytest.fixture(autouse=True)
def test_logger(request):
    """自动记录测试开始和结束"""
    test_name = request.node.name
    
    # 记录测试开始
    logger_config.log_test_start(test_name)
    
    def fin():
        # 记录测试结束
        test_result = "PASSED"
        if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
            test_result = "FAILED"
        elif hasattr(request.node, 'rep_call') and request.node.rep_call.skipped:
            test_result = "SKIPPED"
            
        logger_config.log_test_end(test_name, test_result)
        
        # 处理视频
        page = _get_page_from_item(request.node)
        if page:
            video_helper = VideoHelper(str(REPORTS_DIR / "videos"))
            
            # 处理失败测试的视频
            if hasattr(request.node, '_video_for_allure') and request.node._video_for_allure:
                try:
                    video_path = video_helper.save_failure_video(page, test_name)
                    if video_path:
                        # 添加到Allure报告
                        try:
                            with open(video_path, 'rb') as video_file:
                                allure.attach(
                                    video_file.read(),
                                    name=f"失败测试视频_{test_name}",
                                    attachment_type=allure.attachment_type.WEBM
                                )
                        except Exception:
                            pass
                except Exception as e:
                    print(f"视频处理失败: {e}")
            
            # 清理通过测试的视频
            elif hasattr(request.node, '_video_should_be_deleted') and request.node._video_should_be_deleted:
                try:
                    video_helper.cleanup_passed_video(page)
                except Exception as e:
                    print(f"视频清理失败: {e}")
    
    request.addfinalizer(fin)