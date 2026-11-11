"""ARCH-TASK-001 r1: guarded retirement of empty coil tables and generic task schema.

Revision ID: 5f7a9c1e3b25
Revises: 4e6a8b0d2f14
DDL is forward-only and not transactional in MySQL. Stop writers and retain the
approved external evidence / recovery plan before running this online revision.
"""
from uuid import UUID
import json
import os
import re
from alembic import context, op
from sqlalchemy import text

revision = '5f7a9c1e3b25'
down_revision = '4e6a8b0d2f14'
branch_labels = None
depends_on = None

OLD_TABLES = frozenset({
    'plans', 'performance_main', 'performance_split', 'performance_transform', 'performance_lineage',
    'performance_process_temperature', 'performance_process_tension', 'performance_process_speed',
    'performance_push_down_record', 'performance_integration_receipts', 'performance_integration_observation_events',
    'performance_mapping_receipts', 'performance_mapping_observation_state', 'quality_records', 'defect_records',
    'print_records', 'production_reports', 'performance_targets', 'assessments',
})
NEW_ONLY = frozenset({'plan_main', 'task_field_config_state', 'task_field_definitions',
                      'plan_dispatch_attempts', 'plan_action_events'})
SYSTEM_SCHEMAS = frozenset({'information_schema', 'mysql', 'performance_schema', 'sys'})
DDL = (
    """CREATE TABLE task_field_config_state (
	id TINYINT UNSIGNED NOT NULL,
	active_version INTEGER UNSIGNED NOT NULL DEFAULT 1,
	config_revision BIGINT UNSIGNED NOT NULL DEFAULT 1,
	created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	PRIMARY KEY (id),
	CONSTRAINT ck_task_config_singleton CHECK (id = 1)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE task_field_definitions (
	id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
	config_version INTEGER UNSIGNED NOT NULL,
	scope VARCHAR(24) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	slot_no TINYINT UNSIGNED NOT NULL,
	name VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	value_type VARCHAR(12) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	label_zh_cn VARCHAR(128) NOT NULL,
	label_en_us VARCHAR(128) NOT NULL,
	unit VARCHAR(32),
	is_nullable BOOL NOT NULL DEFAULT 0,
	enabled BOOL NOT NULL DEFAULT 0,
	sync_enabled BOOL NOT NULL DEFAULT 0,
	plan_editable BOOL NOT NULL DEFAULT 0,
	performance_editable BOOL NOT NULL DEFAULT 0,
	performance_owner VARCHAR(16) CHARACTER SET ascii COLLATE ascii_bin,
	plan_visible BOOL NOT NULL DEFAULT 0,
	performance_visible BOOL NOT NULL DEFAULT 0,
	plan_order SMALLINT UNSIGNED,
	performance_order SMALLINT UNSIGNED,
	created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	PRIMARY KEY (id),
	CONSTRAINT uq_task_field_slot UNIQUE (config_version, scope, slot_no),
	CONSTRAINT uq_task_field_name UNIQUE (config_version, scope, name),
	CONSTRAINT ck_task_field_scope_slot CHECK (scope IN ('shared_sync','plan_local','performance_local') AND slot_no BETWEEN 1 AND 100),
	CONSTRAINT ck_task_field_type CHECK (value_type IN ('string','number','boolean'))
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE plan_main (
	id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
	task_no VARCHAR(50) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	target_key VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	field_config_version INTEGER UNSIGNED NOT NULL,
	remark VARCHAR(500),
	created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	production_status VARCHAR(16) CHARACTER SET ascii COLLATE ascii_bin,
	priority SMALLINT UNSIGNED NOT NULL DEFAULT 5,
	dispatch_status VARCHAR(24) CHARACTER SET ascii COLLATE ascii_bin NOT NULL DEFAULT 'pending',
	local_values JSON NOT NULL DEFAULT (JSON_OBJECT()),
	sync_values JSON NOT NULL DEFAULT (JSON_OBJECT()),
	PRIMARY KEY (id),
	CONSTRAINT uq_task_no UNIQUE (task_no),
	CONSTRAINT ck_plan_local_values CHECK (JSON_TYPE(local_values) = 'OBJECT' AND JSON_LENGTH(local_values) <= 100),
	CONSTRAINT ck_plan_sync_values CHECK (JSON_TYPE(sync_values) = 'OBJECT' AND JSON_LENGTH(sync_values) <= 100),
	CONSTRAINT ck_plan_priority CHECK (priority BETWEEN 1 AND 10),
	CONSTRAINT ck_plan_production_status CHECK (production_status IS NULL OR production_status IN ('running','completed')),
	CONSTRAINT ck_plan_dispatch_status CHECK (dispatch_status IN ('pending','paused','claimed','exception','plc_accepted','cancelled','not_required'))
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE INDEX ix_created_page ON plan_main (created_at, id)""",
    """CREATE INDEX ix_plan_claim ON plan_main (target_key, dispatch_status, production_status, priority, created_at, id)""",
    """CREATE INDEX ix_plan_target_state_page ON plan_main (target_key, dispatch_status, created_at, id)""",
    """CREATE TABLE performance_main (
	id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
	task_no VARCHAR(50) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	target_key VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	field_config_version INTEGER UNSIGNED NOT NULL,
	remark VARCHAR(500),
	created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	production_status VARCHAR(16) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	started_at DATETIME(6),
	completed_at DATETIME(6),
	last_observed_at DATETIME(6),
	observation_seq BIGINT UNSIGNED NOT NULL,
	observation_digest BINARY(32) NOT NULL,
	record_source VARCHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	local_values JSON NOT NULL DEFAULT (JSON_OBJECT()),
	sync_values JSON NOT NULL DEFAULT (JSON_OBJECT()),
	PRIMARY KEY (id),
	CONSTRAINT uq_task_no UNIQUE (task_no),
	CONSTRAINT ck_performance_local_values CHECK (JSON_TYPE(local_values) = 'OBJECT' AND JSON_LENGTH(local_values) <= 100),
	CONSTRAINT ck_performance_sync_values CHECK (JSON_TYPE(sync_values) = 'OBJECT' AND JSON_LENGTH(sync_values) <= 100),
	CONSTRAINT ck_performance_status CHECK (production_status IN ('running','completed')),
	CONSTRAINT ck_performance_source CHECK (record_source IN ('sma','ca_ff'))
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE INDEX ix_created_page ON performance_main (created_at, id)""",
    """CREATE INDEX ix_perf_target_state_page ON performance_main (target_key, production_status, created_at, id)""",
    """CREATE TABLE plan_dispatch_attempts (
	dispatch_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	claim_request_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	task_no VARCHAR(50) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	target_key VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	attempt_no INTEGER UNSIGNED NOT NULL,
	field_config_version INTEGER UNSIGNED NOT NULL,
	producer_id VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	parameters JSON NOT NULL,
	attempt_status VARCHAR(24) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	active_target_key VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin GENERATED ALWAYS AS (CASE WHEN attempt_status IN ('claimed','exception') THEN target_key ELSE NULL END) STORED,
	submission_phase VARCHAR(24) CHARACTER SET ascii COLLATE ascii_bin,
	request_seq BIGINT UNSIGNED,
	ack_seq BIGINT UNSIGNED,
	ack_observed_at DATETIME(6),
	failure_key VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin,
	failure_detail VARCHAR(500),
	claimed_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	PRIMARY KEY (dispatch_id),
	CONSTRAINT uq_plan_claim_request UNIQUE (claim_request_id),
	CONSTRAINT uq_plan_attempt_number UNIQUE (task_no, attempt_no),
	CONSTRAINT uq_plan_active_target UNIQUE (active_target_key),
	CONSTRAINT ck_plan_attempt_status CHECK (attempt_status IN ('claimed','exception','plc_accepted','returned')),
	CONSTRAINT ck_plan_submission_phase CHECK (submission_phase IS NULL OR submission_phase IN ('not_submitted','possibly_submitted','acknowledged'))
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE plan_action_events (
	id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
	action_request_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	request_digest BINARY(32) NOT NULL,
	task_no VARCHAR(50) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	action_key VARCHAR(24) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	actor_id BIGINT UNSIGNED NOT NULL,
	from_status VARCHAR(24) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	to_status VARCHAR(24) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
	dispatch_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin,
	reason VARCHAR(500),
	evidence TEXT,
	created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
	PRIMARY KEY (id),
	CONSTRAINT uq_plan_action_request UNIQUE (action_request_id)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE INDEX ix_plan_action_task ON plan_action_events (task_no, id)""",
)


