# Playwright 自动化测试框架

一个基于 Playwright 和 Python 的现代化 Web 自动化测试框架，采用 Page Object Model (POM) 设计模式，提供高效、可维护的测试解决方案。

## 📋 目录

- [项目框架概述](#项目框架概述)
- [快速入门指南](#快速入门指南)
- [核心组件说明](#核心组件说明)
- [页面定位教程](#页面定位教程)
- [代码示例](#代码示例)
- [测试运行](#测试运行)
- [最佳实践](#最佳实践)

## 🏗️ 项目框架概述

### 整体架构设计

本框架采用分层架构设计，确保代码的可维护性和可扩展性：

```
PlaywrightProject/
├── config/           # 配置管理层
│   ├── env_config.py      # 环境配置
│   └── playwright_config.py # Playwright配置
├── pages/            # 页面对象层 (POM)
│   ├── base_page.py       # 基础页面类
│   ├── practice_page.py   # 练习页面类
│   └── simple_practice_page.py # 简化练习页面类
├── tests/            # 测试用例层
│   ├── base_test.py       # 基础测试类
│   ├── test_practice_page.py # 练习页面测试
│   └── test_simple_practice_pom.py # POM模式测试
├── utils/            # 工具服务层
│   ├── logger_config.py   # 日志配置
│   ├── screenshot_helper.py # 截图工具
│   └── video_helper.py    # 视频录制工具
├── conftest.py       # pytest配置和fixture
├── run_tests.py      # 智能测试运行器
└── pytest.ini       # pytest配置文件
```

### 核心特性

- 🎯 **POM设计模式** - 页面对象模型，提高代码复用性和维护性
- 🚀 **智能并行执行** - 自动检测CPU核心数，优化测试执行效率
- 📊 **详细测试报告** - 集成Allure报告，提供可视化测试结果
- 🔧 **灵活配置管理** - 支持多环境配置和参数化测试
- 📸 **自动截图录屏** - 测试失败时自动保存截图和视频
- 🔍 **智能元素定位** - 提供多种定位策略和最佳实践

## 🚀 快速入门指南

### 环境要求

- Python 3.8+
- Node.js 14+ (Playwright依赖)
- Windows/macOS/Linux

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd PlaywrightProject
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **安装浏览器**
   ```bash
   playwright install
   ```

5. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置测试环境参数
   ```

6. **运行测试验证**
   ```bash
   python run_tests.py tests/test_simple_practice_pom.py -v
   ```

## 🔧 核心组件说明

### 配置类详解

#### 1. 环境配置 (env_config.py)

```python
from config.env_config import EnvConfig

# 获取配置实例
config = EnvConfig()

# 使用配置
base_url = config.get_base_url()  # 获取基础URL
timeout = config.get_timeout()    # 获取超时时间
browser = config.get_browser()    # 获取浏览器类型
```

**配置示例：**
```bash
# .env 文件
BASE_URL=https://example.com
BROWSER=chromium
HEADLESS=false
TIMEOUT=30000
PARALLEL_WORKERS=auto
```

#### 2. Playwright配置 (playwright_config.py)

```python
from config.playwright_config import PlaywrightConfig

# 获取浏览器配置
browser_config = PlaywrightConfig.get_browser_config()
viewport_config = PlaywrightConfig.get_viewport_config()
```

### 工具类使用规范

#### 1. 截图工具 (screenshot_helper.py)

```python
from utils.screenshot_helper import ScreenshotHelper

# 在测试中使用
class TestExample(BaseTest):
    def test_example(self):
        # 自动截图（测试失败时）
        ScreenshotHelper.capture_on_failure(self.page, "test_name")
        
        # 手动截图
        ScreenshotHelper.capture_screenshot(self.page, "custom_screenshot")
```

#### 2. 日志配置 (logger_config.py)

项目使用 **loguru** 作为日志系统，提供了丰富的日志功能和自动化配置。

**基本使用：**
```python
from loguru import logger
from utils.logger_config import logger_config

# 日志系统已在conftest.py中自动初始化，直接使用即可
logger.info("测试开始执行")
logger.error("测试执行失败")
logger.debug("调试信息")
logger.warning("警告信息")
```

**在测试中使用日志工具类：**
```python
class TestWithLogging(BaseTest):
    def test_example(self):
        # 记录测试步骤
        logger_config.log_step("导航到登录页面")
        
        # 记录页面操作
        logger_config.log_page_action("填写用户名", "#username", "testuser")
        
        # 记录断言结果
        logger_config.log_assertion("验证页面标题", True, "实际标题", "期望标题")
        
        # 记录截图
        logger_config.log_screenshot("/path/to/screenshot.png", "登录页面")
```

**日志文件说明：**
- `logs/test.log` - 通用日志文件（INFO级别及以上）
- `logs/error.log` - 错误日志文件（ERROR级别及以上）
- `logs/pytest.log` - pytest框架日志（DEBUG级别）

**日志级别配置：**
```python
# 通过环境变量设置日志级别
set LOG_LEVEL=DEBUG  # Windows
export LOG_LEVEL=DEBUG  # Linux/Mac

# 或在代码中配置
logger_config.setup_logger(
    level="DEBUG",
    console_output=True,
    file_output=True
)
```

**日志功能特性：**
- ✅ 自动日志轮转（10MB轮转，保留30天）
- ✅ 彩色控制台输出
- ✅ 结构化日志格式
- ✅ 测试生命周期自动记录
- ✅ 失败测试自动记录详细信息
- ✅ 多进程安全

## 🎯 页面元素定位教程（新手详解版）

### 📚 基础定位方法详解

#### 1. 通过ID定位

**语法格式：**
```python
# Playwright写法
self.page.locator("#element_id")
# 或者
self.page.locator("[id='element_id']")
```

**适用场景：** ID在页面中是唯一的，适合定位关键元素如登录按钮、主要输入框等。

**优点：** 定位速度快、准确性高、代码简洁
**缺点：** 依赖开发人员设置ID，动态生成的ID可能不稳定

**HTML示例：**
```html
<input id="username" type="text" placeholder="请输入用户名">
<button id="login-btn" type="submit">登录</button>
```

**定位器写法：**
```python
# 定位用户名输入框
username_input = self.page.locator("#username")
# 定位登录按钮
login_button = self.page.locator("#login-btn")
```

#### 2. 通过类名定位

**语法格式：**
```python
# 单个类名
self.page.locator(".class_name")
# 多个类名组合
self.page.locator(".class1.class2")
# 包含特定类的元素
self.page.locator("[class*='partial_class']")
```

**适用场景：** 适合定位具有相同样式或功能的元素组，如按钮组、卡片列表等。

**优点：** 灵活性好，可以批量操作相同类型元素
**缺点：** 类名可能重复，需要结合其他条件精确定位

**HTML示例：**
```html
<button class="btn btn-primary">主要按钮</button>
<button class="btn btn-secondary">次要按钮</button>
<div class="card user-card active">用户卡片</div>
```

**定位器写法：**
```python
# 定位所有按钮
all_buttons = self.page.locator(".btn")
# 定位主要按钮
primary_button = self.page.locator(".btn.btn-primary")
# 定位激活状态的用户卡片
active_user_card = self.page.locator(".user-card.active")
```

#### 3. 通过标签名定位

**语法格式：**
```python
# 基本标签定位
self.page.locator("tag_name")
# 结合属性定位
self.page.locator("tag_name[attribute='value']")
```

**适用场景：** 适合定位特定类型的HTML元素，如所有输入框、所有链接等。

**优点：** 语法简单，适合批量操作
**缺点：** 定位范围太广，通常需要结合其他条件

**HTML示例：**
```html
<form>
  <input type="text" name="username">
  <input type="password" name="password">
  <input type="submit" value="登录">
</form>
<a href="/home">首页</a>
<a href="/about">关于我们</a>
```

**定位器写法：**
```python
# 定位所有输入框
all_inputs = self.page.locator("input")
# 定位文本输入框
text_inputs = self.page.locator("input[type='text']")
# 定位所有链接
all_links = self.page.locator("a")
```

#### 4. 通过名称定位

**语法格式：**
```python
# 通过name属性
self.page.locator("[name='element_name']")
# Playwright专用方法
self.page.get_by_label("标签文本")
self.page.get_by_placeholder("占位符文本")
```

**适用场景：** 适合定位表单元素，特别是具有name属性的输入框。

**优点：** 语义化强，便于理解和维护
**缺点：** 依赖开发人员设置name属性

**HTML示例：**
```html
<form>
  <label for="email">邮箱地址：</label>
  <input name="email" type="email" placeholder="请输入邮箱">
  
  <label for="phone">手机号码：</label>
  <input name="phone" type="tel" placeholder="请输入手机号">
</form>
```

**定位器写法：**
```python
# 通过name属性定位
email_input = self.page.locator("[name='email']")
phone_input = self.page.locator("[name='phone']")

# 通过标签文本定位
email_by_label = self.page.get_by_label("邮箱地址")
# 通过占位符定位
email_by_placeholder = self.page.get_by_placeholder("请输入邮箱")
```

#### 5. 通过链接文本定位

**语法格式：**
```python
# 精确文本匹配
self.page.get_by_text("链接文本")
self.page.get_by_text("链接文本", exact=True)
# 部分文本匹配
self.page.get_by_text("部分文本", exact=False)
# 角色+名称定位
self.page.get_by_role("link", name="链接文本")
```

**适用场景：** 适合定位导航链接、按钮等具有明确文本的元素。

**优点：** 直观易懂，不依赖HTML结构
**缺点：** 文本变化会导致定位失败，多语言环境需要特殊处理

**HTML示例：**
```html
<nav>
  <a href="/home">首页</a>
  <a href="/products">产品中心</a>
  <a href="/contact">联系我们</a>
</nav>
<button>立即购买</button>
<button>加入购物车</button>
```

**定位器写法：**
```python
# 定位导航链接
home_link = self.page.get_by_text("首页")
products_link = self.page.get_by_role("link", name="产品中心")

# 定位按钮
buy_button = self.page.get_by_text("立即购买")
cart_button = self.page.get_by_text("加入购物车")

# 部分文本匹配
contact_link = self.page.get_by_text("联系", exact=False)
```

#### 6. 通过CSS选择器定位

**语法格式：**
```python
# 基本选择器
self.page.locator("#id")              # ID选择器
self.page.locator(".class")           # 类选择器
self.page.locator("tag")              # 标签选择器
# 属性选择器
self.page.locator("[attribute='value']")
# 组合选择器
self.page.locator("parent > child")    # 直接子元素
self.page.locator("ancestor descendant") # 后代元素
# 伪类选择器
self.page.locator("input:nth-child(2)") # 第二个子元素
self.page.locator("button:first-of-type") # 同类型第一个
```

**适用场景：** 功能强大，适合复杂的定位需求，特别是需要精确控制定位范围时。

**优点：** 灵活性极高，支持复杂的组合条件
**缺点：** 语法相对复杂，需要CSS基础知识

**HTML示例：**
```html
<div class="form-container">
  <div class="form-group">
    <input type="text" class="form-control" required>
    <span class="error-message">错误信息</span>
  </div>
  <div class="form-group">
    <select class="form-control">
      <option value="1">选项1</option>
      <option value="2" selected>选项2</option>
    </select>
  </div>
</div>
```

**定位器写法：**
```python
# 基本选择器
form_container = self.page.locator(".form-container")
first_input = self.page.locator("input.form-control")

# 组合选择器
first_group_input = self.page.locator(".form-group:first-child input")
selected_option = self.page.locator("option[selected]")
error_message = self.page.locator(".form-group .error-message")

# 属性选择器
required_input = self.page.locator("input[required]")
text_inputs = self.page.locator("input[type='text']")
```

#### 7. 通过XPath定位

**语法格式：**
```python
# 绝对路径（不推荐）
self.page.locator("/html/body/div/form/input")
# 相对路径（推荐）
self.page.locator("//input[@id='username']")
# 文本定位
self.page.locator("//button[text()='提交']")
self.page.locator("//a[contains(text(),'更多')]")
# 轴定位
self.page.locator("//label[text()='用户名']/following-sibling::input")
# 索引定位
self.page.locator("(//input[@type='text'])[2]")
```

**适用场景：** 适合复杂的层级关系定位，特别是CSS选择器难以表达的场景。

**优点：** 功能最强大，支持复杂的逻辑判断和轴定位
**缺点：** 语法复杂，性能相对较差，可读性不如CSS选择器

**HTML示例：**
```html
<form class="login-form">
  <div class="field-group">
    <label>用户名：</label>
    <input type="text" name="username">
  </div>
  <div class="field-group">
    <label>密码：</label>
    <input type="password" name="password">
  </div>
  <button type="submit">登录</button>
  <a href="/register">还没有账号？立即注册</a>
</form>
```

**定位器写法：**
```python
# 属性定位
username_input = self.page.locator("//input[@name='username']")
password_input = self.page.locator("//input[@type='password']")

# 文本定位
login_button = self.page.locator("//button[text()='登录']")
register_link = self.page.locator("//a[contains(text(),'注册')]")

# 轴定位（通过标签找相邻输入框）
username_by_label = self.page.locator("//label[text()='用户名：']/following-sibling::input")

# 层级定位
form_inputs = self.page.locator("//form[@class='login-form']//input")
second_input = self.page.locator("(//div[@class='field-group']//input)[2]")
```

### 🚀 实战示例部分

#### 1. 简单登录页面完整定位示例

**HTML页面结构：**
```html
<!DOCTYPE html>
<html>
<head>
    <title>用户登录</title>
</head>
<body>
    <div class="login-container">
        <h2 id="login-title">用户登录</h2>
        <form id="login-form" class="login-form">
            <div class="form-group">
                <label for="username">用户名：</label>
                <input id="username" name="username" type="text" 
                       placeholder="请输入用户名" required>
                <span class="error-msg" id="username-error"></span>
            </div>
            
            <div class="form-group">
                <label for="password">密码：</label>
                <input id="password" name="password" type="password" 
                       placeholder="请输入密码" required>
                <span class="error-msg" id="password-error"></span>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" name="remember" value="1">
                    记住我
                </label>
            </div>
            
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">登录</button>
                <button type="button" class="btn btn-secondary">重置</button>
            </div>
        </form>
        
        <div class="links">
            <a href="/register">还没有账号？立即注册</a>
            <a href="/forgot-password">忘记密码？</a>
        </div>
    </div>
</body>
</html>
```

**完整页面对象类实现：**
```python
from pages.base_page import BasePage
from playwright.sync_api import Page

class LoginPage(BasePage):
    """登录页面对象类 - 展示多种定位方法"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 方法1：通过ID定位（推荐 - 最稳定）
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_title = page.locator("#login-title")
        
        # 方法2：通过CSS类名定位
        self.login_container = page.locator(".login-container")
        self.form_groups = page.locator(".form-group")
        self.error_messages = page.locator(".error-msg")
        
        # 方法3：通过name属性定位
        self.username_by_name = page.locator("[name='username']")
        self.password_by_name = page.locator("[name='password']")
        self.remember_checkbox = page.locator("[name='remember']")
        
        # 方法4：通过标签文本定位（Playwright推荐）
        self.username_by_label = page.get_by_label("用户名")
        self.password_by_label = page.get_by_label("密码")
        
        # 方法5：通过占位符定位
        self.username_by_placeholder = page.get_by_placeholder("请输入用户名")
        self.password_by_placeholder = page.get_by_placeholder("请输入密码")
        
        # 方法6：通过角色定位（最语义化）
        self.login_button = page.get_by_role("button", name="登录")
        self.reset_button = page.get_by_role("button", name="重置")
        self.register_link = page.get_by_role("link", name="还没有账号？立即注册")
        
        # 方法7：通过CSS选择器组合定位
        self.primary_button = page.locator(".btn.btn-primary")
        self.secondary_button = page.locator(".btn.btn-secondary")
        self.first_form_group = page.locator(".form-group:first-child")
        
        # 方法8：通过XPath定位（复杂场景）
        self.username_error = page.locator("//span[@id='username-error']")
        self.password_error = page.locator("//span[@id='password-error']")
        self.remember_label = page.locator("//label[contains(text(),'记住我')]")
        
    def navigate_to_login(self):
        """导航到登录页面"""
        self.page.goto("/login")
        # 验证页面加载完成
        self.login_title.wait_for(state="visible")
        
    def login_with_credentials(self, username: str, password: str, remember: bool = False):
        """使用凭据登录 - 展示不同定位方法的使用"""
        # 使用ID定位填写用户名（最推荐）
        self.username_input.fill(username)
        
        # 使用标签定位填写密码（语义化推荐）
        self.password_by_label.fill(password)
        
        # 处理记住我复选框
        if remember:
            self.remember_checkbox.check()
        
        # 使用角色定位点击登录按钮（最语义化）
        self.login_button.click()
        
    def verify_error_message(self, field: str, expected_message: str):
        """验证错误信息 - 展示XPath定位的使用"""
        if field == "username":
            error_locator = self.username_error
        elif field == "password":
            error_locator = self.password_error
        else:
            raise ValueError(f"不支持的字段: {field}")
            
        # 等待错误信息出现并验证
        error_locator.wait_for(state="visible")
        actual_message = error_locator.text_content()
        assert expected_message in actual_message, f"期望: {expected_message}, 实际: {actual_message}"
        
    def clear_form(self):
        """清空表单 - 展示CSS选择器的批量操作"""
        # 方法1：逐个清空
        self.username_input.clear()
        self.password_input.clear()
        
        # 方法2：批量清空所有输入框
        all_inputs = self.page.locator("input[type='text'], input[type='password']")
        for i in range(all_inputs.count()):
            all_inputs.nth(i).clear()
```

**对应的测试用例：**
```python
import pytest
from tests.base_test import BaseTest
from pages.login_page import LoginPage

class TestLoginPageLocators(BaseTest):
    """登录页面定位器测试 - 展示实际使用"""
    
    def setup_method(self):
        """测试前置设置"""
        super().setup_method()
        self.login_page = LoginPage(self.page)
        self.login_page.navigate_to_login()
        
    def test_all_locators_are_accessible(self):
        """测试所有定位器都能正常访问元素"""
        # 验证页面标题
        assert self.login_page.login_title.is_visible()
        assert "用户登录" in self.login_page.login_title.text_content()
        
        # 验证输入框可见性（多种定位方法）
        assert self.login_page.username_input.is_visible()  # ID定位
        assert self.login_page.username_by_label.is_visible()  # 标签定位
        assert self.login_page.username_by_placeholder.is_visible()  # 占位符定位
        
        # 验证按钮可见性
        assert self.login_page.login_button.is_visible()  # 角色定位
        assert self.login_page.reset_button.is_visible()
        
    def test_successful_login_flow(self):
        """测试成功登录流程"""
        # 使用页面对象方法登录
        self.login_page.login_with_credentials(
            username="testuser",
            password="testpass123",
            remember=True
        )
        
        # 验证登录成功（假设跳转到首页）
        self.page.wait_for_url("**/dashboard")
        
    def test_form_validation_errors(self):
        """测试表单验证错误"""
        # 不填写任何信息直接提交
        self.login_page.login_button.click()
        
        # 验证错误信息显示
        self.login_page.verify_error_message("username", "用户名不能为空")
        self.login_page.verify_error_message("password", "密码不能为空")
```

#### 2. 动态元素定位处理方案

**场景1：等待元素出现**
```python
class DynamicContentPage(BasePage):
    """动态内容页面处理"""
    
    def wait_for_search_results(self, timeout: int = 10000):
        """等待搜索结果加载"""
        # 方法1：等待特定元素出现
        results_container = self.page.locator(".search-results")
        results_container.wait_for(state="visible", timeout=timeout)
        
        # 方法2：等待加载指示器消失
        loading_spinner = self.page.locator(".loading-spinner")
        loading_spinner.wait_for(state="hidden", timeout=timeout)
        
        # 方法3：等待网络请求完成
        self.page.wait_for_load_state("networkidle")
        
    def handle_dynamic_table(self):
        """处理动态表格数据"""
        # 等待表格加载
        table = self.page.locator("table.data-table")
        table.wait_for(state="visible")
        
        # 等待至少有一行数据
        first_row = self.page.locator("table.data-table tbody tr:first-child")
        first_row.wait_for(state="visible")
        
        # 获取动态生成的行数
        rows = self.page.locator("table.data-table tbody tr")
        row_count = rows.count()
        print(f"表格共有 {row_count} 行数据")
        
    def interact_with_ajax_content(self):
        """与AJAX加载的内容交互"""
        # 触发AJAX请求
        load_more_btn = self.page.locator("#load-more")
        load_more_btn.click()
        
        # 等待新内容加载（通过元素数量变化判断）
        items_before = self.page.locator(".item").count()
        
        # 等待新元素出现
        self.page.wait_for_function(
            f"document.querySelectorAll('.item').length > {items_before}",
            timeout=10000
        )
        
        items_after = self.page.locator(".item").count()
        print(f"加载前: {items_before} 项，加载后: {items_after} 项")
```

**场景2：处理动态ID和类名**
```python
class DynamicAttributePage(BasePage):
    """动态属性页面处理"""
    
    def locate_dynamic_id_element(self, base_id: str):
        """定位动态ID元素"""
        # 方法1：使用部分匹配
        dynamic_element = self.page.locator(f"[id*='{base_id}']")
        
        # 方法2：使用正则表达式
        regex_locator = self.page.locator(f"[id~='{base_id}-\\d+']")
        
        # 方法3：使用XPath contains函数
        xpath_locator = self.page.locator(f"//div[contains(@id, '{base_id}')]")
        
        return dynamic_element
        
    def handle_timestamp_elements(self):
        """处理包含时间戳的元素"""
        # 定位包含时间戳的元素（如：item-1703123456789）
        timestamp_items = self.page.locator("[id^='item-'][id*='-']")
        
        # 获取所有匹配的元素
        count = timestamp_items.count()
        for i in range(count):
            item = timestamp_items.nth(i)
            item_id = item.get_attribute("id")
            print(f"找到动态元素: {item_id}")
```

#### 3. 定位失败时的调试技巧

**调试技巧1：元素可见性检查**
```python
class DebuggingHelper:
    """定位调试辅助类"""
    
    @staticmethod
    def debug_element_state(page: Page, locator_string: str):
        """调试元素状态"""
        locator = page.locator(locator_string)
        
        print(f"\n=== 调试定位器: {locator_string} ===")
        
        # 检查元素是否存在
        count = locator.count()
        print(f"匹配到的元素数量: {count}")
        
        if count == 0:
            print("❌ 元素不存在，请检查定位器语法")
            return False
            
        if count > 1:
            print(f"⚠️  匹配到多个元素({count}个)，建议使用更精确的定位器")
            
        # 检查第一个元素的状态
        first_element = locator.first
        
        try:
            is_visible = first_element.is_visible()
            is_enabled = first_element.is_enabled()
            is_editable = first_element.is_editable()
            
            print(f"可见性: {'✅' if is_visible else '❌'} {is_visible}")
            print(f"可用性: {'✅' if is_enabled else '❌'} {is_enabled}")
            print(f"可编辑: {'✅' if is_editable else '❌'} {is_editable}")
            
            # 获取元素属性
            tag_name = first_element.evaluate("el => el.tagName")
            class_name = first_element.get_attribute("class")
            id_attr = first_element.get_attribute("id")
            
            print(f"标签名: {tag_name}")
            print(f"类名: {class_name}")
            print(f"ID: {id_attr}")
            
            return True
            
        except Exception as e:
            print(f"❌ 检查元素状态时出错: {e}")
            return False
    
    @staticmethod
    def suggest_alternative_locators(page: Page, text_content: str = None, tag_name: str = None):
        """建议替代定位器"""
        print("\n=== 建议的替代定位器 ===")
        
        if text_content:
            print(f"基于文本内容的定位器:")
            print(f"  page.get_by_text('{text_content}')")
            print(f"  page.locator('text={text_content}')")
            print(f"  page.locator('//*[contains(text(), \"{text_content}\")]')")
            
        if tag_name:
            print(f"基于标签的定位器:")
            print(f"  page.locator('{tag_name}')")
            print(f"  page.locator('//{tag_name}')")
            
    @staticmethod
    def wait_and_retry_locator(page: Page, locator_string: str, max_attempts: int = 3):
        """等待并重试定位"""
        for attempt in range(max_attempts):
            try:
                print(f"\n尝试第 {attempt + 1} 次定位: {locator_string}")
                
                locator = page.locator(locator_string)
                
                # 等待元素出现
                locator.wait_for(state="visible", timeout=5000)
                
                print("✅ 定位成功！")
                return locator
                
            except Exception as e:
                print(f"❌ 第 {attempt + 1} 次尝试失败: {e}")
                
                if attempt < max_attempts - 1:
                    print("等待2秒后重试...")
                    page.wait_for_timeout(2000)
                    
        print(f"❌ 所有尝试都失败了，请检查定位器或页面状态")
        return None
```

**使用调试辅助类：**
```python
class TestWithDebugging(BaseTest):
    """带调试功能的测试"""
    
    def test_with_debugging(self):
        """使用调试功能的测试"""
        # 调试元素状态
        DebuggingHelper.debug_element_state(self.page, "#username")
        
        # 等待并重试定位
        username_input = DebuggingHelper.wait_and_retry_locator(
            self.page, "#username"
        )
        
        if username_input:
            username_input.fill("testuser")
        
        # 建议替代定位器
        DebuggingHelper.suggest_alternative_locators(
            self.page, 
            text_content="登录", 
            tag_name="button"
        )
```

#### 4. 最佳实践建议

**实践1：定位器优先级策略**
```python
class LocatorBestPractices:
    """定位器最佳实践"""
    
    # 推荐优先级（从高到低）
    LOCATOR_PRIORITY = [
        "get_by_role()",      # 1. 语义化角色定位（最推荐）
        "get_by_label()",     # 2. 标签文本定位
        "get_by_placeholder()", # 3. 占位符定位
        "get_by_text()",      # 4. 文本内容定位
        "#id",                # 5. ID定位
        "[data-testid]",      # 6. 测试ID定位
        ".class",             # 7. CSS类定位
        "[name]",             # 8. name属性定位
        "tag[attribute]",     # 9. 属性定位
        "//xpath",            # 10. XPath定位（最后选择）
    ]
    
    @staticmethod
    def create_robust_locator(page: Page, element_info: dict):
        """创建健壮的定位器"""
        # 优先使用语义化定位
        if element_info.get('role') and element_info.get('name'):
            return page.get_by_role(element_info['role'], name=element_info['name'])
            
        # 其次使用标签定位
        if element_info.get('label'):
            return page.get_by_label(element_info['label'])
            
        # 再次使用占位符定位
        if element_info.get('placeholder'):
            return page.get_by_placeholder(element_info['placeholder'])
            
        # 最后使用ID或CSS定位
        if element_info.get('id'):
            return page.locator(f"#{element_info['id']}")
            
        if element_info.get('css'):
            return page.locator(element_info['css'])
            
        raise ValueError("无法创建有效的定位器")
```

### 📋 附加说明

#### 1. 定位器编写规范

**命名规范：**
```python
# ✅ 好的命名
username_input = page.locator("#username")
login_button = page.get_by_role("button", name="登录")
user_profile_link = page.get_by_role("link", name="个人资料")

# ❌ 不好的命名
input1 = page.locator("#username")
btn = page.get_by_role("button", name="登录")
link = page.get_by_role("link", name="个人资料")
```

**组织结构：**
```python
class LoginPage(BasePage):
    """登录页面 - 良好的定位器组织"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 按功能区域分组
        # === 表单元素 ===
        self.username_input = page.get_by_label("用户名")
        self.password_input = page.get_by_label("密码")
        self.remember_checkbox = page.get_by_label("记住我")
        
        # === 操作按钮 ===
        self.login_button = page.get_by_role("button", name="登录")
        self.reset_button = page.get_by_role("button", name="重置")
        
        # === 导航链接 ===
        self.register_link = page.get_by_role("link", name="注册")
        self.forgot_password_link = page.get_by_role("link", name="忘记密码")
        
        # === 状态元素 ===
        self.error_message = page.locator(".error-message")
        self.success_message = page.locator(".success-message")
```

#### 2. 定位稳定性建议

**稳定性原则：**
```python
# ✅ 稳定的定位器（推荐）
# 1. 基于用户可见的文本
login_btn = page.get_by_role("button", name="登录")

# 2. 基于语义化的HTML结构
username_field = page.get_by_label("用户名")

# 3. 基于稳定的ID（如果确保不变）
user_menu = page.locator("#user-menu")

# 4. 基于测试专用属性
submit_btn = page.locator("[data-testid='submit-button']")

# ❌ 不稳定的定位器（避免）
# 1. 基于复杂的CSS路径
bad_locator1 = page.locator("div > div:nth-child(3) > form > button:first-child")

# 2. 基于动态生成的类名
bad_locator2 = page.locator(".css-1a2b3c4d5e")

# 3. 基于绝对XPath路径
bad_locator3 = page.locator("/html/body/div[1]/div[2]/form/button[1]")
```

#### 3. 常见错误及解决方法

**错误1：元素未找到**
```python
# 问题：元素可能还未加载
# ❌ 错误做法
username_input = page.locator("#username")
username_input.fill("testuser")  # 可能失败

# ✅ 正确做法
username_input = page.locator("#username")
username_input.wait_for(state="visible")  # 等待元素可见
username_input.fill("testuser")
```

**错误2：定位到多个元素**
```python
# 问题：定位器匹配了多个元素
# ❌ 错误做法
buttons = page.locator("button")  # 可能匹配多个按钮
buttons.click()  # 不确定点击哪个

# ✅ 正确做法
# 方法1：使用更精确的定位器
login_button = page.get_by_role("button", name="登录")
login_button.click()

# 方法2：使用索引选择特定元素
first_button = page.locator("button").first
first_button.click()

# 方法3：使用nth()方法
second_button = page.locator("button").nth(1)
second_button.click()
```

**错误3：元素不可交互**
```python
# 问题：元素存在但不可点击
# ❌ 错误做法
button = page.locator("#submit-btn")
button.click()  # 可能元素被遮挡或禁用

# ✅ 正确做法
button = page.locator("#submit-btn")
# 等待元素可点击
button.wait_for(state="visible")
button.wait_for(state="enabled")
# 确保元素在视口内
button.scroll_into_view_if_needed()
button.click()
```

#### 4. 性能优化提示

**优化技巧：**
```python
class PerformanceOptimizedPage(BasePage):
    """性能优化的页面对象"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # ✅ 好的做法：缓存定位器
        self._username_input = None
        self._login_button = None
    
    @property
    def username_input(self):
        """延迟初始化定位器"""
        if self._username_input is None:
            self._username_input = self.page.get_by_label("用户名")
        return self._username_input
    
    @property
    def login_button(self):
        """延迟初始化定位器"""
        if self._login_button is None:
            self._login_button = self.page.get_by_role("button", name="登录")
        return self._login_button
    
    def batch_fill_form(self, form_data: dict):
        """批量填写表单（减少定位次数）"""
        # ✅ 一次性获取所有需要的元素
        form_fields = {
            'username': self.page.get_by_label("用户名"),
            'password': self.page.get_by_label("密码"),
            'email': self.page.get_by_label("邮箱"),
        }
        
        # 批量填写
        for field_name, locator in form_fields.items():
            if field_name in form_data:
                locator.fill(form_data[field_name])
    
    def wait_for_page_ready(self):
        """等待页面完全加载"""
        # 等待关键元素出现
        self.username_input.wait_for(state="visible")
        
        # 等待网络请求完成
        self.page.wait_for_load_state("networkidle")
        
        # 等待动画完成（如果有）
        self.page.wait_for_timeout(500)
```

**总结：**
- 🎯 **优先使用语义化定位器**：`get_by_role()`, `get_by_label()` 等
- 🔍 **避免脆弱的定位器**：复杂的CSS路径、绝对XPath等
- ⏱️ **合理使用等待机制**：确保元素可见、可用后再操作
- 🐛 **善用调试工具**：定位失败时系统性排查问题
- 📈 **注意性能优化**：缓存定位器、减少重复查找
- 📝 **保持代码整洁**：良好的命名和组织结构

通过掌握这些定位技术和最佳实践，你将能够编写出稳定、高效、易维护的自动化测试代码！

### 高级定位技巧

#### 1. 动态元素定位

```python
class DynamicElementPage(BasePage):
    def wait_for_dynamic_element(self, element_id: str):
        """等待动态元素出现"""
        locator = self.page.locator(f"#{element_id}")
        locator.wait_for(state="visible", timeout=10000)
        return locator
    
    def handle_loading_state(self):
        """处理加载状态"""
        # 等待加载完成
        self.page.wait_for_load_state("networkidle")
        
        # 等待特定元素消失
        loading_spinner = self.page.locator(".loading-spinner")
        loading_spinner.wait_for(state="hidden")
```

#### 2. iframe处理

```python
class IframePage(BasePage):
    def interact_with_iframe(self):
        """与iframe中的元素交互"""
        # 获取iframe
        iframe = self.page.frame_locator("iframe[name='content']")
        
        # 在iframe中定位元素
        iframe_input = iframe.locator("#iframe-input")
        iframe_input.fill("iframe中的文本")
        
        # 点击iframe中的按钮
        iframe_button = iframe.locator("button[type='submit']")
        iframe_button.click()
```

#### 3. 复杂表单处理

```python
class ComplexFormPage(BasePage):
    def fill_complex_form(self, form_data: dict):
        """填写复杂表单"""
        # 下拉选择
        self.page.select_option("select[name='country']", form_data['country'])
        
        # 单选按钮
        self.page.check(f"input[value='{form_data['gender']}']")
        
        # 复选框
        for hobby in form_data['hobbies']:
            self.page.check(f"input[value='{hobby}']")
        
        # 文件上传
        self.page.set_input_files("input[type='file']", form_data['file_path'])
```

### 定位最佳实践

#### 1. 定位器优先级

```python
# 推荐优先级（从高到低）
1. get_by_role()      # 语义化，最稳定
2. get_by_text()      # 用户可见文本
3. get_by_label()     # 表单标签
4. get_by_test_id()   # 测试专用ID
5. CSS选择器          # 简洁明了
6. XPath             # 复杂场景
```

#### 2. 稳定性定位策略

```python
class StableLocatorPage(BasePage):
    # ❌ 不推荐：依赖位置
    first_button = "button:nth-child(1)"
    
    # ❌ 不推荐：依赖样式类
    submit_btn = ".btn-primary"
    
    # ✅ 推荐：语义化定位
    submit_button = "button[type='submit']"
    
    # ✅ 推荐：测试ID
    login_form = "[data-testid='login-form']"
    
    # ✅ 推荐：角色定位
    def get_submit_button(self):
        return self.page.get_by_role("button", name="提交")
```

## 💻 代码示例

### 项目结构概览

```
PlaywrightProject/
├── pages/                    # 页面对象模型
│   ├── base_page.py         # 页面基类
│   └── simple_practice_page.py  # 具体页面类
├── tests/                   # 测试用例
│   ├── base_test.py        # 测试基类
│   └── test_simple_practice_pom.py  # POM模式测试
├── utils/                   # 工具类
│   └── screenshot_helper.py # 截图助手
└── practice_page.html      # 测试页面
```

### POM模式完整实现示例

本章节展示基于POM (Page Object Model) 模式的完整代码实现，包括传统方式与POM方式的对比。通过实际代码演示POM模式的优势和最佳实践。

#### 1. 传统方式 vs POM方式对比

**传统方式问题：**
```python
def test_basic_form_input(self, page: Page):
    """测试基本表单输入 - 传统方式"""
    page.goto("http://localhost:8000/practice_page.html")
    
    # ❌ 问题1: 选择器分散在测试用例中，难以维护
    page.fill("[data-testid='username-input']", "testuser")
    page.fill("[data-testid='password-input']", "password123")
    page.fill("[data-testid='email-input']", "test@example.com")
    
    # ❌ 问题2: 重复的验证代码，缺乏复用性
    expect(page.locator("[data-testid='username-input']")).to_have_value("testuser")
    expect(page.locator("[data-testid='email-input']")).to_have_value("test@example.com")
    
    # ❌ 问题3: 技术细节与业务逻辑混合，可读性差
```

**POM方式解决：**
```python
def test_basic_form_input(self):
    """测试基本表单输入 - POM版本"""
    with allure.step("导航到页面"):
        self.practice_page.goto_practice_page()
    
    with allure.step("填写并验证表单输入"):
        (self.practice_page  # ✅ 优势1: 链式调用，代码简洁
         .fill_basic_form_inputs("testuser", "password123", "test@example.com")
         .verify_form_input_values("testuser", "test@example.com"))  # ✅ 优势2: 业务语义清晰
    
    # ✅ 优势3: 选择器集中管理，易于维护
    # ✅ 优势4: Allure步骤自动生成详细报告
```

#### 2. POM模式核心组件

**页面基类 (BasePage)：**
```python
from abc import ABC
from playwright.sync_api import Page, Locator
from utils.screenshot_helper import ScreenshotHelper
import allure

class BasePage(ABC):
    """页面对象模型基类"""
    
    def __init__(self, page: Page):
        self.page = page
        self.screenshot_helper = ScreenshotHelper(page)
        self.timeout = 10000
    
    def click(self, selector: str, timeout: int = None) -> 'BasePage':
        """点击元素"""
        timeout = timeout or self.timeout
        self.page.locator(selector).click(timeout=timeout)
        return self
    
    def fill(self, selector: str, value: str, timeout: int = None) -> 'BasePage':
        """填写输入框"""
        timeout = timeout or self.timeout
        self.page.locator(selector).fill(value, timeout=timeout)
        return self
    
    def get_element(self, selector: str, timeout: int = None) -> Locator:
        """获取页面元素"""
        timeout = timeout or self.timeout
        return self.page.locator(selector).first
    
    def wait_for_element(self, selector: str, state: str = "visible", timeout: int = None) -> 'BasePage':
        """等待元素状态"""
        timeout = timeout or self.timeout
        self.page.locator(selector).wait_for(state=state, timeout=timeout)
        return self
```

**具体页面类 (SimplePracticePage)：**
```python
from pages.base_page import BasePage
from playwright.sync_api import Page, expect
import allure

class SimplePracticePage(BasePage):
    """简化练习页面类 - POM模式实现"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 元素定位器集中管理
        self.username_input = "[data-testid='username-input']"
        self.password_input = "[data-testid='password-input']"
        self.email_input = "[data-testid='email-input']"
        self.country_select = "[data-testid='country-select']"
        self.hobby_reading = "[data-testid='hobby-reading']"
        self.hobby_music = "[data-testid='hobby-music']"
        self.hobby_sports = "[data-testid='hobby-sports']"
        self.submit_btn = "[data-testid='submit-btn']"
        self.form_alert = "#form-alert"
    
    @allure.step("导航到练习页面")
    def goto_practice_page(self):
        """导航到练习页面"""
        self.page.goto("http://localhost:8000/practice_page.html")
        return self
    
    @allure.step("填写基本表单")
    def fill_basic_form_inputs(self, username: str, password: str, email: str):
        """填写基本表单输入"""
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.fill(self.email_input, email)
        return self  # 支持链式调用
    
    @allure.step("验证表单输入值")
    def verify_form_input_values(self, username: str, email: str):
        """验证表单输入值"""
        expect(self.page.locator(self.username_input)).to_have_value(username)
        expect(self.page.locator(self.email_input)).to_have_value(email)
        return self
    
    @allure.step("选择国家: {country}")
    def select_country_option(self, country: str):
        """选择国家"""
        self.page.select_option(self.country_select, country)
        return self
    
    @allure.step("验证国家选择")
    def verify_country_selection(self, expected_country: str):
        """验证国家选择"""
        expect(self.page.locator(self.country_select)).to_have_value(expected_country)
        return self
    
    @allure.step("选择兴趣爱好")
    def select_hobbies(self, *hobbies):
        """选择兴趣爱好复选框"""
        hobby_mapping = {
            "reading": self.hobby_reading,
            "music": self.hobby_music,
            "sports": self.hobby_sports
        }
        
        for hobby in hobbies:
            if hobby in hobby_mapping:
                self.page.check(hobby_mapping[hobby])
        return self
    
    @allure.step("填写完整表单")
    def fill_complete_form(self, username: str = "testuser", password: str = "password123", 
                          email: str = "test@example.com", country: str = "china"):
        """填写完整表单 - 业务流程封装"""
        return (self
                .fill_basic_form_inputs(username, password, email)
                .select_country_option(country)
                .select_hobbies("reading", "music"))
    
    @allure.step("提交表单")
    def submit_form(self):
        """提交表单"""
        self.click(self.submit_btn)
        return self
    
    @allure.step("验证表单提交成功")
    def verify_form_submission_success(self):
        """验证表单提交成功"""
        expect(self.page.locator(self.form_alert)).to_contain_text("表单提交成功！")
        return self
```

#### 3. POM模式优势对比

| 方面 | 传统方式 | POM方式 |
|------|----------|----------|
| **元素定位** | 测试用例中直接写选择器 | 页面类中统一管理选择器 |
| **页面操作** | 直接调用 page 对象方法 | 封装为页面对象的业务方法 |
| **代码复用** | 重复代码较多 | 高度复用，链式调用 |
| **维护性** | 选择器变更需修改多处 | 只需修改页面类中的定义 |
| **可读性** | 技术细节和业务逻辑混合 | 业务逻辑清晰，技术细节隐藏 |
| **测试报告** | 基本的测试步骤 | 详细的 Allure 步骤和分组 |

### 测试用例类实现

#### 1. 测试基类 (BaseTest)

```python
from abc import ABC
import pytest
from playwright.sync_api import Page, BrowserContext
from utils.screenshot_helper import ScreenshotHelper
import allure

class BaseTest(ABC):
    """测试基类 - POM模式"""
    
    @pytest.fixture(autouse=True)
    def setup_test_context(self, page: Page, context: BrowserContext):
        """统一的测试环境设置"""
        self.page = page
        self.context = context
        self.screenshot_helper = ScreenshotHelper(page)
        
        # 子类可以重写此方法来设置页面对象
        self.setup_page_objects()
        
        yield
        
        # 测试后清理
        self.teardown_test_context()
    
    def setup_page_objects(self):
        """设置页面对象 - 子类重写"""
        pass
    
    def teardown_test_context(self):
        """测试后清理"""
        pass
    
    def take_screenshot(self, name: str = None):
        """截图辅助方法"""
        return self.screenshot_helper.take_screenshot(name)
    
    def assert_element_visible(self, selector: str):
        """断言元素可见"""
        element = self.page.locator(selector)
        assert element.is_visible(), f"元素 {selector} 不可见"
```

#### 2. 完整测试用例 (TestSimplePracticePOM)

```python
import pytest
import allure
from tests.base_test import BaseTest
from pages.simple_practice_page import SimplePracticePage
from playwright.sync_api import expect

@allure.feature("简化练习页面")
@allure.story("POM模式测试")
class TestSimplePracticePOM(BaseTest):
    """基于POM模式的简化练习页面测试"""
    
    def setup_page_objects(self):
        """设置页面对象"""
        self.practice_page = SimplePracticePage(self.page)
    
    @allure.title("测试页面加载")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_page_loads(self):
        """测试页面是否正常加载"""
        with allure.step("导航到页面并验证加载"):
            self.practice_page.goto_practice_page()
            # 验证关键元素存在
            self.assert_element_visible(self.practice_page.username_input)
    
    @allure.title("测试基本表单输入")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_basic_form_input(self):
        """测试基本表单输入 - POM版本"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("填写并验证表单输入"):
            (self.practice_page
             .fill_basic_form_inputs("testuser", "password123", "test@example.com")
             .verify_form_input_values("testuser", "test@example.com"))
    
    @allure.title("测试国家选择功能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_country_selection(self):
        """测试国家选择功能"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("选择并验证国家"):
            (self.practice_page
             .select_country_option("china")
             .verify_country_selection("china"))
    
    @allure.title("测试复选框选择")
    @allure.severity(allure.severity_level.NORMAL)
    def test_checkbox_selection(self):
        """测试复选框选择功能"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("选择兴趣爱好"):
            self.practice_page.select_hobbies("reading", "music")
        
        with allure.step("验证选择结果"):
            expect(self.page.locator(self.practice_page.hobby_reading)).to_be_checked()
            expect(self.page.locator(self.practice_page.hobby_music)).to_be_checked()
    
    @allure.title("测试完整业务流程")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_complete_workflow(self):
        """测试完整的业务流程 - 展示POM链式调用优势"""
        with allure.step("执行完整业务流程"):
            (self.practice_page
             .goto_practice_page()
             .fill_complete_form()
             .submit_form()
             .verify_form_submission_success())
    
    @allure.title("测试业务流程分步验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_step_by_step_workflow(self):
        """测试分步业务流程 - 展示详细步骤"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("填写基本信息"):
            self.practice_page.fill_basic_form_inputs("张三", "123456", "zhangsan@test.com")
        
        with allure.step("选择国家和爱好"):
            (self.practice_page
             .select_country_option("china")
             .select_hobbies("reading", "sports"))
        
        with allure.step("验证表单数据"):
            (self.practice_page
             .verify_form_input_values("张三", "zhangsan@test.com")
             .verify_country_selection("china"))
        
        with allure.step("提交表单并验证"):
            (self.practice_page
             .submit_form()
             .verify_form_submission_success())
    
    @allure.title("参数化测试 - 多组数据验证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("username,email,country", [
        ("user1", "user1@test.com", "china"),
        ("user2", "user2@test.com", "usa"),
        ("user3", "user3@test.com", "japan"),
    ])
    def test_form_with_multiple_data(self, username: str, email: str, country: str):
        """测试表单填写 - 参数化测试"""
        with allure.step(f"使用数据: {username}, {email}, {country}"):
            (self.practice_page
             .goto_practice_page()
             .fill_basic_form_inputs(username, "password123", email)
             .select_country_option(country)
             .verify_form_input_values(username, email)
             .verify_country_selection(country))
```

#### 3. POM模式实现步骤指南

**步骤1: 分析现有测试用例**
```python
# 🔍 分析要点:
# 1. 识别测试中使用的页面元素 (输入框、按钮、下拉框等)
# 2. 分析重复的操作模式 (填写表单、提交、验证等)
# 3. 确定需要封装的业务流程 (登录、注册、购买等)
# 4. 找出可以复用的验证逻辑

# 示例分析结果:
# - 页面元素: username_input, password_input, submit_btn
# - 重复操作: 填写用户名密码、点击提交、验证结果
# - 业务流程: 用户登录流程
```

**步骤2: 创建页面对象类**
```python
# 📝 页面类创建模板:
from pages.base_page import BasePage
from playwright.sync_api import Page, expect
import allure

class LoginPage(BasePage):  # 1. 继承 BasePage 基类
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 2. 定义页面元素选择器 (集中管理)
        self.username_input = "[data-testid='username-input']"
        self.password_input = "[data-testid='password-input']"
        self.login_btn = "[data-testid='login-btn']"
        self.error_message = ".error-message"
    
    # 3. 实现页面操作方法 (业务语义)
    @allure.step("填写登录信息")
    def fill_login_form(self, username: str, password: str):
        """填写登录表单"""
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        return self  # 支持链式调用
    
    @allure.step("点击登录按钮")
    def click_login(self):
        """点击登录按钮"""
        self.click(self.login_btn)
        return self
    
    # 4. 添加验证方法 (分离验证逻辑)
    @allure.step("验证登录成功")
    def verify_login_success(self):
        """验证登录成功"""
        # 验证跳转到首页或显示欢迎信息
        expect(self.page).to_have_url("/dashboard")
        return self
    
    @allure.step("验证登录失败")
    def verify_login_error(self, expected_message: str):
        """验证登录失败信息"""
        expect(self.page.locator(self.error_message)).to_contain_text(expected_message)
        return self
```

**步骤3: 重构测试用例**
```python
# 🧪 测试类重构模板:
import pytest
import allure
from tests.base_test import BaseTest
from pages.login_page import LoginPage

@allure.feature("用户登录")  # 4. 添加 Allure 特性标记
@allure.story("登录功能测试")
class TestLogin(BaseTest):  # 1. 继承 BaseTest 基类
    
    def setup_page_objects(self):  # 2. 初始化页面对象
        """设置页面对象"""
        self.login_page = LoginPage(self.page)
    
    @allure.title("测试成功登录")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_successful_login(self):
        """测试用户成功登录"""
        # 3. 使用页面对象方法 (替换直接页面操作)
        with allure.step("执行登录流程"):
            (self.login_page
             .goto_login_page()  # 导航到登录页
             .fill_login_form("testuser", "password123")  # 填写表单
             .click_login()  # 点击登录
             .verify_login_success())  # 验证成功
    
    @allure.title("测试登录失败")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("username,password,error_msg", [
        ("", "password", "用户名不能为空"),
        ("user", "", "密码不能为空"),
        ("wrong", "wrong", "用户名或密码错误"),
    ])
    def test_login_failure(self, username: str, password: str, error_msg: str):
        """测试登录失败场景 (参数化测试)"""
        with allure.step(f"测试无效登录: {username}/{password}"):
            (self.login_page
             .goto_login_page()
             .fill_login_form(username, password)
             .click_login()
             .verify_login_error(error_msg))
```

**步骤4: 优化和扩展**
```python
# 🚀 高级优化技巧:

# 1. 实现链式调用 - 所有方法返回 self
class LoginPage(BasePage):
    def fill_and_submit_login(self, username: str, password: str):
        """复合业务流程 - 填写并提交登录"""
        return (self
                .fill_login_form(username, password)
                .click_login())

# 2. 添加参数化测试 - 数据驱动
@pytest.mark.parametrize("test_data", [
    {"user": "admin", "pwd": "admin123", "expect": "success"},
    {"user": "guest", "pwd": "guest123", "expect": "success"},
])
def test_multiple_users_login(self, test_data):
    """多用户登录测试"""
    result = (self.login_page
              .goto_login_page()
              .fill_and_submit_login(test_data["user"], test_data["pwd"]))
    
    if test_data["expect"] == "success":
        result.verify_login_success()
    else:
        result.verify_login_error("登录失败")

# 3. 增强错误处理和重试机制
class LoginPage(BasePage):
    @allure.step("安全登录 (带重试)")
    def safe_login(self, username: str, password: str, max_retries: int = 3):
        """带重试机制的安全登录"""
        for attempt in range(max_retries):
            try:
                self.fill_login_form(username, password)
                self.click_login()
                self.verify_login_success()
                return self
            except Exception as e:
                if attempt == max_retries - 1:
                    self.take_screenshot(f"login_failed_attempt_{attempt + 1}")
                    raise e
                allure.attach(f"登录尝试 {attempt + 1} 失败，重试中...", 
                            name="重试信息", attachment_type=allure.attachment_type.TEXT)
        return self

# 4. 添加日志记录和监控
import logging

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @allure.step("监控登录性能")
    def monitored_login(self, username: str, password: str):
        """带性能监控的登录"""
        import time
        start_time = time.time()
        
        try:
            result = self.fill_and_submit_login(username, password)
            login_time = time.time() - start_time
            
            self.logger.info(f"登录耗时: {login_time:.2f}秒")
            allure.attach(f"登录耗时: {login_time:.2f}秒", 
                        name="性能指标", attachment_type=allure.attachment_type.TEXT)
            
            return result
        except Exception as e:
            self.logger.error(f"登录失败: {str(e)}")
            raise
```

#### 4. POM模式最佳实践

**命名规范：**
- 页面类：`XxxPage`
- 测试类：`TestXxxPOM`
- 方法名：使用业务术语而非技术术语

**方法设计：**
- 单一职责：每个方法只做一件事
- 返回 self：支持链式调用
- 参数化：提供灵活的参数选项

**元素定位：**
- 优先使用 `data-testid`
- 提供备用选择器
- 集中管理选择器

**验证方法：**
- 分离操作和验证
- 提供专门的验证方法
- 使用有意义的断言消息

## 🏃‍♂️ 测试运行

### 智能测试运行器

本项目提供了智能测试运行器 `run_tests.py`，支持多种运行方式：

```bash
# 运行所有测试
python run_tests.py

# 运行特定测试文件
python run_tests.py tests/test_simple_practice_pom.py

# 运行特定测试类
python run_tests.py tests/test_simple_practice_pom.py::TestSimplePracticePOM

# 运行特定测试方法
python run_tests.py tests/test_simple_practice_pom.py::TestSimplePracticePOM::test_page_loads

# 详细输出模式
python run_tests.py tests/ -v

# 指定并行进程数
python run_tests.py tests/ -n 4

# 生成Allure报告
python run_tests.py tests/ --alluredir=reports/allure-results
```

### 环境变量配置

```bash
# 设置并行进程数
set PARALLEL_WORKERS=4
# 或使用 auto 自动检测
set PARALLEL_WORKERS=auto

# 设置浏览器类型
set BROWSER=chromium  # 或 firefox, webkit

# 设置无头模式
set HEADLESS=true

# 设置超时时间（毫秒）
set TIMEOUT=30000
```

### 报告生成

```bash
# 生成Allure报告
python run_tests.py tests/ --alluredir=reports/allure-results
allure serve reports/allure-results

# 生成HTML报告
python run_tests.py tests/ --html=reports/report.html --self-contained-html
```

## 🎯 最佳实践

### 1. 页面对象设计原则

- **单一职责**：每个页面类只负责一个页面的操作
- **封装细节**：隐藏定位器和底层操作，提供业务级方法
- **链式调用**：支持方法链式调用，提高代码可读性
- **异常处理**：合理处理元素不存在、超时等异常情况

### 2. 测试用例编写规范

- **独立性**：每个测试用例应该独立运行，不依赖其他测试
- **可重复**：测试结果应该稳定，多次运行结果一致
- **清晰命名**：测试方法名应该清楚描述测试内容
- **适当注释**：复杂逻辑添加必要的注释说明

### 3. 定位器管理

- **集中管理**：将定位器定义在页面类中，便于维护
- **语义化命名**：使用有意义的定位器名称
- **稳定性优先**：选择稳定的定位方式，避免依赖易变属性
- **分层定位**：复杂页面采用分层定位策略

### 4. 测试数据管理

- **参数化测试**：使用pytest.mark.parametrize进行数据驱动测试
- **测试数据分离**：将测试数据与测试逻辑分离
- **环境隔离**：不同环境使用不同的测试数据
- **数据清理**：测试后及时清理产生的测试数据

### 5. 错误处理和调试

- **截图保存**：测试失败时自动截图，便于问题定位
- **日志记录**：记录关键操作和状态信息
- **超时设置**：合理设置元素等待和操作超时时间
- **重试机制**：对于不稳定的操作实现重试机制

---

## 📞 技术支持

如有问题或建议，请通过以下方式联系：

- 📧 邮箱：support@example.com
- 🐛 问题反馈：[GitHub Issues](https://github.com/your-repo/issues)
- 📖 文档：[项目Wiki](https://github.com/your-repo/wiki)

---

**Happy Testing! 🎉**