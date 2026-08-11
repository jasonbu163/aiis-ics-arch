"""
File Path: /tools/lineage-mapping-studio/src-python/graph/builder.py
Description: Build lineage graph JSON from resolved v4 input sources.
Main Features:
  - Builds LocaleFile -> I18nKey -> Component -> API -> Route -> Model -> Table -> Field -> PLC.
  - Keeps node inventory independent from link evidence.
  - Preserves Studio graph JSON contract.
"""
from __future__ import annotations

import time
from typing import Any

from .io import InputSources, read_csv, read_json
from .models import GraphEdge, GraphNode, add_edge, add_node, node_id, node_to_dict, value
from .workbook import read_workbook_bindings


def file_label(path: str) -> str:
    parts = path.split("/")
    return "/".join(parts[-2:]) if len(parts) >= 2 else path


def api_name(row: dict[str, str]) -> str:
    return f"{value(row.get('api_module'))}.{value(row.get('api_function'))}".strip(".")


def route_label(row: dict[str, str]) -> str:
    method = value(row.get("method"))
    path = value(row.get("backend_route") or row.get("frontend_api_path"))
    return f"{method} {path}".strip()


def i18n_subtitle(values: dict[str, str]) -> str:
    zh = values.get("zh-CN") or values.get("zh")
    en = values.get("en-US") or values.get("en")
    parts = []
    if zh:
        parts.append(f"中: {zh}")
    if en:
        parts.append(f"EN: {en}")
    if not parts:
        for locale, text in sorted(values.items())[:2]:
            parts.append(f"{locale}: {text}")
    return " / ".join(parts)


def plc_subtitle(point: dict[str, Any]) -> str:
    source_name = value(point.get("source_name"))
    address = f"DB{value(point.get('db_number'))} {value(point.get('plc_data_type'))} {value(point.get('offset'))}".strip()
    if source_name and address:
        return f"{source_name} · {address}"
    return source_name or address


def add_v4_frontend_nodes(
    frontend_component_refs: list[dict[str, str]],
    frontend_api_refs: list[dict[str, str]],
    frontend_i18n_refs: list[dict[str, str]],
    nodes: dict[str, GraphNode],
) -> None:
    i18n_values: dict[str, dict[str, str]] = {}
    for row in frontend_i18n_refs:
        if value(row.get("record_kind")) != "definition":
            continue
        i18n_key = value(row.get("i18n_key"))
        locale = value(row.get("locale"))
        text_value = value(row.get("value"))
        if i18n_key and locale and text_value:
            i18n_values.setdefault(i18n_key, {})[locale] = text_value

    for row in frontend_i18n_refs:
        row_id = value(row.get("row_id"))
        record_kind = value(row.get("record_kind"))
        i18n_key = value(row.get("i18n_key"))
        locale_file = value(row.get("locale_file"))
        if record_kind == "definition" and locale_file:
            locale_id = node_id("locale", locale_file)
            add_node(nodes, GraphNode(locale_id, "locale", file_label(locale_file), value(row.get("locale")), row_id))
        if i18n_key:
            i18n_id = node_id("i18n", i18n_key)
            subtitle = i18n_subtitle(i18n_values.get(i18n_key, {})) or value(row.get("value") or row.get("source_file"))
            add_node(nodes, GraphNode(i18n_id, "i18n", i18n_key, subtitle[:160], row_id))

    for row in frontend_component_refs:
        component_id_raw = value(row.get("component_id") or row.get("source_file"))
        if not component_id_raw:
            continue
        component_id = node_id("component", component_id_raw)
        add_node(
            nodes,
            GraphNode(
                component_id,
                "component",
                file_label(component_id_raw),
                value(row.get("route_path") or row.get("source_kind")),
                value(row.get("row_id")),
            ),
        )

    for row in frontend_api_refs:
        api_id_raw = value(row.get("api_id") or api_name(row))
        if not api_id_raw:
            continue
        api_id = node_id("api", api_id_raw)
        add_node(nodes, GraphNode(api_id, "api", api_id_raw, value(row.get("frontend_api_path")), value(row.get("row_id"))))


