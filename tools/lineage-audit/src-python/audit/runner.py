"""
File Path: /tools/lineage-audit/src-python/audit/runner.py
Description: Audit orchestration for frontend/backend scanners.
Main Features:
    - Builds the aggregate AuditState.
    - Keeps CLI separate from scanner orchestration.
"""
from __future__ import annotations

from pathlib import Path

from scanners.backend import build_route_matches, parse_backend_function_index, parse_backend_routes, parse_model_tables
from scanners.frontend import (
    list_frontend_api_files,
    list_frontend_source_files,
    parse_component_links,
    parse_frontend_api_file,
    parse_frontend_manifest_routes,
    parse_frontend_routes,
    parse_frontend_usages,
)
from .models import AuditState

def audit(frontend_root: Path, backend_root: Path) -> AuditState:
    state = AuditState()
    router_path = frontend_root / "router" / "index.js"
    state.frontend_routes = [
        *parse_frontend_routes(router_path),
        *parse_frontend_manifest_routes(frontend_root),
    ]
    for api_file in list_frontend_api_files(frontend_root):
        state.frontend_apis.extend(parse_frontend_api_file(api_file, frontend_root))
    state.frontend_usages, state.mock_findings = parse_frontend_usages(frontend_root, state.frontend_routes)
    state.component_links = parse_component_links(frontend_root, state.frontend_routes)
    state.table_by_module, state.class_to_model = parse_model_tables(backend_root)
    function_index = parse_backend_function_index(backend_root)
    state.backend_routes = parse_backend_routes(backend_root, state.class_to_model, function_index)
    state.route_matches = build_route_matches(state.frontend_apis, state.backend_routes)
    return state


def list_frontend_sources(frontend_root: Path) -> list[Path]:
    return list_frontend_source_files(frontend_root)
