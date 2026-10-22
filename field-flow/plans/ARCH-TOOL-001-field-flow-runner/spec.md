Task ID: ARCH-TOOL-001
Revision: r2
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: pending Human Owner review of r2 documentation baseline; software implementation scope not approved
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: Field Flow 独立现场流程运行程序的文档基线、长期运行边界及 CA 演进交接
Owner: Field Flow
Acceptance Chain Reference: 本 spec 的精确范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收

# Field Flow Runtime：讨论结论与后续实施基线

## 1. 本轮授权与状态

用户要求“先把 ff 这边讨论相关文档落实”，已创建根 `field-flow/`，要求 FF 后续 plan 和源码归此目录；
同时要求整理 CA 后续方向与 FF/CA 关系，交由用户复制到对应会话调整。
本轮授权是 PM 文档整理、归属迁移和交接提示词，不是尚未出现的精确 r2 软件实施批准。
当前保持 draft；Development、独立 QA、现场操作与部署均未开始，不创建 tasks.md/checklist.md 或源代码目录。
本 spec 是 FF 讨论结论的唯一范围权威；README/PLAN/catalog 只保留身份、导航、摘要与下一 gate。

r2 替代 r1 的 tools 放置、单工具混合工程、Rust 主/Python 对照、纯进程内状态与短时调试边界。
r1 全文以逐行前缀无损封存在文末，可精确还原原字节；只是历史，不提供当前实施或联网授权，Task ID 和 namespace 保持不变。
[项目契约](../../../AGENTS.md)、[根计划](../../../PLAN.zh-CN.md)与[canonical workflow](../../../.codex/workflows/development-lifecycle-workflow.md)继续适用。
本轮不修改 tools 规则，不建立联网例外，也不将长期现场程序套入离线工具合同。

## 2. 归属与独立实现

Field Flow Runtime 是独立的现场流程运行程序，可在 AW/Backend 尚未完整时按自己的范围迭代。
目标结构如下；本轮只落实 FF 根治理文档及本 spec，下面两个实现子目录为未来目标，不立即创建：

```text
field-flow/
├── README.md / README.zh-CN.md
├── PLAN.md / PLAN.zh-CN.md
├── plans/README.md / README.zh-CN.md
│   └── ARCH-TOOL-001-field-flow-runner/spec.md
├── field-flow-rust/                    # 未来独立 Rust 实现
│   ├── Cargo.toml / Cargo.lock / src/main.rs
│   ├── src/app/ / src/runtime/ / src/infrastructure/
│   ├── config/ / tests/ / 私有运行数据目录
│   └── README.md / README.zh-CN.md
└── field-flow-python/                  # 未来独立 Python 实现
    ├── pyproject.toml / uv.lock / src/
    ├── src/field_flow/app/ / runtime/ / infrastructure/
    ├── config/ / tests/ / 私有运行数据目录
    └── README.md / README.zh-CN.md
```

每个实现都拥有自身清单、锁、源码、配置示例、测试、依赖环境、状态库、日志与 README；
单独复制其中一个实现目录，也能按自己的文档安装、构建、启动和验证，不依赖兄弟实现或父目录清单/运行配置。
实施形成独立迭代任务时维护对应 README/PLAN/catalog，FF 总计划导航到唯一所属 bundle，不复制任务正文。
不跨目录 import 源码，不把测试 fixture 或依赖安装寄托在另一版本，不共享可写 SQLite。
两版只保持业务语义、flow 身份与验收场景对应，不要求逐文件、逐函数或内部技术方案镜像。

Rust 和 Python 都可能长期配合 Backend 承担现场运行；语言本身不构成生产资格或降级理由。
可以先在一个实现把最急需的一条链路做稳，再由另一实现跟进同一场景；实施顺序与首选版本待具体任务决定。
版本选择以同一运行验收为依据，不自动构成双活、热备或同时下发。

## 3. 手写 flow 的基本合同

### R01 身份、职责与数据

每个 app/demo 模块对应一个逻辑 flow，具有稳定 flow_id 与业务名称；两版对应流程使用相同业务身份。
入口保持薄：Rust main.rs 是进程入口，app.rs 仅可作为装配；Python 使用自身包入口，不复制混合工具布局。
runtime 负责调度、监督与生命周期；service 编排手写业务步骤；infrastructure 封装 S7、HTTP、本地状态与日志 IO。
通用层提供 typed 输入输出、质量/时效、错误分类、有限等待和执行状态，不代替业务解释条件。
正常值、缺失、坏 schema、通信错误与 stale 必须可区分；陈旧值和默认填充值不得触发现场动作。
每次动作保留 flow/事件/步骤身份、必要输入摘要和版本；日志不保存真实密钥或完整敏感 payload。

### R02 首批案例

1. demo01：轮询 GET，校验响应和业务条件，以来源 command_id/事件标识写入配置的 PLC DB 点位。
2. demo02：读取 PLC DB，条件满足或观测到 BOOL 上升沿后，以稳定事件身份 POST 当前有效业务值。

首批实现从以上有界案例开始，不以任意脚本执行、表达式语言或流程平台作为前置。
示例 GET 的 command_id/ready/value、点位和值均为 synthetic 合同，不代表第三方接口已有这些字段。
上升沿示例首个有效样本仅建立基线，初始 high 不发送；持续 high 不重复，回到 false 后再次 true 才产生新事件。
重启/断连后保护已有待投与 unknown；新采样先建立可靠基线，不推断不可见期间的边沿，不清状态重放。
轮询可能漏掉短脉冲，事件保持/计数器/握手由实际 PLC 合同解决，不以提高轮询频率承诺不丢事件。

