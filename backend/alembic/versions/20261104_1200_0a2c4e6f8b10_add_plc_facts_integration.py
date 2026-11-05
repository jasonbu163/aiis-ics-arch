"""新增七张有界PLC事实表；显式运行另需目标批准，升级无数据副作用。"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, BigInteger, Integer, String, Boolean, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.mysql import VARBINARY, BINARY, LONGBLOB, DATETIME
revision = '0a2c4e6f8b10'
down_revision = 'f6a8c0e2b4d6'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('plc_facts_stream_state',
        Column('id', Integer, primary_key=True, autoincrement=False),
        Column('storage_epoch', String(36), nullable=False),
        Column('storage_profile', String(32), nullable=False),
        Column('adoption_id', String(36), nullable=False),
        Column('schema_profile', String(32), nullable=False),
        Column('verified_schema_revision', String(16), nullable=False),
        Column('schema_fingerprint', BINARY(32), nullable=False),
        Column('adoption_evidence', LONGBLOB, nullable=False),
        Column('retention_months', Integer, nullable=False),
        Column('high_serial', BigInteger, nullable=False),
        Column('proof_floor_serial', BigInteger, nullable=False),
        Column('proof_floor_ordinal', Integer, nullable=False),
        Column('last_db_time', DATETIME(fsp=6), nullable=False),
        Column('value_bytes', BigInteger, nullable=False),
        Column('proof_rows', BigInteger, nullable=False),
        Column('max_value_bytes', BigInteger, nullable=False),
        Column('max_proof_rows', BigInteger, nullable=False),
        Column('cleanup_last_success', DATETIME(fsp=6), nullable=True),
        Column('cleanup_failures', Integer, nullable=False),
        Column('cleanup_oldest_expired', DATETIME(fsp=6), nullable=True),
        Column('created_at', DATETIME(fsp=6), nullable=False),
        Column('updated_at', DATETIME(fsp=6), nullable=False),
        CheckConstraint('id = 1', name='ck_pf_state_singleton'),
        CheckConstraint('high_serial >= 0 AND proof_floor_serial >= 0 AND proof_floor_ordinal >= 0 AND proof_floor_ordinal <= 32', name='ck_pf_state_position'),
        CheckConstraint('value_bytes >= 0 AND proof_rows >= 0 AND max_value_bytes >= 1048576 AND max_value_bytes <= 1073741824 AND max_proof_rows >= 100 AND max_proof_rows <= 1000000', name='ck_pf_state_capacity'),
        CheckConstraint('retention_months >= 1 AND retention_months <= 3 AND cleanup_failures >= 0', name='ck_pf_state_retention'),
    )
    op.create_table('plc_facts_source_bindings',
        Column('plc_id', VARBINARY(512), primary_key=True),
        Column('instance_id', VARBINARY(512), nullable=False),
        Column('source_generation', VARBINARY(512), nullable=False),
        Column('source_epoch', BigInteger, nullable=False),
        Column('binding_revision', BigInteger, nullable=False),
        Column('config_revision', VARBINARY(512), nullable=False),
        Column('context_sha', BINARY(32), nullable=False),
        Column('definition_set_digest', BINARY(32), nullable=False),
        Column('seq_from', BigInteger, nullable=False),
        Column('seq_through', BigInteger, nullable=False),
        Column('raw_only_windows', LONGBLOB, nullable=False),
        Column('created_at', DATETIME(fsp=6), nullable=False),
        Column('updated_at', DATETIME(fsp=6), nullable=False),
        CheckConstraint('source_epoch > 0 AND binding_revision > 0 AND seq_from > 0 AND seq_through >= seq_from', name='ck_pf_binding_sequence'),
    )
    op.create_table('plc_facts_batches',
        Column('instance_id', VARBINARY(512), primary_key=True),
        Column('batch_id', VARBINARY(512), primary_key=True),
        Column('request_digest', BINARY(32), nullable=False),
        Column('receipt_id', String(36), nullable=False, unique=True),
        Column('terminal', String(12), nullable=False),
        Column('http_status', Integer, nullable=False),
        Column('result', LONGBLOB, nullable=False),
        Column('members', LONGBLOB, nullable=False),
        Column('parent_batch_id', VARBINARY(512), nullable=True),
        Column('parent_depth', Integer, nullable=False),
        Column('rejection_token', LONGBLOB, nullable=True),
        Column('rejection_token_sha', BINARY(32), nullable=True),
        Column('recorded_at', DATETIME(fsp=6), nullable=False),
        Column('proof_expires_at', DATETIME(fsp=6), nullable=False),
        Column('created_at', DATETIME(fsp=6), nullable=False),
        Column('updated_at', DATETIME(fsp=6), nullable=False),
        CheckConstraint("terminal IN ('committed','rejected') AND parent_depth >= 0 AND parent_depth <= 8", name='ck_pf_batch_terminal'),
    )
    op.create_index('ix_pf_batch_expiry', 'plc_facts_batches', ['proof_expires_at', 'receipt_id'])
    op.create_table('plc_facts_sample_receipts',
        Column('id', BigInteger, primary_key=True, autoincrement=True),
        Column('instance_id', VARBINARY(512), nullable=False),
        Column('sample_id', VARBINARY(512), nullable=False),
        Column('part', Integer, nullable=False),
        Column('parts', Integer, nullable=False),
        Column('cycle_id', VARBINARY(512), nullable=False),
        Column('plc_id', VARBINARY(512), nullable=False),
        Column('source_generation', VARBINARY(512), nullable=False),
        Column('source_seq', BigInteger, nullable=False),
        Column('db_number', Integer, nullable=False),
        Column('group_id', VARBINARY(512), nullable=False),
        Column('source_sha', BINARY(32), nullable=False),
        Column('content_digest', BINARY(32), nullable=False),
        Column('point_ids', LONGBLOB, nullable=False),
        Column('commit_serial', BigInteger, nullable=False),
        Column('ordinal', Integer, nullable=False),
        Column('observed_from', DATETIME(fsp=6), nullable=False),
        Column('observed_from_ns', Integer, nullable=False),
        Column('observed_to', DATETIME(fsp=6), nullable=False),
        Column('observed_to_ns', Integer, nullable=False),
        Column('raw_expires_at', DATETIME(fsp=6), nullable=False),
        Column('raw_expires_ns', Integer, nullable=False),
        Column('first_result', LONGBLOB, nullable=False),
        Column('proof_expires_at', DATETIME(fsp=6), nullable=False),
        Column('created_at', DATETIME(fsp=6), nullable=False),
        Column('updated_at', DATETIME(fsp=6), nullable=False),
        UniqueConstraint('instance_id','sample_id','part',name='uq_pf_sample_part'),
        UniqueConstraint('commit_serial','ordinal',name='uq_pf_feed_position'),
        CheckConstraint('source_seq > 0 AND commit_serial > 0 AND ordinal >= 1 AND ordinal <= 32 AND part >= 1 AND part <= parts AND parts <= 16 AND db_number >= 1 AND db_number <= 65535',name='ck_pf_sample_position'),
        CheckConstraint('observed_from_ns BETWEEN 0 AND 999 AND observed_to_ns BETWEEN 0 AND 999 AND raw_expires_ns BETWEEN 0 AND 999',name='ck_pf_sample_ns'),
    )
    op.create_index('ix_pf_feed_plc', 'plc_facts_sample_receipts', ['plc_id', 'commit_serial', 'ordinal'])
    op.create_index('ix_pf_cycle_receipts', 'plc_facts_sample_receipts', ['instance_id', 'cycle_id'])
    op.create_index('ix_pf_sample_expiry', 'plc_facts_sample_receipts', ['proof_expires_at', 'commit_serial'])
    op.create_table('plc_facts_raw_samples',
        Column('id', BigInteger, primary_key=True, autoincrement=True),
        Column('instance_id', VARBINARY(512), nullable=False),
        Column('sample_id', VARBINARY(512), nullable=False),
        Column('cycle_id', VARBINARY(512), nullable=False),
        Column('plc_id', VARBINARY(512), nullable=False),
        Column('source_generation', VARBINARY(512), nullable=False),
        Column('source_seq', BigInteger, nullable=False),
        Column('db_number', Integer, nullable=False),
        Column('source_sha', BINARY(32), nullable=False),
        Column('payload_utf8', LONGBLOB, nullable=False),
        Column('projections', LONGBLOB, nullable=False),
        Column('observed_from', DATETIME(fsp=6), nullable=False),
        Column('observed_from_ns', Integer, nullable=False),
        Column('observed_to', DATETIME(fsp=6), nullable=False),
        Column('observed_to_ns', Integer, nullable=False),
        Column('expires_at', DATETIME(fsp=6), nullable=False),
        Column('expires_ns', Integer, nullable=False),
        Column('created_at', DATETIME(fsp=6), nullable=False),
        Column('updated_at', DATETIME(fsp=6), nullable=False),
        UniqueConstraint('instance_id','sample_id',name='uq_pf_raw_source'),
        CheckConstraint('source_seq > 0 AND db_number BETWEEN 1 AND 65535 AND expires_ns BETWEEN 0 AND 999 AND observed_from_ns BETWEEN 0 AND 999 AND observed_to_ns BETWEEN 0 AND 999',name='ck_pf_raw_bounds'),
    )
    op.create_index('ix_pf_raw_expiry', 'plc_facts_raw_samples', ['expires_at', 'id'])
    op.create_index('ix_pf_raw_plc_db', 'plc_facts_raw_samples', ['plc_id', 'db_number', 'id'])
    op.create_table('plc_facts_cycles',
        Column('instance_id', VARBINARY(512), primary_key=True),
        Column('cycle_id', VARBINARY(512), primary_key=True),
        Column('plc_id', VARBINARY(512), nullable=False),
        Column('source_generation', VARBINARY(512), nullable=False),
        Column('source_seq', BigInteger, nullable=False),
        Column('cycle_digest', BINARY(32), nullable=False),
        Column('manifest_sha', BINARY(32), nullable=False),
        Column('context_sha', BINARY(32), nullable=False),
        Column('manifest_utf8', LONGBLOB, nullable=True),
        Column('context_utf8', LONGBLOB, nullable=True),
        Column('transport_manifest', LONGBLOB, nullable=True),
        Column('expected_parts', LONGBLOB, nullable=False),
        Column('received_parts', LONGBLOB, nullable=False),
        Column('complete', Boolean, nullable=False),
        Column('quality_good', Boolean, nullable=False),
        Column('expires_at', DATETIME(fsp=6), nullable=False),
        Column('expires_ns', Integer, nullable=False),
        Column('proof_expires_at', DATETIME(fsp=6), nullable=False),
        Column('created_at', DATETIME(fsp=6), nullable=False),
        Column('updated_at', DATETIME(fsp=6), nullable=False),
        UniqueConstraint('plc_id','source_generation','source_seq',name='uq_pf_cycle_sequence'),
        CheckConstraint('source_seq > 0 AND expires_ns BETWEEN 0 AND 999',name='ck_pf_cycle_bounds'),
    )
    op.create_index('ix_pf_cycle_expiry', 'plc_facts_cycles', ['expires_at', 'proof_expires_at'])
    op.create_table('plc_facts_latest_points',
        Column('plc_id', VARBINARY(512), primary_key=True),
        Column('point_id', VARBINARY(512), primary_key=True),
        Column('source_epoch', BigInteger, nullable=False),
        Column('definition_digest', BINARY(32), nullable=False),
        Column('instance_id', VARBINARY(512), nullable=False),
        Column('source_generation', VARBINARY(512), nullable=False),
        Column('source_seq', BigInteger, nullable=False),
        Column('config_revision', VARBINARY(512), nullable=False),
        Column('sample_id', VARBINARY(512), nullable=False),
        Column('part', Integer, nullable=False),
        Column('cycle_id', VARBINARY(512), nullable=False),
        Column('db_number', Integer, nullable=False),
        Column('group_id', VARBINARY(512), nullable=False),
        Column('point_fact', LONGBLOB, nullable=False),
        Column('observed_at', DATETIME(fsp=6), nullable=False),
        Column('observed_ns', Integer, nullable=False),
        Column('expires_at', DATETIME(fsp=6), nullable=False),
        Column('expires_ns', Integer, nullable=False),
        Column('created_at', DATETIME(fsp=6), nullable=False),
        Column('updated_at', DATETIME(fsp=6), nullable=False),
        CheckConstraint('source_epoch > 0 AND source_seq > 0 AND part BETWEEN 1 AND 16 AND db_number BETWEEN 1 AND 65535 AND observed_ns BETWEEN 0 AND 999 AND expires_ns BETWEEN 0 AND 999',name='ck_pf_latest_bounds'),
    )
    op.create_index('ix_pf_latest_plc_db', 'plc_facts_latest_points', ['plc_id', 'db_number', 'point_id'])
    op.create_index('ix_pf_latest_expiry', 'plc_facts_latest_points', ['expires_at', 'point_id'])

def downgrade():
    bind = op.get_bind()
    if bind.execute(sa.text("SELECT 1 FROM plc_facts_stream_state LIMIT 1")).first() is not None:
        raise RuntimeError("PLC facts downgrade requires all seven tables empty and unadopted")
    if bind.execute(sa.text("SELECT 1 FROM plc_facts_source_bindings LIMIT 1")).first() is not None:
        raise RuntimeError("PLC facts downgrade requires all seven tables empty and unadopted")
    if bind.execute(sa.text("SELECT 1 FROM plc_facts_batches LIMIT 1")).first() is not None:
        raise RuntimeError("PLC facts downgrade requires all seven tables empty and unadopted")
    if bind.execute(sa.text("SELECT 1 FROM plc_facts_sample_receipts LIMIT 1")).first() is not None:
        raise RuntimeError("PLC facts downgrade requires all seven tables empty and unadopted")
    if bind.execute(sa.text("SELECT 1 FROM plc_facts_raw_samples LIMIT 1")).first() is not None:
        raise RuntimeError("PLC facts downgrade requires all seven tables empty and unadopted")
    if bind.execute(sa.text("SELECT 1 FROM plc_facts_cycles LIMIT 1")).first() is not None:
        raise RuntimeError("PLC facts downgrade requires all seven tables empty and unadopted")
    if bind.execute(sa.text("SELECT 1 FROM plc_facts_latest_points LIMIT 1")).first() is not None:
        raise RuntimeError("PLC facts downgrade requires all seven tables empty and unadopted")
    op.drop_table('plc_facts_latest_points')
    op.drop_table('plc_facts_cycles')
    op.drop_table('plc_facts_raw_samples')
    op.drop_table('plc_facts_sample_receipts')
    op.drop_table('plc_facts_batches')
    op.drop_table('plc_facts_source_bindings')
    op.drop_table('plc_facts_stream_state')
