"""环境配置管理"""
import os
from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


class Environment(str, Enum):
    """环境枚举"""
    TEST = "test"
    PROD = "prod"


class EnvironmentConfig(BaseModel):
    """环境配置模型"""
    name: str
    browser_timeout: int = Field(default=30000, description="浏览器超时时间(毫秒)")
    navigation_timeout: int = Field(default=60000, description="页面导航超时时间(毫秒)")
    element_timeout: int = Field(default=10000, description="元素操作超时时间(毫秒)")
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
        browser_timeout=30000,
        navigation_timeout=60000,
        element_timeout=10000,
        headless=True,
        video_record=True,
        parallel_workers=4
    ),
    
    Environment.PROD: EnvironmentConfig(
        name="生产环境",
        browser_timeout=45000,
        navigation_timeout=90000,
        element_timeout=15000,
        headless=True,
        video_record=False,
        parallel_workers=8,
        retry_times=3
    )
}


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self._current_env = ConfigManager._get_current_environment()
        self._config = ENVIRONMENT_CONFIGS[self._current_env]
        self._validation_rules = ConfigManager._setup_validation_rules()
        # 从环境变量覆盖配置
        self._load_env_overrides()
    
    def _load_env_overrides(self) -> None:
        """从环境变量加载配置覆盖"""
        # 读取HEADLESS环境变量
        headless_env = os.getenv('HEADLESS')
        if headless_env is not None:
            headless_value = headless_env.lower() in ('true', '1', 'yes', 'on')
            self._config.headless = headless_value
            logger.info(f"从环境变量覆盖headless配置: {headless_value}")
        
        # 读取其他可能的环境变量覆盖
        env_mappings = {
            'BROWSER_TIMEOUT': ('browser_timeout', int),
            'NAVIGATION_TIMEOUT': ('navigation_timeout', int),
            'ELEMENT_TIMEOUT': ('element_timeout', int),
            'SLOW_MO': ('slow_mo', int),
            'VIDEO_RECORD': ('video_record', lambda x: x.lower() in ('true', '1', 'yes', 'on')),
            'SCREENSHOT_ON_FAILURE': ('screenshot_on_failure', lambda x: x.lower() in ('true', '1', 'yes', 'on')),
            'PARALLEL_WORKERS': ('parallel_workers', int),
            'RETRY_TIMES': ('retry_times', int)
        }
        
        for env_key, (config_key, converter) in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                try:
                    converted_value = converter(env_value)
                    if self._validate_config_value(config_key, converted_value):
                        setattr(self._config, config_key, converted_value)
                        logger.info(f"从环境变量覆盖{config_key}配置: {converted_value}")
                    else:
                        logger.warning(f"环境变量{env_key}值无效: {env_value}")
                except (ValueError, TypeError) as e:
                    logger.error(f"环境变量{env_key}转换失败: {env_value}, 错误: {e}")
    
    @staticmethod
    def _setup_validation_rules() -> Dict[str, callable]:
        """设置配置验证规则"""
        return {
            'browser_timeout': lambda x: isinstance(x, int) and x > 0,
            'navigation_timeout': lambda x: isinstance(x, int) and x > 0,
            'element_timeout': lambda x: isinstance(x, int) and x > 0,
            'parallel_workers': lambda x: isinstance(x, int) and 1 <= x <= 20,
            'retry_times': lambda x: isinstance(x, int) and 0 <= x <= 10,
            'slow_mo': lambda x: isinstance(x, int) and x >= 0
        }
    
    def _validate_config_value(self, key: str, value: Any) -> bool:
        """验证配置值"""
        if key in self._validation_rules:
            return self._validation_rules[key](value)
        return True
    
    @staticmethod
    def _get_current_environment() -> Environment:
        """获取当前环境"""
        env_name = os.getenv('TEST_ENV', Environment.TEST.value).lower()
        try:
            env = Environment(env_name)
            # 验证环境配置是否存在
            if env not in ENVIRONMENT_CONFIGS:
                logger.warning(f"环境 {env_name} 配置不存在，使用默认测试环境")
                return Environment.TEST
            return env
        except ValueError:
            logger.warning(f"未知环境变量值 {env_name}，使用默认测试环境")
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
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                # 验证新值
                if not self._validate_config_value(key, value):
                    logger.error(f"配置更新失败，验证不通过: {key} = {value}")
                    continue
                
                old_value = getattr(self._config, key)
                setattr(self._config, key, value)
                updated_fields.append(f"{key}: {old_value} -> {value}")
            else:
                logger.warning(f"未知配置项: {key}")
        
        if updated_fields:
            logger.info(f"配置已更新: {', '.join(updated_fields)}")
    
    def validate_current_config(self) -> bool:
        """验证当前配置有效性"""
        config_dict = self._config.model_dump()
        for key, value in config_dict.items():
            if not self._validate_config_value(key, value):
                logger.error(f"配置验证失败: {key} = {value}")
                return False
        return True
    

    
    def is_headless(self) -> bool:
        """是否无头模式"""
        return self._config.headless
    
    def get_browser_timeout(self) -> int:
        """获取浏览器超时时间"""
        return self._config.browser_timeout
    
    def get_navigation_timeout(self) -> int:
        """获取页面导航超时时间"""
        return self._config.navigation_timeout
    
    def get_element_timeout(self) -> int:
        """获取元素操作超时时间"""
        return self._config.element_timeout
    
    def should_record_video(self) -> bool:
        """是否应该录制视频"""
        return self._config.video_record
    
    def should_screenshot_on_failure(self) -> bool:
        """失败时是否截图"""
        return self._config.screenshot_on_failure
    
    def get_parallel_workers(self):
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
                logger.warning(f"PARALLEL_WORKERS环境变量值无效 '{env_workers}'，使用默认配置")
        
        # 使用配置文件中的默认值
        return self._config.parallel_workers
    
    def get_retry_times(self) -> int:
        """获取重试次数"""
        return self._config.retry_times
    
    @staticmethod
    def get_all_environments() -> list:
        """获取所有可用环境"""
        return [env.value for env in Environment]
    
    def export_config(self) -> Dict[str, Any]:
        """导出当前配置"""
        return {
            'environment': self._current_env.value,
            'config': self._config.model_dump()
        }


# 全局配置管理器实例
config_manager = ConfigManager()