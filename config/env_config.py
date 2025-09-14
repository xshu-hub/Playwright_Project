"""环境配置管理"""
import os
from enum import Enum
from typing import Dict, Any, Optional, Union, List, Callable
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pathlib import Path
from loguru import logger

# 加载.env文件
load_dotenv()


class Environment(str, Enum):
    """环境枚举"""
    TEST = "test"
    PROD = "prod"


class EnvironmentConfig(BaseModel):
    """环境配置模型"""
    name: str
    timeout: int = Field(default=30000, description="默认超时时间(毫秒)")
    headless: bool = Field(default=True, description="是否无头模式")
    slow_mo: int = Field(default=0, description="慢动作延迟(毫秒)")
    video_record: bool = Field(default=False, description="是否录制视频")
    screenshot_on_failure: bool = Field(default=True, description="失败时是否截图")
    parallel_workers: int = Field(default=4, description="并行工作进程数")
    retry_times: int = Field(default=2, description="重试次数")
    
    class Config:
        use_enum_values = True


# 环境配置字典
ENVIRONMENT_CONFIGS: Dict[Environment, EnvironmentConfig] = {
    Environment.TEST: EnvironmentConfig(
        name="测试环境",
        headless=True,
        video_record=True,
        parallel_workers=4
    ),
    
    Environment.PROD: EnvironmentConfig(
        name="生产环境",
        headless=True,
        video_record=False,
        parallel_workers=8,
        retry_times=3
    )
}


