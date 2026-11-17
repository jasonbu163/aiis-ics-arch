Task ID: DAA-018
Revision: r3
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-018 Development 记录

## r3 QA1 返工

独立 Verification 的 QA1 对原交接候选给出 `qa_failed`，`checklist.md` SHA-256 为 `f7778f3652b2f0720f2e617693ee8d5a368ad18b657efa3939d5772032be6699`。F-QA1-001 在合成 profile 复现普通 `daa_save_draft` 可不经命名预览直接修改两台 PLC 的双语名称；此前 DEV 自检未发现该漏洞，原 `developer_handoff` 及其证据保留为历史，不代表返工后的候选。协调者已确认 QA 审计结束并要求在原 r3 allowlist 返工。此时已复核 spec SHA、QA checklist SHA 和原候选 20 文件 hash；GUI/CUA 与疑似真实 profile 操作继续暂停。


### QA1 返工后的 DEV self-check 与 developer_handoff

**实际修复。** `services/local_configuration.rs::save` 在原 ETag 检查后复制旧映射；仅对旧 PLC 已删除、且对应旧点 ID 也已删除的情况，从允许映射及候选中移除该点条目。其余候选映射必须与允许映射精确相等，否则返回既有 `name_preview_required`。原 `protect_derived`、普通保存 CAS 不变。单点命名确认、来源复导确认和偏移确认仍通过各自已验证的内部 `save_candidate` 路径；未新增公开入口或第二次提交。旧双空项可读取且不会因无变更或保存无关字段而自动改写。

`point_display_names_tests.rs` 原先通过普通保存插入两台名称作为复导前置数据，这掩盖了 F-QA1-001；现改为分别经真实命名 preview/confirm 种入。新增正式命令 dispatch 的无预览跨 PLC 新增负例，以及普通保存新增双空项、修改、单侧/双侧清空、删除、删除一台 PLC 同时篡改另一台的负例；拒绝后检查 ETag、draft、source、revision、样本/上下文和账本表。测试同时覆盖 UI 已清理与服务端自行清理的合法 PLC 删除、旧双空项、旧请求、同 ID 原样及改源复导和单次 CAS。整个返工仅修改上述两个批准内文件与本 tasks，未修改 QA checklist、spec 或其他任务文件。

