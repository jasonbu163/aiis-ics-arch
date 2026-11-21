"""设备指标配置、两路采样和分域持久回执的 SQLAlchemy 模型。"""
from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.mysql import BIGINT, BINARY, DATETIME, TINYINT

from database import Base

STAMP = text("CURRENT_TIMESTAMP(6)")


class MetricConfig(Base):
    __tablename__ = "observation_metric_configs"
    metric_key = Column(String(64, collation="utf8mb4_bin"), primary_key=True)
    source_group_key = Column(String(64, collation="utf8mb4_bin"), nullable=False)
    category = Column(String(32), nullable=False)
    name_zh = Column(String(128), nullable=False)
    name_en = Column(String(128), nullable=False)
    value_type = Column(String(16), nullable=False)
    unit = Column(String(24))
    decimals = Column(TINYINT(unsigned=True))
    __table_args__ = (CheckConstraint("value_type IN ('number','boolean','string')", name="ck_obs_r10_metric_type"),)


class MetricGroup(Base):
    __tablename__ = "observation_metric_groups"
    group_key = Column(String(64, collation="utf8mb4_bin"), primary_key=True)
    category = Column(String(32), nullable=False)
    name_zh = Column(String(128), nullable=False)
    name_en = Column(String(128), nullable=False)
    enabled = Column(Boolean, nullable=False)
    sort_order = Column(BIGINT, nullable=False)
    __table_args__ = (CheckConstraint("category IN ('production','cleaning','temperature','drive')", name="ck_obs_group_category"),)


class SlotBinding(Base):
    __tablename__ = "observation_metric_slot_bindings"
    target = Column(String(7), primary_key=True)
    group_key = Column(String(64, collation="utf8mb4_bin"), primary_key=True)
    slot_no = Column(TINYINT(unsigned=True), primary_key=True)
    metric_key = Column(String(64, collation="utf8mb4_bin"), ForeignKey("observation_metric_configs.metric_key", name="fk_obs_r10_binding_metric", ondelete="RESTRICT"), nullable=False)
    enabled = Column(Boolean, nullable=False)
    list_visible = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    list_order = Column(Integer)
    first_used_at = Column(DATETIME(fsp=6))
    __table_args__ = (
        UniqueConstraint("target", "group_key", "metric_key", name="uq_obs_r10_binding_metric"),
        CheckConstraint("target IN ('latest','history') AND slot_no BETWEEN 1 AND 100", name="ck_obs_r10_binding_scope"),
        CheckConstraint("list_order IS NULL OR list_order >= 0", name="ck_obs_r10_binding_order"),
    )


class CardConfig(Base):
    __tablename__ = "equipment_card_configs"
    card_key = Column(String(64, collation="utf8mb4_bin"), primary_key=True)
    page_key = Column(String(32), nullable=False)
    title_zh = Column(String(128), nullable=False)
    title_en = Column(String(128), nullable=False)
    enabled = Column(Boolean, nullable=False)
    sort_order = Column(BIGINT, nullable=False)
    items = Column(JSON, nullable=False)
    __table_args__ = (Index("ix_obs_r10_card_page", "page_key", "sort_order", "card_key"),)


class CurveGroup(Base):
    __tablename__ = "monitor_curve_group_configs"
    curve_group_key = Column(String(64, collation="utf8mb4_bin"), primary_key=True)
    category = Column(String(32), nullable=False)
    title_zh = Column(String(128), nullable=False)
    title_en = Column(String(128), nullable=False)
    enabled = Column(Boolean, nullable=False)
    sort_order = Column(BIGINT, nullable=False)
    series = Column(JSON, nullable=False)
    __table_args__ = (Index("ix_obs_r10_curve_category", "category", "sort_order", "curve_group_key"),)


class ReceiptColumns:
    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    target = Column(String(7), nullable=False)
    producer_id = Column(String(64, collation="utf8mb4_bin"), nullable=False)
    event_id = Column(String(128, collation="utf8mb4_bin"), nullable=False)
    request_digest = Column(BINARY(32), nullable=False)
    outcome = Column(String(24), nullable=False)
    processed_at = Column(DATETIME(fsp=6), nullable=False, server_default=STAMP)
    result_record_id = Column(BIGINT(unsigned=True))
    mapping_id = Column(String(64))
    mapping_revision = Column(String(32))
    source_refs = Column(JSON)
    task_evidence = Column(JSON)
    contract_version = Column(String(32), nullable=False, server_default=text("'aiis.metric-ingest/v2'"))
    result_version = Column(String(8), nullable=False, server_default=text("'r10'"))
    result_detail = Column(JSON)


