"""新增采集消费流；隔离停写窗口中保留原事实并回填索引。"""
import os

from alembic import context, op
from sqlalchemy import bindparam, text

revision = "da6c32f8a701"
down_revision = "c9e1a3b5d720"
branch_labels = None
depends_on = None

# 固定当期 DDL，后继模型变更不会改写此段迁移。
TABLE_DDL = (
    """
CREATE TABLE IF NOT EXISTS acq_consumption_activation (
	id SMALLINT UNSIGNED NOT NULL,
	cutoff_at DATETIME(6) NOT NULL,
	ready SMALLINT UNSIGNED NOT NULL,
	PRIMARY KEY (id)
)ENGINE=InnoDB
    """,
    """
CREATE TABLE IF NOT EXISTS acq_consumption_streams (
	plc_id VARBINARY(128) NOT NULL,
	db_number SMALLINT UNSIGNED NOT NULL,
	last_seq BIGINT NOT NULL,
	floor_seq BIGINT NOT NULL,
	PRIMARY KEY (plc_id, db_number)
)ENGINE=InnoDB
    """,
    """
CREATE TABLE IF NOT EXISTS acq_consumption_events (
	plc_id VARBINARY(128) NOT NULL,
	db_number SMALLINT UNSIGNED NOT NULL,
	event_seq BIGINT NOT NULL,
	history_id BIGINT NOT NULL,
	instance_id VARBINARY(128) NOT NULL,
	sample_id VARBINARY(128) NOT NULL,
	source_generation VARBINARY(128) NOT NULL,
	expires_at DATETIME(6) NOT NULL,
	PRIMARY KEY (plc_id, db_number, event_seq),
	CONSTRAINT uq_acq_consumption_history UNIQUE (history_id),
	KEY ix_acq_consumption_event_generation (plc_id, source_generation)
)ENGINE=InnoDB
    """,
    """
CREATE TABLE IF NOT EXISTS acq_consumers (
	consumer_id VARCHAR(36) NOT NULL,
	plc_id VARBINARY(128) NOT NULL,
	db_number SMALLINT UNSIGNED NOT NULL,
	start_mode VARCHAR(8) NOT NULL,
	start_at DATETIME(6) NOT NULL,
	start_seq BIGINT NOT NULL,
	last_confirmed_seq BIGINT NOT NULL,
	excluded_count BIGINT NOT NULL,
	excluded_first_seq BIGINT,
	excluded_last_seq BIGINT,
	target_plc VARBINARY(128) NOT NULL,
	target_db SMALLINT UNSIGNED NOT NULL,
	target_instance VARBINARY(128) NOT NULL,
	target_generation VARBINARY(128) NOT NULL,
	desired_state VARCHAR(8) NOT NULL,
	lease_id VARCHAR(36),
	lease_generation BIGINT NOT NULL,
	worker_id VARBINARY(128),
	lease_expires_at DATETIME(6),
	PRIMARY KEY (consumer_id),
	CONSTRAINT uq_acq_consumer_target_stream UNIQUE (target_plc, target_db, target_generation)
)ENGINE=InnoDB
    """,
    """
CREATE TABLE IF NOT EXISTS acq_consumer_deliveries (
	consumer_id VARCHAR(36) NOT NULL,
	delivery_id VARCHAR(36) NOT NULL,
	event_seq BIGINT NOT NULL,
	config_version VARCHAR(128) NOT NULL,
	config_hash BINARY(32) NOT NULL,
	serializer_version VARCHAR(128) NOT NULL,
	body_hash BINARY(32) NOT NULL,
	created_at DATETIME(6) NOT NULL,
	confirmed_at DATETIME(6),
	PRIMARY KEY (consumer_id, delivery_id),
	CONSTRAINT uq_acq_delivery_event UNIQUE (consumer_id, event_seq),
	KEY ix_acq_delivery_pending (consumer_id, confirmed_at, event_seq)
)ENGINE=InnoDB
    """,
    """
CREATE TABLE IF NOT EXISTS acq_consumer_operations (
	consumer_id VARCHAR(36) NOT NULL,
	operation_id VARCHAR(36) NOT NULL,
	fingerprint BINARY(32) NOT NULL,
	result JSON NOT NULL,
	PRIMARY KEY (consumer_id, operation_id)
)ENGINE=InnoDB
    """,
)

