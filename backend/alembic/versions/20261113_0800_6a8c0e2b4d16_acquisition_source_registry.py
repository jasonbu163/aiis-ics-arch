"""ARCH-ACQ-004 r2: guarded, forward-only source registry schema.

Revision ID: 6a8c0e2b4d16
Revises: 5f7a9c1e3b25
MySQL DDL is not transactional. A partial result stops; restore a verified
predecessor backup after recording the actual objects and revision.
"""
import os
from uuid import UUID

from alembic import context, op
from sqlalchemy import inspect, text

revision = '6a8c0e2b4d16'
down_revision = '5f7a9c1e3b25'
branch_labels = None
depends_on = None

TABLES = ('acq_source_instances', 'acq_source_bindings', 'acq_source_generations', 'acq_source_write_scopes',
          'acq_source_read_scopes', 'acq_source_initialization')


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError('source registry migration requires an inspected online target')
    conn = op.get_bind()
    expected_uuid = os.environ.get('ACQ_REGISTRY_EXPECTED_SERVER_UUID', '')
    expected_schema = os.environ.get('ACQ_REGISTRY_EXPECTED_SCHEMA', '')
    try:
        if str(UUID(expected_uuid)) != expected_uuid or not expected_schema.strip():
            raise ValueError()
    except ValueError:
        raise RuntimeError('explicit expected UUID and schema required') from None
    if conn.dialect.name != 'mysql':
        raise RuntimeError('MySQL 8.4 required')
    conn.execute(text('SET SESSION lock_wait_timeout = 5'))
    conn.execute(text('SET SESSION innodb_lock_wait_timeout = 5'))
    row = conn.execute(text('SELECT @@server_uuid, DATABASE(), VERSION(), '
                            'TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))')).one()
    revisions = list(conn.execute(text('SELECT version_num FROM alembic_version FOR UPDATE')).scalars())
    if (str(row[0]).lower() != expected_uuid or row[1] != expected_schema
            or not str(row[2]).split('-')[0].startswith('8.4.') or row[3] != 28800
            or revisions != [down_revision]):
        raise RuntimeError('source registry target mismatch')
    existing = set(inspect(conn).get_table_names())
    if existing.intersection(TABLES):
        raise RuntimeError('source registry objects already exist; inspect and restore predecessor backup')
    # Import only after target preflight; create each explicit table in dependency order.
    from app.plc_facts.models.source_registry import (
        SourceInstance, SourceBinding, SourceGeneration, SourceWriteScope, SourceReadScope, SourceInitialization,
    )
    for model in (SourceInstance, SourceBinding, SourceGeneration, SourceWriteScope, SourceReadScope, SourceInitialization):
        model.__table__.create(conn, checkfirst=False)


def downgrade():
    raise RuntimeError('forward-only; use the documented verified restoration procedure')
