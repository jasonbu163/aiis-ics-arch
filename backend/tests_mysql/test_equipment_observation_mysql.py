"""Explicitly guarded socket/real-MySQL r8 regression against a disposable fixture."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import time

import httpx
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


@pytest.fixture(scope='module')
def target():
    required = ('OBS_FIXTURE_ROUND', 'OBS_FIXTURE_UUID', 'OBS_FIXTURE_ACK', 'OBS_FIXTURE_API_PORT',
                'MYSQL_HOST', 'MYSQL_PORT', 'MYSQL_DATABASE', 'MYSQL_USER', 'MYSQL_PASSWORD',
                'OBS_DEMO_ADMIN_USER', 'OBS_DEMO_ADMIN_PASS',
                'OBS_DEMO_EXTERNAL_TOKEN', 'OBS_DEMO_SMA_TOKEN')
    if any(not os.environ.get(key) for key in required):
        pytest.skip('requires an explicitly identified disposable ARCH-OBS-001 MySQL/API fixture')
    run = os.environ['OBS_FIXTURE_ROUND']
    ports = {'dev': ('13395', '18395'), 'qa': ('13396', '18396')}
    if run not in ports:
        raise RuntimeError('invalid fixture round')
    db_port, api_port = ports[run]
    uid = os.environ['OBS_FIXTURE_UUID']
    schema = f'arch_obs_r8_{run}'
    if (os.environ['MYSQL_HOST'] != '127.0.0.1' or os.environ['MYSQL_PORT'] != db_port
            or os.environ['MYSQL_DATABASE'] != schema or os.environ['OBS_FIXTURE_API_PORT'] != api_port
            or os.environ['OBS_FIXTURE_ACK'] != f'ARCH-OBS-001:{run}:{uid}:{db_port}:{schema}'):
        raise RuntimeError('fixture scope rejected')
    candidate = Path(__file__).resolve().parents[1]
    if Path.cwd().resolve() != candidate:
        raise RuntimeError('fixture must run from candidate backend')
    url = URL.create('mysql+pymysql', username=os.environ['MYSQL_USER'], password=os.environ['MYSQL_PASSWORD'],
                     host='127.0.0.1', port=int(db_port), database=schema)
    engine = create_engine(url, connect_args={'connect_timeout': 3})
    with engine.connect() as db:
        version, actual_uuid, actual_schema, user, offset = db.execute(text(
            'SELECT VERSION(), @@server_uuid, DATABASE(), CURRENT_USER(), '
            'TIMESTAMPDIFF(SECOND,UTC_TIMESTAMP(6),CURRENT_TIMESTAMP(6))')).one()
        revision = db.execute(text('SELECT version_num FROM alembic_version')).scalar_one()
        if (str(version).split('-')[0] != '8.4.6' or actual_uuid != uid or actual_schema != schema
                or user.split('@')[0] != os.environ['MYSQL_USER'] or offset != 28800 or revision != '8c0e2a4d6f18'):
            raise RuntimeError('fixture database identity mismatch')
    with httpx.Client(base_url=f'http://127.0.0.1:{api_port}/api/v1', timeout=20) as client:
        result = client.post('/auth/login', json={'username': os.environ['OBS_DEMO_ADMIN_USER'],
                                                  'password': os.environ['OBS_DEMO_ADMIN_PASS']})
        assert result.status_code == 200
        admin = result.json()['data']['accessToken']
        yield client, engine, admin
    engine.dispose()


def bearer(name):
    return {'Authorization': 'Bearer ' + os.environ[name]}


def request_ok(client, method, path, token, **kwargs):
    result = client.request(method, path, headers={'Authorization': 'Bearer ' + token} if token else {}, **kwargs)
    assert result.status_code == 200, (path, result.status_code, result.text[:500])
    return result.json()['data']


def test_http_admission_and_strict_envelope(target):
    client, _, _ = target
    post = '/integration/equipment/latest-snapshots'
    assert client.post(post, content=b'{').status_code == 401
    assert client.get('/integration/metric-definitions', params={'equipmentId': 'line-01', 'groupKey': 'temperature', 'target': 'latest'}).status_code == 401
    token = bearer('OBS_DEMO_EXTERNAL_TOKEN')
    assert client.post(post, content='{}', headers={**token, 'Content-Type': 'text/plain'}).status_code == 415
    assert client.post(post, content=' ' * 65537, headers={**token, 'Content-Type': 'application/json'}).status_code == 413
    body = {'sourceRefs': [{'kind': 'external_event', 'sourceEventId': 'validation-only'}],
            'data': {'taskNo': '000042', 'sampledAt': '2026-11-11T09:30:00+08:00', 'values': {'furnaceZone1Actual': 1}}}
    bad = dict(body, data=dict(body['data'], equipmentId='unapproved', groupKey='temperature'))
    assert client.post(post, headers=token, json=bad).status_code == 403
    bad = dict(body, data=dict(body['data'], values={'furnaceZone1Actual': None}))
    assert client.post(post, headers=token, json=bad).status_code == 422
    bad = dict(body, data=dict(body['data'], quality='bad'))
    assert client.post('/integration/monitor/history-samples', headers=token, json=bad).status_code == 422
    assert client.post(post, headers=bearer('OBS_DEMO_SMA_TOKEN'), json=body).status_code == 422


def test_task_change_late_data_dedup_and_evidence(target):
    client, engine, admin = target
    external = os.environ['OBS_DEMO_EXTERNAL_TOKEN']
    facts = None  # Current acquisition sample endpoint does not use the observation Bearer.
    sma = os.environ['OBS_DEMO_SMA_TOKEN']
    run_id = str(time.time_ns() // 1000)
    task_a, task_b = 'A-' + run_id, 'B-' + run_id
    now = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0)
    stamps = [(now - timedelta(seconds=offset)).isoformat() for offset in (25, 13, 1)]
    sample_ids = [f'proof-{run_id}-{i}' for i in range(3)]
    points = ('point-active-task-no', 'point-zone1-temp-act', 'point-zone1-temp-set', 'point-zone1-ready')
    for i, task in enumerate((task_a, task_a, task_b)):
        fact = {'contractVersion': 'plc-facts/v2', 'instanceId': 'daa-fixture', 'sampleId': sample_ids[i],
                'plcId': 'plc-01', 'dbNumber': 42, 'groupId': 'temperature', 'configRevision': 'r1',
                'sourceGeneration': 'generation-1', 'sourceSeq': str(int(run_id) + i),
                'points': [{'pointId': point, 'dataType': typ, 'value': value, 'quality': 'good', 'observedAt': stamps[i]}
                           for point, typ, value in zip(points, ('STRING[50]', 'REAL', 'REAL', 'BOOL'), (task, 0.0, 0.0, False))]}
        request_ok(client, 'POST', '/integration/plc-facts/samples', facts, json=fact)
    query = {'equipmentId': 'line-01', 'pageKey': 'temperature'}
    cards = request_ok(client, 'GET', '/equipment/latest-cards', admin, params=query)
    assert cards['taskNo'] == task_b
    assert all(item['dataState'] == 'missing' for item in cards['cards'][0]['items'])
    def ext(index, task=task_a, quality='good'):
        return {'sourceRefs': [{'kind': 'external_event', 'sourceEventId': f'vendor-{run_id}-{index}'}],
                'data': {'taskNo': task, 'sampledAt': stamps[index], 'quality': quality,
                         'values': {'furnaceZone1Actual': 0.0, 'furnaceZone1Set': 0.0}}}
    a2 = request_ok(client, 'POST', '/integration/equipment/latest-snapshots', external, json=ext(1))
    assert a2['outcome'] == 'stored'
    a1 = request_ok(client, 'POST', '/integration/equipment/latest-snapshots', external, json=ext(0))
    assert a1['outcome'] == 'stale' and a1['recordId'] == a2['recordId']
    assert request_ok(client, 'POST', '/integration/equipment/latest-snapshots', external, json=ext(1)) == a2
    changed = ext(1); changed['data']['values']['furnaceZone1Actual'] = 1
    assert client.post('/integration/equipment/latest-snapshots', headers=bearer('OBS_DEMO_EXTERNAL_TOKEN'), json=changed).status_code == 409
    history = request_ok(client, 'POST', '/integration/monitor/history-samples', external, json=ext(0))
    duplicate = dict(ext(0), eventId='same-source-' + run_id)
    assert request_ok(client, 'POST', '/integration/monitor/history-samples', external, json=duplicate)['outcome'] == 'already_stored'
    bad_task = ext(1, task_b)
    assert client.post('/integration/equipment/latest-snapshots', headers=bearer('OBS_DEMO_EXTERNAL_TOKEN'), json=bad_task).status_code == 409
    card_b = request_ok(client, 'GET', '/equipment/latest-cards', admin, params=query)
    assert card_b['taskNo'] == task_b and all(item['dataState'] == 'missing' for item in card_b['cards'][0]['items'])
    refs = [{'kind': 'plc_fact', 'instanceId': 'daa-fixture', 'plcId': 'plc-01', 'sampleId': sample_ids[2], 'pointId': point} for point in points]
    full = {'contractVersion': 'aiis.metric-ingest/v1', 'producerId': 'sma-line-01', 'eventId': 'b-' + run_id,
            'mappingId': 'sma-temperature', 'mappingRevision': 'r1', 'sourceRefs': refs,
            'data': {'equipmentId': 'line-01', 'groupKey': 'temperature', 'taskNo': task_b, 'sampledAt': stamps[2],
                     'quality': 'good', 'values': {'furnaceZone1Actual': 0.0, 'furnaceZone1Set': 0.0, 'furnaceHeatingReady': False}}}
    forged = dict(full, eventId='forged-' + run_id, sourceRefs=[dict(ref, sampleId='not-a-stored-sample') for ref in refs])
    assert client.post('/integration/equipment/latest-snapshots', headers=bearer('OBS_DEMO_SMA_TOKEN'), json=forged).status_code == 409
    wrong_time = dict(full, eventId='wrong-time-' + run_id, data=dict(full['data'], sampledAt=stamps[1]))
    assert client.post('/integration/equipment/latest-snapshots', headers=bearer('OBS_DEMO_SMA_TOKEN'), json=wrong_time).status_code == 409
    result = request_ok(client, 'POST', '/integration/equipment/latest-snapshots', sma, json=full)
    assert result['outcome'] == 'stored'
    card_b = request_ok(client, 'GET', '/equipment/latest-cards', admin, params=query)
    assert card_b['taskNo'] == task_b and all(item['value'] == 0 for item in card_b['cards'][0]['items'])
    detail = request_ok(client, 'GET', '/equipment/admin/latest-snapshots/' + result['recordId'], admin)
    assert detail['taskEvidence']['sampleId'] == sample_ids[2]
    assert detail['taskEvidence']['pointId'] == 'point-active-task-no'
    with engine.connect() as db:
        row = db.execute(text('SELECT local_values, task_evidence FROM equipment_status_main s '
                              'JOIN metric_ingest_receipts r ON r.id=s.ingest_receipt_id WHERE s.id=:id'),
                         {'id': int(result['recordId'])}).one()
        import json
        values = json.loads(row[0]) if isinstance(row[0], str) else row[0]
        proof = json.loads(row[1]) if isinstance(row[1], str) else row[1]
        assert values['01'] == 0 and values['03'] is False
        assert proof['sampleId'] == sample_ids[2] and history['recordId']


def test_curve_keeps_all_referenced_metrics_numeric(target):
    client, engine, admin = target
    nonce = str(time.time_ns() // 1000)
    metric = 'curve-guard-' + nonce
    groups = ['curve-active-' + nonce, 'curve-disabled-' + nonce]
    create = {'metricKey': metric, 'sourceGroupKey': 'drive', 'category': 'drive', 'nameZh': '测试数值',
              'nameEn': 'Test number', 'valueType': 'number', 'unit': 'Hz', 'decimals': 1}
    try:
        # The existing seeded temperature metric has already been used; its type and unit remain locked.
        for body in ({'valueType': 'boolean'}, {'unit': '°F'}):
            result = client.patch('/equipment/metric-configs/furnaceZone1Actual',
                                  headers={'Authorization': 'Bearer ' + admin}, json=body)
            assert result.status_code == 409 and result.json()['errorCode'] == 'equipment_observation.metric_in_use'
        request_ok(client, 'POST', '/equipment/metric-configs', admin, json=create)
        for index, key in enumerate(groups):
            item = {'curveGroupKey': key, 'category': 'drive', 'titleZh': '测试曲线', 'titleEn': 'Test curve',
                    'enabled': index == 0, 'sortOrder': 1,
                    'series': [{'metricKey': metric, 'enabled': index == 0}]}
            request_ok(client, 'POST', '/monitor/curve-configs', admin, json=item)
        for kind in ('boolean', 'string'):
            result = client.patch('/equipment/metric-configs/' + metric,
                                  headers={'Authorization': 'Bearer ' + admin}, json={'valueType': kind})
            assert result.status_code == 409 and result.json()['errorCode'] == 'equipment_observation.curve_items'
        # Editable metadata remains editable, and an unreferenced, unused key can change type.
        request_ok(client, 'PATCH', '/equipment/metric-configs/' + metric, admin, json={'nameEn': 'Revised label'})
        for key in groups:
            request_ok(client, 'PATCH', '/monitor/curve-configs/' + key, admin, json={'series': []})
        assert request_ok(client, 'PATCH', '/equipment/metric-configs/' + metric, admin,
                          json={'valueType': 'boolean'})['valueType'] == 'boolean'
    finally:
        with engine.begin() as db:
            db.execute(text('DELETE FROM monitor_curve_group_configs WHERE curve_group_key IN (:a,:b)'),
                       {'a': groups[0], 'b': groups[1]})
            db.execute(text('DELETE FROM equipment_metric_configs WHERE metric_key=:key'), {'key': metric})


def test_detail_filters_id_and_equipment_before_lookup(target):
    client, engine, admin = target
    nonce = str(time.time_ns() // 1000)
    auth = {'Authorization': 'Bearer ' + admin}
    rows = []
    with engine.begin() as db:
        receipt = db.execute(text('SELECT id FROM metric_ingest_receipts ORDER BY id LIMIT 1')).scalar_one()
        for table in ('equipment_status_main', 'process_monitor_main'):
            result = db.execute(text(f'''INSERT INTO {table}
                (equipment_id,group_key,task_no,sampled_at,quality,source_sample_key,ingest_receipt_id,local_values,remark)
                VALUES ('unscoped-test-line','temperature',:task,NOW(6),'good',:source,:receipt,:values,'unchanged')'''),
                {'task': 'SCOPE-' + nonce, 'source': bytes(32), 'receipt': receipt, 'values': '{"01":42}'})
            rows.append((table, result.lastrowid))
    try:
        for table, record_id in rows:
            latest = table == 'equipment_status_main'
            base = '/equipment/admin/latest-snapshots/' if latest else '/monitor/admin/history-samples/'
            unauthorized = client.get(base + str(record_id), headers=auth)
            missing = client.get(base + '999999999', headers=auth)
            assert unauthorized.status_code == missing.status_code == 404
            assert unauthorized.json() == missing.json()
            body = {'remark': 'attempt'} if latest else {'remark': 'attempt', 'reviewMark': 'reviewed'}
            unauthorized = client.patch(base + str(record_id), headers=auth, json=body)
            missing = client.patch(base + '999999999', headers=auth, json=body)
            assert unauthorized.status_code == missing.status_code == 404
            assert unauthorized.json() == missing.json()
            list_path = base.rstrip('/')
            assert client.get(list_path, headers=auth, params={'equipmentId': 'unscoped-test-line'}).status_code == 403
            with engine.connect() as db:
                assert db.execute(text(f'SELECT remark FROM {table} WHERE id=:id'), {'id': record_id}).scalar_one() == 'unchanged'
    finally:
        with engine.begin() as db:
            for table, record_id in rows:
                db.execute(text(f'DELETE FROM {table} WHERE id=:id'), {'id': record_id})


def test_curve_and_metric_writes_serialize_on_same_metric(target):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    client, engine, admin = target
    auth = {'Authorization': 'Bearer ' + admin}
    nonce = str(time.time_ns() // 1000)
    metrics = ['curve-race-a-' + nonce, 'curve-race-b-' + nonce]
    groups = ['curve-race-a-' + nonce, 'curve-race-b-' + nonce]
    for key in metrics:
        request_ok(client, 'POST', '/equipment/metric-configs', admin,
                   json={'metricKey': key, 'sourceGroupKey': 'drive', 'category': 'drive', 'nameZh': '并发测试',
                         'nameEn': 'Concurrency test', 'valueType': 'number', 'unit': 'Hz', 'decimals': 1})
    def run_while_locked(metric, action, concurrent_sql):
        started = Event()
        def call():
            started.set()
            return action()
        with engine.connect() as db, ThreadPoolExecutor(max_workers=1) as pool:
            transaction = db.begin()
            try:
                db.execute(text('SELECT metric_key FROM equipment_metric_configs WHERE metric_key=:key FOR UPDATE'), {'key': metric}).one()
                future = pool.submit(call)
                assert started.wait(3)
                time.sleep(0.25)
                assert not future.done(), 'request did not wait on metric transaction lock'
                concurrent_sql(db)
                transaction.commit()
                return future.result(timeout=10)
            finally:
                if transaction.is_active:
                    transaction.rollback()
    try:
        # The curve save must wait and reject when a prior type transaction commits boolean.
        curve = {'curveGroupKey': groups[0], 'category': 'drive', 'titleZh': '并发曲线', 'titleEn': 'Race',
                 'enabled': True, 'sortOrder': 1, 'series': [{'metricKey': metrics[0], 'enabled': True}]}
        result = run_while_locked(metrics[0], lambda: client.post('/monitor/curve-configs', headers=auth, json=curve),
                                  lambda db: db.execute(text("UPDATE equipment_metric_configs SET value_type='boolean' WHERE metric_key=:key"), {'key': metrics[0]}))
        assert result.status_code == 422 and result.json()['errorCode'] == 'equipment_observation.curve_items'
        # The type change must wait and observe a curve committed after its transaction started.
        def insert_curve(db):
            import json
            db.execute(text('INSERT INTO monitor_curve_group_configs (curve_group_key,category,title_zh,title_en,enabled,sort_order,series) '
                            'VALUES (:key,\'drive\',\'并发曲线\',\'Race\',1,1,:series)'),
                       {'key': groups[1], 'series': json.dumps([{'metricKey': metrics[1], 'enabled': True}])})
        result = run_while_locked(metrics[1], lambda: client.patch('/equipment/metric-configs/' + metrics[1], headers=auth,
                                                                   json={'valueType': 'boolean'}), insert_curve)
        assert result.status_code == 409 and result.json()['errorCode'] == 'equipment_observation.curve_items'
        with engine.connect() as db:
            assert db.execute(text('SELECT value_type FROM equipment_metric_configs WHERE metric_key=:key'),
                              {'key': metrics[1]}).scalar_one() == 'number'
    finally:
        with engine.begin() as db:
            db.execute(text('DELETE FROM monitor_curve_group_configs WHERE curve_group_key IN (:a,:b)'),
                       {'a': groups[0], 'b': groups[1]})
            db.execute(text('DELETE FROM equipment_metric_configs WHERE metric_key IN (:a,:b)'),
                       {'a': metrics[0], 'b': metrics[1]})
