"""视频录制助手工具 - 专门用于处理失败测试的视频保存和成功测试的视频清理"""
from pathlib import Path
from datetime import datetime
from typing import Optional
from playwright.sync_api import Page, BrowserContext
from loguru import logger


class VideoHelper:
    """视频录制助手类 - 专门用于处理失败测试的视频保存和成功测试的视频清理"""
    
    def __init__(self, context: BrowserContext, base_path: str = "reports/videos"):
        """
        初始化视频录制助手
        
        Args:
            context: Playwright 浏览器上下文
            base_path: 视频保存基础路径
        """
        self.context = context
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
    
    def save_video_on_failure(
        self,
        page: Page,
        test_name: str,
        error_msg: str = ""
    ) -> Optional[str]:
        """
        在测试失败时保存视频
        
        Args:
            page: Playwright 页面实例
            test_name: 测试名称
            error_msg: 错误信息
            
        Returns:
            保存的视频文件路径
        """
        try:
            # 先关闭页面以确保视频录制完成
            if page and not page.is_closed():
                page.close()
            
            video_path = VideoHelper.get_video_path(page)
            if not video_path:
                logger.warning("未找到视频录制文件")
                return None
            
            # 生成失败视频的新文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            failed_video_name = f"failed_{test_name}_{timestamp}.webm"
            failed_video_path = self.base_path / failed_video_name
            
            source_path = Path(video_path)
            
            # 等待视频文件写入完成，最多等待5秒
            import time
            max_wait_time = 5
            wait_interval = 0.1
            waited_time = 0
            
            while waited_time < max_wait_time:
                if source_path.exists() and source_path.stat().st_size > 0:
                    # 文件存在且有内容，再等待一小段时间确保写入完成
                    time.sleep(0.5)
                    break
                time.sleep(wait_interval)
                waited_time += wait_interval
            
            if not source_path.exists():
                logger.warning(f"视频文件不存在: {video_path}")
                return None
            
            if source_path.stat().st_size == 0:
                logger.warning(f"视频文件为空: {video_path}")
                return None
            
            # 尝试移动文件而不是复制
            import shutil
            try:
                shutil.move(str(source_path), str(failed_video_path))
                file_size = failed_video_path.stat().st_size
                logger.info(f"🎥 测试失败视频 - {test_name} - {error_msg}: {failed_video_path} (大小: {file_size} 字节)")
                return str(failed_video_path)
            except Exception as move_error:
                logger.error(f"移动失败视频文件失败: {str(move_error)}")
                # 如果移动失败，尝试复制然后删除原文件
                try:
                    shutil.copy2(str(source_path), str(failed_video_path))
                    source_path.unlink()  # 删除原文件
                    file_size = failed_video_path.stat().st_size
                    logger.info(f"🎥 测试失败视频 - {test_name} - {error_msg}: {failed_video_path} (大小: {file_size} 字节)")
                    return str(failed_video_path)
                except Exception as copy_error:
                    logger.error(f"复制失败视频文件失败: {str(copy_error)}")
                    return None
                
        except Exception as e:
            logger.error(f"保存失败视频时出错: {str(e)}")
            return None
    
    def cleanup_success_video(self, page: Page) -> bool:
        """
        清理成功测试的视频文件
        
        Args:
            page: Playwright 页面实例
            
        Returns:
            是否成功清理
        """
        try:
            # 由于页面已关闭，需要从上下文获取视频路径
            # 获取上下文中的所有视频文件
            video_files = list(self.base_path.glob("*.webm"))
            
            # 删除非failed开头的视频文件（即成功测试的视频）
            deleted_count = 0
            for video_file in video_files:
                if not video_file.name.startswith("failed_"):
                    try:
                        video_file.unlink()
                        logger.info(f"🗑️ 成功测试视频已删除: {video_file}")
                        deleted_count += 1
                    except Exception as delete_error:
                        # 如果删除失败，可能是文件被占用，尝试等待后再删除
                        import time
                        time.sleep(0.5)
                        try:
                            video_file.unlink()
                            logger.info(f"🗑️ 成功测试视频已删除（重试后）: {video_file}")
                            deleted_count += 1
                        except Exception as retry_error:
                            logger.error(f"删除成功测试视频失败: {str(retry_error)}")
            
            return True
                
        except Exception as e:
            logger.error(f"删除成功测试视频失败: {str(e)}")
            return False
    
    def cleanup_old_videos(self, days: int = 7) -> int:
        """
        清理旧的视频文件
        
        Args:
            days: 保留天数
            
        Returns:
            删除的文件数量
        """
        try:
            current_time = datetime.now()
            deleted_count = 0
            
            for file_path in self.base_path.glob("*.webm"):
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if (current_time - file_time).days > days:
                    file_path.unlink()
                    deleted_count += 1
                    logger.debug(f"删除旧视频: {file_path}")
            
            if deleted_count > 0:
                logger.info(f"清理完成，删除了 {deleted_count} 个旧视频文件")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理视频文件失败: {str(e)}")
            return 0


def create_video_helper(context: BrowserContext, base_path: str = "reports/videos") -> VideoHelper:
    """
    创建视频助手实例
    
    Args:
        context: Playwright 浏览器上下文
        base_path: 视频保存基础路径
        
    Returns:
        视频助手实例
    """
    return VideoHelper(context, base_path)