Task ID: ARCH-PLC-002
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Handoff: QA1 后的 DS 回执关联返工交 fresh-context Verification。两端 E06 原生证据保留。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# ARCH-PLC-002 r1 Development

2026-11-18（Asia/Shanghai）核对 Human Owner 对 `aiis-ics-arch::ARCH-PLC-002 r1` 的批准。正式工作树 HEAD 为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，批准后 [spec.md](spec.md) SHA-256 为 `a4d2744297d3882f90c4f865d2ef8ec0b8e2f5ada30ce4fc754be4913ae2b349`。启动时任务目录只有 spec。按协调者交接，等待 DS-005 / DAA-019 的前序候选和取证固定后才编辑产品源码。

## 实施与自检计划

1. 两端分别将文件名与本机 ID、内容字节和目录绑定到现有短期预览。校验扩展名、长度、非法字符、保留名及批内重名。沿用原子不覆盖写入。用隔离 Rust 测试核对实际文件名、落盘字节、取消与替换竞争等行为。
2. 两端在现有导出对话框显示逐台名称、编辑与行错误；在固定标题区显示结果摘要。用 Vue 组件和 IPC 替身核对多选、旧票据失效、部分结果和未知回执。核对双语键、类型及构建。
3. 同步四份双语手册。记录正式工作树的候选、命令和限制，交协调者启动 fresh-context Verification。原生 E06 由协调者另行组织。

## DS 实施及候选文件

协调者在修改 DS 前将前序 QA 候选和本任务触达的额外文件共 30 项原字节固定在 `/private/tmp/arch-plc-002-predecessor-fpjq3d7g/device-simulator`，并报告前序 25 项 QA 清单 SHA-256 为 `e0c3df10cc048a570d07a67168b58d82361b45c5d4bdaabaeaa203dde1d89284`。DS 与任务记录由本 Development 执行。DAA 文件由另一个 Development 执行，协调者在其前序 QA 后固定基线。

DS 通过所选实例 ID 将完整文件名绑定到预览票据。Rust 校验路径字符、字节长度、扩展名、尾随字符、保留名和批内重名。两个已有 DAA 私有来源前缀也予以拒绝，使合法导出名可进入既有 DAA 导入流程。无效名称返回各实例的原因和无票据结果。原生重选目录前撤销旧目录授权，取消时使票据失效。写出使用预览中同一份内容、SHA-256 和经原生选择的目录描述符，沿用排他原子落盘。

DS 对话框按选中的保存版本为每台提供默认名和输入框。已确认回执按实例 ID 保留名称、目标文件名、状态、失败原因和成功项摘要。缺失回执对应的行显示未知，主动重新开始前继续使用原有检查确认。顶部的结果提示不随点位详情区滚动。双语手册按新流程使用实际文件名示例。

正式工作树与固定的 30 项 DS 前序基线逐项比较。有 12 项变更，均在 r1 范围内。路径相对于 `automation-world/device-simulator/`。

| 文件 | SHA-256 |
| --- | --- |
| `USER_GUIDE.md` | `6c0e22e3e18825c75704699024a5e637480d82483f07b872849731369fa66b51` |
| `USER_GUIDE.zh-CN.md` | `72e5d7f37df109b81a8503fa6fb24a6a6b1b807c6ea422006d91821b9d04f4e9` |
| `runtime/src/services/catalog_export.rs` | `d777ba84f1cff64058eebe3274692b1a9236d9e6160b2749bbd6f6b954dd8370` |
| `runtime/tests/plc_catalog_export.rs` | `fc6f965692eb4fda499188b4a6c403606b98dcf850118b96740a52ed2568d828` |
| `runtime/tests/plc_catalog_import.rs` | `f42852a39663a344007b37ef472e1f367cacea0a02dbe63fe3ce6c8ba84c9f41` |
| `src/app/simulator/components/CatalogExportDialog.vue` | `f285c1ff8172c91e1dcd95472f4e06fd060616576564c10b2f99385f2b0edccc` |
| `src/app/simulator/locales/en-US.json` | `bfd031853eb53613bd19ac1a730dac09160af08c46ead2798176e75709c27251` |
| `src/app/simulator/locales/zh-CN.json` | `ab552e1cb00af7876afa4b850ccdda388566d76ff365bb9140b1b01125a474d3` |
| `src/services/deviceSimulator.ts` | `4972faaefb9d36696a9b6e961793b8510059e9a0669e46c3eabf2408a528faa3` |
| `src/styles/app.css` | `cbc172734ecba501a421276e28759e5e22da0193fe56c27fe10846ac1184916a` |
| `src-tauri/src/commands/catalog_export.rs` | `ea974dc14f088b166023a37d43fb7b9947a7293ceca0394891b3fd891c04a1ed` |
| `tests/plc-catalog-export.test.mjs` | `63e03f3f9d10ff93c69e5612ae081598117e0508b6b059b572e8c97e88515ff6` |

