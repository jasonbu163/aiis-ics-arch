"""ARCH-BE-012 r4 隔离 MySQL 与真实 loopback HTTP 验证入口。"""
import asyncio
import copy
from datetime import datetime, timedelta
from decimal import Decimal
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4

import pytest
import pytest_asyncio

REQUIRED = ('ARCH_BE012_B_OPERATION_APPROVAL', 'ARCH_BE012_B_TARGET_ALIAS', 'ARCH_BE012_B_SCHEMA',
            'ARCH_BE012_B_SERVER_UUID', 'ARCH_BE012_B_MYSQL_PORT', 'ARCH_BE012_B_HTTP_PORT',
            'ARCH_BE012_B_CONFIRM', 'ARCH_BE012_B_TOKEN', 'PLC_FACTS_V2_PROFILE_FILE')
if any(not os.environ.get(name, '').strip() for name in REQUIRED):
    pytest.skip('ARCH-BE-012 B requires a separately approved disposable target', allow_module_level=True)

root = Path(__file__).resolve().parents[2]
if not str(root).startswith('/private/tmp/arch-be012-r4-') or (root / 'backend/.env').exists():
    raise RuntimeError('B requires its own public temporary source without .env')


def require_copy_imports(backend):
    """任何项目配置或数据库导入前检查本轮源码及工作目录。"""
    if Path.cwd().resolve() != backend.resolve() or Path(__file__).resolve().parents[1] != backend.resolve():
        raise RuntimeError('B requires the isolated backend working directory')
    for name, relative in (('settings', 'settings.py'), ('database', 'database/__init__.py'),
                           ('app', 'app/__init__.py')):
        spec = importlib.util.find_spec(name)
        if spec is None or spec.origin is None or Path(spec.origin).resolve() != (backend / relative).resolve():
            raise RuntimeError('B project imports must resolve to the isolated source')


require_copy_imports(root / 'backend')
schema = os.environ['ARCH_BE012_B_SCHEMA']
alias = os.environ['ARCH_BE012_B_TARGET_ALIAS']
server_uuid = os.environ['ARCH_BE012_B_SERVER_UUID']
mysql_port = os.environ['ARCH_BE012_B_MYSQL_PORT']
http_port = os.environ['ARCH_BE012_B_HTTP_PORT']
rounds = {'13392': ('18392', 'arch-be012-r4-dev', 'arch_be012_r4_dev_'),
          '13393': ('18393', 'arch-be012-r4-qa', 'arch_be012_r4_qa_')}
round_target = rounds.get(mysql_port)
if (round_target is None or (http_port, alias) != round_target[:2] or not schema.startswith(round_target[2])
        or not schema.replace('_', '').isalnum()
        or os.environ.get('MYSQL_HOST') != '127.0.0.1' or os.environ.get('MYSQL_PORT') != mysql_port
        or os.environ.get('TEST_MYSQL_DATABASE') != schema or os.environ.get('MYSQL_DATABASE') == schema
        or os.environ.get('MYSQL_USER', '') in ('', 'root') or os.environ.get('TESTING', '').lower() != 'true'
        or os.environ['ARCH_BE012_B_CONFIRM'] != ':'.join(('RUN', alias, schema, server_uuid, mysql_port, http_port))):
    raise RuntimeError('B target guard rejected configuration')
if any(os.environ.get(name, 'False').lower() != 'false' for name in
       ('BACKEND_MOCK_ENABLED', 'PROJECTION_RUNNER_ENABLED', 'ADMIN_BOOTSTRAP_ENABLED',
        'SUPERVISOR_BOOTSTRAP_ENABLED', 'OPERATOR_BOOTSTRAP_ENABLED')):
    raise RuntimeError('B requires default-off mock, runner and bootstrap')

from httpx import AsyncClient
from sqlalchemy import func, inspect, insert, select, text
from database import create_sync_session, get_db_session
from app.plc_facts.crud.sync_maintenance import verify_profile
from app.plc_facts.crud.sync_v2_maintenance import target_now
from app.plc_facts.models.v2 import LatestPointV2, SampleV2
from app.plc_facts.services import async_v2
from app.plc_facts.v2_config import get_profile
from app.plc_facts.v2_domain import expiry, parse_sample, wire_time

HTTP = 'http://127.0.0.1:' + http_port
TOKEN = os.environ['ARCH_BE012_B_TOKEN']
HEADERS = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TOKEN}
LOAD_SAMPLES_PER_PLC = 1800


@pytest_asyncio.fixture(scope='module', loop_scope='module', autouse=True)
async def dispose_async_pool():
    yield
    from database import async_engine
    await async_engine.dispose()


@pytest.fixture(scope='module')
def target():
    profile = get_profile()
    assert profile['target'] == {'alias': alias, 'schema': schema, 'serverUuid': server_uuid,
                                 'schemaRevision': '2c4e6a8b0d12'}
    db = create_sync_session()
    try:
        now = target_now(db, profile['target'])
        assert db.execute(text('SELECT VERSION()')).scalar_one().split('-')[0] == '8.4.6'
        assert verify_profile(db.connection())['applicationTables'] == 77
        assert len(set(inspect(db.connection()).get_table_names()) - {'alembic_version'}) == 77
        assert db.execute(select(func.count()).select_from(SampleV2)).scalar_one() == 0
        assert db.execute(select(func.count()).select_from(LatestPointV2)).scalar_one() == 0
        db.rollback()
    finally:
        db.close()
    return {'now': now, 'sequence': 0}


