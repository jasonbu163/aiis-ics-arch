Task ID: DS-005
Revision: r2
Status: developer_handoff
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Owner Role: Development
Allowed Writers: Development
Handoff: QA2 verdict and evidence remain in checklist; subsequent Owner-requested guide clarification is handed to fresh-context Verification, with Human Owner final acceptance pending.
Approved spec SHA-256: `f9ec8c6941f61b50b31d02a8526c8d53c907486190dd48ae0cc1c374d94851b7`
Approved parent ARCH-PLC-001 r7 SHA-256: `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`
Working tree: `/Users/jason/Desktop/DreamCode/aiis-ics-arch` at base HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`; concurrent governance and DAA work remain present.
Prior r1 tasks SHA-256 before r2 continuation: `a8d2acea744696e4d020d745ae3ec5e1a8ccfad8adebcab3dc4a616a00948a8f`.

## r1 Development metadata（历史）

下列原 r1 头部及其后原开发正文保留；当前有效 Revision、批准摘要与状态以上方 r2 元数据为准。历史时态和失败不得倒改。

```text
Task ID: DS-005
Revision: r1
Status: implementation_in_progress
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Owner Role: Development
Allowed Writers: Development
Handoff: Development in progress; candidate, DEV self-check and coordinated cross-application evidence pending.
Approved spec SHA-256: `fe007553288adbdd426b1ce7edf9ebd8a2d6d0bfa72a549deeb3fb8341975c75`
Approved parent ARCH-PLC-001 r6 SHA-256: `0eb0c10e70507903347b216d2ac712add430fc4511b251a2ad93e00e19ce1408`
Working tree: `/Users/jason/Desktop/DreamCode/aiis-ics-arch`, base HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`; concurrent governance and DAA work existed at start.

```

# Development record

2026-11-17（Asia/Shanghai）：核对 Human Owner 对 DS-005 r1 和父 r6 的精确批准及以上实际文件 SHA。任务目录初始仅有已批准的 `spec.md`；Development 不写 spec 或 checklist。DS 既有 DS-003 / DS-004 的历史和状态独立保留。

初步将 `runtime/src/domain/configuration.rs` 与 `runtime/src/domain/plc_catalog.rs` 的本任务更改写入正式工作树。随后获协调者通知 DS dev 仍在运行，为避免继续触发热重载，保留上述更改、不回滚，并将当前候选复制到任务自有 `/private/tmp/ds005-dev-Cq4eK0/automation-world/device-simulator`；共享 TIA core 同样复制在该临时树内。临时源码、Cargo target、前端输出仅服务本任务实施及合成检查，最终必须整合回正式树并核对一致性。后续协调者报告用户已自行保存并停止两个 dev 应用，相关锁与 Vite 端口经协调者检查已释放；Development 未停止、操作或修改用户进程、`.local/dev` profile 或真实数据。

当前方向是使用现有 `source_versions` 保存 JSON 原字节、可选实例元数据保存本地/外部映射，并对来源、点集和地址重验，不改物理 DDL；模拟监听由用户独立确认。临时候选的首次 `CARGO_TARGET_DIR=/private/tmp/ds005-dev-Cq4eK0/target cargo check --offline --locked --manifest-path runtime/Cargo.toml` exit 0；此结果仅覆盖当时尚未完成的候选，不代表最终自检。完整实现、定向正负例、双语界面、正式树构建和实际文件跨应用联测均在进行中。

# Pending

- 核对并完成严格解析、原始来源和全量映射、编辑保护、保存版本导出、点名与布局确认、端点冲突、TSAP 和 256 字节旧名称。
- 运行精确候选的 Rust、前端、桌面桥接及文档验证，记录命令、退出、限制和文件 SHA；整合到正式源码并重新验证。
- 与协调者及 DAA Development 对齐后，按父 r6 A06 在经核对的 `.local/dev` 实际文件联测；当前尚未执行。保护原有用户配置和历史，不自动连接、采集或上报。
- 完成后才记录 `developer_handoff` 并交 fresh-context Verification；当前没有 QA verdict 或 Human Owner 最终验收。

## 阶段进展与已观察问题（尚非 handoff）

- DS 候选已从任务临时源码树整合至正式工作树；逐个字节核对了 23 个候选路径，当时完全一致；后续对正式树继续修正并发保存保护和映射查找，最终候选 SHA 与复核待冻结。并行修改的 DS PLAN 与 plans 索引未覆盖。未启动两端应用或操作 `.local/dev`。
- 协调者提供的 DAA 合成配置实际服务导出文件 SHA-256 `937c0f3aa0ce583821e4b647a2395a3bc97e0975424a5cb9fe9362f15d320ee5`，含 2 DB、24 点（BOOL/BYTE/INT/REAL），通过隔离 DS 服务进行解析、预览、实际草稿提交、布局/名称确认、版本保存、重开及实际 DS 文件写出；逐 DB/点比较外部身份、技术字段、显示名/描述/来源路径，并核对源文件前后 SHA 不变。命令使用 `DS005_DAA_EXPORT` 指向协调者提供的 `/private/tmp/daa019-dev.MKLyerrV/daa-008-r2-a-fixtures/daa005-test-daa019-export-a7082f7d-6d82-4442-a59f-6eea15640c9b/successful/d1ca2e57-b83d-4b73-a908-b2a482b8b415.json`，`DS005_DAA_EXPORT_SHA256` 为上述摘要，`DS_TEST_RUN_ROOT=/private/tmp/ds005-dev-Cq4eK0/daa-service CARGO_TARGET_DIR=/private/tmp/ds005-dev-Cq4eK0/target cargo test --offline --locked --manifest-path runtime/Cargo.toml --features test-automation --test plc_catalog_import actual_daa_service_file_when_explicitly_supplied -- --exact --nocapture` exit 0、1 passed。此为服务级合成 profile，不是原生界面或父 A06 闭环。
- 隔离候选 Node 测试发现把 Vue reactive preview 直接传给 `structuredClone` 会失败，已改为对 JSON 配置值复制，并增加未知回执和读回期间并发本地编辑测试。正式树 Node `node --test tests/plc-catalog-import.test.mjs tests/plc-catalog-export.test.mjs tests/point-display-names.test.mjs` 后续复测 exit 0，40 passed、1 个旧可选测试 skipped；这是内存组件/状态测试，不是原生 WebView。
- 正式树首轮 Rust 回归并发编译期间，4096 点最大样例测试在 `confirm` 获 `save_receipt_unknown`，该批命令 exit 101；其他当时运行的该测试文件 6 项通过。未盲目重试同一提交。原合成 profile `/private/tmp/ds005-dev-Cq4eK0/formal-tests/d20a8b88-84e6-415b-b3b2-132472268403/profile/device-simulator-v1/config.sqlite` 在测试进程退出后只读检查：draft payload SHA 相符，0 实例、0 来源、0 点，归档 source_versions/source_blobs 各 0，`PRAGMA quick_check=ok`。该次具体结果是未观察到提交，不能推断其他未知回执。
- 减少目录映射逐点查找复杂度后，用全新合成 profile 和正式树运行 `DS_TEST_RUN_ROOT=/private/tmp/ds005-dev-Cq4eK0/formal-tests-after-index CARGO_TARGET_DIR=/private/tmp/ds005-dev-Cq4eK0/formal-runtime-target cargo test --offline --locked --manifest-path runtime/Cargo.toml --features test-automation --test plc_catalog_import complete_maximum_point_catalog_retains_one_source_and_all_mappings -- --exact --nocapture` exit 0、1 passed；该次与前端构建并发，完整测试用时 1.33 秒。该结果不保证任意系统负载下 1 秒存储回执都可获得；未知回执仍须先读回而非重试。
- 隔离副本首轮 Rust 回归因未复制 DAA 两个既有编译夹具且遗漏 `test-automation` 特性而 exit 101；补齐只读夹具和特性后 27 passed、2 ignored。临时副本 `pnpm build` 曾尝试在线依赖状态检查并因无 TTY 拒绝模块目录处理而 exit 1；未安装依赖，之后使用现有项目依赖及补齐只读共享 console-ui 源码重试。正式树 `pnpm exec vue-tsc --noEmit` 与 `pnpm exec vite build --outDir /private/tmp/ds005-dev-Cq4eK0/formal-ui` 均 exit 0；Vite 有既存依赖 PURE 标注和大 chunk 警告。
- 容量补充：合法 DAA 示例 4096 点、无语言元数据的紧凑输入为 515,177 字节，而完整 DS 美化 JSON 约 1,326,435 字节；同一完整内容紧凑输出约 748,672 字节。候选保留普通小文件原有美化格式，仅在美化格式超限时切换完整紧凑 JSON，不丢字段；紧凑结果仍超 1 MiB 则 `catalog_capacity` 拒绝。另一个可解析合成输入 932,177 字节，DS 必需字段使紧凑输出约 1,148,672 字节，无法同时满足 1 MiB 与该输入完整重导；已交协调者及 PM 澄清该预算与验收关系，期间不修改合同上限或省略字段。
- 正式树修复后，以同一实际 DAA 服务文件及 `DS_TEST_RUN_ROOT=/private/tmp/ds005-dev-Cq4eK0/final-formal-tests CARGO_TARGET_DIR=/private/tmp/ds005-dev-Cq4eK0/formal-runtime-target cargo test --offline --locked --manifest-path runtime/Cargo.toml --features test-automation --test plc_catalog_import --test plc_catalog_export --test point_display_names --test configuration_store --test source_import -- --test-threads=1` 执行：exit 0，34 passed、2 个旧式显式兼容探针 ignored。包括归档元数据篡改阻断、事务提交前故障及提交后未知回执、4096 点合法紧凑导出和超额阻断；真实文件服务测试附加的 `DS005_DAA_EXPORT` / `DS005_DAA_EXPORT_SHA256` 与上文一致。
- 正式树在最终 UI 并发保护修正后，`node --test tests/plc-catalog-import.test.mjs tests/plc-catalog-export.test.mjs tests/point-display-names.test.mjs` exit 0，40 passed、1 个可选 fault-log 测试 skipped；`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir /private/tmp/ds005-dev-Cq4eK0/formal-ui`、`cargo fmt --manifest-path runtime/Cargo.toml --check`、`cargo fmt --manifest-path src-tauri/Cargo.toml --check` 均 exit 0。两份手册的 20 个相对文件链接存在，未验证锚点；本次正式候选已对批准文件白名单做差异审计。桌面构建、最终文件 SHA 和原生双端联测待补充。

