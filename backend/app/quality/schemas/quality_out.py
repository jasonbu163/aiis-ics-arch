"""
文件路径: /backend/app/quality/schemas/quality_out.py
功能描述: 质量模块响应 Schema
主要功能:
    - 定义质量检验与缺陷记录响应结构
    - 定义 SPC 响应结构
"""
import datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import ConfigDict, Field

from common.schema_base import ApiSchema


class DefectRecordResponse(ApiSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    inspection_id: int
    position: Optional[str] = Field(default=None, max_length=100)
    defect_type: Optional[str] = Field(default=None, max_length=50)
    level: Optional[str] = Field(default=None, max_length=20)
    length: Optional[Decimal] = Field(default=None, ge=0)
    description: Optional[str] = None
    image_url: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None


class QualityInspectionResponse(ApiSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    coil_no: str = Field(..., min_length=1, max_length=50)
    grade: Optional[str] = Field(default=None, max_length=20)
    spec: Optional[str] = Field(default=None, max_length=50)
    weight: Optional[Decimal] = Field(default=None, ge=0)
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    operator: Optional[str] = Field(default=None, max_length=100)
    shift: Optional[str] = Field(default=None, max_length=20)
    quality_items: Optional[List[Any]] = None
    judgment: Optional[str] = Field(default=None, max_length=20)
    quality_grade: Optional[str] = Field(default=None, max_length=20)
    comment: Optional[str] = None
    inspector: Optional[str] = Field(default=None, max_length=100)
    inspect_time: Optional[datetime.datetime] = None
    coil_images: Optional[List[str]] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    defects: List[DefectRecordResponse] = []


class QualityInspectionListResponse(ApiSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    coil_no: str
    grade: Optional[str] = None
    spec: Optional[str] = None
    weight: Optional[Decimal] = None
    quality_grade: Optional[str] = None
    judgment: Optional[str] = None
    inspector: Optional[str] = None
    inspect_time: Optional[datetime.datetime] = None
    created_at: datetime.datetime


class SPCDataPoint(ApiSchema):
    id: int
    coil_no: str
    grade: Optional[str] = None
    value: Decimal
    time: Optional[datetime.datetime] = None
    operator: Optional[str] = None
    is_normal: bool = True


class SPCStats(ApiSchema):
    cp: Decimal
    cpk: Decimal
    sigma: Decimal
    defect_rate: Decimal
    mean: Decimal
    ucl: Decimal
    lcl: Decimal
    usl: Decimal
    lsl: Decimal
