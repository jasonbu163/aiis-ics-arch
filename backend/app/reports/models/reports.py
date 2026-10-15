"""
文件路径: /backend/app/reports/models/reports.py
功能描述: 报表管理数据模型定义
主要功能:
    - 使用 SQLAlchemy 2.0 现代风格 (Mapped, mapped_column, relationship)
"""
from typing import Optional
# from datetime import datetime, date
import datetime
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Date, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base, IntPk, Timestamp, UpdatedAt


class QualityRecord(Base):
    """质量检查记录"""
    __tablename__ = "quality_records"

    id: Mapped[IntPk]
    performance_id: Mapped[int] = mapped_column(ForeignKey("performance_main.id"), nullable=False, index=True)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    standard_value: Mapped[Optional[str]] = mapped_column(String(100))
    actual_value: Mapped[Optional[str]] = mapped_column(String(100))
    result: Mapped[Optional[str]] = mapped_column(String(20))
    inspector: Mapped[Optional[str]] = mapped_column(String(100))
    inspect_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    remark: Mapped[Optional[str]] = mapped_column(String(500))
    
    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]


class DefectRecord(Base):
    """缺陷记录"""
    __tablename__ = "defect_records"

    id: Mapped[IntPk]
    quality_record_id: Mapped[int] = mapped_column(ForeignKey("quality_records.id"), nullable=False, index=True)
    position: Mapped[Optional[str]] = mapped_column(String(100))
    defect_type: Mapped[Optional[str]] = mapped_column(String(50))
    defect_level: Mapped[Optional[str]] = mapped_column(String(20))
    length: Mapped[Optional[int]] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    created_at: Mapped[Timestamp]


class PerformanceTarget(Base):
    """生产目标设定"""
    __tablename__ = "performance_targets"

    id: Mapped[IntPk]
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    period_type: Mapped[Optional[str]] = mapped_column(String(20))
    period_start: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    period_end: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    
    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]


class Assessment(Base):
    """员工评估记录"""
    __tablename__ = "assessments"

    id: Mapped[IntPk]
    employee_id: Mapped[int] = mapped_column(nullable=False, index=True)
    employee_name: Mapped[Optional[str]] = mapped_column(String(100))
    assessment_type: Mapped[Optional[str]] = mapped_column(String(50))
    assessment_period: Mapped[Optional[str]] = mapped_column(String(20))
    production_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    quality_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    efficiency_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    overall_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    grade: Mapped[Optional[str]] = mapped_column(String(10))
    comments: Mapped[Optional[str]] = mapped_column(String(1000))
    assessor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    assessment_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    
    created_at: Mapped[Timestamp]


class ProductionReport(Base):
    """生产报表"""
    __tablename__ = "production_reports"

    id: Mapped[IntPk]
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    report_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True)
    shift: Mapped[Optional[str]] = mapped_column(String(20))
    total_coils: Mapped[Optional[int]] = mapped_column()
    total_weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    qualified_coils: Mapped[Optional[int]] = mapped_column()
    qualified_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    oee: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    efficiency: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    energy_consumption: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    
    created_at: Mapped[Timestamp]


class PrintRecord(Base):
    """打印记录"""
    __tablename__ = "print_records"

    id: Mapped[IntPk]
    performance_id: Mapped[int] = mapped_column(ForeignKey("performance_main.id"), nullable=False, index=True)
    print_type: Mapped[Optional[str]] = mapped_column(String(50))
    print_status: Mapped[str] = mapped_column(String(20), default="pending")
    print_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    operator_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    
    created_at: Mapped[Timestamp]
