"""新增 v2 原始样本及逐点最新值；仅在两表均空时允许降级。"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '2c4e6a8b0d12'
down_revision = '1b3d5f7a9c20'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'plc_facts_samples_v2',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('instance_id', mysql.VARBINARY(128), nullable=False),
        sa.Column('sample_id', mysql.VARBINARY(128), nullable=False),
        sa.Column('plc_id', mysql.VARBINARY(128), nullable=False),
        sa.Column('db_number', mysql.SMALLINT(unsigned=True), nullable=False),
        sa.Column('group_id', mysql.VARBINARY(128), nullable=False),
        sa.Column('config_revision', mysql.VARBINARY(128), nullable=False),
        sa.Column('source_generation', mysql.VARBINARY(128), nullable=False),
        sa.Column('source_seq', sa.BigInteger(), nullable=False),
        sa.Column('points_json', sa.JSON(), nullable=False),
        sa.Column('content_hash', mysql.BINARY(32), nullable=False),
        sa.Column('sampled_at', mysql.DATETIME(fsp=6), nullable=False),
        sa.Column('stored_at', mysql.DATETIME(fsp=6), nullable=False),
        sa.Column('expires_at', mysql.DATETIME(fsp=6), nullable=False),
        sa.UniqueConstraint('instance_id', 'sample_id', name='uq_pfv2_sample_identity'),
        sa.UniqueConstraint('instance_id', 'plc_id', 'db_number', 'source_generation', 'source_seq', name='uq_pfv2_sample_sequence'),
        sa.CheckConstraint('db_number BETWEEN 1 AND 65535 AND source_seq > 0', name='ck_pfv2_sample_bounds'),
    )
    op.create_index('ix_pfv2_sample_history', 'plc_facts_samples_v2', ['plc_id', 'db_number', 'sampled_at', 'id'])
    op.create_index('ix_pfv2_sample_expiry', 'plc_facts_samples_v2', ['expires_at', 'id'])
    op.create_table(
        'plc_facts_latest_points_v2',
        sa.Column('plc_id', mysql.VARBINARY(128), primary_key=True),
        sa.Column('db_number', mysql.SMALLINT(unsigned=True), primary_key=True),
        sa.Column('point_id', mysql.VARBINARY(128), primary_key=True),
        sa.Column('point_name', sa.String(100), nullable=True),
        sa.Column('data_type', sa.String(16), nullable=True),
        sa.Column('value_json', sa.JSON(none_as_null=True), nullable=True),
        sa.Column('quality', sa.String(4), nullable=True),
        sa.Column('reason', sa.String(128), nullable=True),
        sa.Column('observed_at', mysql.DATETIME(fsp=6), nullable=True),
        sa.Column('expires_at', mysql.DATETIME(fsp=6), nullable=True),
        sa.Column('instance_id', mysql.VARBINARY(128), nullable=False),
        sa.Column('source_generation', mysql.VARBINARY(128), nullable=False),
        sa.Column('source_seq', sa.BigInteger(), nullable=False),
        sa.Column('sample_id', mysql.VARBINARY(128), nullable=True),
        sa.CheckConstraint('db_number BETWEEN 1 AND 65535 AND source_seq > 0', name='ck_pfv2_latest_bounds'),
    )
    op.create_index('ix_pfv2_latest_expiry', 'plc_facts_latest_points_v2', ['expires_at', 'plc_id', 'db_number', 'point_id'])


def downgrade():
    connection = op.get_bind()
    for name in ('plc_facts_samples_v2', 'plc_facts_latest_points_v2'):
        if connection.execute(sa.text('SELECT 1 FROM ' + name + ' LIMIT 1')).first() is not None:
            raise RuntimeError('nonempty PLC facts v2 tables prohibit downgrade')
    op.drop_table('plc_facts_latest_points_v2')
    op.drop_table('plc_facts_samples_v2')
