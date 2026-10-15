"""
文件路径: /backend/app/auxiliary/schemas/auxiliary_query.py
功能描述: 辅助管理查询参数模型
主要功能:
    - 定义班组分页查询参数
    - 定义班次筛选查询参数
    - 定义停机记录筛选查询参数
"""
from typing import Optional

from pydantic import BaseModel


class ShiftTeamQuery(BaseModel):
    page: int = 1
    page_size: int = 20


class ShiftQuery(BaseModel):
    team_id: Optional[int] = None
    page: int = 1
    page_size: int = 20


class StopRecordQuery(BaseModel):
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20
