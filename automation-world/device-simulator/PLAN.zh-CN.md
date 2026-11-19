# DS计划

[English](PLAN.md) · [任务目录](plans/README.zh-CN.md)

本工程 PLAN 管理 DS 后续产品任务；根目录和 AW 只保留总体摘要及入口。根 ARCH-AW-005 历史原件保持原位；Human Owner已于2026-10-27（Asia/Shanghai）最终验收DS-001 r1及ARCH-AW-005 r5。

| 任务 | 状态 | 范围与下一步 |
| --- | --- | --- |
| [DS-005 r3：双向 PLC JSON](plans/DS-005-plc-json-bidirectional/spec.md) | `qa_passed`（r3 文档）；r2 `qa_blocked` | QA2 因父设计的往返证据未闭合而阻塞，见 [checklist](plans/DS-005-plc-json-bidirectional/checklist.md)。本次文档复核通过，待 Human Owner 最终验收。 |
| [DS-004 r3：点位中英文显示名](plans/DS-004-bilingual-point-display-names/spec.md) | `qa_passed`（r3 文档）；r2 `qa_blocked` | QA4 的合成检查未发现新的确定性失败；必需的原生检查因隔离事件仍暂停。本次文档复核通过，待 Human Owner 最终验收。 |
| [DS-003 r5：按 PLC 导出点位 JSON](plans/DS-003-plc-json-export/spec.md) | `qa_passed` | 返修后的 DS→DAA 原生联测完成，QA2 已通过；待 Human Owner 验收。 |
| [DS-002 r2：Modbus TCP 模拟与 S7 兼容](plans/DS-002-multi-protocol-simulation-and-device-debugging/spec.md) | `draft` | 规格已补充六页界面对比、节点图、S7 兼容合同及 AC01–AC12。待精确批准 A0 和有条件的 A1 实施范围。设备读写调试列入后续阶段。 |
| [DS-001 r1：策略表格、批量编辑与界面整改](plans/DS-001-policy-table-and-usability/spec.md) | `owner_accepted` | Human Owner于2026-10-27接受DS当前版本，见[验收及收尾](plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001)。策略/批量编辑、输入/易用性、纯文字手册及另批DIRECT整改已交付；[DEV记录](plans/DS-001-policy-table-and-usability/tasks.md)保留原时点，独立QA未执行（DS-001例外）。本轮只收尾，未追加功能或整套QA。 |
| [ARCH-AW-005 r5：历史产品基线](../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md) | `owner_accepted` | Human Owner于2026-10-27最终接受r5，见[验收及资源保留](../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5)。原QA4的qa_passed按精确候选保留，全部旧失败及G0退役证据保留；后续DS-001人工验收及DIRECT修正不倒记为旧QA4证据。 |
| [aiis-ics-arch::DAA-007 r2：关联联调启动配置](../data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) | `owner_accepted` | 关联DAA-007 r2及本次受控阶段B已于2026-10-30验收。DS启动配置增量按DAA记录接受，不倒记为DS旧QA/接受。历史限制保留，阶段C/自动启动/现场另项。 |

DAA–DS读取至SQLite联调另批，阶段C暂不开展；本任务人工验收例外不改变后续联调核验要求。
