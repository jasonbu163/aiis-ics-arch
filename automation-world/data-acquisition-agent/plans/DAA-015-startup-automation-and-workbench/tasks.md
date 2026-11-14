Task ID: DAA-015
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: QA2 的 F-003/F-004/F-005 已按 r1 返工；以第 7 节新候选与自检交 fresh-context Verification 重新核验

# DAA-015 r1 Development 交接

第 1–5 节保留 QA1 之前的候选和自检历史，第 6 节保留 QA2 之前的返工交接；当前有效的 Development 返工交接与文件摘要见第 7 节。QA1、QA2 已记录 qa_failed，新的独立验证和 Human Owner 最终验收待进行。

## 1. 范围与起点

Human Owner 已按 [spec.md](spec.md) 批准 r1；批准后的 spec SHA-256 为 f571dd51dbed26a3d59f70e78253dc6e47bb89a61453e8c3ed2a97773910340d。正式工作树 /Users/jason/Desktop/DreamCode/aiis-ics-arch 的 HEAD 为 fd999224a8756feda314a33148304b4bf3461876，大量已有未提交改动不是本任务增量，不将 HEAD diff 当作本任务 diff。起始时正式 DAA Vite 在运行；协调者确认 Owner 已停止且 15191 无监听后，Development 才修改正式源码。

实施前将 DAA 源码、文档、夹具复制到 /private/tmp/daa015-dev.DgUHuY/automation-world/data-acquisition-agent，排除 .local、.env*、node_modules、target、dist 和日志；同根 CODE_INDEX.md 是起始版本。这里是带既有脏更改的真实起点，不是 HEAD。正式树增量与该起点逐文件比较产生 /private/tmp/daa015-dev.DgUHuY/daa015-source.patch，SHA-256 df31164ef9844aac8698bc282686c9844c1e827281d31cf38859c71d41d2168d；机器清单 daa015-manifest.json SHA-256 d54f7f06e430f982040fe51eaab57d515bdea82ae5d27e52b31f640aeeda6546。二者与起点快照暂留给 QA；下表也持久记录前后文件摘要。(new) 表示起点不存在。既有工作树和本任务增量均未提交。

## 2. 实施摘要

- 工作台四张运行卡前置，保留错误、未激活、未保存与过期快照提示；配置草稿仍在配置页面。启动设置可折叠，一个问号支持悬停和键盘焦点。顶栏只从 DAA 去掉两个固定标识。共用上报卡按钮改名、地址与最近确认分行，中英文同步。
- 启动偏好使用现有 config SQLite 的受保护私有记录，不改变 DDL、配置草稿或活动版本；缺失默认均关，读错时自动启动关闭。写入事务失败保留旧值；未知写入结果时 UI 禁用开关并要求重新读取。保留配置清理与历史 YAML 只读判空语义；runtime2/3 不获得新版上报能力。
- local_recovery::open 仅对原生启动调用一次自动化。已启用 PLC 由现有 actor 独立连接和有界重试；手动暂停或断开取消本轮自动采集意图。上报复用单样本 worker、参与开关、目标及匹配回执；自动启动不执行手动来源确认的解除阻断或旧目标改写，并对需人工核对的旧目标/阻断显示原因。
- 更新双语 README、用户手册、本地存储说明和代码索引。现有 .local/dev、dev API/数据库、真实数据和真实 PLC 均未读取、启动、修改或连接；无 Docker、MySQL 或系统级自启动。

## 3. Development 自检（非独立 QA）

