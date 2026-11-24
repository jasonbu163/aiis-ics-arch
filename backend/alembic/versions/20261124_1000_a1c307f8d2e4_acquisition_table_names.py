"""ARCH-ACQ-007：受控停写窗口内同库原子更名三张采集表。"""
import os

from alembic import context, op
from sqlalchemy import bindparam, text

revision = "a1c307f8d2e4"
down_revision = "f0a2b4c6d8e1"
branch_labels = None
depends_on = None

RENAMES = {
    'plc_source_registry': 'acq_plc_source_registry',
    'plc_facts_history': 'acq_plc_facts_history',
    'plc_facts_latest': 'acq_plc_facts_latest',
}
CONSUMPTION_TABLES = {
    'acq_consumption_streams', 'acq_consumption_events', 'acq_consumers',
    'acq_consumer_deliveries', 'acq_consumer_operations', 'acq_consumption_activation',
}

# 冻结 ARCH-ACQ-006 的既有触发器定义；同库更名只更新所属表。
TRIGGERS = {
    'acq006_history_append': ('AFTER', 'INSERT', """
        BEGIN
          IF @acq006_append_seq IS NULL OR @acq006_append_seq < 1
             OR NOT (NEW.content_hash <=> @acq006_append_hash) OR NOT EXISTS (
            SELECT 1 FROM acq_consumption_streams
            WHERE plc_id = NEW.plc_id AND db_number = NEW.db_number AND last_seq = @acq006_append_seq
          ) OR NOT EXISTS (SELECT 1 FROM acq_consumption_activation WHERE id = 1 AND ready = 1)
          THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'acq006 guarded history append'; END IF;
          INSERT INTO acq_consumption_events
            (plc_id, db_number, event_seq, history_id, instance_id, sample_id, source_generation, expires_at)
          VALUES (NEW.plc_id, NEW.db_number, @acq006_append_seq, NEW.id, NEW.instance_id, NEW.sample_id,
                  NEW.source_generation, NEW.expires_at);
        END"""),
    'acq006_history_immutable': ('BEFORE', 'UPDATE', """
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'acq006 immutable history'"""),
    'acq006_history_expiry': ('BEFORE', 'DELETE', """
        BEGIN
          IF NOT (@acq006_prune_id <=> OLD.id) OR OLD.expires_at > CURRENT_TIMESTAMP(6)
             OR NOT EXISTS (SELECT 1 FROM acq_consumption_activation WHERE id = 1 AND ready = 1)
          THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'acq006 guarded history expiry'; END IF;
        END"""),
}


def _target(conn):
    uuid, schema, version, offset = conn.execute(text("""
        SELECT @@server_uuid, DATABASE(), VERSION(),
               TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))
    """)).one()
    if (not str(version).startswith('8.4.') or offset != 28800
            or not schema or schema.lower() in {'mysql', 'sys', 'performance_schema', 'information_schema'}
            or schema != os.environ.get('ACQ_TABLE_NAMES_EXPECTED_SCHEMA')
            or uuid != os.environ.get('ACQ_TABLE_NAMES_EXPECTED_SERVER_UUID')
            or os.environ.get('ACQ_TABLE_NAMES_WINDOW_CONFIRMED') != f'{schema}:{uuid}:{down_revision}'):
        raise RuntimeError('acquisition rename requires the exact inspected MySQL maintenance target and window')
    return schema


def _require_revision(conn, *, lock=False):
    query = 'SELECT version_num FROM alembic_version' + (' FOR UPDATE' if lock else '')
    if list(conn.execute(text(query)).scalars()) != [down_revision]:
        raise RuntimeError('acquisition rename requires the exact predecessor revision')


def _require_layout(conn, names, *, lock=False):
    table_names = tuple(RENAMES) + tuple(RENAMES.values()) + tuple(sorted(CONSUMPTION_TABLES))
    query = text("""
        SELECT TABLE_NAME, TABLE_TYPE, ENGINE FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN :names
    """).bindparams(bindparam('names', expanding=True))
    actual = {name: (table_type, engine) for name, table_type, engine
              in conn.execute(query, {'names': table_names})}
    expected = {name: ('BASE TABLE', 'InnoDB') for name in set(names) | CONSUMPTION_TABLES}
    if actual != expected:
        raise RuntimeError('missing, conflicting or partially renamed acquisition tables; inspect maintenance state')
    query = 'SELECT ready FROM acq_consumption_activation WHERE id = 1' + (' FOR UPDATE' if lock else '')
    ready = conn.execute(text(query)).scalar_one_or_none()
    if ready != 1:
        raise RuntimeError('acquisition consumption must be activated before rename')


