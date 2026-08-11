"""
文件路径: /backend/database/session_sync.py
功能描述: 后台同步业务通道数据库会话
主要功能:
    - 提供同步会话工厂
    - 提供上下文管理器
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from database.engine import sync_engine


SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    expire_on_commit=False,
    autoflush=False,
)


def get_sync_db() -> Generator[Session, None, None]:
    """
    获取同步数据库会话（用于 projection、维护任务等同步业务入口）

    使用方式:
        def sync_job():
            db = next(get_sync_db())
            try:
                # 执行数据库操作
                db.commit()
            except Exception:
                db.rollback()
                raise

    Yields:
        Session: 同步数据库会话对象
    """
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_sync_db_context() -> Generator[Session, None, None]:
    """
    获取同步数据库会话上下文管理器

    使用方式:
        def sync_job():
            with get_sync_db_context() as db:
                # 执行数据库操作
                # 自动 commit/rollback/close

    Yields:
        Session: 同步数据库会话对象
    """
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_sync_session() -> Session:
    """
    创建新的同步数据库会话

    注意：调用者需要手动管理 commit/rollback/close

    使用方式:
        db = create_sync_session()
        try:
            # 执行数据库操作
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    Returns:
        Session: 同步数据库会话对象
    """
    return SyncSessionLocal()


__all__ = [
    "SyncSessionLocal",
    "get_sync_db",
    "get_sync_db_context",
    "create_sync_session",
]
