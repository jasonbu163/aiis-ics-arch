Task ID: DS-005
Revision: r2
Status: qa_blocked
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA2 索引返修已核实；DS05-06 证据阻塞交协调者处理，解除后重新 fresh-context Verification，Human Owner 最终验收待后续 gate。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator

# DS-005 r2 独立验证 QA1（2026-11-18，Asia/Shanghai）

## 结论与返修

**Verdict：`qa_failed`。** 本轮发现 F-QA1-001：新增导入源码和测试改变了项目实际文件结构，但 DS 的代码索引没有同步。已通知协调者返回 Development。功能、文件往返和隔离检查结果见下；这些结果不抵消索引失败，也不是 Human Owner 最终验收。

| 编号 | 证据与要求 | Development 应处理 |
| --- | --- | --- |
| F-QA1-001 | 根 [AGENTS.md §5](../../../../AGENTS.md) 明确要求“真实结构发生变化时同步维护 `CODE_INDEX.md`”。本候选新增 `runtime/src/services/catalog_import.rs`、`runtime/tests/plc_catalog_import.rs`、`src-tauri/src/commands/catalog_import.rs`、`src/app/simulator/components/CatalogImportDialog.vue`、`tests/plc-catalog-import.test.mjs`；[DS CODE_INDEX.md](../../CODE_INDEX.md) 第 27–32 行只列目录导出文件，`rg -n 'catalog_import|CatalogImport|plc_catalog_import|plc-catalog-import' automation-world/device-simulator/CODE_INDEX.md` 无匹配，索引与 HEAD 相同。上述新文件均有中文文件头；问题是索引缺失，不是文件头缺失。 | 在 DS-005 r2 已批准的 `CODE_INDEX.md` 路径内同步本任务实际新增结构及职责，按事实更新 Development handoff 和候选哈希；随后交新的 fresh-context QA。Verification 不代修。 |

**英文原生观察补充：** 最初 Development handoff 未有英文原生界面观察；Node 的导入/导出对话框测试把 `t()` 替换成返回 key 的 mock，render 替换为注释节点，因此键结构对称和函数测试本身不足以证明英文界面实际显示及切换。QA1 期间协调者使用同一 DS 二进制及 `.local/dev` 补做只读观察：顶栏切至英文后，Instances 页显示 `Import PLC JSON` / `Export PLC JSON`；导入对话框显示英文安全提示、Choose/Cancel，正常取消；导出选择实际 v6 和合成实例，确认目标及未加载状态后执行 `Preview all points`，观察英文表头、目标说明、四点中英文名与 description，取消且未选择目标目录或写文件；切回中文并正常退出，报告未修改实例或版本。这是协调者观察，非本 QA 自行操作；未在英文模式选择导入源文件、确认导入或执行导出落盘，不把该观察扩大为这些动作的英文原生证明。该补充不改变 F-QA1-001 的失败结论。

## 验证依据、候选与环境

