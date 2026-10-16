Task ID: CU-002
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: CU-002 r1 implemented in current working tree at HEAD 1a5aa2d2fe7089b5671218865238cfaa240f9a30; fresh-context Verification to review approved spec, this DEV record and the CU-002 incremental diff
Task Namespace: aiis-ics-arch
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-002 r1 Development handoff

## 依据与范围

2026-10-16（Asia/Shanghai）命名 Development 按 [owner_approved spec](spec.md) 实施。已读取根 AGENTS / README pair / PLAN pair、canonical lifecycle workflow、development TOML、AW / CU 最近 README 与 PLAN、消费者 README pair、完整 CU-001 bundle、当前 CU-002 bundle（实施前仅 spec）及相关公共层/宿主/参照实现。触达范围内未发现更近 AGENTS。使用 frontend-ui（既有主题及共享组件边界，参考 DESIGN / FRAMEWORK）、i18n-workflow、desktop-tauri（现有启动路径）、code-document-indexer（新增组件沿用中文头注释）。不加载无关后端/PLC规范，不修改 skills。

Human Owner 已精确批准 CU-002 r1，验证限定“能构建、能启动、能引用”，不做全量回归。本记录是 Development self-check，不给 QA verdict 或 Human Owner final acceptance；fresh-context Verification 由主协调在本 handoff 后启动。角色 profile 为 contract_only，主会话、串行交接及 diff 审计仍是合同控制，不宣称平台 ACL、强制路由或完整团队激活。

## 实施与 R / AC 对应

| 需求 / 验收 | 实际实现与 DEV 证据 |
| --- | --- |
| R1/R2 / AC1 | 新增 ThemeToggle、LanguageSwitch，经 src/ui/index.ts 导出。ThemeToggle 输入 theme: UiTheme / label，LanguageSwitch 输入 locale: 'zh-CN' \| 'en-US' / zhLabel / enLabel / label；二者仅 emit toggle，无内部状态、存储或私有依赖。既有六组件、types、theme.css、样式入口均保留。 |
| R1 / AC2 | 原生 button type=button；ThemeToggle 44×44px、20px 固定 Moon、aria-pressed 表达暗色；LanguageSwitch 44px 高胶囊，宿主传“中 / EN”，当前语言高亮。title 与 aria-label 共用宿主目标提示，focus-visible 2px token 描边。样式只在 components.css 末尾追加 .aw-ui 范围内两控件规则，颜色/边框/阴影全部使用现有 --agent-* tokens。 |
| R3 / AC2–AC4 | Workbench 原 actions 插槽同位置替换两按钮，从公共入口导入；仅删除替换后无用 Moon/Sunny 导入。设计样例胶囊、顶栏结构/顺序、侧栏与其他展示不变。cu.theme / cu.locale 原宿主持久化函数沿用。本次 CU build 和 tauri dev 启动成功；交互观察来自同次 dev 服务的浏览器。 |
| R2/R3 / AC5 | 既有 source-consumer 从 @aw-ui 导入同两组件，用自身 theme / locale 和 toggle 绑定，未增加持久化。消费者 build 后，在 CU 全部停止时 preview 自身 dist，点击主题/语言改变其自身页面、语言高亮和目标提示。 |
| R2/R3 / AC6 | 工作台/消费者两组 locale 键结构对称，所需标签及目标提示由各自 locale 提供；仅删除替换后无用键。四 README 更新出口/受控输入/事件/文案/样式作用域/独立运行合同，链接检查通过。索引由主协调机械同步，Development 不写。 |

## 起点、恢复与精确修改文件

起始及交接 HEAD：`1a5aa2d2fe7089b5671218865238cfaa240f9a30`，交付目标为**当前工作树**，未创建 commit、branch、worktree、PR 或 push。CU-001 已验收未提交内容不是本任务变更，未以 HEAD 覆盖其内容。

首次写实现前，将拟改的 12 个既有文件复制至 `/private/tmp/cu-002-r1/before/`（目录起初不存在）；两个新组件与本 tasks 原先不存在。`manifest.txt` 枚举下列 14 个实现/说明路径；`baseline.txt` 记录 HEAD 与新文件。`implementation.diff` 从这些恢复副本逐项生成，仅表达 CU-002 实际增量（新组件以 /dev/null 为起点），供 QA 对照当前源码。无需全仓快照/hash。回退时只能先核对并发归属，再针对该增量处理；本记录不授权当前回退。

