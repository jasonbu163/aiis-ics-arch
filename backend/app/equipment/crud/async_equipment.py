"""
文件路径: /backend/app/equipment/crud/async_equipment.py
功能描述: 设备模块异步 CRUD
主要功能:
    - 查询最新传动参数
    - 查询温控历史参数
    - 查询最新生产参数
"""
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.equipment.models.equipment import EquipmentDrive, EquipmentProductionParameters, EquipmentTemperature


class AsyncEquipmentCRUD:
    """设备模块 SQL 执行层。"""

    async def get_latest_drive(self, db: AsyncSession) -> EquipmentDrive | None:
        result = await db.execute(select(EquipmentDrive).order_by(desc(EquipmentDrive.timestamp)).limit(1))
        return result.scalar_one_or_none()

    async def get_temperature_history(self, db: AsyncSession, limit: int = 10) -> list[EquipmentTemperature]:
        result = await db.execute(select(EquipmentTemperature).order_by(desc(EquipmentTemperature.timestamp)).limit(limit))
        return list(result.scalars().all())

    async def get_latest_production_parameters(self, db: AsyncSession) -> EquipmentProductionParameters | None:
        result = await db.execute(
            select(EquipmentProductionParameters).order_by(desc(EquipmentProductionParameters.timestamp)).limit(1)
        )
        return result.scalar_one_or_none()


equipment_crud = AsyncEquipmentCRUD()
