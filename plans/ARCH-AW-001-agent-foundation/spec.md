Task ID: ARCH-AW-001
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved ARCH-AW-001 r1; Development authorized, tasks.md pending Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: AW Agent 工程迁移、冻结基线与双应用隔离初始化
Owner: Automation World
Acceptance Chain Reference: 本 spec 精确 r1 范围批准 -> Development tasks.md -> fresh-context Verification checklist.md -> Human Owner final acceptance
Related Task: aiis-ics-arch::ARCH-MULTI-001; aiis-ics-arch::CA-CONFIG-001; aiis-ics-arch::ARCH-BE-003

# AW Agent 工程前置初始化

## 1. 目标与批准状态

将 CA 整体迁入 `automation-world/control-agent/`，完成最小路径适配和本地原生验证后冻结；从该冻结基线复制 DAA；从 DTB TSS 的适用源码复制 SMA，原 TSS 完整保留。AW 的双语 README/PLAN 统一拥有后续演进，并同步根入口和 ROADMAP 的当前事实。

这是 **S2 工程前置初始化**，可以在 S1 API 合同完成前进行。交付是三个可分别构建、原生启动且配置隔离的桌面工程；S1 合同、AW 事实 API 和最小业务闭环继续由后续任务完成。ARCH-BE-003 尚未落地不阻塞本任务，也不能由本任务宣称 S2 闭环完成。

Human Owner 已于 2026-10-14 明确批准这份精确 r1，并授权按该范围开始实施。当前交接 Development 创建 tasks.md，后续角色文档继续按 gate 创建；原 draft 的待批准状态保留为第 9 节历史事实。ARCH-MULTI-001 是相关路线文档任务，本任务不继承其文档批准、QA 或最终验收。

## 2. 只读来源盘点

以下为 2026-10-14 的源码事实，不是构建或启动通过证据；Development 实施前必须重新确认。

| 来源 | 当前基线与关键入口 | 本任务处理 |
| --- | --- | --- |
| 本仓库 CA | 本仓库 HEAD `363b297bffe65e020108f5504766b4fb1ec3b381`；`git status --short -- control-agent` 无输出 | 迁移当前源码，记录完整文件清单和 dirty 指纹；根目录其他大量既有改动受保护 |
| DTB TSS | `/Users/jason/Desktop/DreamCode/data-twin-backend/twin-state-studio/`；DTB HEAD `a87c107c10e8d9d9d3e389e357b50d203d2aebf7`；该子目录 status 无输出 | 只读复制适用文件，不写入 DTB；实施前复核 HEAD、dirty 和来源文件 hash |
| CA 工程/配置 | `package.json`、`src-tauri/Cargo.toml`、`tauri.conf.json`、`src-tauri/src/config/mod.rs` | 内部 `frontendDist=../dist` 可随工程整体搬迁；配置会检查 cwd、其 parent 和 manifest 附近 `.env`，不能把这个搜索规则原样当成新应用隔离 |
| CA 运行 | `src-tauri/src/lib.rs`、`main.rs`、`bin/aiis-ics-control-agent-runtime.rs`、`infrastructure/logging.rs` | 保留 CA 的独立桌面/现有无界面入口、原身份和默认门禁；日志也需纳入路径检查 |
| TSS 装配/配置 | `src-tauri/src/app.rs`、`config/mod.rs`、`config/runtime_startup.rs`、`src/App.vue`、`src/app/registry.ts` | 当前会向上搜索 `.env`；启动偏好位于 Tauri app-data；缺文件时 Simulation/Mapping auto-start 均 false；旧 profile 和业务模块不能随复制成为 SMA 默认状态 |
| TSS 构建/帮助 | `scripts/build-help-resources.mjs`、`package.json`、`src/app/help/` | 原帮助脚本依赖 DTB 根 docs，且生成 TSS/backend 两端资源；不得原样作为 SMA 构建前置或跨仓写入入口 |

已读根 AGENTS、README/PLAN pair、ROADMAP pair、根任务 catalog、CA/TSS README/PLAN 与上述入口。CA 和 TSS 使用不同 Vue/Vite 依赖基线，本次分别保留适用锁文件，不统一升级依赖或抽取 shared UI。DTB 根 MIT LICENSE 的版权与许可说明随适用源码保留。

## 3. 目标结构与计划归属

