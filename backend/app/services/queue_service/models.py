"""
任务队列数据模型
定义任务状态、结果和各种任务类型的数据结构
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"          # 等待中
    STARTED = "started"          # 已开始
    PROGRESS = "progress"        # 进行中
    SUCCESS = "success"          # 成功
    FAILURE = "failure"          # 失败
    RETRY = "retry"              # 重试中
    REVOKED = "revoked"          # 已撤销


class TaskPriority(str, Enum):
    """任务优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskProgress(BaseModel):
    """任务进度信息"""
    current: int = Field(0, description="当前进度")
    total: int = Field(100, description="总进度")
    percentage: float = Field(0.0, ge=0.0, le=100.0, description="完成百分比")
    message: Optional[str] = Field(None, description="进度消息")
    eta: Optional[datetime] = Field(None, description="预计完成时间")


class TaskResult(BaseModel):
    """任务结果基类"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果数据")
    error: Optional[str] = Field(None, description="错误信息")
    traceback: Optional[str] = Field(None, description="错误堆栈")
    progress: Optional[TaskProgress] = Field(None, description="任务进度")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    duration: Optional[float] = Field(None, description="执行时长（秒）")
    retry_count: int = Field(0, description="重试次数")
    max_retries: int = Field(3, description="最大重试次数")


class VideoProcessingTask(BaseModel):
    """视频处理任务参数"""
    task_id: str = Field(..., description="任务ID")
    video_file_path: str = Field(..., description="视频文件路径")
    output_dir: str = Field(..., description="输出目录")
    extract_audio: bool = Field(True, description="是否提取音频")
    extract_frames: bool = Field(True, description="是否提取关键帧")
    frame_interval: int = Field(30, description="帧提取间隔（秒）")
    audio_format: str = Field("wav", description="音频格式")
    image_format: str = Field("jpg", description="图像格式")
    priority: TaskPriority = Field(TaskPriority.NORMAL, description="任务优先级")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")


class AudioTranscriptionTask(BaseModel):
    """音频转录任务参数"""
    task_id: str = Field(..., description="任务ID")
    audio_file_path: str = Field(..., description="音频文件路径")
    language: Optional[str] = Field(None, description="音频语言")
    model: str = Field("whisper-base", description="转录模型")
    with_timestamps: bool = Field(True, description="是否包含时间戳")
    chunk_size: int = Field(30, description="音频分块大小（秒）")
    priority: TaskPriority = Field(TaskPriority.NORMAL, description="任务优先级")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")


class ImageAnalysisTask(BaseModel):
    """图像分析任务参数"""
    task_id: str = Field(..., description="任务ID")
    image_paths: List[str] = Field(..., description="图像文件路径列表")
    analysis_types: List[str] = Field(["ocr", "scene"], description="分析类型")
    ocr_language: str = Field("auto", description="OCR语言")
    scene_confidence: float = Field(0.5, description="场景识别置信度")
    priority: TaskPriority = Field(TaskPriority.NORMAL, description="任务优先级")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")


class SummaryGenerationTask(BaseModel):
    """摘要生成任务参数"""
    task_id: str = Field(..., description="任务ID")
    transcript_data: Dict[str, Any] = Field(..., description="转录数据")
    image_analysis_data: Optional[Dict[str, Any]] = Field(None, description="图像分析数据")
    summary_type: str = Field("detailed", description="摘要类型")
    max_length: int = Field(1000, description="最大摘要长度")
    language: str = Field("zh", description="摘要语言")
    include_chapters: bool = Field(True, description="是否包含章节")
    include_keywords: bool = Field(True, description="是否包含关键词")
    priority: TaskPriority = Field(TaskPriority.HIGH, description="任务优先级")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")


class DocumentExportTask(BaseModel):
    """文档导出任务参数"""
    task_id: str = Field(..., description="任务ID")
    content_data: Dict[str, Any] = Field(..., description="内容数据")
    export_formats: List[str] = Field(..., description="导出格式列表")
    template: str = Field("standard", description="导出模板")
    include_images: bool = Field(True, description="是否包含图片")
    include_timestamps: bool = Field(True, description="是否包含时间戳")
    include_metadata: bool = Field(True, description="是否包含元数据")
    custom_filename: Optional[str] = Field(None, description="自定义文件名")
    priority: TaskPriority = Field(TaskPriority.NORMAL, description="任务优先级")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")


class TaskChain(BaseModel):
    """任务链配置"""
    chain_id: str = Field(..., description="任务链ID")
    tasks: List[Dict[str, Any]] = Field(..., description="任务列表")
    auto_start: bool = Field(True, description="是否自动开始")
    stop_on_failure: bool = Field(True, description="失败时是否停止")
    retry_failed: bool = Field(False, description="是否重试失败的任务")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")


class TaskStatistics(BaseModel):
    """任务统计信息"""
    total_tasks: int = Field(0, description="总任务数")
    pending_tasks: int = Field(0, description="等待中任务数")
    running_tasks: int = Field(0, description="运行中任务数")
    completed_tasks: int = Field(0, description="已完成任务数")
    failed_tasks: int = Field(0, description="失败任务数")
    success_rate: float = Field(0.0, description="成功率")
    average_duration: float = Field(0.0, description="平均执行时长")
    queue_size: int = Field(0, description="队列大小")
    active_workers: int = Field(0, description="活跃工作者数量")


class WorkerInfo(BaseModel):
    """工作者信息"""
    worker_id: str = Field(..., description="工作者ID")
    hostname: str = Field(..., description="主机名")
    active_tasks: int = Field(0, description="活跃任务数")
    processed_tasks: int = Field(0, description="已处理任务数")
    load_average: List[float] = Field([], description="负载平均值")
    status: str = Field("online", description="工作者状态")
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow, description="最后心跳时间")


class QueueInfo(BaseModel):
    """队列信息"""
    queue_name: str = Field(..., description="队列名称")
    message_count: int = Field(0, description="消息数量")
    consumer_count: int = Field(0, description="消费者数量")
    priority: TaskPriority = Field(TaskPriority.NORMAL, description="队列优先级")
    routing_key: str = Field("", description="路由键")


class TaskEvent(BaseModel):
    """任务事件"""
    event_id: str = Field(..., description="事件ID")
    task_id: str = Field(..., description="任务ID")
    event_type: str = Field(..., description="事件类型")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="事件时间")
    data: Optional[Dict[str, Any]] = Field(None, description="事件数据")
    worker_id: Optional[str] = Field(None, description="工作者ID") 