Task ID: SMA-004
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Development；Human Owner已于2026-11-04精确批准SMA-004 r1，仅实施本地配置与纯预览、暂时关闭正常投递；003前置接受已核定，完成后须fresh-context独立验证
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch.aw.sma
Classification: child_inherited
Capability: SMA HTTP映射桌面应用的分阶段交付
Owner: AIIS Automation World / SMA 模块 Human Owner
Acceptance Chain Reference: SMA-001 总交付链：各任务精确 Task ID / Revision 范围批准 -> Development developer_handoff -> fresh-context Verification -> Human Owner 分阶段及总体最终验收
Scope Slice: 配置本地唯一权威、离线维护与同一已保存快照的只读预览
Parent Task ID: SMA-001
Same Capability: yes
Same Owner: yes
Same Acceptance Chain: yes
Depends On: SMA-003
Related Task: aiis-ics-arch::ARCH-AW-008, aiis-ics-arch::ARCH-BE-009, aiis-ics-arch::ARCH-BE-010

# SMA-004：配置独立化

## 1. 目标、授权与依赖

本任务是 [SMA-001 r2](../SMA-001-cu-integration-and-scope-cleanup/spec.md) 阶段③，顺序保持“清理 → CU → 配置独立化 → 单目标 GET→POST → 历史与可靠恢复 → 批量”。让连接、API 材料、目标、值规则和映射由 SMA 本机保存与维护，Backend 不在线、HTTP gate 关闭时仍能读取、编辑、保存、导入预览、显式应用、导出及重启恢复。

Human Owner 于 2026-11-04（Asia/Shanghai）的原话为：

> 好的，验收 SMA-003 r1。接下来先准备“配置独立化”的子 spec，暂时不改代码。

上述起草授权当时只覆盖本r1文档；该时点为draft，未创建tasks/checklist、未改代码/依赖/数据库或现有profile、未启动应用或HTTP联调，保留为历史。同日随后Human Owner明确批准精确SMA-004 r1，当前为 **owner_approved**，可按本地配置与纯预览范围交Development，暂时关闭正常投递；完整原话、批准前SHA及边界见§8。PM本次仅登记批准，不执行软件实施或验证。

