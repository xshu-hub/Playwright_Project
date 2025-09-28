# Playwright 新标签页操作指南

## 概述

在Web自动化测试中，经常会遇到点击链接或按钮后打开新标签页的场景。本指南详细介绍了如何在Playwright测试框架中优雅地处理这些情况。

## 核心方法介绍

### 1. `click_and_wait_for_new_tab(selector, timeout=None)`

**用途**：点击指定元素并等待新标签页打开

**参数**：
- `selector`: 要点击的元素选择器
- `timeout`: 等待超时时间（可选）

**返回值**：新打开的Page对象

**示例**：
```python
# 点击链接打开新标签页
new_page = base_page.click_and_wait_for_new_tab("a[target='_blank']")

# 在新页面中执行操作
new_page_obj = SomePage(new_page)
new_page_obj.do_something()

# 关闭新页面
new_page.close()
```

### 2. `switch_to_new_tab(action_callback, timeout=None)`

**用途**：执行自定义操作并等待新标签页打开

**参数**：
- `action_callback`: 触发新标签页的操作回调函数
- `timeout`: 等待超时时间（可选）

**返回值**：新打开的Page对象

**示例**：
```python
# 使用回调函数的方式
new_page = base_page.switch_to_new_tab(
    lambda: base_page.click("#complex-button")
)

# 或者执行更复杂的操作
new_page = base_page.switch_to_new_tab(
    lambda: base_page.page.evaluate("window.open('/new-page', '_blank')")
)
```

### 3. `get_all_pages()`

**用途**：获取当前浏览器上下文中的所有页面

**返回值**：Page对象列表

**示例**：
```python
pages = base_page.get_all_pages()
print(f"当前共有 {len(pages)} 个页面")
for i, page in enumerate(pages):
    print(f"页面 {i}: {page.url}")
```

### 4. `switch_to_page_by_url(url_pattern)`

**用途**：根据URL模式切换到指定页面

**参数**：
- `url_pattern`: URL模式（支持通配符）

**返回值**：匹配的Page对象或None

**示例**：
```python
# 切换到包含"dashboard"的页面
dashboard_page = base_page.switch_to_page_by_url("dashboard")

# 使用通配符匹配
api_page = base_page.switch_to_page_by_url("*/api/*")
```

### 5. `switch_to_page_by_title(title_pattern)`

**用途**：根据页面标题切换到指定页面

**参数**：
- `title_pattern`: 标题模式

**返回值**：匹配的Page对象或None

**示例**：
```python
# 切换到标题包含"登录"的页面
login_page = base_page.switch_to_page_by_title("登录")
```

### 6. `close_other_pages(keep_current=True)`

**用途**：关闭其他页面，只保留当前页面

**参数**：
- `keep_current`: 是否保留当前页面

**示例**：
```python
# 关闭除当前页面外的所有页面
base_page.close_other_pages(keep_current=True)

# 关闭所有页面
base_page.close_other_pages(keep_current=False)
```

### 7. `wait_for_new_page(timeout=None)`

**用途**：等待新页面打开（不执行任何操作）

**参数**：
- `timeout`: 等待超时时间（可选）

**返回值**：新打开的Page对象

**示例**：
```python
# 适用于JavaScript自动打开新窗口的场景
page.evaluate("setTimeout(() => window.open('/new-page'), 1000)")
new_page = base_page.wait_for_new_page(timeout=5000)
```

## 实际应用场景

### 场景1：简单的链接点击

```python
def test_simple_link_click(self, page):
    """测试简单的链接点击打开新标签页"""
    main_page = MainPage(page)
    main_page.navigate()
    
    # 点击链接打开新标签页
    new_page = main_page.click_and_wait_for_new_tab("a[href='/help']")
    
    # 在新页面中验证内容
    help_page = HelpPage(new_page)
    assert help_page.is_help_content_visible()
    
    # 清理
    new_page.close()
```

