"""质量结果与配置合同、隔离 SQLite 迁移和实际 HTTP 验证。"""
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.quality.models import QualityDefectRecord, QualityInspection, QualitySPCMeasurement
from core.deps import get_current_user
from core.registrar import create_app
from database import Base, get_db

pytestmark = pytest.mark.no_db
BEFORE = "e9f3b5d7c021"
AFTER = "f0a2b4c6d8e1"
PREFIX = "/api/v1"
PUB = PREFIX + "/integration/quality"
WEB = PREFIX + "/quality"
CONFIG = WEB + "/field-config"


def migrate(connection, destination, *, stamp=False):
    backend = Path(__file__).resolve().parents[1]
    config = Config(str(backend / "alembic.ini"))
    config.set_main_option("script_location", str(backend / "alembic"))
    scripts = ScriptDirectory.from_config(config)
    if stamp:
        MigrationContext.configure(connection).stamp(scripts, destination)
        return
    assert scripts.get_revision(AFTER).down_revision == BEFORE
    with EnvironmentContext(config, scripts, fn=lambda rev, _: scripts._upgrade_revs(destination, rev)) as env:
        env.configure(connection=connection)
        env.run_migrations()


class SQLiteSession:
    """通过项目 SQLAlchemy Session 对接 AsyncSession 接口，无额外驱动依赖。"""

    def __init__(self, session):
        self.session = session

    def get_bind(self):
        return self.session.get_bind()

    def add(self, row):
        self.session.add(row)

    async def execute(self, statement):
        return self.session.execute(statement)

    async def flush(self):
        self.session.flush()

    async def commit(self):
        self.session.commit()


@pytest.fixture
def built(tmp_path, monkeypatch):
    path = tmp_path / "quality.sqlite3"
    engine = create_engine(f"sqlite:///{path}")
    with engine.begin() as connection:
        migrate(connection, BEFORE, stamp=True)
        Base.metadata.create_all(connection, tables=[
            QualityInspection.__table__, QualityDefectRecord.__table__, QualitySPCMeasurement.__table__,
        ])
        connection.execute(QualityInspection.__table__.insert().values(coil_no="PRESERVED"))
        connection.execute(QualityDefectRecord.__table__.insert().values(inspection_id=1, defect_type="synthetic"))
        connection.execute(QualitySPCMeasurement.__table__.insert().values(
            coil_no="PRESERVED", item="thickness", value=1.2, is_normal=True,
        ))
    with pytest.raises(RuntimeError, match="explicit SQLite fixture"):
        with engine.begin() as connection:
            migrate(connection, AFTER)
    monkeypatch.setenv("QUALITY_EXPECTED_SQLITE_PATH", str(path))
    for _ in range(2):
        with engine.begin() as connection:
            migrate(connection, AFTER)
    with engine.begin() as connection:
        assert connection.execute(text("SELECT coil_no FROM quality_inspections")).scalar_one() == "PRESERVED"
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == AFTER
        assert connection.execute(text("SELECT revision FROM quality_field_config")).scalar_one() == 1
        assert connection.execute(text("SELECT created_at FROM quality_field_config")).scalar_one().endswith("+08:00")
        assert inspect(connection).get_foreign_keys("quality_main") == []
        assert inspect(connection).get_foreign_keys("quality_field_config") == []

    async def get_fixture_db():
        with Session(engine, expire_on_commit=False, autoflush=False) as session:
            try:
                yield SQLiteSession(session)
            finally:
                session.rollback()

    def user():
        if identity.role is None:
            raise HTTPException(status_code=401, detail="not authenticated")
        return SimpleNamespace(id=7, role=identity.role, username="fixture")

    identity = SimpleNamespace(role="admin")
    app = create_app(testing=True)
    app.dependency_overrides[get_db] = get_fixture_db
    app.dependency_overrides[get_current_user] = user
    app.state.role_api_permissions = {"supervisor": ("quality",), "operator": ("quality",)}
    yield engine, app, identity
    engine.dispose()


