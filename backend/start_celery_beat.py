#!/usr/bin/env python3
"""
Celery Beat 启动脚本
用于启动Video2Doc的定时任务调度器
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
    # 启动Celery beat
    celery_app.start([
        'beat',
        '--loglevel=info',
        '--schedule=/tmp/celerybeat-schedule',
        '--pidfile=/tmp/celerybeat.pid'
    ]) 