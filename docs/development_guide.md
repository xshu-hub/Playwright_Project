# 开发指导

本文档提供了在 Playwright Web UI 自动化测试框架中进行开发的详细指导和规范。

## 📝 页面对象类编写规范

### 1. 类结构规范

```python
class PageName(BasePage):
    """页面描述"""
    
    @property
    def url(self) -> str:
        """页面URL"""
        return "页面地址"
    
    @property
    def title(self) -> str:
        """页面标题"""
        return "页面标题"
    
    def __init__(self, page: Page):
        super().__init__(page)
        # 元素定位器定义
        self.element_selector = "#elementId"
    
    # 页面操作方法
    def action_method(self):
        """操作描述"""
        pass
    
    # 页面验证方法
    def verify_method(self):
        """验证描述"""
        pass
```

### 2. 元素定位规范

#### 优先级顺序

1. **id** - 最稳定的定位方式
2. **data-testid** - 专门为测试设计的属性
3. **class** - 样式类名
4. **xpath** - 最后选择，复杂但灵活

#### 命名规范

- 使用描述性的变量名
- 按功能区域分组定义
- 使用下划线分隔单词

```python
def __init__(self, page: Page):
    super().__init__(page)
    
    # 表单元素
    self.username_input = "#username"
    self.password_input = "#password"
    self.submit_button = "button[type='submit']"
    
    # 消息元素
    self.success_message = ".alert-success"
    self.error_message = ".alert-error"
    
    # 导航元素
    self.nav_menu = ".nav-menu"
    self.logout_link = "a[href='/logout']"
```

### 3. 方法设计规范

#### 设计原则

- **单一职责**：每个方法只做一件事
- **返回值**：操作方法返回 self，查询方法返回具体值
- **异常处理**：在基类中统一处理

```python
def login(self, username: str, password: str) -> 'LoginPage':
    """执行登录操作"""
    self.fill(self.username_input, username)
    self.fill(self.password_input, password)
    self.click(self.submit_button)
    return self

def get_user_name(self) -> str:
    """获取用户名"""
    return self.get_text(self.user_name_display)

def is_logged_in(self) -> bool:
    """检查是否已登录"""
    return self.is_element_visible(self.logout_link)
```

### 4. 完整页面对象示例

