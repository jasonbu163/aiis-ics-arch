"""在明确确认的专用 MySQL 上验证 OBS-010 的迁移、写入竞争和恢复。"""
import asyncio
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import os
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi import FastAPI
from jose import jwt
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.equipment_observation.api import routes
from app.equipment_observation.models import EnergyReceipt, EnergySample
from app.equipment_observation.profile import parse_profile
from app.equipment_observation.services.energy_write_sources import storage_identity
from app.user.models.token_blacklist import TokenBlacklist
from app.user.models.user import User
from database import Base, get_db
from settings import settings
from tests.test_energy_registered_ingest import MANAGE, WRITE, batch, metrics
from tests.test_equipment_observation_r10_flow import document as legacy_equipment

PREDECESSOR = "a1c307f8d2e4"
REVISION = "b52e9c416a07"
SUCCESSOR = "obs010_unrelated"
ROOT = Path(__file__).resolve().parents[1]
STAMP = "2026-11-24T12:00:00.000000+08:00"
LEGACY_EVENT = "energyreg1_" + STAMP
LEGACY_ROUTE = "/integration/energy/samples"
MACHINE = {"Authorization": "Bearer obs010-legacy-fixture"}
PROTECTED = (
    "energy_metric_configs", "energy_ingest_receipts", "energy_consumption_main", "observation_write_sources",
    "observation_ingest_receipts", "equipment_main", "monitor_main",
)


@pytest.fixture
def target(monkeypatch, tmp_path):
    port, server, password, confirm = [os.getenv("OBS010_TEST_" + key) for key in ("PORT", "UUID", "PASSWORD", "ACK")]
    if not all((port, server, password, confirm)):
        pytest.skip("requires an explicitly confirmed isolated OBS-010 MySQL instance")
    assert port.isdecimal() and 20000 <= int(port) <= 65535 and str(UUID(server)) == server
    assert confirm == f"ARCH-OBS-010-r1:127.0.0.1:{port}:{server}"
    schema = "obs010_" + uuid4().hex
    url = URL.create("mysql+pymysql", "root", password, "127.0.0.1", int(port))
    root_engine = create_engine(url)
    with root_engine.begin() as db:
        assert db.execute(text("SELECT @@server_uuid")).scalar_one() == server
        db.execute(text(f"CREATE DATABASE `{schema}` DEFAULT CHARACTER SET utf8mb4"))
    db_url = url.set(database=schema)
    engine = create_engine(db_url)
    env = {
        **os.environ, "PYTHONPATH": str(ROOT), "PRIMARY_DATABASE": "mysql",
        "MYSQL_ENABLED": "true", "MYSQL_HOST": "127.0.0.1", "MYSQL_PORT": port, "MYSQL_USER": "root",
        "MYSQL_PASSWORD": password, "MYSQL_DATABASE": schema, "TEST_MYSQL_DATABASE": schema,
        "MYSQL_ROOT_USER": "root", "MYSQL_ROOT_PASSWORD": password, "TESTING": "true",
        "ENERGY_WRITE_EXPECTED_SCHEMA": schema, "ENERGY_WRITE_EXPECTED_SERVER_UUID": server,
        "JWT_SECRET_KEY": "obs010-isolated-credential", "ADMIN_BOOTSTRAP_ENABLED": "false",
    }

    # 用同一真实 Alembic entrypoint 执行任务迁移，合成后继只进入临时迁移副本。
    shutil.copytree(ROOT / "alembic", tmp_path / "alembic", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(ROOT / "alembic.ini", tmp_path / "alembic.ini")
    (tmp_path / "alembic/versions/obs010_unrelated.py").write_text(
        "from alembic import op\nimport sqlalchemy as sa\n"
        f"revision = '{SUCCESSOR}'\ndown_revision = '{REVISION}'\n"
        "def upgrade():\n    op.create_table('obs010_unrelated', sa.Column('id', sa.Integer, primary_key=True))\n"
        "def downgrade():\n    op.drop_table('obs010_unrelated')\n"
    )

    def migrate(revision, operation="upgrade", expected_server=server):
        result = subprocess.run([sys.executable, "-m", "alembic", operation, revision],
            cwd=tmp_path, env={**env, "ENERGY_WRITE_EXPECTED_SERVER_UUID": expected_server},
            capture_output=True, text=True, timeout=30)
        return result.returncode, (result.stdout + result.stderr).replace(password, "[redacted]")

    async_url = db_url.set(drivername="mysql+aiomysql")
    from app.equipment_observation import models as models
    old_models = (models.CardConfig, models.CurveGroup, models.MetricConfig, models.MetricGroup, models.SlotBinding,
                  models.WriteSource, models.Receipt, models.LatestSnapshot, models.HistorySample,
                  EnergyReceipt, EnergySample, models.EnergyMetric, User, TokenBlacklist)
    try:
        Base.metadata.create_all(engine, tables=[model.__table__ for model in old_models])
        with engine.begin() as db:
            db.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) PRIMARY KEY)"))
            db.execute(text("INSERT INTO alembic_version VALUES (:revision)"), {"revision": PREDECESSOR})
        yield engine, async_url, migrate, {"serverUuid": server, "schema": schema, "schemaRevision": "e9f3b5d7c021"}
    finally:
        engine.dispose()
        with root_engine.begin() as db:
            db.execute(text(f"DROP DATABASE IF EXISTS `{schema}`"))
        root_engine.dispose()


