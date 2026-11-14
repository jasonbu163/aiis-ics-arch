Task ID: CU-009
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 于 2026-11-12 批准 CU-009 r1。主协调交 Development 按第 2–5 节实施和定向自检。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: Console UI 公共顶栏圆形语言切换和纯图标刷新，覆盖 DAA 与同用公共按钮的宿主
Owner: Console UI
Acceptance Chain Reference: CU-009 r1 / Human Owner 范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
Related Task: aiis-ics-arch::CU-002; aiis-ics-arch::DAA-010
Created: 2026-11-12 Asia/Shanghai

# CU-009 r1：公共顶栏圆形语言与刷新按钮

## 1. 目标与作用范围

Human Owner 在 DAA-010 r5 的 Mac 检查中提出顶栏调整，并要求同步到 `console-ui`。语言和刷新采用现有明暗切换的圆形尺寸。语言按钮只显示切换目标，中文界面显示 `EN`，英文界面显示 `中`。刷新按钮只呈现刷新图标，文字用于操作提示和辅助技术。

DAA 和 DS 顶栏各自通过 CU 的 `AgentTopbar` 动作插槽装配 `LanguageSwitch` 与带文案的 `ConsoleActionButton`，再由宿主接收刷新事件。SMA、CU 工作台和独立源码消费者也使用同一个 `LanguageSwitch`。公共顶栏承载布局及插槽，宿主负责语言偏好、明暗和刷新动作。CU-002 的验收提供原组件基线。本次修改涉及 DAA-010 r5 第 4 节以外的公共源码及 DAA 顶栏文件，使用一个 CU 所属 STD 任务交付。 [公共顶栏](../../src/ui/components/AgentTopbar.vue) · [DAA 顶栏](../../../data-acquisition-agent/src/components/shell/AgentTopbar.vue) · [DS 顶栏](../../../device-simulator/src/components/shell/AgentTopbar.vue) · [SMA 宿主](../../../semantic-mapping-agent/src/App.vue) · [CU-002 验收](../CU-002-topbar-utility-controls/checklist.md) · [DAA-010 r5](../../../data-acquisition-agent/plans/DAA-010-sample-facts-upload/spec.md)

## 2. 需求与应用接入

1. **语言切换**。修改公共 `LanguageSwitch` 的默认外观为与 `ThemeToggle` 等大的 44 × 44 CSS px 圆形按钮，居中呈现宿主提供的目标语言短标签。以现有 `locale`、`zhLabel`、`enLabel` 和 `label` 取值，去掉并列标签及分隔线。点击、Enter、Space 各发出一次现有 `toggle`，焦点在切换后可见，偏好保存继续由宿主负责。当前语种下的完整目标动作同时用作可访问名称和悬停提示，例如中文的「切换到英语」与英文的「Switch to Chinese」。
2. **刷新**。在公共 `ConsoleActionButton` 中增加显式启用的圆形纯图标模式，复用既有图标、点击、loading 和 disabled 行为，默认普通按钮继续使用原版式。顶栏刷新使用 44 × 44 CSS px 圆形，空闲时仅显示已有 Refresh 图标，忙时有加载及禁用反馈，同一圆形占位稳定。按钮保持原生语义，装饰图标隐藏于辅助技术。用宿主的「刷新」或 `Refresh` 作可访问名称和悬停提示，按钮内无这两段可见文案。鼠标、Enter 和 Space 各触发一次现有刷新事件，禁用态不触发。公共组件使用现有明暗主题 tokens。
3. **宿主**。DAA 与 DS 的已有顶栏刷新改为显式启用公共圆形纯图标模式，复用原翻译和各自的 `refreshBusy` / `refresh-runtime`。CU 工作台使用同一公共模式展示刷新控件，点击仅更新一项明确标为样例的本地事件反馈，双语键成对。SMA 与独立源码消费者通过公共 `LanguageSwitch` 自动得到语言外观，两者现有顶栏没有刷新，保留原动作集合。各宿主沿用已有状态标记、标题、侧栏切换、明暗控件和语言偏好。默认及窄窗布局能正常排列，现有最小窗口下标题和动作不重叠，按钮不收缩或裁切。

## 3. 精确实施范围

路径相对 `automation-world/`。

