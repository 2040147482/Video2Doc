"""
存储服务模块
负责管理处理结果的存储
"""

import os
import json
import shutil
import logging
import asyncio
from typing import Dict, Any, List, Optional, BinaryIO
from datetime import datetime
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)

class StorageService:
    """存储服务类，用于管理处理结果的存储"""
    
    def __init__(self, 
                 results_dir: str = "./results",
                 temp_dir: str = "./temp",
                 max_temp_age_days: int = 1):
        """
        初始化存储服务
        
        Args:
            results_dir: 结果存储目录
            temp_dir: 临时文件目录
            max_temp_age_days: 临时文件最大保存天数
        """
        self.results_dir = Path(results_dir)
        self.temp_dir = Path(temp_dir)
        self.max_temp_age_days = max_temp_age_days
        
        # 创建目录
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.temp_dir.mkdir(exist_ok=True, parents=True)
    
    async def save_processing_result(self, task_id: str, result_data: Dict[str, Any]) -> Dict[str, str]:
        """
        保存处理结果
        
        Args:
            task_id: 任务ID
            result_data: 结果数据
            
        Returns:
            输出文件路径字典 {格式: 路径}
        """
        # 创建任务结果目录
        task_dir = self.results_dir / task_id
        task_dir.mkdir(exist_ok=True)
        
        # 保存元数据
        metadata_file = task_dir / "metadata.json"
        try:
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存结果元数据失败 {task_id}: {str(e)}")
        
        # 保存各种格式的输出
        output_files = {}
        
        # 保存Markdown
        if "markdown_content" in result_data:
            md_file = task_dir / f"{task_id}.md"
            try:
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(result_data["markdown_content"])
                output_files["markdown"] = str(md_file)
            except Exception as e:
                logger.error(f"保存Markdown失败 {task_id}: {str(e)}")
        
        # 保存文本
        if "text_content" in result_data:
            txt_file = task_dir / f"{task_id}.txt"
            try:
                with open(txt_file, "w", encoding="utf-8") as f:
                    f.write(result_data["text_content"])
                output_files["text"] = str(txt_file)
            except Exception as e:
                logger.error(f"保存文本失败 {task_id}: {str(e)}")
        
        # 保存HTML（如果有）
        if "html_content" in result_data:
            html_file = task_dir / f"{task_id}.html"
            try:
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(result_data["html_content"])
                output_files["html"] = str(html_file)
            except Exception as e:
                logger.error(f"保存HTML失败 {task_id}: {str(e)}")
        
        # 保存PDF（如果有）
        if "pdf_path" in result_data:
            pdf_src = Path(result_data["pdf_path"])
            if pdf_src.exists():
                pdf_dst = task_dir / f"{task_id}.pdf"
                try:
                    shutil.copy2(pdf_src, pdf_dst)
                    output_files["pdf"] = str(pdf_dst)
                except Exception as e:
                    logger.error(f"保存PDF失败 {task_id}: {str(e)}")
        
        # 复制帧图像（如果有）
        if "frames" in result_data and isinstance(result_data["frames"], list):
            frames_dir = task_dir / "frames"
            frames_dir.mkdir(exist_ok=True)
            
            for i, frame in enumerate(result_data["frames"]):
                if "path" in frame:
                    src_path = Path(frame["path"])
                    if src_path.exists():
                        dst_path = frames_dir / f"frame_{i:04d}.jpg"
                        try:
                            shutil.copy2(src_path, dst_path)
                            # 更新帧路径
                            frame["path"] = str(dst_path)
                        except Exception as e:
                            logger.error(f"复制帧图像失败 {i}: {str(e)}")
        
        logger.info(f"保存处理结果成功: {task_id}, 输出格式: {list(output_files.keys())}")
        return output_files
    
    async def get_processing_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取处理结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            结果数据，如果不存在则返回None
        """
        metadata_file = self.results_dir / task_id / "metadata.json"
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                result_data = json.load(f)
            return result_data
        except Exception as e:
            logger.error(f"读取结果元数据失败 {task_id}: {str(e)}")
            return None
    
    async def delete_processing_result(self, task_id: str) -> bool:
        """
        删除处理结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功删除
        """
        task_dir = self.results_dir / task_id
        if not task_dir.exists():
            return False
        
        try:
            shutil.rmtree(task_dir)
            logger.info(f"删除处理结果成功: {task_id}")
            return True
        except Exception as e:
            logger.error(f"删除处理结果失败 {task_id}: {str(e)}")
            return False
    
    async def create_zip_archive(self, task_id: str) -> Optional[str]:
        """
        创建ZIP归档
        
        Args:
            task_id: 任务ID
            
        Returns:
            ZIP文件路径，如果创建失败则返回None
        """
        import zipfile
        
        task_dir = self.results_dir / task_id
        if not task_dir.exists():
            logger.error(f"任务目录不存在: {task_id}")
            return None
        
        zip_path = self.results_dir / f"{task_id}.zip"
        
        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(task_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(task_dir)
                        zipf.write(file_path, arcname)
            
            logger.info(f"创建ZIP归档成功: {zip_path}")
            return str(zip_path)
        except Exception as e:
            logger.error(f"创建ZIP归档失败 {task_id}: {str(e)}")
            return None
    
    async def cleanup_temp_files(self):
        """清理临时文件"""
        import time
        
        now = time.time()
        max_age = self.max_temp_age_days * 86400  # 天数转秒数
        
        try:
            for item in self.temp_dir.iterdir():
                if not item.is_file():
                    continue
                
                # 检查文件年龄
                mtime = item.stat().st_mtime
                age = now - mtime
                
                if age > max_age:
                    try:
                        item.unlink()
                        logger.debug(f"清理临时文件: {item}")
                    except Exception as e:
                        logger.error(f"清理临时文件失败 {item}: {str(e)}")
            
            logger.info("临时文件清理完成")
        except Exception as e:
            logger.error(f"临时文件清理失败: {str(e)}")
    
    async def save_file(self, file_data: BinaryIO, filename: str, directory: Optional[str] = None) -> str:
        """
        保存文件
        
        Args:
            file_data: 文件数据
            filename: 文件名
            directory: 目录（相对于结果目录）
            
        Returns:
            保存的文件路径
        """
        if directory:
            save_dir = self.results_dir / directory
        else:
            save_dir = self.results_dir
        
        save_dir.mkdir(exist_ok=True, parents=True)
        file_path = save_dir / filename
        
        try:
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file_data, f)
            
            logger.info(f"保存文件成功: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"保存文件失败 {filename}: {str(e)}")
            raise Exception(f"保存文件失败: {str(e)}")

# 创建全局实例
storage_service = StorageService() 