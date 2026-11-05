"""新八类真实Service的CRUD替身；验证事务/目标/回执/父来源，绝不模拟SQL数据库。"""
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
import importlib
from types import SimpleNamespace
import pytest
from common.exceptions import BusinessException
from common.integration.envelope import source_time
from tests.test_business_integration_contract import example,REQUESTS,RESOURCES
from tests.test_business_integration_storage import manifest
from app.plan.models.plan import Plan  # explicit relationship target for no-conftest pure runs

pytestmark=pytest.mark.no_db


class DB:
    def __init__(self):self.commits=0;self.rollbacks=0;self.fail_commit=False;self.flushes=0
    async def flush(self):self.flushes+=1
    async def refresh(self,row,**kwargs):pass
    async def commit(self):
        self.commits+=1
        if self.fail_commit:raise RuntimeError("SECRET unknown commit")
    async def rollback(self):self.rollbacks+=1


@pytest.fixture
def world(monkeypatch):
    stores={owner:dict(receipts={},records={},events={},state=None,next=1) for owner in ("equipment","performance","monitor")}
    for owner,store in stores.items():
        crud=importlib.import_module(f"app.{owner}.crud.async_integration")
        async def probe(db,adoption):return source_time("2026-11-04T10:01:00.123+08:00")
        async def get_receipt(db,producer,event,store=store):return store["receipts"].get((producer,event))
        async def add_receipt(db,store=store,**values):
            row=SimpleNamespace(id=store["next"],**values);store["next"]+=1
            store["receipts"][(values["producer_id"].decode(),values["event_id"].decode())]=row
            return row
        monkeypatch.setattr(crud,"probe_adoption",probe);monkeypatch.setattr(crud,"get_receipt",get_receipt);monkeypatch.setattr(crud,"add_receipt",add_receipt)
    eq=importlib.import_module("app.equipment.crud.async_integration");store=stores["equipment"]
    async def get_eq(db,resource,data,time):return stores["equipment"]["records"].get((resource,data.equipment_id,time,getattr(data,"coil_no",None)))
    async def add_eq(db,resource,**values):
        table=eq.MODELS[resource]
        row=table(id=stores["equipment"]["next"],**values);stores["equipment"]["next"]+=1
        stores["equipment"]["records"][(resource,values["equipment_id"],values.get("sampled_at",values.get("timestamp")),values.get("coil_no"))]=row
        return row
    async def eq_floats(db,resource,record_id):
        row=next(row for row in stores["equipment"]["records"].values()if row.id==record_id)
        return {field:getattr(row,field)for field in eq._FLOAT_FIELDS.get(resource,())}
    monkeypatch.setattr(eq,"get_record",get_eq);monkeypatch.setattr(eq,"add_record",add_eq);monkeypatch.setattr(eq,"stored_float_values",eq_floats)
    monitor=importlib.import_module("app.monitor.crud.async_integration")
    async def get_curve(db,equipment,time):return stores["monitor"]["records"].get((equipment,time))
    async def add_curve(db,**values):
        row=monitor.Curve(id=stores["monitor"]["next"],**values);stores["monitor"]["next"]+=1
        stores["monitor"]["records"][(values["equipment_id"],values["sampled_at"])]=row
        return row
    async def curve_floats(db,record_id):
        row=next(row for row in stores["monitor"]["records"].values()if row.id==record_id)
        return {field:getattr(row,field)for field in monitor._FLOAT_FIELDS}
    monkeypatch.setattr(monitor,"get_record",get_curve);monkeypatch.setattr(monitor,"add_record",add_curve);monkeypatch.setattr(monitor,"stored_float_values",curve_floats)
    perf=importlib.import_module("app.performance.crud.async_integration")
    async def state(db,equipment,now):
        store=stores["performance"]
        if store["state"] is None:store["state"]=SimpleNamespace(last_sampled_at=None,created_at=now,updated_at=now)
        return store["state"]
    async def event(db,equipment,time):return stores["performance"]["events"].get((equipment,time))
    async def add_event(db,**values):
        row=SimpleNamespace(**values);stores["performance"]["events"][(values["equipment_id"],values["sampled_at"])]=row;return row
    async def active(db,equipment,target_coil=None):return sorted([r for r in stores["performance"]["records"].values() if isinstance(r,perf.Performance) and r.equipment_id==equipment and (r.observation_status in ("in_production","unknown") or r.coil_no==target_coil)],key=lambda row:row.id)
    async def add_perf(db,**values):
        row=perf.Performance(id=101+len(stores["performance"]["records"]),**values);stores["performance"]["records"][row.id]=row;return row
    async def parent(db,parent_id):return stores["performance"]["records"].get(parent_id)
    async def parent_event(db,equipment,parent_id):return next((1 for e in stores["performance"]["events"].values() if e.equipment_id==equipment and e.performance_id==parent_id and e.observation_status=="in_production"),None)
    async def get_process(db,kind,parent_id,data,time):return stores["performance"]["records"].get((kind,parent_id,data.zone,time))
    async def add_process(db,kind,**values):
        row=perf.MODELS[kind](id=201+len(stores["performance"]["records"]),**values);stores["performance"]["records"][(kind,values["performance_id"],values["zone"],values["record_time"])]=row;return row
    for name,fn in dict(state_for_update=state,get_event=event,add_event=add_event,active_records=active,add_performance=add_perf,parent=parent,parent_event=parent_event,get_process=get_process,add_process=add_process).items():monkeypatch.setattr(perf,name,fn)
    return stores


