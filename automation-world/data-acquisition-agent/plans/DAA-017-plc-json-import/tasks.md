Task ID: DAA-017
Revision: r5
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-017 Development 记录

## 批准与工作基线

2026-11-17（Asia/Shanghai）开始实施 `aiis-ics-arch::DAA-017 r4`。已读取精确批准记录，批准登记后 `spec.md` SHA-256 为 `005312642152ee1c0a9bcc9a351171069ddd32121dc074bc7ca55091ebceecaf`；父设计为 ARCH-PLC-001 r5，相关导出任务为 DS-003 r4。交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD 为 `21cd789277695bbafaa55c24e39261fc7247f9b0`；开始时工作树已有大量任务外改动，DAA-018 r3 双语候选也已存在。不得回退或归属这些既有改动。

计划：严格解析和验证真实 JSON 原字节；通过预览、ETag 和一次事务新建 PLC 及可重验目录来源；保护目录身份并保留现有双语流程；再完成受控测试、双语手册及精确交接。联测由主协调统一调度；不连接真实设备、不发送真实 POST。

## 已报告的编辑链缺口

现有 `src-tauri/src/services/local_point_naming.rs` 未列入 r4 allowlist；其 `candidate` 对确认地址只接受 `manual` / `inferred`，而本任务目录地址须为 `catalog`。现有单点编辑走该预览，因此未经修正会阻断目录点的双语、comment 等编辑。已向协调者报告并请求 PM 判断，暂不修改白名单外文件；继续核对其他链路并只在已批准范围内开展独立工作。此记录不是完成或验证结论。

## r5 精确批准及接续

Human Owner 于 2026-11-17 明确回复“批准两个 r5”，PM 已登记本任务 r5；登记后 `spec.md` SHA-256 为 `daa1735f7d8f70c27bae67fd979e5012906592391aaa476db152a1e6763f44e1`。r5 在 r4 基础上仅增加 `src-tauri/src/services/local_point_naming.rs` 和 DA17，保留 r4 批准和上述缺口发现的真实时序。现在按 r5 接续并修复该编辑链，原任务及两项双语基础的独立 QA / Owner gate 保持。

## 实施、自检与受控互通准备

已实现严格封闭的 DS JSON 原字节解析、文件 SHA、全点布局校验、单次预览 token / ETag / 客户端目标绑定、单 PLC 新建、真实来源与多 DB 绑定、历史身份冲突检查及同事务保存。目录在配置读取、保存、激活及重开时重新校验原文和归档；旧 DB/UDT 路径保留。新 PLC 与点默认停用、未分组；目录的点集、技术名、地址及类型受保护。原命名预览可在完整目录证明成立时接受原样 `origin=catalog` 地址，并允许修改双语、comment、分组和启用，仍拒绝目录改名、改地址或批量名称生成。旧无语言名称独立保存，不进入 Point；双语与 comment 各自保留。UI 仅新建并展示所有来源与点，变更目标须重新预览，未知提交结果须先重读；中英文手册和 DAA 源码索引已更新。

测试工作目录均为 DAA 根。环境：macOS 15.7.7，Rust/Cargo 1.89.0，Node 22.19.0，pnpm 11.11.0。下述 `E` 为 `env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT DAA_PLC_READ_ALLOWED=false CARGO_TARGET_DIR=/private/tmp/daa017-r4-dev.O7G5Nm/target TMPDIR=/private/tmp/daa017-r4-dev.O7G5Nm/daa-008-r2-a-fixtures`。Cargo 使用仓库锁和 `--offline`；合成 SQLite 和假 transport 均位于本任务临时根，不发真实 POST、不连接真实设备。

