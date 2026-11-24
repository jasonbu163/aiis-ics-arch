"""质量结果及本地字段配置的独立存储。"""
from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, Column, Index, Integer, JSON, String, UniqueConstraint
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR
from sqlalchemy.types import TypeDecorator

from common.integration.envelope import BUSINESS_TIMEZONE
from database import Base


class QualityDateTime(TypeDecorator):
    """MySQL 以东八区墙上时间保存，SQLite 以带偏移的 RFC 3339 保存。"""

    impl = String(32)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(DATETIME(fsp=6) if dialect.name == 'mysql' else self.impl)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        local = value.astimezone(BUSINESS_TIMEZONE)
        if dialect.name == 'mysql':
            return local.replace(tzinfo=None)
        return local.isoformat(timespec='microseconds')

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return (
            value.replace(tzinfo=BUSINESS_TIMEZONE)
            if dialect.name == 'mysql'
            else datetime.fromisoformat(value)
        )


def ascii_key(length):
    return String(length).with_variant(VARCHAR(length, charset='ascii', collation='ascii_bin'), 'mysql')


class QualityResult(Base):
    __tablename__ = 'quality_main'

    id = Column(BigInteger().with_variant(Integer(), 'sqlite'), primary_key=True)
    task_no = Column(ascii_key(50), nullable=False)
    target_key = Column(ascii_key(64))
    items = Column(JSON, nullable=False)
    created_at = Column(QualityDateTime(), nullable=False)
    updated_at = Column(QualityDateTime(), nullable=False)

    __table_args__ = (
        CheckConstraint("lower(json_type(items)) = 'object'", name='ck_quality_main_items'),
        UniqueConstraint('task_no', name='uq_quality_main_task_no'),
        Index('ix_quality_main_created_id', 'created_at', 'id'),
        Index('ix_quality_main_target_created_id', 'target_key', 'created_at', 'id'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )


class QualityFieldConfig(Base):
    __tablename__ = 'quality_field_config'

    id = Column(Integer, primary_key=True, autoincrement=False)
    definitions = Column(JSON, nullable=False)
    revision = Column(BigInteger, nullable=False)
    created_at = Column(QualityDateTime(), nullable=False)
    updated_at = Column(QualityDateTime(), nullable=False)

    __table_args__ = (
        CheckConstraint("lower(json_type(definitions)) = 'array'", name='ck_quality_config_definitions'),
        CheckConstraint('id = 1', name='ck_quality_config_singleton'),
        CheckConstraint('revision >= 1', name='ck_quality_config_revision'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )
