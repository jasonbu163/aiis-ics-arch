Task ID: DAA-018
Revision: r3
Status: qa_blocked
Owner Role: Verification
Allowed Writers: Verification, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Handoff: QA2 离线复验结果及原生验证阻塞交 Human Owner；隔离条件明确解除后继续独立验证，最终验收仍待 Human Owner

# DAA-018 r3 独立验证 QA1

## 结论与候选

**`qa_failed`。** F-QA1-001 已用独立合成测试复现：产品普通草稿保存入口可以不经单点命名预览、token、输入摘要或确认，直接写入多个 PLC 的双语显示名。该行为违反本版 spec §2.1 的同一预览及「不开放绕过预览的普通保存」约束，必须返回 Development；不能用现有单点预览正例的通过抵消此失败。

本次 Verification 在 Development handoff 后以 fresh context 独立核对 bundle、候选、差异和安全可运行的测试。角色配置是 `contract_only`，不声称平台 ACL、强制路由或 Human Owner 最终验收。审阅了根及 AW/DAA 项目契约和相关 README/PLAN、canonical workflow、实际 verification 角色，并按任务表面读取 `aiis`、`project-governance`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`backend-arch` 和 `code-document-indexer`；没有据此修复产品。

- 验证的正式交付候选：`/Users/jason/Desktop/DreamCode/aiis-ics-arch` 未提交工作树，HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`。任务不属于整棵 dirty 工作树：其他任务和既有并行修改保留；`USER_GUIDE` 整文件哈希包含任务前改动，不把整份 diff 均归给本任务。
- spec `1ccb7f8b99d65b60842d0334b91821e9f4fcfb0e920dac38078ac5f47e1c09d3`；父 ARCH-PLC-001 r4 spec `10dbba00dd190bc0d40d99b6bfad03072e0ba752d8b55d350af4b3f491485967`，均与精确批准/交接一致。
- 当前 Development `tasks.md` SHA-256 `70474dfa8ea6af71f663a36b3dc607959cbfea3eb68a53b175c97ffe45cbb64c`。交接后协调者明确告知，原 `7a19c87ef459a9abab31bb269a8ee08cc68d172777884b83b3e962d1aae5dcbf` 文字中「任务唯一合成 profile」已更正为「首次受控原生窗口使用的合成 profile」，因为任务创建过多个合成 profile；保留原哈希与本次更正事实。没有将其冒称实现候选变化。
- 读取 `tasks.md` 内 20 行清单的原文（包括末尾换行）计算 SHA-256 `25f95f341f13caa741cc84b8e24920e66c5e0daaf71b9517229836ba1993a01c`；按每项逐个重算 20 个实际文件的 SHA-256，**20/20 一致**；这些路径均在 r3 allowlist 内。新测试文件为未跟踪文件；仅按文件清单和 Development 记录界定本任务，不将其他并行 dirty 文件一概归因。
- 最终审计时再次取得上述 HEAD、两个 spec、tasks 及 20 个文件哈希，结果一致。`git diff --check` 对 19 个已跟踪候选文件 exit 0；新测试文件 `git diff --no-index --check /dev/null <file>` exit 1 因文件不同，无空白错误输出。

## F-QA1-001：普通保存绕过双语预览

**规格：** `spec.md` §2.1 第 1–2 条要求扩展原单点命名预览以处理双语修改、同一候选提交，并明确禁止开放绕过预览的普通保存。

**可达调用链：** 正式产品 `src-tauri/src/lib.rs` 注册 `daa_save_draft`；`src-tauri/src/commands/local_acquisition.rs` 的该命令分发至 `engine.save(r.draft, r.expected_etag)`。`services/local_configuration.rs::save` 校验 ETag、清理明确删除 PLC 的旧点映射，再调用 `protect_derived` 和 `save_candidate`；`protect_derived` 检查点技术名、来源身份及部分地址，但不比较保留下来的 `point_display_names`。`save_candidate` / 存储层对映射作结构与引用验证后仍会提交。故合法结构的新增、修改或清空映射可绕过命名候选，甚至一次更改不同 PLC 的多个点。

**独立复现：** 仅在 `/private/tmp/daa018-qa-SrVGeW3v/replica` 复制 DAA `src-tauri`（排除 target）、TIA 共享 crate 和公开 v1 vectors；复制前后核对 `local_configuration.rs` 服务和 domain、IPC 命令、原测试、`Cargo.toml`、`Cargo.lock` 字节 SHA 一致。在该临时副本的现有测试模块末尾添加 QA-only 测试 `qa018_plain_save_bypasses_bilingual_preview`，不修改工作树测试或实现。使用新建 runtime3 合成 profile、`read_allowed=false`。测试先以 fixture 激活合成配置，再读取草稿和 ETag；完全不调用 preview/confirm，只执行下述关键动作：

```rust
let before = e.configuration().unwrap();
let a = before.draft.points[0].clone();
let b = before.draft.points.iter().find(|p| p.plc_id != a.plc_id).unwrap().clone();
let mut draft = before.draft.clone();
draft.point_display_names.insert(a.id.clone(), PointDisplayNames {
    zh_cn: "仅普通保存".into(), en_us: "NO_PREVIEW_A".into(),
});
draft.point_display_names.insert(b.id.clone(), PointDisplayNames {
    zh_cn: "第二台".into(), en_us: "NO_PREVIEW_B".into(),
});
let saved = e.save(draft, before.etag.clone()).unwrap();
assert_ne!(saved.etag, before.etag);
assert_eq!(saved.draft.points, before.draft.points);
let reopened = e.configuration().unwrap();
assert_eq!(reopened.draft.point_display_names[&a.id].en_us, "NO_PREVIEW_A");
assert_eq!(reopened.draft.point_display_names[&b.id].en_us, "NO_PREVIEW_B");
```

实际测试 exit 0，1 passed，打印 `QA018_REPRO: ordinary save committed two PLC display names without preview; etag changed`。这里的 **passed 表示成功复现缺陷**，不是验收通过。普通 IPC 的可达性由上述源调用链核对；未启动 Tauri 或发起真实 IPC。第一次在副本编译时因遗漏仓库公开 `vectors.json` 而 exit 101，复制该公开测试 fixture 后同一命令 exit 0；该环境准备错误没有计为产品失败。既有正式候选的 `point_display_names_reimport_conflict_and_plc_delete_preserve_identity` 也在独立 profile exit 0，其源码本身先通过 `e.save` 直接写入两台 PLC 的名称，再证明同 ID 原样/改源复导保留及 PLC 删除仅清理所属映射。修复应保留这些合法来源导入、删除和历史保护语义，不能简单禁用合法变更。

## 逐项验收结果

| 标准 | 独立结果和限制 |
| --- | --- |
| DA18-01 | **部分核验**：Rust 5 项覆盖缺省、闭合键、null、重复键、非法引用、字符串类型、UTF-8 字节长度、单侧/双侧清空、Unicode 与空格；真实原生界面显示和重开未测。 |
| DA18-02 | **部分核验**：Node 模拟宿主覆盖独立编辑、取消及未知回执后重读门禁；源码按当前 locale 取单语言且空值不回退。正式原生顶栏切换、编辑/取消对配置和样本的完整影响未测。 |
| DA18-03 | **部分核验**：合成测试通过同 ID 复导及改源复导保留、非法 ID 重绑拒绝、并发冲突、删除 PLC 清理本 PLC 并保留另一 PLC；未独立跑完整点/DB 删除及全部历史组合。 |
| DA18-04 | **未完成**：本轮未独立执行新程序零写读取带旧版本和样本的合成旧 profile，也未启动旧普通 native 二进制。Development 的旧 `local-validation` feature 结果不能替代普通 native 入口；当前 GUI/native 暂停，不能声称不误采或不建空库已获独立验证。 |
| DA18-05 | **部分核验**：本地合成旧 revision、样本、冻结、ACK 与完整 context/SHA 保全测试通过；不同 comment 和显示名的 v2 worker fixture 同时断言仅显示名变化时定义摘要不变。未独立完成带旧历史 profile 的完整零写重开矩阵。 |
| DA18-06 | **部分核验**：实际 runtime4 worker 使用内存 `Capture` transport 捕获旧从未发送样本新 v2 正文、新 revision 样本和已冻结重试，比较 name/value、缺失 comment、双语 sentinel 不外发及重试原 bytes；未发送真实 POST。`legacy_status` 合成测试对 attempted、unknown、ACK/不一致状态判断通过；源码将非 `NeverSent` 标记复核。源码显示 runtime 非 4 的 start/resume 拒绝，旧 v1 选批/冻结及 `Transport::post` 使用 `#[cfg(test)]`，runtime4 worker 调用 `post_sample`；正式特性 binary cargo check 通过。此项不声称实际网络或用户旧历史已测试。 |
| DA18-07 | **未完成**：29 项 Node 模拟测试、类型检查及 Rust 正式 feature 编译检查通过；最终候选中文/英文原生点表、编辑、顶栏切换、列宽拖动/跨重启/恢复默认及原生旧功能回归均 not_run。未运行前端 Vite build，Development 的构建不充作独立 QA。 |
| DA18-08 | **失败**：F-QA1-001。正常命名 preview 测试覆盖单候选、一个临时 SQLite trigger 计数的 CAS、篡改/伪造/超时、跨 PLC、旧请求；但产品普通 save 可不经预览写双语映射，故整体原子入口合同不满足。 |
| DA18-09 | **失败**：F-QA1-001 允许合法双语值绕过 preview/token/digest；即使命名确认路径的负例及 Node 未知结果重读门禁通过，也不能整体通过。先行「保存草稿并编辑」的 Node 模拟边界已覆盖；真实原生取消仍未测。 |
| DA18-10 | **部分核验**：test-only 本地 v1 构造保留含双语 sentinel 的完整 `contextUtf8`，context SHA 与冻结 body SHA 自洽；合成旧冻结/ACK 保留测试和 runtime3 不发送测试通过。生产 `facts_wire` 仍供账本重构，未将整个模块误称 test-only；用户真实历史未读取或修改。 |