```text
automation-world/
├── README.md / README.zh-CN.md
├── PLAN.md / PLAN.zh-CN.md
├── plans/README.md / README.zh-CN.md
├── control-agent/                 # 搬迁验证后冻结的 CA
├── data-acquisition-agent/        # 从冻结 CA 复制的 DAA
└── semantic-mapping-agent/        # 从适用 TSS 源码复制的 SMA
plans/ARCH-AW-001-agent-foundation/
└── spec.md                        # 唯一 owning bundle；后续按阶段补角色文件
```

- AW README 解释三者归属、CA 冻结、复制来源、独立启动命令及当前/目标能力；AW PLAN 统筹后续阶段，根 PLAN 保留跨仓摘要与入口。
- 本次启动任务已在根 `plans/` 创建，保留为唯一 owning bundle。AW PLAN 用 `../plans/ARCH-AW-001-agent-foundation/spec.md` 引用它，AW catalog 用 `../../plans/ARCH-AW-001-agent-foundation/spec.md` 引用它，不复制第二份 spec。
- 既有 CA PLAN 在冻结前注明历史兼容基线和 AW 归属；DAA/SMA README 提供自身工程入口。新应用初期由 AW 统一拥有生命周期，不复制 TSS/CA 的任务状态或另开同任务 PLAN/bundle；若以后成为独立 PLAN owner，另行按需建立模块治理套件。
- 不搬走、不批量改写根或外部来源的历史 plans；来源 QA/验收只能作为 provenance，不能变成本任务的验证结论。
- 本次不建立空 `shared/console-ui/` 或 AWC SDK。CA 风格统一壳与共享 UI 保持后续 ROADMAP 目标；初期 SMA 保留适用 TSS 界面。

## 4. 需求

### R1. 来源、文件与迁移基线

1. 在 `tasks.md` 记录两个仓库 HEAD、branch、源目录 status、纳入文件清单及 hash、排除清单、现有 dirty 文件保护办法和迁移前验证结果。复制以实施时明确的来源快照为准，不假定 HEAD 等于当前全部工作树。
2. CA 搬迁保留完整源码、适用锁文件、图标、公开配置及说明；本地 ignored 配置/产物先盘点并原样保全，不输出秘密内容、不遗失、不导入 DAA/SMA。
3. 新复制只纳入适用源码、构建声明/锁文件、必要通用文档和脱敏夹具。排除 `.git`、`.codex`、`.agents`、`node_modules`、`target`、`dist`、缓存、生成 schema/cache、真实 `.env*`、本地数据库、日志、客户 inputs/outputs、真实资源及历史 plans。适用 `.env.example` 可以重新脱敏纳入。
4. 新应用不得依赖 DTB checkout、原 CA/TSS 目录或其 node_modules；不得通过软链接绕过复制、配置隔离或来源清单。

### R2. CA 搬迁、验证与冻结

1. 整体搬至 `automation-world/control-agent/`；仅调整确有影响的工程路径、当前文档链接、默认文件解析及迁移说明，不改产品 identity、功能、PLC/数据库合同或原采集行为。
2. 在关闭外部 I/O 的隔离环境中，先比较迁移前后源码检查、配置解析、控制台初始状态与原生启动。重新构建，不能用旧路径编译的二进制作为新路径证明。
3. 验证满足 CA 迁移门槛后，在 `tasks.md` 形成 freeze receipt：来源、最小适配 diff、最终源码文件/hash manifest、验证命令与结果、时间及尚未验证的现场边界；CA README/PLAN 的冻结声明应在 receipt 前完成。
4. DAA 从该 receipt 对应的 CA 源码复制。之后重新核对 CA manifest 不变；不让 CA 引用后续变化的 DAA/SMA/shared 源码。冻结是维护约定，不表示停止当前 CA 运行或切换生产链路。
5. 冻结后若必须实质修改 CA，停止继续写入，由 PM 修订范围并取得解除冻结/新 Revision 批准，再重新验证并出具 receipt；不以迁移名义长期同步两份源码。

### R3. DAA 继承边界

保留 CA 的通用采集、解码、诊断、日志、控制台及现有无界面入口；仅做名称、配置、存储和启动隔离。旧 raw/latest 数据库快照代码可以临时保留，默认 PLC/数据库/端点探测/自动采集门禁关闭，README 明确尚未接入新 AW 事实/配置 API。此次不把数据库直写改造成 HTTP 上传，不替换现有 Projection writer。