| 实际命令或检查 | Development 实测 |
| --- | --- |
| `E DAA017_DS_EXPORT=/private/tmp/ds003-json-x7cWRU/9f548342-8640-4d63-bd75-c606881f7e74.json DAA017_DS_EXPORT_SHA256=40552ff7b0245adb5722c4c61f9b3d50ba75ea5d6741d88b6d478a364bb700cc cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib catalog_import -- --test-threads=1` | exit 0，8 passed。包含协调者从 DS .local/dev 实际 GUI 导出的文件只读解析及原字节 SHA、BOOL/INT/REAL 检查；其余检查为合成 JSON、来源/身份冲突、双库原子回滚、过期/更改目标/取消、目录保护、r5 预览编辑、激活和重开。此项不等于 DAA GUI 导入或跨应用采集。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib daa017_catalog_sample -- --test-threads=1` | exit 0，1 passed：通过真实采集解码器以内存 S7 字节构造新目录本地样本，模拟 v2 worker 的内存 transport 捕获正文；BOOL=true、INT=42、REAL=12.5，两个不同语言 sentinel 不在正文，未发网络请求。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib <filter> -- --test-threads=1`，filter 依次 `source_import_tests`、`point_naming_tests`、`point_display_names`、`daa018_` | 依次 exit 0，4、4、7、3 passed。`point_naming_tests::native_owned_legacy_seed` 因 `DAA006_NATIVE_SEED_ROOT` 未设置立即返回，不是原生验证。`daa018_` 中旧 v1 test-only 正文保留完整 context；仅测试替身，无实际发送。 |
| `E cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --bin aiis-data-acquisition-agent` | exit 0；正式 feature / binary 编译检查，不运行程序或设备。 |
| `node --test tests/plc-catalog-import.test.mjs tests/point-editing.test.mjs` | exit 0，22 passed；内存 IPC / Vue owner，覆盖文件和目标变动、取消、未知结果及既有编辑行为，不替代原生界面。Node 提示既有 MockTimers experimental。 |
| `pnpm exec vue-tsc --noEmit`；`pnpm exec vite build --outDir /private/tmp/daa017-r4-dev.O7G5Nm/ui --emptyOutDir` | 均 exit 0；Vite 报第三方 PURE 注释与 >500 kB chunk 警告。 |
| `rustfmt --check --edition 2021 --config skip_children=true` 对本任务 Rust 文件；`git diff --check` 对本任务已跟踪文件 | 均 exit 0。新增未跟踪文件另按白名单及内容核对。 |
| 递归比较两份 PLC locale 键并检查新增 catalog literal key；检查两份 USER_GUIDE、两份 local_store README 和 CODE_INDEX 的本地 Markdown 链接 | exit 0，键差集、缺失 literal key、5 文件缺失链接均为 0。首次宽正则把列宽存储标识 `plc.catalog.preview` 误当翻译 key，exit 1；缩到实际 `t(...)` / `label-key` 调用后重检通过。 |

最初旧来源回归使用临时目录 `/private/tmp/daa017-r4-dev.O7G5Nm/tmp`，`source_import_tests` 因既有合成夹具要求目录包含 `daa-008-r2-a-` 而 3 passed / 1 failed、exit 101；改用同一任务根内符合要求的新目录后 4 passed。此失败不是产品通过证据，未改测试或使用用户 profile。所有 Rust 测试均有既有 `empty_for_test` dead-code 警告。

协调者提供的 DS 文件在本 Development 中只读；`shasum -a 256` 为 `40552ff7b0245adb5722c4c61f9b3d50ba75ea5d6741d88b6d478a364bb700cc`。DS→DAA 实际 GUI 导入、`.local/dev` 中显式分组/激活及 loopback 读取由主协调统一调度，结果与对象清理待其回传，不以解析或内存采集替代。真实设备、实际外发、Windows、旧普通 native 二进制兼容、部署及 Human Owner 最终验收均未验证。本任务唯一临时根 `/private/tmp/daa017-r4-dev.O7G5Nm` 保存隔离 Cargo target、合成 profile 和 UI 构建，以便后续独立核验；经协调确认无依赖后只清理此任务根，绝不清理其他任务或用户目录。原 DAA-018 旧 target 只作为本任务隔离 target 的只读克隆来源，没有删除或覆盖。

**主协调首轮原生观察（非独立 QA）：** 已回传实际 DS 文件 SHA `40552ff7b0245adb5722c4c61f9b3d50ba75ea5d6741d88b6d478a364bb700cc`，从 DAA `.local/dev` GUI 导入新 PLC `9f548342-8640-4d63-bd75-c606881f7e74`；中文三点切换英文后显示 `Test running`、`Test count`、`Actual temperature`。新建并启用组、点和 PLC 后保存、激活，仅连接自有 DS `127.0.0.1:31974` 并采集 18 条样本；末条 BOOL `false`、INT `0`、REAL `0.0`，质量 `good`。已暂停并断开，未启动真实上报。协调者报告当时临时 app 与工作树 `src-tauri/target/debug/...` 二进制 SHA 相同，均为 `493d5ecbcaf91a605a2b8d1aba45c8695c87653af02e4e9dd252919c6fae0df0`；GUI/进程和用户数据由协调者管理。此观察对应下方冻结候选，不能代替后续修正候选的原生复核。

