import os
import subprocess
import sys

def run_command(command):
    """运行命令并返回结果"""
    print(f"执行命令: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def fix_numpy_pytorch_compatibility():
    """修复NumPy和PyTorch的兼容性问题"""
    print("开始修复NumPy和PyTorch的兼容性问题...")
    
    # 1. 确保我们在虚拟环境中
    if not os.environ.get('VIRTUAL_ENV'):
        print("请先激活虚拟环境!")
        print("在Windows上: .\\venv\\Scripts\\Activate.ps1")
        print("在Linux/Mac上: source venv/bin/activate")
        return False
    
    # 2. 卸载当前的NumPy
    print("\n卸载当前的NumPy...")
    if not run_command("pip uninstall -y numpy"):
        return False
    
    # 3. 安装兼容的NumPy 1.x版本
    print("\n安装兼容的NumPy 1.26.4版本...")
    if not run_command("pip install numpy==1.26.4"):
        return False
    
    # 4. 验证NumPy版本
    print("\n验证NumPy版本...")
    if not run_command("pip show numpy"):
        return False
    
    print("\n修复完成! 请重新启动后端服务和测试。")
    return True

if __name__ == "__main__":
    # 检查是否在虚拟环境中
    if not os.environ.get('VIRTUAL_ENV'):
        print("警告: 未检测到虚拟环境。")
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            print("已取消操作。")
            sys.exit(1)
    
    # 执行修复
    success = fix_numpy_pytorch_compatibility()
    if not success:
        print("修复失败。")
        sys.exit(1)
    
    print("修复成功!")
    sys.exit(0) 