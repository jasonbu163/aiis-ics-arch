"""按任务号保存自动快照和人工值的实绩模型。"""
from sqlalchemy import CheckConstraint, Column, Index, JSON, String, UniqueConstraint, text
from sqlalchemy.dialects.mysql import BIGINT, BINARY, DATETIME, INTEGER, VARCHAR
from database import Base


def key(length):
    return VARCHAR(length, charset='ascii', collation='ascii_bin')


class Performance(Base):
    __tablename__ = 'performance_main'
    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    task_no = Column(key(50), nullable=False)
    target_key = Column(key(64), nullable=False)
    field_config_version = Column(INTEGER(unsigned=True), nullable=False)
    remark = Column(String(500))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'), onupdate=text('CURRENT_TIMESTAMP(6)'))
    production_status = Column(key(16), nullable=False)
    started_at = Column(DATETIME(fsp=6))
    completed_at = Column(DATETIME(fsp=6))
    last_observed_at = Column(DATETIME(fsp=6))
    observation_seq = Column(BIGINT(unsigned=True), nullable=False)
    observation_digest = Column(BINARY(32), nullable=False)
    record_source = Column(key(32), nullable=False)
    local_values = Column(JSON, nullable=False, server_default=text('(JSON_OBJECT())'))
    sync_values = Column(JSON, nullable=False, server_default=text('(JSON_OBJECT())'))
    __table_args__ = (
        UniqueConstraint('task_no', name='uq_task_no'),
        CheckConstraint("JSON_TYPE(local_values) = 'OBJECT' AND JSON_LENGTH(local_values) <= 100", name='ck_performance_local_values'),
        CheckConstraint("JSON_TYPE(sync_values) = 'OBJECT' AND JSON_LENGTH(sync_values) <= 100", name='ck_performance_sync_values'),
        CheckConstraint("production_status IN ('running','completed')", name='ck_performance_status'),
        CheckConstraint("record_source IN ('sma','ca_ff')", name='ck_performance_source'),
        Index('ix_created_page', 'created_at', 'id'),
        Index('ix_perf_target_state_page', 'target_key', 'production_status', 'created_at', 'id'),
        {'mysql_engine': 'InnoDB', 'mysql_row_format': 'DYNAMIC', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )
