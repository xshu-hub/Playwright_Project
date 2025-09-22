import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestKeyboardNavigation(BaseTest):
    """键盘导航测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_keyboard_navigation(self):
        """测试键盘导航"""
        self.login_page.navigate()
        
        # 简化测试：直接输入用户名和密码，然后使用Enter提交
        self.login_page.enter_username("admin")
        self.login_page.enter_password("admin123")
        
        # 按Enter键提交表单
        self.page.keyboard.press("Enter")
        
        # 等待页面跳转（考虑到登录成功后可能有延迟）
        self.page.wait_for_url("**/pages/dashboard.html", timeout=15000)
        
        # 验证登录成功
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")


if __name__ == '__main__':
    import unittest
    unittest.main()
