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

class PerformanceMappingReceipt(Base):
    __tablename__ = "performance_mapping_receipts"
    __table_args__ = (
        UniqueConstraint("actor_user_id", "equipment_id", "stream", "sample_id", name="uq_performance_mapping_delivery"),
        ForeignKeyConstraint(["performance_id", "equipment_id"], ["performance_main.id", "performance_main.equipment_id"], name="fk_performance_receipt_parent"),
        ForeignKeyConstraint(["temperature_record_id", "equipment_id", "performance_id"], ["performance_process_temperature.id", "performance_process_temperature.equipment_id", "performance_process_temperature.performance_id"], name="fk_performance_receipt_temperature"),
        ForeignKeyConstraint(["tension_record_id", "equipment_id", "performance_id"], ["performance_process_tension.id", "performance_process_tension.equipment_id", "performance_process_tension.performance_id"], name="fk_performance_receipt_tension"),
        ForeignKeyConstraint(["speed_record_id", "equipment_id", "performance_id"], ["performance_process_speed.id", "performance_process_speed.equipment_id", "performance_process_speed.performance_id"], name="fk_performance_receipt_speed"),
        CheckConstraint("(stream = 'production_observation' AND temperature_record_id IS NULL AND tension_record_id IS NULL AND speed_record_id IS NULL) OR (stream = 'process_temperature' AND performance_id IS NOT NULL AND temperature_record_id IS NOT NULL AND tension_record_id IS NULL AND speed_record_id IS NULL) OR (stream = 'process_tension' AND performance_id IS NOT NULL AND temperature_record_id IS NULL AND tension_record_id IS NOT NULL AND speed_record_id IS NULL) OR (stream = 'process_speed' AND performance_id IS NOT NULL AND temperature_record_id IS NULL AND tension_record_id IS NULL AND speed_record_id IS NOT NULL)", name="ck_performance_mapping_stream_target"),
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
    performance_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    temperature_record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tension_record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    speed_record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(millisecond_type(), server_default=text("(UTC_TIMESTAMP(3))"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(millisecond_type(), server_default=text("(UTC_TIMESTAMP(3))"), nullable=False)

class PerformanceObservationState(Base):
    __tablename__ = "performance_mapping_observation_state"
    __table_args__ = (
        UniqueConstraint("equipment_id", name="uq_performance_observation_equipment"),
        ForeignKeyConstraint(["performance_id", "equipment_id"], ["performance_main.id", "performance_main.equipment_id"], name="fk_performance_observation_parent"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[str] = mapped_column(identifier_type(), nullable=False)
    last_sampled_at: Mapped[datetime | None] = mapped_column(millisecond_type(), nullable=True)
    fingerprint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    performance_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    observation_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(millisecond_type(), server_default=text("(UTC_TIMESTAMP(3))"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(millisecond_type(), server_default=text("(UTC_TIMESTAMP(3))"), onupdate=text("UTC_TIMESTAMP(3)"), nullable=False)

def binary_key_type():
    return LargeBinary(200).with_variant(VARBINARY(200), "mysql")
