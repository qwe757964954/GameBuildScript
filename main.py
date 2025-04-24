import json
import os
import subprocess
import sys

def load_build_params(file_path='build_params.json'):
    if not os.path.exists(file_path):
        print(f"[ERROR] 参数文件不存在: {file_path}")
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        params = json.load(f)
    
    print("[INFO] 读取到构建参数:")
    for key, value in params.items():
        print(f"  {key}: {value}")

    return params

def run_git_commands(project_path):
    print("\n[INFO] 开始执行Git操作...")
    
    if not os.path.exists(project_path):
        print(f"[ERROR] 项目路径不存在: {project_path}")
        return False
        
    try:
        # 切换到项目目录
        os.chdir(project_path)
        
        # 使用git checkout .重置修改
        print("[INFO] 执行git checkout .重置修改...")
        checkout_process = subprocess.run(
            ["git", "checkout", "."],
            capture_output=True,
            text=True
        )
        print(checkout_process.stdout)
        if checkout_process.returncode != 0:
            print(f"[ERROR] git checkout失败: {checkout_process.stderr}")
            return False
            
        # 清理缓存文件
        print("[INFO] 清理git缓存文件...")
        clean_process = subprocess.run(
            ["git", "clean", "-xdf"],
            capture_output=True,
            text=True
        )
        print(clean_process.stdout)
        if clean_process.returncode != 0:
            print(f"[ERROR] git clean失败: {clean_process.stderr}")
            return False
        
        # 执行git pull更新代码
        print("[INFO] 执行git pull更新代码...")
        pull_process = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True
        )
        print(pull_process.stdout)
        if pull_process.returncode != 0:
            print(f"[ERROR] git pull失败: {pull_process.stderr}")
            return False
            
        print("[INFO] Git操作完成 ✅")
        return True
        
    except Exception as e:
        print(f"[ERROR] 执行Git命令失败: {e}")
        return False

def execute_build_command(params):
    print("\n[INFO] 开始执行构建流程...")
    
    # 获取参数
    creator_path = params.get("creator_path", "C:/ProgramData/cocos/editors/Creator/3.6.3/CocosCreator.exe")
    project_path = params.get("project_path", "D:/work/Game363")
    config_file = params.get("config_path", "buildConfig_android.json")
    mode = params.get("game_type", "release")
    
    # 先执行Git操作
    if not run_git_commands(project_path):
        print("[WARNING] Git操作失败，但仍将继续构建流程")
    
    # 构建命令
    command = f'python build.py --creator "{creator_path}" --project "{project_path}" --config {config_file} --mode {mode}'
    
    print(f"[INFO] 执行命令: {command}")
    
    try:
        # 切回原目录
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # 执行命令
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
            
            print(decoded_line)
            
        # 等待进程完成
        return_code = process.wait()
        
        if return_code == 0:
            print("[INFO] 构建流程完成 ✅")
        else:
            print(f"[ERROR] 构建失败，返回码: {return_code} ❌")
            
    except Exception as e:
        print(f"[ERROR] 执行命令失败: {e}")

if __name__ == '__main__':
    params = load_build_params()
    if params:
        execute_build_command(params)
