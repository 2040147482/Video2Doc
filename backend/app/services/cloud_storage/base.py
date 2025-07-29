"""
云存储抽象基类
定义统一的存储接口，支持多种云存储提供商
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, BinaryIO, Union
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio


@dataclass
class StorageObject:
    """存储对象信息"""
    key: str  # 对象键/路径
    size: int  # 文件大小（字节）
    last_modified: datetime  # 最后修改时间
    etag: str  # ETag标识
    content_type: str  # MIME类型
    metadata: Dict[str, str]  # 自定义元数据


@dataclass
class UploadProgress:
    """上传进度信息"""
    bytes_transferred: int  # 已传输字节数
    total_bytes: int  # 总字节数
    percentage: float  # 完成百分比
    speed: float  # 传输速度（字节/秒）


class CloudStorageBase(ABC):
    """云存储抽象基类"""
    
    def __init__(self, bucket_name: str, region: str = None, **kwargs):
        """
        初始化云存储客户端
        
        Args:
            bucket_name: 存储桶名称
            region: 区域
            **kwargs: 其他配置参数
        """
        self.bucket_name = bucket_name
        self.region = region
        self.config = kwargs
    
    @abstractmethod
    async def upload_file(
        self,
        file_path: Union[str, Path, BinaryIO],
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        progress_callback: Optional[callable] = None
    ) -> StorageObject:
        """
        上传文件到云存储
        
        Args:
            file_path: 本地文件路径或文件对象
            key: 存储对象键
            content_type: MIME类型
            metadata: 自定义元数据
            progress_callback: 进度回调函数
            
        Returns:
            StorageObject: 上传后的对象信息
        """
        pass
    
    @abstractmethod
    async def download_file(
        self,
        key: str,
        local_path: Union[str, Path],
        progress_callback: Optional[callable] = None
    ) -> Path:
        """
        从云存储下载文件
        
        Args:
            key: 存储对象键
            local_path: 本地保存路径
            progress_callback: 进度回调函数
            
        Returns:
            Path: 下载后的本地文件路径
        """
        pass
    
    @abstractmethod
    async def delete_file(self, key: str) -> bool:
        """
        删除云存储中的文件
        
        Args:
            key: 存储对象键
            
        Returns:
            bool: 删除是否成功
        """
        pass
    
    @abstractmethod
    async def list_files(
        self,
        prefix: str = "",
        limit: int = 1000
    ) -> List[StorageObject]:
        """
        列出云存储中的文件
        
        Args:
            prefix: 对象键前缀
            limit: 最大返回数量
            
        Returns:
            List[StorageObject]: 文件对象列表
        """
        pass
    
    @abstractmethod
    async def get_file_info(self, key: str) -> Optional[StorageObject]:
        """
        获取文件信息
        
        Args:
            key: 存储对象键
            
        Returns:
            Optional[StorageObject]: 文件对象信息
        """
        pass
    
    @abstractmethod
    async def generate_presigned_url(
        self,
        key: str,
        operation: str = "get",
        expires_in: int = 3600
    ) -> str:
        """
        生成预签名URL
        
        Args:
            key: 存储对象键
            operation: 操作类型 (get/put)
            expires_in: 过期时间（秒）
            
        Returns:
            str: 预签名URL
        """
        pass
    
    @abstractmethod
    async def copy_file(self, source_key: str, dest_key: str) -> StorageObject:
        """
        复制文件
        
        Args:
            source_key: 源对象键
            dest_key: 目标对象键
            
        Returns:
            StorageObject: 复制后的对象信息
        """
        pass
    
    async def file_exists(self, key: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            key: 存储对象键
            
        Returns:
            bool: 文件是否存在
        """
        try:
            info = await self.get_file_info(key)
            return info is not None
        except Exception:
            return False
    
    async def get_file_size(self, key: str) -> Optional[int]:
        """
        获取文件大小
        
        Args:
            key: 存储对象键
            
        Returns:
            Optional[int]: 文件大小（字节）
        """
        try:
            info = await self.get_file_info(key)
            return info.size if info else None
        except Exception:
            return None
    
    def _format_key(self, key: str) -> str:
        """
        格式化对象键，确保符合云存储规范
        
        Args:
            key: 原始键
            
        Returns:
            str: 格式化后的键
        """
        # 移除开头的斜杠
        key = key.lstrip('/')
        
        # 替换连续的斜杠
        while '//' in key:
            key = key.replace('//', '/')
        
        return key
    
    def _get_content_type(self, file_path: Union[str, Path]) -> str:
        """
        根据文件扩展名获取MIME类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: MIME类型
        """
        import mimetypes
        
        if isinstance(file_path, (str, Path)):
            content_type, _ = mimetypes.guess_type(str(file_path))
            return content_type or 'application/octet-stream'
        
        return 'application/octet-stream' 