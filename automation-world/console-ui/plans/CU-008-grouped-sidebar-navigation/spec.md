Task ID: CU-008
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved exact CU-008 r1 on 2026-10-17; PM -> Development for CU-only implementation and bounded validation; new fresh-context Verification and Human Owner final acceptance remain pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 兼容平铺的公共二级侧栏导航、受控选择与独立源码消费示例
Owner: Console UI
Acceptance Chain Reference: aiis-ics-arch::CU-008 r1 scope approval -> Development -> new fresh-context QA / Verification -> Human Owner final acceptance
Related Task: aiis-ics-arch::CU-001; aiis-ics-arch::CU-007; aiis-ics-arch::DAA-001

# CU-008 r1：公共二级侧栏导航

## 1. 起草来源、效力与归属

2026-10-17（Asia/Shanghai），本 CU 会话收到 DAA 会话 `01a143e5-5616-76c0-9df7-13b487bc9c26` 转来的需求。主协调传递的 Human Owner 原话为：

> 要不你来补一下？但是 在这个会话发起吧，等到完成了，这边再继续。如何？codex://threads/01a1385a-3a1c-7580-b703-eb5ee675396d

这只作为**转入本 CU 会话起草独立任务**的授权来源，不是对当时尚不存在的 CU-008 r1 的精确范围批准。草案创建时状态为 `draft`；当轮 PM 只创建本文件，未实施、构建/启动/测试、预建 `tasks.md` / `checklist.md`、修改索引或其他工程，也未向 DAA 或其他聊天发送消息。

2026-10-17（Asia/Shanghai），Human Owner 在本 CU 会话精确批准 CU-008 r1，原话由主协调传递：

> 可以，批准 CU-008 r1，按 spec 开始实施。只改 CU，其他 Agent 不动，保留当前卡内边距18。验证 CU 和独立消费者能构建、平铺与分组导航、键盘焦点及窄窗明暗效果即可，不做全量回归。DAA 接入仍在 DAA 会话处理。

**当前为 r1 `owner_approved`。** 本次 PM 仅记录真实批准、交接和 gate 时间效力，保留原215行草案历史；第3–7节的 R01–R08、15个实现/说明路径、10项 AC、验证上限与风险原文不变。精确范围批准 gate 已满足，实际 Development 现在可在本 spec 的 CU-only allowlist 内创建 `tasks.md`、实施并完成限定自检；当前18及其他保护面保持。此批准不代表已实施、DEV handoff、QA 或最终验收，也不授权 DAA 接入、其他 Agent 或外部动作。PM 本次仍只写本文件，不实施、构建/启动/测试或创建后续角色文档。

需求来源为 [DAA-001 r1 spec](../../../data-acquisition-agent/plans/DAA-001-cu-layout-migration/spec.md) §3.2 D02/D04：CU 独立交付兼容平铺的分组/子项、稳定身份与选择事件、选中子项自动展开、宿主翻译/active 状态、无公共存储或业务副作用、键盘/窄窗/日夜可达性，并提供公共 API、消费示例和精确源版本证据。DAA 之后自行固定 alias/依赖并验证业务四页；其业务菜单名称不进入本公共示例。

唯一 owning bundle 是 `automation-world/console-ui/plans/CU-008-grouped-sidebar-navigation/`，由 CU PLAN 管理。CU-001–CU-007 的既有接受和 DAA-001 r1 的范围批准均不转移到本任务；本任务是 `Classification: root`，无 `Parent Task ID`，不继承其他任务的批准、实施、QA 或最终验收。DAA 等待本能力，不构成 CU 反向依赖 DAA 实施的循环 gate。

精确 `CU-008 r1` 的 Human Owner 范围批准已如上发生，当前交实际 Development 实施和创建 `tasks.md`；其 `developer_handoff` 之后启动新的 fresh-context Verification 创建 `checklist.md`，最后由 Human Owner 终验。角色 profile 为 `contract_only`，主协调、bundle 与 diff 审计仍为必要控制，不宣称平台 ACL、强制路由或完整 Agent Team 激活。

## 2. 已读依据与当前事实