@pytest.fixture
async def client(built):
    engine, app, identity = built
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://fixture",
                           headers={"Authorization": "Bearer synthetic"}) as http:
        yield http, engine, identity


def data(response, status=200):
    assert response.status_code == status, response.text
    body = response.json()
    assert set(body) == {"code", "message", "data", "timestamp"}
    assert body["code"] == 200
    return body["data"]


def rejects(response, status, code):
    assert response.status_code == status, response.text
    assert response.json()["errorCode"] == "quality." + code, response.text


def definition(name, kind, **kwargs):
    return {"name": name, "type": kind, "labels": {"zh-CN": name, "en-US": name}, **kwargs}


async def add_fields(http):
    fields = [
        definition("sample_no", "string", editable=True, visible=False),
        definition("defects", "number", isNullable=False),
        definition("reviewed", "boolean", editable=True),
        definition("reportUrl", "link", linkText="下载"),
    ]
    return data(await http.put(CONFIG, json={"revision": 1, "definitions": fields}))


@pytest.mark.asyncio
async def test_upsert_partial_filters_projection_and_role_permissions(client):
    http, engine, identity = client
    fields = await add_fields(http)
    assert fields["revision"] == 2
    assert data(await http.put(CONFIG, json=fields))["revision"] == 2
    rejects(await http.get(PUB + "/by-task/abc"), 404, "not_found")
    assert data(await http.post(PUB + "/upsert", json={"taskNo": " empty01 "}))["outcome"] == "created"
    original = {"taskNo": " abc.1 ", "items": {
        "sample_no": "", "defects": 0, "reviewed": False, "reportUrl": "https://example.com/a",
    }}
    created = data(await http.post(PUB + "/upsert", json=original))
    quality = created["quality"]
    assert created["outcome"] == "created"
    assert quality["taskNo"] == "ABC.1" and quality["targetKey"] is None
    assert quality["items"] == original["items"]
    assert quality["createdAt"].endswith("+08:00")
    assert data(await http.post(PUB + "/upsert", json=original)) == {
        "outcome": "unchanged", "quality": quality,
    }

    changed = data(await http.post(PUB + "/upsert", json={
        "taskNo": "ABC.1", "targetKey": "LINE-a", "items": {"defects": 12.1234},
    }))["quality"]
    assert changed["items"] == {**original["items"], "defects": 12.1234}
    for target in (None, "LINE-b"):
        rejects(await http.post(PUB + "/upsert", json={"taskNo": "ABC.1", "targetKey": target}),
                409, "target_conflict")
    assert len(data(await http.get(PUB, params={"targetKey": "LINE-a"}))["items"]) == 1
    assert data(await http.get(PUB, params={"targetKey": "LINE-A"}))["total"] == 0
    first = data(await http.get(PUB, params={"pageSize": 1}))
    assert first["totalPages"] == 2 and first["items"][0]["taskNo"] == "ABC.1"
    assert data(await http.get(PUB, params={"createdFrom": changed["createdAt"]}))["total"] == 1
    assert data(await http.get(PUB, params={"createdTo": changed["createdAt"]}))["total"] == 1
    assert data(await http.get(PUB, params={"createdFrom": "2026-01-01T12:00:00Z"}))["total"] == 2
    rejects(await http.get(PUB, params={"createdFrom": "2026-01-01T12:00:00"}), 422, "invalid_request")
    assert data(await http.get(PUB + "/field-config"))["revision"] == 2

    identity.role = "operator"
    rejects(await http.get(CONFIG), 403, "forbidden")
    rejects(await http.put(CONFIG, json=fields), 403, "forbidden")
    assert len(data(await http.get(WEB + "/results"))["fields"]) == 4
    rejects(await http.post(WEB + "/results/upsert", json={"taskNo": "abc.1", "items": {"defects": 1}}),
            403, "forbidden")
    rejects(await http.post(WEB + "/results/upsert", json={"taskNo": "absent", "items": {"reviewed": True}}),
            404, "not_found")
    assert data(await http.post(WEB + "/results/upsert", json={
        "taskNo": "abc.1", "items": {"reviewed": True, "sample_no": None},
    }))["quality"]["items"]["sample_no"] is None
    identity.role = "supervisor"
    assert data(await http.post(WEB + "/results/upsert", json={
        "taskNo": "abc.1", "items": {"reviewed": False},
    }))["outcome"] == "updated"
    identity.role = "guest"
    rejects(await http.get(WEB + "/results"), 403, "forbidden")
    identity.role = None
    rejects(await http.get(WEB + "/results"), 401, "unauthenticated")
    assert data(await http.get(PUB + "/by-task/abc.1"))["items"]["reviewed"] is False

    with engine.connect() as connection:
        assert connection.execute(text("SELECT updated_at FROM quality_main WHERE task_no='ABC.1'")).scalar_one().endswith("+08:00")


