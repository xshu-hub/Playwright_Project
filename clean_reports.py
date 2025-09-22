#!/usr/bin/env python3
"""
Allure报告清理脚本
用于手动清理旧的测试结果和报告，而不是每次运行测试时自动清理
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime


def clean_allure_results(results_dir: str = "reports/allure-results"):
    """清理Allure测试结果文件"""
    results_path = Path(results_dir)
    if results_path.exists():
        print(f"🗑️ 清理测试结果目录: {results_path}")
        shutil.rmtree(results_path)
        results_path.mkdir(parents=True, exist_ok=True)
        print("✅ 测试结果已清理")
    else:
        print(f"⚠️ 测试结果目录不存在: {results_path}")


def clean_allure_report(report_dir: str = "reports/allure-report"):
    """清理Allure HTML报告"""
    report_path = Path(report_dir)
    if report_path.exists():
        print(f"🗑️ 清理HTML报告目录: {report_path}")
        shutil.rmtree(report_path)
        print("✅ HTML报告已清理")
    else:
        print(f"⚠️ HTML报告目录不存在: {report_path}")


def clean_screenshots(screenshots_dir: str = "reports/screenshots"):
    """清理测试截图"""
    screenshots_path = Path(screenshots_dir)
    if screenshots_path.exists():
        print(f"🗑️ 清理截图目录: {screenshots_path}")
        for file in screenshots_path.glob("*"):
            if file.is_file():
                file.unlink()
        print("✅ 截图已清理")
    else:
        print(f"⚠️ 截图目录不存在: {screenshots_path}")


def clean_videos(videos_dir: str = "reports/videos"):
    """清理测试视频"""
    videos_path = Path(videos_dir)
    if videos_path.exists():
        print(f"🗑️ 清理视频目录: {videos_path}")
        for file in videos_path.glob("*"):
            if file.is_file():
                file.unlink()
        print("✅ 视频已清理")
    else:
        print(f"⚠️ 视频目录不存在: {videos_path}")


def backup_history(results_dir: str = "reports/allure-results", backup_dir: str = "reports/history-backup"):
    """备份历史数据"""
    results_path = Path(results_dir)
    backup_path = Path(backup_dir)
    
    if not results_path.exists():
        print(f"⚠️ 测试结果目录不存在: {results_path}")
        return
    
    # 创建备份目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_target = backup_path / f"history_{timestamp}"
    backup_target.mkdir(parents=True, exist_ok=True)
    
    # 备份历史相关文件
    history_files = ["history", "environment.properties", "categories.json"]
    backed_up = False
    
    for file_name in history_files:
        source_file = results_path / file_name
        if source_file.exists():
            if source_file.is_dir():
                shutil.copytree(source_file, backup_target / file_name)
            else:
                shutil.copy2(source_file, backup_target / file_name)
            backed_up = True
    
    if backed_up:
        print(f"📦 历史数据已备份到: {backup_target}")
    else:
        print("⚠️ 没有找到需要备份的历史数据")
        # 删除空的备份目录
        backup_target.rmdir()


def main():
    parser = argparse.ArgumentParser(description="Allure报告清理工具")
    parser.add_argument("--all", action="store_true", help="清理所有报告文件")
    parser.add_argument("--results", action="store_true", help="清理测试结果")
    parser.add_argument("--report", action="store_true", help="清理HTML报告")
    parser.add_argument("--screenshots", action="store_true", help="清理截图")
    parser.add_argument("--videos", action="store_true", help="清理视频")
    parser.add_argument("--backup", action="store_true", help="备份历史数据后再清理")
    
    args = parser.parse_args()
    
    print("🧹 Allure报告清理工具")
    print("=" * 50)
    
    # 如果指定了备份选项，先备份历史数据
    if args.backup:
        backup_history()
        print()
    
    # 如果没有指定任何选项，显示帮助
    if not any([args.all, args.results, args.report, args.screenshots, args.videos]):
        print("请指定要清理的内容:")
        print("  --all          清理所有报告文件")
        print("  --results      清理测试结果")
        print("  --report       清理HTML报告")
        print("  --screenshots  清理截图")
        print("  --videos       清理视频")
        print("  --backup       备份历史数据后再清理")
        print()
        print("示例:")
        print("  python clean_reports.py --all")
        print("  python clean_reports.py --results --report")
        print("  python clean_reports.py --backup --all")
        return
    
    # 执行清理操作
    if args.all:
        clean_allure_results()
        clean_allure_report()
        clean_screenshots()
        clean_videos()
    else:
        if args.results:
            clean_allure_results()
        if args.report:
            clean_allure_report()
        if args.screenshots:
            clean_screenshots()
        if args.videos:
            clean_videos()
    
    print()
    print("🎉 清理完成!")


if __name__ == "__main__":
    main()