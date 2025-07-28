"""
语音识别服务包
"""

from .base import BaseSpeechRecognition, SpeechRecognitionResult

# 导入Whisper服务
from .whisper_service import whisper_service

# 设置默认服务
default_service = whisper_service

__all__ = ["BaseSpeechRecognition", "SpeechRecognitionResult", "whisper_service", "default_service"]
