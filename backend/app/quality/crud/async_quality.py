"""
文件路径: /backend/app/quality/crud/async_quality.py
功能描述: 质量模块异步 CRUD
主要功能:
    - 查询 SPC 测量点
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.quality.models.quality import QualitySPCMeasurement


class AsyncQualityCRUD:
    """质量模块 SQL 执行层。"""

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
