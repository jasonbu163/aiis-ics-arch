"""
文件路径: /backend/app/maintenance/models/maintenance.py
功能描述: 维保模块数据模型定义
主要功能:
    - 定义维保项模型
    - 定义维保日志模型
    - 使用 SQLAlchemy 2.0 现代风格
"""
import datetime
from typing import List, Optional

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, IntPk, Timestamp, UpdatedAt


class Maintenance(Base):
    """维保模型"""

    __tablename__ = "maintenance"

    id: Mapped[IntPk]
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)
    maintenance_type: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="normal")
    location: Mapped[Optional[str]] = mapped_column(String(100))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    purchase_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    remark: Mapped[Optional[str]] = mapped_column(String(500))

    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    maintenance_logs: Mapped[List["MaintenanceLog"]] = relationship("MaintenanceLog", back_populates="maintenance")


class MaintenanceLog(Base):
    """维保日志模型"""

    __tablename__ = "maintenance_logs"

    id: Mapped[IntPk]
    maintenance_id: Mapped[int] = mapped_column(ForeignKey("maintenance.id"), nullable=False, index=True)
    maintenance_type: Mapped[Optional[str]] = mapped_column(String(50))
    content: Mapped[Optional[str]] = mapped_column(String(500))
    last_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    next_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    cycle_days: Mapped[Optional[int]] = mapped_column()
    status: Mapped[str] = mapped_column(String(20), default="pending")
    operator: Mapped[Optional[str]] = mapped_column(String(100))
    remark: Mapped[Optional[str]] = mapped_column(String(500))

    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    maintenance: Mapped["Maintenance"] = relationship("Maintenance", back_populates="maintenance_logs")
