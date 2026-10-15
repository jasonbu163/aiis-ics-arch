"""
文件路径: /backend/app/equipment/models/equipment.py
功能描述: 设备管理/工艺监控数据模型定义
主要功能:
    - 定义传动参数仪表盘数据
    - 定义温控参数仪表盘数据
    - 定义生产参数仪表盘数据
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base, IntPk, Timestamp


class EquipmentDrive(Base):
    """传动参数仪表盘数据"""

    __tablename__ = "equipment_drive"

    id: Mapped[IntPk]
    timestamp: Mapped[Timestamp] = mapped_column(index=True)

    tv: Mapped[float] = mapped_column(Float, default=0.0)
    km: Mapped[float] = mapped_column(Float, default=0.0)
    dew_point_set: Mapped[float] = mapped_column(Float, default=0.0)
    dew_point_actual: Mapped[float] = mapped_column(Float, default=0.0)
    oxygen: Mapped[float] = mapped_column(Float, default=0.0)
    muffle_pressure: Mapped[float] = mapped_column(Float, default=0.0)
    nh3_flow_set: Mapped[float] = mapped_column(Float, default=0.0)
    nh3_flow_actual: Mapped[float] = mapped_column(Float, default=0.0)
    ng_flow_set: Mapped[float] = mapped_column(Float, default=0.0)
    ng_flow_actual: Mapped[float] = mapped_column(Float, default=0.0)

    uncoiler_set: Mapped[float] = mapped_column(Float, default=0.0)
    uncoiler_actual: Mapped[float] = mapped_column(Float, default=0.0)
    entry_looper_set: Mapped[float] = mapped_column(Float, default=0.0)
    entry_looper_actual: Mapped[float] = mapped_column(Float, default=0.0)
    furnace_set: Mapped[float] = mapped_column(Float, default=0.0)
    furnace_actual: Mapped[float] = mapped_column(Float, default=0.0)
    exit_looper_set: Mapped[float] = mapped_column(Float, default=0.0)
    exit_looper_actual: Mapped[float] = mapped_column(Float, default=0.0)
    recoiler_set: Mapped[float] = mapped_column(Float, default=0.0)
    recoiler_actual: Mapped[float] = mapped_column(Float, default=0.0)


class EquipmentTemperature(Base):
    """温控参数仪表盘数据"""

    __tablename__ = "equipment_temperature"

    id: Mapped[IntPk]
    timestamp: Mapped[Timestamp] = mapped_column(index=True)

    zone1_set: Mapped[float] = mapped_column(Float, default=0.0)
    zone1_act: Mapped[float] = mapped_column(Float, default=0.0)
    zone2_set: Mapped[float] = mapped_column(Float, default=0.0)
    zone2_act: Mapped[float] = mapped_column(Float, default=0.0)
    zone3_set: Mapped[float] = mapped_column(Float, default=0.0)
    zone3_act: Mapped[float] = mapped_column(Float, default=0.0)
    zone4_set: Mapped[float] = mapped_column(Float, default=0.0)
    zone4_act: Mapped[float] = mapped_column(Float, default=0.0)
    zone5_set: Mapped[float] = mapped_column(Float, default=0.0)
    zone5_act: Mapped[float] = mapped_column(Float, default=0.0)


class EquipmentProductionParameters(Base):
    """生产参数仪表盘数据"""

    __tablename__ = "equipment_production_parameters"

    id: Mapped[IntPk]
    timestamp: Mapped[Timestamp] = mapped_column(index=True)

    coil_no: Mapped[str] = mapped_column(String(50), default="")
    grade: Mapped[str] = mapped_column(String(50), default="")
    thickness: Mapped[float] = mapped_column(Float, default=0.0)
    width: Mapped[float] = mapped_column(Float, default=0.0)
    entry_time: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    total_time: Mapped[float] = mapped_column(Float, default=0.0)
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    speed: Mapped[float] = mapped_column(Float, default=0.0)

    process_steps: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
