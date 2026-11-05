"""
文件路径: /backend/app/performance/crud/async_performance.py
功能描述: 实绩管理异步 CRUD
主要功能:
    - 封装实绩 CRUD 查询和写入
    - 封装过程数据查询和写入
    - 封装下推记录查询和写入
"""
from typing import Any

from sqlalchemy import and_, func as sql_func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.performance.models.performance import (
    Performance,
    ProcessSpeed,
    ProcessTemperature,
    ProcessTension,
    PushDownRecord,
)


from app.performance.crud.async_integration import storage_context
from common.integration.storage import to_storage_time as storage_time


class PerformanceCRUD:
    """实绩管理数据库访问层。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def build_list_query(
        self,
        coil_no: str | None,
        grade: str | None,
        observation_status: str | None,
        start_date,
        end_date,
    ):
        query = select(Performance).options(selectinload(Performance.plan))
        conditions = [Performance.equipment_id.is_(None)]

        if coil_no:
            conditions.append(Performance.coil_no.ilike(f"%{coil_no}%"))
        if grade:
            conditions.append(Performance.grade.ilike(f"%{grade}%"))
        if observation_status:
            if observation_status == "manual_historical":
                conditions.append(Performance.observation_status.is_(None))
            else:
                conditions.append(Performance.observation_status == observation_status)
        if start_date:
            conditions.append(Performance.production_date >= start_date)
        if end_date:
            conditions.append(Performance.production_date <= end_date)
        if conditions:
            query = query.where(and_(*conditions))

        return query

    async def list_performances(
        self,
        page: int,
        page_size: int,
        coil_no: str | None,
        grade: str | None,
        observation_status: str | None,
        start_date,
        end_date,
    ):
        context=await storage_context(self.db)
        query = self.build_list_query(coil_no, grade, observation_status, start_date, end_date)

        count_query = select(sql_func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Performance.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)

        return result.scalars().all(), total

    async def get_performance(self, performance_id: int):
        context=await storage_context(self.db)
        query = select(Performance).options(
            selectinload(Performance.plan),
            selectinload(Performance.temperature_records),
            selectinload(Performance.tension_records),
            selectinload(Performance.speed_records),
        ).where(Performance.id == performance_id, Performance.equipment_id.is_(None)).with_for_update()

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_performance(self, performance: Performance) -> Performance:
        context=await storage_context(self.db)
        if context:
            performance.created_at=storage_time(context[1])
            performance.updated_at=storage_time(context[1])
        self.db.add(performance)
        await self.db.commit()
        await self.db.refresh(performance)
        return performance

    async def save_performance(self, performance: Performance) -> Performance:
        context=await storage_context(self.db)
        if context:
            performance.updated_at=storage_time(context[1])
        await self.db.commit()
        await self.db.refresh(performance)
        return performance

    async def delete_performance(self, performance: Performance) -> None:
        context=await storage_context(self.db)
        await self.db.delete(performance)
        await self.db.commit()

    async def list_temperature_records(self, performance_id: int):
        context=await storage_context(self.db)
        result = await self.db.execute(
            select(ProcessTemperature)
            .where(ProcessTemperature.performance_id == performance_id, ProcessTemperature.equipment_id.is_(None))
            .order_by(ProcessTemperature.record_time)
        )
        return result.scalars().all()

    async def list_tension_records(self, performance_id: int):
        context=await storage_context(self.db)
        result = await self.db.execute(
            select(ProcessTension)
            .where(ProcessTension.performance_id == performance_id, ProcessTension.equipment_id.is_(None))
            .order_by(ProcessTension.record_time)
        )
        return result.scalars().all()

    async def list_speed_records(self, performance_id: int):
        context=await storage_context(self.db)
        result = await self.db.execute(
            select(ProcessSpeed)
            .where(ProcessSpeed.performance_id == performance_id, ProcessSpeed.equipment_id.is_(None))
            .order_by(ProcessSpeed.record_time)
        )
        return result.scalars().all()

    async def create_record(self, record: Any):
        context=await storage_context(self.db)
        if context and getattr(record,"__tablename__",None) in ("performance_process_temperature","performance_process_tension","performance_process_speed"):
            record.record_time=storage_time(record.record_time,context[0]["basisProfile"]["legacyNaive"]) if record.record_time is not None else storage_time(context[1])
            record.created_at=storage_time(context[1])
            record.updated_at=storage_time(context[1])
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def create_push_down_records(self, records: list[PushDownRecord]) -> list[PushDownRecord]:
        context=await storage_context(self.db)
        for record in records:
            self.db.add(record)

        await self.db.commit()
        for record in records:
            await self.db.refresh(record)

        return records

    async def list_push_down_records(self, performance_id: int):
        context=await storage_context(self.db)
        result = await self.db.execute(
            select(PushDownRecord)
            .where(PushDownRecord.performance_id == performance_id)
            .order_by(PushDownRecord.created_at.desc())
        )
        return result.scalars().all()
