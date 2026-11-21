"""采集消费流、运行栅栏和投递元数据；原始点值仍由事实表保存。"""
from sqlalchemy import BigInteger, Column, Index, JSON, String, UniqueConstraint
from sqlalchemy.dialects.mysql import BINARY, DATETIME, SMALLINT, VARBINARY

from database import Base


class ConsumptionStream(Base):
    __tablename__ = 'acq_consumption_streams'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    plc_id = Column(VARBINARY(128), primary_key=True)
    db_number = Column(SMALLINT(unsigned=True), primary_key=True)
    last_seq = Column(BigInteger, nullable=False)
    floor_seq = Column(BigInteger, nullable=False)


class ConsumptionEvent(Base):
    __tablename__ = 'acq_consumption_events'
    __table_args__ = (
        UniqueConstraint('history_id', name='uq_acq_consumption_history'),
        Index('ix_acq_consumption_event_generation', 'plc_id', 'source_generation'),
        {'mysql_engine': 'InnoDB'},
    )
    plc_id = Column(VARBINARY(128), primary_key=True)
    db_number = Column(SMALLINT(unsigned=True), primary_key=True)
    event_seq = Column(BigInteger, primary_key=True)
    history_id = Column(BigInteger, nullable=False)
    instance_id = Column(VARBINARY(128), nullable=False)
    sample_id = Column(VARBINARY(128), nullable=False)
    source_generation = Column(VARBINARY(128), nullable=False)
    expires_at = Column(DATETIME(fsp=6), nullable=False)


class AcquisitionConsumer(Base):
    __tablename__ = 'acq_consumers'
    __table_args__ = (
        UniqueConstraint('target_plc', 'target_db', 'target_generation',
                         name='uq_acq_consumer_target_stream'),
        {'mysql_engine': 'InnoDB'},
    )
    consumer_id = Column(String(36), primary_key=True)
    plc_id = Column(VARBINARY(128), nullable=False)
    db_number = Column(SMALLINT(unsigned=True), nullable=False)
    start_mode = Column(String(8), nullable=False)
    start_at = Column(DATETIME(fsp=6), nullable=False)
    start_seq = Column(BigInteger, nullable=False)
    last_confirmed_seq = Column(BigInteger, nullable=False)
    excluded_count = Column(BigInteger, nullable=False)
    excluded_first_seq = Column(BigInteger)
    excluded_last_seq = Column(BigInteger)
    target_plc = Column(VARBINARY(128), nullable=False)
    target_db = Column(SMALLINT(unsigned=True), nullable=False)
    target_instance = Column(VARBINARY(128), nullable=False)
    target_generation = Column(VARBINARY(128), nullable=False)
    desired_state = Column(String(8), nullable=False)
    lease_id = Column(String(36))
    lease_generation = Column(BigInteger, nullable=False)
    worker_id = Column(VARBINARY(128))
    lease_expires_at = Column(DATETIME(fsp=6))


class AcquisitionDelivery(Base):
    __tablename__ = 'acq_consumer_deliveries'
    __table_args__ = (
        UniqueConstraint('consumer_id', 'event_seq', name='uq_acq_delivery_event'),
        Index('ix_acq_delivery_pending', 'consumer_id', 'confirmed_at', 'event_seq'),
        {'mysql_engine': 'InnoDB'},
    )
    consumer_id = Column(String(36), primary_key=True)
    delivery_id = Column(String(36), primary_key=True)
    event_seq = Column(BigInteger, nullable=False)
    config_version = Column(String(128), nullable=False)
    config_hash = Column(BINARY(32), nullable=False)
    serializer_version = Column(String(128), nullable=False)
    body_hash = Column(BINARY(32), nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False)
    confirmed_at = Column(DATETIME(fsp=6))


class AcquisitionOperation(Base):
    __tablename__ = 'acq_consumer_operations'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    consumer_id = Column(String(36), primary_key=True)
    operation_id = Column(String(36), primary_key=True)
    fingerprint = Column(BINARY(32), nullable=False)
    result = Column(JSON, nullable=False)


class ConsumptionActivation(Base):
    __tablename__ = 'acq_consumption_activation'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(SMALLINT(unsigned=True), primary_key=True, autoincrement=False)
    cutoff_at = Column(DATETIME(fsp=6), nullable=False)
    ready = Column(SMALLINT(unsigned=True), nullable=False)
