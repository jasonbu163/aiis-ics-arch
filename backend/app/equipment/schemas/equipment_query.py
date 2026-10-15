"""
文件路径: /backend/app/equipment/schemas/equipment_query.py
功能描述: 设备模块查询 Schema
主要功能:
    - 定义设备看板查询参数
"""
from pydantic import Field

from common.schema_base import ApiSchema


class EquipmentQueryParams(ApiSchema):
    limit: int = Field(default=100, ge=1, le=1000)
