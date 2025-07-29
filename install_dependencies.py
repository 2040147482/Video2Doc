"""
安装所有必要的依赖项
"""

import subprocess
import sys
import os

def run_command(command):
    """运行命令并输出结果"""
    print(f"执行: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 实时输出命令执行结果
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    # 获取退出码
    return_code = process.poll()
    
    # 如果命令执行失败，输出错误信息
    if return_code != 0:
        print(f"命令执行失败，退出码: {return_code}")
        error_output = process.stderr.read()
        if error_output:
            print(f"错误信息: {error_output}")
    
    return return_code

def install_dependencies():
    """安装所有必要的依赖项"""
    # 基本依赖项
    basic_deps = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-multipart",
        "aiofiles",
        "httpx",
        "requests",
        "aiohttp"
    ]
    
    # 安装基本依赖项
    print("安装基本依赖项...")
    for dep in basic_deps:
        run_command(f"{sys.executable} -m pip install {dep}")
    
    # 安装requirements.txt中的依赖项
    if os.path.exists("backend/requirements.txt"):
        print("\n安装requirements.txt中的依赖项...")
        run_command(f"{sys.executable} -m pip install -r backend/requirements.txt")
    
    print("\n依赖项安装完成！")

if __name__ == "__main__":
    install_dependencies() 