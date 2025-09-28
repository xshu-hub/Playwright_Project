"""简化的环境配置管理"""
import os
import yaml
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pathlib import Path


class EnvironmentConfig(BaseModel):
    """环境配置模型"""
    name: str = "默认配置"
    browser_timeout: int = Field(default=30000, description="浏览器超时时间(毫秒)")
    navigation_timeout: int = Field(default=60000, description="页面导航超时时间(毫秒)")
    element_timeout: int = Field(default=30000, description="元素操作超时时间(毫秒)")
    headless: bool = Field(default=True, description="是否无头模式")
    slow_mo: int = Field(default=0, description="慢动作延迟(毫秒)")
    video_record: bool = Field(default=True, description="是否录制视频")
    screenshot_on_failure: bool = Field(default=True, description="失败时是否截图")
    retry_times: int = Field(default=2, description="重试次数")


class ConfigManager:
    """简化的配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        """初始化配置管理器"""
        self._config_file = config_file or self._get_default_config_path()
        self._config = self._load_config()
        
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        return str(Path(__file__).parent / "config.yaml")
        
    def _load_config(self) -> EnvironmentConfig:
        """从YAML文件加载配置"""
        try:
            config_path = Path(self._config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as file:
                    yaml_config = yaml.safe_load(file) or {}
                return EnvironmentConfig(**yaml_config)
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
        
        return EnvironmentConfig()
    
    @property
    def config(self) -> EnvironmentConfig:
        """获取当前配置"""
        return self._config
    
    def get_browser_config(self) -> Dict[str, Any]:
        """获取浏览器配置"""
        return {
            'headless': self._config.headless,
            'args': BROWSER_ARGS,
            'slow_mo': self._config.slow_mo,
        }
    
    def get_context_config(self) -> Dict[str, Any]:
        """获取上下文配置"""
        return {
            'viewport': VIEWPORT_CONFIG,
            'ignore_https_errors': True,
            'java_script_enabled': True,
            'accept_downloads': True,
            'record_video_size': VIEWPORT_CONFIG if self._config.video_record else None,
            'locale': 'zh-CN',
            'timezone_id': 'Asia/Shanghai'
        }
    
    def get_page_config(self) -> Dict[str, Any]:
        """获取页面配置"""
        return {
            'default_navigation_timeout': self._config.navigation_timeout,
            'default_timeout': self._config.element_timeout,
        }


# 加载YAML配置
def _load_yaml_config() -> Dict[str, Any]:
    """加载YAML配置"""
    try:
        config_path = Path(__file__).parent / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
    except Exception:
        pass
    return {}


# 全局配置
_YAML_CONFIG = _load_yaml_config()

# 浏览器配置
_browser_config = _YAML_CONFIG.get('browser', {})
BROWSER_ARGS = _browser_config.get('args', [
    '--no-sandbox', 
    '--disable-dev-shm-usage', 
    '--disable-gpu',
    '--disable-web-security', 
    '--allow-running-insecure-content'
])
SUPPORTED_BROWSERS = _browser_config.get('supported_browsers', ['chromium', 'firefox', 'webkit'])
DEFAULT_BROWSER = _browser_config.get('default_browser', 'chromium')

# 视窗配置
_viewport_config = _YAML_CONFIG.get('viewport', {})
VIEWPORT_CONFIG = {
    'width': _viewport_config.get('width', 1920),
    'height': _viewport_config.get('height', 1080)
}

# 创建全局配置管理器实例
config_manager = ConfigManager()

# 兼容性配置代理
class _PlaywrightConfigProxy:
    """PLAYWRIGHT_CONFIG代理类"""
    
    @property
    def browser_config(self) -> Dict[str, Any]:
        return config_manager.get_browser_config()
    
    @property
    def context_config(self) -> Dict[str, Any]:
        return config_manager.get_context_config()
    
    @property
    def page_config(self) -> Dict[str, Any]:
        return config_manager.get_page_config()
    
    @property
    def default_browser(self) -> str:
        return DEFAULT_BROWSER
    
    @property
    def supported_browsers(self) -> list:
        return SUPPORTED_BROWSERS
    
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key, None)
    
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


PLAYWRIGHT_CONFIG = _PlaywrightConfigProxy()