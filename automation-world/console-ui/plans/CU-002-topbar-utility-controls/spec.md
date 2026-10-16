Task ID: CU-002
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved CU-002 r1 on 2026-10-16 (Asia/Shanghai); 命名 Development 可按本 Revision 的 allowlist 实施
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 可复用的主题与语言切换控件，以及 CU 顶栏与独立消费者对它们的使用
Owner: Console UI
Acceptance Chain Reference: CU-002 r1 / Human Owner 范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
Related Task: CU-001（已验收的工作台与公共源码基础；不继承其批准、状态或验收）
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-002：顶栏主题与语言公共控件

## 1. 目标与依据

参考 `frontend-js` 的两个顶栏工具控件，将 CU 当前普通操作按钮形态的明暗、中英切换改为专用公共组件；CU 工作台和自身 source-consumer 使用同一出口。顶栏整体布局、其他公共组件和其他 Agent 保持现状。

2026-10-15 源码核对：CU 的两个按钮位于 `Workbench.vue` 的 `AgentTopbar` actions 插槽，均使用 `ConsoleActionButton`；公共层已有 `UiTheme` 与 `.aw-ui` / `--agent-*` 主题合同。参照组件分别使用 44px 圆形 Moon 图标按钮，以及 44px 高、同时显示“中 / EN”并高亮当前语言的胶囊。参照工程的 Pinia、i18n 和点击 div 实现不属于复用合同。

Human Owner 本轮要求：

> 可以，就参考 frontend-js 调整这两个按钮，做成 CU 公共组件，顶栏整体布局先不动，其他 Agent 也不动。先落 CU-002 spec，验证能构建、能启动、能引用就行，不用全量回归。

2026-10-15 据此创建 draft spec，当时精确 r1 尚待范围批准，未创建 tasks/checklist、实施或运行应用验收。Human Owner 于 2026-10-16（Asia/Shanghai）明确批准 CU-002 r1，当前交命名 Development 实施。CU-001 保持已验收历史，CU-002 是独立调整任务。

## 2. 范围与需求

### R1. 两个专用公共控件

- 新增并从 `src/ui/index.ts` 导出 `ThemeToggle`、`LanguageSwitch`；保留既有六组件、展示类型和公共样式入口。
- `ThemeToggle` 参考 [frontend-js ThemeToggle](../../../../frontend-js/src/components/ThemeToggle.vue)：44 × 44px 圆形、20px Moon 图标，两种模式均使用 Moon；暗色状态用强调底色区分，提供边框、文字与悬停反馈，不再显示“日间/夜间”按钮正文。
- `LanguageSwitch` 参考 [frontend-js LangSwitch](../../../../frontend-js/src/components/LangSwitch.vue)：44px 高的圆角胶囊，默认展示“中 / EN”，高亮当前语言，保留紧凑间距、边框与悬停反馈。
- 外观结构参考 frontend-js，颜色、表面、边框、阴影和强调前景适配 CU 现有 `--agent-*` tokens；公共样式限于新增控件规则并处于 `.aw-ui` 作用域，不替换 CU 色板、不调整既有顶栏或通用操作按钮规则。
- 使用原生 `button type="button"` 或具备等价语义的 `ElButton`，支持键盘激活、可见焦点及可访问名称。主题按钮表达当前暗色选中状态；不能照搬点击 div 而丢失按钮语义。

### R2. 受控状态与文案合同

| 组件 | 公共输入 | 公共事件 |
| --- | --- | --- |
| `ThemeToggle` | `theme: UiTheme`；`label: string`，为已翻译的目标主题切换提示，同时用于 tooltip 和可访问名称 | `toggle`，只表达切换请求，无内部持久化 |
| `LanguageSwitch` | `locale: 'zh-CN' \| 'en-US'`；`zhLabel: string`、`enLabel: string`，由宿主提供“中”“EN”；`label: string`，为已翻译的目标语言切换提示，同时用于 tooltip 和可访问名称 | `toggle`，只表达切换请求，无内部持久化 |

- 两个组件只呈现传入状态并发出事件；宿主负责实际主题/语言变化。不增加公共 store、语言框架或自动探测机制。
- 公共组件不得直接或传递依赖 CU 工作台、App/main、私有 i18n、Pinia、Tauri/IPC、runtime、工业配置，也不读取或写入 localStorage、不挂载应用。
- CU 与消费者各自拥有对称 zh-CN/en-US locale；新增显示标签、目标主题/语言 tooltip 与 aria 文案通过翻译结果传入，不在公共组件内硬编码用户可见文案。
- 工作台沿用现有 `cu.theme` / `cu.locale` 宿主持久化，消费者继续由自身状态管理且不新增持久化；不迁移其他 Agent 偏好。

