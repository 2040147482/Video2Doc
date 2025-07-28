"""
语音识别服务模块
提供各种语音识别服务
"""

from .base import BaseSpeechRecognition, SpeechRecognitionResult
from .whisper_service import whisper_service

# 默认使用Whisper服务
default_service = whisper_service

__all__ = ["BaseSpeechRecognition", "SpeechRecognitionResult", "whisper_service", "default_service"]
