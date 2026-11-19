"""ARCH-TASK-001 r2 迁移：保留历史，补齐配置使用证据，放宽通用任务约束。

Revision ID: ae20b4d6f831
Revises: 9d1f3a5c7e20
"""
from collections import defaultdict
import json
import os
import re
from uuid import UUID

from alembic import context, op
from sqlalchemy import text

revision = 'ae20b4d6f831'
down_revision = '9d1f3a5c7e20'
branch_labels = None
depends_on = None

TASK_TABLES = {'plan_main', 'performance_main', 'plan_dispatch_attempts', 'plan_action_events',
               'task_field_config_state', 'task_field_definitions'}
NEW_TABLES = {'task_field_config_versions', 'task_field_config_uses'}
SYSTEM_SCHEMAS = {'mysql', 'information_schema', 'performance_schema', 'sys'}
SUBJECTS = {'plan_main': ('plan', 'task_no'), 'performance_main': ('performance', 'task_no'),
            'plan_dispatch_attempts': ('dispatch', 'dispatch_id')}
STATUS = ('running', 'completed')
TASK_NO = re.compile(r'[A-Z0-9._-]{1,50}')
TARGET_KEY = re.compile(r'[A-Za-z0-9._-]{1,64}')
FIELD_NAME = re.compile(r'[a-z][A-Za-z0-9_]{0,63}')
RESERVED = {'id', 'taskNo', 'targetKey', 'producerId', 'productionStatus', 'remark', 'priority',
            'createdAt', 'updatedAt', 'startedAt', 'completedAt', 'observedAt', 'lastObservedAt',
            'observationSeq', 'hasPlan', 'items', 'fieldConfigVersion', 'configVersion', 'backfillExisting'}
