"""
Celery应用配置
配置Celery实例，Redis后端，任务路由等
"""

import os
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
from kombu import Queue, Exchange
from datetime import timedelta

from app.config import settings


def create_celery_app() -> Celery:
    """创建Celery应用实例"""
    
    # Redis配置
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # 创建Celery实例
    celery_app = Celery(
        'video2doc',
        broker=redis_url,
        backend=redis_url,
        include=[
            'app.services.queue_service.tasks'
        ]
    )
    
    # Celery配置
    celery_app.conf.update(
        # 任务序列化
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        
        # 结果后端配置
        result_backend=redis_url,
        result_expires=3600,  # 结果保留1小时
        result_persistent=True,
        
        # 任务路由配置
        task_routes={
            'app.services.queue_service.tasks.process_video_task': {'queue': 'video_processing'},
            'app.services.queue_service.tasks.transcribe_audio_task': {'queue': 'audio_transcription'},
            'app.services.queue_service.tasks.analyze_images_task': {'queue': 'image_analysis'},
            'app.services.queue_service.tasks.generate_summary_task': {'queue': 'summary_generation'},
            'app.services.queue_service.tasks.export_document_task': {'queue': 'document_export'},
        },
        
        # 队列配置
        task_default_queue='default',
        task_queues=(
            Queue('default', Exchange('default'), routing_key='default'),
            Queue('video_processing', Exchange('video'), routing_key='video.processing'),
            Queue('audio_transcription', Exchange('audio'), routing_key='audio.transcription'),
            Queue('image_analysis', Exchange('image'), routing_key='image.analysis'),
            Queue('summary_generation', Exchange('summary'), routing_key='summary.generation'),
            Queue('document_export', Exchange('export'), routing_key='export.document'),
            Queue('high_priority', Exchange('priority'), routing_key='priority.high'),
        ),
        
        # 工作者配置
        worker_prefetch_multiplier=1,  # 每次只预取一个任务
        worker_max_tasks_per_child=100,  # 每个工作者最多处理100个任务后重启
        worker_disable_rate_limits=False,
        
        # 任务执行配置
        task_acks_late=True,  # 任务完成后才确认
        task_reject_on_worker_lost=True,  # 工作者丢失时拒绝任务
        task_ignore_result=False,  # 不忽略任务结果
        
        # 重试配置
        task_annotations={
            '*': {
                'rate_limit': '10/s',  # 全局速率限制
                'time_limit': 300,     # 5分钟超时
                'soft_time_limit': 270, # 软超时4.5分钟
            },
            'app.services.queue_service.tasks.process_video_task': {
                'rate_limit': '5/s',
                'time_limit': 1800,    # 30分钟超时
                'soft_time_limit': 1620, # 软超时27分钟
                'max_retries': 3,
                'default_retry_delay': 60,
            },
            'app.services.queue_service.tasks.transcribe_audio_task': {
                'rate_limit': '10/s',
                'time_limit': 900,     # 15分钟超时
                'max_retries': 3,
                'default_retry_delay': 30,
            },
            'app.services.queue_service.tasks.analyze_images_task': {
                'rate_limit': '15/s',
                'time_limit': 300,     # 5分钟超时
                'max_retries': 2,
                'default_retry_delay': 30,
            },
            'app.services.queue_service.tasks.generate_summary_task': {
                'rate_limit': '5/s',
                'time_limit': 600,     # 10分钟超时
                'max_retries': 3,
                'default_retry_delay': 60,
            },
            'app.services.queue_service.tasks.export_document_task': {
                'rate_limit': '20/s',
                'time_limit': 180,     # 3分钟超时
                'max_retries': 2,
                'default_retry_delay': 15,
            },
        },
        
        # 监控配置
        worker_send_task_events=True,
        task_send_sent_event=True,
        
        # 安全配置
        worker_hijack_root_logger=False,
        worker_log_color=False,
        
        # 性能配置
        broker_connection_retry_on_startup=True,
        broker_connection_retry=True,
        broker_connection_max_retries=10,
        
        # 定时任务配置（可选）
        beat_schedule={
            'cleanup-expired-results': {
                'task': 'app.services.queue_service.tasks.cleanup_expired_results',
                'schedule': timedelta(hours=1),  # 每小时清理一次
            },
            'generate-task-statistics': {
                'task': 'app.services.queue_service.tasks.generate_statistics',
                'schedule': timedelta(minutes=5),  # 每5分钟生成统计
            },
        },
    )
    
    return celery_app


# 创建全局Celery实例
celery_app = create_celery_app()


def get_celery_app() -> Celery:
    """获取Celery应用实例"""
    return celery_app


# 任务事件处理
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """任务开始前的处理"""
    print(f"Task {task_id} started: {task.name}")


@task_postrun.connect  
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, 
                        retval=None, state=None, **kwds):
    """任务完成后的处理"""
    print(f"Task {task_id} finished: {task.name} - {state}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """任务失败时的处理"""
    print(f"Task {task_id} failed: {exception}")


# 健康检查
def health_check():
    """Celery健康检查"""
    try:
        # 检查Redis连接
        from celery import current_app
        result = current_app.control.ping(timeout=5)
        
        if result:
            return {"status": "healthy", "workers": len(result)}
        else:
            return {"status": "unhealthy", "error": "No workers available"}
            
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# 获取队列统计信息
def get_queue_stats():
    """获取队列统计信息"""
    try:
        from celery import current_app
        inspect = current_app.control.inspect()
        
        # 获取活跃任务
        active_tasks = inspect.active()
        
        # 获取队列长度
        queue_lengths = inspect.active_queues()
        
        # 获取工作者统计
        worker_stats = inspect.stats()
        
        return {
            "active_tasks": active_tasks,
            "queue_lengths": queue_lengths, 
            "worker_stats": worker_stats
        }
        
    except Exception as e:
        return {"error": str(e)}


# 取消任务
def revoke_task(task_id: str, terminate: bool = False):
    """取消任务"""
    try:
        from celery import current_app
        current_app.control.revoke(task_id, terminate=terminate)
        return {"status": "revoked", "task_id": task_id}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}


# 重启工作者
def restart_workers():
    """重启所有工作者"""
    try:
        from celery import current_app
        current_app.control.broadcast('pool_restart', arguments={'reload': True})
        return {"status": "restarted"}
        
    except Exception as e:
        return {"status": "error", "error": str(e)} 