PM 已读取根 AGENTS、README/PLAN 双语、[canonical lifecycle workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)、实际 `.codex/agents/pm.toml`、AW/CU 最近 README/PLAN 与 CU catalog、CU 源码层次与独立消费者教程、CU-001/CU-007 完整 bundle 和 DAA-001 已形成的完整 bundle（目前仅 spec）。未发现 AW/CU 更近的 AGENTS。采用 `aiis`（含 CONTRACTS）与 `project-governance`；技术实现及验证交第 9 节角色处理。

当前 HEAD 为 `f85bea8bbf36b491968c3dc9a839518a1ed434a8`，仓库已有其他会话的 dirty/untracked 改动。HEAD 仅是上下文，不能代替实际工作树，也不能把根总 diff 算成本任务增量。已核对 CU task metadata/catalog，现有 CU-001–CU-007 均有 `owner_accepted` 记录，CU-008 原不存在。

| 已读入口（相对 CU 根目录） | 当前事实及本版影响 |
| --- | --- |
| `src/ui/types.ts`、`src/ui/index.ts` | `NavigationItem` 只有 id/label/icon；唯一公共入口导出八组件和展示类型。采用向后兼容的可选 children 扩展，不增加公共组件。 |
| `src/ui/components/AgentSidebar.vue` | ElMenu/ElMenuItem 平铺；props 为 activeId/items/brand/detail，事件为 `select(id: string)`。保留全部既有调用合同。 |
| `src/ui/components/AgentLayout.vue` | `sidebarHidden` 通过 `v-if` 卸载/重建 sidebar 插槽。无需改 Layout；恢复时由 Sidebar 初始 active 处理展开。 |
| `src/ui/styles/components.css` | 侧栏与菜单共用既有 tokens；≤600px 时平铺菜单 flex-wrap。分组需要局部适配，不能让该规则压平/遮住子项。 |
| `src/workbench/Workbench.vue`、`workbench.css`、私有双语 locale | 四平铺主导航及既有参数/页面样例；可在壳层预览内组合独立导航样例，无需改已有页面内容或共享样式写入机制。 |
| `examples/source-consumer/src/App.vue`、其双语 locale | 只从公共入口导入，自有主题/语言/表格表单；当前一项固定 active 的平铺导航可扩展为自有内存导航演示。 |
| 当前安装的 Element Plus 菜单源码 | 2.14.2 的 menu keyboard helper 仅在 horizontal 模式初始化；现 CU 为 vertical，不能假设换用 ElSubMenu 就已有完整键盘能力。仅在 AgentSidebar 内补齐本版所需行为。 |
| `src/ui/styles/design-profile.json`、`design-profile.generated.css` | 当前公共 cardPaddingPx=18、tableDensity=standard；两文件、既有配色/间距和主题方案均为保护基线，不是本任务验证写入目标。 |

## 3. 范围与公共合同

### R01. 有限二级类型与兼容选择

本版公共类型采用下列非递归形态；通过现有 `src/ui/index.ts` 导出新增类型，原四种展示类型导出保持：

```ts
export interface NavigationChildItem {
  id: string
  label: string
  icon?: Component
}
export interface NavigationItem extends NavigationChildItem {
  children?: NavigationChildItem[]
}
```

`Component` 沿用现有 Vue 类型。`items: NavigationItem[]`、`activeId: string`、`brand: string`、`detail?: string` 和 `select(id: string)` 均保持；不增加 Router、路径导航、权限/业务模型、展开状态 props/events 或任意深度树。

- 无 children 或 `children: []` 的顶层项按既有平铺叶项渲染，激活后只发该叶项 id；空数组不变成不能选择的空分组。
- children 非空的顶层项为可折叠分组，其直接子项均为可选择叶项；分组标题只展开/折叠，**不发 select、不充当页面、不改变 activeId**。顶层叶项与分组可混用，子项可带可选 icon。
- 宿主提供全树非空且唯一的稳定 id，包含分组与所有叶项；切换语言不改 id，label 已由宿主翻译。宿主只把可选择叶项 id 作为 activeId。空 items 正常显示品牌区；未匹配/误传分组 activeId 时没有选中叶项、不自动选默认项，也不发合成 select。
- 重复 id、任意嵌套 children 等不属于有效输入合同；本版用有限类型、文档与正常示例约束，不建设树校验器、修复/去重平台或异常输入矩阵。

