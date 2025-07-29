"""
导出服务基础接口
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from app.models.base import OutputFormat, ExportTemplate

logger = logging.getLogger(__name__)


class BaseExporter(ABC):
    """导出器基础类"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    @abstractmethod
    def format(self) -> OutputFormat:
        """导出格式"""
        pass
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """文件扩展名"""
        pass
    
    @abstractmethod
    async def export(
        self,
        task_id: str,
        content_data: Dict[str, Any],
        template: ExportTemplate = ExportTemplate.STANDARD,
        include_images: bool = True,
        include_timestamps: bool = True,
        include_metadata: bool = True,
        custom_filename: Optional[str] = None
    ) -> Path:
        """
        导出内容
        
        Args:
            task_id: 任务ID
            content_data: 内容数据
            template: 导出模板
            include_images: 是否包含图片
            include_timestamps: 是否包含时间戳
            include_metadata: 是否包含元数据
            custom_filename: 自定义文件名
            
        Returns:
            导出文件路径
        """
        pass
    
    def _get_output_filename(self, task_id: str, custom_filename: Optional[str] = None) -> str:
        """获取输出文件名"""
        if custom_filename:
            # 确保有正确的扩展名
            if not custom_filename.endswith(self.file_extension):
                return f"{custom_filename}{self.file_extension}"
            return custom_filename
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{task_id}_{timestamp}{self.file_extension}"
    
    def _format_timestamp(self, timestamp: float) -> str:
        """格式化时间戳"""
        hours = int(timestamp // 3600)
        minutes = int((timestamp % 3600) // 60)
        seconds = int(timestamp % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _clean_text(self, text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        # 移除多余的空行
        lines = text.split('\n')
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
                prev_empty = False
            elif not prev_empty:
                cleaned_lines.append("")
                prev_empty = True
                
        return '\n'.join(cleaned_lines).strip()
    
    def _extract_content_sections(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取内容sections"""
        sections = {
            'title': content_data.get('title', '视频内容分析报告'),
            'overview': content_data.get('overview', ''),
            'chapters': content_data.get('chapters', []),
            'key_points': content_data.get('key_points', []),
            'topics': content_data.get('topics', []),
            'keywords': content_data.get('keywords', []),
            'transcription': content_data.get('transcription', ''),
            'images': content_data.get('images', []),
            'metadata': {
                'duration': content_data.get('content_duration', 0),
                'generated_at': content_data.get('generated_at', datetime.now().isoformat()),
                'model_used': content_data.get('model_used', 'AI Assistant'),
                'processing_time': content_data.get('processing_time', 0)
            }
        }
        return sections 