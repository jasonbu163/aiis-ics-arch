"""
文件路径: /backend/app/maintenance/crud/async_maintenance.py
功能描述: 维保管理异步 CRUD
主要功能:
    - 封装维保项数据库读写
    - 封装保养记录数据库读写
    - 封装保养记录关联查询
"""
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.maintenance.models.maintenance import Maintenance, MaintenanceLog
from common.async_crud_base import BaseService
from common.data_keys import maintenance_type_storage_values


class MaintenanceCRUD:
    """维保管理数据库访问层。"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.maintenances = BaseService(db, Maintenance)
        self.logs = BaseService(db, MaintenanceLog)

    async def list_maintenances(
        self,
        page: int,
        page_size: int,
        maintenance_type: str | None,
        status: str | None,
    ):
        query = select(Maintenance)
        if maintenance_type:
            query = query.where(Maintenance.maintenance_type.in_(maintenance_type_storage_values(maintenance_type)))
        if status:
            query = query.where(Maintenance.status == status)

        total_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar()

        result = await self.db.execute(query.offset((page - 1) * page_size).limit(page_size))
        return result.scalars().all(), total

    async def get_maintenance(self, id: int):
        return await self.maintenances.get_by_id(id)

    async def create_maintenance(self, data: dict[str, Any]):
        return await self.maintenances.create(data)

    async def update_maintenance(self, id: int, data: dict[str, Any]):
        return await self.maintenances.update(id, data)

    async def delete_maintenance(self, id: int) -> bool:
        return await self.maintenances.delete(id)

    async def list_maintenance_logs(
        self,
        page: int,
        page_size: int,
        maintenance_id: int | None,
        equipment_name: str | None,
        maintenance_type: str | None,
        status: str | None,
    ):
        query = select(MaintenanceLog).options(joinedload(MaintenanceLog.maintenance))

        if maintenance_id:
            query = query.where(MaintenanceLog.maintenance_id == maintenance_id)
        if equipment_name:
            keyword = f"%{equipment_name}%"
            query = query.join(MaintenanceLog.maintenance).where(
                or_(Maintenance.name.ilike(keyword), Maintenance.code.ilike(keyword))
            )
        if maintenance_type:
            query = query.where(MaintenanceLog.maintenance_type.in_(maintenance_type_storage_values(maintenance_type)))
        if status:
            query = query.where(MaintenanceLog.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(MaintenanceLog.last_date.desc())

        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_maintenance_log(self, id: int):
        return await self.logs.get_by_id(id)

    async def create_maintenance_log(self, data: dict[str, Any]):
        return await self.logs.create(data)

    async def update_maintenance_log(self, id: int, data: dict[str, Any]):
        return await self.logs.update(id, data)

    async def delete_maintenance_log(self, id: int) -> bool:
        return await self.logs.delete(id)
