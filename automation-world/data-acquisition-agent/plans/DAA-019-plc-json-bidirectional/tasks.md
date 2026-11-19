Task ID: DAA-019
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: DAA-019 r2 QA 失败后的索引返工及 Development 自检 -> 新的 fresh-context Verification；Human Owner 最终验收待后续决定
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-019 Development 记录

## 批准与工作基线

Human Owner 已精确批准 `aiis-ics-arch::DAA-019 r1`、`aiis-ics-arch::ARCH-PLC-001 r6`、`device-simulator::DS-005 r1` 及版本衔接。实施前核对 DAA-019 spec SHA-256 `1a3b5765676ecb8f0f225f6e2c41687d763bd6c270fe423fb76498e769d4555e`、父 spec SHA-256 `0eb0c10e70507903347b216d2ac712add430fc4511b251a2ad93e00e19ce1408`。正式工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`；开始时已有其他任务的计划文档和新任务 bundle 未提交，予以保留。

计划：按 r6 完整导出已保存 PLC 配置并迁移导入入口；对仅有历史的同源对象以明确选择建立全新本地身份；在自有隔离资源验证合同、保存和上报隔离；跨应用原生联测由协调者安排。当前不操作 `.local/dev`、真实 PLC 或真实 POST。

协调者只读核对发现用户 DAA 开发进程仍占用其 profile，正式源码可能被 watcher 监听；为避免修改触发热重载或重启，先在自有 `/private/tmp/daa019-dev.MKLyerrV` 副本实施和验证。正式树整合须先确认不会影响用户进程，整合后重新验证正式交付源码；此临时副本不作为最终交付。

## 实施与联测前候选（尚非最终 handoff）

已在 PLC 配置页并列提供导入与导出，迁移复用原目录导入对话框；导出从所选持久草稿或活动版本的原 payload 取 SHA，逐 PLC 验证完整点集并通过原生目录选择、预览令牌与排他原子写入输出文件。导入器按 producer 校验 DB 层启用字段，当前同源/身份及端点冲突拒绝；仅有历史时需明确选择新本机实例，保存外部与本地 DB/点映射、原始文件与 SHA，并返回实际提交的 `importedLocalPlcId`。PLC/点默认停用未分组；保留原 Point/PointFact/v2 wire，未增加物理 DDL。目录来源及旧 DB/UDT 分支各自重验；新旧历史不合并。中英文操作指南与本地存储说明已按现行行为更新。

隔离副本的 29 个原文件在正式树整合前逐个与 HEAD 字节比对，5 个新增文件的目标均不存在；整合后 34/34 与隔离候选逐字节一致。工作树还存在协调者及 DS 并行更改，以下清单仅列本角色候选文件，整文件哈希不改变其他角色归属。按照协调者要求未改索引。

### DEV 自检

环境 macOS 15.7.7 (24G720) arm64、Rust/Cargo 1.89.0、Node 22.19.0、pnpm 11.11.0。除注明外工作目录为正式 DAA 根；`E` 为 `env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT DAA_PLC_READ_ALLOWED=false CARGO_TARGET_DIR=/private/tmp/daa019-dev.MKLyerrV/target TMPDIR=/private/tmp/daa019-dev.MKLyerrV/daa-008-r2-a-fixtures`。Rust 使用 `--locked --offline`；各 profile 为自有合成数据，v2 transport 为内存替身，没有真实 POST 或真实 PLC。

| 命令或检查 | 结果 |
| --- | --- |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib daa019_ -- --test-threads=1` | 正式树 exit 0，5 passed：双 producer、普通来源完整导出/同名并发/部分失败、活动版本与历史样本/队列/回执隔离、历史身份映射及 fake v2 正文。 |
| 相同 `E cargo test ... --lib <filter> -- --test-threads=1`，隔离副本依次 `catalog_import`、`source_import_tests`、`point_naming_tests`、`point_display_names`、`daa018_`、`daa017_catalog_sample` | 分别 exit 0，11、4、4、7、3、1 passed；其中旧测试 `native_owned_legacy_seed` 和未提供 `DAA017_DS_EXPORT` 的外部文件测试提前返回，不作为原生/实际文件证据。隔离副本与正式树 34/34 一致。 |
| `E cargo build --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --bin aiis-data-acquisition-agent` | 正式树 exit 0；产物 `/private/tmp/daa019-dev.MKLyerrV/target/debug/aiis-data-acquisition-agent` SHA-256 `475a50c61c6e76ee9b615a62bd387c53ffb1c88a0ad30d0836b04a865737a223`。只编译，未启动；不能代替普通 `pnpm tauri dev` 原生联测。 |
| `node --test tests/plc-catalog-import.test.mjs tests/plc-catalog-export.test.mjs tests/point-editing.test.mjs` | 正式树 exit 0，26 passed，使用无 DOM / 内存 IPC 替身；存在 Node MockTimers experimental 警告。 |
| `pnpm exec vue-tsc --noEmit`；`pnpm exec vite build --outDir /private/tmp/daa019-dev.MKLyerrV/ui-formal --emptyOutDir` | 正式树均 exit 0；Vite 报第三方 PURE 注释和大 chunk 警告。 |
| 本次 Rust 文件 `rustfmt --check --edition 2021 --config skip_children=true`；`git diff --check -- automation-world/data-acquisition-agent`；递归比较 PLC locale；两份 USER_GUIDE 与两份 local_store README 的相对链接 | 均 exit 0；中英文各 264 个叶键，差集 0；32 个链接无缺失。 |

首次隔离编译因未复制公开 v1 vectors 及一处测试构造器缺新增字段 exit 101；补齐隔离测试材料及该测试字段后重跑通过。隔离副本首次 `pnpm exec vue-tsc` 因 node_modules 为指向正式树的只读复用链接，pnpm 尝试依赖检查并因无 TTY 拒绝移除、exit 1；未安装依赖或移除正式 node_modules。其后隔离副本直接使用现有 `.bin/vue-tsc`，正式树使用 `pnpm exec` 均通过。Rust 有既有 `empty_for_test` dead-code 警告。

Cargo 锁只增加 `tauri-plugin-dialog =2.7.2` 及其必需的 14 个传递包；未移除包或改变既有包版本。现有 objc2-foundation 的 libc feature 闭包与 windows-targets 歧义标注随新依赖更新；曾由 Cargo 自动改变的两个无关 windows-sys 选择已恢复，`--locked --offline` 验证通过。没有新增 npm 依赖。

按照 PM 的构建副作用澄清，正式构建前核对 `src-tauri/gen/schemas/` 仅含四个普通、非符号链接的既有生成 JSON；构建后仍为相同四文件。`acl-manifests.json` SHA 由 `b8665c2471bd4c59d570c77e226f37410ce396da52525383a15b5b557f9d786e` 变为 `d3eace193b1e453756736eaf27bb156df62c7a41b2fe101403ee92ef93e69699`；`desktop-schema.json` 与 `macOS-schema.json` 均由 `f68a9c570ecff07ac6826145d33b966d6fc02f7d680967f44437268b08a6ba78` 变为 `2a16f62c90a059a1b67e4501216bb3476f402087e99ba659dd38c9d0521f3b07`；`capabilities.json` 保持 `ccefbe754f766cb08a6123e15fdbe13ab9a8708166ca4c4eb518db19ff5adcb0`。它们是被忽略的标准生成文件，不作为源码候选或清理目标。

普通 DB/UDT 的隔离服务实际导出 JSON SHA-256 `937c0f3aa0ce583821e4b647a2395a3bc97e0975424a5cb9fe9362f15d320ee5`；DS Development 回报在隔离 DS profile 完成服务级解析、导入、重开和重导字段比对。这不是本角色独立验证或原生闭环。

### 联测前候选文件 SHA-256

路径相对 DAA 根；该清单固定的是待跨应用联测的当前未提交工作树，不是 Verification verdict。

