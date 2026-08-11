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


def test_public_backend_source_has_no_old_business_app_directories():
    app_dir = BACKEND_ROOT / "app"
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
