"""
File Path: /tools/plc/projection-mapping/src-python/core/targets.py
Description: Projection target and schema normalization.
"""
from __future__ import annotations

from typing import Any

from core.common import ToolError


def normalize_targets(payload: Any) -> list[str]:
    if isinstance(payload, dict):
        raw_tables = payload.get("tables")
    else:
        raw_tables = payload
    if not isinstance(raw_tables, list):
        raise ToolError("projection targets must be a JSON object with a 'tables' list or a plain list")

    tables: list[str] = []
    for item in raw_tables:
        if isinstance(item, str):
            table_name = item.strip()
        elif isinstance(item, dict):
            table_name = str(item.get("table") or item.get("table_name") or "").strip()
        else:
            table_name = ""
        if table_name:
            tables.append(table_name)

    duplicate_tables = sorted({table for table in tables if tables.count(table) > 1})
    if duplicate_tables:
        raise ToolError(f"duplicate target tables: {duplicate_tables}")
    if not tables:
        raise ToolError("projection targets are empty")
    return tables


def normalize_schema(payload: Any) -> dict[str, list[dict[str, Any]]]:
    tables = payload.get("tables") if isinstance(payload, dict) else payload
    if not isinstance(tables, list):
        raise ToolError("table schema must contain a 'tables' list")

    normalized: dict[str, list[dict[str, Any]]] = {}
    for table in tables:
        if not isinstance(table, dict):
            continue
        table_name = str(table.get("table_name") or table.get("name") or "").strip()
        columns = table.get("columns")
        if not table_name or not isinstance(columns, list):
            continue
        normalized[table_name] = [column for column in columns if isinstance(column, dict)]
    if not normalized:
        raise ToolError("table schema does not contain any usable table definitions")
    return normalized
