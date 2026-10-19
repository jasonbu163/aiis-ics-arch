"""HTTP映射回执及精确键类型；显式迁移拥有DDL。"""
from datetime import datetime
from sqlalchemy import DateTime, String
from sqlalchemy.dialects.mysql import DATETIME

def identifier_type():
    return String(128).with_variant(String(128, collation="utf8mb4_bin"), "mysql")
def millisecond_type():
    return DateTime().with_variant(DATETIME(fsp=3), "mysql")
from sqlalchemy import Integer, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, JSON, text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class MonitorMappingReceipt(Base):
    __tablename__ = "monitor_mapping_receipts"
    __table_args__ = (
        UniqueConstraint("actor_user_id", "equipment_id", "stream", "sample_id", name="uq_monitor_mapping_delivery"),
        ForeignKeyConstraint(["curve_record_id", "equipment_id"], ["monitor_history_process_curves.id", "monitor_history_process_curves.equipment_id"], name="fk_monitor_receipt_curve_record_id"),
        CheckConstraint("(stream = 'process_curve' AND curve_record_id IS NOT NULL)", name="ck_monitor_mapping_stream_target"),
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
    curve_record_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