## 环境、命令与结果

macOS 15.7.7 arm64；Rust/Cargo 1.89.0；Node v22.19.0；pnpm 11.11.0。自有 QA 根为 `/private/tmp/daa018-qa-SrVGeW3v`；`target` 从 Development 的构建 target 拷贝到独立路径后用于离线编译/测试，测试 profile 全部由本次 fixture 在 `daa-008-r2-a-qa` 下创建。与正式源码相同的项目锁文件、`--locked --offline`；未安装依赖。下面 `E` 为 `env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT CARGO_TARGET_DIR=/private/tmp/daa018-qa-SrVGeW3v/target TMPDIR=/private/tmp/daa018-qa-SrVGeW3v/daa-008-r2-a-qa DAA_PLC_READ_ALLOWED=false`；除 QA 临时副本项外，命令工作目录为正式 DAA 根。

| 命令或动作 | 实际结果 |
| --- | --- |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib qa018_plain_save_bypasses_bilingual_preview -- --nocapture --test-threads=1`，工作目录为 QA 临时源码副本 | 首次因副本缺公开 vectors 编译 exit 101；补齐同仓公开 vectors 后 exit 0，1 passed，成功复现 F-QA1-001。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib point_display_names_reimport_conflict_and_plc_delete_preserve_identity -- --test-threads=1` | exit 0，1 passed；单独执行复导、并发、PLC 删除及其前置直接保存。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib point_display_names -- --test-threads=1` | exit 0，5 passed；包括严格映射、预览/CAS、旧请求、复导/删除及 16 MiB 合成容量拒绝。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib daa018_ -- --test-threads=1` | exit 0，3 passed；test-only v1 完整 context、旧冻结/ACK 保全，和 v2 实际 worker 内存 transport 捕获。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib old_ledger_requires_proof_across_parts_batches_and_relations -- --test-threads=1` | exit 0，1 passed；合成内存账本状态判断，不能单独替代全部运行时发送矩阵。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib legacy_engine_does_not_dispatch_or_rewrite_inflight_v1_evidence -- --test-threads=1` | exit 0，1 passed；runtime3 start/resume 拒绝且合成 in-flight 证据保留。 |
| `E cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --bin aiis-data-acquisition-agent` | exit 0；编译检查，不执行 binary。 |
| `node --test tests/point-editing.test.mjs tests/facts-delivery.test.mjs tests/time-and-history-preferences.test.mjs`，显式私有 TMPDIR、移除 DAA env/profile 变量、禁止 PLC | exit 0，29 passed；无 DOM 的 Vue 模拟宿主/内存 IPC，Node 提示 MockTimers experimental。 |
| `pnpm exec vue-tsc --noEmit`，显式私有 TMPDIR、移除 DAA env/profile 变量 | exit 0。 |
| 递归对比 `src/app/plc/locales/{zh-CN,en-US}.json` 键 | exit 0，各 169 个叶键，差集为空；未替代原生双语显示。 |
| `git diff --check` 对候选中 19 个已跟踪文件；新文件 `git diff --no-index --check` | 前者 exit 0；后者 exit 1 表示与空文件不同，未输出空白错误。 |

