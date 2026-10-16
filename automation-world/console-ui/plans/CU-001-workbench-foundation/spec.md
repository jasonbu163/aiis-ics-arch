Task ID: CU-001
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved CU-001 r1 on 2026-10-15; Development may start within the CU-only allowlist
Task Namespace: aiis-ics-arch
Classification: root
Capability: 独立 Console UI 设计工作台与可由各 Agent 编译消费的公共 UI 源码
Owner: Console UI
Acceptance Chain Reference: CU-001 r1 / Human Owner 范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
Related Task: ARCH-AW-001; ARCH-AW-002（背景关联，不继承批准、状态或验收）
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-001：Console UI 工作台基础

## 1. 目标与现状

将 `automation-world/console-ui/` 整理成可独立运行的轻量 Tauri UI 设计工作台，同时拥有一份纯 Vue / TypeScript / CSS 公共源码；CU 工作台自身也消费这份公共源码。
首版服务于壳层、组件、主题和语言的设计预览，不建设配置生成平台或现场运维产品。

2026-10-15 只读核对：CU 仍使用 `aiis-ics-control-agent` package/Cargo 身份、`com.aiis.ics.controlagent` identifier 与 15190/14190 端口；README/PLAN 仍描述冻结 CA。
现有 `App.vue`、壳层和状态模块依赖 `runtimeSnapshot`；Rust 启动与命令注册仍包含 PLC、数据库和 headless 采集能力。
`src/ui/`、`src/workbench/` 与本任务 bundle 在草案创建前不存在。PM 草案阶段未构建、测试或启动应用；本次仅记录范围批准并交接 Development。

## 2. 归属与交付边界

- CU 的 README 定义身份与消费入口，CU PLAN 管自身实施，唯一 owning bundle 是当前目录；不在其他工程复制本任务。
- AW PLAN 管总体阶段和跨工程依赖，并链接各工程 PLAN/spec；不批量移动历史根 `plans/`。
- 当前 CU 是允许改造的 CA 来源副本；不宣称改造后仍保持旧 CA 冻结源码不变，也不新增另一套长期 CAF 冻结工程。
- 现有相邻 `control-agent/`、DAA、SMA 及原 DTB TSS 不属于本任务修改范围。
- AW 白皮书、总体原理与业务设计归 ARCH-AW-002 所在会话；本任务不重写这些文档。

## 3. 范围与需求

### R1. 独立应用身份与最薄桌面壳

- 默认 package/Cargo/bin 为 `aiis-aw-console-ui`，Rust lib 为 `aiis_aw_console_ui_lib`；product/window 名为 `AIIS AW Console UI`，identifier 为 `com.aiis.aw.consoleui`。
- dev/preview 分别固定 15193/14193 且启用 strictPort；package scripts、Vite 与 Tauri devUrl 保持一致，`frontendDist` 仍指向 CU 自身 `dist`。
- Rust 只承担桌面窗口启动所需能力；PLC/DB/headless 逻辑必须脱离启动、命令注册、自动发现 bin 和构建依赖，去掉其专属运行脚本与功能开关。
- 允许在下述 allowlist 内移除失效源码、样例配置及专属依赖；如暂留历史文件，明确其不可执行、未编译的来源用途，不伪称当前能力。
- CU 正常启动不读取工业 `.env`/YAML、不连接 PLC/DB、不发起采集或后台轮询；保留 pnpm、Cargo 和现有 Element Plus 技术链。

### R2. 公共 UI 源码合同

- 唯一公共代码入口为 `src/ui/index.ts`，公共样式入口为 `src/ui/styles/index.css`；公开组件、类型及必要主题资源由这些入口可达。
- 首批限于复用现有视觉的布局壳、侧栏、顶栏、卡片、动作按钮与状态胶囊；必要时保留小型信息/指标展示，不抽取万能组件。
- 公共组件通过 props、slots、events 接收导航、标题、状态和动作；状态类型是展示合同，不携带 PLC/DB/runtime 业务模型。
- `src/ui/` 的直接及传递依赖不得进入 CU `App.vue`、main、workbench、IPC、Tauri API、Rust、`runtimeSnapshot`、业务状态、CU 私有 locale 实例或 `.env`。
- 主题与语言由消费端显式提供或安装；公共层不自动创建第二个 Vue/i18n 应用，也不隐式读写 CU 偏好或挂载到 `#app`。
- 公共样式提供可复用 tokens/主题和组件样式；工作台页面布局、样例专属 CSS 与全局应用启动留在私有层。

### R3. 使用同一组件的设计工作台