## 联测前候选（不是 developer_handoff）

2026-11-17，协调者转达 PM 对既有 r6 / 封存 r5 的只读口径澄清：1 MiB 是实际完整输出上限；符合输入合同及本地约束的文件不因未来输出可能超限而拒绝导入。实际输出超额时按实例报告并拒绝，不截断或覆盖，其他有效实例可继续。此澄清不改变 Revision、范围或验收；普通实际文件 A02 / DS05-02/03 / A06 仍须完成。

- 合法约 932 KB DAA 文件的首次实际导入成功；随后为构造两个实例的测试而保存附加确认时收到 `save_receipt_unknown`。未重试同一提交。测试进程退出后只读检查任务自有 `/private/tmp/ds005-dev-Cq4eK0/oversize-isolation/879ecff3-72f6-450f-be65-5930506cb179/profile/device-simulator-v1/config.sqlite`：1 实例、4096 点、1 份来源、1 source blob、0 revision，draft payload SHA 匹配、`quick_check=ok`；第二实例未出现。此观察只适用于该次进程结束后的合成库，不推广到其他未知回执。
- 用全新任务自有 profile，在目录导入预览候选中以**受控测试装配**直接加入确认和第二个手工实例，一次保存并发布；这不是普通 UI 的确认流程。`DS_TEST_RUN_ROOT=/private/tmp/ds005-dev-Cq4eK0/oversize-isolation2 CARGO_TARGET_DIR=/private/tmp/ds005-dev-Cq4eK0/formal-runtime-target cargo test --offline --locked --manifest-path runtime/Cargo.toml --features test-automation --test plc_catalog_import oversized_complete_output_is_rejected_per_instance_without_overwrite -- --exact --nocapture` exit 0、1 passed：超额目录实例预览给出 `catalog_capacity`，实际提交逐项拒绝该实例并保持其既有同名 sentinel；另一有效实例写出完整文件且可重新解析，保存草稿不变。输入单独经严格解析并满足 1 MiB。曾有第一次采用两次保存的同名定向测试 exit 101（上述未知回执）；该历史保留。
- 正式源码 `CARGO_TARGET_DIR=/private/tmp/ds005-dev-Cq4eK0/formal-tauri-target cargo build --offline --locked --features native-s7 --manifest-path src-tauri/Cargo.toml` exit 0，debug 二进制 SHA-256 `b32946b92cb98f3a95f0b3ddd4d3c2b49461a522b10d352c2449144d747528d7`。它由正式源码构建，但尚未以普通 `pnpm tauri dev` 启动或绑定实际 GUI，之后的启动二进制须另行核对。正式前端静态构建位于任务自有 `/private/tmp/ds005-dev-Cq4eK0/formal-ui`；`index.html` SHA `b6aba8acebe39f734a35be9977eba6313bb0026823e7e22aad4a0aa325e79897`，`assets/index-hbS0HTaY.js` SHA `a4797c9bbd175330ec08cdb1c64ca8a25d889e31a5395e25576e824761386b2e`，CSS SHA `fe7a743bbdc7f990e941835d8d95f6c3cbf7dd59152556a2987a03b23f7a739e`。前端构建只证明该输出，不证明原生窗口。
- 正式树 tracked 候选 `git diff --check` exit 0；5 个新增源码/测试逐个 `git diff --no-index --check /dev/null <file>` 各 exit 1（文件不同），无空白诊断。相邻治理 PLAN 与索引为并行工作，不属于 Development 改动；spec 与父规格 SHA 保持本文件首部所列值。
- 以下路径均相对于 `automation-world/device-simulator/`；它们是联测前候选的**完整文件** SHA，不包括本任务 `tasks.md`、并行治理文件或 DAA 文件。原始隔离源码后来有针对性能和容量的正式树修订，不能再把旧临时源码当最终候选。跨端实际联测前若任一 SHA 改变须重新识别并评估验证范围。

```text
3e7c14677c66de7a462a572735bee6cb6b2409e7b4d2ae1961fe19098911d159  USER_GUIDE.md
05e3a03ff9f7b4fdbdc4d8252bf25ce86b624c3d287b7b6e0899facfb9bdb101  USER_GUIDE.zh-CN.md
3b7a255d3b29a68cbcac613520fb15a3267f99034de216b2844b3cc182a3291b  runtime/src/app.rs
50433a053a8ef6771d093dd344f9d2a0a2c54010e2992a8111995b9ecd462b36  runtime/src/domain/configuration.rs
9a77f3d1be117a5145cf6ce8a33ec55f3c6b50342685ccb8a12eb8914fb363a5  runtime/src/domain/plc_catalog.rs
453d69f925cf149918f8b940a1a099cf853990900d77f1f7eca44d0837b6d3c5  runtime/src/infrastructure/config_store/queries.rs
77d406cc2fc4966fed1d74bd2b8021103332b33e08cf3796cac6a14dd66f053b  runtime/src/services/catalog_export.rs
5c205c38aae7b0f410694d085d6ac9ba90d52588848a45a9d5353d31390c7ac5  runtime/src/services/catalog_import.rs
cf7755fd2ea3452b5a657c8e01066c6b1753aa4b147d2d3be47beb14f32de0f3  runtime/src/services/configuration.rs
d5103e903f2b056dbcf52a7d1285636a2a0cecd6fa1939a43533f5e05c1c9282  runtime/src/services/mod.rs
3ce30bbc576d10eb3fca9b294f383b4225a74dd148f51de5d2371c28fe57dd8e  runtime/src/services/naming.rs
a17ab2e1a7f943aeea3ad43019bd1f8100f7cacae19b71c2706115cac93d4e00  runtime/tests/plc_catalog_import.rs
18f594bba604c89f38dbd8801486461cce3b85d1b2f473e8f8638a2048164006  src-tauri/src/commands/catalog_import.rs
14a2b2408ae4073153b4aefd83e01f276898e5c19c6919569aab40c236ab246f  src-tauri/src/commands/mod.rs
3c795a31c182764a2a3847f27dc3e259a15d7c28021b9a610a1050ba43cbe14c  src-tauri/src/lib.rs
1bfe7639f75c732ca4c16a77c722f4481999f38acc1717fe665ab0dcb9dea301  src/services/deviceSimulator.ts
d25bcbaae9ac297cedca69cd54bbde7953e2d81336e1709feaf735986b527155  src/console/composables/useDeviceSimulator.ts
3dfcc34eec6d1a78703d19f07f68f257e3f9b0d0478ce82fec29933e491570a8  src/app/simulator/views/instances/index.vue
96f456e6a566af80f26974874fccd4fa62e54ff8c3eab8453841557a60d28df8  src/app/simulator/components/CatalogImportDialog.vue
c3f923ca80295d0207483015ab554ec0dda57dbc25f86357323df54c07abdbe8  src/app/simulator/components/PointEditor.vue
895253022becd86480bf753af6ae4d88aaccc638ec4c929b286947c3b0e932fb  src/app/simulator/locales/en-US.json
9a159c4cf76b9cd6e9d137b7c9d4843b79a58bf305914ae8cdc3ff40c123aec4  src/app/simulator/locales/zh-CN.json
55b721993def94297548bddee96ad25352b567967a92d6e91a3fcbbec9daeae6  tests/plc-catalog-import.test.mjs
318654a3db4dee8e24b43dae103b46bb92f289cf33553af2d038fc0387f896c9  tests/point-display-names.test.mjs
```

A06 仍待协调者按父 r6 和 DAA-019 联合安排：先核对两端活动进程、各自 `.local/dev`、原有对象和自动连接/采集/上报状态；只使用可识别合成 DAA PLC、经确认的空闲 loopback 端点与自有文件目录。DS 导入后明确填写监听地址/rack/slot，对每个 DB 完成现有手工布局预览并确认，对目录名称做预览确认，保存版本后在实例页选择该保存版本并重导真实文件。不得把来源客户端 IP 自动当监听地址或触发真实 PLC、连接、采集和外部上报；DAA 历史隔离及 `DEV-PLC-A` 的保护与清理由协调者和 DAA 侧按其规格核对。缺少安全条件即记录 blocker。此前服务级合成文件和内存测试不能替代 UI / 两应用实际文件闭环。

当前状态仍为 `implementation_in_progress`：尚无实际 A06、完整 Development handoff、fresh-context Verification 结论或 Human Owner 最终验收。旧二进制读取新增目录元数据未实测；Windows、真实设备、真实外部上报、生产部署及物理 DDL 不在此候选验证范围。任务根 `/private/tmp/ds005-dev-Cq4eK0` 含本次构建、前端、部分因失败保留的合成 profile 与测试资源；在 A06、Development 和独立 Verification 确认无依赖后，仅清理可归属本任务的目录，不触碰用户 profile 或 DAA 资源。

