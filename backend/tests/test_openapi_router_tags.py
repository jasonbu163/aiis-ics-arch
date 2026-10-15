"""No-DB OpenAPI tag and route-surface checks for the public Core API."""

import pytest

from core.registrar import create_app


pytestmark = pytest.mark.no_db

EXPECTED_TAGS = {
    "Auxiliary - Energy Price",
    "Auxiliary - Shift Teams", "Auxiliary - Shifts", "Auxiliary - Shift Rules", "Auxiliary - Stop Records",
    "Dashboard", "Equipment", "Maintenance", "Maintenance - Logs",
    "Performance", "Performance - Split", "Performance - Lineage",
    "Plan", "Project", "Quality", "Quality - Defects", "Reports", "Reports - Assessments", "Reports - Efficiency", "Reports - Print", "Reports - Targets",
    "Monitor - Temperature", "Monitor - Energy",
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
    assert EXPECTED_TAGS.issubset(tags)


def test_openapi_excludes_disabled_hr_routes_and_c2_stays_clean(tmp_path):
    schema = create_app(testing=True).openapi()
    assert not any(path.startswith('/api/v1/hr') for path in schema['paths'])
    from tests.module_admission_fixtures import generate_core_profile, run_python
    profile = generate_core_profile(tmp_path / 'C2')
    result = run_python(profile, 'import pytest\nraise SystemExit(pytest.main(["--noconftest", "-q", "-m", "no_db", "tests/test_openapi_router_tags.py"]))')
    assert result.returncode == 0, result.stdout + result.stderr


def test_core_realtime_and_collector_paths_keep_stable_prefixes():
    schema = create_app(testing=True).openapi()
    assert "/api/v1/monitor/realtime/latest" in schema["paths"]
    assert "/api/v1/monitor/collector/status" in schema["paths"]
    assert schema["paths"]["/api/v1/monitor/realtime/latest"]["get"]["tags"] == [
        "Monitor - Realtime"
    ]


def test_public_energy_slice_exposes_only_approved_methods():
    paths = create_app(testing=True).openapi()["paths"]
    energy = {path: set(methods) for path, methods in paths.items() if path.startswith("/api/v1/energy")}
    assert energy == {"/api/v1/energy": {"get", "post"}, "/api/v1/energy/current": {"get"}}
