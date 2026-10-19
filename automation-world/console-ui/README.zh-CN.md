# AIIS AW Console UI

[English](README.md)

Console UI（CU）是轻量 Tauri 设计工作台与可复用 Vue / TypeScript / CSS 源码表面。它预览既有 Element Plus 壳层、卡片、动作、状态胶囊与参数。所有数据均标识为**设计样例**，不代表在线 Agent 事实。

## 源码边界

- `src/ui/index.ts`：唯一公共代码入口，导出 `AgentLayout`、`AgentSidebar`、`AgentTopbar`、`ConsoleCard`、`ConsoleActionButton`、`StatusCapsule`、`ThemeToggle`、`LanguageSwitch` 与展示类型。
- `src/ui/styles/index.css`：唯一公共样式入口，提供日夜主题 tokens 和组件样式。沿用既有 `--agent-*` 命名与视觉值，以 `.aw-ui` 限定默认作用域，`[data-aw-theme="dark"]` 选择暗色。
- `src/workbench/`：私有设计样例与组合；工作台和消费端使用同一公共组件。
- `src/workbench/useSharedDesignProfile.ts`：私有本机开发客户端；跨源码 HMR 在内存保留提交快照、结果与参数页状态，不新增 storage key。
- `scripts/shared-design-profile.js`：CLI 与开发插件共用的固定公共 JSON/CSS I/O 与内容版本，导入时无读写。`scripts/shared-design-profile-dev.js` 仅注册本机 Vite 开发通道；相邻 `.d.ts` 只声明插件工厂。
- `src/locales/`：CU 私有双语资源与 i18n 实例；组件通过 props/slots 接收翻译结果，公共 UI 不依赖 i18n。
- `src-tauri/`：只负责窗口启动，无业务命令处理器或工业配置读取器。
- [source-consumer](examples/source-consumer/README.zh-CN.md)：独立最小 Vue/Vite 应用与源码消费教程，由 [CU PLAN](PLAN.zh-CN.md) 管理。

CU 来源于 CA 源码副本，本次已移除可执行 PLC/数据库/headless 逻辑、样例 YAML/env、驱动 features、工业脚本及专属依赖。[CA](../control-agent/README.zh-CN.md)、DAA、SMA 均为独立工程，CU 不改变它们的实现或职责。CU 不读取工业配置、不采集数据、不保存业务配置；`cu.theme` 和 `cu.locale` 持久化 UI 偏好，下述独立版本化草稿仅保存样式值；不迁移旧 Agent 键。

## 运行与构建

使用 pnpm / Cargo 并保留锁文件。当前验证版本：Node 22.19.0、pnpm 11.11.0、Vue 3.5.38、Element Plus 2.14.2、icons 2.3.2、vue-i18n 9.14.5、Vite 5.4.21、TypeScript 5.9.3、vue-tsc 2.2.12；本任务保留既有依赖代际。

```bash
pnpm install --frozen-lockfile
pnpm dev                          # strict 15193
pnpm build                        # 类型检查 + 自身 dist
pnpm preview                      # strict 14193
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo check --manifest-path src-tauri/Cargo.toml --locked
pnpm tauri dev                    # 配合 Vite 启动桌面
pnpm tauri build --no-bundle       # 当前平台原生可执行文件
```

