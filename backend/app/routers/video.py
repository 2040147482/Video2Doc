from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse
from app.models import (
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
import uuid
from datetime import datetime
from typing import Optional
import os

router = APIRouter(prefix="/api", tags=["Video Processing"])

# 支持的视频格式
SUPPORTED_VIDEO_FORMATS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv"}

# 临时存储任务状态（生产环境应使用数据库）
tasks_storage = {}


def validate_video_file(file: UploadFile, max_size: int) -> None:
    """验证上传的视频文件"""
    if not file.filename:
        raise FileUploadError("文件名不能为空")
    
    # 检查文件扩展名
    file_ext = os.path.splitext(file.filename.lower())[1]
    if file_ext not in SUPPORTED_VIDEO_FORMATS:
        raise UnsupportedFileFormatError(file_ext)
    
    # 检查文件大小（这里只是基本检查，实际大小需要在读取时验证）
    if hasattr(file, 'size') and file.size and file.size > max_size:
        raise FileSizeExceededError(file.size, max_size)


def validate_video_url(url: str) -> None:
    """验证视频URL"""
    if not url or not url.strip():
        raise InvalidVideoUrlError("视频链接不能为空")
    
    # 基本URL格式验证
    supported_domains = ["youtube.com", "youtu.be", "bilibili.com", "vimeo.com"]
    if not any(domain in url.lower() for domain in supported_domains):
        raise InvalidVideoUrlError(f"暂不支持该视频平台: {url}")


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


def estimate_processing_time(video_duration: Optional[int] = None) -> int:
    """估算处理时间（秒）"""
    if video_duration:
        # 基于视频时长估算，通常为视频时长的30-50%
        return max(60, int(video_duration * 0.4))
    return 300  # 默认5分钟


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
        # 验证文件
        validate_video_file(file, settings.max_file_size)
        
        # 创建任务
        task_id = create_task(
            task_type="file_upload",
            filename=file.filename,
            language=language,
            output_formats=output_formats.split(",")
        )
        
        # 估算处理时间
        estimated_time = estimate_processing_time()
        
        # 这里应该启动异步处理任务（Celery）
        # 现在只是模拟
        
        return VideoProcessResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="文件上传成功，开始处理",
            estimated_time=estimated_time
        )
        
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
    - YouTube
    - 哔哩哔哩
    - Vimeo
    """
    try:
        if not request.video_url:
            raise InvalidVideoUrlError("视频链接不能为空")
        
        # 验证URL
        validate_video_url(str(request.video_url))
        
        # 创建任务
        task_id = create_task(
            task_type="url_process",
            video_url=str(request.video_url),
            video_name=request.video_name,
            language=request.language,
            output_formats=[fmt.value for fmt in request.output_formats]
        )
        
        # 估算处理时间
        estimated_time = estimate_processing_time()
        
        return VideoProcessResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="视频链接接收成功，开始处理",
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
    """获取所有任务状态"""
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