**测试环境和结果。** 仍在唯一工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`；macOS 15.7.7、Rust/Cargo 1.89.0。以下工作目录为 DAA 根目录，`E` 表示环境前缀 `env -u DAA_ENV_FILE -u DAA_PROFILE_DIR -u DAA006_NATIVE_SEED_ROOT CARGO_TARGET_DIR=/private/tmp/daa018-r2-dev-ewnCpRk3/old-target TMPDIR=/private/tmp/daa018-r2-dev-ewnCpRk3/daa-008-r2-a-fixtures DAA_PLC_READ_ALLOWED=false`。逐项测试仅使用该根新建的合成 profile，`daa018_` 的 v2 worker 使用内存 transport；不启动 native app、不读真实 profile、不发送真实网络请求，Cargo `--locked --offline`。

| 命令 | 实际结果 |
| --- | --- |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib point_display_names_plain_save_requires_preview_and_preserves_history -- --test-threads=1` | 修复前 exit 101，1 failed：正式 `daa_save_draft` dispatch 在未预览时返回成功，复现 F-QA1-001；这是预期的失败证据。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib point_display_names -- --test-threads=1` | 修复后 exit 0，7 passed，包括上述负例、跨 PLC 删改、合法删除、旧空项、复导及单次 CAS；16 MiB 测试只覆盖单配置限额。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib daa018_ -- --test-threads=1` | exit 0，3 passed：v2 捕获 transport 对新/旧未发送/冻结重试正文、test-only v1 完整 context 及旧冻结/ACK 保全回归。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib legacy_engine_does_not_dispatch_or_rewrite_inflight_v1_evidence -- --test-threads=1` | exit 0，1 passed；runtime3 原旧发送拒绝与合成 in-flight 证据未变。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib source_import_tests -- --test-threads=1` | exit 0，4 passed。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib point_naming_tests -- --test-threads=1` | exit 0，harness 4 passed；其中 `native_owned_legacy_seed` 因相应环境变量 unset 直接返回，不是 native 证据。 |
| `E cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --bin aiis-data-acquisition-agent` | exit 0；编译检查，不运行 binary。Rust 测试有一条既有 `empty_for_test` dead-code 警告。 |
| `rustfmt --check --edition 2021 src-tauri/src/services/local_configuration.rs src-tauri/src/infrastructure/local_store/point_display_names_tests.rs`；`git diff --check` 对 19 项已跟踪候选 | 均 exit 0。新测试是 untracked；`git diff --no-index --check /dev/null src-tauri/src/infrastructure/local_store/point_display_names_tests.rs` exit 1 因内容不同，无空白错误输出。 |
| `shasum -a 256 -c /private/tmp/daa018-r2-dev-ewnCpRk3/source-manifest-qa1-fix.sha256` | exit 0，20/20 一致；与 QA1 原候选相比恰为以下两项变化。spec、QA checklist SHA 复核不变。 |

返工没有改变前端文件；Node 29、vue-tsc 和 Vite 结果保留在下方 QA1 前历史记录，本轮未重复运行，不称为返工后的新测试。

**返工候选及资源。** 对照 QA1 审定的原 20 文件清单，只有 `src-tauri/src/services/local_configuration.rs`（新 SHA `e037609e73c6e20700c4dc0af3692605f725eaae3f505bfe7407be8eb1260b3a`）和 `src-tauri/src/infrastructure/local_store/point_display_names_tests.rs`（新 SHA `0b7524ad67f508a10601b98d827cb1dcd1a4397f8207a5ed5fe8836c99e45685`）变化；完整新清单文本 SHA-256 `663ab9df588127442dadef64aa1a750cc4a52a5cf425cd34f2ec7fdd237dea50`，路径均相对 DAA 根，整个文件哈希仍含 USER_GUIDE 先前其他人修改。

GUI/CUA、旧普通 native 二进制和最终原生列宽/语言/跨重启行为继续 **not_run**；原生隔离事件可能发生的写入仍未知，不能写为零写，也不能把本 DEV self-check 冒称独立 QA。任务自有 `/private/tmp/daa018-r2-dev-ewnCpRk3` 及其合成 profile、旧二进制、构建产物、两个候选清单保留至独立验证结束且协调者确认无依赖；QA 自有资源、系统诊断和疑似真实数据均未清理。下一 gate 为协调者显式启动新的 fresh-context Verification，复核本返工候选及所有仍未完成项；Human Owner 最终验收另行决定。

```text
4db4d8ffc87cef55ee075d2b3540e1995e9ce8f19bbdddab0ebd0665bcfb33b4  USER_GUIDE.md
dc42d284d038035fcafdc675dd4d872476ed9168cc38478cccd87d2984c1b9d0  USER_GUIDE.zh-CN.md
ee17a47af5772df2d185395eaf7411b848873385b8e8fe9a110afda4dfa6144c  src-tauri/src/domain/local_configuration.rs
bf6649e042775810c65e0d5d2500d9c81bfc28403d85184a76dad8d3fda850b4  src-tauri/src/domain/point_naming.rs
e037609e73c6e20700c4dc0af3692605f725eaae3f505bfe7407be8eb1260b3a  src-tauri/src/services/local_configuration.rs
1bc7490a20708d26ba65ed1221f4e4b6d85ecd4a5bd5aa417f009f3a134e2598  src-tauri/src/services/local_point_naming.rs
5bd7906b2f0149ecd628d57b4ca26e31e26845ed7b802117561ed095e79ee8d7  src-tauri/src/services/local_delivery_tests.rs
48da6719ba6c2aee2c5c47df70cee8cf821bd412d30d9a72df1301019ccf5176  src-tauri/src/infrastructure/local_store/configuration.rs
5f5f3b754deb498e5038b6a86251bef5bdd464594d3be5a1152ddcbf88371480  src-tauri/src/infrastructure/local_store/mod.rs
0b7524ad67f508a10601b98d827cb1dcd1a4397f8207a5ed5fe8836c99e45685  src-tauri/src/infrastructure/local_store/point_display_names_tests.rs
7c2ec202176971fa4bc7383fa77de7fb74022c7586838f5be38bdb057611d694  src-tauri/src/infrastructure/local_store/delivery_tests.rs
01a50c7a0c4afa53d6d97acea414ba9aedbf1ea666f26e06a39fa14ef17ba839  src-tauri/src/infrastructure/local_store/sample_upload_tests.rs
18bfd1fabfd3d12c3b1be39e9755b2441169bcfbf3d4e097e4d4f7517e0d9448  src-tauri/src/infrastructure/local_store/README.md
00b348f00406ae01658f309f4b39ceed3d8e1db73a7bcc91ab84112b958690a9  src-tauri/src/infrastructure/local_store/README.zh-CN.md
f279ee04bc4e79233cb508d5216fc03f047e2d9c31cbece60b3458c022cbc78a  src/services/localAcquisition.ts
868868f4a7d30cb5dabe4f54103648901451c368424e5b474352c70f3000b0ed  src/console/composables/useLocalAcquisitionConsole.ts
69259955ebcbca4166a4ab3079ee012674af03f93d56eaeac578c97345b32c15  src/app/plc/views/points/index.vue
6df8d4b97b0bb82ccf212555fde284c34e0e71794d4c2fb96b9c64f571d55d76  src/app/plc/locales/en-US.json
4691e3de1f0e04325ee2e0384269ef6f48eca7d451e436ae42a57b53e2f6dd20  src/app/plc/locales/zh-CN.json
f6b8bf5e55df6e6f105b367040ddca275f5cabeff99e728263dfbfda6ec3ce58  tests/point-editing.test.mjs
```

## r3 批准及开发进度

已核对 `DAA-018 r3` 为 `owner_approved`，批准后 SHA-256 `1ccb7f8b99d65b60842d0334b91821e9f4fcfb0e920dac38078ac5f47e1c09d3`；父 `ARCH-PLC-001 r4` 为 `owner_approved`，批准后 SHA-256 `10dbba00dd190bc0d40d99b6bfad03072e0ba752d8b55d350af4b3f491485967`。Human Owner 已批准实施范围、父设计及版本衔接；按 r3 恢复既有范围内开发，保留 r1/r2 阻塞事实。旧 v1 测试构造保留完整 context；产品可达 v2 正文必须不含双语显示名。下文保留当时的事件及阻塞事实，并追加恢复后的 DEV 自检与有限 handoff。

### r3 原生验证隔离事件（2026-11-17，Asia/Shanghai）

**事件及当前状态：** 约 11:36–11:40，自有原生候选退出后查询窗口状态时，CUA 显示了不同于合成 profile 的既有业务配置，疑似候选被再次启动或重新绑定时没有保留进程隔离环境，因而读取了默认真实 profile；具体启动/绑定机制尚未确定。Development 已向协调者报告，关闭该候选窗口；随后 CUA 应用清单未再显示候选运行。自发现异常后未再对该配置执行编辑、连接、采集或发送，也未读取、复制、清理、修复或回滚真实 profile、缓存或日志。已暂停后续 DAA 窗口及 profile 操作，等待协调者和 Human Owner 处理；不可把本次事件写成零写。

**先前可确认的受控部分：** 首次受控原生窗口使用的合成 profile 由保留的旧验证二进制创建，包含人工合成 PLC 和四份样本；无自动采集或自动上报。受控 macOS 候选以临时 app bundle、唯一 `CFBundleIdentifier` 和 ad-hoc CodeSign ID `com.aiis.tests.daa018-isolated-ewncprk3` 构建；编译配置使用 `incognito: true`，锁定的 Wry macOS 实现选择 `WKWebsiteDataStore::nonPersistentDataStore`。构建产物及隔离配置位于 `/private/tmp/daa018-r2-dev-ewnCpRk3`。这与正式应用的 bundle ID 和持久 WebKit 配置不同，不能证明正式 WebKit 的跨重启列宽持久化。

首次沙箱内启动的命令为：

```sh
DAA_ENV_FILE=/private/tmp/daa018-r2-dev-ewnCpRk3/old-profile-second/fixture.env \
DAA_PROFILE_DIR=/private/tmp/daa018-r2-dev-ewnCpRk3/old-profile-second \
DAA_PLC_READ_ALLOWED=false TMPDIR=/private/tmp/daa018-r2-dev-ewnCpRk3/tmp \
'/private/tmp/daa018-r2-dev-ewnCpRk3/old-target/debug/bundle/macos/DAA018 Isolated Test.app/Contents/MacOS/aiis-data-acquisition-agent'
```

沙箱内进程 exit 134，没有打开窗口；仅输出合成 profile 的启动日志，macOS 为该次进程生成的诊断报告显示 AppKit `_RegisterApplication` 的 SIGABRT。该诊断报告由系统生成，未删除。随后经自动审批允许，使用同一命令的 `require_escalated` 启动；窗口初始身份、点表及四份合成样本与任务 profile 相符，界面显示 0 连接、0 采集、自动采集/上报关闭。中英文切换分别显示合成显示名的两种语言，编辑框显示两语言及原 comment，修改未保存输入后取消，表格仍显示原合成值。

点表操作列在横向范围外，CUA 无障碍树把“编辑”和“单点诊断”合并到一个单元格。Development 误点击该单元格触发了合成点的单点诊断请求；界面返回需要先连接 PLC，期间未建立连接，且该受控进程显式禁止 PLC 读取。诊断提示关闭后仅使用可见坐标打开编辑并取消。该误触已报告协调者；不是成功读取证据。

**异常发生顺序：** 对受控候选使用 `app.pressKey('super+q')`，随后 `cua.getState()` 的短暂清单仍显示候选；再调用原 app 绑定的 `app.getAXState()` 时，窗口显示非合成业务配置及既有上报统计。没有依据断言该状态来自哪个实际路径，也没有继续检查该路径。界面可见 0 连接、0 采集、自动采集/上报关闭，上报处于停止状态；这些只反映可见状态，不能排除启动/退出期间发生了事件、日志或其他写入。首次点击关闭因 CUA 提示状态变化未执行；重新取得窗口状态后点击其关闭按钮，清单不再显示候选。没有对其他应用执行关闭。

事件涉及未经授权的疑似真实 profile 读取及可能的启动/退出写入；受影响具体文件、数据变化与是否存在其他系统写入均未知。不得通过重新打开、迁移、复制、清理或回滚这些数据自行验证。原生测试、生产使用、跨平台和最终验收均未完成。

**静态修正与已完成部分：** 受控窗口中拖动列宽未生效；核查现有 Element Plus 表头实现发现它要求 table 的 `border` 才处理拖动。已在本任务允许的点表源码加 `border`，未再次启动应用；拖动和恢复默认仍待安全的独立原生验证。先前合成 Rust 的映射/原子确认测试 2 passed；v2 模拟 transport 对旧未发送样本、新样本及冻结重试的单项测试 1 passed；test-only 旧 v1 完整上下文以及旧冻结/ACK 保全测试各 1 passed。自有旧 validation 二进制生成四样本旧 profile，新程序读取旧记录后，旧 validation 二进制面对新映射安全拒绝（exit 2），两库 schema 和相关记录保持；这不证明普通旧 native 的拒绝行为。前端模拟测试 19 passed；这些均不构成独立 QA 或最终验收。

在协调者要求停止 profile/界面操作后，仅做允许范围内的上述源码修复及不启动应用/数据库的静态检查：DAA 目录执行 `pnpm exec vue-tsc --noEmit` exit 0，`pnpm exec vite build --outDir /private/tmp/daa018-r2-dev-ewnCpRk3/ui-static-check --emptyOutDir` exit 0（第三方 pure 注释及大 chunk 警告），相关跟踪文件 `git diff --check` exit 0。该时点新添加的复导/并发/删除 Rust 测试尚未执行；其他完整回归、容量和真实原生列宽测试也未完成。后续经协调者允许的离线合成自检结果见下节；原生列宽验证仍未执行。此前原生候选在补 `border` 之前构建，不能冒称验证了当前源码。


### r3 QA1 前的离线 DEV self-check 与原 developer_handoff（历史）

**恢复边界。** 上述事件后，协调者明确允许逐条确认隔离后的非 GUI 合成单元测试、类型检查和构建；原生窗口、CUA 和疑似真实 profile 操作继续暂停。事件写入范围及受影响文件仍未知，不能认定零写；界面显示停止不等于审计证明。以下 Rust 测试的 `TMPDIR` 指定任务自有目录、`DAA_PLC_READ_ALLOWED=false`，所用测试 profile 由 fixture 在该根下创建，测试不启动原生 app；v2 worker 的 HTTP 被内存 transport 替代，禁止真实发送。Node 测试为内存 IPC 和无 DOM Vue 宿主，不启浏览器、原生 app 或访问 profile。未运行无法证明隔离的全量测试。

事件之前的旧版样本准备是不同的隔离方式：`seed-old.py` 在自有合成 `fixture.env` 中设置 `DAA_PLC_READ_ALLOWED=true`，validation 启动也设置 `read_allowed=true`，为的是生成合成样本；该 feature 只在 debug 构建使用并强制携带任务所有的 `--fixture-file`，`local_supervisor::transport` 选择 `FixtureTransport`。这不是禁止 PLC 读选项，也不是实际设备或网络 I/O，不能与事件后 `false` 的测试混为一谈。

**交付实现。** 唯一候选为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 工作树，基线 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，含大量任务前及并行脏修改。开发仅触达本节清单内的 20 个 DAA 文件及本 `tasks.md`；两个 USER_GUIDE 各只加入本任务对应段落，文件内其他既有改动不属于本任务。未修改本任务 spec/checklist、PLAN、索引、依赖/锁、schema、`facts_wire`、Point/PointFact 或其他模块。

- 配置级可省略映射只接受当前唯一点 UUID 与闭合中英文字符串对象；两侧空时单点提交删除映射。长度按 UTF-8 字节，拒绝 null、缺键、重复键、未知键、越长及孤儿引用。读取 revision/草稿和保存均验证。
- 单点编辑在既有预览候选中一起纳入技术名、两语言及原字段；摘要、token、ETag、有效期及一次 CAS 保留；未提供新字段的旧请求继续使用原命名规则。显示名编辑未更改地址时保留技术名，原 name/comment/address 不为语言切换、打开、取消或其他语言自动填充而改变。原 `protect_derived` 保留。
- 点表按顶栏语言显示；编辑器分别填写两语言，空值不互相猜测。表格列宽接入原公共偏好工具；补 `border` 后的拖拽能力未在原生窗口重测。
- 提交结果未知时禁止新的命名预览/确认、保存、激活、来源导入与偏移确认；失败的无关读取、失败的重读不会清除此状态，成功重新读取配置才解除。不是声称未知提交一定未写。
- 同 ID 来源原样复导及修改来源文本后复导保留名称；原流程对叶子重命名/删除不允许确认，对直接替换点 ID 的普通保存拒绝，PLC 删除清理所属映射并保留另一 PLC。没有为本任务放宽原来源保护或创建点/DB 删除入口。

**命令和结果。** 环境 macOS 15.7.7，Rust/Cargo 1.89.0，Node 22.19.0，pnpm 11.11.0；工作目录均为 DAA 根目录。下表中 `E` 是 `CARGO_TARGET_DIR=/private/tmp/daa018-r2-dev-ewnCpRk3/old-target TMPDIR=/private/tmp/daa018-r2-dev-ewnCpRk3/daa-008-r2-a-fixtures DAA_PLC_READ_ALLOWED=false`；执行 Rust 命令时将此三项作为环境前缀，Node/前端同样使用后两项。Cargo 使用锁文件与 `--offline`；未安装依赖。

| 实际命令 / 检查 | 结果与边界 |
| --- | --- |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib point_display_names -- --test-threads=1` | exit 0，5 passed；覆盖严格对象/UTF-8、一次 CAS（自有 SQLite 临时 trigger 计数）、伪造/超时/跨 PLC、双语清空和旧请求、已变更源同 ID 复导、并发、直接重绑拒绝、PLC 删除和 16 MiB 单配置容量失败。该容量测试不代表全部存储容量阈值均被运行。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib daa018_ -- --test-threads=1` | exit 0，3 passed。实际 v2 worker 使用捕获 transport 收集 4 个旧未发送样本、新样本与冻结重试 body，独立中英文及 comment sentinel 均未进入 v2 正文，name/value 与样本相符且 v2 无 comment，重试 body 与已冻结 bytes 相同；只改变显示名时点定义摘要不变，新 revision 正常变化。另两个为 test-only v1 完整 context/SHA 和旧 revision、样本、旧冻结/ACK 保全。没有真实 POST。 |
| `E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib legacy_engine_does_not_dispatch_or_rewrite_inflight_v1_evidence -- --test-threads=1` | exit 0，1 passed：runtime3 的旧上报 start/resume 拒绝且原 in-flight 证据保留。源码审计 `build_delivery_cycle`、`freeze_cycle` 与旧响应处理由 `#[cfg(test)]` 控制，生产送达从 runtime4 的 v2 worker 进入；这是旧 v1 本地可读而非已恢复旧 v1 发送。 |
| `env -u DAA006_NATIVE_SEED_ROOT E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib point_naming_tests -- --test-threads=1` | exit 0，harness 4 passed；其中 `native_owned_legacy_seed` 因环境变量未设置立即返回，**不作为 native 测试**，其余 3 项实际运行。 |
| `env -u DAA006_NATIVE_SEED_ROOT E cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib source_import_tests -- --test-threads=1` | exit 0，4 passed；来源预览/确认、旧合成历史及回滚回归。 |
| `E cargo check --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --bin aiis-data-acquisition-agent` | exit 0，正式特性和 binary 入口编译检查；不运行二进制，也不证明 PLC 或原生 UI。 |
| `node --test tests/point-editing.test.mjs tests/facts-delivery.test.mjs tests/time-and-history-preferences.test.mjs` | exit 0，29 passed；包括未知结果后失败读取/失败重读不能解锁，成功重读才能编辑，以及编辑前明确先保存其他草稿的边界。Node 提示 MockTimers experimental。 |
| `pnpm exec vue-tsc --noEmit`；`pnpm exec vite build --outDir /private/tmp/daa018-r2-dev-ewnCpRk3/ui-static-check --emptyOutDir` | 均 exit 0；Vite 有第三方 PURE 注释和 >500 kB chunk 警告。构建覆盖最后的前端源码，未启动产物。 |
| `rustfmt --check --edition 2021 src-tauri/src/services/local_point_naming.rs src-tauri/src/infrastructure/local_store/point_display_names_tests.rs` | exit 0。 |
| `git diff --check`（20 项中已跟踪的 DAA 文件） | exit 0；新测试文件用 `git diff --no-index --check /dev/null src-tauri/src/infrastructure/local_store/point_display_names_tests.rs` 返回 1（与空文件不同），无空白错误输出。 |
| Node 递归比较 `src/app/plc/locales/{zh-CN,en-US}.json` 所有键；Python 检查两份 USER_GUIDE 与两份 local_store README 的相对 Markdown 链接 | 两项均 exit 0；语言键差集均空，4 文件 0 缺失链接。 |

