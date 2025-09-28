"""新标签页操作示例测试

本示例展示了如何在Playwright测试中处理新标签页的各种场景：
1. 点击链接打开新标签页
2. 在新标签页中执行操作
3. 在多个标签页之间切换
4. 管理和清理标签页
"""
import pytest
from playwright.sync_api import Page
from pages.base_page import BasePage


class ExamplePage(BasePage):
    """示例页面对象"""
    
    @property
    def url(self) -> str:
        return "http://localhost:8080/pages/dashboard.html"
    
    @property
    def title(self) -> str:
        return "仪表板"
    
    def __init__(self, page: Page):
        super().__init__(page)
        # 页面元素定位器
        self.new_tab_link = "a[target='_blank']"  # 在新标签页打开的链接
        self.external_link = "a[href*='external']"  # 外部链接
        self.popup_button = "#openPopup"  # 打开弹窗的按钮


class TestNewTabOperations:
    """新标签页操作测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前置条件"""
        self.main_page = ExamplePage(page)
        self.main_page.navigate()
    
    def test_click_and_wait_for_new_tab(self):
        """测试点击链接并等待新标签页打开"""
        # 方法1: 使用 click_and_wait_for_new_tab 方法
        new_page = self.main_page.click_and_wait_for_new_tab(self.main_page.new_tab_link)
        
        # 验证新页面已打开
        assert new_page is not None
        assert "localhost" in new_page.url
        
        # 在新页面中执行操作
        new_page_obj = ExamplePage(new_page)
        # 可以在新页面中继续执行测试操作
        
        # 关闭新页面
        new_page.close()
    
    def test_switch_to_new_tab_with_callback(self):
        """测试使用回调函数切换到新标签页"""
        # 方法2: 使用 switch_to_new_tab 方法
        new_page = self.main_page.switch_to_new_tab(
            lambda: self.main_page.click(self.main_page.new_tab_link)
        )
        
        # 验证新页面
        assert new_page is not None
        
        # 在新页面中创建页面对象并执行操作
        new_page_obj = ExamplePage(new_page)
        # 执行新页面的测试操作...
        
        # 清理
        new_page.close()
    
    def test_multiple_tabs_management(self):
        """测试多标签页管理"""
        # 打开第一个新标签页
        new_page1 = self.main_page.click_and_wait_for_new_tab(self.main_page.new_tab_link)
        
        # 打开第二个新标签页（从主页面）
        new_page2 = self.main_page.click_and_wait_for_new_tab(self.main_page.external_link)
        
        # 获取所有页面
        all_pages = self.main_page.get_all_pages()
        assert len(all_pages) == 3  # 主页面 + 2个新页面
        
        # 根据URL切换页面
        target_page = self.main_page.switch_to_page_by_url("dashboard")
        assert target_page is not None
        
        # 根据标题切换页面
        target_page = self.main_page.switch_to_page_by_title("仪表板")
        assert target_page is not None
        
        # 关闭其他页面，只保留主页面
        self.main_page.close_other_pages(keep_current=True)
        
        # 验证只剩下主页面
        remaining_pages = self.main_page.get_all_pages()
        assert len(remaining_pages) == 1
    
    def test_complex_new_tab_workflow(self):
        """测试复杂的新标签页工作流程"""
        # 1. 在主页面执行一些操作
        self.main_page.wait_for_element("body")
        
        # 2. 点击链接打开新标签页
        new_page = self.main_page.click_and_wait_for_new_tab(self.main_page.new_tab_link)
        
        # 3. 在新标签页中创建页面对象
        new_page_obj = ExamplePage(new_page)
        
        # 4. 在新标签页中执行操作
        new_page_obj.wait_for_page_load()
        # 可以在这里添加更多新页面的操作...
        
        # 5. 切换回主页面
        main_page_from_list = self.main_page.switch_to_page_by_url("dashboard")
        assert main_page_from_list == self.main_page.page
        
        # 6. 在主页面继续执行操作
        # 可以继续在主页面执行操作...
        
        # 7. 再次切换到新页面
        new_page_from_list = self.main_page.switch_to_page_by_url(new_page.url)
        assert new_page_from_list == new_page
        
        # 8. 清理所有新页面
        self.main_page.close_other_pages(keep_current=True)
    
    def test_wait_for_new_page_without_action(self):
        """测试等待新页面打开（不执行操作）"""
        # 这种情况适用于页面自动打开新标签页的场景
        # 比如某些JavaScript代码会自动打开新窗口
        
        # 模拟：执行一个会触发新页面打开的JavaScript
        self.main_page.page.evaluate("""
            setTimeout(() => {
                window.open('http://localhost:8080/pages/login.html', '_blank');
            }, 1000);
        """)
        
        # 等待新页面打开
        new_page = self.main_page.wait_for_new_page(timeout=5000)
        
        # 验证新页面
        assert new_page is not None
        assert "login" in new_page.url
        
        # 清理
        new_page.close()
    
    def test_error_handling_for_new_tab(self):
        """测试新标签页操作的错误处理"""
        # 测试点击不存在的元素
        with pytest.raises(Exception):
            self.main_page.click_and_wait_for_new_tab("#non-existent-element")
        
        # 测试等待新页面超时
        with pytest.raises(Exception):
            self.main_page.wait_for_new_page(timeout=1000)  # 很短的超时时间
    
    def test_new_tab_with_different_page_objects(self):
        """测试在新标签页中使用不同的页面对象"""
        from pages.login_page import LoginPage
        
        # 假设点击某个链接会打开登录页面
        new_page = self.main_page.switch_to_new_tab(
            lambda: self.main_page.page.evaluate("window.open('/pages/login.html', '_blank')")
        )
        
        # 在新标签页中使用LoginPage对象
        login_page = LoginPage(new_page)
        
        # 验证登录页面元素
        login_page.verify_login_page_elements()
        
        # 在登录页面执行操作
        login_page.enter_username("testuser")
        login_page.enter_password("testpass")
        
        # 清理
        new_page.close()


