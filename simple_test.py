#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试脚本 - 验证基本功能
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def test_basic_functionality():
    """测试基本功能"""
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🚀 开始基本功能测试")
            
            # 1. 测试登录页面加载
            print("📄 测试登录页面加载...")
            await page.goto("http://localhost:8080/pages/login.html", timeout=30000)
            await page.wait_for_load_state("domcontentloaded")
            
            # 验证登录表单元素
            username_input = page.locator("#username")
            password_input = page.locator("#password")
            login_button = page.locator("button[type='submit']")
            
            await username_input.wait_for(timeout=10000)
            await password_input.wait_for(timeout=10000)
            await login_button.wait_for(timeout=10000)
            print("✅ 登录页面元素验证成功")
            
            # 2. 测试用户登录
            print("🔐 测试用户登录...")
            await username_input.fill("user1")
            await password_input.fill("user123")
            await login_button.click()
            
            # 等待跳转到仪表板
            await page.wait_for_url("**/dashboard.html", timeout=15000)
            print("✅ 用户登录成功")
            
            # 3. 测试导航到申请创建页面
            print("📝 测试申请创建页面...")
            await page.goto("http://localhost:8080/pages/approval-create.html", timeout=30000)
            await page.wait_for_load_state("domcontentloaded")
            
            # 验证申请表单元素
            title_input = page.locator("#title")
            type_select = page.locator("#type")
            description_textarea = page.locator("#description")
            priority_medium = page.locator(".priority-option.medium")
            submit_button = page.locator("button[type='submit']")
            
            await title_input.wait_for(timeout=10000)
            await type_select.wait_for(timeout=10000)
            await description_textarea.wait_for(timeout=10000)
            await priority_medium.wait_for(timeout=10000)
            await submit_button.wait_for(timeout=10000)
            print("✅ 申请创建页面元素验证成功")
            
            # 4. 创建申请
            print("📋 创建测试申请...")
            test_title = f"简化测试申请 - {int(time.time())}"
            await title_input.fill(test_title)
            await type_select.select_option("leave")
            await description_textarea.fill("这是一个简化测试申请")
            await priority_medium.click()  # 点击优先级选项
            await submit_button.click()
            
            # 等待成功消息
            success_message = page.locator(".success-message").first
            await success_message.wait_for(timeout=10000)
            print("✅ 申请创建成功")
            
            # 5. 测试申请列表页面
            print("📋 测试申请列表页面...")
            await page.goto("http://localhost:8080/pages/approval-list.html", timeout=30000)
            await page.wait_for_load_state("domcontentloaded")
            
            # 等待申请列表加载
            await page.wait_for_timeout(2000)
            
            # 检查是否有申请项
            approval_items = page.locator(".approval-item")
            count = await approval_items.count()
            print(f"📊 找到 {count} 个申请项")
            
            if count > 0:
                print("✅ 申请列表显示正常")
            else:
                print("⚠️ 申请列表为空")
            
            print("🎉 基本功能测试完成！")
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            # 截图保存错误状态
            await page.screenshot(path="simple_test_error.png")
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())