旧验证二进制兼容：事件前分别运行 `TASK_PROFILE=old-profile-second python3 /private/tmp/daa018-r2-dev-ewnCpRk3/seed-old.py` 与 `TASK_PROFILE=old-profile-second python3 /private/tmp/daa018-r2-dev-ewnCpRk3/compat.py`，exit 0；前者通过 fixture 产生 4 份样本、1 个旧 revision，后者以明确 `--env-file/--profile-dir/--fixture-file` 使用新 validation 二进制读取旧数据，旧 payload/相关记录不变，再保存新映射；旧 validation 二进制退出 2，错误 `profile_contract_business_admission_failed`，草稿、source、历史表与两库 schema 版本 (2, 4) 没有被旧程序改写。首次兼容脚本将预期错误误写成 `configuration_corrupt`，断言 exit 1；修正预期并在第二个新建合成 profile 完成上述复现，不掩盖首次错误。旧普通 native 二进制面对新配置的结果仍 **not_run**，validation feature 的成功不能替代它。

开发过程中，旧冻结回执保全测试首次误以为只读 IPC 响应直接暴露 body，断言失败；已改为对同一合成数据库查询原冻结 body 并核对 IPC 暴露的 SHA，再由上述 `daa018_` 三项命令实际通过。r2 历史中另有一次 `--exact` 选中 0 tests，未作为通过。

