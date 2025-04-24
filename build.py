import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

def setup_logger():
    logger = logging.getLogger("cocos_builder")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger


def check_file(path: Path, description: str, logger):
    if not path.exists():
        logger.error(f"{description} 不存在: {path}")
        sys.exit(1)
    return path


def run_subprocess(command: str, logger, cwd: Path = None):
    logger.info(f"执行命令: {command}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        shell=True  # ⭐注意要用 shell=True，因为 command 是字符串
    )
    assert process.stdout
    for raw_line in iter(process.stdout.readline, b''):
        try:
            line = raw_line.decode('utf-8').rstrip()
        except UnicodeDecodeError:
            line = raw_line.decode('gbk', errors='replace').rstrip()
        logger.info(line)
    ret = process.wait()

    if ret == 0:
        logger.info("子进程正常完成 ✅")
    elif ret == 36:
        logger.info("子进程返回码 36，视为构建成功 ✅")
    else:
        logger.error(f"命令执行失败 (退出码 {ret}) ❌")
        sys.exit(ret)
    
    return True




def build_with_cocos_creator(exec_path: Path, project_dir: Path, config_file: Path, logger):
    logger.info("开始使用 Cocos Creator 构建...")

    # 这里 params 用 json string 方式，兼容更多参数
    params = f"configPath=./buildConfig_android.json"

    # 拼接成一条完整的命令
    command = f'"{str(exec_path)}" --project "{str(project_dir)}" --build {params}'

    run_subprocess(command, logger)
    logger.info("Cocos Creator 构建完成 ✅")


def build_apk_with_gradle(build_dir: Path, gradlew: Path, mode: str, logger):
    logger.info("开始使用 Gradle 打包 APK...")
    project_native = build_dir / "proj"
    check_file(gradlew, "Gradle Wrapper", logger)
    logger.info(project_native)
    task = "assembleRelease" if mode == "release" else "assembleDebug"
    run_subprocess([str(gradlew), task], logger, cwd=project_native)
    logger.info("Gradle 打包完成 ✅")


def parse_args():
    parser = argparse.ArgumentParser(description="自动化 Cocos Creator 构建与打包脚本")
    parser.add_argument("--creator", required=True, help="CocosCreator 可执行文件路径")
    parser.add_argument("--project", required=True, help="Cocos 项目根路径")
    parser.add_argument("--config", default="buildConfig_android.json",
                        help="构建配置文件名 (相对于项目路径)")
    parser.add_argument("--mode", choices=["debug", "release"], default="release",
                        help="Gradle 构建模式")
    return parser.parse_args()


def main():
    logger = setup_logger()
    args = parse_args()

    creator_path = Path(args.creator)
    project_path = Path(args.project)
    config_path = project_path / args.config
    build_platform = "android"
    build_dir = project_path / "build" / build_platform
    gradlew_path = build_dir / "proj" / ("gradlew.bat" if os.name == "nt" else "./gradlew")

    # 前置校验
    check_file(creator_path, "CocosCreator 可执行文件", logger)
    check_file(project_path, "项目目录", logger)
    check_file(config_path, "构建配置文件", logger)

    # 执行构建
    build_with_cocos_creator(creator_path, project_path, config_path, logger)

    # 打包 APK
    build_apk_with_gradle(build_dir, gradlew_path, args.mode, logger)

    apk_dir = project_path / "build" / "outputs" / "apk"
    logger.info(f"APK 存放目录: {apk_dir}")


if __name__ == "__main__":
    main()
