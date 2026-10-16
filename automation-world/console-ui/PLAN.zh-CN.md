# Console UI 计划

[English](PLAN.md)

本 PLAN 管理 CU 专属实施任务；[AW PLAN](../PLAN.zh-CN.md) 管理整体阶段和跨工程依赖。

| Task ID | 状态 | 规格 | 最新事实 / 下一 gate |
| --- | --- | --- | --- |
| CU-001 | owner_accepted | [r1](plans/CU-001-workbench-foundation/spec.md) | 工作台和公共 UI 出口已交付，定向复核通过；Human Owner 于 2026-10-15 接受 r1。本轮仅更新 CU 状态，未追加测试。 |
| CU-002 | owner_accepted | [r1](plans/CU-002-topbar-utility-controls/spec.md) | Human Owner 于 2026-10-16 验收 r1，保留原独立 QA 证据；本轮仅 CU 状态收尾，未追加测试。 |
| CU-003 | owner_accepted | [r1](plans/CU-003-topbar-height-alignment/spec.md) | Human Owner 于 2026-10-16 验收 r1，保留 BACKFILL 高度修正及自检、无独立 QA 的事实；本轮仅状态收尾，未追加测试。 |
| CU-004 | owner_accepted | [r1](plans/CU-004-page-design-samples/spec.md) | Human Owner 于 2026-10-16 验收 r1，保留原独立 QA 证据；本轮仅状态收尾，未追加测试。 |
| CU-005 | owner_accepted | [r1](plans/CU-005-design-profile-editor/spec.md) | Human Owner 于 2026-10-16 验收 r1，保留编辑、本地草稿及公共 JSON/CSS 生成的原独立 QA 证据；本轮仅 CU 状态收尾，未追加测试。 |
| CU-006 | owner_accepted | [r1](plans/CU-006-live-design-preview/spec.md) | Human Owner 于 2026-10-16 验收 r1，保留颜色控件与左右同屏预览的原独立 QA 证据；本轮仅 CU 状态收尾，未追加测试。 |
| CU-007 | owner_accepted | [r1](plans/CU-007-apply-shared-design-profile/spec.md) | Human Owner 于 2026-10-16 确认公共样式应用后重启仍保留并接受 r1；保留原独立 QA，用户应用的卡内边距18保持不变。本轮仅状态收尾，未追加应用测试。 |

CU 当前包含轻量 Tauri 设计工作台与公共 UI 源码出口。旧采集执行链已移除，实际 Agent 接入由后续独立任务处理。

完整目录见 [CU 任务目录](plans/README.zh-CN.md)。各任务只保留一份 CU 所属 bundle，根目录历史任务保持原位。
