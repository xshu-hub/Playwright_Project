# Web UI 自动化测试系统

这是一个专为 Web UI 自动化测试设计的动态测试网页系统，包含完整的用户登录、跨用户审批流程、用户管理等功能。

## 🚀 功能特性

### 核心功能
- **用户认证系统**：完整的登录/登出功能，支持记住登录状态
- **跨用户审批流程**：申请提交、审批处理、状态跟踪
- **用户管理**：用户列表、角色权限、状态管理
- **仪表板**：数据统计、最近活动、待处理事项
- **响应式设计**：支持桌面端和移动端

### 技术特性
- 纯前端实现，无需后端服务器
- 本地存储数据持久化
- 现代化 UI 设计
- 完整的表单验证
- 实时消息提示
- 动画效果和交互体验

## 📁 项目结构

```
webapp/
├── index.html              # 系统首页
├── README.md              # 项目说明文档
├── css/
│   └── common.css         # 通用样式文件
├── js/
│   └── common.js          # 通用JavaScript工具库
├── pages/
│   ├── login.html         # 登录页面
│   ├── dashboard.html     # 用户仪表板
│   ├── approval-create.html   # 创建审批申请
│   ├── approval-list.html     # 审批申请列表
│   ├── approval-detail.html   # 审批申请详情
│   └── user-management.html   # 用户管理（管理员）
├── assets/                # 静态资源目录
└── data/                  # 数据存储目录（本地存储）
```

## 🎯 测试账号

系统预置了以下测试账号：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | 管理员 | 拥有所有权限，可管理用户 |
| user1 | user123 | 普通用户 | 可提交和处理审批申请 |
| user2 | user123 | 普通用户 | 可提交和处理审批申请 |

## 🔧 使用方法

### 1. 启动系统

#### 方法一：使用 Python HTTP 服务器
```bash
# 在 webapp 目录下执行
python -m http.server 8000
```
然后访问：http://localhost:8000

#### 方法二：使用 Node.js HTTP 服务器
```bash
# 安装 http-server
npm install -g http-server

# 在 webapp 目录下执行
http-server -p 8000
```
然后访问：http://localhost:8000

#### 方法三：直接打开文件
直接用浏览器打开 `index.html` 文件（某些功能可能受限）

### 2. 系统导航

1. **首页** (`index.html`)
   - 系统介绍和快速入口
   - 显示系统功能说明

2. **登录页面** (`pages/login.html`)
   - 用户身份验证
   - 记住登录状态
   - 演示账号快速登录

3. **用户仪表板** (`pages/dashboard.html`)
   - 个人信息展示
   - 待处理事项统计
   - 最近活动记录
   - 快速操作入口

4. **审批系统**
   - **创建申请** (`pages/approval-create.html`)：提交新的审批申请
   - **申请列表** (`pages/approval-list.html`)：查看和管理申请
   - **申请详情** (`pages/approval-detail.html`)：处理具体申请

5. **用户管理** (`pages/user-management.html`)
   - 仅管理员可访问
   - 用户列表和状态管理
   - 添加/编辑/删除用户

## 🧪 自动化测试场景

### 登录测试
- 正确凭据登录
- 错误凭据处理
- 记住登录状态
- 登出功能

### 审批流程测试
- 创建审批申请
- 申请列表筛选
- 审批操作（通过/拒绝）
- 状态变更跟踪

### 用户管理测试
- 权限控制验证
- 用户CRUD操作
- 角色权限测试
- 状态切换测试

### 表单验证测试
- 必填字段验证
- 格式验证（邮箱、密码等）
- 重复数据检查
- 错误消息显示

### UI交互测试
- 响应式布局
- 动画效果
- 消息提示
- 模态框操作

## 📊 数据存储

系统使用浏览器的 `localStorage` 进行数据持久化：

- `users`：用户数据
- `approvals`：审批申请数据
- `currentUser`：当前登录用户
- `rememberLogin`：记住登录状态

### 数据结构示例

```javascript
// 用户数据
{
  "id": "user_123",
  "username": "user1",
  "name": "张三",
  "email": "user1@example.com",
  "password": "user123",
  "role": "user",
  "status": "active",
  "createdAt": "2024-01-01T00:00:00.000Z"
}

// 审批申请数据
{
  "id": "approval_123",
  "title": "请假申请",
  "type": "leave",
  "priority": "medium",
  "description": "因个人事务需要请假",
  "submitterId": "user_123",
  "submitterName": "张三",
  "status": "pending",
  "createdAt": "2024-01-01T00:00:00.000Z",
  "history": []
}
```

## 🎨 自定义配置

### 修改样式
编辑 `css/common.css` 文件来自定义系统外观。

### 添加功能
在 `js/common.js` 中扩展工具函数和数据管理方法。

### 新增页面
参考现有页面结构，在 `pages/` 目录下创建新的 HTML 文件。

## 🔍 调试和开发

### 浏览器开发者工具
- 使用 F12 打开开发者工具
- 在 Console 中查看日志信息
- 在 Application > Local Storage 中查看数据

### 数据重置
```javascript
// 在浏览器控制台中执行以下代码重置所有数据
localStorage.clear();
location.reload();
```

### 添加测试数据
```javascript
// 在浏览器控制台中执行以下代码添加测试数据
Utils.data.initializeData();
```

## 📝 注意事项

1. **浏览器兼容性**：建议使用现代浏览器（Chrome、Firefox、Safari、Edge）
2. **数据持久化**：数据存储在浏览器本地，清除浏览器数据会丢失所有信息
3. **安全性**：这是测试系统，密码以明文存储，请勿用于生产环境
4. **跨域限制**：直接打开文件可能受到浏览器跨域限制，建议使用 HTTP 服务器

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个测试系统！

## 📄 许可证

MIT License - 详见 LICENSE 文件