"""No-DB checks for public Core frontend page-access defaults."""

import json
from pathlib import Path

import pytest


pytestmark = pytest.mark.no_db

FRONTEND_ROOT = Path(__file__).resolve().parents[2] / "frontend-js"


def _page_access_array(path: Path, key: str) -> list:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(key + "="):
            value = line.split("=", 1)[1].strip().strip("'")
            access = json.loads(value)
            assert isinstance(access, list), f"{path}: {key} must be a JSON array"
            return access
    raise AssertionError(f"{path} is missing {key}")


def test_public_frontend_templates_do_not_enable_project_page_ids():
    for env_name in (".env.example", ".env.docker.dev.example"):
        path = FRONTEND_ROOT / env_name
        assert not any(
            line.startswith("VITE_ROLE_PAGE_ACCESS_JSON=")
            for line in path.read_text(encoding="utf-8").splitlines()
        )
        for key in ("VITE_SUPERVISOR_PAGE_ACCESS_JSON", "VITE_OPERATOR_PAGE_ACCESS_JSON"):
            access = _page_access_array(path, key)
            assert access == []
            assert "monitor.realtime" not in access
