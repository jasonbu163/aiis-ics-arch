"""在显式确认的 MySQL 夹具验证动态单价、旧投影、迁移和竞争。"""
import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from app.energy.api import energy_price
from app.energy.models import EnergyPrice, EnergyPriceHour, EnergyPriceHourMeta, EnergyPriceItem, EnergyPriceItemHour
from app.energy.schemas.energy_price import HourlyPriceRecord
from app.equipment_observation.api import routes
from app.user.models.user import User
from core.registrar import create_app
from database import get_db
from tests.test_energy_public_reads import HISTORY as PUBLIC_SAMPLES
from tests_mysql.test_energy_curve_groups_mysql import seed_curve_metrics, seed_curve_samples
from tests_mysql.test_energy_registered_ingest_mysql import (  # noqa: F401
    SUCCESSOR, fixture_profile, jwt_header, query, snapshot, target,
)

PREDECESSOR = "af6d8b2c4e90"
REVISION = "7cb6e40f3d19"
PRICING = "/energy/pricing"
LATEST = "/equipment/latest-cards"
PROCESS = "/monitor/history-curves"
SAMPLES = "/energy/consumption/samples"
PRICE_TABLES = (EnergyPriceItem.__table__, EnergyPriceHourMeta.__table__, EnergyPriceItemHour.__table__)
FIXED_NOW = datetime(2026, 11, 25, 5, tzinfo=timezone.utc)


def run_migration(migrate, destination, operation="upgrade"):
    code, log = migrate(destination, operation)
    assert code == 0, log


def seed_legacy_prices(engine, full):
    EnergyPrice.__table__.create(engine)
    EnergyPriceHour.__table__.create(engine)
    with Session(engine) as db, db.begin():
        db.add(EnergyPrice(id=9, electric_price=4, hydrogen_price=5, argon_price=6, operator="append-archive"))
        for username, role in (("test_admin", "admin"), ("test_read", "operator"), ("test_manage", "supervisor")):
            db.add(User(username=username, password="unused-isolated-hash", name=username, role=role, is_active=True))
        if full:
            for id_, hour, observed in (
                (22, datetime(1991, 9, 14, 16), datetime(1991, 9, 14, 17, 30)),
                (72, datetime(2026, 11, 23, 15), datetime(2026, 11, 23, 15, 59, 59, 123456)),
                (85, datetime(2026, 11, 23, 16), datetime(2026, 11, 23, 16, 0, 0, 654321)),
            ):
                db.add(
                    EnergyPriceHour(
                        id=id_, hour_start=hour, observed_at=observed, created_at=observed,
                        updated_at=observed, operator="archive-fixture",
                        electric_price=Decimal("0.8000"), hydrogen_price=Decimal("3.0123"),
                        argon_price=Decimal("999999.9999"), electric_remark="原始 电价 ", hydrogen_remark="",
                        argon_remark=None, remark=" 原始总备注 ",
                    ),
                )
    with Session(engine) as db:
        return [
            HourlyPriceRecord.model_validate(row).model_dump(mode="json", by_alias=True)
            for row in db.scalars(select(EnergyPriceHour).order_by(EnergyPriceHour.observed_at.desc()))
        ]


