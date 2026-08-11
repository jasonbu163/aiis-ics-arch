# ARCH-DEV-001 本地开发环境采用与迁移追溯 — Factual Checklist

Task ID: ARCH-DEV-001  
Revision: r4
Status: owner_accepted
Owner Role: QA / Verification  
Allowed Writers: QA / Verification, Human Owner  
Handoff: Human Owner 已最终接受 r4；ARCH-DEV-001 关闭，后续 Git/GitHub 与 1.0.0 定版仍归独立 ARCH-REL-001 gate

Task Namespace: aiis-ics-arch  
Execution Mode: lightweight_same_session  
Role Separation: merged_same_session  
Fresh Context: not provided  
QA Verdict: qa_passed (same-session factual verification; not independent QA)  
Verified: 2026-08-11

## 1. Verification Basis

本 checklist 读取 r4 `owner_approved` spec、`developer_handoff` tasks、五个活动文档及 r3 已有事实。
根据 Human Owner 指示，本轮不启动 Agent Team、没有 fresh context，故只记录机械事实，不能作为独立
QA 证据。Docker runtime 结论只引用 Human Owner 提供的宿主机终端输出，不声称 Codex 独立复跑。

## 2. Acceptance Check

| AC | Result | Evidence |
| --- | --- | --- |
| AC-001 | pass | 两个真实 env 均被根 `.gitignore:90` 忽略；检查和文档未输出 secret 值 |
| AC-002 | pass | backend key set 与 example 一致、无重复；Architecture identity、`mysql:3306`、Core DB、provider/default-off/permissions 全部 pass；三 secret 仅验证为非空非占位 |
| AC-003 | pass | frontend key set 与 example 一致、无重复；API/proxy/default-off/空 page access 通过，五个旧 brand key 已不存在 |
| AC-004 | pass | r3 Compose `config --quiet` exit 0；Codex r4 未执行 daemon lifecycle 或数据库动作 |
| AC-005 | pass | `mutil-project-pm.md` 保留历史并新增第 21 节长期 dev 教程、当前迁移事实和 release gate |
| AC-006 | pass | 文档明确 FE、CA-CONFIG 后续唯一开发源为 `aiis-ics-arch/main`，Vibe 仅作历史参考 |
| AC-007 | pass | PLAN/catalog 已把 ARCH-001 r3 同步为 owner_accepted，并索引本任务真实阶段 |
| AC-008 | pass | allowlist 外实现未改；已删除 smoke Compose/example 未被恢复 |
| AC-009 | pass | 本文件明确 merged_same_session / fresh context not provided，没有冒充独立 QA |
| AC-010 | pass | 四个固定 container names 精确存在、bootstrap 未固定；Human Owner 手工结果为 backend/frontend/mysql healthy、migration `Exited (0)`，后端 health 与前端 HTTP 均通过 |
| AC-011 | pass | 五个活动文档已无指定 obsolete smoke marker；历史 task evidence、ignore 防泄漏规则和 API smoke 工具均保留 |
| AC-012 | pass | tasks/checklist 明确把 dev runtime 标记为 Human Owner 宿主机证据，不冒充 Codex 独立 Docker Verification |

## 3. Limitations and Deferred Gates

- Human Owner 已手工启动真实 `aiis-ics-arch-dev` 并提供容器、HTTP 与 bootstrap default-off 输出；本
  checklist 没有独立重跑，仍不证明长时间稳定性、热更新体验或生产 readiness；
- 没有 release branch/tag/GitHub Release；这些归后续 `ARCH-REL-001`；
- 没有实现 ARCH-FE-001 或 CA-CONFIG-001；两者仍为独立 draft；
- 保留 secret 的来源是否严格为 local-dev-only 需要 Human Owner 自行确认；若复用于现场/生产，应轮换。
- project-governance root checker exit 1，仅报告既有、已接受的 ARCH-001 checklist 含两个 `Handoff:`
  标签；该历史文件不在 r3 allowlist，未修改。ARCH-DEV-001 三文件 metadata 已单独机械核对一致。

## 4. Verdict

`qa_passed` 表示 r4 的失效 smoke 活动文档清理和事实来源标注通过，并继承 r3 已通过的 env、固定名称、
忽略规则、Compose 静态解析、迁移文档与索引机械事实。Human Owner 提供的 dev runtime 结果满足进入
最终接受 gate 的人工证据要求。
它不等于独立 QA、release readiness、生产授权或 Human Owner final acceptance。

下一 gate：Human Owner 审阅本记录并最终接受本任务；接受后再启动
`aiis-ics-arch::ARCH-REL-001`。

## 5. Human Owner Final Acceptance

2026-08-11 Human Owner 原文：

`Human Owner 最终接受 aiis-ics-arch::ARCH-DEV-001 r4。`

本接受关闭 ARCH-DEV-001 r4，但不自动授权 Git add/commit/push、release branch/tag、GitHub Release、
生产部署、真实数据库或 PLC/CA 操作。
