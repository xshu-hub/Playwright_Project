// 通用工具函数
class Utils {
    // 本地存储管理
    static storage = {
        set(key, value) {
            localStorage.setItem(key, JSON.stringify(value));
        },
        
        get(key) {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        },
        
        remove(key) {
            localStorage.removeItem(key);
        },
        
        clear() {
            localStorage.clear();
        }
    };
    
    // 用户会话管理
    static auth = {
        login(user) {
            Utils.storage.set('currentUser', user);
            Utils.storage.set('loginTime', new Date().toISOString());
        },
        
        logout() {
            Utils.storage.remove('currentUser');
            Utils.storage.remove('loginTime');
            window.location.href = 'login.html';
        },
        
        getCurrentUser() {
            return Utils.storage.get('currentUser');
        },
        
        isLoggedIn() {
            return this.getCurrentUser() !== null;
        },
        
        requireAuth() {
            if (!this.isLoggedIn()) {
                window.location.href = 'login.html';
                return false;
            }
            return true;
        }
    };
    
    // 数据管理
    static data = {
        // 获取用户列表
        getUsers() {
            return Utils.storage.get('users') || [
                { id: 1, username: 'admin', password: 'admin123', role: 'admin', name: '管理员', email: 'admin@test.com' },
                { id: 2, username: 'user1', password: 'user123', role: 'user', name: '张三', email: 'zhangsan@test.com' },
                { id: 3, username: 'user2', password: 'user123', role: 'user', name: '李四', email: 'lisi@test.com' },
                { id: 4, username: 'manager', password: 'manager123', role: 'manager', name: '王经理', email: 'manager@test.com' }
            ];
        },
        
        // 保存用户列表
        saveUsers(users) {
            Utils.storage.set('users', users);
        },
        
        // 添加用户
        addUser(user) {
            const users = this.getUsers();
            user.id = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            user.createdAt = new Date().toISOString();
            users.push(user);
            this.saveUsers(users);
            return user;
        },
        
        // 更新用户
        updateUser(userId, updates) {
            const users = this.getUsers();
            const userIndex = users.findIndex(u => u.id === userId);
            if (userIndex === -1) {
                throw new Error('用户不存在');
            }
            users[userIndex] = { ...users[userIndex], ...updates, updatedAt: new Date().toISOString() };
            this.saveUsers(users);
            return users[userIndex];
        },
        
        // 删除用户
        deleteUser(userId) {
            const users = this.getUsers();
            const filteredUsers = users.filter(u => u.id !== userId);
            if (filteredUsers.length === users.length) {
                throw new Error('用户不存在');
            }
            this.saveUsers(filteredUsers);
        },
        
        // 根据用户名查找用户
        findUserByUsername(username) {
            const users = this.getUsers();
            return users.find(user => user.username === username);
        },
        
        // 获取审批申请列表
        getApprovals() {
            return Utils.storage.get('approvals') || [];
        },
        
        // 保存审批申请
        saveApprovals(approvals) {
            Utils.storage.set('approvals', approvals);
        },
        
        // 获取单个申请
        getApproval(id) {
            const approvals = this.getApprovals();
            return approvals.find(approval => approval.id === id);
        },
        
        // 添加新的审批申请
        addApproval(approval) {
            const approvals = this.getApprovals();
            approval.id = 'approval_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            approval.status = 'pending';
            approval.createdAt = new Date().toISOString();
            approval.updatedAt = new Date().toISOString();
            approval.history = [];
            approvals.push(approval);
            this.saveApprovals(approvals);
            return approval;
        },
        
        // 更新申请
        updateApproval(id, updates) {
            const approvals = this.getApprovals();
            const approvalIndex = approvals.findIndex(a => a.id === id);
            if (approvalIndex === -1) {
                throw new Error('申请不存在');
            }
            approvals[approvalIndex] = { ...approvals[approvalIndex], ...updates, updatedAt: new Date().toISOString() };
            this.saveApprovals(approvals);
            return approvals[approvalIndex];
        },
        
        // 删除申请
        deleteApproval(id) {
            const approvals = this.getApprovals();
            const filteredApprovals = approvals.filter(a => a.id !== id);
            if (filteredApprovals.length === approvals.length) {
                throw new Error('申请不存在');
            }
            this.saveApprovals(filteredApprovals);
        },
        
        // 处理审批
        processApproval(id, action, comment, reviewer) {
            const approvals = this.getApprovals();
            const approvalIndex = approvals.findIndex(a => a.id === id);
            if (approvalIndex === -1) {
                throw new Error('申请不存在');
            }
            
            const approval = approvals[approvalIndex];
            if (approval.status !== 'pending') {
                throw new Error('申请已处理，无法重复审批');
            }
            
            // 更新状态
            approval.status = action;
            approval.updatedAt = new Date().toISOString();
            approval.reviewer = reviewer.username;
            approval.reviewerName = reviewer.name;
            approval.reviewedAt = new Date().toISOString();
            approval.reviewComment = comment;
            
            // 添加历史记录
            if (!approval.history) {
                approval.history = [];
            }
            approval.history.push({
                action: action,
                reviewer: reviewer.username,
                reviewerName: reviewer.name,
                comment: comment,
                timestamp: new Date().toISOString()
            });
            
            this.saveApprovals(approvals);
            return approval;
        },
        
        // 更新审批状态（保持向后兼容）
        updateApprovalStatus(id, status, comment = '') {
            const approvals = this.getApprovals();
            const approval = approvals.find(a => a.id === id);
            if (approval) {
                approval.status = status;
                approval.approveTime = new Date().toISOString();
                approval.approveComment = comment;
                approval.approver = Utils.auth.getCurrentUser().username;
                this.saveApprovals(approvals);
            }
            return approval;
        }
    };
    
