"""
File Path: /tools/lineage-audit/src-python/builders/database_audit.py
Description: Database schema inventory builder for lineage audit v4.
Main Features:
    - Builds table_schema.json from statically scanned SQLAlchemy models.
    - Keeps database field inventory separate from route/model link evidence.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


def expression_text(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def mapped_type(annotation: ast.AST | None) -> str:
    text = expression_text(annotation)
    if text.startswith("Mapped[") and text.endswith("]"):
        return text[len("Mapped[") : -1]
    return text


def keyword_value(call: ast.Call | None, keyword: str) -> Any:
    if call is None:
        return None
    for item in call.keywords:
        if item.arg == keyword:
            return ast.literal_eval(item.value) if isinstance(item.value, ast.Constant) else expression_text(item.value)
    return None


def mapped_column_call(value: ast.AST | None) -> ast.Call | None:
    if not isinstance(value, ast.Call):
        return None
    func_name = expression_text(value.func)
    if func_name in {"mapped_column", "Column"} or func_name.endswith(".mapped_column"):
        return value
    return None


def infer_column_type(annotation: ast.AST | None, call: ast.Call | None) -> str:
    if call and call.args:
        return expression_text(call.args[0])
    return mapped_type(annotation)


def parse_model_columns(model_file: Path, class_name: str) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(model_file.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        columns: list[dict[str, Any]] = []
        for stmt in node.body:
            if not isinstance(stmt, ast.AnnAssign) or not isinstance(stmt.target, ast.Name):
                continue
            field_name = stmt.target.id
            call = mapped_column_call(stmt.value)
            columns.append(
                {
                    "name": field_name,
                    "field_name": field_name,
                    "field_type": infer_column_type(stmt.annotation, call),
                    "data_type": mapped_type(stmt.annotation),
                    "nullable": keyword_value(call, "nullable"),
                    "default": keyword_value(call, "default"),
                    "key": "PRI" if keyword_value(call, "primary_key") is True else "",
                    "extra": "index" if keyword_value(call, "index") is True else "",
                    "comment": keyword_value(call, "comment") or "",
                }
            )
        return columns
    return []


def build_table_schema(class_to_model: dict[str, Any], project_root: Path) -> dict[str, Any]:
    tables: list[dict[str, Any]] = []
    seen_tables: set[str] = set()
    for model in sorted(class_to_model.values(), key=lambda item: (item.table_name, item.class_name)):
        if not model.table_name or model.table_name in seen_tables:
            continue
        seen_tables.add(model.table_name)
        model_path = project_root / model.model_file
        columns = parse_model_columns(model_path, model.class_name)
        tables.append(
            {
                "table_name": model.table_name,
                "model_class": model.class_name,
                "model_file": model.model_file,
                "backend_module": model.module,
                "columns": columns,
                "constraints": [],
                "schema_source": "sqlalchemy_static",
            }
        )
    return {
        "source": "lineage-audit.database",
        "schema_source": "sqlalchemy_static",
        "tables": tables,
    }
