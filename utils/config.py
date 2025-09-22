"""YAML配置管理器

基于YAML文件的配置管理系统，支持多环境配置
"""
import os
import yaml
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """环境枚举"""
    TEST = "test"
    PROD = "prod"
    DEV = "dev"


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


class ConfigManager:
    """YAML配置管理器"""

    def __init__(self, config_file: str = None):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径，默认为项目根目录下的config.yaml
        """
        if config_file is None:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_file = os.path.join(project_root, "config.yaml")
        
        self.config_file = config_file
        self._raw_config = self._load_yaml_config()
        self._current_env = self._get_current_environment()
        self._config = self._create_environment_config()
        self._validation_rules = self._setup_validation_rules()
        
        logger.info(f"配置管理器初始化完成，当前环境: {self._current_env}")

    def _load_yaml_config(self) -> Dict[str, Any]:
        """加载YAML配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"成功加载配置文件: {self.config_file}")
                return config
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {self.config_file}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"YAML配置文件解析错误: {e}")
            raise
        except Exception as e:
            logger.error(f"加载配置文件时发生错误: {e}")
            raise

    def _get_current_environment(self) -> Environment:
        """获取当前环境"""
        # 优先从环境变量获取
        env_from_var = os.getenv('PLAYWRIGHT_ENV', '').lower()
        if env_from_var and env_from_var in [e.value for e in Environment]:
            return Environment(env_from_var)
        
        # 从配置文件获取
        current_env = self._raw_config.get('current_environment', 'test')
        try:
            return Environment(current_env)
        except ValueError:
            logger.warning(f"无效的环境配置: {current_env}，使用默认环境: test")
            return Environment.TEST

    def _create_environment_config(self) -> EnvironmentConfig:
        """创建环境配置对象"""
        env_configs = self._raw_config.get('environments', {})
        current_env_config = env_configs.get(self._current_env.value, {})
        
        if not current_env_config:
            logger.warning(f"未找到环境 {self._current_env} 的配置，使用默认配置")
            current_env_config = {
                'name': f'{self._current_env}环境',
                'browser_timeout': 30000,
                'navigation_timeout': 60000,
                'element_timeout': 10000,
                'headless': True,
                'slow_mo': 0,
                'video_record': False,
                'screenshot_on_failure': True,
                'parallel_workers': 4,
                'retry_times': 2
            }
        
        return EnvironmentConfig(**current_env_config)

    @staticmethod
    def _setup_validation_rules() -> Dict[str, callable]:
        """设置配置验证规则"""
        return {
            'browser_timeout': lambda x: isinstance(x, int) and x > 0,
            'navigation_timeout': lambda x: isinstance(x, int) and x > 0,
            'element_timeout': lambda x: isinstance(x, int) and x > 0,
            'parallel_workers': lambda x: isinstance(x, int) and 1 <= x <= 16,
            'retry_times': lambda x: isinstance(x, int) and x >= 0,
            'slow_mo': lambda x: isinstance(x, int) and x >= 0,
        }

    def _validate_config_value(self, key: str, value: Any) -> bool:
        """验证配置值"""
        if key in self._validation_rules:
            return self._validation_rules[key](value)
        return True

    def set_environment(self, env: Environment) -> None:
        """设置当前环境"""
        if env != self._current_env:
            logger.info(f"切换环境: {self._current_env} -> {env}")
            self._current_env = env
            self._config = self._create_environment_config()

    @property
    def current_env(self) -> Environment:
        """获取当前环境"""
        return self._current_env

    @property
    def config(self) -> EnvironmentConfig:
        """获取当前环境配置"""
        return self._config

    def get_config(self, env: Environment = None) -> EnvironmentConfig:
        """获取指定环境的配置"""
        if env is None:
            return self._config
        
        env_configs = self._raw_config.get('environments', {})
        env_config = env_configs.get(env.value, {})
        return EnvironmentConfig(**env_config) if env_config else self._config

    def update_config(self, **kwargs) -> None:
        """更新当前环境配置"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                if self._validate_config_value(key, value):
                    setattr(self._config, key, value)
                    logger.info(f"配置更新: {key} = {value}")
                else:
                    logger.warning(f"配置值验证失败: {key} = {value}")
            else:
                logger.warning(f"未知的配置项: {key}")

    def validate_current_config(self) -> bool:
        """验证当前配置"""
        try:
            config_dict = self._config.dict()
            for key, value in config_dict.items():
                if not self._validate_config_value(key, value):
                    logger.error(f"配置验证失败: {key} = {value}")
                    return False
            return True
        except Exception as e:
            logger.error(f"配置验证时发生错误: {e}")
            return False

    # 便捷访问方法
    def is_headless(self) -> bool:
        """是否无头模式"""
        return self._config.headless

    def get_browser_timeout(self) -> int:
        """获取浏览器超时时间"""
        return self._config.browser_timeout

    def get_navigation_timeout(self) -> int:
        """获取导航超时时间"""
        return self._config.navigation_timeout

    def get_element_timeout(self) -> int:
        """获取元素超时时间"""
        return self._config.element_timeout

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

    def get_slow_mo(self) -> int:
        """获取慢动作延迟"""
        return self._config.slow_mo

    # 浏览器配置相关方法
    def get_browser_config(self) -> Dict[str, Any]:
        """获取浏览器配置"""
        browser_config = self._raw_config.get('browser', {})
        return {
            'default': browser_config.get('default', 'chromium'),
            'supported': browser_config.get('supported', ['chromium', 'firefox', 'webkit']),
            'args': browser_config.get('args', [])
        }

    def get_viewport_config(self) -> Dict[str, int]:
        """获取视口配置"""
        viewport = self._raw_config.get('viewport', {})
        return {
            'width': viewport.get('width', 1920),
            'height': viewport.get('height', 1080)
        }

    def get_context_config(self) -> Dict[str, Any]:
        """获取上下文配置"""
        context = self._raw_config.get('context', {})
        return {
            'ignore_https_errors': context.get('ignore_https_errors', True),
            'java_script_enabled': context.get('java_script_enabled', True),
            'accept_downloads': context.get('accept_downloads', True),
            'locale': context.get('locale', 'zh-CN'),
            'timezone_id': context.get('timezone_id', 'Asia/Shanghai')
        }

    def get_screenshot_config(self) -> Dict[str, Any]:
        """获取截图配置"""
        screenshot = self._raw_config.get('screenshot', {})
        return {
            'full_page': screenshot.get('full_page', True),
            'quality': screenshot.get('quality', 90),
            'type': screenshot.get('type', 'png')
        }

    def get_logging_config(self) -> Dict[str, str]:
        """获取日志配置"""
        logging_config = self._raw_config.get('logging', {})
        return {
            'level': logging_config.get('level', 'INFO'),
            'format': logging_config.get('format', '%(asctime)s | %(levelname)s | %(message)s'),
            'date_format': logging_config.get('date_format', '%Y-%m-%d %H:%M:%S')
        }

    @staticmethod
    def get_all_environments() -> list:
        """获取所有支持的环境"""
        return [env.value for env in Environment]

    def export_config(self) -> Dict[str, Any]:
        """导出当前配置"""
        return {
            'current_environment': self._current_env.value,
            'config': self._config.dict(),
            'browser': self.get_browser_config(),
            'viewport': self.get_viewport_config(),
            'context': self.get_context_config(),
            'screenshot': self.get_screenshot_config(),
            'logging': self.get_logging_config()
        }


# 全局配置管理器实例
config_manager = ConfigManager()


class PlaywrightConfigManager:
    """Playwright 配置管理器 - 提供统一的配置访问接口"""
    
    def __init__(self, config_manager: ConfigManager):
        """初始化Playwright配置管理器
        
        Args:
            config_manager: 主配置管理器实例
        """
        self.config_manager = config_manager
        self._browser_args = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--disable-features=VizDisplayCompositor'
        ]
    
    def get_browser_config_dict(self) -> Dict[str, Any]:
        """获取浏览器配置字典"""
        return {
            'headless': self.config_manager.is_headless(),
            'args': self._browser_args,
            'slow_mo': self.config_manager.get_slow_mo(),
        }
    
    def get_context_config_dict(self) -> Dict[str, Any]:
        """获取上下文配置字典"""
        video_enabled = self.config_manager.should_record_video()
        context_config = self.config_manager.get_context_config()
        viewport_config = self.config_manager.get_viewport_config()
        
        return {
            'viewport': viewport_config,
            'ignore_https_errors': context_config.get('ignore_https_errors', True),
            'java_script_enabled': context_config.get('java_script_enabled', True),
            'accept_downloads': context_config.get('accept_downloads', True),
            'record_video_dir': None,  # 在测试运行时动态设置
            'record_video_size': viewport_config if video_enabled else None,
            'user_agent': os.getenv('USER_AGENT', None),
            'locale': context_config.get('locale', 'zh-CN'),
            'timezone_id': context_config.get('timezone_id', 'Asia/Shanghai')
        }
    
    def get_page_config_dict(self) -> Dict[str, Any]:
        """获取页面配置字典"""
        return {
            'default_navigation_timeout': self.config_manager.get_navigation_timeout(),
            'default_timeout': self.config_manager.get_element_timeout(),
        }
    
    def get_playwright_config(self) -> Dict[str, Any]:
        """获取完整的Playwright配置"""
        browser_config = self.config_manager.get_browser_config()
        return {
            'browser_config': self.get_browser_config_dict(),
            'context_config': self.get_context_config_dict(),
            'page_config': self.get_page_config_dict(),
            'supported_browsers': browser_config.get('supported', ['chromium', 'firefox', 'webkit']),
            'default_browser': browser_config.get('default', 'chromium'),
        }
    
    def get_browser_config(self, browser_name: str = None) -> Dict[str, Any]:
        """获取浏览器特定配置
        
        Args:
            browser_name: 浏览器名称，如果为None则使用默认浏览器
            
        Returns:
            浏览器配置字典
        """
        browser_config = self.config_manager.get_browser_config()
        browser = browser_name or browser_config.get('default', 'chromium')
        config = self.get_browser_config_dict()
        
        # 根据浏览器类型调整配置
        if browser == 'firefox':
            config['args'] = [arg for arg in config['args'] if not arg.startswith('--disable-web-security')]
        
        return config
    
    def get_context_config(self) -> Dict[str, Any]:
        """获取上下文配置"""
        return self.get_context_config_dict()
    
    def get_page_config(self) -> Dict[str, Any]:
        """获取页面配置"""
        return self.get_page_config_dict()
    
    def get_default_browser(self) -> str:
        """获取默认浏览器"""
        browser_config = self.config_manager.get_browser_config()
        return browser_config.get('default', 'chromium')
    
    def get_supported_browsers(self) -> list:
        """获取支持的浏览器列表"""
        browser_config = self.config_manager.get_browser_config()
        return browser_config.get('supported', ['chromium', 'firefox', 'webkit'])
    
    def is_browser_supported(self, browser_name: str) -> bool:
        """检查浏览器是否支持
        
        Args:
            browser_name: 浏览器名称
            
        Returns:
            是否支持该浏览器
        """
        return browser_name in self.get_supported_browsers()


# 全局Playwright配置管理器实例
playwright_config = PlaywrightConfigManager(config_manager)