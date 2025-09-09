from playwright.sync_api import sync_playwright
import time

def debug_approval_process():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # 先登录普通用户创建申请
            print("1. 登录普通用户创建申请...")
            page.goto("http://localhost:8080/pages/login.html")
            page.fill("#username", "user1")
            page.fill("#password", "user123")
            page.click("button[type='submit']")
            page.wait_for_url("**/dashboard.html", timeout=10000)
            print("✓ 普通用户登录成功")
            
            # 创建申请
            print("2. 创建申请...")
            page.goto("http://localhost:8080/pages/approval-create.html")
            page.fill("#title", "调试测试申请")
            page.select_option("#type", "leave")
            page.click(".priority-option[data-priority='high']")
            page.fill("#description", "用于调试的测试申请")
            page.click("button[type='submit']")
            page.wait_for_selector(".success-message", timeout=10000)
            print("✓ 申请创建成功")
            
            # 切换到管理员账号
            print("3. 切换到管理员账号...")
            try:
                # 检查申请数据是否存在
                approvals_data = page.evaluate("() => Utils.storage.get('approvals')")
                print(f"  - 当前申请数据: {approvals_data}")
                
                # 清除当前用户会话并重新登录管理员
                print("  - 清除当前用户会话")
                page.evaluate("() => { Utils.storage.remove('currentUser'); Utils.storage.remove('loginTime'); }")
                
                print("  - 重新登录管理员")
                page.goto("http://localhost:8080/pages/login.html", wait_until="domcontentloaded")
                print(f"  - 导航后URL: {page.url}")
                
                page.wait_for_selector("#username", timeout=5000)
                page.fill("#username", "admin")
                page.fill("#password", "admin123")
                page.click("button[type='submit']")
                page.wait_for_url("**/dashboard.html", timeout=10000)
                print("✓ 管理员登录成功")
            except Exception as e:
                print(f"  - 切换管理员失败: {e}")
                print(f"  - 当前URL: {page.url}")
                raise
            
            # 导航到审批列表
            print("4. 导航到审批列表...")
            page.goto("http://localhost:8080/pages/approval-list.html")
            
            # 等待页面加载完成
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)  # 等待JavaScript执行
            
            # 检查是否有审批项
            approval_items = page.locator(".approval-item")
            if approval_items.count() > 0:
                print(f"✓ 审批列表加载成功，找到 {approval_items.count()} 个申请")
            else:
                print("❌ 没有找到任何申请，可能数据没有正确保存")
                # 打印当前页面内容用于调试
                content = page.locator("#approvalsList").inner_text()
                print(f"  - 审批列表内容: {content}")
                return
            
            # 点击第一个申请的查看按钮
            print("5. 点击查看申请...")
            view_buttons = page.locator("button:has-text('查看详情')")
            if view_buttons.count() > 0:
                view_buttons.first.click()
                page.wait_for_url("**/approval-detail.html*", timeout=10000)
                print("✓ 成功进入申请详情页")
            else:
                print("❌ 没有找到查看按钮")
                return
            
            # 检查审批按钮
            print("6. 检查审批按钮...")
            approve_button = page.locator("button:has-text('通过申请')")
            if approve_button.count() > 0:
                print("✓ 找到通过申请按钮")
                
                # 点击通过申请按钮
                print("7. 点击通过申请按钮...")
                approve_button.click()
                
                # 等待审批表单显示
                print("8. 等待审批表单显示...")
                comment_textarea = page.locator("#approvalComment")
                comment_textarea.wait_for(state="visible", timeout=10000)
                print("✓ 审批表单显示成功")
                
                # 填写审批意见
                print("9. 填写审批意见...")
                comment_textarea.fill("调试测试通过")
                print("✓ 审批意见填写成功")
                
                # 提交审批
                print("10. 提交审批...")
                submit_button = page.locator("button[type='submit']")
                submit_button.click()
                
                # 等待处理完成
                print("11. 等待处理完成...")
                time.sleep(3)
                print("✓ 审批处理完成")
                
            else:
                print("❌ 没有找到通过申请按钮")
                # 打印页面内容用于调试
                print("页面内容:")
                print(page.content()[:1000])
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            # 截图用于调试
            page.screenshot(path="debug_error.png")
            
        finally:
            browser.close()

if __name__ == "__main__":
    debug_approval_process()