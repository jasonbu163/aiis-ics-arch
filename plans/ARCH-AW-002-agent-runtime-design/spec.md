Task ID: ARCH-AW-002
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Existing Human Owner authorization for the bounded documentation task recorded below; Development to revise the whitepaper first, then deliver the detailed design, without code changes
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_governance
Capability: AW 白皮书原位修订与 CAF/CU/DAA/SMA/CA 详细原理设计文档
Owner: Automation World
Acceptance Chain Reference: Human Owner 文档范围批准 -> 本 r2 范围归档 -> Development 文档交付与 tasks.md -> fresh-context Verification checklist.md -> Human Owner 最终验收
Related Task: aiis-ics-arch::ARCH-AW-001; aiis-ics-arch::ARCH-MULTI-001; aiis-ics-arch::ARCH-BE-003; aiis-ics-arch::CA-CONFIG-001

# AW 白皮书修订与详细原理设计文档

## 1. 目标与真实批准依据

本次是有限的文档任务：先原位修订 AW 白皮书，使角色和近期路线符合最新讨论；再交付一份独立、可供后续实施引用的详细原理设计。将 r1 中的设计正文交给 Development 重组到 `docs/`，本 spec 专门规定本次文档范围、内容要求、验收和交接。

2026-10-15，Human Owner 在主会话明确表示：

> 好的，就按这个顺序整理，先修订AW白皮书，再出详细原理设计文档，把CAF、CU以及这次DAA、SMA、CA的讨论都纳入，ARCH-AW-002调整为这次文档任务，先不改代码。

该原话批准的是本 Task ID 的上述文档范围和顺序。`r2` 是 PM 本次整理时赋予的 Revision 标识，不声称 Human Owner 在原话中说过 `r2`；状态记录依据为这次实际范围批准，不扩张为任何功能实施授权。主会话将原话、本 r2 和当前工作树一起交给 Development，无需为相同文档范围重复征询。

本轮文档可描述目标结构、合同草案、原理、风险和未来验证方式；不得创建功能、实现表结构、安装依赖、连接设备或变更运行配置。设计通过也不表示未来实现范围、具体依赖、中央服务或现场动作已经获批。

## 2. 文档分工与当前基线

| 产物 | 本次职责 | 不承载的内容 |
| --- | --- | --- |
| `docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md` | AW 角色、边界、分阶段路线和当前/长期关系的总领白皮书 | 精确实现步骤、开发证据或本次 QA verdict |
| `docs/AIIS_AW_Runtime_Design.md` | CAF/CU/DAA/SMA/CA 的详细运行原理、配置、数据/流程合同及故障行为 | 已实现声明、生产操作手册、未经批准的协议/库定案 |
| 本 spec / 后续 tasks / checklist | 范围和批准 / 实际文档变更及 DEV 检查 / 独立文档验证 | 第二份长期设计正文 |
| 双语 README/PLAN/catalog/ROADMAP | 入口、阶段和边界摘要，引用真实存在的产物 | 重复整篇设计或预造角色证据 |

已读根 AGENTS、README/PLAN pair、AW README/PLAN、DAA/SMA README、现有白皮书相关章节、根任务目录和本任务 r1。ARCH-AW-001 的既有验收只证明当时工程迁入、隔离和独立启动，不证明 SQLite、新 API、共享 UI 或新控制闭环已完成。

主 AW 会话的最新上下文是：旧 CA 按 CAF 理解，AW 中 CA 指新控制角色，并提出 `console-ui`。Development 应只读核对实际目录和已有文档；用户的命名决定、已有源码事实与本次设计目标分别标记。不借文档任务认证未验证的迁移，也不覆盖并发会话的源码或历史证据。

## 3. 内容要求

### R1. 先修订白皮书，再写详细设计