### R4. SMA 可执行复制清单

下表是 r1 已批准的功能过滤决策；不是无差别 `cp`。只在新 SMA 副本作公共归属和独立启动所需裁剪，不修改原 TSS，也不重写映射算法。

| 来源区域 | 纳入/排除与依赖处置 |
| --- | --- |
| 工程声明、Tauri 壳、图标、通用组件/样式、locale | 纳入并改 SMA 身份；保留现有界面和各自锁定依赖。新文案保持中英文对称 |
| `src/app/twin-facts/` 的事实合同/列表、API Materials、Target APIs、值规则、Mapping 配置/预览及 API-first 运行诊断 | 纳入通用 HTTP 功能与纯计算逻辑；保留现有参数位置、类型、版本、lease/receipt 语义，不硬编码客户服务、设备、sourceKey 或场景；无配置时诚实显示未连接 |
| Rust `domain/mapping_runtime/`、`services/mapping_runtime/`、对应 command、通用事实/Simulation HTTP 逻辑与 runtime 类型 | 纳入适用实现与纯本地回归。Simulation 作为继承的测试辅助默认关闭，不要求本轮运行；客户/SQL 关联类型与注册从依赖闭包裁掉 |
| `src/app/connection/` | 只保留通用 Backend bootstrap、OpenAPI 和适用 HTTP 诊断；移除 MSSQL 管理/直连、客户场景/设备 current-state 操作及固定 DTB WebSocket 路径，不保留它们的 API facade 或 IPC 注册 |
| `src/app/device-management/`、`src/app/device-catalog/`、`src/fixtures/deviceCatalog.generated.json`、`inputs/device-catalog/`、catalog 生成脚本/客户 fixture | 排除；从 App、registry、navigation、help、测试和 import 闭包中解除依赖，不靠隐藏菜单留存调用面 |
| Rust legacy `services/projection/`、`services/service_mapping/`、设备能力 Service、`infrastructure/db/`、旧 projection profile/registry 与相关 commands/probes | 排除 direct-MSSQL 及直写业务表路径；从 crate/app 装配、managed state、command 注册、类型引用、Cargo 依赖和测试闭包中解除。不得留下可调用的 legacy run-once/start/resume/初始化 IPC |
| 帮助阅读器与 `scripts/build-help-resources.mjs` | 可保留最小通用阅读器和本地双语说明，覆盖身份、连接前提、映射边界；排除客户操作正文/资源、backend 帮助管理写入和跨 DTB 双端生成脚本。构建检查只读 SMA 自身输入，不写 backend 或外部仓库 |
| TSS README/PLAN、历史 bundle、外部 docs 引用与 QA 状态 | 不作为 SMA 当前正文/状态照搬；保留来源与许可归属，重写必要工程入口。原 TSS 历史完整留在 DTB |

Development 在写入前将表中选择落实为逐文件 copy/exclude manifest 和最小内部依赖调整计划。若发现无法在此边界内解除客户/SQL 依赖，或需大规模改造/丢失通用映射能力，返回 PM 新 Revision；不得静默扩成完整 TSS 重构或退役原 TSS。

### R5. 身份、端口与状态隔离

以下为 r1 的新应用身份和端口分配，原 CA/TSS 保持既有身份。

| 表面 | CA 保留值 | DAA 新值 | SMA 新值 |
| --- | --- | --- | --- |
| Tauri identifier | `com.aiis.ics.controlagent` | `com.aiis.aw.dataacquisitionagent` | `com.aiis.aw.semanticmappingagent` |
| product/window title | `AIIS ICS Control Agent` | `AIIS Data Acquisition Agent` | `AIIS Semantic Mapping Agent` |
| npm/Cargo package、GUI bin | `aiis-ics-control-agent` | `aiis-data-acquisition-agent` | `aiis-semantic-mapping-agent` |
| Rust lib / 现有 headless bin | `aiis_ics_control_agent_lib` / `aiis-ics-control-agent-runtime` | `aiis_data_acquisition_agent_lib` / `aiis-data-acquisition-agent-runtime` | `aiis_semantic_mapping_agent_lib`；不新增 headless 入口 |
| Vite dev / preview | `15190` / `14190` | `15191` / `14191` | `15192` / `14192` |
| localStorage prefix | 保留原 CA keys | `daa.` | `sma.` |
| 新 env namespace | 保留 `CONTROL_AGENT_*` | `DAA_*` | `SMA_*` |

