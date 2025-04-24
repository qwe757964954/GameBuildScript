@echo off
echo [INFO] 开始执行 Python 构建脚本...

REM 切换到当前目录（确保bat文件可以任意位置运行）
cd /d %~dp0

REM 检查是否已安装 Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] 未检测到 Python，请检查环境变量！
    exit /b 1
)

REM 执行 Python 脚本
python main.py

echo [INFO] Python 构建执行完成。
