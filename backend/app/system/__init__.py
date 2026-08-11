"""
文件路径: /backend/app/system/__init__.py
功能描述: 系统字典模块初始化文件
主要功能:
    - 导出字典相关路由
"""
from app.system.api import dict_item_router, router

__all__ = ["router", "dict_item_router"]
