"""
ZIP打包导出器
"""

import logging
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional, List

from .base import BaseExporter
from app.models.base import OutputFormat, ExportTemplate

logger = logging.getLogger(__name__)


class ZipExporter(BaseExporter):
    """ZIP打包导出器"""
    
    @property
    def format(self) -> OutputFormat:
        return OutputFormat.ZIP
    
    @property
    def file_extension(self) -> str:
        return ".zip"
    
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
        导出ZIP格式 - 将多种格式打包到一个ZIP文件中
        
        Note: 此方法需要其他导出器实例来生成各种格式的文件
        """
        logger.info(f"开始导出ZIP: {task_id}")
        
        filename = self._get_output_filename(task_id, custom_filename)
        output_path = self.output_dir / filename
        
        # 创建临时目录存放各种格式文件
        temp_dir = self.output_dir / f"temp_{task_id}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # 生成各种格式的文件
            generated_files = await self._generate_all_formats(
                temp_dir, task_id, content_data, template, 
                include_images, include_timestamps, include_metadata
            )
            
            # 创建ZIP文件
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # 添加文档文件
                for file_path in generated_files:
                    if file_path.exists():
                        arcname = file_path.name
                        zip_file.write(file_path, arcname)
                        logger.debug(f"添加文件到ZIP: {arcname}")
                
                # 添加图片文件（如果有的话）
                if include_images:
                    await self._add_images_to_zip(zip_file, content_data, temp_dir)
                
                # 添加元数据文件
                if include_metadata:
                    await self._add_metadata_to_zip(zip_file, content_data, temp_dir)
            
            logger.info(f"ZIP导出完成: {output_path}")
            return output_path
            
        finally:
            # 清理临时目录
            self._cleanup_temp_dir(temp_dir)
    
    async def _generate_all_formats(
        self,
        temp_dir: Path,
        task_id: str,
        content_data: Dict[str, Any],
        template: ExportTemplate,
        include_images: bool,
        include_timestamps: bool,
        include_metadata: bool
    ) -> List[Path]:
        """生成所有格式的文件"""
        from . import MarkdownExporter, HTMLExporter, TxtExporter, PDFExporter
        
        generated_files = []
        
        # 实例化各个导出器
        exporters = [
            MarkdownExporter(temp_dir),
            HTMLExporter(temp_dir),
            TxtExporter(temp_dir),
        ]
        
        # 尝试添加PDF导出器
        try:
            pdf_exporter = PDFExporter(temp_dir)
            exporters.append(pdf_exporter)
        except Exception as e:
            logger.warning(f"PDF导出器不可用: {e}")
        
        # 生成各种格式
        for exporter in exporters:
            try:
                file_path = await exporter.export(
                    task_id=task_id,
                    content_data=content_data,
                    template=template,
                    include_images=include_images,
                    include_timestamps=include_timestamps,
                    include_metadata=include_metadata,
                    custom_filename=f"{task_id}_{exporter.format.value}"
                )
                generated_files.append(file_path)
                logger.debug(f"生成{exporter.format.value}格式: {file_path}")
            except Exception as e:
                logger.error(f"生成{exporter.format.value}格式失败: {e}")
        
        return generated_files
    
    async def _add_images_to_zip(
        self, 
        zip_file: zipfile.ZipFile, 
        content_data: Dict[str, Any], 
        temp_dir: Path
    ):
        """添加图片文件到ZIP"""
        images = content_data.get('images', [])
        if not images:
            return
        
        # 创建图片目录
        images_added = 0
        for i, image in enumerate(images, 1):
            if isinstance(image, dict):
                image_url = image.get('url', image.get('path', ''))
                if image_url and self._is_local_file(image_url):
                    try:
                        image_path = Path(image_url)
                        if image_path.exists():
                            # 使用安全的文件名
                            safe_filename = f"image_{i:03d}{image_path.suffix}"
                            zip_file.write(image_path, f"images/{safe_filename}")
                            images_added += 1
                    except Exception as e:
                        logger.warning(f"添加图片失败 {image_url}: {e}")
        
        if images_added > 0:
            logger.info(f"添加了 {images_added} 个图片文件到ZIP")
    
    async def _add_metadata_to_zip(
        self, 
        zip_file: zipfile.ZipFile, 
        content_data: Dict[str, Any], 
        temp_dir: Path
    ):
        """添加元数据文件到ZIP"""
        import json
        
        # 创建详细的元数据文件
        metadata = {
            'export_info': {
                'export_time': content_data.get('generated_at', ''),
                'format_version': '1.0',
                'exporter': 'Video2Doc',
            },
            'content_metadata': {
                'title': content_data.get('title', ''),
                'duration': content_data.get('content_duration', 0),
                'model_used': content_data.get('model_used', ''),
                'processing_time': content_data.get('processing_time', 0),
            },
            'structure': {
                'chapters_count': len(content_data.get('chapters', [])),
                'key_points_count': len(content_data.get('key_points', [])),
                'images_count': len(content_data.get('images', [])),
                'topics_count': len(content_data.get('topics', [])),
                'keywords_count': len(content_data.get('keywords', [])),
            }
        }
        
        # 将元数据写入临时文件
        metadata_file = temp_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # 添加到ZIP
        zip_file.write(metadata_file, "metadata.json")
        
        # 创建README文件
        readme_content = self._generate_readme_content(content_data)
        readme_file = temp_dir / "README.txt"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        zip_file.write(readme_file, "README.txt")
    
    def _generate_readme_content(self, content_data: Dict[str, Any]) -> str:
        """生成README内容"""
        title = content_data.get('title', '视频内容分析报告')
        
        readme_lines = [
            f"# {title}",
            "",
            "## 文件说明",
            "",
            "此ZIP文件包含以下内容：",
            "",
            "### 文档文件",
            "- *.md - Markdown格式文档，适用于Obsidian、Notion等工具",
            "- *.html - HTML格式文档，可在浏览器中查看",
            "- *.txt - 纯文本格式文档，兼容性最佳",
            "- *.pdf - PDF格式文档，适合打印和分享（如果可用）",
            "",
            "### 媒体文件",
            "- images/ - 相关图片文件（如果有）",
            "",
            "### 元数据",
            "- metadata.json - 详细的文档元数据信息",
            "- README.txt - 本说明文件",
            "",
            "## 推荐使用方式",
            "",
            "1. **学习笔记**: 使用Markdown文件导入到Obsidian或Notion",
            "2. **在线分享**: 使用HTML文件在浏览器中查看", 
            "3. **打印存档**: 使用PDF文件进行打印",
            "4. **纯文本处理**: 使用TXT文件进行进一步的文本处理",
            "",
            "## 技术信息",
            "",
            f"- 生成时间: {content_data.get('generated_at', 'N/A')}",
            f"- AI模型: {content_data.get('model_used', 'N/A')}",
            f"- 处理时间: {content_data.get('processing_time', 0):.2f}秒",
            "",
            "---",
            "本内容由Video2Doc AI工具自动生成",
        ]
        
        return "\n".join(readme_lines)
    
    def _is_local_file(self, path: str) -> bool:
        """检查是否为本地文件路径"""
        return not (path.startswith('http://') or path.startswith('https://'))
    
    def _cleanup_temp_dir(self, temp_dir: Path):
        """清理临时目录"""
        try:
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                logger.debug(f"清理临时目录: {temp_dir}")
        except Exception as e:
            logger.warning(f"清理临时目录失败: {e}") 