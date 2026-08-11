"""
文件路径: /backend/app/monitor/crud/async_collector.py
功能描述: Monitor collector 状态异步持久化访问
主要功能:
    - 为 FastAPI 查询 collector state
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.monitor.models.monitor import MonitorCollectorState


async def get_state_async(
    db: AsyncSession,
    collector_key: str,
) -> MonitorCollectorState | None:
    return await db.get(MonitorCollectorState, collector_key)
