"""
文件路径: /backend/app/reports/services/async_quality.py
功能描述: 报表质量控制异步服务
主要功能:
    - 编排质量记录和缺陷记录接口
    - 保持质量控制接口既有响应结构
"""
import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from common.data_keys import normalize_defect_level
from app.reports.crud.async_quality import ReportsQualityCRUD
from app.reports.models.reports import DefectRecord, QualityRecord


def serialize_defect(defect: DefectRecord) -> dict:
    return {
        "id": defect.id,
        "quality_record_id": defect.quality_record_id,
        "position": defect.position,
        "defect_type": defect.defect_type,
        "defect_level": normalize_defect_level(defect.defect_level),
        "length": defect.length,
        "description": defect.description,
    }


def serialize_quality_record(record: QualityRecord, defects: list[DefectRecord]) -> dict:
    return {
        "id": record.id,
        "performance_id": record.performance_id,
        "item_name": record.item_name,
        "standard_value": record.standard_value,
        "actual_value": record.actual_value,
        "result": record.result,
        "inspector": record.inspector,
        "inspect_time": record.inspect_time.isoformat() if record.inspect_time else None,
        "remark": record.remark,
        "defects": [
            {
                "id": defect.id,
                "position": defect.position,
                "defect_type": defect.defect_type,
                "defect_level": normalize_defect_level(defect.defect_level),
                "length": defect.length,
                "description": defect.description,
            }
            for defect in defects
        ],
    }


class ReportsQualityService:
    """报表质量控制业务编排层。"""

    @staticmethod
    def crud(db: AsyncSession) -> ReportsQualityCRUD:
        return ReportsQualityCRUD(db)

    async def list_quality_records(self, db: AsyncSession, performance_id: int) -> list[dict]:
        crud = self.crud(db)
        records = await crud.list_quality_records(performance_id)

        data = []
        for record in records:
            defects = await crud.list_defects_by_quality_id(record.id)
            data.append(serialize_quality_record(record, defects))
        return data

    async def create_quality_record(
        self,
        db: AsyncSession,
        performance_id: int,
        item_name: str,
        standard_value: Optional[str],
        actual_value: Optional[str],
        result: Optional[str],
        inspector: Optional[str],
        inspect_time: Optional[str],
        remark: Optional[str],
    ) -> dict:
        inspect_time_dt = datetime.datetime.fromisoformat(inspect_time) if inspect_time else None
        record = QualityRecord(
            performance_id=performance_id,
            item_name=item_name,
            standard_value=standard_value,
            actual_value=actual_value,
            result=result,
            inspector=inspector,
            inspect_time=inspect_time_dt,
            remark=remark,
        )
        record = await self.crud(db).create_quality_record(record)
        return {"id": record.id, "performance_id": record.performance_id, "item_name": record.item_name}

    async def update_quality_record(
        self,
        db: AsyncSession,
        quality_id: int,
        standard_value: Optional[str],
        actual_value: Optional[str],
        result: Optional[str],
        inspector: Optional[str],
        inspect_time: Optional[str],
        remark: Optional[str],
    ) -> bool:
        record = await self.crud(db).get_quality_record(quality_id)
        if not record:
            return False

        if standard_value is not None:
            record.standard_value = standard_value
        if actual_value is not None:
            record.actual_value = actual_value
        if result is not None:
            record.result = result
        if inspector is not None:
            record.inspector = inspector
        if inspect_time is not None:
            record.inspect_time = datetime.datetime.fromisoformat(inspect_time)
        if remark is not None:
            record.remark = remark

        await self.crud(db).save_quality_record(record)
        return True

    async def list_defect_records(self, db: AsyncSession, quality_id: int) -> list[dict]:
        records = await self.crud(db).list_defects_by_quality_id(quality_id)
        return [serialize_defect(record) for record in records]

    async def add_defect_record(
        self,
        db: AsyncSession,
        quality_id: int,
        position: Optional[str],
        defect_type: Optional[str],
        defect_level: Optional[str],
        length: Optional[int],
        description: Optional[str],
    ) -> int | None:
        if not await self.crud(db).get_quality_record(quality_id):
            return None

        defect = DefectRecord(
            quality_record_id=quality_id,
            position=position,
            defect_type=defect_type,
            defect_level=normalize_defect_level(defect_level),
            length=length,
            description=description,
        )
        defect = await self.crud(db).create_defect(defect)
        return defect.id

    async def delete_defect_record(self, db: AsyncSession, defect_id: int) -> bool:
        defect = await self.crud(db).get_defect(defect_id)
        if not defect:
            return False
        await self.crud(db).delete_defect(defect)
        return True


reports_quality_service = ReportsQualityService()
