"""验证无旧 profile 表计时，可通过管理 API 新增表计并立即配置指标。"""
import pytest

from tests.test_energy_registered_ingest import ADMIN, OPERATOR, client_for, install_auth
from tests.test_equipment_observation_r10_flow import app_and_db  # noqa: F401

pytestmark = pytest.mark.no_db


@pytest.mark.asyncio
async def test_empty_meter_profile_accepts_new_configuration_without_reload(app_and_db):
    app, _session, profile, _ = app_and_db
    profile["meters"] = {}
    profile["meterReadScopes"] = {}
    install_auth(app)
    manage = "/energy/meters"
    options = "/energy/consumption/options"
    metric = {"meterId": "water.01", "groupKey": "water", "metricKey": "reading",
              "slotNo": 1, "nameZh": "读数", "nameEn": "Reading", "valueType": "number",
              "measurementMode": "cumulative", "quantityKey": "volume", "enabled": True}
    async with client_for(app) as client:
        assert (await client.get(manage, headers=ADMIN)).json()["data"] == []
        assert (await client.get(options, headers=ADMIN)).json()["data"] == []
        payload = {"meterId": "water.01", "nameZh": "水表", "nameEn": "Water meter"}
        created = await client.post(manage, headers=ADMIN, json=payload)
        assert created.status_code == 200, created.text
        assert created.json()["data"] == {**payload, "readRoles": ["admin"]}
        assert (await client.get(options, headers=ADMIN)).json()["data"] == [payload]
        assert (await client.get(options, headers=OPERATOR)).json()["data"] == []
        saved = await client.post("/energy/metric-configs", headers=ADMIN, json=metric)
        assert saved.status_code == 200, saved.text
        params = {"meterId": payload["meterId"]}
        endpoint = "/energy/consumption/definitions"
        assert (await client.get(endpoint, headers=OPERATOR, params=params)).status_code == 403
        updated = await client.patch(manage, headers=ADMIN,
                                     json={"meterId": payload["meterId"], "readRoles": ["operator", "operator", "admin"]})
        assert updated.json()["data"]["readRoles"] == ["admin", "operator"]
        assert (await client.get(endpoint, headers=OPERATOR, params=params)).json()["data"][0]["metricKey"] == "reading"
        app.state.role_api_permissions = {}
        assert (await client.get(endpoint, headers=OPERATOR, params=params)).status_code == 403
        assert profile["meters"] == {} and profile["meterReadScopes"] == {}
