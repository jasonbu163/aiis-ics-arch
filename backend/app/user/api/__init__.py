"""
文件路径: /backend/app/user/api/__init__.py
功能描述: 用户 API 包初始化
主要功能:
    - 导出认证路由
    - 导出用户管理路由
"""
from app.user.api.routes import auth_router, users_router

__all__ = ["auth_router", "users_router"]
