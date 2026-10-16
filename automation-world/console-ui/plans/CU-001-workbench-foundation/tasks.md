Task ID: CU-001
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: CU-001 r1 implemented in current working tree at HEAD 1a5aa2d2fe7089b5671218865238cfaa240f9a30; fresh-context Verification to review approved spec, this DEV evidence and CU-only diff
Task Namespace: aiis-ics-arch
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-001 r1 Development handoff

## 基础与实施结果

已完整消费 owner_approved spec、根 AGENTS / README / PLAN、AW 与 CU 最近文档、development TOML、canonical workflow 及 frontend-ui / i18n-workflow / desktop-tauri / rust-runtime / code-document-indexer；稳定说明按 project-governance / aiis 边界维护。实际命名 Development 承担实现与自检；不写 spec/checklist，不给 QA verdict 或 Human Owner acceptance。

- R1 / AC1、AC2：package/Cargo/显式 bin 改为 `aiis-aw-console-ui`，lib `aiis_aw_console_ui_lib`，product/window `AIIS AW Console UI`，identifier `com.aiis.aw.consoleui`；dev/preview 15193/14193 strict。只保留 Tauri 窗口启动和三条必要 JSONL 启动日志。移除 PLC/DB/headless 模块、IPC 注册、自动 bin、驱动 feature、工业脚本、专属依赖与 CU 样例 env/YAML，真实 .env 未修改。
- R2 / AC3：`src/ui/index.ts` 和 `src/ui/styles/index.css` 是唯一公共代码/样式出口。六个展示组件通过 props/slots/events 接收文案和状态，仅依赖公共层、Vue、Element Plus、icons；不导入 App/main/workbench、私有 locale、Tauri/IPC、RuntimeSnapshot 或工业配置。公共层不启动应用、不读写偏好。保留既有玻璃顶栏、侧栏、卡片及主题视觉，tokens 使用 `.aw-ui` 作用域。
- R3 / AC4：App 只组合私有 Workbench；工作台从公共出口消费壳层/卡片/按钮/状态。提供壳层、组件/四种状态、参数（标题/色调/compact）预览；所有区域处于明确的 Design sample 标识下。固定演示状态只影响本地展示，无业务持久化或设备动作；仅 `cu.theme`、`cu.locale` 保存 UI 偏好。
- R4 / AC7、AC8：新增独立 `examples/source-consumer`，有自身 package/lock/dependencies/类型配置，只从两公共入口消费；Vite dedupe 与 TS paths 解析消费端自己的 Vue/Element Plus/icons，i18n 也由消费端创建。CU README、src/app README、consumer README 三组双语说明包含源码层次、版本、路径/别名、主题/语言安装与独立 dist 运行教程；无根 workspace、npm 发布或其他 Agent 接入。

## 起点、恢复与变更归属

起始及交接 HEAD：`1a5aa2d2fe7089b5671218865238cfaa240f9a30`。未创建提交、分支、worktree、PR 或推送。
实际读取时 CU 已受 Git 跟踪，初始 `git status --short` 只见 PM 的 CU spec 修改；不沿用草案的“未跟踪”假设。CU `src/` 对冻结 CA `src/` 的 `diff -qr`、Cargo.toml 的 `diff -q` 均退出 0，确认此两面来源无用户增量；未将相邻 CA 当可写面。
清理前建立 `/private/tmp/cu-001-r1/recovery/cu-before.tgz`（214 个归档条目），包含旧 src/src-tauri/config、应用配置和 README，排除 node_modules/target/dist/真实 .env/plans/gen。恢复只针对本任务实际修改；不要整体覆盖 PM spec 或主协调索引，不做全量 hash 清单。

`pnpm tauri build` 自动更新已跟踪的 `src-tauri/gen/schemas/capabilities.json` 中 capability description。初始该文件无改动；按 spec 不手改生成 schema，构建后仅用 `git show HEAD:<该路径>` 机械恢复本任务生成差异，最终该路径无 diff。未恢复整个目录或其他人修改。
PM 修改 `spec.md`，主协调修改 CU PLAN pair 与 plans README pair；这些不属于 Development 的实现改动。最终整个工作树 diff 路径仍在 CU 内。根 CODE_INDEX/AW 索引/根文档/其他 Agent/backend/frontend-js 均未触达。

## DEV self-check：环境、命令与结果