class Receipt(ReceiptColumns, Base):
    __tablename__ = "observation_ingest_receipts"
    __table_args__ = (
        UniqueConstraint("target", "producer_id", "event_id", name="uq_obs_receipt_event"),
        CheckConstraint("BINARY target IN ('latest','history')", name="ck_observation_receipt_target"),
    )


class EnergyReceipt(ReceiptColumns, Base):
    __tablename__ = "energy_ingest_receipts"
    __table_args__ = (
        UniqueConstraint("target", "producer_id", "event_id", name="uq_obs_receipt_event"),
        CheckConstraint("BINARY target = 'energy'", name="ck_energy_receipt_target"),
    )


class SampleColumns:
    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    equipment_id = Column(String(64, collation="utf8mb4_bin"), nullable=False)
    task_no = Column(String(50, collation="utf8mb4_bin"), nullable=False)
    observed_at = Column(DATETIME(fsp=6), nullable=False)
    quality = Column(String(16), nullable=False)
    source_sample_key = Column(BINARY(32), nullable=False)
    ingest_receipt_id = Column(BIGINT(unsigned=True), ForeignKey("observation_ingest_receipts.id", ondelete="RESTRICT"), nullable=False)
    local_values = Column(JSON, nullable=False)
    remark = Column(Text)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=STAMP)
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=STAMP, onupdate=func.now(6))


class LatestSnapshot(SampleColumns, Base):
    __tablename__ = "equipment_main"
    __table_args__ = (
        UniqueConstraint("equipment_id", "task_no", name="uq_obs_latest_task"),
        Index("ix_obs_latest_task_v2", "task_no", "id"),
    )


class HistorySample(SampleColumns, Base):
    __tablename__ = "monitor_main"
    review_mark = Column(String(16))
    __table_args__ = (
        Index("ix_obs_history_task_time_v2", "task_no", "observed_at", "id"),
        Index("ix_obs_history_equipment_time_v2", "equipment_id", "observed_at", "id"),
        CheckConstraint("review_mark IS NULL OR review_mark IN ('abnormal','reviewed')", name="ck_obs_review_mark_v2"),
    )


class EnergyMetric(Base):
    __tablename__ = "energy_metric_configs"
    meter_id = Column(String(64, collation="utf8mb4_bin"), primary_key=True)
    group_key = Column(String(64, collation="utf8mb4_bin"), primary_key=True)
    metric_key = Column(String(64, collation="utf8mb4_bin"), primary_key=True)
    slot_no = Column(TINYINT(unsigned=True), nullable=False)
    name_zh = Column(String(128), nullable=False)
    name_en = Column(String(128), nullable=False)
    value_type = Column(String(16), nullable=False)
    quantity_key = Column(String(64, collation="utf8mb4_bin"), nullable=False)
    measurement_mode = Column(String(16), nullable=False)
    unit = Column(String(24))
    decimals = Column(TINYINT(unsigned=True))
    enabled = Column(Boolean, nullable=False)
    list_visible = Column(Boolean, nullable=False, server_default=text("0"))
    list_order = Column(Integer)
    rules = Column(JSON, nullable=False)
    first_used_at = Column(DATETIME(fsp=6))
    __table_args__ = (
        UniqueConstraint("meter_id", "group_key", "slot_no", name="uq_energy_metric_slot"),
        CheckConstraint("slot_no BETWEEN 1 AND 100 AND value_type = 'number'", name="ck_energy_metric_slot_type"),
        CheckConstraint("measurement_mode IN ('cumulative','interval','instantaneous')", name="ck_energy_metric_mode"),
    )


class EnergySample(Base):
    __tablename__ = "energy_consumption_main"
    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    meter_id = Column(String(64, collation="utf8mb4_bin"), nullable=False)
    group_key = Column(String(64, collation="utf8mb4_bin"), nullable=False)
    observed_at = Column(DATETIME(fsp=6), nullable=False)
    quality = Column(String(16), nullable=False)
    interval_start_at = Column(DATETIME(fsp=6))
    interval_end_at = Column(DATETIME(fsp=6))
    ingest_receipt_id = Column(BIGINT(unsigned=True), ForeignKey("energy_ingest_receipts.id", name="fk_energy_sample_receipt", ondelete="RESTRICT"), nullable=False)
    local_values = Column(JSON, nullable=False)
    remark = Column(Text)
    review_mark = Column(String(16))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=STAMP)
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=STAMP, onupdate=func.now(6))
    __table_args__ = (
        Index("ix_energy_sample_meter_time", "meter_id", "group_key", "observed_at", "id"),
        CheckConstraint("review_mark IS NULL OR review_mark IN ('abnormal','reviewed')", name="ck_energy_review_mark"),
    )