协调者随后在原生 GUI 编辑 `JSON_Temperature_Real`：技术名和地址控件禁用，英文显示名由 `Actual temperature` 改为 `Actual temperature edited` 并保存草稿；切英文后表格显示新值，中文和地址保持。Development 只读解析该实际 DS 文件确认导出 revision 为 `c17bc82a-1c3d-4dfd-81d5-8c192756a4c4`、DB21 三个源点的 `source_enabled` 均为 true；故首轮未覆盖 DA11 的源停用点保留，不以合成单测代替该实际文件证据。

协调者观察 18 条样本的底层 `sample_delivery` 为 `pending`，UI 的全局待传仍为 5。只读源码显示 runtime4 对每条样本均插入此基础行；采样时未绑定的 cycle 以 `reporting_cycles` 三项 NULL 标识，样本详情为 `local_only`，v2 待传统计排除该标识。协调者按本次新 PLC ID 只读汇总返回 `(total, local_only, missing_marker, upload_rows) = (18, 18, 0, 0)`，证实这 18 条均为本地未绑定样本且无上传任务；基础 `pending` 不应冒称已外发。新测试 PLC 已被活动版本和历史引用；清理由协调者核实正常产品操作和历史保护后决定，不直接删除数据库或整个 profile。

清理前协调者另行只读对照含原 `DEV-PLC-A`、不含本次测试 PLC 的最近历史配置：当前草稿中的原 PLC、DB、组、点、来源、原双语映射及 storage policy 均与该历史配置相同；这是协调者观察，清理后状态仍待核对。

本 Development 后续读取了 `long-task-notifier`，发现未在 r5 最后批准 gate 后、自动执行前启动本角色独立计时；不按对话时间或中途观察补造耗时。主协调确认已在本次首个获批实施窗口启动统一计时，终态统一处理通知，本角色不单独发信。

**冻结候选待修正：** 静态对照发现 DS 导出器将 `STRING[n]` 的方括号内容限制为规范十进制，但当前 DAA 复用既有 `width()`，可能接受 `STRING[04]` 或 `STRING[+4]`。实际 DS 联测文件不含这些非规范类型；这不是全类型合同已通过。协调者正在使用已冻结的 GUI 候选，暂不改产品源码；关闭联测窗口后将在本任务允许的 `domain/plc_catalog.rs` 中补充对 `STRING[n]` 规范拼写的严格判断和负例，重跑相关 Rust 检查、重算候选哈希，再交接 fresh-context Verification。

**冻结候选另有待修正：** 当前前端在文件选择时缓存 bytes，确认时提交缓存；若预览期间文件被外部替换，尚未重新读取并比较所选文件，不能证明满足文件变化使预览失效。主线窗口关闭后在已允许的前端 owner 内补确认前重读、逐字节比对与失败后作废预览，并增加 File 替身测试。两项修正均须在主线关闭后重算源码候选，不能把本轮 GUI 结果称为修正后候选的验证。

### 首轮 GUI 冻结候选文件 SHA-256

以下路径相对 DAA 根，整文件哈希包括各文件中已有的 DAA-018 或其他任务改动，并非声称它们全部由 DAA-017 创建。基线为上述正式工作树 HEAD，未提交或推送。此清单固定首轮 GUI 测试候选；之后的七项变化及最终候选见下节。

锁文件未修改：`src-tauri/Cargo.lock` SHA-256 `3689918ee18e16f63357ceb92811bbcf6019486b38ea747853638073e26b18cc`；`pnpm-lock.yaml` SHA-256 `0417e47e58e19974d9bde4f3866164e88ffe1c1c22eb2ade356e48f12464d44c`。`schema.rs`、Cargo manifest、package manifest 和锁文件的 `git status --short` 均无变更。

