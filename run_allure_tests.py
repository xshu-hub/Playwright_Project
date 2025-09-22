#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Allure测试运行脚本
提供便捷的测试执行和报告生成功能
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


class AllureTestRunner:
    """Allure测试运行器"""
    
    def __init__(self, project_root: str = None):
        """
        初始化测试运行器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root) if project_root else Path(__file__).parent
        self.allure_results_dir = self.project_root / "reports" / "allure-results"
        self.allure_report_dir = self.project_root / "reports" / "allure-report"
        
        # 确保目录存在
        self.allure_results_dir.mkdir(parents=True, exist_ok=True)
        self.allure_report_dir.mkdir(parents=True, exist_ok=True)
    
    def run_tests(self, test_path: str = None, markers: str = None, verbose: bool = True, 
                  clean_results: bool = True) -> bool:
        """
        运行测试用例
        
        Args:
            test_path: 测试路径，默认为testcase目录
            markers: pytest标记过滤器
            verbose: 是否显示详细输出
            clean_results: 是否清理旧的测试结果
            
        Returns:
            测试是否成功
        """
        try:
            # 清理旧结果
            if clean_results:
                self._clean_allure_results()
            
            # 构建pytest命令
            cmd = [
                sys.executable, "-m", "pytest",
                "--alluredir", str(self.allure_results_dir),
                "--tb=short"
            ]
            
            # 添加测试路径
            if test_path:
                cmd.append(test_path)
            else:
                cmd.append("testcase")
            
            # 添加标记过滤器
            if markers:
                cmd.extend(["-m", markers])
            
            # 添加详细输出
            if verbose:
                cmd.append("-v")
            
            print(f"执行命令: {' '.join(cmd)}")
            print(f"Allure结果目录: {self.allure_results_dir}")
            
            # 执行测试
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=False)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"运行测试失败: {e}")
            return False
    
    def generate_report(self, open_browser: bool = True) -> bool:
        """
        生成Allure报告
        
        Args:
            open_browser: 是否自动打开浏览器
            
        Returns:
            报告生成是否成功
        """
        try:
            # 检查allure命令是否可用
            if not self._check_allure_command():
                print("错误: 未找到allure命令，请先安装Allure CLI")
                print("安装方法: https://docs.qameta.io/allure/#_installing_a_commandline")
                return False
            
            # 生成报告
            cmd = [
                "allure", "generate", 
                str(self.allure_results_dir),
                "-o", str(self.allure_report_dir),
                "--clean"
            ]
            
            print(f"生成报告命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"生成报告失败: {result.stderr}")
                return False
            
            print(f"Allure报告已生成: {self.allure_report_dir}")
            
            # 打开浏览器
            if open_browser:
                self._open_report()
            
            return True
            
        except Exception as e:
            print(f"生成报告失败: {e}")
            return False
    
    def serve_report(self, port: int = 8080) -> bool:
        """
        启动Allure报告服务器
        
        Args:
            port: 服务器端口
            
        Returns:
            服务器启动是否成功
        """
        try:
            if not self._check_allure_command():
                print("错误: 未找到allure命令")
                return False
            
            cmd = [
                "allure", "serve", 
                str(self.allure_results_dir),
                "--port", str(port)
            ]
            
            print(f"启动报告服务器: {' '.join(cmd)}")
            print(f"报告将在 http://localhost:{port} 上提供")
            
            subprocess.run(cmd)
            return True
            
        except KeyboardInterrupt:
            print("\n服务器已停止")
            return True
        except Exception as e:
            print(f"启动服务器失败: {e}")
            return False
    
    def run_and_report(self, test_path: str = None, markers: str = None, 
                       open_browser: bool = True) -> bool:
        """
        运行测试并生成报告
        
        Args:
            test_path: 测试路径
            markers: pytest标记过滤器
            open_browser: 是否自动打开浏览器
            
        Returns:
            整个流程是否成功
        """
        print("=" * 60)
        print("开始运行Allure测试")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 运行测试
        test_success = self.run_tests(test_path, markers)
        
        print("\n" + "=" * 60)
        print("生成Allure报告")
        print("=" * 60)
        
        # 生成报告
        report_success = self.generate_report(open_browser)
        
        print("\n" + "=" * 60)
        print("测试完成")
        print(f"测试结果: {'成功' if test_success else '失败'}")
        print(f"报告生成: {'成功' if report_success else '失败'}")
        print("=" * 60)
        
        return test_success and report_success
    
    def _clean_allure_results(self):
        """清理旧的Allure结果"""
        try:
            import shutil
            if self.allure_results_dir.exists():
                shutil.rmtree(self.allure_results_dir)
                self.allure_results_dir.mkdir(parents=True, exist_ok=True)
                print(f"已清理旧的测试结果: {self.allure_results_dir}")
        except Exception as e:
            print(f"清理旧结果失败: {e}")
    
    def _check_allure_command(self) -> bool:
        """检查allure命令是否可用"""
        try:
            result = subprocess.run(["allure", "--version"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _open_report(self):
        """打开报告"""
        try:
            report_index = self.allure_report_dir / "index.html"
            if report_index.exists():
                import webbrowser
                webbrowser.open(f"file://{report_index.absolute()}")
                print(f"已在浏览器中打开报告: {report_index}")
        except Exception as e:
            print(f"打开报告失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Allure测试运行器")
    parser.add_argument("--path", "-p", help="测试路径")
    parser.add_argument("--markers", "-m", help="pytest标记过滤器")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--serve", "-s", action="store_true", help="启动报告服务器")
    parser.add_argument("--port", type=int, default=8080, help="服务器端口")
    parser.add_argument("--generate-only", "-g", action="store_true", help="仅生成报告")
    
    args = parser.parse_args()
    
    runner = AllureTestRunner()
    
    if args.serve:
        # 启动服务器模式
        runner.serve_report(args.port)
    elif args.generate_only:
        # 仅生成报告
        runner.generate_report(not args.no_browser)
    else:
        # 运行测试并生成报告
        runner.run_and_report(
            test_path=args.path,
            markers=args.markers,
            open_browser=not args.no_browser
        )


if __name__ == "__main__":
    main()