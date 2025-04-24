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
    log_pipeline_step("STAGE: 读取构建参数")
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

def run_git_commands(project_path):
    log_pipeline_step("STAGE: Git操作 - 清理并更新代码")
    
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

def execute_build_command(params):
    log_pipeline_step("STAGE: 构建流程")
    
    # 获取参数
    creator_path = params.get("creator_path", "C:/ProgramData/cocos/editors/Creator/3.6.3/CocosCreator.exe")
    project_path = params.get("project_path", "D:/work/Game363")
    config_file = params.get("config_path", "buildConfig_android.json")
    mode = params.get("game_type", "release")
    
    # 先执行Git操作
    if not run_git_commands(project_path):
        log_pipeline_step("[WARNING] Git操作失败，但仍将继续构建流程")
    
    # 构建命令
    command = f'python build.py --creator "{creator_path}" --project "{project_path}" --config {config_file} --mode {mode}'
    
    log_pipeline_step(f"STAGE: 执行构建命令")
    log_pipeline_step(f"执行命令: {command}")
    
    try:
        # 切回原目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_pipeline_step(f"切回脚本目录: {script_dir}")
        os.chdir(script_dir)
        
        # 执行命令
        start_time = time.time()
        log_pipeline_step(f"开始构建，时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
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
                print(f"[BUILD] {decoded_line}")
            
        # 等待进程完成
        return_code = process.wait()
        
        end_time = time.time()
        duration = end_time - start_time
        duration_str = time.strftime("%H:%M:%S", time.gmtime(duration))
        
        if return_code == 0:
            log_pipeline_step(f"STAGE: 构建完成 ✅ 总耗时: {duration_str}")
        else:
            log_pipeline_step(f"STAGE: [ERROR] 构建失败，返回码: {return_code} ❌ 耗时: {duration_str}")
            
    except Exception as e:
        log_pipeline_step(f"[ERROR] 执行命令失败: {e}")

if __name__ == '__main__':
    start_time = time.time()
    log_pipeline_step("开始执行构建脚本")
    
    params = load_build_params()
    if params:
        execute_build_command(params)
        
    end_time = time.time()
    duration = end_time - start_time
    duration_str = time.strftime("%H:%M:%S", time.gmtime(duration))
    log_pipeline_step(f"构建脚本执行完毕，总耗时: {duration_str}")
