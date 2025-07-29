"""
导出服务管理器
"""

import logging
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.config import get_settings
from app.models.base import (
    OutputFormat, ExportTemplate, ExportRequest, 
    ExportResponse, ExportStatus
)
from app.services.queue_service import queue_service
from .markdown_exporter import MarkdownExporter
from .html_exporter import HTMLExporter  
from .txt_exporter import TxtExporter
from .pdf_exporter import PDFExporter
from .zip_exporter import ZipExporter

logger = logging.getLogger(__name__)


class ExportService:
    """导出服务管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.exports_dir = Path(self.settings.results_folder) / "exports"
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        
        # 导出状态存储 - 生产环境应使用数据库
        self._export_status: Dict[str, dict] = {}
        
        # 初始化导出器映射
        self._exporters = {
            OutputFormat.MARKDOWN: MarkdownExporter,
            OutputFormat.HTML: HTMLExporter,
            OutputFormat.TXT: TxtExporter,
            OutputFormat.PDF: PDFExporter,
            OutputFormat.ZIP: ZipExporter,
        }
    
    def _create_export_sync(
        self, 
        task_id: str,
        formats: List[str],
        template: str = "standard",
        include_images: bool = True,
        include_timestamps: bool = True,
        include_metadata: bool = True,
        custom_filename: str = None
    ) -> str:
        """
        同步创建导出任务（用于Celery任务）
        
        Args:
            task_id: 任务ID
            formats: 导出格式列表
            template: 模板名称
            include_images: 是否包含图片
            include_timestamps: 是否包含时间戳
            include_metadata: 是否包含元数据
            custom_filename: 自定义文件名
            
        Returns:
            str: 导出ID
        """
        export_id = str(uuid.uuid4())
        
        logger.info(f"同步创建导出任务: {export_id}, 格式: {formats}")
        
        # 模拟任务数据（在实际实现中应该从任务存储获取）
        mock_result_data = {
            "summary": "这是一个模拟的摘要内容",
            "transcript": "这是一个模拟的转录内容",
            "images": [],
            "metadata": {
                "title": "视频分析结果",
                "created_at": datetime.now().isoformat()
            }
        }
        
        # 创建导出状态
        export_status = {
            "export_id": export_id,
            "task_id": task_id,
            "status": "pending",
            "progress": 0.0,
            "message": "导出任务已创建",
            "formats": formats,
            "template": template,
            "include_images": include_images,
            "include_timestamps": include_timestamps,
            "include_metadata": include_metadata,
            "custom_filename": custom_filename,
            "formats_completed": [],
            "download_urls": {},
            "created_at": datetime.now(),
            "completed_at": None,
            "error_details": None
        }
        
        self._export_status[export_id] = export_status
        
        # 同步执行导出处理
        try:
            self._process_export_sync(export_id, mock_result_data)
            logger.info(f"导出任务完成: {export_id}")
        except Exception as e:
            logger.error(f"导出任务失败: {export_id}, 错误: {str(e)}")
            export_status["status"] = "failed"
            export_status["message"] = f"导出失败: {str(e)}"
        
        return export_id
    
    def _process_export_sync(self, export_id: str, result_data: dict):
        """同步处理导出任务"""
        export_status = self._export_status[export_id]
        
        try:
            export_status["status"] = "processing"
            export_status["message"] = "正在处理导出..."
            
            formats = export_status["formats"]
            total_formats = len(formats)
            
            for i, format_name in enumerate(formats):
                try:
                    # 更新进度
                    progress = (i / total_formats) * 100
                    export_status["progress"] = progress
                    export_status["message"] = f"正在生成 {format_name} 格式..."
                    
                    # 执行导出
                    output_format = OutputFormat(format_name.lower())
                    exporter_class = self._exporters.get(output_format)
                    
                    if not exporter_class:
                        raise ValueError(f"不支持的导出格式: {format_name}")
                    
                    exporter = exporter_class()
                    
                    # 创建导出选项
                    export_options = {
                        "template": export_status["template"],
                        "include_images": export_status["include_images"],
                        "include_timestamps": export_status["include_timestamps"],
                        "include_metadata": export_status["include_metadata"],
                        "custom_filename": export_status["custom_filename"]
                    }
                    
                    # 执行导出
                    output_path = exporter.export(
                        data=result_data,
                        output_dir=self.exports_dir / export_id,
                        options=export_options
                    )
                    
                    # 记录完成的格式
                    export_status["formats_completed"].append(format_name)
                    export_status["download_urls"][format_name] = f"/api/export/{export_id}/download/{format_name}"
                    
                    logger.info(f"格式 {format_name} 导出完成: {output_path}")
                    
                except Exception as e:
                    logger.error(f"格式 {format_name} 导出失败: {str(e)}")
                    raise
            
            # 标记为完成
            export_status["status"] = "completed"
            export_status["progress"] = 100.0
            export_status["message"] = "导出完成"
            export_status["completed_at"] = datetime.now()
            
        except Exception as e:
            export_status["status"] = "failed"
            export_status["message"] = f"导出失败: {str(e)}"
            export_status["error_details"] = str(e)
            raise
    
    async def create_export(self, request: ExportRequest) -> ExportResponse:
        """创建导出任务"""
        export_id = str(uuid.uuid4())
        
        logger.info(f"创建导出任务: {export_id}, 格式: {request.formats}")
        
        # 验证任务ID
        task = queue_service.get_task(request.task_id)
        if not task:
            raise ValueError(f"任务不存在: {request.task_id}")
        
        # 检查任务状态
        if task.get("status") != "completed":
            raise ValueError(f"任务尚未完成: {request.task_id}")
        
        # 获取任务结果
        result_data = task.get("result")
        if not result_data:
            raise ValueError(f"任务结果为空: {request.task_id}")
        
        # 创建导出状态
        export_status = {
            "export_id": export_id,
            "task_id": request.task_id,
            "status": "pending",
            "progress": 0.0,
            "message": "导出任务已创建",
            "formats": request.formats,
            "template": request.template,
            "include_images": request.include_images,
            "include_timestamps": request.include_timestamps,
            "include_metadata": request.include_metadata,
            "custom_filename": request.custom_filename,
            "formats_completed": [],
            "download_urls": {},
            "created_at": datetime.now(),
            "completed_at": None,
            "error_details": None
        }
        
        self._export_status[export_id] = export_status
        
        # 异步执行导出
        import asyncio
        asyncio.create_task(self._process_export(export_id, result_data))
        
        # 计算过期时间（24小时后）
        expires_at = datetime.now() + timedelta(hours=24)
        
        return ExportResponse(
            export_id=export_id,
            status="pending",
            message="导出任务已启动",
            expires_at=expires_at
        )
    
    async def get_export_status(self, export_id: str) -> ExportStatus:
        """获取导出状态"""
        status_data = self._export_status.get(export_id)
        if not status_data:
            raise ValueError(f"导出任务不存在: {export_id}")
        
        return ExportStatus(**status_data)
    
    async def cancel_export(self, export_id: str) -> bool:
        """取消导出任务"""
        status_data = self._export_status.get(export_id)
        if not status_data:
            return False
        
        if status_data["status"] in ["completed", "failed", "cancelled"]:
            return False
        
        status_data["status"] = "cancelled"
        status_data["message"] = "导出任务已取消"
        return True
    
    async def get_download_url(self, export_id: str, format_name: str) -> str:
        """获取下载链接"""
        status_data = self._export_status.get(export_id)
        if not status_data:
            raise ValueError(f"导出任务不存在: {export_id}")
        
        if status_data["status"] != "completed":
            raise ValueError(f"导出任务尚未完成: {export_id}")
        
        download_url = status_data["download_urls"].get(format_name)
        if not download_url:
            raise ValueError(f"格式不存在或未完成: {format_name}")
        
        return download_url
    
    async def _process_export(self, export_id: str, result_data: dict):
        """异步处理导出任务"""
        export_status = self._export_status[export_id]
        
        try:
            export_status["status"] = "processing"
            export_status["message"] = "正在处理导出..."
            
            formats = export_status["formats"]
            total_formats = len(formats)
            
            for i, format_name in enumerate(formats):
                try:
                    # 更新进度
                    progress = (i / total_formats) * 100
                    export_status["progress"] = progress
                    export_status["message"] = f"正在生成 {format_name} 格式..."
                    
                    # 执行导出
                    output_format = OutputFormat(format_name.lower())
                    exporter_class = self._exporters.get(output_format)
                    
                    if not exporter_class:
                        raise ValueError(f"不支持的导出格式: {format_name}")
                    
                    exporter = exporter_class()
                    
                    # 创建导出选项
                    export_options = {
                        "template": export_status["template"],
                        "include_images": export_status["include_images"],
                        "include_timestamps": export_status["include_timestamps"],
                        "include_metadata": export_status["include_metadata"],
                        "custom_filename": export_status["custom_filename"]
                    }
                    
                    # 执行导出
                    output_path = exporter.export(
                        data=result_data,
                        output_dir=self.exports_dir / export_id,
                        options=export_options
                    )
                    
                    # 记录完成的格式
                    export_status["formats_completed"].append(format_name)
                    export_status["download_urls"][format_name] = f"/api/export/{export_id}/download/{format_name}"
                    
                    logger.info(f"格式 {format_name} 导出完成: {output_path}")
                    
                except Exception as e:
                    logger.error(f"格式 {format_name} 导出失败: {str(e)}")
                    raise
            
            # 标记为完成
            export_status["status"] = "completed"
            export_status["progress"] = 100.0
            export_status["message"] = "导出完成"
            export_status["completed_at"] = datetime.now()
            
        except Exception as e:
            export_status["status"] = "failed"
            export_status["message"] = f"导出失败: {str(e)}"
            export_status["error_details"] = str(e)
            logger.error(f"导出任务失败: {export_id}, 错误: {str(e)}")
    
    async def cleanup_expired_exports(self, hours: int = 24):
        """清理过期的导出文件"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        expired_exports = []
        
        for export_id, status_data in self._export_status.items():
            created_at = status_data.get("created_at")
            if created_at and created_at < cutoff_time:
                expired_exports.append(export_id)
        
        for export_id in expired_exports:
            try:
                # 删除文件
                export_dir = self.exports_dir / export_id
                if export_dir.exists():
                    import shutil
                    shutil.rmtree(export_dir)
                
                # 删除状态记录
                del self._export_status[export_id]
                logger.info(f"清理过期导出: {export_id}")
                
            except Exception as e:
                logger.error(f"清理导出失败: {export_id}, 错误: {str(e)}")
        
        return len(expired_exports)
    
    def get_available_formats(self) -> List[ExportTemplate]:
        """获取可用的导出格式"""
        formats = [
            ExportTemplate(
                name="markdown",
                display_name="Markdown",
                description="轻量级标记语言格式",
                file_extension=".md",
                mime_type="text/markdown"
            ),
            ExportTemplate(
                name="html",
                display_name="HTML",
                description="网页格式，支持样式和交互",
                file_extension=".html",
                mime_type="text/html"
            ),
            ExportTemplate(
                name="txt",
                display_name="纯文本",
                description="纯文本格式，兼容性最好",
                file_extension=".txt",
                mime_type="text/plain"
            ),
            ExportTemplate(
                name="pdf",
                display_name="PDF",
                description="便携文档格式，适合打印和分享",
                file_extension=".pdf",
                mime_type="application/pdf"
            ),
            ExportTemplate(
                name="zip",
                display_name="ZIP压缩包",
                description="包含所有格式的压缩包",
                file_extension=".zip",
                mime_type="application/zip"
            )
        ]
        return formats
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """获取可用的导出模板"""
        templates = [
            {
                "name": "standard",
                "display_name": "标准模板",
                "description": "包含完整内容的标准格式"
            },
            {
                "name": "minimal",
                "display_name": "简洁模板", 
                "description": "简化版本，只包含主要内容"
            },
            {
                "name": "detailed",
                "display_name": "详细模板",
                "description": "包含所有细节和元数据的完整版本"
            }
        ]
        return templates


# 全局导出服务实例
export_service = ExportService() 