[SMA-003 checklist](../SMA-003-cu-integration/checklist.md#owner-acceptance-r1) 已记录精确 r1 的 `owner_accepted` / `QA Verdict: qa_passed`，候选 digest 为 `ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf`；这是本任务的前置基线，不是本任务的软件批准或验收。与父任务的三项 Same 均为 yes，仅继承上下文；父规格仍为 draft，各子任务保留自己的批准、handoff、fresh QA 和 Owner 接受。

## 2. 当前源码与范围取舍

以下为本次只读源码核对，不是本地配置已经实现或执行验证的证据。

| 实际链路 | 当前事实 / 本任务采用的边界 |
| --- | --- |
| [连接 facade](../../src/app/connection/api/index.ts) → [连接页](../../src/app/connection/views/ConnectionModuleView.vue) | `sma.backend-connection.v1` 是 WebView/browser localStorage；缺值时可回落 `SMA_BACKEND_BASE_URL`。它不是 Rust 配置库，`SMA_PROFILE_DIR` 也不隔离这个键。 |
| [材料 store](../../src/app/twin-facts/store/apiMaterials.ts) → [配置 facade](../../src/app/twin-facts/api/index.ts) | OpenAPI 来自 `GET /openapi.json`，选择及材料快照保存仍走 `/api/tss/v1/api-materials`。离线 load 当前会失败，不能只把选择框保存在内存就称为独立配置。 |
| [目标](../../src/app/twin-facts/store/targetApiConfiguration.ts)、[值规则](../../src/app/twin-facts/store/mappingValueRules.ts)、[映射](../../src/app/twin-facts/store/mappingConfigurations.ts) | CRUD、导入 preview/apply、引用及保存配置均依赖旧 TSS HTTP；映射加载还逐项读取远端 manual-run 审计，编辑时取远端源事实。需要拆开配置加载与事实/审计读取。 |
| [JSON/XLSX helper](../../src/app/twin-facts/utils/mappingConfigurationFiles.ts) | 已有三种资源的模板、单 sheet XLSX、旧目标九列兼容、公式拒绝及显式预览/应用。保留交换合同，改为交给本地配置服务校验和保存。 |
| [Rust runtime](../../src-tauri/src/services/mapping_runtime/mod.rs) / [IPC](../../src-tauri/src/commands/mapping_runtime/mod.rs) | 单次 run 先从 TSS claim 得到冻结 snapshot；持续运行从 TSS 取 configurations/state，并 claim/complete lease。源固定 POST snapshot，目标共用 Backend base URL。不能让新 UI 本地保存而运行器继续用远端另一份配置。 |
| [纯映射 domain](../../src-tauri/src/domain/mapping_runtime/mod.rs) | 已有五类型、fact/constant、四位置、必填/值规则与组包算法；本地已保存配置的预览复用这些语义，不生成 claim、审计成功或投递记录。 |
| [Cargo](../../src-tauri/Cargo.toml)、[启动偏好](../../src-tauri/src/config/runtime_startup.rs) | SMA 当前无 rusqlite/sqlx；本机已有持久化仅启动 JSON 与 UI localStorage。DAA/DS 锁定 `rusqlite =0.32.1` + bundled 可供版本参考，不能称为 SMA 已有 SQLite 能力，也不共享它们的库或业务模块。 |
| [详细设计 §3](../../../../docs/AIIS_SMA_Detailed_Design.md#configuration) | 本地 SQLite 是可单独批准的后续路线；草稿/生效版本、双进度/outbox 等是目标。本 r1 只批准有限配置存储切片时才实施，不连带交付设计全文。 |

**建议一次批准的方案：**一个 Rust 管理的本地 SQLite 配置文件，保存一份完整、有 revision 的配置快照；不建立多库、配置版本历史、active/draft 发布系统或通用配置框架。JSON 用于可审查的配置备份/交换，XLSX 保留人工填写和复核职责；二者都不是正常运行时的第二权威入口，不新增 YAML 启动链。

| 候选 | 本 r1 决定 |
| --- | --- |
| 继续 localStorage 或多份独立 JSON | 不采用：仍会分散原生权威，跨材料/目标/规则/映射的整包应用和版本冲突难以统一。 |
| 单 SQLite、单配置快照 | 采用：用短事务和 revision 比较保证一次应用完整提交，利用现有 serde DTO，保持存储表面有限。新增一个 SMA 自有 rusqlite bundled 依赖，候选精确版本沿用当前 DAA/DS 的 `=0.32.1`；不升级其它工程。 |
| 逐实体完整关系库、版本发布/运行库/outbox | 暂不采用：配置规模与本阶段需求不足以要求这套机制；未来必要时另立 schema/迁移规格。 |

**必须显式批准的行为变化：**本地配置生效后，本版本的正常应用只提供配置维护和纯预览，暂停可调用的单次/持续投递入口；manual、start、resume 和 auto-start 均在 Rust 准入层拒绝。旧 TSS runtime 实现与兼容回归保留，但不作为正常应用的 fallback，不交付永久双模式/双配置开关。第四阶段再以本地配置为基础接入获批的 GET→POST 执行链。若 Owner 要求第三阶段同时继续实际投递，须返回 PM 扩大精确范围，不能暗中绕开旧 lease/审计。

## 3. 要求

### R1. 唯一权威与状态分类

| 类别 | 权威 / 本 r1 生命周期 |
| --- | --- |
| 业务配置 | SQLite 中连接、API catalog/已选材料快照、目标、值规则、映射及引用所需只读源元数据；UI 只是加载快照和未提交表单。所有保存/导入 apply 由 Rust 校验并提交。 |
| UI 本机偏好 | 主题、语言、侧栏、列宽继续原 `sma.*` localStorage/helper；不进入配置 revision、业务备份或跨设备同步。 |
| 本机技术配置 | `SMA_ENV_FILE`、HTTP gate、profile 路径和日志仍归既有技术入口；`runtime-startup.json` v1 保持独立、加载不改字节、保留惰性旧段、缺文件默认 false。它不授权执行，也不进入业务备份。 |
| runtime 状态 | 当前内存状态/诊断与旧 Backend 审计保持各自语义；本 r1 不迁入 cursor、lease、运行历史、outbox、ACK、去重或成功计数，不把配置 revision 叫作运行 checkpoint。 |

只保留当前一个保存的 Backend 连接（scheme/host/port）；不新增多连接列表、独立源/目标 base URL、凭据页或可配置 GET 参数。其在本 r1 用于显式 OpenAPI/事实只读请求，不能因保存连接而发请求。材料的 sourceLocator 是来源证据，不自动覆盖保存的连接。

### R2. 单库、事务与版本

1. 新建 `<SMA profile>/configuration.sqlite3`；profile 用有效绝对 `SMA_PROFILE_DIR`，正常产品路径归既有 SMA app-data。显式 override 非绝对、路径不可用或库不兼容时明确失败，不回落默认目录或临时空库。Development/QA 仅能创建自有可丢弃 profile 的新库；真实默认 profile 的采用另行授权。
2. 本任务明确包含**新配置库 schema v1 的初始化**，不含任何已有库迁移。最小结构为一个 singleton 配置快照行，具有 schemaVersion、单调 revision、完整 document 和真实 updatedAt；内部 SQL/DTO 细节由 Development记录在 tasks，但不得扩展为通用实体框架或新增运行表。
3. document 包含 R1 的配置集合；内部 ID 与业务 key 稳定，业务 key 与已保存来源身份沿用当前不可随意改写语义。旧远端 id/rowVersion 不作为新本地写入凭据。保存返回本地 revision，不能伪称 Backend rowVersion、lease 或业务确认。
4. 每个变更用 expectedRevision 做比较，并在同一短事务内读取、检查全图、保存完整快照、递增 revision；不变导入不递增 revision。冲突显示“配置已变化，请重新加载/预览”，不 last-write-wins。失败或取消后持久配置仍是原快照；UI 只在提交成功后报告保存成功。
5. 单进程配置服务串行协调写入；同一服务的两个UI/测试客户端可对同一revision形成竞态，由事务/CAS决定结果，UI禁用按钮不能替代Rust检查。本版不提供多SMA进程共用profile的协作，不新增OS跨进程排他锁、常驻profile租约或运行lease；遇SQLite busy或revision变化时有界失败，不无限重试，也不据此宣称已实现profile排他。
6. 缺库可初始化空配置，损坏/未知 schema/不可读库必须报错并保留原件，不删库重建或自动降级。日历时间用既有上海公共时间工具，RFC 3339 `+08:00` 保存；不新增历史时间迁移。

### R3. 离线编辑、材料与引用完整性

- 五类现有工作区及 CU 布局保持。连接保存、材料勾选/显式保存、从已选材料加载目标、手工目标、值规则、映射 CRUD 均不依赖 HTTP gate、远端配置、审计或最新事实请求。
- 材料面板打开时先显示本地 catalog/选择，不自动刷新远端。沿用现 OpenAPI 解析器；增加同一面板内的本地 OpenAPI JSON 导入预览/显式应用，支持无后端建立材料。显式网络刷新仍走既有 gate。空/失败/不支持的材料不能抹掉已有材料/目标；catalog 改变仅形成预览，不自动替换派生目标。
- `materialKey`、`apiKey`、`valueRuleKey`、`mappingKey` 保持资源内唯一；同源 method/path 材料身份保持。mapping 的 targetApiKey、binding 的 valueRuleKey 以及 target 的 originMaterialKey 必须在本地完整解析，禁止悬空或指错对象；禁用与删除不同，禁用不抹引用。
- 删除被引用的材料/目标/值规则应拒绝，并展示引用它的配置 key；不级联删除。目标参数/类型或规则变更若使现有 mapping 结构无效，拒绝本次变更，先显式修改/删除引用；不得静默丢 bindings。整包恢复则对新全图一次校验，不按旧图逐行半途删除。
- 保存 mapping 保留间隔、enabled、字段/常量互斥和既有参数语义；`enabled=true` 仅为配置意图，UI 明确它在本 r1 仍不能启动运行。临时表单草稿不自动保存或自动生成已生效配置，不交付草稿版本管理系统。

### R4. 源引用与无事实时的预览

当前绑定身份是每个 binding 的 `sourceKey + factName`（不是行号、中文名或自行编造的 factId/pointId），继续原样保存；legacy mapping-level sourceKey 仅按既有 normalizeBindings 补齐缺失 binding sourceKey，冲突时拒绝，不猜来源。

离线创建/修改 mapping 可在现有绑定编辑区填写或选择这个身份对，或者从既有 JSON/XLSX 导入；这只是引用，不创建事实定义、不写事实值、不恢复模拟器。引用格式错误、字段缺一或类型明显矛盾时拒绝；没有可核对的源元数据时允许保存为“来源未验证”，不能报告来源存在或校验完成。

为离线重开保留已读取/导入配置携带的最小只读源元数据（身份、已知 dataType/factKind、来源与定义版本原值），并显示其证据来源/未验证状态；不把它当权威事实目录，不保存事实值、latest/history、采样时间或新事实定义。旧资源导出未携带元数据时保持未验证，不强制网络查询来完成保存；遇到不同 factId/pointId 合同需后续显式适配，不能仅凭名称合并。

分清“编辑草稿预览”与“已保存配置预览”。后者必须经 Rust 从**当前本地 revision**读取 mapping、目标和规则并组包，返回配置身份/revision和诊断，不能转回 TSS 获取 snapshot。复用现有纯转换/校验语义，不伪造远端 claim/snapshot/审计。预览无网络、不更改业务配置或运行状态。

已实际读取的事实值只在当前会话内用于原只读预览，保留其真实来源与时间；离线重开无值时展示缺值/未解析，必须参数未解析时不输出“可投递”的完整请求。常量仍能预览，无事实不能用 0、空字符串、样例值或元数据冒充已解析来源。测试可使用标明隔离来源的单元 fixture，不交付可编辑事实值或常驻 mock 服务。

### R5. JSON/XLSX 导入、备份与恢复

1. 保留 `targetApis`、`mappingValueRules`、`mappings` 三资源现有 JSON wrapper、XLSX sheet/表头、类型/布尔转换、旧目标九列默认 POST 及原导出/模板。目标参数四位置与五类型不变，继续拒绝公式、宏和无效 workbook；不新增 XLSX 模板平台。
2. 每次先解析/预览 create/update/unchanged/errors，展示资源 key、引用缺失和冲突；预览本身不写库、不查远端。apply 绑定已预览的同一规范化内容与 expectedRevision，并在 Rust重新校验；文件、表单或本地 revision 改变就要求重新预览。
3. 单资源 import 按业务 key upsert、不隐式删除；文件内重复 key 一律为冲突，已有 key 内容变化在 preview 列为 update，Owner显式 apply 才更新。保留同 key 的本地身份；任何一行非法、跨资源引用无效或事务失败都整批拒绝，不先写有效行。导入顺序可以先目标/规则后 mapping；UI 不自动抓取缺失依赖。
4. 增加一个有 `format` / `schemaVersion` 的**完整配置 JSON 备份**，包含连接、catalog/已选材料、目标、规则、映射和最小源元数据。通过现有保存文件通道显式导出；不拷贝打开的 SQLite 主文件，不导出 `.env`、HTTP gate、UI偏好、startup偏好、事实值和运行记录。
5. 恢复在同一既有配置操作区先展示整包替换及删除范围，再显式确认；以新完整图校验、一个事务提交，不分资源半恢复。恢复不还原远端 rowVersion/lease/运行身份，不倒退本地 revision，不开启 HTTP/auto-start。未知备份版本、结构错误或失败原库不变；只读取用户显式选择的文件，不扫描目录或自动找“最近备份”。
6. 固定技术边界而非新增UI参数：一个导入文件/IPC规范化载荷上限10 MiB，每类集合至多10,000项；每次保存、单资源import和整包恢复还必须校验**合并后的完整配置**，各集合最终总数不超过此限，完整JSON备份按实际导出编码连同信封的UTF-8序列化结果也不得超过10 MiB，保证能正常导出及重新导入。超限整事务拒绝，不能靠多次小保存绕过。不把这些防失控边界当批量容量承诺或负载目标。

### R6. 运行准入与运行中编辑策略

本阶段不把旧运行链改造为本地 lease/审计，也不宣称已能运行本地 mapping。正常应用移除配置加载附带的 `/api/tss/v1` CRUD、import、manual-run 审计查询；本地配置读取失败时直接显示错误，**不得 fallback 远端**。

manual/start/resume/auto-start 在原生 IPC/服务的正常应用入口均返回稳定 `SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE`，发生在构造 HTTP client、加载远端配置、claim、spawn 或发送之前；HTTP=true、已有连接、旧 auto-start=true 及直接 IPC 调用都不能绕过。前端呈现双语准入说明，不能只禁用按钮。pause/stop/status 可保留安全停止/只读诊断，不将拒绝操作增加为成功执行。

旧 HTTP 服务与已接受回归仍保留，测试可直接在隔离 fixture 验证其原语义；不向交付应用添加旧 TSS 执行模式选择。新配置不自动同步回 TSS，旧审计不被当作新本地配置运行结果。

新本地模式没有可运行任务。若在进程状态检查中发现已有非终止运行（running/starting/paused/stopping），对配置保存/import apply/整包恢复一律拒绝 `SMA_CONFIGURATION_RUNTIME_BUSY`，需显式 stop 并确认终止后重试；不自动停启或在途换规则。该策略由 Rust 服务统一检查并与准入/配置写入串行协调；未来热更新/版本冻结由后续规格决定。

### R7. 兼容与采用 gate

- 新 profile 保持空业务配置，不自动读原 TSS/Backend、旧 localStorage连接、真实 profile 或别的应用库；显式环境中的 Backend URL 最多作为待确认提示，不偷偷落库或覆盖已保存连接。原旧键和文件不删除、不改写。
- 已有配置只能由 Owner另行授权的人工导出/选文件或人工输入进入本地 preview/apply。三资源旧格式按 R5 兼容；无材料出处的旧目标按手工目标保留其业务参数，不伪造 originMaterialKey。旧远端 ID/version 只可作为明确来源信息，不能冒充本地运行权限。
- 本软件范围只允许可丢弃配置的端到端验证，**不包括真实数据迁移、默认 profile 采用、旧 Backend配置停写、业务 writer 切换或数据库清理**。真实采用前须固定旧来源/目标、备份、只读对比、唯一可编辑权威、回退和在途状态，另获精确授权。

### R8. 保留 UI 与可观察性

沿用五类职责、七个叶ID、现有 CU公共入口与SMA labels/i18n；只在现工作区增加本地文件导入、完整备份/恢复及准入说明所必需的有限操作，不新增配置中心页、向导、通用连接框架或参数面板。触达普通表继续公共列宽/重置；主题、语言、弹层、键盘与上海时间规则保持，UI偏好不触发配置revision。

配置库打开/版本拒绝、提交/冲突/失败、导入应用/恢复和运行准入拒绝留下有限结构化事件（key/revision/结果/错误码）；不记录事实值、完整配置、材料正文或敏感 Header。不为每次读取/预览生成运行审计，更不将配置保存写成目标业务成功。

## 4. 排除与保护

不实现可配置 GET 源、独立目标地址、真实新 Backend业务联调、DAA上传、PLC/DS连接、历史消费、feed/cursor/checkpoint/outbox/ACK/unknown恢复、自动重试、并发/吞吐优化、凭据系统、配置远程同步或CA编排。

不改 Backend/DAA/DS/CA/原TSS/CU公共源码、共享skill/角色/workflow、Tauri产品身份/端口/capabilities/图标、OS托管或打包发布；不恢复事实定义/值写入、Simulation/帮助中心。实际 `.env`、默认app-data、真实profile/配置/数据库/历史、002事故日志原件保护继续有效。部署、Docker、真实DB迁移、真实HTTP/设备和Git发布不在本任务授权中。

## 5. 软件候选 allowlist（仅精确批准后生效）

路径相对 SMA 根；每项仅限 R1–R8。Development启动前在tasks固定实际文件和基线SHA，不按通配扩展能力。PM本次只写本spec及父规格的关系事实；主协调负责PLAN/catalog机械同步。

| 表面 | 允许候选路径 / 用途 |
| --- | --- |
| 配置域/存储 | 新增 `src-tauri/src/contracts/local_configuration.rs`、`src-tauri/src/domain/local_configuration/`、`src-tauri/src/infrastructure/config_store/`、`src-tauri/src/services/local_configuration/`、`src-tauri/src/commands/local_configuration/` 内仅本任务DTO/纯校验/单库事务/薄IPC；各层 `mod.rs` 注册。不得建通用框架/运行状态库。 |
| 装配/准入 | `src-tauri/src/app.rs`、`src-tauri/src/config/mod.rs`、`src-tauri/src/commands/{connection,mapping_runtime,runtimes}/mod.rs`；现 `services/mapping_runtime/mod.rs` 仅共用准入接线/纯算法适配，`domain/mapping_runtime/mod.rs` 仅必要纯函数复用，不改旧HTTP/lease/失败/ambiguous语义。`config/runtime_startup.rs` 原v1磁盘合同保持。 |
| 依赖 | `src-tauri/Cargo.toml` / `Cargo.lock` 仅 SMA自有 rusqlite `=0.32.1` bundled及其锁定传递依赖；无新增前端依赖或SQLite Tauri插件，无其它工程依赖变动。 |
| 连接/配置facade | `src/app/connection/{api/index.ts,types.ts,views/ConnectionModuleView.vue,components/BackendConnectionPanel.vue,components/OpenApiOperationCatalog.vue}`、`src/app/twin-facts/{api/index.ts,types.ts,store/*.ts,utils/mappingConfigurationFiles.ts}`；可新增 `src/app/twin-facts/api/localConfiguration.ts` 作为有限IPC门面，不新建全局API框架。 |
| 现有工作区 | `src/App.vue` 仅本地配置ready/error装配；`src/app/twin-facts/views/TwinFactsModuleView.vue`、`components/{ApiMaterialsPanel,TargetApiConfigurationPanel,MappingValueRulesPanel,MappingConfigurationsPanel,MappingBatchOperationsDialog,ApiFirstMappingRuntimePanel,FactsTablePanel,TwinJsonContractPanel}.vue`；仅本地生命周期、文件操作、来源未验证及准入展示，必要局部样式仍归原文件。 |
| 文案/公共展示 | `src/locales/common/{zh-CN,en-US}.json`、`src/app/{connection,twin-facts}/locales/{zh-CN,en-US}.json`；复用 `src/console/{tableWidths,time,uiPreferences}.ts`，仅新增配置时间展示所需调用，不重写helper/CU设计。 |
| 验证/稳定文档 | `tests/*.test.mjs`、`src-tauri/tests/*.rs`及最小隔离fixture；SMA `README.*`、`src/app/README.*`、根 `CODE_INDEX.md` 仅实改结构；SMA/AW `PLAN.*` 和 `plans/README.*` 对应行由主协调机械同步。 |
| 角色 | PM仅spec；批准后Development创建本bundle的tasks，真实developer_handoff后新的fresh-context Verification创建checklist，不预建或互写。 |

必要路径/依赖/业务行为超出上述范围，或不能保留兼容算法和原回归时，停止该部分返回PM新Revision；不以“配置独立化”授权其它重构。

## 6. 可执行验收设计（尚未执行）

全部指本 r1获批后的必要验证。当前PM没有运行构建、测试、原生应用、SQLite初始化或HTTP。

| AC | 必须可核验的结果 |
| --- | --- |
| AC01 | 固定003已接受候选及本r1精确批准；配置链由UI → store → IPC → Rust配置服务 → 自有SQLite，外部请求捕获无TSS配置/审计fallback；未恢复退役职责。 |
| AC02 | HTTP=false、Backend不存在、可丢弃空profile下完成连接保存、本地OpenAPI JSON导入/材料选择、目标/值规则/mapping新建编辑删除、导出；真正退出OS进程后重开，从同SQLite恢复一致配置/revision。另一个profile保持空且不能读到前者。 |
| AC03 | 同一已保存revision的本地预览无需后端，保留五类型/fact-constant/四位置/必填/合法值/类型拒绝；配置加载、保存、预览和导出不生成运行成功或目标请求。草稿预览与已保存预览身份清楚，后者不使用未保存编辑。 |
| AC04 | 离线保存未知sourceKey+factName引用显示未验证；重开无事实值时必填诊断为缺值、无伪造0/样例；只读元数据不会创建定义/值或变成真实事实。legacy sourceKey正规化、冲突和不同身份合同拒绝有可复现用例。 |
| AC05 | 三资源JSON/XLSX现模板/导出往返、旧目标九列POST兼容仍有效；file内重复key、错误类型/参数/值规则、跨资源缺引用、公式/宏/超限拒绝；preview零写入，apply前内容或revision改变要求重新preview。 |
| AC06 | 完整备份→新隔离profile恢复后的连接/材料/目标/规则/映射及引用等价，原profile未动；恢复的整包删除范围先可见且需确认，损坏/未知版本/取消/中途事务故障均原库完整保留，无半写。恢复不恢复gate/UI/startup或运行记录。 |
| AC07 | 同一配置服务的两个客户端对同revision保存仅一个成功，另一个明确conflict，不要求新增OS进程排他机制；事务提交失败/SQLite busy/不可写/损坏/未知schema/非法profile override均无覆盖或默认路径fallback。连续小保存使合并后全集或实际备份编码超限时整体拒绝，原配置仍可导出/重导入。故障注入用隔离存储单元测试，比较逻辑快照及revision，不以SQLite页字节必定不变作断言。 |
| AC08 | 删除被引用材料/目标/规则被拒绝，影响现mapping的目标参数变更被拒绝，显式解除引用后可删除；disabled不丢引用。非终止runtime状态下save/import/restore被Rust拒绝，stop确认后可提交；不自动停启。 |
| AC09 | manual/start/resume/autostart的UI、直接IPC和服务准入都被明确拒绝；HTTP=false与显式true、旧autostart=true、有效旧连接均不产生TSS claim/config/state或目标连接。HTTP=false下材料/事实刷新也零外发。测试监听器仅专用loopback捕获零accept，不能靠按钮disabled证明。 |
| AC10 | 旧HTTP/lease/审计/failed/ambiguous/stop、五类型/四位置和startup v1既有回归保留其原通过范围；可测旧服务不等于应用仍开放执行。旧JSON加载不改字节、保存保留惰性段；新profiles默认false，不自动导入旧localStorage或真实Backend。 |
| AC11 | CU公共入口、身份/15192与14192 strictPort/普通启动、五组七叶、中英×明暗、配置弹窗/局部横滚/错误与准入说明保持；触达表列宽和每表重置、主题语言偏好不受配置恢复影响，配置时间真实上海到秒、底层精度保持。 |
| AC12 | pnpm check/test/build、Rust fmt/test --locked和隔离native有界smoke有真实命令/退出码；本地配置CRUD与跨进程重开在native+SQLite实测，浏览器不能用localStorage冒充落库。diff/文档/新schema与allowlist一致，无真实profile/外部服务副作用，候选和资源可追溯。 |

### 验证环境与命令边界

Development/Verification按项目既有 pnpm/Cargo锁文件运行 `pnpm check`、`pnpm test`、`pnpm build`、`cargo fmt --manifest-path src-tauri/Cargo.toml --check`、`cargo test --manifest-path src-tauri/Cargo.toml --locked`，普通入口仍为 `pnpm tauri dev`。依赖安装只用项目工具链与锁文件，不为辅助验证新增依赖。失败保留并如实记录，不从DEV自检生成QA结论。

任何启动前固定自有绝对 `SMA_ENV_FILE` / `SMA_PROFILE_DIR`、空Backend、HTTP=false，并验证产物SHA、实际PID/path/env及日志归属。**SMA_PROFILE_DIR只隔离Rust文件，不隔离WKWebView localStorage。正式默认WebKit store禁止用作测试。** 003的dataStoreIdentifier codegen E0308历史限制保留：不可改宏/依赖/正式identity绕过；支持的临时incognito overlay只能用于非持久UI smoke，Rust SQLite可在相同临时profile跨OS进程重开。UI偏好持久化用浏览器独占origin分层核验，不能用incognito证明native偏好持久化；受支持隔离不可用则记录blocker，不启动默认store。

外部请求只允许专项测试自有loopback fixture；新配置生命周期/预览用HTTP=false无需服务。仅为保留旧服务回归可命令级打开gate，仍禁止真实地址。启动后先确认进程已在隔离环境运行再绑定UI，退出后不再读AX或激活该app，避免工具无env重启。QA独立消费候选与原始证据；浏览器、Rust单元、native SQLite重开与真实HTTP各自写清证据层。

## 7. 分层测试依赖与后续 handoff

| 测试层 | 是否需等待API/DAA | 前置门槛与本r1边界 |
| --- | --- | --- |
| 本地配置生命周期、UI、文件、纯组包/校验 | 不需等待两者 | 本r1精确批准、隔离profile/存储及可用本机工具；AC01–AC12归此层。没有最新事实时按缺失验证，不伪造源。 |
| SMA → 事实API/目标业务API的单目标联调 | 需所选API可调用，不必等待DAA全部完成 | 第四阶段另批本地配置执行准入、源GET/目标POST合同、固定候选、测试数据/身份/错误与持久确认。可用Backend受控事实或其它明确Owner来源；若选DAA来源，则须其上传链就绪。 |
| PLC/DS → DAA → Backend facts → SMA → 业务API持久化 | 需DAA上传及对应Backend就绪 | 第四阶段及相应跨端联调范围另批，验证实际事实来源/保存与目标业务副作用；DAA本地SQLite或Backend源码QA不等于这条链已部署可用。 |
| 历史恢复、断线/重复/乱序/unknown与大批量 | 本r1不做 | 第五阶段可靠性合同/实现/接受后再做第六阶段负载；一次联调成功不替代完整恢复和容量验收。 |

相关事实依据只作为依赖背景：[ARCH-AW-008](../../../../plans/ARCH-AW-008-stage-c-facts-contract/spec.md)及其[checklist](../../../../plans/ARCH-AW-008-stage-c-facts-contract/checklist.md)为文档QA2通过、Owner文档终验待定；[ARCH-BE-009 Development](../../../../plans/ARCH-BE-009-backend-facts-integration/tasks.md)当前为r1 A源码/no-DB developer_handoff，独立验证及B采用未交付；[ARCH-BE-010 Development](../../../../plans/ARCH-BE-010-anonymous-business-integration/tasks.md)当前r2 implementation_in_progress，不能用r1 A0 QA代替r2或部署。DAA当前已接受受控阶段B，阶段C上传未交付，见[DAA PLAN](../../../data-acquisition-agent/PLAN.zh-CN.md)。外部状态将变化，联调前以各bundle最新有效交接和可调用证据重新核验，不据本段放行。

本r1获批后Development必须加载 `rust-runtime`（配置/SQLite/纯域/日志）、`desktop-tauri`（IPC/原生隔离）、`frontend-ui` / `i18n-workflow`（现页/双语）；治理用 `aiis` / `project-governance`，结构索引用 `code-document-indexer`。此处不启动后端开发；以后涉及Backend正式API/DB的独立任务由对应角色使用 `backend-arch`。本PM只做范围规划，不代替技术实现或QA。

DEV handoff应固定本r1、003基线、交付工作树/实际文件及before/after SHA、新SQLite schema/本地revision/文件合同、应用运行准入禁用事实、检查/故障/限制、隔离证据和资源。主协调随后实际启动新的命名fresh-context Verification（工具支持时fork_turns=none）创建checklist；QA通过后仍需Human Owner最终接受第三阶段。

## 8. 风险、回退与当前决定

| 风险 | 约束 / 退出方式 |
| --- | --- |
| 本地存储被误当成已恢复投递能力 | R6将正常应用执行入口关闭到原生层；UI/README和handoff必须明确本阶段只是配置与纯预览。该暂时行为变化是本r1范围批准的一部分，未批准前不实施。 |
| 旧连接/远端配置与新库双权威、真实迁移损坏 | 不自动导入或同步、不fallback，旧数据原样保留；真实采用另定备份/唯一权威/回退。没有授权不得读写默认profile来“补迁移”。 |
| 单快照冲突或配置增长 | expectedRevision、原子全图验证/提交和固定上限；只对配置规模作功能承诺，不预建分库/分页/并发框架。 |
| 原生工具重启触及默认profile | 先隔离/验PID再绑定，使用受支持临时store、进程退出后停止UI调用；环境阻塞如实交接，不复用002一次性风险接受。 |
| SQLite schema/binary回退不兼容 | 新库保留并显式导出备份，损坏库不改写；回退本任务源码前先核对新库版本，不让旧程序静默加载/删改新库，不以回退自动重启旧TSS投递。 |

不预设尚未存在的运行outbox/ACK的迁移；今后接入它们时另行定义配置恢复与运行进度关系。起草阶段无必须阻塞文档交付的待决问题，推荐方案及“第三阶段暂不投递”的取舍一并提交Owner范围批准；下述当前决定已批准该精确范围。若以后要求继续投递或改存储策略，仍须修订spec后重新批准。

| 日期（Asia/Shanghai） | Revision / 状态 | 真实记录 |
| --- | --- | --- |
| 2026-11-04 | r1 / draft | 根据“先准备配置独立化子spec、暂时不改代码”完成当前源码取舍与有限范围；只交付PM文档，无软件批准、Development、测试或独立QA。 |
| 2026-11-04 | r1 / owner_approved | Human Owner明确批准本地配置与纯预览、暂时关闭正常投递，并要求完成后独立验证；只登记批准，不改变本r1范围或声称软件已完成。 |

### Human Owner精确范围批准与当前handoff

主协调本轮转交Human Owner的明确原话：

> 好的，批准 SMA-004 r1，按本地配置和纯预览的范围开始开发，暂时关闭正常投递，完成后做独立验证。

批准对应的原r1草案SHA-256为 **`5dbfed2e2785e13ee1393d7fa3b42b40aea5fbec5906b35c418d52ccfd0a1301`**；PM登记前已只读核对一致。本次只将状态/handoff及当前授权登记为 `owner_approved`，Revision仍r1，R1–R8、排除项、allowlist、AC01–AC12、风险和验证边界均保持。正常投递暂时关闭是本次明确批准的一部分，不是隐含恢复旧TSS执行或新GET→POST授权。

同次只读核对[SMA-003 checklist](../SMA-003-cu-integration/checklist.md#owner-acceptance-r1)仍为 `owner_accepted` / `QA Verdict: qa_passed`，SHA-256为 `39d34539b4629fdb0fa1597879b97a113569d95d810acbad2a7bc96b4b0e2f86`，前置gate已满足；不重授其验收或放宽真实profile保护。

当前交接 **PM -> Development**，由主协调实际启动命名Development，按已批准表面创建tasks和实施；真实developer_handoff后仍须启动新的命名fresh-context Verification创建checklist，QA通过后交Human Owner最终验收。当前尚无本任务Development、QA或最终接受事实，不创建未来角色证据，不授权真实配置采用、数据库迁移、实际联调、发布或部署；SMA-001 r2仍为draft，④–⑥仍需各自精确批准。

本profile为contract_only；主会话、完整bundle与diff审计是必要控制，不宣称平台ACL、强制路由、发布部署或总体SMA完成。