## 协调者正式入口隔离启动观察（2026-11-17）

以下为协调者转交的执行事实；本 Development 本次仅记录其报告，未亲自执行或独立复现。此前「尚未以普通入口启动」是当时的历史状态，由本节所述隔离入口观察接续；不改变 `implementation_in_progress` 或构成 developer_handoff。

协调者报告：用户已自行停止原应用，核对锁和 Vite 端口空闲后，在正式 DS 源码目录执行：

```bash
env DS_PROFILE_DIR=/private/tmp/ds005-dev-Cq4eK0/entry-profile CARGO_TARGET_DIR=/private/tmp/ds005-dev-Cq4eK0/formal-tauri-target CARGO_NET_OFFLINE=true pnpm tauri dev --no-watch
```

首次受限沙箱启动在绑定 `127.0.0.1` 时返回 `EPERM`，exit 1；随后使用 `require_escalated` 的沙箱外执行成功。协调者报告 Vite 在 `127.0.0.1:15194` ready，`cargo run` 的 `native-s7` 构建成功，PID `73817` 的 `profile_open` 日志指向本任务自有 `/private/tmp/ds005-dev-Cq4eK0/entry-profile`，UI IPC 响应正常。入口生成的 debug 二进制 SHA-256 为 `883121ba395a2631ab658062903af92e87b64c12bf8eb2b26e36e43af285d8af`，与上文普通 `cargo build` 的 `b32946b92cb98f3a95f0b3ddd4d3c2b49461a522b10d352c2449144d747528d7` 不同，不能将二者视为同一构建产物。

协调者报告，对该自有临时 profile 进程使用 Ctrl-C 停止后，相关锁和 Vite 端口已释放；本次未触碰 `.local/dev`。这一入口与 IPC 观察不等于导入导出 UI 或两应用实际文件闭环；真实 `.local/dev` 的 A06 仍待 DAA 候选冻结后由协调者安排，独立 Verification 和 Human Owner 最终验收均未发生。

## DS-005 r2 Development 接续（2026-11-18）

Human Owner 已明确批准 `aiis-ics-arch::ARCH-PLC-001 r7`、`device-simulator::DS-005 r2`、`aiis-ics-arch::DAA-019 r2` 及版本衔接。只读重新核算：DS-005 活动 r2 spec SHA-256 为 `f9ec8c6941f61b50b31d02a8526c8d53c907486190dd48ae0cc1c374d94851b7`，父 ARCH-PLC-001 活动 r7 spec SHA-256 为 `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`；两者均匹配协调者转交的批准后摘要。规格附录中 r1 / r6 的原字节 SHA 分别为 `fe007553288adbdd426b1ce7edf9ebd8a2d6d0bfa72a549deeb3fb8341975c75` / `0eb0c10e70507903347b216d2ac712add430fc4511b251a2ad93e00e19ce1408`，各与先前批准值一致。r2 仅改变 DS05-06 验收衔接；产品功能、其他验收、文件白名单与数据保护保持，原 r1 的实现、自检、失败、未知回执和协调者入口观察均按上文原貌保留。

**当前候选身份。** 工作树 HEAD 仍为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。以 Python `hashlib.sha256` 对上文「联测前候选」原有 24 项清单逐个读取正式 DS 工作树文件并比对，24/24 相符、0 不符；未从该清单推断其他并行工作树文件的状态。只读 `shasum -a 256 /private/tmp/ds005-dev-Cq4eK0/formal-tauri-target/debug/aiis-device-simulator` 输出 `883121ba395a2631ab658062903af92e87b64c12bf8eb2b26e36e43af285d8af`，与协调者上文记录的正式入口二进制相符；此前普通 cargo build 的 `b32946…` 仍是不同产物的历史事实。本次还只读核对原 formal-ui `index.html` 与 JS 分别仍为 `b6aba8ac…e79897`、`a4797c9b…386b2e`。本轮没有修改产品文件、运行测试或重新构建；r1 记录的自检仍是 Development 历史证据，不是 r2 独立 QA。

**r7 A06 / DS05-06 尚待的三个独立部分。**

- A：复核 DAA 任务自有合成 profile 中真实存储及服务执行的保存、激活、移除、再激活和历史身份隔离证据；只能按实际证据描述为服务级操作，不能冒称原生 GUI。该证据和 DAA 验证由其拥有者及 fresh-context Verification 处理，本 Development 尚未独立复核。
- B：由协调者在重新核对环境后，以既有已激活且安全移出的合成 PLC 历史，在两端 `.local/dev` 的正式原生界面完成 F1 导入 DS、DS 保存版本并导出 F2、DAA 当前同源拒绝及 L1 移除后 L2 实际新建；核对文件 SHA、外部身份与新本机映射。DAA 本轮不激活、不创建其 configuration revision、不采集或上报；DS 不启动模拟或连接设备。原有 8 个 DAA 版本及历史必须保护，DS 发布前也须确认不会裁剪既有历史。
- C：由协调者从 DAA `DEV-PLC-A` 的已保存普通 DB/UDT 来源只读导出真实文件，在 DS 新建本任务停机实例完成导入、确认、保存与重导，核对 DS05-02/03；DAA 同源预览须明确拒绝且不提交。该来源不能称为合成或 catalog，且不修改 `DEV-PLC-A`。

协调者负责实际 GUI、profile 安全核对及结果回传；本轮 Development 未启动应用、未读写用户 `.local/dev`、未操作共享临时根，未进行 A/B/C 实测或清理。测试前后须核对用户现存实例、活动/草稿、版本、历史与上报事实；条件不明即停止，不能以服务 fixture 或预览替代真实提交。旧二进制读取新增目录元数据仍无证据，先前 1 秒存储未知回执风险及其失败记录保持。r2 仍为 `implementation_in_progress`，实际结果回传并记录后才评估精确 `developer_handoff`；fresh-context Verification 和 Human Owner 最终验收均未发生。

## r7 A：合成 profile 的服务历史隔离复核（2026-11-18）

Development 在任务自有临时 profile 独立复跑 DAA 的增强测试，并只读核对 DAA 正式候选 34/34 文件 SHA 与其 `candidate-sha256-final2.txt`（清单 SHA-256 `2800fc8f912950e92307bce9944d0624d4d1725955935d70ac6d158a076a9511`）一致。增强测试相对于 DAA 正式树的两份测试文件仅增加身份、绑定、重开和历史隔离断言；只读 `rsync -nrc --itemize-changes` 排除这两份测试文件和构建输出后，DAA `src-tauri/`、共享 TIA core 及 fixture 未见差异。DAA 的对应正式测试文件 SHA 分别为 `3d568d20e138b2ffda5da74d32450f09ddfdab95eed32a2b153a4fa08e3dcdb2` / `72a1240e626d7874dfcb18f24505dcc3c71d1bf7bebe7d12fc393ece1a8d4f32`，临时增强版本为 `fdfd223ccb4be59a75689c1429fd1153bdc0b5cbc411c2471d121cfc5297b916` / `43b0ea9575837d4a07280eb91cdf1981ecc9c8e729bd40ac5840cebfc6460359`。

```bash
env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT DAA_PLC_READ_ALLOWED=false TMPDIR=/private/tmp/ds005-r7-a-review-VVJuij /private/tmp/daa019-r2-dev.c0EWK6bZ/target/debug/deps/aiis_data_acquisition_agent_lib-d57255d4d287a29b infrastructure::local_store::catalog_export_tests::daa019_active_version_and_reimport_preserve_old_samples_queue_and_receipt --exact --test-threads=1 --nocapture
env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT DAA_PLC_READ_ALLOWED=false TMPDIR=/private/tmp/ds005-r7-a-review-VVJuij /private/tmp/daa019-r2-dev.c0EWK6bZ/target/debug/deps/aiis_data_acquisition_agent_lib-d57255d4d287a29b infrastructure::local_store::catalog_import_tests::daa019_history_requires_choice_and_separates_local_identities --exact --test-threads=1 --nocapture
```

两命令均 exit 0，分别 1 passed、219 filtered；测试二进制 SHA-256 `f8d099162b3ec412c87468dc448b9335e97788fa892a064b8a36a6d35b897f3a`。日志及断言覆盖实际本地保存、激活、移除并再次激活、新本机身份、旧来源/版本、样本、队列及回执隔离；使用假 HTTP 响应，禁用 PLC 读取，均为服务级合成 profile，不是原生界面、真实 PLC 或真实 POST。测试后四个 SQLite 文件 `PRAGMA quick_check=ok`；任务自有 `/private/tmp/ds005-r7-a-review-VVJuij` 连同测试根暂留独立 Verification 核对。

## r7 B/C：协调者原生 GUI 操作与 Development 只读复核

实际界面操作均由协调者在中文环境完成；本 Development 只读核验实际文件、DS 本地 SQLite 和协调者记录，未自行重放 GUI。目录 `/private/tmp/ds005-daa019-roundtrip-vdmwh6dt` 保存基线、实际交换文件及 app bundle。DS bundle 可执行文件和正式 `pnpm tauri dev` 入口二进制 SHA-256 均为 `883121ba395a2631ab658062903af92e87b64c12bf8eb2b26e36e43af285d8af`；这与上文历史普通 `cargo build` 产物不同。