## DS 自检

环境为 macOS 15.7.7（24G720）arm64、Rust 1.89.0、Node 22.19.0 和 pnpm 11.11.0。以下工作目录为正式 DS 应用目录。临时根 `/private/tmp/arch-plc-002-dev.hkE5uJ8v` 是本任务创建的隔离目录。

| 检查 | 命令及结果 |
| --- | --- |
| Rust 导出与导入 | 设置 `CARGO_TARGET_DIR` 为临时根下 `ds-target`，`DS_TEST_RUN_ROOT` 为临时根下的各组专用目录，运行 `cargo test --manifest-path runtime/Cargo.toml --locked --offline --features test-automation --test plc_catalog_export --test plc_catalog_import -- --test-threads=1`。导出 13 项通过，覆盖实际中文名写出、批内重名、单项冲突与部分成功、原字节和 SHA-256、并发、符号链接、目录替换与撤销。导入见下方重跑记录。 |
| Vue 行为与回归 | `node --test tests/plc-catalog-export.test.mjs tests/plc-catalog-import.test.mjs` exit 0，11 项通过。Vue SFC 加 IPC 替身覆盖名称默认值、单台与多台提交、逐行错误、票据撤销、完整与部分回执、全部失败和未知分支。不启动浏览器或 Tauri。 |
| 类型与前端构建 | `pnpm exec vue-tsc --noEmit && pnpm exec vite build --outDir /private/tmp/arch-plc-002-dev.hkE5uJ8v/ds-vite-final` exit 0。Vite 报依赖 PURE 注释和大体积 chunk 警告。最终输出中核对了最新英文未知结果文案，JS SHA-256 为 `c84a41ca645592c497909838a9518d220bb660b48f00b6f015e6f365df55d5ce`。较早输出位于同一临时根的 `ds-vite`。 |
| 桌面桥接 | `CARGO_TARGET_DIR=/private/tmp/arch-plc-002-dev.hkE5uJ8v/ds-tauri-target CARGO_BUILD_JOBS=6 cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --features native-s7 --lib catalog_receipt` exit 0，1 项通过。按正常 native-s7 feature 构建桌面库并验证部分与未知回执薄桥。 |
| 格式、链接与范围 | `cargo fmt --manifest-path runtime/Cargo.toml --check`、`cargo fmt --manifest-path src-tauri/Cargo.toml --check` 及限定 DS 和本 bundle 的 `git diff --check` 均 exit 0。Python 检查 DS 两份手册 54 处本地文件与标题锚点，无缺失。 |

Rust 首次组合（`ds-profiles`）与当次增量重编后的组合（`ds-profiles-final`）均为 exit 101。两次均有 13 项导出和 7 项导入通过，既有大文件用例 `oversized_complete_output_is_rejected_per_instance_without_overwrite` 在调用导出前的 `publish` 返回 `save_receipt_unknown`。两次热缓存串行重跑（`ds-profiles-retry`、最后源码的 `ds-profiles-final-retry`）均为 exit 0，13 项导出和 8 项导入通过。该套件中的可选外部 DAA 文件探针未供应路径，所列结果没有独立跨应用文件证据。测试没有更新导入业务或改变既有断言。

本 Development 没有启动 GUI、修改用户 profile、发起采集或上报。E06 原生确认由协调者安排，结果单独记录。隔离构建及合成验证资源保留到协调者确认不再依赖后处理。

### DS E06 原生证据

Human Owner 报告在 macOS DS 选择已保存 v7，把单台实例的文件名改为 `DS-自定义测试.json`，导出后对话框顶部显示成功。原生操作和界面观察由 Human Owner 完成。本 Development 与协调者未亲眼观察顶部提示。

