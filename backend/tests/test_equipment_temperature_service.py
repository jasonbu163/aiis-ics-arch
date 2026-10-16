"""新温控Service无DB事务/竞争故障注入和SQL作用域验证。"""
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from sqlalchemy.dialects import mysql
from sqlalchemy.exc import IntegrityError, OperationalError
from app.equipment.schemas.temperature_sample_in import TemperatureSampleIn
from app.equipment.services import async_temperature_sample as service
from app.equipment.temperature_sample_domain import fingerprint, TEMPERATURE_FIELDS
from common.exceptions import BusinessException

pytestmark = pytest.mark.no_db


def payload(**changes):
    result = dict(equipmentId="temperature-pilot-01", sampleId="sample-A", sampledAt="2026-10-16T10:00:00.123Z", quality="good")
    result.update({f"zone{z}{k}": 0 if z == 1 else z + 0.5 for z in range(1, 6) for k in ("Set", "Act")})
    result.update(changes)
    return result


class MemoryTransactions:
    """仅Python对象事务模型，不是SQLite或数据库替代证据。"""
    def __init__(self):
        self.saved_samples, self.saved_receipts = [], []
        self.samples, self.receipts = [], []
        self.commits = self.rollbacks = 0
        self.failure = None

    async def commit(self):
        self.commits += 1
        if self.failure == "commit":
            raise OperationalError("secret SQL", {}, Exception("secret DSN"))
        self.saved_samples, self.saved_receipts = deepcopy(self.samples), deepcopy(self.receipts)
        if self.failure == "unknown_commit":
            raise OperationalError("secret SQL", {}, Exception("secret DSN"))

    async def rollback(self):
        self.rollbacks += 1
        self.samples, self.receipts = deepcopy(self.saved_samples), deepcopy(self.saved_receipts)

    def install(self, monkeypatch):
        async def receipt(db, actor, equipment, sample_id):
            return next((x for x in self.receipts if (x.actor_user_id, x.equipment_id, x.sample_id) == (actor, equipment, sample_id)), None)
        async def sample(db, equipment, time):
            return next((x for x in self.samples if (x.equipment_id, x.sampled_at) == (equipment, time)), None)
        async def add_sample(db, **values):
            if self.failure == "business": raise RuntimeError("secret business SQL")
            result = SimpleNamespace(id=len(self.samples)+1, created_at=datetime(2026,10,16), **values)
            self.samples.append(result)
            if self.failure == "sample_flush": raise RuntimeError("secret flush")
            return result
        async def add_receipt(db, **values):
            if self.failure == "receipt": raise RuntimeError("secret receipt SQL")
            self.receipts.append(SimpleNamespace(**values))
            if self.failure == "receipt_flush": raise RuntimeError("secret flush")
        async def listed(db, equipment, record_id=None, limit=100):
            return sorted([x for x in self.samples if x.equipment_id==equipment and (record_id is None or x.id==record_id)], key=lambda x:(x.sampled_at,x.id), reverse=True)[:limit]
        for name, method in dict(get_receipt=receipt,get_sample=sample,add_sample=add_sample,add_receipt=add_receipt,list_samples=listed).items():
            monkeypatch.setattr(service.crud, name, method)


@pytest.mark.asyncio
async def test_idempotence_actor_timezone_and_business_conflicts(monkeypatch):
    db=MemoryTransactions(); db.install(monkeypatch)
    sample=TemperatureSampleIn.model_validate(payload())
    first=await service.receive_sample(db,sample,1)
    assert first.outcome=="created" and db.commits==1
    for actor, data in [(1,payload()),(1,payload(sampledAt="2026-10-16T18:00:00.123+08:00")),(2,payload()),(1,payload(sampleId="sample-B"))]:
        result=await service.receive_sample(db,TemperatureSampleIn.model_validate(data),actor)
        assert result.outcome=="duplicate" and result.record_id==first.record_id
    assert len(db.samples)==1 and len(db.receipts)==3
    for data, error in [(payload(zone1Set=1),"sample_id_conflict"),(payload(sampleId="sample-C",zone1Set=1),"sample_time_conflict")]:
        with pytest.raises(BusinessException) as caught:
            await service.receive_sample(db,TemperatureSampleIn.model_validate(data),1)
        assert caught.value.code==409 and caught.value.error_code.value.endswith(error)
    assert len(db.samples)==1 and len(db.receipts)==3
    for index, time in enumerate(["2026-10-16T10:00:00.124Z","2026-10-16T09:00:00.123Z"]):
        await service.receive_sample(db,TemperatureSampleIn.model_validate(payload(sampleId=f"new{index}",sampledAt=time)),1)
    read=await service.read_samples(db,"temperature-pilot-01",limit=1)
    assert read.items[0].sampled_at.microsecond==124000
    assert len((await service.read_samples(db,"temperature-pilot-01",first.record_id)).items)==1
    assert not (await service.read_samples(db,"other",first.record_id)).items
    assert len(db.samples)==3


@pytest.mark.asyncio
@pytest.mark.parametrize("failure,code",[("business",500),("receipt",500),("sample_flush",500),("receipt_flush",500),("commit",503)])
async def test_atomic_failures_rollback_all(monkeypatch,failure,code):
    db=MemoryTransactions();db.install(monkeypatch);db.failure=failure
    with pytest.raises(BusinessException) as caught:
        await service.receive_sample(db,TemperatureSampleIn.model_validate(payload()),1)
    assert caught.value.code==code and db.rollbacks==1
    assert not db.saved_samples and not db.saved_receipts and not db.samples and not db.receipts
    assert "secret" not in str(caught.value)


