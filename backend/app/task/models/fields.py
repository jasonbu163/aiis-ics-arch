"""通用任务字段版本与管理员修订状态；导入模型不触发数据库操作。"""
from sqlalchemy import Boolean, CheckConstraint, Column, String, UniqueConstraint, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, INTEGER, SMALLINT, TINYINT, VARCHAR
from database import Base


def ascii_key(length):
    return VARCHAR(length, charset='ascii', collation='ascii_bin')


class FieldConfigState(Base):
    __tablename__ = 'task_field_config_state'
    id = Column(TINYINT(unsigned=True), primary_key=True, autoincrement=False)
    active_version = Column(INTEGER(unsigned=True), nullable=False, server_default=text('1'))
    config_revision = Column(BIGINT(unsigned=True), nullable=False, server_default=text('1'))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'), onupdate=text('CURRENT_TIMESTAMP(6)'))
    __table_args__ = (CheckConstraint('id = 1', name='ck_task_config_singleton'),
        {'mysql_engine': 'InnoDB', 'mysql_row_format': 'DYNAMIC', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )


class FieldDefinition(Base):
    __tablename__ = 'task_field_definitions'
    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    config_version = Column(INTEGER(unsigned=True), nullable=False)
    scope = Column(ascii_key(24), nullable=False)
    slot_no = Column(TINYINT(unsigned=True), nullable=False)
    name = Column(ascii_key(64), nullable=False)
    value_type = Column(ascii_key(12), nullable=False)
    label_zh_cn = Column(String(128), nullable=False)
    label_en_us = Column(String(128), nullable=False)
    unit = Column(String(32))
    is_nullable = Column(Boolean, nullable=False, server_default=text('0'))
    enabled = Column(Boolean, nullable=False, server_default=text('0'))
    sync_enabled = Column(Boolean, nullable=False, server_default=text('0'))
    plan_editable = Column(Boolean, nullable=False, server_default=text('0'))
    performance_editable = Column(Boolean, nullable=False, server_default=text('0'))
    performance_owner = Column(ascii_key(16))
    plan_visible = Column(Boolean, nullable=False, server_default=text('0'))
    performance_visible = Column(Boolean, nullable=False, server_default=text('0'))
    plan_order = Column(SMALLINT(unsigned=True))
    performance_order = Column(SMALLINT(unsigned=True))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'), onupdate=text('CURRENT_TIMESTAMP(6)'))
    __table_args__ = (
        UniqueConstraint('config_version', 'scope', 'slot_no', name='uq_task_field_slot'),
        UniqueConstraint('config_version', 'scope', 'name', name='uq_task_field_name'),
        CheckConstraint("scope IN ('shared_sync','plan_local','performance_local') AND slot_no BETWEEN 1 AND 100", name='ck_task_field_scope_slot'),
        CheckConstraint("value_type IN ('string','number','boolean')", name='ck_task_field_type'),
        {'mysql_engine': 'InnoDB', 'mysql_row_format': 'DYNAMIC', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )
