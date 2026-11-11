"""
文件路径: /backend/core/registrar.py
功能描述: FastAPI 应用注册器
主要功能:
    - 集中管理 FastAPI 应用初始化逻辑
    - 注册中间件（CORS、错误处理等）
    - 自动注册路由模块
    - 在应用组合期建立角色权限策略
    - 应用生命周期管理
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from common.log import logger, log_event
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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    try:
        yield
    finally:
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
    from app.module_registry import get_module_manifests
    from core.role_permissions import build_role_api_permissions

    policy = build_role_api_permissions(
        settings.SUPERVISOR_API_PERMISSIONS_JSON,
        settings.OPERATOR_API_PERMISSIONS_JSON,
        get_module_manifests(),
        legacy_present=settings.legacy_role_api_permissions_present,
        warn=lambda **fields: log_event("WARNING", "backend.role_api_permission_ignored", **fields),
    )
    is_testing = settings.TESTING if testing is None else testing

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        lifespan=lifespan,
    )
    app.state.role_api_permissions = policy
    app.state.testing = is_testing
    register_middleware(app)
    register_exception_handlers(app)
    register_routers(app)
    register_health_endpoints(app)
    from app.module_preflight import check_routes
    check_routes(app)
    
    return app
