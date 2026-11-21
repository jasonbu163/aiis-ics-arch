"""指标写入的类型、身份与省略语义回归。"""
from datetime import datetime, timedelta

import pytest

from app.equipment_observation.domain import ObservationError, scalar, task_no
from app.equipment_observation.profile import parse_profile
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


def test_profile_rejects_nonstring_uuid():
    profile = {"target": {"serverUuid": 123, "schema": "fixture", "schemaRevision": "d8f2a4c6b915"},
               "devices": [], "readScopes": {}, "producers": [], "historyRules": [], "groupSettings": []}
    with pytest.raises(ValueError):
        parse_profile(profile)


def test_entire_bundle_uses_device_stale_threshold_not_task_age():
    now = datetime(2026, 11, 11, 9, 30, 30)
    observed = now - timedelta(seconds=20)
    assert freshness(now, observed, 10) == "stale"
    assert freshness(now, observed, 30) == "fresh"