@pytest.mark.asyncio
@pytest.mark.parametrize("target", [REVISION], indirect=True)
async def test_staged_hour_meta_requires_auto_increment_and_no_extra_uniqueness(target, monkeypatch):
    engine, async_url, migrate, _ = target
    monkeypatch.setattr(energy_price, "utc_now", lambda: FIXED_NOW)
    run_migration(migrate, PREDECESSOR)
    legacy = seed_legacy_prices(engine, full=True)
    raw_before = {
        name: query(engine, f"SELECT * FROM {name} ORDER BY id")
        for name in ("energy_price_hours", "energy_prices")
    }
    EnergyPriceHourMeta.__table__.create(engine)
    staged_tables = set(inspect(engine).get_table_names())

    def assert_conflict_preserved():
        staged_ddl = query(engine, "SHOW CREATE TABLE energy_price_hour_meta")
        code, log = migrate(REVISION)
        assert code != 0 and "staged table differs from migration layout: energy_price_hour_meta" in log, log
        assert query(engine, "SELECT version_num FROM alembic_version") == [(PREDECESSOR,)]
        assert set(inspect(engine).get_table_names()) == staged_tables
        assert query(engine, "SHOW CREATE TABLE energy_price_hour_meta") == staged_ddl
        assert query(engine, "SELECT * FROM energy_price_hour_meta") == []
        assert all(query(engine, f"SELECT * FROM {name} ORDER BY id") == rows for name, rows in raw_before.items())

    query(engine, "ALTER TABLE energy_price_hour_meta MODIFY id BIGINT NOT NULL")
    assert_conflict_preserved()
    query(engine, "ALTER TABLE energy_price_hour_meta MODIFY id BIGINT NOT NULL AUTO_INCREMENT")
    query(engine, "ALTER TABLE energy_price_hour_meta ADD UNIQUE INDEX qa1_unique_actor (operator)")
    assert_conflict_preserved()
    query(engine, "ALTER TABLE energy_price_hour_meta DROP INDEX qa1_unique_actor")

    run_migration(migrate, REVISION)
    assert query(engine, "SELECT version_num FROM alembic_version") == [(REVISION,)]
    assert query(engine, "SELECT id FROM energy_price_hour_meta ORDER BY id") == [(22,), (72,), (85,)]
    assert query(engine, "SELECT COUNT(*) FROM energy_price_item_hours") == [(9,)]

    async_engine = create_async_engine(async_url)
    sessions = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False)

    async def db():
        async with sessions() as session:
            yield session

    app = create_app(testing=True)
    app.dependency_overrides[get_db] = db
    headers = jwt_header("test_admin")
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
                                    base_url="http://fixture/api/v1") as client:
            response = await client.post(PRICING + "/hours", headers=headers, json={
                "observedAt": "2026-11-25T11:15:00+08:00",
                "items": {"electric": {"price": "0.9123"}},
            })
            assert response.status_code == 200, response.text
            assert response.json()["data"]["values"]["electric"]["price"] == 0.9123
            current = await client.get("/energy/current", headers=headers)
            assert current.status_code == 200, current.text
            row = current.json()["data"]
            assert (row["electricPrice"], row["hydrogenPrice"], row["argonPrice"]) == (0.9123, 3.0123, 999999.9999)
            assert row["id"] > max(price["id"] for price in legacy)
            assert query(engine, "SELECT id FROM energy_price_hour_meta ORDER BY id") == [(22,), (72,), (85,), (row["id"],)]
            assert all(query(engine, f"SELECT * FROM {name} ORDER BY id") == rows for name, rows in raw_before.items())
    finally:
        await async_engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("target", [REVISION], indirect=True)
