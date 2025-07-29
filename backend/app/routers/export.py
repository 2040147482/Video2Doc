"""
导出API路由
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Path as PathParam
from fastapi.responses import FileResponse

from app.models.base import (
    ExportRequest, ExportResponse, ExportStatus,
    OutputFormat, ExportTemplate
)
from app.services.export import export_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["Export"])


@router.post("", response_model=ExportResponse)
async def create_export(request: ExportRequest):
    """
    创建导出任务
    
    - **task_id**: 已完成的任务ID
    - **formats**: 导出格式列表 (markdown, pdf, html, txt, zip)
    - **template**: 导出模板 (standard, academic, presentation, simple, detailed)
    - **include_images**: 是否包含图片
    - **include_timestamps**: 是否包含时间戳
    - **include_metadata**: 是否包含元数据
    - **custom_filename**: 自定义文件名
    """
    logger.info(f"创建导出请求: {request.model_dump_json(indent=2)}")
    
    try:
        response = await export_service.create_export(request)
        logger.info(f"导出任务已创建: {response.export_id}")
        return response
        
    except ValueError as e:
        logger.warning(f"导出请求参数错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建导出任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建导出任务失败: {str(e)}")


@router.get("/status/{export_id}", response_model=ExportStatus)
async def get_export_status(export_id: str = PathParam(..., description="导出任务ID")):
    """
    获取导出任务状态
    
    - **export_id**: 导出任务ID
    """
    logger.info(f"获取导出状态: {export_id}")
    
    try:
        status = await export_service.get_export_status(export_id)
        return status
        
    except ValueError as e:
        logger.warning(f"导出任务不存在: {export_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取导出状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取导出状态失败: {str(e)}")


@router.delete("/{export_id}")
async def cancel_export(export_id: str = PathParam(..., description="导出任务ID")):
    """
    取消导出任务
    
    - **export_id**: 导出任务ID
    """
    logger.info(f"取消导出任务: {export_id}")
    
    try:
        success = await export_service.cancel_export(export_id)
        if success:
            return {"message": "导出任务已取消"}
        else:
            raise HTTPException(status_code=400, detail="无法取消该导出任务")
            
    except Exception as e:
        logger.error(f"取消导出任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"取消导出任务失败: {str(e)}")


@router.get("/download/{export_id}/{filename}")
async def download_export_file(
    export_id: str = PathParam(..., description="导出任务ID"),
    filename: str = PathParam(..., description="文件名")
):
    """
    下载导出文件
    
    - **export_id**: 导出任务ID
    - **filename**: 文件名
    """
    logger.info(f"下载导出文件: {export_id}/{filename}")
    
    try:
        file_path = export_service.get_export_file_path(export_id, filename)
        if not file_path:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 根据文件扩展名设置媒体类型
        media_type = _get_media_type(filename)
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")


@router.get("/formats", response_model=List[str])
async def get_supported_formats():
    """
    获取支持的导出格式
    """
    formats = export_service.get_supported_formats()
    return [format.value for format in formats]


@router.get("/templates", response_model=List[str])
async def get_available_templates():
    """
    获取可用的导出模板
    """
    templates = export_service.get_available_templates()
    return [template.value for template in templates]


def _get_media_type(filename: str) -> str:
    """根据文件名获取媒体类型"""
    extension = filename.lower().split('.')[-1]
    
    media_types = {
        'md': 'text/markdown',
        'html': 'text/html',
        'txt': 'text/plain',
        'pdf': 'application/pdf',
        'zip': 'application/zip',
        'json': 'application/json'
    }
    
    return media_types.get(extension, 'application/octet-stream') 