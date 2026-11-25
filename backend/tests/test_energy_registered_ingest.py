"""能耗登记和批量 POST 的 HTTP、校验与存储行为。"""
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from fastapi import HTTPException, Request
import httpx
import pytest
from sqlalchemy import select

from app.equipment_observation.models import EnergyMetric, EnergyReceipt, EnergySample, EnergyWriteSource
from app.equipment_observation.profile import valid_identifier
from app.equipment_observation.services import energy_registered_ingest, energy_write_sources
from core.deps import get_current_user
from tests.test_equipment_observation_r10_flow import app_and_db

pytestmark = pytest.mark.no_db
MANAGE = "/energy/write-sources"
WRITE = "/integration/energy/registered-samples"


def batch():
    return {"sourceKey": "Line.A", "target": "energy", "observedAt": "2026-11-24T12:00:00+08:00", "items": {
        "meter2": {"electricity": {"values": {"totalEnergy": 9820, "activePower": 0}}},
        "meter1": {"electricity": {"values": {"intervalEnergy": 120}, "quality": "good",
                                   "intervalStartAt": "2026-11-24T11:00:00+08:00",
                                   "intervalEndAt": "2026-11-24T12:00:00+08:00"}},
    }}


def metrics(session):
    for meter, key, slot, mode in (
        ("meter1", "intervalEnergy", 1, "interval"),
        ("meter2", "totalEnergy", 1, "cumulative"),
        ("meter2", "activePower", 2, "instantaneous"),
    ):
        session.add(EnergyMetric(meter_id=meter, group_key="electricity", metric_key=key, slot_no=slot,
                                 name_zh=key, name_en=key, value_type="number", measurement_mode=mode,
                                 quantity_key="energy", unit="kWh", enabled=True, rules={}))
    session.commit()


def install_auth(app):
    async def jwt_fixture(request: Request):
        header = request.headers.get("authorization")
        if header not in ("Bearer admin-fixture", "Bearer operator-fixture"):
            raise HTTPException(401, "login required")
        return SimpleNamespace(role=header.split()[1].split("-")[0], is_active=True)
    app.dependency_overrides[get_current_user] = jwt_fixture
    app.state.role_api_permissions = {"operator": {"energy-consumption-read"}}


def client_for(app):
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test/api/v1")


ADMIN = {"Authorization": "Bearer admin-fixture"}
OPERATOR = {"Authorization": "Bearer operator-fixture"}


@pytest.mark.asyncio
async def test_registered_sources_permissions_and_key_lifecycle(app_and_db):
    app, session, profile, _ = app_and_db
    install_auth(app)
    profile["target"]["schemaRevision"] = "synthetic-unrelated-successor"
    async with client_for(app) as client:
        for method, path in (("GET", MANAGE), ("POST", MANAGE), ("PATCH", MANAGE + "/Line.A"), ("DELETE", MANAGE + "/Line.A")):
            assert (await client.request(method, path, json={"enabled": True})).status_code == 401
            assert (await client.request(method, path, json={"enabled": True}, headers=OPERATOR)).status_code == 403
        assert (await client.get(MANAGE, headers=ADMIN)).json()["data"] == []
        for key in ("Line.A", "line.a", ".", ".."):
            response = await client.post(MANAGE, headers=ADMIN, json={"sourceKey": key})
            saved = response.json()["data"]
            assert (response.status_code, saved["sourceKey"], saved["enabled"], saved["name"]) == (200, key, True, None)
            assert saved["createdAt"].endswith("+08:00")
            assert set(saved) == {"sourceKey", "name", "enabled", "createdAt", "updatedAt"}
        for key in ("%252E", "%252E%252E"):
            assert (await client.patch(MANAGE + "/" + key, headers=ADMIN, json={"name":"dots"})).status_code == 200
        assert (await client.patch(MANAGE + "/Line.A", headers=ADMIN, json={"sourceKey": "altered"})).status_code == 422
        assert (await client.delete(MANAGE + "/Line.A", headers=ADMIN)).json()["data"] == {"sourceKey": "Line.A", "deleted": True}
        assert (await client.delete(MANAGE + "/Line.A", headers=ADMIN)).status_code == 404
        assert (await client.post(MANAGE, headers=ADMIN, json={"sourceKey": "Line.A"})).status_code == 409
        assert (await client.post(MANAGE, headers=ADMIN, json={"sourceKey": "中文"})).status_code == 422
        assert {item["sourceKey"] for item in (await client.get(MANAGE, headers=ADMIN)).json()["data"]} == {"line.a", ".", ".."}
        assert not valid_identifier(energy_write_sources.storage_identity("Line.A"))


