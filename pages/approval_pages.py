from playwright.sync_api import Page, expect
from .base_page import BasePage
from typing import List, Dict


class ApprovalCreatePage(BasePage):
    """审批申请创建页面对象类"""
    
    @property
    def url(self) -> str:
        """页面URL"""
        return "http://localhost:8080/pages/approval-create.html"
    
    @property
    def title(self) -> str:
        """页面标题"""
        return "创建审批申请 - 审批系统"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 表单元素
        self.approval_form = "#approvalForm"
        self.title_input = "#title"
        self.type_select = "#type"
        self.priority_selector = ".priority-selector"
        self.description_textarea = "#description"
        self.submit_button = "button[type='submit']"
        self.cancel_button = "button[type='button']"
        
        # 消息提示
        self.success_message = ".success-message"
        self.error_message = ".error-message"
        
        # 页面导航
        self.breadcrumb = ".breadcrumb"
        self.back_to_dashboard = "a[href='dashboard.html']"
        
    def navigate(self):
        """导航到创建审批页面"""
        self.page.goto(self.url)
        self.wait_for_page_load()
        
    def wait_for_page_load(self):
        """等待页面加载完成"""
        self.wait_for_element(self.approval_form)
        self.wait_for_element(self.title_input)
        
    def fill_title(self, title: str):
        """填写申请标题"""
        self.fill_input(self.title_input, title)
        
    def select_type(self, type_value: str):
        """选择申请类型"""
        self.select_option(self.type_select, type_value)
        
    def select_priority(self, priority: str):
        """选择优先级"""
        priority_button = f"{self.priority_selector} button[data-priority='{priority}']"
        self.click_element(priority_button)
        
    def fill_description(self, description: str):
        """填写申请描述"""
        self.fill_input(self.description_textarea, description)
        
    def click_submit(self):
        """点击提交按钮"""
        self.click_element(self.submit_button)
        
    def click_cancel(self):
        """点击取消按钮"""
        self.click_element(self.cancel_button)
        
    def create_approval(self, title: str, type_value: str, priority: str, description: str):
        """创建审批申请"""
        self.fill_title(title)
        self.select_type(type_value)
        self.select_priority(priority)
        self.fill_description(description)
        self.click_submit()
        
    def get_success_message(self) -> str:
        """获取成功消息"""
        return self.get_text(self.success_message)
        
    def get_error_message(self) -> str:
        """获取错误消息"""
        return self.get_text(self.error_message)
        
    def wait_for_success_message(self, timeout: int = 5000):
        """等待成功消息显示"""
        self.wait_for_element(self.success_message, timeout=timeout)
        
    def wait_for_error_message(self, timeout: int = 3000):
        """等待错误消息显示"""
        self.wait_for_element(self.error_message, timeout=timeout)
        
    def verify_form_elements(self):
        """验证表单元素"""
        expect(self.page.locator(self.approval_form)).to_be_visible()
        expect(self.page.locator(self.title_input)).to_be_visible()
        expect(self.page.locator(self.type_select)).to_be_visible()
        expect(self.page.locator(self.priority_selector)).to_be_visible()
        expect(self.page.locator(self.description_textarea)).to_be_visible()
        expect(self.page.locator(self.submit_button)).to_be_visible()
        expect(self.page.locator(self.cancel_button)).to_be_visible()


