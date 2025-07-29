"""
简化的摘要API测试
"""

import requests
import json
import uuid
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 创建一个假的视频任务ID
VIDEO_TASK_ID = f"video_{uuid.uuid4().hex}"

def create_mock_task():
    """创建一个模拟任务"""
    print("创建模拟任务...")
    
    # 创建任务数据
    task_data = {
        "task_id": VIDEO_TASK_ID,
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
    
    # 直接访问队列服务创建任务
    try:
        from app.services.queue_service import queue_service
        print(f"队列服务类型: {type(queue_service)}")
        
        # 创建任务
        queue_service.create_task(task_data)
        print(f"✅ 模拟任务已创建: {VIDEO_TASK_ID}")
        
        # 验证任务是否创建成功
        created_task = queue_service.get_task(VIDEO_TASK_ID)
        if created_task:
            print(f"✅ 任务验证成功: {created_task.get('task_id')}")
            return True
        else:
            print("❌ 任务创建后无法获取")
            return False
            
    except Exception as e:
        print(f"❌ 模拟任务创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_summary_api():
    """测试摘要API"""
    print("\n=== 测试摘要API ===")
    
    # 创建摘要请求数据
    summary_data = {
        "task_id": VIDEO_TASK_ID,
        "language": "zh-cn",
        "detail_level": "medium",
        "include_chapters": True,
        "include_key_points": True,
        "max_key_points": 5
    }
    
    print(f"请求数据: {json.dumps(summary_data, ensure_ascii=False)}")
    
    # 发送摘要生成请求
    try:
        print("发送POST请求到 http://localhost:8000/api/summary...")
        response = requests.post(
            "http://localhost:8000/api/summary", 
            json=summary_data,
            timeout=10  # 添加10秒超时
        )
        
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            summary_task_id = data.get("task_id")
            print(f"✅ 摘要任务已启动，任务ID: {summary_task_id}")
            
            # 等待摘要生成完成
            print("等待摘要生成完成...")
            
            max_attempts = 10
            for i in range(max_attempts):
                time.sleep(1)  # 等待1秒
                print(f"检查状态 (尝试 {i+1}/{max_attempts})...")
                
                # 检查摘要状态
                try:
                    status_url = f"http://localhost:8000/api/summary/status/{summary_task_id}"
                    print(f"GET {status_url}")
                    status_response = requests.get(
                        status_url,
                        timeout=5  # 添加5秒超时
                    )
                    
                    print(f"状态响应: {status_response.status_code}")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"状态数据: {json.dumps(status_data, ensure_ascii=False)}")
                        status = status_data.get("status")
                        progress = status_data.get("progress", 0)
                        print(f"任务状态: {status}, 进度: {progress:.1f}%")
                        
                        if status == "completed":
                            print("✅ 摘要生成完成!")
                            return True
                        elif status == "failed":
                            error = status_data.get("error", "未知错误")
                            print(f"❌ 摘要生成失败: {error}")
                            return False
                    else:
                        print(f"获取状态失败: {status_response.status_code}")
                        print(f"响应内容: {status_response.text}")
                except Exception as e:
                    print(f"检查状态时出错: {e}")
            
            print("❌ 摘要生成超时")
            return False
        else:
            print(f"❌ 摘要请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 摘要API测试开始 ===")
    print(f"视频任务ID: {VIDEO_TASK_ID}")
    
    if create_mock_task():
        success = test_summary_api()
        if success:
            print("\n✅ 测试通过!")
        else:
            print("\n❌ 测试失败!")
            sys.exit(1)  # 添加非零退出码表示失败
    else:
        print("\n❌ 无法创建模拟任务!")
        sys.exit(1)  # 添加非零退出码表示失败 