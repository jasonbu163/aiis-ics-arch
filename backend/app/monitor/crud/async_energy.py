"""
文件路径: /backend/app/monitor/crud/async_energy.py
功能描述: Monitor 能耗持久化访问
主要功能:
    - 查询日月汇总与时间趋势
    - 添加能耗样例行但不提交事务
"""
from datetime import date, datetime
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.monitor.models.business_history import HistoryEnergyConsumption, HistoryProcessCurve


async def get_day_totals(db: AsyncSession, target_date: date) -> tuple[Any, Any]:
    result = await db.execute(
        select(
            func.sum(HistoryEnergyConsumption.elect_consum),
            func.sum(HistoryEnergyConsumption.n2_total),
        ).where(func.date(HistoryEnergyConsumption.created_at) == target_date)
    )
    return result.one()


async def get_month_totals(
    db: AsyncSession,
    year: int,
    month: int,
) -> tuple[Any, Any]:
    result = await db.execute(
        select(
            func.sum(HistoryEnergyConsumption.elect_consum),
            func.sum(HistoryEnergyConsumption.n2_total),
        ).where(
            func.extract("month", HistoryEnergyConsumption.created_at) == month,
            func.extract("year", HistoryEnergyConsumption.created_at) == year,
        )
    )
    return result.one()


async def list_daily_totals(
    db: AsyncSession,
    year: int,
    month: int,
) -> list[Any]:
    result = await db.execute(
        select(
            func.date(HistoryEnergyConsumption.created_at).label("time_key"),
            func.sum(HistoryEnergyConsumption.elect_consum).label("elect"),
            func.sum(HistoryEnergyConsumption.n2_total).label("n2"),
        )
        .where(
            func.extract("month", HistoryEnergyConsumption.created_at) == month,
            func.extract("year", HistoryEnergyConsumption.created_at) == year,
        )
        .group_by(func.date(HistoryEnergyConsumption.created_at))
        .order_by(func.date(HistoryEnergyConsumption.created_at))
    )
    return list(result)


async def list_hourly_totals(db: AsyncSession, target_date: date) -> list[Any]:
    result = await db.execute(
        select(
            func.hour(HistoryEnergyConsumption.created_at).label("time_key"),
            func.sum(HistoryEnergyConsumption.elect_consum).label("elect"),
            func.sum(HistoryEnergyConsumption.n2_total).label("n2"),
        )
        .where(func.date(HistoryEnergyConsumption.created_at) == target_date)
        .group_by(func.hour(HistoryEnergyConsumption.created_at))
        .order_by(func.hour(HistoryEnergyConsumption.created_at))
    )
    return list(result)


async def list_latest_process_curves(
    db: AsyncSession,
    limit: int,
) -> list[HistoryProcessCurve]:
    result = await db.execute(
        select(HistoryProcessCurve)
        .order_by(desc(HistoryProcessCurve.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def count_energy_rows_by_date(db: AsyncSession, target_date: date) -> int:
    value = await db.scalar(
        select(func.count()).select_from(HistoryEnergyConsumption).where(
            func.date(HistoryEnergyConsumption.created_at) == target_date
        )
    )
    return int(value or 0)


def add_energy_sample(
    db: AsyncSession,
    *,
    device_id: int,
    coil_number: str,
    elect_consum: float,
    n2_total: float,
    created_at: datetime,
) -> None:
    db.add(
        HistoryEnergyConsumption(
            device_id=device_id,
            coil_number=coil_number,
            elect_consum=elect_consum,
            n2_total=n2_total,
            created_at=created_at,
        )
    )
