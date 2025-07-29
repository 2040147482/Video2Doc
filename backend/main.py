"""
Video2Doc 主应用入口
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.exceptions import create_error_response
from app.routers import health, video, processing, speech, image_recognition, summary, export, storage, queue, payments

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    Args:
        app: FastAPI应用实例
    """
    # 启动时执行
    logger.info("应用启动: Video2Doc API v1.0.0")
    
    # 创建必要的目录
    from pathlib import Path
    settings = get_settings()
    Path(settings.upload_dir).mkdir(exist_ok=True, parents=True)
    Path(settings.temp_dir).mkdir(exist_ok=True, parents=True)
    Path(settings.results_dir).mkdir(exist_ok=True, parents=True)
    
    yield
    
    # 关闭时执行
    logger.info("应用关闭")

# 创建应用
app = FastAPI(
    title="Video2Doc API",
    description="AI驱动的视频内容分析和文档生成平台",
    version="1.0.0",
    lifespan=lifespan
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    请求日志中间件
    
    Args:
        request: 请求对象
        call_next: 下一个处理函数
        
    Returns:
        响应对象
    """
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response

# 配置CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由 - 使用/api前缀
app.include_router(health.router, prefix="/api")
app.include_router(video.router, prefix="/api")
app.include_router(processing.router, prefix="/api")
app.include_router(speech.router, prefix="/api")
app.include_router(image_recognition.router, prefix="/api")
app.include_router(summary.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(storage.router, prefix="/api", tags=["存储管理"])
app.include_router(queue.router, prefix="/api", tags=["队列管理"])
app.include_router(payments.router, prefix="/api", tags=["支付管理"])

# 全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    请求验证异常处理
    
    Args:
        request: 请求对象
        exc: 异常对象
        
    Returns:
        错误响应
    """
    return create_error_response(
        status_code=422,
        message="请求参数验证失败",
        details=[{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()]
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """
    HTTP异常处理
    
    Args:
        request: 请求对象
        exc: 异常对象
        
    Returns:
        错误响应
    """
    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    通用异常处理
    
    Args:
        request: 请求对象
        exc: 异常对象
        
    Returns:
        错误响应
    """
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return create_error_response(
        status_code=500,
        message="服务器内部错误"
    )

# 直接运行应用（开发环境）
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 