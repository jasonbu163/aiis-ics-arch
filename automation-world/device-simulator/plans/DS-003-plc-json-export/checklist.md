Task ID: DS-003
Revision: r5
Status: qa_passed
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Owner Role: Verification
Allowed Writers: Verification
Handoff: DS-003 r5 QA2 qa_passed -> Human Owner 最终验收；保留 QA1 失败和 QA2 阻塞历史

# QA1：独立验证记录

2026-11-17，macOS Darwin arm64。Verification 在 Development handoff 后以 fresh context 独立阅读根契约、canonical workflow、AW/DS 最近规则、完整任务 bundle、交付源码及 scoped diff；按触达面使用 `project-governance`、`aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`。本 profile 为 contract_only；角色约定和 diff 审计不是平台 ACL 或强制路由证明。未修改实现、测试、spec、tasks、其他任务资料或用户 `.local/dev`。

## 判定：qa_failed

**QA1-F01 — 非 RFC variant 的点 ID 被保存并作为 UUID v4 导出。** DS-003 r5 §3 和父规格 ARCH-PLC-001 r5 §4.1 要求规范小写 UUID v4，DS02/DS03 要求完整严格格式与无效身份阻断。`runtime/src/domain/plc_catalog.rs:43-44,147-150` 的 `valid_id` 只检查规范字符串和 `get_version_num() == 4`；当前锁定 uuid 1.23.3 的 `get_version_num()` 只读取版本数字，不检查 variant。`runtime/src/domain/configuration.rs:286-294,340-342` 也允许可解析的该 ID 通过配置校验。

独立测试将合成点 ID 设为 `55555555-5555-4555-0555-555555555555`：Python `uuid.UUID` 返回 `variant=reserved for NCS compatibility`、`version=None`；对照 `55555555-5555-4555-8555-555555555555` 返回 RFC variant、version 4。使用任务自有临时 profile，通过实际 `App` 的配置 store 保存并发布，再调用实际 catalog 预览、目录绑定和 commit：`configuration_validate=Ok(())`、`preview_issues=[]`、`committed=true`、逐文件 `result=written`，导出 JSON 仍包含该 NCS 点 ID。合成输出 SHA-256 `28b28abc3020be9a833de90d61d83cc225b6fca2a1f83142232715422ab8b8a9`。这是可复现的导出器失败，不声称产品界面会自动生成这样的 ID；保存版本内出现该身份时，不应生成无效交换文件。

修复后 Development 应回归 RFC variant 和版本、大小写/规范形式以及适用的 profile、revision、PLC、DB、点身份，并确认错误按实例阻断和其他有效实例单独处理；重新冻结源码、锁文件和测试记录后 handoff，必须由新的 fresh-context Verification 复核。此建议不授权 QA 修改实现或扩大批准范围。

### QA1-F01 可复现证据

实测从正式 DS 工作树读取源码，在 `/private/tmp/ds003-qa-qrPhTm/uuid-qa` 创建一次性 harness。其 Cargo.toml 依赖 `ds-runtime` 的正式工作树路径和 `serde_json = "=1.0.150"`；先复制正式 `runtime/Cargo.lock` 到该目录，再运行 `CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo run --offline --locked --manifest-path /private/tmp/ds003-qa-qrPhTm/uuid-qa/Cargo.toml`，exit 0。最终 harness lock 与正式 runtime lock 的 `diff -u` 仅多出该 `ds003-uuid-qa` 本身的包条目；正式锁文件未改。首次直接 `rustc` 链接不同 serde 编译工件失败，首次未复制锁的离线 harness 也复现问题；以上 exit 0 结果是复制正式锁后重新运行的结果。以下完整测试主体作为持久证据，重跑前应选择新的自有临时根及 profile；未使用网络或用户 profile：

```rust
use ds_runtime::{app::App,domain::{configuration::{self,Workspace},layout,plc_catalog::Target},services::catalog_export::{self,PreviewIntent,TokenIntent}};
use std::path::Path;
fn main() {
 let ncs="55555555-5555-4555-0555-555555555555";
 let mut w:Workspace=serde_json::from_str(r#"{"schemaVersion":1,"instances":[{"id":"11111111-1111-4111-8111-111111111111","name":"Synthetic","port":32194,"dbs":[{"id":"22222222-2222-4222-8222-222222222222","name":"DB","number":21,"length":2,"manual":true,"enabled":true,"points":[{"id":"55555555-5555-4555-0555-555555555555","name":"Count","dataType":"INT","byte":0,"manual":true,"enabled":true}]}]}]}"#).unwrap();
 for i in &mut w.instances { for d in &mut i.dbs {d.address_confirmation=Some(configuration::AddressConfirmation{structure_sha256:layout::structure_signature(d),layout_sha256:layout::layout_signature(d),method:"manual".into(),reason:"synthetic QA".into()});} i.names_confirmation=Some(layout::names_signature(i));}
 println!("configuration_validate={:?}",configuration::validate(&w));
 let app=App::open(Path::new("/private/tmp/ds003-qa-qrPhTm/variant-profile-commit")).unwrap();
 let d=app.configuration.store.load().unwrap();let s=app.configuration.store.save(&d.etag,w.clone()).unwrap();let rev=app.configuration.store.publish(&s.etag).unwrap().revision_id.unwrap();
 let target=Target{instance_id:w.instances[0].id.clone(),host:"127.0.0.1".into(),port:32194,rack:0,slot:1,connection_confirmed:true,loaded_difference_confirmed:true};
 let v=catalog_export::preview(&app,PreviewIntent{revision_id:rev,targets:vec![target]}).unwrap();
 println!("preview_issues={} emitted_point_id={}",v["rows"][0]["issues"],v["rows"][0]["document"]["dbs"][0]["points"][0]["id"]);
 assert_eq!(v["rows"][0]["document"]["dbs"][0]["points"][0]["id"],ncs);assert!(v["rows"][0]["issues"].as_array().unwrap().is_empty());let token=v["token"].as_str().unwrap(); let dir=Path::new("/private/tmp/ds003-qa-qrPhTm/uuid-export"); std::fs::create_dir_all(dir).unwrap(); catalog_export::choose_directory(&app,token,dir).unwrap(); let receipt=catalog_export::commit(&app,TokenIntent{token:token.into()}).unwrap(); let file=dir.join(format!("{}.json",w.instances[0].id)); let exported:serde_json::Value=serde_json::from_slice(&std::fs::read(file).unwrap()).unwrap(); println!("commit_receipt={} exported_point_id={}",receipt,exported["dbs"][0]["points"][0]["id"]); assert_eq!(exported["dbs"][0]["points"][0]["id"],ncs); assert_eq!(receipt["rows"][0]["result"],"written"); assert!(app.shutdown());
}
```

## 输入身份与真实文件对照

