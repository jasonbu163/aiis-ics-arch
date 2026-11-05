Task ID: SMA-001
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Human Owner; exact SMA-001 r1 scope approval pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch.aw.sma
Classification: root
Capability: SMA HTTP 映射工作台接入 CU 公共界面，并清退事实生产、模拟与帮助中心能力
Owner: AIIS Automation World / SMA 模块 Human Owner
Acceptance Chain Reference: 本 spec §10 的 SMA-001 r1 精确范围批准 -> Development tasks.md / developer_handoff -> fresh-context Verification checklist.md -> Human Owner 最终验收

# SMA-001：CU 接入与 SMA 职责收敛

## 1. 目标、身份与当前 gate

SMA 面向大量同类 HTTP API → HTTP API 映射。近期业务为：从 Backend 读取事实，按字段绑定、常量及现有必要类型转换组包，再调用业务 API。本阶段统一既有工作台的 CU 外观，保留映射行为，移除事实生产、模拟器和帮助中心，形成下一阶段可继续建设的简洁入口。

本任务显式建立 `aiis-ics-arch.aw.sma` namespace，以 `SMA-001` 为本阶段 root；不设置 Parent Task ID。根 [ARCH-AW-001](../../../../plans/ARCH-AW-001-agent-foundation/spec.md)、[ARCH-AW-007](../../../../plans/ARCH-AW-007-general-agent-fleet-roadmap/spec.md) 与 [CU-008](../../../console-ui/plans/CU-008-grouped-sidebar-navigation/spec.md) 仅为来源和设计背景，不转移批准、QA 或验收。

当前仅有 PM `spec.md`。本 r1 尚未取得 Human Owner 精确范围批准，不创建 `tasks.md`、`checklist.md`，不进行实现、应用启动或实施验证。主协调可在 AW 现有 `PLAN.md` / `PLAN.zh-CN.md`、`plans/README.md` / `plans/README.zh-CN.md` 四处机械添加本 draft 链接；SMA 自有 PLAN/catalog 在获批后的 Development 阶段建立。PM profile 为 `contract_only`，不构成文件系统 ACL、强制路由或完整 Agent Team 激活证明。

## 2. 已核对的源码基线

以下为 2026-11-03 当前工作树只读事实，不是本任务运行或 QA 结果。交接前需固定实际修改前基线与候选 diff，保护已有和并行 dirty 内容。

| 表面 | 当前事实与证据路径（相对 SMA 根，另有注明除外） |
| --- | --- |
| 来源与 CA 命名 | `README.*` 记载 SMA 来自 DTB TSS `a87c107c10e8d9d9d3e389e357b50d203d2aebf7` 的过滤复制。AW `control-agent/` 是迁移后冻结的旧 PLC 采集兼容运行时；后续通用 CA 是另一个建设目标。不得把三者混称或修改原 TSS / 旧 CA。 |
| CU 未接入 | `package.json` 无 Element Plus；`vite.config.ts` 无 `@aw-ui` alias；`src/main.ts` 加载本地壳样式；`src/App.vue` 自行实现导航/顶栏，尚无明暗主题控制。 |
| CU 可消费合同 | `../console-ui/src/ui/index.ts` 与 `src/ui/styles/index.css` 是公共入口；CU-008 二级导航在其 owning checklist 已 `owner_accepted`。`../data-acquisition-agent/vite.config.ts` 可参考源码消费方式，DAA 实现本身不归本任务。 |
| 已有 HTTP 主链 | `src-tauri/src/services/mapping_runtime/mod.rs` 已取事实、评估、投递。`snapshot_facts` 固定使用 `POST /api/integration/v1/collection-facts/snapshot`；`send_saved_target_request` 使用保存的 Backend base URL 与目标配置。本阶段不是从零重写，也不交付任意 GET 源。 |
| Backend 依赖 | 配置、运行 lease、审计仍依赖 `/api/tss/v1`；当前本仓 `backend/` 未配套该套接口。纯本地通过不能证明现 Backend 业务闭环。调度逐项 `await`，未取得大批量吞吐或并发保证。 |
| 清退耦合 | `TwinJsonContractPanel.vue`、`collectionFacts.ts`、`api/index.ts` 承载事实定义/值写入；`singleFactRuntime.ts` 同时拥有 Simulation 与映射启动偏好。Rust `app.rs` 注册模拟状态与 IPC，`config/runtime_startup.rs` 的 v1 JSON 同时保存两类偏好。 |
| 帮助中心残留 | ARCH-AW-001 已排除完整 DTB 文章与跨仓生成；当前 `src/app/help/HelpCenterView.vue` 仅剩本地身份/映射说明，App/registry/navigation 及 locale 仍有入口和字段；`src/styles.css` 引用 `styles/help.css`。`markdown-it` / `@types/markdown-it` 仍在依赖中，当前 SMA 代码未使用。 |
| 文件与展示 | `mappingConfigurationFiles.ts` 实际使用 `xlsx`；映射导入导出及通用保存链不能随事实编辑一起删。多处普通表为手写表格，时间直接显示原字符串；CU 基础表格样式不自动提供持久列宽。 |

