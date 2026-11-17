"""在独立内存 SQLite 验证 r10 HTTP、业务事务及权限，不连接真实数据库。"""
from datetime import datetime
import hashlib
from types import SimpleNamespace

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.equipment_observation.api import routes
from app.equipment_observation.profile import authenticate
from app.equipment_observation.models import CardConfig, CurveGroup, EnergySample, HistorySample, LatestSnapshot, MetricConfig, MetricGroup, Receipt, SlotBinding
from app.equipment_observation.services import energy_reads, ingest as legacy_ingest, ingest_v2, reads
from core.deps import get_current_user
from database import get_db

pytestmark = pytest.mark.no_db


class AsyncSQLite:
    def __init__(self, session): self.session = session
    def add(self, row): self.session.add(row)
    async def execute(self, statement): return self.session.execute(statement)
    async def flush(self): self.session.flush()
    async def commit(self): self.session.commit()
    async def rollback(self): self.session.rollback()
    async def get(self, model, key): return self.session.get(model, key)
    async def refresh(self, row): self.session.refresh(row)


@pytest.fixture
def app_and_db(monkeypatch):
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    statements = [
        'CREATE TABLE equipment_metric_groups (group_key TEXT PRIMARY KEY, category TEXT NOT NULL, name_zh TEXT NOT NULL, name_en TEXT NOT NULL, enabled BOOLEAN NOT NULL, sort_order INTEGER NOT NULL)',
        'CREATE TABLE equipment_metric_configs (metric_key TEXT PRIMARY KEY, source_group_key TEXT NOT NULL, category TEXT NOT NULL, name_zh TEXT NOT NULL, name_en TEXT NOT NULL, value_type TEXT NOT NULL, unit TEXT, decimals INTEGER)',
        'CREATE TABLE equipment_metric_slot_bindings (target TEXT NOT NULL, group_key TEXT NOT NULL, slot_no INTEGER NOT NULL, metric_key TEXT NOT NULL, enabled BOOLEAN NOT NULL, list_visible BOOLEAN NOT NULL DEFAULT 0, list_order INTEGER, first_used_at DATETIME, PRIMARY KEY(target,group_key,slot_no))',
        'CREATE TABLE equipment_card_configs (card_key TEXT PRIMARY KEY, page_key TEXT NOT NULL, title_zh TEXT NOT NULL, title_en TEXT NOT NULL, enabled BOOLEAN NOT NULL, sort_order INTEGER NOT NULL, items JSON NOT NULL)',
        'CREATE TABLE monitor_curve_group_configs (curve_group_key TEXT PRIMARY KEY, category TEXT NOT NULL, title_zh TEXT NOT NULL, title_en TEXT NOT NULL, enabled BOOLEAN NOT NULL, sort_order INTEGER NOT NULL, series JSON NOT NULL)',
        'CREATE TABLE metric_ingest_receipts (id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT NOT NULL, producer_id TEXT NOT NULL, event_id TEXT NOT NULL, request_digest BLOB NOT NULL, outcome TEXT NOT NULL, processed_at DATETIME NOT NULL, result_record_id INTEGER, mapping_id TEXT, mapping_revision TEXT, source_refs JSON, task_evidence JSON, contract_version TEXT NOT NULL, result_version TEXT NOT NULL, result_detail JSON, UNIQUE(target,producer_id,event_id))',
        'CREATE TABLE equipment_status_main (id INTEGER PRIMARY KEY AUTOINCREMENT, equipment_id TEXT NOT NULL, task_no TEXT NOT NULL, observed_at DATETIME NOT NULL, quality TEXT NOT NULL, source_sample_key BLOB NOT NULL, ingest_receipt_id INTEGER NOT NULL, local_values JSON NOT NULL, remark TEXT, created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL, UNIQUE(equipment_id,task_no))',
        'CREATE TABLE process_monitor_main (id INTEGER PRIMARY KEY AUTOINCREMENT, equipment_id TEXT NOT NULL, task_no TEXT NOT NULL, observed_at DATETIME NOT NULL, quality TEXT NOT NULL, source_sample_key BLOB NOT NULL, ingest_receipt_id INTEGER NOT NULL, local_values JSON NOT NULL, remark TEXT, review_mark TEXT, created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL)',
        'CREATE TABLE energy_metric_configs (meter_id TEXT NOT NULL,group_key TEXT NOT NULL,metric_key TEXT NOT NULL,slot_no INTEGER NOT NULL,name_zh TEXT NOT NULL,name_en TEXT NOT NULL,value_type TEXT NOT NULL,quantity_key TEXT NOT NULL,measurement_mode TEXT NOT NULL,unit TEXT,decimals INTEGER,enabled BOOLEAN NOT NULL,list_visible BOOLEAN NOT NULL DEFAULT 0,list_order INTEGER,rules JSON NOT NULL,first_used_at DATETIME,PRIMARY KEY(meter_id,group_key,metric_key), UNIQUE(meter_id,group_key,slot_no))',
        'CREATE TABLE energy_consumption_main (id INTEGER PRIMARY KEY AUTOINCREMENT,meter_id TEXT NOT NULL,group_key TEXT NOT NULL,observed_at DATETIME NOT NULL,quality TEXT NOT NULL,interval_start_at DATETIME,interval_end_at DATETIME,ingest_receipt_id INTEGER NOT NULL,local_values JSON NOT NULL,remark TEXT,review_mark TEXT,created_at DATETIME NOT NULL,updated_at DATETIME NOT NULL)',
    ]
    with engine.begin() as conn:
        for statement in statements: conn.execute(text(statement))
    session = Session(engine, expire_on_commit=False)
    group_specs = [('production', 'production'), ('heatZone1', 'temperature'), ('washTank1', 'cleaning'), ('driveRoll1', 'drive')]
    for name, category in group_specs:
        session.add(MetricGroup(group_key=name, category=category, name_zh=name, name_en=name, enabled=True, sort_order=0))
    metrics = [('coil', 'production', 'production', 'string'), ('actual', 'heatZone1', 'temperature', 'number'),
               ('ready', 'driveRoll1', 'drive', 'boolean')]
    for key, group, category, kind in metrics:
        session.add(MetricConfig(metric_key=key, source_group_key=group, category=category,
                                 name_zh=key, name_en=key, value_type=kind, unit='°C' if key == 'actual' else None))
        session.add(SlotBinding(target='latest', group_key=group, slot_no=1, metric_key=key, enabled=True, list_visible=False))
    session.add(SlotBinding(target='history', group_key='heatZone1', slot_no=7, metric_key='actual', enabled=True, list_visible=False))
    session.add(CardConfig(card_key='temp-card', page_key='temperature', title_zh='温度', title_en='Temperature', enabled=True,
                           sort_order=0, items=[{'metricKey':'actual', 'enabled':True}]))
    session.add(CurveGroup(curve_group_key='temp-curve', category='temperature', title_zh='温度', title_en='Temperature', enabled=True,
                           sort_order=0, series=[{'metricKey':'actual', 'enabled':True}]))
    session.commit()
    allowed = {'production':['coil'], 'heatZone1':['actual'], 'washTank1':[], 'driveRoll1':['ready']}
    grants = [{'equipmentId':'line', 'groupKey':group, 'target':target, 'metricKeys':keys}
              for target in ('latest','history') for group, keys in allowed.items()]
    producer = {'producerId':'writer', 'kind':'other', 'grants':grants,
                'energyGrants':[{'meterId':'meter1','groupKey':'electricity','metricKeys':['reading','power','interval']},
                                {'meterId':'meter2','groupKey':'electricity','metricKeys':['reading']}]}
    profile = {'target':{}, 'devices':{'line':{'equipmentId':'line', 'nameZh':'线', 'nameEn':'Line',
               'futureToleranceSeconds':300, 'staleAfterSeconds':3600}}, 'readScopes':{'admin':['line']},
               'groupSettings':{}, 'historyRules':{}, 'producers':{'writer':producer},
               'meters':{'meter1':{'meterId':'meter1','nameZh':'表1','nameEn':'Meter 1'},
                         'meter2':{'meterId':'meter2','nameZh':'表2','nameEn':'Meter 2'}},
               'meterReadScopes':{'admin':['meter1','meter2']}}
    async def now(db, target): return datetime(2026,11,17,12,30)
    monkeypatch.setattr(ingest_v2, 'probe_target', now)
    monkeypatch.setattr(reads, 'probe_target', now)
    monkeypatch.setattr(energy_reads, 'probe_target', now)
    monkeypatch.setattr(routes, 'probe_target', now)
    monkeypatch.setattr(routes, 'get_profile', lambda: profile)
    monkeypatch.setattr(routes, 'authenticate', lambda _profile, _header: producer)
    app = FastAPI()
    app.include_router(routes.router, prefix='/api/v1')
    app.dependency_overrides[get_db] = lambda: AsyncSQLite(session)
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role='admin')
    yield app, session, profile, producer
    session.close()
    engine.dispose()


