"""简化的截图助手工具"""
from pathlib import Path
from datetime import datetime
from typing import Optional
from playwright.sync_api import Page
from loguru import logger


class ScreenshotHelper:
    """简化的截图助手类"""
    
    def __init__(self, page: Page, base_path: str = "reports/screenshots"):
        """
        初始化截图助手
        
        Args:
            page: Playwright 页面实例
            base_path: 截图保存基础路径
        """
        self.page = page
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def take_screenshot(
        self,
        filename: Optional[str] = None,
        description: str = "",
        full_page: bool = True
    ) -> Optional[str]:
        """
        截取屏幕截图
        
        Args:
            filename: 文件名，如果为空则自动生成
            description: 截图描述
            full_page: 是否截取整个页面
            
        Returns:
            截图文件路径，失败返回 None
        """
        try:
            # 检查页面状态
            if hasattr(self.page, 'is_closed') and self.page.is_closed():
                logger.warning("页面已关闭，无法截图")
                return None
            
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                filename = f"screenshot_{timestamp}.png"
            
            if not filename.endswith('.png'):
                filename += '.png'
            
            # 完整文件路径
            file_path = self.base_path / filename
            
            # 截图配置
            screenshot_config = {
                'path': str(file_path),
                'full_page': full_page,
                'timeout': 30000  # 30秒超时
            }
            
            # 截图
            self.page.screenshot(**screenshot_config)
            
            # 记录日志
            desc_str = f" - {description}" if description else ""
            logger.info(f"📸 截图已保存: {file_path}{desc_str}")
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"截图失败: {str(e)}")
            return None
    
    def take_failure_screenshot(self, test_name: str, error_msg: str = "") -> Optional[str]:
        """
        截取失败测试的截图
        
        Args:
            test_name: 测试名称
            error_msg: 错误信息
            
        Returns:
            截图文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"failed_{test_name}_{timestamp}.png"
        
        description = f"测试失败截图 - {test_name}"
        if error_msg:
            description += f" - {error_msg[:100]}"  # 限制错误信息长度
        
        return self.take_screenshot(
            filename=filename,
            description=description,
            full_page=True
        )
    
    def take_element_screenshot(
        self,
        element_selector: str,
        filename: Optional[str] = None,
        description: str = ""
    ) -> Optional[str]:
        """
        截取特定元素的截图
        
        Args:
            element_selector: 元素选择器
            filename: 文件名
            description: 截图描述
            
        Returns:
            截图文件路径
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                element_name = element_selector.replace(' ', '_').replace('>', '_')
                filename = f"element_{element_name}_{timestamp}.png"
            
            if not description:
                description = f"元素截图 - {element_selector}"
            
            # 完整文件路径
            file_path = self.base_path / filename
            
            # 截取特定元素
            element = self.page.locator(element_selector)
            if element.count() > 0:
                element.wait_for(state='visible', timeout=5000)
                element.screenshot(path=str(file_path))
                
                logger.info(f"📸 元素截图已保存: {file_path} - {description}")
                return str(file_path)
            else:
                logger.warning(f"未找到元素: {element_selector}")
                return None
                
        except Exception as e:
            logger.error(f"元素截图失败: {str(e)}")
            return None


def create_screenshot_helper(page: Page, base_path: str = "reports/screenshots") -> ScreenshotHelper:
    """
    创建截图助手实例
    
    Args:
        page: Playwright 页面实例
        base_path: 截图保存基础路径
        
    Returns:
        截图助手实例
    """
    return ScreenshotHelper(page, base_path)