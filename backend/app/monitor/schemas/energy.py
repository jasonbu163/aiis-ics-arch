"""
文件路径: /backend/app/monitor/schemas/energy.py
功能描述: Monitor 能耗响应 Schema
主要功能:
    - 定义能耗监控响应结构
"""
import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MonitorEnergyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime.datetime
    power_consumption: Optional[float] = None
    gas_consumption: Optional[float] = None
    total_energy: Optional[float] = None
