"""
任务管理器
提供高级任务管理功能，包括任务创建、监控、取消等
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from celery import group, chain, chord
from celery.result import AsyncResult, GroupResult

from .celery_app import celery_app, get_queue_stats, revoke_task
from .models import (
    TaskStatus, TaskResult, TaskProgress, TaskPriority,
    VideoProcessingTask, AudioTranscriptionTask, ImageAnalysisTask,
    SummaryGenerationTask, DocumentExportTask, TaskChain,
    TaskStatistics, WorkerInfo, QueueInfo
)
from .tasks import (
    process_video_task, transcribe_audio_task, analyze_images_task,
    generate_summary_task, export_document_task
)


class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.celery_app = celery_app
    
    # 基础任务操作
    
    def submit_video_processing(self, task_params: VideoProcessingTask) -> str:
        """提交视频处理任务"""
        result = process_video_task.apply_async(
            args=[task_params.dict()],
            task_id=task_params.task_id,
            queue='video_processing',
            priority=self._get_priority_value(task_params.priority)
        )
        return result.id
    
    def submit_audio_transcription(self, task_params: AudioTranscriptionTask) -> str:
        """提交音频转录任务"""
        result = transcribe_audio_task.apply_async(
            args=[task_params.dict()],
            task_id=task_params.task_id,
            queue='audio_transcription',
            priority=self._get_priority_value(task_params.priority)
        )
        return result.id
    
    def submit_image_analysis(self, task_params: ImageAnalysisTask) -> str:
        """提交图像分析任务"""
        result = analyze_images_task.apply_async(
            args=[task_params.dict()],
            task_id=task_params.task_id,
            queue='image_analysis',
            priority=self._get_priority_value(task_params.priority)
        )
        return result.id
    
    def submit_summary_generation(self, task_params: SummaryGenerationTask) -> str:
        """提交摘要生成任务"""
        result = generate_summary_task.apply_async(
            args=[task_params.dict()],
            task_id=task_params.task_id,
            queue='summary_generation',
            priority=self._get_priority_value(task_params.priority)
        )
        return result.id
    
    def submit_document_export(self, task_params: DocumentExportTask) -> str:
        """提交文档导出任务"""
        result = export_document_task.apply_async(
            args=[task_params.dict()],
            task_id=task_params.task_id,
            queue='document_export',
            priority=self._get_priority_value(task_params.priority)
        )
        return result.id
    
    # 复合任务操作
    
    def submit_complete_video_analysis(
        self, 
        video_file_path: str,
        output_dir: str,
        export_formats: List[str] = None
    ) -> Dict[str, str]:
        """
        提交完整的视频分析工作流
        
        Returns:
            Dict: 包含各个任务ID的字典
        """
        if export_formats is None:
            export_formats = ['markdown', 'html', 'pdf']
        
        # 生成唯一的任务ID前缀
        base_id = str(uuid.uuid4())[:8]
        
        # 1. 视频处理任务
        video_task_id = f"video_{base_id}"
        video_params = VideoProcessingTask(
            task_id=video_task_id,
            video_file_path=video_file_path,
            output_dir=output_dir,
            extract_audio=True,
            extract_frames=True,
            priority=TaskPriority.HIGH
        )
        
        # 2. 创建任务链
        workflow = chain(
            # 视频处理
            process_video_task.s(video_params.dict()),
            
            # 并行执行音频转录和图像分析
            group(
                transcribe_audio_task.s(),
                analyze_images_task.s()
            ),
            
            # 生成摘要（等待前面所有任务完成）
            generate_summary_task.s(),
            
            # 导出文档
            export_document_task.s({
                'export_formats': export_formats,
                'template': 'standard'
            })
        )
        
        # 执行工作流
        result = workflow.apply_async(task_id=f"workflow_{base_id}")
        
        return {
            'workflow_id': result.id,
            'video_task_id': video_task_id,
            'base_id': base_id
        }
    
    def submit_parallel_analysis(
        self,
        audio_file_path: str,
        image_paths: List[str]
    ) -> str:
        """提交并行分析任务组"""
        
        # 创建并行任务组
        analysis_group = group(
            transcribe_audio_task.s({
                'audio_file_path': audio_file_path,
                'language': 'auto',
                'with_timestamps': True
            }),
            analyze_images_task.s({
                'image_paths': image_paths,
                'analysis_types': ['ocr', 'scene']
            })
        )
        
        # 执行任务组
        result = analysis_group.apply_async()
        return result.id
    
    # 任务状态查询
    
    def get_task_status(self, task_id: str) -> TaskResult:
        """获取任务状态"""
        result = AsyncResult(task_id, app=self.celery_app)
        
        # 构建TaskResult
        task_result = TaskResult(
            task_id=task_id,
            status=TaskStatus(result.state),
            result=result.result if result.successful() else None,
            error=str(result.result) if result.failed() else None,
            traceback=result.traceback if result.failed() else None
        )
        
        # 如果有进度信息
        if result.state == TaskStatus.PROGRESS and isinstance(result.result, dict):
            task_result.progress = TaskProgress(**result.result)
        
        return task_result
    
    def get_task_info(self, task_id: str) -> Dict[str, Any]:
        """获取任务详细信息"""
        result = AsyncResult(task_id, app=self.celery_app)
        
        return {
            'task_id': task_id,
            'status': result.state,
            'result': result.result,
            'traceback': result.traceback,
            'successful': result.successful(),
            'failed': result.failed(),
            'ready': result.ready(),
            'date_done': result.date_done
        }
    
    def get_group_status(self, group_id: str) -> Dict[str, Any]:
        """获取任务组状态"""
        group_result = GroupResult.restore(group_id, app=self.celery_app)
        
        if not group_result:
            return {'error': 'Group not found'}
        
        return {
            'group_id': group_id,
            'completed': group_result.completed_count(),
            'total': len(group_result),
            'successful': group_result.successful(),
            'failed': group_result.failed(),
            'ready': group_result.ready(),
            'results': [
                {
                    'task_id': result.id,
                    'status': result.state,
                    'result': result.result
                }
                for result in group_result
            ]
        }
    
    # 任务控制
    
    def cancel_task(self, task_id: str, terminate: bool = False) -> bool:
        """取消任务"""
        try:
            self.celery_app.control.revoke(task_id, terminate=terminate)
            return True
        except Exception:
            return False
    
    def retry_task(self, task_id: str) -> str:
        """重试失败的任务"""
        result = AsyncResult(task_id, app=self.celery_app)
        
        if not result.failed():
            raise ValueError("只能重试失败的任务")
        
        # 获取原始任务参数
        task_info = result.info
        
        # 重新提交任务
        new_result = self.celery_app.send_task(
            result.name,
            args=result.args,
            kwargs=result.kwargs
        )
        
        return new_result.id
    
    def pause_queue(self, queue_name: str) -> bool:
        """暂停队列"""
        try:
            self.celery_app.control.cancel_consumer(queue_name)
            return True
        except Exception:
            return False
    
    def resume_queue(self, queue_name: str) -> bool:
        """恢复队列"""
        try:
            self.celery_app.control.add_consumer(queue_name)
            return True
        except Exception:
            return False
    
    # 监控和统计
    
    def get_queue_statistics(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        return get_queue_stats()
    
    def get_worker_info(self) -> List[WorkerInfo]:
        """获取工作者信息"""
        try:
            inspect = self.celery_app.control.inspect()
            stats = inspect.stats()
            
            workers = []
            for worker_name, worker_stats in (stats or {}).items():
                workers.append(WorkerInfo(
                    worker_id=worker_name,
                    hostname=worker_stats.get('hostname', ''),
                    active_tasks=len(worker_stats.get('active', [])),
                    processed_tasks=worker_stats.get('total', {}).get('tasks.completed', 0),
                    load_average=worker_stats.get('rusage', {}).get('load_avg', []),
                    status='online'
                ))
            
            return workers
            
        except Exception:
            return []
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """获取活跃任务列表"""
        try:
            inspect = self.celery_app.control.inspect()
            active = inspect.active()
            
            tasks = []
            for worker, worker_tasks in (active or {}).items():
                for task in worker_tasks:
                    tasks.append({
                        'task_id': task['id'],
                        'task_name': task['name'],
                        'worker': worker,
                        'args': task.get('args', []),
                        'kwargs': task.get('kwargs', {}),
                        'time_start': task.get('time_start')
                    })
            
            return tasks
            
        except Exception:
            return []
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """获取计划任务列表"""
        try:
            inspect = self.celery_app.control.inspect()
            scheduled = inspect.scheduled()
            
            tasks = []
            for worker, worker_tasks in (scheduled or {}).items():
                for task in worker_tasks:
                    tasks.append({
                        'task_id': task['request']['id'],
                        'task_name': task['request']['task'],
                        'worker': worker,
                        'eta': task.get('eta'),
                        'priority': task.get('priority')
                    })
            
            return tasks
            
        except Exception:
            return []
    
    def generate_task_statistics(self, hours: int = 24) -> TaskStatistics:
        """生成任务统计信息"""
        try:
            # 这里需要根据实际的结果存储来实现
            # 例如从Redis或数据库查询任务统计
            
            # 模拟统计数据
            return TaskStatistics(
                total_tasks=100,
                pending_tasks=5,
                running_tasks=3,
                completed_tasks=85,
                failed_tasks=7,
                success_rate=92.4,
                average_duration=45.2,
                queue_size=8,
                active_workers=len(self.get_worker_info())
            )
            
        except Exception:
            return TaskStatistics()
    
    # 工具方法
    
    def _get_priority_value(self, priority: TaskPriority) -> int:
        """将优先级枚举转换为数值"""
        priority_map = {
            TaskPriority.LOW: 3,
            TaskPriority.NORMAL: 6,
            TaskPriority.HIGH: 9,
            TaskPriority.CRITICAL: 10
        }
        return priority_map.get(priority, 6)
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查Celery连接
            result = self.celery_app.control.ping(timeout=5)
            
            if result:
                return {
                    'status': 'healthy',
                    'workers': len(result),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'No workers available',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def purge_queue(self, queue_name: str) -> int:
        """清空队列"""
        try:
            return self.celery_app.control.purge()
        except Exception:
            return 0
    
    def restart_workers(self) -> bool:
        """重启工作者"""
        try:
            self.celery_app.control.broadcast('pool_restart', arguments={'reload': True})
            return True
        except Exception:
            return False


# 全局任务管理器实例
task_manager = TaskManager() 