1. 同步 package scripts、Tauri devUrl、Vite config、Cargo default-run/lib/bin/import、产品文案及日志身份；dev/preview 端口均固定且冲突时失败，不自动换端口。
2. DAA/SMA 仅显式读取本应用配置；禁止搜索父目录/仓库根 `.env`，禁止自动读取原 `CONTROL_AGENT_*`/`TWIN_STATE_*` 进程变量、旧 CA/TSS app-data 或 localStorage，也不自动迁移旧启动偏好。
3. YAML 仅为本应用脱敏运行配置；JSON 仅承载既有启动偏好/技术清单等原有职责，不新增本机业务事实数据库。相对路径锚定本应用已知根，不以任意 cwd 捡取别的应用文件。
4. 各应用的 config/app-data/log/output/临时导出路径分别解析并记录；DAA/SMA 的本机持久路径使用各自 identifier/目录，运行产物不进入源码。验证使用独立临时根，不写或清空用户原 CA/TSS profile。
5. `runtime-startup.json` 等新应用首启状态保持 auto-start=false；SMA 默认 Backend 未配置，不沿用 `127.0.0.1:8144` 的 DTB 连接。上次 CA/TSS 已保存的 auto-start=true 不得使新应用启动任何循环。

### R6. 原生启动与无外部 I/O

1. 三应用分别构建并原生启动，再同时启动，检查实际进程、窗口身份、Tauri IPC、本地配置解析及互不覆盖。纯浏览器预览只能作为补充，不代替原生证据。
2. 新应用初始外部 I/O 关闭，覆盖 Rust 和 WebView 中的自动 HTTP/WS、PLC、DB、Simulation、Mapping 和帮助更新；触发按钮/IPC 时也须在外部调用前拒绝或提示未配置，不能仅依靠菜单隐藏。CA 验证通过临时显式关闭门禁保持原行为。
3. 用临时脱敏配置/纯本地夹具验证类型、配置来源、映射请求组装及隔离拒绝；不创建长期 mock API，不连接现有 DTB backend、真实 DB/PLC 或真实 Target，不向业务系统写入。
4. 本轮不新增后台常驻/OS 自启语义：关闭窗口和显式退出均结束该实例及其本任务子进程/循环；检查可再次启动、端口释放、其他应用继续运行。若既有 CA 行为与该验收不一致，先记录事实并返回 PM，不能借机改写 CA 生命周期。
5. 日志/证据包含应用身份、配置来源、门禁状态与结果，禁止记录密钥、完整连接串和业务原值；沿用适用日志能力，缺少必要启动/拒绝证据时只补对应事件，不开展全量日志改造。

### R7. 文档、索引与 ROADMAP 同步

双语 AW README/PLAN 和 catalog 说明唯一 bundle、CA 冻结、DAA 临时继承旧实现、SMA 源码过滤及后续 S1/S2 gate；根 README/PLAN/AGENTS/INITIALIZATION/CODE_INDEX 与 `.gitignore` 仅更新实际迁移影响。根 README 现有 CA Cargo 验证命令需使用正确 `--manifest-path`。

ROADMAP pair 按实施事实更新 CA 位置/冻结、DAA/SMA 初始化状态及前置阶段关系；保留未来 API 上传、业务闭环、CA 风格壳和 shared UI 目标。不得把工程完成写成新事实链路、aw_ 表、PW 迁移、现场运行或全部 S2 已完成。

历史任务、旧版本说明、API `/control-agent/` 路径及原有合同身份不作全局替换。发现与此次迁移无关的既有失效链接/历史状态只记录，不顺手修复或复活旧合同。

## 5. 写入 allowlist 与排除面

