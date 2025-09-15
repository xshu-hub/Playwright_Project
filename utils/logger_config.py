"""日志配置工具"""
import os
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
from typing import Optional, Dict, Set
import time
import hashlib
import glob
import threading
from contextvars import ContextVar

# 全局测试上下文变量
current_test_subdir: ContextVar[Optional[str]] = ContextVar('current_test_subdir', default=None)

class LoggerConfig:
    """日志配置类"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # 测试目录路径
        self.tests_dir = Path("tests")
        
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
        
        # 已创建的日志处理器缓存
        self._created_handlers: Set[str] = set()
        
        # 测试子目录映射
        self._test_subdirs: Dict[str, Path] = {}
        
        # 初始化时扫描测试目录
        self._scan_test_directories()
    
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
    
    def _scan_test_directories(self) -> None:
        """扫描tests目录下的所有子目录"""
        if not self.tests_dir.exists():
            return
            
        # 扫描tests目录下的所有子目录
        for subdir in self.tests_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('__'):
                self._test_subdirs[subdir.name] = subdir
                # 为每个测试子目录创建对应的日志目录
                log_subdir = self.log_dir / subdir.name
                log_subdir.mkdir(exist_ok=True)
    
    def _create_log_handlers_for_subdir(self, subdir_name: str, log_level: str, 
                                       rotation: str, retention: str, file_format: str) -> None:
        """为指定的测试子目录创建日志处理器
        
        Args:
            subdir_name: 测试子目录名称
            log_level: 日志级别
            rotation: 日志轮转大小
            retention: 日志保留时间
            file_format: 文件日志格式
        """
        log_subdir = self.log_dir / subdir_name
        log_subdir.mkdir(exist_ok=True)
        
        # 创建子目录专用的正常日志文件
        normal_log_key = f"{subdir_name}_normal"
        if normal_log_key not in self._created_handlers:
            # 使用闭包捕获subdir_name的值
            def create_filter(target_subdir):
                def subdir_filter(record):
                    # loguru的record是字典，检查extra信息
                    if 'extra' in record and record['extra']:
                        extra = record['extra']
                        if extra.get('subdir') == target_subdir:
                            return True
                        if extra.get('test_module') == f"tests.{target_subdir}":
                            return True
                    # 回退到原有的检查逻辑
                    return self._is_from_test_subdir(record, target_subdir)
                return subdir_filter
            
            logger.add(
                str(log_subdir / f"test_{subdir_name}.log"),
                format=file_format,
                level=log_level,
                rotation=rotation,
                retention=retention,
                encoding="utf-8",
                enqueue=True,
                filter=create_filter(subdir_name),
                backtrace=True,  # 启用回溯信息
                diagnose=True    # 启用诊断信息
            )
            self._created_handlers.add(normal_log_key)
        
        # 创建子目录专用的错误日志文件
        error_log_key = f"{subdir_name}_error"
        if error_log_key not in self._created_handlers:
            # 使用闭包捕获subdir_name的值
            def create_error_filter(target_subdir):
                def error_subdir_filter(record):
                    # 首先检查是否为错误级别
                    level_info = record.get('level')
                    if level_info and hasattr(level_info, 'name'):
                        level_name = level_info.name
                    else:
                        level_name = ''
                    if level_name not in ['ERROR', 'CRITICAL']:
                        return False
                    # loguru的record是字典，检查extra信息
                    if 'extra' in record and record['extra']:
                        extra = record['extra']
                        if extra.get('subdir') == target_subdir:
                            return True
                        if extra.get('test_module') == f"tests.{target_subdir}":
                            return True
                    # 回退到原有的检查逻辑
                    return self._is_from_test_subdir(record, target_subdir)
                return error_subdir_filter
            
            # 获取错误日志格式
            error_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message}\n{exception}"
            
            logger.add(
                str(log_subdir / f"test_{subdir_name}_error.log"),
                format=error_format,
                level="ERROR",
                rotation=rotation,
                retention=retention,
                encoding="utf-8",
                enqueue=True,
                filter=create_error_filter(subdir_name),
                backtrace=True,   # 启用回溯信息
                diagnose=True,    # 启用诊断信息
                catch=True        # 捕获异常
            )
            self._created_handlers.add(error_log_key)
    
    def _is_from_test_subdir(self, record, subdir_name: str) -> bool:
        """判断日志记录是否来自指定的测试子目录
        
        Args:
            record: 日志记录字典
            subdir_name: 测试子目录名称
            
        Returns:
            是否来自指定的测试子目录
        """
        # 首先检查当前测试上下文
        current_subdir = current_test_subdir.get()
        if current_subdir == subdir_name:
            return True
            
        # 检查绑定的额外信息
        if 'extra' in record and record['extra']:
            extra = record['extra']
            if extra.get('subdir') == subdir_name:
                return True
        
        # 检查模块名称是否包含测试子目录
        if 'name' in record and record['name']:
            return f"tests.{subdir_name}" in record['name']
        
        # 检查文件路径是否包含测试子目录 - 优先使用文件路径判断
        if 'file' in record and record['file']:
            file_info = record['file']
            if hasattr(file_info, 'path'):
                file_path = str(file_info.path)
            else:
                file_path = str(file_info)
            return f"tests{os.sep}{subdir_name}" in file_path or f"tests/{subdir_name}" in file_path
        
        # 备用检查：使用pathname属性
        if hasattr(record, 'pathname'):
            file_path = record.pathname
            return f"tests{os.sep}{subdir_name}" in file_path or f"tests/{subdir_name}" in file_path
        
        return False
    
    def _cleanup_cache(self, current_time: float) -> None:
        """清理过期的缓存项
        
        Args:
            current_time: 当前时间戳
        """
        # 如果缓存超过限制，清理过期项
        if len(self._log_cache) > self._cache_size_limit:
            expired_keys = [
                key for key, timestamp in self._log_cache.items()
                if current_time - timestamp > self._dedup_window * 2
            ]
            for key in expired_keys:
                del self._log_cache[key]
    
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
        # 移除默认处理器
        logger.remove()
        
        # 获取环境变量中的日志级别
        log_level = os.getenv("LOG_LEVEL", level).upper()
        if log_level not in self.level_mapping:
            log_level = "INFO"
        
        # 简化的控制台输出格式
        console_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        
        # 详细的文件输出格式
        file_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message}"
        
        # 错误日志的详细格式（包含异常信息）
        error_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message}\n{exception}"
        
        # 添加控制台处理器
        if console_output:
            logger.add(
                sys.stdout,
                format=console_format,
                level=log_level,
                colorize=True  # 启用颜色提升开发体验
            )
        
        # 添加文件处理器
        if file_output:
            try:
                # 重新扫描测试目录（检测新增的子目录）
                self._scan_test_directories()
                
                # 创建全局日志文件
                if "global_normal" not in self._created_handlers:
                    logger.add(
                        str(self.log_dir / "global.log"),
                        format=file_format,
                        level=log_level,
                        rotation=rotation,
                        retention=retention,
                        encoding="utf-8",
                        enqueue=True,
                        backtrace=True,  # 启用回溯信息
                        diagnose=True    # 启用诊断信息
                    )
                    self._created_handlers.add("global_normal")
                
                # 创建全局错误日志文件
                if "global_error" not in self._created_handlers:
                    logger.add(
                        str(self.log_dir / "global_error.log"),
                        format=error_format,
                        level="ERROR",
                        rotation=rotation,
                        retention=retention,
                        encoding="utf-8",
                        enqueue=True,
                        backtrace=True,   # 启用回溯信息
                        diagnose=True,    # 启用诊断信息
                        catch=True        # 捕获异常
                    )
                    self._created_handlers.add("global_error")
                
                # 为每个测试子目录创建专用的日志处理器
                for subdir_name in self._test_subdirs.keys():
                    self._create_log_handlers_for_subdir(
                        subdir_name, log_level, rotation, retention, file_format
                    )
                    
            except Exception as e:
                # 如果文件日志失败，只使用控制台日志
                # 使用 sys.stderr 输出警告，避免循环依赖
                sys.stderr.write(f"Warning: Could not setup file logging: {e}\n")
    
    def get_test_logger(self, test_name: str, subdir_name: str = None) -> logger:
        """获取测试专用日志器
        
        Args:
            test_name: 测试名称
            subdir_name: 测试子目录名称（可选）
            
        Returns:
            配置好的日志器实例
        """
        if subdir_name:
            test_logger = logger.bind(test_name=test_name, subdir=subdir_name)
        else:
            test_logger = logger.bind(test_name=test_name)
        return test_logger
    
    def get_subdir_logger(self, subdir_name: str) -> logger:
        """获取指定测试子目录的专用日志器
        
        Args:
            subdir_name: 测试子目录名称
            
        Returns:
            配置好的日志器实例
        """
        # 确保子目录存在于映射中
        if subdir_name not in self._test_subdirs:
            self._scan_test_directories()
        
        # 只在第一次调用时创建处理器
        normal_log_key = f"{subdir_name}_normal"
        if normal_log_key not in self._created_handlers:
            log_level = os.getenv("LOG_LEVEL", "INFO").upper()
            if log_level not in self.level_mapping:
                log_level = "INFO"
            
            rotation = "10 MB"
            retention = "30 days"
            file_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message}"
            
            self._create_log_handlers_for_subdir(
                subdir_name, 
                log_level, 
                rotation, 
                retention, 
                file_format
            )
        
        # 创建带有子目录标识的日志器，添加更多上下文信息
        bound_logger = logger.bind(
            subdir=subdir_name,
            test_module=f"tests.{subdir_name}",
            log_category="test_subdir"
        )
        return bound_logger
    
    def refresh_test_directories(self) -> None:
        """手动刷新测试目录扫描（用于检测新增的测试子目录）"""
        self._scan_test_directories()
    
    def set_test_context(self, subdir_name: str) -> None:
        """设置当前测试上下文
        
        Args:
            subdir_name: 测试子目录名称
        """
        current_test_subdir.set(subdir_name)
    
    def clear_test_context(self) -> None:
        """清除当前测试上下文"""
        current_test_subdir.set(None)
    
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