"""
文件路径: /backend/core/registrar.py
功能描述: FastAPI 应用注册器
主要功能:
    - 集中管理 FastAPI 应用初始化逻辑
    - 注册中间件（CORS、错误处理等）
    - 自动注册路由模块
    - 在应用组合期注册 Projection handler 与点位 catalog
    - 应用生命周期管理
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from common.log import logger
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from settings import settings
from database import async_engine, sync_engine
from common.exceptions import BusinessException
from common.response import ErrorResponse



def register_middleware(app: FastAPI) -> None:
    """注册中间件"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_exception_handlers(app: FastAPI) -> None:
    """注册异常处理器"""

    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        return JSONResponse(
            status_code=200,
            content={
                "code": exc.code,
                "message": exc.message,
                "data": None,
                "errorCode": exc.error_code.value,
            },
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.opt(exception=exc).error("请求错误 - Path: {}", request.url.path)
        
        detail = str(exc) if settings.DEBUG else "服务器内部错误，请稍后重试"
        
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                code=500,
                message="服务器内部错误",
                detail=detail
            ).model_dump()
        )


def register_routers(app: FastAPI) -> None:
    """注册路由"""
    from app.router import router
    app.include_router(router, prefix=settings.API_V1_PREFIX)


def register_projection_control_plane(app: FastAPI) -> None:
    """Build read-only Projection catalogs once during application composition."""
    from projection.policy_catalog import load_snapshot_policy_catalog
    from projection.registry import build_projection_registry

    app.state.projection_registry = build_projection_registry()
    app.state.snapshot_policy_catalog = load_snapshot_policy_catalog()


def build_projection_runtime(app: FastAPI):
    """Compose the first headless raw Projection runtime from app-owned catalogs."""
    from projection.runner import ProjectionRunner
    from projection.runtime import ProjectionRuntime

    runner = ProjectionRunner(
        registry=app.state.projection_registry,
        catalog=app.state.snapshot_policy_catalog,
        batch_size=settings.PROJECTION_RUNNER_BATCH_SIZE,
    )
    return ProjectionRuntime(
        runner=runner,
        interval_seconds=settings.PROJECTION_RUNNER_INTERVAL_SECONDS,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    runtime = None
    try:
        if app.state.projection_runtime_enabled:
            runtime = build_projection_runtime(app)
            runtime.start()
            app.state.projection_runtime = runtime
        yield
    finally:
        if runtime is not None:
            await runtime.stop()
        await cleanup()


async def cleanup() -> None:
    """清理资源"""
    await async_engine.dispose()
    sync_engine.dispose()


def register_health_endpoints(app: FastAPI) -> None:
    """注册健康检查端点"""
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": int(time.time() * 1000),
            "version": settings.APP_VERSION
        }
    
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": settings.APP_DESCRIPTION,
            "docs": "/docs",
            "health": "/health"
        }


def create_app(testing: bool | None = None) -> FastAPI:
    """创建 FastAPI 应用"""
    is_testing = settings.TESTING if testing is None else testing

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        lifespan=lifespan,
    )
    app.state.testing = is_testing
    app.state.projection_runtime_enabled = (
        not is_testing and settings.PROJECTION_RUNNER_ENABLED
    )
    app.state.projection_runtime = None
    register_projection_control_plane(app)
    
    register_middleware(app)
    register_exception_handlers(app)
    register_routers(app)
    register_health_endpoints(app)
    
    return app
