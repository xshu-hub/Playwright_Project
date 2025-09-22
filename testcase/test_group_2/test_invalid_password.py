import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestInvalidPassword(BaseTest):
    """无效密码测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_invalid_password(self):
        """测试无效密码"""
        self.login_page.navigate()
        self.login_page.login("admin", "wrong_password")
        
        # 等待错误消息显示
        self.login_page.wait_for_login_error()
        error_message = self.login_page.get_error_message()
        self.assertIn("密码错误", error_message)


if __name__ == '__main__':
    import unittest
    unittest.main()
