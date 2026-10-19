"""BE006无DB持久事务替身；仅证明Service行为，不替代MySQL证据。"""
from copy import deepcopy
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from common.exceptions import BusinessException
from app.equipment.schemas.drive_sample_in import DriveSampleIn
from app.equipment.services import async_drive_sample as equipment
from app.performance.schemas.production_observation_in import ProductionObservationIn
from app.performance.schemas.process_sample_in import ProcessTemperatureIn
from app.performance.services import async_production_observation as production, async_process_sample as process
from app.monitor.schemas.process_curve_in import ProcessCurveIn
from app.monitor.services import async_process_curve_sample as monitor

pytestmark = pytest.mark.no_db

def identity(**changes):
    return dict(dict(equipmentId="line-A", sampleId="sample-A", sampledAt="2026-10-16T10:00:00.123Z", quality="good"), **changes)

class MemoryTransactions:
    def __init__(self):
        self.rows = {}
        self.receipts = {}
        self.states = {}
        self.durable = ({}, {}, {})
        self.commits = 0
        self.rollbacks = 0
        self.fail = None
    async def flush(self):
        if self.fail == "flush":
            raise RuntimeError("private synthetic flush failure")
    async def refresh(self, row, **kwargs):
        if self.fail == "refresh":
            raise RuntimeError("private synthetic refresh failure")
    async def commit(self):
        if self.fail == "commit":
            raise RuntimeError("private synthetic commit failure")
        self.commits += 1
        self.durable = deepcopy((self.rows, self.receipts, self.states))
    async def rollback(self):
        self.rollbacks += 1
        self.rows, self.receipts, self.states = deepcopy(self.durable)
    def add_row(self, stream, values):
        values = dict(values)
        values.setdefault("id", len(self.rows)+1)
        row = SimpleNamespace(**values)
        self.rows[(stream,row.id)] = row
        return row
    def install(self, monkeypatch):
        from app.equipment.crud import async_mapping_ingest as er, async_drive_sample as ed, async_production_parameter_sample as ep
        from app.performance.crud import async_mapping_ingest as pr, async_production_observation as po, async_process_sample as pc
        from app.monitor.crud import async_mapping_ingest as mr, async_process_curve_sample as mc
        async def receipt(db,actor,equipment,stream,sample_id):
            return db.receipts.get((actor,equipment,stream,sample_id))
        async def add_receipt(db,**values):
            if db.fail == "receipt":
                raise RuntimeError("private synthetic receipt failure")
            key = (values["actor_user_id"],values["equipment_id"],values["stream"],values["sample_id"])
            row = SimpleNamespace(**values)
            db.receipts[key] = row
            return row
        for module in (er,pr):
            monkeypatch.setattr(module,"get_receipt",receipt)
            monkeypatch.setattr(module,"add_receipt",add_receipt)
        async def monitor_receipt(db,actor,equipment,sample_id):
            return await receipt(db,actor,equipment,"process_curve",sample_id)
        async def monitor_add_receipt(db,**values):
            return await add_receipt(db,stream="process_curve",**values)
        monkeypatch.setattr(mr,"get_receipt",monitor_receipt)
        monkeypatch.setattr(mr,"add_receipt",monitor_add_receipt)
        for stream,access in (("drive",ed),("production_parameters",ep)):
            async def get(db,sample,stream=stream):
                return next((r for (s,_),r in db.rows.items() if s==stream and r.equipment_id==sample.equipment_id and r.timestamp==sample.sampled_at and (stream=="drive" or r.coil_no==sample.coil_no)),None)
            async def add(db,stream=stream,**values):
                row=db.add_row(stream,values)
                await db.flush()
                return row
            monkeypatch.setattr(access,"get_business_record",get)
            monkeypatch.setattr(access,"add_record",add)
        async def state(db,equipment):
            if equipment not in db.states:
                db.states[equipment]=SimpleNamespace(equipment_id=equipment,last_sampled_at=None,fingerprint=None,performance_id=None,result=None)
            return db.states[equipment]
        async def applied(db,equipment,at):
            return next((r for r in db.receipts.values() if r.stream=="production_observation" and r.equipment_id==equipment and r.sampled_at==at and r.outcome!="stale"),None)
        async def by_coil(db,equipment,coil):
            return next((r for (s,_),r in db.rows.items() if s=="production" and r.equipment_id==equipment and r.coil_no==coil),None)
        async def by_id(db,equipment,record_id,lock=False):
            r=db.rows.get(("production",record_id))
            return r if r is not None and r.equipment_id==equipment else None
        async def active(db,equipment):
            return [r for (s,_),r in db.rows.items() if s=="production" and r.equipment_id==equipment and r.observation_status in ("in_production","unknown")]
        async def add_production(db,**values):
            defaults=dict(start_time=None,end_time=None,reported_start_time=None,reported_end_time=None,collected_weight=None,
                manual_override_weight=None,effective_weight=None,effective_weight_source=None,observation_status=None,
                weight=None,total_length=None,diameter=None,density=None,grade=None,spec=None,remark=None)
            defaults.update(values)
            return db.add_row("production",defaults)
        for name,fn in (("state_for_update",state),("by_coil",by_coil),("by_id",by_id),("active_records",active),("add_record",add_production)):
            monkeypatch.setattr(po,name,fn)
        monkeypatch.setattr(pr,"get_applied_event",applied)
        async def exists(db,record_id):return ("production",record_id) in db.rows
        monkeypatch.setattr(po,"parent_id_exists",exists)
        async def child(db,kind,parent,sample):
            return next((r for (s,_),r in db.rows.items() if s==kind and r.equipment_id==sample.equipment_id and r.performance_id==parent and r.zone==sample.zone and r.record_time==sample.record_time),None)
        async def add_child(db,kind,**values):return db.add_row(kind,values)
        monkeypatch.setattr(pc,"get_record",child);monkeypatch.setattr(pc,"add_record",add_child)
        async def get_curve(db,equipment,at):
            return next((r for (s,_),r in db.rows.items() if s=="curve" and r.equipment_id==equipment and r.sampled_at==at),None)
        async def add_curve(db,**values):return db.add_row("curve",values)
        monkeypatch.setattr(mc,"get_sample",get_curve);monkeypatch.setattr(mc,"add_sample",add_curve)

