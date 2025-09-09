# 核心组件使用方法

本文档详细介绍了框架中核心组件的使用方法和最佳实践。

## 🏗️ 页面对象模型基类 (BasePage)

### 功能说明

`BasePage` 是所有页面对象的基类，提供了通用的页面操作方法：

- **页面导航**：`navigate()`, `wait_for_page_load()`
- **元素操作**：`click()`, `fill()`, `get_text()`, `wait_for_element()`
- **断言验证**：`expect_element_visible()`, `expect_text_contains()`
- **截图日志**：自动截图和日志记录

### 核心方法

```python
class BasePage(ABC):
    @property
    @abstractmethod
    def url(self) -> str:
        """页面 URL"""
        pass
    
    @property
    @abstractmethod
    def title(self) -> str:
        """页面标题"""
        pass
    
    def navigate(self, url: str = None) -> 'BasePage':
        """导航到页面"""
        
    def get_element(self, selector: str) -> Locator:
        """获取页面元素"""
        
    def click(self, selector: str, **kwargs) -> None:
        """点击元素"""
        
    def fill(self, selector: str, value: str) -> None:
        """填充输入框"""
```

### 使用示例

#### 基础页面对象

```python
from playwright.sync_api import Page
from .base_page import BasePage

class LoginPage(BasePage):
    @property
    def url(self) -> str:
        return "http://localhost:8080/pages/login.html"
    
    @property
    def title(self) -> str:
        return "登录 - 审批系统"
    
    def __init__(self, page: Page):
        super().__init__(page)
        # 定义页面元素
        self.username_input = "#username"
        self.password_input = "#password"
        self.login_button = "button[type='submit']"
        self.error_message = "#errorMessage"
    
    def login(self, username: str, password: str):
        """执行登录操作"""
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)
    
    def get_error_message(self) -> str:
        """获取错误消息"""
        return self.get_text(self.error_message)
```

#### 高级页面对象

```python
class DashboardPage(BasePage):
    @property
    def url(self) -> str:
        return "http://localhost:8080/pages/dashboard.html"
    
    @property
    def title(self) -> str:
        return "仪表板 - 审批系统"
    
    def __init__(self, page: Page):
        super().__init__(page)
        # 导航元素
        self.nav_menu = ".nav-menu"
        self.user_dropdown = ".user-dropdown"
        self.logout_link = "a[href='/logout']"
        
        # 内容元素
        self.welcome_message = ".welcome-message"
        self.stats_cards = ".stats-card"
        self.recent_activities = ".recent-activities"
    
    def get_user_info(self) -> dict:
        """获取用户信息"""
        self.click(self.user_dropdown)
        username = self.get_text(".user-name")
        role = self.get_text(".user-role")
        return {"username": username, "role": role}
    
    def logout(self):
        """退出登录"""
        self.click(self.user_dropdown)
        self.click(self.logout_link)
    
    def get_stats_data(self) -> list:
        """获取统计数据"""
        stats = []
        elements = self.page.locator(self.stats_cards).all()
        for element in elements:
            title = element.locator(".card-title").text_content()
            value = element.locator(".card-value").text_content()
            stats.append({"title": title, "value": value})
        return stats
```

## 🧪 测试基类 (BaseTest)

### 接口定义

```python
class BaseTest(ABC):
    def setup_method(self, method):
        """测试方法前置操作"""
        
    def teardown_method(self, method):
        """测试方法后置操作"""
        
    def take_screenshot(self, name: str = None):
        """截图方法"""
        
    def assert_page_title(self, expected_title: str):
        """断言页面标题"""
```

### 使用规范

1. **继承基类**：所有测试类都应继承 `BaseTest`
2. **使用 fixture**：通过 `@pytest.fixture(autouse=True)` 设置测试前置条件
3. **异常处理**：基类会自动处理测试失败时的截图和日志记录

### 使用示例

#### 基础测试类

```python
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

class TestLogin:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前置设置"""
        self.login_page = LoginPage(page)
        self.dashboard_page = DashboardPage(page)
        
        # 清除存储
        page.evaluate("localStorage.clear()")
        page.evaluate("sessionStorage.clear()")
    
    def test_successful_login(self, page: Page):
        """测试成功登录"""
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        
        # 验证跳转
        expect(page).to_have_url(self.dashboard_page.url)
        
        # 验证用户信息
        user_info = self.dashboard_page.get_user_info()
        assert user_info["username"] == "管理员"
    
    @pytest.mark.parametrize("username,password,expected_error", [
        ("", "password", "用户名不能为空"),
        ("admin", "", "密码不能为空"),
        ("invalid", "password", "用户名或密码错误")
    ])
    def test_login_validation(self, page: Page, username, password, expected_error):
        """测试登录验证"""
        self.login_page.navigate()
        self.login_page.login(username, password)
        
        error_msg = self.login_page.get_error_message()
        assert expected_error in error_msg
```

#### 高级测试类

