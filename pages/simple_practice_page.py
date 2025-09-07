"""简化练习页面的页面对象模型"""
from pages.base_page import BasePage
from playwright.sync_api import Page, expect
import allure


class SimplePracticePage(BasePage):
    """简化练习页面类 - 专门针对test_simple_practice.py的测试用例"""
    
    @property
    def url(self) -> str:
        """页面URL"""
        return "http://localhost:8000/practice_page.html"
    
    @property
    def title(self) -> str:
        """页面标题"""
        return "WebUI自动化测试练习页面"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 页面元素定位器 - 基于test_simple_practice.py中使用的选择器
        self.page_title = "#page-title"
        
        # 基本表单元素
        self.username_input = "[data-testid='username-input']"
        self.password_input = "[data-testid='password-input']"
        self.email_input = "[data-testid='email-input']"
        self.age_input = "[data-testid='age-input']"
        self.comments_textarea = "[data-testid='comments-textarea']"
        
        # 选择元素
        self.country_select = "[data-testid='country-select']"
        
        # 复选框 - 兴趣爱好
        self.hobby_reading = "[data-testid='hobby-reading']"
        self.hobby_music = "[data-testid='hobby-music']"
        self.hobby_sports = "[data-testid='hobby-sports']"
        
        # 单选按钮 - 性别
        self.gender_male = "[data-testid='gender-male']"
        self.gender_female = "[data-testid='gender-female']"
        
        # 按钮
        self.submit_btn = "[data-testid='submit-btn']"
        self.reset_btn = "[data-testid='reset-btn']"
        self.modal_btn = "[data-testid='modal-btn']"
        self.add_row_btn = "[data-testid='add-row-btn']"
        self.remove_row_btn = "[data-testid='remove-row-btn']"
        
        # 模态框元素
        self.modal = "[data-testid='modal']"
        self.modal_input = "[data-testid='modal-input']"
        self.modal_close = "[data-testid='modal-close']"
        
        # 标签页元素
        self.tab_1 = "[data-testid='tab-1']"
        self.tab_2 = "[data-testid='tab-2']"
        self.tab_3 = "[data-testid='tab-3']"
        self.tab_content_1 = "[data-testid='tab-content-1']"
        self.tab_content_2 = "[data-testid='tab-content-2']"
        self.tab_content_3 = "[data-testid='tab-content-3']"
        
        # 表格元素
        self.data_table = "[data-testid='data-table']"
        self.table_rows = "[data-testid='data-table'] tbody tr"
        
        # 提示信息
        self.form_alert = "#form-alert"
    
    # 页面操作方法
    
    @allure.step("导航到练习页面")
    def goto_practice_page(self):
        """导航到练习页面"""
        self.navigate(self.url)
        return self
    
    @allure.step("验证页面加载")
    def verify_page_loads(self):
        """验证页面加载成功"""
        # 验证页面标题
        expect(self.get_element(self.page_title)).to_have_text("WebUI自动化测试练习页面")
        
        # 验证基本元素存在
        expect(self.get_element(self.username_input)).to_be_visible()
        expect(self.get_element(self.password_input)).to_be_visible()
        expect(self.get_element(self.email_input)).to_be_visible()
        return self
    
    @allure.step("填写基本表单")
    def fill_basic_form_inputs(self, username: str, password: str, email: str):
        """填写基本表单输入"""
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.fill(self.email_input, email)
        return self
    
    @allure.step("验证表单输入值")
    def verify_form_input_values(self, username: str, email: str):
        """验证表单输入值"""
        expect(self.get_element(self.username_input)).to_have_value(username)
        expect(self.get_element(self.email_input)).to_have_value(email)
        return self
    
    @allure.step("选择国家")
    def select_country_option(self, country: str):
        """选择国家"""
        self.select_option(self.country_select, country)
        return self
    
    @allure.step("验证国家选择")
    def verify_country_selection(self, expected_country: str):
        """验证国家选择"""
        expect(self.get_element(self.country_select)).to_have_value(expected_country)
        return self
    
    @allure.step("选择兴趣爱好")
    def select_hobbies(self, *hobbies):
        """选择兴趣爱好复选框"""
        hobby_map = {
            'reading': self.hobby_reading,
            'music': self.hobby_music,
            'sports': self.hobby_sports
        }
        
        for hobby in hobbies:
            if hobby in hobby_map:
                self.check(hobby_map[hobby])
        return self
    
    @allure.step("验证兴趣爱好选择")
    def verify_hobby_selections(self, selected_hobbies: list, unselected_hobbies: list = None):
        """验证兴趣爱好选择状态"""
        hobby_map = {
            'reading': self.hobby_reading,
            'music': self.hobby_music,
            'sports': self.hobby_sports
        }
        
        # 验证已选择的
        for hobby in selected_hobbies:
            if hobby in hobby_map:
                expect(self.get_element(hobby_map[hobby])).to_be_checked()
        
        # 验证未选择的
        if unselected_hobbies:
            for hobby in unselected_hobbies:
                if hobby in hobby_map:
                    expect(self.get_element(hobby_map[hobby])).not_to_be_checked()
        return self
    
    @allure.step("选择性别")
    def select_gender(self, gender: str):
        """选择性别单选按钮"""
        gender_map = {
            'male': self.gender_male,
            'female': self.gender_female
        }
        
        if gender in gender_map:
            self.check(gender_map[gender])
        return self
    
    @allure.step("验证性别选择")
    def verify_gender_selection(self, selected_gender: str):
        """验证性别选择状态"""
        if selected_gender == 'male':
            expect(self.get_element(self.gender_male)).to_be_checked()
            expect(self.get_element(self.gender_female)).not_to_be_checked()
        elif selected_gender == 'female':
            expect(self.get_element(self.gender_female)).to_be_checked()
            expect(self.get_element(self.gender_male)).not_to_be_checked()
        return self
    
    @allure.step("模态框操作")
    def perform_modal_operations(self, input_text: str = "测试内容"):
        """执行模态框操作流程"""
        # 打开模态框
        self.click(self.modal_btn)
        
        # 验证模态框可见
        expect(self.get_element(self.modal)).to_be_visible()
        
        # 在模态框中输入内容
        self.fill(self.modal_input, input_text)
        
        # 关闭模态框
        self.click(self.modal_close)
        
        # 验证模态框隐藏
        expect(self.get_element(self.modal)).not_to_be_visible()
        return self
    
    @allure.step("标签页切换操作")
    def perform_tab_switching(self):
        """执行标签页切换操作"""
        # 切换到标签页2
        self.click(self.tab_2)
        expect(self.get_element(self.tab_content_2)).to_be_visible()
        expect(self.get_element(self.tab_content_1)).not_to_be_visible()
        
        # 切换到标签页3
        self.click(self.tab_3)
        expect(self.get_element(self.tab_content_3)).to_be_visible()
        expect(self.get_element(self.tab_content_2)).not_to_be_visible()
        
        # 切换回标签页1
        self.click(self.tab_1)
        expect(self.get_element(self.tab_content_1)).to_be_visible()
        expect(self.get_element(self.tab_content_3)).not_to_be_visible()
        return self
    
    @allure.step("表格操作")
    def perform_table_operations(self):
        """执行表格操作并验证"""
        # 获取初始行数
        initial_rows = self.get_element(self.table_rows).count()
        
        # 添加新行
        self.click(self.add_row_btn)
        
        # 验证行数增加
        new_rows = self.get_element(self.table_rows).count()
        assert new_rows == initial_rows + 1, "表格行数应该增加1"
        
        # 删除行
        self.click(self.remove_row_btn)
        
        # 验证行数减少
        final_rows = self.get_element(self.table_rows).count()
        assert final_rows == initial_rows, "表格行数应该恢复到初始值"
        return self
    
    @allure.step("填写完整表单")
    def fill_complete_form(self, username: str = "testuser", password: str = "password123", 
                          email: str = "test@example.com", age: str = "25", 
                          country: str = "china", comments: str = "测试备注"):
        """填写完整表单"""
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.fill(self.email_input, email)
        self.fill(self.age_input, age)
        self.select_option(self.country_select, country)
        self.check(self.hobby_reading)
        self.check(self.gender_male)
        self.fill(self.comments_textarea, comments)
        return self
    
    @allure.step("提交表单")
    def submit_form(self):
        """提交表单"""
        self.click(self.submit_btn)
        return self
    
    @allure.step("验证表单提交成功")
    def verify_form_submission_success(self):
        """验证表单提交成功"""
        expect(self.get_element(self.form_alert)).to_contain_text("表单提交成功！")
        return self
    
    @allure.step("重置表单")
    def reset_form(self):
        """重置表单"""
        self.click(self.reset_btn)
        return self
    
    @allure.step("验证表单重置")
    def verify_form_reset(self):
        """验证表单重置成功"""
        expect(self.get_element(self.username_input)).to_have_value("")
        expect(self.get_element(self.email_input)).to_have_value("")
        expect(self.get_element(self.hobby_reading)).not_to_be_checked()
        return self