- `src/workbench/` 放 CU 私有预览页、设计样例和组合逻辑；`App.vue` 只作应用组合入口，工作台从公共入口导入同一份 UI。
- 提供壳层预览、少量组件展示、状态切换和参数预览；交互仅改变当前设计预览，不保存业务配置、不模拟真实设备操作。
- 所有样例区域清楚标识“设计样例 / Design sample”，使用固定演示状态和参数；不把样例包装成在线 Agent 或实际采集事实。
- 保留日/夜主题与 zh-CN/en-US 切换；用户可见文案进入对称 locale，公共组件接受消费端文案或显式安装的公共资源。
- 仅主题、语言等 UI 偏好使用 `cu.*` 本地键；不读取/迁移 CA、DAA、SMA 旧键，不加入 SQLite、服务端或业务配置持久化。

### R4. 源码消费教程与本地示例

- CU README pair 与 `src/app/README.*` 纠正身份、源码层次、运行命令、历史来源和公共入口；明确旧采集能力已从 CU 执行链脱离。
- 新增 `examples/source-consumer/` 最小 Vue/Vite 消费示例，仅从公开代码/样式入口引用 CU；不导入私有组件或工作台。
- 文档给出依赖版本要求、源码路径/别名、样式、主题和语言的安装方式；Vue、Element Plus 与使用到的 i18n 依赖由消费端解析为同一实例。
- 消费端把源码编译进自己的 `dist`；源码编译时需要可访问公共源码，安装/运行已构建产物不要求 CU 在线、CU 进程或 CU 的运行依赖目录。
- 首版只交付源码导出；不建设根 monorepo/workspace、npm 发布流水线，不实际接入或修改其他 Agent。

## 4. 写入 allowlist 与角色分工

以下路径全部相对 `automation-world/console-ui/`，仅允许完成 R1–R4 所需修改；Human Owner 最新批准明确本轮只改 CU：

| 表面 | 获批后的允许范围 |
| --- | --- |
| 应用与依赖 | `package.json`、`pnpm-lock.yaml`、现有本地 `pnpm-workspace.yaml`、`vite.config.ts`、`tsconfig*.json`、`index.html` |
| 新公共层与工作台 | `src/ui/**`、`src/workbench/**`、`examples/source-consumer/**`；示例的 README pair 归 CU PLAN 管理 |
| 现有前端解耦 | `src/App.vue`、`src/main.ts`、`src/env.d.ts`、`src/components/**`、`src/layouts/**`、`src/console/**`、`src/locales/**`、`src/styles/**` |
| CU 旧业务清理 | `src/services/runtimeSnapshot.ts`、`src/app/{runtime,collection,plc,gates}/**`，仅移除/脱离旧执行链与搬出可复用展示 |
| 桌面壳与旧 runtime 清理 | `src-tauri/{Cargo.toml,Cargo.lock,build.rs,tauri.conf.json}`、`src-tauri/capabilities/default.json`、`src-tauri/src/{main.rs,lib.rs}`、`src-tauri/src/{bin,commands,config,domain,infrastructure,services}/**` |
| 工业样例清理 | `.env.example`、`config/plc_points.yaml`、`config/plc_snapshot_policy.yaml`；仅处理 CU 副本，不改真实 `.env` 或现场文件 |
| 稳定说明 | `README.md`、`README.zh-CN.md`、`src/app/README.md`、`src/app/README.zh-CN.md` |
| CU 任务索引 | `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`，由主协调机械同步 |

PM 本轮只写本 `spec.md`。Development 按已批准 r1 创建本任务 `tasks.md`；fresh-context Verification 在 `developer_handoff` 后创建 `checklist.md`。
主协调只机械同步 CU `PLAN.*`、CU `plans/README.*` 的相关链接、聚合状态及下一 gate；它们不承载第二份任务正文。根 `CODE_INDEX.md` 与 AW 索引本轮不改，外部汇总由总体会话处理。
生成的依赖、`dist`、Cargo target 与 Tauri 产物保持未跟踪；验证临时产物优先放 `/private/tmp`，不手改生成 schema 或既有图标。
禁止修改上述范围以外的实现、其他任务 bundle、根 AGENTS/README/PLAN/ROADMAP/CODE_INDEX、AW README/PLAN/catalog/总体文档、其他 Agent、backend、frontend-js、真实配置或 Git refs。

## 5. 验收标准