```text
e5ab02974b16d39b675084cddf44a8632152cf05e4c31a4258d2e86a7b1ed6fd  USER_GUIDE.md
03c504f458df09404101ae93568030635dccb198c000088fc2ad01a7af0caaea  USER_GUIDE.zh-CN.md
de041c068dad0765abe14de50518f1777af3b5e82c8e966c2e56bc58c631a226  src-tauri/Cargo.toml
ee275fec7b0d9ae6fa2509e716b43a37db403b68c7e9343e5f7c9191e02b014b  src-tauri/Cargo.lock
09ec4d6dc4663f1dbd83c1aea8cd7ff3df466145024097a9dce6dff8bcbb5189  src-tauri/src/domain/local_configuration.rs
eb4e53be4b9e24820b0f99279b0521ca339d2989a74d6cc90fe6a3fb663a04fa  src-tauri/src/domain/local_runtime.rs
2ffa059286575dca3cfb862eab4874ce2a532643d778accd785c99f21433f98b  src-tauri/src/domain/plc_catalog.rs
c7020e7e8b9a6c2e606aa535a96c9e021fdf759fac8669ee18ca3e829fc6b50d  src-tauri/src/services/mod.rs
984d2275c43e53b660326d892c0b2dc968ed94c73f29a93bf2263f06b52bb259  src-tauri/src/services/catalog_import.rs
4f8fa85ddb0d2e2ac2c69100fa2f8c4f64b6c8580919be68168a911408ade58e  src-tauri/src/services/local_configuration.rs
d3b2e853390eae0d96847a1a0ab1c86690b7228242ba7a07f18af234c115dd8a  src-tauri/src/services/local_supervisor.rs
a0ad23446483aaf703e07ff0b72f7773c370691b93dc3b34a3a26e02afb95b9f  src-tauri/src/services/local_activation.rs
32a42495ab37c56eaae81ed07cbd30eed8b37badcefe0caf408bd2f6f2026fd8  src-tauri/src/services/local_delivery_tests.rs
5b1a1bc4c2341e1a9bc1993c5ebacf12e0b4ee412e4ec7be458b070a3c6875ec  src-tauri/src/infrastructure/local_store/mod.rs
d80a9a8c732901738ef7b8a64fc04fdca1528aa52dab14120c42aa39c55c1476  src-tauri/src/infrastructure/local_store/configuration.rs
d9afc29f450eeeb61590ff5a48ef02a98836a9901b2e83d8868a200ff4f0ce16  src-tauri/src/infrastructure/local_store/catalog_import_tests.rs
fe86e30cdc15d726ea61d0fc4981c663c79b59105ee8371d1ab7c03aa4d4c814  src-tauri/src/infrastructure/local_store/README.md
c01954ad67b49583799b8c811d117a985df08d897cd5f2c7f931dd5cc6d17d54  src-tauri/src/infrastructure/local_store/README.zh-CN.md
9dc75129a5d124c1460e99bca9eab77608d04562fbbaaaa413cd9d5a2317bb62  src-tauri/src/commands/mod.rs
f68a460113b9f940c425a6fcc0b612b3be9b37948d8ad58da4d5803a0a214fd8  src-tauri/src/commands/local_acquisition.rs
e1dfeab0bfc5c8f4189a8ea4aecb25d4f86c6f95f2ff143a57238ea1db38c5e0  src-tauri/src/lib.rs
d8b4ec27ac98edea0a1027f46d4030dec0d2b98618fee8f93336c2f64094983c  src/services/localAcquisition.ts
c71e44e2bbc991ea99d656039eade32c77c72680eb2308ef5f57254fb6aea862  src/console/composables/useLocalAcquisitionConsole.ts
63d969951ec10f8c381f8ac80919fa1c189f8cedc2b6af4c63f95786284d3016  src/app/plc/views/diagnostics/index.vue
b6f5882167a58ce645bf749d42604f77e60014b6f9a8d8586fdc64ae54805de2  src/app/plc/components/SourceImportPanel.vue
97d727503286da29292f6773526618d4d5353d9cdc27e4fee53fbe2f5cc62e1f  src/app/plc/components/CatalogImportDialog.vue
1e988fec388aee0b63125c45efb4e66ba7e90681a2d2035dc42d2114f0443937  src/app/plc/locales/en-US.json
00b82d8efb889c559d72375558309fc40adfcb1c98d58ca53ea26baed92b52cb  src/app/plc/locales/zh-CN.json
e2a469fdd64ecd5a9c6a736ccada95e797b32f7c633b75206609547f2b8e79e1  tests/plc-catalog-import.test.mjs
d9946fc4d70757b12520ffc8579567be2bb4ba3037e4f15ec9feb80373b687e9  src-tauri/src/services/catalog_export.rs
649c88a844dd71398536c9a8a706779f727d8d179345465f098d831d71030593  src-tauri/src/commands/catalog_export.rs
72a1240e626d7874dfcb18f24505dcc3c71d1bf7bebe7d12fc393ece1a8d4f32  src-tauri/src/infrastructure/local_store/catalog_export_tests.rs
82276ed8958e5fc9641d700e43343136c704b0c0018cf6512fb271d6eb6ac9e7  src/app/plc/components/CatalogExportDialog.vue
3641f8967191e3f47285054e433e93cf3db9053f71b7792eab861bf214665fe9  tests/plc-catalog-export.test.mjs
```

清单原文 SHA-256 `11103e42e72487ecfd924f27ecf66ba56e90e74a4fcf2b5a4089bd7a968661d5`，其临时副本为 `/private/tmp/daa019-dev.MKLyerrV/candidate-sha256.txt`。

### 端点冲突后的联测前修正

静态复核发现，若文件中的原客户端端点已被其他当前 PLC 占用，后端虽正确拒绝，但原界面只有预览成功后才出现目标编辑器，用户无法改端点重预览。现仅在前端 owner 中从所选文件提取目标供编辑；后端仍严格解析原字节并重新校验，不能以界面提取替代合同验证。定向 Node 测试覆盖首次端点冲突后改目标重预览、历史重映射时改目标及按实际提交 ID 选中。正式树重跑三组 Node 测试 exit 0、27 passed；`pnpm exec vue-tsc --noEmit` 与 `pnpm exec vite build --outDir /private/tmp/daa019-dev.MKLyerrV/ui-final --emptyOutDir` 均 exit 0，原 Vite 警告保留。此次只改以下两文件；上表 Rust 检查和二进制仍对应相同 Rust 源码。

```text
7765b9f6eade0d31218d2fa00d19d8690568ce5bab0f7928c5510e79b1cf734b  src/console/composables/useLocalAcquisitionConsole.ts
3c1ad397caa7cad357ce6a5132fb3f9bbe9d3a82466748a998d1ec7d8f76420a  tests/plc-catalog-import.test.mjs
```

当前联测前候选清单由前一 34 项中这两项替换得到，完整清单 `/private/tmp/daa019-dev.MKLyerrV/candidate-sha256-final.txt` 的 SHA-256 为 `61edf627f18f9f3bd7f05f85800816a9a7a7b0b4f2ba35953f24fab7b368695f`。`git diff --check -- automation-world/data-acquisition-agent` exit 0。原生端点冲突操作仍待联测，不以 Node 替身冒充。

### 历史本地身份与来源引用保护的联测前修正

PM 澄清“历史身份不冲突”按实际实体及引用判断：独立的 sample/cycle/receipt 自身 ID 不与 PLC/DB/点/来源 ID 混作同一命名空间。导入时仍完整重验全部保留配置 revision/context 的原文 SHA 和目录映射，并在提交前针对 `plc_sources.plc_id`、`collection_cycles.plc_id`、`samples.plc_id` 及实际存在的 reporting `local_plc_id` 作只读碰撞检查。先确认 runtime v2/v3/v4 的已支持完整结构，合法旧版本及 v4 原始结构未提供 reporting 表时不要求新表；本应存在的表损坏则拒绝。点/DB 身份保存在完整 context：既有 `commit_cycle` 按 revision/context 核对点成员，已封存 profile 的 `core_check` 在重开时校验 context、样本定义及 DB 对应；本任务不修改它们的事实语义。

隔离反例确认既有 `prune_config` 在配置版本裁剪后只按草稿/配置版本寻找来源引用，即使 runtime context 保留，仍可能删除其 source archive。原候选在自有合成 profile 导入、激活、移除后继续激活 10 次，同一测试 exit 101，观察到旧 revision 被裁剪、context 仍在而 archive 消失；仅在本任务允许的存储文件内补充对所有保留 runtime context 的 SHA 校验和来源引用保护，流式处理 payload，不更改物理 DDL。修复后正式树相同反例通过并正常重开；另用自有合成损坏 context、缺失 archive 和 runtime v2/v3/v4 本地引用夹具验证拒绝及无部分写入。由于最初内存负例对 reporting_disabled 的外键条件构造不完整，该轮 6 passed / 1 failed；只在隔离损坏夹具中关闭外键后重跑。正式树 `E cargo test ... --lib daa019_ -- --test-threads=1` 最终 exit 0、9 passed；`E cargo test ... --lib catalog_import -- --test-threads=1` exit 0、15 passed；`E cargo build ... --features rust-snap7-driver --bin aiis-data-acquisition-agent` exit 0。首次格式检查从仓库根误用 DAA 相对路径 exit 1；改到 DAA 根后 `rustfmt --check` exit 0，`git diff --check` exit 0。

相对上节清单仅以下两项替换，当前 34 项完整清单 `/private/tmp/daa019-dev.MKLyerrV/candidate-sha256-final2.txt` SHA-256 `2800fc8f912950e92307bce9944d0624d4d1725955935d70ac6d158a076a9511`；正式树 debug driver feature 二进制 SHA-256 `9a1dab62ecd962db75502a651a37eb1b0111ce7ff0765de044763b0dd39cdaab`。不把该构建冒充原生联测二进制。

```text
e99f4223cf99471b33e63157f8be967743bdc0f69ff95ed29d90594b10e3d3dc  src-tauri/src/infrastructure/local_store/configuration.rs
3d568d20e138b2ffda5da74d32450f09ddfdab95eed32a2b153a4fa08e3dcdb2  src-tauri/src/infrastructure/local_store/catalog_import_tests.rs
```

本修复保护 context 引用的来源归档，未改变现有配置 revision 的 `skip(8)` 裁剪策略。协调者报告用户 `.local/dev` 当前已有 8 个 revision，继续激活可能触发现有旧 revision 裁剪；联测条件由协调者与 PM 按保护原配置要求处理，本角色不操作该 profile。

### 待完成和资源

协调者仍须在核对的两个 `.local/dev` 安排实际 DAA→DS→DAA 文件闭环：先由当前同源拒绝，使用唯一合成 PLC 显式激活制造历史、移出并显式激活后提交新本地实例，检查新旧身份、历史和既有 DEV-PLC-A；完成后仅通过正常应用处理本任务对象并保留历史引用。需要记录两端实际版本/文件 SHA、原生界面和生成文件结果；本记录尚不声称这些步骤已通过。之后按真实结果更新本文件、冻结最终候选并由 fresh-context Verification 独立复核，Human Owner 最终验收另行决定。Windows、现场设备、真实网络上报、部署和发布未验证。

`/private/tmp/daa019-dev.MKLyerrV` 为本任务自有隔离源码副本、target、合成 profile、日志与 UI 构建根；其中服务级合成导出供跨角色预检，DS 已报告无进一步读取依赖。待正式联测和独立复核不再依赖时，由协调者核对归属及无占用后仅回收本任务资源；不删除旧生成目录、其他任务或 `.local/dev` 历史。

## r2 接续记录（进行中，尚非 Development handoff）

2026-11-18（Asia/Shanghai），Human Owner 精确批准 `ARCH-PLC-001 r7`、`DAA-019 r2`、`DS-005 r2` 及版本衔接。批准后只读核对本任务 spec SHA-256 `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`，父 spec SHA-256 `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`。产品实现与 r1 allowlist 不变；本次仅调整验收路径。上文 r1 原记录及失败证据保留；其中“在 `.local/dev` 显式激活制造历史”的待办已被 r7 §4.1 取代，未按该旧计划执行。本轮激活、移除和再次激活只在自有合成 profile 证明；协调者单独按 r7 §4.1 B/C 安排用户 profile 的原生文件操作，DAA 全程不激活、不采集、不上报。

正式树 HEAD 仍为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。以只读 Python SHA-256 逐项核对上述最终清单 `/private/tmp/daa019-dev.MKLyerrV/candidate-sha256-final2.txt`（清单 SHA-256 `2800fc8f912950e92307bce9944d0624d4d1725955935d70ac6d158a076a9511`），34/34 项与正式工作树相同、0 项不符。r2 接续未修改产品源码；上文全部文件及替换清单仍是本角色候选。

