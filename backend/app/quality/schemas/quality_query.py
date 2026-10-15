"""
文件路径: /backend/app/quality/schemas/quality_query.py
功能描述: 质量模块查询 Schema
主要功能:
    - 定义质量检验分页与筛选查询参数
"""
from typing import Optional

from pydantic import Field

from common.schema_base import ApiSchema


class QualityQueryParams(ApiSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    coil_no: Optional[str] = None
    grade: Optional[str] = None
    quality_grade: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
