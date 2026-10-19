# DAA 任务目录

[English](README.md)

DAA 实施任务各有唯一的本地 bundle。这里只链接已存在的角色文档；Development 和 Verification 记录在真实生命周期 gate 才创建。

| 任务 | 状态 | PM 范围 | Development | Verification |
| --- | --- | --- | --- | --- |
| DAA-001 CU 布局与既有页面迁移 | owner_accepted | [spec.md](DAA-001-cu-layout-migration/spec.md)；Human Owner 于 2026-10-17 精确批准 r1 | [tasks.md](DAA-001-cu-layout-migration/tasks.md) 第7节；最新阶段 A 精确交接及定向返工自检 | [checklist.md](DAA-001-cu-layout-migration/checklist.md)；新的 fresh Verification qa_passed，F-001/F-002 关闭且失败历史保留；Human Owner 于 2026-10-17 验收 r1，见第7节 |
| DAA-002 本地采集闭环 | qa_passed | [spec.md](DAA-002-local-acquisition-loop/spec.md)；r2精确范围批准保持 | [tasks.md](DAA-002-local-acquisition-loop/tasks.md)；精确r2开发及文档返工已交接，代码/binary与76原样本保留 | [checklist.md](DAA-002-local-acquisition-loop/checklist.md)；独立QA4通过AC01–AC20，F-001–F-004解除、QA1–QA3失败原文保留；Human Owner最终验收待完成 |
| DAA-003 SQLite 唯一入口与 YAML 迁入 | qa_passed | [spec.md](DAA-003-sqlite-only-startup/spec.md)；2026-10-19 精确批准 r1 | [tasks.md](DAA-003-sqlite-only-startup/tasks.md)；精确实施及QA1界面返工已交接，先前失败及限制保留 | [checklist.md](DAA-003-sqlite-only-startup/checklist.md)；新的独立QA2通过，F-001/F-002已解除，QA1失败历史保留；Human Owner最终验收待定 |
| DAA-004 迁入提示收敛与最小源码导入验证 | qa_passed | [spec.md](DAA-004-migration-notice-and-source-import-validation/spec.md)；2026-10-19 精确批准 r1 | [tasks.md](DAA-004-migration-notice-and-source-import-validation/tasks.md)；最终developer_handoff及原生证据/限制保留 | [checklist.md](DAA-004-migration-notice-and-source-import-validation/checklist.md)；新的独立核验通过AC01–AC08，操作差异/观察限制保留；Human Owner最终验收待定 |
| DAA-005 多DB导入与嵌套辅助偏移 | owner_accepted | [spec.md](DAA-005-multi-db-source-import-and-nested-offsets/spec.md)；2026-10-19精确批准r1 | [tasks.md](DAA-005-multi-db-source-import-and-nested-offsets/tasks.md)；精确r1返工交接与原始失败证据保留 | [checklist.md](DAA-005-multi-db-source-import-and-nested-offsets/checklist.md)；2026-10-19 Owner验收r1；QA2通过AC01–AC13与原失败保留；仅收尾，无新增测试 |

[DAA PLAN](../PLAN.zh-CN.md)是本地驾驶舱；[AW PLAN](../../PLAN.zh-CN.md)管理跨工程依赖。历史根目录 bundle 保持原位。