```text
3429583a3eb34f946764bac627f02a403e6ed2ad18e443b6cfa5f32eba7b759e  src-tauri/src/domain/mod.rs
76645a6b2a692ce0ca1c93e15ce46ef2935b48327d75b5418afccbcbe5b5cc61  src-tauri/src/domain/local_configuration.rs
2cb6d3ec900f5cb3d59c2e4748d92060b10b9d9a8f7753b7a8fd463026afdf55  src-tauri/src/domain/plc_catalog.rs
254122cfeedcb43ae1247373f85dd823748d88dbeb3758d0beae0e29b5777680  src-tauri/src/services/mod.rs
774b567199fd54394d5fd5182820796b173899aa4981958aba6c04f980c94b90  src-tauri/src/services/local_configuration.rs
d640023fffa7f084ce42717b4e2fe73f984f5121ab449cb1b5d2117cb7c1de4e  src-tauri/src/services/local_point_naming.rs
0768f8787bb9839f28fe6380ca2b4a09949beb0107a9274d375fb7918db6ed45  src-tauri/src/services/local_supervisor.rs
cda328b9a03e2e3adcddc60964a9a2fefdefd614a35e5cdd1e962fe28ec562d3  src-tauri/src/services/catalog_import.rs
cc99df0f1b0b7b3b5947257cca3870a681af6f85d4e4516a7ebeb053cbbe0f4c  src-tauri/src/services/local_delivery_tests.rs
26e6a75ac180955ce4a04c92ed3f2fe03c3940a1777db5f4f66bbb5d699cbb68  src-tauri/src/infrastructure/local_store/mod.rs
50b66e98cb00e51d208d72464c2d12271c7a9f422cd38089f82e0dccc814f1da  src-tauri/src/infrastructure/local_store/configuration.rs
2564d30757d88975fa4f4a9337bf3824ec3647d0ab915950bee058ba24cb34f0  src-tauri/src/infrastructure/local_store/catalog_import_tests.rs
ea17c30415a204ae77a289c6a0e220a97cb1d999eb4442f2af5b91c30af83cb2  src-tauri/src/infrastructure/local_store/README.md
726967c0ae69f355d30396876ed152cdc6648f3178a3580e96820f9181c1a091  src-tauri/src/infrastructure/local_store/README.zh-CN.md
b528f847e7f25f4a7c46ec8a84840add1df2fafc22c1d67f5035fe04eb81c201  src-tauri/src/commands/local_acquisition.rs
3562f45c01befa2085ca18ce6286814b31345dddf834c8e467102f002cb32cb0  src-tauri/src/lib.rs
c6136f155c055b1da3203a6fdfe7b223101335f6f6011b5d52cbd3f66a90017b  src/services/localAcquisition.ts
d1f1d541fce34fa29f1328c72cff7921ed6cdb50a95f462f5811c41b2c5ca095  src/console/composables/useLocalAcquisitionConsole.ts
af7d89834a3b11252895b08926c206fdf41795d4dffa1642787b79034fa02b97  src/app/plc/components/SourceImportPanel.vue
1664c06953d3fd06131f354ca757e264b3f9a7c3ba1b3623d808adebc9ba3bac  src/app/plc/components/CatalogImportDialog.vue
fdb597a0f1d6af95192f003a5714612152605608fe4fb4bb88fbf4f2bed21454  src/app/plc/views/points/index.vue
62a81e9eec3e04afd1505da595f3951f1fa5ae852426cddaed403747367ceae8  src/app/plc/locales/en-US.json
26ccb3d6ef0485e06b77fc4cbd7f06640373b83270d241654583a6d33a995c90  src/app/plc/locales/zh-CN.json
ff452862bea5aff6c9b3cf2db8e438cc1afee41302e5e796bc061cc27d6fefba  tests/plc-catalog-import.test.mjs
9a8b1e69b7b388746996ba51b3dcd47f5d4fefb74e0a2db302afd418c026b9a3  tests/fixtures/plc-catalog-v1.json
b3921c1b35b7fbaac9a04265ca4355cf2836d6da2837a5c98cf7fce95e034bf4  CODE_INDEX.md
b6ddfd5fcf81cde93bbfc0e586c0d22554f6431601bed4d8142a51d177257a16  USER_GUIDE.md
d0828a7806c34702b8df37db06d67ade6b66e0c742d4b3dff7ead85db3b298ef  USER_GUIDE.zh-CN.md
```

## 首轮 GUI 后的 r5 定向修正

协调者确认首轮 DAA 临时窗口已退出且 `.local/dev` 锁已释放后，Development 才在允许文件中补足两项：严格拒绝 `STRING[04]`、`STRING[+4]` 等非规范类型词法；确认前对所选 `File` 对象重新作有界读取并逐字节比较，读取失败或不一致即作废预览、取消后台 token，不调用提交。读取后再次检查预览、目标和编辑状态，防止异步期间旧确认继续提交。用户手册如实说明浏览器可能保留文件快照：本次内存 File 替身测试不能证明 macOS WebKit 对底层路径替换的具体行为，原生替换测试和最终候选跨应用互通仍需协调者 / Verification 核实。