- 交接基线 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`；spec SHA-256 `9adf299af89711855be896938cf7e6148f4332e171a984aebf10dd32d7c6cd89`；tasks SHA-256 `edcab9f2f52d652f502e602f0fe21dc21adc8e208d0aa6a58fcd34fab338c218`。QA 两次从 tasks 的冻结清单读取并核对 29 个正式工作树文件，均匹配；最后一次检查在本 checklist 写入前。工作树含其他任务和用户已有改动，不能将共享文件整份 diff 都归因于 DS-003。
- 独立只读打开 DS `.local/dev/device-simulator-v1/config.sqlite`（SQLite URI `mode=ro&immutable=1`，读取前无 WAL/SHM），对照 v3 revision `3d50439c-fb2b-41bd-9d95-56c67cd98672` 的原始 payload、存储摘要和实际文件声明摘要，三者均为 `06dc1f3d5c2440fb66dc8af63de92c50ee4bf095e22c6280efd70e2ff60b976b`。实际文件实例 `31d327ba-2b97-4f5e-8949-6956ac3a5648`，文件 2407 bytes，SHA-256 `0268a8098bb36c4b3bdc3f89141ef31123c56fb34ba47e33e275cd87a378e9a6`。
- QA 独立逐项比较该文件和该版本的 1 个 DB、4 个点：ID、名称、DB 编号/大小、类型、byte/bit、各层 enabled、双语、描述及旧值一致。该真实文件覆盖 BOOL、INT、REAL、停用 BOOL，**不含 STRING**；STRING 与停用 DB 等仅由合成 Rust 测试覆盖。源 revision 的读取与文件对照不等于 QA 亲自操作原生导出或 DAA 采集。
- tasks 记录协调者使用最终候选的同一 JSON 进行 macOS 临时原生包选择导出、DAA 新建及 15 条本地 good 样本，并报告停止/清理；QA 未亲自观察这些 GUI/采集操作，不把它们记成独立原生复现。实际同来源重复导入拒绝未被该协调观察覆盖。

## 验收项检查

| 条目 | QA1 结论与范围 |
| --- | --- |
| DS01 | 部分：真实文件与保存版本字节、实例及点已独立只读对照；selected/loaded 差异的提示有源码及合成测试，QA 未亲自重做真实原生操作。 |
| DS02 | **失败**：QA1-F01 允许无效 UUID variant 进入导出文件。真实文件与版本的四点对照成立；STRING 为合成覆盖，不是该真实文件证据。 |
| DS03 | **失败**：QA1-F01 的无效 ID 未定位或阻断。其他已运行合成用例只覆盖指定子集；不可读取的损坏版本在逐实例诊断前整体拒绝，其边界仍需重验。 |
| DS04 | 部分：合成测试检查无效 host/数值、loaded 确认及非默认 TSAP；loopback/不兼容提示有成对文案和源码。未独立做原生负值输入或穷举全部端点。 |
| DS05 | 部分：合成测试检查已有、晚创建、symlink 目标、替换目录、重复确认；代码采用同目录临时文件与排他 linkat。只读/写错与提交边界竞争未独立全面重现；Development 已报告临时文件身份检查与系统调用之间的同用户竞争及目录移动结果未知的限制，不能扩大为完整系统级隔离证明。 |
| DS06 | 部分：合成测试检查保存 payload/草稿隔离和版本删除/目录替换；实际用户 profile 仅有事后只读对照，没有本 QA 的操作前后比较；QA 未启动网络或实例。 |
| DS07 | 部分：Node 测试验证逻辑、双语 locale 对称及共享表格组件；其 render 是测试替身，QA 未独立确认中英原生界面可操作。 |
| DS08 | 部分：25 项 Rust 测试中包含合成版本、store、source import 和 owner 回归；原生选择器与落盘仅有协调者在临时包的观察，不冒充本 QA 原生操作或普通入口完整 GUI 验证。Windows 等未测。 |
| DS09 | 部分：实际文件、SHA、revision/instance 对照独立核实；首次导入/本机采集是协调者观察；同来源再次导入实际拒绝尚无本 QA 观察。合成 DAA 冲突测试不能冒充同一实际文件的重复导入。 |
| DS10 | 部分：本 QA 在正式树和项目锁上完成列出的 Rust、Node、类型、构建和 native-s7 bridge 检查；受限语义仍有 QA1-F01，故不以命令通过代替任务通过。 |
| DS11 | 部分：Rust 合成测试覆盖旧值、双语、描述、停用点与 STRING；真实文件包含双语/描述/停用 BOOL。旧 revision 的原生操作及语言切换前后文件 SHA 未由本 QA 独立执行。 |
| DS12 | 部分：本 QA 仅读取既有 `.local/dev` 版本与文件；协调者测试进程、清理及历史事实以 tasks 原记录为准，不能倒记成本 QA 全过程观察。 |
| DS13 | 源码检查：中英文 USER_GUIDE §7 均含 profile 核对、测试实例、版本选择、导出、SHA、同文件交 DAA 和安全清理说明，且声明操作说明不等于验证。 |

## 本 QA 实测命令与环境

工作目录为 `automation-world/device-simulator`；macOS Darwin 24.6.0 arm64、rustc/cargo 1.89.0、Node v22.19.0、pnpm 11.11.0。无安装依赖。构建 target 复用 Development 已声明的该任务隔离根 `/private/tmp/ds003-dev.Zc2maS/target`，QA 测试 profile 与前端输出使用独立 `/private/tmp/ds003-qa-qrPhTm`。

| 命令 | 实测 |
| --- | --- |
| `DS_TEST_RUN_ROOT=/private/tmp/ds003-qa-qrPhTm/profiles CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test plc_catalog_export --test configuration_store --test source_import --test versions --test owner_contract` | exit 0；9 + 4 + 4 + 5 + 3 = 25 passed；owner 快照测试未启动协议 listener。 |
| `node --test tests/plc-catalog-export.test.mjs tests/point-display-names.test.mjs` | exit 0；33 passed，1 skipped（可选故障注入 fixture 未指定）；非原生 WebView/目录对话框。 |
| `pnpm exec vue-tsc --noEmit` | exit 0。 |
| `pnpm exec vite build --outDir /private/tmp/ds003-qa-qrPhTm/ui` | exit 0；存在依赖 PURE 标注与 >500 kB chunk 警告。 |
| `CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7` | exit 0。 |
| `CARGO_TARGET_DIR=/private/tmp/ds003-dev.Zc2maS/target cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7 --lib catalog_receipt_retains_partial_rows_and_reports_unknown` | exit 0；1 passed。 |
| `cargo fmt --manifest-path runtime/Cargo.toml --check`；`cargo fmt --manifest-path src-tauri/Cargo.toml --check` | 两项 exit 0。 |
| `git diff --check -- <tracked DS-003 candidate code/lock allowlist>` | exit 0；仅检查所列跟踪文件的工作树差异。 |
| Python stdlib 扫描 DS 受触达的中英文 README、USER_GUIDE、CODE_INDEX 及 runtime/tests README 的本地路径链接 | exit 0；105 个本地路径存在；仅检查路径，不检查所有 anchor 或外链。 |
| `git diff --no-index --check /dev/null plans/DS-003-plc-json-export/checklist.md` | exit 1 因为新文件与空文件不同；无 whitespace 诊断。 |
| `diff -u runtime/Cargo.lock /private/tmp/ds003-qa-qrPhTm/uuid-qa/Cargo.lock` | exit 1 表示有差异；人工确认仅新增临时 QA harness 包条目，无原有依赖版本变化。 |
| UUID 合成 harness `cargo run --offline --locked ...` | exit 0；成功重现 QA1-F01。`python3` 的 `uuid.UUID` 独立确认 NCS variant 非 v4。 |

本机 `python3` 没有 `tomllib`，一次尝试的锁文件结构比较 exit 1；随后用上述 `diff -u` 完成逐文本比较。未执行真实设备、FF/CA、Windows、VM、真实上报或生产部署。

## 资源、限制与 handoff

QA 未执行资源回收。`/private/tmp/ds003-qa-qrPhTm` 为本 QA 自有 harness、合成 profile、输出、失败构建中间文件和 UI build；失败复现主体与关键输出已写入本记录，协调者确认无进程或后续证据依赖后可回收。`/private/tmp/ds003-dev.Zc2maS` 是 Development 的共享隔离 target，本 QA 曾复用并新增编译产物；应等返修和后续验证不再使用后由协调者核对回收。最终实际 JSON `/private/tmp/ds003-final-json-RfE0TL/31d327ba-2b97-4f5e-8949-6956ac3a5648.json` 及较早 `/private/tmp/ds003-json-x7cWRU` 尚可能用于 DAA 和后续 QA，协调者确认依赖消失前保留；二者不是本 QA 创建。用户 `.local/dev` 的历史及 v3 来源仍需保留，QA 不清理。

QA1 返修对象：Development；返修后的精确候选须重新 handoff 并启动新的 fresh-context Verification。Human Owner 最终验收、发布、真实设备、外部上报和其他任务的 verdict 不由本结论授予。


# QA2：QA1-F01 返修后的独立验证（暂阻塞）

2026-11-17，Verification 在 Development 新 handoff 后以 fresh context 验证 `device-simulator::DS-003 r5`。本角色只更新本 checklist；按触达表面读取 `project-governance`、`aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`。项目角色 profile 为 `contract_only`；角色约定、串行交接、候选哈希及 diff 检查不是平台 ACL 或强制路由证明。

## QA2 verdict：qa_blocked

**QA1-F01 的修复已独立复现并通过有界回归；完整 r5 验收暂阻塞。** macOS 锁屏使协调者正在执行的**修复后候选**原生 DS→DAA 主线暂未取得完整证据。批准规格 DS01、DS08、DS09 和 §7 需要所选实例的实际原生导出文件及同文件互通；QA1 的真实导出/导入使用修复前候选，不能倒填为新候选的 GUI 证据。已有新引擎对旧真实文件的逐字节重建只证明相同输入时格式和内容未变，不是新原生导出或 DAA 采集。

协调者报告已通过两端正式入口重新编译并启动，DS 二进制 SHA-256 `44aa51f3049e31c5907662eb6abb97a277419a09f4cff235ec11036f98b8ea9f`，DAA 二进制 SHA-256 `3b4c538cb9663ca4c43b691a193ca0c89285d51b9cb986755885ce6073b68a85`，测试窗口二进制与其相同并已核对各自 dev 锁；以上是协调者报告，本 QA 未观察启动或原生 UI 操作。协调者已请求 Human Owner 解锁；待解锁后，在核对目标及安全边界的前提下完成新候选原生目录选择和输出、DAA 使用**该同一文件**的新建/分组/激活/loopback，并提供源 revision、实例、文件字节/SHA、接收及采集结果、同来源重复导入拒绝和任务对象清理证据。 协调者随后报告：本次修复后的同字节窗口 PID `9000`/`9018` 因锁屏没有 GUI 操作而已停止，Vite 已退出，`lsof` 显示两套 profile 锁及测试端口已释放；本轮未新增测试 PLC、连接或上报。本 QA 未亲自观察或验证这次进程收尾。Verification 再核对候选与锁文件身份、实际文件及来源，独立审查证据并如实判定；不能用本 QA 的 Rust 重建或旧候选原生结果替代。若界面操作、STRING/禁用点、双语或重复导入未实际覆盖，继续如实记录限制，不自动标通过。

## 输入身份、返修 diff 与 QA1-F01

- 工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`；批准 spec SHA-256 `9adf299af89711855be896938cf7e6148f4332e171a984aebf10dd32d7c6cd89`，本轮 Development tasks SHA-256 `3ca5fa8ff0c9257c461270b23b6f81b6f4abfd6ae1e26d3904871df7bdcebf3e`；写入前完整 QA1 checklist SHA-256 `d64ce1a93795a82b37907235a58eca00fd909708fb82bfa56e4840b3b7878c18`。写入前两次核验 Development 新冻结清单的 **29/29 文件哈希均匹配**；runtime lock `bdb170c99a5e863bfd7010032739c37bcbd19234de25c47da868b62c9b8bfaab`，desktop lock `39f14c514f35cb37ef1844f3e2f23153d737c8fb91a6c108feb3f6efbd244775`。
- 将原交接和新交接的 29 个完整文件身份对比，仅 `runtime/src/domain/plc_catalog.rs`（旧 `7554fc82bafda6c8c764a9f8065c1ea588d7721acaeb5327bb9f13b8c4220a4e`，新 `a916b1c6e660839bf701fc0d535bf630f5e9dd9a3a775036fc3d36abb3880985`）和 `runtime/tests/plc_catalog_export.rs`（旧 `8e3250dc28c7db8b8e67e18ed68d8dd325d524e7d34462ca65e6204166a0e0e1`，新 `e6bf66e981fa785ed212201b88c94d4c0fda2044bb6f4475df90d44acd8b87fc`）不同。移除新 validator 的 variant 条件并恢复原格式，得到旧文件的精确 SHA；截取新测试中追加 QA1 两项前的旧前缀，得到精确旧 SHA。共享文件及其他脏改动不全归因本任务。
- 在自有临时副本中使用上述**精确还原旧 validator**及 QA1 本记录已保存的完整 harness，实际保存/发布带 enabled NCS 点 `55555555-5555-4555-0555-555555555555` 的合成版本；原 validator 的配置验证 `Ok(())`、`preview_issues=[]`、`committed=true`、`result=written`，文件仍包含该无效点 ID。最后一次 `--locked` 重放输出 SHA-256 `fc7c44d6aeeea1030fc2e1d6a56e2574108c19863195c28655508e0cd9c66554`（包含该次生成时间，非 QA1 原文件）。Python `uuid.UUID` 独立确认该 ID 为 NCS variant、version `None`，`...-8555-...` 为 RFC 4122 variant、version 4。
- 在**正式工作树修复后引擎**用下方独立 harness 重放相同 enabled 点及实际保存/发布/预览/目录绑定/提交：配置仍可保存，但预览 `document=null`，返回 `catalog_identity` 且准确带 DB 和点 ID；提交 `result=failed`、`committed=false`，目标文件不存在。再运行交付测试，验证保存的 disabled NCS 点只阻断其所属实例、另一合法实例仍写出；profile、revision、PLC、DB、点 ID 还覆盖 RFC variant 首位 8/9/a/b、NCS/Microsoft/future、错误版本、大小写及非规范形式。QA1 原失败及其实际写出证据保持在上文。

