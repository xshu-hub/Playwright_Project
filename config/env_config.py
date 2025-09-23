"""环境配置管理 - YAML版本"""
import os
import yaml
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
from functools import lru_cache
from pathlib import Path

# 获取日志记录器
logger = logging.getLogger(__name__)


class EnvironmentConfig(BaseModel):
    """环境配置模型"""
    name: str
    browser_timeout: int = Field(default=30000, description="浏览器超时时间(毫秒)")
    navigation_timeout: int = Field(default=60000, description="页面导航超时时间(毫秒)")
    element_timeout: int = Field(default=30000, description="元素操作超时时间(毫秒)")  # 更新默认值为30秒
    headless: bool = Field(default=True, description="是否无头模式")
    slow_mo: int = Field(default=0, description="慢动作延迟(毫秒)")
    video_record: bool = Field(default=False, description="是否录制视频")
    screenshot_on_failure: bool = Field(default=True, description="失败时是否截图")
    retry_times: int = Field(default=2, description="重试次数")
    
    class Config:
        use_enum_values = True


# 默认环境配置
DEFAULT_CONFIG = EnvironmentConfig(
    name="默认配置",
    browser_timeout=30000,
    navigation_timeout=60000,
    element_timeout=30000,  # 增加元素超时时间从10秒到30秒
    headless=True,
    video_record=True
)


class ConfigManager:
    """配置管理器 - YAML版本"""
    
    def __init__(self, config_file: str = None):
        """
        初始化配置管理器
        
        Args:
            config_file: YAML配置文件路径，默认为config/config.yaml
        """
        self._config_file = config_file or self._get_default_config_path()
        self._config = None
        self._yaml_config = None
        self._load_yaml_config()
        
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        current_dir = Path(__file__).parent
        config_path = current_dir / "config.yaml"
        return str(config_path)
        
    def _load_yaml_config(self) -> None:
        """从YAML文件加载配置"""
        try:
            config_path = Path(self._config_file)
            if not config_path.exists():
                logger.error(f"配置文件不存在: {self._config_file}")
                self._config = DEFAULT_CONFIG.model_copy()
                return
                
            with open(config_path, 'r', encoding='utf-8') as file:
                self._yaml_config = yaml.safe_load(file) or {}
                
            # 直接使用根级配置创建EnvironmentConfig实例
            config_data = {'name': '基础配置', **self._yaml_config}
            self._config = EnvironmentConfig(**config_data)
            logger.info(f"成功加载配置: {self._config.name}")
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self._config = DEFAULT_CONFIG.model_copy()
        
    def reload_config(self) -> None:
        """重新加载配置"""
        logger.info("重新加载YAML配置...")
        self._invalidate_cache()
        self._load_yaml_config()
        logger.info("配置重新加载完成")
    
    def _invalidate_cache(self) -> None:
        """清除所有缓存"""
        # 清除实例方法的缓存
        if hasattr(self.get_browser_config_dict, 'cache_clear'):
            self.get_browser_config_dict.cache_clear()
        if hasattr(self.get_context_config_dict, 'cache_clear'):
            self.get_context_config_dict.cache_clear()
        if hasattr(self.get_page_config_dict, 'cache_clear'):
            self.get_page_config_dict.cache_clear()
        if hasattr(self.playwright_config, 'cache_clear'):
            self.playwright_config.cache_clear()
        
    @property
    def config(self) -> EnvironmentConfig:
        """获取当前配置"""
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """更新配置"""
        logger.info(f"更新配置: {kwargs}")
        updated_fields = []
        
        for key, value in kwargs.items():
            if not hasattr(self._config, key):
                logger.error(f"无效的配置键: {key}")
                continue
                
            setattr(self._config, key, value)
            updated_fields.append(f"{key}={value}")
            logger.info(f"配置已更新: {key} = {value}")
        
        if updated_fields:
            self._invalidate_cache()
            logger.info(f"配置已更新: {', '.join(updated_fields)}")
    

    
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
    
    def get_retry_times(self) -> int:
        """获取重试次数"""
        return self._config.retry_times
    
    @lru_cache(maxsize=1)
    def get_browser_config_dict(self) -> Dict[str, Any]:
        """获取浏览器配置字典（带缓存）"""
        return {
            'headless': self.is_headless(),
            'args': BROWSER_ARGS,
            'slow_mo': self._config.slow_mo,
        }
    
    @lru_cache(maxsize=1)
    def get_context_config_dict(self) -> Dict[str, Any]:
        """获取上下文配置字典（带缓存）"""
        video_enabled = self._config.video_record
        return {
            'viewport': VIEWPORT_CONFIG,
            'ignore_https_errors': True,
            'java_script_enabled': True,
            'accept_downloads': True,
            'record_video_dir': None,  # 在conftest.py中动态设置
            'record_video_size': VIEWPORT_CONFIG if video_enabled else None,
            'user_agent': os.getenv('USER_AGENT', None),
            'locale': os.getenv('LOCALE', 'zh-CN'),
            'timezone_id': os.getenv('TIMEZONE', 'Asia/Shanghai')
        }
    
    @lru_cache(maxsize=1)
    def get_page_config_dict(self) -> Dict[str, Any]:
        """获取页面配置字典（带缓存）"""
        return {
            'default_navigation_timeout': self.get_navigation_timeout(),
            'default_timeout': self.get_element_timeout(),
        }
    
    @property
    @lru_cache(maxsize=1)
    def playwright_config(self) -> Dict[str, Any]:
        """动态获取 Playwright 配置（带缓存）"""
        return {
            'browser_config': self.get_browser_config_dict(),
            'context_config': self.get_context_config_dict(),
            'page_config': self.get_page_config_dict(),
            'supported_browsers': SUPPORTED_BROWSERS,
            'default_browser': DEFAULT_BROWSER,
            'env_config': self.export_config()
        }
    
    def export_config(self) -> Dict[str, Any]:
        """导出当前配置"""
        return self._config.model_dump()


