Task ID: DAA-001
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved exact DAA-001 r1 on 2026-10-17; Development may record D03 baseline and limited consumer-tooling wiring while D02/D04 remain open; final sidebar/view migration and whole-task developer_handoff or QA pass await the independent CU prerequisite; fresh-context Verification and final acceptance remain pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA 阶段 A 的 CU 公共 UI 接入、既有功能归位与兼容验证
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: aiis-ics-arch::DAA-001 r1 scope approval -> CU prerequisite closure and Development handoff -> new fresh-context Verification -> Human Owner final acceptance
Depends On: aiis-ics-arch::ARCH-AW-003 r3 accepted design baseline; CU public grouped-navigation capability gate D02
Related Task: aiis-ics-arch::ARCH-AW-001; aiis-ics-arch::ARCH-AW-003

# DAA 阶段 A：CU 接入与既有界面迁移实施规格

## 1. 本版效力与独立任务身份

2026-10-17（Asia/Shanghai），Human Owner 明确要求：

> 可以，验收 ARCH-AW-003 r3。接下来先出阶段 A 的实施 spec，按 CU 调整 DAA 的布局和既有页面，二级导航的前置依赖也列清楚，批准后再改代码。

该起草决定当时接受 [ARCH-AW-003 r3 文档交付](../../../../plans/ARCH-AW-003-daa-detailed-design/checklist.md)，并授权**先起草本实施 spec**；当时没有批准尚未形成的 DAA-001 r1，也没有授权 CU、DAA 或其他端修改代码。PM 随后提交的 r1 draft SHA-256 为 `1f5d437feb47387b07562f0f96748481d541d1877cac50f268702da45cf2bb6a`。

2026-10-17（Asia/Shanghai），Human Owner 对该精确 r1 明确批准：

> 可以，还是先做阶段 A。批准 DAA-001 r1，按 CU 调整布局并迁移既有功能，不做大量不可用的表单和按钮，完成独立核验。CU 二级导航按独立前置任务处理，新功能后续按 B、C 推进。

**当前为 r1 `owner_approved`。** 本次 PM 仅记录真实批准、当前交接及时间效力；R01–R10、AC01–AC13、59 路径、源码映射和风险保持获批 draft 原文。用户关于不铺设大量不可用表单/按钮的说明已由 §4.2/R07 覆盖，不扩张或重写范围。D01 已满足，D02/D04 尚未解除：实际 Development 可先创建 `tasks.md` 并进行 D03 基线及限定消费工具接线，最终侧栏/视图迁移和整项 `developer_handoff`/QA 通过仍须等待独立 CU 交接。`checklist.md` 只在精确 `developer_handoff` 后由新的 fresh-context Verification 创建；本次批准不等于已实施、QA 或最终验收，不授权创建 CU bundle、修改 CU 或向其他会话发消息。

