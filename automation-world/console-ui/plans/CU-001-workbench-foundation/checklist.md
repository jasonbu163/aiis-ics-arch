Task ID: CU-001
Revision: r1
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner accepted CU-001 r1 on 2026-10-15 (Asia/Shanghai); CU-only status closeout, original QA evidence and limits retained
Task Namespace: aiis-ics-arch
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-001 r1 独立验证

## 验证依据与环境

- 验证日期：2026-10-15；目标为 HEAD `1a5aa2d2fe7089b5671218865238cfaa240f9a30` 加当前 CU 工作树。
- 本次为 Development `developer_handoff` 之后的新鲜上下文命名 Verification；未继承 Development 对话推理。独立完整读取 [owner_approved spec](spec.md)、[Development tasks](tasks.md)、根 AGENTS / README pair / PLAN pair、AW 与 CU 最近 README / PLAN、CU catalog、源码层次与消费者教程。触达目录未发现更近的 AGENTS.md。
- 已读取 canonical lifecycle workflow 与 verification profile，按表面使用 project-governance、aiis、frontend-ui（主题及组件边界参考 FRAMEWORK / DESIGN）、i18n-workflow、desktop-tauri、rust-runtime（继承执行链清理及启动 JSONL）、code-document-indexer。只验证；本轮唯一写入为本 checklist。
- QA 本机 `uname -sm`：`Darwin arm64`。DEV 记录环境：Node `v22.19.0`、pnpm `11.11.0`、cargo/rustc `1.89.0`；锁文件根依赖与 README 所列 Vue `3.5.38`、Element Plus `2.14.2`、icons `2.3.2`、vue-i18n `9.14.5`、Vite `5.4.21`、TypeScript `5.9.3`、vue-tsc `2.2.12` 一致。
- Human Owner 明确限定“只改 CU”“验证能构建、能启动、能引用”“不用做全量回归”。本轮独立审阅源码、关键 diff、删除路径、全部新增公共层/工作台/consumer 源码及现有日志，不重跑构建、测试、静态 audit，不启动应用、Vite、consumer 或 GUI，不增加 hash、端口或截图矩阵。
- 角色 profile 为 `contract_only`。实际 fresh-context 调用、串行交接及 diff/checklist 审计构成本轮合同控制；TOML 配置不作为平台 ACL、强制路由、独立确认的运行模型参数或完整 Agent Team 激活证明。

## AC1–AC8 检查结果

| ID | 独立检查与证据 | 结果 |
| --- | --- | --- |
| AC1 | `package.json`、Cargo 显式 bin/default-run 均为 `aiis-aw-console-ui`，lib 为 `aiis_aw_console_ui_lib`，Tauri product/window 与 HTML title 为 `AIIS AW Console UI`，identifier 为 `com.aiis.aw.consoleui`。scripts/Vite dev `15193`、preview `14193` 均 strict，devUrl 一致。工作台和私有 locale 仅读写 `cu.theme` / `cu.locale`，未迁移旧 Agent 偏好。 | 通过 |
| AC2 | 当前 Rust 源码只有 `main.rs` / `lib.rs`；仅 Tauri 窗口、事件循环和 tracing 启动事件，无工业配置读取、业务 invoke_handler、PLC/DB 连接、采集 loop 或 headless 参数。`autobins=false` 且唯一显式 bin；Cargo 直接依赖仅 tauri/tracing/tracing-subscriber，旧 driver feature、工业脚本、配置样例、业务模块及专属依赖已移除。结合原生启动证据满足本阶段正常启动检查。 | 通过 |
| AC3 | [公共代码入口](../../src/ui/index.ts) 导出六组件和 UiTheme/UiTone/ActionTone/NavigationItem；逐个读取组件及传递类型依赖，均限公共层、Vue、Element Plus、icons。无 App/main/workbench、CU locale 实例、IPC/Tauri、runtimeSnapshot、env、偏好或 mount 副作用。[样式入口](../../src/ui/styles/index.css) 仅导入公共 theme/components CSS，主题 token 在 `.aw-ui`，暗色由 `data-aw-theme` 显式控制。工作台从 `../ui`、consumer 从指向同一入口的 `@aw-ui` 导入。 | 通过 |
| AC4 | [Workbench](../../src/workbench/Workbench.vue) 有壳层、四展示状态/动作、标题/色调/compact 参数与 reset；状态只在当前 ref 中变化，无业务保存或设备动作。固定“设计样例 / Design sample”提示持续覆盖样例区域，双语 keys 对称且动态段来自固定 tone/theme 枚举。DEV 一次浏览器观察确认中文亮色、英文暗色、组件点击反馈、参数即时变化；其永久记录见 tasks 的聚焦界面检查。 | 通过；浏览器证据 |
| AC5 | 核对 `cu-build.log`：vue-tsc 后 Vite 成功，1618 modules / 2.24s；`cargo-check.log`：本 CU crate `Finished dev` / 0.85s。`cargo-fmt.log` 为空，与 tasks 记录的 format 退出 0 相符。实际命令/退出码归 DEV，未将 QA 读取日志称为重新执行。 | 通过；现有构建证据 |
| AC6 | `tauri-build.log` 记录 `pnpm tauri build --no-bundle`、beforeBuildCommand 成功、release 54.42s 和本 CU 原生可执行文件路径；`native-start.log` 三条 JSONL 与当前启动源码一致，main 窗口标题正确。tasks 记录实际原生 PID 58672、pgrep 及检查后 SIGTERM/143。仅证明当前 macOS arm64 原生进程、窗口创建和事件循环启动。 | 通过；原生 CLI 证据 |
| AC7 | [consumer 配置](../../examples/source-consumer/vite.config.ts) 只 alias 两公共入口，dedupe Vue/Element Plus/icons/i18n；TS paths 指向消费端自己的声明，具有独立 package/lock/main/i18n。`consumer-build.log` 记录 vue-tsc + Vite、1614 modules / 2.17s。DEV 永久记录：停止原生 CU 和 CU Vite 后 consumer 自有 dist 在 14194 HTTP200，CU 15193 HTTP000，中文暗色与点击“消费端收到动作事件”生效。无 CU App/私有 locale/IPC/Rust 运行依赖，未接入真实 Agent。 | 通过；构建与浏览器消费证据 |
| AC8 | 三组 README pair 的身份、源码层次、运行/消费命令、编译期源码可达及运行期自有 dist 边界一致；现有 static-audit.log 与已读 audit 源码确认六 README 相对链接和 key 检查结果。唯一 bundle 元数据/批准/handoff 匹配；CU PLAN/catalog 为 qa_in_progress，下一次由协调者机械同步本 verdict。路径集合核对和 diff check 结果见下文，未触达其他工程。 | 通过 |