class ApprovalListPage(BasePage):
    """审批列表页面对象类"""
    
    @property
    def url(self) -> str:
        """页面URL"""
        return "http://localhost:8080/pages/approval-list.html"
    
    @property
    def title(self) -> str:
        """页面标题"""
        return "审批列表 - 审批系统"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 筛选器
        self.status_filter = "#statusFilter"
        self.type_filter = "#typeFilter"
        self.priority_filter = "#priorityFilter"
        self.search_input = "#searchInput"
        self.refresh_button = "#refreshBtn"
        
        # 审批列表
        self.approvals_container = ".approvals-container"
        self.approval_items = ".approval-item"
        self.approval_title = ".approval-title"
        self.approval_status = ".approval-status"
        self.approval_type = ".approval-type"
        self.approval_priority = ".approval-priority"
        self.approval_submitter = ".approval-submitter"
        self.approval_date = ".approval-date"
        
        # 操作按钮
        self.view_button = ".btn-view"
        self.approve_button = ".btn-approve"
        self.reject_button = ".btn-reject"
        
        # 分页
        self.pagination = ".pagination"
        self.page_info = ".page-info"
        
        # 空状态
        self.empty_state = ".empty-state"
        
    def navigate(self):
        """导航到审批列表页面"""
        self.page.goto(self.url)
        self.wait_for_page_load()
        
    def wait_for_page_load(self):
        """等待页面加载完成"""
        self.wait_for_element(self.approvals_container)
        
    def filter_by_status(self, status: str):
        """按状态筛选"""
        self.select_option(self.status_filter, status)
        
    def filter_by_type(self, type_value: str):
        """按类型筛选"""
        self.select_option(self.type_filter, type_value)
        
    def filter_by_priority(self, priority: str):
        """按优先级筛选"""
        self.select_option(self.priority_filter, priority)
        
    def search_approvals(self, search_term: str):
        """搜索审批"""
        self.fill_input(self.search_input, search_term)
        
    def click_refresh(self):
        """点击刷新按钮"""
        self.click_element(self.refresh_button)
        
    def get_approval_count(self) -> int:
        """获取审批数量"""
        return self.page.locator(self.approval_items).count()
        
    def get_approval_titles(self) -> List[str]:
        """获取审批标题列表"""
        items = self.page.locator(self.approval_items)
        titles = []
        for i in range(items.count()):
            title = items.nth(i).locator(self.approval_title).text_content()
            titles.append(title)
        return titles
        
    def click_view_approval(self, index: int = 0):
        """点击查看审批"""
        items = self.page.locator(self.approval_items)
        if index < items.count():
            view_button = items.nth(index).locator(self.view_button)
            view_button.click()
        else:
            raise IndexError(f"审批索引 {index} 超出范围")
            
    def click_approve_approval(self, index: int = 0):
        """点击批准审批"""
        items = self.page.locator(self.approval_items)
        if index < items.count():
            approve_button = items.nth(index).locator(self.approve_button)
            approve_button.click()
        
    def click_reject_approval(self, index: int = 0):
        """点击拒绝审批"""
        items = self.page.locator(self.approval_items)
        if index < items.count():
            reject_button = items.nth(index).locator(self.reject_button)
            reject_button.click()
        
    def get_approval_info(self, index: int = 0) -> Dict[str, str]:
        """获取审批信息"""
        items = self.page.locator(self.approval_items)
        if index >= items.count():
            return {}
            
        item = items.nth(index)
        return {
            "title": item.locator(self.approval_title).text_content(),
            "status": item.locator(self.approval_status).text_content(),
            "type": item.locator(self.approval_type).text_content(),
            "priority": item.locator(self.approval_priority).text_content(),
            "submitter": item.locator(self.approval_submitter).text_content(),
            "date": item.locator(self.approval_date).text_content()
        }
        
    def is_empty_state_visible(self) -> bool:
        """检查空状态是否可见"""
        return self.is_element_visible(self.empty_state)
        
    def wait_for_approval_update(self, timeout: int = 5000):
        """等待审批更新"""
        self.page.wait_for_timeout(1000)  # 等待DOM更新
        
    def verify_list_elements(self):
        """验证列表元素"""
        expect(self.page.locator(self.status_filter)).to_be_visible()
        expect(self.page.locator(self.type_filter)).to_be_visible()
        expect(self.page.locator(self.priority_filter)).to_be_visible()
        expect(self.page.locator(self.search_input)).to_be_visible()
        expect(self.page.locator(self.refresh_button)).to_be_visible()
        expect(self.page.locator(self.approvals_container)).to_be_visible()


