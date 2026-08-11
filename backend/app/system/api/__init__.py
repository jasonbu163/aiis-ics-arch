"""
文件路径: /backend/app/system/api/__init__.py
功能描述: 系统模块 API 包初始化
主要功能:
    - 导出系统字典相关路由
"""
from app.system.api.routes import dict_item_router, router

__all__ = ["router", "dict_item_router"]
