@echo off
echo [PIPELINE] ======================== APK 打包生成阶段 ========================
echo [PIPELINE] 开始时间: %date% %time%

REM 切换到脚本目录
cd /d %~dp0

REM 检查 Python 和脚本是否存在
if not exist build_modules.py (
    echo [PIPELINE] [ERROR] build_modules.py 不存在!
    exit /b 1
)

echo [PIPELINE] 执行 APK 打包生成操作...
python build_modules.py apk_build
if %ERRORLEVEL% NEQ 0 (
    echo [PIPELINE] [ERROR] APK 打包生成失败! 错误代码: %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo [PIPELINE] ====================== APK 打包生成阶段完成 ======================
echo [PIPELINE] 结束时间: %date% %time% 