复核 r1 最终候选服务测试：`daa019_active_version_and_reimport_preserve_old_samples_queue_and_receipt` 在自有 SQLite 使用实际服务保存、激活、以合成 cycle 和内存 fake response 建立旧样本、队列及回执，移除并激活移除版本后，以新本机身份导入；逐表比较旧 `plc_sources`、reporting bindings/generations/cycles、collection cycles、samples、delivery、uploads 与 attempts，检查新实例无 generation 和绑定、PLC/点停用且点未分组。`daa019_history_requires_choice_and_separates_local_identities` 另验证未选择时拒绝、新 PLC/DB/点身份、外部 origin/DB/点 ID 再导出、物理归档不覆盖及重开。这些是服务级合成证据，不是原生 GUI 结果；其正式树执行命令与结果见上文。

协调者另外报告正式入口已在自有临时 profile 启动、退出：DAA 根目录执行 `env -u DAA_ENV_FILE -u DAA006_NATIVE_SEED_ROOT DAA_PROFILE_DIR=/private/tmp/daa019-dev.MKLyerrV/entry-profile DAA_PLC_READ_ALLOWED=false CARGO_TARGET_DIR=/private/tmp/daa019-dev.MKLyerrV/target CARGO_NET_OFFLINE=true pnpm tauri dev --no-watch`，本机 loopback 经已批准提权启动，Vite `15191` ready，`cargo run` 使用 `rust-snap7-driver` 成功，`runtime_started` 后状态 stopped；临时进程 PID `79816` 正常停止后自有 profile 锁与端口释放，未使用用户 profile、连接 PLC 或上报。该次运行 binary SHA-256 `5aaf397a16a61ea7bec116a004c0478c595e6ee444309d75aeb3393609d1b67a`，与上文独立 cargo build 的 `9a1dab62ecd962db75502a651a37eb1b0111ce7ff0765de044763b0dd39cdaab` 分别记录；这不是跨端 GUI 往返结果。

新增逻辑来源身份的针对性自检在自有 `/private/tmp/daa019-r2-dev.c0EWK6bZ` 进行：从正式候选只读复制 Rust 工程、共享 TIA 源码及测试夹具，仅在该副本的历史测试中增加下述断言，正式源码不改。复制前该测试 SHA-256 与正式候选均为 `3d568d20e138b2ffda5da74d32450f09ddfdab95eed32a2b153a4fa08e3dcdb2`；附加断言后的临时测试文件为 `fdfd223ccb4be59a75689c1429fd1153bdc0b5cbc411c2471d121cfc5297b916`。`rsync -nrc --itemize-changes` 对比正式与临时 Rust 工程（排除临时测试文件、构建 target 和工具生成 gen）、测试夹具和共享 TIA 工程（排除 target），三次均 exit 0 且无差异输出。副本测试的唯一改动为保存旧 `sources` ID；确认新 PLC 恰有一个逻辑来源、其 ID 不在旧 ID 中、目录映射引用新来源，并在重新打开后比较完整 sources 和 catalog bindings：

```rust
let old_source_ids: Vec<_> = saved.draft.sources.iter().map(|s| s.id.clone()).collect();
assert!(!old_source_ids.is_empty());
// 导入成功后：
let new_sources: Vec<_> = result.draft.sources.iter().filter(|s| s.plc_id == new_plc).collect();
assert_eq!(new_sources.len(), 1);
assert!(old_source_ids.iter().all(|id| id != &new_sources[0].id));
assert!(result.draft.catalog_bindings.iter().all(|b| b.source_id == new_sources[0].id));
let committed_sources = result.draft.sources.clone();
let committed_bindings = result.draft.catalog_bindings.clone();
// 重新打开 profile 后：
let reopened_draft = reopened.configuration().unwrap().draft;
assert_eq!(reopened_draft.sources, committed_sources);
assert_eq!(reopened_draft.catalog_bindings, committed_bindings);
assert_eq!(reopened_draft.catalog_bindings.len(), 2);
```

临时 DAA 根目录执行，`E2` 为 `env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT DAA_PLC_READ_ALLOWED=false CARGO_TARGET_DIR=/private/tmp/daa019-r2-dev.c0EWK6bZ/target CARGO_BUILD_JOBS=4 CARGO_NET_OFFLINE=true TMPDIR=/private/tmp/daa019-r2-dev.c0EWK6bZ/daa-008-r2-a-fixtures`：

| 命令 | 实际结果 |
| --- | --- |
| `E2 cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib daa019_history_requires_choice_and_separates_local_identities -- --test-threads=1 --nocapture` | 首次 exit 101：临时副本漏带根合同 fixture `contracts/published/http-api/plc-facts-v1/vectors.json`，5 处 `include_str!` 无法读取，未运行测试。只读复制该 fixture 并核对源/副本 SHA-256 均为 `9a5ae0e90a006a7e450ec12557868e9eda20690f4853b6ae29aea2bdf714e782` 后，以完全相同命令重跑 exit 0、1 passed；实际保存、激活、移除、再次激活、历史显式新身份导入并重开。 |
| `E2 cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib daa019_active_version_and_reimport_preserve_old_samples_queue_and_receipt -- --test-threads=1 --nocapture` | exit 0、1 passed；运行的是未修改的正式候选测试本体，覆盖实际持久存储和服务调用、合成样本、fake 回执、队列及旧表逐项不变，新身份无 generation/绑定并默认停用。 |

两次成功测试有既有 `empty_for_test` dead-code 编译警告；二者当时使用同一临时测试二进制 SHA-256 `b31e9e3a513a4a247b5058a46c17135efd891987fc97bc05fcbe903e8dcdc178`，该路径随后由下述临时追加测试重新编译。测试 profile、target、源码副本均仅属本次自检；只含合成测试数据，没有真实 PLC 或 POST。

为在**同一个**含旧样本及上报回执的合成 PLC 上核对全部身份，再仅在临时副本 `catalog_export_tests.rs` 的 `daa019_active_version_and_reimport_preserve_old_samples_queue_and_receipt` 附加断言：保存旧 PLC 的 DB/点/来源 ID；导入后检查新 DB/点数各与旧数相等、各 ID 与旧对象分离、恰有一个新逻辑来源且每个新 DB 的 catalog binding 均引用该来源；前后快照增查 `configuration_contexts`、`reporting_identity`、`sample_upload_settings`，并核对每条旧 source archive 完整行仍存在。该测试本来还逐表比较旧 `plc_sources`（含 generation/sequence）、reporting bindings/generations/cycles、collection cycles、samples、delivery、uploads、attempts、configuration revisions；其中合成回执是 fake response，未发送 POST。按上表第二条 `E2 cargo test ... --lib daa019_active_version_and_reimport_preserve_old_samples_queue_and_receipt -- --test-threads=1 --nocapture` 原命令重跑，exit 0、1 passed，profile 从旧配置保存/激活、造合成样本和回执、移除并激活移除版本，到新身份实际确认导入均执行；这是服务操作而非 GUI。正式 `catalog_export_tests.rs` SHA-256 `72a1240e626d7874dfcb18f24505dcc3c71d1bf7bebe7d12fc393ece1a8d4f32`，该临时测试文件 SHA-256 `43b0ea9575837d4a07280eb91cdf1981ecc9c8e729bd40ac5840cebfc6460359`；重编译临时二进制 SHA-256 `f8d099162b3ec412c87468dc448b9335e97788fa892a064b8a36a6d35b897f3a`。正式候选文件未变。

以上仅为 Development 服务级证据，不能替代协调者的 B/C 真实原生文件往返。独立临时根暂留供协调者和 fresh Verification 核对上述自检，待证据不再依赖且确认无进程占用后只清理该任务自有根；不处理共享临时根或用户 profile。

记录完整性：从当前文本去掉 r2 附录、把元数据两处恢复为 r1，重建得到 r1 tasks SHA-256 `5d057f30062e49a20271ace72424758621cb44b0407a1b30cbe6daa75d685d0c`，与接续前完全一致；Python 尾随空格检查为 0，`git diff --check -- automation-world/data-acquisition-agent` exit 0。核对脚本第一版误在已保留的末尾换行后再追加换行，SHA 断言 exit 1；不修改文档，纠正脚本后重建结果一致。协调者的 B/C 文件往返、保护核对与任务对象清理仍未报告，不得记作完成。Verification 和 Human Owner 最终验收均待后续独立进行。

### r7 §4.1 B/C 协调者原生操作与 Development 只读复核

2026-11-18，协调者报告在实际两端 `.local/dev` 原生界面完成以下操作，Development 独立只读复算实际文件 SHA 和内容。DAA 使用 `env -u DAA_ENV_FILE -u DAA006_NATIVE_SEED_ROOT DAA_PROFILE_DIR=/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/.local/dev DAA_PLC_READ_ALLOWED=false`；DAA 原生 app binary SHA-256 `5aaf397a16a61ea7bec116a004c0478c595e6ee444309d75aeb3393609d1b67a`，DS app binary SHA-256 `883121ba395a2631ab658062903af92e87b64c12bf8eb2b26e36e43af285d8af`，均从下述实际联测 app bundle 核对。此轮 DAA 未激活、未采集或上报，DS 未启动模拟，未进行真实 POST。

- B：复用早前 DAA-017 已实际激活并移除的合成来源 JSON，seed SHA-256 `5198f7fef382f9524b81c66275b76cbdb779deb7741df16d3005f809bf6662e3`，原本机 PLC `e1dc3ad5-305f-4367-af1b-92333a582730`。DAA 经明确选择导入停用的 L1 `a123de20-3d26-4961-819f-0b00708e82cf`，由 `saved_draft` 实际导出 F1，SHA-256 `117f0614a63de4fd11e7dce14a50ed445be87137ce9a47e2cd295bd701973261`，所选草稿 ETag `60e75fe3-df4b-4eca-83b6-ed1d0155c8bb`、payload SHA-256 `eb544ca983f8a442b0d88f3b1869c4d9b391abce26ee02b07122bff989c8f17d`。DS 实际导入、保存 v6 并重导 F2，SHA-256 `ed5a0ddecb223803c6201727718e723a8f9a96168122f098c3271d1f6bc33570`，saved revision `f4b55b18-4bfd-4cf1-b385-9dc73cb48b95`、payload SHA-256 `865a68b41631a412effc33f318b01882fa81f28c201e0c8e642664f2f9f8b237`。L1 尚在当前草稿时，DAA 界面明确拒绝同源 F2；正常移除 L1 并保存、不激活后，明确选择新本机实例，实际导入为停用 L2 `79294849-b7c7-4a58-bc47-5836fe4bc2a0`，L2 的 `saved_draft` 再导出 F3，SHA-256 `840379d35815349025cbf6f450d47561fbc590969a7cefd2fdab2527b7d6e2cb`，草稿 ETag `440d3fea-b28a-44c6-aa84-e069aed8f0a8`、payload SHA-256 `58caa22ea5e3020daf18d9f0af29610a16a29da8d80b8847d84aac4fad10f5d6`。协调者正常 GUI 删除 L2 并保存，DS 两个本任务测试草稿实例已删除并保存。
- C：DAA 对原有 `DEV-PLC-A` 已保存的普通 DB/UDT 来源只读导出，文件 SHA-256 `e609252a4212d2c0f4587d89abc34fc8acbbf763a83c777a90eb5242dbd8336e`，`saved_draft` payload SHA-256 `4b5f702b35a52ee90719a2d32795d96613600441bfbdf881bcef27fcdefee622`。DS 实际导入、保存并重导，文件 SHA-256 `bede8f759b4c06aab2f0cfd23bf70c03eada10c1efed2d3d3d3322e763973dd1`；DAA 原生界面对该文件因同源实例仍在 active 而明确拒绝，没有提交。该测试使用现有真实配置作只读输入，不把它称为合成配置。

