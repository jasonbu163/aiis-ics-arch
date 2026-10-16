Task ID: CU-004
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved CU-004 r1 on 2026-10-16 (Asia/Shanghai); 命名 Development 可按本 Revision 的 allowlist 实施
Task Namespace: aiis-ics-arch
Classification: root
Capability: CU 表格、表单、弹窗及页面状态设计样例与公共样式的独立消费
Owner: Console UI
Acceptance Chain Reference: CU-004 r1 / Human Owner 范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
Related Task: CU-001; CU-002; CU-003（已验收基线关联，不继承其批准、状态或验收）
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-004：页面设计样例

## 1. 目标与依据

在 CU 私有工作台补齐可演示、可参考的通用表格、表单、弹窗和页面状态，优先组合 Element Plus；公共交付仍以既有八组件、公共主题/样式约定和消费教程为主。其他 Agent 不动。

2026-10-16（Asia/Shanghai）只读核对：当前工作台有壳层、组件和参数三个入口，公共层导出八个展示组件；主题由 `.aw-ui` / `data-aw-theme` 与 `--agent-*` tokens 控制，消费者自建 Vue/i18n 和状态。CU-001/002/003 已验收，但相关源码尚未提交，不能将 HEAD 差异全归本任务。

Human Owner 本轮原话：

> 可以，先在 CU 补齐表格、表单、弹窗，以及加载、空数据、失败状态的设计样例，优先复用 Element Plus，其他 Agent 不动。先落 CU-004 spec，验证能构建、能启动、能引用就行，不做全量回归。

草案创建时仅形成 r1 draft；上述同意方向当时不作为精确 r1 实施批准。PM 未创建 tasks/checklist、修改实现或运行构建/启动/消费验证。Human Owner 于 2026-10-16 明确批准 CU-004 r1，当前交命名 Development 实施；本次仅记录批准事实。

## 2. 范围与需求

### R1. 一个私有页面样例入口

- 在现有显式导航增加“页面样例 / Page samples”，由 `Workbench.vue` 显式引入私有 `PageSamples.vue`；保留原入口及壳层组合。
- 展示一套通用列表表格、一份少量字段的表单、一个含编辑表单及确认/取消操作的样例弹窗；表格使用固定少量脱敏记录，表单有必填及基本合法性校验、提交反馈和重置。
- 编辑/确认/提交只改变当前内存预览并给出样例反馈；取消不提交。样例和弹窗持续清楚标识“设计样例 / Design sample”，不呈现为在线事实或实际操作回执。
- 不接 API、IPC、真实配置、PLC/数据库或文件，不新增业务持久化；沿用 CU 已有 `cu.theme` / `cu.locale` 偏好机制，样例内容刷新后不保留。

### R2. 有限的页面状态展示

- 提供手动切换的正常、加载、空数据、失败四种状态，作用于样例列表/内容区域；状态切换可重复且不依赖网络、后台轮询或真实异常。
- 加载有明确提示，空数据有解释，失败有说明和本地“重试”反馈；重试只恢复样例状态，不调用服务。表单校验、提交反馈亦属于本地演示。
- 表格筛选或分页仅在演示需要时使用 Element Plus 最小配置；不增加远程查询、通用 CRUD、schema 表单或业务框架。

### R3. 公共主题与组合边界

- 表格、表单、输入/选择控件、样例弹窗优先直接组合 Element Plus；不为展示封装整套 Table/Form/Dialog，不强制新增公共 Vue 组件或 store，保留八组件出口、类型和 API。
- 公共 CSS 仅增补样例需要的表格/表单/弹层语义样式及 Element Plus 主题 token 映射，沿用既有 `--agent-*` 色板与作用域；私有页面布局留在 workbench CSS。
- 不重做壳层、卡片、按钮或顶栏；CU-003 的顶栏三个控件 44px 对齐规则保持。
- 弹窗和下拉等弹层若脱离宿主 DOM 作用域，必须显式携带或继承该宿主当前主题（同主题容器或等效最小方案）；明暗切换后弹层文字、表面和边框随宿主一致，不污染全局主题、不依赖 CU 私有状态。
- 主题和语言继续归各宿主；新增可见文案、校验和反馈进入各自对称 zh-CN/en-US locale，公共样式/组件不导入 CU 私有 i18n。

