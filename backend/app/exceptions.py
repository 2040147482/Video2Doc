from fastapi import HTTPException, status
from typing import Optional, Any, Dict, Union
from fastapi.responses import JSONResponse


class VideoProcessingError(HTTPException):
    """视频处理异常"""
    def __init__(
        self, 
        detail: str = "视频处理失败", 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class FileUploadError(HTTPException):
    """文件上传异常"""
    def __init__(
        self, 
        detail: str = "文件上传失败", 
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class TaskNotFoundError(HTTPException):
    """任务未找到异常"""
    def __init__(
        self, 
        task_id: str,
        status_code: int = status.HTTP_404_NOT_FOUND,
        headers: Optional[Dict[str, Any]] = None
    ):
        detail = f"任务 {task_id} 未找到"
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class InvalidVideoUrlError(HTTPException):
    """无效视频链接异常"""
    def __init__(
        self, 
        url: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: Optional[Dict[str, Any]] = None
    ):
        detail = f"无效的视频链接: {url}"
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class FileSizeExceededError(HTTPException):
    """文件大小超限异常"""
    def __init__(
        self, 
        file_size: int,
        max_size: int,
        status_code: int = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        headers: Optional[Dict[str, Any]] = None
    ):
        detail = f"文件大小 {file_size} 字节超过限制 {max_size} 字节"
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UnsupportedFileFormatError(HTTPException):
    """不支持的文件格式异常"""
    def __init__(
        self, 
        file_format: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: Optional[Dict[str, Any]] = None
    ):
        detail = f"不支持的文件格式: {file_format}"
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AIServiceError(HTTPException):
    """AI服务异常"""
    def __init__(
        self, 
        service_name: str,
        detail: str = "AI服务调用失败",
        status_code: int = status.HTTP_502_BAD_GATEWAY,
        headers: Optional[Dict[str, Any]] = None
    ):
        full_detail = f"{service_name}: {detail}"
        super().__init__(status_code=status_code, detail=full_detail, headers=headers)


def create_error_response(
    status_code: int, 
    message: str, 
    details: Optional[Any] = None
) -> JSONResponse:
    """
    创建标准化错误响应
    
    Args:
        status_code: HTTP状态码
        message: 错误消息
        details: 错误详情
        
    Returns:
        JSONResponse: 标准化错误响应
    """
    from app.models.base import ErrorResponse
    from datetime import datetime
    
    error_content = ErrorResponse(
        error=f"error_{status_code}",
        message=message,
        details=str(details) if details else None,
        timestamp=datetime.now()
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_content.dict()
    ) 