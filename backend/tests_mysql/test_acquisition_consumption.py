"""ARCH-ACQ-007 隔离 MySQL 8.4 更名、并发和 HTTP 消费回归。"""
import asyncio
from contextlib import closing
from contextvars import ContextVar
from datetime import datetime, timedelta
from hashlib import sha256
import json
import os
from pathlib import Path
from secrets import token_urlsafe
from sqlite3 import connect as sqlite_connect
from types import SimpleNamespace
import subprocess
import sys
from uuid import UUID, uuid4

import pytest

ENV = ('ACQ007_TEST_ROLE', 'ACQ007_TEST_PORT', 'ACQ007_TEST_SERVER_UUID',
       'ACQ007_TEST_PASSWORD', 'ACQ007_TEST_EXECUTION_ACK')
if not all(os.environ.get(key) for key in ENV):
    pytest.skip('ARCH-ACQ-007 requires a dedicated throwaway MySQL instance', allow_module_level=True)

import httpx
import pymysql
import pytest_asyncio
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from app.equipment_observation.services import guard as observation_guard
from app.plc_facts.api import consumption, source_registry, v2
from app.plc_facts.consumption_config import get_grants
from app.plc_facts.crud import async_v2
from app.plc_facts.services import async_consumption, observation_evidence, sync_v2_maintenance
from app.plc_facts.v2_config import CONSUMPTION_REVISION, TABLE_NAMES_REVISION, load_profile
from app.plc_facts.v2_domain import V2Error, wire_time
from core.registrar import create_app

ROLE, PORT, SERVER, PASSWORD, CONFIRM = (os.environ[key] for key in ENV)
if (ROLE not in {'dev', 'qa'} or not PORT.isdecimal() or not 20000 <= int(PORT) <= 65535
        or str(UUID(SERVER)) != SERVER or CONFIRM != f'ARCH-ACQ-007-r2:{ROLE}:127.0.0.1:{PORT}:{SERVER}'):
    raise RuntimeError('isolated MySQL identity not explicitly confirmed')

ROOT = Path(__file__).resolve().parents[1]
API = '/api/v1/acquisition-consumers'
SAMPLES = '/api/v1/integration/plc-facts/samples'
PREDECESSOR = 'c9e1a3b5d720'
TABLE_NAMES_PREDECESSOR = 'f0a2b4c6d8e1'
UNRELATED_FIXTURE_REVISION = 'eeeeeeeeeeee'
LEGACY_FACT_TABLES = ('plc_source_registry', 'plc_facts_history', 'plc_facts_latest')
CONSUMPTION_TABLES = ('acq_consumption_streams', 'acq_consumption_events', 'acq_consumers',
                      'acq_consumer_deliveries', 'acq_consumer_operations', 'acq_consumption_activation')
PUBLIC_PERMISSIONS = ['create', 'read', 'run', 'lease', 'pending', 'ack', 'target']


def connection(schema=None):
    conn = pymysql.connect(host='127.0.0.1', port=int(PORT), user='root', password=PASSWORD,
                           database=schema, autocommit=True, connect_timeout=5)
    with conn.cursor() as cursor:
        cursor.execute('SELECT @@server_uuid, VERSION(), TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(), CURRENT_TIMESTAMP())')
        server, version, offset = cursor.fetchone()
    if server != SERVER or not version.startswith('8.4.') or offset != 28800:
        conn.close()
        raise RuntimeError('isolated MySQL UUID, version or clock mismatch')
    return conn


def run_sql(schema, statement, params=None):
    with connection(schema) as conn, conn.cursor() as cursor:
        cursor.execute(statement, params)
        return cursor.fetchall()


def migrate(schema, revision, *, confirmed=True, extra_versions=None):
    env = dict(os.environ)
    env.update(APP_NAME='ACQ006 fixture', APP_VERSION='1.0.0', DEBUG='False', TESTING='True',
               PRIMARY_DATABASE='mysql', MYSQL_ENABLED='True', MYSQL_HOST='127.0.0.1',
               MYSQL_PORT=PORT, MYSQL_USER='root', MYSQL_PASSWORD=PASSWORD, MYSQL_DATABASE='unused',
               TEST_MYSQL_DATABASE=schema, MYSQL_ROOT_USER='root', MYSQL_ROOT_PASSWORD=PASSWORD,
               JWT_SECRET_KEY='0' * 64, JWT_ALGORITHM='HS256', ACCESS_TOKEN_EXPIRE_MINUTES='5',
               REFRESH_TOKEN_EXPIRE_DAYS='1', API_V1_PREFIX='/api/v1',
               BACKEND_MOCK_ENABLED='False', ADMIN_BOOTSTRAP_ENABLED='False', PYTHONDONTWRITEBYTECODE='1')
    for prefix in ('ACQ_RETIREMENT', 'ACQ_FACTS', 'ACQ_REGISTRY', 'OBS_RETIREMENT', 'ACQ_CONSUMPTION',
                   'OBS_RECEIPT', 'OBS_WRITE', 'QUALITY', 'ACQ_TABLE_NAMES'):
        env[f'{prefix}_EXPECTED_SCHEMA'] = schema
        env[f'{prefix}_EXPECTED_SERVER_UUID'] = SERVER
    env.update(ACQ_FACTS_OPERATION_ID='arch-acq006-bootstrap', ACQ_REGISTRY_R3_EMPTY_CONFIRMED='1',
               TASK_CUTOVER_SCHEMA=schema, TASK_CUTOVER_SERVER_UUID=SERVER, TASK_CUTOVER_OPERATION_ID='arch-acq006',
               TASK_R2_SCHEMA=schema, TASK_R2_SERVER_UUID=SERVER, TASK_R2_OPERATION_ID='arch-acq006-r2',
               TASK_R2_HISTORY_TIME_VERIFIED='Asia/Shanghai', OBS_RETIREMENT_WINDOW_CONFIRMED=f'{schema}:{SERVER}',
               OBS_RECEIPT_WINDOW_CONFIRMED=f'{schema}:{SERVER}',
               ACQ_CONSUMPTION_WINDOW_CONFIRMED=f'{schema}:{SERVER}' if confirmed else 'unconfirmed',
               ACQ_TABLE_NAMES_WINDOW_CONFIRMED=(
                   f'{schema}:{SERVER}:{TABLE_NAMES_PREDECESSOR}' if confirmed else 'unconfirmed'))
    if extra_versions is None:
        command = [sys.executable, '-m', 'alembic', '-x', 'obs_r10_writers_quiesced=yes', 'upgrade', revision]
    else:
        command = [sys.executable, '-c', '''
from alembic import command
from alembic.config import Config
from pathlib import Path
import os
import sys
configuration = Config("alembic.ini", cmd_opts=type("Args", (), {"x": ["obs_r10_writers_quiesced=yes"]})())
configuration.set_main_option("version_locations", os.pathsep.join((str(Path("alembic/versions").resolve()), sys.argv[1])))
command.upgrade(configuration, sys.argv[2])
''', str(extra_versions), revision]
    return subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=90)


def add_source(schema, plc, kind='daa', generation='g1', *, legacy=False):
    table = 'plc_source_registry' if legacy else 'acq_plc_source_registry'
    run_sql(schema, f"""
        INSERT INTO {table} (plc_id, instance_id, source_generation, source_type,
             retired_generations, registration_revision)
        VALUES (%s, %s, %s, %s, JSON_ARRAY(), %s)
    """, (plc, 'instance-' + plc, generation, kind, str(uuid4())))