### R4. 独立消费者与教程

- 现有 source-consumer 自行组合少量表格、表单和弹窗用法，使用自有 locale、内存状态及宿主主题；只通过既有 `@aw-ui` / `@aw-ui-styles` 入口引用公共层，不导入 CU workbench、PageSamples 或私有 locale。
- CU 与消费者使用同一份公共组件/样式入口，消费者从自身 Element Plus 依赖组合原生控件；不复制整套工作台、不新增示例工程。
- 更新 CU 与消费者 README pair，说明 Element Plus 组合方式、样式顺序/语义约定、弹层主题范围、宿主文案与状态责任；编译期源码可达、依赖单实例和运行自身 dist 的既有合同保持。

## 3. 精确写入 allowlist

以下实现路径均相对 `automation-world/console-ui/`，仅在 Human Owner 批准精确 r1 后生效；不授权相邻整理。

| 责任面 | 允许路径与限制 |
| --- | --- |
| CU 私有样例 | `src/workbench/Workbench.vue`，仅入口/显式组合；新增 `src/workbench/PageSamples.vue`；`src/workbench/workbench.css`，仅所需样例布局 |
| CU 文案 | `src/locales/en-US/workbench.json`、`src/locales/zh-CN/workbench.json`，仅新增样例所需对称文案 |
| 公共样式 | `src/ui/styles/theme.css`、`src/ui/styles/components.css`，仅 R3 所需 token 映射和语义样式，不改已有色板、壳层/按钮/顶栏规则 |
| 独立消费者 | `examples/source-consumer/src/App.vue`；`examples/source-consumer/src/locales/en-US.json`、`examples/source-consumer/src/locales/zh-CN.json`，仅 R4 的最小用法与对称文案 |
| 使用说明 | `README.md`、`README.zh-CN.md`、`examples/source-consumer/README.md`、`examples/source-consumer/README.zh-CN.md`，仅新增样例及消费合同 |
| 本任务文档 | 当前 `spec.md` 归 PM；批准后本目录 `tasks.md` 归 Development；developer_handoff 后 `checklist.md` 归 fresh-context QA / Verification |
| CU 机械索引 | `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`，仅主协调同步本任务链接、真实状态和下一 gate |

除此以外不写入。尤其禁止修改公共八组件源码、`src/ui/index.ts`、`src/ui/types.ts`、`src/ui/styles/index.css`、`src/App.vue`/main、consumer main、`src/app/README.*`、依赖/锁文件、Vite/Tauri/Rust/端口或生成文件；根/AW 文档、CODE_INDEX、历史 bundles、其他 Agent、frontend-js/backend、真实配置和 Git refs 均不在范围。若实现确需扩大 allowlist，先回 PM 新 Revision 并重新批准。

## 4. 验收标准与验证上限

| ID | 对应需求 | 最小可复核结果 |
| --- | --- | --- |
| AC1 | R1–R4 | 相对受保护的任务起点，diff 限于 allowlist；八组件/API 与原入口保留；样例无 API/IPC/业务持久化，公共样式无私有依赖或全局主题污染 |
| AC2 | R1/R2 | 同轮一次聚焦观察可见页面样例、表格/表单、样例弹窗；四状态可切换、校验和本地提交/重试反馈可见，弹窗可打开/取消/确认/关闭，设计样例标识明确 |
| AC3 | R1–R3 | CU 目录 `pnpm build` 一次退出 0，包含现有类型检查与生产构建 |
| AC4 | R1–R3 | 现有 `pnpm tauri dev` 在当前主机原生启动一次，保留 window-created/ready 日志；同次 dev 服务可用浏览器完成 AC2、代表性明暗/中英切换及弹窗/下拉随宿主主题观察，明确区别原生启动与浏览器交互证据 |
| AC5 | R3/R4 | CU 停止后，source-consumer 目录 `pnpm build` 与 `pnpm preview` 独立引用一次；自身 dist 展示表格/表单/弹窗、宿主主题/语言及本地交互，不需在线 CU，弹层随消费者主题一致 |
| AC6 | R3/R4/治理 | 两组 locale 键对称，四份 README 使用合同双语一致且相对链接有效；任务元数据与 CU 索引诚实，未预写后续角色结论 |

