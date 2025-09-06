"""练习页面的页面对象模型"""
from pages.base_page import BasePage
from playwright.sync_api import Page, expect
import allure


class PracticePage(BasePage):
    """练习页面类"""
    
    @property
    def url(self) -> str:
        """页面URL"""
        return "/practice_page.html"
    
    @property
    def title(self) -> str:
        """页面标题"""
        return "Web UI 自动化测试练习页面"
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.page_url = "/practice_page.html"
        
        # 基本表单元素
        self.username_input = "[data-testid='username-input']"
        self.password_input = "[data-testid='password-input']"
        self.email_input = "[data-testid='email-input']"
        self.age_input = "[data-testid='age-input']"
        self.birthday_input = "[data-testid='birthday-input']"
        self.submit_btn = "[data-testid='submit-btn']"
        self.reset_btn = "[data-testid='reset-btn']"
        
        # 选择元素
        self.country_select = "[data-testid='country-select']"
        self.hobby_reading = "[data-testid='hobby-reading']"
        self.hobby_music = "[data-testid='hobby-music']"
        self.hobby_sports = "[data-testid='hobby-sports']"
        self.hobby_travel = "[data-testid='hobby-travel']"
        self.gender_male = "[data-testid='gender-male']"
        self.gender_female = "[data-testid='gender-female']"
        self.gender_other = "[data-testid='gender-other']"
        self.comments_textarea = "[data-testid='comments-textarea']"
        
        # 按钮和交互
        self.alert_btn = "[data-testid='alert-btn']"
        self.confirm_btn = "[data-testid='confirm-btn']"
        self.prompt_btn = "[data-testid='prompt-btn']"
        self.modal_btn = "[data-testid='modal-btn']"
        self.add_row_btn = "[data-testid='add-row-btn']"
        self.remove_row_btn = "[data-testid='remove-row-btn']"
        self.start_progress_btn = "[data-testid='start-progress-btn']"
        
        # 表格
        self.data_table = "[data-testid='data-table']"
        self.table_row_1 = "[data-testid='table-row-1']"
        self.table_row_2 = "[data-testid='table-row-2']"
        self.table_row_3 = "[data-testid='table-row-3']"
        
        # 标签页
        self.tab_1 = "[data-testid='tab-1']"
        self.tab_2 = "[data-testid='tab-2']"
        self.tab_3 = "[data-testid='tab-3']"
        self.tab_content_1 = "[data-testid='tab-content-1']"
        self.tab_content_2 = "[data-testid='tab-content-2']"
        self.tab_content_3 = "[data-testid='tab-content-3']"
        self.tab1_button = "[data-testid='tab1-button']"
        self.tab2_input = "[data-testid='tab2-input']"
        self.tab3_select = "[data-testid='tab3-select']"
        
        # 模态框
        self.modal = "[data-testid='modal']"
        self.modal_close = "[data-testid='modal-close']"
        self.modal_input = "[data-testid='modal-input']"
        self.modal_confirm = "[data-testid='modal-confirm']"
        self.modal_cancel = "[data-testid='modal-cancel']"
        
        # 其他元素
        self.page_title = "#page-title"
        self.form_alert = "#form-alert"
        self.progress = "#progress"
        self.progress_text = "#progress-text"
    
    @allure.step("填写基本表单")
    def fill_basic_form(self, username: str, password: str, email: str, age: str = None, birthday: str = None):
        """填写基本表单"""
        self.fill(self.username_input, username)
        print(f"输入用户名: {username}")
        
        self.fill(self.password_input, password)
        print("输入密码")
        
        self.fill(self.email_input, email)
        print(f"输入邮箱: {email}")
        
        if age:
            self.fill(self.age_input, age)
            print(f"输入年龄: {age}")
        
        if birthday:
            self.fill(self.birthday_input, birthday)
            print(f"输入生日: {birthday}")
    
    @allure.step("提交表单")
    def submit_form(self):
        """提交表单"""
        self.click(self.submit_btn)
        print("点击提交按钮")
    
    @allure.step("重置表单")
    def reset_form(self):
        """重置表单"""
        self.click(self.reset_btn)
        print("点击重置按钮")
    
    @allure.step("选择国家")
    def select_country(self, country: str):
        """选择国家"""
        self.select_option(self.country_select, country)
        print(f"选择国家: {country}")
    
    @allure.step("选择兴趣爱好")
    def select_hobbies(self, hobbies: list):
        """选择兴趣爱好"""
        hobby_map = {
            'reading': self.hobby_reading,
            'music': self.hobby_music,
            'sports': self.hobby_sports,
            'travel': self.hobby_travel
        }
        
        for hobby in hobbies:
            if hobby in hobby_map:
                self.check(hobby_map[hobby])
                print(f"选择兴趣爱好: {hobby}")
    
    @allure.step("选择性别")
    def select_gender(self, gender: str):
        """选择性别"""
        gender_map = {
            'male': self.gender_male,
            'female': self.gender_female,
            'other': self.gender_other
        }
        
        if gender in gender_map:
            self.click(gender_map[gender])
            print(f"选择性别: {gender}")
    
    @allure.step("填写备注")
    def fill_comments(self, comments: str):
        """填写备注"""
        self.fill(self.comments_textarea, comments)
        print(f"填写备注: {comments}")
    
    @allure.step("点击警告按钮")
    def click_alert_button(self):
        """点击警告按钮"""
        self.click(self.alert_btn)
        print("点击警告按钮")
    
    @allure.step("点击确认按钮")
    def click_confirm_button(self):
        """点击确认按钮"""
        self.click(self.confirm_btn)
        print("点击确认按钮")
    
    @allure.step("点击输入按钮")
    def click_prompt_button(self):
        """点击输入按钮"""
        self.click(self.prompt_btn)
        print("点击输入按钮")
    
    @allure.step("打开模态框")
    def open_modal(self):
        """打开模态框"""
        self.click(self.modal_btn)
        print("点击打开模态框按钮")
        self.wait_for_element(self.modal, "visible")
    
    @allure.step("关闭模态框")
    def close_modal(self):
        """关闭模态框"""
        self.click(self.modal_close)
        print("点击关闭模态框")
        self.wait_for_element(self.modal, "hidden")
    
    @allure.step("在模态框中输入内容")
    def fill_modal_input(self, text: str):
        """在模态框中输入内容"""
        self.fill(self.modal_input, text)
        print(f"在模态框中输入: {text}")
    
    @allure.step("确认模态框")
    def confirm_modal(self):
        """确认模态框"""
        self.click(self.modal_confirm)
        print("点击模态框确认按钮")
        self.wait_for_element(self.modal, "hidden")
    
    @allure.step("取消模态框")
    def cancel_modal(self):
        """取消模态框"""
        self.click(self.modal_cancel)
        print("点击模态框取消按钮")
        self.wait_for_element(self.modal, "hidden")
    
    @allure.step("添加表格行")
    def add_table_row(self):
        """添加表格行"""
        self.click(self.add_row_btn)
        print("点击添加表格行按钮")
    
    @allure.step("删除表格行")
    def remove_table_row(self):
        """删除表格行"""
        self.click(self.remove_row_btn)
        print("点击删除表格行按钮")
    
    @allure.step("开始进度条")
    def start_progress(self):
        """开始进度条"""
        self.click(self.start_progress_btn)
        print("点击开始进度条按钮")
    
    @allure.step("切换到标签页")
    def switch_to_tab(self, tab_number: int):
        """切换到指定标签页"""
        tab_map = {
            1: self.tab_1,
            2: self.tab_2,
            3: self.tab_3
        }
        
        content_map = {
            1: self.tab_content_1,
            2: self.tab_content_2,
            3: self.tab_content_3
        }
        
        if tab_number in tab_map:
            self.click(tab_map[tab_number])
            # 等待tab内容变为可见
            self.wait_for_element(content_map[tab_number], "visible")
            print(f"切换到标签页 {tab_number}")
    
    @allure.step("获取表格行数")
    def get_table_row_count(self) -> int:
        """获取表格行数"""
        rows = self.page.locator(f"{self.data_table} tbody tr")
        count = rows.count()
        print(f"表格当前行数: {count}")
        return count
    
    @allure.step("验证页面标题")
    def verify_page_title(self, expected_title: str):
        """验证页面标题"""
        actual_title = self.get_text(self.page_title)
        expect(self.page.locator(self.page_title)).to_have_text(expected_title)
        print(f"验证页面标题: {actual_title}")
    
    @allure.step("验证表单警告信息")
    def verify_form_alert(self, expected_message: str):
        """验证表单警告信息"""
        self.wait_for_element(self.form_alert, "visible")
        actual_message = self.get_text(self.form_alert)
        expect(self.page.locator(self.form_alert)).to_contain_text(expected_message)
        print(f"验证警告信息: {actual_message}")
    
    @allure.step("验证模态框可见性")
    def verify_modal_visible(self, should_be_visible: bool = True):
        """验证模态框可见性"""
        if should_be_visible:
            expect(self.page.locator(self.modal)).to_be_visible()
            print("验证模态框可见")
        else:
            expect(self.page.locator(self.modal)).to_be_hidden()
            print("验证模态框隐藏")
    
    @allure.step("验证标签页内容")
    def verify_tab_content_visible(self, tab_number: int):
        """验证标签页内容可见性"""
        content_map = {
            1: self.tab_content_1,
            2: self.tab_content_2,
            3: self.tab_content_3
        }
        
        if tab_number in content_map:
            expect(self.page.locator(content_map[tab_number])).to_be_visible()
            print(f"验证标签页 {tab_number} 内容可见")
    
    @allure.step("验证进度条完成")
    def verify_progress_completed(self):
        """验证进度条完成"""
        # 等待进度条完成
        self.page.wait_for_function("document.getElementById('progress-text').textContent === '100%'")
        progress_text = self.get_text(self.progress_text)
        expect(self.page.locator(self.progress_text)).to_have_text("100%")
        print(f"验证进度条完成: {progress_text}")
    
    @allure.step("删除指定表格行")
    def delete_table_row_by_id(self, row_id: str):
        """删除指定ID的表格行"""
        delete_btn = f"button[data-id='{row_id}']"
        self.click(delete_btn)
        print(f"点击删除按钮，行ID: {row_id}")
        
        # 处理确认对话框
        self.page.on("dialog", lambda dialog: dialog.accept())
    
    @allure.step("验证表格行不存在")
    def verify_table_row_not_exists(self, row_testid: str):
        """验证表格行不存在"""
        row_selector = f"[data-testid='{row_testid}']"
        expect(self.page.locator(row_selector)).not_to_be_visible()
        print(f"验证表格行不存在: {row_testid}")