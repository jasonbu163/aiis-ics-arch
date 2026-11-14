Task ID: DAA-012
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: 已交 fresh-context QA / Verification，独立验证结果见 checklist.md。
Workflow Mode: STD
Spec: [DAA-012 r1](./spec.md)
Spec SHA-256: `b03635116cd6709bef34e186b90a3edcf7f4869f3e3aed9d65f93ef8e10ad214`
Updated: 2026-11-13 Asia/Shanghai

# Development 事实与交接

## 授权、基线和实际范围

Human Owner 指示“调整好文档之后，修复好daa的报错。其他先别动。”文档前置由 ARCH-ACQ-004 QA7 记录；此任务只处理 r1 列出的启动警告。交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，Git HEAD `fd999224a8756feda314a33148304b4bf3461876`，有既存 DAA-010 / ARCH-ACQ-004 等未提交修改与未跟踪文件；本任务未重置、暂存或提交。开发前对八个允许源码文件及六个可调整测试文件记录 SHA-256，整合时 14 项均与初始基线一致。先在仅含源码依赖的私有副本中开发和验证，再逐文件校验并整合至正式工作树；不把私有副本视为最终交付。

以下路径相对 `automation-world/data-acquisition-agent/src-tauri/src/`；before/after 为该任务开始时的现有工作树内容与本次交付内容 SHA-256，不以 Git HEAD 误作并行修改基线。除表列九个文件及本 `tasks.md` 外，本任务未写其他项目文件。`CODE_INDEX.md` 对应条目为文件组及能力说明，未因本任务发生结构失准，故未改动。

| 路径 | 开始时 SHA-256 | 交接时 SHA-256 |
| --- | --- | --- |
| `domain/facts_wire.rs` | `f857eb79280011466b2192a6e170ae082fbbf774b785a4388df65a8faf8f8ed5` | `db4c83964523687b50d887897e3fecef57c64cf3ce00850ca32cb6866ca0aefa` |
| `domain/local_delivery.rs` | `15f8fb76056819c0fc01b225837e9ef2414e895e6d555bc12bac951a9395ccf6` | `908a8ee13f5bebd0eb5ba49f3fef39deb8072adc60e8521f1cc7ee59b9c71752` |
| `domain/sample_upload.rs` | `9ae8f197fe8bd7fad41553593de6293ad5af88fb2e6ec59094f31d73f8f6f925` | `72274a2ffa5bbdf49dfdc62a32680b4cdc432b5b7f4a6ced13e329b5fe2d498e` |
| `infrastructure/facts_http.rs` | `7dd885c923b4bf9bce78a59506a874ac2c4f2adbe6c1e9b78cbbd65114bc90e4` | `c8cbbc5138e67bb343239bbff5208f9f3333ec475545d572c013da9669561601` |
| `infrastructure/local_store/delivery.rs` | `3d1e3a4e1d8c89ef6a18fc219c7fd5340f1d73c18687238924a6e82447e7d028` | `045e14cd3924889aa0ea4e58a45dfd660ea7348f3e0576b612b2111b57cd08b9` |
| `infrastructure/local_store/mod.rs` | `f7fb17c11597e37ca84202dfef8e6ff71b887bd830afb2426a55d5e86a023973` | `72f6805e37637f191c5ee9f23ffcd160ebd85cf56765909cfcc07bb239b75059` |
| `infrastructure/local_store/runtime.rs` | `fc4637a0ab942498180aa858f40c921414968c4a9a647811f899d426e8f35c9d` | `e25b85f99afc875a11855a4ac5c2fb7d55c9c37237ca3bb7a0e355339d38414e` |
| `services/local_delivery.rs` | `8e25d049a22d19bcec83351840eabcec911028e757257e1ed42aacdf70788909` | `dc14cc9df50b27c0c30728b3e098271f262088d170a05b3f4e7a4f552fe589f2` |
| `services/local_delivery_tests.rs` | `21e6f60ccf19ad89b8058b66aee558061cd59fe525ada929acf7fb0fa98d08d2` | `e41ef8893d353619963ac62adaf7fae71c90f32e0a3d663d1f4234768bffc4af` |

完整十四项基线清单在本轮自有临时目录的 `baseline.json`，SHA-256 `1cb7f78e8d1676372cc18d45f4b3124b69cc8b6c09e4f60411b328972a003b21`；九项改动前后清单为 `handoff-manifest.json`，SHA-256 `fc98fec28605042fa596c2a6c4f743e81dc4b35ca645460bff44022ef96e5c7f`。前后内容暂存 `baseline/` 与 `project/`，供独立 Verification 按清单审计；正式工作树每项 after 均已与候选逐字节 SHA-256 核对。

## 修改说明