在上述相同 `E` 环境中，`cargo test ... --lib catalog_import -- --test-threads=1` 连同明确设置的实际 DS 文件路径和 SHA exit 0、8 passed；`cargo test ... --lib daa017_catalog_sample -- --test-threads=1` exit 0、1 passed。`source_import_tests`、`point_naming_tests`、`point_display_names`、`daa018_` 同样按前述命令和顺序重新运行并 exit 0，stdout 本轮重定向到 `/dev/null`，因此复用上次各过滤器所列数量时保留这一限制。`node --test tests/plc-catalog-import.test.mjs tests/point-editing.test.mjs` exit 0、23 passed，其中新增了 File 字节改变及重读失败不能提交的检查。`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir /private/tmp/daa017-r4-dev.O7G5Nm/ui-final --emptyOutDir`、正式 `rust-snap7-driver` cargo check、针对本轮文件的 `rustfmt --check`、本任务已跟踪文件 `git diff --check`、5 份手册/索引链接检查及 locale 键对称检查均 exit 0；Vite 和既有 dead-code 警告仍在。

最终源码候选沿用上一清单中未列出的 21 项不变，仅以下 7 项哈希替换；首轮原生窗口和样本对应旧清单，不能将其结果写成修正后候选的 GUI 通过。再次完整 GUI 导入须使用新 DS 合成实例与新 UUID，且包含源停用点；当前本 Development 不再改 `.local/dev`。

```text
7c0229859322f140489243d6c602334889a359524687f52dfe10e753323c0a44  src-tauri/src/domain/plc_catalog.rs
11e1f8c88b3a510d5a517608801837ad61ed2206e794d4f0c1ce5d7a186add66  src/console/composables/useLocalAcquisitionConsole.ts
36cf138c5298d83d5d1f05647704e0041bcc2b404c29b0130d09ca44f8b43a53  src/app/plc/locales/en-US.json
e3686268631c93f85abc11cdd984ed1c068383690854e12994795f2c12b456af  src/app/plc/locales/zh-CN.json
cd78889592dfa5b3c27a52b5720ceeddb099742eac0bc99f9ee98a9a908ef6e2  tests/plc-catalog-import.test.mjs
1f5befc1fa12239b37c83a019191529794a961fb4430cde1095448f7955a1f1d  USER_GUIDE.md
9ae894b1fb2388d3b0a872aec660537c2fdf35fe2d446c8f87de555a48b225a2  USER_GUIDE.zh-CN.md
```

**主协调最终候选原生复测进行中（非独立 QA）：** 协调者报告使用工作树普通 `pnpm tauri dev` 构建，DAA binary SHA-256 `d2f3f104f7b413c7c63c47a99db85a6f2dc1007105627eeee6c7ffcbadc41a6f`，所运行测试 `.app` 同字节；目标为已核对的 DAA `.local/dev`。从新 DS 合成实例 `31d327ba-2b97-4f5e-8949-6956ac3a5648` 实际导出文件 SHA `0268a8098bb36c4b3bdc3f89141ef31123c56fb34ba47e33e275cd87a378e9a6`，原生预览显示相同摘要、4 点（含源停用 BOOL）、双语与温度描述，确认后新建草稿成功，4 点均默认停用。最终候选实际采集、底层路径替换验证及本任务对象安全清理尚待协调者继续；不得把“已导入”写成这些后续项目通过。

**后续原生观察：** 协调者对新 PLC 仅为 3 个源启用点显式分组并启用，第 4 个源停用 BOOL 仍停用、未分组；只连接自有 DS `127.0.0.1:31975`。最终候选实际采样 15 次，只读统计 15/15 `quality=good`、15 个 `reporting_cycles` 为 local-only 且 `sample_uploads=0`；上报保持停止，原有待发送计数仍为 5，随后断开 DAA 并停止 DS。协调者核对末条样本和 DS 默认初值一致：`Final_Run_Bool` BOOL DB21 `0.0=false`、`Final_Count_Int` INT DB21 `2=0`、`Final_Temperature_Real` REAL DB21 `4=0.0`，三点质量均为 `good`，地址 `origin=catalog`，温度 comment 为 `合成温度`。源停用 `Final_Disabled_Bool` BOOL `1.0` 未进入样本，仍在配置中。

