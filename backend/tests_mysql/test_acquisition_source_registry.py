"""ARCH-ACQ-004 r3 专属合成 MySQL / 双进程 HTTP；未显式批准时不连接。"""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from datetime import timedelta, timezone
from uuid import UUID, uuid4

import pytest


REQUIRED = ('ACQ004_TEST_OPERATION_APPROVAL', 'ACQ004_TEST_SERVER_UUID', 'ACQ004_TEST_ALIAS',
            'ACQ004_TEST_SCHEMA', 'ACQ004_TEST_RESTORE_SCHEMA', 'ACQ004_TEST_GUARD_SCHEMA',
            'ACQ004_TEST_MYSQL_PORT', 'ACQ004_TEST_HTTP_PORT_A', 'ACQ004_TEST_HTTP_PORT_B',
            'ACQ004_TEST_ADMIN_TOKEN', 'ACQ004_TEST_USER_TOKEN', 'ACQ004_TEST_CONFIRM',
            'ACQ004_TEST_DDL_USER', 'ACQ004_TEST_DDL_PASSWORD', 'PLC_FACTS_V2_PROFILE_FILE',
            'MYSQL_HOST', 'MYSQL_PORT', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE', 'TEST_MYSQL_DATABASE')
if any(not os.environ.get(name, '').strip() for name in REQUIRED):
    pytest.skip('requires separately approved ARCH-ACQ-004 r3 disposable target', allow_module_level=True)

root = Path(__file__).resolve().parents[2]
backend = root / 'backend'
owned_root = next((p for p in (root, *root.parents) if p.parent == Path('/private/tmp')
                   and p.name.startswith('arch-acq004-r3-')), None)
alias = os.environ['ACQ004_TEST_ALIAS']
match = re.fullmatch(r'arch-acq004-r3-(dev|qa)', alias)
schema = os.environ['ACQ004_TEST_SCHEMA']
restore_schema = os.environ['ACQ004_TEST_RESTORE_SCHEMA']
guard_schema = os.environ['ACQ004_TEST_GUARD_SCHEMA']
server_uuid = os.environ['ACQ004_TEST_SERVER_UUID']
mysql_port = os.environ['ACQ004_TEST_MYSQL_PORT']
http_a, http_b = os.environ['ACQ004_TEST_HTTP_PORT_A'], os.environ['ACQ004_TEST_HTTP_PORT_B']
expected = ':'.join(('RUN', alias, server_uuid, mysql_port, schema, restore_schema, guard_schema, http_a, http_b))
try:
    valid_uuid = str(UUID(server_uuid)) == server_uuid
except ValueError:
    valid_uuid = False
if (owned_root is None or not root.is_relative_to(owned_root)
        or Path.cwd().resolve() != backend.resolve() or (backend / '.env').exists()
        or match is None or (match is not None and root not in (owned_root, owned_root / 'source', owned_root / match.group(1)))
        or not valid_uuid or not mysql_port.isdigit() or mysql_port == '3307'
        or not http_a.isdigit() or not http_b.isdigit() or http_a == http_b
        or http_a in ('8000', '5190', '15191') or http_b in ('8000', '5190', '15191')
        or (schema, restore_schema, guard_schema) != tuple(f'arch_acq004_r3_{match.group(1)}_{suffix}' for suffix in ('main', 'restore', 'guard'))
        or os.environ['ACQ004_TEST_CONFIRM'] != expected
        or os.environ['MYSQL_HOST'] != '127.0.0.1' or os.environ['MYSQL_PORT'] != mysql_port
        or os.environ.get('TESTING', '').lower() != 'true' or os.environ['TEST_MYSQL_DATABASE'] != schema
        or os.environ['MYSQL_DATABASE'] in (schema, restore_schema, guard_schema)
        or os.environ['MYSQL_USER'] in ('', 'root') or os.environ['ACQ004_TEST_DDL_USER'] in ('', 'root', os.environ['MYSQL_USER'])):
    raise RuntimeError('ACQ004 dedicated target guard rejected configuration')
if any(os.environ.get(key, 'false').lower() != 'false' for key in
       ('BACKEND_MOCK_ENABLED', 'PROJECTION_RUNNER_ENABLED', 'ADMIN_BOOTSTRAP_ENABLED',
        'SUPERVISOR_BOOTSTRAP_ENABLED', 'OPERATOR_BOOTSTRAP_ENABLED')):
    raise RuntimeError('ACQ004 fixture requires unrelated services and bootstrap disabled')

# All project imports and any DB sessions occur after the explicit guard above.
from httpx import AsyncClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from sqlalchemy.pool import NullPool  # noqa: E402
from database import create_sync_session, get_db_session  # noqa: E402
from app.plc_facts.crud import async_v2 as facts_crud  # noqa: E402
from app.plc_facts.crud.sync_v2_maintenance import target_now  # noqa: E402
from app.plc_facts.schemas.source_registry import UpdateIn  # noqa: E402
from app.plc_facts.services import async_source_registry as registry_service, async_v2 as facts_service  # noqa: E402
from app.plc_facts.v2_config import REVISION, get_profile  # noqa: E402
from app.plc_facts.v2_domain import parse_sample  # noqa: E402
from settings import settings  # noqa: E402


@pytest.fixture(scope='module')
def target():
    profile = get_profile()
    assert profile['target'] == {'alias':alias, 'schema':schema, 'serverUuid':server_uuid, 'schemaRevision':REVISION}
    db = create_sync_session()
    try:
        info = db.execute(text('SELECT @@server_uuid,DATABASE(),VERSION(),CURRENT_TIMESTAMP(6),'
                               'TIMESTAMPDIFF(SECOND,UTC_TIMESTAMP(6),CURRENT_TIMESTAMP(6))')).one()
        assert str(info[0]).lower() == server_uuid and info[1] == schema and info[2].split('-')[0] == '8.4.6' and info[4] == 28800
        assert list(db.execute(text('SELECT version_num FROM alembic_version')).scalars()) == [REVISION]
        tables = db.execute(text("SELECT TABLE_NAME,ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME LIKE 'acq_source_%' ORDER BY TABLE_NAME")).all()
        assert tables == []
        assert db.execute(text("SELECT ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='plc_source_registry'")).scalar_one() == 'InnoDB'
        assert db.execute(text('SELECT count(*) FROM plc_facts_history')).scalar_one() == 0
        assert db.execute(text('SELECT count(*) FROM plc_facts_latest')).scalar_one() == 0
        return {'profile':profile, 'now':info[3], 'suffix':uuid4().hex}
    finally:
        db.rollback()
        db.close()


def sample(target, plc, instance, generation, seq, sample_id=None):
    observed = (target['now'] - timedelta(seconds=1)).replace(tzinfo=timezone(timedelta(hours=8))).isoformat(timespec='microseconds')
    return {'contractVersion':'plc-facts/v2', 'instanceId':instance,
            'sampleId':sample_id or 'sample-' + uuid4().hex, 'plcId':plc, 'dbNumber':21,
            'sourceGeneration':generation, 'sourceSeq':str(seq),
            'points':[{'pointId':'counter','dataType':'INT','value':42,'quality':'good','observedAt':observed}]}


def wire(body):
    return json.dumps(body, ensure_ascii=False, separators=(',', ':')).encode()


def expected_source(source):
    return {'instanceId':source['instanceId'], 'sourceGeneration':source['sourceGeneration'],
            'registrationRevision':source['registrationRevision']}


def assert_receipt(response, body, outcome):
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('application/json')
    result = response.json()
    assert result['code'] == 200 and result['message'] == 'success'
    assert result['data'] == {'contractVersion': 'plc-facts/v2', 'instanceId': body['instanceId'],
                              'sampleId': body['sampleId'], 'status': 'committed', 'outcome': outcome}


@pytest.mark.asyncio
async def test_two_running_apis_register_commit_takeover_and_serialize(target, monkeypatch):
    """HTTP 真实进程跨实例可见；并发部分让真实采样事务在绑定锁内受控等待。"""
    plc, inst = 'plc/' + target['suffix'], 'third-' + target['suffix']
    generation = 'gen-old-' + target['suffix']
    admin = {'Authorization':'Bearer ' + os.environ['ACQ004_TEST_ADMIN_TOKEN']}
    user = {'Authorization':'Bearer ' + os.environ['ACQ004_TEST_USER_TOKEN']}
    path = '/api/v1/admin/acquisition-sources'
    async with AsyncClient(base_url='http://127.0.0.1:' + http_a, timeout=15, trust_env=False) as a, \
               AsyncClient(base_url='http://127.0.0.1:' + http_b, timeout=15, trust_env=False) as b:
        assert (await a.get(path)).status_code == 401
        assert (await a.get(path, headers=user)).status_code == 403
        first = sample(target, plc, inst, generation, 1)
        payload = wire(first)
        for client in (a, b):
            denied = await client.post('/api/v1/integration/plc-facts/samples', content=payload,
                                       headers={'Content-Type':'application/json'})
            assert denied.status_code == 403 and denied.json()['errorCode'] == 'plc_facts_v2.scope_rejected'
        created = await a.post(path, headers=admin, json={'sourceType':'external', 'plcId':plc,
            'instanceId':inst, 'sourceGeneration':generation})
        assert created.status_code == 200 and created.json()['data']['outcome'] == 'created'
        source = created.json()['data']['source']
        first_result = await b.post('/api/v1/integration/plc-facts/samples', content=payload, headers={'Content-Type':'application/json'})
        assert_receipt(first_result, first, 'created')
        repeat = await a.post('/api/v1/integration/plc-facts/samples', content=payload, headers={'Content-Type':'application/json'})
        assert_receipt(repeat, first, 'duplicate')
        # Same registered source can submit another DB and a DAA label does not require optional fields.
        other_db = {**sample(target, plc, inst, generation, 1), 'dbNumber':22}
        assert_receipt(await a.post('/api/v1/integration/plc-facts/samples', json=other_db), other_db, 'created')
        second_plc = plc + '-B'
        second_generation = 'gen-b-' + target['suffix']
        other = {'sourceType':'daa', 'plcId':second_plc, 'instanceId':inst, 'sourceGeneration':second_generation}
        assert (await a.post(path, headers=admin, json=other)).status_code == 200
        # The same generation string can be used by a different PLC.
        assert (await a.post(path, headers=admin, json={**other, 'plcId':plc + '-C',
                                                      'sourceGeneration':generation})).status_code == 200
        for number in (21, 22):
            body = {**sample(target, second_plc, inst, second_generation, 1), 'dbNumber':number}
            response = await b.post('/api/v1/integration/plc-facts/samples', json=body)
            assert_receipt(response, body, 'created')
        for field, wrong in (('instanceId', 'wrong'), ('plcId', 'unknown-' + target['suffix']),
                             ('sourceGeneration', second_generation)):
            rejected = await b.post('/api/v1/integration/plc-facts/samples', json={**first, field: wrong})
            assert rejected.status_code == 403 and rejected.json()['errorCode'] == 'plc_facts_v2.scope_rejected'
        for wrong in (0, 65536, True):
            rejected = await b.post('/api/v1/integration/plc-facts/samples', json={**first, 'dbNumber': wrong})
            assert rejected.status_code == 422
        assert (await b.post('/api/v1/integration/plc-facts/samples',
                             json={**first, 'sourceType': 'external'})).status_code == 422
        assert (await b.post('/api/v1/integration/plc-facts/samples',
                             json={**first, 'points': [{**first['points'][0], 'value': 43}]})).status_code == 409
        db = create_sync_session()
        try:
            rows = db.execute(text('SELECT plc_id,db_number,instance_id,source_generation,source_type '
                                   'FROM plc_facts_history WHERE plc_id IN (:one,:two) ORDER BY plc_id,db_number'),
                              {'one': plc.encode(), 'two': second_plc.encode()}).all()
            assert {(bytes(row.plc_id), row.db_number, bytes(row.instance_id), bytes(row.source_generation), row.source_type)
                    for row in rows} == {
                (plc.encode(), 21, inst.encode(), generation.encode(), 'external'),
                (plc.encode(), 22, inst.encode(), generation.encode(), 'external'),
                (second_plc.encode(), 21, inst.encode(), second_generation.encode(), 'daa'),
                (second_plc.encode(), 22, inst.encode(), second_generation.encode(), 'daa')}
        finally:
            db.rollback()
            db.close()
        options = await a.get('/api/v1/acquisition-data/options')
        assert options.status_code == 200
        found = {item['plcId']:item['dbNumbers'] for item in options.json()['data']['items']}
        assert found[plc] == found[second_plc] == [21, 22]
        assert plc + '-C' not in found
        assert (await b.get('/api/v1/acquisition-data/latest', params={'plcId':plc, 'dbNumber':99})).json()['data']['items'] == []
        assert (await b.get('/api/v1/acquisition-data/latest', params={'plcId':'unknown-' + target['suffix'], 'dbNumber':21})).status_code == 403
        live = await b.get('/api/v1/acquisition-data/latest', params={'plcId':plc,'dbNumber':21})
        assert live.status_code == 200 and live.json()['data']['items'][0]['value'] == 42
        edit = {'action':'edit','plcId':plc,'expected':expected_source(source), 'sourceType':'daa'}
        changed = await a.patch(path, headers=admin, json=edit)
        assert changed.status_code == 200 and changed.json()['data']['outcome'] == 'updated'
        source = changed.json()['data']['source']
        assert (await a.patch(path, headers=admin, json=edit)).status_code == 409
        stale = expected_source(source)
        replacement = {'sourceType':'external','instanceId':'next-' + target['suffix'],
                       'sourceGeneration':'gen-new-' + target['suffix']}
        request = {'action':'takeover','plcId':plc,'expected':stale,'replacement':replacement,'confirmTakeover':True}
        invalid = await a.patch(path, headers=admin, json={**request,'confirmTakeover':False})
        assert invalid.status_code == 422
        conflict = await a.patch(path, headers=admin, json={**request,'replacement':{**replacement,'sourceGeneration':generation}})
        assert conflict.status_code == 409 and conflict.json()['errorCode'] == 'acquisition_sources.generation_reused'

        reached, release = asyncio.Event(), asyncio.Event()
        original_insert = facts_crud.insert_sample
        async def held_insert(*args, **kwargs):
            await original_insert(*args, **kwargs)
            reached.set()
            await asyncio.wait_for(release.wait(), timeout=10)
        monkeypatch.setattr(facts_crud, 'insert_sample', held_insert)
        second = sample(target, plc, inst, generation, 2)
        parsed, document, digest = parse_sample(wire(second))
        async def write():
            session = await get_db_session()
            try: return await facts_service.write_sample(session, target['profile'], parsed, document, digest, {})
            finally: await session.close()
        async def takeover():
            session = await get_db_session()
            try: return await registry_service.update(session, target['profile'], UpdateIn.model_validate(request))
            finally: await session.close()
        writer = asyncio.create_task(write())
        try:
            await asyncio.wait_for(reached.wait(), timeout=10)
            updater = asyncio.create_task(takeover())
            await asyncio.sleep(0.2)
            assert not updater.done()
            release.set()
            assert (await asyncio.wait_for(writer, timeout=10))['data']['outcome'] == 'created'
            outcome, replacement_source, _ = await asyncio.wait_for(updater, timeout=10)
            assert outcome == 'replaced' and replacement_source['sourceGeneration'] == replacement['sourceGeneration']
        finally:
            release.set()
        monkeypatch.setattr(facts_crud, 'insert_sample', original_insert)
        denied = await b.post('/api/v1/integration/plc-facts/samples', content=wire(sample(target, plc, inst, generation, 3)), headers={'Content-Type':'application/json'})
        assert denied.status_code == 403
        newer = sample(target, plc, replacement['instanceId'], replacement['sourceGeneration'], 1)
        accepted = await a.post('/api/v1/integration/plc-facts/samples', content=wire(newer), headers={'Content-Type':'application/json'})
        assert_receipt(accepted, newer, 'created')
        newer_db22 = {**sample(target, plc, replacement['instanceId'], replacement['sourceGeneration'], 1), 'dbNumber': 22}
        assert_receipt(await b.post('/api/v1/integration/plc-facts/samples', json=newer_db22), newer_db22, 'created')
        # After takeover the two PLCs have different instances; both DBs must retain their own identity.
        for current_plc, current_instance, current_generation in (
            (plc, replacement['instanceId'], replacement['sourceGeneration']),
            (second_plc, inst, second_generation),
        ):
            for number in (21, 22):
                response = await b.get('/api/v1/acquisition-data/latest', params={'plcId': current_plc, 'dbNumber': number})
                assert response.status_code == 200 and len(response.json()['data']['items']) == 1
                point = response.json()['data']['items'][0]
                assert (point['instanceId'], point['sourceGeneration']) == (current_instance, current_generation)
        live = await b.get('/api/v1/acquisition-data/latest', params={'plcId':plc,'dbNumber':21})
        assert live.json()['data']['items'][0]['instanceId'] == replacement['instanceId']
        start = (target['now'] - timedelta(minutes=2)).replace(tzinfo=timezone(timedelta(hours=8))).isoformat()
        end = (target['now'] + timedelta(minutes=2)).replace(tzinfo=timezone(timedelta(hours=8))).isoformat()
        history = await a.get('/api/v1/acquisition-data/history', params={'plcId':plc,'dbNumber':21,'from':start,'to':end})
        assert history.status_code == 200 and history.json()['data']['total'] == 3
        assert {item['sourceType'] for item in history.json()['data']['items']} == {'external', 'daa'}
        page = await b.get('/api/v1/acquisition-data/history', params={'plcId':plc,'dbNumber':21,'from':start,'to':end,'pageSize':1})
        assert page.status_code == 200 and page.json()['data']['total'] == 3 and len(page.json()['data']['items']) == 1
        detail_id = page.json()['data']['items'][0]['id']
        assert (await b.get('/api/v1/acquisition-data/history/' + detail_id)).status_code == 200
        assert (await b.get('/api/v1/acquisition-data/history/9223372036854775807')).status_code == 404
        target.update(plc=plc, source=replacement_source)


@pytest.mark.asyncio
async def test_first_registration_rejects_preexisting_history_or_latest_generation(target):
    """前驱留下无活跃绑定的事实或水位时，登记不得复用可核到的代次。"""
    assert 'plc' in target
    suffix = target['suffix']
    seed = target['plc'].encode()
    history_plc, latest_plc = ('history-only-' + suffix).encode(), ('latest-only-' + suffix).encode()
    instance, generation = ('legacy-' + suffix).encode(), ('legacy-generation-' + suffix).encode()
    db = create_sync_session()
    try:
        history = db.execute(text('INSERT INTO plc_facts_history '
            '(instance_id,sample_id,plc_id,db_number,group_id,config_revision,source_generation,source_seq,'
            'points_json,content_hash,sampled_at,stored_at,expires_at,source_type) '
            'SELECT :instance,:sample,:plc,db_number,group_id,config_revision,:generation,source_seq,'
            'points_json,content_hash,sampled_at,stored_at,expires_at,source_type FROM plc_facts_history '
            'WHERE plc_id=:seed LIMIT 1'), {'instance':instance, 'sample':('legacy-sample-' + suffix).encode(),
                                           'plc':history_plc, 'generation':generation, 'seed':seed})
        latest = db.execute(text('INSERT INTO plc_facts_latest '
            '(plc_id,db_number,point_id,point_name,data_type,value_json,quality,reason,observed_at,expires_at,'
            'instance_id,source_generation,source_seq,sample_id) '
            'SELECT :plc,db_number,point_id,point_name,data_type,value_json,quality,reason,observed_at,expires_at,'
            ':instance,:generation,source_seq,sample_id FROM plc_facts_latest WHERE plc_id=:seed LIMIT 1'),
            {'plc':latest_plc, 'instance':instance, 'generation':generation, 'seed':seed})
        assert history.rowcount == latest.rowcount == 1
        db.commit()
    finally:
        db.close()
    admin = {'Authorization':'Bearer ' + os.environ['ACQ004_TEST_ADMIN_TOKEN']}
    async with AsyncClient(base_url='http://127.0.0.1:' + http_a, timeout=15, trust_env=False) as client:
        for plc in (history_plc.decode(), latest_plc.decode()):
            body = {'sourceType':'external', 'instanceId':'replacement-' + suffix, 'plcId':plc,
                    'sourceGeneration':generation.decode()}
            rejected = await client.post('/api/v1/admin/acquisition-sources', headers=admin, json=body)
            assert rejected.status_code == 409 and rejected.json()['errorCode'] == 'acquisition_sources.generation_reused'
            body['sourceGeneration'] = 'fresh-' + suffix
            accepted = await client.post('/api/v1/admin/acquisition-sources', headers=admin, json=body)
            assert accepted.status_code == 200 and accepted.json()['data']['outcome'] == 'created'
            repeated = await client.post('/api/v1/admin/acquisition-sources', headers=admin, json=body)
            assert repeated.status_code == 200 and repeated.json()['data']['outcome'] == 'unchanged'


def test_retired_generation_and_wrong_target_guard(target):
    """接管保留退役代次；错误目标拒绝，隔离恢复演练需单独执行。"""
    assert 'plc' in target
    db = create_sync_session()
    try:
        row = db.execute(text('SELECT source_generation, retired_generations FROM plc_source_registry WHERE plc_id=:plc'),
                         {'plc':target['plc'].encode()}).one()
        retired = json.loads(row[1]) if isinstance(row[1], str) else row[1]
        assert row[0].decode() == target['source']['sourceGeneration']
        assert 'gen-old-' + target['suffix'] in retired
        wrong = {**target['profile']['target'], 'schema':guard_schema}
        with pytest.raises(Exception):
            target_now(db, wrong)
    finally:
        db.rollback()
        db.close()


# The migration tests use five separately prebuilt, disposable predecessor schemas.
# They never create a database or clean an existing one and are opt-in independently.
R2_REVISION = '6a8c0e2b4d16'
PREDECESSOR_REVISION = '5f7a9c1e3b25'
LEGACY_TABLES = ('acq_source_instances', 'acq_source_bindings', 'acq_source_generations',
                 'acq_source_write_scopes', 'acq_source_read_scopes', 'acq_source_initialization')
LEGACY_ORDER = ('instance_id', 'plc_id', 'plc_id,source_generation', 'plc_id,db_number',
                'plc_id,db_number', 'id')
FACT_ORDER = {'plc_facts_history': 'id', 'plc_facts_latest': 'plc_id,db_number,point_id'}
FROZEN_R2_FILES = {
    'app/plc_facts/v2_config.py': '9bbe7951890cf20e2468223cd608b8f23541114eaa099b1163d40dbc05d6b905',
    'app/plc_facts/models/source_registry.py': 'ba56736e62a4ea2a9e2aa589dd7a99b8b8d9043818f9e7b7c39814b19d0991c8',
    'app/plc_facts/crud/sync_v2_maintenance.py': '5f54b494a282b752889e0c6865dbb6eff8a3278fc213c6262c2ebba175bd8627',
    'app/plc_facts/services/sync_source_registry_import.py': '2c9442952dc67fb9c363c770c92c27e4a6f8f5e7e5c54a3a37a3d85c69189968',
    'scripts/plc_facts_maintenance/main.py': 'ce6d0af960edd5ec90fbb110194cd160b042fbc47c8b52c3308d709a1550fa14',
    'scripts/plc_facts_maintenance/source_registry.py': 'cb5a066a317ac374fb97b547f8c079a0ff9b0162a50edc838bd3dd049b9c332a',
    'alembic/versions/20261113_0800_6a8c0e2b4d16_acquisition_source_registry.py': 'e9a303628efea7fc312d27999868a4523d0886dff1e1b55b664688ec1f065924',
}


def _revision(conn):
    return list(conn.execute(text('SELECT version_num FROM alembic_version')).scalars())


def _objects(conn):
    return set(conn.execute(text('SELECT TABLE_NAME FROM information_schema.TABLES '
                                 'WHERE TABLE_SCHEMA=DATABASE()')).scalars())


def _facts(conn):
    """Independent column and full-row comparison, including each latest watermark."""
    result = {}
    for table, ordering in FACT_ORDER.items():
        columns = conn.execute(text('SELECT COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_DEFAULT,EXTRA '
                                    'FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() '
                                    'AND TABLE_NAME=:name ORDER BY ORDINAL_POSITION'), {'name': table}).all()
        rows = conn.exec_driver_sql(f'SELECT * FROM `{table}` ORDER BY {ordering}').all()
        result[table] = (columns, rows)
    return result


def _legacy(conn):
    return {table: conn.exec_driver_sql(f'SELECT * FROM `{table}` ORDER BY {ordering}').all()
            for table, ordering in zip(LEGACY_TABLES, LEGACY_ORDER)}


def _record_registry(conn):
    bindings = conn.execute(text(
        'SELECT b.plc_id,b.instance_id,b.source_generation,i.source_type,b.registration_revision,b.created_at,b.updated_at '
        'FROM acq_source_bindings b JOIN acq_source_instances i ON i.instance_id=b.instance_id ORDER BY b.plc_id'
    )).all()
    generations = conn.execute(text(
        'SELECT plc_id,source_generation,instance_id FROM acq_source_generations ORDER BY plc_id,source_generation'
    )).all()
    return bindings, generations


def _verify_registry(conn, before):
    bindings, generations = before
    rows = conn.execute(text(
        'SELECT plc_id,instance_id,source_generation,source_type,registration_revision,created_at,updated_at,retired_generations '
        'FROM plc_source_registry ORDER BY plc_id'
    )).all()
    assert [tuple(row[:7]) for row in rows] == [tuple(row) for row in bindings]
    for row in rows:
        previous = json.loads(row[7]) if isinstance(row[7], str) else row[7]
        expected_previous = sorted(bytes(generation).decode('utf-8') for plc, generation, _ in generations
                                   if plc == row[0] and generation != row[2])
        assert sorted(previous) == expected_previous
        assert any(plc == row[0] and generation == row[2] and instance == row[1]
                   for plc, generation, instance in generations)


def _private_json(path, value):
    data = (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'wb') as stream:
        stream.write(data)
    return hashlib.sha256(data).hexdigest()


def _child_env(name, artifact_dir, module_backend):
    """Pass synthetic settings explicitly; no project dotenv or inherited target settings."""
    return {
        'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'TZ': 'Asia/Shanghai',
        'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONPATH': str(module_backend),
        'APP_NAME': 'fixture', 'APP_VERSION': '1', 'API_V1_PREFIX': '/api/v1', 'DEBUG': 'false',
        'TESTING': 'true', 'DATABASE_TYPE': 'mysql', 'MYSQL_HOST': '127.0.0.1', 'MYSQL_PORT': mysql_port,
        'MYSQL_USER': os.environ['ACQ004_TEST_DDL_USER'], 'MYSQL_PASSWORD': os.environ['ACQ004_TEST_DDL_PASSWORD'],
        'MYSQL_DATABASE': 'unused_synthetic_primary', 'TEST_MYSQL_DATABASE': name,
        'MYSQL_ROOT_USER': 'unused', 'MYSQL_ROOT_PASSWORD': 'unused',
        'JWT_SECRET_KEY': 'synthetic', 'JWT_ALGORITHM': 'HS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '15', 'REFRESH_TOKEN_EXPIRE_DAYS': '1',
        'LOG_DIR': str(artifact_dir / 'logs'),
        'ACQ_REGISTRY_EXPECTED_SERVER_UUID': server_uuid, 'ACQ_REGISTRY_EXPECTED_SCHEMA': name,
    }


def _command(argv, cwd, env, evidence, label):
    completed = subprocess.run(argv, cwd=cwd, env=env, text=True, capture_output=True, timeout=120, check=False)
    path = evidence / (label + '.log')
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
        stream.write(completed.stdout)
        stream.write('\n--- stderr ---\n')
        stream.write(completed.stderr)
    return completed


def _upgrade(case, revision, expect_success=True, confirm_empty=False):
    env = _child_env(case['name'], case['evidence'], backend)
    if confirm_empty:
        env['ACQ_REGISTRY_R3_EMPTY_CONFIRMED'] = '1'
    label = f"{case['name']}-{revision}-{'success' if expect_success else 'failure'}"
    result = _command([sys.executable, '-m', 'alembic', 'upgrade', revision], backend, env, case['evidence'], label)
    assert (result.returncode == 0) == expect_success, f'upgrade outcome differs; inspect private {label}.log'
    if expect_success and revision == REVISION:
        events = [json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
        checks = {event['event']: event['tables'] for event in events if event.get('event') in ('facts-before', 'facts-after')}
        assert set(checks) == {'facts-before', 'facts-after'} and checks['facts-before'] == checks['facts-after']
    return result


def _seed_facts(case):
    """Synthetic data includes a DB not previously readable and a read-only orphan PLC."""
    with case['engine'].begin() as conn:
        now = conn.execute(text('SELECT CURRENT_TIMESTAMP(6)')).scalar_one()
        observed, expires = now - timedelta(seconds=30), now + timedelta(days=20)
        for index, (plc, db_number) in enumerate((('PLC-甲', 21), ('PLC-甲', 22), ('PLC-孤', 23)), start=1):
            points = json.dumps([{'pointId': 'counter', 'dataType': 'INT', 'value': 40 + index,
                                  'quality': 'good', 'observedAt': observed.replace(
                                      tzinfo=timezone(timedelta(hours=8))).isoformat(timespec='microseconds')}],
                                ensure_ascii=False, separators=(',', ':'))
            params = {'instance': 'shared-实例'.encode(), 'sample': f'fixture-{index}'.encode(),
                      'plc': plc.encode(), 'db': db_number, 'generation': b'gen-current', 'seq': index,
                      'points': points, 'digest': hashlib.sha256(points.encode()).digest(),
                      'observed': observed, 'stored': now, 'expires': expires}
            conn.execute(text('INSERT INTO plc_facts_history '
                '(instance_id,sample_id,plc_id,db_number,group_id,config_revision,source_generation,source_seq,'
                'points_json,content_hash,sampled_at,stored_at,expires_at,source_type) '
                'VALUES (:instance,:sample,:plc,:db,NULL,NULL,:generation,:seq,:points,:digest,:observed,:stored,:expires,:kind)'),
                {**params, 'kind': None if index == 3 else 'daa'})
            if index != 3:
                conn.execute(text('INSERT INTO plc_facts_latest '
                    '(plc_id,db_number,point_id,point_name,data_type,value_json,quality,reason,observed_at,expires_at,'
                    'instance_id,source_generation,source_seq,sample_id) '
                    'VALUES (:plc,:db,:point,:name,:type,:value,:quality,NULL,:observed,:expires,:instance,:generation,:seq,:sample)'),
                    {**params, 'point': b'counter', 'name': 'Counter', 'type': 'INT', 'value': str(40 + index), 'quality': 'good'})
        # Expired values may be cleared while their exact generation/sequence watermark remains.
        conn.execute(text('INSERT INTO plc_facts_latest '
            '(plc_id,db_number,point_id,instance_id,source_generation,source_seq) '
            'VALUES (:plc,24,:point,:instance,:generation,99)'),
            {'plc': 'PLC-甲'.encode(), 'point': b'cleared', 'instance': 'shared-实例'.encode(), 'generation': b'gen-old'})


def _legacy_profile(name):
    return {'target': {'alias': alias, 'serverUuid': server_uuid, 'schema': name, 'schemaRevision': PREDECESSOR_REVISION},
            'instances': [{'instanceId': 'shared-实例', 'sourceType': 'daa'}],
            'sources': [{'plcId': 'PLC-甲', 'instanceId': 'shared-实例', 'sourceGeneration': 'gen-current', 'dbNumbers': [21, 22]}],
            'readScopes': {'old': [{'plcId': 'PLC-甲', 'dbNumbers': [21]}, {'plcId': 'PLC-孤', 'dbNumbers': [23]}]}}


def _r2_import(case, frozen_backend):
    """Execute the actual frozen r2 preview and explicitly confirmed import."""
    profile_file = case['evidence'] / (case['name'] + '-target.json')
    source_file = case['evidence'] / (case['name'] + '-legacy.json')
    _private_json(profile_file, {'target': {**_legacy_profile(case['name'])['target'], 'schemaRevision': R2_REVISION}})
    digest = _private_json(source_file, _legacy_profile(case['name']))
    env = _child_env(case['name'], case['evidence'], frozen_backend)
    env.update(PLC_FACTS_V2_PROFILE_FILE=str(profile_file), PLC_FACTS_MAINTENANCE_ENABLED='true')
    common = [sys.executable, 'scripts/plc_facts_maintenance/main.py', 'import-sources',
              '--target-alias', alias, '--schema', case['name'], '--expected-server-uuid', server_uuid,
              '--expected-schema-revision', R2_REVISION, '--operation-approval', 'fixture-operation',
              '--confirmed-by', 'fixture-operator', '--source-file', str(source_file)]
    preview = _command([*common, '--plan'], frozen_backend, env, case['evidence'], case['name'] + '-preview')
    assert preview.returncode == 0, 'r2 preview failed; inspect private log'
    events = [json.loads(line) for line in preview.stdout.splitlines() if line.startswith('{')]
    assert any(event.get('result', {}).get('outcome') == 'preview' and
               event['result'].get('sourceSha256') == digest for event in events)
    confirm = f"IMPORT:{alias}:{case['name']}:{server_uuid}:{digest}"
    applied = _command([*common, '--apply', '--expected-source-sha256', digest, '--confirm', confirm],
                       frozen_backend, env, case['evidence'], case['name'] + '-import')
    assert applied.returncode == 0, 'r2 import failed; inspect private log'
    events = [json.loads(line) for line in applied.stdout.splitlines() if line.startswith('{')]
    assert any(event.get('result', {}).get('outcome') == 'created' for event in events)
    return profile_file


def _r2_export(case, frozen_backend, profile_file):
    env = _child_env(case['name'], case['evidence'], frozen_backend)
    env['PLC_FACTS_V2_PROFILE_FILE'] = str(profile_file)
    output_file = case['evidence'] / (case['name'] + '-export.json')
    command = [sys.executable, 'scripts/plc_facts_maintenance/main.py', 'export-sources',
               '--target-alias', alias, '--schema', case['name'], '--expected-server-uuid', server_uuid,
               '--expected-schema-revision', R2_REVISION, '--operation-approval', 'fixture-operation',
               '--confirmed-by', 'fixture-operator', '--restore-alias', alias + '-restore',
               '--restore-schema', restore_schema, '--restore-server-uuid', server_uuid,
               '--output-file', str(output_file)]
    result = _command(command, frozen_backend, env, case['evidence'], case['name'] + '-export')
    assert result.returncode == 0, 'r2 export failed; inspect private log'
    material = json.loads(output_file.read_text())
    assert material['summary']['bindingCount'] == 1
    assert any(row['plcId'] == 'PLC-甲' and row['sourceGeneration'] == 'gen-old'
               for row in material['generations'])
    return material


@pytest.fixture(scope='module')
def migration_targets():
    suffix = match.group(1)
    names = {key: f'arch_acq004_r3_{suffix}_{key}' for key in ('initialized', 'json', 'empty', 'failure', 'restore')}
    assert names['restore'] == restore_schema and len({schema, guard_schema, *names.values()}) == 7
    confirmation = ':'.join(('MIGRATE', alias, server_uuid, mysql_port, *(names[key] for key in names)))
    if os.environ.get('ACQ004_TEST_MIGRATION_CONFIRM') != confirmation:
        pytest.skip('explicit five-schema migration confirmation required')
    frozen_value = os.environ.get('ACQ004_TEST_FROZEN_R2_ROOT', '')
    frozen = Path(frozen_value).resolve(strict=True) if frozen_value else None
    if (frozen is None or frozen.parent != owned_root or frozen.name != 'frozen-r2'
            or (frozen / 'backend' / '.env').exists()
            or (frozen / 'backend' / 'scripts/plc_facts_maintenance/.env').exists()):
        raise RuntimeError('dedicated frozen r2 source required')
    frozen_backend = frozen / 'backend'
    for relative, digest in FROZEN_R2_FILES.items():
        path = frozen_backend / relative
        if path.is_symlink() or not path.resolve(strict=True).is_relative_to(frozen_backend):
            raise RuntimeError('frozen r2 project source must be a private copy')
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('frozen r2 source differs from approved predecessor baseline')
    url = make_url(settings.SYNC_DATABASE_URL)
    assert url.host == '127.0.0.1' and url.port == int(mysql_port)
    engines = {}
    try:
        for key, name in names.items():
            target_url = url.set(database=name, username=os.environ['ACQ004_TEST_DDL_USER'],
                                 password=os.environ['ACQ004_TEST_DDL_PASSWORD'])
            engine = create_engine(target_url, poolclass=NullPool,
                                   connect_args={'connect_timeout': 2, 'read_timeout': 15, 'write_timeout': 15})
            engines[key] = engine
            # Complete all read-only target and emptiness checks before any test starts a migration.
            with engine.connect() as conn:
                info = conn.execute(text('SELECT @@server_uuid,DATABASE(),VERSION(),CURRENT_USER(),'
                                         'TIMESTAMPDIFF(SECOND,UTC_TIMESTAMP(6),CURRENT_TIMESTAMP(6))')).one()
                assert (str(info[0]).lower(), info[1], info[2].split('-')[0], info[3].split('@', 1)[0], info[4]) == (
                    server_uuid, name, '8.4.6', os.environ['ACQ004_TEST_DDL_USER'], 28800)
                assert _revision(conn) == [PREDECESSOR_REVISION]
                objects = _objects(conn)
                assert set(FACT_ORDER).issubset(objects) and not objects.intersection((*LEGACY_TABLES, 'plc_source_registry'))
                assert all(conn.exec_driver_sql(f'SELECT COUNT(*) FROM `{table}`').scalar_one() == 0 for table in FACT_ORDER)
        evidence = Path(tempfile.mkdtemp(prefix='migration-evidence-', dir=owned_root))
        os.chmod(evidence, 0o700)
        yield {key: {'name': names[key], 'engine': engines[key], 'evidence': evidence} for key in names}, frozen_backend
    finally:
        for engine in engines.values():
            engine.dispose()


def _add_retired(case):
    with case['engine'].begin() as conn:
        conn.execute(text('INSERT INTO acq_source_generations (plc_id,source_generation,instance_id) '
                          'VALUES (:plc,:generation,:instance)'),
                     {'plc': 'PLC-甲'.encode(), 'generation': b'gen-old', 'instance': 'shared-实例'.encode()})


def _assert_upgraded(case, facts_before, registry_before):
    with case['engine'].connect() as conn:
        assert _revision(conn) == [REVISION]
        assert not _objects(conn).intersection(LEGACY_TABLES)
        assert 'plc_source_registry' in _objects(conn)
        assert _facts(conn) == facts_before
        _verify_registry(conn, registry_before)


@pytest.mark.parametrize('case_name', ['initialized', 'json', 'empty'])
def test_three_predecessor_migration_paths(migration_targets, case_name):
    cases, frozen = migration_targets
    case = cases[case_name]
    _seed_facts(case)
    _upgrade(case, R2_REVISION)  # Runs the unmodified historical revision from its predecessor.
    with case['engine'].connect() as conn:
        assert _revision(conn) == [R2_REVISION]
        assert set(LEGACY_TABLES).issubset(_objects(conn))
        initial_facts = _facts(conn)
        assert all(not rows for rows in _legacy(conn).values())
    if case_name != 'initialized':
        # Unknown/empty input cannot silently discard a pending JSON registry.
        _upgrade(case, REVISION, expect_success=False)
        with case['engine'].connect() as conn:
            assert _revision(conn) == [R2_REVISION] and 'plc_source_registry' not in _objects(conn)
            assert _facts(conn) == initial_facts
    if case_name != 'empty':
        profile = _r2_import(case, frozen)
        _add_retired(case)
        if case_name == 'initialized':
            _r2_export(case, frozen, profile)
    with case['engine'].connect() as conn:
        before = _record_registry(conn)
        facts_before = _facts(conn)
        if case_name != 'empty':
            read_pairs = set(conn.execute(text('SELECT plc_id,db_number FROM acq_source_read_scopes')).all())
            assert ('PLC-孤'.encode(), 23) in read_pairs
            assert ('PLC-甲'.encode(), 21) in read_pairs and ('PLC-甲'.encode(), 22) not in read_pairs
            assert any(row.plc_id == 'PLC-甲'.encode() and row.db_number == 22 for row in facts_before['plc_facts_history'][1])
    _upgrade(case, REVISION, confirm_empty=(case_name == 'empty'))
    _assert_upgraded(case, facts_before, before)
    with case['engine'].connect() as conn:
        assert conn.execute(text('SELECT COUNT(*) FROM plc_source_registry')).scalar_one() == (0 if case_name == 'empty' else 1)
    asyncio.run(_check_read_visibility(case, case_name == 'empty'))
    if case_name == 'initialized':
        asyncio.run(_check_post_adoption_changes(case, facts_before))


def test_partial_ddl_refuses_and_verified_predecessor_restore(migration_targets):
    cases, frozen = migration_targets
    failed, restored = cases['failure'], cases['restore']
    _seed_facts(failed)
    _upgrade(failed, R2_REVISION)
    _upgrade(restored, R2_REVISION)
    _r2_import(failed, frozen)
    _add_retired(failed)
    with failed['engine'].connect() as conn:
        backup_facts, backup_registry, backup_tables = _facts(conn), _record_registry(conn), _legacy(conn)
    # Restore only into the separately preflighted empty schema; no DROP or overwrite.
    copy_order = (*LEGACY_TABLES, *FACT_ORDER)
    with restored['engine'].begin() as conn:
        assert all(not rows for rows in _legacy(conn).values())
        assert all(not rows for _, rows in _facts(conn).values())
        for table in copy_order:
            conn.exec_driver_sql(f'INSERT INTO `{restored["name"]}`.`{table}` SELECT * FROM `{failed["name"]}`.`{table}`')
    with restored['engine'].connect() as conn:
        assert _facts(conn) == backup_facts and _legacy(conn) == backup_tables
        assert _record_registry(conn) == backup_registry
    # Reproduce a partially committed CREATE TABLE and prove the migration refuses blind retry.
    from app.plc_facts.models.source_registry import PlcSourceRegistry
    with failed['engine'].begin() as conn:
        PlcSourceRegistry.__table__.create(conn, checkfirst=False)
    _upgrade(failed, REVISION, expect_success=False)
    with failed['engine'].connect() as conn:
        assert _revision(conn) == [R2_REVISION] and 'plc_source_registry' in _objects(conn)
        assert _facts(conn) == backup_facts and _legacy(conn) == backup_tables
        assert conn.execute(text('SELECT COUNT(*) FROM plc_source_registry')).scalar_one() == 0
    # The predecessor backup is migrated independently after the original partial state is preserved.
    _upgrade(restored, REVISION)
    _assert_upgraded(restored, backup_facts, backup_registry)


async def _check_read_visibility(case, empty):
    """Exercise r3 service reads against the migrated case with the real async driver."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from app.plc_facts.v2_domain import V2Error
    url = make_url(settings.DATABASE_URL).set(database=case['name'], username=os.environ['ACQ004_TEST_DDL_USER'],
                                              password=os.environ['ACQ004_TEST_DDL_PASSWORD'])
    engine = create_async_engine(url, poolclass=NullPool, connect_args={'connect_timeout': 2})
    maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    profile = {'target': {'alias': alias, 'serverUuid': server_uuid, 'schema': case['name'], 'schemaRevision': REVISION}}
    try:
        with case['engine'].connect() as conn:
            now = conn.execute(text('SELECT CURRENT_TIMESTAMP(6)')).scalar_one()
            orphan_id = conn.execute(text('SELECT id FROM plc_facts_history WHERE plc_id=:plc'),
                                     {'plc': 'PLC-孤'.encode()}).scalar_one()
        async with maker() as db:
            options = await facts_service.options(db, profile)
            if empty:
                assert options['items'] == []
                with pytest.raises(V2Error) as missing:
                    await facts_service.latest(db, profile, 'PLC-甲', 21)
                assert missing.value.status == 403
            else:
                assert options['items'] == [{'plcId': 'PLC-甲', 'dbNumbers': [21, 22]}]
                old_unreadable_db = await facts_service.latest(db, profile, 'PLC-甲', 22)
                assert len(old_unreadable_db['items']) == 1 and old_unreadable_db['items'][0]['value'] == 42
                assert (await facts_service.latest(db, profile, 'PLC-甲', 99))['items'] == []
                result = await facts_service.history(db, profile, 'PLC-甲', None,
                                                     now - timedelta(minutes=5), now + timedelta(minutes=5), 1, 50)
                assert result['total'] == 2 and {row['dbNumber'] for row in result['items']} == {21, 22}
                with pytest.raises(V2Error) as denied:
                    await facts_service.latest(db, profile, 'PLC-孤', 23)
                assert denied.value.status == 403
            with pytest.raises(V2Error) as hidden:
                await facts_service.detail(db, profile, orphan_id)
            assert hidden.value.status == 404
    finally:
        await engine.dispose()


async def _check_post_adoption_changes(case, backup_facts):
    """保全新登记和事实，验证不能用 r2 表达时不执行破坏性回退。"""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from app.plc_facts.schemas.source_registry import RegistrationIn
    url = make_url(settings.DATABASE_URL).set(database=case['name'], username=os.environ['ACQ004_TEST_DDL_USER'],
                                              password=os.environ['ACQ004_TEST_DDL_PASSWORD'])
    engine = create_async_engine(url, poolclass=NullPool, connect_args={'connect_timeout': 2})
    maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    profile = {'target': {'alias': alias, 'serverUuid': server_uuid, 'schema': case['name'], 'schemaRevision': REVISION}}
    try:
        with case['engine'].connect() as conn:
            now = conn.execute(text('SELECT CURRENT_TIMESTAMP(6)')).scalar_one()
        body = RegistrationIn.model_validate({'plcId': 'PLC-乙', 'instanceId': 'shared-实例',
                                               'sourceGeneration': 'gen-new', 'sourceType': 'external'})
        async with maker() as db:
            outcome, source = await registry_service.register(db, profile, body)
            assert outcome == 'created' and source['plcId'] == 'PLC-乙'
            submitted = sample({'now': now}, 'PLC-乙', 'shared-实例', 'gen-new', 1)
            parsed, document, digest = parse_sample(wire(submitted))
            receipt = await facts_service.write_sample(db, profile, parsed, document, digest, {})
            assert receipt['data']['outcome'] == 'created' and receipt['data']['sampleId'] == submitted['sampleId']
        with case['engine'].connect() as conn:
            after = _facts(conn)
            registrations = conn.execute(text('SELECT instance_id,source_type FROM plc_source_registry ORDER BY plc_id')).all()
        for table in FACT_ORDER:
            assert after[table][0] == backup_facts[table][0]
            assert all(row in after[table][1] for row in backup_facts[table][1])
            assert len(after[table][1]) > len(backup_facts[table][1])
        # r2 stores a single source type per instance.  This r3 state cannot be
        # expressed by that predecessor without losing information; no restore is attempted.
        by_instance = {}
        conflict = False
        for instance, source_type in registrations:
            key = bytes(instance)
            conflict |= key in by_instance and by_instance[key] != source_type
            by_instance[key] = source_type
        assert conflict
        with case['engine'].connect() as conn:
            assert _revision(conn) == [REVISION] and _facts(conn) == after
            assert conn.execute(text('SELECT COUNT(*) FROM plc_source_registry')).scalar_one() == 2
    finally:
        await engine.dispose()
