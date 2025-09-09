from playwright.sync_api import sync_playwright
import time

def debug_approval_list():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 登录
        page.goto('http://localhost:8080/pages/login.html')
        page.fill('#username', 'user1')
        page.fill('#password', 'user123')
        page.click('button[type="submit"]')
        time.sleep(2)
        
        # 先创建一个申请
        print('Creating approval...')
        page.goto('http://localhost:8080/pages/approval-create.html')
        page.wait_for_load_state('networkidle')
        
        page.fill('#title', 'Debug Test Approval')
        page.select_option('#type', 'leave')
        page.click('.priority-option[data-priority="high"]')
        page.fill('#description', 'Debug test description')
        page.click('button[type="submit"]')
        
        # 等待成功消息或页面跳转
        try:
            page.wait_for_selector('.success-message', timeout=3000)
            print('Success message found')
        except:
            print('No success message, checking current URL:', page.url)
        
        print('Approval created, checking list...')
        
        # 导航到申请列表
        page.goto('http://localhost:8080/pages/approval-list.html', wait_until='networkidle')
        time.sleep(1)
        
        print('Page title:', page.title())
        print('URL:', page.url)
        
        # 检查申请项目
        items = page.locator('.approval-item')
        print('Items count:', items.count())
        
        if items.count() > 0:
            print('First item HTML:')
            print(items.nth(0).inner_html())
            
            # 检查各个子元素
            print('\nChecking sub-elements:')
            try:
                title_elem = items.nth(0).locator('.approval-title')
                print('Title element count:', title_elem.count())
                if title_elem.count() > 0:
                    print('Title text:', title_elem.text_content())
            except Exception as e:
                print('Title error:', e)
                
            try:
                type_elem = items.nth(0).locator('.approval-type')
                print('Type element count:', type_elem.count())
                if type_elem.count() > 0:
                    print('Type text:', type_elem.text_content())
                else:
                    # 查找其他可能的类型元素
                    print('Looking for other type elements...')
                    meta_items = items.nth(0).locator('.meta-item')
                    print('Meta items count:', meta_items.count())
                    for i in range(meta_items.count()):
                        meta_text = meta_items.nth(i).text_content()
                        print(f'Meta item {i}: {meta_text}')
                        if '类型' in meta_text or 'type' in meta_text.lower():
                            print(f'Found type in meta item {i}: {meta_text}')
            except Exception as e:
                print('Type error:', e)
        else:
            print('No approval items found')
            print('Page content:')
            print(page.content())
        
        browser.close()

if __name__ == '__main__':
    debug_approval_list()