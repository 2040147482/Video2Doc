from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置设置"""
    
    # 应用基础配置
    app_name: str = "Video2Doc API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 跨域配置
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # 数据库配置
    database_url: str = "sqlite:///./video2doc.db"
    redis_url: str = "redis://localhost:6379"
    
    # 文件上传配置
    max_file_size: int = 2 * 1024 * 1024 * 1024  # 2GB
    upload_folder: str = "./uploads"
    temp_folder: str = "./temp"
    
    # AI服务配置
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    deepgram_api_key: str = ""
    
    # 腾讯云配置
    tencent_secret_id: str = ""
    tencent_secret_key: str = ""
    
    # 文件存储配置
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_bucket_name: str = ""
    aws_region: str = "us-east-1"
    
    # Supabase配置
    supabase_url: str = ""
    supabase_anon_key: str = ""
    
    # Celery配置
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # FFmpeg配置
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"
    
    # JWT配置
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """获取应用配置单例"""
    return Settings()


# 全局配置实例
settings = get_settings() 