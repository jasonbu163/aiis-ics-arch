"""
文件路径: /backend/app/maintenance/schemas/maintenance_query.py
功能描述: 维保管理查询参数模型
主要功能:
    - 定义维保项筛选查询参数
    - 定义保养记录筛选查询参数
"""
from typing import Optional

from pydantic import BaseModel


class MaintenanceQuery(BaseModel):
    maintenance_type: Optional[str] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


class MaintenanceLogQuery(BaseModel):
    maintenance_id: Optional[int] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20