### 旧真实文件的新引擎回归（不是新原生操作）

在协调者启动新一轮应用前，本 QA 检查 DS `.local/dev/device-simulator-v1/config.sqlite` 无 WAL/SHM，仅用 SQLite `mode=ro&immutable=1` 读取 v3 revision `3d50439c-fb2b-41bd-9d95-56c67cd98672` 的原始 payload 及记录摘要；其计算 SHA、数据库记录 SHA 和旧文件 `export.payload_sha256` 都是 `06dc1f3d5c2440fb66dc8af63de92c50ee4bf095e22c6280efd70e2ff60b976b`。旧文件实例 `31d327ba-2b97-4f5e-8949-6956ac3a5648`，2407 bytes，SHA `0268a8098bb36c4b3bdc3f89141ef31123c56fb34ba47e33e275cd87a378e9a6`；1 DB、4 点，覆盖 BOOL/INT/REAL 和停用 BOOL，不含 STRING。

把该 payload、profile、revision、实例、目标和**原文件记录的时间**交给当前 `plc_catalog::build`，每个 JSON 字段相等，pretty serialization 逐字节相等，SHA 仍是 `0268a8098bb36c4b3bdc3f89141ef31123c56fb34ba47e33e275cd87a378e9a6`。这里复用旧时间仅用于可重复比较，未生成或声称新的原生文件；不能证明语言切换、原生选择器、DAA 接收或采集。随后本 QA 未再访问该 `.local/dev`。

## 验收矩阵的本轮证据边界

| 项 | QA2 结果与仍未证明的内容 |
| --- | --- |
| DS01 | 部分：旧实际文件与 revision 的摘要及新引擎重建已核对；修复后候选的原生选择和导出待证。 |
| DS02 | 部分：QA1-F01 已关闭；合成测试覆盖 STRING 和禁用 DB/点，旧实际文件含 BOOL/INT/REAL/禁用 BOOL；尚无修复后候选的原生完整文件。 |
| DS03 | 部分：新旧候选的 NCS 真正提交行为已复现；两实例隔离和各身份变体测试通过。其余负例以已运行合成覆盖范围为限，不宣称穷举；损坏到不可读取的整个 revision 会在逐实例诊断前拒绝。 |
| DS04 | 部分：合成测试覆盖非法目标、端点数值、loaded 差异及非默认 TSAP；未独立做原生负值/空值输入。 |
| DS05 | 部分：合成测试覆盖已有和迟到目标、符号链接、目录替换、重复提交；写错 errno 分类与桥接未知回执单测通过。未独立穷举只读目录及提交瞬间系统竞争；Development 在 tasks 记录的同用户临时名竞争和目录移动可能导致未知结果仍保留，不宣称完整系统隔离。 |
| DS06 | 部分：合成测试核对选定 payload、草稿及版本删除；本 QA 对 `.local/dev` 仅做所述事后只读检查，没有本 QA 自身的真实 profile 前后操作对照。 |
| DS07 | 部分：Node 测试检查中英文键对称与预览组件行为；非原生 WebView，修复后候选的双语界面未由本 QA 亲自操作。 |
| DS08 | 部分：store、source、version、owner 回归和 native-s7 编译检查通过；修复后候选 macOS 原生对话框及落盘待证；Windows/VM 不在本轮。 |
| DS09 | 阻塞：旧同文件互通为修复前候选的协调者观察，不能冒充新候选；实际同来源重复导入拒绝也待证。 |
| DS10 | 已执行本轮正式源码/锁的 Rust、Node、typecheck、build、native-s7 bridge、格式和 scoped diff 检查，见下；通过这些命令不代替其他验收项。 |
| DS11 | 部分：合成测试覆盖旧单条值、双语、独立描述、停用点和 STRING；新候选的旧 revision 原生操作及语言切换前后文件 SHA 未独立观察。 |
| DS12 | 部分：本 QA 不操作真实 profile；本轮协调者执行的目标核对与清理须在其操作结束后提供独立可核对结果。 |
| DS13 | 中英文 USER_GUIDE 的 §7 流程已复核；受触达的 105 个相对路径链接均存在。此检查不证明原生步骤已经执行。 |