@pytest.mark.asyncio
async def test_manual_create_validates_fields_and_never_overwrites_existing_results(client):
    http, engine, identity = client
    create = WEB + "/results"
    assert data(await http.post(create, json={"taskNo": " empty-user "}), 201)["outcome"] == "created"
    config = data(await http.put(CONFIG, json={"revision": 1, "definitions": [
        definition("sample_no", "string", editable=True, visible=False),
        definition("defects", "number", editable=True, isNullable=False),
        definition("reviewed", "boolean", editable=True),
        definition("reportUrl", "link", editable=True),
        definition("automatic", "string"),
        definition("disabled", "string", enabled=False, editable=True),
    ]}))
    body = {"taskNo": " manual.1 ", "targetKey": "Line-a", "items": {
        "sample_no": "", "defects": 0, "reviewed": False, "reportUrl": "https://example.com/report",
    }}
    identity.role = "operator"
    result = data(await http.post(create, json=body), 201)["quality"]
    assert result["taskNo"] == "MANUAL.1" and result["targetKey"] == "Line-a"
    assert result["items"] == {**body["items"], "automatic": None}
    assert result["createdAt"] == result["updatedAt"] and result["updatedAt"].endswith("+08:00")
    assert data(await http.get(WEB + "/results", params={"taskNo": "manual.1"}))["items"] == [result]
    rejects(await http.post(create, json={"taskNo": "MANUAL.1", "items": {"defects": 4}}),
            409, "task_no_conflict")
    assert data(await http.get(PUB + "/by-task/manual.1")) == result

    for items, status, error in (
        ({"sample_no": "no write", "automatic": "private"}, 403, "forbidden"),
        ({"unknown": "bad"}, 422, "invalid_request"),
        ({"disabled": "bad"}, 422, "invalid_request"),
        ({"reportUrl": "/bad"}, 422, "invalid_request"),
        ({"defects": None}, 422, "invalid_request"),
        ({"reviewed": 0}, 422, "invalid_request"),
    ):
        rejects(await http.post(create, json={"taskNo": "invalid", "items": items}), status, error)
        rejects(await http.get(PUB + "/by-task/invalid"), 404, "not_found")
    identity.role = "guest"
    rejects(await http.post(create, json={"taskNo": "denied"}), 403, "forbidden")
    identity.role = None
    rejects(await http.post(create, json={"taskNo": "denied"}), 401, "unauthenticated")
    identity.role = "admin"
    config["definitions"] = [{**field, "enabled": False} if field["name"] == "reportUrl" else field
                             for field in config["definitions"]]
    data(await http.put(CONFIG, json=config))
    identity.role = "supervisor"
    rejects(await http.post(create, json={"taskNo": "config-race", "items": {"reportUrl": body["items"]["reportUrl"]}}),
            422, "invalid_request")
    assert data(await http.post(create, json={"taskNo": "supervisor"}), 201)["outcome"] == "created"
    rejects(await http.post(PUB + "/upsert", json={"taskNo": "manual.1", "targetKey": "line-a"}),
            409, "target_conflict")
    updated = data(await http.post(PUB + "/upsert", json={"taskNo": "manual.1", "items": {"automatic": "FF"}}))
    assert updated["quality"]["items"] == {"sample_no": "", "defects": 0, "reviewed": False, "automatic": "FF"}
    with engine.connect() as connection:
        assert connection.execute(text("SELECT JSON_EXTRACT(items, '$.reportUrl') FROM quality_main "
                                       "WHERE task_no='MANUAL.1'")).scalar_one() == body["items"]["reportUrl"]