- B：协调者从曾真实激活的旧合成 PLC 历史导入 DAA 新本机 L1 `a123de20-3d26-4961-819f-0b00708e82cf`，实际导出 F1 `daa-synthetic-export/a123de20-3d26-4961-819f-0b00708e82cf.json`，SHA-256 `117f0614a63de4fd11e7dce14a50ed445be87137ce9a47e2cd295bd701973261`。DS GUI 将其导入停机实例 `38b0b960-99e0-4ebe-a5c0-dff340ad369f`，DB/点默认停用，明确监听 `127.0.0.1:31978` 并确认地址与命名。DS 保存 v6 `f4b55b18-4bfd-4cf1-b385-9dc73cb48b95`（payload SHA-256 `865a68b41631a412effc33f318b01882fa81f28c201e0c8e642664f2f9f8b237`），界面提示清理 0 份旧历史，实际导出 `ds-export/38b0b960-99e0-4ebe-a5c0-dff340ad369f.json` SHA `ed5a0ddecb223803c6201727718e723a8f9a96168122f098c3271d1f6bc33570`。DAA 当前同源拒绝；协调者移除 L1 后实际导入新本机 L2 `79294849-b7c7-4a58-bc47-5836fe4bc2a0`，并实际导出 `daa-return-export/79294849-b7c7-4a58-bc47-5836fe4bc2a0.json` SHA `840379d35815349025cbf6f450d47561fbc590969a7cefd2fdab2527b7d6e2cb`。
- C：协调者只读导出用户原 `DEV-PLC-A` 普通 DB/UDT 来源文件 `daa-dev-export/f6da5dac-7326-4a6c-bceb-55ad7e74b8cf.json`，SHA `e609252a4212d2c0f4587d89abc34fc8acbbf763a83c777a90eb5242dbd8336e`。DS GUI 新建停机实例 `c8c7d09c-11da-43ba-b0b5-1d3e143e9f13`，监听 `127.0.0.1:31979`，确认地址与命名、DB/点默认停用，与 B 一同保存 v6；重启前导出 `ds-export/c8c7d09c-11da-43ba-b0b5-1d3e143e9f13.json` SHA `bede8f759b4c06aab2f0cfd23bf70c03eada10c1efed2d3d3d3322e763973dd1`。

协调者正常退出 DS 后，以同一候选及 profile 重开，工作台显示 0 实例/运行中/连接；GUI 选择已保存 v6，勾选两实例，确认 loopback 及未加载状态后实际重新导出：`ds-reopen-export/38b0b960-99e0-4ebe-a5c0-dff340ad369f.json` SHA `5c9fa568c7d3d866cee55539d94a317cb53107b3ead548805794cfa073471a92`，`ds-reopen-export/c8c7d09c-11da-43ba-b0b5-1d3e143e9f13.json` SHA `04c194da54cf35902f1fe52d20c1aa68bdab869fdd226db039a60da8c8d62168`。Development 只读 Python 对比各重启前后文件，仅 `exported_at` 不同，其余 JSON 对象、保存版本及 payload SHA 一致。协调者将重开后的合成文件实际导入 DAA 新本机 L3 `ac12bbc8-ecba-4b99-afe7-efe9b580a89e`；普通来源重开文件在 DAA 对现存 `DEV-PLC-A` 同源预览时明确阻断、确认按钮禁用，取消未提交。协调者随后用 GUI 移除 L2/L3 和 DS 两个测试草稿实例并保存，两个应用正常退出；DAA 未激活、采集或上报，DS 未启动模拟或连接设备。

Development 对 F1、DS 导出、F3 和重开导出，以及普通来源 DAA/DS 两次导出，分别用 Python 只读解析和比较：origin、DB/点外部 ID、技术名、双语值、旧名称与独立 description 的存在性及值、数据类型、字节/位地址和 `source_path` 一致；合成来源为 1 DB/4 点，普通来源为 1 DB/3 点。启用事实、端点、producer 和导出时间按各端语义独立处理；DS 输出引用同一 v6，DB/点均停用，DAA DB 层不携带 `source_enabled`。实际合成 catalog GUI 文件有非空独立 description；实际普通 GUI 文件 3 个 description 均为显式空串，空值及字段保留，不宣称该 GUI 文件有非空描述。先前合成普通 DB/UDT **服务级**文件另覆盖非空 description；无语言旧名称及 256 字节覆盖亦为上文服务/Node 测试，本次实际 GUI 文件未提供该字段。协调者转达 PM 只读澄清：DS05-02 未要求普通来源 description 非空，父规格允许显式空串；此解释不修改 Revision，交 Verification 独立判断。

## 用户数据保护的只读核对

DS 数据库无进程打开、无 WAL/journal 时，用 SQLite `mode=ro&immutable=1`、`PRAGMA query_only=ON` 只读检查 `.local/dev/device-simulator-v1/config.sqlite`，`PRAGMA quick_check=ok`，文件 stat 在检查前后不变。与联测前 `/private/tmp/ds005-daa019-roundtrip-vdmwh6dt/baseline-hashes.json`（SHA `2550195d9bd33e04e8396478bd546f08da589920b4e49470e9508d1c427d778d`）比对，用户原 v5 `2448bb7b-7820-49f6-8764-d9124f4c50a5` payload SHA `4fa64ee107ea5410810c985119bb6c8d94e7af563c5a685e0217caae19a82ee7` 未变，原两个 sourceVersions 对象及对应归档内容/血缘仍一致；当前草稿实例列表仍空，v5/v6 均保留。v6 为最新且引用本任务两实例，按既有历史保护保留；当前草稿 sourceVersions 从 2 增至 4，草稿整体 SHA 从基线变化，故此处仅称原版本和空实例语义得到核对，不称整个草稿或 profile 未写入。

DAA 侧独立 Development 的最终只读复核记录见 `automation-world/data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/tasks.md`，SHA `7baafd2f8a5f6bd65cd59f7d7225e175172ef08938e630c273909d7d8922b952`：8 个原 revision、active/previous 与原草稿 payload 匹配基线；118 条 samples 的 ID/SHA、69 条 uploads 和 73 条 attempts 全行、原 binding/source 全行匹配，旧合成样本 11 条；L1/L2/L3 无 generation、samples、binding。8 context 当前对应旧版本，19 来源引用完整，但没有 context、samples 其他列和 sample_delivery 的前测行级摘要，不能称这些项目逐行前后哈希相同。本 Development 未读取 DAA 用户数据库，以上为该角色报告，不扩展其结论。

## Development → fresh-context Verification 交接

