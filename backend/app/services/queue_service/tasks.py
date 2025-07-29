"""
Celery任务定义
定义各种异步任务，包括视频处理、音频转录、图像分析等
"""

import os
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from celery import current_task
from celery.exceptions import Retry

from .celery_app import celery_app
from .models import TaskStatus, TaskProgress, TaskPriority
from app.services.video_processor.extractor import VideoProcessor
from app.services.speech_recognition.whisper_service import WhisperService
from app.services.image_recognition.vision_service import VisionService
from app.services.summary.ai_summary_service import AISummaryService
from app.services.export import export_service


def update_task_progress(current: int, total: int, message: str = None):
    """更新任务进度"""
    if current_task:
        progress = TaskProgress(
            current=current,
            total=total,
            percentage=(current / total) * 100 if total > 0 else 0,
            message=message
        )
        
        current_task.update_state(
            state=TaskStatus.PROGRESS,
            meta=progress.dict()
        )


@celery_app.task(bind=True, name='app.services.queue_service.tasks.process_video_task')
def process_video_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    视频处理任务
    
    Args:
        task_data: 视频处理任务参数
        
    Returns:
        Dict: 处理结果
    """
    try:
        # 更新任务状态
        self.update_state(state=TaskStatus.STARTED, meta={'message': '开始视频处理'})
        
        # 解析任务参数
        video_file_path = task_data['video_file_path']
        output_dir = task_data['output_dir']
        extract_audio = task_data.get('extract_audio', True)
        extract_frames = task_data.get('extract_frames', True)
        frame_interval = task_data.get('frame_interval', 30)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化视频处理器
        processor = VideoProcessor()
        
        # 提取音频
        audio_file = None
        if extract_audio:
            update_task_progress(25, 100, "正在提取音频...")
            audio_file = processor.extract_audio(
                video_path=video_file_path,
                output_path=os.path.join(output_dir, "audio.wav")
            )
        
        # 提取关键帧
        frames = []
        if extract_frames:
            update_task_progress(75, 100, "正在提取关键帧...")
            frames = processor.extract_frames(
                video_path=video_file_path,
                output_dir=output_dir,
                interval=frame_interval
            )
        
        # 完成
        update_task_progress(100, 100, "视频处理完成")
        
        result = {
            'video_file': video_file_path,
            'audio_file': audio_file,
            'frames': frames,
            'output_dir': output_dir,
            'processed_at': datetime.utcnow().isoformat()
        }
        
        return result
        
    except Exception as e:
        # 记录错误
        error_info = {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'task_id': self.request.id
        }
        
        # 重试逻辑
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)
        
        # 最终失败
        self.update_state(
            state=TaskStatus.FAILURE,
            meta=error_info
        )
        raise


@celery_app.task(bind=True, name='app.services.queue_service.tasks.transcribe_audio_task')
def transcribe_audio_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    音频转录任务
    
    Args:
        task_data: 音频转录任务参数
        
    Returns:
        Dict: 转录结果
    """
    try:
        # 更新任务状态
        self.update_state(state=TaskStatus.STARTED, meta={'message': '开始音频转录'})
        
        # 解析任务参数
        audio_file_path = task_data['audio_file_path']
        language = task_data.get('language')
        model = task_data.get('model', 'whisper-base')
        with_timestamps = task_data.get('with_timestamps', True)
        
        # 初始化转录服务
        whisper_service = WhisperService()
        
        # 执行转录
        update_task_progress(50, 100, "正在转录音频...")
        
        result = whisper_service.transcribe_file(
            file_path=audio_file_path,
            language=language,
            with_timestamps=with_timestamps
        )
        
        # 完成
        update_task_progress(100, 100, "音频转录完成")
        
        result.update({
            'audio_file': audio_file_path,
            'transcribed_at': datetime.utcnow().isoformat()
        })
        
        return result
        
    except Exception as e:
        # 错误处理
        error_info = {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'task_id': self.request.id
        }
        
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=30, exc=e)
        
        self.update_state(state=TaskStatus.FAILURE, meta=error_info)
        raise


