"""
文件路径: /backend/app/performance/schemas/performance_lineage.py
功能描述: 实绩 transform / lineage API Schema
主要功能:
    - 定义 B17 分卷、合卷、有效重量和谱系响应合同
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from common.schema_base import ApiSchema


class SplitTransformTargetIn(ApiSchema):
    coil_no: str = Field(min_length=1, max_length=50)
    allocated_weight: Decimal = Field(gt=0)
    target_performance_id: int | None = None
    grade: str | None = Field(default=None, max_length=20)
    spec: str | None = Field(default=None, max_length=50)
    remark: str | None = Field(default=None, max_length=500)


class SplitTransformCreateIn(ApiSchema):
    source_performance_id: int
    targets: list[SplitTransformTargetIn]
    reason: str | None = Field(default=None, max_length=500)


class MergeTransformSourceIn(ApiSchema):
    performance_id: int
    allocated_weight: Decimal = Field(gt=0)


class MergeTransformTargetIn(ApiSchema):
    coil_no: str = Field(min_length=1, max_length=50)
    target_performance_id: int | None = None
    grade: str | None = Field(default=None, max_length=20)
    spec: str | None = Field(default=None, max_length=50)
    remark: str | None = Field(default=None, max_length=500)


class MergeTransformCreateIn(ApiSchema):
    sources: list[MergeTransformSourceIn]
    target: MergeTransformTargetIn
    reason: str | None = Field(default=None, max_length=500)


class EffectiveWeightOverrideIn(ApiSchema):
    effective_weight: Decimal = Field(gt=0)
    reason: str = Field(min_length=1, max_length=500)


class PerformanceLineageResponse(ApiSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    transform_id: int
    performance_id: int
    role: str
    allocated_weight: Decimal
    effective_weight_snapshot: Decimal
    effective_weight_source_snapshot: str
    available_weight_before_snapshot: Decimal
    available_weight_after_snapshot: Decimal
    created_at: datetime


class PerformanceTransformResponse(ApiSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    transform_type: str
    status: str
    quantity_dimension: str
    requested_by_id: int | None = None
    requested_reason: str | None = None
    confirmed_by_id: int | None = None
    confirmed_at: datetime | None = None
    effective_weight_context: str | None = None
    created_at: datetime
    updated_at: datetime
    lineage_entries: list[PerformanceLineageResponse] = []


class PerformanceLineageSummaryResponse(ApiSchema):
    performance_id: int
    effective_weight: Decimal | None
    effective_weight_source: str | None
    committed_source_allocated_weight: Decimal
    available_weight: Decimal | None
    is_current_operable: bool
    current_operability_status: str
    consumed_by_transform_id: int | None = None
    consumed_by_transform_type: str | None = None
