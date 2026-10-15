"""
文件路径: /backend/app/quality/api/__init__.py
功能描述: 质量模块 API 导出
主要功能:
    - 导出质量检验路由与缺陷记录路由
"""
from app.quality.api.routes import defect_router, router

__all__ = ["router", "defect_router"]
