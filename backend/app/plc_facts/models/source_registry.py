"""来源登记模型；仅定义结构，不执行初始化或迁移。"""
from sqlalchemy import CheckConstraint, Column, ForeignKey, JSON, text
from sqlalchemy.dialects.mysql import BINARY, DATETIME, SMALLINT, TINYINT, VARBINARY, VARCHAR

from sqlalchemy.orm import declarative_base

from database import Base

# 历史迁移及前驱维护入口使用独立 metadata，不注册到当前运行模型。
LegacyBase = declarative_base()


class SourceInstance(LegacyBase):
    __tablename__ = 'acq_source_instances'
    instance_id = Column(VARBINARY(128), primary_key=True)
    source_type = Column(VARCHAR(8, charset='ascii', collation='ascii_bin'), nullable=False)
    __table_args__ = (CheckConstraint("source_type IN ('daa', 'external')", name='ck_acq_instance_type'), {'mysql_engine': 'InnoDB'})


class SourceBinding(LegacyBase):
    __tablename__ = 'acq_source_bindings'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    plc_id = Column(VARBINARY(128), primary_key=True)
    instance_id = Column(VARBINARY(128), ForeignKey('acq_source_instances.instance_id'), nullable=False, index=True)
    source_generation = Column(VARBINARY(128), nullable=False)
    registration_revision = Column(VARCHAR(36, charset='ascii', collation='ascii_bin'), nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'))


class SourceGeneration(LegacyBase):
    __tablename__ = 'acq_source_generations'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    plc_id = Column(VARBINARY(128), ForeignKey('acq_source_bindings.plc_id'), primary_key=True)
    source_generation = Column(VARBINARY(128), primary_key=True)
    instance_id = Column(VARBINARY(128), ForeignKey('acq_source_instances.instance_id'), nullable=False, index=True)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'))


class SourceWriteScope(LegacyBase):
    __tablename__ = 'acq_source_write_scopes'
    plc_id = Column(VARBINARY(128), ForeignKey('acq_source_bindings.plc_id'), primary_key=True)
    db_number = Column(SMALLINT(unsigned=True), primary_key=True)
    __table_args__ = (CheckConstraint('db_number BETWEEN 1 AND 65535', name='ck_acq_write_db'), {'mysql_engine': 'InnoDB'})


class SourceReadScope(LegacyBase):
    __tablename__ = 'acq_source_read_scopes'
    plc_id = Column(VARBINARY(128), primary_key=True)
    db_number = Column(SMALLINT(unsigned=True), primary_key=True)
    __table_args__ = (CheckConstraint('db_number BETWEEN 1 AND 65535', name='ck_acq_read_db'), {'mysql_engine': 'InnoDB'})


class SourceInitialization(LegacyBase):
    __tablename__ = 'acq_source_initialization'
    id = Column(TINYINT(unsigned=True), primary_key=True, autoincrement=False)
    input_hash = Column(BINARY(32), nullable=False)
    logical_hash = Column(BINARY(32), nullable=False)
    target_hash = Column(BINARY(32), nullable=False)
    initialized_at = Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'))
    __table_args__ = (CheckConstraint('id = 1', name='ck_acq_initialization_singleton'), {'mysql_engine': 'InnoDB'})



class PlcSourceRegistry(Base):
    """单台 PLC 的活跃上报身份与已退役代次。"""
    __tablename__ = 'plc_source_registry'

    plc_id = Column(VARBINARY(128), primary_key=True)
    instance_id = Column(VARBINARY(128), nullable=False)
    source_generation = Column(VARBINARY(128), nullable=False)
    source_type = Column(VARCHAR(8, charset='ascii', collation='ascii_bin'), nullable=False)
    retired_generations = Column(JSON, nullable=False, default=list)
    registration_revision = Column(VARCHAR(36, charset='ascii', collation='ascii_bin'), nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text('CURRENT_TIMESTAMP(6)'))
    __table_args__ = (
        CheckConstraint("source_type IN ('daa', 'external')", name='ck_plc_source_type'),
        {'mysql_engine': 'InnoDB'},
    )
