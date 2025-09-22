import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from testcase.base_test import BaseTest


class TestLoginPageElements(BaseTest):
    """登录页面元素显示测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储        
        self.login_page.navigate()
        self.clear_storage()
        
    def test_login_page_elements(self):
        """测试登录页面元素显示"""
        expect(self.page).to_have_title("用户登录 - 测试系统")
        self.login_page.verify_login_page_elements()


if __name__ == '__main__':
    import unittest
    unittest.main()