**明确未执行/限制。** 最终源码的原生表头拖拽、恢复默认、切页/重启列宽持久化、完整中英文原生编辑与旧功能回归均 **not_run**；先前 isolated/incognito 原生观察在最终 `border` 和收尾代码之前，只能证明当时受控合成窗口的部分语言/取消行为。非持久 WebKit 与正式应用配置不同，不能证明正式偏好持久性。旧普通 native 二进制兼容及其他操作系统、真实设备和实际网络均未验证；所有 AC 不得整体标记通过。原生访问隔离事件及可能写入仍是已知风险，禁止重新打开、扫描、复制、修改或清理疑似真实数据来追证。

**资源与后续 gate。** 任务唯一临时根 `/private/tmp/daa018-r2-dev-ewnCpRk3` 含自有合成 profile、旧 validation/旧 native 二进制、隔离 Cargo target、测试脚本、incognito 配置与一次原生候选、静态构建和 manifest；由于独立验证和兼容证据尚需复核，保留至协调者确认后续验证不再依赖，再按 workflow 清理已证明任务所有的资源。系统为沙箱启动失败生成的诊断报告未删除；不清理归属不明或任何真实 profile/缓存/日志。未部署、提交或推送。下一步由协调者显式发起 fresh-context Verification，先审查本记录的隔离事件与有限证据；仅 Verification 写 checklist，Human Owner 最终验收另行决定。

