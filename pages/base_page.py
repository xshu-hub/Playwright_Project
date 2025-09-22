"""页面对象模型基类

提供Web自动化测试的基础功能：
1. 页面导航和等待
2. 元素定位和操作
3. 数据输入和验证
4. 截图和日志记录
5. 异常处理和重试机制
"""
import time
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union, Callable, Literal
from playwright.sync_api import Page, Locator, expect, Error, Cookie, ViewportSize, FrameLocator

# 定义选择器类型
SelectorType = Union[str, Locator]
from loguru import logger

from utils.screenshot_helper import ScreenshotHelper
from utils.logger_config import logger_config


class BasePage(ABC):
    """页面对象模型基类"""
    
    def __init__(self, page: Page):
        """
        初始化基础页面
        
        Args:
            page: Playwright 页面实例
        """
        self.page = page
        
        # 使用固定的reports目录创建ScreenshotHelper实例
        self.screenshot_helper = ScreenshotHelper(page, "reports/screenshots")
        self.timeout = 10000  # 默认超时时间 10 秒
        self.short_timeout = 3000  # 短超时时间 3 秒
        self.long_timeout = 30000  # 长超时时间 30 秒
    
    @property
    @abstractmethod
    def url(self) -> str:
        """页面 URL"""
        pass
    
    @property
    @abstractmethod
    def title(self) -> str:
        """页面标题"""
        pass
    
    def navigate(self, url: Optional[str] = None, wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "domcontentloaded") -> 'BasePage':
        """
        导航到页面
        
        Args:
            url: 目标 URL，如果为空则使用页面默认 URL
            wait_until: 等待条件
            
        Returns:
            页面实例
        """
        target_url = url or self.url
        logger_config.log_page_action("导航", target_url)
        
        try:
            self.page.goto(target_url, wait_until=wait_until, timeout=self.long_timeout)
            self.wait_for_page_load()
            logger.info(f"页面导航成功: {target_url}")
            return self
        except Exception as e:
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'target_url': target_url,
                'current_url': self.page.url if hasattr(self, 'page') and self.page else 'Unknown',
                'wait_until': wait_until,
                'timeout': self.long_timeout
            }
            logger.error(f"页面导航失败 [NAV_001] | 目标URL: {target_url} | 当前URL: {error_details['current_url']} | 错误类型: {error_details['error_type']} | 错误信息: {error_details['error_message']} | 等待条件: {wait_until} | 超时设置: {self.long_timeout}ms")
            self.screenshot_helper.take_failure_screenshot("navigation_failed", str(e))
            raise
    
    def wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """
        等待页面加载完成
        
        Args:
            timeout: 超时时间
        """
        timeout = timeout or self.long_timeout
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            self.page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception as e:
            logger.warning(f"等待页面加载超时: {str(e)}")
    
    def _resolve_selector(self, selector: SelectorType) -> Locator:
        """
        解析选择器，支持字符串选择器和Playwright内置选择器
        
        Args:
            selector: 元素选择器（字符串或Locator对象）
            
        Returns:
            Locator对象
        """
        if isinstance(selector, str):
            return self.page.locator(selector)
        elif isinstance(selector, Locator):
            return selector
        else:
            raise ValueError(f"不支持的选择器类型: {type(selector)}")
    
    def get_element(self, selector: SelectorType, timeout: Optional[int] = None) -> Locator:
        """
        获取页面元素
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间
            
        Returns:
            元素定位器
        """
        timeout = timeout or self.timeout
        try:
            element = self._resolve_selector(selector)
            element.wait_for(state="visible", timeout=timeout)
            return element
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'selector': selector_desc,
                'timeout': timeout,
                'current_url': self.page.url if hasattr(self, 'page') and self.page else 'Unknown'
            }
            logger.error(f"获取元素失败 [ELE_001] | 选择器: {selector_desc} | 当前URL: {error_details['current_url']} | 错误类型: {error_details['error_type']} | 错误信息: {error_details['error_message']} | 超时设置: {timeout}ms")
            raise
    
    def click(self, selector: SelectorType, timeout: Optional[int] = None, force: bool = False) -> 'BasePage':
        """
        点击元素
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间
            force: 是否强制点击
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
        logger_config.log_page_action("点击", selector_desc)
        
        try:
            element = self.get_element(selector, timeout)
            element.click(force=force, timeout=timeout)
            logger.info(f"元素点击成功: {selector_desc}")
            return self
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'selector': selector_desc,
                'timeout': timeout,
                'force': force,
                'current_url': self.page.url if hasattr(self, 'page') and self.page else 'Unknown'
            }
            logger.error(f"元素点击失败 [CLK_001] | 选择器: {selector_desc} | 当前URL: {error_details['current_url']} | 错误类型: {error_details['error_type']} | 错误信息: {error_details['error_message']} | 强制点击: {force} | 超时设置: {timeout}ms")
            self.screenshot_helper.take_failure_screenshot("click_failed", str(e))
            raise
    
    def double_click(self, selector: SelectorType, timeout: Optional[int] = None) -> 'BasePage':
        """
        双击元素
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
        logger_config.log_page_action("双击", selector_desc)
        
        try:
            element = self.get_element(selector, timeout)
            element.dblclick(timeout=timeout)
            logger.info(f"元素双击成功: {selector_desc}")
            return self
        except Exception as e:
            logger.error(f"元素双击失败: {selector_desc} | 错误: {str(e)}")
            raise
    
    def fill(self, selector: SelectorType, value: str, timeout: Optional[int] = None, clear: bool = True) -> 'BasePage':
        """
        填充输入框
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            value: 输入值
            timeout: 超时时间
            clear: 是否先清空
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
        logger_config.log_page_action("填充", selector_desc, value)
        
        try:
            element = self.get_element(selector, timeout)
            if clear:
                element.clear(timeout=timeout)
            element.fill(value, timeout=timeout)
            logger.info(f"元素填充成功: {selector_desc} = '{value}'")
            return self
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'selector': selector_desc,
                'value': value,
                'clear_first': clear_first,
                'timeout': timeout,
                'current_url': self.page.url if hasattr(self, 'page') and self.page else 'Unknown'
            }
            logger.error(f"元素填充失败 [FIL_001] | 选择器: {selector_desc} | 填充值: '{value}' | 当前URL: {error_details['current_url']} | 错误类型: {error_details['error_type']} | 错误信息: {error_details['error_message']} | 清空后填充: {clear_first} | 超时设置: {timeout}ms")
            raise
    
    def type_text(self, selector: SelectorType, text: str, delay: int = 100, timeout: Optional[int] = None) -> 'BasePage':
        """
        逐字符输入文本
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            text: 输入文本
            delay: 字符间延迟(毫秒)
            timeout: 超时时间
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
        logger_config.log_page_action("输入", selector_desc, text)
        
        try:
            element = self.get_element(selector, timeout)
            element.type(text, delay=delay, timeout=timeout)
            logger.info(f"文本输入成功: {selector_desc} = '{text}'")
            return self
        except Exception as e:
            logger.error(f"文本输入失败: {selector_desc} = '{text}' | 错误: {str(e)}")
            raise
    
    def select_option(self, selector: SelectorType, value: Union[str, List[str]], timeout: Optional[int] = None) -> 'BasePage':
        """
        选择下拉框选项
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            value: 选项值
            timeout: 超时时间
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
        logger_config.log_page_action("选择", selector_desc, str(value))
        
        try:
            element = self.get_element(selector, timeout)
            element.select_option(value, timeout=timeout)
            logger.info(f"选项选择成功: {selector_desc} = '{value}'")
            return self
        except Exception as e:
            logger.error(f"选项选择失败: {selector_desc} = '{value}' | 错误: {str(e)}")
            raise
    
    def check(self, selector: SelectorType, timeout: Optional[int] = None) -> 'BasePage':
        """
        勾选复选框或单选框
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
        logger_config.log_page_action("勾选", selector_desc)
        
        try:
            element = self.get_element(selector, timeout)
            element.check(timeout=timeout)
            logger.info(f"复选框勾选成功: {selector_desc}")
            return self
        except Exception as e:
            logger.error(f"复选框勾选失败: {selector_desc} | 错误: {str(e)}")
            raise
    
    def uncheck(self, selector: SelectorType, timeout: Optional[int] = None) -> 'BasePage':
        """
        取消勾选复选框
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
        logger_config.log_page_action("取消勾选", selector_desc)
        
        try:
            element = self.get_element(selector, timeout)
            element.uncheck(timeout=timeout)
            logger.info(f"☐ 复选框取消勾选成功: {selector_desc}")
            return self
        except Exception as e:
            logger.error(f"复选框取消勾选失败: {selector_desc} | 错误: {str(e)}")
            raise
    
    def hover(self, selector: SelectorType, timeout: Optional[int] = None) -> 'BasePage':
        """
        悬停在元素上
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
        logger_config.log_page_action("悬停", selector_desc)
        
        try:
            element = self.get_element(selector, timeout)
            element.hover(timeout=timeout)
            logger.info(f"👆 元素悬停成功: {selector_desc}")
            return self
        except Exception as e:
            logger.error(f"元素悬停失败: {selector_desc} | 错误: {str(e)}")
            raise
    
    def scroll_to(self, selector: Optional[SelectorType] = None, x: Optional[int] = None, y: Optional[int] = None) -> 'BasePage':
        """
        滚动到指定位置或元素
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            x: X 坐标
            y: Y 坐标
            
        Returns:
            页面实例
        """
        try:
            if selector:
                element = self.get_element(selector)
                element.scroll_into_view_if_needed()
                selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
                logger.debug(f"成功滚动到元素: {selector_desc}")
            elif x is not None and y is not None:
                self.page.evaluate(f"window.scrollTo({x}, {y})")
                logger.debug(f"成功滚动到坐标: ({x}, {y})")
            return self
        except Exception as e:
            logger.error(f"滚动失败, 错误: {str(e)}")
            raise
    
    def wait_for_element(self, selector: SelectorType, state: Literal["attached", "detached", "hidden", "visible"] = "visible", timeout: Optional[int] = None) -> Locator:
        """
        等待元素出现
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            state: 等待状态 (visible, hidden, attached, detached)
            timeout: 超时时间
            
        Returns:
            元素定位器
        """
        timeout = timeout or self.timeout
        try:
            element = self._resolve_selector(selector)
            element.wait_for(state=state, timeout=timeout)
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.debug(f"元素状态满足条件: {selector_desc}, 状态: {state}")
            return element
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'selector': selector_desc,
                'state': state,
                'timeout': timeout,
                'current_url': self.page.url if hasattr(self, 'page') and self.page else 'Unknown'
            }
            logger.error(f"等待元素失败 [WAI_001] | 选择器: {selector_desc} | 等待状态: {state} | 当前URL: {error_details['current_url']} | 错误类型: {error_details['error_type']} | 错误信息: {error_details['error_message']} | 超时设置: {timeout}ms")
            raise
    
    def wait_for_element_stable(self, selector: SelectorType, stable_time: int = 500, timeout: Optional[int] = None) -> Locator:
        """
        等待元素稳定(位置和大小不再变化)
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            stable_time: 稳定时间(毫秒)
            timeout: 超时时间
            
        Returns:
            元素定位器
        """
        timeout = timeout or self.timeout
        try:
            element = self._resolve_selector(selector)
            # 先等待元素可见
            element.wait_for(state="visible", timeout=timeout)
            
            # 等待元素位置稳定
            last_box = None
            stable_start = None
            
            while True:
                current_box = element.bounding_box()
                current_time = time.time() * 1000
                
                if last_box == current_box:
                    if stable_start is None:
                        stable_start = current_time
                    elif current_time - stable_start >= stable_time:
                        break
                else:
                    stable_start = None
                    last_box = current_box
                
                time.sleep(0.1)
                
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.debug(f"元素已稳定: {selector_desc}")
            return element
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"等待元素稳定失败: {selector_desc}, 错误: {str(e)}")
            raise
    
    def wait_for_text(self, selector: SelectorType, text: str, timeout: Optional[int] = None) -> bool:
        """
        等待元素包含指定文本
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            text: 期望文本
            timeout: 超时时间
            
        Returns:
            是否找到文本
        """
        timeout = timeout or self.timeout
        try:
            element = self._resolve_selector(selector)
            expect(element).to_contain_text(text, timeout=timeout)
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.debug(f"元素包含期望文本: {selector_desc}, 文本: {text}")
            return True
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"等待文本失败: {selector_desc}, 文本: {text}, 错误: {str(e)}")
            return False
    
    def get_text(self, selector: SelectorType, timeout: Optional[int] = None) -> str:
        """
        获取元素文本
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间
            
        Returns:
            元素文本
        """
        timeout = timeout or self.timeout
        try:
            element = self.get_element(selector, timeout)
            text = element.text_content()
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.info(f"📝 元素文本获取成功: {selector_desc} = '{text}'")
            return text or ""
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"元素文本获取失败: {selector_desc} | 错误: {str(e)}")
            raise
    
    def get_attribute(self, selector: SelectorType, attribute: str, timeout: Optional[int] = None) -> Optional[str]:
        """
        获取元素属性
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            attribute: 属性名
            timeout: 超时时间
            
        Returns:
            属性值
        """
        timeout = timeout or self.timeout
        try:
            element = self.get_element(selector, timeout)
            value = element.get_attribute(attribute)
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.info(f"元素属性获取成功: {selector_desc}[{attribute}] = '{value}'")
            return value
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"元素属性获取失败: {selector_desc}[{attribute}] | 错误: {str(e)}")
            raise
    
    def is_visible(self, selector: SelectorType, timeout: Optional[int] = None) -> bool:
        """
        检查元素是否可见
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间
            
        Returns:
            是否可见
        """
        timeout = timeout or self.short_timeout
        try:
            element = self._resolve_selector(selector)
            return element.is_visible(timeout=timeout)
        except (Error, TimeoutError):
            return False
    
    def is_enabled(self, selector: SelectorType, timeout: Optional[int] = None) -> bool:
        """
        检查元素是否可用
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间
            
        Returns:
            是否可用
        """
        timeout = timeout or self.short_timeout
        try:
            element = self.get_element(selector, timeout)
            return element.is_enabled(timeout=timeout)
        except (Error, TimeoutError):
            return False
    
    def get_current_url(self) -> str:
        """
        获取当前页面 URL
        
        Returns:
            当前 URL
        """
        return self.page.url
    
    def get_current_title(self) -> str:
        """
        获取当前页面标题
        
        Returns:
            当前标题
        """
        return self.page.title()
    
    def refresh(self) -> 'BasePage':
        """
        刷新页面
        
        Returns:
            页面实例
        """
        logger_config.log_page_action("刷新页面")
        try:
            self.page.reload(wait_until="domcontentloaded", timeout=self.long_timeout)
            logger.info("🔄 页面刷新成功")
            return self
        except Exception as e:
            logger.error(f"页面刷新失败: {str(e)}")
            raise
    
    def go_back(self) -> 'BasePage':
        """
        返回上一页
        
        Returns:
            页面实例
        """
        logger_config.log_page_action("返回上一页")
        try:
            self.page.go_back(wait_until="domcontentloaded", timeout=self.long_timeout)
            logger.info("返回上一页成功")
            return self
        except Exception as e:
            logger.error(f"返回上一页失败: {str(e)}")
            raise
    
    def go_forward(self) -> 'BasePage':
        """
        前进到下一页
        
        Returns:
            页面实例
        """
        logger_config.log_page_action("前进到下一页")
        try:
            self.page.go_forward(wait_until="domcontentloaded", timeout=self.long_timeout)
            logger.info("前进到下一页成功")
            return self
        except Exception as e:
            logger.error(f"前进到下一页失败: {str(e)}")
            raise
    
    def execute_script(self, script: str, *args) -> Any:
        """
        执行 JavaScript 脚本
        
        Args:
            script: JavaScript 代码
            *args: 脚本参数
            
        Returns:
            脚本执行结果
        """
        try:
            result = self.page.evaluate(script, *args)
            logger.debug(f"执行脚本成功: {script[:100]}...")
            return result
        except Exception as e:
            logger.error(f"执行脚本失败: {script[:100]}..., 错误: {str(e)}")
            raise
    
    def take_screenshot(self, filename: Optional[str] = None, description: str = "") -> Optional[str]:
        """
        截取页面截图
        
        Args:
            filename: 文件名
            description: 截图描述
            
        Returns:
            截图文件路径
        """
        return self.screenshot_helper.take_screenshot(filename, description)
    
    def wait(self, seconds: float) -> 'BasePage':
        """
        等待指定时间
        
        Args:
            seconds: 等待秒数
            
        Returns:
            页面实例
        """
        logger.debug(f"等待 {seconds} 秒")
        time.sleep(seconds)
        return self
    
    def smart_wait(self, condition_func, timeout: Optional[int] = None, poll_interval: float = 0.5) -> 'BasePage':
        """
        智能等待，基于条件函数
        
        Args:
            condition_func: 条件函数，返回True时停止等待
            timeout: 超时时间(毫秒)
            poll_interval: 轮询间隔(秒)
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        start_time = time.time() * 1000
        
        while True:
            try:
                if condition_func():
                    logger.debug("智能等待条件满足")
                    return self
            except (Error, TimeoutError, AssertionError):
                pass
            
            current_time = time.time() * 1000
            if current_time - start_time >= timeout:
                logger.error("智能等待超时")
                raise TimeoutError(f"智能等待超时: {timeout}ms")
            
            time.sleep(poll_interval)
    
    def wait_for_network_idle(self, timeout: Optional[int] = None, idle_time: int = 500) -> 'BasePage':
        """
        等待网络空闲
        
        Args:
            timeout: 超时时间
            idle_time: 空闲时间(毫秒)
            
        Returns:
            页面实例
        """
        timeout = timeout or self.long_timeout
        try:
            # 使用 idle_time 参数来等待网络空闲
            import time
            start_time = time.time() * 1000
            while (time.time() * 1000 - start_time) < timeout:
                try:
                    # 等待网络空闲状态，使用 idle_time 作为空闲判断时间
                    self.page.wait_for_load_state("networkidle", timeout=idle_time)
                    logger.debug(f"网络已空闲 (空闲时间: {idle_time}ms)")
                    return self
                except (Error, TimeoutError):
                    # 如果在 idle_time 内没有达到空闲状态，继续等待
                    time.sleep(0.1)
            logger.warning(f"等待网络空闲超时: {timeout}ms")
            return self
        except Exception as e:
            logger.warning(f"等待网络空闲超时: {str(e)}")
            return self
    
    # ==================== 增强功能方法 ====================
    
    @staticmethod
    def retry_action(action_func: Callable, max_retries: int = 3, 
                    retry_delay: float = 1.0, expected_exceptions: Optional[tuple] = None) -> Any:
        """
        重试机制执行操作
        
        Args:
            action_func: 要执行的操作函数
            max_retries: 最大重试次数
            retry_delay: 重试间隔(秒)
            expected_exceptions: 期望的异常类型元组
            
        Returns:
            操作结果
            
        Raises:
            最后一次执行的异常
        """
        if expected_exceptions is None:
            expected_exceptions = (Exception, TimeoutError, AssertionError)
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"执行操作，尝试次数: {attempt + 1}/{max_retries + 1}")
                result = action_func()
                if attempt > 0:
                    logger.info(f"操作在第 {attempt + 1} 次尝试后成功")
                return result
            except expected_exceptions as e:
                last_exception = e
                if attempt < max_retries:
                    logger.warning(f"操作失败，{retry_delay}秒后重试: {str(e)}")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"操作在 {max_retries + 1} 次尝试后仍然失败: {str(e)}")
        
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("操作失败但未捕获到异常")
    
    def wait_for_condition(self, condition_func: Callable[[], bool], 
                          timeout: Optional[int] = None, poll_interval: float = 0.5,
                          error_message: str = "条件等待超时") -> 'BasePage':
        """
        等待条件满足
        
        Args:
            condition_func: 条件检查函数，返回True时停止等待
            timeout: 超时时间(毫秒)
            poll_interval: 轮询间隔(秒)
            error_message: 超时错误消息
            
        Returns:
            页面实例
            
        Raises:
            TimeoutError: 等待超时
        """
        timeout = timeout or self.timeout
        start_time = time.time() * 1000
        
        while True:
            try:
                if condition_func():
                    logger.debug("等待条件已满足")
                    return self
            except Exception as e:
                logger.debug(f"条件检查异常: {str(e)}")
            
            current_time = time.time() * 1000
            if current_time - start_time >= timeout:
                logger.error(f"等待条件超时: {error_message}")
                raise TimeoutError(f"{error_message} (超时: {timeout}ms)")
            
            time.sleep(poll_interval)
    
    def get_elements(self, selector: SelectorType, timeout: Optional[int] = None) -> List[Locator]:
        """
        获取多个元素
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间(毫秒)
            
        Returns:
            元素列表
        """
        timeout = timeout or self.timeout
        try:
            locator = self._resolve_selector(selector)
            # 等待至少一个元素出现
            locator.first.wait_for(state="attached", timeout=timeout)
            elements = locator.all()
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.debug(f"找到 {len(elements)} 个元素: {selector_desc}")
            return elements
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"获取元素列表失败 {selector_desc}: {str(e)}")
            return []
    
    def get_elements_count(self, selector: SelectorType, timeout: Optional[int] = None) -> int:
        """
        获取元素数量
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间(毫秒)
            
        Returns:
            元素数量
        """
        timeout = timeout or self.timeout
        try:
            locator = self._resolve_selector(selector)
            # 使用 timeout 参数等待至少一个元素出现，然后获取数量
            try:
                locator.first.wait_for(state="attached", timeout=timeout)
            except (Error, TimeoutError):
                # 如果没有元素，返回 0
                pass
            count = locator.count()
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.debug(f"元素数量 {selector_desc}: {count}")
            return count
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"获取元素数量失败 {selector_desc}: {str(e)}")
            return 0
    
    def wait_for_element_count(self, selector: SelectorType, expected_count: int, 
                              timeout: Optional[int] = None) -> 'BasePage':
        """
        等待元素数量达到期望值
        
        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            expected_count: 期望的元素数量
            timeout: 超时时间(毫秒)
            
        Returns:
            页面实例
        """
        def check_count():
            return self.get_elements_count(selector) == expected_count
        
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
        self.wait_for_condition(
            check_count, 
            timeout, 
            error_message=f"等待元素数量 {selector_desc} 达到 {expected_count}"
        )
        return self
    
    def drag_and_drop(self, source_selector: SelectorType, target_selector: SelectorType, 
                     timeout: Optional[int] = None) -> 'BasePage':
        """
        拖拽操作
        
        Args:
            source_selector: 源元素选择器（字符串或Playwright内置选择器）
            target_selector: 目标元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间(毫秒)
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        try:
            source = self.get_element(source_selector, timeout)
            target = self.get_element(target_selector, timeout)
            
            source_desc = str(source_selector) if isinstance(source_selector, str) else f"Locator({source_selector})"
            target_desc = str(target_selector) if isinstance(target_selector, str) else f"Locator({target_selector})"
            logger.info(f"拖拽元素: {source_desc} -> {target_desc}")
            source.drag_to(target)
            
            return self
        except Exception as e:
            logger.error(f"拖拽操作失败: {str(e)}")
            self.take_screenshot(f"drag_drop_error_{int(time.time())}")
            raise
    
    def upload_file(self, selector: SelectorType, file_path: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        文件上传
        
        Args:
            selector: 文件输入框选择器（字符串或Playwright内置选择器）
            file_path: 文件路径
            timeout: 超时时间(毫秒)
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        try:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.info(f"上传文件: {file_path} 到 {selector_desc}")
            element = self.get_element(selector, timeout)
            element.set_input_files(file_path)
            
            return self
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            self.take_screenshot(f"upload_error_{int(time.time())}")
            raise
    
    def switch_to_frame(self, frame_selector: SelectorType, timeout: Optional[int] = None) -> FrameLocator:
        """
        切换到iframe
        
        Args:
            frame_selector: iframe选择器（字符串或Playwright内置选择器）
            timeout: 超时时间(毫秒)
            
        Returns:
            iframe页面对象
        """
        timeout = timeout or self.timeout
        try:
            selector_desc = str(frame_selector) if isinstance(frame_selector, str) else f"Locator({frame_selector})"
            logger.info(f"切换到iframe: {selector_desc}")
            
            # 先等待iframe元素可见
            self.wait_for_element(frame_selector, timeout=timeout)
            
            # 使用page.frame_locator来获取frame
            if isinstance(frame_selector, str):
                frame_locator = self.page.frame_locator(frame_selector)
            else:
                # 如果是Locator对象，先获取其选择器字符串
                frame_locator = self.page.frame_locator(str(frame_selector))
            
            # 返回frame的第一个frame对象
            return frame_locator.first
        except Exception as e:
            logger.error(f"切换iframe失败: {str(e)}")
            raise
    
    def get_page_source(self) -> str:
        """
        获取页面源码
        
        Returns:
            页面HTML源码
        """
        try:
            source = self.page.content()
            logger.debug(f"获取页面源码，长度: {len(source)}")
            return source
        except Exception as e:
            logger.error(f"获取页面源码失败: {str(e)}")
            return ""
    
    def clear_cookies(self) -> 'BasePage':
        """
        清除所有cookies
        
        Returns:
            页面实例
        """
        try:
            logger.info("清除所有cookies")
            self.page.context.clear_cookies()
            return self
        except Exception as e:
            logger.error(f"清除cookies失败: {str(e)}")
            return self
    
    def set_cookie(self, name: str, value: str, domain: Optional[str] = None, 
                  path: str = "/", expires: Optional[int] = None) -> 'BasePage':
        """
        设置cookie
        
        Args:
            name: cookie名称
            value: cookie值
            domain: 域名
            path: 路径
            expires: 过期时间(时间戳)
            
        Returns:
            页面实例
        """
        try:
            cookie_data: Dict[str, Any] = {
                'name': name,
                'value': value,
                'path': path
            }
            
            if domain:
                cookie_data['domain'] = domain
            if expires:
                cookie_data['expires'] = expires
            
            logger.info(f"设置cookie: {name}={value}")
            self.page.context.add_cookies([cookie_data])  # type: ignore[list-item]
            return self
        except Exception as e:
            logger.error(f"设置cookie失败: {str(e)}")
            return self
    
    def get_cookies(self) -> List[Cookie]:
        """
        获取所有cookies
        
        Returns:
            cookies列表
        """
        try:
            cookies = self.page.context.cookies()
            logger.debug(f"获取到 {len(cookies)} 个cookies")
            return cookies
        except Exception as e:
            logger.error(f"获取cookies失败: {str(e)}")
            return []
    
    def set_viewport_size(self, width: int, height: int) -> 'BasePage':
        """
        设置视口大小
        
        Args:
            width: 宽度
            height: 高度
            
        Returns:
            页面实例
        """
        try:
            logger.info(f"设置视口大小: {width}x{height}")
            self.page.set_viewport_size({"width": width, "height": height})
            return self
        except Exception as e:
            logger.error(f"设置视口大小失败: {str(e)}")
            return self
    
    def get_viewport_size(self) -> ViewportSize:
        """
        获取视口大小
        
        Returns:
            视口大小字典 {'width': int, 'height': int}
        """
        try:
            viewport = self.page.viewport_size
            logger.debug(f"当前视口大小: {viewport}")
            return viewport or {'width': 0, 'height': 0}
        except Exception as e:
            logger.error(f"获取视口大小失败: {str(e)}")
            return {'width': 0, 'height': 0}