```python
from playwright.sync_api import Page, Locator
from .base_page import BasePage
from typing import List, Dict

class UserManagementPage(BasePage):
    """用户管理页面"""
    
    @property
    def url(self) -> str:
        return "http://localhost:8080/pages/user-management.html"
    
    @property
    def title(self) -> str:
        return "用户管理 - 审批系统"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 搜索区域
        self.search_input = "#searchInput"
        self.search_button = "#searchButton"
        self.reset_button = "#resetButton"
        
        # 操作按钮
        self.add_user_button = "#addUserButton"
        self.batch_delete_button = "#batchDeleteButton"
        
        # 表格元素
        self.user_table = "#userTable"
        self.table_rows = "#userTable tbody tr"
        self.select_all_checkbox = "#selectAll"
        
        # 分页元素
        self.pagination = ".pagination"
        self.prev_page_button = ".pagination .prev"
        self.next_page_button = ".pagination .next"
        
        # 弹窗元素
        self.user_modal = "#userModal"
        self.modal_title = "#userModal .modal-title"
        self.modal_close_button = "#userModal .close"
        
        # 表单元素
        self.form_username = "#modalUsername"
        self.form_email = "#modalEmail"
        self.form_role = "#modalRole"
        self.form_save_button = "#saveUserButton"
        self.form_cancel_button = "#cancelUserButton"
    
    def search_user(self, keyword: str) -> 'UserManagementPage':
        """搜索用户"""
        self.fill(self.search_input, keyword)
        self.click(self.search_button)
        self.wait_for_table_update()
        return self
    
    def reset_search(self) -> 'UserManagementPage':
        """重置搜索"""
        self.click(self.reset_button)
        self.wait_for_table_update()
        return self
    
    def add_user(self, username: str, email: str, role: str) -> 'UserManagementPage':
        """添加用户"""
        self.click(self.add_user_button)
        self.wait_for_modal_open()
        
        self.fill(self.form_username, username)
        self.fill(self.form_email, email)
        self.select_option(self.form_role, role)
        
        self.click(self.form_save_button)
        self.wait_for_modal_close()
        self.wait_for_table_update()
        return self
    
    def edit_user(self, row_index: int, **kwargs) -> 'UserManagementPage':
        """编辑用户"""
        edit_button = f"{self.table_rows}:nth-child({row_index + 1}) .edit-button"
        self.click(edit_button)
        self.wait_for_modal_open()
        
        if 'username' in kwargs:
            self.fill(self.form_username, kwargs['username'])
        if 'email' in kwargs:
            self.fill(self.form_email, kwargs['email'])
        if 'role' in kwargs:
            self.select_option(self.form_role, kwargs['role'])
        
        self.click(self.form_save_button)
        self.wait_for_modal_close()
        self.wait_for_table_update()
        return self
    
    def delete_user(self, row_index: int) -> 'UserManagementPage':
        """删除用户"""
        delete_button = f"{self.table_rows}:nth-child({row_index + 1}) .delete-button"
        self.click(delete_button)
        
        # 确认删除
        confirm_button = ".confirm-delete"
        self.wait_for_element(confirm_button)
        self.click(confirm_button)
        
        self.wait_for_table_update()
        return self
    
    def get_user_list(self) -> List[Dict[str, str]]:
        """获取用户列表"""
        users = []
        rows = self.page.locator(self.table_rows).all()
        
        for row in rows:
            username = row.locator(".username").text_content()
            email = row.locator(".email").text_content()
            role = row.locator(".role").text_content()
            status = row.locator(".status").text_content()
            
            users.append({
                "username": username,
                "email": email,
                "role": role,
                "status": status
            })
        
        return users
    
    def get_user_count(self) -> int:
        """获取用户总数"""
        count_text = self.get_text(".user-count")
        return int(count_text.split(":")[1].strip())
    
    def select_users(self, indices: List[int]) -> 'UserManagementPage':
        """选择多个用户"""
        for index in indices:
            checkbox = f"{self.table_rows}:nth-child({index + 1}) .row-checkbox"
            self.click(checkbox)
        return self
    
    def batch_delete_selected(self) -> 'UserManagementPage':
        """批量删除选中用户"""
        self.click(self.batch_delete_button)
        
        # 确认批量删除
        confirm_button = ".confirm-batch-delete"
        self.wait_for_element(confirm_button)
        self.click(confirm_button)
        
        self.wait_for_table_update()
        return self
    
    def go_to_page(self, page_number: int) -> 'UserManagementPage':
        """跳转到指定页码"""
        page_link = f".pagination a[data-page='{page_number}']"
        self.click(page_link)
        self.wait_for_table_update()
        return self
    
    def wait_for_modal_open(self):
        """等待弹窗打开"""
        self.wait_for_element(self.user_modal)
        self.page.wait_for_selector(f"{self.user_modal}.show")
    
    def wait_for_modal_close(self):
        """等待弹窗关闭"""
        self.page.wait_for_selector(f"{self.user_modal}.show", state="hidden")
    
    def wait_for_table_update(self):
        """等待表格更新"""
        # 等待加载指示器消失
        self.page.wait_for_selector(".loading", state="hidden")
        # 等待表格内容加载
        self.wait_for_element(self.table_rows)
```

## 🧪 测试用例类编写方法

### 1. 测试类结构