**候选文件 SHA-256 清单。** 路径相对 DAA 根；这些 hash 固定整个文件（包括 USER_GUIDE 中任务前改动），并非声明全部差异由本任务创建。该清单文本本身 SHA-256 为 `25f95f341f13caa741cc84b8e24920e66c5e0daaf71b9517229836ba1993a01c`；原始清单另保留于任务临时根。此清单固定 QA1 前的原候选，返工后的两个文件哈希及新清单见上方 r3 QA1 返工记录。工作树仍包含他人并行修改，QA 应只审查本任务范围且勿覆盖。

```text
4db4d8ffc87cef55ee075d2b3540e1995e9ce8f19bbdddab0ebd0665bcfb33b4  USER_GUIDE.md
dc42d284d038035fcafdc675dd4d872476ed9168cc38478cccd87d2984c1b9d0  USER_GUIDE.zh-CN.md
ee17a47af5772df2d185395eaf7411b848873385b8e8fe9a110afda4dfa6144c  src-tauri/src/domain/local_configuration.rs
bf6649e042775810c65e0d5d2500d9c81bfc28403d85184a76dad8d3fda850b4  src-tauri/src/domain/point_naming.rs
e3dc5847b65efc388f502cf83d343331cd9bf60211258cc1d3e930c2f7456e6d  src-tauri/src/services/local_configuration.rs
1bc7490a20708d26ba65ed1221f4e4b6d85ecd4a5bd5aa417f009f3a134e2598  src-tauri/src/services/local_point_naming.rs
5bd7906b2f0149ecd628d57b4ca26e31e26845ed7b802117561ed095e79ee8d7  src-tauri/src/services/local_delivery_tests.rs
48da6719ba6c2aee2c5c47df70cee8cf821bd412d30d9a72df1301019ccf5176  src-tauri/src/infrastructure/local_store/configuration.rs
5f5f3b754deb498e5038b6a86251bef5bdd464594d3be5a1152ddcbf88371480  src-tauri/src/infrastructure/local_store/mod.rs
3a5b76d5b4cb07d0373dceab9444d383402babc61bec9322bdc254a090c0441d  src-tauri/src/infrastructure/local_store/point_display_names_tests.rs
7c2ec202176971fa4bc7383fa77de7fb74022c7586838f5be38bdb057611d694  src-tauri/src/infrastructure/local_store/delivery_tests.rs
01a50c7a0c4afa53d6d97acea414ba9aedbf1ea666f26e06a39fa14ef17ba839  src-tauri/src/infrastructure/local_store/sample_upload_tests.rs
18bfd1fabfd3d12c3b1be39e9755b2441169bcfbf3d4e097e4d4f7517e0d9448  src-tauri/src/infrastructure/local_store/README.md
00b348f00406ae01658f309f4b39ceed3d8e1db73a7bcc91ab84112b958690a9  src-tauri/src/infrastructure/local_store/README.zh-CN.md
f279ee04bc4e79233cb508d5216fc03f047e2d9c31cbece60b3458c022cbc78a  src/services/localAcquisition.ts
868868f4a7d30cb5dabe4f54103648901451c368424e5b474352c70f3000b0ed  src/console/composables/useLocalAcquisitionConsole.ts
69259955ebcbca4166a4ab3079ee012674af03f93d56eaeac578c97345b32c15  src/app/plc/views/points/index.vue
6df8d4b97b0bb82ccf212555fde284c34e0e71794d4c2fb96b9c64f571d55d76  src/app/plc/locales/en-US.json
4691e3de1f0e04325ee2e0384269ef6f48eca7d451e436ae42a57b53e2f6dd20  src/app/plc/locales/zh-CN.json
f6b8bf5e55df6e6f105b367040ddca275f5cabeff99e728263dfbfda6ec3ce58  tests/point-editing.test.mjs
```

