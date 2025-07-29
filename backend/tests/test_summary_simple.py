"""
简单的摘要API测试
"""

import requests
import json

def test_summary():
    """测试摘要API"""
    print("=== 简单摘要API测试 ===")
    
    # 测试数据
    data = {
        "task_id": "test_video_123",
        "language": "zh-cn",
        "detail_level": "medium",
        "include_chapters": True,
        "include_key_points": True,
        "max_key_points": 5
    }
    
    try:
        print("发送请求...")
        response = requests.post(
            "http://localhost:8000/api/summary",
            json=data,
            timeout=5
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 成功!")
        else:
            print("❌ 失败!")
            
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    test_summary() 