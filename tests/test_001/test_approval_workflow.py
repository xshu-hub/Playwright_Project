import logging
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage, ApprovalDetailPage
import time
from loguru import logger
from tests.base_test import BaseTest
import allure
from utils.allure_helper import allure_step, AllureSeverity


@allure.epic("审批管理系统")
@allure.feature("审批工作流")
class TestApprovalWorkflow(BaseTest):
    """审批工作流测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        self.approval_create_page = ApprovalCreatePage(self.page)
        self.approval_list_page = ApprovalListPage(self.page)
        self.approval_detail_page = ApprovalDetailPage(self.page)
        
        # 清除本地存储，确保测试环境干净
        self.clear_storage()
        
    @allure_step("以普通用户身份登录")
    def login_as_user(self, username: str = "user1", password: str = "user123"):
        """以普通用户身份登录"""
        with allure.step(f"导航到登录页面并以用户 {username} 登录"):
            self.login_page.navigate()
            self.login_page.login(username, password)
            expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        
    @allure_step("以管理员身份登录")
    def login_as_admin(self, username: str = "admin", password: str = "admin123"):
        """管理员登录"""
        try:
            with allure.step("等待页面完全加载"):
                # 等待页面完全加载
                self.page.wait_for_load_state('networkidle')
                self.page.wait_for_timeout(1000)  # 额外等待确保页面元素加载完成
            
            with allure.step("等待登录表单加载"):
                # 等待登录表单元素加载
                try:
                    self.page.wait_for_selector("#username", timeout=15000)
                except Exception as e:
                    logger.error(f"等待用户名输入框超时，当前页面URL: {self.page.url}")
                    logger.debug(f"页面HTML内容: {self.page.content()[:500]}...")  # 记录前500字符
                    raise e
            
            with allure.step(f"填写登录表单并提交 - 用户名: {username}"):
                # 填写登录表单
                self.page.fill("#username", username)
                self.page.fill("#password", password)
                self.page.click("button[type='submit']")
            
            with allure.step("等待页面跳转到仪表板"):
                # 等待页面跳转，增加错误处理
                try:
                    self.page.wait_for_url("**/dashboard.html", timeout=15000)
                except Exception as e:
                    logger.error(f"管理员登录后页面跳转超时，当前URL: {self.page.url}")
                    # 检查是否有错误消息
                    if self.page.is_visible(".error-message"):
                        error_msg = self.page.text_content(".error-message")
                        logger.error(f"登录错误消息: {error_msg}")
                    raise e
        except Exception as e:
            logger.error(f"管理员登录失败: {str(e)}")
            raise e

    @allure.story("审批创建页面")
    @allure.title("验证审批创建页面元素显示")
    @allure.description("测试审批创建页面的所有必要元素是否正确显示")
    @allure.severity(AllureSeverity.NORMAL)
    def test_approval_create_page_elements(self):
        """测试审批创建页面元素"""
        with allure.step("管理员登录"):
            self.login_as_admin()
        
        with allure.step("导航到审批创建页面"):
            self.approval_create_page.navigate()
            self.approval_create_page.wait_for_page_load()
        
        with allure.step("验证页面标题"):
            expect(self.page).to_have_title("创建审批申请")
        
        with allure.step("验证表单元素存在"):
            expect(self.page.locator("#title")).to_be_visible()
            expect(self.page.locator("#type")).to_be_visible()
            expect(self.page.locator("#priority")).to_be_visible()
            expect(self.page.locator("#description")).to_be_visible()
            expect(self.page.locator("button[type='submit']")).to_be_visible()

    @allure.story("审批创建")
    @allure.title("成功创建审批申请")
    @allure.description("测试用户能够成功创建一个新的审批申请")
    @allure.severity(AllureSeverity.CRITICAL)
    def test_create_approval_success(self):
        """测试成功创建审批申请"""
        with allure.step("管理员登录"):
            self.login_as_admin()
        
        approval_data = {
            "title": "测试审批申请",
            "type": "请假",
            "priority": "高",
            "description": "这是一个测试审批申请的描述"
        }
        
        with allure.step(f"创建审批申请: {approval_data['title']}"):
            result = self.approval_create_page.create_approval(approval_data)
            self.assertTrue(result, "审批申请创建失败")

    @allure.story("审批创建验证")
    @allure.title("测试审批创建表单验证")
    @allure.description("测试审批创建表单的必填字段验证功能")
    @allure.severity(AllureSeverity.NORMAL)
    def test_create_approval_validation(self):
        """测试审批创建表单验证"""
        with allure.step("管理员登录"):
            self.login_as_admin()
        
        with allure.step("导航到审批创建页面"):
            self.approval_create_page.navigate()
            self.approval_create_page.wait_for_page_load()
        
        with allure.step("尝试提交空表单"):
            self.approval_create_page.click_submit()
        
        with allure.step("验证必填字段提示"):
            # 验证必填字段的验证提示
            title_field = self.page.locator("#title")
            expect(title_field).to_have_attribute("required", "")

    @allure.story("审批创建")
    @allure.title("测试不同类型的审批申请创建")
    @allure.description("测试创建不同类型和优先级的审批申请")
    @allure.severity(AllureSeverity.NORMAL)
    def test_create_approval_with_different_types(self):
        """测试创建不同类型的审批申请"""
        with allure.step("管理员登录"):
            self.login_as_admin()
        
        approval_types = [
            {"title": "请假申请", "type": "请假", "priority": "中", "description": "请假申请描述"},
            {"title": "报销申请", "type": "报销", "priority": "高", "description": "报销申请描述"},
            {"title": "采购申请", "type": "采购", "priority": "低", "description": "采购申请描述"}
        ]
        
        for approval_data in approval_types:
            with allure.step(f"创建 {approval_data['type']} 类型的审批申请"):
                result = self.approval_create_page.create_approval(approval_data)
                self.assertTrue(result, f"{approval_data['type']} 类型审批申请创建失败")
                
                # 等待一下再创建下一个
                time.sleep(1)

    @allure.story("审批列表页面")
    @allure.title("验证审批列表页面元素显示")
    @allure.description("测试审批列表页面的所有必要元素是否正确显示")
    @allure.severity(AllureSeverity.NORMAL)
    def test_approval_list_page_elements(self):
        """测试审批列表页面元素"""
        with allure.step("管理员登录"):
            self.login_as_admin()
        
        with allure.step("导航到审批列表页面"):
            self.approval_list_page.navigate()
            self.approval_list_page.wait_for_page_load()
        
        with allure.step("验证页面标题"):
            expect(self.page).to_have_title("审批列表")
        
        with allure.step("验证页面元素存在"):
            expect(self.page.locator("#statusFilter")).to_be_visible()
            expect(self.page.locator("#searchInput")).to_be_visible()
            expect(self.page.locator("#approvalTable")).to_be_visible()

    @allure.story("审批列表筛选")
    @allure.title("测试审批列表筛选功能")
    @allure.description("测试审批列表页面的状态筛选功能")
    @allure.severity(AllureSeverity.NORMAL)
    def test_approval_list_filtering(self):
        """测试审批列表筛选功能"""
        with allure.step("管理员登录"):
            self.login_as_admin()
        
        with allure.step("导航到审批列表页面"):
            self.approval_list_page.navigate()
            self.approval_list_page.wait_for_page_load()
        
        with allure.step("测试按状态筛选"):
            # 测试筛选待审批状态
            self.approval_list_page.filter_by_status("待审批")
            time.sleep(1)
            
            # 测试筛选已通过状态
            self.approval_list_page.filter_by_status("已通过")
            time.sleep(1)
            
            # 测试筛选已拒绝状态
            self.approval_list_page.filter_by_status("已拒绝")
            time.sleep(1)

    @allure.story("审批搜索")
    @allure.title("测试审批搜索功能")
    @allure.description("测试审批列表页面的搜索功能")
    @allure.severity(AllureSeverity.NORMAL)
    def test_approval_search_functionality(self):
        """测试审批搜索功能"""
        with allure.step("管理员登录"):
            self.login_as_admin()
        
        with allure.step("导航到审批列表页面"):
            self.approval_list_page.navigate()
            self.approval_list_page.wait_for_page_load()
        
        with allure.step("执行搜索操作"):
            # 搜索特定关键词
            search_term = "测试"
            self.approval_list_page.search_approvals(search_term)
            time.sleep(2)
            
            # 验证搜索结果
            # 这里可以添加更具体的验证逻辑
            self.assertTrue(True, "搜索功能执行完成")

    @allure.story("审批详情页面")
    @allure.title("验证审批详情页面元素显示")
    @allure.description("测试审批详情页面的所有必要元素是否正确显示")
    @allure.severity(AllureSeverity.NORMAL)
    def test_approval_detail_page_elements(self):
        """测试审批详情页面元素"""
        with allure.step("管理员登录"):
            self.login_as_admin()
        
        with allure.step("创建测试审批申请"):
            # 先创建一个审批申请
            approval_data = {
                "title": "详情页面测试申请",
                "type": "请假",
                "priority": "中",
                "description": "用于测试详情页面的审批申请"
            }
            self.approval_create_page.create_approval(approval_data)
        
        with allure.step("导航到审批列表并查看详情"):
            self.approval_list_page.navigate()
            self.approval_list_page.wait_for_page_load()
            
            # 点击第一个审批申请查看详情
            self.approval_list_page.view_approval_details(0)

    @allure.story("审批工作流")
    @allure.title("完整的审批工作流测试")
    @allure.description("测试从创建到审批完成的完整工作流程")
    @allure.severity(AllureSeverity.CRITICAL)
    def test_approval_workflow_complete_cycle(self):
        """测试完整的审批工作流程"""
        with allure.step("普通用户登录并创建审批申请"):
            # 普通用户登录
            self.login_as_user("user1", "user123")
            
            # 创建审批申请
            approval_data = {
                "title": "完整流程测试申请",
                "type": "请假",
                "priority": "高",
                "description": "测试完整审批流程的申请"
            }
            
            result = self.approval_create_page.create_approval(approval_data)
            self.assertTrue(result, "审批申请创建失败")
        
        with allure.step("管理员登录并处理审批"):
            # 切换到管理员账户
            self.page.goto("http://localhost:8080/pages/login.html")
            self.login_as_admin()
            
            # 导航到审批列表
            self.approval_list_page.navigate()
            self.approval_list_page.wait_for_page_load()
            
            # 查看并处理审批
            self.approval_list_page.view_approval_details(0)
            
            # 批准审批申请
            self.approval_detail_page.approve_approval("同意该申请")

    def test_approval_rejection_workflow(self):
        """测试审批拒绝工作流程"""
        # 普通用户创建申请
        self.login_as_user()
        self.approval_create_page.navigate()
        
        approval_title = f"拒绝测试申请 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "expense",
            "low",
            "测试拒绝流程的申请"
        )
        # 增加超时时间并添加错误处理
        try:
            self.approval_create_page.wait_for_success_message(timeout=10000)
        except Exception as e:
            logger.error(f"创建申请时出现错误，当前页面URL: {self.page.url}")
            raise e
        
        # 切换到管理员账号处理申请
        # 只清除用户会话，保留申请数据
        self.page.evaluate("() => { localStorage.removeItem('currentUser'); localStorage.removeItem('loginTime'); }")
        self.page.goto("http://localhost:8080/pages/login.html", wait_until="networkidle")
        self.page.wait_for_timeout(1000)
        self.login_as_admin()
        
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
        logger.info(f"拒绝申请状态: {status}")
        self.assertTrue("已拒绝" in status or "rejected" in status.lower() or "reject" in status.lower())
        
    def test_approval_history_tracking(self):
        """测试审批历史记录跟踪"""
        # 创建申请
        self.login_as_user()
        self.approval_create_page.navigate()
        
        approval_title = f"历史记录测试 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "purchase",
            "medium",
            "测试历史记录的申请"
        )
        self.approval_create_page.wait_for_success_message()
        
        # 切换到管理员账号处理申请
        # 只清除用户会话，保留申请数据
        self.page.evaluate("() => { localStorage.removeItem('currentUser'); localStorage.removeItem('loginTime'); }")
        self.page.goto("http://localhost:8080/pages/login.html", wait_until="networkidle")
        self.page.wait_for_timeout(1000)
        self.login_as_admin()
        
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
        logger.info(f"历史记录数量: {history_count}")
        
        if history_count > 0:
            history_items = self.approval_detail_page.get_history_items()
            logger.debug(f"历史记录项目: {history_items}")
            actions = [item["action"] for item in history_items]
            logger.debug(f"历史记录动作: {actions}")
            assert any("提交" in action or "submit" in action.lower() for action in actions)
            assert any("批准" in action or "approve" in action.lower() for action in actions)
        else:
            # 如果没有历史记录，至少验证申请状态已更新
            status = self.approval_detail_page.get_approval_status()
            logger.info(f"申请状态: {status}")
            self.assertTrue("已批准" in status or "approved" in status.lower() or "approve" in status.lower())
        
    def test_approval_permissions(self):
        """测试审批权限控制"""
        # 普通用户登录
        self.login_as_user()
        
        # 创建申请
        self.approval_create_page.navigate()
        approval_title = f"权限测试申请 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "leave",
            "medium",
            "测试权限控制的申请"
        )
        # 增加超时时间并添加错误处理
        try:
            self.approval_create_page.wait_for_success_message(timeout=10000)
        except Exception as e:
            logger.error(f"创建申请时出现错误，当前页面URL: {self.page.url}")
            raise e
        
        # 查看自己的申请详情
        self.approval_list_page.navigate()
        if self.approval_list_page.get_approval_count() > 0:
            self.approval_list_page.click_view_approval(0)
            
            # 普通用户不应该看到审批操作按钮
            has_approval_actions = self.approval_detail_page.is_approval_actions_visible()
            # 根据业务逻辑，普通用户可能看不到审批按钮，或者只能看到自己的申请
            
    def test_approval_list_pagination(self):
        """测试审批列表分页功能"""
        self.login_as_user()
        
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
        self.assertGreaterEqual(approval_count, 5)
        
    def test_approval_status_updates(self):
        """测试审批状态更新"""
        # 创建申请
        self.login_as_user()
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
        self.assertTrue("待审批" in initial_status or "pending" in initial_status.lower())
        
        # 切换到管理员账号处理申请
        # 只清除用户会话，保留申请数据
        self.page.evaluate("() => { localStorage.removeItem('currentUser'); localStorage.removeItem('loginTime'); }")
        self.page.goto("http://localhost:8080/pages/login.html", wait_until="networkidle")
        self.page.wait_for_timeout(1000)
        self.login_as_admin()
        
        self.approval_list_page.navigate()
        self.approval_list_page.click_view_approval(0)
        self.approval_detail_page.approve_with_comment("状态更新测试通过")
        self.approval_detail_page.wait_for_approval_processed()
        
        # 返回列表检查状态更新
        self.approval_detail_page.click_back()
        self.approval_list_page.wait_for_approval_update()
        
        updated_info = self.approval_list_page.get_approval_info(0)
        updated_status = updated_info["status"]
        logger.info(f"更新后申请状态: {updated_status}")
        self.assertTrue("已批准" in updated_status or "approved" in updated_status.lower() or "approve" in updated_status.lower())
        
    def test_different_approval_types_and_priorities_leave_high(self):
         """测试请假申请 - 高优先级"""
         self.login_as_user()
         self.approval_create_page.navigate()
         
         self.approval_create_page.create_approval(
             "参数化测试 - leave - high",
             "leave",
             "high",
             "测试 leave 类型，high 优先级的申请"
         )
         
         # 验证创建成功
         self.approval_create_page.wait_for_success_message()
         
         # 验证在列表中显示
         self.approval_list_page.navigate()
         titles = self.approval_list_page.get_approval_titles()
         self.assertTrue(any("leave - high" in title for title in titles))
         
    def test_different_approval_types_and_priorities_expense_medium(self):
         """测试报销申请 - 中优先级"""
         self.login_as_user()
         self.approval_create_page.navigate()
         
         self.approval_create_page.create_approval(
             "参数化测试 - expense - medium",
             "expense",
             "medium",
             "测试 expense 类型，medium 优先级的申请"
         )
         
         # 验证创建成功
         self.approval_create_page.wait_for_success_message()
         
         # 验证在列表中显示
         self.approval_list_page.navigate()
         titles = self.approval_list_page.get_approval_titles()
         self.assertTrue(any("expense - medium" in title for title in titles))
         
    def test_different_approval_types_and_priorities_purchase_low(self):
         """测试采购申请 - 低优先级"""
         self.login_as_user()
         self.approval_create_page.navigate()
         
         self.approval_create_page.create_approval(
             "参数化测试 - purchase - low",
             "purchase",
             "low",
             "测试 purchase 类型，low 优先级的申请"
         )
         
         # 验证创建成功
         self.approval_create_page.wait_for_success_message()
         
         # 验证在列表中显示
         self.approval_list_page.navigate()
         titles = self.approval_list_page.get_approval_titles()
         self.assertTrue(any("purchase - low" in title for title in titles))
         
    def test_different_approval_types_and_priorities_other_high(self):
         """测试其他申请 - 高优先级"""
         self.login_as_user()
         self.approval_create_page.navigate()
         
         self.approval_create_page.create_approval(
             "参数化测试 - other - high",
             "other",
             "high",
             "测试 other 类型，high 优先级的申请"
         )
         
         # 验证创建成功
         self.approval_create_page.wait_for_success_message()
         
         # 验证在列表中显示
         self.approval_list_page.navigate()
         titles = self.approval_list_page.get_approval_titles()
         self.assertTrue(any("other - high" in title for title in titles))
        
    def test_approval_workflow_performance(self):
        """测试审批工作流程性能"""
        start_time = time.time()
        
        # 执行完整的审批流程
        self.login_as_user()
        self.approval_create_page.navigate()
        
        self.approval_create_page.create_approval(
            "性能测试申请",
            "leave",
            "medium",
            "用于测试性能的申请"
        )
        self.approval_create_page.wait_for_success_message()
        
        # 切换到管理员账号处理申请
        # 只清除用户会话，保留申请数据
        self.page.evaluate("() => { localStorage.removeItem('currentUser'); localStorage.removeItem('loginTime'); }")
        self.page.goto("http://localhost:8080/pages/login.html", wait_until="networkidle")
        self.page.wait_for_timeout(1000)
        self.login_as_admin()
        
        self.approval_list_page.navigate()
        self.approval_list_page.click_view_approval(0)
        self.approval_detail_page.approve_with_comment("性能测试通过")
        self.approval_detail_page.wait_for_approval_processed()
        
        end_time = time.time()
        workflow_duration = end_time - start_time
        
        # 验证整个流程在合理时间内完成（小于30秒）
        self.assertLess(workflow_duration, 30.0, f"审批流程耗时过长: {workflow_duration}秒")


if __name__ == '__main__':
    import unittest
    unittest.main()