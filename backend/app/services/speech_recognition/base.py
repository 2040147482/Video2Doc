"""
语音识别基础模块
定义语音识别服务的基础接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

class SpeechRecognitionResult:
    """语音识别结果类"""
    
    def __init__(
        self,
        text: str,
        segments: List[Dict[str, Any]] = None,
        language: str = None,
        duration: float = 0.0
    ):
        """
        初始化语音识别结果
        
        Args:
            text: 完整转录文本
            segments: 文本片段列表，每个片段包含开始时间、结束时间和文本
            language: 检测到的语言
            duration: 音频时长（秒）
        """
        self.text = text
        self.segments = segments or []
        self.language = language
        self.duration = duration
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            结果字典
        """
        return {
            "text": self.text,
            "segments": self.segments,
            "language": self.language,
            "duration": self.duration
        }
    
    def get_text_with_timestamps(self) -> str:
        """
        获取带时间戳的文本
        
        Returns:
            带时间戳的文本
        """
        if not self.segments:
            return self.text
        
        result = []
        for segment in self.segments:
            start = self._format_timestamp(segment.get("start", 0))
            end = self._format_timestamp(segment.get("end", 0))
            text = segment.get("text", "")
            result.append(f"[{start} --> {end}] {text}")
        
        return "\n".join(result)
    
    def _format_timestamp(self, seconds: float) -> str:
        """
        格式化时间戳
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化的时间字符串 (HH:MM:SS.mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

class BaseSpeechRecognition(ABC):
    """语音识别基础类"""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