- fresh-context 命名 Verification，独立读取根契约、workflow、根及 AW/DS README 与 PLAN、DS 完整 bundle、[DS-005 r2 spec](spec.md)、最终 [Development tasks](tasks.md)、[ARCH-PLC-001 r7](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 有效条款及适用的 `project-governance`、`aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`；存储和事务复核补读 `backend-arch`。角色为 contract_only，不声称存在平台 ACL 或自动强制路由。
- 正式源码工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，有并行 DAA/治理未提交差异。`shasum -a 256`：活动 spec `f9ec8c6941f61b50b31d02a8526c8d53c907486190dd48ae0cc1c374d94851b7`；最终 tasks `2fc693eb4523ffce72cad3514dd54e6fc13c7e5c736dc44a52efe92df7b29763`；父 r7 `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`，均匹配交接。tasks 中 24 项完整候选 SHA 以 Python `hashlib.sha256` 重新逐项核对，24/24 相符；候选路径均属 spec allowlist。并行 PLAN/catalog 与 DAA 差异不归入 DS Development 候选。
- 宿主为 macOS Darwin 24.6.0 arm64；Rust/Cargo 1.89.0、Node 22.19.0、pnpm 11.11.0。QA 使用自有 `/private/tmp/ds005-qa-r2-SMgAxo` 存放构建与合成数据；本 QA 未启动用户 GUI、连接设备、激活用户配置或发真实 POST。
- 对正式树 tracked 差异执行 `git diff --check -- automation-world/device-simulator`，exit 0；对五个新增文件分别执行 `git diff --no-index --check /dev/null <file>`，均为文件不同的 exit 1 且无空白诊断。`git status --short` 同时列出了并行治理文件和新的任务 bundle；不把它们误认作 DS 24 项产品文件。

## 按验收标准核对

| 标准 | 结果与范围 |
| --- | --- |
| DS05-01 | **有中英文入口及交互观察。** 实例页源码同时挂载导入、导出和新增按钮；中英文键分别为 `导入 PLC JSON` / `Import PLC JSON`，locale 键对称。协调者中文原生操作确实选保存 v6、勾选两实例并重导；英文显示、切换和只读预览补充观察见上。相关取消、同名、selected/loaded 差异及多选结果由本轮 Rust/Node 定向测试覆盖；英文文件选择、导入提交和导出落盘未实测。 |
| DS05-02 | **实际普通 DB/UDT 文件证据成立。** DAA 从现有 `DEV-PLC-A` 的保存草稿只读导出文件 SHA `e609252a4212d2c0f4587d89abc34fc8acbbf763a83c777a90eb5242dbd8336e`；协调者记录中文原生 DS 新建、显式填写 `127.0.0.1:31979`、确认并保存 v6，不重新提供 DB/UDT。QA 独立解析文件：1 DB、3 点，类型为 BOOL/INT/REAL，双语与独立 description 字段存在；3 个 description 均为空串，不能描述为该文件有非空 description。父 r7 沿用的 r5 §4.1 明确允许空说明且 §6.1 对 DS 缺省/空输出空串，故仅因实际值为空不判失败。此来源是既有普通 DB/UDT，不称合成或 catalog。 |
| DS05-03 | **实际文件与保存版本核对成立。** QA 独立比较 C 输入、首次导出和重开后导出：外部 origin、DB/点 ID、技术名、地址、类型、双语、旧名的存在性、description 和 source_path 一致。两份 DS 文件均引用 v6 `f4b55b18-4bfd-4cf1-b385-9dc73cb48b95`，payload SHA `865a68b41631a412effc33f318b01882fa81f28c201e0c8e642664f2f9f8b237`；重开前后只 `exported_at` 不同。重开文件 SHA `04c194da54cf35902f1fe52d20c1aa68bdab869fdd226db039a60da8c8d62168`。协调者记录其交 DAA 预览时因当前同源而阻断并取消，没有提交；B 的实际回导证据另见 DS05-06。 |
| DS05-04 | **合成定向测试通过，按其覆盖范围表述。** 本轮 Rust 覆盖双 producer、DB 启用缺省、显式/不可表达 TSAP、变化文件、取消、身份/端点冲突、伪造归档/映射、非法禁用点布局、ETag/并发及故障回执；保存重开和导出断言旧名 256 字节原样，Node 检查超限阻断。4096 点及单实例输出超额拒绝/其他实例继续的测试通过。 |
| DS05-05 | **合成测试及只读数据核对成立。** 两 producer 导入后 DB 和点均为停用；原生 B/C 的 DS v6 亦均停用。原 TIA 导入与 configuration store 定向回归通过。QA 只读检查 DS SQLite，当时无 WAL/journal，`quick_check=ok`；原 v5 `2448bb7b-7820-49f6-8764-d9124f4c50a5` 的 payload SHA 为基线 `4fa64ee107ea5410810c985119bb6c8d94e7af563c5a685e0217caae19a82ee7`，原两条 sourceVersions 对象仍在草稿，原 v5 与含两测试实例的 v6 均保留。当前草稿 0 实例、sourceVersions 从 2 增至 4，故不称草稿或整个 profile 零写入。 |
| DS05-06 | **A/B/C 的不同证据分别成立，见下节。** A 为任务自有合成 profile 的真实持久化服务测试；B 是协调者记录的中文原生实际文件与新本机提交；C 是上述现有 DB/UDT 只读输入。QA 独立重算文件、身份及存储证据，但没有自行重放用户 GUI。 |
| DS05-07 | **未完整通过。** Rust 35 passed / 2 ignored、Node 40 passed / 1 skipped，类型检查、Vite 构建、两份 fmt 和 20 个手册相对文件链接检查通过；构建 warning 及首次 QA 缓存失败见下。协调者已补充英文只读界面观察，范围见上；F-QA1-001 仍未通过。 |

## r7 A/B/C 的独立证据与边界

**A：自有合成服务 profile。** QA 核对 DAA 最终候选清单 `/private/tmp/daa019-dev.MKLyerrV/candidate-sha256-final2.txt` SHA `2800fc8f912950e92307bce9944d0624d4d1725955935d70ac6d158a076a9511`，正式 DAA 工作树 34/34 文件与清单匹配。与正式树相比，增强临时测试的两份源码差异为增加身份、绑定、来源与重开断言；`rsync -nrc --itemize-changes` 排除两测试文件和 target 后只报告四份生成 schema 的时间戳差异，未报告源码内容差异。增强测试二进制 SHA `f8d099162b3ec412c87468dc448b9335e97788fa892a064b8a36a6d35b897f3a`。QA 以 `DAA_PLC_READ_ALLOWED=false`、未设置 DAA 环境/profile 指向、自有 `TMPDIR` 独立重跑以下两个精确测试，各 exit 0、1 passed / 219 filtered；生成的 4 个配置/运行 SQLite 的 `PRAGMA quick_check` 均为 `ok`：

```text
env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT DAA_PLC_READ_ALLOWED=false TMPDIR=/private/tmp/ds005-qa-r2-SMgAxo/history /private/tmp/daa019-r2-dev.c0EWK6bZ/target/debug/deps/aiis_data_acquisition_agent_lib-d57255d4d287a29b infrastructure::local_store::catalog_export_tests::daa019_active_version_and_reimport_preserve_old_samples_queue_and_receipt --exact --test-threads=1 --nocapture
env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT DAA_PLC_READ_ALLOWED=false TMPDIR=/private/tmp/ds005-qa-r2-SMgAxo/history /private/tmp/daa019-r2-dev.c0EWK6bZ/target/debug/deps/aiis_data_acquisition_agent_lib-d57255d4d287a29b infrastructure::local_store::catalog_import_tests::daa019_history_requires_choice_and_separates_local_identities --exact --test-threads=1 --nocapture
```

测试使用实际本地存储和服务完成保存、激活、移除、再激活及新身份导入；核对旧配置、样本、队列、回执和绑定及新 PLC/DB/点/来源身份隔离。回执由测试数据与假 HTTP response 制造，不是真实 POST，不是原生 GUI。

**B：原生实际文件。** 对 `/private/tmp/ds005-daa019-roundtrip-vdmwh6dt` 中每个真实文件独立 `sha256` 并以 Python 比较 origin、DB/点外部 ID、技术名、类型、地址、双语、旧名存在性、独立 description 与 source_path：旧合成 seed `5198f7fef382f9524b81c66275b76cbdb779deb7741df16d3005f809bf6662e3` → DAA F1 `117f0614a63de4fd11e7dce14a50ed445be87137ce9a47e2cd295bd701973261` → DS F2 `ed5a0ddecb223803c6201727718e723a8f9a96168122f098c3271d1f6bc33570` → DAA F3 `840379d35815349025cbf6f450d47561fbc590969a7cefd2fdab2527b7d6e2cb` 一致。原外部 origin 为 `device_simulator` / profile `227189b1-d035-4a78-a054-ac56921a585a` / PLC `e1dc3ad5-305f-4367-af1b-92333a582730`；1 DB/4 点，含一条非空独立 description。F1 的本机 L1 为 `a123de20-3d26-4961-819f-0b00708e82cf`，F3 对应的 L2 为 `79294849-b7c7-4a58-bc47-5836fe4bc2a0`；它们不是外部 origin ID。协调者另记录用重开后 F2 实际新建 L3 `ac12bbc8-ecba-4b99-afe7-efe9b580a89e` 并在点位页观察默认选择、4 点未分组及停用，后通过 GUI 删除 L2/L3；该次未直接截获 IPC 返回。QA 核对 DS 重开文件 SHA `5c9fa568c7d3d866cee55539d94a317cb53107b3ead548805794cfa073471a92`，与 F2 仅导出时间不同。DAA 文件 DB 层不提供 enabled；DS 文件 DB/点均为自身停用事实。

**C 与保护事实。** 普通文件及 DS 重开文件的核对见 DS05-02/03。协调者在 DAA 操作期间曾误点 L1“测试连接”，返回“PLC 操作队列繁忙或对象不存在”；L1 未激活、读取开关关闭，未建立连接。不能记为从未尝试连接。DAA 侧 Development 只读复核在其 [tasks](../../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/tasks.md) 有精确记录（核对 SHA `7baafd2f8a5f6bd65cd59f7d7225e175172ef08938e630c273909d7d8922b952`）：8 个旧 revision 及 payload、active/previous、草稿和列出的样本 ID/SHA、队列、回执、绑定等与基线相符。前测只保存 context 8/来源引用 19/缺失 0 的汇总，没有逐条 context 摘要；后测 8 条 context 与对应旧 revision payload 一致，不能声称 context 已逐行前后哈希相同。样本其他列和 sample_delivery 也缺少前测逐行摘要。正常来源归档增加，不声称整个 DAA profile 零写入。

## 本轮独立命令与限制

- 从正式 DS 源码，使用自有 target 和合成 profile 执行 `DS_TEST_RUN_ROOT=/private/tmp/ds005-qa-r2-SMgAxo/rust-tests DS005_DAA_EXPORT=<Development 的合成 DAA 服务导出文件> DS005_DAA_EXPORT_SHA256=937c0f3aa0ce583821e4b647a2395a3bc97e0975424a5cb9fe9362f15d320ee5 CARGO_TARGET_DIR=/private/tmp/ds005-qa-r2-SMgAxo/target cargo test --offline --locked --manifest-path runtime/Cargo.toml --features test-automation --test plc_catalog_import --test plc_catalog_export --test point_display_names --test configuration_store --test source_import -- --test-threads=1`：exit 0，35 passed / 2 ignored。实际输入为 `/private/tmp/daa019-dev.MKLyerrV/daa-008-r2-a-fixtures/daa005-test-daa019-export-a7082f7d-6d82-4442-a59f-6eea15640c9b/successful/d1ca2e57-b83d-4b73-a908-b2a482b8b415.json`。首次使用从 Development target 克隆的缓存时 CMake 因缓存记录原路径而 exit 101；只移除 QA 自有副本的 `native-build` 目录后重跑通过，没有改源码，失败保留于此。
- `node --test tests/plc-catalog-import.test.mjs tests/plc-catalog-export.test.mjs tests/point-display-names.test.mjs`：exit 0，40 passed / 1 skipped；`pnpm exec vue-tsc --noEmit`：exit 0；`pnpm exec vite build --outDir /private/tmp/ds005-qa-r2-SMgAxo/ui`：exit 0，有依赖 PURE 注释和 chunk 大小 warning。`cargo fmt --manifest-path runtime/Cargo.toml --check` 与 `cargo fmt --manifest-path src-tauri/Cargo.toml --check`：exit 0。两份用户手册 20 个相对文件链接存在，未验证锚点。
- QA 比较实际 DS 原生 bundle 和正式 `pnpm tauri dev` 入口 debug 二进制，二者 SHA 均为 `883121ba395a2631ab658062903af92e87b64c12bf8eb2b26e36e43af285d8af`；协调者观察的中文 GUI 与文件结果按交接如实记为协调者证据，不冒称本 QA 自行重放。旧二进制读取新可选元数据未实测；1 秒存储未知回执风险保留，需读回，不盲目重试。Windows/VM、真实 PLC、真实外部 POST、生产部署、发布与物理 DDL 均未验证，也非本轮批准范围。
- 临时资源 `/private/tmp/ds005-qa-r2-SMgAxo` 为本 QA 的合成数据库、测试构建和 UI 输出；`/private/tmp/ds005-dev-Cq4eK0`、`/private/tmp/ds005-r7-a-review-VVJuij`、`/private/tmp/ds005-daa019-roundtrip-vdmwh6dt` 和 DAA 的两个临时目录仍含交接、复验或实际文件证据。QA 不回收；后续协调者在新 QA 和 Human Owner 验收后确认归属、无占用且不再承担证据作用时处理。不得清除用户 profile、原 v5、受保护最新 v6 或已归档来源。

## Human Owner 最终验收

待 F-QA1-001 返修并经新的 fresh-context Verification 后，由 Human Owner 自行决定；本记录不代为接受，也不授权发布或现场采用。

---

## DS-005 r2 独立复核 QA2（2026-11-18，Asia/Shanghai）

**Verdict：`qa_blocked`。** F-QA1-001 的索引缺漏已修复并通过本轮定向复核；但 DS05-06 明确引用父 r7 A06 / §4.1，并要求保护两端既有历史，现有证据仍有以下两个缺口。它们是验收证据阻塞，不是已证实的产品实现故障。QA1 的 `qa_failed`、具体证据和命令保留在上文；本轮更新文件头的当前状态及 handoff，追加本节，不改写 QA1 结论。

1. **父 r7 §4.1 B 的同一 L2 观察未闭合。** 协调者记录 L2 `79294849-b7c7-4a58-bc47-5836fe4bc2a0` 确实提交、在列表存在且停用，之后手工选择它再导出 F3；当时未记录其导入后的自动选中，也未直接截获原生 IPC `importedLocalPlcId`。另一次 L3 `ac12bbc8-ecba-4b99-afe7-efe9b580a89e` 的自动选中和未分组/停用观察，不能倒记为 L2；L3 也没有对应再导出。服务与 Node 测试是补充证据，不能把两次原生观察拼成父合同指定的同一 L2 结果。
2. **两端历史保护的前测证据不完整。** 已有基线和 QA1 的只读比对支持 8 个 DAA revision、active/previous、草稿、118 条 sample 的 ID/SHA、69 条 uploads 全行、73 条 attempts 全行、原 binding/source 等被列项目相符；当前 8 条 context 又与旧 revision payload 自洽，19 个来源引用完整。但前测只有 context 数量/引用汇总，缺逐行 context 摘要；`samples` 的其他列和 `sample_delivery` 也没有前测逐行摘要。当前自洽及合成 profile 测试不能证明这些用户历史字段在本次联测前后逐项不变。此结论不宣称实际发生数据修改。

**解除路径：** 优先由协调者提供可信的该次 L2 返回/自动选中原始记录，以及测试前相应历史的逐项基线或足以证明相同事实的原始证据，交新的 fresh-context Verification 核验。若不存在，交 PM 基于实际证据提出可验证的替代验收处理；涉及实质范围或验收变化时，须形成新 Revision 并获 Human Owner 精确批准。不能通过复测倒证缺失的历史前值，也不能由 Verification 自行豁免。当前 `qa_blocked` 不进入 Human Owner 最终验收为通过的 gate。

### 独立依据和候选

- 新 fresh-context Verification 读取根契约和 canonical workflow、根 / AW / DS 最近作用域 README 与 PLAN、DS 完整 bundle、ARCH-PLC-001 r7 活动合同及其沿用的 r5 §4–6、相关实现/diff 与 QA1/Development 可用测试记录；按被验证表面使用 `project-governance`、`aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`backend-arch` 和 `code-document-indexer`。角色为 contract_only，不声称平台 ACL 或自动强制路由。
- 正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的 HEAD 为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。DS spec SHA-256 `f9ec8c6941f61b50b31d02a8526c8d53c907486190dd48ae0cc1c374d94851b7`、父 r7 `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`、Development tasks `3c0d319f6ecae0628b6d52b7c6eac1f8744b7557bc3f2088fe1fc20f0f40c904`；写前 QA1 checklist `a44050702c5b7055461a63842f4e0c93d97c3490a7f305fcca41543f20b3e0eb`。并行 DAA 和治理差异不计入 DS 交付候选。
- Python `re` 按 tasks 规定的每行 SHA、两个 ASCII 空格、相对路径和 LF 提取最终清单，清单 SHA-256 为 `db1cfbd5fd74bee20863796766924b3571421bd4759543cd8d931bfa70aa61d8`；对正式树实际字节用 `hashlib.sha256` 比较，25/25 相符。最终清单前 24 行与 tasks 内返工前 24 行逐字节一致；该 24 项亦是 QA1 当时核对的产品候选。当前产品、索引和入口证据均以正式树及上述摘要限定。

### 按 DS 验收标准核对

| 标准 | QA2 结果与实际边界 |
| --- | --- |
| DS05-01 | **通过现有范围检查。** QA1 已核对中英文入口、导出选择/取消/同名及差异提示；本轮 locale 叶键 629/629、差集 0。协调者补做英文原生语言切换、两入口、导入/导出弹窗及导出预览；英文未实际选择导入源文件、提交或导出落盘。 |
| DS05-02 | **通过现有文件和协调者中文操作证据。** 实际普通 DB/UDT 文件 SHA `e609252a4212d2c0f4587d89abc34fc8acbbf763a83c777a90eb5242dbd8336e`；本轮解析为 1 DB、BOOL/INT/REAL 三点，三个独立 `description` 均存在且为空串，父合同允许空说明。协调者记录显式 loopback、确认并保存，未再次提供 DB/UDT。 |
| DS05-03 | **通过文件核对。** QA2 复算 C 输入、DS 首次导出与重开重导的外部身份、DB/点 ID、技术字段、双语、旧名存在性、description 和 source_path 均一致；两份 DS 输出除 `exported_at` 外相同，均引用保存版本 `f4b55b18-4bfd-4cf1-b385-9dc73cb48b95`、payload SHA `865a68b41631a412effc33f318b01882fa81f28c201e0c8e642664f2f9f8b237`。协调者记录将重开文件交 DAA 同源预览，阻断并取消。 |
| DS05-04 | **通过 QA1 对相同产品候选的定向测试范围。** QA1 Rust 覆盖双 producer、源启用、TSAP、冲突、来源/布局伪造、变化文件、并发、取消、故障回执、256 字节旧名及容量边界；Node 覆盖界面超限和状态处理。具体命令、ignored 和 unknown 回执见上文 QA1。 |
| DS05-05 | **DS 侧通过现有检查。** QA1 合成测试与实际 v6 核对新 DB/点停用，原 DS v5 payload 和两份旧来源保留；草稿来源从 2 增至 4，不称整个 profile 零写。DAA 侧跨端历史完整性受 DS05-06 阻塞限制。 |
| DS05-06 | **阻塞。** A 的自有合成 profile 服务级隔离证据由 QA1 独立复跑；B 确有原生 F1/F2/F3 和新本机身份、同源拒绝记录；C 为上述实际普通 DB/UDT 文件。本轮复算 seed→F1→F2→F3、F2 重开及 C→DS→重开各自的身份和技术字段投影一致，不能替代本节列出的 L2 和历史基线缺口。 |
| DS05-07 | **返工项通过；其他结果沿用 QA1。** CODE_INDEX 仅增加五条对应导入 service、桥接、对话框及两份测试，32 个索引文件目标均存在、新增目标各一次，五个新文件均有中文头部。QA1 以同一 24 项产品候选完成 Rust 35 passed / 2 ignored、Node 40 passed / 1 skipped、Vue 类型检查、Vite build、两份 fmt 及手册文件链接检查；本轮未重复相同源码测试。 |

### 本轮命令、实物与限制

- macOS Darwin 24.6.0 arm64，`rustc 1.89.0`、`cargo 1.89.0`、Node `v22.19.0`、pnpm `11.11.0`。`git show HEAD:automation-world/device-simulator/CODE_INDEX.md | shasum -a 256` 为 `9c62c5754bef8721993512679ed52abb1329266b22cc9318cd0266abf402714a`；当前索引 SHA `ae0fa67fede5e4404a31e2948a8fe133c7a20a365a02f4b19259dcd14ec83963`；`git diff --numstat -- automation-world/device-simulator/CODE_INDEX.md` 为 5 增 0 删，`git diff --check -- automation-world/device-simulator` exit 0。五个新增文件分别执行 `git diff --no-index --check /dev/null <file>` 均 exit 1（文件不同）且无空白诊断。索引链接由 Python `re` 提取并对 `Path.is_file()` 检查，只核文件存在，不核锚点。
- 本轮 Python 只读计算实际文件 SHA 并比较指定字段：seed `5198f7fef382f9524b81c66275b76cbdb779deb7741df16d3005f809bf6662e3`、F1 `117f0614a63de4fd11e7dce14a50ed445be87137ce9a47e2cd295bd701973261`、F2 `ed5a0ddecb223803c6201727718e723a8f9a96168122f098c3271d1f6bc33570`、F3 `840379d35815349025cbf6f450d47561fbc590969a7cefd2fdab2527b7d6e2cb`；DS 重开合成文件 `5c9fa568c7d3d866cee55539d94a317cb53107b3ead548805794cfa073471a92`、普通来源重开文件 `04c194da54cf35902f1fe52d20c1aa68bdab869fdd226db039a60da8c8d62168`。DAA producer 的 DB 层启用字段缺省，DS 两文件 DB/点均停用；按各自语义比较，未要求跨 producer 启用值相等。
- `shasum -a 256` 对照 DS 原生 bundle 可执行文件和正式入口二进制，均为 `883121ba395a2631ab658062903af92e87b64c12bf8eb2b26e36e43af285d8af`；QA1 使用的 DAA 增强服务测试二进制为 `f8d099162b3ec412c87468dc448b9335e97788fa892a064b8a36a6d35b897f3a`。本轮未启动 GUI、连接或激活设备、发 POST、改写用户 profile。协调者误点 L1 测试连接及其失败回执按 QA1 保留，不称从未尝试连接。
- `/private/tmp/ds005-daa019-roundtrip-vdmwh6dt` 仍含实际交换文件、基线和 app bundle；基线 SHA `2550195d9bd33e04e8396478bd546f08da589920b4e49470e9508d1c427d778d`。相关摘要和缺口已写在本 checklist，但文件原文和进一步核验仍依赖该临时目录；QA 不回收。待补证和 Human Owner 审阅不再依赖、协调者确认归属和无占用后按 workflow 处理，不删除用户 profile、原历史或已保留归档。QA1 所列其他临时资源和其保留条件不变。
- 旧二进制读取新增元数据、英文实质文件提交/落盘、Windows/VM、真实 PLC、真实外部上报、部署和发布未验证；1 秒存储未知回执须先读回，不盲目重试。QA2 不授予 Human Owner 最终验收。


---

## Human Owner 要求的手册补充：独立验证（2026-11-18，Asia/Shanghai）

**本次手册交接 verdict：`qa_failed`，退回 Development。** 以下是文档操作说明的问题，不声称产品实现故障。DS-005 r2 整体仍保留此前 `qa_blocked`：QA2 所列同一 L2 原生观察与历史前测基线缺口尚未由本次手册核对解除；既有 QA1 失败和 QA2 证据均保留。Human Owner 最终验收未发生。

| 编号 | 证据与影响 | 交 Development |
| --- | --- | --- |
| F-GUIDE-001 | [中文手册](../../USER_GUIDE.zh-CN.md#multi-db-import) 和 [英文手册](../../USER_GUIDE.md#multi-db-import) 第 44 行在逐 DB 完成布局后只说选点并做一次命名，没有说明每个导入 DB 的所有点均需命名，也没有明确跨页覆盖。第 287 行的示例只说每 DB 选当前页，不说明超过一页时继续选择。DB/UDT 新点初始技术名为空（`runtime/src/services/source_import.rs:281–289`）；点表切换 DB 会清空选择，表头只作用当前页（`src/app/simulator/views/points/index.vue:105–113,191–194`）；名称服务只变更选中点（`runtime/src/services/naming.rs:52–85`；`automation-world/shared/tia-import-core/src/naming.rs:145–146`）；导出校验所有点的技术名（`runtime/src/domain/plc_catalog.rs:202–212`）。因此照简略步骤只命名最后 DB 或当前页时，其他新点可仍为空并使该实例导出失败。以上为源码逻辑推断，未在原生 GUI 重放。 | 在双语通用路线明确：先逐 DB 完成布局，然后逐 DB 选择全部需要输出的点，超过一页时覆盖所有页，分别预览、核对并确认命名；对应修正示例措辞。以实际命名范围和页面选择行为为准。 |
| F-GUIDE-002 | [英文手册](../../USER_GUIDE.md) 第 26、42 行使用加粗界面标题 `Multi-source DB / UDT import`；实际 `SourceImportPanel.vue:3` 使用 `simulator.importSources`，`src/app/simulator/locales/en-US.json:124` 的标题为 `DB / UDT source import`。中文标题与 locale 相符。 | 将英文两处可见入口名称与实际界面一致；同时复查中英文其他操作文案。 |

**可操作性建议：** 两份手册第 30、51 行区分了选行与启用，但仅说启用所需 DB 和点。若介绍后续运行，建议说明 DB 表单的“启用”开关，以及点位行 **编辑 → 启用 → 完成编辑 → 保存草稿**（`points/index.vue:81–94,127–131`、`PointEditor.vue:37–45`）。仅交换 JSON 仍不要求启用或确认初值/策略。

### 检查范围和结果

- **DS05-01 / DS05-07 的手册部分：未通过。** 已对照中英文新增的手工建点、DB/UDT 和 PLC JSON 路线、按钮及运行时确认检查；问题见 F-GUIDE-001/002。实例创建、手工点编辑、JSON 新建草稿、保存/加载/启动分离等步骤在本次静态核对范围内可与源码对应。
- **DS05-05 / DS05-07 的边界：部分检查成立。** `CatalogImportDialog.vue:5–40` 和 `runtime/src/services/catalog_import.rs:114–155,203–252` 支持独立 loopback 监听确认、预览/提交及新 DB/点默认停用；点位行勾选与启用开关分别存在。`CatalogExportDialog.vue:6–24,60–64` 及 `runtime/src/domain/plc_catalog.rs:94–110,143–159` 显示导出从选定保存版本读取，客户端目标/TSAP 与加载版本差异分别确认，目录校验名称及布局而不要求初值/策略确认。结果未知时需读回，不盲目重试。
- 本次只核对手册增量及对应实现；DS05-02/03/04/06 的既有 QA1/QA2 结果和限制不因本节扩大。未启动或重放原生 GUI，未使用用户 profile，未重新运行未变源码的完整测试、构建或跨端联测；英文实际选择文件、提交和落盘仍未实测。真实 PLC、真实上报、部署和发布均不在本次验证内。

### 候选、环境与命令

- 正式工作树 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`；并行 DAA/治理差异不归入本次手册交接。`git rev-parse HEAD` exit 0。`shasum -a 256` 核对活动 spec `f9ec8c6941f61b50b31d02a8526c8d53c907486190dd48ae0cc1c374d94851b7`、父 r7 `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`、交接 tasks `f1fcc17a8ef44e44459b06e946305ed5de34c6b18947f52f3204585e8fb8ae4d`、写前 checklist `606056ea6a59c3b5db3a052648ee872c521c58f39f223027f47c2f3594e9bce6`；手册 `USER_GUIDE.md` 为 `1d3f2031cef8472dee778a60eea17ec4bd15b9ce50186f426286c6458f2ce366`、`USER_GUIDE.zh-CN.md` 为 `97fb417dc2149ef790b6cc88c0ab10d703559d981749eadd8124d1f0b00da597`，exit 0。
- Python 3 标准库只读提取 tasks 中 QA1 返修交接的 25 行 SHA/路径，以 `hashlib.sha256` 核对正式树：23 项不变，只有两份手册变化；按原顺序、两个 ASCII 空格及 LF 重建清单 SHA `d5b9db0f0c9fced72d30a59c08f4a23d881defed113c4c4ce1458e1fbbe9c4ce`，与 Development 交接一致，exit 0。该摘要只限定交接候选，不声称工作树其余差异属于本任务。
- `git diff --check -- automation-world/device-simulator/USER_GUIDE.md automation-world/device-simulator/USER_GUIDE.zh-CN.md` exit 0。Python 3 使用 `re`/`pathlib`/`urllib.parse` 提取两份手册相对 Markdown 文件链接，并核对目标文件及显式 ID/标题锚点：54 项、缺失 0，exit 0。Node 读取 `src/app/simulator/locales/{en-US,zh-CN}.json` 递归比较叶键：629/629，差集 0，exit 0；键对称不证明按钮名称与手册一致或语言切换实测。
- macOS 15.7.7、Darwin arm64、Node v22.19.0、pnpm 11.11.0；只读核对 `SourceImportPanel.vue`、点位/实例页面、目录导入导出对话框、编辑器、相关 Rust 服务和 locale。一次探索性 `wc` 错猜了不存在的 `SourceImportDialog.vue`，exit 1；随后读取实际的 `SourceImportPanel.vue`，不影响上述结论。
- 本次验证未创建临时产物，也不回收 QA1/QA2 已列且仍可能用于联测和验收的临时证据。角色为 contract_only；读取根与最近作用域契约、完整任务 bundle 和 workflow，按表面使用 `project-governance`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping`、`rust-runtime`，不声称平台 ACL 或强制路由。

**Handoff：** F-GUIDE-001/002 返 Development 修订双语手册并更新其 handoff/候选摘要；之后由新的 fresh-context Verification 复验。原 DS05-06 阻塞按 QA2 的解除路径独立处理，不能借手册返修或另一次观察倒补原始证据；结果仅交 Human Owner 决定最终验收。

---

## DS-005 r2 手册返工独立复验（2026-11-18，Asia/Shanghai）

**本次手册返工 verdict：`qa_failed`，退回 Development。** F-GUIDE-001 已部分改善但尚未全部关闭；F-GUIDE-002 和此前的启用路径建议在本次静态核对范围内已处理。这里的失败是说明范围与可操作性问题，不判定产品实现故障。DS-005 r2 整体继续保持 QA2 的 `qa_blocked`：同一 L2 原生观察及历史前测基线证据缺口未由本次手册复验解除；原失败、证据、解除路径和 Human Owner 最终验收待定均保留。

| 检查项 | 结果及依据 |
| --- | --- |
| F-GUIDE-001 | **部分修复，仍失败。** [中文手册](../../USER_GUIDE.zh-CN.md)和[英文手册](../../USER_GUIDE.md)第 37、44、51 行已说明点表选择可跨页累计、切换 DB 会清除，须各 DB 重新选择和确认。但第 44 行仍以“全部需要确认名称的点”/“every point whose name needs confirmation”描述选择范围，没有明确新导入 DB/UDT 中每个要随完整 JSON 导出的点都必须取得合法技术名，包括之后被停用的点。第 288 行的详细 DB/UDT 示例仍只说每个 DB 勾当前整页，没有说明超过一页时继续逐页累计后再预览。该示例实际只有 Alpha 2 点、Beta 4 点，各可在一页显示；问题在用户按该详细示例推广到多页数据时可能漏选，而非声称这六点示例必然漏选。`runtime/src/services/source_import.rs:281–291` 的新点初始 `name` 为空；`src/app/simulator/views/points/index.vue:105–113,191–194` 的表头只作用当前页，切 DB 清选择；`runtime/src/services/naming.rs:52–85` 和 `automation-world/shared/tia-import-core/src/naming.rs:145–146` 仅处理选中点；`runtime/src/domain/plc_catalog.rs:202–212` 逐点验证名称，没有跳过停用点。这是源码逻辑核对，未作原生重放。**交 Development：** 双语通用路线明确先完成每个 DB 的布局核对，再逐 DB、逐页覆盖所有需要输出且尚需命名的点，包括停用点；详细示例明确本例各一页及多页时的选择方法。保持名称确认的实例级真实语义，不虚构逐点确认状态。 |
| F-GUIDE-002 | **已修复。** 英文手册第 26、42 行均使用 `DB / UDT source import`；`src/app/simulator/components/SourceImportPanel.vue:3` 使用 `simulator.importSources`，英文 locale `src/app/simulator/locales/en-US.json:124` 对应同一标题。中文对应 `多源 DB / UDT 导入`。 |
| 运行前启用路径建议 | **已处理（静态范围）。** 双语手册第 52 行说明在 DB 表单启用 DB，以及逐点行内 `编辑 / Edit → 启用 / Enabled → 完成编辑 / Finish editing → 保存草稿 / Save draft`，再确认初值/策略、保存版本、停机加载与启动；也说明只导出不要求启用。对应 `views/points/index.vue:81–94,127–131` 和 `PointEditor.vue:37–45`。本次未在原生界面实操。 |
| DS05-01 / DS05-07 手册相关范围 | **未完全通过。** 对照实例页、DB/UDT 来源导入、PLC JSON 导入/导出对话框和中英文 locale，新增路线的关键按钮、分离监听确认、保存版本导出与显式启用路径在静态范围内可对应；F-GUIDE-001 使手册返工未完成。未重新判定其余验收项，也不扩大 QA1/QA2 的结论。 |

### 候选、命令与限制

- 正式工作树 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。活动 DS spec SHA-256 `f9ec8c6941f61b50b31d02a8526c8d53c907486190dd48ae0cc1c374d94851b7`、父 r7 `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`、Development tasks `79a609e4c2bb60738d5b30bc89486ac94bcc79742bf806d40044fa79523d6993`、写前 checklist `4b77154c3bc6f07e24cbe4d84ba636e06afb7c405051e9c726de4165398176d6`。两份手册 SHA 分别为 `USER_GUIDE.md` `2cf2558aafda555fa14a656823414439a7e794da0c92874f66220f101f8882ef` 和 `USER_GUIDE.zh-CN.md` `cd1c9a747cc988514fd970e88361d4588e27c9a1ba19139fc23ac644b2c102e8`。与 tasks 的 QA1 返修 25 项原清单比对：仅两份手册变化，其他 23 项不变；按交接的顺序、两空格和 LF 重建候选 SHA `8cdf839a33460e5eb175f2f96d3f7202db4dbbd8e2ffc529903f4008cdb4744d`，与本次 handoff 一致。并行 DAA/治理差异不归入本次候选。
- 在仓库根执行 `git diff --check -- automation-world/device-simulator/USER_GUIDE.zh-CN.md automation-world/device-simulator/USER_GUIDE.md`：exit 0。Python 3 标准库 heredoc 使用 `re`、`pathlib`、`urllib.parse` 与标题/显式 ID 提取检查两份手册相对 Markdown 链接及锚点：54 项、缺失 0，exit 0。另以 Python `hashlib.sha256` 提取 tasks 中最后 25 条 SHA 清单并逐项比对正式树、重算候选，exit 0。
- Node heredoc 递归比较 `src/app/simulator/locales/en-US.json` 与 `zh-CN.json` 叶键：629 / 629，差集 0，exit 0；静态逐项读取对应组件及 locale 核对按钮。键对称不证明原生语言切换。一次探索性 `rg` 因 zsh 对不存在的 `routes*` 展开失败而 exit 1；另一次误查 `scanDeclarations` 键得到 undefined，随后通过 `SourceImportPanel.vue:15` 确认实际键为 `simulator.scan`，并核对两种 locale 第 129 行，未把误查当产品缺陷。部分 zsh 登录 shell 输出 `/bin/ps: Operation not permitted`，上述记录为相应检查命令的实际退出结果。
- 首次尝试以 Python heredoc 追加本节因源文本编码解析失败而 exit 1，未执行写入；复核 checklist 与两份手册 SHA 未变后，以补丁追加本节。
- 环境：macOS 15.7.7、Darwin arm64、Node v22.19.0、pnpm 11.11.0、Python 3.9.6。本轮为手册复验，未启动或重放原生 GUI、未读取或修改用户 profile、未重复未变源码的 Rust / Node 完整测试或构建、未进行跨端联测；已有英文实际文件提交/落盘、旧二进制兼容和未知回执等限制继续有效。本轮未创建临时产物；QA1/QA2 所列临时证据及保留条件不变。
- fresh-context Verification 独立读取根和最近作用域契约、任务 bundle、相关实现/diff 与可用 DEV/QA 记录，按本次表面使用 `project-governance`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping` 与 `rust-runtime`；角色为 contract_only，不声称平台 ACL 或强制路由。
- 写后以 Python 比较本节之前的字节，SHA 仍为上述写前 checklist 摘要；`git diff --no-index --check /dev/null automation-world/device-simulator/plans/DS-005-plc-json-bidirectional/checklist.md` exit 1 表示文件不同，无空白诊断。两份手册和 tasks 的 SHA 仍与本次交接候选一致。

**Handoff：** F-GUIDE-001 的剩余手册缺口返 Development；更新 handoff 和候选摘要后须由新的 fresh-context Verification 复验。DS05-06 的阻塞仍按 QA2 既定路径独立处理，不能由本次手册结果替代；Human Owner 最终验收仍待相应 gate。

---

## DS-005 r2 最新手册返工及 Owner 文件独立复验（2026-11-18，Asia/Shanghai）

**本次手册交接 verdict：`qa_failed`，退回 Development。** F-GUIDE-001 中关于全部导入点（包括停用点）必须具有合法技术名、逐 DB 跨页累计选择的缺口已按下述静态检查补齐；F-GUIDE-002 和此前运行启用路径的修复仍成立。但新修订的通用 DB/UDT 路线存在 F-GUIDE-003 的核对时序问题。本次仅判定文档操作说明，未发现或宣称新的产品实现故障。**DS-005 r2 整体继续为 `qa_blocked`**：QA2 所列同一 L2 原生观察/IPC 与既有历史前测基线缺口没有解除；此前全部失败及证据保留，Human Owner 最终验收未发生。

| 检查项 | 本轮结果与证据 |
| --- | --- |
| F-GUIDE-001 范围与分页 | 已处理此前具体缺口。[中文手册](../../USER_GUIDE.zh-CN.md)和[英文手册](../../USER_GUIDE.md)第 44 行明确所有 DB/UDT 导入点（含停用点）须有合法技术名、逐 DB 逐页累计；第 288 行明确 Alpha/Beta 各一页，多页时覆盖所有页，切换 DB 清空选择。`runtime/src/services/source_import.rs:281–289` 中新导入点初始名为空；`views/points/index.vue:105–113,169–170,191–194` 的表头只选当前页、翻页可累计、切换 DB 清除；`runtime/src/services/naming.rs:52–85` 的候选只对所选点可变，`runtime/src/domain/plc_catalog.rs:202–212` 对全部点验证名称及唯一性，未跳过停用点。名称确认仍是实例级事实，不宣称逐点独立确认。 |
| F-GUIDE-003 核对时序 | **未通过。** 中英文通用 DB/UDT 路线第 44 行均写先执行“预览所选点命名 → 确认” / “Preview selected point names → Confirm”，随后才要求核对候选名；而 `src/app/simulator/components/PointNamePreviewDialog.vue:3–11,29–31` 在确认前展示候选表，`views/points/index.vue:219–223` 的确认提交成功后关闭候选。照通用步骤可能未经检查先确认，无法在该预览中再核对。第 288 行详细示例顺序已经正确，不消除第 44 行与之矛盾。**返 Development：** 两份通用路线明确按“预览 → 核对每个候选 → 确认”操作，保持其余范围、逐 DB 和跨页提示；更新 handoff 后交新的 fresh-context Verification。 |
| F-GUIDE-002 / 运行启用路径 | 此前修复仍成立于静态范围：英文 `DB / UDT source import` 与 `SourceImportPanel.vue:3`、英文 locale 第 124 行一致；中英文第 52 行分别指出 DB 开关和逐点编辑、启用、完成编辑、保存草稿的路径。`views/points/index.vue:81–94,127–131` 和 `PointEditor.vue:37–45` 与之对应。未重放原生界面。 |
| DS05-01 / DS05-07 手册 | 关键入口、保存版本导出、分离监听和运行启用路径经静态对照；F-GUIDE-003 使本轮手册返工未通过。其他验收项沿用 QA1/QA2 的范围和限制，本轮未重新判定产品整体。 |

### Owner 文件：只读事实与报告边界

对 `/private/tmp/plc-json-owner-manual-82_5g47q/daa-export/` 下实际三文件用 Python 3 `json.loads` 和 `hashlib.sha256` 只读解析，exit 0：

| 文件 | SHA-256 | 文件内 producer / 配置状态 |
| --- | --- | --- |
| F1 `4670e3bd-8d51-4734-84d8-303b3d2afca2.json` | `63260610d54cb339d2807366abf078a0682ceab034f6adb06a8385237e2cdd68` | `data_acquisition_agent` / `saved_draft` |
| F2 `66155773-770a-42ea-9ad9-cf72be59766d.json` | `c62949dcfef4c054c7f0147a35e10af9095523e67e416f1ae2445b29f7dc8ec0` | `device_simulator` / `saved_revision`，revision `63124411-7ad9-4e7e-aad1-39d5965b2bca`，payload SHA `d631324df188ddac7866ce78c0a31b9fadb05f9f1713354165ecd00579eab551` |
| F3 `7d2ca225-da04-4548-b755-22a174c0fd22.json` | `e14176aca6f28fb3e188d2904a29c22de89dad4e16fc7f0df132fb1a30f38ca2` | `data_acquisition_agent` / `saved_draft` |

三个文件各 1 DB / 4 点；比较 format/schema、外部 origin、PLC 名称和协议、DB 的 ID/名称/编号/长度，以及点的 ID/技术名/双语名/description/类型/字节与位地址及可选旧名、source_path 的**存在性和值**，投影一致。此三文件所有点均未提供旧 `display_name` 和 `source_path`，不把缺省说成非空值。DAA 文件 DB 层 `source_enabled` 缺省，DS 文件为 `false`；三文件四点均为 `false`，按 producer 各自语义记录，不要求跨 producer 状态相同。上述是文件静态事实，不证明 GUI 提交或 IPC 返回。

Development 的 [tasks](tasks.md) 转述 Human Owner 原生操作和协调者针对本轮用户 profile 的前后比较；本 QA 未自行访问 profile 或重放该操作，不将其转述升级为独立原生见证。`shasum -a 256 /private/tmp/plc-json-owner-manual-82_5g47q/full-baseline.json` exit 0，摘要为 `dfc8bee1006da84f98a3efe6298a892df435ea146b6f56a34a08d228fe438269`；本轮未独立逐行比对用户数据库。最新一轮也未截获对应 DAA IPC 返回，不能用它补造 QA2 的同一 L2 证据；新前测亦不能倒证先前缺失的用户历史前值。

### 候选、命令、环境与限制

- 正式工作树 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`；`shasum -a 256` 核对活动 DS spec `f9ec8c6941f61b50b31d02a8526c8d53c907486190dd48ae0cc1c374d94851b7`、父 r7 spec `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`、当前 tasks `74fa6bdd59c64326d7d50ad9d03673bc0a26afeb753559371e69461ef0bfbe74`、写前 checklist `05ba79e85b4bdcf1b3785703eed04de8ed9cd524487f218430c7a8a3e893edab`；英文手册 `8128905e67a7759a8681aa4d6889d0487254bc0378af2da36447ff59bd155905`、中文手册 `bea2285931d3b81684e31b71196f55b555f12ceed74de6a5467d8bfae0bce067`。Python 3 只读提取 tasks 的 QA1 后 25 项清单并以 `hashlib.sha256` 逐项核对：除上述两份手册外 23 项不变；按原顺序、两个 ASCII 空格和 LF 重建候选清单 SHA `8782cbe4b7f12964eae858172781cece06ff728c89674a164931481e301e41d6`，匹配最新 Development handoff，exit 0。并行 DAA 与治理差异不计入本交接候选。
- `git diff --check -- automation-world/device-simulator/USER_GUIDE.md automation-world/device-simulator/USER_GUIDE.zh-CN.md` exit 0；`git diff --no-index --check /dev/null automation-world/device-simulator/plans/DS-005-plc-json-bidirectional/tasks.md` exit 1 表示未跟踪文件不同，无空白诊断。Python 3 标准库 `re` / `pathlib` / `urllib.parse` 只读检查两手册相对文件链接及显式 ID/标题锚点：54 项、缺失 0，exit 0。
- 环境为 macOS 15.7.7 / Darwin arm64、Python 3.9.6、Node v22.19.0、pnpm 11.11.0。为文档返工复验，未启动 GUI、读取或修改用户 profile、连接真实设备、重新运行未变源码的测试与构建；QA1/QA2 原有测试命令、结果及英文文件提交/落盘、旧二进制兼容、未知回执等限制继续有效。
- fresh-context Verification 读取根及最近作用域项目规则、DS 完整任务 bundle、相关手册、实际 UI/locale/运行时实现、diff 和已有 DEV/QA 记录；按本次核验表面使用 `project-governance`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping`、`rust-runtime`。本角色为 contract_only，不声称平台 ACL 或强制路由。
- `/private/tmp/plc-json-owner-manual-82_5g47q` 的三份文件和基线仍供审阅及核验，原文件内容依赖此临时目录；QA 不回收。QA2 既有 `/private/tmp/ds005-daa019-roundtrip-vdmwh6dt` 等证据及保留条件不变。待相关复验和 Human Owner 审阅不再依赖时，由协调者确认归属、无占用和后续需要后按 workflow 处理；不删除用户 profile 或受保护历史。

**Handoff：** F-GUIDE-003 返 Development 后重新 fresh-context 验证；DS05-06 的两个阻塞按 QA2 解除路径独立处理。验证结论交 Human Owner 审阅，最终验收由 Human Owner 在相应 gate 作出；本记录不授权发布、部署或现场采用。

写后审计（追加本条前）：Python 3 `hashlib.sha256` 核对原有 37,954 字节仍为写前 SHA `05ba79e85b4bdcf1b3785703eed04de8ed9cd524487f218430c7a8a3e893edab`，exit 0；`git diff --no-index --check /dev/null automation-world/device-simulator/plans/DS-005-plc-json-bidirectional/checklist.md` exit 1 表示文件不同、无空白诊断。spec、tasks 和两份手册的 SHA 仍与本节交接候选一致。

---

## DS-005 r2 F-GUIDE-003 手册返工独立复验（2026-11-18，Asia/Shanghai）

**本次手册定向复验 `qa_passed`；DS-005 r2 整体仍为 `qa_blocked`。** F-GUIDE-003 的中英文时序缺口已在本次静态范围内关闭；此前的 `qa_failed`、QA2 证据和 Human Owner 最终验收状态保留。

| 检查项 | 本轮结果与证据 |
| --- | --- |
| F-GUIDE-003 / DS05-01、DS05-07 手册部分 | **通过定向静态复验。** [英文手册](../../USER_GUIDE.md)和[中文手册](../../USER_GUIDE.zh-CN.md)第 44 行的 DB/UDT 通用路线均明确先预览所选点命名、逐个核对候选，最后确认；第 288 行示例也保持预览、核对、确认顺序。`src/app/simulator/components/PointNamePreviewDialog.vue:3-11,29-31` 在确认前展示名称候选表，`src/app/simulator/views/points/index.vue:219-223` 提交成功后关闭候选，与手册顺序一致。本次未重放原生 GUI。 |
| F-GUIDE-001 / 002 | 复用上节既有静态 QA 结论；本轮对照手册第 44、288 行和点表 `index.vue:105-113,169-170,191-194`、`runtime/src/services/naming.rs:52-85`、`runtime/src/domain/plc_catalog.rs:202-212`，逐 DB 和跨页选择、切换 DB 清选、包括停用点须有合法技术名的说明仍在；英文 `DB / UDT source import` 与 locale 第 124 行一致。未将实例级名称确认说成逐点确认。 |
| DS05-02 至 DS05-06 等整体验收 | 本轮不重新判定。QA2 的同一 L2 原生自动选中 / IPC `importedLocalPlcId` 观察未闭合，以及当时前测缺少 context、samples 其他列和 sample_delivery 逐行基线，两项阻塞未解除；后来的 F1 / F2 / F3 及新基线仍按上节事实保留，未捕获对应 DAA IPC 返回，不能倒补旧观察或前值。解除路径仍为 QA2 所述原始证据，若无则由 PM 提出可验证替代验收并在实质变更时取得新 Revision 的 Human Owner 精确批准。 |

### 候选、环境和命令

- 正式工作树 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`；`shasum -a 256` exit 0：DS r2 spec `f9ec8c6941f61b50b31d02a8526c8d53c907486190dd48ae0cc1c374d94851b7`，父 r7 spec `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`，Development tasks `43db8fe80658e252b20a35c93c751de8cc89b5004ac717440d51ad913957bf11`，写前 checklist `a32cee5e2fb1734632ac6eca9efd52a61435b44b175e3c84f7eef4a40d3a7728`；英文手册 `29350674a651606cf16542f59f3b68efa0bd62f1e5d5af0a3acfed1ba7b6aecb`，中文手册 `d71005a6ab2533461a6a7044909cfed060e0dd77b5e2b816f387778fa3a3c559`。
- Python 3 标准库只读提取 tasks 中 QA1 返修后的 25 项清单，按原顺序核算实际文件 SHA；除两份手册外其余 23 项与原清单相同，按每行两个 ASCII 空格和 LF 重建的候选清单 SHA 为 `e0c3df10cc048a570d07a67168b58d82361b45c5d4bdaabaeaa203dde1d89284`，与最新 Development handoff 一致，exit 0。此清单不包含并行 DAA / 治理差异或角色文档。
- `git diff --check -- automation-world/device-simulator/USER_GUIDE.md automation-world/device-simulator/USER_GUIDE.zh-CN.md` exit 0；Python 3 标准库只读检查两份手册相对 Markdown 文件链接和显式 ID / 标题锚点，54 项、缺失 0，exit 0。Python 按命名预览的位置向后依次查找核对和确认，中英文均顺序正确，exit 0。此前首次顺序脚本错误地取了同一行更早的布局“确认”，因此 exit 1；修正定位后通过，该脚本错误不是产品失败。
- macOS 15.7.7 / Darwin arm64，Python 3.9.6，Node v22.19.0，pnpm 11.11.0。复验未启动或重放 GUI，未访问用户 profile、连接 PLC 或上报，也未重跑未变源码测试与构建；QA1 / QA2 原有测试输出和英文实质文件提交/落盘、旧二进制兼容、未知回执等限制继续有效。本轮未生成临时产物，也未回收原有证据。
- 本 fresh-context Verification 阅读适用根及最近作用域规则、DS 完整 bundle、相关实现 / diff 和可用交接及 QA 证据，按表面参考 `project-governance`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping`、`rust-runtime` 和 `desktop-tauri`；为 contract_only。
- 首次尝试以 Python heredoc 追加本节时源文本编码解析失败、exit 1，未执行写入；随后使用补丁追加。

**候选衔接和 handoff：** 本次 DS 手册返工的复验已结束，协调者可将上列精确候选纳入 ARCH-PLC-002 r1 的候选固定过程。该任务 §1 要求在修改共同文件前确认两端现有人工联测、返工和 QA 取证不再依赖被覆盖文件，并固定候选及证据；摘要本身不保存原文件，仍须由协调者确保旧候选原字节和证据可用并完成两端衔接。此记录不解除 DS05-06 的阻塞，不授予 Human Owner 最终验收；验证结果交 Human Owner 审阅。

写后审计（追加本条前）：Python `hashlib.sha256` 核对原有 46,332 字节仍为写前 SHA `a32cee5e2fb1734632ac6eca9efd52a61435b44b175e3c84f7eef4a40d3a7728`，exit 0；`git diff --no-index --check /dev/null automation-world/device-simulator/plans/DS-005-plc-json-bidirectional/checklist.md` exit 1 表示文件不同、无空白诊断；spec、tasks 和两份手册 SHA 仍与本节记录一致。

## 2026-11-18 双语操作速查定向复核（DS-005 r2）

**本轮文档 verdict 为 qa_failed，F-GUIDE-004 退回 Development。整个 DS-005 r2 仍为 qa_blocked。**

- 候选定位：正式工作树 HEAD 为 f7c5608c0e433612b15821a578a7ef3e4f155cdb。DS 目录执行 `shasum -a 256 USER_GUIDE*.md plans/DS-005*/tasks.md` 成功；英文、中文和 tasks 摘要分别为 84b2b972e0f02b4484d9aface9919c0a48a6d9821bcfbba2b1ca8de96a613254、cacc118b2b66af77c7b9eb028b1fad42af7ad91d0e4c90cfe594f09f324c5ee0、527f62cf2f9f7c12e5a2c81086f1c052137ef9bc77cb6d0170bbddc741371fce。写前 checklist 摘要 1d0263673b3486cc225fd01feab6fb25fa0ea46f615a97fd41e6813e28cf60f2。
- 中英文速查均从三种材料直接进入相应路线。点位页和编辑器提供手工 DB、点、类型和地址；SourceImportPanel 要求先保存编辑，再扫描、选声明与目标、预览并确认；CatalogImportDialog 需要选择文件、填写并确认本机监听、预览后提交新草稿。逐 DB 地址先于整实例命名，点表表头只选当前页，换页可累选，换 DB 清空。命名预览按全实例处理，DB/UDT 要覆盖停用点，JSON 固定名是整实例候选。证据见 views/points/index.vue:97、109、191、219，PointNamePreviewDialog.vue:6，runtime/src/services/naming.rs:31、52。速查把预览、核对、确认分别写出，运行与仅导出各有清楚的后续动作。导出对话框先预览，再选目录并导出可用行，按实例查看结果。
- **F-GUIDE-004**：两份手册第 347 行（§7 步骤 2）先保存版本，然后仅确认启用点的初值/策略并加载该版本。即使所有点都启用，在保存版本后补的确认也只进当前草稿。若已启用 DB 内有停用点，运行加载还会检查这些点。runtime/src/services/configuration.rs:160、188 和 runtime/src/domain/layout.rs:267 及其后两项签名校验与速查相符。请将双语详例与速查对齐：后续要运行时先确认各启用 DB 内全部点（含停用点）的初值/策略，再保存版本并加载该版本；若导出版本已保存，补确认后另存并加载新版本。仅导出可以直接保存版本。
- 文件名边界：CatalogExportDialog.vue:106 以忽略大小写的方式检查结尾，已有 .json / .JSON 时保留原名和大小写，否则追加 .json。两份手册 §7 步骤 4 已说明只有一个扩展名，但未明说已有混合大小写后缀会原样保留，可在同轮补明。
- 静态验证：在 DS 目录运行 Python 3 标准库 pathlib/re 检查 Markdown 链接和显式锚点，英文 23/23、中文 23/23 通过。git diff --check -- USER_GUIDE.md USER_GUIDE.zh-CN.md 无诊断。本轮只读复核文档和源码，未重跑全套构建、原生桌面或 PLC 联测，未访问用户 profile、连接设备或改变应用状态。
- 旧临时文件已按 Owner 授权清理（协调者及 Development 交接记录），仓内仍有历史记录与摘要。本轮未从删除的原件重验。DS05-06 的原生 IPC 观察和历史基线缺口继续沿用。文档修订后交新的独立 Verification 复核；最终验收归 Human Owner。

## 2026-11-18 F-GUIDE-004 双语手册限定复验

**F-GUIDE-004 已关闭，本次文档复验为 `qa_passed`。DS-005 r2 整体仍为 `qa_blocked`。**

- 中英文手册第 2 节速查、第 3.3 节示例和第 7 节步骤 2–4 的时序一致。仅导出时确认 DB 地址和点名、保存草稿再保存版本。运行时，每个启用 DB 的所有点（含停用点）先确认初值和策略，再保存版本，并在实例停止时加载新保存的版本。已保存导出版本后补确认，需要另存、加载新版。运行依据为 `runtime/src/domain/layout.rs` 的启用 DB 分支与第 298、301 行逐点检查，`runtime/src/services/configuration.rs` 第 150–174 行将确认签名写入候选草稿。旧快照保留原内容。第 7 节两种语言的文件名规则均与 `CatalogExportDialog.vue:106` 一致，已有任意大小写的 .json 后缀原样保留，否则追加 .json。
- Darwin arm64，正式工作树 HEAD 为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。DS 目录执行 `shasum -a 256 USER_GUIDE*.md plans/DS-005*/tasks.md` 核得英文、中文、tasks 分别为 `f38595f553156cd71bea6ea82121a965fb696e4eeca13f2f5d11e3cf121f9a37`、`ed68926ea62b8ce13c1d8c4ba82c2c02c0cf8641c0745eb2ca7102a04077e3bd`、`edc160f6a8b4e119333a5f47563c985b27b52bd2dc8dee344ddd217336462244`。写前 checklist 摘要为 `095e160c0541583f5e7cc48855e6d2f6a8a66d7c774053d5b753a80d8ee03239`。
- Python 3 按 tasks 最后一组 25 个候选路径、两个空格及 LF 复算摘要，得 `44d34cb2e9c956a3afc9c3a61fb0bc781273e78c86b128a225656e3c6ea2534f`。仅替换回上轮两份手册摘要后重得上轮 `84e5160ec4a59385dc581547cb517710426bacb9e226cd5e249918a98df1c712`，本轮其余 23 项一致。两份手册的 46 处相对链接及其显式锚点检查通过；`git diff --check -- USER_GUIDE*.md` exit 0。
- 限定静态复验，未运行 GUI、访问用户 profile 或重跑构建。历史临时工件根据交接已按用户授权删除。DS05-06 同一 L2 的 DAA 原生选中和 IPC 返回值对应证据、旧前测逐行基线仍缺失。本轮结论交 Human Owner 审阅，最终验收待 Human Owner 决定。

## 2026-11-18 · DS-005 r3 独立文档复核

**Verdict 为 `qa_passed`，限 r3 §3 的既有证据收尾。** Human Owner 对本修订的最终验收待决定。r2 的 QA1 失败、QA2 整体阻塞、手册各轮失败及限定复验均保留原判。

| 标准 | 独立复核依据与适用边界 |
| --- | --- |
| DS05-01 | 本文件 QA1、QA2 及手册复验记录覆盖双语入口、选择保存版本、逐实例导出、重名及取消。协调者英文原生记录止于切换、弹窗、预览和取消；英文选择文件、提交与落盘尚无实测。 |
| DS05-02 | 历史普通 DB/UDT 文件含一 DB、BOOL/INT/REAL 三点，其独立 description 均为空。协调者记录中文导入、手填本机监听及保存；当时 QA 核过实际交换文件。 |
| DS05-03 | 原 QA 比对 DS v6 保存重开后重导的外部身份和点位字段。[DAA QA3](../../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/checklist.md) 与本文件另记 Owner 新轮一 DB 四点的 F1/F2/F3 摘要、身份、地址、类型及双语等指定字段。归属分别为当时文件检查人与界面操作者。 |
| DS05-04 | QA1/QA2 原候选合成检查覆盖双 producer、TSAP、冲突、取消、并发、非法布局、绑定完整性与 256 字节旧名。假回执和隔离 profile 仅支持服务层覆盖。 |
| DS05-05 | 原记录支持新建 DB/点停用，既有 v5 及所列来源保留，草稿有新增。原轮误点连接及协调者报告未建立连接仍按其记录；[DS-004 原生隔离事件](../DS-004-bilingual-point-display-names/checklist.md)的影响仍未知。 |
| DS05-06 | Owner 报告中文 DAA→DS→DAA 往返、同源拒绝、移除旧草稿后新建 L2、无手选即显示该 PLC 和四点并再次导出。协调者另报本地 ID 区别于外部 origin，四点停用、未分组。同次 IPC 返回值未捕获。DAA QA3 仅核新轮前测所列 37 表旧行及新增行，更早的 context、samples 其他列及 sample_delivery 逐行前值仍未知。 |
| DS05-07 | 历史 Rust 35 passed / 2 ignored、Node 40 passed / 1 skipped、类型与构建及格式检查均按原候选引用，首次缓存失败、构建警告保留。F-GUIDE-004 复验仅覆盖双语手册的确认、保存、加载、后缀及链接。 |
| DS05-08 | 按原 25 项清单路径重算得 44d34cb2e9c956a3afc9c3a61fb0bc781273e78c86b128a225656e3c6ea2534f，相对 F-GUIDE-003 清单变化七项（双语手册、导出服务、导入测试、TS 服务、两份 locale）。按交接顺序追加五项后得 b2c686a7be8b73f030d61480265d76ee078761a9df066036cc53af1053d6357f。[ARCH-PLC-002](../../../plans/ARCH-PLC-002-plc-json-export-feedback/checklist.md) 记录该导出反馈范围 QA1 失败、E04 返工用 Vue/IPC 替身复验、QA2 通过及 Owner 接受；两份手册另有 F-GUIDE-004 复验。当前组合候选缺少整套原生或产品复测。 |

**跨端上报佐证（DS05-06）**。按 [spec §2.4](spec.md) 的行号读取既有协调者会话，核对报告及脱敏汇总。其本机观察覆盖 seq 91–103 共 13 条，回执 status 为 committed、outcome 为 created 或 duplicate，正文 SHA 对应。至少一点的双语显示名均有值，13 份请求正文无显示名字段及对应文本；MySQL history 核对的是身份、摘要、指定三点字段和值及点集无显示类字段，latest 三点 good、seq 103。对应时段 DS 日志未见 WARN/ERROR 是协调者的观察。该样本仅支持此次本机配置的 DAA/后端链路。

**环境及命令**。Darwin arm64，正式树 HEAD f7c5608c0e433612b15821a578a7ef3e4f155cdb。shasum -a 256 核得本任务 spec 100f54502135b541ec9138748e03b1c1e34ff6a3a49f7fe127cbbca595aaa274、父 r8 spec 38085d5f0dd5d9db444008b9e04963371ddff3995cbb050641281ce6517931e5、tasks e9d30f299db291ba89e47abaa1d830e0079c9fa650d9faafb6190047c2e58b7e、写前 checklist 93578dbd90f0e62bbafb79cbe3550eeeedb410107824eb95edf21cb3349365d3。Python 3 hashlib/pathlib/re 复算 tasks 历史前 56,117 字节 edc160f6a8b4e119333a5f47563c985b27b52bd2dc8dee344ddd217336462244、候选清单及 r3 交接相对链接，成功。git diff --stat、git status --short 和 git diff --check -- automation-world/device-simulator 核对并行工作树差异，空白检查无诊断。私有会话的结构化输出首次作为字符串解析遇到 TypeError，按实际结构读取后核得 13 条回执/摘要有效、13 条指定身份摘要与点集匹配、13 条后端点集无显示类字段。

**资源与交接**。旧交换文件、基线及候选副本据原交接已按 Owner 同意清理，原件不可复核。本轮只追加 checklist，未生成临时工件，未运行测试、构建、GUI、PLC、数据库查询或上报，未访问用户 profile。旧版兼容、英文完整操作、真实设备、长稳及生产采用仍无相应证据。r3 文档标准无待返工项，交 Human Owner 决定最终验收。