## r2 阻塞历史（保留）

## r2 批准及开发进度

Human Owner 已精确批准 DAA-018 r2 及版本衔接；批准后 `spec.md` 的 SHA-256 为 `9d02dbdc03310c4c758c20a833c1f69778ea312ccfe7d42b0bb582389bd7def6`，已核对 `owner_approved`。r2 将命名预览 DTO 和服务加入原 allowlist；单点显示名与原点编辑共用原预览和一次 CAS。实施中发现旧上报构造合同冲突并停止，**尚未完成实现、自检或 handoff**。

### r2 阻塞：历史冻结批次包含完整上下文

`configuration.rs::prepare_context` 保存完整配置；`facts_wire.rs::build_cycle` 原样设置 `Cycle.context_utf8`，`Batch::bytes` 序列化整个 Cycle。`local_store/delivery.rs::freeze_cycle` 用此 Cycle 冻结 `plc-facts/v1` 正文，因此含 `pointDisplayNames` 的上下文会使历史批次正文包含显示名原文，而 r2 §3 / DA18-06 要求历史批次正文不得包含任一显示名。该旧建批路径受 `#[cfg(test)]` 限定；本证据仅证明可运行的历史测试构造链，不代表当前普通生产路径会发送该正文。

按 r2 §6 的旧上传链不兼容停止条件，Development 暂停并已交协调者返回 PM；没有裁剪上下文、修改 `facts_wire`、旧合同或历史数据。下一 gate 是 PM 审视合同与可达性并形成具体修订，Human Owner 精确批准后方可继续；不能自行把构造成功当作不泄漏，也不能将测试路径误称现行生产发送。

