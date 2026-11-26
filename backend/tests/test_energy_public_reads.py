"""在隔离 SQLite HTTP 夹具验证 ARCH-ENERGY-003 筛选与回包合同。"""
from datetime import datetime
import json
from pathlib import Path

from fastapi import FastAPI
import pytest

from app.equipment_observation.api.routes import router
from app.equipment_observation.models import EnergyMetric, EnergyReceipt, EnergySample
from app.equipment_observation.services import energy_public_reads
from tests.test_energy_registered_ingest import client_for
from tests.test_equipment_observation_r10_flow import app_and_db  # noqa: F401

pytestmark = pytest.mark.no_db
LATEST = "/integration/energy/latest"
HISTORY = "/integration/energy/samples"
HISTORY_QUERY = {"meterId": "meter-02", "groupKey": "electricity",
                 "from": "2026-11-24T04:00:00Z", "to": "2026-11-24T13:00:00+08:00"}
STAMP = datetime(2026, 11, 24, 12)
CONTRACT = Path(__file__).resolve().parents[2] / "contracts/published/http-api/energy-public-reads-v1"


def metric(meter, group, key, slot, enabled=True, mode="instantaneous"):
    return EnergyMetric(meter_id=meter, group_key=group, metric_key=key, slot_no=slot,
                        name_zh=key, name_en=key, value_type="number", quantity_key="energy",
                        measurement_mode=mode, unit="kW", enabled=enabled, rules={})


def seed_samples(session):
    session.add_all([
        metric("meter-01", "electricity", "intervalEnergy", 1, mode="interval"),
        metric("meter-02", "electricity", "totalEnergy", 1, False, "cumulative"),
        metric("meter-02", "electricity", "activePower", 2),
        metric("meter-02", "thermal", "temperature", 1),
        metric("Meter-02", "electricity", "caseValue", 1),
    ])
    receipt = EnergyReceipt(target="energy", producer_id="read-fixture", event_id="existing-samples",
                            request_digest=bytes(32), outcome="stored", processed_at=STAMP,
                            contract_version="aiis.metric-ingest/v2", result_version="r10")
    session.add(receipt)
    session.flush()
    samples = [
        ("meter-01", "electricity", 12, "good", {"01": 120}),
        ("meter-02", "electricity", 13, "good", {"02": 21.5}),
        ("meter-02", "electricity", 13, "bad", {"02": 0}),
        ("meter-02", "electricity", 12, "good", {"01": 9820, "02": 21.3, "03": 999}),
        ("meter-02", "thermal", 12, "unknown", {"01": 55}),
        ("Meter-02", "electricity", 12, "good", {"01": 6}),
        ("historical-unconfigured", "thermal", 11, "unknown", {"01": 88}),
    ]
    for meter, group, hour, quality, values in samples:
        interval = meter == "meter-01"
        session.add(EnergySample(meter_id=meter, group_key=group, observed_at=STAMP.replace(hour=hour),
                                 quality=quality, local_values=values, ingest_receipt_id=receipt.id,
                                 interval_start_at=STAMP.replace(hour=11) if interval else None,
                                 interval_end_at=STAMP if interval else None,
                                 remark="private-fixture", review_mark="reviewed", created_at=STAMP, updated_at=STAMP))
        session.flush()
    session.commit()


def pairs(items):
    return [(item["meterId"], item["groupKey"]) for item in items]


async def data(client, path, params=None, **kwargs):
    response = await client.get(path, params=params, **kwargs)
    assert response.status_code == 200, response.text
    envelope = response.json()
    assert set(envelope) == {"code", "message", "data"}
    assert envelope["code"] == 200 and envelope["message"] == "success"
    return envelope["data"]


async def check_latest(client):
    full = (await data(client, LATEST))["items"]
    assert pairs(full) == [("Meter-02", "electricity"), ("historical-unconfigured", "thermal"),
                           ("meter-01", "electricity"), ("meter-02", "electricity"), ("meter-02", "thermal")]
    original, *_ = (await data(client, LATEST, {"meterId": "meter-02"}))["items"]
    assert original == {"meterId": "meter-02", "groupKey": "electricity", "quality": "bad",
                        "observedAt": "2026-11-24T13:00:00.000000+08:00", "values": {"activePower": 0}}
    assert (await data(client, LATEST, {"meterId": "meter-02"}))["items"] == full[3:]
    assert (await data(client, LATEST, {"groupKey": "electricity"}))["items"] == [full[0], full[2], full[3]]
    assert (await data(client, LATEST, {"meterId": "meter-02", "groupKey": "electricity"})) == {"items": [original]}
    assert (await data(client, LATEST, {"meterId": "METER-02"})) == {"items": []}
    assert full[1]["values"] == {} and full[1]["quality"] == "unknown"
    assert full[2]["intervalStartAt"] == "2026-11-24T11:00:00.000000+08:00"
    assert full[2]["intervalEndAt"] == "2026-11-24T12:00:00.000000+08:00"
    assert (await data(client, LATEST, headers={"Authorization": "Bearer invalid"})) == {"items": full}