Development 对 seed、F1/F2/F3 和 C 的两份文件逐一 `shasum -a 256`，与上述值一致；用 Python 解析后仅排除各端 `source_enabled`、连接端点和 export 头，按外部 ID 排序比较其余合同字段：seed→F1→F2→F3 与 C 的 DAA→DS 文件均一致，包括 origin、DB/点 ID、技术名、数据类型、字节/位地址、source_path、双语显示名及 description；PLC 名称和协议也一致。B 为 1 DB/4 点，包含 BOOL/INT/REAL/STRING[10]；C 为 1 DB/3 点，包含 BOOL/INT/REAL。DAA 文件 producer 为 `data_acquisition_agent`、state 为 `saved_draft` 且 DB 层缺省 enabled；DS 文件 producer 为 `device_simulator`、state 为 `saved_revision` 且 DB 层有 enabled。各文件真实输出时间、版本和启用含义不同，不要求整文件哈希相等。

误操作事实：协调者曾误点 L1 的“测试连接”，界面返回“PLC 操作队列繁忙或对象不存在”；L1 未激活，未能建立连接。使用的 DAA 读取开关为 `DAA_PLC_READ_ALLOWED=false`；不能把本次操作记成从未尝试测试连接或把该返回当成设备连接成功。

保护复核以 `/private/tmp/ds005-daa019-roundtrip-vdmwh6dt/baseline-hashes.json`（SHA-256 `2550195d9bd33e04e8396478bd546f08da589920b4e49470e9508d1c427d778d`）为前测基线；文件只读、两端联测目录暂留。Development 在 GUI 清理 L2 后，用 SQLite `mode=ro&immutable=1`、`PRAGMA query_only=ON` 只读检查：原 8 个 revision ID/记录 SHA 与基线 8/8 相同，各 payload 自身 SHA 均正确；active `b94d8b79-5e89-44f7-989d-ae5d80e1bef9`、previous `9acbff9e-0539-4b91-b397-a6d7cf1a1368` 不变，最终草稿 payload SHA 与基线均为 `4b5f702b35a52ee90719a2d32795d96613600441bfbdf881bcef27fcdefee622`，所以其中原 PLC、普通来源、组及点配置与基线一致。

按协调者提供的原 SQL 排序及 `sha256(json.dumps(rows,sort_keys=True,ensure_ascii=False,default=lambda x:x.hex() if isinstance(x,bytes) else str(x),separators=(',',':')).encode())` 重算：`sample_uploads` 全行 69 条 SHA `548809948e519b88d518c7dd64754115b37c56165b3cca281f0ce6a00879ba72`、`sample_upload_attempts` 全行 73 条 SHA `76bbec1635f4a33d7a9e6a9c2af88046bf7d50403c26f4648ffaee22e7b48b15`、`reporting_bindings` 全行 1 条 SHA `90d148f04c36ffd1811e0c35af3b4b122d4091bdca0f5fc06df8615d077ac4f7`、原 PLC 的 `plc_sources` 全行 1 条 SHA `fe5fc638ce938e6a58363c41f1485dbec4570ad4e226faaaa6e0f0e2fe2a72d7` 均与基线一致；`samples` 按原基线只比较 `id,sha256`，118 条 SHA `e8a63271908d6c5e5f9b7f455d9010e78d789f1a1190a75ad53ed6d80d676bef` 相同，当前 118 条 payload 各自与其 SHA 一致，旧合成 PLC 仍有 11 条样本。`samples` 其他列及 `sample_delivery` 无前测行级摘要，不能宣称这些列已作前后逐行哈希比对。L1/L2 目前均无 `plc_sources`、samples 或 reporting binding。

`configuration_contexts` 基线没有行级 SHA，因此不能声称进行了前后逐行哈希对比；联测前协调者检查输出为 8 条 context、19 条来源引用、缺失归档引用 0，Development 联测后复查同为 8/19/0。当前 8 行均为 schema v1，payload/SHA 各与当前对应的 8 个旧 revision 逐字一致，全部 19 条来源归档内容 SHA 有效。联测前原始检查位于当前会话 rollout `/Users/jason/.codex/sessions/2026/11/17/rollout-2026-11-17T23-32-54-01a1ea23-c141-7303-afa2-eb00f14811db.jsonl` 第 53 行的 `[716]`/`[717]`，但当时未保存每行摘要。旧 seed 来源归档仍在，F2 来源归档当前也存在；正常审计和本任务来源可能增加，不能说整个 profile 零写或直接清除归档。

协调者当时在 PLC 列表观察到 L2 存在且停用，之后为导出手工选择 L2；F3 四点 `source_enabled` 均 false，但当时未在点位页观察导入后的默认 PLC 选择与分组。按 D19-04，协调者正使用 DS 重开后真实重导文件执行最小补核；其结果、清理及补核后的保护复查尚未报告，本阶段仍非 handoff。

### 重开后的界面补核及最终保护复查

协调者随后重开 DS 并从同一 `saved_revision` `f4b55b18-4bfd-4cf1-b385-9dc73cb48b95` 重新实际导出两份文件：合成来源 SHA-256 `5c9fa568c7d3d866cee55539d94a317cb53107b3ead548805794cfa073471a92`；普通 DB/UDT 来源 SHA-256 `04c194da54cf35902f1fe52d20c1aa68bdab869fdd226db039a60da8c8d62168`。Development 只读解析并验证，两份文件分别与先前 DS 输出除 `exported_at` 外全文一致，版本及 payload SHA 保持。

协调者使用重开后的合成文件在 DAA GUI 再次历史回导，预览新本机 L3 `ac12bbc8-ecba-4b99-afe7-efe9b580a89e`，确认并保存后没有手工选 PLC，直接进入“点位与采集组配置”：PLC 下拉自动显示 `DS003_QA2_TEST_20261117`，DB 下拉显示“请选择”，四点均为“未分组”、启用“否”。协调者随即只读核对已保存草稿：该名称唯一的 PLC ID 确为 L3，PLC 停用，4 点的 enabled 均 false 且 group ID 均为空，包含 1 DB、1 逻辑来源。此为本次 L3 的实际界面观察；没有直接截获 IPC 返回值，也没有补称 L2 的自动选中。服务测试已断言 `importedLocalPlcId` 是实际提交 ID，Node 测试覆盖前端据此选择及清除 DB；三类证据分别保留。

协调者随后通过正常 DAA GUI 移除 L3 并保存，PLC 列表仅剩 `DEV-PLC-A`；对重开后的普通 DB/UDT 来源文件发起 DAA 预览时，界面显示“此来源仍在草稿、活动或运行配置中…”，确认按钮禁用，取消且未提交。DAA 以正常 Cmd-Q 退出。整个补核未激活、采集或上报，也未触发真实连接或 POST。

Development 在补核结束、数据库文件无进程打开且没有 WAL 文件时，再以 SQLite `mode=ro&immutable=1` 和 `PRAGMA query_only=ON` 执行上节同一基线 SQL 与 SHA 序列化：原 8 个 revision ID/SHA 及 payload 校验全部一致，active/previous 和草稿 SHA 均与基线一致，草稿仅包含原 PLC；118 条 sample 的 ID/SHA、69 条 uploads 全行、73 条 attempts 全行、1 条 reporting binding 全行和原 PLC source 全行的摘要仍均一致，118 条 sample 当前 payload SHA 均有效，旧合成 PLC 仍为 11 条样本。L1/L2/L3 均无本机 `plc_sources`、samples 或 reporting binding；`runtime_metadata.clean_exit=1`。当前 8 条 context 均与对应旧 revision 的 payload/SHA 一致，19 条来源引用及物理内容 SHA 有效。原 seed、F2、L3 输入的物理来源归档各仍有 1 行；这是正常可追溯来源记录，不在 SQLite 中直接清除。上节对缺少 context、samples 其他列及 `sample_delivery` 前测行级摘要的限制仍然适用，不能把当前自洽等同于对这些表全部列做过前后哈希比较。

### Development → fresh-context Verification 交接

