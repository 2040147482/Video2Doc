from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import os
from datetime import datetime

# 导入应用模块
from app.config import settings
from app.routers import health, video
from app.exceptions import create_error_response
from app.models import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print(f"🚀 {settings.app_name} v{settings.app_version} 正在启动...")
    
    # 创建必要的目录
    os.makedirs(settings.upload_folder, exist_ok=True)
    os.makedirs(settings.temp_folder, exist_ok=True)
    
    print(f"📁 上传目录: {settings.upload_folder}")
    print(f"📁 临时目录: {settings.temp_folder}")
    print(f"🌐 CORS 允许的源: {settings.cors_origins}")
    
    yield
    
    # 关闭时执行
    print(f"🛑 {settings.app_name} 正在关闭...")


# 创建FastAPI应用实例
def create_app() -> FastAPI:
    """创建并配置FastAPI应用"""
    
    app = FastAPI(
        title=settings.app_name,
        description="一个在线AI工具平台，用户上传视频或粘贴视频链接后，AI自动识别视频中的语音与图像内容，并将其结构化生成为可编辑、可导出的文档格式",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        debug=settings.debug
    )
    
    # 配置CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(health.router)
    app.include_router(video.router)
    
    return app


# 创建应用实例
app = create_app()


# 全局异常处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证异常"""
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            error_type="validation_error",
            message="请求参数验证失败",
            details=str(exc)
        )
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """处理404错误"""
    return JSONResponse(
        status_code=404,
        content=create_error_response(
            error_type="not_found",
            message="请求的资源不存在",
            details=f"路径 {request.url.path} 未找到"
        )
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """处理500错误"""
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            error_type="internal_error",
            message="服务器内部错误",
            details="请稍后重试或联系技术支持"
        )
    )


# 中间件：请求日志
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = datetime.now()
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = (datetime.now() - start_time).total_seconds()
    
    # 记录日志（生产环境应使用专业的日志库）
    if settings.debug:
        print(f"📝 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    # 添加处理时间到响应头
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    ) 