Task ID: SMA-002
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Development; Human Owner approved exact SMA-002 r1 on 2026-11-04 (Asia/Shanghai)
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch.aw.sma
Classification: child_inherited
Capability: SMA HTTP映射桌面应用的分阶段交付
Owner: AIIS Automation World / SMA 模块 Human Owner
Acceptance Chain Reference: SMA-001 总交付链：各任务精确 Task ID / Revision 范围批准 -> Development developer_handoff -> fresh-context Verification -> Human Owner 分阶段及总体最终验收
Scope Slice: 职责清理与既有 HTTP 映射基线保全
Parent Task ID: SMA-001
Same Capability: yes
Same Owner: yes
Same Acceptance Chain: yes

# SMA-002：职责清理

## 1. 目标、关系与批准边界

本任务是 [SMA-001 r2 总规格](../SMA-001-cu-integration-and-scope-cleanup/spec.md) 阶段①：退出事实生产、Simulation producer 和帮助中心，留下连接、只读源事实、目标接口/API材料、映射任务/合法值规则、映射运行/诊断五类职责。沿用现有壳层，聚焦功能、注册与引用清理，为 [SMA-003](../SMA-003-cu-integration/spec.md) 提供清理基线。

同父任务为同一 SMA 能力/Owner/总验收链的范围切片，三项 Same 均为 yes；只复用上下文，不继承软件批准、QA 或验收。2026-11-04 Human Owner 先授权“拆出‘职责清理’和‘CU 接入’两个子 spec……暂时不改代码”（完整原话见总规格 §1），当时本 r1 为未批准软件的 draft；同日随后明确批准精确 SMA-002 r1 并要求开始职责清理开发及独立验证，原话与边界见 §7。当前软件范围已批准，交接 Development。

现行运行器源仍固定 `POST /api/integration/v1/collection-facts/snapshot`，目标共用保存的 Backend base URL，配置/lease/审计依赖旧 `/api/tss/v1`。保留现有 HTTP 语义；本地回归不能证明当前本仓 Backend 配套或真实业务闭环。

## 2. 范围与要求

### R1. 保留映射，退出事实生产

保留只读源事实查询/分页/筛选/刷新/选点与现有只读事实导出；来源缺失时显示缺失，不构造可编辑空合同。保留 API材料/手工目标、sourceKey+factName/常量绑定、现有必要类型转换、必填/类型/合法值校验、body/query/path/header组包、纯预览、已保存配置单次投递和持续运行控制/诊断。

清退事实定义增删改、定义导入/模板及 Preview/Apply、手工值写入和事实值导入，包括事件、store分支、API facade、专属类型/弹窗及闲置文案。纯映射预览无HTTP/运行记录；JSON/XLSX的目标API/值规则/映射配置模板、导入预览/显式应用/导出及通用保存链有效，保留仍使用的 `xlsx`。

### R2. 先保全 mapping 偏好，再移除 Simulation

- 从 `singleFactRuntime.ts` 拆出 mapping-only 启动偏好后，删除 Simulation 页/组件/store、规则API/类型、启动/轮询分支、Rust服务/状态及五个 `*_collection_fact_simulation_runtime` IPC注册/实现和专属测试依赖；普通启动/切页/刷新不查询模拟规则或写事实。
- `runtime-startup.json` 保持 schemaVersion 1 的最小兼容；保全旧 `apiMappingRuntime.enabled` 与历史 `factsPollingIntervalMs`。后者仅兼容偏好，实际仍按各Mapping间隔调度。
- `collectionFactSimulation` 仅留在Rust磁盘兼容DTO/夹具中作惰性数据，不进入前端运行状态；旧enabled=true也不运行模拟。加载不改写；显式保存mapping偏好仅改mapping部分，保留已有惰性legacy段，新文件用停用中性值。
- 缺文件时mapping auto-start=false；损坏/未知版本报错且不覆盖。有效旧mapping auto-start仍受原HTTP gate、配置就绪与正常启动校验。无OS开机托管、daemon、SQLite或自动配置迁移。

### R3. 帮助中心全链退出

删除 `HelpCenterView.vue`、App import/render、registry分组、`helpQuickStart` / `helpGlossary` 页ID、无调用 `helpKey` / `helpTopicId`、闲置双语帮助键、`help.css` 和引用；无代码使用后删除 `markdown-it` / `@types/markdown-it` 及锁文件项。不留隐藏入口、空页或替代内置帮助模块；正常字段说明、校验错误、状态说明和README操作文档保留。

