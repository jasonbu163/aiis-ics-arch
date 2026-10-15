"""
文件路径: /backend/app/reports/crud/async_quality.py
功能描述: 报表质量控制异步 CRUD
主要功能:
    - 查询、创建和更新质量记录
    - 查询、创建和删除缺陷记录
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.reports.models.reports import DefectRecord, QualityRecord


class ReportsQualityCRUD:
    """报表质量控制数据库访问层。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_quality_records(self, performance_id: int):
        result = await self.db.execute(select(QualityRecord).where(QualityRecord.performance_id == performance_id))
        return result.scalars().all()

    async def list_defects_by_quality_id(self, quality_id: int):
        result = await self.db.execute(select(DefectRecord).where(DefectRecord.quality_record_id == quality_id))
        return result.scalars().all()

    async def get_quality_record(self, quality_id: int):
        result = await self.db.execute(select(QualityRecord).where(QualityRecord.id == quality_id))
        return result.scalar_one_or_none()

    async def create_quality_record(self, record: QualityRecord) -> QualityRecord:
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def save_quality_record(self, record: QualityRecord) -> QualityRecord:
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def create_defect(self, defect: DefectRecord) -> DefectRecord:
        self.db.add(defect)
        await self.db.commit()
        await self.db.refresh(defect)
        return defect

    async def get_defect(self, defect_id: int):
        result = await self.db.execute(select(DefectRecord).where(DefectRecord.id == defect_id))
        return result.scalar_one_or_none()

    async def delete_defect(self, defect: DefectRecord) -> None:
        await self.db.delete(defect)
        await self.db.commit()