def _rows(connection, statement, parameters=None):
    return connection.execute(text(statement), parameters or {})


def _target(connection):
    expected_schema = os.environ.get('TASK_CUTOVER_SCHEMA', '')
    expected_server = os.environ.get('TASK_CUTOVER_SERVER_UUID', '')
    operation = os.environ.get('TASK_CUTOVER_OPERATION_ID', '')
    if not re.fullmatch(r'[A-Za-z0-9_]{1,64}', expected_schema) or not re.fullmatch(r'[A-Za-z0-9._-]{1,64}', operation):
        raise RuntimeError('task cutover requires explicitly identified schema and operation')
    try:
        if str(UUID(expected_server)) != expected_server:
            raise ValueError('noncanonical UUID')
    except ValueError:
        raise RuntimeError('task cutover requires canonical server UUID') from None
    actual_schema, actual_server, version, offset = _rows(connection, """
        SELECT DATABASE(), @@server_uuid, VERSION(),
               TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))
    """).one()
    if (actual_schema, actual_server) != (expected_schema, expected_server):
        raise RuntimeError('task cutover target mismatch')
    if str(version).split('-')[0] != '8.4.6' or offset != 28800:
        raise RuntimeError('task cutover requires MySQL 8.4.6 and Shanghai database clock')
    if list(_rows(connection, 'SELECT version_num FROM alembic_version').scalars()) != [down_revision]:
        raise RuntimeError('task cutover requires exact single predecessor')
    return expected_schema


