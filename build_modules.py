import json
import os
import subprocess
import sys
import time
import datetime

def log_pipeline_step(message):
    """输出带有管道格式的日志信息"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[PIPELINE] [{timestamp}] {message}")

def load_build_params(file_path='build_params.json'):
    """加载构建参数"""
    log_pipeline_step("加载构建参数")
    if not os.path.exists(file_path):
        log_pipeline_step(f"[ERROR] 参数文件不存在: {file_path}")
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        params = json.load(f)
    
    log_pipeline_step("读取到构建参数:")
    for key, value in params.items():
        log_pipeline_step(f"  {key}: {value}")
    
    # 添加默认参数，如果没有提供
    if "creator_path" not in params:
        params["creator_path"] = "C:/ProgramData/cocos/editors/Creator/3.6.3/CocosCreator.exe"
        log_pipeline_step(f"  使用默认 creator_path: {params['creator_path']}")
    
    if "project_path" not in params:
        params["project_path"] = "D:/work/Game363"
        log_pipeline_step(f"  使用默认 project_path: {params['project_path']}")

    return params

def run_git_update():
    """执行Git更新操作"""
    log_pipeline_step("STAGE: Git操作 - 清理并更新代码")
    params = load_build_params()
    if not params:
        return False
        
    project_path = params.get("project_path")
    
    if not os.path.exists(project_path):
        log_pipeline_step(f"[ERROR] 项目路径不存在: {project_path}")
        return False
        
    try:
        # 切换到项目目录
        log_pipeline_step(f"切换到项目目录: {project_path}")
        os.chdir(project_path)
        
        # 使用git checkout .重置修改
        log_pipeline_step("执行git checkout .重置修改...")
        checkout_process = subprocess.run(
            ["git", "checkout", "."],
            capture_output=True,
            text=True
        )
        if checkout_process.stdout.strip():
            log_pipeline_step(checkout_process.stdout)
        if checkout_process.returncode != 0:
            log_pipeline_step(f"[ERROR] git checkout失败: {checkout_process.stderr}")
            return False
        else:
            log_pipeline_step("git checkout完成")
            
        # 清理缓存文件
        log_pipeline_step("执行git clean -xdf清理缓存文件...")
        clean_process = subprocess.run(
            ["git", "clean", "-xdf"],
            capture_output=True,
            text=True
        )
        if clean_process.stdout.strip():
            log_pipeline_step(clean_process.stdout)
        if clean_process.returncode != 0:
            log_pipeline_step(f"[ERROR] git clean失败: {clean_process.stderr}")
            return False
        else:
            log_pipeline_step("git clean完成")
        
        # 执行git pull更新代码
        log_pipeline_step("执行git pull更新代码...")
        pull_process = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True
        )
        if pull_process.stdout.strip():
            log_pipeline_step(pull_process.stdout)
        if pull_process.returncode != 0:
            log_pipeline_step(f"[ERROR] git pull失败: {pull_process.stderr}")
            return False
        else:
            log_pipeline_step("git pull完成")
            
        log_pipeline_step("Git操作全部完成 ✅")
        return True
        
    except Exception as e:
        log_pipeline_step(f"[ERROR] 执行Git命令失败: {e}")
        return False

def run_cocos_build():
    """执行Cocos Creator构建操作"""
    log_pipeline_step("STAGE: Cocos 工程生成")
    params = load_build_params()
    if not params:
        return False
        
    creator_path = params.get("creator_path")
    project_path = params.get("project_path")
    config_file = params.get("config_path")
    
    if not os.path.exists(creator_path):
        log_pipeline_step(f"[ERROR] Cocos Creator路径不存在: {creator_path}")
        return False
        
    if not os.path.exists(project_path):
        log_pipeline_step(f"[ERROR] 项目路径不存在: {project_path}")
        return False
    
    try:
        # 构建命令
        log_pipeline_step("执行Cocos Creator构建...")
        command = f'"{creator_path}" --project "{project_path}" --build "configPath={project_path}/{config_file}"'
        log_pipeline_step(f"执行命令: {command}")
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
        )
        
        # 实时输出日志
        for line in iter(process.stdout.readline, b''):
            try:
                decoded_line = line.decode('utf-8').strip()
            except UnicodeDecodeError:
                decoded_line = line.decode('gbk', errors='replace').strip()
            
            if decoded_line:
                print(f"[COCOS] {decoded_line}")
        
        # 等待进程完成
        return_code = process.wait()
        
        if return_code == 0 or return_code == 36:  # Cocos Creator有时返回36但实际构建成功
            log_pipeline_step("Cocos 工程生成完成 ✅")
            return True
        else:
            log_pipeline_step(f"[ERROR] Cocos 工程生成失败，返回码: {return_code} ❌")
            return False
            
    except Exception as e:
        log_pipeline_step(f"[ERROR] 执行Cocos构建命令失败: {e}")
        return False

def run_apk_build():
    """执行APK打包操作"""
    log_pipeline_step("STAGE: APK 打包生成")
    params = load_build_params()
    if not params:
        return False
        
    project_path = params.get("project_path")
    mode = params.get("game_type", "release")
    
    # 检查构建目录是否存在
    build_dir = os.path.join(project_path, "build", "android", "proj")
    if not os.path.exists(build_dir):
        log_pipeline_step(f"[ERROR] Android构建目录不存在: {build_dir}")
        log_pipeline_step("请先执行Cocos工程生成步骤")
        return False
        
    try:
        # 切换到构建目录
        log_pipeline_step(f"切换到Android构建目录: {build_dir}")
        os.chdir(build_dir)
        
        # 确定构建任务
        task = "assembleRelease" if mode == "release" else "assembleDebug"
        log_pipeline_step(f"执行Gradle构建: {task}")
        
        # 执行Gradle构建
        gradle_cmd = "gradlew.bat" if os.name == "nt" else "./gradlew"
        command = f"{gradle_cmd} {task}"
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
        )
        
        # 实时输出日志
        for line in iter(process.stdout.readline, b''):
            try:
                decoded_line = line.decode('utf-8').strip()
            except UnicodeDecodeError:
                decoded_line = line.decode('gbk', errors='replace').strip()
            
            if decoded_line:
                print(f"[GRADLE] {decoded_line}")
        
        # 等待进程完成
        return_code = process.wait()
        
        if return_code == 0:
            log_pipeline_step("APK 打包生成完成 ✅")
            return True
        else:
            log_pipeline_step(f"[ERROR] APK 打包生成失败，返回码: {return_code} ❌")
            return False
            
    except Exception as e:
        log_pipeline_step(f"[ERROR] 执行APK打包命令失败: {e}")
        return False

def verify_build():
    """验证构建结果"""
    log_pipeline_step("STAGE: 构建结果验证")
    params = load_build_params()
    if not params:
        return False
        
    project_path = params.get("project_path")
    mode = params.get("game_type", "release")
    
    # 检查APK输出目录
    apk_dir = os.path.join(project_path, "build", "android", "proj", "app", "build", "outputs", "apk", mode)
    log_pipeline_step(f"检查APK输出目录: {apk_dir}")
    
    if not os.path.exists(apk_dir):
        log_pipeline_step(f"[ERROR] APK输出目录不存在: {apk_dir}")
        return False
        
    try:
        # 列出目录下所有APK文件
        apk_files = [f for f in os.listdir(apk_dir) if f.endswith('.apk')]
        
        if apk_files:
            log_pipeline_step("找到以下APK文件:")
            for apk in apk_files:
                apk_path = os.path.join(apk_dir, apk)
                size_mb = os.path.getsize(apk_path) / (1024 * 1024)
                log_pipeline_step(f"  {apk} (大小: {size_mb:.2f} MB)")
            
            # 获取APK版本信息（如有需要可以添加）
            
            log_pipeline_step("构建验证成功 ✅")
            return True
        else:
            log_pipeline_step("[ERROR] 未找到APK文件 ❌")
            return False
            
    except Exception as e:
        log_pipeline_step(f"[ERROR] 验证构建结果失败: {e}")
        return False

if __name__ == "__main__":
    # 命令行参数处理
    if len(sys.argv) < 2:
        log_pipeline_step("请指定要执行的操作: git_update, cocos_build, apk_build, verify_build")
        sys.exit(1)
        
    action = sys.argv[1]
    result = False
    
    start_time = time.time()
    
    if action == "git_update":
        result = run_git_update()
    elif action == "cocos_build":
        result = run_cocos_build()
    elif action == "apk_build":
        result = run_apk_build()
    elif action == "verify_build":
        result = verify_build()
    else:
        log_pipeline_step(f"未知操作: {action}")
        sys.exit(1)
        
    end_time = time.time()
    duration = end_time - start_time
    duration_str = time.strftime("%H:%M:%S", time.gmtime(duration))
    
    log_pipeline_step(f"操作 {action} 完成，耗时: {duration_str}")
    
    if not result:
        sys.exit(1) 