### r2 部分实施与只读/诊断结果

候选仍为 `main` 工作树，基线 HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，有任务外未提交改动。此轮尚未完成的任务内文件为：

- `src-tauri/src/domain/{local_configuration.rs,point_naming.rs}`、`src-tauri/src/services/{local_configuration.rs,local_point_naming.rs}`、`src-tauri/src/infrastructure/local_store/configuration.rs`：初步配置映射和命名候选，尚待完整验证。
- `src-tauri/src/infrastructure/local_store/delivery_tests.rs`：仅增加旧批次双 sentinel 泄漏的隔离复现测试；测试成功表示复现了冲突，不是功能验收通过。
- `src/services/localAcquisition.ts`、`src/console/composables/useLocalAcquisitionConsole.ts`、`src/app/plc/views/points/index.vue`、`src/app/plc/locales/{en-US,zh-CN}.json`：初步编辑/列表、列宽及未知提交结果处理，尚待验证。`src/styles/app.css` 等其余脏更改为既有改动，本轮未修改。
- 本 `tasks.md`；spec、checklist 及其他任务未修改。

环境：macOS 15.7.7、Rust/Cargo 1.89.0、Node 22.19.0、pnpm 11.11.0。以下命令均在 DAA 目录执行：

| 命令 / 检查 | 真实结果 |
| --- | --- |
| `CARGO_TARGET_DIR=/private/tmp/daa018-r2-dev-ewnCpRk3/old-target cargo build --manifest-path src-tauri/Cargo.toml --locked --offline --features local-validation --bin daa-local-validation` | 修改代码前 exit 0；9 条既有 dead-code 警告。 |
| 同一 target 的 `cargo build --manifest-path src-tauri/Cargo.toml --locked --offline --features rust-snap7-driver --bin aiis-data-acquisition-agent` | 修改代码前 exit 0。 |
| `CARGO_TARGET_DIR=/private/tmp/daa018-r2-dev-ewnCpRk3/old-target TMPDIR=/private/tmp/daa018-r2-dev-ewnCpRk3/daa-008-r2-a-fixtures cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib daa018_legacy_batch_context_contains_display_name_sentinels -- --nocapture --test-threads=1` | exit 0，1 test passed：确认真实合成样本的旧 v1 冻结 body 同时包含 `哨兵中文_DAA018` 和 `SENTINEL_EN_DAA018`。无网络发送。 |
| 上述测试先误加 `--exact` | exit 0 但 **0 tests**（完整模块路径未匹配），不作为测试通过；随后运行了上一行。 |
| `pnpm exec vue-tsc --noEmit` | 初步代码 exit 0；不证明原生 UI 或业务行为。 |
| `git diff --check`（上述已跟踪实现文件） | exit 0。 |

