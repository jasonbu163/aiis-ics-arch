Task ID: DS-004
Revision: r2
Task Namespace: device-simulator
Workflow Mode: STD
Execution Mode: agent_team_same_session
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Status: qa_blocked
Verdict: qa_blocked
Handoff: r2 合成检查结果及 DS4-07 原生 blocker 交 Human Owner；解除隔离暂停后完成必需 fresh Verification，再由 Human Owner 决定最终验收。
# 独立 Verification 记录

## 范围、身份和结论

2026-11-17（Asia/Shanghai），由实际选择的 `verification` 角色、`fork_turns="none"` 开始，未继承 Development 对话推理。独立阅读根 `AGENTS.md`、根和最近作用域 README/PLAN、canonical workflow、verification 角色、完整 spec/tasks、相关实现及 diff。适用复核 skills：`project-governance`、`frontend-ui`、`i18n-workflow`、`rust-runtime`、`desktop-tauri`、`code-document-indexer`。这里只验证，不修改产品、spec 或 tasks。`contract_only` 表示合同控制，不证明角色文件 ACL 或平台强制路由。

规格为 `owner_approved`，SHA-256 `322b2be3639d124f02a0585a1cfaf1b3eb34e1a519f18b145f551ac1fa856ae4`；tasks 为 `developer_handoff`，SHA-256 `8ee3fa076b6ca3508ded00896ff3867c3aa3d2e93363cbf715f5e352b167548a`。正式交付工作树 base HEAD 为 `21cd789277695bbafaa55c24e39261fc7247f9b0`，不是独立 commit。下列九个 Development 候选/新测试文件的实际 SHA 在检查开始及结束时均与 tasks 一致：

```text
22331f7649a5849102cc919f8441dfbf9f472b54e43a806a3831e7426d0b75e4  runtime/src/domain/configuration.rs
e4e365fa9f7411fb9ac5fb58dbdc478fd62ee0e4d7bcdbaba81761f4266a9dec  runtime/src/services/source_import.rs
d30e505d7cb73e7f9989109dcd8523264ce59da9a9d902928d08a21f84380c6d  src/services/deviceSimulator.ts
30b86a632b09255d80ff67a77a650b4033265fdc321df3035eddb6b05a6c1c0a  src/app/simulator/views/points/index.vue
ef57a7f010506377b9155822ccacc5eff44aa110fcb67817984e8b0520e21079  src/app/simulator/components/PointEditor.vue
ca4cb7709be5e64d952f65b2ad073ad688279c3cc83262c3c2e5d1cd3915f3a1  src/app/simulator/locales/en-US.json
e078891300d0660e005c4c2a28eef23e49f873a8a5f94ea7853613b7db129744  src/app/simulator/locales/zh-CN.json
f084fca67bf363a0801eb80b630a36075728d60f921d1b221e967034cd63de25  runtime/tests/point_display_names.rs
f5544d59948b209c79741c9ae163f55b3bfba9d361592c985d95b84a4e10cd3a  tests/point-display-names.test.mjs
```

同目录 `CODE_INDEX.md` SHA `d3cdbaa62dcaf36536dd09d87f30963c5edbac137b72dd80c6bd46ceea917cc8`；`USER_GUIDE.md` SHA `569eaa40071c60f8ce588211e32dbd454b03fcbe30f919ca2a4680ed5fac073e`；`USER_GUIDE.zh-CN.md` SHA `8efbe998809a178c1cecd8641d6fec8bffc5abbfcccad3cea03525d9d3819c69`。diff 中本任务的代码、测试、文案和索引条目在已批准 allowlist 内。工作树还存在大量并行变更，包括 DS `src-tauri/src/config/bootstrap.rs`、其他指南内容、PLAN 和其他任务；tasks 将其列为任务外/先有变更，Verification 无法独立证明每处历史归属，未覆盖或回退它们。正式树 Tauri check 也包含该并行 bootstrap（SHA `d4341e8a909d15666b389c3928daf31d2a18e7b5b8c8b37ea239db0f8b451d4f`），不能解释为只编译了 DS-004 单独补丁。

**失败 F1：已提交的保存遇到未知回执时，界面错误地声称操作未完成，且所提示的刷新并不读回草稿。** 这在下面两个独立证据中成立：

1. 使用自有 4096 点合成 profile，每点中文/英文各 256 UTF-8 字节、描述 500 字节，配置有效且 5,926,517 字节低于 16 MiB。先成功发布一版，第二次保存返回 `save_receipt_unknown`、程序 exit 1；未重试。进程退出后只读 SQLite：`quick_check=ok`，草稿和旧 revision 的 payload SHA 均匹配；草稿首点描述前缀 `1`，旧 revision 为 `0`，证明未知回执的草稿实际已提交且旧版完整。DB SHA `e02672a414d7a6fb8e44b89379ae2341f8d53dccf8ea604702ca5e54a0872804`。这是当次时序观察，不宣称每次必现或磁盘容量已耗尽。128 点同等字段长度的 5 次保存/发布及重开成功。另一独立无 `test-automation` feature 的 4096 点 `services::queries::save` 样本返回 `result=ok/committed=true`，说明不能把超时说成确定性结果。
2. 单独的新小型合成 profile 用非默认测试能力 `after_save_commit` 一次性故障点，实际调用 `services::queries::save` 和 `Response::from_result`，得到 `{"result":"unknown","errorCode":"save_receipt_unknown","committed":null,"receiptState":"unknown","currentEtag":null,"data":null}`；退出后只读 SQLite 验证新双语名已提交，payload 哈希匹配，`quick_check=ok`。这是明确标记的故障注入，不能冒充自然超时或原生 GUI 试验。

`src/App.vue:12`、`:46` 在该 code 无专用翻译时使用 `operationFailedWithCode`，中英文分别显示“操作未完成（save_receipt_unknown）”和“Operation failed (save_receipt_unknown)”，与实际可能已提交相矛盾。`:13` 的通用 unknown 提示要求刷新“当前值与序号”，没有指明读取草稿/版本事实；`src/console/composables/useDeviceSimulator.ts:21` 的 `refresh` 在已有 configuration 时只查 runtime snapshot。独立内存执行真实状态逻辑：一次模拟 unknown 保存后调用 `refresh()`，保存调用 1 次、configuration 读取 0 次、snapshot 读取 1 次，原 ETag 仍保留。`src/components/console/ConfigRevisionBar.vue:7` 的保存按钮 disabled 条件不含 unknown；此处未模拟用户手动再次点击，不能声称它一定发生覆盖。应用没有自动重试；手动重新提交可能被已提交后的旧 ETag 拒绝，但必须先重新读回并核对，不能凭当前快照判断。此项违反本任务对显式保存/可核对持久化与版本容量的验收要求；返回 Development。若修复所需文件超出 r1 allowlist，先回 PM 处理范围，不由 Verification 扩写。

## 验收逐项

| 条款 | 独立结果与限制 |
| --- | --- |
| DS4-01 | 部分通过，整体受 F1 影响。Rust 实测缺字段、null、错类型、缺键、额外键、UTF-8 字节上限、Unicode/空格保留；in-memory 真 Vue editor 测试中文/英文独立、单侧清空和非法长度拒绝；SQLite 测试保存、重开、单侧变更。4096 满长度的第二次保存回执未知且 UI 误称失败。真实原生表单操作未测。 |
| DS4-02 | 部分证据通过，原生未测。真实 Vue 页面逻辑在内存 renderer 下切换 locale，空侧不回退，技术名存在，JSON 草稿与 ETag 不变，保存调用 0；editor 取消不发 confirm。源码 `useAgentLocale` 切换 locale/本机偏好，不请求保存。测试未通过真实顶栏/原生 WebView 实测持久化 bytes、版本、loaded、source，不能把内存测试扩为该证明。 |
| DS4-03 | 部分证据通过。旧二进制创建的旧值、旧版、新二进制只读测试和 TIA 合成源码测试均保留旧 `displayName`，新语言和描述默认未设置；中文编辑不改旧值、技术名/另一侧。新旧二进制读取旧库前后整库 SHA 相同。语言未标记的中文/英文文案已审；真实原生展示未测。 |
| DS4-04 | 合成兼容证据通过，完整条款受 F1 影响。旧库 old/new 读取零写回；新二进制显式写新字段后，旧二进制返回精确 `storage_payload`，整库 SHA 和目录条目均不变，未误开空库。旧 source archive 的 86 字节 blob 和两份 revision 也经只读哈希核对。常规 Rust 测试检查新草稿/发布版本、旧 payload、selected ETag、重开及 stale ETag；未实测原生 actual_loaded 行为。旧二进制是 DEV 保留的旧构建，实际 SHA 和行为经本轮复核，其构建时源码身份依 DEV handoff，不能独立追溯为签名构建。 |
| DS4-05 | 合成服务测试覆盖 DB 同身份重导保留中英、旧名、描述；新点未继承、不同 ID 不串值；layout/naming 预览及确认、取消、stale import CAS 和另一实例隔离。使用内存合成 TIA bytes，不是 DS-003 JSON 导出/导入或真实设备；并非所有 UDT/物理设备组合。 |
| DS4-06 | 部分证据通过。领域层拒绝 null/数值/对象/数组及超 500 字节，原样保留合法内容；合成 TIA 和手工点的独立字段、清空行为通过服务或内存组件测试，旧注释不自动填描述；历史 bytes 检查见 DS4-04。未在原生界面完成两类点的端到端保存/重开。 |
| DS4-07 | **未完成 / 环境隔离阻塞。** Rust、Node、格式、类型、Vite build 与正式树 Tauri `cargo check` 结果见下；未启动真实 macOS 窗口，未实测双语表单、顶栏切换、真实列宽拖动/应用重启持久化/复位，也未执行普通 `pnpm tauri dev` 的启动回归。共享表格源码具有稳定 `configuration.points` / column keys、最小宽、拖拽、localStorage 和复位；Node 宽度工具测试通过，但不能替代原生操作。 |

## 原生隔离评估与解除条件

普通 bootstrap 即使有 `DS_PROFILE_DIR` 覆盖也先读取源码树 `.env`；本轮未人工读取或修改该文件内容，Vite 按现有构建行为执行，不能据此断言构建工具未解析环境文件。`src-tauri/src/lib.rs:37-67` 使用 profile UUID 作为 WebKit `data_store_identifier`，但系统 WebKit/XPC 的应用身份、共享缓存和实际落盘目录不由该 UUID 完整限定。DEV 未启动的临时 `DS004-dev.app` 外层 identifier 为 `com.aiis.aw.ds004.g6mp7m`，本轮 `otool -s __TEXT __info_plist ...` 看见内嵌 plist 只有 name/version、无 `CFBundleIdentifier`；已知唯一 identifier 的 Application Support 与 WebKit 目录在查询时不存在，不能由此证明 Mach-O/系统服务不会选择产品或进程名共享目录。测试自动化入口又限定其他任务的 manifest/profile/identity。没有证明实际 OS/XPC 写入完全限于本任务资源，故未运行该 app、未更改 HOME、未启动本地 server，未申请绕过沙箱；没有 auto-review 拒绝事件可报告。

解除条件：在可证明独立 macOS 用户或隔离 macOS 测试环境中，准备全新自有 profile、唯一 WebKit store 与 app 身份，预先明确并核实 WebKit/XPC/应用数据实际落点，再从与正式交付逐文件一致的候选及受控本地资源启动；记录正常关闭/重开及真实双语编辑、顶栏切换前后 SQLite/ETag/版本/source/loaded、列宽拖动/重启/复位。不可使用用户现有 profile 或共享 WebKit store。若使用临时源码快照，须核对与正式源码及普通入口的区别；临时快照不能证明正式入口已运行。

## 环境、命令和结果

本轮命令工作目录均为 `automation-world/device-simulator`，除另行写明。macOS 15.7.7 Darwin 24.6.0 arm64；rustc/cargo 1.89.0，Node v22.19.0，pnpm 11.11.0。临时根 `/private/tmp/ds004-qa.TwgHEz` 为本轮新建，目标、生成前端和 profile 均在该目录；cargo 使用锁文件和 `--offline`。Shell 初始化多次打印 `/bin/ps: Operation not permitted`，不改变下列已列 exit。无依赖安装。