| 检查 | 实际结果 |
| --- | --- |
| TMPDIR=/private/tmp/daa015-dev.DgUHuY/daa-008-r2-a-fixtures cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib startup_ -- --test-threads=1 | exit 0，7 passed。四组合通过 local_recovery::open 入口；两台 PLC 为内存 transport，分别覆盖暂时连接失败后恢复、手动暂停/断开、下一次启动；自动上报真实启动链使用按 profile 注入的内存 HTTP 回执，覆盖新增绑定、逐份提交与匹配回执。另核对旧目标 prepared/attempt=0、来源阻断不被改写。不是原生 GUI 或真实 PLC/后端证据。 |
| TMPDIR=/private/tmp/daa015-dev.DgUHuY/daa-008-r2-a-fixtures cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib source_import_tests -- --test-threads=1 | exit 0，4 passed；第一次在另一自有目录运行 3/4，旧夹具因要求目录名包含 daa-008-r2-a- 拒绝，按该约定在本任务子目录重跑通过。 |
| TMPDIR=/private/tmp/daa015-dev.DgUHuY/daa-008-r2-a-fixtures cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib runtime2_and_3_keep_local_collection_and_refuse_v2_delivery -- --test-threads=1 | exit 0，1 passed；runtime2/3 可保存自动采集偏好、保持上报拒绝。 |
| cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --features rust-snap7-driver | exit 0；生产 S7 feature 编译，无告警；未运行驱动连接。 |
| cargo fmt --manifest-path src-tauri/Cargo.toml --all -- --check | exit 0。 |
| node --test tests/startup-settings.test.mjs tests/facts-delivery.test.mjs tests/point-editing.test.mjs tests/sample-details.test.mjs tests/time-and-history-preferences.test.mjs | exit 0，38 passed。新增组件测试在 Vue 渲染器中验证中英文、两个独立开关、失败和待确认写入、鼠标/键盘帮助、折叠、两个上报页面及长地址/时间顺序；不冒称原生窗口截图。 |
| pnpm build --outDir /private/tmp/daa015-dev.DgUHuY/daa-dist | exit 0。TypeScript 和 Vite 构建通过；第三方 VueUse PURE 注释、chunk 较大和输出目录未清空提示仍存在。初次构建发现两处可空类型错误，修正后通过。 |
| 双语 locale 键结构比较 | exit 0，695 个键成对。 |
| 本任务双语 README、手册与本地存储说明的相对文件链接 | exit 0，38/38 目标存在（未验证锚点）。 |
| git diff --check（触达的已跟踪源码、README 与索引） | exit 0；新文件另经格式化/构建。 |

一次 startup_ 测试重跑为 6/7：新测试错误地以 UUID 排序作为 PLC 配置顺序而随机超时。已改为按本地 PLC ID 明确对应，单测及最终 7/7 重跑通过。Rust 测试构建保留一个既有 empty_for_test 未使用告警；生产 S7 feature cargo check 无告警。一次独立 127.0.0.1:0 合成 listener 探测被沙箱以 Operation not permitted 拒绝；采用内存 transport，未运行真实 HTTP listener。未做系统原生窗口、Windows 原生、真实设备或生产部署验证，不能把本自检记作独立 QA 或最终验收。DAA-010 r5 已有首次目录竞态不在本任务内。

## 4. 文件摘要

表中路径相对仓库根，SHA-256 为起始快照 / 当前交接候选；新文件起点记为 (new)。完整机器清单与可复核增量路径见第 1 节。

| 文件 | 起始 SHA-256 | 候选 SHA-256 |
| --- | --- | --- |