def sample(target, *, count=2, plc='PLC-A', number=21, seq=None, identity=None):
    target['sequence'] += 1
    sequence = seq if seq is not None else target['sequence']
    observed = wire_time(target['now'] - timedelta(seconds=1))
    return {'contractVersion': 'plc-facts/v2', 'instanceId': 'daa-a',
            'sampleId': identity or 'sample-' + str(uuid4()), 'plcId': plc, 'dbNumber': number,
            'groupId': 'fixture-group', 'configRevision': 'fixture-revision', 'sourceGeneration': 'gen-a',
            'sourceSeq': str(sequence), 'points': [{'pointId': f'point-{i:03}', 'dataType': 'INT', 'value': i,
                                                   'quality': 'good', 'observedAt': observed} for i in range(count)]}


def body(document):
    return json.dumps(document, ensure_ascii=False, separators=(',', ':')).encode()


def counts():
    db = create_sync_session()
    try:
        result = tuple(db.execute(select(func.count()).select_from(model)).scalar_one()
                       for model in (SampleV2, LatestPointV2))
        db.rollback()
        return result
    finally:
        db.close()


def migration_run(action, revision):
    """限定本轮迁移账号、UUID 和 schema 的显式 Alembic 夹具。"""
    user = os.environ.get('ARCH_BE012_B_MIGRATION_USER', '')
    password = os.environ.get('ARCH_BE012_B_MIGRATION_PASSWORD', '')
    confirmation = ':'.join(('MIGRATE', alias, schema, server_uuid, mysql_port))
    if (not user.startswith('archbe012_') or user == os.environ['MYSQL_USER'] or not password
            or os.environ.get('ARCH_BE012_B_DDL_CONFIRM') != confirmation):
        raise RuntimeError('isolated migration guard rejected configuration')
    db = create_sync_session()
    try:
        target_now(db, get_profile()['target'])
        db.rollback()
    finally:
        db.close()
    environment = dict(os.environ, MYSQL_USER=user, MYSQL_PASSWORD=password, PYTHONPATH=str(root / 'backend'))
    return subprocess.run([sys.executable, '-m', 'alembic', 'downgrade' if action == 'down' else 'upgrade', revision],
                          cwd=root / 'backend', env=environment, capture_output=True, text=True, timeout=30)


def test_empty_downgrade_and_upgrade(target):
    down = migration_run('down', '1b3d5f7a9c20')
    assert down.returncode == 0
    db = create_sync_session()
    try:
        assert db.execute(text('SELECT @@server_uuid')).scalar_one() == server_uuid
        assert db.execute(text('SELECT DATABASE()')).scalar_one() == schema
        assert db.execute(text('SELECT version_num FROM alembic_version')).scalar_one() == '1b3d5f7a9c20'
        assert not {'plc_facts_samples_v2', 'plc_facts_latest_points_v2'} & set(inspect(db.connection()).get_table_names())
        db.rollback()
    finally:
        db.close()
    # 上一 head 的目标校验由该独立迁移子进程和同一连接 UUID 显式确认。
    environment = dict(os.environ, MYSQL_USER=os.environ['ARCH_BE012_B_MIGRATION_USER'],
                       MYSQL_PASSWORD=os.environ['ARCH_BE012_B_MIGRATION_PASSWORD'], PYTHONPATH=str(root / 'backend'))
    up = subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', '2c4e6a8b0d12'],
                        cwd=root / 'backend', env=environment, capture_output=True, text=True, timeout=30)
    assert up.returncode == 0
    db = create_sync_session()
    try:
        target_now(db, get_profile()['target'])
        assert len(set(inspect(db.connection()).get_table_names()) - {'alembic_version'}) == 77
        db.rollback()
    finally:
        db.close()


async def send(client, raw):
    return await client.post('/api/v1/integration/plc-facts/samples', content=raw, headers=HEADERS)


@pytest.mark.asyncio(loop_scope='module')
async def test_samples_limits_and_independent_dbs(target):
    async with AsyncClient(base_url=HTTP, timeout=10, trust_env=False) as client:
        for count in (400, 512):
            response = await send(client, body(sample(target, count=count)))
            assert response.status_code == 200 and response.json()['data']['outcome'] == 'created'
        exact = body(sample(target))
        exact += b' ' * (524288 - len(exact))
        assert (await send(client, exact)).status_code == 200
        before = counts()
        assert (await send(client, exact + b' ')).status_code == 413
        assert (await send(client, body(sample(target, count=513)))).status_code == 422
        assert counts() == before
        sequence = target['sequence'] + 10
        first = body(sample(target, number=21, seq=sequence))
        second = body(sample(target, number=22, seq=sequence))
        assert (await send(client, first)).status_code == 200
        assert (await send(client, second)).status_code == 200


