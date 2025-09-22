@echo off
REM Allure测试报告便捷命令脚本
REM 使用方法：
REM   allure_commands.bat run          - 运行所有测试并生成报告
REM   allure_commands.bat group1       - 运行group1测试
REM   allure_commands.bat group2       - 运行group2测试
REM   allure_commands.bat group3       - 运行group3测试
REM   allure_commands.bat serve        - 启动报告服务器
REM   allure_commands.bat generate     - 仅生成报告
REM   allure_commands.bat clean        - 清理报告文件

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0"
set "ALLURE_RESULTS=%PROJECT_ROOT%reports\allure-results"
set "ALLURE_REPORT=%PROJECT_ROOT%reports\allure-report"

REM 确保目录存在
if not exist "%ALLURE_RESULTS%" mkdir "%ALLURE_RESULTS%"
if not exist "%ALLURE_REPORT%" mkdir "%ALLURE_REPORT%"

if "%1"=="" (
    echo 使用方法：
    echo   %0 run          - 运行所有测试并生成报告
    echo   %0 group1       - 运行group1测试
    echo   %0 group2       - 运行group2测试  
    echo   %0 group3       - 运行group3测试
    echo   %0 serve        - 启动报告服务器
    echo   %0 generate     - 仅生成报告
    echo   %0 clean        - 清理报告文件
    goto :eof
)

if "%1"=="run" (
    echo 运行所有测试用例...
    python -m pytest testcase --alluredir="%ALLURE_RESULTS%" -v --tb=short
    if !errorlevel! equ 0 (
        echo 测试完成，生成报告...
        call :generate_report
    ) else (
        echo 测试执行失败，但仍生成报告...
        call :generate_report
    )
    goto :eof
)

if "%1"=="group1" (
    echo 运行Group1测试用例...
    python -m pytest testcase -m group1 --alluredir="%ALLURE_RESULTS%" -v --tb=short
    if !errorlevel! equ 0 (
        echo 测试完成，生成报告...
        call :generate_report
    ) else (
        echo 测试执行失败，但仍生成报告...
        call :generate_report
    )
    goto :eof
)

if "%1"=="group2" (
    echo 运行Group2测试用例...
    python -m pytest testcase -m group2 --alluredir="%ALLURE_RESULTS%" -v --tb=short
    if !errorlevel! equ 0 (
        echo 测试完成，生成报告...
        call :generate_report
    ) else (
        echo 测试执行失败，但仍生成报告...
        call :generate_report
    )
    goto :eof
)

if "%1"=="group3" (
    echo 运行Group3测试用例...
    python -m pytest testcase -m group3 --alluredir="%ALLURE_RESULTS%" -v --tb=short
    if !errorlevel! equ 0 (
        echo 测试完成，生成报告...
        call :generate_report
    ) else (
        echo 测试执行失败，但仍生成报告...
        call :generate_report
    )
    goto :eof
)

if "%1"=="serve" (
    echo 启动Allure报告服务器...
    allure serve "%ALLURE_RESULTS%" --port 8080
    goto :eof
)

if "%1"=="generate" (
    call :generate_report
    goto :eof
)

if "%1"=="clean" (
    echo 清理报告文件...
    if exist "%ALLURE_RESULTS%" rmdir /s /q "%ALLURE_RESULTS%"
    if exist "%ALLURE_REPORT%" rmdir /s /q "%ALLURE_REPORT%"
    mkdir "%ALLURE_RESULTS%"
    mkdir "%ALLURE_REPORT%"
    echo 报告文件已清理
    goto :eof
)

echo 未知命令: %1
goto :eof

:generate_report
echo 生成Allure报告...
allure generate "%ALLURE_RESULTS%" -o "%ALLURE_REPORT%" --clean
if !errorlevel! equ 0 (
    echo 报告已生成: %ALLURE_REPORT%\index.html
    echo 正在打开报告...
    start "" "%ALLURE_REPORT%\index.html"
) else (
    echo 生成报告失败，请检查Allure CLI是否已安装
    echo 安装方法: https://docs.qameta.io/allure/#_installing_a_commandline
)
goto :eof