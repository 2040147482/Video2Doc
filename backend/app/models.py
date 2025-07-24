from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OutputFormat(str, Enum):
    """输出格式枚举"""
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"
    TXT = "txt"
    ZIP = "zip"


class VideoUploadRequest(BaseModel):
    """视频上传请求模型"""
    video_url: Optional[HttpUrl] = Field(None, description="视频链接")
    video_name: Optional[str] = Field(None, max_length=255, description="视频名称")
    language: str = Field("auto", description="视频语言")
    output_formats: List[OutputFormat] = Field(
        default=[OutputFormat.MARKDOWN], 
        description="输出格式列表"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_url": "https://www.youtube.com/watch?v=example",
                "video_name": "示例视频",
                "language": "zh-CN",
                "output_formats": ["markdown", "pdf"]
            }
        }


class VideoProcessResponse(BaseModel):
    """视频处理响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    message: str = Field(..., description="状态消息")
    estimated_time: Optional[int] = Field(None, description="预估处理时间(秒)")


class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: str
    status: TaskStatus
    progress: int = Field(..., ge=0, le=100, description="进度百分比")
    message: str
    created_at: datetime
    updated_at: datetime
    result_urls: Optional[List[str]] = Field(None, description="结果文件下载链接")
    error_details: Optional[str] = Field(None, description="错误详情")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: Literal["ok", "error"] = Field(..., description="服务状态")
    message: str = Field(..., description="状态消息")
    version: str = Field(..., description="API版本")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Optional[str] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")


class VideoAnalysisResult(BaseModel):
    """视频分析结果模型"""
    task_id: str
    video_info: dict = Field(..., description="视频基本信息")
    transcript: str = Field(..., description="语音转文字结果")
    summary: str = Field(..., description="AI生成摘要")
    key_frames: List[dict] = Field(default_factory=list, description="关键帧信息")
    chapters: List[dict] = Field(default_factory=list, description="章节划分")
    output_files: dict = Field(..., description="输出文件路径") 