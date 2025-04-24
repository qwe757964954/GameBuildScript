@echo off
echo [PIPELINE] ============================ Git 更新阶段 ============================
echo [PIPELINE] 开始时间: %date% %time%

REM 切换到脚本目录
cd /d %~dp0

REM 检查 Python 和脚本是否存在
if not exist build_modules.py (
    echo [PIPELINE] [ERROR] build_modules.py 不存在!
    exit /b 1
)

echo [PIPELINE] 执行 Git 更新操作...
python build_modules.py git_update
if %ERRORLEVEL% NEQ 0 (
    echo [PIPELINE] [ERROR] Git 更新失败! 错误代码: %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo [PIPELINE] ========================== Git 更新阶段完成 ==========================
echo [PIPELINE] 结束时间: %date% %time% 