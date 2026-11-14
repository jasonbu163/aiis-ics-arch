Task ID: DAA-012
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: AC01–AC03 独立验证通过，交 Human Owner 最终验收。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-012 r1 独立验证

2026-11-13（Asia/Shanghai）。命名 Verification `/root/daa012_qa` 在 fresh context 接收精确 Development handoff。核对了根项目契约、适用目录的 README/PLAN、完整任务 bundle、正式源码、差异和测试输出。用 `project-governance`、`aiis`、`rust-runtime`、`desktop-tauri` 和 `code-document-indexer` 复核对应范围。项目角色副本与当前 AIIS 源 profile 的指令一致，配置 effort 分别为 `xhigh` 与 `max`。本轮使用命名 Verification，结论不依赖配置值推断运行参数。文档前置见 ARCH-ACQ-004 的 QA7 记录。 [项目契约](../../../../AGENTS.md) · [工作流](../../../../.codex/workflows/development-lifecycle-workflow.md) · [文档前置](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/checklist.md#独立验证-qa7--采集指南返工)

## 候选身份

交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，Git HEAD `fd999224a8756feda314a33148304b4bf3461876`。既有未提交内容以 Development 交接前的原字节为比较基线。逐一重算 14 个获批 Rust 文件的基线、私有候选与正式源码摘要，确认 8 个产品 Rust 文件与 1 个现有测试文件有差异，其余 5 个可调整测试文件与基线逐字节一致。9 个变更文件逐项匹配交接的 before/after 表，测试与构建均从正式路径执行。 [批准规格](spec.md) · [Development 交接及逐文件摘要](tasks.md)

| 独立重算的输入 | SHA-256 |
| --- | --- |
| 批准后的 `spec.md` | `b03635116cd6709bef34e186b90a3edcf7f4869f3e3aed9d65f93ef8e10ad214` |
| 已交接的 `tasks.md` | `e2a622bd3a227df83c2709d46d776720cf990601cf423abcced929f3c2c485a2` |
| 14 项基线清单 | `1cb7f78e8d1676372cc18d45f4b3124b69cc8b6c09e4f60411b328972a003b21` |
| 9 项交接清单 | `fc98fec28605042fa596c2a6c4f743e81dc4b35ca645460bff44022ef96e5c7f` |
| 以基线和正式原件生成的 unified diff（3 行上下文） | `2791bb16b590fb127dabf7bc3e9354c1c7a93aa182c75dcf1f269745a80712bb` |

## AC01 · 普通启动与锁定构建

macOS 15.7.7（24G720）arm64，Rust/Cargo 1.89.0，Node 22.19.0，pnpm 11.11.0，Tauri CLI 2.11.3，Vite 5.4.21。QA 在自有 `/private/tmp/daa012-r1-qa-j0rRBoTE` 下 APFS 克隆 Development Cargo cache。`CARGO_NET_OFFLINE=true`，`CARGO_TARGET_DIR` 指向 QA 私有 `target`，清除继承的 Rust lint 参数。`DAA_PROFILE_DIR` 指向新建的绝对 `profile` 路径，`DAA_ENV_FILE` 指向私有空文件，`DAA_PLC_READ_ALLOWED=false`，清除其他继承的 `DAA_*`。配置、锁及运行日志均落入该临时 profile。用户 `.local/dev` 只核对元数据时间，现有两库时间早于本轮启动，原 env 与历史库未被 QA 打开。 [应用启动配置](../../src-tauri/tauri.conf.json) · [profile 选择](../../src-tauri/src/config/mod.rs)

1. 在 DAA 应用根目录执行普通 `pnpm tauri dev`。Vite 在 177 ms ready，`http://127.0.0.1:15191/` 实测 HTTP 200。Tauri 实际执行 `cargo run --no-default-features --features rust-snap7-driver --color always --`，debug 构建进入 DAA 二进制，启动段 DAA 编译告警和错误均为 0。 stdout 与临时 profile 的 `runtime.jsonl` 都记录 `runtime_started`、`result=stopped`。源码启动路径以停止的采集意图和默认停传控制状态初始化。验证脚本退出 0。 [启动状态](../../src-tauri/src/services/local_supervisor.rs) · [上报控制状态](../../src-tauri/src/services/local_delivery.rs)
2. 在 `src-tauri` 运行 `cargo clean --offline -p aiis-data-acquisition-agent`，只清 QA 私有 `CARGO_TARGET_DIR` 的该包缓存，退出 0。随后执行 `cargo build --locked --offline --no-default-features --features rust-snap7-driver --bin aiis-data-acquisition-agent`，实际重新编译正式源码中的 DAA crate，10.97 s，退出 0，完整构建输出为一条 `Compiling` 与一条 `Finished dev profile`，0 告警、0 错误。
3. 复核 Development 基线完整构建日志和退出码文件，51 条 `dead_code` 诊断及 Cargo 汇总一致，分别为 HTTP 29、domain 8、local store 10、service 4。基线退出 0。基线日志 SHA-256 `dd0c52894e4bef525e7e198279d841e7d32b8a274ab057bff76983e78e5ded5b`，QA 重编译日志 `2c82248b8ad37467a59c492c14b179c5ca2b005282306dc01b829d7d9fe00a77`，QA Tauri 终端日志 `c504342100d928d1e83806cbede0b9428dd0c118373c5927d345a67c15c002bd`。

原生启动的持久日志实测行如下。

```json
{"at":"2026-11-13T14:53:12.705+08:00","error_code":null,"event":"runtime_started","process":"daa-local","resource":"instance","result":"stopped"}
```

## AC02 · 既有回归

在正式 `src-tauri` 对每个 filter 独立执行 `cargo test --locked --offline --no-default-features --features rust-snap7-driver --lib <filter> -- --test-threads=1`。`TMPDIR` 指向 QA 自有的 `daa-008-r2-a-fixtures`，本机回环只用于现有 HTTP mock。七次命令均退出 0，共 49 个顶层测试通过。已有 `#[cfg(test)]` 的 `src/config/mod.rs:85` 中 `AgentConfig::empty_for_test` 在 lib test 构建有 1 条 `dead_code` 告警，位于获批源码范围外。 [HTTP 夹具](../../src-tauri/src/infrastructure/facts_http_tests.rs) · [上报夹具](../../src-tauri/src/infrastructure/local_store/sample_upload_tests.rs) · [profile 夹具](../../src-tauri/src/infrastructure/local_store/profile_contract_tests.rs)

| Cargo filter | 结果与代表性证据 |
| --- | --- |
| `infrastructure::facts_http::tests::` | 6/6。原 UTF-8 正文、样本路径、无 Bearer，拒绝超限正文及 URL 凭据。 |
| `services::local_delivery::tests::` | 14/14。worker/HTTP 超时及停传边界，退避和时钟行为。 |
| `infrastructure::local_store::delivery_tests::` | 13/13。旧 v1 冻结、分片、拒绝和回执账本断言。 |
| `infrastructure::local_store::sample_upload_tests::` | 13/13。原字节重试与匹配回执才确认，目标重绑、来源绑定、旧账本与新版重开保护。 |
| `infrastructure::local_store::profile_contract_tests::profile_contract_partial_ack_and_rejected_parent_are_valid_cold_states` | 1/1。v1 部分 ACK 和已拒绝父批次可冷态重开。 |
| `infrastructure::local_store::profile_contract_tests::profile_contract_factory_initializes_and_cold_reopens` | 1/1。受支持 profile 初始化与冷重开。 |
| `infrastructure::local_store::profile_contract_tests::profile_contract_business_ledger_refusal_before_and_after_native` | 1/1。账本前检/后检拒绝及保护。 |

## AC03 · 差异与交付检查

- 完整对比 9 文件。生产路径保留 `build_cycle` 的 `sourceGeneration` ID 校验、历史 `verify_success` 和拒绝回执 `classify`。`schema.rs` 仍使用已校验的原正文与分片证明，v1 详情与列表、v2 HTTP 入口、冻结/重试/回执处理和 `commit_cycle_with_reporting` 继续走既有调用路径。旧预览和探测的具名 IPC 原本即返回 `legacy_delivery_read_only`。 [历史校验](../../src-tauri/src/infrastructure/local_store/schema.rs) · [v2 HTTP](../../src-tauri/src/infrastructure/facts_http.rs) · [具名 IPC](../../src-tauri/src/commands/local_delivery.rs)
- 变更为测试专用定义/载荷的 `#[cfg(test)]`、无调用旧包装的移除，以及两处文件头对应说明。测试差异仅移除四个无调用 GET mock 实现，现有测试和有效断言保留。逐行确认新增 lint 压制、伪造调用、可见性扩张、依赖/锁文件、IPC、HTTP、SQLite DDL 与工具链改动均为 0。`CODE_INDEX.md` 现有 DAA 分组条目覆盖保留路径。 [代码索引](../../../../CODE_INDEX.md)
- 对 9 个 touched Rust 文件执行 `rustfmt --edition 2021 --check --config skip_children=true <九文件>`，对工作树和暂存区执行 `git diff --check`、`git diff --cached --check`，均退出 0。本 bundle 的相对链接及锚点、尾随空白用 Python 标准库检查，均通过。
- 当前 `tasks.md` 可凭明确状态、正文 handoff 与已固定摘要验证，但缺少 `project-governance` 规定的两条独立元数据 `Allowed Writers` 和 `Handoff`。本条作为文档格式发现交回协调者，由 Development 补录。本项不影响 r1 技术验收证据。

## 交接与资源

**`qa_passed`，AC01–AC03 通过。** 证据覆盖 macOS 标准启动、正式源码锁定构建和定向合成回归。Windows 原生、发布打包、现有 `.local/dev` 采用、DS、项目 dev API、MySQL、真实 PLC 与上传联调仍归各自范围。

QA 在启动检查完成后对自己以 `start_new_session=True` 启动的进程组 3322 发 `SIGTERM`，Tauri 包装进程状态 `-15`，`ELIFECYCLE` 尾行出现在主动停止后。`lsof` 复核该组、15191 监听和 QA profile 锁均无占用。QA 只写本 `checklist.md`，临时构建缓存、日志和合成 profile 独立存放。QA 专用 `/private/tmp/daa012-r1-qa-j0rRBoTE` 与 Development 专用 `/private/tmp/daa012-r1-dev-xk6hgocn` 的必要证据已汇入持久记录，交协调者按工作流核对占用后回收。

## Human Owner 最终验收

待 Human Owner 决定。

## 交接元数据复核

Development 已补录 `Allowed Writers` 与 `Handoff`。更新后 `tasks.md` 的 SHA-256 为 `ba0d0528223bba2e2f513a6520935cb47f7eec1db7634e5fd7727cce78536982`。在内存中去除这两行后重算摘要，与上表原交接摘要一致；规格和 9 个正式源码摘要也全部匹配。格式发现关闭，AC01–AC03 沿用本轮独立证据，待 Human Owner 最终验收。 [Development 交接](tasks.md)
