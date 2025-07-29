"""
测试导出功能
"""

import requests
import json
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:8000/api"

def create_test_summary_task():
    """创建测试摘要任务"""
    print("=== 创建测试摘要任务 ===")
    
    try:
        from app.services.queue_service import queue_service
        
        # 创建完整的摘要任务
        task_id = "test_export_task"
        task_data = {
            "task_id": task_id,
            "type": "summary",
            "status": "completed",
            "progress": 100.0,
            "result": {
                "title": "AI视频分析报告",
                "overview": "这是一个关于人工智能技术在视频分析领域应用的详细报告。本报告深入探讨了当前AI技术在视频内容理解、自动标注、智能剪辑等方面的最新进展。",
                "chapters": [
                    {
                        "title": "技术概述",
                        "content": "人工智能在视频分析中的应用包括计算机视觉、自然语言处理、深度学习等多个技术领域的融合。",
                        "start_time": 30.5
                    },
                    {
                        "title": "实际应用",
                        "content": "当前AI视频分析技术在安防监控、内容创作、教育培训、娱乐媒体等行业得到广泛应用。",
                        "start_time": 120.8
                    },
                    {
                        "title": "未来发展",
                        "content": "随着硬件性能提升和算法优化，AI视频分析将在实时性、准确性、智能化程度方面持续改进。",
                        "start_time": 180.2
                    }
                ],
                "key_points": [
                    {
                        "description": "AI技术显著提升了视频内容理解的准确性",
                        "timestamp": 45.0
                    },
                    {
                        "description": "深度学习模型在视频分类任务中表现优异",
                        "timestamp": 85.5
                    },
                    {
                        "description": "实时视频分析是当前技术发展的重要方向",
                        "timestamp": 150.3
                    }
                ],
                "topics": ["人工智能", "视频分析", "计算机视觉", "深度学习", "实时处理"],
                "keywords": ["AI", "机器学习", "神经网络", "视频处理", "自动化", "智能分析"],
                "transcription": "大家好，今天我们来讨论人工智能在视频分析领域的应用。首先，让我们了解一下技术概述...",
                "images": [
                    {
                        "description": "AI视频分析架构图",
                        "timestamp": 60.0,
                        "url": "https://example.com/architecture.png"
                    },
                    {
                        "description": "应用场景示例",
                        "timestamp": 140.0,
                        "url": "https://example.com/applications.png"
                    }
                ],
                "generated_at": "2024-01-20T10:30:00Z",
                "model_used": "GPT-4 Vision",
                "processing_time": 45.2,
                "content_duration": 300.0
            }
        }
        
        queue_service.create_task(task_data)
        print(f"✅ 测试摘要任务已创建: {task_id}")
        return task_id
        
    except Exception as e:
        print(f"❌ 创建测试任务失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_get_formats():
    """测试获取支持的格式"""
    print("\n=== 测试获取支持的格式 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/export/formats", timeout=5)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            formats = response.json()
            print(f"支持的格式: {formats}")
            return True
        else:
            print(f"获取格式失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"请求异常: {e}")
        return False

def test_get_templates():
    """测试获取可用的模板"""
    print("\n=== 测试获取可用的模板 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/export/templates", timeout=5)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            templates = response.json()
            print(f"可用的模板: {templates}")
            return True
        else:
            print(f"获取模板失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"请求异常: {e}")
        return False

def test_create_export(task_id: str):
    """测试创建导出任务"""
    print("\n=== 测试创建导出任务 ===")
    
    export_data = {
        "task_id": task_id,
        "formats": ["markdown", "html", "txt"],  # 先测试这几种格式
        "template": "standard",
        "include_images": True,
        "include_timestamps": True,
        "include_metadata": True,
        "custom_filename": "ai_video_analysis_report"
    }
    
    print(f"导出请求: {json.dumps(export_data, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/export",
            json=export_data,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            export_id = result.get("export_id")
            print(f"✅ 导出任务已创建: {export_id}")
            return export_id
        else:
            print(f"❌ 创建导出任务失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_export_status(export_id: str):
    """测试获取导出状态"""
    print(f"\n=== 测试获取导出状态: {export_id} ===")
    
    max_attempts = 30  # 最多等待30秒
    for i in range(max_attempts):
        try:
            response = requests.get(
                f"{BASE_URL}/export/status/{export_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get("status")
                progress = status_data.get("progress", 0)
                message = status_data.get("message", "")
                formats_completed = status_data.get("formats_completed", [])
                download_urls = status_data.get("download_urls", {})
                
                print(f"状态: {status}, 进度: {progress:.1f}%, 消息: {message}")
                
                if formats_completed:
                    print(f"已完成格式: {[f.get('value', f) if isinstance(f, dict) else f for f in formats_completed]}")
                
                if status == "completed":
                    print("✅ 导出完成!")
                    if download_urls:
                        print("下载链接:")
                        for format_name, url in download_urls.items():
                            print(f"  {format_name}: {url}")
                    return True, download_urls
                elif status == "failed":
                    error = status_data.get("error_details", "未知错误")
                    print(f"❌ 导出失败: {error}")
                    return False, {}
                elif status == "cancelled":
                    print("❌ 导出已取消")
                    return False, {}
                    
            else:
                print(f"获取状态失败: {response.status_code} - {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"检查状态时出错: {e}")
        
        time.sleep(1)
    
    print("❌ 导出超时")
    return False, {}

def test_download_file(export_id: str, filename: str):
    """测试下载文件"""
    print(f"\n=== 测试下载文件: {filename} ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/export/download/{export_id}/{filename}",
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 保存文件到本地
            local_filename = f"downloaded_{filename}"
            with open(local_filename, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ 文件下载成功: {local_filename} ({file_size} bytes)")
            
            # 如果是文本文件，显示前几行内容
            if filename.endswith(('.md', '.txt', '.html')):
                try:
                    with open(local_filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                        preview = content[:500] + "..." if len(content) > 500 else content
                        print(f"文件预览:\n{preview}")
                except:
                    print("无法预览文件内容")
            
            return True
        else:
            print(f"❌ 下载失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 下载异常: {e}")
        return False

def main():
    """主测试流程"""
    print("=== 开始导出功能测试 ===")
    
    # 1. 创建测试任务
    task_id = create_test_summary_task()
    if not task_id:
        print("❌ 无法创建测试任务")
        sys.exit(1)
    
    # 2. 测试获取格式和模板
    if not test_get_formats():
        print("❌ 获取格式失败")
        sys.exit(1)
    
    if not test_get_templates():
        print("❌ 获取模板失败")
        sys.exit(1)
    
    # 3. 创建导出任务
    export_id = test_create_export(task_id)
    if not export_id:
        print("❌ 无法创建导出任务")
        sys.exit(1)
    
    # 4. 监控导出状态
    success, download_urls = test_export_status(export_id)
    if not success:
        print("❌ 导出任务失败")
        sys.exit(1)
    
    # 5. 测试文件下载
    download_success = True
    for format_name, url in download_urls.items():
        # 从URL中提取文件名
        filename = url.split('/')[-1]
        if not test_download_file(export_id, filename):
            download_success = False
    
    if download_success:
        print("\n🎉 所有测试通过!")
    else:
        print("\n❌ 部分下载测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main() 