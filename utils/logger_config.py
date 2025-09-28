"""简化的日志配置工具"""
import os
import sys
from pathlib import Path
from loguru import logger
from typing import Optional


class LoggerConfig:
    """简化的日志配置类"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self._initialized = False
    
    def setup_logger(
        self,
        level: str = "INFO",
        console_output: bool = True,
        file_output: bool = True,
        rotation: str = "10 MB",
        retention: str = "7 days"
    ) -> None:
        """设置日志配置
        
        Args:
            level: 日志级别
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            rotation: 日志轮转大小
            retention: 日志保留时间
        """
        if self._initialized:
            return
            
        # 移除默认处理器
        logger.remove()
        
        # 获取环境变量中的日志级别
        log_level = os.getenv("LOG_LEVEL", level).upper()
        if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            log_level = "INFO"
        
        # 控制台输出格式
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
                # 全局日志文件
                logger.add(
                    str(self.log_dir / "test.log"),
                    format=file_format,
                    level=log_level,
                    rotation=rotation,
                    retention=retention,
                    encoding="utf-8",
                    enqueue=True
                )
                
                # 错误日志文件
                logger.add(
                    str(self.log_dir / "error.log"),
                    format=file_format,
                    level="ERROR",
                    rotation=rotation,
                    retention=retention,
                    encoding="utf-8",
                    mode="a",
                    enqueue=True
                )
                
            except Exception as e:
                # 如果文件日志失败，只使用控制台日志
                sys.stderr.write(f"Warning: Could not setup file logging: {e}\n")
        
        self._initialized = True
    
    @staticmethod
    def log_test_start(test_name: str) -> None:
        """记录测试开始"""
        logger.info(f"开始执行测试: {test_name}")
    
    @staticmethod
    def log_test_end(test_name: str, result: str) -> None:
        """记录测试结束"""
        logger.info(f"测试完成: {test_name} - {result}")
    
    @staticmethod
    def log_page_action(action: str, element: str = "", value: str = "") -> None:
        """记录页面操作"""
        element_str = f" 元素: {element}" if element else ""
        value_str = f" 值: {value}" if value else ""
        logger.debug(f"页面操作: {action}{element_str}{value_str}")


# 全局日志配置实例
logger_config = LoggerConfig()


def setup_logger(
    level: str = "INFO",
    console_output: bool = True,
    file_output: bool = True
) -> None:
    """快速设置日志配置"""
    logger_config.setup_logger(
        level=level,
        console_output=console_output,
        file_output=file_output
    )


def get_logger():
    """获取日志器实例"""
    return logger