# Allure 测试报告集成指南

本项目已集成 Allure 测试报告框架，提供美观、详细的测试报告。

## 安装依赖

### Python 依赖
```bash
pip install -r requirements.txt
```

### Allure 命令行工具
```bash
# 使用 npm 安装（推荐）
npm install -g allure-commandline

# 或使用 Homebrew (macOS)
brew install allure

# 或使用 Scoop (Windows)
scoop install allure
```

## 快速开始

### 1. 运行测试并生成报告
```bash
# 运行所有测试
pytest

# 运行特定模块的测试
pytest -m login
pytest -m user_management
pytest -m approval_workflow

# 运行特定测试文件
pytest tests/test_002/test_login.py

# 运行特定测试方法
pytest tests/test_002/test_login.py::TestLogin::test_successful_login_admin
```

### 2. 生成和查看报告
```bash
# 生成Allure报告
allure generate reports/allure-results -o reports/allure-report --clean

# 启动报告服务
allure serve reports/allure-results

# 清理旧结果
rm -rf reports/allure-results/* reports/allure-report/*
# Windows用户使用: Remove-Item -Path "reports/allure-results/*", "reports/allure-report/*" -Recurse -Force
```

### 3. 使用HTTP服务器查看报告
```bash
# 启动简单的HTTP服务器查看报告
python -m http.server 8080 --directory reports/allure-report

# 然后在浏览器中访问 http://localhost:8080
```

## 测试运行选项

### 基本用法
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_002/test_login.py

# 运行特定测试方法
pytest tests/test_002/test_login.py::TestLogin::test_successful_login_admin

# 运行指定目录的测试
pytest tests/test_001/

# 运行带标记的测试
pytest -m smoke
pytest -m login
pytest -m "not slow"
```

### 报告选项
```bash
# 清理之前的结果并运行测试
pytest --clean-alluredir

# 详细输出
pytest -v

# 并行运行测试（需要安装 pytest-xdist）
pytest -n 4

# 失败时停止
pytest -x

# 显示最慢的10个测试
pytest --durations=10
```

## 报告功能特性

### 1. 测试分层结构
- **Epic**: 业务领域（如：用户管理系统、审批管理系统）
- **Feature**: 功能模块（如：用户登录、审批工作流）
- **Story**: 用户故事（如：管理员登录、创建审批申请）

### 2. 测试步骤记录
每个测试用例都包含详细的执行步骤，便于问题定位：
```python
@allure.story("用户登录")
@allure.title("管理员成功登录")
def test_admin_login(self):
    with allure.step("导航到登录页面"):
        self.login_page.navigate()
    
    with allure.step("输入管理员凭据"):
        self.login_page.login("admin", "admin123")
    
    with allure.step("验证登录成功"):
        expect(self.page).to_have_url("**/dashboard.html")
```

### 3. 严重程度分级
- **BLOCKER**: 阻塞性问题
- **CRITICAL**: 关键功能
- **NORMAL**: 普通功能
- **MINOR**: 次要功能
- **TRIVIAL**: 微小问题

### 4. 附件支持
- 自动截图（失败时）
- 页面源码
- 浏览器日志
- 自定义附件

## 目录结构

```
Playwright_Project/
├── reports/
│   ├── allure-results/      # 测试结果文件
│   ├── allure-report/       # 生成的HTML报告
│   ├── screenshots/         # 测试截图
│   └── videos/             # 测试录像
├── pytest.ini              # pytest配置
├── utils/
│   └── allure_helper.py     # Allure辅助工具
└── tests/                   # 测试用例（已集成Allure注解）
```

## 最佳实践

### 1. 测试用例注解
```python
@allure.epic("用户管理系统")
@allure.feature("用户登录")
@allure.story("管理员登录")
@allure.title("验证管理员能够成功登录系统")
@allure.description("测试管理员使用正确的用户名和密码登录系统")
@allure.severity(AllureSeverity.CRITICAL)
def test_admin_login_success(self):
    # 测试实现
    pass
```

### 2. 步骤记录
```python
def test_create_user(self):
    with allure.step("管理员登录"):
        self.login_as_admin()
    
    with allure.step("导航到用户管理页面"):
        self.user_page.navigate()
    
    with allure.step("创建新用户"):
        user_data = {"username": "testuser", "role": "user"}
        self.user_page.create_user(user_data)
    
    with allure.step("验证用户创建成功"):
        self.assertTrue(self.user_page.user_exists("testuser"))
```

### 3. 附件添加
```python
# 添加截图
allure.attach(self.page.screenshot(), name="页面截图", attachment_type=allure.attachment_type.PNG)

# 添加文本信息
allure.attach(str(user_data), name="用户数据", attachment_type=allure.attachment_type.TEXT)

# 添加JSON数据
allure.attach(json.dumps(response_data), name="响应数据", attachment_type=allure.attachment_type.JSON)
```

## 故障排除

### 1. Allure 命令未找到
```bash
# 检查安装
allure --version

# 重新安装
npm install -g allure-commandline
```

### 2. 报告生成失败
- 检查 `reports/allure-results` 目录是否存在且包含测试结果文件
- 确保有足够的磁盘空间
- 检查文件权限

### 3. 故障排除
- 检查端口是否被占用
- 尝试使用不同的端口：`allure serve reports/allure-results -p 8082`

### 4. 中文显示问题
确保系统支持 UTF-8 编码，在 Windows 上可能需要设置环境变量：
```bash
set PYTHONIOENCODING=utf-8
```

## 持续集成

在 CI/CD 流水线中集成 Allure 报告：

```yaml
# GitHub Actions 示例
- name: Run tests with Allure
  run: pytest

- name: Generate Allure Report
  run: allure generate reports/allure-results -o reports/allure-report --clean

- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./reports/allure-report
```

## 更多资源

- [Allure 官方文档](https://docs.qameta.io/allure/)
- [Allure Python 集成](https://docs.qameta.io/allure/#_python)
- [pytest-allure 插件](https://github.com/allure-framework/allure-python)