    // UI工具函数
    static ui = {
        // 显示消息提示
        showMessage(message, type = 'info') {
            const messageDiv = document.createElement('div');
            messageDiv.className = `alert alert-${type}`;
            messageDiv.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 9999;
                animation: slideIn 0.3s ease-out;
            `;
            
            switch(type) {
                case 'success':
                    messageDiv.style.background = 'linear-gradient(45deg, #28a745, #20c997)';
                    break;
                case 'error':
                    messageDiv.style.background = 'linear-gradient(45deg, #dc3545, #fd7e14)';
                    break;
                case 'warning':
                    messageDiv.style.background = 'linear-gradient(45deg, #ffc107, #fd7e14)';
                    break;
                default:
                    messageDiv.style.background = 'linear-gradient(45deg, #667eea, #764ba2)';
            }
            
            messageDiv.textContent = message;
            document.body.appendChild(messageDiv);
            
            setTimeout(() => {
                messageDiv.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => {
                    document.body.removeChild(messageDiv);
                }, 300);
            }, 3000);
        },
        
        // 确认对话框
        confirm(message, callback) {
            if (window.confirm(message)) {
                callback();
            }
        },
        
        // 格式化日期
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        // 获取状态显示文本
        getStatusText(status) {
            const statusMap = {
                'pending': '待审批',
                'approved': '已通过',
                'rejected': '已拒绝'
            };
            return statusMap[status] || status;
        },
        
        // 获取角色显示文本
        getRoleText(role) {
            const roleMap = {
                'admin': '管理员',
                'manager': '经理',
                'user': '普通用户'
            };
            return roleMap[role] || role;
        }
    };
    
    // 表单验证
    static validation = {
        // 验证必填字段
        required(value, fieldName) {
            if (!value || value.trim() === '') {
                throw new Error(`${fieldName}不能为空`);
            }
            return true;
        },
        
        // 验证邮箱格式
        email(value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                throw new Error('邮箱格式不正确');
            }
            return true;
        },
        
        // 验证密码强度
        password(value) {
            if (value.length < 6) {
                throw new Error('密码长度至少6位');
            }
            return true;
        }
    };
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// 初始化数据
document.addEventListener('DOMContentLoaded', function() {
    // 确保基础数据存在
    if (!Utils.storage.get('users')) {
        Utils.data.saveUsers(Utils.data.getUsers());
    }
    
    if (!Utils.storage.get('approvals')) {
        Utils.data.saveApprovals([]);
    }
});