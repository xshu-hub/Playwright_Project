from playwright.sync_api import sync_playwright
import time

def test_data_persistence():
    """测试数据持久化"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("=== 第一步：用户登录并创建申请 ===")
        page.goto("http://localhost:8080/pages/login.html")
        page.fill("#username", "user1")
        page.fill("#password", "user123")
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard.html")
        
        # 创建申请
        page.goto("http://localhost:8080/pages/approval-create.html")
        approval_title = f"数据持久化测试 - {int(time.time())}"
        page.fill("#title", approval_title)
        page.select_option("#type", "leave")
        page.click(".priority-option[data-priority='high']")
        page.fill("#description", "测试数据持久化")
        page.click("button[type='submit']")
        page.wait_for_url("**/approval-list.html")
        
        # 检查申请是否创建成功
        approvals_count = page.locator(".approval-item").count()
        print(f"创建申请后，列表中有 {approvals_count} 个申请")
        
        print("=== 第二步：登出并切换到管理员 ===")
        # 直接清除用户会话，保留申请数据
        page.evaluate("() => { localStorage.removeItem('currentUser'); localStorage.removeItem('loginTime'); }")
        page.goto("http://localhost:8080/pages/login.html")
        
        # 管理员登录
        page.fill("#username", "admin")
        page.fill("#password", "admin123")
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard.html")
        
        print("=== 第三步：检查申请是否还存在 ===")
        page.goto("http://localhost:8080/pages/approval-list.html")
        page.wait_for_timeout(1000)
        
        approvals_count_after = page.locator(".approval-item").count()
        print(f"管理员登录后，列表中有 {approvals_count_after} 个申请")
        
        # 查找特定申请
        found = False
        for i in range(approvals_count_after):
            title_element = page.locator(".approval-item").nth(i).locator(".approval-title")
            title_text = title_element.text_content()
            print(f"申请 {i}: {title_text}")
            if approval_title in title_text:
                found = True
                break
        
        print(f"是否找到创建的申请: {found}")
        
        browser.close()

if __name__ == "__main__":
    test_data_persistence()