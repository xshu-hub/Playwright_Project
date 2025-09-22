import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestEmptyUsername(BaseTest):
    """空用户名测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_empty_username(self):
        """测试空用户名"""
        self.login_page.navigate()
        self.login_page.enter_password("admin123")
        self.login_page.click_login_button()
        
        # 验证HTML5表单验证
        username_field = self.page.locator("#username")
        self.assertTrue(username_field.evaluate("el => !el.validity.valid"))


if __name__ == '__main__':
    import unittest
    unittest.main()
