"""写入登记的公开请求、规范回执向量和身份边界回归。"""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.equipment_observation.api.routes import router
from app.equipment_observation.domain import ObservationError
from app.equipment_observation.services.registered_ingest import normalize
from app.equipment_observation.services.write_sources import source_key, storage_identity
from common.integration.http import strict_json

pytestmark = pytest.mark.no_db
CONTRACT = Path(__file__).resolve().parents[2] / "contracts/published/http-api/observation-write-sources-v1"


def request():
    return {"sourceKey": "SMA.1", "target": "history", "taskNo": " some-task ",
            "observedAt": "2026-11-20T03:04:05.123456Z", "items": {"area": {"number": 0, "enabled": False, "text": ""}}}


def test_published_digest_and_equivalent_replay():
    vector = json.loads((CONTRACT / "vectors.json").read_text())
    original = strict_json(json.dumps(vector["request"]).encode())
    replay = strict_json(vector["equivalentReplayJson"].encode())
    normalized, _, digest, event = normalize(original)
    expected = vector["internalTestExpectations"]
    assert normalize(replay)[2:] == (digest, event)
    assert expected == {"eventId": event, "requestDigestSha256": digest.hex(),
                        "storageIdentity": storage_identity(original["sourceKey"])}
    assert normalized["taskNo"] == vector["normalizedTaskNo"]
    assert normalized["observedAt"] == vector["normalizedTimestamp"]
    for key, other in (("sourceKey", "SMA.2"), ("target", "latest"), ("taskNo", "X"),
                       ("observedAt", "2026-11-20T06:30:00.000001Z")):
        assert normalize({**original, key: other})[3] != event
    change = deepcopy(original)
    change["items"]["heatZone1"]["zone1Actual"] = 0
    assert normalize(change)[2] != digest and normalize(change)[3] == event


@pytest.mark.parametrize("key", (".", "..", "sma-1", "SMA-1", "_" * 64))
def test_source_keys_preserve_case_and_derive_fixed_width_identity(key):
    assert source_key(key) == key
    assert storage_identity(key).startswith("obsreg_")
    assert len(storage_identity(key)) == 64
    if key.lower() != key:
        assert storage_identity(key.lower()) != storage_identity(key)


@pytest.mark.parametrize("key", ("", " A", "a\n", "a/b", "名", "_" * 65))
def test_reject_invalid_source_keys(key):
    with pytest.raises(ObservationError, match="invalid_request"):
        source_key(key)


def test_false_and_empty_values_survive_normalization():
    doc = request()
    doc["items"]["second"] = {}
    normalized, _, _, _ = normalize(doc)
    assert normalized["observedAt"] == "2026-11-20T11:04:05.123456+08:00"
    assert normalized["items"] == {"area": {"number": 0, "enabled": False, "text": ""}, "second": {}}


@pytest.mark.parametrize("changes", (
    {"observedAt": "2026-11-20T11:04:05"}, {"observedAt": "2026-11-20T11:04:05+07:60"},
    {"observedAt": "2026-11-20T03:04:05.1234561Z"}, {"taskNo": "ß"}, {"target": "energy"},
    {"items": {}}, {"items": {"area": {}}}, {"items": {"area": {"k": None}}},
    {"items": {"area": {"k": []}}}, {"items": {"area": {"k": 10 ** 400}}}, {"quality": "good"},
))
def test_invalid_base_shape_or_scalar_is_rejected(changes):
    with pytest.raises(ObservationError) as failure:
        normalize({**request(), **changes})
    assert failure.value.status == 422


