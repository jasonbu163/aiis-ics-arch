"""
文件路径: /backend/app/performance/api/__init__.py
功能描述: 实绩管理 API 导出
主要功能:
    - 导出实绩路由
    - 导出分卷路由
"""
from app.performance.api.routes import router
from app.performance.api.split_routes import router as split_router

__all__ = ["router", "split_router"]
