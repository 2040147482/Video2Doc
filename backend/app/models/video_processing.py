from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ProcessingStatus(str, Enum):
    """视频处理状态枚举"""
    PENDING = "pending"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    PROCESSING_AUDIO = "processing_audio"
    PROCESSING_FRAMES = "processing_frames"
    GENERATING_OUTPUT = "generating_output"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProcessingOptions(BaseModel):
    """视频处理选项"""
    extract_audio: bool = True
    extract_frames: bool = True
    frame_interval: int = 5  # 每隔多少秒提取一帧
    detect_scenes: bool = True  # 是否基于场景变化检测关键帧
    language: str = "auto"
    output_formats: List[str] = Field(default_factory=lambda: ["markdown"])
    
    class Config:
        json_schema_extra = {
            "example": {
                "extract_audio": True,
                "extract_frames": True,
                "frame_interval": 5,
                "detect_scenes": True,
                "language": "zh-CN",
                "output_formats": ["markdown", "pdf"]
            }
        }

class ProcessingTask(BaseModel):
    """视频处理任务"""
    task_id: str
    file_path: Optional[str] = None
    video_url: Optional[str] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    progress: float = 0.0
    options: ProcessingOptions
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_123456789",
                "file_path": "/uploads/video123.mp4",
                "status": "pending",
                "progress": 0.0,
                "options": {
                    "extract_audio": True,
                    "extract_frames": True,
                    "frame_interval": 5,
                    "detect_scenes": True,
                    "language": "zh-CN",
                    "output_formats": ["markdown"]
                },
                "created_at": "2023-07-26T12:00:00",
                "updated_at": "2023-07-26T12:00:00"
            }
        }

class FrameInfo(BaseModel):
    """视频帧信息"""
    path: str
    timestamp: int
    timestamp_formatted: str
    frame_number: int
    text_content: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "path": "/temp/frames/frame_0001.jpg",
                "timestamp": 5,
                "timestamp_formatted": "00:00:05",
                "frame_number": 1,
                "text_content": "检测到的文本内容",
                "description": "一个人站在讲台前讲解幻灯片"
            }
        }

class ProcessingResult(BaseModel):
    """视频处理结果"""
    task_id: str
    status: ProcessingStatus
    output_files: Dict[str, str] = Field(default_factory=dict)  # 格式 -> 文件路径
    transcript: Optional[str] = None
    summary: Optional[str] = None
    frames: List[FrameInfo] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_123456789",
                "status": "completed",
                "output_files": {
                    "markdown": "/results/output_123456789.md",
                    "pdf": "/results/output_123456789.pdf"
                },
                "transcript": "这是视频的完整转录内容...",
                "summary": "这是视频内容的摘要...",
                "frames": [
                    {
                        "path": "/temp/frames/frame_0001.jpg",
                        "timestamp": 5,
                        "timestamp_formatted": "00:00:05",
                        "frame_number": 1,
                        "text_content": "检测到的文本内容",
                        "description": "一个人站在讲台前讲解幻灯片"
                    }
                ],
                "created_at": "2023-07-26T12:30:00"
            }
        }

class ProcessingStatusResponse(BaseModel):
    """处理状态响应"""
    task_id: str
    status: ProcessingStatus
    progress: float
    message: str
    estimated_time_remaining: Optional[int] = None  # 剩余时间（秒）
    result: Optional[ProcessingResult] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_123456789",
                "status": "processing_audio",
                "progress": 0.45,
                "message": "正在处理音频...",
                "estimated_time_remaining": 120
            }
        } 