| 路径 | r1 已批准允许的写入 |
| --- | --- |
| `control-agent/**` -> `automation-world/control-agent/**` | 目录整体搬迁和 R2 必要适配；freeze receipt 后禁止新增实质改动 |
| `automation-world/data-acquisition-agent/**` | R1/R3/R5/R6 限定的 CA 副本、身份/配置隔离、必要回归和 README |
| `automation-world/semantic-mapping-agent/**` | R1/R4/R5/R6 清单内的 TSS 适用副本、最小依赖裁剪、隔离、回归和 README |
| `automation-world/README.md`、`README.zh-CN.md`、`PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md` | AW 身份、统一生命周期索引与唯一根 bundle 的相对引用 |
| 根 `AGENTS.md`、`README.md`、`README.zh-CN.md`、`PLAN.md`、`PLAN.zh-CN.md`、`ROADMAP.md`、`ROADMAP.zh-CN.md`、`INITIALIZATION.md`、`INITIALIZATION.zh-CN.md`、`CODE_INDEX.md`、`.gitignore` | 仅迁移事实、AW 归属、正确命令/路径与新应用运行产物忽略；保留其他任务 dirty 内容 |
| `plans/README.md`、`plans/README.zh-CN.md` | 本任务机械索引；只链接已存在角色文件 |
| `plans/ARCH-AW-001-agent-foundation/spec.md` | 仅 PM/Human Owner 的范围与批准记录 |
| 同 bundle `tasks.md` / `checklist.md` | 批准后 Development 创建 tasks；developer_handoff 后 fresh-context Verification 创建 checklist |
| `/private/tmp/ARCH-AW-001-*/` | 归属明确的配置、夹具、构建/启动证据与临时清单；脱敏摘要回写所属角色文档 |

所有 DTB 文件只读。禁止修改 backend API/Model/Alembic/业务配置、现有业务模块、PLC 点表语义、公共 HTTP 合同、其他任务 bundle、角色/workflow/skills 配置。不得复制真实配置/数据/资源、建立第二 bundle、抽取 shared UI、恢复 legacy/Celery、替换 Projection、发布/tag/push、部署、启动 Docker、执行真实设备/数据库/Target 操作。新增路径或实质风险超出表格时回 PM 修订。

## 6. 顺序与阶段门槛

| 顺序 | 必需结果 | 下一步条件 |
| --- | --- | --- |
| 0 | Human Owner 已批准精确 ARCH-AW-001 r1 | Development 创建 tasks 并按 r1 开始实施 |
| 1 | 源版本/dirty 指纹、保护清单、copy/exclude manifest、迁移前 no-I/O 基线 | 来源或 GUI 环境不足先记录 blocker |
| 2 | CA 整体移动、最小适配、重新构建及本地原生验证 | CA 迁移门槛通过 |
| 3 | CA freeze receipt 和源码 hash manifest | receipt 对应源码固定 |
| 4 | 从冻结 CA 复制 DAA，完成身份/配置隔离 | CA 冻结 hash 未变化 |
| 5 | 从 TSS 复制适用 SMA 源码，完成过滤/依赖处置与隔离 | DTB 来源 hash 未变化 |
| 6 | 三者构建、单独及同时原生启动、配置回归和无 I/O 检查 | R1–R6 证据完整 |
| 7 | 双语文档/ROADMAP/索引同步，DEV 自检与精确 handoff | 交出 diff、源码指纹、命令/退出码和限制 |
| 8 | fresh-context Verification 独立审计与复验 | checklist 给出真实 verdict |
| 9 | Human Owner 最终验收 | 源码基线接受；现场切换仍另行授权 |

CA 迁移失败时不冻结、不复制 DAA；SMA 独立性失败时不借用 DTB 路径绕过。原生环境不可用的必需项目保持未验证，并在 QA 阶段记 `qa_blocked`，不能自动改成 deferred/pass。

## 7. 验收标准与验证合同

