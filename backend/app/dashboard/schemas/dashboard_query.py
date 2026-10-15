"""
文件路径: /backend/app/dashboard/schemas/dashboard_query.py
功能描述: Dashboard 查询参数模型
主要功能:
    - 预留看板接口查询参数
    - 为后续时间范围筛选扩展提供边界
"""
from pydantic import BaseModel


class DashboardQuery(BaseModel):
    pass