def fixture_profile(database_target):
    return parse_profile({
        "target": database_target, "devices": [{"equipmentId": "line", "nameZh": "线", "nameEn": "Line",
                    "futureToleranceSeconds": 300, "staleAfterSeconds": 3600}],
        "readScopes": {"admin": ["line"]}, "historyRules": [], "groupSettings": [],
        "producers": [{"producerId": "Line.A", "tokenSha256": sha256(b"obs010-legacy-fixture").hexdigest(),
            "kind": "external", "enabled": True, "energyGrants": [
                {"meterId": "meter2", "groupKey": "electricity", "metricKeys": ["activePower"]}],
            "grants": [{"equipmentId": "line", "groupKey": "heatZone1", "target": target, "metricKeys": ["actual"]}
                       for target in ("latest", "history")]}],
        "meters": [{"meterId": meter, "nameZh": meter, "nameEn": meter} for meter in ("meter1", "meter2")],
        "meterReadScopes": {"admin": ["meter1", "meter2"], "operator": ["meter1"]},
    })


def jwt_header(username):
    token = jwt.encode({"sub": username, "type": "access"}, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return {"Authorization": "Bearer " + token}


def query(engine, statement, **params):
    with engine.begin() as db:
        result = db.execute(text(statement), params)
        return result.all() if result.returns_rows else None


def snapshot(engine):
    return {table: query(engine, f"SELECT * FROM `{table}` ORDER BY 1,2") for table in PROTECTED}


def test_mysql_migration_batch_atomicity_replay_and_operational_compatibility(target, monkeypatch):
    from sqlalchemy.orm import Session
    from app.equipment_observation.models import MetricConfig, MetricGroup, SlotBinding, WriteSource

    engine, async_url, migrate, target_profile = target
    profile = fixture_profile(target_profile)
    monkeypatch.setattr(routes, "get_profile", lambda: profile)
    with Session(engine) as session:
        for username in ("admin", "operator"):
            session.add(User(username=username, password="isolated-fixture-not-a-login",
                             name=username, role=username, is_active=True))
        now = datetime(2026, 11, 24, 12)
        session.add(WriteSource(source_key="Line.A", storage_identity="obsreg_fixture", name="fixture",
                                enabled=True, created_at=now, updated_at=now))
        session.add(MetricGroup(group_key="heatZone1", category="temperature", name_zh="温区",
                               name_en="Heat zone", enabled=True, sort_order=0))
        session.add(MetricConfig(metric_key="actual", source_group_key="heatZone1", category="temperature",
                                name_zh="实测", name_en="Actual", value_type="number"))
        session.flush()
        for kind in ("latest", "history"):
            session.add(SlotBinding(target=kind, group_key="heatZone1", slot_no=1, metric_key="actual", enabled=True))
        metrics(session)

    async def run():
        async_engine = create_async_engine(async_url)
        state = {"commit_unknown": False}

        class FixtureSession(AsyncSession):
            async def commit(self):
                await super().commit()
                if state["commit_unknown"] and any(isinstance(obj, EnergyReceipt) for obj in self.identity_map.values()):
                    state["commit_unknown"] = False
                    raise RuntimeError("synthetic lost commit acknowledgment")

        sessions = async_sessionmaker(async_engine, class_=FixtureSession, expire_on_commit=False, autoflush=False)

        async def database():
            async with sessions() as db:
                yield db

        app = FastAPI()
        app.include_router(routes.router, prefix="/api/v1")
        app.dependency_overrides[get_db] = database
        app.state.role_api_permissions = {"operator": {"energy-consumption-read"}}
        admin, operator = jwt_header("admin"), jwt_header("operator")
        transport = httpx.ASGITransport(app=app)
        legacy = {"eventId": LEGACY_EVENT, "data": {"meterId": "meter2", "groupKey": "electricity",
                  "observedAt": STAMP, "quality": "good", "values": {"activePower": 1}}}
        obs = legacy_equipment(timestamp=STAMP)
        obs["data"]["groups"] = {"heatZone1": {"actual": 55}}
        legacy_observation_paths = ("/integration/equipment/latest-snapshots", "/integration/monitor/history-samples")
        try:
            async with httpx.AsyncClient(transport=transport, base_url="http://fixture/api/v1") as client:
                old = await client.post(LEGACY_ROUTE, headers=MACHINE, json=legacy)
                assert old.status_code == 200, old.text
                previous = []
                for path in legacy_observation_paths:
                    response = await client.post(path, headers=MACHINE, json=obs)
                    assert response.status_code == 200, response.text
                    previous.append(response.json())
                old_rows = snapshot(engine)
                code, log = migrate(REVISION, expected_server=str(uuid4()))
                assert code != 0 and "target mismatch" in log
                assert snapshot(engine) == old_rows
                code, log = migrate(REVISION)
                assert code == 0, log
                assert snapshot(engine) == old_rows
                assert (await client.get(MANAGE)).status_code == 401
                assert (await client.get(MANAGE, headers={"Authorization": "Bearer invalid"})).status_code == 401
                assert (await client.post(MANAGE, headers=operator, json={"sourceKey": "Line.A"})).status_code == 403
                assert (await client.post(MANAGE, headers=admin, json={"sourceKey": "Line.A"})).status_code == 200
                assert (await client.post(MANAGE, headers=admin, json={"sourceKey": "line.a"})).status_code == 200
                assert (await client.post(LEGACY_ROUTE, headers=MACHINE, json=legacy)).json() == old.json()
                request = batch()
                changed = deepcopy(request)
                changed["items"]["meter2"]["electricity"]["values"]["activePower"] = 2
                left, right = await asyncio.gather(client.post(WRITE, json=request), client.post(WRITE, json=request))
                assert left.status_code == right.status_code == 200, (left.text, right.text)
                assert left.json() == right.json()
                assert len(left.json()["data"]["records"]) == 2
                assert (await client.post(WRITE, json=changed)).status_code == 409
                assert query(engine, "SELECT contract_version, COUNT(*) FROM energy_ingest_receipts GROUP BY 1 ORDER BY 1") == [
                    ("aiis.energy-registered/v1", 1), ("aiis.metric-ingest/v2", 1)]
                for payload in (request, changed):
                    payload["observedAt"] = "2026-11-24T12:01:00+08:00"
                collided = await asyncio.gather(client.post(WRITE, json=request), client.post(WRITE, json=changed))
                assert sorted(result.status_code for result in collided) == [200, 409]

                # 已提交的非法历史导入标识被拒绝；合法 v2 同 sourceKey/eventId 不碰撞。
                query(engine, """INSERT INTO energy_ingest_receipts
                    (target,producer_id,event_id,request_digest,outcome,processed_at)
                    VALUES ('energy',:producer,'historical-invalid-import',UNHEX(REPEAT('00',32)),'stored',NOW(6))""",
                    producer=storage_identity("old-import"))
                assert (await client.post(MANAGE, headers=admin, json={"sourceKey": "old-import"})).status_code == 409

                request["observedAt"] = "2026-11-24T12:02:00+08:00"
                new_legacy = deepcopy(legacy)
                new_legacy["eventId"] = "energyreg1_2026-11-24T12:02:00.000000+08:00"
                new_legacy["data"]["observedAt"] = request["observedAt"]
                results = await asyncio.gather(client.post(WRITE, json=request),
                    client.post(LEGACY_ROUTE, headers=MACHINE, json=new_legacy))
                assert [result.status_code for result in results] == [200, 200], [r.text for r in results]

                request["observedAt"] = "2026-11-24T12:03:00+08:00"
                baseline = snapshot(engine)
                query(engine, """CREATE TRIGGER obs010_fail_second BEFORE INSERT ON energy_consumption_main
                    FOR EACH ROW BEGIN IF NEW.meter_id = 'meter2' THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'OBS010 isolated second insert failure'; END IF; END""")
                assert (await client.post(WRITE, json=request)).status_code == 503
                assert snapshot(engine) == baseline
                query(engine, "DROP TRIGGER obs010_fail_second")
                state["commit_unknown"] = True
                uncertain = await client.post(WRITE, json=request)
                assert uncertain.status_code == 503 and uncertain.json()["errorCode"] == "equipment_observation.commit_unknown"
                replay = await client.post(WRITE, json=request)
                assert replay.status_code == 200 and len(replay.json()["data"]["records"]) == 2
                assert (await client.post(WRITE, json=request)).json() == replay.json()

                for remove in (False, True):
                    request["observedAt"] = f"2026-11-24T12:0{5 if remove else 4}:00+08:00"
                    change = client.delete(MANAGE + "/Line.A", headers=admin) if remove else client.patch(
                        MANAGE + "/Line.A", headers=admin, json={"enabled": False})
                    write, stopped = await asyncio.gather(client.post(WRITE, json=request), change)
                    assert write.status_code in (200, 403) and stopped.status_code == 200
                    if write.status_code == 200:
                        receipt_id = int(write.json()["data"]["receiptId"])
                        assert query(engine, "SELECT COUNT(*) FROM energy_consumption_main WHERE ingest_receipt_id=:id", id=receipt_id) == [(2,)]
                    assert (await client.post(WRITE, json=request)).status_code == 403
                    if not remove:
                        assert (await client.patch(MANAGE + "/Line.A", headers=admin, json={"enabled": True})).status_code == 200

                code, log = migrate(SUCCESSOR)
                assert code == 0, log
                assert target_profile["schemaRevision"] == "e9f3b5d7c021"
                assert (await client.get(MANAGE, headers=admin)).status_code == 200
                assert (await client.get("/energy/consumption/samples", headers=operator, params={"meterId":"meter2"})).status_code == 403
                assert (await client.get("/energy/consumption/samples", headers=operator, params={"meterId":"meter1"})).status_code == 200
                assert (await client.get("/integration/energy/metric-definitions", headers=MACHINE,
                                         params={"meterId":"meter2","groupKey":"electricity"})).status_code == 200
                assert (await client.post(LEGACY_ROUTE, headers=MACHINE, json=legacy)).json() == old.json()
                request["sourceKey"] = "line.a"
                assert (await client.post(WRITE, json=request)).status_code == 200
                for path, expected in zip(legacy_observation_paths, previous):
                    assert (await client.post(path, headers=MACHINE, json=obs)).json() == expected
                baseline = snapshot(engine)
                code, log = migrate(PREDECESSOR, "downgrade")
                assert code != 0 and "retain energy registrations" in log
                assert snapshot(engine) == baseline
                assert len(query(engine, "SELECT * FROM energy_write_sources")) == 2

                # 设备来源登记消失对能耗无影响，实际能耗结构消失才失败。
                query(engine, "RENAME TABLE observation_write_sources TO obs010_hidden_registry")
                assert (await client.get(MANAGE, headers=admin)).status_code == 200
                assert (await client.post(WRITE, json=request)).status_code == 200
                query(engine, "RENAME TABLE energy_metric_configs TO obs010_hidden_energy_metrics")
                failed = await client.get("/energy/metric-configs", headers=admin)
                assert failed.status_code == 503 and failed.json()["errorCode"] == "equipment_observation.not_ready"
        finally:
            await async_engine.dispose()

    asyncio.run(run())
