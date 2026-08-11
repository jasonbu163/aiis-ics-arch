"""
文件路径: /backend/app/user/api/v1/__init__.py
功能描述: 用户模块 v1 API 导出
主要功能:
    - 导出认证路由
    - 导出用户管理路由
"""
from app.user.api.v1.auth import auth_router
from app.user.api.v1.users import users_router

__all__ = ["auth_router", "users_router"]

