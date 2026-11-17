"""r10 业务原采集时间、整包缺测和数值精度的无数据库回归。"""
from decimal import Decimal
from datetime import datetime, timedelta

import pytest
import httpx
from fastapi import FastAPI

from app.equipment_observation.domain import ObservationError
from app.equipment_observation.services import v2_domain
from app.equipment_observation.services.energy_statistics import summarize
from app.equipment_observation.api import routes
from app.equipment_observation.services import ingest_v2
from app.equipment_observation.profile import parse_profile
from database import get_db

pytestmark = pytest.mark.no_db


def device(**data):
    return {"eventId": "event-1", "data": {"equipmentId": "line-1", "taskNo": "000042",
            "observedAt": "2026-11-17T10:30:00.123456+08:00", "quality": "good", "groups": {}, **data}}


@pytest.mark.parametrize("value", [None, "2026-11-17T10:30:00", "2026-11-17T10:30:00.1234567+08:00", "bad"])
def test_observed_at_must_be_representable_and_offset_aware(value):
    with pytest.raises(ObservationError) as error:
        v2_domain.device_event(device(observedAt=value), {"producerId": "producer"}, "latest")
    assert error.value.reason == "invalid_observed_at"


def test_observed_at_normalizes_offset_without_losing_microseconds():
    row = v2_domain.device_event(device(observedAt="2026-11-17T02:30:00.1234560Z"),
                                 {"producerId": "producer"}, "history")
    assert row["observedAt"].isoformat() == "2026-11-17T10:30:00.123456"
    assert row["taskNo"] == "000042"


def test_explicit_empty_group_differs_in_idempotency_but_allows_missing_values():
    producer = {"producerId": "producer"}
    absent = v2_domain.device_event(device(), producer, "latest")
    empty = v2_domain.device_event(device(groups={"zone1": {}}), producer, "latest")
    assert absent["groups"] == {} and empty["groups"] == {"zone1": {}}
    assert absent["requestDigest"] != empty["requestDigest"]


def test_falsy_scalars_are_preserved_and_inexact_number_is_rejected():
    assert v2_domain.scalar(Decimal("0"), "number") == 0
    assert v2_domain.scalar(False, "boolean") is False
    assert v2_domain.scalar("", "string") == ""
    assert v2_domain.scalar(Decimal("0.1"), "number") == 0.1
    with pytest.raises(ObservationError) as error:
        v2_domain.scalar(Decimal("0.1234567890123456789"), "number")
    assert error.value.reason == "metric_type"


def test_energy_interval_must_be_real_and_ordered():
    doc = {"eventId": "event-1", "data": {"meterId": "meter", "groupKey": "electricity",
           "observedAt": "2026-11-17T09:00:00+08:00", "values": {"power": Decimal("1")},
           "intervalStartAt": "2026-11-17T08:00:00+08:00", "intervalEndAt": "2026-11-17T09:00:00+08:00"}}
    sample = v2_domain.energy_event(doc, {"producerId": "producer"})
    assert sample["intervalStartAt"] < sample["intervalEndAt"]
    for mutation in ({"intervalEndAt": None}, {"intervalStartAt": "2026-11-17T10:00:00+08:00"}):
        with pytest.raises(ObservationError):
            v2_domain.energy_event({**doc, "data": {**doc["data"], **mutation}}, {"producerId": "producer"})


def test_statistics_require_boundaries_and_rules_and_use_decimal():
    start = datetime(2026, 11, 17, 8)
    end = start + timedelta(hours=1)
    samples = [{"observedAt": start, "quality": "good", "value": Decimal("1000")},
               {"observedAt": end, "quality": "good", "value": Decimal("1006")}]
    rules = {"continuityConfirmed": True, "maxGapSeconds": 3600}
    assert summarize("cumulative", "kWh", samples, start, end, rules)["amount"] == Decimal("6")
    assert summarize("cumulative", "kWh", samples, start, end, {})["reason"] == "continuity_unknown"
    assert summarize("cumulative", "kWh", samples[1:], start, end, rules)["reason"] == "boundary_missing"
    assert summarize("cumulative", None, samples, start, end, rules)["reason"] == "unit_unknown"
    assert summarize("cumulative", "kWh", [{**samples[0], "value": 1007}, samples[1]], start, end, rules)["reason"] == "counter_decreased"
    assert summarize("instantaneous", "kW", samples, start, end, rules)["amount"] is None


def test_interval_sum_requires_complete_disjoint_segments():
    start = datetime(2026, 11, 17, 8)
    middle, end = start + timedelta(minutes=30), start + timedelta(hours=1)
    samples = [{"observedAt": middle, "quality": "good", "value": 2,
                "intervalStartAt": start, "intervalEndAt": middle},
               {"observedAt": end, "quality": "good", "value": 3,
                "intervalStartAt": middle, "intervalEndAt": end}]
    assert summarize("interval", "kWh", samples, start, end, {})["amount"] == Decimal("5")
    assert summarize("interval", "kWh", samples[1:], start, end, {})["reason"] == "interval_gap"
    assert summarize("interval", "kWh", samples + samples[:1], start, end, {})["reason"] == "interval_overlap"
    assert summarize("interval", "kWh", [{**samples[0], "quality": "bad"}, samples[1]], start, end, {})["reason"] == "bad_or_missing_sample"


