Task ID: FF-003
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Human Owner exact FF-003 r1 scope approval pending; Development and fresh-context Verification have not started
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 独立 C# 无界面运行时、demo01 HTTP GET 到 SQLite 执行状态及 S7 DB INT 的本地合成闭环与自身使用构建手册
Owner: Field Flow
Acceptance Chain Reference: FF-003 r1 精确范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
Related Task: FF-001, FF-002, ARCH-TOOL-001

# FF-003：C# 独立运行时与 demo01 本地闭环

## 1. 当前阶段、目标与可靠输入

**当前仅为 FF-003 r1 draft，精确范围批准 pending。** Human Owner 最新请求是“可以，那么现在顺手把cs版本的ff也构建出来吧”。此前讨论同意独立第三工程、.NET 10 LTS / 无界面 Console + Generic Host、与既有 demo01 相同的业务语义、多流并发和每 PLC 统一长连接 / 有界串行队列。这是本规格的需求来源；本文件形成前没有 FF-003 精确 Revision 批准，不据“现在构建”推断 DIRECT、BACKFILL 或跳过批准。

目标是在 `field-flow/field-flow-csharp/` 交付可单独复制、锁定依赖、构建、运行、测试及本机 publish 的 C# 工程。首轮包含完整的 HTTP GET -> 严格 typed 命令 -> SQLite 持久身份 / 状态 -> 标准 DB 两字节 INT 写入，以及独立读取、恢复、日志、健康和正常退出。Python 继续用于学习 / 快速原型，Rust 保持长期 runtime 建设主线，C# 是 .NET runtime / Windows 部署的候选方向；语言定位不证明目标平台或生产资格。未来生产 flow 按需选一种实现，不要求三份同步。

本任务独立 `Classification: root`，无 Parent Task ID。相关 [FF-001 r4 spec](../FF-001-dual-runtime-demo01/spec.md)、[Development](../FF-001-dual-runtime-demo01/tasks.md)、[QA2](../FF-001-dual-runtime-demo01/checklist.md) 及 [FF-002 r1 spec](../FF-002-user-guide-and-runtime-positioning/spec.md)、[Development](../FF-002-user-guide-and-runtime-positioning/tasks.md)、[QA2](../FF-002-user-guide-and-runtime-positioning/checklist.md) 已读取；其当前均为独立 QA 通过、Human Owner 最终验收 pending。两任务的批准、实现、QA、失败与资源不转移为 C# 结论。原 [ARCH-TOOL-001](../ARCH-TOOL-001-field-flow-runner/spec.md) 及所有历史保持。

2026-10-27（Asia/Shanghai）只读核对：根 / FF 索引未发现已占用的 FF-003 bundle，C# 目录不存在；协调器的工具链 inventory 中 PATH 和四个常见 SDK 目录未找到 dotnet。未安装、下载 SDK / NuGet 包，未编译或运行 C#，无协议预检结果。微软官方 release metadata 是版本选择依据，不是本机已安装证明。

已消费根 [AGENTS.md](../../../AGENTS.md)、README / PLAN 双语、FF / 两工程 README / PLAN / 手册、完整相关 bundle 和嵌套历史、实际 `.codex/agents/pm.toml` 及 [canonical workflow](../../../.codex/workflows/development-lifecycle-workflow.md)。角色为实际命名 `pm`；profile 为 `contract_only`，由主会话、bundle 和 diff 审计控制，不宣称平台 ACL、强制路由或自动激活。

## 2. 分阶段写权与精确 allowlist

所有路径相对仓库根；`**` 仅允许本规格需要的少量文件，不授权全目录重构。

| 阶段 / owner | 允许写入 | 限制 |
| --- | --- | --- |
| 本轮 PM | `field-flow/plans/FF-003-csharp-runtime-demo01/spec.md` 及必要父目录 | 只定义范围 / AC / 风险 / handoff；不创建 tasks、checklist、工程空壳、配置或空 evidence。 |
| 本轮主协调器 | `field-flow/PLAN.md`、`field-flow/PLAN.zh-CN.md`、`field-flow/plans/README.md`、`field-flow/plans/README.zh-CN.md`、根 `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`、`CODE_INDEX.md` | spec 真实形成后仅机械索引 FF-003 r1 draft / 下一 gate；不改其他任务事实或将既有双版本称作已完成三版本。PM 不写这九份导航。 |
| 精确 r1 批准后的 Development | `field-flow/field-flow-csharp/**` | 自身 global.json、solution / csproj、NuGet.Config、必要 MSBuild 配置 / locks、分层 C# 源码、typed YAML sample、locale、tests / test fixture / golden、`.gitignore`、自身 LICENSE / 第三方 notices、README / PLAN / catalog / USER_GUIDE / BUILD 双语及 CODE_INDEX。无父 / 兄弟工程 ProjectReference、源码引用、可执行文件 / fixture / 可写状态依赖。 |
| 批准后必要公共文档 | `field-flow/README.md`、`field-flow/README.zh-CN.md`、`field-flow/USER_GUIDE.md`、`field-flow/USER_GUIDE.zh-CN.md`、根 `README.md`、`README.zh-CN.md`，以及上行九份索引 | 仅新增 C# 自身路线、三工程定位 / 能力对照、真实目录与当前 gate；保留原 R/P 事实与限制。索引仍由协调器机械同步，文档主体由 Development。 |
| 当前角色事实 | 本 bundle 的 `tasks.md`、`checklist.md`、真实 `evidence/**` | Development 获批后才创建 tasks；真正 developer_handoff 后 fresh Verification 才创建 checklist。证据附件有实际输出才建立，分别由实际产生者记录来源；权威摘要 / verdict 仍归角色文档。PM 只写 spec。 |
| 获批后的私有资源 | 各执行者新建的 `/private/tmp/ff-003-r1-<unique>/` | 独占 SDK / CLI home / NuGet cache、build / publish、单工程副本、教程副本、新 synthetic 状态与日志 / 报告；确切路径 / 用途 / 保留条件归 tasks / checklist。公共包可按官方来源准备，禁止借兄弟运行环境。 |

明确排除 `field-flow-rust/**`、`field-flow-python/**` 的全部正式源码、测试、配置、locale、锁和文档写入，FF-001 / FF-002 / ARCH 全 bundle 及旧 evidence / 错误状态库，根 AGENTS / ROADMAP / shared skills / workflow / 角色配置，backend、frontend、AW / DAA / DS / SMA / CA、tools、真实配置 / 数据和任务外 dirty。不得 reset / 清树、全局格式化或按 HEAD 整体归因。不会为 checker 造子任务或改旧任务状态。

本 PM 阶段只允许规则 / 源码 / 公开 primary 文档 / 元数据只读核查及静态文档自检。SDK 准备、NuGet restore、build / test / publish、synthetic schema、监听器和本地合成写入，均须先有本精确 r1 批准。无全局安装 / sudo / profile 修改、Docker、真实 DB / PLC / 第三方业务 HTTP、Git refs / commit / push、发布 / 部署、服务安装、外部发送或旧资源回收授权。

## 3. Skill 路由、工具链与来源（R01）

PM 使用 `aiis`、`project-governance`。Development / Verification 使用这两项，并按实际面使用 `plc-point-mapping`（仅标准 DB / INT / offset）、`backend-arch`（仅本地状态 / 事务 / 稳定 key）、`i18n-workflow`（CLI 文案 / locale 对称）、`code-document-indexer`（关键源码说明 / 真实结构索引）。C# 无专属 runtime skill，按 AIIS 的 `language_neutral_engineering_standard.md` 与 `operational_logging_baseline.md` 落地，资源归因参考 `RUNTIME_RESOURCE_TRIAGE.md`。不套 Rust 专用、Python 后端打包、FastAPI / ORM / Celery / Redis、Tauri / Web 或通用工具模板。专门技术实现与验证归相应角色。

