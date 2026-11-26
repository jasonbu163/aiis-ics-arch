"""验证曲线组 API 的隔离权限、字段校验、标识和过程回归。"""
import json
from pathlib import Path
from urllib.parse import quote

import pytest
from sqlalchemy import text

from app.equipment_observation.models import EnergyMetric
from tests.test_energy_registered_ingest import ADMIN, OPERATOR, client_for, install_auth
from tests.test_equipment_observation_r10_flow import app_and_db  # noqa: F401


pytestmark = pytest.mark.no_db
MANAGEMENT = "/energy/curve-configs"
CONSUMPTION = "/energy/consumption/curve-configs"
TABLE = "energy_curve_group_configs"


def payload(key="power", meter="meter1", **overrides):
    return {"curveGroupKey": key, "titleZh": "功率", "meterId": meter, "groupKey": "electricity",
            "sortOrder": 0, "enabled": True, "series": [series("primary")], **overrides}


def series(key, enabled=True, style="solid"):
    return {"metricKey": key, "enabled": enabled, "lineStyle": style}


def seed_curve_metrics(session):
    configs = [
        ("meter1", "primary", 1, "power", "kW", True, "instantaneous"),
        ("meter1", "standby", 2, "power", "kW", False, "instantaneous"),
        ("meter1", "count", 3, "power", None, True, "instantaneous"),
        ("meter1", "total", 4, "energy", "kWh", True, "cumulative"),
        ("meter1", "increment", 5, "energy", "kWh", True, "interval"),
        ("meter1", "unrelated", 6, "other", "kW", True, "instantaneous"),
        ("meter1", "uncalibrated", 7, "power", "", True, "instantaneous"),
        ("meter2", "primary", 3, "power", "kW", True, "instantaneous"),
    ]
    for meter, key, slot, quantity, unit, enabled, mode in configs:
        session.add(EnergyMetric(meter_id=meter, group_key="electricity", metric_key=key, slot_no=slot,
                                 name_zh=key, name_en=key, value_type="number", quantity_key=quantity,
                                 measurement_mode=mode, unit=unit, enabled=enabled, rules={}, decimals=2))
    session.commit()


def assert_error(result, status, code):
    assert result.status_code == status, result.text
    reason = f"equipment_observation.{code}"
    assert result.json() == {"code": status, "message": reason, "data": None, "errorCode": reason}


@pytest.fixture
def curve_app(app_and_db):
    app, session, profile, _ = app_and_db
    session.execute(text(f"CREATE TABLE {TABLE} (curve_group_key TEXT PRIMARY KEY, title_zh TEXT NOT NULL, "
                         "title_en TEXT NOT NULL, meter_id TEXT NOT NULL, group_key TEXT NOT NULL, "
                         "sort_order INTEGER NOT NULL, enabled BOOLEAN NOT NULL, series JSON NOT NULL)"))
    seed_curve_metrics(session)
    install_auth(app)
    profile["meterReadScopes"]["operator"] = ["meter1"]
    return app, session, profile


