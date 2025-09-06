"""Playwright 配置文件"""
from playwright.sync_api import Playwright
import os
from typing import Dict, List, Any, Optional

# 环境变量配置
ENV = os.getenv('TEST_ENV', 'test')
CI_MODE = os.getenv('CI', 'false').lower() == 'true'

# 基础配置
HEADLESS = os.getenv('HEADLESS', 'false' if not CI_MODE else 'true').lower() == 'true'
BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', '30000'))
NAVIGATION_TIMEOUT = int(os.getenv('NAVIGATION_TIMEOUT', '60000'))
ELEMENT_TIMEOUT = int(os.getenv('ELEMENT_TIMEOUT', '10000'))
SLOW_MO = int(os.getenv('SLOW_MO', '0' if CI_MODE else '500'))

# 浏览器配置
BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-web-security',
    '--allow-running-insecure-content',
    '--disable-features=VizDisplayCompositor'
]

# CI环境下添加额外参数
if CI_MODE:
    BROWSER_ARGS.extend([
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-extensions',
        '--no-first-run'
    ])

BROWSER_CONFIG = {
    'headless': HEADLESS,
    'args': BROWSER_ARGS,
    'slow_mo': SLOW_MO,
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
    'record_video_dir': 'reports/videos' if os.getenv('RECORD_VIDEO', 'false' if CI_MODE else 'true').lower() == 'true' else None,
    'record_video_size': VIEWPORT_CONFIG,
    'user_agent': os.getenv('USER_AGENT', None),
    'locale': os.getenv('LOCALE', 'zh-CN'),
    'timezone_id': os.getenv('TIMEZONE', 'Asia/Shanghai')
}

# 页面配置
PAGE_CONFIG = {
    'default_navigation_timeout': NAVIGATION_TIMEOUT,
    'default_timeout': ELEMENT_TIMEOUT,
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

# 并行测试配置
def _get_parallel_workers():
    """获取并行工作进程数，支持auto值"""
    env_workers = os.getenv('PARALLEL_WORKERS', '4')
    if env_workers.lower() == 'auto':
        return 'auto'
    try:
        return int(env_workers)
    except ValueError:
        print(f"警告: PARALLEL_WORKERS环境变量值无效 '{env_workers}'，使用默认值4")
        return 4

PARALLEL_WORKERS = _get_parallel_workers()

# 重试配置
RETRY_CONFIG = {
    'max_retries': int(os.getenv('MAX_RETRIES', '3' if CI_MODE else '2')),
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
        'timeout': env_config.timeout,
        'video_record': env_config.video_record,
        'screenshot_on_failure': env_config.screenshot_on_failure,
        'parallel_workers': env_config.parallel_workers,
        'retry_times': env_config.retry_times
    }

# 主配置字典
PLAYWRIGHT_CONFIG = {
    'env': ENV,
    'ci_mode': CI_MODE,
    'headless': HEADLESS,
    'slow_mo': SLOW_MO,
    'browser_timeout': BROWSER_TIMEOUT,
    'navigation_timeout': NAVIGATION_TIMEOUT,
    'element_timeout': ELEMENT_TIMEOUT,
    'browser_config': BROWSER_CONFIG,
    'context_config': CONTEXT_CONFIG,
    'page_config': PAGE_CONFIG,
    'supported_browsers': SUPPORTED_BROWSERS,
    'default_browser': DEFAULT_BROWSER,
    'screenshot_config': SCREENSHOT_CONFIG,
    'parallel_workers': PARALLEL_WORKERS,
    'retry_config': RETRY_CONFIG
}

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