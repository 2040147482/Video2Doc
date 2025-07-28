"""
简化的语音识别路由模块
用于调试和测试
"""

import os
import logging
import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel, Field

from app.services.speech_recognition import default_service, SpeechRecognitionResult
from app.services.file_service import file_service
from app.config import Settings, get_settings

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(prefix="/speech-simple", tags=["speech-simple"])

# 模型定义
class SimpleTranscriptionResponse(BaseModel):
    """简化转录响应模型"""
    task_id: str = Field(..., description="任务ID")
    text: str = Field(..., description="转录文本")
    language: Optional[str] = Field(None, description="检测到的语言")
    duration: float = Field(0.0, description="音频时长（秒）")
    status: str = Field("completed", description="状态")

class LanguageDetectionResponse(BaseModel):
    """语言检测响应模型"""
    language: str = Field(..., description="检测到的语言")
    confidence: float = Field(1.0, description="置信度")

@router.post("/transcribe", response_model=SimpleTranscriptionResponse)
async def transcribe_audio_file_simple(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    settings: Settings = Depends(get_settings)
):
    """
    简化的转录音频文件接口
    
    Args:
        file: 音频文件
        language: 语言代码
        settings: 应用设置
        
    Returns:
        转录结果
    """
    # 生成任务ID
    task_id = f"transcribe_{uuid.uuid4().hex}"
    
    try:
        # 保存音频文件
        audio_path, file_info = await file_service.save_upload_file(file, task_id)
        
        logger.info(f"音频文件已保存: {audio_path}")
        
        # 执行转录
        result = await default_service.transcribe(str(audio_path), language)
        
        # 清理临时文件
        try:
            os.unlink(audio_path)
        except Exception as e:
            logger.warning(f"清理临时文件失败: {str(e)}")
        
        # 返回结果
        return SimpleTranscriptionResponse(
            task_id=task_id,
            text=result.text,
            language=result.language,
            duration=result.duration,
            status="completed"
        )
    except Exception as e:
        logger.error(f"转录请求处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"转录请求处理失败: {str(e)}")

@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language_simple(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """
    简化的检测音频语言接口
    
    Args:
        file: 音频文件
        settings: 应用设置
        
    Returns:
        检测到的语言
    """
    try:
        # 保存音频文件
        task_id = f"detect_lang_{uuid.uuid4().hex}"
        audio_path, file_info = await file_service.save_upload_file(file, task_id)
        
        logger.info(f"音频文件已保存: {audio_path}")
        
        # 检测语言
        language = await default_service.detect_language(str(audio_path))
        
        # 清理临时文件
        try:
            os.unlink(audio_path)
        except Exception as e:
            logger.warning(f"清理临时文件失败: {str(e)}")
        
        # 返回结果
        return LanguageDetectionResponse(
            language=language,
            confidence=1.0
        )
    except Exception as e:
        logger.error(f"语言检测请求处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"语言检测请求处理失败: {str(e)}") 