- 精确交付为 `device-simulator::DS-005 r2`，活动 spec、父 r7 的批准 SHA 见文件首部；正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`、HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 的未提交差异，产品候选为上文 24 项完整 SHA 清单，另有本 `tasks.md`。并行 DAA/治理差异不属于本 Development 交付；未修改 spec 或 checklist。
- 正式树 DEV self-check 为 Rust 34 passed/2 ignored、Node 40 passed/1 skipped，Vue 类型检查、Vite 构建、两份 Rust fmt、native-s7 Cargo 构建成功；隔离 1 MiB 超额单实例拒绝/不覆盖/其他实例继续导出测试 1 passed。命令、失败、重跑、正式普通入口及 24 项 SHA 在上文；r7 A 为合成服务增强测试，B/C 为协调者真实文件原生界面，三者不可互相冒充。
- 英文 i18n 键对称及 Node/静态检查和双语手册有证据，**英文原生 GUI 未实测**；中文原生操作是本轮事实。旧二进制读取新增配置元数据未验证；既有 1 秒存储回执在系统负载下可能为 unknown，必须先读回，不得盲目重试。Windows、真实 PLC、真实上报、部署及发布未验证。DEV 不授予 QA verdict 或 Human Owner 最终验收。
- `/private/tmp/ds005-dev-Cq4eK0`、`/private/tmp/ds005-r7-a-review-VVJuij` 和 `/private/tmp/ds005-daa019-roundtrip-vdmwh6dt` 的候选、合成 profile、失败证据、真实交换文件及 bundle 按各自归属暂留 fresh Verification；待证据不再需要、确认无进程占用且协调后才清理自有临时资源，不删除用户 profile、v5/v6 或正常来源归档。

记录过程首次 Python heredoc 因源文本编码在解析时 exit 1，未执行写入；只读 SHA 仍为接续前 `72a7f28a98660c26c0435790e97c1c97c44dc56579923d42ef41a75bb279a7c8` 后使用 UTF-8 heredoc 接续。此故障未影响产品代码或测试结果。

B 的旧外部 origin 从实际 F1 只读解析为 `kind=device_simulator`、`profile_id=227189b1-d035-4a78-a054-ac56921a585a`、`plc_id=e1dc3ad5-305f-4367-af1b-92333a582730`；源历史合成文件 SHA-256 `5198f7fef382f9524b81c66275b76cbdb779deb7741df16d3005f809bf6662e3`。L1、L2、L3 是上文分别记录的新本机 ID，均不作为旧外部 ID；F1/F2/F3 的外部 origin 及 DB/点外部身份经独立只读比对一致。

## QA1 返修与新的 Development 交接（2026-11-18）

独立 QA1 以 `qa_failed` 退回 F-QA1-001：DS 新增导入源码/测试改变了文件结构，但 `CODE_INDEX.md` 未登记。原 QA1 [checklist](checklist.md) SHA-256 `a44050702c5b7055461a63842f4e0c93d97c3490a7f305fcca41543f20b3e0eb`；原交接 tasks SHA-256 `2fc693eb4523ffce72cad3514dd54e6fc13c7e5c736dc44a52efe92df7b29763`。QA1 失败、证据及其权限保持在 checklist 中，不由 Development 修改或改写为通过。

本次仅在批准范围内向 `CODE_INDEX.md` 添加 5 条链接和职责：运行时 `catalog_import.rs`、Tauri 同名桥、`CatalogImportDialog.vue`、`plc_catalog_import.rs` 集成测试及 `plc-catalog-import.test.mjs`。原索引 SHA `9c62c5754bef8721993512679ed52abb1329266b22cc9318cd0266abf402714a`，新 SHA `ae0fa67fede5e4404a31e2948a8fe133c7a20a365a02f4b19259dcd14ec83963`；五个文件均已有中文头部，未改产品源码。本轮未修改 spec、checklist、用户数据或任何 profile。

Development 以 Python `re` 提取索引的 Markdown 文件链接并用 `Path.is_file()` 检查：32 条目标全部存在、0 缺失，5 个新增目标各出现一次；仅检查文件存在，不验证锚点。用 `hashlib.sha256` 逐项检查上次 24 项候选，24/24 未变，追加新索引组成以下 25 项完整候选；`git diff --check -- CODE_INDEX.md` exit 0，实际 diff 仅增加 5 行索引。活动 spec、父 spec、QA1 checklist SHA 不变，正式入口及实际联测 bundle 的二进制 SHA 均仍为 `883121ba395a2631ab658062903af92e87b64c12bf8eb2b26e36e43af285d8af`。本次为文档索引返修，不重复运行先前源码未变时已完成的编译与测试；先前 DEV 检查及 QA1 独立检查各自的命令、退出码、失败和限制分别见上文与 QA1 checklist。

协调者补充的英文原生观察发生在 QA1 期间：使用同一候选及 `.local/dev`，顶栏切为英文，Instances 页显示 `Import PLC JSON` 和 `Export PLC JSON`；导入对话框的英文提示及 Choose/Cancel 可见并取消。导出选择已保存 v6 与合成实例、确认目标及未加载状态后选择 `Preview all points`，看到英文表头及四点中英文名称/description，取消时未选择目录或写文件，随后切回中文并正常退出。此为协调者实际观察，本 Development 未重放；未在英文模式选择导入源文件、提交导入或执行导出落盘。上文交接时“英文原生 GUI 未实测”保留为当时事实，由本补充接续，不能扩大本次观察范围。

QA1 还记录协调者在此前 DAA 联测期间误点过 L1“测试连接”，返回“PLC 操作队列繁忙或对象不存在”；L1 未激活、读取开关关闭，未建立连接。该事实与未经尝试连接不同，保留供后续 Verification 独立评估。

以下候选清单每行是完整 SHA-256、两个 ASCII 空格和相对 DS 根目录的路径，含行末 LF；按列出顺序拼接全部 25 行的 UTF-8 字节，清单 SHA-256 为 `db1cfbd5fd74bee20863796766924b3571421bd4759543cd8d931bfa70aa61d8`。`tasks.md` 和 QA1 `checklist.md` 是各自角色事实文件，SHA 另行核对，不计入此产品及索引候选清单。

```text
3e7c14677c66de7a462a572735bee6cb6b2409e7b4d2ae1961fe19098911d159  USER_GUIDE.md
05e3a03ff9f7b4fdbdc4d8252bf25ce86b624c3d287b7b6e0899facfb9bdb101  USER_GUIDE.zh-CN.md
3b7a255d3b29a68cbcac613520fb15a3267f99034de216b2844b3cc182a3291b  runtime/src/app.rs
50433a053a8ef6771d093dd344f9d2a0a2c54010e2992a8111995b9ecd462b36  runtime/src/domain/configuration.rs
9a77f3d1be117a5145cf6ce8a33ec55f3c6b50342685ccb8a12eb8914fb363a5  runtime/src/domain/plc_catalog.rs
453d69f925cf149918f8b940a1a099cf853990900d77f1f7eca44d0837b6d3c5  runtime/src/infrastructure/config_store/queries.rs
77d406cc2fc4966fed1d74bd2b8021103332b33e08cf3796cac6a14dd66f053b  runtime/src/services/catalog_export.rs
5c205c38aae7b0f410694d085d6ac9ba90d52588848a45a9d5353d31390c7ac5  runtime/src/services/catalog_import.rs
cf7755fd2ea3452b5a657c8e01066c6b1753aa4b147d2d3be47beb14f32de0f3  runtime/src/services/configuration.rs
d5103e903f2b056dbcf52a7d1285636a2a0cecd6fa1939a43533f5e05c1c9282  runtime/src/services/mod.rs
3ce30bbc576d10eb3fca9b294f383b4225a74dd148f51de5d2371c28fe57dd8e  runtime/src/services/naming.rs
a17ab2e1a7f943aeea3ad43019bd1f8100f7cacae19b71c2706115cac93d4e00  runtime/tests/plc_catalog_import.rs
18f594bba604c89f38dbd8801486461cce3b85d1b2f473e8f8638a2048164006  src-tauri/src/commands/catalog_import.rs
14a2b2408ae4073153b4aefd83e01f276898e5c19c6919569aab40c236ab246f  src-tauri/src/commands/mod.rs
3c795a31c182764a2a3847f27dc3e259a15d7c28021b9a610a1050ba43cbe14c  src-tauri/src/lib.rs
1bfe7639f75c732ca4c16a77c722f4481999f38acc1717fe665ab0dcb9dea301  src/services/deviceSimulator.ts
d25bcbaae9ac297cedca69cd54bbde7953e2d81336e1709feaf735986b527155  src/console/composables/useDeviceSimulator.ts
3dfcc34eec6d1a78703d19f07f68f257e3f9b0d0478ce82fec29933e491570a8  src/app/simulator/views/instances/index.vue
96f456e6a566af80f26974874fccd4fa62e54ff8c3eab8453841557a60d28df8  src/app/simulator/components/CatalogImportDialog.vue
c3f923ca80295d0207483015ab554ec0dda57dbc25f86357323df54c07abdbe8  src/app/simulator/components/PointEditor.vue
895253022becd86480bf753af6ae4d88aaccc638ec4c929b286947c3b0e932fb  src/app/simulator/locales/en-US.json
9a159c4cf76b9cd6e9d137b7c9d4843b79a58bf305914ae8cdc3ff40c123aec4  src/app/simulator/locales/zh-CN.json
55b721993def94297548bddee96ad25352b567967a92d6e91a3fcbbec9daeae6  tests/plc-catalog-import.test.mjs
318654a3db4dee8e24b43dae103b46bb92f289cf33553af2d038fc0387f896c9  tests/point-display-names.test.mjs
ae0fa67fede5e4404a31e2948a8fe133c7a20a365a02f4b19259dcd14ec83963  CODE_INDEX.md
```

重新交接 `device-simulator::DS-005 r2` 至 fresh-context Verification：交付为正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`、HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 的上述 25 项候选和本 Development 事实记录。并行 DAA/治理差异不计入；受保护历史及原临时证据按上文保留。旧二进制兼容性、1 秒未知回执、英文未提交/落盘、真实设备/上报及其他已列限制不因索引返修改变。本次 self-check 不是 QA2 verdict，Human Owner 最终验收未发生。

## Human Owner 要求明确操作步骤：手册补充及 Development 交接（2026-11-18）

Human Owner 在进行本机手动联测时要求说明如何创建实例、创建或导入点位，以及后续保存和交换；协调者转达本轮 DAA 导出 → DS 导入、保存 v7 并导出四点文件的结果。本 Development 未操作该界面或 `.local/dev`，不将转达冒充本角色自行重放。此前 QA1 失败、QA2 `qa_blocked`、历史缺口和尚待的同一 L2 证据均在 `checklist.md` 原样保留；此处不改变 verdict 或宣称联测已全部闭环。

在批准的 DS-005 r2 手册白名单内，补充 `USER_GUIDE.zh-CN.md` 和 `USER_GUIDE.md`：开头按手工建点、DB/UDT 文件、PLC JSON 三条路径给出页面、按钮、确认和可见结果；分别说明保存草稿、地址/名称确认、保存版本、导出以及需要运行时的初值/策略、加载和启动。新增与实际界面文案对应的目标及版本差异确认、导出错误处理，明确行选择不等于启用、仅交换不要求先确认初值/策略、JSON 来自所选保存版本。仅完善现有功能操作说明；本次未改源码、spec、checklist、配置或用户数据，未启动设备或应用。

DEV 自检：

- 只读对照 `CatalogImportDialog.vue`、`CatalogExportDialog.vue`、`views/points/index.vue`、`services/naming.rs`、`domain/plc_catalog.rs` 和中英文 locale：确认导入前未保存草稿会阻止预览、导入新建草稿、导出读取已保存版本、目标确认和加载版本差异分别有勾选，以及 `catalog_connection` 的实际校验条件；没有把其原因归结为初值/策略。
- 在仓库根执行 Python 标准库 `re` / `pathlib` 对两份手册的 Markdown 相对链接及锚点逐项检查：54 项，缺失 0，exit 0；`git diff --check -- automation-world/device-simulator/USER_GUIDE.zh-CN.md automation-world/device-simulator/USER_GUIDE.md` exit 0。手册说明核对基于源码，未在英文界面重新实操；纯文档追加未重复运行原源码测试或编译。
- 两份手册当前完整 SHA-256：`USER_GUIDE.md` 为 `1d3f2031cef8472dee778a60eea17ec4bd15b9ce50186f426286c6458f2ce366`；`USER_GUIDE.zh-CN.md` 为 `97fb417dc2149ef790b6cc88c0ab10d703559d981749eadd8124d1f0b00da597`。用 Python `hashlib.sha256` 重算上文 QA1 返修交接的 25 项清单：只有这两份手册变化，其他 23 项不变；依原 25 行顺序、两 ASCII 空格及 LF 格式替换上述两个摘要得到当前候选清单 SHA-256 `d5b9db0f0c9fced72d30a59c08f4a23d881defed113c4c4ce1458e1fbbe9c4ce`。活动 DS spec SHA-256 仍为 `f9ec8c6941f61b50b31d02a8526c8d53c907486190dd48ae0cc1c374d94851b7`，父 r7 仍为 `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`。