1. 白皮书原位更新，保留文件名和既有入口；在正文记录本次更新日期、内容修订标识及 v0.4 来源关系，不把文件名当成冻结的新发布版本。
2. 保留有效历史来源、引用标识和旧方案的来历；将失效方向明确归为历史/长期目标，更新正文中的现行结论。不能只追加一段声明却让同文中的当前规则互相矛盾。
3. 白皮书聚焦角色和路线，详细原理由新设计文档展开；两者互链并声明当前能力、设计方向、建议和未决项的效力。
4. r1 的讨论结论迁入新设计文档时按主题重组，覆盖 R2–R8；不复制为聊天逐字稿，也不把新设计写成已经运行的系统。

### R2. CAF、CU 与 Agent 的角色

| 名称 | 文档必须说明的边界 |
| --- | --- |
| CAF | 原 CA 的冻结/参考工程身份；与新 CA 明确区分。未确认的英文全称或路径不擅自创造；不得把冻结参考工程宣称为新的活动共享运行时 |
| CU / console-ui | 建议定位为共享 UI 组件库及可运行的 UI 设计工作台，各 Agent 在源码/构建阶段引用，安装运行无需 CU 在线；设计定位与已实现情况分开 |
| DAA | 采集、解码、时间/质量标记、事实 API 上传；固定配置链路，首版无需业务低代码流程 |
| SMA | 将 AW 事实加工为语义对象并向第三方/上层 API 投递；不得直写平台业务表或 PLC |
| CA | Tauri 管理入口和独立 Rust 控制执行，消费本系统校验并持久化的有效执行意图，映射/判断后写设备并回报结果 |
| Backend | 接入校验、持久意图、事实接口、原子领取与回执，拥有内部存储和 schema；不在请求线程承担 PLC 常驻循环 |

“对外投递/对内执行”按业务责任划分：CA 可以 POST 领取/心跳/回执，SMA 可以 GET 补充材料；CA 回执不交给 SMA 代行。采集、映射与执行保持独立入口、配置、凭据、运行状态及生命周期，可共享代码而不合并为同一进程。

### R3. CU 的 UI 低代码与业务流程画布

说明两种能力不同：CU 的 UI 组件编排用于页面/布局/参数界面；SMA/CA 的业务画布描述触发、取数、转换、判断和动作。二者可复用视觉组件和编辑交互，不能混用发布语义。

Rust Flow Core 属于运行时共享能力，不归 CU 组件库负责；CU 不直接操作 PLC，不成为 Agent 的在线依赖。详细设计给出模块关系和构建/运行两张视图，实际目录仅作为示意或经只读核对的现状，不在本轮新建 workspace、共享包或工作台源码。

### R4. DAA 的 S7 与 DB/UDT 设计

首版支持方向限于西门子 S7，其他协议延期；具体 CPU/驱动/访问方式/类型支持矩阵待后续实施任务确认，不宣称覆盖所有 S7。

- 导入 TIA 导出的 `.db`/`.udt` 文本源，保存完整结构、字段顺序、嵌套引用和来源；说明 PLC `.db` 源文件与 SQLite 文件不同。
- 支持单点编辑；手工地址与推算地址保留来源，修改结构/类型/数组等时标记受影响偏移待复核。
- 整 DB 偏移推算由用户手动触发，提醒 DB 与全部 UDT 信息完整；软件检查完整引用、支持类型、数组/字符串/对齐等布局，并在缺失或不支持时拒绝猜测。
- 绝对地址推算限标准非优化 DB，基于完整结构而非仅选中采集点；先预览影响，再确认保存草稿，不立即改变运行采集。
- 输入完整性不能证明与 PLC 当前程序一致，设计须要求与 TIA 实际偏移核对。
- 采集、重连、超时、分组和上报频率分别配置；显示时间、质量、失败与积压。`latest` 合并和 `samples` 批量样本模式作为待决取舍，不能把轮询等同完整事件采集。

### R5. 本地 SQLite 与 Backend API

