"""简化的练习页面测试用例"""
import pytest
from playwright.sync_api import Page, expect


class TestSimplePractice:
    """简化的练习页面测试类"""
    
    def test_page_loads(self, page: Page):
        """测试页面加载"""
        page.goto("http://localhost:8000/practice_page.html")
        
        # 验证页面标题
        expect(page.locator("#page-title")).to_have_text("WebUI自动化测试练习页面")
        
        # 验证基本元素存在
        expect(page.locator("[data-testid='username-input']")).to_be_visible()
        expect(page.locator("[data-testid='password-input']")).to_be_visible()
        expect(page.locator("[data-testid='email-input']")).to_be_visible()
    
    def test_basic_form_input(self, page: Page):
        """测试基本表单输入"""
        page.goto("http://localhost:8000/practice_page.html")
        
        # 填写表单
        page.fill("[data-testid='username-input']", "testuser")
        page.fill("[data-testid='password-input']", "password123")
        page.fill("[data-testid='email-input']", "test@example.com")
        
        # 验证输入值
        expect(page.locator("[data-testid='username-input']")).to_have_value("testuser")
        expect(page.locator("[data-testid='email-input']")).to_have_value("test@example.com")
    
    def test_country_selection(self, page: Page):
        """测试国家选择"""
        page.goto("http://localhost:8000/practice_page.html")
        
        # 选择国家
        page.select_option("[data-testid='country-select']", "china")
        
        # 验证选择
        expect(page.locator("[data-testid='country-select']")).to_have_value("china")
    
    def test_checkbox_selection(self, page: Page):
        """测试复选框选择"""
        page.goto("http://localhost:8000/practice_page.html")
        
        # 选择兴趣爱好
        page.check("[data-testid='hobby-reading']")
        page.check("[data-testid='hobby-music']")
        
        # 验证选择
        expect(page.locator("[data-testid='hobby-reading']")).to_be_checked()
        expect(page.locator("[data-testid='hobby-music']")).to_be_checked()
        expect(page.locator("[data-testid='hobby-sports']")).not_to_be_checked()
    
    def test_radio_button_selection(self, page: Page):
        """测试单选按钮选择"""
        page.goto("http://localhost:8000/practice_page.html")
        
        # 选择性别
        page.check("[data-testid='gender-male']")
        
        # 验证选择
        expect(page.locator("[data-testid='gender-male']")).to_be_checked()
        expect(page.locator("[data-testid='gender-female']")).not_to_be_checked()
    
    def test_modal_operations(self, page: Page):
        """测试模态框操作"""
        page.goto("http://localhost:8000/practice_page.html")
        
        # 打开模态框
        page.click("[data-testid='modal-btn']")
        
        # 验证模态框可见
        expect(page.locator("[data-testid='modal']")).to_be_visible()
        
        # 在模态框中输入内容
        page.fill("[data-testid='modal-input']", "测试内容")
        
        # 关闭模态框
        page.click("[data-testid='modal-close']")
        
        # 验证模态框隐藏
        expect(page.locator("[data-testid='modal']")).not_to_be_visible()
    
    def test_tab_switching(self, page: Page):
        """测试标签页切换"""
        page.goto("http://localhost:8000/practice_page.html")
        
        # 切换到标签页2
        page.click("[data-testid='tab-2']")
        expect(page.locator("[data-testid='tab-content-2']")).to_be_visible()
        expect(page.locator("[data-testid='tab-content-1']")).not_to_be_visible()
        
        # 切换到标签页3
        page.click("[data-testid='tab-3']")
        expect(page.locator("[data-testid='tab-content-3']")).to_be_visible()
        expect(page.locator("[data-testid='tab-content-2']")).not_to_be_visible()
        
        # 切换回标签页1
        page.click("[data-testid='tab-1']")
        expect(page.locator("[data-testid='tab-content-1']")).to_be_visible()
        expect(page.locator("[data-testid='tab-content-3']")).not_to_be_visible()
    
    def test_table_operations(self, page: Page):
        """测试表格操作"""
        page.goto("http://localhost:8000/practice_page.html")
        
        # 获取初始行数
        initial_rows = page.locator("[data-testid='data-table'] tbody tr").count()
        
        # 添加新行
        page.click("[data-testid='add-row-btn']")
        
        # 验证行数增加
        new_rows = page.locator("[data-testid='data-table'] tbody tr").count()
        assert new_rows == initial_rows + 1, "表格行数应该增加1"
        
        # 删除行
        page.click("[data-testid='remove-row-btn']")
        
        # 验证行数减少
        final_rows = page.locator("[data-testid='data-table'] tbody tr").count()
        assert final_rows == initial_rows, "表格行数应该恢复到初始值"
    
    def test_form_submission(self, page: Page):
        """测试表单提交"""
        page.goto("http://localhost:8000/practice_page.html")
        
        # 填写完整表单
        page.fill("[data-testid='username-input']", "testuser")
        page.fill("[data-testid='password-input']", "password123")
        page.fill("[data-testid='email-input']", "test@example.com")
        page.fill("[data-testid='age-input']", "25")
        page.select_option("[data-testid='country-select']", "china")
        page.check("[data-testid='hobby-reading']")
        page.check("[data-testid='gender-male']")
        page.fill("[data-testid='comments-textarea']", "测试备注")
        
        # 提交表单
        page.click("[data-testid='submit-btn']")
        
        # 验证提交成功消息
        expect(page.locator("#form-alert")).to_contain_text("表单提交成功！")
    
    def test_form_reset(self, page: Page):
        """测试表单重置"""
        page.goto("http://localhost:8000/practice_page.html")
        
        # 填写表单
        page.fill("[data-testid='username-input']", "testuser")
        page.fill("[data-testid='email-input']", "test@example.com")
        page.check("[data-testid='hobby-reading']")
        
        # 重置表单
        page.click("[data-testid='reset-btn']")
        
        expect(page.locator("[data-testid='username-input']")).to_have_value("")
        expect(page.locator("[data-testid='email-input']")).to_have_value("")
        expect(page.locator("[data-testid='hobby-reading']")).not_to_be_checked()