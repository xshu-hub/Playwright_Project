#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration file for Allure integration with unittest
"""

import pytest
import allure
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """Pytest配置钩子"""
    # 确保Allure结果目录存在
    allure_dir = config.getoption("--alluredir")
    if allure_dir:
        Path(allure_dir).mkdir(parents=True, exist_ok=True)
    
    # 设置Allure环境信息
    allure_env_path = Path(allure_dir) / "environment.properties" if allure_dir else None
    if allure_env_path:
        with open(allure_env_path, 'w', encoding='utf-8') as f:
            f.write(f"Test.Framework=Playwright + Unittest + Allure\n")
            f.write(f"Python.Version={sys.version.split()[0]}\n")
            f.write(f"Test.Environment=Local\n")
            f.write(f"Test.Execution.Date={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Browser=Chromium\n")
            f.write(f"Platform={os.name}\n")


def pytest_runtest_setup(item):
    """测试用例设置钩子"""
    # 为每个测试用例添加Allure标签
    if hasattr(item, 'cls') and item.cls:
        # 添加测试类名作为Epic
        allure.dynamic.epic(item.cls.__name__)
        
        # 根据测试路径添加Feature
        test_path = str(item.fspath)
        if 'test_group_1' in test_path:
            allure.dynamic.feature("登录功能测试")
            allure.dynamic.tag("group1")
        elif 'test_group_2' in test_path:
            allure.dynamic.feature("错误处理测试")
            allure.dynamic.tag("group2")
        elif 'test_group_3' in test_path:
            allure.dynamic.feature("UI元素测试")
            allure.dynamic.tag("group3")
        
        # 添加测试方法名作为Story
        allure.dynamic.story(item.name)
        
        # 添加严重程度
        if 'login' in item.name.lower():
            allure.dynamic.severity(allure.severity_level.CRITICAL)
        elif 'error' in item.name.lower() or 'invalid' in item.name.lower():
            allure.dynamic.severity(allure.severity_level.NORMAL)
        else:
            allure.dynamic.severity(allure.severity_level.MINOR)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试报告生成钩子"""
    outcome = yield
    report = outcome.get_result()
    
    # 获取测试实例
    test_instance = getattr(item, 'instance', None)
    
    # 在测试执行的各个阶段附加日志
    if test_instance and hasattr(test_instance, 'logger'):
        try:
            # 附加测试日志
            log_content = _get_test_logs(test_instance)
            if log_content:
                allure.attach(
                    log_content,
                    name=f"测试日志 - {report.when}",
                    attachment_type=allure.attachment_type.TEXT
                )
        except Exception as e:
            print(f"附加日志失败: {e}")
    
    # 只在测试失败时处理截图和视频
    if report.when == "call" and report.failed:
        if test_instance:
            # 附加截图
            try:
                if hasattr(test_instance, 'page') and test_instance.page:
                    screenshot = test_instance.page.screenshot()
                    allure.attach(
                        screenshot,
                        name="失败截图",
                        attachment_type=allure.attachment_type.PNG
                    )
            except Exception as e:
                print(f"附加截图失败: {e}")
            
            # 附加视频（如果存在）
            try:
                if hasattr(test_instance, 'video_helper'):
                    video_path = _get_latest_video_path(test_instance)
                    if video_path and video_path.exists():
                        with open(video_path, 'rb') as video_file:
                            allure.attach(
                                video_file.read(),
                                name="失败视频",
                                attachment_type=allure.attachment_type.MP4
                            )
            except Exception as e:
                print(f"附加视频失败: {e}")
            
            # 附加页面HTML
            try:
                if hasattr(test_instance, 'page') and test_instance.page:
                    html_content = test_instance.page.content()
                    allure.attach(
                        html_content,
                        name="页面HTML",
                        attachment_type=allure.attachment_type.HTML
                    )
            except Exception as e:
                print(f"附加HTML失败: {e}")
    
    return report


def _get_test_logs(test_instance):
    """获取测试日志内容"""
    try:
        # 尝试从logger获取日志内容
        if hasattr(test_instance, 'logger'):
            # 这里可以根据实际的日志配置来获取日志内容
            # 由于loguru的特殊性，我们可能需要从日志文件中读取
            log_file_path = Path("logs") / f"{test_instance.__class__.__name__}.log"
            if log_file_path.exists():
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        return None
    except Exception:
        return None


def _get_latest_video_path(test_instance):
    """获取最新的视频文件路径"""
    try:
        if hasattr(test_instance, 'get_session_dir'):
            video_dir = test_instance.get_session_dir() / "videos"
            if video_dir.exists():
                video_files = list(video_dir.glob("*.webm"))
                if video_files:
                    # 返回最新的视频文件
                    return max(video_files, key=lambda x: x.stat().st_mtime)
        return None
    except Exception:
        return None


@pytest.fixture(autouse=True)
def allure_test_context(request):
    """自动为所有测试添加Allure上下文"""
    # 添加测试描述
    if hasattr(request.function, '__doc__') and request.function.__doc__:
        allure.dynamic.description(request.function.__doc__.strip())
    
    # 添加测试ID
    allure.dynamic.testcase(f"TC_{request.node.nodeid.replace('::', '_').replace('/', '_')}")
    
    yield
    
    # 测试完成后的清理工作
    pass


def pytest_collection_modifyitems(config, items):
    """修改收集到的测试项"""
    for item in items:
        # 为所有测试添加默认标记
        item.add_marker(pytest.mark.ui)
        
        # 根据测试路径添加特定标记
        test_path = str(item.fspath)
        if 'test_group_1' in test_path:
            item.add_marker(pytest.mark.group1)
            item.add_marker(pytest.mark.login)
        elif 'test_group_2' in test_path:
            item.add_marker(pytest.mark.group2)
        elif 'test_group_3' in test_path:
            item.add_marker(pytest.mark.group3)