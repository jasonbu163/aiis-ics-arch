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


class PerformanceIntegrationReceipt(Base):
    __tablename__ = "performance_integration_receipts"
    __table_args__ = (
        UniqueConstraint("producer_id", "event_id", name="uq_performance_integration_delivery"),
        CheckConstraint("outcome IN ('created', 'updated', 'duplicate', 'stale')", name="ck_performance_integration_outcome"),
        ForeignKeyConstraint(["performance_id", "equipment_id"], ["performance_main.id", "performance_main.equipment_id"], name="fk_performance_integration_parent"),
        ForeignKeyConstraint(['temperature_record_id', 'equipment_id', 'performance_id'], ['performance_process_temperature.id', 'performance_process_temperature.equipment_id', 'performance_process_temperature.performance_id'], name="fk_performance_integration_temperature"),
        ForeignKeyConstraint(['tension_record_id', 'equipment_id', 'performance_id'], ['performance_process_tension.id', 'performance_process_tension.equipment_id', 'performance_process_tension.performance_id'], name="fk_performance_integration_tension"),
        ForeignKeyConstraint(['speed_record_id', 'equipment_id', 'performance_id'], ['performance_process_speed.id', 'performance_process_speed.equipment_id', 'performance_process_speed.performance_id'], name="fk_performance_integration_speed"),
        CheckConstraint("(stream = 'production_observation' AND temperature_record_id IS NULL AND tension_record_id IS NULL AND speed_record_id IS NULL) OR (stream = 'process_temperature' AND performance_id IS NOT NULL AND temperature_record_id IS NOT NULL AND tension_record_id IS NULL AND speed_record_id IS NULL) OR (stream = 'process_tension' AND performance_id IS NOT NULL AND temperature_record_id IS NULL AND tension_record_id IS NOT NULL AND speed_record_id IS NULL) OR (stream = 'process_speed' AND performance_id IS NOT NULL AND temperature_record_id IS NULL AND tension_record_id IS NULL AND speed_record_id IS NOT NULL)", name="ck_performance_integration_target"),
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
    tension_record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    speed_record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    performance_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


class PerformanceIntegrationObservationEvent(Base):
    __tablename__ = "performance_integration_observation_events"
    __table_args__ = (
        UniqueConstraint("equipment_id", "sampled_at", name="uq_performance_integration_observation_time"),
        ForeignKeyConstraint(["performance_id", "equipment_id"], ["performance_main.id", "performance_main.equipment_id"], name="fk_performance_integration_event_parent"),
        CheckConstraint("observation_status IN ('in_production', 'not_in_production', 'unknown')", name="ck_performance_integration_event_status"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[str] = mapped_column(equipment_type(), nullable=False)
    sampled_at: Mapped[datetime] = mapped_column(millisecond_type(), nullable=False)
    business_digest: Mapped[str] = mapped_column(String(71), nullable=False)
    observation_status: Mapped[str] = mapped_column(String(32), nullable=False)
    performance_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mapping_id: Mapped[str] = mapped_column(String(128), nullable=False)
    mapping_revision: Mapped[str] = mapped_column(String(128), nullable=False)
    source_refs: Mapped[list] = mapped_column(JSON, nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)
    committed_at: Mapped[datetime] = mapped_column(millisecond_type(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(millisecond_type(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(millisecond_type(), nullable=False)
