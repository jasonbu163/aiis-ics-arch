"""
文件路径: /backend/core/deps.py
功能描述: FastAPI 依赖注入模块
主要功能:
    - 数据库会话依赖
    - 用户认证依赖
    - 消费应用组合期有效角色权限并检查
"""
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from settings import settings
from core.security import verify_password
from database import get_db
from app.user.models.user import User

security = HTTPBearer()


def get_role_permissions(role: str, request: Request | None = None) -> list[str]:
    """消费本应用组合期策略；未建立策略或未知角色时拒绝授权。"""
    policy = getattr(request.app.state, "role_api_permissions", None) if request else None
    return sorted(policy.get(role, ())) if policy else []


def require_permissions(*required_permissions: str):
    """
    权限验证依赖工厂函数
    
    用法:
        @router.get("/users", dependencies=[Depends(require_permissions("system"))])
        async def list_users(): ...
    """
    async def permission_checker(
        request: Request,
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role == "admin":
            return current_user

        user_permissions = get_role_permissions(current_user.role, request)

        for perm in required_permissions:
            if perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要 {perm} 权限"
                )
        return current_user
    
    return permission_checker


async def get_current_user_with_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> tuple[User, str]:
    """获取当前用户和 token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token 已失效或已登出",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise credentials_exception

        from app.user.services.async_token_blacklist import TokenBlacklistService
        token_id = payload.get("jti") or token
        if await TokenBlacklistService.is_blacklisted(db, token_id):
            raise credentials_exception

        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user, token


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    user, _ = await get_current_user_with_token(credentials, db)
    return user


async def get_current_active_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前管理员用户"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user
