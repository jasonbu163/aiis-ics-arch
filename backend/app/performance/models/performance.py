"""
文件路径: /backend/app/performance/models/performance.py
功能描述: 生产实绩数据模型定义
主要功能:
    - 使用 SQLAlchemy 2.0 现代风格 (Mapped, mapped_column, relationship)
"""

from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Performance(Base):
    """生产实绩模型"""
    __tablename__ = "performance_main"

    __table_args__ = (
        UniqueConstraint("device_id", "coil_no", name="uq_performance_main_device_coil"),
        Index(
            "ix_performance_main_device_observation_status",
            "device_id",
            "observation_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    plan_id: Mapped[int | None] = mapped_column(ForeignKey("plans.id"), nullable=True)
    coil_no: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_coil_no: Mapped[str] = mapped_column(String(50), nullable=False)
    grade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    spec: Mapped[str | None] = mapped_column(String(50))
    weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    total_length: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    diameter: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    density: Mapped[Decimal | None] = mapped_column(Numeric(5, 3))
    production_date: Mapped[date] = mapped_column(nullable=False)
    start_time: Mapped[datetime | None] = mapped_column(nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(nullable=True)
    output_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False, default=0)
    qualified_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False, default=0)
    efficiency_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), default=0, server_default="0.00")
    quality_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), default=0, server_default="0.00")
    collected_weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    manual_override_weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    effective_weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    effective_weight_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    manual_override_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    manual_override_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    manual_override_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    total_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_duration_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_split: Mapped[bool] = mapped_column(default=False)
    remark: Mapped[str | None] = mapped_column(String(500))

    # PLC projection provenance. Legacy/manual rows keep these fields NULL.
    device_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    observation_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    record_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    first_observed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_observed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    first_raw_snapshot_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_raw_snapshot_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    plc_key: Mapped[str | None] = mapped_column(String(80), nullable=True)
    db_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    group_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    plan: Mapped["Plan | None"] = relationship("Plan", back_populates="performances")
    splits: Mapped[list["Split"]] = relationship("Split", back_populates="performance", cascade="all, delete-orphan")
    temperature_records: Mapped[list["ProcessTemperature"]] = relationship("ProcessTemperature", back_populates="performance", cascade="all, delete-orphan")
    tension_records: Mapped[list["ProcessTension"]] = relationship("ProcessTension", back_populates="performance", cascade="all, delete-orphan")
    speed_records: Mapped[list["ProcessSpeed"]] = relationship("ProcessSpeed", back_populates="performance", cascade="all, delete-orphan")
    push_down_records: Mapped[list["PushDownRecord"]] = relationship("PushDownRecord", back_populates="performance", cascade="all, delete-orphan")
    lineage_entries: Mapped[list["PerformanceLineage"]] = relationship("PerformanceLineage", back_populates="performance")


class Split(Base):
    """分卷模型"""
    __tablename__ = "performance_split"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    performance_id: Mapped[int] = mapped_column(ForeignKey("performance_main.id"), nullable=False)
    split_no: Mapped[str] = mapped_column(String(50), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    spec: Mapped[str] = mapped_column(String(50), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    performance: Mapped["Performance"] = relationship("Performance", back_populates="splits")


class ProcessTemperature(Base):
    """温度过程数据模型"""
    __tablename__ = "performance_process_temperature"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    performance_id: Mapped[int] = mapped_column(ForeignKey('performance_main.id'), nullable=False, index=True)
    zone: Mapped[str] = mapped_column(String(50), nullable=False)
    set_temp: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    max_temp: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    min_temp: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    avg_temp: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    duration: Mapped[Decimal | None] = mapped_column()
    record_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    performance: Mapped["Performance"] = relationship("Performance", back_populates="temperature_records")


class ProcessTension(Base):
    """张力过程数据模型"""
    __tablename__ = "performance_process_tension"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    performance_id: Mapped[int] = mapped_column(ForeignKey('performance_main.id'), nullable=False, index=True)
    zone: Mapped[str] = mapped_column(String(50), nullable=False)
    set_tension: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    avg_tension: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    max_tension: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    min_tension: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    record_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    performance: Mapped["Performance"] = relationship("Performance", back_populates="tension_records")


class ProcessSpeed(Base):
    """速度过程数据模型"""
    __tablename__ = "performance_process_speed"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    performance_id: Mapped[int] = mapped_column(ForeignKey('performance_main.id'), nullable=False, index=True)
    zone: Mapped[str] = mapped_column(String(50), nullable=False)
    set_speed: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    avg_speed: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    max_speed: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    record_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    performance: Mapped["Performance"] = relationship("Performance", back_populates="speed_records")


class PushDownRecord(Base):
    """下推记录模型"""
    __tablename__ = "performance_push_down_record"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    performance_id: Mapped[int] = mapped_column(ForeignKey('performance_main.id'), nullable=False, index=True)
    push_down_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_system: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default='pending')
    message: Mapped[str | None] = mapped_column(String(500))
    operator_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    performance: Mapped["Performance"] = relationship("Performance", back_populates="push_down_records")


class PerformanceTransform(Base):
    """实绩卷材业务变换头记录。"""

    __tablename__ = "performance_transform"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    transform_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    quantity_dimension: Mapped[str] = mapped_column(String(20), nullable=False, default="weight")
    requested_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    requested_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confirmed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    effective_weight_context: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    lineage_entries: Mapped[list["PerformanceLineage"]] = relationship(
        "PerformanceLineage",
        back_populates="transform",
        cascade="all, delete-orphan",
    )


class PerformanceLineage(Base):
    """实绩卷材变换谱系边。"""

    __tablename__ = "performance_lineage"

    __table_args__ = (
        Index("ix_performance_lineage_transform_role", "transform_id", "role"),
        Index("ix_performance_lineage_performance_role", "performance_id", "role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    transform_id: Mapped[int] = mapped_column(ForeignKey("performance_transform.id"), nullable=False)
    performance_id: Mapped[int] = mapped_column(ForeignKey("performance_main.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    allocated_weight: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    effective_weight_snapshot: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    effective_weight_source_snapshot: Mapped[str] = mapped_column(String(32), nullable=False)
    available_weight_before_snapshot: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    available_weight_after_snapshot: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    transform: Mapped["PerformanceTransform"] = relationship("PerformanceTransform", back_populates="lineage_entries")
    performance: Mapped["Performance"] = relationship("Performance", back_populates="lineage_entries")
