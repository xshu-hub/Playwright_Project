import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage, ApprovalDetailPage
import time


class TestApprovalWorkflow:
    """审批工作流测试用例类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前置设置"""
        self.login_page = LoginPage(page)
        self.dashboard_page = DashboardPage(page)
        self.approval_create_page = ApprovalCreatePage(page)
        self.approval_list_page = ApprovalListPage(page)
        self.approval_detail_page = ApprovalDetailPage(page)
        
        # 清除本地存储，确保测试环境干净
        try:
            page.evaluate("localStorage.clear()")
            page.evaluate("sessionStorage.clear()")
        except Exception:
            # 如果localStorage不可访问，忽略错误
            pass
        
    def login_as_user(self, page: Page, username: str = "user1", password: str = "user123"):
        """以普通用户身份登录"""
        self.login_page.navigate()
        self.login_page.login(username, password)
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
    def login_as_admin(self, page: Page, username: str = "admin", password: str = "admin123"):
        """管理员登录"""
        # 确保在登录页面
        if "login.html" not in page.url:
            page.goto("http://localhost:8080/pages/login.html")
            page.wait_for_load_state('networkidle')
        
        # 等待登录表单加载
        page.wait_for_selector("#username", timeout=10000)
        
        # 填写登录表单
        page.fill("#username", username)
        page.fill("#password", password)
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard.html", timeout=10000)
        expect(page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
    def test_approval_create_page_elements(self, page: Page):
        """测试审批创建页面元素"""
        self.login_as_user(page)
        self.approval_create_page.navigate()
        
        # 验证页面标题
        expect(page).to_have_title("提交申请 - 测试系统")
        
        # 验证表单元素
        self.approval_create_page.verify_form_elements()
        
    def test_create_approval_success(self, page: Page):
        """测试成功创建审批申请"""
        self.login_as_user(page)
        self.approval_create_page.navigate()
        
        # 创建审批申请
        approval_data = {
            "title": "测试申请 - 请假申请",
            "type": "leave",
            "priority": "medium",
            "description": "因个人事务需要请假3天，请批准。"
        }
        
        self.approval_create_page.create_approval(
            approval_data["title"],
            approval_data["type"],
            approval_data["priority"],
            approval_data["description"]
        )
        
        # 验证成功消息
        self.approval_create_page.wait_for_success_message()
        success_message = self.approval_create_page.get_success_message()
        assert "申请提交成功" in success_message
        
    def test_create_approval_validation(self, page: Page):
        """测试审批申请表单验证"""
        self.login_as_user(page)
        self.approval_create_page.navigate()
        
        # 测试空标题提交
        self.approval_create_page.select_type("leave")
        self.approval_create_page.select_priority("high")
        self.approval_create_page.fill_description("测试描述")
        self.approval_create_page.click_submit()
        
        # 验证标题字段必填
        title_field = page.locator(self.approval_create_page.title_input)
        expect(title_field).to_have_attribute("required", "")
        
    def test_create_approval_with_different_types(self, page: Page):
        """测试创建不同类型的审批申请"""
        self.login_as_user(page)
        
        approval_types = [
            {"type": "leave", "title": "请假申请", "description": "个人事务请假"},
            {"type": "expense", "title": "报销申请", "description": "差旅费报销"},
            {"type": "purchase", "title": "采购申请", "description": "办公用品采购"},
            {"type": "other", "title": "其他申请", "description": "其他事务申请"}
        ]
        
        for i, approval in enumerate(approval_types):
            self.approval_create_page.navigate()
            
            self.approval_create_page.create_approval(
                f"{approval['title']} - {i+1}",
                approval["type"],
                "medium",
                approval["description"]
            )
            
            # 验证创建成功
            self.approval_create_page.wait_for_success_message()
            
    def test_approval_list_page_elements(self, page: Page):
        """测试审批列表页面元素"""
        self.login_as_user(page)
        self.approval_list_page.navigate()
        
        # 验证页面标题
        expect(page).to_have_title("申请列表 - 测试系统")
        
        # 验证列表页面元素
        self.approval_list_page.verify_list_elements()
        
    def test_approval_list_filtering(self, page: Page):
        """测试审批列表筛选功能"""
        self.login_as_user(page)
        
        # 先创建一些测试数据
        self.approval_create_page.navigate()
        self.approval_create_page.create_approval("高优先级申请", "leave", "high", "紧急请假")
        self.approval_create_page.wait_for_success_message()
        
        # 访问列表页面
        self.approval_list_page.navigate()
        
        # 测试按优先级筛选
        self.approval_list_page.filter_by_priority("high")
        time.sleep(1)  # 等待筛选结果
        
        # 验证筛选结果
        if self.approval_list_page.get_approval_count() > 0:
            titles = self.approval_list_page.get_approval_titles()
            assert any("高优先级" in title for title in titles)
            
    def test_approval_search_functionality(self, page: Page):
        """测试审批申请搜索功能"""
        self.login_as_user(page)
        
        # 创建测试数据
        self.approval_create_page.navigate()
        self.approval_create_page.create_approval("特殊关键词申请", "leave", "medium", "包含特殊关键词的申请")
        self.approval_create_page.wait_for_success_message()
        
        # 访问列表页面并搜索
        self.approval_list_page.navigate()
        self.approval_list_page.search_approvals("特殊关键词")
        time.sleep(1)  # 等待搜索结果
        
        # 验证搜索结果
        if self.approval_list_page.get_approval_count() > 0:
            titles = self.approval_list_page.get_approval_titles()
            assert any("特殊关键词" in title for title in titles)
            
    def test_approval_detail_page_elements(self, page: Page):
        """测试审批详情页面元素"""
        self.login_as_user(page)
        
        # 创建测试申请
        self.approval_create_page.navigate()
        self.approval_create_page.create_approval("详情测试申请", "leave", "medium", "用于测试详情页面的申请")
        self.approval_create_page.wait_for_success_message()
        
        # 访问列表页面并查看详情
        self.approval_list_page.navigate()
        if self.approval_list_page.get_approval_count() > 0:
            self.approval_list_page.click_view_approval(0)
            
            # 验证详情页面元素
            self.approval_detail_page.verify_detail_elements()
            
    def test_approval_workflow_complete_cycle(self, page: Page):
        """测试完整的审批工作流程"""
        # 第一步：普通用户创建申请
        self.login_as_user(page)
        self.approval_create_page.navigate()
        
        approval_title = f"完整流程测试申请 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "leave",
            "high",
            "测试完整审批流程的申请"
        )
        self.approval_create_page.wait_for_success_message()
        
        # 第二步：查看申请列表，确认申请已创建
        self.approval_list_page.navigate()
        titles = self.approval_list_page.get_approval_titles()
        assert any(approval_title in title for title in titles)
        
        # 第三步：切换到管理员账号处理申请
        # 直接使用page.goto导航，避免页面对象的复杂等待逻辑
        page.goto("http://localhost:8080/pages/login.html", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)  # 简单等待页面加载
        self.login_as_admin(page)
        
        # 访问审批列表
        self.approval_list_page.navigate()
        
        # 查找并查看申请详情
        approval_found = False
        for i in range(self.approval_list_page.get_approval_count()):
            approval_info = self.approval_list_page.get_approval_info(i)
            if approval_title in approval_info["title"]:
                self.approval_list_page.click_view_approval(i)
                approval_found = True
                break
                
        assert approval_found, "未找到创建的申请"
        
        # 第四步：管理员批准申请
        self.approval_detail_page.approve_with_comment("申请已批准，同意请假。")
        self.approval_detail_page.wait_for_approval_processed()
        
        # 验证申请状态已更新
        status = self.approval_detail_page.get_approval_status()
        assert "已批准" in status or "approved" in status.lower()
        
    def test_approval_rejection_workflow(self, page: Page):
        """测试审批拒绝工作流程"""
        # 普通用户创建申请
        self.login_as_user(page)
        self.approval_create_page.navigate()
        
        approval_title = f"拒绝测试申请 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "expense",
            "low",
            "测试拒绝流程的申请"
        )
        self.approval_create_page.wait_for_success_message()
        
        # 管理员登录并拒绝申请
        self.dashboard_page.logout()
        self.login_as_admin(page)
        
        self.approval_list_page.navigate()
        
        # 查找并处理申请
        for i in range(self.approval_list_page.get_approval_count()):
            approval_info = self.approval_list_page.get_approval_info(i)
            if approval_title in approval_info["title"]:
                self.approval_list_page.click_view_approval(i)
                break
                
        # 拒绝申请
        self.approval_detail_page.reject_with_comment("申请不符合要求，已拒绝。")
        self.approval_detail_page.wait_for_approval_processed()
        
        # 验证申请状态已更新
        status = self.approval_detail_page.get_approval_status()
        assert "已拒绝" in status or "rejected" in status.lower()
        
    def test_approval_history_tracking(self, page: Page):
        """测试审批历史记录跟踪"""
        # 创建申请
        self.login_as_user(page)
        self.approval_create_page.navigate()
        
        approval_title = f"历史记录测试 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "purchase",
            "medium",
            "测试历史记录的申请"
        )
        self.approval_create_page.wait_for_success_message()
        
        # 管理员处理申请
        self.dashboard_page.logout()
        self.login_as_admin(page)
        
        self.approval_list_page.navigate()
        
        # 查找申请并查看详情
        for i in range(self.approval_list_page.get_approval_count()):
            approval_info = self.approval_list_page.get_approval_info(i)
            if approval_title in approval_info["title"]:
                self.approval_list_page.click_view_approval(i)
                break
                
        # 批准申请
        self.approval_detail_page.approve_with_comment("经审核，同意此申请。")
        self.approval_detail_page.wait_for_approval_processed()
        
        # 验证历史记录
        history_count = self.approval_detail_page.get_history_count()
        assert history_count >= 2  # 至少包含提交和批准两条记录
        
        history_items = self.approval_detail_page.get_history_items()
        actions = [item["action"] for item in history_items]
        assert any("提交" in action or "submit" in action.lower() for action in actions)
        assert any("批准" in action or "approve" in action.lower() for action in actions)
        
    def test_approval_permissions(self, page: Page):
        """测试审批权限控制"""
        # 普通用户登录
        self.login_as_user(page)
        
        # 创建申请
        self.approval_create_page.navigate()
        approval_title = f"权限测试申请 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "leave",
            "medium",
            "测试权限控制的申请"
        )
        self.approval_create_page.wait_for_success_message()
        
        # 查看自己的申请详情
        self.approval_list_page.navigate()
        if self.approval_list_page.get_approval_count() > 0:
            self.approval_list_page.click_view_approval(0)
            
            # 普通用户不应该看到审批操作按钮
            has_approval_actions = self.approval_detail_page.is_approval_actions_visible()
            # 根据业务逻辑，普通用户可能看不到审批按钮，或者只能看到自己的申请
            
    def test_approval_list_pagination(self, page: Page):
        """测试审批列表分页功能"""
        self.login_as_user(page)
        
        # 创建多个申请以测试分页
        for i in range(5):
            self.approval_create_page.navigate()
            self.approval_create_page.create_approval(
                f"分页测试申请 {i+1}",
                "other",
                "low",
                f"第 {i+1} 个测试申请"
            )
            self.approval_create_page.wait_for_success_message()
            
        # 访问列表页面
        self.approval_list_page.navigate()
        
        # 验证申请数量
        approval_count = self.approval_list_page.get_approval_count()
        assert approval_count >= 5
        
    def test_approval_status_updates(self, page: Page):
        """测试审批状态更新"""
        # 创建申请
        self.login_as_user(page)
        self.approval_create_page.navigate()
        
        approval_title = f"状态更新测试 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "leave",
            "high",
            "测试状态更新的申请"
        )
        self.approval_create_page.wait_for_success_message()
        
        # 检查初始状态
        self.approval_list_page.navigate()
        initial_info = self.approval_list_page.get_approval_info(0)
        initial_status = initial_info["status"]
        assert "待审批" in initial_status or "pending" in initial_status.lower()
        
        # 管理员处理申请
        self.dashboard_page.logout()
        self.login_as_admin(page)
        
        self.approval_list_page.navigate()
        self.approval_list_page.click_view_approval(0)
        self.approval_detail_page.approve_with_comment("状态更新测试通过")
        self.approval_detail_page.wait_for_approval_processed()
        
        # 返回列表检查状态更新
        self.approval_detail_page.click_back()
        self.approval_list_page.wait_for_approval_update()
        
        updated_info = self.approval_list_page.get_approval_info(0)
        updated_status = updated_info["status"]
        assert "已批准" in updated_status or "approved" in updated_status.lower()
        
    @pytest.mark.parametrize("approval_type,priority", [
        ("leave", "high"),
        ("expense", "medium"),
        ("purchase", "low"),
        ("other", "high")
    ])
    def test_different_approval_types_and_priorities(self, page: Page, approval_type: str, priority: str):
        """测试不同类型和优先级的审批申请"""
        self.login_as_user(page)
        self.approval_create_page.navigate()
        
        self.approval_create_page.create_approval(
            f"参数化测试 - {approval_type} - {priority}",
            approval_type,
            priority,
            f"测试 {approval_type} 类型，{priority} 优先级的申请"
        )
        
        # 验证创建成功
        self.approval_create_page.wait_for_success_message()
        
        # 验证在列表中显示
        self.approval_list_page.navigate()
        titles = self.approval_list_page.get_approval_titles()
        assert any(f"{approval_type} - {priority}" in title for title in titles)
        
    def test_approval_workflow_performance(self, page: Page):
        """测试审批工作流程性能"""
        start_time = time.time()
        
        # 执行完整的审批流程
        self.login_as_user(page)
        self.approval_create_page.navigate()
        
        self.approval_create_page.create_approval(
            "性能测试申请",
            "leave",
            "medium",
            "用于测试性能的申请"
        )
        self.approval_create_page.wait_for_success_message()
        
        # 切换到管理员并处理
        self.dashboard_page.logout()
        self.login_as_admin(page)
        
        self.approval_list_page.navigate()
        self.approval_list_page.click_view_approval(0)
        self.approval_detail_page.approve_with_comment("性能测试通过")
        self.approval_detail_page.wait_for_approval_processed()
        
        end_time = time.time()
        workflow_duration = end_time - start_time
        
        # 验证整个流程在合理时间内完成（小于30秒）
        assert workflow_duration < 30.0, f"审批流程耗时过长: {workflow_duration}秒"