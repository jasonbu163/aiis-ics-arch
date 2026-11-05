"""七表事实owner模型；键使用完整二进制，原文/Decimal保存在UTF-8 BLOB。"""
from sqlalchemy import Column, BigInteger, Integer, String, Boolean, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.mysql import VARBINARY, BINARY, LONGBLOB, DATETIME
from database import Base

class BatchReceipt(Base):
    __tablename__ = 'plc_facts_batches'
    instance_id = Column(VARBINARY(512), primary_key=True)
    batch_id = Column(VARBINARY(512), primary_key=True)
    request_digest = Column(BINARY(32), nullable=False)
    receipt_id = Column(String(36), nullable=False, unique=True)
    terminal = Column(String(12), nullable=False)
    http_status = Column(Integer, nullable=False)
    result = Column(LONGBLOB, nullable=False)
    members = Column(LONGBLOB, nullable=False)
    parent_batch_id = Column(VARBINARY(512), nullable=True)
    parent_depth = Column(Integer, nullable=False)
    rejection_token = Column(LONGBLOB, nullable=True)
    rejection_token_sha = Column(BINARY(32), nullable=True)
    recorded_at = Column(DATETIME(fsp=6), nullable=False)
    proof_expires_at = Column(DATETIME(fsp=6), nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False)
    updated_at = Column(DATETIME(fsp=6), nullable=False)
    __table_args__ = (
        CheckConstraint("terminal IN ('committed','rejected') AND parent_depth >= 0 AND parent_depth <= 8", name='ck_pf_batch_terminal'),
        Index('ix_pf_batch_expiry', 'proof_expires_at', 'receipt_id'),
    )

class SampleReceipt(Base):
    __tablename__ = 'plc_facts_sample_receipts'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    instance_id = Column(VARBINARY(512), nullable=False)
    sample_id = Column(VARBINARY(512), nullable=False)
    part = Column(Integer, nullable=False)
    parts = Column(Integer, nullable=False)
    cycle_id = Column(VARBINARY(512), nullable=False)
    plc_id = Column(VARBINARY(512), nullable=False)
    source_generation = Column(VARBINARY(512), nullable=False)
    source_seq = Column(BigInteger, nullable=False)
    db_number = Column(Integer, nullable=False)
    group_id = Column(VARBINARY(512), nullable=False)
    source_sha = Column(BINARY(32), nullable=False)
    content_digest = Column(BINARY(32), nullable=False)
    point_ids = Column(LONGBLOB, nullable=False)
    commit_serial = Column(BigInteger, nullable=False)
    ordinal = Column(Integer, nullable=False)
    observed_from = Column(DATETIME(fsp=6), nullable=False)
    observed_from_ns = Column(Integer, nullable=False)
    observed_to = Column(DATETIME(fsp=6), nullable=False)
    observed_to_ns = Column(Integer, nullable=False)
    raw_expires_at = Column(DATETIME(fsp=6), nullable=False)
    raw_expires_ns = Column(Integer, nullable=False)
    first_result = Column(LONGBLOB, nullable=False)
    proof_expires_at = Column(DATETIME(fsp=6), nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False)
    updated_at = Column(DATETIME(fsp=6), nullable=False)
    __table_args__ = (
        UniqueConstraint('instance_id','sample_id','part',name='uq_pf_sample_part'),
        UniqueConstraint('commit_serial','ordinal',name='uq_pf_feed_position'),
        CheckConstraint('source_seq > 0 AND commit_serial > 0 AND ordinal >= 1 AND ordinal <= 32 AND part >= 1 AND part <= parts AND parts <= 16 AND db_number >= 1 AND db_number <= 65535',name='ck_pf_sample_position'),
        CheckConstraint('observed_from_ns BETWEEN 0 AND 999 AND observed_to_ns BETWEEN 0 AND 999 AND raw_expires_ns BETWEEN 0 AND 999',name='ck_pf_sample_ns'),
        Index('ix_pf_feed_plc','plc_id','commit_serial','ordinal'),
        Index('ix_pf_cycle_receipts','instance_id','cycle_id'),
        Index('ix_pf_sample_expiry','proof_expires_at','commit_serial'),
    )
