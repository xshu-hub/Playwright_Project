"""日志配置模块 - 简化版本

提供统一的日志配置和管理功能，专注于核心功能。
"""

import os
import sys
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from loguru import Logger


class LoggerConfig:
    """简化的日志配置类
    
    专注于核心日志功能，移除了复杂的去重和子目录处理逻辑。
    """
    
    def __init__(self, log_dir: Optional[str] = None):
        """初始化日志配置
        
        Args:
            log_dir: 日志目录路径，默认为项目根目录下的logs文件夹
        """
        # 设置日志目录
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            # 默认使用项目根目录下的logs文件夹
            project_root = Path(__file__).parent.parent
            self.log_dir = project_root / "logs"
        
        # 创建日志目录
        self.log_dir.mkdir(exist_ok=True)
        
        # 日志级别映射
        self.level_mapping = {
            "DEBUG": "DEBUG",
            "INFO": "INFO", 
            "WARNING": "WARNING",
            "ERROR": "ERROR",
            "CRITICAL": "CRITICAL"
        }
        
        # 标记是否已初始化
        self._initialized = False
    
    def setup_logger(
        self,
        level: str = "INFO",
        console_output: bool = True,
        file_output: bool = True,
        rotation: str = "10 MB",
        retention: str = "30 days",
        compression: str = "zip"
    ) -> None:
        """设置日志配置
        
        Args:
            level: 日志级别
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            rotation: 日志轮转大小
            retention: 日志保留时间
            compression: 压缩格式
        """
        # 避免重复初始化
        if self._initialized:
            return
            
        # 移除默认处理器
        logger.remove()
        
        # 获取环境变量中的日志级别
        log_level = os.getenv("LOG_LEVEL", level).upper()
        if log_level not in self.level_mapping:
            log_level = "INFO"
        
        # 简化的控制台输出格式
        console_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        
        # 文件输出格式
        file_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message}"
        
        # 添加控制台处理器
        if console_output:
            logger.add(
                sys.stdout,
                format=console_format,
                level=log_level,
                colorize=True
            )
        
        # 添加文件处理器
        if file_output:
            try:
                # 确保日志目录存在
                self.log_dir.mkdir(parents=True, exist_ok=True)
                
                # 普通日志文件
                app_log_path = str(self.log_dir / "app.log")
                logger.add(
                    app_log_path,
                    format=file_format,
                    level=log_level,
                    rotation=rotation,
                    retention=retention,
                    compression=compression,
                    encoding="utf-8",
                    enqueue=True
                )
                
                # 错误日志文件
                error_log_path = str(self.log_dir / "error.log")
                logger.add(
                    error_log_path,
                    format=file_format,
                    level="ERROR",
                    rotation=rotation,
                    retention=retention,
                    compression=compression,
                    encoding="utf-8",
                    enqueue=True
                )
                
                # 记录日志文件路径
                print(f"日志文件已配置: {app_log_path}, {error_log_path}")
                    
            except Exception as e:
                # 如果文件日志失败，只使用控制台日志
                sys.stderr.write(f"Warning: Could not setup file logging: {e}\n")
        
        self._initialized = True
    
    @staticmethod
    def get_logger(name: Optional[str] = None) -> 'Logger':
        """获取日志器实例
        
        Args:
            name: 日志器名称
            
        Returns:
            日志器实例
        """
        if name:
            return logger.bind(name=name)
        return logger
    
    @staticmethod
    def log_test_start(test_name: str) -> None:
        """记录测试开始
        
        Args:
            test_name: 测试名称
        """
        logger.info(f"🚀 开始执行测试: {test_name}")
    
    @staticmethod
    def log_test_end(test_name: str, result: str, duration: Optional[float] = None) -> None:
        """记录测试结束
        
        Args:
            test_name: 测试名称
            result: 测试结果 (PASSED/FAILED/SKIPPED)
            duration: 执行时长(秒)
        """
        emoji = {
            "PASSED": "✅",
            "FAILED": "❌", 
            "SKIPPED": "⏭️"
        }.get(result, "❓")
        
        duration_str = f" (耗时: {duration:.2f}s)" if duration else ""
        logger.info(f"{emoji} 测试完成: {test_name} - {result}{duration_str}")
    
    @staticmethod
    def log_step(step_name: str) -> None:
        """记录测试步骤
        
        Args:
            step_name: 步骤名称
        """
        logger.info(f"📋 执行步骤: {step_name}")
    
    @staticmethod
    def log_screenshot(screenshot_path: str, description: str = "") -> None:
        """记录截图信息
        
        Args:
            screenshot_path: 截图路径
            description: 截图描述
        """
        desc = f" - {description}" if description else ""
        logger.info(f"📸 截图已保存: {screenshot_path}{desc}")
    
    @staticmethod
    def log_page_action(action: str, element: str = "", value: str = "") -> None:
        """记录页面操作
        
        Args:
            action: 操作类型
            element: 元素定位器
            value: 操作值
        """
        element_str = f" 元素: {element}" if element else ""
        value_str = f" 值: {value}" if value else ""
        logger.debug(f"🖱️ 页面操作: {action}{element_str}{value_str}")


# 全局日志配置实例
logger_config = LoggerConfig()


def setup_logger(
    level: str = "INFO",
    console_output: bool = True,
    file_output: bool = False
) -> None:
    """快速设置日志配置
    
    Args:
        level: 日志级别
        console_output: 是否输出到控制台
        file_output: 是否输出到文件
    """
    logger_config.setup_logger(
        level=level,
        console_output=console_output,
        file_output=file_output
    )


def get_logger(name: Optional[str] = None) -> 'Logger':
    """获取日志器实例
    
    Args:
        name: 日志器名称
        
    Returns:
        日志器实例
    """
    return LoggerConfig.get_logger(name)