- 精确目标为 `aiis-ics-arch::DAA-019 r2`，批准后 spec SHA-256 `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`，父 `ARCH-PLC-001 r7` SHA-256 `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`。交付为正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`、HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 上的未提交差异，不是临时源码副本或 commit。上文 34 项文件 SHA 清单按后续两组替换构成最终候选；交接前正式树 34/34 与完整清单 `candidate-sha256-final2.txt`（SHA `2800fc8f912950e92307bce9944d0624d4d1725955935d70ac6d158a076a9511`）一致。本 Development 另写本 tasks，未改 spec、checklist 或其他任务事实。
- DEV self-check、正式入口构建、Node/Vue/Rust 结果及失败重跑见上文；r7 A 的合成持久化服务测试、B/C 两端原生实际文件及重开补核分别记录，不互相冒充。中英文用户手册已说明导入导出、来源与版本、显式目标及新本机身份不合并历史；具体行为以源码和手册为准。
- 已通过正常应用删除 L1、L2、L3 和 DS 任务测试草稿实例；不直接删除用户配置、历史或已保留来源归档。`/private/tmp/ds005-daa019-roundtrip-vdmwh6dt` 中真实文件、基线及两端 app bundle，`/private/tmp/daa019-dev.MKLyerrV` 中原隔离验证材料，以及 `/private/tmp/daa019-r2-dev.c0EWK6bZ` 中自有补充测试材料暂留供 fresh Verification 核对；在不再承担证据作用、核实归属和无占用后由协调者按 workflow 回收，不删除用户 `.local/dev` 或既有工具生成目录。
- 已知限制：旧版二进制读取新增配置元数据的兼容性未验证；Windows、VM、真实 PLC、真实 POST、生产部署与发布不在本轮验证范围。上述误点测试连接、未直接捕获的 IPC 返回、用户 profile 前测 context/samples 其他列/sample_delivery 行级摘要缺失均如实保留，交 Verification 独立评估；Development 不给出 QA verdict 或 Human Owner 最终验收。

## r2 独立 QA 失败后的索引返工及重新交接

独立 Verification 的本任务 `checklist.md`（读取时 SHA-256 `a470f1ea2d7e20360eb84ba1a1f86b625e9e658bb07f63e911072112f54e421d`）记录 `qa_failed`：本任务新增的 catalog-export service、command、原生存储测试、Vue 对话框和 Node 测试未同步 `CODE_INDEX.md`。该文件位于已批准 r2 allowlist；本次只修改该索引及本 tasks，保留之前的全部实施、失败和自检事实，不修改 checklist、spec、产品源码或用户数据。此前指示不改索引的工作安排不构成 Human Owner 豁免，现据独立 QA 的实际发现修正。

在保留既有条目、原有文件风格及其他内容的前提下，将索引范围描述由 catalog-import 扩为 catalog-import / catalog-export，并新增以下五项与现有职责对应的相对链接：

- `src-tauri/src/services/catalog_export.rs`：保存版本的 PLC 预览、来源及绑定验证和原子不覆盖文件导出。
- `src-tauri/src/commands/catalog_export.rs`：导出 IPC 及与预览令牌绑定的原生目录选择。
- `src-tauri/src/infrastructure/local_store/catalog_export_tests.rs`：合成 SQLite 导出、冲突、活动版本和历史样本/队列隔离测试。
- `src/app/plc/components/CatalogExportDialog.vue`：保存版本及 PLC 选择、预览、目录确认和逐实例结果。
- `tests/plc-catalog-export.test.mjs`：以内存 IPC 检查导出对话框状态、目录取消及逐实例结果。

返工前 `CODE_INDEX.md` SHA-256 `b3921c1b35b7fbaac9a04265ca4355cf2836d6da2837a5c98cf7fce95e034bf4`；返工后 SHA-256 `9a1c7e94713f36d024849cee926da5b01194c7e2363933a3e32e3ea81f72a03a`。Development 实际检查：`git diff -- automation-world/data-acquisition-agent/CODE_INDEX.md` 仅显示一处范围描述和五条索引；`git diff --check -- automation-world/data-acquisition-agent/CODE_INDEX.md` exit 0；Python 扫描全部 19 个相对链接，目标均为存在的文件、上述五项各恰有一条，且无尾随空格。此次只改文档，不重建二进制或触碰 `.local/dev`；上文对应 34 项产品候选的测试和构建结果未因文档修改而冒称重跑。

新的精确 Development 候选为上文最终 34 项加以下一项，共 35 项；重新逐项计算正式工作树文件 SHA，35/35 一致：

```text
9a1c7e94713f36d024849cee926da5b01194c7e2363933a3e32e3ea81f72a03a  CODE_INDEX.md
```

完整 35 项清单由原 `/private/tmp/daa019-dev.MKLyerrV/candidate-sha256-final2.txt` 的 34 行原样加上上述一行构成，保存在任务自有 `/private/tmp/daa019-index-rework.EEKrDEG1/candidate-sha256.txt`，SHA-256 `40dadba1d4704605bf6cb89c581f3258a46605f7884bdab1ff5a71cece890875`；待 fresh Verification 不再依赖并由协调者确认归属及无占用后回收，不清理共享临时根或用户 profile。交付仍为正式树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的未提交差异，HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`；DAA-019 r2 规格 SHA-256 仍为 `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`。

本返工只处理已证实的索引缺漏；原 `qa_failed` 结论与独立证据阻塞不因此消失。用户 profile 旧 context、样本其他列和 `sample_delivery` 缺前测逐行基线，不能由当前自洽倒证之前的行内容；L2 的原生 IPC 返回/自动选中与再导出未在同一操作中直接记录，不能把 L3 的观察倒记为 L2。英文原生界面检查由协调者另行执行，未计入本次 Development 自检结果。需重新启动 fresh-context Verification，由其独立判断；Development 不改 checklist，不给 QA verdict 或 Human Owner 最终验收。

### 协调者英文原生界面补证

协调者报告：使用同一 35 项候选和 DAA `.local/dev`，在原生界面顶栏切换英语后，PLC configuration 页实际显示 `Import PLC JSON` 与 `Export PLC JSON`。打开导入对话框，可见英文标题、提示及 `Choose` / `Cancel`，随后取消；打开导出对话框，勾选原 `DEV-PLC-A` 并执行 `Preview selected PLCs`，可见英文来源、目标及确认文案，未选择目录或写文件。点位页同一技术点在英文界面显示 `switch`，切回中文后显示 `开关`。协调者报告此次未修改草稿、激活、采集或上报；退出后 `runtime_metadata.clean_exit=1`。

这是协调者实测的上述入口与单个点位语言切换，不冒称 Development 亲自操作，也不代表所有英文路径均已检查。原 QA1 `qa_failed`、用户 profile 前测行级基线限制和同一 L2 的直接返回/自动选择证据限制均保留；是否解除相关证据阻塞由后续独立 Verification 判定。35 项产品及索引候选清单与 SHA 不变。

## r2 用户操作手册补充及 Development 交接

2026-11-18，Human Owner 在手动往返期间要求把创建 PLC、导入点位、编辑显示名及 JSON 交换的步骤写清楚。本次不改变产品范围、验收或实现，仅更新 r2 已批准白名单中的 `USER_GUIDE.zh-CN.md` 和 `USER_GUIDE.md` 第 2 节，并记录本交接；未改 spec、checklist、代码或 `.local/dev`。两份手册此前的未提交内容及 QA 历史均保留。

两份指南按目的区分 JSON 直接新建 PLC、普通 DB/UDT 来源、已有 PLC 导出和实际采集；逐步说明 PLC 弹窗保存、源文件及块选择、差异预览、标准布局/人工地址核对、点位双语和注释、采集组与启用、JSON 目标确认/逐台导出、显式激活和工作台操作。特别说明 DAA 当前没有手工新增单点按钮，JSON 来源导入的新 PLC 和点默认停用、未分组；现有同源实例会拒绝导入而不覆盖，只有历史存在时显式选择新本机身份，旧历史和上报绑定不继承。普通采集与真实上报均为后续单独动作。

DEV self-check（正式工作树）：按页面、对话框、状态方法及 `common` / `plc` 双语 locale 对照操作步骤；`git diff --check -- automation-world/data-acquisition-agent/USER_GUIDE.zh-CN.md automation-world/data-acquisition-agent/USER_GUIDE.md` exit 0。Python 扫描两本手册 38 个相对文件及标题锚点链接，缺失 0；分别校对 22 个中、英文按钮/标题字面量，缺失 0。只做文档修改和静态检查，未新跑编译、自动化产品测试或原生操作；先前 QA 及用户执行往返的结论和限制不因此改变。