```sh
CARGO_TARGET_DIR=/private/tmp/ds004-qa.TwgHEz/cargo DS_TEST_RUN_ROOT=/private/tmp/ds004-qa.TwgHEz/rust cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test point_display_names --test configuration_store --test source_import --test versions --test owner_contract
# exit 0: 19 passed; compatibility_probe 单独标记 ignored
CARGO_TARGET_DIR=/private/tmp/ds004-qa.TwgHEz/cargo DS_TEST_RUN_ROOT=/private/tmp/ds004-qa.TwgHEz/rust-no-feature cargo test --manifest-path runtime/Cargo.toml --locked --offline --test point_display_names
# exit 0: 3 passed, 1 ignored
node --test tests/*.test.mjs
# exit 0: 23 passed
cargo fmt --manifest-path runtime/Cargo.toml --check
# exit 0
pnpm exec vue-tsc --noEmit
# exit 0
pnpm exec vite build --outDir /private/tmp/ds004-qa.TwgHEz/ui
# exit 0; Rollup PURE 注释与 >500 kB chunk 警告
CARGO_TARGET_DIR=/private/tmp/ds004-qa.TwgHEz/cargo-tauri CARGO_NET_OFFLINE=true cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features native-s7
# exit 0; 正式工作树 Tauri 编译检查，不启动窗口
git diff --check -- runtime/src/domain/configuration.rs runtime/src/services/source_import.rs src/services/deviceSimulator.ts src/app/simulator/views/points/index.vue src/app/simulator/components/PointEditor.vue src/app/simulator/locales/en-US.json src/app/simulator/locales/zh-CN.json CODE_INDEX.md USER_GUIDE.md USER_GUIDE.zh-CN.md
# exit 0
git diff --no-index --check /dev/null runtime/tests/point_display_names.rs
git diff --no-index --check /dev/null tests/point-display-names.test.mjs
# 各 exit 1 表示新文件与 /dev/null 不同；无 whitespace 错误输出
```

独立 Python stdlib 扫描两份指南和 `CODE_INDEX.md` 的相对文件链接：41 个存在、0 个缺失，exit 0；未检查 anchors。初次容量 helper 的 `rustc` 未提供 `-L native=.../out/native`，链接报 `library 'ds_s7_native' not found`、exit 1，未运行 profile；补上本轮独立构建的 native 库路径后下述两个运行。archive 只读查询首次误用不存在的 `source_versions.bytes` 列并报错，随后以 `source_blobs.utf8`/`byte_len` 复查成功；旧/new 二进制两次只读本身均 exit 0、整库 SHA 未变。

### 兼容与容量复现命令

旧 probe 的 SHA 为 `70589d62bd2708f3c0a0276cfb5c86280473358e9e636bf086dcfc2d0e70eb4a`；本轮新 probe SHA `d024f36aae40a4f2ba11318bdd8954c2422591698c7ff2e46b3229a0d33133e7`。顺序执行，profile 是本轮全新路径；以下每条 exit 0：

```sh
DS4_COMPAT_PROFILE=/private/tmp/ds004-qa.TwgHEz/compat-profile DS4_COMPAT_MODE=create /private/tmp/ds-004-r1-dev.G6mp7M/cargo-old/debug/deps/point_display_names-f259d2b34ad19b3e --ignored --exact compatibility_probe --nocapture
DS4_COMPAT_PROFILE=/private/tmp/ds004-qa.TwgHEz/compat-profile DS4_COMPAT_MODE=old /private/tmp/ds-004-r1-dev.G6mp7M/cargo-old/debug/deps/point_display_names-f259d2b34ad19b3e --ignored --exact compatibility_probe --nocapture
DS4_COMPAT_PROFILE=/private/tmp/ds004-qa.TwgHEz/compat-profile DS4_COMPAT_MODE=old /private/tmp/ds004-qa.TwgHEz/cargo/debug/deps/point_display_names-99d266ed86815772 --ignored --exact compatibility_probe --nocapture
DS4_COMPAT_PROFILE=/private/tmp/ds004-qa.TwgHEz/compat-profile DS4_COMPAT_MODE=upgrade /private/tmp/ds004-qa.TwgHEz/cargo/debug/deps/point_display_names-99d266ed86815772 --ignored --exact compatibility_probe --nocapture
DS4_COMPAT_PROFILE=/private/tmp/ds004-qa.TwgHEz/compat-profile DS4_COMPAT_MODE=reject /private/tmp/ds-004-r1-dev.G6mp7M/cargo-old/debug/deps/point_display_names-f259d2b34ad19b3e --ignored --exact compatibility_probe --nocapture
```

旧库创建、旧/新读取后的 SHA 均 `f92c15d71296858a2b7541a35b73ef3e9b22f9c5409dfee473b9f9ff3b8aaf0f`；upgrade 后旧版拒绝前后均 `bc803432f4a36af86f0649e244b22d3e79aaed36225e3a27f7e1b37cea232685`，profile 路径清单不变。另复制 DEV 合成 archive 到 `/private/tmp/ds004-qa.TwgHEz/archive-profile`，以相同 old/new `DS4_COMPAT_MODE=old` 命令读取，均 exit 0，整库 SHA 均 `abe4291ec0969a95c6b8769e5cfc9470588dd7b1a8020f3d47e28f276b5d4e6d`；source_blob SHA `8a90d93c0f5eda7fd350251ee03865c2a009374be18e24afba2e38440e1fcdd8`，长度 86，存在两份 revision。

容量程序由 DEV 留存的 `capacity_probe.rs` 复制到本轮 temp，并将 profile 根改为 `capacity-128-profile` 或 `capacity-4096-profile`、点数改为 128/4096；两份 helper SHA 分别为 `9df41c6f600d1b01bd9265af66015832381bfb8025ec10ad5f16174a6fcac5a8` 和 `00dc1865b33dc60ac9622087d3076594e2b63c3b624022c3e369dd98d81c3ed4`。实际编译/运行（profile 不能已存在）为：

```sh
rustc --edition=2021 /private/tmp/ds004-qa.TwgHEz/capacity-128.rs -L dependency=/private/tmp/ds004-qa.TwgHEz/cargo/debug/deps -L native=/private/tmp/ds004-qa.TwgHEz/cargo/debug/build/ds-runtime-3a1f1c5c1ca3d4db/out/native --extern ds_runtime=/private/tmp/ds004-qa.TwgHEz/cargo/debug/deps/libds_runtime-670baab2b361753b.rlib --extern serde_json=/private/tmp/ds004-qa.TwgHEz/cargo/debug/deps/libserde_json-67b195081674173f.rlib -o /private/tmp/ds004-qa.TwgHEz/capacity-128
DYLD_LIBRARY_PATH=/private/tmp/ds004-qa.TwgHEz/cargo/debug/build/ds-runtime-3a1f1c5c1ca3d4db/out/native /private/tmp/ds004-qa.TwgHEz/capacity-128
rustc --edition=2021 /private/tmp/ds004-qa.TwgHEz/capacity-4096.rs -L dependency=/private/tmp/ds004-qa.TwgHEz/cargo/debug/deps -L native=/private/tmp/ds004-qa.TwgHEz/cargo/debug/build/ds-runtime-3a1f1c5c1ca3d4db/out/native --extern ds_runtime=/private/tmp/ds004-qa.TwgHEz/cargo/debug/deps/libds_runtime-670baab2b361753b.rlib --extern serde_json=/private/tmp/ds004-qa.TwgHEz/cargo/debug/deps/libserde_json-67b195081674173f.rlib -o /private/tmp/ds004-qa.TwgHEz/capacity-4096
DYLD_LIBRARY_PATH=/private/tmp/ds004-qa.TwgHEz/cargo/debug/build/ds-runtime-3a1f1c5c1ca3d4db/out/native /private/tmp/ds004-qa.TwgHEz/capacity-4096
```

两次编译 exit 0。128 点运行 exit 0、185,693 bytes、5 revisions 重开成功；4096 点运行 exit 1、`Error: "save_receipt_unknown"`、只有首版成功回执，详见 F1。读回使用 Python `sqlite3.connect('file:'+path+'?mode=ro', uri=True)`，核 `PRAGMA quick_check`，分别读取 `configuration_draft.canonical_payload/sha256` 和 `configuration_revisions.payload/sha256` 并以 `hashlib.sha256(payload)` 比较；未更改或重试该 profile。无 feature 的 service 样本在该 profile 的自有副本上把描述前缀改为 `2`，通过 `queries::save` 得到已知成功，DB SHA `4c7264f30e089e7124ac3a04b8868671045690680125bfc357cdfe05ecac0de8`；不是对原 unknown 操作的重试。

故障注入独立 helper 是 `/private/tmp/ds004-qa.TwgHEz/unknown_fault.rs`，SHA `e97e503b338e16594ea3f1da70fe79d44c39ba99d8459335fb2507522df4ee03`；它在全新合成库设置 `test_fault("after_save_commit")` 后仅调用一次 `queries::save`，再输出 `Response::from_result`。编译/运行命令如下，均 exit 0：

```sh
rustc --edition=2021 /private/tmp/ds004-qa.TwgHEz/unknown_fault.rs -L dependency=/private/tmp/ds004-qa.TwgHEz/cargo/debug/deps -L native=/private/tmp/ds004-qa.TwgHEz/cargo/debug/build/ds-runtime-3a1f1c5c1ca3d4db/out/native --extern ds_runtime=/private/tmp/ds004-qa.TwgHEz/cargo/debug/deps/libds_runtime-670baab2b361753b.rlib --extern serde_json=/private/tmp/ds004-qa.TwgHEz/cargo/debug/deps/libserde_json-67b195081674173f.rlib -o /private/tmp/ds004-qa.TwgHEz/unknown-fault
DYLD_LIBRARY_PATH=/private/tmp/ds004-qa.TwgHEz/cargo/debug/build/ds-runtime-3a1f1c5c1ca3d4db/out/native /private/tmp/ds004-qa.TwgHEz/unknown-fault /private/tmp/ds004-qa.TwgHEz/unknown-fault-profile
```

内存 UI 检查用 `node --input-type=module`，通过 TypeScript `transpileModule`、Vue 和 Node `vm` 加载正式 `useDeviceSimulator.ts`；注入一次 `IpcFailure('save_receipt_unknown', null, true)` 与计数器。断言 `save()` 返回 false、`unknown=true`，再执行 `refresh()` 并检查 save/configuration/snapshot 调用分别为 1/0/1、ETag 为旧值。读取两份正式 locale JSON，证明 `errors.save_receipt_unknown` 均不存在及上述 fallback/通用 warning；该测试未渲染原生 WebView。

```sh
node --input-type=module <<'JS'
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
import ts from 'typescript';
const require=createRequire(import.meta.url);
const src=fs.readFileSync('src/console/composables/useDeviceSimulator.ts','utf8');
const code=ts.transpileModule(src,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
class IpcFailure extends Error {constructor(code,etag=null,unknown=false){super(code);this.code=code;this.currentEtag=etag;this.unknown=unknown;}}
let saveCalls=0, configCalls=0, snapshotCalls=0;
const ipc={IpcFailure,desktopAvailable:true,saveConfiguration:async()=>{saveCalls++;throw new IpcFailure('save_receipt_unknown',null,true)},getConfiguration:async()=>{configCalls++;throw Error('unexpected configuration read')},getSnapshot:async()=>{snapshotCalls++;return {instances:[]}}};
const context={exports:{},require:name=>name==='vue'?require('vue'):ipc,performance:{now:()=>5000},document:{hidden:false},structuredClone};
vm.runInNewContext(code,context);
const state=context.exports.useDeviceSimulator();
state.bootstrap.value={}; state.configuration.value={etag:'previous',workspace:{instances:[]}}; state.draft.value={instances:[]};
assert.equal(await state.save(),false); assert.equal(state.unknown.value,true); assert.equal(state.error.value,'save_receipt_unknown');
await state.refresh(); assert.equal(saveCalls,1); assert.equal(configCalls,0); assert.equal(snapshotCalls,1); assert.equal(state.configuration.value.etag,'previous');
for(const locale of ['zh-CN','en-US']){
 const messages=JSON.parse(fs.readFileSync(`src/app/simulator/locales/${locale}.json`,'utf8'));
 assert.equal(messages.errors.save_receipt_unknown,undefined);
 console.log(locale,'fallback=',messages.operationFailedWithCode.replace('{code}','save_receipt_unknown'),'warning=',messages.unknownReceipt);
}
const app=fs.readFileSync('src/App.vue','utf8'); const bar=fs.readFileSync('src/components/console/ConfigRevisionBar.vue','utf8');
assert.match(app,/te\(key\)\s*\?\s*t\(key\)\s*:\s*t\('simulator\.operationFailedWithCode'/);
console.log('saveCalls=',saveCalls,'configReadsAfterRefresh=',configCalls,'snapshotReads=',snapshotCalls,'unknown=',state.unknown.value,'saveButton=',bar.split('\n').find(x=>x.includes('data-testid="configuration-save"')).trim());
JS
# exit 0
```

