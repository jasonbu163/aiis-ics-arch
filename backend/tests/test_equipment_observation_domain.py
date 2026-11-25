"""指标写入的类型、身份与省略语义回归。"""
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.equipment_observation.domain import ObservationError, scalar, task_no
from app.equipment_observation.profile import parse_profile, require_energy_target
from app.equipment_observation.services.guard import current_clock
from app.equipment_observation.services.reads import freshness

pytestmark = pytest.mark.no_db


def producer():
    return {"producerId": "vendor-1", "kind": "external", "sourceId": "source-1",
            "mappingId": "mapping-1", "mappingRevision": "r1",
            "grants": [{"equipmentId": "line-1", "groupKey": "temperature", "target": target,
                        "metricKeys": ["actual"]} for target in ("latest", "history")]}


def body():
    return {"sourceRefs": [{"kind": "external_event", "sourceEventId": "sample-1"}],
            "data": {"taskNo": " 00a-1 ", "sampledAt": "2026-11-11T08:00:00.123+08:00",
                     "values": {"actual": 0}}}


def test_task_no_ascii_and_numeric_domain():
    assert task_no(" 00a-1 ") == "00A-1"
    assert scalar(0, "number") == 0
    assert scalar(False, "boolean") is False
    for invalid in ("ß", "中文", ""):
        with pytest.raises(ObservationError):
            task_no(invalid)
    for invalid in (10**400, 2**65, float("inf"), True):
        with pytest.raises(ObservationError):
            scalar(invalid, "number")


def test_nonstring_uuid_is_ignored_by_observation_and_rejected_for_energy():
    profile = {"target": {"serverUuid": 123, "schema": "fixture", "schemaRevision": "e9f3b5d7c021"},
               "devices": [], "readScopes": {}, "producers": [], "historyRules": [], "groupSettings": []}
    parsed = parse_profile(profile)
    assert parsed["target"] == profile["target"]
    with pytest.raises(ObservationError, match="not_ready"):
        require_energy_target(parsed)


def test_entire_bundle_uses_device_stale_threshold_not_task_age():
    now = datetime(2026, 11, 11, 9, 30, 30)
    observed = now - timedelta(seconds=20)
    assert freshness(now, observed, 10) == "stale"
    assert freshness(now, observed, 30) == "fresh"


@pytest.mark.asyncio
async def test_observation_clock_converts_db_utc_without_session_timezone_probe():
    utc = datetime(2026, 11, 17, 23, 30, 0, 123456)
    db = SimpleNamespace(execute=AsyncMock(return_value=SimpleNamespace(scalar_one=lambda: utc)))
    assert await current_clock(db) == datetime(2026, 11, 18, 7, 30, 0, 123456)
    db.execute.assert_awaited_once()
    assert str(db.execute.await_args.args[0]) == "SELECT UTC_TIMESTAMP(6)"
