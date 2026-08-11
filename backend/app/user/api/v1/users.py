"""
文件路径: /backend/app/user/api/v1/users.py
功能描述: 用户管理 API 路由
主要功能:
    - 用户列表查询
    - 用户详情查询
    - 用户创建、更新和软删除
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.models.user import User
from app.user.schemas.user_in import UserCreate, UserPasswordReset, UserUpdate
from app.user.services.async_user import UserService
from common.response import SuccessResponse
from core.deps import require_permissions
from database import get_db

users_router = APIRouter(prefix="/users", tags=["User - Users"])


@users_router.get("", response_model=SuccessResponse)
async def get_user_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize", description="每页数量"),
    username: str | None = Query(None, description="用户名过滤"),
    role: str | None = Query(None, description="角色过滤"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("system")),
):
    """获取用户列表"""
    users, total = await UserService.get_page(db, page, page_size, username, role)

    return SuccessResponse(data={
        "items": [serialize_user(user) for user in users],
        "total": total,
        "page": page,
        "pageSize": page_size,
    })


@users_router.get("/{user_id}", response_model=SuccessResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("system")),
):
    """获取用户详情"""
    user = await UserService.get_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return SuccessResponse(data=serialize_user(user))


@users_router.post("", response_model=SuccessResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("system")),
):
    """创建用户"""
    user = await UserService.create(db, user_data, actor=current_user)
    return SuccessResponse(
        message="创建成功",
        data=serialize_user(user),
    )


@users_router.put("/{user_id}", response_model=SuccessResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("system")),
):
    """更新用户"""
    user = await UserService.update(db, user_id, user_data, actor=current_user)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return SuccessResponse(
        message="更新成功",
        data=serialize_user(user),
    )


@users_router.patch("/{user_id}/password", response_model=SuccessResponse)
async def reset_user_password(
    user_id: int,
    password_data: UserPasswordReset,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("system")),
):
    """重置目标用户密码"""
    result = await UserService.reset_password(db, user_id, password_data, actor=current_user)
    if not result:
        raise HTTPException(status_code=404, detail="用户不存在")

    return SuccessResponse(message="重置成功", data=result)


@users_router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("system")),
):
    """删除用户（软删除）"""
    deleted = await UserService.delete(db, user_id, actor=current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="用户不存在")

    return SuccessResponse(message="删除成功")


def serialize_user(user: User) -> dict:
    """将用户 ORM 对象序列化为前端消费的 camelCase 结构。"""
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "role": user.role,
        "phone": user.phone,
        "email": user.email,
        "isActive": user.is_active,
        "status": "active" if user.is_active else "inactive",
        "createdAt": user.created_at.isoformat() if user.created_at else None,
        "updatedAt": user.updated_at.isoformat() if user.updated_at else None,
    }