## 数据、资源和下一 gate

所有 SQLite profile 均为本轮新建或 DEV 明确声明的自有合成库副本；新库首次打开执行既有 `0001_initial.sql` 初始建库 DDL，未对现有用户库做 DDL、迁移或 schema 改造。无真实 PLC、用户 profile、网络上报、DS-003 JSON 导入/导出、发布或部署。Rust TIA 重导仅使用合成输入 bytes。

本轮 `/private/tmp/ds004-qa.TwgHEz` 留给 Development/下一轮 QA 核查，含自有合成 profile、helper 和隔离构建；`/private/tmp/ds-004-r1-dev.G6mp7M` 仍属 Development 保留资源。关键结论、校验值与限制已写入本记录，不以临时文件作为唯一结论来源。Verification 不执行清理；返工与 QA 完成且不再需要证据后，由 coordinator 确认归属、占用和回收条件。

F1 返回 Development，修复后须记录新候选、重测已提交但回执未知的准确提示与草稿核对行为，并再次 fresh-context Verification。DS4-07 的安全隔离与原生操作仍须完成。Human Owner 只有在后续可用的独立 QA 结果上决定最终验收；本 `qa_failed` 不等于 Owner 接受，也不授权实际环境、设备或发布。

---

## QA2：返工候选的独立 Verification（2026-11-17）

### 结论与精确身份

**QA2 verdict：`qa_failed`。** QA1 F1 的原始失败事实、验证内容和 verdict 全部保留在上文；本轮对原保存未知回执提示及其单一恢复路径的复核通过，但发现新的 **F2：保存核对期间，后一个已知的暂停/停止失败会覆盖前一个运行控制未知回执，保存核对后错误解除 unknown 标志**。F2 返回 Development；本 QA 不能由自动化通过数量抵销。另有 DS4-07 原生隔离 blocker，不能因为有失败而遗忘。Human Owner 最终验收尚未发生。

本轮由 coordinator 在新 Development `developer_handoff` 后实际调用 `verification`、`fork_turns="none"`；没有继承 Development 对话推理。独立读取根 AGENTS、根和 AW/DS 最近 README/PLAN、canonical workflow、verification 角色、完整 spec/tasks/QA1 checklist、候选源码与 diff、可用测试输出；只验证并写本 checklist。使用 `project-governance`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping` 和 `code-document-indexer`，不借 skill 修改产品。`contract_only` 是角色和 handoff 合同，不宣称平台 ACL 或强制路由。

正式工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的未提交候选，base HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`；不是独立提交。spec SHA-256 `322b2be3639d124f02a0585a1cfaf1b3eb34e1a519f18b145f551ac1fa856ae4`；返工后 tasks SHA-256 `f461f3754d66aa5ab4199215debb4a108c36ead8c4120e2ef4c143983aea352a`；本 QA 写前 QA1 checklist SHA-256 `d40b62e37348de997eaf7eaaf2c1ea83a9a6d5545214867c5b49eca953f1e86d`。按 tasks 最后清单逐一计算 14 文件均匹配；按 `SHA256␠␠相对路径\n`、tasks 所列次序构造的清单 SHA-256 为 `b01305af289c017b2ce2868e4d2928da2cd7fa6721a68ae4332b93019cef6348`。这些摘要锁定整个候选文件，不能把文件内既有或并行工作一律归因 DS-004；工作树另有大量并行变更。原 QA1 与本节之间仅更新本文件顶部当前 handoff 行，原 QA1 全文留存。

### F1 复核：已提交且回执未知

在新建自有 `/private/tmp/ds004-qa2.zcTzan/fault/` 中，以正式 Rust service `queries::save` 和明确的测试 feature 故障点 `after_save_commit` 实际调用一次保存。Rust 结果是 `result=unknown`、`errorCode=save_receipt_unknown`、`committed=null`、`receiptState=unknown`；服务读回的新 ETag `c3e867e4-09f2-4a92-8517-3b596361d3f9` 不同于提交前的 `35894564-76b9-460b-a974-36439bf9ff4c`。进程退出后用 SQLite `mode=ro` 检查：`quick_check=ok`、`user_version=1`、草稿实际包含 `故障注入` / `Synthetic fault` 与描述 `explicit`、revision 数 0；payload 实算和保存 SHA 均为 `4660c608c3345c66eb9aedc76888b31714529ef25901f1c2ec68212fb53dcc56`，整库 SHA `51f405d8535f27086e2a5cef78684c1e7702f32768a1b2b78218d6298df360e2`。此结果证明**本次受控故障注入**已经提交，并非自然超时或原生 GUI 证明；未对这个 profile 重试保存。

Node 内存测试将本轮真实 Rust unknown envelope 和已保存草稿交给正式 TS IPC facade 与 Vue 状态逻辑，模拟 Tauri invoke 边界：保存调用一次，未知状态保留，复查不替换本地草稿；一致时再次读取 ETag/工作区后才显式确认。还检查远端 ETag 或内容变化、本地并发编辑、编辑框打开、读失败及显式重读丢弃；并核对非点位页可见的中英文错误提示与“配置中心 → DB 点位”、顶栏刷新仅为运行快照、禁止重复提交、关窗可能丢失未保存本地编辑和重读会丢弃本地草稿等文案。单一额外未知 stop 及只读刷新可按既有测试保留；QA1 F1 的特定误称失败/仅刷新快照问题在这些范围内关闭。此项关闭不覆盖以下 F2 或原生界面。

### 新失败 F2（开放；返回 Development）

**可复现条件与观测**：`/private/tmp/ds004-qa2.zcTzan/multiple-receipts-facade.cjs`（SHA-256 `bdb0ab938c906808c48b7d4274039f22b6421962210bbf8924639306befb5e5f`）在 Node VM 转译并执行正式 `src/services/deviceSimulator.ts` 与 `src/console/composables/useDeviceSimulator.ts`。保存响应和已提交草稿来自上面的本轮真实 Rust 故障证据；停/暂停响应由测试边界**合成**，不是实际 Tauri、原生窗口或现场设备操作。顺序为一次未知保存 → `stop` 返回 `runtime_task_receipt_unknown` / unknown → `pause` 返回 `control_rejected` / known → 只读检查并确认一致保存。实际输出：

```text
after stop: {"error":"runtime_task_receipt_unknown","unknown":true,"uncertain":true}
after pause: {"error":"control_rejected","unknown":true,"uncertain":true}
after save reconciliation: {"accepted":true,"error":"control_rejected","unknown":false,"uncertain":false,"controls":["stop","pause"],"saveCount":1}
AssertionError: unknown stop receipt must remain visible after save reconciliation
```

脚本 exit 1；断言失败是本轮故意检验必须保留未知回执的结果，不是产品 crash。实际源码 `src/console/composables/useDeviceSimulator.ts:29-30,64-79` 只保存一个 `safetyFailure`；后一个已知失败替换未知 stop，`clearUncertainSave()` 随之用已知结果设 `unknown=false`。保存确认只读取配置，不核对该 stop 的运行结果，却将它从 UI 的未知回执中抹去；之后 `save()` 的 unknown 门禁不再保护该状态。

该合成序列有正式代码路径支持：`src-tauri/src/commands/mod.rs::execute` 中提交型 runtime task join 失败可形成 `runtime_task_receipt_unknown`；`runtime/src/services/queries.rs::control` 对失败的 pause 返回 `control_rejected`，`runtime/src/services/owner.rs::control` 在未运行时拒绝 pause。未知 stop 的 `action` catch 不主动刷新，`src/app/simulator/views/overview/index.vue:30` 依旧快照的 `running` 状态可仍允许 Pause，因此 stop 已执行但回执未知、随后暂停被拒绝是可能的时序；定时刷新何时发生取决于调度，本轮未模拟 OS/Tauri 真实时序。应保留各未核对的 unknown，或在相关事实被可靠核对前保持其可见与必要保护；具体实现由 Development 决定，不在 QA 中修复。返工后须以精确候选重新做 fresh-context Verification。

### 逐项验收与限制

| 验收项 | QA2 独立结论 |
| --- | --- |
| DS4-01 | 部分证据通过：无 feature Rust 3 通过（1 个显式兼容 probe 忽略），检查空/单侧、Unicode、非法键/类型/null/UTF-8 字节上限和显式保存/重开；Node 内存 editor 检查取消及双语字段。真实原生表单仍未测；F2 影响整体验收。 |
| DS4-02 | 部分证据通过：内存 renderer 的正式页面切换两种语言，空侧不回退、技术名和草稿/ETag 不变、保存调用为 0；原生顶栏与持久化 bytes/版本/loaded/source 在真实窗口的切换未测。 |
| DS4-03 | 合成与旧二进制证据支持旧 `displayName` 保留且新字段不自动填充；中英文旧字段标注和独立编辑经源码/Node/Rust 检查。真实原生展示未测。 |
| DS4-04 | 新建合成 profile 顺序 old create/old read/new read 后整库 SHA 均 `792282031bff3f2002be20033aa2457d5eee2c53bae7d9257fff900002afd6dd`；new 显式 upgrade 后 old reject 前后均 `a84c4abd125c873e599e16f1dadfd2ed0c0313d94a5a637cab874a1b0357f29c`，文件清单一致，五次 probe 均 exit 0。旧二进制 SHA `70589d62bd2708f3c0a0276cfb5c86280473358e9e636bf086dcfc2d0e70eb4a`，构建时源码身份依 DEV/QA1 历史，非独立签名证明。旧 archive 的更广证据见保留的 QA1；原生 actual_loaded 未测。 |
| DS4-05 | 合成 DB/UDT 服务回归检查同 ID 重导、变化 ID 隔离、预览/取消、并发 ETag 及其他实例；未使用真实设备，未测试 DS-003 JSON 导出/导入。 |
| DS4-06 | 合成 Rust/Node 覆盖独立描述、清空、500 UTF-8 字节边界及历史字段隔离；原生手工/TIA 双类点完整保存重开未测。 |
| DS4-07 | **未完成：原生验证阻塞。** 真实 macOS 原生双语编辑、顶栏切换、表格列宽拖动/跨重启持久化/复位及普通 `pnpm tauri dev` 启动均未执行。内存列宽工具测试和本轮隔离前端 build 不能代替这些检查；本轮未重跑 Tauri Rust check，QA1 的正式树编译检查及限制仍在原记录。 |

### 本轮环境、命令与证据

环境：macOS 15.7.7 / Darwin 24.6.0 arm64、rustc/cargo 1.89.0、Node v22.19.0、pnpm 11.11.0。除另示路径，命令在 `automation-world/device-simulator`；Cargo 均 `--locked --offline`，无依赖安装：

```sh
CARGO_TARGET_DIR=/private/tmp/ds004-qa2.zcTzan/cargo DS_TEST_RUN_ROOT=/private/tmp/ds004-qa2.zcTzan/fault cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test point_display_names committed_save_receipt_fault_emits_real_readback_for_ui_reconciliation -- --nocapture
# exit 0：1 passed；真实 service 故障注入输出 /private/tmp/ds004-qa2.zcTzan/fault.log
CARGO_TARGET_DIR=/private/tmp/ds004-qa2.zcTzan/cargo DS_TEST_RUN_ROOT=/private/tmp/ds004-qa2.zcTzan/regression cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test point_display_names --test configuration_store --test source_import --test versions --test owner_contract
# exit 0：20 passed，1 ignored；/private/tmp/ds004-qa2.zcTzan/rust.log
CARGO_TARGET_DIR=/private/tmp/ds004-qa2.zcTzan/cargo DS_TEST_RUN_ROOT=/private/tmp/ds004-qa2.zcTzan/no-feature cargo test --manifest-path runtime/Cargo.toml --locked --offline --test point_display_names
# exit 0：3 passed，1 ignored
DS4_FAULT_LOG=/private/tmp/ds004-qa2.zcTzan/fault.log node --test tests/*.test.mjs
# exit 0：31 passed，0 skipped；/private/tmp/ds004-qa2.zcTzan/node.log
node /private/tmp/ds004-qa2.zcTzan/multiple-receipts-facade.cjs
# exit 1：F2 独立断言失败；同目录 multiple-receipts-facade.log
cargo fmt --manifest-path runtime/Cargo.toml --check
pnpm exec vue-tsc --noEmit
node /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator/node_modules/vue-tsc/bin/vue-tsc.js --noEmit
# 上述三项各 exit 0，类型检查为正式树
```

