"""
文件路径: /backend/app/user/crud/async_token_blacklist.py
功能描述: Token 黑名单异步 CRUD 数据访问
主要功能:
    - 查询黑名单记录
    - 新增黑名单记录
    - 删除过期黑名单记录
"""
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.models.token_blacklist import TokenBlacklist


async def get_by_token(db: AsyncSession, token: str) -> TokenBlacklist | None:
    result = await db.execute(
        select(TokenBlacklist).where(TokenBlacklist.token == token)
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, token: str, expires_at: datetime) -> TokenBlacklist:
    blacklist_entry = TokenBlacklist(
        token=token,
        expires_at=expires_at,
    )
    db.add(blacklist_entry)
    await db.flush()
    await db.refresh(blacklist_entry)
    return blacklist_entry


async def remove_by_token(db: AsyncSession, token: str) -> None:
    await db.execute(
        delete(TokenBlacklist).where(TokenBlacklist.token == token)
    )


async def remove_expired_before(db: AsyncSession, before: datetime) -> None:
    await db.execute(
        delete(TokenBlacklist).where(TokenBlacklist.expires_at < before)
    )

