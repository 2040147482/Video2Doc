from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse
from app.models.base import (
    VideoUploadRequest, 
    VideoProcessResponse, 
    TaskStatusResponse,
    TaskStatus,
    ErrorResponse
)
from app.config import Settings, get_settings
from app.exceptions import (
    FileUploadError,
    FileSizeExceededError,
    UnsupportedFileFormatError,
    TaskNotFoundError,
    InvalidVideoUrlError
)
from app.services.file_service import file_service
from app.services.video_service import video_service
import uuid
from datetime import datetime
from typing import Optional
import os

router = APIRouter(prefix="/api", tags=["Video Processing"])

# 支持的视频格式
SUPPORTED_VIDEO_FORMATS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv"}

# 临时存储任务状态（生产环境应使用数据库）
tasks_storage = {}


def create_task(task_type: str, **kwargs) -> str:
    """创建新任务"""
    task_id = str(uuid.uuid4())
    
    tasks_storage[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "progress": 0,
        "message": "任务已创建，等待处理",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "task_type": task_type,
        "result_urls": None,
        "error_details": None,
        **kwargs
    }
    
    return task_id


def estimate_processing_time(
    task_type: str,
    file_size: Optional[int] = None,
    video_duration: Optional[int] = None,
    platform: Optional[str] = None
) -> int:
    """估算处理时间（秒）"""
    base_time = 60  # 基础时间1分钟
    
    if task_type == "file_upload" and file_size:
        # 基于文件大小估算：每100MB约需30秒
        size_factor = file_size / (100 * 1024 * 1024)  # 转换为100MB单位
        file_time = int(size_factor * 30)
        return max(base_time, file_time)
    
    elif task_type == "url_process":
        if platform:
            download_time = video_service.estimate_download_time(platform, video_duration)
            process_time = int(video_duration * 0.3) if video_duration else 120
            return download_time + process_time
    
    return base_time + (int(video_duration * 0.4) if video_duration else 180)


@router.post("/upload", response_model=VideoProcessResponse, summary="上传视频文件")
async def upload_video_file(
    file: UploadFile = File(..., description="视频文件"),
    language: str = Form("auto", description="视频语言"),
    output_formats: str = Form("markdown", description="输出格式（逗号分隔）"),
    settings: Settings = Depends(get_settings)
) -> VideoProcessResponse:
    """
    上传视频文件进行处理
    
    - **file**: 视频文件（支持 mp4, mov, avi, mkv, webm 等格式）
    - **language**: 视频语言（auto 为自动检测）
    - **output_formats**: 输出格式，多个格式用逗号分隔
    """
    try:
        # 验证文件基本信息
        if not file.filename:
            raise FileUploadError("文件名不能为空")
        
        # 验证文件格式
        file_service.validate_file_format(file.filename, SUPPORTED_VIDEO_FORMATS)
        
        # 创建任务ID
        task_id = create_task(
            task_type="file_upload",
            filename=file.filename,
            language=language,
            output_formats=output_formats.split(","),
            content_type=file.content_type
        )
        
        # 保存文件
        try:
            file_path, file_info = await file_service.save_upload_file(file, task_id)
            
            # 更新任务信息
            tasks_storage[task_id].update({
                "file_path": str(file_path),
                "file_info": file_info,
                "message": "文件上传成功，开始处理"
            })
            
            # 估算处理时间
            estimated_time = estimate_processing_time("file_upload", file_info["size"])
            
            return VideoProcessResponse(
                task_id=task_id,
                status=TaskStatus.PENDING,
                message="文件上传成功，开始处理",
                estimated_time=estimated_time
            )
            
        except (FileSizeExceededError, UnsupportedFileFormatError):
            # 清理失败的任务记录
            if task_id in tasks_storage:
                del tasks_storage[task_id]
            raise
            
    except (FileUploadError, FileSizeExceededError, UnsupportedFileFormatError):
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/upload-url", response_model=VideoProcessResponse, summary="处理视频链接")
async def process_video_url(
    request: VideoUploadRequest,
    settings: Settings = Depends(get_settings)
) -> VideoProcessResponse:
    """
    处理视频链接
    
    支持的平台：
    - YouTube (youtube.com, youtu.be)
    - 哔哩哔哩 (bilibili.com, b23.tv)
    - Vimeo (vimeo.com)
    """
    try:
        if not request.video_url:
            raise InvalidVideoUrlError("视频链接不能为空")
        
        url = str(request.video_url)
        
        # 验证并获取视频信息
        try:
            video_info = await video_service.get_video_info(url)
        except InvalidVideoUrlError:
            raise
        except Exception as e:
            raise InvalidVideoUrlError(f"获取视频信息失败: {str(e)}")
        
        # 创建任务
        task_id = create_task(
            task_type="url_process",
            video_url=url,
            video_name=request.video_name or video_info.get("title", "未知视频"),
            language=request.language,
            output_formats=[fmt.value for fmt in request.output_formats],
            video_info=video_info
        )
        
        # 估算处理时间
        estimated_time = estimate_processing_time(
            "url_process",
            video_duration=video_info.get("duration"),
            platform=video_info.get("platform")
        )
        
        # 更新任务状态
        tasks_storage[task_id].update({
            "message": f"视频链接解析成功，来自 {video_info.get('platform', '未知平台')}",
            "estimated_time": estimated_time
        })
        
        return VideoProcessResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message=f"视频链接解析成功: {video_info.get('title', '未知视频')}",
            estimated_time=estimated_time
        )
        
    except InvalidVideoUrlError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视频链接处理失败: {str(e)}")