## 实测命令与环境

macOS Darwin 24.6.0 arm64；`rustc 1.89.0` / `cargo 1.89.0`，Node `v22.19.0`，pnpm `11.11.0`。命令在正式 `automation-world/device-simulator` 目录执行；无依赖安装；本 QA 自有隔离根 `/private/tmp/ds003-qa2-Ggidgy`。以下 `R=/private/tmp/ds003-qa2-Ggidgy` 为该固定目录的简写。

| 命令 | 观察结果 |
| --- | --- |
| `DS_TEST_RUN_ROOT=$R/profiles CARGO_TARGET_DIR=$R/target cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test plc_catalog_export --test configuration_store --test source_import --test versions --test owner_contract` | exit 0，11 + 4 + 4 + 5 + 3 = 27 passed；合成 profile；owner 快照不启动协议 listener。 |
| `CARGO_TARGET_DIR=$R/target-old cargo run --offline --locked --manifest-path $R/repro/Cargo.toml` | exit 0；旧 validator 真实写出 NCS 点，见上。首次生成独立 harness lock 时未加 `--locked`，随后改用新的自有 profile/目录执行此锁定重放。 |
| `QA_REPLAY_ROOT=$R/replay-two CARGO_TARGET_DIR=$R/target cargo run --offline --locked --manifest-path $R/new-harness/Cargo.toml` | exit 0；修复后真实 service 定位错误、拒绝提交且无目标文件。 |
| `CARGO_TARGET_DIR=$R/target cargo run --offline --locked --manifest-path $R/actual-regression/Cargo.toml` | exit 0；旧实际文件与新引擎生成的 Value 及 2407 字节逐字节相等。 |
| `diff -u runtime/Cargo.lock $R/repro/Cargo.lock`；`diff -u runtime/Cargo.lock $R/new-harness/Cargo.lock`；`diff -u runtime/Cargo.lock $R/actual-regression/Cargo.lock` | 每个 exit 1 表示差异；人工检查仅各自新增临时 harness 包条目，原依赖版本不变。三个临时 lock 初次均由正式 runtime lock 复制，再由离线 Cargo 添加自身包；项目 lock 未改。 |
| `CARGO_TARGET_DIR=$R/target cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7` | exit 0；检查正式桌面 target/插件，不代表打开原生窗口。 |
| `CARGO_TARGET_DIR=$R/target cargo test --manifest-path runtime/Cargo.toml --locked --offline --lib exclusive_link_distinguishes_conflict_from_other_write_errors` | exit 0；1 passed。 |
| `CARGO_TARGET_DIR=$R/target cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7 --lib catalog_receipt_retains_partial_rows_and_reports_unknown` | exit 0；1 passed。 |
| `node --test tests/plc-catalog-export.test.mjs tests/point-display-names.test.mjs` | exit 0；33 passed、1 skipped（可选故障 fixture 未指定），不是原生 WebView。 |
| `pnpm exec vue-tsc --noEmit`；`pnpm exec vite build --outDir $R/ui` | 两者 exit 0；Vite 给出现有 PURE 标注和大于 500 kB chunk 警告。 |
| `cargo fmt --manifest-path runtime/Cargo.toml --check`；`cargo fmt --manifest-path src-tauri/Cargo.toml --check` | 两者 exit 0。 |
| `git diff --check -- runtime/src/app.rs runtime/src/domain/mod.rs runtime/src/services/mod.rs runtime/src/infrastructure/config_store/mod.rs runtime/src/infrastructure/config_store/queries.rs src-tauri/Cargo.toml src-tauri/Cargo.lock src-tauri/src/lib.rs src-tauri/src/commands/mod.rs src/services/deviceSimulator.ts src/app/simulator/views/instances/index.vue src/app/simulator/locales/en-US.json src/app/simulator/locales/zh-CN.json src/styles/app.css README.md README.zh-CN.md USER_GUIDE.md USER_GUIDE.zh-CN.md CODE_INDEX.md runtime/README.md runtime/README.zh-CN.md tests/README.md tests/README.zh-CN.md` | exit 0。新增 `runtime/src/domain/plc_catalog.rs`、`runtime/src/services/catalog_export.rs`、`runtime/tests/plc_catalog_export.rs`、`src-tauri/src/commands/catalog_export.rs`、`src/app/simulator/components/CatalogExportDialog.vue` 和 `tests/plc-catalog-export.test.mjs` 逐个以 `git diff --no-index --check /dev/null <file>` 检查：各 exit 1 因与空文件不同，无 whitespace diagnostics。 |
| Python stdlib 相对 Markdown 路径检查 | exit 0；受触达的 105 个本地路径存在；未检查所有 anchor 或外链。 |

### 独立修复后重放 harness（持久化测试主体）

临时 Cargo 项目的 `ds-runtime` path 指向正式 DS `runtime`，`serde_json = "=1.0.150"`，`QA_REPLAY_ROOT` 必须指向新的自有临时目录；不读取用户 profile 或连接设备：

```rust
use ds_runtime::{app::App,domain::{configuration::{self,Workspace},layout,plc_catalog::Target},services::catalog_export::{self,PreviewIntent,TokenIntent}};
use std::path::PathBuf;
fn main() {
 let invalid="55555555-5555-4555-0555-555555555555";
 let mut w:Workspace=serde_json::from_str(r#"{"schemaVersion":1,"instances":[{"id":"11111111-1111-4111-8111-111111111111","name":"Synthetic","port":32194,"dbs":[{"id":"22222222-2222-4222-8222-222222222222","name":"DB","number":21,"length":2,"manual":true,"enabled":true,"points":[{"id":"55555555-5555-4555-0555-555555555555","name":"Count","dataType":"INT","byte":0,"manual":true,"enabled":true}]}]}]}"#).unwrap();
 for i in &mut w.instances { for d in &mut i.dbs {d.address_confirmation=Some(configuration::AddressConfirmation{structure_sha256:layout::structure_signature(d),layout_sha256:layout::layout_signature(d),method:"manual".into(),reason:"synthetic QA".into()});} i.names_confirmation=Some(layout::names_signature(i));}
 assert!(configuration::validate(&w).is_ok());
 let root=PathBuf::from(std::env::var("QA_REPLAY_ROOT").unwrap());let app=App::open(&root.join("profile")).unwrap();
 let d=app.configuration.store.load().unwrap();let s=app.configuration.store.save(&d.etag,w.clone()).unwrap();let rev=app.configuration.store.publish(&s.etag).unwrap().revision_id.unwrap();
 let target=Target{instance_id:w.instances[0].id.clone(),host:"127.0.0.1".into(),port:32194,rack:0,slot:1,connection_confirmed:true,loaded_difference_confirmed:true};
 let v=catalog_export::preview(&app,PreviewIntent{revision_id:rev,targets:vec![target]}).unwrap();
 assert!(v["rows"][0]["document"].is_null());
 assert!(v["rows"][0]["issues"].as_array().unwrap().iter().any(|i|i["code"]=="catalog_identity" && i["pointId"]==invalid && i["dbId"]==w.instances[0].dbs[0].id));
 let token=v["token"].as_str().unwrap();let dir=root.join("output");std::fs::create_dir_all(&dir).unwrap();catalog_export::choose_directory(&app,token,&dir).unwrap();
 let receipt=catalog_export::commit(&app,TokenIntent{token:token.into()}).unwrap();
 assert_eq!(receipt["rows"][0]["result"],"failed");assert_eq!(receipt["committed"],false);assert!(!dir.join(format!("{}.json",w.instances[0].id)).exists());
 println!("preview_document_null={} issues={} receipt={} no_file=true",v["rows"][0]["document"].is_null(),v["rows"][0]["issues"],receipt);assert!(app.shutdown());
}
```

### 旧真实文件的新引擎重建主体

该只读比较依赖仍保留的旧文件及相应 v3 原始 payload；payload 须以只读 SQLite 查询指定 revision、校验 stored SHA 后复制至自有临时目录。比较时复用原导出时间，不得将结果解释为新原生导出：