def test_live_and_published_anonymous_operations_have_no_auth_requirement():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    contract = json.loads((CONTRACT / "openapi.json").read_text())
    base = "/api/v1/integration/observations"
    paths = app.openapi()["paths"]
    for operation, url in (("post", base), ("get", base + "/latest")):
        assert not paths[url][operation].get("security")
        assert contract["paths"][url][operation]["security"] == []
    route = "/api/v1/equipment/write-sources/{sourceKey}"
    assert [paths[route][method]["parameters"][0]["name"] for method in ("patch", "delete")] == ["sourceKey", "sourceKey"]
    assert paths[base]["post"]["requestBody"] == contract["paths"][base]["post"]["requestBody"]
    client = TestClient(app)
    response = client.get(base + "/latest", params={"sourceKey": "a", "target": "energy"})
    assert response.status_code == 422 and response.json()["errorCode"] == "equipment_observation.invalid_request"
    response = client.post(base, content=b"{}", headers={"content-type": "text/plain"})
    assert response.status_code == 415 and response.json()["errorCode"] == "equipment_observation.media_type"
    response = client.post(base, content=b"x" * 65537, headers={"content-type": "application/json"})
    assert response.status_code == 413 and response.json()["errorCode"] == "equipment_observation.payload_too_large"


@pytest.mark.asyncio
@pytest.mark.parametrize("duplicate", (True, False))
async def test_source_registration_conflict_rolls_back_flushed_row(monkeypatch, duplicate):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, Mock
    from sqlalchemy.exc import IntegrityError
    from app.equipment_observation.services import write_sources

    _, now, _, _ = normalize(request())
    monkeypatch.setattr(write_sources, "current_clock", AsyncMock(return_value=now))
    db = SimpleNamespace(add=Mock(), flush=AsyncMock(), rollback=AsyncMock(), commit=AsyncMock(),
                         execute=AsyncMock(return_value=SimpleNamespace(first=lambda: (1,))))
    if duplicate:
        db.flush.side_effect = IntegrityError("insert", (), Exception("duplicate identity"))
    with pytest.raises(ObservationError, match="configuration_conflict") as failure:
        await write_sources.create(db, {"target": {}}, "Source", None, True)
    assert failure.value.status == 409
    db.rollback.assert_awaited_once()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("changes, delete, expected", (
    ({"name": "Existing"}, False, ("Existing", True, False)),
    ({"enabled": True}, False, ("Existing", True, False)),
    ({"name": "Existing", "enabled": True}, False, ("Existing", True, False)),
    ({"name": "Renamed"}, False, ("Renamed", True, True)),
    ({"name": "Existing", "enabled": False}, False, ("Existing", False, True)),
    ({"name": None}, False, (None, True, True)),
    ({}, True, ("Existing", False, True)),
))
async def test_source_change_updates_timestamp_only_on_mutation(monkeypatch, changes, delete, expected):
    from datetime import timedelta
    from types import SimpleNamespace
    from unittest.mock import AsyncMock
    from app.equipment_observation.services import write_sources

    _, created, _, _ = normalize(request())
    previous = created + timedelta(seconds=1)
    now = previous + timedelta(seconds=1)
    row = SimpleNamespace(source_key="Source", name="Existing", enabled=True,
                          created_at=created, updated_at=previous, deleted_at=None)
    lookup = AsyncMock(return_value=row)
    clock = AsyncMock(return_value=now)
    db = SimpleNamespace(flush=AsyncMock(), rollback=AsyncMock(), commit=AsyncMock())
    monkeypatch.setattr(write_sources, "source_row", lookup)
    monkeypatch.setattr(write_sources, "current_clock", clock)

    result = await write_sources.change(db, {"target": {}}, "Source", changes, delete=delete)

    name, enabled, mutated = expected
    assert (row.name, row.enabled, row.created_at) == (name, enabled, created)
    lookup.assert_awaited_once_with(db, "Source", lock=True)
    assert row.updated_at == (now if mutated else previous)
    assert row.deleted_at == (now if delete else None)
    assert result == ({"sourceKey": "Source", "deleted": True} if delete else write_sources.data(row))
    assert (clock.await_count, db.flush.await_count, db.commit.await_count, db.rollback.await_count) == (
        int(mutated), int(mutated), int(mutated), int(not mutated),
    )
