"""在专用 MySQL 验证表计后继迁移、并发覆盖与读写兼容。"""
import asyncio
from uuid import uuid4

from fastapi import FastAPI
import httpx
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from app.equipment_observation.api import routes
from database import get_db
from tests.test_energy_public_reads import HISTORY, LATEST, seed_samples
from tests.test_energy_registered_ingest import ADMIN, MANAGE, OPERATOR, WRITE, batch, install_auth, metrics
from tests_mysql.test_energy_registered_ingest_mysql import (
    LEGACY_ROUTE, MACHINE, METER_REVISION, REVISION, SUCCESSOR, fixture_profile, snapshot, target,  # noqa: F401
)

METERS = "/energy/meters"
OPTIONS = "/energy/consumption/options"


@pytest.mark.asyncio
@pytest.mark.parametrize("target", [METER_REVISION], indirect=True)
async def test_meter_migration_permissions_and_atomic_updates(target, monkeypatch):
    engine, async_url, migrate, identity = target
    profile = fixture_profile(identity)
    profile["meterReadScopes"]["localReviewer"] = ["meter1"]
    monkeypatch.setattr(routes, "get_profile", lambda: profile)
    code, log = migrate(REVISION)
    assert code == 0, log
    with Session(engine) as session:
        metrics(session)
        seed_samples(session)
        session.execute(text("UPDATE energy_consumption_main SET meter_id='meter1' WHERE meter_id='meter-01'"))
        session.commit()
    original = snapshot(engine)
    tables = set(inspect(engine).get_table_names())
    code, log = migrate(METER_REVISION, expected_server=str(uuid4()))
    assert code != 0 and "target mismatch" in log
    assert set(inspect(engine).get_table_names()) == tables
    code, log = migrate(METER_REVISION)
    assert code == 0, log
    assert set(inspect(engine).get_table_names()) == tables | {"energy_meters"}
    assert inspect(engine).get_foreign_keys("energy_meters") == []
    assert snapshot(engine) == original
    code, log = migrate(SUCCESSOR)
    assert code == 0, log

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
            await _check_http(client, engine, profile, original)
            code, log = migrate(REVISION, "downgrade")
            assert code != 0 and "retain energy meter definitions" in log
    finally:
        await async_engine.dispose()


