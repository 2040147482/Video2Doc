"""
摘要服务模型定义
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    """摘要请求模型"""
    task_id: str = Field(..., description="视频处理任务ID")
    language: str = Field("zh-cn", description="摘要语言，如: zh-cn, en")
    detail_level: str = Field("medium", description="摘要详细程度: low, medium, high")
    include_chapters: bool = Field(True, description="是否包含章节")
    include_key_points: bool = Field(True, description="是否包含关键点")
    max_key_points: int = Field(5, description="最大关键点数量")
    max_length: Optional[int] = Field(None, description="摘要最大长度（字符数）")
    focus_topics: Optional[List[str]] = Field(None, description="重点关注的主题")


class SummaryResponse(BaseModel):
    """摘要响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="响应消息")


class SummaryStatusResponse(BaseModel):
    """摘要状态响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    progress: float = Field(..., description="处理进度 (0-100)")
    result: Optional[Dict[str, Any]] = Field(None, description="摘要结果")
    error: Optional[str] = Field(None, description="错误信息") 