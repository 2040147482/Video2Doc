"""
完整的摘要API测试
"""

import requests
import json
import time

def test_complete_summary():
    """测试完整的摘要流程"""
    print("=== 完整摘要API测试 ===")
    
    # 测试数据
    data = {
        "task_id": "test_video_456",
        "language": "zh-cn",
        "detail_level": "medium",
        "include_chapters": True,
        "include_key_points": True,
        "max_key_points": 5
    }
    
    try:
        # 1. 发送摘要生成请求
        print("1. 发送摘要生成请求...")
        response = requests.post(
            "http://localhost:8000/api/summary",
            json=data,
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code != 200:
            print("❌ 摘要生成请求失败!")
            return False
        
        # 解析响应
        result = response.json()
        summary_task_id = result.get("task_id")
        print(f"✅ 摘要任务已启动，任务ID: {summary_task_id}")
        
        # 2. 等待并检查状态
        print("\n2. 等待摘要生成完成...")
        max_attempts = 15
        for i in range(max_attempts):
            time.sleep(1)
            print(f"检查状态 (尝试 {i+1}/{max_attempts})...")
            
            try:
                status_response = requests.get(
                    f"http://localhost:8000/api/summary/status/{summary_task_id}",
                    timeout=5
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status")
                    progress = status_data.get("progress", 0)
                    print(f"状态: {status}, 进度: {progress:.1f}%")
                    
                    if status == "completed":
                        print("✅ 摘要生成完成!")
                        result_data = status_data.get("result")
                        if result_data:
                            print(f"摘要标题: {result_data.get('title', 'N/A')}")
                            print(f"摘要概述: {result_data.get('overview', 'N/A')[:100]}...")
                            print(f"关键点数量: {len(result_data.get('key_points', []))}")
                            print(f"章节数量: {len(result_data.get('chapters', []))}")
                        return True
                    elif status == "failed":
                        error = status_data.get("error", "未知错误")
                        print(f"❌ 摘要生成失败: {error}")
                        return False
                else:
                    print(f"获取状态失败: {status_response.status_code}")
                    
            except Exception as e:
                print(f"检查状态时出错: {e}")
        
        print("❌ 摘要生成超时")
        return False
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_summary()
    if success:
        print("\n🎉 完整测试通过!")
    else:
        print("\n❌ 完整测试失败!") 