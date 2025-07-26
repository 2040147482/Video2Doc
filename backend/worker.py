"""
Celery工作进程模块
负责处理异步视频处理任务
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入Celery
try:
    from celery import Celery
    HAS_CELERY = True
except ImportError:
    logger.warning("Celery未安装，将使用同步处理")
    HAS_CELERY = False

# 创建Celery实例
if HAS_CELERY:
    # 从环境变量获取Redis URL
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    
    celery_app = Celery(
        "video_processing",
        broker=redis_url,
        backend=redis_url
    )
    
    # 配置Celery
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Shanghai',
        enable_utc=True,
        task_track_started=True,
        worker_max_tasks_per_child=10,  # 处理10个任务后重启worker（防止内存泄漏）
        task_time_limit=3600,  # 任务超时时间（秒）
    )
    
    logger.info(f"Celery初始化成功，使用Redis: {redis_url}")
else:
    celery_app = None
    logger.warning("Celery未初始化")

# 异步运行函数
def run_async(func, *args, **kwargs):
    """
    运行异步函数
    
    Args:
        func: 异步函数
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        函数结果
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # 如果事件循环已经运行，创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(func(*args, **kwargs))

# 视频处理任务
if HAS_CELERY:
    @celery_app.task(name="process_video")
    def process_video(task_id: str, task_data: Dict[str, Any]):
        """
        处理视频任务
        
        Args:
            task_id: 任务ID
            task_data: 任务数据
        """
        from app.services.queue_service import queue_service
        from app.models.video_processing import ProcessingStatus
        
        logger.info(f"开始处理视频任务: {task_id}")
        
        try:
            # 导入必要的模块
            from app.services.video_processor.extractor import video_extractor
            from app.services.video_processor.analyzer import video_analyzer
            from app.services.storage_service import storage_service
            
            # 更新任务状态
            queue_service.update_task_status(
                task_id=task_id,
                status=ProcessingStatus.EXTRACTING,
                progress=0.1,
                message="正在提取视频信息..."
            )
            
            # 获取视频路径
            video_path = task_data.get("file_path")
            if not video_path:
                raise ValueError("视频路径不能为空")
            
            # 获取视频元数据
            metadata = run_async(video_analyzer.get_video_metadata, video_path)
            
            # 更新任务状态
            queue_service.update_task_status(
                task_id=task_id,
                status=ProcessingStatus.PROCESSING_AUDIO,
                progress=0.2,
                message="正在提取音频..."
            )
            
            # 提取音频
            options = task_data.get("options", {})
            if options.get("extract_audio", True):
                audio_path = run_async(video_extractor.extract_audio, video_path)
            else:
                audio_path = None
            
            # 更新任务状态
            queue_service.update_task_status(
                task_id=task_id,
                status=ProcessingStatus.PROCESSING_FRAMES,
                progress=0.4,
                message="正在提取视频帧..."
            )
            
            # 提取帧
            frames = []
            if options.get("extract_frames", True):
                frame_interval = options.get("frame_interval", 5)
                detect_scenes = options.get("detect_scenes", False)
                frames = run_async(
                    video_extractor.extract_frames,
                    video_path,
                    frame_interval,
                    detect_scenes
                )
            
            # 更新任务状态
            queue_service.update_task_status(
                task_id=task_id,
                status=ProcessingStatus.GENERATING_OUTPUT,
                progress=0.8,
                message="正在生成输出..."
            )
            
            # 创建结果数据
            # 注意：这里只是一个简单的示例，实际应用中应该有更复杂的处理逻辑
            result_data = {
                "task_id": task_id,
                "status": ProcessingStatus.COMPLETED,
                "metadata": metadata,
                "frames": frames,
                "transcript": "这是一个示例转录文本",  # 实际应该调用语音识别服务
                "summary": "这是一个示例摘要",  # 实际应该调用AI摘要服务
                "markdown_content": "# 视频分析结果\n\n## 摘要\n\n这是一个示例摘要\n\n## 转录\n\n这是一个示例转录文本",
                "text_content": "视频分析结果\n\n摘要\n\n这是一个示例摘要\n\n转录\n\n这是一个示例转录文本"
            }
            
            # 保存结果
            output_files = run_async(storage_service.save_processing_result, task_id, result_data)
            result_data["output_files"] = output_files
            
            # 更新任务状态
            queue_service.update_task_status(
                task_id=task_id,
                status=ProcessingStatus.COMPLETED,
                progress=1.0,
                message="处理完成"
            )
            
            logger.info(f"任务处理成功: {task_id}")
            return {"success": True, "task_id": task_id}
        except Exception as e:
            logger.error(f"任务处理失败 {task_id}: {str(e)}")
            
            # 更新任务状态
            queue_service.update_task_status(
                task_id=task_id,
                status=ProcessingStatus.FAILED,
                progress=0.0,
                message=f"处理失败: {str(e)}",
                error=str(e)
            )
            
            return {"success": False, "task_id": task_id, "error": str(e)}

# 启动Celery Worker的命令：
# celery -A worker worker --loglevel=info

if __name__ == "__main__":
    logger.info("Celery Worker就绪，等待任务...") 