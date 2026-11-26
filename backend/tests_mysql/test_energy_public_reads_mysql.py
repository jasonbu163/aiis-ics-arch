"""在明确隔离的 MySQL 和回环 HTTP 上验证能耗公有读取。"""
import asyncio
from contextlib import redirect_stdout
from io import StringIO
import re
import socket

from fastapi import FastAPI
import httpx
import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session
import uvicorn

from app.equipment_observation.api import routes
from app.equipment_observation.models import MetricConfig, MetricGroup, SlotBinding
from app.user.models.user import User
from database import get_db
from tests.test_energy_public_reads import CONTRACT, HISTORY, HISTORY_QUERY, LATEST, check_history, check_latest, data, seed_samples
from tests.test_energy_registered_ingest import MANAGE, WRITE, batch, metrics
from tests.test_equipment_observation_r10_flow import document
from tests_mysql.test_energy_registered_ingest_mysql import (
    LEGACY_ROUTE, MACHINE, METER_REVISION, STAMP, SUCCESSOR, fixture_profile, jwt_header, query, snapshot, target,  # noqa: F401
)

@pytest.mark.asyncio
@pytest.mark.parametrize("target", [METER_REVISION], indirect=True)
async def test_public_reads_on_mysql_and_loopback_http(target, monkeypatch):
    engine, async_url, migrate, target_profile = target
    code, log = migrate(METER_REVISION)
    assert code == 0, log
    profile = fixture_profile(target_profile)
    monkeypatch.setattr(routes, "get_profile", lambda: profile)
    with Session(engine) as session:
        session.add(User(username="admin", password="isolated-fixture-not-a-login", name="Admin", role="admin", is_active=True))
        session.add(MetricGroup(group_key="heatZone1", category="temperature", name_zh="温区",
                                name_en="Heat zone", enabled=True, sort_order=0))
        session.add(MetricConfig(metric_key="actual", source_group_key="heatZone1", category="temperature",
                                 name_zh="实测", name_en="Actual", value_type="number"))
        session.flush()
        for kind in ("latest", "history"):
            session.add(SlotBinding(target=kind, group_key="heatZone1", slot_no=1, metric_key="actual", enabled=True))
        metrics(session)
        seed_samples(session)

    async_engine = create_async_engine(async_url, isolation_level="READ COMMITTED")
    sessions = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False)

    async def database():
        async with sessions() as session:
            yield session

    app = FastAPI()
    app.include_router(routes.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = database
    legacy = {"eventId": "read-fixture-legacy", "data": {"meterId": "meter2", "groupKey": "electricity",
              "observedAt": "2026-11-24T11:00:00+08:00", "quality": "good", "values": {"activePower": 1}}}
    observation = document(timestamp=STAMP)
    observation["data"]["groups"] = {"heatZone1": {"actual": 55}}
    admin = jwt_header("admin")

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://fixture/api/v1") as client:
        try:
            baseline = snapshot(engine)
            await check_latest(client)
            await check_history(client)
            assert snapshot(engine) == baseline
            assert (await client.post(LEGACY_ROUTE, json=legacy)).status_code == 401
            assert (await client.post(LEGACY_ROUTE, headers={"Authorization": "Bearer invalid"}, json=legacy)).status_code == 401
            assert (await client.get("/energy/consumption/samples", params={"meterId": "meter2"})).status_code == 401
            assert (await client.get("/energy/metric-configs")).status_code == 401
            assert (await client.get(MANAGE)).status_code == 401
            assert (await client.post(LEGACY_ROUTE, headers=MACHINE, json=legacy)).status_code == 200
            old = (await data(client, LATEST, {"meterId": "meter2"}))["items"]
            assert old[0]["values"] == {"activePower": 1}

            assert (await client.post(MANAGE, headers=admin, json={"sourceKey": "Line.A"})).status_code == 200
            written = await client.post(WRITE, json=batch())
            assert written.status_code == 200 and len(written.json()["data"]["records"]) == 2
            assert (await client.post(WRITE, json=batch())).json() == written.json()
            assert (await client.delete(MANAGE + "/Line.A", headers=admin)).status_code == 200
            stored = (await data(client, LATEST, {"meterId": "meter2"}))["items"]
            assert stored[0]["values"] == {"totalEnergy": 9820, "activePower": 0}
            assert (await client.get("/energy/consumption/samples", headers=admin, params={"meterId": "meter2"})).status_code == 200
            for name in ("/integration/equipment/latest-snapshots", "/integration/monitor/history-samples"):
                previous = await client.post(name, headers=MACHINE, json=observation)
                assert previous.status_code == 200, previous.text
                assert (await client.post(name, headers=MACHINE, json=observation)).json() == previous.json()

            before = snapshot(engine)
            code, log = migrate(SUCCESSOR)
            assert code == 0, log
            assert query(engine, "SELECT version_num FROM alembic_version") == [(SUCCESSOR,)]
            assert (await data(client, LATEST, {"meterId": "meter2"}))["items"] == stored
            await check_history(client)
            await check_published_example(app)
            assert snapshot(engine) == before
            await check_concurrent_insert(client, engine, async_engine)

            profile["target"]["serverUuid"] = "00000000-0000-4000-8000-000000000001"
            assert (await client.get(LATEST)).status_code == 503
            profile["target"]["serverUuid"] = target_profile["serverUuid"]
            query(engine, "RENAME TABLE energy_metric_configs TO fixture_unavailable_metrics")
            for endpoint, params in ((LATEST, None), (HISTORY, HISTORY_QUERY)):
                response = await client.get(endpoint, params=params)
                assert response.status_code == 503
                assert response.json()["errorCode"] == "equipment_observation.not_ready"
        finally:
            await async_engine.dispose()


async def check_published_example(app):
    """运行发布的标准库样例，并以同一 HTTP 回包核对 SMA 固定取值路径。"""
    snippet = re.search(r"```python\n(.*?)\n```", (CONTRACT / "README.md").read_text(encoding="utf-8"), re.S).group(1)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        base = f"http://127.0.0.1:{listener.getsockname()[1]}/api/v1"
        server = uvicorn.Server(uvicorn.Config(app, lifespan="off", log_config=None, access_log=False, ws="none"))
        run = asyncio.create_task(server.serve(sockets=[listener]))
        try:
            async with asyncio.timeout(5):
                while not server.started:
                    await asyncio.sleep(0.01)
            scope = {}
            executable = snippet.replace("http://127.0.0.1:8000/api/v1", base).replace("pageSize=20", "pageSize=2")
            with redirect_stdout(StringIO()) as output:
                await asyncio.to_thread(exec, executable, scope)
            lines = output.getvalue().splitlines()
            assert len(lines) == 4 and lines[0].endswith(" 0") and "'totalEnergy': 9820" in lines[-1]
            async with httpx.AsyncClient(base_url=base) as client:
                pointers = ("items", 0, "values", "activePower")
                fixed = await data(client, LATEST, {"meterId": "meter-02", "groupKey": "electricity"})
                for part in pointers:
                    fixed = fixed[part]
                assert fixed == 0
                empty = await data(client, LATEST, {"meterId": "meter-99", "groupKey": "electricity"})
                assert empty["items"] == []
                missing = await data(client, LATEST, {"meterId": "meter-01", "groupKey": "electricity"})
                assert missing["items"][0]["values"].get("activePower") is None
        finally:
            server.should_exit = True
            await asyncio.wait_for(run, 5)


async def check_concurrent_insert(client, engine, async_engine):
    """READ COMMITTED 下在样本 SELECT 后插入新值，验证页和总数一致。"""
    sample_reads = []

    def after_sample_read(_connection, _cursor, statement, _parameters, _context, _many):
        if "energy_consumption_main" not in statement or sample_reads:
            return
        sample_reads.append(statement)
        query(engine, """INSERT INTO energy_consumption_main
            (meter_id, group_key, observed_at, quality, local_values, ingest_receipt_id, created_at, updated_at)
            SELECT meter_id, group_key, observed_at, quality, local_values, ingest_receipt_id, created_at, updated_at
            FROM energy_consumption_main WHERE meter_id='meter-02' AND group_key='electricity' ORDER BY id LIMIT 1""")

    event.listen(async_engine.sync_engine, "after_cursor_execute", after_sample_read)
    try:
        during = await data(client, HISTORY, HISTORY_QUERY)
    finally:
        event.remove(async_engine.sync_engine, "after_cursor_execute", after_sample_read)
    assert len(sample_reads) == 1
    assert during["total"] == len(during["items"]) == 3
    after = await data(client, HISTORY, HISTORY_QUERY)
    assert after["total"] == len(after["items"]) == 4
