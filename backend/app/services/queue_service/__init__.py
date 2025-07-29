"""
任务队列服务包
提供基于Celery的异步任务处理能力
"""

from .celery_app import celery_app, get_celery_app
from .task_manager import TaskManager, task_manager
from .tasks import (
    process_video_task,
    transcribe_audio_task,
    analyze_images_task,
    generate_summary_task,
    export_document_task
)
from .models import (
    TaskStatus,
    TaskResult,
    TaskProgress,
    VideoProcessingTask,
    AudioTranscriptionTask,
    ImageAnalysisTask,
    SummaryGenerationTask,
    DocumentExportTask
)

__all__ = [
    # 核心组件
    'celery_app',
    'get_celery_app',
    'TaskManager',
    'task_manager',
    
    # 任务函数
    'process_video_task',
    'transcribe_audio_task', 
    'analyze_images_task',
    'generate_summary_task',
    'export_document_task',
    
    # 数据模型
    'TaskStatus',
    'TaskResult',
    'TaskProgress',
    'VideoProcessingTask',
    'AudioTranscriptionTask', 
    'ImageAnalysisTask',
    'SummaryGenerationTask',
    'DocumentExportTask'
] 