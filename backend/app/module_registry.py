"""
文件路径: /backend/app/module_registry.py
功能描述: 后端业务模块 manifest 组合根注册工具
主要功能:
    - 定义模块 manifest 元数据结构
    - 从已导入 app package 的直接子 package 受控发现 manifest
    - 为 Router、Projection、Alembic 和 schema maintenance 提供稳定注册结果

Registry 只读取静态 manifest、Router 定义和 model package。它不执行 DDL、
migration、seed、外部连接或后台 runtime；认证 user 与现场 control_agent 仍由
app.router 显式挂载。
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib import import_module
import importlib.resources
from importlib.util import find_spec
import pkgutil
import sys
from typing import Any, Literal

from fastapi import APIRouter

from common.log import log_event


@dataclass(frozen=True)
class ModuleManifest:
    """业务模块对组合根暴露的注册元数据。"""

    name: str
    enabled: bool = True
    order: int = 100
    routers: tuple[str, ...] = ()
    models_package: str | None = None
    permissions: tuple[str, ...] = ()


class ModuleRegistryError(RuntimeError):
    """模块发现、注册配置或导入失败。"""


DiscoveryStatus = Literal["loaded", "disabled", "skipped-no-manifest", "failed"]


@dataclass(frozen=True)
class ModuleDiscoveryDiagnostic:
    """一条不含敏感配置或业务 payload 的模块发现诊断。"""

    module: str
    stage: str
    status: DiscoveryStatus
    error_type: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        """Return a stable, redacted representation suitable for tests/logging."""
        return {
            "module": self.module,
            "stage": self.stage,
            "status": self.status,
            "error_type": self.error_type,
        }


_EXPLICIT_BOUNDARY_MODULES = frozenset({"user", "control_agent"})
_LAST_DISCOVERY_DIAGNOSTICS: tuple[ModuleDiscoveryDiagnostic, ...] = ()


def get_module_discovery_diagnostics() -> tuple[ModuleDiscoveryDiagnostic, ...]:
    """Return diagnostics from the most recent registry operation.

    Only stable module/stage/status/error type fields are retained. Exception text,
    configuration values, connection strings and request payloads are intentionally
    excluded from this surface.
    """
    return _LAST_DISCOVERY_DIAGNOSTICS


# Short alias for callers/tests that use the generic discovery wording.
get_discovery_diagnostics = get_module_discovery_diagnostics


def _record_diagnostic(
    diagnostics: list[ModuleDiscoveryDiagnostic],
    *,
    module: str,
    stage: str,
    status: DiscoveryStatus,
    error_type: str | None = None,
) -> None:
    diagnostic = ModuleDiscoveryDiagnostic(
        module=module,
        stage=stage,
        status=status,
        error_type=error_type,
    )
    diagnostics.append(diagnostic)

    if status == "failed":
        log_event(
            "ERROR",
            "backend.module_discovery_failed",
            module=module,
            stage=stage,
            error_type=error_type,
        )
    elif status == "skipped-no-manifest":
        log_event(
            "INFO",
            "backend.module_discovery_skipped",
            module=module,
            stage=stage,
            reason="no_manifest",
        )
    else:
        log_event(
            "INFO",
            "backend.module_discovery_loaded",
            module=module,
            stage=stage,
            status=status,
        )


def _publish_diagnostics(diagnostics: Iterable[ModuleDiscoveryDiagnostic]) -> None:
    global _LAST_DISCOVERY_DIAGNOSTICS
    _LAST_DISCOVERY_DIAGNOSTICS = tuple(diagnostics)


def _failed_error(*, module: str, stage: str, reason: str) -> ModuleRegistryError:
    """Create a locateable error without embedding arbitrary exception text."""
    error = ModuleRegistryError(f"module registry {stage} failed for {module}: {reason}")
    error.module = module  # type: ignore[attr-defined]
    error.stage = stage  # type: ignore[attr-defined]
    return error


def _iter_immediate_child_packages(app_package: Any) -> tuple[str, ...]:
    """Enumerate direct child packages of the imported ``app`` package only.

    ``pkgutil`` is the normal source and PyInstaller-compatible path. The resources
    and already-imported-package fallbacks keep discovery package-aware when a
    frozen importer does not expose ``iter_modules``; neither fallback scans an
    arbitrary filesystem directory.
    """
    package_name = getattr(app_package, "__name__", "app")
    package_paths = getattr(app_package, "__path__", None)
    if package_paths is None:
        raise _failed_error(module=package_name, stage="package", reason="app is not a package")

    candidates: list[str] = []
    pkgutil_error: Exception | None = None
    try:
        for module_info in pkgutil.iter_modules(package_paths):
            if module_info.ispkg:
                candidates.append(module_info.name)
    except Exception as exc:  # pragma: no cover - exercised by frozen/importer smoke
        pkgutil_error = exc

    # Some frozen importers expose package resources but not pkgutil's optional
    # iter_modules hook. ``Traversable`` keeps this tied to the imported package.
    try:
        package_files = importlib.resources.files(app_package)
        for child in package_files.iterdir():
            child_name = getattr(child, "name", "")
            if not child_name or child_name.startswith("_"):
                continue
            try:
                is_package = child.is_dir() and (
                    child.joinpath("__init__.py").is_file()
                    or (
                        (child_spec := find_spec(f"{package_name}.{child_name}")) is not None
                        and child_spec.submodule_search_locations is not None
                    )
                )
            except (AttributeError, ImportError, ModuleNotFoundError, OSError):
                is_package = False
            if is_package:
                if child_name not in candidates:
                    candidates.append(child_name)
    except Exception:
        # ``pkgutil`` or sys.modules may still provide the package view. A missing
        # resources reader is not itself a manifest failure.
        pass

    # PyInstaller may import collected children lazily. Any direct child package
    # already materialized in sys.modules remains a valid package-aware candidate.
    prefix = f"{package_name}."
    for imported_name, imported_module in tuple(sys.modules.items()):
        if not imported_name.startswith(prefix):
            continue
        child_name = imported_name[len(prefix) :]
        if "." in child_name or not child_name:
            continue
        if getattr(imported_module, "__path__", None) is not None:
            if child_name not in candidates:
                candidates.append(child_name)

    if not candidates:
        reason = "no immediate child packages"
        if pkgutil_error is not None:
            reason = f"package iterator {type(pkgutil_error).__name__}; {reason}"
        raise _failed_error(module=package_name, stage="package-discovery", reason=reason) from pkgutil_error

    return tuple(sorted(candidates))


def _load_manifest_optional(module_name: str) -> ModuleManifest | None:
    """Load one exact manifest, returning ``None`` only for no manifest."""
    module_path = f"app.{module_name}.manifest"
    try:
        module = import_module(module_path)
    except ModuleNotFoundError as exc:
        # Only the exact manifest module being absent means "not opted in". Any
        # dependency failure inside manifest.py must remain visible.
        if exc.name == module_path:
            return None
        raise _failed_error(
            module=module_name,
            stage="manifest-import",
            reason=f"internal import {type(exc).__name__}",
        ) from exc
    except Exception as exc:
        raise _failed_error(
            module=module_name,
            stage="manifest-import",
            reason=f"import {type(exc).__name__}",
        ) from exc

    sentinel = object()
    manifest = getattr(module, "manifest", sentinel)
    if manifest is sentinel:
        raise _failed_error(module=module_name, stage="manifest-export", reason="manifest export missing")
    if not isinstance(manifest, ModuleManifest):
        raise _failed_error(
            module=module_name,
            stage="manifest-export",
            reason="manifest export is not ModuleManifest",
        )
    if manifest.name != module_name:
        raise _failed_error(
            module=module_name,
            stage="manifest-name",
            reason="manifest name does not match package",
        )
    return manifest


def load_module_manifest(module_name: str) -> ModuleManifest:
    """Load one exact manifest; missing manifest is an explicit error here."""
    manifest = _load_manifest_optional(module_name)
    if manifest is None:
        raise _failed_error(
            module=module_name,
            stage="manifest-import",
            reason="manifest module missing",
        )
    return manifest


def _discover_module_manifests(
    module_names: Iterable[str] | None = None,
) -> tuple[ModuleManifest, ...]:
    diagnostics: list[ModuleDiscoveryDiagnostic] = []
    try:
        app_package = import_module("app")
        discovered_names = (
            tuple(module_names)
            if module_names is not None
            else _iter_immediate_child_packages(app_package)
        )
    except ModuleRegistryError as exc:
        _record_diagnostic(
            diagnostics,
            module="app",
            stage="package-discovery",
            status="failed",
            error_type=type(exc).__name__,
        )
        _publish_diagnostics(diagnostics)
        raise
    except Exception as exc:
        _record_diagnostic(
            diagnostics,
            module="app",
            stage="package-discovery",
            status="failed",
            error_type=type(exc).__name__,
        )
        _publish_diagnostics(diagnostics)
        raise _failed_error(
            module="app",
            stage="package-discovery",
            reason=f"import {type(exc).__name__}",
        ) from exc

    manifests: list[ModuleManifest] = []
    for module_name in discovered_names:
        if module_name in _EXPLICIT_BOUNDARY_MODULES:
            continue
        try:
            manifest = _load_manifest_optional(module_name)
        except ModuleRegistryError as exc:
            _record_diagnostic(
                diagnostics,
                module=module_name,
                stage=getattr(exc, "stage", "manifest"),
                status="failed",
                error_type=type(exc).__name__,
            )
            _publish_diagnostics(diagnostics)
            raise
        except Exception as exc:
            _record_diagnostic(
                diagnostics,
                module=module_name,
                stage="manifest",
                status="failed",
                error_type=type(exc).__name__,
            )
            _publish_diagnostics(diagnostics)
            raise _failed_error(
                module=module_name,
                stage="manifest",
                reason=f"load {type(exc).__name__}",
            ) from exc

        if manifest is None:
            _record_diagnostic(
                diagnostics,
                module=module_name,
                stage="manifest",
                status="skipped-no-manifest",
            )
            continue

        manifests.append(manifest)
        _record_diagnostic(
            diagnostics,
            module=module_name,
            stage="manifest",
            status="loaded" if manifest.enabled else "disabled",
        )

    by_name: dict[str, ModuleManifest] = {}
    for manifest in manifests:
        if manifest.name in by_name:
            _record_diagnostic(
                diagnostics,
                module=manifest.name,
                stage="duplicate-name",
                status="failed",
                error_type="DuplicateModuleName",
            )
            _publish_diagnostics(diagnostics)
            raise _failed_error(
                module=manifest.name,
                stage="duplicate-name",
                reason="manifest name is duplicated",
            )
        by_name[manifest.name] = manifest

    ordered = tuple(sorted(manifests, key=lambda manifest: (manifest.order, manifest.name)))
    _publish_diagnostics(diagnostics)
    return ordered


def discover_module_manifests(
    module_names: Iterable[str] | None = None,
) -> tuple[ModuleManifest, ...]:
    """Discover valid ordinary module manifests in deterministic order."""
    return _discover_module_manifests(module_names)


def get_module_manifests(module_names: Iterable[str] | None = None) -> tuple[ModuleManifest, ...]:
    """Return valid ordinary module manifests in ``(order, name)`` order."""
    return discover_module_manifests(module_names)


def get_enabled_module_manifests(
    module_names: Iterable[str] | None = None,
) -> tuple[ModuleManifest, ...]:
    """Return enabled manifests for ordinary Router and Projection discovery."""
    return tuple(manifest for manifest in get_module_manifests(module_names) if manifest.enabled)


def resolve_import_path(import_path: str) -> Any:
    """Resolve ``module:attribute`` import paths used by manifest metadata."""
    module_path, separator, attribute_path = import_path.partition(":")
    if not separator or not module_path or not attribute_path:
        raise ModuleRegistryError(f"Import path must use 'module:attribute': {import_path}")

    module = import_module(module_path)
    target: Any = module
    for attribute in attribute_path.split("."):
        target = getattr(target, attribute)
    return target


def include_module_routers(
    parent_router: APIRouter,
    manifests: Iterable[ModuleManifest] | None = None,
) -> list[str]:
    """Include enabled manifest routers in the ordinary business router."""
    loaded_router_paths: list[str] = []
    selected_manifests = (
        tuple(manifest for manifest in manifests if manifest.enabled)
        if manifests is not None
        else get_enabled_module_manifests()
    )
    for manifest in selected_manifests:
        for router_path in manifest.routers:
            try:
                module_router = resolve_import_path(router_path)
            except Exception as exc:
                _record_runtime_failure(
                    module=manifest.name,
                    stage="router-import",
                    error_type=type(exc).__name__,
                )
                raise _failed_error(
                    module=manifest.name,
                    stage="router-import",
                    reason="router import failed",
                ) from exc
            if not isinstance(module_router, APIRouter):
                _record_runtime_failure(
                    module=manifest.name,
                    stage="router-export",
                    error_type="InvalidRouterExport",
                )
                raise _failed_error(
                    module=manifest.name,
                    stage="router-export",
                    reason="router path did not resolve to APIRouter",
                )
            parent_router.include_router(module_router)
            loaded_router_paths.append(router_path)
    return loaded_router_paths


def import_model_packages(
    manifests: Iterable[ModuleManifest] | None = None,
) -> list[str]:
    """Import all valid manifest model packages, including disabled modules.

    This only makes SQLAlchemy model metadata visible. It does not create tables,
    invoke Alembic, seed data or connect to a database.
    """
    imported_packages: list[str] = []
    selected_manifests = tuple(manifests) if manifests is not None else get_module_manifests()
    for manifest in selected_manifests:
        if not manifest.models_package:
            continue
        try:
            import_module(manifest.models_package)
        except Exception as exc:
            _record_runtime_failure(
                module=manifest.name,
                stage="models-import",
                error_type=type(exc).__name__,
            )
            raise _failed_error(
                module=manifest.name,
                stage="models-import",
                reason="model package import failed",
            ) from exc
        imported_packages.append(manifest.models_package)
    return imported_packages


def _record_runtime_failure(*, module: str, stage: str, error_type: str) -> None:
    diagnostics = list(get_module_discovery_diagnostics())
    _record_diagnostic(
        diagnostics,
        module=module,
        stage=stage,
        status="failed",
        error_type=error_type,
    )
    _publish_diagnostics(diagnostics)