## 3. 范围与需求

### R1. 消费 CU 公共 UI，保持 SMA 独立身份

- 经公共入口复用布局、分组导航、顶栏、卡片、按钮、状态胶囊、主题与语言切换控件及公共样式。SMA 自有兼容依赖、锁文件与 Vue 单实例解析；不借用 CU `node_modules`，不复制整套 CU。
- SMA 拥有主题、语言、导航及业务状态。新 UI 偏好以 `sma.*` 命名，与 CU/DAA/TSS 隔离；保持现有中英语言资源机制，不为接入额外重建国际化框架。
- 基础样式先于 CU 公共样式；页面与弹窗/下拉在同一当前主题作用域。消费者只维护自身页面布局，不能修改 CU 公共 profile、生成 CSS、默认值、组件合同、私有 workbench 或 CU locale。
- 保持产品/窗口 `AIIS Semantic Mapping Agent`、identifier `com.aiis.aw.semanticmappingagent`、dev/preview `15192 / 14192`、独立 `dist` 与普通 `pnpm tauri dev` 入口。构建后运行 SMA 无需 CU 进程在线。

### R2. 导航与映射能力收敛

可见导航只保留以下职责，使用稳定 ID 与 CU 已有有限二级导航，不增加节点编排器或客户业务页面：

| 导航职责 | 保留能力 |
| --- | --- |
| 连接 | 当前 Backend 连接与 OpenAPI 诊断；默认 I/O 关闭时明确显示关闭状态。 |
| 源事实 | 按 sourceKey / 名称 / 类型等现有条件查询、分页、刷新、只读浏览；供映射选择现有事实。找不到来源时显示缺失，不提供创建入口。 |
| 目标接口 | API 材料、手工目标 API、现有参数位置与 schema；保留当前配置管理行为。 |
| 映射 | 映射任务、合法值规则、字段/常量绑定、现有类型转换及校验、请求预览。 |
| 映射运行与诊断 | 明确区分纯预览、已保存映射的单次投递、持续映射的启动/暂停/恢复/停止、现有计数、错误和日志。 |

保留 body/query/path/header 参数组包、必填/类型/合法值拒绝、sourceKey+factName 绑定、既有 JSON/XLSX 目标 API/值规则/映射配置模板及导入预览/显式应用/导出。纯预览不发 HTTP、不创建运行记录；单次投递继续使用已保存配置和明确动作。不得因换壳更改现有发送、lease、审计、幂等能力标识或失败/不确定结果语义。

### R3. 源事实成为只读输入