- 对旧批次派发、时钟与写回中确有既有测试覆盖的定义，按需限制到测试构建；清除既无运行也无测试调用的旧客户端 GET 探测、调度和孤立引用。`services/local_delivery_tests.rs` 只删除已移除的 GET trait 对应四个无调用 mock 方法，保留测试与断言。
- 历史 v1 SQLite 回执核验仍在生产构建调用 `classify`；保留正常构建所需的拒绝/成功校验流程，测试独用的结果载荷和旧组批材料限定于测试。历史 source generation 仍在 `build_cycle` 的原有 ID 校验循环中校验。v2 单样本目标、派发、重试、请求及回执和 SQLite DDL 未作合同变更。
- 未通过 `allow/expect(dead_code)`、扩大可见性、伪造调用或空读字段处理告警；不修改依赖、锁文件、工具链、Tauri 配置、IPC、API 或数据库结构。生产运行的旧 v1 历史校验和 v2 路径保留。

## Developer 自检

环境：macOS 15.7.7 arm64；`rustc 1.89.0`、`cargo 1.89.0`；使用现有 Cargo 锁文件和离线缓存。所有命令在 `automation-world/data-acquisition-agent/src-tauri` 中运行；`CARGO_TARGET_DIR=/private/tmp/daa012-r1-dev-xk6hgocn/target`，`TMPDIR=/private/tmp/daa012-r1-dev-xk6hgocn/daa-008-r2-a-fixtures`。测试数据仅在本次专属临时目录；未启动真实 DAA profile、DS、项目 dev API/MySQL 或实际 PLC。

1. 基线与交付构建：`cargo build --locked --offline --no-default-features --features rust-snap7-driver --bin aiis-data-acquisition-agent`。基线相同命令退出 0，DAA crate 汇总 51 warnings；最终正式工作树同命令退出 0，DAA crate 0 warnings / 0 errors。完整输出分别为 `baseline-build.log` 和 `formal-build.log`。该构建 feature、binary 和 debug profile 与普通启动的 Rust 编译路径一致；本角色未执行原生窗口启动，由 fresh Verification 使用独立 profile 检查。
2. 现有合成回归：对每个下列 filter 执行 `cargo test --locked --offline --no-default-features --features rust-snap7-driver --lib <filter> -- --test-threads=1`，候选版本与正式文件摘要一致；均退出 0，共 49 个顶层测试通过。回环监听只在本机 127.0.0.1 临时端口，故在本机网络沙箱允许后运行。逐组完整日志 `final-test-0.log` 至 `final-test-6.log`。
   - `infrastructure::facts_http::tests::`：6/6。
   - `services::local_delivery::tests::`：14/14。
   - `infrastructure::local_store::delivery_tests::`：13/13。
   - `infrastructure::local_store::sample_upload_tests::`：13/13，含原字节重试、匹配回执与旧 ledger。
   - `infrastructure::local_store::profile_contract_tests::profile_contract_partial_ack_and_rejected_parent_are_valid_cold_states`、`profile_contract_factory_initializes_and_cold_reopens`、`profile_contract_business_ledger_refusal_before_and_after_native`：各 1/1。
3. 原沙箱首次执行 HTTP 和 service 套件时，两个 loopback bind 分别在测试文件第 41、473 行返回 `Operation not permitted`（其余 5/6 与 13/14 通过）。单独允许本地回环后，两个失败用例各自复测通过；最终以上四组及 profile 用最终候选重新完整运行均通过。之前两个失败及其复测日志保留于私有目录，不把受限环境首轮记成通过。
4. 上述 `cargo test --lib` 仍报告已有测试专用的 `src/config/mod.rs::AgentConfig::empty_for_test` 一条 warning；该文件不在批准改动面，普通启动等效构建不含此告警。无隐藏 lint；不将测试构建警告误称为 0。
5. 正式工作树九个 touched Rust 文件执行 `rustfmt --edition 2021 --check --config skip_children=true <九文件路径>`，退出 0；仓库根目录 `git diff --check` 退出 0。两项与交接时 SHA-256 对应。改动前候选仅触达上述范围，格式化只处理上述九文件。

6. 对 `spec.md` 与本 `tasks.md` 的本地 Markdown 链接执行路径存在性检查，缺失 0；对两份文件逐行检查尾随空白，发现 0。

## 资源和边界

本任务私有目录 `/private/tmp/daa012-r1-dev-xk6hgocn` 包含基线、候选、编译缓存、合成 profile 和完整测试日志；合成测试及进程已结束。为供 fresh Verification 审核具体基线差异及克隆 `target/` 加速原生测试，暂时保留；独立验证读完且确认无需依赖后由协调者回收整个专用目录，不得删除用户 `.local/dev`、历史库或任务外资源。文档先行的完成证据、正式源码和上述结果并不代表独立 QA 结论或 Human Owner 最终验收。Windows 原生结果不在本任务验证范围。
