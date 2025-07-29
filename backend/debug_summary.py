"""
摘要API调试脚本
"""

import requests
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_task():
    """创建测试任务"""
    print("=== 创建测试任务 ===")
    
    try:
        from app.services.queue_service import queue_service
        
        # 创建任务数据
        task_data = {
            "task_id": "test_video_123",
            "type": "video",
            "status": "completed",
            "progress": 100.0,
            "url": "https://example.com/video.mp4",
            "output_format": "markdown",
            "metadata": {
                "title": "测试视频",
                "duration": 180.5
            },
            "transcription_task_id": None,
            "image_analysis_task_id": None
        }
        
        # 创建任务
        queue_service.create_task(task_data)
        print("✅ 测试任务创建成功")
        return True
        
    except Exception as e:
        print(f"❌ 创建测试任务失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_summary_endpoint():
    """测试摘要端点"""
    print("\n=== 摘要API调试测试 ===")
    
    # 测试数据
    test_data = {
        "task_id": "test_video_123",
        "language": "zh-cn",
        "detail_level": "medium",
        "include_chapters": True,
        "include_key_points": True,
        "max_key_points": 5
    }
    
    print(f"测试数据: {json.dumps(test_data, ensure_ascii=False)}")
    
    try:
        # 发送请求
        print("发送POST请求到 http://localhost:8000/api/summary...")
        response = requests.post(
            "http://localhost:8000/api/summary",
            json=test_data,
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 请求成功!")
            return True
        else:
            print("❌ 请求失败!")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health_endpoint():
    """测试健康检查端点"""
    print("\n=== 健康检查测试 ===")
    
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"健康检查状态码: {response.status_code}")
        print(f"健康检查内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 健康检查通过!")
            return True
        else:
            print("❌ 健康检查失败!")
            return False
            
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

if __name__ == "__main__":
    # 先测试健康检查
    if test_health_endpoint():
        # 创建测试任务
        if create_test_task():
            # 再测试摘要端点
            test_summary_endpoint()
        else:
            print("❌ 无法创建测试任务")
            sys.exit(1)
    else:
        print("❌ 服务器可能未启动或有问题")
        sys.exit(1) 