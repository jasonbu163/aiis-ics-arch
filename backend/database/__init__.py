"""
文件路径: /backend/database/__init__.py
功能描述: 数据库层模块初始化
主要功能:
    - 提供统一的数据库访问接口
    - 分离异步和同步会话管理
    - 导出数据库组件

使用指南:
===========

1. FastAPI 路由（异步）：
   from database import get_db, Base
   from sqlalchemy.ext.asyncio import AsyncSession
   from fastapi import Depends

   @router.get("/items")
   async def get_items(db: AsyncSession = Depends(get_db)):
       result = await db.execute(select(Item))
       return result.scalars().all()

2. 后台同步业务入口：
   from database import get_sync_db_context, Base

   def process_data():
       with get_sync_db_context() as db:
           items = db.query(Item).all()
           # 处理数据...

3. 定义模型：
   from database import Base
   from sqlalchemy import Column, Integer, String

   class Item(Base):
       __tablename__ = "items"  # 可选，会自动生成
       id = Column(Integer, primary_key=True)
       name = Column(String(100))
"""
from database.base import Base, TimestampMixin, IntPk, Timestamp, UpdatedAt
from database.engine import async_engine, sync_engine, root_engine
from database.session_async import async_session_maker, get_db, get_db_session
from database.session_sync import SyncSessionLocal, create_sync_session, get_sync_db, get_sync_db_context

__all__ = [
    "Base",
    "TimestampMixin",
    "IntPk",
    "Timestamp",
    "UpdatedAt",
    "async_engine",
    "sync_engine",
    "root_engine",
    "async_session_maker",
    "get_db",
    "get_db_session",
    "SyncSessionLocal",
    "get_sync_db",
    "get_sync_db_context",
    "create_sync_session",
]
