"""No-DB checks for public Core frontend page-access defaults."""

import json
from pathlib import Path

import pytest


pytestmark = pytest.mark.no_db

FRONTEND_ROOT = Path(__file__).resolve().parents[2] / "frontend-js"


def _role_page_access(path: Path) -> dict:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("VITE_ROLE_PAGE_ACCESS_JSON="):
            value = line.split("=", 1)[1].strip().strip("'")
            return json.loads(value)
    raise AssertionError(f"{path} is missing VITE_ROLE_PAGE_ACCESS_JSON")


def test_public_frontend_templates_do_not_enable_project_page_ids():
    for env_name in (".env.example", ".env.docker.dev.example"):
        access = _role_page_access(FRONTEND_ROOT / env_name)
        assert access == {}
        assert "monitor.realtime" not in str(access)
