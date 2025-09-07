"""使用POM模式的简化练习页面测试用例"""
import pytest
from playwright.sync_api import Page
from tests.base_test import BaseTest
from pages.simple_practice_page import SimplePracticePage
import allure


class TestSimplePracticePOM(BaseTest):
    """使用POM模式的简化练习页面测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_page_object(self, page: Page):
        """设置页面对象"""
        self.practice_page = SimplePracticePage(page)
    
    @allure.feature("页面加载")
    @allure.story("验证页面基本加载")
    def test_page_loads(self):
        """测试页面加载 - POM版本"""
        with allure.step("导航到练习页面并验证加载"):
            self.practice_page.goto_practice_page().verify_page_loads()
    
    @allure.feature("表单操作")
    @allure.story("基本表单输入")
    def test_basic_form_input(self):
        """测试基本表单输入 - POM版本"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("填写并验证表单输入"):
            (self.practice_page
             .fill_basic_form_inputs("testuser", "password123", "test@example.com")
             .verify_form_input_values("testuser", "test@example.com"))
    
    @allure.feature("表单操作")
    @allure.story("国家选择")
    def test_country_selection(self):
        """测试国家选择 - POM版本"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("选择并验证国家"):
            (self.practice_page
             .select_country_option("china")
             .verify_country_selection("china"))
    
    @allure.feature("表单操作")
    @allure.story("复选框选择")
    def test_checkbox_selection(self):
        """测试复选框选择 - POM版本"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("选择并验证兴趣爱好"):
            (self.practice_page
             .select_hobbies('reading', 'music')
             .verify_hobby_selections(['reading', 'music'], ['sports']))
    
    @allure.feature("表单操作")
    @allure.story("单选按钮选择")
    def test_radio_button_selection(self):
        """测试单选按钮选择 - POM版本"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("选择并验证性别"):
            (self.practice_page
             .select_gender('male')
             .verify_gender_selection('male'))
    
    @allure.feature("UI交互")
    @allure.story("模态框操作")
    def test_modal_operations(self):
        """测试模态框操作 - POM版本"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("执行模态框操作流程"):
            self.practice_page.perform_modal_operations("测试内容")
    
    @allure.feature("UI交互")
    @allure.story("标签页切换")
    def test_tab_switching(self):
        """测试标签页切换 - POM版本"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("执行标签页切换操作"):
            self.practice_page.perform_tab_switching()
    
    @allure.feature("表格操作")
    @allure.story("动态表格操作")
    def test_table_operations(self):
        """测试表格操作 - POM版本"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("执行表格操作"):
            self.practice_page.perform_table_operations()
    
    @allure.feature("表单操作")
    @allure.story("完整表单提交")
    def test_form_submission(self):
        """测试表单提交 - POM版本"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("填写完整表单"):
            self.practice_page.fill_complete_form()
        
        with allure.step("提交表单并验证成功"):
            (self.practice_page
             .submit_form()
             .verify_form_submission_success())
    
    @allure.feature("表单操作")
    @allure.story("表单重置")
    def test_form_reset(self):
        """测试表单重置 - POM版本"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("填写表单数据"):
            (self.practice_page
             .fill_basic_form_inputs("testuser", "password123", "test@example.com")
             .select_hobbies('reading'))
        
        with allure.step("重置表单并验证"):
            (self.practice_page
             .reset_form()
             .verify_form_reset())
    
    @allure.feature("综合测试")
    @allure.story("完整业务流程")
    def test_complete_workflow(self):
        """测试完整业务流程 - POM版本"""
        with allure.step("1. 页面加载验证"):
            self.practice_page.goto_practice_page().verify_page_loads()
        
        with allure.step("2. 填写基本信息"):
            self.practice_page.fill_basic_form_inputs("workflow_user", "secure123", "workflow@test.com")
        
        with allure.step("3. 选择个人偏好"):
            (self.practice_page
             .select_country_option("china")
             .select_hobbies('reading', 'music')
             .select_gender('male'))
        
        with allure.step("4. 验证选择结果"):
            (self.practice_page
             .verify_form_input_values("workflow_user", "workflow@test.com")
             .verify_country_selection("china")
             .verify_hobby_selections(['reading', 'music'], ['sports'])
             .verify_gender_selection('male'))
        
        with allure.step("5. 测试UI交互功能"):
            self.practice_page.perform_modal_operations("工作流测试")
            self.practice_page.perform_tab_switching()
        
        with allure.step("6. 测试表格操作"):
            self.practice_page.perform_table_operations()
        
        with allure.step("7. 完成表单提交"):
            (self.practice_page
             .fill_complete_form(username="workflow_user", email="workflow@test.com")
             .submit_form()
             .verify_form_submission_success())
    
    @allure.feature("数据驱动测试")
    @allure.story("多组数据验证")
    @pytest.mark.parametrize("username,email,country", [
        ("user1", "user1@test.com", "china"),
        ("user2", "user2@test.com", "usa"),
        ("user3", "user3@test.com", "japan"),
    ])
    def test_form_with_multiple_data(self, username: str, email: str, country: str):
        """测试多组数据的表单填写 - POM版本"""
        with allure.step(f"测试用户: {username}"):
            self.practice_page.goto_practice_page()
        
        with allure.step("填写表单数据"):
            (self.practice_page
             .fill_basic_form_inputs(username, "password123", email)
             .select_country_option(country))
        
        with allure.step("验证数据填写正确"):
            (self.practice_page
             .verify_form_input_values(username, email)
             .verify_country_selection(country))
    
    @allure.feature("错误处理")
    @allure.story("表单验证")
    def test_form_validation_workflow(self):
        """测试表单验证工作流 - POM版本"""
        with allure.step("导航到页面"):
            self.practice_page.goto_practice_page()
        
        with allure.step("填写部分表单数据"):
            self.practice_page.fill_basic_form_inputs("partial_user", "pass123", "partial@test.com")
        
        with allure.step("重置并重新填写完整数据"):
            (self.practice_page
             .reset_form()
             .verify_form_reset()
             .fill_complete_form(username="complete_user", email="complete@test.com"))
        
        with allure.step("提交并验证成功"):
            (self.practice_page
             .submit_form()
             .verify_form_submission_success())