### R02. active、展开与状态寿命

activeId 是宿主的当前项真相。用户选择有效叶项时每次激活只发一次 `select(id)`，宿主决定更新 activeId 及右侧内容；组展开、初始化和外部 prop 变化不发选择事件。选中高亮最终与宿主 activeId 一致，不把菜单内部短暂交互状态当业务页面状态。

首次挂载 activeId 指向子项、外部 activeId 变为某个子项、或同一 active 子项因 items **结构**变化改属新组时，自动展开对应父组。更新后的 active 叶项和父组状态一致；换到顶层叶项不强制关闭其他组。label/语言/主题变化不重置 active 或手动展开状态，不因 computed items 重建而每次重开全部组，也不抢焦点。

用户可手动展开/折叠任意组，包括当前 active 子项的父组；折叠不取消其叶项选择，父标题仍体现“内有当前项”，而非成为第二个选中页面。之后 activeId 变更/结构归属变更或重新挂载时，按上述规则展开所需父组。多组可同时展开，不新增手风琴规则。手动展开状态仅存在当前 Sidebar 实例内存，不读写 storage、URL、文件或业务状态。

既有 `AgentLayout` 隐藏侧栏会卸载实例，恢复时保留宿主 activeId 并重新展开其父组；无需承诺恢复其他手动展开组，也不修改 Layout。隐藏/恢复、语言/主题/导航选择均不得触发业务请求、IPC、配置写入或公共偏好读写。

### R03. 键盘、语义与焦点

沿用 ElMenu/ElSubMenu/ElMenuItem 的菜单、展开及选择语义与现有依赖。当前 vertical 模式缺少的必要键盘行为只在 AgentSidebar 内补齐；不能导入 Element Plus 私有实现、创建独立焦点框架或把菜单改造成通用树。

Tab/Shift+Tab 可进入和离开导航，能到达可见顶层项、组标题及已展开子项，不困住焦点；折叠子项不可获得焦点。上下方向键可在可见菜单项间移动；右方向键在组上展开并可进入子项，左方向键从子项回到父组、在组上可折叠。Enter/Space 在组上切换展开、在叶项上选择；同一按键不能同时经 keydown 和合成 click 产生两次切换/选择。无需额外实现所有桌面快捷键或任意树焦点策略。

父组有清楚的展开指示和 aria-expanded，active 叶项与“包含 active 叶项”的父组可区分，焦点样式独立于 active/hover 且日夜可见。折叠当前含焦点的子树时把焦点回到父标题；外部 active/翻译/主题变化不强制移动焦点。隐藏/恢复由宿主现有可聚焦顶栏开关操作，恢复不自动把焦点从开关抢走；菜单仍可经键盘再次进入。

### R04. 仅侧栏必要样式

复用 `.aw-ui` 与现有 `--agent-*` / Element Plus 变量，补足分组标题、子项层次、active 父组、焦点及菜单内部滚动/换行。只改侧栏/菜单相关规则，保持平铺菜单原视觉和其他公共组件外观；不能借机改配色、全局间距、卡片密度、壳层布局或公共主题方案。

≤600px 可对**含分组的菜单**增加局部类和覆盖，使组与子项保持内联展开的层次及可达性；原平铺 flex-wrap 行为继续可用，不把菜单转为脱离主题作用域的 popup。代表性窄窗中长中英文 label、展开子项和末项都可通过换行或侧栏局部滚动到达，不能被高度/overflow 裁掉、需要悬停才出现或挡住焦点。无需改 AgentLayout 或新增移动端导航系统。

### R05. CU 与独立消费者的有限展示

CU 保留既有四平铺主导航和已接受页面；在壳层预览内新增一个小型二级导航设计样例，使用同一公共 AgentSidebar、宿主内存 activeId/select 和一个外部切换当前项的有限控件。分组示例至少包含一个顶层叶项与一组两个子项；原主导航证明旧平铺路径仍可使用。布局 CSS 仅承载该样例，不重排整体工作台或主题编辑器。

