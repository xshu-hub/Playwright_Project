"""Demo test for test_003 package"""
import pytest
from pages.login_page import LoginPage


class TestDemo:
    """Demo测试类"""
    
    def test_demo_function(self, page):
        """简单的演示测试"""
        login_page = LoginPage(page)
        login_page.navigate()
        
        # 验证页面标题
        assert "登录" in page.title()
        
        # 验证登录页面元素
        login_page.verify_login_page_elements()