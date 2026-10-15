"""
文件路径: /backend/app/plan/api/__init__.py
功能描述: 计划模块 API 包初始化
主要功能:
    - 导出计划管理路由
"""
from app.plan.api.routes import router

__all__ = ["router"]
