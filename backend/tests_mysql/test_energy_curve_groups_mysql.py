"""在专用 MySQL 验证能耗曲线迁移保护、历史数据与并发部分更新。"""
import asyncio
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI
import httpx
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from app.equipment_observation.api import routes
from app.equipment_observation.models import EnergyMetric, EnergyReceipt, EnergySample, HistorySample, LatestSnapshot, Receipt
from database import get_db
from tests.test_energy_curve_groups import CONSUMPTION, MANAGEMENT, TABLE, assert_error, payload, seed_curve_metrics, series
from tests.test_energy_public_reads import HISTORY, LATEST
from tests.test_energy_registered_ingest import ADMIN, MANAGE, OPERATOR, WRITE, install_auth
from tests.test_equipment_observation_r10_flow import document
from tests_mysql.test_energy_registered_ingest_mysql import (
    LEGACY_ROUTE, MACHINE, METER_REVISION, SUCCESSOR, fixture_profile, query, snapshot, target,  # noqa: F401
)

REVISION = "af6d8b2c4e90"
STAMP = datetime(2026, 11, 24, 12)


def seed_curve_samples(session):
    total = session.get(EnergyMetric, ("meter1", "electricity", "total"))
    total.rules = {"continuityConfirmed": True, "maxGapSeconds": 60}
    receipt = EnergyReceipt(target="energy", producer_id="curve-fixture", event_id="retained",
                            request_digest=bytes(32), outcome="stored", processed_at=STAMP)
    session.add(receipt)
    session.flush()
    for sec, values, quality, interval in (
        (0, {"01": 0, "02": 4, "04": 12}, "good", None),
        (20, {"02": 5, "04": 14}, "good", None),
        (20, {"01": 5, "04": 14}, "bad", None),
        (40, {"01": 0, "02": 7, "04": 17, "05": 5}, "good", (0, 40)),
        (50, {"01": 0, "02": 7, "04": 18}, "good", None),
    ):
        session.add(EnergySample(meter_id="meter1", group_key="electricity", observed_at=STAMP.replace(second=sec),
            quality=quality, interval_start_at=STAMP.replace(second=interval[0]) if interval else None,
            interval_end_at=STAMP.replace(second=interval[1]) if interval else None,
            local_values=values, ingest_receipt_id=receipt.id, created_at=STAMP, updated_at=STAMP))
    session.add(EnergySample(meter_id="meter2", group_key="electricity", observed_at=STAMP,
                            quality="good", local_values={"03": 23}, ingest_receipt_id=receipt.id))
    for kind, model in (("latest", LatestSnapshot), ("history", HistorySample)):
        retained = Receipt(target=kind, producer_id="curve-fixture", event_id="retained",
                           request_digest=bytes(32), outcome="stored", processed_at=STAMP)
        session.add(retained)
        session.flush()
        session.add(model(equipment_id="line", task_no="000042", observed_at=STAMP, quality="good",
                          source_sample_key=bytes(32), ingest_receipt_id=retained.id,
                          local_values={}, created_at=STAMP, updated_at=STAMP))
    session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize("target", [REVISION], indirect=True)
