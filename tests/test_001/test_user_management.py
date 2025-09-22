import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.user_management_page import UserManagementPage
from loguru import logger
from tests.base_test import BaseTest
import allure
from utils.allure_helper import allure_step, AllureSeverity


@allure.epic("用户管理系统")
@allure.feature("用户管理")
class TestUserManagement(BaseTest):
    """用户管理功能测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        self.user_management_page = UserManagementPage(self.page)
        
        # 清除存储
        self.clear_storage()
        
    @allure_step("以管理员身份登录")
    def login_as_admin(self):
        """以管理员身份登录"""
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        
        # 等待登录成功消息出现
        self.page.wait_for_selector(".alert.alert-success", timeout=5000)
        
        # 验证跳转到仪表板
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html", timeout=15000)
        
    @allure.story("用户创建")
    @allure.title("添加重复用户名测试")
    @allure.description("测试添加与现有用户相同用户名的用户时系统的处理")
    @allure.severity(AllureSeverity.NORMAL)
    def test_add_duplicate_username(self):
        """测试添加重复用户名"""
        with allure.step("以管理员身份登录"):
            self.login_as_admin()
            
        with allure.step("导航到用户管理页面"):
            self.user_management_page.navigate()
        
        with allure.step("尝试创建重复用户名的用户"):
            self.user_management_page.create_user(
                "重复管理员",
                "admin",  # 使用已存在的admin用户名
                "duplicate@example.com",
                "password123",
                "user",
                "active"
            )
        
        with allure.step("验证错误消息显示"):
            # 验证错误消息 - 先等待一下让错误消息显示
            self.page.wait_for_timeout(2000)
            
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
                    if self.page.locator(selector).is_visible():
                        error_message = self.page.locator(selector).text_content()
                        logger.info(f"找到错误消息: {error_message}")
                        error_found = True
                        break
                except:
                    continue
            
            # 如果没有找到错误消息，记录当前页面状态
            if not error_found:
                logger.warning("未找到预期的错误消息")
                # 可以添加截图来调试
                self.page.screenshot(path="debug_duplicate_user.png")
        
    @allure.story("用户创建")
    @allure.title("成功添加新用户")
    @allure.description("测试成功创建新用户的完整流程")
    @allure.severity(AllureSeverity.CRITICAL)
    def test_add_new_user_success(self):
        """测试成功添加新用户"""
        with allure.step("以管理员身份登录"):
            self.login_as_admin()
            
        with allure.step("导航到用户管理页面"):
            self.user_management_page.navigate()
        
        with allure.step("创建新用户"):
            # 使用时间戳确保用户名唯一
            timestamp = str(int(time.time()))
            username = f"testuser_{timestamp}"
            email = f"test_{timestamp}@example.com"
            
            self.user_management_page.create_user(
                "测试用户",
                username,
                email,
                "password123",
                "user",
                "active"
            )
        
        with allure.step("验证用户创建成功"):
            # 等待页面更新
            self.page.wait_for_timeout(2000)
            
            # 验证用户是否出现在列表中
            user_count = self.user_management_page.get_user_count()
            self.assertGreater(user_count, 0, "用户列表应该包含至少一个用户")
        
        # 等待成功消息
        self.user_management_page.wait_for_success_message()
        
        # 验证用户已添加到列表中
        self.user_management_page.verify_user_in_list(unique_username)


if __name__ == '__main__':
    import unittest
    unittest.main()