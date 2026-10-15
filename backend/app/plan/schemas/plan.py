"""
文件路径: /backend/app/plan/schemas/plan.py
功能描述: 生产计划数据验证模型定义
主要功能:
    - 定义计划创建、更新、响应的数据结构
    - 查询参数模型
    - 仪表盘统计模型
"""
from pydantic import ConfigDict, Field, field_validator
from typing import Any, Optional
# from datetime import datetime, date
import datetime
from decimal import Decimal

from app.plan.domain import is_valid_coil_no
from common.schema_base import ApiSchema


class PlanBase(ApiSchema):
    coil_no: str = Field(..., min_length=1, max_length=50)
    grade: str = Field(..., min_length=1, max_length=20)
    spec: str = Field(..., min_length=1, max_length=50)
    weight: Decimal = Field(..., ge=0)
    thickness: Decimal = Field(..., ge=0)
    width: Decimal = Field(..., gt=0)
    material_status: str = Field(default="special", description="degreasing, annealing, tension, special")
    density: Decimal = Field(default=Decimal("0"), ge=0)
    entry_length: Decimal = Field(default=Decimal("0"), ge=0)
    uncoiler1_tension: Decimal = Field(default=Decimal("0"), ge=0)
    exit_tension: Decimal = Field(default=Decimal("0"), ge=0)
    process1_tension: Decimal = Field(default=Decimal("0"), ge=0)
    entry_loop_tension: Decimal = Field(default=Decimal("0"), ge=0)
    exit_loop_tension: Decimal = Field(default=Decimal("0"), ge=0)
    entry_unit_tension: Decimal = Field(default=Decimal("0"), ge=0)
    entry_loop_unit_tension: Decimal = Field(default=Decimal("0"), ge=0)
    process_unit_tension: Decimal = Field(default=Decimal("0"), ge=0)
    exit_loop_unit_tension: Decimal = Field(default=Decimal("0"), ge=0)
    exit_unit_tension: Decimal = Field(default=Decimal("0"), ge=0)
    priority: int = Field(default=5, ge=1, le=10, description="优先级 1-10, 默认5")
    remark: Optional[str] = None

    @field_validator("coil_no")
    @classmethod
    def validate_coil_no(cls, value: str) -> str:
        if not is_valid_coil_no(value):
            raise ValueError("plan_invalid_coil_no")
        return value


class PlanCreate(PlanBase):
    pass


class PlanUpdate(ApiSchema):
    grade: Optional[str] = None
    spec: Optional[str] = None
    weight: Optional[Decimal] = None
    thickness: Optional[Decimal] = None
    width: Optional[Decimal] = None
    material_status: Optional[str] = None
    density: Optional[Decimal] = None
    entry_length: Optional[Decimal] = None
    uncoiler1_tension: Optional[Decimal] = None
    exit_tension: Optional[Decimal] = None
    process1_tension: Optional[Decimal] = None
    entry_loop_tension: Optional[Decimal] = None
    exit_loop_tension: Optional[Decimal] = None
    entry_unit_tension: Optional[Decimal] = None
    entry_loop_unit_tension: Optional[Decimal] = None
    process_unit_tension: Optional[Decimal] = None
    exit_loop_unit_tension: Optional[Decimal] = None
    exit_unit_tension: Optional[Decimal] = None
    priority: Optional[int] = Field(default=None, ge=1, le=10)
    remark: Optional[str] = None


class PlanResponse(PlanBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    status: str
    priority: int = 5
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None


class PlanQueryParams(ApiSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    coil_no: Optional[str] = None
    grade: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None


class PlanDashboardStats(ApiSchema):
    status_counts: dict
    priority_counts: dict
    total_count: int
    active_count: int
    pending_count: int


class PlanLinkRequest(ApiSchema):
    plan_id: int = Field(..., gt=0)


class PlanLinkCandidate(ApiSchema):
    id: int
    coil_no: str
    grade: str
    spec: str
    weight: Decimal
    status: str
    priority: int
    match_type: str = "canonical_coil_no"


class PlanPerformanceLinkageResult(ApiSchema):
    performance_id: int
    performance_coil_no: str
    canonical_coil_no: str
    action: str
    linked: bool
    plan_id: int | None = None
    plan_status: str | None = None
    candidate_count: int = 0


class PlanXlsxImportError(ApiSchema):
    row: int | None = None
    field: str | None = None
    error_code: str
    message: str
    detail: dict[str, Any] | None = None


class PlanXlsxImportResult(ApiSchema):
    dry_run: bool
    valid: bool
    created_count: int
    error_count: int
    errors: list[PlanXlsxImportError]
