"""
File Path: /tools/lineage-audit/src-python/builders/frontend_audit.py
Description: Frontend inventory and link builders for lineage audit v4.
Main Features:
    - Builds frontend source, component, API, i18n and link CSV rows.
    - Keeps node inventory generation separate from graph link evidence.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

from audit.common import normalize_path


I18N_CALL_PATTERN = re.compile(
    r"(?:\$t|\bt|i18n\.t)\(\s*['\"]([^'\"]+)['\"]",
    re.MULTILINE,
)


def uri_key(method: str, uri: str) -> str:
    normalized_uri = normalize_path(uri)
    return f"{method.upper()} {normalized_uri}"


def flatten_locale_payload(payload: Any, prefix: str = "") -> list[tuple[str, str]]:
    if isinstance(payload, dict):
        rows: list[tuple[str, str]] = []
        for key, value in payload.items():
            next_key = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(flatten_locale_payload(value, next_key))
        return rows
    if isinstance(payload, list):
        return [(prefix, json.dumps(payload, ensure_ascii=False))]
    return [(prefix, "" if payload is None else str(payload))]


def read_locale_definitions(frontend_root: Path, rel_fn: Callable[[Path], str]) -> list[dict[str, Any]]:
    locales_root = frontend_root / "locales"
    rows: list[dict[str, Any]] = []
    if not locales_root.exists():
        return rows

    for path in sorted(locales_root.glob("*/*.json")):
        locale = path.parent.name
        namespace = path.stem
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for key, value in flatten_locale_payload(payload):
            if not key:
                continue
            rows.append(
                {
                    "record_kind": "definition",
                    "locale_file": rel_fn(path),
                    "locale": locale,
                    "i18n_key": f"{namespace}.{key}",
                    "value": value,
                    "source_file": "",
                    "source_kind": "",
                    "route_path": "",
                    "route_name": "",
                    "evidence_symbol": "",
                }
            )
    return rows


def read_i18n_references(
    frontend_root: Path,
    source_paths: list[Path],
    routes: list[Any],
    rel_fn: Callable[[Path], str],
    classify_source: Callable[[Path], str],
    find_route: Callable[[str, list[Any]], tuple[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in source_paths:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        source_file = rel_fn(path)
        route_path, route_name = find_route(source_file, routes)
        for match in I18N_CALL_PATTERN.finditer(text):
            rows.append(
                {
                    "record_kind": "reference",
                    "locale_file": "",
                    "locale": "",
                    "i18n_key": match.group(1),
                    "value": "",
                    "source_file": source_file,
                    "source_kind": classify_source(path),
                    "route_path": route_path,
                    "route_name": route_name,
                    "evidence_symbol": match.group(0),
                }
            )
    return rows


def build_frontend_outputs(
    frontend_root: Path,
    routes: list[Any],
    apis: list[Any],
    usages: list[Any],
    mock_findings: list[Any],
    rel_fn: Callable[[Path], str],
    classify_source: Callable[[Path], str],
    find_route: Callable[[str, list[Any]], tuple[str, str]],
    list_sources: Callable[[Path], list[Path]],
    add_row_ids: Callable[[list[dict[str, Any]], str, list[str]], list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    source_paths = list_sources(frontend_root)
    mock_count_by_source: dict[str, int] = {}
    for finding in mock_findings:
        mock_count_by_source[finding.source_file] = mock_count_by_source.get(finding.source_file, 0) + 1

    source_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    source_by_rel = {rel_fn(path): path for path in source_paths}
    for path in source_paths:
        source_file = rel_fn(path)
        route_path, route_name = find_route(source_file, routes)
        source_kind = classify_source(path)
        source_rows.append(
            {
                "source_file": source_file,
                "source_kind": source_kind,
                "route_path": route_path,
                "route_name": route_name,
                "mock_finding_count": mock_count_by_source.get(source_file, 0),
            }
        )
        component_rows.append(
            {
                "component_id": source_file,
                "source_file": source_file,
                "source_kind": source_kind,
                "route_path": route_path,
                "route_name": route_name,
            }
        )

    mock_rows: list[dict[str, Any]] = []
    for finding in mock_findings:
        source_path = source_by_rel.get(finding.source_file)
        route_path, route_name = find_route(finding.source_file, routes)
        mock_rows.append(
            {
                "source_file": finding.source_file,
                "source_kind": classify_source(source_path) if source_path else "",
                "route_path": route_path,
                "route_name": route_name,
                "line": finding.line,
                "reason": finding.reason,
                "snippet": finding.snippet,
            }
        )

    api_rows = [
        {
            "api_id": f"{api.module}.{api.function}",
            "api_module": api.module,
            "api_function": api.function,
            "api_file": api.api_file,
            "method": api.method,
            "frontend_api_path": api.path,
            "raw_path_expr": api.raw_path_expr,
            "confidence": api.confidence,
        }
        for api in apis
    ]
    api_uri_rows = [
        {
            "api_id": f"{api.module}.{api.function}",
            "method": api.method,
            "normalized_uri": normalize_path(api.path),
            "uri_key": uri_key(api.method, api.path),
            "frontend_api_path": api.path,
            "raw_path_expr": api.raw_path_expr,
            "api_file": api.api_file,
            "confidence": api.confidence,
        }
        for api in apis
    ]

    i18n_rows = [
        *read_locale_definitions(frontend_root, rel_fn),
        *read_i18n_references(frontend_root, source_paths, routes, rel_fn, classify_source, find_route),
    ]

    usage_rows: list[dict[str, Any]] = []
    for usage in usages:
        usage_rows.append(
            {
                "from_kind": "Component",
                "from_id": usage.source_file,
                "to_kind": "API",
                "to_id": f"{usage.api_module}.{usage.api_function}",
                "edge_type": "component_uses_api",
                "source_file": usage.source_file,
                "evidence_symbol": usage.api_function,
                "confidence": "confirmed",
            }
        )

    i18n_definition_keys = {row["i18n_key"] for row in i18n_rows if row["record_kind"] == "definition"}
    for row in i18n_rows:
        if row["record_kind"] == "definition":
            usage_rows.append(
                {
                    "from_kind": "LocaleFile",
                    "from_id": row["locale_file"],
                    "to_kind": "I18nKey",
                    "to_id": row["i18n_key"],
                    "edge_type": "defines_i18n_key",
                    "source_file": row["locale_file"],
                    "evidence_symbol": row["locale"],
                    "confidence": "confirmed",
                }
            )
        elif row["record_kind"] == "reference":
            usage_rows.append(
                {
                    "from_kind": "I18nKey",
                    "from_id": row["i18n_key"],
                    "to_kind": "Component",
                    "to_id": row["source_file"],
                    "edge_type": "component_refs_i18n_key",
                    "source_file": row["source_file"],
                    "evidence_symbol": row["evidence_symbol"],
                    "confidence": "confirmed" if row["i18n_key"] in i18n_definition_keys else "manual_review",
                }
            )

    return {
        "frontend_sources": add_row_ids(source_rows, "frontend_sources", ["source_file"]),
        "frontend_component_refs": add_row_ids(component_rows, "frontend_component_refs", ["component_id"]),
        "frontend_api_refs": add_row_ids(api_rows, "frontend_api_refs", ["api_id", "frontend_api_path"]),
        "frontend_api_uri_refs": add_row_ids(
            api_uri_rows,
            "frontend_api_uri_refs",
            ["api_id", "method", "normalized_uri"],
        ),
        "frontend_i18n_refs": add_row_ids(
            i18n_rows,
            "frontend_i18n_refs",
            ["record_kind", "locale_file", "locale", "i18n_key", "source_file"],
        ),
        "frontend_mock_findings": add_row_ids(
            mock_rows,
            "frontend_mock_findings",
            ["source_file", "line", "reason", "snippet"],
        ),
        "frontend_links": add_row_ids(
            usage_rows,
            "frontend_links",
            ["from_kind", "from_id", "to_kind", "to_id", "edge_type", "source_file"],
        ),
    }
