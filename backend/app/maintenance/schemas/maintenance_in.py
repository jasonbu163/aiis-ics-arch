"""
文件路径: /backend/app/maintenance/schemas/maintenance_in.py
功能描述: 维保管理创建和更新入参模型
主要功能:
    - 定义维保项写入模型
    - 定义保养记录写入模型
"""
import datetime
from typing import Optional

from common.schema_base import ApiSchema


class MaintenanceCreate(ApiSchema):
    name: str
    code: str
    maintenance_type: Optional[str] = None
    status: str = "normal"
    location: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    purchase_date: Optional[datetime.date] = None
    remark: Optional[str] = None


class MaintenanceUpdate(ApiSchema):
    name: Optional[str] = None
    maintenance_type: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    purchase_date: Optional[datetime.date] = None
    remark: Optional[str] = None


class MaintenanceLogCreate(ApiSchema):
    maintenance_id: int
    maintenance_type: Optional[str] = None
    content: Optional[str] = None
    last_date: Optional[datetime.date] = None
    next_date: Optional[datetime.date] = None
    cycle_days: Optional[int] = None
    status: str = "pending"
    operator: Optional[str] = None
    remark: Optional[str] = None


class MaintenanceLogUpdate(ApiSchema):
    maintenance_type: Optional[str] = None
    content: Optional[str] = None
    last_date: Optional[datetime.date] = None
    next_date: Optional[datetime.date] = None
    cycle_days: Optional[int] = None
    status: Optional[str] = None
    operator: Optional[str] = None
    remark: Optional[str] = None
