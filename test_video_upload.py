"""
视频上传功能测试脚本
测试本地视频上传和视频链接解析功能
"""

import requests
import os
import time
import json
from pathlib import Path
import tempfile
import random

# API基础URL
BASE_URL = "http://localhost:8000"

def create_test_video(size_kb=1024, name="test_video.mp4"):
    """创建测试视频文件"""
    temp_dir = Path("temp_test")
    temp_dir.mkdir(exist_ok=True)
    
    file_path = temp_dir / name
    
    # 创建指定大小的随机二进制文件
    with open(file_path, "wb") as f:
        f.write(random.randbytes(size_kb * 1024))
    
    print(f"创建测试文件: {file_path} ({size_kb}KB)")
    return file_path

def test_health():
    """测试健康检查接口"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"健康检查: {response.status_code}")
        print(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_supported_formats():
    """测试获取支持的格式接口"""
    try:
        response = requests.get(f"{BASE_URL}/api/supported-formats")
        print(f"支持的格式: {response.status_code}")
        if response.status_code == 200:
            formats = response.json()
            print(f"支持的视频格式: {formats['video_formats']}")
            print(f"支持的视频平台: {formats['video_platforms']}")
            print(f"最大文件大小: {formats['max_file_size_mb']}MB")
        return response.status_code == 200
    except Exception as e:
        print(f"获取支持的格式失败: {e}")
        return False

def test_video_url():
    """测试视频链接处理接口"""
    try:
        # 测试YouTube链接
        data = {
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "video_name": "测试视频",
            "language": "auto",
            "output_formats": ["markdown", "pdf"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/upload-url", 
            json=data
        )
        
        print(f"视频链接处理: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"任务ID: {result['task_id']}")
            print(f"状态: {result['status']}")
            print(f"消息: {result['message']}")
            
            # 测试获取任务状态
            time.sleep(1)
            status_response = requests.get(f"{BASE_URL}/api/status/{result['task_id']}")
            print(f"任务状态: {status_response.status_code}")
            if status_response.status_code == 200:
                print(status_response.json())
        
        return response.status_code == 200
    except Exception as e:
        print(f"视频链接处理失败: {e}")
        return False

def test_file_upload():
    """测试文件上传接口"""
    try:
        # 创建测试文件
        test_file = create_test_video(size_kb=512, name="test_video.mp4")
        
        # 上传文件
        with open(test_file, "rb") as f:
            files = {"file": (test_file.name, f, "video/mp4")}
            data = {
                "language": "auto",
                "output_formats": "markdown,pdf"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/upload",
                files=files,
                data=data
            )
        
        print(f"文件上传: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"任务ID: {result['task_id']}")
            print(f"状态: {result['status']}")
            print(f"消息: {result['message']}")
            
            # 测试获取任务状态
            time.sleep(1)
            status_response = requests.get(f"{BASE_URL}/api/status/{result['task_id']}")
            print(f"任务状态: {status_response.status_code}")
            if status_response.status_code == 200:
                print(status_response.json())
        
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()
        
        return response.status_code == 200
    except Exception as e:
        print(f"文件上传失败: {e}")
        return False

def test_list_tasks():
    """测试获取任务列表接口"""
    try:
        response = requests.get(f"{BASE_URL}/api/tasks")
        print(f"任务列表: {response.status_code}")
        if response.status_code == 200:
            tasks = response.json()
            print(f"任务数量: {len(tasks)}")
            if tasks:
                print(f"最新任务: {tasks[0]['task_id']} - {tasks[0]['status']}")
        return response.status_code == 200
    except Exception as e:
        print(f"获取任务列表失败: {e}")
        return False

def cleanup():
    """清理测试文件"""
    temp_dir = Path("temp_test")
    if temp_dir.exists():
        for file in temp_dir.iterdir():
            file.unlink()
        temp_dir.rmdir()
    print("清理测试文件完成")

def main():
    """运行所有测试"""
    print("开始测试视频上传功能...")
    
    tests = [
        ("健康检查", test_health),
        ("支持的格式", test_supported_formats),
        ("视频链接处理", test_video_url),
        ("文件上传", test_file_upload),
        ("任务列表", test_list_tasks)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n=== 测试: {name} ===")
        try:
            result = test_func()
            if result:
                print(f"✅ {name} 测试通过")
                passed += 1
            else:
                print(f"❌ {name} 测试失败")
                failed += 1
        except Exception as e:
            print(f"❌ {name} 测试出错: {e}")
            failed += 1
    
    print(f"\n测试完成: {passed} 通过, {failed} 失败")
    
    # 清理
    cleanup()
    
    return passed, failed

if __name__ == "__main__":
    main() 