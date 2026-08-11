# ARCH-DEV-001 本地开发环境采用与迁移追溯 — Factual Checklist

Task ID: ARCH-DEV-001  
Revision: r2  
Status: qa_passed  
Owner Role: QA / Verification  
Allowed Writers: QA / Verification, Human Owner  
Handoff: same-session factual checklist passed with no independent/fresh-context claim；交给 Human Owner final acceptance 和后续人工 dev runtime gate

Task Namespace: aiis-ics-arch  
Execution Mode: lightweight_same_session  
Role Separation: merged_same_session  
Fresh Context: not provided  
QA Verdict: qa_passed (same-session factual verification; not independent QA)  
Verified: 2026-08-11

## 1. Verification Basis

本 checklist 读取 r2 `owner_approved` spec、`developer_handoff` tasks、当前两个真实 dev env、对应
example、Compose、`.gitignore`、`mutil-project-pm.md` 和四个索引文件。根据 Human Owner 指示，本轮
不启动 Agent Team、没有 fresh context，故只记录机械事实，不能作为独立 QA 证据。

## 2. Acceptance Check

| AC | Result | Evidence |
| --- | --- | --- |
| AC-001 | pass | 两个真实 env 均被根 `.gitignore:90` 忽略；检查和文档未输出 secret 值 |
| AC-002 | pass | backend key set 与 example 一致、无重复；Architecture identity、`mysql:3306`、Core DB、provider/default-off/permissions 全部 pass；三 secret 仅验证为非空非占位 |
| AC-003 | pass | frontend key set 与 example 一致、无重复；API/proxy/default-off/空 page access 通过，五个旧 brand key 已不存在 |
| AC-004 | pass | Compose `config --quiet` exit 0；未执行 daemon lifecycle 或数据库动作 |
| AC-005 | pass | `mutil-project-pm.md` 保留历史并新增第 21 节长期 dev 教程、当前迁移事实和 release gate |
| AC-006 | pass | 文档明确 FE、CA-CONFIG 后续唯一开发源为 `aiis-ics-arch/main`，Vibe 仅作历史参考 |
| AC-007 | pass | PLAN/catalog 已把 ARCH-001 r3 同步为 owner_accepted，并索引本任务真实阶段 |
| AC-008 | pass | allowlist 外实现未改；预先存在的 smoke-example tracked deletion 原样保留 |
| AC-009 | pass | 本文件明确 merged_same_session / fresh context not provided，没有冒充独立 QA |

## 3. Limitations and Deferred Gates

- 未启动真实 `aiis-ics-arch-dev` lifecycle；Human Owner 将按迁移文档人工启动并观察；
- 未证明 dev 数据持久化、热更新或人工登录的本轮现场体验；ARCH-001 r3 曾独立验证过 dev lifecycle，
  但本任务不把历史证据冒充本轮 runtime；
- 没有 release branch/tag/GitHub Release；这些归后续 `ARCH-REL-001`；
- 没有实现 ARCH-FE-001 或 CA-CONFIG-001；两者仍为独立 draft；
- 保留 secret 的来源是否严格为 local-dev-only 需要 Human Owner 自行确认；若复用于现场/生产，应轮换。
- project-governance root checker exit 1，仅报告既有、已接受的 ARCH-001 checklist 含两个 `Handoff:`
  标签；该历史文件不在 r2 allowlist，未修改。ARCH-DEV-001 三文件 metadata 已单独机械核对一致。

## 4. Verdict

`qa_passed` 只表示 r2 的 env 字段收敛、忽略规则、Compose 静态解析、迁移文档和索引机械事实通过。
它不等于独立 QA、Docker runtime 通过、release readiness、生产授权或 Human Owner final acceptance。

下一 gate：Human Owner 审阅本记录并人工启动 dev Compose；确认稳定后，再决定是否最终接受本任务并
启动 `aiis-ics-arch::ARCH-REL-001`。

## 5. Human Owner Final Acceptance

Pending。Human Owner 尚未对 ARCH-DEV-001 r2 给出最终接受语句。