从 SMA 清退事实定义创建/修改/删除、定义导入/模板、定义 Preview/Apply、手工事实值修改及事实值导入，包括对应事件、store 分支、API facade、类型、专属弹窗和闲置 locale。保留只读查询、选点及现有只读事实导出；后者不得保留可写编辑入口。撤销缺失来源自动构造可编辑空合同的路径。

清退只作用于 SMA 调用面，不删除或变更 Backend 接口、上游事实、真实配置/profile、数据库或历史数据。真正的映射纯计算、请求预览和隔离映射测试继续保留。

### R4. 完整退役 SMA Simulation / producer

- 先解耦映射启动偏好，再删除 `SingleFactRuntimePanel.vue`、Simulation store、模拟规则调用/类型/locale、Rust Simulation 服务、状态装配、五个 `*_collection_fact_simulation_runtime` IPC、模拟启动分支与专属测试。清理仅被它们使用的依赖和域/合同 helper，逐项证明无保留调用者。
- 不以隐藏页或未注册菜单替代清退。普通启动、切页、刷新和旧偏好加载均不得创建模拟任务、查询模拟规则或写入事实。
- `runtime-startup.json` 保持 schemaVersion 1 的最小兼容，不引入本地业务数据库或自动迁移。映射偏好移入独立的 mapping-only 状态；保全既有 `apiMappingRuntime.enabled` 和历史 `factsPollingIntervalMs`，后者仍为兼容偏好，不改变现有按 Mapping 间隔调度。
- 旧 `collectionFactSimulation` 只允许存在于 Rust 磁盘兼容 DTO/夹具中，作为惰性数据，不能进入前端运行状态或产生执行能力。旧文件加载不改写；即使其 `enabled=true` 也不运行模拟。显式保存映射偏好时仅更新映射部分，保留已有惰性 legacy 段；新文件用停用中性值。缺文件时映射 auto-start=false。损坏/未知版本仍报错，不覆盖文件或默认为获准运行。
- 映射 app-open auto-start 的有效旧选择仍受原 I/O gate、配置就绪与正常启动校验约束。无 OS 开机托管、后台 daemon 或新启动策略；所有验证只用可丢弃 profile，禁止改写用户实际文件。

### R5. 按用户要求彻底清退帮助中心

删除 SMA 本地帮助页及 App import/render、registry 分组、`helpQuickStart` / `helpGlossary` 页 ID、无调用 `helpKey` / `helpTopicId`、闲置双语帮助键、`help.css` 及其引用。确认无代码依赖后删除 `markdown-it` / `@types/markdown-it` 与锁文件项。不保留隐藏入口、空帮助占位或另一套内置帮助模块；正常字段说明、校验错误、运行状态说明及 README 操作指引保留。

### R6. 表格、时间与残留样式

- 本轮保留且触达的普通业务表统一经 SMA 公共组件/列宽工具提供拖拽、合理最小宽、横向滚动、翻页/筛选/刷新/切页保持、重载/重启恢复和每表恢复默认。按应用+表稳定 ID+字段 ID 保存本机 UI 偏好，固定选择/序号/操作列可例外；非法/失效偏好回默认，不写业务配置版本或跨设备同步。可参考 DAA/DS `src/console/tableWidths.ts`，不改这两个工程，也不扩建 CU 公共合同。
- 触达的业务日历时间按 `Asia/Shanghai`、24 小时 `YYYY-MM-DD HH:mm:ss` 显示；统一工具管理。保留底层精度和事件事实语义，区分 Backend 实际更新时间、映射执行和回执时间；没有原始事实就显示缺失，不用界面刷新时刻冒充，也不把单调计数格式化为日期。
- 不迁移历史数据或批量改写外部返回。时区缺失且无法确认的旧值显示缺失/未明确状态，不猜测日期；合法带时区输入在展示边界转换一次。必要的本地 IPC 日历时间按根合同核对，保持原始精度；不改变外部 HTTP 协议。
- 清理因 R1–R5 失去引用的旧 TSS 壳样式、Projection CSS、孤立导入及误导术语；每个删除项有引用证据。保留来源、兼容 API 路径、稳定错误码和必要历史标识，不要求全仓关键词清零，不做相邻重构或依赖代际升级。

