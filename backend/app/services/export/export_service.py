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
        status_data["completed_at"] = datetime.now()
        
        logger.info(f"导出任务已取消: {export_id}")
        return True
    
    async def _process_export(self, export_id: str, result_data: Dict[str, Any]):
        """处理导出任务"""
        try:
            status_data = self._export_status[export_id]
            task_id = status_data["task_id"]
            
            # 更新状态为处理中
            status_data["status"] = "processing"
            status_data["message"] = "正在导出文件"
            
            formats = status_data["formats"]
            total_formats = len(formats)
            completed_formats = []
            download_urls = {}
            
            for i, format_enum in enumerate(formats):
                if status_data["status"] == "cancelled":
                    break
                
                try:
                    # 获取导出器类
                    exporter_class = self._exporters.get(format_enum)
                    if not exporter_class:
                        logger.error(f"不支持的导出格式: {format_enum}")
                        continue
                    
                    # 更新进度
                    progress = (i / total_formats) * 100
                    status_data["progress"] = progress
                    status_data["message"] = f"正在导出 {format_enum.value} 格式"
                    
                    # 创建导出器实例
                    exporter = exporter_class(self.exports_dir)
                    
                    # 执行导出
                    output_path = await exporter.export(
                        task_id=task_id,
                        content_data=result_data,
                        template=status_data["template"],
                        include_images=status_data["include_images"],
                        include_timestamps=status_data["include_timestamps"],
                        include_metadata=status_data["include_metadata"],
                        custom_filename=status_data["custom_filename"]
                    )
                    
                    # 生成下载URL
                    download_url = f"/api/export/download/{export_id}/{output_path.name}"
                    download_urls[format_enum.value] = download_url
                    completed_formats.append(format_enum)
                    
                    logger.info(f"导出格式完成 {format_enum.value}: {output_path}")
                    
                except Exception as e:
                    logger.error(f"导出格式失败 {format_enum.value}: {str(e)}")
                    continue
            
            # 更新最终状态
            if status_data["status"] != "cancelled":
                if completed_formats:
                    status_data["status"] = "completed"
                    status_data["message"] = f"导出完成，生成了 {len(completed_formats)} 种格式"
                    status_data["progress"] = 100.0
                    status_data["formats_completed"] = completed_formats
                    status_data["download_urls"] = download_urls
                    status_data["completed_at"] = datetime.now()
                else:
                    status_data["status"] = "failed"
                    status_data["message"] = "所有格式导出失败"
                    status_data["error_details"] = "无法生成任何格式的文件"
            
        except Exception as e:
            logger.error(f"导出任务处理失败 {export_id}: {str(e)}")
            status_data["status"] = "failed"
            status_data["message"] = "导出任务处理失败"
            status_data["error_details"] = str(e)
            status_data["completed_at"] = datetime.now()
    
    def get_export_file_path(self, export_id: str, filename: str) -> Optional[Path]:
        """获取导出文件路径"""
        status_data = self._export_status.get(export_id)
        if not status_data:
            return None
        
        file_path = self.exports_dir / filename
        if file_path.exists():
            return file_path
        
        return None
    
    async def cleanup_expired_exports(self):
        """清理过期的导出文件"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        expired_exports = []
        
        for export_id, status_data in self._export_status.items():
            created_at = status_data.get("created_at")
            if created_at and created_at < cutoff_time:
                expired_exports.append(export_id)
        
        for export_id in expired_exports:
            try:
                # 删除文件
                status_data = self._export_status[export_id]
                task_id = status_data["task_id"]
                
                # 删除相关文件
                import glob
                for file_path in glob.glob(str(self.exports_dir / f"{task_id}_*")):
                    Path(file_path).unlink(missing_ok=True)
                
                # 删除状态记录
                del self._export_status[export_id]
                logger.info(f"清理过期导出: {export_id}")
                
            except Exception as e:
                logger.error(f"清理过期导出失败 {export_id}: {e}")
    
    def get_supported_formats(self) -> List[OutputFormat]:
        """获取支持的导出格式"""
        return list(self._exporters.keys())
    
    def get_available_templates(self) -> List[ExportTemplate]:
        """获取可用的导出模板"""
        return list(ExportTemplate)


# 全局导出服务实例
export_service = ExportService() 