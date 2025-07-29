"""
HTML导出器
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import html

from .base import BaseExporter
from app.models.base import OutputFormat, ExportTemplate

logger = logging.getLogger(__name__)


class HTMLExporter(BaseExporter):
    """HTML导出器"""
    
    @property
    def format(self) -> OutputFormat:
        return OutputFormat.HTML
    
    @property
    def file_extension(self) -> str:
        return ".html"
    
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
        """导出HTML格式"""
        logger.info(f"开始导出HTML: {task_id}")
        
        sections = self._extract_content_sections(content_data)
        filename = self._get_output_filename(task_id, custom_filename)
        output_path = self.output_dir / filename
        
        html_content = self._generate_html_content(
            sections, template, include_images, include_timestamps, include_metadata
        )
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML导出完成: {output_path}")
        return output_path
    
    def _generate_html_content(
        self,
        sections: Dict[str, Any],
        template: ExportTemplate,
        include_images: bool,
        include_timestamps: bool,
        include_metadata: bool
    ) -> str:
        """生成HTML内容"""
        title = html.escape(sections['title'])
        
        # HTML模板
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="zh-CN">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'    <title>{title}</title>',
            '    <style>',
            self._get_css_styles(template),
            '    </style>',
            '</head>',
            '<body>',
            '    <div class="container">',
        ]
        
        # 标题
        html_parts.append(f'        <h1 class="main-title">{title}</h1>')
        
        # 导航菜单
        if template != ExportTemplate.SIMPLE:
            html_parts.extend(self._generate_navigation(sections))
        
        # 元数据
        if include_metadata and template != ExportTemplate.SIMPLE:
            html_parts.extend(self._generate_metadata_html(sections['metadata']))
        
        # 概述
        if sections['overview']:
            html_parts.extend([
                '        <section id="overview" class="section">',
                '            <h2>概述</h2>',
                f'            <div class="content">{self._format_html_text(sections["overview"])}</div>',
                '        </section>'
            ])
        
        # 关键点
        if sections['key_points']:
            html_parts.extend(self._generate_key_points_html(
                sections['key_points'], include_timestamps
            ))
        
        # 章节内容
        if sections['chapters']:
            html_parts.extend(self._generate_chapters_html(
                sections['chapters'], include_timestamps
            ))
        
        # 完整转录
        if template == ExportTemplate.DETAILED and sections['transcription']:
            html_parts.extend([
                '        <section id="transcription" class="section">',
                '            <h2>完整转录</h2>',
                '            <div class="transcription">',
                f'                <pre>{html.escape(sections["transcription"])}</pre>',
                '            </div>',
                '        </section>'
            ])
        
        # 图像
        if include_images and sections['images'] and template != ExportTemplate.SIMPLE:
            html_parts.extend(self._generate_images_html(
                sections['images'], include_timestamps
            ))
        
        # 主题和关键词
        if template in [ExportTemplate.ACADEMIC, ExportTemplate.DETAILED]:
            if sections['topics']:
                html_parts.extend([
                    '        <section id="topics" class="section">',
                    '            <h2>主要主题</h2>',
                    '            <ul class="topics-list">',
                ])
                for topic in sections['topics']:
                    html_parts.append(f'                <li>{html.escape(str(topic))}</li>')
                html_parts.extend([
                    '            </ul>',
                    '        </section>'
                ])
            
            if sections['keywords']:
                keywords_html = ', '.join([html.escape(str(kw)) for kw in sections['keywords']])
                html_parts.extend([
                    '        <section id="keywords" class="section">',
                    '            <h2>关键词</h2>',
                    f'            <div class="keywords">{keywords_html}</div>',
                    '        </section>'
                ])
        
        # 脚注
        if include_metadata:
            html_parts.extend([
                '        <footer class="footer">',
                '            <p><em>本文档由AI自动生成</em></p>',
                '        </footer>'
            ])
        
        html_parts.extend([
            '    </div>',
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html_parts)
    
    def _get_css_styles(self, template: ExportTemplate) -> str:
        """获取CSS样式"""
        base_styles = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .main-title {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        h2 {
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }
        
        h3 {
            color: #5a6c7d;
            margin-top: 25px;
        }
        
        .content {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #e9ecef;
        }
        
        .metadata-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .metadata-table th,
        .metadata-table td {
            border: 1px solid #dee2e6;
            padding: 12px;
            text-align: left;
        }
        
        .metadata-table th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        
        .key-points-list {
            list-style: none;
            padding: 0;
        }
        
        .key-points-list li {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #28a745;
        }
        
        .timestamp {
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 0.9em;
            color: #495057;
        }
        
        .navigation {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        
        .navigation ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .navigation a {
            color: #3498db;
            text-decoration: none;
            padding: 5px 10px;
            border-radius: 3px;
            transition: background-color 0.2s;
        }
        
        .navigation a:hover {
            background-color: #e9ecef;
        }
        
        .transcription {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            overflow-x: auto;
        }
        
        .transcription pre {
            margin: 0;
            padding: 20px;
            white-space: pre-wrap;
        }
        
        .images-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .image-item {
            border: 1px solid #dee2e6;
            border-radius: 5px;
            overflow: hidden;
        }
        
        .image-item img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .image-caption {
            padding: 10px;
            background: #f8f9fa;
            font-size: 0.9em;
        }
        
        .topics-list {
            columns: 2;
            column-gap: 30px;
        }
        
        .keywords {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
        }
        
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            text-align: center;
            color: #6c757d;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .container {
                padding: 20px;
            }
            
            .navigation ul {
                flex-direction: column;
                gap: 5px;
            }
            
            .topics-list {
                columns: 1;
            }
        }
        """
        
        # 根据模板调整样式
        if template == ExportTemplate.ACADEMIC:
            base_styles += """
            .main-title {
                text-align: center;
                font-size: 2.5em;
            }
            
            .metadata-table {
                font-size: 0.9em;
            }
            """
        elif template == ExportTemplate.PRESENTATION:
            base_styles += """
            h2 {
                font-size: 2em;
                text-align: center;
                border: none;
                color: #2c3e50;
            }
            
            .section {
                text-align: center;
                margin-bottom: 60px;
            }
            """
        
        return base_styles
    
    def _generate_navigation(self, sections: Dict[str, Any]) -> list:
        """生成导航菜单"""
        nav_items = []
        
        if sections['overview']:
            nav_items.append('<li><a href="#overview">概述</a></li>')
        
        if sections['key_points']:
            nav_items.append('<li><a href="#key-points">关键要点</a></li>')
        
        if sections['chapters']:
            nav_items.append('<li><a href="#chapters">详细内容</a></li>')
        
        if sections['images']:
            nav_items.append('<li><a href="#images">相关图片</a></li>')
        
        if sections['topics']:
            nav_items.append('<li><a href="#topics">主要主题</a></li>')
        
        if sections['keywords']:
            nav_items.append('<li><a href="#keywords">关键词</a></li>')
        
        if not nav_items:
            return []
        
        return [
            '        <nav class="navigation">',
            '            <h3>目录</h3>',
            '            <ul>',
            *[f'                {item}' for item in nav_items],
            '            </ul>',
            '        </nav>'
        ]
    
    def _generate_metadata_html(self, metadata: Dict[str, Any]) -> list:
        """生成元数据HTML"""
        lines = [
            '        <section id="metadata" class="section">',
            '            <h2>文档信息</h2>',
            '            <table class="metadata-table">',
        ]
        
        duration = metadata.get('duration', 0)
        if duration:
            lines.append(f'                <tr><th>视频时长</th><td>{self._format_timestamp(duration)}</td></tr>')
        
        generated_at = metadata.get('generated_at', '')
        if generated_at:
            try:
                dt = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                lines.append(f'                <tr><th>生成时间</th><td>{formatted_time}</td></tr>')
            except:
                lines.append(f'                <tr><th>生成时间</th><td>{html.escape(generated_at)}</td></tr>')
        
        model = metadata.get('model_used', '')
        if model:
            lines.append(f'                <tr><th>AI模型</th><td>{html.escape(model)}</td></tr>')
        
        processing_time = metadata.get('processing_time', 0)
        if processing_time:
            lines.append(f'                <tr><th>处理时间</th><td>{processing_time:.2f}秒</td></tr>')
        
        lines.extend([
            '            </table>',
            '        </section>'
        ])
        
        return lines
    
    def _generate_key_points_html(self, key_points: list, include_timestamps: bool) -> list:
        """生成关键点HTML"""
        lines = [
            '        <section id="key-points" class="section">',
            '            <h2>关键要点</h2>',
            '            <ol class="key-points-list">',
        ]
        
        for point in key_points:
            if isinstance(point, dict):
                point_text = html.escape(point.get('description', str(point)))
                timestamp = point.get('timestamp')
                if include_timestamps and timestamp:
                    timestamp_str = f' <span class="timestamp">{self._format_timestamp(timestamp)}</span>'
                    lines.append(f'                <li>{point_text}{timestamp_str}</li>')
                else:
                    lines.append(f'                <li>{point_text}</li>')
            else:
                lines.append(f'                <li>{html.escape(str(point))}</li>')
        
        lines.extend([
            '            </ol>',
            '        </section>'
        ])
        
        return lines
    
    def _generate_chapters_html(self, chapters: list, include_timestamps: bool) -> list:
        """生成章节HTML"""
        lines = [
            '        <section id="chapters" class="section">',
            '            <h2>详细内容</h2>',
        ]
        
        for i, chapter in enumerate(chapters, 1):
            if isinstance(chapter, dict):
                title = html.escape(chapter.get('title', f'第{i}章'))
                content = chapter.get('content', '')
                start_time = chapter.get('start_time')
                
                if include_timestamps and start_time:
                    timestamp_str = f' <span class="timestamp">{self._format_timestamp(start_time)}</span>'
                    lines.append(f'            <h3>{title}{timestamp_str}</h3>')
                else:
                    lines.append(f'            <h3>{title}</h3>')
                
                if content:
                    lines.append(f'            <div class="content">{self._format_html_text(content)}</div>')
            else:
                lines.append(f'            <h3>第{i}章</h3>')
                lines.append(f'            <div class="content">{self._format_html_text(str(chapter))}</div>')
        
        lines.append('        </section>')
        return lines
    
    def _generate_images_html(self, images: list, include_timestamps: bool) -> list:
        """生成图片HTML"""
        lines = [
            '        <section id="images" class="section">',
            '            <h2>相关图片</h2>',
            '            <div class="images-grid">',
        ]
        
        for i, image in enumerate(images, 1):
            if isinstance(image, dict):
                description = html.escape(image.get('description', f'图片 {i}'))
                timestamp = image.get('timestamp')
                url = image.get('url', image.get('path', ''))
                
                lines.append('                <div class="image-item">')
                if url:
                    lines.append(f'                    <img src="{html.escape(url)}" alt="{description}" />')
                
                caption_parts = [description]
                if include_timestamps and timestamp:
                    caption_parts.append(f'<span class="timestamp">{self._format_timestamp(timestamp)}</span>')
                
                lines.append(f'                    <div class="image-caption">{" - ".join(caption_parts)}</div>')
                lines.append('                </div>')
        
        lines.extend([
            '            </div>',
            '        </section>'
        ])
        
        return lines
    
    def _format_html_text(self, text: str) -> str:
        """格式化HTML文本"""
        if not text:
            return ""
        
        # 转义HTML字符
        escaped_text = html.escape(text)
        
        # 将换行符转换为<br>标签
        formatted_text = escaped_text.replace('\n', '<br>')
        
        return formatted_text 