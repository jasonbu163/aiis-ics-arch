"""ARCH-ACQ-003 r2 真实 MySQL 隔离库迁移与恢复验证；不创建实例或账号。"""
from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import time

import pytest

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ('ARCH_ACQ003_FIXTURE_ROUND', 'ARCH_ACQ003_FIXTURE_PORT', 'ARCH_ACQ003_FIXTURE_UUID',
            'ARCH_ACQ003_SCHEMA_UPGRADE', 'ARCH_ACQ003_SCHEMA_RENAMED',
            'ARCH_ACQ003_SCHEMA_ALTERED', 'ARCH_ACQ003_SCHEMA_GUARD',
            'ARCH_ACQ003_FIXTURE_ACK', 'MYSQL_HOST', 'MYSQL_PORT', 'MYSQL_USER', 'MYSQL_PASSWORD',
            'MYSQL_DATABASE', 'TESTING')
if any(not os.environ.get(key, '').strip() for key in REQUIRED):
    pytest.skip('ACQ003 requires an explicitly identified isolated MySQL fixture', allow_module_level=True)

round_name = os.environ['ARCH_ACQ003_FIXTURE_ROUND']
port = os.environ['ARCH_ACQ003_FIXTURE_PORT']
server_uuid = os.environ['ARCH_ACQ003_FIXTURE_UUID']
schemas = tuple(os.environ[key] for key in ('ARCH_ACQ003_SCHEMA_UPGRADE', 'ARCH_ACQ003_SCHEMA_RENAMED',
                                             'ARCH_ACQ003_SCHEMA_ALTERED', 'ARCH_ACQ003_SCHEMA_GUARD'))
expected_schemas = tuple(f'arch_acq003_{round_name}_{suffix}' for suffix in ('upgrade', 'renamed', 'altered', 'guard'))
expected_ack = ':'.join(('ACQ003', round_name, server_uuid, port, *schemas))
if (round_name not in ('dev', 'qa') or not ROOT.is_relative_to(Path('/private/tmp'))
        or not ROOT.name.startswith('arch-acq003-r2-candidate-')
        or (ROOT / 'backend/.env').exists() or Path.cwd().resolve() != (ROOT / 'backend').resolve()
        or port not in ('3307', '13393', '13394') or os.environ['MYSQL_HOST'] != '127.0.0.1'
        or os.environ['MYSQL_PORT'] != port or os.environ['MYSQL_USER'] != f'arch_acq003_{round_name}'
        or not re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', server_uuid)
        or os.environ['TESTING'].lower() != 'true' or schemas != expected_schemas
        or os.environ['MYSQL_DATABASE'] in schemas or os.environ['MYSQL_DATABASE'] == 'industrial_level_2_system'
        or 'industrial_level_2_system' in schemas or os.environ['ARCH_ACQ003_FIXTURE_ACK'] != expected_ack):
    raise RuntimeError('ACQ003 isolated fixture guard rejected configuration')

# Every project import must resolve to this temporary, public candidate.
for name, relative in (('settings', 'settings.py'), ('database', 'database/__init__.py'), ('app', 'app/__init__.py')):
    found = importlib.util.find_spec(name)
    if found is None or found.origin is None or Path(found.origin).resolve() != (ROOT / 'backend' / relative).resolve():
        raise RuntimeError('ACQ003 project imports must resolve to the isolated candidate')

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool


def engine(schema):
    if schema not in schemas:
        raise RuntimeError('schema outside isolated fixture allowlist')
    url = URL.create('mysql+pymysql', username=os.environ['MYSQL_USER'], password=os.environ['MYSQL_PASSWORD'],
                     host='127.0.0.1', port=int(port), database=schema)
    return create_engine(url, poolclass=NullPool,
                         connect_args={'connect_timeout': 3, 'read_timeout': 30, 'write_timeout': 30})


def verify_connection(db, schema):
    version, uuid, actual_schema, current_user, offset = db.execute(text('''
        SELECT VERSION(), @@server_uuid, DATABASE(), CURRENT_USER(),
               TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))
    ''')).one()
    if (str(version).split('-')[0] != '8.4.6' or uuid != server_uuid or actual_schema != schema
            or current_user.split('@', 1)[0] != os.environ['MYSQL_USER'] or offset != 28800):
        raise RuntimeError('fixture database identity mismatch')


