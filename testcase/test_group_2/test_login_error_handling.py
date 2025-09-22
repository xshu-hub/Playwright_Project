import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestLoginErrorHandling(BaseTest):
    """登录错误处理测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_login_error_handling(self):
        """测试登录错误处理"""
        self.login_page.navigate()
        
        # 测试各种错误情况
        error_cases = [
            {"username": "invalid", "password": "invalid"},
            {"username": "", "password": "admin123"},
            {"username": "admin", "password": ""},
            {"username": "", "password": ""}
        ]
        
        for case in error_cases:
            if case["username"]:
                self.login_page.enter_username(case["username"])
            if case["password"]:
                self.login_page.enter_password(case["password"])
            
            self.login_page.click_login_button()
            
            # 验证仍在登录页面或显示错误消息
            current_url = self.page.url
            self.assertIn("login.html", current_url)
            
            # 清除字段准备下一次测试
            self.login_page.clear_form()


if __name__ == '__main__':
    import unittest
    unittest.main()