@pytest.mark.asyncio(loop_scope='module')
async def test_duplicate_concurrency_and_conflicts(target):
    raw = body(sample(target))
    async with AsyncClient(base_url=HTTP, timeout=10, trust_env=False) as client:
        replies = await asyncio.gather(*(send(client, raw) for _ in range(4)))
        for index, reply in enumerate(replies):
            if reply.status_code == 503:
                replies[index] = await send(client, raw)
        assert all(reply.status_code == 200 for reply in replies)
        assert sorted(reply.json()['data']['outcome'] for reply in replies) == ['created', 'duplicate', 'duplicate', 'duplicate']
        changed = json.loads(raw)
        changed['points'][0]['value'] += 1
        assert (await send(client, body(changed))).status_code == 409


def test_nonempty_downgrade_is_rejected(target):
    before = counts()
    assert before[0] > 0 and before[1] > 0
    result = migration_run('down', '1b3d5f7a9c20')
    assert result.returncode != 0 and 'nonempty PLC facts v2 tables prohibit downgrade' in result.stderr
    assert counts() == before
    db = create_sync_session()
    try:
        target_now(db, get_profile()['target'])
        db.rollback()
    finally:
        db.close()


@pytest.mark.asyncio(loop_scope='module')
async def test_commit_then_lost_ack_can_be_recovered(target):
    document = sample(target)
    raw = body(document)
    parsed, payload, digest = parse_sample(raw)
    db = await get_db_session()
    original_commit = db.commit
    async def lost_after_commit():
        await original_commit()
        raise ConnectionError('synthetic response loss after commit')
    db.commit = lost_after_commit
    from app.plc_facts.v2_domain import V2Error
    try:
        with pytest.raises(V2Error) as error:
            await async_v2.write_sample(db, get_profile(), parsed, payload, digest, {})
        assert error.value.key == 'plc_facts_v2.commit_outcome_unknown'
    finally:
        await db.close()
    async with AsyncClient(base_url=HTTP, timeout=10, trust_env=False) as client:
        response = await send(client, raw)
        assert response.status_code == 200 and response.json()['data']['outcome'] == 'duplicate'


@pytest.mark.asyncio(loop_scope='module')
async def test_failure_before_commit_rolls_back_both_tables(target):
    document = sample(target, count=1)
    document['points'][0]['pointId'] = 'rollback-point'
    raw = body(document)
    parsed, payload, digest = parse_sample(raw)
    before = counts()
    db = await get_db_session()
    async def fail_before_commit():
        raise ConnectionError('synthetic failure before commit')
    db.commit = fail_before_commit
    from app.plc_facts.v2_domain import V2Error
    try:
        with pytest.raises(V2Error) as error:
            await async_v2.write_sample(db, get_profile(), parsed, payload, digest, {})
        assert error.value.key == 'plc_facts_v2.commit_outcome_unknown'
    finally:
        await db.close()
    assert counts() == before
    async with AsyncClient(base_url=HTTP, timeout=10, trust_env=False) as client:
        retry = await send(client, raw)
        assert retry.status_code == 200 and retry.json()['data']['outcome'] == 'created'


@pytest.mark.asyncio(loop_scope='module')
async def test_http_response_lost_after_observed_commit(target):
    document = sample(target)
    raw = body(document)
    reader, writer = await asyncio.open_connection('127.0.0.1', int(http_port))
    request = (b'POST /api/v1/integration/plc-facts/samples HTTP/1.1\r\nHost: 127.0.0.1\r\n'
               + b'Content-Type: application/json\r\nAuthorization: Bearer ' + TOKEN.encode()
               + b'\r\nContent-Length: ' + str(len(raw)).encode() + b'\r\nConnection: close\r\n\r\n' + raw)
    writer.write(request)
    await writer.drain()
    committed = False
    for _ in range(100):
        db = create_sync_session()
        try:
            committed = bool(db.execute(select(func.count()).select_from(SampleV2).where(
                SampleV2.instance_id == b'daa-a', SampleV2.sample_id == document['sampleId'].encode())).scalar_one())
            db.rollback()
        finally:
            db.close()
        if committed:
            break
        await asyncio.sleep(0.05)
    writer.close()
    await writer.wait_closed()
    assert committed
    async with AsyncClient(base_url=HTTP, timeout=10, trust_env=False) as client:
        replay = await send(client, raw)
        assert replay.status_code == 200 and replay.json()['data']['outcome'] == 'duplicate'


