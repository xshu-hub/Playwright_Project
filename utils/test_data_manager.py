"""测试数据管理器

提供统一的测试数据管理功能：
1. 支持JSON和Excel格式的数据文件
2. 数据缓存和动态加载
3. 数据验证和错误处理
4. 环境变量和配置管理
5. 数据过滤和查询功能
"""
import json
import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from loguru import logger
from dataclasses import dataclass
from enum import Enum
import re
import jsonschema
from jsonschema import validate, ValidationError


class DataFormat(Enum):
    """数据格式枚举"""
    JSON = "json"
    EXCEL = "excel"
    CSV = "csv"


@dataclass
class TestUser:
    """测试用户数据类"""
    username: str
    password: str
    name: str
    email: str
    role: str
    status: str = "active"
    description: str = ""


@dataclass
class TestData:
    """测试数据基类"""
    id: str
    name: str
    description: str
    data: Dict[str, Any]
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TestDataManager:
    """测试数据管理器"""
    
    def __init__(self, data_dir: str = "testdata"):
        """
        初始化测试数据管理器
        
        Args:
            data_dir: 测试数据目录路径
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 数据缓存
        self._cache = {}
        self._users_cache = {}
        self._config_cache = {}
        
        # 数据验证模式
        self._validation_schemas = self._load_validation_schemas()
        
        # 支持的文件格式
        self.supported_formats = {
            '.json': self._load_json,
            '.xlsx': self._load_excel,
            '.xls': self._load_excel,
            '.csv': self._load_csv
        }
        
        logger.info(f"测试数据管理器初始化完成，数据目录: {self.data_dir}")
        
        # 验证核心数据文件
        self._validate_core_files()
    
    def _load_validation_schemas(self) -> Dict[str, Dict]:
        """加载数据验证模式"""
        schemas = {
            "users": {
                "type": "object",
                "properties": {
                    "users": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "username": {"type": "string", "minLength": 1},
                                "password": {"type": "string", "minLength": 1},
                                "name": {"type": "string"},
                                "email": {"type": "string", "format": "email"},
                                "role": {"type": "string", "enum": ["admin", "user", "manager"]},
                                "status": {"type": "string", "enum": ["active", "inactive"]}
                            },
                            "required": ["username", "password", "name", "email", "role"]
                        }
                    }
                },
                "required": ["users"]
            },
            "config": {
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "object",
                        "patternProperties": {
                            ".*": {
                                "type": "object",
                                "properties": {
                                    "base_url": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
        return schemas
    
    def _validate_core_files(self):
        """验证核心数据文件的完整性"""
        core_files = {
            "users.json": "users",
            "config.json": "config"
        }
        
        for filename, schema_key in core_files.items():
            file_path = self.data_dir / filename
            if not file_path.exists():
                logger.warning(f"核心数据文件不存在: {filename}")
                continue
                
            try:
                data = self._load_json(file_path)
                if data and schema_key in self._validation_schemas:
                    self._validate_data(data, self._validation_schemas[schema_key], filename)
                    logger.info(f"数据文件验证通过: {filename}")
            except Exception as e:
                logger.error(f"验证数据文件失败 {filename}: {e}")
    
    def _validate_data(self, data: Dict, schema: Dict, source: str = "unknown"):
        """验证数据格式"""
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            error_msg = f"数据验证失败 ({source}): {e.message}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"数据验证异常 ({source}): {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """加载JSON文件"""
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 验证文件大小（防止过大文件）
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                logger.warning(f"数据文件过大: {file_path} ({file_path.stat().st_size} bytes)")
                
            logger.debug(f"成功加载JSON文件: {file_path}")
            return data
            
        except FileNotFoundError as e:
            logger.error(f"JSON文件不存在: {file_path}")
            raise e
        except json.JSONDecodeError as e:
            logger.error(f"JSON文件格式错误: {file_path}, 错误: {e}")
            raise ValueError(f"JSON格式错误: {e}")
        except PermissionError as e:
            logger.error(f"没有权限读取文件: {file_path}")
            raise e
        except Exception as e:
            logger.error(f"读取JSON文件时发生未知错误: {file_path}, 错误: {e}")
            raise e
    
    def _load_excel(self, file_path: Path) -> Dict[str, Any]:
        """加载Excel文件"""
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"Excel文件不存在: {file_path}")
            
            # 验证文件扩展名
            if file_path.suffix.lower() not in ['.xlsx', '.xls']:
                raise ValueError(f"不支持的Excel文件格式: {file_path.suffix}")
            
            # 验证文件大小
            file_size = file_path.stat().st_size
            if file_size > 50 * 1024 * 1024:  # 50MB
                raise ValueError(f"Excel文件过大: {file_size} bytes (最大支持50MB)")
            
            # 读取所有工作表
            excel_data = pd.read_excel(file_path, sheet_name=None)
            
            if not excel_data:
                raise ValueError(f"Excel文件为空或无法读取: {file_path}")
            
            # 转换为字典格式
            result = {}
            for sheet_name, df in excel_data.items():
                if df.empty:
                    logger.warning(f"工作表 '{sheet_name}' 为空")
                    result[sheet_name] = []
                else:
                    # 检查必要的列
                    if sheet_name in ['Users', 'FormData', 'ApprovalData']:
                        self._validate_excel_sheet(df, sheet_name)
                    
                    # 将DataFrame转换为字典列表，处理NaN值
                    records = df.fillna('').to_dict('records')
                    result[sheet_name] = records
            
            logger.debug(f"成功加载Excel文件: {file_path}, 工作表: {list(result.keys())}")
            return result
            
        except FileNotFoundError as e:
            logger.error(f"Excel文件不存在: {file_path}")
            raise e
        except pd.errors.EmptyDataError:
            logger.error(f"Excel文件为空: {file_path}")
            raise ValueError(f"Excel文件为空: {file_path}")
        except pd.errors.ParserError as e:
            logger.error(f"Excel文件解析错误: {file_path}, 错误: {e}")
            raise ValueError(f"Excel文件格式错误: {e}")
        except PermissionError as e:
            logger.error(f"没有权限读取Excel文件: {file_path}")
            raise e
        except Exception as e:
            logger.error(f"加载Excel文件失败: {file_path}, 错误: {e}")
            raise e
    
    def _validate_excel_sheet(self, df: pd.DataFrame, sheet_name: str):
        """验证Excel工作表结构"""
        required_columns = {
            'Users': ['username', 'password', 'name', 'email', 'role'],
            'FormData': ['test_case', 'name', 'username', 'email', 'password', 'role'],
            'ApprovalData': ['request_id', 'requester', 'request_type', 'status', 'priority'],
            'LoginScenarios': ['scenario', 'username', 'password', 'expected_result']
        }
        
        if sheet_name in required_columns:
            missing_columns = set(required_columns[sheet_name]) - set(df.columns)
            if missing_columns:
                if sheet_name == 'LoginScenarios':
                    logger.warning(f"工作表 '{sheet_name}' 缺少推荐列: {missing_columns}")
                else:
                    raise ValueError(f"工作表 '{sheet_name}' 缺少必要列: {missing_columns}")
            
            # 检查数据行数
            if len(df) == 0:
                logger.warning(f"工作表 '{sheet_name}' 没有数据行")
            elif len(df) > 1000:
                logger.warning(f"工作表 '{sheet_name}' 数据行数过多: {len(df)} 行")
    
    def _load_csv(self, file_path: Path) -> Dict[str, Any]:
        """加载CSV文件"""
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"CSV文件不存在: {file_path}")
            
            # 验证文件扩展名
            if file_path.suffix.lower() != '.csv':
                raise ValueError(f"不支持的CSV文件格式: {file_path.suffix}")
            
            # 验证文件大小
            file_size = file_path.stat().st_size
            if file_size > 20 * 1024 * 1024:  # 20MB
                raise ValueError(f"CSV文件过大: {file_size} bytes (最大支持20MB)")
            
            df = pd.read_csv(file_path, encoding='utf-8')
            
            if df.empty:
                logger.warning(f"CSV文件为空: {file_path}")
                return {"data": []}
            
            # 处理NaN值并转换为字典列表
            records = df.fillna('').to_dict('records')
            
            logger.debug(f"成功加载CSV文件: {file_path}, 数据行数: {len(records)}")
            return {"data": records}
            
        except FileNotFoundError as e:
            logger.error(f"CSV文件不存在: {file_path}")
            raise e
        except pd.errors.EmptyDataError:
            logger.error(f"CSV文件为空: {file_path}")
            raise ValueError(f"CSV文件为空: {file_path}")
        except pd.errors.ParserError as e:
            logger.error(f"CSV文件解析错误: {file_path}, 错误: {e}")
            raise ValueError(f"CSV文件格式错误: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"CSV文件编码错误: {file_path}, 错误: {e}")
            raise ValueError(f"CSV文件编码错误，请使用UTF-8编码: {e}")
        except PermissionError as e:
            logger.error(f"没有权限读取CSV文件: {file_path}")
            raise e
        except Exception as e:
            logger.error(f"加载CSV文件失败: {file_path}, 错误: {e}")
            raise e
    
    def load_data_file(self, filename: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        加载数据文件
        
        Args:
            filename: 文件名
            use_cache: 是否使用缓存
            
        Returns:
            数据字典
        """
        file_path = self.data_dir / filename
        
        # 检查缓存
        if use_cache and str(file_path) in self._cache:
            logger.debug(f"从缓存加载数据: {filename}")
            return self._cache[str(file_path)]
        
        # 检查文件是否存在
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        # 根据文件扩展名选择加载方法
        file_ext = file_path.suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"不支持的文件格式: {file_ext}")
        
        # 加载数据
        data = self.supported_formats[file_ext](file_path)
        
        # 缓存数据
        if use_cache:
            self._cache[str(file_path)] = data
        
        return data
    
    def get_users(self, filename: str = "users.json", role: str = None, status: str = None) -> List[TestUser]:
        """
        获取用户数据
        
        Args:
            filename: 用户数据文件名
            role: 过滤角色
            status: 过滤状态
            
        Returns:
            用户列表
        """
        cache_key = f"{filename}_{role}_{status}"
        
        # 检查缓存
        if cache_key in self._users_cache:
            return self._users_cache[cache_key]
        
        # 加载用户数据
        data = self.load_data_file(filename)
        users_data = data.get('users', [])
        
        # 转换为TestUser对象
        users = []
        for user_data in users_data:
            user = TestUser(**user_data)
            
            # 应用过滤条件
            if role and user.role != role:
                continue
            if status and user.status != status:
                continue
                
            users.append(user)
        
        # 缓存结果
        self._users_cache[cache_key] = users
        
        logger.debug(f"加载用户数据: {len(users)} 个用户")
        return users
    
    def get_user_by_username(self, username: str, filename: str = "users.json") -> Optional[TestUser]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            filename: 用户数据文件名
            
        Returns:
            用户对象或None
        """
        if not username or not isinstance(username, str):
            raise ValueError("用户名不能为空且必须是字符串")
        
        username = username.strip()
        if not username:
            raise ValueError("用户名不能为空白字符")
        
        try:
            users = self.get_users(filename)
            
            if not users:
                logger.warning(f"用户数据文件 {filename} 中没有用户数据")
                return None
            
            for user in users:
                if user.username == username:
                    return user
            
            logger.warning(f"未找到用户: {username}")
            return None
            
        except Exception as e:
            logger.error(f"获取用户信息时发生错误: {e}")
            return None
    
    def get_users_by_role(self, role: str, filename: str = "users.json") -> List[TestUser]:
        """
        根据角色获取用户列表
        
        Args:
            role: 用户角色
            filename: 用户数据文件名
            
        Returns:
            用户列表
        """
        return self.get_users(filename, role=role)
    
    def get_test_data(self, data_type: str, filename: str = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        获取测试数据
        
        Args:
            data_type: 数据类型
            filename: 文件名（可选）
            filters: 过滤条件
            
        Returns:
            测试数据列表
        """
        if filename is None:
            filename = f"{data_type}.json"
        
        data = self.load_data_file(filename)
        
        # 获取指定类型的数据
        if data_type in data:
            test_data = data[data_type]
        elif 'data' in data:
            test_data = data['data']
        else:
            test_data = data
        
        # 确保返回列表格式
        if not isinstance(test_data, list):
            test_data = [test_data]
        
        # 应用过滤条件
        if filters:
            filtered_data = []
            for item in test_data:
                match = True
                for key, value in filters.items():
                    if key not in item or item[key] != value:
                        match = False
                        break
                if match:
                    filtered_data.append(item)
            test_data = filtered_data
        
        logger.debug(f"获取测试数据: {data_type}, 数量: {len(test_data)}")
        return test_data
    
    def get_config(self, config_name: str, filename: str = "config.json") -> Dict[str, Any]:
        """
        获取配置数据
        
        Args:
            config_name: 配置名称
            filename: 配置文件名
            
        Returns:
            配置字典
        """
        cache_key = f"{filename}_{config_name}"
        
        # 检查缓存
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        data = self.load_data_file(filename)
        config = data.get(config_name, {})
        
        # 处理环境变量替换
        config = self._resolve_env_variables(config)
        
        # 缓存配置
        self._config_cache[cache_key] = config
        
        return config
    
    def _resolve_env_variables(self, data: Any) -> Any:
        """
        解析环境变量
        
        Args:
            data: 原始数据
            
        Returns:
            解析后的数据
        """
        if isinstance(data, str):
            # 查找环境变量模式 ${VAR_NAME} 或 $VAR_NAME
            pattern = r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)'
            
            def replace_env_var(match):
                var_name = match.group(1) or match.group(2)
                return os.getenv(var_name, match.group(0))
            
            return re.sub(pattern, replace_env_var, data)
        
        elif isinstance(data, dict):
            return {key: self._resolve_env_variables(value) for key, value in data.items()}
        
        elif isinstance(data, list):
            return [self._resolve_env_variables(item) for item in data]
        
        return data
    
    def get_url_config(self, env: str = "test") -> Dict[str, str]:
        """
        获取URL配置
        
        Args:
            env: 环境名称
            
        Returns:
            URL配置字典
        """
        config = self.get_config("urls")
        return config.get(env, config.get("default", {}))
    
    def get_base_url(self, env: str = "test") -> str:
        """
        获取基础URL
        
        Args:
            env: 环境名称
            
        Returns:
            基础URL
        """
        url_config = self.get_url_config(env)
        return url_config.get("base_url", "http://localhost:8080")
    
    def validate_data_file(self, filename: str) -> bool:
        """
        验证数据文件格式
        
        Args:
            filename: 文件名
            
        Returns:
            验证结果
        """
        try:
            data = self.load_data_file(filename, use_cache=False)
            
            # 基本格式验证
            if not isinstance(data, dict):
                logger.error(f"数据文件格式错误: {filename} - 根节点必须是字典")
                return False
            
            # 用户数据验证
            if 'users' in data:
                users_data = data['users']
                if not isinstance(users_data, list):
                    logger.error(f"用户数据格式错误: {filename} - users必须是列表")
                    return False
                
                required_fields = ['username', 'password', 'name', 'email', 'role']
                for i, user in enumerate(users_data):
                    for field in required_fields:
                        if field not in user:
                            logger.error(f"用户数据缺少必需字段: {filename} - 用户{i} 缺少 {field}")
                            return False
            
            logger.info(f"数据文件验证通过: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"数据文件验证失败: {filename}, 错误: {e}")
            return False
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        self._users_cache.clear()
        self._config_cache.clear()
        logger.info("测试数据缓存已清空")
    
    def reload_data(self, filename: str = None):
        """
        重新加载数据
        
        Args:
            filename: 文件名，为None时重新加载所有数据
        """
        if filename:
            # 清除指定文件的缓存
            file_path = str(self.data_dir / filename)
            if file_path in self._cache:
                del self._cache[file_path]
            
            # 清除相关的用户和配置缓存
            keys_to_remove = []
            for key in self._users_cache.keys():
                if key.startswith(filename):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del self._users_cache[key]
            
            keys_to_remove = []
            for key in self._config_cache.keys():
                if key.startswith(filename):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del self._config_cache[key]
            
            logger.info(f"重新加载数据文件: {filename}")
        else:
            # 清空所有缓存
            self.clear_cache()
            logger.info("重新加载所有数据文件")
    
    def list_data_files(self) -> List[str]:
        """
        列出所有数据文件
        
        Returns:
            文件名列表
        """
        files = []
        for file_path in self.data_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                files.append(file_path.name)
        return sorted(files)
    
    def get_data_file_info(self, filename: str) -> Dict[str, Any]:
        """
        获取数据文件信息
        
        Args:
            filename: 文件名
            
        Returns:
            文件信息字典
        """
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        info = {
            'filename': filename,
            'path': str(file_path),
            'size': file_path.stat().st_size,
            'modified': file_path.stat().st_mtime,
            'format': file_path.suffix.lower(),
            'cached': str(file_path) in self._cache
        }
        
        # 尝试获取数据结构信息
        try:
            data = self.load_data_file(filename)
            info['keys'] = list(data.keys()) if isinstance(data, dict) else []
            info['valid'] = True
        except Exception as e:
            info['keys'] = []
            info['valid'] = False
            info['error'] = str(e)
        
        return info


# 全局测试数据管理器实例
test_data_manager = TestDataManager()