def document(event='one', timestamp='2026-11-17T12:00:00+08:00'):
    return {'eventId':event, 'data':{'equipmentId':'line', 'taskNo':'000042', 'observedAt':timestamp,
            'quality':'good', 'groups':{'production':{'coil':''}, 'heatZone1':{'actual':0},
                                       'washTank1':{}, 'driveRoll1':{'ready':False}}}}


@pytest.mark.asyncio
@pytest.mark.parametrize('kind', ['sma', 'external', 'other'])
async def test_discovery_and_two_paths_use_admin_groups_without_legacy_settings(app_and_db, kind):
    app, session, profile, producer = app_and_db
    producer['kind'] = kind
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1',
                                 headers={'Authorization':'Bearer fixture'}) as client:
        found = await client.get('/integration/metric-definitions', params={'equipmentId':'line'})
        assert found.status_code == 200
        groups = {g['groupKey']:g['metrics'] for g in found.json()['data']['groups']}
        assert {'production','heatZone1','washTank1','driveRoll1'} == set(groups)
        assert groups['washTank1'] == [] and groups['heatZone1'][0]['historyEnabled'] is True
        latest = await client.post('/integration/equipment/latest-snapshots', json=document())
        history = await client.post('/integration/monitor/history-samples', json=document())
        assert latest.status_code == history.status_code == 200
        assert latest.json()['data']['outcome'] == history.json()['data']['outcome'] == 'stored'
        assert {item['metricKey'] for item in history.json()['data']['skipped']} == {'coil','ready'}
        one = session.execute(select(LatestSnapshot)).scalar_one()
        historical = session.execute(select(HistorySample)).scalar_one()
        assert one.local_values == {'production':{'01':''}, 'heatZone1':{'01':0}, 'driveRoll1':{'01':False}}
        assert historical.local_values == {'heatZone1':{'07':0}}
        assert (await client.post('/integration/equipment/latest-snapshots', json=document())).json()['data'] == latest.json()['data']
        changed = document(); changed['data']['groups'].pop('washTank1')
        assert (await client.post('/integration/equipment/latest-snapshots', json=changed)).status_code == 409
        cards = await client.get('/equipment/latest-cards', params={'equipmentId':'line','pageKey':'temperature'})
        assert cards.status_code == 200 and cards.json()['data']['cards'][0]['items'][0]['value'] == 0
        assert cards.json()['data']['taskNo'] == '000042'
        unknown = document('unknown'); unknown['data']['groups']['notRegistered'] = {}
        assert (await client.post('/integration/equipment/latest-snapshots', json=unknown)).status_code == 422
        assert session.execute(select(Receipt).where(Receipt.event_id=='unknown')).scalar_one_or_none() is None