```python
class TestFeatureName:
    """功能测试类描述"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前置设置"""
        # 初始化页面对象
        # 清理测试环境
        # 设置测试数据
    
    def test_positive_case(self, page: Page):
        """正向测试用例"""
        pass
    
    def test_negative_case(self, page: Page):
        """负向测试用例"""
        pass
    
    @pytest.mark.parametrize("param1,param2,expected", [
        ("value1", "value2", "expected1"),
        ("value3", "value4", "expected2"),
    ])
    def test_parameterized_case(self, page: Page, param1, param2, expected):
        """参数化测试用例"""
        pass
```

### 2. 测试方法命名规范

#### 格式

`test_[功能]_[场景]_[预期结果]`

#### 示例

- `test_login_valid_credentials_success`
- `test_login_invalid_password_show_error`
- `test_form_empty_fields_validation_error`
- `test_user_add_duplicate_username_show_warning`
- `test_search_valid_keyword_return_results`

### 3. 断言最佳实践

```python
# 使用 Playwright 的 expect 断言
from playwright.sync_api import expect

def test_page_navigation(self, page: Page):
    self.login_page.navigate()
    
    # 页面断言
    expect(page).to_have_url(self.login_page.url)
    expect(page).to_have_title(self.login_page.title)
    
    # 元素断言
    expect(page.locator("#username")).to_be_visible()
    expect(page.locator(".error-message")).to_contain_text("错误信息")
    
    # 状态断言
    expect(page.locator("#submitButton")).to_be_enabled()
    expect(page.locator(".loading")).to_be_hidden()
```

### 4. 完整测试类示例

