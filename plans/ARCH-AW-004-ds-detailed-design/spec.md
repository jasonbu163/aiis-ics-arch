Task ID: ARCH-AW-004
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner accepted exact ARCH-AW-004 r2 detailed design on 2026-10-18 after the completed Development handoff and AC1–AC29 fresh-context document QA; checklist records owner_accepted, documentation closeout is complete, and G0/software/load/real-environment work remains separately gated
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS 首版多实例 S7 模拟器详细设计及 DAA/CU 复用依据文档
Owner: Automation World
Acceptance Chain Reference: aiis-ics-arch::ARCH-AW-004 r2 exact scope approved 2026-10-18 -> completed Development documentation handoff -> AC1–AC29 fresh-context document QA passed -> Human Owner design acceptance recorded 2026-10-18
Related Task: aiis-ics-arch::ARCH-AW-002; aiis-ics-arch::ARCH-AW-003; aiis-ics-arch::DAA-001; aiis-ics-arch::DAA-002

# DS 多实例 S7 模拟器详细设计规格 r2

## 1. 目标、请求依据与当前 gate

本文件继续同一 `aiis-ics-arch::ARCH-AW-004`，Revision仍为r2，PM spec合法状态保持 **owner_approved**；当前任务的设计终验已由Human Owner完成，[checklist](checklist.md#owner-acceptance-r2)记录 **owner_accepted**。本版目标是在既有DS详细设计上补齐每PLC连接容量、连接生命周期、有界队列与公平、负载验收，简化日志故障与配置恢复，并给出在线手改和运行值保留推荐；这些设计文档现已交付并验收。总体分层及范围不变，不新建Revision/Task ID，不重开已验收ARCH-AW-002/003。

2026-10-18（Asia/Shanghai），Human Owner 授权整理本版规格，原话为：

> 好的，按这些建议先整理 ARCH-AW-004 r2 spec。每个 PLC 暂按 16 条连接且可配置，补齐连接管理、队列公平和负载验收，简化日志及配置恢复；在线手改和运行值保留给出推荐方案，先不改代码。

这句话在草案阶段只授权PM形成可审阅的r2 spec；当时并非整版范围批准，PM只写本spec、主协调同步r2 draft，未启动后续角色。该真实时序保留为历史。

2026-10-18（Asia/Shanghai），Human Owner随后在本主会话`01a14e52-eeb4-7c82-bade-bc0a237fa2ff`直接明确批准精确r2，批准对应草案SHA-256为`e5c92a6fb0ec2b7fbe4086a1dc1d27402c011c07464941363a063a4f364fe4b9`，原话为：

> 可以，批准 ARCH-AW-004 r2 spec，在线手改和运行值保留按推荐方案。接着更新 DS 详细设计并完成文档核验，先不改代码。

上述为精确范围批准时点的真实记录：PM当时记为`owner_approved`，R21的一次性hold维护写与R22的兼容运行值保留推荐被Owner采纳，并转Development文档修订。此后Development已交付r2正文，新的fresh-context Verification已独立通过AC1–AC29；这些角色记录和原QA输入指纹保持，不由本次状态同步替代。

2026-10-18（Asia/Shanghai），Human Owner在本主会话直接完成精确r2设计终验，原话为：

> ARCH-AW-004 r2 详细设计验收通过，更新状态并完成收尾，先不改代码。

**当前设计交付与最终验收均已完成，无待启动的Development/QA或待Owner终验gate**。现[Owner接受记录](checklist.md#owner-acceptance-r2)为`owner_accepted`，接受正文SHA-256为`0eb3c149bf7093bbdce2f0b7a07af71e769fe24cb04a542c7f4dc43e6979eecb`；本次PM只同步spec状态/历史，不改正文/tasks/checklist/索引或重跑设计QA。G0、软件实施、L1–L5负载及真实环境仍属未来独立批准范围。

第4节编号需求及AC表保留草案原文，其中“本draft/待批准/需审阅”等是规格形成阶段的时点措辞；附录A连同其引导语按草案保存时点原字节保护，其中“active=r2 draft”也指当时，当前唯一active状态以开头owner_approved及本节批准记录为准。本次批准已经履行设计范围审阅gate，不改变任何R/AC、数值、allowlist或风险。G0、容量实测、软件实施与真实环境动作的独立批准/证据gate仍未完成；“PM本轮/草案本轮”只约束对应PM阶段，不能用来阻止现在已获批的Development文档修订。

已完成的 **r1 历史**：Human Owner曾批准精确r1，Development已交付当时正文与[handoff](tasks.md#7-精确-developer_handoff)，独立Verification已记录[AC1–AC15文档qa_passed](checklist.md#6-verdict-与交接)，**r1 Human Owner最终验收仍pending**。批准来源、完整原规格及其R/AC/风险在第9节和附录A保留。r1的批准/交付/QA不移给r2；原PM批准时保护r1字节、后续角色接续r2并保留历史的时序均保留，本次不改任何原文/QA证据。

本会话 `01a14e52-eeb4-7c82-bade-bc0a237fa2ff` 继续为唯一 active lifecycle coordinator；来源会话不并行编辑本任务。本 profile 为 `contract_only`，角色归属、串行 handoff 和 diff 审计是合同控制，不宣称平台 ACL 或自动激活。

本任务继续只产出设计文档与文档核验。下文所有容量、队列、时延和资源数字现为 **r2已批准设计目标**，不是已测能力；后续技术原型与软件实施仍须独立获批。不得创建 DS 工程、测试程序、依赖、运行配置、SQLite 文件或正式 schema。

## 2. 已有依据与设计效力

本轮 PM 完整消费根 AGENTS、README/PLAN 双语、docs/plans 双语索引、实际 pm TOML、canonical lifecycle workflow、r1 spec/tasks/checklist 与 367 行 DS 正文；使用 `aiis`、`project-governance`，并消费其跨端合同、资源归因与运行日志参考。此处只定义需求与验收，不代 Development 做技术实现或代 QA 给 verdict。现有 DAA/CU 复用证据沿用 r1 明示读时快照；r2 正文修订前由 Development 刷新触达来源和状态，不把旧快照说成新验收。

| 依据 | 本版须保持的效力与边界 |
| --- | --- |
| [AW 白皮书 DS 章节](../../docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md)、[AW 运行原理 DS 章节](../../docs/AIIS_AW_Runtime_Design.md#ds) | DS 是开发、测试、联调工具；配置区域决定自动模拟或写入保持，不固定 DB 编号/数量。统一写入口在提交前拒绝越权；跨重启持久化、服务核心语言及协议库尚无已实现结论。 |
| [ARCH-AW-002](../ARCH-AW-002-agent-runtime-design/spec.md) | r3 文档已验收，作为既有总体边界；本任务不修订该 bundle、不重跑或继承其 QA。 |
| [DAA 详细设计](../../docs/AIIS_DAA_Detailed_Design.md)、[ARCH-AW-003](../ARCH-AW-003-daa-detailed-design/spec.md) | 已验收设计是可对读依据，不能代替当前 DAA 实现或原生验证。 |
| [DAA 当前说明](../../automation-world/data-acquisition-agent/README.zh-CN.md)、[DAA PLAN](../../automation-world/data-acquisition-agent/PLAN.zh-CN.md)、[DAA-002 Development](../../automation-world/data-acquisition-agent/plans/DAA-002-local-acquisition-loop/tasks.md) | r1正文固定2026-10-18 17:40:28 +08:00读时快照至§6.15，包含76份fixture样本/历史对账；当时仍在研、未完整handoff/独立QA，原快照保留。本轮收尾读取的根PLAN已记录DAA-002 r2为`developer_handoff`，B0–B6交付及最终原生历史/正常重开完成，新的fresh-context QA正在进行、verdict与Owner最终验收待完成。两次状态分别属于其读取时点，均不是DS/S7容量或现场证据；不追逐后续状态，r2 Development需重新固定检查日期与状态。 |
| DAA `tia_source.rs`、`plc_layout.rs` 及点位编辑调用链 | Development 必须核对实际函数、支持范围与调用者，再决定复用等级；当前受限解析、偏移推算不等于完整 TIA 布局引擎，也不存在已确认的通用公共 parser crate。 |
| [CU 公共说明](../../automation-world/console-ui/README.zh-CN.md) 与公共 UI 导出 | 按当前实际公共源码和已验收任务核对；DS 以编译期消费为方向，业务状态与运行生命周期归 DS，不依赖 CU 在线。 |
| 既有 `vibe-l2-front-end/tools/plc/s7-virtual-plc/` | 只读参考现有模拟规则、内存和 S7 server 路径；未经证据不能把库的理论能力写成当前工具已验证的写保护。不得修改该外部工程。 |
| [DS r1 正文](../../docs/AIIS_DS_Detailed_Design.md#configuration)、[r1 Development](tasks.md)、[r1 Verification](checklist.md) | 现有单 owner/单 item 边界、stop 保值、跨进程初始化是修订基础；r1 的 apply journal、纯日志故障封后续写和所有 apply 全初始化须按本版 R19/R20/R22 替换。完整 r1 历史保持，不将其 qa_passed 改写为 r2 结论。 |

工作树有多个并发任务修改。各角色须记录自己的起点与精确差异，保留其他任务内容，不 reset、不整文件回退、不将全树 dirty 归因本任务。DAA/CU 继续变化时，正文记录检查日期、路径和事实等级，后续实施再刷新依赖快照。

## 3. 分阶段精确 allowlist

以下仍为精确10路径，不使用目录通配，表内路径和角色权限原文不变。表中草案/批准后/交接后写入顺序是已经履行的文档阶段合同：Development修订、新fresh-context QA及Owner终验现均完成，不据此启动新一轮写入。本次PM仅同步spec状态/历史，主协调仅机械同步根四索引的ARCH-AW-004行；未来G0/实施/负载另需独立获批任务。

| 精确路径 | 写入者、时点与允许内容 |
| --- | --- |
| `plans/ARCH-AW-004-ds-detailed-design/spec.md` | PM / Human Owner；范围、需求、验收、风险与真实批准历史。PM 本轮唯一仓库写入。 |
| `docs/AIIS_DS_Detailed_Design.md` | 本轮保护 r1 字节；精确 r2 批准后 Development 修订既有正文，保留版本关系及 r1 QA 所指字节的历史依据。 |
| `docs/README.md` | 精确 r2 批准后 Development；仅在必要时同步 DS 唯一行的用途/非实施说明。 |
| `docs/README.zh-CN.md` | 与英文 DS 行语义对应；其他行保持。 |
| `plans/ARCH-AW-004-ds-detailed-design/tasks.md` | 本轮保护 r1；r2 批准后由 Development 接续 r2 计划/自检/新 handoff，保留完整 r1 历史及固定摘要，不建第二文件或空壳。 |
| `plans/ARCH-AW-004-ds-detailed-design/checklist.md` | 本轮保护 r1；精确 r2 developer_handoff 后由新的 fresh-context Verification 接续 r2 核验并保留 r1 verdict/证据，最后只记录真实 Owner 决定。 |
| `PLAN.md` | 主协调；仅新增/机械同步 ARCH-AW-004 唯一行，引用 spec，状态不强于角色事实。 |
| `PLAN.zh-CN.md` | 主协调；同一任务行的中文对应。 |
| `plans/README.md` | 主协调；仅新增/同步 ARCH-AW-004 唯一行，只链接实际存在的角色文档。 |
| `plans/README.zh-CN.md` | 主协调；同一 catalog 行的中文对应。 |

原AW白皮书、AW Runtime、DAA/SMA详细设计和其他任务bundle保持本版起点内容。r2草案阶段未改r1正文/docs索引/后续角色文件，根DS索引曾按真实draft状态同步；当时起点为`/private/tmp/arch-aw-004-r2-spec-0k5rn2r8/`的1659文件摘要与before副本，作为历史保留。本次批准记录及后续文档执行起点为`/private/tmp/arch-aw-004-r2-exec-ns_oqo5j/`；旧临时证据不改写，临时附件不作唯一权威。已批准后再改变allowlist、需求、验收或风险，必须回PM新Revision并重新批准。

排除全部源码、UI、测试、依赖/锁文件、配置、SQLite 文件、正式 schema/DDL、env/YAML、contracts、CODE_INDEX、AGENTS、角色/skills/workflow。只读核对可以查看相关源码及声明的依赖信息，不能安装、构建、启动、连接、发送、迁移或更改它们。

## 4. 编号需求

R1–R12 继续承载 r1 的完整首版设计要求；下列 R13–R23 为 r2 增量及明确替换。冲突时，以本版明示替换为准，不并存两套行为：连接与资源预算按 R13–R18；日志故障按 R19；配置 apply/recovery 按 R20；在线手改按 R21；运行值按 R22。附录 A 保留完整 r1 原文供历史核对，不是另一份 active spec。

### R1. 独立正文与当前/目标区分

正文须可独立阅读，记录检查日期、任务与内容修订，链接本 spec 和已有 AW/DAA 依据。区分当前源码事实、已决定首版目标、推荐实现机制、需原型验证的候选和未来扩展。DS 定位为 Tauri 管理的开发工具，服务端模拟核心与管理界面分层；仅在当前设计中给出接口职责和运行视图，不新建工程。

### R2. 基于 DAA/CU 实际调用链的复用矩阵

逐项核对并列出来源文件/符号或可复查段落、当前状态、支持限制、DS 复用方式和后续 gate。至少覆盖 CU 公共壳/主题/语言/导航、DAA 点位/DB 编辑与导入预览、源解析、UDT 展开、偏移推算、S7 类型编码/解码候选、SQLite 配置/版本/激活模式、日志与快照、采集客户端连接及历史上传。

明确区分“可直接消费的公共出口”“可借鉴但需独立抽取/适配的 DAA 私有实现”“不适用 DS 的采集/历史上传业务”；未获 DAA 最终验收的代码注明状态，不写成已接受共享能力。不得为了 DS 把 DAA 纳入本任务重构，不承诺公共 crate 已存在，不把 DAA S7 客户端等同 DS S7 服务端。复用结论应足够支持后续实施估算和分工，而非只有泛化建议。

### R3. 最小组件与数据/控制流

给出组件图与职责说明，至少包含 DS 页面、Tauri IPC adapter、配置/校验/激活服务、实例管理、规则调度、统一内存访问、协议 server adapter、配置 SQLite、运行快照/日志。明确配置从草稿到已保存到运行生效的路径，以及客户端读写、模拟 tick、UI 手改、初始化/重置的进入路径和反馈；不把业务写入移入 UI 或 CU。

服务核心可在 Rust 与 Python sidecar 等候选间进行有依据的评审；必须列最小选型条件、现有证据不足处及后续原型 gate，不因 Tauri 强制 Rust，不把语言选择悬置为整个详细设计无法确定的理由。

### R4. 多实例、endpoint 与生命周期

每实例有稳定 ID、显示名、S7 endpoint/端口/rack/slot 相关身份、配置 revision、独立内存/规则/统计/日志和运行状态。说明同机不同端口的多实例方案、绑定冲突、失败隔离、客户驱动自定义端口兼容前提，以及配置保存不自动开始监听。

明确至少启动、运行、暂停规则、停止、失败、重置的含义与合法操作：暂停模拟是否继续接受客户端、停止是否关闭连接、重启何时重新初始化。给出进行中请求/规则 tick、停止与重置之间的屏障与拒绝行为；同一实例不得重复监听，单实例故障不自动停止其他实例。应用关闭策略给出首版推荐并说明其后续原生验证，不默认承诺后台服务继续运行。

### R5. DB/UDT 导入、点位编辑与布局

DB 号、名称、数量、点位和区域策略均可编辑，示例不指定业务 DB 编号作为拓扑约束。保存完整源、来源/摘要、声明树、UDT 引用和地址来源；`.db` 为 TIA 源文件，与 SQLite 文件区分。

列首版支持/拒绝/人工确认矩阵，诚实复用 DAA 当前受限范围。导入要预览差异并人工确认，缺失/循环 UDT、不支持语法、重复身份、越界和重叠均明确处理。偏移推算手动触发、提醒完整 DB/UDT、限定标准非优化与已支持布局；不从选中叶点猜测完整偏移，不将人工地址等同自动布局证明。重导入、类型/结构更改取消受影响确认，并给出运行中结构修改的首版安全应用策略。

需核对 DAA 导入器是否解析 `BEGIN` 到 `END_DATA_BLOCK` 的初始赋值；当前若仅消费声明结构，DS 不能默认导入 TIA 运行初值。首版须明确类型默认值与 DS 显式配置初始值的优先级、未导入初值的 UI 提示，以及重导入时保留/取消初值确认的规则。

### R6. 本地 SQLite 配置与运行内存分离

用概念模型列实例、DB/UDT 源/结构、点位/地址确认、区域/覆盖策略、规则参数、配置版本及必要应用状态。只定义职责和约束，不交付正式 DDL/schema 或写数据库。

定义保存/校验/显式应用的反馈、配置冲突/激活失败/重开恢复和旧 revision 的处理。当前模拟内存值与配置初始值分开；首版跨进程重启的运行值策略应给明确推荐与理由，不能声称配置 SQLite 自动保存所有运行值。自动启动、默认监听范围、存储路径与身份使用独立 DS 命名，具体应用包名/开发端口可留后续工程任务确认。

### R7. 可配置读写策略与所有权

至少给出自动模拟、写入保持及初始值/持续固定值的语义表，并定义策略作用层级、继承/覆盖优先级和冲突校验。自动模拟区默认客户端只读；写入保持仅初始化或显式重置应用初始值，此后允许的客户端写入跨 tick 和重连保持。客户端读取权限、客户端写权限、规则写、UI 手改和重置权限分别表述，UI 不能成为隐式绕过入口。

持续规则与客户端可写字段重叠的首版推荐是校验拒绝，要求唯一写入所有者；若选择更复杂语义，须明确配置和可验证时序，不以最后写者偶然覆盖作为合同。至少包含一个不固定 DB 号的“初始值 → 客户端写入 → 后续 tick/重连 → 显式重置”示例。

### R8. 协议写入准入与兼容矩阵

列 S7 server 首版读/写操作、支持的数据形态、边界/权限错误、服务端在提交前拦截的选型要求、连接身份/端口兼容和未来技术验证。协议层写请求可能只有地址/长度/原始字节，应通过已确认布局与触达范围校验，不能假设请求自带业务字段类型。

拒写须在内存变更前完成并返回真实协议失败；只在事后回调报警或写回旧值不满足要求。若候选库不能证明该能力，标成技术阻塞/替代适配评审 gate，不能靠文档承诺通过。多项批次的失败粒度、部分成功及返回行为需在设计中明确推荐并受协议能力核实。

### R9. 统一内存访问、并发和一致性

所有写来源经同一实例内受控入口，定义按实例串行化/受控提交模型和读取可观察边界。整字节/跨字段写覆盖其中 BOOL 位时，要按整个触达范围检查权限；同字节不同位合法写避免读改写丢更新。覆盖地址/长度/bit/载荷校验、同点并发客户端、规则 tick、UI 手改、停止/重置、配置换版及失败不改变内存的行为。

不要无证据承诺整个 PLC、跨 DB、多个协议请求或多个实例的全局原子快照。给出后续实现需核实的原子粒度和协议结果与日志结果的一致关系。

### R10. 页面与可观察反馈

参考 DAA/CU 当前页面组织，给出 DS 首版导航和逐页对象、字段、操作、反馈及权限。至少能完成实例增删/配置、DB/UDT 导入预览/编辑/地址确认、模拟与读写策略设置、显式应用、逐实例启动停止/暂停/重置、在线值观察/手改和有界日志查看。

展示已保存/运行 revision、监听状态、客户端连接、规则启停、当前值/更新时间/来源、拒写原因和实例故障；不把 UI 点击、配置保存、连接成功或协议写成功解释为真实设备动作。日志与刷新有界、不要每 tick 无限堆积；记录必要状态变化及写入审计，不复制 DAA 采样历史/outbox。

### R11. 后续验证场景与分阶段实施交接

提供未来实现验收矩阵，至少覆盖：两个实例隔离；同端口冲突；完整/缺失/循环 UDT；不支持布局与手工地址；重导入确认失效；自动模拟变化与拒写；写入保持跨 tick/重连；初始/固定值区别；重叠字段/BOOL 位越权；多客户端并发；停止/重置/换版竞态；权限拒绝内存不变；保存/应用失败；重开初始化；退出资源释放；DAA 自定义端口连接模拟器。

每场景写预期、责任与需要的证据类型。本轮只审阅这些设计，不执行协议/原生/数据库实验。候选实施阶段先验证 server 写保护及客户端兼容，再落最小实例/配置/内存/UI，最后联调；公共提取应受实际复用收益和 DAA 稳定状态约束，不阻塞既有 DAA 工作。Modbus、命令响应/握手/状态机/延迟响应为未来独立范围。

### R12. 文档质量与边界控制

正文结构、示例、表格/图与 R1–R23 一致；docs 索引双语对应、链接有效。Design 文档不替代公开 contracts、任务 spec 或运行手册，不新增流程 runtime/低代码画布、中央 Backend、账号权限服务、真实 PLC 连接、发布部署或自动迁移。

### R13. 每 PLC 16 连接的含义、配置与预算

一个 PLC 指一个 DS S7 实例，不是一个独立程序、IP 或真实 CPU。每实例已建立并发 S7 会话默认/目标 **16**，可配置；这是未来原型与实施验收目标，不是当前已测上限。同一程序多个端口可承载多实例；8×16 仅是待验证组合，不证明已支持 128 并发负载。

设计正文至少区分 OS 监听 backlog、已 accept TCP socket、TCP/COTP/S7 握手中、已建立 S7 session、closing、已释放。一次连接只计一个 transport 对象；晋升/关闭/异常释放使用明确状态转换，不能重复计数。closing 在句柄/callback真实释放前仍占 TCP/全局资源及此前C或H名额，不能为快速重连提前虚减；页面把实际已建立会话数、closing数和已占预算分列，避免将保留名额误报为仍在服务。

以下为本 draft 建议的配置域和资源预算；范围与默认都需精确批准，库可实现性及真实容量仍待 G0/负载 gate：

| 配置或预算 | 首版建议 | 校验与应用规则 |
| --- | --- | --- |
| 每实例已建立 S7 上限 C | 默认16，整数1–64 | 不接受0、负数、小数、无限或静默截断；16以上标为未验证容量。库若达不到16须判候选不满足目标或回 PM 明确调整，不能偷偷降低。 |
| 每实例握手中上限 H | 默认4，整数1–16 | TCP accept 后至 S7 建立前占 H；握手成功须先取得 C 名额，再释放 H；失败/超时释放一次。 |
| 每实例已 accept TCP 硬预算 | C+H，默认20 | 包含握手、已建立与 closing；OS backlog 单独有界，不当成额外已接入名额。超额 accept 立即关闭而不保留对象。 |
| 全局会话/TCP/握手预算 | 分别128/160/32 | 三项独立计数；启用实例的 C、C+H、H 配置总和须分别不超预算，否则拒绝应用/启动并列出冲突。全局值是资源上限目标，不是吞吐证明。 |
| 实例与执行资源 | 保留最多8实例的建议；全 DS 含 sidecar 建议≤64线程、≤1024句柄，排队内存见R15 | 不创建每报文/每tick无限线程；库自有线程、child process、socket和任务均纳入预算。平台采集口径和可实现上限在未来冻结。 |

全局会话/TCP数是名额预算，不承诺能与线程/句柄/CPU目标同时打满。候选的资源模型必须参与预校验：例如每连接一线程的适配，128会话仅连接线程就超过默认64线程硬预算，因而不得在该profile宣称L3可成立；须换可满足预算的候选，或先回PM批准有明确资源目标的独立扩展profile。库自有线程不能漏计，不能等接入后静默降连接目标。

连接/资源限额的修改仍须先 stop，再显式 apply，不能在线把 C 降至当前会话以下、强退旧连接或改运行内存。显示 saved/selected/loaded 的不同限额。未来若原型要求缩小上述有效域或提高硬预算，记录证据并交 PM 审阅相应实施范围，不把“可配置”变成无界承诺。

### R14. 接入、超时、断连、重连与连接管理

满额拒绝后来者，不抢占现有连接、不自动改端口、不以新连接替换空闲老连接。若当前握手阶段支持真实协议拒绝则给可核查失败；否则立即关闭新 socket，并将 transport 拒绝与 S7 item 失败分别展示，不能伪造尚未建立的 S7 回执。连接总额、握手额或全局资源额任何一项不足都拒绝，原因可观察。

建议握手绝对超时5秒、半报文组装绝对超时2秒、待提交请求期限2秒、网络发送超时2秒；配置域分别1–30秒、0.5–30秒、0.1–30秒、0.1–30秒。半报文期限从本帧首字节起算，不能靠持续滴入一字节无限延长；最大 frame/PDU/声明长度先验有界，未收全不占无限 buffer。正常采样的长连接不因连接年龄、UI隐藏或低频采样被当死连接：首版默认关闭“仅因无业务报文而踢出”的 idle 策略，显式布尔开关与可选60–3600秒期限分开，不能借0表示无限。真正的未完成握手、半报文、发送阻塞、transport错误及经过验证的 liveness 失败才按对应规则关闭。

断连/异常/超时/主动关闭统一清理待处理工作、适配器注册、buffer、socket和预算；释放必须幂等。旧连接未释放时重连按当前真实计数重新竞争，不绕过满额，不继承旧连接ID、队列或未确认写。保持区的值独立于连接，不因清理/重连重置。过慢接收者只使该连接发送队列受限、超时/关闭，不阻塞其他客户端、规则或 stop。

连接列表至少展示 instance、临时 connection/session ID、peer地址/端口、握手/已建立/closing状态、建立时间、最后接收/完成请求时间、in-flight/排队数量与字节、收发/拒绝/超时计数及最近关闭原因。支持显式确认后关闭**单条连接**：先关该连接准入、取消其未提交积压、完成已进入不可取消提交段的 item，再有界关闭/释放；其他连接和实例继续。无可靠客户端业务身份，不把 peer/IP 当认证授权。

### R15. 分层有界队列、字节预算与过载结果

保留每实例唯一内存提交 owner。网络收发、PDU解析、响应编码、SQLite与磁盘日志 I/O 不在 owner 临界区等待；读取在 owner 内复制有界快照后再发送，写入只在有界校验/staging/提交段持有 owner。不得用无限 Channel、无界任务或日志背压掩盖慢客户端。

| 层级 | 首版建议预算 | 超限行为 |
| --- | --- | --- |
| 每连接 | 最多1个执行中PDU、2个待处理PDU；执行/等待/未完成frame/待发送输入加预留响应合计≤64KiB | 协商可承载的 in-flight 不高于实现预算；有完整可回执请求则在提交前返回真实资源/状态失败，否则关闭连接。不能先成功接收再无限堆积。 |
| 每实例协议队列 | 待处理≤64 PDU、≤1024 items；全部协议阶段buffer加预留响应合计≤1MiB，任一先到即满 | 字节数包含执行、等待、未完成frame、待发送，不只数排队；按整个待接入请求预算决定准入。整PDU未准入时不执行其中任何item，逐item边界仍按R8/R9。 |
| 全局协议排队 | 待处理≤256 PDU；全部协议阶段buffer加预留响应合计≤4MiB | 所有实例共享硬计数；不借其他实例队列绕过；拒绝原因区分实例额与全局额。 |
| UI/控制/规则 | UI待处理≤4项/实例；普通控制待处理≤8项/实例；每规则最多1个待处理tick | stop不排在普通积压后；同规则合并为最新模拟时间，累加missed/coalesced，不补跑无限历史。规则描述/索引也纳入实例内存预算。 |

每个请求还受协商 PDU、最大 item/载荷和期限约束；预算对 payload、描述符、预留输出及未完成 frame 的核算须在正文说明，不能只数队列长度漏掉大字节。上表是待批准推荐，不宣称候选库已暴露这些控制点。适配器不能可靠限 in-flight、队列/字节或输出缓冲时，须在 G0/资源原型列阻塞与替代方案，不能仅在 UI 显示一个无效限额。

### R16. 连接间、协议/规则/UI之间的公平

推荐最小方案是：每实例的协议、规则和UI三个有界工作类轮转；协议类内按活跃连接 round-robin，每次最多一个 item，保留同连接同PDU内部 item 顺序；规则类按到期点轮转并合并tick；UI类每次一个命令。空类跳过，单 item 的最大工作量仍由 PDU/地址/类型预算限制。必要时用字节credit补充轮转，但不引入通用任务调度平台。不能让单连接大批次独占整个PDU的所有item，也不在临界区等待网络/磁盘。

stop/关闭准入具有及时控制通道；普通控制按单实例串行且有界，不能被客户端洪峰饿死，也不能因无限控制请求永久挤占正常工作。暂停只停止规则准入，不让出 rule owner。连接间公平不承诺同时到达的写有全局顺序；实际 item 提交顺序、epoch/seq才是结果依据。

正文应给出一条洪峰连接、至少两条低频连接、持续规则、UI请求和 stop 同时出现的时序，以及队列满/不同item大小时的选择。后续负载场景须量化各连接等待/完成/拒绝率与规则missed，不能用总吞吐掩盖个别连接饥饿；在有余量的基准负载下所有连接与规则持续获得服务，在过载下仍保持有界和控制可达。

### R17. stop、取消、期限与不可逆提交边界

明确 queued/执行但未提交/进入不可取消提交段/已提交/已发送结果的分界。stop先原子关闭新准入与accept、取消**尚未提交且未进入不可取消提交段**的积压，再完成已经进入提交段的单item，最后退出callback、关闭transport与listener、释放预算；不等待整条长队列逐个提交。已成功提交的item绝不回滚或重放。多item PDU中前项已提交、后项被取消时，返回真实逐item结果；若连接关闭使完整回执无法送达，标明部分结果未知，不伪造整个PDU全失败/全成功。

期限与提交准入必须在同一受控边界裁决：可确定未提交而超时=拒绝、内存/seq不变；已提交但回执丢失或调用超时=结果未知，不能当拒绝后自动重试。读回只确认当前值/seq，存在后续并发写时不能据此还原原item是否成功，不承诺exactly-once。旧epoch的排队/回调不能进入新image。stop超时保持stopping/failed及准入关闭，不假报资源已释放；apply/reset只在完整stopped后进行。对已承诺进入提交段的工作不能强行取消、释放仍被使用的image，库不支持有界退出时仍走候选隔离/替代gate。

### R18. 后续容量和负载验收合同

本轮只定义未来证据，不运行负载。以下是建议基准 profile 和验收目标，需 Human Owner 审阅；未来独立实施/压测任务须固定 OS/build、CPU核心/架构、RAM、客户端/库/编译选项/版本、native或sidecar进程边界、协商PDU、loopback/网络拓扑及背景负载，之后才能报告容量。建议参考主机至少4物理核心、16GiB RAM、SSD；不同OS/硬件结果分别报告，不能外推。

| 场景 | 必须固定的负载与时长 | 后续预期与证据 |
| --- | --- | --- |
| L1 单实例16连接基准 | 5分钟预热后持续60分钟；每连接10轮/秒，每轮2个请求，每请求1 item、读200B；独立hold写区每10轮将第2读请求替换为1次8B写；每实例128条规则（96动态、32fixed），100ms tick | 常态320请求/秒，其中304读、16写，应用payload约60928B/秒，不含协议开销；记录逐连接时延/错误/字节及规则指标。布局可用任意DB号/数量构造，fixture不是产品拓扑。 |
| L2 多实例必测组合 | 2×16连接，各实例完整L1，持续60分钟；一实例过载/stop/故障时另一实例仍测量 | 实例内存、连接、队列和故障隔离；独立报告每实例与全局资源，不以总量平均掩盖差异。 |
| L3 独立扩展profile探索 | 8×16连接，各实例L1，预热后30分钟；仅在扩展profile另经PM范围审阅/Owner批准后开展 | 不是默认≤64线程profile的同时满足承诺：每连接一线程候选在128连接时必超该预算，不得静默突破。先明确替代候选或扩展资源预算再探索；未批准/未通过前不得宣称支持128负载，也不把L3当L1/L2已验证结论。 |
| L4 满额/握手/重连 | C=16时第17条；H=4时第5条未完成握手；各连接至少100次断开重连，含半关闭与异常，轮转并加100–1000ms抖动 | 原会话不抢占；真实计数/拒绝/释放一致；最终socket/线程/句柄回到可解释基线，无单调增长，保持值不因重连变化。 |
| L5 公平/过载/慢连接 | 在L1基础上单连接以4倍请求频率洪峰15分钟，再全体2倍频率15分钟；另加入握手不完成、半报文滴流、只发不读各5分钟 | 队列/字节始终有界；一连接洪峰时低频连接持续完成请求，正常低频连接p99建议≤250ms；全体过载可有明确拒绝，但stop仍可达、合法提交保持正确，恢复基准后队列回落。 |

L1/L2建议通过目标：正常已准入请求端到端p95≤50ms、p99≤100ms，排队p99≤50ms，规则missed比例≤1%，非故意错误/越权写/BOOL丢更新为0；基准stop≤2秒、过载stop≤5秒。全 DS/sidecar 合计平均CPU≤一个逻辑核的100%，预热后RSS≤512MiB，60分钟净增长≤32MiB；线程/句柄与R13预算对账，反复重连后不持续增长。这些是待实测目标，不是工控实时保证；不满足须真实失败/说明，不静默降低负载或更换分母。

报告必须提供 p50/p95/p99/max、吞吐/读写字节、逐连接完成/拒绝/超时、TCP/握手/会话/closing峰值、CPU口径、所有进程RSS、线程/句柄、队列深度/字节/等待、规则missed/coalesced、stop各阶段耗时及采样原始证据；明确预热/持续阶段和分位数统计对象。越权失败前后内存hash、item回执和公平/资源计数须能关联。仅能连上16条或一次读取成功，不等于吞吐/稳定容量通过。大PDU、多item、BOOL/STRING和布局上限另列兼容/边界场景，不由200B基准替代。

### R19. 简化日志故障与 fixed 无变化行为

推荐正常保留有界 JSON Lines stdout/文件日志、轮转及内存事件；**纯日志介质、轮转或可选持久sink失败不封闭全部模拟写**。告警、显示observability_degraded和丢弃计数，降级为有界内存环形事件；环满可丢最旧记录并累计丢弃数量/首末时间，恢复后记录缺口，不回放已提交写以“补审计”。日志队列/磁盘不阻塞owner或网络。正常运行不承诺无限逐item持久审计或断电后的完整写入证据。

区分三类事实：日志故障只影响可观察性；配置SQLite事务确定失败/回滚必须如实返回保存/选择失败并保留原持久版本，commit结果未知则按R20查询而不假称回滚；内存owner、准入或提交结果本身不能维持正确性属于runtime fault，仍须关闭该实例准入。共享磁盘错误不可直接推断三者同时失败。任何成功提交都不因之后日志失败改报失败、回滚、重复执行；UI维护确认也应提示当前日志降级而不伪造持久记录成功。保留最小result ID/epoch/seq与操作真实回执，事件丢弃不改变它们。

持续fixed仍为rule持续owner，但目标值未变化时跳过重复mutation，不必每tick增加commit_seq或重写值更新时间；仍检查有效epoch/状态/所有权，规则状态与健康计数独立维护。初始值只在初始化时生效，fixed在规则生效时维护目标，二者语义不因跳过无变化提交而合并。

### R20. 最小配置恢复与 apply 幂等

推荐取消 r1 多阶段持久apply journal；保持单DS配置SQLite、不可变revision、CAS保存、逐实例停机显式apply和配置/运行内存分离。`saved`=持久保存的候选revision；`selected`=单SQLite事务选中的实例revision；`loaded`=本进程确实装入的image事实。selected不是loaded，saved不启动/监听，不宣称SQLite与RAM跨介质原子。

最小路径为：验证stopped/expected selection与epoch→从不可变revision预校验并构建候选image和保留清单→取得控制序列并复核→单SQLite事务CAS更新selected引用→安装预构建image、换epoch并标loaded→回成功。构建/SQLite在owner临界区之外；加载/安装未完成时start不可用。只持久保存所需配置与selection，不引入持久命令系统、分阶段journal或后台恢复daemon。

| 失败/重试时点 | 必须说明的真实结果 |
| --- | --- |
| 预校验/构建失败，或选中事务确定回滚 | selected不变、旧image和值保留且stopped；不能提示已应用。用户草稿/候选保留供修改。 |
| SQLite commit结果未知 | 查询当前selected确认；查询也失败时显示selection结果未知并保持stopped/禁start，不把内存尚未安装当作SQLite已回滚。 |
| selected已提交，内存安装前失败 | 新selected是真实持久事实；旧loaded/image可保留作只读诊断但不可服务，不伪称原版本仍可直接start。重试加载selected，或用户显式选择旧revision。 |
| 安装成功但回执丢失 | selected/loaded及当前值已生效且stopped，调用方结果未知；刷新状态。重复apply同一selected且loaded revision/内容摘要一致时幂等返回already_loaded，不再换epoch、初始化或丢失保留值。 |
| selected相同但未loaded | 走“加载当前selected”的恢复路径，不重复改selection；本进程尚有旧image时按R22兼容/确认方案重建，成功安装后后续重试为幂等。无法证明兼容时要求确认初始化，不盲拷旧bytes。 |
| 任一阶段崩溃/进程重开 | 只读已提交selected的完整不可变revision重新校验/初始化，全部stopped；事务前崩溃取旧selected，事务后取新selected。selected损坏/缺失/不兼容则停机报错，不自动用最新saved或猜测旧版。 |

相同selected/loaded版本的apply重试绝不是reset；明确“重新初始化”必须走独立reset并确认。不同revision即便内容相似，也先做R22兼容检查和影响清单，再按新revision应用；所有跨进程重开仍初始化，不靠记录operation ID恢复运行值。返回旧revision是新的显式选择/加载，不能自动找回历史运行bytes。显示selected/loaded不一致、加载失败与重试入口；不让一个错误“apply失败”掩盖持久选择已经改变。

### R21. 在线手改的比较与首版推荐

| 方案 | 收益与复杂度 | 本版建议 |
| --- | --- | --- |
| 维持严格持续owner，UI只写ui-owner字段 | 最少规则；client-owner hold不能临时手调，须改配置/停机 | 保留此普通UI写路径，作为默认保护基础。 |
| 显式受控一次性UI维护写 | 便于测试client-owner hold；需独立开关、CAS、确认和结果反馈；无持续接管状态 | **首版推荐**，仅对明确允许的write_hold点开放，默认关闭维护开关。 |
| 临时接管/租约后恢复owner | 可在接管期间排除客户端或规则，但需恢复/取消/超时/stop/reset及崩溃语义 | 首版不采用，不增加租约服务或临时持续owner；未来有真实场景再独立批准。 |

一次性维护写不是第二个持续写owner：client/none的hold点只有显式`allow_ui_maintenance`有效且当前running/rules_paused时可发起，owner不改变，client_write原权限不改变；默认关闭，按实例→DB→region→point明确继承并展示effective来源。rule字段及未允许的字段即使暂停也拒绝；要改fixed/规则目标须改配置、停机apply，不能借维护绕过。ui-owner字段继续用普通typed UI写，不叠加两条持续路径。

UI先展示类型化新旧值、当前revision/epoch/point last_seq、维护开关与影响，确认“本次只改当前值、不持久保存初值、不锁住客户端，下一次合法客户端写可覆盖”；提交带expected loaded revision、epoch和point last_seq。统一内存入口做同样的范围/coverage/类型/状态及维护权限检查，CAS不符返回conflict并刷新重确认，不静默覆盖。维护成功产生新seq、来源ui_maintenance/operation ID与有界审计结果；随后客户端按既有权限继续写，次序由同owner串行提交决定。

UI排队、超时、stop与回执未知遵R15/R17；失败不改值，已提交后回执丢失须读回，不自动重试。维护写不改配置初值、不暗含暂停/恢复规则、不升级真实设备权限。日志降级按R19如实显示，不能把本地可选审计说成已持久完整。

### R22. 运行值保留的逐场景推荐

首版仍停机显式apply，不批准热更新，也不持久保存运行值。推荐默认策略为 **preserve_compatible_hold**：对下表允许的明确兼容范围保留；应用前显示逐点“保留/初始化/删除”的清单和原因，用户确认后才选中/加载。也允许用户显式选“全部初始化”，但重复apply同一loaded revision不触发该选项，须另用reset。

兼容条件至少为稳定点ID、DB身份/号/长度、地址/bit/宽度、类型/编码、已确认布局摘要及相关有效mode/持续owner/读写与维护权限/初值一致；来源仅注释等变化不自动使兼容成立，仍按摘要与确认核对。保留在预构建新image时按已校验typed值编码，不把旧DB bytes恢复到新布局；不兼容、缺证明或校验失败不能默默称“已保留”。

| 场景 | 默认推荐与用户可见影响 |
| --- | --- |
| 同进程stop→start，未apply/reset | 保留全部当前值与规则模拟时间；不重新初始化，断连本身不影响hold。 |
| 同布局，仅名称/显示/连接限额等非值语义变化 | 停机apply仍换epoch；兼容点全部值和规则时间可保留，明确列出检查结果；连接不会恢复，start仍独立。 |
| 规则参数/seed/周期变化 | 兼容hold保留；全部规则点/规则时钟统一初始化到新revision的t=0，避免多时间基准；影响清单明确指出未改参数的规则也重置。 |
| 初值变化 | 受影响点按新初值/类型默认初始化；其他兼容hold保留；规则按新revision的t=0初始化。不能“保留”掩盖新初值未生效。 |
| mode、owner、读写/维护权限变化 | 受影响点初始化，取消不再合法的待处理/旧epoch写；其他兼容hold保留，规则统一t=0。暂停不让权仍成立。 |
| DB结构/号/长度、地址或类型变化，增删点 | 受影响DB整体初始化，不按旧offset拼回；未受影响DB只保留满足全部兼容条件的hold；新增点初始化、删除点丢弃，规则统一t=0。 |
| 显式reset | 当前loaded revision所有点初始化、规则t=0、新epoch；确认丢弃全部运行值，保持stopped。 |
| 跨进程正常/非正常重开 | 只按selected配置全部初始化、规则t=0、stopped；不恢复运行值、连接、临时接管或运行意图。 |
| 显式回到旧revision | 默认全部初始化并确认，不能从旧日志/旧bytes复活历史值；仍需单独start。 |

失败按R20阶段区分：selection确定未变时保留旧image/值并stopped；selected已变但未装入时旧image仅作诊断、不得服务，恢复前需确认保留计划或初始化；安装成功后ack丢失不回滚，不让重复apply再初始化。若用户选保留但某点兼容/值编码失败，应用前失败并给影响清单，允许用户另选明确初始化后重试，禁止静默降级。所有保留只覆盖本进程仍持有的值，不引入磁盘快照/持久运行值能力。

### R23. 正文一致性、历史保护与后续交接

精确r2获批后，Development须把R13–R22具体融入组件流、概念配置、页面、状态/错误、策略、时序、G0/验证矩阵和分阶段建议，而不是附一段与旧正文矛盾的补丁；删除active正文中“日志失败封全部后续写”“必须多阶段journal”“任何apply都全初始化”“只有ui-owner可手改且无维护例外”的冲突描述，并保留r1历史引用。R1–R12的导入支持子集/初值警示、BOOL/STRING/raw覆盖、提交前拒写、多item边界、独立DS命名、DAA/CU复用和排除项仍完整。

G0继续先证明写前拒写、全部client/rule/UI/维护/初始化写路径收口、真实PDU/item回执/部分成功、BOOL/STRING字节与真实DAA自定义端口兼容；再确定语言、库/版本、进程边界和资源可控点。语言未选不悬置其他设计，也不因本r2批准自动允许原型运行。后续负载和故障注入均另在获批实施任务中执行。

PM本轮只交r2 spec及文档自检；不修r1正文/tasks/checklist、不生成r2空角色文件。批准后Development在同一tasks接续r2计划/自检/新handoff且保留完整r1事实，新fresh-context Verification在其后接续checklist验证整版r2而非继承r1 verdict；最终Owner验收仍单独记录。

## 5. 验收标准

下表是**已获批r2正文修订后的独立文档验收口径**，29条AC原文不变；不是本次PM核对的QA verdict，也不是软件/容量/现场行为已通过。AC1–AC15继续覆盖既有完整设计，AC16–AC29覆盖增量及形成时的治理历史；全部须在精确r2 handoff后重新独立核验。

| AC | 对应需求 | 文档可核验标准 |
| --- | --- | --- |
| AC1 | R1/R12 | 独立 DS 正文、日期/revision/效力、已有依据及首版/扩展边界完整；不重开已验收任务。 |
| AC2 | R2 | 复用矩阵有实际路径/符号及状态/限制/方式/gate，覆盖规定主题；DAA-002读时验收状态、parser非公共能力、client/server不等价均准确，不把历史快照写成当下结论。 |
| AC3 | R3 | 组件职责、控制/配置/读写/反馈流可追踪，CU 与 UI 不拥有设备内存或业务执行。 |
| AC4 | R4 | 至少两个实例的 endpoint/内存/日志/规则/故障隔离可从设计推演；端口冲突和自定义端口前提明确。 |
| AC5 | R4/R6 | 生命周期、暂停/停止/重置、关闭/重开、在途屏障与配置应用语义没有矛盾。 |
| AC6 | R5 | 导入/编辑/确认流程、支持矩阵与 DAA 实际范围对应；完整结构、受限推算、重导入失效和运行中修改均明确；不假定解析器导入运行初值，默认值/显式初值及提示规则齐全。 |
| AC7 | R6 | SQLite 概念配置与运行内存分离，revision/激活/恢复有明确行为，跨重启值策略有首版推荐。 |
| AC8 | R7/R21 | 策略表、层级优先级、来源权限、唯一持续写owner及显式一次性维护例外、完整保持/重置示例一致；不固定DB编号/两个DB拓扑。 |
| AC9 | R8 | server 写保护必须提交前拦截，原始地址/字节校验与协议失败/多项返回边界明确；未验证库能力不写已支持。 |
| AC10 | R9 | 字节/BOOL 重叠、并发写、读改写与停止/换版竞态可推演，失败内存不变；原子边界不夸大。 |
| AC11 | R10 | 逐页流程覆盖完整首版操作与有界反馈，依 CU 公共消费，配置保存/运行事实分开。 |
| AC12 | R11 | 验证矩阵覆盖全部规定场景，标明未来证据和分阶段依赖，未用本轮静态阅读代替运行证明。 |
| AC13 | R3/R11 | 服务核心候选有实际证据、选型条件和原型 gate；后续实施与公共抽取分工明确，Modbus/响应模拟延期。 |
| AC14 | R12/§3 | 新文档/索引语义和链接/围栏/表格可检查，实际差异严格在 allowlist；他任务 dirty 保留，未改代码/配置/旧任务。 |
| AC15 | §1/§8 | 精确批准、Development 自检/交接、fresh-context QA 和 Human Owner 最终验收据真实时序分开；不预造 QA 或终态。 |
| AC16 | R13 | 能逐状态算出TCP/握手/S7/closing计数、C=16默认与1–64配置域、C+H和全局预算；有效范围/停机应用/超额拒绝/非已测声明完整，16不被写成程序数/IP数或已验128容量。 |
| AC17 | R14 | 满额不抢占，握手/半报文/待提交/发送期限有建议值、有效域和关闭阶段；正常低频长连接不因idle误踢；异常/重连/释放不重复计数、不重置hold。 |
| AC18 | R14 | 连接列表字段、真实计数、关闭原因与单连接关闭时序可定位；关准入→取消未提交→完成提交段→释放不影响其他连接/实例，无业务身份/权限夸大。 |
| AC19 | R15 | 每连接/实例/全局PDU、item、字节、输出预留和UI/控制/规则均有有限预算；超限在提交前真实失败或关闭，网络/磁盘不在owner临界区等待。 |
| AC20 | R16 | 明确工作类轮转、连接间item轮转/保序、规则合并与普通控制界限，给洪峰/低频/规则/UI/stop时序；公平验收能观察逐连接等待/完成/拒绝而非只看总量。 |
| AC21 | R17 | stop先封准入并取消未提交积压，已进入提交段item完成一次；多item前后结果、超时拒绝与已提交回执未知分开，旧epoch/超时退出不假报stopped或回滚。 |
| AC22 | R18 | L1–L5具连接数、轮询频率、每轮请求/item/字节、读写混合、规则数、预热/持续时长与重连次数；单实例16、2×16和8×16的效力不同，负载数字与算术一致。 |
| AC23 | R13/R18 | 后续证据包含端到端与排队p95/p99、CPU/RSS/线程/句柄、队列/字节、missed/coalesced和stop耗时；建议阈值、统计口径、固定环境和过载/公平/慢连接结果明确，未执行不写容量通过。 |
| AC24 | R19 | 纯日志故障告警+有界内存/丢弃降级，不全封模拟写；配置失败与内存正确性故障单独处理，已提交不因日志改报失败/重放；fixed无变化不反复commit/seq/改时间，仍有持续owner。 |
| AC25 | R20 | 单SQLite选择事务、saved/selected/loaded、无多阶段journal的路径及六行故障表可推演；重复同selected/loaded apply幂等不初始化，回执未知不被写成事务回滚，reset独立，重开按selected初始化停机。 |
| AC26 | R21 | 至少三方案比较且选一次性hold维护；默认关、effective开关、rule禁写、确认、epoch/revision/point seq CAS、统一入口、后续客户端可覆盖及审计降级全部明确，无持续双owner/租约服务。 |
| AC27 | R22 | 逐场景保留矩阵覆盖stop-start、纯参数/连接限额、规则/初值/权限、结构/地址/类型、reset、跨进程重开和回旧版；兼容证明/影响清单/确认/失败阶段清晰，不拷旧bytes至新布局、不暗授热更新/持久值。 |
| AC28 | R2/R12/R23 | r2正文各图/概念配置/页面/策略/时序/G0/验证矩阵一致替换旧冲突；全部原写路径和BOOL/STRING/真实DAA端口gate保留，来源状态重固，语言未定不代替设计。 |
| AC29 | R23/§3/§9 | 本轮PM差异只在spec，r1正文/tasks/checklist/其他正文保护；r1批准/交付/QA/未终验与r2 draft/待批准清晰，10路径和分阶段归属准确，无第二spec/空后续角色文件；链接/锚点/表格/围栏/R-AC覆盖和实际自检可复查。 |

## 6. 风险、回退与未决技术 gate

| 风险 | 本版设计要求与后续处置 |
| --- | --- |
| DAA 正在开发，复用点快速变化 | 固定检查日期与文件/符号；如实标记其状态和限制，后续实施前刷新；不为复用修改 DAA。 |
| server 库只通知写后事件，无法提交前拒绝 | 作为首个技术原型 gate；不以周期覆盖冒充写保护，评估其他适配或明确不满足后停止该候选。 |
| TIA 类型/布局覆盖不足 | 先定义受支持子集和人工确认，缺定义拒绝推算；不承诺优化 DB 或所有 S7 CPU。 |
| 共享内存并发和 BOOL 位越权 | 统一入口、整个触达范围准入、明确原子粒度与在途屏障；后续测试需要真实协议和内存对照。 |
| DS 详细设计被当成生产控制证明 | 正文、示例、交接及 QA 都保留开发工具定位和证据层次；真实设备另行授权验证。 |
| 文档任务扩大为框架抽取/工程启动 | 精确文件 allowlist；只记录候选目录/接口/阶段，抽取、建工程、安装/运行留独立任务。 |
| 16连接配置被当成已验证吞吐/128会话容量 | 将连接准入、资源预算与L1–L5负载分开；固定版本与环境，失败如实记录。候选达不到16或需收窄有效域时回PM，不静默降级。 |
| 有界队列仍造成大item占用、慢socket或规则饥饿 | owner只处理有界内存工作；网络/日志I/O外移；按item轮转、合并tick和逐连接证据。不能控制库内队列/线程则候选资源gate不满足。 |
| 一次性维护被误当临时owner或覆盖并发客户端 | 默认关闭、明确effective权限、用户确认、统一入口CAS；客户端随后仍可写。需长时间独占时保留严格owner/改配置方案，不暗增租约。 |
| 日志降级造成证据缺口 | 告警、内存环/丢弃计数与恢复缺口，保留真实结果；不承诺持久审计完整性。若将来要求强持久审计，必须另批准更强合同。 |
| selected提交成功但内存未装入 | 禁start、明示selected/loaded差异，重建当前selected；不是自动回滚。重开只依不可变selected，不引入journal弥补虚假跨介质原子。 |
| 兼容保留判断错误或失败后暗中丢值 | 明确摘要/身份/类型/策略比较、逐点清单与确认；不兼容时拒绝保留并允许显式初始化。selection后故障旧image只读诊断，不能继续按旧配置服务。 |

本轮可逆写入仅为spec；若草案需撤销，只做本轮spec delta的受控修订，保留r1历史、其他dirty和角色文档，不自动reset。未来获批正文修订的回退也只处理本任务delta，不回退他任务。服务语言/库、精确CPU/操作/类型支持、应用包标识/开发端口等未决项记录责任、证据与下一gate；R13–R18容量域、调度/退出可控性由未来Runtime/协议原型与独立QA确认。持久运行值、临时接管和强持久审计属于后续范围，不以未决列表悬置本版必须给出的推荐。

## 7. 排除项

不实现 DS、共享 parser/runtime/crate、S7 server、SQLite 或 UI，不修改 DAA/CU/SMA/CA/Backend，不补测这些任务；不安装依赖、构建/启动应用、监听端口、运行协议/数据库/原生实验、操作真实 PLC 或第三方接口；不写 schema/迁移/配置、不发布/部署/提交/推送、不向其他用户会话或外部人员发送任务。

首版不含 Modbus、响应/握手/状态机模拟、完整 PLC 执行引擎、SMA/CA 可视化流程 runtime、中央配置服务、生产托管/高可用或现场安全证明。r2亦不增加热应用、持久运行值、临时owner租约、持久命令系统、通用队列平台或强持久审计；可以说明扩展边界，不预建空壳。

## 8. 角色交接与所需 skill

以下为已完成的r2文档交付链及所遵循的角色/skill边界；当前终态事实以第1/9/12节及checklist的Owner接受记录为准，不重新启动Development或QA。

1. **PM → Human Owner（精确r2范围批准已完成）**：Human Owner已于2026-10-18明确批准当前r2草案指纹，采纳在线手改与运行值保留推荐；批准原话/草案SHA见第1/9节。10路径分阶段allowlist、R1–R23、AC1–AC29、数值及风险不变，不把批准写成最终验收。
2. **Human Owner → Development（已完成的文档阶段）**：已按获批r2修订正文并交接本角色tasks，完整消费当时bundle/差异/规则/来源并保留r1历史。使用`aiis`、`project-governance`；Tauri/退出设计用`desktop-tauri`，owner/队列/连接/本地存储/日志设计用`rust-runtime`和aiis资源/日志参考，TIA/布局用`plc-point-mapping`，均只做设计需要的只读核对。后续UI代码/文案实施仍另用`frontend-ui`/`i18n-workflow`且另获范围批准。
3. **r2 Development → 新fresh-context Verification（已完成）**：精确r2 handoff后已实际启动新的命名Verification，独立核验整版AC1–AC29并记录qa_passed；未沿用r1 verdict替代。原handoff/QA输入指纹、来源、检查和限制在tasks/checklist保留，本次不重核设计或重跑QA。
4. **Verification → Human Owner（设计终验已完成）**：Human Owner于2026-10-18直接接受精确r2详细设计，checklist当前owner_accepted。当前无未完成文档gate；G0、容量实测、软件实施、发布部署、SQLite运行写入及真实设备仍须后续独立批准。

本 profile 为 `contract_only`。角色文档归属、串行 handoff、当前工作树和 diff 审计是合同控制，不宣称平台 ACL、强制路由或 Agent Team 自动激活。

## 9. 修订与批准记录

前三行逐字保留r1时点记载，其中“第1节”指附录A原规格第1节；其后追加真实后续时序，不能将历史“尚未发生”读成当前状态。

既有r2 draft/owner_approved行及第10/11节均保留各自记录时点；其中“尚无交接/QA/终验”“待最终验收”是当时历史，当前r2终验事实见新增接受行及下方active字段。

| 日期 | Revision | 真实记录 |
| --- | --- | --- |
| 2026-10-18 | r1 draft | PM 根据用户本次明确文档请求分配独立 ARCH-AW-004，形成多实例 S7、DB/UDT、点位编辑和可配置读写策略的具体范围；未取得精确 Revision 批准，未产生 Development/QA/最终验收事实。 |
| 2026-10-18 | r1 draft 事实刷新 | 只读核对 DAA PLAN 与 DAA-002 tasks §6.9，更新其恢复实施及部分原生证据快照；本任务范围、allowlist、R/AC、Revision 与批准 gate 均不改变。 |
| 2026-10-18 | r1 owner_approved | Human Owner 在来源会话明确批准继续 `ARCH-AW-004 r1` 的详细设计及 DAA 复用核对，先不改代码；实际 userMessage 与原话已核实并记于第 1 节。PM 记录批准及向 Development 的交接，r1 范围、10 路径、R1–R12、AC1–AC15、风险和既有 draft 历史保持；本会话接手唯一协调，独立 QA 与最终验收仍待后续真实发生。 |
| 2026-10-18 | r1 developer_handoff | Development真实交付设计正文、docs双语入口及自检；来源/摘要/精确handoff见[tasks §7](tasks.md#7-精确-developer_handoff)。本行是PM引用其事实，不代写Development证据。 |
| 2026-10-18 | r1 qa_passed，终验pending | 新fresh-context Verification真实通过AC1–AC15，见[checklist §6](checklist.md#6-verdict-与交接)；G0/软件实施未验证，Human Owner尚未最终验收。 |
| 2026-10-18 | r2 draft | Human Owner要求先整理r2 spec，按每PLC16连接且可配置，补连接/公平/负载并简化日志/恢复、给维护和保留建议。PM仅修本spec形成R13–R23与AC16–AC29；精确整版范围批准、r2 Development/QA/终验均未发生。 |
| 2026-10-18 | r2 owner_approved | Human Owner在本主会话直接批准精确ARCH-AW-004 r2，批准草案SHA为`e5c92a6fb0ec2b7fbe4086a1dc1d27402c011c07464941363a063a4f364fe4b9`，明确采纳R21/R22推荐并要求更新详细设计、完成文档核验、先不改代码。PM仅记录批准/转Development，未改R1–R23、29条AC、数值、allowlist、风险或r1完整引文；尚无r2正文交接/独立QA/Owner终验事实。 |
| 2026-10-18 | r2设计owner_accepted，spec仍owner_approved | Development已交付正文SHA`0eb3c149bf7093bbdce2f0b7a07af71e769fe24cb04a542c7f4dc43e6979eecb`，新的fresh-context QA已通过AC1–AC29，Human Owner随后直接表示『ARCH-AW-004 r2 详细设计验收通过，更新状态并完成收尾，先不改代码。』既有Verification已记checklist owner_accepted，本次PM仅同步状态/历史，不修改范围、原QA或实施软件。 |

**r1批准来源（保留历史）**：来源会话`01a13d84-c40c-7bc3-9cca-e7cb57438d62`，主协调此前`read_thread`核实实际userMessage：turn `01a14e52-7297-7bb0-9eaf-eee22a10dfa7`、message `01a14e52-72c2-7331-a357-f4e6840e8ff8`，2026-10-18 Asia/Shanghai。原话为：

> 好的，帮我新建一个「DS 设备模拟器」会话，继续 ARCH-AW-004 r1。这个设计任务范围批准，先把详细设计文档整理出来，结合 DAA 确认可复用部分，先不改代码。

Human Owner scope approval of exact ARCH-AW-004 r1: approved（2026-10-18）；历史保留，不覆盖r2。

Human Owner final acceptance of ARCH-AW-004 r1: pending。

Human Owner scope approval of exact ARCH-AW-004 r2: approved（2026-10-18，Asia/Shanghai）；直接批准原话见第1节，在线手改与运行值保留按R21/R22推荐方案。

Human Owner final acceptance of ARCH-AW-004 r2: owner_accepted（2026-10-18，Asia/Shanghai）；仅详细设计终验，权威接受记录见[checklist](checklist.md#owner-acceptance-r2)，PM spec Status合法保持owner_approved。

## 10. r2草案阶段PM文档自检（历史保留）

以下原自检记录保留r2草案阶段的2026-10-18时点，因此其中“active=r2 draft/当前spec=r2 draft/只写spec/随后同步DS行”等是当时事实，不是本次批准后的active gate。它不是独立QA、r2验收或软件验证。工作目录为仓根；辅助Python只用stdlib读Markdown/摘要/差异，文件写本任务私有tmp，不使用或更改项目依赖；旧脚本、结果和临时目录本次不改写。

| 实际命令/检查 | 真实结果与边界 |
| --- | --- |
| `python3 /private/tmp/arch-aw-004-r2-spec-0k5rn2r8/pm/check-spec.py` | exit0；active元数据为r2 draft，23个R/29个AC及全部R覆盖、26个本地链接/其中7个anchor链接、表格列数/围栏/尾空白、10路径/原bundle三文件结构通过；L1请求/字节与全局名额算术一致。这是结构/引用和PM自检，不是设计独立verdict。 |
| 同脚本的原文/保护检查 | exit0；引文可恢复完整205行r1 spec，SHA为`5cb85aba5bbbc4d608e56e218ad2e13873af4992848823bd9500dce42714aa26`；r1正文/tasks/checklist、docs双语索引及既有AW/DAA/SMA四正文共9路径对本轮基线原字节相同。 |
| 同脚本对`baseline-manifest.json`与当前`git ls-files --cached --others --exclude-standard -z`摘要审计 | exit0；PM写入仅spec。首次摘要及收尾核对时，根四索引已有DAA-002并发行变化，另7条DAA路径变化均为foreign；共享索引变化不归本次DS协调者或PM。DS主协调将在PM正式handoff后才只同步DS行，既有DAA变化保留。明细在`pm/scope-delta.json`，保护校验不把全树dirty认领为本任务。 |
| `git diff --check -- plans/ARCH-AW-004-ds-detailed-design/spec.md` | exit0，stdout/stderr空；另用起点对比覆盖未提交/未跟踪差异，不仅依赖tracked检查。 |
| `git diff --no-index --check /private/tmp/arch-aw-004-r2-spec-0k5rn2r8/before/plans/ARCH-AW-004-ds-detailed-design/spec.md plans/ARCH-AW-004-ds-detailed-design/spec.md` | exit1，stdout/stderr空；表示确有spec差异、无空白诊断，不写成exit0。真实receipt在`pm/whitespace-checks.json`。 |

PM人工复核增量优先级、C/H/TCP/closing名额、64线程与L3扩展profile区别、按item公平/stop边界、日志故障与事务未知、重复apply幂等、维护CAS和逐场景保留之间的关系；这是规格自检，不代替后续Development技术设计或fresh-context QA。当前r1角色文件仍是r1，spec已是r2 draft；未为了全bundle Revision一致而改写后续角色历史。

本轮没有应用/sidecar/端口/浏览器tab/数据库/构建/分支/worktree；未运行G0、负载、原生、设备或项目测试。`/private/tmp/arch-aw-004-r2-spec-0k5rn2r8/pm/`仅有本轮stdlib脚本与JSON检查附件，连同协调起点暂留供Owner审阅及后续追溯，权威要求/结果已在本spec自足记录，不以易失tmp作唯一依据。

## 11. r2批准记录PM核对与交接（历史保留）

以下是范围批准转Development时点的PM记录，原检查和输入事实保持；其“尚未授予最终验收”和未来交接措辞不代表当前gate。后来完成的设计终验及本次状态同步见第12节。

2026-10-18（Asia/Shanghai）以`/private/tmp/arch-aw-004-r2-exec-ns_oqo5j/before/`及`baseline-manifest.json`为新起点，先确认当前草案SHA与Owner直接批准的`e5c92a6fb0ec2b7fbe4086a1dc1d27402c011c07464941363a063a4f364fe4b9`一致，再仅记录批准和交接。辅助`user-approval.txt`保存直接用户原话；权威摘要与原话已在本spec第1/9节自足记录，不依赖临时副本。

复用原stdlib规格检查逻辑，新建并运行`python3 /private/tmp/arch-aw-004-r2-exec-ns_oqo5j/pm/check-approved-spec.py`：最终exit0。新基线以`files`封装文件条目并含`absent`记录，与旧平铺摘要map不同，初次适配曾exit1；已仅按真实结构修正新tmp脚本的基线读取，旧脚本/证据未改，R/AC保护断言未放宽。当前元数据检查为owner_approved，23个R/29个AC全覆盖、26本地链接（7含anchor）、17表/围栏/尾空白及10路径检查通过。

严格对新起点比较：第4节R1–R23整段、29条AC原行、allowlist原表、第6/7节风险与排除、r1/r2既有修订历史行、原PM自检表及**附录A整体**字节均未改变；r1完整引文仍为205行、原SHA不变。r1正文/tasks/checklist、docs双语索引与既有AW/DAA/SMA四正文共9保护路径原字节不变。PM仓库写入仅spec；共享根索引由主协调机械同步DS行，其余并发变化不归PM、不回退。检查、保护摘要和approval delta只写新起点的`pm/`附件，不修改旧r2-spec/r1临时证据。

本次`git diff --check -- plans/ARCH-AW-004-ds-detailed-design/spec.md`为exit0；新before对当前spec的`git diff --no-index --check`为exit1且stdout/stderr空，表示批准记录确有差异、无空白诊断。本次为PM核对而非r2独立QA。交接精确批准后的spec与差异给唯一主协调，由其串行启动Development修订设计，再交新的fresh-context Verification；尚未授予最终验收或软件/协议/负载/数据库/原生实验权限。PM记录结束后停写。

## 12. r2设计终验状态与收尾

本次只依据Human Owner在本主会话的直接接受原话及既有Verification接受记录同步规格状态；未重开PM范围、未增加Revision、未重审设计或启动Development/QA。已核对接受正文SHA`0eb3c149bf7093bbdce2f0b7a07af71e769fe24cb04a542c7f4dc43e6979eecb`与原QA输入一致，当前checklist SHA为`1839ce7917425e1ca42977b71bb6f23682aa11574db09c8254dd02cbc5a28268`；原QA输入spec SHA`ff49d20b220bb6c45e94690ab9fa9b9c941ce761e26c65df6b42f15b3ac50874`仍是当时真实指纹，本次状态delta不会改写该事实或旧receipts。

资源收尾由主协调执行，既有checklist §7已记录：三个一次性文档写入helper共56087字节已删除，无运行占用；r1/r2-spec/r2-exec三目录约4MB核心证据继续保留。本角色只引用已发生的收尾，不执行额外清理，不触碰DAA或未知资源。

本轮仅做状态delta、R/AC/allowlist/风险/排除/附录A原文保护及必要Markdown空白/本地链接核对，receipt保存在`/private/tmp/arch-aw-004-r2-exec-ns_oqo5j/closeout/pm/`；不改旧PM/QA receipts或其他角色文件。设计终验已完成，只余未来独立G0、实施、负载及真实环境gate；状态交接给主协调后停写。

<a id="r1-spec-history"></a>
## 附录 A：r1 完整原规格历史快照

以下逐行引文完整保留本轮起点的205行r1 spec，含原始要求/AC/allowlist/风险、批准与当时gate叙述。其元数据、未发生后续角色的说法及章节指向均属于**r1记录时点**，不是当前r2 gate；r1后来交付/独立QA与未终验事实以当前第1/9节和原角色文件为准。唯一active元数据仍是本文件开头的r2 draft；引文不是第二spec或另一任务事实源。

历史原文SHA-256：`5cb85aba5bbbc4d608e56e218ad2e13873af4992848823bd9500dce42714aa26`。去除下方每行引文标记可恢复原字节。

> Task ID: ARCH-AW-004
> Revision: r1
> Status: owner_approved
> Owner Role: PM
> Allowed Writers: PM, Human Owner
> Handoff: Human Owner approved the exact ARCH-AW-004 r1 documentation scope on 2026-10-18; PM transfers to Development for the approved documentation work; fresh-context Verification and Human Owner final acceptance remain pending
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Task Namespace: aiis-ics-arch
> Classification: root
> Capability: DS 首版多实例 S7 模拟器详细设计及 DAA/CU 复用依据文档
> Owner: Automation World
> Acceptance Chain Reference: aiis-ics-arch::ARCH-AW-004 r1 scope approval -> Development documentation handoff -> fresh-context Verification -> Human Owner final acceptance
> Related Task: aiis-ics-arch::ARCH-AW-002; aiis-ics-arch::ARCH-AW-003; aiis-ics-arch::DAA-001; aiis-ics-arch::DAA-002
>
> # DS 多实例 S7 模拟器详细设计规格
>
> ## 1. 目标、请求依据与当前 gate
>
> 新建独立 DS 设计任务，交付可供以后单独实施引用的中文详细设计 Markdown，并基于正在开发的 DAA 核实可复用部分。本任务不重开已验收的 ARCH-AW-002，不把设计验收转为代码、协议服务端或设备行为已实现的声明。
>
> 2026-10-18（Asia/Shanghai），Human Owner 的本次请求为：
>
> > 好的，先单独建立DS设计任务，把详细设计md整理出来，结合正在开发的DAA确认可复用部分。首版只做多实例S7模拟，支持DB/UDT导入、点位编辑和可配置读写策略，Modbus和响应模拟后续再做，先不改代码。
>
> 该请求明确了文档目标、首版功能边界和代码排除项。`ARCH-AW-004` 与 `r1` 是 PM 在核对未占用后分配的任务标识，不声称用户在该初始原话中点名 Task ID 或 Revision。PM 当时按 STD 形成具体可审阅的 r1 draft，未预写范围批准、Development 或 QA 结论；该草案时序保留在第 9 节。
>
> 同日，Human Owner 在来源会话 `01a13d84-c40c-7bc3-9cca-e7cb57438d62` 明确批准精确 `ARCH-AW-004 r1`。主协调已用 `read_thread` 核实实际 `userMessage`：turn `01a14e52-7297-7bb0-9eaf-eee22a10dfa7`，message `01a14e52-72c2-7331-a357-f4e6840e8ff8`（2026-10-18，Asia/Shanghai），原话为：
>
> > 好的，帮我新建一个「DS 设备模拟器」会话，继续 ARCH-AW-004 r1。这个设计任务范围批准，先把详细设计文档整理出来，结合 DAA 确认可复用部分，先不改代码。
>
> PM 据此记录 `owner_approved`，当前 gate 为 Development 按第 3 节已批准 allowlist 交付设计正文、只读复用核对与文档自检，不重复请求范围批准；尚无 Development 交接、独立 QA 或最终验收事实。新会话 `01a14e52-eeb4-7c82-bade-bc0a237fa2ff` 接手本任务唯一 active lifecycle coordinator，来源会话不再并行编辑本任务。此次记录不改变 r1 的范围、需求、验收、allowlist 或风险，也不授权软件实施；最终验收仍归 Human Owner。
>
> 本任务只产出设计与文档核验。首版实施可以后续独立立项；本次不得创建 DS 工程壳、模块、运行配置、依赖或测试程序。
>
> ## 2. 已有依据与设计效力
>
> PM 已消费根 AGENTS、README/PLAN 双语、docs 与 plans 索引、AW README/PLAN 双语、DAA README/PLAN 双语、实际 PM role 与 canonical lifecycle workflow；新任务目录不存在既有 tasks/checklist，不预造后续角色文档。适用 `aiis` 与 `project-governance`；专门技术设计交给 Development 按第 8 节 skill 路由处理。
>
> | 依据 | 本版须保持的效力与边界 |
> | --- | --- |
> | [AW 白皮书 DS 章节](../../docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md)、[AW 运行原理 DS 章节](../../docs/AIIS_AW_Runtime_Design.md#ds) | DS 是开发、测试、联调工具；配置区域决定自动模拟或写入保持，不固定 DB 编号/数量。统一写入口在提交前拒绝越权；跨重启持久化、服务核心语言及协议库尚无已实现结论。 |
> | [ARCH-AW-002](../ARCH-AW-002-agent-runtime-design/spec.md) | r3 文档已验收，作为既有总体边界；本任务不修订该 bundle、不重跑或继承其 QA。 |
> | [DAA 详细设计](../../docs/AIIS_DAA_Detailed_Design.md)、[ARCH-AW-003](../ARCH-AW-003-daa-detailed-design/spec.md) | 已验收设计是可对读依据，不能代替当前 DAA 实现或原生验证。 |
> | [DAA 当前说明](../../automation-world/data-acquisition-agent/README.zh-CN.md)、[DAA PLAN](../../automation-world/data-acquisition-agent/PLAN.zh-CN.md)、[DAA-002 Development §6.9](../../automation-world/data-acquisition-agent/plans/DAA-002-local-acquisition-loop/tasks.md) | 2026-10-18 本次复核快照：DAA-001 Stage A 已验收；DAA-002 r2 已从历史阻塞恢复为 `implementation_in_progress`。B0及非原生 DEV 检查存在，Owner 原生保存/重载/正常退出与稳定 ID 已对账，同一隔离 profile 重开后保持停采。其余 B6 原生点位/激活/采样/历史验证仍在进行，尚无完整 developer_handoff、独立 QA 或最终验收。正文以检查时快照标记事实，不能称其能力全部已验收。 |
> | DAA `tia_source.rs`、`plc_layout.rs` 及点位编辑调用链 | Development 必须核对实际函数、支持范围与调用者，再决定复用等级；当前受限解析、偏移推算不等于完整 TIA 布局引擎，也不存在已确认的通用公共 parser crate。 |
> | [CU 公共说明](../../automation-world/console-ui/README.zh-CN.md) 与公共 UI 导出 | 按当前实际公共源码和已验收任务核对；DS 以编译期消费为方向，业务状态与运行生命周期归 DS，不依赖 CU 在线。 |
> | 既有 `vibe-l2-front-end/tools/plc/s7-virtual-plc/` | 只读参考现有模拟规则、内存和 S7 server 路径；未经证据不能把库的理论能力写成当前工具已验证的写保护。不得修改该外部工程。 |
>
> 工作树有多个并发任务修改。各角色须记录自己的起点与精确差异，保留其他任务内容，不 reset、不整文件回退、不将全树 dirty 归因本任务。DAA/CU 继续变化时，正文记录检查日期、路径和事实等级，后续实施再刷新依赖快照。
>
> ## 3. 分阶段精确 allowlist
>
> 以下共 10 个仓库文件，不使用目录通配。文件进入 allowlist 不等于跨角色或越过 gate 的写权限。
>
> | 精确路径 | 写入者、时点与允许内容 |
> | --- | --- |
> | `plans/ARCH-AW-004-ds-detailed-design/spec.md` | PM / Human Owner；范围、需求、验收、风险与真实批准历史。PM 本轮唯一仓库写入。 |
> | `docs/AIIS_DS_Detailed_Design.md` | 精确 r1 批准后 Development；新建本版 DS 详细设计正文。 |
> | `docs/README.md` | 批准后 Development；仅新增 DS 设计文档入口及用途/非实施说明，保留其他行。 |
> | `docs/README.zh-CN.md` | 批准后 Development；与英文新增行语义对应。 |
> | `plans/ARCH-AW-004-ds-detailed-design/tasks.md` | 批准后 Development；实施计划、只读技术核对、实际文档差异、自检与 developer_handoff。 |
> | `plans/ARCH-AW-004-ds-detailed-design/checklist.md` | 精确 developer_handoff 后新 fresh-context Verification；独立文档核验、verdict 与 Human Owner 真实终验。 |
> | `PLAN.md` | 主协调；仅新增/机械同步 ARCH-AW-004 唯一行，引用 spec，状态不强于角色事实。 |
> | `PLAN.zh-CN.md` | 主协调；同一任务行的中文对应。 |
> | `plans/README.md` | 主协调；仅新增/同步 ARCH-AW-004 唯一行，只链接实际存在的角色文档。 |
> | `plans/README.zh-CN.md` | 主协调；同一 catalog 行的中文对应。 |
>
> 原 AW 白皮书、AW Runtime、DAA/SMA 详细设计和其他任务 bundle 保持本版起点内容，不为新增 DS 文档重写已有已验收正文。若确需增加跨文档链接，可由新文档单向引用；若必须变更 allowlist、需求、验收或风险，先回 PM 新 Revision 并重新批准。
>
> 排除全部源码、UI、测试、依赖/锁文件、配置、SQLite 文件、正式 schema/DDL、env/YAML、contracts、CODE_INDEX、AGENTS、角色/skills/workflow。只读核对可以查看相关源码及声明的依赖信息，不能安装、构建、启动、连接、发送、迁移或更改它们。
>
> ## 4. 编号需求
>
> ### R1. 独立正文与当前/目标区分
>
> 正文须可独立阅读，记录检查日期、任务与内容修订，链接本 spec 和已有 AW/DAA 依据。区分当前源码事实、已决定首版目标、推荐实现机制、需原型验证的候选和未来扩展。DS 定位为 Tauri 管理的开发工具，服务端模拟核心与管理界面分层；仅在当前设计中给出接口职责和运行视图，不新建工程。
>
> ### R2. 基于 DAA/CU 实际调用链的复用矩阵
>
> 逐项核对并列出来源文件/符号或可复查段落、当前状态、支持限制、DS 复用方式和后续 gate。至少覆盖 CU 公共壳/主题/语言/导航、DAA 点位/DB 编辑与导入预览、源解析、UDT 展开、偏移推算、S7 类型编码/解码候选、SQLite 配置/版本/激活模式、日志与快照、采集客户端连接及历史上传。
>
> 明确区分“可直接消费的公共出口”“可借鉴但需独立抽取/适配的 DAA 私有实现”“不适用 DS 的采集/历史上传业务”；未获 DAA 最终验收的代码注明状态，不写成已接受共享能力。不得为了 DS 把 DAA 纳入本任务重构，不承诺公共 crate 已存在，不把 DAA S7 客户端等同 DS S7 服务端。复用结论应足够支持后续实施估算和分工，而非只有泛化建议。
>
> ### R3. 最小组件与数据/控制流
>
> 给出组件图与职责说明，至少包含 DS 页面、Tauri IPC adapter、配置/校验/激活服务、实例管理、规则调度、统一内存访问、协议 server adapter、配置 SQLite、运行快照/日志。明确配置从草稿到已保存到运行生效的路径，以及客户端读写、模拟 tick、UI 手改、初始化/重置的进入路径和反馈；不把业务写入移入 UI 或 CU。
>
> 服务核心可在 Rust 与 Python sidecar 等候选间进行有依据的评审；必须列最小选型条件、现有证据不足处及后续原型 gate，不因 Tauri 强制 Rust，不把语言选择悬置为整个详细设计无法确定的理由。
>
> ### R4. 多实例、endpoint 与生命周期
>
> 每实例有稳定 ID、显示名、S7 endpoint/端口/rack/slot 相关身份、配置 revision、独立内存/规则/统计/日志和运行状态。说明同机不同端口的多实例方案、绑定冲突、失败隔离、客户驱动自定义端口兼容前提，以及配置保存不自动开始监听。
>
> 明确至少启动、运行、暂停规则、停止、失败、重置的含义与合法操作：暂停模拟是否继续接受客户端、停止是否关闭连接、重启何时重新初始化。给出进行中请求/规则 tick、停止与重置之间的屏障与拒绝行为；同一实例不得重复监听，单实例故障不自动停止其他实例。应用关闭策略给出首版推荐并说明其后续原生验证，不默认承诺后台服务继续运行。
>
> ### R5. DB/UDT 导入、点位编辑与布局
>
> DB 号、名称、数量、点位和区域策略均可编辑，示例不指定业务 DB 编号作为拓扑约束。保存完整源、来源/摘要、声明树、UDT 引用和地址来源；`.db` 为 TIA 源文件，与 SQLite 文件区分。
>
> 列首版支持/拒绝/人工确认矩阵，诚实复用 DAA 当前受限范围。导入要预览差异并人工确认，缺失/循环 UDT、不支持语法、重复身份、越界和重叠均明确处理。偏移推算手动触发、提醒完整 DB/UDT、限定标准非优化与已支持布局；不从选中叶点猜测完整偏移，不将人工地址等同自动布局证明。重导入、类型/结构更改取消受影响确认，并给出运行中结构修改的首版安全应用策略。
>
> 需核对 DAA 导入器是否解析 `BEGIN` 到 `END_DATA_BLOCK` 的初始赋值；当前若仅消费声明结构，DS 不能默认导入 TIA 运行初值。首版须明确类型默认值与 DS 显式配置初始值的优先级、未导入初值的 UI 提示，以及重导入时保留/取消初值确认的规则。
>
> ### R6. 本地 SQLite 配置与运行内存分离
>
> 用概念模型列实例、DB/UDT 源/结构、点位/地址确认、区域/覆盖策略、规则参数、配置版本及必要应用状态。只定义职责和约束，不交付正式 DDL/schema 或写数据库。
>
> 定义保存/校验/显式应用的反馈、配置冲突/激活失败/重开恢复和旧 revision 的处理。当前模拟内存值与配置初始值分开；首版跨进程重启的运行值策略应给明确推荐与理由，不能声称配置 SQLite 自动保存所有运行值。自动启动、默认监听范围、存储路径与身份使用独立 DS 命名，具体应用包名/开发端口可留后续工程任务确认。
>
> ### R7. 可配置读写策略与所有权
>
> 至少给出自动模拟、写入保持及初始值/持续固定值的语义表，并定义策略作用层级、继承/覆盖优先级和冲突校验。自动模拟区默认客户端只读；写入保持仅初始化或显式重置应用初始值，此后允许的客户端写入跨 tick 和重连保持。客户端读取权限、客户端写权限、规则写、UI 手改和重置权限分别表述，UI 不能成为隐式绕过入口。
>
> 持续规则与客户端可写字段重叠的首版推荐是校验拒绝，要求唯一写入所有者；若选择更复杂语义，须明确配置和可验证时序，不以最后写者偶然覆盖作为合同。至少包含一个不固定 DB 号的“初始值 → 客户端写入 → 后续 tick/重连 → 显式重置”示例。
>
> ### R8. 协议写入准入与兼容矩阵
>
> 列 S7 server 首版读/写操作、支持的数据形态、边界/权限错误、服务端在提交前拦截的选型要求、连接身份/端口兼容和未来技术验证。协议层写请求可能只有地址/长度/原始字节，应通过已确认布局与触达范围校验，不能假设请求自带业务字段类型。
>
> 拒写须在内存变更前完成并返回真实协议失败；只在事后回调报警或写回旧值不满足要求。若候选库不能证明该能力，标成技术阻塞/替代适配评审 gate，不能靠文档承诺通过。多项批次的失败粒度、部分成功及返回行为需在设计中明确推荐并受协议能力核实。
>
> ### R9. 统一内存访问、并发和一致性
>
> 所有写来源经同一实例内受控入口，定义按实例串行化/受控提交模型和读取可观察边界。整字节/跨字段写覆盖其中 BOOL 位时，要按整个触达范围检查权限；同字节不同位合法写避免读改写丢更新。覆盖地址/长度/bit/载荷校验、同点并发客户端、规则 tick、UI 手改、停止/重置、配置换版及失败不改变内存的行为。
>
> 不要无证据承诺整个 PLC、跨 DB、多个协议请求或多个实例的全局原子快照。给出后续实现需核实的原子粒度和协议结果与日志结果的一致关系。
>
> ### R10. 页面与可观察反馈
>
> 参考 DAA/CU 当前页面组织，给出 DS 首版导航和逐页对象、字段、操作、反馈及权限。至少能完成实例增删/配置、DB/UDT 导入预览/编辑/地址确认、模拟与读写策略设置、显式应用、逐实例启动停止/暂停/重置、在线值观察/手改和有界日志查看。
>
> 展示已保存/运行 revision、监听状态、客户端连接、规则启停、当前值/更新时间/来源、拒写原因和实例故障；不把 UI 点击、配置保存、连接成功或协议写成功解释为真实设备动作。日志与刷新有界、不要每 tick 无限堆积；记录必要状态变化及写入审计，不复制 DAA 采样历史/outbox。
>
> ### R11. 后续验证场景与分阶段实施交接
>
> 提供未来实现验收矩阵，至少覆盖：两个实例隔离；同端口冲突；完整/缺失/循环 UDT；不支持布局与手工地址；重导入确认失效；自动模拟变化与拒写；写入保持跨 tick/重连；初始/固定值区别；重叠字段/BOOL 位越权；多客户端并发；停止/重置/换版竞态；权限拒绝内存不变；保存/应用失败；重开初始化；退出资源释放；DAA 自定义端口连接模拟器。
>
> 每场景写预期、责任与需要的证据类型。本轮只审阅这些设计，不执行协议/原生/数据库实验。候选实施阶段先验证 server 写保护及客户端兼容，再落最小实例/配置/内存/UI，最后联调；公共提取应受实际复用收益和 DAA 稳定状态约束，不阻塞既有 DAA 工作。Modbus、命令响应/握手/状态机/延迟响应为未来独立范围。
>
> ### R12. 文档质量与边界控制
>
> 正文结构、示例、表格/图与 R1–R11 一致；新增 docs 索引双语对应、链接有效。Design 文档不替代公开 contracts、任务 spec 或运行手册，不新增流程 runtime/低代码画布、中央 Backend、账号权限服务、真实 PLC 连接、发布部署或自动迁移。
>
> ## 5. 验收标准
>
> 下表的“通过”仅指本版文档交付满足设计要求，不是软件或现场行为已通过。
>
> | AC | 对应需求 | 文档可核验标准 |
> | --- | --- | --- |
> | AC1 | R1/R12 | 独立 DS 正文、日期/revision/效力、已有依据及首版/扩展边界完整；不重开已验收任务。 |
> | AC2 | R2 | 复用矩阵有实际路径/符号及状态/限制/方式/gate，覆盖规定主题；DAA-002 未验收、parser 非公共能力、client/server 不等价均准确。 |
> | AC3 | R3 | 组件职责、控制/配置/读写/反馈流可追踪，CU 与 UI 不拥有设备内存或业务执行。 |
> | AC4 | R4 | 至少两个实例的 endpoint/内存/日志/规则/故障隔离可从设计推演；端口冲突和自定义端口前提明确。 |
> | AC5 | R4/R6 | 生命周期、暂停/停止/重置、关闭/重开、在途屏障与配置应用语义没有矛盾。 |
> | AC6 | R5 | 导入/编辑/确认流程、支持矩阵与 DAA 实际范围对应；完整结构、受限推算、重导入失效和运行中修改均明确；不假定解析器导入运行初值，默认值/显式初值及提示规则齐全。 |
> | AC7 | R6 | SQLite 概念配置与运行内存分离，revision/激活/恢复有明确行为，跨重启值策略有首版推荐。 |
> | AC8 | R7 | 策略表、层级优先级、来源权限、唯一写入所有者和完整保持/重置示例一致；不固定 DB 编号/两个 DB 拓扑。 |
> | AC9 | R8 | server 写保护必须提交前拦截，原始地址/字节校验与协议失败/多项返回边界明确；未验证库能力不写已支持。 |
> | AC10 | R9 | 字节/BOOL 重叠、并发写、读改写与停止/换版竞态可推演，失败内存不变；原子边界不夸大。 |
> | AC11 | R10 | 逐页流程覆盖完整首版操作与有界反馈，依 CU 公共消费，配置保存/运行事实分开。 |
> | AC12 | R11 | 验证矩阵覆盖全部规定场景，标明未来证据和分阶段依赖，未用本轮静态阅读代替运行证明。 |
> | AC13 | R3/R11 | 服务核心候选有实际证据、选型条件和原型 gate；后续实施与公共抽取分工明确，Modbus/响应模拟延期。 |
> | AC14 | R12/§3 | 新文档/索引语义和链接/围栏/表格可检查，实际差异严格在 allowlist；他任务 dirty 保留，未改代码/配置/旧任务。 |
> | AC15 | §1/§8 | 精确批准、Development 自检/交接、fresh-context QA 和 Human Owner 最终验收据真实时序分开；不预造 QA 或终态。 |
>
> ## 6. 风险、回退与未决技术 gate
>
> | 风险 | 本版设计要求与后续处置 |
> | --- | --- |
> | DAA 正在开发，复用点快速变化 | 固定检查日期与文件/符号；如实标记其状态和限制，后续实施前刷新；不为复用修改 DAA。 |
> | server 库只通知写后事件，无法提交前拒绝 | 作为首个技术原型 gate；不以周期覆盖冒充写保护，评估其他适配或明确不满足后停止该候选。 |
> | TIA 类型/布局覆盖不足 | 先定义受支持子集和人工确认，缺定义拒绝推算；不承诺优化 DB 或所有 S7 CPU。 |
> | 共享内存并发和 BOOL 位越权 | 统一入口、整个触达范围准入、明确原子粒度与在途屏障；后续测试需要真实协议和内存对照。 |
> | DS 详细设计被当成生产控制证明 | 正文、示例、交接及 QA 都保留开发工具定位和证据层次；真实设备另行授权验证。 |
> | 文档任务扩大为框架抽取/工程启动 | 精确文件 allowlist；只记录候选目录/接口/阶段，抽取、建工程、安装/运行留独立任务。 |
>
> 本轮是可逆文档写入。回退只针对本任务新增正文/入口和本任务索引 delta，保留原已验收文档、其他 dirty 和角色历史；不得自动 reset 或删除他人文件。服务语言/库、精确 CPU/操作/类型支持、应用包标识/开发端口、持久内存扩展等未决项应记录责任、证据与下一 gate；不能用待决列表替代本版必须具体说明的数据/策略/生命周期。
>
> ## 7. 排除项
>
> 不实现 DS、共享 parser/runtime/crate、S7 server、SQLite 或 UI，不修改 DAA/CU/SMA/CA/Backend，不补测这些任务；不安装依赖、构建/启动应用、监听端口、运行协议/数据库/原生实验、操作真实 PLC 或第三方接口；不写 schema/迁移/配置、不发布/部署/提交/推送、不向其他用户会话或外部人员发送任务。
>
> 首版不含 Modbus、响应/握手/状态机模拟、完整 PLC 执行引擎、SMA/CA 可视化流程 runtime、中央配置服务、生产托管/高可用或现场安全证明。可以说明扩展边界，不预建扩展空壳。
>
> ## 8. 角色交接与所需 skill
>
> 1. **PM → Human Owner（范围批准已完成）**：Human Owner 已于 2026-10-18 明确批准本 `ARCH-AW-004 r1` 文档任务，批准原话与来源标识见第 1 节；10 路径、R1–R12、AC1–AC15 和风险保持该精确版本。此次为范围批准，不是最终验收。
> 2. **Human Owner → Development（当前 gate）**：按已批准 r1 直接推进，读取完整已形成 bundle、最近 README/PLAN 和当前工作树。使用 `aiis`、`project-governance`；涉及具体 Tauri/运行时/点位技术设计时按实际范围消费 `desktop-tauri`、`rust-runtime`、`plc-point-mapping`，只做设计所需只读核对。后续 UI/用户文案代码任务另按 `frontend-ui` / `i18n-workflow`，本版不借 skill 扩大实现。
> 3. **Development → fresh-context Verification**：交付精确 r1、批准依据、正文和入口、路径/符号复用证据、diff/指纹、文档检查结果及未运行项；QA 用新 fresh context 独立审阅 AC，并只写 checklist。不得以既有 ARCH-AW-002/003 或 DAA/CU QA 代替本版核验。
> 4. **Verification → Human Owner**：给真实文档 verdict、剩余技术原型/实现 gate 与最终验收入口；`qa_passed` 只表示设计文档可供终验，不启动软件实施。
>
> 本 profile 为 `contract_only`。角色文档归属、串行 handoff、当前工作树和 diff 审计是合同控制，不宣称平台 ACL、强制路由或 Agent Team 自动激活。
>
> ## 9. 修订与批准记录
>
> | 日期 | Revision | 真实记录 |
> | --- | --- | --- |
> | 2026-10-18 | r1 draft | PM 根据用户本次明确文档请求分配独立 ARCH-AW-004，形成多实例 S7、DB/UDT、点位编辑和可配置读写策略的具体范围；未取得精确 Revision 批准，未产生 Development/QA/最终验收事实。 |
> | 2026-10-18 | r1 draft 事实刷新 | 只读核对 DAA PLAN 与 DAA-002 tasks §6.9，更新其恢复实施及部分原生证据快照；本任务范围、allowlist、R/AC、Revision 与批准 gate 均不改变。 |
> | 2026-10-18 | r1 owner_approved | Human Owner 在来源会话明确批准继续 `ARCH-AW-004 r1` 的详细设计及 DAA 复用核对，先不改代码；实际 userMessage 与原话已核实并记于第 1 节。PM 记录批准及向 Development 的交接，r1 范围、10 路径、R1–R12、AC1–AC15、风险和既有 draft 历史保持；本会话接手唯一协调，独立 QA 与最终验收仍待后续真实发生。 |
>
> Human Owner scope approval of exact ARCH-AW-004 r1: approved，2026-10-18（Asia/Shanghai）；来源及原话见第 1 节。
>
> Human Owner final acceptance: pending。
