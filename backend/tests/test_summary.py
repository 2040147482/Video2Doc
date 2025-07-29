"""
摘要服务功能测试
"""

import os
import json
import time
import requests
import uuid
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000/api"


def test_health():
    """测试健康检查"""
    print("=== 测试健康检查 ===")
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 健康检查测试通过")
        print(f"状态: {data.get('status')}")
        print(f"版本: {data.get('version')}")
        return True
    else:
        print(f"❌ 健康检查测试失败: {response.status_code}")
        return False


def create_mock_video_task():
    """创建模拟视频任务"""
    print("=== 创建模拟视频任务 ===")
    
    # 创建一个模拟的视频处理任务
    task_id = f"video_{uuid.uuid4().hex}"
    
    # 创建模拟转录任务
    transcription_task_id = f"transcription_{uuid.uuid4().hex}"
    
    # 创建模拟图像分析任务
    image_task_id = f"image_analysis_{uuid.uuid4().hex}"
    
    # 模拟POST请求创建视频任务
    video_data = {
        "url": "https://example.com/sample-video.mp4",
        "output_format": "markdown"
    }
    
    response = requests.post(f"{BASE_URL}/video/process-url", json=video_data)
    
    if response.status_code == 200:
        actual_task_id = response.json().get("task_id")
        print(f"✅ 视频任务已创建: {actual_task_id}")
        return actual_task_id
    else:
        print(f"❌ 视频任务创建失败: {response.status_code}")
        # 返回一个假的任务ID以继续测试
        return task_id


def test_summary_generation(video_task_id):
    """测试摘要生成"""
    print("=== 测试摘要生成 ===")
    
    # 创建摘要请求数据
    summary_data = {
        "task_id": video_task_id,
        "language": "zh-cn",
        "detail_level": "medium",
        "include_chapters": True,
        "include_key_points": True,
        "max_key_points": 5
    }
    
    # 发送摘要生成请求
    response = requests.post(f"{BASE_URL}/summary", json=summary_data)
    
    if response.status_code == 200:
        data = response.json()
        summary_task_id = data.get("task_id")
        print(f"✅ 摘要任务已启动，任务ID: {summary_task_id}")
        
        # 等待摘要生成完成
        print("等待摘要生成完成...")
        
        max_attempts = 10
        for i in range(max_attempts):
            time.sleep(1)  # 等待1秒
            
            # 检查摘要状态
            status_response = requests.get(f"{BASE_URL}/summary/status/{summary_task_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                progress = status_data.get("progress", 0)
                print(f"任务状态: {status}, 进度: {progress:.1%}")
                
                if status == "completed":
                    result = status_data.get("result")
                    print("✅ 摘要生成完成!")
                    
                    # 打印摘要结果摘要
                    if result:
                        print(f"标题: {result.get('title')}")
                        print(f"概述: {result.get('overview')[:100]}...")
                        
                        key_points = result.get("key_points", [])
                        print(f"关键点数量: {len(key_points)}")
                        
                        chapters = result.get("chapters", [])
                        print(f"章节数量: {len(chapters)}")
                        
                        if len(chapters) > 0:
                            print(f"第一章标题: {chapters[0].get('title')}")
                            
                        print(f"关键词: {', '.join(result.get('keywords', []))[:100]}...")
                    
                    return True, summary_task_id
                
                elif status == "failed":
                    error = status_data.get("error", "未知错误")
                    print(f"❌ 摘要生成失败: {error}")
                    return False, summary_task_id
            else:
                print(f"获取状态失败: {status_response.status_code}")
        
        print("❌ 摘要生成超时")
        return False, summary_task_id
    else:
        print(f"❌ 摘要请求失败: {response.status_code}")
        print(f"错误信息: {response.text}")
        return False, None


def test_cancel_summary(task_id):
    """测试取消摘要任务"""
    print("=== 测试取消摘要任务 ===")
    
    if not task_id:
        print("❌ 未提供任务ID，跳过测试")
        return False
    
    # 发送取消请求
    response = requests.delete(f"{BASE_URL}/summary/{task_id}")
    
    if response.status_code == 200:
        print("✅ 摘要任务已取消")
        
        # 验证任务状态
        status_response = requests.get(f"{BASE_URL}/summary/status/{task_id}")
        
        if status_response.status_code == 200:
            status = status_response.json().get("status")
            if status == "cancelled":
                print("✅ 任务状态已更新为已取消")
                return True
            else:
                print(f"❌ 任务状态未更新: {status}")
                return False
        else:
            print(f"❌ 获取状态失败: {status_response.status_code}")
            return False
    else:
        print(f"❌ 取消请求失败: {response.status_code}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("==================================================")
    print("摘要服务功能测试")
    print("==================================================")
    
    # 测试健康检查
    print("\n测试: 健康检查")
    print("------------------------------")
    health_result = test_health()
    
    # 创建模拟视频任务
    video_task_id = create_mock_video_task()
    
    # 测试摘要生成
    print("\n测试: 摘要生成")
    print("------------------------------")
    summary_result, summary_task_id = test_summary_generation(video_task_id)
    
    # 测试取消摘要
    print("\n测试: 取消摘要")
    print("------------------------------")
    # 创建一个新的摘要任务用于测试取消
    new_summary_data = {
        "task_id": video_task_id,
        "language": "zh-cn",
        "detail_level": "low"
    }
    response = requests.post(f"{BASE_URL}/summary", json=new_summary_data)
    if response.status_code == 200:
        cancel_task_id = response.json().get("task_id")
        print(f"创建用于取消的任务: {cancel_task_id}")
        cancel_result = test_cancel_summary(cancel_task_id)
    else:
        print("❌ 无法创建用于取消的任务")
        cancel_result = False
    
    # 汇总结果
    print("\n==================================================")
    print("测试完成:")
    print("==================================================")
    print(f"健康检查: {'✅ 通过' if health_result else '❌ 失败'}")
    print(f"摘要生成: {'✅ 通过' if summary_result else '❌ 失败'}")
    print(f"取消摘要: {'✅ 通过' if cancel_result else '❌ 失败'}")
    
    # 返回总体结果
    return all([health_result, summary_result, cancel_result])


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 