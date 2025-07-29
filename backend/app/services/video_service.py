import re
import asyncio
import aiohttp
import os
import uuid
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from app.exceptions import VideoUploadException, VideoProcessingException


class VideoService:
    """视频链接处理服务"""
    
    # 支持的视频平台配置
    SUPPORTED_PLATFORMS = {
        "youtube": {
            "domains": ["youtube.com", "youtu.be", "www.youtube.com", "m.youtube.com"],
            "patterns": [
                r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})",
                r"youtube\.com/embed/([a-zA-Z0-9_-]{11})"
            ]
        },
        "bilibili": {
            "domains": ["bilibili.com", "www.bilibili.com", "m.bilibili.com", "b23.tv"],
            "patterns": [
                r"bilibili\.com/video/(BV[a-zA-Z0-9]{10})",
                r"bilibili\.com/video/(av\d+)",
                r"b23\.tv/([a-zA-Z0-9]+)"
            ]
        },
        "vimeo": {
            "domains": ["vimeo.com", "www.vimeo.com"],
            "patterns": [
                r"vimeo\.com/(\d+)"
            ]
        }
    }
    
    # 支持的音频URL正则
    AUDIO_URL_PATTERNS = [
        r"^https?://.*\.(mp3|wav|ogg|m4a|aac|flac)(\?.*)?$",
        r"^https?://.*/(audio|sound)/.*$",
        r"^https?://(soundcloud\.com|audiomack\.com|bandcamp\.com)/.*$"
    ]
    
    def validate_video_url(self, url: str) -> Dict[str, Any]:
        """
        验证视频URL并提取平台信息
        
        Args:
            url: 视频URL
            
        Returns:
            dict: 包含平台、视频ID等信息
            
        Raises:
            VideoUploadException: URL无效或不支持的平台
        """
        if not url or not url.strip():
            raise VideoUploadException("视频链接不能为空")
        
        url = url.strip()
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # 移除 www. 前缀进行匹配
            clean_domain = domain.replace("www.", "")
            
            for platform, config in self.SUPPORTED_PLATFORMS.items():
                # 检查域名
                if any(d in domain for d in config["domains"]):
                    # 尝试提取视频ID
                    for pattern in config["patterns"]:
                        match = re.search(pattern, url, re.IGNORECASE)
                        if match:
                            video_id = match.group(1)
                            return {
                                "platform": platform,
                                "video_id": video_id,
                                "original_url": url,
                                "domain": domain
                            }
            
            # 如果没有匹配到支持的平台
            supported_domains = []
            for config in self.SUPPORTED_PLATFORMS.values():
                supported_domains.extend(config["domains"])
            
            raise VideoUploadException(
                f"暂不支持该视频平台。支持的平台：{', '.join(supported_domains)}"
            )
            
        except Exception as e:
            if isinstance(e, VideoUploadException):
                raise
            raise VideoUploadException(f"URL格式无效: {str(e)}")
    
    async def is_valid_url(self, url: str) -> bool:
        """
        检查URL是否有效
        
        Args:
            url: 需要检查的URL
            
        Returns:
            bool: URL是否有效
        """
        if not url or not url.strip():
            return False
        
        url = url.strip()
        
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return False
                
            # 尝试发送HEAD请求检查URL是否可访问
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.head(url, timeout=10) as response:
                        return response.status < 400
                except:
                    # 如果HEAD请求失败，尝试GET请求
                    try:
                        async with session.get(url, timeout=10) as response:
                            return response.status < 400
                    except:
                        return False
        except:
            return False
    
    async def is_audio_url(self, url: str) -> bool:
        """
        检查URL是否为音频文件
        
        Args:
            url: 需要检查的URL
            
        Returns:
            bool: 是否为音频URL
        """
        if not url or not url.strip():
            return False
        
        url = url.strip()
        
        # 检查URL是否匹配音频模式
        for pattern in self.AUDIO_URL_PATTERNS:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        
        # 检查Content-Type
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=10) as response:
                    content_type = response.headers.get("Content-Type", "")
                    return content_type.startswith("audio/")
        except:
            return False
    
    async def download_audio(self, url: str, temp_dir: str) -> str:
        """
        从URL下载音频文件
        
        Args:
            url: 音频URL
            temp_dir: 临时目录
            
        Returns:
            str: 下载的音频文件路径
        """
        # 确保临时目录存在
        os.makedirs(temp_dir, exist_ok=True)
        
        # 生成唯一文件名
        file_name = f"audio_{uuid.uuid4().hex}"
        file_ext = ".mp3"  # 默认扩展名
        
        # 尝试从URL获取扩展名
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        if path.endswith((".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac")):
            file_ext = os.path.splitext(path)[1]
        
        file_path = os.path.join(temp_dir, f"{file_name}{file_ext}")
        
        try:
            # 如果是视频平台URL，需要先提取音频
            try:
                platform_info = self.validate_video_url(url)
                # 这里应该集成yt-dlp或其他工具提取音频
                # 暂时返回错误
                raise NotImplementedError("从视频平台提取音频功能尚未实现")
            except VideoUploadException:
                # 不是视频平台URL，直接下载
                pass
            
            # 直接下载音频文件
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise VideoProcessingException(f"下载失败，状态码: {response.status}")
                    
                    # 检查Content-Type
                    content_type = response.headers.get("Content-Type", "")
                    if not content_type.startswith(("audio/", "application/octet-stream")):
                        # 如果不是音频类型，但URL有效，尝试继续下载
                        if not await self.is_audio_url(url):
                            raise VideoProcessingException(f"不是有效的音频文件: {content_type}")
                    
                    # 下载文件
                    with open(file_path, "wb") as f:
                        while True:
                            chunk = await response.content.read(1024 * 1024)  # 1MB chunks
                            if not chunk:
                                break
                            f.write(chunk)
            
            return file_path
        except Exception as e:
            # 清理可能部分下载的文件
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except:
                    pass
            
            if isinstance(e, (VideoUploadException, VideoProcessingException, NotImplementedError)):
                raise
            raise VideoProcessingException(f"下载音频失败: {str(e)}")
    
    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        获取视频基本信息（标题、时长等）
        
        Args:
            url: 视频URL
            
        Returns:
            dict: 视频信息
        """
        platform_info = self.validate_video_url(url)
        
        try:
            if platform_info["platform"] == "youtube":
                return await self._get_youtube_info(platform_info)
            elif platform_info["platform"] == "bilibili":
                return await self._get_bilibili_info(platform_info)
            elif platform_info["platform"] == "vimeo":
                return await self._get_vimeo_info(platform_info)
            else:
                # 返回基本信息
                return {
                    "title": f"{platform_info['platform']} 视频",
                    "duration": None,
                    "description": "",
                    "thumbnail": None,
                    "platform": platform_info["platform"],
                    "video_id": platform_info["video_id"],
                    "original_url": url
                }
                
        except Exception as e:
            # 如果获取详细信息失败，返回基本信息
            return {
                "title": f"视频 - {platform_info['video_id']}",
                "duration": None,
                "description": f"来自 {platform_info['platform']}",
                "thumbnail": None,
                "platform": platform_info["platform"],
                "video_id": platform_info["video_id"],
                "original_url": url,
                "error": str(e)
            }
    
    async def _get_youtube_info(self, platform_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取YouTube视频信息"""
        # 这里可以集成YouTube Data API
        # 现在返回模拟数据
        return {
            "title": f"YouTube 视频 - {platform_info['video_id']}",
            "duration": None,
            "description": "YouTube 视频描述",
            "thumbnail": f"https://img.youtube.com/vi/{platform_info['video_id']}/maxresdefault.jpg",
            "platform": "youtube",
            "video_id": platform_info["video_id"],
            "original_url": platform_info["original_url"]
        }
    
    async def _get_bilibili_info(self, platform_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取B站视频信息"""
        # 这里可以集成B站API
        # 现在返回模拟数据
        return {
            "title": f"B站视频 - {platform_info['video_id']}",
            "duration": None,
            "description": "B站视频描述",
            "thumbnail": None,
            "platform": "bilibili", 
            "video_id": platform_info["video_id"],
            "original_url": platform_info["original_url"]
        }
    
    async def _get_vimeo_info(self, platform_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取Vimeo视频信息"""
        # 这里可以集成Vimeo API
        # 现在返回模拟数据
        return {
            "title": f"Vimeo 视频 - {platform_info['video_id']}",
            "duration": None,
            "description": "Vimeo 视频描述",
            "thumbnail": None,
            "platform": "vimeo",
            "video_id": platform_info["video_id"],
            "original_url": platform_info["original_url"]
        }
    
    def estimate_download_time(self, platform: str, video_duration: Optional[int] = None) -> int:
        """估算视频下载时间（秒）"""
        base_time = {
            "youtube": 30,
            "bilibili": 45,
            "vimeo": 25
        }
        
        base = base_time.get(platform, 30)
        
        if video_duration:
            # 基于视频时长估算，假设下载时间约为视频时长的10-20%
            return max(base, int(video_duration * 0.15))
        
        return base


# 全局视频服务实例
video_service = VideoService() 