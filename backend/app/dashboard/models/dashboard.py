"""
文件路径: /backend/app/dashboard/models/dashboard.py
功能描述: Dashboard 看板数据模型定义
主要功能:
    - 使用 SQLAlchemy 2.0 现代风格 (Mapped, mapped_column)
"""
from typing import Optional
# from datetime import datetime, date
import datetime
from decimal import Decimal
from sqlalchemy import String, Numeric, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from database import Base, IntPk, Timestamp, UpdatedAt


class DailyProductionStats(Base):
    """每日生产统计模型"""
    __tablename__ = "daily_production_stats"
    
    id: Mapped[IntPk]
    stats_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, unique=True, index=True, comment="统计日期")
    
    production_weight: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0, comment="生产重量(吨)")
    completed_coils: Mapped[int] = mapped_column(default=0, comment="完成卷数")
    target_weight: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0, comment="目标重量(吨)")
    
    oee_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, comment="OEE比率(%)")
    availability_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, comment="可用率(%)")
    performance_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, comment="性能效率(%)")
    quality_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, comment="质量指数(%)")
    
    energy_electricity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="电力消耗(kWh)")
    energy_gas: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="天然气消耗(m³)")
    
    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]


class QualityGradeStats(Base):
    """质量等级统计模型"""
    __tablename__ = "quality_grade_stats"
    
    id: Mapped[IntPk]
    stats_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True, comment="统计日期")
    
    grade_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="等级名称")
    grade_count: Mapped[int] = mapped_column(default=0, comment="数量")
    grade_color: Mapped[str] = mapped_column(String(20), default="#1890ff", comment="显示颜色")
    
    created_at: Mapped[Timestamp]


class DowntimeRecord(Base):
    """停机记录模型"""
    __tablename__ = "downtime_records"
    
    id: Mapped[IntPk]
    stats_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True, comment="统计日期")
    
    reason: Mapped[str] = mapped_column(String(100), nullable=False, comment="停机原因")
    duration_minutes: Mapped[int] = mapped_column(default=0, comment="停机时长(分钟)")
    color: Mapped[str] = mapped_column(String(20), default="#1890ff", comment="显示颜色")
    
    created_at: Mapped[Timestamp]


class ProductionStatusRecord(Base):
    """生产状态记录模型"""
    __tablename__ = "production_status_records"
    
    id: Mapped[IntPk]
    record_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True, comment="记录时间")
    
    online_coil_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="在线卷号")
    online_coil_progress: Mapped[int] = mapped_column(default=0, comment="在线卷进度(%)")
    online_coil_status: Mapped[str] = mapped_column(String(50), default="生产中", comment="在线卷状态")
    
    ready_coil_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="准备卷号")
    ready_coil_grade: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="准备卷牌号")
    ready_coil_weight: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0, comment="准备卷重量")
    
    current_speed: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, comment="当前速度(m/min)")
    furnace_temp: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, comment="炉区温度(℃)")
    
    created_at: Mapped[Timestamp]


class TemperatureZoneRecord(Base):
    """炉区温度记录模型"""
    __tablename__ = "temperature_zone_records"
    
    id: Mapped[IntPk]
    record_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True, comment="记录时间")
    
    zone_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="区域名称")
    temperature: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, comment="温度(℃)")
    
    created_at: Mapped[Timestamp]