任务独立临时根 `/private/tmp/daa018-r2-dev-ewnCpRk3` 包含隔离 Cargo target、测试用合成 runtime3 profile 和修改前旧二进制；保留以便后续复现及兼容对照，任务结束且无需验证后由协调者按资源规则回收。旧原生二进制 SHA-256 `40e650f096b93a7f70b294540c09ebbc90cc80125f3442e351eae017c0ee845a`；旧 validation 二进制 `16e7fabea7ac2d37ecb19408714975d29dc79323bec75dae280d4f4a09f01d21`。旧二进制实际遇新配置、新版读旧 profile、完整 Rust/Node 回归、产物构建、采样/v2、原生 UI 和旧冻结/ACK 保全均 **not_run**；没有读取真实 profile、连接设备或发送网络请求。当前不是 DEV self-check 通过、`developer_handoff`、QA verdict 或 Human Owner 最终验收。

## r1 阻塞历史（保留）

## 批准与候选工作树

- 已核对 `spec.md` 为 `owner_approved`、`Revision: r1`；批准后 SHA-256 为 `107cd65850290950387958b539b8eddb685afd01650e7cc077acde268ededcb5`。
- 唯一交付工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；核对时 `main` HEAD 为 `21cd789277695bbafaa55c24e39261fc7247f9b0`。工作树已有大量任务外未提交修改，保留原状。
- Development 尚未改动实现；本轮仅创建本 `tasks.md`。没有创建测试 profile、构建目录或其他任务临时资源。

## 阻塞：现有点位编辑与批准的文件范围

点位编辑的实际链路为 `src/app/plc/views/points/index.vue::applyLocalPoint` → `src/console/composables/useLocalAcquisitionConsole.ts::stagePointEdit/confirmNames` → `daa_preview_point_names` / `daa_confirm_point_names` → `src-tauri/src/services/local_point_naming.rs::candidate`。预览缓存候选；确认时复核 token、输入摘要、ETag、有效期及重新构造的候选，再一次调用 `save_candidate` 保存。

`src-tauri/src/domain/point_naming.rs` 的 `PointPatch` 和 `NameRequest` 拒绝未知字段，也没有接收双语显示名的字段；`services/local_point_naming.rs::candidate` 因此无法把它们纳入同一候选。两文件均不在 r1 实施 allowlist。另一入口 `daa_save_draft` 的 `Save` 也拒绝额外参数，且 `services/local_configuration.rs::protect_derived` 原样阻止技术名和部分地址改动绕过命名预览。若用户同时编辑显示名和这些原有字段，隐式拆为两次保存可能在并发或容量失败时留下部分提交；绕过预览、保护或借用 ETag/其他配置字段传递确认信息均不符合原流程及本规格的安全边界。

拟请 PM 评估的最小新增实施文件为：

1. `src-tauri/src/domain/point_naming.rs`：在单点编辑输入中明确承载两语言值，绑定原输入摘要。
2. `src-tauri/src/services/local_point_naming.rs`：将显示名纳入原预览候选及确认复核，沿原单次 CAS 提交。

现有 r1 已允许的 `point_naming_tests.rs` 可承载针对性的原子性与并发验证；最终具体范围以 PM 新 Revision 和 Human Owner 的精确批准为准。本记录不是对新增文件的授权。源码复核还发现现有 DB/UDT 重导对缺失叶子返回 `leaf_removal_blocked`，同路径沿用原点 ID；PLC 删除位于 r1 已允许的 composable。此静态结论不是删除与重导验收结果。

## 已执行检查与限制

| 命令 / 检查 | 结果 |
| --- | --- |
| `shasum -a 256 automation-world/data-acquisition-agent/plans/DAA-018-bilingual-point-display-names/spec.md` | exit 0；结果与上述批准后 SHA 一致。 |
| `git status --short`、`git rev-parse HEAD`、`git branch --show-current` | exit 0；确认上述工作树、HEAD 与既有并行改动。 |
| `rg` 和 `sed` / `cat` 只读检查配置、命名预览、保存与来源复导调用链 | 静态确认上述阻塞；不构成运行测试。 |
| `git diff --no-index --check /dev/null automation-world/data-acquisition-agent/plans/DAA-018-bilingual-point-display-names/tasks.md` | exit 1（新文件与 `/dev/null` 不同），无空白错误输出。 |

Rust/Node 测试、类型检查、构建、采集与上报构造、旧二进制兼容及原生 UI 均 **not_run**；没有发起网络发送、设备操作、数据库迁移或读取用户真实 profile。不存在 DEV self-check 通过、`developer_handoff`、独立 QA 或 Human Owner 最终验收。

下一 gate：协调者交 PM 形成可审阅的新 Revision；Human Owner 精确批准后，Development 依据获批范围继续。原有 r1 事实保留，不把该阻塞当作完成或自动扩大范围。