### R7. 文档与任务归属

获批后建立 SMA 双语 `PLAN.*`、`plans/README.*`，索引唯一 SMA-001 bundle；按实际结构更新 SMA `README.*`、`src/app/README.*` 与根 `CODE_INDEX.md`。SMA README 明确当前 Backend-held TSS 配置/固定 snapshot/当前目标 base URL 与未来 SQLite、通用 GET、可靠交付之间的边界。必要时仅机械更新根/AW 双语入口对应的 SMA 行，原根 ARCH-AW-001 bundle 保持原位。

AW PLAN 中 CU 仍称平铺/二级待做的对应行可依据 CU owning CU-008 事实最小纠正，不扩展成全仓历史治理。PLAN/catalog 只链接实际存在的角色文件；开发自检和独立 QA 各归其角色文档，不把局部 UI 通过写为业务闭环完成。

## 4. 排除项

本 r1 不交付任意 URL/GET latest/history 源、源/目标独立地址模型、新 Backend/AW 合同、Backend 配套实现、本地 SQLite 配置权威或迁移、持久游标/outbox/可靠业务回执、批量并发优化/容量保证、通用 CA/节点编排器、PLC/DAA/DS 功能、原 TSS/冻结 CA 修改、认证体系或 CU 自身设计迭代。

默认不连接真实 HTTP Backend/业务目标、DB、PLC，不运行原 TSS/CA/DAA/DS，不安装系统服务，不执行 Docker up/down/build、数据库迁移、部署、签名分发、Git/GitHub commit/push/tag/release。此任务批准或 QA 通过均不提供这些授权。

## 5. 候选 allowlist 与角色写入边界

以下为提交 Human Owner 审阅的实施 allowlist，仅在精确 r1 获批后生效。相对路径以 SMA 根为基准；每个文件仍须直接追溯 R1–R7，通配仅指明列模块内必要变更，不授权新增能力。Development 在 `tasks.md` 固定精确文件清单；超出表中表面或改变范围/AC/风险时返回 PM 新 Revision。