| AC | 可检查标准 | 关联需求 |
| --- | --- | --- |
| AC1 | 两来源 HEAD/dirty、逐文件来源/排除与 hash、既有 dirty 保护记录齐全；原 TSS 前后相同；未复制真实配置/数据/客户工件 | R1/R4 |
| AC2 | 根 CA 工程整体迁入 AW，重新构建和原生 no-I/O 启动通过；原身份/功能合同保留，最小路径变更可追溯 | R2 |
| AC3 | freeze receipt 在 DAA 复制前形成；DAA 来源匹配该 receipt；交接时 CA hash 与冻结 manifest 一致 | R2/R3 |
| AC4 | DAA 保留通用采集/诊断与既有 headless 入口，可独立构建；默认外部门禁关闭，文档明确旧快照实现和新 API 未接入 | R3 |
| AC5 | SMA 保留通用 facts/targets/mapping/运行诊断；客户模块与 legacy SQL/IPC 从装配和依赖闭包排除；纯映射计算/请求组装回归通过 | R4 |
| AC6 | package/crate/lib/bin/product/identifier、dev/preview 端口及 localStorage keys 与表格一致；三实例同时运行无端口/状态覆盖 | R5/R6 |
| AC7 | DAA/SMA 从本应用 cwd、`src-tauri/` 与临时 cwd 启动均不拾取父/根 `.env` 或旧 CA/TSS env/profile；旧启动偏好为 true 的夹具不能触发新应用循环 | R5 |
| AC8 | 实际记录三者配置/app-data/log/output 绝对路径，互不读写；只操作临时 profile，用户旧 profile 与 TSS 文件 hash 不变；退出后端口/本任务进程释放 | R5/R6 |
| AC9 | 分别及同时原生启动有窗口、进程、IPC 和启动/门禁证据；默认/拒绝路径均没有 PLC、真实 DB、DTB Backend、真实 Target 请求；浏览器证据不冒充原生 | R6 |
| AC10 | 三应用前端与 Rust 适用检查通过或给出精确 blocker；SMA build/check 不访问 DTB/docs/backend 或跨仓写资源；构建独立于原 CA/TSS | R1/R4/R6 |
| AC11 | AW 与根双语 README/PLAN/catalog、ROADMAP、当前路径和忽略规则一致；唯一 root bundle；未来 S1/闭环/shared/现场门槛清晰；历史任务未批改 | R7 |
| AC12 | diff 与 allowlist 相符，tasks/checklist 权威与 gate 正确；fresh QA 复核来源/冻结/隔离/原生证据，Human Owner 最终验收独立记录 | 全部 |

验证环境为当前 macOS 宿主机、项目声明的 pnpm/Cargo 和可用 Tauri 原生 GUI。保留源码锁定版本，不为了验证升级生态。依赖安装用各工程锁文件；Agent 辅助依赖不得进入项目。当前平台验证不宣称 Windows/Linux、安装器签名、安装后运行或长期现场可靠性通过。

Development 将下列命令展开为三应用的真实路径、环境、退出码与输出摘要；CA 迁移前在旧路径做对应基线。不能为通过检查运行真实 ignored probes。

```bash
pnpm --dir automation-world/control-agent install --frozen-lockfile
pnpm --dir automation-world/control-agent build
cargo fmt --manifest-path automation-world/control-agent/src-tauri/Cargo.toml --all -- --check
cargo test --manifest-path automation-world/control-agent/src-tauri/Cargo.toml --all-targets --locked
# DAA/SMA 各自执行 install/build、同形 Rust 检查；SMA 另执行自身 check。
# 原生启动：各应用 cwd 内执行其 pnpm tauri dev / tauri:dev 入口，使用已审查临时 no-I/O 配置。
# 单独与同时启动分别取证；退出后核对进程、端口、文件变化及冻结/来源 hash。
git diff --check
bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh .
```

配置来源、旧偏好隔离和被删除 IPC 必须有针对性回归；不为纯目录/标题修改堆叠镜像实现的测试。AW 跨 owner 相对链接用定向链接/唯一性检查验证：旧 governance checker 只识别本地 `plans/*/spec.md` 时如实记录工具限制，不复制 bundle 或修改 checker 来凑通过。

主协调在本 spec 阶段报告根 governance checker 已因既有多 Revision 元数据和历史 catalog 问题退出 1；这些不是本任务新增问题，也不在本任务修复范围。本任务对新增 bundle、阶段元数据、链接和受保护文件单独检查，整体 checker 结果继续如实记录。

## 8. 风险、恢复与 handoff