@pytest.mark.asyncio(loop_scope='module')
async def test_order_scope_and_expiry(target):
    newer = sample(target, seq=10002)
    older = sample(target, seq=10001)
    older['points'][0]['value'] = 999
    async with AsyncClient(base_url=HTTP, timeout=10, trust_env=False) as client:
        assert (await send(client, body(newer))).status_code == 200
        assert (await send(client, body(older))).status_code == 200
        unauthorized = await client.post('/api/v1/integration/plc-facts/samples', content=body(sample(target)),
                                         headers={'Content-Type': 'application/json', 'Authorization': 'Bearer wrong'})
        assert unauthorized.status_code == 401
        cross_scope = sample(target, plc='PLC-Z')
        assert (await send(client, body(cross_scope))).status_code == 403
        expired = sample(target)
        for point in expired['points']:
            point['observedAt'] = '2020-01-01T00:00:00+08:00'
        before = counts()
        assert (await send(client, body(expired))).status_code == 410
        assert counts() == before
    db = create_sync_session()
    try:
        row = db.get(LatestPointV2, (b'PLC-A', 21, b'point-000'))
        assert row.source_seq == 10002 and row.value_json == 0
        db.rollback()
    finally:
        db.close()


@pytest.mark.asyncio(loop_scope='module')
async def test_old_and_new_sequences_concurrently_keep_newest(target):
    older = sample(target, count=1, seq=400000)
    newer = sample(target, count=1, seq=400001)
    older['points'][0].update(pointId='concurrent-order', value=1)
    newer['points'][0].update(pointId='concurrent-order', value=2)
    bodies = (body(older), body(newer))
    async with AsyncClient(base_url=HTTP, timeout=10, trust_env=False) as client:
        responses = list(await asyncio.gather(*(send(client, raw) for raw in bodies)))
        for index, response in enumerate(responses):
            if response.status_code == 503:
                responses[index] = await send(client, bodies[index])
        assert all(response.status_code == 200 for response in responses)
    db = create_sync_session()
    try:
        row = db.get(LatestPointV2, (b'PLC-A', 21, b'concurrent-order'))
        assert row.source_seq == 400001 and row.value_json == 2
        for document in (older, newer):
            assert db.execute(select(func.count()).select_from(SampleV2).where(
                SampleV2.instance_id == b'daa-a', SampleV2.sample_id == document['sampleId'].encode())).scalar_one() == 1
        db.rollback()
    finally:
        db.close()


@pytest.mark.asyncio(loop_scope='module')
async def test_read_permissions_and_history(target):
    token = os.environ.get('ARCH_BE012_B_READER_TOKEN', '')
    admin_token = os.environ.get('ARCH_BE012_B_ADMIN_TOKEN', '')
    denied_token = os.environ.get('ARCH_BE012_B_DENIED_TOKEN', '')
    if not all((token, admin_token, denied_token)):
        pytest.fail('approved fixture must provide synthetic reader, unscoped admin and denied tokens')
    async with AsyncClient(base_url=HTTP, timeout=10, trust_env=False) as client:
        assert (await client.get('/api/v1/acquisition-data/options')).status_code == 401
        headers = {'Authorization': 'Bearer ' + token}
        options = await client.get('/api/v1/acquisition-data/options', headers=headers)
        assert options.status_code == 200 and options.json()['data']['items']
        latest = await client.get('/api/v1/acquisition-data/latest', params={'plcId': 'PLC-A', 'dbNumber': 21}, headers=headers)
        assert latest.status_code == 200 and latest.json()['data']['items']
        params = {'plcId': 'PLC-A', 'dbNumber': 21, 'from': wire_time(target['now'] - timedelta(days=1)),
                  'to': wire_time(target['now'] + timedelta(days=1))}
        history = await client.get('/api/v1/acquisition-data/history', params=params, headers=headers)
        assert history.status_code == 200 and history.json()['data']['items']
        identity = history.json()['data']['items'][0]['id']
        detail = await client.get('/api/v1/acquisition-data/history/' + identity, headers=headers)
        assert detail.status_code == 200 and detail.json()['data']['points']
        outside = await client.get('/api/v1/acquisition-data/latest', params={'plcId': 'PLC-A', 'dbNumber': 22}, headers=headers)
        assert outside.status_code == 403
        unscoped = {'Authorization': 'Bearer ' + admin_token}
        assert (await client.get('/api/v1/acquisition-data/options', headers=unscoped)).json()['data']['items'] == []
        assert (await client.get('/api/v1/acquisition-data/latest', params={'plcId': 'PLC-A', 'dbNumber': 21}, headers=unscoped)).status_code == 403
        assert (await client.get('/api/v1/acquisition-data/options', headers={'Authorization': 'Bearer ' + denied_token})).status_code == 403
        db = create_sync_session()
        try:
            outside_id = db.execute(select(SampleV2.id).where(SampleV2.plc_id == b'PLC-A', SampleV2.db_number == 22)).scalar_one()
            db.rollback()
        finally:
            db.close()
        hidden = await client.get('/api/v1/acquisition-data/history/' + str(outside_id), headers=headers)
        missing = await client.get('/api/v1/acquisition-data/history/9223372036854775807', headers=headers)
        assert hidden.status_code == missing.status_code == 404