### R3. 最小接入与说明

- 工作台在原 `AgentTopbar` actions 插槽原位置替换两个按钮，并从公共入口导入；保留设计样例胶囊、标题/副标题、侧栏操作、顺序与整体布局。
- 不修改 `AgentTopbar.vue`、布局组件、已有响应式规则或其他组件展示；仅移除替换后无用的工作台图标导入。
- 现有 `examples/source-consumer/src/App.vue` 通过 `@aw-ui` 引用这两个控件，使用消费者自己的主题、语言、文案与事件；仍只通过既有公共代码/样式入口消费。
- CU 与 source-consumer README pair 同步新增出口和简短使用合同，说明受控状态、文案、样式及运行独立性。不建设新示例应用或实际接入其他 Agent。

## 3. 精确写入 allowlist

下列路径均相对 `automation-world/console-ui/`，仅允许完成 R1–R3 所需变更，不授权顺手整理：

| 责任面 | 允许路径与限制 |
| --- | --- |
| 公共组件 | `src/ui/components/ThemeToggle.vue`、`src/ui/components/LanguageSwitch.vue`，新增本任务两组件 |
| 公共出口与样式 | `src/ui/index.ts`，仅新增出口；`src/ui/styles/components.css`，仅新增这两个控件及其状态/焦点规则 |
| CU 宿主 | `src/workbench/Workbench.vue`，仅两控件替换、输入/事件绑定及相应导入；`src/locales/en-US/workbench.json`、`src/locales/zh-CN/workbench.json`，仅所需对称文案及替换产生的无用键清理 |
| 独立消费者 | `examples/source-consumer/src/App.vue`；`examples/source-consumer/src/locales/en-US.json`、`examples/source-consumer/src/locales/zh-CN.json`，仅两控件消费、状态/事件绑定及所需对称文案 |
| 使用说明 | `README.md`、`README.zh-CN.md`、`examples/source-consumer/README.md`、`examples/source-consumer/README.zh-CN.md`，仅新增出口/使用说明 |
| 本任务文档 | `plans/CU-002-topbar-utility-controls/spec.md` 归 PM；批准后 `tasks.md` 归 Development；developer_handoff 后 `checklist.md` 归 fresh-context QA / Verification |
| CU 机械索引 | `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`，仅由主协调同步本任务链接、真实状态与下一 gate |

除此以外不写入。尤其不改 `src/ui/types.ts`、`src/ui/styles/theme.css`、`src/ui/styles/index.css`、`src/app/README.*`、依赖/锁文件、构建配置、端口、Tauri/Rust 或生成 schema；不修改 CU-001 bundle、根/AW 文档与索引、CODE_INDEX、frontend-js、CA/DAA/SMA 或其他工程。公共源码层次及入口不变，本任务不扩大为文档索引重建。

## 4. 验收标准与验证上限

| ID | 对应需求 | 最小可复核结果 |
| --- | --- | --- |
| AC1 | R1/R2 | 两组件通过公共出口可达；输入/事件符合合同，传递依赖和存储边界正确；既有六组件和主题合同保留，diff 限于 allowlist |
| AC2 | R1–R3 | 一次聚焦 smoke 可见圆形 Moon 与“中 / EN”胶囊；主题切换、语言高亮与目标提示随宿主状态更新；普通点击和键盘可激活，无需组合截图或全页面矩阵 |
| AC3 | R1–R3 | CU 目录 `pnpm build` 退出 0，包含现有类型检查与生产构建；不要求新增镜像实现细节的单元测试 |
| AC4 | R3 | 按现有 `pnpm tauri dev` 路径在当前主机启动 CU 桌面窗口；在同一轮 smoke 核对 AC2。可使用该次 dev 服务的浏览器前端观察交互，但必须区分原生启动与浏览器观察证据，不以浏览器冒充原生窗口启动 |
| AC5 | R2/R3 | source-consumer 目录 `pnpm build` 退出 0；本任务创建的 CU 进程结束后，消费者以现有 `pnpm preview` 运行自身 dist，两组件正常呈现并响应自身宿主事件，不依赖在线 CU |
| AC6 | R2/R3 | 两组 locale 键对称、README pair 出口/使用合同一致且相对链接有效；任务元数据与 CU 索引真实，不预写后续角色证据或验收结论 |

