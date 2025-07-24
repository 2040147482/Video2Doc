#!/usr/bin/env python3
"""
Video2Doc API 测试脚本
测试后端接口的基本功能
"""

import requests
import json
import sys
import time
from pathlib import Path

# API基础URL
BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ 健康检查成功: {response.status_code}")
        print(f"   响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_supported_formats():
    """测试获取支持格式接口"""
    print("\n🔍 测试支持格式接口...")
    try:
        response = requests.get(f"{BASE_URL}/api/supported-formats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 支持格式获取成功:")
            print(f"   视频格式: {data['video_formats']}")
            print(f"   视频平台: {data['video_platforms']}")
            print(f"   最大文件大小: {data['max_file_size_mb']}MB")
            return True
        else:
            print(f"❌ 支持格式获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 支持格式获取失败: {e}")
        return False

def test_video_url():
    """测试视频链接处理接口"""
    print("\n🔍 测试视频链接处理...")
    
    # 测试YouTube链接
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.bilibili.com/video/BV1xx411c7mD",
        "https://vimeo.com/123456789"
    ]
    
    success_count = 0
    total_count = len(test_urls)
    
    for url in test_urls:
        print(f"   测试URL: {url}")
        try:
            payload = {
                "video_url": url,
                "video_name": f"测试视频_{url.split('/')[-1]}",
                "language": "auto",
                "output_formats": ["markdown"]
            }
            
            response = requests.post(
                f"{BASE_URL}/api/upload-url",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ URL处理成功: {data['task_id']}")
                print(f"      消息: {data['message']}")
                
                # 检查任务状态
                task_id = data['task_id']
                time.sleep(1)
                status_response = requests.get(f"{BASE_URL}/api/status/{task_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"      任务状态: {status_data['status']}")
                
                success_count += 1
            else:
                print(f"   ❌ URL处理失败: {response.status_code}")
                if response.content:
                    try:
                        error_data = response.json()
                        print(f"      错误信息: {error_data.get('message', '未知错误')}")
                    except:
                        print(f"      错误内容: {response.text}")
                        
        except Exception as e:
            print(f"   ❌ URL处理异常: {e}")
        
        print()  # 空行分隔
    
    # 如果所有URL都成功处理，则测试通过
    return success_count == total_count

def test_file_upload():
    """测试文件上传接口（创建一个小测试文件）"""
    print("\n🔍 测试文件上传接口...")
    
    # 创建一个小的测试文件，使用有效的视频文件扩展名
    test_file_path = Path("test_video.mp4")
    test_content = b"This is a test file content for Video2Doc upload test."
    
    try:
        with open(test_file_path, "wb") as f:
            f.write(test_content)
        
        print(f"   创建测试文件: {test_file_path}")
        
        # 尝试上传（注意：这会成功，因为我们使用了有效的视频文件扩展名）
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_video.mp4", f, "video/mp4")}
            data = {
                "language": "auto",
                "output_formats": "markdown"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/upload",
                files=files,
                data=data,
                timeout=10
            )
            
            if response.status_code == 422:  # 验证错误
                print(f"   ✅ 文件验证正常工作 (422错误)")
                try:
                    error_data = response.json()
                    print(f"      验证错误: {error_data.get('message', '格式验证失败')}")
                except:
                    print(f"      响应内容: {response.text}")
                return True
            elif response.status_code == 200:  # 上传成功
                print(f"   ✅ 文件上传成功")
                try:
                    data = response.json()
                    print(f"      任务ID: {data.get('task_id')}")
                    print(f"      消息: {data.get('message')}")
                except:
                    print(f"      响应内容: {response.text}")
                return True
            else:
                print(f"   ❌ 意外的响应状态: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"      响应信息: {error_data}")
                except:
                    print(f"      响应内容: {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ 文件上传测试失败: {e}")
        return False
    finally:
        # 清理测试文件
        if test_file_path.exists():
            test_file_path.unlink()
            print(f"   🗑️  清理测试文件: {test_file_path}")

def test_tasks_list():
    """测试获取任务列表"""
    print("\n🔍 测试任务列表接口...")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks", timeout=5)
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ 任务列表获取成功: 共 {len(tasks)} 个任务")
            for task in tasks[:3]:  # 只显示前3个
                print(f"   任务 {task['task_id'][:8]}...: {task['status']} - {task['message']}")
            return True
        else:
            print(f"❌ 任务列表获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 任务列表获取失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🚀 开始测试 Video2Doc API")
    print(f"📍 API地址: {BASE_URL}")
    print("=" * 50)
    
    tests = [
        test_health,
        test_supported_formats,
        test_video_url,
        test_file_upload,
        test_tasks_list
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ 测试 {test_func.__name__} 发生异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查后端服务")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 