@pytest.mark.asyncio
async def test_manual_create_unknown_commit_is_reported_for_readback(client, monkeypatch):
    http, _, _ = client

    async def lose_commit_reply(self):
        self.session.commit()
        raise SQLAlchemyError("synthetic commit response lost")

    monkeypatch.setattr(SQLiteSession, "commit", lose_commit_reply)
    body = {"taskNo": "unknown-commit"}
    rejects(await http.post(WEB + "/results", json=body), 503, "commit_unknown")
    assert data(await http.get(PUB + "/by-task/unknown-commit"))["taskNo"] == "UNKNOWN-COMMIT"
    rejects(await http.post(WEB + "/results", json=body), 409, "task_no_conflict")


@pytest.mark.asyncio
async def test_validation_is_atomic_and_disabled_values_are_preserved(client):
    http, _, _ = client
    config = await add_fields(http)
    url = "https://example.com/inspection"
    body = {"taskNo": "XYZ01", "items": {"reportUrl": url, "defects": 0}}
    data(await http.post(PUB + "/upsert", json=body))
    for items in (
        {"unknown": 1}, {"Sample_no": "A"}, {"reportUrl": "//example.com"},
        {"reportUrl": "javascript:alert(1)"}, {"reportUrl": "https://u:p@example.com"},
        {"reportUrl": "https://example.com/a b"}, {"reportUrl": "https://example.com/\u0000"},
        {"reportUrl": "https://example.com/" + "x" * 2048}, {"defects": True},
        {"defects": "12"}, {"defects": 10**10}, {"defects": 0.12345},
        {"reviewed": 0}, {"sample_no": "a" * 256}, {"defects": None},
        {"defects": 7, "reportUrl": "/bad"},
    ):
        rejects(await http.post(PUB + "/upsert", json={"taskNo": "xyz01", "items": items}),
                422, "invalid_request")
    # The JSON token carries more significant decimal places than a binary float preserves.
    rejects(await http.post(PUB + "/upsert", headers={"Content-Type": "application/json"},
                            content='{"taskNo":"xyz01","items":{"defects":1.000000000000000000000001}}'),
            422, "invalid_request")
    rejects(await http.post(PUB + "/upsert", json={"taskNo": 123}), 422, "invalid_request")
    assert data(await http.get(PUB + "/by-task/xyz01"))["items"]["defects"] == 0

    definitions = config["definitions"]
    _, link, *_ = sorted(definitions, key=lambda field: field["name"])
    assert link["name"] == "reportUrl"
    link["enabled"] = False
    link["linkText"] = "  "
    disabled = data(await http.put(CONFIG, json=config))
    assert "reportUrl" not in data(await http.get(PUB + "/by-task/xyz01"))["items"]
    assert len(data(await http.get(PUB + "/field-config"))["definitions"]) == 3
    rejects(await http.post(PUB + "/upsert", json=body), 422, "invalid_request")
    rejects(await http.put(CONFIG, json=config), 409, "config_revision_conflict")

    link = next(field for field in disabled["definitions"] if field["name"] == "reportUrl")
    assert link["linkText"] is None
    for definitions in (
        [field for field in disabled["definitions"] if field != link],
        [*disabled["definitions"], link],
        [{**field, "type": "string"} if field == link else field for field in disabled["definitions"]],
    ):
        rejects(await http.put(CONFIG, json={**disabled, "definitions": definitions}),
                422, "invalid_request")
    link["enabled"] = True
    data(await http.put(CONFIG, json=disabled))
    assert data(await http.get(PUB + "/by-task/xyz01"))["items"]["reportUrl"] == url


