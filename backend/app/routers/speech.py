"""
语音识别路由模块
提供语音识别相关API端点
"""

import os
import logging
import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.speech_recognition import default_service, SpeechRecognitionResult
from app.services.file_service import file_service
from app.services.queue_service import queue_service
from app.config import Settings, get_settings

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(prefix="/api/speech", tags=["speech"])

# 模型定义
class TranscriptionRequest(BaseModel):
    """转录请求模型"""
    language: Optional[str] = Field(None, description="语言代码，例如：zh, en, ja等")
    model: Optional[str] = Field("whisper-1", description="模型名称")
    prompt: Optional[str] = Field(None, description="提示词，用于引导转录")
    temperature: Optional[float] = Field(0.0, description="采样温度，控制随机性")
    with_timestamps: bool = Field(False, description="是否包含时间戳")

class TranscriptionResponse(BaseModel):
    """转录响应模型"""
    task_id: str = Field(..., description="任务ID")
    text: str = Field(..., description="转录文本")
    language: Optional[str] = Field(None, description="检测到的语言")
    duration: float = Field(0.0, description="音频时长（秒）")
    segments: Optional[List[Dict[str, Any]]] = Field(None, description="文本片段")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_123456789",
                "text": "这是转录的文本内容。",
                "language": "zh",
                "duration": 120.5,
                "segments": [
                    {
                        "start": 0.0,
                        "end": 5.2,
                        "text": "这是第一个片段。"
                    },
                    {
                        "start": 5.2,
                        "end": 10.5,
                        "text": "这是第二个片段。"
                    }
                ]
            }
        }