| 改动面 | 文件与限制 |
| --- | --- |
| CU 公共组件和样式 | `console-ui/src/ui/components/LanguageSwitch.vue`、`console-ui/src/ui/components/ConsoleActionButton.vue`、`console-ui/src/ui/styles/components.css`。仅对应控件、相关明暗/焦点/忙态样式及必要窄窗约束，沿用原公共出口。 |
| CU 工作台 | `console-ui/src/workbench/Workbench.vue`、`console-ui/src/locales/zh-CN/workbench.json`、`console-ui/src/locales/en-US/workbench.json`。仅样例接入及成对文案。 |
| 两处已有刷新接入 | `data-acquisition-agent/src/components/shell/AgentTopbar.vue`、`device-simulator/src/components/shell/AgentTopbar.vue`。仅刷新按钮组合和必要的顶栏局部布局。 |
| 公共消费说明 | `console-ui/README.md`、`console-ui/README.zh-CN.md`、`console-ui/examples/source-consumer/README.md`、`console-ui/examples/source-consumer/README.zh-CN.md`。仅语言目标显示及可选纯图标用法。 |
| 任务记录 | 本任务 `spec.md` 归 PM。批准后实际 Development 写 `tasks.md`，交接后 fresh-context Verification 写 `checklist.md`。CU `PLAN.*` 与 `plans/README.*` 由主协调按实况机械同步本条。 |

本次走源码和 UI 验证。应用业务页面、Rust/IPC 实现、数据、PLC/DS 行为、其他顶栏动作、默认设计方案、构建配置、依赖、发布及部署属于其他范围。Development 与 Verification 使用 `frontend-ui` 和 `i18n-workflow`，按既有 pnpm 锁定工具链工作。公共出口、组件目录和主题结构沿用现有文件。

## 4. 验收

| 编号 | 可复核结果 |
| --- | --- |
| AC01 外观与文案 | DAA、DS、CU 工作台各可见同尺寸的圆形主题、语言与刷新控件。中英文切换分别显示 `EN` 和 `中`，刷新正文无文字。SMA、独立消费者得到圆形目标语言按钮。普通 `ConsoleActionButton` 的可见文案及既有动作外观保留。 |
| AC02 操作与无障碍 | 在明暗两主题下检查焦点可见、图标与字符可辨、两语提示及可访问名称正确。鼠标与 Tab / Enter / Space 验证一次激活。DAA 与 DS 源码核对仍转发原刷新事件与 busy 状态，受控验证覆盖加载/禁用无重复触发。CU 工作台样例可观察一次事件反馈，语言切换仍走原宿主偏好。 |
| AC03 窗口与集成 | 检查 DAA 默认 1280 × 820 和现有最小 960 × 640，至少覆盖英文长文案与侧栏展开、收起。再检查一次 CU 窄窗布局。控件可见、可聚焦、不重叠，未引入顶栏横向溢出。核对 DAA、DS、SMA、CU 与独立消费者的实际共享源码入口及各自 `pnpm build`，记录真实命令与结果。 |
| AC04 范围与说明 | 双语键一致、公共消费说明与实现相符、局部链接有效、`git diff --check` 通过。核对 DAA-010 r5 的规格、运行目标与独立候选范围，区分本任务 UI 观察与 r5 原生 S7/HTTP 证据。 |

聚焦 UI 检查可使用本任务自有的无原生桥接前端预览或已构建静态输出。需检查宿主事件时使用受控状态，区分浏览器和实际桌面证据。各角色使用归属明确的临时配置、端口及产物。关键结果进任务记录，临时路径只作附件。验收范围为以上控件与源消费回归。

## 5. 并行与交接

`@aw-ui` 直连公共源码。共享树的文件变化可能触发运行中的 DAA 或 DS 热更新。先核对 DAA-010 r5 进程实际使用的源路径和证据采集窗口。若仍消费同一工作树，CU-009 在隔离源码副本实施及验证，等 r5 不再从该树取证后整合至交付树并核对实效和源码一致性。测试与清理仅使用本任务自有的副本、前端预览与临时产物。范围发生实质变化时返回 PM。 [Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)

本稿于 2026-11-12（Asia/Shanghai）形成。Human Owner 同日明确批准 CU-009 r1 按 STD 实施及定向验证第 2–5 节。以下为批准原文。由实际 Development 实施和自检，交 fresh-context Verification，再由 Human Owner 最终验收。

> 批准 CU-009 r1 按 STD 实施及定向验证第 2–5 节。Console UI 同步公共顶栏的圆形语言切换和纯图标刷新，DAA 与 DS 接入公共刷新样式，CU 工作台展示同一控件，SMA 及独立消费者跟随共享语言样式。DAA-010 r5 按原批准范围独立继续。
