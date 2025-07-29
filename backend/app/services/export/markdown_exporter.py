"""
Markdown导出器
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .base import BaseExporter
from app.models.base import OutputFormat, ExportTemplate

logger = logging.getLogger(__name__)


class MarkdownExporter(BaseExporter):
    """Markdown导出器"""
    
    @property
    def format(self) -> OutputFormat:
        return OutputFormat.MARKDOWN
    
    @property
    def file_extension(self) -> str:
        return ".md"
    
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
        """导出Markdown格式"""
        logger.info(f"开始导出Markdown: {task_id}")
        
        sections = self._extract_content_sections(content_data)
        filename = self._get_output_filename(task_id, custom_filename)
        output_path = self.output_dir / filename
        
        markdown_content = self._generate_markdown_content(
            sections, template, include_images, include_timestamps, include_metadata
        )
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Markdown导出完成: {output_path}")
        return output_path
    
    def _generate_markdown_content(
        self,
        sections: Dict[str, Any],
        template: ExportTemplate,
        include_images: bool,
        include_timestamps: bool,
        include_metadata: bool
    ) -> str:
        """生成Markdown内容"""
        lines = []
        
        # 标题
        lines.append(f"# {sections['title']}")
        lines.append("")
        
        # 元数据（根据模板）
        if include_metadata and template != ExportTemplate.SIMPLE:
            lines.extend(self._generate_metadata_section(sections['metadata']))
            lines.append("")
        
        # 概述
        if sections['overview']:
            lines.append("## 概述")
            lines.append("")
            lines.append(self._clean_text(sections['overview']))
            lines.append("")
        
        # 关键点
        if sections['key_points']:
            lines.append("## 关键要点")
            lines.append("")
            for i, point in enumerate(sections['key_points'], 1):
                if isinstance(point, dict):
                    point_text = point.get('description', str(point))
                    timestamp = point.get('timestamp')
                    if include_timestamps and timestamp:
                        lines.append(f"{i}. {point_text} `[{self._format_timestamp(timestamp)}]`")
                    else:
                        lines.append(f"{i}. {point_text}")
                else:
                    lines.append(f"{i}. {point}")
            lines.append("")
        
        # 章节内容
        if sections['chapters']:
            lines.append("## 详细内容")
            lines.append("")
            for i, chapter in enumerate(sections['chapters'], 1):
                if isinstance(chapter, dict):
                    title = chapter.get('title', f'第{i}章')
                    content = chapter.get('content', '')
                    start_time = chapter.get('start_time')
                    
                    if include_timestamps and start_time:
                        lines.append(f"### {title} `[{self._format_timestamp(start_time)}]`")
                    else:
                        lines.append(f"### {title}")
                    lines.append("")
                    
                    if content:
                        lines.append(self._clean_text(content))
                        lines.append("")
                else:
                    lines.append(f"### 第{i}章")
                    lines.append("")
                    lines.append(self._clean_text(str(chapter)))
                    lines.append("")
        
        # 完整转录（详细模板）
        if template == ExportTemplate.DETAILED and sections['transcription']:
            lines.append("## 完整转录")
            lines.append("")
            lines.append("```")
            lines.append(self._clean_text(sections['transcription']))
            lines.append("```")
            lines.append("")
        
        # 图像（如果包含）
        if include_images and sections['images'] and template != ExportTemplate.SIMPLE:
            lines.append("## 相关图片")
            lines.append("")
            for i, image in enumerate(sections['images'], 1):
                if isinstance(image, dict):
                    description = image.get('description', f'图片 {i}')
                    timestamp = image.get('timestamp')
                    url = image.get('url', image.get('path', ''))
                    
                    if include_timestamps and timestamp:
                        lines.append(f"### {description} `[{self._format_timestamp(timestamp)}]`")
                    else:
                        lines.append(f"### {description}")
                    
                    if url:
                        lines.append(f"![{description}]({url})")
                    lines.append("")
        
        # 主题和关键词
        if template in [ExportTemplate.ACADEMIC, ExportTemplate.DETAILED]:
            if sections['topics']:
                lines.append("## 主要主题")
                lines.append("")
                for topic in sections['topics']:
                    lines.append(f"- {topic}")
                lines.append("")
            
            if sections['keywords']:
                lines.append("## 关键词")
                lines.append("")
                keywords_str = ", ".join(sections['keywords'])
                lines.append(f"`{keywords_str}`")
                lines.append("")
        
        # 脚注
        if include_metadata:
            lines.append("---")
            lines.append("")
            lines.append("*本文档由AI自动生成*")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_metadata_section(self, metadata: Dict[str, Any]) -> list:
        """生成元数据section"""
        lines = []
        lines.append("## 文档信息")
        lines.append("")
        lines.append("| 项目 | 值 |")
        lines.append("|------|-----|")
        
        duration = metadata.get('duration', 0)
        if duration:
            lines.append(f"| 视频时长 | {self._format_timestamp(duration)} |")
        
        generated_at = metadata.get('generated_at', '')
        if generated_at:
            try:
                dt = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                lines.append(f"| 生成时间 | {formatted_time} |")
            except:
                lines.append(f"| 生成时间 | {generated_at} |")
        
        model = metadata.get('model_used', '')
        if model:
            lines.append(f"| AI模型 | {model} |")
        
        processing_time = metadata.get('processing_time', 0)
        if processing_time:
            lines.append(f"| 处理时间 | {processing_time:.2f}秒 |")
        
        return lines 