外层 while 是 runtime 的循环调度；未来迁往 CA 时通常映射为定时触发加一次有界流程，图中不要求无限回环。
每条 flow 的业务步骤仍手写且可单独阅读，不提前设计 DSL、节点编译器或从代码反编译的通用平台。

### R03 配置、协议与副作用

各实现使用自己的显式配置与 synthetic 示例；连接、点位、轮询/时效/超时等参数与业务代码分开。
不导入 backend 应用、不读取其真实 .env，不默认扫描仓库地址或配置；凭据来自实现自身明确的安全配置。
候选技术为 Rust Tokio/reqwest/S7 adapter、Python asyncio/httpx/S7 adapter；精确依赖与锁由后续实施冻结。
现有 Rust 候选含 native C++ 构建要求；本轮不安装依赖，不将先前版本记录或 latest 文档当运行兼容证据。
首批 S7 能力建议限标准 DB 绝对地址 BOOL/INT/DINT/REAL，明确字节序、范围与质量；BOOL 真正按 bit 写，不做整字节改写。
实际 CPU/固件、通信权限与非优化 DB 条件待现场核对；本任务不修改 PLC 程序/安全设置，不承诺全西门子型号兼容。
拟采用显式启动、默认 dry-run、明确 execute 开关；无参仅帮助。这里只定义方向，不声称命令已存在或可运行。
真实目标上的 GET/read 也属于外部动作；软件开关不能替代 Human Owner 对具体目标与动作的授权。

## 4. 长期运行所需合同

### R04 flow 监督与连接

每条 flow 独立监督与故障隔离；同一 flow 不重叠迭代，不积压补跑轮询 tick，HTTP 等待不阻塞其他 flow。
同一 PLC 使用持久连接和串行 IO；同步 driver 由单 owner 专用工作线程处理，使用有界队列，不阻塞异步调度器。
连接、读写、HTTP、队列等待与退出都有有限预算；停止后未开始的请求不得继续下发。
读瞬时错误可进入 recovering，按有界退避重连并报告健康变化；持续错误按策略降级/告警/等待处理。
不机械沿用“三次读失败永久退出”为唯一现场策略；重试预算、升级条件、探测与暂停策略在实施 spec 冻结。
配置/schema/类型错误与瞬时网络错误分开；非法配置或陈旧输入必须阻止对应动作，其他独立 flow 可以继续。

### R05 本地 SQLite、进度与恢复

每个实现各有独立本地 SQLite，保存必要事件 ID、步骤进度、待投递、在途、已确认和 unknown 状态。
状态库只记录本地执行/投递事实，不接管 Backend 的业务数据真相；不让两版或多个实例直接共享可写库。
副作用前先持久化执行身份与必要意图，避免重启生成新身份再执行同一业务事件。
同一事件重复轮询应复用已有进度；进程重启先恢复/核对状态，不通过删除库、清集合或重置计数器来重放。
若 PLC 已确认且后续回报失败，只补报原事件，不回到 PLC 写步骤；有待核对步骤时不得宣称整个业务完成。
HTTP 补投/查询须按接收方幂等与确认合同沿用原身份；未明确支持时不能假设重试 POST 安全。
只读可恢复不代表副作用可重试；已发送写/POST 后超时、断连或无法证明未生效时进入 unknown。
unknown 保留必要上下文并暂停对应副作用，按既定接收方合同查询/握手或人工核对，禁止盲重发。
SQLite 能帮助避免本地重复执行，但不能原子提交外部 PLC/HTTP，也不能提供物理 exactly-once。
S7 protocol ack、PLC 逻辑接受/完成、HTTP 接收确认与最终业务完成分别记录；实际 PLC 握手仍需合同。
事务边界、DDL/schema 版本、崩溃恢复点、状态兼容与迁移方式由后续实施 spec 冻结；本轮不建库、不运行 schema。

### R06 可观测性、容量与托管

长期运行需要持续 JSON Lines 日志、轮转与保留策略；Rust 按 tracing 生态，Python 使用自身结构化日志实现。
最低记录版本/配置摘要、flow 健康、最近成功、连接变化、动作身份/结果、恢复、unknown、队列/磁盘告警和退出。
不得逐 tick 刷低价值读取，也不得输出 token、完整连接串/请求体、真实 PLC payload 或私有配置内容。
队列、待投递、状态库、日志与磁盘均设容量边界；到上限时保护关键状态、暂停新副作用并暴露降级状态。
不能为腾空间删除 unknown、未确认事件或破坏已确认进度；清理/归档规则保留恢复与追责依据。
状态持久化或必要审计失败时不得继续新下发；失败可见，不以“仍在跑”表示流程健康。
停机先停止新下发，处理在途状态，关闭客户端并实际 join 自有任务/线程后才报告退出完成。
托管方式、服务账号、启动/重启/升级/备份/日志盘及停机权限计划由现场 OS 与实施范围确定，不提前安装 service。
故障注入与必要长时验证是现场运行 gate，时长/负载/指标后续冻结；短时 smoke 不替代托管和长稳证据。

## 5. Backend、writer 与切换

### R07 Backend 边界

Backend 负责业务校验和业务数据，通过已稳定或另行确认的 API 与 FF 交付命令/事实/结果。
不在此虚构 API 路径、鉴权、schema 或接口已实现；第三方 HTTP 的合同也须单独确认。
FF 拥有现场连接、调度与执行证据，不依赖 backend 进程内轮询 PLC；本地持久化不替代上游业务状态。
本轮只记录责任边界；真实 API/PLC 操作与托管部署须具体实施范围、环境配置和明确授权。

### R08 一个有效 writer

