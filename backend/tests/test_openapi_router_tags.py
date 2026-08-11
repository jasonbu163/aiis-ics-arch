"""No-DB OpenAPI tag and route-surface checks for the public Core API."""

import pytest

from core.registrar import create_app


pytestmark = pytest.mark.no_db

EXPECTED_TAGS = {
    "User - Auth",
    "User - Users",
    "Control Agent",
    "System - Dictionary",
    "System - Dictionary Items",
    "System - Projection Mapping",
    "Monitor - Collector",
    "Monitor - Realtime",
    "Schema Maintenance",
}


def test_openapi_contains_only_public_core_operation_tags():
    schema = create_app(testing=True).openapi()
    tags = {
        tag
        for methods in schema["paths"].values()
        for operation in methods.values()
        for tag in operation.get("tags", [])
    }
    assert tags == EXPECTED_TAGS


def test_openapi_excludes_project_business_routes():
    schema = create_app(testing=True).openapi()
    paths = set(schema["paths"])
    assert not any(
        path.startswith("/api/v1/" + prefix)
        for path in paths
        for prefix in (
            "plans",
            "performances",
            "projects",
            "equipment",
            "quality",
            "reports",
            "energy",
            "hr",
            "maintenance",
            "dashboard",
        )
    )


def test_core_realtime_and_collector_paths_keep_stable_prefixes():
    schema = create_app(testing=True).openapi()
    assert "/api/v1/monitor/realtime/latest" in schema["paths"]
    assert "/api/v1/monitor/collector/status" in schema["paths"]
    assert schema["paths"]["/api/v1/monitor/realtime/latest"]["get"]["tags"] == [
        "Monitor - Realtime"
    ]
