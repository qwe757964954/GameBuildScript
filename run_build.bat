@echo off
echo [PIPELINE] ============================ Build Process Started ============================
echo [PIPELINE] Current time: %date% %time%
echo [PIPELINE] Working directory: %cd%

cd /d %~dp0
echo [PIPELINE] Changed to script directory: %cd%

REM Check if Python exists
echo [PIPELINE] Checking Python installation...
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [PIPELINE] [ERROR] Python not found. Please check PATH settings.
    exit /b 1
) ELSE (
    python --version
    echo [PIPELINE] Python installation verified.
)

REM Check if build_params.json exists
echo [PIPELINE] Checking for build parameters file...
if not exist build_params.json (
    echo [PIPELINE] [ERROR] build_params.json not found!
    exit /b 1
) ELSE (
    echo [PIPELINE] Found build_params.json file.
    type build_params.json
)

REM 执行各个构建阶段
echo [PIPELINE] ======================== 开始执行构建流程 ========================

echo [PIPELINE] [1/4] Git 更新阶段
call run_git_update.bat
IF ERRORLEVEL 1 (
    echo [PIPELINE] [ERROR] Git 更新阶段失败！
    exit /b %ERRORLEVEL%
)

echo [PIPELINE] [2/4] Cocos 工程生成阶段
call run_cocos_build.bat
IF ERRORLEVEL 1 (
    echo [PIPELINE] [ERROR] Cocos 工程生成阶段失败！
    exit /b %ERRORLEVEL%
)

echo [PIPELINE] [3/4] APK 打包生成阶段
call run_apk_build.bat
IF ERRORLEVEL 1 (
    echo [PIPELINE] [ERROR] APK 打包生成阶段失败！
    exit /b %ERRORLEVEL%
)

echo [PIPELINE] [4/4] 构建结果验证阶段
call run_verify_build.bat
IF ERRORLEVEL 1 (
    echo [PIPELINE] [ERROR] 构建结果验证阶段失败！
    exit /b %ERRORLEVEL%
)

echo [PIPELINE] ========================== Build Process Finished ==========================
echo [PIPELINE] End time: %date% %time%
echo [PIPELINE] 构建流程全部完成！