**Developer handoff：** 精确 Revision `device-simulator::DS-005 r2`，正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`、base HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`；本轮变更两份手册及本 `tasks.md`，交 fresh-context Verification 核对手册、候选变化及尚待联测证据。既有临时资源与旧二进制、未知回执、英文文件提交、真实设备/上报等限制照旧；此文档自检不构成独立 QA 或 Human Owner 最终验收。

### 手册复核反馈返修及重新交接（2026-11-18）

协调者转达独立 Verification 对上述手册交接的三项问题后，Development 在同一批准文件白名单内返修：英文导入卡片名改为界面实际的 `DB / UDT source import`；手工和 DB/UDT 路线明确在每个 DB 逐页选择所需点位、分别预览并确认名称，切换 DB 会清除勾选；JSON 导入后补全需要运行时分别启用 DB 和逐点启用、完成编辑、保存草稿、确认初值/策略、保存和加载的步骤，注明只导出不要求启用。保留其他原文及上文历史摘要；不修改产品源码、spec、checklist 或用户数据。

DEV 自检：只读核对 `SourceImportPanel.vue`、`views/points/index.vue`、`PointEditor.vue` 的卡片、DB/点开关和切换 DB 时清除选择的实现；以 Python 对中英文 locale 中 8 个关键标签逐项检查手册，双方各 8/8 均出现。标准库 `re` / `pathlib` 重查两份手册 54 个相对链接及锚点，缺失 0，exit 0；`git diff --check -- automation-world/device-simulator/USER_GUIDE.zh-CN.md automation-world/device-simulator/USER_GUIDE.md automation-world/device-simulator/plans/DS-005-plc-json-bidirectional/tasks.md` exit 0，但 Git 不会检查未跟踪的本 `tasks.md`；对该文件另执行 `git diff --no-index --check /dev/null automation-world/device-simulator/plans/DS-005-plc-json-bidirectional/tasks.md`，exit 1 表示文件不同且无空白诊断。本轮只改文档，未重跑源码测试，未操作原生界面或 `.local/dev`。

本轮两份手册的完整 SHA-256 分别为 `USER_GUIDE.md` `2cf2558aafda555fa14a656823414439a7e794da0c92874f66220f101f8882ef`、`USER_GUIDE.zh-CN.md` `cd1c9a747cc988514fd970e88361d4588e27c9a1ba19139fc23ac644b2c102e8`。相对上文 QA1 返修交接的 25 项原清单仍只有此两份手册发生变化，其他 23 项不变；按原顺序替换这两个摘要、每行两个 ASCII 空格及 LF 后，完整清单 SHA-256 为 `8cdf839a33460e5eb175f2f96d3f7202db4dbbd8e2ffc529903f4008cdb4744d`。上节摘要为返修前事实，不覆盖。

**新的 Developer handoff：** `device-simulator::DS-005 r2`，正式工作树及 base HEAD 如上；本轮修改两份用户手册与本 `tasks.md`，交新的 fresh-context Verification。既有 QA verdict、历史证据缺口及原有风险保持，Development 不授予 QA verdict 或 Human Owner 最终验收。

### F-GUIDE-001 剩余返工与 Owner 手工往返证据（2026-11-18）

接收 `checklist.md` 中 DS-005 r2 手册返工独立复验的正式 `qa_failed` 交接（写前 checklist SHA-256 `05ba79e85b4bdcf1b3785703eed04de8ed9cd524487f218430c7a8a3e893edab`），保留原失败及 QA2 `qa_blocked`。本次只修改两份用户手册：DB/UDT 通用路线明确完整 JSON 导出要求所有导入点具有合法技术名，包含停用点；详细示例明确 Alpha、Beta 本例各一页，多页时须累计选择各页、预览并确认，再逐 DB 重复，切换 DB 清除选择。静态对照 `domain/plc_catalog.rs` 对所有点验证技术名，未虚构逐点确认状态。未修改产品源码、spec、checklist、用户 profile 或任何测试数据。

本 Development 用 Python 标准库只读解析协调者提供的 `/private/tmp/plc-json-owner-manual-82_5g47q/daa-export/` 三个实际文件并计算 SHA：DAA F1 `4670e3bd-8d51-4734-84d8-303b3d2afca2.json` 为 `63260610d54cb339d2807366abf078a0682ceab034f6adb06a8385237e2cdd68`；DS F2 `66155773-770a-42ea-9ad9-cf72be59766d.json` 为 `c62949dcfef4c054c7f0147a35e10af9095523e67e416f1ae2445b29f7dc8ec0`，producer 为 DS、保存版本为 v7 的 `63124411-7ad9-4e7e-aad1-39d5965b2bca`；DAA F3 `7d2ca225-da04-4548-b755-22a174c0fd22.json` 为 `e14176aca6f28fb3e188d2904a29c22de89dad4e16fc7f0df132fb1a30f38ca2`。三个文件各 1 DB、4 点；比较 origin、PLC 名称、DB/点 ID、名称、类型、地址、双语和描述一致，另比较旧显示名及来源路径的 `get` 值一致。DB `source_enabled` 按各 producer 合同分别处理，不要求相同。Python 只读比较 exit 0；这不证明本角色重放了 GUI 或原生 IPC。

协调者转达 Human Owner 已通过 DS 界面移除本轮测试实例并保存草稿，未删除历史；协调者依据前测 `full-baseline.json`（SHA-256 `dfc8bee1006da84f98a3efe6298a892df435ea146b6f56a34a08d228fe438269`）作只读逐行比较：DS 既有 revision、source_blob、source_version 全部保留，三者各新增 1 条；草稿实例为空，但保留来源使草稿 SHA 与前测不同，不能称字节一致。DAA 旧配置、历史、样本、队列和回执行未减少或变化，草稿 SHA 恢复原值。本 Development 未自行读取或核对这些 profile，以上为协调者报告；新一轮未截获 DAA IPC 返回，旧一轮缺失前测仍不可倒证。是否满足验收由 fresh-context Verification 判断，不能将这些结果写成 QA 通过。临时文件 `/private/tmp/plc-json-owner-manual-82_5g47q` 仍供核验，暂不删除。

DEV 自检：Python `re` / `pathlib` / `urllib.parse` 检查双语手册 54 个相对链接和显式 ID/标题锚点，缺失 0、exit 0；`git diff --check -- automation-world/device-simulator/USER_GUIDE.zh-CN.md automation-world/device-simulator/USER_GUIDE.md` exit 0。只读 `hashlib.sha256` 比对上文 25 项候选：除两份手册外其余 23 项不变。当前 `USER_GUIDE.md` SHA-256 `8128905e67a7759a8681aa4d6889d0487254bc0378af2da36447ff59bd155905`，`USER_GUIDE.zh-CN.md` SHA-256 `bea2285931d3b81684e31b71196f55b555f12ceed74de6a5467d8bfae0bce067`；按原顺序替换两项、每行两个 ASCII 空格及 LF，当前完整候选清单 SHA-256 `8782cbe4b7f12964eae858172781cece06ff728c89674a164931481e301e41d6`。本次只改说明和 Development 记录，未重跑未变源码的测试与构建，未启动应用、访问用户 profile 或重放 GUI。

**Developer handoff：** `device-simulator::DS-005 r2`，正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，base HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`；本轮修改双语手册与本 `tasks.md`，交新的 fresh-context Verification 复核剩余手册问题及实际证据。既有 QA 结果、待核验历史保护、IPC 缺口和其他限制均保留；Human Owner 最终验收未发生。

### F-GUIDE-003 返工与 Development 交接（2026-11-18）

接收独立 Verification 的 F-GUIDE-003 正式返工交接（写前 `checklist.md` SHA-256 `a32cee5e2fb1734632ac6eca9efd52a61435b44b175e3c84f7eef4a40d3a7728`）。仅将双语手册 DB/UDT 通用路线的命名操作改为**预览 → 核对候选名称 → 确认**，不改变其他内容；历史 QA 结果和证据保留，未修改 spec、checklist、代码或用户 profile。

DEV 自检：Python 标准库按双语路线中的按钮和核对文字位置验证预览、核对、确认顺序，中文和英文均为 True，exit 0；`git diff --check -- automation-world/device-simulator/USER_GUIDE.md automation-world/device-simulator/USER_GUIDE.zh-CN.md` exit 0。Python `hashlib.sha256` 重算上文 25 项候选，只有两份手册与原 QA1 清单不同，其余 23 项不变：`USER_GUIDE.md` SHA-256 `29350674a651606cf16542f59f3b68efa0bd62f1e5d5af0a3acfed1ba7b6aecb`，`USER_GUIDE.zh-CN.md` SHA-256 `d71005a6ab2533461a6a7044909cfed060e0dd77b5e2b816f387778fa3a3c559`；原顺序、每行两空格和 LF 的当前清单 SHA-256 为 `e0c3df10cc048a570d07a67168b58d82361b45c5d4bdaabaeaa203dde1d89284`。本轮仅文本顺序修正，未运行项目、源码测试或 GUI，未访问 `.local`。

**Developer handoff：** `device-simulator::DS-005 r2`，正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，base HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`；两份手册和本 `tasks.md` 交新的 fresh-context Verification。DS05-06 证据阻塞及其余限制按已有 checklist 保留，本交接不构成 QA 或 Human Owner 最终验收。

