"""
文件路径: /backend/app/energy/api/__init__.py
功能描述: 能耗模块 API 导出
主要功能:
    - 导出能耗模块路由
"""
from app.energy.api.routes import router

__all__ = ["router"]