```rust
use ds_runtime::domain::{configuration::{hash_bytes, Workspace}, plc_catalog::{self, Target}};
use serde_json::Value;
use std::fs;
fn main() {
 let old_file = "/private/tmp/ds003-final-json-RfE0TL/31d327ba-2b97-4f5e-8949-6956ac3a5648.json";
 let original = fs::read(old_file).unwrap();
 let old: Value = serde_json::from_slice(&original).unwrap();
 let payload = fs::read("/private/tmp/ds003-qa2-Ggidgy/v3-payload.json").unwrap();
 assert_eq!(hash_bytes(&payload), old["export"]["payload_sha256"]);
 let workspace: Workspace = serde_json::from_slice(&payload).unwrap();
 let plc_id=old["origin"]["plc_id"].as_str().unwrap();
 let instance=workspace.instances.iter().find(|i| i.id == plc_id).unwrap();
 let conn=&old["plc"]["connection"];
 let target=Target {instance_id:plc_id.into(), host:conn["host"].as_str().unwrap().into(), port:conn["port"].as_u64().unwrap() as u32, rack:conn["rack"].as_u64().unwrap() as u32, slot:conn["slot"].as_u64().unwrap() as u32, connection_confirmed:true, loaded_difference_confirmed:true};
 let doc=plc_catalog::build(&workspace,instance,old["export"]["profile_id"].as_str().unwrap(),old["export"]["revision_id"].as_str().unwrap(),&payload,old["export"]["exported_at"].as_str().unwrap(),&target).expect("current engine must accept real saved revision");
 assert_eq!(doc,old,"same source, target and timestamp must match every field");
 let bytes=serde_json::to_vec_pretty(&doc).unwrap();
 assert_eq!(bytes,original,"same serde serialization must reproduce exact previous file bytes");
 println!("current_engine_same_fields_and_bytes=true bytes={} sha256={} revision={} instance={}",bytes.len(),hash_bytes(&bytes),old["export"]["revision_id"],plc_id);
 println!("payload_sha256={} dbs={} points={}",hash_bytes(&payload),old["dbs"].as_array().unwrap().len(),old["dbs"].as_array().unwrap().iter().map(|d| d["points"].as_array().unwrap().len()).sum::<usize>());
}
```

## 资源、限制与 handoff

本 QA 未回收资源。`/private/tmp/ds003-qa2-Ggidgy` 为本 QA 创建，含合成 profile、旧候选临时源码副本及结果、临时 harness/locks、隔离 Cargo targets、前端产物和一份仅读取的 v3 payload 副本；不得把其当成唯一持久证据。上述代码、输入身份及关键结果已写入本记录。协调者在后续验证和 Human Owner gate 均不再依赖其内容、确认无进程占用且确认为本 QA 所有后按 workflow 安全回收；包含 profile 内容的临时副本不应长期保留。其他 QA/Development 资源、两端 `.local/dev`、用户历史和旧实际 JSON 不归本 QA 清理。

本轮仅测试自有合成目录、只读旧 DS 数据，未亲自启动 GUI/网络 listener，也未操作真实 PLC、生产数据库、外部上报、FF/CA、Windows 或 VM。解锁与新候选原生证据完成后交回 Verification；当前结论为 `qa_blocked`，不授予 Human Owner 最终验收或其他任务通过。


# QA2 解锁后接续：原生补证及剩余阻塞

2026-11-17（Asia/Shanghai），用户解锁后，同一 fresh-context Verification 接续相同 DS-003 r5 handoff；本次只读文件、三座本机 SQLite 和二进制，仅写本 checklist。**原锁屏 `qa_blocked` 历史及 QA1 保持上文原样。**原生主线所需文件和本地样本现已取得；QA2 当前仍为 **`qa_blocked`**，剩余原因收窄为下述 DS11 的 SHA 比较口径，非原锁屏。

## 结论与 DS11 的精确问题

协调者报告在修复后候选的中文和英文原生导出界面分别选择同一 v4 测试实例、确认目标和 loaded 差异并预览四点；英文界面还实际操作原生目录取消、冲突目录及新目录导出。取消后原预览 SHA 保持且导出按钮禁用；选择已有中文文件目录时提示已存在、禁止覆盖并要求换目录，导出按钮禁用；原文件未变。协调者说明预览 modal 遮住顶栏，AX 树也只暴露 modal 控件，因此**没有**在保持同一原生预览打开时切换顶栏语言；本 QA 未亲见这些 GUI 操作。

本 QA 独立读取两份实际文件并比较：中文文件 SHA-256 `5198f7fef382f9524b81c66275b76cbdb779deb7741df16d3005f809bf6662e3`，`exported_at=2026-11-17T20:36:08.720+08:00`；英文文件 SHA-256 `74686eaa257c3a5590dfef4425124bafbf9d3fd162581f3ebdf27b57c8b79d59`，`exported_at=2026-11-17T20:50:47.731+08:00`；两者均 2387 bytes，**除各自真实生成时间字段之外，所有 JSON 字段相等**，来源 payload SHA 相同。源代码每次新预览生成时间并将其写入文件。另以真实 Vue 组件脚本、真实双语 locale、模拟 IPC 在内存切换语言，同一 preview 对象、选择、token 和预览文件 SHA 保持不变；这是非原生组件测试，不能说原生同预览切换已发生。

DS11 写的是“语言切换不改变数据或 SHA”，但 §3 同时要求 `exported_at` 是真实生成时间；在本原生可操作路径中需要先关闭 preview 才能切换顶栏语言，再生成新 preview，所得两份文件由于时间不同而 SHA 不同。上述结果证明两份文件的**其他**数据与来源 SHA 相同，不证明跨生成时刻的完整文件 SHA 相同，也不能单凭两个不同时间判断语言本身改变了文件。请 PM 澄清 DS11 的比较对象是来源 payload SHA、同一已生成 preview SHA，还是不同生成时刻的完整导出文件 SHA，并判断是否构成验收范围实质变化而需新 Revision/Owner 批准。Verification 不自行改写 spec 或以未发生的同预览原生操作填补。澄清后对精确候选接续判定；Human Owner 最终验收仍另行决定。

## 实际文件、来源和跨应用事实

- 原生中文文件 `/private/tmp/ds003-qa2-json-dCWNwR/e1dc3ad5-305f-4367-af1b-92333a582730.json`，英文文件 `/private/tmp/ds003-qa2-en-hFbT6k/e1dc3ad5-305f-4367-af1b-92333a582730.json`。DS 工作树 debug 二进制和协调者临时 .app 的可执行文件均实测 SHA `44aa51f3049e31c5907662eb6abb97a277419a09f4cff235ec11036f98b8ea9f`；DAA 二者均实测 `3b4c538cb9663ca4c43b691a193ca0c89285d51b9cb986755885ce6073b68a85`。同字节证明可执行文件一致，不把临时 .app GUI 操作称为本 QA 亲自操作，也不推定完整普通入口 UI 已独立复现。
- 本 QA 先确认三个 SQLite 路径均无 `-wal`、`-shm`、`-journal`，再以 `file:...?...mode=ro&immutable=1` 只读。DS revision `b4fd38fa-0d2a-48e6-b83b-fb16d2da35c8` 是 saved sequence v4；存储 payload、实时计算及文件声明 SHA 均为 `20c8882a2f5e1e902ae32896043e773370f3e24972a863cc731a279c6ed3345d`；profile、PLC `e1dc3ad5-305f-4367-af1b-92333a582730` 和 loopback `127.0.0.1:31976` 一致。对照该实例的 1 DB、4 点，ID、程序名、DB 号/长度、类型、byte/bit、各层 enabled、双语、独立描述、旧单条值缺省及 source path 均一致。文件为 UTF-8 无 BOM；独立解析检查重复 key、canonical RFC v4 身份；本例不含规则或实时值。BOOL、INT、REAL 已启用，`STRING[10]` 停用。
- DAA `source_documents` 的测试 source `f0f54d04-cc0e-47cb-80c9-03465b0126fe` 保存的内容与**中文实际文件原始 2387 字节完全一致**，SHA 同为 `5198f7fe…`。采样时 configuration context `9acbff9e-0539-4b91-b397-a6d7cf1a1368` 的原文 SHA `9cd6aa61e77ac627b905a0cebc382db0950ba7dedda38db546149b19cbeb273f` 校验通过；同一 source、DB binding、4 对 catalog/local 点 ID 以及双语值与原文件一致。
- 独立查询该 PLC 的 11 个 collection cycles / 11 个 samples，均为 `good`；每个 sample 原始 payload SHA 正确，11 × 3 个事实的 ID、程序名、类型、DB21 地址和质量均与文件一致，值分别为 BOOL `false`（0.0）、INT `0`（2）、REAL `0.0`（4）；停用 STRING 点不在这些样本中。11 个 `reporting_cycles` 均为全 null 的 local-only 身份，该 PLC 的 `sample_uploads=0`。协调者报告当时只连接该 loopback、自动/实际上报停止、其界面原待发送 5/已确认 69 未变；本 QA 只直接核对上述持久记录，未亲见连接或上报 UI，也不声称所有数据库零写。
- 协调者报告 DAA 导入前 4 点初始停用，第二次选择同一文件出现“PLC 端点重复”，确认按钮禁用；该次实际 UI 拒绝由 endpoint 校验先触发，不能误写成原生界面曾显示 origin 冲突。源码还对 identity/source 冲突 fail closed，相关合成测试见 DAA 自身记录；本 DS verdict 不替代 DAA-017 的独立 QA。
- 清理后，DS 当前草稿与原 saved v1 经 JSON 对象比较完全相同，原实例仍有其 v1 selection；DAA 当前 draft、active payload 与联测前 active revision `423e612e-291c-45d0-b171-557126ee4ad5` 对象相同，后两版本内容 SHA 均 `4b5f702b35a52ee90719a2d32795d96613600441bfbdf881bcef27fcdefee622`。这不表示删除测试历史：DS v4、DAA context、来源和 11 条样本仍是可追溯历史。协调者报告测试实例经 UI 移除并停止测试应用；进程/端口占用应以最终核对结果为准。