Development 在 tasks 记录实际环境、命令/退出码、一次启动和聚焦观察，以及本任务增量与限制；关键事实永久写入 bundle，临时产物优先 `/private/tmp`。只关闭本任务创建的进程/tab，不停止用户或其他任务进程。

fresh-context Verification 独立审阅精确 r1、Development handoff、当前源码/增量 diff 和上述证据，仅对疑点或缺失项复查；不因角色分离重复完整构建/启动。环境无法完成原生启动时记录阻塞，不以浏览器替代或自动降低验收。

验收只覆盖必要构建、当前主机一次启动和独立引用；不做全量回归、组合矩阵、其他 Agent/CA/TSS 验证、Rust 全套测试、额外 native 打包、跨平台、长时间 GUI 轮询或压力测试。QA 通过后仍交 Human Owner 最终验收。

## 5. 风险、恢复与延后项

- 弹层 Teleport 与 Element Plus 默认变量可能脱离 `.aw-ui` 或混入亮色值；以宿主范围和代表性弹层观察收敛，不通过全局 body/html 主题修改解决，不扩展整个主题系统。
- 当前工作树包含 CU-001/002/003 已验收未提交内容及他人改动；Development 写前保留拟改文件的必要恢复依据，记录本任务增量，不覆盖既有修改，不以 HEAD 全量恢复。
- 回退方案仅撤销本任务实际增量、移除新增样例入口并恢复原组合；先核对并发归属，不能整体 `git restore` CU。该方案不授权当前执行回退。
- 延后侧栏分组、指标卡/信息网格提炼、更多公共组件、DAA/SMA 实际接入、低代码拖拽/设计保存/代码生成、通用 CRUD/schema 表单、npm 发布和依赖升级。
- 排除 SQLite/业务配置、工业 runtime/Flow Core、真实 PLC/数据库、发布部署与 Git/GitHub 操作；当前无需要先决定的业务选项，内部最小实现由 Development 在合同内选择。

## 6. Handoff、批准与修订记录

PM 使用 `aiis` / `project-governance` 定义本范围。Development 与 Verification 按表面加载 `frontend-ui`（按需 DESIGN / FRAMEWORK）、`i18n-workflow`、`desktop-tauri`（既有启动路径）；新增源码头部说明按需遵循 `code-document-indexer`，根索引仍禁写；不加载无关后端/PLC/Rust runtime 实现规范。

Human Owner 于 **2026-10-16（Asia/Shanghai）**明确批准 **CU-004 r1**，本任务批准原话：

> 可以，批准 CU-004 r1，先按原范围实施，其他 Agent 不动，验证能构建、能启动、能引用即可，不做全量回归。

下一 gate：命名 Development 创建 tasks，按已批准 r1 实施并交接 fresh-context 命名 Verification；最终验收由 Human Owner 决定。PM 本轮仅记录批准，主会话负责 CU 双语索引。profile 为 `contract_only`，任务 bundle、串行 handoff 与 diff 审计是必要合同控制，不宣称平台 ACL、强制路由或完整团队激活。范围、allowlist、验收或风险实质变化时须新 Revision 并重新批准。

| 日期 | Revision | 记录 |
| --- | --- | --- |
| 2026-10-16 | r1 | PM 创建 draft；仅元数据/链接/空白检查，未实施、构建、启动或验证引用；精确范围批准 pending |
| 2026-10-16 | r1 | Human Owner 明确批准 CU-004 r1；仅机械记录批准与 Development handoff，范围、allowlist、AC 和草稿历史保留，未实施或追加测试 |

执行依据：[根 AGENTS](../../../../AGENTS.md)、[Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)。归属 [CU PLAN](../../PLAN.md)；背景为 [CU-001](../CU-001-workbench-foundation/spec.md)、[CU-002](../CU-002-topbar-utility-controls/spec.md)、[CU-003](../CU-003-topbar-height-alignment/spec.md) 的完整 bundle，总体依赖见 [AW PLAN](../../../PLAN.md)。
