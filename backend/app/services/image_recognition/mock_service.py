"""
模拟图像识别服务
用于测试和开发，不依赖外部API
"""

import time
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .base import (
    BaseImageRecognition, 
    ImageAnalysisResult, 
    OCRResult, 
    SceneAnalysisResult, 
    ObjectDetectionResult
)

# 配置日志
logger = logging.getLogger(__name__)

class MockImageRecognition(BaseImageRecognition):
    """模拟图像识别服务"""
    
    def __init__(self):
        """初始化模拟服务"""
        super().__init__()
        self.model_name = "MockImageRecognition"
        
        # 模拟数据
        self.mock_texts = [
            "这是一段模拟的OCR文本",
            "Mock OCR Text Example",
            "图像中包含的文字内容",
            "Sample text from image"
        ]
        
        self.mock_scenes = [
            "一个现代化的办公室环境，有电脑和文件",
            "户外自然风景，包含树木和天空",
            "室内会议室，有投影屏幕和桌椅",
            "城市街道场景，有建筑物和车辆"
        ]
        
        self.mock_objects = [
            "person", "computer", "chair", "table", "screen", 
            "book", "phone", "car", "tree", "building"
        ]
        
        self.mock_colors = [
            ["蓝色", "白色", "灰色"],
            ["绿色", "棕色", "蓝色"],
            ["白色", "黑色", "银色"],
            ["红色", "黄色", "绿色"]
        ]
        
    async def analyze_image(self, image_path: str, analysis_options: Optional[Dict[str, Any]] = None) -> ImageAnalysisResult:
        """
        分析单张图像（模拟实现）
        
        Args:
            image_path: 图像文件路径
            analysis_options: 分析选项
        
        Returns:
            ImageAnalysisResult: 分析结果
        """
        start_time = time.time()
        
        # 验证图像
        if not self.validate_image(image_path):
            raise ValueError(f"无效的图像文件: {image_path}")
        
        # 模拟处理延迟
        await asyncio.sleep(0.5)
        
        # 获取分析选项
        options = analysis_options or {}
        enable_ocr = options.get("enable_ocr", True)
        enable_scene_analysis = options.get("enable_scene_analysis", True)
        enable_object_detection = options.get("enable_object_detection", True)
        language = options.get("language", "auto")
        detail_level = options.get("detail_level", "medium")
        
        # 模拟OCR结果
        ocr_results = []
        extracted_text = ""
        if enable_ocr:
            ocr_results = await self.extract_text(image_path, language)
            extracted_text = " ".join([ocr.text for ocr in ocr_results])
        
        # 模拟场景分析
        scene_analysis = SceneAnalysisResult(
            description="模拟场景分析失败",
            confidence=0.0,
            tags=[]
        )
        if enable_scene_analysis:
            scene_analysis = await self.describe_scene(image_path, detail_level)
        
        # 模拟目标检测
        objects = []
        if enable_object_detection:
            objects = await self.detect_objects(image_path)
        
        # 从文件名推断时间戳
        frame_timestamp = self._extract_timestamp_from_filename(image_path)
        
        processing_time = time.time() - start_time
        
        return ImageAnalysisResult(
            frame_timestamp=frame_timestamp,
            frame_path=image_path,
            ocr_results=ocr_results,
            extracted_text=extracted_text,
            scene_analysis=scene_analysis,
            objects=objects,
            processing_time=processing_time,
            model_used=self.model_name
        )
    
    async def extract_text(self, image_path: str, language: str = "auto") -> List[OCRResult]:
        """
        从图像中提取文字（模拟实现）
        
        Args:
            image_path: 图像文件路径
            language: 语言代码
        
        Returns:
            List[OCRResult]: OCR结果列表
        """
        # 模拟处理延迟
        await asyncio.sleep(0.2)
        
        # 基于文件名生成不同的模拟文本
        import hashlib
        file_hash = hashlib.md5(image_path.encode()).hexdigest()
        text_index = int(file_hash[:2], 16) % len(self.mock_texts)
        
        mock_text = self.mock_texts[text_index]
        
        # 根据语言调整文本
        if language in ["zh", "zh-cn", "chinese"]:
            if "Mock" in mock_text or "Sample" in mock_text:
                mock_text = "这是一段中文OCR识别文本"
        elif language in ["en", "english"]:
            if "这是" in mock_text or "图像" in mock_text:
                mock_text = "This is a sample OCR text from image"
        
        return [
            OCRResult(
                text=mock_text,
                confidence=0.85 + (int(file_hash[2:4], 16) % 15) / 100,  # 0.85-0.99
                bounding_box={
                    "x": 10,
                    "y": 10,
                    "width": 200,
                    "height": 30
                },
                language=language if language != "auto" else "zh-cn"
            )
        ]
    
    async def describe_scene(self, image_path: str, detail_level: str = "medium") -> SceneAnalysisResult:
        """
        描述图像场景（模拟实现）
        
        Args:
            image_path: 图像文件路径
            detail_level: 详细程度
        
        Returns:
            SceneAnalysisResult: 场景分析结果
        """
        # 模拟处理延迟
        await asyncio.sleep(0.3)
        
        # 基于文件名生成不同的模拟场景
        import hashlib
        file_hash = hashlib.md5(image_path.encode()).hexdigest()
        scene_index = int(file_hash[4:6], 16) % len(self.mock_scenes)
        color_index = int(file_hash[6:8], 16) % len(self.mock_colors)
        
        description = self.mock_scenes[scene_index]
        colors = self.mock_colors[color_index]
        
        # 根据详细程度调整描述
        if detail_level == "high":
            description += "，光线良好，构图均衡，色彩饱和度适中"
        elif detail_level == "low":
            description = description.split("，")[0]  # 只保留第一部分
        
        # 生成标签
        tags = []
        if "办公室" in description:
            tags = ["办公", "室内", "工作", "电脑"]
        elif "自然" in description:
            tags = ["自然", "户外", "风景", "植物"]
        elif "会议室" in description:
            tags = ["会议", "室内", "商务", "屏幕"]
        elif "街道" in description:
            tags = ["城市", "户外", "交通", "建筑"]
        else:
            tags = ["室内", "现代", "简洁"]
        
        return SceneAnalysisResult(
            description=description,
            confidence=0.80 + (int(file_hash[8:10], 16) % 20) / 100,  # 0.80-0.99
            tags=tags,
            colors=colors,
            composition="居中构图" if "center" in image_path.lower() else "三分构图"
        )
    
    async def detect_objects(self, image_path: str) -> List[ObjectDetectionResult]:
        """
        检测图像中的对象（模拟实现）
        
        Args:
            image_path: 图像文件路径
        
        Returns:
            List[ObjectDetectionResult]: 检测到的对象列表
        """
        # 模拟处理延迟
        await asyncio.sleep(0.2)
        
        # 基于文件名生成不同的模拟对象
        import hashlib
        file_hash = hashlib.md5(image_path.encode()).hexdigest()
        
        # 生成2-4个对象
        num_objects = 2 + int(file_hash[10:12], 16) % 3
        objects = []
        
        for i in range(num_objects):
            obj_index = (int(file_hash[12+i*2:14+i*2], 16)) % len(self.mock_objects)
            confidence = 0.70 + (int(file_hash[14+i*2:16+i*2], 16) % 30) / 100  # 0.70-0.99
            
            # 生成边界框
            x = 10 + i * 50
            y = 10 + i * 40
            width = 80 + (int(file_hash[16+i*2:18+i*2], 16) % 40)
            height = 60 + (int(file_hash[18+i*2:20+i*2], 16) % 40)
            
            objects.append(ObjectDetectionResult(
                label=self.mock_objects[obj_index],
                confidence=confidence,
                bounding_box={
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                }
            ))
        
        return objects
    
    def _extract_timestamp_from_filename(self, image_path: str) -> float:
        """从文件名中提取时间戳"""
        try:
            # 尝试从文件名中提取时间戳
            # 假设文件名格式如: frame_123.45.jpg
            filename = Path(image_path).stem
            if "frame_" in filename:
                timestamp_str = filename.split("frame_")[1]
                return float(timestamp_str)
            
            # 如果没有时间戳，基于文件名生成一个
            import hashlib
            file_hash = hashlib.md5(image_path.encode()).hexdigest()
            return float(int(file_hash[:8], 16) % 3600)  # 0-3600秒
            
        except Exception as e:
            logger.warning(f"无法从文件名提取时间戳: {str(e)}")
            return 0.0 