- CA 搬迁改变 cwd 上级环境查找和编译路径；以迁移前后隔离配置解析与重新构建证明，不能只凭独立工程结构判断通过。日志目录须一起检查。
- SMA 过滤涉及 App/registry、Rust composition root、help 构建及测试闭包；只准完成公共边界和独立启动所必需的裁剪。源 TSS 旧 PLAN/历史 QA 与较新源码描述存在时序差异，以本任务实际文件基线与独立回归为准，不改写来源历史。
- 复制增加两份独立维护面；本任务不建立持续目录覆盖同步。后续复用修复按明确文件/能力移植并另立范围。
- 恢复依据迁移前清单与 CA freeze receipt，只处理本任务文件；不得 reset/覆盖其他 dirty 文件，不删用户配置。需要回退已运行应用或移动回旧路径时先列精确恢复动作并取得授权，不在本阶段执行生产切换。
- 必需原生 GUI、依赖或隔离能力不足时记录 `dev_blocked`/`qa_blocked` 与解除条件；不降低 AC、不用已通过前端构建替代原生证据。

PM 本阶段仅使用 aiis、project-governance 确定边界，不实施迁移或技术验证。Development/Verification 按各自角色加载：`desktop-tauri`（身份、构建、原生生命周期）、`rust-runtime`（配置/运行/IPC/日志）、`frontend-ui`（App/manifest/界面最小适配）、`i18n-workflow`（新可见文案）、`code-document-indexer`（关键头部与实际结构索引）及 `project-governance`（双语/索引）。只有触达点位解码合同时加载 `plc-point-mapping`；本 Revision 不授予修改该合同。后台 API/schema 工作需后续独立 spec 与 `backend-arch`，不由 PM/本任务代做。

Development handoff 必须给出精确 r1、冻结 CA manifest、SMA copy/exclude manifest、最终 diff/文件列表、no-I/O 配置来源、命令/退出码、原生证据、已知限制与临时资源。fresh-context Verification 读取完整 bundle 和当前工作树，独立验证后创建 checklist；PM 不写 DEV/QA 证据，不授予最终验收或平台 ACL。

## 9. 范围批准与修订历史

| 日期 | Revision | 事实 |
| --- | --- | --- |
| 2026-10-14 | r1 | PM draft：记录 Human Owner 确认的 CA 搬迁/冻结、DAA 继承、TSS 复制为 SMA、AW 统一管理方向；精确范围批准 pending |
| 2026-10-14 | r1 | Human Owner 明确批准精确 r1，授权按本范围开始实施；PM 仅更新批准状态与交接，既有范围和 AC 保持不变 |
| 2026-10-14 | r1 | Human Owner 澄清验证投入：工程可构建、独立启动及必要来源/配置隔离；SMA 聚焦映射 Runtime，不做完整 TSS 功能或临时 UI 验收；范围和 AC 不变 |

Human Owner 范围批准记录：**owner_approved，2026-10-14**。原话：

> 可以，批准 ARCH-AW-001 r1，按这个范围开始实施。CA 只迁移和做必要路径适配，验证后冻结；DAA/SMA 先完成工程初始化、配置隔离和独立启动验证，SQLite 配置及映射存储后续另立 spec。

本次批准涵盖 r1 的 SMA 适用源码过滤、初期 TSS 界面、R5 身份/端口、S2 工程前置分期及必需 macOS 原生隔离验证；SQLite 配置及映射存储按 Human Owner 明确意见后续另立 spec。若范围或 AC 实质改变，PM 更新 Revision 后重新批准。上述为范围批准时的交接记录；后续实施、QA verdict 和最终验收事实分别归属 tasks.md/checklist.md。

### 2026-10-14 验证执行口径澄清

Human Owner 原话：

> 软件搞过来，能跑就证明成功了，不用每个功能都去试，尤其是tss，只是需要映射相关runtime，前端ui都是要调整的。不用大费周章全部测试一遍

- 本轮验证聚焦可构建、独立原生启动及必要来源/配置隔离。SMA 聚焦映射 Runtime；继承的 TSS UI 是临时参考，后续调整，本轮不进行完整 TSS 产品、逐功能或 UI 验收/打磨。
- 已有 AC 的 Development 证据保留在 tasks.md，不为本次澄清重裁代码或新增测试轮次。fresh-context Verification 读取完整 bundle、来源/冻结清单和已有构建、启动、隔离证据，只做必要的定向复核，不再次执行全套或逐功能回归，也不为临时 UI 追加逐项试用、截图或优化。
- 这是既有 r1 工程初始化范围内的验证执行方法澄清，未新增或改变 AC、范围及 Revision，无需再次范围批准。原独立 Verification -> checklist verdict -> Human Owner 最终验收流程继续；既有证据和真实未验证边界保持如实记录。
