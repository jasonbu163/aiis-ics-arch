"""完整不可变样本及投递回执；两unique与UTC毫秒由显式迁移建立。"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, String, UniqueConstraint, text
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


def identifier_type():
    return String(128).with_variant(String(128, collation="utf8mb4_bin"), "mysql")


def millisecond_type():
    return DateTime().with_variant(DATETIME(fsp=3), "mysql")


class EquipmentTemperatureSample(Base):
    __tablename__ = "equipment_temperature_samples"
    __table_args__ = (
        UniqueConstraint("equipment_id", "sampled_at", name="uq_temperature_sample_business"),
        UniqueConstraint("id", "equipment_id", name="uq_temperature_sample_id_equipment"),
        CheckConstraint("quality = 'good'", name="ck_temperature_sample_quality"),
        Index("ix_temperature_sample_equipment_time_id", "equipment_id", "sampled_at", "id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[str] = mapped_column(identifier_type(), nullable=False)
    sampled_at: Mapped[datetime] = mapped_column(millisecond_type(), nullable=False)
    quality: Mapped[str] = mapped_column(String(16), nullable=False)
    zone1_set: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    zone1_act: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    zone2_set: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    zone2_act: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    zone3_set: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    zone3_act: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    zone4_set: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    zone4_act: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    zone5_set: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    zone5_act: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(millisecond_type(), server_default=text("(UTC_TIMESTAMP(3))"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(millisecond_type(), server_default=text("(UTC_TIMESTAMP(3))"), nullable=False)


class EquipmentTemperatureSampleReceipt(Base):
    __tablename__ = "equipment_temperature_sample_receipts"
    __table_args__ = (
        UniqueConstraint("actor_user_id", "equipment_id", "sample_id", name="uq_temperature_sample_delivery"),
        ForeignKeyConstraint(["sample_record_id", "equipment_id"],
                             ["equipment_temperature_samples.id", "equipment_temperature_samples.equipment_id"],
                             name="fk_temperature_receipt_sample_equipment"),
        CheckConstraint("outcome IN ('created', 'duplicate')", name="ck_temperature_receipt_outcome"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    equipment_id: Mapped[str] = mapped_column(identifier_type(), nullable=False)
    sample_id: Mapped[str] = mapped_column(identifier_type(), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    sample_record_id: Mapped[int] = mapped_column(Integer, nullable=False)
    sampled_at: Mapped[datetime] = mapped_column(millisecond_type(), nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(millisecond_type(), server_default=text("(UTC_TIMESTAMP(3))"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(millisecond_type(), server_default=text("(UTC_TIMESTAMP(3))"), nullable=False)