```python
import pytest
from playwright.sync_api import Page, expect
from pages.user_management_page import UserManagementPage
from pages.login_page import LoginPage
from utils.test_data import TestData

class TestUserManagement:
    """用户管理功能测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前置设置"""
        self.login_page = LoginPage(page)
        self.user_page = UserManagementPage(page)
        self.test_data = TestData()
        
        # 登录系统
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        
        # 导航到用户管理页面
        self.user_page.navigate()
        
        # 清理测试数据
        self._cleanup_test_users()
    
    def teardown_method(self):
        """测试后置清理"""
        self._cleanup_test_users()
    
    def test_add_user_valid_data_success(self, page: Page):
        """测试添加用户 - 有效数据 - 成功"""
        user_data = self.test_data.get_valid_user()
        
        # 获取添加前的用户数量
        initial_count = self.user_page.get_user_count()
        
        # 添加用户
        self.user_page.add_user(
            username=user_data["username"],
            email=user_data["email"],
            role=user_data["role"]
        )
        
        # 验证用户已添加
        final_count = self.user_page.get_user_count()
        assert final_count == initial_count + 1
        
        # 验证用户信息
        users = self.user_page.get_user_list()
        added_user = next((u for u in users if u["username"] == user_data["username"]), None)
        assert added_user is not None
        assert added_user["email"] == user_data["email"]
        assert added_user["role"] == user_data["role"]
    
    def test_add_user_duplicate_username_show_error(self, page: Page):
        """测试添加用户 - 重复用户名 - 显示错误"""
        user_data = self.test_data.get_valid_user()
        
        # 先添加一个用户
        self.user_page.add_user(
            username=user_data["username"],
            email=user_data["email"],
            role=user_data["role"]
        )
        
        # 尝试添加重复用户名的用户
        self.user_page.click(self.user_page.add_user_button)
        self.user_page.wait_for_modal_open()
        
        self.user_page.fill(self.user_page.form_username, user_data["username"])
        self.user_page.fill(self.user_page.form_email, "different@example.com")
        self.user_page.select_option(self.user_page.form_role, user_data["role"])
        
        self.user_page.click(self.user_page.form_save_button)
        
        # 验证错误消息
        error_message = page.locator(".error-message")
        expect(error_message).to_be_visible()
        expect(error_message).to_contain_text("用户名已存在")
    
    @pytest.mark.parametrize("username,email,role,expected_error", [
        ("", "test@example.com", "user", "用户名不能为空"),
        ("testuser", "", "user", "邮箱不能为空"),
        ("testuser", "invalid-email", "user", "邮箱格式不正确"),
        ("testuser", "test@example.com", "", "角色不能为空"),
    ])
    def test_add_user_invalid_data_show_validation_error(
        self, page: Page, username, email, role, expected_error
    ):
        """测试添加用户 - 无效数据 - 显示验证错误"""
        self.user_page.click(self.user_page.add_user_button)
        self.user_page.wait_for_modal_open()
        
        if username:
            self.user_page.fill(self.user_page.form_username, username)
        if email:
            self.user_page.fill(self.user_page.form_email, email)
        if role:
            self.user_page.select_option(self.user_page.form_role, role)
        
        self.user_page.click(self.user_page.form_save_button)
        
        # 验证错误消息
        error_message = page.locator(".validation-error")
        expect(error_message).to_be_visible()
        expect(error_message).to_contain_text(expected_error)
    
    def test_search_user_valid_keyword_return_results(self, page: Page):
        """测试搜索用户 - 有效关键词 - 返回结果"""
        # 添加测试用户
        test_users = self.test_data.get_multiple_users(3)
        for user in test_users:
            self.user_page.add_user(
                username=user["username"],
                email=user["email"],
                role=user["role"]
            )
        
        # 搜索用户
        search_keyword = test_users[0]["username"][:3]  # 使用用户名前3个字符
        self.user_page.search_user(search_keyword)
        
        # 验证搜索结果
        users = self.user_page.get_user_list()
        assert len(users) > 0
        
        # 验证所有结果都包含搜索关键词
        for user in users:
            assert search_keyword.lower() in user["username"].lower()
    
    def test_edit_user_valid_data_success(self, page: Page):
        """测试编辑用户 - 有效数据 - 成功"""
        # 添加测试用户
        original_user = self.test_data.get_valid_user()
        self.user_page.add_user(
            username=original_user["username"],
            email=original_user["email"],
            role=original_user["role"]
        )
        
        # 编辑用户
        new_email = "updated@example.com"
        new_role = "admin"
        
        self.user_page.edit_user(0, email=new_email, role=new_role)
        
        # 验证用户信息已更新
        users = self.user_page.get_user_list()
        updated_user = next((u for u in users if u["username"] == original_user["username"]), None)
        
        assert updated_user is not None
        assert updated_user["email"] == new_email
        assert updated_user["role"] == new_role
    
    def test_delete_user_confirm_success(self, page: Page):
        """测试删除用户 - 确认删除 - 成功"""
        # 添加测试用户
        user_data = self.test_data.get_valid_user()
        self.user_page.add_user(
            username=user_data["username"],
            email=user_data["email"],
            role=user_data["role"]
        )
        
        # 获取删除前的用户数量
        initial_count = self.user_page.get_user_count()
        
        # 删除用户
        self.user_page.delete_user(0)
        
        # 验证用户已删除
        final_count = self.user_page.get_user_count()
        assert final_count == initial_count - 1
        
        # 验证用户不在列表中
        users = self.user_page.get_user_list()
        deleted_user = next((u for u in users if u["username"] == user_data["username"]), None)
        assert deleted_user is None
    
    def test_batch_delete_selected_users_success(self, page: Page):
        """测试批量删除 - 选中用户 - 成功"""
        # 添加多个测试用户
        test_users = self.test_data.get_multiple_users(3)
        for user in test_users:
            self.user_page.add_user(
                username=user["username"],
                email=user["email"],
                role=user["role"]
            )
        
        # 获取删除前的用户数量
        initial_count = self.user_page.get_user_count()
        
        # 选择前两个用户并批量删除
        self.user_page.select_users([0, 1])
        self.user_page.batch_delete_selected()
        
        # 验证用户已删除
        final_count = self.user_page.get_user_count()
        assert final_count == initial_count - 2
    
    def _cleanup_test_users(self):
        """清理测试用户"""
        test_usernames = self.test_data.get_test_usernames()
        users = self.user_page.get_user_list()
        
        for i, user in enumerate(users):
            if user["username"] in test_usernames:
                self.user_page.delete_user(i)
```

