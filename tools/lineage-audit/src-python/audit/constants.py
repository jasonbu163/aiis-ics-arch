"""
File Path: /tools/lineage-audit/src-python/audit/constants.py
Description: Shared constants and default paths for lineage audit.
Main Features:
    - Defines tool roots and default scan/output paths.
    - Defines regex patterns and cleanup ownership.
"""
from __future__ import annotations

import re
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_FRONTEND_ROOT = PROJECT_ROOT / "frontend-js" / "src"
DEFAULT_BACKEND_ROOT = PROJECT_ROOT / "backend" / "app"
DEFAULT_OUTPUTS_DIR = TOOL_ROOT / "outputs"
MODULE_ALIGNMENT_POLICY_PATH = TOOL_ROOT / "inputs" / "module_alignment_policy.yaml"
TOOL_OWNED_OUTPUTS = {
    "alignment_findings.csv",
    "alignment_overview.csv",
    "audit_manifest.json",
    "backend",
    "backend_route_model_links.csv",
    "backend_route_table_links.csv",
    "backend_routes.csv",
    "backend_routes_without_models.csv",
    "backend_routes_without_tables.csv",
    "component_data_flow.csv",
    "database",
    "frontend",
    "frontend_api_clients.csv",
    "frontend_api_usage.csv",
    "frontend_component_api_links.csv",
    "frontend_missing_api_components.csv",
    "frontend_pages.csv",
    "lineage_audit_report.md",
    "lineage_audit_report.zh-CN.md",
    "mock_findings.csv",
    "projection_candidates.csv",
}

HTTP_METHODS = {"get", "post", "put", "delete", "patch"}
STATIC_DATA_PATTERNS = [
    (re.compile(r"\bmock\b|Mock|模拟|假数据", re.IGNORECASE), "mock_keyword"),
    (re.compile(r"\bdemo\b|Demo|示例", re.IGNORECASE), "demo_keyword"),
    (re.compile(r"\bplaceholder\b|占位", re.IGNORECASE), "placeholder_keyword"),
    (re.compile(r"\bTODO\b|FIXME|待接入|待真实", re.IGNORECASE), "todo_keyword"),
    (re.compile(r"\bconst\s+\w+\s*=\s*\[", re.IGNORECASE), "local_array_literal"),
    (re.compile(r"\bconst\s+\w+\s*=\s*\{", re.IGNORECASE), "local_object_literal"),
]
COMMON_CALLS = {
    "dict",
    "list",
    "set",
    "print",
    "len",
    "str",
    "int",
    "float",
    "bool",
    "Query",
    "Depends",
    "SuccessResponse",
    "HTTPException",
}