def _drop_order(edges):
    remaining = set(OLD_TABLES)
    result = []
    while remaining:
        # Remove tables not referenced by another still-present legacy table.
        leaves = sorted(t for t in remaining if not any(parent == t and child in remaining for child, parent in edges))
        if not leaves:
            raise RuntimeError('task cutover found a cyclic legacy foreign-key dependency')
        result.extend(leaves)
        remaining.difference_update(leaves)
    return result


def _preflight(connection, schema):
    objects = list(_rows(connection, """
        SELECT TABLE_NAME, TABLE_TYPE FROM information_schema.TABLES WHERE TABLE_SCHEMA = :schema
    """, {'schema': schema}))
    base_tables = {name for name, kind in objects if kind == 'BASE TABLE'}
    object_names = {name for name, _ in objects}
    if not OLD_TABLES <= base_tables or NEW_ONLY & object_names:
        raise RuntimeError('task cutover found missing legacy table or occupied target name')
    for table in sorted(OLD_TABLES):
        if _rows(connection, f'SELECT 1 FROM `{table}` LIMIT 1').first() is not None:
            raise RuntimeError(f'task cutover requires empty legacy table {table}')
    edges = set()
    foreign_keys = _rows(connection, """
        SELECT TABLE_SCHEMA, TABLE_NAME, REFERENCED_TABLE_SCHEMA, REFERENCED_TABLE_NAME
        FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_NAME IS NOT NULL
          AND (TABLE_SCHEMA = :schema OR REFERENCED_TABLE_SCHEMA = :schema)
    """, {'schema': schema})
    for local_schema, child, target_schema, parent in foreign_keys:
        if target_schema == schema and parent in OLD_TABLES:
            if local_schema != schema or child not in OLD_TABLES:
                raise RuntimeError('task cutover found an external foreign key into legacy tables')
            edges.add((child, parent))
    names = re.compile(r'\b(?:' + '|'.join(re.escape(t) for t in sorted(OLD_TABLES, key=len, reverse=True)) + r')\b', re.I)
    for query in ("SELECT TABLE_SCHEMA, VIEW_DEFINITION FROM information_schema.VIEWS",
                  "SELECT ROUTINE_SCHEMA, ROUTINE_DEFINITION FROM information_schema.ROUTINES",
                  "SELECT EVENT_SCHEMA, EVENT_DEFINITION FROM information_schema.EVENTS"):
        for object_schema, definition in _rows(connection, query):
            if object_schema in SYSTEM_SCHEMAS:
                continue
            if definition is None or names.search(definition):
                raise RuntimeError('task cutover cannot rule out a visible view, routine or event dependency')
    for object_schema, object_table, definition in _rows(connection, """
        SELECT EVENT_OBJECT_SCHEMA, EVENT_OBJECT_TABLE, ACTION_STATEMENT FROM information_schema.TRIGGERS
    """):
        if object_schema in SYSTEM_SCHEMAS:
            continue
        if definition is None or (object_schema == schema and object_table in OLD_TABLES) or names.search(definition):
            raise RuntimeError('task cutover cannot rule out a trigger dependency')
    return _drop_order(edges)


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError('task cutover requires online guard; offline SQL is prohibited')
    connection = op.get_bind()
    schema = _target(connection)
    previous_timeout = _rows(connection, 'SELECT @@SESSION.lock_wait_timeout').scalar_one()
    _rows(connection, 'SET SESSION lock_wait_timeout = 5')
    try:
        order = _preflight(connection, schema)
        print(json.dumps({'task': 'ARCH-TASK-001', 'phase': 'preflight_passed', 'tables': order}))
        for table in order:
            op.execute(f'DROP TABLE `{table}`')
            print(json.dumps({'task': 'ARCH-TASK-001', 'phase': 'dropped', 'table': table}))
        for statement in DDL:
            op.execute(statement)
        op.execute('INSERT INTO task_field_config_state (id, active_version, config_revision) VALUES (1, 1, 1)')
        print(json.dumps({'task': 'ARCH-TASK-001', 'phase': 'created'}))
    finally:
        _rows(connection, 'SET SESSION lock_wait_timeout = :timeout', {'timeout': previous_timeout})


def downgrade():
    raise RuntimeError('task cutover is forward-only; approved recovery requires external DDL evidence')