精确交付为 `aiis-ics-arch::DAA-019 r2`、正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`、HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 的未提交差异；spec SHA-256 仍为 `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`。对前述 35 项候选清单逐项复算，除以下两份手册外其余 33 项一致：

```text
fc6de733bcaa2871c41c28249586a33e7e6bfcce769ab14c27e653b2d0c0e99c  USER_GUIDE.md
00c7e067b3037406408596fb87070c027a50478dec7fa3dd0be03d97452b0686  USER_GUIDE.zh-CN.md
```

此版本交 fresh-context Verification 复核，不授予 QA verdict 或 Human Owner 最终验收。`qa_blocked` 原因、既有历史保护证据限制、当前手动往返尚未完成及待清理资源均须保留，不因手册更新关闭。

### 手册同源冲突说明返工及重新交接

协调者转达独立复核发现：上次双语手册对同源冲突后的移除步骤笼统写为必须激活，未区分实例只存在草稿的情形。现仅修改两本指南 2.4 对应段落：实例只存在草稿时，正常移除并保存草稿后可重试；活动或运行配置仍有实例时，按原流程停采、断连、移除并保存草稿，显式激活移除后的配置再重试。保留移除前业务影响核对、同源不覆盖与历史隔离说明。用户实际本轮往返和 QA verdict 由协调者与 Verification 记录，不在此倒写。

自检：对照 DAA-019 r2 §3 与 `configuration.rs` 的当前配置同源/端点检查；`git diff --check -- automation-world/data-acquisition-agent/USER_GUIDE.md automation-world/data-acquisition-agent/USER_GUIDE.zh-CN.md` exit 0。对原 35 项候选逐项复算，无缺失，除两本指南外其余 33 项一致。本轮未修改代码、spec、checklist 或用户 profile，未运行编译或原生操作；界面现有 `catalog_origin_conflict` 文案仍对全部情形笼统提示激活，本次并未修改该文案，已如实通知协调者。

在上节交接基础上替换两本指南为以下最新 SHA-256，其余候选和正式工作树/HEAD 不变：

```text
b889b15bc8cf31421230c29c2ef7367421f28949c2b3ce1e6d3aa58728300f37  USER_GUIDE.md
689a5cfd51712543b5b5fa60c9e4143155d87b2f57603607c2fd587619f00c11  USER_GUIDE.zh-CN.md
```

此候选重新交 fresh-context Verification；原 QA 及证据限制完整保留，不由 Development 宣称 QA verdict 或 Human Owner 最终验收。

### 同源说明的操作路径与英文导航补充

根据协调者转达的独立复核意见，两本指南 2.4 在先核对业务影响、确需移除已有实例的前提下，明确写出「PLC 配置 → 对应行编辑 → 移除 → 确认 → 顶部保存草稿」；仅草稿存在时保存后可重试，活动或运行配置仍有实例时需按原流程停采、断连并激活移除后的配置。英文 2.1 的导航修正为界面实际的 `Configuration → PLC configuration`。未改产品 locale、代码、spec、checklist 或用户 profile。

自检：对照 `diagnostics/index.vue` 的移除及确认动作、两种语言的 `navigation.json` / `common.json`，导航和编辑、移除、确认、保存标签一致；`git diff --check -- automation-world/data-acquisition-agent/USER_GUIDE.md automation-world/data-acquisition-agent/USER_GUIDE.zh-CN.md` exit 0。原 35 项清单除两本手册外 33 项仍一致；本次未运行原生操作。最新候选替换上节手册 SHA-256 为：

```text
e1575f9af0ed4b39fb4ab439cc67b0aef6eb4b45042253fb460e50076f8a99d3  USER_GUIDE.md
d427d6d3da286ac5600f1abc9d8e94b3c18dfb8a91a099350dcd4cb2a9eba9c0  USER_GUIDE.zh-CN.md
```

产品 `catalog_origin_conflict` 现有中英文提示仍笼统要求激活，且用户正在手动操作；本次仅做文档修正，已将最小 locale 文案调整的范围评估交协调者。正式工作树和 HEAD 不变；此候选重新交 fresh-context Verification，原 QA 与证据限制均保留。

### DB 长度、目录来源与停用步骤补充

协调者转达独立复核意见后，双语手册 2.2 补充：普通来源新增 DB 的 `65536` 字节是初始值，不代表真实长度；标准推算只有所有点均符合并参与非人工偏移确认时才更新理论长度，否则应依据实际 PLC 资料在「源文件与完整结构 → 查看完整结构」填写 DB 长度，关闭后在顶部保存草稿。2.2/2.4 还说明已有 JSON 目录 DB 的 PLC 禁用「选择源文件」，不能追加 DB/UDT。2.3 补充批量禁用并取消分组及单点关闭启用（不自动取消分组）的区别。

自检对照 `tia_source/reconcile.rs` 的新增/既有 DB 长度、`plc_layout.rs` 的确认条件、`SourceImportPanel.vue` 的目录禁用和长度编辑、点表分组/编辑实现，以及两种语言界面标签。初查有一条 `rg` 命令因 zsh 的不存在文件 glob 未匹配而失败，改用实际 `src-tauri/src` 路径检索后确认；`git diff --check -- automation-world/data-acquisition-agent/USER_GUIDE.md automation-world/data-acquisition-agent/USER_GUIDE.zh-CN.md` exit 0。原 35 项候选其余 33 项一致；没有修改产品代码、locale、spec、checklist 或用户 profile，也未运行原生操作。最新手册 SHA-256 为：

```text
9db2d0e4f4ec59e78809205449c42e0c5fbf458923c2f54ca4c76dd7fcb49e77  USER_GUIDE.md
db8dff473617f1c7781014e0fccb13bc4a4bc039fc1d5efeee84af5fb13cd3b6  USER_GUIDE.zh-CN.md
```

正式工作树和 HEAD 不变；此候选重新交 fresh-context Verification。上节 DAA 产品冲突提示尚未修改，既有 QA 和证据限制保留。

### 同源冲突中英文提示修正及 Development 交接

协调者报告 Human Owner 已完成当前 DAA 往返及测试实例清理、保存草稿，且 DAA 界面没有待提交操作；本 Development 未自行操作或核验该 profile。依据已批准的 DAA-019 r2 §3.2、§4 双语 locale 白名单及 D19-04，仅修改 `src/app/plc/locales/{zh-CN,en-US}.json` 的 `catalog_origin_conflict` 一键：说明同源不覆盖，确需移除应先核对影响；仅在草稿中时移除并保存后可重试，活动或运行配置中仍有时须先停采、断连、移除并保存草稿，再显式激活移除后的配置。未改冲突判定、其他业务源码、依赖、spec、checklist 或用户 profile；既有草稿及历史不由本角色处理。

DEV self-check，均在正式 DAA 根目录：

| 操作 | 实际结果 |
| --- | --- |
| `node --test tests/plc-catalog-import.test.mjs` | exit 0，6 passed。 |
| Node `vue-i18n` 加载两个 PLC locale、比较完整叶键并切换语言解析 `plc.catalog.errors.catalog_origin_conflict` | exit 0；中英文各 264 个叶键，结构一致，两种语言均解析到对应新文案。源码 `src/locales/index.ts` 按 `app/<module>/locales` 以 `plc` 命名空间装配；只读核查 `local.label` 的错误码解析。首查装配入口的 `rg` 因 zsh 的 `src/i18n*` 无匹配而失败，改用 `rg ... src` 后定位真实入口。此为程序级语言解析，不冒称原生界面切换。 |
| `pnpm exec vue-tsc --noEmit` | exit 0。 |
| `pnpm exec vite build --outDir /private/tmp/daa019-locale-JKjeIr/ui --emptyOutDir` | exit 0；Vite 报第三方 PURE 注释及大 chunk 警告。只读核对构建 JS 包含两种新文案后，已仅回收本任务自建临时构建目录。 |
| `git diff --check` 限本次两份 locale 与两份手册 | exit 0。 |

本轮没有重跑 DAA 原生 GUI 或中英文原生切换；用户刚刚的往返、后续清理与 profile 保护证据由协调者及独立 Verification 按实际记录。原 QA 及历史基线限制继续保留，不以此文案自检替代。

精确候选为 `aiis-ics-arch::DAA-019 r2` 正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`、HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 未提交差异；spec SHA-256 `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`。对原 35 项候选清单逐项复算，31 项相同，四项替换为：

```text
9db2d0e4f4ec59e78809205449c42e0c5fbf458923c2f54ca4c76dd7fcb49e77  USER_GUIDE.md
db8dff473617f1c7781014e0fccb13bc4a4bc039fc1d5efeee84af5fb13cd3b6  USER_GUIDE.zh-CN.md
0c155e4aec53e44396662fc274a761307124c601cf1e8013ed90ddcefcb4c6a4  src/app/plc/locales/en-US.json
4a67351e4aece572719766b83bf6e81fb6f765c758d36333e54cd0d723de3a2f  src/app/plc/locales/zh-CN.json
```

Development 将本精确候选重新交 fresh-context Verification；不授予 QA verdict 或 Human Owner 最终验收。

### Human Owner 新一轮手动往返与只读对账

2026-11-18，Human Owner 按协调者的逐步指引操作实际两端 `.local/dev`；以下界面操作为 Human Owner 报告，不冒称本 Development 的自动化原生操作。DAA 中原合成实例 L1 `4670e3bd-8d51-4734-84d8-303b3d2afca2` 仍在草稿时导入 DS 文件，Owner 报告界面拒绝同源；随后通过界面移除 L1 并保存草稿，未激活，再导入同一 DS 文件。Owner 报告新 L2 导入确认后未手工选择即显示该 PLC 和 4 点，随后对该同一 L2 导出，最后通过正常界面移除 L2 并保存草稿。协调者报告在 L2 移除前只读核对已保存草稿：新本地 PLC ID `7d2ca225-da04-4548-b755-22a174c0fd22`，4 点均停用、未分组；外部 origin PLC ID 仍为 `e1dc3ad5-305f-4367-af1b-92333a582730`。本角色不把协调者草稿检查或 Owner 报告冒充亲自观察界面，也未捕获此次 IPC 的 `importedLocalPlcId`。

本 Development 对同一任务临时根 `/private/tmp/plc-json-owner-manual-82_5g47q/daa-export/` 的三个实际文件独立只读解析及 SHA-256 核对，均与协调者交接一致：

| 文件及角色 | 文件 SHA-256 | 选择的配置 |
| --- | --- | --- |
| `4670e3bd-8d51-4734-84d8-303b3d2afca2.json`：DAA F1 | `63260610d54cb339d2807366abf078a0682ceab034f6adb06a8385237e2cdd68` | `saved_draft`，标识 `356bcb4f-7a5c-4d81-9b82-78ed07c643a7` |
| `66155773-770a-42ea-9ad9-cf72be59766d.json`：DS F2 | `c62949dcfef4c054c7f0147a35e10af9095523e67e416f1ae2445b29f7dc8ec0` | `saved_revision`，v7 revision `63124411-7ad9-4e7e-aad1-39d5965b2bca` |
| `7d2ca225-da04-4548-b755-22a174c0fd22.json`：DAA F3 | `e14176aca6f28fb3e188d2904a29c22de89dad4e16fc7f0df132fb1a30f38ca2` | `saved_draft`，标识 `40f5162f-8a92-4011-9409-50b9e1078af8` |

文件 producer 分别为 DAA、DS、DAA，均为 1 DB、4 点，4 点的 `source_enabled` 均为 false；DAA 文件按合同省略 DB 层 `source_enabled`，DS 文件包含该字段。将各文件的 export 头、连接端点及两端启用字段排除，按外部 DB/点 ID 排序比较，其余内容一致，包括 origin、DB/点 ID、技术名、类型、字节/位地址、source_path、双语显示名及描述；不要求整份文件 SHA 相同。

使用本轮操作前完整逐行基线 `full-baseline.json`（SHA-256 `dfc8bee1006da84f98a3efe6298a892df435ea146b6f56a34a08d228fe438269`），本 Development 通过 SQLite URI `mode=ro`、`PRAGMA query_only=ON` 和只读事务重算 DAA config/runtime 及 DS config：每行以 `json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':'), default=lambda x: {'bytes_hex': x.hex()} if isinstance(x, bytes) else str(x)).encode()` 做 SHA-256，与前测排序后的行哈希多重集比较。所有基线既有行均在当前对应表中逐行保留；DAA 原 8 个配置 revision、activation、contexts、samples、`sample_delivery`、队列及回执等既有行未改变。DAA 草稿原始 payload SHA 与前测均为 `4b5f702b35a52ee90719a2d32795d96613600441bfbdf881bcef27fcdefee622`，当前草稿仅含原 `DEV-PLC-A`；DAA `source_documents` 新增 1 行、`runtime_events` 新增 9 行，故不声称 profile 零写。

DS 所有基线既有行哈希亦保持；配置 revision、source blob 和 source version 各新增 1 行。DS 当前草稿的 `instances` 为空，payload 与当前存储的 SHA 自校验相符，但因保留本轮来源而与本轮前草稿 SHA 不同。以上对账只覆盖该基线列出的 DAA/DS 配置及运行表与单独比较的草稿 payload，不将未列入表声称已经比较。