async def _check_http(client, engine, profile, original):
    async def meters():
        result = await client.get(METERS, headers=ADMIN)
        assert result.status_code == 200, result.text
        return {item["meterId"]: item for item in result.json()["data"]}

    assert (await client.get(METERS)).status_code == 401
    assert (await client.get(METERS, headers=OPERATOR)).status_code == 403
    before = await meters()
    assert before["meter1"]["readRoles"] == ["admin", "localReviewer", "operator"]
    assert [row["meterId"] for row in (await client.get(OPTIONS, headers=OPERATOR)).json()["data"]] == ["meter1"]
    assert before["meter1"]["nameZh"] == profile["meters"]["meter1"]["nameZh"]
    calls = [client.patch(METERS, headers=ADMIN, json={"meterId": "meter1", key: value})
             for key, value in (("nameZh", "并发表"), ("nameEn", "Concurrent Meter"))]
    concurrent = await asyncio.gather(*calls)
    assert [result.status_code for result in concurrent] == [200, 200], [result.text for result in concurrent]
    override = (await meters())["meter1"]
    assert override == {**before["meter1"], "nameZh": "并发表", "nameEn": "Concurrent Meter"}
    assert profile["meters"]["meter1"]["nameZh"] == before["meter1"]["nameZh"]
    payload = {"meterId": "水表/A.1", "nameZh": "水表", "nameEn": "Water meter"}
    created = await asyncio.gather(*(client.post(METERS, headers=ADMIN, json=payload) for _ in range(2)))
    assert sorted(result.status_code for result in created) == [200, 409], [r.text for r in created]
    assert (await client.post(METERS, headers=ADMIN, json={**payload, "meterId": "水表/a.1"})).status_code == 200
    assert (await client.post(METERS, headers=ADMIN, json={**payload, "meterId": "meter2"})).status_code == 409
    assert (await client.patch(METERS, headers=ADMIN, json={**payload, "nameZh": "自来水"})).status_code == 200
    assert (await client.patch(METERS, headers=ADMIN, json={"meterId": "unknown", "nameZh": "无"})).status_code == 404
    for invalid in ({"meterId": payload["meterId"]}, {**payload, "enabled": True}, {**payload, "nameEn": None}):
        result = await client.patch(METERS, headers=ADMIN, json=invalid)
        assert result.status_code == 422 and result.json()["errorCode"] == "equipment_observation.invalid_request"

    latest = (await client.get(LATEST)).json()["data"]
    history_params = {"meterId": "meter1", "from": "2026-11-24T10:00:00+08:00", "to": "2026-11-24T13:00:00+08:00"}
    historical = await client.get(HISTORY, params=history_params)
    assert historical.status_code == 200, historical.text
    assert (await client.patch(METERS, headers=ADMIN, json={"meterId": "meter1", "readRoles": ["localReviewer"]})).status_code == 200
    assert (await client.get(OPTIONS, headers=OPERATOR)).json()["data"] == []
    for path in ("/energy/consumption/definitions", "/energy/consumption/samples", "/energy/consumption/summary",
                 "/energy/metric-configs", "/energy/admin/consumption-samples"):
        result = await client.get(path, headers=ADMIN, params={**history_params, "groupKey": "electricity", "metricKey": "intervalEnergy"})
        assert result.status_code == 403, (path, result.text)
    with engine.connect() as db:
        sample_id = db.execute(text("SELECT id FROM energy_consumption_main WHERE meter_id='meter1' LIMIT 1")).scalar_one()
    assert (await client.patch(f"/energy/admin/consumption-samples/{sample_id}", headers=ADMIN, json={"remark": "hidden"})).status_code == 404
    assert (await client.get(LATEST)).json()["data"] == latest
    assert (await client.get(HISTORY, params=history_params)).json() == historical.json()
    assert snapshot(engine) == original

    metric = {"meterId": payload["meterId"], "groupKey": "electricity", "metricKey": "reading",
              "slotNo": 1, "nameZh": "读数", "nameEn": "Reading", "valueType": "number",
              "measurementMode": "cumulative", "quantityKey": "energy", "enabled": True}
    saved = await client.post("/energy/metric-configs", headers=ADMIN, json=metric)
    assert saved.status_code == 200, saved.text
    assert (await client.post(MANAGE, headers=ADMIN, json={"sourceKey": "Line.A"})).status_code == 200
    document = batch()
    document["observedAt"] = "2026-11-24T12:59:00+08:00"
    document["items"][payload["meterId"]] = {"electricity": {"values": {"reading": 0}}}
    write = await client.post(WRITE, json=document)
    assert write.status_code == 200, write.text
    assert len(write.json()["data"]["records"]) == 3
    legacy = {"eventId": "meter005-legacy", "data": {"meterId": "meter2", "groupKey": "electricity",
              "observedAt": "2026-11-24T12:57:00+08:00", "quality": "good", "values": {"activePower": 1}}}
    written = await client.post(LEGACY_ROUTE, headers=MACHINE, json=legacy)
    assert written.status_code == 200, written.text
    assert (await client.post(LEGACY_ROUTE, headers=MACHINE, json=legacy)).json() == written.json()
    legacy["eventId"] = "meter005-legacy-unknown"
    legacy["data"]["meterId"] = payload["meterId"]
    assert (await client.post(LEGACY_ROUTE, headers=MACHINE, json=legacy)).status_code == 403

    with engine.begin() as db:
        times = db.execute(text("SELECT created_at, updated_at FROM energy_meters WHERE meter_id='meter1'")).one()
        assert times[0] <= times[1]
        db.execute(text("RENAME TABLE energy_meters TO meter005_hidden"))
    failed = await client.get(OPTIONS, headers=ADMIN)
    assert failed.status_code == 503 and failed.json()["errorCode"] == "equipment_observation.not_ready"
    assert (await client.get(MANAGE, headers=ADMIN)).status_code == 200
    assert (await client.get(LATEST)).status_code == 200
    assert (await client.post(WRITE, json=document)).json() == write.json()
    with engine.begin() as db:
        db.execute(text("RENAME TABLE meter005_hidden TO energy_meters"))
