Task ID: DAA-013
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: QA4 的英文接入按钮问题已返工，待新的 fresh-context Verification 复核精确候选。
Workflow Mode: STD
Spec: [DAA-013 r1](./spec.md)
Spec SHA-256: `fc9d5deba6245f4f0c457bc6ee26673298361f08be60b107d6b3d09704a82bb8`
Updated: 2026-11-13 Asia/Shanghai

# Development 事实与交接

本节至首次资源边界保留 QA1 前的原始交接事实；返工后的最终文件摘要与检查见文末。

## 批准、起点与实际范围

Human Owner 明确批准「还是STD吧，批准 DAA-013 r1」。Development 按该精确修订第 3、4 节工作；最终交付是 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 工作树，Git HEAD `fd999224a8756feda314a33148304b4bf3461876`，未暂存或提交。起点已有大量 DAA-010、DAA-012、CU-009 和 ARCH-ACQ-004 相关未提交及未跟踪工作，因此以下 before 是本任务开始时的实际工作树快照，不是 Git HEAD。任务加载 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`，以及 IPC 字段与数据库事务相关的 `backend-arch` 指引。

先在 `/private/tmp/daa013-r1-dev-OfJKE3/candidate` 创建源码与依赖隔离副本，排除 `.env*`、`.local`、构建产物与既有 profile；构建输出及合成 SQLite 均使用本任务临时资源。协调者确认 Human Owner 已停止 DAA；合入前协调者再次只读检查 15191、已有 dev 的两个 SQLite 和正式 DAA 可执行文件，均无打开句柄。另一 ARCH-ACQ-004 会话确认本任务负责 DAA 重叠设置界面、locale、测试和指南。14 个候选变更文件合入前逐项与初始 SHA-256 比较，均一致；逐项写入并重新校验后，正式文件与验证候选一致。后续仅对测试文件增加 runtime2/3 和多状态保护用例，增量合入前再次核对该文件上一次 SHA-256。保留其他会话既有修改，未修改 `spec.md`、`checklist.md`、数据库 DDL、依赖或锁文件。

以下路径相对于 DAA 项目目录。表中的 14 项加本 `tasks.md` 是本任务实际交付文件；`sample_upload.rs` 两个源码和其测试在 Git 起点本来即为未跟踪文件。未引入新源码结构，未改 `CODE_INDEX.md`。

| 路径 | 开始时 SHA-256 | 交接时 SHA-256 |
| --- | --- | --- |
| `src/components/console/FactsDeliveryDialog.vue` | `ff955905f005c90c1e9129b628c8faf2196ad547c66a71bb5bb7e685f295d07c` | `66e9149f8734d6e7c47c03a0ba34a22c996546e8daaea72c7abc290fbe1d260b` |
| `src/console/composables/useLocalAcquisitionConsole.ts` | `6b660c6ecd5941f1742eedf5e704f42c4d33faf655939739abde6d62d789a500` | `2067d4c4f1f4a0d39ff22d15be461f4898c3f41d8fa6b3d9c1b9afa282f2d439` |
| `src/services/factsDelivery.ts` | `6eace885162b595f108a9c881ecb1f3ad1e3c1db59a1e1ac1ed677a889a53dfb` | `115dc1d7fb6ae289331ff302e00f7f0e00b69aed1a2b12ccdf8f3a4ce946bed3` |
| `src/locales/en-US/common.json` | `cb19cf17fbdd55aab33df6d32ab6305f48f37f39c5970f63d0f490efb9fd7a88` | `c9535dc0818aacf1e529b8c2c1bfecefc1ba946744e83ddaaba4a3d2b9337c39` |
| `src/locales/zh-CN/common.json` | `dd0092edafe049ee271b4d7a52c921390694e3a139e8ca6a49074df086f1ab46` | `9eb9025354fdc58c14a59a77aeb90e822173051a47f10567546b0b2be026833a` |
| `src/styles/app.css` | `4a0bf6bd9cce4b13e82b409664fd2100f1199b9e096cf50ab1cd735f387c4977` | `d73dd01040e20d22902198134598fa9b139e3c9335cdf791115122d5811fd9cb` |
| `src-tauri/src/domain/sample_upload.rs` | `72274a2ffa5bbdf49dfdc62a32680b4cdc432b5b7f4a6ced13e329b5fe2d498e` | `ac0dac6e8e18048899b59a2eaae1bdc72ad3d906ee179fb0eb439101e75f860b` |
| `src-tauri/src/services/local_delivery.rs` | `dc14cc9df50b27c0c30728b3e098271f262088d170a05b3f4e7a4f552fe589f2` | `2cf8a91b3c918b9c4a453e2aba1be88894c3874374a0a59a629ab1b82925a4ff` |
| `src-tauri/src/infrastructure/local_store/sample_upload.rs` | `038f030256d3f833d2970a56a57fae26d8137e7d6c714f70ee0029437b12f19c` | `84afa652b8b4ff114bf2683138ed5f587f1a1c090efc2bc545ae714779de2e71` |
| `tests/facts-delivery.test.mjs` | `86516e7fb13226c0f67ae65f555c5fd3c028848ee6c18001cf12d8deda2cd4ed` | `d51e9e9ae8d447f9714a14dfc15c8b3fd8ef71887fd7c5acd43b8297ee66458f` |
| `src-tauri/src/services/local_delivery_tests.rs` | `e41ef8893d353619963ac62adaf7fae71c90f32e0a3d663d1f4234768bffc4af` | `99afcfd90f4e511d258708130440d649357e43a1a9561e6f2f9eb477c4c4eed1` |
| `src-tauri/src/infrastructure/local_store/sample_upload_tests.rs` | `b80992bafee998f6527afb0cd8b3e1bdb4cd6e7fb8c78cc5eaccf883b2b43bb7` | `ce3f4c97e0418f2d8d52fc6c2d66b0276fabf3dba5f05cb3df3f4d897399be56` |
| `STAGE_C_GUIDE.md` | `b5dca306f7865003ee2f7cd203a3afb892d9c31433e5b6a0bb7e88185fd63d4e` | `4b6854fed2a742ef3efa4f7e2e1a45b57cb9eda144f7b8d21651d4ee99e3c982` |
| `STAGE_C_GUIDE.zh-CN.md` | `621778efe38ec663aac2618fd3714b47ee365d8f8c3652bb2c3b0104f2eb2d49` | `dda01608f7ee820cefe28e330cf07673cdcf593e626ccd6e6048bf0105ccbcc5` |

## 实施事实

- 设置/来源 IPC 每条绑定带本机 PLC ID 和独立三项，固定 `identityMode=per_plc` 仅作 IPC 兼容标记，不是用户开关或数据库持久状态。前端在标记缺失时拒绝打开编辑、开始/继续及同目标重绑；严格 Rust DTO 拒绝旧请求和非法/重复身份。
- 在既有单次事务与设置版本 CAS 内，从 `reporting_generations` 获取或验证 `(plc_id, source_generation) -> instance_id, local_plc_id, local_generation`，采样按 PLC 获取身份；旧 `reporting_identity` 在所有当前绑定实例相同时保存该实例，在混合实例时置空以令旧版单实例全检拒绝。新版 `full_check` 按代次逐条检查关联，未引入 DDL 或迁移。空绑定、同实例、异实例、复用代次和不在活动配置的已保存绑定按获批范围处理。
- 设置界面按活动本机 PLC 分行，保留历史已存绑定及其本机 ID；DB 来自活动配置。三字段 JSON 和带旧 `dbNumbers` 的 JSON 都只写入本行三项。保存与同目标/开始确认继续使用原有启停、版本和完整来源集合；确认逐项显示实例 / PLC / DB / 代次，含合格历史待传来源。冻结请求、原目标、尝试和回执仍由原逐样本账本与 worker 处理。中英操作指南对应更新。

## DEV self-check

环境 macOS 15.7.7 arm64，Node `v22.19.0`、pnpm `11.11.0`、rustc/cargo `1.89.0`。除明确说明外在 DAA 目录运行；Cargo 使用项目 `Cargo.lock` 与 `CARGO_TARGET_DIR=/private/tmp/daa013-r1-dev-OfJKE3/cargo-target`，测试用自建合成 profile，不访问真实后端或设备。

1. 正式树 `node --test tests/facts-delivery.test.mjs` 退出 0，6/6：settings 与来源 IPC 参数、开始及继续的完整来源、缺失兼容标记拒绝、逐行手填/粘贴、无效输入不改其他行、取消、重复与双语键等。对照隔离基线**实际旧 SFC**（SHA-256 `ff955905f005c90c1e9129b628c8faf2196ad547c66a71bb5bb7e685f295d07c`）编译并执行旧 save：直接保存新版混合绑定时旧界面阻止；重新填写后它透传 `identityMode`，但又提交顶层 `instanceId` 并丢弃逐行实例；全空也提交顶层 `instanceId:null`。捕获的两种实际旧请求均被新版严格 DTO 拒绝；并分别验证移除顶层旧字段后缺失逐行实例仍拒绝。合成请求 SHA-256 `a8bc7f8a7309519dd508b024d193b4f420147bdb980f447d4beb54f90e5937a1`。
2. `cargo test --locked --manifest-path src-tauri/Cargo.toml --lib infrastructure::local_store::sample_upload_tests -- --test-threads=1` 在初始候选退出 0，14/14；最终测试变更后在正式树分别运行 filter `per_plc_identity_preserves_legacy_and_refuses_old_ipc_and_old_admission`、`mixed_bindings_preserve_all_existing_sample_and_receipt_states`、`runtime2_and_3_keep_local_collection_and_refuse_v2_delivery`，均退出 0。覆盖两实例、相同实例及代次字符串、旧代次换实例拒绝、CAS 冲突、重复 PLC、暂不活动绑定、旧准入等效拒绝及重开。四个合成旧周期分别包含无标记前驱、全空仅本地、未冻结、已冻结未派发、unknown、已确认；比较样本原文/摘要、周期和上下文、序号、观察/采集时间、冻结目标与正文、尝试与回执，混合实例保存前后及重开一致。另有现有定向用例覆盖采集开始时捕获的旧身份、迟到旧尝试回执和显式同目标重绑。runtime2 unsealed 与 runtime3 sealed 均可本地采集两 DB 且拒绝 v2 开始，版本不变。
3. `cargo test --locked --manifest-path src-tauri/Cargo.toml --lib v2_saved_binding_cycle_reopens_and_delivers_matching_receipts_over_loopback -- --nocapture` 在隔离候选执行：默认沙箱对 `127.0.0.1:0` 返回 EPERM，针对该合成回环测试按工具机制获最小提权后退出 0。两台 PLC 各两个 DB 产生四次逐样本 POST；过期版本、缺少来源或错实例确认均拒绝且未开始。首个错实例回执使样本保持 unknown，真实 worker 以完全相同正文重试，最终四个样本都以匹配回执确认，逐条检查实例、PLC、DB、代次、样本、序号和正文。旧错样本回执及迟到回执另由上述账本用例覆盖。隔离目标未连接任何真实后端。
4. 真实生产构建的 Vue 设置组件在自建合成状态/IPC 验证容器中用浏览器 `960 × 640` 观察：中英文每台一行，A 手填、B 两种 JSON、无效粘贴不串改、关闭取消、保存回读完整不同实例、DB 保持 `DB22, DB23`。测试各三项为 128 字节的长身份时，上报确认内容可滚动，确认/取消可操作；浏览器临时 viewport 已恢复。此项为浏览器组件和合成 IPC 证据，不代表原生 Tauri/Windows、真实 profile 或现场联调。自建静态回环服务器在默认沙箱同样 EPERM，最小提权后完成并已停止。
5. 隔离副本 `pnpm --config.verify-deps-before-run=false build` 退出 0；正式树执行相同脚本组成的 `pnpm --config.verify-deps-before-run=false exec vue-tsc --noEmit` 与 `pnpm --config.verify-deps-before-run=false exec vite build --outDir /private/tmp/daa013-r1-dev-OfJKE3/formal-build --emptyOutDir` 均退出 0，正式产物与隔离产物的资源文件名一致。首次原样 `pnpm build` 因复制依赖目录触发 pnpm 自动校验/联网安装及无 TTY 中止，退出 1；禁用该自动重装后使用已有锁定依赖构建，未安装或修改依赖。Vite 报已有依赖 PURE 注释及大 chunk 提示。
6. 正式树 `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check` 退出 0；`cargo check --locked --manifest-path src-tauri/Cargo.toml --features rust-snap7-driver` 退出 0；普通开发路径等效的 `cargo build --locked --offline --manifest-path src-tauri/Cargo.toml --no-default-features --features rust-snap7-driver --bin aiis-data-acquisition-agent` 退出 0、无 Rust warnings，未启动应用。`cargo test --lib` 存在既有测试专用 `empty_for_test` 一条 dead_code warning；不将其写成零警告。首次隔离编译缺少未复制的公开 `contracts/.../vectors.json` 而退出 101；补入公开合同文件后锁定编译通过。
7. 仓库 `git diff --check` 退出 0；双语指南和 spec 的 53 个本地相对链接路径存在性检查缺失 0（不验证锚点）。正式树上述 14 项 `shasum -a 256 -c /private/tmp/daa013-r1-dev-OfJKE3/integration-sha256.txt` 均 OK，获批 spec 当前哈希仍为本文件头所列值。

## 限制、资源与精确交接

- 本记录是 Development self-check 与 `developer_handoff`，不是独立 QA verdict 或 Human Owner 验收。DAA-010 r5 的既有 `qa_failed`、其后续修订及实际采用边界不因本任务改变。需 fresh-context Verification 对本精确修订、上述交付树、before/after、实现和验证独立复核并创建自己的 `checklist.md`。
- 旧 binary 未实际执行；旧全检拒绝按原实现等效 SQL 和实际旧 SFC 发送路径验证，不将其称为原生降级验证。Windows 10/11 x64、实际旧程序、真实 profile/待处理样本、真实后端、MySQL、PLC、服务启停、部署和发布均未测试或操作。
- 本任务专属 `/private/tmp/daa013-r1-dev-OfJKE3` 包含初始基线、候选、旧 SFC 驱动与真实请求、合成 UI 验证夹具、构建目录和 Cargo 缓存；测试和临时服务器已停止。为供 fresh Verification 审核旧基线及重复验证暂保留，Verification 无依赖后由协调者确认归属并清理，不触及用户 `.local`、配置、数据库、历史或其他任务资源。


## QA1 返工与新的 developer_handoff

2026-11-13，fresh-context Verification 对同一获批 r1 记录 `qa_failed`，将 [F-DAA013-QA1-001 与 F-DAA013-QA1-002](./checklist.md) 返回 Development。原任务范围未扩展；QA1 verdict 和证据保持原样，Development 不修改 checklist。返工仍在 `/private/tmp/daa013-r1-dev-OfJKE3/candidate` 隔离实施，交付正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `fd999224a8756feda314a33148304b4bf3461876`，未暂存或提交。合入前协调者确认 15191、现有 dev 双库和正式 DAA 二进制无打开句柄；七个文件逐项比较 QA1 首次交接 SHA，均未出现新并行编辑，再逐项合入并与候选核对。

根因一是旧 Start 在读取设置与来源并比较确认之后才取得与保存共用的 `delivery` 锁；只更改目标的并发保存可先提交并停传，旧 Start 随后却恢复旧目标。根因二是同目标重绑的 Service 完整来源比较和 SQLite 重绑分处两个 storage actor 回合；激活或旧轮落库可以改变来源集合，而旧的重绑写入只复核版本、目标和目标样本身份。两项均在 QA1 日志和隔离红例中确定性复现。

返工在读取 Start 确认快照前取得现有 `delivery` 锁并保持到运行状态发布，和保存串行；最终来源确认前在同一 storage actor 回合重验版本、目标与完整来源。重绑写入前在同一 storage actor 回合再次比较完整来源集合，既拒绝新增历史来源，也拒绝来源移除。worker 标记发送尝试前，在同一 actor 回合确认当前来源均已包含于先前确认，避免新来源在选择样本和最终派发之间插入。上报失败/来源变化补充中英提示。未引入新数据库结构、全局状态或用户开关；三个同步回归使用逐次调用的回调控制测试时序。

锁顺序：Start/保存使用 `delivery → storage`，Start 恢复 in-flight 时在持有 `delivery` 下对 `delivery_http` 仅 `try_lock`；worker 先持有 `delivery_http` 再取得 `delivery`，因此对向持锁时 Start 立即返回 `delivery_http_busy` 而不等待。storage actor 回合不取得 `delivery`；重绑不新增锁。网络等待不持有 `delivery` 或 SQLite 事务，已在途的原尝试仍可结算。

以下七项是 QA1 后实际返工文件，before 是 QA1 首次交接时内容，after 是本次交付内容；其他首次交接文件未由本次返工修改。`tasks.md` 本次追加此记录。

| 路径 | QA1 前 SHA-256 | 返工后 SHA-256 |
| --- | --- | --- |
| `src-tauri/src/services/local_delivery.rs` | `2cf8a91b3c918b9c4a453e2aba1be88894c3874374a0a59a629ab1b82925a4ff` | `f8f71af5ff072b4872347f1052f00e3914f8e14035c103ee047078c50895bbe6` |
| `src-tauri/src/services/local_delivery_tests.rs` | `99afcfd90f4e511d258708130440d649357e43a1a9561e6f2f9eb477c4c4eed1` | `14d8307e2d87fbada2559938fe8cfccd05f95ee8ea912d13d48c6e19819e6366` |
| `src-tauri/src/infrastructure/local_store/sample_upload.rs` | `84afa652b8b4ff114bf2683138ed5f587f1a1c090efc2bc545ae714779de2e71` | `82ee5e92829f128f69a7ce09768f4e5cb88ca1cceb34897936539a242c617951` |
| `src-tauri/src/infrastructure/local_store/sample_upload_tests.rs` | `ce3f4c97e0418f2d8d52fc6c2d66b0276fabf3dba5f05cb3df3f4d897399be56` | `3f1ed2277fdb87e74bd1e28a960c89de3948ac6b5304b9d8de6558ea4042df8d` |
| `src/locales/en-US/common.json` | `c9535dc0818aacf1e529b8c2c1bfecefc1ba946744e83ddaaba4a3d2b9337c39` | `7009dc1d000dcfa9188859ea54ae3a87674e2a14658c5819adce2e3e3d3bbd5e` |
| `src/locales/zh-CN/common.json` | `9eb9025354fdc58c14a59a77aeb90e822173051a47f10567546b0b2be026833a` | `5b25c1bb6e2ec5e36cf3ec4ae5bd3fa59facb562e5fe60f9f94f55d3560e33a7` |
| `tests/facts-delivery.test.mjs` | `d51e9e9ae8d447f9714a14dfc15c8b3fd8ef71887fd7c5acd43b8297ee66458f` | `9b007af7d13a6e518151d8d57f9461bf6187c1198da1f9d2f5dd038c1a39bb8c` |

### 返工 DEV self-check

- QA1 复现文件与日志 `/private/tmp/daa013-r1-qa-urkO9e/race-repro.log`、`rebind-repro.log` 只读；未改 QA 文件。在自己的隔离副本中，旧 Start + 新目标的同步测试先重现红例：旧目标 POST，退出 101；锁调整后返回 `source_confirmation_changed` 且无 POST，退出 0。独立 QA 的来源 4→2 同目标重绑时序在返工候选返回 `source_confirmation_changed`，原目标、unknown 状态、正文、摘要和无重绑记录均保留。另覆盖来源增加、重绑中并发保存目标后拒绝、重新确认后允许原字节重绑、Start 最终核对中新来源到达、样本选中后新来源到达而不标记尝试/不 POST。
- 隔离候选 `TMPDIR=/private/tmp/daa013-r1-dev-OfJKE3/daa010-r5-dev-private CARGO_TARGET_DIR=/private/tmp/daa013-r1-dev-OfJKE3/cargo-target cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib infrastructure::local_store::sample_upload_tests -- --test-threads=1` 退出 0，17/17，覆盖旧库、冻结/回执、runtime2/3、多 PLC 和重绑。准备新增 Start 测试时首次编译因测试缺少 `Arc` 导入退出 101，补入测试导入后该用例和后续正式检查通过。
- 正式树以同一 `TMPDIR`、`CARGO_TARGET_DIR` 执行 `cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib services::local_delivery::tests -- --test-threads=1`，退出 0，18/18。包含 QA 两处并发时序、新增来源时的 Start/派发、真实回环多 PLC/DB 及错误回执重试、pause/resume、并发保存时在途请求仍以原目标和字节取得匹配回执且停止新派发。回环端口按前次已批准隔离验证使用最小提权；未连接真实服务。正式树单独执行 `cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib rebind_rechecks_complete_sources_after_late_historical_cycle -- --nocapture` 退出 0。
- 正式树 `node --test tests/facts-delivery.test.mjs` 退出 0，6/6，含四个并发相关错误码的中英文可见文案键；`cargo fmt --manifest-path src-tauri/Cargo.toml -- --check` 退出 0；`pnpm --config.verify-deps-before-run=false exec vue-tsc --noEmit` 与 `pnpm --config.verify-deps-before-run=false exec vite build --outDir /private/tmp/daa013-r1-dev-OfJKE3/qa1-formal-build --emptyOutDir` 退出 0。Vite 仍有依赖 PURE 注释和大 chunk 提示。
- 正式树 `CARGO_TARGET_DIR=/private/tmp/daa013-r1-dev-OfJKE3/cargo-target cargo build --locked --offline --manifest-path src-tauri/Cargo.toml --no-default-features --features rust-snap7-driver --bin aiis-data-acquisition-agent` 退出 0，无普通构建 Rust warnings；`cargo test --lib` 仍有既有 `empty_for_test` 一条测试专用 dead_code warning。`git diff --check` 退出 0。已验证源码与正式文件由 `/private/tmp/daa013-r1-dev-OfJKE3/qa1-final-sha256.txt` 逐项核对。

**新交接**：请协调者为上述精确 r1、HEAD 和返工后工作树启动新的 fresh-context Verification，复核两项 QA1 finding、并发锁顺序、来源增减和在途结算；本自检不代替 QA verdict，也不授予 Human Owner 最终验收。旧版二进制原生回退、Windows、真实 profile、实际后端/设备、MySQL、部署与发布仍未验证或授权。自有 Dev/QA 临时根仅供 QA2 复核，相关合成进程已结束；验证不再依赖后由协调者确认归属再清理。

## QA2 返工与新的 developer_handoff

2026-11-13，fresh-context Verification 对 QA1 返工对象记录 `qa_failed`，将 [F-DAA013-QA2-001](./checklist.md#f-daa013-qa2-001--超时保存延迟提交后仍可向旧目标派发) 返回 Development。本次仍为 Human Owner 已批准的 DAA-013 r1，规格与 allowlist 未扩展，QA1 和 QA2 原事实、verdict 保持不变。此前 QA1 交接及其摘要为历史记录，最终内容以下表与本节为准。正式交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `fd999224a8756feda314a33148304b4bf3461876`，未暂存或提交。Development 未修改 spec 或 checklist。

根因是现有 storage actor 的写调用在 10 秒返回 `storage_pending` 后，已入队写入仍可能随后执行并提交；此前保存仅在 `Ok` 时停止 worker，因此目标迟到更新后仍可能使用旧目标派发。返工保留原错误返回，将保存成功或结果未确认的 `storage_pending` 均在持有既有 `delivery` 锁时停止新派发；可确定的同步失败仍保留原运行状态。界面以中英文说明保存结果未确认、上报已暂停以及稍后重开设置核对。若迟到写入失败同样保持暂停，需明确重新确认继续。派发标记尝试前在同一 actor 回合再核对当前目标和已确认来源，防止选中样本后目标改变仍发送；原冻结目标、正文、尝试和在途回执未改写。

在途回执遇到同类 storage 超时还暴露一个次序窗口：旧派发失败若在释放 HTTP 许可后才写入错误，可能覆盖用户随后明确恢复的状态。现在 worker 先在既有 HTTP 许可内锁存本轮错误及停传，再释放许可；worker 锁序仍为 `delivery_http → delivery`，Start 持有 `delivery` 时只对 HTTP 执行非阻塞 `try_lock`，冲突立即返回而不相互等待。storage actor 回调不取得 `delivery`，网络等待不持有 `delivery` 或 SQLite 事务。未添加全局开关、DDL、持久状态或 profile 迁移。

以下六项为 QA2 后返工文件；before 是 QA2 验证对象，after 是本次最终正式交付。合入前协调者再次核对 15191、现有 dev 两库和正式 DAA 二进制均无打开句柄，且正式树 14 项均与 QA2 基线一致；逐项合入后复核并行改动。后续在途回执定向验证时，又单独核对并合入两个 Rust 文件：`local_delivery.rs` 中间值 `2a3b68f5b496348e8b6080d3a5884df22d7324270c2dc5b523f45a91bc59d1fe`、`local_delivery_tests.rs` 中间值 `60dc36eedab4e0858a49cd39b7ac5a5826d086b9e7f86dab928ac215a12d325b`。`tasks.md` 本次更新头部并追加本节。

| 路径 | QA2 前 SHA-256 | 本次交付 SHA-256 |
| --- | --- | --- |
| `src-tauri/src/services/local_delivery.rs` | `f8f71af5ff072b4872347f1052f00e3914f8e14035c103ee047078c50895bbe6` | `212b6f898ab5c13eba8e0cc624666ce1fb6372c1de36f8e14cb6a53b50a1daf2` |
| `src-tauri/src/services/local_delivery_tests.rs` | `14d8307e2d87fbada2559938fe8cfccd05f95ee8ea912d13d48c6e19819e6366` | `273b83da043e7ca4b01ec5185ba065bee33c83363f06e3b4564db4662808ad17` |
| `src/components/console/FactsDeliveryDialog.vue` | `66e9149f8734d6e7c47c03a0ba34a22c996546e8daaea72c7abc290fbe1d260b` | `1ddac4d8464dfae3fae0ebbde18c9c46800df49ba5e60b0e2fb6b9ddd25aa7bd` |
| `src/locales/en-US/common.json` | `7009dc1d000dcfa9188859ea54ae3a87674e2a14658c5819adce2e3e3d3bbd5e` | `f1828339abf86579b01bd1f6581578976799ee1189296f09d43efd2eff030744` |
| `src/locales/zh-CN/common.json` | `5b25c1bb6e2ec5e36cf3ec4ae5bd3fa59facb562e5fe60f9f94f55d3560e33a7` | `d174d0a695ebd1a259917cd4a41961c459b595754d637ebd3c5d2a99dcf8f285` |
| `tests/facts-delivery.test.mjs` | `9b007af7d13a6e518151d8d57f9461bf6187c1198da1f9d2f5dd038c1a39bb8c` | `eb0ed338fb58b0f52a2c6afed64f6a75b25f8c93f80ff4397c8a5d66eadd30f5` |

### QA2 返工 DEV self-check

- 只读 QA2 原复现和日志 `/private/tmp/daa013-r1-qa2-Zmn9qT/pending-save-repro.log`；在自有隔离候选先复现 10 秒超时后迟到提交及旧目标 POST 的红例（退出 101），修正后验证返回 `storage_pending` 即停传，未决时 Start 返回 `storage_timeout`，迟到成功后旧版本确认被拒、新版本与完整来源明确确认后可向新目标发送。迟到校验失败时设置保持原样但仍暂停，显式确认原设置可恢复。
- 合成 HTTP 回执在 storage actor 阻塞期间到达：回执写入也超时并排队，worker 在释放 HTTP 许可之前锁存失败；storage 恢复后原请求按原目标及原正文结算、匹配回执保留，没有新增旧目标 POST。旧版本不能恢复，新版本确认后可以恢复并发新目标。首次使用 4 秒等待新 POST 的强化测试失败；诊断为 storage 读取超时后现有 worker 使用 5 秒回退轮询间隔，将等待上限调整为 8 秒后该用例通过（隔离候选 1/1，16.54 秒）。中途一次 `--exact` 缺少完整模块名导致 0 tests，移除该参数后才执行上述 1/1。隔离候选 `v2_worker_retries_after_local_ack_write_failure_without_reopen` 1/1，验证回执写入失败后同进程显式恢复。
- 正式树使用 `TMPDIR=/private/tmp/daa013-r1-dev-OfJKE3/daa010-r5-dev-private`、`CARGO_TARGET_DIR=/private/tmp/daa013-r1-dev-OfJKE3/cargo-target` 执行 `cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib --no-default-features --features rust-snap7-driver services::local_delivery::tests -- --test-threads=1`，退出 0，22/22，50.74 秒。覆盖 QA1 两个确定性并发反例、QA2 10 秒未决成功及失败、阻塞期间在途回执与恢复、目标/来源在最终派发前变化、正常 pause/save、双 PLC 多 DB 真实 worker 的隔离随机回环 HTTP 和匹配回执。默认 sandbox 曾对合成回环绑定返回 EPERM，本次按授权对该测试作最小提权；未连接真实服务。测试 stdout 留存 `/private/tmp/daa013-r1-dev-OfJKE3/qa3-formal-delivery-tests.log`。Cargo 测试编译仍有既有 `empty_for_test` 一条 dead_code warning。
- 本次首次合入后，正式树 `node --test tests/facts-delivery.test.mjs` 退出 0，7/7，包含真实编译设置组件中 `storage_pending` 的中英文实际显示；`pnpm --config.verify-deps-before-run=false exec vue-tsc --noEmit` 及 `pnpm --config.verify-deps-before-run=false exec vite build --outDir /private/tmp/daa013-r1-dev-OfJKE3/qa2-formal-build --emptyOutDir` 均退出 0。Vite 保留已有依赖 PURE 注释和大 chunk 提示。该前端及测试文件与最终交付哈希相同，后续只改两个 Rust 文件。此前隔离 SQLite 17/17 的源码及测试在本次返工中未变；其旧库、完整来源增减及冻结材料证据保留于 QA1 节。
- 最终正式树 `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check` 退出 0；`CARGO_TARGET_DIR=/private/tmp/daa013-r1-dev-OfJKE3/cargo-target cargo build --locked --offline --manifest-path src-tauri/Cargo.toml --no-default-features --features rust-snap7-driver --bin aiis-data-acquisition-agent` 退出 0，无普通构建 Rust warning，未启动应用；`git diff --check` 退出 0。下表 14/14 由 `shasum -a 256 -c /private/tmp/daa013-r1-dev-OfJKE3/qa3-final-sha256.txt` 核对通过。

### 最终源码及指南 SHA-256

| 路径 | SHA-256 |
| --- | --- |
| `src/components/console/FactsDeliveryDialog.vue` | `1ddac4d8464dfae3fae0ebbde18c9c46800df49ba5e60b0e2fb6b9ddd25aa7bd` |
| `src/console/composables/useLocalAcquisitionConsole.ts` | `2067d4c4f1f4a0d39ff22d15be461f4898c3f41d8fa6b3d9c1b9afa282f2d439` |
| `src/services/factsDelivery.ts` | `115dc1d7fb6ae289331ff302e00f7f0e00b69aed1a2b12ccdf8f3a4ce946bed3` |
| `src/locales/en-US/common.json` | `f1828339abf86579b01bd1f6581578976799ee1189296f09d43efd2eff030744` |
| `src/locales/zh-CN/common.json` | `d174d0a695ebd1a259917cd4a41961c459b595754d637ebd3c5d2a99dcf8f285` |
| `src/styles/app.css` | `d73dd01040e20d22902198134598fa9b139e3c9335cdf791115122d5811fd9cb` |
| `src-tauri/src/domain/sample_upload.rs` | `ac0dac6e8e18048899b59a2eaae1bdc72ad3d906ee179fb0eb439101e75f860b` |
| `src-tauri/src/services/local_delivery.rs` | `212b6f898ab5c13eba8e0cc624666ce1fb6372c1de36f8e14cb6a53b50a1daf2` |
| `src-tauri/src/infrastructure/local_store/sample_upload.rs` | `82ee5e92829f128f69a7ce09768f4e5cb88ca1cceb34897936539a242c617951` |
| `tests/facts-delivery.test.mjs` | `eb0ed338fb58b0f52a2c6afed64f6a75b25f8c93f80ff4397c8a5d66eadd30f5` |
| `src-tauri/src/services/local_delivery_tests.rs` | `273b83da043e7ca4b01ec5185ba065bee33c83363f06e3b4564db4662808ad17` |
| `src-tauri/src/infrastructure/local_store/sample_upload_tests.rs` | `3f1ed2277fdb87e74bd1e28a960c89de3948ac6b5304b9d8de6558ea4042df8d` |
| `STAGE_C_GUIDE.md` | `4b6854fed2a742ef3efa4f7e2e1a45b57cb9eda144f7b8d21651d4ee99e3c982` |
| `STAGE_C_GUIDE.zh-CN.md` | `dda01608f7ee820cefe28e330cf07673cdcf593e626ccd6e6048bf0105ccbcc5` |

**精确交接**：请协调者安排新的 fresh-context Verification 对 DAA-013 r1、上述 HEAD 和最终 14 项工作树复核 QA2 失败、QA1 两个反例、锁顺序、在途回执与实际确认，独立记录结论。本节是 Development 自检与交接，不改变 QA2 `qa_failed`，亦不授予 Human Owner 最终验收。旧版二进制原生回退、Windows、真实 profile、实际后端/设备、MySQL、Docker、部署和发布仍未验证或授权。

本任务自有 `/private/tmp/daa013-r1-dev-OfJKE3`（候选、基线、构建与测试证据）及 Verification 自有 `/private/tmp/daa013-r1-qa2-Zmn9qT` 为 fresh Verification 复核暂保留；合成测试进程已结束，相关证据不再需要后由协调者确认归属和清理时点，不触碰真实配置、数据库、历史或其他任务资源。

## ARCH-ACQ-004 R4-QA-03 指南及确认提示返工 developer_handoff

ARCH-ACQ-004 r4 的 fresh-context Verification 将 [R4-QA-03](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md#失败与返回项) 中双语 Stage C 指南交 DAA-013 归属方修正；Human Owner 已授权由该会话转交。协调者另交办两条实际使用的确认提示同步纠错。本次仍按已批准 [DAA-013 r1 §3](spec.md#3-实施范围与风险) 的当前指南、双语 locale 与定向测试 allowlist，未扩展规格，工作树 HEAD 为 `fd999224a8756feda314a33148304b4bf3461876`，未暂存或提交。只改以下五项及本 `tasks.md`；未改 `spec.md`、`checklist.md`、Rust、后端、数据库或其他任务文件。协调者合入前核对五项和本记录的起点摘要，并确认 15191、现有 dev 双库和正式 DAA 二进制无打开句柄。

双语 Stage C 现行步骤按目标实际采用版本分支：已采用 r3/r4 单表时，每 PLC 登记 `plcId`、`instanceId`、`sourceGeneration`、`sourceType`；类型仅标注展示，样本 POST 准入匹配前三项，`dbNumber` 仍为样本字段和查询筛选项，不登记 DB 读写清单；符合查询条件的已登记 PLC 事实可读。尚未切换的 r2 目标继续核对已有 DB 上报及读取授权。中英文维护手册链接分别指向现有的单表和冻结 r2 前驱标题；不宣称 r4 完成最终验收或实际环境已切换。两条真实确认提示按同样版本规则说明，并保留完整本地实例 / PLC / DB / 代次列表、原始同目标核对和回执条件；未动无调用的 `sourceDbMismatch` 旧键。

以下为本轮变更前后 SHA-256，before 均是 DAA-013 QA3 所验证候选中的对应值。

| 路径 | 变更前 SHA-256 | 本次交付 SHA-256 |
| --- | --- | --- |
| `STAGE_C_GUIDE.md` | `4b6854fed2a742ef3efa4f7e2e1a45b57cb9eda144f7b8d21651d4ee99e3c982` | `2bfa71a94cc223a3d37c0564743528222010c94a175166dd50d972ae587787ea` |
| `STAGE_C_GUIDE.zh-CN.md` | `dda01608f7ee820cefe28e330cf07673cdcf593e626ccd6e6048bf0105ccbcc5` | `a5637f079081edf7a1441148f99cfd4d93deaebf5dc13b2509dad0a13d393d73` |
| `src/locales/en-US/common.json` | `f1828339abf86579b01bd1f6581578976799ee1189296f09d43efd2eff030744` | `aaeefe870271399796b34c5c9c336cd3c21190612ee398dd11926bde987eb4ca` |
| `src/locales/zh-CN/common.json` | `d174d0a695ebd1a259917cd4a41961c459b595754d637ebd3c5d2a99dcf8f285` | `14b0e5f0b8d71b447180f3d5624890cf90876d54b81a7c4436901cf20e538f6f` |
| `tests/facts-delivery.test.mjs` | `eb0ed338fb58b0f52a2c6afed64f6a75b25f8c93f80ff4397c8a5d66eadd30f5` | `53e206910701d2fe5f75bbb8403f22e6fbe3cc67d28b07203e4cf0967a27da36` |

### 本轮 DEV self-check

- 先对实际 composable 与合成 IPC/确认对话框添加回归断言，旧文案运行 `node --test --test-name-pattern='start and resume confirm' tests/facts-delivery.test.mjs` 退出 1，因旧文本要求 DB 均已登记；更正后隔离候选与正式树分别 `node --test tests/facts-delivery.test.mjs` 退出 0，7/7。实际代码路径分别执行中文开始、英文继续及两种语言的同目标重绑，核对两台 PLC 的 DB21/DB22、目标、合同、完整来源和版本随 IPC 保留，且单表/旧 r2 文案及占位符均正确。该测试使用确认对话框和 IPC 替身，未运行原生界面。双语 `common.json` 共 664 个叶键一致；程序化比较确认每种语言只修改上述两个提示键，`sourceDbMismatch` 未变。
- 隔离候选排除 `.env*`、`.local`、Rust 目录和既有构建产物，使用项目现有依赖与锁定 pnpm；`pnpm --config.verify-deps-before-run=false build` 退出 0。正式树 `pnpm --config.verify-deps-before-run=false exec vue-tsc --noEmit` 和 `pnpm --config.verify-deps-before-run=false exec vite build --outDir /private/tmp/daa013-r4-guides-HCwgxt/formal-dist --emptyOutDir` 均退出 0。合入后的 DAA `src` 和共享 `console-ui/src/ui` 与隔离构建源码逐文件一致，两个构建产物 `diff -qr` 一致。Vite 保留既有 VueUse PURE 注释和大 chunk 提示；未启动 dev server。
- `python3 /private/tmp/daa013-r4-guides-HCwgxt/check_guides.py before` 在旧指南报告 46 个本地链接、21 个片段、1 个缺失，退出 1；缺失即中文 r2 迁移标题。更正后用 `candidate` 和 `formal` 各运行一次，均退出 0：48 个本地链接、24 个标题或显式锚点，缺失 0，代码围栏闭合。人工逐项比较中英单表/旧版登记、POST、读回及采用边界。
- DAA-008 历史后缀从历史标题至文件末尾逐字节相同：英文 23110 字节，SHA-256 `3b4c17fae74afb2b11df51d6491e39025180fab0bf83650beeeacac7e88327fc`；中文 20602 字节，SHA-256 `d3fb8a87caf7107eecff4ff6fb74048a87db44b5f6639e2eac179936a7f0b7cc`。正式树 `git diff --check` 退出 0；本记录链接和尾随空白另作静态检查。

### 本次交接的完整源码及指南 SHA-256

| 路径 | SHA-256 |
| --- | --- |
| `src/components/console/FactsDeliveryDialog.vue` | `1ddac4d8464dfae3fae0ebbde18c9c46800df49ba5e60b0e2fb6b9ddd25aa7bd` |
| `src/console/composables/useLocalAcquisitionConsole.ts` | `2067d4c4f1f4a0d39ff22d15be461f4898c3f41d8fa6b3d9c1b9afa282f2d439` |
| `src/services/factsDelivery.ts` | `115dc1d7fb6ae289331ff302e00f7f0e00b69aed1a2b12ccdf8f3a4ce946bed3` |
| `src/locales/en-US/common.json` | `aaeefe870271399796b34c5c9c336cd3c21190612ee398dd11926bde987eb4ca` |
| `src/locales/zh-CN/common.json` | `14b0e5f0b8d71b447180f3d5624890cf90876d54b81a7c4436901cf20e538f6f` |
| `src/styles/app.css` | `d73dd01040e20d22902198134598fa9b139e3c9335cdf791115122d5811fd9cb` |
| `src-tauri/src/domain/sample_upload.rs` | `ac0dac6e8e18048899b59a2eaae1bdc72ad3d906ee179fb0eb439101e75f860b` |
| `src-tauri/src/services/local_delivery.rs` | `212b6f898ab5c13eba8e0cc624666ce1fb6372c1de36f8e14cb6a53b50a1daf2` |
| `src-tauri/src/infrastructure/local_store/sample_upload.rs` | `82ee5e92829f128f69a7ce09768f4e5cb88ca1cceb34897936539a242c617951` |
| `tests/facts-delivery.test.mjs` | `53e206910701d2fe5f75bbb8403f22e6fbe3cc67d28b07203e4cf0967a27da36` |
| `src-tauri/src/services/local_delivery_tests.rs` | `273b83da043e7ca4b01ec5185ba065bee33c83363f06e3b4564db4662808ad17` |
| `src-tauri/src/infrastructure/local_store/sample_upload_tests.rs` | `3f1ed2277fdb87e74bd1e28a960c89de3948ac6b5304b9d8de6558ea4042df8d` |
| `STAGE_C_GUIDE.md` | `2bfa71a94cc223a3d37c0564743528222010c94a175166dd50d972ae587787ea` |
| `STAGE_C_GUIDE.zh-CN.md` | `a5637f079081edf7a1441148f99cfd4d93deaebf5dc13b2509dad0a13d393d73` |

**精确交接**：DAA-013 r1 QA3 原 `qa_passed` 仅针对改动前的 14 项候选，保留其证据和结论，不直接外推到本轮文件；请协调者安排新的 fresh-context Verification 独立复核上述指南、确认提示、双语等价、链接及历史字节，并将精确候选交 ARCH-ACQ-004 r4 后续联合验证。ARCH-ACQ-004 r4 当前 `qa_failed` 及其余返回项按该任务记录处理，Human Owner 最终验收与实际环境采用仍由各自授权决定。本轮未运行原生 UI、应用、容器、后端、数据库、profile 或设备；未重跑不相关的 Rust/MySQL 测试。

本轮自有 `/private/tmp/daa013-r4-guides-HCwgxt` 保存五项变更前副本、历史后缀、隔离前端源码与现有依赖、静态检查脚本和构建结果，未复制真实 `.env` 或 `.local`，没有运行中服务。为 fresh Verification 暂留，完成且无后续证据依赖后由协调者核对归属并清理；不影响用户环境和其他任务资源。

## 确认提示面向使用者的精简及 developer_handoff

在上节交接后的独立验证之前，协调者要求进一步精简两项确认文案。本次仍属已批准 DAA-013 r1 locale 与定向测试范围，仅修改中英文 `delivery.confirmRegistration`、`delivery.confirmSameTarget` 的对应文字及现有测试断言。提示要求核对实例 / PLC / 来源代次与目标登记一致，说明 DB 是本地样本信息，并按目标后端规则核对是否允许上报；界面不显示单表或旧 r2 版本术语。完整本地来源列表、占位符和实际 IPC 保留，同目标的相同逻辑 provider 与数据库、原身份原字节及可靠回执条件逐字保留。具体版本分支继续在前述双语指南说明；未增加界面开关或后端检测。

本次以 `/private/tmp/daa013-r4-guides-HCwgxt` 的同一隔离候选完成，合入前协调者确认正式三项及 `tasks.md` 摘要不变，15191、dev 双库和正式 DAA 二进制均无打开句柄。以下为精简前和本次最终文件 SHA-256；之前指南和其历史后缀未改，其他 11 项交付文件亦与上节清单一致。

| 路径 | 精简前 SHA-256 | 本次交付 SHA-256 |
| --- | --- | --- |
| `src/locales/en-US/common.json` | `aaeefe870271399796b34c5c9c336cd3c21190612ee398dd11926bde987eb4ca` | `6df9455806f16c264fb7a978fe277465431c7bdceedb5c39fe2b015ef015f7cc` |
| `src/locales/zh-CN/common.json` | `14b0e5f0b8d71b447180f3d5624890cf90876d54b81a7c4436901cf20e538f6f` | `942a8dd5c89cbea35fca1d61cf2ce4c17f16bc06e7a48bc1b2edb6afb93066fd` |
| `tests/facts-delivery.test.mjs` | `53e206910701d2fe5f75bbb8403f22e6fbe3cc67d28b07203e4cf0967a27da36` | `11622c0f29cdaca4b4753029010eef794eb3c2e5ccd51c0b419dfcab7aa2d56c` |

### 本次 DEV self-check

- 隔离副本先调整实际 composable 确认行为断言，旧版产品提示的 `node --test --test-name-pattern='start and resume confirm' tests/facts-delivery.test.mjs` 按预期退出 1；精简后隔离与正式树 `node --test tests/facts-delivery.test.mjs` 均退出 0，7/7。测试覆盖中英文开始/继续与同目标重绑，保留两 PLC/DB 来源、目标、合同、设置版本和原 IPC 参数；验证身份登记、按后端规则核对 DB 上报许可，且不显示单表或 r2 术语。两份 locale 共 664 个叶键对称，改变的只有这两个 key，占位符未变，旧 `sourceDbMismatch` 未变。
- 对比精简前后两种语言的两项提示，确认除目标说明句以外全文逐字不变，并核对同一 provider 和数据库、原身份原字节及可靠回执均保留。隔离候选 `pnpm --config.verify-deps-before-run=false build` 退出 0；正式树 `pnpm --config.verify-deps-before-run=false exec vue-tsc --noEmit` 和 `pnpm --config.verify-deps-before-run=false exec vite build --outDir /private/tmp/daa013-r4-guides-HCwgxt/clarity-formal-dist --emptyOutDir` 均退出 0。正式 `src` 与隔离候选逐文件一致，两个构建产物 `diff -qr` 一致；Vite 仍有既有 VueUse PURE 注释及大 chunk 提示。`git diff --check` 退出 0；未启动 dev 或访问 profile、后端、设备。

### 精简后的完整源码及指南 SHA-256

| 路径 | SHA-256 |
| --- | --- |
| `src/components/console/FactsDeliveryDialog.vue` | `1ddac4d8464dfae3fae0ebbde18c9c46800df49ba5e60b0e2fb6b9ddd25aa7bd` |
| `src/console/composables/useLocalAcquisitionConsole.ts` | `2067d4c4f1f4a0d39ff22d15be461f4898c3f41d8fa6b3d9c1b9afa282f2d439` |
| `src/services/factsDelivery.ts` | `115dc1d7fb6ae289331ff302e00f7f0e00b69aed1a2b12ccdf8f3a4ce946bed3` |
| `src/locales/en-US/common.json` | `6df9455806f16c264fb7a978fe277465431c7bdceedb5c39fe2b015ef015f7cc` |
| `src/locales/zh-CN/common.json` | `942a8dd5c89cbea35fca1d61cf2ce4c17f16bc06e7a48bc1b2edb6afb93066fd` |
| `src/styles/app.css` | `d73dd01040e20d22902198134598fa9b139e3c9335cdf791115122d5811fd9cb` |
| `src-tauri/src/domain/sample_upload.rs` | `ac0dac6e8e18048899b59a2eaae1bdc72ad3d906ee179fb0eb439101e75f860b` |
| `src-tauri/src/services/local_delivery.rs` | `212b6f898ab5c13eba8e0cc624666ce1fb6372c1de36f8e14cb6a53b50a1daf2` |
| `src-tauri/src/infrastructure/local_store/sample_upload.rs` | `82ee5e92829f128f69a7ce09768f4e5cb88ca1cceb34897936539a242c617951` |
| `tests/facts-delivery.test.mjs` | `11622c0f29cdaca4b4753029010eef794eb3c2e5ccd51c0b419dfcab7aa2d56c` |
| `src-tauri/src/services/local_delivery_tests.rs` | `273b83da043e7ca4b01ec5185ba065bee33c83363f06e3b4564db4662808ad17` |
| `src-tauri/src/infrastructure/local_store/sample_upload_tests.rs` | `3f1ed2277fdb87e74bd1e28a960c89de3948ac6b5304b9d8de6558ea4042df8d` |
| `STAGE_C_GUIDE.md` | `2bfa71a94cc223a3d37c0564743528222010c94a175166dd50d972ae587787ea` |
| `STAGE_C_GUIDE.zh-CN.md` | `a5637f079081edf7a1441148f99cfd4d93deaebf5dc13b2509dad0a13d393d73` |

**精确交接**：请以 DAA-013 r1、正式工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876`、上述 14 项最终摘要和本记录为对象，安排新的 fresh-context Verification；原 QA3 结论仅适用于更早候选。ARCH-ACQ-004 r4 的独立验证与 Human Owner 最终验收按各自任务记录处理。临时根及其保留、清理条件沿上节，新增的隔离和正式构建输出仅供本次复核，不含真实 `.env` 或 `.local`。

