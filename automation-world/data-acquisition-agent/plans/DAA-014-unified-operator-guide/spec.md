Task ID: DAA-014
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 交 Development 按获批的 DAA-014 r1 实施与自检
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: DAA 操作说明合并及重复指南退役
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: 本稿第 4、5 节和 Development Lifecycle Workflow
Related Task: DAA-007, DAA-008, DAA-010, DAA-011, DAA-013, ARCH-ACQ-004, ARCH-ACQ-005
Created: 2026-11-14 Asia/Shanghai

# DAA 统一操作手册

## 1. 目标

把阶段 B、C 指南中仍适用的日常操作整理成一套长期 DAA 操作手册。文件沿用 DS 的命名 `USER_GUIDE.md` 和 `USER_GUIDE.zh-CN.md`。DAA README 用简短启动说明引导读者进入完整手册。采集数据模块指南面向所有发送方和读取方，说明后端如何登记、接收和查询数据。 [DS 手册](../../../device-simulator/USER_GUIDE.zh-CN.md) · [采集数据模块指南](../../../../docs/acquisition-data-guide.zh-CN.md)

## 2. 需求与顺序

1. **R01 DAA 操作。** 用一条流程讲清「PLC 或模拟器 → DAA 采集 → 本机样本 → 上报 → 后端回执和 Web 核对」，说明采集和上报可以分别启停。按现有界面写启动和 profile 选择、连接、配置点位与采集组、保存和激活、开始和暂停采集、查看本地样本、按 PLC 粘贴三项接入参数、选择参与上报、确认目标、查看队列与回执、恢复和停止。采用一个合成 PLC/DB 的最短示例，DS 的建模细节链接其手册。已有兼容 profile 可接续，切换前核对实际目录，保留原配置和历史。
2. **R02 两项手测。** 先停采集，仅发送身份和目标已核对且符合投递条件的本机样本，验证匹配 `instanceId` 和 `sampleId` 的 `committed` 回执（`created` 或 `duplicate`），再在 Web 采集历史按 PLC、DB、采样时段核对同份样本。没有可发送样本时说明如何预先生成已绑定的样本，已有「仅本地记录」不自动补传。确认开始前检查所有可能投递的来源及积压，已尝试的样本保留原身份、正文和目标。第二项开启采集和上报，用一份新产生的本地样本核对同样的闭环。写明预期结果、找不到记录时的检查入口和手测结束时的暂停动作。
3. **R03 后端通用说明。** 现有采集数据指南保留原理、Web 来源登记、来源和样本字段、存储、上报/重试、第三方示例、逐点最新值和完整历史读取及到精确合同的链接。`plcId`、`instanceId`、`sourceGeneration` 匹配登记，`sourceType` 用于展示，`dbNumber` 属于样本字段。已采用的来源删除与历史独立读取语义以现行 provider 为准。将 DAA 专属原理和操作集中到手册，原指南保留一段 DAA 入口说明和链接。精确的 POST/GET 字段和限制由 `contracts/` 维护。
4. **R04 旧入口收尾。** 两项手测和由此发现的调试事项收尾前，现有阶段 B/C 手册保持原样供本次操作。完成后，将有效操作指向新手册，从 README 及适用的现行链接撤下两套旧操作流程。默认把旧路径收为简短指引。整理前核对 DAA-007 的受控阶段 B 基线、DAA-008 的 B-RUN-01 冻结材料及 DAA-011 的原文恢复、摘要和行号引用。若旧稿承担证据，优先使用现存的精确版本或保存必要原字节快照，在旧路径和本任务记录给出可追溯入口、原文件名及版本定位。无法保证历史锚点或精确证据可达时，将该文件原样留作历史例外并记录原因，同时从现行操作入口撤下。两项手测即使通过，DAA-010 r5 独立 `qa_failed` 及其 Windows 原生验证待办仍按各自记录处理。 [阶段 B 验收](../DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) · [DAA-010 独立核验](../DAA-010-sample-facts-upload/checklist.md#独立验证-qa2) · [DAA-011 文档核验](../DAA-011-dev-manual-refresh/checklist.md)

## 3. 写入范围与回退

| 时点 | 文件范围 |
| --- | --- |
| 范围获批后 | DAA `USER_GUIDE.md`、`USER_GUIDE.zh-CN.md` 和 `README` 双语，以及 `docs/acquisition-data-guide.zh-CN.md`。必要时同步 `docs/README` 双语的对应索引项。 |
| 两项手测及其调试收尾后 | DAA `JOINT_TEST_GUIDE`、`STAGE_C_GUIDE` 双语的指引或历史处置。确有必要时在本 bundle 的 `evidence/` 仅留本次迁移所需的四份以内原文快照。AW `README` 双语、DS `USER_GUIDE` 双语、DAA `src/app/README` 双语及 DAA `PLAN` 中 DAA-011 旧链接，只调整引用目标。历史专属链接继续指向原任务或精确历史材料。 |
| 任务记录 | 本任务三文件与 DAA 双语 `PLAN`、`plans/README` 中本任务的一行或链接。 |

既往任务的规格、测试记录、历史验收及其中的版本摘要属于原任务。工作树已有更改按实施起点保留。文档回退仅撤销本任务增量。代码、依赖、合同、真实配置、SQLite、样本和 dev 库、PLC、服务启停、临时运行资源处置及发布均在本任务之外。手测由 Human Owner 按当前已确认的 dev 范围操作。

## 4. 验收

| 编号 | 通过标准 |
| --- | --- |
| AC01 | 从两种语言的简明 README 可进入同一套手册。按现行中英文界面、入口和合成夹具静态走读，一次本地采集、停采独立上报、采集与上报并行、查看与暂停都有明确步骤及可见结果。 |
| AC02 | 两份文档分工清楚。DAA 按 PLC 填三项，采集 DB 来自本机配置。通用指南的来源登记、回执、最新值与历史和现行 provider 合同相符。 |
| AC03 | 旧入口仅在约定时点收尾。活跃链接、语言切换及受影响的历史入口可达，原任务状态和精确证据可追溯。例外冻结材料不在日常操作路径。 |
| AC04 | 写入限定于文档。Development 的静态检查覆盖差异、改动中的链接和锚点、双语和所列启动命令语法。独立 Verification 依据实际文档与源码复核，无需构建、重跑采集或发出 HTTP 写入。人工联调结果按实际记录引用，文档通过不升级阶段 C 验收。 |

## 5. 批准与交接

2026-11-14（Asia/Shanghai），Human Owner 明确批准 DAA-014 r1：「批准 DAA-014 r1，按规格整理 DAA 手册与采集数据指南，并清理旧的阶段指南。不要过度设计。」获批草案的 SHA-256 为 `2d3f4b9a320e49db0fb05c1a068c38a20e8b661969ace764ae10f43ab9418d07`。

据 Human Owner 与主会话协调者本轮反馈，停采独立上报和采集与上报并行两项 dev 手测均已完成。Development 按 `project-governance` 实施和自检，按 R04 核对调试事项收尾情况与历史证据后整理旧入口。完成文档与自检后交 fresh-context Verification，独立核验后由 Human Owner 最终验收。[Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)