独立 source-consumer 继续只从 `@aw-ui` / `@aw-ui-styles` 消费公共源码；在自身侧栏增加小型平铺/分组模式选择及受控 active 示例，模式/选择均仅内存。保留现有表格/表单/弹窗内容及状态；切换样例不能为了演示销毁它们或替换整个应用布局。两边能观察选择、外部 active 更新和父组展开，样例使用通用面板/样例名称，清楚标识 Design sample，不复制 DAA 业务菜单或 CU 私有实现。

新增标签、模式/当前项说明及可访问名称进入各自对称 zh-CN/en-US locale，公共 UI 不导入 CU 或消费者 i18n 实例。原 CU theme/locale 持久化与现有设计方案机制保持；本任务不新增导航/展开偏好，消费者继续不持久化。

### R06. 文档与可消费交接

CU README pair 与 source-consumer README pair 描述完整公共类型、平铺/分组代码示例、空 children、组/叶选择区别、active/展开/焦点寿命、宿主翻译/状态与独立编译边界。示例实际经公共导出编译，入口、CSS 顺序、alias/dedupe 和现有依赖版本不变；不引入 npm 发布或在线 CU 服务。

Development handoff 在 tasks 记录最终公共 API 示例、实际公共源码/样式及其传递依赖的完整路径清单与逐文件 SHA-256；包含公共入口、types、八组件、公共样式入口及实际导入的 CSS，并单列受保护 JSON/CSS。记录 HEAD 作为上下文；只有 Git ref 确实固定相同内容时才可作为消费版本，否则用实际工作树清单，不编造版本/tag/hash。新 Verification 对实际清单和被验证文件核对，在 checklist 记录独立 verdict；Human Owner 终验后形成可供 DAA D02/D04 消费的精确 CU-008 Revision、批准/DEV/QA/终验依据和源清单。

本草案不预填交付 hash/ref 或接受结果。DAA 仍自行固定 alias、依赖解析和实际消费清单，并完成其自身 QA；CU QA 不替代 DAA QA，CU 完成也不自动修改 DAA 或解除其余 gate。后续源有变化须明确新差异，不能把旧 hash 当当前消费证明。

### R07. 基线与受保护面

Development 写前重新读取完整已形成 bundle，记录现有 dirty/untracked、拟改文件起点和受保护文件摘要，保留其他会话工作；只提交本任务实际增量，不恢复 HEAD 或旧验证默认。公共 `design-profile.json` 与 `design-profile.generated.css` 必须保持**本任务写前原字节**，当前 cardPaddingPx=18、tableDensity=standard，不执行 apply/import/generate 或修改方案来验证导航。

AgentLayout、其余七公共组件、公共主题/纯映射、设计方案编辑器/私有应用通道、端口/锁文件/依赖及 Rust/Tauri 均受保护。范围内失败只作相应修复；如必须改这些表面、新增文件或扩大 API/验收/风险，先回 PM 新 Revision 和 Human Owner 批准。

### R08. 有限验证与真实证据

批准后只做第 6 节限定验证。DEV 自检不是独立 QA；任务三文件记录真实命令、环境、退出码、观察、失败/返工、精确增量与资源归属。缺少必需浏览器交互证据不能记通过；不为方便新增测试框架、路由库、运行时依赖或长期 mock。浏览器 dev 足以验证本公共 Vue 能力，不以独立原生打包、重复 Tauri 启动或现场链路作为前置。

## 4. 精确 allowlist 与角色分工

下表路径相对 `automation-world/console-ui/`，全部是既有文件的最小修改；精确 r1 范围批准后才由 Development 实施。不为用满 allowlist 而修改文件，不新增产品源码文件或整目录授权。