@pytest.mark.asyncio
@pytest.mark.parametrize('kind', ['sma', 'external', 'other'])
@pytest.mark.parametrize('target,path,model', [
    ('latest', '/integration/equipment/latest-snapshots', LatestSnapshot),
    ('history', '/integration/monitor/history-samples', HistorySample),
])
async def test_receipt_replay_requires_current_group_and_metric_authority(app_and_db, monkeypatch, target, path, model, kind):
    app, session, profile, producer = app_and_db
    producer.update(tokenSha256=hashlib.sha256(b'fixture').hexdigest(), enabled=True, kind=kind)
    monkeypatch.setattr(routes, 'authenticate', authenticate)
    original_grants = [dict(grant) for grant in producer['grants']]
    body = document('permission-replay')
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1',
                                 headers={'Authorization':'Bearer fixture'}) as client:
        first = await client.post(path, json=body)
        assert first.status_code == 200
        assert (await client.post(path, json=body)).json() == first.json()
        changed = document('permission-replay')
        changed['data']['groups']['heatZone1']['actual'] = 1
        assert (await client.post(path, json=changed)).status_code == 409
        original_rows = len(session.execute(select(model)).scalars().all())
        original_receipts = len(session.execute(select(Receipt)).scalars().all())
        producer['grants'] = [grant for grant in original_grants if grant['groupKey'] != 'production']
        assert (await client.post(path, json=body)).status_code == 403
        producer['grants'] = [dict(grant, metricKeys=[]) if grant['target'] == target and grant['groupKey'] == 'heatZone1'
                              else dict(grant) for grant in original_grants]
        assert (await client.post(path, json=body)).status_code == 403
        producer['grants'] = original_grants
        producer['enabled'] = False
        assert (await client.post(path, json=body)).status_code == 403
        producer['enabled'] = True
        assert (await client.post(path, json=body)).json() == first.json()
        assert len(session.execute(select(model)).scalars().all()) == original_rows
        assert len(session.execute(select(Receipt)).scalars().all()) == original_receipts
        if target == 'history':
            producer['grants'] = [grant for grant in original_grants
                                  if grant['target'] == 'history' and grant['groupKey'] == 'heatZone1']
            permitted_body = document('permission-narrow-new')
            permitted_body['data']['groups'] = {'heatZone1': {'actual': 0}}
            assert (await client.post(path, json=permitted_body)).status_code == 200
            assert len(session.execute(select(model)).scalars().all()) == original_rows + 1


