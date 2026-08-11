"""
文件路径: /backend/database/engine.py
功能描述: 数据库引擎配置
主要功能:
    - 提供异步数据库引擎（用于 FastAPI）
    - 提供同步数据库引擎（用于 Alembic、投影与维护任务）
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

from settings import settings


def _engine_options() -> dict:
    options = {
        "echo": False,
        "pool_pre_ping": True,
    }
    if settings.primary_database != "sqlite":
        options.update(
            pool_size=5,
            max_overflow=10,
        )
    return options


async_engine = create_async_engine(
    settings.DATABASE_URL,
    **_engine_options(),
)

sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    **_engine_options(),
)

root_engine = None
if settings.MYSQL_ENABLED:
    root_engine = create_engine(
        settings.ROOT_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

__all__ = [
    "async_engine",
    "sync_engine",
    "root_engine",
]
