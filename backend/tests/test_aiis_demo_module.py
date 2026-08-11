"""
文件路径: /backend/tests/test_aiis_demo_module.py
功能描述: B11.2 AIIS Demo 参考模块合同测试
主要功能:
    - 锁定默认 disabled manifest 与受控 discovery 语义
    - 验证隔离 enabled override 的 ping 响应合同
    - 验证空模型包、无副作用导入、Projection 排除与文档结构
"""
from __future__ import annotations

import ast
import importlib
from dataclasses import replace
from pathlib import Path

import httpx
import pytest
from fastapi import APIRouter, FastAPI

from app.aiis_demo.manifest import manifest
from app.module_registry import (
    ModuleManifest,
    get_enabled_module_manifests,
    get_module_manifests,
    include_module_routers,
)
from core.registrar import create_app
from database import Base
from projection.registry import build_projection_registry


pytestmark = pytest.mark.no_db

MODULE_DIR = Path(__file__).resolve().parents[1] / "app" / "aiis_demo"
EXPECTED_FILES = {
    "__init__.py",
    "manifest.py",
    "README.md",
    "README.zh-CN.md",
    "api/__init__.py",
    "api/routes.py",
    "crud/__init__.py",
    "mocks/__init__.py",
    "models/__init__.py",
    "schemas/__init__.py",
    "schemas/ping.py",
    "seeds/__init__.py",
    "services/__init__.py",
    "services/async_ping.py",
}
EMPTY_PACKAGES = ("crud", "mocks", "models", "seeds")
FORBIDDEN_IMPORT_PREFIXES = (
    "sqlalchemy",
    "database",
    "alembic",
    "settings",
    "control_agent",
    "plc",
    "threading",
    "asyncio",
    "subprocess",
    "socket",
    "requests",
    "httpx",
)


def test_aiis_demo_has_exact_reference_skeleton():
    """The reference package has only the approved standard files."""
    actual_files = {
        path.relative_to(MODULE_DIR).as_posix()
        for path in MODULE_DIR.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }

    assert actual_files == EXPECTED_FILES
    assert (MODULE_DIR / "manifest.py").is_file()


def test_aiis_demo_manifest_is_exact_and_default_disabled():
    """Manifest metadata is fixed and does not enable the real app route."""
    assert manifest == ModuleManifest(
        name="aiis_demo",
        enabled=False,
        order=900,
        routers=("app.aiis_demo.api.routes:router",),
        models_package="app.aiis_demo.models",
        permissions=("aiis_demo",),
    )

    discovered = {item.name: item for item in get_module_manifests()}
    enabled = {item.name for item in get_enabled_module_manifests()}

    assert discovered["aiis_demo"] == manifest
    assert "aiis_demo" not in enabled


def test_default_app_openapi_and_projection_exclude_aiis_demo():
    """Default composition excludes the disabled route and Projection owner."""
    schema = create_app(testing=True).openapi()
    assert "/api/v1/aiis-demo/ping" not in schema["paths"]

    from app.router import router as application_router

    assert "/aiis-demo/ping" not in {route.path for route in application_router.routes}

    projection_registry = build_projection_registry()
    assert all(handler.owner_module != "aiis_demo" for handler in projection_registry.handlers)
    assert not list((MODULE_DIR / "services").glob("sync_*.py"))


@pytest.mark.asyncio
async def test_isolated_enabled_override_exposes_ping_without_registry_edit():
    """An immutable in-memory manifest copy can expose the route in isolation."""
    isolated_router = APIRouter()
    enabled_copy = replace(manifest, enabled=True)

    assert include_module_routers(isolated_router, (enabled_copy,)) == list(manifest.routers)

    app = FastAPI()
    app.include_router(isolated_router, prefix="/api/v1")
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/v1/aiis-demo/ping")

    assert response.status_code == 200
    assert response.json() == {
        "code": 200,
        "message": "success",
        "data": {"module": "aiis_demo", "status": "ok", "reference": True},
    }
    assert manifest.enabled is False


def test_empty_models_package_does_not_change_metadata():
    """Importing the empty models package leaves SQLAlchemy metadata unchanged."""
    before = set(Base.metadata.tables)
    importlib.import_module("app.aiis_demo.models")
    after = set(Base.metadata.tables)

    assert after == before
    assert not any(table_name.startswith("aiis_demo") for table_name in after)


def test_module_python_imports_have_no_db_or_external_side_effect_dependencies():
    """Non-document Python files stay within the static reference boundary."""
    for source_file in MODULE_DIR.rglob("*.py"):
        tree = ast.parse(source_file.read_text(encoding="utf-8"))
        imported_modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)

        forbidden = {
            imported
            for imported in imported_modules
            if any(
                imported == prefix or imported.startswith(f"{prefix}.")
                for prefix in FORBIDDEN_IMPORT_PREFIXES
            )
        }
        assert not forbidden, f"{source_file} imports forbidden dependencies: {sorted(forbidden)}"


def test_empty_placeholder_packages_contain_no_fake_implementation():
    """Empty package entries contain only their package docstring."""
    for package_name in EMPTY_PACKAGES:
        source = (MODULE_DIR / package_name / "__init__.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert len(tree.body) == 1
        assert isinstance(tree.body[0], ast.Expr)
        assert isinstance(tree.body[0].value, ast.Constant)
        assert isinstance(tree.body[0].value.value, str)


def test_module_readmes_document_reference_copy_permission_migration_and_restart_contract():
    """Both README languages state the same non-business lifecycle boundaries."""
    english = (MODULE_DIR / "README.md").read_text(encoding="utf-8").lower()
    chinese = (MODULE_DIR / "README.zh-CN.md").read_text(encoding="utf-8").lower()

    for content in (english, chinese):
        assert "reference" in content
        assert "permission" in content
        assert "migration" in content
        assert "restart" in content
        assert "hot unload" in content
        assert "enabled" in content
        assert "copy" in content or "复制" in content
        assert "rename" in content or "改名" in content