环境：macOS Darwin arm64；Node `v22.19.0`，pnpm `11.11.0`，cargo `1.89.0`，rustc `1.89.0`。
源码使用现有技术代际；Cargo.lock 从 542 个包缩减为 428 个包，保留包版本未升级；CU pnpm-lock 仅移除 @tauri-apps/api 相关锁项。消费者固定现有直接依赖版本并拥有自身锁文件。
2026-10-15 修改 Tauri 配置前核对[官方 config](https://tauri.app/reference/config/)，确认 devUrl 与相对配置文件 frontendDist 语义；保留 `../dist` 和既有 core capability 权限基线。

下表命令默认在 CU 目录执行，consumer 行在 `examples/source-consumer/`。这些是 Development 自检，不是独立 QA。

| 命令 / 动作 | 实际结果 | 证据 |
| --- | --- | --- |
| `pnpm install --lockfile-only --offline` | 退出 0，CU 锁文件必要删除 | pnpm-lock diff |
| 初次 `pnpm build` / sandbox 中再次运行 | 退出 1；pnpm 自动依赖检查触发 install，复制 node_modules 的清理因无 TTY 被拒；未到源码编译 | 后续正常环境重跑成功，见下行；无修改依赖生态 |
| `CI=true pnpm install --frozen-lockfile` | 退出 0，使用本机正常依赖安装环境 | `cu-install.log` |
| `pnpm build`（本机正常 pnpm 环境） | 退出 0，vue-tsc + Vite，1618 modules，2.24s | `cu-build.log` |
| `cargo fmt --manifest-path src-tauri/Cargo.toml --check` | 退出 0 | `cargo-fmt.log` |
| `cargo check --manifest-path src-tauri/Cargo.toml --locked` | 退出 0，0.85s；初次 offline check 15.95s 也退出 0 并产生必要锁文件更新 | `cargo-check.log` / `cargo-check-initial.log` |
| `pnpm tauri build --no-bundle` | 退出 0；release 54.42s，macOS arm64 原生可执行文件成功 | `tauri-build.log` |
| `src-tauri/target/release/aiis-aw-console-ui` | 实际原生 PID 58672；窗口创建与事件循环 ready；检查后 SIGTERM，工具退出 143 | `native-start.log`，下文永久收录关键日志 |
| `pnpm dev` | 15193 strict，浏览器一次聚焦检查成功；完成后关闭 PID 55232，wrapper 退出 0 | `cu-dev.log`，下文界面观察 |
| consumer `pnpm install --offline` | 退出 1，store 缺 plugin-vue tarball；随后正常安装 | 后续安装日志 |
| consumer `CI=true pnpm install` | 退出 0，独立 node_modules/lockfile | `consumer-install.log` |
| consumer `pnpm build` | 退出 0，vue-tsc + Vite，1614 modules，2.17s | `consumer-build.log` |
| CU 停止后 consumer `pnpm preview` | PID 59411 / 14194；CU 15193 HTTP000，consumer HTTP200，浏览器组件/主题/语言/事件正常；检查后 SIGTERM，wrapper 退出 0 | `consumer-preview.log`，下文运行观察 |
| `python3 /private/tmp/cu-001-r1/audit.py` | 退出 0，locale 对称/字面量 key、公共隔离、六 README 链接、Cargo 保留版本通过 | `static-audit.log` |
| `git diff --check` | 退出 0 | 当前工作树 |

辅助 audit 初稿使用系统 Python 不提供的 `tomllib`，退出 1；改为标准库正则核对 Cargo package name/version 后退出 0。未安装辅助依赖进入项目环境。构建只出现既有第三方 PURE 注释警告，install 提示 vue-i18n 9 已 deprecated；本任务未升级。

### 原生启动证据（来源：编译后的原生进程 stdout）

```json
{"timestamp":"2026-10-15T09:19:40.928114Z","level":"INFO","fields":{"event":"cu_process_start","process":"aiis-aw-console-ui","result":"starting"}}
{"timestamp":"2026-10-15T09:19:41.302408Z","level":"INFO","fields":{"event":"cu_window_created","window":"main","title":"AIIS AW Console UI","result":"ready"}}
{"timestamp":"2026-10-15T09:19:41.302425Z","level":"INFO","fields":{"event":"cu_event_loop_ready","process":"aiis-aw-console-ui","result":"ready"}}
```

CLI pgrep 同时确认实际 PID；Rust 启动源码不存在工业配置读取、命令注册或外部连接代码。未接管原生 AX 或长时间轮询 GUI；原生证据仅声明进程/窗口创建/事件循环启动，不宣称原生交互测试。

### 一次聚焦界面与消费检查（来源：Vite/IAB 浏览器）

- CU `http://localhost:15193` 初始中文亮色，截图可见既有侧栏/玻璃顶栏/卡片、公共入口说明和设计样例告示；切换后英文暗色文案和主题生效。
- Components 展示 Idle/Ready/Attention/Error 四胶囊；Primary action 点击出现 “Action triggered in this preview”，disabled action 禁用。
- Parameters 修改标题为 `CU preview`、选 Attention sample、开启 compact，右侧公共 ConsoleCard 标题/胶囊/密度即时更新；截图可见英文暗色布局无重叠。
- 已停止原生 CU 和 CU Vite，然后打开 `http://localhost:14194` 的 consumer 自有 dist。截图和 AX 可见独立壳层与 Design sample，切成中文暗色后可见“源码消费示例”，点击动作出现“消费端收到动作事件”。同时 CU 15193 HTTP000、consumer 14194 HTTP200，pgrep 仅见消费者进程。
- 两个临时 IAB 标签页均已关闭；初次 `visible:true` 在子 agent 不支持，随即使用 `visible:false`，没有调用 cua.getApp 或增加 GUI 轮询。

### 资源收尾与限制

本任务创建的原生 PID 58672、CU Vite PID 55232、消费者 preview PID 59411 均已关闭，最终 pgrep 未见匹配 CU/consumer 进程。未启动其他 Agent、Docker、数据库或设备连接。
保留 `/private/tmp/cu-001-r1/`：恢复 tgz、实施辅助脚本、静态 audit 及上述构建/启动日志，供 QA 复核及最终验收后主协调盘点；正文永久保留关键结果，临时路径不是唯一证据。CU 自身 `node_modules`、`dist`、`src-tauri/target`（含原有缓存和本次产物）及 consumer 自身 `node_modules` / `dist` 保留且被忽略；不清理来源不明旧缓存。无新增 frozen 工程。

已按批准口径完成构建/一次启动/引用，不追加 CA/TSS 回归、旧工业 Rust 全套测试、多 cwd/端口/截图矩阵或压力测试。Windows/Linux、签名/安装包分发、原生交互、实际 Agent 接入、现场业务链与工业配置都没有验证。源码消费在编译期需要可访问公共源码并正确配置依赖单实例；运行已构建 dist 无需 CU 在线。保留旧依赖代际及大尺寸 Element Plus CSS 是已知现状，不构成本任务升级范围。

## 精确 Development 修改文件

以下路径相对 CU；删除文件也逐项列出。PM spec 与主协调的四个本地索引文件不列为 Development 写入。

```text
.env.example
README.md
README.zh-CN.md
config/plc_points.yaml
config/plc_snapshot_policy.yaml
examples/source-consumer/README.md
examples/source-consumer/README.zh-CN.md
examples/source-consumer/index.html
examples/source-consumer/package.json
examples/source-consumer/pnpm-lock.yaml
examples/source-consumer/pnpm-workspace.yaml
examples/source-consumer/src/App.vue
examples/source-consumer/src/locales/en-US.json
examples/source-consumer/src/locales/zh-CN.json
examples/source-consumer/src/main.ts
examples/source-consumer/tsconfig.json
examples/source-consumer/vite.config.ts
index.html
package.json
plans/CU-001-workbench-foundation/tasks.md
pnpm-lock.yaml
src-tauri/Cargo.lock
src-tauri/Cargo.toml
src-tauri/build.rs
src-tauri/capabilities/default.json
src-tauri/src/bin/aiis-ics-control-agent-runtime.rs
src-tauri/src/commands/headless_runtime.rs
src-tauri/src/commands/mod.rs
src-tauri/src/commands/plc_collection.rs
src-tauri/src/commands/plc_diagnostics.rs
src-tauri/src/commands/runtime_snapshot.rs
src-tauri/src/config/mod.rs
src-tauri/src/domain/authorization.rs
src-tauri/src/domain/headless_runtime.rs
src-tauri/src/domain/mod.rs
src-tauri/src/domain/plc.rs
src-tauri/src/domain/plc_collection.rs
src-tauri/src/domain/runtime.rs
src-tauri/src/infrastructure/database.rs
src-tauri/src/infrastructure/database/entities/mod.rs
src-tauri/src/infrastructure/database/entities/monitor_collector_state.rs
src-tauri/src/infrastructure/database/entities/plc_db_block_latest_snapshot.rs
src-tauri/src/infrastructure/database/entities/plc_db_block_raw_snapshot.rs
src-tauri/src/infrastructure/database/repositories/mod.rs
src-tauri/src/infrastructure/logging.rs
src-tauri/src/infrastructure/minimal_s7_adapter.rs
src-tauri/src/infrastructure/mod.rs
src-tauri/src/infrastructure/plc_client.rs
src-tauri/src/infrastructure/plc_decode.rs
src-tauri/src/infrastructure/plc_points.rs
src-tauri/src/infrastructure/plc_s7.rs
src-tauri/src/infrastructure/plc_snapshot_policy.rs
src-tauri/src/infrastructure/rust_snap7_adapter.rs
src-tauri/src/lib.rs
src-tauri/src/main.rs
src-tauri/src/services/authorization_gate.rs
src-tauri/src/services/mod.rs
src-tauri/src/services/plc_collection.rs
src-tauri/src/services/plc_diagnostics.rs
src-tauri/src/services/runtime_snapshot.rs
src-tauri/tauri.conf.json
src/App.vue
src/app/README.md
src/app/README.zh-CN.md
src/app/collection/locales/en-US.json
src/app/collection/locales/zh-CN.json
src/app/collection/manifest.ts
src/app/collection/views/status/index.vue
src/app/gates/locales/en-US.json
src/app/gates/locales/zh-CN.json
src/app/gates/manifest.ts
src/app/gates/views/authorization/index.vue
src/app/plc/locales/en-US.json
src/app/plc/locales/zh-CN.json
src/app/plc/manifest.ts
src/app/plc/views/diagnostics/index.vue
src/app/runtime/locales/en-US.json
src/app/runtime/locales/zh-CN.json
src/app/runtime/manifest.ts
src/app/runtime/views/overview/index.vue
src/components/common/MetricGrid.vue
src/components/console/ConsoleActionButton.vue
src/components/console/ConsoleCard.vue
src/components/console/ConsoleInfoGrid.vue
src/components/console/ConsoleMetricCard.vue
src/components/console/ConsoleOperationDialog.vue
src/components/console/ConsoleTableShell.vue
src/components/console/PlcRuntimeUnitPicker.vue
src/components/console/ReadinessGrid.vue
src/components/shell/AgentSidebar.vue
src/components/shell/AgentTopbar.vue
src/components/shell/RuntimeStatusCapsule.vue
src/console/composables/useAgentLocale.ts
src/console/composables/useAgentTheme.ts
src/console/composables/useControlAgentConsole.ts
src/console/sections.ts
src/console/types.ts
src/env.d.ts
src/layouts/AgentLayout.vue
src/locales/en-US/common.json
src/locales/en-US/navigation.json
src/locales/en-US/workbench.json
src/locales/index.ts
src/locales/zh-CN/common.json
src/locales/zh-CN/navigation.json
src/locales/zh-CN/workbench.json
src/main.ts
src/services/runtimeSnapshot.ts
src/styles/app.css
src/styles/theme.css
src/ui/components/AgentLayout.vue
src/ui/components/AgentSidebar.vue
src/ui/components/AgentTopbar.vue
src/ui/components/ConsoleActionButton.vue
src/ui/components/ConsoleCard.vue
src/ui/components/StatusCapsule.vue
src/ui/index.ts
src/ui/styles/components.css
src/ui/styles/index.css
src/ui/styles/theme.css
src/ui/types.ts
src/workbench/Workbench.vue
src/workbench/workbench.css
vite.config.ts
```

## Developer handoff

交接目标：**CU-001 r1 / 当前工作树（HEAD 1a5aa2d2fe7089b5671218865238cfaa240f9a30）**；输入是批准 spec、本 tasks、上述全部实现文件及 git diff/untracked 文件、构建和启动日志。Development 已完成 R1–R4 对应的克制自检。
下一 gate：主协调显式启动不继承本 Development 推理的 fresh-context 命名 Verification，独立复核 AC1–AC8 现有证据；仅对有疑点项目复跑。QA 记录归 checklist；Human Owner 最终验收在 QA 之后。本 handoff 不授予发布、部署、Git refs 或现场动作。

## 交接后文案澄清（2026-10-15）

按主协调转达的最终阅读澄清，仅修改 CU `README.md` / `README.zh-CN.md`，将相邻工程的“Frozen CA / 冻结 CA”改为“CA、DAA、SMA 均为独立工程，CU 不改变它们的实现或职责”的双语同义表述，保留 CU 来源说明，避免把当前 CA 与历史来源混称。本追加只记录 Development 文案变更，不改源码、不变更既有构建/启动证据，不运行构建、测试或启动；交由 Verification 只读确认两处文案差异。