## 本轮补充隔离检查

此前 29 个候选文件、两锁和原有测试结果仍按上文 QA2 记录。本次在正式 Rust runtime、锁依赖及自有 `/private/tmp/ds003-qa2-Ggidgy` 下进一步检查：

- `CARGO_TARGET_DIR=/private/tmp/ds003-qa2-Ggidgy/target cargo run --offline --locked --manifest-path /private/tmp/ds003-qa2-Ggidgy/contract-harness/Cargo.toml`：exit 0。16 类直接 domain 负例包括重复点 ID、DB/点跨类 ID、点名、DB ID/编号、未知类型、`STRING[0]`、BOOL bit、禁用点重叠/越界、不可核实来源、文本字节上限、DB/点数上限、未确认命名/布局；各返回预期错误和适用的 DB/点定位，另一合法实例仍可独立 build。该项为内存 domain 测试；保存版本的逐实例提交和 NCS 行为见上文 service 回归。非整数 `byte` 在 workspace 反序列化时拒绝整个损坏 revision，不声称可从不可读版本逐点恢复。
- `QA_FS_ROOT=/private/tmp/ds003-qa2-Ggidgy/fs-run2 CARGO_TARGET_DIR=/private/tmp/ds003-qa2-Ggidgy/target cargo run --offline --locked --manifest-path /private/tmp/ds003-qa2-Ggidgy/fs-harness/Cargo.toml`：exit 0。真实同名目录被拒绝并保留原 inode；service cancel 不写；将自有输出目录设为 `0500` 后提交失败且无目标/临时文件；在测试进程中暂设 `RLIMIT_FSIZE=0` 注入真实写入失败，返回 `catalog_write`，不留目标/临时文件。原生取消及同名文件冲突另有上述协调者观察；不宣称已证明所有同用户对抗竞争或电源故障。
- 两个 harness 首次均从正式 `runtime/Cargo.lock` 复制再离线生成自身条目，`diff -u runtime/Cargo.lock <harness>/Cargo.lock` 各 exit 1；仅新增各自测试包条目，原依赖版本不变；项目锁未改。测试主体保留如下。
- `node --test /private/tmp/ds003-qa2-Ggidgy/i18n-preview-test.mjs`：exit 0，5 passed；在现有 DS 组件测试宿主中附加上述 locale 切换状态断言，IPC 为模拟，render 仍为测试替身，不是原生 WebView。
- `shasum -a 256` 对正式 DS/DAA debug 二进制、两个对应临时 .app 可执行文件和两份实际 JSON 逐个校验；值如上。Python stdlib 使用只读 SQLite、`hashlib`、`json`、`uuid` 核对上述 payload、文件、绑定、全部 11 条样本及清理后配置；不写业务 profile。核对时无 WAL/SHM/journal。`lsof -nP -iTCP:15191 -iTCP:15194 -iTCP:31976` 在英文复验后曾显示 PID 18355 的 node 监听 15191；已交协调者核查，不能提前写成全部已释放。

### 当前验收项归纳

| 项 | 本轮证据与限制 |
| --- | --- |
| DS01 | 中文及英文原生 v4 实例选择/预览为协调者观察；本 QA 独立核对源版本、实例、摘要和文件。loaded 差异提示另有合成测试。 |
| DS02 | 实际同一文件覆盖 BOOL、INT、REAL、STRING 和停用点，全部字段与 v4 对照；UUID 和严格解析有独立检查。 |
| DS03 | 上述 16 类 domain 负例、NCS 保存/提交复现及合法另一实例覆盖；损坏到无法反序列化的整个 revision 的限制如实保留。 |
| DS04 | invalid host/数值、loaded 确认、非默认 TSAP 由先前合成测试验证；原生极端数值输入未观察。 |
| DS05 | 协调者观察原生选择取消及已有文件冲突；合成和实际隔离文件系统故障覆盖已有文件/目录/链接、迟到目标、替换、重复、只读和写错。系统级对抗竞争仍非已证明事实。 |
| DS06 | 合成 profile 的 payload/草稿/选择及删除竞争回归通过；两端实际业务配置的清理后结果只读对照。该事实不等同于原生操作全过程由 QA 亲见或数据库没有历史写入。 |
| DS07 | 协调者分别操作了中文和英文原生入口、实例选择及预览；本 QA 未亲见。实际语言不能在同一 modal 预览内通过顶栏切换。 |
| DS08 | 编译、版本/配置回归、同字节原生窗口和真实落盘有上述证据；GUI 为协调者观察，Windows/VM 不在范围。 |
| DS09 | 实际 DS 文件在 DAA 的原始字节、来源、绑定和 11 轮 local-only 样本已独立只读核对；同文件再次导入的 UI 拒绝为协调者观察，错误为 duplicate endpoint。 |
| DS10 | 前述正式工作树 Rust/Node/type/build/bridge 和本轮定向合成检查通过；候选/锁最终身份仍需在 handoff 前复核。 |
| DS11 | 旧值、单侧空/两侧非空、描述及停用点有合成与实际数据证据；来源 SHA 及除真实生成时间外字段一致，同预览的内存状态测试通过；**不同生成时刻文件 SHA 不同，比较口径待 PM 澄清**。 |
| DS12 | 两端配置清理结果已只读核对；实际启动/连接/停止为协调者操作，未触及真实设备或外部上报的判断按其观察和本 QA 持久记录边界报告。 |
| DS13 | 双语手册和受触达本地链接检查如上文。 |

### Domain 负例 harness

