"""
AWS S3 云存储适配器
支持Amazon S3 和兼容S3的云存储服务
"""

import asyncio
from typing import Optional, Dict, Any, List, BinaryIO, Union
from pathlib import Path
from datetime import datetime
import mimetypes

try:
    import aioboto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    aioboto3 = None
    ClientError = Exception
    NoCredentialsError = Exception
    BOTO3_AVAILABLE = False

from .base import CloudStorageBase, StorageObject, UploadProgress


class S3Storage(CloudStorageBase):
    """AWS S3 存储实现"""
    
    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        **kwargs
    ):
        """
        初始化S3存储
        
        Args:
            bucket_name: S3存储桶名称
            region: AWS区域
            aws_access_key_id: AWS访问密钥ID
            aws_secret_access_key: AWS访问密钥
            endpoint_url: 自定义S3端点（用于兼容S3的服务）
            **kwargs: 其他配置参数
        """
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "aioboto3 is required for S3 storage. "
                "Install it with: pip install aioboto3"
            )
        
        super().__init__(bucket_name, region, **kwargs)
        
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        
        # S3客户端配置
        self.s3_config = {
            'region_name': region,
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
        }
        
        if endpoint_url:
            self.s3_config['endpoint_url'] = endpoint_url
    
    async def _get_s3_client(self):
        """获取S3客户端"""
        session = aioboto3.Session()
        return session.client('s3', **self.s3_config)
    
    async def upload_file(
        self,
        file_path: Union[str, Path, BinaryIO],
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        progress_callback: Optional[callable] = None
    ) -> StorageObject:
        """上传文件到S3"""
        key = self._format_key(key)
        
        # 准备上传参数
        extra_args = {}
        
        if content_type:
            extra_args['ContentType'] = content_type
        elif isinstance(file_path, (str, Path)):
            content_type = self._get_content_type(file_path)
            extra_args['ContentType'] = content_type
        
        if metadata:
            extra_args['Metadata'] = metadata
        
        async with await self._get_s3_client() as s3:
            try:
                # 处理不同类型的文件输入
                if isinstance(file_path, (str, Path)):
                    # 文件路径
                    file_path = Path(file_path)
                    if not file_path.exists():
                        raise FileNotFoundError(f"源文件不存在: {file_path}")
                    
                    # 获取文件大小用于进度计算
                    file_size = file_path.stat().st_size
                    
                    # 创建进度回调包装器
                    def progress_wrapper(bytes_transferred):
                        if progress_callback:
                            progress = UploadProgress(
                                bytes_transferred=bytes_transferred,
                                total_bytes=file_size,
                                percentage=(bytes_transferred / file_size) * 100,
                                speed=0  # boto3不提供速度信息
                            )
                            asyncio.create_task(
                                asyncio.to_thread(progress_callback, progress)
                            )
                    
                    # 上传文件
                    await s3.upload_file(
                        str(file_path),
                        self.bucket_name,
                        key,
                        ExtraArgs=extra_args,
                        Callback=progress_wrapper if progress_callback else None
                    )
                
                elif hasattr(file_path, 'read'):
                    # 文件对象
                    await s3.upload_fileobj(
                        file_path,
                        self.bucket_name,
                        key,
                        ExtraArgs=extra_args
                    )
                
                else:
                    raise ValueError(f"不支持的文件输入类型: {type(file_path)}")
                
                # 获取上传后的对象信息
                response = await s3.head_object(Bucket=self.bucket_name, Key=key)
                
                return StorageObject(
                    key=key,
                    size=response['ContentLength'],
                    last_modified=response['LastModified'],
                    etag=response['ETag'].strip('"'),
                    content_type=response.get('ContentType', 'application/octet-stream'),
                    metadata=response.get('Metadata', {})
                )
            
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchBucket':
                    raise ValueError(f"S3存储桶不存在: {self.bucket_name}")
                elif error_code == 'AccessDenied':
                    raise PermissionError("S3访问被拒绝，请检查凭据和权限")
                else:
                    raise Exception(f"S3上传失败: {e}")
            
            except NoCredentialsError:
                raise ValueError("未找到AWS凭据，请配置访问密钥")
    
    async def download_file(
        self,
        key: str,
        local_path: Union[str, Path],
        progress_callback: Optional[callable] = None
    ) -> Path:
        """从S3下载文件"""
        key = self._format_key(key)
        local_path = Path(local_path)
        
        # 确保目标目录存在
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with await self._get_s3_client() as s3:
            try:
                # 获取文件大小用于进度计算
                response = await s3.head_object(Bucket=self.bucket_name, Key=key)
                file_size = response['ContentLength']
                
                # 创建进度回调包装器
                def progress_wrapper(bytes_transferred):
                    if progress_callback:
                        progress = UploadProgress(
                            bytes_transferred=bytes_transferred,
                            total_bytes=file_size,
                            percentage=(bytes_transferred / file_size) * 100,
                            speed=0
                        )
                        asyncio.create_task(
                            asyncio.to_thread(progress_callback, progress)
                        )
                
                # 下载文件
                await s3.download_file(
                    self.bucket_name,
                    key,
                    str(local_path),
                    Callback=progress_wrapper if progress_callback else None
                )
                
                return local_path
            
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchKey':
                    raise FileNotFoundError(f"S3文件不存在: {key}")
                elif error_code == 'NoSuchBucket':
                    raise ValueError(f"S3存储桶不存在: {self.bucket_name}")
                else:
                    raise Exception(f"S3下载失败: {e}")
    
    async def delete_file(self, key: str) -> bool:
        """删除S3中的文件"""
        key = self._format_key(key)
        
        async with await self._get_s3_client() as s3:
            try:
                await s3.delete_object(Bucket=self.bucket_name, Key=key)
                return True
            
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchKey':
                    return False  # 文件不存在，视为删除成功
                else:
                    return False
    
    async def list_files(
        self,
        prefix: str = "",
        limit: int = 1000
    ) -> List[StorageObject]:
        """列出S3中的文件"""
        prefix = self._format_key(prefix) if prefix else ""
        
        async with await self._get_s3_client() as s3:
            try:
                response = await s3.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix,
                    MaxKeys=min(limit, 1000)  # S3单次最多返回1000个对象
                )
                
                files = []
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        files.append(StorageObject(
                            key=obj['Key'],
                            size=obj['Size'],
                            last_modified=obj['LastModified'],
                            etag=obj['ETag'].strip('"'),
                            content_type='application/octet-stream',  # 需要额外请求获取
                            metadata={}  # 需要额外请求获取
                        ))
                
                return files
            
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchBucket':
                    raise ValueError(f"S3存储桶不存在: {self.bucket_name}")
                else:
                    raise Exception(f"S3列表文件失败: {e}")
    
    async def get_file_info(self, key: str) -> Optional[StorageObject]:
        """获取S3文件信息"""
        key = self._format_key(key)
        
        async with await self._get_s3_client() as s3:
            try:
                response = await s3.head_object(Bucket=self.bucket_name, Key=key)
                
                return StorageObject(
                    key=key,
                    size=response['ContentLength'],
                    last_modified=response['LastModified'],
                    etag=response['ETag'].strip('"'),
                    content_type=response.get('ContentType', 'application/octet-stream'),
                    metadata=response.get('Metadata', {})
                )
            
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchKey':
                    return None
                else:
                    raise Exception(f"S3获取文件信息失败: {e}")
    
    async def generate_presigned_url(
        self,
        key: str,
        operation: str = "get",
        expires_in: int = 3600
    ) -> str:
        """生成S3预签名URL"""
        key = self._format_key(key)
        
        # 映射操作类型
        operation_map = {
            'get': 'get_object',
            'put': 'put_object'
        }
        
        client_method = operation_map.get(operation, 'get_object')
        
        async with await self._get_s3_client() as s3:
            try:
                url = await s3.generate_presigned_url(
                    client_method,
                    Params={'Bucket': self.bucket_name, 'Key': key},
                    ExpiresIn=expires_in
                )
                return url
            
            except ClientError as e:
                raise Exception(f"S3生成预签名URL失败: {e}")
    
    async def copy_file(self, source_key: str, dest_key: str) -> StorageObject:
        """在S3中复制文件"""
        source_key = self._format_key(source_key)
        dest_key = self._format_key(dest_key)
        
        async with await self._get_s3_client() as s3:
            try:
                # 复制对象
                copy_source = {'Bucket': self.bucket_name, 'Key': source_key}
                await s3.copy_object(
                    CopySource=copy_source,
                    Bucket=self.bucket_name,
                    Key=dest_key
                )
                
                # 返回复制后的文件信息
                return await self.get_file_info(dest_key)
            
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchKey':
                    raise FileNotFoundError(f"S3源文件不存在: {source_key}")
                else:
                    raise Exception(f"S3复制文件失败: {e}")
    
    async def create_bucket_if_not_exists(self):
        """如果存储桶不存在则创建"""
        async with await self._get_s3_client() as s3:
            try:
                await s3.head_bucket(Bucket=self.bucket_name)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    # 存储桶不存在，创建它
                    try:
                        if self.region == 'us-east-1':
                            # us-east-1不需要LocationConstraint
                            await s3.create_bucket(Bucket=self.bucket_name)
                        else:
                            await s3.create_bucket(
                                Bucket=self.bucket_name,
                                CreateBucketConfiguration={'LocationConstraint': self.region}
                            )
                    except ClientError as create_error:
                        raise Exception(f"创建S3存储桶失败: {create_error}")
                else:
                    raise Exception(f"检查S3存储桶失败: {e}") 