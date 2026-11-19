"""有限采用/时间纯合同与owner探针；无数据库/SQLite/网络。"""
from copy import deepcopy
from datetime import datetime, timezone
import importlib
import json
from types import SimpleNamespace
import pytest
from common.integration.storage import (StorageProbe, parse_adoption_manifest, validate_adoption_probe, to_storage_time, to_legacy_time)

pytestmark=pytest.mark.no_db


def manifest(owner):
    profile=importlib.import_module(f"app.{owner}.integration_storage").BUSINESS_TIME_COLUMN_PROFILE
    return dict(version="business-time-adoption/v1",profile="shanghai-v1",module=owner,serverUuid="fixture-server",
        schema="fixture_schema",schemaRevision="1b3d5f7a9c20",sourceRevision="fixture-source",
        fixedColumnDigest=profile["digest"],basisProfile=dict(profileId="be010.fixed-basis/v1",legacyNaive="utc_wall",systemWire="utc_wall",
            **(dict(manualNaive="shanghai_wall",manualAuditWire="utc_wall") if owner=="performance" else {})),
        reports={kind:dict(reference="private:"+kind,digest="sha256:"+"0"*64) for kind in ("inspection","migration","verification")},
        backupRef="private:backup",ownerApprovalRef="fixture-approved-target",verifiedAt="2026-11-04T10:00:00.000+08:00",state="adopted")


@pytest.mark.parametrize('owner', ('performance',))
@pytest.mark.parametrize('revision', ('2c4e6a8b0d12', '3d5f7a9c1e23', '4e6a8b0d2f14',
    '5f7a9c1e3b25', '6a8c0e2b4d16', '7b9d1f3a5c7e', '8c0e2a4d6f18', '9d1f3a5c7e20', 'ae20b4d6f831', 'c9e1a3b5d720'))
def test_successor_requires_matching_fresh_adoption(owner, revision):
    old = manifest(owner)
    new = deepcopy(old)
    new['schemaRevision'] = revision
    assert parse_adoption_manifest(new, owner) == new
    probe = StorageProbe('fixture-server', 'fixture_schema', revision, datetime(2026, 11, 4, 2))
    with pytest.raises(ValueError):
        validate_adoption_probe(old, probe)
    assert validate_adoption_probe(new, probe).manifest == new
    with pytest.raises(ValueError):
        validate_adoption_probe(new, StorageProbe('wrong-server', probe.schema, probe.schema_revision, probe.utc_now))
    with pytest.raises(ValueError):
        validate_adoption_probe(new, StorageProbe(probe.server_uuid, 'wrong_schema', probe.schema_revision, probe.utc_now))
    new['schemaRevision'] = 'unrecognized'
    with pytest.raises(ValueError):
        parse_adoption_manifest(new, owner)


@pytest.mark.parametrize("owner",("performance",))
@pytest.mark.parametrize("revision",("1b3d5f7a9c20","ae20b4d6f831","c9e1a3b5d720"))
def test_exact_profile_and_adoption_rejection(owner,revision,tmp_path):
    module=importlib.import_module(f"app.{owner}.integration_config")
    prefix=owner.upper()+"_INTEGRATION_"
    evidence={**manifest(owner), "schemaRevision":revision}
    assert parse_adoption_manifest(evidence,owner)==evidence
    file=tmp_path/"adoption.json";file.write_text(json.dumps(evidence))
    config=module.IntegrationConfig(_env_file=None,**{prefix+"ENABLED":True,prefix+"EQUIPMENT_IDS_JSON":'["line-demo"]',prefix+"PRODUCER_IDS_JSON":'["sma-demo"]',prefix+"STORAGE_PROFILE":"shanghai-v1",prefix+"ADOPTION_FILE":str(file)})
    assert config.require_ready("line-demo","sma-demo")==evidence
    for equipment, producer in (("other","sma-demo"), ("line-demo","other")):
        with pytest.raises(Exception):
            config.require_ready(equipment,producer)
    for path,value in [("schemaRevision","wrong"),("fixedColumnDigest","sha256:"+"f"*64),("state","candidate")]:
        broken=deepcopy(evidence);broken[path]=value;file.write_text(json.dumps(broken))
        with pytest.raises(Exception):config.require_ready("line-demo","sma-demo")
    for field,value in [("legacyNaive","unknown"),("profileId","cohort/v1"),("extra","utc_wall")]:
        broken=deepcopy(evidence);broken["basisProfile"][field]=value
        with pytest.raises(ValueError):parse_adoption_manifest(broken,owner)
    del evidence["basisProfile"]["systemWire"]
    with pytest.raises(ValueError):parse_adoption_manifest(evidence,owner)


def test_aware_naive_inverse():
    utc=datetime(2026,11,3,17,1,2,123000)
    shanghai=to_storage_time(utc,"utc_wall")
    assert shanghai==datetime(2026,11,4,1,1,2,123000)
    assert to_storage_time(shanghai,"shanghai_wall")==shanghai
    assert to_storage_time(utc.replace(tzinfo=timezone.utc),"shanghai_wall")==shanghai
    assert to_legacy_time(shanghai,"utc_wall")==utc
    assert to_legacy_time(shanghai,"shanghai_wall")==shanghai
    assert to_storage_time(None,"utc_wall") is None
    with pytest.raises(ValueError):to_storage_time(utc,"unknown")




