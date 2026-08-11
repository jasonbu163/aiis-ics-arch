"""
文件路径: /backend/app/user/schemas/auth.py
功能描述: 认证相关 Schema 定义
主要功能:
    - 登录请求
    - Token 响应
    - Refresh Token 请求
"""
from common.schema_base import ApiSchema


class LoginRequest(ApiSchema):
    username: str
    password: str


class TokenResponse(ApiSchema):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: dict


class RefreshTokenRequest(ApiSchema):
    refresh_token: str


class LogoutRequest(ApiSchema):
    refresh_token: str | None = None


class SelfProfileUpdate(ApiSchema):
    name: str | None = None
    phone: str | None = None
    email: str | None = None


class PasswordChangeRequest(ApiSchema):
    old_password: str | None = None
    new_password: str | None = None
