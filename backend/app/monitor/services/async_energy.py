"""
文件路径: /backend/app/monitor/services/async_energy.py
功能描述: Monitor 能耗统计查询 Service
主要功能:
    - 查询当天与当月能耗汇总
    - 按时间范围组装能耗趋势
    - 普通查询不生成或写入样本
"""
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.monitor.crud import async_energy as energy_crud


async def get_energy_summary_data(db: AsyncSession, time_range: str) -> Dict[str, Any]:
    """获取能耗统计汇总数据。"""
    now = datetime.now()
    today_elect, today_n2 = await energy_crud.get_day_totals(db, now.date())
    month_elect, month_n2 = await energy_crud.get_month_totals(db, now.year, now.month)

    trend_records = await get_energy_trend_records(db, time_range)
    return {
        "todayTotal": {"elect": today_elect or 0, "n2": today_n2 or 0},
        "monthTotal": {"elect": month_elect or 0, "n2": month_n2 or 0},
        "currentPower": trend_records[-1]["elect"] if trend_records else 0,
        "trends": trend_records,
    }


async def get_energy_trend_records(db: AsyncSession, time_range: str) -> list[dict[str, Any]]:
    """按前端时间范围返回能耗趋势数据。"""
    range_key = (time_range or "realtime").lower()

    if range_key == "day":
        now = datetime.now()
        result = await energy_crud.list_daily_totals(
            db,
            year=now.year,
            month=now.month,
        )
        return [
            {"time": row.time_key.strftime("%m/%d"), "elect": row.elect or 0, "n2": row.n2 or 0}
            for row in result
        ]

    if range_key == "hour":
        today = datetime.now().date()
        result = await energy_crud.list_hourly_totals(db, today)
        return [
            {"time": f"{int(row.time_key):02d}:00", "elect": row.elect or 0, "n2": row.n2 or 0}
            for row in result
        ]

    records = await energy_crud.list_latest_process_curves(db, limit=20)
    return [
        {
            "time": record.created_at.strftime("%H:%M"),
            "elect": record.elect_consum,
            "n2": record.n2_total,
        }
        for record in reversed(records)
    ]
