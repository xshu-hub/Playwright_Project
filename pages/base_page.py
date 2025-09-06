"""页面对象模型基类"""
import time
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union
from playwright.sync_api import Page, Locator, expect
from loguru import logger
import allure

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
        
        # 获取当前会话目录
        import os
        session_dir = os.environ.get('PYTEST_SESSION_DIR', 'reports')
        
        # 使用会话目录创建ScreenshotHelper实例
        self.screenshot_helper = ScreenshotHelper(page, f"{session_dir}/screenshots")
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
    
    def navigate(self, url: str = None, wait_until: str = "domcontentloaded") -> 'BasePage':
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
            logger.info(f"成功导航到页面: {target_url}")
            return self
        except Exception as e:
            logger.error(f"导航到页面失败: {target_url}, 错误: {str(e)}")
            self.screenshot_helper.take_failure_screenshot("navigation_failed", str(e))
            raise
    
    def wait_for_page_load(self, timeout: int = None) -> None:
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
    
    def get_element(self, selector: str, timeout: int = None) -> Locator:
        """
        获取页面元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
            
        Returns:
            元素定位器
        """
        timeout = timeout or self.timeout
        try:
            element = self.page.locator(selector)
            element.wait_for(state="visible", timeout=timeout)
            return element
        except Exception as e:
            logger.error(f"获取元素失败: {selector}, 错误: {str(e)}")
            raise
    
    def click(self, selector: str, timeout: int = None, force: bool = False) -> 'BasePage':
        """
        点击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
            force: 是否强制点击
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        logger_config.log_page_action("点击", selector)
        
        try:
            element = self.get_element(selector, timeout)
            element.click(force=force, timeout=timeout)
            logger.debug(f"成功点击元素: {selector}")
            return self
        except Exception as e:
            logger.error(f"点击元素失败: {selector}, 错误: {str(e)}")
            self.screenshot_helper.take_failure_screenshot("click_failed", str(e))
            raise
    
    def double_click(self, selector: str, timeout: int = None) -> 'BasePage':
        """
        双击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        logger_config.log_page_action("双击", selector)
        
        try:
            element = self.get_element(selector, timeout)
            element.dblclick(timeout=timeout)
            logger.debug(f"成功双击元素: {selector}")
            return self
        except Exception as e:
            logger.error(f"双击元素失败: {selector}, 错误: {str(e)}")
            raise
    
    def fill(self, selector: str, value: str, timeout: int = None, clear: bool = True) -> 'BasePage':
        """
        填充输入框
        
        Args:
            selector: 元素选择器
            value: 输入值
            timeout: 超时时间
            clear: 是否先清空
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        logger_config.log_page_action("填充", selector, value)
        
        try:
            element = self.get_element(selector, timeout)
            if clear:
                element.clear(timeout=timeout)
            element.fill(value, timeout=timeout)
            logger.debug(f"成功填充元素: {selector}, 值: {value}")
            return self
        except Exception as e:
            logger.error(f"填充元素失败: {selector}, 值: {value}, 错误: {str(e)}")
            raise
    
    def type_text(self, selector: str, text: str, delay: int = 100, timeout: int = None) -> 'BasePage':
        """
        逐字符输入文本
        
        Args:
            selector: 元素选择器
            text: 输入文本
            delay: 字符间延迟(毫秒)
            timeout: 超时时间
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        logger_config.log_page_action("输入", selector, text)
        
        try:
            element = self.get_element(selector, timeout)
            element.type(text, delay=delay, timeout=timeout)
            logger.debug(f"成功输入文本: {selector}, 文本: {text}")
            return self
        except Exception as e:
            logger.error(f"输入文本失败: {selector}, 文本: {text}, 错误: {str(e)}")
            raise
    
    def select_option(self, selector: str, value: Union[str, List[str]], timeout: int = None) -> 'BasePage':
        """
        选择下拉框选项
        
        Args:
            selector: 元素选择器
            value: 选项值
            timeout: 超时时间
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        logger_config.log_page_action("选择", selector, str(value))
        
        try:
            element = self.get_element(selector, timeout)
            element.select_option(value, timeout=timeout)
            logger.debug(f"成功选择选项: {selector}, 值: {value}")
            return self
        except Exception as e:
            logger.error(f"选择选项失败: {selector}, 值: {value}, 错误: {str(e)}")
            raise
    
    def check(self, selector: str, timeout: int = None) -> 'BasePage':
        """
        勾选复选框或单选框
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        logger_config.log_page_action("勾选", selector)
        
        try:
            element = self.get_element(selector, timeout)
            element.check(timeout=timeout)
            logger.debug(f"成功勾选元素: {selector}")
            return self
        except Exception as e:
            logger.error(f"勾选元素失败: {selector}, 错误: {str(e)}")
            raise
    
    def uncheck(self, selector: str, timeout: int = None) -> 'BasePage':
        """
        取消勾选复选框
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        logger_config.log_page_action("取消勾选", selector)
        
        try:
            element = self.get_element(selector, timeout)
            element.uncheck(timeout=timeout)
            logger.debug(f"成功取消勾选元素: {selector}")
            return self
        except Exception as e:
            logger.error(f"取消勾选元素失败: {selector}, 错误: {str(e)}")
            raise
    
    def hover(self, selector: str, timeout: int = None) -> 'BasePage':
        """
        悬停在元素上
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
            
        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        logger_config.log_page_action("悬停", selector)
        
        try:
            element = self.get_element(selector, timeout)
            element.hover(timeout=timeout)
            logger.debug(f"成功悬停在元素: {selector}")
            return self
        except Exception as e:
            logger.error(f"悬停元素失败: {selector}, 错误: {str(e)}")
            raise
    
    def scroll_to(self, selector: str = None, x: int = None, y: int = None) -> 'BasePage':
        """
        滚动到指定位置或元素
        
        Args:
            selector: 元素选择器
            x: X 坐标
            y: Y 坐标
            
        Returns:
            页面实例
        """
        try:
            if selector:
                element = self.get_element(selector)
                element.scroll_into_view_if_needed()
                logger.debug(f"成功滚动到元素: {selector}")
            elif x is not None and y is not None:
                self.page.evaluate(f"window.scrollTo({x}, {y})")
                logger.debug(f"成功滚动到坐标: ({x}, {y})")
            return self
        except Exception as e:
            logger.error(f"滚动失败, 错误: {str(e)}")
            raise
    
    def wait_for_element(self, selector: str, state: str = "visible", timeout: int = None) -> Locator:
        """
        等待元素出现
        
        Args:
            selector: 元素选择器
            state: 等待状态 (visible, hidden, attached, detached)
            timeout: 超时时间
            
        Returns:
            元素定位器
        """
        timeout = timeout or self.timeout
        try:
            element = self.page.locator(selector)
            element.wait_for(state=state, timeout=timeout)
            logger.debug(f"元素状态满足条件: {selector}, 状态: {state}")
            return element
        except Exception as e:
            logger.error(f"等待元素失败: {selector}, 状态: {state}, 错误: {str(e)}")
            raise
    
    def wait_for_element_stable(self, selector: str, stable_time: int = 500, timeout: int = None) -> Locator:
        """
        等待元素稳定(位置和大小不再变化)
        
        Args:
            selector: 元素选择器
            stable_time: 稳定时间(毫秒)
            timeout: 超时时间
            
        Returns:
            元素定位器
        """
        timeout = timeout or self.timeout
        try:
            element = self.page.locator(selector)
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
                
            logger.debug(f"元素已稳定: {selector}")
            return element
        except Exception as e:
            logger.error(f"等待元素稳定失败: {selector}, 错误: {str(e)}")
            raise
    
    def wait_for_text(self, selector: str, text: str, timeout: int = None) -> bool:
        """
        等待元素包含指定文本
        
        Args:
            selector: 元素选择器
            text: 期望文本
            timeout: 超时时间
            
        Returns:
            是否找到文本
        """
        timeout = timeout or self.timeout
        try:
            element = self.page.locator(selector)
            expect(element).to_contain_text(text, timeout=timeout)
            logger.debug(f"元素包含期望文本: {selector}, 文本: {text}")
            return True
        except Exception as e:
            logger.error(f"等待文本失败: {selector}, 文本: {text}, 错误: {str(e)}")
            return False
    
    def get_text(self, selector: str, timeout: int = None) -> str:
        """
        获取元素文本
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
            
        Returns:
            元素文本
        """
        timeout = timeout or self.timeout
        try:
            element = self.get_element(selector, timeout)
            text = element.text_content()
            logger.debug(f"获取元素文本: {selector}, 文本: {text}")
            return text or ""
        except Exception as e:
            logger.error(f"获取元素文本失败: {selector}, 错误: {str(e)}")
            raise
    
    def get_attribute(self, selector: str, attribute: str, timeout: int = None) -> Optional[str]:
        """
        获取元素属性
        
        Args:
            selector: 元素选择器
            attribute: 属性名
            timeout: 超时时间
            
        Returns:
            属性值
        """
        timeout = timeout or self.timeout
        try:
            element = self.get_element(selector, timeout)
            value = element.get_attribute(attribute)
            logger.debug(f"获取元素属性: {selector}, 属性: {attribute}, 值: {value}")
            return value
        except Exception as e:
            logger.error(f"获取元素属性失败: {selector}, 属性: {attribute}, 错误: {str(e)}")
            raise
    
    def is_visible(self, selector: str, timeout: int = None) -> bool:
        """
        检查元素是否可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
            
        Returns:
            是否可见
        """
        timeout = timeout or self.short_timeout
        try:
            element = self.page.locator(selector)
            return element.is_visible(timeout=timeout)
        except Exception:
            return False
    
    def is_enabled(self, selector: str, timeout: int = None) -> bool:
        """
        检查元素是否可用
        
        Args:
            selector: 元素选择器
            timeout: 超时时间
            
        Returns:
            是否可用
        """
        timeout = timeout or self.short_timeout
        try:
            element = self.get_element(selector, timeout)
            return element.is_enabled()
        except Exception:
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
            logger.debug("页面刷新成功")
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
            logger.debug("返回上一页成功")
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
            logger.debug("前进到下一页成功")
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
    
    def take_screenshot(self, filename: str = None, description: str = "") -> Optional[str]:
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
    
    def smart_wait(self, condition_func, timeout: int = None, poll_interval: float = 0.5) -> 'BasePage':
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
            except Exception:
                pass
            
            current_time = time.time() * 1000
            if current_time - start_time >= timeout:
                logger.error("智能等待超时")
                raise TimeoutError(f"智能等待超时: {timeout}ms")
            
            time.sleep(poll_interval)
    
    def wait_for_network_idle(self, timeout: int = None, idle_time: int = 500) -> 'BasePage':
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
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.debug("网络已空闲")
            return self
        except Exception as e:
            logger.warning(f"等待网络空闲超时: {str(e)}")
            return self