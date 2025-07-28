"""
图像识别API路由模块
"""

import os
import logging
import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.image_recognition import default_service, ImageAnalysisResult
from app.services.file_service import file_service
from app.services.queue_service import queue_service
from app.config import Settings, get_settings

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(prefix="/image-recognition", tags=["image-recognition"])

# Pydantic模型定义
class ImageAnalysisRequest(BaseModel):
    """图像分析请求模型"""
    enable_ocr: bool = Field(True, description="是否启用OCR文字识别")
    enable_scene_analysis: bool = Field(True, description="是否启用场景分析")
    enable_object_detection: bool = Field(True, description="是否启用目标检测")
    language: str = Field("auto", description="OCR语言，如: auto, zh-cn, en")
    detail_level: str = Field("medium", description="场景分析详细程度: low, medium, high")

class ImageAnalysisResponse(BaseModel):
    """图像分析响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="响应消息")

class ImageAnalysisStatusResponse(BaseModel):
    """图像分析状态响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    progress: float = Field(..., description="处理进度 (0-100)")
    result: Optional[Dict[str, Any]] = Field(None, description="分析结果")
    error: Optional[str] = Field(None, description="错误信息")

class BatchAnalysisRequest(BaseModel):
    """批量分析请求模型"""
    frame_paths: List[str] = Field(..., description="帧图像文件路径列表")
    analysis_options: Optional[Dict[str, Any]] = Field(None, description="分析选项")

class BatchAnalysisResponse(BaseModel):
    """批量分析响应模型"""
    task_id: str = Field(..., description="任务ID")
    total_frames: int = Field(..., description="总帧数")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="响应消息")

