# Automation World 计划

[English](PLAN.md)

| Task ID | 状态 | 规格 | 最新事实 / 下一 gate |
| --- | --- | --- | --- |
| ARCH-PLC-002 | owner_accepted | [r1 导出命名与反馈](plans/ARCH-PLC-002-plc-json-export-feedback/spec.md) | QA2 通过回执返修复验，Human Owner 已验收 r1，见 [checklist](plans/ARCH-PLC-002-plc-json-export-feedback/checklist.md)。 |
| ARCH-PLC-001 | `qa_passed`（r8 文档）；r7 `owner_approved` | [r8 双向设计（收尾）](plans/ARCH-PLC-001-shared-plc-point-json/spec.md) | Human Owner 已批准保留旧版本的测试路径；已批准的 r6 保留。本次文档复核通过，待 Human Owner 最终验收。 |
| DS-005 | `qa_passed`（r3 文档）；r2 `qa_blocked` | [r3 双向 JSON（收尾）](device-simulator/plans/DS-005-plc-json-bidirectional/spec.md) | QA2：父设计的往返证据未闭合，见 [checklist](device-simulator/plans/DS-005-plc-json-bidirectional/checklist.md)。本次文档复核通过，待 Human Owner 最终验收。 |
| DAA-019 | `qa_passed`（r3 文档）；r2 `qa_blocked` | [r3 双向 JSON（收尾）](data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/spec.md) | QA2：历史与同次导入证据未闭合，见 [checklist](data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/checklist.md)。本次文档复核通过，待 Human Owner 最终验收。 |
| DS-004 | `qa_passed`（r3 文档）；r2 `qa_blocked` | [r3 双语显示名（收尾）](device-simulator/plans/DS-004-bilingual-point-display-names/spec.md) | QA4 的合成检查未发现新的确定性失败；必需的原生检查因隔离事件仍暂停。本次文档复核通过，待 Human Owner 最终验收。 |
| DAA-018 | `qa_passed`（r4 文档）；r3 `qa_blocked` | [r4 双语显示名（收尾）](data-acquisition-agent/plans/DAA-018-bilingual-point-display-names/spec.md) | QA2 已复核预览绕过修复；必需的原生检查因隔离事件仍暂停。本次文档复核通过，待 Human Owner 最终验收。 |
| DS-003 | qa_passed | [r5 导出规格](device-simulator/plans/DS-003-plc-json-export/spec.md) | 返修后的 DS→DAA 原生联测完成，QA2 已通过；待 Human Owner 验收。 |
| DAA-017 | qa_passed | [r5 导入规格](data-acquisition-agent/plans/DAA-017-plc-json-import/spec.md) | 返修后的 DS→DAA 原生联测完成，QA2 已通过；待 Human Owner 验收。 |
| SMA-001 | draft | [r2 总规格](semantic-mapping-agent/plans/SMA-001-cu-integration-and-scope-cleanup/spec.md) | SMA-002、SMA-003 已验收。[SMA-004 r1 于 2026-11-14 验收](semantic-mapping-agent/plans/SMA-004-local-configuration/checklist.md#owner-acceptance-r1)，独立 QA2 已通过。正常投递处于关闭状态。 |
| ARCH-AW-009 | `qa_blocked` | [r2 spec](../plans/ARCH-AW-009-ca-flow-editor-json/spec.md) | 已验证 CU 公共壳及部分原生交互，剩余原生复验受阻，FF 联合验收待进行。 |
| ARCH-AW-007 | owner_accepted | [r2](../plans/ARCH-AW-007-general-agent-fleet-roadmap/spec.md) | Human Owner 于 2026-10-21 最终验收精确 r2 文档，原独立 AC01–AC14 QA 保留。DAA、SMA 表格、CA 通用编排/内部连接器及未来全类型健康分工明确，首版无登录；完整 r1 历史/QA 保留，证据已归档，两处自有临时目录共 49 文件已清理，未改代码、未追加测试。 |
| ARCH-AW-006 | owner_approved | [r2](../plans/ARCH-AW-006-unified-flow-agent-design/spec.md) | 精确 r2 设计已批准：DAA 大量采集、SMA 表格/工作台、CA 节点编排/版本/上下文/扩展；首版无登录。完整 r1 保留，文档实施统一归 007 r2，软件工作另立范围。 |
| ARCH-AW-001 | owner_accepted | [r1](../plans/ARCH-AW-001-agent-foundation/spec.md) | CA已迁入并冻结，DAA/SMA可构建并独立启动；定向复核通过，Human Owner于2026-10-14接受r1；本轮未追加测试。UI与SQLite后续处理。 |

CA保留冻结兼容基线；后续采集发展由DAA承接。独立事实/业务provider已通过隔离QA；DAA上传及SMA执行/业务闭环仍另项。共享CU及各应用本地SQLite进展归下方所属计划。完整索引见[任务目录](plans/README.zh-CN.md)。

## 子工程计划

AW 管理整体阶段和跨工程依赖。各子工程 PLAN 管理自身实施任务，并链接唯一的本地 bundle；根目录历史任务保持原位。

[DAA-007 r2](data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) — Human Owner于2026-10-30验收r2，并确认阶段B在本次受控DS联调范围内完成；AC01–AC22核验及8590份样本/4295轮完整重开比较通过。历史checkpoint缺失和15:27来源未明事项继续跟踪。配置/历史及原联调profile保留；阶段C、自动启动策略和现场验证另项。

[DAA-006 r3](data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/checklist.md#owner-acceptance-r3) 于2026-10-20获Human Owner最终验收。独立AC01–AC20核验及另行DIRECT界面确认层次分开记录，原blocked历史及原生观察限度保留。验收源码清单已固定，任务临时资源已归档/清理；本次仅验收收尾，未追加测试。后续阶段B已按DAA-007在本次受控DS联调范围验收，DS旧接受保持独立，阶段C另项。

| 工程 | 所属计划 | 当前阶段 |
| --- | --- | --- |
| Semantic Mapping Agent | [SMA PLAN](semantic-mapping-agent/PLAN.zh-CN.md) | 职责清理、CU 接入和本地配置与纯预览均已验收。GET→POST 执行和 Backend、DAA 联调仍是 SMA-001 r2 草案中的后续阶段。 |
| Console UI | [CU PLAN](console-ui/PLAN.zh-CN.md) | CU-001至CU-008均已最终验收，包含分组/二级导航；DAA和SMA各按自身已接受任务接入，新CA接入仍属后续。 |
| Device Simulator | [DS PLAN](device-simulator/PLAN.zh-CN.md) | DS-001 r1及ARCH-AW-005 r5已于2026-10-27获owner_accepted，10月27日DS/手册/整改已接受；10月29日草稿/版本DIRECT增量为DEV自检、人工确认待定；历史QA4及全部失败保留，独立QA仅DS-001例外未执行。验收/资源收尾已记录，未追加功能或整套QA；受控DAA–DS SQLite联调已按DAA-007独立验收，阶段C另项。 |
| Data Acquisition Agent | [DAA PLAN](data-acquisition-agent/PLAN.zh-CN.md) | [DAA-002 r2](data-acquisition-agent/plans/DAA-002-local-acquisition-loop/checklist.md#owner-acceptance-r2); [DAA-003 r1](data-acquisition-agent/plans/DAA-003-sqlite-only-startup/checklist.md#owner-acceptance-r1); [DAA-004 r1](data-acquisition-agent/plans/DAA-004-migration-notice-and-source-import-validation/checklist.md#owner-acceptance-r1); [DAA-007 r2](data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2)已于2026-10-30验收；DAA-001/005/006原接受保持。阶段B仅在本次受控DS联调范围完成，失败历史、证据可用性限制和来源未明事项保留。当前SQLite入口不再迁入YAML，配置/历史及原联调profile保留，阶段C、自动启动策略与真实现场另项。 |

Backend协作依赖：[BE-009](../plans/ARCH-BE-009-backend-facts-integration/spec.md)事实与[BE-010](../plans/ARCH-BE-010-anonymous-business-integration/spec.md) typed业务provider均通过隔离A+B QA。Owner终验、实际schema/时间采用、DAA上传器及SMA执行接线分别保留；当前已选择后端优先、DAA后续的实施顺序。
