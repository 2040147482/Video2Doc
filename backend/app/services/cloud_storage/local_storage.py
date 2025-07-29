"""
本地文件系统存储适配器
用于开发和测试环境，或者不使用云存储的部署
"""

import os
import shutil
import asyncio
import aiofiles
from typing import Optional, Dict, Any, List, BinaryIO, Union
from pathlib import Path
from datetime import datetime
import hashlib
import urllib.parse

from .base import CloudStorageBase, StorageObject, UploadProgress


class LocalStorage(CloudStorageBase):
    """本地文件系统存储实现"""
    
    def __init__(self, bucket_name: str, base_path: str = "./storage", **kwargs):
        """
        初始化本地存储
        
        Args:
            bucket_name: 存储桶名称（用作子目录）
            base_path: 存储根目录
            **kwargs: 其他配置参数
        """
        super().__init__(bucket_name, **kwargs)
        self.base_path = Path(base_path)
        self.bucket_path = self.base_path / bucket_name
        
        # 创建存储目录
        self.bucket_path.mkdir(parents=True, exist_ok=True)
    
    def _get_full_path(self, key: str) -> Path:
        """获取文件的完整本地路径"""
        key = self._format_key(key)
        return self.bucket_path / key
    
    async def upload_file(
        self,
        file_path: Union[str, Path, BinaryIO],
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        progress_callback: Optional[callable] = None
    ) -> StorageObject:
        """上传文件到本地存储"""
        key = self._format_key(key)
        dest_path = self._get_full_path(key)
        
        # 确保目标目录存在
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 处理不同类型的文件输入
        if isinstance(file_path, (str, Path)):
            source_path = Path(file_path)
            if not source_path.exists():
                raise FileNotFoundError(f"源文件不存在: {file_path}")
            
            # 异步复制文件
            total_size = source_path.stat().st_size
            bytes_copied = 0
            
            async with aiofiles.open(source_path, 'rb') as src, \
                       aiofiles.open(dest_path, 'wb') as dst:
                
                while True:
                    chunk = await src.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    
                    await dst.write(chunk)
                    bytes_copied += len(chunk)
                    
                    # 调用进度回调
                    if progress_callback:
                        progress = UploadProgress(
                            bytes_transferred=bytes_copied,
                            total_bytes=total_size,
                            percentage=(bytes_copied / total_size) * 100,
                            speed=0  # 本地复制速度很快，不计算
                        )
                        await asyncio.create_task(
                            asyncio.to_thread(progress_callback, progress)
                        )
        
        elif hasattr(file_path, 'read'):
            # 处理文件对象
            async with aiofiles.open(dest_path, 'wb') as dst:
                # 如果是异步文件对象
                if hasattr(file_path, 'read') and asyncio.iscoroutinefunction(file_path.read):
                    while True:
                        chunk = await file_path.read(8192)
                        if not chunk:
                            break
                        await dst.write(chunk)
                else:
                    # 同步文件对象
                    while True:
                        chunk = file_path.read(8192)
                        if not chunk:
                            break
                        await dst.write(chunk)
        
        else:
            raise ValueError(f"不支持的文件输入类型: {type(file_path)}")
        
        # 获取文件信息
        stat = dest_path.stat()
        
        # 计算ETag（使用文件内容的MD5）
        etag = await self._calculate_etag(dest_path)
        
        # 确定content_type
        if not content_type:
            content_type = self._get_content_type(dest_path)
        
        # 保存元数据（如果提供）
        if metadata:
            await self._save_metadata(key, metadata)
        
        return StorageObject(
            key=key,
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            etag=etag,
            content_type=content_type,
            metadata=metadata or {}
        )
    
    async def download_file(
        self,
        key: str,
        local_path: Union[str, Path],
        progress_callback: Optional[callable] = None
    ) -> Path:
        """从本地存储下载文件"""
        source_path = self._get_full_path(key)
        dest_path = Path(local_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"文件不存在: {key}")
        
        # 确保目标目录存在
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 异步复制文件
        total_size = source_path.stat().st_size
        bytes_copied = 0
        
        async with aiofiles.open(source_path, 'rb') as src, \
                   aiofiles.open(dest_path, 'wb') as dst:
            
            while True:
                chunk = await src.read(8192)
                if not chunk:
                    break
                
                await dst.write(chunk)
                bytes_copied += len(chunk)
                
                # 调用进度回调
                if progress_callback:
                    progress = UploadProgress(
                        bytes_transferred=bytes_copied,
                        total_bytes=total_size,
                        percentage=(bytes_copied / total_size) * 100,
                        speed=0
                    )
                    await asyncio.create_task(
                        asyncio.to_thread(progress_callback, progress)
                    )
        
        return dest_path
    
    async def delete_file(self, key: str) -> bool:
        """删除本地存储中的文件"""
        file_path = self._get_full_path(key)
        
        try:
            if file_path.exists():
                file_path.unlink()
                
                # 同时删除元数据文件
                metadata_path = self._get_metadata_path(key)
                if metadata_path.exists():
                    metadata_path.unlink()
                
                return True
            return False
        except Exception:
            return False
    
    async def list_files(
        self,
        prefix: str = "",
        limit: int = 1000
    ) -> List[StorageObject]:
        """列出本地存储中的文件"""
        prefix = self._format_key(prefix) if prefix else ""
        prefix_path = self.bucket_path / prefix if prefix else self.bucket_path
        
        files = []
        count = 0
        
        # 遍历目录
        for root, dirs, filenames in os.walk(self.bucket_path):
            if count >= limit:
                break
            
            root_path = Path(root)
            
            for filename in filenames:
                if count >= limit:
                    break
                
                # 跳过元数据文件
                if filename.endswith('.metadata'):
                    continue
                
                file_path = root_path / filename
                relative_path = file_path.relative_to(self.bucket_path)
                key = str(relative_path).replace('\\', '/')
                
                # 检查前缀匹配
                if prefix and not key.startswith(prefix):
                    continue
                
                try:
                    stat = file_path.stat()
                    etag = await self._calculate_etag(file_path)
                    content_type = self._get_content_type(file_path)
                    metadata = await self._load_metadata(key)
                    
                    files.append(StorageObject(
                        key=key,
                        size=stat.st_size,
                        last_modified=datetime.fromtimestamp(stat.st_mtime),
                        etag=etag,
                        content_type=content_type,
                        metadata=metadata
                    ))
                    
                    count += 1
                
                except Exception:
                    continue
        
        return files
    
    async def get_file_info(self, key: str) -> Optional[StorageObject]:
        """获取文件信息"""
        file_path = self._get_full_path(key)
        
        if not file_path.exists():
            return None
        
        try:
            stat = file_path.stat()
            etag = await self._calculate_etag(file_path)
            content_type = self._get_content_type(file_path)
            metadata = await self._load_metadata(key)
            
            return StorageObject(
                key=key,
                size=stat.st_size,
                last_modified=datetime.fromtimestamp(stat.st_mtime),
                etag=etag,
                content_type=content_type,
                metadata=metadata
            )
        
        except Exception:
            return None
    
    async def generate_presigned_url(
        self,
        key: str,
        operation: str = "get",
        expires_in: int = 3600
    ) -> str:
        """生成预签名URL（本地存储返回文件路径）"""
        file_path = self._get_full_path(key)
        
        if operation == "get" and not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {key}")
        
        # 对于本地存储，返回file:// URL
        return f"file://{file_path.absolute()}"
    
    async def copy_file(self, source_key: str, dest_key: str) -> StorageObject:
        """复制文件"""
        source_path = self._get_full_path(source_key)
        dest_path = self._get_full_path(dest_key)
        
        if not source_path.exists():
            raise FileNotFoundError(f"源文件不存在: {source_key}")
        
        # 确保目标目录存在
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 复制文件
        shutil.copy2(source_path, dest_path)
        
        # 复制元数据
        source_metadata = await self._load_metadata(source_key)
        if source_metadata:
            await self._save_metadata(dest_key, source_metadata)
        
        # 返回目标文件信息
        return await self.get_file_info(dest_key)
    
    def _get_metadata_path(self, key: str) -> Path:
        """获取元数据文件路径"""
        file_path = self._get_full_path(key)
        return file_path.with_suffix(file_path.suffix + '.metadata')
    
    async def _save_metadata(self, key: str, metadata: Dict[str, str]):
        """保存文件元数据"""
        metadata_path = self._get_metadata_path(key)
        
        try:
            import json
            async with aiofiles.open(metadata_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(metadata, ensure_ascii=False, indent=2))
        except Exception:
            pass  # 元数据保存失败不影响主要功能
    
    async def _load_metadata(self, key: str) -> Dict[str, str]:
        """加载文件元数据"""
        metadata_path = self._get_metadata_path(key)
        
        if not metadata_path.exists():
            return {}
        
        try:
            import json
            async with aiofiles.open(metadata_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception:
            return {}
    
    async def _calculate_etag(self, file_path: Path) -> str:
        """计算文件的ETag（MD5哈希）"""
        hash_md5 = hashlib.md5()
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest() 