class TestAdvancedNewTabScenarios:
    """高级新标签页场景测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前置条件"""
        self.main_page = ExamplePage(page)
        self.main_page.navigate()
    
    def test_new_tab_with_context_isolation(self):
        """测试新标签页的上下文隔离"""
        # 在主页面设置一些状态
        self.main_page.page.evaluate("localStorage.setItem('test', 'main_page')")
        
        # 打开新标签页
        new_page = self.main_page.click_and_wait_for_new_tab(self.main_page.new_tab_link)
        
        # 验证新标签页可以访问相同的localStorage（同源）
        storage_value = new_page.evaluate("localStorage.getItem('test')")
        assert storage_value == 'main_page'
        
        # 在新标签页设置不同的值
        new_page.evaluate("localStorage.setItem('test', 'new_page')")
        
        # 验证主页面也能看到变化（因为是同源）
        main_storage_value = self.main_page.page.evaluate("localStorage.getItem('test')")
        assert main_storage_value == 'new_page'
        
        # 清理
        new_page.close()
    
    def test_new_tab_performance_monitoring(self):
        """测试新标签页的性能监控"""
        import time
        
        # 记录开始时间
        start_time = time.time()
        
        # 打开新标签页
        new_page = self.main_page.click_and_wait_for_new_tab(self.main_page.new_tab_link)
        
        # 记录结束时间
        end_time = time.time()
        
        # 验证打开新标签页的时间在合理范围内
        open_time = end_time - start_time
        assert open_time < 10  # 应该在10秒内完成
        
        # 可以添加更多性能相关的断言
        
        # 清理
        new_page.close()
    
    def test_new_tab_with_network_interception(self):
        """测试新标签页的网络拦截"""
        # 设置网络拦截
        def handle_request(route, request):
            if "api" in request.url:
                # 模拟API响应
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body='{"status": "mocked"}'
                )
            else:
                route.continue_()
        
        # 在主页面设置拦截
        self.main_page.page.route("**/*", handle_request)
        
        # 打开新标签页
        new_page = self.main_page.click_and_wait_for_new_tab(self.main_page.new_tab_link)
        
        # 在新标签页也需要设置拦截（如果需要的话）
        new_page.route("**/*", handle_request)
        
        # 在新标签页中测试网络请求
        response = new_page.evaluate("""
            fetch('/api/test').then(r => r.json())
        """)
        
        # 验证拦截生效
        # assert response["status"] == "mocked"
        
        # 清理
        new_page.close()


if __name__ == "__main__":
    # 运行示例测试
    pytest.main([__file__, "-v"])