协调者随后只读检查 `/private/tmp/plc002-owner-vl_d8us2/ds/DS-自定义测试.json`，实际文件 SHA-256 为 `f24a68fd9c65433918748fef3fe6bddeff793cee404cab20375bc5b3a3572942`，producer 为 DS，保存 revision 为 `63124411-7ad9-4e7e-aad1-39d5965b2bca`。逐字段比对前序 F2，origin、PLC、DB 与 4 个点均一致。导出后 `lsof` 显示 PID 94265 持有 DS `.local/dev` 配置库，程序为 `src-tauri/target/debug/aiis-device-simulator`，磁盘二进制 SHA-256 为 `0ebc89720cfd1aabc9992420054c0f27d44905cdb1ad7d4e77f4fe5fdd6393e4`。协调者在正式树复核了 Rust 服务和 Vue 组件 SHA，与上表相符。原生文件留供独立 Verification 核对，双语自动检查见 DS 自检表。

## DAA 实施及候选文件

DAA 实施和自检由并行 Development `/root/daa_guide_revision` 执行，以下根据其交接记录，文件 SHA 已由本 Development 在正式工作树复算。协调者固定的 DAA 前序基线位于 `/private/tmp/arch-plc-002-predecessor-fpjq3d7g/data-acquisition-agent`，包含前序 QA 清单 35 项和额外触达文件 1 项。前序 QA 清单 SHA-256 是 `03acaaf5b4605c246d9148badaf8e514135b02a0645edbbc04d1093fbb46b858`。

DAA 从保存草稿或 active 版本列出各台 PLC 的默认名。预览验证调用通过本机 PLC ID 提交逐文件名称，将已校验的名称与对应内容及票据绑定。前序原子不覆盖写入返回逐项状态和摘要。Vue 将返回的回执与已确认的 ID 和文件名匹配，明确拒绝逐项报告失败，缺失回执或 worker 结果不明的项报告未知。双语摘要在对话框标题区保留。Development 中途发现目录重选等待期间旧授权仍可提交，协调者暂停原生验证。最后候选在打开选择器前撤销旧授权，由定向 Rust 用例验证此间旧目录无法提交。

与 36 项固定基线相比，以下 11 项变更均属于批准范围，其他 25 项一致。路径相对于 `automation-world/data-acquisition-agent/`。

| 文件 | SHA-256 |
| --- | --- |
| `USER_GUIDE.md` | `35c8d240ecfb0b24a5ffc1b7bbf66cd6cdc0b78a87dde3c3a824a798f0464339` |
| `USER_GUIDE.zh-CN.md` | `d51b3fa514a9684565a61d8b98e509aba3f95e7746a9cdd57df10a66fd022440` |
| `src/app/plc/components/CatalogExportDialog.vue` | `6f4e6f3d64a02307dfade1048b9ffb31b8a4d6dac7dd03961295945336ac63f2` |
| `src/app/plc/locales/en-US.json` | `1cdf6c108af1e388ecbb8781cba72f80e1d44a59933efc6a076d2706b63691d5` |
| `src/app/plc/locales/zh-CN.json` | `1df07e7c29c609dfb2318939bc909f07235d91ea72aa56b00b74786d2c722716` |
| `src/styles/app.css` | `84909dac3fbe674222f8742c161bf200913e8f6180d807e419c9dde2dec269f4` |
| `src-tauri/src/commands/catalog_export.rs` | `a96b20110b223004bc9fae5c028f044d474e31b012b110de988d561ded808544` |
| `src-tauri/src/infrastructure/local_store/catalog_export_tests.rs` | `c5127b65e939a334e6aa331382693a01c5eab6fbce978a67ef13a8c7b40608cb` |
| `src-tauri/src/infrastructure/local_store/catalog_import_tests.rs` | `a8423aca164a6c8b92ffdf8ecc17008ff539b76a43622b108b695275ae81d40d` |
| `src-tauri/src/services/catalog_export.rs` | `d47e7e386d1a783348ab1a96fefdd7f47fc945edd8a38213e5c178d0a92aaf1e` |
| `tests/plc-catalog-export.test.mjs` | `90f6c10593464ec5b6bb303506b2f7093ab0aa86398ad661d5e33a330fdede5d` |

### DAA 自检

以下命令由 DAA Development 在正式 DAA 应用目录运行。