同一 flow、PLC 写资源和 HTTP 业务效果同时只能有一个有效 writer；只读监控也不能暗中升级为写端。
Rust/Python/未来 CA 切换前：停止旧端新下发，核对 pending/in-flight/unknown，保留已确认进度，确认资源所有权。
随后明确事件身份与状态交接、兼容策略及必要迁移，核验旧端已释放后才启动新端；交接不能直接共享 SQLite。
本机锁只保护本机约定，不能证明跨实例/跨主机互斥；部署侧排他和现场切换证据需独立 gate。
不得因某端失联就自动启动另一 writer，不把双实现目录误写成热备方案。

## 6. FF 与未来 CA

FF 可独立长期维护，是手写流程、现场经验和可验证案例来源；不等待 CA，也不强制迁入 CA。
CA 后续承担节点编辑、编排和版本化执行；FF 本轮不引入 CA GUI、通用图引擎或 AI 执行依赖。
现在保留稳定 flow 身份、步骤顺序、输入输出、状态/错误语义和简明说明，作为未来人工对照或迁移依据。
代码中不支持的逻辑未来可保留为 custom 节点或待人工处理，不承诺任意 Rust/Python 无损转换。

CA AI 方向归“梳理 MES、SMA 与 CA 接口设计”会话 `01a15850-0076-7d13-90ba-0bdfd81a9556` 后续规划：
AI 可分析受支持单流代码或自然语言，形成 CA 节点/连线草稿；必须与原流真实行为对照，不自动取得执行权。
AI 与画布应编辑同一版本化草稿，基于最新 revision 提交增量 patch，支持差异审阅/撤销及本地合同校验。
拟校验节点、类型、引用、边、权限和预算；聊天不能修改当前运行版本，保存/选择启动遵循 CA 自身合同。
DeepSeek 可作为首个 provider 候选；AI 创作所需联网与既有本地执行分开，本地执行不以 AI 在线为前提。
凭据由本地 Rust/安全配置持有，不暴露前端，不默认上传真实配置/数据；AI 不直接获得 PLC/业务 HTTP 执行工具。
建议分期：本地节点库/手动基本流 -> AI 模板与对话共创 -> 受支持的单流代码迁移。
以上均为另一会话待细化的方向，不是当前已实现功能；本任务不改 AW-006/AW-007/ROADMAP、不发消息、不调用模型。

## 7. 本轮文档交付、候选实施范围与验收

### D01 本轮 PM 文档交付

迁移本 spec 到当前路径，移除旧有效 spec，完整封存 r1 原字节及 hash；不留下重复事实源或 stub。
由主协调器基于本 spec 机械建立 FF 根 README/PLAN/catalog 双语导航，并更新根 README/PLAN/catalog/CODE_INDEX 必要入口。
这些导航写入只表达本轮 PM 文档事实，不承载额外设计正文、批准结果、DEV/QA 证据或可用命令。
PM 仅写迁移前后 spec 路径；当前不创建两个实现子目录、依赖清单、测试、数据库、服务或其他实施文档。

### D02 未来候选 allowlist 与阶段

未来软件候选范围限 `field-flow/**`，根目录只做必要导航；精确文件、接口、依赖、技术值和风险由实施 spec 再冻结。
根 AGENTS/ROADMAP、AW/DAA/DS/SMA/CA、backend 源码、现有 tools、真实配置/密钥/数据均不在 FF 候选实现范围。
本轮先交可审阅文档；之后先取得精确实施 Revision 批准，再由 Development 计划/实现、自检和 handoff。
fresh-context Verification 在真实 handoff 后独立验证；Human Owner 保留范围/风险决定及最终验收，不能倒填后续 gate。
需要的 skill：aiis/project-governance 负责边界与治理，rust-runtime 负责长期运行与本地 IO，plc-point-mapping 负责点位合同；
后续状态模型/schema 按实际范围路由 backend-arch 等适用规范，源码头/索引和人类文案分别遵循 code-document-indexer/i18n-workflow。
不因“runtime/worker”用词引入 Celery、Redis、GUI 或不相关模板；不再套 project-tooling 的混合工程/离线工具规则。

| 文档项 | 本轮可审阅标准 |
| --- | --- |
| DOC01 | 根 field-flow 归属、两独立实现目标与当前未建源码的事实清楚，链接仅指向存在文档。 |
| DOC02 | 任一语言可长期维护，先后实施与 writer 排他、状态交接边界明确。 |
| DOC03 | 手写 flow、Backend、持久状态、恢复/unknown、容量/日志/退出合同完整，精确实施值仍待冻结。 |
| DOC04 | FF/CA 独立关系、AI 未来方向与可复制提示词齐备，不越权修改或联系另一会话。 |
| DOC05 | r1 能按 hash 逐字节还原；当前唯一 Task ID/namespace/r2 draft，无 tasks/checklist 或虚构实施/QA。 |

以下是未来实现验收建议，不表示本轮已执行或成为已批准实施清单：

| 场景 | 后续验证应证明 |
| --- | --- |
| RUN01 独立交付 | 各自单独复制后可安装/构建/启动/验证，锁/配置/状态/fixture 无兄弟目录依赖。 |
| RUN02 双例闭环 | 同场景真实本地 S7+HTTP 协议闭环、类型/位写邻位、单流/并发与 dry-run 语义一致。 |
| RUN03 隔离/恢复 | 某 flow 或目标故障不拖死独立 flow，读错误恢复、坏 schema/stale 拒绝、重连预算有证据。 |
| RUN04 崩溃/unknown | 副作用前后各崩溃点可恢复原身份，响应丢失不重复 PLC 写，不以重启清状态。 |
| RUN05 补投/容量 | 回报只补报、按合同沿原身份投递，积压/磁盘满时保护 pending/unknown 并可恢复。 |
| RUN06 切换/退出 | writer 停交接/状态兼容、旧端资源实际释放、跨实例排他及真实 join 有可观察证据。 |
| RUN07 托管/长时 | 在明确 OS、时长、负载、指标下验证日志轮转、健康、恢复、资源趋势和必要现场兼容。 |

