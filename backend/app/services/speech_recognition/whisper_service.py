"""
OpenAI Whisper语音识别服务
使用OpenAI Whisper API进行语音识别
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# 导入基础类
from .base import BaseSpeechRecognition, SpeechRecognitionResult

# 配置日志
logger = logging.getLogger(__name__)

class WhisperService(BaseSpeechRecognition):
    """OpenAI Whisper语音识别服务"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-1"):
        """
        初始化Whisper服务
        
        Args:
            api_key: OpenAI API密钥，如果为None则从环境变量获取
            model: Whisper模型名称
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("未设置OpenAI API密钥，将使用本地Whisper模型")
            self.use_api = False
        else:
            self.use_api = True
        
        self.model = model
        
        # 如果使用API，导入OpenAI客户端
        if self.use_api:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("OpenAI客户端初始化成功")
            except ImportError:
                logger.error("未安装OpenAI包，请使用pip install openai安装")
                self.use_api = False
            except Exception as e:
                logger.error(f"OpenAI客户端初始化失败: {str(e)}")
                self.use_api = False
        
        # 如果不使用API，尝试导入本地Whisper
        if not self.use_api:
            try:
                import whisper
                self.whisper = whisper
                self.whisper_model = None  # 延迟加载模型
                logger.info("本地Whisper初始化成功")
            except ImportError:
                logger.error("未安装Whisper包，请使用pip install openai-whisper安装")
                raise ImportError("未安装Whisper包，请使用pip install openai-whisper安装")
    
    async def _load_local_model(self, model_name: str = "base"):
        """
        加载本地Whisper模型
        
        Args:
            model_name: 模型名称，可选值：tiny, base, small, medium, large
            
        Returns:
            加载的模型
        """
        if self.whisper_model is None:
            logger.info(f"加载本地Whisper模型: {model_name}")
            # 在线程池中加载模型，避免阻塞事件循环
            loop = asyncio.get_event_loop()
            self.whisper_model = await loop.run_in_executor(
                None, 
                lambda: self.whisper.load_model(model_name)
            )
            logger.info(f"本地Whisper模型加载成功: {model_name}")
        
        return self.whisper_model
    
    async def transcribe(
        self, 
        audio_path: Union[str, Path],
        language: Optional[str] = None,
        **kwargs
    ) -> SpeechRecognitionResult:
        """
        转录音频
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码（如果已知）
            **kwargs: 其他参数
            
        Returns:
            转录结果
            
        Raises:
            Exception: 如果转录失败
        """
        audio_path = str(audio_path)
        logger.info(f"转录音频: {audio_path}")
        
        try:
            if self.use_api:
                return await self._transcribe_with_api(audio_path, language, **kwargs)
            else:
                return await self._transcribe_with_local(audio_path, language, **kwargs)
        except Exception as e:
            logger.error(f"音频转录失败: {str(e)}")
            raise Exception(f"音频转录失败: {str(e)}")
    
    async def _transcribe_with_api(
        self, 
        audio_path: str,
        language: Optional[str] = None,
        **kwargs
    ) -> SpeechRecognitionResult:
        """
        使用OpenAI API转录音频
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码（如果已知）
            **kwargs: 其他参数
            
        Returns:
            转录结果
        """
        logger.info(f"使用OpenAI API转录音频: {audio_path}")
        
        # 构建请求参数
        request_params = {
            "model": self.model,
            "response_format": "verbose_json",
        }
        
        if language:
            request_params["language"] = language
        
        # 添加其他参数
        for key, value in kwargs.items():
            if key in ["prompt", "temperature"]:
                request_params[key] = value
        
        # 在线程池中执行API调用，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        
        with open(audio_path, "rb") as audio_file:
            response = await loop.run_in_executor(
                None,
                lambda: self.client.audio.transcriptions.create(
                    file=audio_file,
                    **request_params
                )
            )
        
        # 解析响应
        result_dict = response.model_dump()
        
        # 创建结果对象
        return SpeechRecognitionResult(
            text=result_dict.get("text", ""),
            segments=result_dict.get("segments", []),
            language=result_dict.get("language"),
            duration=result_dict.get("duration", 0.0)
        )
    
    async def _transcribe_with_local(
        self, 
        audio_path: str,
        language: Optional[str] = None,
        **kwargs
    ) -> SpeechRecognitionResult:
        """
        使用本地Whisper模型转录音频
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码（如果已知）
            **kwargs: 其他参数
            
        Returns:
            转录结果
        """
        logger.info(f"使用本地Whisper模型转录音频: {audio_path}")
        
        # 获取模型名称
        model_name = kwargs.get("model_name", "base")
        
        # 加载模型
        model = await self._load_local_model(model_name)
        
        # 构建转录选项
        transcribe_options = {}
        
        if language:
            transcribe_options["language"] = language
        
        # 添加其他参数
        for key, value in kwargs.items():
            if key in ["initial_prompt", "temperature", "beam_size"]:
                transcribe_options[key] = value
        
        # 在线程池中执行转录，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: model.transcribe(audio_path, **transcribe_options)
        )
        
        # 创建结果对象
        return SpeechRecognitionResult(
            text=result.get("text", ""),
            segments=result.get("segments", []),
            language=result.get("language"),
            duration=result.get("duration", 0.0)
        )
    
    async def detect_language(self, audio_path: Union[str, Path]) -> str:
        """
        检测音频语言
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            语言代码
            
        Raises:
            Exception: 如果语言检测失败
        """
        audio_path = str(audio_path)
        logger.info(f"检测音频语言: {audio_path}")
        
        try:
            if self.use_api:
                # 使用API进行语言检测
                # 注意：OpenAI API目前没有专门的语言检测端点，我们使用转录API并获取返回的语言
                result = await self._transcribe_with_api(audio_path)
                return result.language or "en"
            else:
                # 使用本地模型进行语言检测
                model = await self._load_local_model("base")
                
                # 在线程池中执行语言检测，避免阻塞事件循环
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: model.detect_language(audio_path)
                )
                
                return result[0] or "en"
        except Exception as e:
            logger.error(f"音频语言检测失败: {str(e)}")
            raise Exception(f"音频语言检测失败: {str(e)}")
    
    async def transcribe_with_timestamps(
        self, 
        audio_path: Union[str, Path],
        language: Optional[str] = None,
        **kwargs
    ) -> SpeechRecognitionResult:
        """
        转录音频并带有时间戳
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码（如果已知）
            **kwargs: 其他参数
            
        Returns:
            带时间戳的转录结果
            
        Raises:
            Exception: 如果转录失败
        """
        # 对于Whisper，普通转录已经包含时间戳信息
        return await self.transcribe(audio_path, language, **kwargs)

# 创建全局实例
whisper_service = WhisperService()