```python
class TestDashboard:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前置设置"""
        self.login_page = LoginPage(page)
        self.dashboard_page = DashboardPage(page)
        
        # 登录到系统
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        
        # 等待仪表板加载
        expect(page).to_have_url(self.dashboard_page.url)
    
    def test_dashboard_elements_visible(self, page: Page):
        """测试仪表板元素可见性"""
        # 验证导航元素
        expect(page.locator(self.dashboard_page.nav_menu)).to_be_visible()
        expect(page.locator(self.dashboard_page.user_dropdown)).to_be_visible()
        
        # 验证内容元素
        expect(page.locator(self.dashboard_page.welcome_message)).to_be_visible()
        expect(page.locator(self.dashboard_page.stats_cards)).to_be_visible()
    
    def test_user_info_display(self, page: Page):
        """测试用户信息显示"""
        user_info = self.dashboard_page.get_user_info()
        
        assert user_info["username"] is not None
        assert user_info["role"] is not None
        assert len(user_info["username"]) > 0
    
    def test_stats_data_loading(self, page: Page):
        """测试统计数据加载"""
        stats = self.dashboard_page.get_stats_data()
        
        assert len(stats) > 0
        for stat in stats:
            assert "title" in stat
            assert "value" in stat
            assert stat["title"] is not None
            assert stat["value"] is not None
    
    def test_logout_functionality(self, page: Page):
        """测试退出登录功能"""
        self.dashboard_page.logout()
        
        # 验证跳转到登录页
        expect(page).to_have_url(self.login_page.url)
        
        # 验证登录表单可见
        expect(page.locator(self.login_page.username_input)).to_be_visible()
```

## 🛠️ 工具助手类

### ScreenshotHelper 使用

```python
from utils.screenshot_helper import ScreenshotHelper

class TestWithScreenshots:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.screenshot_helper = ScreenshotHelper(page)
        self.login_page = LoginPage(page)
    
    def test_login_with_screenshots(self, page: Page):
        """带截图的登录测试"""
        # 步骤截图
        self.login_page.navigate()
        self.screenshot_helper.take_step_screenshot("页面加载完成")
        
        # 元素截图
        self.screenshot_helper.take_element_screenshot(
            "#loginForm", 
            "login_form.png", 
            "登录表单"
        )
        
        # 执行登录
        self.login_page.login("admin", "admin123")
        
        # 结果截图
        self.screenshot_helper.take_step_screenshot("登录完成")
```

### VideoHelper 使用

```python
from utils.video_helper import VideoHelper

class TestWithVideo:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, context):
        self.video_helper = VideoHelper(context)
        self.login_page = LoginPage(page)
    
    def test_login_with_video(self, page: Page):
        """带视频录制的登录测试"""
        # 开始录制
        self.video_helper.start_recording("login_test")
        
        try:
            # 执行测试步骤
            self.login_page.navigate()
            self.login_page.login("admin", "admin123")
            
            # 验证结果
            expect(page).to_have_url("/dashboard")
            
        finally:
            # 保存视频
            video_path = self.video_helper.stop_recording(save_video=True)
            print(f"视频已保存到: {video_path}")
```

## 📋 最佳实践

### 页面对象设计原则

1. **单一职责**：每个页面对象只负责一个页面
2. **封装性**：隐藏页面内部实现细节
3. **可重用性**：方法设计要便于在不同测试中重用
4. **可维护性**：元素定位和操作逻辑分离

### 测试用例设计原则

1. **独立性**：每个测试用例应该独立运行
2. **可读性**：测试名称和步骤要清晰明了
3. **可维护性**：使用页面对象模式，避免重复代码
4. **稳定性**：合理使用等待和断言机制

### 代码组织建议

```
pages/
├── __init__.py
├── base_page.py          # 基础页面类
├── login_page.py         # 登录页面
├── dashboard_page.py     # 仪表板页面
└── user_management_page.py  # 用户管理页面

tests/
├── __init__.py
├── conftest.py           # 测试配置
├── test_login.py         # 登录测试
├── test_dashboard.py     # 仪表板测试
└── test_user_management.py  # 用户管理测试
```

### 错误处理策略

```python
class RobustPage(BasePage):
    def safe_click(self, selector: str, timeout: int = 5000):
        """安全点击，带重试机制"""
        try:
            self.wait_for_element(selector, timeout=timeout)
            self.click(selector)
        except TimeoutError:
            self.logger.warning(f"元素 {selector} 点击超时，尝试重新定位")
            self.page.reload()
            self.wait_for_element(selector, timeout=timeout)
            self.click(selector)
    
    def safe_fill(self, selector: str, value: str, clear_first: bool = True):
        """安全填充，确保输入成功"""
        element = self.get_element(selector)
        
        if clear_first:
            element.clear()
        
        element.fill(value)
        
        # 验证输入是否成功
        actual_value = element.input_value()
        if actual_value != value:
            self.logger.warning(f"输入验证失败，期望: {value}, 实际: {actual_value}")
            element.clear()
            element.fill(value)
```