@pytest.mark.asyncio
async def test_latest_replay_requires_current_authority_for_the_full_replacement_scope(app_and_db):
    app, session, profile, producer = app_and_db
    profile['producers']['other'] = {'producerId':'other', 'grants':[
        {'equipmentId':'line', 'groupKey':'production', 'target':'latest', 'metricKeys':['coil']}]}
    body = document('permission-sparse')
    body['data']['groups'] = {'heatZone1': {'actual': 0}}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1',
                                 headers={'Authorization':'Bearer fixture'}) as client:
        first = await client.post('/integration/equipment/latest-snapshots', json=body)
        assert first.status_code == 200
        producer['grants'] = [grant for grant in producer['grants'] if grant['groupKey'] != 'production']
        assert (await client.post('/integration/equipment/latest-snapshots', json=body)).status_code == 403
        assert len(session.execute(select(Receipt)).scalars().all()) == 1


@pytest.mark.asyncio
async def test_curves_return_current_localized_area_name_without_changing_stable_key(app_and_db):
    app, session, profile, producer = app_and_db
    area = session.get(MetricGroup, 'heatZone1')
    area.name_zh, area.name_en = '一号加热区', 'Heating Zone One'
    session.commit()
    query = {'equipmentId':'line', 'category':'temperature', 'taskNo':'000042',
             'from':'2026-11-17T11:59:00+08:00', 'to':'2026-11-17T12:01:00+08:00'}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1') as client:
        for zh, en in [('一号加热区', 'Heating Zone One'), ('重命名一区', 'Renamed Zone One')]:
            for language, expected in [('zh-CN', zh), ('en-US', en)]:
                result = await client.get('/monitor/history-curves', params=query, headers={'Accept-Language':language})
                assert result.status_code == 200
                series = result.json()['data']['groups'][0]['series'][0]
                assert series['groupKey'] == 'heatZone1' and series['groupLabel'] == expected
            area.name_zh, area.name_en = '重命名一区', 'Renamed Zone One'
            session.commit()