# API路由定义
@router.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_image_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    enable_ocr: bool = Form(True),
    enable_scene_analysis: bool = Form(True),
    enable_object_detection: bool = Form(True),
    language: str = Form("auto"),
    detail_level: str = Form("medium"),
    settings: Settings = Depends(get_settings)
):
    """
    分析上传的图像文件
    """
    task_id = f"image_analysis_{uuid.uuid4().hex}"
    
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只支持图像文件")
        
        # 保存上传的文件
        image_path, file_info = await file_service.save_upload_file(file, task_id)
        logger.info(f"图像文件已保存: {image_path}")
        
        # 创建任务
        task_data = {
            "task_id": task_id,
            "type": "image_analysis",
            "status": "pending",
            "progress": 0.0,
            "file_path": str(image_path),
            "file_info": file_info,
            "analysis_options": {
                "enable_ocr": enable_ocr,
                "enable_scene_analysis": enable_scene_analysis,
                "enable_object_detection": enable_object_detection,
                "language": language,
                "detail_level": detail_level
            }
        }
        
        queue_service.create_task(task_data)
        logger.info(f"图像分析任务已创建: {task_id}")
        
        # 启动后台处理
        background_tasks.add_task(_process_image_analysis, task_id)
        
        return ImageAnalysisResponse(
            task_id=task_id,
            status="pending",
            message="图像分析任务已启动"
        )
        
    except Exception as e:
        logger.error(f"图像分析请求处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"图像分析请求处理失败: {str(e)}")

@router.get("/status/{task_id}", response_model=ImageAnalysisStatusResponse)
async def get_analysis_status(task_id: str):
    """
    获取图像分析任务状态
    """
    try:
        task = queue_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        result = None
        if task.get("status") == "completed" and "result" in task:
            result = task["result"]
        
        return ImageAnalysisStatusResponse(
            task_id=task_id,
            status=task.get("status", "unknown"),
            progress=task.get("progress", 0.0),
            result=result,
            error=task.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")

@router.post("/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze_images(
    background_tasks: BackgroundTasks,
    request: BatchAnalysisRequest,
    settings: Settings = Depends(get_settings)
):
    """
    批量分析图像帧
    """
    task_id = f"batch_analysis_{uuid.uuid4().hex}"
    
    try:
        # 验证帧路径
        valid_paths = []
        for frame_path in request.frame_paths:
            if os.path.exists(frame_path):
                valid_paths.append(frame_path)
            else:
                logger.warning(f"帧文件不存在: {frame_path}")
        
        if not valid_paths:
            raise HTTPException(status_code=400, detail="没有有效的图像文件")
        
        # 创建批量任务
        task_data = {
            "task_id": task_id,
            "type": "batch_image_analysis",
            "status": "pending",
            "progress": 0.0,
            "frame_paths": valid_paths,
            "total_frames": len(valid_paths),
            "completed_frames": 0,
            "results": [],
            "analysis_options": request.analysis_options or {}
        }
        
        queue_service.create_task(task_data)
        logger.info(f"批量图像分析任务已创建: {task_id}, 共 {len(valid_paths)} 帧")
        
        # 启动后台处理
        background_tasks.add_task(_process_batch_analysis, task_id)
        
        return BatchAnalysisResponse(
            task_id=task_id,
            total_frames=len(valid_paths),
            status="pending",
            message=f"批量图像分析任务已启动，共 {len(valid_paths)} 帧"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量分析请求处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量分析请求处理失败: {str(e)}")

@router.delete("/{task_id}")
async def cancel_analysis_task(task_id: str):
    """
    取消图像分析任务
    """
    try:
        task = queue_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 更新任务状态
        queue_service.update_task_status(task_id, "cancelled", 0.0, "任务已取消")
        
        # 清理临时文件
        if "file_path" in task:
            try:
                os.unlink(task["file_path"])
                logger.info(f"已清理临时文件: {task['file_path']}")
            except Exception as e:
                logger.warning(f"清理临时文件失败: {str(e)}")
        
        return {"message": "任务已取消"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")

# 后台处理函数
async def _process_image_analysis(task_id: str):
    """处理单张图像分析任务"""
    try:
        # 获取任务信息
        task = queue_service.get_task(task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return
        
        # 更新状态为处理中
        queue_service.update_task_status(task_id, "in_progress", 10.0, "开始图像分析")
        
        # 执行图像分析
        image_path = task["file_path"]
        analysis_options = task.get("analysis_options", {})
        
        logger.info(f"开始分析图像: {image_path}")
        result = await default_service.analyze_image(image_path, analysis_options)
        
        # 转换结果为字典
        result_dict = result.to_dict()
        
        # 更新任务结果
        task["result"] = result_dict
        task["status"] = "completed"
        task["progress"] = 100.0
        queue_service.update_task(task_id, task)
        
        logger.info(f"图像分析完成: {task_id}")
        
        # 清理临时文件
        try:
            os.unlink(image_path)
            logger.info(f"已清理临时文件: {image_path}")
        except Exception as e:
            logger.warning(f"清理临时文件失败: {str(e)}")
        
    except Exception as e:
        logger.error(f"图像分析处理失败 {task_id}: {str(e)}")
        queue_service.update_task_status(task_id, "failed", 0.0, "", str(e))

async def _process_batch_analysis(task_id: str):
    """处理批量图像分析任务"""
    try:
        # 获取任务信息
        task = queue_service.get_task(task_id)
        if not task:
            logger.error(f"批量任务不存在: {task_id}")
            return
        
        # 更新状态为处理中
        queue_service.update_task_status(task_id, "in_progress", 5.0, "开始批量图像分析")
        
        frame_paths = task["frame_paths"]
        analysis_options = task.get("analysis_options", {})
        total_frames = len(frame_paths)
        results = []
        
        logger.info(f"开始批量分析 {total_frames} 帧图像")
        
        for i, frame_path in enumerate(frame_paths):
            try:
                # 检查任务是否被取消
                current_task = queue_service.get_task(task_id)
                if current_task and current_task.get("status") == "cancelled":
                    logger.info(f"批量任务已被取消: {task_id}")
                    return
                
                # 分析当前帧
                result = await default_service.analyze_image(frame_path, analysis_options)
                results.append(result.to_dict())
                
                # 更新进度
                progress = 5.0 + (i + 1) / total_frames * 90.0
                task["completed_frames"] = i + 1
                task["results"] = results
                task["progress"] = progress
                queue_service.update_task(task_id, task)
                
                logger.info(f"已完成第 {i+1}/{total_frames} 帧分析")
                
            except Exception as e:
                logger.error(f"分析帧失败 {frame_path}: {str(e)}")
                # 添加错误结果
                error_result = {
                    "frame_path": frame_path,
                    "error": str(e),
                    "frame_timestamp": 0.0,
                    "processing_time": 0.0
                }
                results.append(error_result)
        
        # 完成任务
        task["status"] = "completed"
        task["progress"] = 100.0
        task["results"] = results
        queue_service.update_task(task_id, task)
        
        logger.info(f"批量图像分析完成: {task_id}, 成功分析 {len(results)} 帧")
        
    except Exception as e:
        logger.error(f"批量图像分析处理失败 {task_id}: {str(e)}")
        queue_service.update_task_status(task_id, "failed", 0.0, "", str(e)) 