# 创建全局配置管理器实例
config_manager = ConfigManager()

# ============ YAML配置全局变量 ============

@lru_cache(maxsize=1)
def _load_yaml_global_config():
    """从YAML加载全局配置（带缓存）"""
    try:
        config_path = Path(__file__).parent / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
    except Exception as e:
        logger.warning(f"加载全局YAML配置失败: {e}")
    return {}

# 加载YAML配置
_YAML_CONFIG = _load_yaml_global_config()

# 浏览器配置
_browser_config = _YAML_CONFIG.get('browser', {})
BROWSER_ARGS = _browser_config.get('args', [
    '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu',
    '--disable-web-security', '--allow-running-insecure-content',
    '--disable-features=VizDisplayCompositor'
])
SUPPORTED_BROWSERS = _browser_config.get('supported_browsers', ['chromium', 'firefox', 'webkit'])
DEFAULT_BROWSER = _browser_config.get('default_browser', 'chromium')

# 视窗配置
_viewport_config = _YAML_CONFIG.get('viewport', {})
VIEWPORT_CONFIG = {
    'width': _viewport_config.get('width', 1920),
    'height': _viewport_config.get('height', 1080)
}

# 截图配置
_screenshot_config = _YAML_CONFIG.get('screenshot', {})
SCREENSHOT_CONFIG = {
    'path': _screenshot_config.get('path', 'reports/screenshots'),
    'full_page': _screenshot_config.get('full_page', True),
    'type': _screenshot_config.get('type', 'png')
}

# 重试配置
_retry_config = _YAML_CONFIG.get('retry', {})
RETRY_CONFIG = {
    'max_retries': _retry_config.get('max_retries', 2),
    'retry_delay': _retry_config.get('retry_delay', 1000),
    'retry_on_failure': _retry_config.get('retry_on_failure', True)
}

# 兼容性支持 - 简化的PLAYWRIGHT_CONFIG代理
class _PlaywrightConfigProxy:
    """PLAYWRIGHT_CONFIG代理类，提供动态配置访问"""
    
    @property
    def browser(self) -> Dict[str, Any]:
        return config_manager.get_browser_config_dict()
    
    @property
    def context(self) -> Dict[str, Any]:
        return config_manager.get_context_config_dict()
    
    @property
    def page(self) -> Dict[str, Any]:
        return config_manager.get_page_config_dict()
    
    def __getitem__(self, key: str) -> Any:
        return config_manager.playwright_config[key]
    
    def get(self, key: str, default: Any = None) -> Any:
        return config_manager.playwright_config.get(key, default)

PLAYWRIGHT_CONFIG = _PlaywrightConfigProxy()

# 配置工具函数
def get_config(key: str, default: Any = None) -> Any:
    """获取配置值"""
    return config_manager.playwright_config.get(key, default)

def update_config(updates: Dict[str, Any]) -> None:
    """更新配置"""
    config_manager.update_config(**updates)

def get_browser_config(browser_name: str = None) -> Dict[str, Any]:
    """获取浏览器特定配置"""
    browser = browser_name or DEFAULT_BROWSER
    config = config_manager.get_browser_config_dict().copy()
    
    # Firefox特殊处理
    if browser == 'firefox':
        config['args'] = [arg for arg in config['args'] if not arg.startswith('--disable-web-security')]
    
    return config

def get_env_config() -> Dict[str, Any]:
    """获取环境配置字典"""
    return config_manager.export_config()

def get_playwright_config() -> Dict[str, Any]:
    """获取完整的Playwright配置"""
    return config_manager.playwright_config