Cargo 报一条既有 `empty_for_test` dead-code 警告。没有执行 GUI/CUA、真实 native 入口、真实网络、PLC、用户 `.env` 或真实 profile；没有借 Development 自检结果代替 QA。没有执行完整 Rust/Node 全量、Vite 构建或其他平台验证，不能将未执行项写成通过。

## 隔离事件、剩余 gate 与资源

Development `tasks.md` 报告：此前自有受控原生候选退出后，CUA 查询可能重新启动或错误绑定默认真实 DAA profile；已通知协调者/用户，启动或退出日志及其他写入是否发生未知，**不能写为零写**。本 Verification 不检查、读取、复制、修复、删除或回滚疑似真实 profile、日志或缓存，也没有使用 CUA。先前 incognito 合成窗口的部分语言/取消观察发生于最终 `border` 修改之前，且使用非持久 WebKit，既非本轮 QA、也不证明正式应用列宽持久性。

继续暂停所有 GUI/CUA 启动或附着及真实 native 入口。未来解除需协调者/Human Owner 明确处理该暂停，并先建立可证明不会回落至用户 profile、不会被工具重新绑定的隔离运行条件、唯一合成 profile 和禁止真实设备/网络的约束；在获准的隔离环境中验证最终候选原生编辑、顶栏切换、列宽拖动/跨重启/重置与旧普通 native 安全拒绝，保留精确证据。不能用旧 validation 二进制或早期 incognito 观察替代。

