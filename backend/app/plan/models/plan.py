"""计划、下发批次和人工动作的通用任务模型。"""
from sqlalchemy import CheckConstraint, Column, Computed, Index, JSON, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.mysql import BIGINT, BINARY, CHAR, DATETIME, INTEGER, SMALLINT, VARCHAR
from database import Base


def key(length):
    return VARCHAR(length, charset='ascii', collation='ascii_bin')


def uuid_type():
    return CHAR(36, charset='ascii', collation='ascii_bin')


def stamp():
    return Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'))


def updated():
    return Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'), onupdate=text('CURRENT_TIMESTAMP(6)'))


class Plan(Base):
    __tablename__ = 'plan_main'
    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    task_no = Column(key(50), nullable=False)
    target_key = Column(key(64), nullable=False)
    field_config_version = Column(INTEGER(unsigned=True), nullable=False)
    remark = Column(String(500))
    created_at = stamp()
    updated_at = updated()
    production_status = Column(key(16))
    priority = Column(SMALLINT(unsigned=True), nullable=False, server_default=text('5'))
    dispatch_status = Column(key(24), nullable=False, server_default=text("'pending'"))
    local_values = Column(JSON, nullable=False, server_default=text('(JSON_OBJECT())'))
    sync_values = Column(JSON, nullable=False, server_default=text('(JSON_OBJECT())'))
    __table_args__ = (
        UniqueConstraint('task_no', name='uq_task_no'),
        CheckConstraint("JSON_TYPE(local_values) = 'OBJECT' AND JSON_LENGTH(local_values) <= 100", name='ck_plan_local_values'),
        CheckConstraint("JSON_TYPE(sync_values) = 'OBJECT' AND JSON_LENGTH(sync_values) <= 100", name='ck_plan_sync_values'),
        CheckConstraint('priority BETWEEN 1 AND 10', name='ck_plan_priority'),
        CheckConstraint("production_status IS NULL OR production_status IN ('running','completed')", name='ck_plan_production_status'),
        CheckConstraint("dispatch_status IN ('pending','paused','claimed','exception','plc_accepted','cancelled','not_required')", name='ck_plan_dispatch_status'),
        Index('ix_created_page', 'created_at', 'id'),
        Index('ix_plan_target_state_page', 'target_key', 'dispatch_status', 'created_at', 'id'),
        Index('ix_plan_claim', 'target_key', 'dispatch_status', 'production_status', 'priority', 'created_at', 'id'),
        {'mysql_engine': 'InnoDB', 'mysql_row_format': 'DYNAMIC', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )


class DispatchAttempt(Base):
    __tablename__ = 'plan_dispatch_attempts'
    dispatch_id = Column(uuid_type(), primary_key=True)
    claim_request_id = Column(uuid_type(), nullable=False)
    task_no = Column(key(50), nullable=False)
    target_key = Column(key(64), nullable=False)
    attempt_no = Column(INTEGER(unsigned=True), nullable=False)
    field_config_version = Column(INTEGER(unsigned=True), nullable=False)
    producer_id = Column(key(64), nullable=False)
    parameters = Column(JSON, nullable=False)
    attempt_status = Column(key(24), nullable=False)
    active_target_key = Column(key(64), Computed("CASE WHEN attempt_status IN ('claimed','exception') THEN target_key ELSE NULL END", persisted=True))
    submission_phase = Column(key(24))
    request_seq = Column(BIGINT(unsigned=True))
    ack_seq = Column(BIGINT(unsigned=True))
    ack_observed_at = Column(DATETIME(fsp=6))
    failure_key = Column(key(64))
    failure_detail = Column(String(500))
    claimed_at = stamp()
    updated_at = updated()
    __table_args__ = (
        UniqueConstraint('claim_request_id', name='uq_plan_claim_request'),
        UniqueConstraint('task_no', 'attempt_no', name='uq_plan_attempt_number'),
        UniqueConstraint('active_target_key', name='uq_plan_active_target'),
        CheckConstraint("attempt_status IN ('claimed','exception','plc_accepted','returned')", name='ck_plan_attempt_status'),
        CheckConstraint("submission_phase IS NULL OR submission_phase IN ('not_submitted','possibly_submitted','acknowledged')", name='ck_plan_submission_phase'),
        {'mysql_engine': 'InnoDB', 'mysql_row_format': 'DYNAMIC', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )


class ActionEvent(Base):
    __tablename__ = 'plan_action_events'
    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    action_request_id = Column(uuid_type(), nullable=False)
    request_digest = Column(BINARY(32), nullable=False)
    task_no = Column(key(50), nullable=False)
    action_key = Column(key(24), nullable=False)
    actor_id = Column(BIGINT(unsigned=True), nullable=False)
    from_status = Column(key(24), nullable=False)
    to_status = Column(key(24), nullable=False)
    dispatch_id = Column(uuid_type())
    reason = Column(String(500))
    evidence = Column(Text)
    created_at = stamp()
    __table_args__ = (UniqueConstraint('action_request_id', name='uq_plan_action_request'), Index('ix_plan_action_task', 'task_no', 'id'),
        {'mysql_engine': 'InnoDB', 'mysql_row_format': 'DYNAMIC', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )
