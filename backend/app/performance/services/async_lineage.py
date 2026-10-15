"""
文件路径: /backend/app/performance/services/async_lineage.py
功能描述: 实绩分/合卷 transform 与 lineage 业务服务
主要功能:
    - 维护 Performance transform / lineage 事务
    - 计算 effective / available weight
    - 拒绝超额、重复角色和无有效重量的业务变换
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.performance.models.performance import (
    Performance,
    PerformanceLineage,
    PerformanceTransform,
)
from app.performance.schemas.performance_lineage import (
    EffectiveWeightOverrideIn,
    MergeTransformCreateIn,
    SplitTransformCreateIn,
)
from common.data_keys import (
    PerformanceCurrentOperabilityStatus,
    PerformanceEffectiveWeightSource,
    PerformanceLineageErrorCode,
    PerformanceLineageRole,
    PerformanceRecordSource,
    PerformanceTransformStatus,
    PerformanceTransformType,
)
from common.exceptions import BusinessException


WEIGHT_QUANT = Decimal("0.0001")


def _quantize(value: Decimal) -> Decimal:
    return Decimal(value).quantize(WEIGHT_QUANT, rounding=ROUND_HALF_UP)


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _business_error(
    error_code: PerformanceLineageErrorCode,
    *,
    code: int = 400,
) -> BusinessException:
    return BusinessException(error_code, code=code)


class PerformanceLineageService:
    """实绩 transform / lineage 服务。"""

    @staticmethod
    async def _get_performance_for_update(
        db: AsyncSession,
        performance_id: int,
    ) -> Performance:
        result = await db.execute(
            select(Performance)
            .where(Performance.id == performance_id)
            .with_for_update()
        )
        performance = result.scalar_one_or_none()
        if performance is None:
            raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_NOT_FOUND, code=404)
        return performance

    @staticmethod
    async def _get_performance(
        db: AsyncSession,
        performance_id: int,
    ) -> Performance:
        result = await db.execute(select(Performance).where(Performance.id == performance_id))
        performance = result.scalar_one_or_none()
        if performance is None:
            raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_NOT_FOUND, code=404)
        return performance

    @staticmethod
    async def _committed_source_allocated_weight(
        db: AsyncSession,
        performance_id: int,
    ) -> Decimal:
        committed, _, _ = await PerformanceLineageService._source_consumption(db, performance_id)
        return committed

    @staticmethod
    async def _source_consumption(
        db: AsyncSession,
        performance_id: int,
    ) -> tuple[Decimal, int | None, str | None]:
        result = await db.execute(
            select(
                PerformanceLineage.allocated_weight,
                PerformanceLineage.transform_id,
                PerformanceTransform.transform_type,
            )
            .join(PerformanceTransform, PerformanceTransform.id == PerformanceLineage.transform_id)
            .where(
                PerformanceLineage.performance_id == performance_id,
                PerformanceLineage.role == PerformanceLineageRole.SOURCE.value,
                PerformanceTransform.status == PerformanceTransformStatus.COMMITTED.value,
            )
            .order_by(PerformanceLineage.created_at.desc(), PerformanceLineage.id.desc())
        )
        total = Decimal("0")
        consumed_transform_id: int | None = None
        consumed_transform_type: str | None = None
        for allocated_weight, transform_id, transform_type in result.all():
            total += allocated_weight
            if consumed_transform_id is None:
                consumed_transform_id = transform_id
                consumed_transform_type = transform_type
        return _quantize(total), consumed_transform_id, consumed_transform_type

    @staticmethod
    async def _available_weight(
        db: AsyncSession,
        performance: Performance,
    ) -> tuple[Decimal, Decimal]:
        if performance.effective_weight is None:
            raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_EFFECTIVE_WEIGHT_REQUIRED)
        effective = _quantize(performance.effective_weight)
        committed = await PerformanceLineageService._committed_source_allocated_weight(
            db,
            performance.id,
        )
        available = _quantize(effective - committed)
        if available < Decimal("0"):
            raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_INSUFFICIENT_AVAILABLE_WEIGHT)
        return effective, available

    @staticmethod
    def _lineage_source_snapshot(
        transform: PerformanceTransform,
        performance: Performance,
        allocated_weight: Decimal,
        effective_weight: Decimal,
        available_before: Decimal,
    ) -> PerformanceLineage:
        return PerformanceLineage(
            transform=transform,
            performance_id=performance.id,
            role=PerformanceLineageRole.SOURCE.value,
            allocated_weight=allocated_weight,
            effective_weight_snapshot=effective_weight,
            effective_weight_source_snapshot=performance.effective_weight_source or "",
            available_weight_before_snapshot=available_before,
            available_weight_after_snapshot=_quantize(available_before - allocated_weight),
        )

    @staticmethod
    def _lineage_target_snapshot(
        transform: PerformanceTransform,
        performance: Performance,
        allocated_weight: Decimal,
    ) -> PerformanceLineage:
        effective = _quantize(performance.effective_weight or allocated_weight)
        return PerformanceLineage(
            transform=transform,
            performance=performance,
            role=PerformanceLineageRole.TARGET.value,
            allocated_weight=allocated_weight,
            effective_weight_snapshot=effective,
            effective_weight_source_snapshot=performance.effective_weight_source or "",
            available_weight_before_snapshot=effective,
            available_weight_after_snapshot=effective,
        )

    @staticmethod
    async def _load_transform(
        db: AsyncSession,
        transform_id: int,
    ) -> PerformanceTransform:
        result = await db.execute(
            select(PerformanceTransform)
            .options(selectinload(PerformanceTransform.lineage_entries))
            .where(PerformanceTransform.id == transform_id)
        )
        transform = result.scalar_one_or_none()
        if transform is None:
            raise _business_error(
                PerformanceLineageErrorCode.PERFORMANCE_TRANSFORM_NOT_FOUND,
                code=404,
            )
        return transform

    @staticmethod
    async def _lineage_graph(db: AsyncSession) -> dict[int, set[int]]:
        result = await db.execute(
            select(
                PerformanceLineage.transform_id,
                PerformanceLineage.performance_id,
                PerformanceLineage.role,
            )
            .join(PerformanceTransform, PerformanceTransform.id == PerformanceLineage.transform_id)
            .where(PerformanceTransform.status == PerformanceTransformStatus.COMMITTED.value)
        )
        roles_by_transform: dict[int, dict[str, set[int]]] = {}
        for transform_id, performance_id, role in result.all():
            roles = roles_by_transform.setdefault(transform_id, {"source": set(), "target": set()})
            if role == PerformanceLineageRole.SOURCE.value:
                roles["source"].add(performance_id)
            elif role == PerformanceLineageRole.TARGET.value:
                roles["target"].add(performance_id)

        graph: dict[int, set[int]] = {}
        for roles in roles_by_transform.values():
            for source_id in roles["source"]:
                graph.setdefault(source_id, set()).update(roles["target"])
        return graph

    @staticmethod
    def _has_path(graph: dict[int, set[int]], start_id: int, end_id: int) -> bool:
        seen: set[int] = set()
        stack = [start_id]
        while stack:
            current_id = stack.pop()
            if current_id == end_id:
                return True
            if current_id in seen:
                continue
            seen.add(current_id)
            stack.extend(graph.get(current_id, set()) - seen)
        return False

    @staticmethod
    async def _assert_existing_targets_do_not_cycle(
        db: AsyncSession,
        *,
        source_ids: set[int],
        target_ids: set[int],
    ) -> None:
        if not target_ids:
            return
        if source_ids & target_ids:
            raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_LINEAGE_DOUBLE_ROLE)
        graph = await PerformanceLineageService._lineage_graph(db)
        for source_id in source_ids:
            for target_id in target_ids:
                if PerformanceLineageService._has_path(graph, target_id, source_id):
                    raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_LINEAGE_CYCLE)
        raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_LINEAGE_DOUBLE_ROLE)

    @staticmethod
    async def split(
        db: AsyncSession,
        data: SplitTransformCreateIn,
        operator_id: int | None,
    ) -> PerformanceTransform:
        try:
            if len(data.targets) < 2:
                raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_TRANSFORM_INVALID_CARDINALITY)
            source = await PerformanceLineageService._get_performance_for_update(
                db,
                data.source_performance_id,
            )
            await PerformanceLineageService._assert_existing_targets_do_not_cycle(
                db,
                source_ids={source.id},
                target_ids={
                    target.target_performance_id
                    for target in data.targets
                    if target.target_performance_id is not None
                },
            )
            source_effective, source_available = await PerformanceLineageService._available_weight(db, source)
            target_allocations = [_quantize(target.allocated_weight) for target in data.targets]
            total_allocated = _quantize(sum(target_allocations, Decimal("0")))
            if total_allocated > source_available:
                raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_INSUFFICIENT_AVAILABLE_WEIGHT)
            if total_allocated < source_available:
                raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_TRANSFORM_REQUIRES_FULL_SOURCE)

            now = datetime.now()
            transform = PerformanceTransform(
                transform_type=PerformanceTransformType.SPLIT.value,
                status=PerformanceTransformStatus.COMMITTED.value,
                quantity_dimension="weight",
                requested_by_id=operator_id,
                requested_reason=_clean_text(data.reason),
                confirmed_by_id=operator_id,
                confirmed_at=now,
                effective_weight_context=(
                    f"source:{source.id};effective:{source_effective};available:{source_available}"
                ),
            )
            db.add(transform)
            await db.flush()
            db.add(
                PerformanceLineageService._lineage_source_snapshot(
                    transform,
                    source,
                    total_allocated,
                    source_effective,
                    source_available,
                )
            )

            for target_data, allocated_weight in zip(data.targets, target_allocations):
                coil_no = _clean_text(target_data.coil_no)
                if coil_no is None:
                    raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_TRANSFORM_INVALID_CARDINALITY)
                target = Performance(
                    plan_id=source.plan_id,
                    coil_no=coil_no,
                    parent_coil_no=source.coil_no,
                    grade=_clean_text(target_data.grade) or source.grade,
                    spec=_clean_text(target_data.spec) or source.spec,
                    weight=allocated_weight,
                    collected_weight=None,
                    manual_override_weight=None,
                    effective_weight=allocated_weight,
                    effective_weight_source=PerformanceEffectiveWeightSource.SPLIT_GENERATED.value,
                    production_date=source.production_date,
                    start_time=source.start_time,
                    end_time=source.end_time,
                    output_quantity=Decimal("0"),
                    qualified_quantity=Decimal("0"),
                    total_duration_seconds=source.total_duration_seconds,
                    total_duration_source=source.total_duration_source,
                    is_split=False,
                    remark=_clean_text(target_data.remark),
                    record_source=PerformanceRecordSource.SPLIT_GENERATED.value,
                )
                db.add(target)
                await db.flush()
                db.add(
                    PerformanceLineageService._lineage_target_snapshot(
                        transform,
                        target,
                        allocated_weight,
                    )
                )

            await db.commit()
            return await PerformanceLineageService._load_transform(db, transform.id)
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def merge(
        db: AsyncSession,
        data: MergeTransformCreateIn,
        operator_id: int | None,
    ) -> PerformanceTransform:
        try:
            source_ids = [source.performance_id for source in data.sources]
            if len(source_ids) < 2:
                raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_TRANSFORM_INVALID_CARDINALITY)
            if len(set(source_ids)) != len(source_ids):
                raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_LINEAGE_DOUBLE_ROLE)

            sources: list[Performance] = []
            source_snapshots: list[tuple[Performance, Decimal, Decimal, Decimal]] = []
            for source_data in data.sources:
                source = await PerformanceLineageService._get_performance_for_update(
                    db,
                    source_data.performance_id,
                )
                source_effective, source_available = await PerformanceLineageService._available_weight(db, source)
                allocated_weight = _quantize(source_data.allocated_weight)
                if allocated_weight > source_available:
                    raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_INSUFFICIENT_AVAILABLE_WEIGHT)
                if allocated_weight < source_available:
                    raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_TRANSFORM_REQUIRES_FULL_SOURCE)
                sources.append(source)
                source_snapshots.append((source, allocated_weight, source_effective, source_available))

            target_coil_no = _clean_text(data.target.coil_no)
            if target_coil_no is None:
                raise _business_error(PerformanceLineageErrorCode.PERFORMANCE_TRANSFORM_INVALID_CARDINALITY)
            await PerformanceLineageService._assert_existing_targets_do_not_cycle(
                db,
                source_ids=set(source_ids),
                target_ids=(
                    {data.target.target_performance_id}
                    if data.target.target_performance_id is not None
                    else set()
                ),
            )
            total_allocated = _quantize(
                sum((allocated for _, allocated, _, _ in source_snapshots), Decimal("0"))
            )
            first_source = sources[0]
            now = datetime.now()
            transform = PerformanceTransform(
                transform_type=PerformanceTransformType.MERGE.value,
                status=PerformanceTransformStatus.COMMITTED.value,
                quantity_dimension="weight",
                requested_by_id=operator_id,
                requested_reason=_clean_text(data.reason),
                confirmed_by_id=operator_id,
                confirmed_at=now,
                effective_weight_context=(
                    "sources:"
                    + ",".join(f"{source.id}:{allocated}" for source, allocated, _, _ in source_snapshots)
                ),
            )
            db.add(transform)
            await db.flush()

            for source, allocated_weight, source_effective, source_available in source_snapshots:
                db.add(
                    PerformanceLineageService._lineage_source_snapshot(
                        transform,
                        source,
                        allocated_weight,
                        source_effective,
                        source_available,
                    )
                )

            target = Performance(
                plan_id=first_source.plan_id,
                coil_no=target_coil_no,
                parent_coil_no=target_coil_no,
                grade=_clean_text(data.target.grade) or first_source.grade,
                spec=_clean_text(data.target.spec) or first_source.spec,
                weight=total_allocated,
                collected_weight=None,
                manual_override_weight=None,
                effective_weight=total_allocated,
                effective_weight_source=PerformanceEffectiveWeightSource.MERGE_GENERATED.value,
                production_date=first_source.production_date,
                start_time=min((source.start_time for source in sources if source.start_time), default=None),
                end_time=max((source.end_time for source in sources if source.end_time), default=None),
                output_quantity=Decimal("0"),
                qualified_quantity=Decimal("0"),
                is_split=False,
                remark=_clean_text(data.target.remark),
                record_source=PerformanceRecordSource.MERGE_GENERATED.value,
            )
            db.add(target)
            await db.flush()
            db.add(
                PerformanceLineageService._lineage_target_snapshot(
                    transform,
                    target,
                    total_allocated,
                )
            )

            await db.commit()
            return await PerformanceLineageService._load_transform(db, transform.id)
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def override_effective_weight(
        db: AsyncSession,
        performance_id: int,
        data: EffectiveWeightOverrideIn,
        operator_id: int | None,
    ) -> Performance:
        try:
            performance = await PerformanceLineageService._get_performance_for_update(
                db,
                performance_id,
            )
            effective_weight = _quantize(data.effective_weight)
            performance.manual_override_weight = effective_weight
            performance.effective_weight = effective_weight
            performance.effective_weight_source = PerformanceEffectiveWeightSource.MANUAL_OVERRIDE_WEIGHT.value
            performance.manual_override_by_id = operator_id
            performance.manual_override_at = datetime.now()
            performance.manual_override_reason = _clean_text(data.reason)
            performance.weight = effective_weight
            await db.commit()
            await db.refresh(performance)
            return performance
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def get_transform(
        db: AsyncSession,
        transform_id: int,
    ) -> PerformanceTransform:
        return await PerformanceLineageService._load_transform(db, transform_id)

    @staticmethod
    async def get_summary(
        db: AsyncSession,
        performance_id: int,
    ) -> dict[str, Decimal | int | bool | None | str]:
        performance = await PerformanceLineageService._get_performance(
            db,
            performance_id,
        )
        committed, consumed_transform_id, consumed_transform_type = await PerformanceLineageService._source_consumption(
            db,
            performance_id,
        )
        available = None
        status = PerformanceCurrentOperabilityStatus.LINEAGE_UNAVAILABLE.value
        is_current_operable = False
        if performance.effective_weight is not None:
            available = _quantize(_quantize(performance.effective_weight) - committed)
            if available > Decimal("0"):
                status = PerformanceCurrentOperabilityStatus.OPERABLE.value
                is_current_operable = True
                consumed_transform_id = None
                consumed_transform_type = None
            elif consumed_transform_type == PerformanceTransformType.SPLIT.value:
                status = PerformanceCurrentOperabilityStatus.CONSUMED_BY_SPLIT.value
            elif consumed_transform_type == PerformanceTransformType.MERGE.value:
                status = PerformanceCurrentOperabilityStatus.CONSUMED_BY_MERGE.value
        return {
            "performance_id": performance.id,
            "effective_weight": performance.effective_weight,
            "effective_weight_source": performance.effective_weight_source,
            "committed_source_allocated_weight": committed,
            "available_weight": available,
            "is_current_operable": is_current_operable,
            "current_operability_status": status,
            "consumed_by_transform_id": consumed_transform_id,
            "consumed_by_transform_type": consumed_transform_type,
        }


async_performance_lineage_service = PerformanceLineageService()