## 现有 DEV 命令与证据复核

日志均位于 `/private/tmp/cu-001-r1/`；以下退出码为 tasks 的真实 Development 执行记录，QA 读取对应输出核对，未复跑。

| 命令及 cwd | DEV 结果与 QA 复核内容 |
| --- | --- |
| CU：`pnpm build` | 退出 0；`cu-build.log` 含类型检查与生产构建成功、独立 dist JS/CSS 输出。 |
| CU：`cargo fmt --manifest-path src-tauri/Cargo.toml --check` | 退出 0；`cargo-fmt.log` 无输出，源码格式与 handoff 相符。 |
| CU：`cargo check --manifest-path src-tauri/Cargo.toml --locked` | 退出 0；`cargo-check.log` 含本 CU crate 与成功结束。 |
| CU：`pnpm tauri build --no-bundle` | 退出 0；`tauri-build.log` 含成功 release 构建和 `src-tauri/target/release/aiis-aw-console-ui`。 |
| CU：`src-tauri/target/release/aiis-aw-console-ui` | PID 58672；原生 stdout 三事件成功，主动 SIGTERM 后退出 143，不是启动失败。 |
| CU：`pnpm dev` | `cu-dev.log` 记录 15193 strict、Vite ready；交互结果来自 tasks 的一次 IAB 浏览器观察。 |
| consumer：`pnpm build` | 退出 0；`consumer-build.log` 含类型检查与自身生产 dist。 |
| consumer：`pnpm preview` | `consumer-preview.log` 明确 127.0.0.1:14194 strict；停止 CU 后独立运行/主题/语言/点击事实由 tasks 永久记录，未冒充 native 交互。 |
| CU：`python3 /private/tmp/cu-001-r1/audit.py` | 退出 0；已读脚本和 `static-audit.log`：locale 对称/字面量 key、公共隔离、六 README 链接、Cargo 保留版本通过，542 → 428 packages。 |

原生 JSONL 关键事实：`2026-10-15T09:19:40.928114Z` 的 `cu_process_start`，`09:19:41.302408Z` 的 `cu_window_created`（`main`、`AIIS AW Console UI`、`ready`），以及 `09:19:41.302425Z` 的 `cu_event_loop_ready`。完整三行已经永久收录 tasks；临时日志不是唯一证据。浏览器观察也已永久收录 tasks，未生成或要求新增截图文件。

DEV 初次构建的依赖清理/TTY 失败、consumer offline 缺 tarball、辅助 audit 的 tomllib 不可用均有后续成功记录，没有遗留实现 failure。第三方 PURE 注释警告与 vue-i18n 9 deprecated 提示保留为已知现状，不扩大本任务依赖升级范围。

## QA 实际只读命令与 diff 审计

