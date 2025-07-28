"""
视频处理路由模块
负责处理视频处理相关API端点
"""

import uuid
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query

# 修改导入路径
from app.models.video_processing import (
    ProcessingOptions, 
    ProcessingTask, 
    ProcessingResult,
    ProcessingStatus,
    ProcessingStatusResponse
)
from app.services.queue_service import queue_service
from app.services.storage_service import storage_service
from app.config import Settings, get_settings

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(prefix="/processing", tags=["processing"])

@router.post("/start", response_model=ProcessingStatusResponse)
async def start_processing(
    task_id: str,
    options: ProcessingOptions,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings)
):
    """
    开始视频处理
    
    Args:
        task_id: 任务ID
        options: 处理选项
        background_tasks: 后台任务
        settings: 应用设置
        
    Returns:
        处理状态响应
    """
    # 获取任务信息
    task_data = queue_service.get_task(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    # 创建处理任务
    processing_task = ProcessingTask(
        task_id=task_id,
        file_path=task_data.get("file_path"),
        video_url=task_data.get("video_url"),
        options=options,
        status=ProcessingStatus.PENDING
    )
    
    # 更新任务状态
    queue_service.update_task_status(
        task_id=task_id,
        status=ProcessingStatus.PENDING,
        progress=0.0,
        message="任务已加入队列，等待处理"
    )
    
    # 将任务加入队列
    # 注意：这里使用了后台任务而不是直接调用Celery
    # 在实际生产环境中，应该使用Celery或其他任务队列
    background_tasks.add_task(
        process_video_task,
        task_id,
        processing_task.dict()
    )
    
    return ProcessingStatusResponse(
        task_id=task_id,
        status=ProcessingStatus.PENDING,
        progress=0.0,
        message="任务已加入队列，等待处理"
    )

@router.get("/status/{task_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(
    task_id: str,
    settings: Settings = Depends(get_settings)
):
    """
    获取处理状态
    
    Args:
        task_id: 任务ID
        settings: 应用设置
        
    Returns:
        处理状态响应
    """
    # 获取任务信息
    task_data = queue_service.get_task(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    # 获取结果（如果已完成）
    result = None
    if task_data.get("status") == ProcessingStatus.COMPLETED:
        result_data = await storage_service.get_processing_result(task_id)
        if result_data:
            result = ProcessingResult(**result_data)
    
    return ProcessingStatusResponse(
        task_id=task_id,
        status=task_data.get("status", ProcessingStatus.PENDING),
        progress=task_data.get("progress", 0.0),
        message=task_data.get("message", ""),
        estimated_time_remaining=task_data.get("estimated_time_remaining"),
        result=result
    )

@router.get("/result/{task_id}", response_model=ProcessingResult)
async def get_processing_result(
    task_id: str,
    settings: Settings = Depends(get_settings)
):
    """
    获取处理结果
    
    Args:
        task_id: 任务ID
        settings: 应用设置
        
    Returns:
        处理结果
    """
    # 获取任务信息
    task_data = queue_service.get_task(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    # 检查任务状态
    if task_data.get("status") != ProcessingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"任务 {task_id} 尚未完成")
    
    # 获取结果
    result_data = await storage_service.get_processing_result(task_id)
    if not result_data:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 的结果不存在")
    
    return ProcessingResult(**result_data)

@router.delete("/{task_id}", response_model=Dict[str, bool])
async def cancel_processing(
    task_id: str,
    settings: Settings = Depends(get_settings)
):
    """
    取消处理任务
    
    Args:
        task_id: 任务ID
        settings: 应用设置
        
    Returns:
        操作结果
    """
    # 获取任务信息
    task_data = queue_service.get_task(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    # 检查任务状态
    status = task_data.get("status")
    if status == ProcessingStatus.COMPLETED or status == ProcessingStatus.FAILED:
        raise HTTPException(status_code=400, detail=f"任务 {task_id} 已经处理完成或失败，无法取消")
    
    # 更新任务状态
    queue_service.update_task_status(
        task_id=task_id,
        status=ProcessingStatus.CANCELLED,
        message="任务已取消"
    )
    
    return {"success": True}

@router.get("/tasks", response_model=List[ProcessingStatusResponse])
async def get_all_processing_tasks(
    status: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    settings: Settings = Depends(get_settings)
):
    """
    获取所有处理任务
    
    Args:
        status: 过滤状态
        limit: 限制数量
        offset: 偏移量
        settings: 应用设置
        
    Returns:
        处理任务列表
    """
    # 获取所有任务
    all_tasks = queue_service.get_all_tasks()
    
    # 过滤任务
    if status:
        filtered_tasks = [task for task in all_tasks if task.get("status") == status]
    else:
        filtered_tasks = all_tasks
    
    # 分页
    paginated_tasks = filtered_tasks[offset:offset + limit]
    
    # 转换为响应模型
    response_tasks = []
    for task_data in paginated_tasks:
        task_id = task_data.get("task_id")
        result = None
        
        # 获取结果（如果已完成）
        if task_data.get("status") == ProcessingStatus.COMPLETED:
            result_data = await storage_service.get_processing_result(task_id)
            if result_data:
                result = ProcessingResult(**result_data)
        
        response_tasks.append(
            ProcessingStatusResponse(
                task_id=task_id,
                status=task_data.get("status", ProcessingStatus.PENDING),
                progress=task_data.get("progress", 0.0),
                message=task_data.get("message", ""),
                estimated_time_remaining=task_data.get("estimated_time_remaining"),
                result=result
            )
        )
    
    return response_tasks

# 后台处理函数（实际生产环境应该放在worker.py中）
async def process_video_task(task_id: str, task_data: Dict[str, Any]):
    """
    处理视频任务
    
    Args:
        task_id: 任务ID
        task_data: 任务数据
    """
    from app.services.video_processor.extractor import video_extractor
    from app.services.video_processor.analyzer import video_analyzer
    
    try:
        # 更新任务状态
        queue_service.update_task_status(
            task_id=task_id,
            status=ProcessingStatus.EXTRACTING,
            progress=0.1,
            message="正在提取视频信息..."
        )
        
        # 获取视频路径
        video_path = task_data.get("file_path")
        if not video_path:
            raise ValueError("视频路径不能为空")
        
        # 获取视频元数据
        metadata = await video_analyzer.get_video_metadata(video_path)
        
        # 更新任务状态
        queue_service.update_task_status(
            task_id=task_id,
            status=ProcessingStatus.PROCESSING_AUDIO,
            progress=0.2,
            message="正在提取音频..."
        )
        
        # 提取音频
        options = task_data.get("options", {})
        if options.get("extract_audio", True):
            audio_path = await video_extractor.extract_audio(video_path)
        else:
            audio_path = None
        
        # 更新任务状态
        queue_service.update_task_status(
            task_id=task_id,
            status=ProcessingStatus.PROCESSING_FRAMES,
            progress=0.4,
            message="正在提取视频帧..."
        )
        
        # 提取帧
        frames = []
        if options.get("extract_frames", True):
            frame_interval = options.get("frame_interval", 5)
            detect_scenes = options.get("detect_scenes", False)
            frames = await video_extractor.extract_frames(
                video_path,
                interval=frame_interval,
                detect_scenes=detect_scenes
            )
        
        # 更新任务状态
        queue_service.update_task_status(
            task_id=task_id,
            status=ProcessingStatus.GENERATING_OUTPUT,
            progress=0.8,
            message="正在生成输出..."
        )
        
        # 创建结果数据
        # 注意：这里只是一个简单的示例，实际应用中应该有更复杂的处理逻辑
        result_data = {
            "task_id": task_id,
            "status": ProcessingStatus.COMPLETED,
            "metadata": metadata,
            "frames": frames,
            "transcript": "这是一个示例转录文本",  # 实际应该调用语音识别服务
            "summary": "这是一个示例摘要",  # 实际应该调用AI摘要服务
            "markdown_content": "# 视频分析结果\n\n## 摘要\n\n这是一个示例摘要\n\n## 转录\n\n这是一个示例转录文本",
            "text_content": "视频分析结果\n\n摘要\n\n这是一个示例摘要\n\n转录\n\n这是一个示例转录文本"
        }
        
        # 保存结果
        output_files = await storage_service.save_processing_result(task_id, result_data)
        result_data["output_files"] = output_files
        
        # 更新任务状态
        queue_service.update_task_status(
            task_id=task_id,
            status=ProcessingStatus.COMPLETED,
            progress=1.0,
            message="处理完成"
        )
        
        logger.info(f"任务处理成功: {task_id}")
    except Exception as e:
        logger.error(f"任务处理失败 {task_id}: {str(e)}")
        
        # 更新任务状态
        queue_service.update_task_status(
            task_id=task_id,
            status=ProcessingStatus.FAILED,
            progress=0.0,
            message=f"处理失败: {str(e)}",
            error=str(e)
        ) 