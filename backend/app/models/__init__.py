"""
模型定义包
"""

# 导出基础模型
from app.models.base import (
    TaskStatus,
    OutputFormat,
    VideoUploadRequest,
    VideoProcessResponse,
    TaskStatusResponse,
    HealthResponse,
    ErrorResponse,
    VideoAnalysisResult
)

# 导出视频处理模型
from app.models.video_processing import (
    ProcessingStatus,
    ProcessingOptions,
    ProcessingTask,
    FrameInfo,
    ProcessingResult,
    ProcessingStatusResponse
) 