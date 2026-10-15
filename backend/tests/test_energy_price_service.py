"""能源价格规则、假事务与真实 SQL 编译的隔离测试。"""
from datetime import datetime, timezone, date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError
from sqlalchemy.dialects import mysql
from app.energy.schemas.energy_price import PriceCreate, PriceRecord, HourlyPriceRecord, history_bounds
from app.energy.services import async_energy_price as service
from app.energy.crud import async_energy_price as crud

pytestmark = pytest.mark.no_db


def payload(**values):
    return PriceCreate(electricPrice=values.pop("electricPrice", 0), hydrogenPrice="1.23000", argonPrice="999999.9999", **values)


def record(**values):
    return SimpleNamespace(id=1, electric_price=Decimal("0"), hydrogen_price=Decimal("1.2300"), argon_price=Decimal("999999.9999"), electric_remark=None, hydrogen_remark=None, argon_remark=None, remark=values.get("remark"), operator="actor", observed_at=datetime(2026,10,13),hour_start=datetime(2026,10,13),created_at=datetime(2026, 10, 13), updated_at=datetime(2026, 10, 13))


@pytest.mark.parametrize("value", [0, "0.000000", "1.2345", "999999.9999", "1.2345000000000000000000000000000000", "1e-4"])
def test_valid_precise_prices(value):
    result = payload(electricPrice=value)
    assert result.electric_price == Decimal(str(value))
    assert isinstance(result.electric_price, Decimal)


@pytest.mark.parametrize("value", [True, False, None, "", " ", "abc", "NaN", "Infinity", float("inf"), float("nan"), -1, "999999.99991", "1000000", "0.00001", "1.2345000000000000000000000000000001", "1_000", [], {}])
def test_invalid_prices(value):
    with pytest.raises(ValidationError):
        payload(electricPrice=value)


@pytest.mark.parametrize("field,limit", [("electricRemark",500),("hydrogenRemark",500),("argonRemark",500),("remark",2000)])
def test_remark_snapshot_and_limits(field, limit):
    assert payload(**{field:""}).model_dump()[{"electricRemark":"electric_remark","hydrogenRemark":"hydrogen_remark","argonRemark":"argon_remark"}.get(field,field)] is None
    payload(**{field:"文"*limit})
    with pytest.raises(ValidationError):
        payload(**{field:"文"*(limit+1)})
    with pytest.raises(ValidationError):
        payload(**{field:12})


@pytest.mark.parametrize("extra", ["id", "operator", "createdAt", "updatedAt", "remarks"])
def test_server_metadata_cannot_be_forged(extra):
    with pytest.raises(ValidationError):
        payload(**{extra:"forged"})


def test_required_prices_and_local_number_serialization():
    with pytest.raises(ValidationError):
        PriceCreate(electricPrice=0)
    data = PriceRecord.model_validate(record()).model_dump(mode="json", by_alias=True)
    assert data["electricPrice"] == 0
    assert all(isinstance(data[key], (float,int)) for key in ("electricPrice","hydrogenPrice","argonPrice"))
    assert payload(remark="  preserved 文 ").remark == "  preserved 文 "




@pytest.mark.asyncio
async def test_service_transaction_success_and_actor(monkeypatch):
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    upsert = AsyncMock(return_value=record())
    events = []
    monkeypatch.setattr(crud, 'upsert_price', upsert)
    monkeypatch.setattr(service, 'log_event', lambda *args, **kwargs: events.append(kwargs))
    now = datetime(2026,10,13,2,59,tzinfo=timezone.utc)
    result = await service.save_price(db,payload(remark='private'),'actor',now)
    assert isinstance(result,HourlyPriceRecord)
    assert upsert.call_args.args[1]['observed_at'] == datetime(2026,10,13,2,59)
    assert upsert.call_args.args[1]['hour_start'] == datetime(2026,10,13,2)
    assert upsert.call_args.args[2] == 'actor'
    db.commit.assert_awaited_once(); db.rollback.assert_not_awaited()
    assert events == [dict(actor='actor',record_id=1,result='success')]
    assert 'private' not in str(events)


