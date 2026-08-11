"""
文件路径: /backend/app/aiis_demo/api/__init__.py
功能描述: AIIS Demo API package 入口
主要功能:
    - 导出 AIIS Demo 参考路由
"""
from app.aiis_demo.api.routes import router


__all__ = ["router"]
