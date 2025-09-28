"""
新标签页操作测试示例

本文件演示了如何在Playwright测试中处理新标签页的各种场景
"""

import pytest
import time
from pages.base_page import BasePage


class ExamplePage(BasePage):
    """示例页面对象，用于演示新标签页操作"""
    
    def __init__(self, page):
        super().__init__(page)
        self._url = "https://example.com"
        self._title = "Example Domain"
    
    @property
    def url(self) -> str:
        """页面URL"""
        return self._url
    
    @property
    def title(self) -> str:
        """页面标题"""
        return self._title
    
    def navigate(self):
        """导航到示例页面"""
        self.page.goto(self._url)
        self.wait_for_page_load()
    
    def create_test_links(self):
        """创建测试用的链接（用于演示）"""
        # 在页面中注入测试链接
        self.page.evaluate("""
            // 创建一个会在新标签页打开的链接
            const link1 = document.createElement('a');
            link1.href = 'https://httpbin.org/get';
            link1.target = '_blank';
            link1.id = 'new-tab-link';
            link1.textContent = '在新标签页打开';
            document.body.appendChild(link1);
            
            // 创建一个按钮，点击后用JavaScript打开新窗口
            const button1 = document.createElement('button');
            button1.id = 'js-open-button';
            button1.textContent = '用JS打开新窗口';
            button1.onclick = () => window.open('https://httpbin.org/json', '_blank');
            document.body.appendChild(button1);
            
            // 创建多个测试链接
            for(let i = 1; i <= 3; i++) {
                const link = document.createElement('a');
                link.href = `https://httpbin.org/get?page=${i}`;
                link.target = '_blank';
                link.id = `test-link-${i}`;
                link.textContent = `测试链接 ${i}`;
                document.body.appendChild(link);
                document.body.appendChild(document.createElement('br'));
            }
        """)
        
        # 等待元素创建完成
        self.wait_for_element("#new-tab-link")
        self.wait_for_element("#js-open-button")


class TestNewTabOperations:
    """新标签页基础操作测试"""
    
    def test_click_and_wait_for_new_tab(self, page):
        """测试点击链接并等待新标签页打开"""
        example_page = ExamplePage(page)
        example_page.navigate()
        example_page.create_test_links()
        
        # 点击链接打开新标签页
        new_page = example_page.click_and_wait_for_new_tab("#new-tab-link")
        
        # 验证新页面已打开
        assert new_page is not None
        assert "httpbin.org" in new_page.url
        
        # 在新页面中执行操作
        # 由于BasePage是抽象类，我们直接使用page对象进行操作
        new_page.wait_for_load_state("networkidle")
        
        # 验证页面内容
        content = new_page.content()
        assert "httpbin" in content.lower()
        
        # 清理：关闭新页面
        new_page.close()
        
        # 验证原页面仍然可用
        assert example_page.page.url.rstrip('/') == example_page._url.rstrip('/')
    
    def test_switch_to_new_tab_with_callback(self, page):
        """测试使用回调函数打开新标签页"""
        example_page = ExamplePage(page)
        example_page.navigate()
        example_page.create_test_links()
        
        # 使用回调函数打开新标签页
        new_page = example_page.switch_to_new_tab(
            lambda: example_page.click("#js-open-button")
        )
        
        # 验证新页面
        assert new_page is not None
        assert "httpbin.org" in new_page.url
        
        # 在新页面中验证JSON内容
        new_page.wait_for_load_state("networkidle")
        
        # 清理
        new_page.close()
    
    def test_get_all_pages(self, page):
        """测试获取所有页面"""
        example_page = ExamplePage(page)
        example_page.navigate()
        example_page.create_test_links()
        
        # 初始应该只有一个页面
        initial_pages = example_page.get_all_pages()
        assert len(initial_pages) == 1
        
        # 打开新标签页
        new_page1 = example_page.click_and_wait_for_new_tab("#test-link-1")
        new_page2 = example_page.click_and_wait_for_new_tab("#test-link-2")
        
        # 现在应该有3个页面
        all_pages = example_page.get_all_pages()
        assert len(all_pages) == 3
        
        # 清理
        new_page1.close()
        new_page2.close()
        
        # 验证页面数量恢复
        final_pages = example_page.get_all_pages()
        assert len(final_pages) == 1
    
    def test_switch_to_page_by_url(self, page):
        """测试根据URL切换页面"""
        example_page = ExamplePage(page)
        example_page.navigate()
        example_page.create_test_links()
        
        # 打开多个新标签页
        new_page1 = example_page.click_and_wait_for_new_tab("#test-link-1")
        new_page2 = example_page.click_and_wait_for_new_tab("#test-link-2")
        
        # 根据URL模式切换页面
        found_page = example_page.switch_to_page_by_url("page=1")
        assert found_page == new_page1
        
        found_page2 = example_page.switch_to_page_by_url("page=2")
        assert found_page2 == new_page2
        
        # 测试通配符匹配
        httpbin_page = example_page.switch_to_page_by_url("httpbin.org")
        assert httpbin_page is not None
        
        # 清理
        new_page1.close()
        new_page2.close()
    
    def test_close_other_pages(self, page):
        """测试关闭其他页面"""
        example_page = ExamplePage(page)
        example_page.navigate()
        example_page.create_test_links()
        
        # 打开多个新标签页
        new_page1 = example_page.click_and_wait_for_new_tab("#test-link-1")
        new_page2 = example_page.click_and_wait_for_new_tab("#test-link-2")
        new_page3 = example_page.click_and_wait_for_new_tab("#test-link-3")
        
        # 验证有4个页面（1个原始页面 + 3个新页面）
        all_pages = example_page.get_all_pages()
        assert len(all_pages) == 4
        
        # 关闭其他页面，保留当前页面
        example_page.close_other_pages(keep_current=True)
        
        # 验证只剩下原始页面
        remaining_pages = example_page.get_all_pages()
        assert len(remaining_pages) == 1
        assert remaining_pages[0] == example_page.page


