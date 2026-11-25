# Semantic Mapping Agent 计划

[English](PLAN.md)

本 PLAN 管理 SMA 任务；[AW PLAN](../PLAN.zh-CN.md)管理跨工程依赖。历史 ARCH-AW-001 证据保持在仓库根目录。

| Task ID | 状态 | 规格 | 最新事实 / 下一 gate |
| --- | --- | --- | --- |
| SMA-001 | qa_blocked | [r3 整体实施规格](plans/SMA-001-cu-integration-and-scope-cleanup/spec.md) | [QA3 对 rework-2 的 14 项隔离验收通过](plans/SMA-001-cu-integration-and-scope-cleanup/checklist.md#qa3--rework-2-独立复验)，等 Human Owner 完成真实 dev 的 AC14 并决定最终验收。 |
| SMA-002 | owner_accepted | [r1 职责清理](plans/SMA-002-scope-cleanup/spec.md) | [独立验证与 Owner 收口](plans/SMA-002-scope-cleanup/checklist.md)固定候选 af7140357f2a81fa6a2870aed1c2d092dfe4e64ab7795dbf472cf62cdbcff6e2，确认无漂移，并在 Owner 接受已披露影响与限制后关闭 B1。QA 通过，条件性清理验收仅对此候选生效；原事件历史与未来 profile 保护不变。 |
| SMA-003 | owner_accepted | [r1 CU 接入](plans/SMA-003-cu-integration/spec.md) | [独立验证与 Owner 验收](plans/SMA-003-cu-integration/checklist.md#owner-acceptance-r1)固定候选 ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf：QA 通过、N1/N2 已关闭，Human Owner 于 2026-11-04 最终验收本 CU 阶段。历史失败及原生跨进程偏好持久性未实测限制保留；API/DAA 对接和 SMA 总体完成另项。 |
| SMA-004 | owner_accepted | [r1 配置独立化](plans/SMA-004-local-configuration/spec.md) | [Owner 于 2026-11-14 验收](plans/SMA-004-local-configuration/checklist.md#owner-acceptance-r1)独立 QA2 通过的精确候选，覆盖本地 SQLite 配置、备份恢复及纯预览。正常投递处于关闭状态。 |
| SMA-005 | qa_blocked | [r1 页面交互首批](plans/SMA-005-page-interaction/spec.md) | OpenAPI 只读测试（#4）和投递可用状态（#6）的独立离线检查通过，[验证记录](plans/SMA-005-page-interaction/checklist.md)等待 Human Owner 补齐原生 GET 手测证据。 |
| SMA-006 | draft | [r1 弹窗交互首批](plans/SMA-006-dialog-interaction/spec.md) | 框内错误反馈（#7）、未保存输入保护（#8）和长弹窗滚动（#9）。 |
| SMA-007 | qa_passed | [r1 开发 profile 路径对齐](plans/SMA-007-dev-profile-path/spec.md) | 相对和绝对路径的[独立验证](plans/SMA-007-dev-profile-path/checklist.md)通过，待 Human Owner 最终验收。 |
| SMA-008 | qa_blocked | [r3 现有采集 API 手动回环](plans/SMA-008-acquisition-data-get/spec.md) | rework-1 的[独立复验](plans/SMA-008-acquisition-data-get/checklist.md)通过软件与夹具检查。AC04 等待 Human Owner 操作 dev POST、核对回执及历史回读。 |
| SMA-009 | qa_passed | [r1 工作区与手工回环界面](plans/SMA-009-workspace-and-loopback-ui/spec.md) | 首批 rework-1 [独立复验](plans/SMA-009-workspace-and-loopback-ui/checklist.md)通过，等待 Human Owner 最终验收。 |
| SMA-010 | draft | [r2 炉温 → 实绩单次闭环](plans/SMA-010-single-performance-mapping/spec.md) | 单次闭环草案保留作参考，炉温 → 实绩已列入 SMA-001 r3 整体验收用例。 |

实施顺序为 **SMA-002 → SMA-003 → SMA-004**。三个阶段均已验收。整体实施范围与验收用例见 r3 草案。

实际角色文件和待创建阶段见[任务目录](plans/README.zh-CN.md)。
