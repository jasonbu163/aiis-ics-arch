"""匿名集成永久最小回执的声明；仅 metadata，无 migration、连接、默认 UTC 或用户伪身份。"""
from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKeyConstraint, Integer, JSON, LargeBinary, String, UniqueConstraint
from sqlalchemy.dialects.mysql import DATETIME, VARBINARY
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


def exact_identity_type():
    # UTF-8 bytes: case, Unicode and trailing bytes compare exactly in MySQL.
    return LargeBinary(512).with_variant(VARBINARY(512), "mysql")


def equipment_type():
    return String(128).with_variant(String(128, collation="utf8mb4_bin"), "mysql")


def millisecond_type():
    return DateTime().with_variant(DATETIME(fsp=3), "mysql")


class EquipmentIntegrationReceipt(Base):
    __tablename__ = "equipment_integration_receipts"
    __table_args__ = (
        UniqueConstraint("producer_id", "event_id", name="uq_equipment_integration_delivery"),
        CheckConstraint("outcome IN ('created', 'updated', 'duplicate')", name="ck_equipment_integration_outcome"),
        ForeignKeyConstraint(['temperature_record_id', 'equipment_id'], ['equipment_temperature_samples.id', 'equipment_temperature_samples.equipment_id'], name="fk_equipment_integration_temperature"),
        ForeignKeyConstraint(['drive_record_id', 'equipment_id'], ['equipment_drive.id', 'equipment_drive.equipment_id'], name="fk_equipment_integration_drive"),
        ForeignKeyConstraint(['parameter_record_id', 'equipment_id'], ['equipment_production_parameters.id', 'equipment_production_parameters.equipment_id'], name="fk_equipment_integration_parameter"),
        CheckConstraint("(stream = 'temperature' AND temperature_record_id IS NOT NULL AND drive_record_id IS NULL AND parameter_record_id IS NULL) OR (stream = 'drive' AND temperature_record_id IS NULL AND drive_record_id IS NOT NULL AND parameter_record_id IS NULL) OR (stream = 'production_parameters' AND temperature_record_id IS NULL AND drive_record_id IS NULL AND parameter_record_id IS NOT NULL)", name="ck_equipment_integration_target"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    producer_id: Mapped[bytes] = mapped_column(exact_identity_type(), nullable=False)
    event_id: Mapped[bytes] = mapped_column(exact_identity_type(), nullable=False)
    contract_version: Mapped[str] = mapped_column(String(64), nullable=False)
    digest_profile: Mapped[str] = mapped_column(String(32), nullable=False)
    equipment_id: Mapped[str] = mapped_column(equipment_type(), nullable=False)
    stream: Mapped[str] = mapped_column(String(32), nullable=False)
    mapping_id: Mapped[str] = mapped_column(String(128), nullable=False)
    mapping_revision: Mapped[str] = mapped_column(String(128), nullable=False)
    source_refs: Mapped[list] = mapped_column(JSON, nullable=False)
    request_digest: Mapped[str] = mapped_column(String(71), nullable=False)
    business_digest: Mapped[str] = mapped_column(String(71), nullable=False)
    source_time: Mapped[datetime] = mapped_column(millisecond_type(), nullable=False)
    committed_at: Mapped[datetime] = mapped_column(millisecond_type(), nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(millisecond_type(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(millisecond_type(), nullable=False)
    temperature_record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    drive_record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parameter_record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
