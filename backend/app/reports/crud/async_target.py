"""
文件路径: /backend/app/reports/crud/async_target.py
功能描述: 目标设定异步 CRUD
主要功能:
    - 查询、创建、更新和删除目标
    - 查询目标达成率所需实绩数据
"""
import datetime

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.data_keys import period_type_storage_values, target_type_storage_values
from app.performance.models import Performance
from app.reports.models.reports import PerformanceTarget


class TargetCRUD:
    """目标设定数据库访问层。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def build_list_query(self, target_type: str | None, period_type: str | None):
        query = select(PerformanceTarget).order_by(desc(PerformanceTarget.created_at))
        if target_type:
            query = query.where(PerformanceTarget.target_type.in_(target_type_storage_values(target_type)))
        if period_type:
            query = query.where(PerformanceTarget.period_type.in_(period_type_storage_values(period_type)))
        return query

    async def list_targets(self, page: int, page_size: int, target_type: str | None, period_type: str | None):
        query = self.build_list_query(target_type, period_type)
        result = await self.db.execute(query.offset((page - 1) * page_size).limit(page_size))
        return result.scalars().all()

    async def count_all_targets(self) -> int:
        result = await self.db.execute(select(func.count(PerformanceTarget.id)))
        return result.scalar() or 0

    async def create_target(self, target: PerformanceTarget) -> PerformanceTarget:
        self.db.add(target)
        await self.db.commit()
        await self.db.refresh(target)
        return target

    async def get_target(self, target_id: int):
        result = await self.db.execute(select(PerformanceTarget).where(PerformanceTarget.id == target_id))
        return result.scalar_one_or_none()

    async def save_target(self, target: PerformanceTarget) -> PerformanceTarget:
        await self.db.commit()
        await self.db.refresh(target)
        return target

    async def delete_target(self, target: PerformanceTarget) -> None:
        await self.db.delete(target)
        await self.db.commit()

    async def list_performances_between(self, start_date: datetime.date, end_date: datetime.date):
        result = await self.db.execute(
            select(Performance).where(
                and_(
                    Performance.production_date >= start_date,
                    Performance.production_date <= end_date,
                )
            )
        )
        return result.scalars().all()
