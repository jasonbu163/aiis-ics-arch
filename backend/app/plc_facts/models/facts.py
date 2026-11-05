"""七表事实owner模型；键使用完整二进制，原文/Decimal保存在UTF-8 BLOB。"""
from sqlalchemy import Column, BigInteger, Integer, String, Boolean, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.mysql import VARBINARY, BINARY, LONGBLOB, DATETIME
from database import Base

class RawSample(Base):
    __tablename__ = 'plc_facts_raw_samples'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    instance_id = Column(VARBINARY(512), nullable=False)
    sample_id = Column(VARBINARY(512), nullable=False)
    cycle_id = Column(VARBINARY(512), nullable=False)
    plc_id = Column(VARBINARY(512), nullable=False)
    source_generation = Column(VARBINARY(512), nullable=False)
    source_seq = Column(BigInteger, nullable=False)
    db_number = Column(Integer, nullable=False)
    source_sha = Column(BINARY(32), nullable=False)
    payload_utf8 = Column(LONGBLOB, nullable=False)
    projections = Column(LONGBLOB, nullable=False)
    observed_from = Column(DATETIME(fsp=6), nullable=False)
    observed_from_ns = Column(Integer, nullable=False)
    observed_to = Column(DATETIME(fsp=6), nullable=False)
    observed_to_ns = Column(Integer, nullable=False)
    expires_at = Column(DATETIME(fsp=6), nullable=False)
    expires_ns = Column(Integer, nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False)
    updated_at = Column(DATETIME(fsp=6), nullable=False)
    __table_args__ = (
        UniqueConstraint('instance_id','sample_id',name='uq_pf_raw_source'),
        CheckConstraint('source_seq > 0 AND db_number BETWEEN 1 AND 65535 AND expires_ns BETWEEN 0 AND 999 AND observed_from_ns BETWEEN 0 AND 999 AND observed_to_ns BETWEEN 0 AND 999',name='ck_pf_raw_bounds'),
        Index('ix_pf_raw_expiry','expires_at','id'),
        Index('ix_pf_raw_plc_db','plc_id','db_number','id'),
    )

class Cycle(Base):
    __tablename__ = 'plc_facts_cycles'
    instance_id = Column(VARBINARY(512), primary_key=True)
    cycle_id = Column(VARBINARY(512), primary_key=True)
    plc_id = Column(VARBINARY(512), nullable=False)
    source_generation = Column(VARBINARY(512), nullable=False)
    source_seq = Column(BigInteger, nullable=False)
    cycle_digest = Column(BINARY(32), nullable=False)
    manifest_sha = Column(BINARY(32), nullable=False)
    context_sha = Column(BINARY(32), nullable=False)
    manifest_utf8 = Column(LONGBLOB, nullable=True)
    context_utf8 = Column(LONGBLOB, nullable=True)
    transport_manifest = Column(LONGBLOB, nullable=True)
    expected_parts = Column(LONGBLOB, nullable=False)
    received_parts = Column(LONGBLOB, nullable=False)
    complete = Column(Boolean, nullable=False)
    quality_good = Column(Boolean, nullable=False)
    expires_at = Column(DATETIME(fsp=6), nullable=False)
    expires_ns = Column(Integer, nullable=False)
    proof_expires_at = Column(DATETIME(fsp=6), nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False)
    updated_at = Column(DATETIME(fsp=6), nullable=False)
    __table_args__ = (
        UniqueConstraint('plc_id','source_generation','source_seq',name='uq_pf_cycle_sequence'),
        CheckConstraint('source_seq > 0 AND expires_ns BETWEEN 0 AND 999',name='ck_pf_cycle_bounds'),
        Index('ix_pf_cycle_expiry','expires_at','proof_expires_at'),
    )

class LatestPoint(Base):
    __tablename__ = 'plc_facts_latest_points'
    plc_id = Column(VARBINARY(512), primary_key=True)
    point_id = Column(VARBINARY(512), primary_key=True)
    source_epoch = Column(BigInteger, nullable=False)
    definition_digest = Column(BINARY(32), nullable=False)
    instance_id = Column(VARBINARY(512), nullable=False)
    source_generation = Column(VARBINARY(512), nullable=False)
    source_seq = Column(BigInteger, nullable=False)
    config_revision = Column(VARBINARY(512), nullable=False)
    sample_id = Column(VARBINARY(512), nullable=False)
    part = Column(Integer, nullable=False)
    cycle_id = Column(VARBINARY(512), nullable=False)
    db_number = Column(Integer, nullable=False)
    group_id = Column(VARBINARY(512), nullable=False)
    point_fact = Column(LONGBLOB, nullable=False)
    observed_at = Column(DATETIME(fsp=6), nullable=False)
    observed_ns = Column(Integer, nullable=False)
    expires_at = Column(DATETIME(fsp=6), nullable=False)
    expires_ns = Column(Integer, nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False)
    updated_at = Column(DATETIME(fsp=6), nullable=False)
    __table_args__ = (
        CheckConstraint('source_epoch > 0 AND source_seq > 0 AND part BETWEEN 1 AND 16 AND db_number BETWEEN 1 AND 65535 AND observed_ns BETWEEN 0 AND 999 AND expires_ns BETWEEN 0 AND 999',name='ck_pf_latest_bounds'),
        Index('ix_pf_latest_plc_db','plc_id','db_number','point_id'),
        Index('ix_pf_latest_expiry','expires_at','point_id'),
    )
