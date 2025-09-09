import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.user_management_page import UserManagementPage
import time


class TestUserManagement:
    """用户管理测试用例类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前置设置"""
        self.login_page = LoginPage(page)
        self.dashboard_page = DashboardPage(page)
        self.user_management_page = UserManagementPage(page)
        
        # 清除本地存储，确保测试环境干净
        try:
            page.evaluate("localStorage.clear()")
            page.evaluate("sessionStorage.clear()")
        except Exception:
            # 如果localStorage不可访问，忽略错误
            pass
        
    def login_as_admin(self, page: Page):
        """以管理员身份登录"""
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
    def login_as_user(self, page: Page):
        """以普通用户身份登录"""
        self.login_page.navigate()
        self.login_page.login("user1", "user123")
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
    def test_user_management_page_access_admin(self, page: Page):
        """测试管理员访问用户管理页面"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 验证页面标题
        expect(page).to_have_title("用户管理 - 审批系统")
        
        # 验证页面元素
        self.user_management_page.verify_page_elements()
        
    def test_user_management_page_access_user(self, page: Page):
        """测试普通用户访问用户管理页面（权限控制）"""
        self.login_as_user(page)
        
        # 尝试访问用户管理页面
        self.user_management_page.navigate()
        
        # 根据权限设计，普通用户可能被重定向或显示权限不足
        # 这里假设会重定向到仪表板或显示错误信息
        current_url = page.url
        assert "user-management" not in current_url or "权限不足" in page.content()
        
    def test_user_list_display(self, page: Page):
        """测试用户列表显示"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 验证用户列表加载
        user_count = self.user_management_page.get_user_count()
        assert user_count >= 3  # 至少有admin, user1, user2三个默认用户
        
        # 验证用户信息显示
        if user_count > 0:
            user_info = self.user_management_page.get_user_info(0)
            assert "name" in user_info
            assert "username" in user_info
            assert "email" in user_info
            assert "role" in user_info
            assert "status" in user_info
            
    def test_add_new_user_success(self, page: Page):
        """测试成功添加新用户"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 获取初始用户数量
        initial_count = self.user_management_page.get_user_count()
        
        # 创建新用户
        timestamp = int(time.time())
        new_user_data = {
            "name": f"测试用户{timestamp}",
            "username": f"testuser{timestamp}",
            "email": f"test{timestamp}@example.com",
            "password": "test123456",
            "role": "user",
            "status": "active"
        }
        
        self.user_management_page.create_user(
            new_user_data["name"],
            new_user_data["username"],
            new_user_data["email"],
            new_user_data["password"],
            new_user_data["role"],
            new_user_data["status"]
        )
        
        # 验证成功消息
        self.user_management_page.wait_for_success_message()
        success_message = self.user_management_page.get_success_message()
        assert "用户创建成功" in success_message or "添加成功" in success_message
        
        # 验证用户数量增加
        self.user_management_page.wait_for_user_update()
        new_count = self.user_management_page.get_user_count()
        assert new_count == initial_count + 1
        
        # 验证新用户在列表中
        assert self.user_management_page.verify_user_in_list(new_user_data["username"])
        
    def test_add_user_form_validation(self, page: Page):
        """测试添加用户表单验证"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 点击添加用户按钮
        self.user_management_page.click_add_user()
        
        # 验证表单元素
        self.user_management_page.verify_user_form_elements()
        
        # 测试空表单提交
        self.user_management_page.click_save_user()
        
        # 验证必填字段
        name_field = page.locator(self.user_management_page.form_name)
        username_field = page.locator(self.user_management_page.form_username)
        email_field = page.locator(self.user_management_page.form_email)
        password_field = page.locator(self.user_management_page.form_password)
        
        expect(name_field).to_have_attribute("required", "")
        expect(username_field).to_have_attribute("required", "")
        expect(email_field).to_have_attribute("required", "")
        expect(password_field).to_have_attribute("required", "")
        
    def test_add_duplicate_username(self, page: Page):
        """测试添加重复用户名"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 尝试创建与现有用户相同用户名的用户
        self.user_management_page.create_user(
            "重复用户",
            "admin",  # 使用已存在的用户名
            "duplicate@example.com",
            "password123",
            "user",
            "active"
        )
        
        # 验证错误消息
        self.user_management_page.wait_for_error_message()
        error_message = self.user_management_page.get_error_message()
        assert "用户名已存在" in error_message or "已被使用" in error_message
        
    def test_edit_user_success(self, page: Page):
        """测试成功编辑用户信息"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 确保有用户可以编辑
        if self.user_management_page.get_user_count() > 0:
            # 获取第一个用户的原始信息
            original_info = self.user_management_page.get_user_info(0)
            
            # 编辑用户信息
            new_name = f"编辑后的{original_info['name']}"
            self.user_management_page.edit_user(0, name=new_name)
            
            # 验证成功消息
            self.user_management_page.wait_for_success_message()
            
            # 验证信息已更新
            self.user_management_page.wait_for_user_update()
            updated_info = self.user_management_page.get_user_info(0)
            assert updated_info["name"] == new_name
            
    def test_edit_user_modal(self, page: Page):
        """测试编辑用户模态框"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        if self.user_management_page.get_user_count() > 0:
            # 点击编辑按钮
            self.user_management_page.click_edit_user(0)
            
            # 验证模态框显示
            assert self.user_management_page.is_user_modal_visible()
            
            # 验证模态框标题
            modal_title = self.user_management_page.get_modal_title()
            assert "编辑用户" in modal_title or "修改用户" in modal_title
            
            # 验证表单已填充现有数据
            form_values = self.user_management_page.get_form_values()
            assert form_values["name"] != ""
            assert form_values["username"] != ""
            assert form_values["email"] != ""
            
            # 取消编辑
            self.user_management_page.click_cancel_user_form()
            
    def test_delete_user_success(self, page: Page):
        """测试成功删除用户"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 先创建一个测试用户用于删除
        timestamp = int(time.time())
        test_username = f"deletetest{timestamp}"
        
        self.user_management_page.create_user(
            f"待删除用户{timestamp}",
            test_username,
            f"delete{timestamp}@example.com",
            "delete123",
            "user",
            "active"
        )
        self.user_management_page.wait_for_success_message()
        
        # 查找并删除创建的用户
        user_index = self.user_management_page.find_user_index_by_username(test_username)
        if user_index >= 0:
            initial_count = self.user_management_page.get_user_count()
            
            # 删除用户
            self.user_management_page.delete_user(user_index)
            
            # 验证成功消息
            self.user_management_page.wait_for_success_message()
            
            # 验证用户数量减少
            self.user_management_page.wait_for_user_update()
            new_count = self.user_management_page.get_user_count()
            assert new_count == initial_count - 1
            
            # 验证用户不再在列表中
            assert not self.user_management_page.verify_user_in_list(test_username)
            
    def test_delete_user_confirmation(self, page: Page):
        """测试删除用户确认对话框"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        if self.user_management_page.get_user_count() > 0:
            # 点击删除按钮
            self.user_management_page.click_delete_user(0)
            
            # 验证删除确认模态框显示
            assert self.user_management_page.is_delete_modal_visible()
            
            # 取消删除
            self.user_management_page.cancel_delete_user()
            
            # 验证模态框关闭
            assert not self.user_management_page.is_delete_modal_visible()
            
    def test_toggle_user_status(self, page: Page):
        """测试切换用户状态"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        if self.user_management_page.get_user_count() > 1:  # 确保不是操作管理员自己
            # 获取用户原始状态
            original_info = self.user_management_page.get_user_info(1)
            original_status = original_info["status"]
            
            # 切换状态
            self.user_management_page.click_toggle_user_status(1)
            
            # 等待状态更新
            self.user_management_page.wait_for_user_update()
            
            # 验证状态已改变
            updated_info = self.user_management_page.get_user_info(1)
            updated_status = updated_info["status"]
            assert updated_status != original_status
            
    def test_user_search_functionality(self, page: Page):
        """测试用户搜索功能"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 搜索管理员用户
        self.user_management_page.search_users("admin")
        time.sleep(1)  # 等待搜索结果
        
        # 验证搜索结果
        if self.user_management_page.get_user_count() > 0:
            user_names = self.user_management_page.get_user_names()
            # 验证搜索结果包含相关用户
            assert any("admin" in name.lower() for name in user_names)
            
    def test_user_role_filter(self, page: Page):
        """测试用户角色筛选"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 按管理员角色筛选
        self.user_management_page.filter_by_role("admin")
        time.sleep(1)  # 等待筛选结果
        
        # 验证筛选结果
        if self.user_management_page.get_user_count() > 0:
            for i in range(self.user_management_page.get_user_count()):
                user_info = self.user_management_page.get_user_info(i)
                assert "管理员" in user_info["role"] or "admin" in user_info["role"].lower()
                
    def test_user_status_filter(self, page: Page):
        """测试用户状态筛选"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 按活跃状态筛选
        self.user_management_page.filter_by_status("active")
        time.sleep(1)  # 等待筛选结果
        
        # 验证筛选结果
        if self.user_management_page.get_user_count() > 0:
            for i in range(self.user_management_page.get_user_count()):
                user_info = self.user_management_page.get_user_info(i)
                assert "活跃" in user_info["status"] or "active" in user_info["status"].lower()
                
    def test_refresh_user_list(self, page: Page):
        """测试刷新用户列表"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 获取初始用户数量
        initial_count = self.user_management_page.get_user_count()
        
        # 点击刷新按钮
        self.user_management_page.click_refresh()
        
        # 等待刷新完成
        time.sleep(1)
        
        # 验证列表已刷新（数量应该保持一致）
        refreshed_count = self.user_management_page.get_user_count()
        assert refreshed_count == initial_count
        
    def test_user_form_cancel(self, page: Page):
        """测试取消用户表单操作"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 打开添加用户表单
        self.user_management_page.click_add_user()
        assert self.user_management_page.is_user_modal_visible()
        
        # 填写部分信息
        self.user_management_page.fill_user_form(
            "测试取消",
            "canceltest",
            "cancel@test.com",
            "cancel123"
        )
        
        # 取消操作
        self.user_management_page.click_cancel_user_form()
        
        # 验证模态框关闭
        assert not self.user_management_page.is_user_modal_visible()
        
    def test_user_email_validation(self, page: Page):
        """测试用户邮箱格式验证"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 打开添加用户表单
        self.user_management_page.click_add_user()
        
        # 填写无效邮箱格式
        self.user_management_page.fill_user_form(
            "邮箱测试",
            "emailtest",
            "invalid-email",  # 无效邮箱格式
            "email123"
        )
        
        # 尝试提交
        self.user_management_page.click_save_user()
        
        # 验证邮箱字段验证
        email_field = page.locator(self.user_management_page.form_email)
        expect(email_field).to_have_attribute("type", "email")
        
    def test_empty_user_list_state(self, page: Page):
        """测试空用户列表状态"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 使用一个不存在的搜索词
        self.user_management_page.search_users("不存在的用户名xyz123")
        time.sleep(1)
        
        # 验证空状态显示
        if self.user_management_page.get_user_count() == 0:
            assert self.user_management_page.is_empty_state_visible()
            
    @pytest.mark.parametrize("role,status", [
        ("admin", "active"),
        ("user", "active"),
        ("user", "inactive")
    ])
    def test_create_users_with_different_roles_and_status(self, page: Page, role: str, status: str):
        """测试创建不同角色和状态的用户"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        timestamp = int(time.time())
        username = f"param_test_{role}_{status}_{timestamp}"
        
        self.user_management_page.create_user(
            f"参数化测试用户 {role} {status}",
            username,
            f"{username}@example.com",
            "param123",
            role,
            status
        )
        
        # 验证创建成功
        self.user_management_page.wait_for_success_message()
        
        # 验证用户在列表中
        assert self.user_management_page.verify_user_in_list(username)
        
        # 验证用户信息正确
        user_index = self.user_management_page.find_user_index_by_username(username)
        if user_index >= 0:
            user_info = self.user_management_page.get_user_info(user_index)
            assert role.lower() in user_info["role"].lower() or (role == "admin" and "管理员" in user_info["role"])
            
    def test_user_management_performance(self, page: Page):
        """测试用户管理操作性能"""
        self.login_as_admin(page)
        
        start_time = time.time()
        
        # 执行一系列用户管理操作
        self.user_management_page.navigate()
        
        # 创建用户
        timestamp = int(time.time())
        self.user_management_page.create_user(
            f"性能测试用户{timestamp}",
            f"perftest{timestamp}",
            f"perf{timestamp}@example.com",
            "perf123",
            "user",
            "active"
        )
        self.user_management_page.wait_for_success_message()
        
        # 搜索用户
        self.user_management_page.search_users(f"perftest{timestamp}")
        time.sleep(1)
        
        # 编辑用户
        user_index = self.user_management_page.find_user_index_by_username(f"perftest{timestamp}")
        if user_index >= 0:
            self.user_management_page.edit_user(user_index, name=f"编辑后性能测试{timestamp}")
            self.user_management_page.wait_for_success_message()
        
        end_time = time.time()
        operation_duration = end_time - start_time
        
        # 验证操作在合理时间内完成（小于15秒）
        assert operation_duration < 15.0, f"用户管理操作耗时过长: {operation_duration}秒"
        
    def test_user_management_responsive_design(self, page: Page):
        """测试用户管理页面响应式设计"""
        self.login_as_admin(page)
        self.user_management_page.navigate()
        
        # 测试不同屏幕尺寸
        screen_sizes = [
            (1920, 1080),  # 桌面
            (1024, 768),   # 平板横屏
            (768, 1024),   # 平板竖屏
            (375, 667)     # 手机
        ]
        
        for width, height in screen_sizes:
            page.set_viewport_size({"width": width, "height": height})
            
            # 验证关键元素仍然可见
            expect(page.locator(self.user_management_page.page_header)).to_be_visible()
            expect(page.locator(self.user_management_page.add_user_button)).to_be_visible()
            expect(page.locator(self.user_management_page.users_container)).to_be_visible()
            
        # 恢复默认视口
        page.set_viewport_size({"width": 1280, "height": 720})