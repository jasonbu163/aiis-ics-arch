# Automation World 计划

[English](PLAN.md)

| Task ID | 状态 | 规格 | 最新事实 / 下一 gate |
| --- | --- | --- | --- |
| ARCH-AW-007 | owner_accepted | [r2](../plans/ARCH-AW-007-general-agent-fleet-roadmap/spec.md) | Human Owner 于 2026-10-21 最终验收精确 r2 文档，原独立 AC01–AC14 QA 保留。DAA、SMA 表格、CA 通用编排/内部连接器及未来全类型健康分工明确，首版无登录；完整 r1 历史/QA 保留，证据已归档，两处自有临时目录共 49 文件已清理，未改代码、未追加测试。 |
| ARCH-AW-006 | owner_approved | [r2](../plans/ARCH-AW-006-unified-flow-agent-design/spec.md) | 精确 r2 设计已批准：DAA 大量采集、SMA 表格/工作台、CA 节点编排/版本/上下文/扩展；首版无登录。完整 r1 保留，文档实施统一归 007 r2，软件工作另立范围。 |
| ARCH-AW-001 | owner_accepted | [r1](../plans/ARCH-AW-001-agent-foundation/spec.md) | CA已迁入并冻结，DAA/SMA可构建并独立启动；定向复核通过，Human Owner于2026-10-14接受r1；本轮未追加测试。UI与SQLite后续处理。 |

CA保留冻结兼容基线；后续采集发展由DAA承接。S1 API合同、AW事实上传、业务闭环、共享UI、SQLite配置及映射存储另立spec。完整索引见[任务目录](plans/README.zh-CN.md)。

## 子工程计划

AW 管理整体阶段和跨工程依赖。各子工程 PLAN 管理自身实施任务，并链接唯一的本地 bundle；根目录历史任务保持原位。

[DAA-007 r2](data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/spec.md)保持implementation_in_progress：B0/P1/P2已完成，必要增量自检和最终候选已固定；当前awaiting_owner_native。原生M01–M09、同库对账、developer_handoff及fresh核验尚未发生，阶段B整体未关闭、阶段C排除。

[DAA-006 r3](data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/checklist.md#owner-acceptance-r3) 于2026-10-20获Human Owner最终验收。独立AC01–AC20核验及另行DIRECT界面确认层次分开记录，原blocked历史及原生观察限度保留。验收源码清单已固定，任务临时资源已归档/清理；本次仅验收收尾，未追加测试。DAA 阶段 B 整体仍未关闭，已有受控本地证据和已验收增量继续有效。DS产品/协议基线已随ARCH-AW-005 r5及DS-001 r1于2026-10-27获Human Owner最终接受，原独立技术QA保留。DAA–DS S7读取至SQLite联调及其核验/验收仍在DAA工作流按独立批准推进，DS验收不关闭阶段B或提供本次联调授权；阶段C暂不开展。下表各任务状态保留其原有有限范围。

| 工程 | 所属计划 | 当前阶段 |
| --- | --- | --- |
| Console UI | [CU PLAN](console-ui/PLAN.zh-CN.md) | CU-001–CU-007 已获最终验收，公共侧栏当前仍为平铺；二级导航仍需 CU 独立任务，DAA 接入另项处理。 |
| Device Simulator | [DS PLAN](device-simulator/PLAN.zh-CN.md) | DS-001 r1及ARCH-AW-005 r5已于2026-10-27获owner_accepted，当前DS、手册及另批DIRECT整改已接受；历史QA4及全部失败保留，独立QA仅DS-001例外未执行。验收/资源收尾已记录，未追加功能或整套QA；DAA–DS SQLite联调另批，阶段C暂不开展。 |
| Data Acquisition Agent | [DAA PLAN](data-acquisition-agent/PLAN.zh-CN.md) | [DAA-001 r1](data-acquisition-agent/plans/DAA-001-cu-layout-migration/spec.md) 已于 2026-10-17 owner_accepted；[DAA-002 r2](data-acquisition-agent/plans/DAA-002-local-acquisition-loop/spec.md) 当前为 qa_passed。独立QA4已通过受控阶段B的AC01–AC20，F-001–F-004均已解除，全部失败历史及76份原样本保留，其Human Owner最终验收仍待定。[DAA-003 r1](data-acquisition-agent/plans/DAA-003-sqlite-only-startup/spec.md) 当前为 qa_passed：新的独立QA2在 [checklist](data-acquisition-agent/plans/DAA-003-sqlite-only-startup/checklist.md) 确认F-001/F-002已解除，QA1失败历史完整保留。普通pnpm tauri dev已采用唯一SQLite入口，旧YAML仅首次空实例迁入停用草稿，已有SQLite配置/历史优先保留；必要增量与原受控原生保存重开证据已核准。自有测试进程/15191已释放，证据保留，Human Owner最终验收待定；阶段C/Backend/SMA/DS及真实配置/PLC/生产DB/API/现场动作仍排除。 [DAA-004 r1](data-acquisition-agent/plans/DAA-004-migration-notice-and-source-import-validation/spec.md) 新的独立Verification通过AC01–AC08，有限README/界面调整及受控三点DB/UDT导入闭环已完成；操作差异和观察限制保留，已有配置/历史与SQLite防重回执保持。待Human Owner最终验收；阶段C和真实TIA/PLC联调仍属范围外。 [checklist](data-acquisition-agent/plans/DAA-004-migration-notice-and-source-import-validation/checklist.md)。 [DAA-005 r1](data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md) owner_accepted; Human Owner已于2026-10-19最终验收精确DAA-005 r1，独立QA2已通过AC01–AC13。本次仅验收收尾，原失败和原生证据保留，未追加测试或实现改动。 [checklist](data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/checklist.md). |
