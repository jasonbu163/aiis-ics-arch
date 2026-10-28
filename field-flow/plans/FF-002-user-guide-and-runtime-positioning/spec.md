Task ID: FF-002
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved exact FF-002 r1 on 2026-10-23; handoff to Development within the approved documentation and bounded rehearsal scope; fresh Verification follows developer_handoff; no implementation completion, QA verdict or final acceptance asserted
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: Field Flow 双语使用与案例开发手册、Rust 目标平台构建说明及两语言后续定位
Owner: Field Flow
Acceptance Chain Reference: FF-002 r1 范围批准 -> Development 文档交付与必要演练 -> fresh-context QA / Verification -> Human Owner 最终验收
Related Task: FF-001, ARCH-TOOL-001

# FF-002：使用手册、案例开发教程与运行时定位

## 1. 当前阶段与目标

**当前为 FF-002 r1 owner_approved。** Human Owner 于 2026-10-23（Asia/Shanghai）明确批准：“批准 FF-002 r1，按方案完成 Python/Rust 对照使用手册、案例开发教程和 Rust BUILD 说明，完成后按 STD 进入独立 QA。”批准对象为原审阅 draft SHA256=`2cb1e14ea24b8ea1cf13b8c23bda39481d320638e46dddebad3f5949f15503a9` 的精确 r1，主协调器转交原文，PM 已核对原稿指纹。现交接实际命名 Development 在本 r1 原范围内实施；本次只记录范围批准，不代表实施完成、自检通过、独立 QA 或 Human Owner 最终验收，不扩大任何外部动作权限。

以下两段保留起草阶段原文，其中“当前”“尚不是范围批准”等仅描述批准前时点，不覆盖上述当前 gate：

当前仅为 **FF-002 r1 draft**。Human Owner 要求解释 FF 自有测试夹具及现在的使用方式，并交付 Python / Rust 对照使用手册，详细说明在 app 内新增案例、注册接线、代码运行、可用方法及用法，以及 Rust 按目标系统构建可执行文件。后续定位为：Python 用于熟悉语言、练手与快速原型，本任务不做 Python 打包；Rust 是长期部署 runtime 的建设主线。这个请求授权本轮整理可审阅规格，尚不是对本文件精确 Revision 的范围批准。

本任务交付正式文档，不新增 runtime 能力。批准后由 Development 写手册并做范围匹配的步骤核对及有限本机演练，真实 `developer_handoff` 后另启 fresh-context Verification，再交 Human Owner 最终验收。当前不创建 `tasks.md`、`checklist.md`、实现、测试、配置或构建产物，不安装依赖、编译/运行工程、初始化状态库或启动监听器。

[FF-001 r4 spec](../FF-001-dual-runtime-demo01/spec.md)、[Development](../FF-001-dual-runtime-demo01/tasks.md)及[QA2](../FF-001-dual-runtime-demo01/checklist.md)是既有双语言 demo01 本地闭环的独立事实源；当前 QA2 为 `qa_passed`，Human Owner 最终验收仍 pending。它的批准、失败历史、QA、候选与资源不转移为 FF-002 的批准或验证。本任务为独立 `root`，无 Parent Task ID；[ARCH-TOOL-001 r2](../ARCH-TOOL-001-field-flow-runner/spec.md)及全部旧 Revision 原样保留。

起草前已核对 FF / 根任务索引，未发现 FF-002 实际 bundle。先前聊天建议过的“FF-002 DS 联调”未创建、未批准，不构成占用或实施事实；本文件是 FF-002 的唯一范围入口，后续 DS 联调须另取未用编号并独立批准。

## 2. 已核对的当前事实

下表是文档范围的输入，不是本任务的新运行验证；交付手册时仍须按当前正式源码逐项复核。

