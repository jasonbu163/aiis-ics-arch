"""
文件路径: /backend/app/quality/schemas/quality_in.py
功能描述: 质量模块写入 Schema
主要功能:
    - 定义质量检验创建与更新入参
    - 定义缺陷记录创建与更新入参
"""
import datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import Field

from common.schema_base import ApiSchema


class DefectRecordCreate(ApiSchema):
    position: Optional[str] = Field(default=None, max_length=100)
    defect_type: Optional[str] = Field(default=None, max_length=50)
    level: Optional[str] = Field(default=None, max_length=20)
    length: Optional[Decimal] = Field(default=None, ge=0)
    description: Optional[str] = None
    image_url: Optional[str] = Field(default=None, max_length=500)


class DefectRecordUpdate(ApiSchema):
    position: Optional[str] = None
    defect_type: Optional[str] = None
    level: Optional[str] = None
    length: Optional[Decimal] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class QualityInspectionCreate(ApiSchema):
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
    defects: Optional[List[DefectRecordCreate]] = None


class QualityInspectionUpdate(ApiSchema):
    grade: Optional[str] = None
    spec: Optional[str] = None
    weight: Optional[Decimal] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    operator: Optional[str] = None
    shift: Optional[str] = None
    quality_items: Optional[List[Any]] = None
    judgment: Optional[str] = None
    quality_grade: Optional[str] = None
    comment: Optional[str] = None
    inspector: Optional[str] = None
    inspect_time: Optional[datetime.datetime] = None
    coil_images: Optional[List[str]] = None
    defects: Optional[List[DefectRecordCreate]] = None
