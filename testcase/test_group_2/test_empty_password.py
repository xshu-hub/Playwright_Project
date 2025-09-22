import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestEmptyPassword(BaseTest):
    """空密码测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_empty_password(self):
        """测试空密码"""
        self.login_page.navigate()
        self.login_page.enter_username("admin")
        self.login_page.click_login_button()
        
        # 验证HTML5表单验证
        password_field = self.page.locator("#password")
        self.assertTrue(password_field.evaluate("el => !el.validity.valid"))


if __name__ == '__main__':
    import unittest
    unittest.main()
