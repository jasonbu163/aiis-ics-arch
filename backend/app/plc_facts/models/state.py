"""七表事实owner模型；键使用完整二进制，原文/Decimal保存在UTF-8 BLOB。"""
from sqlalchemy import Column, BigInteger, Integer, String, Boolean, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.mysql import VARBINARY, BINARY, LONGBLOB, DATETIME
from database import Base

class StreamState(Base):
    __tablename__ = 'plc_facts_stream_state'
    id = Column(Integer, primary_key=True, autoincrement=False)
    storage_epoch = Column(String(36), nullable=False)
    storage_profile = Column(String(32), nullable=False)
    adoption_id = Column(String(36), nullable=False)
    schema_profile = Column(String(32), nullable=False)
    verified_schema_revision = Column(String(16), nullable=False)
    schema_fingerprint = Column(BINARY(32), nullable=False)
    adoption_evidence = Column(LONGBLOB, nullable=False)
    retention_months = Column(Integer, nullable=False)
    high_serial = Column(BigInteger, nullable=False)
    proof_floor_serial = Column(BigInteger, nullable=False)
    proof_floor_ordinal = Column(Integer, nullable=False)
    last_db_time = Column(DATETIME(fsp=6), nullable=False)
    value_bytes = Column(BigInteger, nullable=False)
    proof_rows = Column(BigInteger, nullable=False)
    max_value_bytes = Column(BigInteger, nullable=False)
    max_proof_rows = Column(BigInteger, nullable=False)
    cleanup_last_success = Column(DATETIME(fsp=6), nullable=True)
    cleanup_failures = Column(Integer, nullable=False)
    cleanup_oldest_expired = Column(DATETIME(fsp=6), nullable=True)
    created_at = Column(DATETIME(fsp=6), nullable=False)
    updated_at = Column(DATETIME(fsp=6), nullable=False)
    __table_args__ = (
        CheckConstraint('id = 1', name='ck_pf_state_singleton'),
        CheckConstraint('high_serial >= 0 AND proof_floor_serial >= 0 AND proof_floor_ordinal >= 0 AND proof_floor_ordinal <= 32', name='ck_pf_state_position'),
        CheckConstraint('value_bytes >= 0 AND proof_rows >= 0 AND max_value_bytes >= 1048576 AND max_value_bytes <= 1073741824 AND max_proof_rows >= 100 AND max_proof_rows <= 1000000', name='ck_pf_state_capacity'),
        CheckConstraint('retention_months >= 1 AND retention_months <= 3 AND cleanup_failures >= 0', name='ck_pf_state_retention'),
    )

class SourceBinding(Base):
    __tablename__ = 'plc_facts_source_bindings'
    plc_id = Column(VARBINARY(512), primary_key=True)
    instance_id = Column(VARBINARY(512), nullable=False)
    source_generation = Column(VARBINARY(512), nullable=False)
    source_epoch = Column(BigInteger, nullable=False)
    binding_revision = Column(BigInteger, nullable=False)
    config_revision = Column(VARBINARY(512), nullable=False)
    context_sha = Column(BINARY(32), nullable=False)
    definition_set_digest = Column(BINARY(32), nullable=False)
    seq_from = Column(BigInteger, nullable=False)
    seq_through = Column(BigInteger, nullable=False)
    raw_only_windows = Column(LONGBLOB, nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False)
    updated_at = Column(DATETIME(fsp=6), nullable=False)
    __table_args__ = (
        CheckConstraint('source_epoch > 0 AND binding_revision > 0 AND seq_from > 0 AND seq_through >= seq_from', name='ck_pf_binding_sequence'),
    )