| 命令 / 方法 | 实际结果 |
| --- | --- |
| `git rev-parse HEAD` | 退出 0；与 tasks 的起点/交接 HEAD 完全一致。 |
| `cat` / `sed` 阅读合同、源码、关键 `git diff HEAD -- <CU 路径>` 和现有日志；`rg --files --hidden --no-ignore` 枚举当前源码/最近 AGENTS | 当前源码与交接一致。无更近 AGENTS 的 rg 返回 1（无匹配）；两次读取已删除旧 composable/style 路径返回 1，后续通过当前源码枚举确认其已按范围移除，不属于实现失败。 |
| `git diff --name-only HEAD -- automation-world/console-ui`、`git ls-files --others --exclude-standard -- automation-world/console-ui`，标准库只读 Python 将路径集合与 tasks 的逐项清单比较 | 退出 0；创建本 checklist 前为 101 个 tracked 差异 + 28 个新文件 = 129 路径；124 个 DEV 路径逐项一致，无未列/缺失项。其余五项恰为 PM spec 和协调者 CU PLAN/catalog pair。 |
| `git diff --name-only HEAD -- automation-world/console-ui/src-tauri/gen`；根 diff 仅做路径边界核对 | 退出 0；gen 无差异，CU 外 tracked diff 为空。确认本任务未修改 CA/DAA/SMA/backend/frontend-js/根索引或 AW 总体文档；不进行其他工程内容审计。 |
| `git diff --check -- automation-world/console-ui` | 退出 0，无输出。 |
| `git check-ignore -v <CU 与 consumer 的 node_modules/dist、CU src-tauri/target>` | 退出 0；五个依赖/构建目录均命中现有 ignore。 |
| `ls -lh /private/tmp/cu-001-r1`、`du -sh /private/tmp/cu-001-r1`、读取 recovery 目录 | 退出 0；总计 1.4M，恢复 `cu-before.tgz` 约 1.3M，构建/启动/audit 日志可读。 |

Tauri 构建曾自动生成 capability description 差异，DEV 已按起始 HEAD 机械恢复；QA 确认 gen 无 diff，未修改生成 schema。根 CODE_INDEX/AW 索引和旧 CA 总体说明由批准的 CU-only 写入约束及其他 owner 管理，不作为新 blocker。

## 资源、限制与验收审计

- DEV 收尾记录：原生 PID 58672、CU Vite PID 55232、consumer preview PID 59411 和两临时 IAB 标签页均已关闭，最终 pgrep 无匹配。QA 未重新启动或轮询进程/端口，不把历史关闭记录称为当前独立现场检查。
- `/private/tmp/cu-001-r1/` 的恢复归档、辅助脚本和日志继续保留，供 Human Owner 验收及协调者收尾盘点；QA 不执行回收。CU/consumer 的 node_modules/dist、CU target 保留且忽略，包含原有缓存，不能整体清理。
- 本阶段已验证基线：公共组件及主题源码隔离、轻量工作台、当前平台构建/原生启动、独立 consumer 构建与浏览器消费。
- 未验证且不阻断 r1：原生窗口交互、签名/安装包分发、Windows/Linux、实际 Agent 接入、工业配置、真实 PLC/DB 与 AW 业务链。全 CA/TSS 回归、长时间 GUI/压力/端口矩阵、发布和部署不在本次验收范围。
- 源码消费需要编译期可达的公共源码及消费端正确配置单实例依赖；已编译 dist 的运行不要求 CU 在线。保留既有依赖代际与 Element Plus CSS 体量不构成新增升级任务。

## Verdict、blocker 与 handoff

**Verdict：qa_passed。** AC1–AC8 在精确 r1 最小验收范围内证据充分，未发现需返回 Development 的实现失败；无开放 blocker。结论来自本次独立源码/合同/diff 审阅和对既有可读输出的复核，不宣称重跑或扩大覆盖。

交接 Human Owner：审阅 CU-001 r1 及本 checklist 后作最终验收。主协调可机械同步 CU PLAN/catalog 的 `qa_passed` 和 checklist 链接；本 Verification 不修改这些索引，也不授予发布、部署、Git refs、数据库或现场操作权限。

## Human Owner final acceptance

状态：**owner_accepted**。Human Owner 于 **2026-10-15（Asia/Shanghai）**明确验收 CU-001 r1，原话由主协调转达：

> 可以，CU-001 r1 验收通过，更新 CU 内的状态收尾就行，不用再追加测试了。

本次仅机械录入真实 Human Owner 决定；原 `qa_passed` verdict、证据和限制保留，下方文档 delta 复核段的 pending 为当次复核的历史状态。未追加构建、测试、启动、hash、扫描或新 QA。现有恢复与证据资源继续保留，供未提交工作追溯；不执行清理。CU 的四个本地索引由主协调机械同步。

## 交接后文档 delta 复核（2026-10-15）

只读核对 CU `README.md:16`、`README.zh-CN.md:16` 及 tasks 的“交接后文案澄清”追加段。与首次 QA 已读文本相比，英文 `Frozen CA` / 中文“冻结 CA”称呼已改为双语一致的“CA、DAA、SMA 均为独立工程，CU 不改变它们的实现或职责”；CU 来自 CA 源码副本、已移除自身旧执行链的说明保留。该句准确限定本任务对相邻工程的边界，没有改变批准范围或公共源码合同。

Development 追加记录明确本次 delta 仅为 README pair 与实施记录的文档变更，无源码变更；本次 QA 定向核对的 delta 未包含源码、配置、接口或行为调整，不重新进行源码扫描、构建、测试、启动或 GUI 检查。既有源码审阅与构建/原生启动/消费者证据继续适用，**qa_passed 维持，无新增 blocker；Human Owner final acceptance 仍 pending**。本次 Verification 仅追加本 checklist。
