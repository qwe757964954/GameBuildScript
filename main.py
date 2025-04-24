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

def execute_build_command(params):
    print("\n[INFO] 开始执行构建流程...")
    
    # 默认参数
    creator_path = params.get("creator_path", "C:/ProgramData/cocos/editors/Creator/3.6.3/CocosCreator.exe")
    project_path = params.get("project_path", "D:/work/Game363")
    config_file = params.get("config_path", "buildConfig_android.json")
    mode = params.get("game_type", "release")
    
    # 构建命令
    command = f'python build.py --creator "{creator_path}" --project "{project_path}" --config {config_file} --mode {mode}'
    
    print(f"[INFO] 执行命令: {command}")
    
    try:
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