## DS-005 r2 操作手册速查及资源收尾更新（2026-11-18）

按 Human Owner 本轮要求，在原批准白名单内改写 `USER_GUIDE.md` 与 `USER_GUIDE.zh-CN.md` 的快速流程。先按现有材料选手工、DB / UDT 或 PLC JSON 路线，再逐 DB 确认地址、预览并核对名称后确认。单列保存版本及导出或运行的后续动作。更新第 7、8 节的快速流程衔接。仅修改双语手册和本 Development 记录。

- DEV 只读核对实例、点位和策略页面、`InstanceEditor.vue`、`PointEditor.vue`、`SourceImportPanel.vue`、`PointNamePreviewDialog.vue`、JSON 导入导出对话框和中英文 locale，并对照 `runtime/src/services/{layout,naming,configuration}.rs`、`runtime/src/domain/{layout,plc_catalog}.rs`。布局确认会清除实例命名确认，应先做完各 DB 地址。点表逐页累选，换 DB 清除。运行加载校验覆盖已启用 DB 内的所有点，导出校验覆盖各 DB 的完整点集、地址和名称。
- Python 3 标准库 `json`、`re`、`pathlib`、`urllib.parse` 检查每份快速流程 30 个 locale 标签、布局和名称预览及核对顺序、初值/策略确认与保存版本顺序，并核对两份完整手册 46 个相对链接及锚点，缺失 0，exit 0。此前两次脚本 exit 1 分别是检索章节时误把三级标题当正文边界，以及英文人工地址理由未引用界面全名，已分别修正。DS 目录执行 `git diff --check -- USER_GUIDE.md USER_GUIDE.zh-CN.md` exit 0，`git diff --no-index --check /dev/null plans/DS-005-plc-json-bidirectional/tasks.md` exit 1 表示文件不同，无空白诊断。仅静态核对，未重复构建、测试产品代码或重放桌面操作。
- base HEAD 仍为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。双语手册 SHA-256 见下。Python `hashlib.sha256` 按上文 QA1 后 25 路径清单的顺序、每行两空格及 LF 复算当前工作树，完整清单摘要 `84e5160ec4a59385dc581547cb517710426bacb9e226cd5e249918a98df1c712`。除两份本轮手册之外，较 DS-005 旧清单的五处差异与已验收 [ARCH-PLC-002 r1 Development 清单](../../../plans/ARCH-PLC-002-plc-json-export-feedback/tasks.md) 逐项一致：导出服务、导入测试、前端服务及两份 locale。其余 18 项不变。本轮工作树不是历史独立验证的原始字节候选。

| 文件 | SHA-256 |
| --- | --- |
| `USER_GUIDE.md` | `84b2b972e0f02b4484d9aface9919c0a48a6d9821bcfbba2b1ca8de96a613254` |
| `USER_GUIDE.zh-CN.md` | `cacc118b2b66af77c7b9eb028b1fad42af7ad91d0e4c90cfe594f09f324c5ee0` |

资源状态由协调者报告。Human Owner 本轮明确要求清理旧验证工件。协调者核对归属和进程占用后，清理了本任务先前留存的 `/private/tmp/` 下 `ds005-daa019-roundtrip-vdmwh6dt`、`ds005-dev-Cq4eK0`、`ds005-qa-r2-SMgAxo`、`ds005-r7-a-review-VVJuij`、`plc-json-owner-manual-82_5g47q`、`arch-plc-002-predecessor-fpjq3d7g` 等自有测试目录。原路径中的交换文件、快照和测试副本不再可用。仓库内的历史结论、摘要及 DS05-06 未闭合事实按原记录保留。两端 `.local/dev` 未纳入清理。本 Development 未执行删除或访问用户 profile。

**Developer handoff：** `device-simulator::DS-005 r2`，正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，base HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。将上述两份手册和本记录交 fresh-context Verification 定向核对。本次范围为双语手册，DS05-06 历史阻塞及 Human Owner 最终验收状态沿用既有记录。

### F-GUIDE-004 返工与 Development 交接（2026-11-18）

接续独立 Verification 的定向返工，写前 checklist SHA-256 为 `095e160c0541583f5e7cc48855e6d2f6a8a66d7c774053d5b753a80d8ee03239`。双语手册仅改第 7 节步骤 2、4。仅导出可在确认地址、点名并保存草稿后直接保存版本。需要运行时，先确认每个启用 DB 内所有点、含停用点的初值和策略，再保存和停机加载新版本。已经保存导出版本时，补确认后另存版本并加载新版本。默认文件名以所选保存版本的实例名为准，已有 `.json` 后缀时忽略大小写识别并原样保留，否则补后缀。

DEV 只读对照速查、`runtime/src/domain/layout.rs`、`runtime/src/services/configuration.rs`、`CatalogExportDialog.vue` 和两份 locale。Python 3 标准库核对两种语言第 7 节的草稿/版本、运行确认/保存/加载时序、已有版本的补确认路径、后缀规则和 46 个相对链接及锚点，exit 0。首次脚本把 locale 的 `versions.publish` 当作顶层键，修正后重跑通过。DS 目录执行 `git diff --check -- USER_GUIDE.md USER_GUIDE.zh-CN.md` exit 0，未重跑构建或界面操作。

| 文件 | SHA-256 |
| --- | --- |
| `USER_GUIDE.md` | `f38595f553156cd71bea6ea82121a965fb696e4eeca13f2f5d11e3cf121f9a37` |
| `USER_GUIDE.zh-CN.md` | `ed68926ea62b8ce13c1d8c4ba82c2c02c0cf8641c0745eb2ca7102a04077e3bd` |

按上轮 25 个候选路径的相同顺序及格式计算，完整清单 SHA-256 为 `44d34cb2e9c956a3afc9c3a61fb0bc781273e78c86b128a225656e3c6ea2534f`，替换回写前两份手册的摘要后重得上轮清单摘要，故其余 23 项字节保持一致。

**Developer handoff：** `device-simulator::DS-005 r2`，正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，base HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。两份手册及本记录交 fresh-context Verification 定向复核第 7 节。DS05-06 的历史阻塞和 Human Owner 最终验收状态沿用既有记录。

## DS-005 r3 既有证据收尾与 Development 交接（2026-11-18，Asia/Shanghai）

