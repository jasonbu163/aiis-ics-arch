"""
文件路径: /backend/app/user/services/async_token_blacklist.py
功能描述: Token 黑名单异步业务服务
主要功能:
    - 将 Token 标识加入黑名单
    - 检查 Token 标识是否在黑名单中
    - 清理过期黑名单记录
"""
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.user.crud import async_token_blacklist as token_blacklist_crud
from app.user.models.token_blacklist import TokenBlacklist


def _now_like(value: datetime) -> datetime:
    """返回与数据库时间值同 naive/aware 形态的当前时间。"""
    return datetime.now(value.tzinfo) if value.tzinfo else datetime.now()


class TokenBlacklistService:
    """Token 黑名单服务"""

    @staticmethod
    async def add_to_blacklist(db: AsyncSession, token: str, expires_at: datetime) -> TokenBlacklist:
        """将 Token 标识加入黑名单"""
        existing = await token_blacklist_crud.get_by_token(db, token)
        if existing:
            return existing

        return await token_blacklist_crud.create(db, token, expires_at)

    @staticmethod
    async def is_blacklisted(db: AsyncSession, token: str) -> bool:
        """检查 Token 标识是否在黑名单中"""
        entry = await token_blacklist_crud.get_by_token(db, token)

        if not entry:
            return False

        if entry.expires_at < _now_like(entry.expires_at):
            await TokenBlacklistService.remove_expired(db, token)
            return False

        return True

    @staticmethod
    async def remove_expired(db: AsyncSession, token: str | None = None):
        """删除过期的黑名单记录"""
        if token:
            await token_blacklist_crud.remove_by_token(db, token)
        else:
            await token_blacklist_crud.remove_expired_before(db, datetime.now())

        await db.flush()

