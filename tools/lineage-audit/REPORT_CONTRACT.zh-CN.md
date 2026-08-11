<!--
  File Path: /tools/lineage-audit/REPORT_CONTRACT.zh-CN.md
  Description: 界面血缘审计报告合同
  Main Features:
    - 定义 v4 全量节点优先输出合同
    - 定义证据报告与 AI 报告引用规则
-->
# 界面血缘审计报告合同

[English Version](REPORT_CONTRACT.md)

本合同定义 `tools/lineage-audit/` 的当前持久输出形态。当前 v4 版本采用全量节点优先策略：

```text
LocaleFile -> I18nKey -> Component -> API -> Route -> Model -> Table -> Field
```

节点清单必须全量输出；link 表只表达静态证据。没有连线不代表对象不存在，只代表当前审计没有建立关系。

## 当前输出

| 文件 | 合同角色 |
| --- | --- |
| `outputs/frontend/frontend_sources.csv` | 前端源文件全量清单。 |
| `outputs/frontend/frontend_i18n_refs.csv` | i18n key 定义与组件引用证据。 |
| `outputs/frontend/frontend_component_refs.csv` | Component / page / store 节点清单。 |
| `outputs/frontend/frontend_api_refs.csv` | API client 节点清单。 |
| `outputs/frontend/frontend_api_uri_refs.csv` | 前端 API URI 清单，用于 Studio 按 URI 匹配 API -> Route。 |
| `outputs/frontend/frontend_mock_findings.csv` | 广义 mock/static 行级信号清单，用于清账复核。 |
| `outputs/frontend/frontend_links.csv` | `LocaleFile -> I18nKey -> Component -> API` 前端证据边。 |
| `outputs/backend/backend_routes.csv` | FastAPI route 节点清单。 |
| `outputs/backend/backend_route_uri_refs.csv` | 后端 Route URI 清单，用于 Studio 按 URI 匹配 API -> Route。 |
| `outputs/backend/backend_models.csv` | SQLAlchemy model 全量清单。 |
| `outputs/backend/backend_route_model_links.csv` | `Route -> Model -> Table` 后端证据边。 |
| `outputs/database/table_schema.json` | `Table -> Field` 事实来源。 |
| `outputs/reports/evidence_report.md` / `.zh-CN.md` | 确定性工具证据摘要。 |
| `outputs/reports/ai_audit_report.md` / `.zh-CN.md` | AI 基于 CSV/manifest 生成的派生分析报告。 |
| `outputs/audit_manifest.json` | 本次扫描和输出元数据。 |
| `outputs/alignment_overview.csv` | 带 frontend/backend policy state 的、policy 范围内 Module 配对证据。 |
| `outputs/alignment_findings.csv` | 可检查的 policy 差异与 manual-review 证据缺口。 |

每个 CSV 必须以 `row_id` 作为第一列。AI 报告和人工复核备注必须引用 `CSV 文件名 + row_id`。

## Module 对齐证据

`alignment_overview.csv` 固定以 `row_id`、`frontend_module`、`frontend_policy_state`、`backend_module`、`backend_policy_state`、`evidence_state` 开始。policy state 仅可为 `conformant`、`nonconformant`、`unassessed`、`approved_exception`、`not_applicable`；evidence state 仅可为 `confirmed`、`inferred`、`manual_review`。

`alignment_findings.csv` 固定以 `row_id`、`module_key`、`layer`、`observed`、`expected`、`finding_state`、`evidence_state`、`evidence_refs` 开始。它只包含获批 policy 可检查的差异或明确无法证明的证据；policy 缺失的候选必须是 `manual_review`，不是 defect verdict。

manifest 会记录 policy version 和两份输出合同。backend route evidence 中的 Router tag 字段只记录静态 `APIRouter` metadata，不证明 effective OpenAPI、runtime registration 或实际可达的 API 行为。

manifest 还会记录 `frontend_source_coverage`：生产 `.vue`、`.js`、`.mjs`、`.ts` inventory 根、机械 test/fixture/mock 排除项，以及窄 TypeScript 解析边界。`.tsx`、React source、compiler/type-check、runtime import 与完整 JavaScript/TypeScript parser 均不在当前 profile 内。

## 稳定报告章节

| 章节 | 用途 |
| --- | --- |
| 汇总 | 统计前端、后端、数据库模块的节点与 link 数量。 |
| 证据口径 | 说明本次使用的 CSV、manifest 和静态分析限制。 |
| 断链观察 | 基于 link 表空值、孤点和 Studio 过滤结果说明需要人工复核的位置。 |
| i18n 观察 | 基于 `frontend_i18n_refs.csv` 和 `frontend_links.csv` 说明可见文案变量来源。 |
| Mock/Static 复核 | 基于 `frontend_mock_findings.csv` 作为广义复核队列；分类后才能视为业务缺陷。 |
| 图谱建议 | 说明哪些文件可交给 `lineage-mapping-studio` 可视化复核。 |
| 下一步 | 给出修复、复核或继续投影映射前的建议。 |

## 字段词汇

| 字段 | 含义 |
| --- | --- |
| `row_id` | 稳定证据行标识。 |
| `source_file` / `source_kind` | 前端源文件与来源类型。 |
| `component_id` | 前端组件 / 页面 / store 节点 ID，当前通常为源文件路径。 |
| `api_id` | 前端 API client 节点 ID，格式通常为 `module.function`。 |
| `normalized_uri` | 规范化后的 API 或 route path。 |
| `uri_key` | `METHOD normalized_uri` 组合键，用于 API -> Route 匹配。 |
| `line` / `reason` / `snippet` | `frontend_mock_findings.csv` 中的 mock/static 信号位置、scanner 原因和短源码片段。 |
| `route_id` | 后端 route 节点 ID，格式通常为 `METHOD /path`。 |
| `model_id` / `model_class` | SQLAlchemy model 节点 ID 与类名。 |
| `table_name` | 从 model `__tablename__` 得到的表名。 |
| `from_kind` / `from_id` | link 起点节点类型与 ID。 |
| `to_kind` / `to_id` | link 终点节点类型与 ID。 |
| `edge_type` | link 类型，例如 `component_uses_api`、`defines_i18n_key`。 |
| `evidence_type` / `evidence_file` / `evidence_symbol` | route/model 链接的静态证据位置。 |
| `confidence` | `confirmed`、`inferred` 或 `manual_review`。 |

## 可信度语义

| 值 | 含义 |
| --- | --- |
| `confirmed` | scanner 在当前 profile 规则内找到了直接静态证据。 |
| `inferred` | scanner 根据 route/service/crud 静态引用推断得到；运行时 join 仍需人工复核。 |
| `manual_review` | scanner 无法证明链路，需要人工判断。 |

## 边界

- `lineage-audit` 不生成 `plc_projection_mapping.xlsx`。
- `lineage-audit` 不读取或生成 `plc_points.yaml`。
- `lineage-audit` 不生成 `projection_rules.yaml`。
- `lineage-audit` 将 API URI 证据留在 `frontend/`，将 Route URI 证据留在 `backend/`；跨边界 API -> Route 匹配由 `lineage-mapping-studio` 按相同 `uri_key` 完成。
- `database/table_schema.json` 当前由静态 SQLAlchemy model 解析生成；也可以按 `projection-mapping export-schema` SOP 用真实数据库反射后复制确认。
- 可视化图谱由 `tools/lineage-mapping-studio/` 消费本合同输出和外部映射材料。