| 表面 | 允许路径及目的 |
| --- | --- |
| 启动与源码消费 | `package.json`、`pnpm-lock.yaml`、`vite.config.ts`、`tsconfig.json`、`src/vite-env.d.ts`、`src/App.vue`、`src/main.ts`：仅 CU 依赖/alias/类型、装配及原入口保持。 |
| 导航、样式、通用 UI | `src/app/{navigation.ts,registry.ts}`、`src/styles.css`、`src/app/styles/{shell.css,shared.css,responsive.css}`；`src/components/{BackToTopButton.vue,PaginationBar.vue,usePagination.ts}`。允许新增 `src/console/` 下仅用于本任务的主题/语言偏好、列宽和时间 helper，以及 `src/styles/app.css`；不建框架、插件体系或新公共包。 |
| 连接展示 | `src/app/connection/manifest.ts`、`components/{BackendConnectionPanel.vue,OpenApiOperationCatalog.vue}`、`views/ConnectionModuleView.vue`、`styles.css`：CU 组合、表格与帮助元数据清退；不改连接 API 合同或 gate。 |
| 映射模块 | `src/app/twin-facts/{index.ts,manifest.ts,types.ts}`、`api/index.ts`、`store/*.ts`、`components/*.vue`、`views/TwinFactsModuleView.vue`、`utils/collectionFactFiles.ts`、`utils/mappingConfigurationFiles.ts`：仅既有工作台适配、producer 清退、映射偏好解耦和原文件交换链保全；该 view 仅同步本轮组合及头部说明，退役后不再宣称 JSON fact authoring 或双 runtime。可新增该 store 内的 mapping-only 启动偏好文件，不引入新业务模块。 |
| 帮助与文案 | 删除 `src/app/help/HelpCenterView.vue`、`src/styles/help.css`；修改 `src/locales/index.ts`、`src/locales/common/{zh-CN,en-US}.json`、`src/app/{connection,twin-facts}/locales/{zh-CN,en-US}.json`。 |
| Rust 清退与兼容 | `src-tauri/src/app.rs`、`src-tauri/src/commands/{mod.rs,runtimes/mod.rs,mapping_runtime/mod.rs}`、`src-tauri/src/config/runtime_startup.rs`、`src-tauri/src/services/{mod.rs,mapping_runtime/mod.rs,simulation/**}`；`src-tauri/src/{domain,contracts}/{mod.rs,collection_facts/mod.rs}` 及 `domain/runtime/mod.rs` 仅按无调用证据裁剪/时间口径核对；`src-tauri/{Cargo.toml,Cargo.lock}` 仅删除专属闲置依赖。保留通用 file_export 运行链。 |
| 有界验证 | `tests/*.test.mjs`、`src-tauri/tests/{collection_simulation_tests.rs,mapping_runtime_continuous_tests.rs,mapping_runtime_manual_run_tests.rs}`；可新增本任务偏好/清退/映射/列宽/时间回归和最小 fixture，fixture 只服务离线或 loopback 验证。删除模拟专属测试不准删除仍有意义的映射断言。 |
| 稳定文档与索引 | 本模块 `README.*`、`src/app/README.*`、新 `PLAN.*` / `plans/README.*`；仓根 `CODE_INDEX.md`、`README.*` / `PLAN.*` 及 AW `README.*` / `PLAN.*` / `plans/README.*` 仅对应 SMA 状态、入口和上述 CU 行的最小机械同步。不得覆盖其他任务 dirty。 |
| 角色权威 | PM 仅本 `spec.md`；获批 Development 创建本目录 `tasks.md` 并记录实现/self-check；交接后 fresh-context Verification 才创建 `checklist.md`，不得互写。 |

禁止写 `../console-ui/**`、`../control-agent/**`、`../data-acquisition-agent/**`、`../device-simulator/**`、外部 DTB/TSS、`backend/**`、共享 skill/workflow/角色配置、真实 `.env` / app-data / profile / SQLite / 历史。Tauri 标识、窗口限制、capability 与图标沿用，不在本轮重设计。

## 6. 验收标准

以下为未来 Development 与独立 Verification 的验收设计，当前均未执行；不是 PM 自检或 QA verdict。

