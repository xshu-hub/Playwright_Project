"""
基础测试类 - 使用unittest框架提供测试基础功能
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import os
import sys
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Playwright, Browser, BrowserContext, Page, sync_playwright
import logging
from typing import Optional
import allure

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config import playwright_config
from utils.config import config_manager
from utils.logger_config import logger_config
from utils.screenshot_helper import ScreenshotHelper
from utils.video_helper import VideoHelper


class BaseTest(unittest.TestCase):
    """测试基类，提供通用的测试设置和工具方法"""
    
    # 类级别的共享资源
    _playwright: Optional[Playwright] = None
    _browser: Optional[Browser] = None
    _session_dir: Optional[Path] = None
    
    @classmethod
    def setUpClass(cls):
        """类级别的初始化，启动浏览器"""
        # 设置日志
        cls._setup_logging()
        
        # 创建报告目录
        cls._setup_report_directories()
        
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
        """每个测试方法执行前的初始化"""
        with allure.step("初始化测试环境"):
            from loguru import logger
            self.logger = logger
            self.logger.info(f"开始测试: {self.__class__.__name__}.{self._testMethodName}")
            
            # 动态识别testcase子包并配置日志
            temp_config = logger_config.__class__()
            testcase_group = temp_config._get_testcase_group()
            if testcase_group:
                # 移除现有处理器
                logger.remove()
                # 为特定子包设置日志
                logger_config.setup_logger_for_group(testcase_group, file_output=True)
            else:
                # 使用默认日志配置
                logger_config.setup_logger(file_output=True)
            
            # 初始化测试失败标记
            self._test_failed = False
            
            # 创建浏览器上下文
            context_config = playwright_config.get_context_config()
            
            # 获取会话目录
            session_dir = self.get_session_dir()
            
            # 配置视频录制
            current_config = config_manager.get_config()
            if current_config.video_record:
                context_config['record_video_dir'] = str(session_dir / "videos")
                context_config['record_video_size'] = {"width": 1280, "height": 720}
            
            # 创建上下文
            self.context = self._browser.new_context(**context_config)
            
            # 创建页面
            self.page = self.context.new_page()
            
            # 初始化辅助工具
            self.screenshot_helper = ScreenshotHelper(self.page, session_dir / "screenshots")
            self.video_helper = VideoHelper(self.page, session_dir / "videos")
            
            # 记录测试开始
            test_name = f"{self.__class__.__name__}.{self._testMethodName}"
            logger_config.log_test_start(test_name)
            self.logger.info(f"测试环境初始化完成: {self._testMethodName}")

    def tearDown(self):
        """每个测试方法的清理"""
        with allure.step("清理测试环境"):
            # 使用测试状态标记来判断是否失败
            test_failed = getattr(self, '_test_failed', False)
            
            # 记录测试结果
            if test_failed:
                error_details = {
                    'test_class': self.__class__.__name__,
                    'test_method': self._testMethodName,
                    'test_full_name': f"{self.__class__.__name__}.{self._testMethodName}",
                    'browser_type': getattr(self, 'browser_type', 'Unknown'),
                    'current_url': self.page.url if hasattr(self, 'page') and self.page else 'Unknown',
                    'session_dir': str(self.get_session_dir()) if hasattr(self, 'get_session_dir') else 'Unknown'
                }
                self.logger.error(f"测试失败 [TEST_001] | 测试类: {error_details['test_class']} | 测试方法: {error_details['test_method']} | 浏览器类型: {error_details['browser_type']} | 当前URL: {error_details['current_url']} | 会话目录: {error_details['session_dir']}")
                self._take_failure_screenshot()
            else:
                self.logger.info(f"测试成功: {self.__class__.__name__}.{self._testMethodName}")
            
            # 处理视频录制 - 必须在关闭页面之前处理
            video_path = None
            if hasattr(self, 'video_helper'):
                if test_failed:
                    # 测试失败时保存视频
                    video_path = self.video_helper.save_video_on_failure(
                        self.page,
                        f"{self.__class__.__name__}_{self._testMethodName}",
                        "Test failed"
                    )
                    if video_path:
                        self.logger.info(f"失败测试视频已保存: {video_path}")
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
        
        self.logger.info(f"测试方法 {self._testMethodName} 结束")
        super().tearDown()

    def run(self, result=None):
        """重写run方法以捕获测试结果和详细信息"""
        # 保存原始的addFailure和addError方法
        original_add_failure = result.addFailure if result else None
        original_add_error = result.addError if result else None
        
        def mark_test_failed(test, traceback_info, *args, **kwargs):
            """标记测试失败"""
            test._test_failed = True
            
        # 替换result的方法以捕获失败
        if result:
            def new_add_failure(test, traceback_info):
                mark_test_failed(test, traceback_info)
                if original_add_failure:
                    original_add_failure(test, traceback_info)
                    
            def new_add_error(test, traceback_info):
                mark_test_failed(test, traceback_info)
                if original_add_error:
                    original_add_error(test, traceback_info)
            
            result.addFailure = new_add_failure
            result.addError = new_add_error
        
        try:
            # 运行测试
            super().run(result)
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
        # 不在类级别配置日志，避免生成默认的app.log和error.log
        # 日志配置将在每个测试方法的setUp中根据testcase子包动态配置
        
        # 创建类专用的logger（仅用于控制台输出）
        cls.logger = logging.getLogger(cls.__name__)
    
    @classmethod
    def _setup_report_directories(cls):
        """创建报告目录"""
        # 固定使用reports目录，不再使用动态会话目录
        cls._session_dir = Path("reports")
        
        # 创建必要的目录
        directories = [
            Path("reports/screenshots"),
            Path("reports/videos")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _take_failure_screenshot(self):
        """测试失败时截图"""
        try:
            if hasattr(self, 'screenshot_helper'):
                test_name = f"{self.__class__.__name__}_{self._testMethodName}"
                # 使用take_failure_screenshot方法，它会自动添加时间戳避免覆盖
                screenshot_path = self.screenshot_helper.take_failure_screenshot(test_name, "测试执行失败")
                if screenshot_path:
                    self.logger.info(f"失败截图已保存: {screenshot_path}")
        except Exception as e:
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'test_class': self.__class__.__name__,
                'test_method': self._testMethodName,
                'current_url': self.page.url if hasattr(self, 'page') and self.page else 'Unknown',
                'session_dir': str(self.get_session_dir()) if hasattr(self, 'get_session_dir') else 'Unknown'
            }
            self.logger.error(f"截图失败 [SCR_001] | 测试: {error_details['test_class']}.{error_details['test_method']} | 当前URL: {error_details['current_url']} | 错误类型: {error_details['error_type']} | 错误信息: {error_details['error_message']} | 会话目录: {error_details['session_dir']}")
    
    def clear_storage(self):
        """清除浏览器存储"""
        with allure.step("清除浏览器存储"):
            if hasattr(self, 'page') and self.page:
                # 清除localStorage
                self.page.evaluate("() => window.localStorage.clear()")
                # 清除sessionStorage
                self.page.evaluate("() => window.sessionStorage.clear()")
                # 清除cookies
                self.context.clear_cookies()
                self.logger.info("浏览器存储已清除")

    def wait_for_page_load(self, timeout: int = 30000):
        """等待页面加载完成"""
        with allure.step(f"等待页面加载完成 (超时: {timeout}ms)"):
            if hasattr(self, 'page') and self.page:
                self.page.wait_for_load_state('networkidle', timeout=timeout)
                self.logger.info(f"页面加载完成: {self.page.url}")

    def get_session_dir(self) -> Path:
        """获取会话目录"""
        return self._session_dir

    def take_screenshot(self, name: str = None):
        """截图"""
        with allure.step(f"截图: {name or '默认截图'}"):
            return self.screenshot_helper.take_screenshot(name)
    
    # Allure辅助方法
    @staticmethod
    def allure_step(step_name: str):
        """Allure步骤装饰器"""
        return allure.step(step_name)
    
    def attach_screenshot(self, name: str = "Screenshot"):
        """附加截图到Allure报告"""
        try:
            if hasattr(self, 'page') and self.page:
                screenshot = self.page.screenshot()
                allure.attach(
                    screenshot,
                    name=name,
                    attachment_type=allure.attachment_type.PNG
                )
                self.logger.info(f"截图已附加到Allure报告: {name}")
        except Exception as e:
            self.logger.error(f"附加截图失败: {e}")
    
    def attach_text(self, text: str, name: str = "Text"):
        """附加文本到Allure报告"""
        allure.attach(
            text,
            name=name,
            attachment_type=allure.attachment_type.TEXT
        )
    
    def attach_html(self, html: str, name: str = "HTML"):
        """附加HTML到Allure报告"""
        allure.attach(
            html,
            name=name,
            attachment_type=allure.attachment_type.HTML
        )
    
    def attach_json(self, json_data: str, name: str = "JSON"):
        """附加JSON到Allure报告"""
        allure.attach(
            json_data,
            name=name,
            attachment_type=allure.attachment_type.JSON
        )