本地协议夹具、构建和短时测试不能代表实机工艺/物理完成、第三方兼容、托管部署或长期运行验收。
固定端口、fixture 实现、精确命令、DDL、依赖 patch、超时/队列/磁盘/保留数值与长时时长由后续 spec 冻结。

## 8. 风险、待定项与回退

现场 OS/架构、PLC 型号/固件/DB/握手、HTTP schema/鉴权/幂等/确认、Backend 稳定 API 均待确认，不阻塞本轮文档。
Rust/Python 首条链路顺序、状态交接格式、接收方可核实能力、托管账号与容量阈值须在实施范围中决策。
不能用本地 SQLite、S7 ack 或 HTTP 2xx 推断物理 exactly-once；未知结果、安全互锁与现场停机权始终保留。
本轮回退只针对本次导航/spec 差异，r1 从本文件历史可恢复；不回退任务外 dirty、不删除真实状态或外部动作。
未来升级回退需先核对状态 schema/未确认事件兼容，停止新下发；不能仅换二进制或重新建库来“恢复”。

<a id="ca-handoff-prompt"></a>

## 9. 可复制到 CA 会话的提示词

下面只供 Human Owner 手工复制，本会话不自动发送：

```text
请在“梳理 MES、SMA 与 CA 接口设计”会话中，先按本会话自身 workflow 读取当前 AGENTS、README/PLAN、相关完整任务 bundle，整理 CA 后续设计规格和路线修订建议，暂不开始代码、真实 API/PLC 操作、依赖安装或模型调用。

FF 已确定在仓库根 field-flow/ 独立演进，未来 field-flow-rust/ 与 field-flow-python/ 各自可独立复制、构建、启动和维护，可长期配合 Backend。当前只落实 PM 文档基线，软件实施尚未批准。FF 不等待 CA/AI，不强制迁到 CA，请不要回写 FF 文档或代码。

请保留 ARCH-AW-006 r2、ARCH-AW-007 r2 及完整历史批准/DEV/独立验证事实；把以下内容作为后续方向，按自身范围决定新 Revision 或任务，先给出可审阅规格与路线建议，不把原 r2 的文档验收写成软件实现证据，也不擅自扩大旧批准。

1. FF 是手写流程和可验证案例来源；每个 app/demo 是一个稳定 flow_id 的逻辑流，runtime 的外层 while 对应未来 CA 定时触发加一次有界流程，不要求图中无限回环。首例 HTTP GET -> 条件 -> S7 写；次例 S7 读 -> 条件/上升沿 -> HTTP POST。迁移保留步骤、typed 输入输出、质量/时效、幂等/确认、错误和 unknown 语义。
2. CA 可分析受支持的 Rust/Python 单流或自然语言，生成节点与连线草稿；不支持的逻辑明确标成 custom 节点或待人工处理，必须与原流真实行为对照，不承诺任意代码无损转换。
3. 可以考虑 DeepSeek 作为首个 AI provider。AI 与画布共同编辑同一份版本化草稿，始终基于最新 revision 做增量 patch；要有差异审阅、撤销与并发修改冲突处理，不用聊天文字覆盖整份流程或当前运行版本。
4. 草稿必须在本地校验节点、类型、引用、边、权限、预算及运行合同。AI 只提供创作建议，不直接获得 PLC 或业务 HTTP 执行工具；保存、版本化、选择启动沿 CA 自身合同，聊天修改不能即时改变现场运行。
5. AI 创作可以联网，已有本地执行应独立于 AI 服务可用性。凭据留在本地 Rust/安全配置，不暴露前端，不默认上传真实配置/数据；模型输入范围、脱敏、审阅和 provider 错误路径需明确。
6. FF 与 CA 对同一 flow/PLC 写资源/HTTP 业务效果只能有一个有效 writer。迁移/切换先停新下发、核对 pending/in-flight/unknown、保留已确认进度并明确状态交接/兼容；不直接共享 FF 的可写 SQLite，本机锁不代表跨实例互斥。
7. 建议分期：先稳定本地节点库与手动基本流，再做 AI 模板/对话共创，最后做受支持的单流代码迁移。请明确各期需求、排除项、验收、风险及所需批准，保持 FF 现场链路可以独立推进。

请先返回建议修改的文档/任务归属、分期范围和需要确认的事项；按你当前 workflow 获得所需精确批准后再落实对应文档，不自动启动实现或真实接口操作。
```

## 10. 修订与 PM 自检

| 日期 | Revision | 真实记录 |
| --- | --- | --- |
| 2026-10-21 | r1 | 原根 plans 下 PM draft；范围批准 pending，无代码实施；完整原文封存于下。 |
| 2026-10-21 | r2 | 按用户本轮文档整理/根 field-flow 归属/CA 提示词要求修订；软件实施批准 pending，DEV/QA 未开始。 |

PM 文档自检：2026-10-21，Python 文档断言 exit 0；身份字段按全文件行首匹配均唯一，3 个当前本地链接、两个锚点与 DOC01–DOC05 一致。
r1 每行统一 `r1|` 前缀（含空行），去前缀还原 18,137 字节，与原始备份逐字节相同且 SHA256 不变；旧 spec 已移除，未创建源码子目录或后续角色文件。
本轮仅调整归档编码和提取说明，保持 r2 draft 与原范围；未运行实现检查，不作为独立 QA。