NUMBER = re.compile(r'-?(?:0|[1-9][0-9]{0,9})(?:\.[0-9]{1,4})?')
DDL = (
    """CREATE TABLE task_field_config_versions (
        config_version INTEGER UNSIGNED NOT NULL PRIMARY KEY,
        definition_count SMALLINT UNSIGNED NOT NULL,
        CONSTRAINT ck_task_config_definition_count CHECK (definition_count <= 300)
    ) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE task_field_config_uses (
        config_version INTEGER UNSIGNED NOT NULL,
        subject_kind VARCHAR(16) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
        subject_key VARCHAR(50) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
        PRIMARY KEY (config_version, subject_kind, subject_key),
        CONSTRAINT ck_task_config_use_kind CHECK (subject_kind IN ('plan','performance','dispatch')),
        CONSTRAINT fk_task_config_use_version FOREIGN KEY (config_version)
            REFERENCES task_field_config_versions (config_version)
    ) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """ALTER TABLE plan_main
        MODIFY target_key VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin NULL,
        DROP CHECK ck_plan_production_status,
        ADD CONSTRAINT ck_plan_production_status_r2 CHECK (production_status IN ('new','running','completed','error'))""",
    """ALTER TABLE performance_main
        MODIFY target_key VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin NULL,
        MODIFY observation_seq BIGINT UNSIGNED NULL,
        MODIFY observation_digest BINARY(32) NULL,
        MODIFY record_source VARCHAR(32) CHARACTER SET ascii COLLATE ascii_bin NULL,
        DROP CHECK ck_performance_status,
        ADD CONSTRAINT ck_performance_status_r2 CHECK (production_status IN ('new','running','completed','error'))""",
)
FILL_STATUS = """UPDATE plan_main AS plan LEFT JOIN performance_main AS perf ON plan.task_no = perf.task_no
    SET plan.production_status = COALESCE(perf.production_status, 'new')
    WHERE plan.production_status IS NULL"""
REQUIRE_STATUS = """ALTER TABLE plan_main
    MODIFY production_status VARCHAR(16) CHARACTER SET ascii COLLATE ascii_bin NOT NULL"""


def _execute(connection, sql, **parameters):
    return connection.execute(text(sql), parameters)


def _require(ok, reason):
    if not ok:
        raise RuntimeError(f'ARCH-TASK-001 r2: {reason}')


def _target(connection):
    _require(connection.dialect.name == 'mysql', 'migration requires MySQL')
    schema, uuid, version, time_offset = _execute(connection, """
        SELECT DATABASE(), @@server_uuid, VERSION(), TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(), NOW())
    """).one()
    expected_uuid = os.environ.get('TASK_R2_SERVER_UUID', '')
    operation = os.environ.get('TASK_R2_OPERATION_ID', '')
    _require(schema and schema not in SYSTEM_SCHEMAS and schema == os.environ.get('TASK_R2_SCHEMA')
             and uuid.lower() == expected_uuid.lower() and re.fullmatch(r'[A-Za-z0-9._-]{1,64}', operation),
             'approved schema, server UUID and operation identifier are required')
    _require(version.startswith('8.4.') and time_offset == 28800, 'unexpected database version or session time zone')
    _require(os.environ.get('TASK_R2_HISTORY_TIME_VERIFIED') == 'Asia/Shanghai',
             'historical time zone evidence must be confirmed before migration')
    _require(_execute(connection, 'SELECT version_num FROM alembic_version').scalars().all() == [down_revision],
             'database is not at the exact predecessor')
    return schema


def _dependencies(connection, schema):
    objects = dict(_execute(connection, """
        SELECT TABLE_NAME, CONCAT(TABLE_TYPE, ':', COALESCE(ENGINE, ''))
        FROM information_schema.TABLES WHERE TABLE_SCHEMA = :schema
    """, schema=schema).all())
    _require(all(objects.get(table) == 'BASE TABLE:InnoDB' for table in TASK_TABLES)
             and not NEW_TABLES.intersection(objects), 'missing task table or occupied evidence table name')
    _require(not _execute(connection, """
        SELECT TABLE_NAME FROM information_schema.KEY_COLUMN_USAGE
        WHERE REFERENCED_TABLE_NAME IS NOT NULL
          AND ((REFERENCED_TABLE_SCHEMA = :schema AND REFERENCED_TABLE_NAME IN
               ('plan_main','performance_main','plan_dispatch_attempts','plan_action_events','task_field_config_state','task_field_definitions'))
            OR (TABLE_SCHEMA = :schema AND TABLE_NAME IN
               ('plan_main','performance_main','plan_dispatch_attempts','plan_action_events','task_field_config_state','task_field_definitions')))
        LIMIT 1
    """, schema=schema).first(), 'dependent foreign key found')
    names = re.compile(r'\b(?:' + '|'.join(sorted(TASK_TABLES)) + r')\b', re.I)
    for query in ('SELECT TABLE_SCHEMA, VIEW_DEFINITION FROM information_schema.VIEWS',
                  'SELECT ROUTINE_SCHEMA, ROUTINE_DEFINITION FROM information_schema.ROUTINES',
                  'SELECT EVENT_SCHEMA, EVENT_DEFINITION FROM information_schema.EVENTS'):
        for owner, definition in _execute(connection, query):
            if owner not in SYSTEM_SCHEMAS:
                _require(definition is not None and not names.search(definition), 'unverified view, routine or event dependency')
    for owner, table, statement in _execute(connection, """
        SELECT EVENT_OBJECT_SCHEMA, EVENT_OBJECT_TABLE, ACTION_STATEMENT FROM information_schema.TRIGGERS
    """):
        if owner not in SYSTEM_SCHEMAS:
            _require(not (owner == schema and table in TASK_TABLES) and statement is not None
                     and not names.search(statement), 'unverified trigger dependency')


def _json_object(raw):
    value = json.loads(raw) if isinstance(raw, (str, bytes)) else raw
    _require(isinstance(value, dict) and len(value) <= 100, 'historical values are not a valid slot object')
    return value


def _known_fields(connection, active_version):
    snapshots = defaultdict(dict, {1: {}})
    for version, scope, slot, name, kind, unit in _execute(connection, """
        SELECT config_version, scope, slot_no, name, value_type, unit FROM task_field_definitions
    """):
        _require(1 <= version <= active_version and 1 <= slot <= 100
                 and scope in ('shared_sync', 'plan_local', 'performance_local')
                 and kind in ('string', 'boolean', 'number') and FIELD_NAME.fullmatch(name) and name not in RESERVED,
                 'historical definition cannot be interpreted unambiguously')
        key = (scope, f'{slot:02d}')
        _require(key not in snapshots[version], 'historical field slot is ambiguous')
        snapshots[version][key] = (name, kind, unit)
    _require(len(snapshots) == active_version, 'historical definition version is missing')
    for snapshot in snapshots.values():
        for group in ('plan_local', 'performance_local'):
            names = [name for (scope, _), (name, _, _) in snapshot.items() if scope in ('shared_sync', group)]
            _require(len(names) == len(set(names)), 'historical field names are ambiguous')
    return snapshots


def _valid_value(value, kind):
    return isinstance(value, str) and (
        (kind == 'string' and len(value) <= 255) or
        (kind == 'boolean' and value in ('true', 'false')) or
        (kind == 'number' and NUMBER.fullmatch(value) is not None)
    )


def _verify_slots(values, scope, bound, current):
    for slot, value in _json_object(values).items():
        key = (scope, slot)
        definition = bound.get(key)
        _require(definition is not None and definition == current.get(key) and _valid_value(value, definition[1]),
                 'a historical slot or type cannot be safely interpreted by the current configuration')


def _history(connection):
    versions = _execute(connection, 'SELECT active_version FROM task_field_config_state WHERE id = 1').scalars().all()
    _require(len(versions) == 1, 'current configuration state is missing')
    active_version = versions[0]
    snapshots = _known_fields(connection, active_version)
    current = snapshots[active_version]
    for table, module in (('plan_main', 'plan'), ('performance_main', 'performance')):
        for task, target, status, version, shared, local in _execute(connection, f"""
            SELECT task_no, target_key, production_status, field_config_version, sync_values, local_values FROM {table}
        """):
            _require(TASK_NO.fullmatch(task) and isinstance(target, str) and TARGET_KEY.fullmatch(target)
                     and (status in STATUS or (module == 'plan' and status is None)) and version in snapshots,
                     'historical task identity, status, target or configuration is invalid')
            _verify_slots(shared, 'shared_sync', snapshots[version], current)
            _verify_slots(local, module + '_local', snapshots[version], current)
    _require(not _execute(connection, """
        SELECT 1 FROM plan_main AS plan JOIN performance_main AS perf ON plan.task_no = perf.task_no
        WHERE plan.target_key <> perf.target_key LIMIT 1
    """).first(), 'historical same-number targets conflict')
    for dispatch_id, version in _execute(connection, 'SELECT dispatch_id, field_config_version FROM plan_dispatch_attempts'):
        try:
            valid_id = str(UUID(dispatch_id)) == dispatch_id
        except (ValueError, TypeError, AttributeError):
            valid_id = False
        _require(valid_id and version in snapshots, 'historical dispatch identity or configuration is invalid')
    _require(not _execute(connection, '''
        SELECT 1 FROM plan_action_events AS event LEFT JOIN plan_dispatch_attempts AS attempt
          ON event.dispatch_id = attempt.dispatch_id AND event.task_no = attempt.task_no
        WHERE event.dispatch_id IS NOT NULL AND attempt.dispatch_id IS NULL LIMIT 1
    ''').first(), 'historical action references an unknown dispatch attempt')
    return {version: len(snapshot) for version, snapshot in snapshots.items()}


def upgrade():
    _require(not context.is_offline_mode(), 'online guards are required before applying DDL')
    connection = op.get_bind()
    schema = _target(connection)
    previous_timeout = _execute(connection, 'SELECT @@SESSION.lock_wait_timeout').scalar_one()
    _execute(connection, 'SET SESSION lock_wait_timeout = 5')
    try:
        _dependencies(connection, schema)
        counts = _history(connection)
        print('ARCH-TASK-001 r2 target and historical preflight passed')
        # MySQL DDL auto-commits. These steps are deliberately forward-only and require an external backup.
        for statement in DDL[:2]:
            op.execute(statement)
        connection.execute(text("""
            INSERT INTO task_field_config_versions (config_version, definition_count) VALUES (:version, :count)
        """), [{'version': version, 'count': count} for version, count in sorted(counts.items())])
        for table, (kind, identity) in SUBJECTS.items():
            _execute(connection, f"""
                INSERT INTO task_field_config_uses (config_version, subject_kind, subject_key)
                SELECT field_config_version, :kind, {identity} FROM {table}
            """, kind=kind)
        print('ARCH-TASK-001 r2 historical configuration evidence copied')
        for statement in DDL[2:]:
            op.execute(statement)
        op.execute(FILL_STATUS)
        op.execute(REQUIRE_STATUS)
        print('ARCH-TASK-001 r2 task constraints and null-state conversion applied')
    finally:
        _execute(connection, 'SET SESSION lock_wait_timeout = :timeout', timeout=previous_timeout)


def downgrade():
    raise RuntimeError('ARCH-TASK-001 r2 is forward-only. Restore only from an approved, reconciled backup.')
