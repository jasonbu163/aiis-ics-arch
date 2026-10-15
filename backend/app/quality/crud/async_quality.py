"""
文件路径: /backend/app/quality/crud/async_quality.py
功能描述: 质量模块异步 CRUD
主要功能:
    - 查询、创建、更新、删除质量检验记录
    - 查询、创建、删除缺陷记录
    - 查询 SPC 测量点
"""
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from common.data_keys import quality_grade_storage_values
from app.quality.models.quality import QualityDefectRecord, QualityInspection, QualitySPCMeasurement


class AsyncQualityCRUD:
    """质量模块 SQL 执行层。"""

    async def list_inspections(
        self,
        db: AsyncSession,
        page: int,
        page_size: int,
        coil_no: str | None = None,
        grade: str | None = None,
        quality_grade: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> tuple[list[QualityInspection], int]:
        query = select(QualityInspection)

        if coil_no:
            query = query.where(QualityInspection.coil_no.ilike(f"%{coil_no}%"))
        if grade:
            query = query.where(QualityInspection.grade == grade)
        if quality_grade:
            query = query.where(QualityInspection.quality_grade.in_(quality_grade_storage_values(quality_grade)))
        if start_date:
            query = query.where(QualityInspection.inspect_time >= start_date)
        if end_date:
            query = query.where(QualityInspection.inspect_time <= end_date)

        total_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar_one()

        result = await db.execute(
            query.order_by(desc(QualityInspection.created_at)).offset((page - 1) * page_size).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_inspection_with_defects(self, db: AsyncSession, quality_id: int) -> QualityInspection | None:
        result = await db.execute(
            select(QualityInspection)
            .options(selectinload(QualityInspection.defects))
            .where(QualityInspection.id == quality_id)
        )
        return result.scalar_one_or_none()

    async def get_inspection(self, db: AsyncSession, quality_id: int) -> QualityInspection | None:
        result = await db.execute(select(QualityInspection).where(QualityInspection.id == quality_id))
        return result.scalar_one_or_none()

    async def create_inspection(self, db: AsyncSession, inspection: QualityInspection) -> QualityInspection:
        db.add(inspection)
        await db.flush()
        return inspection

    async def delete_inspection(self, db: AsyncSession, inspection: QualityInspection) -> None:
        await db.delete(inspection)

    async def list_defects(self, db: AsyncSession, page: int, page_size: int) -> tuple[list[QualityDefectRecord], int]:
        total_result = await db.execute(select(func.count()).select_from(QualityDefectRecord))
        total = total_result.scalar_one()

        result = await db.execute(
            select(QualityDefectRecord)
            .order_by(desc(QualityDefectRecord.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def list_defects_by_inspection(self, db: AsyncSession, quality_id: int) -> list[QualityDefectRecord]:
        result = await db.execute(select(QualityDefectRecord).where(QualityDefectRecord.inspection_id == quality_id))
        return list(result.scalars().all())

    async def get_defect(
        self, db: AsyncSession, quality_id: int, defect_id: int
    ) -> QualityDefectRecord | None:
        result = await db.execute(
            select(QualityDefectRecord).where(
                QualityDefectRecord.id == defect_id,
                QualityDefectRecord.inspection_id == quality_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_defect(self, db: AsyncSession, defect: QualityDefectRecord) -> QualityDefectRecord:
        db.add(defect)
        await db.flush()
        await db.refresh(defect)
        return defect

    async def delete_defect(self, db: AsyncSession, defect: QualityDefectRecord) -> None:
        await db.delete(defect)

    async def list_spc_measurements(
        self,
        db: AsyncSession,
        item: str,
        grade: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[QualitySPCMeasurement]:
        query = select(QualitySPCMeasurement).where(QualitySPCMeasurement.item == item)

        if grade:
            query = query.where(QualitySPCMeasurement.grade == grade)
        if start_date:
            query = query.where(QualitySPCMeasurement.measured_at >= start_date)
        if end_date:
            query = query.where(QualitySPCMeasurement.measured_at <= end_date)

        result = await db.execute(query.order_by(QualitySPCMeasurement.measured_at))
        return list(result.scalars().all())


quality_crud = AsyncQualityCRUD()