协调器导航检查（2026-10-21）：7 份 FF Markdown 的 44 个本地链接（含根新增入口）及锚点均解析，3 对双语导航结构/任务状态一致。
根 7 份导航的 `git diff --check` exit 0；与会前快照比较，根差异仅为 FF 入口，AGENTS、ROADMAP 双语、AW-006 r2、AW-007 r2 和 AW Runtime Design 的 hash 不变。
r1 恢复仍为 18,137 字节且 SHA256 一致；旧空目录已移除，未创建 source、tasks.md 或 checklist.md。
实际治理命令 `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch field-flow` exit 1：会前与会后均为完全相同的 310 行诊断，FF 诊断为 0，不能标为全仓治理通过。
以上是协调器/PM 文档自检记录，不是独立 Verification，也不是软件、现场或长期运行验证。

<a id="r1-history"></a>

## 11. r1 完整历史（逐行前缀无损封存）

原路径：`plans/ARCH-TOOL-001-field-flow-runner/spec.md`。
原 SHA256：`71db7a41f089d0f7f5147a198b873a3eedd3a076ee96a666cf36f7ba6d0f6b0a`。
下方四反引号 fenced block 内每一行（包括历史空行）均增加 `r1|` 前缀，以避免旧元数据被检查器识别为当前字段。
还原时仅去掉每行开头恰好一个 `r1|`，原样保留其余 UTF-8 字节与换行（包括原末尾换行）；还原结果应为 18,137 字节并匹配上述 SHA256。
前缀是归档编码，不属于原文；历史相对链接不按新位置解释。
历史中的 tools、短时调试、纯内存状态、未来命令及角色记录都只属于 r1，不覆盖当前 r2。

