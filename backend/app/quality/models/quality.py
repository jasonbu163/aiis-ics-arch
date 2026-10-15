"""
文件路径: /backend/app/quality/models/quality.py
功能描述: 质量管理数据模型定义
主要功能:
    - 定义质量检验、缺陷记录与 SPC 测量点表结构
    - 使用 SQLAlchemy 2.0 现代风格
"""
import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, IntPk, Timestamp, UpdatedAt


class QualityInspection(Base):
    """质量检验模型"""

    __tablename__ = "quality_inspections"

    id: Mapped[IntPk]

    coil_no: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="料卷号")
    grade: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="牌号")
    spec: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="规格")
    weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True, comment="重量(吨)")

    start_time: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=True, comment="生产开始时间")
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=True, comment="生产结束时间")
    operator: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="操作员")
    shift: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="班次")

    quality_items: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="质量检查项目JSON")

    judgment: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="综合判定")
    quality_grade: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="质量等级")
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="质量评语")

    inspector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="检验员")
    inspect_time: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=True, comment="检验时间")

    coil_images: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, comment="钢卷图片URL列表")

    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    defects: Mapped[List["QualityDefectRecord"]] = relationship(
        "QualityDefectRecord", back_populates="inspection", cascade="all, delete-orphan"
    )


class QualityDefectRecord(Base):
    """缺陷记录模型"""

    __tablename__ = "quality_defect_records"

    id: Mapped[IntPk]
    inspection_id: Mapped[int] = mapped_column(
        ForeignKey("quality_inspections.id", ondelete="CASCADE"), index=True, nullable=False
    )

    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="缺陷位置")
    defect_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="缺陷类型")
    level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="缺陷等级")
    length: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True, comment="缺陷长度(mm)")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="缺陷描述")
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="缺陷图片URL")

    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    inspection: Mapped["QualityInspection"] = relationship("QualityInspection", back_populates="defects")


class QualitySPCMeasurement(Base):
    """SPC 测量点模型"""

    __tablename__ = "quality_spc_measurements"

    id: Mapped[IntPk]
    coil_no: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="料卷号")
    grade: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True, comment="牌号")
    item: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="分析项目")
    value: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, comment="测量值")
    operator: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="操作员")
    measured_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
        server_default=func.now(),
        comment="测量时间",
    )
    is_normal: Mapped[bool] = mapped_column(nullable=False, default=True, comment="是否正常点")

    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]