| 面 | r1 冻结选择 / 责任 |
| --- | --- |
| SDK / TFM | .NET SDK **10.0.403**、`net10.0`，首轮运行 runtime **10.0.14**。自身 global.json 固定完整 SDK 版本、`rollForward=disable`、`allowPrerelease=false`；不隐式使用主机其他 SDK。 |
| 宿主准备 | 首轮实际验收 macOS arm64；Development 记录真实 OS / CPU。若仍无 SDK，获批后只从下述微软官方 tar.gz 下载至新私有根，先核对 SHA512 再解压到空的 `sdk/`，用绝对路径调用 dotnet；不运行 pkg / sudo、不修改全局 PATH / shell profile、用户 SDK 或工具配置。 |
| 运行依赖 | `Microsoft.Extensions.Hosting=10.0.14`、`Microsoft.Data.Sqlite=10.0.14`、`YamlDotNet=16.3.0`。HTTP、Channels、JSON、Socket、时间 / SHA256 / 文件能力优先 BCL；日志用 Microsoft.Extensions.Logging 加单一 checked JSONL 持久 sink，不另建日志框架。SQLitePCLRaw / native SQLite 传递依赖由自身 lock 固化并如实列入 notices / publish 清单。 |
| 测试依赖 | `Microsoft.NET.Test.Sdk=18.11.0`、`MSTest.TestFramework=4.5.1`、`MSTest.TestAdapter=4.5.1`。仅 tests 交叉校验引用 `S7netplus=0.20.0`；不进入产品 csproj 或产品 publish。版本存在与兼容标记是只读事实，真实 restore / build / interop 均未执行。 |
| 锁与源 | 自身 NuGet.Config 清除继承 package sources，只用 `https://api.nuget.org/v3/index.json`；不继承父 / 用户私有 feed / 凭据。首次获批显式生成每个 csproj 的 packages.lock.json，记录精确直接 / 传递版本及 content hash；随后全部 `--locked-mode`，不使用浮动 / preview 版本。 |
| 私有缓存 | `DOTNET_CLI_HOME`、`NUGET_PACKAGES`、NuGet HTTP / plugin cache、build / publish / test results 都指向当前私有根；CLI telemetry 禁用、不自动安装 workload / 全局 tool / HTTPS dev certificate。构建服务器关闭 / 正常结束。`HOME` 与 `CODEX_HOME` 不改。 |