原生前置依赖见 [Tauri](https://tauri.app/start/prerequisites/)。产品/窗口名 `AIIS AW Console UI`，package/bin 为 `aiis-aw-console-ui`，lib 为 `aiis_aw_console_ui_lib`，identifier 为 `com.aiis.aw.consoleui`。Tauri 通过 `../dist` 嵌入 CU 自身产物；不代表签名、分发或部署。依赖、dist、target 和生成的原生产物保持未跟踪。

## 消费公共源码

完整步骤见[消费者教程](examples/source-consumer/README.zh-CN.md)。编译时需可访问 CU 公共源码，设置 `@aw-ui` 指向 `src/ui/index.ts`，`@aw-ui-styles` 指向 `src/ui/styles/index.css`。消费端自行安装兼容 Vue、Element Plus 和 icons，并通过 Vite `resolve.dedupe` 保持单实例。示例自行安装 i18n，再把翻译文案传给公共组件。

```ts
import { AgentLayout, ConsoleCard, StatusCapsule, type UiTheme } from '@aw-ui'
import 'element-plus/dist/index.css'
import '@aw-ui-styles'
```

消费端自行创建/挂载 Vue app，通过 `AgentLayout` 的 `theme` 属性显式提供 `light`/`dark`，提供本地化文案并管理状态和事件。公共导入不会挂载应用、读写偏好、调用 IPC、读取运行快照或 CU 私有文件。单独组合组件时可使用 `.aw-ui` 与 `data-aw-theme` 包裹，公共组件应处于该主题作用域内；body reset 和页面布局由消费端负责。

`ThemeToggle` 接收 `theme: UiTheme` 和翻译后的目标动作 `label`；`LanguageSwitch` 接收 `locale: 'zh-CN' | 'en-US'`、翻译后的 `zhLabel` / `enLabel`（通常为“中” / “EN”）及目标动作 `label`。二者均仅发出 `toggle`，不修改状态或写入 storage。label 同时提供原生 tooltip 与可访问名称，主题按钮还表达当前暗色状态。通过 `@aw-ui` 导入并放在公共样式作用域内，由宿主处理事件和更新 props。CU 保留既有 UI 偏好，消费者拥有独立状态且不持久化；消费者构建产物无需 CU 在线。

源码编译完成后，消费端只运行**自身** `dist`，无需 CU 进程、源码 checkout 或 CU node_modules。首版仅提供源码出口，不建立 npm 发布、根 workspace、在线 CU 服务，也未实际接入其他 Agent。层次说明见 [src/app](src/app/README.zh-CN.md)，批准范围见 [spec](plans/CU-001-workbench-foundation/spec.md)。

## 平铺与分组导航

`AgentSidebar` 保留 `activeId: string`、`items: NavigationItem[]`、`brand: string`、可选 `detail` 及 `select(id: string)`。公共入口导出以下有限非递归类型（可选 icon 使用 Vue 的 `Component` 类型）：

```ts
interface NavigationChildItem { id: string; label: string; icon?: Component }
interface NavigationItem extends NavigationChildItem { children?: NavigationChildItem[] }
```

无 children 或 `children: []` 的顶层项为可选叶项；非空组只展开/折叠，直接子项为可选叶项。宿主为组和叶项提供全树非空、唯一、稳定的 id；翻译只改 label，不改 id。嵌套组和重复 id 不属于有效合同。空 items 保留品牌区；未知或误传组 activeId 不选中任何叶项，不发默认选择事件。

宿主翻译文案、拥有 active 状态并处理每次激活的一次 select，可从外部更新 active 或拒绝选择；最终叶项高亮与 aria-current 跟随 prop。初始子项、外部 active 改到子项及 active 子项改属新组会展开其父组，不合成选择、不移动焦点。含当前项的父组用标题强调色区分于当前叶项背景；手动折叠它仍保留选择。允许多组同时展开。文案/主题变化保留展开状态；手动展开只存在 Sidebar 实例内存。AgentLayout 隐藏会卸载 Sidebar，恢复时保留宿主 active 并重新展开其父组，不恢复其他手动展开组，也不从开关抢焦点。公共层不提供导航存储、路由、权限模型或业务/IPC 副作用。

Tab/Shift+Tab 可遍历可见叶项与组标题并离开菜单；上下键在可见项间移动，右键展开组并进入首子项，左键从子项回父组或折叠当前组。Enter/Space 单次激活叶项或切换组。折叠包含焦点的子树时焦点回父标题；已折叠子项不进入 Tab，外部 prop 变化不移动焦点。组 aria-expanded、叶项 aria-current、父组标题强调色及焦点轮廓均在当前明暗主题作用域内。窄窗分组内联展开并局部滚动，平铺菜单保留换行。

工作台保留四个平铺主导航，在壳层预览增加受控分组“设计样例”。独立消费者可在相同稳定 id 的平铺/分组模式间切换，提供宿主外部 active 按钮与事件计数，表格/表单/弹窗状态保持挂载。其 [App.vue](examples/source-consumer/src/App.vue) 通过公共导出实际编译；导航无需 CU 服务在线。固定未提交源码时应引用精确 CU-008 Revision 与 [Development handoff](plans/CU-008-grouped-sidebar-navigation/tasks.md) 的完整路径/SHA-256 清单，以及之后真实形成的独立 Verification/Owner 依据；HEAD 本身不能代表这些工作树字节。DAA 接入及其验收继续归 DAA 自身任务。

## Element Plus 页面组合

CU 私有的**页面样例**演示表格、校验表单、编辑弹窗及手动选择的正常/加载/空数据/失败状态。数据与重试/提交/编辑反馈只在内存中，刷新会重置样例。八个公共组件及 API 保持不变。独立消费者直接用自身 Element Plus 依赖组合更小的表格/表单/弹窗，拥有自己的 locale 与状态，不导入 PageSamples 或工作台文件。

先导入 Element Plus CSS，再导入 `@aw-ui-styles`。`ElTable` 使用 `aw-data-table`，`ElForm` 使用 `aw-sample-form`，动作区使用 `aw-form-actions`，状态内容使用 `aw-page-state`。公共 CSS 将 Element Plus 变量映射到当前作用域的 `--agent-*` tokens；页面布局由各宿主负责。这些类是样式约定，不是新增公共 Vue 组件。

脱离布局的弹窗需要显式主题作用域。本例用 Vue `Teleport to="body"` 包裹 `<div class="aw-ui aw-sample-overlays" :data-aw-theme="theme">`，其内嵌套 `:append-to-body="false"` 的 `ElDialog`。每个 `ElSelect`（包括弹窗内）使用 `:teleported="false"`，使下拉继承该作用域。主题容器持续绑定宿主主题，并通过 `ElConfigProvider` 提供宿主 Element Plus 语言；不设置全局 html/body 主题变量。标签、校验、反馈及所有状态切换归宿主负责。页面样例业务数据仅在内存中；下述独立参数编辑器管理样式草稿。

## 样式方案：预览、草稿与共享源码

CU 参数页编辑有限的 schemaVersion 1 方案：明暗 palette 各有 background、surface、surfaceMuted、text、textMuted、border、accent、accentStrong、onAccent（仅 `#RRGGBB`，规范化为小写）。共享整数为 cardPaddingPx 12–32（默认24）、actionGapPx 4–24（12）、cardRadiusPx 8–28（20）、controlRadiusPx 4–20（14），单位均为px；tableDensity 为 standard（默认，单元格垂直padding为8px）或 compact（4px）。compact卡片内边距/圆角及small控件圆角由其派生。默认配色值仅归公共JSON；状态色、装饰玻璃/阴影、布局与44px顶栏控件保持固定。

参数页左侧为有限编辑器，右侧为实时设计样例。桌面滚动时预览保持可见，窄窗时上下排列。仅展开当前日间/夜间配色；显式模式选择与顶栏共用宿主主题及 `cu.theme` 偏好，两套配色分别保留。每项颜色包含色块、Element Plus 拾色器和六位 HEX 输入；合法修改无需保存、导出或重启即可生效。工作台、实时样例、拾色弹层及样例弹窗共用最近有效方案与当前主题。表面色作用于 Element Plus 控件、表格基础表面和弹层；卡片装饰背景、玻璃与阴影仍固定。原标题/色调/compact 控件保留于编辑器下方次级区域。编辑颜色不会自动切换主题或语言。无效字段保留上一次有效预览，在字段旁和常驻预览状态显示对应模式/字段并禁用保存/导出，修正后立即恢复。首次打开始终使用编译时公共默认。保存/恢复/重置均显式执行，只触达 `cu.design-profile.draft.v1`；主题/语言键和业务样例分离。草稿仅属于当前CU浏览器/WebView/origin，消费者及其他Agent不读取。缺失/损坏草稿回到公共默认并反馈，存储失败如实提示。重置恢复公共默认并仅删除本草稿。JSON导出为可复制文本，不是原生文件写入或源码更新。

[design-profile.json](src/ui/styles/design-profile.json) 是唯一可编辑的公共默认源；[design-profile.generated.css](src/ui/styles/design-profile.generated.css) 是确定性生成结果，不可手改。纯JS校验/映射由预览和CLI复用，固定主题tokens保留在theme.css。公共样式按固定主题→生成方案→组件顺序加载，消费者继续用同一公共样式入口和组件API。

在CU目录执行：

```bash
pnpm design:profile                         # 仅帮助，无读写
pnpm design:profile --help                  # 同上
# 先将导出JSON复制到明确的本地文件：
pnpm design:profile --import /absolute/path/profile.json
pnpm design:profile --generate              # 从公共JSON重新生成固定CSS
pnpm design:profile --check                 # 只读一致性检查
pnpm build                                 # 先check，不隐式生成
```

所有字段必填；未知字段、路径、任意CSS/脚本、非法类型/颜色/范围/版本在目标写入前拒绝。导入只通过单文件安全替换更新固定CU公共JSON/CSS，不承诺两文件事务。CSS缺失/stale时执行 `--generate` 再 `--check`；公共JSON损坏时先从有效备份恢复，再生成。I/O失败返回非零，应检查两个目标、必要时恢复有效JSON，再generate/check；导入前自行备份有效公共方案。

共享流程为导出→显式工程导入→generate/check→宿主开发刷新或重构建。既有消费者源码不变，通过正常公共样式入口消费生成CSS，自身dist不需要CU在线且不读CU草稿。DAA/SMA本任务未接入；后续宿主自行同步与构建，已安装桌面二进制须重构建及分发，不承诺实时传播或依赖在线CU。

本机源码开发模式（`pnpm dev` 或 `pnpm tauri dev`）下，预览合法编辑后点击**应用到公共样式**，显式将完整明暗配色与共享尺寸写入上述同一公共 JSON 并生成 CSS；CU 自己也消费这些公共源。无效编辑或通道不可用时禁用按钮；应用中保留提交快照并防止重复提交。成功反馈跨本次 HMR 保留且参数页保持打开；刷新/启动采用更新后的公共默认。应用不保存草稿，也不修改主题/语言偏好。preview 与打包版不注册源码写入端点，禁用应用并提示导出/CLI 路径。

私有 `/__cu/design-profile` 通道仅接受实际 loopback 连接及既有 15193 本地 Host；受保护 GET 建立进程会话与两文件内容版本，POST 须匹配本机 Origin、会话 token 与受限 JSON 请求。无跨域 CORS，不接受输出路径、任意 CSS/脚本或消费者目录。版本冲突拒绝写入：先导出当前编辑、刷新、核对公共默认后重试。应用时不要并行运行 CLI 或手工编辑公共目标；进程内串行与乐观版本检查不是跨进程锁。I/O/网络失败不代表已确认应用：检查两个目标，必要时恢复有效 JSON，再执行 `pnpm design:profile --generate` 和 `pnpm design:profile --check`，最后刷新。两次单文件安全替换不等于双文件事务。其他 Agent 仍消费原公共样式入口，自行同步源码、刷新开发态或重构建并分发已安装二进制。