@pytest.mark.asyncio(loop_scope='module')
async def test_real_precision_through_mysql_and_http(target):
    document = sample(target, count=4)
    tokens = ('1.234567890123456789', '9007199254740993', '-0', '1e-1000000')
    for index, point in enumerate(document['points']):
        point.update(pointId=f'precision-{index}', dataType='REAL', value=0)
    raw = body(document)
    for token in tokens:
        raw = raw.replace(b'"value":0', b'"value":' + token.encode(), 1)
    async with AsyncClient(base_url=HTTP, timeout=10, trust_env=False) as client:
        assert (await send(client, raw)).status_code == 200
        db = create_sync_session()
        try:
            row = db.execute(select(SampleV2).where(SampleV2.instance_id == b'daa-a',
                             SampleV2.sample_id == document['sampleId'].encode())).scalar_one()
            assert [point['value'] for point in row.points_json] == list(tokens)
            identity = row.id
            db.rollback()
        finally:
            db.close()
        headers = {'Authorization': 'Bearer ' + os.environ['ARCH_BE012_B_READER_TOKEN']}
        latest = await client.get('/api/v1/acquisition-data/latest', params={'plcId': 'PLC-A', 'dbNumber': 21}, headers=headers)
        detail = await client.get('/api/v1/acquisition-data/history/' + str(identity), headers=headers)
        for response in (latest, detail):
            assert response.status_code == 200
            for token in tokens:
                assert b'"value":' + token.encode() in response.content
            content = json.loads(response.content, parse_float=Decimal, parse_int=Decimal)['data']
            points = content.get('points', content.get('items'))
            actual = {point['pointId']: point['value'] for point in points}
            assert actual['precision-0'] == Decimal(tokens[0])
            assert actual['precision-1'] == Decimal(tokens[1])
            assert actual['precision-2'].is_signed()
            assert actual['precision-3'] == Decimal(tokens[3])


def legacy_batch(sequence):
    """用仓库固定 v1 向量构造本次合成样本。"""
    from app.plc_facts.canonical import canonical, digest, sha
    from app.plc_facts.crud.sync_maintenance import clock
    from app.plc_facts.models import StreamState
    vector = json.loads((root / 'contracts/published/http-api/plc-facts-v1/vectors.json').read_text())['request']
    document = copy.deepcopy(vector)
    identity = str(uuid4())
    db = create_sync_session()
    try:
        now = clock(db, db.get(StreamState, 1))
        db.rollback()
    finally:
        db.close()
    observed = now.seconds(-2)
    payload = json.loads(document['samples'][0]['payloadUtf8'])
    manifest = json.loads(document['cycles'][0]['manifestUtf8'])
    for item in (payload, manifest):
        item.update(cycleId='cycle-' + identity, sourceSeq=str(sequence), startedAt=observed.wire(),
                    finishedAt=observed.wire(), savedAt=observed.wire())
    payload['sampleId'] = 'sample-' + identity
    payload['points']['point_x'].update(value=202, observedAt=observed.wire())
    source = canonical(payload).decode()
    source_sha = sha(source.encode())
    manifest['samples'][0].update(sampleId=payload['sampleId'], sha256=source_sha[7:])
    for reading in manifest['reads']:
        reading.update(startedAt=observed.wire(), finishedAt=observed.wire())
    part = document['samples'][0]
    part.update(sampleId=payload['sampleId'], cycleId=payload['cycleId'], payloadUtf8=source, sourceSha256=source_sha)
    projection = {key: value for key, value in payload.items() if key not in ('schemaVersion', 'revision')}
    projection.update(configRevision=payload['revision'], sourceSha256=source_sha, part=1, parts=1)
    part['contentDigest'] = digest('sample-part', projection)
    cycle = document['cycles'][0]
    cycle.update(cycleId=payload['cycleId'], manifestUtf8=canonical(manifest).decode())
    cycle['manifestSha256'] = sha(cycle['manifestUtf8'].encode())
    transport = cycle['transportManifest'][0]
    transport.update(sampleId=payload['sampleId'], sourceSha256=source_sha)
    transport['parts'][0]['contentDigest'] = part['contentDigest']
    document.update(batchId='batch-' + identity, batchCreatedAt=now.wire())
    document['requestDigest'] = digest('batch', {key: value for key, value in document.items() if key != 'requestDigest'})
    return canonical(document)


def assert_v1_state(revision):
    from app.plc_facts.models import SourceBinding, StreamState
    required = ('ARCH_BE012_B_V1_ADOPTION_ID', 'ARCH_BE012_B_V1_STORAGE_EPOCH',
                'ARCH_BE012_B_V1_FINGERPRINT', 'ARCH_BE012_B_V1_PROOF_ROWS', 'ARCH_BE012_B_V1_NEXT_SEQUENCE')
    if any(not os.environ.get(name) for name in required):
        pytest.fail('the approved upgrade fixture must supply its recorded v1 baseline')
    db = create_sync_session()
    try:
        state = db.get(StreamState, 1)
        binding = db.get(SourceBinding, b'plc-demo')
        assert db.execute(text('SELECT @@server_uuid')).scalar_one() == server_uuid
        assert db.execute(text('SELECT DATABASE()')).scalar_one() == schema
        assert verify_profile(db.connection())['revision'] == revision
        assert state.verified_schema_revision == revision
        assert state.adoption_id == os.environ['ARCH_BE012_B_V1_ADOPTION_ID']
        assert state.storage_epoch == os.environ['ARCH_BE012_B_V1_STORAGE_EPOCH']
        assert bytes(state.schema_fingerprint).hex() == os.environ['ARCH_BE012_B_V1_FINGERPRINT']
        assert state.proof_rows == int(os.environ['ARCH_BE012_B_V1_PROOF_ROWS'])
        assert binding.instance_id == b'daa-demo' and binding.source_generation == b'generation-demo'
        db.rollback()
    finally:
        db.close()


