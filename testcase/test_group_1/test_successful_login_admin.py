import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestSuccessfulLoginAdmin(BaseTest):
    """管理员账号成功登录测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储
        self.login_page.navigate()
        self.clear_storage()
        
    def test_successful_login_admin(self):
        """测试管理员账号成功登录"""
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        self.page.wait_for_selector(".alert.alert-success", timeout=5000)
        
        # 验证登录成功后跳转到仪表板
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        # 验证用户信息显示正确
        user_info = self.dashboard_page.get_user_info()
        self.assertEqual(user_info["name"], "管理员")
        self.assertEqual(user_info["role"], "管理员")
        
        # 添加一个故意失败的断言用于测试
        self.assertEqual("实际值", "期望值", "这是一个故意失败的断言，用于测试失败处理")


if __name__ == '__main__':
    import unittest
    unittest.main()