当前阶段以本地 SQLite 保存配置，DAA 已明确采用；SMA/CA 建议复用同一生命周期，实例分别拥有独立库。说明 draft/active/previous 建议与白皮书 current/previous 长期双槽合同的区别，draft 保留/schema/切换策略待定。

Rust 配置服务负责校验和写入，Tauri 通过受控 command 管理；SQLite 事务保存和内存启用分别处理，说明批次边界、崩溃恢复及旧配置显式导入。不得形成 env/YAML/SQLite 多个可编辑业务配置权威。

配置回退与运行记录分开：outbox、采集待上报、消费游标、CA 执行事实和审计不能随回退删除。凭据引用、安全存储、保留量及缓冲容量是明确待决项；配置 SQLite 不自动等于离线无损或主机容灾。

DAA 通过 Backend 采集 API 上报，Agent 不持 Redis/业务库凭据、不依赖内部表或 SQL。Backend 可以改变存储实现，但已接收/可靠保存/仅入队的回执语义不能静默降低；Redis 不在本次部署范围，也不替代可靠执行意图真相源。

给出非冻结的信息合同草案：来源实例/设备/点位、样本或批次身份、值与类型、采集时间/质量、配置 revision、顺序/游标、接收或拒绝范围及可重试原因。API 路径、认证、包装、部分接收、幂等和容量策略待后续后端任务决定。

### R6. SMA/CA 共用可视化 Flow Runtime

推荐 Tauri + Vue 画布 + Rust 解释流程定义，不为每次编辑生成/编译 Rust 源码。共享编辑器、模型校验、调度、步骤执行、分支、取消和跟踪；分别装配角色节点、权限及副作用恢复策略，不共享进程、可写状态库或运行队列。

流程定义草案包含 schemaVersion、flowId/revision、role、节点类型/版本/参数、连线、资源引用和限额；执行记录另含 runId、输入身份、固定配置版本和步骤结果。画布位置不决定执行顺序。首版建议有限顺序/分支/等待、有向无环图及明确重入策略，不默认任意脚本、循环或插件市场。

节点合同说明输入输出、权限、超时、取消、副作用、幂等与恢复；SMA 装配拒绝设备写入节点，不能仅隐藏菜单。SMA 按目标 API 幂等合同重发；CA 先核实设备结果，公共重试工具不能统一决定副作用重试。

Vue Flow 仅为画布候选，具体依赖未定；完整 Node-RED 作为 Node.js 编排加 Rust 设备服务的备选。必须解释编辑器与运行时的区别，不宣称任意 Node-RED JSON/Function 节点可直接由 Rust 执行。

### R7. CA 控制语义与示例闭环

外部请求先经过本系统 API 校验和持久化，再由 CA 经 API 原子领取有效意图；入库不自动等于允许执行。不从任意外部 URL 直接取数据写 PLC，不通过 SQL 轮询任意业务表。

区分参数同步（可比较源版本并合并旧目标）与动作请求（逐条追踪），以及查询/领取、received/accepted/completed/unknown 等状态语义。提供令牌/租约、唯一写入方、现场条件时效/质量、写前核实和 PLC 最终联锁的设计责任。

下发节点封装暂存数据、提交序号、PLC 校验/确认、回执；多字段半写、确认丢失、超时、重启和取消不能靠盲重试解决。`unknown` 必须核实，数据库去重不等于物理动作恰好一次。精确握手和设备程序仍是未来专项。

给出三条典型流程：DAA 定时采集并上传；SMA 事实变化/周期映射并投递；CA 领取意图、映射/条件、下发并确认。解释持续条件与上升沿事件、配置发布与业务请求的区别，以及无设备副作用预览。回退流程定义不撤销已发生动作。

### R8. 近期/长期路线与待决项

当前阶段本地配置、API 上传与白皮书长期中央配置发布、AWB/Axum、PG/Redis、HA/SA 等方向分层，不强行同时建设。ROADMAP §3 配置流、§7 近期中央配置及关联阶段表必须同步，不能留下近期集中保存配置与本地 SQLite 权威并存的矛盾。

