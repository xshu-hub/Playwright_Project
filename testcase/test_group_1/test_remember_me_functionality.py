import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestRememberMeFunctionality(BaseTest):
    """记住我功能测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_remember_me_functionality(self):
        """测试记住我功能"""
        self.login_page.navigate()
        self.login_page.enter_username("admin")
        self.login_page.enter_password("admin123")
        
        # 检查记住我复选框
        remember_checkbox = self.page.locator("#rememberMe")
        if remember_checkbox.is_visible():
            remember_checkbox.check()
            self.assertTrue(remember_checkbox.is_checked())
        
        self.login_page.click_login_button()
        
        # 等待页面跳转（考虑到登录成功后可能有延迟）
        self.page.wait_for_url("**/pages/dashboard.html", timeout=15000)
        
        # 验证登录成功
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")


if __name__ == '__main__':
    import unittest
    unittest.main()
