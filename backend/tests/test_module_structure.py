"""No-DB structural checks for public Core modules."""

from pathlib import Path

import pytest

from app.module_registry import get_module_manifests


pytestmark = pytest.mark.no_db

CORE_MODULES = ("aiis_demo", "monitor", "schema_maintenance", "system")
REQUIRED_DIRS = ("api", "models", "schemas", "crud", "services", "mocks", "seeds")


def test_core_modules_keep_the_standard_package_shape():
    app_dir = Path("app")
    for module_name in CORE_MODULES:
        module_dir = app_dir / module_name
        assert (module_dir / "__init__.py").is_file()
        for directory in REQUIRED_DIRS:
            assert (module_dir / directory / "__init__.py").is_file()


def test_core_modules_opt_in_with_manifest_and_no_central_allowlist():
    manifests = get_module_manifests()
    assert {manifest.name for manifest in manifests} == set(CORE_MODULES)
    registry_source = Path("app/module_registry.py").read_text(encoding="utf-8")
    assert "REGISTERED_MODULES" not in registry_source
    assert "pkgutil.iter_modules" in registry_source


def test_explicit_runtime_boundaries_stay_outside_manifest_discovery():
    discovered = {manifest.name for manifest in get_module_manifests()}
    assert {"user", "control_agent"}.isdisjoint(discovered)


def test_project_business_module_directories_are_absent():
    app_dir = Path("app")
    for module_name in (
        "auxiliary",
        "dashboard",
        "energy",
        "equipment",
        "hr",
        "maintenance",
        "performance",
        "plan",
        "project",
        "quality",
        "reports",
    ):
        assert not (app_dir / module_name).exists()
