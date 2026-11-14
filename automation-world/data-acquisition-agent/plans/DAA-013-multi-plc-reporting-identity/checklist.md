Task ID: DAA-013
Revision: r1
Status: qa_passed
Owner Role: Verification
Allowed Writers: Verification, Human Owner
Handoff: QA6 通过上报确认可读性增量。DAA-013 r1 精确候选交 Human Owner 最终验收。
Workflow Mode: STD
Fresh Context: yes
Spec SHA-256: `fc9d5deba6245f4f0c457bc6ee26673298361f08be60b107d6b3d09704a82bb8`
Development handoff SHA-256: `92747a78a4f04418134d858e112bfb495bf08f8e540ca931a0d00673dbb23c4f`
Updated: 2026-11-13 Asia/Shanghai

# DAA-013 r1 独立验证 QA1

本节原交接 SHA-256 为 `4d08209889600f94f327443a74c4464bfc964367e7f753bfe12ef99ffbb291a6`。

**结论：`qa_failed`。并发保存已提交并停传后，旧设置版本的开始确认仍可重新启传，worker 会向旧目标发送。同目标重绑也会在完整来源集合变化后接受旧确认。**

## 验证对象

- 正式源码为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 工作树，HEAD `fd999224a8756feda314a33148304b4bf3461876`。Verification 在独立上下文复核批准和交接、根及最近作用域规则、实际差异与测试。交接表 14 项正式文件和 Development 只读基线的 before/after SHA-256 均匹配。未发现本任务新增 DDL、profile 版本、锁文件、Tauri 配置或 IPC adapter 变更。并行 ARCH-ACQ-004 及其他工作树差异按 Development 起点区分。 [批准规格](spec.md) · [精确交接及文件哈希](tasks.md)
- macOS 15.7.7 arm64，Node 22.19.0，pnpm 11.11.0，Cargo/rustc 1.89.0。项目生产构建、Rust SQLite 与网络测试使用独立源码副本，排除私有 env、`.local`、既有 profile 和构建产物。QA 只向正式树写入本文件。

## F-DAA013-QA1-001 · 旧确认可在保存之后启传并发送到旧地址

对应 R02 停传语义、R03 过期确认须拒绝、AC02。旧实现同样存在该确认窗口，属于本轮验收覆盖的启传路径。普通界面单 owner 的 `busy` 会串行界面动作，具名 IPC 服务入口仍可遇到并发。

