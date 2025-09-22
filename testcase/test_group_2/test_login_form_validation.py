import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestLoginFormValidation(BaseTest):
    """登录表单验证测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_login_form_validation(self):
        """测试登录表单验证"""
        self.login_page.navigate()
        
        # 测试用户名长度验证
        self.login_page.enter_username("a")  # 太短
        self.login_page.enter_password("admin123")
        self.login_page.click_login_button()
        
        # 验证表单验证消息
        username_field = self.page.locator("#username")
        self.assertTrue(username_field.evaluate("el => !el.validity.valid"))


if __name__ == '__main__':
    import unittest
    unittest.main()
