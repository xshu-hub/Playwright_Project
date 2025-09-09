"""测试基类

提供Web自动化测试的基础功能：
1. 浏览器和页面管理
2. 测试数据和环境配置
3. 截图和日志记录
4. 测试报告集成
5. 异常处理和清理
"""
import pytest
import allure
from abc import ABC
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from playwright.sync_api import Page, BrowserContext, expect
import json
import time
from pathlib import Path
from loguru import logger

from config.env_config import config_manager
from utils.screenshot_helper import ScreenshotHelper
from utils.video_helper import VideoHelper
from utils.logger_config import logger_config
from pages.base_page import BasePage


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
        logger.info(f"开始测试: {self.test_name}")
        
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
        logger.info(f"测试完成: {self.test_name}, 结果: {test_result}, 耗时: {duration}秒")
        
        # 保存测试执行信息
        self._save_test_execution_info(method)
        
        # 清理测试数据
        self._cleanup_test_data()
    
    def _save_test_execution_info(self, method):
        """
        保存测试执行信息
        
        Args:
            method: 测试方法
        """
        try:
            execution_info = {
                'test_name': method.__name__,
                'execution_time': datetime.now().isoformat(),
                'page_url': self.page.url if hasattr(self, 'page') and self.page else None,
                'viewport_size': self.page.viewport_size if hasattr(self, 'page') and self.page else None,
                'user_agent': self.page.evaluate('navigator.userAgent') if hasattr(self, 'page') and self.page else None
            }
            
            # 保存到Allure报告
            allure.attach(
                json.dumps(execution_info, indent=2, ensure_ascii=False),
                name="测试执行信息",
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
             logger.warning(f"保存测试执行信息失败: {str(e)}")
    
    def _cleanup_test_data(self):
        """
        清理测试数据
        """
        try:
            # 清理临时文件
            temp_dir = Path("temp")
            if temp_dir.exists():
                for file in temp_dir.glob("test_*"):
                    file.unlink()
            
            # 清理测试变量
            if hasattr(self, 'test_data'):
                delattr(self, 'test_data')
            
            # 清理自定义清理函数
            if hasattr(self, '_cleanup_functions'):
                for cleanup_func in self._cleanup_functions:
                    try:
                        cleanup_func()
                    except Exception as e:
                         logger.warning(f"执行清理函数失败: {str(e)}")
                delattr(self, '_cleanup_functions')
                
            logger.debug("测试数据清理完成")
        except Exception as e:
            logger.warning(f"清理测试数据时出错: {str(e)}")
    
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
        
        # 初始化BasePage实例
        self.base_page = BasePage(page)
        
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
            logger.error(f"浏览器控制台错误: {msg.text}")
        elif msg.type == "warning":
            logger.warning(f"浏览器控制台警告: {msg.text}")
        else:
            logger.info(f"浏览器控制台: [{msg.type}] {msg.text}")
    
    def _handle_page_error(self, error):
        """
        处理页面错误
        
        Args:
            error: 页面错误
        """
        logger.error(f"页面错误: {error}")
        
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
                logger_config.log_step("导航到页面成功", {"url": url})
            except Exception as e:
                logger_config.log_step("导航到页面失败", {"url": url, "error": str(e)})
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
                logger.warning(f"添加截图到 Allure 报告失败: {str(e)}")
        
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
                logger.info(f"✅ 元素可见断言通过: {selector}")
                
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
                logger.info(f"✅ 元素不可见断言通过: {selector}")
                
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
                    logger.info(f"✅ 文本存在断言通过: '{expected_text}' 在 {selector}")
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
                logger.info(f"✅ URL 包含断言通过: '{expected_url_part}' 在 {current_url}")
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
                logger.info(f"✅ 标题包含断言通过: '{expected_title_part}' 在 {current_title}")
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
                logger.info(f"元素状态满足: {selector} - {state}")
            except Exception as e:
                logger.error(f"等待元素失败: {selector} - {state}, 错误: {str(e)}")
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
                self.base_page.click(selector, timeout)
            except Exception as e:
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
                self.base_page.fill(selector, value, timeout)
            except Exception as e:
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
                return self.base_page.get_text(selector, timeout)
            except Exception as e:
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
            logger.error(f"添加 Allure 附件失败: {str(e)}")
    
    # ==================== 增强功能方法 ====================
    
    def add_cleanup_function(self, cleanup_func: Callable):
        """
        添加自定义清理函数
        
        Args:
            cleanup_func: 清理函数
        """
        if not hasattr(self, '_cleanup_functions'):
            self._cleanup_functions = []
            self._cleanup_functions.append(cleanup_func)
            logger.debug(f"添加清理函数: {cleanup_func.__name__}")
    
    def set_test_data(self, key: str, value: Any):
        """
        设置测试数据
        
        Args:
            key: 数据键
            value: 数据值
        """
        if not hasattr(self, 'test_data'):
            self.test_data = {}
            self.test_data[key] = value
            logger.debug(f"设置测试数据: {key} = {value}")
    
    def get_test_data(self, key: str, default: Any = None) -> Any:
        """
        获取测试数据
        
        Args:
            key: 数据键
            default: 默认值
            
        Returns:
            数据值
        """
        if not hasattr(self, 'test_data'):
            return default
        return self.test_data.get(key, default)
    
    def wait_for_page_load(self, timeout: int = 30000):
        """
        等待页面完全加载
        
        Args:
            timeout: 超时时间(毫秒)
        """
        try:
             logger.info("等待页面完全加载")
             self.page.wait_for_load_state("networkidle", timeout=timeout)
             self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
             logger.info("页面加载完成")
        except Exception as e:
             logger.warning(f"等待页面加载超时: {str(e)}")
    
    def execute_javascript(self, script: str, *args) -> Any:
        """
        执行JavaScript代码
        
        Args:
            script: JavaScript代码
            *args: 传递给脚本的参数
            
        Returns:
            执行结果
        """
        try:
             logger.debug(f"执行JavaScript: {script[:100]}...")
             result = self.page.evaluate(script, *args)
             logger.debug(f"JavaScript执行结果: {result}")
             return result
        except Exception as e:
             logger.error(f"JavaScript执行失败: {str(e)}")
             raise
    
    def scroll_to_element(self, selector: str, timeout: int = 5000):
        """
        滚动到指定元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间(毫秒)
        """
        try:
             logger.info(f"滚动到元素: {selector}")
             element = self.page.locator(selector)
             element.scroll_into_view_if_needed(timeout=timeout)
        except Exception as e:
             logger.error(f"滚动到元素失败: {str(e)}")
             raise
    
    def scroll_to_top(self):
        """
        滚动到页面顶部
        """
        try:
             logger.info("滚动到页面顶部")
             self.page.evaluate("window.scrollTo(0, 0)")
        except Exception as e:
             logger.error(f"滚动到顶部失败: {str(e)}")
    
    def scroll_to_bottom(self):
        """
        滚动到页面底部
        """
        try:
             logger.info("滚动到页面底部")
             self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        except Exception as e:
             logger.error(f"滚动到底部失败: {str(e)}")
    
    def wait_for_ajax_complete(self, timeout: int = 10000):
        """
        等待AJAX请求完成
        
        Args:
            timeout: 超时时间(毫秒)
        """
        try:
             logger.info("等待AJAX请求完成")
             self.page.wait_for_function(
                 "() => window.jQuery ? jQuery.active === 0 : true",
                 timeout=timeout
             )
             logger.info("AJAX请求已完成")
        except Exception as e:
             logger.warning(f"等待AJAX完成超时: {str(e)}")
    
    def assert_element_count(self, selector: str, expected_count: int, timeout: int = 5000, message: str = "") -> None:
        """
        断言元素数量
        
        Args:
            selector: 元素选择器
            expected_count: 期望的元素数量
            timeout: 超时时间(毫秒)
            message: 自定义错误消息
        """
        with allure.step(f"断言元素数量: {selector} = {expected_count}"):
            try:
                elements = self.page.locator(selector)
                actual_count = elements.count()
                
                if actual_count == expected_count:
                    logger_config.log_assertion(
                        f"元素数量检查: {selector}",
                        True,
                        f"期望: {expected_count}, 实际: {actual_count}",
                        expected_count
                    )
                    logger.info(f"✅ 元素数量断言通过: {selector} = {expected_count}")
                else:
                    raise AssertionError(f"元素数量不匹配: 期望 {expected_count}, 实际 {actual_count}")
                
            except Exception as e:
                error_msg = message or f"元素数量断言失败: {selector}"
                logger_config.log_assertion(
                    f"元素数量检查: {selector}",
                    False,
                    str(e),
                    expected_count
                )
                
                # 失败截图
                self.take_screenshot("assertion_failed", error_msg)
                
                pytest.fail(f"{error_msg}. 错误: {str(e)}")
    
    def assert_page_performance(self, max_load_time: float = 5.0):
        """
        断言页面性能
        
        Args:
            max_load_time: 最大加载时间(秒)
        """
        with allure.step(f"断言页面性能: 最大加载时间 {max_load_time}s"):
            try:
                # 获取页面性能指标
                performance = self.page.evaluate("""
                    () => {
                        const timing = performance.timing;
                        return {
                            loadTime: (timing.loadEventEnd - timing.navigationStart) / 1000,
                            domReady: (timing.domContentLoadedEventEnd - timing.navigationStart) / 1000,
                            firstPaint: performance.getEntriesByType('paint')[0]?.startTime / 1000 || 0
                        };
                    }
                """)
                
                load_time = performance.get('loadTime', 0)
                
                # 记录性能信息
                allure.attach(
                    json.dumps(performance, indent=2),
                    name="页面性能指标",
                    attachment_type=allure.attachment_type.JSON
                )
                
                logger.info(f"页面加载时间: {load_time:.2f}秒")
                
                # 断言性能
                if load_time <= max_load_time:
                     logger.info(f"✅ 页面性能断言通过: {load_time:.2f}s <= {max_load_time}s")
                else:
                    raise AssertionError(f"页面加载时间过长: {load_time:.2f}s > {max_load_time}s")
                
            except Exception as e:
                 logger.error(f"页面性能断言失败: {str(e)}")
                 self.take_screenshot("performance_failed")
                 raise
    
    def create_test_report_summary(self) -> Dict[str, Any]:
        """
        创建测试报告摘要
        
        Returns:
            测试报告摘要字典
        """
        try:
            summary = {
                'test_start_time': getattr(self, 'test_start_time', None),
                'test_end_time': datetime.now().isoformat(),
                'page_url': self.page.url if hasattr(self, 'page') and self.page else None,
                'viewport_size': self.page.viewport_size if hasattr(self, 'page') and self.page else None,
                'test_data': getattr(self, 'test_data', {})
            }
            
            return summary
        except Exception as e:
             logger.error(f"创建测试报告摘要失败: {str(e)}")
             return {}
    
    def attach_test_summary_to_allure(self):
        """
        将测试摘要附加到Allure报告
        """
        try:
            summary = self.create_test_report_summary()
            allure.attach(
                json.dumps(summary, indent=2, ensure_ascii=False),
                name="测试执行摘要",
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
             logger.warning(f"附加测试摘要到Allure失败: {str(e)}")