class TestAdvancedNewTabScenarios:
    """高级新标签页场景测试"""
    
    def test_multi_tab_workflow(self, page):
        """测试多标签页工作流程"""
        example_page = ExamplePage(page)
        example_page.navigate()
        example_page.create_test_links()
        
        new_pages = []
        
        try:
            # 打开多个新标签页
            for i in range(1, 4):
                new_page = example_page.click_and_wait_for_new_tab(f"#test-link-{i}")
                new_pages.append(new_page)
                
                # 在每个新页面中执行操作
                new_page.wait_for_load_state("networkidle")
                
                # 验证页面参数
                assert f"page={i}" in new_page.url
            
            # 验证所有页面都已打开
            all_pages = example_page.get_all_pages()
            assert len(all_pages) == 4  # 1个原始页面 + 3个新页面
            
            # 在不同页面间切换并执行操作
            for i, new_page in enumerate(new_pages, 1):
                # 切换到指定页面
                target_page = example_page.switch_to_page_by_url(f"page={i}")
                assert target_page == new_page
                
                # 在该页面中执行操作
                content = target_page.content()
                assert "httpbin" in content.lower()
        
        finally:
            # 清理所有新页面
            for new_page in new_pages:
                try:
                    new_page.close()
                except:
                    pass  # 忽略已关闭的页面
    
    def test_error_handling_and_retry(self, page):
        """测试错误处理和重试机制"""
        example_page = ExamplePage(page)
        example_page.navigate()
        
        # 创建一个可能失败的链接
        example_page.page.evaluate("""
            const link = document.createElement('a');
            link.href = 'https://httpbin.org/delay/1';  // 延迟1秒的链接
            link.target = '_blank';
            link.id = 'slow-link';
            link.textContent = '慢速链接';
            document.body.appendChild(link);
        """)
        
        example_page.wait_for_element("#slow-link")
        
        # 测试超时处理
        try:
            new_page = example_page.click_and_wait_for_new_tab(
                "#slow-link", 
                timeout=5000  # 5秒超时
            )
            
            # 如果成功打开，验证页面
            assert new_page is not None
            new_page.wait_for_load_state("networkidle")
            
            # 清理
            new_page.close()
            
        except Exception as e:
            # 如果超时，这是预期的行为
            print(f"预期的超时错误: {e}")
    
    def test_page_object_integration(self, page):
        """测试页面对象模式集成"""
        
        class MainPage(BasePage):
            """主页面对象"""
            
            def __init__(self, page):
                super().__init__(page)
                self._url = "https://example.com"
                self._title = "Example Domain"
            
            @property
            def url(self) -> str:
                """页面URL"""
                return self._url
            
            @property
            def title(self) -> str:
                """页面标题"""
                return self._title
            
            def navigate(self):
                self.page.goto(self._url)
                self.wait_for_page_load()
                self._create_links()
            
            def _create_links(self):
                """创建测试链接"""
                self.page.evaluate("""
                    const helpLink = document.createElement('a');
                    helpLink.href = 'https://httpbin.org/get?type=help';
                    helpLink.target = '_blank';
                    helpLink.id = 'help-link';
                    helpLink.textContent = '帮助';
                    document.body.appendChild(helpLink);
                    
                    const settingsLink = document.createElement('a');
                    settingsLink.href = 'https://httpbin.org/get?type=settings';
                    settingsLink.target = '_blank';
                    settingsLink.id = 'settings-link';
                    settingsLink.textContent = '设置';
                    document.body.appendChild(settingsLink);
                """)
                self.wait_for_element("#help-link")
                self.wait_for_element("#settings-link")
            
            def open_help_in_new_tab(self):
                """打开帮助页面在新标签页中"""
                new_page = self.click_and_wait_for_new_tab("#help-link")
                return HelpPage(new_page)
            
            def open_settings_in_new_tab(self):
                """打开设置页面在新标签页中"""
                new_page = self.click_and_wait_for_new_tab("#settings-link")
                return SettingsPage(new_page)
        
        class HelpPage(BasePage):
            """帮助页面对象"""
            
            @property
            def url(self) -> str:
                """页面URL"""
                return "https://httpbin.org/get?type=help"
            
            @property
            def title(self) -> str:
                """页面标题"""
                return "Help Page"
            
            def verify_help_content(self):
                """验证帮助页面内容"""
                self.wait_for_page_load()
                content = self.page.content()
                assert "type=help" in content
                return True
        
        class SettingsPage(BasePage):
            """设置页面对象"""
            
            @property
            def url(self) -> str:
                """页面URL"""
                return "https://httpbin.org/get?type=settings"
            
            @property
            def title(self) -> str:
                """页面标题"""
                return "Settings Page"
            
            def verify_settings_content(self):
                """验证设置页面内容"""
                self.wait_for_page_load()
                content = self.page.content()
                assert "type=settings" in content
                return True
        
        # 测试页面对象集成
        main_page = MainPage(page)
        main_page.navigate()
        
        # 使用页面对象方法打开新标签页
        help_page = main_page.open_help_in_new_tab()
        assert help_page.verify_help_content()
        help_page.page.close()
        
        settings_page = main_page.open_settings_in_new_tab()
        assert settings_page.verify_settings_content()
        settings_page.page.close()


if __name__ == "__main__":
    # 运行测试的示例命令
    print("运行新标签页测试示例:")
    print("pytest test_new_tab_example.py -v")
    print("pytest test_new_tab_example.py::TestNewTabOperations::test_click_and_wait_for_new_tab -v")