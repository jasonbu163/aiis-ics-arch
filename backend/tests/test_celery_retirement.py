"""No-DB checks that the public Core runtime has no Celery worker surface."""

from pathlib import Path

import pytest


pytestmark = pytest.mark.no_db

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_celery_worker_surfaces_and_dependencies_are_absent():
    retired_paths = (
        BACKEND_ROOT / "worker",
        BACKEND_ROOT / "app" / "worker_control",
        BACKEND_ROOT / "core" / "celery.py",
        BACKEND_ROOT / "scripts" / "celery",
    )
    assert all(not path.exists() for path in retired_paths)
    pyproject = (BACKEND_ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
    assert '"celery' not in pyproject
    assert '"redis' not in pyproject
    assert '"flower' not in pyproject


def test_public_backend_source_has_no_old_business_app_directories_in_c2(tmp_path):
    from tests.module_admission_fixtures import generate_core_profile, run_python
    profile = generate_core_profile(tmp_path / "C2")
    result = run_python(profile, 'import pytest\nraise SystemExit(pytest.main(["--noconftest", "-q", "-m", "no_db", "tests/test_celery_retirement.py"]))')
    assert result.returncode == 0, result.stdout + result.stderr