@pytest.mark.asyncio
async def test_sqlite_concurrent_partial_updates_do_not_lose_fields(client, built):
    http, _, _ = client
    await add_fields(http)
    _, app, _ = built

    def separate_connection(items, *, task_no="parallel", path=PUB + "/upsert"):
        async def send():
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://fixture",
                                   headers={"Authorization": "Bearer synthetic"}) as call:
                return await call.post(path, json={"taskNo": task_no, "items": items})
        return asyncio.run(send())

    responses = await asyncio.gather(
        asyncio.to_thread(separate_connection, {"defects": 0}),
        asyncio.to_thread(separate_connection, {"reviewed": False}),
    )
    assert {data(reply)["outcome"] for reply in responses} == {"created", "updated"}
    assert data(await http.get(PUB + "/by-task/parallel"))["items"] == {
        "defects": 0, "reportUrl": None, "reviewed": False, "sample_no": None,
    }
    responses = await asyncio.gather(*[
        asyncio.to_thread(separate_connection, {"sample_no": item}, task_no=task, path=WEB + "/results")
        for task, item in [(" private-same ", "A"), ("PRIVATE-SAME", "B")]
    ])
    assert sorted(response.status_code for response in responses) == [201, 409]
    winner = next(response for response in responses if response.status_code == 201)
    rejected = next(response for response in responses if response.status_code == 409)
    rejects(rejected, 409, "task_no_conflict")
    assert data(await http.get(PUB + "/by-task/private-same")) == data(winner, 201)["quality"]


@pytest.mark.asyncio
async def test_legacy_quality_routes_retire_without_changing_old_storage_or_spc(client):
    http, engine, _ = client
    retired = [("GET", WEB), ("POST", WEB), ("GET", WEB + "/1"), ("PUT", WEB + "/1"),
               ("DELETE", WEB + "/1"), ("POST", WEB + "/1/defects"), ("DELETE", WEB + "/1/defects/1"),
               ("GET", PREFIX + "/defects")]
    for method, path in retired:
        assert (await http.request(method, path, json={})).status_code == 404
    spc = data(await http.get(WEB + "/spc/data", params={"item": "thickness"}))
    assert len(spc) == 1 and spc[0]["coilNo"] == "PRESERVED"
    assert (await http.get(WEB + "/spc/stats", params={"item": "thickness"})).status_code == 200
    assert data(await http.get(WEB + "/results"))["total"] == 0
    data(await http.post(PUB + "/upsert", json={"taskNo": "PRESERVED", "items": {}}))
    assert data(await http.get(WEB + "/results"))["total"] == 1
    with engine.connect() as connection:
        assert connection.execute(text("SELECT coil_no FROM quality_inspections")).scalar_one() == "PRESERVED"
        assert connection.execute(text("SELECT inspection_id, defect_type FROM quality_defect_records")).one() == (1, "synthetic")
        assert connection.execute(text("SELECT count(*) FROM quality_spc_measurements")).scalar_one() == 1


@pytest.mark.asyncio
async def test_published_contract_matches_routes_and_examples(client):
    http, _, _ = client
    contract = Path(__file__).resolve().parents[2] / "contracts/published/http-api/quality-results-v1"
    published = json.loads((contract / "openapi.json").read_text())
    source = (await http.get("/openapi.json")).json()
    assert len(published["paths"]) == 8
    assert sum(map(len, published["paths"].values())) == 10
    for path, item in published["paths"].items():
        assert item == source["paths"][path]
    for category, entries in published["components"].items():
        assert all(schema == source["components"][category][key] for key, schema in entries.items())
    for request in json.loads((contract / "examples/requests.json").read_text())["requests"]:
        response = await http.request(request["method"], request["path"], params=request.get("query"), json=request.get("body"))
        data(response, request.get("expectedStatus", 200))
