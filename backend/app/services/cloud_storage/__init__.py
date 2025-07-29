"""
云存储服务模块
提供统一的云存储接口和多种存储后端支持
"""

import os
from typing import Optional, Dict, Any, Union
from enum import Enum

from .base import CloudStorageBase, StorageObject, UploadProgress
from .local_storage import LocalStorage

# 可选的云存储实现
try:
    from .s3_storage import S3Storage
    S3_AVAILABLE = True
except ImportError:
    S3Storage = None
    S3_AVAILABLE = False


class StorageType(str, Enum):
    """存储类型枚举"""
    LOCAL = "local"
    S3 = "s3"
    # 未来可以添加更多类型
    # AZURE = "azure"
    # GCS = "gcs"
    # SUPABASE = "supabase"


class StorageFactory:
    """云存储工厂类"""
    
    @staticmethod
    def create_storage(
        storage_type: Union[str, StorageType],
        bucket_name: str,
        **config
    ) -> CloudStorageBase:
        """
        创建云存储实例
        
        Args:
            storage_type: 存储类型
            bucket_name: 存储桶名称
            **config: 存储配置参数
            
        Returns:
            CloudStorageBase: 云存储实例
        """
        if isinstance(storage_type, str):
            storage_type = StorageType(storage_type.lower())
        
        if storage_type == StorageType.LOCAL:
            return LocalStorage(
                bucket_name=bucket_name,
                base_path=config.get('base_path', './storage'),
                **{k: v for k, v in config.items() if k != 'base_path'}
            )
        
        elif storage_type == StorageType.S3:
            if not S3_AVAILABLE:
                raise ImportError(
                    "S3 storage is not available. Install aioboto3: pip install aioboto3"
                )
            
            return S3Storage(
                bucket_name=bucket_name,
                region=config.get('region', 'us-east-1'),
                aws_access_key_id=config.get('aws_access_key_id'),
                aws_secret_access_key=config.get('aws_secret_access_key'),
                endpoint_url=config.get('endpoint_url'),
                **{k: v for k, v in config.items() 
                   if k not in ['region', 'aws_access_key_id', 'aws_secret_access_key', 'endpoint_url']}
            )
        
        else:
            raise ValueError(f"不支持的存储类型: {storage_type}")


class StorageManager:
    """云存储管理器"""
    
    def __init__(self):
        self._instances: Dict[str, CloudStorageBase] = {}
        self._default_instance: Optional[CloudStorageBase] = None
    
    def register_storage(
        self,
        name: str,
        storage_type: Union[str, StorageType],
        bucket_name: str,
        is_default: bool = False,
        **config
    ) -> CloudStorageBase:
        """
        注册云存储实例
        
        Args:
            name: 存储实例名称
            storage_type: 存储类型
            bucket_name: 存储桶名称
            is_default: 是否设为默认存储
            **config: 存储配置参数
            
        Returns:
            CloudStorageBase: 云存储实例
        """
        storage = StorageFactory.create_storage(
            storage_type=storage_type,
            bucket_name=bucket_name,
            **config
        )
        
        self._instances[name] = storage
        
        if is_default or not self._default_instance:
            self._default_instance = storage
        
        return storage
    
    def get_storage(self, name: Optional[str] = None) -> CloudStorageBase:
        """
        获取云存储实例
        
        Args:
            name: 存储实例名称，None则返回默认实例
            
        Returns:
            CloudStorageBase: 云存储实例
        """
        if name is None:
            if self._default_instance is None:
                raise ValueError("未设置默认云存储实例")
            return self._default_instance
        
        if name not in self._instances:
            raise ValueError(f"未找到云存储实例: {name}")
        
        return self._instances[name]
    
    def set_default(self, name: str):
        """
        设置默认云存储实例
        
        Args:
            name: 存储实例名称
        """
        if name not in self._instances:
            raise ValueError(f"未找到云存储实例: {name}")
        
        self._default_instance = self._instances[name]
    
    def remove_storage(self, name: str):
        """
        移除云存储实例
        
        Args:
            name: 存储实例名称
        """
        if name in self._instances:
            if self._instances[name] == self._default_instance:
                self._default_instance = None
            del self._instances[name]
    
    def list_storages(self) -> Dict[str, str]:
        """
        列出所有已注册的存储实例
        
        Returns:
            Dict[str, str]: {名称: 类型} 的映射
        """
        return {
            name: type(storage).__name__
            for name, storage in self._instances.items()
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'StorageManager':
        """
        从配置创建存储管理器
        
        Args:
            config: 存储配置，格式如下:
            {
                "default": "local",
                "storages": {
                    "local": {
                        "type": "local",
                        "bucket_name": "video2doc",
                        "base_path": "./storage"
                    },
                    "s3": {
                        "type": "s3",
                        "bucket_name": "video2doc-bucket",
                        "region": "us-east-1",
                        "aws_access_key_id": "...",
                        "aws_secret_access_key": "..."
                    }
                }
            }
            
        Returns:
            StorageManager: 配置好的存储管理器
        """
        manager = cls()
        
        storages_config = config.get('storages', {})
        default_name = config.get('default')
        
        for name, storage_config in storages_config.items():
            storage_type = storage_config.pop('type')
            is_default = (name == default_name)
            
            manager.register_storage(
                name=name,
                storage_type=storage_type,
                is_default=is_default,
                **storage_config
            )
        
        return manager
    
    @classmethod
    def from_env(cls) -> 'StorageManager':
        """
        从环境变量创建存储管理器
        
        环境变量:
        - STORAGE_TYPE: 存储类型 (local/s3)
        - STORAGE_BUCKET: 存储桶名称
        - STORAGE_BASE_PATH: 本地存储路径
        - AWS_ACCESS_KEY_ID: AWS访问密钥ID
        - AWS_SECRET_ACCESS_KEY: AWS访问密钥
        - AWS_REGION: AWS区域
        - AWS_ENDPOINT_URL: 自定义S3端点
        
        Returns:
            StorageManager: 配置好的存储管理器
        """
        manager = cls()
        
        storage_type = os.getenv('STORAGE_TYPE', 'local').lower()
        bucket_name = os.getenv('STORAGE_BUCKET', 'video2doc')
        
        config = {}
        
        if storage_type == 'local':
            config['base_path'] = os.getenv('STORAGE_BASE_PATH', './storage')
        
        elif storage_type == 's3':
            config.update({
                'region': os.getenv('AWS_REGION', 'us-east-1'),
                'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
                'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
                'endpoint_url': os.getenv('AWS_ENDPOINT_URL'),
            })
        
        manager.register_storage(
            name='default',
            storage_type=storage_type,
            bucket_name=bucket_name,
            is_default=True,
            **config
        )
        
        return manager


# 全局存储管理器实例
storage_manager = StorageManager()

# 导出主要类和实例
__all__ = [
    'CloudStorageBase',
    'StorageObject', 
    'UploadProgress',
    'StorageType',
    'StorageFactory',
    'StorageManager',
    'LocalStorage',
    'S3Storage',
    'storage_manager'
] 