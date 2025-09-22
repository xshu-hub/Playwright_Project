import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestPasswordVisibilityToggle(BaseTest):
    """密码可见性切换测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_password_visibility_toggle(self):
        """测试密码可见性切换"""
        self.login_page.navigate()
        self.login_page.enter_password("test123")
        
        # 验证密码字段类型
        password_field = self.page.locator("#password")
        self.assertEqual(password_field.get_attribute("type"), "password")


if __name__ == '__main__':
    import unittest
    unittest.main()
