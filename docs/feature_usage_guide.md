# 功能使用指南

本文档详细介绍了 Playwright Web UI 自动化测试框架中各项功能的使用方法。

## 📸 截图功能

### 使用步骤

#### 1. 自动截图（推荐）

```python
# 测试失败时自动截图，无需额外代码
def test_login_failure(self, page):
    login_page = LoginPage(page)
    login_page.login("invalid", "password")
    # 失败时会自动截图到 reports/screenshots/
```

#### 2. 手动截图

```python
def test_manual_screenshot(self, page):
    login_page = LoginPage(page)
    # 步骤截图
    login_page.screenshot_helper.take_step_screenshot("登录页面加载")
    
    # 元素截图
    login_page.screenshot_helper.take_element_screenshot(
        "#loginForm", 
        "login_form.png", 
        "登录表单截图"
    )
```

### 实现原理

- **自动截图**：通过 `conftest.py` 中的 `pytest_runtest_makereport` 钩子函数实现
- **截图存储**：按测试会话创建独立目录，避免文件冲突
- **多格式支持**：支持 PNG、JPEG 格式，可配置压缩质量

### 技术细节

```python
# 截图配置
SCREENSHOT_CONFIG = {
    'path': 'reports/screenshots',
    'full_page': True,
    'type': 'png',
    'animations': 'disabled'  # 禁用动画，确保截图稳定
}
```

## 🎥 视频录制功能

### 使用步骤

#### 1. 环境变量配置

```bash
# .env 文件
RECORD_VIDEO=true
```

#### 2. 程序化控制

```python
def test_with_video(self, page, context):
    video_helper = VideoHelper(context)
    video_helper.start_recording("test_login")
    
    # 执行测试步骤
    login_page = LoginPage(page)
    login_page.login("admin", "password")
    
    # 保存视频
    video_path = video_helper.stop_recording(save_video=True)
```

### 实现原理

- **上下文级录制**：在浏览器上下文创建时启用录制
- **条件保存**：支持仅在失败时保存视频，节省存储空间
- **格式优化**：使用 WebM 格式，平衡文件大小和质量

## 📝 日志系统

### 使用步骤

#### 1. 基础日志记录

```python
from utils.logger_config import logger_config
from loguru import logger

def test_with_logging(self, page):
    logger.info("开始执行登录测试")
    login_page = LoginPage(page)
    
    # 页面操作会自动记录日志
    login_page.navigate()
    login_page.login("admin", "password")
```

#### 2. 自定义日志配置

```python
# 在 conftest.py 或测试文件中
logger_config.setup_logger(
    level="DEBUG",
    console_output=True,
    file_output=True,
    rotation="10 MB",
    retention="30 days"
)
```

### 技术细节

- **去重机制**：5秒内的重复日志会被自动去重
- **多级输出**：同时输出到控制台和文件
- **自动轮转**：支持按大小和时间轮转日志文件
- **结构化日志**：包含时间戳、级别、文件位置等信息

## ❓ 常见问题解决方案

### Q: 截图文件过大怎么办？

A: 调整截图质量和格式

```python
screenshot_helper.take_screenshot(
    quality=60,  # 降低质量
    full_page=False  # 只截取可视区域
)
```

### Q: 视频录制失败？

A: 检查浏览器上下文配置

```python
# 确保在创建上下文时启用录制
CONTEXT_CONFIG = {
    'record_video_dir': 'reports/videos',
    'record_video_size': {'width': 1920, 'height': 1080}
}
```

### Q: 日志文件过多？

A: 配置自动清理

```python
logger_config.setup_logger(
    retention="7 days",  # 只保留7天
    compression="zip"    # 压缩旧日志
)
```

## 🔧 高级配置

### 截图高级配置

```python
# 自定义截图配置
class CustomScreenshotHelper(ScreenshotHelper):
    def __init__(self, page):
        super().__init__(page)
        self.config = {
            'path': 'custom/screenshots',
            'quality': 80,
            'full_page': True,
            'clip': {'x': 0, 'y': 0, 'width': 1920, 'height': 1080}
        }
```

### 视频录制高级配置

```python
# 自定义视频配置
VIDEO_CONFIG = {
    'dir': 'reports/videos',
    'size': {'width': 1920, 'height': 1080},
    'mode': 'retain-on-failure'  # 仅失败时保留
}
```

### 日志系统高级配置

```python
# 多环境日志配置
if os.getenv('ENVIRONMENT') == 'production':
    logger_config.setup_logger(
        level="WARNING",
        file_output=True,
        console_output=False
    )
else:
    logger_config.setup_logger(
        level="DEBUG",
        file_output=True,
        console_output=True
    )
```

## 📊 性能优化建议

### 截图优化

1. **按需截图**：只在关键步骤或失败时截图
2. **压缩设置**：合理设置图片质量，平衡文件大小和清晰度
3. **定期清理**：定期清理旧的截图文件

### 视频录制优化

1. **条件录制**：只在需要时启用视频录制
2. **分辨率控制**：根据需要调整录制分辨率
3. **存储管理**：及时清理不需要的视频文件

### 日志系统优化

1. **级别控制**：生产环境使用较高的日志级别
2. **轮转策略**：合理设置日志轮转策略
3. **异步写入**：对于高频日志，考虑使用异步写入