官方 [10.0 release metadata](https://dotnetcli.blob.core.windows.net/dotnet/release-metadata/10.0/releases.json) 在本轮读取时给出 2026-10-25 的 runtime 10.0.14 / SDK 10.0.403；[支持政策](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core)列 .NET 10 为 LTS、支持至 2028-11-14。本任务固定此候选，不自动跟随 latest；后续 patch 变更记录工具链 / lock / 受影响验证，若改变批准风险或能力范围回 PM。

本机允许的 SDK 归档：`https://builds.dotnet.microsoft.com/dotnet/Sdk/10.0.403/dotnet-sdk-10.0.403-osx-arm64.tar.gz`；官方 metadata SHA512：`5893c66b48ea3674c7da18501059d606e96f3672fabe4d5e41762e692c7c83df3ee0b2b9dc5a0786191da2dc413d7335158101c14c935ab217f31ac2529770f3`。下载 / hash / 解压 / `--info` 必须逐步记录；不匹配、缺包或网络 / 权限失败则停止相应步骤，不能写已构建。

包选择的 primary 记录：[Hosting](https://www.nuget.org/packages/Microsoft.Extensions.Hosting)、[Sqlite 10.0.14](https://www.nuget.org/packages/Microsoft.Data.Sqlite/10.0.14)、[YamlDotNet 16.3.0](https://www.nuget.org/packages/YamlDotNet/16.3.0)、[Test SDK](https://www.nuget.org/packages/Microsoft.NET.Test.Sdk)、[MSTest Framework](https://www.nuget.org/packages/MSTest.TestFramework)、[MSTest Adapter](https://www.nuget.org/packages/MSTest.TestAdapter)。页面当前版本不是锁文件；Development 将实际包来源、解析图与 hash 记录到 tasks。此 family 内同职责小型接线 / 文件拆分可自行决定；增加新栈 / fork / native PLC 依赖或改变验收须新 Revision。

## 4. 工程结构与入口（R02）

只创建一个产品工程和必需测试工程，允许按 C# 生态少量拆分，不逐文件翻译 R/P。建议结构如下；实际文件名由 Development 在 tasks / CODE_INDEX 固定。

```text
field-flow-csharp/
  global.json, FieldFlow.slnx, NuGet.Config, Directory.Build.props
  src/FieldFlow/FieldFlow.csproj, packages.lock.json, Program.cs
    Cli/, Configuration/, Application/Flows/Demo01.cs
    Application/ExecutionService.cs, Domain/
    Runtime/, Infrastructure/{Http,Plc,State,Logging}/
  tests/FieldFlow.Tests/                 # unit / protocol / lifecycle tests
  tests/FieldFlow.Fixture/               # 独立 C# test-only HTTP + S7 夹具 CLI
  tests/golden/                         # 固定字节 oracle，非运行依赖
  config/loopback.yaml, locales/{zh-CN,en-US}.json
  README.*, PLAN.*, plans/README.*, USER_GUIDE.*, BUILD.*
  CODE_INDEX.md, LICENSE, THIRD_PARTY_NOTICES.*, .gitignore
```

`Program.cs` 只做参数入口 / composition root，通常 <200 行；CLI adapter 校验形状后调用 Application；Domain 不依赖 Socket / SQLite / Host；runtime 只调度 / 监督 / 停止；HTTP / S7 / SQL / 文件属于 Infrastructure。新增关键源码保留中文文件头 / 职责说明并登记CODE_INDEX；单文件 >500 行需拆分评审，手写 >800 行视为架构缺口；不为每个小类建独立程序集，不增加插件 / DSL / 自动扫描框架。支撑目录按 project-governance 提供必要 README-only pair，全部归本工程上层 PLAN；自身 PLAN / catalog 只导航 FF 唯一 bundle，不复制任务正文。

无参、`--help` 和 `--lang zh-CN|en-US --help` **在配置读取与 Host 装配前早返回**，exit0；空 cwd 保持为空，无配置 / state / log / 网络 IO。错误命令 exit2。可见帮助 / 错误摘要使用对称 locale；稳定状态 / error / event key 不翻译。locale 编入产品程序集资源，帮助不读取外部locale文件，不能靠父 cwd fallback；BUILD说明其嵌入位置。

[Generic Host 文档](https://learn.microsoft.com/en-us/dotnet/core/extensions/generic-host)描述默认 appsettings / environment / logging providers；本工程需显式禁用这些默认配置读取及默认文本日志，run 只读自身 `--config` 指定 YAML 和明确 CLI 参数，不自动读 appsettings、.env、父 / 兄弟配置或 secret store。Host 仍负责依赖装配与生命周期，stdout 统一 JSONL，不混入生命周期文本。`dotnet run` 的 SDK 构建输出不算产品 stdout；验证产品日志直接运行已构建 DLL / apphost。

## 5. CLI、配置与边界预算（R03）

支持 `run --config <path> --state-dir <path> [--execute]`；省略 execute 为 dry_run，运行中不能自动换模式。显式 `state init --synthetic --mode dry_run|execute --state-dir <new-path> --instance-id <id>` 仅创建本任务全新 synthetic 目录；路径已存在、任何文件 / 库、符号链接或冲突拒绝，父目录须已存在，不覆盖 / 自动迁移。`state inspect --state-dir <path>` 只读元数据、状态计数及必要未决摘要，不写 DDL / pragma / 锁文件 / 日志。普通 run 用 `Mode=ReadWrite` 打开已存在库并校验 schema / implementation / mode / instance，不建 schema、不创建缺库。

配置为 ≤64KiB 人工可审阅 YAML；JSON 是 locale / 报告，SQLite 是执行事实，JSONL 是运行 / 审计；不增加 Excel / TIA 导入。拒绝 YAML 重复 key / alias 复杂展开、未知 / 缺字段、字符串或 bool 隐式转数字，JSON 输入也不宽松转换。

```yaml
schema_version: 1
instance_id: ff-csharp-demo01
plcs:
  - id: plc_demo
    host: 127.0.0.1
    port: 33102
    rack: 0
    slot: 1
    connect_timeout_ms: 3000
    io_timeout_ms: 5000
    queue_capacity: 16
    queue_wait_ms: 2000
    ready_wait_ms: 3000
flows:
  - id: demo01
    kind: demo01
    business_name: synthetic_command_to_int
    interval_ms: 500
    source_id: demo01-feed
    get_url: http://127.0.0.1:33880/demo01/command
    target: {plc_id: plc_demo, db_number: 1, db_size_bytes: 16, byte_offset: 0, type: INT}
    input_max_age_ms: 10000
http: {connect_timeout_ms: 500, total_timeout_ms: 1500, pool_wait_ms: 500, max_connections: 8, max_body_bytes: 4096}
shutdown_timeout_ms: 15000
```

ID 为 `[A-Za-z0-9_-]{1,64}`，1..4 PLC、1..8 flow；重复 ID、同 endpoint 多 PLC alias、未知 kind、重叠写目标启动前拒绝。普通产品只注册 demo01，验证读取 / 慢流只在 tests。物理资源以规范 IPv4 / port / rack / slot / DB / byte range 表示，不能用 plc_id / flow_id alias 绕过冲突。PLC host 为 IPv4 字面量，不做扫描 / DNS；本任务实际联网仅下述 loopback。HTTP URI 可校验 http(s) 形状且无凭据 / fragment，但本轮无实际外部接口授权。

| 参数 | 允许范围 / 关系 |
| --- | --- |
| PLC connect / IO | 500..3000 / 500..5000 ms；默认 3000 / 5000，均有限总期限 |
| queue capacity / queue wait / ready wait | 1..16 / 100..5000 / 100..5000 ms；最多每 flow 一个待完成 PLC 请求，无旁路无界队列 |
| interval / input max age | 100..10000 / 1..60000 ms；完成后再等 interval |
| HTTP connect / pool wait / total | 各前两项 100..1500，total 100..5000 ms；connect 与 pool wait 各 ≤ total |
| HTTP connections / body | 1..8 / 1..4096 bytes；请求池等待计入同一次 HTTP total |
| shutdown | 5000..20000 ms 且 ≥ max(HTTP total, 各 PLC connect, IO)+5500；默认 15000 |

ready 等待、队列等待、真正 dispatch 后 IO 分别起算；等待期间受原命令时效限制，**不能先消耗 IO 预算或在 dispatch 后继续用旧 queue deadline 截断合法 IO**。HTTP total 包含池等待、连接、header / body读取，不随每个阶段重置。单 PLC connect 包含 TCP / COTP / Setup / 错误关闭；IO 包含发送、完整收帧、解析和错误关闭，允许最多500ms调度误差。涉及命令同时取原 source deadline 的较小值；不得延长源有效期。

## 6. Typed demo01、INT 与来源时间（R04）

`Demo01` 只写一次有界业务迭代：await 一次 GET、严格转换为 idle 或 Intent，再 await ExecutionService；不持有无限循环 / retry、原始 PLC writer、SQL 或全局生命周期。runtime 创建每 flow 独立 async task，单流一轮结束再等 interval，最大重叠1，无 tick 积压 / 追赶。HTTP 与 timer 等待不占 PLC 队列位置 / 执行位；某 flow 输入 / HTTP 错误不终止独立 flow。

复用 HttpClient / SocketsHttpHandler；禁环境代理、redirect、应用层 retry，只有 HTTP200 / JSON Content-Type / UTF-8、完整 ≤4096 bytes 的 body 可解析。仅 GET，无 POST / auth。固定为恰好七个 key 的两个变体：

```json
{"schema_version":1,"source_id":"demo01-feed","ready":false,"command_id":null,"value":null,"issued_at_ms":null,"expires_at_ms":null}
{"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":"shape-only-001","value":42,"issued_at_ms":1792742400000,"expires_at_ms":1792742430000}
```

上例历史时间只说明形状。ready 必须 JSON bool；ready=false 四个业务字段必须 null；ready=true ID 合法非空、value 为有符号16位范围的 JSON 整数，拒绝 bool / float / string / null。source 匹配配置，重复 / 未知 / 缺 key、非法 UTF-8 / JSON / 过深结构拒绝，不拿默认值、上轮值或缓存触发写。

来源 `issued_at_ms` / `expires_at_ms` 为严格 signed64 Unix 毫秒整数，保持 epoch 语义。必须 `0 < expires-issued <=60000`、issued≤now+1000、now<expires、now-issued≤input_max_age_ms；安全算术拒绝溢出。接收时和原身份持久后、入队 / 出队及真实发送闸门前复核。原来源 deadline 取 `min(expires, issued+input_max_age)`，以接收时 wall / monotonic 锚点转换一次，排队不刷新。每 flow 保留原 ClockAnchor，wall 相对 monotonic 漂移绝对值 >1000ms 锁存 `clock_invalid`、停止本次运行新写，独立读继续；不重建锚点掩盖跳变。重启仍按原来源时刻判断，不复活旧命令；测试用受控 TimeProvider / 屏障，不改宿主系统时间。

INT 仅标准 DB 绝对 byte offset 的两字节 signed16 大端补码；五值 -32768 / -1 / 0 / 42 / 32767 分别 8000 / FFFF / 0000 / 002A / 7FFF。DB1..65535、声明大小2..65536、offset0..65534且offset+2≤size；fixture 还独立检查实际16字节块边界，邻接A5不变。配置声明不证明真实 PLC 块大小。直接读取通过同一 owner 返回独立 typed Sample（request / flow / session 身份、short value、quality、真实 sampled_at）；错误不返回旧好值。不提供 BOOL / REAL / DINT、多 item、I/Q/M、符号 / 优化 DB、CPU 操作或安全设置。

## 7. PLC 选型、统一 owner 与协议预检（R05–R06）

### 7.1 只读选型依据及明确选择

S7netplus 是此前讨论的候选，不是获准必须采用的产品驱动。本轮只读核查 [官方仓库](https://github.com/S7NetPlus/s7netplus)、[异步读写源码](https://raw.githubusercontent.com/S7NetPlus/s7netplus/main/S7.Net/PlcAsynchronous.cs)、[响应检查](https://raw.githubusercontent.com/S7NetPlus/s7netplus/main/S7.Net/PLC.cs) 与 [NuGet 0.20.0](https://www.nuget.org/packages/S7netplus/0.20.0)：所读 main 的公开 byte read / write 不暴露原 ACK proof，内部 RequestTsdu 私有；read 检最小长度 / status，write 检 status[14]，不能由此证明当前 ref / function / 完整结构匹配。Async 取消是 cooperative。**这是所读源码的静态结论，未执行 0.20.0 失败预检，也不将 main 当 NuGet 原包逐字节证明。** 上游 tests 使用 Snap7 server 的说明不证明本任务 / 真实 PLC 兼容。

**r1 选择本工程极小 managed S7 INT adapter**，基于 .NET Socket / NetworkStream 原生 async + CancellationToken + dispose / await 完成；没有 native PLC 库、P/Invoke、第三方 fork / reflection / 私有 transport 接入或产品 driver child。该选择让当前请求 reference、原 ACK、TCP生命周期与总期限可见，同时新增有限握手 / codec 正确性责任，必须通过下述独立 oracle / 真实协议 gate。不是通用 PLC 驱动产品；若必要边界不可满足，记录 dev_blocked 返回 PM，不临时换栈 / 放宽 T3 / 加运行代理。

协议范围仅：单 TCP 长连接、TPKT v3 / reserved0 / 16位大端长度、COTP CR/CC 与单 DT（EOT）、S7 SetupCommunication、单 item ReadVar04 / WriteVar05、DB area84、BYTE element count2 表示两字节 INT。支持 TCP 自身拆段 / 慢字节的有限收齐；不支持 COTP 分片、跨 PDU、多 item / 连续大块 / 其他功能。COTP / Setup 按明确支持形状校验类型、长度、连接 reference / TSAP / negotiated PDU；协议外变体稳定拒绝并退役会话。本产品请求并只接受本子集的240字节协商PDU，其他值记unsupported并停止该session；任何单帧 TPKT 总长硬 cap512，在读完4字节头后先验声明长度再分配，绝不按不可信大长度分配。COTP / Setup 字段依据 [ConnectionRequest](https://raw.githubusercontent.com/S7NetPlus/s7netplus/main/S7.Net/Protocol/ConnectionRequest.cs)、[TsapPair](https://raw.githubusercontent.com/S7NetPlus/s7netplus/main/S7.Net/Protocol/TsapPair.cs) 与独立报文 / 交叉校验固定，不复制上游完整实现或宣称覆盖全部协议。

每个新 session 的 Setup 使用ref1，后续业务ref从2递增到65535，同session不复用；耗尽前无未结工作时正常换会话，原命令身份 / dispatch_count 不变。response先验证：协议32、ACK_DATA03、reserved0000、当前ref匹配、global class/code均0、parameter长度2 / 当前04或05 / count1；Read data长度6 / payload总20 / returnFF / transport04 / bitlength16 / 两字节；Write data长度1 / payload总15 / 唯一returnFF。TPKT、COTP、S7声明与实际长度完全一致，不容短包 / 附加字节。只有内部校验器产生的 typed WriteAck 可进入 T3，不用任意 `validated=true`、Task完成或连接状态替代。

每 job 至多发送一个 ReadVar / WriteVar。第一份错 ref / op / 长度 / negative ACK、超时、断连立即失败并退出 ready；旧 IO 及 socket 实际结束前不启动替身 / 下一 job，迟到正确 ACK 不补成功、不转给下一个请求。进入写 send 调用后所有不能证明匹配正 ACK 的错误保守 unknown；negative ACK 同样不自动重发。能证明从未进入调用者才 canceled / expired。

### 7.2 R05：统一 owner、队列与真实开始

每 PLC 一个 owner task 持有一个 current session / generation 和 bounded FIFO；所有 flow 的读写共享其唯一通路，最多一个实际 driver call。无 native同步调用或 `Task.Run` 阻塞调度器 / 每请求新连。相同点多流逐个独立采样，连接复用不等于共享快照、业务去重或写动作互斥。

owner 状态 `disconnected / connecting / ready / recovering / stopping / stopped`。等待 ready 有界，flow 不各自 connect / retry；一个恢复周期最多5次连接，间隔250 / 500 / 1000 / 2000ms，耗尽后 cooldown10000ms，可取消；成功 IO 后清连续失败，恢复不重放可能已发写。unknown 只阻止重叠写资源，不终止不相关读。

队列接纳 / 取消 / dispatch 采用可观察的单一 phase / permit 规则。T2 commit 是保守派发意图，**不是 driver_call_started**；只有实际进入当前 session 的发送调用才计 health.in_flight=1，等待队列 / T2 / 调用前屏障为0，匹配完成或真实关闭后为0。队列满、ready / queue 超时和 dispatch IO 超时使用不同 error key。测试覆盖合法等待超过 queue 截止的“等待+IO总和”但各阶段合法，及出队 / 调用前原 ClockAnchor 再检查。

### 7.3 R06：独立 oracle、夹具与先行 gate

夹具仅本工程 `tests/FieldFlow.Fixture`：C# synthetic HTTP、透明 TPKT proxy、managed S7 标准 DB1 / 16字节 INT 子集 server，三个 listener 均只绑定127.0.0.1：**33102（proxy / 产品入口）、33103（server）、33880（HTTP）**。不占用 Rust31102 / 31103 / 31880 或 Python32102 / 32103 / 32880，不用102 / wildcard。冲突则停止并报告，不杀占用者 / 自动换端口。proxy两段TCP属于同一透传会话；仅测试会临时允许独立client，正常复用窗口只有一session。

fixture parser / response builder 不调用产品 S7 encoder / validator 来生成预期或自证正确。两项独立 oracle 均必需：

1. 将下表既有真实 loopback 帧及来源 / hash 固化为 C# 自有 `tests/golden` 常量 / 数据，expected bytes / offset / 长度人工可审阅，测试不在运行时读取旧工程 / bundle。来源 [FF-001 gate-1.json](../FF-001-dual-runtime-demo01/evidence/r3-dev/gate-1.json)，SHA256=`bcae313dee187b35294ead7c512f7bfceac83797205c4f76b7edc27850d24e77`。这些是原 native Snap7 本地协议证据，不是现场帧；只作有限 oracle，原 QA 不替 C# 验收。
2. 在 test 项目单独引用精确 S7netplus0.20.0（独立 lock、PrivateAssets=all），通过其公开连接 / 两字节 ReadBytesAsync / WriteBytesAsync 对 C# fixture 做正常握手、五个 INT / 相邻字节读取的真实交叉检验。该 test client 不参与产品 T3 / negative ACK 证明；预检记录实际 NuGet包 / TFM / hash / 版本，不能拿源码宣传替 pass。产品停止后再交叉读，避免污染一session统计；不运行 Rust / Python / DS 服务。

| 固定 oracle | 全帧 hex / 总字节数 |
| --- | --- |
| Read DB1 offset0 / ref0001 | `0300001f02f080320100000001000e00000401120a10020002000184000000` /31 |
| Read ACK value42 / ref0001 | `0300001b02f0803203000000010002000600000401ff040010002a` /27 |
| Write DB1 offset0 value42 / ref0001 | `0300002502f080320100000001000e00060501120a1002000200018400000000040010002a` /37 |
| Write ACK / ref0001 | `0300001602f0803203000000010002000100000501ff` /22 |

golden 的ref0001是原捕获样本；本产品Setup后业务ref2的 expected 变体在数据中显式列出，不修改来源帧 / 依赖被测 encoder动态生成。逐字段负例及每长度截断用固定变体；fixture响应/计数与产品解析分别核对。S7netplus正常互操作无法证明所有错误ACK检查，仍须下述产品故障注入。

**精确 r1 批准后的第一个技术 gate：** 先锁定 restore / build、codec单元与fixture交叉检验，再用正式共用 Execution / state / owner 做真实HTTP+S7 normal Read/Write，以及坏ref读、已应用写后错function / 坏ref / 短ACK / 丢ACK。写actualWriteVar=1、unknown1 / confirmed0，同身份≥10轮与原库重启不重发；独立读回42+A5不升级unknown。保留 request / 原ACK / 实发ACK、实际计数 / 内存、三表只读导出、真实退出 / PID / 端口；整个gate外层120秒含回收，单次仍遵循各预算。失败保留证据并停在本范围 blocker；通过才继续完整runtime / 文档 / copy，不把gate当全部AC或 QA。

人工 fixture 必须输出结构化 fixture_ready，固定本次新生成 command_id / 原issued / expires=issued+30000 / 值42 / source demo01-feed；重复GET不刷新。先完成restore / build / init、准备第二终端，再启动fixture并在默认input age10秒内运行一种模式；dry / execute用两个独立新教学场景。人工入口只提供现有单命令，故障 / 多读流控制在tests内部，不建管理面板 / 任意点表 / 通用PLC模拟器。Ctrl-C / SIGTERM正常关闭，生成自身protocol.json，包含确切PID、会话 / ReadVar / WriteVar / applied计数、有限trace / 内存及join / ports结果。

## 8. SQLite 身份、事务与恢复（R07–R08）

### R07：本地状态与受控持久化

C# 独占自身state-dir的跨进程文件锁，锁持有到最后自有工作真正结束；第二writer拒绝。implementation固定 `csharp`、schema_version=1，mode / instance不可变，拒绝R/P库或不明schema。SQLite只属于本实例执行事实，不是Backend业务库，也不与其他语言互换；本任务只经显式synthetic init建新schema，不迁移现有库。

最小三表：store_meta（schema / implementation / mode / instance / UUID / created_at）；commands（PK source_id+command_id、flow / canonical target范围 / config与payload hash / INT值 / 原issued与expires / state / dispatch_count0或1 / run及request身份 / error / ack_kind / created_at / updated_at）；command_events（单调seq、命令FK / run-request / old-new / reason / 有限摘要 / created_at，仅追加）。规范摘要用SHA256固定影响命令含义的字段，不能hash原JSON字段顺序；不保存原body / secrets / URL query。

`(source_id, command_id)` 不含run / retry / mode。首次合法意图后，flow、物理目标、值、原来源时间及语义配置不可变；同ID同摘要复用原状态，同ID不同任何语义为identity_conflict，保留原意图并暂停该写flow，不覆盖时间 / 目标 / payload。idle不建命令。

T1同一短事务插入pending及event，commit成功才可准备动作。取得有界队列位置并确认mode / TTL / stop / capacity / audit / unknown后，T2 CAS pending->in_flight、dispatch_count0->1并append event，commit后才能交付唯一permit；提交失败不遗留可执行请求。owner在实际发送前再检查原期限 / ClockAnchor / stop。T3只有匹配typed正ACK后同事务in_flight->confirmed、ack_kind=s7_protocol及event；确认提交失败保留in_flight / unknown、闭新写闸门，不回pending。SQLite与外部写无法原子提交，T2不是发送证明。

采用本地文件系统、DELETE journal、synchronous=FULL、foreign_keys=ON、page_size4096，主文件64MiB上限；不用EF / 自动迁移 / 网络共享盘。状态与必要审计由**单个专属持久化worker / thread**串行持有，bounded提交队列≤32；不在flow调度路径直接同步SQL / flush。busy_timeout≤500ms，事务工作期限1000ms，短事务无网络IO；排队 / timeout / 迟到结果有请求身份，不产生重复事务 / dispatch。

微软 [SQLite async说明](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/async)明确 ADO.NET async 方法实际同步。`WaitAsync` / 取消awaiter不证明native SQLite或文件flush停止；持久化timeout立即闭新写闸门、停止新提交，保留最后持久事实，观察真实worker完成 / join，期间不释放writer锁或开替身。r1不承诺任意磁盘 / 内核挂死的硬取消；正常退出必须真join，未join记shutdown_incomplete / 非零，不能报告resources_released。受控故障用busy / 有界delay / 写失败验证此区别；外层harness只可清理自身确切PID且记验证失败，不包装成正常退出。

### R08：状态与 unknown 物理阻断

| 状态 | 含义 / 允许处理 |
| --- | --- |
| pending | 已持久意图、dispatch0；重启后须当前GET再次给同摘要且原TTL有效才可继续，不离线重放库存意图。 |
| in_flight | dispatch1、可能已开始 / 生效，非成功；重启在任何新下发前统一转unknown并追加恢复event，哪怕崩溃可能发生在send前。 |
| confirmed | 当前匹配S7正ACK且T3 commit；重复 / 原库重启永不再写同身份，非PLC业务接受、工艺完成或物理exactly-once。 |
| unknown | 可能进入send后超时 / 断连 / 坏或丢ACK / 进程崩溃 / T3无法证明；保留原身份与证据，读回、重连、下一tick / 新ID / 重启不解除或重发。 |
| expired / canceled | 可证明未进入真实写send的到期 / 停止 / 拒绝；保留dispatch_count，不重置后重试。无法证明未发送则unknown。 |
| simulated | 仅dry_run库的would_write，dispatch0、无ack_kind / confirmed；不影响execute库身份 / 进度。 |

每次接纳及派发检查原库全部unknown的规范endpoint / rack-slot / DB / 字节区间，重叠就阻写；不能换flow / source / plc alias / commandID绕过。unknown只阻重叠写，独立读继续。已confirmed不因之后日志失败倒退。无reset / clear / replay / unknown人工改状态CLI，无自动回读确认；真正业务握手 / 人工处置另立范围。

dry_run对合法would_write经同owner做一次目标INT只读采样以验证读链，持久状态仍仅simulated，WriteVar必须0；execute显式且只用独立匹配库。切换C# / Rust / Python / CA writer需停旧端、核对pending / in_flight / unknown和confirmed进度、确认唯一资源 / 业务效果归属再交接；不同可写库不提供跨实例 / 跨主机fencing，不因失联自动接管。

## 9. 新时间合同、日志、健康与容量（R09）

C# 从首次数据写入即遵循根Asia/Shanghai合同：所有自身日历字段（SQLite created_at / updated_at / event、JSONL timestamp、sample / health日历字段及inspect）由统一时间工具输出RFC3339 **+08:00**，不随OS时区变化。不要使用SQLite UTC `CURRENT_TIMESTAMP`默认值。Unix来源毫秒不加八小时，monotonic timestamp / duration按自身语义；必要事件时间、采样时间、状态更新时间、health刷新分别命名，缺真时间不伪造。按不同系统TZ运行的等价时刻测试须同+08结果。旧R/P的UTC日历及历史不迁移 / 重写。

产品stdout与state-dir/runtime.jsonl逐行单个JSON对象，至少 timestamp / event / implementation=csharp / run / instance、适用flow / command / request / session / target、result、old-new、duration / error_key。必要事件含 process/config/init、flow状态、owner连接/退避/恢复、intent / permit / driver_call_started / ack / unknown / 冲突、容量或审计闭闸、stop_gate_closed / task与worker join / resources_released / shutdown_complete或incomplete。普通读不逐tick刷日志，5秒health聚合；无health HTTP listener / GUI。

checked持久sink用同一持久化worker确保整行写、flush / 必要sync成功回执。副作用前状态与必要审计落盘 / stdout失败不下发；副作用后sink失败不抹掉confirmed或重发，保留最后持久in_flight / unknown / confirmed并停新写。日志队列有界，不吞IO错误、不靠无损承诺或ILogger调用返回推断落盘。stdout阻塞 / sink期限同样不等于底层worker已终止，按R07处理，必要stderr仅有限脱敏错误。

单行≤4KiB、文件≤5MiB、最多4备份 / 总25MiB；启动不截旧日志。commands上限10000、events上限100000；events≥90000、主库≥48MiB、磁盘可用<256MiB或身份达上限暂停新副作用，保留恢复余量；主库硬64MiB、含journal状态占用上限128MiB。不自动淘汰去重身份 / unknown / confirmed或清库续跑。测试可降阈值 / 注入写失败，不填满真实磁盘。

health至少含每flow starting / running / recovering / blocked / stopping / stopped、最近迭代 / 成功与连续错误，每owner状态 / queue_depth / 实际in_flight，pending / unknown计数、clock / audit / capacity健康；区分运行中与业务健康，idle非错误。状态 / 审计故障阻新副作用，不应终止独立PLC读 / 缓存健康快照。

## 10. 正常停止与故障退出（R10）

ConsoleLifetime / 显式停止token处理Ctrl-C及本机SIGTERM：先以与真实send开始同一线性化闸门关闭全部owner新接纳 / 新dispatch，再取消所有尚未开始队列 / 调用前屏障请求。各owner同时获停机通知；已开始IO在剩余单次 / global截止内完成或cancel + dispose socket，await该任务真实结束。必要保守unknown / 最后状态持久化后，await所有flow / owner / HTTP工作、关闭SQLite / 日志并真join持久化worker。只有全部完成才resources_released / shutdown_complete、exit0。

默认一个15000ms全局shutdown预算，不按flow / PLC / worker重复加期限；config关系见R03。无参help不装配Host，不启动任何线程 / 服务。退出2为CLI / config / 缺库 / metadata错误，运行故障 / unresolved unknown / persistence失败 / shutdown_incomplete退出1；错误key区分，不用正常退出摘要遮蔽unknown。因故障dispose连接不等于物理撤销已接收写。

正常产品不创建driver child；测试harness / fixture / crash场景创建的自有child必须逐个实际wait / reap，记录exact PID和session / socket / task结尾。父进程强杀后的OS连接消失与原库in_flight->unknown由独立harness证明；不能声称被杀进程完成了join。阻塞worker未结束、协议操作只取消了waiter、任一自有task / child仍活时均不得称已释放。外层故障清理只对记录的自有确切PID，强杀记失败cleanup、不杀端口占用者 / 同名进程。

## 11. 手册、教程与本机 publish（R11–R12）

C# 自身 README / PLAN / catalog / USER_GUIDE / BUILD 中英等价，独立复制后拥有全部必要步骤，不以父 / 兄弟手册为运行前提。总FF手册加入第三列 / 读者路线；不修改两旧工程文档或改写FF-001 / FF-002状态。

USER_GUIDE 包含：依赖 / SDK来源与锁准备、目录 / CLI / 配置对象、状态 / 日志路径、无参help、先init再fixture、分终端dry / execute / inspect / 正常停止 / exact PID和端口核查、原TTL与10秒input age关系、原库重启 / unknown / 单writer交接。不同shell不共享变量；记录PID的shell负责wait与后续检查，fixture退出后立即捕获自己的退出码，不能拿空PID / ps权限错误当进程消失。

app可用方法表必须对应最终源码：路径 / typed参数 / async返回 / error key / 生命周期owner / 最短用例，至少Demo01一次、配置Flow / Plc / IntTarget、GET / strict parser / Intent、ExecutionService.ApplyAsync、独立ReadInt16Async / Sample、ClockAnchor / TimeProvider、Stop、inspect / health / 日志。写必须经ExecutionService；raw S7 / owner内部write / SQL不作为应用快捷API。不得虚构已发布SDK。

新增同能力 `Teaching01` 教程给完整app / YAML，并按最终C#显式注册方式逐文件讲清：新增Flow类、kind校验、DI / factory或switch注册、runtime派发、配置身份与目标冲突、实际需要的locale / CODE_INDEX接线。不做assembly扫描 / 自动发现。教程只在本任务私有复制品应用，再build / 校验 / 两模式最小真实运行；正式产品只注册demo01。无需新文案则说明locale不改；需要时中英对称，不修改兄弟工程。

BUILD区分源码开发的dotnet run / DLL、test-only fixture和产品publish：首轮必验 **osx-arm64 self-contained目录**，显式 `PublishSingleFile=false / PublishTrimmed=false / PublishAot=false`，无ReadyToRun / 全静态承诺。实际检查apphost / DLL / deps / runtimeconfig / managed依赖 / native SQLite / .NET runtime / locale / sample / notices清单，copy整个必要publish目录到新位置实跑help及本地两模式，状态 / 日志仍在外部私有路径；产品不携test依赖 / fixture或运行库 / 真实配置。不只生成产物就称可运行。

| 目标 | 本 r1 所需证据 / gate |
| --- | --- |
| macOS arm64 / osx-arm64 | 当前宿主实际locked restore / build / tests / start / self-contained publish / copy run / 正常资源释放必需；记录真实OS与native依赖。 |
| Windows x64 / win-x64 | .NET部署候选；给native SDK / RID / SQLite资产 / 信号与文件锁适配检查及明确命令，均not_run。本轮不下载Windows SDK、不跨publish、不宣称Windows已交付，不安装Windows Service。 |
| Linux x64 / linux-x64 | 同样给RID / OS系统库 / native SQLite / lifecycle前提与命令，均not_run；本轮不跨publish或原生运行。 |

后两行未来命令必须说明先在另批目标任务冻结相应RID依赖图 / lock、再locked restore / publish和目标机运行；不能把当前osx lock假定全RID可用。无需现在为三平台制造产物。官方依据：[global.json](https://learn.microsoft.com/en-us/dotnet/core/tools/global-json)、[NuGet lock](https://learn.microsoft.com/en-us/nuget/consume-packages/package-references-in-project-files#locking-dependencies)、[publish命令](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-publish)、[发布模式](https://learn.microsoft.com/en-us/dotnet/core/deploying/)。它们不替代本工程实测。

发布 / 更新不能覆盖现有执行库 / 日志；先停writer、核对schema / implementation / mode / instance和未决命令再替换文件。r1无安装器 / 签名 / 自动更新 / 服务托管 / 离线交付包 / 迁移工具 / 现场部署。C# SQLite包含native组件，managed PLC实现不等于整个应用无native或全静态。

## 12. 获批后的拟执行入口与证据（R13）

以下是尚未创建 / 执行的命令合同，不是运行记录。Development可在不改变能力 / 风险 / AC的前提下落实最终path，并在tasks与手册给精确可复制argv；参数需经所pin SDK自身help核对。首个lock生成与所有网络准备只在批准后进行，不用隐式restore掩盖改锁。

新私有root记作F，项目记作P；均须替换为执行者创建并输出的真实绝对路径，不能照抄字母 / 尖括号。dotnet为F/sdk/dotnet；先核官方归档SHA512再解压，验证 `dotnet --info / --version / --list-runtimes`。已校验且冻结的SDK是工具链，Development / QA可只读复用同一份官方SDK（像共用已有编译器），也可各自准备同pin副本；各自CLI home / NuGet可写cache / bin / obj / publish / state / fixture进程必须独立，不复用DEV构建产物或可写运行环境。只读普通包cache可受控复用，不能因此借兄弟项目环境。SDK归属 / hash及QA依赖写入handoff，QA完成前不得自动回收；批准范围内这些必要准备无需新的范围批准。配置私有CLI home / NuGet cache后，从P运行：

```bash
"$FF_DOTNET" restore FieldFlow.slnx --configfile NuGet.Config --use-lock-file -r osx-arm64 -p:SelfContained=true
"$FF_DOTNET" restore FieldFlow.slnx --configfile NuGet.Config --locked-mode -r osx-arm64 -p:SelfContained=true
"$FF_DOTNET" build FieldFlow.slnx -c Release --no-restore -r osx-arm64 -p:SelfContained=true --disable-build-servers
"$FF_DOTNET" test tests/FieldFlow.Tests/FieldFlow.Tests.csproj -c Release --no-build --no-restore -r osx-arm64 --filter TestCategory=ProtocolGate --logger trx --results-directory "$FF_RUN_ROOT/results-gate"
"$FF_DOTNET" test tests/FieldFlow.Tests/FieldFlow.Tests.csproj -c Release --no-build --no-restore -r osx-arm64 --logger trx --results-directory "$FF_RUN_ROOT/results-full"
"$FF_DOTNET" publish src/FieldFlow/FieldFlow.csproj -c Release --no-restore -r osx-arm64 --self-contained true -p:PublishSingleFile=false -p:PublishTrimmed=false -p:PublishAot=false --disable-build-servers -o "$FF_RUN_ROOT/publish-osx-arm64"
```

私有环境变量用FF_DOTNET / FF_RUN_ROOT等任务名称，不改HOME / CODEX_HOME。首次restore显式包含本机self-contained所需runtime pack图，build / publish参数与已restore图一致；若SDK要求进一步显式属性，Development在同范围修正并记录，不以implicit restore改锁。首次生成锁后，重试与复制 / QA使用locked-mode，确认锁未变化；test有真实数量 / 名称及断言，0-test成功不算通过。ProtocolGate外层120秒、各故障case含回收≤30秒，完整协议 / lifecycle harness总上限240秒；超时报告失败并只回收自有资源，不能删失败case / 延长输入TTL取绿。

人工入口需最终提供等价于：

```bash
"$FF_DOTNET" run --project src/FieldFlow/FieldFlow.csproj -c Release --runtime osx-arm64 --no-build --no-restore -- --help
"$FF_BIN" state init --synthetic --mode dry_run --state-dir "$FF_RUN_ROOT/dry/state" --instance-id ff-csharp-demo01
"$FF_BIN" state init --synthetic --mode execute --state-dir "$FF_RUN_ROOT/execute/state" --instance-id ff-csharp-demo01
"$FF_FIXTURE" --config "$FF_PROJECT/config/loopback.yaml" --evidence-dir "$FF_RUN_ROOT/dry/fixture"
"$FF_BIN" run --config "$FF_PROJECT/config/loopback.yaml" --state-dir "$FF_RUN_ROOT/dry/state"
"$FF_BIN" state inspect --state-dir "$FF_RUN_ROOT/dry/state"
```

execute另起自己的新fixture场景，产品run加`--execute`并使用execute/state；fixture与runtime分终端 / 有harness编排，须先ready再run，正常stop / wait / inspect / report / exact PID / 三口rebind按手册顺序执行。`FF_BIN` / `FF_FIXTURE`须明确取自本工程实际构建位置，不能把dotnet包装PID当产品PID。测试产品stdout直接调用自身apphost或`dotnet FieldFlow.dll`；无参help从新空cwd另验。

单工程独立复制排除bin / obj / SDK / caches / results / publish / 状态 / 日志 / 真实配置，保留自身manifest / locks / source / tests / golden / locale / docs；直接父目录只有project、无父运行清单 / 兄弟项目。使用同pin工具链（可只读复用已校验SDK）和独立build输出 / 私有state / 自有fixture，执行locked restore / build / test / start / publish必要步骤；公共官方包可使用当前任务私有cache。源码候选 / 正式工作树 / copied project逐文件hash一致，不能只在副本交付变更或以副本结果替代正式入口。

Development的tasks须记录逐AC命令 / cwd / OS / CPU / SDK / runtime / lock / 包hash、真实stdout / stderr / exit、失败 / rework、源码与copy / publish清单hash，实际合成状态 / ACK / 时间 / 计数证据，以及全部自有目录 / task-thread / PID / listener / 构建服务器资源清单。必要原始输出与脱敏报告持久化至本bundle真实evidence，不能只留/tmp；不提交SQLite / SDK / 二进制 / 日志敏感内容。未执行必需检查是not_run / blocker，不填pass。

## 13. 验收标准

全部是 FF-003 C# 自身验收。轻量unit覆盖纯规则 / codec，涉及并发、协议、状态恢复和停止的AC必须有真实loopback / 产品证据，不以mock成功或旧FF QA替代。可合并互补场景，不机械复制FF-001全部历史矩阵。

| AC | 必须可观察的结果 / 对应需求 |
| --- | --- |
| AC01 | 正式与单工程复制均自身SDK10.0.403 / net10.0锁定restore / build / 实际测试 / start成立，manifest / lock / source / golden与候选一致，无父 / R/P / DS服务或可写状态依赖；SDK、runtime、NuGet / native资产实测可追溯，缺环境不报pass。（R01/R02/R13） |
| AC02 | 分层 / 薄Program、typed配置与对称CLI成立；空cwd无参 / 两语help早返回零IO；未知 / 缺字段、重复key / ID / endpoint、重叠写目标、非法预算 / 类型 / schema / implementation / mode / instance拒绝；init不覆盖，普通run缺库不建文件 / schema，inspect只读。（R02/R03/R07） |
| AC03 | ProtocolGate在120秒内含实际回收通过：固定黄金帧逐字节 / 单元截断与字段拒绝、自有fixture独立parser、test-only S7netplus0.20.0真实交叉校验成立；产品正常与坏ref读、已应用写的错function / 坏ref / 短ACK / 丢ACK得到规定状态 / 计数，原库重启不重发。gate不充当完整AC。（R06） |
| AC04 | 正常demo01真实HTTP GET→typed→state→WriteVar→停止后独立S7读回，五INT值正确且邻接A5保持；非法类型 / 值 / 声明和实际块范围拒绝。default dry真实GET / read而WriteVar0、仅simulated / confirmed0；execute只在匹配独立库，一次正ACK+T3才confirmed。（R03/R04/R07/R08） |
| AC05 | idle、非200、错误Content-Type / UTF-8 / JSON / 七键 / source、超body、stale / future / 长TTL / 时间溢出均零新写；同ID不刷新源时间，入队后expiry / input age到期零发送；排队与真实send前受控wall ±漂移>1000ms均clock_invalid、原锚点锁存，读继续；日历+08不影响Unix / monotonic判断。（R04/R09） |
| AC06 | 相同身份≥10轮 / 原库重启只1次实际写；payload / time / target / flow immutable冲突保原记录。T1后未派发、T2后发送前崩溃、server已应用丢ACK或父强杀、ACK后T3失败、confirmed后sink失败均真实按合同恢复 / 不重发；unknown按物理重叠阻断新ID / source / flow / PLC alias，独立读仍继续，回读不升级unknown。（R07/R08） |
| AC07 | 同PLC至少3独立测试读流，各≥20独立request / sample，正常S7session1、driver最大在途1、正确归流；同时一个GET延迟1200ms流与100ms间隔读在8秒完成≥20次、相邻成功间隔≤500ms，同慢flow重叠≤1、无tick补跑，HTTP不占PLC执行位。（R04/R05） |
| AC08 | FIFO queue1000ms / IO1200ms、每响应600ms的两请求都成功，第二总耗时可>1000ms但等待 / 实际IO各合法；ready / queue timeout与IO错误分开。T2与调用前屏障health.in_flight=0、真实ACK等待=1、完成 / 关闭=0；source / ClockAnchor在出队及send前复核。（R03/R05） |
| AC09 | 缺席 / 断连 / 静默握手 / 分段慢字节真实总期限含socket关闭 / IO结束：connect≤配置+500且≤3500ms、IO≤配置+500且≤5500ms，不只waiter返回；owner统一有界退避，旧操作 / socket结束前不换session。坏 / 旧ref / 错op / negative / 长短 / 附加 / late ACK不变good或confirmed，不重发；近ref上界维护无复用。（R05/R06） |
| AC10 | 队列与send前屏障各有待请求时stop线性化闭闸，闭闸后这些请求WriteVar0；在途IO保守结果，默认15秒内flow / owner / HTTP工作真实结束、持久化worker真join、store / 日志 / sockets关闭。父强杀仅独立harness观察OS释放 / 原库恢复；exact PIDs absent、33102 / 33103 / 33880无listener且rebind。超时 / 强杀 / 未join如实失败，无resources_released假象；端口冲突保留占用者。（R05/R07/R10） |
| AC11 | stdout / 轮转文件逐行JSON与稳定字段 / 脱敏成立；必要审计前失败零写、事后失败保最后状态。降低阈值证明轮转 / 容量闭新写不淘汰身份；同步SQLite / flush的受控busy / delay / 错误不阻PLC读，timeout不冒称worker已停。各SQLite日历 / JSONL / sample时间一致+08且不随主机TZ，epoch / 单调期限不机械平移。（R07/R09） |
| AC12 | 中英自身手册 / BUILD / 索引齐备、配置 / 方法 / owner / error对应源码；两个独立shell可照做default两模式 / inspect / stop / PID核查；Teaching01在独立副本按逐文件C#注册接线、build与两模式最小协议运行通过，正式产品仅demo01；Python / Rust / C#定位与未来按需单实现一致。（R02/R11/R13） |
| AC13 | 本机osx-arm64 self-contained目录publish真实成功，产品无test S7net / fixture依赖；发布清单含实际.NET / SQLite native / locale / 配置 / notices范围，新位置copy后help和本地dry / execute / 正常停止通过，既有state / logs不覆盖。Windows / Linux命令及未实测gate准确，未冒称全静态 / AOT / 全平台交付。（R01/R12/R13） |
| AC14 | approved spec / tasks / 精确candidate / diff / 逐AC证据及资源handoff完整；旧FF001 / FF002 / ARCH和R/P所有正式文件保护hash不变，任务外dirty不归因 / 不覆盖。实际fresh-context Verification独立创建checklist / verdict，qa_passed只交Human Owner终验，所有现场 / 托管 / 长稳 / 部署gate保持。（第2节/R13） |

## 14. 风险、排除、回退与 handoff

| 风险 / 取舍 | 本轮处理 / 未授权边界 |
| --- | --- |
| 自有managed协议实现可能与真实S7变体不同 | 明确小子集、严格拒绝、黄金帧与test-only第三方交叉检验、先gate；失败保留 / dev_blocked，不放宽ACK或改为通用驱动。有限loopback不证明Siemens型号 / 固件 / 安全 / PUT-GET / 非优化DB现场兼容。 |
| 测试client与fixture共同错误 | fixture不用产品codec作oracle；固定既有原帧、独立第三方正常访问和产品真实负例分别给证据。交叉检验也不替产品的关联 / TTL / T3验证。 |
| SQLite / 文件sync不可硬取消 | 专属有限worker隔离调度，超时停新写 / 不开替身，真实join才报释放；任意磁盘 / 内核挂死不在硬取消保证内。实际环境不满足必要正常 / 受控故障验收即blocked / failed，不掩成通过。 |
| SQLite与PLC无原子事务、unknown会停写 | 保守持久身份 / 物理重叠阻断，无自动重发 / 回读确认 / 删库绕过。真正设备握手、接收方幂等、人工处置后续另批。 |
| 本机缺SDK / NuGet与native资产兼容未测 | 本r1可审阅批准中明确官方私有准备与hash / lock；不能下载 / restore即报具体blocker。工具链存在 / 包页面兼容不算build / run。 |
| C# .NET / Windows候选被误解为三平台已交付 | 首轮只本机macOS arm64实测 / publish；Windows / Linux原生运行、服务安装 / 托管 / 信号锁语义、现场升级另gate。 |
| 三工程各自状态与本地锁不提供全局writer归属 | 不并行执行同资源业务效果；切换先停旧 / 核未决与confirmed。跨库 / 跨主机fencing、自动接管 / 双活后续另批。 |
| 新+08时间与旧UTC混淆、并行dirty / 旧资源被误改 | C#新库新时间工具 / 原epoch语义；不导入或迁移R/P历史。任务级allowlist / hash保护，旧失败库 / tmp不动。 |

排除demo02 / POST / auth、BOOL / REAL / DINT、其他协议 / 点表导入、通用插件 / DSL / GUI / CA / AI、共享采集缓存 / 快照、Backend / DS / 真实第三方接入、生产库 / 真实PLC / 工艺动作、跨语言状态互换、unknown处置 / 归档工具、服务 / 安装器 / 签名 / AOT / 静态单文件、跨目标publish、现场 / 长稳 / 生产容量资格、发布 / 部署 / Git操作。以上后续gate不阻本轮有限合成基线，但不得以deferred覆盖本轮必需AC缺口。

回退只限本任务明确归属的源码 / 文档diff，不能自动覆盖并行编辑；先停新dispatch、保留原state / logs / identities与失败证据，不反向写PLC、不删库重新跑、不启用未通过gate路径。首次C#schema不兼容时拒绝run，今后改变schema另显式维护范围。临时copy / SDK / cache / build / 新synthetic库均列归属；必要证据先持久，QA / Owner还依赖的保留。Human Owner最终验收后，active coordinator核对归属 / 占用 / 后续依赖再安全回收自有资源；PM / QA不代清理旧任务。

**PM -> Human Owner：** 审阅精确 **FF-003 r1** 的独立C#工程、上述有限managed S7子集与测试oracle、官方SDK / NuGet私有准备、新synthetic schema、三个固定loopback端口、AC01–AC14、本机publish / 教程及风险。当前精确范围批准pending；本轮只spec / 必要机械导航，所有C#下载 / 实施 / build / test / schema / protocol / publish均not_run。

精确批准后，主协调器实际选择`development`；Development创建tasks、先工具链与协议gate、再完整runtime / 独立copy / 教程 / publish、逐AC自检与精确candidate / 资源handoff。真正developer_handoff后，协调器实际选择`verification`, `fork_turns="none"`；其读取approved spec / 完整bundle / 实现与diff / 锁 / 原始证据独立验证，只写checklist与自己的真实附件，不静默修实现。QA通过仍只交Human Owner最终验收。

开发可自主解决批准边界内常规类名 / 小文件拆分 / 注册接线 / 受影响bugfix；只有范围 / allowlist / 验收 / 风险 / 模式实质变化才回PM新Revision及重新批准，不把每个普通实现选择变成新gate。当前不启动Development / Verification，不启停其notifier窗口。

| 日期 | Revision | 真实阶段 |
| --- | --- | --- |
| 2026-10-27 | r1 | PM根据C#实现请求建立可审阅draft；只读核验规则 / 完整相关bundle / 手册 / primary来源，精确Human Owner批准pending。SDK / 包 / C#运行与全部AC未执行，无DEV完成 / QA verdict / Owner终验。 |

PM文档自检（2026-10-27）：只读辅助Python断言exit0，唯一FF-003 / r1 / draft / namespace / root元数据、AC01–AC14、10个现存本地链接、fence / 无尾空白、四份golden帧字节数及TPKT长度、原来源hash均一致。协调器baseline中784份既有FF文件逐项SHA256无变化；本bundle仅spec.md，C#工程 / tasks / checklist仍不存在。`git diff --check -- field-flow/plans/FF-003-csharp-runtime-demo01/spec.md` exit0；新文件未跟踪，该命令本身不替代前述内容断言。不曾运行C#下载 / restore / build / tests / schema / fixture / protocol / publish，无新服务 / child / 状态库或PM自有临时根。这是PM静态检查，不是Development自检、独立QA或全仓治理通过。最终SHA256在对外handoff给出，不在本文件自引用。

此spec的拟执行命令、候选技术选择和旧FF证据均不构成本任务运行通过。
