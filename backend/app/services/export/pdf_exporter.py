"""
PDF导出器
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from .base import BaseExporter
from app.models.base import OutputFormat, ExportTemplate

logger = logging.getLogger(__name__)


class PDFExporter(BaseExporter):
    """PDF导出器"""
    
    def __init__(self, output_dir: Path):
        super().__init__(output_dir)
        if not PDF_AVAILABLE:
            logger.warning("ReportLab未安装，PDF导出功能不可用")
    
    @property
    def format(self) -> OutputFormat:
        return OutputFormat.PDF
    
    @property
    def file_extension(self) -> str:
        return ".pdf"
    
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
        """导出PDF格式"""
        if not PDF_AVAILABLE:
            raise RuntimeError("ReportLab未安装，无法生成PDF")
        
        logger.info(f"开始导出PDF: {task_id}")
        
        sections = self._extract_content_sections(content_data)
        filename = self._get_output_filename(task_id, custom_filename)
        output_path = self.output_dir / filename
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        # 构建内容
        story = self._build_pdf_content(
            sections, template, include_images, include_timestamps, include_metadata
        )
        
        # 生成PDF
        doc.build(story)
        
        logger.info(f"PDF导出完成: {output_path}")
        return output_path
    
    def _build_pdf_content(
        self,
        sections: Dict[str, Any],
        template: ExportTemplate,
        include_images: bool,
        include_timestamps: bool,
        include_metadata: bool
    ) -> list:
        """构建PDF内容"""
        story = []
        styles = getSampleStyleSheet()
        
        # 自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=20,
            textColor=colors.darkblue,
            spaceAfter=20,
            alignment=1  # 居中
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.darkgreen,
            spaceAfter=12,
            spaceBefore=12
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.darkslategray,
            spaceAfter=8,
            spaceBefore=8
        )
        
        # 标题
        story.append(Paragraph(sections['title'], title_style))
        story.append(Spacer(1, 20))
        
        # 元数据表格
        if include_metadata and template != ExportTemplate.SIMPLE:
            story.append(Paragraph("文档信息", heading_style))
            metadata_table = self._create_metadata_table(sections['metadata'])
            if metadata_table:
                story.append(metadata_table)
                story.append(Spacer(1, 20))
        
        # 概述
        if sections['overview']:
            story.append(Paragraph("概述", heading_style))
            overview_text = self._clean_text(sections['overview'])
            story.append(Paragraph(overview_text, styles['Normal']))
            story.append(Spacer(1, 15))
        
        # 关键点
        if sections['key_points']:
            story.append(Paragraph("关键要点", heading_style))
            for i, point in enumerate(sections['key_points'], 1):
                if isinstance(point, dict):
                    point_text = point.get('description', str(point))
                    timestamp = point.get('timestamp')
                    if include_timestamps and timestamp:
                        text = f"{i}. {point_text} [{self._format_timestamp(timestamp)}]"
                    else:
                        text = f"{i}. {point_text}"
                else:
                    text = f"{i}. {point}"
                
                story.append(Paragraph(text, styles['Normal']))
                story.append(Spacer(1, 6))
            story.append(Spacer(1, 15))
        
        # 章节内容
        if sections['chapters']:
            story.append(Paragraph("详细内容", heading_style))
            for i, chapter in enumerate(sections['chapters'], 1):
                if isinstance(chapter, dict):
                    title = chapter.get('title', f'第{i}章')
                    content = chapter.get('content', '')
                    start_time = chapter.get('start_time')
                    
                    if include_timestamps and start_time:
                        chapter_title = f"{title} [{self._format_timestamp(start_time)}]"
                    else:
                        chapter_title = title
                    
                    story.append(Paragraph(chapter_title, subheading_style))
                    
                    if content:
                        content_text = self._clean_text(content)
                        story.append(Paragraph(content_text, styles['Normal']))
                        story.append(Spacer(1, 12))
                else:
                    story.append(Paragraph(f"第{i}章", subheading_style))
                    chapter_text = self._clean_text(str(chapter))
                    story.append(Paragraph(chapter_text, styles['Normal']))
                    story.append(Spacer(1, 12))
        
        # 完整转录（详细模板）
        if template == ExportTemplate.DETAILED and sections['transcription']:
            story.append(PageBreak())
            story.append(Paragraph("完整转录", heading_style))
            transcription_text = self._clean_text(sections['transcription'])
            # 使用等宽字体样式
            code_style = ParagraphStyle(
                'Code',
                parent=styles['Code'],
                fontSize=10,
                leftIndent=20,
                rightIndent=20
            )
            story.append(Paragraph(transcription_text, code_style))
            story.append(Spacer(1, 15))
        
        # 图像信息
        if include_images and sections['images'] and template != ExportTemplate.SIMPLE:
            story.append(Paragraph("相关图片", heading_style))
            for i, image in enumerate(sections['images'], 1):
                if isinstance(image, dict):
                    description = image.get('description', f'图片 {i}')
                    timestamp = image.get('timestamp')
                    url = image.get('url', image.get('path', ''))
                    
                    if include_timestamps and timestamp:
                        image_text = f"{i}. {description} [{self._format_timestamp(timestamp)}]"
                    else:
                        image_text = f"{i}. {description}"
                    
                    story.append(Paragraph(image_text, styles['Normal']))
                    if url:
                        story.append(Paragraph(f"URL: {url}", styles['Code']))
                    story.append(Spacer(1, 8))
            story.append(Spacer(1, 15))
        
        # 主题和关键词
        if template in [ExportTemplate.ACADEMIC, ExportTemplate.DETAILED]:
            if sections['topics']:
                story.append(Paragraph("主要主题", heading_style))
                for topic in sections['topics']:
                    story.append(Paragraph(f"• {topic}", styles['Normal']))
                    story.append(Spacer(1, 4))
                story.append(Spacer(1, 15))
            
            if sections['keywords']:
                story.append(Paragraph("关键词", heading_style))
                keywords_str = ", ".join(sections['keywords'])
                story.append(Paragraph(keywords_str, styles['Normal']))
                story.append(Spacer(1, 15))
        
        # 脚注
        if include_metadata:
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.gray,
                alignment=1  # 居中
            )
            story.append(Paragraph("<i>本文档由AI自动生成</i>", footer_style))
        
        return story
    
    def _create_metadata_table(self, metadata: Dict[str, Any]) -> Optional[Table]:
        """创建元数据表格"""
        data = []
        
        duration = metadata.get('duration', 0)
        if duration:
            data.append(['视频时长', self._format_timestamp(duration)])
        
        generated_at = metadata.get('generated_at', '')
        if generated_at:
            try:
                dt = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                data.append(['生成时间', formatted_time])
            except:
                data.append(['生成时间', generated_at])
        
        model = metadata.get('model_used', '')
        if model:
            data.append(['AI模型', model])
        
        processing_time = metadata.get('processing_time', 0)
        if processing_time:
            data.append(['处理时间', f'{processing_time:.2f}秒'])
        
        if not data:
            return None
        
        table = Table(data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table 