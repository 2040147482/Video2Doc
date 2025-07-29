#!/usr/bin/env python3
"""
Celery Worker 启动脚本
用于启动Video2Doc的异步任务处理工作者
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ.setdefault('PYTHONPATH', str(project_root))

from app.services.queue_service.celery_app import celery_app

if __name__ == '__main__':
    # 启动Celery worker
    celery_app.start([
        'worker',
        '--loglevel=info',
        '--concurrency=4',
        '--hostname=worker@%h',
        '--queues=default,video_processing,audio_transcription,image_analysis,summary_generation,document_export',
        '--pool=prefork',
        '--optimization=fair'
    ]) 