| 精确路径 | 唯一允许内容 |
| --- | --- |
| `src/ui/types.ts` | R01 非递归导航类型扩展，保持旧类型。 |
| `src/ui/index.ts` | 导出新增 NavigationChildItem，保留八组件及既有类型出口。 |
| `src/ui/components/AgentSidebar.vue` | 二级渲染、受控 active/展开及必要键盘焦点补齐。 |
| `src/ui/styles/components.css` | 仅 R04 侧栏/菜单样式及相应窄窗规则。 |
| `src/workbench/Workbench.vue` | 壳层预览内有限导航样例/内存状态，原四平铺主导航和既有内容保持。 |
| `src/workbench/workbench.css` | 仅导航样例局部布局，保留既有参数页及150px密度下拉修复。 |
| `src/locales/zh-CN/workbench.json` | 导航样例与可访问说明。 |
| `src/locales/en-US/workbench.json` | 对称英文键、占位符和文案。 |
| `examples/source-consumer/src/App.vue` | 消费端有限平铺/分组/受控选择演示及其局部样式。 |
| `examples/source-consumer/src/locales/zh-CN.json` | 消费端导航示例文案。 |
| `examples/source-consumer/src/locales/en-US.json` | 对称英文键、占位符和文案。 |
| `README.md` | 公共导航合同、兼容与宿主责任说明。 |
| `README.zh-CN.md` | 对称中文说明。 |
| `examples/source-consumer/README.md` | 可编译消费示例与源版本/状态寿命说明。 |
| `examples/source-consumer/README.zh-CN.md` | 对称中文教程。 |

| 阶段/归属 | 精确路径 | 允许内容 |
| --- | --- | --- |
| PM / Human Owner | `plans/CU-008-grouped-sidebar-navigation/spec.md` | 本规格、真实批准与 Revision 历史；当前唯一 PM 写入。 |
| Development，批准后新增 | `plans/CU-008-grouped-sidebar-navigation/tasks.md` | 实施/自检、实际源清单与精确 handoff。 |
| 新 fresh-context Verification，developer_handoff 后新增 | `plans/CU-008-grouped-sidebar-navigation/checklist.md` | 独立验证/verdict 及真实 Human Owner 最终验收。 |
| 主协调 | `PLAN.md` | 仅 CU-008 行的真实状态、spec 链接与下一 gate。 |
| 主协调 | `PLAN.zh-CN.md` | 对应中文行。 |
| 主协调 | `plans/README.md` | 仅 CU-008 catalog 行，存在后才链接对应角色文件。 |
| 主协调 | `plans/README.zh-CN.md` | 对应中文行。 |

根/AW 的 AGENTS/README/PLAN/catalog/CODE_INDEX、DAA/SMA/CA、backend/frontend-js/tools、历史 bundle 及其他未列文件均不写。本版不改 `src/app/README.*`：源码层次不变，无新产品文件，沿用 CU-007 的本地 README 登记方式，不新建或扩写结构索引。package/lock/workspace/Vite/tsconfig、全部 src-tauri/原生产物源配置/端口、公共主题 JSON/生成 CSS/纯校验映射、CLI/私有应用通道、其余公共组件和既有页面/参数编辑器不可改。真实配置、用户偏好、数据、Git refs/推送/发布/部署/数据库/PLC 与外部消息发送不在范围。

## 5. 验收标准