本轮自有 `/private/tmp/daa018-qa-SrVGeW3v` 含合成 profiles、临时源码副本、QA-only 测试和独立 Cargo target；先保留供返工/复验，待协调者确认不再依赖后按任务资源规则清理。Development 的 `/private/tmp/daa018-r2-dev-ewnCpRk3` 非本轮资源，不删除；系统诊断报告和任何疑似真实资料均不触碰。关键复现与结果已写入本 checklist，不仅依赖临时路径。

**Handoff：** F-QA1-001 交 Development 在同一批准范围内处理并保持合法导入/删除语义；返工 handoff 固定新候选后重新发起 fresh-context Verification，覆盖本轮未完成项及失败回归。QA 结论不授予 Human Owner 最终验收，不批准导出/导入、生产、部署、真实数据库或现场操作。


---

# DAA-018 r3 独立验证 QA2（返工后）

## 当前结论与审计边界

**`qa_blocked`。** QA1 的 F-QA1-001 在本轮独立负例覆盖的普通保存路径中不再复现；本轮未确认新的实现功能失败。但 DA18-04 的旧普通 native 二进制，以及 DA18-01/02/07 的最终候选原生编辑、语言切换、列宽拖动/跨重启/恢复等必测项仍未执行，不能给出 `qa_passed`。下方准确区分一次配置读取与应用启动/关闭产生的持久写入；不能称整个 profile 或进程生命周期零写。QA1 正文、失败证据和隔离事故原文保留；本文件仅更新元数据中的当前状态与 handoff，并在末尾追加本 QA2。QA1 原文件 SHA-256 `f7778f3652b2f0720f2e617693ee8d5a368ad18b657efa3939d5772032be6699`，其 `qa_failed` 为当时候选的历史结论，不被覆盖。

本轮为返工 `developer_handoff` 后 fresh-context Verification，仅审查、运行隔离检查与写本 checklist，没有修复实现或编辑 spec/tasks。角色为 `contract_only`，不声称平台 ACL、强制路由或 Human Owner 最终验收。读取项目根及 AW/DAA 规则、README/PLAN、canonical workflow、verification 配置和完整任务记录，按表面核查 `project-governance`、`aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`backend-arch`、`code-document-indexer`。

- 交付对象是正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的未提交候选，HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`；其他任务和 USER_GUIDE 的既有并行改动没有归因或回退。
- `spec.md` SHA-256 `1ccb7f8b99d65b60842d0334b91821e9f4fcfb0e920dac38078ac5f47e1c09d3`；`tasks.md` SHA-256 `b967c04be176b1a601d22d82ea14f24d2d944ff3388ab885db6b7d9febf4be93`；父 `ARCH-PLC-001 r4` spec SHA-256 `10dbba00dd190bc0d40d99b6bfad03072e0ba752d8b55d350af4b3f491485967`。最新 20 行 manifest 原文 SHA-256 `663ab9df588127442dadef64aa1a750cc4a52a5cf425cd34f2ec7fdd237dea50`，逐文件 20/20 与正式工作树一致；开始和写本记录前均复核。
- 审查候选差异、服务入口和受控测试：普通 IPC `daa_save_draft` 经 dispatch 调用 `LocalEngine::save`；后者对保留的映射比较旧值，删除 PLC 且该旧点也被删除时清除该点映射；然后仍执行 `protect_derived` 和原 CAS。受控单点命名确认重新验证输入 digest、token、ETag、300 秒期限及重建候选后调用一次 `save_candidate`。来源导入与偏移确认仍使用自己的受控候选路径。上述是源码及下列指定测试证据，不外推所有平台。

## F-QA1-001 返工复验

独立 QA 在 `/private/tmp/daa018-qa2-gQoXyhmB/replica` 复制当前 DAA `src-tauri`（排除 target）、同仓 `shared/tia-import-core` 和公开 v1 vectors；修改临时副本前用 `rsync -aicn` / `cmp` 检查副本相应来源与正式树一致，然后仅在副本追加 QA 自编测试，未修改正式测试或实现。自编 `qa2_ordinary_dispatch_requires_preview_and_preserves_every_unrelated_record` 在 runtime3 自有合成配置中先建立包含两个 PLC、旧 revision 和样本的资料；对正式 `daa_save_draft` dispatch 不调用预览，尝试两 PLC 同时新增、同时篡改、清空一侧、双侧置空及删除映射，均返回 `name_preview_required`。另用真实 preview/confirm 分别种入两 PLC 名称，再试删除一个 PLC 同时篡改另一 PLC，仍拒绝；每个拒绝后比较完整配置视图/ETag、草稿/source、revision、样本/上下文及旧账本快照，均未变。合法删除一台 PLC 时服务端清除所属映射，另一台映射和受保护历史不变；返回结果及日志只涉及自有 profile。

