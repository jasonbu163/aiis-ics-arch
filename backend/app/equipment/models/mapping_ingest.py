"""HTTP映射回执及精确键类型；显式迁移拥有DDL。"""
from datetime import datetime
from sqlalchemy import DateTime, String, LargeBinary
from sqlalchemy.dialects.mysql import DATETIME, VARBINARY

def identifier_type():
    return String(128).with_variant(String(128, collation="utf8mb4_bin"), "mysql")
def millisecond_type():
    return DateTime().with_variant(DATETIME(fsp=3), "mysql")
from sqlalchemy import Integer, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, JSON, text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class EquipmentMappingReceipt(Base):
    __tablename__ = "equipment_mapping_receipts"
    __table_args__ = (
        UniqueConstraint("actor_user_id", "equipment_id", "stream", "sample_id", name="uq_equipment_mapping_delivery"),
        ForeignKeyConstraint(["drive_record_id", "equipment_id"], ["equipment_drive.id", "equipment_drive.equipment_id"], name="fk_equipment_receipt_drive_record_id"),
        ForeignKeyConstraint(["parameter_record_id", "equipment_id"], ["equipment_production_parameters.id", "equipment_production_parameters.equipment_id"], name="fk_equipment_receipt_parameter_record_id"),
        CheckConstraint("(stream = 'drive' AND drive_record_id IS NOT NULL AND parameter_record_id IS NULL) OR (stream = 'production_parameters' AND drive_record_id IS NULL AND parameter_record_id IS NOT NULL)", name="ck_equipment_mapping_stream_target"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    equipment_id: Mapped[str] = mapped_column(identifier_type(), nullable=False)
    stream: Mapped[str] = mapped_column(identifier_type(), nullable=False)
    sample_id: Mapped[str] = mapped_column(identifier_type(), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    sampled_at: Mapped[datetime] = mapped_column(millisecond_type(), nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(millisecond_type(), server_default=text("(UTC_TIMESTAMP(3))"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(millisecond_type(), server_default=text("(UTC_TIMESTAMP(3))"), nullable=False)
    drive_record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parameter_record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

def binary_key_type():
    return LargeBinary(200).with_variant(VARBINARY(200), "mysql")
