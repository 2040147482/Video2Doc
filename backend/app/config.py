from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os
from pydantic import Field


class Settings(BaseSettings):
    # 应用基本配置
    app_name: str = "Video2Doc API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS配置
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # 数据库配置
    database_url: str = "postgresql://user:password@localhost/video2doc"
    redis_url: str = "redis://localhost:6379"
    
    # 文件存储配置
    upload_folder: str = "uploads"
    temp_folder: str = "temp"
    results_folder: str = "results"
    max_file_size: int = 2 * 1024 * 1024 * 1024  # 2GB
    max_audio_size_mb: int = 500  # 500MB
    
    # AI服务API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    perplexity_api_key: str = ""
    
    # Creem支付平台配置
    creem_api_key: str = Field(default="", description="Creem API密钥")
    creem_webhook_secret: str = Field(default="", description="Creem Webhook密钥")
    
    # 云存储配置（可选）
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = ""
    
    # Celery配置
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # FFmpeg路径
    ffmpeg_path: str = "ffmpeg"
    
    # 日志配置
    log_level: str = "INFO"
    
    # 目录路径属性
    @property
    def upload_dir(self) -> str:
        """上传文件目录路径"""
        return os.path.abspath(self.upload_folder)
    
    @property
    def temp_dir(self) -> str:
        """临时文件目录路径"""
        return os.path.abspath(self.temp_folder)
    
    @property
    def results_dir(self) -> str:
        """结果文件目录路径"""
        return os.path.abspath(self.results_folder)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


# 全局配置实例
settings = get_settings() 