async def receive(index,payload,db):
    owner=("equipment",)*3+("performance",)*4+("monitor",)
    request=REQUESTS[index].model_validate(payload)
    if index<3:
        from app.equipment.services.async_integration import receive_sample
        return await receive_sample(db,request,manifest(owner[index]),RESOURCES[index])
    if index==3:
        from app.performance.services.async_integration_observation import receive_observation
        return await receive_observation(db,request,manifest("performance"))
    if index<7:
        from app.performance.services.async_integration_process import receive_sample
        return await receive_sample(db,request,manifest("performance"),101,RESOURCES[index].removeprefix("process_"))
    from app.monitor.services.async_integration import receive_sample
    return await receive_sample(db,request,manifest("monitor"))


@pytest.mark.parametrize("index",range(8))
async def test_all_eight_real_service_targets_and_stable_receipt(index,world):
    db=DB()
    if index in (4,5,6):await receive(3,example(3),db)
    payload=example(index);payload["eventId"]="target"
    first=await receive(index,payload,db)
    again=await receive(index,payload,db)
    assert first.record_id is not None and first.status=="committed"
    assert first.source_time.isoformat().endswith("+08:00")
    assert again.outcome=="duplicate" and again.original_outcome==first.outcome and again.committed_at==first.committed_at
    assert again.record_id==first.record_id and again.receipt_id==first.receipt_id
    owner=("equipment",)*3+("performance",)*4+("monitor",)
    receipt=world[owner[index]]["receipts"][("sma-demo","target")]
    assert receipt.source_refs==payload["sourceRefs"] and receipt.mapping_revision==payload["mappingRevision"]
    assert receipt.source_time==datetime(2026,11,4,10,0,0,123000)
    assert db.commits==(3 if index in (4,5,6) else 2)
    changed=deepcopy(payload);changed["mappingRevision"]="different"
    with pytest.raises(BusinessException) as conflict:await receive(index,changed,db)
    assert conflict.value.code==409 and str(conflict.value.error_code).endswith("event_conflict")


@pytest.mark.parametrize("index,field",[(0,"zone1Set"),(1,"tv"),(2,"weight"),(7,"z6TempAct")])
async def test_immutable_or_partial_conflict_rolls_back(index,field,world):
    db=DB();payload=example(index);await receive(index,payload,db)
    payload["eventId"]="changed";payload["data"][field]=1
    with pytest.raises(BusinessException) as caught:await receive(index,payload,db)
    assert caught.value.code==409 and db.rollbacks>=1


async def test_partial_null_fill_and_process_post_merge_range(world):
    db=DB();payload=example(1);first=await receive(1,payload,db)
    payload["eventId"]="fill";payload["data"].pop("tv");payload["data"]["km"]=0
    filled=await receive(1,payload,db)
    assert filled.outcome=="updated" and filled.changed_fields==["km"] and filled.record_id==first.record_id
    await receive(3,example(3),db)
    payload=example(4);payload["eventId"]="min";payload["data"]={**payload["data"],"minTemp":10};await receive(4,payload,db)
    payload["eventId"]="max";payload["data"].pop("minTemp");payload["data"]["maxTemp"]=5
    with pytest.raises(BusinessException) as caught:await receive(4,payload,db)
    assert caught.value.code==422