独立 QA 自编 `qa2_offset_confirmation_preserves_names_across_plcs` 在两台均已有双语值的合成配置上实际执行 `offsets_at` 和 `confirm_offsets_at`：两台名称与受保护历史保持。正式候选 7 项 `point_display_names` 回归另覆盖 UI 已清理/服务端清理两种删除、旧双空项不因读取/无关保存静默改写、同 ID 原样和改源复导、旧无 `displayNames` 请求、一次 CAS 及并发、过期/伪造/篡改负例。首次运行 QA 自编测试的 TMPDIR 未包含夹具强制的 `daa-008-r2-a-` 标识，harness exit 101，在到达产品逻辑前失败；改为本次独有的合规子目录后同项 exit 0、1 passed，不将首次结果当作产品失败或通过。

## 旧 profile：读取、启动与关闭分别测量

仅在自有 `/private/tmp/daa018-qa2-gQoXyhmB` 建立合成 profile；旧 debug `local-validation` 二进制 SHA-256 `16e7fabea7ac2d37ecb19408714975d29dc79323bec75dae280d4f4a09f01d21`，新程序为本轮从正式源码 `--locked --offline --features local-validation` 构建的 debug validation 二进制，SHA-256 `79c3e50827d7df86b3dbeb57ef1194e1d678cb6da86b3eafcd47c93b0474a14e`。使用明确绝对 `--env-file`、`--profile-dir` 和 `--fixture-file`，进程环境删除 `DAA_*`；这两个都是**测试专用 validation 入口，不是普通 native**。旧版种子使用本任务自有 fixture.env 中的 `DAA_PLC_READ_ALLOWED=true` 生成合成样本，`local-validation` 强制 fixture 且选择 `FixtureTransport`，不是访问真实 PLC；禁止网络上报。每个 profile 有 1 条旧 revision、4 个样本，两库 user_version 分别为 2/4。

1. 在已启动的新 validation 程序中，单次 `daa_get_configuration` 前后逐表比较 config/runtime 中所有表、完整 schema、user_version，并比较该自有 profile 的所有文件 SHA：**均未变化**。旧草稿、来源、revision payload/SHA、contexts、样本、队列和回执保持；这只证明所测读取调用零写。
2. 启动新程序后、读取命令之前，`runtime_events` 从 11 增至 12（`runtime_started`），`runtime_metadata.clean_exit` 发生变化；正常关闭后从 12 增至 13（`runtime_stopped`），`clean_exit` 再变化；两个阶段均改变 `runtime.sqlite` 和 `logs/runtime.jsonl` 文件 SHA。正常启动/关闭因此不是全 profile 零写。
3. 旧 validation 在另一份分别由旧版新建且内容等价的合成 profile 上同样分段：启动和关闭各追加相同类型事件、切换 clean-exit 并修改相同类型文件；单次读取同样所有表和文件不变。它支持上述是已有启停行为的结论，不证明普通 native 行为。
4. 在第一份合成旧 profile 上用新 validation 的真实单点 preview/confirm 保存双语新字段后，旧 validation 打开该 profile exit 2，错误 `profile_contract_business_admission_failed`；拒绝前后所有 SQLite 表、schema、user_version 和 profile 文件 SHA 均不变，未新增空库。该结果不替代旧普通 native 的安全拒绝、无误采及无空库验证。

DA18-04 的 `零写读取` 以所测读取调用及旧草稿/版本/样本原字节不变如实报告；不扩大为启动到退出零写。若需要求整个进程生命周期或日志零写，现有实测不满足该更宽口径，应由 PM/Human Owner 对已批准语义明确处理，不由 Verification 静默修改 spec。尝试直接复制本轮自有已封存合成 profile 构造对照时，因路径/inode 身份封存被 `profile_contract_invalid` 安全拒绝，exit 2；随后分别用旧 validation 新建两份合成 profile 才完成上述新旧对照，未改写封存凭据或复制任何真实 profile。

## 按验收标准的当前证据