class LanguageDetectionResponse(BaseModel):
    """语言检测响应模型"""
    language: str = Field(..., description="检测到的语言代码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "zh"
            }
        }

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    model: str = Form("whisper-1"),
    prompt: Optional[str] = Form(None),
    temperature: float = Form(0.0),
    with_timestamps: bool = Form(False),
    settings: Settings = Depends(get_settings)
):
    """
    转录音频文件
    
    Args:
        background_tasks: 后台任务
        file: 音频文件
        language: 语言代码
        model: 模型名称
        prompt: 提示词
        temperature: 采样温度
        with_timestamps: 是否包含时间戳
        settings: 应用设置
        
    Returns:
        转录结果
    """
    # 生成任务ID
    task_id = f"transcribe_{uuid.uuid4().hex}"
    
    try:
        # 保存音频文件
        audio_path = await file_service.save_upload_file(
            file, 
            allowed_types=["audio/mpeg", "audio/wav", "audio/ogg", "audio/x-m4a", "audio/webm"],
            max_size_mb=settings.max_audio_size_mb
        )
        
        logger.info(f"音频文件已保存: {audio_path}")
        
        # 创建转录选项
        transcribe_options = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature
        }
        
        # 在后台执行转录
        background_tasks.add_task(
            _process_transcription,
            task_id,
            audio_path,
            language,
            with_timestamps,
            transcribe_options
        )
        
        # 返回初始响应
        return TranscriptionResponse(
            task_id=task_id,
            text="转录中...",
            language=language,
            duration=0.0
        )
    except Exception as e:
        logger.error(f"转录请求处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"转录请求处理失败: {str(e)}")

@router.post("/transcribe/url", response_model=TranscriptionResponse)
async def transcribe_audio_url(
    url: str = Form(...),
    request: TranscriptionRequest = None,
    background_tasks: BackgroundTasks = None,
    settings: Settings = Depends(get_settings)
):
    """
    转录音频URL
    
    Args:
        url: 音频URL
        request: 转录请求
        background_tasks: 后台任务
        settings: 应用设置
        
    Returns:
        转录结果
    """
    # 使用默认值处理可能为None的参数
    if request is None:
        request = TranscriptionRequest()
    
    if background_tasks is None:
        raise HTTPException(status_code=500, detail="内部服务器错误：无法访问后台任务")
    
    # 生成任务ID
    task_id = f"transcribe_{uuid.uuid4().hex}"
    
    try:
        # 下载音频文件
        from app.services.video_service import video_service
        
        # 验证URL
        if not await video_service.is_valid_url(url):
            raise HTTPException(status_code=400, detail="无效的URL")
        
        # 获取音频文件
        audio_path = await video_service.download_audio(url, settings.temp_dir)
        
        logger.info(f"音频文件已下载: {audio_path}")
        
        # 创建转录选项
        transcribe_options = {
            "model": request.model,
            "prompt": request.prompt,
            "temperature": request.temperature
        }
        
        # 在后台执行转录
        background_tasks.add_task(
            _process_transcription,
            task_id,
            audio_path,
            request.language,
            request.with_timestamps,
            transcribe_options
        )
        
        # 返回初始响应
        return TranscriptionResponse(
            task_id=task_id,
            text="转录中...",
            language=request.language,
            duration=0.0
        )
    except Exception as e:
        logger.error(f"转录URL处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"转录URL处理失败: {str(e)}")

@router.get("/transcribe/{task_id}", response_model=TranscriptionResponse)
async def get_transcription(
    task_id: str,
    settings: Settings = Depends(get_settings)
):
    """
    获取转录结果
    
    Args:
        task_id: 任务ID
        settings: 应用设置
        
    Returns:
        转录结果
    """
    # 获取任务结果
    task_data = queue_service.get_task(task_id)
    
    if not task_data:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    # 检查任务状态
    status = task_data.get("status")
    
    if status == "failed":
        raise HTTPException(status_code=500, detail=task_data.get("error_message", "转录失败"))
    
    if status != "completed":
        # 返回进行中的状态
        return TranscriptionResponse(
            task_id=task_id,
            text="转录中...",
            language=task_data.get("language"),
            duration=task_data.get("duration", 0.0)
        )
    
    # 返回完整结果
    return TranscriptionResponse(
        task_id=task_id,
        text=task_data.get("text", ""),
        language=task_data.get("language"),
        duration=task_data.get("duration", 0.0),
        segments=task_data.get("segments")
    )

@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """
    检测音频语言
    
    Args:
        file: 音频文件
        settings: 应用设置
        
    Returns:
        检测到的语言
    """
    try:
        # 保存音频文件
        audio_path = await file_service.save_upload_file(
            file, 
            allowed_types=["audio/mpeg", "audio/wav", "audio/ogg", "audio/x-m4a", "audio/webm"],
            max_size_mb=settings.max_audio_size_mb
        )
        
        logger.info(f"音频文件已保存: {audio_path}")
        
        # 检测语言
        language = await default_service.detect_language(audio_path)
        
        # 清理临时文件
        try:
            os.unlink(audio_path)
        except Exception as e:
            logger.warning(f"清理临时文件失败: {str(e)}")
        
        return LanguageDetectionResponse(language=language)
    except Exception as e:
        logger.error(f"语言检测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"语言检测失败: {str(e)}")

# 后台处理函数
async def _process_transcription(
    task_id: str,
    audio_path: str,
    language: Optional[str],
    with_timestamps: bool,
    options: Dict[str, Any]
):
    """
    处理转录任务
    
    Args:
        task_id: 任务ID
        audio_path: 音频文件路径
        language: 语言代码
        with_timestamps: 是否包含时间戳
        options: 转录选项
    """
    try:
        # 创建任务
        queue_service.create_task({
            "task_id": task_id,
            "status": "processing",
            "audio_path": audio_path,
            "language": language
        })
        
        # 执行转录
        if with_timestamps:
            result = await default_service.transcribe_with_timestamps(audio_path, language, **options)
        else:
            result = await default_service.transcribe(audio_path, language, **options)
        
        # 更新任务状态
        queue_service.update_task_status(
            task_id=task_id,
            status="completed",
            message="转录完成",
            error=""
        )
        
        # 更新任务结果
        task_data = queue_service.get_task(task_id)
        task_data.update(result.to_dict())
        queue_service._save_task(task_id)
        
        logger.info(f"转录任务完成: {task_id}")
        
        # 清理临时文件
        try:
            os.unlink(audio_path)
        except Exception as e:
            logger.warning(f"清理临时文件失败: {str(e)}")
    except Exception as e:
        logger.error(f"转录任务失败: {str(e)}")
        
        # 更新任务状态
        queue_service.update_task_status(
            task_id=task_id,
            status="failed",
            message="转录失败",
            error=str(e)
        )
