"""No-DB structural checks for public Core modules."""

from pathlib import Path

import pytest

from app.module_registry import get_module_manifests


pytestmark = pytest.mark.no_db

CORE_MODULES = ("auxiliary", "aiis_demo", "equipment_observation", "schema_maintenance", "system")
REQUIRED_DIRS = ("api", "models", "schemas", "crud", "services", "mocks", "seeds")


def test_core_modules_keep_the_standard_package_shape():
    app_dir = Path("app")
    manifests = {manifest.name for manifest in get_module_manifests()}
    assert {"equipment", "monitor"}.isdisjoint(manifests)
    for module_name in CORE_MODULES:
        module_dir = app_dir / module_name
        assert (module_dir / "__init__.py").is_file()
        for directory in REQUIRED_DIRS:
            if module_name == "equipment_observation" and directory == "schemas":
                assert (module_dir / "schemas.py").is_file()
            elif module_name != "equipment_observation" or directory in {"api", "models", "services"}:
                assert (module_dir / directory / "__init__.py").is_file()


def test_core_modules_opt_in_with_manifest_and_no_central_allowlist():
    manifests = get_module_manifests()
    assert set(CORE_MODULES).issubset(manifest.name for manifest in manifests)
    registry_source = Path("app/module_registry.py").read_text(encoding="utf-8")
    assert "REGISTERED_MODULES" not in registry_source
    assert "pkgutil.iter_modules" in registry_source


def test_explicit_runtime_boundaries_stay_outside_manifest_discovery():
    discovered = {manifest.name for manifest in get_module_manifests()}
    assert {"user", "control_agent"}.isdisjoint(discovered)


def test_project_business_module_directories_are_absent_in_c2(tmp_path):
    from tests.module_admission_fixtures import generate_core_profile, run_python
    profile = generate_core_profile(tmp_path / "C2")
    result = run_python(profile, 'import pytest\nraise SystemExit(pytest.main(["--noconftest", "-q", "-m", "no_db", "tests/test_module_structure.py", "tests/test_celery_retirement.py", "tests/test_core_migration_baseline.py"]))')
    assert result.returncode == 0, result.stdout + result.stderr