| 标准 | QA2 结果与边界 |
| --- | --- |
| DA18-01 | 部分：严格闭合对象、缺省/空/null/未知键、重复 ID、256 UTF-8 字节、Unicode 与单侧/双侧清空的 Rust 定向测试通过；最终原生界面及重开未测。 |
| DA18-02 | 部分：源码当前 locale 仅取对应值、空值为空；Node 模拟宿主覆盖分语言编辑、取消和先保存既有草稿的边界，中英 locale 各 169 叶键且对称；原生顶栏切换/取消及对草稿、样本的完整观察未测。 |
| DA18-03 | 部分：上述正式 dispatch 反例、同 ID 原样/改源复导、并发及删除，以及 QA 自编的带名称偏移确认通过；未把点/DB 其他删除和所有现场来源外推为已测。 |
| DA18-04 | 部分：合成旧 revision/样本的 validation 读取调用零写，旧 validation 对新字段安全拒绝且原表/文件不变；启动/关闭有上述既有写入；旧普通 native 尚未运行。 |
| DA18-05 | 部分：合成新旧 revision、独立 comment、样本定义、旧冻结/排队和 ACK 保全测试通过；新旧内容不会被要求相等；未读取用户历史。 |
| DA18-06 | 部分：正式源码 runtime4 worker 在 fake `Capture` transport 捕获旧 `NeverSent` 样本转 v2、新 revision 样本及冻结重试；两语言 sentinel 与 comment 未出现在正文，name/value 与样本一致，v2 没有 comment，冻结重试 bytes 相同。旧账本需复核状态与 runtime3 start/resume 拒绝有定向测试；源码中旧 v1 建批/冻结/选批及 `Transport::post` 为 `#[cfg(test)]`，runtime4 产品 worker 用 `post_sample`，正式 feature binary 仅编译检查。没有真实 POST。 |
| DA18-07 | 未完成：Node、vue-tsc 和 Vite 构建通过；最终原生界面的编辑、中英、顶栏、列宽拖拽、跨重启/恢复及旧功能回归均未测。 |
| DA18-08 | 部分：正式回归和独立普通保存反例覆盖单点技术名/comment/双语同候选、SQLite 临时 trigger 计一次 CAS、旧请求、跨 PLC 拒绝和不经 preview 的普通保存拒绝；最终原生 UI 未测。 |
| DA18-09 | 部分：伪造/篡改、过期、旧 ETag/并发、清空、先行保存及未知结果重读门禁在隔离 Rust/Node 测试中通过；最终原生取消和故障交互未测。 |
| DA18-10 | 部分：test-only v1 本地冻结正文保留完整 contextUtf8，包含两种 sentinel 且 context/body SHA 自洽；旧冻结和 ACK 记录在合成测试中保持。生产账本本地重构保留，不能把测试构造称为网络发送，也不声称真实历史已扫描。 |

## 环境、命令与结果

macOS 15.7.7 arm64；rustc/cargo 1.89.0；Node 22.19.0；pnpm 11.11.0。除标为 QA 副本和脚本外，工作目录为正式 DAA 目录。`E` 表示 `env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT CARGO_TARGET_DIR=/private/tmp/daa018-qa2-gQoXyhmB/target TMPDIR=/private/tmp/daa018-qa2-gQoXyhmB/daa-008-r2-a-qa2 DAA_PLC_READ_ALLOWED=false`；CARGO target 为本轮私有副本，`--locked --offline`，不安装依赖。

| 命令或操作 | 实际结果 |
| --- | --- |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib qa2_ordinary_dispatch_requires_preview_and_preserves_every_unrelated_record -- --nocapture --test-threads=1`，QA 副本 | 合规 TMPDIR 后 exit 0、1 passed；首轮目录标识不符的 exit 101 已在上文记录。 |
| 同命令将 filter 换为 `qa2_offset_confirmation_preserves_names_across_plcs`，QA 副本 | exit 0、1 passed。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib <filter> -- --test-threads=1` | `point_display_names` 7 passed；`daa018_` 3 passed；`legacy_engine_does_not_dispatch_or_rewrite_inflight_v1_evidence` 1 passed；`source_import_tests` 4 passed；`point_naming_tests` harness 4 passed（其中 `native_owned_legacy_seed` 因环境变量未设置直接返回，不能算 native 证据）；`old_ledger_requires_proof_across_parts_batches_and_relations` 1 passed；各 exit 0。为获取不截断的统计曾重复运行过滤组，均 exit 0；既有 `empty_for_test` dead-code warning。 |
| `E cargo build --manifest-path src-tauri/Cargo.toml --locked --offline --features local-validation --bin daa-local-validation` | exit 0，9 条 dead-code warning；只用于自有 fixture。 |
| `E cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --bin aiis-data-acquisition-agent` | exit 0；只编译检查，不启动普通二进制或采集。 |
| `python3 /private/tmp/daa018-qa2-gQoXyhmB/seed-old.py`，另以 `seed-lifecycle-{new,old}.py` 分别种子；`compat-qa2.py`、`lifecycle-qa2.py` | 合成种子和上述分段检查均 exit 0；旧 validation 新字段拒绝是脚本内预期的子进程 exit 2。最初复制已封存 profile 的对照脚本 exit 1，子进程按契约 exit 2；另建 profile 后成功。脚本入口环境指定私有 TMPDIR 并移除 DAA 变量，子进程进一步移除全部 `DAA_*`。 |
| `node --test tests/point-editing.test.mjs tests/facts-delivery.test.mjs tests/time-and-history-preferences.test.mjs` | exit 0、29 passed；内存 IPC / 无 DOM Vue 模拟宿主，MockTimers experimental warning；不代表原生。 |
| `pnpm exec vue-tsc --noEmit`；`pnpm exec vite build --outDir /private/tmp/daa018-qa2-gQoXyhmB/ui --emptyOutDir` | 均 exit 0；Vite 有第三方 PURE 注释与大 chunk warning，未启动构建产物。前端命令均移除 DAA 环境变量、指定私有 TMPDIR 和禁止 PLC 读取。 |
| `rustfmt --check --edition 2021` 对本次 Rust 配置、命名与新测试文件；候选 19 个已跟踪文件 `git diff --check` | 均 exit 0；untracked 新测试文件 `git diff --no-index --check /dev/null <file>` exit 1 表示与空文件不同，未输出空白错误。 |
| 递归比较 plc 两种 locale 键；检查两份 USER_GUIDE 和两份 local_store README 相对链接 | 均 exit 0；各 169 叶键、差集为空，4 文件中 26 个相对链接无缺失。 |