def add_v4_backend_nodes(
    backend_routes: list[dict[str, str]],
    backend_models: list[dict[str, str]],
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
) -> None:
    for row in backend_routes:
        route_id_raw = value(row.get("route_id") or route_label(row))
        if not route_id_raw:
            continue
        route_id = node_id("route", route_id_raw)
        add_node(nodes, GraphNode(route_id, "route", route_id_raw, value(row.get("backend_function")), value(row.get("row_id"))))

    for row in backend_models:
        model_class = value(row.get("model_class") or row.get("model_id"))
        if not model_class:
            continue
        model_id = node_id("model", model_class)
        table_name = value(row.get("table_name"))
        add_node(nodes, GraphNode(model_id, "model", model_class, value(row.get("backend_module") or row.get("model_file")), value(row.get("row_id"))))
        if table_name:
            table_id = node_id("table", table_name)
            add_node(nodes, GraphNode(table_id, "table", table_name, value(row.get("model_file") or row.get("backend_module")), value(row.get("row_id"))))
            add_edge(edges, model_id, table_id, "maps_to_table", value(row.get("row_id")))


def add_v4_frontend_links(rows: list[dict[str, str]], edges: dict[str, GraphEdge]) -> None:
    kind_map = {
        "LocaleFile": "locale",
        "I18nKey": "i18n",
        "Component": "component",
        "API": "api",
    }
    for row in rows:
        source_kind = kind_map.get(value(row.get("from_kind")))
        target_kind = kind_map.get(value(row.get("to_kind")))
        source_id_raw = value(row.get("from_id"))
        target_id_raw = value(row.get("to_id"))
        if not source_kind or not target_kind or not source_id_raw or not target_id_raw:
            continue
        add_edge(
            edges,
            node_id(source_kind, source_id_raw),
            node_id(target_kind, target_id_raw),
            value(row.get("edge_type")) or "link",
            value(row.get("row_id")),
        )


def add_uri_links(
    frontend_api_uri_refs: list[dict[str, str]],
    backend_route_uri_refs: list[dict[str, str]],
    edges: dict[str, GraphEdge],
) -> int:
    routes_by_uri_key: dict[str, list[dict[str, str]]] = {}
    for row in backend_route_uri_refs:
        uri_key = value(row.get("uri_key"))
        route_id_raw = value(row.get("route_id"))
        if not uri_key or not route_id_raw:
            continue
        routes_by_uri_key.setdefault(uri_key, []).append(row)

    match_count = 0
    for row in frontend_api_uri_refs:
        uri_key = value(row.get("uri_key"))
        api_id_raw = value(row.get("api_id"))
        if not uri_key or not api_id_raw:
            continue
        for route in routes_by_uri_key.get(uri_key, []):
            route_id_raw = value(route.get("route_id"))
            if not route_id_raw:
                continue
            add_edge(
                edges,
                node_id("api", api_id_raw),
                node_id("route", route_id_raw),
                "matches_route",
                "|".join(item for item in [value(row.get("row_id")), value(route.get("row_id"))] if item) or uri_key,
            )
            match_count += 1
    return match_count


def add_v4_backend_links(rows: list[dict[str, str]], nodes: dict[str, GraphNode], edges: dict[str, GraphEdge]) -> None:
    for row in rows:
        route_id_raw = value(row.get("route_id") or route_label(row))
        if not route_id_raw:
            continue
        route_id = node_id("route", route_id_raw)
        model_class = value(row.get("model_class"))
        if model_class:
            model_id = node_id("model", model_class)
            add_node(nodes, GraphNode(model_id, "model", model_class, value(row.get("evidence_type")), value(row.get("row_id"))))
            add_edge(edges, route_id, model_id, "uses_model", value(row.get("row_id")))
            table_name = value(row.get("table_name"))
            if table_name:
                table_id = node_id("table", table_name)
                add_node(nodes, GraphNode(table_id, "table", table_name, value(row.get("model_file") or row.get("backend_module")), value(row.get("row_id"))))
                add_edge(edges, model_id, table_id, "maps_to_table", value(row.get("row_id")))


