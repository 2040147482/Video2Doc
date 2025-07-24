import re
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from app.exceptions import InvalidVideoUrlError, VideoProcessingError


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
    
    def validate_video_url(self, url: str) -> Dict[str, Any]:
        """
        验证视频URL并提取平台信息
        
        Args:
            url: 视频URL
            
        Returns:
            dict: 包含平台、视频ID等信息
            
        Raises:
            InvalidVideoUrlError: URL无效或不支持的平台
        """
        if not url or not url.strip():
            raise InvalidVideoUrlError("视频链接不能为空")
        
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
            
            raise InvalidVideoUrlError(
                f"暂不支持该视频平台。支持的平台：{', '.join(supported_domains)}"
            )
            
        except Exception as e:
            if isinstance(e, InvalidVideoUrlError):
                raise
            raise InvalidVideoUrlError(f"URL格式无效: {str(e)}")
    
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