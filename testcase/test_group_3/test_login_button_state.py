import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestLoginButtonState(BaseTest):
    """登录按钮状态测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_login_button_state(self):
        """测试登录按钮状态"""
        self.login_page.navigate()
        
        # 等待页面加载完成
        self.page.wait_for_selector("button[type='submit']", timeout=5000)
        
        # 验证登录按钮初始状态
        login_button = self.page.locator("button[type='submit']")
        self.assertTrue(login_button.is_visible())
        self.assertTrue(login_button.is_enabled())
        
        # 输入用户名和密码后验证按钮状态
        self.login_page.enter_username("admin")
        self.login_page.enter_password("admin123")
        self.assertTrue(login_button.is_enabled())


if __name__ == '__main__':
    import unittest
    unittest.main()
