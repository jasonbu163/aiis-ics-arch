"""
文件路径: /backend/app/auxiliary/crud/async_auxiliary.py
功能描述: 辅助管理异步 CRUD
主要功能:
    - 封装班组数据库读写
    - 封装班次数据库读写
    - 封装停机记录数据库读写
    - 封装排班规则数据库读写
"""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auxiliary.models.auxiliary import Shift, ShiftRule, ShiftTeam, StopRecord
from common.async_crud_base import BaseService


class AuxiliaryCRUD:
    """辅助管理数据库访问层。"""

    def __init__(self, db: AsyncSession):
        self.shift_teams = BaseService(db, ShiftTeam)
        self.shifts = BaseService(db, Shift)
        self.shift_rules = BaseService(db, ShiftRule)
        self.stop_records = BaseService(db, StopRecord)

    async def list_shift_teams(self, page: int, page_size: int):
        return await self.shift_teams.list(page=page, page_size=page_size)

    async def get_shift_team(self, id: int):
        return await self.shift_teams.get_by_id(id)

    async def create_shift_team(self, data: dict[str, Any]):
        return await self.shift_teams.create(data)

    async def update_shift_team(self, id: int, data: dict[str, Any]):
        return await self.shift_teams.update(id, data)

    async def delete_shift_team(self, id: int) -> bool:
        return await self.shift_teams.delete(id)

    async def list_shifts(
        self,
        page: int,
        page_size: int,
        team_id: int | None,
        start_date: Any | None = None,
        end_date: Any | None = None,
    ):
        conditions = []
        if team_id:
            conditions.append(Shift.team_id == team_id)
        if start_date:
            conditions.append(Shift.date >= start_date)
        if end_date:
            conditions.append(Shift.date <= end_date)

        query = select(Shift)
        count_query = select(func.count()).select_from(Shift)
        if conditions:
            query = query.where(*conditions)
            count_query = count_query.where(*conditions)

        query = query.order_by(Shift.date.asc()).offset((page - 1) * page_size).limit(page_size)
        items = (await self.shifts.db.execute(query)).scalars().all()
        total = (await self.shifts.db.execute(count_query)).scalar_one()
        return items, total

    async def get_shift(self, id: int):
        return await self.shifts.get_by_id(id)

    async def create_shift(self, data: dict[str, Any]):
        return await self.shifts.create(data)

    async def update_shift(self, id: int, data: dict[str, Any]):
        return await self.shifts.update(id, data)

    async def delete_shift(self, id: int) -> bool:
        return await self.shifts.delete(id)

    async def get_active_shift_rule(self):
        query = select(ShiftRule).where(ShiftRule.status == "active").order_by(ShiftRule.id.asc()).limit(1)
        return (await self.shift_rules.db.execute(query)).scalar_one_or_none()

    async def update_shift_rule(self, id: int, data: dict[str, Any]):
        return await self.shift_rules.update(id, data)

    async def list_stop_records(
        self,
        page: int,
        page_size: int,
        status: str | None,
        shift: str | None = None,
        start_time: Any | None = None,
        end_time: Any | None = None,
        stop_type: str | None = None,
    ):
        conditions = []
        if status:
            conditions.append(StopRecord.status == status)
        if shift:
            conditions.append(StopRecord.shift == shift)
        if stop_type:
            conditions.append(StopRecord.stop_type == stop_type)
        if start_time:
            conditions.append(StopRecord.start_time >= start_time)
        if end_time:
            conditions.append(StopRecord.start_time <= end_time)

        query = select(StopRecord)
        count_query = select(func.count()).select_from(StopRecord)
        if conditions:
            query = query.where(*conditions)
            count_query = count_query.where(*conditions)

        query = query.order_by(StopRecord.start_time.desc()).offset((page - 1) * page_size).limit(page_size)
        items = (await self.stop_records.db.execute(query)).scalars().all()
        total = (await self.stop_records.db.execute(count_query)).scalar_one()
        return items, total

    async def get_stop_record(self, id: int):
        return await self.stop_records.get_by_id(id)

    async def create_stop_record(self, data: dict[str, Any]):
        return await self.stop_records.create(data)

    async def update_stop_record(self, id: int, data: dict[str, Any]):
        return await self.stop_records.update(id, data)

    async def delete_stop_record(self, id: int) -> bool:
        return await self.stop_records.delete(id)