### R4. 残留清理与展示规则交接

只清理因R1–R3无引用的旧TSS/Projection CSS、孤立import、专属依赖和误导头部/术语，逐项提供引用证据，不泛化关键词删除。来源、HTTP路径、错误码、幂等能力标识、lease/审计、失败/ambiguous/停止语义继续保留，不重写运行器。

本任务不承担五类保留页的全量视觉改造；实际新增或触达的普通业务表/日历时间仍按根AGENTS落实列宽和上海时间规则。必要时通过SMA统一helper实现，交接表/字段稳定ID及回归；不能以等待CU豁免已触达内容，也不扩展无关页。SMA-003复用并完成其剩余页面展示范围。

## 3. 排除与保护

不接入CU，不改CU/DAA/DS/旧CA/原TSS，不改Backend或现行HTTP合同；不实现新GET、独立源/目标地址、配置独立化/SQLite、历史/outbox/回执、并发吞吐或通用CA。

实际 `.env`、app-data/profile、配置、数据库、历史不修改/删除；验证只用可丢弃数据。真实HTTP/DB/PLC、OS服务、Docker、部署和Git发布无授权。保持SMA身份、15192/14192、普通 `pnpm tauri dev`、原配置发现及 `SMA_HTTP_ENABLED=false`。

## 4. 候选 allowlist

仅在精确SMA-002 r1软件范围批准后生效，路径相对SMA根；Development固定实际必要文件，不因通配扩大能力。

| 表面 | 允许路径 / 目的 |
| --- | --- |
| 装配/入口 | `src/App.vue`、`src/main.ts`、`src/app/{navigation.ts,registry.ts}`、`src/app/connection/manifest.ts`：仅入口/import/帮助元数据与必要组合。 |
| facts/mapping（本行路径相对 `src/app/twin-facts/`） | `{index.ts,manifest.ts,types.ts}`、`api/index.ts`、`store/*.ts`、`components/*.vue`、`views/TwinFactsModuleView.vue`、`utils/{collectionFactFiles.ts,mappingConfigurationFiles.ts}`：仅R1–R4；view头部退出fact authoring/双runtime声明。可新增该store内mapping-only偏好文件。 |
| 帮助/样式/文案 | 删除 `src/app/help/HelpCenterView.vue`、`src/styles/help.css`；修改 `src/styles.css`、`src/app/styles/{shell.css,shared.css,responsive.css}`、`src/locales/index.ts`、`src/locales/common/{zh-CN,en-US}.json`、`src/app/{connection,twin-facts}/locales/{zh-CN,en-US}.json`。 |
| 已触达展示 | 可新增/复用 `src/console/{tableWidths.ts,time.ts}`；`src/components/PaginationBar.vue`仅必要表格接入，不新增主题/布局框架。 |
| Rust清退/兼容（本行路径相对 `src-tauri/src/`） | `app.rs`、`commands/{mod.rs,runtimes/mod.rs,mapping_runtime/mod.rs}`、`config/runtime_startup.rs`、`services/{mod.rs,mapping_runtime/mod.rs,simulation/**}`、`{domain,contracts}/{mod.rs,collection_facts/mod.rs}`、`domain/runtime/mod.rs`：仅专属裁剪、偏好与触达时间核对，通用file_export链保留。 |
| 依赖/回归 | `package.json`/`pnpm-lock.yaml`、`src-tauri/Cargo.toml`/`src-tauri/Cargo.lock`仅闲置专属依赖清退；`tests/*.test.mjs`、`src-tauri/tests/*`仅模拟专属测试删除、映射保全及清退/偏好/已触达展示的有界回归和最小fixture。 |
| 文档/角色 | 模块 `README.*`、`src/app/README.*`、`PLAN.*`、`plans/README.*`、根 `CODE_INDEX.md`及AW对应索引行最小同步；PM仅本spec，获批DEV创建本tasks，handoff后fresh QA创建本checklist。 |

其它应用、Backend、共享skill/workflow/角色配置、Tauri identity/capabilities/图标及真实数据禁止写；超allowlist或改变合同/AC/风险即返回PM修订。

## 5. 验收设计（尚未执行）

原合并r1的AC04–AC09主要归本任务，AC12/13按本切片适用；CU/全量展示归SMA-003，各自形成证据。

