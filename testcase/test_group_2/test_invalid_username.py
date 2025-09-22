import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestInvalidUsername(BaseTest):
    """无效用户名测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_invalid_username(self):
        """测试无效用户名"""
        self.login_page.navigate()
        self.login_page.login("invalid_user", "admin123")
        
        # 验证显示错误消息
        self.login_page.wait_for_login_error()
        error_message = self.login_page.get_error_message()
        self.assertIn("用户名不存在", error_message)


if __name__ == '__main__':
    import unittest
    unittest.main()
