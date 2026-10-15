"""
文件路径: /backend/app/maintenance/services/async_maintenance.py
功能描述: 维保管理异步业务服务
主要功能:
    - 编排维保项管理业务
    - 编排保养记录管理业务
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.maintenance.crud.async_maintenance import MaintenanceCRUD
from app.maintenance.schemas.maintenance_in import (
    MaintenanceCreate,
    MaintenanceLogCreate,
    MaintenanceLogUpdate,
    MaintenanceUpdate,
)
from common.data_keys import normalize_maintenance_type


class MaintenanceService:
    """维保管理业务编排层。"""

    def __init__(self, db: AsyncSession):
        self.crud = MaintenanceCRUD(db)

    async def list_maintenances(
        self,
        page: int,
        page_size: int,
        maintenance_type: str | None,
        status: str | None,
    ):
        return await self.crud.list_maintenances(
            page=page,
            page_size=page_size,
            maintenance_type=maintenance_type,
            status=status,
        )

    async def get_maintenance(self, id: int):
        return await self.crud.get_maintenance(id)

    async def create_maintenance(self, data: MaintenanceCreate):
        payload = data.model_dump()
        payload["maintenance_type"] = normalize_maintenance_type(payload.get("maintenance_type"))
        return await self.crud.create_maintenance(payload)

    async def update_maintenance(self, id: int, data: MaintenanceUpdate):
        payload = data.model_dump(exclude_unset=True)
        if "maintenance_type" in payload:
            payload["maintenance_type"] = normalize_maintenance_type(payload["maintenance_type"])
        return await self.crud.update_maintenance(id, payload)

    async def delete_maintenance(self, id: int) -> bool:
        return await self.crud.delete_maintenance(id)

    async def list_maintenance_logs(
        self,
        page: int,
        page_size: int,
        maintenance_id: int | None,
        equipment_name: str | None,
        maintenance_type: str | None,
        status: str | None,
    ):
        return await self.crud.list_maintenance_logs(
            page=page,
            page_size=page_size,
            maintenance_id=maintenance_id,
            equipment_name=equipment_name,
            maintenance_type=maintenance_type,
            status=status,
        )

    async def get_maintenance_log(self, id: int):
        return await self.crud.get_maintenance_log(id)

    async def create_maintenance_log(self, data: MaintenanceLogCreate):
        payload = data.model_dump()
        payload["maintenance_type"] = normalize_maintenance_type(payload.get("maintenance_type"))
        return await self.crud.create_maintenance_log(payload)

    async def update_maintenance_log(self, id: int, data: MaintenanceLogUpdate):
        payload = data.model_dump(exclude_unset=True)
        if "maintenance_type" in payload:
            payload["maintenance_type"] = normalize_maintenance_type(payload["maintenance_type"])
        return await self.crud.update_maintenance_log(id, payload)

    async def delete_maintenance_log(self, id: int) -> bool:
        return await self.crud.delete_maintenance_log(id)
