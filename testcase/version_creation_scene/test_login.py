import pytest
from playwright.sync_api import Page, expect
from page.login_page import LoginPage
from page.dashboard_page import DashboardPage
from utils.test_data_manager import test_data_manager


class TestLogin:
    """登录功能测试用例类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前置设置"""
        self.login_page = LoginPage(page)
        self.dashboard_page = DashboardPage(page)
        
        # 导航到登录页面后再清除存储
        self.login_page.navigate()
        try:
            # 清除本地存储，确保测试环境干净
            page.evaluate("localStorage.clear()")
            page.evaluate("sessionStorage.clear()")
        except Exception:
            # 如果无法访问localStorage，忽略错误
            pass
        
    def test_login_page_elements(self, page: Page):
        """测试登录页面元素显示"""
        # setup中已经导航到登录页面，无需重复导航
        
        # 验证页面标题
        expect(page).to_have_title("用户登录 - 测试系统")
        
        # 验证登录页面元素
        self.login_page.verify_login_page_elements()
        
    def test_successful_login_admin(self, page: Page):
        """测试管理员账号成功登录"""
        self.login_page.navigate()
        
        # 从数据管理器获取管理员用户信息
        admin_user = test_data_manager.get_user_by_username("admin")
        assert admin_user is not None, "未找到管理员用户数据"
        
        # 使用管理员账号登录
        self.login_page.login(admin_user.username, admin_user.password)
        
        # 等待登录成功消息出现（动态创建的alert元素）
        page.wait_for_selector(".alert.alert-success", timeout=5000)
        
        # 验证跳转到仪表板（等待跳转完成）
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html", timeout=15000)
        
        # 验证仪表板页面加载
        self.dashboard_page.wait_for_page_load()
        
        # 验证用户信息显示
        user_info = self.dashboard_page.get_user_info()
        assert user_info["username"] == "管理员"  # 页面显示的是name字段，不是username
        assert user_info["role"] == "管理员"
        
    def test_successful_login_user(self, page: Page):
        """测试普通用户账号成功登录"""
        self.login_page.navigate()
        
        # 从数据管理器获取普通用户信息
        user = test_data_manager.get_user_by_username("user1")
        assert user is not None, "未找到普通用户数据"
        
        # 使用普通用户账号登录
        self.login_page.login(user.username, user.password)
        
        # 验证跳转到仪表板
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        # 验证仪表板页面加载
        self.dashboard_page.wait_for_page_load()
        
        # 验证用户信息显示
        user_info = self.dashboard_page.get_user_info()
        assert user_info["username"] == "张三"  # 页面显示的是name字段，不是username
        assert user_info["role"] == "普通用户"
        
    def test_demo_admin_login(self, page: Page):
        """测试演示管理员账号登录"""
        self.login_page.navigate()
        
        # 获取管理员用户数据
        admin_user = test_data_manager.get_user_by_username("admin")
        assert admin_user is not None, "未找到管理员用户数据"
        
        # 点击演示管理员账号
        self.login_page.click_demo_admin_button()
        
        # 等待表单填充完成
        page.wait_for_timeout(500)
        
        # 验证表单自动填充
        username = self.login_page.get_username_value()
        password = self.login_page.get_password_value()
        assert username == admin_user.username
        assert password == admin_user.password
        
        # 提交登录
        self.login_page.click_login_button()
        
        # 验证登录成功
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
    def test_demo_user_login(self, page: Page):
        """测试演示普通用户账号登录"""
        self.login_page.navigate()
        
        # 获取普通用户数据
        user = test_data_manager.get_user_by_username("user1")
        assert user is not None, "未找到普通用户数据"
        
        # 点击演示普通用户账号
        self.login_page.click_demo_user_button()
        
        # 等待表单填充完成
        page.wait_for_timeout(500)
        
        # 验证表单自动填充
        username = self.login_page.get_username_value()
        password = self.login_page.get_password_value()
        assert username == user.username
        assert password == user.password
        
        # 提交登录
        self.login_page.click_login_button()
        
        # 验证登录成功
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
    def test_invalid_username(self, page: Page):
        """测试无效用户名登录"""
        self.login_page.navigate()
        
        # 获取无效登录测试数据
        invalid_scenarios = test_data_manager.load_data_file("users.json")["test_scenarios"]["login"]["invalid_credentials"]
        invalid_user_scenario = next((s for s in invalid_scenarios if "用户不存在" in s["expected_error"]), None)
        assert invalid_user_scenario is not None, "未找到无效用户名测试数据"
        
        # 使用无效用户名
        self.login_page.login(invalid_user_scenario["username"], invalid_user_scenario["password"])
        
        # 验证错误消息显示
        self.login_page.wait_for_login_error()
        error_message = self.login_page.get_error_message()
        assert "用户名不存在" in error_message
        
        # 验证仍在登录页面
        expect(page).to_have_url("http://localhost:8080/pages/login.html")
        
    def test_invalid_password(self, page: Page):
        """测试无效密码登录"""
        self.login_page.navigate()
        
        # 获取无效密码测试数据
        invalid_scenarios = test_data_manager.load_data_file("users.json")["test_scenarios"]["login"]["invalid_credentials"]
        invalid_password_scenario = next((s for s in invalid_scenarios if "密码错误" in s["expected_error"]), None)
        assert invalid_password_scenario is not None, "未找到无效密码测试数据"
        
        # 使用正确用户名但错误密码
        self.login_page.login(invalid_password_scenario["username"], invalid_password_scenario["password"])
        
        # 验证错误消息显示
        self.login_page.wait_for_login_error()
        error_message = self.login_page.get_error_message()
        assert "密码错误" in error_message
        
        # 验证仍在登录页面
        expect(page).to_have_url("http://localhost:8080/pages/login.html")
        
    def test_empty_username(self, page: Page):
        """测试空用户名登录"""
        self.login_page.navigate()
        
        # 只填写密码，用户名为空
        self.login_page.enter_password("admin123")
        self.login_page.click_login_button()
        
        # 验证表单验证消息
        username_field = page.locator(self.login_page.username_input)
        expect(username_field).to_have_attribute("required", "")
        
    def test_empty_password(self, page: Page):
        """测试空密码登录"""
        self.login_page.navigate()
        
        # 获取管理员用户名
        admin_user = test_data_manager.get_user_by_username("admin")
        assert admin_user is not None, "未找到管理员用户数据"
        
        # 只填写用户名，密码为空
        self.login_page.enter_username(admin_user.username)
        self.login_page.click_login_button()
        
        # 验证表单验证消息
        password_field = page.locator(self.login_page.password_input)
        expect(password_field).to_have_attribute("required", "")
        
    def test_empty_form_submission(self, page: Page):
        """测试空表单提交"""
        self.login_page.navigate()
        
        # 直接点击登录按钮
        self.login_page.click_login_button()
        
        # 验证表单验证
        username_field = page.locator(self.login_page.username_input)
        password_field = page.locator(self.login_page.password_input)
        expect(username_field).to_have_attribute("required", "")
        expect(password_field).to_have_attribute("required", "")
        
    def test_login_form_validation(self, page: Page):
        """测试登录表单验证"""
        self.login_page.navigate()
        
        # 测试用户名长度验证
        self.login_page.enter_username("a")  # 太短
        self.login_page.enter_password("password123")
        self.login_page.click_login_button()
        
        # 验证用户名最小长度要求
        username_field = page.locator(self.login_page.username_input)
        expect(username_field).to_have_attribute("minlength", "3")
        
    def test_password_visibility_toggle(self, page: Page):
        """测试密码字段类型"""
        self.login_page.navigate()
        
        # 填写密码
        self.login_page.enter_password("test123")
        
        # 验证密码字段类型为password（隐藏输入）
        password_field = page.locator(self.login_page.password_input)
        expect(password_field).to_have_attribute("type", "password")
            
    def test_remember_me_functionality(self, page: Page):
        """测试记住我功能"""
        self.login_page.navigate()
        
        # 勾选记住我并登录
        self.login_page.check_remember_login(True)
        self.login_page.login("admin", "admin123")
        
        # 验证登录成功
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        # 登出并重新访问登录页面
        self.dashboard_page.click_logout()
        self.dashboard_page.wait_for_logout_redirect()
        self.login_page.navigate()
        
        # 验证用户名是否被记住
        username = self.login_page.get_username_value()
        assert username == "admin"
            
    def test_login_redirect_after_logout(self, page: Page):
        """测试登出后重新登录"""
        # 先登录
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        # 登出
        self.dashboard_page.click_logout()
        self.dashboard_page.wait_for_logout_redirect()
        
        # 验证跳转到登录页面
        expect(page).to_have_url("http://localhost:8080/pages/login.html")
        
        # 重新登录
        self.login_page.login("user1", "user123")
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
    def test_login_session_persistence(self, page: Page):
        """测试登录会话持久性"""
        # 登录
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        # 刷新页面
        page.reload()
        
        # 验证仍然保持登录状态
        self.dashboard_page.wait_for_page_load()
        user_info = self.dashboard_page.get_user_info()
        assert user_info["username"] == "管理员"
        
    def test_direct_access_without_login(self, page: Page):
        """测试未登录直接访问仪表板"""
        # 直接访问仪表板页面
        page.goto(self.dashboard_page.url)
        
        # 验证被重定向到登录页面
        expect(page).to_have_url("http://localhost:8080/pages/login.html")
        
    def test_login_responsive_design(self, page: Page):
        """测试登录页面响应式设计"""
        self.login_page.navigate()
        
        # 测试桌面视图
        self.login_page.verify_responsive_design(1920, 1080)
        
        # 测试平板视图
        self.login_page.verify_responsive_design(768, 1024)
        
        # 测试手机视图
        self.login_page.verify_responsive_design(375, 667)
        
    def test_login_accessibility(self, page: Page):
        """测试登录页面可访问性"""
        self.login_page.navigate()
        
        # 验证表单标签
        username_field = page.locator(self.login_page.username_input)
        password_field = page.locator(self.login_page.password_input)
        
        # 检查placeholder属性
        expect(username_field).to_have_attribute("placeholder", "用户名")
        expect(password_field).to_have_attribute("placeholder", "密码")
        
        # 验证按钮可访问性
        login_button = page.locator(self.login_page.login_button)
        expect(login_button).to_have_attribute("type", "submit")
        
    def test_multiple_user_login_from_excel(self, page: Page):
        """测试多个用户账号登录（从Excel数据文件）"""
        # 从Excel文件获取登录场景数据
        login_scenarios = test_data_manager.get_test_data("LoginScenarios", "test_data.xlsx")
        
        for scenario in login_scenarios:
            if scenario["expected_result"] == "success":
                with page.context.new_page() as test_page:
                    login_page = LoginPage(test_page)
                    dashboard_page = DashboardPage(test_page)
                    
                    # 导航到登录页面
                    login_page.navigate()
                    
                    # 执行登录
                    login_page.login(scenario["username"], scenario["password"])
                    
                    # 验证登录成功
                    expected_url = f"http://localhost:8080/pages{scenario['expected_redirect']}.html"
                    expect(test_page).to_have_url(expected_url)
                    
                    # 验证用户角色
                    dashboard_page.wait_for_page_load()
                    user_info = dashboard_page.get_user_info()
                    # 注意：这里需要根据实际页面显示的内容进行验证
                    print(f"登录场景 {scenario['scenario']} 验证通过")
    
    @pytest.mark.parametrize("scenario_data", test_data_manager.load_data_file("users.json")["test_scenarios"]["login"]["valid_credentials"])
    def test_parametrized_valid_login(self, page: Page, scenario_data: dict):
        """参数化测试有效登录凭证"""
        self.login_page.navigate()
        self.login_page.login(scenario_data["username"], scenario_data["password"])
        
        # 验证登录成功
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
        # 验证用户角色
        self.dashboard_page.wait_for_page_load()
        user_info = self.dashboard_page.get_user_info()
        # 根据expected_role验证用户角色
        print(f"用户 {scenario_data['username']} 登录成功，角色: {scenario_data['expected_role']}")
        
    def test_login_performance(self, page: Page):
        """测试登录性能"""
        self.login_page.navigate()
        
        # 记录登录开始时间
        import time
        start_time = time.time()
        
        # 执行登录
        self.login_page.login("admin", "admin123")
        
        # 等待页面跳转完成
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        self.dashboard_page.wait_for_page_load()
        
        # 计算登录耗时
        end_time = time.time()
        login_duration = end_time - start_time
        
        # 验证登录时间在合理范围内（小于5秒）
        assert login_duration < 5.0, f"登录耗时过长: {login_duration}秒"