@pytest.mark.asyncio
async def test_scope_create_filter_partial_updates_and_openapi(curve_app):
    app, session, profile = curve_app
    async with client_for(app) as client:
        for method, path in (("GET", MANAGEMENT), ("GET", CONSUMPTION), ("POST", MANAGEMENT),
                             ("PATCH", MANAGEMENT + "/unknown")):
            assert_error(await client.request(method, path, json={}), 401, "unauthenticated")
        assert_error(await client.get(MANAGEMENT, headers=OPERATOR), 403, "forbidden")
        assert_error(await client.post(MANAGEMENT, headers=OPERATOR, json=payload()), 403, "forbidden")
        assert (await client.get(CONSUMPTION, headers=OPERATOR)).json()["data"] == []
        old = (await client.get("/monitor/curve-configs", headers=ADMIN)).json()
        assert old["data"][0]["curveGroupKey"] == "temp-curve"
        bad_process = await client.post("/monitor/curve-configs", headers=ADMIN, json={})
        assert bad_process.status_code == 422 and "detail" in bad_process.json()

        desired = payload("电表/A", series=[series("standby", style="dashed"), series("primary")])
        saved = await client.post(MANAGEMENT, headers=ADMIN, json=desired)
        assert saved.status_code == 200, saved.text
        assert saved.json()["data"] == {**desired, "titleEn": ""}
        assert_error(await client.post(MANAGEMENT, headers=ADMIN, json=desired), 409, "configuration_conflict")
        for key, kwargs in (("other-meter", {"meter": "meter2"}), ("hidden", {"enabled": False}),
                            ("before", {"sortOrder": -1})):
            result = await client.post(MANAGEMENT, headers=ADMIN, json=payload(key, **kwargs))
            assert result.status_code == 200, result.text
        for key, escaped in ((".", "%252e"), ("..", "%252e%252e"), ("%2e", "%25%32%65"),
                             ("%2e%2e", "%25%32%65%25%32%65"), ("电表/a", quote("电表/a", safe=""))):
            assert (await client.post(MANAGEMENT, headers=ADMIN, json=payload(key, enabled=False))).status_code == 200
            result = await client.patch(MANAGEMENT + "/" + escaped, headers=ADMIN, json={"titleEn": key})
            assert result.status_code == 200 and result.json()["data"]["curveGroupKey"] == key, result.text

        target = MANAGEMENT + "/" + quote(desired["curveGroupKey"], safe="")
        updated = await client.patch(target, headers=ADMIN, json={"titleEn": "Power", "sortOrder": 12})
        assert updated.json()["data"] == {**desired, "titleEn": "Power", "sortOrder": 12}
        assert_error(await client.patch(target, headers=ADMIN, json={"curveGroupKey": "changed"}), 422, "invalid_request")
        assert_error(await client.patch(target, headers=ADMIN, json={"titleEn": None}), 422, "invalid_request")
        assert_error(await client.patch(MANAGEMENT + "/unknown", headers=ADMIN, json={"enabled": False}), 404, "not_found")
        groups = (await client.get(CONSUMPTION, headers=OPERATOR)).json()["data"]
        assert [row["curveGroupKey"] for row in groups] == ["before", "电表/A"]
        assert_error(await client.get(CONSUMPTION, headers=OPERATOR, params={"meterId": "meter2"}), 403, "forbidden")
        group = await client.get(MANAGEMENT, headers=ADMIN, params={"meterId": "meter2"})
        assert [row["curveGroupKey"] for row in group.json()["data"]] == ["other-meter"]
        app.state.role_api_permissions = {}
        assert_error(await client.get(CONSUMPTION, headers=OPERATOR), 403, "forbidden")
        profile["meterReadScopes"]["admin"] = ["meter1"]
        assert_error(await client.get(MANAGEMENT, headers=ADMIN, params={"meterId": "meter2"}), 403, "forbidden")
        assert_error(await client.patch(target, headers=ADMIN, json={"meterId": "meter2"}), 403, "forbidden")
        assert_error(await client.patch(MANAGEMENT + "/other-meter", headers=ADMIN, json={"meterId": "meter1"}), 403, "forbidden")
        assert (await client.get("/monitor/curve-configs", headers=ADMIN)).json() == old

        paths = app.openapi()["paths"]
        for method, path in (("get", MANAGEMENT), ("post", MANAGEMENT),
                             ("patch", MANAGEMENT + "/{curveGroupKey}"), ("get", CONSUMPTION)):
            operation = paths["/api/v1" + path][method]
            assert operation["tags"] == ["Energy"]
            assert operation["security"] == [{"HTTPBearer": []}]
            assert "422" in operation["responses"] and "503" in operation["responses"]


@pytest.mark.asyncio
async def test_title_metric_curve_validation_and_schema_failure(curve_app):
    app, session, _ = curve_app
    invalid = [
        ({"titleZh": "   "}, "invalid_request"),
        ({"series": [series("primary", False)]}, "curve_items"),
        ({"series": [series("primary"), series("primary", False)]}, "curve_items"),
        ({"series": [series("missing")]}, "curve_items"),
        ({"series": [series("primary"), series("unrelated")]}, "curve_units"),
        ({"series": [series("primary"), series("count")]}, "curve_units"),
        ({"groupKey": "missing"}, "curve_items"),
        ({"series": [series("primary", style="dotted")]}, "invalid_request"),
    ]
    async with client_for(app) as client:
        for changes, code in invalid:
            assert_error(await client.post(MANAGEMENT, headers=ADMIN, json=payload(**changes)), 422, code)
        for key, values in (("unitless", [series("count"), series("uncalibrated")]),
                            ("disabled-other", [series("primary"), series("total", False)])):
            assert (await client.post(MANAGEMENT, headers=ADMIN, json=payload(key, series=values))).status_code == 200
        assert (await client.patch(MANAGEMENT + "/unitless", headers=ADMIN, json={"enabled": False})).status_code == 200
        session.execute(text(f"ALTER TABLE {TABLE} RENAME TO energy_curve_unavailable"))
        session.commit()
        assert_error(await client.get(CONSUMPTION, headers=OPERATOR), 503, "not_ready")
        assert (await client.get("/energy/consumption/definitions", headers=OPERATOR, params={"meterId": "meter1"})).status_code == 200


def test_published_curve_openapi_matches_registered_contract(curve_app):
    app, _, _ = curve_app
    live = app.openapi()
    path = Path(__file__).resolve().parents[2] / "contracts/published/http-api/energy-curve-groups-v1/openapi.json"
    published = json.loads(path.read_text())
    expected_paths = {
        "/api/v1" + MANAGEMENT, "/api/v1" + CONSUMPTION, "/api/v1" + MANAGEMENT + "/{curveGroupKey}",
    }
    assert set(published["paths"]) == expected_paths
    assert published["paths"] == {path: live["paths"][path] for path in expected_paths}
    for section, values in published["components"].items():
        assert values == {name: live["components"][section][name] for name in values}
