from playwright.sync_api import Page, expect
from .base_page import BasePage
from typing import List, Dict


class UserManagementPage(BasePage):
    """用户管理页面对象"""
    
    @property
    def url(self) -> str:
        return f"{self.base_url}/pages/user-management.html"
        
    @property
    def title(self) -> str:
        return "用户管理 - 测试系统"
        
    def __init__(self, page: Page):
        super().__init__(page)
        self.base_url = "http://localhost:8080"
        
        # 页面头部
        self.page_header = ".page-header"
        self.page_title = ".page-title"
        self.add_user_button = "#addUserBtn"
        self.refresh_button = "#refreshBtn"
        
        # 筛选器
        self.role_filter = "#roleFilter"
        self.status_filter = "#statusFilter"
        self.search_filter = "#searchFilter"
        
        # 用户列表
        self.users_container = ".users-container"
        self.users_table = "#usersTable"
        self.users_table_body = "#usersTableBody"
        self.users_count = "#usersCount"
        self.user_row = "tr"
        
        # 用户信息
        self.user_avatar = ".user-avatar"
        self.user_name = ".user-name"
        self.user_username = ".user-username"
        self.user_email = "td:nth-child(2)"
        self.role_badge = ".role-badge"
        self.status_badge = ".status-badge"
        
        # 用户操作
        self.user_actions = ".user-actions"
        self.edit_user_button = ".btn-sm:has-text('编辑')"
        self.delete_user_button = ".btn-sm:has-text('删除')"
        self.toggle_status_button = ".btn-sm:has-text('禁用'), .btn-sm:has-text('启用')"
        
        # 模态框
        self.user_modal = "#userModal"
        self.modal_title = "#modalTitle"
        self.user_form = "#userForm"
        self.save_user_button = "#saveUserBtn"
        self.close_modal_button = ".close"
        
        # 表单字段
        self.username_input = "#username"
        self.name_input = "#name"
        self.email_input = "#email"
        self.password_input = "#password"
        self.role_select = "#role"
        self.status_select = "#status"
        self.form_message = "#userFormMessage"
        
        # 空状态
        self.empty_state = ".empty-state"
        
    def navigate(self):
        """导航到用户管理页面"""
        self.page.goto(self.url)
        self.wait_for_page_load()
        
    def wait_for_page_load(self):
        """等待页面加载完成"""
        self.wait_for_element(self.page_header)
        self.wait_for_element(self.users_container)
        
    def click_add_user(self):
        """点击添加用户按钮"""
        self.click_element(self.add_user_button)
        self.wait_for_element(self.user_modal)
        
    def search_users(self, search_term: str):
        """搜索用户"""
        self.fill_input(self.search_input, search_term)
        
    def filter_by_role(self, role: str):
        """按角色筛选"""
        self.select_option(self.role_filter, role)
        
    def filter_by_status(self, status: str):
        """按状态筛选"""
        self.select_option(self.status_filter, status)
        
    def click_refresh(self):
        """点击刷新按钮"""
        self.click_element(self.refresh_button)
        
    def get_user_count(self) -> int:
        """获取用户数量"""
        return self.page.locator(self.user_row).count()
        
    def get_user_names(self) -> List[str]:
        """获取所有用户姓名"""
        names = []
        rows = self.page.locator(self.user_row)
        for i in range(rows.count()):
            name = rows.nth(i).locator(self.user_name).text_content()
            names.append(name)
        return names
        
    def get_user_info(self, index: int = 0) -> Dict[str, str]:
        """获取指定用户的信息"""
        rows = self.page.locator(self.user_row)
        if index >= rows.count():
            raise IndexError(f"用户索引 {index} 超出范围")
            
        row = rows.nth(index)
        return {
            "name": row.locator(self.user_name).text_content(),
            "username": row.locator(self.user_username).text_content(),
            "email": row.locator(self.user_email).text_content(),
            "role": row.locator(self.user_role).text_content(),
            "status": row.locator(self.user_status).text_content(),
            "last_login": row.locator(self.user_last_login).text_content()
        }
        
    def click_edit_user(self, index: int = 0):
        """点击编辑用户"""
        rows = self.page.locator(self.user_row)
        if index < rows.count():
            rows.nth(index).locator(self.edit_button).click()
            self.wait_for_element(self.user_modal)
        else:
            raise IndexError(f"用户索引 {index} 超出范围")
            
    def click_delete_user(self, index: int = 0):
        """点击删除用户"""
        rows = self.page.locator(self.user_row)
        if index < rows.count():
            rows.nth(index).locator(self.delete_button).click()
            self.wait_for_element(self.delete_modal)
        else:
            raise IndexError(f"用户索引 {index} 超出范围")
            
    def click_toggle_user_status(self, index: int = 0):
        """点击切换用户状态"""
        rows = self.page.locator(self.user_row)
        if index < rows.count():
            rows.nth(index).locator(self.toggle_status_button).click()
        else:
            raise IndexError(f"用户索引 {index} 超出范围")
            
    def fill_user_form(self, name: str, username: str, email: str, password: str = "", role: str = "user", status: str = "active"):
        """填写用户表单"""
        self.fill_input(self.form_name, name)
        self.fill_input(self.form_username, username)
        self.fill_input(self.form_email, email)
        if password:
            self.fill_input(self.form_password, password)
        self.select_option(self.form_role, role)
        self.select_option(self.form_status, status)
        
    def click_save_user(self):
        """点击保存用户"""
        self.click_element(self.save_button)
        
    def click_cancel_user_form(self):
        """点击取消用户表单"""
        self.click_element(self.cancel_button)
        
    def create_user(self, name: str, username: str, email: str, password: str, role: str = "user", status: str = "active"):
        """创建新用户"""
        self.click_add_user()
        self.fill_user_form(name, username, email, password, role, status)
        self.click_save_user()
        
    def edit_user(self, index: int, name: str = None, username: str = None, email: str = None, password: str = None, role: str = None, status: str = None):
        """编辑用户信息"""
        self.click_edit_user(index)
        
        if name is not None:
            self.fill_input(self.form_name, name)
        if username is not None:
            self.fill_input(self.form_username, username)
        if email is not None:
            self.fill_input(self.form_email, email)
        if password is not None:
            self.fill_input(self.form_password, password)
        if role is not None:
            self.select_option(self.form_role, role)
        if status is not None:
            self.select_option(self.form_status, status)
            
        self.click_save_user()
        
    def confirm_delete_user(self):
        """确认删除用户"""
        self.click_element(self.delete_confirm_button)
        
    def cancel_delete_user(self):
        """取消删除用户"""
        self.click_element(self.delete_cancel_button)
        
    def delete_user(self, index: int):
        """删除用户"""
        self.click_delete_user(index)
        self.confirm_delete_user()
        
    def close_modal(self):
        """关闭模态框"""
        self.click_element(self.modal_close)
        
    def get_modal_title(self) -> str:
        """获取模态框标题"""
        return self.get_element_text(self.modal_title)
        
    def is_user_modal_visible(self) -> bool:
        """检查用户模态框是否可见"""
        return self.is_element_visible(self.user_modal)
        
    def is_delete_modal_visible(self) -> bool:
        """检查删除确认模态框是否可见"""
        return self.is_element_visible(self.delete_modal)
        
    def is_empty_state_visible(self) -> bool:
        """检查是否显示空状态"""
        return self.is_element_visible(self.empty_state)
        
    def get_success_message(self) -> str:
        """获取成功消息"""
        return self.get_element_text(self.success_message)
        
    def get_error_message(self) -> str:
        """获取错误消息"""
        return self.get_element_text(self.error_message)
        
    def wait_for_success_message(self, timeout: int = 5000):
        """等待成功消息显示"""
        self.wait_for_element(self.success_message, timeout=timeout)
        
    def wait_for_error_message(self, timeout: int = 3000):
        """等待错误消息显示"""
        self.wait_for_element(self.error_message, timeout=timeout)
        
    def wait_for_user_update(self, timeout: int = 5000):
        """等待用户信息更新"""
        self.page.wait_for_timeout(1000)  # 等待状态更新
        
    def get_form_values(self) -> Dict[str, str]:
        """获取表单当前值"""
        return {
            "name": self.page.locator(self.form_name).input_value(),
            "username": self.page.locator(self.form_username).input_value(),
            "email": self.page.locator(self.form_email).input_value(),
            "role": self.page.locator(self.form_role).input_value(),
            "status": self.page.locator(self.form_status).input_value()
        }
        
    def verify_page_elements(self):
        """验证页面元素"""
        expect(self.page.locator(self.page_header)).to_be_visible()
        expect(self.page.locator(self.add_user_button)).to_be_visible()
        expect(self.page.locator(self.search_section)).to_be_visible()
        expect(self.page.locator(self.search_input)).to_be_visible()
        expect(self.page.locator(self.role_filter)).to_be_visible()
        expect(self.page.locator(self.status_filter)).to_be_visible()
        expect(self.page.locator(self.refresh_button)).to_be_visible()
        expect(self.page.locator(self.users_container)).to_be_visible()
        
    def verify_user_form_elements(self):
        """验证用户表单元素"""
        expect(self.page.locator(self.form_name)).to_be_visible()
        expect(self.page.locator(self.form_username)).to_be_visible()
        expect(self.page.locator(self.form_email)).to_be_visible()
        expect(self.page.locator(self.form_password)).to_be_visible()
        expect(self.page.locator(self.form_role)).to_be_visible()
        expect(self.page.locator(self.form_status)).to_be_visible()
        expect(self.page.locator(self.save_button)).to_be_visible()
        expect(self.page.locator(self.cancel_button)).to_be_visible()
        
    def verify_user_in_list(self, username: str) -> bool:
        """验证用户是否在列表中"""
        usernames = []
        rows = self.page.locator(self.user_row)
        for i in range(rows.count()):
            user_username = rows.nth(i).locator(self.user_username).text_content()
            usernames.append(user_username)
        return username in usernames
        
    def find_user_index_by_username(self, username: str) -> int:
        """根据用户名查找用户索引"""
        rows = self.page.locator(self.user_row)
        for i in range(rows.count()):
            user_username = rows.nth(i).locator(self.user_username).text_content()
            if user_username == username:
                return i
        return -1