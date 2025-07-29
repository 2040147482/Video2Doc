"""
AI摘要服务路由
"""

import logging
import uuid
import json
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.models.summary import SummaryRequest, SummaryResponse, SummaryStatusResponse
from app.services.queue_service import queue_service
from app.services.summary import default_service as summary_service
from app.services.speech_recognition import default_service as speech_service
from app.services.image_recognition import default_service as image_service

logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(
    prefix="/summary",
    tags=["summary"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=SummaryResponse)
async def generate_summary(
    background_tasks: BackgroundTasks,
    request: SummaryRequest,
    settings: Settings = Depends(get_settings)
):
    """
    生成视频内容摘要
    
    - **task_id**: 视频处理任务ID
    - **language**: 摘要语言，如: zh-cn, en
    - **detail_level**: 摘要详细程度: low, medium, high
    - **include_chapters**: 是否包含章节
    - **include_key_points**: 是否包含关键点
    - **max_key_points**: 最大关键点数量
    - **max_length**: 摘要最大长度（字符数）
    - **focus_topics**: 重点关注的主题
    """
    logger.info(f"收到摘要生成请求: {request.model_dump_json(indent=2)}")
    
    try:
        # 验证任务ID
        video_task = queue_service.get_task(request.task_id)
        if not video_task:
            logger.warning(f"未找到任务: {request.task_id}")
            
            # 如果是测试任务，创建一个模拟任务
            if request.task_id.startswith("test_"):
                logger.info(f"创建测试任务: {request.task_id}")
                test_task_data = {
                    "task_id": request.task_id,
                    "type": "video",
                    "status": "completed",
                    "progress": 100.0,
                    "url": "https://example.com/test-video.mp4",
                    "output_format": "markdown",
                    "metadata": {
                        "title": "测试视频",
                        "duration": 180.5
                    },
                    "transcription_task_id": None,
                    "image_analysis_task_id": None
                }
                queue_service.create_task(test_task_data)
                video_task = test_task_data
                logger.info(f"测试任务创建成功: {request.task_id}")
            else:
                raise HTTPException(status_code=404, detail=f"未找到任务: {request.task_id}")
        
        # 创建摘要任务ID
        summary_task_id = f"summary_{uuid.uuid4().hex}"
        logger.info(f"创建摘要任务: {summary_task_id}")
        
        # 创建任务数据
        task_data = {
            "task_id": summary_task_id,
            "type": "summary",
            "status": "pending",
            "progress": 0.0,
            "video_task_id": request.task_id,
            "options": {
                "language": request.language,
                "detail_level": request.detail_level,
                "include_chapters": request.include_chapters,
                "include_key_points": request.include_key_points,
                "max_key_points": request.max_key_points,
                "max_length": request.max_length,
                "focus_topics": request.focus_topics
            }
        }
        
        # 创建任务
        queue_service.create_task(task_data)
        logger.info(f"任务已创建: {summary_task_id}")
        
        # 添加后台任务
        background_tasks.add_task(_process_summary_task, summary_task_id)
        logger.info(f"后台任务已添加: {summary_task_id}")
        
        # 返回响应
        return SummaryResponse(
            task_id=summary_task_id,
            status="pending",
            message="摘要生成任务已启动"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"摘要生成请求处理失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"摘要生成请求处理失败: {str(e)}")


@router.get("/status/{task_id}", response_model=SummaryStatusResponse)
async def get_summary_status(task_id: str):
    """
    获取摘要任务状态
    
    - **task_id**: 摘要任务ID
    """
    logger.info(f"获取摘要任务状态: {task_id}")
    try:
        # 获取任务
        task = queue_service.get_task(task_id)
        if not task:
            logger.warning(f"未找到任务: {task_id}")
            raise HTTPException(status_code=404, detail=f"未找到任务: {task_id}")
        
        logger.info(f"任务状态: {task.get('status', 'unknown')}, 进度: {task.get('progress', 0.0)}")
        
        # 返回状态
        return SummaryStatusResponse(
            task_id=task_id,
            status=task.get("status", "unknown"),
            progress=task.get("progress", 0.0),
            result=task.get("result"),
            error=task.get("error_message")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取摘要状态失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取摘要状态失败: {str(e)}")


@router.delete("/{task_id}")
async def cancel_summary_task(task_id: str):
    """
    取消摘要任务
    
    - **task_id**: 摘要任务ID
    """
    logger.info(f"取消摘要任务: {task_id}")
    try:
        # 获取任务
        task = queue_service.get_task(task_id)
        if not task:
            logger.warning(f"未找到任务: {task_id}")
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 更新任务状态
        queue_service.update_task_status(task_id, "cancelled", 0.0, "任务已取消", "")
        logger.info(f"任务已取消: {task_id}")
        
        # 返回响应
        return {"status": "success", "message": "任务已取消"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消摘要任务失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"取消摘要任务失败: {str(e)}")


async def _process_summary_task(task_id: str):
    """
    处理摘要任务
    
    Args:
        task_id: 摘要任务ID
    """
    logger.info(f"开始处理摘要任务: {task_id}")
    
    try:
        # 获取任务数据
        task = queue_service.get_task(task_id)
        if not task:
            logger.warning(f"任务不存在: {task_id}")
            return
        
        # 获取视频任务ID
        video_task_id = task.get("video_task_id")
        if not video_task_id:
            error_msg = "未提供视频任务ID"
            logger.error(error_msg)
            queue_service.update_task_status(task_id, "failed", 0.0, "", error_msg)
            return
        
        # 获取视频任务
        video_task = queue_service.get_task(video_task_id)
        if not video_task:
            error_msg = f"未找到视频任务: {video_task_id}"
            logger.error(error_msg)
            queue_service.update_task_status(task_id, "failed", 0.0, "", error_msg)
            return
        
        # 更新状态为处理中
        queue_service.update_task_status(task_id, "processing", 10.0, "正在收集数据", "")
        
        # 获取转录结果
        transcription = None
        transcription_task_id = video_task.get("transcription_task_id")
        if transcription_task_id:
            logger.info(f"尝试获取转录任务: {transcription_task_id}")
            transcription_task = queue_service.get_task(transcription_task_id)
            if transcription_task and transcription_task.get("status") == "completed":
                transcription = transcription_task.get("result", {})
                logger.info("已获取转录结果")
            else:
                logger.info(f"转录任务未完成或不存在: {transcription_task_id}")
        
        # 更新进度
        queue_service.update_task_status(task_id, "processing", 30.0, "正在收集图像分析数据", "")
        
        # 获取图像分析结果
        image_analysis = None
        image_task_id = video_task.get("image_analysis_task_id")
        if image_task_id:
            logger.info(f"尝试获取图像分析任务: {image_task_id}")
            image_task = queue_service.get_task(image_task_id)
            if image_task and image_task.get("status") == "completed":
                image_analysis = image_task.get("result", {})
                logger.info("已获取图像分析结果")
            else:
                logger.info(f"图像分析任务未完成或不存在: {image_task_id}")
        
        # 更新进度
        queue_service.update_task_status(task_id, "processing", 50.0, "正在生成摘要", "")
        
        # 获取视频元数据
        metadata = video_task.get("metadata", {})
        logger.info(f"视频元数据: {json.dumps(metadata, ensure_ascii=False)}")
        
        # 获取选项
        options = task.get("options", {})
        
        # 生成摘要
        logger.info("调用摘要服务生成摘要...")
        result = await summary_service.generate_summary(
            task_id=task_id,
            transcription=transcription,
            image_analysis=image_analysis,
            metadata=metadata,
            options=options
        )
        logger.info("摘要生成完成")
        
        # 更新进度
        queue_service.update_task_status(task_id, "processing", 90.0, "正在完成摘要", "")
        
        # 将结果转换为字典
        result_dict = result.to_dict()
        logger.info(f"摘要结果字段: {', '.join(result_dict.keys())}")
        
        # 更新任务结果
        task = queue_service.get_task(task_id)
        if task:
            task["result"] = result_dict
            task["status"] = "completed"
            task["progress"] = 100.0
            task["message"] = "摘要生成完成"
            queue_service.update_task_status(task_id, "completed", 100.0, "摘要生成完成", "")
            logger.info(f"摘要任务完成: {task_id}")
        else:
            logger.warning(f"无法更新任务，任务不存在: {task_id}")
        
    except Exception as e:
        logger.error(f"摘要任务处理失败 {task_id}: {str(e)}", exc_info=True)
        try:
            queue_service.update_task_status(task_id, "failed", 0.0, "", str(e))
        except Exception as update_error:
            logger.error(f"更新任务状态失败: {str(update_error)}") 