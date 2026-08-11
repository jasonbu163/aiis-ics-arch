"""
File Path: /tools/lineage-audit/src-python/builders/backend_audit.py
Description: Backend inventory and link builders for lineage audit v4.
Main Features:
    - Builds exhaustive FastAPI route and SQLAlchemy model inventories.
    - Builds Route -> Model -> Table evidence links without filtering nodes.
"""
from __future__ import annotations

from typing import Any, Callable

from audit.common import normalize_path


def uri_key(method: str, uri: str) -> str:
    normalized_uri = normalize_path(uri)
    return f"{method.upper()} {normalized_uri}"


def build_backend_outputs(
    backend_routes: list[Any],
    class_to_model: dict[str, Any],
    add_row_ids: Callable[[list[dict[str, Any]], str, list[str]], list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    route_rows: list[dict[str, Any]] = []
    route_uri_rows: list[dict[str, Any]] = []
    route_model_rows: list[dict[str, Any]] = []

    for route in backend_routes:
        route_id = f"{route.method} {route.path}"
        normalized_uri = normalize_path(route.path)
        route_rows.append(
            {
                "route_id": route_id,
                "method": route.method,
                "backend_route": route.path,
                "backend_module": route.module,
                "backend_function": route.function,
                "backend_api_file": route.api_file,
                "router_var": route.router_var,
                "router_tags": ";".join(route.router_tags),
                "tag_evidence_file": route.tag_evidence_file,
                "tag_evidence_symbol": route.tag_evidence_symbol,
                "tag_evidence_state": route.tag_evidence_state,
                "called_symbols": ";".join(route.called_symbols),
                "confidence": route.confidence,
            }
        )
        route_uri_rows.append(
            {
                "route_id": route_id,
                "method": route.method,
                "normalized_uri": normalized_uri,
                "uri_key": uri_key(route.method, route.path),
                "backend_route": route.path,
                "backend_module": route.module,
                "backend_function": route.function,
                "backend_api_file": route.api_file,
                "confidence": route.confidence,
            }
        )

        model_refs = route.model_refs or (None,)
        for model_ref in model_refs:
            route_model_rows.append(
                {
                    "route_id": route_id,
                    "method": route.method,
                    "backend_route": route.path,
                    "backend_module": route.module,
                    "backend_function": route.function,
                    "backend_api_file": route.api_file,
                    "router_tags": ";".join(route.router_tags),
                    "tag_evidence_file": route.tag_evidence_file,
                    "tag_evidence_symbol": route.tag_evidence_symbol,
                    "tag_evidence_state": route.tag_evidence_state,
                    "model_class": model_ref.model_class if model_ref else "",
                    "model_file": model_ref.model_file if model_ref else "",
                    "table_name": model_ref.table_name if model_ref else "",
                    "evidence_type": model_ref.evidence_type if model_ref else "",
                    "evidence_file": model_ref.evidence_file if model_ref else "",
                    "evidence_symbol": model_ref.evidence_symbol if model_ref else "",
                    "confidence": model_ref.confidence if model_ref else "manual_review",
                }
            )

    model_rows = [
        {
            "model_id": model.class_name,
            "model_class": model.class_name,
            "model_file": model.model_file,
            "backend_module": model.module,
            "table_name": model.table_name,
        }
        for model in sorted(class_to_model.values(), key=lambda item: (item.module, item.class_name))
    ]

    return {
        "backend_routes": add_row_ids(route_rows, "backend_routes", ["method", "backend_route", "backend_function"]),
        "backend_route_uri_refs": add_row_ids(
            route_uri_rows,
            "backend_route_uri_refs",
            ["route_id", "method", "normalized_uri"],
        ),
        "backend_models": add_row_ids(model_rows, "backend_models", ["model_class", "table_name", "model_file"]),
        "backend_route_model_links": add_row_ids(
            route_model_rows,
            "backend_route_model_links",
            ["method", "backend_route", "backend_function", "model_class", "table_name"],
        ),
    }