| automation-world/data-acquisition-agent/README.md | d7d28953c3015a3668e14ad3f8612f7da0d922bcb9e9000e226af14fbbc883bf | e34b67b5aae4a0e06012c20ee1908ba2c157b2380520f5a3dcf97f535587398b |
| automation-world/data-acquisition-agent/README.zh-CN.md | 1c34165c2867c489c99b8551b404006f5fd3b01cb28520cb9797209d766b3842 | dd40f061608f80907c647fd48d59fd615fc22c8eb8004aed231e06c85531b749 |
| automation-world/data-acquisition-agent/USER_GUIDE.md | 7ffc201d39ab919a180ff03bcef0b8c4a944a4cd4599319836af57c6e7ee8e50 | 019b73d40ef8e881ec03544891b6cf59652d4e37ec1ba1ba49a97213c4c37b29 |
| automation-world/data-acquisition-agent/USER_GUIDE.zh-CN.md | 3c337d6984d31068bab4b658bddcf24049ad125ac20156a5dc8bd72c39492557 | 4a66349f1936998485616e4389e0049d9b54f068de1851e4329041fca2cd4e94 |
| automation-world/data-acquisition-agent/src/App.vue | 4284d71a05828f6f24c275404250eb3233a7636b9b04a49cc53648235c54fba8 | 0420ca46124c9380d93631780dcf50cafe314cf3733ed06cf21b84188ff283fe |
| automation-world/data-acquisition-agent/src/app/runtime/views/overview/index.vue | 546fddd8ca20a257a06dccc24b786901a49f16f5b2ec370cc618c11d308adaf4 | 71c517f7323fe4ff88c3b447aa80ee3d4798bb8a8ff64b2e2a2926abd76556d4 |
| automation-world/data-acquisition-agent/src/components/console/StartupSettings.vue | (new) | d3e67d8a77cb6bd30d97907d0e4baa78f3cc0dd196310638f1f36153a6d38df5 |
| automation-world/data-acquisition-agent/src/components/shell/AgentTopbar.vue | 589bd51b6588594548d7c216d3b686e087d4dadb29cc582fca0106980a4b77f9 | 6f64c0865c9d2fd635d556a272407d1a534fc1776fdbaf5cdc56ad2226cfb0ea |
| automation-world/data-acquisition-agent/src/console/composables/useLocalAcquisitionConsole.ts | a2e0c762a725596be65d120338ba5d976d2d417c54f6954648b9897844ad6f5a | 14c2bcdfb13823532e99ae5baf41eae7d4fd9676ad31a89933e990e9d11af8dd |
| automation-world/data-acquisition-agent/src/layouts/AgentLayout.vue | b8c95fb0a31b78edebc030144a1e028d5bf98e627c57621e1829809245780a94 | c0fa289a74ab8e06d3d0bd7a249565502e28f5157d3ce5aac4fddfcf27523bcd |
| automation-world/data-acquisition-agent/src/locales/en-US/common.json | 3bb918a23d1b0e17c6924e69c9f319c9c39f0d73e5fdc581f19f6cbc3bd11ba8 | 311269010e5c1594107bc1a4c2361a165c692f44dd6de8578dd1fe291593f990 |
| automation-world/data-acquisition-agent/src/locales/zh-CN/common.json | 9f6ecd67e922e14f3816b3a1e5add2cc778f1eca03e72dedff23172a4aa7081d | 1fa3f0c9d945f4d2cbfe4409f47e5556546efe168d95da3d6ba66461f8e9b05e |
| automation-world/data-acquisition-agent/src/services/localAcquisition.ts | 4cb5601d49996781b6d40e120bf84b47a2e93ecb3a45adc0cfc2e527658b48e6 | 30d015d373cdcd948a76a19f0c00a9c80396d7cc77c532dae66a665538b8b80f |
| automation-world/data-acquisition-agent/src/styles/app.css | 4df7abab0ae203b73356c511ff72b84fd34119f1f606081df1523be2f574efa4 | 0d04ee296c5a5c60944f0bf443a9aa8577c9404ab5b09384869c988fd7204f05 |
| automation-world/data-acquisition-agent/src-tauri/src/commands/local_acquisition.rs | f7c5a73282d2d462897f76f5861ed11a6a0952c7c0ac62cf5978e70f74f589f5 | 8c4abcb2e2e34534bedc0ef360bf8ef77154f643afaee844b37cb4c62d8427ba |
| automation-world/data-acquisition-agent/src-tauri/src/domain/local_runtime.rs | f123494df4c39385792c8072a6c7d28dace8de16e135611496e80cd143b00a1e | 0c5d1738b9298994247f5623f8b46d8e75a323b84db48a5535053a5a83792794 |
| automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.md | f81769b26dcb01fabad30975857e013e1c373ba577ae41d5302aa51fb7340db0 | d8c2b558eaf19204821130c0220d447f94ba38a94c7eade96913d362c6e6aa3e |
| automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md | 27b3f5ab724e6e483db18a94835988588bf1dc138f605ee4d968bb08019f740a | dbd3b5fc6d768f42f42258b926c8f42cd0a270e5f3a11591f1096a617e2bd773 |
| automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/configuration.rs | f84d3d0ad2eb630b0f421b09e2ed4d31ad81dcac4099236d421dc685a1d4278f | 16c429d7f83977bc39526033add30761c79bd361f4d56e05f470c0c8fd8c4ad0 |
| automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload.rs | 82089068688aac068bc70cede713febe7bae395c98b15a875cfe9b53106de637 | 6c1c694b4d202f1488a53801b71ef80eef828c39938d4b66302bf1c26d525676 |
| automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload_tests.rs | 05eb87bbe5896d7a59e182f86e8abe084988bc5cc6dde8328a07696956d87011 | 3cc18026f599c1092060cce4fff9b5adf9b97a4be9f8057f6c674cd53cc1975e |
| automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/tests.rs | 3c7dd4a7c8246996536b568fb5fe7a5b449a4db9ed4d8bdb89a9d38778d5e669 | fd4e24eb3632a173ffa584fe798c5c0b50e552449e89082dd12badc9d2295fec |
| automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/yaml_migration.rs | 200a6dbeb5c58f56cb3d2c39cc06af3d5194047a54069b3114e9d680733a5602 | 29802a5ebb8490d41c760b6cd12799b0c7321331ed22fdea593d404c0ce084c7 |
| automation-world/data-acquisition-agent/src-tauri/src/lib.rs | 9266b4790eb4c57864cb4d260f394abfafbcb71891d5cd0b7dcd88dea55c36f0 | e7dbd646c1b1ec9a8380e47a5f1333a6c706b6d351441fa421f55aa944a36b40 |
| automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery.rs | b5bb2866cba2bab5e69b330bf3ef9b6fb4b9a7a1416987990aca0cba18e47204 | aefb46690bd46530181dc4a3acaec4411d09b3eb7f5de878d16f4714f314b548 |
| automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery_tests.rs | da1af96460cd6d10cc94eb3ea02592a388f031d6e986bbf1ed9191fc3769bdda | 6489851bad47232b04466fe77af6222660b660941b40b6f304424e3b6f1be882 |
| automation-world/data-acquisition-agent/src-tauri/src/services/local_recovery.rs | c71ac344d11490d2c08d6fd09ca309da4e1dca55d0be16bc0227c659f84955c0 | f987e7c7ac0f528faf4266df61f9cd8332d4344787bea651e0f21bd537a69e39 |
| automation-world/data-acquisition-agent/src-tauri/src/services/local_startup.rs | (new) | 7e2c5b2e7606c71ad03b9cdf9b13596b3d779d3106e1b048cc57a8f8a3014ca0 |
| automation-world/data-acquisition-agent/src-tauri/src/services/local_supervisor.rs | 5ffb46755fe480d3cff2f2c8141536c927972fc194f8eebcc8f9342002a1bf25 | af9b4fd0f36cb5e0c70b46c5297742388f0a13b6c7deaa3a8e46114695c9c704 |
| automation-world/data-acquisition-agent/src-tauri/src/services/mod.rs | 040898a98d7188f71f83b4b6dbc4ccb37e967f396177fee4ba7a471233363444 | 7ab931d3c10a1a86ff4b468f7a69a93b5007e7277cc8b5c151b2dc4f892b0260 |
| automation-world/data-acquisition-agent/tests/startup-settings.test.mjs | (new) | 1315260dbda9b35fd7094ac4c8f5bdef487f56e320e008a73ff0ef612abd16da |
| CODE_INDEX.md | d3f9f54bad8ae31e420ea9e3151d48b7feddd204d7a6d7f5c9a03ff70d07306d | e6e9f707519cd20712727a94e81d7c4131aa8a82458a8f4f0b14fe381ce685a3 |

