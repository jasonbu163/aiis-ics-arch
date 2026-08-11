"""
文件路径: /backend/app/user/crud/async_user.py
功能描述: 用户异步 CRUD 数据访问
主要功能:
    - 按用户名查询用户
    - 按 ID 查询用户
    - 创建、更新、软删除用户
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.models.user import User


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return list(result.scalars().all())


async def get_page(
    db: AsyncSession,
    page: int,
    page_size: int,
    username: str | None = None,
    role: str | None = None,
) -> tuple[list[User], int]:
    query = select(User)
    count_query = select(func.count(User.id))

    if username:
        query = query.where(User.username.ilike(f"%{username}%"))
        count_query = count_query.where(User.username.ilike(f"%{username}%"))
    if role:
        query = query.where(User.role == role)
        count_query = count_query.where(User.role == role)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    return list(result.scalars().all()), total


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update(db: AsyncSession, user: User, update_data: dict) -> User:
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


async def soft_delete(db: AsyncSession, user: User) -> User:
    user.is_active = False
    await db.flush()
    return user
