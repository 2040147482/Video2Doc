"""
格式转换器模块
负责转换和优化音频和图像
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# 配置日志
logger = logging.getLogger(__name__)

class FormatConverter:
    """格式转换器类，用于转换和优化音频和图像"""
    
    def __init__(self, temp_dir: str = "./temp"):
        """
        初始化格式转换器
        
        Args:
            temp_dir: 临时文件存储目录
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True, parents=True)
    
    async def convert_audio_format(
        self, 
        audio_path: str, 
        output_format: str = "wav",
        sample_rate: int = 16000,
        channels: int = 1
    ) -> str:
        """
        转换音频格式
        
        Args:
            audio_path: 音频文件路径
            output_format: 输出格式
            sample_rate: 采样率
            channels: 声道数
            
        Returns:
            转换后的音频文件路径
            
        Raises:
            Exception: 如果转换失败
        """
        output_path = self.temp_dir / f"{Path(audio_path).stem}_converted.{output_format}"
        
        try:
            logger.info(f"转换音频格式: {audio_path} -> {output_format}")
            
            # 使用FFmpeg转换音频
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-i", audio_path, 
                "-ar", str(sample_rate),  # 采样率
                "-ac", str(channels),     # 声道数
                "-y",                     # 覆盖输出文件
                str(output_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "未知错误"
                logger.error(f"音频转换失败: {error_msg}")
                raise Exception(f"音频转换失败: {error_msg}")
                
            logger.info(f"音频转换成功: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"音频转换错误: {str(e)}")
            raise Exception(f"音频转换错误: {str(e)}")
    
    async def optimize_frame(
        self, 
        frame_path: str, 
        output_format: str = "jpg",
        resize: Optional[tuple] = None,
        quality: int = 90
    ) -> str:
        """
        优化图像帧
        
        Args:
            frame_path: 帧图像路径
            output_format: 输出格式
            resize: 调整大小 (width, height)，None表示不调整
            quality: 图像质量（1-100）
            
        Returns:
            优化后的图像路径
            
        Raises:
            Exception: 如果优化失败
        """
        output_path = self.temp_dir / f"{Path(frame_path).stem}_optimized.{output_format}"
        
        try:
            logger.info(f"优化图像帧: {frame_path}")
            
            # 构建FFmpeg命令
            cmd = ["ffmpeg", "-i", frame_path]
            
            # 添加调整大小选项
            if resize:
                width, height = resize
                cmd.extend(["-vf", f"scale={width}:{height}"])
            
            # 添加质量选项
            if output_format.lower() == "jpg" or output_format.lower() == "jpeg":
                cmd.extend(["-q:v", str(int(quality / 10))])  # FFmpeg的质量范围是1-31，越小越好
            elif output_format.lower() == "png":
                cmd.extend(["-compression_level", str(int((100 - quality) / 10))])  # PNG压缩级别0-9，越大压缩率越高
            
            # 添加输出路径
            cmd.extend(["-y", str(output_path)])
            
            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "未知错误"
                logger.error(f"图像优化失败: {error_msg}")
                raise Exception(f"图像优化失败: {error_msg}")
                
            logger.info(f"图像优化成功: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"图像优化错误: {str(e)}")
            raise Exception(f"图像优化错误: {str(e)}")
    
    async def create_thumbnail(
        self, 
        image_path: str, 
        width: int = 320,
        height: int = 180
    ) -> str:
        """
        创建缩略图
        
        Args:
            image_path: 图像路径
            width: 缩略图宽度
            height: 缩略图高度
            
        Returns:
            缩略图路径
            
        Raises:
            Exception: 如果创建失败
        """
        output_path = self.temp_dir / f"{Path(image_path).stem}_thumb.jpg"
        
        try:
            logger.info(f"创建缩略图: {image_path}")
            
            # 使用FFmpeg创建缩略图
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-i", image_path, 
                "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
                "-y", str(output_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "未知错误"
                logger.error(f"缩略图创建失败: {error_msg}")
                raise Exception(f"缩略图创建失败: {error_msg}")
                
            logger.info(f"缩略图创建成功: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"缩略图创建错误: {str(e)}")
            raise Exception(f"缩略图创建错误: {str(e)}")
    
    async def extract_audio_segment(
        self, 
        audio_path: str, 
        start_time: float,
        duration: float
    ) -> str:
        """
        提取音频片段
        
        Args:
            audio_path: 音频文件路径
            start_time: 开始时间（秒）
            duration: 持续时间（秒）
            
        Returns:
            提取的音频片段路径
            
        Raises:
            Exception: 如果提取失败
        """
        output_path = self.temp_dir / f"{Path(audio_path).stem}_segment_{int(start_time)}s.wav"
        
        try:
            logger.info(f"提取音频片段: {audio_path} ({start_time}s - {start_time + duration}s)")
            
            # 使用FFmpeg提取音频片段
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-i", audio_path, 
                "-ss", str(start_time),
                "-t", str(duration),
                "-y", str(output_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "未知错误"
                logger.error(f"音频片段提取失败: {error_msg}")
                raise Exception(f"音频片段提取失败: {error_msg}")
                
            logger.info(f"音频片段提取成功: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"音频片段提取错误: {str(e)}")
            raise Exception(f"音频片段提取错误: {str(e)}")

# 创建全局实例
format_converter = FormatConverter()
