"""
云存储管理API路由
提供文件存储、管理和统计功能
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from pydantic import BaseModel

from app.services.enhanced_file_service import enhanced_file_service
from app.exceptions import create_error_response

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic 模型
class FileInfoResponse(BaseModel):
    """文件信息响应模型"""
    key: str
    size: int
    last_modified: str
    etag: str
    content_type: str
    metadata: Dict[str, str]


class FileListResponse(BaseModel):
    """文件列表响应模型"""
    files: List[FileInfoResponse]
    total_count: int
    prefix: str
    limit: int


class StorageStatsResponse(BaseModel):
    """存储统计响应模型"""
    storage_type: str
    total_files: int
    total_size: int
    total_size_mb: float
    file_types: Dict[str, Dict[str, int]]
    bucket_name: str


class UploadResponse(BaseModel):
    """文件上传响应模型"""
    storage_key: str
    original_filename: str
    size: int
    content_type: str
    etag: str
    uploaded_at: str
    metadata: Dict[str, str]
    storage_type: str


class PresignedUrlResponse(BaseModel):
    """预签名URL响应模型"""
    url: str
    expires_in: int
    operation: str


class CleanupResponse(BaseModel):
    """清理响应模型"""
    deleted_count: int
    max_age_days: int
    storage_name: Optional[str]


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    task_id: str,
    file: UploadFile = File(...),
    storage_name: Optional[str] = Query(None, description="存储实例名称"),
    metadata: Optional[str] = Query(None, description="JSON格式的自定义元数据")
):
    """
    上传文件到云存储
    
    Args:
        task_id: 任务ID
        file: 上传的文件
        storage_name: 存储实例名称（可选）
        metadata: 自定义元数据（JSON字符串）
    """
    try:
        # 解析元数据
        file_metadata = {}
        if metadata:
            import json
            try:
                file_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="元数据格式错误，必须是有效的JSON")
        
        # 上传文件
        result = await enhanced_file_service.upload_file(
            file=file,
            task_id=task_id,
            storage_name=storage_name,
            metadata=file_metadata
        )
        
        logger.info(f"文件上传成功: {result['storage_key']}")
        return UploadResponse(**result)
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.get("/files", response_model=FileListResponse)
async def list_files(
    prefix: str = Query("", description="文件键前缀"),
    limit: int = Query(100, ge=1, le=1000, description="最大返回数量"),
    storage_name: Optional[str] = Query(None, description="存储实例名称")
):
    """
    列出云存储中的文件
    
    Args:
        prefix: 文件键前缀
        limit: 最大返回数量
        storage_name: 存储实例名称
    """
    try:
        files = await enhanced_file_service.list_files(
            prefix=prefix,
            limit=limit,
            storage_name=storage_name
        )
        
        logger.info(f"获取文件列表成功: {len(files)} 个文件")
        
        return FileListResponse(
            files=[FileInfoResponse(**file_info) for file_info in files],
            total_count=len(files),
            prefix=prefix,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


@router.get("/files/{storage_key:path}", response_model=FileInfoResponse)
async def get_file_info(
    storage_key: str,
    storage_name: Optional[str] = Query(None, description="存储实例名称")
):
    """
    获取指定文件的详细信息
    
    Args:
        storage_key: 存储对象键
        storage_name: 存储实例名称
    """
    try:
        file_info = await enhanced_file_service.get_file_info(
            storage_key=storage_key,
            storage_name=storage_name
        )
        
        if not file_info:
            raise HTTPException(status_code=404, detail=f"文件不存在: {storage_key}")
        
        logger.info(f"获取文件信息成功: {storage_key}")
        return FileInfoResponse(**file_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文件信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文件信息失败: {str(e)}")


@router.delete("/files/{storage_key:path}")
async def delete_file(
    storage_key: str,
    storage_name: Optional[str] = Query(None, description="存储实例名称")
):
    """
    删除指定文件
    
    Args:
        storage_key: 存储对象键
        storage_name: 存储实例名称
    """
    try:
        success = await enhanced_file_service.delete_file(
            storage_key=storage_key,
            storage_name=storage_name
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"文件不存在或删除失败: {storage_key}")
        
        logger.info(f"文件删除成功: {storage_key}")
        return {"message": "文件删除成功", "storage_key": storage_key}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件删除失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")


@router.get("/download-url/{storage_key:path}", response_model=PresignedUrlResponse)
async def generate_download_url(
    storage_key: str,
    expires_in: int = Query(3600, ge=60, le=86400, description="URL过期时间（秒）"),
    storage_name: Optional[str] = Query(None, description="存储实例名称")
):
    """
    生成文件下载URL
    
    Args:
        storage_key: 存储对象键
        expires_in: URL过期时间（秒）
        storage_name: 存储实例名称
    """
    try:
        url = await enhanced_file_service.generate_download_url(
            storage_key=storage_key,
            expires_in=expires_in,
            storage_name=storage_name
        )
        
        logger.info(f"生成下载URL成功: {storage_key}")
        
        return PresignedUrlResponse(
            url=url,
            expires_in=expires_in,
            operation="download"
        )
        
    except Exception as e:
        logger.error(f"生成下载URL失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成下载URL失败: {str(e)}")


@router.get("/upload-url/{storage_key:path}", response_model=PresignedUrlResponse)
async def generate_upload_url(
    storage_key: str,
    expires_in: int = Query(3600, ge=60, le=86400, description="URL过期时间（秒）"),
    storage_name: Optional[str] = Query(None, description="存储实例名称")
):
    """
    生成文件上传URL
    
    Args:
        storage_key: 存储对象键
        expires_in: URL过期时间（秒）
        storage_name: 存储实例名称
    """
    try:
        url = await enhanced_file_service.generate_upload_url(
            storage_key=storage_key,
            expires_in=expires_in,
            storage_name=storage_name
        )
        
        logger.info(f"生成上传URL成功: {storage_key}")
        
        return PresignedUrlResponse(
            url=url,
            expires_in=expires_in,
            operation="upload"
        )
        
    except Exception as e:
        logger.error(f"生成上传URL失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成上传URL失败: {str(e)}")


@router.post("/copy")
async def copy_file(
    source_key: str,
    dest_key: str,
    storage_name: Optional[str] = Query(None, description="存储实例名称")
):
    """
    复制文件
    
    Args:
        source_key: 源文件键
        dest_key: 目标文件键
        storage_name: 存储实例名称
    """
    try:
        result = await enhanced_file_service.copy_file(
            source_key=source_key,
            dest_key=dest_key,
            storage_name=storage_name
        )
        
        logger.info(f"文件复制成功: {source_key} -> {dest_key}")
        
        return {
            "message": "文件复制成功",
            "source_key": source_key,
            "dest_key": dest_key,
            "file_info": result
        }
        
    except Exception as e:
        logger.error(f"文件复制失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件复制失败: {str(e)}")


@router.get("/stats", response_model=StorageStatsResponse)
async def get_storage_stats(
    storage_name: Optional[str] = Query(None, description="存储实例名称")
):
    """
    获取存储统计信息
    
    Args:
        storage_name: 存储实例名称
    """
    try:
        stats = await enhanced_file_service.get_storage_stats(storage_name=storage_name)
        
        logger.info(f"获取存储统计成功: {stats['storage_type']}")
        return StorageStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"获取存储统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取存储统计失败: {str(e)}")


@router.post("/cleanup", response_model=CleanupResponse)
async def cleanup_expired_files(
    max_age_days: int = Query(7, ge=1, le=365, description="最大保存天数"),
    storage_name: Optional[str] = Query(None, description="存储实例名称")
):
    """
    清理过期文件
    
    Args:
        max_age_days: 最大保存天数
        storage_name: 存储实例名称
    """
    try:
        deleted_count = await enhanced_file_service.cleanup_expired_files(
            max_age_days=max_age_days,
            storage_name=storage_name
        )
        
        logger.info(f"文件清理完成: 删除了 {deleted_count} 个过期文件")
        
        return CleanupResponse(
            deleted_count=deleted_count,
            max_age_days=max_age_days,
            storage_name=storage_name
        )
        
    except Exception as e:
        logger.error(f"文件清理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件清理失败: {str(e)}")


@router.get("/health")
async def storage_health_check():
    """
    存储系统健康检查
    """
    try:
        # 检查默认存储是否可用
        storage = enhanced_file_service.get_storage()
        
        # 尝试列出文件来测试连接
        await storage.list_files(limit=1)
        
        return {
            "status": "healthy",
            "storage_type": type(storage).__name__,
            "bucket_name": storage.bucket_name,
            "timestamp": f"{logger.info('存储健康检查通过')}"
        }
        
    except Exception as e:
        logger.error(f"存储健康检查失败: {str(e)}")
        raise HTTPException(status_code=503, detail=f"存储服务不可用: {str(e)}") 