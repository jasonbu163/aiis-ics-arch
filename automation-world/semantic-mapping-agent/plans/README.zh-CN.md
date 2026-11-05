# SMA 任务目录

[English](README.md)

[SMA PLAN](../PLAN.zh-CN.md) 是当前任务看板。下表链接各任务唯一的权威 bundle，角色文档在对应生命周期 gate 才创建。

| Task ID | 唯一规格 / 关系 | 实施记录 | 独立验证 |
| --- | --- | --- | --- |
| SMA-001 | [r2 总规格](SMA-001-cu-integration-and-scope-cleanup/spec.md)；draft root，SMA-002/SMA-003 已接受、SMA-004 已单独获批 | 未创建；经获批子任务推进实施 | 未创建；无总体 QA verdict 或验收 |
| SMA-002 | [r1 职责清理](SMA-002-scope-cleanup/spec.md)；SMA-001 获批子任务 | [tasks](SMA-002-scope-cleanup/tasks.md)；developer_handoff，精确候选 af7140357f2a81fa6a2870aed1c2d092dfe4e64ab7795dbf472cf62cdbcff6e2 | [checklist](SMA-002-scope-cleanup/checklist.md)；qa_passed、owner_accepted 仅对无漂移候选生效，B1 Owner 处置及事件历史保留 |
| SMA-003 | [r1 CU 接入](SMA-003-cu-integration/spec.md)；精确 CU 阶段于 2026-11-04 获最终验收 | [tasks](SMA-003-cu-integration/tasks.md)；developer_handoff，候选 ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf | [checklist](SMA-003-cu-integration/checklist.md#owner-acceptance-r1)；owner_accepted / qa_passed，N1/N2 已关闭；历史失败、验证限制及资源保留边界维持 |
| SMA-004 | [r1 配置独立化](SMA-004-local-configuration/spec.md)；owner_approved，SMA-003 已接受 | [tasks](SMA-004-local-configuration/tasks.md)；rework-1 developer_handoff，53 项 9d514bc4 候选及六文件增量 | [checklist](SMA-004-local-configuration/checklist.md#qa2-r1)；QA2 qa_passed，F-QA1-001/002/003 已关闭；完整 QA1 失败历史及证明限制保留，Owner 最终验收 pending |

父任务只提供上下文，不转移范围批准、验证或验收。SMA-004 之后的阶段仅在总规格列目标和依赖，不创建空 bundle。原未实施 r1 草案保留为[历史快照](SMA-001-cu-integration-and-scope-cleanup/evidence/r1-before-task-split/spec.md)，不作为第二份活动规格。
