import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestMultipleLoginAttempts(BaseTest):
    """多次登录尝试测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_multiple_login_attempts(self):
        """测试多次登录尝试"""
        self.login_page.navigate()
        
        # 多次尝试错误登录
        for i in range(3):
            self.login_page.enter_username("wrong_user")
            self.login_page.enter_password("wrong_pass")
            self.login_page.click_login_button()
            
            # 验证仍在登录页面
            current_url = self.page.url
            self.assertIn("login.html", current_url)
            
            # 清除输入字段
            self.login_page.clear_form()
        
        # 最后尝试正确登录
        self.login_page.enter_username("admin")
        self.login_page.enter_password("admin123")
        self.login_page.click_login_button()
        
        # 等待页面跳转（考虑到登录成功后可能有延迟）
        self.page.wait_for_url("**/pages/dashboard.html", timeout=15000)
        
        # 验证登录成功
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")


if __name__ == '__main__':
    import unittest
    unittest.main()