实际 Development 修改路径（相对 CU）：

```text
src/ui/components/ThemeToggle.vue
src/ui/components/LanguageSwitch.vue
src/ui/index.ts
src/ui/styles/components.css
src/workbench/Workbench.vue
src/locales/en-US/workbench.json
src/locales/zh-CN/workbench.json
examples/source-consumer/src/App.vue
examples/source-consumer/src/locales/en-US.json
examples/source-consumer/src/locales/zh-CN.json
README.md
README.zh-CN.md
examples/source-consumer/README.md
examples/source-consumer/README.zh-CN.md
plans/CU-002-topbar-utility-controls/tasks.md
```

未写 spec/checklist、CU PLAN/catalog、AgentTopbar、既有六组件、旧 CSS 规则、token 文件、types、依赖/锁文件、构建/端口配置、Tauri/Rust、CU-001 bundle、CODE_INDEX、根/AW文档或其他工程。初始 git status 已有 `src-tauri/gen/schemas/capabilities.json` 差异，本轮不把该既有差异归为 CU-002，不手改/恢复生成 schema。构建产物与缓存遵循既有 ignore。

## DEV self-check：命令、退出码与观察

环境：macOS `Darwin arm64`，Node `v22.19.0`，pnpm `11.11.0`。沿用现有依赖和锁文件，无安装新辅助依赖。以下是实际 Development 检查，默认 cwd=CU；consumer 行 cwd=examples/source-consumer。日志保留在 `/private/tmp/cu-002-r1/`，关键事实在本文件永久记录。

| 命令 / 动作 | 实际结果 |
| --- | --- |
| `pnpm build`（输出至 cu-build.log） | 退出 0；vue-tsc --noEmit + Vite，1622 modules，2.17s；自身 dist 生成。 |
| `lsof -nP -iTCP:15193 -iTCP:14194 -sTCP:LISTEN` + 定向 `ps` | 启动前无端口占用；sandbox 内 ps 被拒，随后只为进程归属与启动使用本机授权执行环境，未改项目配置。 |
| `pnpm tauri dev`（tauri-dev.log） | Cargo dev 0.37s 完成，Vite 15193 strict ready；原生 PID 11214，窗口与事件循环 JSONL ready，见下文。观察后 SIGTERM 停止原生11214、Vite11122、pnpm10923，wrapper 最终退出143（主动停止，不是启动失败）。 |
| 同轮 `http://localhost:15193` IAB 聚焦观察 | 点击两控件生效；Enter 激活主题、Tab 到语言控件、Space 激活语言；目标提示/暗色pressed/语言高亮即时更新，focus-visible 可见。具体值见下文；未调用 cua.getApp。 |
| consumer `pnpm build`（consumer-build.log） | 退出 0；vue-tsc --noEmit + Vite，1618 modules，2.22s，自身 dist 生成。 |
| CU 停止后 consumer `pnpm preview`（consumer-preview.log） | 14194 strict，PID11934；curl CU15193 HTTP000、consumer14194 HTTP200；独立页面两控件点击生效。观察后 SIGTERM11934，preview wrapper退出0。 |
| `python3 - <<'PY'` 标准库定向静态检查 | 退出 0；两组 locale 键相同、宿主 literal t keys可解析；四 README 的相对链接与新组件合同存在；新组件无存储/工作台/i18n/Pinia/Tauri/mount依赖且具有button/title/aria；原 CSS 是新文件完整前缀，仅追加规则；生成14文件 implementation.diff。未新增测试套件或项目辅助依赖。 |
| `git diff --check -- automation-world/console-ui` | 退出 0，无空白错误。 |
| 收尾 `ps` / `lsof` 精确核对 | 无 CU/consumer运行进程，无15193/14194监听；lsof无匹配退出1为预期。两个本任务IAB tab均已关闭。 |

两次 build 均有第三方 @vueuse PURE 注释位置警告，不影响退出0，未扩展为依赖升级。登录 shell 的 Homebrew shellenv 曾报 sandbox ps 权限提示，构建本体仍成功；进程检查已在授权环境完成。