@pytest.mark.asyncio
@pytest.mark.parametrize('failure',['write','snapshot','commit'])
async def test_service_failure_rolls_back_without_partial_write(failure,monkeypatch):
    db = SimpleNamespace(commit=AsyncMock(),rollback=AsyncMock())
    if failure == 'commit': db.commit.side_effect = RuntimeError('failed')
    upsert = AsyncMock(side_effect=RuntimeError('failed')) if failure == 'write' else AsyncMock(return_value=record())
    if failure == 'snapshot': upsert.return_value.electric_price = None
    monkeypatch.setattr(crud,'upsert_price',upsert)
    with pytest.raises((RuntimeError,ValidationError)):
        await service.save_price(db,payload(),'actor',datetime(2026,10,13,tzinfo=timezone.utc))
    db.rollback.assert_awaited_once()
    if failure != 'commit': db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_real_crud_sql_unique_atomic_complete_group_and_queries():
    from sqlalchemy import UniqueConstraint
    from app.energy.models.energy_price_hour import EnergyPriceHour
    table=EnergyPriceHour.__table__
    assert any(isinstance(c,UniqueConstraint) and c.name=='uq_energy_price_hours_hour_start' and [v.name for v in c.columns]==['hour_start'] for c in table.constraints)
    values=payload().model_dump(exclude={'observed_at'}) | dict(observed_at=datetime(2026,10,13,2,59),hour_start=datetime(2026,10,13,2))
    sql=str(crud.upsert_statement(values,'actor').compile(dialect=mysql.dialect()))
    assert 'ON DUPLICATE KEY UPDATE' in sql and 'utc_timestamp' in sql.lower()
    update=sql.split('ON DUPLICATE KEY UPDATE')[1]
    for key in (*values.keys(),'operator'):
        assert (f'{key} = VALUES({key})' in update) == (key != 'hour_start')
    for key in ('id','created_at','hour_start'): assert f'{key} =' not in update
    statements=[]
    class Result:
        def scalar_one(self): return 9
        def scalar_one_or_none(self): return None
        def scalars(self): return self
        def all(self): return []
    class Session:
        async def execute(self,statement): statements.append(statement.compile(dialect=mysql.dialect()));return Result()
    db=Session(); now=datetime(2026,10,13,4)
    assert await crud.current_price(db,now) is None
    assert await crud.price_history(db,3,4,history_bounds(date(2026,10,13))) == ([],9)
    assert 'observed_at <=' in str(statements[0]) and now in statements[0].params.values()
    assert 'ORDER BY energy_price_hours.observed_at DESC, energy_price_hours.id DESC' in str(statements[0])
    assert 'observed_at >=' in str(statements[1]) and 'observed_at <' in str(statements[1])
    assert statements[2].params['param_1']==8 and statements[2].params['param_2']==4
    assert history_bounds(date.min)[0] == datetime.min
    assert history_bounds(date.max)[1] is None


