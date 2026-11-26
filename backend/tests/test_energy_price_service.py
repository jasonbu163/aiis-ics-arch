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




def install_write_stubs(monkeypatch, row=None, error=None):
    from app.energy.pricing import BUILTIN_ITEMS

    monkeypatch.setattr(crud, "items_for_update", AsyncMock(return_value=dict.fromkeys(BUILTIN_ITEMS)))
    write = AsyncMock(side_effect=error)
    monkeypatch.setattr(crud, "upsert_hour", write)
    monkeypatch.setattr(crud, "saved_legacy_price", AsyncMock(return_value=row or vars(record())))
    return write


@pytest.mark.asyncio
async def test_service_transaction_success_and_actor(monkeypatch):
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    write = install_write_stubs(monkeypatch)
    events = []
    monkeypatch.setattr(service, "log_event", lambda *args, **kwargs: events.append(kwargs))
    now = datetime(2026, 10, 13, 2, 59, tzinfo=timezone.utc)
    result = await service.save_price(db, payload(remark="private"), "actor", now)
    assert isinstance(result, HourlyPriceRecord)
    _, hour, prices, actor, observed, fields = write.call_args.args
    assert hour == datetime(2026, 10, 13, 10)
    assert observed == datetime(2026, 10, 13, 10, 59)
    assert actor == "actor" and fields == {"remark": "private"}
    assert prices["electric"] == {"price": Decimal(0), "remark": None}
    db.commit.assert_awaited_once()
    db.rollback.assert_not_awaited()
    assert events == [dict(actor="actor", record_id=1, result="success")]


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["write", "snapshot", "commit"])
async def test_service_failure_rolls_back_without_partial_write(failure, monkeypatch):
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    row = vars(record())
    if failure == "commit":
        db.commit.side_effect = RuntimeError("failed commit")
    if failure == "snapshot":
        row["electric_price"] = None
    install_write_stubs(monkeypatch, row, RuntimeError("failed write") if failure == "write" else None)
    with pytest.raises((RuntimeError, ValidationError)):
        await service.save_price(db, payload(), "actor", datetime(2026, 10, 13, tzinfo=timezone.utc))
    db.rollback.assert_awaited_once()
    if failure != "commit":
        db.commit.assert_not_awaited()


def test_legacy_projection_selects_inherited_values_without_querying_old_tables():
    sql = str(crud.legacy_projection().compile(dialect=mysql.dialect()))
    assert "energy_price_hours" not in sql
    assert "energy_prices" not in sql
    assert sql.count("energy_price_item_hours.hour_start <= energy_price_hour_meta.hour_start") == 3
    assert "greatest(" in sql and "energy_price_hour_meta.has_builtin" in sql
    assert history_bounds(date.min)[0] == datetime.min
    assert history_bounds(date.max)[1] is None


def test_shanghai_repeated_hour_has_one_canonical_bucket_and_retains_actual_event():
    from datetime import timedelta
    from app.energy.pricing import storage_bounds, storage_hour, storage_time

    first = datetime.fromisoformat("1991-09-15T01:30:00+09:00")
    second = datetime.fromisoformat("1991-09-15T01:30:00+08:00")
    assert storage_hour(first) == storage_hour(second) == datetime(1991, 9, 15, 0)
    assert storage_time(first) == datetime(1991, 9, 15, 0, 30)
    assert storage_time(second) == datetime(1991, 9, 15, 1, 30)
    start, end = storage_bounds(date(1991, 9, 15))
    assert (end - start) == timedelta(hours=25)
    start, end = history_bounds(date(1991, 9, 15))
    buckets = {storage_hour((start + timedelta(hours=hour, minutes=30)).replace(tzinfo=timezone.utc))
               for hour in range(int((end - start).total_seconds() / 3600))}
    assert len(buckets) == 24
    old = HourlyPriceRecord.model_validate(record())
    old.observed_at = datetime(1000, 1, 1)
    assert old.model_dump(mode="json", by_alias=True)["observedAt"] == "1000-01-01T08:00:00+08:00"


@pytest.mark.asyncio
async def test_service_rejects_unpersistable_derived_bucket_before_crud_or_commit(monkeypatch):
    write = install_write_stubs(monkeypatch)
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    with pytest.raises(ValueError, match="unpersistable_observed_at"):
        await service.save_price(db, payload(), "fixture", datetime(1000, 1, 1, tzinfo=timezone.utc))
    write.assert_not_awaited()
    db.commit.assert_not_awaited()
    db.rollback.assert_not_awaited()