```rust
use ds_runtime::domain::{configuration::{self,Workspace},layout,plc_catalog::{self,Target}};
use serde_json::json;
fn main(){
 let mut base:Workspace=serde_json::from_value(json!({"schemaVersion":1,"instances":[
 {"id":"11111111-1111-4111-8111-111111111111","name":"A","port":32194,"dbs":[{"id":"22222222-2222-4222-8222-222222222222","name":"DBA","number":21,"length":8,"manual":true,"enabled":true,"points":[{"id":"33333333-3333-4333-8333-333333333333","name":"Flag","dataType":"BOOL","byte":0,"bit":0,"manual":true,"enabled":true},{"id":"44444444-4444-4444-8444-444444444444","name":"Count","dataType":"INT","byte":2,"manual":true,"enabled":true}]}]},
 {"id":"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa","name":"B","port":32195,"dbs":[{"id":"bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb","name":"DBB","number":22,"length":4,"manual":true,"points":[{"id":"cccccccc-cccc-4ccc-8ccc-cccccccccccc","name":"Other","dataType":"INT","byte":0,"manual":true}]}]}
 ]})).unwrap();
 fn confirm(w:&mut Workspace){for i in &mut w.instances{for d in &mut i.dbs{d.address_confirmation=Some(configuration::AddressConfirmation{structure_sha256:layout::structure_signature(d),layout_sha256:layout::layout_signature(d),method:"manual".into(),reason:"synthetic test".into()});}i.names_confirmation=Some(layout::names_signature(i));}}
 fn check(w:&Workspace,n:usize)->Result<serde_json::Value,Vec<plc_catalog::Issue>>{let i=&w.instances[n];let t=Target{instance_id:i.id.clone(),host:"127.0.0.1".into(),port:i.port as u32,rack:0,slot:1,connection_confirmed:true,loaded_difference_confirmed:true};let payload=serde_json::to_vec(w).unwrap();plc_catalog::build(w,i,"eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee","ffffffff-ffff-4fff-8fff-ffffffffffff",&payload,"2026-11-17T09:00:00+08:00",&t)}
 confirm(&mut base);assert!(check(&base,0).is_ok()&&check(&base,1).is_ok());
 let cases=["duplicate_point_id","duplicate_cross_db_point_id","duplicate_name","duplicate_db_id","duplicate_db_number","unknown_type","string_zero","bad_bool_bit","overlap_disabled","out_of_range_disabled","bad_source","text_bytes","too_many_db","too_many_points","unconfirmed_names","unconfirmed_layout"];
 for case in cases {
  let mut w=base.clone();
  match case {
   "duplicate_point_id"=>w.instances[0].dbs[0].points[1].id=w.instances[0].dbs[0].points[0].id.clone(),
   "duplicate_cross_db_point_id"=>w.instances[0].dbs[0].points[1].id=w.instances[0].dbs[0].id.clone(),
   "duplicate_name"=>w.instances[0].dbs[0].points[1].name=w.instances[0].dbs[0].points[0].name.clone(),
   "duplicate_db_id"|"duplicate_db_number"=>{let mut d=w.instances[0].dbs[0].clone();d.id=if case=="duplicate_db_id"{d.id}else{"dddddddd-dddd-4ddd-8ddd-dddddddddddd".into()};d.number=if case=="duplicate_db_id"{24}else{d.number};d.points[0].id="99999999-9999-4999-8999-999999999999".into();d.points[0].name="AnotherFlag".into();d.points[1].id="88888888-8888-4888-8888-888888888888".into();d.points[1].name="AnotherCount".into();w.instances[0].dbs.push(d);},
   "unknown_type"=>w.instances[0].dbs[0].points[1].data_type="REAL64".into(),
   "string_zero"=>w.instances[0].dbs[0].points[1].data_type="STRING[0]".into(),
   "bad_bool_bit"=>w.instances[0].dbs[0].points[0].bit=Some(8),
   "overlap_disabled"=>{w.instances[0].dbs[0].points[1].byte=Some(0);w.instances[0].dbs[0].points[1].enabled=false;},
   "out_of_range_disabled"=>{w.instances[0].dbs[0].points[1].byte=Some(8);w.instances[0].dbs[0].points[1].enabled=false;},
   "bad_source"=>w.instances[0].dbs[0].manual=false,
   "text_bytes"=>w.instances[0].dbs[0].points[1].description=Some("测".repeat(167)),
   "too_many_db"=>{let d=w.instances[0].dbs[0].clone();w.instances[0].dbs=vec![d;33];},
   "too_many_points"=>{let p=w.instances[0].dbs[0].points[0].clone();w.instances[0].dbs[0].points=vec![p;4097];},
   "unconfirmed_names"|"unconfirmed_layout"=>{},_=>unreachable!()
  }
  confirm(&mut w);
  if case=="unconfirmed_names"{w.instances[0].names_confirmation=None;}
  if case=="unconfirmed_layout"{w.instances[0].dbs[0].address_confirmation=None;}
  let code=match case{"duplicate_point_id"|"duplicate_cross_db_point_id"=>"catalog_identity","duplicate_name"=>"catalog_point_name","duplicate_db_id"|"duplicate_db_number"=>"catalog_db_invalid","unknown_type"|"string_zero"=>"catalog_type","bad_bool_bit"|"out_of_range_disabled"=>"catalog_address","overlap_disabled"=>"catalog_overlap","bad_source"=>"catalog_source_unverified","text_bytes"=>"catalog_text_limit","too_many_db"|"too_many_points"=>"catalog_capacity","unconfirmed_names"=>"catalog_names_unconfirmed","unconfirmed_layout"=>"catalog_layout_unconfirmed",_=>unreachable!()};
  let issues=check(&w,0).unwrap_err();assert!(issues.iter().any(|v|v.code==code),"{case}: {issues:?}");if !["too_many_db","too_many_points","unconfirmed_names"].contains(&case){assert!(issues.iter().any(|v|v.code==code && v.db_id.is_some()),"missing DB location: {case}");}if ["duplicate_point_id","duplicate_cross_db_point_id","duplicate_name","unknown_type","string_zero","bad_bool_bit","overlap_disabled","out_of_range_disabled","text_bytes"].contains(&case){assert!(issues.iter().any(|v|v.code==code && v.point_id.is_some()),"missing point location: {case}");}assert!(check(&w,1).is_ok(),"valid separate instance blocked in {case}");println!("{case}={code}; separate_valid_instance=ok");
 }
 let mut value=serde_json::to_value(&base).unwrap();value["instances"][0]["dbs"][0]["points"][0]["byte"]=json!(1.5);assert!(serde_json::from_value::<Workspace>(value).is_err());println!("noninteger_byte=entire_revision_decode_rejected");
}
```

### 自有目录故障 harness

```rust
use ds_runtime::{app::App,domain::{configuration::{self,Workspace},layout,plc_catalog::Target},services::catalog_export::{self,PreviewIntent,TokenIntent}};
use std::{fs,path::PathBuf,os::unix::fs::{MetadataExt,PermissionsExt}};
fn preview(app:&App,rev:&str,id:&str)->String {
 let t=Target{instance_id:id.into(),host:"127.0.0.1".into(),port:32194,rack:0,slot:1,connection_confirmed:true,loaded_difference_confirmed:true};
 let p=catalog_export::preview(app,PreviewIntent{revision_id:rev.into(),targets:vec![t]}).unwrap();assert_eq!(p["rows"][0]["issues"].as_array().unwrap().len(),0);p["token"].as_str().unwrap().into()
}
fn main(){
 let root=PathBuf::from(std::env::var("QA_FS_ROOT").unwrap());let app=App::open(&root.join("profile")).unwrap();
 let mut w:Workspace=serde_json::from_str(r#"{"schemaVersion":1,"instances":[{"id":"11111111-1111-4111-8111-111111111111","name":"Synthetic","port":32194,"dbs":[{"id":"22222222-2222-4222-8222-222222222222","name":"DB","number":21,"length":2,"manual":true,"enabled":true,"points":[{"id":"55555555-5555-4555-8555-555555555555","name":"Count","dataType":"INT","byte":0,"manual":true,"enabled":true}]}]}]}"#).unwrap();
 for i in &mut w.instances {for d in &mut i.dbs {d.address_confirmation=Some(configuration::AddressConfirmation{structure_sha256:layout::structure_signature(d),layout_sha256:layout::layout_signature(d),method:"manual".into(),reason:"synthetic QA".into()});}i.names_confirmation=Some(layout::names_signature(i));}
 let id=w.instances[0].id.clone();let d=app.configuration.store.load().unwrap();let s=app.configuration.store.save(&d.etag,w).unwrap();let rev=app.configuration.store.publish(&s.etag).unwrap().revision_id.unwrap();
 let dir=root.join("out");fs::create_dir(&dir).unwrap();let dest=dir.join(format!("{id}.json"));
 fs::create_dir(&dest).unwrap();let inode=fs::metadata(&dest).unwrap().ino();let t=preview(&app,&rev,&id);let q=catalog_export::choose_directory(&app,&t,&dir).unwrap();assert_eq!(q["rows"][0]["conflict"],true);let r=catalog_export::commit(&app,TokenIntent{token:t}).unwrap();assert_eq!(r["rows"][0]["errorCode"],"catalog_target_exists");assert_eq!(fs::metadata(&dest).unwrap().ino(),inode);assert!(dest.is_dir());fs::remove_dir(&dest).unwrap();println!("directory_target=refused existing_directory_unchanged=true");
 let t=preview(&app,&rev,&id);let c=catalog_export::cancel(&app,TokenIntent{token:t}).unwrap();assert_eq!(c["committed"],false);assert_eq!(fs::read_dir(&dir).unwrap().count(),0);println!("service_cancel=unchanged empty_output=true");
 fs::set_permissions(&dir,fs::Permissions::from_mode(0o500)).unwrap();let t=preview(&app,&rev,&id);catalog_export::choose_directory(&app,&t,&dir).unwrap();let r=catalog_export::commit(&app,TokenIntent{token:t}).unwrap();fs::set_permissions(&dir,fs::Permissions::from_mode(0o700)).unwrap();assert_eq!(r["rows"][0]["result"],"failed");assert_eq!(r["rows"][0]["errorCode"],"catalog_temp_create");assert_eq!(fs::read_dir(&dir).unwrap().count(),0);println!("readonly_directory=failed catalog_temp_create no_target_or_temp=true");
 let t=preview(&app,&rev,&id);catalog_export::choose_directory(&app,&t,&dir).unwrap();let mut saved:libc::rlimit=unsafe{std::mem::zeroed()};assert_eq!(unsafe{libc::getrlimit(libc::RLIMIT_FSIZE,&mut saved)},0);let limited=libc::rlimit{rlim_cur:0,rlim_max:saved.rlim_max};let old_signal=unsafe{libc::signal(libc::SIGXFSZ,libc::SIG_IGN)};assert_eq!(unsafe{libc::setrlimit(libc::RLIMIT_FSIZE,&limited)},0);let result=catalog_export::commit(&app,TokenIntent{token:t});assert_eq!(unsafe{libc::setrlimit(libc::RLIMIT_FSIZE,&saved)},0);unsafe{libc::signal(libc::SIGXFSZ,old_signal)};let r=result.unwrap();assert_eq!(r["rows"][0]["result"],"failed");assert_eq!(r["rows"][0]["errorCode"],"catalog_write");assert_eq!(fs::read_dir(&dir).unwrap().count(),0);println!("write_error=failed catalog_write no_target_or_temp=true");
 assert!(app.shutdown());
}
```

