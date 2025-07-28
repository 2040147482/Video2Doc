"""
超级简化的语音识别路由模块
用于逐步诊断问题
"""

import os
import logging
import uuid
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel, Field

# 只导入最基本的依赖
from app.config import Settings, get_settings

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(prefix="/speech-ultra-simple", tags=["speech-ultra-simple"])

class UltraSimpleResponse(BaseModel):
    """超级简化响应模型"""
    status: str = "ok"
    message: str = "测试成功"
    task_id: str = ""

@router.post("/test", response_model=UltraSimpleResponse)
async def ultra_simple_test():
    """超级简化的测试端点"""
    task_id = f"test_{uuid.uuid4().hex}"
    logger.info(f"超级简化测试调用: {task_id}")
    
    return UltraSimpleResponse(
        status="ok",
        message="超级简化测试成功",
        task_id=task_id
    )

@router.post("/file-upload-test", response_model=UltraSimpleResponse)
async def file_upload_test(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """文件上传测试端点"""
    task_id = f"upload_test_{uuid.uuid4().hex}"
    logger.info(f"文件上传测试: {task_id}, 文件名: {file.filename}")
    
    # 只读取文件大小，不保存
    content = await file.read()
    file_size = len(content)
    
    return UltraSimpleResponse(
        status="ok",
        message=f"文件上传测试成功，大小: {file_size} 字节",
        task_id=task_id
    )

@router.post("/file-service-test", response_model=UltraSimpleResponse)
async def file_service_test(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """文件服务测试端点"""
    task_id = f"file_service_test_{uuid.uuid4().hex}"
    logger.info(f"文件服务测试: {task_id}")
    
    try:
        # 导入文件服务
        from app.services.file_service import file_service
        logger.info("文件服务导入成功")
        
        # 保存文件
        audio_path, file_info = await file_service.save_upload_file(file, task_id)
        logger.info(f"文件保存成功: {audio_path}")
        
        # 清理文件
        try:
            os.unlink(audio_path)
            logger.info("文件清理成功")
        except Exception as e:
            logger.warning(f"文件清理失败: {e}")
        
        return UltraSimpleResponse(
            status="ok",
            message=f"文件服务测试成功，保存路径: {audio_path}",
            task_id=task_id
        )
        
    except Exception as e:
        logger.error(f"文件服务测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件服务测试失败: {str(e)}")

@router.post("/speech-service-test", response_model=UltraSimpleResponse)
async def speech_service_test(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """语音服务测试端点"""
    task_id = f"speech_test_{uuid.uuid4().hex}"
    logger.info(f"语音服务测试: {task_id}")
    
    try:
        # 导入服务
        from app.services.file_service import file_service
        from app.services.speech_recognition import default_service
        logger.info("服务导入成功")
        
        # 保存文件
        audio_path, file_info = await file_service.save_upload_file(file, task_id)
        logger.info(f"文件保存成功: {audio_path}")
        
        # 测试语音识别
        result = await default_service.transcribe(str(audio_path))
        logger.info(f"语音识别成功: {result.text}")
        
        # 清理文件
        try:
            os.unlink(audio_path)
            logger.info("文件清理成功")
        except Exception as e:
            logger.warning(f"文件清理失败: {e}")
        
        return UltraSimpleResponse(
            status="ok",
            message=f"语音服务测试成功，转录结果: {result.text}",
            task_id=task_id
        )
        
    except Exception as e:
        logger.error(f"语音服务测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"语音服务测试失败: {str(e)}") 