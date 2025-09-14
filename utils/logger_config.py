"""日志配置工具"""
import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Optional

from loguru import logger


class LoggerConfig:
    """日志配置类"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # 日志级别映射
        self.level_mapping = {
            "DEBUG": "DEBUG",
            "INFO": "INFO", 
            "WARNING": "WARNING",
            "ERROR": "ERROR",
            "CRITICAL": "CRITICAL"
        }
        
        # 日志去重缓存
        self._log_cache = {}
        self._cache_size_limit = 1000
        self._dedup_window = 5  # 5秒内的重复日志将被去重
        self._cleanup_counter = 0  # 清理计数器
    
    def _should_log(self, message: str, level: str) -> bool:
        """检查是否应该记录日志（去重检查）
        
        Args:
            message: 日志消息
            level: 日志级别
            
        Returns:
            是否应该记录日志
        """
        # 生成消息的哈希值作为缓存键
        message_hash = hashlib.md5(f"{level}:{message}".encode()).hexdigest()
        current_time = time.time()
        
        # 检查缓存中是否存在相同的日志
        if message_hash in self._log_cache:
            last_time = self._log_cache[message_hash]
            # 如果在去重窗口时间内，则跳过
            if current_time - last_time < self._dedup_window:
                return False
        
        # 更新缓存
        self._log_cache[message_hash] = current_time
        
        # 清理过期的缓存项
        self._cleanup_cache(current_time)
        
        return True
    
    def _cleanup_cache(self, current_time: float) -> None:
        """清理过期的缓存项
        
        Args:
            current_time: 当前时间戳
        """
        # 增加清理计数器
        self._cleanup_counter += 1
        
        # 定期清理或缓存超过限制时清理
        if len(self._log_cache) > self._cache_size_limit or self._cleanup_counter >= 100:
            expired_keys = [
                key for key, timestamp in self._log_cache.items()
                if current_time - timestamp > self._dedup_window * 2
            ]
            for key in expired_keys:
                del self._log_cache[key]
            
            # 如果清理后仍然超过限制，强制清理一半缓存
            if len(self._log_cache) > self._cache_size_limit:
                cache_items = list(self._log_cache.items())
                # 保留较新的一半
                cache_items.sort(key=lambda x: x[1], reverse=True)
                self._log_cache = dict(cache_items[:self._cache_size_limit//2])
            
            # 重置计数器
            self._cleanup_counter = 0
    
    def log_with_dedup(self, level: str, message: str) -> None:
        """带去重功能的日志记录
        
        Args:
            level: 日志级别
            message: 日志消息
        """
        if self._should_log(message, level):
            getattr(logger, level.lower())(message)
    
    def setup_logger(
        self,
        name: str = "playwright_test",
        level: str = "INFO",
        console_output: bool = True,
        file_output: bool = True,
        rotation: str = "10 MB",
        retention: str = "30 days",
        compression: str = "zip"
    ) -> None:
        """设置日志配置
        
        Args:
            name: 日志器名称
            level: 日志级别
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            rotation: 日志轮转大小
            retention: 日志保留时间
            compression: 压缩格式
        """
        # 移除默认处理器
        logger.remove()
        
        # 获取环境变量中的日志级别
        log_level = os.getenv("LOG_LEVEL", level).upper()
        if log_level not in self.level_mapping:
            log_level = "INFO"
        
        # 统一的日志格式配置
        formats = self._get_log_formats()
        
        # 添加控制台处理器
        if console_output:
            logger.add(
                sys.stdout,
                format=formats['console'],
                level=log_level,
                colorize=True,
                backtrace=True,
                diagnose=True,
                filter=self._console_filter
            )
        
        # 添加文件处理器
        if file_output:
            try:
                # 通用日志文件
                log_file = self.log_dir / f"{name}.log"
                logger.add(
                    str(log_file),
                    format=formats['file'],
                    level=log_level,
                    rotation=rotation,
                    retention=retention,
                    compression=compression,
                    encoding="utf-8",
                    enqueue=True,
                    backtrace=True,
                    diagnose=True
                )
                
                # 错误日志文件
                error_log_file = self.log_dir / f"{name}_error.log"
                logger.add(
                    str(error_log_file),
                    format=formats['file'],
                    level="ERROR",
                    rotation=rotation,
                    retention=retention,
                    compression=compression,
                    encoding="utf-8",
                    enqueue=True,
                    backtrace=True,
                    diagnose=True
                )
            except Exception as e:
                # 如果文件日志失败，只使用控制台日志
                # 这里不能使用logger，因为logger还没有完全设置好
                sys.stderr.write(f"Warning: Could not setup file logging: {e}\n")
    
    def _get_log_formats(self) -> dict:
        """获取统一的日志格式"""
        return {
            'console': (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            'file': (
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
                "{process.id}:{thread.id} | {name}:{function}:{line} | {message}"
            )
        }
    
    def _console_filter(self, record):
        """控制台日志过滤器"""
        # 过滤掉一些不重要的日志
        message = record['message']
        if any(keyword in message.lower() for keyword in ['debug', 'trace']):
            return record['level'].name != 'DEBUG'
        return True
    
    def get_test_logger(self, test_name: str) -> logger:
        """获取测试专用日志器
        
        Args:
            test_name: 测试名称
            
        Returns:
            配置好的日志器实例
        """
        test_logger = logger.bind(test_name=test_name)
        return test_logger
    
    def log_test_start(self, test_name: str, test_data: Optional[dict] = None) -> None:
        """记录测试开始
        
        Args:
            test_name: 测试名称
            test_data: 测试数据
        """
        logger.info(f"🚀 开始执行测试: {test_name}")
        if test_data:
            logger.debug(f"测试数据: {test_data}")
    
    def log_test_end(self, test_name: str, result: str, duration: Optional[float] = None) -> None:
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
    
    def log_step(self, step_name: str, step_data: Optional[dict] = None) -> None:
        """记录测试步骤
        
        Args:
            step_name: 步骤名称
            step_data: 步骤数据
        """
        logger.info(f"📋 执行步骤: {step_name}")
        if step_data:
            logger.debug(f"步骤数据: {step_data}")
    
    def log_assertion(self, assertion: str, result: bool, actual=None, expected=None) -> None:
        """记录断言结果
        
        Args:
            assertion: 断言描述
            result: 断言结果
            actual: 实际值
            expected: 期望值
        """
        emoji = "✅" if result else "❌"
        logger.info(f"{emoji} 断言: {assertion} - {'通过' if result else '失败'}")
        
        if not result and actual is not None and expected is not None:
            logger.error(f"期望值: {expected}, 实际值: {actual}")
    
    def log_screenshot(self, screenshot_path: str, description: str = "") -> None:
        """记录截图信息
        
        Args:
            screenshot_path: 截图路径
            description: 截图描述
        """
        desc = f" - {description}" if description else ""
        logger.info(f"📸 截图已保存: {screenshot_path}{desc}")
    
    def log_page_action(self, action: str, element: str = "", value: str = "") -> None:
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


def get_logger(name: str = None):
    """获取日志器实例
    
    Args:
        name: 日志器名称
        
    Returns:
        日志器实例
    """
    if name:
        return logger.bind(name=name)
    return logger