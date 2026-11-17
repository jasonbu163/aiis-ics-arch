Task ID: DAA-015
Revision: r1
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: Human Owner 已最终验收 DAA-015 r1。任务专属临时测试资料已清理，中英文手册按钮名称已同步并通过独立静态核验。

# DAA-015 r1：独立验证 QA1

2026-11-14（Asia/Shanghai）。以命名 Verification 角色在不继承 Development 对话的 fresh context 核验；以 [批准规格](spec.md)、[Development 交接](tasks.md)、真实工作树及隔离测试为依据。核对根和最近作用域的契约与说明、canonical workflow；使用 project-governance、desktop-tauri、rust-runtime、frontend-ui、i18n-workflow 和 code-document-indexer 检查相应表面。仅写本文件；角色约束是工作流合同。

## 候选一致性

- 正式工作树基准 HEAD：`fd999224a8756feda314a33148304b4bf3461876`。实际批准 spec SHA-256：`f571dd51dbed26a3d59f70e78253dc6e47bb89a61453e8c3ed2a97773910340d`；交接 tasks SHA-256：`a303fc506afe79ced160134b69d8f0a7ebba9a820495ed2d404a1e60be9ca319`。
- 用 Python SHA-256 逐文件验证 Development 快照的 29 个原文件、3 个确实不存在的路径，及正式树 32 个候选文件，全部与交接相符。补丁 SHA-256 `df31164ef9844aac8698bc282686c9844c1e827281d31cf38859c71d41d2168d`；清单 SHA-256 `d54f7f06e430f982040fe51eaab57d515bdea82ae5d27e52b31f640aeeda6546`；补丁的 32 个路径与清单全等，`git apply --check --reverse` 退出 0。对比隔离的起点与 DAA 工作树，清单外仅 `tasks.md` 与协调者管理的两组双语索引；现有共享 Console UI、DS、后端与其他任务差异不计作本候选。索引涵盖新增启动运行器、设置组件与测试。没有以 HEAD 的整体脏差异替代任务补丁。

## 验收对照

| 验收 | QA1 | 独立证据 |
| --- | --- | --- |
| AC01 / R01–R02 | 失败 F-002 | 对照已确认预览的 HTML 结构与实际 Vue 装配：四卡、独立启动设置、上报运行、采集运行；折叠只留展开标题区，问号支持悬停与焦点。两页共用上报按钮、确认逻辑、地址和时间两行；长 URL 在组件中完整保留，CSS 使用可换行的独立值列。配置草稿条仍用于配置页；保存、激活、版本详情及回滚入口保留。DAA 两固定标签取消，产品标识、主题/语言/刷新操作保留，任务 diff 未动共享 UI 或另一个宿主。错误、未激活、未保存提示仍有对应入口；上报刷新失败时单一告警误标新采集快照，见 F-002。 |
| AC02 / R03 | 设置持久化通过；整项受 F-001 影响 | 原生 `run → local_recovery::open → LocalEngine::open → startup_automation` 源码与合成重开测试；新/已封存兼容 profile 的两项独立偏好、四种组合的采集开关与上报启用尝试，合规目标的上报单独由原生恢复入口成功发送。无偏好默认均关，保存不改 etag/本次意图；合成 SQL 触发器中断保留旧值，未知 schema 失败保持停态且配置可读，前端未确认写入会要求重新读取。兼容 runtime2/3 仍拒绝新版上报；设置不改 DDL 或重建库。切页、定时/手工刷新、保存和激活均不调用自动启动入口。 |
| AC03 / R03–R04 | 失败 F-001 | 两个合成 PLC 独立调度，首次连接失败时另一台先保存采样，故障恢复后可采样；已有测试通过运行中暂停、待重连时断开与重开。静态路径核对活动版本、PLC 启用、组选入、读取和容量准入；手工暂停采集在连接退避期间仍会触发后续自动连接。 |
| AC04 / R05 | 已验证路径通过 | 原生恢复入口 + profile 定向内存 HTTP：只发参与且匹配绑定的逐份样本，由匹配回执确认；新增合规参与 PLC 后再次打开可发，未重切启动开关。已阻断来源和旧目标已准备的 attempt=0 样本继续等待，目标、身份及冻结正文保持；合规的其他 PLC 可继续。源码核对保存与启动串行，尝试登记同一 actor 回合重新查目标/绑定/参与状态；暂停停止新派发，已发请求由原管线收尾。真实后端协议拒绝语义与历史样本仍按既有合同。 |
| AC05 | 测试与生产 feature 编译通过；原生窗口未执行 | 合成 profile 执行与原生入口共用的 `local_recovery::open`，核对实际 Tauri 配置注入 `rust-snap7-driver`，独立编译。TypeScript、Vite 产物、Vue 渲染证据见下。未运行 Mac/Windows Tauri GUI、实物驱动或实际 API。 |

## 返工证据