def add_schema_fields(table_schema: dict[str, Any], nodes: dict[str, GraphNode], edges: dict[str, GraphEdge]) -> list[dict[str, Any]]:
    schema_tables = table_schema.get("tables") if isinstance(table_schema, dict) else []
    if not isinstance(schema_tables, list):
        return []
    for table in schema_tables:
        if not isinstance(table, dict):
            continue
        table_name = value(table.get("table_name") or table.get("table"))
        table_id = node_id("table", table_name)
        add_node(nodes, GraphNode(table_id, "table", table_name, "business table", "table_schema.json"))
        for column in table.get("columns") or []:
            if not isinstance(column, dict):
                continue
            field_name = value(column.get("field_name") or column.get("name"))
            if not field_name:
                continue
            field_id = node_id("field", f"{table_name}.{field_name}")
            add_node(nodes, GraphNode(field_id, "field", field_name, value(column.get("field_type") or column.get("data_type")), table_name))
            add_edge(edges, table_id, field_id, "has_field", "table_schema.json")
    return schema_tables


def add_workbook_bindings(
    bindings: list[dict[str, Any]],
    workbook_points: list[dict[str, Any]],
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
) -> None:
    point_by_name = {value(point.get("point_name")): point for point in workbook_points if value(point.get("point_name"))}
    for binding in bindings:
        table_name = value(binding.get("table_name"))
        field_name = value(binding.get("field_name"))
        point_name = value(binding.get("point_name"))
        if not table_name or not field_name:
            continue
        table_id = node_id("table", table_name)
        field_id = node_id("field", f"{table_name}.{field_name}")
        add_node(nodes, GraphNode(table_id, "table", table_name, "xlsx target", "plc_projection_mapping.xlsx"))
        add_node(nodes, GraphNode(field_id, "field", field_name, value(binding.get("field_type")), "plc_projection_mapping.xlsx"))
        add_edge(edges, table_id, field_id, "has_field", "plc_projection_mapping.xlsx")
        if point_name:
            point = point_by_name.get(point_name, {})
            plc_id = node_id("plc", point_name)
            add_node(
                nodes,
                GraphNode(
                    plc_id,
                    "plc",
                    point_name,
                    plc_subtitle(
                        {
                            "source_name": binding.get("source_name") or point.get("source_name"),
                            "db_number": binding.get("db_number") or point.get("db_number"),
                            "plc_data_type": binding.get("plc_data_type") or point.get("plc_data_type"),
                            "offset": binding.get("offset") or point.get("offset"),
                        }
                    ),
                    value(binding.get("group_name") or point.get("group_name")),
                ),
            )
            add_edge(edges, field_id, plc_id, "bound_to_plc", "plc_projection_mapping.xlsx")

    for point in workbook_points:
        point_name = value(point.get("point_name"))
        if not point_name:
            continue
        plc_id = node_id("plc", point_name)
        add_node(nodes, GraphNode(plc_id, "plc", point_name, plc_subtitle(point), value(point.get("group_name"))))


