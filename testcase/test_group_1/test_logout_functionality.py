import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestLogoutFunctionality(BaseTest):
    """登出功能测试用例"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_logout_functionality(self):
        """测试登出功能"""
        # 先登录
        self.login_page.navigate()
        self.login_page.enter_username("admin")
        self.login_page.enter_password("admin123")
        self.login_page.click_login_button()
        
        # 等待页面跳转（考虑到登录成功后可能有延迟）
        self.page.wait_for_url("**/pages/dashboard.html", timeout=15000)
        
        # 验证登录成功
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        # 执行登出
        self.dashboard_page.logout()
        
        # 等待登出完成
        self.page.wait_for_url("**/pages/login.html", timeout=10000)
        
        # 验证重定向到登录页面
        expect(self.page).to_have_url("http://localhost:8080/pages/login.html")


if __name__ == '__main__':
    import unittest
    unittest.main()