## 阻塞、资源与 handoff

此前隔离事故事实见 QA1 和 Development 历史：CUA 可能重新绑定或启动默认真实 profile，具体路径及启动/退出写入仍未知，不能称该事件零写。本轮没有启动或附着 GUI/CUA、普通 native，亦未检查、读取、复制、修复、删除或回滚任何疑似真实 profile、缓存或日志；没有真实设备操作或外部发送。继续暂停这些入口，不能因非 GUI 测试通过自行解除。

解除当前阻塞需要协调者/Human Owner 先明确处理暂停，并建立可证明不会回退或重新绑定用户 profile 的隔离运行条件、唯一合成 profile、禁止真实设备/网络的约束；再对最终候选执行中文/英文原生点表及编辑/取消、顶栏切换、列宽拖拽与跨重启/恢复默认和旧功能回归，并在受控隔离副本测试旧**普通 native**对新字段的安全拒绝、无误采及无空库。validation feature、Node 模拟和旧 incognito 观察不能替代。完成剩余检查后由协调者安排必要的独立 Verification，再进入 Human Owner 最终验收。

本轮自有 `/private/tmp/daa018-qa2-gQoXyhmB` 包含 QA-only 临时源码副本/测试、隔离 target、fixture 合成 profiles、两种 validation 二进制、分段脚本及静态 UI 构建；保留至后续核验不再依赖，由协调者按资源规则确认归属及占用后回收。前述失败复现与本轮必要结果已写入 checklist，不只依赖临时路径；本角色不回收 Development/QA1 资源、系统诊断或任何真实资料。`qa_blocked` 结果交 Human Owner 知悉，不构成最终验收，不授权导出/导入、生产部署、真实数据库、设备或上报。

---

# Coordinator 隔离前置探针（2026-11-17，Asia/Shanghai）

Human Owner 选择继续先完成双语验收。下述为本会话 coordinator 自报及其工具输出的摘要；本记录者未独立执行这些探针，也未据此开展新的原生 QA。环境为 macOS 15.7.7 arm64；完整命令和策略原文未在本节提供。

- Coordinator 在 DS 和 DAA 各自 `.local` 下建立唯一自有临时文件哨兵：`sandbox-exec` 对直接进程、普通子进程及符号链接拒绝读取和写入自有 `other` 目录，允许自有 `own` 目录读写。Python UDP `connect(127.0.0.1, 9)` 未发送数据：允许网络的对照 exit 0；`deny network*` 后返回 `PermissionError` / `EPERM`，exit 1。普通工具沙箱内首次调用 `sandbox-exec` exit 71；经 auto-review 放行后合成探针可用。
- 更严格的全局文件读写白名单导致合成 `cat`、`touch`、`true` 进程 `SIGABRT`，该策略未成立。Coordinator 报告按时间、程序、Python 父 PID 和 `SIGABRT` 核对后精确清理三份由这些进程生成的系统报告，结果 `removed 3`、`all_absent true`。这是本轮新事件，不改变此前 DAA 原生隔离事故的未知影响，也不能称此前事故零写。
- Coordinator 随后改用禁止全局写、限制用户目录读取、禁止网络与 Mach 的策略，合成 canary 通过；本轮 `.local` 探针目录均由 coordinator 清理。这些结果不证明 AppKit / WebKit / XPC、CUA 重新绑定或旧 DAA 普通 native 的隔离安全。