class ConfigManager:
    """配置管理器"""

    def __init__(self) -> None:
        self._current_env: Environment = self._get_current_environment()
        self._config: EnvironmentConfig = ENVIRONMENT_CONFIGS[self._current_env]
        self._validation_rules: Dict[str, Callable[[Any], bool]] = self._setup_validation_rules()
    
    def _setup_validation_rules(self) -> Dict[str, Callable[[Any], bool]]:
        """设置配置验证规则"""
        return {
            'timeout': lambda x: self._validate_timeout(x),
            'headless': lambda x: isinstance(x, bool),
            'slow_mo': lambda x: isinstance(x, int) and 0 <= x <= 5000,
            'parallel_workers': lambda x: self._validate_parallel_workers(x),
            'retry_times': lambda x: isinstance(x, int) and 0 <= x <= 10,
            'video_record': lambda x: isinstance(x, bool),
            'screenshot_on_failure': lambda x: isinstance(x, bool)
        }
    
    def _validate_timeout(self, value: Any) -> bool:
        """验证超时时间"""
        if not isinstance(value, int):
            return False
        return 1000 <= value <= 300000  # 1秒到5分钟
    
    def _validate_parallel_workers(self, value: Any) -> bool:
        """验证并行工作进程数"""
        if isinstance(value, str) and value.lower() == 'auto':
            return True
        if not isinstance(value, int):
            return False
        return 1 <= value <= 16  # 1到16个进程
    
    def _validate_config_value(self, key: str, value: Any) -> bool:
        """验证配置值"""
        if key in self._validation_rules:
            return self._validation_rules[key](value)
        return True
    
    def _get_current_environment(self) -> Environment:
        """获取当前环境"""
        env_name = os.getenv('TEST_ENV', Environment.TEST.value).lower()
        try:
            env = Environment(env_name)
            # 验证环境配置是否存在
            if env not in ENVIRONMENT_CONFIGS:
                logger.warning(f"警告: 环境 {env_name} 配置不存在，使用默认测试环境")
                return Environment.TEST
            return env
        except ValueError:
            logger.warning(f"警告: 未知环境变量值 {env_name}，使用默认测试环境")
            return Environment.TEST
    
    def set_environment(self, env: Environment) -> None:
        """设置当前环境"""
        if env not in Environment:
            raise ValueError(f"不支持的环境: {env}")
        
        if env not in ENVIRONMENT_CONFIGS:
            raise ValueError(f"未找到环境配置: {env.value}")
        
        old_env = self._current_env
        self._current_env = env
        self._config = ENVIRONMENT_CONFIGS[env]
        logger.info(f"环境已从 {old_env.value} 切换到: {env.value}")
    
    @property
    def current_env(self) -> Environment:
        """当前环境"""
        return self._current_env
    
    @property
    def config(self) -> EnvironmentConfig:
        """当前环境配置"""
        return self._config
    
    def get_config(self, env: Environment = None) -> EnvironmentConfig:
        """获取指定环境配置"""
        if env is None:
            env = self._current_env
        
        if env not in ENVIRONMENT_CONFIGS:
            raise ValueError(f"未找到环境配置: {env.value}")
        
        return ENVIRONMENT_CONFIGS[env]
    
    def update_config(self, **kwargs) -> None:
        """更新当前环境配置"""
        updated_fields = []
        errors = []
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                # 尝试类型转换
                converted_value = self._convert_config_value(key, value)
                if converted_value is None:
                    errors.append(f"配置类型转换失败: {key} = {value}")
                    continue
                
                # 验证新值
                if not self._validate_config_value(key, converted_value):
                    errors.append(f"配置验证失败: {key} = {converted_value}")
                    continue
                
                old_value = getattr(self._config, key)
                setattr(self._config, key, converted_value)
                updated_fields.append(f"{key}: {old_value} -> {converted_value}")
            else:
                errors.append(f"未知配置项: {key}")
        
        if errors:
            logger.error(f"配置更新错误: {'; '.join(errors)}")
        if updated_fields:
            logger.info(f"配置已更新: {', '.join(updated_fields)}")
    
    def _convert_config_value(self, key: str, value: Any) -> Optional[Any]:
        """转换配置值类型"""
        try:
            if key == 'timeout' and isinstance(value, str):
                return int(value)
            elif key == 'headless' and isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            elif key == 'slow_mo' and isinstance(value, str):
                return int(value)
            elif key == 'parallel_workers' and isinstance(value, str):
                if value.lower() == 'auto':
                    return 'auto'
                return int(value)
            elif key == 'retry_times' and isinstance(value, str):
                return int(value)
            elif key in ('video_record', 'screenshot_on_failure') and isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return value
        except (ValueError, TypeError):
            return None
    
    def validate_current_config(self) -> bool:
        """验证当前配置有效性"""
        config_dict = self._config.dict()
        for key, value in config_dict.items():
            if not self._validate_config_value(key, value):
                logger.warning(f"配置验证失败: {key} = {value}")
                return False
        return True
    

    
    def is_headless(self) -> bool:
        """是否无头模式"""
        return self._config.headless
    
    def get_timeout(self) -> int:
        """获取超时时间"""
        return self._config.timeout
    
    def should_record_video(self) -> bool:
        """是否应该录制视频"""
        return self._config.video_record
    
    def should_screenshot_on_failure(self) -> bool:
        """失败时是否截图"""
        return self._config.screenshot_on_failure
    
    def get_parallel_workers(self) -> Union[int, str]:
        """获取并行工作进程数"""
        # 优先使用环境变量PARALLEL_WORKERS
        env_workers = os.getenv('PARALLEL_WORKERS')
        if env_workers:
            # 处理特殊值
            if env_workers.lower() == 'auto':
                return 'auto'
            try:
                workers = int(env_workers)
                if workers <= 0:
                    return 'auto'
                return workers
            except ValueError:
                logger.warning(f"警告: PARALLEL_WORKERS环境变量值无效 '{env_workers}'，使用默认配置")
        
        # 使用配置文件中的默认值
        return self._config.parallel_workers
    
    def get_retry_times(self) -> int:
        """获取重试次数"""
        return self._config.retry_times
    
    def get_all_environments(self) -> List[str]:
        """获取所有可用环境"""
        return [env.value for env in Environment]
    
    def export_config(self) -> Dict[str, Any]:
        """导出当前配置"""
        return {
            'environment': self._current_env.value,
            'config': self._config.dict()
        }


# 全局配置管理器实例
config_manager = ConfigManager()