## 资源及后续 gate

本 QA 不回收资源。QA 自有 `/private/tmp/ds003-qa2-Ggidgy` 含上述一次性 harness、synthetic profile、两个 Cargo targets、旧源码副本、前端产物和受保护 v3 payload 副本；关键测试主体和结论已持久化在本 checklist。协调者确认本任务与 DAA 对原始文件/工具无后续验证依赖、无进程占用并已确认归属后，按 canonical workflow 适时回收；若 QA/PM 还需重放，则保留至其结束。协调者拥有的两个临时 .app、各次实际导出文件及 Development/DAA QA targets 由其单独核对；两端 `.local/dev` 的原有配置与测试历史不得因此清理。

本 QA 未亲自操作 GUI、连接或上报；这次也未改 spec、tasks、实现、测试或配置。PM 澄清 DS11 后，Verification 对该精确 r5 接续；`qa_blocked` 不等于实现失败或 Human Owner 最终验收。


# QA2 口径澄清后的最终 verdict：qa_passed

2026-11-17（Asia/Shanghai），协调者转交 PM 对 DS11 的只读澄清：r5 同时要求真实 `exported_at` 和来源 payload 原始字节 SHA，“语言切换不改变数据或 SHA”比较同一来源版本、同一连接目标、同一预览/生成时间；不要求不同时刻生成的完整文件 SHA 相同。本次澄清未更改 spec、范围或验收标准；上节记录的验收口径暂阻塞由此解除，QA1 的失败与两次 QA2 阻塞历史保留。

Verification 在该明确口径下复核：两份原生文件的来源版本和连接目标完全一致；两份文件中真实生成时间各不相同。将**英文文件中唯一一次出现的时间字节**替换为中文文件的时间后，内存中的 2387 字节与中文文件逐字节完全一致，SHA 均为 `5198f7fef382f9524b81c66275b76cbdb779deb7741df16d3005f809bf6662e3`。这是为控制生成时间做的只读比较，未改任一文件，不把归一化结果冒充实际原生文件。实际中文/英文文件 SHA 分别为 `5198f7fe…` 和 `74686eaa…`，如实保留。真实 DS Vue 组件脚本的内存状态测试使用实际 locale、模拟 IPC：保持同一预览时切换语言，preview、来源和文件 SHA、token、已选实例不变；该测试不是原生 WebView。协调者分别观察中文与英文原生操作，但 modal 中无法通过顶栏切语言，不能声称曾在原生同一预览中切换。

对真实中文文件，本 QA 还用 Python stdlib 对该具体文档检查 UTF-8、重复键、精确已知字段、层级/大小、格式与版本、RFC UUID v4、上海时间、数值范围、BOOL bit、STRING 长度、地址占位及重叠、点名/ID 唯一、双语字段和文本长度；1 DB、4 点通过。此检查只覆盖该实际文档所用类型，不声称对所有可选格式或全部边界做了穷举。

为补足 DS06，本 QA 在自有临时 profile 中复用正式 `runtime/tests/plc_catalog_export.rs` 的实际 TIA 合成导入、命名/布局确认和 saved revision 场景；以正式引擎执行 preview、选目录和真实 commit，记录的整个 `config.sqlite`（包括 source archive、draft、revisions 与 selection）前后字节完全相同，SHA-256 `7f9787386e5e7bdbe18558d8ee57b67dd0ff7af985d631dc6cffd8b7e5b92edc`；输出文件成功写入自有目录。命令 `DS_TEST_RUN_ROOT=/private/tmp/ds003-qa2-Ggidgy/tia-ro CARGO_TARGET_DIR=/private/tmp/ds003-qa2-Ggidgy/target cargo test --manifest-path /private/tmp/ds003-qa2-Ggidgy/fs-harness/Cargo.toml --locked --offline --test read_only_tia imported_tia_paths_and_explicit_description_are_not_inferred -- --exact --nocapture` exit 0，1 passed，10 filtered。该合成证据不冒充实际 dev profile 操作前后全程快照；QA 所做的实际文件和数据库事后只读对照见上节。

TIA 复验以交付测试的同名函数为主体，在 publish 后和 preview 前保存 `fs::read(root.join("device-simulator-v1/config.sqlite"))`；用 `catalog_export::choose_directory` 和 `catalog_export::commit` 在自有新目录完成写出并断言 `result == "written"`，随后再次读取该 SQLite，断言 `before_bytes == after_bytes` 并打印两者 SHA。构建只在自有临时 Cargo 项目中发生，未修改仓库测试。

本 QA 的 `lsof -nP -iTCP:15191 -iTCP:15194 -iTCP:31976` 和 `lsof <DS .ds-profile.lock> <DAA .daa-runtime.lock>` 最后一次分别 exit 1 且无输出；此前观察到的 PID 18355 / 15191 listener 之后已不再出现。此观察以本机 `lsof` 可见范围为限。最终再次核对正式交付树 29/29 文件身份、spec、tasks 和两份锁 SHA 均与本轮 handoff 一致，结果见上节输入身份。

**QA2 结论为 `qa_passed`，交 Human Owner 进行本任务最终验收。**结论覆盖 r5 受控 macOS、合成测试和协调者原生联测的所述范围；不授予 DAA-017、DS-004、DAA-018 的 QA 或最终验收，也不证明 Windows/VM、真实 PLC、外部上报、生产部署、所有文件系统对抗竞争或旧二进制兼容。

## 证据与自有资源收尾

本 QA 不再依赖 `/private/tmp/ds003-qa2-Ggidgy` 下的构建、harness、synthetic profile、v3 payload 副本或两份临时导出文件。自有 harness 主体、命令、哈希、样本/绑定/来源结果及局限已写入本 checklist；中文实际原始文件的完整 2387 字节另已由 DAA 存入自身 `source_documents` 和采样 context，英文实际文件与其仅有上文两个时间字节值的受控差异。两端真实 dev 历史及其 source/sample 数据继续保留。

协调者应先确认 DAA-017 等并行验证也不再依赖这些文件、相关进程已退出、任务归属明确，再按 Human Owner 已要求的测试结束清理回收自有临时目录与文件；本 QA 不替其回收，也不清理用户 `.local/dev`。本 QA 仅更新 DS-003 checklist，未改 spec、tasks、实现、测试或项目配置。