前端构建使用 `/private/tmp/ds004-qa2.zcTzan/snapshot/device-simulator`，复制当前 `src`、`index.html`、包/锁/TS/Vite 文件与相邻共享 `console-ui/src/ui`，不复制 `.env*`，复用既有 node_modules 符号链接；`diff -rq` 确认两份源码树与正式工作树逐文件一致，`cmp` 确认 Vite 配置相同。隔离目录执行 `node /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator/node_modules/vite/bin/vite.js build --outDir /private/tmp/ds004-qa2.zcTzan/ui` exit 0；有已有依赖 PURE 注释与 >500 kB chunk 警告。该 build 是隔离快照的构建，不是正式普通启动。此前在此快照运行 `pnpm exec vite build ...` 时 pnpm 尝试获取 registry 元数据，输出 `ERR_PNPM_META_FETCH_FAIL`，随后因无 TTY 中止模块目录移除/安装而 exit 1；没有安装依赖。未读取或修改用户 `.env`，不把失败隐藏为成功。

独立 Python 扫描两份 locale：叶子键 480 / 480、集合一致；两份用户指南和 module CODE_INDEX 相对文件链接 41 项、0 缺失，未验证锚点。范围内 12 个 tracked 文件 `git diff --check` exit 0；两个新测试文件分别 `git diff --no-index --check /dev/null <file>` 返回 1 表示存在差异、无 whitespace 诊断。新增测试的头部和索引项已审。14 文件 SHA 与精确交接清单一致；未将其他任务或并行 bootstrap 归为本任务。

### 原生 blocker、资源与 handoff

当前指令因另一任务原生测试退出后疑似重新绑定或启动至默认真实 DAA profile、影响未知，明确暂停一切 GUI/CUA 启动或附着。本轮未启动应用、浏览器原生窗口、CUA、PLC、网络上报或真实数据库，未读取/修改用户 `.env`；新合成 SQLite 初始化运行项目现有的初始建库 DDL，没有对用户历史库执行 DDL/迁移。QA1 的隔离评估和 DS4-07 缺口保留：将来只有在事件已调查、明确解除暂停，且有可证明独立 macOS 用户/环境、自有 profile、唯一 WebKit store/app 身份并核实 OS/XPC 数据落点的安全方案后，才能对与正式交付一致的候选及普通入口验证真实编辑、顶栏、SQLite/ETag/版本/loaded/source 和列宽跨重启/复位；不能将临时快照运行冒称正式入口。

本 QA 自有 `/private/tmp/ds004-qa2.zcTzan` 保留独立脚本、日志、合成 profile、兼容 probe、隔离构建和 QA1 写前副本，供 Development 与下一轮 QA 核对；核心结论、摘要和命令已持久化在本 checklist。QA 不清理；返工及 QA 完成且无证据依赖后由 coordinator 盘点归属和回收。F2 精确证据交回 Development，修复后须新 handoff 和 fresh-context QA；本 QA 不能给予 Human Owner 最终验收，也不授权 DS-003/DAA-017 导出导入、生产、现场或发布。

---

## QA3：第二次返工候选的独立 Verification（2026-11-17）

### 结论与验证身份

**QA3 verdict：`qa_failed`。** F1 的受控单保存恢复和 F2 原始覆盖序列在本轮所测范围内通过；QA1、QA2 的失败事实及原 verdict 仍完整保留。新发现 **F3：未核实的其他未知回执在安全控制核对后，会被一次普通点位命名预览或草稿重读清除，随后保存被放行**；以及 **F4：保存期间另一未知回执到达时，保存关闭仍可放行**。F3/F4 返回 Development，不能以其他测试通过抵销。DS4-07 的真实原生界面和普通入口仍因隔离事件暂停，另有 blocker；Human Owner 最终验收尚未发生。