@pytest.mark.asyncio
async def test_missing_history_events_make_real_breaks_and_late_samples_keep_observed_order(app_and_db):
    app, session, profile, producer = app_and_db
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1',
                                 headers={'Authorization':'Bearer fixture'}) as client:
        t2 = document('t2','2026-11-17T12:00:02+08:00')
        t0 = document('t0','2026-11-17T12:00:00+08:00')
        t1 = document('t1','2026-11-17T12:00:01+08:00'); t1['data']['groups'] = {}
        for body in (t2,t0,t1):
            assert (await client.post('/integration/monitor/history-samples', json=body)).status_code == 200
        older = session.execute(select(HistorySample).where(HistorySample.observed_at == datetime(2026,11,17,12,0,0))).scalar_one()
        changed = await client.patch(f'/monitor/admin/history-samples/{older.id}', json={'remark':'late management change'})
        assert changed.status_code == 200, changed.text
        session.execute(text('UPDATE process_monitor_main SET updated_at=:stamp WHERE id=:id'),
                        {'stamp':datetime(2026,11,17,13), 'id':older.id})
        session.commit()
        query = {'equipmentId':'line','category':'temperature','taskNo':'000042',
                 'from':'2026-11-17T11:59:00+08:00','to':'2026-11-17T12:01:00+08:00'}
        result = await client.get('/monitor/history-curves', params=query)
        assert result.status_code == 200
        points = result.json()['data']['groups'][0]['series'][0]['points']
        assert [point['observedAt'][17:19] for point in points] == ['00','01','02']
        assert [point['present'] for point in points] == [True,False,True]
        assert points[1]['value'] is None
        assert len(session.execute(select(HistorySample)).scalars().all()) == 3


@pytest.mark.asyncio
async def test_bundle_stale_same_time_conflict_and_empty_replacement(app_and_db):
    app, session, profile, producer = app_and_db
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1',
                                 headers={'Authorization':'Bearer fixture'}) as client:
        assert (await client.post('/integration/equipment/latest-snapshots', json=document())).status_code == 200
        old = document('old','2026-11-17T11:59:00+08:00')
        stale = await client.post('/integration/equipment/latest-snapshots', json=old)
        assert stale.status_code == 200 and stale.json()['data']['outcome'] == 'stale'
        same = document('conflict'); same['data']['groups']['heatZone1']['actual'] = 42
        assert (await client.post('/integration/equipment/latest-snapshots', json=same)).status_code == 409
        assert session.execute(select(Receipt).where(Receipt.event_id=='conflict')).scalar_one_or_none() is None
        empty = document('empty','2026-11-17T12:00:01+08:00'); empty['data']['groups'] = {}
        result = await client.post('/integration/equipment/latest-snapshots', json=empty)
        assert result.status_code == 200 and session.execute(select(LatestSnapshot)).scalar_one().local_values == {}


@pytest.mark.asyncio
async def test_two_distinct_history_events_at_the_same_instant_are_retained(app_and_db):
    app, session, profile, producer = app_and_db
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1',
                                 headers={'Authorization':'Bearer fixture'}) as client:
        first, second = document('a'), document('b')
        second['data']['groups']['heatZone1']['actual'] = 12
        assert (await client.post('/integration/monitor/history-samples', json=first)).status_code == 200
        assert (await client.post('/integration/monitor/history-samples', json=second)).status_code == 200
        rows = session.execute(select(HistorySample)).scalars().all()
        assert len(rows) == 2 and rows[0].observed_at == rows[1].observed_at and rows[0].id != rows[1].id


@pytest.mark.asyncio
async def test_no_enabled_history_returns_idempotent_receipt_without_row(app_and_db):
    app, session, profile, producer = app_and_db
    binding = session.get(SlotBinding, ('history','heatZone1',7)); binding.enabled = False; session.commit()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1',
                                 headers={'Authorization':'Bearer fixture'}) as client:
        first = await client.post('/integration/monitor/history-samples', json=document())
        assert first.status_code == 200 and first.json()['data']['outcome'] == 'no_history_metrics'
        assert (await client.post('/integration/monitor/history-samples', json=document())).json() == first.json()
        assert session.execute(select(HistorySample)).scalars().all() == []


