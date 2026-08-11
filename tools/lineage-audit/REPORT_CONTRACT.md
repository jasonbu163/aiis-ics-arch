<!--
  File Path: /tools/lineage-audit/REPORT_CONTRACT.md
  Description: Interface lineage audit report contract
  Main Features:
    - Defines the v4 inventory-first output contract
    - Defines evidence and AI report citation rules
-->
# Interface Lineage Audit Report Contract

Chinese version: [REPORT_CONTRACT.zh-CN.md](REPORT_CONTRACT.zh-CN.md)

This contract defines the current durable output shape of `tools/lineage-audit/`. The current v4 version is inventory-first:

```text
LocaleFile -> I18nKey -> Component -> API -> Route -> Model -> Table -> Field
```

Node inventories must be exhaustive. Link tables only express static evidence. Missing links do not mean missing objects; they only mean the current audit did not establish a relationship.

## Current Outputs

| File | Contract role |
| --- | --- |
| `outputs/frontend/frontend_sources.csv` | Exhaustive frontend source inventory. |
| `outputs/frontend/frontend_i18n_refs.csv` | i18n key definition and component reference evidence. |
| `outputs/frontend/frontend_component_refs.csv` | Component / page / store node inventory. |
| `outputs/frontend/frontend_api_refs.csv` | API client node inventory. |
| `outputs/frontend/frontend_api_uri_refs.csv` | Frontend API URI inventory for Studio-side API -> Route matching. |
| `outputs/frontend/frontend_mock_findings.csv` | Broad row-level mock/static signal inventory for cleanup review. |
| `outputs/frontend/frontend_links.csv` | Frontend evidence links for `LocaleFile -> I18nKey -> Component -> API`. |
| `outputs/backend/backend_routes.csv` | FastAPI route node inventory. |
| `outputs/backend/backend_route_uri_refs.csv` | Backend route URI inventory for Studio-side API -> Route matching. |
| `outputs/backend/backend_models.csv` | Exhaustive SQLAlchemy model inventory. |
| `outputs/backend/backend_route_model_links.csv` | Backend evidence links for `Route -> Model -> Table`. |
| `outputs/database/table_schema.json` | Source of truth for `Table -> Field`. |
| `outputs/reports/evidence_report.md` / `.zh-CN.md` | Deterministic tool evidence summary. |
| `outputs/reports/ai_audit_report.md` / `.zh-CN.md` | AI-authored derived analysis from CSV/manifest evidence. |
| `outputs/audit_manifest.json` | Scan and output metadata for this run. |
| `outputs/alignment_overview.csv` | Policy-scoped module-pairing evidence with frontend/backend policy states. |
| `outputs/alignment_findings.csv` | Policy-checkable differences and manual-review evidence gaps. |

Every CSV must use `row_id` as the first column. AI reports and manual review notes must cite `CSV filename + row_id`.

## Module-alignment evidence

`alignment_overview.csv` always starts with `row_id`, `frontend_module`, `frontend_policy_state`, `backend_module`, `backend_policy_state`, and `evidence_state`. The policy states are limited to `conformant`, `nonconformant`, `unassessed`, `approved_exception`, and `not_applicable`; evidence state is `confirmed`, `inferred`, or `manual_review`.

`alignment_findings.csv` always starts with `row_id`, `module_key`, `layer`, `observed`, `expected`, `finding_state`, `evidence_state`, and `evidence_refs`. It contains only approved-policy checks or explicitly unproven evidence. A policy-missing candidate is `manual_review`, not a defect verdict.

The manifest records the policy version and both output contracts. Router tag fields on backend route evidence record static `APIRouter` metadata only. They do not prove the effective OpenAPI document, runtime registration, or reachable API behavior.

The manifest also records `frontend_source_coverage`: production `.vue`, `.js`, `.mjs` and `.ts` inventory roots, mechanical test/fixture/mock exclusions, and the narrow TypeScript parsing boundary. `.tsx`, React source, compiler/type-check, runtime imports and full JavaScript/TypeScript parsing are outside this profile.

## Stable Report Sections

| Section | Purpose |
| --- | --- |
| Summary | Count frontend, backend and database node/link outputs. |
| Evidence Scope | State CSV/manifest evidence used and static-analysis limits. |
| Broken Chain Review | Use empty link fields, orphan nodes and Studio filters to identify manual-review areas. |
| i18n Review | Use `frontend_i18n_refs.csv` and `frontend_links.csv` to trace visible copy keys. |
| Mock/Static Review | Use `frontend_mock_findings.csv` as a broad review queue; classify rows before treating them as business defects. |
| Graph Guidance | Explain which files feed `lineage-mapping-studio`. |
| Next Steps | Recommend repairs, review gates or projection-mapping prerequisites. |

## Field Vocabulary

| Field | Meaning |
| --- | --- |
| `row_id` | Stable evidence row ID. |
| `source_file` / `source_kind` | Frontend source file and source type. |
| `component_id` | Frontend component / page / store node ID, usually the source file path. |
| `api_id` | Frontend API client node ID, usually `module.function`. |
| `normalized_uri` | Normalized API or route path. |
| `uri_key` | `METHOD normalized_uri` join key for API -> Route matching. |
| `line` / `reason` / `snippet` | Mock/static signal location, scanner reason and short source snippet in `frontend_mock_findings.csv`. |
| `route_id` | Backend route node ID, usually `METHOD /path`. |
| `model_id` / `model_class` | SQLAlchemy model node ID and class name. |
| `table_name` | Table name derived from model `__tablename__`. |
| `from_kind` / `from_id` | Link source node kind and ID. |
| `to_kind` / `to_id` | Link target node kind and ID. |
| `edge_type` | Link type, such as `component_uses_api` or `defines_i18n_key`. |
| `evidence_type` / `evidence_file` / `evidence_symbol` | Static evidence location for route/model links. |
| `confidence` | `confirmed`, `inferred` or `manual_review`. |

## Confidence Semantics

| Value | Meaning |
| --- | --- |
| `confirmed` | The scanner found direct static evidence inside the current profile rules. |
| `inferred` | The scanner inferred the link from route/service/crud static references; runtime-only joins still need review. |
| `manual_review` | The scanner cannot prove the link and a human must judge it. |

## Boundary

- `lineage-audit` does not generate `plc_projection_mapping.xlsx`.
- `lineage-audit` does not read or generate `plc_points.yaml`.
- `lineage-audit` does not generate `projection_rules.yaml`.
- `lineage-audit` keeps API URI evidence under `frontend/` and Route URI evidence under `backend/`; `lineage-mapping-studio` owns the cross-boundary API -> Route match by identical `uri_key`.
- `database/table_schema.json` is currently generated from static SQLAlchemy model parsing; it may also be regenerated through the `projection-mapping export-schema` SOP and copied after confirmation.
- Visual graphs are rendered by `tools/lineage-mapping-studio/` from this contract plus external mapping materials.
