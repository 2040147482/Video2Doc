"""
自定义异常类和错误响应处理
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理datetime对象"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def create_error_response(
    status_code: int,
    message: str,
    details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
) -> JSONResponse:
    """
    创建标准化的错误响应
    
    Args:
        status_code: HTTP状态码
        message: 错误消息
        details: 错误详情
    
    Returns:
        JSONResponse: 标准化的错误响应
    """
    from app.models.base import ErrorResponse
    
    error_content = ErrorResponse(
        status_code=status_code,
        message=message,
        details=details
    ).model_dump()
    
    # 使用自定义编码器序列化内容
    content = json.dumps(error_content, cls=CustomJSONEncoder, ensure_ascii=False)
    
    return JSONResponse(
        status_code=status_code,
        content=content,
        media_type="application/json"
    )


# 自定义异常类
class VideoUploadException(HTTPException):
    """视频上传异常"""
    def __init__(self, detail: str = "视频上传失败"):
        super().__init__(status_code=400, detail=detail)


class FileSizeLimitException(HTTPException):
    """文件大小超限异常"""
    def __init__(self, detail: str = "文件大小超过限制"):
        super().__init__(status_code=413, detail=detail)


class FileTypeException(HTTPException):
    """文件类型异常"""
    def __init__(self, detail: str = "不支持的文件类型"):
        super().__init__(status_code=400, detail=detail)


class VideoProcessingException(HTTPException):
    """视频处理异常"""
    def __init__(self, detail: str = "视频处理失败"):
        super().__init__(status_code=500, detail=detail)


class SpeechRecognitionException(HTTPException):
    """语音识别异常"""
    def __init__(self, detail: str = "语音识别失败"):
        super().__init__(status_code=500, detail=detail)


class ImageRecognitionException(HTTPException):
    """图像识别异常"""
    def __init__(self, detail: str = "图像识别失败"):
        super().__init__(status_code=500, detail=detail)


class SummaryException(HTTPException):
    """摘要生成异常"""
    def __init__(self, detail: str = "摘要生成失败"):
        super().__init__(status_code=500, detail=detail)


class TaskNotFoundException(HTTPException):
    """任务未找到异常"""
    def __init__(self, detail: str = "任务未找到"):
        super().__init__(status_code=404, detail=detail)


class InvalidVideoUrlError(HTTPException):
    """无效视频URL异常"""
    def __init__(self, detail: str = "无效的视频URL"):
        super().__init__(status_code=400, detail=detail)


class VideoProcessingError(HTTPException):
    """视频处理错误异常"""
    def __init__(self, detail: str = "视频处理错误"):
        super().__init__(status_code=500, detail=detail) 