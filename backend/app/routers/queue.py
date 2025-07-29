"""
队列管理API路由
提供任务队列的管理和监控接口
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.models.base import ErrorResponse
from app.exceptions import create_error_response
from app.services.queue_service import (
    task_manager, TaskStatus, TaskPriority,
    VideoProcessingTask, AudioTranscriptionTask, ImageAnalysisTask,
    SummaryGenerationTask, DocumentExportTask, TaskStatistics
)

router = APIRouter(tags=["队列管理"])


# 请求模型
class VideoProcessingRequest(BaseModel):
    """视频处理请求"""
    video_file_path: str
    output_dir: str
    extract_audio: bool = True
    extract_frames: bool = True
    frame_interval: int = 30
    priority: TaskPriority = TaskPriority.NORMAL


class AudioTranscriptionRequest(BaseModel):
    """音频转录请求"""
    audio_file_path: str
    language: Optional[str] = None
    model: str = "whisper-base"
    with_timestamps: bool = True
    priority: TaskPriority = TaskPriority.NORMAL


class ImageAnalysisRequest(BaseModel):
    """图像分析请求"""
    image_paths: List[str]
    analysis_types: List[str] = ["ocr", "scene"]
    priority: TaskPriority = TaskPriority.NORMAL


class SummaryGenerationRequest(BaseModel):
    """摘要生成请求"""
    transcript_data: Dict[str, Any]
    image_analysis_data: Optional[Dict[str, Any]] = None
    summary_type: str = "detailed"
    max_length: int = 1000
    language: str = "zh"
    priority: TaskPriority = TaskPriority.HIGH


class DocumentExportRequest(BaseModel):
    """文档导出请求"""
    content_data: Dict[str, Any]
    export_formats: List[str]
    template: str = "standard"
    include_images: bool = True
    include_timestamps: bool = True
    include_metadata: bool = True
    custom_filename: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL


class CompleteWorkflowRequest(BaseModel):
    """完整工作流请求"""
    video_file_path: str
    output_dir: str
    export_formats: List[str] = ["markdown", "html", "pdf"]


# 响应模型
class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    status: str
    message: str


class WorkflowResponse(BaseModel):
    """工作流响应"""
    workflow_id: str
    video_task_id: str
    base_id: str
    message: str


# 基础任务提交接口

@router.post("/tasks/video", response_model=TaskResponse)
async def submit_video_processing_task(request: VideoProcessingRequest):
    """提交视频处理任务"""
    try:
        import uuid
        task_id = str(uuid.uuid4())
        
        task_params = VideoProcessingTask(
            task_id=task_id,
            video_file_path=request.video_file_path,
            output_dir=request.output_dir,
            extract_audio=request.extract_audio,
            extract_frames=request.extract_frames,
            frame_interval=request.frame_interval,
            priority=request.priority
        )
        
        submitted_task_id = task_manager.submit_video_processing(task_params)
        
        return TaskResponse(
            task_id=submitted_task_id,
            status="submitted",
            message="视频处理任务已提交"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/audio", response_model=TaskResponse)
async def submit_audio_transcription_task(request: AudioTranscriptionRequest):
    """提交音频转录任务"""
    try:
        import uuid
        task_id = str(uuid.uuid4())
        
        task_params = AudioTranscriptionTask(
            task_id=task_id,
            audio_file_path=request.audio_file_path,
            language=request.language,
            model=request.model,
            with_timestamps=request.with_timestamps,
            priority=request.priority
        )
        
        submitted_task_id = task_manager.submit_audio_transcription(task_params)
        
        return TaskResponse(
            task_id=submitted_task_id,
            status="submitted",
            message="音频转录任务已提交"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/image", response_model=TaskResponse)
async def submit_image_analysis_task(request: ImageAnalysisRequest):
    """提交图像分析任务"""
    try:
        import uuid
        task_id = str(uuid.uuid4())
        
        task_params = ImageAnalysisTask(
            task_id=task_id,
            image_paths=request.image_paths,
            analysis_types=request.analysis_types,
            priority=request.priority
        )
        
        submitted_task_id = task_manager.submit_image_analysis(task_params)
        
        return TaskResponse(
            task_id=submitted_task_id,
            status="submitted",
            message="图像分析任务已提交"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/summary", response_model=TaskResponse)
async def submit_summary_generation_task(request: SummaryGenerationRequest):
    """提交摘要生成任务"""
    try:
        import uuid
        task_id = str(uuid.uuid4())
        
        task_params = SummaryGenerationTask(
            task_id=task_id,
            transcript_data=request.transcript_data,
            image_analysis_data=request.image_analysis_data,
            summary_type=request.summary_type,
            max_length=request.max_length,
            language=request.language,
            priority=request.priority
        )
        
        submitted_task_id = task_manager.submit_summary_generation(task_params)
        
        return TaskResponse(
            task_id=submitted_task_id,
            status="submitted",
            message="摘要生成任务已提交"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/export", response_model=TaskResponse)
async def submit_document_export_task(request: DocumentExportRequest):
    """提交文档导出任务"""
    try:
        import uuid
        task_id = str(uuid.uuid4())
        
        task_params = DocumentExportTask(
            task_id=task_id,
            content_data=request.content_data,
            export_formats=request.export_formats,
            template=request.template,
            include_images=request.include_images,
            include_timestamps=request.include_timestamps,
            include_metadata=request.include_metadata,
            custom_filename=request.custom_filename,
            priority=request.priority
        )
        
        submitted_task_id = task_manager.submit_document_export(task_params)
        
        return TaskResponse(
            task_id=submitted_task_id,
            status="submitted",
            message="文档导出任务已提交"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 复合工作流接口

@router.post("/workflows/complete", response_model=WorkflowResponse)
async def submit_complete_workflow(request: CompleteWorkflowRequest):
    """提交完整的视频分析工作流"""
    try:
        result = task_manager.submit_complete_video_analysis(
            video_file_path=request.video_file_path,
            output_dir=request.output_dir,
            export_formats=request.export_formats
        )
        
        return WorkflowResponse(
            workflow_id=result["workflow_id"],
            video_task_id=result["video_task_id"],
            base_id=result["base_id"],
            message="完整工作流已启动"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/parallel")
async def submit_parallel_analysis(
    audio_file_path: str,
    image_paths: List[str]
):
    """提交并行分析工作流"""
    try:
        task_group_id = task_manager.submit_parallel_analysis(
            audio_file_path=audio_file_path,
            image_paths=image_paths
        )
        
        return {
            "task_group_id": task_group_id,
            "message": "并行分析任务组已启动"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 任务状态查询接口

@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """获取任务状态"""
    try:
        task_result = task_manager.get_task_status(task_id)
        return task_result.dict()
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")


@router.get("/tasks/{task_id}/info")
async def get_task_info(task_id: str):
    """获取任务详细信息"""
    try:
        task_info = task_manager.get_task_info(task_id)
        return task_info
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")


@router.get("/groups/{group_id}/status")
async def get_group_status(group_id: str):
    """获取任务组状态"""
    try:
        group_status = task_manager.get_group_status(group_id)
        return group_status
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"任务组不存在: {group_id}")


# 任务控制接口

@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str, terminate: bool = False):
    """取消任务"""
    try:
        success = task_manager.cancel_task(task_id, terminate=terminate)
        
        if success:
            return {"message": f"任务 {task_id} 已取消"}
        else:
            raise HTTPException(status_code=400, detail="任务取消失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/retry")
async def retry_task(task_id: str):
    """重试失败的任务"""
    try:
        new_task_id = task_manager.retry_task(task_id)
        
        return {
            "new_task_id": new_task_id,
            "message": f"任务已重新提交: {new_task_id}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queues/{queue_name}/pause")
async def pause_queue(queue_name: str):
    """暂停队列"""
    try:
        success = task_manager.pause_queue(queue_name)
        
        if success:
            return {"message": f"队列 {queue_name} 已暂停"}
        else:
            raise HTTPException(status_code=400, detail="队列暂停失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queues/{queue_name}/resume")
async def resume_queue(queue_name: str):
    """恢复队列"""
    try:
        success = task_manager.resume_queue(queue_name)
        
        if success:
            return {"message": f"队列 {queue_name} 已恢复"}
        else:
            raise HTTPException(status_code=400, detail="队列恢复失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 监控和统计接口

@router.get("/statistics", response_model=TaskStatistics)
async def get_task_statistics():
    """获取任务统计信息"""
    try:
        stats = task_manager.generate_task_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workers")
async def get_worker_info():
    """获取工作者信息"""
    try:
        workers = task_manager.get_worker_info()
        return {"workers": [worker.dict() for worker in workers]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/active")
async def get_active_tasks():
    """获取活跃任务列表"""
    try:
        tasks = task_manager.get_active_tasks()
        return {"active_tasks": tasks}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/scheduled")
async def get_scheduled_tasks():
    """获取计划任务列表"""
    try:
        tasks = task_manager.get_scheduled_tasks()
        return {"scheduled_tasks": tasks}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queues/stats")
async def get_queue_statistics():
    """获取队列统计信息"""
    try:
        stats = task_manager.get_queue_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 管理接口

@router.get("/health")
async def health_check():
    """队列系统健康检查"""
    try:
        health = task_manager.health_check()
        return health
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queues/{queue_name}/purge")
async def purge_queue(queue_name: str):
    """清空队列"""
    try:
        count = task_manager.purge_queue(queue_name)
        return {
            "message": f"队列 {queue_name} 已清空",
            "purged_count": count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workers/restart")
async def restart_workers():
    """重启工作者"""
    try:
        success = task_manager.restart_workers()
        
        if success:
            return {"message": "工作者重启命令已发送"}
        else:
            raise HTTPException(status_code=400, detail="工作者重启失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 