| ID | 可复核结果 | 需求 |
| --- | --- | --- |
| AC01 | 新类型只二级且由唯一公共入口导出；旧平铺调用不新增必填参数，八公共组件及原 props/select 兼容。顶层叶/非空组/子项正常，空 children 按叶项，稳定唯一 id 与无递归约束有文档。 | R01 |
| AC02 | 组标题不发 select；一次叶项点击/键盘激活只发一次正确 id。宿主回写 active 后叶/父高亮一致；初始化、外部 active/结构更新不发合成 select，未匹配 active 无伪默认选择。 | R01–R02 |
| AC03 | 初始子项、外部 active 改到子项、active 改属组及 sidebarHidden 恢复均展开正确父组；手动折叠/重开不改选择；label/语言/主题更新不清展开状态、不抢焦点，无导航/展开存储。 | R02 |
| AC04 | 代表性 Tab 进出、方向键到组/展开进入子项、Enter/Space 选择、折叠后焦点返回可用；无隐藏子项焦点或重复激活。父组展开语义与叶项 active、focus 可区分。 | R03 |
| AC05 | 两个宿主在代表性桌面与≤600px窄窗均可到达展开子项和末项；中英文/长标签、日夜 active/父组/焦点可辨，未改平铺外观、整体壳层或公共主题方案。 | R04–R05 |
| AC06 | CU 自身四平铺主导航仍可使用，独立二级样例与 source-consumer 的平铺/分组/外部 active 使用同一公共组件；消费者无 CU 私有导入/运行服务前置，无新业务或持久化副作用。 | R05 |
| AC07 | CU 与 source-consumer 各一次最终 `pnpm build` 成功；含现有类型/Vite 检查，CU 原只读 design-profile 一致性检查保持。真实浏览器完成限定导航交互，证据与未运行部分如实区分。 | R08 |
| AC08 | 两层 README pair 对称且本地链接有效，API 示例可由实际示例编译；两套 locale 键/占位符对称；handoff 含实际公共源/样式清单与逐文件 SHA、批准/DEV/QA/Owner 证据归属清楚。 | R05–R06 |
| AC09 | 实际增量逐路径在 allowlist；未跟踪新增全文纳入，其他会话改动保留，保护摘要/并发归因可审；两公共方案文件原字节及18/standard保护通过。 | R07 |
| AC10 | 精确 r1 批准后实际 Development 才实施/创建 tasks；其 developer_handoff 后新的 fresh-context Verification 形成独立 verdict；qa_passed 只进入 Owner 终验，不提前宣称 DAA 接入或 D02/D04 完成。 | R06–R08 |

## 6. 验证上限与方法

Development 在实现冻结后分别于 CU 根目录和 `examples/source-consumer/` 各执行一次最终 `pnpm build`，记录命令/cwd/退出码/真实日志；不要求为本纯导航任务先跑修改前 build。工具链与锁文件沿用现有 pnpm；必要时仅按现有 `pnpm install --frozen-lockfile` 恢复声明依赖，不升级锁或把 Agent 辅助包装进项目。失败、返工或新疑点才重复对应检查。

用现有本地浏览器 dev/preview 和两个示例完成一次聚焦观察：旧平铺选择；混合组展开/折叠与两个子项选择；初始子项/外部 active 变化自动展开；label/locale/主题变化保状态；隐藏恢复；一条代表性键盘路径与一条窄窗路径。桌面可取1280×800、窄窗可取390×720；二者是验证视口，不是新设计常量。用少量日夜/中英观察覆盖这些能力，不展开全部组合矩阵；空 children、空 items、结构变更/无匹配 active 可用同一临时组件夹具定向核对，无需新增产品控件或测试框架。

默认 CU dev/preview 15193/14193，消费者15194/14194；先检查既有监听归属，不停止用户或其他任务进程。必要隔离仅用命令行覆盖临时端口并记录 origin，不改配置。使用独立验证浏览器状态，保留用户原偏好；不点击设计方案应用/导入/生成。浏览器 dev 对本公共 Vue 能力足够，不新增 Tauri/Cargo/native 打包/启动要求，也不把浏览器交互宣称为原生 WebView 证据。

fresh-context Verification 独立读取精确 approved spec、完整 tasks、当前实现及精确增量/新增全文、日志和源清单，亲自复查代表性导航/焦点/窄窗交互并核对保护面；可审阅两个最终 build 的实际输出，只有缺失/疑点才复跑。QA 不修实现，不以 DEV 截图或单纯文本匹配替代必要交互。必要证据不可得则具体记录 qa_blocked，不自行降低 AC 或记通过。

文档/locale/链接及 whitespace、保护摘要检查保持定向；临时验证 helper、日志/截图优先 `/private/tmp`，记录关键结果到 tasks/checklist，不以临时路径作唯一证据。记录本任务服务 PID/端口、产物和保留原因，只停止本任务创建的服务；资源清理由主协调在终验后核对归属处理。排除旧页面表格/表单全量回归、主题编辑/共享写入再验证、后台/PLC/数据库/Rust/跨平台/长稳和发布部署测试。

## 7. 风险、回退与延期

