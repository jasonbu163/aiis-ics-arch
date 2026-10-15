"""
文件路径: /backend/app/equipment/api/__init__.py
功能描述: 设备模块 API 导出
主要功能:
    - 导出设备看板路由
"""
from app.equipment.api.routes import router

__all__ = ["router"]
