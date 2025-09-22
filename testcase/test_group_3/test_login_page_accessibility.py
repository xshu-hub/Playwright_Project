import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestLoginPageAccessibility(BaseTest):
    """登录页面可访问性测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_login_page_accessibility(self):
        """测试登录页面可访问性"""
        self.login_page.navigate()
        
        # 验证表单标签
        username_label = self.page.locator("label[for='username']")
        password_label = self.page.locator("label[for='password']")
        
        if username_label.is_visible():
            self.assertTrue(username_label.is_visible())
        if password_label.is_visible():
            self.assertTrue(password_label.is_visible())
        
        # 验证输入字段的可访问性属性
        username_field = self.page.locator("#username")
        password_field = self.page.locator("#password")
        
        self.assertTrue(username_field.is_visible())
        self.assertTrue(password_field.is_visible())


if __name__ == '__main__':
    import unittest
    unittest.main()
