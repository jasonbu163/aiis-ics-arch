# DAA 任务目录

[English](README.md)

DAA 实施任务各有唯一的本地 bundle。这里只链接已存在的角色文档；Development 和 Verification 记录在真实生命周期 gate 才创建。

| 任务 | 状态 | PM 范围 | Development | Verification |
| --- | --- | --- | --- | --- |
| DAA-001 CU 布局与既有页面迁移 | owner_accepted | [spec.md](DAA-001-cu-layout-migration/spec.md)；Human Owner 于 2026-10-17 精确批准 r1 | [tasks.md](DAA-001-cu-layout-migration/tasks.md) 第7节；最新阶段 A 精确交接及定向返工自检 | [checklist.md](DAA-001-cu-layout-migration/checklist.md)；新的 fresh Verification qa_passed，F-001/F-002 关闭且失败历史保留；Human Owner 于 2026-10-17 验收 r1，见第7节 |
| DAA-002 本地采集闭环 | `owner_accepted` | [spec.md](DAA-002-local-acquisition-loop/spec.md)；r2精确范围批准保持 | [tasks.md](DAA-002-local-acquisition-loop/tasks.md)；精确r2开发及文档返工已交接，历史实施与原raw引用按bundle保留 | [checklist.md](DAA-002-local-acquisition-loop/checklist.md#owner-acceptance-r2); Human Owner于2026-10-30验收r2，QA4通过AC01–AC20、F-001–F-004解除。本地采集、双SQLite、容量恢复及受控原生基线已接受。失败历史和历史raw当前可用性限制保留；后续入口退役/DS联调归DAA-003/007。 |
| DAA-003 SQLite 唯一入口与 YAML 迁入 | `owner_accepted` | [spec.md](DAA-003-sqlite-only-startup/spec.md)；2026-10-19 精确批准 r1 | [tasks.md](DAA-003-sqlite-only-startup/tasks.md)；精确实施及QA1界面返工已交接，先前失败及限制保留 | [checklist.md](DAA-003-sqlite-only-startup/checklist.md#owner-acceptance-r1); Human Owner于2026-10-30验收r1，QA2解除F-001/F-002。接受SQLite唯一入口及历史一次性停用草稿迁入；DAA-007已退出普通迁入链。配置/历史和私有回执保护保持，失败及历史raw当前可用性限制保留。 |
| DAA-004 迁入提示收敛与最小源码导入验证 | `owner_accepted` | [spec.md](DAA-004-migration-notice-and-source-import-validation/spec.md)；2026-10-19 精确批准 r1 | [tasks.md](DAA-004-migration-notice-and-source-import-validation/tasks.md)；最终developer_handoff及原生证据/限制保留 | [checklist.md](DAA-004-migration-notice-and-source-import-validation/checklist.md#owner-acceptance-r1); Human Owner于2026-10-30验收r1，AC01–AC08核验通过双语说明、界面收敛及受控三点DB/UDT导入。操作差异、观察及历史raw当前可用性限制保留，配置/历史和私有回执保持。 |
| DAA-005 多DB导入与嵌套辅助偏移 | owner_accepted | [spec.md](DAA-005-multi-db-source-import-and-nested-offsets/spec.md)；2026-10-19精确批准r1 | [tasks.md](DAA-005-multi-db-source-import-and-nested-offsets/tasks.md)；精确r1返工交接与原始失败证据保留 | [checklist.md](DAA-005-multi-db-source-import-and-nested-offsets/checklist.md)；2026-10-19 Owner验收r1；QA2通过AC01–AC13与原失败保留；仅收尾，无新增测试 |
| DAA-007 DS联调、时间与启动配置 | `owner_accepted` | [spec.md](DAA-007-ds-joint-validation-and-time-contract/spec.md)；精确r2已批准 | [tasks.md](DAA-007-ds-joint-validation-and-time-contract/tasks.md)保留r1/r2历史、Owner补证、闭库对账及G1 developer_handoff | [checklist.md](DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2); Human Owner于2026-10-30验收r2，并确认阶段B在本次受控DS联调范围内完成；AC01–AC22核验及8590份样本/4295轮完整重开比较通过。历史checkpoint缺失和15:27来源未明事项继续跟踪。配置/历史及原联调profile保留；阶段C、自动启动策略和现场验证另项。 |
| DAA-006 点位技术命名与导入能力复用准备 | owner_accepted | [spec.md](DAA-006-point-naming-and-import-reuse/spec.md)；2026-10-19 精确批准 r3；迁入展示收尾和有限警告清理前置于命名/复用 | [tasks.md](DAA-006-point-naming-and-import-reuse/tasks.md)；精确r3 developer_handoff，最终同库检查及原生限制均已记录 | [checklist.md](DAA-006-point-naming-and-import-reuse/checklist.md#owner-acceptance-r3)；Human Owner于2026-10-20验收r3及另行DIRECT界面调整；独立AC01–AC20核验、原blocked历史/原生限度保留；源码已固定，临时资源已收尾，后续受控阶段B验收见DAA-007，阶段C另项 |

[DAA PLAN](../PLAN.zh-CN.md)是本地驾驶舱；[AW PLAN](../../PLAN.zh-CN.md)管理跨工程依赖。历史根目录 bundle 保持原位。
