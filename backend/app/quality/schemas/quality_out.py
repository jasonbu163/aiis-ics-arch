"""
文件路径: /backend/app/quality/schemas/quality_out.py
功能描述: 质量模块响应 Schema
主要功能:
    - 定义 SPC 响应结构
"""
import datetime
from decimal import Decimal
from typing import Optional

from common.schema_base import ApiSchema


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