Human Owner 在审阅五份精确收尾草案后回复「批准这组收尾草案」。本轮按 [DS-005 r3 §4–5](spec.md) 及 [ARCH-PLC-001 r8](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 执行 STD 文档交接。批准后的两份 spec SHA-256 分别为 `100f54502135b541ec9138748e03b1c1e34ff6a3a49f7fe127cbbca595aaa274` 和 `38085d5f0dd5d9db444008b9e04963371ddff3995cbb050641281ce6517931e5`。本节是 r3 的 Development 交接。上文 56,117 字节（含 r2 文件头和全部历史）SHA-256 为 `edc160f6a8b4e119333a5f47563c985b27b52bd2dc8dee344ddd217336462244`，沿用原字节。交接时 DS [历史 checklist](checklist.md) SHA-256 为 `93578dbd90f0e62bbafb79cbe3550eeeedb410107824eb95edf21cb3349365d3`。

### DS05-01–07 的证据及归属

- **DS05-01、07 · 原候选的独立 QA 与语言观察。** [DS checklist](checklist.md) 的 QA1 保留 `qa_failed` 和 F-QA1-001（索引缺项），另记录当时正式源码 Rust 35 passed / 2 ignored、Node 40 passed / 1 skipped、Vue 类型、Vite 构建和两份格式检查。首次 QA Rust 缓存失败、Vite PURE 注释和大 chunk 警告仍以原记录为准。QA2 对索引返工和 DS05-01–05 给出有界结论，延用同一 24 项产品清单的原测试结果，整体仍因 DS05-06 `qa_blocked`。协调者报告在两应用 `.local/dev` 的历史联合操作中完成中文原生操作，DS 英文仅观察到切换、导入/导出入口和弹窗、导出预览并取消。英文选择导入文件、提交及导出落盘均未实测。原生操作、自动化检查与 QA 的实物核对分别由原记录人员承担。
- **DS05-02、03 · 普通 DB/UDT 与新一轮实物。** 原 QA1/QA2 对既有普通 DB/UDT 构成的 DAA 实际文件、DS v6 首次导出及重开后重导核对外部身份与点位字段。该普通文件为 1 DB、BOOL/INT/REAL 三点，独立 `description` 字段均为空串。中文原生操作及单独填写模拟监听按协调者原记录归属。新一轮 Owner 手工 F1→F2→F3 是另一组 1 DB、4 点文件，见上文 F-GUIDE-001 返工条目、[DS checklist 的 Owner 文件段](checklist.md)及 [DAA-019 QA3](../../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/checklist.md)。当时 Development 和独立 QA 核过 SHA、origin、外部 DB/点 ID、技术名、类型、地址、双语、独立说明、旧名及来源路径。DS F2 取保存版本 v7。启用字段按各 producer 的配置事实比较，DAA 的 DB 层缺省与 DS 的停用按各自语义保留。
- **DS05-04、05 · 有界服务测试与 DS 历史。** QA1/QA2 的合成正负例涵盖双 producer、源启用缺省、TSAP、冲突与取消、非法停用点布局、原文字节和映射完整性、并发/ETag、回执和 256 字节旧名。原 DS 只读核对支持新 DB/点停用、既有 v5 和列出的原来源保留，草稿来源有新增。QA1 的 DAA 合成隔离使用自有 profile 和假 HTTP 回执，证据限持久化服务层。协调者原轮曾误点 L1 测试连接并报告未建立连接；该尝试保留在 QA1 历史中。
- **DS05-06 · Owner 手动往返与本轮历史核对。** 据 [DAA-019 Development 记录](../../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/tasks.md)，Owner 在两端 `.local/dev` 用实际文件完成中文 DAA→DS→DAA 操作，当前同源被拒；移除旧草稿实例后从历史来源新建 L2。Owner 报告同一次导入无手选即显示新 PLC 和 4 点，并对该 L2 再导出。协调者另报本机新 ID 与外部 origin 不同，四点停用、未分组。同次原生 IPC `importedLocalPlcId` 返回未直接截获。QA 核对的是文件及可用的存储证据。DAA-019 QA3 对该轮前测列出的 37 表作过独立只读逐行比较，前测行无缺失，并记录 DAA `source_documents` +1、`runtime_events` +9，DS `configuration_revisions`、`source_blobs`、`source_versions` 各 +1。协调者另报 Owner 移除测试实例并保存后，DS 草稿实例为空，保留来源使草稿 SHA 改变，DAA 草稿 SHA 与该轮前测相同。各库读事务和草稿读取各有观察时点。更早一轮缺失 `context`、`samples` 其他列及 `sample_delivery` 的逐行前值，仍无法核证。另一任务的原生隔离事件影响仍未知，见 [DS-004 历史 checklist](../DS-004-bilingual-point-display-names/checklist.md)。
- **DS05-06 · 协调者观察到的实际 v2 上报。** 2026-11-18 经用户允许，协调者对已发生的 13 条本机 v2 上报 `seq` 91–103 核对本地请求及持久回执、服务端注册和 MySQL `history` / `latest`。其报告 13 条均有匹配的 `status=committed`、`outcome=created` 或 `duplicate` 回执，本地正文字节 SHA 与回执吻合，对应 MySQL history 的身份、正文 SHA 以及 3 点字段和值一致。实际配置至少一处点位的两种显示名均非空，13 份正文不含显示名字段及该点两种对应显示文本，所核后端点集无显示类字段。Latest 为 3 点 `good`、seq 103；协调者也报告对应时段 DS 日志未见 WARN/ERROR。复查定位见 [r3 spec §2.4](spec.md) 指向的本地会话，第 28239–28242 及 28257–28260 行附近。本 Development 只读核对既有会话条目和脱敏计数，事实归协调者，覆盖限实际抽查的本机配置、时点及字段。该观测属于 DAA/后端链路的跨端辅助证据，旧轮前值、同次 IPC、其他配置、长稳及现场运行仍未获证明。

### DS05-07、08 的正式工作树与候选衔接

正式交付树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的 `main`，基准 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。候选由未提交工作树文件组成，HEAD 只标识基线。树中另有 DS-004、DAA 和治理并行差异。本次以 DS 原 25 项清单的路径顺序及 ARCH-PLC-002 DS 表的额外路径作字节核对。

- 历史 DS QA2 在 QA1 产品候选 24 项加索引后核对 25 项，清单 SHA-256 `db1cfbd5fd74bee20863796766924b3571421bd4759543cd8d931bfa70aa61d8`。F-GUIDE-003 后的 25 项清单为 `e0c3df10cc048a570d07a67168b58d82361b45c5d4bdaabaeaa203dde1d89284`，由 [ARCH-PLC-002 Development](../../../plans/ARCH-PLC-002-plc-json-export-feedback/tasks.md) 引为后继改动前固定候选。原 30 项 DS 固定副本已按历史资源记录清理。本次可从保留摘要重建旧 25 项清单的摘要，旧文件字节与当时完整 30 项快照已无法从该临时路径重新核对。
- 正式树当前 25 项清单 SHA-256 为 `44d34cb2e9c956a3afc9c3a61fb0bc781273e78c86b128a225656e3c6ea2534f`，与 [DS checklist 的 F-GUIDE-004 定向复验](checklist.md) 一致。两份手册 `USER_GUIDE.md` 与 `USER_GUIDE.zh-CN.md` 分别为 `f38595f553156cd71bea6ea82121a965fb696e4eeca13f2f5d11e3cf121f9a37` 和 `ed68926ea62b8ce13c1d8c4ba82c2c02c0cf8641c0745eb2ca7102a04077e3bd`。只替换回上轮速查的两份手册摘要，即复算得 `84e5160ec4a59385dc581547cb517710426bacb9e226cd5e249918a98df1c712`，支持这两次手册候选间其余 23 项一致。独立 F-GUIDE-004 的 `qa_passed` 限静态手册复验，覆盖确认、保存、加载时序、大小写文件后缀和双语链接；DS-005 r2 整体 `qa_blocked` 保留。
- 相对 F-GUIDE-003，当前 25 项有 18 项相同、7 项变化，其中两份是上述手册，另五项与 ARCH-PLC-002 末次交接相符：`runtime/src/services/catalog_export.rs`、`runtime/tests/plc_catalog_import.rs`、`src/services/deviceSimulator.ts`、`src/app/simulator/locales/en-US.json`、`src/app/simulator/locales/zh-CN.json`。ARCH-PLC-002 DS 表中另五项在旧 25 项路径之外，当前也与其末次交接相符：`runtime/tests/plc_catalog_export.rs`、`src/app/simulator/components/CatalogExportDialog.vue`、`src/styles/app.css`、`src-tauri/src/commands/catalog_export.rs`、`tests/plc-catalog-export.test.mjs`。依上述五项的列举顺序追加到原 25 项路径，每行 SHA、两个 ASCII 空格、DS 相对路径及 LF，当前 30 项摘要为 `b2c686a7be8b73f030d61480265d76ee078761a9df066036cc53af1053d6357f`。
- [ARCH-PLC-002 的 checklist](../../../plans/ARCH-PLC-002-plc-json-export-feedback/checklist.md) 载明该任务 QA1 `qa_failed`、E04 返工后 QA2 `qa_passed`、Human Owner 独立接受 r1 的逐 PLC 导出命名与结果反馈。当前与其末次摘要相符的是上述 10 个 DS 实现/测试文件，两份手册则对应 F-GUIDE-004 候选。ARCH-PLC-002 QA2 的 E04 基于 Vue 与 IPC 替身，沿用 QA1 文件核对及 Owner 的原生报告。与旧 DS 产品候选不同的字节按这两条后继记录衔接，覆盖各记录所列检查范围，当前工作树未接受一次新的全套产品或原生验证。

### DEV 自检与 developer_handoff

- `shasum -a 256` 核对批准后的 DS r3、父 r8、DS 历史 checklist 和写前 tasks，均匹配本节摘要，exit 0。`git rev-parse HEAD`、`git status --short --branch`、`git ls-files --others --exclude-standard` 及 DS 路径的 `git diff --stat` 核对正式交付树和旁支差异，exit 0。Python 3 标准库 `pathlib`、`re`、`hashlib` 只读核对上述清单、后继 r1 交接中的 DS 表及其返工替换，exit 0。Python 3 `json`、`itertools.islice` 读取本地会话指定行并核对可脱敏指标，exit 0。
- 写后以 Python 3 标准库核对历史前缀 SHA、两份批准 spec 与历史 checklist 摘要、本节相对文档链接和行末空白，exit 0。`git diff --check -- automation-world/device-simulator` exit 0；本 `tasks.md` 为未跟踪文件，另以 `git diff --no-index --check /dev/null automation-world/device-simulator/plans/DS-005-plc-json-bidirectional/tasks.md` 检查，exit 1 表示文件不同，无空白诊断。
- 唯一写入为本 `tasks.md` 的 r3 追加。本轮未访问 `.local/dev`、SQLite/MySQL、GUI、网络或 PLC，未运行测试、构建或上报，未创建、删除或重建临时验证资源。协调者先前清理的交换文件、基线、构建和候选快照的位置见上文「操作手册速查及资源收尾更新」；复核依赖仓内既有摘要、命令和原角色结论。已保留的版本及历史按原角色记录理解。1 秒存储回执仍可能为 `unknown`，应先读回再决定后续动作。旧版读取新增元数据、英文提交/落盘、Windows/VM、所有异常与并发、真实 PLC、长稳、部署及生产采用缺乏相应证据。

**Developer handoff** — `device-simulator::DS-005 r3`，精确批准 spec、父 r8、正式工作树、当前候选及历史前缀摘要见本节。交协调者按 STD 启动新的 fresh-context Verification，依据 [r3 §3–4](spec.md)、[历史 checklist](checklist.md)、[DAA-019 QA3](../../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/checklist.md) 与 [ARCH-PLC-002 QA/Owner 记录](../../../plans/ARCH-PLC-002-plc-json-export-feedback/checklist.md) 复核本次追加、候选衔接及证据归属。两项原证据缺口按上文保留。文档 verdict 由 Verification 决定，最终验收归 Human Owner。
