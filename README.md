# Playwright Web UI 自动化测试框架

一个基于 Playwright 和 pytest 的现代化 Web UI 自动化测试框架，采用页面对象模型(POM)设计模式，支持多浏览器、并行执行、失败重试等企业级功能。

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
- **并行测试执行**：支持多进程并行执行，大幅提升测试效率
- **智能配置管理**：支持环境变量、配置文件的多层配置
- **丰富的测试报告**：集成 Allure 报告，提供详细的测试结果

## 🛠️ 技术栈

- **核心框架**：Playwright + pytest
- **报告工具**：Allure
- **并行执行**：pytest-xdist
- **日志系统**：loguru
- **配置管理**：pydantic + PyYAML


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

# 5. 配置环境（可选）
# 编辑 config/config.yaml 文件，根据需要修改配置

# 6. 运行测试
python run_tests.py
```

### 常用命令

```bash
# 运行所有测试
python run_tests.py

# 运行特定测试文件
pytest tests/test_login.py -v

# 运行标记测试
pytest -m smoke -v

# 并行运行测试
pytest -n 4 tests/

# 生成 Allure 报告
allure serve reports/allure-results
```

## 📁 项目结构

```
PlaywrightProject/
├── config/                   # 配置模块
│   ├── config.yaml          # YAML配置文件
│   ├── env_config.py        # 环境配置管理
│   └── playwright_config.py # Playwright 配置
├── pages/                    # 页面对象模块
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
├── conftest.py              # pytest 配置
├── pytest.ini              # pytest 配置文件
├── requirements.txt         # 依赖列表
└── run_tests.py            # 测试运行器
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