@pytest.fixture
def store(monkeypatch):
    db=MemoryTransactions();db.install(monkeypatch);return db

@pytest.mark.asyncio
async def test_partial_merge_duplicate_atomic_conflict_and_presence(store):
    first=await equipment.receive_sample(store,DriveSampleIn.model_validate(identity(tv=0)),1)
    row=store.rows[("drive",first["record_id"])];assert row.tv==0 and row.km is None
    duplicate=await equipment.receive_sample(store,DriveSampleIn.model_validate(identity(tv=0)),1)
    assert duplicate["outcome"]=="duplicate" and len(store.rows)==1
    supplied=identity(km=1.25);supplied["sampleId"]="fill"
    assert (await equipment.receive_sample(store,DriveSampleIn.model_validate(supplied),2))["outcome"]=="updated"
    bad=identity(km=9,oxygen=2);bad["sampleId"]="conflict"
    with pytest.raises(BusinessException) as error:await equipment.receive_sample(store,DriveSampleIn.model_validate(bad),1)
    assert error.value.error_code.value.endswith("mapping_value_conflict")
    assert store.rows[("drive",first["record_id"])].oxygen is None and len(store.receipts)==2
    changed=identity(tv=0,km=1.25)
    with pytest.raises(BusinessException) as error:await equipment.receive_sample(store,DriveSampleIn.model_validate(changed),1)
    assert error.value.error_code.value.endswith("mapping_sample_id_conflict")

@pytest.mark.asyncio
@pytest.mark.parametrize("failure",["flush","refresh","receipt","commit"])
async def test_partial_failure_no_success_receipt(store,failure):
    store.fail=failure
    with pytest.raises(BusinessException) as error:await equipment.receive_sample(store,DriveSampleIn.model_validate(identity(tv=1)),1)
    assert error.value.code==(503 if failure=="commit" else 500)
    assert not store.rows and not store.receipts and store.rollbacks==1

