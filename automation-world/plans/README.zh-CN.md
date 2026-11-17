# Automation World 任务目录

[English](README.md)

| Task ID | 唯一规格 | 实施记录 | 独立验证 |
| --- | --- | --- | --- |
| ARCH-PLC-001 | [r5 设计](ARCH-PLC-001-shared-plc-point-json/spec.md)；`owner_approved` | 未创建；软件实施另项 | 未创建；待实际 Development 交接 |
| device-simulator::DS-004 | [r2 双语显示名](../device-simulator/plans/DS-004-bilingual-point-display-names/spec.md)；`owner_approved` | [tasks](../device-simulator/plans/DS-004-bilingual-point-display-names/tasks.md)；r2 `developer_handoff` | [checklist](../device-simulator/plans/DS-004-bilingual-point-display-names/checklist.md)；r1 QA1/QA2/QA3 `qa_failed`，r2 QA4 `qa_blocked` |
| aiis-ics-arch::DAA-018 | [r3 双语显示名](../data-acquisition-agent/plans/DAA-018-bilingual-point-display-names/spec.md)；`owner_approved` | [tasks](../data-acquisition-agent/plans/DAA-018-bilingual-point-display-names/tasks.md)；返工已交接，原生隔离事件已记录 | [checklist](../data-acquisition-agent/plans/DAA-018-bilingual-point-display-names/checklist.md)；QA1 `qa_failed`，QA2 `qa_blocked` |
| device-simulator::DS-003 | [r5 导出规格](../device-simulator/plans/DS-003-plc-json-export/spec.md)；`owner_approved` | [tasks](../device-simulator/plans/DS-003-plc-json-export/tasks.md)；返修已交接 | [checklist](../device-simulator/plans/DS-003-plc-json-export/checklist.md)；QA1 `qa_failed`，QA2 `qa_passed`，待 Owner 验收 |
| aiis-ics-arch::DAA-017 | [r5 导入规格](../data-acquisition-agent/plans/DAA-017-plc-json-import/spec.md)；`owner_approved` | [tasks](../data-acquisition-agent/plans/DAA-017-plc-json-import/tasks.md)；返修已交接 | [checklist](../data-acquisition-agent/plans/DAA-017-plc-json-import/checklist.md)；QA1 `qa_failed`，QA2 `qa_passed`，待 Owner 验收 |
| SMA-001 | [r2 总规格](../semantic-mapping-agent/plans/SMA-001-cu-integration-and-scope-cleanup/spec.md)，草案 | 子任务交接见 [SMA 目录](../semantic-mapping-agent/plans/README.zh-CN.md) | SMA-002、SMA-003 已验收。[SMA-004 r1 于 2026-11-14 验收](../semantic-mapping-agent/plans/SMA-004-local-configuration/checklist.md#owner-acceptance-r1)，独立 QA2 已通过。总体验收待定。 |
| ARCH-AW-007 | [r2 spec](../../plans/ARCH-AW-007-general-agent-fleet-roadmap/spec.md)；文档范围已批准，完整 r1 保留 | [r2 tasks](../../plans/ARCH-AW-007-general-agent-fleet-roadmap/tasks.md)；developer_handoff，原 DEV 自检及完整 r1 历史保留 | [r2 checklist](../../plans/ARCH-AW-007-general-agent-fleet-roadmap/checklist.md)；2026-10-21 owner_accepted，原独立 AC01–AC14 QA/r1 证据保留，校验归档留存、自有临时资源已清理，未追加测试 |
| ARCH-AW-006 | [r2 spec](../../plans/ARCH-AW-006-unified-flow-agent-design/spec.md)；owner_approved 设计，完整 r1 保留 | 未创建；文档实施归 007 r2，软件范围/批准另立待定 | 未创建；文档 QA 记录归 007 r2，软件 QA 范围/批准另立待定 |
| ARCH-AW-001 | [r1 spec](../../plans/ARCH-AW-001-agent-foundation/spec.md) | [tasks](../../plans/ARCH-AW-001-agent-foundation/tasks.md) | [checklist](../../plans/ARCH-AW-001-agent-foundation/checklist.md)；2026-10-14 owner_accepted，保留原qa_passed；本轮未追加测试 |
| CU-001 | [r1 spec](../console-ui/plans/CU-001-workbench-foundation/spec.md)；draft，归属 CU | 未开始；待范围批准 | 未开始 |

本目录链接各任务唯一的 owning bundle，不复制任务正文。ARCH-AW-001 保持在仓库根目录；CU-001 归属 [CU PLAN](../console-ui/PLAN.zh-CN.md)。整体阶段和依赖归 [AW PLAN](../PLAN.zh-CN.md)。