| ID | 对应需求 | 最小可复核结果 |
| --- | --- | --- |
| AC1 | R1 | package/Cargo/bin/lib/identifier 与标题一致；15193/14193 配置一致且 strict；CU UI 偏好仅使用自身键 |
| AC2 | R1 | 静态检查启动链、注册命令、bin 与依赖：无可执行 PLC/DB/headless 采集路径；正常启动不加载工业配置或建立外部连接 |
| AC3 | R2 | 公共代码/样式入口完整，传递导入满足隔离边界；壳层已不依赖 RuntimeSnapshot，工作台确实使用公开组件 |
| AC4 | R3 | 一次聚焦界面检查确认壳层、组件/状态、参数样例可展示，设计样例标识清楚，主题和语言切换生效 |
| AC5 | R1–R3 | CU `pnpm build` 通过类型与生产构建；`cargo fmt --manifest-path src-tauri/Cargo.toml --check`、`cargo check --manifest-path src-tauri/Cargo.toml --locked` 通过 |
| AC6 | R1 | 当前平台完成一次 Tauri 构建（可用 `pnpm tauri build --no-bundle`）和一次原生启动确认；不要求签名、安装包分发或三平台矩阵 |
| AC7 | R2/R4 | 本地示例消费者类型/构建通过；CU 未运行时，其自有构建产物可展示公共壳/组件及主题/语言，不依赖 CU App/IPC/Rust |
| AC8 | R4/治理 | README pair 身份、命令与消费教程一致；文档链接有效，必要 CU 索引与任务元数据正确，diff 不触达其他工程 |

Development 记录实际环境、命令、退出码和一次启动/界面证据；Verification 独立复核对应结果，必要时仅复跑有疑点的项目。
验收维持必要构建、一次启动与公共入口消费；不要求全 CA/TSS 功能回归、多 cwd 污染矩阵、完整端口或截图矩阵、长时间 GUI 轮询、复制 hash 清单或为本次批准记录构建软件。
原生构建或启动缺少环境时如实报告阻塞，不能用浏览器预览冒充原生证明；独立 QA 通过后仍待 Human Owner 最终验收。

## 6. 风险、恢复与排除项

- 旧壳/组件含 CA 类型、翻译键和样式耦合；解耦只做到当前公共入口和工作台所需，不扩展重做设计系统。
- CU 当前目录未受 Git 跟踪；实施前确认旧源码来源版本和用户增量，并为拟清理文件保留必要恢复依据。不能默认依靠 `git restore`，也不要求新增冻结副本、全量 hash 或 Git 提交。
- 回退只针对本任务实际修改的 CU 内容和 CU 索引条目；发现并发修改先核对归属，不覆盖其他会话工作。恢复依据和保留资源由 Development 记录。
- 当前目录/运行合同与 AW 总体文档仍可能描述旧 CA；由各 owner 协调归属，文档差异不自动扩大本任务写入范围。
- 排除完整浏览器拖拽低代码、任意源码在线编辑、配置保存/代码生成平台、SQLite 业务配置、新 AW API、Rust Flow Core、真实 PLC/DB、生产部署和发布。
- 实际 Agent 接入、公共库版本发布、更多组件或工业业务页另立任务；CU 工作台可运行不表示 AW 业务链已贯通。

## 7. Handoff、批准与修订记录

后续 Development 加载 `frontend-ui`（设计与工程边界）、`i18n-workflow`、`desktop-tauri`；清理继承 Rust runtime 时加载 `rust-runtime`，关键源码头部说明需要时加载 `code-document-indexer`；治理文档继续遵循 `project-governance` 与 `aiis`，根索引保持本轮禁写。
Human Owner 于 2026-10-15 明确批准精确 `CU-001 r1`，包括默认应用身份、15193/14193 端口、CU 内遗留采集能力脱离/清理及源码共享和样例工作台边界。批准原话：

> 可以，批准 CU-001 r1，按这个范围开始实施。只改 CU，先完成设计工作台和公共组件出口，其他 Agent 不动。验证能构建、能启动、能引用就行，不用做全量回归。

按该批准将原草案的根 CODE_INDEX/AW 索引写入例外收回，本轮实际写入全部限制在 CU 内。下一 gate 为命名 Development 实施并交接 fresh-context Verification；PM 不代做技术实现或验证，Human Owner 最终验收仍在 QA 之后。
若上述选择、allowlist、验收或风险发生实质改变，PM 修订新 Revision 并重新提交批准；未指定的组件内部组织由 Development 在已批准边界内确定。

| 日期 | Revision | 记录 |
| --- | --- | --- |
| 2026-10-15 | r1 | PM 创建范围草案；当时尚未获得 Human Owner 精确批准，未开始实施，未创建 tasks/checklist |
| 2026-10-15 | r1 | Human Owner 明确批准 CU-001 r1 开始实施；按原话收敛为只改 CU，根 CODE_INDEX/AW 索引本轮不改，验证维持构建/一次启动/公共入口消费 |

执行合同：[根 AGENTS](../../../../AGENTS.md)、[Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)。本任务归属 [CU PLAN](../../PLAN.md)，总体依赖见 [AW PLAN](../../../PLAN.md)。