@pytest.mark.asyncio
async def test_production_lifecycle_watermark_stale_reactivation_and_manual_zero(store):
    def observation(at,status="in_production",coil="A",**values):
        p=identity(**values);p.update(sampleId=at,sampledAt=f"2026-10-16T{at}:00.123Z",observationStatus=status)
        if status=="in_production":p["coilNo"]=coil
        return ProductionObservationIn.model_validate(p)
    first=await production.receive_observation(store,observation("10:00",weight=2),1)
    record=store.rows[("production",first["record_id"])];assert record.weight==2
    record.manual_override_weight=0;record.weight=0;record.effective_weight=0;record.effective_weight_source="manual_override_weight"
    await store.commit()  # Model a completed manual transaction before the next observation.
    await production.receive_observation(store,observation("10:01",weight=4),1)
    record=store.rows[("production",first["record_id"])]
    assert record.weight==0 and record.collected_weight==4 and record.effective_weight_source=="manual_override_weight"
    second=await production.receive_observation(store,observation("10:02",coil="B"),1)
    record=store.rows[("production",first["record_id"])]
    assert record.observation_status=="not_in_production" and second["record_id"]!=first["record_id"]
    stale=await production.receive_observation(store,observation("09:59",coil="C"),1)
    assert stale["outcome"]=="stale" and len(store.rows)==2
    await production.receive_observation(store,observation("10:03","not_in_production"),1)
    assert all(r.observation_status=="not_in_production" for r in store.rows.values())
    reactivated=await production.receive_observation(store,observation("10:04",coil="A"),1)
    record=store.rows[("production",first["record_id"])]
    assert reactivated["record_id"]==first["record_id"] and record.observation_status=="in_production"
    changed=observation("10:04",coil="B");changed.sample_id="different"
    with pytest.raises(BusinessException) as error:await production.receive_observation(store,changed,2)
    assert error.value.error_code.value.endswith("mapping_observation_time_conflict")

@pytest.mark.asyncio
async def test_empty_inactive_watermark_prevents_old_start_and_process_parent_retry(store):
    p=identity(observationStatus="unknown")
    await production.receive_observation(store,ProductionObservationIn.model_validate(p),1)
    assert not store.rows and store.states["line-A"].last_sampled_at
    p.update(sampleId="old",sampledAt="2026-10-16T09:00:00Z",observationStatus="in_production",coilNo="0")
    assert (await production.receive_observation(store,ProductionObservationIn.model_validate(p),1))["outcome"]=="stale"
    child=dict(equipmentId="line-A",sampleId="child",quality="good",recordTime="2026-10-16T10:00:00Z",coilNo="0",zone="Z",setTemp=0)
    with pytest.raises(BusinessException) as error:await process.receive_sample(store,ProcessTemperatureIn.model_validate(child),1,1,"temperature")
    assert error.value.code==404 and len(store.receipts)==2
    p.update(sampleId="new",sampledAt="2026-10-16T11:00:00Z")
    parent=await production.receive_observation(store,ProductionObservationIn.model_validate(p),1)
    result=await process.receive_sample(store,ProcessTemperatureIn.model_validate(child),1,parent["record_id"],"temperature")
    assert result["record_id"] and store.rows[("temperature",result["record_id"])].duration is None

@pytest.mark.asyncio
async def test_curve_immutable_time_and_presence(store):
    p=identity(z1TempSet=0,lineSpeedAct=1.25)
    result=await monitor.receive_sample(store,ProcessCurveIn.model_validate(p),1)
    p["sampleId"]="another"
    assert (await monitor.receive_sample(store,ProcessCurveIn.model_validate(p),2))["record_id"]==result["record_id"]
    p["dewPoint"]=0
    with pytest.raises(BusinessException) as error:await monitor.receive_sample(store,ProcessCurveIn.model_validate(p),3)
    assert error.value.error_code.value.endswith("mapping_sample_time_conflict") and len(store.rows)==1

@pytest.mark.parametrize('owner',[equipment,production,monitor])
@pytest.mark.parametrize('message',["Duplicate entry 'x' for key 'unrelated_unique'","Duplicate entry 'uq_equipment_mapping_delivery' for key 'other'"])
def test_only_named_unique_errors_are_races(owner,message):
    from sqlalchemy.exc import IntegrityError
    error=IntegrityError('private SQL',{},Exception(1062,message))
    assert not owner.unique_race(error)

@pytest.mark.parametrize('manual,reported,observed,expected,seconds',[
    ((0,2),(0,3),(0,4),'manual_time',2),
    ((None,None),(0,3),(0,4),'reported_time',3),
    ((None,None),(None,None),(0,4),'external_observed',4),
    ((None,None),(None,None),(None,None),'unavailable',None)])
def test_duration_priority(manual,reported,observed,expected,seconds):
    def at(second):return datetime(2026,10,16,10,0,second) if second is not None else None
    row=SimpleNamespace(start_time=at(manual[0]),end_time=at(manual[1]),reported_start_time=at(reported[0]),reported_end_time=at(reported[1]),first_observed_at=at(observed[0]),last_observed_at=at(observed[1]))
    production.apply_duration(row)
    assert row.total_duration_source==expected and row.total_duration_seconds==seconds


