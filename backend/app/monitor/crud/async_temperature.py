"""
文件路径: /backend/app/monitor/crud/async_temperature.py
功能描述: Monitor 过程曲线持久化访问
主要功能:
    - 按日期查询与计数过程曲线
    - 添加过程曲线样例行但不提交事务
"""
from datetime import datetime, timedelta
from app.monitor.crud.async_integration import storage_context
from common.integration.storage import to_storage_time as storage_time

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.monitor.models.business_history import HistoryProcessCurve


async def list_curves_by_date(
    db: AsyncSession,
    date_str: str,
) -> list[HistoryProcessCurve]:
    context=await storage_context(db)
    if context:
        start=storage_time(datetime.fromisoformat(date_str),context[0]["basisProfile"]["systemWire"])
        return list((await db.execute(select(HistoryProcessCurve).where(HistoryProcessCurve.equipment_id.is_(None),HistoryProcessCurve.created_at>=start,HistoryProcessCurve.created_at<start+timedelta(days=1)).order_by(HistoryProcessCurve.created_at))).scalars().all())
    result = await db.execute(
        select(HistoryProcessCurve)
        .where(HistoryProcessCurve.equipment_id.is_(None), func.date(HistoryProcessCurve.created_at) == date_str)
        .order_by(HistoryProcessCurve.created_at)
    )
    return list(result.scalars().all())


async def count_curves_by_date(db: AsyncSession, date_str: str) -> int:
    context=await storage_context(db)
    if context:
        start=storage_time(datetime.fromisoformat(date_str),context[0]["basisProfile"]["systemWire"])
        return int((await db.scalar(select(func.count()).select_from(HistoryProcessCurve).where(HistoryProcessCurve.equipment_id.is_(None),HistoryProcessCurve.created_at>=start,HistoryProcessCurve.created_at<start+timedelta(days=1)))) or 0)
    value = await db.scalar(
        select(func.count()).select_from(HistoryProcessCurve).where(
            HistoryProcessCurve.equipment_id.is_(None), func.date(HistoryProcessCurve.created_at) == date_str
        )
    )
    return int(value or 0)


def add_curve_sample(
    db: AsyncSession,
    *,
    device_id: int,
    coil_number: str,
    created_at: datetime,
    values: dict,
) -> None:
    db.add(
        HistoryProcessCurve(
            device_id=device_id,
            coil_number=coil_number,
            created_at=created_at,
            **values,
        )
    )