async def test_production_history_stale_zero_active_and_manual_zero(world):
    db=DB();first=await receive(3,example(3),db)
    row=world["performance"]["records"][101];row.manual_override_weight=Decimal(0);row.effective_weight=Decimal(0);row.weight=Decimal(0)
    payload=example(3);payload["eventId"]="newer";payload["data"]["sampledAt"]="2026-11-04T10:00:01.123+08:00";payload["data"]["weight"]=1
    await receive(3,payload,db)
    assert row.weight==0 and row.effective_weight==0 and row.collected_weight==1
    payload=example(3);payload["eventId"]="historical"
    duplicate=await receive(3,payload,db);assert duplicate.outcome=="duplicate" and duplicate.record_id==first.record_id
    payload["eventId"]="stale";payload["data"]["sampledAt"]="2026-11-04T09:59:59.123+08:00"
    stale=await receive(3,payload,db);assert stale.confirmation=="decision_only" and not stale.applied and stale.record_id is None
    payload["eventId"]="exit";payload["data"]={"equipmentId":"line-demo","sampledAt":"2026-11-04T10:00:02.123+08:00","quality":"good","observationStatus":"not_in_production"}
    await receive(3,payload,db)
    payload["eventId"]="zero-active";payload["data"]["sampledAt"]="2026-11-04T10:00:03.123+08:00"
    result=await receive(3,payload,db);assert not result.applied and world["performance"]["state"].last_sampled_at.second==3


async def test_missing_parent_and_commit_unknown_without_blind_retry(world):
    db=DB()
    with pytest.raises(BusinessException) as missing:await receive(4,example(4),db)
    assert missing.value.code==404 and not world["performance"]["receipts"]
    db.fail_commit=True
    with pytest.raises(BusinessException) as unknown:await receive(1,example(1),db)
    assert unknown.value.code==503 and str(unknown.value.error_code).endswith("commit_unknown") and db.commits==1


async def test_failed_cleanup_cannot_erase_commit_unknown(world):
    class BrokenCleanup(DB):
        async def rollback(self):raise RuntimeError('synthetic unavailable connection')
    db=BrokenCleanup();db.fail_commit=True
    with pytest.raises(BusinessException) as caught:await receive(1,example(1),db)
    assert caught.value.code==503 and str(caught.value.error_code).endswith('commit_unknown')
    assert db.commits==1



async def test_reactivation_locks_inactive_target_with_active_rows(world):
    db=DB();first=await receive(3,example(3),db)
    payload=example(3);payload["eventId"]="switch";payload["data"]["coilNo"]="next";payload["data"]["sampledAt"]="2026-11-04T10:00:01.123+08:00"
    second=await receive(3,payload,db)
    assert second.record_id>first.record_id
    payload=example(3);payload["eventId"]="reactivate";payload["data"]["sampledAt"]="2026-11-04T10:00:02.123+08:00"
    result=await receive(3,payload,db)
    assert result.record_id==first.record_id and result.outcome=="updated"
    assert world["performance"]["records"][second.record_id].observation_status=="not_in_production"


@pytest.mark.parametrize('owner,index,resource,request_type,receipt_type,filename',[
    ('equipment',1,'drive','DriveRequest','DriveReceipt','async_integration'),
    ('performance',4,'process_temperature','ProcessTemperatureRequest','ProcessTemperatureReceipt','async_integration_observation'),
    ('monitor',7,'process_curve','ProcessCurveRequest','ProcessCurveReceipt','async_integration'),
])
@pytest.mark.parametrize('mode,failures,number,attempts,status',[
    ('named',2,1062,3,None),('named',3,1062,3,503),('other',1,1062,1,500),('named',1,1213,1,500),
])
async def test_precommit_named_unique_recovery_remains_bounded(owner,index,resource,request_type,receipt_type,filename,mode,failures,number,attempts,status,monkeypatch):
    from sqlalchemy.exc import IntegrityError
    from common.integration.envelope import source_time
    service=importlib.import_module(f'app.{owner}.services.{filename}')
    dto=importlib.import_module(f'app.{owner}.schemas.integration')
    request=getattr(dto,request_type).model_validate(example(index));db=DB();calls=[]
    async def probe(*args):calls.append('probe');return source_time('2026-11-04T11:00:00+08:00')
    async def receipt(*args):calls.append('read');return None
    async def add_receipt(*args,**values):return SimpleNamespace(id=501,**values)
    async def apply(*args):
        calls.append('apply')
        if calls.count('apply')<=failures:
            key='uq_'+owner+'_integration_delivery'if mode=='named'else'not-approved-key'
            raise IntegrityError('private SQL',{},Exception(number,"Duplicate entry 'private' for key '"+key+"'"))
        return dict(recordId=101,performanceId=101 if owner=='performance'else None,affectedRecordIds=[101],confirmation='business_committed',applied=True,outcome='created',changedFields=[]),{}
    monkeypatch.setattr(service.crud,'probe_adoption',probe);monkeypatch.setattr(service.crud,'get_receipt',receipt);monkeypatch.setattr(service.crud,'add_receipt',add_receipt)
    if status is None:await service.transaction(db,request,manifest(owner),resource,getattr(dto,receipt_type),apply,101 if owner=='performance'else None)
    else:
        with pytest.raises(BusinessException)as caught:await service.transaction(db,request,manifest(owner),resource,getattr(dto,receipt_type),apply,101 if owner=='performance'else None)
        assert caught.value.code==status
    assert calls.count('apply')==attempts and db.commits==int(status is None)
    assert db.rollbacks==min(failures,attempts)
    assert calls[:2]==['probe','read']