class CurrentReadResult:
    def __init__(self,value):self.value=value
    def scalar_one_or_none(self):return self.value

class ObservationReadView:
    """Actual SQL with synthetic RR view; state wait publishes t1 then later t2, no DB."""
    def __init__(self,digest,first_state_race=False):
        from app.performance.models.mapping_ingest import PerformanceObservationState,PerformanceMappingReceipt
        from app.performance.mapping_domain import source_time
        self.view=None;self.waited=False;self.events=[];self.added=[];self.commits=0;self.rollbacks=0
        self.first_state_race=first_state_race;self.state_insert_pending=False
        self.state=PerformanceObservationState(id=1,equipment_id='line-A',last_sampled_at=source_time('2026-10-16T11:00:00Z'),
            fingerprint='t2',performance_id=None,observation_status='not_in_production',result={'record_id':None,'affected_record_ids':[],
            'sampled_at':'2026-10-16T11:00:00.000Z','outcome':'updated'})
        self.old_event=PerformanceMappingReceipt(id=1,actor_user_id=1,equipment_id='line-A',stream='production_observation',
            sample_id='original',sampled_at=source_time('2026-10-16T10:00:00Z'),fingerprint=digest,outcome='created',performance_id=7,
            result={'record_id':7,'affected_record_ids':[7],'sampled_at':'2026-10-16T10:00:00.000Z','outcome':'created'})
    async def execute(self,query):
        from sqlalchemy.dialects import mysql
        text=str(query.compile(dialect=mysql.dialect(),compile_kwargs={'literal_binds':True}))
        table=query.get_final_froms()[0].name
        if table=='performance_mapping_observation_state':
            assert query._for_update_arg is not None
            self.events.append(('state_lock',text))
            if self.first_state_race:return CurrentReadResult(None)
            self.waited=True
            return CurrentReadResult(self.state)
        assert table=='performance_mapping_receipts' and query._for_update_arg is None
        if self.view is None:self.view=[self.old_event] if self.waited else []
        if 'outcome !=' in text:
            self.events.append(('history_consistent_read',text))
            return CurrentReadResult(self.view[0] if self.view else None)
        self.events.append(('delivery_consistent_read',text))
        return CurrentReadResult(None) # New actor/sample identity has no committed receipt.
    def add(self,row):
        from app.performance.models.mapping_ingest import PerformanceObservationState
        self.added.append(row)
        if isinstance(row,PerformanceObservationState):self.state_insert_pending=True
    async def flush(self):
        if self.state_insert_pending:
            from sqlalchemy.exc import IntegrityError
            self.state_insert_pending=False;self.first_state_race=False
            raise IntegrityError('synthetic',{},Exception(1062,"Duplicate entry 'line-A' for key 'uq_performance_observation_equipment'"))
    async def rollback(self):
        self.rollbacks+=1;self.view=None;self.added=[];self.events.append(('rollback',None))
    async def commit(self):self.commits+=1;self.events.append(('commit',None))

@pytest.mark.asyncio
@pytest.mark.parametrize('changed',[False,True])
@pytest.mark.parametrize('first_state_race',[False,True])
async def test_locked_watermark_history_starts_a_new_rr_view(changed,first_state_race):
    original=ProductionObservationIn.model_validate(identity(sampleId='original',sampledAt='2026-10-16T10:00:00Z',observationStatus='in_production',coilNo='A',weight=1))
    digest=production.fingerprint(original,'production_observation')
    sample=ProductionObservationIn.model_validate(identity(sampleId='replay',sampledAt='2026-10-16T10:00:00Z',observationStatus='in_production',coilNo='A',weight=2 if changed else 1))
    db=ObservationReadView(digest,first_state_race)
    if changed:
        with pytest.raises(BusinessException) as error:await production.receive_observation(db,sample,2)
        assert error.value.error_code.value=='performance.mapping_observation_time_conflict'
        assert db.commits==0 and not db.added
    else:
        result=await production.receive_observation(db,sample,2)
        assert result['outcome']=='duplicate' and result['record_id']==7 and db.commits==1
        assert len(db.added)==1 and db.added[0].outcome=='duplicate'
    events=[name for name,_ in db.events]
    index=events.index('history_consistent_read')
    assert events[index-1]=='state_lock' and events[index-2]=='rollback'
    assert db.state.last_sampled_at.hour==11 and db.state.performance_id is None