Development 在 tasks 记录实际命令、退出码、环境、构建/一次启动/一次消费观察及限制；验证产物优先放 `/private/tmp`，关键事实记录在 bundle，不能只留下临时路径。只关闭本任务创建的进程，不停止用户或其他任务的进程。

fresh-context Verification 独立审阅精确 r1、Development handoff、当前实现/diff 与证据；仅对有疑点或缺失证据复跑对应检查，不因角色分离重复完整构建/启动矩阵。原生路径无法启动时如实记录阻塞，不自动改写验收条件。

本任务验收止于上述必要构建、启动、引用与两个按钮的聚焦观察；不做全量回归、其他 Agent/CA/TSS 功能验证、Rust 全套测试、额外原生打包、三平台/端口/截图矩阵、长时间 GUI 轮询或压力测试。QA 通过后仍交 Human Owner 最终验收。

## 5. 风险、恢复与排除项

- frontend-js 使用另一套 token 和应用 store；只参考两控件视觉/反馈，避免引入第二套主题、i18n 或全局样式。强调前景沿用 CU token，确保按钮文字/图标可辨识。
- CU-001 的已验收变更尚在当前工作树，不能把 HEAD 当作 CU-002 的完整起点。Development 在修改前保留拟改文件的必要恢复依据，记录本任务实际增量，不回退既有或并发工作；无需新增冻结副本、全量 hash 或提交。
- 如需回退，仅撤销 CU-002 实际改动并恢复原插槽按钮组合；先核对当前归属，不对整个 CU 执行 `git restore` 或覆盖恢复。回退策略不等于当前执行回退授权。
- 排除顶栏整体重做、侧栏/卡片/其他操作按钮调整、更多公共组件、拖拽低代码与设计保存、真实 Agent 接入、npm 发布、依赖升级、SQLite/PLC/数据库、工业 runtime、发布部署和 Git refs 操作。更多 UI 调整另立范围。
- 当前无待定的业务选择；组件内部最小组织由 Development 在本合同内确定，不扩展公共 API。范围、allowlist、验收或风险实质变化时回 PM 修订新 Revision 并重新批准。

## 6. Handoff 与修订记录

PM 使用 `aiis` 与 `project-governance` 定义范围；技术实现交 Development，需加载 `frontend-ui`（按需阅读 DESIGN / FRAMEWORK）、`i18n-workflow`、`desktop-tauri`（现有启动路径），新增源码头部说明按需使用 `code-document-indexer`。本任务不修改 Rust runtime，不为技术实现加载无关后端/PLC skills。说明与索引继续遵循 project-governance / aiis，外部索引保持禁写。

Human Owner 于 **2026-10-16（Asia/Shanghai）**明确批准 **CU-002 r1**，原话：

> 可以，批准 CU-002 r1，按这个范围开始实施。只调整 CU 的明暗和中英切换按钮，做成公共组件，顶栏整体布局和其他 Agent 不动。验证能构建、能启动、能引用就行，不用全量回归。

下一 gate：命名 Development 创建 tasks 并按已批准 r1 的 allowlist 实施，交接 fresh-context QA / Verification；Human Owner 最终验收仍在 QA 之后。本次仅记录批准事实，未变更 Revision、范围、allowlist 或验收标准，未实施或追加测试。三角色文档及主协调 diff/索引审计属于合同控制，不宣称平台 ACL、强制路由或完整团队激活。

| 日期 | Revision | 记录 |
| --- | --- | --- |
| 2026-10-15 | r1 | PM 根据 Human Owner 请求创建 draft spec；仅文档检查，未实施、构建、启动或运行消费验证；精确范围批准 pending |
| 2026-10-16 | r1 | Human Owner 明确批准 CU-002 r1；仅机械记录批准与 Development handoff，范围、allowlist、验收标准及原草案历史保留，未实施或追加测试 |

执行依据：[根 AGENTS](../../../../AGENTS.md)、[Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)。任务归属 [CU PLAN](../../PLAN.md)，背景为 [CU-001 spec](../CU-001-workbench-foundation/spec.md) 与其完整 bundle；总体依赖由 [AW PLAN](../../../PLAN.md) 管理。