给出文档之后的候选实施阶段及验证关注点，不将全部阶段绑成本次交付或批准：DAA 最小采集闭环、有限共享流程、SMA/CA 模拟闭环、另行授权现场验证。保留支持矩阵、样本模式、API 合同、画布选型、SQLite 生命周期、后台托管、驱动、握手与仲裁等开放问题。

### R9. 来源、索引与说明一致性

白皮书与详细设计以中文正文交付，保持既有语言形态；docs README、根 PLAN/catalog 和 ROADMAP 按现有英文/中文 pair 同步。两份设计正文、索引和 ROADMAP 使用一致名称与边界，CAF 历史身份与新 CA 不能混淆。

保留既有白皮书有效来源和许可信息；新增官方技术来源只用于支撑实际事实，推论标为建议。新详细设计需可独立阅读并引用本 spec 及白皮书；不制造已冻结的可执行 API/schema 文件，不把公开合同搬出 `contracts/`。

## 4. 精确写入 allowlist

| 路径 | 允许的本次写入 |
| --- | --- |
| `docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md` | 先完成 R1–R8 的总领原位修订，保留历史来源/版本说明；不更名或新增白皮书副本 |
| `docs/AIIS_AW_Runtime_Design.md` | 再创建 R2–R9 的详细原理设计正文 |
| `docs/README.md`、`docs/README.zh-CN.md` | 增加两份文档入口与用途，保持 docs README-only 归属 |
| `ROADMAP.md`、`ROADMAP.zh-CN.md` | 仅同步本任务影响的角色/配置流/§7/关联阶段边界和设计链接，保留其他工作流事实 |
| `PLAN.md`、`PLAN.zh-CN.md` | 主会话机械同步 ARCH-AW-002 当前 Revision、状态、文档产物、验证摘要和下一 gate |
| `plans/README.md`、`plans/README.zh-CN.md` | 主会话机械同步唯一任务行，只链接已存在角色文档 |
| `plans/ARCH-AW-002-agent-runtime-design/spec.md` | 仅 PM/Human Owner 修订范围、真实批准与历史 |
| 同任务 `tasks.md` | Development 创建/更新文档实施、自检与 developer_handoff |
| 同任务 `checklist.md` | developer_handoff 后，fresh-context Verification 创建/更新独立文档验证 |

除上述路径外均不在本任务写入范围。尤其不修改 AGENTS、根/AW/Agent README 的运行声明、CAF/CA/DAA/SMA/CU 源码、配置、依赖、锁文件、数据库迁移、contracts 或其他任务 bundle；当前旧描述在新文档中注明其历史/现状效力，不顺手重写。需要额外文件或实质新选型时返回 PM。

## 5. 顺序与角色交接

1. Development 接收本 r2、Human Owner 原话、来源文档及当前 diff，先记录既有改动保护和文档边界。
2. 原位修订白皮书，固定本轮角色与阶段语义，再据此编写详细设计；最后同步允许的索引和 ROADMAP pair。
3. Development 记录实际检查、退出码、未决项与文档清单，形成精确 r2 developer_handoff。不得把文档描述写成实现完成。
4. 主协调启动 fresh-context Verification 审核本 r2、tasks、文档及 diff；Verification 不静默修文，不实施技术方案。
5. 独立文档 QA 后交 Human Owner 最终验收。未决技术选择可以作为本次文档中诚实记录的待决项，不伪造选型结论。

