"""
文件路径: /backend/app/performance/schemas/performance_query.py
功能描述: 实绩管理查询参数模型
主要功能:
    - 定义实绩列表查询参数
    - 定义分卷列表查询参数
"""
import datetime
from typing import Optional

from pydantic import BaseModel


class PerformanceQuery(BaseModel):
    page: int = 1
    page_size: int = 20
    coil_no: Optional[str] = None
    grade: Optional[str] = None
    observation_status: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None


class SplitQuery(BaseModel):
    page: int = 1
    page_size: int = 20
    parent_coil_no: Optional[str] = None
