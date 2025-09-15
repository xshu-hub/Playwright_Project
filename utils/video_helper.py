"""视频录制助手工具"""
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from playwright.sync_api import Page, BrowserContext
from loguru import logger


class VideoHelper:
    """视频录制助手类"""
    
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
        
        # 视频录制配置
        self.default_config = {
            'size': {'width': 1920, 'height': 1080},
            'mode': 'retain-on-failure'  # 'on', 'off', 'retain-on-failure'
        }
        
        self.is_recording = False
        self.current_video_path: Optional[Path] = None
    
    def start_recording(
        self,
        test_name: str = "",
        video_config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        开始录制视频
        
        Args:
            test_name: 测试名称
            video_config: 视频配置
            
        Returns:
            是否成功开始录制
        """
        try:
            if self.is_recording:
                logger.warning("视频录制已在进行中")
                return False
            
            # 合并配置
            config = {**self.default_config}
            if video_config:
                config.update(video_config)
            
            # 生成视频文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            test_prefix = f"{test_name}_" if test_name else ""
            video_filename = f"{test_prefix}test_{timestamp}.webm"
            self.current_video_path = self.base_path / video_filename
            
            # 注意: Playwright 的视频录制需要在创建上下文时配置
            # 这里主要是记录状态和路径信息，实际录制由 Playwright 上下文管理
            self.is_recording = True
            
            logger.info(f"🎥 视频录制已启用: {self.current_video_path}")
            return True
            
        except Exception as e:
            logger.error(f"启用视频录制失败: {str(e)}")
            return False
    
    def stop_recording(self, save_video: bool = True) -> Optional[str]:
        """
        停止录制视频
        
        Args:
            save_video: 是否保存视频
            
        Returns:
            视频文件路径，如果不保存或失败则返回 None
        """
        try:
            if not self.is_recording:
                logger.warning("当前没有进行视频录制")
                return None
            
            self.is_recording = False
            
            if save_video and self.current_video_path:
                logger.info(f"🎥 视频录制完成: {self.current_video_path}")
                return str(self.current_video_path)
            else:
                # 删除视频文件
                if self.current_video_path and self.current_video_path.exists():
                    self.current_video_path.unlink()
                    logger.info("🗑️ 视频文件已删除")
                return None
                
        except Exception as e:
            logger.error(f"停止录制视频失败: {str(e)}")
            return None
        finally:
            self.current_video_path = None
    
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
            video_path = VideoHelper.get_video_path(page)
            if not video_path:
                logger.warning("未找到视频录制文件")
                return None
            
            # 生成失败视频的新文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            failed_video_name = f"failed_{test_name}_{timestamp}.webm"
            failed_video_path = self.base_path / failed_video_name
            
            # 关闭页面以确保视频文件完整
            page.close()
            
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
    
    @staticmethod
    def get_video_info(file_path: str) -> dict:
        """
        获取视频文件信息
        
        Args:
            file_path: 视频文件路径
            
        Returns:
            视频信息字典
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {}
            
            stat = path.stat()
            return {
                'filename': path.name,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'absolute_path': str(path.absolute())
            }
            
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            return {}
    
    @staticmethod
    def compress_video(input_path: str, output_path: Optional[str] = None, quality: str = "medium") -> Optional[str]:
        """
        压缩视频文件 (需要 ffmpeg)
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            quality: 压缩质量 (low, medium, high)
            
        Returns:
            压缩后的视频路径
        """
        try:
            import subprocess
            
            input_file = Path(input_path)
            if not input_file.exists():
                logger.error(f"输入视频文件不存在: {input_path}")
                return None
            
            if not output_path:
                output_path = str(input_file.parent / f"compressed_{input_file.name}")
            
            # 质量参数映射
            quality_params = {
                'low': ['-crf', '28'],
                'medium': ['-crf', '23'],
                'high': ['-crf', '18']
            }
            
            # 构建 ffmpeg 命令
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-c:v', 'libx264',
                '-preset', 'medium',
                *quality_params.get(quality, quality_params['medium']),
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',  # 覆盖输出文件
                str(output_path)
            ]
            
            # 执行压缩
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"视频压缩完成: {output_path}")
                return str(output_path)
            else:
                logger.error(f"视频压缩失败: {result.stderr}")
                return None
                
        except ImportError:
            logger.warning("视频压缩需要安装 ffmpeg")
            return None
        except Exception as e:
            logger.error(f"视频压缩失败: {str(e)}")
            return None


class VideoRecordingContext:
    """视频录制上下文管理器"""
    
    def __init__(self, video_helper: VideoHelper, test_name: str = "", save_on_success: bool = False):
        """
        初始化视频录制上下文
        
        Args:
            video_helper: 视频助手实例
            test_name: 测试名称
            save_on_success: 成功时是否保存视频
        """
        self.video_helper = video_helper
        self.test_name = test_name
        self.save_on_success = save_on_success
        self.video_path = None
        self.test_failed = False
    
    def __enter__(self):
        """进入上下文"""
        self.video_helper.start_recording(self.test_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        # 判断是否有异常（测试失败）
        self.test_failed = exc_type is not None
        
        # 根据测试结果决定是否保存视频
        save_video = self.test_failed or self.save_on_success
        self.video_path = self.video_helper.stop_recording(save_video)
        
        return False  # 不抑制异常


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