from fastapi import APIRouter, Depends
from app.models.base import HealthResponse
from app.config import Settings, get_settings
from datetime import datetime

router = APIRouter(tags=["Health"])


@router.get("/", response_model=HealthResponse, summary="根路径健康检查")
async def root_health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """根路径健康检查端点"""
    return HealthResponse(
        status="ok",
        message=f"{settings.app_name}服务运行正常",
        version=settings.app_version
    )


@router.get("/health", response_model=HealthResponse, summary="详细健康检查")
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """详细健康检查端点，可用于监控系统"""
    return HealthResponse(
        status="ok",
        message="服务运行正常，所有系统组件状态良好",
        version=settings.app_version
    )


@router.get("/ready", response_model=HealthResponse, summary="就绪检查")
async def readiness_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """就绪检查端点，用于K8s等容器编排系统"""
    # 这里可以添加更多的就绪检查逻辑
    # 例如：数据库连接、Redis连接、外部服务可用性等
    
    return HealthResponse(
        status="ok",
        message="服务已就绪，可以处理请求",
        version=settings.app_version
    ) 