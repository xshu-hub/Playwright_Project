import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestDemoAdminLogin(BaseTest):
    """演示管理员账号登录测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_demo_admin_login(self):
        """测试演示管理员账号登录"""
        self.login_page.navigate()
        self.login_page.click_demo_admin_button()
        
        # 验证用户名和密码已自动填写       
        username_value = self.page.locator("#username").input_value()
        password_value = self.page.locator("#password").input_value()
        self.assertEqual(username_value, "admin")
        self.assertEqual(password_value, "admin123")
        
        # 点击登录按钮
        self.login_page.click_login_button()
        self.page.wait_for_selector(".alert.alert-success", timeout=5000)
        
        # 验证登录成功后跳转到仪表板页面      
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")


if __name__ == '__main__':
    import unittest
    unittest.main()
