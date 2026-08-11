"""No-DB checks for the explicit Core schema-maintenance surface."""

from pathlib import Path

import pytest

from core.registrar import create_app


pytestmark = pytest.mark.no_db


def test_schema_maintenance_exposes_only_read_status_and_explicit_actions():
    schema = create_app(testing=True).openapi()
    paths = {
        path
        for path in schema["paths"]
        if path.startswith("/api/v1/schema-maintenance/")
    }
    assert paths == {
        "/api/v1/schema-maintenance/status",
        "/api/v1/schema-maintenance/initialize",
        "/api/v1/schema-maintenance/upgrade",
    }
    assert "/api/v1/schema-maintenance/apply" not in schema["paths"]


def test_schema_maintenance_source_contains_no_project_table_names():
    source = "".join(
        path.read_text(encoding="utf-8")
        for path in Path("app/schema_maintenance").rglob("*.py")
    )
    for marker in ("energy_prices", "performance_main", "projects", "quality_records"):
        assert marker not in source