def test_same_time_latest_values_are_not_ordered_by_arrival_or_id():
    start = datetime(2026, 11, 17, 8)
    end = start + timedelta(hours=1)
    first = {"observedAt": end, "quality": "good", "value": 6}
    same = summarize("instantaneous", "kW", [first, dict(first)], start, end, {})
    assert same["latest"] == Decimal(6) and same["latestState"] == "known"
    different = summarize("instantaneous", "kW", [first, {**first, "value": 7}], start, end, {})
    assert different["latest"] is None and different["latestState"] == "conflict"
    bad = summarize("instantaneous", "kW", [first, {**first, "quality": "bad"}], start, end, {})
    assert bad["latest"] is None and bad["latestState"] == "incomplete"


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/integration/equipment/latest-snapshots", "/integration/monitor/history-samples"])
async def test_http_preserves_raw_number_until_admission(monkeypatch, path):
    producer = {"producerId": "fixture"}
    monkeypatch.setattr(routes, "get_profile", lambda: {"target": {}})
    monkeypatch.setattr(routes, "authenticate", lambda _profile, _header: producer)
    async def admission(_db, _profile, _producer, target, _parsed, original):
        event = v2_domain.device_event(original, producer, target)
        return {"value": v2_domain.scalar(event["groups"]["temperature"]["actual"], "number")}
    monkeypatch.setattr(ingest_v2, "device", admission)
    app = FastAPI()
    app.include_router(routes.router)
    app.dependency_overrides[get_db] = lambda: object()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        template = ('{"eventId":"one","data":{"equipmentId":"line","taskNo":"000042",'
                    '"observedAt":"2026-11-17T10:30:00+08:00","quality":"good",'
                    '"groups":{"temperature":{"actual":NUMBER}}}}')
        headers = {"Authorization": "Bearer fixture", "Content-Type": "application/json"}
        accepted = await client.post(path, content=template.replace("NUMBER", "0.1"), headers=headers)
        rejected = await client.post(path, content=template.replace("NUMBER", "0.1234567890123456789"), headers=headers)
        assert accepted.status_code == 200 and accepted.json()["data"]["value"] == 0.1
        assert rejected.status_code == 422 and rejected.json()["errorCode"] == "equipment_observation.metric_type"


def test_new_areas_do_not_need_legacy_group_settings_or_plc_binding():
    profile = {"target": {"serverUuid": "00000000-0000-4000-8000-000000000001", "schema": "fixture", "schemaRevision": "9d1f3a5c7e20"},
        "devices": [{"equipmentId": "line", "nameZh": "线", "nameEn": "Line", "staleAfterSeconds": 20, "futureToleranceSeconds": 60}],
        "readScopes": {"admin": ["line"]}, "meters": [{"meterId": "meter", "nameZh": "表", "nameEn": "Meter"}],
        "meterReadScopes": {"admin": ["meter"]}, "historyRules": [], "groupSettings": [],
        "producers": [{"producerId": "fixture", "tokenSha256": "0" * 64, "kind": "other", "enabled": True,
            "grants": [{"equipmentId": "line", "groupKey": "new-area", "target": "latest", "metricKeys": ["actual"]}],
            "energyGrants": [{"meterId": "meter", "groupKey": "electricity", "metricKeys": ["reading"]}]}]}
    parsed = parse_profile(profile)
    assert parsed["devices"]["line"]["staleAfterSeconds"] == 20
    assert parsed["groupSettings"] == {}
    assert parsed["producers"]["fixture"]["grants"][0]["groupKey"] == "new-area"
    assert parsed["meterReadScopes"]["admin"] == ["meter"]


@pytest.mark.asyncio
async def test_empty_bundle_requires_explicit_target_grant():
    producer = {"producerId": "fixture", "grants": []}
    profile = {"devices": {"line-1": {}}, "groupSettings": {}, "producers": {}}
    with pytest.raises(ObservationError) as error:
        await ingest_v2.device(None, profile, producer, "latest", device())
    assert error.value.status == 403 and error.value.reason == "forbidden"


def test_runtime_openapi_matches_published_v2_machine_request_schemas():
    """Swagger 和公开合同必须展示同一正文，而原始 JSON 仍由边界校验。"""
    import json
    from pathlib import Path
    from fastapi import FastAPI
    from app.equipment_observation.api.routes import router
    app = FastAPI()
    app.include_router(router, prefix='/api/v1')
    published = json.loads((Path(__file__).resolve().parents[2] /
        'contracts/published/http-api/equipment-observation-v2/openapi.json').read_text())
    runtime = app.openapi()
    for path in ('/api/v1/integration/equipment/latest-snapshots',
                 '/api/v1/integration/monitor/history-samples', '/api/v1/integration/energy/samples'):
        actual = runtime['paths'][path]['post']['requestBody']['content']['application/json']['schema']
        expected = published['paths'][path]['post']['requestBody']['content']['application/json']['schema']
        actual = {key: value for key, value in actual.items() if key != 'title'}
        assert actual == expected, path
    latest = runtime['paths']['/api/v1/integration/equipment/latest-snapshots']['post']['requestBody']['content']['application/json']['schema']
    history = runtime['paths']['/api/v1/integration/monitor/history-samples']['post']['requestBody']['content']['application/json']['schema']
    assert 'quality' not in latest['properties']['data']['required']
    assert history['properties']['data']['properties']['quality']['const'] == 'good'
