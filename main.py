import json
import os

def load_build_params(file_path='build_params.json'):
    if not os.path.exists(file_path):
        print(f"[ERROR] 参数文件不存在: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        params = json.load(f)
    
    print("[INFO] 读取到构建参数:")
    for key, value in params.items():
        print(f"  {key}: {value}")

    # 模拟构建逻辑
    simulate_build(params)

def simulate_build(params):
    print("\n[INFO] 开始模拟构建流程...")
    game_version = params.get("game_version", "unknown")
    is_debug = params.get("is_debug", False)

    print(f"构建版本号: {game_version}")
    print(f"构建模式: {'调试' if is_debug else '正式'}")

    # TODO: 在这里调用实际打包逻辑

    print("[INFO] 构建流程完成 ✅")

if __name__ == '__main__':
    load_build_params()
