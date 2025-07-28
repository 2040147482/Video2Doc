"""
图像识别服务基础模块
定义抽象基类和数据结构
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)

@dataclass
class OCRResult:
    """OCR识别结果"""
    text: str
    confidence: float
    bounding_box: Optional[Dict[str, int]] = None  # {"x": int, "y": int, "width": int, "height": int}
    language: Optional[str] = None

@dataclass
class ObjectDetectionResult:
    """目标检测结果"""
    label: str
    confidence: float
    bounding_box: Dict[str, int]  # {"x": int, "y": int, "width": int, "height": int}
    
@dataclass
class SceneAnalysisResult:
    """场景分析结果"""
    description: str
    confidence: float
    tags: List[str]
    colors: Optional[List[str]] = None
    composition: Optional[str] = None

@dataclass
class ImageAnalysisResult:
    """图像分析综合结果"""
    frame_timestamp: float  # 视频中的时间戳（秒）
    frame_path: str  # 帧图像文件路径
    
    # OCR结果
    ocr_results: List[OCRResult]
    extracted_text: str  # 合并的OCR文本
    
    # 场景分析
    scene_analysis: SceneAnalysisResult
    
    # 目标检测
    objects: List[ObjectDetectionResult]
    
    # 元数据
    processing_time: float
    model_used: str
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "frame_timestamp": self.frame_timestamp,
            "frame_path": self.frame_path,
            "ocr_results": [
                {
                    "text": ocr.text,
                    "confidence": ocr.confidence,
                    "bounding_box": ocr.bounding_box,
                    "language": ocr.language
                } for ocr in self.ocr_results
            ],
            "extracted_text": self.extracted_text,
            "scene_analysis": {
                "description": self.scene_analysis.description,
                "confidence": self.scene_analysis.confidence,
                "tags": self.scene_analysis.tags,
                "colors": self.scene_analysis.colors,
                "composition": self.scene_analysis.composition
            },
            "objects": [
                {
                    "label": obj.label,
                    "confidence": obj.confidence,
                    "bounding_box": obj.bounding_box
                } for obj in self.objects
            ],
            "processing_time": self.processing_time,
            "model_used": self.model_used,
            "error": self.error
        }

class BaseImageRecognition(ABC):
    """图像识别服务抽象基类"""
    
    def __init__(self):
        """初始化基础配置"""
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        self.max_image_size = 10 * 1024 * 1024  # 10MB
        
    @abstractmethod
    async def analyze_image(self, image_path: str, analysis_options: Optional[Dict[str, Any]] = None) -> ImageAnalysisResult:
        """
        分析单张图像
        
        Args:
            image_path: 图像文件路径
            analysis_options: 分析选项，如：
                {
                    "enable_ocr": True,
                    "enable_scene_analysis": True,
                    "enable_object_detection": True,
                    "language": "auto",
                    "detail_level": "medium"
                }
        
        Returns:
            ImageAnalysisResult: 分析结果
        """
        pass
    
    @abstractmethod
    async def extract_text(self, image_path: str, language: str = "auto") -> List[OCRResult]:
        """
        从图像中提取文字（OCR）
        
        Args:
            image_path: 图像文件路径
            language: 语言代码，如 "zh-cn", "en", "auto"
        
        Returns:
            List[OCRResult]: OCR结果列表
        """
        pass
    
    @abstractmethod
    async def describe_scene(self, image_path: str, detail_level: str = "medium") -> SceneAnalysisResult:
        """
        描述图像场景
        
        Args:
            image_path: 图像文件路径
            detail_level: 详细程度 ("low", "medium", "high")
        
        Returns:
            SceneAnalysisResult: 场景分析结果
        """
        pass
    
    @abstractmethod
    async def detect_objects(self, image_path: str) -> List[ObjectDetectionResult]:
        """
        检测图像中的对象
        
        Args:
            image_path: 图像文件路径
        
        Returns:
            List[ObjectDetectionResult]: 检测到的对象列表
        """
        pass
    
    def validate_image(self, image_path: str) -> bool:
        """
        验证图像文件
        
        Args:
            image_path: 图像文件路径
        
        Returns:
            bool: 是否为有效图像
        """
        try:
            image_path = Path(image_path)
            
            # 检查文件是否存在
            if not image_path.exists():
                logger.warning(f"图像文件不存在: {image_path}")
                return False
            
            # 检查文件格式
            if image_path.suffix.lower() not in self.supported_formats:
                logger.warning(f"不支持的图像格式: {image_path.suffix}")
                return False
            
            # 检查文件大小
            if image_path.stat().st_size > self.max_image_size:
                logger.warning(f"图像文件过大: {image_path.stat().st_size} bytes")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"图像验证失败: {str(e)}")
            return False
    
    async def batch_analyze(self, image_paths: List[str], analysis_options: Optional[Dict[str, Any]] = None) -> List[ImageAnalysisResult]:
        """
        批量分析图像
        
        Args:
            image_paths: 图像文件路径列表
            analysis_options: 分析选项
        
        Returns:
            List[ImageAnalysisResult]: 分析结果列表
        """
        results = []
        
        for image_path in image_paths:
            try:
                result = await self.analyze_image(image_path, analysis_options)
                results.append(result)
            except Exception as e:
                logger.error(f"分析图像失败 {image_path}: {str(e)}")
                # 创建错误结果
                error_result = ImageAnalysisResult(
                    frame_timestamp=0.0,
                    frame_path=image_path,
                    ocr_results=[],
                    extracted_text="",
                    scene_analysis=SceneAnalysisResult(
                        description="分析失败",
                        confidence=0.0,
                        tags=[]
                    ),
                    objects=[],
                    processing_time=0.0,
                    model_used=self.__class__.__name__,
                    error=str(e)
                )
                results.append(error_result)
        
        return results 