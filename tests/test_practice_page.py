"""练习页面测试用例"""
import pytest
import allure
from pages.practice_page import PracticePage
from tests.base_test import BaseTest


@allure.epic("WebUI自动化测试练习")
@allure.feature("练习页面功能测试")
class TestPracticePage(BaseTest):
    """练习页面测试类"""
    
    def setup_method(self, method):
        """测试方法前置操作"""
        super().setup_method(method)
    
    @pytest.fixture(autouse=True)
    def setup_practice_page(self, setup_test_context):
        """设置练习页面"""
        self.practice_page = PracticePage(self.page)
        # 导航到练习页面
        self.page.goto("http://localhost:8000/practice_page.html")
        self.practice_page.wait_for_page_load()
    
    @allure.story("基本表单功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_basic_form_submission(self):
        """测试基本表单提交功能"""
        with allure.step("填写并提交基本表单"):
            self.practice_page.fill_basic_form(
                username="testuser",
                password="password123",
                email="test@example.com",
                age="25",
                birthday="1998-01-01"
            )
            self.practice_page.submit_form()
            
        with allure.step("验证表单提交成功"):
            self.practice_page.verify_form_alert("表单提交成功！")
    
    @allure.story("基本表单功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_form_reset(self):
        """测试表单重置功能"""
        with allure.step("填写表单数据"):
            self.practice_page.fill_basic_form(
                username="testuser",
                password="password123",
                email="test@example.com"
            )
            
        with allure.step("重置表单"):
            self.practice_page.reset_form()
            
        with allure.step("验证表单已清空"):
            # 验证输入框已清空
            username_value = self.page.locator(self.practice_page.username_input).input_value()
            assert username_value == "", "用户名输入框应该为空"
            
            email_value = self.page.locator(self.practice_page.email_input).input_value()
            assert email_value == "", "邮箱输入框应该为空"
    
    @allure.story("表单验证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_form_validation(self):
        """测试表单验证功能"""
        with allure.step("提交空表单"):
            self.practice_page.submit_form()
            
        with allure.step("验证必填字段提示"):
            # 验证浏览器原生验证消息
            username_input = self.page.locator(self.practice_page.username_input)
            assert username_input.evaluate("el => el.validity.valid") == False, "用户名字段应该显示验证错误"
    
    @allure.story("下拉选择功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_country_selection(self):
        """测试国家选择功能"""
        with allure.step("选择国家"):
            self.practice_page.select_country("china")
            
        with allure.step("验证国家选择"):
            selected_value = self.page.locator(self.practice_page.country_select).input_value()
            assert selected_value == "china", "应该选择中国"
    
    @allure.story("复选框功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_hobby_selection(self):
        """测试兴趣爱好选择功能"""
        with allure.step("选择多个兴趣爱好"):
            hobbies = ['reading', 'music', 'sports']
            self.practice_page.select_hobbies(hobbies)
            
        with allure.step("验证兴趣爱好选择"):
            for hobby in hobbies:
                hobby_map = {
                    'reading': self.practice_page.hobby_reading,
                    'music': self.practice_page.hobby_music,
                    'sports': self.practice_page.hobby_sports
                }
                checkbox = self.page.locator(hobby_map[hobby])
                assert checkbox.is_checked(), f"{hobby} 复选框应该被选中"
    
    @allure.story("单选按钮功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_gender_selection(self):
        """测试性别选择功能"""
        with allure.step("选择性别"):
            self.practice_page.select_gender('male')
            
        with allure.step("验证性别选择"):
            male_radio = self.page.locator(self.practice_page.gender_male)
            assert male_radio.is_checked(), "男性单选按钮应该被选中"
            
            female_radio = self.page.locator(self.practice_page.gender_female)
            assert not female_radio.is_checked(), "女性单选按钮不应该被选中"
    
    @allure.story("文本域功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_comments_input(self):
        """测试备注输入功能"""
        comment_text = "这是一个测试备注，包含多行内容。\n第二行内容。"
        
        with allure.step("输入备注内容"):
            self.practice_page.fill_comments(comment_text)
            
        with allure.step("验证备注内容"):
            textarea_value = self.page.locator(self.practice_page.comments_textarea).input_value()
            assert textarea_value == comment_text, "备注内容应该匹配输入的文本"
    
    @allure.story("JavaScript交互")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_alert_dialog(self):
        """测试警告对话框功能"""
        with allure.step("设置对话框处理"):
            dialog_message = None
            
            def handle_dialog(dialog):
                nonlocal dialog_message
                dialog_message = dialog.message
                dialog.accept()
            
            self.page.on("dialog", handle_dialog)
            
        with allure.step("点击警告按钮"):
            self.practice_page.click_alert_button()
            
        with allure.step("验证警告消息"):
            assert dialog_message == "这是一个警告消息！", "警告消息应该匹配预期内容"
    
    @allure.story("JavaScript交互")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_confirm_dialog(self):
        """测试确认对话框功能"""
        with allure.step("设置确认对话框处理"):
            dialog_message = None
            
            def handle_dialog(dialog):
                nonlocal dialog_message
                dialog_message = dialog.message
                dialog.accept()  # 点击确定
            
            self.page.on("dialog", handle_dialog)
            
        with allure.step("点击确认按钮"):
            self.practice_page.click_confirm_button()
            
        with allure.step("验证确认消息"):
            assert dialog_message == "你确定要执行这个操作吗？", "确认消息应该匹配预期内容"
    
    @allure.story("JavaScript交互")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_prompt_dialog(self):
        """测试输入对话框功能"""
        test_input = "测试输入内容"
        
        with allure.step("设置输入对话框处理"):
            dialog_message = None
            
            def handle_dialog(dialog):
                nonlocal dialog_message
                dialog_message = dialog.message
                dialog.accept(test_input)  # 输入内容并确定
            
            self.page.on("dialog", handle_dialog)
            
        with allure.step("点击输入按钮"):
            self.practice_page.click_prompt_button()
            
        with allure.step("验证输入消息"):
            assert dialog_message == "请输入你的名字：", "输入提示消息应该匹配预期内容"
    
    @allure.story("模态框功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_modal_operations(self):
        """测试模态框操作功能"""
        with allure.step("打开模态框"):
            self.practice_page.open_modal()
            self.practice_page.verify_modal_visible(True)
            
        with allure.step("在模态框中输入内容"):
            test_text = "模态框测试内容"
            self.practice_page.fill_modal_input(test_text)
            
        with allure.step("确认模态框"):
            self.practice_page.confirm_modal()
            self.practice_page.verify_modal_visible(False)
    
    @allure.story("模态框功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_modal_cancel(self):
        """测试模态框取消功能"""
        with allure.step("打开模态框"):
            self.practice_page.open_modal()
            self.practice_page.verify_modal_visible(True)
            
        with allure.step("取消模态框"):
            self.practice_page.cancel_modal()
            self.practice_page.verify_modal_visible(False)
    
    @allure.story("模态框功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_modal_close_button(self):
        """测试模态框关闭按钮功能"""
        with allure.step("打开模态框"):
            self.practice_page.open_modal()
            self.practice_page.verify_modal_visible(True)
            
        with allure.step("点击关闭按钮"):
            self.practice_page.close_modal()
            self.practice_page.verify_modal_visible(False)
    
    @allure.story("表格操作")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_table_add_row(self):
        """测试表格添加行功能"""
        with allure.step("获取初始行数"):
            initial_count = self.practice_page.get_table_row_count()
            
        with allure.step("添加新行"):
            self.practice_page.add_table_row()
            
        with allure.step("验证行数增加"):
            new_count = self.practice_page.get_table_row_count()
            assert new_count == initial_count + 1, "表格行数应该增加1"
    
    @allure.story("表格操作")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_table_remove_row(self):
        """测试表格删除行功能"""
        with allure.step("确保有足够的行数"):
            current_count = self.practice_page.get_table_row_count()
            if current_count < 2:
                self.practice_page.add_table_row()
            
        with allure.step("获取删除前行数"):
            initial_count = self.practice_page.get_table_row_count()
            
        with allure.step("删除行"):
            self.practice_page.remove_table_row()
            
        with allure.step("验证行数减少"):
            new_count = self.practice_page.get_table_row_count()
            assert new_count == initial_count - 1, "表格行数应该减少1"
    
    @allure.story("表格操作")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_table_delete_specific_row(self):
        """测试删除指定表格行功能"""
        with allure.step("设置确认对话框处理"):
            self.page.on("dialog", lambda dialog: dialog.accept())
            
        with allure.step("删除第一行"):
            self.practice_page.delete_table_row_by_id("1")
            
        with allure.step("验证第一行已删除"):
            self.practice_page.verify_table_row_not_exists("table-row-1")
    
    @allure.story("标签页功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_tab_switching(self):
        """测试标签页切换功能"""
        with allure.step("切换到标签页2"):
            self.practice_page.switch_to_tab(2)
            self.practice_page.verify_tab_content_visible(2)
            
        with allure.step("切换到标签页3"):
            self.practice_page.switch_to_tab(3)
            self.practice_page.verify_tab_content_visible(3)
            
        with allure.step("切换回标签页1"):
            self.practice_page.switch_to_tab(1)
            self.practice_page.verify_tab_content_visible(1)
    
    @allure.story("标签页功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_tab_content_interaction(self):
        """测试标签页内容交互功能"""
        with allure.step("在标签页1中点击按钮"):
            self.practice_page.switch_to_tab(1)
            self.practice_page.click(self.practice_page.tab1_button)
            
        with allure.step("在标签页2中输入内容"):
            self.practice_page.switch_to_tab(2)
            test_text = "标签页2测试内容"
            self.practice_page.fill(self.practice_page.tab2_input, test_text)
            
            # 验证输入内容
            input_value = self.page.locator(self.practice_page.tab2_input).input_value()
            assert input_value == test_text, "标签页2输入内容应该匹配"
            
        with allure.step("在标签页3中选择选项"):
            self.practice_page.switch_to_tab(3)
            self.practice_page.select_option(self.practice_page.tab3_select, "option2")
            
            # 验证选择内容
            selected_value = self.page.locator(self.practice_page.tab3_select).input_value()
            assert selected_value == "option2", "标签页3选择内容应该匹配"
    
    @allure.story("进度条功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.slow
    def test_progress_bar(self):
        """测试进度条功能"""
        with allure.step("启动进度条"):
            self.practice_page.start_progress()
            
        with allure.step("等待进度条完成"):
            self.practice_page.verify_progress_completed()
    
    @allure.story("综合功能测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_complete_form_workflow(self):
        """测试完整的表单工作流程"""
        with allure.step("填写基本表单"):
            self.practice_page.fill_basic_form(
                username="completeuser",
                password="securepass123",
                email="complete@test.com",
                age="30",
                birthday="1993-05-15"
            )
            
        with allure.step("提交表单并验证"):
            self.practice_page.submit_form()
            self.practice_page.verify_form_alert("表单提交成功！")
            
        with allure.step("测试其他功能"):
            # 测试模态框
            self.practice_page.open_modal()
            self.practice_page.fill_modal_input("综合测试")
            self.practice_page.confirm_modal()
            
            # 测试表格操作
            initial_count = self.practice_page.get_table_row_count()
            self.practice_page.add_table_row()
            new_count = self.practice_page.get_table_row_count()
            assert new_count == initial_count + 1, "表格行数应该增加"
            
            # 测试标签页
            self.practice_page.switch_to_tab(2)
            self.practice_page.verify_tab_content_visible(2)