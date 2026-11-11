"""ARCH-ACQ-002 r2 显式隔离 MySQL 验证；不创建实例、账号或 schema。"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ('ARCH_ACQ002_FIXTURE_ROUND', 'ARCH_ACQ002_FIXTURE_PORT', 'ARCH_ACQ002_FIXTURE_UUID',
            'ARCH_ACQ002_SCHEMA_EMPTY', 'ARCH_ACQ002_SCHEMA_UPGRADE', 'ARCH_ACQ002_SCHEMA_GUARD',
            'ARCH_ACQ002_FIXTURE_ACK', 'MYSQL_USER', 'MYSQL_PASSWORD')
if any(not os.environ.get(key, '').strip() for key in REQUIRED):
    pytest.skip('ACQ002 requires an explicitly identified disposable MySQL fixture', allow_module_level=True)

round_name = os.environ['ARCH_ACQ002_FIXTURE_ROUND']
port = os.environ['ARCH_ACQ002_FIXTURE_PORT']
server_uuid = os.environ['ARCH_ACQ002_FIXTURE_UUID']
schemas = tuple(os.environ[key] for key in ('ARCH_ACQ002_SCHEMA_EMPTY', 'ARCH_ACQ002_SCHEMA_UPGRADE', 'ARCH_ACQ002_SCHEMA_GUARD'))
expected_ack = ':'.join(('ACQ002', round_name, server_uuid, port, *schemas))
if (round_name not in ('dev', 'qa') or not ROOT.is_relative_to(Path('/private/tmp'))
        or not ROOT.name == 'source' or not ROOT.parent.name.startswith('arch-acq002-r2-')
        or (ROOT / 'backend/.env').exists() or Path.cwd().resolve() != (ROOT / 'backend').resolve()
        or not port.isdigit() or not 1024 <= int(port) <= 65535 or port == '3307'
        or os.environ.get('MYSQL_HOST') != '127.0.0.1' or os.environ.get('MYSQL_PORT') != port
        or os.environ.get('MYSQL_USER', '').lower() in ('root', '')
        or os.environ.get('TESTING', '').lower() != 'true'
        or len(set(schemas)) != 3 or any(not re.fullmatch('arch_acq002_' + round_name + r'_[a-z0-9_]+', s) for s in schemas)
        or os.environ.get('MYSQL_DATABASE') in schemas or os.environ['ARCH_ACQ002_FIXTURE_ACK'] != expected_ack):
    raise RuntimeError('ACQ002 disposable fixture guard rejected configuration')

# Resolve project imports to this public candidate before importing any settings or DB module.
for name, relative in (('settings', 'settings.py'), ('database', 'database/__init__.py'), ('app', 'app/__init__.py')):
    found = importlib.util.find_spec(name)
    if found is None or found.origin is None or Path(found.origin).resolve() != (ROOT / 'backend' / relative).resolve():
        raise RuntimeError('ACQ002 project imports must resolve to the isolated candidate')

# Only after the offline identity guards is the SQL client imported.
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool


def engine(schema):
    url = URL.create('mysql+pymysql', username=os.environ['MYSQL_USER'], password=os.environ['MYSQL_PASSWORD'],
                     host='127.0.0.1', port=int(port), database=schema)
    return create_engine(url, poolclass=NullPool, connect_args={'connect_timeout': 3, 'read_timeout': 20, 'write_timeout': 20})


def verify_connection(db, schema):
    version, uuid, actual_schema, current_user = db.execute(text('SELECT VERSION(), @@server_uuid, DATABASE(), CURRENT_USER()')).one()
    if (str(version).split('-')[0] != '8.4.6' or uuid != server_uuid or actual_schema != schema
            or current_user.split('@', 1)[0].lower() == 'root'):
        raise RuntimeError('fixture database identity mismatch')


def migrate(schema, revision, *, extra=None, expect=0):
    environment = dict(os.environ, TEST_MYSQL_DATABASE=schema,
                       ACQ_RETIREMENT_EXPECTED_SCHEMA=schema, ACQ_RETIREMENT_EXPECTED_SERVER_UUID=server_uuid)
    for key in ('ACQ_RETIREMENT_RECOVERY_EVIDENCE_SHA256', 'ACQ_RETIREMENT_RECOVERY_CONFIRMED'):
        environment.pop(key, None)
    environment.update(extra or {})
    result = subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', revision], cwd=ROOT / 'backend',
                            env=environment, capture_output=True, text=True, timeout=90)
    # Preserve return code, never print command environment or database credentials.
    assert (result.returncode == 0) == (expect == 0), f'Alembic exit={result.returncode}, expected={expect}'
    return result


def revision(db):
    return list(db.execute(text('SELECT version_num FROM alembic_version')).scalars())


def state(db):
    return set(inspect(db).get_table_names()) - {'alembic_version'}


def migration_module():
    path = ROOT / 'backend/alembic/versions/20261110_2215_3d5f7a9c1e23_retire_legacy_acquisition.py'
    spec = importlib.util.spec_from_file_location('acq002_isolated_migration', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot(db, names):
    """Capture structure and per-table count/checksum without exporting row values."""
    result = {}
    for name in sorted(names):
        ddl = db.exec_driver_sql(f'SHOW CREATE TABLE `{name}`').one()[1]
        count = db.exec_driver_sql(f'SELECT COUNT(*) FROM `{name}`').scalar_one()
        checksum = db.exec_driver_sql(f'CHECKSUM TABLE `{name}`').one()[1]
        result[name] = (ddl, count, checksum)
    return result


def schema_signature(db, names):
    """逐项比较同一 schema 的表选项、列、索引、约束和引用。"""
    queries = {
        'tables': """SELECT TABLE_NAME, ENGINE, ROW_FORMAT, TABLE_COLLATION, CREATE_OPTIONS
                     FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE()
                     ORDER BY TABLE_NAME""",
        'columns': """SELECT TABLE_NAME, ORDINAL_POSITION, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE,
                            COLUMN_DEFAULT, EXTRA, CHARACTER_SET_NAME, COLLATION_NAME,
                            CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE,
                            DATETIME_PRECISION, COLUMN_COMMENT, GENERATION_EXPRESSION
                     FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()
                     ORDER BY TABLE_NAME, ORDINAL_POSITION""",
        'indexes': """SELECT TABLE_NAME, INDEX_NAME, NON_UNIQUE, SEQ_IN_INDEX, COLUMN_NAME,
                            COLLATION, SUB_PART, NULLABLE, INDEX_TYPE, INDEX_COMMENT, IS_VISIBLE, EXPRESSION
                     FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = DATABASE()
                     ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX""",
        'constraints': """SELECT TABLE_NAME, CONSTRAINT_NAME, CONSTRAINT_TYPE, ENFORCED
                         FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA = DATABASE()
                         ORDER BY TABLE_NAME, CONSTRAINT_NAME""",
        'checks': """SELECT tc.TABLE_NAME, tc.CONSTRAINT_NAME, cc.CHECK_CLAUSE
                    FROM information_schema.TABLE_CONSTRAINTS AS tc
                    JOIN information_schema.CHECK_CONSTRAINTS AS cc
                      ON tc.CONSTRAINT_SCHEMA = cc.CONSTRAINT_SCHEMA AND tc.CONSTRAINT_NAME = cc.CONSTRAINT_NAME
                    WHERE tc.TABLE_SCHEMA = DATABASE() ORDER BY tc.TABLE_NAME, tc.CONSTRAINT_NAME""",
        'references': """SELECT TABLE_NAME, CONSTRAINT_NAME, ORDINAL_POSITION, COLUMN_NAME,
                                REFERENCED_TABLE_SCHEMA, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                         FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = DATABASE()
                         ORDER BY TABLE_NAME, CONSTRAINT_NAME, ORDINAL_POSITION""",
    }
    return {kind: [tuple(row) for row in db.execute(text(sql)) if row[0] in names]
            for kind, sql in queries.items()}


def normalized_show_create(ddl):
    """仅归一 MySQL 为同一 utf8mb4 排序规则补写的冗余字符集声明。"""
    return ddl.replace(' CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci', ' COLLATE utf8mb4_unicode_ci')


@pytest.fixture(scope='module')
def targets():
    engines = [engine(s) for s in schemas]
    for schema, db_engine in zip(schemas, engines):
        with db_engine.connect() as db:
            verify_connection(db, schema)
            if inspect(db).get_table_names():
                raise RuntimeError('fixture schema is not empty')
    try:
        yield engines
    finally:
        for db_engine in engines: db_engine.dispose()


def test_01_empty_schema_full_chain(targets):
    migrate(schemas[0], '3d5f7a9c1e23')
    module = migration_module()
    with targets[0].connect() as db:
        verify_connection(db, schemas[0])
        assert revision(db) == [module.revision]
        assert state(db) == module.EXPECTED_TABLES - set(module.RETIRED_TABLES)
        from app.module_registry import import_model_packages
        from app.control_agent.models.gate_token import ControlAgentGateToken  # noqa: F401
        from app.user.models.user import User  # noqa: F401
        from app.user.models.token_blacklist import TokenBlacklist  # noqa: F401
        from database import Base
        import_model_packages()
        assert set(Base.metadata.tables) == state(db)
    # Alembic downgrade must refuse the forward-only revision.
    environment = dict(os.environ, TEST_MYSQL_DATABASE=schemas[0])
    result = subprocess.run([sys.executable, '-m', 'alembic', 'downgrade', module.down_revision],
                            cwd=ROOT / 'backend', env=environment, capture_output=True, text=True, timeout=30)
    assert result.returncode != 0 and 'forward-only' in result.stderr
    with targets[0].connect() as db: assert revision(db) == [module.revision]


def test_02_predecessor_upgrade_preserves_structures_and_rows(targets):
    module = migration_module()
    migrate(schemas[1], module.down_revision)
    with targets[1].begin() as db:
        verify_connection(db, schemas[1])
        assert revision(db) == [module.down_revision] and state(db) == module.EXPECTED_TABLES
        db.execute(text("INSERT INTO projection_mapping_sets (id,plc_key,db_number,group_name,handler_key) VALUES (1,'fixture',1,'g','historical')"))
        db.execute(text("INSERT INTO projection_runtime_cursors (id,mapping_set_id,last_raw_snapshot_id) VALUES (1,1,123)"))
        db.execute(text("""INSERT INTO plc_facts_samples_v2
            (instance_id,sample_id,plc_id,db_number,group_id,config_revision,source_generation,source_seq,
             points_json,content_hash,sampled_at,stored_at,expires_at)
            VALUES ('fixture','sample','PLC-A',21,'g','r','generation',1,JSON_ARRAY(),UNHEX(REPEAT('00',32)),
                    '2026-11-10 10:00:00.123456','2026-11-10 10:00:01.123456','2027-02-10 10:00:00.123456')"""))
        db.execute(text("""INSERT INTO plc_facts_latest_points_v2
            (plc_id,db_number,point_id,point_name,data_type,value_json,quality,observed_at,expires_at,
             instance_id,source_generation,source_seq,sample_id)
            VALUES ('PLC-A',21,'point','point','INT',JSON_EXTRACT('1','$'),'good',
                    '2026-11-10 10:00:00.123456','2027-02-10 10:00:00.123456','fixture','generation',1,'sample')"""))
    business_before = business_round(schemas[1])
    protected = module.EXPECTED_TABLES - set(module.RETIRED_TABLES)
    with targets[1].connect() as db: before = snapshot(db, protected)
    migrate(schemas[1], module.revision)
    with targets[1].connect() as db:
        assert revision(db) == [module.revision] and state(db) == protected
        assert snapshot(db, protected) == before
        assert db.execute(text('SELECT last_raw_snapshot_id FROM projection_runtime_cursors WHERE id=1')).scalar_one() == 123
    # At head Alembic repeats as a read-only no-op.
    migrate(schemas[1], module.revision)
    with targets[1].connect() as db: assert snapshot(db, protected) == before
    business_round(schemas[1], before=business_before)
    # Subsequent v2 writes/cleanup are synthetic and occur only after preservation comparison.
    with pytest.MonkeyPatch.context() as patch:
        v2_http_and_cleanup(schemas[1], targets[1], patch)


def test_03_guards_lock_timeout_and_registration_recovery(targets, monkeypatch, tmp_path):
    module = migration_module()
    migrate(schemas[2], module.down_revision)
    old = set(module.RETIRED_TABLES)
    protected = module.EXPECTED_TABLES - old
    with targets[2].connect() as db:
        before = snapshot(db, protected)
        old_ddl = {name: db.exec_driver_sql(f'SHOW CREATE TABLE `{name}`').one()[1] for name in old}
        old_signature = schema_signature(db, old)
        assert db.execute(text("SELECT CHARACTER_SET_NAME FROM information_schema.COLLATIONS "
                               "WHERE COLLATION_NAME='utf8mb4_unicode_ci'")).scalar_one() == 'utf8mb4'
    # A nonempty old table prevents the first DDL.
    with targets[2].begin() as db:
        db.execute(text("""INSERT INTO plc_facts_batches (instance_id,batch_id,request_digest,receipt_id,terminal,http_status,
            result,members,parent_depth,recorded_at,proof_expires_at,created_at,updated_at)
            VALUES ('fixture','sample',UNHEX(REPEAT('00',32)),'fixture','committed',200,'{}','{}',0,NOW(6),NOW(6),NOW(6),NOW(6))"""))
    migrate(schemas[2], module.revision, expect=1)
    with targets[2].begin() as db:
        assert revision(db) == [module.down_revision] and state(db) == module.EXPECTED_TABLES
        db.execute(text('DELETE FROM plc_facts_batches'))
        db.execute(text('CREATE VIEW acq002_fixture_view AS SELECT * FROM plc_db_block_raw_snapshots'))
    migrate(schemas[2], module.revision, expect=1)
    with targets[2].begin() as db:
        assert revision(db) == [module.down_revision] and state(db) == module.EXPECTED_TABLES
        db.execute(text('DROP VIEW acq002_fixture_view'))
    migrate(schemas[2], module.revision, extra={'ACQ_RETIREMENT_EXPECTED_SERVER_UUID': 'incorrect'}, expect=1)
    # A real conflicting table lock must fail in bounded time without DDL.
    with targets[2].connect() as blocker:
        blocker.exec_driver_sql('LOCK TABLES `plc_facts_batches` READ')
        try:
            started = time.monotonic()
            migrate(schemas[2], module.revision, expect=1)
            elapsed = time.monotonic() - started
            assert 4 <= elapsed < 20
        finally:
            blocker.exec_driver_sql('UNLOCK TABLES')
    with targets[2].connect() as db:
        assert revision(db) == [module.down_revision] and state(db) == module.EXPECTED_TABLES
        assert snapshot(db, protected) == before
    # Execute the same migration's DDL on one connection, then simulate failure before Alembic registration.
    monkeypatch.setenv('ACQ_RETIREMENT_EXPECTED_SCHEMA', schemas[2])
    monkeypatch.setenv('ACQ_RETIREMENT_EXPECTED_SERVER_UUID', server_uuid)
    with targets[2].connect() as db:
        module.context = SimpleNamespace(is_offline_mode=lambda: False)
        module.op = SimpleNamespace(get_bind=lambda: db, execute=db.exec_driver_sql)
        module.upgrade()
    with targets[2].connect() as db:
        assert revision(db) == [module.down_revision] and state(db) == protected
        assert snapshot(db, protected) == before
    migrate(schemas[2], module.revision, expect=1)
    # Fixture evidence is synthetic: same migration, saved DDL and protected-data audit above.
    evidence = __import__('hashlib').sha256('\n'.join(old_ddl[k] for k in sorted(old_ddl)).encode()).hexdigest()
    migrate(schemas[2], module.revision, extra={'ACQ_RETIREMENT_RECOVERY_EVIDENCE_SHA256': evidence,
            'ACQ_RETIREMENT_RECOVERY_CONFIRMED': schemas[2] + ':' + server_uuid})
    with targets[2].connect() as db:
        assert revision(db) == [module.revision] and state(db) == protected
        assert snapshot(db, protected) == before
    # Exact table DDL can be restored in the dedicated guard schema only; no version stamp.
    with targets[2].begin() as db:
        for name in sorted(old_ddl): db.exec_driver_sql(old_ddl[name])
        restored = {name: db.exec_driver_sql(f'SHOW CREATE TABLE `{name}`').one()[1] for name in old}
        restored_signature = schema_signature(db, old)
        canonical_before = {name: normalized_show_create(ddl) for name, ddl in old_ddl.items()}
        canonical_after = {name: normalized_show_create(ddl) for name, ddl in restored.items()}
        if restored_signature != old_signature or canonical_after != canonical_before:
            from difflib import unified_diff
            differences = []
            for name in sorted(old):
                if restored[name] == old_ddl[name]:
                    continue
                (tmp_path / f'{name}.before.sql').write_text(old_ddl[name])
                (tmp_path / f'{name}.restored.sql').write_text(restored[name])
                differences.extend(unified_diff(old_ddl[name].splitlines(), restored[name].splitlines(),
                                                fromfile=name + '.before', tofile=name + '.restored', lineterm=''))
            pytest.fail(f'fixture schema mismatch; details in {tmp_path}\n' + '\n'.join(differences), pytrace=False)
        import hashlib, json
        def digest(value):
            return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()
        proof = {'tables': len(old), 'metadataBefore': digest(old_signature), 'metadataAfter': digest(restored_signature),
                 'normalizedBefore': digest(canonical_before), 'normalizedAfter': digest(canonical_after),
                 'showCreateChanged': sorted(name for name in old if old_ddl[name] != restored[name]),
                 'showCreateAddedCharsetDeclarations': sum(
                     restored[name].count(' CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
                     - old_ddl[name].count(' CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci') for name in old)}
        (tmp_path / 'ddl-restore-proof.json').write_text(json.dumps(proof, indent=2, sort_keys=True) + '\n')


def business_round(schema, *, before=None):
    """相同目标合成凭据：前驱写八路，后继拒旧凭据、重放旧回执并写八路。"""
    import asyncio
    from copy import deepcopy
    from importlib import import_module
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from common.exceptions import BusinessException
    from tests.test_business_integration_contract import REQUESTS, RESOURCES, example
    from tests.test_business_integration_storage import manifest

    async def run():
        url = URL.create('mysql+aiomysql', username=os.environ['MYSQL_USER'], password=os.environ['MYSQL_PASSWORD'],
                         host='127.0.0.1', port=int(port), database=schema)
        async_engine = create_async_engine(url, poolclass=NullPool)
        sessions = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False)
        owners = ('equipment',) * 3 + ('performance',) * 4 + ('monitor',)
        current_revision = '2c4e6a8b0d12' if before is None else '3d5f7a9c1e23'

        def payload(index, group):
            item = example(index)
            identity = 'acq002-' + group
            item.update(producerId=identity, eventId='event-' + str(index))
            item['data']['equipmentId'] = identity
            if 'coilNo' in item['data']: item['data']['coilNo'] = identity
            return item

        def evidence(owner, rev=current_revision):
            item = manifest(owner)
            item.update(serverUuid=server_uuid, schema=schema, schemaRevision=rev,
                        sourceRevision='synthetic-acq002', ownerApprovalRef='isolated-fixture-only')
            return item

        async def receive(index, item, parent, adoption):
            request = REQUESTS[index].model_validate(item)
            async with sessions() as db:
                if index < 3:
                    return await import_module('app.equipment.services.async_integration').receive_sample(db, request, adoption, RESOURCES[index])
                if index == 3:
                    return await import_module('app.performance.services.async_integration_observation').receive_observation(db, request, adoption)
                if index < 7:
                    return await import_module('app.performance.services.async_integration_process').receive_sample(db, request, adoption, parent, RESOURCES[index].removeprefix('process_'))
                return await import_module('app.monitor.services.async_integration').receive_sample(db, request, adoption)

        try:
            if before is not None:
                for owner, index in (('equipment', 0), ('performance', 3), ('monitor', 7)):
                    with pytest.raises(BusinessException) as error:
                        await receive(index, payload(index, 'old'), before[3][1], evidence(owner, '2c4e6a8b0d12'))
                    assert error.value.code == 503
                for index in (3, 0, 1, 2, 4, 5, 6, 7):
                    old_item, old_record, old_receipt, old_committed = before[index]
                    replay = await receive(index, old_item, before[3][1], evidence(owners[index]))
                    assert replay.outcome == 'duplicate'
                    assert (replay.record_id, replay.receipt_id, replay.committed_at) == (old_record, old_receipt, old_committed)
            group = 'old' if before is None else 'new'
            results = {}
            parent = None
            for index in (3, 0, 1, 2, 4, 5, 6, 7):
                item = payload(index, group)
                result = await receive(index, item, parent, evidence(owners[index]))
                if index == 3: parent = result.record_id
                replay = await receive(index, item, parent, evidence(owners[index]))
                assert replay.outcome == 'duplicate' and replay.receipt_id == result.receipt_id
                results[index] = (deepcopy(item), result.record_id, result.receipt_id, result.committed_at)
            return results
        finally:
            await async_engine.dispose()
    return asyncio.run(run())


def v2_http_and_cleanup(schema, sync_engine, monkeypatch):
    """使用合成 profile 和实际隔离数据库执行五路 v2 合同与 cleanup。"""
    import asyncio
    from copy import deepcopy
    from datetime import timedelta
    import hashlib
    import json
    from fastapi import FastAPI
    from httpx import ASGITransport, AsyncClient
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.orm import Session
    from app.plc_facts.api import v2 as api
    from app.plc_facts.v2_config import parse_profile
    from app.plc_facts.v2_domain import V2Error
    from app.plc_facts.services.sync_v2_maintenance import run as cleanup

    with sync_engine.connect() as db:
        now, offset = db.execute(text('SELECT CURRENT_TIMESTAMP(6), TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))')).one()
        assert offset == 28800
    token = 'synthetic-acq002-token-for-isolated-tests'
    document = {'target': {'alias': 'synthetic', 'schema': schema, 'serverUuid': server_uuid, 'schemaRevision': '3d5f7a9c1e23'},
                'credentials': [{'instanceId': 'machine', 'tokenSha256': hashlib.sha256(token.encode()).hexdigest()}],
                'sources': [{'plcId': 'PLC-A', 'instanceId': 'machine', 'sourceGeneration': 'new-generation', 'dbNumbers': [21]}],
                'readScopes': {'fixture-role': [{'plcId': 'PLC-A', 'dbNumbers': [21]}]}}
    profile = parse_profile(document)
    async def exercise():
        url = URL.create('mysql+aiomysql', username=os.environ['MYSQL_USER'], password=os.environ['MYSQL_PASSWORD'],
                         host='127.0.0.1', port=int(port), database=schema)
        async_engine = create_async_engine(url, poolclass=NullPool)
        sessions = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False)
        async def get_session(): return sessions()
        monkeypatch.setattr(api, 'get_db_session', get_session)
        monkeypatch.setattr(api, 'get_profile', lambda: profile)
        app = FastAPI()
        app.include_router(api.router, prefix='/api/v1')
        app.dependency_overrides[api.reader] = lambda: SimpleNamespace(role='fixture-role')
        ts = now.isoformat(timespec='microseconds') + '+08:00'
        item = {'contractVersion': 'plc-facts/v2', 'instanceId': 'machine', 'sampleId': 'new-sample',
                'plcId': 'PLC-A', 'dbNumber': 21, 'groupId': 'g', 'configRevision': 'r',
                'sourceGeneration': 'new-generation', 'sourceSeq': '2', 'points': [
                    {'pointId': 'point', 'dataType': 'INT', 'value': 42, 'quality': 'good', 'observedAt': ts}]}
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://isolated') as client:
            assert (await client.post('/api/v1/integration/plc-facts/samples', json=item)).status_code == 401
            created = await client.post('/api/v1/integration/plc-facts/samples', json=item, headers=headers)
            assert created.status_code == 200 and created.json()['data']['outcome'] == 'created'
            duplicate = await client.post('/api/v1/integration/plc-facts/samples', json=item, headers=headers)
            assert duplicate.status_code == 200 and duplicate.json()['data']['outcome'] == 'duplicate'
            conflict = deepcopy(item); conflict['points'][0]['value'] = 43
            assert (await client.post('/api/v1/integration/plc-facts/samples', json=conflict, headers=headers)).status_code == 409
            options = await client.get('/api/v1/acquisition-data/options')
            assert options.status_code == 200 and options.json()['data']['items'] == [{'plcId': 'PLC-A', 'dbNumbers': [21]}]
            latest = await client.get('/api/v1/acquisition-data/latest', params={'plcId': 'PLC-A', 'dbNumber': 21})
            assert latest.status_code == 200 and latest.json()['data']['items'][0]['value'] == 42
            assert (await client.get('/api/v1/acquisition-data/latest', params={'plcId': 'PLC-A', 'dbNumber': 22})).status_code == 403
            params = {'plcId': 'PLC-A', 'dbNumber': 21,
                      'from': (now - timedelta(minutes=1)).isoformat(timespec='microseconds') + '+08:00',
                      'to': (now + timedelta(minutes=1)).isoformat(timespec='microseconds') + '+08:00'}
            history = await client.get('/api/v1/acquisition-data/history', params=params)
            assert history.status_code == 200 and history.json()['data']['items']
            sample_id = history.json()['data']['items'][0]['id']
            detail = await client.get('/api/v1/acquisition-data/history/' + sample_id)
            assert detail.status_code == 200 and detail.json()['data']['points'][0]['value'] == 42
            profile['target']['schemaRevision'] = '2c4e6a8b0d12'
            assert (await client.get('/api/v1/acquisition-data/options')).status_code == 503
            profile['target']['schemaRevision'] = '3d5f7a9c1e23'
            def disabled(): raise V2Error('not_ready', 503)
            monkeypatch.setattr(api, 'get_profile', disabled)
            assert (await client.get('/api/v1/acquisition-data/options')).status_code == 503
        await async_engine.dispose()
    asyncio.run(exercise())
    with sync_engine.begin() as db:
        db.execute(text("UPDATE plc_facts_samples_v2 SET expires_at=CURRENT_TIMESTAMP(6)-INTERVAL 1 SECOND WHERE sample_id='new-sample'"))
        db.execute(text("UPDATE plc_facts_latest_points_v2 SET expires_at=CURRENT_TIMESTAMP(6)-INTERVAL 1 SECOND WHERE sample_id='new-sample'"))
    with Session(sync_engine) as db:
        old_target = dict(profile['target'], schemaRevision='2c4e6a8b0d12')
        with pytest.raises(V2Error): cleanup(db, old_target, False)
        db.rollback()
        assert cleanup(db, profile['target'], False)['rows'] >= 2
        assert cleanup(db, profile['target'], True)['rows'] >= 2
    with sync_engine.connect() as db:
        assert db.execute(text("SELECT COUNT(*) FROM plc_facts_samples_v2 WHERE sample_id='new-sample'")).scalar_one() == 0
        row = db.execute(text("SELECT source_seq, value_json FROM plc_facts_latest_points_v2 WHERE plc_id='PLC-A' AND db_number=21 AND point_id='point' ")).one()
        assert row == (2, None)
