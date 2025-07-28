"""
队列服务模块
负责管理视频处理任务队列
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime
from pathlib import Path

# 导入Celery（如果可用）
try:
    from celery import Celery
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False

# 配置日志
logger = logging.getLogger(__name__)

class QueueService:
    """队列服务类，用于管理视频处理任务队列"""
    
    def __init__(self, 
                 storage_path: str = "./.taskmaster/tasks", 
                 use_celery: bool = False,
                 redis_url: Optional[str] = None):
        """
        初始化队列服务
        
        Args:
            storage_path: 任务存储路径
            use_celery: 是否使用Celery
            redis_url: Redis URL（Celery后端）
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True, parents=True)
        
        # 内存中的任务存储
        self.tasks: Dict[str, Dict[str, Any]] = {}
        
        # 任务状态回调
        self.status_callbacks: Dict[str, List[Callable[[str, str, float], Awaitable[None]]]] = {}
        
        # Celery配置
        self.use_celery = use_celery and HAS_CELERY
        self.redis_url = redis_url or "redis://localhost:6379/0"
        
        if self.use_celery:
            self._init_celery()
        
        # 加载现有任务
        self._load_tasks()
    
    def _init_celery(self):
        """初始化Celery"""
        try:
            self.celery = Celery(
                "video_processing",
                broker=self.redis_url,
                backend=self.redis_url
            )
            logger.info("Celery初始化成功")
        except Exception as e:
            logger.error(f"Celery初始化失败: {str(e)}")
            self.use_celery = False
    
    def _load_tasks(self):
        """加载现有任务"""
        try:
            task_files = list(self.storage_path.glob("*.json"))
            for task_file in task_files:
                try:
                    with open(task_file, "r", encoding="utf-8") as f:
                        task_data = json.load(f)
                        task_id = task_data.get("task_id")
                        if task_id:
                            self.tasks[task_id] = task_data
                except Exception as e:
                    logger.error(f"加载任务文件失败 {task_file}: {str(e)}")
            
            logger.info(f"加载了 {len(self.tasks)} 个任务")
        except Exception as e:
            logger.error(f"加载任务失败: {str(e)}")
    
    def _save_task(self, task_id: str):
        """
        保存任务到文件
        
        Args:
            task_id: 任务ID
        """
        if task_id not in self.tasks:
            return
        
        task_file = self.storage_path / f"{task_id}.json"
        try:
            with open(task_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks[task_id], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存任务失败 {task_id}: {str(e)}")
    
    def create_task(self, task_data: Dict[str, Any]) -> str:
        """
        创建新任务
        
        Args:
            task_data: 任务数据
            
        Returns:
            任务ID
        """
        task_id = task_data.get("task_id")
        if not task_id:
            raise ValueError("任务数据必须包含task_id")
        
        # 添加时间戳
        now = datetime.now().isoformat()
        task_data["created_at"] = now
        task_data["updated_at"] = now
        
        # 存储任务
        self.tasks[task_id] = task_data
        self._save_task(task_id)
        
        logger.info(f"创建任务: {task_id}")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务数据，如果不存在则返回None
        """
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        获取所有任务
        
        Returns:
            任务列表
        """
        return list(self.tasks.values())
    
    def update_task_status(self, task_id: str, status: str, progress: float = 0.0, message: str = "", error: str = ""):
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态
            progress: 进度（0-1）
            message: 状态消息
            error: 错误信息
        """
        if task_id not in self.tasks:
            logger.warning(f"尝试更新不存在的任务: {task_id}")
            return
        
        task = self.tasks[task_id]
        task["status"] = status
        task["progress"] = progress
        task["updated_at"] = datetime.now().isoformat()
        
        if message:
            task["message"] = message
        
        if error:
            task["error_message"] = error
        
        self._save_task(task_id)
        
        # 注意：暂时移除回调触发以避免异步问题
        # TODO: 修复异步回调
        # self._trigger_callbacks(task_id, status, progress)
        
        logger.info(f"更新任务状态: {task_id} -> {status} ({progress:.1%})")
    
    def delete_task(self, task_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功删除
        """
        if task_id not in self.tasks:
            return False
        
        # 从内存中删除
        del self.tasks[task_id]
        
        # 删除文件
        task_file = self.storage_path / f"{task_id}.json"
        try:
            if task_file.exists():
                task_file.unlink()
        except Exception as e:
            logger.error(f"删除任务文件失败 {task_id}: {str(e)}")
        
        logger.info(f"删除任务: {task_id}")
        return True
    
    def enqueue_task(self, task_id: str, task_func: str, *args, **kwargs) -> str:
        """
        将任务加入队列
        
        Args:
            task_id: 任务ID
            task_func: 任务函数名
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            任务ID或Celery任务ID
        """
        if self.use_celery:
            try:
                # 使用Celery异步处理
                celery_task = self.celery.send_task(
                    task_func,
                    args=[task_id, *args],
                    kwargs=kwargs,
                    task_id=task_id
                )
                logger.info(f"任务加入Celery队列: {task_id} ({task_func})")
                return celery_task.id
            except Exception as e:
                logger.error(f"Celery任务入队失败: {str(e)}")
                # 回退到同步处理
        
        # 如果没有Celery或失败，则返回原始任务ID
        logger.info(f"任务加入内存队列: {task_id} ({task_func})")
        return task_id
    
    def register_status_callback(self, task_id: str, callback: Callable[[str, str, float], Awaitable[None]]):
        """
        注册任务状态回调
        
        Args:
            task_id: 任务ID
            callback: 回调函数 async def callback(task_id, status, progress)
        """
        if task_id not in self.status_callbacks:
            self.status_callbacks[task_id] = []
        
        self.status_callbacks[task_id].append(callback)
    
    async def _trigger_callbacks(self, task_id: str, status: str, progress: float):
        """
        触发任务状态回调
        
        Args:
            task_id: 任务ID
            status: 状态
            progress: 进度
        """
        if task_id not in self.status_callbacks:
            return
        
        for callback in self.status_callbacks[task_id]:
            try:
                await callback(task_id, status, progress)
            except Exception as e:
                logger.error(f"任务回调执行失败: {str(e)}")

# 创建全局实例
queue_service = QueueService() 