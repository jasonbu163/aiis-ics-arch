"""
文件路径: /backend/app/reports/crud/async_efficiency.py
功能描述: 报表效率统计异步 CRUD
主要功能:
    - 查询实绩统计数据集
    - 查询停机记录统计数据集
"""
import datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auxiliary.models import StopRecord
from app.performance.models import Performance
from common.data_keys import PerformanceRecordSource


class EfficiencyCRUD:
    """效率统计数据库访问层。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_performances(self, start_dt: datetime.datetime, end_dt: datetime.datetime):
        start_day = start_dt.date()
        end_day = end_dt.date()
        result = await self.db.execute(
            select(Performance)
            .where(
                and_(
                    Performance.production_date >= start_day,
                    Performance.production_date <= end_day,
                    or_(
                        Performance.record_source.is_(None),
                        Performance.record_source
                        != PerformanceRecordSource.UNPLANNED_PLC.value,
                    ),
                )
            )
            .order_by(Performance.production_date.asc())
        )
        return result.scalars().all()

    async def list_stop_records(self, start_dt: datetime.datetime, end_dt: datetime.datetime):
        result = await self.db.execute(
            select(StopRecord)
            .where(
                and_(
                    StopRecord.start_time <= end_dt,
                    func.coalesce(StopRecord.end_time, StopRecord.start_time) >= start_dt,
                )
            )
            .order_by(StopRecord.start_time.asc())
        )
        return result.scalars().all()