async def v1_http_roundtrip():
    raw = legacy_batch(int(os.environ['ARCH_BE012_B_V1_NEXT_SEQUENCE']))
    async with AsyncClient(base_url=HTTP, timeout=10, trust_env=False) as client:
        post = await client.post('/api/v1/integration/plc-facts/batches', content=raw,
                                 headers={'Content-Type': 'application/json'})
        assert post.status_code == 200 and post.json()['data']['status'] == 'committed'
        latest = await client.get('/api/v1/integration/plc-facts/latest', params={'plcId': 'plc-demo'})
        assert latest.status_code == 200 and latest.json()['data']['items']
        history = await client.get('/api/v1/integration/plc-facts/history',
                                   params={'mode': 'changes', 'plcId': 'plc-demo', 'start': 'earliest'})
        assert history.status_code == 200 and history.json()['data']['items']


@pytest.mark.asyncio(loop_scope='module')
async def test_v1_previous_revision_only():
    if os.environ.get('ARCH_BE012_B_V1_PHASE') != 'previous':
        pytest.skip('previous-revision v1 check runs before the v2 migration')
    assert_v1_state('1b3d5f7a9c20')
    await v1_http_roundtrip()


@pytest.mark.asyncio(loop_scope='module')
async def test_v1_revalidated_state_and_three_http_routes(target):
    assert_v1_state('2c4e6a8b0d12')
    await v1_http_roundtrip()


def expired_observation(now):
    return next(candidate for days in range(75, 110)
                for candidate in (now - timedelta(days=days),)
                if now - timedelta(hours=24) < expiry(candidate) <= now)


def seed_expired_fixture(now):
    """只向已核验的专用 schema 写入 5000 样本和 5000 最新值。"""
    observed = expired_observation(now)
    expires = expiry(observed)
    points = [{'pointId': f'bulk-{index:03}', 'name': 'x' * 90, 'dataType': 'INT', 'value': index,
               'quality': 'good', 'observedAt': wire_time(observed)} for index in range(70)]
    assert len(body({'points': points})) <= 16 * 1024
    db = create_sync_session()
    try:
        for start in range(0, 5000, 100):
            histories = [dict(instance_id=b'daa-a', sample_id=f'bulk-{index}'.encode(), plc_id=b'PLC-A',
                              db_number=21, group_id=b'fixture-group', config_revision=b'fixture-revision',
                              source_generation=b'gen-a', source_seq=100000 + index, points_json=points,
                              content_hash=b'\x00' * 32, sampled_at=observed, stored_at=now, expires_at=expires)
                         for index in range(start, start + 100)]
            latest = [dict(plc_id=b'PLC-A', db_number=21, point_id=f'bulk-{index}'.encode(),
                           point_name='bulk', data_type='INT', value_json=1, quality='good', reason=None,
                           observed_at=observed, expires_at=expires, instance_id=b'daa-a',
                           source_generation=b'gen-a', source_seq=100000 + index,
                           sample_id=f'bulk-{index}'.encode()) for index in range(start, start + 100)]
            db.execute(insert(SampleV2), histories)
            db.execute(insert(LatestPointV2), latest)
            db.commit()
    finally:
        db.close()


def seed_unexpired_sentinel(now):
    """同库加入应受保护的历史及 latest 值。"""
    point = {'pointId': 'protected-point', 'dataType': 'INT', 'value': 42,
             'quality': 'good', 'observedAt': wire_time(now)}
    db = create_sync_session()
    try:
        db.add(SampleV2(instance_id=b'daa-a', sample_id=b'protected-history', plc_id=b'PLC-A',
                        db_number=21, group_id=b'fixture-group', config_revision=b'fixture-revision',
                        source_generation=b'gen-a', source_seq=900000, points_json=[point],
                        content_hash=b'\x01' * 32, sampled_at=now, stored_at=now, expires_at=now + timedelta(hours=1)))
        db.add(LatestPointV2(plc_id=b'PLC-A', db_number=21, point_id=b'protected-point',
                             point_name='protected', data_type='INT', value_json=42, quality='good', reason=None,
                             observed_at=now, expires_at=now + timedelta(hours=1), instance_id=b'daa-a',
                             source_generation=b'gen-a', source_seq=900000, sample_id=b'protected-history'))
        db.commit()
    finally:
        db.close()


