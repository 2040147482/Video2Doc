"""
增强版文件服务
集成云存储功能，提供更强大的文件管理能力
"""

import os
import uuid
import asyncio
import aiofiles
from pathlib import Path
from typing import Optional, BinaryIO, Dict, Any, List
from fastapi import UploadFile
import hashlib
from datetime import datetime, timedelta
import mimetypes

from app.config import settings
from app.exceptions import FileSizeLimitException, FileTypeException
from app.services.cloud_storage import (
    storage_manager, StorageObject, UploadProgress, CloudStorageBase
)


class EnhancedFileService:
    """增强版文件存储和处理服务"""
    
    def __init__(self):
        self.local_upload_dir = Path(settings.upload_folder)
        self.local_temp_dir = Path(settings.temp_folder)
        
        # 确保本地目录存在
        self.local_upload_dir.mkdir(parents=True, exist_ok=True)
        self.local_temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化云存储
        self._init_cloud_storage()
    
    def _init_cloud_storage(self):
        """初始化云存储配置"""
        try:
            # 从环境变量配置云存储
            storage_manager.from_env()
        except Exception as e:
            # 如果云存储配置失败，使用本地存储作为备份
            storage_manager.register_storage(
                name='local',
                storage_type='local',
                bucket_name='video2doc',
                base_path=str(self.local_upload_dir.parent),
                is_default=True
            )
    
    def get_storage(self, storage_name: Optional[str] = None) -> CloudStorageBase:
        """获取云存储实例"""
        return storage_manager.get_storage(storage_name)
    
    async def upload_file(
        self,
        file: UploadFile,
        task_id: str,
        storage_name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        上传文件到云存储
        
        Args:
            file: FastAPI UploadFile对象
            task_id: 任务ID
            storage_name: 存储实例名称
            metadata: 自定义元数据
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 文件信息
        """
        if not file.filename:
            raise ValueError("文件名不能为空")
        
        # 验证文件
        await self._validate_file(file)
        
        # 生成云存储键
        storage_key = self._generate_storage_key(file.filename, task_id)
        
        # 准备元数据
        file_metadata = {
            'task_id': task_id,
            'original_filename': file.filename,
            'uploaded_at': datetime.utcnow().isoformat(),
            'content_type': file.content_type or 'application/octet-stream'
        }
        
        if metadata:
            file_metadata.update(metadata)
        
        # 获取云存储实例
        storage = self.get_storage(storage_name)
        
        # 上传到云存储
        storage_object = await storage.upload_file(
            file_path=file.file,
            key=storage_key,
            content_type=file.content_type,
            metadata=file_metadata,
            progress_callback=progress_callback
        )
        
        return {
            'storage_key': storage_object.key,
            'original_filename': file.filename,
            'size': storage_object.size,
            'content_type': storage_object.content_type,
            'etag': storage_object.etag,
            'uploaded_at': storage_object.last_modified.isoformat(),
            'metadata': storage_object.metadata,
            'storage_type': type(storage).__name__
        }
    
    async def download_file(
        self,
        storage_key: str,
        local_path: Optional[Path] = None,
        storage_name: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> Path:
        """
        从云存储下载文件
        
        Args:
            storage_key: 存储对象键
            local_path: 本地保存路径
            storage_name: 存储实例名称
            progress_callback: 进度回调函数
            
        Returns:
            Path: 下载后的本地文件路径
        """
        storage = self.get_storage(storage_name)
        
        if not local_path:
            # 生成临时文件路径
            local_path = self.local_temp_dir / f"download_{uuid.uuid4().hex}_{Path(storage_key).name}"
        
        return await storage.download_file(
            key=storage_key,
            local_path=local_path,
            progress_callback=progress_callback
        )
    
    async def delete_file(
        self,
        storage_key: str,
        storage_name: Optional[str] = None
    ) -> bool:
        """
        删除云存储中的文件
        
        Args:
            storage_key: 存储对象键
            storage_name: 存储实例名称
            
        Returns:
            bool: 删除是否成功
        """
        storage = self.get_storage(storage_name)
        return await storage.delete_file(storage_key)
    
    async def get_file_info(
        self,
        storage_key: str,
        storage_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            storage_key: 存储对象键
            storage_name: 存储实例名称
            
        Returns:
            Optional[Dict]: 文件信息
        """
        storage = self.get_storage(storage_name)
        storage_object = await storage.get_file_info(storage_key)
        
        if not storage_object:
            return None
        
        return {
            'key': storage_object.key,
            'size': storage_object.size,
            'last_modified': storage_object.last_modified.isoformat(),
            'etag': storage_object.etag,
            'content_type': storage_object.content_type,
            'metadata': storage_object.metadata
        }
    
    async def list_files(
        self,
        prefix: str = "",
        limit: int = 100,
        storage_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        列出云存储中的文件
        
        Args:
            prefix: 对象键前缀
            limit: 最大返回数量
            storage_name: 存储实例名称
            
        Returns:
            List[Dict]: 文件列表
        """
        storage = self.get_storage(storage_name)
        storage_objects = await storage.list_files(prefix=prefix, limit=limit)
        
        return [
            {
                'key': obj.key,
                'size': obj.size,
                'last_modified': obj.last_modified.isoformat(),
                'etag': obj.etag,
                'content_type': obj.content_type,
                'metadata': obj.metadata
            }
            for obj in storage_objects
        ]
    
    async def generate_download_url(
        self,
        storage_key: str,
        expires_in: int = 3600,
        storage_name: Optional[str] = None
    ) -> str:
        """
        生成文件下载URL
        
        Args:
            storage_key: 存储对象键
            expires_in: 过期时间（秒）
            storage_name: 存储实例名称
            
        Returns:
            str: 下载URL
        """
        storage = self.get_storage(storage_name)
        return await storage.generate_presigned_url(
            key=storage_key,
            operation='get',
            expires_in=expires_in
        )
    
    async def generate_upload_url(
        self,
        storage_key: str,
        expires_in: int = 3600,
        storage_name: Optional[str] = None
    ) -> str:
        """
        生成文件上传URL
        
        Args:
            storage_key: 存储对象键
            expires_in: 过期时间（秒）
            storage_name: 存储实例名称
            
        Returns:
            str: 上传URL
        """
        storage = self.get_storage(storage_name)
        return await storage.generate_presigned_url(
            key=storage_key,
            operation='put',
            expires_in=expires_in
        )
    
    async def copy_file(
        self,
        source_key: str,
        dest_key: str,
        storage_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        复制文件
        
        Args:
            source_key: 源对象键
            dest_key: 目标对象键
            storage_name: 存储实例名称
            
        Returns:
            Dict: 复制后的文件信息
        """
        storage = self.get_storage(storage_name)
        storage_object = await storage.copy_file(source_key, dest_key)
        
        return {
            'key': storage_object.key,
            'size': storage_object.size,
            'last_modified': storage_object.last_modified.isoformat(),
            'etag': storage_object.etag,
            'content_type': storage_object.content_type,
            'metadata': storage_object.metadata
        }
    
    async def cleanup_expired_files(
        self,
        max_age_days: int = 7,
        storage_name: Optional[str] = None
    ) -> int:
        """
        清理过期文件
        
        Args:
            max_age_days: 最大保存天数
            storage_name: 存储实例名称
            
        Returns:
            int: 清理的文件数量
        """
        storage = self.get_storage(storage_name)
        
        # 获取所有文件
        all_files = await storage.list_files(limit=10000)
        
        # 计算过期时间
        expire_time = datetime.utcnow() - timedelta(days=max_age_days)
        
        # 清理过期文件
        deleted_count = 0
        for file_obj in all_files:
            if file_obj.last_modified < expire_time:
                try:
                    if await storage.delete_file(file_obj.key):
                        deleted_count += 1
                except Exception:
                    continue  # 忽略删除失败的文件
        
        return deleted_count
    
    def _generate_storage_key(self, original_filename: str, task_id: str) -> str:
        """生成云存储对象键"""
        file_ext = Path(original_filename).suffix.lower()
        date_dir = datetime.now().strftime("%Y/%m/%d")
        safe_filename = f"{task_id}{file_ext}"
        return f"uploads/{date_dir}/{safe_filename}"
    
    async def _validate_file(self, file: UploadFile) -> None:
        """验证上传文件"""
        if not file.filename:
            raise ValueError("文件名不能为空")
        
        # 检查文件类型
        file_ext = Path(file.filename).suffix.lower()
        supported_formats = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv'}
        
        if file_ext not in supported_formats:
            raise FileTypeException(f"不支持的文件格式: {file_ext}")
        
        # 检查文件大小（如果可以获取）
        if hasattr(file, 'size') and file.size:
            if file.size > settings.max_file_size:
                raise FileSizeLimitException(
                    f"文件大小 {file.size} 字节超过限制 {settings.max_file_size} 字节"
                )
    
    async def backup_to_cloud(
        self,
        local_file_path: Path,
        task_id: str,
        backup_storage: str = 'backup'
    ) -> Optional[str]:
        """
        备份本地文件到云存储
        
        Args:
            local_file_path: 本地文件路径
            task_id: 任务ID
            backup_storage: 备份存储名称
            
        Returns:
            Optional[str]: 备份后的存储键
        """
        try:
            # 生成备份键
            backup_key = self._generate_storage_key(local_file_path.name, f"backup_{task_id}")
            
            # 获取备份存储
            storage = self.get_storage(backup_storage)
            
            # 上传文件
            storage_object = await storage.upload_file(
                file_path=local_file_path,
                key=backup_key,
                metadata={
                    'backup_type': 'local_file',
                    'task_id': task_id,
                    'original_path': str(local_file_path),
                    'backup_time': datetime.utcnow().isoformat()
                }
            )
            
            return storage_object.key
        
        except Exception:
            # 备份失败不影响主要功能
            return None
    
    async def get_storage_stats(
        self,
        storage_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取存储统计信息
        
        Args:
            storage_name: 存储实例名称
            
        Returns:
            Dict: 存储统计信息
        """
        storage = self.get_storage(storage_name)
        
        # 获取所有文件
        all_files = await storage.list_files(limit=10000)
        
        total_files = len(all_files)
        total_size = sum(file_obj.size for file_obj in all_files)
        
        # 按文件类型统计
        type_stats = {}
        for file_obj in all_files:
            content_type = file_obj.content_type or 'unknown'
            if content_type not in type_stats:
                type_stats[content_type] = {'count': 0, 'size': 0}
            type_stats[content_type]['count'] += 1
            type_stats[content_type]['size'] += file_obj.size
        
        return {
            'storage_type': type(storage).__name__,
            'total_files': total_files,
            'total_size': total_size,
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'file_types': type_stats,
            'bucket_name': storage.bucket_name
        }


# 全局增强文件服务实例
enhanced_file_service = EnhancedFileService() 