适用 skill：本次文档和跨角色边界使用 `aiis`、任务/索引治理使用 `project-governance`。遇到需要冻结算法、接口或依赖的具体技术问题，保留待决项并 handoff，不替未来技术角色工作。后续实现分别需要 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping`、`backend-arch`，不在本轮执行。

## 6. 验收标准与必要检查

| AC | 本次文档验收标准 | 对应需求 |
| --- | --- | --- |
| AC1 | 白皮书原位修订先于详细设计；保留原文件名、来源和可追溯修订说明，两文互链 | R1 |
| AC2 | CAF、CU、DAA/SMA/新 CA 定义清楚，现状/目标/建议区分，CU 运行不成为 Agent 前置 | R2–R3 |
| AC3 | UI 低代码与业务流程画布区分，Rust Flow Core 不归 CU；共享代码与独立运行边界一致 | R3/R6 |
| AC4 | DAA 无流程画布；S7/DB/UDT/单点编辑/手动整 DB 推算的完整性、非优化、预览、实点复核要求齐全 | R4 |
| AC5 | SQLite 本地权威、候选生命周期和记录分离、API 存储隔离及回执语义明确，无自动 Redis/中央服务建设承诺 | R5/R8 |
| AC6 | 有流程/节点合同草案、装配权限、不同恢复策略；Node-RED 与 Vue 画布的事实和建议无混淆 | R6 |
| AC7 | CA 有持久意图、原子领取、握手/unknown/唯一写入/PLC 联锁，以及发布与执行区别 | R7 |
| AC8 | 含典型链路、故障行为、未来分阶段验证和开放问题；不将文档通过等同实现或设备安全验收 | R7–R8 |
| AC9 | ROADMAP 双语同步近期本地配置与角色边界，消除 §3/§7/关联阶段的有效结论冲突；其他任务状态未被改写 | R8–R9 |
| AC10 | docs README、根 PLAN/catalog 双语入口一致，链接与围栏有效；本轮文件在 allowlist 内，无代码/配置/依赖变更 | R9/§4 |
| AC11 | tasks 如实记录 DEV 检查；fresh-context checklist 独立给出文档 verdict 和剩余技术边界，未冒充 Human Owner 最终验收 | §5 |

检查限于文档内容覆盖、术语/阶段交叉比对、Markdown 本地路径/新增锚点/围栏/表格、双语索引对应和 scoped diff/whitespace。记录真实命令和退出码；不因纯文档任务运行工程构建、PLC/数据库操作或全产品回归。已存在的无关断链单列，不静默扩大修复范围。

## 7. 风险、回退与停止条件

主要风险是旧名称与新角色混用、白皮书长期中央配置和近期 SQLite 冲突、CU 被误解为在线服务或运行时所有者，以及将设计建议写成已实施事实。通过文档职责分工、两文互链和明确状态词控制。

文档回退应只恢复本任务新增/修改的段落，不覆盖其他会话 dirty 内容；本轮不执行回退或文件删除。不重命名白皮书以保留入口。未知 CAF 全称、路径或实现状态如实写待核对，不编造。

发现需要新增可执行 schema、安装库、创建 CU/CA 工程、改 PLC/数据库、恢复 Redis/Celery、改角色/workflow、部署/推送或扩大文件范围时停止该部分，返回 PM 修订；不把文档任务转为实现任务。

## 8. 修订与批准历史

- `r1 draft`，2026-10-15：将 DAA/SMA/CA、SQLite 和共享流程讨论直接整理为 215 行 PM 设计正文；仅 spec 已形成，未创建 tasks/checklist，也未获得功能实现授权。该正文体裁由本 r2 替代，讨论结论按 R1–R8 交给 Development 整理到 docs。
- `r2 owner_approved`，2026-10-15：依据第 1 节 Human Owner 实际原话，将同一 ARCH-AW-002 限定为白皮书先行、详细原理设计随后、允许索引/ROADMAP 同步的文档任务；纳入 CAF/CU 和本次三个 Agent 讨论。编号由 PM 赋予，不伪称用户原话包含 r2，不批准任何代码或现场动作。

PM 仅写本 spec。`contract_only` 不构成平台 ACL 或强制路由；主会话、完整任务 bundle、当前工作树和 diff 审计仍是必要控制。
