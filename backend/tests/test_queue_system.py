"""
任务队列系统综合测试
测试Celery任务队列的各项功能
"""

import asyncio
import requests
import json
import time
from datetime import datetime


class TaskQueueTester:
    """任务队列测试器"""
    
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health_check(self):
        """测试健康检查"""
        print("🔍 测试队列系统健康检查...")
        
        try:
            response = self.session.get(f"{self.base_url}/queue/health")
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   健康状态: {data}")
                return True
            else:
                print(f"   健康检查失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"   健康检查异常: {str(e)}")
            return False
    
    def test_worker_info(self):
        """测试工作者信息"""
        print("\n🔍 测试工作者信息...")
        
        try:
            response = self.session.get(f"{self.base_url}/queue/workers")
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                workers = data.get("workers", [])
                print(f"   活跃工作者数量: {len(workers)}")
                
                for worker in workers:
                    print(f"   - 工作者: {worker.get('worker_id')}")
                    print(f"     主机: {worker.get('hostname')}")
                    print(f"     活跃任务: {worker.get('active_tasks')}")
                
                return True
            else:
                print(f"   获取工作者信息失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"   获取工作者信息异常: {str(e)}")
            return False
    
    def test_submit_video_task(self):
        """测试提交视频处理任务"""
        print("\n🔍 测试提交视频处理任务...")
        
        task_data = {
            "video_file_path": "/tmp/test_video.mp4",
            "output_dir": "/tmp/output",
            "extract_audio": True,
            "extract_frames": True,
            "frame_interval": 30,
            "priority": "high"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/queue/tasks/video",
                json=task_data
            )
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get("task_id")
                print(f"   任务ID: {task_id}")
                print(f"   状态: {data.get('status')}")
                print(f"   消息: {data.get('message')}")
                return task_id
            else:
                print(f"   提交任务失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"   提交任务异常: {str(e)}")
            return None
    
    def test_submit_audio_task(self):
        """测试提交音频转录任务"""
        print("\n🔍 测试提交音频转录任务...")
        
        task_data = {
            "audio_file_path": "/tmp/test_audio.wav",
            "language": "zh",
            "model": "whisper-base",
            "with_timestamps": True,
            "priority": "normal"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/queue/tasks/audio",
                json=task_data
            )
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get("task_id")
                print(f"   任务ID: {task_id}")
                print(f"   状态: {data.get('status')}")
                return task_id
            else:
                print(f"   提交任务失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"   提交任务异常: {str(e)}")
            return None
    
    def test_submit_summary_task(self):
        """测试提交摘要生成任务"""
        print("\n🔍 测试提交摘要生成任务...")
        
        task_data = {
            "transcript_data": {
                "text": "这是一个测试的转录文本内容。",
                "segments": [
                    {"start": 0.0, "end": 2.5, "text": "这是一个测试"}
                ]
            },
            "summary_type": "detailed",
            "max_length": 500,
            "language": "zh",
            "priority": "high"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/queue/tasks/summary",
                json=task_data
            )
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get("task_id")
                print(f"   任务ID: {task_id}")
                print(f"   状态: {data.get('status')}")
                return task_id
            else:
                print(f"   提交任务失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"   提交任务异常: {str(e)}")
            return None
    
    def test_task_status(self, task_id):
        """测试获取任务状态"""
        if not task_id:
            return None
            
        print(f"\n🔍 测试获取任务状态: {task_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/queue/tasks/{task_id}/status")
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   任务状态: {data.get('status')}")
                print(f"   结果: {data.get('result', 'N/A')}")
                
                if data.get('progress'):
                    progress = data['progress']
                    print(f"   进度: {progress.get('percentage', 0):.1f}%")
                    print(f"   消息: {progress.get('message', '')}")
                
                return data
            else:
                print(f"   获取状态失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"   获取状态异常: {str(e)}")
            return None
    
    def test_complete_workflow(self):
        """测试完整工作流"""
        print("\n🔍 测试完整视频分析工作流...")
        
        workflow_data = {
            "video_file_path": "/tmp/test_complete_video.mp4",
            "output_dir": "/tmp/complete_output",
            "export_formats": ["markdown", "html", "pdf"]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/queue/workflows/complete",
                json=workflow_data
            )
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                workflow_id = data.get("workflow_id")
                print(f"   工作流ID: {workflow_id}")
                print(f"   视频任务ID: {data.get('video_task_id')}")
                print(f"   基础ID: {data.get('base_id')}")
                return workflow_id
            else:
                print(f"   提交工作流失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"   提交工作流异常: {str(e)}")
            return None
    
    def test_statistics(self):
        """测试统计信息"""
        print("\n🔍 测试任务统计信息...")
        
        try:
            response = self.session.get(f"{self.base_url}/queue/statistics")
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   总任务数: {data.get('total_tasks', 0)}")
                print(f"   等待任务: {data.get('pending_tasks', 0)}")
                print(f"   运行任务: {data.get('running_tasks', 0)}")
                print(f"   完成任务: {data.get('completed_tasks', 0)}")
                print(f"   失败任务: {data.get('failed_tasks', 0)}")
                print(f"   成功率: {data.get('success_rate', 0):.1f}%")
                print(f"   活跃工作者: {data.get('active_workers', 0)}")
                return True
            else:
                print(f"   获取统计信息失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"   获取统计信息异常: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始任务队列系统综合测试\n")
        print("=" * 50)
        
        results = {}
        
        # 1. 健康检查
        results['health'] = self.test_health_check()
        
        # 2. 工作者信息
        results['workers'] = self.test_worker_info()
        
        # 3. 提交各类任务
        video_task_id = self.test_submit_video_task()
        audio_task_id = self.test_submit_audio_task()
        summary_task_id = self.test_submit_summary_task()
        
        results['video_task'] = video_task_id is not None
        results['audio_task'] = audio_task_id is not None
        results['summary_task'] = summary_task_id is not None
        
        # 4. 检查任务状态
        if video_task_id:
            self.test_task_status(video_task_id)
        if audio_task_id:
            self.test_task_status(audio_task_id)
        if summary_task_id:
            self.test_task_status(summary_task_id)
        
        # 5. 测试完整工作流
        workflow_id = self.test_complete_workflow()
        results['workflow'] = workflow_id is not None
        
        if workflow_id:
            # 等待一下再检查工作流状态
            time.sleep(2)
            self.test_task_status(workflow_id)
        
        # 6. 统计信息
        results['statistics'] = self.test_statistics()
        
        # 测试结果汇总
        print("\n" + "=" * 50)
        print("📊 测试结果汇总:")
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
        
        print(f"\n总计: {passed_tests}/{total_tests} 通过")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 所有测试通过！任务队列系统运行正常。")
        else:
            print(f"\n⚠️  有 {total_tests - passed_tests} 个测试失败，请检查配置。")
        
        return results


def main():
    """主函数"""
    print("Video2Doc 任务队列系统测试")
    print("确保以下服务正在运行:")
    print("1. Redis 服务器 (默认端口 6379)")
    print("2. FastAPI 应用 (python main.py)")
    print("3. Celery Worker (python start_celery_worker.py)")
    print()
    
    input("按回车键开始测试...")
    
    tester = TaskQueueTester()
    results = tester.run_all_tests()
    
    return results


if __name__ == "__main__":
    main() 