"""截图助手工具"""
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable
from playwright.sync_api import Page
from loguru import logger

try:
    import allure
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False


class ScreenshotHelper:
    """截图助手类"""
    
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
        
        # 截图配置
        self.default_config = {
            'full_page': True,
            'type': 'png',
            'animations': 'disabled'
        }
    
    def take_screenshot(
        self,
        filename: Optional[str] = None,
        description: str = "",
        full_page: bool = True,
        element_selector: Optional[str] = None,
        quality: int = 80,
        attach_to_allure: bool = True,
        **kwargs
    ) -> Optional[str]:
        """
        截取屏幕截图
        
        Args:
            filename: 文件名，如果为空则自动生成
            description: 截图描述
            full_page: 是否截取整个页面
            element_selector: 元素选择器，如果提供则只截取该元素
            quality: 截图质量 (1-100)
            attach_to_allure: 是否附加到Allure报告
            **kwargs: 其他截图参数
            
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
            
            # 根据质量设置确定文件格式
            if quality < 100 and not filename.endswith(('.png', '.jpg', '.jpeg')):
                filename = filename.rsplit('.', 1)[0] + '.jpg' if '.' in filename else filename + '.jpg'
            elif not filename.endswith(('.png', '.jpg', '.jpeg')):
                filename += '.png'
            
            # 完整文件路径
            file_path = self.base_path / filename
            
            # 合并截图配置
            screenshot_config = dict(self.default_config, **kwargs)
            screenshot_config['full_page'] = full_page
            screenshot_config['path'] = str(file_path)
            
            # 设置图片质量和格式
            if quality < 100:
                screenshot_config['type'] = 'jpeg'
                screenshot_config['quality'] = quality  # 修复：使用数字而不是字符串
            
            # 添加超时设置
            if 'timeout' not in screenshot_config:
                screenshot_config['timeout'] = 30000  # 修复：使用数字而不是字符串
            
            # 截图
            if element_selector:
                # 截取特定元素
                element = self.page.locator(element_selector)
                if element.count() > 0:
                    # 等待元素可见
                    element.wait_for(state='visible', timeout=5000)
                    element.screenshot(**screenshot_config)
                else:
                    logger.warning(f"未找到元素: {element_selector}，改为截取整页")
                    self.page.screenshot(**screenshot_config)
            else:
                # 截取整页或视口
                self.page.screenshot(**screenshot_config)
            
            # 附加到Allure报告
            if attach_to_allure and ALLURE_AVAILABLE:
                try:
                    with open(file_path, 'rb') as f:
                        allure.attach(
                            f.read(),
                            name=description or f"截图 - {filename}",
                            attachment_type=allure.attachment_type.PNG
                        )
                except Exception as e:
                    logger.warning(f"附加截图到Allure失败: {e}")
            
            # 记录日志
            desc_str = f" - {description}" if description else ""
            logger.info(f"截图已保存: {file_path}{desc_str} (质量: {quality})")
            
            return str(file_path)
            
        except Exception as e:
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'page_url': self.page.url if self.page else 'Unknown',
                'filename': filename or 'auto-generated',
                'full_page': full_page,
                'quality': quality,
                'base_path': str(self.base_path)
            }
            logger.error(f"截图失败 [SCR_002] | 页面URL: {error_details['page_url']} | 文件名: {error_details['filename']} | 全页截图: {error_details['full_page']} | 质量: {error_details['quality']} | 错误类型: {error_details['error_type']} | 错误信息: {error_details['error_message']} | 保存路径: {error_details['base_path']}")
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
    
    def take_step_screenshot(self, step_name: str, step_number: int = 0) -> Optional[str]:
        """
        截取测试步骤截图
        
        Args:
            step_name: 步骤名称
            step_number: 步骤编号
            
        Returns:
            截图文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        step_prefix = f"step{step_number:02d}_" if step_number > 0 else "step_"
        filename = f"{step_prefix}{step_name}_{timestamp}.png"
        
        description = f"测试步骤截图 - {step_name}"
        
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
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            element_name = element_selector.replace(' ', '_').replace('>', '_')
            filename = f"element_{element_name}_{timestamp}.png"
        
        if not description:
            description = f"元素截图 - {element_selector}"
        
        return self.take_screenshot(
            filename=filename,
            description=description,
            element_selector=element_selector
        )
    
    def take_comparison_screenshots(
        self,
        before_action: Optional[Callable],
        after_action: Optional[Callable],
        action_name: str = "action"
    ) -> tuple[Optional[str], Optional[str]]:
        """
        截取操作前后的对比截图
        
        Args:
            before_action: 操作前的截图动作
            after_action: 操作后的截图动作
            action_name: 操作名称
            
        Returns:
            (操作前截图路径, 操作后截图路径)
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 操作前截图
        before_filename = f"before_{action_name}_{timestamp}.png"
        before_path = self.take_screenshot(
            filename=before_filename,
            description=f"操作前截图 - {action_name}"
        )
        
        # 执行操作前的动作
        if before_action:
            before_action()
        
        # 操作后截图
        after_filename = f"after_{action_name}_{timestamp}.png"
        after_path = self.take_screenshot(
            filename=after_filename,
            description=f"操作后截图 - {action_name}"
        )
        
        # 执行操作后的动作
        if after_action:
            after_action()
        
        return before_path, after_path
    
    def cleanup_old_screenshots(self, days: int = 7) -> int:
        """
        清理旧的截图文件
        
        Args:
            days: 保留天数
            
        Returns:
            删除的文件数量
        """
        try:
            current_time = datetime.now()
            deleted_count = 0
            
            for file_path in self.base_path.glob("*.png"):
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if (current_time - file_time).days > days:
                    file_path.unlink()
                    deleted_count += 1
                    logger.debug(f"删除旧截图: {file_path}")
            
            if deleted_count > 0:
                logger.info(f"清理完成，删除了 {deleted_count} 个旧截图文件")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理截图文件失败: {str(e)}")
            return 0
    
    @staticmethod
    def get_screenshot_info(file_path: str) -> dict:
        """
        获取截图文件信息
        
        Args:
            file_path: 截图文件路径
            
        Returns:
            截图信息字典
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {}
            
            stat = path.stat()
            return {
                'filename': path.name,
                'size': stat.st_size,
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'absolute_path': str(path.absolute())
            }
            
        except Exception as e:
            logger.error(f"获取截图信息失败: {str(e)}")
            return {}


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