class ApprovalDetailPage(BasePage):
    """审批详情页面对象类"""
    
    @property
    def url(self) -> str:
        """页面URL"""
        return "http://localhost:8080/pages/approval-detail.html"
    
    @property
    def title(self) -> str:
        """页面标题"""
        return "审批详情 - 审批系统"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 审批信息
        self.approval_title = ".approval-title"
        self.approval_status = ".approval-status"
        self.approval_type = ".approval-type"
        self.approval_priority = ".approval-priority"
        self.approval_description = ".approval-description"
        self.submitter_info = ".submitter-info"
        self.submit_time = ".submit-time"
        
        # 审批操作
        self.comment_textarea = "#comment"
        self.approve_button = "#approveBtn"
        self.reject_button = "#rejectBtn"
        self.back_button = "#backBtn"
        
        # 审批历史
        self.history_section = ".approval-history"
        self.history_items = ".history-item"
        self.history_action = ".history-action"
        self.history_comment = ".history-comment"
        self.history_time = ".history-time"
        self.history_user = ".history-user"
        
    def navigate_with_id(self, approval_id: str):
        """导航到指定ID的审批详情页面"""
        url = f"{self.url}?id={approval_id}"
        self.page.goto(url)
        self.wait_for_page_load()
        
    def wait_for_page_load(self):
        """等待页面加载完成"""
        self.wait_for_element(self.approval_title)
        self.wait_for_element(self.approval_description)
        
    def get_approval_title(self) -> str:
        """获取审批标题"""
        return self.get_text(self.approval_title)
        
    def get_approval_status(self) -> str:
        """获取审批状态"""
        return self.get_text(self.approval_status)
        
    def get_approval_description(self) -> str:
        """获取审批描述"""
        return self.get_text(self.approval_description)
        
    def get_submitter_info(self) -> str:
        """获取提交者信息"""
        return self.get_text(self.submitter_info)
        
    def get_submit_time(self) -> str:
        """获取提交时间"""
        return self.get_text(self.submit_time)
        
    def fill_comment(self, comment: str):
        """填写审批意见"""
        self.fill_input(self.comment_textarea, comment)
        
    def click_approve(self):
        """点击批准按钮"""
        self.click_element(self.approve_button)
        
    def click_reject(self):
        """点击拒绝按钮"""
        self.click_element(self.reject_button)
        
    def approve_with_comment(self, comment: str = ""):
        """批准审批并添加意见"""
        if comment:
            self.fill_comment(comment)
        self.click_approve()
        
    def reject_with_comment(self, comment: str = ""):
        """拒绝审批并添加意见"""
        if comment:
            self.fill_comment(comment)
        self.click_reject()
        
    def click_back(self):
        """点击返回按钮"""
        self.click_element(self.back_button)
        
    def get_history_count(self) -> int:
        """获取历史记录数量"""
        return self.page.locator(self.history_items).count()
        
    def get_history_items(self) -> List[Dict[str, str]]:
        """获取历史记录列表"""
        items = self.page.locator(self.history_items)
        history = []
        for i in range(items.count()):
            item = items.nth(i)
            history.append({
                "action": item.locator(self.history_action).text_content(),
                "comment": item.locator(self.history_comment).text_content(),
                "time": item.locator(self.history_time).text_content(),
                "user": item.locator(self.history_user).text_content()
            })
        return history
        
    def is_approval_actions_visible(self) -> bool:
        """检查审批操作按钮是否可见"""
        return (self.is_element_visible(self.approve_button) and 
                self.is_element_visible(self.reject_button))
        
    def wait_for_approval_processed(self, timeout: int = 5000):
        """等待审批处理完成"""
        self.page.wait_for_timeout(2000)  # 等待状态更新
        
    def verify_detail_elements(self):
        """验证详情页面元素"""
        expect(self.page.locator(self.approval_title)).to_be_visible()
        expect(self.page.locator(self.approval_status)).to_be_visible()
        expect(self.page.locator(self.approval_description)).to_be_visible()
        expect(self.page.locator(self.submitter_info)).to_be_visible()
        expect(self.page.locator(self.submit_time)).to_be_visible()
        expect(self.page.locator(self.back_button)).to_be_visible()