## QA4 英文接入按钮返工与 developer_handoff

DAA-013 r1 的 fresh-context Verification 记录 `qa_failed`，将 [F-DAA013-QA4-001](checklist.md#f-daa013-qa4-001--英文单表接入步骤的-web-控件名称与实际界面不符) 返回 Development；QA4 验证时的 `checklist.md` SHA-256 为 `b5a2926806b26a0aaa2c203989b622da35c2df6a07f2c1f53cee42f68ad5b8e3`。本次仍按获批 r1 第 3 节的英文 Stage C 当前接入范围，仅修改 `STAGE_C_GUIDE.md` 的两处操作文字及追加本记录，未改中文指南、产品源码、spec 或 checklist。QA4 原失败与其他验证事实保留；本轮自检不代替独立 verdict。

r4 实际 Web 表格行按钮及弹窗标题的 key 为 `sourceConfig.parameters`，英文为 **Connection parameters**；弹窗复制按钮 key 为 `sourceConfig.copy`，英文为 **Copy parameters**。现行页面 `frontend-js/src/app/acquisition-data/views/sources/index.vue` SHA-256 `6f3c8f34b2b7b7398c935a488492958a0077e4eabc4dd4008a73be25810421c0`，其英文 locale SHA-256 `be96ed15affcdfdfb937db877dd5f1886b1f92aaa535d53dce9e479c27fda9f0`。英文指南的 r3/r4 分支现明确先打开该行 **Connection parameters**，再点 **Copy parameters** 复制三项 JSON。

旧 r2 分支也改为这两个按钮名称：只读核对 `/private/tmp/arch-acq004-r3-dev.0fxOzki5/pre-integration/frontend-js/src/app/acquisition-data/` 的冻结前驱页面和英文 locale，其 SHA-256 分别为 `4d3a03a44a838859f8eba63ace59c81a6915d93608c975dd6f0b779f49ae701c`、`d1580d5c020c3e31b0bc4bb248c8176f214acf79004fd10de5bdd1576c242381`，均与 [ARCH-ACQ-004 r2 历史交接](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/tasks.md#qa6-文档返工与-development-handoff)的文件清单一致；页面实际绑定相同两个 key，英文值也相同。本次是冻结源码与既有摘要核对，不声称重新运行旧 r2 原生界面。两份无私密配置的前驱源码副本暂存于 `/private/tmp/daa013-r4-guides-HCwgxt/qa4-r2-frontend/` 供独立复核。

英文指南起点 SHA-256 `2bfa71a94cc223a3d37c0564743528222010c94a175166dd50d972ae587787ea`，最终 `15ccd0f8a6d9c5d250b2588204db90a3f33af8094d812cfb25396186b376a235`。协调者在 QA4 固定验前清单后核对指南、tasks、checklist 摘要，Development 核对此前交接 14 项后合入；其余 13 项均保持 QA4 候选字节。

### QA4 返工 DEV self-check

- 仅有两行英文指南差异。定向 Python 检查两种版本分支所列名称与各自实际页面绑定及 locale 一致，并确认单表四字段、无 DB 清单及旧 r2 读写授权描述保留。正式指南与隔离候选 `cmp -s` 退出 0。
- `python3 /private/tmp/daa013-r4-guides-HCwgxt/check_guides.py candidate` 和 `... formal` 均退出 0：48 个本地链接、24 个标题或显式片段均有效，代码围栏闭合。英文 DAA-008 历史后缀逐字节不变，23110 字节，SHA-256 `3b4c17fae74afb2b11df51d6491e39025180fab0bf83650beeeacac7e88327fc`；中文指南整体未变。`git diff --check` 退出 0。
- 本次文档静态核验未启动应用、服务或容器，未访问数据库、profile、设备，也未重跑与此次纯文案变更无关的构建或测试。未直接运行旧 r2 产品或原生 Tauri；实际环境采用与联合链路按各自任务及授权处理。

### QA4 返工后的完整源码及指南 SHA-256

| 路径 | SHA-256 |
| --- | --- |
| `src/components/console/FactsDeliveryDialog.vue` | `1ddac4d8464dfae3fae0ebbde18c9c46800df49ba5e60b0e2fb6b9ddd25aa7bd` |
| `src/console/composables/useLocalAcquisitionConsole.ts` | `2067d4c4f1f4a0d39ff22d15be461f4898c3f41d8fa6b3d9c1b9afa282f2d439` |
| `src/services/factsDelivery.ts` | `115dc1d7fb6ae289331ff302e00f7f0e00b69aed1a2b12ccdf8f3a4ce946bed3` |
| `src/locales/en-US/common.json` | `6df9455806f16c264fb7a978fe277465431c7bdceedb5c39fe2b015ef015f7cc` |
| `src/locales/zh-CN/common.json` | `942a8dd5c89cbea35fca1d61cf2ce4c17f16bc06e7a48bc1b2edb6afb93066fd` |
| `src/styles/app.css` | `d73dd01040e20d22902198134598fa9b139e3c9335cdf791115122d5811fd9cb` |
| `src-tauri/src/domain/sample_upload.rs` | `ac0dac6e8e18048899b59a2eaae1bdc72ad3d906ee179fb0eb439101e75f860b` |
| `src-tauri/src/services/local_delivery.rs` | `212b6f898ab5c13eba8e0cc624666ce1fb6372c1de36f8e14cb6a53b50a1daf2` |
| `src-tauri/src/infrastructure/local_store/sample_upload.rs` | `82ee5e92829f128f69a7ce09768f4e5cb88ca1cceb34897936539a242c617951` |
| `tests/facts-delivery.test.mjs` | `11622c0f29cdaca4b4753029010eef794eb3c2e5ccd51c0b419dfcab7aa2d56c` |
| `src-tauri/src/services/local_delivery_tests.rs` | `273b83da043e7ca4b01ec5185ba065bee33c83363f06e3b4564db4662808ad17` |
| `src-tauri/src/infrastructure/local_store/sample_upload_tests.rs` | `3f1ed2277fdb87e74bd1e28a960c89de3948ac6b5304b9d8de6558ea4042df8d` |
| `STAGE_C_GUIDE.md` | `15ccd0f8a6d9c5d250b2588204db90a3f33af8094d812cfb25396186b376a235` |
| `STAGE_C_GUIDE.zh-CN.md` | `a5637f079081edf7a1441148f99cfd4d93deaebf5dc13b2509dad0a13d393d73` |

**精确交接**：请协调者以 DAA-013 r1、工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876`、上述 14 项最终摘要及本记录安排新的 fresh-context Verification。QA4 `qa_failed` 及 QA3 先前候选的结果各保留原边界，Human Owner 最终验收待定。自有隔离根 `/private/tmp/daa013-r4-guides-HCwgxt` 继续供独立核对，相关证据与源码副本无服务依赖；独立核对完成且无后续依赖时由协调者确认归属后清理，不触及其他任务资源。

## 上报确认可读性修正与 developer_handoff

Human Owner 反馈 DAA-013 r1 开始上报确认在最小窗口中难以阅读。按获批 r1 的 R03/AC01 现有确认范围，Development 将开始、继续及同目标重绑的确认改为带标题的分区：独立目标与合同、逐来源的实例 ID／上报 PLC ID／DB／来源代次，以及简短队列或原身份原字节重试和可靠回执说明。重绑保留新旧地址、同一逻辑目标及数据库的核对提示。来源直接逐项读取实际 `material.sources`，不拼接再解析标识，也不为历史来源猜测名称；确认后的设置版本、完整来源数组和 IPC 参数保持原样。其他简单确认不变。

合入前协调者确认下表 14 项起始摘要、任务文档，以及 15191、dev 双库、正式 DAA 可执行文件的句柄和进程状态；Development 逐项复核后只合入以下 5 项。起点 `tasks.md` SHA-256 `4af58dd5542fbbdd0b7b393a742a808803a54a8694c5931b19f579e72d1ab797`，`checklist.md` SHA-256 `971e5381d45997a19187184539fc4a3e187c2b25a16fed4cceb171fbd97e42e8`，获批 spec SHA-256 `fc9d5deba6245f4f0c457bc6ee26673298361f08be60b107d6b3d09704a82bb8`。未修改 spec、checklist 或其他任务文件。

| 本次文件 | 合入前 SHA-256 | 合入后 SHA-256 |
| --- | --- | --- |
| `src/console/composables/useLocalAcquisitionConsole.ts` | `2067d4c4f1f4a0d39ff22d15be461f4898c3f41d8fa6b3d9c1b9afa282f2d439` | `a2e0c762a725596be65d120338ba5d976d2d417c54f6954648b9897844ad6f5a` |
| `src/styles/app.css` | `d73dd01040e20d22902198134598fa9b139e3c9335cdf791115122d5811fd9cb` | `deea6bf71eda3cb6fe948c7ffaf96ecc537a33c6002995e34c9e49b6314a7f9e` |
| `src/locales/en-US/common.json` | `6df9455806f16c264fb7a978fe277465431c7bdceedb5c39fe2b015ef015f7cc` | `90790e07569962bc1d0c0029381daed3e45a33858cdb0c5ececca52b83f17a0f` |
| `src/locales/zh-CN/common.json` | `942a8dd5c89cbea35fca1d61cf2ce4c17f16bc06e7a48bc1b2edb6afb93066fd` | `6598f86d54df4b3d7abcae737bfdcc861ac3c7643571efc04a67fa1cd7172609` |
| `tests/facts-delivery.test.mjs` | `11622c0f29cdaca4b4753029010eef794eb3c2e5ccd51c0b419dfcab7aa2d56c` | `b46d950a50099fe4545f201971d6cdcb857d4a2abc30f3314d036ccae7fd52d5` |

### 本次 DEV self-check

- 隔离副本先用新断言运行旧确认实现，因未提供结构化内容按预期退出 1；修正后隔离及正式树 `node --test tests/facts-delivery.test.mjs` 均退出 0，7/7。定向测试使用真实 Vue VNode、服务适配与合成 IPC，覆盖中英开始／继续／重绑的确认和取消、三条来源含旧 unknown 样本和含斜杠的 128 字节标识、精确参数、过期拒绝及双语键对称。
- 隔离 `pnpm --config.verify-deps-before-run=false build` 退出 0；正式树 `pnpm --config.verify-deps-before-run=false exec vue-tsc --noEmit` 与 `pnpm --config.verify-deps-before-run=false exec vite build --outDir /private/tmp/daa013-r1-confirm-NV212D/formal-dist --emptyOutDir` 均退出 0，正式构建与隔离产物 `diff -qr` 退出 0。构建仅有既有 VueUse PURE 注释和大 chunk 提示。正式 5 项与候选 SHA 一致，`git diff --check` 对这 5 项退出 0。
- 使用真实 Element Plus 与私有合成 IPC 的本地静态页面，在 960×640 headless Chrome 检查中文浅色开始及英文暗色重绑。首次检查发现 Element Plus 容器居中导致目标顶部裁切，隔离中改为拉伸后复验：目标首屏可见，长来源可用键盘 End 滚至底部，按钮持续可见，Esc 和取消无控制 IPC；英文重绑确认只产生一次合成 IPC，保留原 sampleId、旧 URL、设置版本及三条完整来源。截图保存在本轮临时根 `confirm-zh-light.png`、`rebind-en-dark.png` 和 `rebind-en-dark-scrolled.png`；另应协调者请求用虚构的单台 PLC 和普通长度标识生成 `confirm-zh-one-plc.png`。默认沙箱对回环监听及 Chrome 启动分别拒绝，针对自有回环静态服务和临时浏览器提权后成功；两者均已结束。静态 fixture 的 favicon 请求曾返回 404，不影响应用或确认内容。
- 未运行原生 Tauri、实际上报、设备或后端，未读取或写入真实 profile、数据库、环境密钥；未重跑与本次前端修正无关的 Rust/MySQL 测试。截图和合成渲染不代替独立 QA 或 Human Owner 原生验收。

### 本次完整源码及指南 SHA-256

| 路径 | SHA-256 |
| --- | --- |
| `src/components/console/FactsDeliveryDialog.vue` | `1ddac4d8464dfae3fae0ebbde18c9c46800df49ba5e60b0e2fb6b9ddd25aa7bd` |
| `src/console/composables/useLocalAcquisitionConsole.ts` | `a2e0c762a725596be65d120338ba5d976d2d417c54f6954648b9897844ad6f5a` |
| `src/services/factsDelivery.ts` | `115dc1d7fb6ae289331ff302e00f7f0e00b69aed1a2b12ccdf8f3a4ce946bed3` |
| `src/locales/en-US/common.json` | `90790e07569962bc1d0c0029381daed3e45a33858cdb0c5ececca52b83f17a0f` |
| `src/locales/zh-CN/common.json` | `6598f86d54df4b3d7abcae737bfdcc861ac3c7643571efc04a67fa1cd7172609` |
| `src/styles/app.css` | `deea6bf71eda3cb6fe948c7ffaf96ecc537a33c6002995e34c9e49b6314a7f9e` |
| `src-tauri/src/domain/sample_upload.rs` | `ac0dac6e8e18048899b59a2eaae1bdc72ad3d906ee179fb0eb439101e75f860b` |
| `src-tauri/src/services/local_delivery.rs` | `212b6f898ab5c13eba8e0cc624666ce1fb6372c1de36f8e14cb6a53b50a1daf2` |
| `src-tauri/src/infrastructure/local_store/sample_upload.rs` | `82ee5e92829f128f69a7ce09768f4e5cb88ca1cceb34897936539a242c617951` |
| `tests/facts-delivery.test.mjs` | `b46d950a50099fe4545f201971d6cdcb857d4a2abc30f3314d036ccae7fd52d5` |
| `src-tauri/src/services/local_delivery_tests.rs` | `273b83da043e7ca4b01ec5185ba065bee33c83363f06e3b4564db4662808ad17` |
| `src-tauri/src/infrastructure/local_store/sample_upload_tests.rs` | `3f1ed2277fdb87e74bd1e28a960c89de3948ac6b5304b9d8de6558ea4042df8d` |
| `STAGE_C_GUIDE.md` | `15ccd0f8a6d9c5d250b2588204db90a3f33af8094d812cfb25396186b376a235` |
| `STAGE_C_GUIDE.zh-CN.md` | `a5637f079081edf7a1441148f99cfd4d93deaebf5dc13b2509dad0a13d393d73` |

**精确交接**：DAA-013 r1，正式工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876`，以上 14 项摘要及本记录，请协调者安排 fresh-context Verification。QA5 的 `qa_passed` 仅对应本轮修改前候选，不外推至本次修正；Human Owner 最终验收待定。自有 `/private/tmp/daa013-r1-confirm-NV212D` 含无 `.env`／`.local` 的隔离源码、合成 fixture、截图和构建产物，供用户及独立验证复核；不含运行服务，在复核结束且无后续依赖后由协调者确认归属再清理。

