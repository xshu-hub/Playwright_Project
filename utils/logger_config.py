"""日志配置模块 - 支持按testcase子包分组存放日志

提供统一的日志配置和管理功能，支持动态识别testcase子包并分组存放日志文件。
"""

import os
import sys
import inspect
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from loguru import Logger


class LoggerConfig:
    """支持按testcase子包分组的日志配置类
    
    动态识别testcase子包，为每个子包创建独立的日志文件。
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
        
        # 存储已创建的日志处理器
        self._handlers = {}
    
    def _get_testcase_group(self) -> Optional[str]:
        """动态识别当前测试所属的testcase子包
        
        Returns:
            子包名称，如 'test_group_1', 'test_group_2' 等，如果不在testcase子包中则返回None
        """
        try:
            # 获取调用栈
            frame = inspect.currentframe()
            while frame:
                # 获取文件路径
                file_path = frame.f_code.co_filename
                if file_path and 'testcase' in file_path:
                    path_obj = Path(file_path)
                    # 检查是否在testcase目录下的子包中
                    parts = path_obj.parts
                    testcase_index = -1
                    for i, part in enumerate(parts):
                        if part == 'testcase':
                            testcase_index = i
                            break
                    
                    if testcase_index >= 0 and testcase_index + 1 < len(parts):
                        # 获取testcase下的直接子目录名
                        subpackage = parts[testcase_index + 1]
                        if subpackage.startswith('test_group'):
                            return subpackage
                
                frame = frame.f_back
            
            return None
        except Exception:
            return None
    
    def setup_logger_for_group(self, group: str, level: str = "INFO", 
                              console_output: bool = True, file_output: bool = True,
                              rotation: str = "10 MB", retention: str = "30 days", 
                              compression: str = "zip") -> None:
        """为指定的testcase子包设置日志配置
        
        Args:
            group: testcase子包名称
            level: 日志级别
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            rotation: 日志轮转大小
            retention: 日志保留时间
            compression: 压缩格式
        """
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
                
                # 获取指定子包的日志文件路径
                log_paths = self._get_log_file_paths(group)
                
                # 普通日志文件
                app_log_path = log_paths['app']
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
                error_log_path = log_paths['error']
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
                print(f"日志文件已配置 (子包: {group}): {app_log_path}, {error_log_path}")
                    
            except Exception as e:
                # 如果文件日志失败，只使用控制台日志
                error_details = {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'log_dir': str(self.log_dir),
                    'testcase_group': group,
                    'attempted_files': [log_paths.get('app', 'app.log'), log_paths.get('error', 'error.log')]
                }
                sys.stderr.write(f"日志配置失败 [LOG_001] | 日志目录: {error_details['log_dir']} | 子包: {error_details['testcase_group']} | 错误类型: {error_details['error_type']} | 错误信息: {error_details['error_message']} | 尝试创建的文件: {error_details['attempted_files']}\n")
    
    def _get_log_file_paths(self, group: Optional[str] = None) -> Dict[str, str]:
        """获取日志文件路径
        
        Args:
            group: testcase子包名称
            
        Returns:
            包含app.log和error.log路径的字典
        """
        if group:
            # 为特定子包创建日志文件
            group_dir = self.log_dir / group
            group_dir.mkdir(exist_ok=True)
            return {
                'app': str(group_dir / f"{group}_app.log"),
                'error': str(group_dir / f"{group}_error.log")
            }
        else:
            # 默认日志文件
            return {
                'app': str(self.log_dir / "app.log"),
                'error': str(self.log_dir / "error.log")
            }
    
    def setup_logger(
        self,
        level: str = "INFO",
        console_output: bool = True,
        file_output: bool = True,
        rotation: str = "10 MB",
        retention: str = "30 days",
        compression: str = "zip"
    ) -> None:
        """设置日志配置，支持按testcase子包分组
        
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
                
                # 动态识别testcase子包
                testcase_group = self._get_testcase_group()
                log_paths = self._get_log_file_paths(testcase_group)
                
                # 普通日志文件
                app_log_path = log_paths['app']
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
                error_log_path = log_paths['error']
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
                group_info = f" (子包: {testcase_group})" if testcase_group else ""
                print(f"日志文件已配置{group_info}: {app_log_path}, {error_log_path}")
                    
            except Exception as e:
                # 如果文件日志失败，只使用控制台日志
                error_details = {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'log_dir': str(self.log_dir),
                    'testcase_group': testcase_group,
                    'attempted_files': [log_paths.get('app', 'app.log'), log_paths.get('error', 'error.log')]
                }
                sys.stderr.write(f"日志配置失败 [LOG_001] | 日志目录: {error_details['log_dir']} | 子包: {error_details['testcase_group']} | 错误类型: {error_details['error_type']} | 错误信息: {error_details['error_message']} | 尝试创建的文件: {error_details['attempted_files']}\n")
        
        self._initialized = True
    
    @staticmethod
    def get_logger(name: Optional[str] = None) -> 'Logger':
        """获取日志器实例，支持按testcase子包分组
        
        Args:
            name: 日志器名称
            
        Returns:
            日志器实例
        """
        # 创建新的日志配置实例来动态识别子包
        temp_config = LoggerConfig()
        testcase_group = temp_config._get_testcase_group()
        
        if name:
            logger_instance = logger.bind(name=name)
        else:
            logger_instance = logger
            
        # 如果识别到testcase子包，添加子包信息到日志上下文
        if testcase_group:
            logger_instance = logger_instance.bind(testcase_group=testcase_group)
            
        return logger_instance
    
    @staticmethod
    def log_test_start(test_name: str) -> None:
        """记录测试开始
        
        Args:
            test_name: 测试名称
        """
        logger.info(f"开始执行测试: {test_name}")
    
    @staticmethod
    def log_test_end(test_name: str, result: str, duration: Optional[float] = None) -> None:
        """记录测试结束
        
        Args:
            test_name: 测试名称
            result: 测试结果 (PASSED/FAILED/SKIPPED)
            duration: 执行时长(秒)
        """
        duration_str = f" (耗时: {duration:.2f}s)" if duration else ""
        logger.info(f"测试完成: {test_name} - {result}{duration_str}")
    
    @staticmethod
    def log_step(step_name: str) -> None:
        """记录测试步骤
        
        Args:
            step_name: 步骤名称
        """
        logger.info(f"执行步骤: {step_name}")
    
    @staticmethod
    def log_screenshot(screenshot_path: str, description: str = "") -> None:
        """记录截图信息
        
        Args:
            screenshot_path: 截图路径
            description: 截图描述
        """
        desc = f" - {description}" if description else ""
        logger.info(f"截图已保存: {screenshot_path}{desc}")
    
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
        logger.debug(f"页面操作: {action}{element_str}{value_str}")


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
    """获取日志器实例，支持按testcase子包分组
    
    Args:
        name: 日志器名称
        
    Returns:
        日志器实例
    """
    return LoggerConfig.get_logger(name)