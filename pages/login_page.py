from playwright.sync_api import Page, expect
from .base_page import BasePage


class LoginPage(BasePage):
    """登录页面对象类"""
    
    @property
    def url(self) -> str:
        """页面URL"""
        return "http://localhost:8080/pages/login.html"
    
    @property
    def title(self) -> str:
        """页面标题"""
        return "登录 - 审批系统"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 页面元素定位器
        self.username_input = "#username"
        self.password_input = "#password"
        self.remember_checkbox = "#rememberMe"
        self.login_button = "button[type='submit']"
        self.demo_admin_button = ".demo-account[data-username='admin']"
        self.demo_user_button = ".demo-account[data-username='user1']"
        self.error_message = "#errorMessage"
        self.success_message = ".success-message"
        self.loading_state = ".btn.loading"
        
        # 页面标题和标识元素
        self.page_title = "h1.login-title"
        self.login_form = "#loginForm"
        self.demo_accounts_section = ".demo-accounts"
        
    def navigate(self):
        """导航到登录页面"""
        super().navigate(self.url)
        self.wait_for_page_load()
        
    def wait_for_page_load(self):
        """等待页面加载完成"""
        # 使用更长的超时时间等待关键元素
        self.wait_for_element(self.login_form, timeout=self.long_timeout)
        self.wait_for_element(self.username_input, timeout=self.long_timeout)
        self.wait_for_element(self.password_input, timeout=self.long_timeout)
        
    def enter_username(self, username: str):
        """输入用户名"""
        self.fill(self.username_input, username)
        
    def enter_password(self, password: str):
        """输入密码"""
        self.fill(self.password_input, password)
        
    def check_remember_login(self, should_check: bool = True):
        """设置记住登录状态"""
        checkbox = self.page.locator(self.remember_checkbox)
        if should_check and not checkbox.is_checked():
            checkbox.check()
        elif not should_check and checkbox.is_checked():
            checkbox.uncheck()
            
    def click_login_button(self):
        """点击登录按钮"""
        self.click(self.login_button)
        
    def click_demo_admin_button(self):
        """点击演示管理员账号按钮"""
        self.click(self.demo_admin_button)
        
    def click_demo_user_button(self):
        """点击演示普通用户账号按钮"""
        self.click(self.demo_user_button)
        
    def login(self, username: str, password: str, remember: bool = False):
        """执行登录操作"""
        self.enter_username(username)
        self.enter_password(password)
        if remember:
            self.check_remember_login(True)
        self.click_login_button()
        
    def login_with_demo_admin(self):
        """使用演示管理员账号登录"""
        self.click_demo_admin_button()
        self.wait_for_login_success()
        
    def login_with_demo_user(self):
        """使用演示普通用户账号登录"""
        self.click_demo_user_button()
        self.wait_for_login_success()
        
    def wait_for_login_success(self, timeout: int = 5000):
        """等待登录成功"""
        self.wait_for_element(self.success_message, timeout=timeout)
        
    def wait_for_login_error(self, timeout: int = 3000):
        """等待登录错误消息显示"""
        self.wait_for_element(self.error_message, timeout=timeout)
        
    def get_error_message(self) -> str:
        """获取错误消息"""
        return self.get_text(self.error_message)
        
    def get_success_message(self) -> str:
        """获取成功消息"""
        return self.get_text(self.success_message)
        
    def is_login_button_loading(self) -> bool:
        """检查登录按钮是否处于加载状态"""
        return self.is_element_visible(self.loading_state)
        
    def is_remember_login_checked(self) -> bool:
        """检查记住登录复选框是否被选中"""
        return self.page.locator(self.remember_checkbox).is_checked()
        
    def get_username_value(self) -> str:
        """获取用户名输入框的值"""
        return self.page.locator(self.username_input).input_value()
        
    def get_password_value(self) -> str:
        """获取密码输入框的值"""
        return self.page.locator(self.password_input).input_value()
        
    def clear_form(self):
        """清空表单"""
        self.page.locator(self.username_input).clear()
        self.page.locator(self.password_input).clear()
        if self.is_remember_login_checked():
            self.check_remember_login(False)
            
    def is_demo_accounts_visible(self) -> bool:
        """检查演示账号区域是否可见"""
        return self.is_element_visible(self.demo_accounts_section)
        
    def get_page_title(self) -> str:
        """获取页面标题"""
        return self.get_text(self.page_title)
        
    def verify_login_page_elements(self):
        """验证登录页面元素"""
        # 验证表单元素存在
        expect(self.page.locator(self.login_form)).to_be_visible()
        expect(self.page.locator(self.username_input)).to_be_visible()
        expect(self.page.locator(self.password_input)).to_be_visible()
        expect(self.page.locator(self.remember_checkbox)).to_be_visible()
        expect(self.page.locator(self.login_button)).to_be_visible()
        
        # 验证演示账号区域
        expect(self.page.locator(self.demo_accounts_section)).to_be_visible()
        expect(self.page.locator(self.demo_admin_button)).to_be_visible()
        expect(self.page.locator(self.demo_user_button)).to_be_visible()
        
        # 验证页面标题
        expect(self.page.locator(self.page_title)).to_be_visible()
        
    def verify_form_validation(self):
        """验证表单验证功能"""
        # 清空表单
        self.clear_form()
        
        # 尝试提交空表单
        self.click_login_button()
        
        # 验证必填字段验证
        username_field = self.page.locator(self.username_input)
        password_field = self.page.locator(self.password_input)
        
        # 检查HTML5验证
        expect(username_field).to_have_attribute("required")
        expect(password_field).to_have_attribute("required")
        
    def submit_form_with_enter(self):
        """使用回车键提交表单"""
        self.page.locator(self.password_input).press("Enter")
        
    def verify_responsive_design(self, width: int = 375, height: int = 667):
        """验证响应式设计"""
        # 设置移动设备视口
        self.page.set_viewport_size({"width": width, "height": height})
        
        # 验证元素在小屏幕上仍然可见
        expect(self.page.locator(self.login_form)).to_be_visible()
        expect(self.page.locator(self.username_input)).to_be_visible()
        expect(self.page.locator(self.password_input)).to_be_visible()
        
        # 恢复默认视口
        self.page.set_viewport_size({"width": 1280, "height": 720})