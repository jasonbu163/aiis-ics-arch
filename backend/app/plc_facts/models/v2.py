"""PLC 事实 v2 样本历史及逐点最新值；模型导入不触发数据库操作。"""
from sqlalchemy import BigInteger, CheckConstraint, Column, Index, JSON, String, UniqueConstraint
from sqlalchemy.dialects.mysql import BINARY, DATETIME, SMALLINT, VARBINARY

from database import Base


class SampleV2(Base):
    __tablename__ = 'plc_facts_history'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    instance_id = Column(VARBINARY(128), nullable=False)
    sample_id = Column(VARBINARY(128), nullable=False)
    plc_id = Column(VARBINARY(128), nullable=False)
    db_number = Column(SMALLINT(unsigned=True), nullable=False)
    group_id = Column(VARBINARY(128), nullable=True)
    config_revision = Column(VARBINARY(128), nullable=True)
    source_generation = Column(VARBINARY(128), nullable=False)
    source_seq = Column(BigInteger, nullable=False)
    points_json = Column(JSON, nullable=False)
    content_hash = Column(BINARY(32), nullable=False)
    sampled_at = Column(DATETIME(fsp=6), nullable=False)
    stored_at = Column(DATETIME(fsp=6), nullable=False)
    expires_at = Column(DATETIME(fsp=6), nullable=False)
    source_type = Column(String(8), nullable=True)
    __table_args__ = (
        UniqueConstraint('instance_id', 'sample_id', name='uq_pfv2_sample_identity'),
        UniqueConstraint('instance_id', 'plc_id', 'db_number', 'source_generation', 'source_seq', name='uq_pfv2_sample_sequence'),
        CheckConstraint('db_number BETWEEN 1 AND 65535 AND source_seq > 0', name='ck_pfv2_sample_bounds'),
        CheckConstraint("source_type IS NULL OR CAST(source_type AS BINARY) IN (X'646161', X'65787465726E616C')", name='ck_pfv2_source_type'),
        Index('ix_pfv2_sample_history', 'plc_id', 'db_number', 'sampled_at', 'id'),
        Index('ix_pfv2_sample_expiry', 'expires_at', 'id'),
    )


class LatestPointV2(Base):
    __tablename__ = 'plc_facts_latest'

    plc_id = Column(VARBINARY(128), primary_key=True)
    db_number = Column(SMALLINT(unsigned=True), primary_key=True)
    point_id = Column(VARBINARY(128), primary_key=True)
    point_name = Column(String(100), nullable=True)
    data_type = Column(String(16), nullable=True)
    value_json = Column(JSON(none_as_null=True), nullable=True)
    quality = Column(String(4), nullable=True)
    reason = Column(String(128), nullable=True)
    observed_at = Column(DATETIME(fsp=6), nullable=True)
    expires_at = Column(DATETIME(fsp=6), nullable=True)
    instance_id = Column(VARBINARY(128), nullable=False)
    source_generation = Column(VARBINARY(128), nullable=False)
    source_seq = Column(BigInteger, nullable=False)
    sample_id = Column(VARBINARY(128), nullable=True)
    __table_args__ = (
        CheckConstraint('db_number BETWEEN 1 AND 65535 AND source_seq > 0', name='ck_pfv2_latest_bounds'),
        Index('ix_pfv2_latest_expiry', 'expires_at', 'plc_id', 'db_number', 'point_id'),
    )
