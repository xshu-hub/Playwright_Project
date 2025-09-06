"""环境配置管理"""
import os
from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field


class Environment(str, Enum):
    """环境枚举"""
    DEV = "dev"
    TEST = "test"
    STAGING = "staging"
    PROD = "prod"


class EnvironmentConfig(BaseModel):
    """环境配置模型"""
    name: str
    base_url: str
    api_base_url: str = ""
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
    Environment.DEV: EnvironmentConfig(
        name="开发环境",
        base_url="http://localhost:3000",
        api_base_url="http://localhost:8000/api",
        headless=False,
        slow_mo=500,
        video_record=True,
        parallel_workers=2
    ),
    
    Environment.TEST: EnvironmentConfig(
        name="测试环境",
        base_url="https://test.example.com",
        api_base_url="https://test-api.example.com/api",
        headless=True,
        video_record=True,
        parallel_workers=4
    ),
    
    Environment.STAGING: EnvironmentConfig(
        name="预发布环境",
        base_url="https://staging.example.com",
        api_base_url="https://staging-api.example.com/api",
        headless=True,
        video_record=False,
        parallel_workers=6
    ),
    
    Environment.PROD: EnvironmentConfig(
        name="生产环境",
        base_url="https://www.example.com",
        api_base_url="https://api.example.com/api",
        headless=True,
        video_record=False,
        parallel_workers=8,
        retry_times=3
    )
}


class ConfigManager:
    """配置管理器 - 增强版本"""
    
    def __init__(self):
        self._current_env = self._get_current_environment()
        self._config = ENVIRONMENT_CONFIGS[self._current_env]
        self._validation_rules = self._setup_validation_rules()
    
    def _setup_validation_rules(self) -> Dict[str, callable]:
        """设置配置验证规则"""
        return {
            'base_url': lambda x: x.startswith(('http://', 'https://')),
            'api_base_url': lambda x: x.startswith(('http://', 'https://')) or x == '',
            'timeout': lambda x: isinstance(x, int) and x > 0,
            'parallel_workers': lambda x: isinstance(x, int) and 1 <= x <= 20,
            'retry_times': lambda x: isinstance(x, int) and 0 <= x <= 10,
            'slow_mo': lambda x: isinstance(x, int) and x >= 0
        }
    
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
                print(f"警告: 环境 {env_name} 配置不存在，使用默认测试环境")
                return Environment.TEST
            return env
        except ValueError:
            print(f"警告: 未知环境变量值 {env_name}，使用默认测试环境")
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
        print(f"环境已从 {old_env.value} 切换到: {env.value}")
    
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
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                # 验证新值
                if not self._validate_config_value(key, value):
                    print(f"配置更新失败，验证不通过: {key} = {value}")
                    continue
                
                old_value = getattr(self._config, key)
                setattr(self._config, key, value)
                updated_fields.append(f"{key}: {old_value} -> {value}")
            else:
                print(f"警告: 未知配置项: {key}")
        
        if updated_fields:
            print(f"配置已更新: {', '.join(updated_fields)}")
    
    def validate_current_config(self) -> bool:
        """验证当前配置有效性"""
        config_dict = self._config.dict()
        for key, value in config_dict.items():
            if not self._validate_config_value(key, value):
                print(f"配置验证失败: {key} = {value}")
                return False
        return True
    
    def get_base_url(self) -> str:
        """获取基础URL"""
        return self._config.base_url
    
    def get_api_base_url(self) -> str:
        """获取API基础URL"""
        return self._config.api_base_url
    
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
    
    def get_parallel_workers(self) -> int:
        """获取并行工作进程数"""
        return self._config.parallel_workers
    
    def get_retry_times(self) -> int:
        """获取重试次数"""
        return self._config.retry_times
    
    def get_all_environments(self) -> list:
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