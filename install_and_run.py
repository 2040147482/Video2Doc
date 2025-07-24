#!/usr/bin/env python3
"""
Video2Doc 一键安装和启动脚本
自动安装依赖并启动后端服务
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """运行命令并处理错误"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败:")
        print(f"   错误: {e.stderr}")
        return False

def main():
    print("🚀 Video2Doc 一键安装启动脚本")
    print("=" * 50)
    
    # 检查是否在正确目录
    if not Path("backend").exists():
        print("❌ 请在项目根目录运行此脚本")
        return 1
    
    # 进入backend目录
    os.chdir("backend")
    print(f"📁 当前目录: {os.getcwd()}")
    
    # 安装基础依赖
    if not run_command("pip install -r requirements-basic.txt", "安装基础依赖"):
        print("❌ 基础依赖安装失败，尝试单独安装...")
        
        # 逐个安装核心包
        core_packages = [
            "fastapi==0.115.6",
            "uvicorn[standard]==0.32.1", 
            "pydantic==2.10.4",
            "pydantic-settings==2.7.0",
            "python-multipart==0.0.17",
            "aiofiles==24.1.0",
            "python-dotenv==1.0.1"
        ]
        
        for package in core_packages:
            if not run_command(f"pip install {package}", f"安装 {package}"):
                print(f"❌ 无法安装 {package}，请手动安装")
                return 1
    
    # 检查关键模块
    print("\n🔍 检查关键模块...")
    try:
        import fastapi
        import uvicorn
        import aiofiles
        import pydantic
        import pydantic_settings
        print("✅ 所有关键模块导入成功")
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return 1
    
    # 检查应用是否可以导入
    print("\n🔍 检查应用导入...")
    try:
        import sys
        sys.path.append(".")
        from main import app
        print("✅ FastAPI 应用导入成功")
    except Exception as e:
        print(f"❌ 应用导入失败: {e}")
        print("   这可能是正常的，如果依赖缺失的话")
    
    # 启动服务
    print("\n🚀 启动开发服务...")
    print("服务地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        return 0
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 