@pytest.mark.asyncio
async def test_unknown_commit_and_lost_response_replay(monkeypatch):
    db=MemoryTransactions();db.install(monkeypatch);db.failure="unknown_commit"
    with pytest.raises(BusinessException) as caught:
        await service.receive_sample(db,TemperatureSampleIn.model_validate(payload()),1)
    assert caught.value.code==503 and db.commits==1
    db.failure=None
    retry=await service.receive_sample(db,TemperatureSampleIn.model_validate(payload()),1)
    assert retry.outcome=="duplicate" and retry.record_id==1 and len(db.samples)==len(db.receipts)==1
    # 上一成功响应被调用方丢弃，重试仍引用已提交recordId。
    retry=await service.receive_sample(db,TemperatureSampleIn.model_validate(payload()),1)
    assert retry.outcome=="duplicate" and len(db.samples)==1


@pytest.mark.asyncio
@pytest.mark.parametrize("errno,key,expected_calls,code",[(1062,"uq_temperature_sample_business",3,503),(1062,"uq_temperature_sample_delivery",3,503),(1062,"unrelated",1,500),(1452,"fk",1,500)])
async def test_race_is_bounded_and_other_integrity_is_not_duplicate(monkeypatch,errno,key,expected_calls,code):
    db=MemoryTransactions();db.install(monkeypatch)
    failure=IntegrityError("private SQL",{},Exception(errno,f"Duplicate entry 'synthetic' for key '{key}'"))
    method=AsyncMock(side_effect=failure);monkeypatch.setattr(service.crud,"add_sample",method)
    with pytest.raises(BusinessException) as caught:
        await service.receive_sample(db,TemperatureSampleIn.model_validate(payload()),1)
    assert caught.value.code==code and method.await_count==db.rollbacks==expected_calls
    assert not db.saved_receipts


@pytest.mark.asyncio
async def test_committed_race_winner_reloaded_after_rollback(monkeypatch):
    db=MemoryTransactions();db.install(monkeypatch)
    sample=TemperatureSampleIn.model_validate(payload())
    first=await service.receive_sample(db,sample,1)
    calls=0;real=service.crud.get_receipt
    async def racing(*args):
        nonlocal calls
        calls+=1
        if calls==1: raise IntegrityError("private",{},Exception(1062,"Duplicate entry 'synthetic' for key 'equipment_temperature_sample_receipts.uq_temperature_sample_delivery'"))
        return await real(*args)
    monkeypatch.setattr(service.crud,"get_receipt",racing)
    retry=await service.receive_sample(db,sample,1)
    assert retry.record_id==first.record_id and retry.outcome=="duplicate" and db.rollbacks==1


@pytest.mark.asyncio
async def test_crud_pushes_scope_id_limit_and_source_order_to_sql():
    from app.equipment.crud import async_temperature_sample as crud
    statements=[]
    class Result:
        def scalars(self): return self
        def all(self): return []
    async def execute(stmt): statements.append(stmt);return Result()
    db=SimpleNamespace(execute=execute)
    await crud.list_samples(db,"temperature-pilot-01",7,1)
    compiled=statements[0].compile(dialect=mysql.dialect())
    sql=str(compiled)
    assert "equipment_id =" in sql and ".id =" in sql and "sampled_at DESC" in sql and "id DESC" in sql and "LIMIT" in sql
    assert set(compiled.params.values())=={"temperature-pilot-01",7,1}
    assert "receipt" not in sql


def test_fingerprint_numeric_equivalence_and_no_identity_leak():
    a=TemperatureSampleIn.model_validate(payload())
    b=TemperatureSampleIn.model_validate(payload(zone1Set=-0.0,zone2Set=Decimal("2.5000"),sampleId="other",sampledAt="2026-10-16T18:00:00.123000+08:00"))
    assert fingerprint(a)==fingerprint(b)


def test_unique_error_uses_actual_constraint_key_not_duplicate_value():
    error=IntegrityError("private",{},Exception(1062,"Duplicate entry 'uq_temperature_sample_delivery' for key 'another_key'"))
    assert not service._unique_race(error)
    for key in ("uq_temperature_sample_delivery","uq_temperature_sample_business"):
        error=IntegrityError("private",{},Exception(1062,f"Duplicate entry 'value' for key 'schema.{key}'"))
        assert service._unique_race(error)


@pytest.mark.asyncio
async def test_post_commit_log_failure_recovers_same_record_on_retry(monkeypatch):
    db=MemoryTransactions();db.install(monkeypatch)
    original=service.log_event
    def failed_log(*args,**kwargs):raise RuntimeError("private log sink")
    monkeypatch.setattr(service,"log_event",failed_log)
    sample=TemperatureSampleIn.model_validate(payload())
    with pytest.raises(RuntimeError):await service.receive_sample(db,sample,1)
    assert len(db.saved_samples)==len(db.saved_receipts)==1
    monkeypatch.setattr(service,"log_event",original)
    replay=await service.receive_sample(db,sample,1)
    assert replay.record_id==1 and replay.outcome=="duplicate" and len(db.samples)==1