| 表面 | 当前事实与应保留的边界 |
| --- | --- |
| 两个工程 | Rust 位于 `field-flow/field-flow-rust/`，Python 位于 `field-flow/field-flow-python/`；各有自己的清单、锁、源码、配置、locale、测试/夹具及私有状态。任一工程应能单独复制使用，父/兄弟目录的任务链接只是可选文档导航。 |
| 现有业务入口 | Rust `src/app/demo01.rs::iteration`；Python `src/field_flow/app/demo01.py::once`。两版配置只接受 `kind=demo01`，runtime 直接调用该模块；没有自动发现 app 或通用注册器。Python 现有函数未写完整类型注解，手册应解释实际对象合同，不能伪称已有强类型公共 SDK。 |
| 能力 | 当前业务例是有界 HTTP GET -> 严格命令/时间校验 -> 执行服务 -> 标准 DB 两字节有符号 INT 写入。运行时有独立 INT 读取能力，用户配置未注册通用读流或 demo02；POST、BOOL、DINT、REAL、鉴权等不能列成已实现方法。 |
| 调度 | 不同 flow 并发；同一 flow 一轮完成再等待 interval，不重叠、不追赶历史 tick。每 PLC 一个 FIFO owner 及常驻 driver 子进程/session 串行 IO，HTTP/定时等待不占 PLC 队列。多流读同点是独立采样，不是共同快照。 |
| Rust 人工夹具 | `ff-fixture --config ... --evidence-dir <新目录>` 来自 `test-fixture` feature；内置本工程 HTTP、透明 S7 proxy、native S7 server。当前入口固定一条 `cmd-001` / 值 42，按 ENTER 正常关闭，输出 `protocol.json`。 |
| Python 人工夹具 | `python -m tests.fixtures --config ... --evidence-dir <新目录>` 启动本语言三项服务；生成一条新固定命令身份 / 值 42，按 SIGINT/SIGTERM 正常关闭，输出 `report.json`。其 source 取首条 flow，不能推断为多 feed 可交互服务。 |
| 固定端口 | Rust：127.0.0.1 的 proxy 31102、server 31103、HTTP 31880；Python：32102、32103、32880。端口冲突失败，不杀占用者、不自动换端口。 |
| 状态与退出 | `state init --synthetic` 显式创建全新私有库；`run` 不建 schema；`state inspect` 只读。dry_run / execute 分库、版本和 instance 必须匹配。可能已发送但不能证明确认的写进入 unknown，不清库、不刷新身份、不盲重发；强制清理不等于正常退出。 |
| Rust 进程与构建 | 产品 driver 由 `current_exe()` 启动隐藏 `__driver` 模式，当前没有独立 `ff-driver` 可执行文件。产品与测试夹具构建分开；`rust-snap7=1.142.2` 的冻结 build.rs 经 cc 编译 native C++ 静态 archive，不能据此断言最终程序全静态或无系统库。 |
| 平台现状 | 已有本机证据限 macOS arm64；Rust 源码直接使用 UnixStream、Unix signal、POSIX 锁/FD 等，Python 也依赖 `fcntl`。Windows 不能仅凭 Rust target 可安装或上游库宣传便宣称当前工程可构建/交付。Linux 亦须明确本任务未实测的边界。 |

已读根 [AGENTS.md](../../../AGENTS.md)、根及 FF / 两工程 README/PLAN 双语、完整关联 bundle 与嵌套历史、[canonical workflow](../../../.codex/workflows/development-lifecycle-workflow.md)、实际 `.codex/agents/pm.toml` 及适用 shared skill。实际选定角色为 `pm`；TOML 的 model / effort 是配置证据，不冒充底层运行遥测。profile 为 `contract_only`，不宣称平台 ACL、强制路由或团队自动激活。

## 3. 交付文件、写入阶段与 allowlist

### 3.1 本轮 PM 阶段

下段为起草阶段的写入 / 导航记录，原文保留；本次 PM 仅在同一 spec 记录精确 r1 批准及交接，主协调器据真实 `owner_approved` 机械同步导航。后续 Development 仍受第 3.2 / 3.3 节原 allowlist 和角色分工约束。

PM 唯一写入：`field-flow/plans/FF-002-user-guide-and-runtime-positioning/spec.md`。主协调器可依据已形成的 spec 机械同步必要任务导航，表达 r1 draft / 待范围批准，仅链接已存在角色文件。PM 不写导航、不替后续角色填记录。

### 3.2 精确 r1 获批后的文档面

所有路径相对仓库根。以下是上限，不要求为凑齐清单修改无关内容；README 只放入口和稳定定位，PLAN / catalog 只放唯一任务导航及真实阶段，不复制手册正文或三角色事实。

| 类别 | 精确路径 | 限制 |
| --- | --- | --- |
| 新增对照总手册 | `field-flow/USER_GUIDE.md`、`field-flow/USER_GUIDE.zh-CN.md` | 两语言对照、读者路径、共同概念与差异；不成为子工程运行必需依赖。 |
| 新增 Rust 自包含手册 | `field-flow/field-flow-rust/USER_GUIDE.md`、`field-flow/field-flow-rust/USER_GUIDE.zh-CN.md` | 单独复制本工程即可完成自身准备、运行、理解服务及案例开发。 |
| 新增 Python 自包含手册 | `field-flow/field-flow-python/USER_GUIDE.md`、`field-flow/field-flow-python/USER_GUIDE.zh-CN.md` | 源码学习 / 快速原型路线，包含全部自身步骤；不要求复制 Rust 或父文档。 |
| 新增 Rust 构建说明 | `field-flow/field-flow-rust/BUILD.md`、`field-flow/field-flow-rust/BUILD.zh-CN.md` | 当前构建、二进制/运行文件清单、native/系统依赖、平台核对矩阵及未验证限制。 |
| FF 必要入口 | `field-flow/README.md`、`field-flow/README.zh-CN.md`、`field-flow/PLAN.md`、`field-flow/PLAN.zh-CN.md`、`field-flow/plans/README.md`、`field-flow/plans/README.zh-CN.md` | 新手册入口与新定位；FF-001 历史状态继续引用原 bundle。 |
| Rust 必要导航 / 索引 | `field-flow/field-flow-rust/README.md`、`field-flow/field-flow-rust/README.zh-CN.md`、`field-flow/field-flow-rust/PLAN.md`、`field-flow/field-flow-rust/PLAN.zh-CN.md`、`field-flow/field-flow-rust/plans/README.md`、`field-flow/field-flow-rust/plans/README.zh-CN.md`、`field-flow/field-flow-rust/CODE_INDEX.md` | 链接本工程手册 / BUILD，校正已过时的当前阶段导航；不改历史任务正文。 |
| Python 必要导航 / 索引 | `field-flow/field-flow-python/README.md`、`field-flow/field-flow-python/README.zh-CN.md`、`field-flow/field-flow-python/PLAN.md`、`field-flow/field-flow-python/PLAN.zh-CN.md`、`field-flow/field-flow-python/plans/README.md`、`field-flow/field-flow-python/plans/README.zh-CN.md`、`field-flow/field-flow-python/CODE_INDEX.md` | 说明源码使用与 Python 不做打包的本轮范围；保留现有工程和旧证据。 |
| 根必要导航 | `README.md`、`README.zh-CN.md`、`PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`、`CODE_INDEX.md` | 仅 FF 入口、精确任务状态与下一 gate，由主协调器机械同步；保留其他任务行和并行 dirty。 |
| 当前角色事实 | `field-flow/plans/FF-002-user-guide-and-runtime-positioning/tasks.md`；`field-flow/plans/FF-002-user-guide-and-runtime-positioning/checklist.md` | 前者仅 Development 在范围批准后创建/维护；后者仅 fresh Verification 在 developer_handoff 后创建/维护。PM 继续只写 spec。 |
| 真实证据附件 | `field-flow/plans/FF-002-user-guide-and-runtime-positioning/evidence/**` | 仅已有真实来源、命令记录、必要输出 / hash；不预建空证据，不提交数据库、构建物、环境、真实配置或日志中的敏感内容。权威摘要仍归 tasks/checklist。 |