async def test_new_performance_explicitly_refreshes_mysql_expression_defaults_before_rules():
    """B真实MySQL MissingGreenlet回归：规则访问前显式await刷新SQL表达式NULL列。"""
    from app.performance.crud.async_integration import add_performance
    from sqlalchemy.sql.elements import Null
    calls=[]
    names=('output_quantity','qualified_quantity','efficiency_rate','quality_score')
    class Database:
        def add(self,row):self.row=row;calls.append('add')
        async def flush(self):
            assert all(isinstance(getattr(self.row,name),Null)for name in names)
            calls.append('flush')
        async def refresh(self,row,**kwargs):
            assert row is self.row and kwargs=={'with_for_update':True}
            assert calls==['add','flush']
            for name in names:setattr(row,name,None)
            calls.append('refresh')
    db=Database();row=await add_performance(db,coil_no='synthetic',parent_coil_no='synthetic')
    assert calls==['add','flush','refresh']and all(getattr(row,name)is None for name in names)


@pytest.mark.parametrize('index',(1,7))
async def test_float_comparison_uses_exact_physical_projection_not_text_display(index,world,monkeypatch):
    """B文本FLOAT仅0.1，DOUBLE为真实binary32；首写、重放及异内容冲突保持原合同。"""
    import struct
    owner='equipment'if index==1 else'monitor'
    module=importlib.import_module('app.'+owner+'.crud.async_integration')
    field='tv'if index==1 else'line_speed_set'
    wire='tv'if index==1 else'lineSpeedSet'
    exact=struct.unpack('!f',struct.pack('!f',0.1))[0]
    calls=[]
    async def physical(db,*args):
        calls.append(args)
        return {field:exact}
    monkeypatch.setattr(module,'stored_float_values',physical)
    class TextDatabase(DB):
        async def refresh(self,row,**kwargs):setattr(row,field,0.1)
    db=TextDatabase();payload=example(index);payload['data'][wire]=Decimal('0.1')
    first=await receive(index,payload,db);assert first.outcome=='created'
    replay=await receive(index,payload,db);assert replay.receipt_id==first.receipt_id and replay.outcome=='duplicate'
    same=deepcopy(payload);same['eventId']+='-business';again=await receive(index,same,db);assert again.record_id==first.record_id and again.outcome=='duplicate'
    changed=deepcopy(payload);changed['eventId']+='-conflict';changed['data'][wire]=Decimal('0.2')
    with pytest.raises(BusinessException)as exc:await receive(index,changed,db)
    assert exc.value.code==409 and str(exc.value.error_code).endswith('value_conflict')
    assert calls and db.commits==3


@pytest.mark.parametrize('owner,resource,count',(('equipment','drive',20),('equipment','production_parameters',5),('monitor',None,21)))
async def test_physical_float_projection_emits_mysql_double_cast_for_fixed_columns(owner,resource,count):
    from sqlalchemy.dialects.mysql import dialect
    module=importlib.import_module('app.'+owner+'.crud.async_integration');queries=[]
    class Capture:
        async def execute(self,statement):queries.append(statement);return self
        def mappings(self):return self
        def one(self):return {}
    db=Capture()
    if owner=='equipment':await module.stored_float_values(db,resource,101)
    else:await module.stored_float_values(db,101)
    assert len(queries)==1
    mysql84=dialect();mysql84.server_version_info=(8,4,6)
    sql=str(queries[0].compile(dialect=mysql84,compile_kwargs={'literal_binds':True}))
    assert sql.count('CAST(')==count and sql.count(' AS DOUBLE)')==count and sql.endswith('FOR UPDATE'),sql
    if owner=='equipment':
        queries.clear();assert await module.stored_float_values(db,'temperature',101)=={} and queries==[]