| AC | 必须可核验的结果 | 需求 |
| --- | --- | --- |
| AC01 | 实际使用两个 CU 公共入口和公共组件；无 CU 私有 import、依赖目录借用或 CU 源码修改。自身构建产物正常显示且 CU 不在线；产品身份、15192/14192 strictPort、独立 dist、原配置发现与 gate 保持。 | R1 |
| AC02 | 五类职责全部可达；分组展开/折叠、选中态、键盘焦点与单次 select 正常，切换主题/语言不触发业务调用、不丢已输入映射内容；无帮助或模拟可达页。 | R1/R2/R5 |
| AC03 | 中英 × 明暗检查连接、源事实、目标 API、值规则、映射与运行页；字段说明、表单、弹窗、下拉、加载/空/失败/关闭状态可读。桌面及浏览器 390×720 窄窗无不可达动作；表格横向滚动，弹窗局部滚动。保留 Tauri 原窗口限制。 | R1/R2/R6 |
| AC04 | 源事实查询/分页/选点及只读导出保持；找不到来源只显示缺失。源事实定义/值写入 UI、事件、API facade/导入路径不存在；隔离请求捕获证明只读使用不发定义/values 写入。 | R3 |
| AC05 | 当前字段/常量和五种数据类型语义、body/query/path/header 组包、必填/类型/合法值拒绝、纯预览无 I/O 均有回归；JSON/XLSX 配置导入预览/显式应用/导出保留。`xlsx` 与通用保存链仍有效。 | R2/R3 |
| AC06 | 已保存映射单次投递与持续运行控制在可丢弃 loopback fixture 中保留现有行为，目标地址仍来自已保存 Backend；失败/ambiguous/lease 拒绝不因 UI 变化变为成功或盲目重试。运行测试不作为真实业务保存证明。 | R2 |
| AC07 | Simulation 组件/store/服务/装配/五个 IPC/规则 API/启动调用和专属依赖已完整退出；仅可保留 R4 指定的惰性磁盘兼容字段与 fixture。旧 simulation=true 偏好不产生模拟状态、规则请求或事实写入。 | R4 |
| AC08 | 临时 v1 偏好夹具证明映射 enabled 与历史 interval 保全，加载前后文件字节不变，显式修改只更新映射部分；缺文件默认 false；损坏/未知版本报错且原文件不覆盖。映射 gate 关闭即使旧 autostart=true 仍无外发。无 OS 托管变更。 | R4 |
| AC09 | HelpCenterView、帮助分组/页 ID、闲置 help 字段/键、help.css/import、markdown 依赖无可达或构建残留；正常字段说明与 README 保留。删除清单有引用证据，稳定兼容路径/错误码不被误删。 | R5/R6 |
| AC10 | 每张触达普通业务表实测拖拽/最小宽/横滚；翻页、筛选、刷新、切页、重载后宽度恢复；不同表/语言以稳定 ID 隔离；每表恢复默认只清当前表；失效偏好回默认。 | R6 |
| AC11 | 同一带时区日历值在不同宿主时区下均显示上海到秒，底层值/精度不变；采集/保存/执行/确认等标签按实际字段语义，缺失/无时区不猜测；无历史数据迁移。 | R6 |
| AC12 | `pnpm check`、`pnpm test`、`pnpm build`、Rust fmt/test `--locked` 的适用检查通过；默认关闭 I/O 的当前平台 Tauri 有界 smoke 可显示 CU 和剩余页、关闭退出。所有 fixture/进程/端口/临时 profile 有归属及收尾记录，未接真实系统。 | R1–R6 |
| AC13 | 双语 README/PLAN/catalog、CODE_INDEX 与当前结构一致；来源、固定 snapshot、旧 Backend 依赖、大批量未证明及后续 gate 明确；task namespace/Classification/Owner/验收链一致。diff 仅落 allowlist，旧 CA/TSS/CU/DAA/DS 和并行改动保全。 | R7 |

## 7. 验证环境与交接证据

获批后由 Development 选择最少必要实施步骤，记录修改前基线、精确候选文件/hash 或 diff、真实命令/退出码、截图或操作证据及限制。使用项目 pnpm/Cargo 与锁文件；不把 Agent 辅助依赖装进工程。建议必需命令（SMA 根）：

```bash
pnpm install --frozen-lockfile
pnpm check
pnpm test
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo test --manifest-path src-tauri/Cargo.toml --locked
```

UI/native smoke 仅在显式隔离的可丢弃 `SMA_PROFILE_DIR`、空 Backend、`SMA_HTTP_ENABLED=false` 下进行；普通桌面入口仍为 `pnpm tauri dev`。现有 HTTP 语义检查可用专用 loopback fixture，只为夹具显式开启 gate，禁止触及非 loopback 地址或复用真实配置。fixture 不成为交付应用的常驻 mock/API。

必要证据覆盖 AC 表的纯逻辑、真实 UI 操作和最小本地 IPC；仅截图不能替代默认无 I/O 和偏好兼容断言。原生或依赖环境不足时如实记录 blocker，不把浏览器或源码检查冒充原生通过。链接检查仅覆盖本任务涉及文档；不运行全仓治理初始化/迁移或为预建未来角色文件跑整套 checker。

## 8. 风险、兼容与回退