def assert_unexpired_sentinel(now):
    db = create_sync_session()
    try:
        history = db.execute(select(SampleV2).where(SampleV2.instance_id == b'daa-a',
                             SampleV2.sample_id == b'protected-history')).scalar_one()
        latest = db.get(LatestPointV2, (b'PLC-A', 21, b'protected-point'))
        assert history.points_json[0]['value'] == 42 and history.expires_at == now + timedelta(hours=1)
        assert latest.value_json == 42 and latest.source_seq == 900000 and latest.expires_at == now + timedelta(hours=1)
        db.rollback()
    finally:
        db.close()


def expired_fixture_count(now):
    db = create_sync_session()
    try:
        result = sum(db.execute(select(func.count()).select_from(model).where(model.expires_at <= now)).scalar_one()
                     for model in (SampleV2, LatestPointV2))
        db.rollback()
        return result
    finally:
        db.close()


def run_cleanup_once():
    confirmation = ':'.join(('APPLY', 'cleanup-v2', alias, schema, server_uuid, '2c4e6a8b0d12'))
    command = [sys.executable, 'scripts/plc_facts_maintenance/main.py', 'cleanup-v2', '--apply',
               '--target-alias', alias, '--schema', schema, '--expected-server-uuid', server_uuid,
               '--expected-schema-revision', '2c4e6a8b0d12', '--operation-approval',
               os.environ['ARCH_BE012_B_OPERATION_APPROVAL'], '--confirmed-by', 'synthetic-b-operator',
               '--confirm', confirmation]
    environment = dict(os.environ, PLC_FACTS_MAINTENANCE_ENABLED='True', PYTHONPATH=str(root / 'backend'))
    result = subprocess.run(command, cwd=root / 'backend', env=environment,
                            capture_output=True, text=True, timeout=15, check=True)
    events = [json.loads(line) for line in result.stdout.splitlines()]
    assert events[-1]['event'] == 'complete' and events[-1]['status'] == 'ok'
    return next(event['result'] for event in events if event.get('event') == 'commit')


@pytest.mark.asyncio(loop_scope='module')
async def test_cleanup_skips_locked_row_and_preserves_newer_value(target):
    observed = expired_observation(target['now'])
    db = create_sync_session()
    try:
        db.add(LatestPointV2(plc_id=b'PLC-A', db_number=21, point_id=b'cleanup-race', point_name='race',
                             data_type='INT', value_json=1, quality='good', reason=None, observed_at=observed,
                             expires_at=expiry(observed), instance_id=b'daa-a', source_generation=b'gen-a',
                             source_seq=299999, sample_id=b'old-race'))
        db.commit()
    finally:
        db.close()
    locked = create_sync_session()
    try:
        locked.execute(text('SET SESSION innodb_lock_wait_timeout = 1'))
        locked.execute(select(LatestPointV2).where(LatestPointV2.plc_id == b'PLC-A',
                       LatestPointV2.db_number == 21, LatestPointV2.point_id == b'cleanup-race').with_for_update()).scalar_one()
        replacement = sample(target, count=1, seq=300000)
        replacement['points'][0].update(pointId='cleanup-race', value=2)
        async with AsyncClient(base_url=HTTP, timeout=10, trust_env=False) as client:
            pending = asyncio.create_task(send(client, body(replacement)))
            await asyncio.sleep(0.2)
            assert not pending.done()
            await asyncio.to_thread(run_cleanup_once)
            locked.commit()
            response = await pending
            assert response.status_code == 200
        await asyncio.to_thread(run_cleanup_once)
    finally:
        locked.close()
    db = create_sync_session()
    try:
        row = db.get(LatestPointV2, (b'PLC-A', 21, b'cleanup-race'))
        assert row.source_seq == 300000 and row.value_json == 2 and row.expires_at > target['now']
        db.rollback()
    finally:
        db.close()


