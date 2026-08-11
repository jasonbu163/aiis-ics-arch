"""No-DB checks for the Core backend local and packaged entry points."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

import main as production_main
import run as development_run
from settings import resolve_env_file


pytestmark = pytest.mark.no_db

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_source_runtime_env_is_backend_root(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert resolve_env_file() == BACKEND_ROOT / ".env"


def test_packaged_runtime_env_is_beside_executable(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    executable = tmp_path / "aiis-ics-architecture-backend"
    monkeypatch.setattr(sys, "executable", str(executable))
    assert resolve_env_file() == tmp_path / ".env"


def test_development_entry_enables_reload(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        development_run.uvicorn,
        "run",
        lambda app, **kwargs: captured.update(app=app, **kwargs),
    )
    development_run.main()
    assert captured["app"] == "main:app"
    assert captured["reload"] is True
    assert captured["workers"] == 1


def test_production_entry_disables_reload(monkeypatch):
    captured = {}
    monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(production_main.settings, "BACKEND_WORKERS", 2)
    monkeypatch.setattr(
        production_main.uvicorn,
        "run",
        lambda app, **kwargs: captured.update(app=app, **kwargs),
    )
    production_main.run_server()
    assert captured["app"] == "main:app"
    assert captured["reload"] is False
    assert captured["workers"] == 2


def test_backend_build_collects_manifest_and_database_driver_surfaces():
    source = (BACKEND_ROOT / "build.py").read_text(encoding="utf-8")
    assert "--collect-submodules=app" in source
    for driver in ("aiomysql", "pymysql", "asyncpg", "psycopg2"):
        assert f"--hidden-import={driver}" in source
