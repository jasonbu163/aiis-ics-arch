# Data Acquisition Agent 计划

[English](PLAN.md)

本 PLAN 管理 DAA 实施任务；[AW PLAN](../PLAN.zh-CN.md)管理跨工程阶段与依赖。历史工程初始化及已验收设计 bundle 保持根目录原位。

| Task ID | 状态 | 规格 | 最新事实 / 下一 gate |
| --- | --- | --- | --- |
| DAA-001 | owner_accepted | [r1](plans/DAA-001-cu-layout-migration/spec.md) | Human Owner 于 2026-10-17 验收 r1；新的 fresh Verification 通过，F-001/F-002 关闭，原失败历史保留。仅阶段 A 布局与既有功能兼容，B/C 实施另批。 |
| DAA-002 | `owner_accepted` | [r2](plans/DAA-002-local-acquisition-loop/spec.md) | Human Owner于2026-10-30验收r2，QA4通过AC01–AC20、F-001–F-004解除。本地采集、双SQLite、容量恢复及受控原生基线已接受。失败历史和历史raw当前可用性限制保留；后续入口退役/DS联调归DAA-003/007。 |
| DAA-003 | `owner_accepted` | [r1](plans/DAA-003-sqlite-only-startup/spec.md) | Human Owner于2026-10-30验收r1，QA2解除F-001/F-002。接受SQLite唯一入口及历史一次性停用草稿迁入；DAA-007已退出普通迁入链。配置/历史和私有回执保护保持，失败及历史raw当前可用性限制保留。 |
| DAA-004 | `owner_accepted` | [r1](plans/DAA-004-migration-notice-and-source-import-validation/spec.md) | Human Owner于2026-10-30验收r1，AC01–AC08核验通过双语说明、界面收敛及受控三点DB/UDT导入。操作差异、观察及历史raw当前可用性限制保留，配置/历史和私有回执保持。 |
| DAA-005 | owner_accepted | [r1](plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md) | Human Owner已于2026-10-19最终验收精确DAA-005 r1，独立QA2已通过AC01–AC13。本次仅验收收尾，原失败和原生证据保留，未追加测试或实现改动。 [checklist](plans/DAA-005-multi-db-source-import-and-nested-offsets/checklist.md). |
| DAA-007 | `owner_accepted` | [r2](plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) | Human Owner于2026-10-30验收r2，并确认阶段B在本次受控DS联调范围内完成；AC01–AC22核验及8590份样本/4295轮完整重开比较通过。历史checkpoint缺失和15:27来源未明事项继续跟踪。配置/历史及原联调profile保留；阶段C、自动启动策略和现场验证另项。 |
| DAA-006 | owner_accepted | [r3](plans/DAA-006-point-naming-and-import-reuse/spec.md) | Human Owner于2026-10-20最终验收r3及另行DIRECT界面调整；独立AC01–AC20核验、原blocked历史及原生限度保留。验收源码已固定，临时资源已归档/清理；后续受控阶段B验收见DAA-007，阶段C另项。 |

完整任务见[DAA 任务目录](plans/README.zh-CN.md)。[ARCH-AW-003 r3 详细设计](../../docs/AIIS_DAA_Detailed_Design.md)已获最终验收，设计验收不提供实施批准。

Human Owner于2026-10-30验收DAA-002 r2、DAA-003 r1、DAA-004 r1和DAA-007 r2，确认[阶段B在本次受控DS联调范围内完成](plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2)。DS既有接受与本次S7读取至SQLite证据分别保留；历史证据限制和来源未明事项继续跟踪。已有SQLite配置、历史和原联调profile保留；阶段C、自动启动策略及真实现场验证另行推进，本次不启动。