@celery_app.task(bind=True, name='app.services.queue_service.tasks.analyze_images_task')
def analyze_images_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    图像分析任务
    
    Args:
        task_data: 图像分析任务参数
        
    Returns:
        Dict: 分析结果
    """
    try:
        # 更新任务状态
        self.update_state(state=TaskStatus.STARTED, meta={'message': '开始图像分析'})
        
        # 解析任务参数
        image_paths = task_data['image_paths']
        analysis_types = task_data.get('analysis_types', ['ocr', 'scene'])
        
        # 初始化视觉服务
        vision_service = VisionService()
        
        # 分析图像
        results = []
        total_images = len(image_paths)
        
        for i, image_path in enumerate(image_paths):
            update_task_progress(
                i + 1, total_images, 
                f"正在分析图像 {i + 1}/{total_images}"
            )
            
            # 执行分析
            analysis_result = vision_service.analyze_image(
                image_path=image_path,
                analysis_types=analysis_types
            )
            
            results.append({
                'image_path': image_path,
                'analysis': analysis_result
            })
        
        # 完成
        update_task_progress(100, 100, "图像分析完成")
        
        result = {
            'images': results,
            'total_images': total_images,
            'analyzed_at': datetime.utcnow().isoformat()
        }
        
        return result
        
    except Exception as e:
        # 错误处理
        error_info = {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'task_id': self.request.id
        }
        
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=30, exc=e)
        
        self.update_state(state=TaskStatus.FAILURE, meta=error_info)
        raise


@celery_app.task(bind=True, name='app.services.queue_service.tasks.generate_summary_task')
def generate_summary_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    AI摘要生成任务
    
    Args:
        task_data: 摘要生成任务参数
        
    Returns:
        Dict: 摘要结果
    """
    try:
        # 更新任务状态
        self.update_state(state=TaskStatus.STARTED, meta={'message': '开始生成摘要'})
        
        # 解析任务参数
        transcript_data = task_data['transcript_data']
        image_analysis_data = task_data.get('image_analysis_data')
        summary_type = task_data.get('summary_type', 'detailed')
        max_length = task_data.get('max_length', 1000)
        language = task_data.get('language', 'zh')
        
        # 初始化摘要服务
        summary_service = AISummaryService()
        
        # 生成摘要
        update_task_progress(50, 100, "正在生成AI摘要...")
        
        result = summary_service.generate_summary(
            transcript_data=transcript_data,
            image_data=image_analysis_data,
            summary_type=summary_type,
            max_length=max_length,
            language=language
        )
        
        # 完成
        update_task_progress(100, 100, "摘要生成完成")
        
        result.update({
            'generated_at': datetime.utcnow().isoformat(),
            'summary_type': summary_type,
            'language': language
        })
        
        return result
        
    except Exception as e:
        # 错误处理
        error_info = {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'task_id': self.request.id
        }
        
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)
        
        self.update_state(state=TaskStatus.FAILURE, meta=error_info)
        raise


@celery_app.task(bind=True, name='app.services.queue_service.tasks.export_document_task')
def export_document_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    文档导出任务
    
    Args:
        task_data: 文档导出任务参数
        
    Returns:
        Dict: 导出结果
    """
    try:
        # 更新任务状态
        self.update_state(state=TaskStatus.STARTED, meta={'message': '开始导出文档'})
        
        # 解析任务参数
        content_data = task_data['content_data']
        export_formats = task_data['export_formats']
        template = task_data.get('template', 'standard')
        
        # 导出文档
        update_task_progress(50, 100, "正在导出文档...")
        
        # 使用同步方式调用导出服务
        from app.services.export import ExportService
        export_srv = ExportService()
        
        export_id = export_srv._create_export_sync(
            task_id=task_data.get('task_id', self.request.id),
            formats=export_formats,
            template=template,
            include_images=task_data.get('include_images', True),
            include_timestamps=task_data.get('include_timestamps', True),
            include_metadata=task_data.get('include_metadata', True),
            custom_filename=task_data.get('custom_filename')
        )
        
        # 完成
        update_task_progress(100, 100, "文档导出完成")
        
        result = {
            'export_id': export_id,
            'formats': export_formats,
            'exported_at': datetime.utcnow().isoformat()
        }
        
        return result
        
    except Exception as e:
        # 错误处理
        error_info = {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'task_id': self.request.id
        }
        
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=15, exc=e)
        
        self.update_state(state=TaskStatus.FAILURE, meta=error_info)
        raise


# 维护任务
@celery_app.task(name='app.services.queue_service.tasks.cleanup_expired_results')
def cleanup_expired_results():
    """清理过期的任务结果"""
    try:
        from celery import current_app
        from datetime import datetime, timedelta
        
        # 获取过期时间
        expire_time = datetime.utcnow() - timedelta(hours=24)
        
        # 清理逻辑（这里需要根据实际的结果存储实现）
        # 例如：清理Redis中的过期结果
        
        return {"cleaned_at": datetime.utcnow().isoformat()}
        
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='app.services.queue_service.tasks.generate_statistics')
def generate_statistics():
    """生成任务统计信息"""
    try:
        from .celery_app import get_queue_stats
        
        stats = get_queue_stats()
        stats['generated_at'] = datetime.utcnow().isoformat()
        
        return stats
        
    except Exception as e:
        return {"error": str(e)}


# 任务链功能
def create_video_processing_chain(video_file_path: str, output_dir: str) -> str:
    """
    创建完整的视频处理任务链
    
    Args:
        video_file_path: 视频文件路径
        output_dir: 输出目录
        
    Returns:
        str: 任务链ID
    """
    from celery import chain
    
    # 构建任务链
    task_chain = chain(
        # 1. 视频处理
        process_video_task.s({
            'video_file_path': video_file_path,
            'output_dir': output_dir,
            'extract_audio': True,
            'extract_frames': True
        }),
        
        # 2. 音频转录
        transcribe_audio_task.s(),
        
        # 3. 图像分析
        analyze_images_task.s(),
        
        # 4. 摘要生成
        generate_summary_task.s(),
        
        # 5. 文档导出
        export_document_task.s({
            'export_formats': ['markdown', 'pdf', 'html'],
            'template': 'standard'
        })
    )
    
    # 执行任务链
    result = task_chain.apply_async()
    
    return result.id


# 并行任务组
def create_parallel_analysis_group(audio_file: str, image_files: List[str]) -> str:
    """
    创建并行分析任务组
    
    Args:
        audio_file: 音频文件路径
        image_files: 图像文件列表
        
    Returns:
        str: 任务组ID
    """
    from celery import group
    
    # 构建并行任务组
    task_group = group(
        transcribe_audio_task.s({'audio_file_path': audio_file}),
        analyze_images_task.s({'image_paths': image_files})
    )
    
    # 执行任务组
    result = task_group.apply_async()
    
    return result.id 