### 场景2：复杂的多步操作

```python
def test_complex_multi_step_operation(self, page):
    """测试复杂的多步操作打开新标签页"""
    main_page = MainPage(page)
    main_page.navigate()
    
    # 执行复杂操作打开新标签页
    new_page = main_page.switch_to_new_tab(lambda: (
        main_page.fill("#search-input", "test"),
        main_page.click("#search-button"),
        main_page.click("#open-in-new-tab")
    ))
    
    # 在新页面中执行测试
    search_page = SearchPage(new_page)
    search_page.verify_search_results()
    
    new_page.close()
```

### 场景3：多标签页工作流

```python
def test_multi_tab_workflow(self, page):
    """测试多标签页工作流程"""
    main_page = MainPage(page)
    main_page.navigate()
    
    # 打开多个新标签页
    tab1 = main_page.click_and_wait_for_new_tab("#link1")
    tab2 = main_page.click_and_wait_for_new_tab("#link2")
    tab3 = main_page.click_and_wait_for_new_tab("#link3")
    
    # 在不同标签页中执行操作
    page1 = Page1(tab1)
    page1.perform_action1()
    
    page2 = Page2(tab2)
    page2.perform_action2()
    
    page3 = Page3(tab3)
    page3.perform_action3()
    
    # 切换回主页面
    main_page_ref = main_page.switch_to_page_by_url("main")
    assert main_page_ref == main_page.page
    
    # 验证主页面状态
    main_page.verify_final_state()
    
    # 清理所有新标签页
    main_page.close_other_pages(keep_current=True)
```

### 场景4：错误处理和重试

```python
def test_new_tab_with_retry(self, page):
    """测试新标签页操作的错误处理和重试"""
    main_page = MainPage(page)
    main_page.navigate()
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            new_page = main_page.click_and_wait_for_new_tab(
                "#sometimes-slow-link", 
                timeout=5000
            )
            
            # 验证新页面加载成功
            if new_page.url and "error" not in new_page.url:
                break
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(1)  # 等待1秒后重试
    
    # 在新页面中执行测试
    new_page_obj = NewPage(new_page)
    new_page_obj.verify_content()
    
    new_page.close()
```

## 最佳实践

### 1. 资源管理

```python
def test_proper_resource_management(self, page):
    """正确的资源管理示例"""
    main_page = MainPage(page)
    main_page.navigate()
    
    new_pages = []
    try:
        # 打开多个新标签页
        for i in range(3):
            new_page = main_page.click_and_wait_for_new_tab(f"#link{i}")
            new_pages.append(new_page)
            
        # 执行测试操作
        for new_page in new_pages:
            # 在每个新页面中执行操作
            pass
            
    finally:
        # 确保清理所有新页面
        for new_page in new_pages:
            try:
                new_page.close()
            except:
                pass  # 忽略关闭失败的情况
```

### 2. 使用上下文管理器

```python
from contextlib import contextmanager

@contextmanager
def new_tab_context(base_page, selector):
    """新标签页上下文管理器"""
    new_page = None
    try:
        new_page = base_page.click_and_wait_for_new_tab(selector)
        yield new_page
    finally:
        if new_page:
            new_page.close()

def test_with_context_manager(self, page):
    """使用上下文管理器的示例"""
    main_page = MainPage(page)
    main_page.navigate()
    
    with new_tab_context(main_page, "#help-link") as new_page:
        help_page = HelpPage(new_page)
        help_page.verify_help_content()
        # 新页面会自动关闭
```

### 3. 页面对象模式集成