**F-001（R03 / AC02、AC03）：暂停采集不能取消尚未执行的自动重连。** 仅开启自动采集，用同一合成 profile 重开应用恢复入口；两台已启用 PLC 均有完整采集组；第一台注入一次 `connection_failed`，第二台正常采集。等待第一台进入退避，在约一秒的重连窗口前对它发送真实 actor 的 `request([plc_id], "collection", false, active_revision, None)`（对应工作台「暂停所选采集」）。日志先记录暂停 `operation_completed: applied`，约一秒后同一 PLC 仍出现 `connection_restored`。1.4 秒后读到 `desiredConnection=true, connected=true, desiredCollection=false, savedCycles=0`。隔离新增诊断用例 `qa_daa015_pause_offline_collection_must_cancel_automatic_connection_retry` 断言失败（退出 101；生产文件与仓库测试未改）。[actor 的手动采集分支](../../src-tauri/src/services/local_supervisor.rs#L618)清除自动采集标志但保留连接意图，[重连分支](../../src-tauri/src/services/local_supervisor.rs#L764)仍按该意图工作。预期：手动暂停后，尚未发起且仅由这个自动采集意图产生的连接重试不得执行；保留既有手动连接与在途动作语义，不把暂停变成普遍断开。回归应覆盖离线暂停，而不仅是离线断开和采集启动后暂停。

**F-002（R01 / AC01）：只上报刷新失败时，告警错误归用新采集时间，旧上报值仍作为当前状态呈现。** 先让 `daa_get_local_snapshot` 和上报读取同时成功：采集快照 `11:00:01`，上报「上报中」、待传 `13`、已确认 `7`、最近确认 `10:59:59`；再让采集快照成功更新至 `11:04:22`，只让上报读取抛出 `storage_busy`。用真实 composable、Overview 和 FactsDeliveryPanel Vue SSR（外围组件替身、无原生桥）得到告警「快照刷新失败，保留上海时间 2026-11-14 11:04:22 的最近成功快照」，但卡片仍是「上报中」、`13`、`7`、`10:59:59`，`暂停上报` 保持可用且无上报值过期标记。原因是 [refresh](../../src/console/composables/useLocalAcquisitionConsole.ts#L271)先写新的采集快照，再捕获上报读取失败；[工作台全局告警](../../src/app/runtime/views/overview/index.vue#L12)套用采集时间，而[共用上报卡](../../src/components/console/FactsDeliveryPanel.vue#L7)继续使用此前上报对象。配置页也有相同全局告警，并共用此卡。预期：清楚区分上报不可用/过期与采集刷新结果，旧上报值如保留应带明确过期标记，不把采集时间或历史回执时间当上报快照刷新时间；启停呈现不得使操作者把未知的上报状态当作已知。

## 命令、环境与资源

macOS 15.7.7（24G720）、Rust/Cargo 1.89.0、Node 22.19.0、pnpm 11.11.0。Rust 测试 `TMPDIR` 指向 QA 专属 `daa-008-r2-a-fixtures`，使用现有 Cargo 缓存与锁文件；测试副本的新增诊断仅位于临时目录。未读取或修改现有 `.local/dev`、dev API/数据库、真实 PLC、真实配置及样本；未启动或重启用户服务，不使用 Docker、MySQL 或实际 HTTP 监听。只读 `lsof` 未发现 15191 监听。

- `cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib startup_ -- --test-threads=1`：7/7，退出 0。用相同命令分别选择 `runtime2_and_3_keep_local_collection_and_refuse_v2_delivery` 和 `source_import_tests`：1/1 和 4/4，退出 0。现有未用测试 helper 告警不影响运行。
- 同一 Cargo 命令分别选择 `dispatch_rechecks_`、`qa_start_confirmation_must_not_dispatch_after_concurrent_settings_save`、`v2_worker_pause_save_preserves_inflight_receipt_and_stops_new_dispatch` 和 `plc_switch_rechecks_before_dispatch_without_stopping_other_sources`：合计 5/5，退出 0。
- `cargo fmt --manifest-path src-tauri/Cargo.toml --all -- --check` 与 `cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --features rust-snap7-driver`：退出 0，后一项验证生产 feature 编译，不连接驱动。
- 隔离 UI 源和依赖副本中 `node --test tests/*.test.mjs`：38/38，退出 0。首次复制误排除了依赖内的 `dist`，补齐原依赖副本后通过。`pnpm build` 在移动的依赖副本上触发非交互依赖重装保护；直接运行同一 package 脚本的 `./node_modules/.bin/vue-tsc --noEmit` 和 `./node_modules/.bin/vite build --outDir <QA>/daa-dist` 均退出 0；Vite 有第三方 VueUse 注释与大 chunk 提示。695 个 locale 键对称；受触达双语说明、规格与交接的相对文件链接目标存在（未验证所有锚点）。任务范围 `git diff --check` 无问题。
- F-001 使用隔离源码的同一 Cargo test 命令选择该诊断名，`--nocapture` 记录上述 actor 状态；F-002 用 `node <QA>/qa-stale.cjs` 记录合成前后状态及 Vue 输出。Chrome 无头启动退出 134、未得到 DOM，实浏览器与两平台原生窗口均无本轮证据；长地址实际像素布局、原生焦点与窗口操作仍待后续现场/原生检查。当前失败已由运行器及 Vue 可重复证据确认，与浏览器环境限制无关。
- Development 的 `/private/tmp/daa015-dev.DgUHuY`（准确起点、补丁、清单、合成夹具与产物）和 QA 的 `/private/tmp/daa015-qa.5cjZ1S`（诊断测试源、日志、合成夹具、UI 依赖副本和构建产物）均保留用于返工复核；关键失败值与复现步骤已持久写在本文件。正式树原有 Cargo target 为共享缓存。有证据或返工依赖时暂留；后续关闭后由协调者核对归属、进程和依赖并回收，QA 不回收。

Human Owner 最终验收：pending。F-001、F-002 修复并经新一轮独立 QA 后再进入最终验收。Windows 原生、Mac 原生 GUI、真实 PLC/后端及阶段 C 的验收分别记录；本轮没有相关放行。

写入后再次反向检查 Development 补丁通过；QA 前后未提交文件状态清单仅新增此 checklist。

## 独立验证 QA2（2026-11-14，Asia/Shanghai）

本轮以新的命名 Verification 角色和 fresh context 消费 [获批 r1](spec.md)、[返工交接第 6 节](tasks.md#6-qa1-返工及新的-developer_handoff)、QA1 历史、正式工作树和自己的隔离验证。核对根、Automation World、DAA 与触达目录的说明及 canonical workflow；使用 project-governance、aiis、rust-runtime、desktop-tauri、frontend-ui、i18n-workflow、code-document-indexer 对应任务表面。角色按 `contract_only` 执行。当前结论为 `qa_failed`。

### 本轮候选

- 交付树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `fd999224a8756feda314a33148304b4bf3461876`。批准的 spec SHA-256 `f571dd51dbed26a3d59f70e78253dc6e47bb89a61453e8c3ed2a97773910340d`，当前 tasks SHA-256 `e6f9de214d30894757c4df2b8ac991948815f80e520201085f7d79c65be7e0c1`。
- 逐文件匹配 Development 起点、QA1 候选与正式树三份摘要，共 34 路径，其中 3 路径在起点确实不存在。核对 `daa015-qa2-manifest.json` SHA-256 `c51f4cc5d55e319b65a79d037cef2f0cce6ab4a8672ddff5f1f407dbe86ecc7c`。起点→QA2 的 `daa015-qa2-source.patch`（34 文件，SHA-256 `3925faba55bb26a92106a0b49c6c1e066cb2a3d662aa192d2c6fa384dd2e4dd3`）及 QA1→QA2 的 `daa015-qa1-rework.patch`（8 文件，SHA-256 `766e4f83cab4a3688949098e11f0f0a61cd7cc5accefda3226125c95e7b94fff`），各补丁路径与清单逐项对应；在各自起点正向 `git apply --check --whitespace=error`、在正式树反向 `git apply --check --reverse` 均退出 0。DAA 起点至正式树的清单外差异只包括本任务交接、QA 记录及协调者维护的两对双语索引。任务源码增量未触及共享 UI、DS、后端、SMA 或发布配置。

### 验收对照

| 验收 | 本轮结果 | 证据 |
| --- | --- | --- |
| AC01 / R01–R02 | 失败，F-003、F-004 | 工作台依次为连接、采集、待上报、容量卡，随后是启动设置、上报和采集。配置页仍使用草稿保存、激活、版本详情及回滚，顶栏只移除指定两标签。双语 Vue 探针核对共用上报卡及实际两页组件。长地址按独立值列换行，原手动确认仍显示目标、合同及来源。QA1 的周期上报刷新失败路径已通过。折叠与保存上报设置后的快照读取分支仍失败。 |
| AC02 / R03 | 持久化和隔离路径通过 | 空白与旧兼容合成 profile，默认关、四种设置组合、关闭重开、保持 etag/草稿及本次运行、事务失败及坏记录停止自动化的检查通过。runtime2/3 保持仅本地能力。由 `run → local_recovery::open` 恢复后读取设置，切换、页面与刷新不执行启动。 |
| AC03 / R03–R04 | 失败，F-005。F-001 原路径已关闭 | 独立诊断走 `local_recovery::open` 与真实 `daa_set_collection` / `daa_set_connection` dispatch。第一次自动连接失败时等待暂停 applied，1.5 秒后第一台 `desiredConnection=false, connected=false, desiredCollection=false, savedCycles=0`、第二台 `savedCycles=4`。再次打开，手动启动在离线时以 `connection_required` 失败，之后自动恢复采集，连接后暂停保留连接。另验证显式手动连接后暂停保留该意图，现有测试也覆盖手动连接暂时失败时保留该意图。已有启动测试覆盖停用、单 PLC 失败及恢复、断开及重开。待容量准入时激活新端点仍会沿用旧的自动连接意图。 |
| AC04 / R05 | 通过所验证路径 | 启动路径使用旧兼容样本、合成逐 PLC 身份及内存传输，匹配回执才确认，采集关闭也能独立发合格待传；下次启动读取后来保存的参与和绑定。复验来源阻断和目标变化前已准备、`attempt=0` 的样本保持原目标、身份、冻结正文，无自动解除阻断或改绑。派发前复核、过期手动确认、暂停后在途回执、逐 PLC 参与隔离通过。 |
| AC05 | Rust 启动链、生产 feature 检查与前端构建通过 | 测试执行 Tauri 原生入口使用的 `local_recovery::open`，检查正式 Tauri 配置传 `rust-snap7-driver` 并独立编译。独立 Vue SSR/renderer 使用实际两页和 composable，外层 Element Plus 控件及调用边界由合成替身承接。未运行 Mac/Windows Tauri GUI。 |

### 新增失败与复查

**F-003（R01 / AC01）：折叠后的启动设置仍保留可聚焦问号。** 在中、英两种语言用实际 `StartupSettings.vue` 点击折叠。设置正文节点已移除，展开入口存在，但还能取得问号按钮。触发该按钮原有 `focus` handler，`aria-expanded` 变为 `true`，tooltip 从 `display:none` 变为可见。[组件 header](../../src/components/console/StartupSettings.vue#L7)的问号与说明没有受 `expanded` 控制，仅第 14 行正文受控。预期按规格折叠后只留标题和展开入口，不能通过鼠标或键盘打开该问号。展开后帮助仍需支持键盘焦点和悬停。

**F-004（R01–R02 / AC01）：保存上报目标后紧接的快照读取失败，两页仍显示旧上报数据。** 在真实前端 composable 与两个 Vue 页面中先成功读取上报中、旧目标 `http://fixture.invalid/old/report-target`、待上报 `732`、已确认 `943`、最近可靠确认 `2026-11-14 09:01:03`。打开上报设置，保存新目标 `http://fixture.invalid/new/report-target` 成功，让紧接的 `getDeliverySnapshot` 返回 `storage_busy`。生产 [Rust 保存路径](../../src-tauri/src/services/local_delivery.rs#L85)在改目标成功后会暂停上报，探针据此更新模拟事实。两页两语言都仍显示「上报中」、旧地址、计数和回执时间，没有上报不可用或过期标记。通用 `error=storage_busy`，`deliverySnapshotError=''`，因此 [保存分支](../../src/console/composables/useLocalAcquisitionConsole.ts#L71)的读取错误只由 `perform` 捕获，绕过 [周期刷新错误标记](../../src/console/composables/useLocalAcquisitionConsole.ts#L289) 与[上报卡遮蔽](../../src/components/console/FactsDeliveryPanel.vue#L86)。下一次成功读才纠正，即使只是一个刷新窗口，也会把已知失效的数据标成当前。预期该读取失败时两个页面马上标注上报不可用或过期，保留安全暂停，启动保持禁用直至成功刷新。

**F-005（R03–R04 / AC03）：旧启动任务会连接之后激活的新端点。** 同一合成 PLC 先从应用启动恢复链连接端点 `127.0.0.1:31001`。容量表注入低可用空间，确认 `connected=true`、`error=capacity_paused`，自动采集仍在等待。恢复测试容量后，在下一次启动探测前保存并激活同一 PLC ID、同一组、端口改为 `31003` 的新配置，全程无手动连接或采集。1.5 秒后 `desiredConnection=true, connected=true, desiredCollection=false, savedCycles=0`，日志记录新配置激活后恢复连接。两个端点均为内存传输，变更已使旧连接断开。[安装分支](../../src-tauri/src/services/local_supervisor.rs#L416)在旧端点仍连接时清除启动归属但保留连接意图，随后按端点变化断开旧连接，[重连分支](../../src-tauri/src/services/local_supervisor.rs#L781)因此连接新端点。预期此次旧启动任务不得连接之后激活的端点；显式人工连接意图沿用既有规则。

**F-002 原复现分支已通过。** 中英两种语言分别渲染实际工作台和上报与存储页面。采集快照从 `09:01:03` 成功更新到 `09:06:49`、上报返回 `storage_busy` 时，上报区显示不可用，没有旧状态、地址、计数、回执时间，也没有把采集时间标为上报刷新时间；尝试启动未调用上报控制，暂停仍可调用。上报成功读回停止态后，两页恢复当前计数、地址、回执及启动按钮。仅采集失败时单独标记采集错误，成功的上报状态仍可使用。F-004 单列保存后的另一条读取入口。

### 命令、环境与资源

macOS arm64 15.7.7（24G720），Rust/Cargo 1.89.0、Node 22.19.0、pnpm 11.11.0。Rust 只使用锁定依赖、现有 Cargo 缓存与 QA 专属 `TMPDIR`。未启动/重启用户服务，`lsof -nP -iTCP:15191 -sTCP:LISTEN` 无监听。未读取或操作现有 `.local/dev`、真实配置/样本、dev API、数据库或真实 PLC。无 Docker、MySQL、真实 HTTP listener 或设备连接。Vue 验证覆盖 DOM 结构与 renderer 事件，Mac 和 Windows 原生窗口的焦点、视觉布局及设备/后端验证分别待实测。

- DAA 正式树 `cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib startup_ -- --test-threads=1`，8/8、退出 0；同一命令分别过滤 `runtime2_and_3_keep_local_collection_and_refuse_v2_delivery`、`dispatch_rechecks_`、`qa_start_confirmation_must_not_dispatch_after_concurrent_settings_save`、`v2_worker_pause_save_preserves_inflight_receipt_and_stops_new_dispatch`、`plc_switch_rechecks_before_dispatch_without_stopping_other_sources`，共 6/6、退出 0。`cargo fmt --manifest-path src-tauri/Cargo.toml --all -- --check`、`cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --features rust-snap7-driver` 退出 0。测试构建保留既有 `empty_for_test` 未使用告警。
- 独立诊断仅写入隔离副本，沿用锁文件和 Cargo target。`cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib qa2_ -- --test-threads=1 --nocapture` 的 `qa2_exact_startup_manual_pause_repro` 通过；记录了真实 dispatch 的多个动作及两台 in-memory PLC 的状态。隔离 Rust 第一次缺少项目的本地 path 依赖，补入原样副本后正常编译。
- 隔离 UI 使用正式 DAA 与共享组件源、现有锁定依赖副本。`node --test tests/startup-settings.test.mjs tests/facts-delivery.test.mjs` 12/12、退出 0；`./node_modules/.bin/vue-tsc --noEmit`、`./node_modules/.bin/vite build --outDir <QA2>/daa-dist --emptyOutDir` 退出 0，Vite 保留第三方注释和 chunk 大小提示。`node <QA2>/ui-probe.cjs` 退出 1；两页/两语言的周期失败及恢复断言通过，折叠和保存后失败的实测如上。两语言 common locale 各 697 键结构相同，受触达双语文档及任务 spec/tasks 的 45 个相对链接文件目标存在；未检查全部锚点。任务范围 `git diff --check` 退出 0。
- 隔离 Rust 检查使用同一锁定 Cargo 命令仅过滤 `qa2_pending_startup_does_not_connect_changed_endpoint_on_activation`，退出 101。初版探针使用 128 MiB 配额提前阻止种子激活，改为重开后在测试容量表注入低可用空间，覆盖实际激活入口；结果详见 F-005。
- QA2 独立证据 `/private/tmp/daa015-qa2.TJ14Wm` 含合成 profile/夹具、隔离源码及依赖、诊断和构建日志。Development `/private/tmp/daa015-dev.DgUHuY` 内持有三份状态的快照证据及补丁，QA1 目录 `/private/tmp/daa015-qa.5cjZ1S` 保留历史复现。关键状态值与复现步骤已写在本文件。请协调者在无验证、返工或证据依赖后核对自有资源与占用并回收。正式 Rust `target` 为共享缓存。

当前 `qa_failed`。返工由 Development 执行，新的交接仍需 fresh-context Verification。Human Owner 最终验收 `pending`。

## 独立验证 QA3（2026-11-14，Asia/Shanghai）

本轮以命名 Verification 角色在 fresh context 核验，角色按 `contract_only` 执行。独立读取根与最近作用域规则、canonical workflow、[获批 r1 规格](spec.md)、[Development 交接](tasks.md)第 7 节及此前两轮记录，并检查正式源码和差异。使用 project-governance、aiis、desktop-tauri、rust-runtime、frontend-ui、i18n-workflow 和 code-document-indexer 对照相关表面。结论为 `qa_failed`，见 F-006。

### 候选一致性

正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `fd999224a8756feda314a33148304b4bf3461876`。批准 spec SHA-256 为 `f571dd51dbed26a3d59f70e78253dc6e47bb89a61453e8c3ed2a97773910340d`，返工 tasks SHA-256 为 `1db9756aea301886fdfb0c091a025eae9a99297e27c8536e61a7584c020d289e`。`/private/tmp/daa015-dev.DgUHuY` 中的清单、两份补丁逐项匹配交接。

| 文件 | SHA-256 | 核验 |
| --- | --- | --- |
| `daa015-qa3-manifest.json` | `0b7c9d22df85f4dafdddff5cf15b26063ed4fbda0dbec67819ccbcb897c22b90` | 34 路径的原始起点、QA2 快照及正式树摘要匹配 |
| `daa015-qa3-source.patch` | `d8166901f77a805ef79b16457006ab2551ca6243339eab12238321630321d9ee` | 34 路径，正向与反向检查通过 |
| `daa015-qa2-rework.patch` | `ddc7af4aa69e2379356d22d0a3cde6408ee084560d170e1400727d2384ff0510` | 6 路径，正向与反向检查通过 |

两份补丁分别在原始起点和 QA2 快照执行 `git apply --check --whitespace=error`，在正式树执行 `git apply --check --reverse`，均退出 0。DAA 起点到正式树的清单外差异为交接、QA 文件和协调者维护的双语 PLAN 与目录。核对任务增量位于 DAA 和相关代码索引，未触及共享 Console UI、DS、SMA、后端或发布配置。

### 验收对照

| 验收 | QA3 结果 | 独立证据 |
| --- | --- | --- |
| AC01 / R01–R02 | 已核验分支通过。F-002、F-003、F-004 原复现通过 | 正式 Vue 工作台和上报与存储分别用中英文渲染。折叠只呈现标题和展开入口，问号与说明移除，重开时帮助状态复位，鼠标悬停和键盘焦点仍可打开。仅上报周期读取失败及保存新地址后读取失败均显示上报不可用，隐藏旧地址、运行状态、计数及确认时间，禁用启动并保留安全暂停，确认刷新后恢复。组件测试覆盖保存结果待确认、启停和改绑命令返回错误、迟到的旧状态与旧错误及恢复。工作台四卡顺序、启动设置与运行区、顶栏两项清理、配置中心草稿入口及手动上报确认经源码和相关组件回归核对。长地址与确认时间使用独立行，原生像素布局未测。 |
| AC02 / R03 | 合成持久化和开关隔离通过 | 通过实际原生启动调用的 `local_recovery::open`，复验默认停态、四种开关组合、独立保存及关闭重开。旧兼容合成 profile 保留已有草稿、激活版本及样本，不改 DDL。写入回滚和读取坏记录保持安全状态，runtime2/3 保留本地采集、拒绝新版上报。 |
| AC03 / R03–R04 | 失败，F-006 | 逐 PLC 连接、故障恢复、另一台先采集、断开和重开通过。F-001 离线暂停通过，人工连接意图与连接后暂停也通过。F-005 原场景及单次端点变化、显式人工连接、同端点现连、禁用后重启用的四分支均通过。先激活同端点、再激活新端点的两步路径仍由旧启动连接自动连上新端点。 |
| AC04 / R05 | 合成执行与回执通过 | 复验仅自动上报、逐 PLC 参与及绑定、同一 profile 保存新参与来源后下次启动、匹配回执才确认。来源已阻断及旧目标的 `prepared/attempt=0` 样本原目标、身份和冻结正文保留。派发前重新核对、并发确认和安全暂停保留在途回执通过。 |
| AC05 | 启动链、编译与前端构建通过 | Rust 用正常启动共用的 `local_recovery::open` 在隔离 profile 上运行，生产 `rust-snap7-driver` feature 编译并核对正式 Tauri 配置。Vue SSR 和 renderer 使用实际页面/组件与合成调用，Mac 和 Windows 原生窗口尚未验证。 |

### F-006（R03–R04 / AC03）

**先激活同端点配置，再换端点，仍会因旧启动连接意图连接新的 PLC 端点。**

1. 用合成 profile 保存两个启用的 PLC 及完整组，仅开启下次自动采集，经实际 `local_recovery::open` 重开。给第一台的一次连接注入受控失败，待容量表注入低可用空间后重连到 `127.0.0.1:31001`。确认该 PLC 已连接且状态为 `capacity_paused`，尚未开始采集。
2. 恢复合成容量，随后仅修改该 PLC 名称并通过真实保存、激活入口安装相同端点。现有连接保留，`desiredCollection=false, savedCycles=0`。
3. 将同一 PLC 的端口改为 `31003`，再次保存及激活。全程未手工请求连接或开启采集，应用未重开。第二次 `configuration_activated: applied`（14:20:01.079）后紧接同一 PLC 的 `connection_restored`（14:20:01.080）；1.5 秒后 `desiredConnection=true, connected=true, desiredCollection=false, savedCycles=0`。

预期同端点激活保留当前物理连接并取消尚未开始的自动采集。之后变化到一个新端点时，保留现连这一行为不应产生手动连接意图，故旧启动连接不得打开新端点。显式人工连接继续按既有规则。第一次同端点安装保留了 `desired_connection`，却同时清除了 `startup_connection_owned`；第二次安装主动断开旧端点后，重连分支继续消费该连接意图。[安装分支](../../src-tauri/src/services/local_supervisor.rs#L416) · [重连分支](../../src-tauri/src/services/local_supervisor.rs#L787)

### 命令、环境及资源

macOS arm64 15.7.7（24G720），Rust/Cargo 1.89.0，Node 22.19.0，pnpm 11.11.0。无现有 `.local/dev`、dev API 或数据库、真实 PLC、真实样本、Docker/MySQL 写入或读取。未启动或重启用户服务，15191 只读监听查询无匹配。真实设备、后端、Mac 和 Windows 原生 GUI、阶段 C 和发布部署均未实测。

- 正式 DAA 树以 `TMPDIR=/private/tmp/daa015-qa3.MVejAl/daa-008-r2-a-fixtures` 运行 `cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib <过滤器> -- --test-threads=1`。过滤器 `startup_` 9/9，`runtime2_and_3_keep_local_collection_and_refuse_v2_delivery` 1/1，`dispatch_rechecks_` 2/2，`qa_start_confirmation_must_not_dispatch_after_concurrent_settings_save`、`v2_worker_pause_save_preserves_inflight_receipt_and_stops_new_dispatch`、`plc_switch_rechecks_before_dispatch_without_stopping_other_sources` 各 1/1，均退出 0。测试构建保留原有 `empty_for_test` 告警。
- `cargo fmt --manifest-path src-tauri/Cargo.toml --all -- --check` 和 `cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --features rust-snap7-driver` 均退出 0。
- `node --test tests/*.test.mjs` 39/39，`./node_modules/.bin/vue-tsc --noEmit`、`./node_modules/.bin/vite build --outDir /private/tmp/daa015-qa3.MVejAl/daa-dist --emptyOutDir` 均退出 0。Vite 保留第三方标注和 chunk 大小提示。QA2 独立 UI 探针复制后在正式 DAA 目录运行 `node /private/tmp/daa015-qa3.MVejAl/ui-probe.cjs` 退出 0，复验两个真实 Vue 页面 × 两种语言。双语 common locale 697 个键相同，62 个触达文档及任务记录的本地文件链接目标存在，未检查全部锚点。触达范围 `git diff --check` 通过。
- F-006 在隔离源码中运行上述 Cargo 测试命令，manifest 指向 `/private/tmp/daa015-qa3.MVejAl/isolated/automation-world/data-acquisition-agent/src-tauri/Cargo.toml`，过滤 `qa3_same_endpoint_then_replacement_is_not_automatic` 并加 `--nocapture`，退出 101。隔离副本首次因缺编译时载入的 PLC facts v1 公开测试向量未编译，补入原样文件后运行至断言失败。诊断只在隔离副本追加测试，生产源码及仓库测试无本轮编辑。
- `/private/tmp/daa015-qa3.MVejAl` 含隔离源码和诊断用例、测试日志、Vite 产物、专属合成 profile。Development 的 `/private/tmp/daa015-dev.DgUHuY` 和历史独立 QA 的 `/private/tmp/daa015-qa.5cjZ1S`、`/private/tmp/daa015-qa2.TJ14Wm` 继续保留用于本次返工及核对，正式 Rust target 是共用构建缓存。由协调者在确认无证据、进程或后续返工依赖后回收任务专属资源。

当前结论 `qa_failed`，F-006 交回 Development。在本 Revision 重新交接并完成独立核验后，交 Human Owner 最终验收。当前最终验收 `pending`。


## 独立验证 QA4（2026-11-14，Asia/Shanghai）

以命名 Verification 角色与 fresh context 消费 [获批 r1](spec.md)、[Development 交接第 8 节](tasks.md#8-qa3-返工及新的-developer_handoff) 和以上 QA1–QA3 原始证据。依根及最近作用域规则、canonical workflow、project-governance 与 rust-runtime 核验，前端复验对照 frontend-ui 与 i18n-workflow。角色按 `contract_only` 执行。

### 精确候选

- 正式工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，本轮 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，交接记载的 HEAD `fd999224a8756feda314a33148304b4bf3461876` 是较早时点。以正式树文件内容和起点补丁固定候选。获批 spec SHA-256 `f571dd51dbed26a3d59f70e78253dc6e47bb89a61453e8c3ed2a97773910340d`，交接 tasks SHA-256 `5538f899ac5c28e84067f7f902a4cc42c099303a3ff488255f3cc87c2f617bb3`。
- `/private/tmp/daa015-dev.DgUHuY/daa015-qa4-manifest.json` SHA-256 `52001c772e90de2c010807b3cd81e564a6ef221e69b5def9200fc9f194650648`。Python SHA-256 比较原始起点、QA3 快照与正式候选各 34 项全部匹配，QA3 列与原 QA3 清单候选列全等。起点补丁 `daa015-qa4-source.patch` SHA-256 `cef29a63dbdacd12b3c2c236d5b197dfe26d93f65340caf4e1e0493d076c1063`，34 个改动路径与清单相同。返工补丁 `daa015-qa3-rework.patch` SHA-256 `e38f303fec5b6561e580252497798c14f538af213d01562ecb191629841ebddf`，仅 `local_supervisor.rs` 和 `local_store/tests.rs`。两份补丁分别在各自起点正向 `git apply --check --whitespace=error`、在正式树反向 `git apply --check --reverse` 均退出 0。两处 Rust/test 文件与获批范围相符。并行的 DAA-016 草稿及索引变更在工作树可见，独立于本次候选。

### 验收证据

| 验收 | QA4 结果 |
| --- | --- |
| AC01 / R01–R02 | 通过。工作台、启动设置、两页共用的上报卡、快照处理、中英文及对应 QA1/QA2 测试与 QA3 证据中的候选逐字节相同。12 项定向 Node 测试复验折叠、键盘和悬停帮助，以及快照失败/恢复、按钮和回执呈现。两页双语 renderer、前端类型检查与构建采用 QA3 已通过的同版本 UI 证据。 |
| AC02 / R03 | 通过。通过实际 `local_recovery::open` 复验四种开关组合、旧合成 profile 持久化、读写失败及 runtime2/3 本地能力。独立 IPC 探针对已有采集关闭自动采集开关，当次仍继续采集，关闭再打开才保持停态。原保存的开启设置在重开时以新活动配置运行，当次人工暂停未改写该设置。 |
| AC03 / R03–R04 | 通过，F-006 关闭，F-001、F-005 定向复验通过。实际恢复、PLC actor、草稿保存及两次激活均运行于隔离源码，用两台内存 PLC 覆盖容量等待、已经采集、已连接后暂停、显式人工连接、停用再启用。原始 F-006 复现与 IPC 探针结果见下。 |
| AC04 / R05 | 通过。`startup_` 中复验旧合成样本的逐源绑定、参与开关、匹配回执与下次启动吸收新绑定。原有阻断与 `prepared/attempt=0` 冻结目标和正文保持。定向复验派发前当前目标及身份检查，以及暂停后在途回执仍保存、无新派发。 |
| AC05 | 通过规格内源码及合成启动验证。复核正常 Tauri 启动 `run → local_recovery::open` 与 `tauri.conf.json` 传递 `rust-snap7-driver`。Rust 格式和生产 feature 检查通过。原生窗口及现场边界见下。 |

### F-006 关闭证据

先按 QA3 原始独立用例重跑。合成 PLC 从启动恢复后连接 `127.0.0.1:31001`，容量不足时等待自动采集。恢复容量并以同端点激活名称变更，当前连接保留且采集未启动。第二次激活将端口改为夹具端点 `127.0.0.1:31003`。1.5 秒后 `desiredConnection=false, connected=false, desiredCollection=false, savedCycles=0`，退出 0。QA3 原复现的前两项为 `true`。

独立 IPC 探针通过实际 `daa_save_draft`、`daa_activate_configuration`、`daa_set_collection`、`daa_set_connection`、`daa_save_startup_settings` 的 Rust dispatch 复验。首台合成 PLC 首次连接失败时，另一台先采集。每组第二次激活后观察 1.43 秒，另一台各多保存 3 轮：

| 首台场景 | 更新后连接意图 / 已连接 / 采集意图 | 新增采样轮 |
| --- | --- | --- |
| 容量等待，经同端点激活后更换端点 | `false / false / false` | 0 |
| 已连接后手动暂停，经同端点激活后更换端点 | `false / false / false` | 0 |
| 已自动采集，经同端点激活后更换端点 | `false / false / false` | 0 |
| 已自动采集并明确手动连接，经同端点激活后更换端点 | `true / true / false` | 0 |
| 同端点激活后停用，再次激活启用 | `false / false / false` | 0 |

先前的人工暂停在执行时保留原现连。重开后原保存的自动采集开关对新活动版本生效，保存采样后运行状态的 `used_revision` 命中新版本。再保存关闭时仍继续当前采集，下次重开进入停态。[配置安装分支](../../src-tauri/src/services/local_supervisor.rs#L416)在同端点保留连接来源，更换端点或禁用时撤销归属于启动的连接，并停止其自动采集意图。[人工动作分支](../../src-tauri/src/services/local_supervisor.rs#L596)保留独立人工连接意图。现有能力和已验证的手动启停路径可继续使用。

### 命令、环境与资源

macOS arm64 15.7.7（24G720），Rust/Cargo 1.89.0，Node 22.19.0，pnpm 11.11.0。Rust 执行于 `/private/tmp/daa015-qa4.huYPyb/isolated/automation-world/data-acquisition-agent`，源码来自正式树，`TMPDIR` 为 QA4 子目录 `daa-008-r2-a-fixtures`，`CARGO_TARGET_DIR` 为 QA4 专属 `target` 副本。编译产物、日志、诊断与合成 profile 均在该任务临时根下。Rust 运行及生产 feature 编译使用隔离副本，正式 DAA 目录只执行 Node 定向组件测试。没有启动或重启用户服务，没有读取或操作现有 `.local/dev`、dev API/数据库、真实 PLC 或真实样本。没有启动原生窗口、Docker、MySQL 或真实 HTTP 服务。

- `cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib <过滤器> -- --test-threads=1`，`startup_` 10/10（含六场景的 Development 回归）、`runtime2_and_3_keep_local_collection_and_refuse_v2_delivery` 1/1、`dispatch_rechecks_` 2/2、`v2_worker_pause_save_preserves_inflight_receipt_and_stops_new_dispatch` 1/1。均退出 0，测试编译保留既有 `empty_for_test` 告警。
- 同一命令增加 `--nocapture`，分别选择 `qa3_same_endpoint_then_replacement_is_not_automatic` 与 `qa4_startup_origin_through_ipc_and_restart`，各 1/1、退出 0。诊断仅加在隔离测试副本。后者首次用零可用空间尝试激活，按现有容量准入返回 `capacity_paused`，退出 101。调整探针在确认启动处于等待后先恢复合成容量，再走激活，覆盖预期路径。
- `cargo fmt --manifest-path src-tauri/Cargo.toml --all -- --check` 与 `cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --features rust-snap7-driver` 均退出 0。正式 DAA 目录 `node --test tests/startup-settings.test.mjs tests/facts-delivery.test.mjs` 12/12，退出 0。`git diff --check` 与本节本地 Markdown 链接文件目标检查均通过。
- QA4 自有 `/private/tmp/daa015-qa4.huYPyb` 含隔离源码、两次探针的日志、合成 profile、Cargo 缓存副本与前后审计记录。以上结果和关键状态已持久记录。由协调者在归属、证据及占用条件核准后回收本任务专属资源。旧 Development 和 QA1–QA3 资源及正式树 Cargo 缓存均由现有记录跟踪。QA4 无常驻进程、分支或工作树。

**Verdict** `qa_passed`。F-006 关闭，QA1–QA3 结果保留。源码与合成验证结果交 Human Owner，最终验收 `pending`。Mac 与 Windows 原生 GUI、真实设备和后端、阶段 C 与发布部署仍无本轮验收证据。

**资源收尾记录** 协调者确认归属及无打开句柄后，回收了可重建的 QA4 隔离编译缓存 `/private/tmp/daa015-qa4.huYPyb/target`。QA 只读复核确认该路径已不存在，隔离源码、合成 profile、测试与探针日志及前后审计记录仍在原任务目录。

### Human Owner 会话自述的手测反馈

Human Owner 在会话中确认启动设置的两处 DIRECT 界面修正均正常，标题与下方卡片一致，问号提示完整显示。随后反馈「我测了，可以启动软件后自动上报和采集」。该反馈未提供具体 profile、后端、样本数量、回执或各开关独立组合的测试结果。以上按 Human Owner 手测自述记录。独立 QA4 结论仍为 `qa_passed`，Human Owner 最终验收仍为 `pending`。

## Human Owner 最终验收（DAA-015 r1）

Human Owner 于 2026-11-14（Asia/Shanghai）在当前会话明确验收 DAA-015 r1。登记时间为 `2026-11-14T15:41:19+08:00`。验收原文如下。

> 验收 DAA-015 r1，等 DAA-016 完成后同步中英文手册的按钮名称，并清理本轮临时测试资料。

最终状态为 `owner_accepted`。QA4 的源码和合成验证对应后续 DIRECT 界面小修之前的精确候选。DIRECT 小修随后完成构建和组件测试，Human Owner 目视确认启动设置标题与下方卡片一致、问号完整显示提示，并自述软件启动后可自动采集、自动上报。会话反馈未给出具体 profile、后端目标、样本数量、回执或开关组合。Windows 原生验证仍待实测。

中英文手册的按钮名称由协调者在 DAA-016 完成后另行同步。本轮临时测试资料的清理由协调者另行处理，并以实际清理记录为准。

### 验收后资源收尾

协调者按 Human Owner 要求回收了 DAA-015 专属的五个临时测试目录。QA 只读复核确认 `/private/tmp/daa015-dev.DgUHuY`、`/private/tmp/daa015-qa.5cjZ1S`、`/private/tmp/daa015-qa2.TJ14Wm`、`/private/tmp/daa015-qa3.MVejAl`、`/private/tmp/daa015-qa4.huYPyb` 均已不存在。QA4 历史候选的[清单](evidence/daa015-qa4-manifest.json)和[源码补丁](evidence/daa015-qa4-source.patch)已归档，两份 SHA-256 均与原 QA4 记录一致。本次仅追加资源收尾事实，原 QA 记录与 `owner_accepted` 结论均予保留。

### 验收后手册按钮文案的独立核验

2026-11-14（Asia/Shanghai）。命名 Verification 在 fresh context 核验 Human Owner 验收 DAA-015 r1 后指定的双语手册文案更正。正式工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`。环境为 macOS arm64 15.7.7（24G720）、Git 2.50.1、Python 3.9.6、ripgrep 15.2.0。核验依据为 [r1 规格 R02](spec.md#2-需求)、[Development 同步及自检](tasks.md#10-验收后手册按钮文案同步)、[DAA-016 r1 QA2](../DAA-016-docs-closeout/checklist.md#daa-016-r1-独立文档复验--qa2)及当前源码。角色按 `contract_only` 执行。

| 核查项 | 独立结果 |
| --- | --- |
| 按钮与手册 | 工作台和上报与存储页面共用 `FactsDeliveryPanel.vue`，其启动按钮经 `ConsoleActionButton.vue` 翻译 `common.delivery.startOrResume`。`src/locales/index.ts` 在两种语言的 `common` 下加载对应 `common.json`。手册各在第 70 行使用「启动上报」和 **Start reporting**，旧称均无命中。 [按钮源码](../../src/components/console/FactsDeliveryPanel.vue#L8) · [中文手册](../../USER_GUIDE.zh-CN.md#L70) · [英文手册](../../USER_GUIDE.md#L70) |
| 两份手册差异与导航 | 与同步前基线逐字节比较，各只替换一处按钮名称。18 个 Markdown 链接逐项保留并确认目标可达，包括两份 README 启动标题及英文手册第 3 行的 [英文采集指南](../../../../docs/acquisition-data-guide.md)。 |
| 任务记录与归档 | `tasks.md` 的本轮增量仅为末尾 §10，之前的 §1–8 复算与原 QA4 交接摘要一致。两份 QA4 归档件摘要仍与原记录一致，五个专属临时路径再次确认不存在。 |

同步前摘要来自 Development 交接。英文手册以 `git show HEAD:<路径>` 的原文应用 DAA-016 导航更改重建，且摘要与 DAA-016 已核验交接清单匹配；中文手册同步前字节等于 HEAD 原文。用 `python3 -B -` 独立解析 locale JSON、按正反方向比对两处替换、检查链接，并截取 `tasks.md` §10 之前的原字节复算 SHA-256。首次截取误计标题前的空行，校正分界后所有断言退出 0。查阅 Development 自检，再重跑 `git --no-optional-locks diff --check HEAD -- <两份手册、DAA-015 tasks.md 与 checklist.md>`，退出 0。

| 文件 | 同步前 SHA-256 | 同步后 SHA-256 |
| --- | --- | --- |
| `USER_GUIDE.zh-CN.md` | `4a66349f1936998485616e4389e0049d9b54f068de1851e4329041fca2cd4e94` | `ec4cd783a546486c68be598770c9ba99391d6cb90682be3c2ebd5af85a63210b` |
| `USER_GUIDE.md` | `92861b37c492e7eb57eebb5b23aafa4ac6dbe654df1fca9c1175ca303ed5d5eb` | `1aa85cf01edfee3cbd43d7ce70df4e27f0476bb537fe80b77c5b21ea97574d09` |
| `tasks.md` | `ecbf75ea315c159bdc29e185326e45ddb50b058bb18288e853fc6959d118d407` | `6977d70bb3abe39dab1c54683c4afc2df66f4fb35e9b9bc58574053476025262` |

**结论** 验收后双语手册按钮文案更正独立静态核验通过，交 Human Owner 知悉。DAA-015 r1 `owner_accepted` 及 QA4 历史候选各按原记录。DAA-016 r1 文档实施通过 QA2，待 Human Owner 最终验收。本轮范围限文案、链接、源码翻译映射和差异核对，应用、数据库及设备均未测试。
