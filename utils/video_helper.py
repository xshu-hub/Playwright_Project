"""简化的视频助手工具"""
from pathlib import Path
from datetime import datetime
from typing import Optional
from playwright.sync_api import Page
from loguru import logger


class VideoHelper:
    """简化的视频助手类"""
    
    def __init__(self, base_path: str = "reports/videos"):
        """
        初始化视频助手
        
        Args:
            base_path: 视频保存基础路径
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_video_path(page: Page) -> Optional[str]:
        """
        获取页面的视频录制路径
        
        Args:
            page: Playwright 页面实例
            
        Returns:
            视频文件路径
        """
        try:
            video_path = page.video.path() if page.video else None
            return str(video_path) if video_path else None
        except Exception as e:
            logger.error(f"获取视频路径失败: {str(e)}")
            return None
    
    def save_failure_video(
        self,
        page: Page,
        test_name: str,
        error_msg: str = ""
    ) -> Optional[str]:
        """
        保存失败测试的视频
        
        Args:
            page: Playwright 页面实例
            test_name: 测试名称
            error_msg: 错误信息
            
        Returns:
            保存的视频文件路径
        """
        try:
            video_path = self.get_video_path(page)
            if not video_path:
                logger.warning("未找到视频录制文件")
                return None
            
            # 生成失败视频的新文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            failed_video_name = f"failed_{test_name}_{timestamp}.webm"
            failed_video_path = self.base_path / failed_video_name
            
            # 等待视频文件写入完成
            import time
            time.sleep(1)
            
            # 移动视频文件
            if Path(video_path).exists():
                Path(video_path).rename(failed_video_path)
                
                desc = f"测试失败视频 - {test_name}"
                if error_msg:
                    desc += f" - {error_msg[:100]}"
                
                logger.info(f"🎥 {desc}: {failed_video_path}")
                return str(failed_video_path)
            else:
                logger.warning(f"视频文件不存在: {video_path}")
                return None
                
        except Exception as e:
            logger.error(f"保存失败视频失败: {str(e)}")
            return None
    
    def cleanup_passed_video(self, page: Page) -> bool:
        """
        清理通过测试的视频文件
        
        Args:
            page: Playwright 页面实例
            
        Returns:
            是否成功清理
        """
        try:
            video_path = self.get_video_path(page)
            if not video_path:
                return True
            
            # 等待一小段时间确保视频文件已写入
            import time
            time.sleep(0.5)
            
            if Path(video_path).exists():
                Path(video_path).unlink()
                logger.info(f"已删除通过测试的视频文件: {video_path}")
                return True
            else:
                logger.debug(f"视频文件不存在，无需删除: {video_path}")
                return True
                
        except Exception as e:
            logger.error(f"删除视频文件失败: {e}")
            return False


def create_video_helper(base_path: str = "reports/videos") -> VideoHelper:
    """
    创建视频助手实例
    
    Args:
        base_path: 视频保存基础路径
        
    Returns:
        视频助手实例
    """
    return VideoHelper(base_path)