@pytest.mark.asyncio
async def test_v1_receipt_replays_before_v2_required_fields_and_remains_scoped(app_and_db):
    app, session, profile, producer = app_and_db
    producer.update(kind='external', sourceId='source', mappingId='mapping', mappingRevision='r1')
    old = {'sourceRefs':[{'kind':'external_event','sourceEventId':'old-sample'}],
           'data':{'equipmentId':'line','groupKey':'heatZone1','taskNo':'000042',
                   'sampledAt':'2026-11-17T12:00:00+08:00','values':{'actual':0}}}
    normalized = legacy_ingest.normalize(old, producer, 'latest')
    normalized['mappingId'], normalized['mappingRevision'] = 'mapping', 'r1'
    session.add(Receipt(target='latest',producer_id='writer',event_id=normalized['eventId'],
        request_digest=legacy_ingest.fingerprint(normalized),outcome='stored',processed_at=datetime(2026,11,17,12),
        result_record_id=9,mapping_id='mapping',mapping_revision='r1',source_refs=normalized['sourceRefs'],
        task_evidence={'pointId':'expired'},contract_version='aiis.metric-ingest/v1',result_version='r8'))
    session.commit()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1',
                                 headers={'Authorization':'Bearer fixture'}) as client:
        replay = await client.post('/integration/equipment/latest-snapshots', json=old)
        assert replay.status_code == 200 and replay.json()['data']['recordId'] == '9'
        assert replay.json()['data']['resultLocation'] == 'equipment_status_r8_archive'
        changed = {'sourceRefs':old['sourceRefs'], 'data':{**old['data'],'values':{'actual':1}}}
        assert (await client.post('/integration/equipment/latest-snapshots', json=changed)).status_code == 409
        assert session.execute(select(LatestSnapshot)).scalars().all() == []
        for grant in producer['grants']:
            if grant['groupKey'] == 'heatZone1': grant['metricKeys'] = []
        assert (await client.post('/integration/equipment/latest-snapshots', json=old)).status_code == 403


@pytest.mark.asyncio
async def test_replacement_cannot_clear_another_writers_group(app_and_db, monkeypatch):
    app, session, profile, producer = app_and_db
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1',
                                 headers={'Authorization':'Bearer fixture'}) as client:
        assert (await client.post('/integration/equipment/latest-snapshots', json=document())).status_code == 200
        limited = {'producerId':'limited','kind':'other','grants':[{'equipmentId':'line','groupKey':'heatZone1',
                   'target':'latest','metricKeys':['actual']}]}
        profile['producers']['limited'] = limited
        monkeypatch.setattr(routes, 'authenticate', lambda _profile, _header: limited)
        limited_doc = document('narrow','2026-11-17T12:00:03+08:00'); limited_doc['data']['groups'] = {'heatZone1':{'actual':3}}
        result = await client.post('/integration/equipment/latest-snapshots', json=limited_doc)
        assert result.status_code == 403
        assert session.execute(select(Receipt).where(Receipt.event_id=='narrow')).scalar_one_or_none() is None
        row = session.execute(select(LatestSnapshot)).scalar_one()
        assert row.local_values['production']['01'] == '' and row.local_values['driveRoll1']['01'] is False


