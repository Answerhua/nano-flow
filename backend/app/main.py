"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from .config import settings
from .api.v1 import generate

# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO" if not settings.APP_DEBUG else "DEBUG"
)

# 创建 FastAPI 应用
app = FastAPI(
    title="Nano Flow API",
    description="可爱风格流程图生成 API",
    version="1.0.0",
    debug=settings.APP_DEBUG
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(generate.router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Nano Flow API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查配置
        config_ok = bool(settings.QWEN_API_KEY and settings.GRSAI_API_KEY)
        
        return {
            "status": "healthy" if config_ok else "degraded",
            "config": {
                "qwen_configured": bool(settings.QWEN_API_KEY),
                "grsai_configured": bool(settings.GRSAI_API_KEY)
            },
            "environment": settings.APP_ENV
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("=" * 60)
    logger.info("🚀 Nano Flow API Starting...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug Mode: {settings.APP_DEBUG}")
    logger.info(f"Host: {settings.APP_HOST}:{settings.APP_PORT}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Shutting down Nano Flow API...")


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.APP_DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        log_level="info"
    )
