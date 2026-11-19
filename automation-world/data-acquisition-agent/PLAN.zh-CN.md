# Data Acquisition Agent 计划

[English](PLAN.md)

本 PLAN 管理 DAA 实施任务；[AW PLAN](../PLAN.zh-CN.md)管理跨工程阶段与依赖。历史工程初始化及已验收设计 bundle 保持根目录原位。

| Task ID | 状态 | 规格 | 最新事实 / 下一 gate |
| --- | --- | --- | --- |
| DAA-019 | `qa_passed`（r3 文档）；r2 `qa_blocked` | [r3 双向 JSON（收尾）](plans/DAA-019-plc-json-bidirectional/spec.md) | QA2 因历史与同次导入证据未闭合而阻塞，见 [checklist](plans/DAA-019-plc-json-bidirectional/checklist.md)。本次文档复核通过，待 Human Owner 最终验收。 |
| DAA-018 | `qa_passed`（r4 文档）；r3 `qa_blocked` | [r4 双语显示名（收尾）](plans/DAA-018-bilingual-point-display-names/spec.md) | QA2 已复核预览绕过修复；必需的原生检查因隔离事件仍暂停。本次文档复核通过，待 Human Owner 最终验收。 |
| DAA-017 | `qa_passed`（r5） | [r5 导入规格](plans/DAA-017-plc-json-import/spec.md) | 返修后的 DS→DAA 原生联测完成，QA2 已通过；待 Human Owner 验收。 |
| DAA-016 | `owner_accepted`（r1） | [r1 规格](plans/DAA-016-docs-closeout/spec.md) | 文档收尾和 Windows 记录单通过独立 QA2，并获 Human Owner 最终验收。[tasks](plans/DAA-016-docs-closeout/tasks.md) · [checklist](plans/DAA-016-docs-closeout/checklist.md) |
| DAA-015 | `owner_accepted`（r1） | [r1 规格](plans/DAA-015-startup-automation-and-workbench/spec.md) | 工作台与启动设置通过独立 QA4，并获 Human Owner 验收；QA1–QA3 失败历史保留。[tasks](plans/DAA-015-startup-automation-and-workbench/tasks.md) · [checklist](plans/DAA-015-startup-automation-and-workbench/checklist.md) |
| DAA-014 | `owner_accepted`（r1） | [r1 规格](plans/DAA-014-unified-operator-guide/spec.md) | 统一操作文档通过独立 QA2，Human Owner 于 2026-11-14 最终验收。[tasks](plans/DAA-014-unified-operator-guide/tasks.md) · [checklist](plans/DAA-014-unified-operator-guide/checklist.md) |
| DAA-013 | `owner_accepted`（r1） | [r1 规格](plans/DAA-013-multi-plc-reporting-identity/spec.md) | Human Owner 已验收各轮独立验证范围，上报确认框可读性修正通过 QA6；Windows 原生验证另行跟踪。[tasks](plans/DAA-013-multi-plc-reporting-identity/tasks.md) · [checklist](plans/DAA-013-multi-plc-reporting-identity/checklist.md) |
| DAA-012 | `owner_accepted`（r1） | [r1 规格](plans/DAA-012-startup-warning-cleanup/spec.md) | Human Owner 已验收[独立验证](plans/DAA-012-startup-warning-cleanup/checklist.md)范围：macOS 开发启动无告警、49 项定向回归通过；Windows 原生验证另行跟踪。 |
| DAA-011 | `archived`（r1；旧指南已接替） | [r1 规格与历史决定](plans/DAA-011-dev-manual-refresh/spec.md#daa011-historical-disposition) | 原独立文档 QA 通过，当时未单独终验；现行指南由已验收的 DAA-014/016 接续。[tasks](plans/DAA-011-dev-manual-refresh/tasks.md) · [checklist](plans/DAA-011-dev-manual-refresh/checklist.md) |
| DAA-010 | `qa_failed`（r5）；r8 Mac 受控范围 `owner_accepted` | [r5 与 r8 规格](plans/DAA-010-sample-facts-upload/spec.md) | r8 兼容 profile 相对与绝对路径，保留预建目录前提并复用已有 Mac/dev 证据；首次自动创建目录的竞态仍未修复，Windows 原生验证另行跟踪。[tasks](plans/DAA-010-sample-facts-upload/tasks.md) · [checklist](plans/DAA-010-sample-facts-upload/checklist.md) |
| DAA-008 | `archived`（r4；旧 v1 方案停止） | [r4 规格与历史决定](plans/DAA-008-reliable-facts-upload/spec.md#daa008-historical-disposition) | 旧 B-RUN-01 不再推进；未完成的 B/AC18–AC20 和原 QA 结果保留，不追认通过。现行 v2 上报由 DAA-010 接续。[tasks](plans/DAA-008-reliable-facts-upload/tasks.md) · [checklist](plans/DAA-008-reliable-facts-upload/checklist.md) |
| DAA-001 | owner_accepted | [r1](plans/DAA-001-cu-layout-migration/spec.md) | Human Owner 于 2026-10-17 验收 r1；新的 fresh Verification 通过，F-001/F-002 关闭，原失败历史保留。仅阶段 A 布局与既有功能兼容，B/C 实施另批。 |
| DAA-002 | `owner_accepted` | [r2](plans/DAA-002-local-acquisition-loop/spec.md) | Human Owner于2026-10-30验收r2，QA4通过AC01–AC20、F-001–F-004解除。本地采集、双SQLite、容量恢复及受控原生基线已接受。失败历史和历史raw当前可用性限制保留；后续入口退役/DS联调归DAA-003/007。 |
| DAA-003 | `owner_accepted` | [r1](plans/DAA-003-sqlite-only-startup/spec.md) | Human Owner于2026-10-30验收r1，QA2解除F-001/F-002。接受SQLite唯一入口及历史一次性停用草稿迁入；DAA-007已退出普通迁入链。配置/历史和私有回执保护保持，失败及历史raw当前可用性限制保留。 |
| DAA-004 | `owner_accepted` | [r1](plans/DAA-004-migration-notice-and-source-import-validation/spec.md) | Human Owner于2026-10-30验收r1，AC01–AC08核验通过双语说明、界面收敛及受控三点DB/UDT导入。操作差异、观察及历史raw当前可用性限制保留，配置/历史和私有回执保持。 |
| DAA-005 | owner_accepted | [r1](plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md) | Human Owner已于2026-10-19最终验收精确DAA-005 r1，独立QA2已通过AC01–AC13。本次仅验收收尾，原失败和原生证据保留，未追加测试或实现改动。 [checklist](plans/DAA-005-multi-db-source-import-and-nested-offsets/checklist.md). |
| DAA-007 | `owner_accepted` | [r2](plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) | Human Owner于2026-10-30验收r2，并确认阶段B在本次受控DS联调范围内完成；AC01–AC22核验及8590份样本/4295轮完整重开比较通过。历史checkpoint缺失和15:27来源未明事项继续跟踪。配置/历史及原联调profile保留；阶段C、自动启动策略和现场验证另项。 |
| DAA-006 | owner_accepted | [r3](plans/DAA-006-point-naming-and-import-reuse/spec.md) | Human Owner于2026-10-20最终验收r3及另行DIRECT界面调整；独立AC01–AC20核验、原blocked历史及原生限度保留。验收源码已固定，临时资源已归档/清理；后续受控阶段B验收见DAA-007，阶段C另项。 |

完整任务见[DAA 任务目录](plans/README.zh-CN.md)。[ARCH-AW-003 r3 详细设计](../../docs/AIIS_DAA_Detailed_Design.md)已获最终验收，设计验收不提供实施批准。

Human Owner于2026-10-30验收DAA-002 r2、DAA-003 r1、DAA-004 r1和DAA-007 r2，确认[阶段B在本次受控DS联调范围内完成](plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2)。DS既有接受与本次S7读取至SQLite证据分别保留；历史证据限制和来源未明事项继续跟踪。已有SQLite配置、历史和原联调profile保留；阶段C、自动启动策略及真实现场验证另行推进，本次不启动。