def module():
    path = ROOT / 'backend/alembic/versions/20261111_1030_4e6a8b0d2f14_finalize_plc_facts_tables.py'
    spec = importlib.util.spec_from_file_location('acq003_isolated_migration', path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def operation(schema):
    return f'acq003-{round_name}-{schema.rsplit("_", 1)[1]}'


def migrate(schema, revision, *, extra=None, expect_success=True, offline=False):
    if schema not in schemas:
        raise RuntimeError('schema outside isolated fixture allowlist')
    env = dict(os.environ, TEST_MYSQL_DATABASE=schema,
               ACQ_RETIREMENT_EXPECTED_SCHEMA=schema, ACQ_RETIREMENT_EXPECTED_SERVER_UUID=server_uuid,
               ACQ_FACTS_EXPECTED_SCHEMA=schema, ACQ_FACTS_EXPECTED_SERVER_UUID=server_uuid,
               ACQ_FACTS_OPERATION_ID=operation(schema))
    env.pop('ACQ_FACTS_RECOVERY_STAGE', None)
    env.pop('ACQ_FACTS_RECOVERY_EVIDENCE_SHA256', None)
    env.update(extra or {})
    command = [sys.executable, '-m', 'alembic', 'upgrade', revision]
    if offline:
        command.append('--sql')
    result = subprocess.run(command, cwd=ROOT / 'backend', env=env, capture_output=True, text=True, timeout=120)
    assert (result.returncode == 0) == expect_success, f'Alembic exit={result.returncode}: {result.stderr[-3000:]}'
    return result


def target_env(monkeypatch, schema):
    monkeypatch.setenv('ACQ_FACTS_EXPECTED_SCHEMA', schema)
    monkeypatch.setenv('ACQ_FACTS_EXPECTED_SERVER_UUID', server_uuid)
    monkeypatch.setenv('ACQ_FACTS_OPERATION_ID', operation(schema))


def insert_fixture(db):
    for n in (1, 2):
        db.execute(text('''INSERT INTO plc_facts_samples_v2
            (instance_id,sample_id,plc_id,db_number,group_id,config_revision,source_generation,source_seq,
             points_json,content_hash,sampled_at,stored_at,expires_at)
            VALUES (:instance,:sample,'PLC-A',21,'group','config','gen',:seq,
                    JSON_ARRAY(JSON_OBJECT('pointId','temp','value',:seq)), UNHEX(SHA2(:sample,256)),
                    '2026-11-10 10:00:00.123456','2026-11-10 10:00:01.123456','2027-02-10 10:00:00.123456')'''),
                   {'instance': 'fixture', 'sample': f'sample-{n}', 'seq': n})
    db.execute(text('''INSERT INTO plc_facts_latest_points_v2
        (plc_id,db_number,point_id,point_name,data_type,value_json,quality,observed_at,expires_at,
         instance_id,source_generation,source_seq,sample_id)
        VALUES ('PLC-A',21,'temp','temperature','INT',JSON_EXTRACT('2','$'),'good',
                '2026-11-10 10:00:00.123456','2027-02-10 10:00:00.123456','fixture','gen',2,'sample-2')'''))
    db.execute(text('ALTER TABLE plc_facts_samples_v2 AUTO_INCREMENT = 100'))


def other_tables_digest(db):
    m = module()
    names = set(inspect(db).get_table_names()) - {'alembic_version', m.OLD_HISTORY, m.OLD_LATEST, m.HISTORY, m.LATEST}
    output = {}
    for name in sorted(names):
        assert re.fullmatch(r'[a-z0-9_]+', name)
        ddl = db.exec_driver_sql(f'SHOW CREATE TABLE `{name}`').one()[1]
        count = db.exec_driver_sql(f'SELECT COUNT(*) FROM `{name}`').scalar_one()
        checksum = db.exec_driver_sql(f'CHECKSUM TABLE `{name}`').one()[1]
        output[name] = (hashlib.sha256(ddl.encode()).hexdigest(), count, checksum)
    return output


@pytest.fixture(scope='module')
def targets():
    engines = [engine(schema) for schema in schemas]
    for schema, db_engine in zip(schemas, engines):
        with db_engine.connect() as db:
            verify_connection(db, schema)
            if inspect(db).get_table_names():
                raise RuntimeError('ACQ003 fixture schemas must all be empty')
    # All four identities have been read-only checked before the first write.
    for schema, db_engine in zip(schemas, engines):
        migrate(schema, '3d5f7a9c1e23')
        with db_engine.begin() as db:
            insert_fixture(db)
    try:
        yield engines
    finally:
        for db_engine in engines:
            db_engine.dispose()


def test_01_guards_reject_real_schema_before_collection(targets):
    env = dict(os.environ, ARCH_ACQ003_SCHEMA_GUARD='industrial_level_2_system')
    result = subprocess.run([sys.executable, '-m', 'pytest', '--collect-only', '-q',
                             'tests_mysql/test_acquisition_facts_r2.py'],
                            cwd=ROOT / 'backend', env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode != 0 and 'isolated fixture guard rejected' in result.stderr + result.stdout
    result = migrate(schemas[0], '3d5f7a9c1e23:4e6a8b0d2f14', expect_success=False, offline=True)
    assert 'offline' in (result.stderr + result.stdout).lower()


def test_02_upgrade_preserves_rows_other_tables_keys_and_watermark(targets, monkeypatch):
    m = module()
    schema = schemas[0]
    target_env(monkeypatch, schema)
    with targets[0].connect() as db:
        before = m._audit(db, m.OLD_HISTORY, m.OLD_LATEST)
        assert before['history']['count'] == 2 and before['historyAutoIncrement'] == 100
        proof = m.recovery_evidence_sha256(db)
        other_before = other_tables_digest(db)
    migrate(schema, m.revision)
    with targets[0].connect() as db:
        assert list(db.execute(text('SELECT version_num FROM alembic_version')).scalars()) == [m.revision]
        assert m._state(db)[0] == 'altered'
        assert m._audit(db, m.HISTORY, m.LATEST) == before
        assert m.recovery_evidence_sha256(db) == proof
        assert other_tables_digest(db) == other_before
        assert db.execute(text('SELECT COUNT(*) FROM plc_facts_history WHERE source_type IS NOT NULL')).scalar_one() == 0
        assert db.execute(text('SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() '
                               "AND TABLE_NAME IN ('plc_facts_batches','plc_db_block_raw_snapshots')")).scalar_one() == 0
    migrate(schema, m.revision)  # registered successor is a read-only Alembic no-op
    env = dict(os.environ, TEST_MYSQL_DATABASE=schema)
    result = subprocess.run([sys.executable, '-m', 'alembic', 'downgrade', m.down_revision],
                            cwd=ROOT / 'backend', env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode != 0 and 'forward-only' in result.stderr
    for invalid in ('DAA', 'daa ', 'daa\0', 'External'):
        with pytest.raises(Exception):
            with targets[0].begin() as db:
                db.execute(text('UPDATE plc_facts_history SET source_type=:value WHERE id=1'), {'value': invalid})
    # MySQL trims excess trailing spaces even in STRICT_TRANS_TABLES before CHECK.
    # The stored value is still exact; the API never accepts sourceType in requests.
    with targets[0].connect() as db:
        db.execute(text('UPDATE plc_facts_history SET source_type=:value WHERE id=1'), {'value': 'external '})
        assert db.execute(text('SELECT source_type FROM plc_facts_history WHERE id=1')).scalar_one() == 'external'
        db.rollback()


def test_03_renamed_recovery_requires_matching_evidence(targets, monkeypatch):
    m = module()
    schema = schemas[1]
    target_env(monkeypatch, schema)
    with targets[1].connect() as db:
        proof = m.recovery_evidence_sha256(db)
        before = m._audit(db, m.OLD_HISTORY, m.OLD_LATEST)
        db.execute(text(m.RENAME_SQL))
        assert m._state(db)[0] == 'renamed'
    migrate(schema, m.revision, expect_success=False)
    migrate(schema, m.revision, extra={'ACQ_FACTS_RECOVERY_STAGE': 'renamed',
                                      'ACQ_FACTS_RECOVERY_EVIDENCE_SHA256': '0' * 64}, expect_success=False)
    migrate(schema, m.revision, extra={'ACQ_FACTS_RECOVERY_STAGE': 'renamed',
                                      'ACQ_FACTS_RECOVERY_EVIDENCE_SHA256': proof})
    with targets[1].connect() as db:
        assert m._state(db)[0] == 'altered'
        assert m._audit(db, m.HISTORY, m.LATEST) == before
        assert list(db.execute(text('SELECT version_num FROM alembic_version')).scalars()) == [m.revision]


def test_04_altered_recovery_requires_matching_evidence(targets, monkeypatch):
    m = module()
    schema = schemas[2]
    target_env(monkeypatch, schema)
    with targets[2].connect() as db:
        proof = m.recovery_evidence_sha256(db)
        before = m._audit(db, m.OLD_HISTORY, m.OLD_LATEST)
        db.execute(text(m.RENAME_SQL))
        db.execute(text(m.ALTER_SQL))
        assert m._state(db)[0] == 'altered'
        assert m.recovery_evidence_sha256(db) == proof
    migrate(schema, m.revision, expect_success=False)
    migrate(schema, m.revision, extra={'ACQ_FACTS_RECOVERY_STAGE': 'renamed',
                                      'ACQ_FACTS_RECOVERY_EVIDENCE_SHA256': proof}, expect_success=False)
    migrate(schema, m.revision, extra={'ACQ_FACTS_RECOVERY_STAGE': 'altered',
                                      'ACQ_FACTS_RECOVERY_EVIDENCE_SHA256': proof})
    with targets[2].connect() as db:
        assert m._audit(db, m.HISTORY, m.LATEST) == before
        assert list(db.execute(text('SELECT version_num FROM alembic_version')).scalars()) == [m.revision]


def test_05_wrong_target_mixed_shape_dependency_and_lock_timeout(targets, monkeypatch):
    m = module()
    schema = schemas[3]
    target_env(monkeypatch, schema)
    with targets[3].connect() as db:
        before = m._audit(db, m.OLD_HISTORY, m.OLD_LATEST)
    migrate(schema, m.revision, extra={'ACQ_FACTS_EXPECTED_SERVER_UUID': 'wrong'}, expect_success=False)
    with targets[3].begin() as db:
        db.execute(text(f'RENAME TABLE `{m.OLD_HISTORY}` TO `{m.HISTORY}`'))
    migrate(schema, m.revision, expect_success=False)
    with targets[3].begin() as db:
        db.execute(text(f'RENAME TABLE `{m.HISTORY}` TO `{m.OLD_HISTORY}`'))
        db.execute(text(f'CREATE VIEW acq003_fixture_view AS SELECT id FROM `{m.OLD_HISTORY}`'))
    migrate(schema, m.revision, expect_success=False)
    with targets[3].begin() as db:
        db.execute(text('DROP VIEW acq003_fixture_view'))
    with targets[3].connect() as blocker:
        blocker.exec_driver_sql(f'LOCK TABLES `{m.OLD_HISTORY}` READ')
        try:
            started = time.monotonic()
            migrate(schema, m.revision, expect_success=False)
            assert 4 <= time.monotonic() - started < 30
        finally:
            blocker.exec_driver_sql('UNLOCK TABLES')
    with targets[3].connect() as db:
        assert m._state(db)[0] == 'old'
        assert m._audit(db, m.OLD_HISTORY, m.OLD_LATEST) == before
        assert list(db.execute(text('SELECT version_num FROM alembic_version')).scalars()) == [m.down_revision]


def test_06_evidence_mapping_rolls_back_every_row_on_mismatch(targets):
    """Only synthetic identities; exact original digest and NULL guard, one transaction."""
    m = module()
    with targets[0].connect() as db:
        original = m._audit(db, m.HISTORY, m.LATEST)
        mapping = list(db.execute(text('SELECT id,instance_id,sample_id,content_hash FROM plc_facts_history ORDER BY id')))
    assert len(mapping) == 2
    def apply(db, rows):
        for row_id, instance, sample, digest in rows:
            result = db.execute(text('''UPDATE plc_facts_history SET source_type='external'
                WHERE id=:id AND instance_id=:instance AND sample_id=:sample AND content_hash=:hash AND source_type IS NULL'''),
                                {'id': row_id, 'instance': instance, 'sample': sample, 'hash': digest})
            if result.rowcount != 1:
                raise ValueError('mapping identity mismatch')
        assert m._audit(db, m.HISTORY, m.LATEST) == original
    bad = [mapping[0], (mapping[1][0], mapping[1][1], b'wrong-sample', mapping[1][3])]
    with pytest.raises(ValueError, match='identity'):
        with targets[0].begin() as db:
            apply(db, bad)
    with targets[0].connect() as db:
        assert db.execute(text('SELECT COUNT(*) FROM plc_facts_history WHERE source_type IS NOT NULL')).scalar_one() == 0
        assert m._audit(db, m.HISTORY, m.LATEST) == original
    with targets[0].begin() as db:
        apply(db, mapping)
    with targets[0].connect() as db:
        assert db.execute(text("SELECT COUNT(*) FROM plc_facts_history WHERE source_type='external'")).scalar_one() == 2
        assert m._audit(db, m.HISTORY, m.LATEST) == original