本任务以 [DAA 详细设计](../../../../docs/AIIS_DAA_Detailed_Design.md#diagnostics) §12/§16 的阶段 A 为依据，交付“消费 CU 公共源码、按目标导航归位**已经存在**的界面与动作”。本版不实现阶段 B 的采集/SQLite 和阶段 C 的事实上传，也不把未来页面字段变成假保存、假采集或假上报。

唯一 bundle 位于 `automation-world/data-acquisition-agent/plans/DAA-001-cu-layout-migration/`，由 DAA 自身 PLAN 管理；AW PLAN 只索引阶段和依赖，根索引只链接此处。它与 ARCH-AW-003 的文档能力、Owner 范围和验收结果不同，因此是 `Classification: root`，**没有 Parent Task ID，也不继承设计任务的批准或 QA**。这是角色交付合同，不是平台 ACL、自动路由或完整 Agent Team 激活声明。

## 2. 必读依据与当前源码基线

本轮 PM 已读根 AGENTS、README/PLAN 双语、canonical lifecycle workflow、实际 pm TOML、AW/DAA/CU 最近 README/PLAN（存在者）、DAA `src/app/README.*`、CU source-consumer 教程、ARCH-AW-003 完整 spec/tasks/checklist 及 774 行 DAA 设计。使用 `aiis`、其 BLUEPRINT/CONTRACTS 与 `project-governance`；技术实现按第 10 节交对应角色，不由 PM 构建、启动或实施。

当前 HEAD 为 `f85bea8bbf36b491968c3dc9a839518a1ed434a8`，实际输入是包含其他会话改动的工作树。不能以 HEAD 代替未提交文件版本，也不能把整个 dirty diff 算作本任务。本轮读取的 DAA 设计 SHA-256 为 `20071f25c374f40ee4600bffda4aef13f37bb86a82c2a6cd1f19e2580370a576`；源文件事实如下，执行时须重新核对并建立修改前基线。

| 源码入口（相对 DAA 根目录，CU 另标） | 已核实的当前行为 |
| --- | --- |
| [App.vue](../../src/App.vue)、[sections.ts](../../src/console/sections.ts)、[types.ts](../../src/console/types.ts) | 自有壳层与 overview/collection/plc/gates 四平铺入口；无 Vue Router，不接 CU。各业务视图接收根层 props/动作。 |
| [useControlAgentConsole.ts](../../src/console/composables/useControlAgentConsole.ts) | 根层一次调用，拥有快照、选中 PLC、分页、busy/结果和操作确认；`onMounted` 只主动刷新一次，未设置轮询定时器。刷新执行 loadRuntimeSnapshot 后再 probeBackend。 |
| [runtimeSnapshot.ts](../../src/services/runtimeSnapshot.ts) | Tauri IPC 集中在此；浏览器用 fallback，控制返回未接受。`probeBackend` 会执行有界 health GET，**不是无网络行为**。没有配置保存/导入导出、日志订阅或事实上传接口。 |
| [现有采集视图](../../src/app/collection/views/status/index.vue) | 逐 PLC 启停读取、启用/暂停旧 raw/latest 写库；全部 PLC 的组合采集启停；运行单元、门禁、collector state、快照策略和 latest DB 组。没有勾选子集调度。 |
| [现有 PLC 视图](../../src/app/plc/views/diagnostics/index.vue) | 选 PLC、显示 endpoint/点位合同摘要、对所选 PLC 一次性读取并分页显示结果；不是持续连接管理、全量点表编辑或单点测试。 |
| [运行总览](../../src/app/runtime/views/overview/index.vue)、[授权诊断](../../src/app/gates/views/authorization/index.vue) | 运行摘要、数据库就绪/heartbeat，以及授权门禁/本地 self-test 的只读展示；没有登录或授权配置写入。 |
| [useAgentTheme.ts](../../src/console/composables/useAgentTheme.ts)、[useAgentLocale.ts](../../src/console/composables/useAgentLocale.ts)、[locales/index.ts](../../src/locales/index.ts) | `daa.theme`、`daa.locale`；主题优先已存值否则系统偏好，语言优先已存值否则浏览器语言。旧主题写 html 的 data-agent-theme；locale 自动聚合模块翻译。 |
| [main.ts](../../src/main.ts)、[app.css](../../src/styles/app.css)、[theme.css](../../src/styles/theme.css) | Element Plus CSS 后加载 DAA 自有全局 tokens/壳卡按钮样式，与 CU 重名类可能相互覆盖。 |
| [Vite](../../vite.config.ts)、[TypeScript](../../tsconfig.json)、[依赖声明](../../package.json)、[锁文件](../../pnpm-lock.yaml) | 当前无 CU alias/dedupe/外部源码 include；锁定 Vue 3.5.38、Element Plus 2.14.2、icons 2.3.2、i18n 9.14.5、Vite 5.4.21、TypeScript 5.9.3、vue-tsc 2.2.12，已与现 CU 消费范例兼容，不需新增依赖。 |
| [Rust 启动](../../src-tauri/src/lib.rs)、[快照服务](../../src-tauri/src/services/runtime_snapshot.rs)、[采集服务](../../src-tauri/src/services/plc_collection.rs) | 启动模式由 env 决定；快照读取可按 gate 查询数据库，不能因命令名称含 snapshot 就推定无外部 I/O。现单 DB 组、统一周期和直库 writer 保持；S7 每次读取建连/断连尚未迁移。 |
| [CU 公共入口](../../../console-ui/src/ui/index.ts)、[类型](../../../console-ui/src/ui/types.ts)、[侧栏](../../../console-ui/src/ui/components/AgentSidebar.vue) | 八组件和展示类型已公开；NavigationItem 仅 id/label/icon，侧栏循环 ElMenuItem，**无公共二级导航**。CU-001–007 的已有接受不包含该能力。 |

本次不读取真实 `.env`/用户 profile 或凭据，不连接 PLC/数据库/API，不运行应用、构建或工程测试。现状以本地源码为据；历史初始化“能启动”的证据不代替本任务的修改前/后对账。

## 3. 范围、依赖与实施次序

### 3.1 边界

包括：CU 八公共组件/公共样式的源码消费、四个右侧页与目标两级导航、既有控制/状态/诊断归位、宿主主题/语言/弹层适配、定向构建/隔离本地浏览器启动/兼容验证及最小文档索引；满足 R09 隔离条件的本地原生 UI smoke 可选。可新增必要的 UI 展示状态（加载/失败/缺功能原因），不改变 Rust/IPC/配置权威或采集行为。

排除：多 PLC 唯一长连接及连接命令、任意勾选批量调度、跨 DB/组独立周期、点位 enabled/单点测试/完整 DB/UDT 导入和偏移算法、YAML 编辑/导入导出新能力、配置保存/应用版本协议、双 SQLite/历史/容量/队列、事实 API/凭据存储/独立上传/补传、Backend/SMA/CA/CU 的具体实现、真实 PLC/数据库/业务 API、旧链路切换、生产回滚、原生生命周期/后台运行/打包签名分发。当前没有的能力不因页面叫“配置”而获得实现授权。

### 3.2 前置依赖与 gate

| ID | 归属及解除条件 | 允许先做/阻塞范围 |
| --- | --- | --- |
| D01 | Human Owner 对精确 `aiis-ics-arch::DAA-001 r1` 的范围批准；实际决定写入本 spec。 | 未批准前仅本 PM draft 和协调索引，不写代码/tasks。 |
| D02 | **CU 自身的独立二级导航任务**，目前没有已创建 Task ID；须由 CU 所属会话单独出 spec、取得精确批准、实施、自检、新 fresh-context QA 及 Human Owner 接受，提供可消费公共合同/版本和消费者证据。这里不编造 Task ID/链接，不创建 CU bundle 或发消息代其立项。 | DAA 获批后可先做 D03 基线、映射核对和限定消费工具接线；最终侧栏接入及整项 `developer_handoff`/QA 通过须等交接。不可在 DAA 私有 fork、原生 ElSubMenu 或配置页内部 tabs 绕过公共依赖。 |
| D03 | Development 修改前固定 DAA 源码/工具链/构建与安全启动、功能和外部 I/O gate 基线；复核本文映射，当前差异与历史失败分别记录。 | 基线准备可与 CU 任务并行；未采到的历史证据不能事后补写成修改前结果。 |
| D04 | D02 交接后在 `tasks.md` 固定 CU 精确 Task ID/Revision/接受依据、Git ref（可用时）及实际公共源码/样式文件清单 SHA-256，记录 DAA alias 解析目标和依赖解析。 | 本版不提前冻结 CU 新 props/types；若合同满足下述能力且本 allowlist 可承接，可按批准范围继续。重大接口/路径/风险/验收变化先回 PM 新 Revision，不静默加文件。 |

D02 的公共能力需求是：保留既有平铺导航兼容；支持分组、可折叠子项、稳定选项身份和选择事件；选中子项时正确显示并展开其父组；宿主提供翻译与当前项，组件不写偏好/业务状态；键盘展开/选择/焦点可用，窄窗可到达各子项，明暗主题一致。CU 应在自身既有平铺范例和独立消费者中提供相应证据；DAA 仍须验证自己的四页接入，不能继承 CU QA 代替 DAA QA。本 spec 不规定 children 属性或事件的具体 API 名称。

推荐顺序：D01 → D03 与 CU D02 各自推进 → D04 → DAA 公共壳/视图迁移 → 定向 self-check → 新 fresh-context Verification → Human Owner 终验。Backend 正式事实合同可在其会话并行讨论，SMA 实现不作为阶段 A 前置。

## 4. 目标页面与旧功能映射

### 4.1 唯一主导航

```text
工作台                         workbench
配置中心（折叠分组，不是右侧页） configuration
 ├─ PLC 配置                  plc-config
 ├─ 点位与采集组配置           points-groups
 └─ 上报与存储                 reporting-storage
```

四个叶子在右侧独立显示；标题、选中叶子与父组展开一致。页内可有折叠详情，但不以横向 tabs 替代三个侧栏子项；不加授权/日志等新一级菜单。pageId 是本任务批准的 UI 内存选择，不是 IPC/业务身份；不新增导航或折叠状态 storage key。默认工作台。顶部保留模式、Backend 探测结果、手动刷新、主题和语言；状态颜色只作展示，不能自动解释为连 PLC/上传成功。

### 4.2 PAGE / ACTION / STATE / IPC / PREFERENCE / I/O-GATE 对账矩阵

下表中的 IPC 名和 facade 是既有合同，阶段 A **逐一保持命令、参数、目标和调用意图**。刷新不增加频率；选择页面/PLC 不发控制。工作台只保留已经支持的逐台与“全部”控制，不新增勾选批量或启动连接的语义。

| 旧入口/对象 | 新页面及动作 | 保留状态/反馈 | 既有 facade / IPC /偏好 | I/O 与兼容边界 |
| --- | --- | --- | --- | --- |
| overview：指标、运行事实、就绪格 | 工作台摘要及可展开运行详情 | raw/latest 计数、heartbeat、生成时间、模式、数据库状态 | runtimeSnapshot、summaryItems、operationItems；`get_runtime_snapshot` | 展示当前快照，不把直库计数标成本地队列/容量。浏览器 fallback 明示非实时证据。 |
| 全局刷新 | CU 顶栏手动刷新 | 加载/刷新失败可见，保留最近成功快照并标陈旧；busy 最终释放 | `refreshRuntime` → loadRuntimeSnapshot → `get_runtime_snapshot` → probeBackend | 既有 Backend health GET 仍有界；不因切页/主题/语言触发额外刷新，不改 endpoint/超时。 |
| collection：PLC 运行单元列表 | 工作台 PLC 列表 | 原 plcKey/endpoint/readState/persistenceState/collectionState/sampleStatus、成功/错误与计数 | `plcCollectionStatus.plcUnits` | 已有多 PLC 列表不等于目标唯一受管理连接；不得标“已保持连接”。 |
| 逐 PLC 启动/停止读取 | 工作台逐行原动作 | 原禁用原因、全局 control busy、请求结果及随后实际快照 | startPlcRead/stopPlcRead → `start_plc_read_for_plc` / `stop_plc_read_for_plc`，参数 `plcKey` | 仍是旧读取 worker，不改成 connect/disconnect；不自动启写库。 |
| 逐 PLC 开启/暂停写库 | 工作台逐行原动作，明确标旧快照写库 | 原 persistenceState、读取前置、write gate 与失败 | enablePlcPersistence/pausePlcPersistence → `enable_plc_persistence_for_plc` / `pause_plc_persistence_for_plc` | 仍直写旧 raw/latest，**不改名为上报或本地 SQLite 保存**；暂停写库保留既有读取行为。 |
| 全部 PLC 启动/停止采集 | 工作台“全部”动作，保留原确认弹窗 | 确认/取消/busy/result、affectedPlcKeys/status/gateErrors、各 PLC 实态 | startPlcCollection/stopPlcCollection → `start_plc_collection` / `stop_plc_collection` | 旧组合读取+写库；停止只影响本 Tauri supervisor，不影响外部 headless。不得改成三个独立新开关。 |
| collector state 与 latest DB 组 | 工作台采集诊断/最新 DB 组 | 原间隔、耗时、延迟、质量/错误、rawSnapshotId、分页 | collectionPage/collectionPageSize、latestGroups | 不是完整 YAML 采集组编辑器或连续日志；质量失败/部分成功不能归并为成功。 |
| plc：目标选择与 endpoint | PLC 配置页只读列表/当前配置；可跳转点位页 | selectedPlcKey、合同路径/加载/endpoint/rack/slot、现有状态 | `setSelectedPlcKey`；共享根状态 | 选择不连接/不读取；没有独立连接测试命令，不能用一次读取冒充测试。编辑/连接测试以能力说明或禁用+原因呈现。 |
| plc：点位合同摘要 | 点位与采集组页，继续先选 PLC | 原总量/可读可写标记/问题/类型摘要；范围如实标明为合同汇总 | plcPointContract、selectedPlcPointSummaryText | 汇总不是完整点位定义清单；可写标记不产生写 PLC 入口；无 enabled/组周期可保存服务。 |
| plc：读取一次及样本表 | 点位与采集组页“读取所选 PLC 样本一次” | plcReadBusy、attempted/succeeded/error、所选目标/结果不匹配时提示、原分页 | readPlcSamplesOnceForPlc → `read_plc_samples_once_for_plc`，参数 `plcKey`；samplePage/samplePageSize | 原动作读取选中 PLC 的配置样本，**不是单点测试**；只读结果不注入生产事实。浏览器无原生桥或 read gate 不满足时禁用。 |
| collection：快照历史策略 | 上报与存储页“现行快照存储策略”只读区 | 路径/version/latestMode/rawHotRetentionDays、点位策略/校验/错误 | `plcCollectionStatus.snapshotPolicy` | 保留实际旧语义，不强行改成三自然月或新 SQLite 天数/容量；不新增策略编辑/写回。 |
| overview：数据库及 Backend 信息 | 上报与存储页现行链路详情，顶栏保留探测摘要 | databaseEnabled/configured、accessMode、Backend/探测结果 | runtimeSnapshot、backendProbe | Backend health 可达不等于事实 API 已接入；无 API/JSON 高级编辑/上报测试或独立上报按钮。 |
| gates：全部授权诊断 | 工作台附属“授权门禁”可展开区 | 启用/高危/上位配置/timeout/failClosed/self-test/provider/operator/scope/resource/approval | authorizationGate 现有只读快照；无新增 IPC | 本地 self-test 与真实授权分清；不改 gate、认证或 operator 策略，也不删失效诊断入口。 |
| 原主题/语言与 Element Plus locale | CU 顶栏两个公共控件；页面、表格、弹窗同步 | 已存偏好/首启 fallback 规则保持；中英互切不重置页面/目标/结果 | 仍只用 `daa.theme`、`daa.locale`；宿主 composables/i18n | 不迁移 CA/TSS/CU 偏好、不读写 cu.*；主题作用域按 R04 调整，不改变业务配置。 |
| 原没有的采集/上报日志流、积压/容量 | 工作台两个反馈分区：采集诊断（当前快照）/上报日志（未接入） | 有数据的既有错误/耗时/反馈照实展示；缺失区明确未实现，不填 0/绿色在线/虚构日志 | 仅现有快照/命令结果，无新增 stream/文件读取/定时器 | 两区宽窗并列、窄窗上下；不保存长期 UI 日志副本。未来真实日志/队列归 B/C。 |

`start_plc_read` 等全体 facade/旧兼容别名仍保持源码和 IPC 注册；本轮不删除尚未暴露为按钮的运行能力。当前 GUI 无配置编辑/导入导出，必须明确告知仍从现行 YAML/env 读取；不伪造这类“旧功能”或新增文件选择/保存命令。阶段 B/C 的说明集中在对应页一处，不要求铺满不能用的表单/按钮。

### 4.3 简单工作流程

首次打开工作台，看到真实当前快照或明确的浏览器/未加载状态。需要查看现行连接配置时进入 PLC 配置，选择 PLC 后可直达点位与采集组查看摘要/执行既有一次读取诊断；上报与存储展示旧快照策略及新上报未接入原因。现有现场配置仍在外部 YAML/env 管理，本阶段页面不承担保存。日常在工作台进行已获现场授权的旧读取/写库/全部采集控制并查看结果；**测试本任务时只用隔离夹具，不操作现场**。

从任意页面返回工作台，已选 PLC、分页、最后结果和全局确认状态不会因 view 卸载重置；修改“选择 PLC”本身仍按原规则重置相关分页/结果。点击导航、折叠菜单、主题或语言均不触发采集/写库/测试/重新启动。新的上传工作流只留能力说明，不能让用户走完假测试后提示成功。

## 5. 编号需求

### R01. 修改前基线与范围对账

Development 在第一笔代码修改前保存源文件/受保护面清单与 SHA、dirty 来源、工具版本、依赖锁定、原 `pnpm build` 及隔离本地启动结果，逐行核对第 4.2 节。启动必须按 R09 先截断健康探测与 IPC 外发。基线失败先记录原命令/环境/实际错误与归因；本范围内 UI 兼容问题可处理，环境或范围外问题不顺手修复。不能拿旧 bundle 的启动结论或修改后的截图充当修改前基线。

### R02. 公共源消费与工程接线

只从 CU `src/ui/index.ts` 与 `src/ui/styles/index.css` 导入八组件及展示类型；选择明确相邻公共源码路径，不复制公共实现到 DAA。DAA Vite 的 `@aw-ui`、`@aw-ui-styles` 指向相邻 CU 对应入口；显式 dedupe Vue/Element Plus/icons/i18n，`server.fs.allow` 最小开放 DAA/CU 公共源，不能扩大到整个用户目录。TypeScript paths/include 解析公共 Vue/TS 到 DAA 自有声明，必要的 node 类型支持限现有依赖。依赖已兼容，本版不升级 package/lock、不建 workspace/npm 发布或引用 CU node_modules 作为消费者依赖。

CSS 顺序为 Element Plus → CU 公共样式 → DAA 页面布局；停止加载并删除被取代的 DAA theme.css，清除 app.css 中与 CU 重复的 tokens/公共壳/卡片/按钮/菜单外观，只保留宿主 reset、页面业务布局和不重定义公共外观的语义样式。公共方案只由 CU 拥有，当前 cardPaddingPx=18 随公共源消费，不复制数值为本地常量。不加载 CU App/main/workbench/locales、design draft 或私有共享样式写入通道。

### R03. 薄适配、页面与状态寿命

既有 layout/topbar/sidebar、Card/Action/RuntimeStatus 文件可保留为宿主薄适配：只做翻译、props/slots/事件和展示 tone 映射，实际渲染使用 CU 公共组件，不保留第二套公共 DOM/样式。DAA 创建 app、组合页面、提供 i18n、主题/语言/状态与动作；CU 不拥有 DAA 业务、IPC、偏好或生命周期。公共 cards 的正文 slot 外可套宿主业务布局容器承接原 bodyClass，不覆盖公共卡片内部 padding 等样式。

根 composable 仍是唯一现有状态/副作用 owner，App 不按 active page 加 key 或重复挂载 owner；拆分视图只接收 props/事件，不能自建快照时钟、invoke、fetch 或 watcher 自动控制。修改 UI 的选择 ID/页面注册属于本版范围，业务 IPC 和源状态 key 不改。保留全局确认弹窗及原确认/取消/执行忙时规则。阶段 A 不新增采集 timer、后台运行或自动刷新功能。

### R04. 主题、语言与弹层作用域

继续 DAA 偏好键、允许值和首启规则；宿主通过 `theme: light/dark` 传入 CU 布局，主题变化不再向 html/body 写公共 tokens 或用旧 data-agent-theme 驱动第二主题。页面 reset 可以设置无业务含义的基础尺寸；不要从 CU 私有偏好读主题。主题/语言切换由公共控件发事件、宿主更新，现 i18n 模块发现和 Element Plus locale 保留。

全局操作弹窗以及 ElMessage 等脱离布局的反馈使用宿主 `Teleport`/显式 `.aw-ui` + `data-aw-theme` 作用域；ElDialog 不再 append 到未带主题的 body，相关弹层/select 要继承当前 scope。ElMessage 的挂载容器须位于同一显式作用域，不修改全局 html/body 变量规避。可访问标签、关闭/确认、disabled/loading/错误和中英文同时验证；不可用操作给可聚焦说明，不能仅靠 disabled 按钮的 hover title。

### R05. 导航与现有内容归位

依 D02/D04 接入 CU 公共二级导航，准确实现第 4 节四叶子与配置分组；保持选中叶子/父级、标题、键盘与窄窗可达。旧授权页改成工作台附属面板，其视图/翻译保留；只删除失去用途的 gates 主导航 manifest。runtime/collection/plc manifests 调整到实际页面，新增同属 plc 的点位页 manifest；不用新路由框架、复制一套业务菜单或第五个主页面。

### R06. 动作、门禁和结果兼容

第 4.2 节所有现有动作/状态/表格/诊断均可达，原全体组合操作确认不弱化，逐台动作不隐式扩大目标。保留浏览器限制、readGateErrors/writeGateErrors/envErrors、busy、读取前置和已启停规则；Rust 仍最终判断准入。结果同时展示 accepted/status/affectedPlcKeys/gateErrors 和实际各 PLC 状态，不把 accepted 单独解释为全体业务成功或把 partial/failed 画成 success。命令异常与刷新失败要显示真实失败/陈旧状态，并结束 loading，保留可再次操作路径；此为宿主反馈适配，不改 facade 或 Rust 错误合同。

读状态、写库状态、质量、诊断状态、Backend 探测相互独立；不能用“上报成功”“已连接”概括旧语义。fallback、本地授权自检、缺失/未加载状态显式标示来源；没有积压/容量字段就显示未提供，不把 unknown 当 0。敏感口令/token/完整连接串不进日志、截图、预览或导出。

### R07. 页面能力缺口与数据真相

PLC/点位组/上报存储页只实现已存在的数据/动作；不存在的配置编辑/保存/导入导出/偏移/启用开关/连接测试/单点测试/独立上传/存储限额/只读事实批次预览等按第 3 节明确延期。可用说明或禁用且说明原因，不增加假表单提交、随机数据、模拟成功或上线默认开启的 mock 通道。旧 rawHotRetentionDays/policy 仍按当前语义展示，不替后端应用新三自然月规则。

### R08. 适配、日志分区与可访问性

页面组合采用 CU 卡片和原生 Element Plus（表格 `aw-data-table` 等公共约定），宿主只布局。工作台反馈两区宽窗并列、窄窗上下，现有采集快照与上报未接入的含义清楚；支持长 endpoint/错误/英文及空列表，表格局部横滚，分页和操作能到达，焦点不被隐藏菜单/弹窗吞掉。沿用当前 Tauri 最小窗口 960×640，另以浏览器窄视口检查公共响应式；不改窗口限制或承诺移动端/原生平台行为。尺寸是验证样例，不是新增公共设计常量。

### R09. 聚焦、安全和可重做验证

只使用批准范围内本地无业务 I/O 的夹具验证。浏览器载入前通过可用自动化工具的初始化/拦截能力在 IPC/fetch 边界提供脱敏快照/回执，截断 Backend health 与所有非静态业务请求，记录请求/命令次数和参数；只允许自身本地静态资源加载。不能先挂载真实 App 再补拦截，也不修改 runtimeSnapshot.ts 或真实 env 来做长期产品 mock。隔离夹具/辅助脚本/产物放 `/private/tmp`；可复查步骤和结果摘要进入 tasks/checklist，临时目录不作唯一证据。

夹具至少覆盖：浏览器无原生桥、无 PLC/合同缺失、两 PLC 混合实态、read/write gate 关闭、单次读成功/失败/未执行、控制 accepted/blocked/partial、IPC reject、刷新失败/陈旧、操作中切页/重复点击、旧全体确认取消/确认和目标参数。对照 source 调用表验证未新增控制、不扩大目标、busy 结束、选择/分页/结果与主题语言切换稳定；关键切页动作之后不得额外 invoke/fetch/自动启动。用实际渲染交互与调用断言核对非平凡映射/寿命，纯文本关键词检查不足。

Human Owner 对本版的精确批准同时覆盖源码构建、上述隔离浏览器预览/启动，以及满足隔离条件的可选本地 Tauri/WebView UI smoke，不另设通用启动批准 gate。原生 smoke 启动前须证明：使用显式绝对 DAA_ENV_FILE/DAA_PROFILE_DIR 和脱敏配置，处理继承 env 高优先级，autostart=stopped，全部 PLC/数据库/授权外发 gate 关闭，健康探测已截断。若必要拦截/隔离能力不可用、不能证明无外发或需要修改受保护运行时才能实现，则不启动，按具体原因记录原生证据 deferred；浏览器无外发交互证据仍必需，浏览器伪桥不能冒充原生。可选原生证据延期不阻止本版约定的浏览器 UI 交付。真实 PLC/数据库/API、生产/切换、原生生命周期/后台托管/打包分发、headless 采集/长稳和现场性能仍另行批准。

### R10. 文档、角色与差异收敛

仅更新本地 README pair 的 CU 消费/运行边界、src/app pair 的实际页面归属及 CODE_INDEX 的 DAA 条目；保持原身份/端口/命令与配置发现语义。DEV 真实计划/self-check/失败/限制写 tasks；新 fresh-context QA 只验证并写 checklist，不能修实现。索引仅由主协调据已存在角色事实机械同步。不改 ARCH-AW-003 已接受正文/证据；全任务仍为精确 DAA-001 r1，不新增平行根 bundle。

## 6. 精确文件 allowlist 与角色所有权

下列路径均相对仓库根。`M`=允许最小修改；`N`=允许按本规格新增；`D`=仅因本次替代而移除。未发生必要改动的文件无需为了覆盖 allowlist 而重写。当前 PM **只写本 spec**；代码表仅在 D01 后供 Development 使用。无目录通配；变更路径/需求/风险实质扩大须新 Revision。

| 操作 | 精确路径 | Development 允许内容 |
| --- | --- | --- |
| M | `automation-world/data-acquisition-agent/src/App.vue` | 四页/全局状态与弹层组合，保唯一 owner。 |
| M | `automation-world/data-acquisition-agent/src/main.ts` | 公共 CSS 顺序及必要既有 Element Plus 组件注册。 |
| M | `automation-world/data-acquisition-agent/src/layouts/AgentLayout.vue` | CU Layout 薄组合；宿主页面选择/侧栏可达。 |
| M | `automation-world/data-acquisition-agent/src/components/shell/AgentSidebar.vue` | CU Sidebar 薄适配，消费 D04 合同。 |
| M | `automation-world/data-acquisition-agent/src/components/shell/AgentTopbar.vue` | CU Topbar/ThemeToggle/LanguageSwitch 和已有顶栏动作。 |
| M | `automation-world/data-acquisition-agent/src/components/shell/RuntimeStatusCapsule.vue` | CU StatusCapsule 的宿主展示映射。 |
| M | `automation-world/data-acquisition-agent/src/components/console/ConsoleCard.vue` | CU Card 的翻译/slots 薄适配。 |
| M | `automation-world/data-acquisition-agent/src/components/console/ConsoleActionButton.vue` | CU ActionButton 的翻译/事件薄适配。 |
| M | `automation-world/data-acquisition-agent/src/components/console/ConsoleMetricCard.vue` | 指标内容按 CU 卡片承载，不保第二卡片外观。 |
| M | `automation-world/data-acquisition-agent/src/components/console/ConsoleOperationDialog.vue` | 原确认行为保留，弹层主题/可访问性。 |
| M | `automation-world/data-acquisition-agent/src/components/console/PlcRuntimeUnitPicker.vue` | 既有选择和状态保留，公共表格样式/窄窗。 |
| M | `automation-world/data-acquisition-agent/src/console/types.ts` | 四叶子/配置分组及必要 UI 展示类型，不改 wire DTO。 |
| M | `automation-world/data-acquisition-agent/src/console/sections.ts` | 唯一导航注册与页面归位。 |
| M | `automation-world/data-acquisition-agent/src/console/composables/useControlAgentConsole.ts` | UI pageId、共享状态输出、刷新/异常展示与反馈 scope；不改 IPC 意图/采样逻辑。 |
| M | `automation-world/data-acquisition-agent/src/console/composables/useAgentTheme.ts` | 保偏好规则，暴露宿主主题给 CU，停用全局旧主题驱动。 |
| M | `automation-world/data-acquisition-agent/src/console/composables/useAgentLocale.ts` | 保偏好规则，向 CU 提供当前语言/目标可访问标签。 |
| M | `automation-world/data-acquisition-agent/src/app/runtime/manifest.ts` | 工作台元数据。 |
| M | `automation-world/data-acquisition-agent/src/app/runtime/views/overview/index.vue` | 现有总览归位工作台，附属现有诊断/面板组合。 |
| M | `automation-world/data-acquisition-agent/src/app/collection/manifest.ts` | 上报与存储页元数据；原采集面板不再作一级入口。 |
| M | `automation-world/data-acquisition-agent/src/app/collection/views/status/index.vue` | 工作台既有采集面板，策略移出、旧动作/状态保留。 |
| M | `automation-world/data-acquisition-agent/src/app/plc/manifest.ts` | PLC 配置只读页元数据。 |
| M | `automation-world/data-acquisition-agent/src/app/plc/views/diagnostics/index.vue` | 连接配置只读/选择区，点位诊断内容迁至同模块子页。 |
| N | `automation-world/data-acquisition-agent/src/app/plc/points-manifest.ts` | 同模块点位与采集组页元数据。 |
| N | `automation-world/data-acquisition-agent/src/app/plc/views/points/index.vue` | 既有合同摘要/一次读取/样本表，未实现配置说明。 |
| N | `automation-world/data-acquisition-agent/src/app/collection/views/storage/index.vue` | 旧策略/链路只读及未接入上报/本地存储说明。 |
| D | `automation-world/data-acquisition-agent/src/app/gates/manifest.ts` | 只删除被附属诊断取代的主导航 manifest；保留 gates 视图/locales。 |
| M | `automation-world/data-acquisition-agent/src/styles/app.css` | 去掉被 CU 替代的公共样式，只留宿主 reset/页面布局/业务语义。 |
| D | `automation-world/data-acquisition-agent/src/styles/theme.css` | 公共主题取代，删除并移除导入，无私有副本。 |
| M | `automation-world/data-acquisition-agent/vite.config.ts` | 公共源 alias/dedupe/fs allow，既有端口/strictPort 保持。 |
| M | `automation-world/data-acquisition-agent/tsconfig.json` | 公共入口 paths/include 与消费者依赖类型解析。 |
| M | `automation-world/data-acquisition-agent/tsconfig.node.json` | 仅 Vite 公共源路径所需现有 node 类型/配置支持。 |
| M | `automation-world/data-acquisition-agent/src/locales/zh-CN/navigation.json` | 四页/分组文案。 |
| M | `automation-world/data-acquisition-agent/src/locales/en-US/navigation.json` | 与中文键/占位符对称。 |
| M | `automation-world/data-acquisition-agent/src/locales/zh-CN/common.json` | 目标动作/可访问/全局反馈文案。 |
| M | `automation-world/data-acquisition-agent/src/locales/en-US/common.json` | 与中文对称。 |
| M | `automation-world/data-acquisition-agent/src/app/runtime/locales/zh-CN.json` | 工作台/运行与快照来源、状态反馈。 |
| M | `automation-world/data-acquisition-agent/src/app/runtime/locales/en-US.json` | 与中文对称。 |
| M | `automation-world/data-acquisition-agent/src/app/plc/locales/zh-CN.json` | 两个 PLC 域页面/只读与延期说明。 |
| M | `automation-world/data-acquisition-agent/src/app/plc/locales/en-US.json` | 与中文对称。 |
| M | `automation-world/data-acquisition-agent/src/app/collection/locales/zh-CN.json` | 既有动作准确用语/存储只读/日志缺口说明。 |
| M | `automation-world/data-acquisition-agent/src/app/collection/locales/en-US.json` | 与中文对称。 |
| M | `automation-world/data-acquisition-agent/README.md` | CU 公共消费、四页/兼容边界和验证说明。 |
| M | `automation-world/data-acquisition-agent/README.zh-CN.md` | 与英文说明对称。 |
| M | `automation-world/data-acquisition-agent/src/app/README.md` | 真实页面/模块归属与状态 owner，不建立新治理规则。 |
| M | `automation-world/data-acquisition-agent/src/app/README.zh-CN.md` | 与英文说明对称。 |
| M | `CODE_INDEX.md` | 仅既有 DAA 条目的页面/公共源/本地 PLAN 结构摘要，保其他并发条目。 |

| 阶段/归属 | 精确路径 | 允许内容 |
| --- | --- | --- |
| PM / Human Owner | `automation-world/data-acquisition-agent/plans/DAA-001-cu-layout-migration/spec.md` | 本规格及真实范围批准/Revision 历史。 |
| Development，D01 后 N | `automation-world/data-acquisition-agent/plans/DAA-001-cu-layout-migration/tasks.md` | 实施计划、D03/D04、真实变更/self-check/失败/限制/精确 handoff。 |
| 新 fresh-context Verification，developer_handoff 后 N | `automation-world/data-acquisition-agent/plans/DAA-001-cu-layout-migration/checklist.md` | 独立验证、差异/保护审计、verdict 和真实 Human Owner 终验。 |
| 主协调 M | `automation-world/data-acquisition-agent/PLAN.md` | 仅 DAA-001 的真实状态/下一 gate。 |
| 主协调 M | `automation-world/data-acquisition-agent/PLAN.zh-CN.md` | 对应中文行。 |
| 主协调 M | `automation-world/data-acquisition-agent/plans/README.md` | 仅 DAA-001 catalog 行，存在后才链接角色文件。 |
| 主协调 M | `automation-world/data-acquisition-agent/plans/README.zh-CN.md` | 对应中文行。 |
| 主协调 M | `automation-world/PLAN.md` | 仅 DAA 子工程阶段/依赖行。 |
| 主协调 M | `automation-world/PLAN.zh-CN.md` | 对应中文行。 |
| 主协调 M | `PLAN.md` | 仅 DAA-001 索引行，链接唯一子工程 bundle。 |
| 主协调 M | `PLAN.zh-CN.md` | 对应中文行。 |
| 主协调 M | `plans/README.md` | 仅 DAA-001 指针行，不建根 bundle。 |
| 主协调 M | `plans/README.zh-CN.md` | 对应中文行。 |

以上共 59 个精确路径：Development 实现/说明 46、tasks 1；PM spec 1；QA checklist 1；主协调索引 10。治理初始化由主协调本次最小建立 DAA PLAN/catalog pair 并修正 README 生命周期入口；这不是代码实施。ARCH-AW-003 真实终验收尾与 AW 既有 CU 汇总纠偏属于本次独立协调事实，不授予 DAA Development 修改那些历史任务/其他子工程记录的权限。

**受保护面**包括 `src/services/runtimeSnapshot.ts`、`src/locales/index.ts`、全部 `src-tauri/`/Rust/Cargo/Tauri config/capabilities、package.json/pnpm-lock/workspace、env/YAML/profile/数据、全部 CU 公共/私有源码与其治理、Backend/SMA/CA/tools、已接受 DAA/SMA/AW 设计、ARCH-AW-003 bundle、根 AGENTS/workflow/skills/ROADMAP/其他任务。除表中两项 D 外不得移动或删除既有文件。不新增正式产品 mock、测试框架、运行时依赖、repo 输出/原型或独立测试工程；必要隔离验证 helper 在 `/private/tmp` 并由角色记录实际事实。若现有工具无法给出必需兼容证据，报告具体 blocker，不偷偷增依赖/开现场 gate。

## 7. 验收标准

下列是本版已批准、D02/D04 解除后须满足的实施验收；本次仅记录范围批准，尚无本版 Development/QA 通过结果。

| AC | 可验证交付 | 需求 |
| --- | --- | --- |
| AC01 | D03 的修改前源码/构建/隔离启动/功能/gate 基线真实存在且可对读；失败与历史/环境/新回归分开，原工作树改动保留。 | R01 |
| AC02 | D02 提供真实独立批准/新 QA/Owner 接受和消费者证据；D04 固定精确公共源/依赖解析，DAA 无私有二级导航替代、没有提前冻结或冒认 CU API。 | R02/R05 |
| AC03 | 编译经 CU 两公共入口消费全部八组件/展示类型，alias/dedupe/fs/types 正确；无 CU 私有导入/在线进程/node_modules 前置、无重复公共主题/源码副本；DAA 自身 dist 可独立静态启动。 | R02–R03 |
| AC04 | 只有工作台和配置中心两一级项及三个准确子页，四个右侧独立页/选中标题/父展开/键盘/窄窗一致；授权诊断在工作台仍完整可达。 | R05/R08 |
| AC05 | 第 4.2 节逐项 old→new 内容/动作/状态对账无丢失；逐台/all 的原命令/参数/确认/门禁及 headless 边界保持，partial/blocked/reject 如实展示。写库未标为上报，读取未标为长连接。 | R06 |
| AC06 | 只有一个根状态/副作用 owner；切页、折叠、主题/语言不发新增控制或 refresh，不丢目标/分页/结果/全局操作状态；选择 PLC 的原重置规则保持；无新采集/刷新定时器。 | R03/R06 |
| AC07 | `daa.theme`/`daa.locale` 和首启规则保持，CU 控件/Element Plus/页面/弹窗/消息随主题语言同步；无 cu.* 访问、html/body 公共主题覆盖、翻译裸 key、键/占位符不对称。 | R04 |
| AC08 | 四页能力缺口、fallback/自检/快照来源真实；无假配置保存/导入导出/单点测试/上报/容量/日志成功，旧策略未被新三自然月/SQLite 规则替换。 | R07 |
| AC09 | 原读取/写库/全体控制确认、loading/禁用原因/结果以及空/错误/部分/陈旧均可用；IPC 异常和刷新失败能结束 busy 并反馈，不用按钮点击代实际状态。 | R06/R09 |
| AC10 | 日夜/中英文、当前最小原生窗口对应视口及浏览器窄窗中导航/长文本/表格局部滚动/分页/确认和两反馈区可达；采集快照与上报未接入区别清楚，弹层无未主题化脱出。 | R04/R08 |
| AC11 | 修改后 `pnpm build`（包含 vue-tsc）通过；采用现有工具的隔离本地浏览器启动和 R09 夹具交互/命令次数参数断言覆盖。真实 health/PLC/DB/API 外发为零，验证前拦截可证明；浏览器/原生证据与未运行原因分开。 | R01/R09 |
| AC12 | 精确路径及两项删除合法、未跟踪新增全文纳入；受保护源码/锁文件/配置/设计/其他工程指纹或并发归因通过。README pair/CODE_INDEX 最小一致，本地链接/锚点/围栏与 JSON locale 解析/键占位符检查通过。 | R10/第6节 |
| AC13 | 实际 Development 在 tasks 记录精确批准/依赖/版本、完整差异、自检命令退出码、资源和 handoff；之后新的 fresh-context Verification 独立形成 verdict，QA 不改实现；QA pass 只进入 Human Owner 终验。 | R10 |

## 8. 后续验证方法与证据边界

在 DAA 自身目录使用既有 pnpm 与锁文件；依赖缺失时可按现有 `pnpm install --frozen-lockfile` 恢复消费者依赖，不升级或安装 Agent 辅助包到项目环境。执行前核查当前文件和工具链，不把本文锁版本当将来永不变化的环境事实。主要命令为 `pnpm build`、已准备好 R09 拦截后的 `pnpm dev` 或 `pnpm preview`；按实际使用选择，不同时重复启动同一端口。分别记录修改前后退出码/日志、导航交互/受控命令轨迹和截图（工具可取得时），不为装饰性差异编写大量镜像测试。

默认使用 DAA dev 15191/preview 14191 及 strictPort；先识别端口/进程归属，遇已有实例不停止它或占用它的资源，可以隔离命令行端口并记录浏览器 origin/偏好隔离，不修改产品固定端口。`pnpm tauri dev` 会自行启动 `pnpm dev`，不可叠加。Tauri config 保持原字节；可选原生 smoke 仅按 R09 在已证明隔离后执行，缺少隔离就记录原因并延期。CU 进程不作为测试前置，不为证明独立性停掉别人开的 CU。

fresh-context QA 消费批准 spec、tasks、D03/D04 与完整当前 diff/新增文件、self-check 输出/限制，独立核对 AC01–AC13，重复有必要的定向浏览器/构建与调用证据；DEV 截图/脚本 pass、CU QA 或源文本扫描不能独立替代结果。未取得必要浏览器交互/拦截证据或 CU 交接就记精确 qa_blocked，不虚报通过。可选原生 smoke 按 R09 区分实际证据与具体延期原因，不作浏览器定义的本版 UI 交付阻塞项；原生生命周期/打包分发、真实设备/数据库/API和生产交付仍排除，不因此追加整仓/Rust/数据库/长稳矩阵。

Development/Verification 列出本任务创建的服务器 PID/端口、临时夹具/报告/profile 归属和保留原因；停止自己的预览服务器，保持他人进程/真实 profile 不变。验收后由主协调按证据和后续依赖处理临时资源，不清未知 `/tmp`、分支或 worktree。实际命令、结果、版本/指纹和限制写入各角色文件，临时路径不是唯一可审阅事实。

## 9. 风险、回退与延期

| 风险 | 本版处理 / 停止条件 |
| --- | --- |
| CU 二级能力未交付或接口漂移 | D02/D04 串行 gate；只先做可独立准备。不能给缺导航的任务终验或自行修改 CU；超 allowlist/实质范围变化回 PM 新 Revision。 |
| 旧 CSS 与 CU 同名覆盖、弹层漏作用域 | 删除旧主题源/导入，app.css 去公共重复，仅保宿主语义；明暗+弹窗/消息实看，不能用覆盖 CU 私有选择器补洞。 |
| 四页外观被误认新完整 DAA | 页内明确当前只读/旧写库/未接入；既有行为、阶段 B/C 缺口和使用方式直接可见。 |
| view 重建导致重复快照/health/采集或状态丢失 | 根 owner 不重挂；R09 比较调用次数/参数、操作中切页与状态恢复。生产 facade/Rust 不变。 |
| 启动读到真实配置或健康探测外发 | 浏览器先截断全部业务请求/IPC；不读真实 profile。可选原生 smoke 先证明显式配置/继承 env/autostart/外发 gate/健康探测全部隔离；无法满足或需改受保护运行时则不启动，记录具体原因并延期原生证据。 |
| 基线失败、端口冲突或其他会话改动 | 保存起点、逐路径归因、只处理本范围；不“修好”无关依赖/Rust/环境。证据不足报 blocker。 |

回退材料包括获批前后 UI/配置接线 diff、依赖公共版本清单和页面/动作对账。需要回退时只反向应用**本任务已确认的 UI 与接口映射差异**并重新聚焦构建/界面核对，保留当前并发修改；不 reset 整工作树、不撤销 CU 独立任务、不迁移/清空用户 YAML/env/偏好/数据或重置队列/序号/ack。实际生产切换、真实资源删除和现场回退仍另行批准。

阶段 B/C 的接口、类型/偏移支持、长连接/公平周期、SQLite/schema/容量/激活、可靠采样/上传/回执/顺序和后端/SMA配合继续以 [已接受详细设计](../../../../docs/AIIS_DAA_Detailed_Design.md#handoff) 为目标，另立实施 spec。阶段 A 验收只证明本版公共 UI 接入与既有功能兼容，不证明目标现场链路、持久性或业务闭环。

## 10. 技术 skill、交接与批准历史

| 后续实际表面 | 必需 skill / 角色边界 |
| --- | --- |
| DAA Vue/CU 消费/样式/布局与定向浏览器验证 | Development / Verification 使用 `frontend-ui`（按 DESIGN/FRAMEWORK 适用部分）、`i18n-workflow`；保持现有工业运维对象/状态，不另选设计系统。 |
| Tauri 消费与桥接/原生证据判断 | `desktop-tauri`；本版只保留 IPC 调用语义和源配置，不修改 Rust/capabilities；进入 Rust runtime/PLC/OS 改动先另立范围并用 `rust-runtime`。 |
| 新关键源码头/真实结构索引 | `code-document-indexer`，仅当前 DAA allowlist/条目，不全仓生成。 |
| bundle/索引与跨端边界 | `project-governance` + `aiis`；PM spec、DEV tasks、QA checklist 各自归属。 |
| 实际 browser 自动化 | 使用当时可用的 purpose-built 浏览器工具及其规则；若选择 terminal Playwright 再加载对应 skill，不新增项目测试框架/依赖。 |

本 PM 未执行上述实现/测试工作。Frontend skill 的后端组合规则只有在修改服务/API合同表面时才适用；本版只消费已存在 IPC，不新增 Backend 工作。后续采集/点位/正式 API 分别路由 rust-runtime/plc-point-mapping/backend-arch；不在 UI 迁移中恢复 Celery/Redis。

修订/批准记录：

- 2026-10-17，r1 draft：由 Human Owner 第 1 节请求起草阶段 A spec；实际 PM 只写本文件，依据当前源码形成页面/状态/IPC/偏好/gate 映射、59 路径分阶段 allowlist、CU 独立依赖和 13 项 AC。本次是 PM 自检，不是 Development、独立 QA 或范围批准。
- 2026-10-17，r1 owner_approved：Human Owner 按第 1 节原话精确批准 SHA-256 为 `1f5d437feb47387b07562f0f96748481d541d1877cac50f268702da45cf2bb6a` 的 r1 draft；本次 PM 仅补记批准、交接和时间效力，R01–R10、AC01–AC13、59 路径、源码映射和风险原文不变。D01 已满足，D02/D04 尚未解除；不以设计任务终验或本批准替代 CU 独立前置。
- Development handoff、D02/D04 闭合、新 fresh-context Verification 与 DAA-001 最终验收：pending。

当前交给实际 Development 消费精确已批准 `DAA-001 r1`、完整已形成 bundle、起点和 CU gate。D02/D04 未解除时，只先记录 D03 基线及限定消费工具接线；不得实施最终侧栏/视图迁移、宣布整项 developer_handoff 或 QA 通过，也不替 CU 立项或实施。独立 CU 接受交接并按 D04 固定公共版本后，才继续批准范围内的迁移与定向 self-check；主协调在精确 developer_handoff 后显式启动新的实际 Verification（工具支持时 `fork_turns="none"`），其独立 verdict 后再请 Human Owner 终验。本 spec 不授权发布、部署、Git 推送、现场外发或联系 Backend/SMA/CU 的其他用户会话。
