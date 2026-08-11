"""
文件路径: /backend/tests/app/monitor/test_collector.py
功能描述: Control Agent collector 状态查询合同测试
主要功能:
    - 验证 collector 状态查询的缺失状态合同
    - 固定 Service 与 HTTP 无参查询的 Control Agent 默认 key
    - 保留显式 collector key 查询能力
"""
from app.monitor.services.collector.async_query import get_collector_status_data


async def test_collector_status_defaults_to_control_agent_plc(db_session):
    status = await get_collector_status_data(db_session)

    assert status["collectorKey"] == "control-agent-plc"
    assert status["status"] == "stopped"
    assert status["stale"] is True
    assert status["sampleCount"] == 0


async def test_collector_status_returns_default_when_missing(db_session):
    status = await get_collector_status_data(
        db_session,
        collector_key="missing-collector",
    )

    assert status["collectorKey"] == "missing-collector"
    assert status["status"] == "stopped"
    assert status["stale"] is True
    assert status["sampleCount"] == 0


async def test_collector_route_keeps_public_contract(test_client, auth_headers):
    response = await test_client.get(
        "/api/v1/monitor/collector/status",
        params={"collectorKey": "missing-collector"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["collectorKey"] == "missing-collector"
    assert data["status"] == "stopped"


async def test_collector_route_defaults_to_control_agent_plc(test_client, auth_headers):
    response = await test_client.get(
        "/api/v1/monitor/collector/status",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["collectorKey"] == "control-agent-plc"
    assert data["status"] == "stopped"
