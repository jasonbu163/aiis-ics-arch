"""
File Path: /tools/lineage-audit/src-python/reports/writers.py
Description: Output writers, manifest writer and deterministic evidence reports.
Main Features:
    - Writes v4 frontend/backend/database evidence files.
    - Writes audit manifest and bilingual deterministic reports.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from builders.backend_audit import build_backend_outputs
from builders.database_audit import build_table_schema
from builders.frontend_audit import build_frontend_outputs
from builders.module_alignment import build_module_alignment_outputs
from audit.common import add_row_ids, clean_tool_outputs, rel, write_csv, write_json
from audit.constants import MODULE_ALIGNMENT_POLICY_PATH, PROJECT_ROOT
from audit.models import AuditState
from audit.runner import list_frontend_sources
from scanners.frontend import EXCLUDED_SOURCE_PARTS, PRODUCTION_SOURCE_SUFFIXES, classify_frontend_source, find_route_for_source

def write_outputs(state: AuditState, outputs_dir: Path, frontend_root: Path, backend_root: Path) -> dict[str, Path]:
    outputs_dir.mkdir(parents=True, exist_ok=True)
    clean_tool_outputs(outputs_dir)
    generated_at = time.strftime("%Y-%m-%d %H:%M:%S")

    frontend_dir = outputs_dir / "frontend"
    backend_dir = outputs_dir / "backend"
    database_dir = outputs_dir / "database"
    reports_dir = outputs_dir / "reports"
    for directory in (frontend_dir, backend_dir, database_dir, reports_dir):
        directory.mkdir(parents=True, exist_ok=True)

    frontend_outputs = build_frontend_outputs(
        frontend_root,
        state.frontend_routes,
        state.frontend_apis,
        state.frontend_usages,
        state.mock_findings,
        rel,
        classify_frontend_source,
        find_route_for_source,
        list_frontend_sources,
        add_row_ids,
    )
    backend_outputs = build_backend_outputs(
        state.backend_routes,
        state.class_to_model,
        add_row_ids,
    )
    table_schema = build_table_schema(state.class_to_model, PROJECT_ROOT)
    policy, alignment_outputs = build_module_alignment_outputs(
        MODULE_ALIGNMENT_POLICY_PATH,
        frontend_outputs["frontend_api_refs"],
        backend_outputs["backend_routes"],
        backend_outputs["backend_models"],
        table_schema,
        add_row_ids,
    )

    paths = {
        "summary": reports_dir / "evidence_report.md",
        "summary_zh_cn": reports_dir / "evidence_report.zh-CN.md",
        "manifest": outputs_dir / "audit_manifest.json",
        "frontend_sources": frontend_dir / "frontend_sources.csv",
        "frontend_i18n_refs": frontend_dir / "frontend_i18n_refs.csv",
        "frontend_component_refs": frontend_dir / "frontend_component_refs.csv",
        "frontend_api_refs": frontend_dir / "frontend_api_refs.csv",
        "frontend_api_uri_refs": frontend_dir / "frontend_api_uri_refs.csv",
        "frontend_mock_findings": frontend_dir / "frontend_mock_findings.csv",
        "frontend_links": frontend_dir / "frontend_links.csv",
        "backend_routes": backend_dir / "backend_routes.csv",
        "backend_route_uri_refs": backend_dir / "backend_route_uri_refs.csv",
        "backend_models": backend_dir / "backend_models.csv",
        "backend_route_model_links": backend_dir / "backend_route_model_links.csv",
        "alignment_overview": outputs_dir / "alignment_overview.csv",
        "alignment_findings": outputs_dir / "alignment_findings.csv",
        "table_schema": database_dir / "table_schema.json",
    }

    write_csv(paths["frontend_sources"], frontend_outputs["frontend_sources"], [
        "row_id",
        "source_file",
        "source_kind",
        "route_path",
        "route_name",
        "mock_finding_count",
    ])
    write_csv(paths["frontend_i18n_refs"], frontend_outputs["frontend_i18n_refs"], [
        "row_id",
        "record_kind",
        "locale_file",
        "locale",
        "i18n_key",
        "value",
        "source_file",
        "source_kind",
        "route_path",
        "route_name",
        "evidence_symbol",
    ])
    write_csv(paths["frontend_component_refs"], frontend_outputs["frontend_component_refs"], [
        "row_id",
        "component_id",
        "source_file",
        "source_kind",
        "route_path",
        "route_name",
    ])
    write_csv(paths["frontend_api_refs"], frontend_outputs["frontend_api_refs"], [
        "row_id",
        "api_id",
        "api_module",
        "api_function",
        "api_file",
        "method",
        "frontend_api_path",
        "raw_path_expr",
        "confidence",
    ])
    write_csv(paths["frontend_api_uri_refs"], frontend_outputs["frontend_api_uri_refs"], [
        "row_id",
        "api_id",
        "method",
        "normalized_uri",
        "uri_key",
        "frontend_api_path",
        "raw_path_expr",
        "api_file",
        "confidence",
    ])
    write_csv(paths["frontend_mock_findings"], frontend_outputs["frontend_mock_findings"], [
        "row_id",
        "source_file",
        "source_kind",
        "route_path",
        "route_name",
        "line",
        "reason",
        "snippet",
    ])
    write_csv(paths["frontend_links"], frontend_outputs["frontend_links"], [
        "row_id",
        "from_kind",
        "from_id",
        "to_kind",
        "to_id",
        "edge_type",
        "source_file",
        "evidence_symbol",
        "confidence",
    ])
    write_csv(paths["backend_routes"], backend_outputs["backend_routes"], [
        "row_id",
        "route_id",
        "method",
        "backend_route",
        "backend_module",
        "backend_function",
        "backend_api_file",
        "router_var",
        "router_tags",
        "tag_evidence_file",
        "tag_evidence_symbol",
        "tag_evidence_state",
        "called_symbols",
        "confidence",
    ])
    write_csv(paths["backend_route_uri_refs"], backend_outputs["backend_route_uri_refs"], [
        "row_id",
        "route_id",
        "method",
        "normalized_uri",
        "uri_key",
        "backend_route",
        "backend_module",
        "backend_function",
        "backend_api_file",
        "confidence",
    ])
    write_csv(paths["backend_models"], backend_outputs["backend_models"], [
        "row_id",
        "model_id",
        "model_class",
        "model_file",
        "backend_module",
        "table_name",
    ])
    write_csv(paths["backend_route_model_links"], backend_outputs["backend_route_model_links"], [
        "row_id",
        "route_id",
        "method",
        "backend_route",
        "backend_module",
        "backend_function",
        "backend_api_file",
        "router_tags",
        "tag_evidence_file",
        "tag_evidence_symbol",
        "tag_evidence_state",
        "model_class",
        "model_file",
        "table_name",
        "evidence_type",
        "evidence_file",
        "evidence_symbol",
        "confidence",
    ])
    write_csv(paths["alignment_overview"], alignment_outputs["alignment_overview"], [
        "row_id",
        "frontend_module",
        "frontend_policy_state",
        "backend_module",
        "backend_policy_state",
        "evidence_state",
        "data_roles",
        "evidence_refs",
    ])
    write_csv(paths["alignment_findings"], alignment_outputs["alignment_findings"], [
        "row_id",
        "module_key",
        "layer",
        "observed",
        "expected",
        "finding_state",
        "evidence_state",
        "evidence_refs",
    ])
    write_json(paths["table_schema"], table_schema)

    csv_outputs = {
        "frontend_sources": (paths["frontend_sources"], frontend_outputs["frontend_sources"]),
        "frontend_i18n_refs": (paths["frontend_i18n_refs"], frontend_outputs["frontend_i18n_refs"]),
        "frontend_component_refs": (paths["frontend_component_refs"], frontend_outputs["frontend_component_refs"]),
        "frontend_api_refs": (paths["frontend_api_refs"], frontend_outputs["frontend_api_refs"]),
        "frontend_api_uri_refs": (paths["frontend_api_uri_refs"], frontend_outputs["frontend_api_uri_refs"]),
        "frontend_mock_findings": (paths["frontend_mock_findings"], frontend_outputs["frontend_mock_findings"]),
        "frontend_links": (paths["frontend_links"], frontend_outputs["frontend_links"]),
        "backend_routes": (paths["backend_routes"], backend_outputs["backend_routes"]),
        "backend_route_uri_refs": (paths["backend_route_uri_refs"], backend_outputs["backend_route_uri_refs"]),
        "backend_models": (paths["backend_models"], backend_outputs["backend_models"]),
        "backend_route_model_links": (paths["backend_route_model_links"], backend_outputs["backend_route_model_links"]),
        "alignment_overview": (paths["alignment_overview"], alignment_outputs["alignment_overview"]),
        "alignment_findings": (paths["alignment_findings"], alignment_outputs["alignment_findings"]),
    }
    write_audit_manifest(
        paths["manifest"],
        generated_at,
        frontend_root,
        backend_root,
        csv_outputs,
        paths,
        table_schema,
        policy,
    )
    write_v4_markdown_report(
        paths["summary"],
        csv_outputs,
        table_schema,
        generated_at,
        language="en",
        policy_version=policy["version"],
    )
    write_v4_markdown_report(
        paths["summary_zh_cn"],
        csv_outputs,
        table_schema,
        generated_at,
        language="zh-CN",
        policy_version=policy["version"],
    )
    return paths


def write_v4_markdown_report(
    path: Path,
    csv_outputs: dict[str, tuple[Path, list[dict[str, Any]]]],
    table_schema: dict[str, Any],
    generated_at: str,
    language: str,
    policy_version: int,
) -> None:
    table_count = len(table_schema.get("tables", []))
    field_count = sum(len(table.get("columns", [])) for table in table_schema.get("tables", []))
    if language == "zh-CN":
        lines = [
            "# 血缘审计证据报告",
            "",
            f"生成时间：`{generated_at}`",
            "",
            "## v4 合同",
            "",
            "本报告来自 v4 全量节点优先合同：节点全量输出，连线只表达证据；断链不再通过 missing 表表达。",
            "",
            "## 输出统计",
            "",
            "| 输出 | 行数 | 路径 |",
            "| --- | ---: | --- |",
        ]
        for key, (csv_path, rows) in csv_outputs.items():
            lines.append(f"| `{key}` | {len(rows)} | `{rel(csv_path)}` |")
        lines.extend(
            [
                f"| `database.table_schema` | {table_count} tables / {field_count} fields | `{rel(path.parent.parent / 'database' / 'table_schema.json')}` |",
                "",
                "## Module 对齐证据",
                "",
                f"- 使用 `inputs/module_alignment_policy.yaml` version `{policy_version}`；未在 policy 中确认的候选只标记为 `unassessed` / `manual_review`，不是 defect verdict。",
                "- Router tag 只证明静态源码 metadata；不证明 OpenAPI、runtime registration 或 API 可达性。",
                "- 前端生产 inventory 覆盖 `.vue`、`.js`、`.mjs`、`.ts`；`*.test.*`、`*.spec.*`、`__tests__/`、fixture 与 mock source 不进入 production evidence。",
                "- TypeScript 仅按局部静态规则识别常见 typed export 与 `request.<method><T>(...)`；不运行 compiler、type-check、runtime import 或完整 parser。",
                "## 后续",
                "",
                "- Studio 需要改为先加载全量节点清单，再加载 link 边。",
                "- PLC 点位和 Field -> PLC 绑定不在本环节内，由 projection-mapping 后续流程处理。",
            ]
        )
    else:
        lines = [
            "# Lineage Audit Evidence Report",
            "",
            f"Generated at: `{generated_at}`",
            "",
            "## v4 Contract",
            "",
            "This report follows the v4 inventory-first contract: emit all nodes first, then use links only as evidence. Broken chains are no longer represented by separate missing tables.",
            "",
            "## Output Counts",
            "",
            "| Output | Rows | Path |",
            "| --- | ---: | --- |",
        ]
        for key, (csv_path, rows) in csv_outputs.items():
            lines.append(f"| `{key}` | {len(rows)} | `{rel(csv_path)}` |")
        lines.extend(
            [
                f"| `database.table_schema` | {table_count} tables / {field_count} fields | `{rel(path.parent.parent / 'database' / 'table_schema.json')}` |",
                "",
                "## Module-alignment evidence",
                "",
                f"- Uses `inputs/module_alignment_policy.yaml` version `{policy_version}`. Candidates absent from policy remain `unassessed` / `manual_review`, not defect verdicts.",
                "- Router tags prove static source metadata only; they do not prove OpenAPI, runtime registration or API reachability.",
                "- Production frontend inventory covers `.vue`, `.js`, `.mjs` and `.ts`; `*.test.*`, `*.spec.*`, `__tests__/`, fixture and mock source do not enter production evidence.",
                "- TypeScript uses narrow static rules for common typed exports and `request.<method><T>(...)`; it does not run a compiler, type-check, runtime import or full parser.",
                "## Next",
                "",
                "- Studio must load exhaustive node inventories first, then link edges.",
                "- PLC points and Field -> PLC bindings are outside this stage and remain in the projection-mapping workflow.",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_manifest(
    path: Path,
    generated_at: str,
    frontend_root: Path,
    backend_root: Path,
    csv_outputs: dict[str, tuple[Path, list[dict[str, Any]]]],
    paths: dict[str, Path],
    table_schema: dict[str, Any],
    policy: dict[str, Any],
) -> None:
    outputs: dict[str, dict[str, Any]] = {}
    for key, (csv_path, rows) in csv_outputs.items():
        outputs[key] = {
            "path": rel(csv_path),
            "row_count": len(rows),
            "columns": list(rows[0].keys()) if rows else ["row_id"],
            "row_id_required": True,
        }

    ai_report_paths = [
        paths["summary"].parent / "ai_audit_report.md",
        paths["summary"].parent / "ai_audit_report.zh-CN.md",
    ]
    ai_report_status = "generated" if all(item.exists() for item in ai_report_paths) else "not_generated"

    payload = {
        "tool": "lineage-audit",
        "profile": "vue_fastapi_sqlalchemy",
        "field_contract_version": "2026-06-27-v4-inventory-first",
        "module_alignment_policy_version": policy["version"],
        "generated_at": generated_at,
        "contract_principle": "nodes_are_exhaustive_links_are_evidence",
        "inputs": {
            "frontend_root": rel(frontend_root),
            "backend_root": rel(backend_root),
            "plc_points_yaml": "not_used_in_this_stage",
            "module_alignment_policy": rel(MODULE_ALIGNMENT_POLICY_PATH),
        },
        "frontend_source_coverage": {
            "extensions": list(PRODUCTION_SOURCE_SUFFIXES),
            "inventory_roots": [
                "app/**/views/",
                "app/**/components/",
                "pages/",
                "layouts/",
                "views/",
                "components/",
                "store/",
            ],
            "excluded_patterns": [
                "*.test.*",
                "*.spec.*",
                "__tests__/",
                *[f"{part}/" for part in sorted(EXCLUDED_SOURCE_PARTS)],
                "mock.*",
            ],
            "typescript_support": "narrow_static_exports_and_request_method_generics",
        },
        "outputs": {
            **outputs,
            "database_table_schema": {
                "path": rel(paths["table_schema"]),
                "table_count": len(table_schema.get("tables", [])),
                "field_count": sum(len(table.get("columns", [])) for table in table_schema.get("tables", [])),
                "schema_source": table_schema.get("schema_source", ""),
                "row_id_required": False,
            },
            "deterministic_summary": {
                "path": rel(paths["summary"]),
                "zh_cn_path": rel(paths["summary_zh_cn"]),
                "role": "tool_generated_summary_not_ai_audit_report",
            },
        },
        "ai_report": {
            "status": ai_report_status,
            "expected_files": [
                rel(ai_report_paths[0]),
                rel(ai_report_paths[1]),
            ],
            "required_citation": "AI reports must cite CSV file names and row_id values.",
        },
        "limits": [
            "Static analysis only; no frontend runtime rendering was executed.",
            "TypeScript coverage is limited to narrow static source/API/manifest rules; no TypeScript compiler, type-check, runtime import or full parser was used.",
            "React and .tsx source are outside this Vue profile and are not scanned.",
            "Router tag evidence proves static APIRouter metadata only; it does not prove effective OpenAPI, runtime registration or public API reachability.",
            "Module alignment results are policy-scoped static evidence for manual governance review, not G-005 gates or defect verdicts.",
            "Backend route/model links express evidence only; all backend models are emitted through backend_models.csv even when no route link exists.",
            "database/table_schema.json is generated from static SQLAlchemy model code in this stage.",
            "PLC points and Field -> PLC bindings belong to projection-mapping, not this scanner.",
        ],
    }
    write_json(path, payload)
