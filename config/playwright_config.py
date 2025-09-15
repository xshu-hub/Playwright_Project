"""Playwright 配置文件"""
from playwright.sync_api import Playwright
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 环境变量配置
ENV = os.getenv('TEST_ENV', 'test')

# 基础配置（超时和无头模式配置已移至 env_config.py）
SLOW_MO = int(os.getenv('SLOW_MO', '500'))

# 浏览器配置
BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-web-security',
    '--allow-running-insecure-content',
    '--disable-features=VizDisplayCompositor'
]

# 浏览器配置（动态获取无头模式设置）
def get_browser_config_dict():
    from config.env_config import config_manager
    return {
        'headless': config_manager.is_headless(),
        'args': BROWSER_ARGS,
        'slow_mo': SLOW_MO,
    }

BROWSER_CONFIG = get_browser_config_dict()

# 上下文配置
VIEWPORT_CONFIG = {
    'width': int(os.getenv('VIEWPORT_WIDTH', '1920')),
    'height': int(os.getenv('VIEWPORT_HEIGHT', '1080'))
}

# 上下文配置（动态获取视频录制设置）
def get_context_config_dict():
    from config.env_config import config_manager
    video_enabled = config_manager.config.video_record
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

CONTEXT_CONFIG = get_context_config_dict()

# 页面配置（动态获取超时设置）
def get_page_config_dict():
    from config.env_config import config_manager
    return {
        'default_navigation_timeout': config_manager.get_navigation_timeout(),
        'default_timeout': config_manager.get_element_timeout(),
    }

PAGE_CONFIG = get_page_config_dict()

# 支持的浏览器
SUPPORTED_BROWSERS = ['chromium', 'firefox', 'webkit']
DEFAULT_BROWSER = os.getenv('BROWSER', 'chromium')

# 截图配置
SCREENSHOT_CONFIG = {
    'path': 'reports/screenshots',
    'full_page': True,
    'type': 'png'
}

# 并行测试配置已移至 env_config.py 统一管理

# 重试配置
RETRY_CONFIG = {
    'max_retries': int(os.getenv('MAX_RETRIES', '2')),
    'retry_delay': int(os.getenv('RETRY_DELAY', '1000')),
    'retry_on_failure': os.getenv('RETRY_ON_FAILURE', 'true').lower() == 'true'
}

# 环境特定配置已移至 env_config.py 统一管理
# ENV_CONFIGS 已废弃，请使用 config.env_config.config_manager

# 获取当前环境配置
def get_env_config() -> Dict[str, Any]:
    """获取当前环境配置"""
    from config.env_config import config_manager
    env_config = config_manager.config
    return {
        'headless': env_config.headless,
        'slow_mo': env_config.slow_mo,
        'browser_timeout': env_config.browser_timeout,
        'navigation_timeout': env_config.navigation_timeout,
        'element_timeout': env_config.element_timeout,
        'video_record': env_config.video_record,
        'screenshot_on_failure': env_config.screenshot_on_failure,
        'parallel_workers': env_config.parallel_workers,
        'retry_times': env_config.retry_times
    }

# 主配置字典
# 主配置字典（动态配置）
def get_playwright_config():
    return {
        'env': ENV,
        'browser_config': get_browser_config_dict(),
        'context_config': get_context_config_dict(),
        'page_config': get_page_config_dict(),
        'supported_browsers': SUPPORTED_BROWSERS,
        'default_browser': DEFAULT_BROWSER,
        'screenshot_config': SCREENSHOT_CONFIG,
        'retry_config': RETRY_CONFIG
    }

PLAYWRIGHT_CONFIG = get_playwright_config()

# 配置工具函数
def get_config(key: str, default: Any = None) -> Any:
    """获取配置值"""
    return PLAYWRIGHT_CONFIG.get(key, default)

def update_config(updates: Dict[str, Any]) -> None:
    """更新配置"""
    PLAYWRIGHT_CONFIG.update(updates)

def get_browser_config(browser_name: str = None) -> Dict[str, Any]:
    """获取浏览器特定配置"""
    browser = browser_name or DEFAULT_BROWSER
    config = BROWSER_CONFIG.copy()
    
    # 根据浏览器类型调整配置
    if browser == 'firefox':
        config['args'] = [arg for arg in config['args'] if not arg.startswith('--disable-web-security')]
    
    return config