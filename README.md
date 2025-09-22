# Playwright Web UI 自动化测试框架

一个基于 Playwright 和 unittest 的现代化 Web UI 自动化测试框架，采用页面对象模型(POM)设计模式，支持多浏览器、截图录制、失败重试等企业级功能。

## 📋 目录

- [框架特点](#框架特点)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [详细文档](#详细文档)
- [支持与贡献](#支持与贡献)

## 🏗️ 框架特点

- **分层架构设计**：配置层、页面对象层、测试用例层、工具层清晰分离
- **页面对象模型(POM)**：封装页面元素和操作，提高代码复用性和维护性
- **多浏览器支持**：支持 Chromium、Firefox、WebKit 三种浏览器引擎
- **智能配置管理**：支持环境变量、配置文件的多层配置
- **丰富的截图和视频录制**：自动截图、失败截图、视频录制功能
- **完善的日志系统**：详细的测试执行日志和错误追踪

## 🛠️ 技术栈

- **核心框架**：Playwright + unittest
- **日志系统**：loguru
- **配置管理**：pydantic + YAML配置
- **图像处理**：Pillow + opencv-python


## 📚 详细文档

- [功能使用指南](docs/feature_usage_guide.md) - 截图、视频录制、日志系统等功能的详细使用说明
- [核心组件使用方法](docs/core_components_guide.md) - BasePage、BaseTest 等核心组件的使用方法和最佳实践
- [开发指导](docs/development_guide.md) - 页面对象编写规范、测试用例编写方法、新手入门指南
- [元素定位教程](docs/element_locating_guide.md) - 详细的元素定位方法和最佳实践指南
- [Playwright 定位器迁移指南](docs/playwright_locators_migration_guide.md) - 从传统定位器迁移到页面对象模型的完整指南

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+ (Playwright 依赖)
- Git

### 安装步骤

```bash
# 1. 克隆项目
git clone <your-repository-url>
cd PlaywrightProject

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装浏览器
playwright install

# 5. 配置项目（可选）
# 项目使用 config.yaml 进行配置，默认配置已可直接使用
# 如需自定义，可编辑 config.yaml 文件或设置环境变量 PLAYWRIGHT_ENV

# 6. 运行测试
python -m unittest discover tests -v
```

### 常用命令

```bash
# 运行所有测试
python -m unittest discover tests -v

# 运行特定测试文件
python -m unittest tests.test_login -v

# 运行特定测试方法
python -m unittest tests.test_login.TestLogin.test_successful_login_admin -v

# 运行测试并显示详细输出
python -m unittest discover tests -v
```

## 📁 项目结构

```
PlaywrightProject/
├── config.yaml               # 项目配置文件
├── config/                   # 配置模块
│   └── config.py               # 统一配置管理（包含Playwright配置）
├── utils/                    # 工具模块
│   ├── config.py            # YAML配置管理
│   ├── logger_config.py     # 日志配置
│   ├── screenshot_helper.py # 截图助手
│   └── video_helper.py      # 视频录制助手
│   ├── base_page.py         # 页面基类
│   ├── login_page.py        # 登录页面
│   ├── dashboard_page.py    # 仪表板页面
│   └── ...                  # 其他页面对象
├── tests/                    # 测试用例模块
│   ├── base_test.py         # 测试基类
│   ├── test_login.py        # 登录测试
│   └── ...                  # 其他测试文件
├── utils/                    # 工具模块
│   ├── logger_config.py     # 日志配置
│   ├── screenshot_helper.py # 截图助手
│   └── video_helper.py      # 视频助手
├── reports/                  # 测试报告目录
│   ├── screenshots/         # 截图文件
│   └── videos/             # 视频文件
└── requirements.txt         # 依赖列表
```

## 📞 支持与贡献

如有问题或建议，请提交 Issue 或 Pull Request。

### 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

**Happy Testing! 🎉**