## 🚀 新手快速入门指南

### 步骤 1：环境准备

#### 1. 克隆项目

```bash
git clone <repository-url>
cd PlaywrightProject
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
playwright install
```

#### 3. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的配置
```

### 步骤 2：运行测试

#### 1. 运行所有测试

```bash
python run_tests.py
```

#### 2. 运行特定测试

```bash
pytest tests/test_login.py -v
```

#### 3. 运行标记测试

```bash
pytest -m smoke -v
```

### 步骤 3：编写第一个测试

#### 1. 创建页面对象

```python
# pages/my_page.py
from .base_page import BasePage

class MyPage(BasePage):
    @property
    def url(self) -> str:
        return "http://example.com/my-page"
    
    @property
    def title(self) -> str:
        return "My Page Title"
```

#### 2. 创建测试用例

```python
# tests/test_my_feature.py
import pytest
from pages.my_page import MyPage

class TestMyFeature:
    @pytest.fixture(autouse=True)
    def setup(self, page):
        self.my_page = MyPage(page)
    
    def test_my_first_test(self, page):
        self.my_page.navigate()
        # 添加测试逻辑
```

## 📋 代码模板

### 页面对象模板

```python
# pages/template_page.py
from playwright.sync_api import Page
from .base_page import BasePage

class TemplatePage(BasePage):
    """页面模板类"""
    
    @property
    def url(self) -> str:
        return "页面URL"
    
    @property
    def title(self) -> str:
        return "页面标题"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # TODO: 定义页面元素选择器
        self.main_element = "#main"
        
    def navigate(self):
        """导航到页面"""
        super().navigate(self.url)
        self.wait_for_page_load()
        
    def wait_for_page_load(self):
        """等待页面加载完成"""
        self.wait_for_element(self.main_element)
        
    # TODO: 添加页面操作方法
    def perform_action(self):
        """执行页面操作"""
        pass
        
    # TODO: 添加页面验证方法
    def verify_element(self):
        """验证页面元素"""
        pass
```

### 测试用例模板

```python
# tests/test_template.py
import pytest
from playwright.sync_api import Page, expect
from pages.template_page import TemplatePage

class TestTemplate:
    """测试模板类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前置设置"""
        self.template_page = TemplatePage(page)
        
        # TODO: 添加测试环境准备代码
        page.evaluate("localStorage.clear()")
        
    def test_positive_scenario(self, page: Page):
        """正向测试场景"""
        # TODO: 实现测试逻辑
        self.template_page.navigate()
        
        # 执行操作
        self.template_page.perform_action()
        
        # 验证结果
        expect(page).to_have_url(self.template_page.url)
        
    def test_negative_scenario(self, page: Page):
        """负向测试场景"""
        # TODO: 实现负向测试逻辑
        pass
        
    @pytest.mark.parametrize("param1,param2,expected", [
        ("value1", "value2", "expected1"),
        # TODO: 添加更多测试数据
    ])
    def test_data_driven_scenario(self, page: Page, param1, param2, expected):
        """数据驱动测试场景"""
        # TODO: 实现参数化测试逻辑
        pass
```

## 🎯 开发最佳实践

### 1. 代码质量

- 使用类型提示
- 编写清晰的文档字符串
- 遵循 PEP 8 代码规范
- 使用有意义的变量和方法名

### 2. 测试设计

- 测试用例应该独立且可重复
- 使用数据驱动测试处理多种输入
- 合理使用测试标记进行分类
- 编写清晰的测试描述

### 3. 维护性

- 定期重构重复代码
- 保持页面对象的简洁性
- 及时更新过时的定位器
- 维护测试数据的一致性

### 4. 性能优化

- 合理使用等待机制
- 避免不必要的页面加载
- 优化测试数据的准备和清理
- 并行执行独立的测试用例