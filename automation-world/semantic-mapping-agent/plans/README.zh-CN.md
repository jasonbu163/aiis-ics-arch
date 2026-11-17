# SMA 任务目录

[English](README.md)

[SMA PLAN](../PLAN.zh-CN.md) 是当前任务看板。下表链接各任务唯一的权威 bundle，角色文档在对应生命周期 gate 才创建。

| Task ID | 唯一规格 / 关系 | 实施记录 | 独立验证 |
| --- | --- | --- | --- |
| SMA-001 | [r2 总规格](SMA-001-cu-integration-and-scope-cleanup/spec.md)，草案 | 总 tasks 未创建。通过已批准的子任务推进实施。 | 总 checklist 未创建。SMA-002、SMA-003 和 SMA-004 r1 已验收。 |
| SMA-002 | [r1 职责清理](SMA-002-scope-cleanup/spec.md)；SMA-001 获批子任务 | [tasks](SMA-002-scope-cleanup/tasks.md)；developer_handoff，精确候选 af7140357f2a81fa6a2870aed1c2d092dfe4e64ab7795dbf472cf62cdbcff6e2 | [checklist](SMA-002-scope-cleanup/checklist.md)；qa_passed、owner_accepted 仅对无漂移候选生效，B1 Owner 处置及事件历史保留 |
| SMA-003 | [r1 CU 接入](SMA-003-cu-integration/spec.md)；精确 CU 阶段于 2026-11-04 获最终验收 | [tasks](SMA-003-cu-integration/tasks.md)；developer_handoff，候选 ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf | [checklist](SMA-003-cu-integration/checklist.md#owner-acceptance-r1)；owner_accepted / qa_passed，N1/N2 已关闭；历史失败、验证限制及资源保留边界维持 |
| SMA-004 | [r1 配置独立化](SMA-004-local-configuration/spec.md)，owner_approved | [tasks](SMA-004-local-configuration/tasks.md)，rework-1 developer_handoff，53 项 9d514bc4 候选 | [验收记录](SMA-004-local-configuration/checklist.md)记录独立 QA2 和 2026-11-14 Owner 验收，含 QA1 历史及取证限制。 |
| SMA-005 | [r1 页面交互首批](SMA-005-page-interaction/spec.md)，SMA-001 已批准子任务 | [tasks](SMA-005-page-interaction/tasks.md)，#4 和 #6 已交接 | [验证记录](SMA-005-page-interaction/checklist.md)，独立离线检查通过，待 Human Owner 补齐原生 GET 手测证据，当前 qa_blocked。 |
| SMA-006 | [r1 弹窗交互首批](SMA-006-dialog-interaction/spec.md)，SMA-001 子任务草案 | 等待范围批准 | 等待 Development 交接 |
| SMA-007 | [r1 开发 profile 路径对齐](SMA-007-dev-profile-path/spec.md)，SMA-001 已批准子任务 | [tasks](SMA-007-dev-profile-path/tasks.md#developer_handoff-rework-2)，第二轮返工交接 | [验证记录](SMA-007-dev-profile-path/checklist.md)，第二轮返工候选独立验证通过，待 Human Owner 最终验收。 |

各子任务独立批准范围、验证和验收。执行阶段④–⑥的目标与依赖见总规格。原 r1 草案保留为[历史快照](SMA-001-cu-integration-and-scope-cleanup/evidence/r1-before-task-split/spec.md)。
