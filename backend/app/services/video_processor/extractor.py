"""
视频提取器模块
负责从视频中提取音频和关键帧
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# 配置日志
logger = logging.getLogger(__name__)

class VideoExtractor:
    """视频提取器类，用于从视频中提取音频和帧"""
    
    def __init__(self, temp_dir: str = "./temp"):
        """
        初始化视频提取器
        
        Args:
            temp_dir: 临时文件存储目录
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
    async def extract_audio(self, video_path: str, output_format: str = "wav") -> str:
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            output_format: 输出音频格式，默认为wav
            
        Returns:
            提取的音频文件路径
            
        Raises:
            Exception: 如果音频提取失败
        """
        output_path = self.temp_dir / f"{Path(video_path).stem}_audio.{output_format}"
        
        try:
            logger.info(f"从视频 {video_path} 提取音频...")
            # 使用FFmpeg异步提取音频
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", str(output_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "未知错误"
                logger.error(f"FFmpeg音频提取失败: {error_msg}")
                raise Exception(f"FFmpeg音频提取失败: {error_msg}")
                
            logger.info(f"音频提取成功: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"音频提取错误: {str(e)}")
            raise Exception(f"音频提取错误: {str(e)}")
    
    async def extract_frames(
        self, 
        video_path: str, 
        interval: int = 5,
        detect_scenes: bool = False,
        max_frames: int = 100
    ) -> List[Dict[str, Any]]:
        """
        提取视频帧
        
        Args:
            video_path: 视频文件路径
            interval: 帧提取间隔（秒）
            detect_scenes: 是否使用场景检测
            max_frames: 最大帧数
            
        Returns:
            帧信息列表
            
        Raises:
            Exception: 如果帧提取失败
        """
        frames_dir = self.temp_dir / f"{Path(video_path).stem}_frames"
        frames_dir.mkdir(exist_ok=True)
        
        frames = []
        
        try:
            logger.info(f"从视频 {video_path} 提取帧...")
            
            if detect_scenes:
                # 使用场景检测提取关键帧
                await self._extract_frames_by_scene_detection(video_path, frames_dir, max_frames)
            else:
                # 按固定间隔提取帧
                await self._extract_frames_by_interval(video_path, frames_dir, interval)
            
            # 获取提取的帧信息
            frame_count = 0
            for frame_file in sorted(frames_dir.glob("*.jpg")):
                if frame_count >= max_frames:
                    break
                    
                frame_number = int(frame_file.stem)
                timestamp = frame_number * interval
                
                frames.append({
                    "path": str(frame_file),
                    "timestamp": timestamp,
                    "timestamp_formatted": self._format_timestamp(timestamp),
                    "frame_number": frame_number
                })
                frame_count += 1
                
            logger.info(f"帧提取成功，共 {len(frames)} 帧")
            return frames
        except Exception as e:
            logger.error(f"帧提取错误: {str(e)}")
            raise Exception(f"帧提取错误: {str(e)}")
    
    async def _extract_frames_by_interval(
        self, 
        video_path: str, 
        output_dir: Path, 
        interval: int
    ) -> None:
        """
        按固定间隔提取帧
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            interval: 间隔（秒）
            
        Raises:
            Exception: 如果帧提取失败
        """
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", video_path, "-vf", f"fps=1/{interval}", 
            f"{output_dir}/%04d.jpg",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "未知错误"
            logger.error(f"FFmpeg帧提取失败: {error_msg}")
            raise Exception(f"FFmpeg帧提取失败: {error_msg}")
    
    async def _extract_frames_by_scene_detection(
        self, 
        video_path: str, 
        output_dir: Path, 
        max_frames: int
    ) -> None:
        """
        使用场景检测提取关键帧
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            max_frames: 最大帧数
            
        Raises:
            Exception: 如果帧提取失败
        """
        # 使用FFmpeg的场景检测过滤器
        # 这里使用简化的场景检测方法，实际应用可能需要更复杂的算法
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", video_path, 
            "-vf", f"select='gt(scene,0.3)',showinfo", 
            "-vsync", "vfr", 
            f"{output_dir}/%04d.jpg",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "未知错误"
            logger.error(f"FFmpeg场景检测失败: {error_msg}")
            raise Exception(f"FFmpeg场景检测失败: {error_msg}")
    
    async def get_video_duration(self, video_path: str) -> float:
        """
        获取视频时长（秒）
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频时长（秒）
            
        Raises:
            Exception: 如果获取时长失败
        """
        try:
            process = await asyncio.create_subprocess_exec(
                "ffprobe", "-v", "error", "-show_entries", "format=duration", 
                "-of", "default=noprint_wrappers=1:nokey=1", video_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "未知错误"
                logger.error(f"FFprobe获取视频时长失败: {error_msg}")
                raise Exception(f"FFprobe获取视频时长失败: {error_msg}")
            
            duration = float(stdout.decode().strip())
            logger.info(f"视频时长: {duration}秒")
            return duration
        except Exception as e:
            logger.error(f"获取视频时长错误: {str(e)}")
            raise Exception(f"获取视频时长错误: {str(e)}")
    
    def _format_timestamp(self, seconds: int) -> str:
        """
        将秒数格式化为 HH:MM:SS 格式
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化的时间字符串
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# 创建全局实例
video_extractor = VideoExtractor()