def build_graph(sources: InputSources) -> dict[str, Any]:
    frontend_sources = read_csv(sources.frontend_sources)
    frontend_i18n_refs = read_csv(sources.frontend_i18n_refs)
    frontend_component_refs = read_csv(sources.frontend_component_refs)
    frontend_api_refs = read_csv(sources.frontend_api_refs)
    frontend_api_uri_refs = read_csv(sources.frontend_api_uri_refs)
    frontend_links = read_csv(sources.frontend_links)
    backend_routes = read_csv(sources.backend_routes)
    backend_route_uri_refs = read_csv(sources.backend_route_uri_refs)
    backend_models = read_csv(sources.backend_models)
    backend_route_model_links = read_csv(sources.backend_route_model_links)
    table_schema = read_json(sources.table_schema)
    xlsx_bindings, xlsx_points = read_workbook_bindings(sources.xlsx)

    nodes: dict[str, GraphNode] = {}
    edges: dict[str, GraphEdge] = {}

    add_v4_frontend_nodes(frontend_component_refs, frontend_api_refs, frontend_i18n_refs, nodes)
    add_v4_backend_nodes(backend_routes, backend_models, nodes, edges)
    add_v4_frontend_links(frontend_links, edges)
    api_route_uri_matches = add_uri_links(frontend_api_uri_refs, backend_route_uri_refs, edges)
    add_v4_backend_links(backend_route_model_links, nodes, edges)
    schema_tables = add_schema_fields(table_schema, nodes, edges)
    add_workbook_bindings(xlsx_bindings, xlsx_points, nodes, edges)

    positioned_nodes = layout_nodes(list(nodes.values()))
    return {
        "version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_files": {
            "default_inputs_dir": str(sources.default_inputs_dir),
            "audit_outputs_dir": str(sources.audit_outputs_dir) if sources.audit_outputs_dir else None,
            "frontend_sources": str(sources.frontend_sources),
            "frontend_i18n_refs": str(sources.frontend_i18n_refs),
            "frontend_component_refs": str(sources.frontend_component_refs),
            "frontend_api_refs": str(sources.frontend_api_refs),
            "frontend_api_uri_refs": str(sources.frontend_api_uri_refs),
            "frontend_links": str(sources.frontend_links),
            "backend_routes": str(sources.backend_routes),
            "backend_route_uri_refs": str(sources.backend_route_uri_refs),
            "backend_models": str(sources.backend_models),
            "backend_route_model_links": str(sources.backend_route_model_links),
            "table_schema": str(sources.table_schema),
            "xlsx": str(sources.xlsx) if sources.xlsx and sources.xlsx.exists() else None,
        },
        "stats": {
            "frontend_sources": len(frontend_sources),
            "frontend_i18n_refs": len(frontend_i18n_refs),
            "frontend_component_refs": len(frontend_component_refs),
            "frontend_api_refs": len(frontend_api_refs),
            "frontend_api_uri_refs": len(frontend_api_uri_refs),
            "frontend_links": len(frontend_links),
            "backend_routes": len(backend_routes),
            "backend_route_uri_refs": len(backend_route_uri_refs),
            "backend_models": len(backend_models),
            "backend_route_model_links": len(backend_route_model_links),
            "api_route_uri_matches": api_route_uri_matches,
            "table_schema_tables": len(schema_tables),
            "xlsx_bindings": len(xlsx_bindings),
            "nodes": len(positioned_nodes),
            "edges": len(edges),
        },
        "nodes": [node_to_dict(node) for node in positioned_nodes],
        "edges": [edge.__dict__ for edge in edges.values()],
    }


def layout_nodes(nodes: list[GraphNode]) -> list[dict[str, Any]]:
    order = ["locale", "i18n", "component", "api", "route", "model", "table", "field", "plc"]
    grouped: dict[str, list[GraphNode]] = {kind: [] for kind in order}
    for node in nodes:
        grouped.setdefault(node.kind, []).append(node)

    positioned: list[dict[str, Any]] = []
    node_column_width = 280
    node_row_height = 98
    lane_gap = 60
    for lane_index, kind in enumerate(order):
        group = grouped.get(kind, [])
        for index, node in enumerate(group):
            positioned.append(
                {
                    **node_to_dict(node),
                    "ordinal": index + 1,
                    "position": {
                        "x": lane_index * (node_column_width + lane_gap),
                        "y": 52 + index * node_row_height,
                    },
                }
            )
    return positioned