本轮前测只能证明**这一轮**操作前后的可比行，不可倒证上一轮未保存前测的旧 context、样本其他列及 `sample_delivery`。本次未捕获 L2 的实际 IPC 返回 ID；Owner 的未手选自动选中报告、协调者的草稿只读检查和本 Development 的文件/数据库复算是不同证据。文件和基线暂存于上述自有临时根，待独立复核不再依赖且协调者确认无占用后清理；不直接清理用户 profile 或历史。交 fresh-context Verification 独立评估，不由 Development 改 checklist、给 QA verdict 或代替 Human Owner 最终验收。

### QA3 文案缺陷返工与 Development 交接

独立 Verification 的 QA3 记录 `F-DAA019-QA3-001`（返工时 checklist SHA-256 `0f556176f7d525bed03c09a8c104848b7e42e3d792ec4ec65165a5afdaf3813e`）：`catalog_origin_conflict` 被导入当前同源和 PLC 内多个目录来源不一致共用，之前的文案仅描述同源并建议移除/激活，对来源不一致不准确。完整检索 Rust 错误码调用点，确认 `configuration.rs` 的当前同源及多 DB 来源不一致、`catalog_export.rs` 的多 DB 来源不一致三处生产分支；前端 import/export 均经现有 `local.label` 使用同一 locale 键。

在 DAA-019 r2 已批准白名单内，仅修改 `src/app/plc/locales/{zh-CN,en-US}.json` 的该键，改为通用「PLC 来源身份存在冲突，核对当前配置与点位目录来源，参阅手册 PLC JSON 导入导出章节」，不臆断具体原因、不建议移除或激活。具体导入场景的条件步骤已在双语手册 2.4；本次未改变 UI 结构、错误码、IPC、冲突逻辑、依赖或用户 profile，不触碰 spec 和 checklist。原 QA 失败和证据限制完整保留。

DEV 自检（正式 DAA 根目录）：`node --test tests/plc-catalog-import.test.mjs tests/plc-catalog-export.test.mjs` exit 0、8 passed；Node `vue-i18n` 加载中英 PLC locale，完整叶键各 264 且一致，两语言均解析同一错误码并检查通用文案不含移除/断连/激活建议，exit 0；`pnpm exec vue-tsc --noEmit` exit 0；`pnpm exec vite build --outDir /private/tmp/daa019-qa3-NhFUNc/ui --emptyOutDir` exit 0，有第三方 PURE 注释和大 chunk 警告，独立核对构建 JS 含两个新文案后只回收此任务自建临时目录；`git diff --check` 限两份 locale exit 0。未重跑原生界面、用户操作、真实 PLC 或上报；程序级翻译检查不冒充原生中英文切换。

精确候选为 `aiis-ics-arch::DAA-019 r2` 正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`、HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 未提交差异；spec SHA-256 `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`。原 35 项清单复算 31 项相同，以下四项为此候选：

```text
9db2d0e4f4ec59e78809205449c42e0c5fbf458923c2f54ca4c76dd7fcb49e77  USER_GUIDE.md
db8dff473617f1c7781014e0fccb13bc4a4bc039fc1d5efeee84af5fb13cd3b6  USER_GUIDE.zh-CN.md
0d02cbd85a0b4dc9096925728d2698f5d811e24030894fa29c65552c58097eee  src/app/plc/locales/en-US.json
715e385a8e82449c12b6b03f6a7ab213bf9f9a51723898587ae9b1a160d144df  src/app/plc/locales/zh-CN.json
```

Development 将精确候选重新交 fresh-context Verification；原 QA verdict、旧轮前测及同次 IPC 证据限制仍由独立 Verification 评估，不由 Development 决定最终验收。

### 双语操作手册整理与 Development 交接（2026-11-18，Asia/Shanghai）

- `DAA-019 r2`，沿用已批准的双语手册范围。Human Owner 要求简练、完整地写清新增 PLC 和配置点位时容易遗漏的操作。Development `/root/daa_guide` 在正式交付树 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 的未提交基线上只修改两份用户手册，并追加本记录。保留其他任务的既有差异。
- 两份手册在顶部直达第 2 节，按手头文件或目标选择路线。普通来源路线覆盖添加或复用 PLC、逐页选 DB、预览后确认、逐 DB 核地址与实际长度、人工确认、分组与启用。JSON 路线覆盖直接新建草稿、目标及全点位核对、导出来源与写出结果，以及同源冲突和历史新身份。仅交换与实际采集各自有完成点。采集路线按保存、激活、连接、开始采集及本地样本核对展开。
- 对照 PLC 配置页和点位页、`SourceImportPanel.vue`、`CatalogImportDialog.vue`、`CatalogExportDialog.vue`、`ConfigRevisionBar.vue`、采集状态页及 `useLocalAcquisitionConsole.ts`，核实按钮、前置条件及保存动作。Python 3 标准库只读校验两份 Markdown 的相对链接及锚点（48 项）、第 2 节与两个 locale 的按钮/字段文本（92 项）及双语流程步数（3/5/3/4/4/3），exit 0。`git diff --check -- automation-world/data-acquisition-agent/USER_GUIDE.md automation-world/data-acquisition-agent/USER_GUIDE.zh-CN.md` exit 0。此次为文档改动，未重跑代码构建、测试或原生操作。
- 协调者报告，Human Owner 明确要求删除旧验证工件后，协调者经占用检查清理任务自有临时目录，未触及两端 `.local/dev`。本 Development 用 Python 3 `os.path.lexists` 只读复查以下七处均已不存在，exit 0。它们在 `/private/tmp` 下，分别为 `ds005-daa019-roundtrip-vdmwh6dt`、`daa019-dev.MKLyerrV`、`daa019-index-rework.EEKrDEG1`、`daa019-qa.yLy006l9`、`daa019-r2-dev.c0EWK6bZ`、`plc-json-owner-manual-82_5g47q`、`arch-plc-002-predecessor-fpjq3d7g`。历史记录和结论保留，之后无法用这些临时原件复核。本轮未创建测试目录或运行产物。

本轮仅交接下列两份手册及本追加记录给 fresh-context Verification。对应 spec SHA-256 为 `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`，父 `ARCH-PLC-001 r7` spec SHA-256 为 `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`。此前的完整产品候选和证据各按其时间点解释。旧轮前测及同次原生 IPC 返回值缺口不由本轮文档整理解除。

```text
b096f7cc578d48ec9736ef2a358908f5aa3e87127e0794848c68b241f5734624  USER_GUIDE.md
7e2b44d4af6d205bd3507c13a54b4dfbce20a24d07369702ad4b7029f5a4aafc  USER_GUIDE.zh-CN.md
```

### F-DAA019-QA5-001 手册返修与 Development 交接（2026-11-18，Asia/Shanghai）

在正式交付树 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 的未提交基线上，Development `/root/daa_guide` 各修正两份手册 §2.5 步骤 2 一处。默认取 PLC 名，缺少 `.json` 后缀才补上，后缀不区分大小写。核对 `CatalogExportDialog.vue` 的实际默认名表达式和 ARCH-PLC-002 E01。Node ESM 提取该表达式，断言 `LineA`、`LineA.json`、`LineA.JSON`、`LineA.JsOn` 四例均通过，exit 0。两份手册的 `git diff --check` exit 0。仅静态复核，无 GUI、用户 profile 或运行数据操作。

将 `DAA-019 r2`（spec SHA-256 `a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`）的以下两份手册交 fresh-context Verification 限定复验。既有验证和证据缺口按其原范围保留。

```text
e6e78aa6aa37607f3ad1f87460195fb94a88a4353ff2727c97bab60e807d7fe0  USER_GUIDE.md
70449aa68c3c4d821f8a86e47269f224e1925c70b9f87ef4484b8b69c6c5d72e  USER_GUIDE.zh-CN.md
```

## DAA-019 r3 Development 文档交接（2026-11-18，Asia/Shanghai）

**活动 Revision：`aiis-ics-arch::DAA-019 r3`。交接状态：`developer_handoff`。** Human Owner 在协调者列明五份精确草案后回复「批准这组收尾草案」。核对 [本任务批准规格](spec.md) SHA-256 `e0eb80fefbc14a664dfc380f1081691ad8e415d5ca4cff0f66fe9890612e29bd`，同次精确批准的 [ARCH-PLC-001 r8](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) SHA-256 `38085d5f0dd5d9db444008b9e04963371ddff3995cbb050641281ce6517931e5`。本段为最新交接；原 r2 文件头及全部历史按写前字节保留。写前 SHA-256 是 `28052c99001d5bb808012f2682ccadccd4185aadf48a91c663114f82b4f147cd`，与 QA6 当时读取的 tasks 一致。移除本段及新增分隔空行可重建该文件。

### R3-01 正式交付树与既有候选

正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`、分支 `main`、HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。交付为未提交工作树上的文档增量。树内已有其他任务和角色的差异，HEAD 本身不足以识别产品候选。

- 原 34 项最终清单 SHA-256 `2800fc8f912950e92307bce9944d0624d4d1725955935d70ac6d158a076a9511`，可由上文初表及之后两组替换重建。Development 自检、随后的协调者原生记录和 [QA1–QA6](checklist.md) 各自只覆盖原时间点。QA1 `qa_failed` 记录索引缺项；QA2 复核索引修复，整体 `qa_blocked`。QA3 复核后轮实际文件及对账，发现共享冲突错误码文案过于具体，记录 `qa_failed`。QA4 独立限定复验通用双语冲突文案并关闭 F-DAA019-QA3-001，整体仍 `qa_blocked`。QA4 的 35 项排序清单 SHA-256 `03acaaf5b4605c246d9148badaf8e514135b02a0645edbbc04d1093fbb46b858`。
- [ARCH-PLC-002 r1 Development](../../../plans/ARCH-PLC-002-plc-json-export-feedback/tasks.md) 以该 35 项和额外样式文件固定 36 项 DAA 前序基线，其中 11 项变化。后继合同接替原固定 UUID 文件名，覆盖逐 PLC 命名与校验、选择器授权及逐项结果反馈。该任务 QA1 E04 失败、QA2 返工复验和 `owner_accepted` 归其自身。相对 QA1，后继 QA2 的返工只触达两个 DS 文件。其 E06 DAA 单台改名导出与报告属于该任务独立证据。[ARCH-PLC-002 独立验证](../../../plans/ARCH-PLC-002-plc-json-export-feedback/checklist.md)
- DAA-019 QA5 对当时双语手册记录 `qa_failed`（F-DAA019-QA5-001）。返工后，QA6 以当时实际源码的默认文件名表达式、五个用例和本地链接静态复验。只有文件名未带大小写不敏感的 `.json` 后缀时才补上。现行英文 `USER_GUIDE.md` 的 SHA-256 为 `e6e78aa6aa37607f3ad1f87460195fb94a88a4353ff2727c97bab60e807d7fe0`，中文 `USER_GUIDE.zh-CN.md` 为 `70449aa68c3c4d821f8a86e47269f224e1925c70b9f87ef4484b8b69c6c5d72e`，均与 QA6 匹配。QA6 关闭局部缺陷，r2 整体仍 `qa_blocked`。[DAA-019 独立验证](checklist.md)

