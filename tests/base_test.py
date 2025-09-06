"""测试基类"""
import pytest
import allure
from abc import ABC
from datetime import datetime
from typing import Optional, Dict, Any
from playwright.sync_api import Page, BrowserContext
# from loguru import logger

from config.env_config import config_manager
from utils.screenshot_helper import ScreenshotHelper
from utils.video_helper import VideoHelper
from utils.logger_config import logger_config


class BaseTest(ABC):
    """测试基类"""
    
    def setup_method(self, method):
        """
        测试方法前置操作
        
        Args:
            method: 测试方法
        """
        self.test_name = method.__name__
        self.test_start_time = datetime.now()
        
        # 记录测试开始
        print(f"开始测试: {self.test_name}")
        
        # Allure 测试信息
        allure.dynamic.title(self.test_name)
        allure.dynamic.description(f"测试方法: {self.test_name}")
    
    def teardown_method(self, method):
        """
        测试方法后置操作
        
        Args:
            method: 测试方法
        """
        # 计算测试执行时间
        duration = (datetime.now() - self.test_start_time).total_seconds()
        
        # 记录测试结束
        test_result = "PASSED"  # 默认通过，失败会在异常处理中更新
        print(f"测试完成: {self.test_name}, 结果: {test_result}, 耗时: {duration}秒")
    
    @pytest.fixture(autouse=True)
    def setup_test_context(self, page: Page, context: BrowserContext):
        """
        设置测试上下文
        
        Args:
            page: Playwright 页面实例
            context: Playwright 浏览器上下文
        """
        self.page = page
        self.context = context
        
        # 获取当前会话目录
        import os
        session_dir = os.environ.get('PYTEST_SESSION_DIR', 'reports')
        
        # 使用会话目录创建Helper实例
        self.screenshot_helper = ScreenshotHelper(page, f"{session_dir}/screenshots")
        self.video_helper = VideoHelper(context, f"{session_dir}/videos")
        
        # 设置页面基础配置
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        # 添加控制台日志监听
        self.page.on("console", self._handle_console_message)
        
        # 添加页面错误监听
        self.page.on("pageerror", self._handle_page_error)
    
    def _handle_console_message(self, msg):
        """
        处理浏览器控制台消息
        
        Args:
            msg: 控制台消息
        """
        if msg.type == "error":
            print(f"浏览器控制台错误: {msg.text}")
        elif msg.type == "warning":
            print(f"浏览器控制台警告: {msg.text}")
        else:
            print(f"浏览器控制台: [{msg.type}] {msg.text}")
    
    def _handle_page_error(self, error):
        """
        处理页面错误
        
        Args:
            error: 页面错误
        """
        print(f"页面错误: {error}")
        
        # 截图记录错误
        self.take_screenshot("page_error", f"页面错误: {str(error)[:100]}")
    
    def navigate_to(self, url: str, wait_until: str = "domcontentloaded") -> None:
        """
        导航到指定 URL
        
        Args:
            url: 目标 URL
            wait_until: 等待条件
        """
        with allure.step(f"导航到: {url}"):
            logger_config.log_step("导航到页面", {"url": url})
            
            try:
                self.page.goto(url, wait_until=wait_until, timeout=30000)
                print(f"成功导航到: {url}")
            except Exception as e:
                print(f"导航失败: {url}, 错误: {str(e)}")
                self.take_screenshot("navigation_failed")
                raise
    
    def take_screenshot(self, name: str = None, description: str = "") -> Optional[str]:
        """
        截取屏幕截图
        
        Args:
            name: 截图名称
            description: 截图描述
            
        Returns:
            截图文件路径
        """
        if not name:
            name = f"{self.test_name}_{datetime.now().strftime('%H%M%S')}"
        
        screenshot_path = self.screenshot_helper.take_screenshot(name, description)
        
        # 添加到 Allure 报告
        if screenshot_path:
            try:
                with open(screenshot_path, 'rb') as f:
                    allure.attach(
                        f.read(),
                        name=f"截图_{name}",
                        attachment_type=allure.attachment_type.PNG
                    )
            except Exception as e:
                print(f"添加截图到 Allure 报告失败: {str(e)}")
        
        return screenshot_path
    
    def assert_element_visible(self, selector: str, timeout: int = 10000, message: str = "") -> None:
        """
        断言元素可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
            message: 自定义错误消息
        """
        with allure.step(f"断言元素可见: {selector}"):
            try:
                element = self.page.locator(selector)
                element.wait_for(state="visible", timeout=timeout)
                
                logger_config.log_assertion(f"元素可见: {selector}", True)
                print(f"✅ 元素可见断言通过: {selector}")
                
            except Exception as e:
                error_msg = message or f"元素不可见: {selector}"
                logger_config.log_assertion(f"元素可见: {selector}", False, str(e), "元素可见")
                
                # 失败截图
                self.take_screenshot("assertion_failed", error_msg)
                
                pytest.fail(f"{error_msg}. 错误: {str(e)}")
    
    def assert_element_not_visible(self, selector: str, timeout: int = 3000, message: str = "") -> None:
        """
        断言元素不可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
            message: 自定义错误消息
        """
        with allure.step(f"断言元素不可见: {selector}"):
            try:
                element = self.page.locator(selector)
                element.wait_for(state="hidden", timeout=timeout)
                
                logger_config.log_assertion(f"元素不可见: {selector}", True)
                print(f"✅ 元素不可见断言通过: {selector}")
                
            except Exception as e:
                error_msg = message or f"元素仍然可见: {selector}"
                logger_config.log_assertion(f"元素不可见: {selector}", False, str(e), "元素不可见")
                
                # 失败截图
                self.take_screenshot("assertion_failed", error_msg)
                
                pytest.fail(f"{error_msg}. 错误: {str(e)}")
    
    def assert_text_present(self, selector: str, expected_text: str, timeout: int = 10000, message: str = "") -> None:
        """
        断言文本存在
        
        Args:
            selector: 元素选择器
            expected_text: 期望文本
            timeout: 超时时间
            message: 自定义错误消息
        """
        with allure.step(f"断言文本存在: {selector} 包含 '{expected_text}'"):
            try:
                element = self.page.locator(selector)
                element.wait_for(state="visible", timeout=timeout)
                
                actual_text = element.text_content()
                
                if expected_text in actual_text:
                    logger_config.log_assertion(
                        f"文本包含检查: {selector}",
                        True,
                        actual_text,
                        expected_text
                    )
                    print(f"✅ 文本存在断言通过: '{expected_text}' 在 {selector}")
                else:
                    raise AssertionError(f"期望文本 '{expected_text}' 不在实际文本 '{actual_text}' 中")
                
            except Exception as e:
                error_msg = message or f"文本 '{expected_text}' 不存在于 {selector}"
                logger_config.log_assertion(
                    f"文本包含检查: {selector}",
                    False,
                    str(e),
                    expected_text
                )
                
                # 失败截图
                self.take_screenshot("assertion_failed", error_msg)
                
                pytest.fail(f"{error_msg}. 错误: {str(e)}")
    
    def assert_url_contains(self, expected_url_part: str, message: str = "") -> None:
        """
        断言 URL 包含指定内容
        
        Args:
            expected_url_part: 期望的 URL 部分
            message: 自定义错误消息
        """
        with allure.step(f"断言 URL 包含: {expected_url_part}"):
            current_url = self.page.url
            
            if expected_url_part in current_url:
                logger_config.log_assertion(
                    "URL 包含检查",
                    True,
                    current_url,
                    expected_url_part
                )
                print(f"✅ URL 包含断言通过: '{expected_url_part}' 在 {current_url}")
            else:
                error_msg = message or f"URL 不包含 '{expected_url_part}'"
                logger_config.log_assertion(
                    "URL 包含检查",
                    False,
                    current_url,
                    expected_url_part
                )
                
                # 失败截图
                self.take_screenshot("assertion_failed", error_msg)
                
                pytest.fail(f"{error_msg}. 当前 URL: {current_url}")
    
    def assert_title_contains(self, expected_title_part: str, message: str = "") -> None:
        """
        断言页面标题包含指定内容
        
        Args:
            expected_title_part: 期望的标题部分
            message: 自定义错误消息
        """
        with allure.step(f"断言标题包含: {expected_title_part}"):
            current_title = self.page.title()
            
            if expected_title_part in current_title:
                logger_config.log_assertion(
                    "标题包含检查",
                    True,
                    current_title,
                    expected_title_part
                )
                print(f"✅ 标题包含断言通过: '{expected_title_part}' 在 {current_title}")
            else:
                error_msg = message or f"标题不包含 '{expected_title_part}'"
                logger_config.log_assertion(
                    "标题包含检查",
                    False,
                    current_title,
                    expected_title_part
                )
                
                # 失败截图
                self.take_screenshot("assertion_failed", error_msg)
                
                pytest.fail(f"{error_msg}. 当前标题: {current_title}")
    
    def wait_for_element(self, selector: str, state: str = "visible", timeout: int = 10000) -> None:
        """
        等待元素状态
        
        Args:
            selector: 元素选择器
            state: 等待状态
            timeout: 超时时间
        """
        with allure.step(f"等待元素 {state}: {selector}"):
            try:
                element = self.page.locator(selector)
                element.wait_for(state=state, timeout=timeout)
                print(f"元素状态满足: {selector} - {state}")
            except Exception as e:
                print(f"等待元素失败: {selector} - {state}, 错误: {str(e)}")
                self.take_screenshot("wait_failed")
                raise
    
    def click_element(self, selector: str, timeout: int = 10000) -> None:
        """
        点击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
        """
        with allure.step(f"点击元素: {selector}"):
            try:
                element = self.page.locator(selector)
                element.wait_for(state="visible", timeout=timeout)
                element.click(timeout=timeout)
                print(f"成功点击元素: {selector}")
            except Exception as e:
                print(f"点击元素失败: {selector}, 错误: {str(e)}")
                self.take_screenshot("click_failed")
                raise
    
    def fill_input(self, selector: str, value: str, timeout: int = 10000) -> None:
        """
        填充输入框
        
        Args:
            selector: 元素选择器
            value: 输入值
            timeout: 超时时间
        """
        with allure.step(f"填充输入框: {selector} = '{value}'"):
            try:
                element = self.page.locator(selector)
                element.wait_for(state="visible", timeout=timeout)
                element.clear()
                element.fill(value)
                print(f"成功填充输入框: {selector} = '{value}'")
            except Exception as e:
                print(f"填充输入框失败: {selector}, 错误: {str(e)}")
                self.take_screenshot("fill_failed")
                raise
    
    def get_element_text(self, selector: str, timeout: int = 10000) -> str:
        """
        获取元素文本
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
            
        Returns:
            元素文本
        """
        with allure.step(f"获取元素文本: {selector}"):
            try:
                element = self.page.locator(selector)
                element.wait_for(state="visible", timeout=timeout)
                text = element.text_content() or ""
                print(f"获取元素文本: {selector} = '{text}'")
                return text
            except Exception as e:
                print(f"获取元素文本失败: {selector}, 错误: {str(e)}")
                self.take_screenshot("get_text_failed")
                raise
    
    def add_allure_step(self, step_name: str, step_data: Dict[str, Any] = None) -> None:
        """
        添加 Allure 测试步骤
        
        Args:
            step_name: 步骤名称
            step_data: 步骤数据
        """
        with allure.step(step_name):
            logger_config.log_step(step_name, step_data)
            
            if step_data:
                for key, value in step_data.items():
                    allure.attach(
                        str(value),
                        name=key,
                        attachment_type=allure.attachment_type.TEXT
                    )
    
    def add_allure_attachment(self, content: str, name: str, attachment_type=allure.attachment_type.TEXT) -> None:
        """
        添加 Allure 附件
        
        Args:
            content: 附件内容
            name: 附件名称
            attachment_type: 附件类型
        """
        try:
            allure.attach(content, name=name, attachment_type=attachment_type)
        except Exception as e:
            print(f"添加 Allure 附件失败: {str(e)}")