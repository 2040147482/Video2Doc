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
from app.routers import health, video
# 导入新的处理路由
from app.routers import processing
# 导入语音识别路由
from app.routers import speech
# 导入简化的语音识别路由（用于调试）
from app.routers import speech_simple
# 导入超级简化的语音识别路由（用于诊断）
from app.routers import speech_ultra_simple
# 导入图像识别路由
from app.routers import image_recognition

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
    # 启动前执行
    settings = get_settings()
    logger.info(f"应用启动: {settings.app_name} v{settings.app_version}")
    
    # 创建必要的目录
    from pathlib import Path
    Path(settings.upload_dir).mkdir(exist_ok=True, parents=True)
    Path(settings.temp_dir).mkdir(exist_ok=True, parents=True)
    Path(settings.results_dir).mkdir(exist_ok=True, parents=True)
    
    yield
    
    # 关闭时执行
    logger.info("应用关闭")

# 创建应用
app = FastAPI(
    title="Video2Doc API",
    description="视频内容AI分析工具API",
    version="0.1.0",
    lifespan=lifespan,
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

# 注册路由
app.include_router(health.router, prefix="/api")
app.include_router(video.router, prefix="/api")
# 添加新的处理路由
app.include_router(processing.router, prefix="/api")
# 添加语音识别路由
app.include_router(speech.router, prefix="/api")
# 添加简化的语音识别路由（用于调试）
app.include_router(speech_simple.router, prefix="/api")
# 添加超级简化的语音识别路由（用于诊断）
app.include_router(speech_ultra_simple.router, prefix="/api")
# 添加图像识别路由
app.include_router(image_recognition.router, prefix="/api")

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