文档中的源码 / YAML / locale 示例是教程正文，不写回正式源码。新增案例的必要逐文件接线只在第 8 节的任务自有临时副本执行，用于证明文档可照做；有效文档最终交付到当前正式工作树，不把手册只留在临时副本。

### 3.3 明确排除

不修改任一工程的 `src/**`、`tests/**`、`config/**`、`locales/**`、Cargo/uv/pyproject 清单或锁、`.python-version`、`.gitignore`、license / 第三方源码、现有配置和状态。本任务不新增依赖、产品能力、通用插件 / 自动 app 发现、注册器重构、demo02、HTTP POST / 鉴权、DS / Backend 联调、跨语言状态迁移、unknown 处置入口、后台托管、安装器 / 签名 / 发布 / 部署。

根 AGENTS / ROADMAP、其他任务及其 evidence、AW / DAA / DS / SMA / CA、backend、frontend-js、现有 tools、共享 skill 和项目外环境均排除。真实 `.env` / 客户配置不读取；公开 `.env.example` 如确有相关内容可只读，不能借机自动发现目标。无 Git refs、commit/push、Docker 操作、真实数据库 / PLC / 第三方业务 HTTP 操作、外部发送或任务外资源回收。

## 4. 需求

### R01 两语言定位与当前证据

1. 总手册和两工程入口一致说明：Python 为熟悉语言、练手及快速原型；Rust 为后续长期部署 runtime 的主要建设方向。长期运行仍须完成独立的目标平台、托管、现场、容量和长稳验收，语言选择不等于已具生产资格。
2. 保留已有 Python 工程、功能、测试、依赖及 FF-001 双语言本地验证事实，不将其事后改写成“仅伪代码”或撤销既有 QA；旧历史文档无需修改。
3. 本次对照教程使用同一现有能力，帮助理解语义与语言差异；不建立未来所有生产 flow 必须双语言同步实现的长期要求，也不承诺两版内部布局或 API 逐行相同。
4. 当前稳定能力、仍待 Owner 验收的本地候选及未来方向分别写清，FF-002 文档 QA 不替 FF-001 终验或未来部署验收。

### R02 手册组织与独立复制

1. 提供前述八份新文档，英文与中文内容等价，命令、参数、告警、返回 / 错误语义和平台矩阵保持对称；技术标识和状态 key 不翻译。
2. 总手册给出读者路线、目录对照、共同业务链路与语言差异表。每个子工程 USER_GUIDE 含完整的自身依赖准备、目录、CLI、夹具、状态、运行、服务用法、新案例注册及验证步骤，不能仅让读者去父级或兄弟文档查必需命令。
3. 子工程内可链接自身 BUILD / README / CODE_INDEX / notices；指向父任务的链接只能作为可选治理导航，父目录缺失不影响运行教程。无需为此复制任务 bundle。

### R03 自有夹具与现在可用的手跑入口

1. 分别说明 HTTP synthetic command 源、真实 S7 server / 注册内存、透明 TCP proxy / 请求计数与故障注入的职责和进程边界。proxy 前后两段 TCP 不是两个业务 PLC client；这是有限本地协议夹具，不是 DS 产品，也不要求 DS、Backend、Docker 或另一语言的进程。
2. 明确区分自动化集成测试 / CLI smoke 与可独立打开终端的人工夹具入口；测试内部可动态改响应 / 注入故障，不代表人工 CLI 已有交互面板、管理 API、持续新命令生成或任意点表能力。
3. 逐语言列真实命令、feature / 环境、固定端口、输出目录的全新要求、就绪观察、runtime 停止方法、fixture 正常停止方法及实际报告名。Rust 按 ENTER；Python 用 SIGINT/SIGTERM，不混写。
4. 说明 fixture 命令身份、值 42、生成时刻 / expiry 和 `input_max_age_ms` 的关系。重复 GET 不更新时间；应先完成安装 / 编译 / init 再起 fixture，并在有效窗口内启动 runtime。超过时效的 stale / idle / duplicate 是实际语义，不用手改原时间、重建运行库或刷新同 ID 绕过。
5. 解释当前人工入口对 source、DB1 / 16 bytes、配置首流、固定端口及命令数等实际约束；不能将通用 typed config 的可表达范围写成人工 fixture 已实现的全部能力。故障历史和 Python 原 API preflight 明确为历史失败入口，不加入正常“全绿”使用路径。