async def cleanup_for_load(target, started, aggregate=None):
    evidence = Path(os.environ['ARCH_BE012_B_TICK_EVIDENCE']).resolve()
    if evidence != (root.parent / 'evidence' / 'cleanup-ticks.jsonl').resolve():
        raise RuntimeError('tick evidence must use this round-owned path')
    evidence.parent.mkdir(parents=True, exist_ok=True)
    cleared = None
    with evidence.open('x', encoding='utf-8') as stream:
        for tick in range(30):
            await asyncio.sleep(max(0, started + tick * 60 - time.monotonic()))
            summary = await asyncio.to_thread(run_cleanup_once)
            completed = datetime.fromisoformat(summary['completedAt'])
            oldest = summary['oldestExpiredAt']
            lag = max(0, (completed - datetime.fromisoformat(oldest)).total_seconds()) if oldest else 0
            if not summary['oldestKnown']:
                lag = None
            remaining = expired_fixture_count(target['now'])
            elapsed = time.monotonic() - started
            stream.write(json.dumps({'tick': tick + 1, 'rows': summary['rows'], 'bytes': summary['bytes'],
                                     'oldestKnown': summary['oldestKnown'], 'oldestExpiredAt': oldest,
                                     'lagSeconds': lag, 'remainingFixtureRows': remaining,
                                     'elapsedSeconds': round(elapsed, 3)}, separators=(',', ':')) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
            if remaining == 0 and cleared is None:
                cleared = elapsed
            if aggregate is not None:
                aggregate.update(ticks=tick + 1, rows=aggregate['rows'] + summary['rows'],
                                 bytes=aggregate['bytes'] + summary['bytes'], lastLagSeconds=lag,
                                 remainingFixtureRows=remaining, clearedSeconds=cleared)
            if elapsed >= 15 * 60 and cleared is None:
                raise AssertionError('expired fixture was not cleared in 15 minutes')
    assert cleared is not None and cleared <= 15 * 60
    return cleared


@pytest.mark.asyncio(loop_scope='module')
async def test_steady_load_and_cleanup_capacity(target):
    if os.environ.get('ARCH_BE012_B_RUN_LOAD') != 'True':
        pytest.fail('the approved B run must enable the 30-minute load scenario')
    evidence = Path(os.environ['ARCH_BE012_B_LOAD_EVIDENCE']).resolve()
    if evidence != (root.parent / 'evidence' / 'load-summary.json').resolve():
        raise RuntimeError('load evidence must use this round-owned path')
    evidence.parent.mkdir(parents=True, exist_ok=True)
    def empty_plc():
        return {'attempted': 0, 'success': 0, 'failed': 0, 'pointsTotal': 0,
                'pointsMin': None, 'pointsMax': None, 'pointCounts': {},
                'bodyBytesTotal': 0, 'bodyBytesMin': None, 'bodyBytesMax': None}
    report = {'status': 'failed', 'attempted': 0, 'success': 0, 'failed': 0, 'p95Ms': None,
              'elapsedSeconds': 0, 'plcs': {plc: empty_plc() for plc in ('PLC-A', 'PLC-B')},
              'cleanup': {'ticks': 0, 'rows': 0, 'bytes': 0, 'lastLagSeconds': None,
                          'remainingFixtureRows': None, 'clearedSeconds': None}}
    latencies = []
    started = time.monotonic()
    with evidence.open('x', encoding='utf-8') as stream:
        try:
            seed_expired_fixture(target['now'])
            seed_unexpired_sentinel(target['now'])
            assert expired_fixture_count(target['now']) == 10000
            started = time.monotonic()
            async with AsyncClient(base_url=HTTP, timeout=10, trust_env=False) as client:
                async def producer(plc):
                    for index in range(LOAD_SAMPLES_PER_PLC):
                        await asyncio.sleep(max(0, started + index + 1 - time.monotonic()))
                        document = sample(target, count=64, plc=plc, seq=200000 + index)
                        raw = body(document)
                        row = report['plcs'][plc]
                        row['attempted'] += 1
                        report['attempted'] += 1
                        point_count, size = len(document['points']), len(raw)
                        count_key = str(point_count)
                        row['pointCounts'][count_key] = row['pointCounts'].get(count_key, 0) + 1
                        for prefix, value in (('points', point_count), ('bodyBytes', size)):
                            row[prefix + 'Total'] += value
                            row[prefix + 'Min'] = value if row[prefix + 'Min'] is None else min(row[prefix + 'Min'], value)
                            row[prefix + 'Max'] = value if row[prefix + 'Max'] is None else max(row[prefix + 'Max'], value)
                        before = time.monotonic()
                        try:
                            response = await send(client, raw)
                        except BaseException:
                            row['failed'] += 1
                            report['failed'] += 1
                            raise
                        if response.status_code != 200:
                            row['failed'] += 1
                            report['failed'] += 1
                            raise AssertionError('load request failed')
                        row['success'] += 1
                        report['success'] += 1
                        latencies.append(time.monotonic() - before)
                async with asyncio.TaskGroup() as group:
                    group.create_task(producer('PLC-A'))
                    group.create_task(producer('PLC-B'))
                    cleanup = group.create_task(cleanup_for_load(target, started, report['cleanup']))
                cleanup_seconds = cleanup.result()
                assert_unexpired_sentinel(target['now'])
                replay = sample(target, count=1, seq=99999)
                replay['points'][0].update(pointId='bulk-0', value=999)
                assert (await send(client, body(replay))).status_code == 200
            db = create_sync_session()
            try:
                tombstone = db.get(LatestPointV2, (b'PLC-A', 21, b'bulk-0'))
                assert tombstone.source_seq == 100000 and tombstone.value_json is None and tombstone.expires_at is None
                db.rollback()
            finally:
                db.close()
            assert len(latencies) == 2 * LOAD_SAMPLES_PER_PLC
            ordered = sorted(latencies)
            p95 = ordered[(95 * len(ordered) + 99) // 100 - 1]
            assert p95 <= 0.5 and cleanup_seconds <= 15 * 60
            report['status'] = 'passed'
        finally:
            if latencies:
                ordered = sorted(latencies)
                report['p95Ms'] = round(ordered[(95 * len(ordered) + 99) // 100 - 1] * 1000, 3)
            report['elapsedSeconds'] = round(time.monotonic() - started, 3)
            encoded = json.dumps(report, ensure_ascii=True, separators=(',', ':'))
            assert len(encoded) <= 8192
            stream.write(encoded + '\n')
            stream.flush()
            os.fsync(stream.fileno())