### 本次原生启动事实

`pnpm tauri dev` 真实创建当前 macOS 原生进程与窗口，关键 JSONL 如下（UTC，换算本地为2026-10-16）。未用浏览器代替原生启动：

```jsonl
{"timestamp":"2026-10-15T16:06:20.845176Z","level":"INFO","fields":{"event":"cu_process_start","process":"aiis-aw-console-ui","result":"starting"}}
{"timestamp":"2026-10-15T16:06:21.028994Z","level":"INFO","fields":{"event":"cu_window_created","window":"main","title":"AIIS AW Console UI","result":"ready"}}
{"timestamp":"2026-10-15T16:06:21.034280Z","level":"INFO","fields":{"event":"cu_event_loop_ready","process":"aiis-aw-console-ui","result":"ready"}}
```

### 同轮浏览器与独立消费观察

CU 浏览器沿用其既有偏好，初始英文暗色。点击主题与语言后出现中文亮色：主题 title/aria-label为“切换到夜间模式”、aria-pressed=false，语言目标“切换到英语”、高亮“中”。DOM实际测量主题44×44px，语言高44px/宽92.390625px，元素均BUTTON。Enter切换到暗色后目标变为“切换到日间模式”，pressed=true；Tab聚焦语言，`:focus-visible=true`，outline=`rgb(103, 232, 249) solid 2px`。Space切换到英文，高亮EN，目标提示为“Switch to light mode”与“Switch to Chinese”。暗色主题按钮背景=`rgb(34, 211, 238)`，前景=`rgb(6, 33, 42)`，使用现有强调/前景tokens。

一次截图 `/private/tmp/cu-002-r1/cu-controls.jpg` 可见圆形Moon与胶囊、EN高亮及语言键盘focus，原顶栏结构和设计样例标识保留。交互来自IAB浏览器，不宣称原生窗口交互覆盖。

已关闭CU原生/dev及CU tab后，消费者自身dist初始英文亮色；点击两控件后为中文暗色，标题“源码消费示例”，主题pressed=true且目标“切换到日间模式”，语言高亮“中”且目标“切换到英语”，两控件高44px。同期CU15193 HTTP000、consumer14194 HTTP200，进程列表仅见消费者preview，证明无需在线CU；消费者状态从自身ref/i18n驱动，无新增持久化。观察后关闭该tab和preview。

## 资源、限制与下一 gate

本任务创建的原生PID11214、Vite11122、pnpm10923、consumer preview11934以及两个IAB tab均已关闭；不停止用户/其他任务进程。保留 `/private/tmp/cu-002-r1/` 的12文件恢复副本、manifest、baseline、14文件增量diff、两次build/tauri-dev/consumer-preview日志与一次截图供QA和验收追溯。关键结果已收录本文，临时目录不是唯一证据；验收后由主协调按归属盘点，不清理来源不明缓存。CU/consumer既有node_modules/dist与CU target保留且忽略；无新增worktree/branch或冻结工程。

已完成批准范围的必要构建、一次当前主机启动、同轮两控件观察与一次独立引用。没有全量回归、其他Agent/CA/TSS验证、额外Cargo套件、native打包、跨平台、签名/分发/发布/部署、真实数据库/PLC或工业runtime验证。原生窗口交互没有单独验证；原生启动与浏览器交互证据明确分开。源码消费仍需编译期公共源码可达及消费端依赖单实例，已编译dist运行无需CU在线。现有依赖代际和CSS体量不在本任务升级范围。无已知新增实现阻塞。

**精确 developer_handoff：CU-002 r1 / 当前工作树（HEAD 1a5aa2d2fe7089b5671218865238cfaa240f9a30）**。fresh-context命名Verification输入为批准spec、本tasks、上述15文件、`/private/tmp/cu-002-r1/before/`及implementation.diff、实际命令日志与一次截图，另结合当前git diff/untracked事实区分CU-001基础及协调者索引。本任务实施和DEV self-check已记录；请主协调显式启动fork_turns=none的Verification独立审阅AC1–AC6，只有疑点或缺证据才复跑对应检查。Verification仅写checklist并给独立结论，Human Owner最终验收在QA之后；本handoff不授予发布/部署/Git refs/真实设备操作权限。