| 风险 | 本阶段处理 |
| --- | --- |
| 清退共享 store 误伤映射启动与文件保存 | 先分离映射偏好，再移除 Simulation；保存链和 `xlsx` 按调用者保留；AC05/07/08 把前后语义分开核验。 |
| 旧 simulation=true 或损坏偏好 | 只有惰性兼容解码；不执行、不自动迁移、不覆盖原文件；真实 profile 全程只读/不触达。 |
| CU 依赖冲突、暗色弹层或旧 CSS 覆盖 | 消费端自有兼容依赖与 dedupe、严格公共入口、主题作用域，覆盖表单/弹层实际 UI；不改 CU profile。 |
| 清退帮助被误读为只删项目文章 | 本 r1 明确连当前本地阅读器和所有入口一起退出；正常操作说明归字段文案/README。 |
| 本地通过被误报为 HTTP/业务闭环 | 保留当前固定 POST snapshot、共用 Backend base URL 与 `/api/tss/v1` 依赖限制；无任意 GET、可靠 outbox、真实业务或吞吐接受。 |
| 并行工作树/回退覆盖其它任务 | Development 固定自己精确差异；回退仅按获准的本任务源码补丁，不执行全仓 reset/clean、不还原他人 dirty、不回滚用户数据。 |

本阶段不进行数据结构或历史迁移，因此无需恢复数据库作为回退步骤。若发现必须改变 Backend 合同、存储权威、真实配置、CU 公共 API 或扩大路径，停止该部分，返回 PM 新 Revision 与 Human Owner 批准。临时产物优先 `/private/tmp`；必要证据摘要持久化在各角色文档，验收后按 workflow 清理无后续依赖的自有资源。

## 9. 角色与 skill handoff

- PM 已按 `aiis` / `project-governance` 定义范围与治理；不替技术角色实施或独立验证。
- 获批 Development 读取完整已形成 bundle 及最近 README/PLAN，加载 `frontend-ui`、`i18n-workflow`、`desktop-tauri`、`rust-runtime`；文档/索引使用 `project-governance`、`code-document-indexer`。如需深入 UI→API/IPC 清退溯源，按需使用 `interface-lineage-audit`，不为本任务新增审计工具。当前不修改 Backend，不以加载后端 skill 扩大范围。
- Development `tasks.md` 给出精确 SMA-001 r1、交付工作树、文件清单/候选 diff、self-check、未通过项/已知限制及临时资源，状态到 `developer_handoff`。
- 主协调随后实际启动命名 Verification，以 fresh context（工具支持时 `fork_turns="none"`）读取本 spec、tasks、候选源码/diff/证据，按相关技术 skill 独立核验并创建 `checklist.md`；失败保留并返工。DEV self-check 不是独立 QA。
- `qa_passed` 只进入 Human Owner 最终验收；本 r1 UI/清退接受不等于任意 GET→POST、当前 Backend 业务闭环、大批量吞吐、生产/现场就绪或发布授权。

## 10. 批准与 Revision 历史

| 日期（Asia/Shanghai） | Revision | 事实 |
| --- | --- | --- |
| 2026-11-03 | r1 | PM draft：记录 CU 公共 UI 接入、HTTP 映射职责收敛、事实生产/Simulation/帮助中心清退，以及列宽/时间、兼容和离线验收边界。精确 Human Owner 范围批准 pending；未实施、未运行验证、无 QA verdict 或最终验收。 |

待 Human Owner 决定的是 **SMA-001 r1 的完整范围、allowlist、AC01–AC13 与风险**。批准原话、日期和精确 Revision 形成后才可将 spec 标为 `owner_approved` 并交给 Development；当前讨论、历史任务批准、用户源码来源提问及本 draft 索引均不能代替该决定。

后续问题独立立项：可配置 GET/latest/history 源与稳定采样身份、源/目标地址模型、新 Backend 事实/配置合同、SQLite 权威、持久进度/outbox/回执与 unknown 对账、批量调度/吞吐、跨平台包及真实业务联调。本 r1 不预先设计或实现这些机制。