重建 QA4 的 35 项并与现树比对，25 项原字节相同。8 个重叠路径匹配 ARCH-PLC-002 交付表，分别是 `src-tauri/src/commands/catalog_export.rs`、`src-tauri/src/infrastructure/local_store/{catalog_export_tests,catalog_import_tests}.rs`、`src-tauri/src/services/catalog_export.rs`、`src/app/plc/components/CatalogExportDialog.vue`、`src/app/plc/locales/{en-US,zh-CN}.json`、`tests/plc-catalog-export.test.mjs`。另有 QA4 清单之外的 `src/styles/app.css` 匹配后继交付表。原清单的剩余两项是上述 QA6 手册，也已区别于 ARCH-PLC-002 当时的手册字节。按这些来源可重建现行涉及的 36 项 DAA 文件清单，模块相对路径升序，每行「小写 SHA-256、两个 ASCII 空格、路径、LF」，整份清单 SHA-256 为 `91cd78967c3fc67f6c8891641057924fecf1400267d9e2cc9027e8c03e5f45f4`。QA4 locale 和旧原生候选与现行组合树没有整候选同一性证据，现行组合树没有完整行为复验。

### R3-02 / R3-03 原生报告、独立比对与既有检查

- Human Owner 报告在两端 `.local/dev` 做过中英文切换和 DAA→DS→DAA 文件往返。后轮在当前同源合成实例仍在草稿时回导被拒绝，正常移除并保存草稿、未激活后，明确选择作为历史来源的新本机实例导入。Owner 报告确认后无需手选即显示新 L2 及四个点，并对同一 L2 再导出，随后经正常界面移除该测试实例、保存草稿。协调者另报告当时只读检查草稿，证实本机新身份、保留外部 origin、4 点停用未分组。本轮 GUI 操作为 Owner 报告，独立 QA 未亲历，未直接截获同次原生 IPC 的 `importedLocalPlcId`。早轮 L2 的提交及再导出和另一次 L3 的自动选中仍按分次记录。协调者的英文原生补核只覆盖入口、弹窗、取消及导出预览，英文实际提交和写文件未核。
- 上文 Development 和 QA3 当时分别只读核对后轮三份实际文件，F1、F2、F3 的 SHA-256 分别是 `63260610d54cb339d2807366abf078a0682ceab034f6adb06a8385237e2cdd68`、`c62949dcfef4c054c7f0147a35e10af9095523e67e416f1ae2445b29f7dc8ec0`、`e14176aca6f28fb3e188d2904a29c22de89dad4e16fc7f0df132fb1a30f38ca2`。producer 依次 DAA、DS、DAA，各 1 DB / 4 点。按外部 DB / 点 ID 排序，排除 export 头、连接目标及两端启用字段后，外部 origin、DB/点身份、技术名、类型、地址、source_path、双语及 description 一致。DAA 省略 DB 层 `source_enabled`，DS 有该字段，点层记录停用。文件比对与 GUI、IPC 事实各按独立层级。早轮 catalog 和普通 DB/UDT 文件比较仍见 QA1/QA2。
- 原服务合成 profile 检查覆盖空侧双语和独立 description、严格导入和冲突、显式新身份、外部映射重开及再导出、旧 generation/sequence、样本、绑定、队列和回执隔离。QA1 的一项写出一项失败由当时隔离副本中的定向真实服务检查证明，同名竞争与 stale 见增强测试二进制，OS 故障注入及双原生 GUI 并发未做。Node 替身覆盖按返回 ID 选中、清空 DB、目录取消及未知时不猜测。fake transport 用不同中英文 sentinel 经过实际 v2 正文构造，未发真实 POST。PLC 配置页的双语入口、单个导入弹窗挂载、键对称、冲突文案及操作手册沿用当时的源码、语言资源、程序与文档检查。原 DEV/QA 的 Rust、Node、类型和构建命令、异常退出、提前返回和重跑限制仍见上文及原独立记录，无新增产品验证。[DAA-019 独立验证](checklist.md)

### R3-04 协调者既有本机真实 v2 只读对账

2026-11-18，协调者经用户允许只读观察本机该次 `seq=91–103` 共 13 条实际 v2 上报，均有匹配 `sampleId` 的可靠回执，状态 `committed`、outcome 为 `created` 或 `duplicate`，本地请求正文字节与回执 SHA 均与存储记录一致。对应 MySQL `plc_facts_history` 的来源身份、正文 SHA 和所核 3 点的点名、类型、值及质量均一致。此配置至少一实际点的中英文显示名均非空，13 份正文均未见显示名字段或对应的两种文本，后端点集未见显示名字段。`plc_facts_latest` 的 3 点均为 `good`、`seq=103`。协调者另报告对应时段的 DS 日志未见 `WARN` / `ERROR`。

以上只限一次本机配置、所列 13 条、3 个点及当时时点。本角色仅阅读协调者已有 transcript，不是本角色或独立 QA 亲验。私有定位为 `~/.codex/sessions/2026/11/16/rollout-2026-11-16T09-24-47-01a1e1f4-eb7e-74d2-b055-3696e1a855ec.jsonl` 约第 28239–28242 行的样本、回执与 history/latest 对比，以及第 28257–28260 行的双语排除核对；行号变动可按内容定位。仓库只保留脱敏结论、归属与定位。

### R3-05 保留的缺口和资源状态

- 早轮 `configuration_contexts` 只有 8/19/0 汇总，旧 `samples` 仅核 ID/SHA，其余列及 `sample_delivery` 缺可比逐行前值。早轮能比较的 revision、队列、绑定、回执等保留原结果。QA3 后一轮 37 表比对仅说明各自事务、基线所列行及时点，DAA 有正常来源与审计新增，DS 有新 revision 和来源，草稿另行比较。各库事务没有同一时点的原子快照，无法倒证旧轮逐行保持，也未据此判定旧数据损坏。
- 同次原生 IPC 返回 ID 仍未直接观察。早轮协调者曾误点测试连接并报告未建立连接。关联 DAA-018 原生隔离事件可能涉及重启或重绑默认真实 profile，写入和影响范围仍未知。本交接保留该事实。[原隔离记录](../DAA-018-bilingual-point-display-names/checklist.md)
- 旧二进制兼容、Windows/VM、真实 PLC、异常或未知回执的实际路径、其他点集与配置、持续运行和生产采用均未由本次有限材料验证。旧原生输出、前测基线、测试副本及固定前序快照已经按 Owner 要求由协调者清理，七处定位见上文「双语操作手册整理」及 QA5。原件已不可读，历史摘要和限制保留。本轮无新建、恢复或清理的测试资源。[原资源记录](checklist.md)

### R3-06 DEV self-check 与交接

本轮唯一写入文件为 `automation-world/data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/tasks.md`。用 `git status --porcelain=v1 --untracked-files=all`、`git rev-parse HEAD`、`git worktree list` 核对正式树，`shasum -a 256` 核对批准规格，Python 3 `pathlib/hashlib` 比较候选、原文前缀、两份 spec、写前 checklist SHA-256 `1442d5e2ff1d237d3b592e9bb5c32fbd7590c4e461e2b0174ab50e9fd4b391`，校验新增段相对链接及尾随空白，exit 0。另以 `git diff --no-index --check /dev/null <tasks.md>` 覆盖未追踪文件，无空白诊断，差异退出码 1。未重跑产品测试或构建，未启动应用、访问用户 profile、SQLite/MySQL、PLC、DS 日志或网络，未采集、上报或执行 Git 写入。DEV 只做文档与源码身份核对。

交当前协调者串行启动 fresh-context Verification，独立复核本 r3 精确规格、完整 bundle、追加范围、候选和历史证据归属，以及 R3-01 至 R3-06 所列限制。DAA-019 r2 的历史 verdict 保留。本 r3 的独立文档 verdict 和 Human Owner 最终验收均待各自阶段决定。

### R3-06 交接摘要更正与重新交接（2026-11-18，Asia/Shanghai）

[QA7](checklist.md) 记录 F-DAA019-R3-001。上节 DEV self-check 转录初次 r3 交接写入前的 `checklist.md` 摘要时漏写 `8b`，原记录只有 62 位。正确的 64 位 SHA-256 为 `1442d5e2ff1d237d3b592e9bb5c8b32fbd7590c4e461e2b0174ab50e9fd4b391`。Python 3 `hashlib` 按 QA7 标题分隔处取历史前缀，在内存中复算得到该值。含 QA7 的完整 checklist SHA-256 为 `3d45a4b855980d55f7d22816f765175374d23a3c65778e91b326091c81b8919d`。

本次只追加本段以更正文档中的摘要转录笔误；QA7 的 `qa_failed` 为文档复核结论。将本段及新增分隔空行去掉后，原 `tasks.md` 的 SHA-256 仍为 `7b0f91fb35a145aeb1ce231fdf9a78f63f68112e0d65d49e6c0915272526af4a`，包含原文件头及前次交接的全部字节。DAA-019 r2 的 `qa_blocked` 和原未验证边界继续保留，包括同次原生 IPC 返回 ID、旧轮逐行前值、隔离事件影响及已清理工件不可复验。更正没有引入产品验证结果。

**活动 Revision `aiis-ics-arch::DAA-019 r3`，状态 `developer_handoff`。** 正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main`，HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，未提交文档增量。批准后的 [spec.md](spec.md) SHA-256 为 `e0eb80fefbc14a664dfc380f1081691ad8e415d5ca4cff0f66fe9890612e29bd`。DEV 自检用 Python 3 复算前缀及 bundle 文件摘要，检查新增段两条相对链接和尾随空白，均通过。未重跑测试或构建，未创建测试资源，未访问应用、GUI、用户 profile、SQLite、MySQL、网络或 PLC。交协调者启动新的 fresh-context Verification 复核 R3-06 的摘要及追加交接；复核 verdict 和 Human Owner 最终验收由各自阶段决定。