@pytest.mark.asyncio
async def test_multi_meter_http_replay_summary_and_scope(app_and_db):
    app, session, profile, _ = app_and_db
    install_auth(app)
    profile["meterReadScopes"]["operator"] = ["meter1"]
    metrics(session)
    async with client_for(app) as client:
        assert (await client.post(MANAGE, headers=ADMIN, json={"sourceKey": "Line.A"})).status_code == 200
        request = batch()
        response = await client.post(WRITE, json=request)
        assert response.status_code == 200, response.text
        stored = response.json()["data"]
        assert stored["observedAt"] == "2026-11-24T12:00:00.000000+08:00"
        assert [item["meterId"] for item in stored["records"]] == ["meter1", "meter2"]
        receipt = session.get(EnergyReceipt, int(stored["receiptId"]))
        assert receipt.result_detail == {"records": stored["records"]}
        assert receipt.result_record_id is None
        rows = list(session.execute(select(EnergySample).order_by(EnergySample.meter_id)).scalars())
        assert [item.quality for item in rows] == ["good", "unknown"]
        assert {item.ingest_receipt_id for item in rows} == {receipt.id}
        assert rows[1].local_values == {"01": 9820, "02": 0}
        session.get(EnergyMetric, ("meter2", "electricity", "activePower")).enabled = False
        session.commit()
        equivalent = deepcopy(request)
        equivalent["observedAt"] = "2026-11-24T04:00:00.0000000Z"
        equivalent["items"]["meter1"]["electricity"]["intervalStartAt"] = "2026-11-24T03:00:00Z"
        equivalent["items"]["meter1"]["electricity"]["values"]["intervalEnergy"] = 120.0
        equivalent["items"]["meter2"]["electricity"]["quality"] = None
        replay = await client.post(WRITE, json=equivalent, headers={"Authorization": "deliberately ignored"})
        assert replay.json()["data"] == stored
        changed = deepcopy(request)
        changed["items"].pop("meter2")
        response = await client.post(WRITE, json=changed)
        assert response.status_code == 409 and response.json()["errorCode"] == "equipment_observation.event_conflict"
        samples = "/energy/consumption/samples"
        assert (await client.get(samples, params={"meterId": "meter1"})).status_code == 401
        assert (await client.get(samples, params={"meterId": "meter2"}, headers=OPERATOR)).status_code == 403
        values = (await client.get(samples, params={"meterId": "meter2"}, headers=ADMIN)).json()["data"]["items"][0]["values"]
        assert {item["value"] for item in values} == {0, 9820}
        summary = await client.get("/energy/consumption/summary", headers=OPERATOR,
            params={"meterId": "meter1", "groupKey": "electricity", "metricKey": "intervalEnergy",
                    "from": "2026-11-24T11:00:00+08:00", "to": "2026-11-24T12:00:00+08:00"})
        assert summary.json()["data"]["amount"] == 120
        assert (await client.patch(MANAGE + "/Line.A", headers=ADMIN, json={"enabled": False})).status_code == 200
        assert (await client.post(WRITE, json=request)).status_code == 403
        assert (await client.patch(MANAGE + "/Line.A", headers=ADMIN, json={"enabled": True})).status_code == 200
        assert (await client.post(WRITE, json=request)).json()["data"] == stored
        assert (await client.delete(MANAGE + "/Line.A", headers=ADMIN)).status_code == 200
        assert (await client.post(WRITE, json=request)).status_code == 403
        assert len(session.execute(select(EnergySample)).scalars().all()) == 2


@pytest.mark.asyncio
async def test_invalid_second_item_entirely_rejected(app_and_db):
    app, session, _, _ = app_and_db
    install_auth(app)
    metrics(session)
    async with client_for(app) as client:
        assert (await client.post(MANAGE, headers=ADMIN, json={"sourceKey": "Line.A"})).status_code == 200
        for fields, reason in (
            ({"values": {}}, "values"), ({"values": {"activePower": None}}, "metric_type"),
            ({"values": {"activePower": True}}, "metric_type"), ({"values": {"missing": 0}}, "metric_scope"),
            ({"values": {"activePower": 0}, "quality": "maybe"}, "quality"),
            ({"values": {"activePower": 0}, "intervalStartAt": "2026-11-24T11:00:00+08:00"}, "invalid_time_range"),
            ({"values": {"activePower": 0}, "intervalStartAt": "2026-11-24T11:00:00+08:00",
              "intervalEndAt": "2026-11-24T12:00:00+08:00"}, "invalid_time_range"),
        ):
            request = batch()
            request["items"]["meter2"]["electricity"] = fields
            response = await client.post(WRITE, json=request)
            assert response.status_code == 422 and response.json()["errorCode"] == "equipment_observation." + reason
        invalid = batch()
        invalid["sourceKey"] = "Unknown"
        assert (await client.post(WRITE, json=invalid)).status_code == 403
        assert (await client.post(WRITE, content=b"{}")).status_code == 415
        assert (await client.post(WRITE, content=b" " * 65537, headers={"content-type": "application/json"})).status_code == 413
        assert (await client.post(WRITE, content=b'{"a":1,"a":2}', headers={"content-type": "application/json"})).status_code == 422
        assert session.execute(select(EnergyReceipt)).scalars().all() == []
        assert session.execute(select(EnergySample)).scalars().all() == []


def test_canonical_keys_offsets_and_exact_decimal():
    request = batch()
    request["items"]["meter2"]["electricity"]["values"]["activePower"] = Decimal("0.000")
    result, _, digest, event_id, _ = energy_registered_ingest.normalize(request)
    equivalent = deepcopy(request)
    equivalent["items"] = dict(reversed(list(equivalent["items"].items())))
    equivalent["items"]["meter2"]["electricity"]["values"]["activePower"] = 0
    equivalent["items"]["meter2"]["electricity"]["quality"] = "unknown"
    equivalent["observedAt"] = "2026-11-24T04:00:00Z"
    assert energy_registered_ingest.normalize(equivalent)[2:4] == (digest, event_id)
    assert result["observedAt"].endswith(".000000+08:00")