## 5. 资源与交接

/private/tmp/daa015-dev.DgUHuY 为本任务自有目录，含起点源码快照、两份精确清单、专属 Node 依赖副本、Vite 产物以及合成测试夹具；前述测试的部分旧辅助 fixture 和一次失败留下的合成 profile 仍在其中。它们不含用户 .local 或 .env。请 Verification 先用快照和 patch 审计精确增量；QA 完成且无继续依赖后，由协调者核对进程/占用并回收整个精确目录。Rust src-tauri/target 是正式树原有构建缓存，本次 Cargo 使用它，不归本任务单独删除。未创建容器、数据库服务、独立工作树或分支。

本文件记录 Development 的 developer_handoff。独立验证的结论和 Human Owner 最终验收另由对应角色与用户给出。

## 6. QA1 返工及新的 developer_handoff

QA1 以 [checklist.md](checklist.md) F-001/F-002 将 r1 退回 Development。本节是原 r1 内返工，不修改批准规格、不代写 QA 结论。批准的 spec SHA-256 仍为 `f571dd51dbed26a3d59f70e78253dc6e47bb89a61453e8c3ed2a97773910340d`；交付仍是正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD 仍为 `fd999224a8756feda314a33148304b4bf3461876`，包含已有未提交工作。协调者确认用户停止 DAA 后，只读检查 15191 无监听，才返工。没有操作或读取现有 `.local/dev`、dev API/数据库、真实样本或真实 PLC，也没有启动 Docker、MySQL 或原生 GUI。

