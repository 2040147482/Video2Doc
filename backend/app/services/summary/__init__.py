"""
AI摘要生成服务包
"""

from app.services.summary.base import BaseSummaryService
from app.services.summary.mock_service import MockSummaryService

# 默认使用模拟摘要服务
default_service = MockSummaryService()

__all__ = [
    "BaseSummaryService",
    "MockSummaryService",
    "default_service"
] 