class DeliveryLockSchedule:
    """Actual equipment SQL: another request commits delivery while business lock waits."""
    def __init__(self,stream,sample):
        self.stream=stream;self.sample=sample;self.waited=False;self.view=None;self.sql=[];self.rollbacks=0;self.commits=0
    async def execute(self,query):
        from sqlalchemy.dialects import mysql
        from app.equipment.models.equipment import EquipmentDrive,EquipmentProductionParameters
        from app.equipment.models.mapping_ingest import EquipmentMappingReceipt
        text=str(query.compile(dialect=mysql.dialect(),compile_kwargs={'literal_binds':True}));self.sql.append(text)
        table=query.get_final_froms()[0].name
        if table=='equipment_mapping_receipts':
            assert query._for_update_arg is None
            if self.view is None:self.view=self.waited
            if not self.view:return CurrentReadResult(None)
            return CurrentReadResult(EquipmentMappingReceipt(actor_user_id=1,equipment_id='line-A',stream=self.stream,
                sample_id=self.sample.sample_id,fingerprint='other-committed-content',sampled_at=self.sample.sampled_at,
                result={'record_id':7},outcome='created'))
        assert query._for_update_arg is not None
        self.waited=True
        if self.stream=='drive':return CurrentReadResult(EquipmentDrive(id=7,equipment_id='line-A',timestamp=self.sample.sampled_at,tv=1))
        return CurrentReadResult(EquipmentProductionParameters(id=7,equipment_id='line-A',timestamp=self.sample.sampled_at,
            coil_no='A',http_coil_key=b'A',width=1))
    async def rollback(self):self.rollbacks+=1;self.view=None
    async def commit(self):self.commits+=1;raise AssertionError('conflicting delivery must not commit')

@pytest.mark.asyncio
@pytest.mark.parametrize('stream',['drive','production_parameters'])
async def test_business_lock_wait_preserves_delivery_conflict_priority(stream):
    from app.equipment.schemas.production_parameter_sample_in import ProductionParameterSampleIn
    from app.equipment.services import async_production_parameter_sample as parameter_service
    sample=(DriveSampleIn.model_validate(identity(tv=2)) if stream=='drive' else ProductionParameterSampleIn.model_validate(identity(coilNo='A',width=2)))
    db=DeliveryLockSchedule(stream,sample)
    service=equipment if stream=='drive' else parameter_service
    with pytest.raises(BusinessException) as error:await service.receive_sample(db,sample,1)
    assert error.value.error_code.value=='equipment.mapping_sample_id_conflict'
    assert db.commits==0 and db.rollbacks==2 and len(db.sql)==3
    assert 'FOR UPDATE' in db.sql[1] and 'FOR UPDATE' not in db.sql[2]

@pytest.mark.asyncio
@pytest.mark.parametrize('stream',['production_observation','process_temperature','process_tension','process_speed'])
async def test_every_performance_stream_rechecks_committed_delivery_on_rejection(monkeypatch,stream):
    from app.performance.crud import async_mapping_ingest as receipts
    from app.performance.mapping_error_codes import MappingError
    calls=0
    sample=ProductionObservationIn.model_validate(identity(observationStatus='unknown')) if stream=='production_observation' else SimpleNamespace(equipment_id='line-A',sample_id='same',record_time=datetime(2026,10,16))
    monkeypatch.setattr(production,'fingerprint',lambda *args,**kwargs:'current-content')
    async def receipt(*args):
        nonlocal calls
        calls+=1
        return None if calls==1 else SimpleNamespace(fingerprint='committed-other',result={})
    monkeypatch.setattr(receipts,'get_receipt',receipt)
    async def apply(*args):raise BusinessException(MappingError.VALUE_CONFLICT,code=409)
    db=MemoryTransactions()
    with pytest.raises(BusinessException) as error:await production.transaction(db,sample,1,stream,apply)
    assert error.value.error_code==MappingError.SAMPLE_ID_CONFLICT and calls==2 and db.commits==0

@pytest.mark.asyncio
async def test_curve_business_rejection_rechecks_delivery_with_a_fresh_view(monkeypatch):
    from app.monitor.crud import async_mapping_ingest as receipts,async_process_curve_sample as curves
    calls=0
    async def receipt(*args):
        nonlocal calls
        calls+=1
        return None if calls==1 else SimpleNamespace(fingerprint='different-delivery',result={})
    monkeypatch.setattr(receipts,'get_receipt',receipt)
    monkeypatch.setattr(curves,'get_sample',AsyncMock(return_value=SimpleNamespace(fingerprint='different-time-content')))
    db=MemoryTransactions()
    with pytest.raises(BusinessException) as error:await monitor.receive_sample(db,ProcessCurveIn.model_validate(identity(lineSpeedAct=1)),1)
    assert error.value.error_code.value=='monitor.mapping_sample_id_conflict' and calls==2 and db.commits==0

