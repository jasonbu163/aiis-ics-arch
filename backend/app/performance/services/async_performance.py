"""
文件路径: /backend/app/performance/services/async_performance.py
功能描述: 生产实绩业务逻辑服务层
主要功能:
    - 实绩 CRUD 操作封装
    - 过程数据查询与管理
    - 下推记录管理
"""
from typing import List, Dict, Any
from datetime import datetime, date

from sqlalchemy.ext.asyncio import AsyncSession

from app.performance.crud.async_performance import PerformanceCRUD
from app.performance.domain import (
    InvalidPerformanceTimeRange,
    apply_performance_duration,
    normalize_parent_coil_no,
)
from app.performance.models.performance import (
    Performance, ProcessTemperature, ProcessTension, 
    ProcessSpeed, PushDownRecord
)
from app.performance.schemas.performance_in import (
    PerformanceCreate, PerformanceUpdate,
    ProcessTemperatureCreate, ProcessTensionCreate, ProcessSpeedCreate,
)
from common.data_keys import PerformanceEffectiveWeightSource, PerformanceRecordSource
from common.error_codes import ErrorCode
from common.exceptions import BusinessException


class PerformanceService:
    """生产实绩服务 - 业务逻辑层"""

    @staticmethod
    def crud(db: AsyncSession) -> PerformanceCRUD:
        return PerformanceCRUD(db)
    
    @staticmethod
    async def get_list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        coil_no: str | None = None,
        grade: str | None = None,
        observation_status: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None
    ) -> Dict[str, Any]:
        performances, total = await PerformanceService.crud(db).list_performances(
            page=page,
            page_size=page_size,
            coil_no=coil_no,
            grade=grade,
            observation_status=observation_status,
            start_date=start_date,
            end_date=end_date,
        )

        return {
            "items": performances,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    @staticmethod
    async def get_by_id(db: AsyncSession, performance_id: int) -> Performance | None:
        return await PerformanceService.crud(db).get_performance(performance_id)

    @staticmethod
    async def create(db: AsyncSession, performance_data: PerformanceCreate) -> Performance:
        payload = performance_data.model_dump()
        payload["parent_coil_no"] = normalize_parent_coil_no(
            payload["coil_no"],
            payload.get("parent_coil_no"),
        )
        if payload.get("weight") is not None:
            payload["manual_override_weight"] = payload["weight"]
            payload["effective_weight"] = payload["weight"]
            payload["effective_weight_source"] = PerformanceEffectiveWeightSource.MANUAL_OVERRIDE_WEIGHT.value
            payload["manual_override_at"] = datetime.now()
            payload["manual_override_reason"] = payload.get("remark") or "manual_entry"
        payload["record_source"] = PerformanceRecordSource.MANUAL_ENTRY.value
        performance = Performance(
            **payload
        )
        try:
            apply_performance_duration(performance)
        except InvalidPerformanceTimeRange as exc:
            raise BusinessException(ErrorCode.PERFORMANCE_INVALID_TIME_RANGE) from exc
        return await PerformanceService.crud(db).create_performance(performance)

    @staticmethod
    async def update(
        db: AsyncSession,
        performance_id: int,
        performance_data: PerformanceUpdate
    ) -> Performance | None:
        performance = await PerformanceService.get_by_id(db, performance_id)
        if not performance:
            return None

        update_data = performance_data.model_dump(exclude_unset=True)
        for field in ("grade", "weight"):
            if field in update_data and update_data[field] is None:
                raise ValueError(f"手工实绩字段 {field} 不允许为空")
        manual_weight = update_data.pop("weight", None)
        for field, value in update_data.items():
            setattr(performance, field, value)
        if manual_weight is not None:
            performance.weight = manual_weight
            performance.manual_override_weight = manual_weight
            performance.effective_weight = manual_weight
            performance.effective_weight_source = PerformanceEffectiveWeightSource.MANUAL_OVERRIDE_WEIGHT.value
            performance.manual_override_at = datetime.now()
            performance.manual_override_reason = update_data.get("remark") or performance.manual_override_reason or "manual_update"
        try:
            apply_performance_duration(performance)
        except InvalidPerformanceTimeRange as exc:
            raise BusinessException(ErrorCode.PERFORMANCE_INVALID_TIME_RANGE) from exc
        
        return await PerformanceService.crud(db).save_performance(performance)

    @staticmethod
    async def delete(db: AsyncSession, performance_id: int) -> bool:
        performance = await PerformanceService.get_by_id(db, performance_id)
        if not performance:
            return False
        
        await PerformanceService.crud(db).delete_performance(performance)
        return True

    @staticmethod
    async def get_process_data(db: AsyncSession, performance_id: int) -> Dict[str, List]:
        crud = PerformanceService.crud(db)
        return {
            "temperature": await crud.list_temperature_records(performance_id),
            "tension": await crud.list_tension_records(performance_id),
            "speed": await crud.list_speed_records(performance_id),
        }

    @staticmethod
    async def add_temperature_record(
        db: AsyncSession,
        data: ProcessTemperatureCreate
    ) -> ProcessTemperature:
        record = ProcessTemperature(**data.model_dump())
        return await PerformanceService.crud(db).create_record(record)

    @staticmethod
    async def add_tension_record(
        db: AsyncSession,
        data: ProcessTensionCreate
    ) -> ProcessTension:
        record = ProcessTension(**data.model_dump())
        return await PerformanceService.crud(db).create_record(record)

    @staticmethod
    async def add_speed_record(
        db: AsyncSession,
        data: ProcessSpeedCreate
    ) -> ProcessSpeed:
        record = ProcessSpeed(**data.model_dump())
        return await PerformanceService.crud(db).create_record(record)

    @staticmethod
    async def push_down(
        db: AsyncSession,
        performance_ids: List[int],
        operator_id: int,
        target_system: str | None = None
    ) -> List[PushDownRecord]:
        records = []
        for pid in performance_ids:
            record = PushDownRecord(
                performance_id=pid,
                push_down_type="batch" if len(performance_ids) > 1 else "single",
                target_system=target_system,
                operator_id=operator_id,
                status="completed",
                completed_at=datetime.now()
            )
            records.append(record)

        return await PerformanceService.crud(db).create_push_down_records(records)

    @staticmethod
    async def get_push_down_records(
        db: AsyncSession,
        performance_id: int
    ) -> List[PushDownRecord]:
        return await PerformanceService.crud(db).list_push_down_records(performance_id)

async_performance_service: PerformanceService = PerformanceService()
