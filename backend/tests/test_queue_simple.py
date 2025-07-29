"""
简化的任务队列系统测试
"""

import requests
import time


def test_queue_health():
    """测试队列健康状态"""
    print("🔍 测试队列健康状态...")
    
    try:
        response = requests.get("http://localhost:8000/api/queue/health", timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"健康状态: {data}")
            return True
        else:
            print(f"请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"连接失败: {str(e)}")
        return False


def test_submit_task():
    """测试提交简单任务"""
    print("\n🔍 测试提交音频转录任务...")
    
    task_data = {
        "audio_file_path": "/tmp/test_audio.wav",
        "language": "zh",
        "model": "whisper-base",
        "with_timestamps": True,
        "priority": "normal"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/queue/tasks/audio",
            json=task_data,
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get("task_id")
            print(f"任务ID: {task_id}")
            print(f"状态: {data.get('status')}")
            print(f"消息: {data.get('message')}")
            return task_id
        else:
            print(f"提交失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"提交异常: {str(e)}")
        return None


def test_task_status(task_id):
    """测试获取任务状态"""
    if not task_id:
        return None
        
    print(f"\n🔍 测试获取任务状态: {task_id}")
    
    try:
        response = requests.get(
            f"http://localhost:8000/api/queue/tasks/{task_id}/status", 
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"任务状态: {data.get('status')}")
            if data.get('error'):
                print(f"错误信息: {data.get('error')}")
            return data
        else:
            print(f"获取状态失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"获取状态异常: {str(e)}")
        return None


def test_statistics():
    """测试统计信息"""
    print("\n🔍 测试统计信息...")
    
    try:
        response = requests.get("http://localhost:8000/api/queue/statistics", timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"总任务数: {data.get('total_tasks', 0)}")
            print(f"活跃工作者: {data.get('active_workers', 0)}")
            return True
        else:
            print(f"获取统计失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"获取统计异常: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("📋 任务队列系统简化测试")
    print("=" * 40)
    
    # 1. 健康检查
    if not test_queue_health():
        print("❌ 健康检查失败，请确保:")
        print("   - Redis服务正在运行")
        print("   - FastAPI应用正在运行")
        print("   - Celery Worker正在运行")
        return
    
    # 2. 提交任务
    task_id = test_submit_task()
    
    # 3. 检查任务状态
    if task_id:
        time.sleep(2)  # 等待任务处理
        test_task_status(task_id)
    
    # 4. 统计信息
    test_statistics()
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    main() 