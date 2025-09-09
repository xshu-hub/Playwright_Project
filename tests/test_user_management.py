import pytest
import time
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.user_management_page import UserManagementPage


class TestUserManagement:
    """用户管理功能测试用例类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前置设置"""
        self.login_page = LoginPage(page)
        self.dashboard_page = DashboardPage(page)
        self.user_management_page = UserManagementPage(page)
        
        # 清除存储
        try:
            page.evaluate("localStorage.clear()")
            page.evaluate("sessionStorage.clear()")
        except Exception:
            pass
        
    def login_as_admin(self, page: Page):
        """以管理员身份登录"""
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        
        # 等待登录成功消息出现
        page.wait_for_selector(".alert.alert-success", timeout=5000)
        
        # 验证跳转到仪表板
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html", timeout=15000)
        
    def test_add_duplicate_username(self, page: Page):
        """测试添加重复用户名"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 尝试创建与admin相同用户名的用户
        self.user_management_page.create_user(
            "重复管理员",
            "admin",  # 使用已存在的admin用户名
            "duplicate@example.com",
            "password123",
            "user",
            "active"
        )
        
        # 验证错误消息 - 先等待一下让错误消息显示
        page.wait_for_timeout(2000)
        
        # 检查是否有错误消息显示
        error_selectors = [
            ".alert.alert-error",
            ".error-message", 
            "[class*='error']",
            "#userFormMessage .error-message"
        ]
        
        error_found = False
        for selector in error_selectors:
            try:
                if page.locator(selector).is_visible():
                    error_text = page.locator(selector).text_content()
                    print(f"找到错误消息: {error_text}")
                    error_found = True
                    break
            except:
                continue
        
        if not error_found:
            # 如果没找到错误消息，截图并打印页面内容
            page.screenshot(path="debug_error_message.png")
            print("页面HTML:", page.content()[-1000:])  # 打印最后1000个字符
            
        assert error_found, "应该显示重复用户名的错误消息"
        
    def test_add_new_user_success(self, page: Page):
        """测试成功添加新用户"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 生成唯一用户名
        unique_username = f"newuser{int(time.time())}"
        
        # 创建新用户
        self.user_management_page.create_user(
            "新用户",
            unique_username,
            "newuser@example.com",
            "password123",
            "user",
            "active"
        )
        
        # 等待成功消息
        self.user_management_page.wait_for_success_message()
        
        # 验证用户已添加到列表中
        self.user_management_page.verify_user_in_list(unique_username)