@pytest.mark.parametrize("full", [False, True])
async def test_explicit_migration_recovery_rollback_and_routed_api(target, monkeypatch, full):
    engine, async_url, migrate, identity = target
    monkeypatch.setattr(routes, "get_profile", lambda: fixture_profile(identity))
    monkeypatch.setattr(energy_price, "utc_now", lambda: FIXED_NOW)
    run_migration(migrate, PREDECESSOR)
    legacy = seed_legacy_prices(engine, full)
    with Session(engine) as session:
        seed_curve_metrics(session)
        seed_curve_samples(session)
    observation_before = snapshot(engine)
    raw_before = {name: query(engine, f"SELECT * FROM {name} ORDER BY id") for name in ("energy_price_hours", "energy_prices")}
    code, log = migrate(REVISION, expected_server=str(uuid4()))
    assert code != 0 and "target or write window mismatch" in log
    assert not set(table.name for table in PRICE_TABLES).intersection(inspect(engine).get_table_names())

    # 模拟 DDL 已提交，回填发生 SQL 错误。目标 revision 与三个业务表行保持未采用状态。
    if full:
        query(engine, "CREATE TABLE energy_price_items (marker INT NOT NULL) ENGINE=InnoDB")
        query(engine, "INSERT INTO energy_price_items VALUES (91)")
        code, log = migrate(REVISION)
        assert code != 0 and "staged table differs" in log
        assert query(engine, "SELECT marker FROM energy_price_items") == [(91,)]
        query(engine, "DROP TABLE energy_price_items")
    for table in PRICE_TABLES:
        table.create(engine)
    if full:
        query(engine, """CREATE TRIGGER pricing_fail_import BEFORE INSERT ON energy_price_item_hours
            FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'isolated price import interruption'""")
        code, log = migrate(REVISION)
        assert code != 0 and "isolated price import interruption" in log, log
        assert query(engine, "SELECT version_num FROM alembic_version") == [(PREDECESSOR,)]
        for table in PRICE_TABLES:
            assert query(engine, f"SELECT count(*) FROM {table.name}") == [(0,)]
        query(engine, "DROP TRIGGER pricing_fail_import")

    run_migration(migrate, REVISION)
    run_migration(migrate, REVISION)
    assert query(engine, "SELECT COUNT(*) FROM energy_price_item_hours") == [(len(legacy) * 3,)]
    run_migration(migrate, PREDECESSOR, "downgrade")
    assert not set(table.name for table in PRICE_TABLES).intersection(inspect(engine).get_table_names())
    assert all(query(engine, f"SELECT * FROM {name} ORDER BY id") == rows for name, rows in raw_before.items())
    run_migration(migrate, REVISION)

    async_engine = create_async_engine(async_url)
    sessions = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False)

    async def db():
        async with sessions() as session:
            yield session

    app = create_app(testing=True)
    app.dependency_overrides[get_db] = db
    app.state.role_api_permissions = {
        "operator": {"energy-price-read"},
        "supervisor": {"energy-price-manage"},
    }
    admin, reader, writer = (jwt_header("test_" + role) for role in ("admin", "read", "manage"))
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app, raise_app_exceptions=False), base_url="http://fixture/api/v1") as client:
            async def data(method, path, headers=admin, expected=200, **arguments):
                result = await client.request(method, path, headers=headers, **arguments)
                assert result.status_code == expected, result.text
                return result.json().get("data")

            assert await data("GET", "/energy") == {"items": legacy, "total": len(legacy), "page": 1, "pageSize": 20}
            assert await data("GET", "/energy/current") == (legacy[0] if full else None)
            historical = await data("GET", PRICING + "/hours?date=1991-09-15")
            if full:
                assert historical["items"][0]["hourStart"] == "1991-09-15T00:00:00+08:00"
                assert historical["items"][0]["values"]["electric"]["observedAt"] == "1991-09-15T01:30:00+08:00"
                assert historical["items"][0]["values"]["hydrogen"]["remark"] == ""
                assert (await data("GET", "/energy?date=2026-11-23"))["items"] == [legacy[1]]
                assert (await data("GET", PRICING + "/hours?date=2026-11-24"))["total"] == 1
            else:
                assert historical["items"] == []

            assert (await client.get(PRICING + "/items")).status_code == 401
            assert (await client.get(PRICING + "/items", headers=writer)).status_code == 403
            assert [item["itemKey"] for item in await data("GET", PRICING + "/items", reader)] == ["electric", "hydrogen", "argon"]
            water = {"itemKey": " water_feed ", "nameZh": "工业用水", "unit": "元/m³", "sortOrder": 15}
            for actor in (reader, writer):
                assert (await client.post(PRICING + "/items", headers=actor, json=water)).status_code == 403
            assert (await data("POST", PRICING + "/items", json=water))["itemKey"] == "water_feed"
            assert (await client.post(PRICING + "/items", headers=admin, json=water)).status_code == 409
            water_path = PRICING + "/items/water_feed"
            assert (await data("PATCH", water_path, json={"nameEn": "Water", "sortOrder": 5}))["nameEn"] == "Water"
            assert (await client.patch(water_path, headers=admin, json={"itemKey": "other"})).status_code == 422
            current = await data("GET", PRICING + "/current", reader)
            assert current[0] == dict(itemKey="water_feed", nameZh="工业用水", nameEn="Water", unit="元/m³",
                                      price=None, remark=None, observedAt=None, updatedAt=None, operator=None)
            blank = await data("GET", PRICING + "/hours?date=2026-11-20&page=9&pageSize=1")
            assert blank["items"] == [] and blank["total"] == 0
            assert [item["itemKey"] for item in blank["columns"]] == ["water_feed", "electric", "hydrogen", "argon"]

            old_write = {"electricPrice": "0.8", "hydrogenPrice": "3", "argonPrice": "4",
                         "observedAt": "2026-11-25T10:03:00+08:00", "remark": "prior"}
            record_hour = "2026-11-25T11:15:00+08:00"

            async def write(items, when=record_hour, **extras):
                return await data("POST", PRICING + "/hours", writer, json={"observedAt": when, "items": items, **extras})

            first = await write({"electric": {"price": "0.9", "remark": "e"}})
            assert set(first["values"]) == {"electric"}
            if not full:
                assert await data("GET", "/energy/current") is None
            old = await data("POST", "/energy", writer, json=old_write)
            assert old["id"] > max((item["id"] for item in legacy), default=0)
            next_view = await data("GET", "/energy/current")
            assert [next_view[key + "Price"] for key in ("electric", "hydrogen", "argon")] == [0.9, 3, 4]
            assert next_view["id"] != old["id"]
            await write({"hydrogen": {"price": "3.4321"}}, "2026-11-25T10:04:00+08:00")
            snapshot_view = await data("GET", "/energy/current")
            assert snapshot_view["id"] == next_view["id"] and snapshot_view["hydrogenPrice"] == 3.4321
            assert snapshot_view["updatedAt"] > next_view["updatedAt"]
            await write({"water_feed": {"price": 0, "remark": "water"}})
            assert await data("GET", "/energy/current") == snapshot_view
            await write({"water_feed": {"price": 0.0001}})
            actual = await data("GET", PRICING + "/hours?date=2026-11-25&pageSize=1")
            assert set(actual["items"][0]["values"]) == {"electric", "water_feed"}
            assert actual["items"][0]["values"]["water_feed"]["remark"] == "water"
            await write({"water_feed": {"price": 0, "remark": ""}}, remark="group")
            updated_legacy = await data("GET", "/energy/current")
            assert updated_legacy["remark"] == "group" and updated_legacy["observedAt"] == snapshot_view["observedAt"]
            assert updated_legacy["updatedAt"] > snapshot_view["updatedAt"]
            await write({"water_feed": {"price": 0}}, remark=None)
            assert (await data("GET", "/energy/current"))["remark"] is None
            assert (await client.patch(water_path, headers=admin, json={"unit": "元/L"})).status_code == 422
            await data("PATCH", water_path, json={"enabled": False})
            assert [item["itemKey"] for item in await data("GET", PRICING + "/current")] == ["electric", "hydrogen", "argon"]
            for page in (1, 2, 999):
                historical = await data("GET", PRICING + f"/hours?date=2026-11-25&pageSize=1&page={page}")
                assert historical["columns"][0]["itemKey"] == "water_feed"
                assert historical["total"] == 2
            assert all(item["itemKey"] != "water_feed" for item in (await data("GET", PRICING + "/hours?date=2026-11-20"))["columns"])
            assert (await client.post(PRICING + "/hours", headers=writer, json={"items": {"water_feed": {"price": 1}}})).status_code == 422
            await data("PATCH", water_path, json={"enabled": True})

            before = await data("GET", PRICING + "/hours")
            for literal in ('1.234500000000000001', 'NaN', '-0.0001', '1000000', 'true'):
                bad = await client.post(PRICING + "/hours", headers={**writer, "Content-Type": "application/json"},
                                        content='{"items":{"electric":{"price":' + literal + '},"water_feed":{"price":1}}}')
                assert bad.status_code == 422, bad.text
            assert (await client.post(PRICING + "/hours", headers=writer,
                                      json={"items": {"water_feed": {"price": 8}, "missing": {"price": 9}}})).status_code == 422
            assert (await client.post(PRICING + "/hours", headers=writer,
                                      json={"observedAt": "2999-01-01T01:00:00+08:00", "items": {"water_feed": {"price": 0}}})).status_code == 422
            query(engine, """CREATE TRIGGER pricing_fail_write BEFORE INSERT ON energy_price_item_hours
                FOR EACH ROW BEGIN IF NEW.item_key = 'hydrogen' THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'synthetic second price failure'; END IF; END""")
            await data("POST", PRICING + "/hours", writer, json={
                "items": {"water_feed": {"price": 9}, "hydrogen": {"price": 8}},
                "observedAt": "2026-11-25T09:15:00+08:00",
            }, expected=500)
            query(engine, "DROP TRIGGER pricing_fail_write")
            assert await data("GET", PRICING + "/hours") == before
            assert (await client.post(PRICING + "/hours", headers=reader, json={"items": {"water_feed": {"price": 1}}})).status_code == 403

            await check_competing_writes(data, write, writer, old_write)
            assert all(query(engine, f"SELECT * FROM {name} ORDER BY id") == rows for name, rows in raw_before.items())
            assert snapshot(engine) == observation_before
            parameters = {"meterId": "meter1", "groupKey": "electricity", "from": "2026-11-24T12:00:00+08:00",
                          "to": "2026-11-24T12:00:40+08:00"}
            observed_paths = ((LATEST, {"equipmentId": "line", "pageKey": "temperature"}), (PROCESS, {"equipmentId": "line", "category": "temperature",
                                                     "from": parameters["from"], "to": parameters["to"]}),
                              (SAMPLES, parameters), (PUBLIC_SAMPLES, parameters))
            baseline = [await data("GET", path, params=params) for path, params in observed_paths]
            run_migration(migrate, SUCCESSOR)
            same_price = await write({"water_feed": {"price": 0}})
            assert same_price["values"]["water_feed"]["price"] == 0
            assert (await data("GET", PRICING + "/current"))[0]["price"] == 0
            assert [await data("GET", path, params=params) for path, params in observed_paths] == baseline
            run_migration(migrate, REVISION, "downgrade")

            # 回退演练：完整保留新数据，验证兼容投影可转换回 UTC 旧格式。
            exported = await data("GET", PRICING + "/hours")
            compatible = await data("GET", "/energy")
            assert restored_legacy_copy(engine, compatible["items"]) == compatible["items"]
            assert any("water_feed" in row["values"] for row in exported["items"])
            code, log = migrate(PREDECESSOR, "downgrade")
            assert code != 0 and "reconciliation failed" in log
            assert await data("GET", PRICING + "/hours") == exported
    finally:
        await async_engine.dispose()