@pytest.mark.asyncio
async def test_hourly_group_semantics_in_memory_not_mysql_concurrency_proof(monkeypatch):
    from copy import deepcopy
    rows={}; sequence=0
    async def upsert(db,values,actor):
        nonlocal sequence
        key=values['hour_start']; previous=rows.get(key)
        if previous is None: sequence+=1
        row=SimpleNamespace(**values,operator=actor,id=previous.id if previous else sequence,created_at=previous.created_at if previous else datetime(2026,10,13),updated_at=datetime(2026,10,14))
        rows[key]=row
        return row
    async def current(db,now):
        valid=[row for row in rows.values() if row.observed_at<=now]
        return max(valid,key=lambda r:(r.observed_at,r.id)) if valid else None
    async def history(db,page,size,bounds):
        valid=sorted((row for row in rows.values() if bounds is None or (bounds[0]<=row.observed_at and (bounds[1] is None or row.observed_at<bounds[1]))),key=lambda r:(r.observed_at,r.id),reverse=True)
        return valid[(page-1)*size:page*size],len(valid)
    monkeypatch.setattr(crud,'upsert_price',upsert);monkeypatch.setattr(crud,'current_price',current);monkeypatch.setattr(crud,'price_history',history)
    db=SimpleNamespace(commit=AsyncMock(),rollback=AsyncMock())
    async def save(time,**kwargs):
        return await service.save_price(db,payload(**kwargs),'actor',datetime.fromisoformat(time))
    assert await service.current_price(db,datetime(2026,10,13,tzinfo=timezone.utc)) is None
    first=await save('2026-10-13T10:00:00+08:00',remark='first')
    second=await save('2026-10-13T02:59:00+00:00',electricPrice=2,remark='second')
    assert first.id==second.id and first.created_at==second.created_at
    assert second.electric_price==2 and second.remark=='second' and len(rows)==1
    latest=await save('2026-10-13T11:00:00+08:00',electricPrice=3)
    await save('2026-10-12T10:00:00+08:00',electricPrice=4)
    assert (await service.current_price(db,datetime(2026,10,13,4,tzinfo=timezone.utc))).id==latest.id
    assert (await service.current_price(db,datetime(2026,10,20,tzinfo=timezone.utc))).id==latest.id
    day=await service.price_history(db,1,24,date(2026,10,13));assert day.total==2
    assert [row.id for row in day.items]==[latest.id,first.id]
    assert (await service.price_history(db,99,24,date(2026,10,13))).total==2
    assert (await service.price_history(db,1,24,date(2026,10,15))).items==[]
    await save('2026-10-13T23:59:59+08:00'); await save('2026-10-14T00:00:00+08:00')
    assert len(rows)==5
    # An imported future row is not eligible for current until its event time.
    future=await save('2026-10-20T10:00:00+08:00')
    assert (await service.current_price(db,datetime(2026,10,15,tzinfo=timezone.utc))).id!=future.id


@pytest.mark.asyncio
async def test_shanghai_repeated_hour_has_one_canonical_utc_bucket_retains_actual_event(monkeypatch):
    from datetime import timedelta
    from zoneinfo import ZoneInfo
    calls=[]
    async def upsert(db,values,actor):
        calls.append(values)
        return SimpleNamespace(**values,id=1,operator=actor,created_at=datetime(1991,9,14,16),updated_at=datetime(2026,10,13))
    monkeypatch.setattr(crud,'upsert_price',upsert)
    db=SimpleNamespace(commit=AsyncMock(),rollback=AsyncMock())
    first=await service.save_price(db,payload(),'actor',datetime.fromisoformat('1991-09-15T01:30:00+09:00'))
    second=await service.save_price(db,payload(electricPrice=2),'actor',datetime.fromisoformat('1991-09-15T01:30:00+08:00'))
    assert first.id==second.id and first.created_at==second.created_at
    assert calls[0]['hour_start']==calls[1]['hour_start']==datetime(1991,9,14,16)
    assert calls[0]['observed_at']==datetime(1991,9,14,16,30)
    assert calls[1]['observed_at']==datetime(1991,9,14,17,30)
    assert second.electric_price==2
    # Enumerate all real hours of this 25-hour natural day: only 24 civil keys exist.
    start,end=history_bounds(date(1991,9,15));buckets=set()
    for hour in range(int((end-start).total_seconds()/3600)):
        instant=(start+timedelta(hours=hour,minutes=30)).replace(tzinfo=timezone.utc)
        await service.save_price(db,payload(),'actor',instant)
        buckets.add(calls[-1]['hour_start'])
    assert len(buckets)==24
    old=HourlyPriceRecord.model_validate(record())
    old.observed_at=datetime(1000,1,1)
    assert old.model_dump(mode='json',by_alias=True)['observedAt']=='1000-01-01T08:00:00+08:00'


@pytest.mark.asyncio
async def test_service_rejects_unpersistable_derived_bucket_before_crud_or_commit(monkeypatch):
    write = AsyncMock()
    monkeypatch.setattr(crud, 'upsert_price', write)
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    with pytest.raises(ValueError, match='unpersistable_observed_at'):
        await service.save_price(db,payload(),'fixture',datetime(1000,1,1,tzinfo=timezone.utc))
    write.assert_not_awaited(); db.commit.assert_not_awaited(); db.rollback.assert_not_awaited()