| AC | 必须可核验的结果 |
| --- | --- |
| AC01 | 五类保留职责可达；源事实只读查询/分页/选点/导出有效，缺失不创建；定义/values写入UI、事件、API/导入闭包退出，隔离请求捕获无事实写入。 |
| AC02 | Simulation页/store/Rust服务/状态/五个IPC/规则请求/启动调用全部退出，专属依赖/测试删除有证据；仅R2惰性磁盘兼容字段/夹具留存。 |
| AC03 | 临时合法v1的mapping enabled/历史interval保全，加载前后字节不变，显式保存仅改mapping；缺失默认false，损坏/未知版本报错不覆盖；simulation=true无执行，gate=false时mapping=true仍零外发。 |
| AC04 | 帮助页/导航/页ID、无调用help字段/双语键、CSS/import和markdown依赖无可达或构建残留；正常字段说明/README保留。 |
| AC05 | 五种现有类型、字段/常量、body/query/path/header、必填/类型/合法值拒绝及纯预览无I/O有回归；JSON/XLSX配置预览/显式应用/导出、xlsx与通用保存链有效。 |
| AC06 | loopback中原单次/持续HTTP行为、保存的Backend地址、lease拒绝、失败/ambiguous不变；不盲重试或改错误为成功，不宣称真实业务闭环。 |
| AC07 | 必要中英操作smoke和默认无I/O的本平台Tauri有界smoke可进入保留页并退出；实际触达表格满足列宽规则，日历时间上海到秒/原值精度/缺失语义正确；未变页不作全量视觉接受。 |
| AC08 | pnpm check/test/build与Rust fmt/test --locked通过或有精确blocker；删除/保留引用清单、文档/结构/allowlist一致，真实profile/数据和并行修改保全。 |

## 6. 后续验证、风险与 handoff

以下为本次获批 Development / Verification 应执行的命令与环境要求；本次 PM 仅登记批准，未执行这些检查：

```bash
pnpm install --frozen-lockfile
pnpm check
pnpm test
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo test --manifest-path src-tauri/Cargo.toml --locked
```

UI/native用可丢弃绝对 `SMA_PROFILE_DIR`、空Backend、`SMA_HTTP_ENABLED=false`，普通入口 `pnpm tauri dev`。HTTP仅专用loopback fixture显式开gate，禁止非loopback/真实地址；fixture不交付为常驻mock。记录真实命令/退出码、候选diff/hash、必要操作/请求证据、临时资源及收尾；环境不足不冒充pass。

主要风险为共享store/保存链误删与旧偏好触发：先拆mapping偏好，保全xlsx/file_export，再做退役闭包。回退只限确认属本任务的源码补丁，不reset/clean他人dirty、不回滚用户配置/数据；发现需新合同/迁移则停止该部分返回PM。

PM使用 `aiis` / `project-governance`；获批DEV/QA按技术面加载 `frontend-ui`、`i18n-workflow`、`desktop-tauri`、`rust-runtime`，文档用 `project-governance` / `code-document-indexer`，清退溯源按需 `interface-lineage-audit`，不新增审计工具或Backend范围。

DEV handoff给精确SMA-002 r1、交付工作树/文件、清退与保留清单、偏好兼容、已触达表格/时间helper、检查限制与资源；随后新命名fresh-context Verification（支持时 `fork_turns="none"`）独立创建checklist，DEV自检不是QA。Human Owner接受清理基线后SMA-003才可实施，其仍需独立软件范围批准。

## 7. 修订与当前决定

2026-11-04（Asia/Shanghai）：先从 SMA-001 未实施 r1 拆出本 r1，当时只批准文档创建，软件范围仍为 draft。该历史状态不代表下述软件批准后的当前状态。

同日随后，Human Owner 明确批准精确 SMA-002 r1，并要求执行：

> 那就先批准 SMA-002 r1，按职责清理的范围开始开发，保留现有 HTTP 映射功能，完成后做独立验证。SMA-003 等清理验收后再做。

本次批准使本 spec 的既有职责清理范围与 allowlist 生效，Revision 仍为 r1，R1–R4、排除项、allowlist、AC01–AC08 与风险均未变。当前 `Status: owner_approved`，handoff 为 Development；由主协调实际启动命名 Development，完成 developer_handoff 后再启动 fresh-context Verification。实施、独立 QA 和 Human Owner 最终验收尚未完成，本次范围批准不授予总体接受、发布或任务外动作。

SMA-001 r2 与 SMA-003 r1 仍为 draft；SMA-003 软件实施继续等待 SMA-002 清理基线的 Human Owner 验收及其自身精确软件范围批准，不随本次批准启动。
