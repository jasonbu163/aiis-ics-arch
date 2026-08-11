"""
File Path: /tools/lineage-mapping-studio/src-python/graph/io.py
Description: Input path resolution and file readers for lineage graph generation.
Main Features:
  - Keeps Studio defaults local to its inputs directory.
  - Allows explicit component-level source overrides.
  - Provides mtime signatures for watcher rebuilds.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUTS_DIR = TOOL_ROOT / "inputs"
DEFAULT_OUTPUT = DEFAULT_INPUTS_DIR / "lineage_graph.json"
DEFAULT_XLSX = DEFAULT_INPUTS_DIR / "plc_projection_mapping.xlsx"

V4_INPUT_FILES = {
    "frontend_sources": "frontend/frontend_sources.csv",
    "frontend_i18n_refs": "frontend/frontend_i18n_refs.csv",
    "frontend_component_refs": "frontend/frontend_component_refs.csv",
    "frontend_api_refs": "frontend/frontend_api_refs.csv",
    "frontend_api_uri_refs": "frontend/frontend_api_uri_refs.csv",
    "frontend_links": "frontend/frontend_links.csv",
    "backend_routes": "backend/backend_routes.csv",
    "backend_route_uri_refs": "backend/backend_route_uri_refs.csv",
    "backend_models": "backend/backend_models.csv",
    "backend_route_model_links": "backend/backend_route_model_links.csv",
    "table_schema": "database/table_schema.json",
}


@dataclass(frozen=True)
class InputSources:
    frontend_sources: Path
    frontend_i18n_refs: Path
    frontend_component_refs: Path
    frontend_api_refs: Path
    frontend_api_uri_refs: Path
    frontend_links: Path
    backend_routes: Path
    backend_route_uri_refs: Path
    backend_models: Path
    backend_route_model_links: Path
    table_schema: Path
    xlsx: Path | None
    default_inputs_dir: Path
    audit_outputs_dir: Path | None = None

    def watched_paths(self) -> list[Path]:
        paths = [
            self.frontend_sources,
            self.frontend_i18n_refs,
            self.frontend_component_refs,
            self.frontend_api_refs,
            self.frontend_api_uri_refs,
            self.frontend_links,
            self.backend_routes,
            self.backend_route_uri_refs,
            self.backend_models,
            self.backend_route_model_links,
            self.table_schema,
        ]
        if self.xlsx:
            paths.append(self.xlsx)
        return paths


def resolve_sources(
    inputs_dir: Path = DEFAULT_INPUTS_DIR,
    audit_outputs_dir: Path | None = None,
    frontend_dir: Path | None = None,
    backend_dir: Path | None = None,
    database_dir: Path | None = None,
    xlsx_path: Path | None = DEFAULT_XLSX,
) -> InputSources:
    """Resolve v4 inputs with component-level overrides.

    The Studio always has a local default `inputs/` set. Passing `audit_outputs_dir`
    or a more specific frontend/backend/database directory overrides only that
    component; other components still fall back to the Studio inputs directory.
    """
    frontend_base = frontend_dir or (audit_outputs_dir / "frontend" if audit_outputs_dir else inputs_dir / "frontend")
    backend_base = backend_dir or (audit_outputs_dir / "backend" if audit_outputs_dir else inputs_dir / "backend")
    database_base = database_dir or (audit_outputs_dir / "database" if audit_outputs_dir else inputs_dir / "database")
    return InputSources(
        frontend_sources=frontend_base / "frontend_sources.csv",
        frontend_i18n_refs=frontend_base / "frontend_i18n_refs.csv",
        frontend_component_refs=frontend_base / "frontend_component_refs.csv",
        frontend_api_refs=frontend_base / "frontend_api_refs.csv",
        frontend_api_uri_refs=frontend_base / "frontend_api_uri_refs.csv",
        frontend_links=frontend_base / "frontend_links.csv",
        backend_routes=backend_base / "backend_routes.csv",
        backend_route_uri_refs=backend_base / "backend_route_uri_refs.csv",
        backend_models=backend_base / "backend_models.csv",
        backend_route_model_links=backend_base / "backend_route_model_links.csv",
        table_schema=database_base / "table_schema.json",
        xlsx=xlsx_path,
        default_inputs_dir=inputs_dir,
        audit_outputs_dir=audit_outputs_dir,
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def mtime_signature(paths: list[Path]) -> tuple[tuple[str, float | None], ...]:
    signature: list[tuple[str, float | None]] = []
    for path in paths:
        signature.append((str(path), path.stat().st_mtime if path.exists() else None))
    return tuple(signature)
