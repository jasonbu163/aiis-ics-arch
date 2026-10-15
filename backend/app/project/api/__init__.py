"""
文件路径: /backend/app/project/api/__init__.py
功能描述: 项目模块 API 导出
主要功能:
    - 导出项目模块路由
"""
from app.project.api.routes import router

__all__ = ["router"]
