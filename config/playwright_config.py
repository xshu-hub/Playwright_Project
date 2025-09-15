"""Playwright 配置文件"""
from playwright.sync_api import Playwright
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from loguru import logger

# 加载 .env 文件
load_dotenv()

# 环境变量配置
ENV = os.getenv('TEST_ENV', 'test')

# 浏览器配置
BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-web-security',
    '--allow-running-insecure-content',
    '--disable-features=VizDisplayCompositor'
]

def get_browser_config() -> Dict[str, Any]:
    """获取浏览器配置，结合环境配置"""
    from config.env_config import config_manager
    env_config = config_manager.config
    
    return {
        'headless': env_config.headless,
        'args': BROWSER_ARGS,
        'slow_mo': env_config.slow_mo,
    }

# 上下文配置
VIEWPORT_CONFIG = {
    'width': int(os.getenv('VIEWPORT_WIDTH', '1920')),
    'height': int(os.getenv('VIEWPORT_HEIGHT', '1080'))
}

CONTEXT_CONFIG = {
    'viewport': VIEWPORT_CONFIG,
    'ignore_https_errors': True,
    'java_script_enabled': True,
    'accept_downloads': True,
    'record_video_dir': 'reports/videos' if os.getenv('RECORD_VIDEO', 'true').lower() == 'true' else None,
    'record_video_size': VIEWPORT_CONFIG,
    'user_agent': os.getenv('USER_AGENT', None),
    'locale': os.getenv('LOCALE', 'zh-CN'),
    'timezone_id': os.getenv('TIMEZONE', 'Asia/Shanghai')
}

# 页面配置 - 使用env_config.py中的超时配置
def get_page_config() -> Dict[str, Any]:
    """获取页面配置，使用统一的超时管理"""
    from config.env_config import config_manager
    env_config = config_manager.config
    
    return {
        'default_navigation_timeout': env_config.timeout,
        'default_timeout': env_config.timeout,
    }

# 支持的浏览器
SUPPORTED_BROWSERS = ['chromium', 'firefox', 'webkit']
DEFAULT_BROWSER = os.getenv('BROWSER', 'chromium')

# 截图配置
SCREENSHOT_CONFIG = {
    'path': 'reports/screenshots',
    'full_page': True,
    'type': 'png'
}

# 主配置字典 - 仅包含Playwright特定配置
def get_playwright_config() -> Dict[str, Any]:
    """获取完整的Playwright配置"""
    return {
        'env': ENV,
        'browser_config': get_browser_config(),
        'context_config': CONTEXT_CONFIG,
        'page_config': get_page_config(),
        'supported_browsers': SUPPORTED_BROWSERS,
        'default_browser': DEFAULT_BROWSER,
        'screenshot_config': SCREENSHOT_CONFIG
    }

# 向后兼容
PLAYWRIGHT_CONFIG = get_playwright_config()

# 配置工具函数
def get_config(key: str, default: Any = None) -> Any:
    """获取配置值"""
    return PLAYWRIGHT_CONFIG.get(key, default)

def update_config(updates: Dict[str, Any]) -> None:
    """更新配置"""
    PLAYWRIGHT_CONFIG.update(updates)

def get_browser_specific_config(browser_name: str = None) -> Dict[str, Any]:
    """获取浏览器特定配置"""
    browser = browser_name or DEFAULT_BROWSER
    config = get_browser_config().copy()
    
    # 根据浏览器类型调整配置
    if browser == 'firefox':
        config['args'] = [arg for arg in config['args'] if not arg.startswith('--disable-web-security')]
    
    return config