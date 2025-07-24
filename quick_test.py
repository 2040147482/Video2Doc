#!/usr/bin/env python3
"""
快速测试脚本 - 检查环境并启动简化版服务
"""

import sys
import os
import subprocess

def check_python():
    """检查Python版本"""
    version = sys.version_info
    print(f"🐍 Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要 Python 3.8+")
        return False
    return True

def install_basic_packages():
    """安装基础包"""
    packages = ["fastapi", "uvicorn"]
    
    for package in packages:
        print(f"📦 安装 {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package} 安装成功")
        except subprocess.CalledProcessError:
            print(f"❌ {package} 安装失败")
            return False
    return True

def test_imports():
    """测试关键模块导入"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI 和 Uvicorn 导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def start_simple_server():
    """启动简化版服务器"""
    print("\n🚀 启动简化版 FastAPI 服务...")
    print("=" * 50)
    
    # 进入backend目录
    backend_dir = "backend"
    if os.path.exists(backend_dir):
        os.chdir(backend_dir)
        print(f"📁 切换到目录: {os.getcwd()}")
    
    # 运行简化版服务
    try:
        print("🌐 服务将启动在: http://localhost:8000")
        print("📖 API文档: http://localhost:8000/docs")
        print("按 Ctrl+C 停止服务")
        print("-" * 50)
        
        subprocess.run([sys.executable, "main_simple.py"])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    print("🔍 Video2Doc 快速环境检测")
    print("=" * 50)
    
    if not check_python():
        return 1
    
    if not install_basic_packages():
        print("❌ 基础包安装失败")
        return 1
    
    if not test_imports():
        print("❌ 模块导入测试失败")
        return 1
    
    print("\n✅ 环境检查通过！")
    
    # 启动简化版服务
    start_simple_server()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 