### R04 完整运行路径

1. 每工程给出从工程目录 / 新复制目录出发的可复制顺序：检查已有工具及锁 -> 锁定依赖准备或 Rust 构建 -> 无参 / 中英帮助 -> 创建新的私有父目录 -> 预先显式 init dry_run / execute -> dry-run 教学场景启动 fixture 并确认就绪 -> 默认 dry-run -> 正常停止 runtime / fixture、inspect 并确认资源释放 -> 在另一个全新教学场景启动 fixture 后立即运行 execute -> 正常停止、inspect、确认资源释放。不要求读者在同一个默认 10 秒有效窗口内完成 dry-run、退出观察再 execute；所有依赖 / build / init 都在各场景的 fixture 启动前完成。两个场景使用各自新建且模式匹配的 synthetic 状态，不能将 dry_run 库转作 execute。原 execute 场景的重启仍保留原库 / 身份，不能通过重启 fixture 刷新同 ID 的时间绕过时效 / 去重。另从空 cwd 验证无参 / 帮助无配置、网络或状态副作用，调用已构建的本工程 executable 或已准备好的本工程 Python 环境；不声称未构建 / 未准备依赖的源码可直接执行。两种模式及两语言按顺序执行，不同时成为相同业务资源的 writer。
2. 命令必须标明在哪个终端、cwd、运行入口以及路径解释方式。不同 shell 不共享变量；第二终端应复制第一终端输出的真实绝对路径，并明确赋值，不能照抄未设置的 `$FF_RUN_ROOT` 或尖括号占位符。
3. 解释 normal run 不建 schema、init 不覆盖、mode / implementation / instance / schema 不匹配的错误；CLI / 参数错误、运行故障和正常退出码按真实实现列出。
4. Python 使用自身 `uv.lock`、已有 CPython 3.11 / `.python-version` 和自身环境，命令显式 `--python 3.11 --no-python-downloads`；缺工具先报告，不自动下载解释器或全局安装。这里交付源码使用说明，不做 Python exe、wheel / sdist 交付、PyInstaller / Nuitka、离线包或安装器；不删除既有 build backend、锁及 FF-001 历史构建证据。
5. 命令示例只用公开合成配置 / 本工程夹具。config 文件必须显式指定；状态和日志归新私有路径，不扫描父 / 兄弟配置。

### R05 配置、状态、日志及运行生命周期

1. 说明 typed YAML 字段及对应对象、ID / kind / target 的不同含义、有限预算、允许范围与跨字段关系，给出两语言当前配置对照。DB 号、大小、offset 是显式配置；示例 DB1 不是现场固定合同。
2. 用一个 HTTP GET -> INT 案例解释单轮、flow 外层调度、HTTP client 复用、PLC owner / driver session 复用、FIFO 与错误恢复；用已有测试 / 源码案例解释多流并发、同流不重叠、同点独立采样和无共享快照。未注册用户流不能冒充可直接启动的产品命令。
3. 给出实际状态文件 / 锁 / gate / JSONL 路径、相对 / 绝对路径规则、`state inspect` 可观察项和必要日志事件、轮转 / 容量上限、health 是日志而非监听接口。SQLite 属本地执行事实，不替 Backend 业务库。
4. 解释 T1 / T2 / T3、pending / in_flight / confirmed / unknown / expired / canceled / simulated；`confirmed` 是匹配协议 ACK + 本地确认持久化，不是物理 / 工艺完成。unknown / 冲突 / 时钟异常 / 审计和容量背压该如何识别、停止与保留证据，不提供绕过写法。
5. dry_run 和 execute 库不能互换，不把复制 / 重置 / 删库写成恢复办法；Rust / Python 不共享可写库或直接互换状态。切换 writer 须停旧端、核对未决和已确认进度并明确交接，跨主机 fencing 尚未实现。
6. 正常 stop 的闭闸、取消未开始请求、在途结果与 unknown、join / wait / 子进程回收逐步解释。forced / fault_cleanup / shutdown_incomplete 与正常退出分开；不按进程名或端口扫描后杀占用者，不把 Ctrl-C 已发送或 PID 被打印当释放证据。
7. Unix 来源毫秒、monotonic 耗时及日历日志 / SQLite 元数据按真实语义说明，不能机械加八小时。发现现有日历表示与当前根时间合同不一致时，如实列限制和后续整改 gate；本任务不静默改 schema、历史时间或日志实现。

### R06 app 可用方法及基础设施边界

