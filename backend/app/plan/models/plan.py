"""
文件路径: /backend/app/plan/models/plan.py
功能描述: 生产计划数据模型定义
主要功能:
    - 使用 SQLAlchemy 2.0 现代风格 (Mapped, mapped_column, relationship)
"""
from datetime import datetime
from typing import List
from decimal import Decimal

from sqlalchemy import Integer, String, Numeric, SmallInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

class Plan(Base):
    """生产计划模型"""
    __tablename__ = "plans"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    coil_no: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)
    spec: Mapped[str] = mapped_column(String(50), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    thickness: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    width: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    material_status: Mapped[str] = mapped_column(String(20), nullable=False, default="special")
    density: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    entry_length: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    
    # Tension parameters (2 decimal places)
    uncoiler1_tension: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    exit_tension: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    process1_tension: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    entry_loop_tension: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    exit_loop_tension: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    
    # Unit tension parameters (4 decimal places)
    entry_unit_tension: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=Decimal("0"))
    entry_loop_unit_tension: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=Decimal("0"))
    process_unit_tension: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=Decimal("0"))
    exit_loop_unit_tension: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=Decimal("0"))
    exit_unit_tension: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=Decimal("0"))
    
    status: Mapped[str] = mapped_column(String(20), default="planned", index=True)
    priority: Mapped[int] = mapped_column(SmallInteger, default=5, index=True)
    
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    performances: Mapped[List["Performance"]] = relationship("Performance", back_populates="plan", cascade="all, delete-orphan")