本轮由 coordinator 在新 `developer_handoff` 后调用 `verification`、`fork_turns="none"`，未继承 Development 的对话推理。独立阅读根 `AGENTS.md`、根和 AW/DS 最近作用域 README/PLAN、canonical workflow、verification 角色、完整 spec/tasks/checklist、变更代码及 diff 和可用测试输出。按触达面使用 `project-governance`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping` 及 `code-document-indexer`，仅验证；角色合同为 `contract_only`，不宣称平台 ACL、强制路由或自动执行。此次只修改本 checklist 的当前 handoff 和追加 QA3；不修改产品、spec、tasks 或其他任务。

正式未提交候选位于 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，base HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，不是独立 commit。`spec.md` 为 `owner_approved`，SHA-256 `322b2be3639d124f02a0585a1cfaf1b3eb34e1a519f18b145f551ac1fa856ae4`；最新 `tasks.md` 为 `developer_handoff`，SHA-256 `6608394c29ff180a80e8bd8dbedd652b67760b316186f55a35da56dc1dcc4abd`；QA3 写前本 checklist SHA-256 `a122c57cfbb5d0cb9b74b45d9b0786ddd5cfed9c3cdb9fea268e6ad01ea88f10`。按 tasks 最后清单顺序对 14 个文件逐一 `shasum -a 256`，每项匹配；以 `SHA256  相对路径\n` 汇总的清单 SHA-256 为 `d80180e4611354d5a42973a9db42ccd9ffbb5f3bba64699252c391b9f30f38c1`。清单锁定完整文件，不意味着文件内所有先有差异都归本任务；仓库另有大量并行脏变更，未覆盖或回退。

### F1/F2 的本轮复核

本轮使用全新自有 `/private/tmp/ds004-qa3.aymirQ`，实际运行正式 Rust service 和非默认 `test-automation` 的一次性 `after_save_commit` 故障点。`queries::save` 产生 `result=unknown`、`errorCode=save_receipt_unknown`、`committed=null`、`receiptState=unknown`；ETag 从 `0b28b17b-0bd2-44f9-bdcd-10a48433f012` 变为 `29636113-6074-4c4a-89c5-129a89ac9b40`。进程退出后，以 SQLite `mode=ro` 检查自有故障 profile：`quick_check=ok`、`user_version=1`、revision 数 0，已保存点的两种语言为 `故障注入` / `Synthetic fault`，描述为 `explicit`，计算和存储 payload SHA 均为 `6221590ca111ff236ed6bd7c02bad7db61450363c2f859113bea1f6f44a9ae27`；整库 SHA `369f2e8c7f9652374df484ee44bf77c878905f323fee56864d00d00f54f08b5a`。此为标记的故障注入，不是自然超时、原生 IPC 或设备测试；没有对该保存重试。

将此轮真实 Rust unknown envelope/已保存 workspace 输入正式 TypeScript IPC facade 和真实 Vue 状态逻辑，Tauri `invoke` 边界仅用合成响应。独立脚本 `/private/tmp/ds004-qa3.aymirQ/facade-matrix.cjs`，SHA-256 `d2da54af2e88e173beaf1f0f81c59aa887ee456c9a9ef376a50d9705c1239873`，exit 0。两次分别按“先确认保存、后确认控制”和相反顺序执行：一次未知保存；实例 A 未知 stop → 已知拒绝 pause → 实例 B 未知 pause → A 再次未知 stop；保留三个各自实例/动作回执；后台快照失败及 stale、缺失、重复、无效 epoch 的核对都未清除记录；待定期间命名预览和再次保存未发出；保存 ETag 在确认前变化、控制 epoch 在确认前变化及本地并发编辑均阻止相应确认。两次核对均要求显式确认，均保留本地稿，保存调用始终一次。F2 的原始“未知 stop 被已知 pause 拒绝覆盖，再随保存确认消失”在所测路径中未再复现。恢复当前状态不证明过去未知操作的成功或失败；这些检查也不覆盖下述 F3。

### F3：其他未知回执被普通操作清除（开放，返回 Development）

独立脚本 `/private/tmp/ds004-qa3.aymirQ/other-unknown-preview.cjs`，SHA-256 `d60ba138cfc7a3d6a92619e837de54d7b330f8d27ed44f19a7c0aee5f67674db`，以 Node VM 转译并执行正式 `src/services/deviceSimulator.ts` 和 `src/console/composables/useDeviceSimulator.ts`。Tauri `invoke` 及 apply、stop、snapshot、preview、save 响应均为**合成**，没有启动 GUI、真实 IPC、PLC 或访问用户 profile。步骤是：

1. 合成一次 `apply_receipt_unknown`，再合成未知 stop；显式读取两次一致的当前状态并确认 stop 的当前事实。此时原 apply 仍为 `error=apply_receipt_unknown, unknown=true`，控制回执已确认；当前事实未证明 apply 过去的结果。
2. 执行点位页面已有的命名预览对应 `local.action(() => ipc.previewNames(...))`。该预览返回合成已知成功后，实际 `error=null, unknown=false, dirty=false`；没有对原 apply 进行任何核对或确认。
3. 再调用保存，合成保存调用次数变为 1 且返回成功。脚本对“apply unknown 应继续保留”的断言 exit 1，输出 `false !== true`；这是有意检验的断言失败，不是应用 crash，也不宣称真实数据库已保存。

`useDeviceSimulator.ts:40,86-91` 中，`dirty` 不包含 `otherUnknown`；在不再有 `uncertainSave`/`uncertainControls` 时，普通非安全 `action` 先将 `otherUnknown=null` 并清空 `unknown`。点位页 `src/app/simulator/views/points/index.vue:80-82,182-183` 的命名预览禁用条件含 dirty/busy/选择，但不含 `unknown`；选择点后可进入上述真实状态/facade 路径。`save()` 在 `unknown=false` 后不再阻止提交。`other-unknown-reload.cjs`（SHA-256 `febfb5cf52d815b15a16537444783c1f1b0075687497aab49db1a29a1269d469`）独立复现“经已有明确确认的 Reload draft 后同样清除 apply unknown，接着保存被放行”，exit 1；读取草稿不足以证明之前 apply 的结果。HEAD 基线原先的通用 action 也会清空未知标志，因此本记录不把此行为全部归因于 DS-004 新增代码；但它与本次返工要求保留交错未知回执、避免未经核实解除配置修改冻结的合同冲突。应由 Development 判断合规修复与范围，QA 不静默修复；若超出 r1 allowlist，回 PM 处理。

### F4：保存关闭与并发未知预览释放（开放，返回 Development）

独立脚本 `/private/tmp/ds004-qa3.aymirQ/save-close-race.cjs`，SHA-256 `788f8b5d1b2ed1a617a1e6c80018f90e510427c8b3054dd28d27cd04f2df5a26`，使用正式 TS facade 与 Vue 状态、合成 invoke 边界和两个明确的异步屏障。先在本地草稿存在编辑时启动预览释放，再发起保存；`cancelPreview` 的未知响应在保存仍 in flight 时到达，记录为 `unknown=true`；随后合成保存已知成功并读回同一草稿。实际 `save()` 返回 `true`，但 `unknown=true`、`error=ipc_transport_unknown`、`dirty=false`。脚本对“存在另一个未知回执时保存关闭不应收到成功放行”的断言 exit 1；没有运行原生窗口或真实 IPC。

可达性依据：`instances/index.vue:93-96` 和 `ConfigRevisionBar.vue:37` 在组件卸载时以 `void local.releasePreview(...)` 异步释放，`useDeviceSimulator.ts:203-209` 的释放不受其他操作的 busy 门禁阻止，因此该读取/释放可与后续保存交错；`src/App.vue:56-59` 的保存关闭只检查 `local.save()` 的布尔值，返回 true 后立即发 `ds-close-decision=close`，没有再核对 unknown。`dirty` 不包含 `otherUnknown`，下一次普通关窗也不因此单独触发提示。真实 UI 的导航、关闭和 OS 调度尚未实测，故只认定正式代码路径及合成并发时序可复现，不宣称此轮原生窗口已关闭或真实 profile 已受影响。此时序会使仍未核实的内存记录因关闭而消失，与本轮未知回执保留/关闭保护要求冲突；返回 Development，修复需由 fresh-context QA 复核。

### 验收逐项与边界

| 项目 | QA3 独立结果 |
| --- | --- |
| DS4-01 | Rust 非 feature 3 项通过，覆盖闭合对象缺键/null/类型/多余键/UTF-8 边界、Unicode 原值及保存重开；Node 内存组件覆盖空/单侧和长度。真实原生编辑未测；整体受 F3/F4 影响。 |
| DS4-02 | Node 内存页面覆盖中英切换、空侧不回退、技术名及草稿/ETag 不变；未在真实顶栏检查持久 bytes、版本、loaded、source。 |
| DS4-03 | 合成旧字段和 TIA 测试支持旧 `displayName` 独立保留、不自动填双语/描述；中英文标注经 locale/组件检查。原生展示未测。 |
| DS4-04 | 新自有合成 profile 中，old create/read 和 new read exit 0，SQLite SHA 均为 `f28db01b6efbbd6602f29b661437953d543ef6e1b0b32db606869f40907aae45`；new 显式 upgrade 后 old reject 返回预期 `storage_payload`、exit 0，前后 DB SHA 均为 `9fc967af4a479d34a7c1d8ba0a9b2acc37777a542cb45e843bb32435bec7129a`。旧 probe SHA `70589d62bd2708f3c0a0276cfb5c86280473358e9e636bf086dcfc2d0e70eb4a`，构建来源依 DEV 记录，非独立签名证明；新 probe SHA `e6cddf5906edcadc1dd787cc209afba7c8c138830ce7d69e6def5d1f3506916a`。旧 archive 的更广检查仍见 QA1；本轮没有实测原生 actual_loaded。 |
| DS4-05 | 锁文件离线 Rust 合成回归覆盖同 ID 重导保留、不同 ID 隔离、layout/naming 预览、取消、stale ETag 和实例隔离；无真实 PLC、无 DS-003 JSON 导入导出。 |
| DS4-06 | Rust/Node 合成证据覆盖独立描述、清空、非法类型及 500 UTF-8 字节限制，旧字段不自动转换；原生两类点完整保存/重开未测。 |
| DS4-07 | **未完成：原生验证阻塞。** 本轮 Rust、Node、类型、构建及共享列宽工具测试不能证明真实 macOS 双语编辑、顶栏切换、拖动列宽、重启持久化/复位或普通 `pnpm tauri dev` 启动。 |

### 环境、命令和结果

macOS 15.7.7 / Darwin 24.6.0 arm64，rustc/cargo 1.89.0、Node v22.19.0、pnpm 11.11.0。除另示路径，工作目录为正式 `automation-world/device-simulator`；Cargo 使用项目锁文件及 `--offline`，所有 target、前端构建和新合成 profile 均指向本轮临时根。没有安装依赖；Vite 当前配置 `envDir: false`。本轮不读取或修改用户 `.env`、profile、设备或网络。

```sh
CARGO_TARGET_DIR=/private/tmp/ds004-qa3.aymirQ/cargo DS_TEST_RUN_ROOT=/private/tmp/ds004-qa3.aymirQ/rust cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test point_display_names --test configuration_store --test source_import --test versions --test owner_contract -- --nocapture > /private/tmp/ds004-qa3.aymirQ/rust.log 2>&1
# exit 0；20 passed，1 explicit compatibility probe ignored；包含真实 after_save_commit 服务故障注入。
CARGO_TARGET_DIR=/private/tmp/ds004-qa3.aymirQ/cargo DS_TEST_RUN_ROOT=/private/tmp/ds004-qa3.aymirQ/rust-no-feature-2 cargo test --manifest-path runtime/Cargo.toml --locked --offline --test point_display_names
# exit 0；3 passed，1 ignored。
DS4_FAULT_LOG=/private/tmp/ds004-qa3.aymirQ/rust.log node --test tests/*.test.mjs > /private/tmp/ds004-qa3.aymirQ/node.log 2>&1
# exit 0；35 passed，0 skipped。该套件为 Development 编写，本轮独立执行；本记录的额外 facade matrix/F3 是独立探针。
node /private/tmp/ds004-qa3.aymirQ/facade-matrix.cjs
# exit 0；save-first、controls-first 均通过，边界见上。
node /private/tmp/ds004-qa3.aymirQ/other-unknown-preview.cjs
node /private/tmp/ds004-qa3.aymirQ/other-unknown-reload.cjs
# 各 exit 1；F3 对保留未知回执的断言失败，边界及可见结果见上。
cargo fmt --manifest-path runtime/Cargo.toml --check
node node_modules/vue-tsc/bin/vue-tsc.js --noEmit
node node_modules/vite/bin/vite.js build --outDir /private/tmp/ds004-qa3.aymirQ/ui
# 三项各 exit 0；构建来自正式工作树，既有依赖 PURE 注释及大于 500 kB chunk 告警。
git diff --check -- runtime/src/domain/configuration.rs runtime/src/services/source_import.rs src/services/deviceSimulator.ts src/console/composables/useDeviceSimulator.ts src/app/simulator/views/points/index.vue src/app/simulator/components/PointEditor.vue src/app/simulator/locales/en-US.json src/app/simulator/locales/zh-CN.json src/styles/app.css USER_GUIDE.md USER_GUIDE.zh-CN.md CODE_INDEX.md
# exit 0。
git diff --no-index --check /dev/null runtime/tests/point_display_names.rs
git diff --no-index --check /dev/null tests/point-display-names.test.mjs
# 各 exit 1 因为新文件与 /dev/null 不同；均无 whitespace 诊断。
```

旧二进制 probe 路径为 `/private/tmp/ds-004-r1-dev.G6mp7M/cargo-old/debug/deps/point_display_names-f259d2b34ad19b3e`，本轮新 probe 为 `/private/tmp/ds004-qa3.aymirQ/cargo/debug/deps/point_display_names-f259d2b34ad19b3e`；均使用 `DS4_COMPAT_PROFILE=/private/tmp/ds004-qa3.aymirQ/compat` 以及 `--ignored --exact compatibility_probe --nocapture`。依次对 old 执行 `DS4_COMPAT_MODE=create`、old `old`、new `old`、new `upgrade`、old `reject`，五次均 exit 0；创建和升级仅针对该自有合成 profile。任务内新增文件头与 module `CODE_INDEX.md` 条目经审查；stdlib 相对文件链接扫描 41 项、0 缺失（未验证 anchors）；中英文 locale 叶子键均 490、集合一致，点位页/editor 的静态 key 和相关受控动态枚举无缺失。首次 key 扫描 exit 1，是 QA 正则误将动态前缀视作完整 literal，修正为完整函数调用并显式检查动态枚举后 exit 0；保留该检查修正事实。

写后历史审计最初两次因 QA 比较脚本对分隔符前换行的预期错误而 exit 1；将唯一顶部 handoff 恢复作比较后，QA1/QA2 旧内容与写前副本完整相同（最终比较 exit 0）。

### 原生 blocker、资源与 handoff

另一任务原生窗口退出后疑似重新启动或绑定至默认真实 DAA profile，影响未知；coordinator 明确暂停一切 GUI/CUA 启动或附着。本轮未启动 DS/DAA/窗口/CUA，也未申请 `require_escalated`。QA1/QA2 原生 blocker 历史保持不变。解除必须先调查事件并明确解除暂停，再在可证明独立的 macOS 用户或隔离环境中建立全新自有 profile、唯一 app/WebKit store 身份并核实 OS/XPC 数据落点；针对与正式候选一致的源码及普通入口验证真实编辑、顶栏、SQLite/ETag/版本/source/loaded 和列宽跨重启/复位。旧候选、临时快照与本轮构建均不能冒充该原生结果。

本轮自有 `/private/tmp/ds004-qa3.aymirQ` 保留合成 profile、日志、探针与离线构建，供返工和后续独立验证核对；DEV 的 `/private/tmp/ds-004-r1-dev.G6mp7M` 仍属 Development 资源。新 SQLite 仅在合成 profile 执行既有初始建库 DDL；没有对用户历史库执行 DDL/迁移。必要证据摘要已写入本 checklist；QA 不回收资源，待返工和后续 QA 不再依赖且 coordinator 核实归属、占用后处理。F3/F4 返回 Development；后续新候选须再 fresh-context Verification，QA 结论只交 Human Owner 决定最终验收。此 verdict 不授权现场、生产、DS-003/DAA-017 实施、发布或部署。

---

## QA4：DS-004 r2 fresh-context Verification（2026-11-17）

### 结论、身份与边界

**本轮 verdict：`qa_blocked`。** 本轮规定的非图形合成检查未发现新的确定性实现缺陷；DS4-07 必需的真实 macOS 原生编辑、顶栏、表列宽跨重启及普通入口回归和真实正常关闭/重开尚未执行。因另一任务的 DAA 原生隔离事故，coordinator 明确暂停全部 GUI/CUA/native 应用启动及附着，影响未知；不能用此轮内存 renderer、Rust 合成进程或构建冒称真实 WebView、Tauri IPC、窗口关闭或设备结果。QA1 F1、QA2 F2、QA3 F3/F4 的原始失败与 verdict 保留在上文；r2 排除了无保存直接交错的 HEAD 旧通用 F3，不声称修复了该通用行为。Human Owner 最终验收尚未发生。

本次由 coordinator 在 Development handoff 后实际调用 `verification`、`fork_turns="none"`，未继承 Development 的对话推理。独立阅读根 `AGENTS.md`、根及 AW/DS 最近作用域 README/PLAN、canonical workflow、verification 角色、完整任务 bundle、实现及 scoped diff 和可用测试输出；按触达面使用 `project-governance`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping`、`code-document-indexer`，只验证、不修复。角色为 `contract_only`，不声明平台 ACL、强制路由或自动执行。仅更新本 checklist 顶部当前状态和追加本节，未改 spec、tasks、实现、测试或项目配置。

正式未提交工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的 base HEAD 为 `21cd789277695bbafaa55c24e39261fc7247f9b0`。活动 spec `owner_approved` SHA-256 `c3e719d6373c70d4fe45df289a26cd83f104e88878b74693900f76533509c267`；Development `developer_handoff` tasks SHA-256 `3d9f21a1c276b8f7faa44b981f57b4a73d2195f77ce36d994b61981626452e23`；本次写前 checklist SHA-256 `057624c3e55f2a6ea4de896479c8140d499f6c0e21024eb2db7f6af3d7c7c5b9`。按 tasks 末尾顺序逐项核对 15 个完整文件，均与声明 SHA 一致；以 `SHA256  相对路径\n` 汇总的有序清单 SHA-256 `eeee96a3206739ae1de678166123d742d9d3a9e9d010d3f90fc36c92af70f257`。候选文件均在 r2 allowlist；完整文件锁定不代表共享文件每行差异均由本任务产生。其他并行脏改动未覆盖或回退，也不能凭本轮核验断定其历史归属。

### 逐项验收与限定证据

| 验收 | 本轮独立结果 |
| --- | --- |
| DS4-01 | **部分证据通过，原生未测。** 非 feature Rust 测试检查对象缺键/null/错类型/多键、UTF-8 字节边界与 Unicode；真实 PointEditor 在内存 renderer 检查单侧空、清空、取消与独立描述；合成 SQLite 保存/重开。 |
| DS4-02 | **部分证据通过，原生未测。** 内存真实点位页切中英文、空侧不回退，技术名与草稿/ETag 不变；未实测真实顶栏、持久 bytes、版本、loaded 和 source 的切换前后。 |
| DS4-03 | **合成证据通过。** 旧 `displayName` 在 old/new 读取和 TIA 合成重导中保留，不自动填新双语/描述；页面与配对文案区分无语言旧值。原生展示未测。 |
| DS4-04 | **合成证据通过，原生 loaded 未测。** 自建旧 profile：旧/新程序读取后整库 SHA 不变；另自建包含 2 个 revision 和 86 字节 source blob 的 profile，old/new 读取后整库 SHA `d00b74ec7254c8fd532efa710cef7ba2a574ceff4c0e5975e6b737d64368c3cb`，历史 payload/摘要、source bytes/摘要及 selection 不变。新程序显式升级后历史 bytes 和 selection 仍相同；旧程序安全返回 `storage_payload`，拒绝前后 DB SHA `9c3675efe5a6276190308d75658ae089f6285253e9e5ea18a5d4d33716882b25`，未误开空 profile。旧二进制 SHA `70589d62bd2708f3c0a0276cfb5c86280473358e9e636bf086dcfc2d0e70eb4a`，其旧源码构建身份依 DEV 记录，不是独立签名证明。 |
| DS4-05 | **合成证据通过。** Rust TIA 测试覆盖同 ID 重导与新/替换 ID 隔离、预览/取消、stale ETag 和其他实例；不是 JSON 导入导出或真实 PLC。 |
| DS4-06 | **部分证据通过，原生未测。** 合成 TIA/手工点、描述独立清空与保存、非法类型及 500 UTF-8 字节边界、旧字段/历史保留经 Rust 和内存组件检查。 |
| DS4-07 | **not_run，阻塞。** 真实 macOS 双语编辑、顶栏切换、拖列宽、跨正常重启恢复/复位和正式普通 `pnpm tauri dev` 未执行；Rust/Node/构建不替代它们。 |
| DS4-08 | **合成证据通过。** 一次满额保存：4096 点、5,926,517 bytes、每点双语各 256 bytes 和描述 500 bytes，`queries::save` 返回 `saved`、新 ETag `1afda2dc-9cff-481f-975c-218505330e63`；只读 SQLite `quick_check=ok`，payload SHA 与存储值均 `2a19e5db025d6365138a2b6cd6401fe8f72de5f587ec6d14a272489144bb8b97`。随后独立 helper 在该**已有非空合成库**提交 4097 点和 17,779,445-byte 工作区，分别 `point_capacity` / `configuration_capacity`；前后 workspace、ETag 和整库字节相同。一次成功不保证其他时序无未知回执；QA1 的较早未知样本继续保留。 |
| DS4-09 | **所测合成路径通过，范围有限。** 真实 Rust `after_save_commit` 返回 `save_receipt_unknown`、`committed=null`；同一 Store 串行 worker 的 `try_send` 在等待回执前，后续同 Store Load 在该 Save job 后，源码见 `runtime/src/infrastructure/config_store/mod.rs:87-88,117-147,209-215,252-256`。本轮显式屏障的服务故障 profile 同 Store Load ETag 由 `b344ea14-6321-4baa-a171-3ce1b26324c1` 变为 `466cd5a5-9b58-48b8-912b-5cdd7df412ae`。另一个本轮新合成 profile 构造已加载但停止的模拟实例并故障删除：正常 service 返回 `save_receipt_unknown` 后，同 Store 当前草稿无该实例，额外检查 runtime 实例已移除且无 cleanup error；这只证明该次故障的当前事实与该闭包收尾，Load 本身不证明一般删除收尾或原请求成败。`save_commit_unknown`、runtime-task JoinError 与 invoke 断连在 JS 边界分别合成，非实际 commit 故障/真实 JoinError/真实 IPC。原 ETag、输入及确认 ID 保留；读失败、ETag 变化、编辑及 cleanup 未证的冻结见本轮测试。 |
| DS4-10 | **合成屏障通过。** 对真实 TS facade 和 composable 分别模拟 invoke 拒绝及 runtime-task unknown，在两次相同当前读取后才放行原合成保存的迟到副作用；两种路径均仍 unknown、冲突保存被阻止，保存调用始终 1 次，原 `v0`、点 ID 与本地输入保留。不是固定延时、实际 Tauri JoinError 或真实 IPC 证明。 |
| DS4-11 | **合成证据通过。** Rust `confirmPoints` 实例真实 prepare 在故障后使命名/地址确认失效并重新计算初值/策略签名，双语和描述不丢；独立 facade/state 探针分别检查 `save_commit_unknown` 差异读取及已知成功的不同候选：未伪报失败，合法空格/Unicode 保留；读取在途继续编辑时不覆盖、不解冻。明确比较后选择重读及其丢弃提示、失效 ETag 由内存测试与源码复核。 |
| DS4-12 | **合成证据通过。** 独立真实 facade/state：save unknown → stop unknown → pause 已知拒绝 → 显式核对保存，stop 的实例、动作与 unknown 仍保留，输入不变，原保存一次；改变运行 epoch 后控制确认被拒。必要 stop 在保存 unknown 待核对状态可发出。读取当前控制事实不证明过去操作的成败。 |
| DS4-13 | **单窗口内存证据通过，原生未测。** 编译并渲染真实 `App.vue` 模板、实际 composable 与 facade，合成 release/save 双屏障：已知保存成功和释放 unknown 分开可见，不自动 emit close；门禁内新释放显示“尚未发送”，取消后才发出；取消保留 unknown，用户显式放弃后才 emit。另有既有内存测试覆盖事实变化后二次确认及 emit 失败。仅证明测试中的前端跟踪边界，不声明跨 IPC、原生退出或崩溃原子性。 |
| DS4-14 | **合成部分通过，真实正常关闭/重开未测。** transport/runtime-task 无终结证明时两次相同读取与人工确认均不能解冻或重试；本窗口记录有丢失提示。自有合成子进程测试证明存活时锁冲突，正常退出后重取锁并核对同一 profile UUID `52594137-fabe-4c6b-aae5-5304aa6611a3`。错误身份、缺少输入、读取失败、实际关闭失败/崩溃/强退不声称安全恢复；真实原生退路未验证。 |
| DS4-15 | **部分证据通过，整体随原生阻塞。** 中英文 locale 各 524 叶键、键集一致；App/点位页/editor 所查静态及受控动态 key 无缺失；点位表复用稳定 `configuration.points` 公共列宽键，未实测原生持久化/复位。未接触真实 profile、设备、网络或 DS-003/DAA-017。 |

### 命令、环境与真实结果

macOS 15.7.7 / Darwin 24.6.0 arm64，rustc/cargo 1.89.0、Node v22.19.0、pnpm 11.11.0；工作目录为正式 `automation-world/device-simulator`。本轮新目录 `/private/tmp/ds004-r2-qa.ZaSm1T` 中的 target、profile、日志和 Vite 产物均自有；Cargo 使用锁文件和 `--offline`。未安装依赖，正式树 Vite 配置 `envDir: false`。新建合成 SQLite 使用项目现有初始建库 DDL；未对任何现有用户库执行 DDL/迁移。

```sh
CARGO_TARGET_DIR=/private/tmp/ds004-r2-qa.ZaSm1T/cargo DS_TEST_RUN_ROOT=/private/tmp/ds004-r2-qa.ZaSm1T/rust cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test point_display_names --test configuration_store --test source_import --test versions --test owner_contract -- --nocapture > /private/tmp/ds004-r2-qa.ZaSm1T/rust.log 2>&1
# exit 0：24 passed，2 显式 ignored；rust.log SHA b8e02651877eb291a4c7de7b3b691aec6f7679161d9f641fadb9b59133e937a4
CARGO_TARGET_DIR=/private/tmp/ds004-r2-qa.ZaSm1T/cargo DS_TEST_RUN_ROOT=/private/tmp/ds004-r2-qa.ZaSm1T/no-feature cargo test --manifest-path runtime/Cargo.toml --locked --offline --test point_display_names > /private/tmp/ds004-r2-qa.ZaSm1T/no-feature.log 2>&1
# exit 0：5 passed，2 显式 ignored
DS4_FAULT_LOG=/private/tmp/ds004-r2-qa.ZaSm1T/rust.log node --test tests/*.test.mjs > /private/tmp/ds004-r2-qa.ZaSm1T/node.log 2>&1
# exit 0：48 passed，0 skipped；这些是本轮实际独立执行的 DEV 测试，非 DEV 自检冒充 QA
cargo fmt --manifest-path runtime/Cargo.toml --check
node node_modules/vue-tsc/bin/vue-tsc.js --noEmit
node node_modules/vite/bin/vite.js build --outDir /private/tmp/ds004-r2-qa.ZaSm1T/ui
# 各 exit 0；Vite 有现有依赖 PURE 注释及 >500 kB chunk 警告
node /private/tmp/ds004-r2-qa.ZaSm1T/independent-ui2.cjs
node /private/tmp/ds004-r2-qa.ZaSm1T/stop-interleave.cjs
node /private/tmp/ds004-r2-qa.ZaSm1T/prepared-interleave.cjs
# 各 exit 0；正式 facade/state/真实 App 模板 + 合成 invoke/event 和显式屏障，非 GUI
```

独立 Rust helpers 编译用 `rustc --edition=2021`、本轮 `cargo/debug/deps` 的 `ds_runtime` 和 `serde_json`、本轮 `cargo/debug/build/ds-runtime-3a1f1c5c1ca3d4db/out/native` 链接路径；运行时将 `DYLD_LIBRARY_PATH` 指向该目录。`reject_after_save.rs` 和 `removal_fifo.rs` 编译、运行各 exit 0；前者在本轮满额合成 profile 上只发送两次无效请求，后者使用全新 `removal-profile` 和非默认故障点。前者的首次 helper 编译因 QA 脚本借用冲突退出 1，修正后第二次因缺 `-L native` 链接退出 1；补全路径后成功，均未改产品。`independent-ui2.cjs` 首次断言误取在途队列第 0 项而非 deferred 项 exit 1，按 token 取项后 exit 0；是 QA 探针修正，不隐藏初次结果。合成 profile 发现扫描对 3 个既有回归中故意构造的损坏/无 schema 夹具给出 sqlite 错误；目标满额 profile 的只读校验成功。

旧/new 兼容探针均只指向本轮新建 `compat` 和 `compat-archive`：old/create、old/old、new/old、new/upgrade、old/reject 依次 exit 0；附加旧 source archive helper 仅指向后者，exit 0。旧 probe 使用 Development 留存的旧二进制，新 probe 使用本轮离线构建的 no-feature 二进制；新 probe SHA `1d969d62e5fbee90ddbcd23d1969e72a24d1a831e859dd0e0421bc5cf151c8f0`。只读 sqlite 查询重新计算历史 revision/source 散列，并比较保存的原始字节与 selection。无任何旧/新测试二进制使用用户 profile。

`git diff --check -- <13 个 tracked 候选文件>` exit 0；两新增测试 `git diff --no-index --check /dev/null <file>` 各 exit 1 表示文件与空文件不同，均无 whitespace 诊断。两份指南与 `CODE_INDEX.md` 的相对文件链接检查 41 项、0 缺失，anchors 未检查。探针 SHA：`independent-ui2.cjs` `988082ad25bf08f2fbe1e806c013109f7d9c819e1d6db9dfb9afeecb93f5f3e0`；`stop-interleave.cjs` `b0d37e2c0ea9c9e61594d1370cea99feda550583529ae19719d5c2b1db6ad25f`；`removal_fifo.rs` `926572daafcd92bd156f7636324c42b35cacb15c91db30163a35c4b9364537be`；`reject_after_save.rs` `c5520690848c01aa353357a4178c08a1832f11699d93b97982e13aae673469a0`。

### Blocker、解除条件和 handoff

此次未启动、附着任何 GUI/CUA、DS/DAA 原生应用窗口，未读取或修改用户 `.env`、真实 profile、设备、真实数据库或网络，也未调查、检查或回滚另案疑似真实记录。先由 coordinator/Owner 调查隔离事件并明确解除暂停，再证明独立 macOS 用户或隔离环境、全新自有合成 profile、唯一应用/WebKit 身份及 OS/XPC 实际数据落点；之后针对与正式交付一致的精确候选及普通入口执行 DS4-07 的原生编辑、顶栏、SQLite/ETag/版本/source/loaded、列宽跨正常重启与复位，以及安全正常关闭/重开。解除前不能把未测项写成通过或 deferred complete；若候选改变须重新锁定并 fresh Verification。

本轮 `/private/tmp/ds004-r2-qa.ZaSm1T` 为 QA 自有，含隔离 target、构建、脚本和合成 profile；`/private/tmp/ds-004-r1-dev.G6mp7M` 为 Development 既有资源，旧二进制仅供兼容对照。关键命令、结果和边界已持久化于本 checklist，QA 不清理；待后续核验不再依赖并由 coordinator 核实归属、占用后回收。此 `qa_blocked` 与证据 handoff 给 Human Owner 知悉并决定解除条件；后续必需 QA 完成后方进入 Human Owner 最终验收。未授权真实 profile、设备、JSON 导出/导入、生产、发布或部署。

---

## 协调者前置配置探针（2026-11-17，Asia/Shanghai）

本节仅记录 coordinator 向本 Verification 提供的探针事实，**不是本 Verification 独立执行或复现的测试，也不是新 QA verdict**。原 `qa_blocked`、QA1–QA4 历史、原生暂停及全部解除条件不变。

协调者报告：在 Human Owner 授权的 DS 自有 `.local` 唯一临时根，复制当前 `src-tauri/src/config/bootstrap.rs`；副本及正式源码 SHA-256 均为 `d4341e8a909d15666b389c3928daf31d2a18e7b5b8c8b37ea239db0f8b451d4f`。用 `rustc --edition=2021` 构建临时 harness，将 `CARGO_MANIFEST_DIR` 指向该快照的 `src-tauri`，链接保留的 QA4 无 `test-automation` runtime 库 `libds_runtime-f3dc85d8b60c292c.rlib` 和 serde，调用复制源码的真实 `bootstrap::load`。协调者报告该测试没有启动 GUI 或产品原生应用，也没有访问数据库、真实 `.env`、真实 profile、设备或网络。

| 协调者报告的输入 | 结果 |
| --- | --- |
| 自有 `.env` 指向自有 profile，进程无覆盖 | exit 0，选择自有 profile。 |
| 进程 `DS_PROFILE_DIR` 覆盖 | exit 0，进程值覆盖生效。 |
| 无效相对路径 `../outside` | exit 2，`profile_absolute_required`。 |
| 自有 `.env` 缺失 | exit 0，回落到自有测试 default sentinel。 |
| 自有 `.env` 是空文件 | exit 0，回落到自有测试 default sentinel。 |
| 自有 `.env` 是符号链接 | exit 2，`env_regular_file_required:DS_PROFILE_DIR`。 |

六项与该探针的预期一致；缺失或空文件的两项**实际发生回落**，不能写成拒绝或 fail-closed。协调者报告临时根清理状态为 `true`。协调者补充的完整编译命令如下；`$RUN_DIR` 代指已清理且未记录绝对路径的自有临时根：

```sh
CARGO_MANIFEST_DIR="$RUN_DIR/snapshot/src-tauri" rustc --edition=2021 "$RUN_DIR/bootstrap_probe.rs" --extern ds_runtime=/private/tmp/ds004-r2-qa.ZaSm1T/cargo/debug/deps/libds_runtime-f3dc85d8b60c292c.rlib --extern serde=/private/tmp/ds004-r2-qa.ZaSm1T/cargo/debug/deps/libserde-bdd9a14844d5283f.rlib -L dependency=/private/tmp/ds004-r2-qa.ZaSm1T/cargo/debug/deps -L native=/private/tmp/ds004-r2-qa.ZaSm1T/cargo/debug/build/ds-runtime-3a1f1c5c1ca3d4db/out/native -o "$RUN_DIR/bootstrap_probe"
```

协调者报告运行时清空进程环境，再设置 `PATH`、`DYLD_LIBRARY_PATH`，并按用例设置或移除 `DS_PROFILE_DIR`；默认路径使用自有 `$RUN_DIR/own-default`。未提供环境变量的具体值，且没有保留完整运行日志；本 Verification 未重新运行探针，也未独立检查其清理情况。本 Verification 只读重核了正式 `bootstrap.rs` 的上述 SHA。

该 harness 是临时配置探针，并链接既有 runtime rlib；它不是 Tauri 正式入口或原生应用启动，不证明 WebKit/XPC 身份及落点、异常重启、CUA 窗口与进程绑定、真实 GUI 或正常关闭/重开。此前 DAA 隔离事件的未知影响不变。DS4-07 及相关原生 gate 继续 `not_run`，最终验收仍由 Human Owner 决定；未实施 DS-003 / DAA-017 导出或导入。

---

## 协调者精确 PID 哨兵探针（2026-11-17，Asia/Shanghai）

本节是 coordinator 报告的有限探针事实，**不是本 Verification 独立执行或复现，也不是 DS / DAA 原生 QA 或新 verdict**。协调者仅为自有哨兵暂时解除 GUI 暂停；对真实 DS / DAA 的 GUI、CUA、native 启动和附着暂停，以及既有 `qa_blocked`、原生 gate 和全部历史继续保留。

协调者报告：在 DS `.local` 随机自有子目录建立无 DS / DAA 代码和数据的随机 bundle AppKit 小窗，经 `sandbox-exec` 直接执行；所用策略配置为禁止全局文件写入、禁止用户目录及临时目录读取，唯一自有根放行，并禁止网络。同一经 auto-review 的 Python 父进程报告 `AXIsProcessTrusted=true`，`SIGCHLD=SIG_DFL` 且 `SA_NOCLDWAIT=false`。父进程强持有唯一子进程的 `Popen`，AX 操作期间没有调用 `poll` / `wait`；哨兵通过自有管道回报随机标题、bundle ID 和 PID，父进程以 `proc_pidpath` 核对自有二进制。此次 child PID 为 `85299`。

协调者报告只使用 `AXUIElementCreateApplication(child_pid)` 定位应用；所取 app、window、button 和 close button 的 `AXUIElementGetPid` 均与 child PID 一致。在自有 window 的标题及角色匹配后，对自有按钮单次 `AXPress` 并观察到随机标题变化；随后对自有 close button 单次 `AXPress` 返回成功。未使用 CUA、系统级 AX、全局按键、按名称查找或关闭后重查；未启动 DS / DAA、真实设备或发起真实网络 POST。以上均是协调者报告，本 Verification 未独立核查哨兵、策略、执行链或操作结果。

协调者说明，close button 返回成功后，脚本立即向仍未回收的唯一 child 发送 `SIGTERM` 并 `wait`，所得退出结果为 `-15`。因此不能由此声称已观察正常退出、锁释放或重启，也不能把动作返回成功当作关闭全过程完成的证明。协调者报告自有 `.local` 测试根已删除，以该唯一 PID 精确匹配的系统诊断清理数量为 0；本 Verification 未独立检查清理。`85299` 仅为当次历史 PID，不构成当前进程身份或操作依据。

随机 bundle ID、自有根的实际值和完整原始日志未持久保存，故当前无法从本记录独立复现或审计原始输出。公开的本机 ApplicationServices 头文件将 `AXUIElementCreateApplication` 定义为取得指定 PID 的应用对象，将 `AXUIElementGetPid` 定义为取得元素关联 PID；它们本身不能证明 sandbox、WebKit / XPC 或系统缓存的归属。本次协调者探针最多支持其报告的当次 PID 约束哨兵操作；没有验证 DS / DAA 原生入口、真实 WebKit store、进程正常关闭与同 profile 重开，也没有解除 DS4-07 或隔离 blocker。Human Owner 最终验收仍未发生。

---

## 协调者 WebKit 前置探针（2026-11-17，Asia/Shanghai）

本节记录 coordinator 提供的自报事实，**不是本 Verification 独立执行或复现，也不是 DS / DAA 原生 QA 或新 verdict**。随机测试 app 不含 DS / DAA 代码或配置。原 `qa_blocked`、既有历史、真实应用原生 / GUI / CUA 暂停、隔离 blocker 和用户数据边界不变。

1. 协调者报告，对自有随机测试 app 直接调用 `fetchAllDataStoreIdentifiers` 两次，分别在严格目录 / 网络限制和 `allow default` + 禁止网络的对照条件下发生 `SIGSEGV`。第二次系统诊断所记录顶层符号包含 `WTF::RunLoop::dispatch`；此符号本身不证明崩溃根因。协调者报告两个自有 `.local` 测试目录分别已删除，并按可核随机程序名、PID 和异常精确匹配，各清理一份系统诊断报告；本 Verification 未独立核查这些报告、匹配或清理。
2. 协调者报告，改为预先构造 nonPersistent `WKWebView` 并完成空白 HTML 加载后，同一接口返回，进程 exit 0；自有根已清理，无该次诊断。本 Verification 未独立复现；这一观察不证明持久 store 行为。
3. 协调者报告，在上述预热后采用严格目录及网络规则，对新自有 UUID 的预查输出 `EXISTS 0`；调用 `dataStoreForIdentifier` 后，实际 `WKWebView` 的 identifier / isPersistent 检查输出 `STORE_MATCH 1`，同一 WebView 中 `localStorage` 读回成功。同时 stderr 显示写入其 Cookies 路径时 `Operation not permitted`；进程退出后再查输出 `EXISTS 0`，未执行重开。对该事前查不到的自有 UUID 调用异步删除，回调报告成功，随后枚举输出 `AFTER_REMOVE 0`。这不能证明跨进程持久化，也不能说删除了一个已持久 store。协调者报告该次唯一自有测试目录已清理，无该次诊断；本 Verification 未独立检查。

上述输出及清理范围均依协调者报告；本次 handoff 未提供各测试的随机程序名、PID、UUID、完整命令和原始日志，不能据此独立复核具体运行或清理。`allow default` 对照不等于只允许访问自有目录，本记录不能证明系统服务或用户目录不存在其他读写，也不声明零写。

当前所报结果仅表明：在禁止用户目录写入的该合成路径上，尚不能证明持久化；同一 WebView 中的读回不等于退出后的持久化。不能将其外推为实际 DS / Wry 的 OS 落点、真实原生行为或一般性故障。DS4-07、真实 WebKit / XPC 落点及正常关闭 / 同一 profile 重开继续未完成，Human Owner 最终验收仍未发生。

---

## 协调者 WebKit 受限持久化补充探针（2026-11-17，Asia/Shanghai）

本节仅记录 coordinator 提供的自报事实，**不是本 Verification 独立执行或复现，也不是 DS / DAA 原生 QA 或新 verdict**。原 `qa_blocked`、既有历史、真实应用原生 / GUI / CUA 暂停、隔离 blocker 和用户数据边界不变。

协调者报告：使用唯一随机 bundle 和 UUID，先确认自有 UUID 不存在，并确认该 app 独占的系统 WebKit 子目录和系统临时子目录此前不存在。所用 sandbox 配置除 `.local` 自有根外，只放行上述两个新目录，并禁止网络；该描述不独立证明 WebKit XPC 或其他系统服务继承该限制。页面通过 `loadHTMLString` 使用合成 `https://qa.invalid/` baseURL；本次未运行 DS / DAA。该 baseURL 不作为实际网络请求是否发生的证据。

| 协调者报告的步骤 | 结果及边界 |
| --- | --- |
| nonPersistent WebView 预热后 inspect | exit 0，`EXISTS 0`。 |
| 创建 store 并同进程检查 | exit 0，`STORE_MATCH 1`、`VALUE_MATCH 1`。 |
| 后续独立进程 inspect | exit 0，`EXISTS 1`；协调者据此判断 store 对象已落盘 / 可跨进程枚举。本 Verification 未独立核查具体文件落点。 |
| 独立进程 reopen | exit 5，`STORE_MATCH 1`、`VALUE_MATCH 0`；数据跨进程保留未获证明，不能将该合成探针结果归为真实 DS 缺陷。 |
| 相关 app 退出后调用官方删除 API，再由另一进程 inspect | 删除回调报告成功，后续输出 `AFTER_REMOVE 0`；不由此推断 WebKit / XPC 的所有外围缓存或系统写入均已清除。 |

协调者报告该随机 app 的两个自有系统目录和 `.local` 临时根均已清理成功，本次无系统诊断；本 Verification 未独立检查清理。本次 handoff 未提供随机 bundle / UUID、目录绝对路径、完整命令及原始日志，故不能由本记录独立复核运行和归属。

此结果区分了 store 标识在后续进程中可枚举与其中的数据在后续进程中保留；`VALUE_MATCH 0` 是本次合成探针的真实非零结果，原因未确定。它不证明 DS 普通入口、真实 WebKit / XPC 落点、列宽跨重启、正常关闭或同一 profile 重开。以上仍须在满足现有隔离条件后验证；Human Owner 最终验收未发生。

---

## 协调者 HTTP WebKit 合成探针（2026-11-17，Asia/Shanghai）

本节仅记录 coordinator 提供的自报事实，**不是本 Verification 独立执行或复现，也不是 DS / DAA 原生 QA 或新 verdict**。原 `qa_blocked`、全部历史、真实应用原生 / GUI / CUA 暂停、隔离 blocker 和用户数据边界不变。

协调者报告，初次使用错误的 numeric `remote ip` 沙箱语法，进程 exit 65，未创建 store；随后关闭该次自有服务并清理目录。调整为 `localhost:端口` 后，自有 C 子进程在所测条件下访问唯一允许的 loopback 端口 exit 0；访问其他所测 loopback 端口收到 `EPERM`、exit 10。这只说明所测子进程及端口的观察，不证明 WebKit XPC 或其他系统服务继承同一限制。

协调者报告，唯一随机 app / UUID 在测试前不存在；sandbox 将该 app 的 WebKit 目录、系统临时目录及 `.local` 自有根作为数据目录放行。页面由自有本机 HTTP 服务提供静态内容，不含外部资源；未运行 DS / DAA。

| 协调者报告的步骤 | 结果及边界 |
| --- | --- |
| 初次 inspect | exit 0，`EXISTS 0`。 |
| 创建 store 并同进程检查 | exit 0，`STORE_MATCH 1`、`VALUE_MATCH 1`。 |
| 另一进程 inspect | exit 0，`EXISTS 1`。 |
| 另一进程 reopen | exit 5，`STORE_MATCH 1`、`VALUE_MATCH 0`；未证明数据跨进程保留，不归因真实 DS。 |
| 按 UUID 调用系统删除 API | 协调者报告删除完成，后续输出 `AFTER_REMOVE 0`；不能据此断言所有外围系统缓存或写入均已清除。 |

协调者报告自有 HTTP 服务已关闭，两个系统目录和 `.local` 自有根已清理，且无本次诊断；本 Verification 未独立检查运行或清理。本次 handoff 未提供随机 app / UUID、端口、目录绝对路径、完整命令和原始日志，不能据此独立复核具体运行或资源归属。

本次合成实验中，store 标识在另一进程可枚举，但重开返回 `VALUE_MATCH 0`，因此仍未证明数据跨进程持久；原因未确定，不能将其外推为实际 DS 的缺陷或 OS 落点。DS4-07、真实 WebKit / XPC 隔离及正常关闭 / 同一 profile 重开仍未完成；Human Owner 最终验收未发生。

---

## 协调者同源 HTTP WebKit 补充探针（2026-11-17，Asia/Shanghai）

本节仅记录 coordinator 提供的自报事实，**不是本 Verification 独立执行或复现，也不是 DS / DAA 原生 QA 或新 verdict**。原 `qa_blocked`、全部历史、真实应用原生 / GUI / CUA 暂停、隔离 blocker 和用户数据边界不变。

协调者报告，实验使用自有本机 HTTP loopback，除 `.local` 自有根外仅放行两个事前不存在的自有系统目录，并采用只允许一个端口的网络策略。所测允许端口返回 exit 0，其他所测 loopback 端口返回 `EPERM`、exit 10；这一观察不单独证明 WebKit XPC 或其他系统服务继承了同一限制。

创建时使用真实 origin `http://127.0.0.1:<自有端口>`，报告 `STORE_MATCH 1`、`VALUE_MATCH 1`。随后协调者显式释放该 WebView 并等待 5 秒，inspect 返回 `EXISTS 1`；自有 WebKit 目录内只观察到 MediaKeys salt 文件。相同 origin 的另一进程 reopen 返回 exit 5，JavaScript 回报 `value:null`。因此本次合成实验仍未证明数据跨进程持久化；等待 5 秒本身不证明写入已完成，具体原因未确定，不能将其归因于真实 DS 缺陷。

协调者报告，按 UUID 的删除回调和后续 `AFTER_REMOVE 0` 均成功；独有 WebKit / 系统临时目录、`.local` 自有根及本机服务均已清理或关闭，本次无诊断。删除结果不能证明所有外围系统缓存或写入均已清除；本 Verification 未独立核查运行或清理。本次 handoff 未提供实际端口、UUID、目录绝对路径、完整命令和原始日志，不能据此独立复核具体运行或资源归属。

该实验不验证 DS 普通入口、真实 WebKit / XPC 隔离、列宽跨重启、正常关闭或同一 profile 重开。DS4-07 及相关原生 gate 仍未完成；Human Owner 最终验收未发生。

---

## 协调者 Unix IPC 同源探针及只读评估（2026-11-17，Asia/Shanghai）

本节分别记录 coordinator 的自报事实及本 Verification 的 SDK 源码只读判断；**不是本 Verification 独立执行或复现的测试，也不是 DS / DAA 原生 QA 或新 verdict**。原 `qa_blocked`、全部历史、真实应用原生 / GUI / CUA 暂停、隔离 blocker 和用户数据边界不变。

协调者报告，本次策略与前次 `deny network*` 不同：阻断 TCP / UDP 进出，仅放行自有 loopback TCP 端口，同时允许 Unix IPC。所测自有 TCP 端口 exit 0，其他所测 loopback TCP 端口返回 `EPERM`、exit 10，Unix socket 检查 exit 0。该结果不证明 WebKit 的 Mach / XPC 服务、文件访问或其他进程继承同一沙箱限制。

协调者报告，两阶段使用同一 `http://127.0.0.1:<自有端口>` origin，实际 WebView store 均输出 `STORE_MATCH 1`；create 输出 `VALUE_MATCH 1`。随后将 WebView 释放并等待 5 秒，store inspect 输出 `EXISTS 1`；自有 WebKit 目录内只观察到 MediaKeys salt 文件。新进程 reopen 输出 `VALUE_MATCH 0`，JavaScript 返回 `value:null`，进程 exit 5。系统 remove callback 后输出 `AFTER_REMOVE 0`；唯一 WebKit / 系统临时目录、`.local` 自有根和两项自有服务均已清理或关闭，本次无诊断。以上均为协调者报告，本 Verification 未独立检查运行、目录或清理；不能据单个目录观察断定其他落点不存在，也不能把 `value:null` 归因于真实 DS 缺陷。

协调者进一步描述该已清理、未留 SHA 的 harness 核心逻辑：先以 nonPersistent `WKWebView` 加载 Warm HTML，在 `didFinishNavigation` 后将 delegate 和 view 引用置空；create / reopen 分别新建配置，先将 `websiteDataStore` 设为 `dataStoreForIdentifier:self.sid`，再以该配置初始化待测 WebView。报告检查待测 view 的 `configuration.websiteDataStore.identifier` 和 `isPersistent`，经 `loadRequest` 访问同一端口并在导航完成后执行 JavaScript；create 对 `localStorage` 写入并读回 `own`，reopen 读取同一 key 返回 null。JavaScript completion 后将 delegate 和 `self.view` 置空，5 秒后请求 `NSApp` 结束；create 进程报告 exit 0。原源码、二进制和完整输出未随交接提供，不能独立复核实际错误处理、对象引用或执行时序。

本 Verification 只读核对本机 `WKWebView.h:103–115`：初始化时复制传入配置，之后再修改配置不会影响该 WebView。若实际实现与协调者描述一致，先设置 store 再初始化、检查待测 view 的 identifier / isPersistent，减少了误用预热 nonPersistent store 或配置设置过晚的可能；报告的相同 origin、导航完成和同 key 读回也减少了简单 origin 不同的可能。`isPersistent` 表明 store 类型，不是写入已落盘的证明；将单个引用置空未证明所有强引用已释放，固定等待 5 秒也不是持久化屏障。交接未说明 WebView 是否附着于窗口，本机 SDK 未表明未附着窗口必然使用纯内存，不能据此判定原因。

一个可控的后续方法是：在无真实用户数据和共享用户目录、且已获相应授权的隔离 macOS 用户会话或 VM 中，以不显示窗口的同一重建 harness、相同 OS / 应用身份 / origin 和自有 loopback 服务、禁止对外网络，分别用目录权限宽松正对照及当前严格规则、各自唯一 UUID 做跨进程对比。除导航和 JS 结果外，记录有效 bundle 身份、待测 view 的 store identifier / isPersistent、JS error、正常进程退出及弱引用释放，并可等待 `fetchDataRecordsOfTypes` 针对 `WKWebsiteDataTypeLocalStorage` 的回调作为补充观察；该回调不应冒称磁盘同步证明。正对照通过且严格规则失败，才支持继续调查限制条件的影响；正对照也失败时仍须审查 harness 或环境。该建议未执行，不修改既有 gate；任何合成结果都不能代替 DS 正式入口、真实 WebKit / XPC、列宽跨重启或正常关闭 / 同一 profile 重开验证。Human Owner 最终验收未发生。

---

## 协调者 WebKit 同用户持久化成功探针（2026-11-17，Asia/Shanghai）

本节仅记录 coordinator 提供的自报事实，**不是本 Verification 独立执行或复现，也不是 DS / DAA 原生 QA 或新 verdict**。原 `qa_blocked`、全部历史、真实应用原生 / GUI / CUA 暂停、隔离 blocker 和用户数据边界不变。

协调者报告，在当前 macOS 用户下使用无 DS / DAA 代码或配置的随机唯一 bundle、UUID 和自有 `.local` 根。sandbox 策略禁止读取 `/Users` 等非任务目录的文件数据和全局写入，仅放行自有 `.local` 根以及事前不存在的随机 bundle 专属 WebKit、Caches、HTTPStorages、Application Support、系统 temp / cache 目录与专属 prefs；网络仅允许自建 localhost TCP 端口和 Unix IPC。协调者报告实际权限 canary：自有文件读 exit 0；受保护文件读取及经符号链接读取均 exit 10；其他路径 `stat` exit 0，仅证实所测 metadata 可获取；自有 TCP exit 0、其他所测 TCP 返回 `EPERM` / exit 10，Unix socket exit 0。这些是所测条件下的结果，不独立证明 WebKit XPC 或所有系统服务均继承主进程规则，也不据此声称无系统 metadata 访问。

协调者报告，nonPersistent WebView 预热后，自有 UUID 初查不存在；实际测试 `WKWebView` 的 identifier / isPersistent 符合该自有 UUID。经自有 HTTP origin 写入后等待 5 秒，`fetchDataRecords` 的 LocalStorage 检查输出 `LOCAL_RECORDS 1`；释放 view 后用弱引用确认 `VIEW_RELEASED 1`，再等待 5 秒。协调者报告自有 UUID 的 `Origins` / LocalStorage SQLite 文件实际出现；另一个独立进程以相同 UUID 和 origin 重开后输出 `VALUE_MATCH 1`，正常 exit 0。因此该次**合成测试**支持该条件下的 localStorage 跨进程读回，不证明 DS 正式 app 的存储、关闭或重启。

协调者报告，按唯一 UUID 的系统删除 API 回调成功、后续枚举不再存在；六个专属系统目录和 `.local` 测试根均已清理。本 Verification 未独立核查执行、归属或清理；该次交接未单独给出专属 prefs 是否产生及其清理明细，删除回调也不能证明所有外围系统服务或缓存均无残留。

本次 harness SHA-256 为 `50287defeed59ef317f4ebf8a106c16f8ff91ceb6866e2966dc8f8e12b39b393`，sandbox policy SHA-256 为 `508a43b67834f262955b3b0319048ff9603fb4c7a24c4b47b144511ab8667040`，均为协调者提供；本 Verification 本次未收到并核算原文件。本次交接未提供可独立审计的完整命令、原始输出、实际 bundle / UUID、端口及资源绝对路径；不能仅凭哈希重建测试。

本次相较失败探针同时改变了 metadata 权限、额外自有系统目录和 WebView 生命周期，不能将成功归因于其中任何单一因素，也不撤销先前失败事实。该结果为后续当前用户环境的隔离方案提供增量，仍不能代替 DS 普通入口、实际应用和 WebKit / XPC 身份及落点、DS4-07 原生界面、同一 profile 的正常关闭 / 重开及其他现行 gate。Human Owner 最终验收未发生。
