Task ID: ARCH-FE-007
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r1；交 Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_governance
Capability: frontend-js 设计基线与实现参考路由
Owner: 根目录 AGENTS.md 项目契约
Acceptance Chain Reference: 本规格范围批准 → Development handoff → fresh-context Verification → Human Owner 最终验收
Related Task: ARCH-FE-006；AIIS::FUI-003

# frontend-js 设计基线与实现参考路由

## 1. 目标与现状

Human Owner 要求在根目录 [AGENTS.md](../../AGENTS.md) 写明：`frontend-js/` 保持 Vue + JavaScript；新增或重构页面优先遵循本项目 DESIGN；需要实现参考时查阅 `frontend-ui` 的工业 JavaScript 模板。此次只调整文档，现有页面不动。

根契约第 2 节已经将 `frontend-js/` 定义为 Vue 3 + Vite JavaScript Core 前端模板。项目 [中文 DESIGN](../../frontend-js/DESIGN.zh-CN.md) 与 [英文 DESIGN](../../frontend-js/DESIGN.md) 已形成页面和弹窗设计指导；ARCH-FE-006 r1 独立 QA 通过，Human Owner 最终验收状态见其[验证记录](../ARCH-FE-006-frontend-design-guidance/checklist.md)。本次不改变该任务的验收状态。FUI-003 r2 的共享工业 JS / TS 模板已完成 Human Owner 验收，本次只引用其工业 JS 模板作为实现参考。

本项目 `.codex/skills` 当前通过相对软链接指向 AIIS shared skills，[工业 JS 模板](../../.codex/skills/frontend-ui/templates/frontend-admin-industrial-js/)位于该入口下。实际页面继续复用项目的主题、共享组件和业务合同；模板提供实现参考，不自动复制或覆盖既有页面。

## 2. 批准后写入范围

在根 `AGENTS.md` 的「仓库边界」现有 `frontend-js/` 条目作一次外科式补充，保持既有 Vue 3 + Vite + JavaScript 形态，明确：

1. 新增或重构 `frontend-js/` 页面时优先遵循项目 `frontend-js/DESIGN.zh-CN.md` 及其英文 pair。
2. 需要查看实现时，参考 `frontend-ui` 的工业 JavaScript 模板 `templates/frontend-admin-industrial-js/`。
3. 继续采用本项目既有主题和共享组件，模板是参考，不隐含自动复制、页面批量整改或替换项目业务。
4. 根契约中的其他项目、治理、运行、安全、时区和表格规则保持原意。可使用指向现有目标的相对链接，文字保持简洁。

本任务的实现面仅为根 `AGENTS.md` 的上述条目。STD 角色按各自职责创建本任务 `tasks.md` 和 `checklist.md`，协调者按既有 workflow 机械同步相关双语 PLAN / task catalog 的本任务索引。不得修改 `frontend-js/` 页面、组件、样式、设计文档、测试、模板、依赖或配置，也不操作运行服务和业务数据。

Human Owner 同时要求分析 `frontend-js` 页面并在会话给出报告。该分析由协调者只读完成，单独说明证据、覆盖范围及未验证项，不生成报告文件，不作为本任务实施写入面的扩展。

## 3. 验收标准

| 编号 | 可检查结果 |
| --- | --- |
| AC01 | 根 `AGENTS.md` 明确 `frontend-js/` 保持 Vue 3 + Vite + JavaScript，新增或重构页面优先按项目 DESIGN。 |
| AC02 | 规则明确工业 JS 模板用于需要时参考实现，并保留项目主题及共享组件的优先关系；没有暗示自动覆盖或批量修改已有页面。 |
| AC03 | 本任务实现 diff 限定在 `AGENTS.md` 的既有前端条目，相关相对链接有效；现有业务和其他项目契约内容保持原样。 |
| AC04 | 记录交付工作树范围检查和 `git diff --check` 实际命令及退出码。既有并行修改应保留并如实区分；文档改动无需运行前端构建。 |
| AC05 | Development 完成自检并形成精确交接后，由 fresh-context Verification 独立核验正文、链接、差异和范围，结果交 Human Owner 最终验收。 |

## 4. 工作方式与风险

Development 使用 `project-governance` 和 `frontend-ui` 的适用规则，按本任务精确范围修改并记录检查。Verification 独立复核，不以 Development 自检代替 QA。工作树可能存在并行未提交改动，按当前内容做最小补充并保留其他作者内容。

主要风险是把模板参考写成自动替换，或把项目规则扩展为立即整改现有页面。采用条目级修改和差异审查控制。若所需变更超出本规格，回 PM 修订后重新批准。

## 5. 修订与批准

| Revision | 状态 | 说明 |
| --- | --- | --- |
| r1 | draft | 明确前端项目基线、页面设计依据及工业 JS 模板的参考关系。 |

本规格起草时为 PM 草案。范围批准、独立 QA 和最终验收分别记录。

### r1 Human Owner 范围批准与交接

Human Owner 于 2026-11-23（上海时间）对精确 ARCH-FE-007 r1 的批准原话为：

> 批准 ARCH-FE-007 r1。按这版把规则写进 AGENTS.md，只改文档。页面报告先保留，现有页面和代码都别动。

批准前规格 SHA-256 为 `19943b13485496f01b3a1fa8ef4346dc1d8590612f5086b7420649c5f1869f0e`，经本次交接前重新核对一致。上方修订表中的 `draft` 为起草时历史状态。本记录和文件头 `owner_approved` 表示 r1 范围已获批准，范围、验收与写入清单不变。

交实际命名 Development 修改获批文档并记录自检与交接；随后由 fresh-context 命名 Verification 独立核验。页面报告按 Human Owner 指示先保留，现有页面和代码均不改动。范围批准不等于 QA 通过或最终验收。