本轮未启动或附着 DS / DAA GUI、未运行旧普通程序、未操作真实设备或发送网络 POST；UDP 探针未发送数据。未实施 JSON 导入 / 导出或修改用户手册。合成 sandbox 探针不计为 DA18-04 或原生 UI 验收；系统生成诊断与原生 UI 隔离仍须先证明，原有其他 gate 均保留。当前状态继续为 **`qa_blocked`**，最终验收由 Human Owner 决定。

---

# Coordinator 非 GUI 启动配置探针（2026-11-17，Asia/Shanghai）

以下是本会话 coordinator 自报的探针结果，本记录者未独立执行这五项。Coordinator 将 `TMPDIR` 指向 DAA `.local` 下唯一自有临时根，harness 初始进程环境仅含 `PATH` 与 `TMPDIR`；使用 QA2 保留的 Rust 测试 harness `/private/tmp/daa018-qa2-gQoXyhmB/target/debug/deps/aiis_data_acquisition_agent_lib-7d909662ee5e8aff`，SHA-256 `a306a7c7488b6b2305b8843fa5cc407a102c2a02f47f8d9f293965b11530600b`。每项以 `--exact <完整测试名> --nocapture --test-threads=1` 分别运行，均 **exit 0、1 passed**：

- `config::startup_env_tests::startup_env_owned_file_and_profile_fail_before_writes`
- `config::startup_env_tests::startup_env_relative_profile_uses_selected_file_directory`
- `config::startup_env_tests::startup_env_relative_profile_is_independent_of_working_directory`
- `config::local_bootstrap::startup_env_tests::startup_env_relative_profile_reaches_ordinary_bootstrap`
- `config::local_bootstrap::startup_env_tests::startup_env_read_admission_is_process_only_and_stopped`

这些检查覆盖合成文件和进程配置函数；既有 harness 未重编译，不代表正式普通启动，也未启动 native 或测试图形界面，不能证明旧普通 binary 的安全拒绝。Coordinator 报告运行后唯一 `.local` 临时根已删除；没有使用真实 env、profile、PLC 或发送 POST。隔离 gate、旧普通 native 和原生 UI 验收仍未完成，当前状态继续为 **`qa_blocked`**。

---

# Coordinator 合成配置与上报探针（2026-11-17，Asia/Shanghai）

以下为本会话 coordinator 自报的执行结果；本记录者未独立执行这些检查，不将其记为新的独立原生 QA。

1. Coordinator 在 DAA `.local` 新建唯一自有根，并核对旧、新 validation 二进制的 QA2 SHA-256 分别为 `16e7fabea7ac2d37ecb19408714975d29dc79323bec75dae280d4f4a09f01d21`、`79c3e50827d7df86b3dbeb57ef1194e1d678cb6da86b3eafcd47c93b0474a14e`。sandbox 限制读写自有根并禁止网络；自有文件、他有合成哨兵和符号链接 canary 分别 exit 0 / 1 / 1，UDP connect 被 `EPERM` 拒绝。旧 validation 以强制的内存 `FixtureTransport` 在最终 profile 原位生成 1 条旧 revision 和 4 个旧样本；新 validation 经命名 preview / confirm 保存中英文双语 draft。比较旧 revision、source、context 和 sample 数据摘要不变；旧 validation 面对新 draft exit 2，返回 `profile_contract_business_admission_failed`，所查历史不变。这是测试专用 validation，不是旧普通 native 或 GUI 验收；coordinator 报告本组两个自有 `.local` 临时根已删除。
2. Coordinator 首次将既有 Rust 上报测试的 `TMPDIR` 指向 `.local` 自有临时根时，测试 helper 报 `fixture root is not a system temporary path`，v2 测试 exit 101，未到实际正文断言；该失败是测试夹具路径准入问题，不归因产品。随后使用全新 `/private/tmp` 自有系统临时根，未使用 `.local/dev`；在相同网络禁止及自有 / 受保护文件 canary 条件下，使用 QA2 保留测试 harness（SHA-256 `a306a7c7488b6b2305b8843fa5cc407a102c2a02f47f8d9f293965b11530600b`）分别执行以下测试，均 exit 0、1 passed：

   - `services::local_delivery::tests::daa018_v2_transport_old_new_and_frozen_retry_exclude_display_names`
   - `services::local_delivery::tests::legacy_engine_does_not_dispatch_or_rewrite_inflight_v1_evidence`

   前者用内存 `Capture` transport 检查旧、新及冻结重试的 v2 正文不含 `displayNames`；后者检查旧 v1 引擎不 dispatch。没有真实 POST 或 PLC 操作。Coordinator 报告自有系统临时根及 canary 目录已清理。

上述结果不解除普通 native 和原生 UI 的 blocker，不构成新、旧普通程序兼容验收；所有已有证据和此前隔离事故的未知影响保留。当前状态继续为 **`qa_blocked`**，最终验收由 Human Owner 决定。
