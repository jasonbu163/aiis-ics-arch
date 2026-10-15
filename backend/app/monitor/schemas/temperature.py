"""
文件路径: /backend/app/monitor/schemas/temperature.py
功能描述: Monitor 温度与过程曲线响应 Schema
主要功能:
    - 定义温度监控响应结构
"""
import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MonitorTemperatureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime.datetime
    furnace_temp: Optional[float] = None
    coil_temp: Optional[float] = None
    tension: Optional[float] = None
    speed: Optional[float] = None