1. 给出源码路径与方法对照，逐项说明参数对象 / 类型、返回、async / await、主要稳定错误 key、生命周期 owner 和最短用例。至少覆盖 demo01 一轮、Flow / Plc / Target、严格输入解析 / Intent、HTTP GET、INT read、Execution.apply、Clock / anchor、Stop、状态读取 / inspect 与日志观察。
2. 以当前源码为准：Rust `iteration(&Flow, &Plc, &Http, &Owner, &State, &Stop, &mut Clock) -> Result<()>`；Python `once(http, flow, plc, execution)` 的真实对象、`idle` / 执行结果和 `Failure` 传播。Python 的类型表是文档解释，不假造现有注解或新增公共 API。
3. 区分 app 能正常组合的服务、runtime 装配 / 生命周期对象和基础设施内部能力。PLC 写必须经 Execution.apply 保留时效、身份、事务、stop 和 unknown 保护；`Owner::write`、raw S7 / driver IPC / SQL 不作为 flow 任意副作用快捷方法。INT read 也经本 PLC owner，不逐轮新建 client。
4. 状态 / 日志内部方法可解释职责，不包装成承诺长期稳定的 SDK；现成 typed GET / INT 服务与未提供的 POST、认证、通用读写、事件订阅、自动注册明确区分。需要新 API 的业务只记后续任务，不能为完成手册新增实现。

### R07 两语言新增同能力案例教程

1. 使用一个自定义名的 GET -> 已有 INT 能力案例，分别给完整的单轮源码和逐文件改动示例，解释每一步。新增名用于教学，不把未实现 demo02 / 上升沿 / POST 偷渡进教程。
2. Rust 必须解释 `src/app/<case>.rs`、`src/app/mod.rs`、`src/config.rs` 的 kind 校验和 `src/runtime.rs` 的明确派发接线；Python 必须解释 `src/field_flow/app/<case>.py`、实际 import 所在模块、`src/field_flow/config.py`、`src/field_flow/runtime.py`。按真实代码决定哪些现有文件必须改，不能只展示放文件 / 改 YAML。
3. 给出配置副本、flow / source / business 身份、target 与冲突约束、入口及命令。若为复用当前人工 fixture 保留 `demo01-feed`、DB1 或其他固定值，必须说明这是当前夹具限制；教程不能把配置改成 fixture 实际不会提供的 feed 后宣称可跑。
4. locale / CLI 帮助若无新增文案，明确无需改 locale；如示例确有新增 key，则给两语言自身 zh-CN / en-US 同步位置及内容。说明 CODE_INDEX / README 导航如何更新，但本任务不把示例接线写回正式工程。
5. 案例保持一次有界迭代，调度归 runtime，业务条件归 app，IO / 状态写入归既有服务；不复制 raw S7、SQL 或无界 retry。给出源码编译 / 导入检查、对应配置校验和最小 dry-run / execute / inspect 的验证步骤及预期观察。
6. 文档中的新增源码在自有临时副本逐条照做验证；若示例需修改超出这些显式接线的通用 schema / driver / state / 协议能力才可工作，则缩回已有能力，或记录后续阻塞，不顺手修正式实现。

### R08 Rust release 与目标平台构建说明

1. 使用本工程 `Cargo.toml` / `Cargo.lock` 和当前 `rust-version=1.89`，给出锁定 release 构建和产物运行命令，区分 `--no-default-features --bin field-flow` 产品构建与 `--features test-fixture --bin ff-fixture` 夹具构建 / 故障 hook。发布 runtime 不要求随带测试夹具；本任务不发布任何产物。
2. 核对所有实际运行必需的二进制 / native / 动态系统库、配置、locale 和 notices；明确 driver child 来自同一产品 executable，正常运行不要求人工启动隐藏入口，也不虚构独立 ff-driver。按实际构建解释哪些 locale 已编入二进制、哪些文件仍需显式提供，不能照搬 Python 的文件布局。
3. `rust-snap7=1.142.2` 的 source / checksum / build.rs、cc 及 native C++ 规则以冻结锁和原缓存源码为依据；必要时只补官方 primary 文档并记录精确 URL / 版本。指出 native archive 编译不等于最终全静态；本机动态依赖可用原生只读工具核对，不能猜测 MSVC / GNU / musl / static 支持。
4. 以 macOS / Linux / Windows 三行列出：目标 OS / arch、原生编译条件、Rust target 与 C/C++ compiler / linker / 系统 SDK 差别、当前源码平台限制、本任务实际验证状态、待验证 gate。区分“官方工具链可选”“源码静态核查”“本机实际构建 / 运行”；Windows 的 Unix 源码阻塞必须明示，Linux 没有实际构建也不能写已交付。
5. 原生构建给出适用条件下可照做的步骤；交叉编译说明 target 标准库之外还需 target linker、native C++ / SQLite 构建链及匹配系统库，不能把 `rustup target add` 写成完整跨平台方案。本任务不安装 / 下载额外 target、MSVC、GNU、SDK 或交叉工具链。
6. 在 BUILD 明确源码 / 配置 / 新 synthetic 状态与既有执行状态的不同生命周期：可执行文件替换或迁机前先停 writer、核对 schema / instance / mode 和未决命令，保留原状态与日志；不能随意复制运行中 SQLite / 锁 / gate，不能删除库重新开始。字段、schema 或兼容性缺口仅记后续任务。
7. 链接已有第三方 notices，准确保留包装层、native 和 build.rs 的来源 / license 差异。文档核对和本机链接结果不等于完成分发合规结论、全静态证明、签名、安装器或现场部署资格。

