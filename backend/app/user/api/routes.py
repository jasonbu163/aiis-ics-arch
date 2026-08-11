"""
文件路径: /backend/app/user/api/routes.py
功能描述: 用户模块路由汇聚
主要功能:
    - 汇聚认证路由
    - 汇聚用户管理路由
"""
from app.user.api.v1 import auth_router, users_router

__all__ = ["auth_router", "users_router"]

