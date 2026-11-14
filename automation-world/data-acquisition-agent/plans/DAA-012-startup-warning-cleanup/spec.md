Task ID: DAA-012
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 DAA-012 r1。先完成文档调整，再交 Development 实施启动告警清理。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 清理 DAA 普通开发启动的 Rust 未使用代码告警
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: 本稿第 3、4 节与 Development Lifecycle Workflow
Related Task: DAA-006, DAA-008, DAA-010, ARCH-ACQ-004
Created: 2026-11-13 Asia/Shanghai

# DAA 开发启动 Rust 告警清理

## 1. 目标与当前证据

用户要求清除 2026-11-13 粘贴的 `pnpm tauri dev` 日志中的告警。日志显示 Tauri 调用 `cargo run --no-default-features --features rust-snap7-driver`，DAA crate 产生 51 条 `dead_code` 告警，Cargo 随后完成构建，运行时以停采、停传状态启动。ARCH-ACQ-004 r2 将 Rust 告警清理列为独立范围。 [Tauri 启动配置](../../src-tauri/tauri.conf.json) · [ARCH-ACQ-004 r2 范围](../../../../plans/ARCH-ACQ-004-acquisition-source-registry/spec.md#4-允许改动与交付边界)

| 基线文件（相对 `src-tauri/src/`） | 告警数 | 清理边界 |
| --- | ---: | --- |
| `infrastructure/facts_http.rs` | 29 | 核实旧读接口探测、响应解析及旧批次 HTTP 调用的实际引用。保留现行单样本 HTTP 与共用传输设置。 |
| `domain/local_delivery.rs`、`domain/facts_wire.rs`、`domain/sample_upload.rs` | 6、1、1 | 区分历史账本核验仍使用的材料和仅测试使用的字段、接口及默认构造包装。保留序列化字段和验证语义。 |
| `infrastructure/local_store/delivery.rs`、`infrastructure/local_store/mod.rs`、`infrastructure/local_store/runtime.rs` | 4、4、2 | 核实旧派发、写回、调度及采样包装调用者。保留现有旧库校验、历史可读性和 v2 样本账本。 |
| `services/local_delivery.rs` | 4 | 核实旧投递设置和探测入口、旧回执处理及测试时钟辅助。保留 v2 设置、派发、退避和回执。 |

## 2. 实施范围

- **R01 清理定义与引用。** 逐条核对调用关系。仅被现有测试使用的定义及其导入、初始化按需进入 `#[cfg(test)]`。确认无运行和测试用途的死代码连同孤立引用一起移除。历史 SQLite 核验仍依赖的类型、字段和函数保留在正常构建。若旧模块同时包含仍在使用和仅供测试的代码，按定义处理。禁止新增或扩大 `allow(dead_code)`、`expect(dead_code)`、编译 lint 开关，禁止借扩大可见性、空读字段或伪造调用压制告警。
- **R02 保持现行行为。** 继续使用 `pnpm tauri dev`、现有 Snap7 feature 和运行配置。保持 v2 的上报设置、同一目标与来源绑定、样本 ID 和序号、请求字节、重试及回执确认。保留已有 v1 历史账本和回执、版本化 SQLite 结构与凭据校验，旧派发仍按现有入口停用。普通启动保持停采、停传。
- **R03 精确改动面。** 产品源码限第 1 节表中的八个 Rust 文件。确需调整已有测试引用时，只触及 `src-tauri/src/infrastructure/facts_http_tests.rs`、`src-tauri/src/infrastructure/local_store/{delivery_tests,sample_upload_tests,profile_contract_tests,time_contract_tests}.rs` 和 `src-tauri/src/services/local_delivery_tests.rs`，保留已有有效断言。`CODE_INDEX.md` 仅在结构索引实际失准时同步对应 DAA 条目。任务文档按角色维护，模块双语索引由协调者同步。实现与自检使用 `rust-runtime`、`desktop-tauri`，涉及结构索引时使用 `code-document-indexer`。
- **R04 操作边界。** 现有 `.local/dev`、真实设备、项目 dev API 和 MySQL 的操作归其联调范围。本任务使用合成夹具和任务专有临时目录。排除依赖、锁文件、工具链、Tauri 设置、启动脚本、IPC/HTTP 合同、SQLite DDL、profile 迁移及无关重构、格式改写和其他包的告警。先记录交付工作树基线，保全并行修改。失败时只回退本任务源码差异，保全本地资料。

## 3. 验收

| 编号 | 可核对结果 |
| --- | --- |
| AC01 原构建入口 | 从交付源码按项目锁文件运行 `cargo build --locked --no-default-features --features rust-snap7-driver --bin aiis-data-acquisition-agent`，与普通 `pnpm tauri dev` 的 crate、feature 和 debug profile 一致。保留完整诊断及退出码，51 条基线告警全部消失，DAA crate 无新增告警或错误。核对实际 `pnpm tauri dev` 入口和配置。原生启动可安全执行时，用独立临时 profile 确认日志和停采停传状态。若普通 Vite 端口占用或无法打开窗口，记录限制并提供等效构建证据。 |
| AC02 既有回归 | 运行现有 `facts_http_tests`、`local_delivery_tests`、`delivery_tests`、`sample_upload_tests`，加上受触达的 profile 回归。证据覆盖 v2 原字节重试与匹配回执、v1 账本核验及受支持的旧 profile 重开；无须连接项目 dev 或现场 PLC。用现有合成夹具，保留对拒绝情形和兼容性的断言。 |
| AC03 差异复核 | 检查 touched Rust 的格式、`git diff --check`、改动清单和上述链接。确认无 lint 压制、假调用、可见性扩张、功能及数据契约变化。记录构建/测试命令、环境、退出码、候选身份和资源归属，回收本任务已无依赖的临时资料。 |

## 4. 批准与交接

2026-11-13（Asia/Shanghai），Human Owner 在本会话回复已展示的 DAA-012 r1 方案，确认文档调整完成后实施本稿的 DAA 启动告警清理。获批草稿 SHA-256 为 `2ba59d14d4c5a9252f23972d19cecae5245e407471a5b6bcf07f05a501442302`。Human Owner 指示原文如下。

> 调整好文档之后，修复好daa的报错。其他先别动。

文档调整完成后，由 Development 在同一交付工作树实施本稿范围并记录自检，再交 fresh-context Verification 独立核对，最终由 Human Owner 验收。 [Development Lifecycle Workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)