| 检查 | 命令及结果 |
| --- | --- |
| Vue 行为与回归 | `node --test tests/plc-catalog-export.test.mjs tests/plc-catalog-import.test.mjs` exit 0，11 项通过。 |
| 类型与前端构建 | `pnpm exec vue-tsc --noEmit` 与 `pnpm exec vite build --outDir /private/tmp/arch-plc-002-daa-7Lx7oV/ui --emptyOutDir` 均 exit 0。Vite 报第三方 PURE 注释和大体积 chunk 警告。 |
| Rust | 使用下方隔离命令，`catalog_export` 最终 exit 0，5 项通过。覆盖非法路径与保留名、重名无票据、中文落盘与 SHA、目录重选失败和打开 picker 时旧目录并发提交被拒。最后一处选择器保护补入之前，`catalog_import` exit 0，15 项通过。初次 `arch_plc_002` exit 0，1 项通过。Rust 报既有 `empty_for_test` 未使用警告。 |
| 格式、链接和双语 | `rustfmt --check --edition 2021 --config skip_children=true` 对表中的四个 Rust 文件 exit 0。PLC locale 两种语言各 277 个叶键，键集合一致。两本手册 38 个相对链接和标题锚点通过。`git diff --check -- automation-world/data-acquisition-agent` exit 0。 |

```sh
env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT \
  DAA_PLC_READ_ALLOWED=false \
  CARGO_TARGET_DIR=/private/tmp/arch-plc-002-daa-7Lx7oV/target \
  CARGO_BUILD_JOBS=4 CARGO_NET_OFFLINE=true \
  TMPDIR=/private/tmp/arch-plc-002-daa-7Lx7oV/daa-008-r2-a-fixtures \
  cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib catalog_export -- --test-threads=1
```

DAA Development 使用隔离合成 profile。

### DAA E06 原生证据

Human Owner 报告在 macOS DAA 从已保存草稿导出单台 PLC，使用其自定文件名 `DEV-自定义测试2.json`，并看到对话框顶部显示成功。界面操作和观察由 Human Owner 完成。

协调者随后只读检查 `/private/tmp/plc002-owner-vl_d8us2/daa/DEV-自定义测试2.json`，SHA-256 为 `1a60086e9585520054dd8c23687e9bc75cc262a6d691ca6b1f8ed2aa2d3fa00a`，producer 为 `data_acquisition_agent`，来源类型为 `saved_draft`。与先前 `DEV-PLC-A` 的实际导出文件 `/private/tmp/ds005-daa019-roundtrip-vdmwh6dt/daa-dev-export/f6da5dac-7326-4a6c-bceb-55ad7e74b8cf.json` 比对，origin、PLC、DB 及 3 个点的所有字段一致。协调者的 `lsof` 显示 PID 5774 持有 DAA `.local/dev` 配置库，Tauri debug 二进制 SHA-256 为 `39c3f2f43fd57af48fc437e1df7f38ea6b187f9251798ba1572486b59c771b0a`。Rust 服务和 Vue 导出对话框摘要分别为 `d47e7e386d1a783348ab1a96fefdd7f47fc945edd8a38213e5c178d0a92aaf1e` 和 `6f4e6f3d64a02307dfade1048b9ffb31b8a4d6dac7dd03961295945336ac63f2`，与上表相符。本 Development 另行复算了实际输出文件和这两个源码文件的摘要。

## Developer handoff

- 精确候选为 `aiis-ics-arch::ARCH-PLC-002 r1`，批准后 spec SHA-256 为 `a4d2744297d3882f90c4f865d2ef8ec0b8e2f5ada30ce4fc754be4913ae2b349`。交付是正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的 `main`、HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 上的未提交候选。上表合计 23 个产品、测试和手册文件相对各自固定前序基线有变更。另有本任务 Development 记录。
- DS、DAA 各 30 和 36 项基线逐项复比，变更均属于 r1 允许范围。交接时在仓库根执行 `git diff --check` exit 0，批准后的 spec SHA 复算一致。正式树还含前序任务变更，应以固定原字节和上表摘要确定本任务差异。
- 两端自动化范围、原生操作报告与文件核对、DS 旧导入容量夹具在重编后偶发的 `save_receipt_unknown` 均见上文。Windows 原生行为未验证。未执行真实 PLC 操作、采集、上报、部署或发布。DS-005 与 DAA-019 前序验收状态各按其原记录。
- 本任务隔离测试、编译与前端产物位于 `/private/tmp/arch-plc-002-dev.hkE5uJ8v` 和 `/private/tmp/arch-plc-002-daa-7Lx7oV`。协调者固定的原字节和原生输出位于上述独立目录。在独立验证及协调者确认无运行、后续工作或证据依赖后，按明确归属回收。Human Owner 既有 profile 和历史数据由其保留。
- 协调者已在本次 DAA 原生证据补录前启动 fresh-context Verification。此次只更新 `tasks.md`，检测候选文件和批准规格均保持上文摘要。Verification 独立记录结论，Human Owner 最终验收另行决定。

