"""
基础测试类 - 将pytest fixture功能整合到unittest框架中
"""
import unittest
import os
import sys
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Playwright, Browser, BrowserContext, Page, sync_playwright
import logging
from typing import Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config import playwright_config
from utils.config import config_manager
from utils.logger_config import logger_config
from utils.screenshot_helper import ScreenshotHelper
from utils.video_helper import VideoHelper
from utils.allure_helper import allure_helper, AllureSeverity


class BaseTest(unittest.TestCase):
    """基础测试类，继承自unittest.TestCase，提供Playwright测试基础设施"""
    
    # 类级别的共享资源
    _playwright: Optional[Playwright] = None
    _browser: Optional[Browser] = None
    _session_dir: Optional[Path] = None
    
    @classmethod
    def setUpClass(cls):
        """类级别的设置，初始化Playwright和浏览器"""
        super().setUpClass()
        
        # 设置日志
        cls._setup_logging()
        
        # 创建报告目录
        cls._setup_report_directories()
        
        # 初始化Allure环境信息
        cls._setup_allure_environment()
        
        # 初始化Playwright
        cls._playwright = sync_playwright().start()
        
        # 启动浏览器
        browser_config = playwright_config.get_browser_config()
        browser_name = playwright_config.get_default_browser()
        browser_type = getattr(cls._playwright, browser_name)
        
        launch_options = {
            'headless': browser_config.get('headless', False),
            'args': browser_config.get('args', []),
            'slow_mo': browser_config.get('slow_mo', 0)
        }
        cls._browser = browser_type.launch(**launch_options)
        
        cls.logger = logging.getLogger(cls.__name__)
        cls.logger.info(f"测试类 {cls.__name__} 初始化完成")
    
    @classmethod
    def tearDownClass(cls):
        """类级别的清理，关闭浏览器和Playwright"""
        if cls._browser:
            cls._browser.close()
        if cls._playwright:
            cls._playwright.stop()
        
        cls.logger.info(f"测试类 {cls.__name__} 清理完成")
        super().tearDownClass()
    
    def setUp(self):
        """每个测试方法的初始化"""
        from loguru import logger
        self.logger = logger
        self.logger.info(f"🚀 开始测试: {self.__class__.__name__}.{self._testMethodName}")
        
        # 初始化测试失败标记
        self._test_failed = False
        
        # 创建浏览器上下文
        self.context = self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(self._session_dir / "videos") if self._session_dir else None,
            record_video_size={"width": 1920, "height": 1080}
        )
        
        # 创建页面
        self.page = self.context.new_page()
        
        # 初始化截图助手
        self.screenshot_helper = ScreenshotHelper(
            page=self.page,
            base_path="reports/screenshots"
        )
        
        # 初始化视频助手
        self.video_helper = VideoHelper(
            context=self.context,
            base_path="reports/videos"
        )
        
        # 初始化Allure助手
        self.allure_helper = allure_helper
        
        self.logger.info(f"✅ 测试环境初始化完成: {self._testMethodName}")

    def tearDown(self):
        """每个测试方法的清理"""
        # 使用测试状态标记来判断是否失败
        test_failed = getattr(self, '_test_failed', False)
        
        # 记录测试结果
        if test_failed:
            self.logger.error(f"❌ 测试失败: {self.__class__.__name__}.{self._testMethodName}")
            self._take_failure_screenshot()
            # 添加失败截图到Allure报告
            self._attach_failure_artifacts_to_allure()
        else:
            self.logger.info(f"✅ 测试成功: {self.__class__.__name__}.{self._testMethodName}")
        
        # 处理视频录制 - 必须在关闭页面之前处理
        if hasattr(self, 'video_helper'):
            if test_failed:
                # 测试失败时保存视频
                video_path = self.video_helper.save_video_on_failure(
                    self.page,
                    f"{self.__class__.__name__}_{self._testMethodName}",
                    "Test failed"
                )
                if video_path:
                    self.logger.info(f"🎥 失败测试视频已保存: {video_path}")
            # 注意：成功测试的视频清理在关闭上下文后进行
        
        # 关闭页面
        if hasattr(self, 'page') and not self.page.is_closed():
            self.page.close()
        
        # 关闭上下文
        if hasattr(self, 'context'):
            self.context.close()
        
        # 成功测试的视频清理 - 在上下文关闭后进行
        if hasattr(self, 'video_helper') and not test_failed:
            self.video_helper.cleanup_success_video(self.page)
        
        self.logger.info(f"🏁 测试方法 {self._testMethodName} 结束")
        super().tearDown()

    def run(self, result=None):
        """重写run方法以捕获测试结果和详细信息"""
        # 保存原始的addFailure和addError方法
        original_add_failure = result.addFailure if result else None
        original_add_error = result.addError if result else None
        
        def mark_test_failed(test, traceback_info, *args, **kwargs):
            self._test_failed = True
            # 记录断言失败的详细信息
            if hasattr(self, 'logger'):
                self.logger.error(f"💥 断言失败: {self.__class__.__name__}.{self._testMethodName}")
                # 提取断言错误信息
                if traceback_info and len(traceback_info) > 1:
                    error_msg = str(traceback_info[1]).strip()
                    self.logger.error(f"📝 失败原因: {error_msg}")
                    # 如果是AssertionError，记录更详细的信息
                    if "AssertionError" in str(traceback_info[1]):
                        lines = str(traceback_info[1]).split('\n')
                        for line in lines:
                            if line.strip() and not line.startswith('  File'):
                                self.logger.error(f"🔍 错误详情: {line.strip()}")
            if original_add_failure:
                return original_add_failure(test, traceback_info, *args, **kwargs)
        
        def mark_test_error(test, traceback_info, *args, **kwargs):
            self._test_failed = True
            # 记录测试错误的详细信息
            if hasattr(self, 'logger'):
                self.logger.error(f"💥 测试错误: {self.__class__.__name__}.{self._testMethodName}")
                if traceback_info and len(traceback_info) > 1:
                    error_msg = str(traceback_info[1]).strip()
                    self.logger.error(f"📝 错误原因: {error_msg}")
            if original_add_error:
                return original_add_error(test, traceback_info, *args, **kwargs)
        
        # 替换方法以捕获失败和错误
        if result:
            result.addFailure = mark_test_failed
            result.addError = mark_test_error
        
        try:
            return super().run(result)
        finally:
            # 恢复原始方法
            if result:
                if original_add_failure:
                    result.addFailure = original_add_failure
                if original_add_error:
                    result.addError = original_add_error
    
    @classmethod
    def _setup_logging(cls):
        """设置日志配置"""
        logger_config.setup_logger(
            level="INFO",
            console_output=True,
            file_output=True
        )
    
    @classmethod
    def _setup_report_directories(cls):
        """设置报告目录"""
        # 使用固定的reports目录，不再按会话分开
        test_session_dir = Path('reports')
        cls._session_dir = test_session_dir
        
        # 创建主报告目录和子目录
        test_session_dir.mkdir(parents=True, exist_ok=True)
        (test_session_dir / 'screenshots').mkdir(exist_ok=True)
        (test_session_dir / 'videos').mkdir(exist_ok=True)
        
        # 设置环境变量
        os.environ['PYTEST_SESSION_DIR'] = str(test_session_dir)
        
        logger = logging.getLogger(__name__)
        logger.info(f"📁 报告目录设置完成: {test_session_dir}")
    
    @classmethod
    def _setup_allure_environment(cls):
        """设置Allure环境信息"""
        viewport_config = config_manager.get_viewport_config()
        env_info = {
            "测试环境": config_manager.current_env.value,
            "浏览器": playwright_config.get_default_browser(),
            "无头模式": str(config_manager.is_headless()),
            "视口大小": f"{viewport_config['width']}x{viewport_config['height']}",
            "操作系统": os.name,
            "Python版本": sys.version.split()[0],
            "测试框架": "Playwright + unittest",
            "报告工具": "Allure"
        }
        
        # 生成默认测试分类
        allure_helper.generate_default_categories()
        
        # 添加环境信息
        allure_helper.add_environment_info(env_info)
        
        logger = logging.getLogger(__name__)
        logger.info("📋 Allure环境信息设置完成")
    
    def _attach_failure_artifacts_to_allure(self):
        """将失败测试的截图和视频附加到Allure报告"""
        try:
            # 添加失败截图
            screenshot_name = f"{self.__class__.__name__}_{self._testMethodName}_failure"
            screenshot_path = Path("reports/screenshots") / f"{screenshot_name}.jpg"
            if screenshot_path.exists():
                self.allure_helper.attach_screenshot(str(screenshot_path), "失败截图")
            
            # 添加失败视频（如果存在）
            video_name = f"failed_{self.__class__.__name__}_{self._testMethodName}"
            video_dir = Path("reports/videos")
            for video_file in video_dir.glob(f"{video_name}*.webm"):
                self.allure_helper.attach_video(str(video_file), "失败视频")
                break
            
            # 添加页面HTML源码
            if hasattr(self, 'page') and not self.page.is_closed():
                html_content = self.page.content()
                self.allure_helper.attach_html(html_content, "页面HTML源码")
            
            # 添加浏览器控制台日志
            if hasattr(self, 'page') and not self.page.is_closed():
                console_logs = []
                # 注意：这里需要在测试过程中收集控制台日志
                # 可以在setUp中添加监听器来收集日志
                if hasattr(self, '_console_logs'):
                    console_logs = self._console_logs
                
                if console_logs:
                    logs_text = "\n".join([f"[{log['type']}] {log['text']}" for log in console_logs])
                    self.allure_helper.attach_text(logs_text, "浏览器控制台日志")
                    
        except Exception as e:
            self.logger.error(f"添加Allure附件时发生错误: {str(e)}")
    
    def _take_failure_screenshot(self):
        """测试失败时截图"""
        try:
            if hasattr(self, 'screenshot_helper') and hasattr(self, 'page'):
                screenshot_name = f"{self.__class__.__name__}_{self._testMethodName}_failure"
                self.screenshot_helper.take_screenshot(screenshot_name)
                self.logger.info(f"失败截图已保存: {screenshot_name}")
        except Exception as e:
            self.logger.error(f"截图失败: {str(e)}")
    
    def clear_storage(self):
        """清除浏览器存储"""
        try:
            self.page.evaluate("localStorage.clear()")
            self.page.evaluate("sessionStorage.clear()")
        except Exception:
            # 如果无法访问localStorage，忽略错误
            pass
    
    def wait_for_page_load(self, timeout: int = 30000):
        """等待页面加载完成"""
        self.page.wait_for_load_state('networkidle', timeout=timeout)
    

    
    def get_session_dir(self) -> Path:
        """获取当前会话目录"""
        return self._session_dir
    
    def take_screenshot(self, name: str = None):
        """手动截图"""
        if not name:
            name = f"{self.__class__.__name__}_{self._testMethodName}"
        return self.screenshot_helper.take_screenshot(name)