@pytest.mark.skip(reason="retired coil production integration; historical BE-010 evidence")
async def test_production_locks_active_and_inactive_target_in_one_sorted_current_read():
    from app.performance.crud.async_integration import active_records
    from sqlalchemy.dialects.mysql import dialect
    queries=[]
    class Capture:
        async def execute(self,statement):queries.append(statement);return self
        def scalars(self):return self
        def all(self):return []
    await active_records(Capture(),"line-demo","old-inactive")
    assert len(queries)==1
    sql=str(queries[0].compile(dialect=dialect(),compile_kwargs={"literal_binds":True}))
    assert " OR " in sql and "old-inactive" in sql and "ORDER BY performance_main.id" in sql and sql.endswith("FOR UPDATE")


@pytest.mark.parametrize('source',('external_observation','unplanned_plc','manual_entry'))
@pytest.mark.parametrize('legacy_basis,system_basis,manual_basis,audit_basis',[
    ('shanghai_wall','utc_wall','shanghai_wall','utc_wall'),
    ('utc_wall','shanghai_wall','utc_wall','shanghai_wall'),
])
@pytest.mark.skip(reason="retired coil performance GET; historical BE-010 evidence")
async def test_adopted_old_get_preserves_known_utc_and_other_proven_bases(source,legacy_basis,system_basis,manual_basis,audit_basis,monkeypatch):
    """旧受保护GET实际DTO/serializer；预期由来源事实独立给定，不调用被测basis选择器。"""
    from datetime import date
    from decimal import Decimal
    from fastapi import FastAPI
    from httpx import AsyncClient,ASGITransport
    from app.performance.models.performance import Performance
    from app.performance.api import routes
    from app.performance.services import async_performance
    from common.integration.envelope import source_time
    from database import get_db
    evidence=manifest('performance');evidence['basisProfile'].update(legacyNaive=legacy_basis,systemWire=system_basis,manualNaive=manual_basis,manualAuditWire=audit_basis)
    parse_adoption_manifest(evidence,'performance')
    values={column.key:None for column in Performance.__table__.columns}
    values.update(id=101,coil_no='HTTP-COIL',equipment_id='line-demo'if source=='external_observation'else None,http_coil_key=b'HTTP-COIL'if source=='external_observation'else None,parent_coil_no='HTTP-COIL',production_date=date(2026,11,4),is_split=False,record_source=source,observation_status='in_production',first_observed_at=datetime(2026,11,3,17,0,0,123000),last_observed_at=datetime(2026,11,3,17,5,0,123000),reported_start_time=datetime(2026,11,3,16,59),reported_end_time=datetime(2026,11,3,17,5),start_time=datetime(2026,11,3,16,58),end_time=datetime(2026,11,3,17,4),manual_override_at=datetime(2026,11,3,17),manual_override_weight=0,effective_weight=0,weight=0,collected_weight=12,effective_weight_source='manual_override_weight',total_duration_seconds=360,total_duration_source='manual_time',created_at=datetime(2026,11,3,17),updated_at=datetime(2026,11,3,17,5))
    old=SimpleNamespace(__table__=Performance.__table__,**values)
    physical_values=dict(values)
    groups={'reported_start_time':'utc_wall','reported_end_time':'utc_wall',
        'first_observed_at':'utc_wall'if source=='external_observation'else legacy_basis,
        'last_observed_at':'utc_wall'if source=='external_observation'else legacy_basis,
        'start_time':manual_basis,'end_time':manual_basis,'manual_override_at':audit_basis,
        'created_at':system_basis,'updated_at':system_basis}
    for field,basis in groups.items():physical_values[field]=to_storage_time(physical_values[field],basis)
    physical=SimpleNamespace(__table__=Performance.__table__,**physical_values);before=dict(physical.__dict__)
    state={'adopted':False}
    async def context(db):return(evidence,source_time('2026-11-04T10:00:00+08:00'))if state['adopted']else None
    async def get_by_id(db,record_id):return physical if state['adopted']else old
    async def db_dependency():yield object()
    app=FastAPI();app.include_router(routes.router,prefix='/api/v1');app.dependency_overrides[get_db]=db_dependency
    for route in app.routes:
        if getattr(route,'path',None)=='/api/v1/performances/{performance_id}'and'GET'in route.methods:
            for dependency in route.dependant.dependencies:
                if dependency.name=='current_user':app.dependency_overrides[dependency.call]=lambda:SimpleNamespace(role='admin')
    monkeypatch.setattr(async_performance,'storage_context',context)
    monkeypatch.setattr(routes.async_performance_service,'get_by_id',get_by_id)
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://fixture')as client:
        original=await client.get('/api/v1/performances/101');state['adopted']=True
        adopted=await client.get('/api/v1/performances/101')
    assert original.status_code==adopted.status_code==200
    assert original.json()['data']==adopted.json()['data']
    assert Decimal(adopted.json()['data']['manualOverrideWeight'])==0
    assert adopted.json()['data']['productionDate']=='2026-11-04'
    assert physical.__dict__==before
