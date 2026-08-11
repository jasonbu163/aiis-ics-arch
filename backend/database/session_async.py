"""
文件路径: /backend/database/session_async.py
功能描述: FastAPI 异步数据库会话
主要功能:
    - 提供异步会话工厂
    - 提供依赖注入函数 get_db
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.engine import async_engine


async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话（用于 FastAPI 依赖注入）

    使用方式:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: 异步数据库会话对象
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """
    获取异步数据库会话（用于非依赖注入场景）

    使用方式:
        async with get_db_session() as session:
            result = await session.execute(query)

    Returns:
        AsyncSession: 异步数据库会话对象
    """
    return async_session_maker()


__all__ = [
    "async_session_maker",
    "get_db",
    "get_db_session",
]
