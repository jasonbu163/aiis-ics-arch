# Data Acquisition Agent 计划

[English](PLAN.md)

本 PLAN 管理 DAA 实施任务；[AW PLAN](../PLAN.zh-CN.md)管理跨工程阶段与依赖。历史工程初始化及已验收设计 bundle 保持根目录原位。

| Task ID | 状态 | 规格 | 最新事实 / 下一 gate |
| --- | --- | --- | --- |
| DAA-001 | owner_accepted | [r1](plans/DAA-001-cu-layout-migration/spec.md) | Human Owner 于 2026-10-17 验收 r1；新的 fresh Verification 通过，F-001/F-002 关闭，原失败历史保留。仅阶段 A 布局与既有功能兼容，B/C 实施另批。 |
| DAA-002 | qa_passed | [r2](plans/DAA-002-local-acquisition-loop/spec.md) | 独立QA4已通过受控阶段B的AC01–AC20，F-001–F-004均已解除，全部失败历史及76份原样本保留。待Human Owner最终验收；缺省legacy模式保持，阶段C、Backend/SMA、DS联调及真实现场动作仍排除。 |
| DAA-003 | qa_passed | [r1](plans/DAA-003-sqlite-only-startup/spec.md) | 新的独立QA2已通过，[checklist](plans/DAA-003-sqlite-only-startup/checklist.md) 确认F-001/F-002解除并完整保留QA1失败历史。普通入口采用唯一SQLite，YAML仅首次空实例迁入停用草稿，已有配置/历史优先保留。必要增量与原受控原生保存重开证据已核准，自有测试进程/15191已释放、证据保留；Human Owner最终验收待定。 |
| DAA-004 | qa_passed | [r1](plans/DAA-004-migration-notice-and-source-import-validation/spec.md) | 新的独立Verification通过AC01–AC08，有限README/界面调整及受控三点DB/UDT导入闭环已完成；操作差异和观察限制保留，已有配置/历史与SQLite防重回执保持。待Human Owner最终验收；阶段C和真实TIA/PLC联调仍属范围外。 [checklist](plans/DAA-004-migration-notice-and-source-import-validation/checklist.md) |
| DAA-005 | owner_accepted | [r1](plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md) | Human Owner已于2026-10-19最终验收精确DAA-005 r1，独立QA2已通过AC01–AC13。本次仅验收收尾，原失败和原生证据保留，未追加测试或实现改动。 [checklist](plans/DAA-005-multi-db-source-import-and-nested-offsets/checklist.md). |
| DAA-007 | `implementation_in_progress`（r2） | [r2](plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) | r2 B0/P1/P2已完成：YAML常驻链退役、最小.env/profile、标准启动和UI显式读取控制已写入正式源码，必要增量自检通过、候选冻结。当前awaiting_owner_native；M01–M09、同库对账及fresh核验待发生，阶段C排除。 |
| DAA-006 | owner_accepted | [r3](plans/DAA-006-point-naming-and-import-reuse/spec.md) | Human Owner于2026-10-20最终验收r3及另行DIRECT界面调整；独立AC01–AC20核验、原blocked历史及原生限度保留。验收源码已固定，临时资源已归档/清理；整体B、DS及阶段C门禁保持。 |

完整任务见[DAA 任务目录](plans/README.zh-CN.md)。[ARCH-AW-003 r3 详细设计](../../docs/AIIS_DAA_Detailed_Design.md)已获最终验收，设计验收不提供实施批准。

DAA 阶段 B 整体仍未关闭，已有受控本地证据和已验收增量继续有效；仍需取得满足联调要求且独立验收的 DS 协议基线，再另批 DAA–DS S7 读取至 SQLite 联调，完成 fresh QA 与 Human Owner 验收。阶段 C 实施在 B 整体验收及 Backend API 合同稳定后推进。上表各任务状态保留其原有有限范围。具体接续条件见 [DAA-006 r3 §9](plans/DAA-006-point-naming-and-import-reuse/spec.md#9-ds-接续清单与-stage-b--stage-c-依赖)。