<!-- BEGIN R1 ORIGINAL BYTES -->
````markdown
r1|Task ID: ARCH-TOOL-001
r1|Revision: r1
r1|Status: draft
r1|Owner Role: PM
r1|Allowed Writers: PM, Human Owner
r1|Handoff: pending Human Owner scope approval of ARCH-TOOL-001 r1
r1|Workflow Mode: STD
r1|Execution Mode: agent_team_same_session
r1|Task Namespace: aiis-ics-arch
r1|Classification: root
r1|Capability: 独立前台现场调试工具，Rust 主实现与 Python 对照，实现并发手写 HTTP/S7 循环流
r1|Owner: Human Owner（项目级现场调试工具）
r1|Acceptance Chain Reference: 本 spec 的范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
r1|
r1|# 现场手写流程调试工具
r1|
r1|## 1. 目标与当前事实
r1|
r1|在 AW、Backend 尚未完整时，先交付可复制、可构建、可启动的独立 CLI，供学习 Rust 和人工现场调试。
r1|两版保持相同示例语义：HTTP GET 判断后写 PLC DB；PLC DB 读取判断后 HTTP POST。
r1|业务条件保留在手写 demo 中，公共层封装连接、类型转换、调度、退出与错误；不建立通用流程平台。
r1|
r1|当前 [tools README](../../tools/README.zh-CN.md) 与 [tools PLAN](../../tools/PLAN.zh-CN.md) 明确禁止网络访问。
r1|本 r1 提议只为 `tools/field-flow/` 增加受控联网例外：人工显式启动、前台运行、显式配置 PLC/HTTP 目标。
r1|实施时同步 tools 双语规则，其余工具继续离线。本 draft 不代表例外已获批准，也不授权连接真实目标。
r1|生产常驻采集和控制仍归 AW；本工具不注册到 DAA/SMA/CA，不消费 Backend 命令合同。
r1|
r1|| 已读源码 / 配置 | 可参考的事实与限制 |
r1|| --- | --- |
r1|| [managed_s7.rs](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/managed_s7.rs) | 持久 S7 会话、单 owner、显式 RemotePort / 超时；主要接口为 connect/read/read_bounded/disconnect，没有本工具所需写入接口。只参考模式，不导入 DAA/Tauri。 |
r1|| [rust_snap7_adapter.rs](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/rust_snap7_adapter.rs) | 旧读适配器在调用内连接、读取、断开；不直接复制为循环流的短会话默认。 |
r1|| [DAA Cargo.toml](../../automation-world/data-acquisition-agent/src-tauri/Cargo.toml)、[tools uv.lock](../../tools/uv.lock) | 现有 Rust 候选为 rust-snap7 1.142.2；tools 当前 Python 锁为 python-snap7 3.0.0。本任务建立独立依赖和锁，不修改这些文件。 |
r1|
r1|## 2. 范围与需求
r1|
r1|### R01 工程结构与职责
r1|
r1|建议使用一个工具根，保留语言原生入口；不机械建立 `rust-version/python-version` 两套治理外壳：
r1|
r1|```text
r1|tools/field-flow/
r1|├── Cargo.toml / Cargo.lock             # [[bin]] 指向 src-rust/main.rs
r1|├── pyproject.toml / uv.lock / main.py   # Python 薄入口
r1|├── README.md / README.zh-CN.md
r1|├── PLAN.md / PLAN.zh-CN.md / plans/README.*
r1|├── examples/                           # 公开 synthetic YAML 与说明
r1|├── inputs/ / outputs/                  # 本工具私有输入、可丢弃输出
r1|├── src-rust/
r1|│   ├── main.rs / commands.rs / runtime.rs
r1|│   ├── config.rs / domain.rs / logging.rs
r1|│   ├── app/mod.rs / app/demo01.rs / app/demo02.rs
r1|│   └── infrastructure/mod.rs / plc.rs / http.rs
r1|├── src-python/field_flow/              # 对应职责，使用 Python 包结构
r1|│   ├── cli.py / runtime.py / config.py / domain.py / logging.py
r1|│   ├── app/demo01.py / app/demo02.py
r1|│   └── infrastructure/plc.py / http.py
r1|└── tests/                              # 必要测试和专用本地协议 fixture
r1|```
r1|
r1|`main.rs/main.py` 只做入口与装配；`app.rs` 仅在需要时作为装配文件，不替代 Rust 二进制入口。
r1|`app/demo*` 是 application service，表达一次迭代的读取、条件和动作；runtime 持有循环与生命周期。
r1|infrastructure 隔离 S7/HTTP；config/domain 保留必要类型与状态。不建含义混杂的万能 core，不预造插件层。
r1|
r1|### R02 技术栈和依赖隔离
r1|
r1|- Rust：Tokio、reqwest、rust-snap7；候选 rust-snap7 1.142.2，由 Development 在新 Cargo.lock 锁定并真实构建。
r1|- Python：asyncio、httpx、python-snap7 3.x，必要 YAML 解析依赖；通过本工具 pyproject/uv.lock 和独立 `.venv` 管理。
r1|- 精确 patch、Python/Rust/OS/架构和锁校验结果由 Development 记录；不能把 latest 文档 URL 当版本冻结证据。
r1|- Rust 候选 crate 随包编译 native C++，首次构建需要匹配的 C++ 工具链。Python 3.x 为协议纯 Python 实现；不假定两者 ABI 或行为相同。
r1|- 不修改 backend、tools 现有依赖，不依赖 DAA、DS、Tauri、数据库、Docker 或运行中的服务；HTTP client 复用连接池。
r1|
r1|### R03 小份显式配置
r1|
r1|使用必填 `--config <YAML>`，不自动发现或读取仓库 / backend `.env`。
r1|YAML 只表达连接、点位、轮询和超时参数；业务判断留在 demo，不设计表达式语言。
r1|最小字段覆盖 PLC id/host/port/rack/slot/connect_timeout_ms/io_timeout_ms，HTTP GET/POST URL、HTTP 超时、可选 token_env，
r1|点位 id/db_number/byte_offset/type/BOOL bit，以及每 flow 的 interval_ms。解析为 typed config，缺失或非法值启动前报错。
r1|HTTP 密钥只从 `token_env` 指定的环境变量读取；公开示例只放 loopback、synthetic 点位与占位符，不含真实地址或凭据。
r1|两个版本读取同一配置形状。`examples/loopback.yaml` 明确配置本地测试端口；现场配置由人工审核后放入 inputs 或显式外部路径。
r1|inputs/outputs、日志、`.env*` 实值、`.venv`、target/cache 忽略；保留必要空目录占位和公开示例。
r1|
r1|### R04 并发、PLC owner 和退出
r1|
r1|- 每条 flow 一个异步任务；同一 flow 的一次迭代完成后等待配置间隔，不重叠、不补跑堆积 tick；HTTP 等待不阻塞其他 flow。
r1|- 每个 PLC 由一条专用工作线程独占一个同步 S7 client；Rust 与 Python 均用有界请求队列串行操作，异步调用方等待结果。
r1|- HTTP 请求和业务判断不占 PLC 队列 / 会话锁；同步 S7 调用不得直接阻塞 Tokio/asyncio 调度线程。
r1|- 连接、发送、接收、队列等待均有有限超时；取消或队列期限到期的未开始请求不得再下发。
r1|- Ctrl-C 停止接收工作、取消等待、丢弃未执行请求，等待在途调用按 socket 超时返回，再 disconnect、关闭 HTTP client、join 工作线程。
r1|- 不把 abort/cancel 或停止等待当线程已释放。退出摘要仅在线程、任务和自有连接真正结束后记录；失败 flow 停止，其他 flow 可继续，最终退出码反映失败。
r1|- 启动前按 PLC endpoint、DB 和位范围拒绝多个已选 flow 的重叠写区；不引入优先级、锁表或复杂仲裁。
r1|
r1|### R05 有限 S7 点位能力
r1|
r1|首版支持标准 DB 绝对地址的 BOOL、INT、DINT、REAL；INT/DINT 为有符号大端，REAL 为大端 IEEE754 f32，拒绝越界值与非有限浮点。
r1|BOOL 的 bit 为 0..7；写入必须走真正的 S7 bit 访问，禁止读整字节再改写整字节，以免覆盖邻位。
r1|点位类型、地址和长度在 IO 前验证；不开放任意内存、I/Q/M、CPU 启停、下载、密码修改、TIA/XLSX/UDT 导入。
r1|西门子具体 CPU/固件尚未确定，不承诺所有型号可用。1200/1500 须核对 PUT/GET 与非优化通信 DB 等实际条件；
r1|修改 PLC 工程或安全设置不属于本任务授权。S7 write 成功只代表协议确认，不代表 PLC 程序接受或物理动作完成。
r1|
r1|### R06 demo01：HTTP GET -> 条件 -> PLC 写入
r1|
r1|示例 GET 返回 `{"command_id":"cmd-001","ready":true,"value":42}`；ready 为 true、标识非空且 value 符合目标点位类型时才尝试写入。
r1|每进程记录已处理 / 已尝试 command_id，同一事件不因每次 GET 仍满足条件而反复写；dry-run 也只记录一次 would_write。
r1|使用有界内存集合，达到上限时停止该 flow 并提示人工处理，不能静默淘汰后重新执行旧事件。
r1|写入明确成功、明确失败或 unknown 均有事件结果；写失败后不在下一 tick 自动重发相同事件。
r1|进程重启后集合不保留，可能再次遇到旧事件；不承诺跨重启 exactly-once，重启执行前须人工确认上游未完成命令。
r1|
r1|### R07 demo02：PLC 读取 -> 上升沿 -> HTTP POST
r1|
r1|读取配置的 BOOL 触发点和一个示例值点；仅观测到 false -> true 时 POST 该次读取的示例值及 event_id。
r1|进程启动首次成功采样只建立基线，初始 true 不 POST；持续 true 不重复 POST，回到 false 后再次 true 才产生新事件。
r1|读失败期间不使用旧值触发，重连后首个成功样本重新建立基线，不能推断离线期间的边沿。
r1|HTTP 2xx 及示例响应确认仅表示对方响应成功；不写回 PLC 确认位，不推断第三方业务完成。
r1|不保留跨重启事件，也不补发进程停止 / 采样间隔内错过的脉冲。
r1|
r1|### R08 默认 dry-run 与错误语义
r1|
r1|显式 `run` 默认允许配置目标上的 GET/S7 read，但不执行 PLC write 或 HTTP POST，只记录 would_write/would_post。
r1|只有同一命令增加 `--execute` 才启用副作用；不能在循环中自动切换模式，不增加模拟审批 token 或自动审批机制。
r1|GET/只读 S7 的瞬时失败可有限重试 / 重连：每次读取最多 3 次总尝试，有限指数退避，仍失败则停止该 flow。
r1|非法配置、类型、HTTP schema 或 S7 点位拒绝不无限重连；不能以陈旧缓存继续动作。
r1|PLC write/POST 一旦已下发，遇到超时、断连或无法证实未生效的失败，标记 `unknown` 并停止对应 flow，等待人工核对。
r1|不得被通用重试器、下一 tick、自动重连或 client 内置重试再次下发；明确业务拒绝记 failed，也不自动重发。
r1|人工核对后才能显式重启；README 说明进程内去重边界及未知结果恢复步骤，不宣称持久命令系统。
r1|
r1|### R09 日志、文档与学习路径
r1|
r1|两版运行证据输出 JSON Lines，Rust 使用 tracing；包含 event、run_id、flow_id、target_id、event_id、result、duration_ms 和安全错误码。
r1|记录启动/配置摘要、连接变化、动作 start/result、dry-run、retry、unknown、flow 停止和 shutdown；不逐 tick 刷普通读取日志。
r1|不记录 token、Authorization、完整 URL query、完整 HTTP body 或原始 PLC payload；副作用审计输出失败时停止后续下发。
r1|需要保存时显式 `--log-file`，默认不创建持久文件；输出及日志不得成为公开现场数据。
r1|README pair 给出安装 / 构建 / 单流 / 双流 / dry-run / execute / Ctrl-C 命令、结果摘要，以及“复制 demo -> 修改一次迭代 -> 注册”的最短教程。
r1|CLI 人类文案按 i18n-workflow 保持中英文对称，日志状态 key 稳定；不引入 UI。
r1|工具 PLAN 与 catalogs 只引用根目录本任务唯一 bundle，不复制 spec/tasks/checklist 或建立第二事实源。
r1|
r1|## 3. 拟交付命令与本地验收
r1|
r1|以下命令是待实现合同，当前尚不存在程序；从 `tools/field-flow/` 执行。
r1|
r1|```bash
r1|cargo build --locked
r1|uv sync --locked
r1|cargo run --locked --
r1|uv run --locked python main.py
r1|cargo run --locked -- run --config examples/loopback.yaml --flow demo01
r1|uv run --locked python main.py run --config examples/loopback.yaml --flow demo01
r1|cargo run --locked -- run --config examples/loopback.yaml --flow demo01 --flow demo02 --execute
r1|uv run --locked python main.py run --config examples/loopback.yaml --flow demo01 --flow demo02 --execute
r1|uv run --locked python main.py fixture --config examples/loopback.yaml
r1|```
r1|
r1|README 还须给 demo02 单独运行与双 flow dry-run 命令。无参仅 help/exit 0；错误子命令非零，不读取配置、不联网、不写文件。
r1|fixture 是测试专用 synthetic S7 server + HTTP GET/POST server，可复用 python-snap7 Server，必须发出真实 loopback 协议请求。
r1|固定监听 `127.0.0.1:31102`（S7）和 `127.0.0.1:31880`（HTTP）；启动前检查，冲突报错退出，不杀占用者、不自动换端口、不绑定 wildcard/102。
r1|Rust/Python 依次连接同一形状的 fresh fixture，重置 synthetic 状态后比较计数和结果；不依赖尚在开发的 DS。
r1|
r1|| AC | 验收标准 / 对应需求 |
r1|| --- | --- |
r1|| AC01 | 本工具可单独复制；依赖锁完整，Rust/Python 在记录的本机 OS/架构真实构建/安装和启动，无 backend/AW/其他 tools 依赖污染。（R01–R03） |
r1|| AC02 | 两版无参/help exit 0 且无 IO；错误子命令、无效配置、类型越界非零；同一 synthetic YAML 可用，真实配置与密钥不提交。（R03/R05/R09） |
r1|| AC03 | 两版 demo01 本地 GET -> S7 write -> 独立协议读回成立；相同 command_id 多次轮询仅一次写，不同 id 可再次写。（R05/R06） |
r1|| AC04 | 两版 demo02 初始 high 不 POST；false -> true POST 一次，持续 high 不重复，第二个边沿再次 POST；HTTP 端记录实际请求。（R07） |
r1|| AC05 | 每版两个 flow 同时运行；延迟 HTTP 响应时另一 flow 仍前进，同 flow 最大在途迭代为 1，共享 PLC client 操作串行，无重叠写区获准启动。（R04） |
r1|| AC06 | dry-run 有真实读取但 PLC/HTTP 服务端副作用计数为 0；显式 execute 才产生 write/POST，日志可解析且脱敏。（R08/R09） |
r1|| AC07 | BOOL 真正按位写且不伤邻位；INT/DINT/REAL 编解码与边界正确；不以 byte read-modify-write 替代。（R05） |
r1|| AC08 | 读失败有限退避/恢复，不拿陈旧值触发；注入“已应用写/POST 但响应丢失”，得到 unknown、停止该 flow、服务端只收到一次动作。（R06–R08） |
r1|| AC09 | Ctrl-C 时停止新动作、join 在途线程并关闭连接；fixture/server/端口实际释放，端口冲突不干扰占用者。（R04） |
r1|| AC10 | README/PLAN/catalog pairs、源码头和 CODE_INDEX 与实际入口一致；Development 提供真实命令/退出码/版本/证据和资源清单，fresh Verification 独立复核。（R01/R02/R09） |
r1|
r1|只增加证明上述行为所需的少量单元与协议测试；不要求长稳、压力、全型号、全 OS 或生产验证。
r1|Development 至少记录 cargo fmt/check/build/test、uv lock 检查、Python 测试及两条本地协议闭环；QA 独立执行范围匹配检查。
r1|本地 fixture 通过不等于实机 / 第三方兼容、现场工艺安全或生产可用；相关项保持未验证。
r1|
r1|## 4. 写入 allowlist、排除项与交接
r1|
r1|- 实现面仅 `tools/field-flow/**`；`tools/README.*`、`tools/PLAN.*` 仅增加本工具例外、索引和状态。
r1|- 必要时新增 `tools/plans/README.md`、`tools/plans/README.zh-CN.md`；只引用根唯一 bundle，保留其他工具事实。
r1|- 根 `PLAN.md/PLAN.zh-CN.md`、`plans/README.md/plans/README.zh-CN.md`、`CODE_INDEX.md`、`.gitignore` 仅本任务机械索引 / 精确忽略。
r1|- 本 bundle：PM 只写本 spec；批准后 Development 才创建 tasks.md；developer_handoff 后 fresh Verification 才创建 checklist.md，必要 evidence 归本任务。
r1|- 根 README/AGENTS/ROADMAP、backend、frontend-js、现有 tools 依赖、AW/DAA/DS/SMA/CA 源码和配置全部排除；保留现有 dirty 改动。
r1|- 排除流程图引擎、插件平台、GUI、DB/Redis/Worker、服务化、打包发布、Git 推送、部署、自动恢复持久队列、真实设备及第三方请求。
r1|
r1|Development 必须使用 project-tooling、rust-runtime、plc-point-mapping；治理文档使用 project-governance，源码头/索引使用 code-document-indexer，CLI 文案使用 i18n-workflow。
r1|不得因点位 skill 扩大为 XLSX/TIA 导入、因异步循环引入 Celery，或加载无关桌面/前后端实现方案。
r1|批准精确 r1 后 Development 创建计划并实现；记录精确工作树/diff、锁/环境、DEV self-check、未验现场项及临时资源。
r1|fresh-context Verification 读取完整有效 bundle 与实现/diff，独立记录 AC verdict；Human Owner 保留最终验收。
r1|
r1|## 5. 风险、回退与待确定项
r1|
r1|现场网络条件、CPU/固件/DB 布局、HTTP 鉴权/schema/幂等合同与实际 OS 尚未确认，不阻塞泛化工具的本地实现。
r1|真正现场接入前由 Human Owner 提供并审核这些配置，明确目标、读写点位和动作授权；本任务不改 PLC 设置。
r1|轮询会漏掉短脉冲，读间隔内值可能变化，进程内去重不能提供跨重启 exactly-once；实际互锁/握手需独立范围。
r1|native C++ 构建与协议库存在平台差异；先记录本机可运行证据，其他目标平台单独验证。
r1|停止工具即停止新下发；已成功或 unknown 的外部动作不能自动回滚，人工核对；本地源码回退仅针对本任务 diff，不触碰其他改动。
r1|fixture 资源按任务归属退出和回收；必要证据进入 tasks/checklist 摘要及任务 evidence，不能只留临时目录。
r1|
r1|## 6. 参考与批准记录
r1|
r1|官方参考仅用于接口与约束判断，依赖以新锁和真实构建记录为准：
r1|[rust-snap7 client](https://docs.rs/rust-snap7/latest/rust_snap7/struct.S7Client.html)、
r1|[Tokio 阻塞工作与专用线程](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html)、
r1|[reqwest client 复用](https://docs.rs/reqwest/latest/reqwest/struct.Client.html)、
r1|[python-snap7 3.x 安装](https://python-snap7.readthedocs.io/en/latest/installation.html)、
r1|[Python client API](https://python-snap7.readthedocs.io/en/latest/API/client.html)、
r1|[Siemens PUT/GET 与通信 DB 示例](https://cache.industry.siemens.com/dl/files/115/82212115/att_1039292/v2/82212115_S7_communication_S7-1500_S7-1200_en.pdf)。
r1|
r1|| 日期 | Revision | 记录 |
r1|| --- | --- | --- |
r1|| 2026-10-21 | r1 | PM draft；Human Owner 范围批准 pending。未安装依赖、实现代码、启动 fixture 或连接设备。 |
r1|
r1|PM 文档自检：2026-10-21，Python 只读断言 exit 0，身份元数据、6 个本地链接、AC01–AC10、空白与 staged 文件归属一致；当前仅有 spec.md。
r1|未运行实现检查；本记录不作为 Development self-check、独立 QA 或最终验收。
````
<!-- END R1 ORIGINAL BYTES -->