1. 真实合成 runtime4 SQLite 保存目标 `http://127.0.0.1:38117`，有两个待传 DB 样本。发起使用该设置版本与完整来源集合的 `start`，在确认比较成功之后、取得 `delivery` 锁之前暂停。临时副本仅加 `cfg(test)` 调度屏障，产品判断、事务和 worker 逻辑保持原样。
2. 另一线程只修改目标为 `http://127.0.0.1:38118`，保存成功，读取 `running=false`。本机 PLC / DB / 实例 / 代次集合相同。
3. 放行旧 Start。预期拒绝旧确认并零派发。实际返回 `Ok(running=true, origin=http://127.0.0.1:38118/api/v1/integration/plc-facts/samples)`，worker 的合成 Transport 捕获 POST 目标 `http://127.0.0.1:38117/api/v1/integration/plc-facts/samples`。该复现使用传输替身，未连接任何端口。设置读取和比对先于锁，随后控制器写入旧目标，worker 只对照来源集合，来源未变时继续。 [确认与锁](../../src-tauri/src/services/local_delivery.rs#L160) · [启传状态](../../src-tauri/src/services/local_delivery.rs#L231) · [worker 核对](../../src-tauri/src/services/local_delivery.rs#L255)

复现命令在 QA 根 `race/automation-world/data-acquisition-agent` 执行。退出码 101，1 项失败，日志含旧目标、新目标与返回值。

```sh
cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib qa_start_confirmation_must_not_dispatch_after_concurrent_settings_save -- --nocapture
```

## F-DAA013-QA1-002 · 同目标重绑接受已过期的完整来源确认

对应 R03 同目标核对使用完整来源集合、R04 显式重绑条件。用真实合成 runtime4 SQLite 将 A 的样本置为 unknown，当前设置为新目标，待重绑样本仍持有旧目标。发起同目标重绑，在 Service 比对设置版本和 4 条完整来源之后、提交 SQLite 前使用测试屏障暂停。激活配置移除没有待传样本的 B，完整来源从 4 条降为 2 条，设置版本相同，A 样本身份仍在其中。放行后预期拒绝过期确认并保留原目标。实际返回 `Ok`，A 样本目标从 `http://127.0.0.1:38117/api/v1/integration/plc-facts/samples` 改成 `http://127.0.0.1:38118/api/v1/integration/plc-facts/samples`。重绑没有启动 worker 或发起网络请求。SQLite 写入复核了设置版本、URL 和目标样本是否在传入集合内，未复核当前完整来源。 [Service 复核](../../src-tauri/src/services/local_delivery.rs#L67) · [SQLite 写入复核](../../src-tauri/src/infrastructure/local_store/sample_upload.rs#L336)

同一 QA 临时副本执行以下命令。退出码 101，1 项失败，日志含 `4 -> 2`、旧确认返回值和写入后的目标。首次合成测试编译遇到内部 fixture 可见性限制，临时副本仅调整 `cfg(test)` 下的 fixture 可见性后通过编译并复现。

```sh
cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib qa_rebind_refuses_stale_complete_source_confirmation -- --nocapture
```

## 逐项证据

| 验收 | 结果 | QA 证据 |
| --- | --- | --- |
| AC01 逐台配置与布局 | 通过 | IAB 中实际生产构建全壳使用合成 Tauri IPC，从「配置中心 → 上报与存储 → 上报设置」进入。960 × 640 中英文均有紧凑逐行输入。两个同名 PLC 分别显示 `local-a / DB21`、`local-b / DB22, DB23`；选择 B 的粘贴按钮时提示明确显示 `local-b`。A 手填三项，各恰为 128 UTF-8 字节，含中文、大小写和末尾可辨认字符。输入聚焦后可用 End 查看末尾，英文 ASCII 字段横向滚至 1023 px；页面宽度 960 px，设置弹窗宽 900 px。B 的三项 JSON 与附带 `dbNumbers:[99]` 的旧 JSON 均可填入，DB 仍是 DB22/23。失败粘贴不改两行，部分填写提示本机 ID，重复 PLC ID 禁止保存，关闭取消后重开保留旧值。随后中英文实际保存，重开核对完整身份；不活动 C 保留原三项和空 DB。英文取消确认后仍停止，英文和中文确认后显示可暂停。确认包含 A/DB21、B/DB22/23、历史/DB24，中文确认弹窗内容滚动高度 600 px、可见 504 px，按钮可用。 |
| AC02 同异实例、持久化与确认 | **失败** | 合成 SQLite 验证两个不同实例、不同 PLC 共用实例和代次、单行编辑、暂不活动绑定、重开、旧代次换实例拒绝、重复 PLC、过期 CAS 拒绝。真实回环中普通时序的旧版本、缺来源和错实例确认均拒绝；保存本身零派发。并发时序见 F-DAA013-QA1-001、F-DAA013-QA1-002。 |
| AC03 多来源逐样本回执 | 通过 | 真实 Rust worker 和 SQLite 接隔离回环 HTTP。2 台 PLC 各 2 个 DB，共 4 个独立样本，5 次逐样本 POST。核对对应实例、PLC、DB、代次、样本 ID、正序号和确认材料。第一份错实例回执进入 unknown，以相同原字节重试，最后 4 个样本均取得有效匹配回执。定向账本测试覆盖错样本/旧尝试回执；未绑定轮保持本地。 |
| AC04 旧库与冻结材料 | 历史保全通过，重绑失败 | SQLite 定向测试 16/16。旧合法共用实例两绑定直接读回；合成旧周期覆盖无标记前驱、全空仅本地、有标记与未冻结待传、冻结未发送、unknown、已确认。比较 8 条样本原文、标识、时间、序号、采样配置上下文和 3 条投递账本及尝试记录，修改设置与重开后相同。旧轮开始时捕获旧身份，后续新轮使用新绑定。runtime2/3 各本地采集 2 个 DB、保持版本并拒绝 v2 开始。等效旧全检要求共享实例匹配代次，在混合实例和空共享值下拒绝；新程序可重开且保全数据。实际旧 SFC 编译并运行旧 save，捕获透传 `identityMode` 的两种请求，SHA-256 `a8bc7f8a7309519dd508b024d193b4f420147bdb980f447d4beb54f90e5937a1`。正常重绑测试覆盖原身份、冻结字节与迟到回执；并发重绑的完整集合确认见 F-DAA013-QA1-002。新 DTO 拒绝旧顶层 `instanceId`（含全空解绑请求），去掉该字段后仍拒绝缺逐行实例的请求。 |
| AC05 正式候选与边界 | 通过 | 独立核对 14 项 before/after、批准和交接 SHA、allowlist、现行双语指南及锁定构建。规格、指南与 checklist 的本地相对链接均有目标文件。隔离验证范围为生产 Vue/合成 IPC、Rust/真实合成 SQLite、Rust worker/隔离回环 HTTP，以及测试替身控制并发时序。 |

## 命令、环境限制与资源

命令默认从隔离 DAA 目录执行。Cargo 使用 QA 根独立 `CARGO_TARGET_DIR`；回环与并发检查使用 QA 根下 `fixtures` 作为 `TMPDIR`。正式树执行 Node 定向测试、格式与 diff 只读检查。

| 命令 | 结果 |
| --- | --- |
| `node --test tests/facts-delivery.test.mjs` | 退出 0，6/6，含两条来源随开始/继续传递、同目标重绑 IPC 形态、双语键、逐行设置和取消。 |
| `pnpm --config.verify-deps-before-run=false build` | 退出 0。使用项目锁定的已备依赖。Vite 报既有 VueUse PURE 注释与 chunk 大小提示。 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check`；`git diff --check` | 均退出 0。 |
| `cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib infrastructure::local_store::sample_upload_tests -- --test-threads=1` | 退出 0，16/16。首次 QA 副本漏复制共享路径依赖，补入后通过。 |
| `cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib v2_saved_binding_cycle_reopens_and_delivers_matching_receipts_over_loopback -- --nocapture` | 默认沙箱在 `127.0.0.1:0` 返回 EPERM、退出 101。仅对合成回环测试提权复跑，退出 0，1/1。 |
| `cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib v2_worker_pause_preserves_inflight_receipt_and_stops_new_dispatch -- --nocapture` | 退出 0，1/1，失败 CAS 不停传，暂停后仍结算在途回执，继续复用 worker。 |
| `cargo build --locked --offline --manifest-path src-tauri/Cargo.toml --no-default-features --features rust-snap7-driver --bin aiis-data-acquisition-agent` | 退出 0，普通 Tauri 开发路径的 Rust feature 等效构建无 Rust warning。测试构建另外出现一条既有 `AgentConfig::empty_for_test` dead_code。 |
| `node old-ui-check.cjs` | 退出 0。QA 复用旧 SFC 驱动，在自己的临时根编译旧实现、生成请求并复核 SHA。 |
| 独立静态回环服务器 + IAB | 默认监听 EPERM；获准仅为临时页面监听 `127.0.0.1:54370`。首次合成 IPC 结构化拷贝不能克隆 Vue proxy，夹具改用 JSON 序列化后复跑成功。浏览器 viewport 已恢复并关闭测试页，静态服务器已停止。 |

QA 根 `/private/tmp/daa013-r1-qa-urkO9e` 暂保留至返工和 fresh QA 复核完成，包含 `race-repro.log`、`rebind-repro.log`、确定性复现的临时源码与测试、构建和浏览器夹具。并发复现与 loopback fixture 已关闭并移除各自合成 profile。Dev 根 `/private/tmp/daa013-r1-dev-OfJKE3` 保持只读。未操作 15191、真实 `.local/dev` 或默认 profile、真实后端、MySQL、Docker、DS、PLC、Git refs。原生 Windows、真实旧二进制降级、正式环境采用、部署和发布均留待各自授权及验证。

Verification 将 F-DAA013-QA1-001 和 F-DAA013-QA1-002 交 Development，经返工后再做独立验证。Human Owner 最终验收待定。

# DAA-013 r1 独立验证 QA2

**结论为 `qa_failed`。QA1 的两条确定性反例在本候选均通过。新的 F-DAA013-QA2-001 证实设置保存超时后延迟提交时，worker 可发起新的旧目标 POST。**

## 验证依据与范围

- fresh-context Verification 独立读取根及最近作用域约定、批准稿、完整 Development 交接、QA1 历史、实现差异和测试输出。获批 spec SHA-256 为 `fc9d5deba6245f4f0c457bc6ee26673298361f08be60b107d6b3d09704a82bb8`，返工 handoff SHA-256 为 `9ff52236f25c607a7de88d0ec8d4bdc7e3c7bd822490264960a9f006e1825db6`。正式工作树 HEAD 为 `fd999224a8756feda314a33148304b4bf3461876`。按 Development 实际起点、QA1 隔离树、正式返工树三方逐项核验 14 条哈希，QA1 到 QA2 七个返工路径与交接一致。正式树与 QA2 构建副本的 14 项均匹配最终清单。核对实际起点到正式树的完整 DAA 源码和测试，变化限交接表的 12 个源码或测试文件及两份指南。包清单、pnpm/Cargo 锁文件、Tauri 配置、命令 adapter、schema 和 profile 准入入口的哈希一致。并行 ARCH-ACQ-004 差异以实际起点为准。 [批准规格](spec.md) · [返工交接及最终哈希](tasks.md#qa1-返工与新的-developer_handoff)
- macOS 15.7.7 arm64，Node 22.19.0、pnpm 11.11.0、Cargo/rustc 1.89.0。QA2 使用独立源码、构建目录、合成 runtime SQLite 和随机回环端口。实际工作树仅写入此 checklist。原生 Windows、实际旧二进制降级、真实 profile、已运行服务、真实后端、MySQL、Docker、DS/PLC、部署、发布和 Git refs 均在本次执行范围外。

## F-DAA013-QA2-001 · 超时保存延迟提交后仍可向旧目标派发

对应 R02 保存应停传并要求显式开始、R03 过期确认须拒绝发送及 AC02。以下复现使用真实 storage actor、SQLite、设置保存路径和现有 worker。QA2 隔离副本仅在 Save 取得 `delivery` 锁后、入队前增加调度回调，保留实际 10 秒等待和写入、派发判定。POST 目的地由合成 `Transport` 捕获，无外部连接。

1. 使用临时 runtime4 SQLite 保存 `http://127.0.0.1:38117`，空队列下按该版本和完整来源显式开始。暂持 `delivery_http` 保持派发静止。
2. 启动仅修改目标为 `http://127.0.0.1:38118` 的正常 CAS 保存。在 Save 持锁、入队前令 storage actor 进入合成等待，Save 在其后入队。让调用经过原本的 10 秒等待并返回 `storage_pending`。
3. 放行 actor。排队的 Save 照常提交新 revision 与新目标。同一 actor 再读取已提交设置并落一轮新样本。复核完整来源集合与旧确认完全相等，读取快照为 `running=true`。
4. 释放 HTTP 锁。预期为保存提交后停传、等待对新目标的显式确认并零新派发。实际现有 worker 新发出 POST，捕获目的地为 `http://127.0.0.1:38117/api/v1/integration/plc-facts/samples`。该样本在新设置提交后才进入队列。复现退出 101，测试运行 11.60 秒。日志 SHA-256 为 `fa33dd232bbcc071151b49bdab4881f9fa7c4b7b53615041b485057e338bc862`。

```sh
cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib qa2_pending_settings_commit_must_not_allow_new_post_to_stale_origin -- --nocapture
```

`StoreHandle::call(false)` 超时会结束调用方等待，队列中写回调仍会执行。Save 仅在收到 `Ok` 时设置 `running=false`。worker 的最终门槛比较内存 `origin` 和当前来源是否都已确认；设置版本和 SQLite 已提交目标没有参与最终派发校验。 [存储入队与超时](../../src-tauri/src/infrastructure/local_store/mod.rs#L603) · [保存和运行状态](../../src-tauri/src/services/local_delivery.rs#L55) · [标记发送前的最终检查](../../src-tauri/src/services/local_delivery.rs#L342)

## 逐项结果

| 验收 | QA2 结论与证据 |
| --- | --- |
| AC01 逐台配置与布局 | 通过。以本轮实际 Vue 生产构建加合成 Tauri IPC 在 Chrome 运行 960 × 640。两个同名本机 PLC 按 ID 分行，分别显示 DB21 和 DB22、DB23。A 手填三项各 128 UTF-8 字节，ASCII 项按 End 可查看末尾（字段滚动偏移 950 px）；B 接受三项 JSON 和旧 `dbNumbers:[99]`，保留活动 DB22、DB23。无效粘贴保留 A、B 草稿，部分输入报本机 B，重复 PLC ID 阻止保存。关闭取消后重开恢复原值。随后保存并切换英文重开，A、B 及不活动 C 的完整绑定都在。设置弹窗内容宽 898 px，页面宽 960 px。英文确认列出合同、目标、A/DB21、B/DB22、B/DB23 和历史 DB24；取消后仍停止，确认后可暂停，切回中文显式继续后也可暂停。 |
| AC02 同异实例、持久化与确认 | **失败**。同实例、异实例、不同 PLC 复用代次、只改一台、保留不活动绑定、重开、过期 CAS、旧代次换实例、错实例和缺来源确认的常规用例通过。F-DAA013-QA1-001 的正常 Save 先提交时，旧 Start 返回 `source_confirmation_changed`、零派发。Start 最终核对或 worker 选中样本之后加入历史来源均被拦截，worker 反例保留 prepared/attempt=0。存储延迟提交场景见 F-DAA013-QA2-001。 |
| AC03 多来源逐样本回执 | 通过。两台 PLC 各两个 DB，四份真实 SQLite 样本经现有 worker 发出五次隔离回环 HTTP POST。首份错实例回执保持 unknown，恢复重试使用同一请求字节，四个样本最终按实例、PLC、DB、代次、样本 ID、序号及有效回执匹配确认。账本覆盖错样本和迟到旧尝试，未绑定轮仍仅本地。在途回执仍能按原目标与正文结算，正常保存及暂停停止新派发，显式继续复用 worker。 |
| AC04 旧库与冻结材料 | 通过。运行 17 项 SQLite 定向验证，覆盖旧单实例直接读回、未标记前驱、全空仅本地、有标记周期、未冻结待传、已冻结未发送、unknown 和已确认，比较保存与重开前后原身份、样本、序号、观察时间、上下文、冻结目标/正文/摘要、回执及历史尝试。旧轮保留开始时的身份，新轮按新绑定；runtime2/3 保持本地读取及 v2 禁止。QA1-002 的 4→2 来源变更使重绑返回 `source_confirmation_changed`，目标、unknown、正文、摘要和尝试材料保全；新增历史来源亦拒绝，设置版本并发变更返回 `delivery_settings_conflict`，重新确认后才允许原字节重绑。用旧版等效准入复核混合实例拒绝，并编译实际旧 SFC 重放两种旧请求，JSON SHA-256 为 `a8bc7f8a7309519dd508b024d193b4f420147bdb980f447d4beb54f90e5937a1`，新 DTO 拒绝旧顶层实例或缺逐行实例。 |
| AC05 正式候选与边界 | 通过。实际三方差异、allowlist、双语操作步骤、锁定构建与本地相对链接目标经核对。QA2 证据覆盖浏览器/合成 IPC、真实合成 SQLite、隔离回环 HTTP 和受控 actor 时序。 |

## 锁审计与命令结果

Start 与正常 Save 的主顺序为 `delivery → storage`。Start 对反向获取的 `delivery_http` 使用 `try_lock`，worker 可持 `delivery_http` 等待 `delivery`；Start 在互斥时直接返回 `delivery_http_busy`，不循环等待。storage actor 的确认、重绑和标记尝试回调只处理 Stores，不反向取得 `delivery`；HTTP 响应等待期间不持有 `delivery` 或 SQLite 事务。实际在途测试通过。F-DAA013-QA2-001 属于异步写入完成与运行状态失配。

| 命令或检查 | 结果 |
| --- | --- |
| 正式树 `node --test tests/facts-delivery.test.mjs` | 退出 0，6/6。 |
| 正式树 `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check`、仓库 `git diff --check`、初末 `shasum -a 256 -c` | 均退出 0，14/14 正式交付哈希一致。独立路径扫描核对本轮阅读文件的本地相对链接目标，未校验锚点。 |
| 隔离树 `pnpm --config.verify-deps-before-run=false build` | 退出 0。首次复制错误排除了依赖自己的 `dist`，补齐已锁定的现有依赖目录后通过。Vite 有既有 VueUse PURE 注释及大 chunk 提示。 |
| 隔离树 `cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib infrastructure::local_store::sample_upload_tests -- --test-threads=1` | 退出 0，17/17。 |
| 隔离树 `cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib services::local_delivery::tests -- --test-threads=1` | 默认 sandbox 试监听合成回环返回 EPERM。仅针对测试执行最小提权。第一次服务组 12/18，六个历史 v1 fixture 拒绝初始临时目录命名。按其约定使用 QA2 自有 `daa010-r5-dev-private` 目录重跑，退出 0，18/18。测试构建有既有 `AgentConfig::empty_for_test` dead_code 警告。 |
| 隔离树 `cargo check` 及 `cargo build`，均加 `--locked --offline --manifest-path src-tauri/Cargo.toml --no-default-features --features rust-snap7-driver --bin aiis-data-acquisition-agent` | 均退出 0，无 Rust 构建警告。按现有 Tauri 开发 feature 编译，未启动原生应用。 |
| `node old-ui-check.cjs`、静态合成服务与 Chrome | 旧 SFC 退出 0；生产构建经静态服务随机回环端口 59813 验证。Chrome viewport 已复原、独立测试页关闭、服务器已停止。 |

QA2 专属根 `/private/tmp/daa013-r1-qa2-Zmn9qT` 为后续返工与 fresh QA 暂保留。包含 `pending-save-repro.log`、`repro/automation-world/data-acquisition-agent` 调度复现、隔离源码构建、两段差异和定向日志。相关进程已结束，失败复现中的合成 profile 已移除；旧 v1 fixture 留下的六个合成 profile 在本根下的 `daa010-r5-dev-private/`。复现步骤、输出、代码位置和结果以上文为持久证据。Development 和 QA1 的临时根只读保留，协调者在下一轮证据复核完成后确认归属与清理。

Verification 将 F-DAA013-QA2-001 交 Development。返工后须重新独立验证该时序、正常保存与在途回执，以及已通过的 QA1 反例。Human Owner 最终验收待定。


# DAA-013 r1 独立验证 QA3

**结论为 `qa_passed`。** QA1 两处确认并发反例和 QA2 未决设置保存的旧目标派发反例均在本交接候选关闭。AC01–AC05 的隔离验证通过，交 Human Owner 最终验收。

## 验证对象与环境

- Fresh-context Verification 独立读取项目和最近作用域约定、3MD、实际源码、起点差异和测试输出。获批 spec SHA-256 为 `fc9d5deba6245f4f0c457bc6ee26673298361f08be60b107d6b3d09704a82bb8`，最新 Development handoff SHA-256 为 `0cc6e79e1a737b8c6d6af75cccb823d2e0fe7ad15f2922909bdebe11011d7580`。正式源码为本仓工作树，HEAD `fd999224a8756feda314a33148304b4bf3461876`。最终 14 项哈希在交接表中固定。清单文件 SHA-256 为 `4260748e59e76435ded06fee8d838e00d33c6cbd4adce3d6d53da1af9afea5dd`，正式树核验 14/14，未插入调度夹具的隔离构建副本也为 14/14。以 DAA-013 实际起点逐文件比较，源码及测试差异为 12 项，另有双语指南两项，均在 allowlist。命令 adapter、schema、profile 准入入口、锁文件、包清单及 Tauri 配置与起点相同。 [获批规格](spec.md) · [最终文件摘要](tasks.md#最终源码及指南-sha-256)
- 环境为 macOS 15.7.7 arm64、Node 22.19.0、pnpm 11.11.0、Cargo/rustc 1.89.0。使用隔离源码副本、锁定的现有依赖、独立构建目录、合成 SQLite 和随机回环端口。正式工作树只写本清单。项目私有 env、用户及默认 profile、15191、现有服务、真实后端、MySQL、Docker、DS、PLC、Git refs、部署和发布均未接触。Windows 10/11 x64 原生验证、真实旧二进制降级与实际环境采用留给各自后续验证。

## 验收结果

| 验收 | QA3 独立证据 |
| --- | --- |
| AC01 逐台配置与布局 | 通过。Chrome 在 960 × 640 运行实际生产构建和合成 IPC，从配置中心进入上报设置。两个同名 PLC 通过 `local-a` / `local-b` 区分，各有一行，分别显示 DB21、DB22/23。不活动 C 显示原 ID 和空 DB。A 手填各 128 UTF-8 字节的三项，长字段按 End 横向滚动 801 px，设置弹窗内容宽 898 px，页面宽 960 px。B 的三项 JSON 和旧 `dbNumbers:[99]` 均可粘贴，DB22/23 保持不变。非法粘贴保留两行草稿，部分输入指向 B，重复 PLC ID 未调用保存，关闭后重开原值保留。正常保存三条绑定后切换英文重开核对 A/B，保留 C。英中两次触发 `storage_pending` 均显示对应语言的「上报已暂停、稍后重开核对」提示。设置的保存、关闭以及长标识确认弹窗的取消和确认实际可操作。 |
| AC02 同异实例、持久化与确认 | 通过。SQLite 覆盖不同实例、不同 PLC 共用实例和代次、只改一台、保留不活动绑定、重开、过期 CAS、同 PLC 旧代次换实例和非法／重复身份拒绝。浏览器确认列出目标、合同和 A/DB21、B/DB22、B/DB23、历史 DB24 各自完整身份，取消无控制调用，确认提交当前设置版本及四条来源。定向 Rust 验证过期、缺失及错实例确认拒绝，Start 和重绑并发反例以及保存未决成功／失败时的停止与显式恢复见下节。 |
| AC03 多来源逐样本回执 | 通过。两台 PLC 各两个 DB，真实合成 SQLite 和现有 worker 通过随机隔离回环发出五次逐样本 POST。首份错实例回执保持 unknown，重试正文原字节相同，最终四份样本按实例、PLC、DB、代次、样本 ID、序号及匹配回执确认。错样本及错尝试回执由账本定向测试拒绝。未绑定轮仅保存在本地。在途回执与暂停／恢复的并发证据见下节。 |
| AC04 旧库与冻结材料 | 通过。SQLite 17 项覆盖旧单实例直接读回、前驱无标记、全空仅本地、有标记、未冻结待传、已冻结未发送、unknown 与已确认。比较保存和重开前后的标识、样本原文、配置上下文、观察时间、序号、目标、冻结正文／摘要、尝试及回执。旧轮保留开始时绑定，新轮使用新绑定。runtime2/3 本地采集仍可用且保持版本、拒绝 v2；旧共享实例准入等效检查对混合实例拒绝。实际旧 SFC 在隔离驱动中重放，旧请求 SHA-256 为 `a8bc7f8a7309519dd508b024d193b4f420147bdb980f447d4beb54f90e5937a1`。旧请求中的顶层实例及缺少逐行实例均被新 DTO 拒绝。显式同目标重绑保留冻结正文和原尝试证据。 |
| AC05 正式候选与边界 | 通过。独立完成源码哈希、实际差异、allowlist、生产 Vue 构建、Rust 启动等效构建、锁定测试、双语指南、格式、空白和本地相对链接检查。浏览器验证采用合成 IPC，Rust 样本与账本采用真实合成 SQLite，网络测试使用仅监听隔离回环的合成服务。 |

## 并发时序及锁序

- **F-DAA013-QA1-001**。正常设置保存先提交时，旧确认返回 `source_confirmation_changed`，POST 为 0。Start 从读取确认快照到发布运行状态与 Save 共用 `delivery` 锁。最终确认与完整来源、设置版本及目标重验在同一 actor 回合。确认后新增历史来源和选中样本后新增历史来源的用例均拒绝，后者没有尝试和 POST。
- **F-DAA013-QA1-002**。重绑的完整来源从四条减到两条时拒绝旧确认，原目标、unknown 状态、正文、摘要和尝试保持。新增历史来源也拒绝。并发保存改变目标时拒绝，重新确认后才允许以原字节重绑。
- **F-DAA013-QA2-001**。运行真实 storage actor 和 10 秒写等待的复现。保存返回 `storage_pending` 时已停止新派发，actor 未决期间 Start 返回 `storage_timeout`。迟到成功提交新版本及新目标后，旧版本返回 `source_confirmation_changed`，零旧目标 POST，新版本和完整来源明确确认后只发往新目标。迟到校验失败时，原 revision、目标与绑定均保留，上报仍暂停，显式确认原配置后恢复。同步 CAS 失败保留原运行状态。
- **在途回执和 HTTP 许可**。旧目标首个请求在 actor 阻塞期间返回匹配回执，回执写入也排队并超时。测试取得 HTTP 许可时，`storage_pending` 已锁存在控制状态。恢复 actor 后原请求以原目标、原字节和匹配回执确认，无新旧目标请求。重新确认新设置后第二个样本仅发往新目标并确认。worker 的顺序为 `delivery_http → delivery`，Start/Save 持有 `delivery` 后调用 storage。Start 取 HTTP 许可只做 `try_lock`，互斥即返回 `delivery_http_busy`。storage actor 回调没有反向获取 `delivery`，网络等待期间不持有 `delivery` 或 SQLite 事务。 [保存、确认、派发和回执](../../src-tauri/src/services/local_delivery.rs)
- **选样前旧 tick 的预冻结**。QA3 在独立副本仅加入 `cfg(test)` 的选样前调度屏障。先暂停旧 tick，成功保存新目标并停止，再持久化一轮新样本。放行后 SQLite 可留下旧 URL 的 `prepared` 材料，`attempt=0`、尝试表 0 行、POST 0 次。显式核对新版本和完整来源后，已有确认事务将未尝试条目切到新目标，正文逐字节一致；两条样本仅在新地址各 POST 一次并匹配确认。已尝试样本仍遵循原目标保护和同目标重绑条件。 [选样与确认事务](../../src-tauri/src/infrastructure/local_store/sample_upload.rs)

## 命令、结果与资源

Cargo 在 QA3 隔离副本运行，设置 `CARGO_TARGET_DIR` 为 QA3 根下 `cargo-target`，测试用 `TMPDIR` 为 QA3 根下 `daa010-r5-dev-private`。该临时目录名匹配旧合成测试的准入条件。Rust 定向测试使用 `--locked --offline --manifest-path src-tauri/Cargo.toml --lib --no-default-features --features rust-snap7-driver`。

| 命令或检查 | 结果 |
| --- | --- |
| `cargo test` 加上述参数及 `services::local_delivery::tests -- --test-threads=1` | 退出 0，22/22，50.64 秒。仅对合成回环监听使用最小提权。测试编译有一条既有 `AgentConfig::empty_for_test` dead_code warning。日志 SHA-256 为 `1a2f08e52b4c588431dcf7ef838befb8ee5d452be51f2b9a7a0d4356331d8ff8`。 |
| `cargo test` 加上述参数及 `infrastructure::local_store::sample_upload_tests -- --test-threads=1` | 退出 0，17/17，10.06 秒。日志 SHA-256 为 `745d792634b944b56e20804c73f7325d72bc70df019640bdf314ead190351623`。 |
| `cargo test` 加上述参数及 `qa3_unattempted_concurrent_freeze_is_recovered_with_identical_bytes_after_reconfirmation -- --nocapture` | 仅在带测试调度屏障的独立副本执行，退出 0，1/1，0.66 秒。日志 SHA-256 为 `5d6ad78fe9c116cc9a38f21effcb6e63702277b930f77c7d9b9bf7f6999c810b`。 |
| `cargo build --locked --offline --manifest-path src-tauri/Cargo.toml --no-default-features --features rust-snap7-driver --bin aiis-data-acquisition-agent` | 退出 0。按标准 Tauri 开发入口的 feature 等效构建，普通构建无 Rust warning。未启动原生应用。 |
| `node --test tests/facts-delivery.test.mjs`；`pnpm --config.verify-deps-before-run=false build`；`node old-ui-check.cjs` | 均退出 0。Node 7/7。生产构建使用现有锁定依赖，Vite 有既有 VueUse PURE 注释及大 chunk 提示。旧 SFC 夹具在 QA3 自有副本运行。 |
| `node serve.cjs`；`playwright-cli -s=daa013-qa3 open http://127.0.0.1:49313 --browser=chrome`；`playwright-cli -s=daa013-qa3 run-code --filename=browser-check.cjs` | 本地浏览器独立会话最终退出 0。内置浏览器不可用，改用既有 Playwright CLI。首次 CLI 夹具把 `TextEncoder` 用在工具执行上下文，切到页面上下文后通过；静态夹具唯一浏览器控制台错误是缺 favicon 的 404。 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check`；`git diff --check`；`shasum -a 256 -c` 及本地链接扫描 | 全部退出 0。复核正式交付 14/14。指南及 3MD 的 72 个本地相对链接目标存在，锚点未做批量解析。 |

QA3 自有临时根为 `/private/tmp/daa013-r1-qa3-vynEZ6`，包含隔离树、独立构建目录、差异、日志、受控时序副本、浏览器夹具与浏览器运行记录，以及六份旧 v1 合成测试 profile。其他合成测试自行关闭并删除其 profile。Rust 测试均已结束，独立 Chrome 会话均已关闭，静态回环服务器已停止，已只读确认 QA3 浏览器 PID 和回环端口 49313 均无运行实例。必要复现步骤、输出与哈希已记在本清单。协调者确认无后续复核或证据依赖后，可回收 QA3 自有临时根。Development、QA1、QA2 临时根的清理沿用各自交接条件。

Verification 将 DAA-013 r1 的 `qa_passed` 交 Human Owner 最终验收，当前最终验收待定。

## 协调者收尾

协调者在 QA3 通过并将必要验证证据写入本清单后，核对四个临时根均归 DAA-013 r1、属主为 `jason`、权限为 `0700`，无挂载或 `lsof` 打开的句柄，并确认相关测试、浏览器与回环服务已结束。协调者已清理 `/private/tmp/daa013-r1-dev-OfJKE3`、`/private/tmp/daa013-r1-qa-urkO9e`、`/private/tmp/daa013-r1-qa2-Zmn9qT` 和 `/private/tmp/daa013-r1-qa3-vynEZ6`，Verification 只读复核四个路径均已不存在。必要的复现步骤、验证结果及证据摘要已持久化在本清单。QA3 结论为 `qa_passed`，Human Owner 最终验收待定。

# DAA-013 r1 独立验证 QA4

2026-11-13（Asia/Shanghai），命名 Verification 在 fresh context 独立复核 DAA-013 r1 的双语 Stage C 指南、上报确认文案及定向测试返工。**当前候选为 `qa_failed`。** R4-QA-03 的单表、旧 r2 分支及中文链接通过复验，新增英文单表操作的界面标签不符，见 F-DAA013-QA4-001。QA3 结论及证据适用于其先前候选。 [批准规格](spec.md) · [本轮精确交接](tasks.md#精简后的完整源码及指南-sha-256) · [原 R4-QA-03](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md#失败与返回项)

## 候选与变更范围

- 正式工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876`，spec SHA-256 `fc9d5deba6245f4f0c457bc6ee26673298361f08be60b107d6b3d09704a82bb8`，本轮 Development handoff SHA-256 `9c5bc1a568adbf31c6a65931b2023a1a732eb998539bceb17ae61581ce2c1573`。正式树 14 项均匹配末尾交接表。与 QA3 的 14 项清单比对，9 项相同，5 项变更的 QA3 前驱副本也逐项匹配其原摘要。实际逐文件 diff 限两份指南的现行说明、两种 locale 各两条提示和一份定向测试，均在 r1 allowlist 内。依据包括根与最近作用域约定、完整 3MD、ARCH-ACQ-004 r4 规格及 R4-QA-03、实际源码及测试和构建输出。根规则下按 `project-governance`、`aiis`、`frontend-ui`、`i18n-workflow` 复核。 [工作流](../../../../.codex/workflows/development-lifecycle-workflow.md)
- 本轮变更文件 SHA-256 如下，路径相对 DAA 项目。

| 路径 | QA4 SHA-256 |
| --- | --- |
| `STAGE_C_GUIDE.md` | `2bfa71a94cc223a3d37c0564743528222010c94a175166dd50d972ae587787ea` |
| `STAGE_C_GUIDE.zh-CN.md` | `a5637f079081edf7a1441148f99cfd4d93deaebf5dc13b2509dad0a13d393d73` |
| `src/locales/en-US/common.json` | `6df9455806f16c264fb7a978fe277465431c7bdceedb5c39fe2b015ef015f7cc` |
| `src/locales/zh-CN/common.json` | `942a8dd5c89cbea35fca1d61cf2ce4c17f16bc06e7a48bc1b2edb6afb93066fd` |
| `tests/facts-delivery.test.mjs` | `11622c0f29cdaca4b4753029010eef794eb3c2e5ccd51c0b419dfcab7aa2d56c` |

## F-DAA013-QA4-001 · 英文单表接入步骤的 Web 控件名称与实际界面不符

DAA-013 AC05、ARCH-ACQ-004 R4-05/R4-06 和按指南实操的 R4-AC05。英文指南第 102 行让使用者保存登记后复制该行加粗的 **Access parameters**。现行 Web 来源表行操作及弹窗均解析 `acquisition-data.sourceConfig.parameters`，英文实际为 **Connection parameters**，弹窗按钮为 **Copy parameters**。按指南在英文界面查找 **Access parameters** 无对应控件。中文第 104 行「接入参数」与 Web 行操作一致。请 Development 将英文单表操作写成实际行按钮和复制按钮，并核对旧 r2 分支的冻结版标签，或用不依赖标签的准确步骤。旧 r2 的英文标签本轮没有对应版本的直接运行证据，确认的反例限现行单表候选。 [英文指南第 102 行](../../STAGE_C_GUIDE.md#L102) · [Web 行操作](../../../../frontend-js/src/app/acquisition-data/views/sources/index.vue#L28) · [Web 弹窗及复制操作](../../../../frontend-js/src/app/acquisition-data/views/sources/index.vue#L65) · [英文 locale](../../../../frontend-js/src/app/acquisition-data/locales/en-US.json#L10)

## 验收与执行证据

| 验收 | QA4 结果 |
| --- | --- |
| R01–R03／AC01–AC02 确认提示与调用 | **通过本轮增量。** 两条实际提示的三标识需匹配目标登记，DB 随本机样本列出，并按目标后端规则核对上报许可。共 664 个中英叶键对称，仅 `delivery.confirmRegistration` 与 `delivery.confirmSameTarget` 的值变化。开始和继续保留目标、合同、全部合格来源及历史待传样本；同目标重绑保留新旧地址、同一逻辑 provider 及同一数据库、原身份与原字节、可靠回执约束。占位符与 QA3 前驱一致。合成 IPC 运行两种语言的开始、继续、同目标重绑，每项确认和取消各一次，12/12；确认保留两台 PLC 的三条来源（含一条历史代次）、设置版本及原 IPC 参数，取消时无控制写入。 |
| R03–R04／AC03–AC04 逐样本结算和旧库保护 | 本轮提示差异未触及相关 Rust、确认逻辑、IPC 类型、adapter 或本地账本。证据沿用 QA3 对对应源码的隔离 SQLite、回环 HTTP 及故障时序记录。QA4 复核实际调用与原身份、原字节、可靠回执的提示。 |
| AC05 双语指南及 R4-QA-03 | **规则和锚点通过，英文 Web 操作标签失败。** 两份指南均限定单表步骤适用于已采用 r3/r4 的目标。每台 PLC 登记 `plcId`、`instanceId`、`sourceGeneration`、`sourceType`，POST 对前三项准入，类型用于标注，DB 属于样本及查询筛选。已登记 PLC 的合格事实可按 DB 读回；未切换 r2 仍有独立 DB 读写授权。未推定实际环境切换。当前两版 48 个本地链接、24 个片段均有效，中央指南另有 13 个本地链接、10 个片段通过。旧版唯一缺失的中文 `#r2-候选迁移导入与恢复` 已复现，修正后指向 `#r2-候选迁移导入与恢复冻结前驱工具`。DAA-008 历史标题至文末逐字节与 QA3 候选一致。英文实际按钮见 F-DAA013-QA4-001。 |

macOS 15.7.7 arm64，Node v22.19.0、pnpm 11.11.0、Vite 5.4.21。使用已安装的仓库锁定依赖，Vite 现行配置 `envDir: false`。以下前端命令从正式 DAA 目录执行，根仓库仅写入本 checklist。

| 命令或检查 | 退出码与结果 |
| --- | --- |
| `git rev-parse HEAD`、`shasum -a 256`、`git diff --check`、`diff -u` 与内联 `python3` SHA-256 核对 | 当前工作树与末尾交接表 14/14，变更前 5/5，其余 9/9 对应 QA3 摘要。空白检查退出 0。`diff -u` 对五个有意变更路径返回 1，逐段审阅变更。 |
| `node --test tests/facts-delivery.test.mjs` | 退出 0，7/7。实际 composable、真实 Vue I18n、合成 IPC 与确认框替身覆盖语言、来源集合、同目标核对和具名 IPC。 |
| `node --input-type=commonjs` 内联合成 IPC 探针 | 最终退出 0，12/12。TypeScript 编译正式 i18n 装配、composable 及 `factsDelivery`，用八个真实模块 locale 模拟 Vite glob，只替换对话框与 IPC；断言两语三动作的确认/取消、三条来源、旧新 URL、设置版本和回执措辞。首次退出 1，探针误把 `src/app/README.md` 当模块目录，限定到存在的 locale 文件后复跑通过。 |
| `pnpm --config.verify-deps-before-run=false exec vue-tsc --noEmit`、`pnpm --config.verify-deps-before-run=false exec vite build --outDir "$QA4/dist" --emptyOutDir`、`diff -qr "$QA4/dist" /private/tmp/daa013-r4-guides-HCwgxt/clarity-formal-dist` | 全部退出 0，独立正式生产构建与 Development 产物逐字节一致。产物 `index-BzMbOGgy.js` SHA-256 `13d0d7b3fa8828f7ee54a43c0717f79c6a17579596d027a76301f6d28d23138d`，有既有 VueUse PURE 注释及大 chunk 提示。 |
| 内联 `python3` 本地链接、代码围栏、历史字节及 JSON 核验 | 退出 0。核对目标文件、GitHub 风格标题片段和显式 HTML 锚点，检查 locale 重复键、键差异和占位符。历史英文 23,110 字节，SHA-256 `3b4c17fae74afb2b11df51d6491e39025180fab0bf83650beeeacac7e88327fc`；中文 20,602 字节，SHA-256 `d3fb8a87caf7107eecff4ff6fb74048a87db44b5f6639e2eac179936a7f0b7cc`。 |

## 交接与资源

`qa_failed` 返回 Development 修正 F-DAA013-QA4-001，按修订后精确候选另行独立验证。Human Owner 最终验收待定。ARCH-ACQ-004 的其他 findings 和两个候选的原生联合链路仍按其任务记录。QA4 运行边界为静态文档、前端生产构建与合成 IPC；Rust/MySQL 套件、原生 Tauri/Windows、实际 profile、用户服务、真实后端、容器和设备均未执行或访问。本轮只读使用 `/private/tmp/daa013-r4-guides-HCwgxt` 的 QA3 前驱副本和 Development 产物，QA4 无后续依赖。QA4 自建 `$QA4` 为 `/private/tmp/daa013-r1-qa4.xMVBswAd`，只有独立前端构建，无服务、profile 或数据库；必要证据在本清单，协调者可核对归属并回收。Development 根由协调者同时核对后续返工依赖和清理时点。

# DAA-013 r1 独立验证 QA5

2026-11-13（Asia/Shanghai），命名 Verification 在 fresh context 独立复核 QA4 后的英文指南返工。**结论为 `qa_passed`。** F-DAA013-QA4-001 已关闭，QA4 的失败和当轮其余验证证据保留。精确候选交 Human Owner 最终验收。

## 候选与范围

- 正式工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876`。获批 spec SHA-256 `fc9d5deba6245f4f0c457bc6ee26673298361f08be60b107d6b3d09704a82bb8`，本轮 Development handoff SHA-256 `4af58dd5542fbbdd0b7b393a742a808803a54a8694c5931b19f579e72d1ab797`，写入本节前的 QA4 checklist SHA-256 `b5a2926806b26a0aaa2c203989b622da35c2df6a07f2c1f53cee42f68ad5b8e3`。正式树 14/14 匹配最终交接表。以 QA3 交接表叠加 QA4 本清单实测的 5 项摘要，重建 QA4 的 14 项清单并与上一交接表核对一致。与 QA4 比较，13 项逐字节相同，唯一变化是英文指南第 102–103 行的按钮操作文字，符合 r1 第 3 节。其 SHA-256 从 `2bfa71a94cc223a3d37c0564743528222010c94a175166dd50d972ae587787ea` 变为 `15ccd0f8a6d9c5d250b2588204db90a3f33af8094d812cfb25396186b376a235`。 [批准规格](spec.md) · [14 项正式交接摘要](tasks.md#qa4-返工后的完整源码及指南-sha-256) · [QA4](#daa-013-r1-独立验证-qa4)
- 本轮独立读取项目与最近作用域文档、3MD、两版 Web 页面与 locale、实际差异及可用 QA4 构建证据，使用 `project-governance`、`frontend-ui` 和 `i18n-workflow`。AC01–AC04 及 AC05 已通过的确认提示、双语键、合成 IPC 与构建结果，按上文 QA3、QA4 各自的已核对证据适用范围引用。QA5 针对 AC05 剩余英文标签和受影响的指南步骤执行静态验证。

## 验收结果

| 验收 | 独立证据 |
| --- | --- |
| AC05／F-DAA013-QA4-001 英文 Web 操作 | 通过。现行 r4 页面第 28、65、68 行与冻结 r2 页面第 34、82、85 行均将行按钮及弹窗标题绑定到 `acquisition-data.sourceConfig.parameters`，将弹窗复制按钮绑定到 `acquisition-data.sourceConfig.copy`。两版 `en-US.json` 分别解析为 **Connection parameters** 和 **Copy parameters**。两版 `copyParameters` 均将弹窗的参数 JSON 交给剪贴板。第 102–103 行对各自目标先指向行按钮，再指向弹窗复制按钮。 [英文指南](../../STAGE_C_GUIDE.md#6-register-sources-and-start-delivery) · [r4 实际页面](../../../../frontend-js/src/app/acquisition-data/views/sources/index.vue#L28) · [r4 英文 locale](../../../../frontend-js/src/app/acquisition-data/locales/en-US.json#L10) · [r2 历史交接](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/tasks.md#qa6-文档返工与-development-handoff) |
| AC05／R4-QA-03 文案和版本边界 | 通过。r4 Web 复制 `instanceId`、`plcId`、`sourceGeneration`，r2 的 JSON 另含 `dbNumbers`。英文指南保留按目标实际采用版本选择分支，已采用单表的目标登记四项，按三标识匹配 POST，`sourceType` 用于标注，DB 随样本及查询。旧 r2 继续按独立的 DB 写入和读取授权运行。中文操作、双语读回说明、迁移锚点和实际采用边界保持 QA4 已核对的内容。此结果覆盖 DAA-013 归属的指南步骤，ARCH-ACQ-004 原生联合链路的验收状态按该任务记录。 [中文指南](../../STAGE_C_GUIDE.zh-CN.md#6-登记来源并开始上报) · [联合验证记录](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md#arch-acq-004-r4-独立复验-qa2) |
| AC05 链接与 DAA-008 历史 | 通过。每份 Stage C 指南均有 24 个本地链接及 12 个片段，根采集指南另有 13 个本地链接及 10 个片段。目标路径、标题或显式锚点均有效，代码围栏闭合。两份 Stage C 指南自 DAA-008 历史标题至文末与留存前驱逐字节一致。英文 23,110 字节，SHA-256 `3b4c17fae74afb2b11df51d6491e39025180fab0bf83650beeeacac7e88327fc`；中文 20,602 字节，SHA-256 `d3fb8a87caf7107eecff4ff6fb74048a87db44b5f6639e2eac179936a7f0b7cc`。 [根采集指南](../../../../docs/acquisition-data-guide.zh-CN.md) |

两版 Web 源码与 ARCH-ACQ-004 对应交接记录的 SHA-256 一致。r2 使用 `/private/tmp/arch-acq004-r3-dev.0fxOzki5/pre-integration/frontend-js/src/app/acquisition-data/` 冻结前驱原件，另核对 Development 暂存副本与原件逐字节一致。

| Web 版本 | `views/sources/index.vue` SHA-256 | `locales/en-US.json` SHA-256 |
| --- | --- | --- |
| r4 正式树 | `6f3c8f34b2b7b7398c935a488492958a0077e4eabc4dd4008a73be25810421c0` | `be96ed15affcdfdfb937db877dd5f1886b1f92aaa535d53dce9e479c27fda9f0` |
| r2 冻结前驱 | `4d3a03a44a838859f8eba63ace59c81a6915d93608c975dd6f0b779f49ae701c` | `d1580d5c020c3e31b0bc4bb248c8176f214acf79004fd10de5bdd1576c242381` |

## 命令、限制与交接

macOS 15.7.7 arm64，Python 3.9.6，在正式工作树执行只读检查。正式树写入限本 checklist。

| 检查 | 结果 |
| --- | --- |
| `git rev-parse HEAD`、`shasum -a 256`、`git diff --check` | 均退出 0。核对正式 HEAD、3MD 摘要和空白。只读核对 QA4 既有构建 `index-BzMbOGgy.js` 摘要为 `13d0d7b3fa8828f7ee54a43c0717f79c6a17579596d027a76301f6d28d23138d`，与 QA4 记录一致。 |
| `diff -u` 对 QA4 英文指南与正式指南 | 退出 1，符合预期的两处行差异。独立内联 `python3` 重建摘要表并核对 14 项、仅第 102–103 行变化、两版页面绑定、JSON 字段、locale 和历史后缀，最终检查均退出 0。首次组合探针误将 r4 交接表行当成两列格式，修正为按哈希和路径两项匹配后通过。 |
| 内联 `python3` 相对路径及片段扫描 | 退出 0。核对双语 Stage C 和根采集指南共 61 个本地链接、34 个片段及代码围栏。 |

QA5 采用两版实际 Web 源码的静态证据。本轮没有重跑构建、Rust/MySQL、Web 运行态或原生 DAA，也未访问私有 env、已有 profile、后端、现有服务或设备。Windows 实测、实际采用、发布以及 ARCH-ACQ-004 的双候选原生链路沿各自记录处理。Human Owner 最终验收待定。

QA5 未创建临时文件、构建目录、测试 profile 或服务。只读使用 `/private/tmp/daa013-r4-guides-HCwgxt` 的 QA4 英文前驱和 r2 Web 源码副本、`/private/tmp/daa013-r1-qa4.xMVBswAd` 的 QA4 构建，以及 ARCH-ACQ-004 的冻结前驱原件。前两处必要证据已写入本清单，协调者确认归属、无运行占用及无后续复核或证据依赖后可回收。ARCH-ACQ-004 前驱由其任务协调者按原保留条件处理。

# DAA-013 r1 独立验证 QA6

2026-11-13（Asia/Shanghai），命名 Verification 在 fresh context 复核开始、继续和同目标重绑的确认弹窗。**结论为 `qa_passed`。** 本轮覆盖 R03、AC01／AC02 的确认界面与 IPC 增量，以及 AC05 的正式候选和前端检查。此前各轮的验收结果按其对应候选保留。Human Owner 最终验收待定。 [获批规格](spec.md) · [本轮 Development handoff](tasks.md#上报确认可读性修正与-developer_handoff)

## 精确候选与范围

正式交付树 Git HEAD `fd999224a8756feda314a33148304b4bf3461876`。获批 spec SHA-256 `fc9d5deba6245f4f0c457bc6ee26673298361f08be60b107d6b3d09704a82bb8`，本轮 Development handoff SHA-256 `92747a78a4f04418134d858e112bfb495bf08f8e540ca931a0d00673dbb23c4f`，复核前 QA5 checklist SHA-256 `971e5381d45997a19187184539fc4a3e187c2b25a16fed4cceb171fbd97e42e8`。工作树中的 14 项交付文件逐项匹配本轮最后一张交接表。以 QA5 核对过的 14 项摘要为基线，9 项字节一致，5 项变更的前驱副本逐项匹配 QA5 摘要。逐段检查确认 5 项均在获批 allowlist 内。 [QA5](#daa-013-r1-独立验证-qa5) · [QA6 交付表](tasks.md#本次完整源码及指南-sha-256)

| 变更路径（相对 DAA 目录） | QA6 SHA-256 |
| --- | --- |
| `src/console/composables/useLocalAcquisitionConsole.ts` | `a2e0c762a725596be65d120338ba5d976d2d417c54f6954648b9897844ad6f5a` |
| `src/locales/en-US/common.json` | `90790e07569962bc1d0c0029381daed3e45a33858cdb0c5ececca52b83f17a0f` |
| `src/locales/zh-CN/common.json` | `6598f86d54df4b3d7abcae737bfdcc861ac3c7643571efc04a67fa1cd7172609` |
| `src/styles/app.css` | `deea6bf71eda3cb6fe948c7ffaf96ecc537a33c6002995e34c9e49b6314a7f9e` |
| `tests/facts-delivery.test.mjs` | `b46d950a50099fe4545f201971d6cdcb857d4a2abc30f3314d036ccae7fd52d5` |

## 验收与证据

| 验收 | 独立证据 |
| --- | --- |
| R03／AC01 最小窗口可读性 | 在 960×640 用真实 Vue、Element Plus、CU 和 DAA 样式、实际 locale 装配与合成 IPC 渲染两种语言、明暗两种主题、开始／继续／重绑三种动作，12/12。首屏可见确认标题、完整目标与合同及来源标题。重绑并列显示原地址和当前地址。每条来源以独立标签显示 `instanceId`、`plcId`、`dbNumber`、`sourceGeneration`，DOM 逐字段等于夹具输入；覆盖每项 128 UTF-8 字节的 ASCII 标识、标识内斜杠、DB21/22 及历史待传 DB23。长值换行，内容无横向溢出。稳定布局高度 608 px，滚动视区高 504 px，长内容高 692–837 px；两枚底部按钮始终在视口内。观察中浅开始与英深重绑截图，目标、标签和值层级可辨。 |
| R03／AC01 键盘与关闭 | Tab 可进入弹窗的滚动区域并显示焦点轮廓，End 可到最末说明；浏览器矩阵中焦点留在确认框。分别用 Esc、标题栏关闭按钮与取消按钮验证 12 次，控制 IPC 为 0。另用实际 `ConsoleActionButton` 的忙态禁用和实际样本详情 `ElDialog` 复核，重绑中 Tab／End 可用，Esc 关闭上层确认、保留详情并产生 0 次控制 IPC。限制见下。 |
| R03／AC02 原设置版本与原来源 | 确认 12/12 每次只提交一笔合成 `daa_set_delivery`，核对 `action`、原 `settingsRevision` 和三项来源的完整原始数组；重绑另核对原 `sampleId` 与 `oldUrl`。源码仍将原 `material.sources` 与原 settings 直接交既有 adapter，展示独立读取字段。定向测试继续覆盖过期拒绝。简单确认复用原 `confirmAction`，其原标题、按钮及行为沿用，暂停仍直接走原 IPC。 [Composable](../../src/console/composables/useLocalAcquisitionConsole.ts) · [IPC adapter](../../src/services/factsDelivery.ts) |
| R03–R04／AC03–AC04 重绑约束和既有数据保护 | 双语均要求根据实际部署配置核对同一逻辑目标／provider 和同一数据库，指出仅连通或读回相同数据不足，并要求只按该样本原身份及原字节重试且须有效回执；中文采用「同一逻辑目标」措辞。浏览器核对说明与合成 IPC；同一真实数据库身份仍由操作者核对。既有 Rust、SQLite 账本、队列和回执代码在 14 项清单中匹配先前摘要，相关隔离实证见 QA3。 [原重绑准入](../../src-tauri/src/infrastructure/local_store/sample_upload.rs#L336) · [QA3](#daa-013-r1-独立验证-qa3) |
| AC05 双语及范围 | 双语各 675 个叶键对称、无重复、占位符一致。各语种修改 2 条原确认文案，新增 11 个确认键，真实装配中两种语言的标题与字段均可显示。CSS 只调整上报确认，双语 Stage C 指南及其它 9 项交付文件沿用 QA5 验证候选。 |

**既有键盘限制。** 使用实际 DAA 动作按钮并绑定 `local.busy` 时，Esc 关闭确认后焦点落回 `BODY`，下一次 Tab 到「开始 / 继续上报」，即使底层样本详情仍可见。用完全相同的独立夹具替换为已校验 SHA-256 的 QA5 前驱 composable、CSS 与双语 locale 后，开始和嵌套重绑两条路径复现同样轨迹。该既有行为与本轮新增的弹窗内可见焦点、键盘滚动及取消零控制 IPC 分别记录。

## 命令、环境与交接

macOS 15.7.7 arm64，Node v22.19.0、pnpm 11.11.0、Vite 5.4.21，使用仓库已安装依赖。按根与近作用域规则、完整 3MD 和实际差异，使用 `project-governance`、`frontend-ui`、`i18n-workflow` 与 Playwright。

| 命令或检查 | 退出码与结果 |
| --- | --- |
| `git rev-parse HEAD`、`shasum -a 256`、`git diff --check`、内联 `python3`、`diff -u` | 校验、空白及 JSON 检查退出 0。确认 14/14 正式候选、5/5 变更前副本和 675 个双语叶键。逐段检查前驱与候选差异，`diff -u` 对有意更改的文件退出 1。 |
| `node --test tests/facts-delivery.test.mjs` | 退出 0，7/7。 |
| `pnpm --config.verify-deps-before-run=false exec vue-tsc --noEmit`；`pnpm --config.verify-deps-before-run=false exec vite build --outDir "$QA6/dist" --emptyOutDir`；`diff -qr "$QA6/dist" /private/tmp/daa013-r1-confirm-NV212D/formal-dist` | 均退出 0。生产产物逐字节相同，`index-B3oGeqb_.js` SHA-256 `cb11cec25ab9b9d3d5b8c8edd5168b5f39064c8d9eaeba279bc9c578411cbd77`。Vite 输出既有 VueUse PURE 注释和大 chunk 提示。Vite 配置使用 `envDir: false`。 |
| `pnpm --config.verify-deps-before-run=false exec vite build --config vite.fixture.config.ts`；`node "$QA6/serve.cjs"`；`playwright-cli … open … --browser=chrome`、`… run-code --filename=browser-check.js`、`… product-check.js`、`… compare-focus.js` | 最终三组浏览器探针退出 0。沿用 Development 合成数据形状，从正式源码重建独立夹具并编写新的浏览器断言；内容只由随机回环端口 `51787` 提供。首次尺寸探针早于入场动画结束，待动画结束后通过。完整面板夹具额外引入无关的合成列表刷新错误，最终缩小到实际动作组件和实际样本详情验证焦点。默认沙箱拒绝回环监听（EPERM），仅临时静态服务与独立 Chrome 会话使用最小提权。浏览器矩阵报告页面错误 0，非夹具来源的页面请求 0。 |

本轮只运行前端静态检查、生产构建与合成浏览器，实际 `.local/dev`、私有 env、原生 Tauri、数据库、用户服务、后端和设备均在本轮验证边界外。Rust/MySQL 与 ARCH-ACQ-004 联合测试证据沿各自原记录，Windows 原生和实际采用仍待相应验证与决定。

QA6 自有 `$QA6=/private/tmp/daa013-r1-qa6.6KGyRV0c` 保存独立源码、构建、临时探针与合成截图；Chrome 测试会话已关闭，随机静态端口已停止监听。截图 SHA-256 分别为 `22fb9ba68c90dcc41d09ed40e0988731bd33e5cdbf8980af9342f9653f47ddbd`（中文浅色开始）和 `af5441a96870a4a1550287082f884344549dbc9af7c94fecac1e82d97fec9df2`（英文深色重绑）。必要行为、版本与摘要均已持久化。本轮已完成对 Development 临时根 `/private/tmp/daa013-r1-confirm-NV212D` 的复核，协调者确认归属、无运行占用且 Human Owner 或后续任务无需再查看截图和夹具后，可回收两处临时根。Verification 将精确候选和本轮限制交 Human Owner 最终验收。