async def test_curve_migration_guarded_successor_and_http(target, monkeypatch):
    engine, async_url, migrate, identity = target
    monkeypatch.setattr(routes, "get_profile", lambda: fixture_profile(identity))
    code, log = migrate(METER_REVISION)
    assert code == 0, log
    with Session(engine) as session:
        seed_curve_metrics(session)
        seed_curve_samples(session)
    before = snapshot(engine)
    tables = set(inspect(engine).get_table_names())
    code, log = migrate(REVISION, expected_server=str(uuid4()))
    assert code != 0 and "migration target mismatch" in log
    assert set(inspect(engine).get_table_names()) == tables

    # 模拟 DDL 后版本尚未推进的中断。目标出现时必须停住，保留内容供维护审查。
    query(engine, f"CREATE TABLE {TABLE} (marker INT NOT NULL)")
    query(engine, f"INSERT INTO {TABLE} VALUES (71)")
    code, log = migrate(REVISION)
    assert code != 0 and "curve group table already exists" in log
    assert query(engine, f"SELECT marker FROM {TABLE}") == [(71,)]
    assert query(engine, "SELECT version_num FROM alembic_version") == [(METER_REVISION,)]
    query(engine, f"DROP TABLE {TABLE}")
    code, log = migrate(REVISION)
    assert code == 0, log
    assert set(inspect(engine).get_table_names()) == tables | {TABLE}
    assert inspect(engine).get_foreign_keys(TABLE) == []
    assert snapshot(engine) == before

    async_engine = create_async_engine(async_url)
    sessions = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False)

    async def db():
        async with sessions() as session:
            yield session

    app = FastAPI()
    app.include_router(routes.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = db
    install_auth(app)
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://fixture/api/v1") as client:
            await check_curves(client, engine, migrate, before)
    finally:
        await async_engine.dispose()


async def check_curves(client, engine, migrate, before):
    for path in (MANAGEMENT, CONSUMPTION):
        assert (await client.get(path, headers=ADMIN)).json()["data"] == []
    parameters = {"meterId": "meter1", "groupKey": "electricity", "from": "2026-11-24T12:00:00+08:00",
                  "to": "2026-11-24T12:00:40+08:00"}
    base = "/energy/consumption"
    result = await client.get(base + "/samples", params={**parameters, "pageSize": 2}, headers=OPERATOR)
    assert result.status_code == 200 and result.json()["data"]["totalPages"] == 2, result.text
    seed = payload("curves", series=[series("standby", style="dashed"), series("primary")])
    responses = await asyncio.gather(*(client.post(MANAGEMENT, headers=ADMIN, json=seed) for _ in range(2)))
    assert sorted(result.status_code for result in responses) == [200, 409]
    changes = ({"titleEn": "Concurrent"}, {"sortOrder": 8}, {"series": [series("primary"), series("standby", style="dashed")]})
    responses = await asyncio.gather(*(client.patch(MANAGEMENT + "/curves", headers=ADMIN, json=change) for change in changes))
    assert [response.status_code for response in responses] == [200, 200, 200], [response.text for response in responses]
    expected = {**seed, **changes[0], **changes[1], **changes[2]}
    assert (await client.get(CONSUMPTION, headers=OPERATOR)).json()["data"] == [expected]
    assert_error(await client.get(CONSUMPTION, headers=OPERATOR, params={"meterId": "meter2"}), 403, "forbidden")

    for key, fields in (
        ("primary", {"state": "reading", "latest": 0, "amount": None, "reason": "instantaneous_not_usage"}),
        ("standby", {"state": "reading", "latest": 7, "amount": None, "reason": "instantaneous_not_usage"}),
        ("total", {"state": "incomplete", "latest": 17, "amount": None, "reason": "bad_or_missing_sample"}),
        ("increment", {"state": "complete", "latest": 5, "amount": 5, "reason": None}),
    ):
        result = await client.get(base + "/summary", params={**parameters, "metricKey": key}, headers=OPERATOR)
        data = result.json()["data"]
        assert {key: data[key] for key in fields} == fields, result.text
    assert snapshot(engine) == before
    public_before = (await client.get(HISTORY, params=parameters)).json()
    assert len(public_before["data"]["items"]) == 4
    code, log = migrate(SUCCESSOR)
    assert code == 0, log
    assert (await client.get(CONSUMPTION, headers=OPERATOR)).json()["data"] == [expected]
    assert (await client.patch(MANAGEMENT + "/curves", headers=ADMIN, json={"enabled": False})).status_code == 200
    assert (await client.get(CONSUMPTION, headers=OPERATOR)).json()["data"] == []
    assert (await client.get(HISTORY, params=parameters)).json() == public_before
    assert (await client.get(LATEST)).status_code == 200

    assert (await client.post(MANAGE, headers=ADMIN, json={"sourceKey": "Line.A"})).status_code == 200
    batch = {"sourceKey": "Line.A", "target": "energy", "observedAt": "2026-11-24T12:00:30+08:00",
             "items": {"meter1": {"electricity": {"values": {"primary": 0}}}}}
    stored = await client.post(WRITE, json=batch)
    assert stored.status_code == 200, stored.text
    assert (await client.post(WRITE, json=batch)).json() == stored.json()
    # 旧同路径 POST 继续要求机器 Bearer 和既有 grant。
    assert (await client.post(LEGACY_ROUTE, json=document())).status_code == 401
    assert (await client.post(LEGACY_ROUTE, headers=MACHINE, json=document())).status_code == 422
    code, log = migrate(REVISION, "downgrade")
    assert code == 0, log
    code, log = migrate(METER_REVISION, "downgrade")
    assert code != 0 and "retain energy curve groups" in log
    assert query(engine, f"SELECT curve_group_key FROM {TABLE}") == [("curves",)]
    for table in ("equipment_main", "monitor_main", "observation_ingest_receipts"):
        assert snapshot(engine)[table] == before[table]
