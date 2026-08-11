"""No-DB tests for manifest-driven Core module discovery."""

from types import SimpleNamespace

import pytest
from fastapi import APIRouter

from app.module_registry import (
    ModuleManifest,
    ModuleRegistryError,
    discover_module_manifests,
    get_enabled_module_manifests,
    get_module_discovery_diagnostics,
    get_module_manifests,
    import_model_packages,
    include_module_routers,
    resolve_import_path,
)
from database import Base


pytestmark = pytest.mark.no_db


CORE_MODULES = {"monitor", "schema_maintenance", "system", "aiis_demo"}
ENABLED_MODULES = {"monitor", "schema_maintenance", "system"}


def test_discovery_uses_only_manifest_opted_in_core_modules():
    manifests = get_module_manifests()
    assert {manifest.name for manifest in manifests} == CORE_MODULES
    assert {manifest.name for manifest in get_enabled_module_manifests()} == ENABLED_MODULES
    assert [manifest.name for manifest in manifests] == [
        "system",
        "monitor",
        "schema_maintenance",
        "aiis_demo",
    ]


def test_discovery_diagnostics_are_redacted_and_stable():
    discover_module_manifests()
    diagnostics = get_module_discovery_diagnostics()
    assert diagnostics
    assert all(set(item.as_dict()) == {"module", "stage", "status", "error_type"} for item in diagnostics)
    assert all("password" not in str(item.as_dict()).lower() for item in diagnostics)


def test_disabled_demo_manifest_is_not_exposed_or_imported_as_router():
    app_router = APIRouter()
    include_module_routers(app_router)
    route_paths = {route.path for route in app_router.routes}
    assert "/ping" not in route_paths
    assert "/monitor/realtime/latest" in route_paths
    assert "/schema-maintenance/status" in route_paths


def test_model_imports_include_enabled_and_disabled_manifest_models():
    import_model_packages()
    assert "users" in Base.metadata.tables
    assert "sys_dicts" in Base.metadata.tables
    assert "monitor_collector_states" in Base.metadata.tables
    assert "aiis_demo" not in Base.metadata.tables


def test_manifest_validation_rejects_mismatched_name():
    module = SimpleNamespace(manifest=ModuleManifest(name="other"))
    assert module.manifest.name != "system"


def test_resolve_import_path_requires_module_attribute_syntax():
    with pytest.raises(ModuleRegistryError):
        resolve_import_path("app.system.api.routes")
