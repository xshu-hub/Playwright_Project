import time
import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from tests.base_test import BaseTest
import allure
from utils.allure_helper import allure_step, AllureSeverity


@allure.epic("用户认证系统")
@allure.feature("用户登录")
class TestLogin(BaseTest):
    """登录功能测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        
        # 导航到登录页面后再清除存储
        self.login_page.navigate()
        self.clear_storage()
        
    @allure.story("页面元素验证")
    @allure.title("验证登录页面元素显示正确")
    @allure.description("测试登录页面的所有必要元素是否正确显示，包括标题、输入框、按钮等")
    @allure.severity(AllureSeverity.NORMAL)
    def test_login_page_elements(self):
        """测试登录页面元素显示"""
        with allure.step("验证页面标题"):
            expect(self.page).to_have_title("用户登录 - 测试系统")
        
        with allure.step("验证登录页面所有元素"):
            self.login_page.verify_login_page_elements()
        
    @allure.story("成功登录")
    @allure.title("管理员账号成功登录")
    @allure.description("测试使用管理员账号(admin/admin123)成功登录系统")
    @allure.severity(AllureSeverity.CRITICAL)
    def test_successful_login_admin(self):
        """测试管理员账号成功登录"""
        with allure.step("导航到登录页面"):
            self.login_page.navigate()
        
        with allure.step("使用管理员账号登录"):
            self.login_page.login("admin", "admin123")
        
        with allure.step("等待登录成功消息"):
            self.page.wait_for_selector(".alert.alert-success", timeout=5000)
        
        with allure.step("验证跳转到仪表板页面"):
            expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html", timeout=15000)
        
        with allure.step("等待仪表板页面加载完成"):
            self.dashboard_page.wait_for_page_load()
        
        with allure.step("验证用户信息显示正确"):
            user_info = self.dashboard_page.get_user_info()
            self.assertEqual(user_info["username"], "管理员")
            self.assertEqual(user_info["role"], "管理员")
        
    @allure.story("成功登录")
    @allure.title("普通用户账号成功登录")
    @allure.description("测试使用普通用户账号(user1/user123)成功登录系统")
    @allure.severity(AllureSeverity.CRITICAL)
    def test_successful_login_user(self):
        """测试普通用户账号成功登录"""
        with allure.step("导航到登录页面"):
            self.login_page.navigate()
        
        with allure.step("使用普通用户账号登录"):
            self.login_page.login("user1", "user123")
        
        with allure.step("验证跳转到仪表板页面"):
            expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        with allure.step("等待仪表板页面加载完成"):
            self.dashboard_page.wait_for_page_load()
        
        with allure.step("验证用户信息显示正确"):
            user_info = self.dashboard_page.get_user_info()
            # 故意让测试失败 - 期望错误的用户名
            self.assertEqual(user_info["username"], "管理员")  # 这会导致测试失败，实际应该是"张三"
            self.assertEqual(user_info["role"], "普通用户")
        
    @allure.story("演示账号登录")
    @allure.title("演示管理员账号登录")
    @allure.description("测试点击演示管理员按钮自动填充并登录")
    @allure.severity(AllureSeverity.NORMAL)
    def test_demo_admin_login(self):
        """测试演示管理员账号登录"""
        with allure.step("导航到登录页面"):
            self.login_page.navigate()
        
        with allure.step("点击演示管理员账号按钮"):
            self.login_page.click_demo_admin_button()
        
        with allure.step("等待表单填充完成"):
            self.page.wait_for_timeout(500)
        
        # 验证表单自动填充
        username = self.login_page.get_username_value()
        password = self.login_page.get_password_value()
        self.assertEqual(username, "admin")
        self.assertEqual(password, "admin123")
        
        # 提交登录
        self.login_page.click_login_button()
        
        # 验证登录成功
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
    @allure.story("演示账号登录")
    @allure.title("演示普通用户账号登录")
    @allure.description("测试点击演示普通用户按钮自动填充并登录")
    @allure.severity(AllureSeverity.NORMAL)
    def test_demo_user_login(self):
        """测试演示普通用户账号登录"""
        with allure.step("导航到登录页面"):
            self.login_page.navigate()
        
        with allure.step("点击演示普通用户账号按钮"):
            self.login_page.click_demo_user_button()
        
        with allure.step("等待表单填充完成"):
            self.page.wait_for_timeout(500)
        
        with allure.step("点击登录按钮"):
            self.login_page.click_login_button()
        
        with allure.step("验证跳转到仪表板页面"):
            expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        with allure.step("验证用户信息显示正确"):
            user_info = self.dashboard_page.get_user_info()
            self.assertEqual(user_info["username"], "张三")
            self.assertEqual(user_info["role"], "普通用户")
        
    @allure.story("登录失败")
    @allure.title("无效用户名登录失败")
    @allure.description("测试使用不存在的用户名登录时显示错误信息")
    @allure.severity(AllureSeverity.NORMAL)
    def test_invalid_username(self):
        """测试无效用户名"""
        with allure.step("导航到登录页面"):
            self.login_page.navigate()
        
        with allure.step("输入无效用户名和密码"):
            self.login_page.login("invalid_user", "password123")
        
        with allure.step("验证显示错误消息"):
            self.login_page.wait_for_error_message()
            error_message = self.login_page.get_error_message()
            self.assertIn("用户名或密码错误", error_message)
        
        with allure.step("验证仍在登录页面"):
            expect(self.page).to_have_url("http://localhost:8080/pages/login.html")
        
    @allure.story("登录失败")
    @allure.title("无效密码登录失败")
    @allure.description("测试使用错误密码登录时显示错误信息")
    @allure.severity(AllureSeverity.NORMAL)
    def test_invalid_password(self):
        """测试无效密码"""
        with allure.step("导航到登录页面"):
            self.login_page.navigate()
        
        with allure.step("输入正确用户名和错误密码"):
            self.login_page.login("admin", "wrong_password")
        
        with allure.step("验证显示错误消息"):
            self.login_page.wait_for_error_message()
            error_message = self.login_page.get_error_message()
            self.assertIn("用户名或密码错误", error_message)
        
        with allure.step("验证仍在登录页面"):
            expect(self.page).to_have_url("http://localhost:8080/pages/login.html")
        
    def test_empty_username(self):
        """测试空用户名登录"""
        self.login_page.navigate()
        
        # 只填写密码，用户名为空
        self.login_page.enter_password("admin123")
        self.login_page.click_login_button()
        
        # 验证表单验证消息
        username_field = self.page.locator(self.login_page.username_input)
        expect(username_field).to_have_attribute("required", "")
        
    def test_empty_password(self):
        """测试空密码登录"""
        self.login_page.navigate()
        
        # 只填写用户名，密码为空
        self.login_page.enter_username("admin")
        self.login_page.click_login_button()
        
        # 验证表单验证消息
        password_field = self.page.locator(self.login_page.password_input)
        expect(password_field).to_have_attribute("required", "")
        
    def test_empty_form_submission(self):
        """测试空表单提交"""
        self.login_page.navigate()
        
        # 直接点击登录按钮
        self.login_page.click_login_button()
        
        # 验证表单验证
        username_field = self.page.locator(self.login_page.username_input)
        password_field = self.page.locator(self.login_page.password_input)
        expect(username_field).to_have_attribute("required", "")
        expect(password_field).to_have_attribute("required", "")
        
    def test_login_form_validation(self):
        """测试登录表单验证"""
        self.login_page.navigate()
        
        # 测试用户名长度验证
        self.login_page.enter_username("a")  # 太短
        self.login_page.enter_password("password123")
        self.login_page.click_login_button()
        
        # 验证用户名最小长度要求
        username_field = self.page.locator(self.login_page.username_input)
        expect(username_field).to_have_attribute("minlength", "3")
        
    def test_password_visibility_toggle(self):
        """测试密码字段类型"""
        self.login_page.navigate()
        
        # 填写密码
        self.login_page.enter_password("test123")
        
        # 验证密码字段默认为password类型
        password_field = self.page.locator(self.login_page.password_input)
        expect(password_field).to_have_attribute("type", "password")
        
    def test_remember_me_functionality(self):
        """测试记住我功能"""
        self.login_page.navigate()
        
        # 勾选记住我选项并登录
        self.login_page.check_remember_login()
        self.login_page.login("admin", "admin123")
        
        # 验证登录成功
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        # 退出登录
        self.dashboard_page.logout()
        
        # 验证返回登录页面时记住我状态
        expect(self.page).to_have_url("http://localhost:8080/pages/login.html")
        
    def test_login_redirect_after_logout(self):
        """测试登出后重新登录"""
        # 先登录
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        # 退出登录
        self.dashboard_page.logout()
        
        # 验证跳转到登录页面
        expect(self.page).to_have_url("http://localhost:8080/pages/login.html")
        
        # 重新登录
        self.login_page.login("admin", "admin123")
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
    def test_login_session_persistence(self):
        """测试登录会话持久性"""
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        
        # 验证登录成功
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        # 刷新页面
        self.page.reload()
        
        # 验证仍然保持登录状态
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
    def test_direct_access_without_login(self):
        """测试未登录直接访问受保护页面"""
        # 直接访问仪表板页面
        self.page.goto("http://localhost:8080/pages/dashboard.html")
        
        # 应该被重定向到登录页面
        expect(self.page).to_have_url("http://localhost:8080/pages/login.html")
        
    def test_login_responsive_design(self):
        """测试登录页面响应式设计"""
        self.login_page.navigate()
        
        # 测试移动端视口
        self.page.set_viewport_size({"width": 375, "height": 667})
        
        # 验证登录表单仍然可见和可用
        self.assert_element_visible(self.login_page.username_input)
        self.assert_element_visible(self.login_page.password_input)
        self.assert_element_visible(self.login_page.login_button)
        
        # 恢复桌面端视口
        self.page.set_viewport_size({"width": 1280, "height": 720})
        
    def test_login_accessibility(self):
        """测试登录页面可访问性"""
        self.login_page.navigate()
        
        # 验证记住我选项的标签
        remember_label = self.page.locator("label[for='rememberMe']")
        expect(remember_label).to_be_visible()
        
        # 验证表单字段有正确的属性
        username_field = self.page.locator(self.login_page.username_input)
        password_field = self.page.locator(self.login_page.password_input)
        
        expect(username_field).to_have_attribute("id", "username")
        expect(password_field).to_have_attribute("id", "password")
        
        # 验证表单字段有placeholder属性
        expect(username_field).to_have_attribute("placeholder", "用户名")
        expect(password_field).to_have_attribute("placeholder", "密码")
        
    def test_multiple_user_login_admin(self):
        """测试管理员登录"""
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        user_info = self.dashboard_page.get_user_info()
        self.assertEqual(user_info["username"], "管理员")
        self.assertEqual(user_info["role"], "管理员")
        
    def test_multiple_user_login_user1(self):
        """测试用户1登录"""
        self.login_page.navigate()
        self.login_page.login("user1", "user123")
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        user_info = self.dashboard_page.get_user_info()
        self.assertEqual(user_info["username"], "张三")
        self.assertEqual(user_info["role"], "普通用户")
        
    def test_multiple_user_login_user2(self):
        """测试用户2登录"""
        self.login_page.navigate()
        self.login_page.login("user2", "user123")
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        user_info = self.dashboard_page.get_user_info()
        self.assertEqual(user_info["username"], "李四")
        self.assertEqual(user_info["role"], "普通用户")
        
    def test_login_performance(self):
        """测试登录性能"""
        self.login_page.navigate()
        
        # 记录登录开始时间
        start_time = time.time()
        
        # 执行登录
        self.login_page.login("admin", "admin123")
        
        # 等待页面跳转完成
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        # 记录登录结束时间
        end_time = time.time()
        login_duration = end_time - start_time
        
        # 故意让测试失败 - 设置不合理的性能要求
        self.assertLess(login_duration, 0.1, f"登录耗时过长: {login_duration}秒")  # 0.1秒内完成登录是不现实的


if __name__ == '__main__':
    import unittest
    unittest.main()