@pytest.mark.asyncio
@pytest.mark.parametrize('owner,args',[(equipment,(1,'line-A','drive','same','digest')),(production,(1,'line-A','process_speed','same','digest')),(monitor,(1,'line-A','same','digest'))])
@pytest.mark.parametrize('failure',['read-system','read-dbapi','commit'])
async def test_rejection_delivery_recovery_failures_never_return_success(monkeypatch,owner,args,failure):
    from sqlalchemy.exc import DBAPIError
    calls=0
    async def receipt(*values):
        nonlocal calls
        calls+=1
        if failure=='read-system':raise RuntimeError('private read failure')
        if failure=='read-dbapi':raise DBAPIError('private SQL',{},Exception('private DSN'))
        return SimpleNamespace(fingerprint='digest',result={'record_id':7})
    monkeypatch.setattr(owner.receipts,'get_receipt',receipt)
    db=MemoryTransactions();db.fail='commit' if failure=='commit' else None
    with pytest.raises(BusinessException) as error:await owner.delivery_after_rejection(db,*args)
    assert error.value.code==(500 if failure=='read-system' else 503) and db.commits==0 and db.rollbacks==1 and calls==1

@pytest.mark.asyncio
@pytest.mark.parametrize('owner,args',[(equipment,(1,'line-A','drive','same','digest')),(production,(1,'line-A','process_speed','same','digest')),(monitor,(1,'line-A','same','digest'))])
async def test_rejection_recovery_same_content_returns_stable_original_id(monkeypatch,owner,args):
    monkeypatch.setattr(owner.receipts,'get_receipt',AsyncMock(return_value=SimpleNamespace(fingerprint='digest',result={'record_id':7,'outcome':'created'})))
    db=MemoryTransactions()
    result=await owner.delivery_after_rejection(db,*args)
    assert result=={'record_id':7,'outcome':'duplicate','sample_id':'same'} and db.commits==1 and not db.rows


@pytest.mark.asyncio
async def test_initial_read_view_rollback_failure_is_not_recovered_as_success(monkeypatch):
    calls=0
    async def receipt(*args):
        nonlocal calls
        calls+=1
        return None if calls==1 else SimpleNamespace(fingerprint='same',result={'record_id':7})
    monkeypatch.setattr(production.receipts,'get_receipt',receipt)
    db=MemoryTransactions();rollbacks=0
    async def rollback():
        nonlocal rollbacks
        rollbacks+=1
        if rollbacks==1:raise RuntimeError('private rollback failure')
    monkeypatch.setattr(db,'rollback',rollback)
    with pytest.raises(BusinessException) as error:
        await production.receive_observation(db,ProductionObservationIn.model_validate(identity(observationStatus='unknown')),1)
    assert error.value.code==503 and calls==1 and db.commits==0 and rollbacks==2


@pytest.mark.asyncio
@pytest.mark.parametrize('stream',['drive','production_parameters'])
async def test_locked_newly_committed_business_row_refresh_uses_current_read(stream):
    from app.equipment.schemas.production_parameter_sample_in import ProductionParameterSampleIn
    from app.equipment.services import async_production_parameter_sample as parameter_service
    from sqlalchemy.exc import InvalidRequestError
    sample=DriveSampleIn.model_validate(identity(tv=1)) if stream=='drive' else ProductionParameterSampleIn.model_validate(identity(coilNo='A',width=1))
    class RefreshReadView(DeliveryLockSchedule):
        def __init__(self,*args):super().__init__(*args);self.added=[];self.current_reads=0
        async def flush(self):pass
        def add(self,row):self.added.append(row)
        async def refresh(self,row,*,with_for_update=None):
            if not with_for_update:raise InvalidRequestError('old RR snapshot cannot see newly committed business row')
            self.current_reads+=1
        async def commit(self):self.commits+=1
    db=RefreshReadView(stream,sample)
    result=await (equipment if stream=='drive' else parameter_service).receive_sample(db,sample,1)
    assert result['outcome']=='duplicate' and result['record_id']==7
    assert db.current_reads==1 and db.commits==1 and len(db.added)==1