**返工内容**：F-001 为启动采集所创建的连接意图单独标记归属。离线时暂停采集取消本轮尚未完成的自动连接及重试；已经连接时暂停采集保留连接；用户另外明确请求的手动连接意图不被暂停采集撤销。手动开始采集若因尚未连接、准入或容量失败，不提前清除仍有效的自动意图。激活后不会由旧的未完成启动任务自动连接新配置。F-002 将采集快照与上报快照的刷新错误分开；上报读取失败时，工作台与上报页面的共用卡片显示不可用，隐藏旧的运行状态、地址、计数及回执时间，只留安全暂停入口；禁止依据旧状态启动，成功刷新后恢复。手动确认上报时再次核对状态，避免等待确认期间发生刷新错误。采集快照错误只使用采集快照自身的时间说明。用户可见文案中英文成对。

**返工自检结果（非独立验证）**，以下命令均在 DAA 目录执行，临时 profile 均为本任务专属合成资料：

| 命令或检查 | 结果 |
| --- | --- |
| `TMPDIR=/private/tmp/daa015-dev.DgUHuY/daa-008-r2-a-fixtures cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib startup_offline_pause_and_manual_connection_intents -- --test-threads=1` | exit 0，1/1。走 `local_recovery::open`、两台内存模拟 PLC，覆盖 QA1 离线暂停、另一台持续采集、重开、手动启动失败后自动恢复、已连接暂停、手动连接失败后暂停仍保留手动连接意图。 |
| 同一 Cargo 命令将过滤器换为 `startup_` | exit 0，8/8，含四开关组合、合成 PLC 重连、老 profile 与设置错误、参与 PLC、原身份/目标与匹配回执。测试 profile 和传输均为隔离夹具。 |
| 同一 Cargo 命令依次过滤 `dispatch_rechecks_`、`qa_start_confirmation_must_not_dispatch_after_concurrent_settings_save`、`v2_worker_pause_save_preserves_inflight_receipt_and_stops_new_dispatch`、`plc_switch_rechecks_before_dispatch_without_stopping_other_sources` | 分别 exit 0，2/2、1/1、1/1、1/1；覆盖目标/来源变更、手动确认竞争、暂停后在途回执和逐 PLC 派发。 |
| `node --test tests/*.test.mjs` | exit 0，39/39。新增用例以真实 composable 与共用上报卡 Vue SSR 模拟两处页面、中英文、仅上报读取失败、隐藏旧值、暂停和刷新恢复；同时覆盖只有采集刷新失败。它们不是原生窗口或真实 IPC 证据。 |
| `./node_modules/.bin/vue-tsc --noEmit` 和 `./node_modules/.bin/vite build --outDir /private/tmp/daa015-dev.DgUHuY/daa-qa2-dist --emptyOutDir` | 均 exit 0；构建仍有第三方 VueUse 注释及 chunk 大小提示。 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml --all -- --check`；`cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --features rust-snap7-driver` | 均 exit 0；后者只编译生产驱动 feature，不连接 PLC。测试构建仍有此前存在的 `empty_for_test` 未使用告警。 |
| 中英 common locale 键比较；本轮触及文件 `git diff --check`；两份补丁 `git apply --check --reverse` | 均 exit 0；两语言各 697 个键。新增未跟踪文件由 Rust 格式化、TypeScript 构建及 Node 测试另行检查。 |

返工过程中一次新增 UI 测试将说明文案中“启动上报”误判为启动按钮；改成断言实际按钮后通过。一次完整 Node 回归为 38/39：旧确认对话框测试直接调用启动，没有模拟页面已成功读取上报快照；补齐这一现有前置状态后 39/39。没有删除测试或放宽产品检查。

**精确差异**：第 4 节是 QA1 候选，不是本次最终文件摘要。原始起点、QA1 快照和原补丁均保留；当前完整 34 个源码/文档/测试文件的前后摘要见 `/private/tmp/daa015-dev.DgUHuY/daa015-qa2-manifest.json`，SHA-256 `c51f4cc5d55e319b65a79d037cef2f0cce6ab4a8672ddff5f1f407dbe86ecc7c`。起点到本次候选补丁 `daa015-qa2-source.patch`，SHA-256 `3925faba55bb26a92106a0b49c6c1e066cb2a3d662aa192d2c6fa384dd2e4dd3`；QA1 到本次的 8 文件返工补丁 `daa015-qa1-rework.patch`，SHA-256 `766e4f83cab4a3688949098e11f0f0a61cd7cc5accefda3226125c95e7b94fff`。两份补丁均已对正式树反向检查通过。新增进入清单的 `FactsDeliveryPanel.vue` 与 `facts-delivery.test.mjs` 的 QA1 哈希分别与 QA1 独立副本和原始起点相同。任务记录 `tasks.md` 不在源码补丁中；两个 PLAN 索引由协调者维护，不属于 Development 源码清单。

| 返工文件（相对 DAA 根） | QA1 SHA-256 | 返工后 SHA-256 |
| --- | --- | --- |
| `src/console/composables/useLocalAcquisitionConsole.ts` | `14c2bcdfb13823532e99ae5baf41eae7d4fd9676ad31a89933e990e9d11af8dd` | `974cc46967529265c7cfafd0f2dc80084e1792de57935178f1cb555a4223cc20` |
| `src/locales/en-US/common.json` | `311269010e5c1594107bc1a4c2361a165c692f44dd6de8578dd1fe291593f990` | `da4943f8adce489a1aeebe894dc41be54a25d0fdb999d8f1a0c809b364575e08` |
| `src/locales/zh-CN/common.json` | `1fa3f0c9d945f4d2cbfe4409f47e5556546efe168d95da3d6ba66461f8e9b05e` | `da9c159c1a87391467bddca0f8d83a01ed6aed27a6124e19304f2e85031e1b2b` |
| `src-tauri/src/infrastructure/local_store/tests.rs` | `fd4e24eb3632a173ffa584fe798c5c0b50e552449e89082dd12badc9d2295fec` | `15417e9571512a4a7e740b2910af467312f60626d709ea66f192f5188894bc9f` |
| `src-tauri/src/services/local_supervisor.rs` | `af9b4fd0f36cb5e0c70b46c5297742388f0a13b6c7deaa3a8e46114695c9c704` | `15b9729c661d1478d09f71359670351263350059d755b2e0e696c2b16a8c3874` |
| `tests/startup-settings.test.mjs` | `1315260dbda9b35fd7094ac4c8f5bdef487f56e320e008a73ff0ef612abd16da` | `5092d3b91c41a20d1ef0446dc0e750e7eea2227494eb9c52a9932094eeaa62a4` |
| `src/components/console/FactsDeliveryPanel.vue` | `8e2b14c639e4bf72feaf479ab90e5d848d7513f0ef84058eda8acde8a91af199` | `3479318f093c287e1e9e5d97ce540823f103f0e6400686f7435b7574866433dc` |
| `tests/facts-delivery.test.mjs` | `8a15e64935fbda677a7c32fc8f3202b1adcd2d313c9fb0b38f6295d35c893696` | `3eb20e2453287caa6c445fccff280eadfa4b19e8162cdd9d60cae28a567cf6fb` |

`/private/tmp/daa015-dev.DgUHuY` 的原始起点、QA1 与新候选证据和临时构建为本任务所有，暂留供新一轮 QA 核对；完成核验且没有继续依赖后，由协调者检查归属、运行情况并回收。QA1 `/private/tmp/daa015-qa.5cjZ1S` 为独立 QA 证据，Development 未修改或清理。真实 Mac/Windows 原生窗口、真实设备、真实后端、部署与 Human Owner 验收仍在本次证据之外。

## 7. QA2 返工及新的 developer_handoff

QA2 在 [checklist.md](checklist.md) 记录 F-003、F-004、F-005 并退回 Development。本节为已批准 r1 内返工，保留前两轮历史，不修改规格或 QA 文件。批准 spec SHA-256 `f571dd51dbed26a3d59f70e78253dc6e47bb89a61453e8c3ed2a97773910340d`；交付仍为正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `fd999224a8756feda314a33148304b4bf3461876`，既有未提交改动保留。返工前只读核对 QA2 交接 34 个文件摘要全部匹配，`lsof -nP -iTCP:15191 -sTCP:LISTEN` 无监听；正式 DAA 保持停止。

- F-003：折叠「启动设置」时移除问号及提示，只保留标题和展开入口；折叠会清除悬停、焦点和点击的帮助状态。重新展开后仍可悬停、聚焦或点击查看帮助。
- F-004：保存设置、启动、暂停或重新绑定可能先改变运行状态后才因快照读取失败而报错。前端在这类操作之前标记上报状态暂不可用；只有取得新的有效上报快照才恢复显示。保存未知结果及命令错误保留不可用状态，仍可安全暂停；先前在途的轮询结果通过序号检查，不得覆盖后来的操作结果或清除错误。采集与上报的刷新状态仍分别处理，原有保存错误和确认流程保留。
- F-005：激活配置时先判断自动启动连接是否会因端点变更或禁用而断开；容量阻止采集而仍 pending 的旧启动连接意图不带入新端点或禁用配置。显式人工连接意图、同端点已有连接以及手工暂停时保留连接的语义不变。

**Development 自检（非独立 QA）**，以下命令在 DAA 目录执行。Rust 的 `TMPDIR` 为 `/private/tmp/daa015-dev.DgUHuY/daa-008-r2-a-fixtures`，只使用任务专属合成 profile、合成 PLC 内存传输和内存回执：

| 命令或检查 | 结果 |
| --- | --- |
| `TMPDIR=/private/tmp/daa015-dev.DgUHuY/daa-008-r2-a-fixtures cargo test --manifest-path src-tauri/Cargo.toml --offline --locked --lib startup_pending_activation_respects_connection_ownership -- --test-threads=1` | exit 0，1/1，走 `local_recovery::open` 和配置保存/激活：低容量使自动采集 pending，覆盖更换端点、显式手动连接、同端点及禁用后重新启用。无真实网络或 PLC。 |
| 同一 Cargo 命令过滤器换为 `startup_` | exit 0，9/9，含四种启动组合、QA1 离线暂停与人工连接、旧兼容 profile、来源/目标保护和内存匹配回执。 |
| 同一 Cargo 命令分别过滤 `dispatch_rechecks_`、`qa_start_confirmation_must_not_dispatch_after_concurrent_settings_save`、`v2_worker_pause_save_preserves_inflight_receipt_and_stops_new_dispatch`、`plc_switch_rechecks_before_dispatch_without_stopping_other_sources` | 均 exit 0，合计 5/5；复验派发目标与来源、并发确认、暂停在途回执和逐 PLC 参与。 |
| `node --test tests/*.test.mjs` | exit 0，39/39。真实 composable 与 Vue renderer/SSR 定向覆盖中英折叠及帮助恢复、保存成功后快照失败、`storage_pending`、启停和改绑已变更但返回失败、旧轮询成功或失败迟到、保存期间和恢复。 |
| `node /private/tmp/daa015-qa2.TJ14Wm/ui-probe.cjs` | exit 0；QA2 原探针使用正式候选源码，实际工作台及上报存储两个 Vue 页面、中英文，复验折叠、周期读取失败、保存后读取失败和恢复。外围控件与 IPC 为合成替身；不是原生 GUI。 |
| `./node_modules/.bin/vue-tsc --noEmit`；`./node_modules/.bin/vite build --outDir /private/tmp/daa015-dev.DgUHuY/daa-qa3-dist --emptyOutDir` | 均 exit 0；Vite 保留第三方 VueUse 注释和 chunk 大小提示。 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml --all -- --check`；`cargo check --manifest-path src-tauri/Cargo.toml --offline --locked --features rust-snap7-driver` | 均 exit 0。生产驱动 feature 仅编译未连接设备；测试构建保留原有 `empty_for_test` 未使用告警。 |
| 触达文件 `git diff --check`，两份新补丁 `git apply --check --reverse` | 均 exit 0；新增未跟踪文件另经 Rust 格式化、TypeScript 检查和测试。 |

返工中完整 Node 回归第一次为 38/39：原有确认测试在一次命令返回错误后立即尝试下一次启动，没有先取得新快照；测试改为先用成功的安全暂停获得新快照后，复验原来的确认分支，最终 39/39。没有删除测试或放宽不可用期间的保护。

**精确候选**：原始起点及 QA1、QA2 快照和对应补丁均保留。当前完整 34 文件摘要在 `/private/tmp/daa015-dev.DgUHuY/daa015-qa3-manifest.json`，SHA-256 `0b7c9d22df85f4dafdddff5cf15b26063ed4fbda0dbec67819ccbcb897c22b90`。起点到当前候选 `daa015-qa3-source.patch` SHA-256 `d8166901f77a805ef79b16457006ab2551ca6243339eab12238321630321d9ee`；QA2 到当前候选 6 文件增量 `daa015-qa2-rework.patch` SHA-256 `ddc7af4aa69e2379356d22d0a3cde6408ee084560d170e1400727d2384ff0510`。均存放在同一临时目录，两份补丁反向核对正式树成功；本任务 `tasks.md` 及协调者维护的 PLAN 索引不列入源码清单。

| 返工文件（相对 DAA 根） | QA2 SHA-256 | 当前候选 SHA-256 |
| --- | --- | --- |
| `src/components/console/StartupSettings.vue` | `d3e67d8a77cb6bd30d97907d0e4baa78f3cc0dd196310638f1f36153a6d38df5` | `a25ec673dbe6ddc823ffcfcd89bc09bd5811ee1ccab509ea2b6dfde1c0ab24a1` |
| `src/console/composables/useLocalAcquisitionConsole.ts` | `974cc46967529265c7cfafd0f2dc80084e1792de57935178f1cb555a4223cc20` | `98776928b7b6067c9cb994594db82f4ed45deed9f536677346693ddd49d08ca4` |
| `src-tauri/src/infrastructure/local_store/tests.rs` | `15417e9571512a4a7e740b2910af467312f60626d709ea66f192f5188894bc9f` | `0f8a2dabebd16366d3ecf81eaafbe50e1d92d3b97426795c6eb52db436f3fc47` |
| `src-tauri/src/services/local_supervisor.rs` | `15b9729c661d1478d09f71359670351263350059d755b2e0e696c2b16a8c3874` | `9970d8693ee90275ba6912e18eba17cd05b1f7425cbe5860e91c93db377fde8b` |
| `tests/startup-settings.test.mjs` | `5092d3b91c41a20d1ef0446dc0e750e7eea2227494eb9c52a9932094eeaa62a4` | `547ce58c6f7eb45e4ae1074181456532d75052a03999f972a6cbfbdc4af95852` |
| `tests/facts-delivery.test.mjs` | `3eb20e2453287caa6c445fccff280eadfa4b19e8162cdd9d60cae28a567cf6fb` | `70dc7988fb023899acdb4bc8c3744253a096172c3bdfefa94ec258ff49295da9` |

本轮未读取或操作现有 `.local/dev`、dev API/数据库、真实配置、样本或 PLC，未启动 Docker/MySQL/系统原生窗口。`/private/tmp/daa015-dev.DgUHuY` 为本任务所有，原始与多轮候选快照、补丁、测试及构建产物暂留给新一轮 QA；完成核验且无继续依赖后由协调者核对进程和归属后回收。QA1、QA2 独立证据目录未修改或清理。Mac/Windows 原生窗口、真实设备/后端、部署及 Human Owner 最终验收均不在本次证据之内。

