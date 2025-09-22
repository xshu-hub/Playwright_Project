from playwright.sync_api import Page, expect
from .base_page import BasePage


class DashboardPage(BasePage):
    """仪表板页面对象类"""
    
    @property
    def url(self) -> str:
        """页面URL"""
        return "http://localhost:8080/pages/dashboard.html"
    
    @property
    def title(self) -> str:
        """页面标题"""
        return "仪表板 - 审批系统"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 页面头部元素
        self.page_header = ".dashboard-header"
        self.user_info = ".user-info"
        self.user_avatar = ".user-avatar"
        self.user_name = ".user-name"
        self.user_role = ".user-role"
        self.logout_button = "button.btn.btn-secondary"
        
        # 统计卡片
        self.stats_container = ".stats-grid"
        self.pending_approvals_card = ".stat-card:has-text('待处理审批')"
        self.submitted_approvals_card = ".stat-card:has-text('我的申请')"
        self.total_users_card = ".stat-card:has-text('系统用户')"
        self.stat_numbers = ".stat-number"
        
        # 快速操作区域
        self.quick_actions = ".quick-actions"
        self.create_approval_btn = "#createApprovalBtn"
        self.approval_list_btn = "#approvalListBtn"
        self.user_management_btn = "#userManagementBtn"
        
        # 最近活动区域
        self.recent_activities = ".recent-activities"
        self.activities_list = ".activities-list"
        self.activity_item = ".activity-item"
        self.activity_title = ".activity-title"
        self.activity_time = ".activity-time"
        self.activity_status = ".activity-status"
        
        # 待处理事项区域
        self.pending_items = ".pending-items"
        self.pending_list = ".pending-list"
        self.pending_item = ".pending-item"
        self.pending_title = ".pending-title"
        self.pending_priority = ".pending-priority"
        self.pending_date = ".pending-date"
        
        # 空状态
        self.empty_state = ".empty-state"
        self.empty_message = ".empty-message"
        
    def navigate(self):
        """导航到仪表板页面"""
        super().navigate(self.url)
        self.wait_for_page_load()
        
    def wait_for_page_load(self):
        """等待仪表板页面加载完成"""
        self.wait_for_element(self.page_header, timeout=self.long_timeout)
        self.wait_for_element(self.user_info, timeout=self.long_timeout)
        
    def get_user_name(self) -> str:
        """获取当前用户姓名"""
        return self.get_text(self.user_name)
        
    def get_user_role(self) -> str:
        """获取用户角色"""
        return self.get_text(self.user_role)
        
    def get_user_info(self) -> dict:
        """获取用户信息"""
        return {
            "name": self.get_user_name(),
            "role": self.get_user_role()
        }
        
    def click_logout(self):
        """点击退出登录按钮"""
        self.click(self.logout_button)
        
    def logout(self):
        """执行退出登录操作"""
        self.click_logout()
        self.wait_for_logout_redirect()
        
    def wait_for_logout_redirect(self, timeout: int = 10000):
        """等待退出登录重定向"""
        # 等待页面跳转到登录页面
        self.page.wait_for_url("**/login.html", timeout=timeout)
        
    # 统计数据相关方法
    def get_pending_approvals_count(self) -> str:
        """获取待处理审批数量"""
        card = self.page.locator(self.pending_approvals_card)
        return card.locator(self.stat_numbers).text_content()
        
    def get_submitted_approvals_count(self) -> str:
        """获取已提交审批数量"""
        card = self.page.locator(self.submitted_approvals_card)
        return card.locator(self.stat_numbers).text_content()
        
    def get_total_users_count(self) -> str:
        """获取系统用户总数"""
        card = self.page.locator(self.total_users_card)
        return card.locator(self.stat_numbers).text_content()
        
    def click_create_approval(self):
        """点击创建审批按钮"""
        self.click_element(self.create_approval_btn)
        
    def click_approval_list(self):
        """点击审批列表按钮"""
        self.click_element(self.approval_list_btn)
        
    def click_user_management(self):
        """点击用户管理按钮"""
        self.click_element(self.user_management_btn)
        
    def wait_for_navigation_to_create_approval(self, timeout: int = 5000):
        """等待导航到创建审批页面"""
        self.page.wait_for_url("**/create-approval.html", timeout=timeout)
        
    def wait_for_navigation_to_approval_list(self, timeout: int = 5000):
        """等待导航到审批列表页面"""
        self.page.wait_for_url("**/approval-list.html", timeout=timeout)
        
    def wait_for_navigation_to_user_management(self, timeout: int = 5000):
        """等待导航到用户管理页面"""
        self.page.wait_for_url("**/user-management.html", timeout=timeout)
        
    def get_recent_activities_count(self) -> int:
        """获取最近活动数量"""
        activities = self.page.locator(self.activity_item)
        return activities.count()
        
    def get_recent_activity_titles(self) -> list[str]:
        """获取最近活动标题列表"""
        activities = self.page.locator(self.activity_item)
        titles = []
        for i in range(activities.count()):
            title_element = activities.nth(i).locator(self.activity_title)
            titles.append(title_element.text_content())
        return titles
        
    def get_pending_items_count(self) -> int:
        """获取待处理事项数量"""
        items = self.page.locator(self.pending_item)
        return items.count()
        
    def get_pending_item_titles(self) -> list[str]:
        """获取待处理事项标题列表"""
        items = self.page.locator(self.pending_item)
        titles = []
        for i in range(items.count()):
            title_element = items.nth(i).locator(self.pending_title)
            titles.append(title_element.text_content())
        return titles
        
    def click_pending_item(self, index: int = 0):
        """点击待处理事项"""
        items = self.page.locator(self.pending_item)
        if index < items.count():
            items.nth(index).click()
        else:
            raise IndexError(f"待处理事项索引 {index} 超出范围")
            
    def click_activity_item(self, index: int = 0):
        """点击活动项"""
        activities = self.page.locator(self.activity_item)
        if index < activities.count():
            activities.nth(index).click()
        else:
            raise IndexError(f"活动项索引 {index} 超出范围")
            
    def is_user_management_button_visible(self) -> bool:
        """检查用户管理按钮是否可见（管理员权限）"""
        return self.is_element_visible(self.user_management_btn)
        
    def is_empty_state_visible(self) -> bool:
        """检查是否显示空状态"""
        return self.is_element_visible(self.empty_state)
        
    def get_empty_message(self) -> str:
        """获取空状态消息"""
        return self.get_text(self.empty_message)
        
    def verify_dashboard_elements(self):
        """验证仪表板页面元素"""
        # 验证页面头部
        expect(self.page.locator(self.page_header)).to_be_visible()
        expect(self.page.locator(self.user_info)).to_be_visible()
        expect(self.page.locator(self.user_name)).to_be_visible()
        expect(self.page.locator(self.user_role)).to_be_visible()
        expect(self.page.locator(self.logout_button)).to_be_visible()
        
        # 验证统计卡片
        expect(self.page.locator(self.stats_container)).to_be_visible()
        
        # 验证快速操作区域
        expect(self.page.locator(self.quick_actions)).to_be_visible()
        expect(self.page.locator(self.create_approval_btn)).to_be_visible()
        expect(self.page.locator(self.approval_list_btn)).to_be_visible()
        
        # 验证最近活动区域
        expect(self.page.locator(self.recent_activities)).to_be_visible()
        
    def verify_admin_elements(self):
        """验证管理员特有元素"""
        expect(self.page.locator(self.user_management_btn)).to_be_visible()
        expect(self.page.locator(self.total_users_card)).to_be_visible()
        
    def verify_user_elements(self):
        """验证普通用户元素"""
        expect(self.page.locator(self.pending_approvals_card)).to_be_visible()
        expect(self.page.locator(self.submitted_approvals_card)).to_be_visible()
        
    def refresh_page(self):
        """刷新页面"""
        self.page.reload()
        self.wait_for_page_load()
        
    def verify_responsive_design(self):
        """验证响应式设计"""
        # 移动端视口
        self.page.set_viewport_size({"width": 375, "height": 667})
        
        # 验证关键元素在移动端仍然可见
        expect(self.page.locator(self.page_header)).to_be_visible()
        expect(self.page.locator(self.user_info)).to_be_visible()
        expect(self.page.locator(self.quick_actions)).to_be_visible()
        
        # 恢复桌面视口
        self.page.set_viewport_size({"width": 1280, "height": 720})
        
    def wait_for_data_load(self, timeout: int = 10000):
        """等待数据加载完成"""
        # 等待统计数据加载
        self.page.wait_for_function(
            "() => document.querySelectorAll('.stat-number').length > 0 && "
            "Array.from(document.querySelectorAll('.stat-number')).every(el => el.textContent.trim() !== '')",
            timeout=timeout
        )