"""截图助手工具"""
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Union, Dict, Any, Tuple
from playwright.sync_api import Page
from loguru import logger


class ScreenshotHelper:
    """截图助手类"""
    
    def __init__(self, page: Page, base_path: str = "reports/screenshots") -> None:
        """
        初始化截图助手
        
        Args:
            page: Playwright 页面实例
            base_path: 截图保存基础路径
        """
        self.page: Page = page
        self.base_path: Path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 截图配置
        self.default_config: Dict[str, Any] = {
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
        max_retries: int = 3,
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
            **kwargs: 其他截图参数
            
        Returns:
            截图文件路径，失败返回 None
        """
        for attempt in range(max_retries):
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
                
                # 获取唯一文件路径，避免冲突
                file_path = self._get_unique_filepath(filename)
                
                # 合并截图配置
                screenshot_config = {**self.default_config, **kwargs}
                screenshot_config['full_page'] = full_page
                screenshot_config['path'] = str(file_path)
                
                # 设置图片质量和格式
                if quality < 100:
                    screenshot_config['type'] = 'jpeg'
                    screenshot_config['quality'] = quality
                
                # 添加超时设置
                if 'timeout' not in screenshot_config:
                    screenshot_config['timeout'] = 30000  # 30秒超时
                
                # 等待页面稳定
                try:
                    self.page.wait_for_load_state('networkidle', timeout=5000)
                except Exception:
                    pass  # 忽略网络空闲等待失败
                
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
                
                # 验证截图文件
                if file_path.exists() and file_path.stat().st_size > 0:
                    # 记录日志
                    desc_str = f" - {description}" if description else ""
                    logger.info(f"📸 截图已保存: {file_path}{desc_str} (质量: {quality})")
                    return str(file_path)
                else:
                    raise Exception("截图文件为空或不存在")
                    
            except Exception as e:
                logger.warning(f"截图尝试 {attempt + 1}/{max_retries} 失败: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"截图最终失败: {str(e)}")
                    return None
                # 短暂等待后重试
                import time
                time.sleep(0.5)
        
        return None
    
    def _get_unique_filepath(self, filename: str) -> Path:
        """获取唯一的文件路径，避免冲突"""
        base_path: Path = self.base_path / filename
        if not base_path.exists():
            return base_path
        
        # 文件已存在，添加序号
        name_parts: list[str] = filename.rsplit('.', 1)
        base_name: str = name_parts[0]
        extension: str = name_parts[1] if len(name_parts) > 1 else 'png'
        
        counter: int = 1
        while True:
            new_filename: str = f"{base_name}_{counter}.{extension}"
            new_path: Path = self.base_path / new_filename
            if not new_path.exists():
                return new_path
            counter += 1
            if counter > 1000:  # 防止无限循环
                return self.base_path / f"{base_name}_{datetime.now().strftime('%f')}.{extension}"
    
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
        before_action: Optional[callable],
        after_action: Optional[callable],
        action_name: str = "action"
    ) -> Tuple[Optional[str], Optional[str]]:
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
        
        timestamp: str = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 操作前截图
        before_filename: str = f"before_{action_name}_{timestamp}.png"
        before_path: Optional[str] = self.take_screenshot(
            filename=before_filename,
            description=f"操作前截图 - {action_name}"
        )
        
        # 执行操作前的动作
        if before_action:
            before_action()
        
        # 操作后截图
        after_filename: str = f"after_{action_name}_{timestamp}.png"
        after_path: Optional[str] = self.take_screenshot(
            filename=after_filename,
            description=f"操作后截图 - {action_name}"
        )
        
        # 执行操作后的动作
        if after_action:
            after_action()
        
        return before_path, after_path
    
    def cleanup_old_screenshots(self, days: int = 7, max_size_mb: int = 500) -> int:
        """
        智能清理旧截图文件
        
        Args:
            days: 保留天数
            max_size_mb: 最大目录大小(MB)
            
        Returns:
            删除的文件数量
        """
        try:
            from datetime import timedelta
            deleted_count = 0
            cutoff_time = datetime.now() - timedelta(days=days)
            
            # 获取所有截图文件信息
            files_info = []
            total_size = 0
            
            for pattern in ["*.png", "*.jpg", "*.jpeg"]:
                for file_path in self.base_path.glob(pattern):
                    if file_path.is_file():
                        stat = file_path.stat()
                        files_info.append({
                            'path': file_path,
                            'mtime': stat.st_mtime,
                            'size': stat.st_size
                        })
                        total_size += stat.st_size
            
            # 按修改时间排序（旧的在前）
            files_info.sort(key=lambda x: x['mtime'])
            
            # 删除过期文件
            for file_info in files_info[:]:
                if file_info['mtime'] < cutoff_time.timestamp():
                    file_info['path'].unlink()
                    files_info.remove(file_info)
                    deleted_count += 1
                    total_size -= file_info['size']
                    logger.debug(f"删除过期截图: {file_info['path']}")
            
            # 如果目录仍然过大，删除最旧的文件
            max_size_bytes = max_size_mb * 1024 * 1024
            while total_size > max_size_bytes and files_info:
                oldest_file = files_info.pop(0)
                oldest_file['path'].unlink()
                deleted_count += 1
                total_size -= oldest_file['size']
                logger.debug(f"删除旧截图(空间限制): {oldest_file['path']}")
            
            if deleted_count > 0:
                logger.info(f"清理完成，删除了 {deleted_count} 个截图文件，当前目录大小: {(total_size / 1024 / 1024):.1f}MB")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理截图文件失败: {str(e)}")
            return 0
    
    def get_screenshot_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取截图文件信息
        
        Args:
            file_path: 截图文件路径
            
        Returns:
            截图信息字典
        """
        try:
            path: Path = Path(file_path)
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