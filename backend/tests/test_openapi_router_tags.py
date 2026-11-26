"""No-DB OpenAPI tag and route-surface checks for the public Core API."""

import pytest

from core.registrar import create_app


pytestmark = pytest.mark.no_db

EXPECTED_TAGS = {
    "Energy",
    "Auxiliary - Shift Teams", "Auxiliary - Shifts", "Auxiliary - Shift Rules", "Auxiliary - Stop Records",
    "Equipment observation", "Maintenance", "Maintenance - Logs",
    "Performance", "Plan", "Task fields", "Project", "Quality", "Quality - Defects",
    "User - Auth",
    "User - Users",
    "Control Agent",
    "System - Dictionary",
    "System - Dictionary Items",
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
    assert not {"Dashboard", "Performance - Split", "Performance - Lineage", "Reports"}.intersection(tags)


def test_openapi_excludes_disabled_hr_routes_and_c2_stays_clean(tmp_path):
    schema = create_app(testing=True).openapi()
    assert not any(path.startswith('/api/v1/hr') for path in schema['paths'])
    from tests.module_admission_fixtures import generate_core_profile, run_python
    profile = generate_core_profile(tmp_path / 'C2')
    result = run_python(profile, 'import pytest\nraise SystemExit(pytest.main(["--noconftest", "-q", "-m", "no_db", "tests/test_openapi_router_tags.py"]))')
    assert result.returncode == 0, result.stdout + result.stderr


def test_retired_realtime_and_collector_paths():
    schema = create_app(testing=True).openapi()
    assert "/api/v1/monitor/realtime/latest" not in schema["paths"]
    assert "/api/v1/monitor/collector/status" not in schema["paths"]


def test_public_energy_slice_exposes_only_approved_methods():
    paths = create_app(testing=True).openapi()["paths"]
    energy = {path: set(paths[path]) for path in ("/api/v1/energy", "/api/v1/energy/current")}
    assert energy == {"/api/v1/energy": {"get", "post"}, "/api/v1/energy/current": {"get"}}


def test_energy_swagger_group_and_authentication_labels():
    paths = create_app(testing=True).openapi()["paths"]
    public = {
        ("/api/v1/integration/energy/latest", "get"),
        ("/api/v1/integration/energy/samples", "get"),
        ("/api/v1/integration/energy/registered-samples", "post"),
    }
    assert public <= {(path, method) for path, methods in paths.items() for method in methods}
    for path, methods in paths.items():
        is_energy = path == "/api/v1/energy" or path.startswith(("/api/v1/energy/", "/api/v1/integration/energy/"))
        is_management = path.startswith(("/api/v1/energy/write-sources", "/api/v1/energy/metric-configs",
                                        "/api/v1/energy/admin/", "/api/v1/energy/curve-configs")) or path == "/api/v1/energy/meters"
        for method, operation in methods.items():
            tags = operation.get("tags", [])
            if not is_energy:
                assert "Energy" not in tags
                continue
            assert tags == ["Energy"]
            if (path, method) in public:
                assert operation["summary"].startswith("Public — ")
                assert not operation.get("security")
            else:
                scheme = "ObservationMachineBearer" if path.startswith("/api/v1/integration/energy/") else "HTTPBearer"
                assert operation["security"] == [{scheme: []}]
                assert operation["summary"].startswith("Management — ") == is_management
