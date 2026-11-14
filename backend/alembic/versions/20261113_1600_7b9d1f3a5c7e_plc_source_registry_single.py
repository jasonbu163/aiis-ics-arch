"""归并 PLC 来源登记到单表。

Revision ID: 7b9d1f3a5c7e
Revises: 6a8c0e2b4d16

MySQL DDL 会隐式提交。中断后保留现场并按任务恢复步骤核对，
不能对部分结果执行 stamp 或盲目重跑。
"""
import hashlib
import json
import os
from uuid import UUID

from alembic import context, op
from sqlalchemy import inspect, select, text

revision = '7b9d1f3a5c7e'
down_revision = '6a8c0e2b4d16'
branch_labels = None
depends_on = None

OLD_TABLES = (
    'acq_source_instances', 'acq_source_bindings', 'acq_source_generations',
    'acq_source_write_scopes', 'acq_source_read_scopes', 'acq_source_initialization',
)


FACT_TABLES = {
    'plc_facts_history': 'id',
    'plc_facts_latest': 'plc_id, db_number, point_id',
}


def fact_snapshot(conn):
    """Reconcile schema and every fact row, including latest sequence watermarks."""
    result = {}
    for table, ordering in FACT_TABLES.items():
        ddl = conn.exec_driver_sql('SHOW CREATE TABLE `' + table + '`').one()[1]
        digest = hashlib.sha256()
        count = 0
        statement = text('SELECT * FROM `' + table + '` ORDER BY ' + ordering)
        rows = conn.execute(statement.execution_options(stream_results=True))
        try:
            for row in rows:
                count += 1
                for value in row:
                    encoded = repr(value).encode('utf-8')
                    digest.update(len(encoded).to_bytes(8, 'big'))
                    digest.update(encoded)
        finally:
            rows.close()
        result[table] = {'schemaSha256': hashlib.sha256(ddl.encode('utf-8')).hexdigest(),
                         'rowCount': count, 'rowsSha256': digest.hexdigest()}
    return result


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError('PLC source migration requires an inspected online target')
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
    target = conn.execute(text(
        'SELECT @@server_uuid, DATABASE(), VERSION(), '
        'TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))'
    )).one()
    revisions = list(conn.execute(text('SELECT version_num FROM alembic_version FOR UPDATE')).scalars())
    if (str(target[0]).lower() != expected_uuid or target[1] != expected_schema
            or not str(target[2]).split('-')[0].startswith('8.4.')
            or target[3] != 28800 or revisions != [down_revision]):
        raise RuntimeError('PLC source migration target mismatch')
    tables = set(inspect(conn).get_table_names())
    if not set(OLD_TABLES).issubset(tables) or 'plc_source_registry' in tables:
        raise RuntimeError('unexpected source registry objects; inspect and restore before retrying')

    marker_count = conn.execute(text('SELECT COUNT(*) FROM acq_source_initialization WHERE id = 1')).scalar_one()
    if marker_count != 1:
        counts = [conn.execute(text('SELECT COUNT(*) FROM ' + name)).scalar_one() for name in OLD_TABLES]
        if any(counts) or os.environ.get('ACQ_REGISTRY_R3_EMPTY_CONFIRMED') != '1':
            raise RuntimeError('source registry is not initialized; import the old profile or confirm an empty registry')

    facts_before = fact_snapshot(conn)
    print(json.dumps({'event': 'facts-before', 'tables': facts_before}, sort_keys=True))

    bindings = conn.execute(text(
        'SELECT b.plc_id, b.instance_id, b.source_generation, i.source_type, '
        'b.registration_revision, b.created_at, b.updated_at '
        'FROM acq_source_bindings b JOIN acq_source_instances i ON i.instance_id = b.instance_id '
        'ORDER BY b.plc_id'
    )).mappings().all()
    binding_count = conn.execute(text('SELECT COUNT(*) FROM acq_source_bindings')).scalar_one()
    if len(bindings) != binding_count:
        raise RuntimeError('source bindings have missing instances')
    generations = conn.execute(text(
        'SELECT plc_id, source_generation, instance_id FROM acq_source_generations ORDER BY plc_id, source_generation'
    )).all()
    retired = {}
    for plc_id, generation, instance_id in generations:
        retired.setdefault(bytes(plc_id), []).append((bytes(generation), bytes(instance_id)))
    records = []
    for row in bindings:
        plc_id = bytes(row['plc_id'])
        current = bytes(row['source_generation'])
        known = retired.pop(plc_id, [])
        if (current, bytes(row['instance_id'])) not in known:
            raise RuntimeError('active generation is missing or mismatched')
        previous = [value.decode('utf-8') for value, _ in known if value != current]
        records.append({
            'plc_id': plc_id,
            'instance_id': bytes(row['instance_id']),
            'source_generation': current,
            'source_type': row['source_type'],
            'retired_generations': previous,
            'registration_revision': row['registration_revision'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
        })
    if retired:
        raise RuntimeError('retired generations have missing bindings')

    from app.plc_facts.models.source_registry import (
        PlcSourceRegistry, SourceBinding, SourceGeneration, SourceInitialization,
        SourceInstance, SourceReadScope, SourceWriteScope,
    )
    table = PlcSourceRegistry.__table__
    table.create(conn, checkfirst=False)
    if records:
        conn.execute(table.insert(), records)
    saved = [dict(row) for row in conn.execute(select(table).order_by(table.c.plc_id)).mappings()]
    for row in saved:
        for column in ('plc_id', 'instance_id', 'source_generation'):
            row[column] = bytes(row[column])
    if saved != records:
        raise RuntimeError('source registry comparison failed; restore before retrying')

    facts_after = fact_snapshot(conn)
    print(json.dumps({'event': 'facts-after', 'tables': facts_after}, sort_keys=True))
    if facts_before != facts_after:
        raise RuntimeError('fact table reconciliation failed; inspect and restore before retrying')

    for model in (SourceGeneration, SourceWriteScope, SourceReadScope,
                  SourceBinding, SourceInstance, SourceInitialization):
        model.__table__.drop(conn, checkfirst=False)


def downgrade():
    raise RuntimeError('forward-only; use the documented verified restoration procedure')
