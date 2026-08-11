"""
文件路径: /backend/app/monitor/crud/async_realtime.py
功能描述: Control Agent latest facts 异步持久化访问
主要功能:
    - 按设备查询 PLC DB-block latest facts
    - 固定 PLC、DB 号与 group 名的合并顺序
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.monitor.models.monitor import PlcDbBlockLatestSnapshot


async def list_latest_snapshots(
    db: AsyncSession,
    device_id: int,
) -> list[PlcDbBlockLatestSnapshot]:
    result = await db.scalars(
        select(PlcDbBlockLatestSnapshot)
        .where(PlcDbBlockLatestSnapshot.device_id == device_id)
        .order_by(
            PlcDbBlockLatestSnapshot.plc_key.asc(),
            PlcDbBlockLatestSnapshot.db_number.asc(),
            PlcDbBlockLatestSnapshot.group_name.asc(),
            PlcDbBlockLatestSnapshot.id.asc(),
        )
    )
    return list(result.all())