## QA1 后的返工与新 Developer handoff

2026-11-18（Asia/Shanghai）按 [QA1 记录](checklist.md)返工 E04。DS 逐台按本机实例 ID 核对回执。每台只有一条回执、文件名与确认目标完全一致且状态有效时才采用。缺失、重复、错名或未知状态值的行保留所确认的实例名和文件名，并报告结果未知。其他可信行保留其实际结果和摘要。提交仍为单次调用。

回执回归测试以 Vue SFC 和 IPC 替身复现错名、相互矛盾的重复回执及非法状态。新增测试在修复前 exit 1，错误文件被计为已写入。修复后 `node --test tests/plc-catalog-export.test.mjs tests/plc-catalog-import.test.mjs` exit 0，12 项通过。覆盖异常邻行仍明确失败、缺行、正常部分成功、全部成功及未知时不重复提交。正式 DS 根执行 `pnpm exec vue-tsc --noEmit && pnpm exec vite build --outDir /private/tmp/arch-plc-002-qa1-rework.NggGJYAw/ui` exit 0。构建有第三方 PURE 注释及大 chunk 警告，JS `index-BPTWbf2I.js` SHA-256 为 `b25b3265e1a36c04a00e5d1db88cc045eaabb0d4ce6bb6120308f971002eedfe`。该隔离产物保留至协调者确认复验无依赖。

交接仍为 `aiis-ics-arch::ARCH-PLC-002 r1` 正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`、`main` HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 的未提交候选。spec SHA-256 仍为 `a4d2744297d3882f90c4f865d2ef8ec0b8e2f5ada30ce4fc754be4913ae2b349`。复算 QA1 的 23 个候选文件，21 项摘要一致，以下两项以新摘要替换。仓库根 `git diff --check` exit 0。

| DS 文件 | 返工后 SHA-256 |
| --- | --- |
| `src/app/simulator/components/CatalogExportDialog.vue` | `d98e377fbfcb9d58b065abacbafc476670ec9cdf0016db86df6d9796cd02e92e` |
| `tests/plc-catalog-export.test.mjs` | `f107fde1308786931865e6568670eeb9f9244eea71e9f23d01ac5850dec111fc` |

本轮自检层级为 Vue + IPC 替身及构建，沿用上文两端原生文件与 Human Owner 观察证据。未再次启动原生界面、调用真实 PLC 或重跑 Rust 用例。协调者接收新候选并启动另一轮 fresh-context Verification。

协调者确认 QA1 已持久记录两份 E06 输出的 SHA 及字段比对，输出目录无后续依赖。其检查 `/private/tmp/plc002-owner-vl_d8us2` 内仅有两份预期测试文件、摘要一致且 `lsof` 无打开句柄后，已回收这两份文件和空目录。前序联测证据和固定候选快照保留。此回收由协调者执行。

## QA2 后资源收尾

2026-11-18（Asia/Shanghai），[QA2 记录](checklist.md)确认以下三个本任务隔离目录已无 QA 证据依赖。协调者报告逐个用 `lsof +D` 确认无打开句柄后已回收，合计约 3.7 GiB。

- `/private/tmp/arch-plc-002-dev.hkE5uJ8v`
- `/private/tmp/arch-plc-002-daa-7Lx7oV`
- `/private/tmp/arch-plc-002-qa1-rework.NggGJYAw`

E06 测试导出目录已按上文回收。固定前序候选 `/private/tmp/arch-plc-002-predecessor-fpjq3d7g` 与旧联测文件仍供 DS-005 和 DAA-019 核对，暂予保留。此处仅追加资源收尾事实。QA2 验证时的 `tasks.md` SHA-256 仍为 `93fe10c0255cf3d31be01e30678cb83efdff08996dab81acf0bf389d25665ee7`，以当时清单记录为准。