工具链说明的官方 primary 入口为 [Cargo build](https://doc.rust-lang.org/cargo/commands/cargo-build.html) 和 [Rust platform support](https://doc.rust-lang.org/rustc/platform-support.html)；它们说明构建选项和编译器目标支持，不替代冻结原包、当前 FF 平台源码及本任务的实际构建证据。

### R09 导航、证据与交接

1. 仅按第 3 节同步本任务必要双语入口 / 索引，两子工程过时的阶段描述以唯一 FF-001 bundle 当前事实为准；不改其 spec / tasks / checklist / evidence，不将历史 DEV 用词直接批量替换成全局终验。
2. 所有新命令、方法表、配置 / 源码示例与当前实现逐项映射，Development 在 tasks 记录对应路径及核对依据、实际命令 / cwd / 版本 / 退出码、失败 / 限制、候选文档清单 / hash 和临时资源。
3. fresh Verification 独立读取精确 r1、tasks、正式文档 / 源码 / diff 与必要原始输出，以自己的核对和必要复演给 verdict；DEV 绿灯不替 QA。源码缺口如实交回 PM，范围 / allowlist / 验收 / 风险实质变化须新 Revision 和 Human Owner 批准。

## 5. 所需 skill 与责任 handoff

PM 使用 `aiis`、`project-governance` 管理本次工业边界、任务身份、范围和批准链，不替 Development / Verification 做技术构建或协议验证。

后续 Development / Verification 必须按本任务表面使用：`aiis`、`project-governance`、`rust-runtime`（运行方法、长期 runtime 边界、Rust / native 构建文档）、`plc-point-mapping`（仅标准 DB INT 地址 / 类型解释）、`code-document-indexer`（真实入口 / 索引）、`i18n-workflow`（双语人类说明、教程中的 locale 合同）。涉及本地执行状态 / 事务解释时使用 `backend-arch` 的适用合同，不套用 FastAPI / ORM / migration 模板。

不因 BUILD 这个文件名引入 Python 后端打包 skill，不使用 Tauri / 前端 / Celery / Docker / project-tooling 模板。必要的日志、语言分层和资源生命周期 reference 随相应 skill 按需读取；专门技术工作由相应实际命名角色完成，PM 只定义交付与证据要求。

## 6. 验收标准

全部为 FF-002 自身的验收，不复用 FF-001 的 QA verdict 作为本任务通过。

| AC | 可观察标准 / 对应需求 |
| --- | --- |
| AC01 | 唯一 FF-002 / r1 / namespace / 独立验收链和角色事实完整；未继承 FF-001 或旧讨论批准；不抢用未创建的 DS 联调建议作实现事实。（第 1–3 节 / R09） |
| AC02 | 八份新文档齐备且英文 / 中文命令、参数、能力、错误、风险和平台矩阵对称；总手册比较清楚，两子工程各自独立复制后具备全部必需使用 / 开发说明。（R02） |
| AC03 | Python 学习 / 快速原型且本任务不打包、Rust 长期 runtime 建设主线的定位一致；现有 Python 源码 / 测试 / 历史 QA 保留，未来不强制所有生产 flow 双语言同步。（R01 / R04） |
| AC04 | HTTP / S7 server / proxy 的职责、进程、端口、固定命令 / 时间、人工入口 / 自动测试、正常退出 / 报告及 DS 差别均对应源码；没有虚构人工控制 / 持续命令入口。（R03） |
| AC05 | 两工程均有从空 cwd help、锁 / 环境准备到显式 init、dry-run、execute、inspect、正常停止及实际资源检查的完整命令；终端 / cwd / 实际路径和 fixture 有效窗口清楚，有限本机复演符合文档。（R04 / 第 8 节） |
| AC06 | 配置对象 / 字段、预算、路径、状态 / 时效 / unknown / writer / 日志 / 容量 / 正常与故障退出均能从当前源码核对；没有清库、改时效或绕过 Execution 的恢复建议。（R05） |
| AC07 | 可用方法表包含真实路径、签名或 Python 实际对象合同、参数 / 返回 / async / 错误 / owner 和用例；flow 服务、装配与基础设施内部能力分清，没有承诺不存在的公共 API。（R06） |
| AC08 | 两语言同能力自定义案例的完整代码 / 配置和逐文件注册接线可在独立临时副本照做；源码 / import 或编译、校验及最小运行观察成功，正式实现 / 配置 / locale / 锁没有因此变化。（R07 / 第 8 节） |
| AC09 | 以真实源码 / 既有测试入口解释 flow 并发、同流不重叠、HTTP 不占 PLC 队列、同 PLC 持久 session 和独立采样；示例不冒称当前人工 CLI 已能启动未注册产品流。（R05 / R07） |
| AC10 | Rust BUILD 给出产品 release 与夹具 feature 差异、实际 executable / child / 配置 / locale / native / 系统依赖清单；本机实际依赖核对与本地步骤成立，未虚构 ff-driver 或全静态单文件交付。（R08） |
| AC11 | 三平台矩阵有原生 / 交叉工具链条件、Unix 源码阻塞与逐项未测状态；冻结 rust-snap7 源和官方 primary 来源可追溯，不把 target 存在或 macOS 成功当 Windows / Linux 交付证据。（R08） |
| AC12 | 批准范围内导航与索引双语一致、只链接真实角色文件、独立工程无必需父 / 兄弟运行依赖；FF-001 及 ARCH 历史 / 证据 hash 保持，任务外 dirty 原样保留。（R02 / R09） |
| AC13 | tasks / checklist 分别有真实核对与演练命令 / 版本 / 退出码 / 限制、文档与临时资源清单；PID / 固定端口实际释放，必要证据持久化；无未授权安装 / 设备 / 数据 / 外部动作。（第 8 节 / R09） |
| AC14 | 实际 fresh-context Verification 对上述 AC 独立给 verdict；平台未测 / 后续移植 / 现场 / 长稳 / 分发等 gate 保持清楚，qa_passed 仅进入 Human Owner 最终验收。（第 5、8、10 节） |

## 7. 风险、取舍与回退

| 风险 / 取舍 | 处理与边界 |
| --- | --- |
| 为让教程好看而虚构现有能力或修代码 | 所有命令 / 方法 / 注册步骤对应当前源码；源码缺口单列限制 / 后续范围，不修改正式实现。不把希望存在的通用服务写成现有 API。 |
| 自包含手册有少量重复内容 | 总手册负责比较，各工程保留自身完整必需步骤；采用相同章节和核对表维持中英 / 两工程一致，优先保证独立使用。无需引入生成器或新依赖。 |
| fixture 命令过期 / 固定身份使初学者误以为失败 | 先准备依赖 / build / init，再起 fixture；解释固定原时间与去重。新的教学运行使用全新私有 synthetic 目录，不把该方法推广成现场故障恢复或删除旧状态。 |
| 新案例示例暗含未实现注册 / feed | 给出真实 config / runtime 接线和夹具限制；在自有副本演练，证明示例可用；不扩成插件框架。 |
| 三平台构建承诺超出现有 Unix 源码与本机证据 | 文档 / 来源核对矩阵满足本任务三平台说明；Windows 源码阻塞、Linux 未实测明确记录，移植 / 原生环境验证另任务。不能为交付文档降低这一事实边界。 |
| native archive / license 被误读为无需依赖或已可分发 | 按冻结原包和本机实际链接情况解释并链接原 notices；静态 archive、最终动态库与分发要求分别记录，不作未经证明的单文件或许可结论。 |
| 现有时间表示和当前根合同不同 | 源 Unix ms / monotonic 保留各自语义，实际日历日志 / 元数据如实解释；不篡改历史，不以文档任务暗中迁移状态。需要实现整改时回 PM 新范围。 |
| 与 FF-001 / DS 等并行 dirty 相邻 | 只按精确文档 allowlist 和任务级 diff / hash 审计；禁止整树 reset / 格式化 / 清理。旧资源和失败库不归本任务操作。 |

回退只针对本任务新增文档和归属明确的文档差异，不能自动撤销并行编辑或回退 runtime / 状态。暂存演练源码只用于核验教程，不整合为产品能力。发现命令可能误操作现有状态时停止该步骤，保留原证据，改为新私有 synthetic 场景；不得通过清库、改状态或启动第二 writer 来证明教程“可用”。

## 8. 精确批准后允许的验证

精确 r1 的 Human Owner 范围批准 gate 现已满足；以下起草时的条件说明与第 1–9 项验证边界原文保持。当前尚无本任务运行 / 验证结果；后续仅实际 Development / Verification 执行并记录获批范围内的必要验证。

以下是未来执行边界，当前全部 `not_run`；获得 Human Owner 对 **FF-002 r1** 的范围批准后才生效。

1. 静态核对中英结构、Markdown 链接 / 锚点 / 空白、实际文件与方法 / 参数 / 配置 / feature / locale、身份和索引状态；验证八份文档不靠父 / 兄弟运行依赖。命令 / 来源证据进入 tasks，Verification 再独立审查。
2. 在本任务新建的 `/private/tmp/ff-002-r1-<unique>/` 下，分别建立 Rust / Python 单工程干净副本；复制排除 `target`、`.venv`、`dist`、cache、状态、锁 / gate 运行文件和日志，不复制真实配置。可使用正常公共 package cache，不借兄弟环境、可执行文件、fixture 或可写状态。
3. 使用已有本机工具及冻结锁完成手册所必需的 Rust release / fixture 构建、Python uv 环境准备和无参 / 中英帮助。构建 / 环境写入本任务私有根；不修改正式清单 / 锁，不自动安装或下载解释器 / Rust target / 系统编译器。正常缺失的锁定依赖可按既有声明准备到私有环境 / cache；网络或依赖缺失如实记录，不绕过限制。
4. 新 synthetic SQLite 仅在该私有根内通过既有显式 init 创建；dry_run / execute 分离，instance 与配置匹配，不读取 / 覆盖真实库或 FF-001 旧运行库。后续重启同一演练场景保持原状态 / 身份，不能用换库掩盖 unknown / 重发。
5. 只绑定第 2 节六个既有固定 loopback 端口，逐语言和模式串行。先只读核对占用，冲突则停止该演练并报告；不杀占用者、不换端口、不连真实 PLC、DS、Backend、第三方 HTTP。dry-run 与一次 execute 的最小真实 GET -> INT 链路、inspect 和正常关闭足够证明教程步骤，无需重跑 FF-001 全部故障 / ACK 拒绝 / 崩溃矩阵。
6. 把 R07 文档中的自定义案例逐文件应用到各自临时副本，允许仅该教程必需的 app / import / kind 校验 / runtime 派发、配置副本和对称 locale / 索引示例，复用现有能力与锁。执行必要编译 / 导入、配置与有限运行检查，保留示例差异及结果；不写回正式工程，不新增 runtime API / schema / driver 能力或依赖。
7. 本机可做 release 二进制帮助、实际动态依赖和正常退出核对；不安装服务、不部署、不测试未有的 Windows / Linux 环境，不为“验证平台”下载工具链。本机成功与文档来源核对分栏，必需本机步骤缺失则 QA blocked / failed，不能以“文档任务”免去演练；本 spec 明确未要求的跨平台实测保持未测 gate。
8. 记录每条实际命令 / cwd / OS / arch / 工具和依赖版本 / 退出码、必要报告与失败。所有启动的 runtime / driver / fixture 均须实际 wait / join，核对确切 PID 和固定端口释放；强制清理如实记故障，不能当正常教程通过。不得修改宿主系统时间或运行整库清理。
9. Development 在 handoff 列完整任务自建临时目录、源码副本、环境 / target、合成状态和报告的用途 / 归属 / 保留条件；关键结论持久到 tasks / evidence，不能只依赖 `/private/tmp`。Verification 核对资源和证据依赖，Human Owner 终验后由 active coordinator 按 canonical workflow 核对归属 / 占用 / 下游依赖再回收，无权清理 FF-001 / 其他任务资源。

## 9. 待定项与后续工作

真实现场 OS / CPU / PLC / 工艺 / 网络、Backend API、DS 联调、服务托管 / 升级 / 备份 / 许可分发、长稳及生产容量不阻塞本轮文档，但均不在本轮取得资格。平台移植、API / fixture 易用性缺口、demo02 / 其他数据类型、unknown 人工处置和跨语言迁移须另任务或新 Revision。

本轮不强求统一 API 形状、补 Python 类型注解、修改 Rust POSIX 层、自动刷 fixture 时间或新增交互面板。教程若不能在现有能力内自洽，先明确缺口，不能因文档需要而静默扩实施面。

## 10. 批准、角色交接与修订

以下三段为起草阶段批准请求与预期 handoff 原文；“当前尚无范围批准”“当前不启动后续角色”仅描述当时。本节新增批准记录及当前交接见其后，原需求、allowlist、AC、风险及验证边界不变。

PM -> Human Owner：请审阅精确 **FF-002 r1** 的八份新文档、文档 allowlist、AC01–AC14，以及第 8 节独立临时副本 / 新 synthetic 状态 / 六个固定 loopback 端口内的必要本机演练。当前尚无范围批准；原用户请求和 FF-001 r4 批准均不替代此 gate。

Human Owner 明确批准精确 r1 后，主协调器实际选择 `development` 角色；Development 读取完整已形成 bundle，在批准文档面实施、自检、记录 tasks 和精确候选 / 限制 / 资源，形成 `developer_handoff`。随后主协调器实际选择 `verification`, `fork_turns="none"`，从新上下文读取 approved spec、tasks、正式文档 / 源码 / diff 与证据，逐 AC 独立出 checklist verdict。QA 不修实现，Development 不代写 QA；`qa_passed` 后仍待 Human Owner 最终验收。

范围、allowlist、验收、风险或模式实质改变时停止未授权部分，回 PM 新 Revision 和 Human Owner 批准。仅角色文档 / diff / 主会话审计形成合同控制，不声称文件 ACL 或自动强制流程。当前不启动后续角色、不执行第 8 节命令。

**PM -> Development 当前交接：** Human Owner 已明确批准上述精确 FF-002 r1。由主协调器实际选择 `development` 角色读取本文件与已形成 bundle，按原文档 allowlist / R01–R09 / AC01–AC14 / 第 8 节边界实施、自检并创建 / 维护自己的 tasks。真实 `developer_handoff` 后由主协调器实际选择 `verification`, `fork_turns="none"` 进入独立 QA，最终仍待 Human Owner 验收。PM 不创建 tasks / checklist，不写导航、手册、源码或配置，不执行本任务程序；本次批准记录不改 Revision 或扩大范围。

| 日期 | Revision | 真实阶段 |
| --- | --- | --- |
| 2026-10-23 | r1 | PM 新建有边界的双语手册 / Rust BUILD 文档 draft；范围批准 pending。仅只读现有合同 / 文档 / 源码 / 锁与冻结 native build 文件并写本 spec，未安装 / 构建 / 初始化 / 监听 / 运行 / QA，未授予最终验收。 |
| 2026-10-23 | r1 | Human Owner 明确回复“批准 FF-002 r1，按方案完成 Python/Rust 对照使用手册、案例开发教程和 Rust BUILD 说明，完成后按 STD 进入独立 QA。”批准精确原审稿 SHA256=`2cb1e14ea24b8ea1cf13b8c23bda39481d320638e46dddebad3f5949f15503a9` 的 r1；Status 改为 owner_approved，交接实际 Development。仅新增真实批准 / gate 记录；原 draft 历史、需求、allowlist、AC、风险及验证边界保持，无实施完成 / QA / 最终验收结论。 |

PM 文档自检（2026-10-23）：只读辅助断言核对唯一身份 / draft、9 项需求、AC01–AC14、6 个活动本地链接、空白及后续角色文件仍未创建；FF-001 三文件、ARCH 讨论 spec 与两工程共 96 份受保护文件的 SHA256 对比无差异。此为 PM 文档检查，不是 Development 自检、独立 QA、全仓治理通过或运行验证。最终精确文件 SHA256 在 PM -> Human Owner 交接时给出，不在本文件内自引用。
