import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestSessionPersistence(BaseTest):
    """会话持久性测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_session_persistence(self):
        """测试会话持久化"""
        # 先登录
        self.login_page.navigate()
        self.login_page.enter_username("admin")
        self.login_page.enter_password("admin123")
        self.login_page.click_login_button()
        
        # 等待页面跳转（考虑到登录成功后可能有延迟）
        self.page.wait_for_url("**/pages/dashboard.html", timeout=15000)
        
        # 验证登录成功
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        # 刷新页面验证会话持久化
        self.page.reload()
        
        # 等待页面重新加载
        self.page.wait_for_url("**/pages/dashboard.html", timeout=10000)
        
        # 验证仍在仪表板页面（会话保持）
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")


if __name__ == '__main__':
    import unittest
    unittest.main()
