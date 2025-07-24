import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, BinaryIO
from fastapi import UploadFile
import hashlib
from datetime import datetime

from app.config import settings
from app.exceptions import FileSizeExceededError, UnsupportedFileFormatError


class FileService:
    """文件存储和处理服务"""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_folder)
        self.temp_dir = Path(settings.temp_folder)
        
        # 确保目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_file_path(self, original_filename: str, task_id: str) -> Path:
        """生成安全的文件存储路径"""
        # 提取文件扩展名
        file_ext = Path(original_filename).suffix.lower()
        
        # 生成安全的文件名：任务ID + 扩展名
        safe_filename = f"{task_id}{file_ext}"
        
        # 按日期分目录存储
        date_dir = datetime.now().strftime("%Y%m%d")
        file_path = self.upload_dir / date_dir / safe_filename
        
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        return file_path
    
    async def save_upload_file(self, file: UploadFile, task_id: str) -> tuple[Path, dict]:
        """
        保存上传的文件
        
        Args:
            file: FastAPI UploadFile对象
            task_id: 任务ID
            
        Returns:
            tuple: (文件路径, 文件信息)
        """
        if not file.filename:
            raise ValueError("文件名不能为空")
        
        # 生成文件路径
        file_path = self.generate_file_path(file.filename, task_id)
        
        # 初始化文件信息
        file_info = {
            "original_name": file.filename,
            "size": 0,
            "content_type": file.content_type,
            "md5": hashlib.md5(),
            "saved_path": str(file_path)
        }
        
        # 异步保存文件并计算MD5
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):  # 8KB chunks
                file_info["size"] += len(chunk)
                file_info["md5"].update(chunk)
                
                # 检查文件大小限制
                if file_info["size"] > settings.max_file_size:
                    # 删除已保存的不完整文件
                    if file_path.exists():
                        file_path.unlink()
                    raise FileSizeExceededError(file_info["size"], settings.max_file_size)
                
                await f.write(chunk)
        
        # 完成MD5计算
        file_info["md5"] = file_info["md5"].hexdigest()
        
        return file_path, file_info
    
    def validate_file_format(self, filename: str, supported_formats: set) -> None:
        """验证文件格式"""
        file_ext = Path(filename).suffix.lower()
        if file_ext not in supported_formats:
            raise UnsupportedFileFormatError(file_ext)
    
    def get_file_info(self, file_path: Path) -> dict:
        """获取文件基本信息"""
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        stat = file_path.stat()
        return {
            "size": stat.st_size,
            "created_time": datetime.fromtimestamp(stat.st_ctime),
            "modified_time": datetime.fromtimestamp(stat.st_mtime),
            "extension": file_path.suffix.lower(),
            "name": file_path.name
        }
    
    async def delete_file(self, file_path: Path) -> bool:
        """删除文件"""
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False
    
    def cleanup_temp_files(self, older_than_hours: int = 24) -> int:
        """清理临时文件"""
        cleaned_count = 0
        cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
        
        try:
            for file_path in self.temp_dir.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
        except Exception as e:
            print(f"清理临时文件时出错: {e}")
        
        return cleaned_count


# 全局文件服务实例
file_service = FileService() 