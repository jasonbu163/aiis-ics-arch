"""
文件路径: /backend/app/dashboard/crud/async_dashboard.py
功能描述: Dashboard 异步 CRUD
主要功能:
    - 封装看板统计查询
    - 封装看板缓存表查询
    - 封装近期计划查询
"""
import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dashboard.models.dashboard import (
    DailyProductionStats,
    DowntimeRecord,
    ProductionStatusRecord,
    QualityGradeStats,
    TemperatureZoneRecord,
)
from app.plan.models import Plan


class DashboardCRUD:
    """Dashboard 数据库访问层。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_stats_by_date(self, stats_date: datetime.date):
        result = await self.db.execute(
            select(DailyProductionStats).where(DailyProductionStats.stats_date == stats_date)
        )
        return result.scalar_one_or_none()

    async def count_pending_plans(self) -> int:
        result = await self.db.execute(select(func.count(Plan.id)).where(Plan.status.in_(["planned", "preparing"])))
        return result.scalar() or 0

    async def list_daily_stats_from(self, start_date: datetime.date):
        result = await self.db.execute(
            select(DailyProductionStats)
            .where(DailyProductionStats.stats_date >= start_date)
            .order_by(DailyProductionStats.stats_date)
        )
        return result.scalars().all()

    async def list_daily_stats_between(self, start_date: datetime.date, end_date: datetime.date):
        result = await self.db.execute(
            select(DailyProductionStats)
            .where(and_(DailyProductionStats.stats_date >= start_date, DailyProductionStats.stats_date < end_date))
            .order_by(DailyProductionStats.stats_date)
        )
        return result.scalars().all()

    async def list_quality_grade_stats(self, stats_date: datetime.date):
        result = await self.db.execute(select(QualityGradeStats).where(QualityGradeStats.stats_date == stats_date))
        return result.scalars().all()

    async def list_temperature_records_from(self, start_time: datetime.datetime):
        result = await self.db.execute(
            select(TemperatureZoneRecord)
            .where(TemperatureZoneRecord.record_time >= start_time)
            .order_by(TemperatureZoneRecord.record_time)
        )
        return result.scalars().all()

    async def list_downtime_records(self, stats_date: datetime.date):
        result = await self.db.execute(
            select(DowntimeRecord)
            .where(DowntimeRecord.stats_date == stats_date)
            .order_by(DowntimeRecord.duration_minutes.desc())
        )
        return result.scalars().all()

    async def get_latest_production_status(self):
        result = await self.db.execute(
            select(ProductionStatusRecord).order_by(ProductionStatusRecord.record_time.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def list_recent_plans(self, limit: int = 5):
        result = await self.db.execute(select(Plan).order_by(Plan.created_at.desc()).limit(limit))
        return result.scalars().all()
