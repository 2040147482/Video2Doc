"""
图像识别服务包
"""

from .base import (
    BaseImageRecognition,
    ImageAnalysisResult,
    OCRResult,
    SceneAnalysisResult,
    ObjectDetectionResult
)

from .mock_service import MockImageRecognition

# 创建默认服务实例
default_service = MockImageRecognition()

__all__ = [
    "BaseImageRecognition",
    "ImageAnalysisResult", 
    "OCRResult",
    "SceneAnalysisResult",
    "ObjectDetectionResult",
    "MockImageRecognition",
    "default_service"
] 