协调者还用自有临时 JSON 在 macOS 原生界面预览后执行 `os.replace`：原预览 SHA `41fb112960d077a260969e50194bfbf9613577024d002002aca96be6acf7b6f4`，替换文件 SHA `608c952bba80784e9394258ffbccf0e8fa44fe8d9bc214a917ea12f6c460797f`；点确认后出现“文件已变化或无法重新读取，请重新选择并预览”，未成功提交。这证明本次 macOS / WebKit 特定替换场景被阻断，不外推所有系统和文件快照实现。测试实体的正常清理仍由协调者进行。

**协调者的 DAA 清理观察：** 已通过应用 UI 从草稿移除两台本任务测试 PLC `31d327ba-2b97-4f5e-8949-6956ac3a5648`、`9f548342-8640-4d63-bd75-c606881f7e74`，保存并激活；工作台恢复仅 `DEV-PLC-A`、0 连接 / 采集，上报停止，原 5 条待发送和 69 条已确认未变，两个自启开关关闭。协调者只读核对 active 与 draft 一致，原 PLC / DB / 分组 / 点 / 来源 / 存储与联测前活动 revision 相同，原用户双语显示名仍在草稿。15+18 条测试样本和相关版本作为历史保留，均无 `sample_uploads`；未直接删除数据库或队列。复测进程与 Vite 已退出并释放端口及锁。DS 自身对象清理由 DS 任务记录。

最终 DS 导出 revision 为 `3d50439c-fb2b-41bd-9d95-56c67cd98672`；原文件 `/private/tmp/ds003-final-json-RfE0TL/31d327ba-2b97-4f5e-8949-6956ac3a5648.json`、SHA-256 `0268a8098bb36c4b3bdc3f89141ef31123c56fb34ba47e33e275cd87a378e9a6` 暂由协调者保留供 Verification，核验不再依赖后由其确认归属再清理。Development 自有 `/private/tmp/daa017-r4-dev.O7G5Nm` 同样保留至独立核验无依赖；不清理其他任务资源或用户 profile。

## developer_handoff

交接 `aiis-ics-arch::DAA-017 r5`，批准后 spec SHA-256 `daa1735f7d8f70c27bae67fd979e5012906592391aaa476db152a1e6763f44e1`；候选为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 工作树、HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，准确源码及文档为上文首轮 28 文件清单应用最后七项替换。运行入口是本工作树的 DAA `pnpm tauri dev`，实际最终二进制 SHA 如上。工作树已有大量并行与先前改动，候选哈希固定整文件，不能把全部 Git 差异归因本任务。Development 自检、初次错误和其后重跑、模拟 v2 与协调者实际联测证据均按上文记录。

请主协调启动不继承本 Development 推理上下文的 fresh-context Verification，提供精确 spec、此 tasks、28 项最终源码哈希、锁文件、工作树 diff、实际 DS 文件及当前资源状态；由 Verification 独立核验 DA01–DA17 并独占 `checklist.md`。本 Development 不作 QA verdict 或 Human Owner 最终验收。当前观察只覆盖本机受控合成 DS / DAA 路径；旧普通二进制、Windows、其他平台、真实设备、实际外发、部署和生产采用均未验证，DS-004 / DAA-018 原有 `qa_blocked` 状态不因本任务改变。

## QA1 返修与当前 developer_handoff

独立 QA1 已结束并记录 `qa_failed`，`checklist.md` SHA-256 `bac8d30eb829b9a5f6273e29dded4200bb41ada95cd7d2a17c77551aeeaa01e9`。F-DAA017-QA1-001 指出：旧候选只校验 UUID 的版本半字节及小写文本，错误接受 NCS variant 的 `ca21fc06-a489-4948-03fc-08b8e798168e`；QA 以实际 DS 文件的停用点复现，未声称提交到用户数据。此失败事实和原 checklist 均保留。

QA1 冻结后，Development 在 r5 允许的 `src-tauri/src/domain/plc_catalog.rs` 为共享 `canonical_id` 增加 `uuid::Variant::RFC4122` 判断，保留原版本 4 与规范小写要求；不改变本地既有配置的身份规则。在该文件与 `src-tauri/src/infrastructure/local_store/catalog_import_tests.rs` 新增回归：以 QA 的同一非法 ID 替换合成 fixture 中的停用点，检查解析及本地预览拒绝；本地预览还比较草稿、源归档、其他受保护数据和 ETag。解析测试逐一覆盖 origin profile / PLC、export profile / revision、DB 和点 ID 的 NCS、Microsoft 与保留 variant，并检查 RFC variant 的 `8`、`9`、`a`、`b` 正例。