def _require_triggers(conn, history):
    query = text("""
        SELECT TRIGGER_NAME, ACTION_TIMING, EVENT_MANIPULATION, EVENT_OBJECT_TABLE, ACTION_STATEMENT
        FROM information_schema.TRIGGERS
        WHERE TRIGGER_SCHEMA = DATABASE()
          AND (EVENT_OBJECT_TABLE IN :history_names OR TRIGGER_NAME IN :trigger_names)
    """).bindparams(bindparam('history_names', expanding=True), bindparam('trigger_names', expanding=True))
    rows = conn.execute(query, {'history_names': ('plc_facts_history', 'acq_plc_facts_history'),
                                'trigger_names': tuple(TRIGGERS)}).all()
    if {row[0] for row in rows} != set(TRIGGERS) or len(rows) != len(TRIGGERS):
        raise RuntimeError('unexpected or inaccessible acquisition history trigger set; keep writes stopped')
    for name, timing, event, table, body in rows:
        expected_timing, expected_event, expected_body = TRIGGERS[name]
        if ((timing, event, table) != (expected_timing, expected_event, history)
                or not body or ' '.join(body.split()) != ' '.join(expected_body.split())):
            raise RuntimeError(f'incompatible acquisition history trigger: {name}; keep writes stopped')


def _require_no_references(conn):
    # 外部 SQL、routine、event、触发器正文和授权须由目标 Owner 在确认窗口前另外审阅。
    names = {'names': tuple(RENAMES)}
    foreign_keys = text("""
        SELECT 1 FROM information_schema.KEY_COLUMN_USAGE
        WHERE (REFERENCED_TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IN :names)
           OR (TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN :names AND REFERENCED_TABLE_NAME IS NOT NULL)
        LIMIT 1
    """).bindparams(bindparam('names', expanding=True))
    views = text("""
        SELECT 1 FROM information_schema.VIEW_TABLE_USAGE
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN :names
        LIMIT 1
    """).bindparams(bindparam('names', expanding=True))
    if conn.execute(foreign_keys, names).first() or conn.execute(views, names).first():
        raise RuntimeError('visible foreign-key or view reference to acquisition table; keep writes stopped')


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError('acquisition rename requires an inspected online maintenance window')
    with op.get_context().autocommit_block():
        conn = op.get_bind()
        if conn.dialect.name != 'mysql':
            raise RuntimeError('acquisition rename requires MySQL 8.4')
        schema = _target(conn)
        lock = conn.execute(text('SELECT SHA2(CONCAT(:schema, :suffix), 256)'),
                            {'schema': schema, 'suffix': ':acq006'}).scalar_one()
        args = {'name': lock}
        if conn.execute(text('SELECT GET_LOCK(:name, 0)'), args).scalar_one() != 1:
            raise RuntimeError('another acquisition cutover is running')
        try:
            timeout = conn.execute(text('SELECT @@SESSION.lock_wait_timeout')).scalar_one()
            row_timeout = conn.execute(text('SELECT @@SESSION.innodb_lock_wait_timeout')).scalar_one()
            try:
                conn.execute(text('SET SESSION lock_wait_timeout = 5, innodb_lock_wait_timeout = 5'))
                conn.execute(text('START TRANSACTION'))
                _require_revision(conn, lock=True)
                _require_layout(conn, RENAMES, lock=True)
                _require_triggers(conn, 'plc_facts_history')
                _require_no_references(conn)
                # RENAME is atomic within this schema and commits the preceding SQL transaction.
                # The named lock and confirmed no-writer window remain required across DDL.
                pairs = ', '.join(f'`{old}` TO `{new}`' for old, new in RENAMES.items())
                conn.execute(text('RENAME TABLE ' + pairs))
                _require_layout(conn, RENAMES.values())
                _require_triggers(conn, 'acq_plc_facts_history')
                _require_revision(conn)
            finally:
                # Clears a preflight transaction on failure. MySQL cannot undo committed DDL.
                conn.execute(text('ROLLBACK'))
                conn.execute(text('SET SESSION lock_wait_timeout = :timeout, innodb_lock_wait_timeout = :row_timeout'),
                             {'timeout': timeout, 'row_timeout': row_timeout})
        finally:
            conn.execute(text('SELECT RELEASE_LOCK(:name)'), args)


def downgrade():
    raise RuntimeError('acquisition table rename is forward-only; use the inspected maintenance recovery procedure')
