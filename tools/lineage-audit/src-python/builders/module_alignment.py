"""
File Path: /tools/lineage-audit/src-python/builders/module_alignment.py
Description: Static module-alignment policy evidence builder.
Main Features:
    - Loads the human-maintained module-alignment policy.
    - Produces reviewable overview and finding rows without defect verdicts.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import yaml

from audit.models import ToolError


POLICY_STATES = {"conformant", "nonconformant", "unassessed", "approved_exception", "not_applicable"}
EVIDENCE_STATES = {"confirmed", "inferred", "manual_review"}
TABLE_ROLES = {"raw", "latest", "projection", "read_model"}


def load_module_alignment_policy(path: Path) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ToolError(f"Unable to read module alignment policy: {path}") from exc
    except yaml.YAMLError as exc:
        raise ToolError(f"Invalid module alignment policy YAML: {path}") from exc
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ToolError("module_alignment_policy.yaml must declare version: 1")
    for key in ("modules", "frontend_only", "backend_only", "approved_exceptions"):
        if not isinstance(payload.get(key, []), list):
            raise ToolError(f"module_alignment_policy.yaml field '{key}' must be a list")
    for index, entry in enumerate(payload["modules"]):
        if not isinstance(entry, dict) or not all(isinstance(entry.get(key), str) and entry[key] for key in ("key", "frontend", "backend")):
            raise ToolError(f"modules[{index}] must define non-empty key, frontend and backend strings")
        table_roles = entry.get("table_roles", [])
        if not isinstance(table_roles, list):
            raise ToolError(f"modules[{index}].table_roles must be a list")
        for role_index, role_entry in enumerate(table_roles):
            if not isinstance(role_entry, dict) or not isinstance(role_entry.get("table"), str) or role_entry.get("role") not in TABLE_ROLES:
                raise ToolError(
                    f"modules[{index}].table_roles[{role_index}] must declare table and one of {sorted(TABLE_ROLES)}"
                )
    return payload


def _module_for_frontend_api(row: dict[str, Any]) -> str:
    api_file = str(row.get("api_file", ""))
    marker = "/src/app/"
    if marker in api_file:
        remainder = api_file.split(marker, 1)[1]
        return remainder.split("/", 1)[0]
    if "/src/api/" in api_file:
        return "root_api"
    return "shared"


def _refs(rows: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool], limit: int = 5) -> str:
    return ";".join(str(row["row_id"]) for row in rows if predicate(row))[:1000]


def _exception_keys(policy: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for entry in policy["approved_exceptions"]:
        if isinstance(entry, str):
            keys.add(entry)
        elif isinstance(entry, dict) and isinstance(entry.get("key"), str):
            keys.add(entry["key"])
    return keys


def build_module_alignment_outputs(
    policy_path: Path,
    frontend_api_rows: list[dict[str, Any]],
    backend_route_rows: list[dict[str, Any]],
    backend_model_rows: list[dict[str, Any]],
    table_schema: dict[str, Any],
    add_row_ids: Callable[[list[dict[str, Any]], str, list[str]], list[dict[str, Any]]],
) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    policy = load_module_alignment_policy(policy_path)
    frontend_modules = {_module_for_frontend_api(row) for row in frontend_api_rows}
    backend_modules = {str(row["backend_module"]) for row in backend_route_rows}
    table_names = {str(table.get("table_name", "")) for table in table_schema.get("tables", [])}
    exception_keys = _exception_keys(policy)
    overview_rows: list[dict[str, Any]] = []
    finding_rows: list[dict[str, Any]] = []
    covered_frontend: set[str] = set()
    covered_backend: set[str] = set()

    def add_finding(module_key: str, layer: str, observed: str, expected: str, finding_state: str, evidence_state: str, refs: str) -> None:
        finding_rows.append(
            {
                "module_key": module_key,
                "layer": layer,
                "observed": observed,
                "expected": expected,
                "finding_state": finding_state,
                "evidence_state": evidence_state,
                "evidence_refs": refs,
            }
        )

    for entry in policy["modules"]:
        key = entry["key"]
        frontend = entry["frontend"]
        backend = entry["backend"]
        covered_frontend.add(frontend)
        covered_backend.add(backend)
        frontend_present = frontend in frontend_modules
        backend_present = backend in backend_modules
        exception = key in exception_keys
        frontend_state = "approved_exception" if exception else ("conformant" if frontend_present else "nonconformant")
        backend_state = "approved_exception" if exception else ("conformant" if backend_present else "nonconformant")
        evidence_state = "confirmed" if frontend_present and backend_present else "manual_review"
        frontend_refs = _refs(frontend_api_rows, lambda row: _module_for_frontend_api(row) == frontend)
        backend_refs = _refs(backend_route_rows, lambda row: row.get("backend_module") == backend)
        overview_rows.append(
            {
                "frontend_module": frontend,
                "frontend_policy_state": frontend_state,
                "backend_module": backend,
                "backend_policy_state": backend_state,
                "evidence_state": evidence_state,
                "data_roles": ";".join(f"{item['table']}:{item['role']}" for item in entry.get("table_roles", [])),
                "evidence_refs": ";".join(filter(None, [frontend_refs, backend_refs, f"module_alignment_policy.yaml:modules[{key}]"])),
            }
        )
        if not exception and not frontend_present:
            add_finding(key, "frontend", "not_observed", frontend, "policy_mismatch", "manual_review", f"module_alignment_policy.yaml:modules[{key}]")
        if not exception and not backend_present:
            add_finding(key, "backend", "not_observed", backend, "policy_mismatch", "manual_review", f"module_alignment_policy.yaml:modules[{key}]")
        for role_entry in entry.get("table_roles", []):
            table = role_entry["table"]
            if table not in table_names:
                add_finding(
                    key,
                    "table_role",
                    "table_not_in_static_schema",
                    f"{table}:{role_entry['role']}",
                    "manual_review",
                    "manual_review",
                    f"module_alignment_policy.yaml:modules[{key}].table_roles;table_schema.json:table={table}",
                )

    for frontend in policy["frontend_only"]:
        if not isinstance(frontend, str):
            continue
        covered_frontend.add(frontend)
        present = frontend in frontend_modules
        overview_rows.append(
            {
                "frontend_module": frontend,
                "frontend_policy_state": "conformant" if present else "nonconformant",
                "backend_module": "",
                "backend_policy_state": "not_applicable",
                "evidence_state": "confirmed" if present else "manual_review",
                "data_roles": "",
                "evidence_refs": ";".join(filter(None, [_refs(frontend_api_rows, lambda row: _module_for_frontend_api(row) == frontend), "module_alignment_policy.yaml:frontend_only"])),
            }
        )
    for backend in policy["backend_only"]:
        if not isinstance(backend, str):
            continue
        covered_backend.add(backend)
        present = backend in backend_modules
        overview_rows.append(
            {
                "frontend_module": "",
                "frontend_policy_state": "not_applicable",
                "backend_module": backend,
                "backend_policy_state": "conformant" if present else "nonconformant",
                "evidence_state": "confirmed" if present else "manual_review",
                "data_roles": "",
                "evidence_refs": ";".join(filter(None, [_refs(backend_route_rows, lambda row: row.get("backend_module") == backend), "module_alignment_policy.yaml:backend_only"])),
            }
        )

    for frontend in sorted(frontend_modules - covered_frontend):
        refs = _refs(frontend_api_rows, lambda row: _module_for_frontend_api(row) == frontend)
        overview_rows.append(
            {
                "frontend_module": frontend,
                "frontend_policy_state": "unassessed",
                "backend_module": "",
                "backend_policy_state": "unassessed",
                "evidence_state": "manual_review",
                "data_roles": "",
                "evidence_refs": refs,
            }
        )
        add_finding(frontend, "frontend", frontend, "approved module_alignment_policy entry", "policy_missing", "manual_review", refs)
    for backend in sorted(backend_modules - covered_backend):
        refs = _refs(backend_route_rows, lambda row: row.get("backend_module") == backend)
        overview_rows.append(
            {
                "frontend_module": "",
                "frontend_policy_state": "unassessed",
                "backend_module": backend,
                "backend_policy_state": "unassessed",
                "evidence_state": "manual_review",
                "data_roles": "",
                "evidence_refs": refs,
            }
        )
        add_finding(backend, "backend", backend, "approved module_alignment_policy entry", "policy_missing", "manual_review", refs)

    return policy, {
        "alignment_overview": add_row_ids(
            overview_rows,
            "alignment_overview",
            ["frontend_module", "backend_module", "frontend_policy_state", "backend_policy_state"],
        ),
        "alignment_findings": add_row_ids(
            finding_rows,
            "alignment_findings",
            ["module_key", "layer", "observed", "expected", "finding_state"],
        ),
    }