@router.get("/status/{task_id}", response_model=TaskStatusResponse, summary="获取任务状态")
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    获取任务处理状态
    
    - **task_id**: 任务ID
    """
    if task_id not in tasks_storage:
        raise TaskNotFoundError(task_id)
    
    task_data = tasks_storage[task_id]
    
    return TaskStatusResponse(
        task_id=task_data["task_id"],
        status=task_data["status"],
        progress=task_data["progress"],
        message=task_data["message"],
        created_at=task_data["created_at"],
        updated_at=task_data["updated_at"],
        result_urls=task_data["result_urls"],
        error_details=task_data["error_details"]
    )


@router.get("/tasks", response_model=list[TaskStatusResponse], summary="获取所有任务")
async def get_all_tasks() -> list[TaskStatusResponse]:
    """获取所有任务状态（按创建时间倒序）"""
    tasks = []
    for task_data in tasks_storage.values():
        tasks.append(TaskStatusResponse(
            task_id=task_data["task_id"],
            status=task_data["status"],
            progress=task_data["progress"],
            message=task_data["message"],
            created_at=task_data["created_at"],
            updated_at=task_data["updated_at"],
            result_urls=task_data["result_urls"],
            error_details=task_data["error_details"]
        ))
    
    return sorted(tasks, key=lambda x: x.created_at, reverse=True)


@router.delete("/tasks/{task_id}", summary="删除任务")
async def delete_task(task_id: str) -> dict:
    """删除指定任务及其相关文件"""
    if task_id not in tasks_storage:
        raise TaskNotFoundError(task_id)
    
    task_data = tasks_storage[task_id]
    
    # 如果是文件上传任务，删除相关文件
    if task_data.get("task_type") == "file_upload" and task_data.get("file_path"):
        from pathlib import Path
        file_path = Path(task_data["file_path"])
        await file_service.delete_file(file_path)
    
    # 删除任务记录
    del tasks_storage[task_id]
    
    return {"message": f"任务 {task_id} 已删除"}


@router.get("/supported-formats", summary="获取支持的文件格式")
async def get_supported_formats() -> dict:
    """获取支持的视频文件格式和平台"""
    return {
        "video_formats": list(SUPPORTED_VIDEO_FORMATS),
        "video_platforms": list(video_service.SUPPORTED_PLATFORMS.keys()),
        "max_file_size": get_settings().max_file_size,
        "max_file_size_mb": get_settings().max_file_size // (1024 * 1024)
    } 