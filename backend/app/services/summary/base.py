"""
AI摘要服务基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SummarySection(BaseModel):
    """摘要的一个章节"""
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    source_timestamps: List[float] = Field(default_factory=list, description="来源时间戳（秒）")
    source_frames: List[int] = Field(default_factory=list, description="来源帧编号")
    importance: float = Field(0.0, description="重要性评分（0-1）")
    keywords: List[str] = Field(default_factory=list, description="关键词列表")


class SummaryChapter(BaseModel):
    """摘要的一个章节，可能包含多个小节"""
    title: str = Field(..., description="章节标题")
    sections: List[SummarySection] = Field(default_factory=list, description="小节列表")
    start_time: float = Field(0.0, description="开始时间（秒）")
    end_time: float = Field(0.0, description="结束时间（秒）")


class KeyPoint(BaseModel):
    """关键点"""
    content: str = Field(..., description="关键点内容")
    timestamp: Optional[float] = Field(None, description="时间戳（秒）")
    frame_number: Optional[int] = Field(None, description="帧编号")
    source_type: str = Field("auto", description="来源类型：audio, video, combined")
    importance: float = Field(0.0, description="重要性评分（0-1）")


class SummaryResult(BaseModel):
    """摘要结果"""
    title: str = Field(..., description="摘要标题")
    overview: str = Field(..., description="总体概述")
    key_points: List[KeyPoint] = Field(default_factory=list, description="关键点列表")
    chapters: List[SummaryChapter] = Field(default_factory=list, description="章节列表")
    topics: List[str] = Field(default_factory=list, description="主题列表")
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="生成时间")
    model_used: str = Field(..., description="使用的模型")
    processing_time: float = Field(..., description="处理时间（秒）")
    content_duration: float = Field(0.0, description="内容时长（秒）")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()


class BaseSummaryService(ABC):
    """AI摘要服务基类"""
    
    @abstractmethod
    async def generate_summary(
        self, 
        task_id: str,
        transcription: Optional[Dict[str, Any]] = None,
        image_analysis: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> SummaryResult:
        """
        生成内容摘要
        
        Args:
            task_id: 任务ID
            transcription: 语音识别结果
            image_analysis: 图像分析结果
            metadata: 视频元数据
            options: 摘要选项
            
        Returns:
            摘要结果
        """
        pass
    
    @abstractmethod
    async def generate_title(self, content: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        生成标题
        
        Args:
            content: 内容文本
            options: 选项
            
        Returns:
            生成的标题
        """
        pass
    
    @abstractmethod
    async def extract_key_points(
        self, 
        content: str, 
        max_points: int = 5,
        options: Optional[Dict[str, Any]] = None
    ) -> List[KeyPoint]:
        """
        提取关键点
        
        Args:
            content: 内容文本
            max_points: 最大关键点数量
            options: 选项
            
        Returns:
            关键点列表
        """
        pass 