```python
class MainPage(BasePage):
    """主页面对象"""
    
    def open_help_in_new_tab(self) -> 'HelpPage':
        """打开帮助页面在新标签页中"""
        new_page = self.click_and_wait_for_new_tab("#help-link")
        return HelpPage(new_page)
    
    def open_settings_in_new_tab(self) -> 'SettingsPage':
        """打开设置页面在新标签页中"""
        new_page = self.click_and_wait_for_new_tab("#settings-link")
        return SettingsPage(new_page)

def test_page_object_integration(self, page):
    """页面对象模式集成示例"""
    main_page = MainPage(page)
    main_page.navigate()
    
    # 使用页面对象方法打开新标签页
    help_page = main_page.open_help_in_new_tab()
    help_page.verify_help_content()
    help_page.page.close()
    
    settings_page = main_page.open_settings_in_new_tab()
    settings_page.update_user_preferences()
    settings_page.page.close()
```

## 常见问题和解决方案

### 问题1：新标签页打开超时

**原因**：网络慢或页面加载时间长

**解决方案**：
```python
# 增加超时时间
new_page = base_page.click_and_wait_for_new_tab(
    "#slow-link", 
    timeout=30000  # 30秒
)

# 或者使用重试机制
def open_new_tab_with_retry(base_page, selector, max_retries=3):
    for attempt in range(max_retries):
        try:
            return base_page.click_and_wait_for_new_tab(selector, timeout=10000)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2)
```

### 问题2：无法找到新打开的页面

**原因**：页面打开后立即被重定向或关闭

**解决方案**：
```python
# 等待页面稳定后再进行操作
new_page = base_page.click_and_wait_for_new_tab("#link")
new_page.wait_for_load_state("networkidle")  # 等待网络空闲
new_page.wait_for_timeout(1000)  # 额外等待1秒

# 验证页面URL是否符合预期
assert "expected-url" in new_page.url
```

### 问题3：内存泄漏（页面未正确关闭）

**原因**：测试结束后未关闭新页面

**解决方案**：
```python
@pytest.fixture(autouse=True)
def cleanup_pages(self, page):
    """自动清理页面的fixture"""
    yield
    # 测试结束后清理所有页面
    try:
        base_page = BasePage(page)
        all_pages = base_page.get_all_pages()
        for p in all_pages[1:]:  # 保留第一个页面（主页面）
            p.close()
    except:
        pass
```

## 性能优化建议

### 1. 并行处理多个标签页

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def test_parallel_tab_operations(self, page):
    """并行处理多个标签页的操作"""
    main_page = MainPage(page)
    main_page.navigate()
    
    # 打开多个新标签页
    new_pages = []
    for i in range(3):
        new_page = main_page.click_and_wait_for_new_tab(f"#link{i}")
        new_pages.append(new_page)
    
    # 并行执行操作
    def process_page(page_info):
        page_obj, page_index = page_info
        # 在每个页面中执行操作
        return f"Page {page_index} processed"
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(
            process_page, 
            [(page, i) for i, page in enumerate(new_pages)]
        ))
    
    # 清理
    for new_page in new_pages:
        new_page.close()
```

### 2. 延迟加载页面对象

```python
class LazyPageManager:
    """延迟加载页面对象管理器"""
    
    def __init__(self, base_page):
        self.base_page = base_page
        self._page_cache = {}
    
    def get_page(self, page_type, selector):
        """延迟获取页面对象"""
        if page_type not in self._page_cache:
            new_page = self.base_page.click_and_wait_for_new_tab(selector)
            self._page_cache[page_type] = page_type(new_page)
        return self._page_cache[page_type]
    
    def cleanup(self):
        """清理所有缓存的页面"""
        for page_obj in self._page_cache.values():
            page_obj.page.close()
        self._page_cache.clear()
```

## 总结

通过使用本框架提供的新标签页操作方法，您可以：

1. **简化代码**：使用简洁的API处理复杂的新标签页场景
2. **提高稳定性**：内置的等待和错误处理机制
3. **增强可维护性**：清晰的方法命名和完整的文档
4. **优化性能**：智能的资源管理和清理机制

记住在测试结束后始终清理新打开的页面，以避免内存泄漏和资源浪费。