工作目录、隔离根与上文相同；以下 `E2` 为 `env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT -u DAA017_DS_EXPORT -u DAA017_DS_EXPORT_SHA256 DAA_PLC_READ_ALLOWED=false CARGO_TARGET_DIR=/private/tmp/daa017-r4-dev.O7G5Nm/target TMPDIR=/private/tmp/daa017-r4-dev.O7G5Nm/daa-008-r2-a-fixtures`。Rust 命令均使用 `--locked --offline`，本次返修不操作 `.local/dev`、真实设备或真实 POST。

| 实际命令或检查 | Development 返修自检 |
| --- | --- |
| 仅加回归、尚未修复时：`E2 cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib non_rfc_uuid -- --test-threads=1` | exit 101，0 passed / 2 failed；解析与本地预览实际返回成功而非预期的 `catalog_point_invalid`，确认测试重现 QA 所报缺陷。 |
| 修复后重复同一命令 | exit 0，2 passed。独立合成 SQLite 位于本任务临时根。 |
| `E DAA017_DS_EXPORT=/private/tmp/ds003-final-json-RfE0TL/31d327ba-2b97-4f5e-8949-6956ac3a5648.json DAA017_DS_EXPORT_SHA256=0268a8098bb36c4b3bdc3f89141ef31123c56fb34ba47e33e275cd87a378e9a6 cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib catalog_import -- --test-threads=1` | exit 0，10 passed；文件 SHA 另以 `shasum -a 256` 只读核对一致。此项是现有 DS 文件的解析检查，不是返修后二进制的原生 GUI 互通。 |
| `E2 cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib <filter> -- --test-threads=1`，filter 依次为 `daa017_catalog_sample`、`source_import_tests`、`point_naming_tests`、`point_display_names`、`daa018_` | 依次 exit 0，1、4、4、7、3 passed；`native_owned_legacy_seed` 因未设置种子提前返回，模拟 transport 未发送实际网络请求。 |
| `E2 cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --bin aiis-data-acquisition-agent` | exit 0；检查正式驱动 feature / binary 的编译，不启动应用或设备。 |
| `rustfmt --check --edition 2021 --config skip_children=true src-tauri/src/domain/plc_catalog.rs src-tauri/src/infrastructure/local_store/catalog_import_tests.rs`；`git diff --check -- automation-world/data-acquisition-agent` | 最终均 exit 0。首次 rustfmt 检查因新增测试两行折行不符 exit 1，修正格式后重检通过；两个新增源文件为未跟踪文件，后者 Git diff 检查不覆盖它们。Rust 测试保留既有 `empty_for_test` dead-code 警告。 |

新候选仍为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 工作树、HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，spec SHA-256 仍为 `daa1735f7d8f70c27bae67fd979e5012906592391aaa476db152a1e6763f44e1`。已按上文首轮 28 文件清单应用七项替换进行整文件核对：26 项与 QA1 对象不变，以下两项为此次唯二源码 / 测试替换；锁文件、manifest 和 schema 状态未变：

```text
8d8032a216ef75984a8016aa3d66346752753d69897f4eeb99eaeabc42923ae8  src-tauri/src/domain/plc_catalog.rs
9f00e9adf708d219832e85280eaf8313c11b10097b48022b86a6ca0e14360f7f  src-tauri/src/infrastructure/local_store/catalog_import_tests.rs
```

上文二进制 SHA `d2f3f104f7b413c7c63c47a99db85a6f2dc1007105627eeee6c7ffcbadc41a6f` 和原生联测均对应 QA1 前候选，不是此返修源码的新二进制或新候选原生复验；本次未重新构建或运行原生应用。此前实际 DS 文件和 `/private/tmp/daa017-r4-dev.O7G5Nm` 按各自归属继续保留供复验，待协调者确认无后续依赖后安全清理。返修测试没有接触用户 `.local/dev`，也没有清理他人资源。

Development 现将本 r5 修复候选和实际自检交给主协调，供另一 fresh-context Verification 独立复核，原 QA1 失败不因此自动改变；Human Owner 最终验收仍待决定。此前未验证平台、旧版二进制、真实设备、真实外发、部署与生产采用的限制不变。
