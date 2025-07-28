"""
OpenAI Whisper语音识别服务
使用OpenAI Whisper API进行语音识别
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from .base import BaseSpeechRecognition, SpeechRecognitionResult

# 配置日志
logger = logging.getLogger(__name__)

class WhisperService(BaseSpeechRecognition):
    """基于OpenAI Whisper的语音识别服务"""
    
    def __init__(self):
        """初始化Whisper服务"""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.model_name = "whisper-1"  # OpenAI API模型名称
        self.local_model_name = "base"  # 本地模型名称
        self.local_model = None
        self.use_mock = False  # 是否使用模拟模式
        
        if not self.api_key:
            print("未设置OpenAI API密钥，将使用本地Whisper模型")
            try:
                import whisper
                self.local_model = whisper.load_model(self.local_model_name)
                logger.info(f"已加载本地Whisper模型: {self.local_model_name}")
            except Exception as e:
                logger.warning(f"无法加载本地Whisper模型: {str(e)}")
                logger.warning("将使用模拟模式进行语音识别")
                self.use_mock = True
    
    async def transcribe(
        self, 
        audio_path: str, 
        language: Optional[str] = None,
        **options
    ) -> SpeechRecognitionResult:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码
            **options: 其他选项
            
        Returns:
            SpeechRecognitionResult: 转录结果
        """
        if self.use_mock:
            return self._get_mock_result(audio_path, language)
            
        try:
            if self.api_key:
                return await self._transcribe_with_api(audio_path, language, **options)
            else:
                return await self._transcribe_with_local(audio_path, language, **options)
        except Exception as e:
            logger.error(f"转录失败: {str(e)}")
            return SpeechRecognitionResult(
                text="转录失败",
                language=language or "unknown",
                duration=0.0,
                segments=[]
            )
    
    async def detect_language(self, audio_path: str) -> str:
        """
        检测音频语言
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            str: 检测到的语言代码
        """
        if self.use_mock:
            return "zh-CN" if "zh" in os.environ.get("LANG", "") else "en"
            
        try:
            if self.api_key:
                # 使用API检测语言
                import openai
                openai.api_key = self.api_key
                
                with open(audio_path, "rb") as audio_file:
                    response = await openai.Audio.atranscribe(
                        model=self.model_name,
                        file=audio_file,
                        response_format="verbose_json"
                    )
                
                return response.get("language", "en")
            else:
                # 使用本地模型检测语言
                if not self.local_model:
                    return "en"  # 默认英语
                
                result = self.local_model.transcribe(audio_path, task="translate")
                return result.get("language", "en")
        except Exception as e:
            logger.error(f"语言检测失败: {str(e)}")
            return "en"  # 默认英语
    
    async def transcribe_with_timestamps(
        self, 
        audio_path: str, 
        language: Optional[str] = None,
        **options
    ) -> SpeechRecognitionResult:
        """
        转录音频文件并包含时间戳
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码
            **options: 其他选项
            
        Returns:
            SpeechRecognitionResult: 转录结果
        """
        if self.use_mock:
            return self._get_mock_result_with_timestamps(audio_path, language)
            
        try:
            if self.api_key:
                return await self._transcribe_with_api(
                    audio_path, 
                    language, 
                    response_format="verbose_json",
                    **options
                )
            else:
                return await self._transcribe_with_local(
                    audio_path, 
                    language, 
                    with_timestamps=True,
                    **options
                )
        except Exception as e:
            logger.error(f"带时间戳转录失败: {str(e)}")
            return SpeechRecognitionResult(
                text="转录失败",
                language=language or "unknown",
                duration=0.0,
                segments=[]
            )
    
    async def _transcribe_with_api(
        self, 
        audio_path: str, 
        language: Optional[str] = None,
        **options
    ) -> SpeechRecognitionResult:
        """使用OpenAI API转录"""
        import openai
        openai.api_key = self.api_key
        
        with open(audio_path, "rb") as audio_file:
            response_format = options.get("response_format", "text")
            model = options.get("model", self.model_name)
            
            response_kwargs = {
                "model": model,
                "file": audio_file,
                "response_format": response_format
            }
            
            if language:
                response_kwargs["language"] = language
            
            if "prompt" in options and options["prompt"]:
                response_kwargs["prompt"] = options["prompt"]
            
            if "temperature" in options:
                response_kwargs["temperature"] = float(options["temperature"])
            
            response = await openai.Audio.atranscribe(**response_kwargs)
            
            if response_format == "verbose_json":
                # 处理包含时间戳的JSON响应
                segments = []
                for segment in response.get("segments", []):
                    segments.append({
                        "start": segment.get("start", 0),
                        "end": segment.get("end", 0),
                        "text": segment.get("text", "")
                    })
                
                return SpeechRecognitionResult(
                    text=response.get("text", ""),
                    language=response.get("language", language or "unknown"),
                    duration=response.get("duration", 0.0),
                    segments=segments
                )
            else:
                # 处理纯文本响应
                return SpeechRecognitionResult(
                    text=response,
                    language=language or "unknown",
                    duration=0.0,
                    segments=[]
                )
    
    async def _transcribe_with_local(
        self, 
        audio_path: str, 
        language: Optional[str] = None,
        with_timestamps: bool = False,
        **options
    ) -> SpeechRecognitionResult:
        """使用本地Whisper模型转录"""
        if not self.local_model:
            raise ValueError("未加载本地Whisper模型")
        
        # 使用线程池运行CPU密集型任务
        loop = asyncio.get_event_loop()
        
        # 转录选项
        transcribe_options = {}
        if language:
            transcribe_options["language"] = language
        
        if "prompt" in options and options["prompt"]:
            transcribe_options["initial_prompt"] = options["prompt"]
        
        if "temperature" in options:
            transcribe_options["temperature"] = float(options["temperature"])
        
        # 使用run_in_executor在线程池中运行CPU密集型任务
        result = await loop.run_in_executor(
            None,
            lambda: self.local_model.transcribe(audio_path, **transcribe_options)
        )
        
        # 处理结果
        text = result.get("text", "")
        detected_language = result.get("language", language or "unknown")
        
        if with_timestamps:
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": segment.get("text", "")
                })
            
            return SpeechRecognitionResult(
                text=text,
                language=detected_language,
                duration=result.get("duration", 0.0),
                segments=segments
            )
        else:
            return SpeechRecognitionResult(
                text=text,
                language=detected_language,
                duration=result.get("duration", 0.0),
                segments=[]
            )
    
    def _get_mock_result(self, audio_path: str, language: Optional[str] = None) -> SpeechRecognitionResult:
        """获取模拟转录结果"""
        logger.info(f"使用模拟模式转录: {audio_path}")
        
        # 根据文件名生成一些模拟文本
        filename = Path(audio_path).name
        mock_text = f"这是一段模拟转录文本，基于文件 {filename}。这是语音识别的模拟结果，因为无法加载真实的语音识别模型。"
        
        detected_language = language or "zh-CN" if "zh" in os.environ.get("LANG", "") else "en"
        
        return SpeechRecognitionResult(
            text=mock_text,
            language=detected_language,
            duration=30.0,
            segments=[]
        )
    
    def _get_mock_result_with_timestamps(self, audio_path: str, language: Optional[str] = None) -> SpeechRecognitionResult:
        """获取带时间戳的模拟转录结果"""
        logger.info(f"使用模拟模式转录(带时间戳): {audio_path}")
        
        # 根据文件名生成一些模拟文本
        filename = Path(audio_path).name
        mock_text = f"这是一段模拟转录文本，基于文件 {filename}。这是语音识别的模拟结果，因为无法加载真实的语音识别模型。"
        
        detected_language = language or "zh-CN" if "zh" in os.environ.get("LANG", "") else "en"
        
        # 创建模拟片段
        segments = [
            {"start": 0.0, "end": 5.0, "text": "这是一段模拟转录文本，"},
            {"start": 5.0, "end": 10.0, "text": f"基于文件 {filename}。"},
            {"start": 10.0, "end": 15.0, "text": "这是语音识别的模拟结果，"},
            {"start": 15.0, "end": 20.0, "text": "因为无法加载真实的语音识别模型。"}
        ]
        
        return SpeechRecognitionResult(
            text=mock_text,
            language=detected_language,
            duration=20.0,
            segments=segments
        )


# 全局Whisper服务实例
whisper_service = WhisperService()
