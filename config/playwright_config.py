"""Playwright 配置文件"""
from playwright.sync_api import Playwright
import os

# 基础配置
BASE_URL = os.getenv('BASE_URL', 'https://example.com')
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', '30000'))
NAVIGATION_TIMEOUT = int(os.getenv('NAVIGATION_TIMEOUT', '30000'))
ELEMENT_TIMEOUT = int(os.getenv('ELEMENT_TIMEOUT', '10000'))

# 浏览器配置
BROWSER_CONFIG = {
    'headless': HEADLESS,
    'args': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-web-security',
        '--allow-running-insecure-content',
        '--disable-features=VizDisplayCompositor'
    ],
    'slow_mo': int(os.getenv('SLOW_MO', '0')),
}

# 上下文配置
CONTEXT_CONFIG = {
    'viewport': {'width': 1920, 'height': 1080},
    'ignore_https_errors': True,
    'java_script_enabled': True,
    'accept_downloads': True,
    'record_video_dir': 'reports/videos' if os.getenv('RECORD_VIDEO', 'true').lower() == 'true' else None,  # 默认启用视频录制
    'record_video_size': {'width': 1920, 'height': 1080},
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
PARALLEL_WORKERS = int(os.getenv('PARALLEL_WORKERS', '4'))

# 重试配置
RETRY_CONFIG = {
    'max_retries': int(os.getenv('MAX_RETRIES', '2')),
    'retry_delay': int(os.getenv('RETRY_DELAY', '1000'))
}

# 主配置字典
PLAYWRIGHT_CONFIG = {
    'base_url': BASE_URL,
    'headless': HEADLESS,
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