async def check_history(client):
    result = await data(client, HISTORY, HISTORY_QUERY)
    assert {key: value for key, value in result.items() if key != "items"} == {
        "page": 1, "pageSize": 20, "total": 3, "totalPages": 1,
    }
    assert [item["values"] for item in result["items"]] == [
        {"activePower": 0}, {"activePower": 21.5}, {"totalEnergy": 9820, "activePower": 21.3},
    ]
    assert (await data(client, HISTORY, HISTORY_QUERY, headers={"Authorization": "malformed"})) == result
    assert (await data(client, HISTORY, {**HISTORY_QUERY, "page": 2, "pageSize": 2})) == {
        "items": result["items"][2:], "page": 2, "pageSize": 2, "total": 3, "totalPages": 2,
    }
    for page in (3, 10**30):
        out_of_range = await data(client, HISTORY, {**HISTORY_QUERY, "page": page})
        assert out_of_range == {"items": [], "page": page, "pageSize": 20, "total": 3, "totalPages": 1}
    coincident = await data(client, HISTORY, {**HISTORY_QUERY, "from": HISTORY_QUERY["to"]})
    assert coincident["items"] == result["items"][:2]
    assert (await data(client, HISTORY, {key: value for key, value in HISTORY_QUERY.items() if key != "groupKey"}))["total"] == 4
    assert (await data(client, HISTORY, {**HISTORY_QUERY, "groupKey": "unknown"})) == {
        "items": [], "page": 1, "pageSize": 20, "total": 0, "totalPages": 0,
    }


@pytest.mark.asyncio
async def test_public_read_filters_and_values(app_and_db, monkeypatch):
    app, session, _, _ = app_and_db

    async def fixture_target(_db, _target):
        pass

    monkeypatch.setattr(energy_public_reads, "verify_energy_target", fixture_target)
    seed_samples(session)
    async with client_for(app) as client:
        await check_latest(client)
        await check_history(client)


@pytest.mark.asyncio
async def test_public_query_validation_uses_observation_envelope(app_and_db):
    app, *_ = app_and_db
    async with client_for(app) as client:
        for params in ({"meterId": ""}, {"meterId": " "}, {"groupKey": "a" * 65}):
            response = await client.get(LATEST, params=params)
            assert response.status_code == 422
            assert response.json()["errorCode"] == "equipment_observation.invalid_request"
        for params, error in (
            ({}, "invalid_request"),
            ({**HISTORY_QUERY, "page": 0}, "invalid_request"),
            ({**HISTORY_QUERY, "pageSize": 101}, "invalid_request"),
            ({**HISTORY_QUERY, "from": "2026-11-24T05:00:00+00:60"}, "invalid_observed_at"),
            ({**HISTORY_QUERY, "from": "2026-11-24T05:00:00.0000001Z"}, "invalid_observed_at"),
            ({**HISTORY_QUERY, "from": "2026-11-24T05:00:01Z"}, "invalid_time_range"),
        ):
            response = await client.get(HISTORY, params=params)
            assert response.status_code == 422
            assert response.json() == {"code": 422, "message": f"equipment_observation.{error}",
                                       "errorCode": f"equipment_observation.{error}", "data": None}


def test_public_openapi_snapshot_and_sample_vectors():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    runtime = app.openapi()["paths"]
    published = json.loads((CONTRACT / "openapi.json").read_text(encoding="utf-8"))
    assert published["servers"] == [{"url": "/api/v1"}]
    assert set(published["paths"]) == {LATEST, HISTORY}
    for path in (LATEST, HISTORY):
        operation = runtime["/api/v1" + path]["get"]
        assert published["paths"][path] == {"get": operation}
        assert operation["security"] == []
        assert set(operation["responses"]) == {"200", "422", "503"}
        assert "$ref" not in json.dumps(operation)
    assert runtime["/api/v1" + HISTORY]["post"]["security"] == [{"ObservationMachineBearer": []}]
    assert runtime["/api/v1" + "/energy/consumption/samples"]["get"]["security"] == [{"HTTPBearer": []}]
    vectors = json.loads((CONTRACT / "examples/reads.json").read_text(encoding="utf-8"))
    assert {vector["path"] for vector in vectors} == {LATEST, HISTORY}
    for vector in vectors:
        assert vector["method"] == "GET" and vector["status"] == 200
        schema = published["paths"][vector["path"]]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
        response = vector["response"]
        assert set(response) == set(schema["required"]) and response["code"] == 200
        schema = schema["properties"]["data"]
        assert set(response["data"]) == set(schema["required"])
        item_schema = schema["properties"]["items"]["items"]
        for item in response["data"]["items"]:
            assert set(item) == set(item_schema["required"])
            assert item["observedAt"].endswith("+08:00") and type(item["values"]["activePower"]) in (int, float)
