# DS任务目录

[English](README.md) · [DS计划](../PLAN.zh-CN.md)

后续 DS 产品任务的唯一范围归本地 `plans/<任务>/spec.md`，进度归本工程 PLAN。ARCH-AW-005作为根目录历史关联保留，不搬动、复制或继承其审批和验收。

| 任务 | 状态 | 范围入口 | 后续记录 |
| --- | --- | --- | --- |
| DS-005 双向 PLC JSON | `qa_passed`（r3 文档）；r2 `qa_blocked` | [r3 规格（收尾）](DS-005-plc-json-bidirectional/spec.md) | [Development](DS-005-plc-json-bidirectional/tasks.md)；[QA2](DS-005-plc-json-bidirectional/checklist.md) 因父设计证据阻塞。；r3 文档复核 `qa_passed`，待 Human Owner 验收 |
| DS-004 点位中英文显示名 | `qa_passed`（r3 文档）；r2 `qa_blocked` | [r3 spec（收尾）](DS-004-bilingual-point-display-names/spec.md) | [Development 记录](DS-004-bilingual-point-display-names/tasks.md)；[Verification checklist](DS-004-bilingual-point-display-names/checklist.md)；r1 的 QA3 `qa_failed`，r2 的 QA4 `qa_blocked`。；r3 文档复核 `qa_passed`，待 Human Owner 验收 |
| DS-003 按 PLC 导出点位 JSON | `qa_passed` | [r5 spec](DS-003-plc-json-export/spec.md) | [Development 记录](DS-003-plc-json-export/tasks.md)；[QA1 失败、QA2 通过](DS-003-plc-json-export/checklist.md)；待 Owner 验收。 |
| DS-002 Modbus TCP 模拟与 S7 兼容 | `draft` | [r2 spec](DS-002-multi-protocol-simulation-and-device-debugging/spec.md) | 待批准 A0 和 A1 实施范围，A0 通过后才进入 A1。实施记录在获批后创建，核验记录在实施交接后创建。设备读写调试列入后续阶段。 |
| DS-001 策略表格、批量编辑与界面整改 | `owner_accepted` | [r1 spec](DS-001-policy-table-and-usability/spec.md) | Human Owner于2026-10-27最终接受当前版本，见[验收/收尾](DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001)。[实施/自检记录](DS-001-policy-table-and-usability/tasks.md)及[纯文字手册](../USER_GUIDE.zh-CN.md)保留；独立QA/checklist未执行（本任务例外）。 |
| 关联aiis-ics-arch::DAA-007 r2启动增量 | `owner_accepted` | [DAA唯一spec](../../data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) | 关联DAA-007 r2及本次受控阶段B已于2026-10-30验收。DS启动配置增量按DAA记录接受，不倒记为DS旧QA/接受。历史限制保留，阶段C/自动启动/现场另项。 |

历史基线：[ARCH-AW-005 r5 spec](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md) · [DEV记录](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/tasks.md) · [核验及2026-10-27 Owner最终接受](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5)。历史技术QA与Owner接受分层保留；DAA–DS读取至SQLite联调另批，阶段C暂不开展。