# Guard both the cutover snapshot and the active feed. An old writer cannot
# append a sample with no event. Expiry metadata outlives the history row.
TRIGGERS = {
    'acq006_history_append': ('AFTER', 'INSERT', 'plc_facts_history', """
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
    'acq006_history_immutable': ('BEFORE', 'UPDATE', 'plc_facts_history', """
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'acq006 immutable history'"""),
    'acq006_history_expiry': ('BEFORE', 'DELETE', 'plc_facts_history', """
        BEGIN
          IF NOT (@acq006_prune_id <=> OLD.id) OR OLD.expires_at > CURRENT_TIMESTAMP(6)
             OR NOT EXISTS (SELECT 1 FROM acq_consumption_activation WHERE id = 1 AND ready = 1)
          THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'acq006 guarded history expiry'; END IF;
        END"""),
}


def _target(conn):
    uuid, schema, version, offset = conn.execute(text("""
        SELECT @@server_uuid, DATABASE(), VERSION(),
               TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(), CURRENT_TIMESTAMP())
    """)).one()
    if (conn.dialect.name != 'mysql' or not str(version).startswith('8.4.') or offset != 28800
            or not schema or schema.lower() in {'mysql', 'sys', 'performance_schema', 'information_schema'}
            or schema != os.environ.get('ACQ_CONSUMPTION_EXPECTED_SCHEMA')
            or uuid != os.environ.get('ACQ_CONSUMPTION_EXPECTED_SERVER_UUID')
            or os.environ.get('ACQ_CONSUMPTION_WINDOW_CONFIRMED') != f'{schema}:{uuid}'
            or list(conn.execute(text('SELECT version_num FROM alembic_version')).scalars()) != [down_revision]):
        raise RuntimeError('acquisition consumption requires the exact inspected MySQL maintenance target')
    return schema


def _guard_metadata(conn):
    return conn.execute(text("""
        SELECT TRIGGER_NAME, ACTION_TIMING, EVENT_MANIPULATION, EVENT_OBJECT_TABLE, ACTION_STATEMENT
        FROM information_schema.TRIGGERS
        WHERE TRIGGER_SCHEMA = DATABASE()
          AND (EVENT_OBJECT_TABLE = 'plc_facts_history' OR TRIGGER_NAME IN :names)
    """).bindparams(bindparam('names', expanding=True)), {'names': tuple(TRIGGERS)}).all()


def _install_guards(conn):
    names = {row[0] for row in _guard_metadata(conn)}
    for name, (timing, event, table, body) in TRIGGERS.items():
        if name not in names:
            conn.execute(text(f'CREATE TRIGGER IF NOT EXISTS {name} {timing} {event} ON {table} FOR EACH ROW {body}'))
    existing = _guard_metadata(conn)
    for name, timing, event, table, body in existing:
        expected = TRIGGERS.get(name)
        if (expected is None or (timing, event, table) != expected[:3]
                or ' '.join(body.split()) != ' '.join(expected[3].split())):
            raise RuntimeError('unexpected history trigger; inspect maintenance state')
    if {row[0] for row in existing} != set(TRIGGERS):
        raise RuntimeError('incomplete history guards; inspect maintenance state')


# The cutoff is committed before indexing. Restarting uses the same cohort.
_EVENT_COHORT = """
    SELECT h.plc_id, h.db_number,
           ROW_NUMBER() OVER (PARTITION BY h.plc_id, h.db_number ORDER BY h.stored_at, h.id) AS event_seq,
           h.id AS history_id, h.instance_id, h.sample_id, h.source_generation, h.expires_at
    FROM plc_facts_history AS h JOIN acq_consumption_activation AS a ON a.id = 1
    WHERE h.expires_at > a.cutoff_at
"""


def _backfill(conn):
    conn.execute(text('START TRANSACTION'))
    try:
        conn.execute(text(f"""
            INSERT INTO acq_consumption_events
                (plc_id, db_number, event_seq, history_id, instance_id, sample_id, source_generation, expires_at)
            SELECT candidate.* FROM ({_EVENT_COHORT}) AS candidate
            LEFT JOIN acq_consumption_events AS existing ON existing.history_id = candidate.history_id
            WHERE existing.history_id IS NULL
        """))
        bad = conn.execute(text(f"""
            SELECT 1 FROM acq_consumption_events AS existing
            LEFT JOIN ({_EVENT_COHORT}) AS candidate ON existing.history_id = candidate.history_id
            WHERE candidate.history_id IS NULL OR NOT (
                existing.plc_id = candidate.plc_id AND existing.db_number = candidate.db_number
                AND existing.event_seq = candidate.event_seq AND existing.instance_id = candidate.instance_id
                AND existing.sample_id = candidate.sample_id AND existing.source_generation = candidate.source_generation
                AND existing.expires_at = candidate.expires_at
            ) LIMIT 1
        """)).first()
        if bad:
            raise RuntimeError('history feed backfill mismatch; inspect maintenance state')
        conn.execute(text("""
            INSERT INTO acq_consumption_streams (plc_id, db_number, last_seq, floor_seq)
            SELECT e.plc_id, e.db_number, MAX(e.event_seq), 0 FROM acq_consumption_events AS e
            LEFT JOIN acq_consumption_streams AS s ON s.plc_id = e.plc_id AND s.db_number = e.db_number
            WHERE s.plc_id IS NULL GROUP BY e.plc_id, e.db_number
        """))
        if conn.execute(text("""
            SELECT 1 FROM acq_consumption_streams AS s LEFT JOIN
              (SELECT plc_id, db_number, MAX(event_seq) AS last_seq
               FROM acq_consumption_events GROUP BY plc_id, db_number) AS e
              ON e.plc_id = s.plc_id AND e.db_number = s.db_number
            WHERE NOT (s.last_seq <=> e.last_seq) OR s.floor_seq <> 0 LIMIT 1
        """)).first():
            raise RuntimeError('history stream head mismatch; inspect maintenance state')
        conn.execute(text('UPDATE acq_consumption_activation SET ready = 1 WHERE id = 1'))
        conn.execute(text('COMMIT'))
    except BaseException:
        conn.execute(text('ROLLBACK'))
        raise


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError('acquisition consumption requires an inspected online maintenance target')
    with op.get_context().autocommit_block():
        conn = op.get_bind()
        if conn.dialect.name != 'mysql':
            raise RuntimeError('acquisition consumption requires MySQL 8.4')
        schema = _target(conn)
        lock_name = conn.execute(text('SELECT SHA2(CONCAT(:schema, :suffix), 256)'),
                                 {'schema': schema, 'suffix': ':acq006'}).scalar_one()
        if conn.execute(text('SELECT GET_LOCK(:name, 0)'), {'name': lock_name}).scalar_one() != 1:
            raise RuntimeError('another acquisition consumption cutover is running')
        timeout = conn.execute(text('SELECT @@SESSION.lock_wait_timeout')).scalar_one()
        try:
            _target(conn)
            conn.execute(text('SET SESSION lock_wait_timeout = 5'))
            for ddl in TABLE_DDL:
                conn.execute(text(ddl))
            _install_guards(conn)
            conn.execute(text("""
                INSERT INTO acq_consumption_activation (id, cutoff_at, ready) VALUES (1, CURRENT_TIMESTAMP(6), 0)
                ON DUPLICATE KEY UPDATE id = id
            """))
            _backfill(conn)
        finally:
            conn.execute(text('SET SESSION lock_wait_timeout = :timeout'), {'timeout': timeout})
            conn.execute(text('SELECT RELEASE_LOCK(:name)'), {'name': lock_name})


def downgrade():
    raise RuntimeError('acquisition consumption is forward-only; recovery requires the inspected cutover procedure')