@pytest.mark.asyncio
async def test_meter_configuration_ingest_and_separate_statistics(app_and_db):
    app, session, profile, producer = app_and_db
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1',
                                 headers={'Authorization':'Bearer fixture'}) as client:
        configs = [('meter1','reading',1,'cumulative','energy','kWh'), ('meter1','power',2,'instantaneous','power','kW'),
                   ('meter1','interval',3,'interval','energy','kWh'), ('meter2','reading',1,'interval','energy','kWh')]
        for meter, key, slot, mode, quantity, unit in configs:
            data = {'meterId':meter, 'groupKey':'electricity','metricKey':key,'slotNo':slot,'nameZh':key,'nameEn':key,
                    'valueType':'number','quantityKey':quantity,'measurementMode':mode,'unit':unit,'enabled':True,
                    'rules':{'continuityConfirmed':True,'maxGapSeconds':3600}}
            assert (await client.post('/energy/metric-configs', json=data)).status_code == 200
        found = await client.get('/integration/energy/metric-definitions', params={'meterId':'meter2','groupKey':'electricity'})
        assert found.status_code == 200 and found.json()['data']['definitions'][0]['measurementMode'] == 'interval'
        def energy(event, meter, time, values, start=None, end=None):
            data = {'meterId':meter,'groupKey':'electricity','observedAt':f'2026-11-17T{time}+08:00','quality':'good','values':values}
            if start is not None:
                data.update(intervalStartAt=f'2026-11-17T{start}+08:00', intervalEndAt=f'2026-11-17T{end}+08:00')
            return {'eventId':event,'data':data}
        samples = [energy('m1-0','meter1','08:00:00',{'reading':1000,'power':10}),
                   energy('m1-1','meter1','08:30:00',{'reading':1003,'interval':2},'08:00:00','08:30:00'),
                   energy('m1-2','meter1','09:00:00',{'reading':1006,'interval':3},'08:30:00','09:00:00'),
                   energy('m2-1','meter2','08:30:00',{'reading':2},'08:00:00','08:30:00'),
                   energy('m2-2','meter2','09:00:00',{'reading':3},'08:30:00','09:00:00')]
        receipts = []
        for sample in samples:
            result = await client.post('/integration/energy/samples', json=sample)
            assert result.status_code == 200, result.text
            receipts.append(result.json()['data'])
        assert (await client.post('/integration/energy/samples', json=samples[-1])).json()['data'] == receipts[-1]
        changed = energy('m2-2','meter2','09:00:00',{'reading':4},'08:30:00','09:00:00')
        assert (await client.post('/integration/energy/samples', json=changed)).status_code == 409
        params = {'groupKey':'electricity','metricKey':'reading','from':'2026-11-17T08:00:00+08:00',
                  'to':'2026-11-17T09:00:00+08:00'}
        first = await client.get('/energy/consumption/summary', params={**params, 'meterId':'meter1'})
        second = await client.get('/energy/consumption/summary', params={**params, 'meterId':'meter2'})
        assert first.status_code == second.status_code == 200
        assert first.json()['data']['amount'] == 6 and second.json()['data']['amount'] == 5
        power = await client.get('/energy/consumption/summary', params={**params, 'meterId':'meter1','metricKey':'power'})
        assert power.json()['data']['amount'] is None and power.json()['data']['reason'] == 'instantaneous_not_usage'
        assert (await client.patch('/energy/metric-configs/meter1/electricity/reading', json={'unit':'MWh'})).status_code == 409
        assert len(session.execute(select(EnergySample)).scalars().all()) == 5


@pytest.mark.asyncio
async def test_ordinary_energy_reader_is_limited_to_granted_meters_and_cannot_manage(app_and_db):
    app, session, profile, producer = app_and_db
    app.state.role_api_permissions = {'operator': {'energy-consumption-read'}}
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role='operator')
    profile['meterReadScopes']['operator'] = ['meter1']
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1') as client:
        assert (await client.get('/energy/consumption/samples', params={'meterId':'meter1'})).status_code == 200
        assert (await client.get('/energy/consumption/samples', params={'meterId':'meter2'})).status_code == 403
        assert (await client.get('/energy/metric-configs', params={'meterId':'meter1'})).status_code == 403


@pytest.mark.asyncio
async def test_disabling_group_hides_cards_and_curves_without_stopping_history(app_and_db):
    app, session, profile, producer = app_and_db
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test/api/v1',
                                 headers={'Authorization':'Bearer fixture'}) as client:
        disabled = await client.patch('/equipment/metric-groups/heatZone1', json={'enabled':False})
        assert disabled.status_code == 200
        assert (await client.post('/integration/equipment/latest-snapshots', json=document())).status_code == 200
        assert (await client.post('/integration/monitor/history-samples', json=document())).status_code == 200
        assert session.execute(select(HistorySample)).scalar_one().local_values['heatZone1'] == {'07':0}
        cards = (await client.get('/equipment/latest-cards', params={'equipmentId':'line','pageKey':'temperature'})).json()['data']
        query = {'equipmentId':'line','category':'temperature','taskNo':'000042',
                 'from':'2026-11-17T11:59:00+08:00','to':'2026-11-17T12:01:00+08:00'}
        curves = (await client.get('/monitor/history-curves', params=query)).json()['data']
        assert cards['cards'] == [] and curves['groups'] == []
        assert (await client.patch('/equipment/metric-groups/heatZone1', json={'enabled':True})).status_code == 200
        cards = (await client.get('/equipment/latest-cards', params={'equipmentId':'line','pageKey':'temperature'})).json()['data']
        curves = (await client.get('/monitor/history-curves', params=query)).json()['data']
        assert cards['cards'][0]['items'][0]['value'] == 0
        assert curves['groups'][0]['series'][0]['points'][0]['value'] == 0