def bytes_body(body):
    return json.dumps(body, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def sample(plc, seq, timestamp, *, db=21, generation='g1', sample_id=None):
    return {'contractVersion': 'plc-facts/v2', 'instanceId': 'instance-' + plc,
            'sampleId': sample_id or f'{plc}-{generation}-{seq}', 'plcId': plc, 'dbNumber': db,
            'sourceGeneration': generation, 'sourceSeq': str(seq),
            'points': [{'pointId': 'zero', 'dataType': 'INT', 'value': 0,
                        'quality': 'good', 'observedAt': wire_time(timestamp)}]}


def insert_old(schema, seq, observed, expires, stored):
    run_sql(schema, """
        INSERT INTO plc_facts_history (instance_id, sample_id, plc_id, db_number, source_generation,
             source_seq, points_json, content_hash, sampled_at, stored_at, expires_at, source_type)
        VALUES (%s, %s, %s, 21, 'g1', %s, %s, %s, %s, %s, %s, 'daa')
    """, ('instance-old', f'old-g1-{seq}', 'old', seq,
          bytes_body(sample('old', seq, observed)['points']), b'x' * 32, observed, stored, expires))


def test_fresh_schema_uses_full_alembic_chain_from_same_candidate():
    schema = f'arch_acq007_r2_{ROLE}_fresh_{uuid4().hex[:12]}'
    run_sql(None, f'CREATE DATABASE `{schema}` CHARACTER SET utf8mb4')
    try:
        assert run_sql(schema, 'SHOW TABLES') == ()
        result = migrate(schema, TABLE_NAMES_REVISION)
        assert result.returncode == 0, result.stderr
        for step in ('-> d4e6f8a0b2c4', '6a8c0e2b4d16 -> 7b9d1f3a5c7e',
                     f'{TABLE_NAMES_PREDECESSOR} -> {TABLE_NAMES_REVISION}'):
            assert step in result.stderr
        names = {name for (name,) in run_sql(schema, 'SHOW TABLES')}
        assert names.isdisjoint(LEGACY_FACT_TABLES)
        assert names.issuperset(tuple('acq_' + name for name in LEGACY_FACT_TABLES) + CONSUMPTION_TABLES)
        assert run_sql(schema, 'SELECT version_num FROM alembic_version') == ((TABLE_NAMES_REVISION,),)
        assert run_sql(schema, 'SELECT id, ready FROM acq_consumption_activation') == ((1, 1),)
        assert run_sql(schema, 'SELECT COUNT(*) FROM acq_plc_source_registry') == ((0,),)
    finally:
        run_sql(None, f'DROP DATABASE `{schema}`')


@pytest.fixture(scope='module')
def isolated(tmp_path_factory):
    schema = f'arch_acq007_r2_{ROLE}_{uuid4().hex[:12]}'
    run_sql(None, f'CREATE DATABASE `{schema}` CHARACTER SET utf8mb4')
    try:
        r2_registry = migrate(schema, '6a8c0e2b4d16')
        assert r2_registry.returncode == 0, r2_registry.stderr
        timestamp = datetime(2026, 1, 2, 3, 4, 5, 987654)
        registration = str(uuid4())
        run_sql(schema, "INSERT INTO acq_source_instances VALUES ('fixture-instance','daa')")
        run_sql(schema, '''
            INSERT INTO acq_source_bindings
            VALUES ('frozen-source','fixture-instance','active-gen',%s,%s,%s)
        ''', (registration, timestamp, timestamp))
        run_sql(schema, '''
            INSERT INTO acq_source_generations (plc_id, source_generation, instance_id)
            VALUES ('frozen-source','retired-gen','fixture-instance'), ('frozen-source','active-gen','fixture-instance')
        ''')
        run_sql(schema, '''
            INSERT INTO acq_source_initialization (id, input_hash, logical_hash, target_hash)
            VALUES (1, UNHEX(REPEAT('11',32)), UNHEX(REPEAT('22',32)), UNHEX(REPEAT('33',32)))
        ''')
        pre = migrate(schema, PREDECESSOR)
        assert pre.returncode == 0, pre.stderr
        assert run_sql(schema, '''
            SELECT instance_id, source_generation, source_type, retired_generations,
                   registration_revision, created_at, updated_at
            FROM plc_source_registry WHERE plc_id='frozen-source'
        ''') == ((b'fixture-instance', b'active-gen', 'daa', '["retired-gen"]',
                  registration, timestamp, timestamp),)
        ddl = run_sql(schema, 'SHOW CREATE TABLE plc_source_registry')[0][1]
        for fragment in ("PRIMARY KEY (`plc_id`)", "ENGINE=InnoDB", "DEFAULT CURRENT_TIMESTAMP(6)",
                         "ascii_bin", "ck_plc_source_type"):
            assert fragment in ddl
        assert not run_sql(schema, "SHOW TABLES LIKE 'acq_plc_source_registry'")
        now = run_sql(schema, 'SELECT CURRENT_TIMESTAMP(6)')[0][0]
        add_source(schema, 'old', legacy=True)
        insert_old(schema, 1, now - timedelta(days=2), now + timedelta(days=30), now - timedelta(seconds=15))
        insert_old(schema, 2, now - timedelta(days=100), now - timedelta(days=1), now - timedelta(seconds=10))
        insert_old(schema, 3, now - timedelta(days=1), now + timedelta(days=31), now - timedelta(seconds=5))
        run_sql(schema, """
            INSERT INTO plc_facts_latest
                (plc_id, db_number, point_id, data_type, value_json, quality, observed_at, expires_at,
                 instance_id, source_generation, source_seq, sample_id)
            VALUES ('old', 21, 'zero', 'INT', CAST('0' AS JSON), 'good', %s, %s, 'instance-old', 'g1', 3, 'old-g1-3')
        """, (now - timedelta(days=1), now + timedelta(days=31)))
        before = [run_sql(schema, f'SELECT * FROM {table}')
                  for table in ('plc_facts_history', 'plc_facts_latest', 'plc_source_registry')]

        refused = migrate(schema, CONSUMPTION_REVISION, confirmed=False)
        assert refused.returncode != 0 and 'exact inspected MySQL maintenance target' in refused.stderr
        assert run_sql(schema, "SHOW TABLES LIKE 'acq_consumption_events'") == ()

        # A conflicting task-owned trigger interrupts after DDL. Resume keeps the inspected data.
        run_sql(schema, """
            CREATE TRIGGER acq006_history_immutable BEFORE UPDATE ON plc_facts_history
            FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'synthetic interrupted cutover'
        """)
        interrupted = migrate(schema, CONSUMPTION_REVISION)
        assert interrupted.returncode != 0 and 'unexpected history trigger' in interrupted.stderr
        assert run_sql(schema, 'SELECT version_num FROM alembic_version') == ((PREDECESSOR,),)
        with pytest.raises(pymysql.MySQLError, match='guarded history append'):
            insert_old(schema, 4, now, now + timedelta(days=30), now)
        with pytest.raises(pymysql.MySQLError, match='guarded history expiry'):
            run_sql(schema, "DELETE FROM plc_facts_history WHERE sample_id='old-g1-2'")
        run_sql(schema, 'DROP TRIGGER acq006_history_immutable')
        for timing, event, table in (
            ('AFTER', 'UPDATE', 'plc_facts_history'),
            ('BEFORE', 'DELETE', 'plc_facts_history'),
            ('BEFORE', 'UPDATE', 'plc_facts_latest'),
        ):
            # Same name and body must not mask different trigger metadata.
            run_sql(schema, f"""
                CREATE TRIGGER acq006_history_immutable {timing} {event} ON {table}
                FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'acq006 immutable history'
            """)
            refused = migrate(schema, CONSUMPTION_REVISION)
            assert refused.returncode != 0 and 'unexpected history trigger' in refused.stderr
            assert run_sql(schema, 'SELECT version_num FROM alembic_version') == ((PREDECESSOR,),)
            assert not run_sql(schema, 'SELECT id FROM acq_consumption_activation WHERE ready=1')
            assert before == [run_sql(schema, f'SELECT * FROM {table}')
                              for table in ('plc_facts_history', 'plc_facts_latest', 'plc_source_registry')]
            run_sql(schema, 'DROP TRIGGER acq006_history_immutable')
        # An interruption with existing matching events reuses the original cutoff and rows.
        run_sql(schema, 'INSERT INTO acq_consumption_activation VALUES (1, %s, 0)', (now,))
        run_sql(schema, """
            INSERT INTO acq_consumption_events
              (plc_id, db_number, event_seq, history_id, instance_id, sample_id, source_generation, expires_at)
            SELECT plc_id, db_number, 1, id, instance_id, sample_id, source_generation, expires_at
            FROM plc_facts_history WHERE sample_id='old-g1-1'
        """)
        resumed = migrate(schema, CONSUMPTION_REVISION)
        assert resumed.returncode == 0, resumed.stderr
        assert before == [run_sql(schema, f'SELECT * FROM {table}')
                          for table in ('plc_facts_history', 'plc_facts_latest', 'plc_source_registry')]
        assert run_sql(schema, 'SELECT event_seq, sample_id FROM acq_consumption_events ORDER BY event_seq') == (
            (1, b'old-g1-1'), (2, b'old-g1-3'),
        )
        assert run_sql(schema, 'SELECT version_num FROM alembic_version') == ((CONSUMPTION_REVISION,),)
        quality = migrate(schema, TABLE_NAMES_PREDECESSOR)
        assert quality.returncode == 0, quality.stderr
        run_sql(schema, '''
            INSERT INTO acq_consumers VALUES
            ('fixture-consumer','old',21,'retained',NOW(6),2,1,0,NULL,NULL,
             'reserved-target',21,'reserved-instance','g1','paused',NULL,0,NULL,NULL)
        ''')
        run_sql(schema, '''
            INSERT INTO acq_consumer_deliveries VALUES
            ('fixture-consumer','fixture-delivery',2,'config-v1',UNHEX(REPEAT('10',32)),
             'serializer.v1',UNHEX(REPEAT('20',32)),NOW(6),NULL)
        ''')
        run_sql(schema, '''
            INSERT INTO acq_consumer_operations VALUES
            ('fixture-consumer','fixture-operation',UNHEX(REPEAT('30',32)),JSON_OBJECT('eventSeq','2'))
        ''')

        def snapshot(tables):
            return [(sorted(run_sql(schema, f'SELECT * FROM {table}'), key=repr),
                     sorted((r[1:6], r[7], r[10], r[13], r[14]) for r in run_sql(schema, f'SHOW INDEX FROM {table}')))
                    for table in tables]

        before_rename = snapshot(LEGACY_FACT_TABLES + CONSUMPTION_TABLES)
        refused = migrate(schema, TABLE_NAMES_REVISION, confirmed=False)
        assert refused.returncode != 0 and 'exact inspected MySQL maintenance target' in refused.stderr
        run_sql(schema, 'DROP TRIGGER acq006_history_immutable')
        run_sql(schema, """
            CREATE TRIGGER acq006_history_immutable BEFORE UPDATE ON plc_facts_latest
            FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'acq006 immutable history'
        """)
        wrong_trigger = migrate(schema, TABLE_NAMES_REVISION)
        assert wrong_trigger.returncode != 0 and 'incompatible acquisition history trigger' in wrong_trigger.stderr
        assert snapshot(LEGACY_FACT_TABLES + CONSUMPTION_TABLES) == before_rename
        run_sql(schema, 'DROP TRIGGER acq006_history_immutable')
        for timing, event, message in (
            ('AFTER', 'UPDATE', 'acq006 immutable history'),
            ('BEFORE', 'DELETE', 'acq006 immutable history'),
            ('BEFORE', 'UPDATE', 'wrong definition'),
        ):
            run_sql(schema, f'''
                CREATE TRIGGER acq006_history_immutable {timing} {event} ON plc_facts_history
                FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = %s
            ''', (message,))
            rejected = migrate(schema, TABLE_NAMES_REVISION)
            assert rejected.returncode != 0 and 'incompatible acquisition history trigger' in rejected.stderr
            run_sql(schema, 'DROP TRIGGER acq006_history_immutable')
        run_sql(schema, """
            CREATE TRIGGER acq006_history_immutable BEFORE UPDATE ON plc_facts_history
            FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'acq006 immutable history'
        """)
        run_sql(schema, 'CREATE TABLE acq_plc_facts_history LIKE plc_facts_history')
        collision = migrate(schema, TABLE_NAMES_REVISION)
        assert collision.returncode != 0 and 'missing, conflicting or partially renamed' in collision.stderr
        run_sql(schema, 'DROP TABLE acq_plc_facts_history')
        run_sql(schema, 'RENAME TABLE plc_source_registry TO acq_plc_source_registry')
        partial = migrate(schema, TABLE_NAMES_REVISION)
        assert partial.returncode != 0 and 'missing, conflicting or partially renamed' in partial.stderr
        run_sql(schema, 'RENAME TABLE acq_plc_source_registry TO plc_source_registry')
        renamed = migrate(schema, TABLE_NAMES_REVISION)
        assert renamed.returncode == 0, renamed.stderr
        assert snapshot(tuple('acq_' + name for name in LEGACY_FACT_TABLES) + CONSUMPTION_TABLES) == before_rename
        with pytest.raises(pymysql.MySQLError, match='immutable history'):
            run_sql(schema, "UPDATE acq_plc_facts_history SET source_type='external' WHERE sample_id='old-g1-1'")
        with pytest.raises(pymysql.MySQLError, match='guarded history expiry'):
            run_sql(schema, "DELETE FROM acq_plc_facts_history WHERE sample_id='old-g1-2'")

        extra_versions = tmp_path_factory.mktemp('acq007_unrelated_revision')
        (extra_versions / 'unrelated_fixture.py').write_text(f'''
from alembic import op
revision = {UNRELATED_FIXTURE_REVISION!r}
down_revision = {TABLE_NAMES_REVISION!r}

def upgrade():
    op.execute("CREATE TABLE unrelated_fixture (id INTEGER PRIMARY KEY) ENGINE=InnoDB")

def downgrade():
    op.drop_table("unrelated_fixture")
''')
        unrelated = migrate(schema, UNRELATED_FIXTURE_REVISION, extra_versions=extra_versions)
        assert unrelated.returncode == 0, unrelated.stderr
        assert run_sql(schema, 'SELECT version_num FROM alembic_version') == ((UNRELATED_FIXTURE_REVISION,),)
        yield schema, now
    finally:
        run_sql(None, f'DROP DATABASE `{schema}`')


@pytest.fixture
def runtime_credentials(isolated):
    schema, _ = isolated
    username, password = 'arch_acq007_' + uuid4().hex[:12], token_urlsafe(32)
    account = (username, '%')
    run_sql(None, 'CREATE USER %s@%s IDENTIFIED BY %s', (*account, password))
    try:
        run_sql(None, f'GRANT SELECT, INSERT, UPDATE, DELETE ON `{schema}`.* TO %s@%s', account)
        yield username, password
    finally:
        run_sql(None, 'DROP USER %s@%s', account)


@pytest_asyncio.fixture
async def runtime(isolated, runtime_credentials, monkeypatch, tmp_path):
    schema, now = isolated
    username, password = runtime_credentials
    engine = create_async_engine(URL.create('mysql+aiomysql', username=username, password=password,
                                            host='127.0.0.1', port=int(PORT), database=schema), pool_size=12)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    commit_fault = ContextVar('fault', default=None)

    async def session():
        db = factory()
        fault = commit_fault.get()
        if fault:
            original = db.commit

            async def commit():
                if fault == 'before':
                    raise ConnectionError('synthetic loss before commit')
                await original()
                raise ConnectionError('synthetic loss after commit')

            db.commit = commit
        return db

    profile = {'target': {'schemaRevision': CONSUMPTION_REVISION, 'schema': schema,
                          'serverUuid': SERVER, 'alias': 'isolated-acq007'}}
    profile_path = tmp_path / 'old-facts-profile.json'
    profile_bytes = bytes_body(profile)
    profile_path.write_bytes(profile_bytes)
    profile_settings = SimpleNamespace(PLC_FACTS_V2_PROFILE_FILE=profile_path)
    for module in (consumption, source_registry, v2):
        monkeypatch.setattr(module, 'get_profile', lambda: load_profile(profile_settings))
        monkeypatch.setattr(module, 'get_db_session', session)
    monkeypatch.setattr(observation_evidence, 'get_profile', lambda: load_profile(profile_settings))
    app = create_app(testing=True)
    app.dependency_overrides[source_registry.get_current_active_admin] = lambda: SimpleNamespace(id=1)
    credentials = tmp_path / 'consumer-credential-digests.json'
    credentials.touch(mode=0o600)
    monkeypatch.setenv('ACQ_CONSUMPTION_CREDENTIALS_FILE', str(credentials))
    entries = []

    def grant(identity, plc, db=21, permissions=None, token=None):
        token = token or token_urlsafe(36)
        entries.append({'sha256': sha256(token.encode()).hexdigest(), 'consumerId': identity,
                        'plcId': plc, 'dbNumber': db, 'permissions': permissions or PUBLIC_PERMISSIONS})
        credentials.write_text(json.dumps({'grants': entries}), encoding='utf-8')
        get_grants.cache_clear()
        return {'Authorization': 'Bearer ' + token}

    def target(plc):
        name = 'target-' + uuid4().hex[:10]
        add_source(schema, name, 'external')
        return {'plcId': plc, 'dbNumber': 21, 'startMode': 'retained',
                'target': {'kind': 'plc-facts-v2', 'plcId': name, 'dbNumber': 21,
                           'instanceId': 'instance-' + name, 'sourceGeneration': 'g1'}}

    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://isolated.test') as http:
            yield http, schema, now, grant, target, commit_fault
    finally:
        get_grants.cache_clear()
        await engine.dispose()
        assert profile_path.read_bytes() == profile_bytes


def response(result, code=200, error=None):
    assert result.status_code == code, result.text
    document = result.json()
    assert document['code'] == code
    if error:
        assert document['errorCode'] == error
    return document['data']


async def push(http, document, headers=None, raw=None):
    return await http.post(SAMPLES, content=raw or bytes_body(document),
                           headers={'Content-Type': 'application/json', **(headers or {})})


async def start(http, path, headers, worker='worker-a'):
    response(await http.put(path + '/run-state', headers=headers,
                            json={'operationId': str(uuid4()), 'desiredState': 'running'}))
    lease = response(await http.post(path + '/lease', headers=headers,
                                     json={'operationId': str(uuid4()), 'workerId': worker, 'action': 'acquire'}))
    return {**headers, 'X-Consumer-Lease-Id': lease['leaseId'],
            'X-Consumer-Lease-Generation': lease['leaseGeneration']}


@pytest.mark.asyncio
async def test_stale_profile_source_management_and_observation_evidence(runtime):
    http, schema, now, *_ = runtime
    route = '/api/v1/admin/acquisition-sources'
    plc, instance, generation = 'tasks-evidence', 'instance-tasks-evidence', 'g1'
    registered = {'plcId': plc, 'instanceId': instance, 'sourceGeneration': generation, 'sourceType': 'external'}
    created = response(await http.post(route, json=registered))
    assert created['outcome'] == 'created'
    records = response(await http.get(route))
    assert created['source'] in records['items']
    body = sample(plc, 1, now)
    body['points'] = [{'pointId': 'task', 'dataType': 'STRING[16]', 'value': 'ORDER-001',
                       'quality': 'good', 'observedAt': wire_time(now)}]
    assert response(await push(http, body))['outcome'] == 'created'
    assert response(await push(http, body))['outcome'] == 'duplicate'
    binding = {'plcId': plc, 'dbNumber': 21, 'taskPointId': 'task', 'idleValue': '',
               'maxTaskAgeSeconds': 600}
    async with await v2.get_db_session() as db:
        target = {'schema': schema, 'serverUuid': SERVER, 'schemaRevision': TABLE_NAMES_PREDECESSOR}
        with pytest.raises(observation_guard.EvidenceUnavailable):
            await observation_guard.probe_target(db, target)
        await db.rollback()
        assert await observation_evidence.current_task(db, binding) == {
            'state': 'active', 'taskNo': 'ORDER-001', 'observedAt': wire_time(now),
        }
        evidence = await observation_evidence.confirm_task(db, binding, 'ORDER-001', now, [], 'external')
        assert evidence['sampleId'] == body['sampleId'] and evidence['sourceGeneration'] == generation
        config = Config(str(ROOT / 'alembic.ini'))
        config.set_main_option('script_location', str(ROOT / 'alembic'))
        migration = ScriptDirectory.from_config(config).get_revision(TABLE_NAMES_REVISION).module
        with pytest.raises(RuntimeError, match='inaccessible acquisition history trigger set'):
            connection = await db.connection()
            await connection.run_sync(migration._require_triggers, 'acq_plc_facts_history')
    expected = {key: created['source'][key] for key in ('instanceId', 'sourceGeneration', 'registrationRevision')}
    removed = response(await http.patch(route, json={'plcId': plc, 'action': 'delete', 'expected': expected, 'confirmDelete': True}))
    assert removed['outcome'] == 'deleted'


@pytest.mark.asyncio
@pytest.mark.parametrize('break_layout, restore_layout', (
    ('RENAME TABLE acq_consumer_operations TO acq_consumer_operations_fixture',
     'RENAME TABLE acq_consumer_operations_fixture TO acq_consumer_operations'),
    ('ALTER TABLE acq_consumer_operations RENAME COLUMN result TO fixture_result',
     'ALTER TABLE acq_consumer_operations RENAME COLUMN fixture_result TO result'),
    ('ALTER TABLE acq_consumption_streams MODIFY last_seq BIGINT UNSIGNED NOT NULL',
     'ALTER TABLE acq_consumption_streams MODIFY last_seq BIGINT NOT NULL'),
    ('ALTER TABLE acq_consumption_events DROP INDEX uq_acq_consumption_history',
     'ALTER TABLE acq_consumption_events ADD CONSTRAINT uq_acq_consumption_history UNIQUE (history_id)'),
    ('UPDATE acq_consumption_activation SET ready=0 WHERE id=1',
     'UPDATE acq_consumption_activation SET ready=1 WHERE id=1'),
    ('DELETE FROM acq_consumption_activation WHERE id=1',
     'INSERT INTO acq_consumption_activation (id, cutoff_at, ready) VALUES (1, %s, 1)'),
), ids=('table', 'column', 'type', 'unique', 'inactive', 'missing-ready'))
async def test_incompatible_layout_declines_read_and_write(runtime, break_layout, restore_layout):
    http, schema, now, *_ = runtime
    plc = 'layout-' + uuid4().hex[:12]
    add_source(schema, plc)
    cutoff = run_sql(schema, 'SELECT cutoff_at FROM acq_consumption_activation WHERE id=1')[0][0]
    run_sql(schema, break_layout)
    try:
        response(await http.get('/api/v1/acquisition-data/latest', params={'plcId': plc, 'dbNumber': 21}),
                 503, 'plc_facts_v2.not_ready')
        response(await push(http, sample(plc, 1, now)), 503, 'plc_facts_v2.not_ready')
        for table in ('acq_plc_facts_history', 'acq_plc_facts_latest', 'acq_consumption_events',
                      'acq_consumption_streams'):
            assert not run_sql(schema, f'SELECT plc_id FROM {table} WHERE plc_id=%s', (plc,))
    finally:
        run_sql(schema, restore_layout, (cutoff,) if '%s' in restore_layout else None)


@pytest.mark.asyncio
async def test_exact_maintenance_revision_identity_and_live_clock(runtime, runtime_credentials, tmp_path):
    _, schema, _, *_ = runtime
    valid = {'schema': schema, 'serverUuid': SERVER, 'schemaRevision': UNRELATED_FIXTURE_REVISION}
    async with await v2.get_db_session() as db:
        for bad in ({'schema': 'other-schema'}, {'serverUuid': str(uuid4())}):
            with pytest.raises(V2Error, match='not_ready'):
                await async_v2.target_now(db, {**valid, **bad})
            await db.rollback()
        await db.execute(text("SET time_zone = '+00:00'"))
        try:
            with pytest.raises(V2Error, match='not_ready'):
                await async_v2.target_now(db, valid)
        finally:
            await db.execute(text("SET time_zone = '+08:00'"))
        await async_v2.target_now(db, valid)
    engine = create_engine(URL.create('mysql+pymysql', username='root', password=PASSWORD,
                                      host='127.0.0.1', port=int(PORT), database=schema))
    try:
        for bad in ({'schemaRevision': CONSUMPTION_REVISION}, {'serverUuid': str(uuid4())}, {'schema': 'other-schema'}):
            with Session(engine) as db, pytest.raises(V2Error, match='not_ready'):
                sync_v2_maintenance.run(db, {**valid, **bad}, apply=False)
        with Session(engine) as db:
            assert sync_v2_maintenance.run(db, valid, apply=False)['rows'] >= 0
    finally:
        engine.dispose()

    username, password = runtime_credentials
    env = dict(os.environ, MYSQL_USER=username, MYSQL_PASSWORD=password, TEST_MYSQL_DATABASE=schema,
               PLC_FACTS_V2_PROFILE_FILE=str(tmp_path / 'old-facts-profile.json'))
    command = [sys.executable, 'scripts/plc_facts_maintenance/main.py', 'cleanup-v2', '--plan',
               '--target-alias', 'isolated-acq007', '--schema', schema, '--expected-server-uuid', SERVER,
               '--operation-approval', 'isolated-fixture', '--confirmed-by', 'test-executor',
               '--expected-schema-revision']
    actual = subprocess.run([*command, UNRELATED_FIXTURE_REVISION], cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=10)
    assert actual.returncode == 0 and '"event":"dry-run"' in actual.stdout
    stale = subprocess.run([*command, CONSUMPTION_REVISION], cwd=ROOT, env=env,
                           capture_output=True, text=True, timeout=10)
    assert stale.returncode == 1 and '"errorCode":"plc_facts.maintenance_failed"' in stale.stdout


@pytest.mark.asyncio
async def test_locked_stream_rollback_duplicate_and_generation(runtime, monkeypatch):
    http, schema, now, grant, make_target, _ = runtime
    add_source(schema, 'lock-a')
    add_source(schema, 'lock-b')
    entered = asyncio.Event()
    resume = asyncio.Event()
    original = async_v2.advance_latest

    async def delay(db, data, observed, expires):
        await original(db, data, observed, expires)
        if data.plc_id == 'lock-a' and data.source_seq == '1':
            entered.set()
            await asyncio.wait_for(resume.wait(), timeout=8)
        if data.plc_id == 'lock-a' and data.source_seq == '3':
            raise RuntimeError('synthetic rollback after append')

    monkeypatch.setattr(async_v2, 'advance_latest', delay)
    first = asyncio.create_task(push(http, sample('lock-a', 1, now)))
    await asyncio.wait_for(entered.wait(), timeout=5)
    second = asyncio.create_task(push(http, sample('lock-a', 2, now - timedelta(days=1))))
    other = await asyncio.wait_for(push(http, sample('lock-b', 1, now)), timeout=5)
    assert response(other)['outcome'] == 'created'
    assert not second.done()
    resume.set()
    assert response(await first)['outcome'] == 'created'
    assert response(await second)['outcome'] == 'created'
    assert response(await push(http, sample('lock-a', 2, now - timedelta(days=1))))['outcome'] == 'duplicate'
    response(await push(http, sample('lock-a', 3, now)), 503, 'plc_facts_v2.not_ready')
    assert response(await push(http, sample('lock-a', 4, now)))['outcome'] == 'created'
    source = run_sql(schema, """
        SELECT event_seq, sample_id, history_id FROM acq_consumption_events
        WHERE plc_id='lock-a' ORDER BY event_seq
    """)
    assert tuple(row[:2] for row in source) == ((1, b'lock-a-g1-1'), (2, b'lock-a-g1-2'), (3, b'lock-a-g1-4'))
    assert source[0][2] < run_sql(schema, "SELECT history_id FROM acq_consumption_events WHERE plc_id='lock-b'")[0][0]
    identity = str(uuid4())
    headers, path = grant(identity, 'lock-a'), API + '/' + identity
    response(await http.put(path, headers=headers, json=make_target('lock-a')))
    leased = await start(http, path, headers)
    run_sql(schema, "DELETE FROM acq_plc_source_registry WHERE plc_id='lock-a'")
    assert response(await http.get(path + '/next', headers=leased))['sample']['sourceGeneration'] == 'g1'
    response(await push(http, sample('lock-a', 5, now)), 403, 'plc_facts_v2.scope_rejected')
    add_source(schema, 'lock-a', generation='g2')
    assert response(await push(http, sample('lock-a', 1, now, generation='g2')))['outcome'] == 'created'
    assert run_sql(schema, """
        SELECT event_seq, source_generation FROM acq_consumption_events WHERE plc_id='lock-a' ORDER BY event_seq
    """) == ((1, b'g1'), (2, b'g1'), (3, b'g1'), (4, b'g2'))


@pytest.mark.asyncio
async def test_event_mismatch_and_missing_append_never_commit_a_fact(runtime):
    http, schema, now, *_ = runtime
    add_source(schema, 'event-guard')
    first, second = (sample('event-guard', seq, now) for seq in (1, 2))
    assert response(await push(http, first))['outcome'] == 'created'

    def state():
        return [run_sql(schema, f"SELECT * FROM {table} WHERE plc_id='event-guard'")
                for table in ('acq_plc_facts_history', 'acq_plc_facts_latest', 'acq_consumption_streams')]

    before = state()
    (event,) = run_sql(schema, "SELECT * FROM acq_consumption_events WHERE plc_id='event-guard'")
    run_sql(schema, "DELETE FROM acq_consumption_events WHERE plc_id='event-guard'")
    try:
        response(await push(http, first), 503, 'plc_facts_v2.not_ready')
        assert state() == before
    finally:
        run_sql(schema, "INSERT INTO acq_consumption_events VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", event)
    run_sql(schema, "UPDATE acq_consumption_events SET sample_id='wrong' WHERE plc_id='event-guard'")
    try:
        response(await push(http, first), 503, 'plc_facts_v2.not_ready')
        assert state() == before
    finally:
        run_sql(schema, "UPDATE acq_consumption_events SET sample_id=%s WHERE plc_id='event-guard'",
                (first['sampleId'],))

    original = run_sql(schema, 'SHOW CREATE TRIGGER acq006_history_append')[0][2]
    run_sql(schema, 'DROP TRIGGER acq006_history_append')
    try:
        response(await push(http, second), 503, 'plc_facts_v2.not_ready')
        assert state() == before
        assert run_sql(schema, "SELECT event_seq FROM acq_consumption_events WHERE plc_id='event-guard'") == ((1,),)
    finally:
        run_sql(schema, original)
    assert response(await push(http, second))['outcome'] == 'created'
    assert response(await push(http, second))['outcome'] == 'duplicate'


@pytest.mark.asyncio
async def test_origin_retained_now_and_midstream_gap(runtime, monkeypatch):
    http, schema, now, grant, make_target, _ = runtime
    actual_clock = async_consumption.crud.clock
    clock_override = ContextVar('read_clock_override', default=None)

    async def clock(db):
        return clock_override.get() or await actual_clock(db)

    monkeypatch.setattr(async_consumption.crud, 'clock', clock)
    for plc, sample_time in [('initial-gap', now - timedelta(days=2)), ('live-gap', now - timedelta(days=2))]:
        add_source(schema, plc)
        for seq, observed in [(1, now), (2, sample_time), (3, now)]:
            assert response(await push(http, sample(plc, seq, observed)))['outcome'] == 'created'
    mid = run_sql(schema, """
        SELECT expires_at FROM acq_consumption_events WHERE plc_id='initial-gap' AND event_seq=2
    """)[0][0] + timedelta(seconds=1)

    async def make(plc, mode, queued=False):
        identity = str(uuid4())
        headers, path = grant(identity, plc), API + '/' + identity
        create = make_target(plc)
        create['startMode'] = mode
        if queued:
            clock_override.set(mid)
        result = response(await http.put(path, headers=headers, json=create))
        assert response(await http.put(path, headers=headers, json=create)) == result
        clock_override.set(None)
        return path, headers, result

    path, headers, retained = await make('initial-gap', 'retained', queued=True)
    assert retained['excludedHistory'] == {'count': '1', 'firstEventSeq': '2', 'lastEventSeq': '2'}
    leased = await start(http, path, headers)
    assert response(await http.get(path + '/next', headers=leased))['eventSeq'] == '1'
    now_path, now_headers, only_new = await make('live-gap', 'now')
    assert only_new['startSeq'] == only_new['lastConfirmedSeq'] == '3'
    leased_now = await start(http, now_path, now_headers)
    assert response(await http.get(now_path + '/next', headers=leased_now)) == {'status': 'empty'}
    live_path, living, _ = await make('live-gap', 'retained')
    live_headers = living
    living = await start(http, live_path, live_headers)
    assert response(await http.get(live_path + '/next', headers=living))['eventSeq'] == '1'

    # Advance one task to the middle using the real pending/ACK routes.
    await deliver(http, live_path, living)
    await deliver(http, path, leased)
    assert response(await push(http, sample('live-gap', 4, now)))['outcome'] == 'created'
    assert response(await http.get(now_path + '/next', headers=leased_now))['eventSeq'] == '4'
    clock_override.set(mid)
    leased = await start(http, path, headers, worker='future-reader')
    living = await start(http, live_path, live_headers, worker='future-reader')
    assert response(await http.get(path + '/next', headers=leased))['eventSeq'] == '3'
    failure = response(await http.get(live_path + '/next', headers=living), 410, 'acquisition_consumer.gap')
    assert failure == {'eventSeq': '2', 'lastConfirmedSeq': '1'}
    clock_override.set(None)
    history_id = run_sql(schema, "SELECT history_id FROM acq_consumption_events WHERE plc_id='live-gap' AND event_seq=2")[0][0]
    maintenance = create_engine(URL.create('mysql+pymysql', username='root', password=PASSWORD,
                                           host='127.0.0.1', port=int(PORT), database=schema))
    try:
        with Session(maintenance) as session:
            session.execute(text('SET timestamp = UNIX_TIMESTAMP(:mid)'), {'mid': mid})
            result = sync_v2_maintenance.run(session, {
                'serverUuid': SERVER, 'schema': schema, 'schemaRevision': UNRELATED_FIXTURE_REVISION,
            }, apply=True)
        assert result['rows'] > 0
    finally:
        maintenance.dispose()
    assert not run_sql(schema, 'SELECT id FROM acq_plc_facts_history WHERE id=%s', (history_id,))
    assert run_sql(schema, 'SELECT history_id FROM acq_consumption_events WHERE history_id=%s', (history_id,)) == ((history_id,),)
    assert response(await http.get(live_path, headers=living))['status'] == 'blocked'
    response(await http.get(live_path + '/next', headers=living), 410, 'acquisition_consumer.gap')


def delivery_inputs(ready):
    target = ready['target']
    sample_body = {**{key: value for key, value in target.items() if key != 'kind'},
                   'contractVersion': 'plc-facts/v2', 'points': ready['sample']['points']}
    raw = bytes_body(sample_body)
    pending = {'eventSeq': ready['eventSeq'], 'configVersion': 'fixture-version',
               'configHash': sha256(b'fixture-config').hexdigest(), 'serializerVersion': 'json-v1',
               'bodySha256': sha256(raw).hexdigest(), 'target': target}
    return sample_body, raw, pending


def save_fixture_config(store, version, rename_to, *, create=False):
    with closing(sqlite_connect(store)) as config_db, config_db:
        if create:
            config_db.execute('CREATE TABLE configuration (version TEXT PRIMARY KEY, serializer TEXT, document BLOB)')
        config_db.execute('INSERT INTO configuration VALUES (?, ?, ?)',
                          (version, 'json-v1', bytes_body({'renamePoints': {'zero': rename_to}})))


def rebuild_from_config(store, ready, version, expected=None):
    """运行模拟器从新 SQLite 连接读取固定版本，不保留先前 GET 或 POST 正文。"""
    with closing(sqlite_connect(store)) as config_db:
        row = config_db.execute('SELECT serializer, document FROM configuration WHERE version=?', (version,)).fetchone()
    if row is None:
        raise ValueError('immutable configuration version missing')
    serializer, configuration = row
    if serializer != 'json-v1':
        raise ValueError('unsupported frozen serializer')
    rules = json.loads(configuration)['renamePoints']
    sample_body, _, pending = delivery_inputs(ready)
    sample_body['points'] = [
        {**point, 'pointId': rules.get(point['pointId'], point['pointId'])} for point in sample_body['points']
    ]
    raw = bytes_body(sample_body)
    pending.update(configVersion=version, configHash=sha256(configuration).hexdigest(),
                   serializerVersion=serializer, bodySha256=sha256(raw).hexdigest())
    if expected is not None and any(pending[key] != expected[key] for key in pending):
        raise ValueError('reconstructed configuration or body differs')
    return sample_body, raw, pending


def target_headers(path, leased, delivery_id):
    return {**leased, 'X-Consumer-Id': path.rsplit('/', 1)[-1], 'X-Delivery-Id': delivery_id}


def ack_payload(result):
    return {**result['data'], 'operationId': str(uuid4()), 'httpStatus': 200, 'code': 200}


async def deliver(http, path, leased):
    ready = response(await http.get(path + '/next', headers=leased))
    delivery = ready['deliveryId']
    sample_body, raw, pending = delivery_inputs(ready)
    pending_path = f'{path}/pending/{delivery}'
    response(await http.put(pending_path, headers=leased, json=pending))
    written = await push(http, sample_body, target_headers(path, leased, delivery), raw)
    response(written)
    response(await http.post(pending_path + '/ack', headers=leased, json=ack_payload(written.json())))
    return ready


@pytest.mark.asyncio
async def test_lease_lost_commit_replay_restart_and_compatibility(runtime, tmp_path):
    http, schema, now, grant, make_target, fault = runtime
    add_source(schema, 'recover')
    add_source(schema, 'recover-other')
    response(await push(http, sample('recover', 1, now)))
    identity, other = str(uuid4()), str(uuid4())
    path = API + '/' + identity
    headers = grant(identity, 'recover')
    wrong_scope = grant(identity, 'recover-other')
    create = make_target('recover')
    response(await http.put(path, json=create), 401, 'acquisition_consumer.authentication_required')
    response(await http.put(path, headers=wrong_scope, json=create), 403, 'acquisition_consumer.scope_rejected')
    response(await http.get(API + '/' + other, headers=headers), 403, 'acquisition_consumer.scope_rejected')
    response(await http.get(path, headers={'Authorization': 'Bearer ' + 'x' * 40}), 401,
             'acquisition_consumer.authentication_required')
    fault.set('after')
    response(await http.put(path, headers=headers, json=create), 503, 'acquisition_consumer.commit_outcome_unknown')
    fault.set(None)
    response(await http.put(path, headers=headers, json=create))
    change = {'operationId': str(uuid4()), 'desiredState': 'running'}
    fault.set('before')
    response(await http.put(path + '/run-state', headers=headers, json=change), 503,
             'acquisition_consumer.commit_outcome_unknown')
    fault.set(None)
    assert response(await http.get(path, headers=headers))['desiredState'] == 'paused'
    response(await http.get(path, headers=wrong_scope), 403, 'acquisition_consumer.scope_rejected')
    response(await http.put(path + '/run-state', headers=headers, json=change))
    response(await http.put(path + '/run-state', headers=headers, json={**change, 'desiredState': 'paused'}), 409,
             'acquisition_consumer.operation_conflict')
    tries = [{'operationId': str(uuid4()), 'workerId': f'worker-{index}', 'action': 'acquire'} for index in range(2)]
    results = await asyncio.gather(*(http.post(path + '/lease', headers=headers, json=operation) for operation in tries))
    assert sorted(result.status_code for result in results) == [200, 409]
    winner = next(index for index, result in enumerate(results) if result.status_code == 200)
    lease = response(results[winner])
    assert response(await http.post(path + '/lease', headers=headers, json=tries[winner])) == lease
    old = {**headers, 'X-Consumer-Lease-Id': lease['leaseId'], 'X-Consumer-Lease-Generation': lease['leaseGeneration']}
    ready = response(await http.get(path + '/next', headers=old))
    delivery, sequence = ready['deliveryId'], ready['eventSeq']
    config_path = tmp_path / 'simulated-sma-config.sqlite'
    save_fixture_config(config_path, 'version-one', 'zero-mapped', create=True)
    save_fixture_config(config_path, 'version-two', 'new-config-point')
    sample_body, raw, pending = rebuild_from_config(config_path, ready, 'version-one')
    pending_path = f'{path}/pending/{delivery}'
    fault.set('after')
    response(await http.put(pending_path, headers=old, json=pending), 503,
             'acquisition_consumer.commit_outcome_unknown')
    fault.set(None)
    actual_pending = response(await http.put(pending_path, headers=old, json=pending))
    assert actual_pending['bodySha256'] == sha256(raw).hexdigest()
    response(await push(http, sample_body), 401, 'acquisition_consumer.authentication_required')
    response(await push(http, sample_body, target_headers(path, old, delivery), raw + b' '), 409,
             'acquisition_consumer.pending_conflict')
    fault.set('after')
    response(await push(http, sample_body, target_headers(path, old, delivery), raw), 503,
             'plc_facts_v2.commit_outcome_unknown')
    fault.set(None)

    # Simulate worker restart and expiration without waiting 30 seconds.
    run_sql(schema, "UPDATE acq_consumers SET lease_expires_at='2000-01-01' WHERE consumer_id=%s", (identity,))
    recovered = await start(http, path, headers, worker='replacement')
    response(await http.get(path + '/next', headers=old), 409, 'acquisition_consumer.lease_stale')
    response(await push(http, sample_body, target_headers(path, old, delivery), raw), 409,
             'acquisition_consumer.lease_stale')
    rebuilt = response(await http.get(path + '/next', headers=recovered))
    assert rebuilt['deliveryId'] == delivery
    frozen_state = response(await http.get(path, headers=headers))
    frozen = frozen_state['pending']
    assert frozen['deliveryId'] == delivery and frozen['configVersion'] == 'version-one'
    assert rebuild_from_config(config_path, rebuilt, frozen['configVersion'], frozen)[1] == raw
    with pytest.raises(ValueError, match='configuration or body differs'):
        rebuild_from_config(config_path, rebuilt, 'version-two', frozen)
    with closing(sqlite_connect(config_path)) as config_db, config_db:
        assert b'recover-g1-1' not in config_db.serialize()
        config_db.execute('DELETE FROM configuration WHERE version=?', (frozen['configVersion'],))
    with pytest.raises(ValueError, match='configuration version missing'):
        rebuild_from_config(config_path, rebuilt, frozen['configVersion'], frozen)
    assert response(await http.get(path, headers=headers)) == frozen_state
    target_plc = create['target']['plcId']
    assert run_sql(schema, 'SELECT sample_id FROM acq_plc_facts_history WHERE plc_id=%s', (target_plc,)) == (
        (delivery.encode(),),
    )
    save_fixture_config(config_path, 'version-one', 'zero-mapped')
    replay_sample, replay_raw, _ = rebuild_from_config(config_path, rebuilt, frozen['configVersion'], frozen)
    posted = await push(http, replay_sample, target_headers(path, recovered, delivery), replay_raw)
    assert response(posted)['outcome'] == 'duplicate'
    good = ack_payload(posted.json())
    for changed, status in (
        ({'instanceId': 'wrong'}, 409), ({'sampleId': str(uuid4())}, 409),
        ({'httpStatus': 500}, 422), ({'code': 500}, 422), ({'contractVersion': 'plc-facts/v1'}, 422),
        ({'status': 'pending'}, 422), ({'outcome': 'ignored'}, 422),
    ):
        response(await http.post(pending_path + '/ack', headers=recovered, json={**good, **changed}), status,
                 'acquisition_consumer.receipt_mismatch' if status == 409 else 'acquisition_consumer.invalid_request')
        after_bad_ack = response(await http.get(path, headers=headers))
        assert after_bad_ack['lastConfirmedSeq'] == '0' and after_bad_ack['pending'] == frozen
        assert run_sql(schema, 'SELECT sample_id FROM acq_plc_facts_history WHERE plc_id=%s', (target_plc,)) == (
            (delivery.encode(),),
        )
    fault.set('after')
    response(await http.post(pending_path + '/ack', headers=recovered, json=good), 503,
             'acquisition_consumer.commit_outcome_unknown')
    fault.set(None)
    checked = response(await http.get(path, headers=headers))
    assert checked['lastConfirmedSeq'] == sequence and checked['pending'] is None
    assert response(await http.post(pending_path + '/ack', headers=old, json=good))['lastConfirmedSeq'] == sequence
    assert response(await http.get(path + '/next', headers=recovered)) == {'status': 'empty'}
    target = create['target']['plcId']
    facts = response(await http.get('/api/v1/acquisition-data/history', params={
        'plcId': target, 'dbNumber': 21, 'from': wire_time(now - timedelta(days=1)), 'to': wire_time(now + timedelta(days=1)),
    }))
    assert len(facts['items']) == 1 and facts['items'][0]['sampleId'] == delivery
    actual = response(await http.get('/api/v1/acquisition-data/history/' + facts['items'][0]['id']))
    assert actual['points'][0]['value'] == 0
    assert actual['points'][0]['pointId'] == 'zero-mapped'
    for endpoint, query in [('options', {}), ('latest', {'plcId': 'recover', 'dbNumber': 21}),
                            ('latest/browse', {'plcId': 'recover'})]:
        response(await http.get('/api/v1/acquisition-data/' + endpoint, params=query))
    assert response(await push(http, sample('recover-other', 1, now)))['outcome'] == 'created'
    assert run_sql(schema, "SELECT COUNT(*) FROM acq_consumer_deliveries WHERE consumer_id=%s", (identity,)) == ((1,),)
    assert not run_sql(schema, """
        SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME IN ('acq_consumption_events', 'acq_consumer_deliveries')
        AND COLUMN_NAME IN ('points_json', 'request_body', 'response_body')
    """)


@pytest.mark.asyncio
async def test_pause_and_target_rollover_preserve_pending(runtime):
    http, schema, now, grant, make_target, fault = runtime
    source = 'pending-blocked'
    add_source(schema, source)
    response(await push(http, sample(source, 1, now)))
    identity = str(uuid4())
    path, headers = API + '/' + identity, grant(identity, source)
    create = make_target(source)
    response(await http.put(path, headers=headers, json=create))
    leased = await start(http, path, headers)
    ready = response(await http.get(path + '/next', headers=leased))
    delivery = ready['deliveryId']
    sample_body, raw, pending = delivery_inputs(ready)
    pending_path = f'{path}/pending/{delivery}'
    response(await http.put(pending_path, headers=leased, json=pending))

    renewal = {'operationId': str(uuid4()), 'workerId': 'worker-a', 'action': 'renew'}
    fault.set('after')
    response(await http.post(path + '/lease', headers=leased, json=renewal), 503,
             'acquisition_consumer.commit_outcome_unknown')
    fault.set(None)
    resumed = response(await http.post(path + '/lease', headers=leased, json=renewal))
    assert resumed['leaseId'] == leased['X-Consumer-Lease-Id']
    assert response(await http.post(path + '/lease', headers=leased, json=renewal)) == resumed

    pause = {'operationId': str(uuid4()), 'desiredState': 'paused'}
    response(await http.put(path + '/run-state', headers=headers, json=pause))
    response(await http.get(path + '/next', headers=leased), 409, 'acquisition_consumer.paused')
    response(await push(http, sample_body, target_headers(path, leased, delivery), raw), 409,
             'acquisition_consumer.paused')
    assert response(await http.get(path, headers=headers))['pending']['deliveryId'] == delivery
    response(await http.put(path + '/run-state', headers=headers,
                            json={'operationId': str(uuid4()), 'desiredState': 'running'}))
    response(await http.put(pending_path, headers=leased, json={**pending, 'configVersion': 'edited'}), 409,
             'acquisition_consumer.pending_conflict')
    run_sql(schema, "UPDATE acq_plc_source_registry SET source_generation='g2' WHERE plc_id=%s", (create['target']['plcId'],))
    response(await push(http, sample_body, target_headers(path, leased, delivery), raw), 403,
             'plc_facts_v2.scope_rejected')
    blocked = response(await http.get(path, headers=headers))
    assert blocked['pending']['deliveryId'] == delivery and blocked['lastConfirmedSeq'] == '0'
    assert blocked['status'] == 'blocked'


@pytest.mark.asyncio
@pytest.mark.parametrize('mode', ['now', 'retained'])
@pytest.mark.parametrize('first_lock', ['ingest', 'create'])
async def test_create_and_ingest_freeze_exact_stream_prefix(runtime, monkeypatch, mode, first_lock):
    http, schema, now, grant, make_target, _ = runtime
    plc = f'cutoff-{mode}-{first_lock}'
    add_source(schema, plc)
    response(await push(http, sample(plc, 1, now)))
    identity = str(uuid4())
    path, headers = API + '/' + identity, grant(identity, plc)
    create = {**make_target(plc), 'startMode': mode}
    current = ContextVar('source_lock_request')
    held, other_attempt, resume = asyncio.Event(), asyncio.Event(), asyncio.Event()
    original = async_consumption.crud.lock_stream

    async def lock(db, source, number):
        name = current.get()
        if (source, number) != (plc.encode(), 21):
            return await original(db, source, number)
        if name != first_lock:
            other_attempt.set()
        stream = await original(db, source, number)
        if name == first_lock:
            held.set()
            await asyncio.wait_for(resume.wait(), timeout=8)
        return stream

    async def create_consumer():
        current.set('create')
        return await http.put(path, headers=headers, json=create)

    async def ingest():
        current.set('ingest')
        return await push(http, sample(plc, 2, now - timedelta(days=1)))

    with monkeypatch.context() as patch:
        patch.setattr(async_consumption.crud, 'lock_stream', lock)
        actions = {'create': create_consumer, 'ingest': ingest}
        other_name = 'create' if first_lock == 'ingest' else 'ingest'
        first = asyncio.create_task(actions[first_lock]())
        other = None
        try:
            await asyncio.wait_for(held.wait(), timeout=4)
            other = asyncio.create_task(actions[other_name]())
            await asyncio.wait_for(other_attempt.wait(), timeout=4)
            completed, _ = await asyncio.wait({other}, timeout=0.10)
            assert not completed, 'the competing transaction passed the held source stream lock'
        finally:
            resume.set()
            await asyncio.gather(*[task for task in (first, other) if task is not None])
    results = {first_lock: first.result(), other_name: other.result()}
    created = response(results['create'])
    assert response(results['ingest'])['outcome'] == 'created'
    watermark = 2 if first_lock == 'ingest' else 1
    assert created['startSeq'] == str(watermark)
    assert created['lastConfirmedSeq'] == (str(watermark) if mode == 'now' else '0')
    assert response(await http.put(path, headers=headers, json=create)) == created
    response(await push(http, sample(plc, 3, now)))
    lease = await start(http, path, headers)
    expected = list(range(1 if mode == 'retained' else watermark + 1, 4))
    observed = [int((await deliver(http, path, lease))['eventSeq']) for _ in expected]
    assert observed == expected
    assert response(await http.get(path + '/next', headers=lease)) == {'status': 'empty'}
    assert response(await http.get(path, headers=lease))['lastConfirmedSeq'] == '3'


@pytest.mark.asyncio
async def test_all_consumer_mutations_are_recoverable_on_both_sides_of_commit(runtime):
    http, schema, now, grant, make_target, fault = runtime
    plc = 'mutation-matrix'
    add_source(schema, plc)
    response(await push(http, sample(plc, 1, now)))
    identity = str(uuid4())
    path, headers = API + '/' + identity, grant(identity, plc)

    async def snapshot():
        result = await http.get(path, headers=headers)
        if result.status_code == 404:
            return response(result, 404, 'acquisition_consumer.not_found')
        return response(result)

    async def check(method, url, auth, body, changed, conflict):
        assert any(body.get(key) != value for key, value in changed.items())
        before = await snapshot()
        for stage in ('before', 'after'):
            reset = fault.set(stage)
            try:
                response(await http.request(method, url, headers=auth, json=body), 503,
                         'acquisition_consumer.commit_outcome_unknown')
            finally:
                fault.reset(reset)
            after = await snapshot()
            if stage == 'before':
                assert after == before
            else:
                assert after != before
        if method == 'POST' and url.endswith('/ack'):
            assert after['lastConfirmedSeq'] == '1' and after['pending'] is None
        expected = response(await http.request(method, url, headers=auth, json=body))
        assert response(await http.request(method, url, headers=auth, json=body)) == expected
        response(await http.request(method, url, headers=auth, json={**body, **changed}), 409,
                 'acquisition_consumer.' + conflict)
        assert await snapshot() == after
        return expected

    request = make_target(plc)
    await check('PUT', path, headers, request, {'startMode': 'now'}, 'operation_conflict')
    await check('PUT', path + '/run-state', headers, {'operationId': str(uuid4()), 'desiredState': 'running'},
                {'desiredState': 'paused'}, 'operation_conflict')
    lease = await check('POST', path + '/lease', headers, {
        'operationId': str(uuid4()), 'workerId': 'matrix-worker', 'action': 'acquire',
    }, {'workerId': 'wrong'}, 'operation_conflict')
    leased = {**headers, 'X-Consumer-Lease-Id': lease['leaseId'],
              'X-Consumer-Lease-Generation': lease['leaseGeneration']}
    await check('POST', path + '/lease', leased, {
        'operationId': str(uuid4()), 'workerId': 'matrix-worker', 'action': 'renew',
    }, {'workerId': 'wrong'}, 'operation_conflict')

    ready = response(await http.get(path + '/next', headers=leased))
    delivery = ready['deliveryId']
    sample_body, raw, pending = delivery_inputs(ready)
    pending_path = f'{path}/pending/{delivery}'
    await check('PUT', pending_path, leased, pending, {'configVersion': 'wrong'}, 'pending_conflict')
    before_target = await snapshot()
    write_headers = target_headers(path, leased, delivery)
    for stage, target_rows in (('before', 0), ('after', 1)):
        reset = fault.set(stage)
        try:
            response(await push(http, sample_body, write_headers, raw), 503, 'plc_facts_v2.commit_outcome_unknown')
        finally:
            fault.reset(reset)
        assert await snapshot() == before_target
        assert run_sql(schema, 'SELECT COUNT(*) FROM acq_plc_facts_history WHERE plc_id=%s', (sample_body['plcId'],)) == (
            (target_rows,),
        )
    posted = await push(http, sample_body, write_headers, raw)
    assert response(posted)['outcome'] == 'duplicate'
    await check('POST', pending_path + '/ack', leased, ack_payload(posted.json()),
                {'outcome': 'created'}, 'operation_conflict')
    await check('POST', path + '/lease', leased, {
        'operationId': str(uuid4()), 'workerId': 'matrix-worker', 'action': 'release',
    }, {'workerId': 'wrong'}, 'operation_conflict')
    await check('PUT', path + '/run-state', headers, {'operationId': str(uuid4()), 'desiredState': 'paused'},
                {'desiredState': 'running'}, 'operation_conflict')
    final = await snapshot()
    assert final['lastConfirmedSeq'] == '1' and final['pending'] is None and final['lease'] is None