def restored_legacy_copy(engine, rows):
    # 在临时恢复表中演练回退投影。源表与新事实全程保留。
    fields = tuple(EnergyPriceHour.__table__.columns.keys())
    name = "pricing_rollback_fixture"
    columns = ", ".join(fields)
    binds = ", ".join(":" + field for field in fields)
    with engine.begin() as connection:
        connection.execute(text(f"CREATE TEMPORARY TABLE {name} LIKE energy_price_hours"))
        try:
            for row in rows:
                values = dict(HourlyPriceRecord.model_validate(row))
                for key in ("hour_start", "observed_at", "created_at", "updated_at"):
                    values[key] = values[key].astimezone(timezone.utc).replace(tzinfo=None)
                connection.execute(text(f"INSERT INTO {name} ({columns}) VALUES ({binds})"), values)
            restored = connection.execute(text(f"SELECT * FROM {name} ORDER BY observed_at DESC, id DESC")).mappings()
            return [HourlyPriceRecord.model_validate(row).model_dump(mode="json", by_alias=True) for row in restored]
        finally:
            connection.execute(text(f"DROP TEMPORARY TABLE {name}"))


async def check_competing_writes(data, write, writer, original):
    hour = "2026-11-25T12:00:00+08:00"
    by_name = lambda key, price: {key: {"price": price}}
    await asyncio.gather(write(by_name("electric", 2), hour), write(by_name("hydrogen", 5), hour))
    result = await data("GET", PRICING + "/hours?date=2026-11-25&pageSize=1")
    assert {key: value["price"] for key, value in result["items"][0]["values"].items()} == {"electric": 2, "hydrogen": 5}
    await asyncio.gather(write(by_name("electric", 6), hour), write(by_name("electric", 7), hour))
    current = await data("GET", "/energy/current")
    assert current["electricPrice"] in {6, 7} and current["hydrogenPrice"] == 5
    payload = {**original, "observedAt": hour, "electricPrice": 8, "hydrogenPrice": 9, "argonPrice": 10}
    await asyncio.gather(data("POST", "/energy", writer, json=payload), write(by_name("electric", 11), hour))
    current = await data("GET", "/energy/current")
    assert current["electricPrice"] in {8, 11} and current["hydrogenPrice"] == 9 and current["argonPrice"] == 10
    imported = await write(by_name("electric", 33), "2026-11-23T13:00:00+08:00")
    changed = await data("GET", "/energy/current")
    assert changed == current and imported["values"]["electric"]["price"] == 33
    newest = await data("GET", PRICING + "/current")
    assert next(item for item in newest if item["itemKey"] == "electric")["price"] == current["electricPrice"]
