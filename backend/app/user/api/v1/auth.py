"""
文件路径: /backend/app/user/api/v1/auth.py
功能描述: 用户认证 API 路由
主要功能:
    - 用户登录
    - 用户登出
    - 获取当前用户信息
    - 刷新访问令牌
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.models.user import User
from app.user.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    SelfProfileUpdate,
)
from app.user.schemas.user_out import UserResponse
from app.user.services.async_token_blacklist import TokenBlacklistService
from app.user.services.async_user import UserService
from common.response import SuccessResponse
from core.deps import get_current_user, get_current_user_with_token
from core.jwt import create_access_token, create_refresh_token, decode_token
from database import get_db
from settings import settings

auth_router = APIRouter(prefix="/auth", tags=["User - Auth"])


def _expires_at_from_payload(payload: dict, fallback_hours: int = 2) -> datetime:
    exp = payload.get("exp")
    if exp:
        return datetime.fromtimestamp(exp)
    return datetime.now() + timedelta(hours=fallback_hours)


@auth_router.post("/login", response_model=SuccessResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """用户登录，获取访问令牌"""
    user = await UserService.authenticate(
        db,
        login_data.username,
        login_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return SuccessResponse(
        message="登录成功",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "role": user.role,
            },
        },
    )


@auth_router.post("/logout", response_model=SuccessResponse)
async def logout(
    logout_data: LogoutRequest | None = Body(default=None),
    db: AsyncSession = Depends(get_db),
    token_data: tuple[User, str] = Depends(get_current_user_with_token),
):
    """用户登出"""
    _user, token = token_data

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的 token")

    token_id = payload.get("jti") or token
    await TokenBlacklistService.add_to_blacklist(
        db,
        token_id,
        _expires_at_from_payload(payload),
    )

    if logout_data and logout_data.refresh_token:
        refresh_payload = decode_token(logout_data.refresh_token)
        if not refresh_payload or refresh_payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="无效的 refresh_token")

        refresh_token_id = refresh_payload.get("jti") or logout_data.refresh_token
        await TokenBlacklistService.add_to_blacklist(
            db,
            refresh_token_id,
            _expires_at_from_payload(refresh_payload),
        )

    return SuccessResponse(message="登出成功")


@auth_router.get("/me", response_model=SuccessResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """获取当前用户信息"""
    return SuccessResponse(
        message="获取成功",
        data={
            "id": current_user.id,
            "username": current_user.username,
            "name": current_user.name,
            "role": current_user.role,
            "phone": current_user.phone,
            "email": current_user.email,
            "is_active": current_user.is_active,
            "status": "active" if current_user.is_active else "inactive",
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        },
    )


@auth_router.patch("/me", response_model=SuccessResponse)
async def update_current_user_profile(
    profile_data: SelfProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新当前用户自己的基础资料"""
    user = await UserService.update_self_profile(db, current_user, profile_data)
    return SuccessResponse(
        message="更新成功",
        data={
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": user.role,
            "phone": user.phone,
            "email": user.email,
            "is_active": user.is_active,
            "status": "active" if user.is_active else "inactive",
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
    )


@auth_router.patch("/me/password", response_model=SuccessResponse)
async def change_current_user_password(
    password_data: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """当前用户修改自己的密码"""
    result = await UserService.change_own_password(db, current_user, password_data)
    return SuccessResponse(message="修改成功", data=result)


@auth_router.post("/refresh", response_model=SuccessResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """刷新访问令牌"""
    refresh_token_value = refresh_data.refresh_token

    payload = decode_token(refresh_token_value)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的 refresh_token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="无效的 refresh_token")

    token_id = payload.get("jti") or refresh_token_value
    if await TokenBlacklistService.is_blacklisted(db, token_id):
        raise HTTPException(status_code=401, detail="无效的 refresh_token")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="无效的 refresh_token")

    user = await UserService.get_by_username(db, username)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")

    new_access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.username},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return SuccessResponse(
        message="刷新成功",
        data={
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        },
    )