| 风险 | 本版约束与停止条件 |
| --- | --- |
| ElMenu 内部选择/展开与受控 prop 不一致，键盘事件重复 | 复用菜单机制，只在 Sidebar 内做必要同步/补齐；代表性外部 active 与一次按键事件核对，不能引入第二份业务导航真相。 |
| ≤600px flex-wrap 使分组挤压、长英文或末项不可达 | 对含组菜单局部适配，平铺保持，实看窄窗/焦点；不能靠全局壳重构解决。 |
| 示例改动破坏已接受参数/页面或用户公共方案 | 独立局部演示、最小样式；两个方案文件原字节保护，不通过编辑样式验证导航。 |
| 未提交源漂移导致 DAA 固定错误版本 | DEV/QA 对同一实际文件清单和摘要，Owner 接受后才交依赖使用；差异变化先明确再消费，不伪造 ref 或继承旧 QA。 |
| 并发 dirty/环境问题被误算成本任务 | 保留起点及精确增量、逐路径归因；范围外失败或需额外路径时返回 PM，不顺手修依赖/其他工程。 |

回退只反向应用本任务已确认增量，核对当前归属并保留并发修改；不 reset/restore 整工作树、不恢复旧公共方案、不清用户 storage 或未知临时资源。实际破坏性回退仍按具体授权处理。任意深度树、路由/权限集成、拖拽菜单、可持久化展开偏好、公共主题重做、DAA/SMA 接入、原生生命周期/分发及现场动作延期另项，不阻塞本版限定导航交付。

## 8. gate 与角色交接

执行依据为根 AGENTS §4 与 canonical workflow：`spec.md -> Human Owner 批准精确 Task ID / Revision -> tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance`。`project-governance` 明确“Development creates tasks.md only after exact Human Owner Revision approval”；本版现已取得第1节的独立精确批准，不能以此前转述需求、DAA 批准或旧 CU 接受替代该事实。

主协调已提交本 r1 及15个实现/说明路径、10项 AC 与风险，Human Owner 于2026-10-17作出第1节精确批准。精确批准前仅 PM 草案和主协调机械索引的限制属于该时点历史；现在交实际 Development 完成限定实施/自检及精确 handoff，再由主协调显式启动 `agent_type="verification", fork_turns="none"` 的新 fresh context；失败回实际 Development，实质范围变化回 PM 新 Revision。QA pass 后由 Human Owner 最终验收，接受事实与清单可供 DAA 所属任务引用；本任务不发送跨会话消息或代写 DAA 记录。

## 9. 技术 skill 与修订历史

| 后续表面 | 交对应角色的 skill / 边界 |
| --- | --- |
| Vue 类型、菜单、局部样式/示例与定向交互验证 | Development / Verification 使用 `frontend-ui`，按现有 Element Plus 设计与框架适用部分执行；不另选设计系统。 |
| 两宿主新增文案/可访问名称 | `i18n-workflow`；各宿主对称资源，公共层只接已翻译字符串。 |
| bundle/机械索引、公共与消费边界 | `project-governance` + `aiis`；三角色各守文档权威。 |
| 实际 browser 自动化 | 使用当时可用工具及其规则；若用 terminal Playwright 再加载相应 skill，不安装新项目测试依赖。 |

本任务不触达桌面壳/Rust、后端/API、点位或新产品源码结构；不加载这些范围的实现 skill，也不自动扩写 CODE_INDEX。PM 不代做 Development/Verification 技术工作。

- 2026-10-17，r1 draft：实际 PM 依据已读治理、当前公共/私有源码与 DAA D02/D04 起草本文件；仅有起草授权，尚无精确 CU-008 r1 范围批准。未实施、构建/启动/测试、创建 tasks/checklist 或改索引。
- 2026-10-17，r1 owner_approved：Human Owner 按第1节原话精确批准 CU-008 r1；PM 仅补记状态、真实批准和 Development 交接及时间效力，R01–R08、15路径、AC01–AC10、验证上限与风险保持原草案不变，原 draft 历史保留。实际 Development 可开始批准范围内的实施；本次未写实现/tasks/checklist/索引或运行测试。
- Development、独立新 fresh-context Verification、Human Owner 最终验收及对 DAA 的可消费交接：pending。
