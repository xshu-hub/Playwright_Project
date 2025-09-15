#!/usr/bin/env python3
"""
智能测试运行器 - 结合环境变量的pytest启动脚本
自动读取PARALLEL_WORKERS环境变量，提供灵活的测试执行方式
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from config.env_config import config_manager

# 获取日志记录器
logger = logging.getLogger(__name__)

def get_parallel_workers():
    """获取并行工作进程数"""
    # 1. 优先使用命令行参数中的-n值（如果存在）
    for i, arg in enumerate(sys.argv):
        if arg == '-n' and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    
    # 2. 使用环境变量PARALLEL_WORKERS
    parallel_workers = config_manager.get_parallel_workers()
    
    # 3. 特殊值处理
    if parallel_workers == 'auto':
        return "auto"  # 自动模式
    elif isinstance(parallel_workers, int):
        if parallel_workers == 1:
            return "0"  # 单线程模式
        elif parallel_workers <= 0:
            return "auto"  # 自动模式
        else:
            return str(parallel_workers)
    else:
        return str(parallel_workers)

def build_pytest_command():
    """构建pytest命令"""
    # 基础命令
    cmd = ["pytest"]
    
    # 获取并行数
    parallel_workers = get_parallel_workers()
    
    # 检查是否已经有-n参数
    has_n_param = any(arg == '-n' for arg in sys.argv[1:])
    
    if not has_n_param:
        # 添加并行参数
        cmd.extend(["-n", parallel_workers])
    
    # 添加其他命令行参数（排除脚本名）
    cmd.extend(sys.argv[1:])
    
    return cmd

def main():
    """主函数"""
    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 构建命令
    cmd = build_pytest_command()
    
    # 显示配置信息
    parallel_workers = get_parallel_workers()
    logger.info(f"🚀 智能测试运行器")
    logger.info(f"📊 并行配置: {parallel_workers} ({'单线程' if parallel_workers == '0' else '自动' if parallel_workers == 'auto' else f'{parallel_workers}个进程'})") 
    logger.info(f"🔧 执行命令: {' '.join(cmd)}")
    logger.info(f"📁 工作目录: {project_root}")
    logger.info("-" * 50)
    
    # 执行命令
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        logger.warning("\n❌ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 执行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()