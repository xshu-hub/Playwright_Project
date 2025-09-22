"""
Allure测试报告工具类
提供测试用例的步骤记录、附件添加、结果分类展示等功能
"""

import os
import json
import allure
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from enum import Enum

from utils.logger_config import logger


class AllureSeverity:
    """Allure严重程度常量类"""
    BLOCKER = "blocker"
    CRITICAL = "critical"
    NORMAL = "normal"
    MINOR = "minor"
    TRIVIAL = "trivial"


class AllureStoryType(Enum):
    """Allure故事类型枚举"""
    UI_TEST = "UI自动化测试"
    API_TEST = "API接口测试"
    INTEGRATION_TEST = "集成测试"
    SMOKE_TEST = "冒烟测试"
    REGRESSION_TEST = "回归测试"


class AllureHelper:
    """Allure测试报告工具类"""
    
    def __init__(self):
        """初始化Allure工具类"""
        self.results_dir = Path("reports/allure-results")
        self.reports_dir = Path("reports/allure-report")
        self._ensure_directories()
        
    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.results_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
    @staticmethod
    def step(title: str):
        """
        测试步骤装饰器
        
        Args:
            title: 步骤标题
        """
        return allure.step(title)
    
    @staticmethod
    def feature(name: str):
        """
        功能模块装饰器
        
        Args:
            name: 功能模块名称
        """
        return allure.feature(name)
    
    @staticmethod
    def story(name: str):
        """
        用户故事装饰器
        
        Args:
            name: 用户故事名称
        """
        return allure.story(name)
    
    @staticmethod
    def severity(level: str):
        """
        严重程度装饰器
        
        Args:
            level: 严重程度级别
        """
        return allure.severity(level)
    
    @staticmethod
    def title(name: str):
        """
        测试用例标题装饰器
        
        Args:
            name: 测试用例标题
        """
        return allure.title(name)
    
    @staticmethod
    def description(text: str):
        """
        测试用例描述装饰器
        
        Args:
            text: 描述内容
        """
        return allure.description(text)
    
    @staticmethod
    def tag(*tags: str):
        """
        测试标签装饰器
        
        Args:
            tags: 标签列表
        """
        return allure.tag(*tags)
    
    @staticmethod
    def link(url: str, name: str = None):
        """
        添加链接装饰器
        
        Args:
            url: 链接地址
            name: 链接名称
        """
        return allure.link(url, name)
    
    @staticmethod
    def issue(url: str, name: str = None):
        """
        添加问题链接装饰器
        
        Args:
            url: 问题链接地址
            name: 问题名称
        """
        return allure.issue(url, name)
    
    @staticmethod
    def testcase(url: str, name: str = None):
        """
        添加测试用例链接装饰器
        
        Args:
            url: 测试用例链接地址
            name: 测试用例名称
        """
        return allure.testcase(url, name)
    
    @staticmethod
    def attach_text(text: str, name: str = "文本附件", attachment_type: str = allure.attachment_type.TEXT):
        """
        添加文本附件
        
        Args:
            text: 文本内容
            name: 附件名称
            attachment_type: 附件类型
        """
        allure.attach(text, name=name, attachment_type=attachment_type)
        logger.info(f"📎 已添加文本附件: {name}")
    
    @staticmethod
    def attach_file(file_path: str, name: str = None, attachment_type: str = None):
        """
        添加文件附件
        
        Args:
            file_path: 文件路径
            name: 附件名称
            attachment_type: 附件类型
        """
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ 附件文件不存在: {file_path}")
            return
            
        # 自动推断附件类型
        if attachment_type is None:
            file_ext = Path(file_path).suffix.lower()
            if file_ext in ['.png', '.jpg', '.jpeg']:
                attachment_type = allure.attachment_type.PNG
            elif file_ext in ['.html', '.htm']:
                attachment_type = allure.attachment_type.HTML
            elif file_ext in ['.json']:
                attachment_type = allure.attachment_type.JSON
            elif file_ext in ['.xml']:
                attachment_type = allure.attachment_type.XML
            elif file_ext in ['.txt', '.log']:
                attachment_type = allure.attachment_type.TEXT
            else:
                attachment_type = allure.attachment_type.TEXT
        
        # 设置默认名称
        if name is None:
            name = Path(file_path).name
            
        with open(file_path, 'rb') as f:
            allure.attach(f.read(), name=name, attachment_type=attachment_type)
        
        logger.info(f"📎 已添加文件附件: {name} ({file_path})")
    
    @staticmethod
    def attach_screenshot(screenshot_path: str, name: str = "截图"):
        """
        添加截图附件
        
        Args:
            screenshot_path: 截图文件路径
            name: 附件名称
        """
        AllureHelper.attach_file(screenshot_path, name, allure.attachment_type.PNG)
    
    @staticmethod
    def attach_video(video_path: str, name: str = "视频录制"):
        """
        添加视频附件
        
        Args:
            video_path: 视频文件路径
            name: 附件名称
        """
        if not os.path.exists(video_path):
            logger.warning(f"⚠️ 视频文件不存在: {video_path}")
            return
            
        with open(video_path, 'rb') as f:
            allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.MP4)
        
        logger.info(f"📎 已添加视频附件: {name} ({video_path})")
    
    @staticmethod
    def attach_json(data: Dict[Any, Any], name: str = "JSON数据"):
        """
        添加JSON数据附件
        
        Args:
            data: JSON数据
            name: 附件名称
        """
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        allure.attach(json_str, name=name, attachment_type=allure.attachment_type.JSON)
        logger.info(f"📎 已添加JSON附件: {name}")
    
    @staticmethod
    def attach_html(html_content: str, name: str = "HTML内容"):
        """
        添加HTML内容附件
        
        Args:
            html_content: HTML内容
            name: 附件名称
        """
        allure.attach(html_content, name=name, attachment_type=allure.attachment_type.HTML)
        logger.info(f"📎 已添加HTML附件: {name}")
    
    @staticmethod
    def dynamic_feature(name: str):
        """
        动态设置功能模块
        
        Args:
            name: 功能模块名称
        """
        allure.dynamic.feature(name)
    
    @staticmethod
    def dynamic_story(name: str):
        """
        动态设置用户故事
        
        Args:
            name: 用户故事名称
        """
        allure.dynamic.story(name)
    
    @staticmethod
    def dynamic_title(name: str):
        """
        动态设置测试标题
        
        Args:
            name: 测试标题
        """
        allure.dynamic.title(name)
    
    @staticmethod
    def dynamic_description(text: str):
        """
        动态设置测试描述
        
        Args:
            text: 描述内容
        """
        allure.dynamic.description(text)
    
    @staticmethod
    def dynamic_tag(*tags: str):
        """
        动态设置测试标签
        
        Args:
            tags: 标签列表
        """
        allure.dynamic.tag(*tags)
    
    @staticmethod
    def dynamic_severity(level: str):
        """
        动态设置严重程度
        
        Args:
            level: 严重程度级别
        """
        allure.dynamic.severity(level)
    
    @staticmethod
    def dynamic_link(url: str, name: str = None):
        """
        动态添加链接
        
        Args:
            url: 链接地址
            name: 链接名称
        """
        allure.dynamic.link(url, name)
    
    def add_environment_info(self, env_info: Dict[str, str]):
        """
        添加环境信息
        
        Args:
            env_info: 环境信息字典
        """
        env_file = self.results_dir / "environment.properties"
        
        with open(env_file, 'w', encoding='utf-8') as f:
            for key, value in env_info.items():
                f.write(f"{key}={value}\n")
        
        logger.info(f"📋 已添加环境信息到: {env_file}")
    
    def add_categories(self, categories: List[Dict[str, Any]]):
        """
        添加测试分类配置
        
        Args:
            categories: 分类配置列表
        """
        categories_file = self.results_dir / "categories.json"
        
        with open(categories_file, 'w', encoding='utf-8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📋 已添加测试分类配置到: {categories_file}")
    
    def generate_default_categories(self):
        """生成默认的测试分类配置"""
        default_categories = [
            {
                "name": "产品缺陷",
                "messageRegex": ".*AssertionError.*",
                "traceRegex": ".*AssertionError.*"
            },
            {
                "name": "测试缺陷",
                "messageRegex": ".*NoSuchElementException.*|.*TimeoutException.*",
                "traceRegex": ".*NoSuchElementException.*|.*TimeoutException.*"
            },
            {
                "name": "环境问题",
                "messageRegex": ".*ConnectionError.*|.*NetworkError.*",
                "traceRegex": ".*ConnectionError.*|.*NetworkError.*"
            },
            {
                "name": "配置问题",
                "messageRegex": ".*ConfigurationError.*|.*FileNotFoundError.*",
                "traceRegex": ".*ConfigurationError.*|.*FileNotFoundError.*"
            }
        ]
        
        self.add_categories(default_categories)
    
    def clean_results(self):
        """清理旧的测试结果"""
        if self.results_dir.exists():
            import shutil
            shutil.rmtree(self.results_dir)
            self.results_dir.mkdir(exist_ok=True)
            logger.info(f"🧹 已清理测试结果目录: {self.results_dir}")
    
    def generate_report(self, open_browser: bool = False):
        """
        生成Allure报告
        
        Args:
            open_browser: 是否自动打开浏览器
        """
        try:
            import subprocess
            
            # 生成报告
            cmd = f"allure generate {self.results_dir} -o {self.reports_dir} --clean"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Allure报告生成成功: {self.reports_dir}")
                
                if open_browser:
                    # 打开报告
                    serve_cmd = f"allure open {self.reports_dir}"
                    subprocess.Popen(serve_cmd, shell=True)
                    logger.info("🌐 已在浏览器中打开Allure报告")
            else:
                logger.error(f"❌ Allure报告生成失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ 生成Allure报告时发生错误: {str(e)}")
    
    def serve_report(self, port: int = 8080):
        """
        启动Allure报告服务
        
        Args:
            port: 服务端口
        """
        try:
            import subprocess
            
            cmd = f"allure serve {self.results_dir} --port {port}"
            logger.info(f"🚀 启动Allure报告服务，端口: {port}")
            subprocess.run(cmd, shell=True)
            
        except Exception as e:
            logger.error(f"❌ 启动Allure报告服务时发生错误: {str(e)}")


# 全局Allure工具实例
allure_helper = AllureHelper()


# 常用装饰器快捷方式
def allure_step(title: str):
    """测试步骤装饰器快捷方式"""
    return AllureHelper.step(title)


def allure_feature(name: str):
    """功能模块装饰器快捷方式"""
    return AllureHelper.feature(name)


def allure_story(name: str):
    """用户故事装饰器快捷方式"""
    return AllureHelper.story(name)


def allure_severity(level: str):
    """严重程度装饰器快捷方式"""
    return AllureHelper.severity(level)


def allure_title(name: str):
    """测试标题装饰器快捷方式"""
    return AllureHelper.title(name)


def allure_description(text: str):
    """测试描述装饰器快捷方式"""
    return AllureHelper.description(text)


def allure_tag(*tags: str):
    """测试标签装饰器快捷方式"""
    return AllureHelper.tag(*tags)