Task ID: SMA-008
Revision: r3
Owner Role: Development
Allowed Writers: Development
Status: developer_handoff
Handoff: fresh-context Verification 复核下列精确候选及验收边界

# SMA-008 r3 开发交接

## 实施

- 保留原本地配置、历史测试、常规运行门禁和其他页面。在「事实表」新增「采集 API 手工回环」。现有 options/latest 用于选点，按范围搜索 history，再以选定历史详情构造一份测试 POST。latest 中混合样本不会用于 POST。
- 在旧 v1 文档追加可选 `acquisitionLoopback` 配置，不创建新表，不动业务 schema 或旧 profile。复用 Rust CAS、配置备份和恢复，修正已保存配置展示。选点、目标和映射保存，临时点值、请求、回执、采样序号及重试身份存于当前会话。真实值先在 Rust 保留 JSON 数字精度，再将原值文本传给 UI。
- 映射可改目标点位标识、点名，可填写采集组和配置版本常量，所选原始点仍保留类型、值、质量及采集时间。源与目标的 PLC/DB 组合必须不同，用户输入序号以字符串校验、原样发送。预览期间 GET 不写入，显式确认后才发送普通 samples POST；核对响应、未知结果同会话原字节重试，已知拒绝不自动重发。回读时间以所选点的最大采集时间为基础，避免未选的较晚源点改变查询范围。
- 清退此前未交接 r2 草稿中的消费者运行、Bearer、进程恢复和冻结版本表代码。Cargo.lock 只增加现有 uuid crate 的根依赖引用，版本不变。使用既有 serde_json 的 arbitrary_precision feature 和既有 uuid 的 v4 feature，不引入新 crate 版本。
- 使用已存在的 CU 卡片、动作和列宽工具及 Element Plus 弹窗。同步双语文案和使用步骤。保留共享工作树并行的既有 CU/SMA 改动，未重置任何其他任务文件。

## 自检

| 证据 | 结果 |
| --- | --- |
| `pnpm check`、`pnpm test`、`pnpm build` | 三项退出 0，前端 20 项通过。构建有依赖的 Rollup PURE 注解及包体积提示。 |
| `cargo check --manifest-path src-tauri/Cargo.toml --offline`、`cargo fmt --manifest-path src-tauri/Cargo.toml --check` | 退出 0。 |
| 临时环境下 `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline` | 42 通过，1 项只读 dev 用例默认忽略。全套使用本任务环境设置，不读取用户 profile。 |
| `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --test acquisition_loopback_tests` | 离线类型测试与原生服务本机 HTTP 夹具 2 通过。样本提交后模拟丢回执、同字节重发、唯一目标回读、409、HTTP gate、预览失效、原始数据不进入 SQLite/备份/日志；夹具的服务仅绑定随机回环端口。 |
| `SMA_HTTP_ENABLED=true cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --test acquisition_loopback_tests dev_get_only -- --exact --ignored` | 1 通过。在同一原生 HTTP adapter 上只读调用现有 dev 127.0.0.1:8000，读取 options、PLC-BE012-DEV-441247C3 下 DB 21 的单点/多点/全量 latest、历史列表和 ID 1 详情。操作者为 Development。 |
| 既有 Playwright CLI 运行 `tests/acquisition-loopback.browser.cjs` | Chrome 夹具通过 1280×800 中文浅色、1024×720 英文暗色、两个弹窗、Escape/Enter、列宽拖拽和恢复、未知/重试/回读。该检查使用本机 Vite 和模拟 IPC。 |
| `git diff --check`、任务文档相对链接、运行时代码检索 | 差异和相对文件链接正常。新功能中无 acquisition-consumers、Bearer、运行任务或冻结表。 |

隔离 native fixture 可从 SMA 目录运行上述 Rust 测试。若需完全隔离环境，令环境变量 `SMA_ENV_FILE` 指向测试自有绝对普通文件，文件内容 `SMA_HTTP_ENABLED=false`。仅开只读 dev case 时用同一个文件配合进程变量 `SMA_HTTP_ENABLED=true`。本机监听及 dev 回环网络需要相应 sandbox 权限。窗体夹具先从 SMA 目录运行 `pnpm exec vite --host 127.0.0.1 --port 15208 --strictPort`，再在自有临时目录运行 `playwright-cli -s=<task session> open about:blank --browser chrome` 与 `playwright-cli -s=<task session> run-code --filename <absolute SMA path>/tests/acquisition-loopback.browser.cjs`，结尾关闭该独立会话和 Vite。

## 交接边界

本候选在原生服务的回环夹具测试了 POST、同字节重试和回读，现有 dev 只做 GET，未调用真实 dev POST、修改后台、使用用户正式 SMA profile 或执行数据库迁移。真正的 SMA dev POST 由 Human Owner 按需显式点击，在已登记测试 PLC/DB 上核准未使用序号；实际步骤见 [中文 README](../../README.zh-CN.md)。示例目标 DB 61421，实例与代次沿用此前已登记的 external 测试来源。这里的核对不替代用户操作，也不涵盖持续投递及重启恢复。

开发自有 Vite、临时 Chromium 会话和临时夹具文件结束后回收。共享工作树已有的 Rust target 和前端 dist 保留用于构建、正常启动与接续验证。

## Developer handoff · 精确工作树

基准 HEAD `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。本次候选以路径排序的 31 个交付文件摘要固定，清单 SHA-256 为 `6900d4ef456c96e4b5014193e1d8c0bda89bdfb910a04b52b936df5d5747f22b`。工作树中若有并行修改，交接文件摘要覆盖当时实测的完整文件。下列依赖观察值不属于 Development 写入范围。

```text
ee876328b0ca06121b7717d81d5305d2ac9817efd93d33e04134584604dfc988  CODE_INDEX.md
4abf1f67601fe9323a893533dc5a93e61bd9d3a108585ac68314db367080b906  automation-world/semantic-mapping-agent/README.md
bbb17a41f9c981a84286abe518f1a09c45f872b81f64e05c2368959a15d43588  automation-world/semantic-mapping-agent/README.zh-CN.md
8853d90b1af1809f1458a4e58a9c612e6c1c6f0db60c380a3cccb381da227993  automation-world/semantic-mapping-agent/src-tauri/Cargo.lock
83ec00ed6a986e796a2fbef046d96b4611f6000f049a8ad6723235a03de76e61  automation-world/semantic-mapping-agent/src-tauri/Cargo.toml
55410c873898f6cabc183c97bbef421bc27eaf119ee3a3bbb14d7f5c4dc831d6  automation-world/semantic-mapping-agent/src-tauri/src/app.rs
bc19996f16a197f9960939465344047d027ef44d3298a2a480458d943160d2c0  automation-world/semantic-mapping-agent/src-tauri/src/commands/acquisition.rs
a8999ab970e2aa130a9c5517bc06d4679806e6d5dfc25a17616b6267a971fd68  automation-world/semantic-mapping-agent/src-tauri/src/commands/mod.rs
7bbec9c65b2e3cb5d6bb1cb7648df4beed664ae3905834c43f4978007803dfa6  automation-world/semantic-mapping-agent/src-tauri/src/contracts/acquisition.rs
3facdbbfcc2f3437e5394b0193bb5995f6d8270875cfc87e71e942e530103477  automation-world/semantic-mapping-agent/src-tauri/src/contracts/local_configuration.rs
8358b46c97bcb61f6254e895aea2c795a2378ae5ac33ba84c064267de48cf627  automation-world/semantic-mapping-agent/src-tauri/src/contracts/mod.rs
a3c0ef096caa5657f90724882905e2dafe21b51597794e4696fa8e39eebedf19  automation-world/semantic-mapping-agent/src-tauri/src/domain/acquisition.rs
3dd4c4168fe8a36ee67aa07c77d3ed5d2c17eeb39e0ccc2d459fc32547514356  automation-world/semantic-mapping-agent/src-tauri/src/domain/local_configuration/validation.rs
65d725ee2744bad53521281804c8391bd7807e434ec9f17ed744e5538e45d7db  automation-world/semantic-mapping-agent/src-tauri/src/domain/mod.rs
51f7496d076ae172bcbd709c4342a848d67ee0bfa11335220192a0644bf412d3  automation-world/semantic-mapping-agent/src-tauri/src/infrastructure/acquisition.rs
ebaf79fc9e78a08cbbf96499dd033b2c90c757c015ebd8b81ecf3751702bd9cd  automation-world/semantic-mapping-agent/src-tauri/src/infrastructure/mod.rs
57345f4fc490c2e363c645ef6006523b96a3f7b1b19351250bf360b6e90bc4f5  automation-world/semantic-mapping-agent/src-tauri/src/services/acquisition.rs
43b46a1a7d868329338757d81f3548cb2f449c1a7c40843d550c6011eafc9a06  automation-world/semantic-mapping-agent/src-tauri/src/services/local_configuration/mod.rs
19f510ff75e2e97b78628d5b1818fea58a40180a884ef9a6b7fe3e8a40ebd607  automation-world/semantic-mapping-agent/src-tauri/src/services/mod.rs
b916aba3e16f3a2650dcef2e642803d6054a7aae9096ab2feef13e2c50ea2ddb  automation-world/semantic-mapping-agent/src-tauri/tests/acquisition_loopback_tests.rs
ec23b88495bda26da3801dd3466393b56e0f7e0e49638a23970d77fdafa14650  automation-world/semantic-mapping-agent/src/app/twin-facts/api/acquisition.ts
73b4b221f167a13819f3d138947c12690dbea7d45be8e9ce6ca5fd39d9141a88  automation-world/semantic-mapping-agent/src/app/twin-facts/api/localConfiguration.ts
1c0eb9b59bab5ad5c352f565dc29f53ca6eca35c4e519fbf1d9ab44249d21d98  automation-world/semantic-mapping-agent/src/app/twin-facts/components/AcquisitionLoopbackPanel.vue
d8329360789e8adfecf48e71936ffee5f2cde5702c032403940945c1e2b47e8a  automation-world/semantic-mapping-agent/src/app/twin-facts/components/AcquisitionPointsTable.vue
b99cda1cee2c7f448b3589bdbad831f8ad489a856fc1625da6db9e54a15f5efa  automation-world/semantic-mapping-agent/src/app/twin-facts/components/TwinJsonContractPanel.vue
a16cd2f36f75423c167ac2ff189289c061f5994e61788566a71e347c2e814721  automation-world/semantic-mapping-agent/src/app/twin-facts/locales/en-US.json
a83f5b40d0ae6a3bc11076766fb1c58bd9e518ec68d7df4a1c991a4b91425ae6  automation-world/semantic-mapping-agent/src/app/twin-facts/locales/zh-CN.json
51b923a686a59c4858c2677d7750def421068bb7c1334cbdc8da388eede198b1  automation-world/semantic-mapping-agent/src/app/twin-facts/store/acquisitionLoopback.ts
04b8584878db3115ac02d6513f05ccaa855d56131aea80ad4031d6585049729d  automation-world/semantic-mapping-agent/src/locales/common/en-US.json
bb5270815fd6e00650f1f3c0700147dacc05cbc415b497024edd0e535087861c  automation-world/semantic-mapping-agent/src/locales/common/zh-CN.json
6be2e688aecff30e0e15b3f4fd0eb9257d61c1b303ecdd0366ad93b2f641f8a6  automation-world/semantic-mapping-agent/tests/acquisition-loopback.browser.cjs
```

只读依赖：

```text
dccc124737a4e24dfc907f80c49154d0fd9f8cb7dae101f2991e6762ac6463b0  automation-world/console-ui/src/ui/index.ts
36d26a60ee5b4aef4f4bc8319099647ce79b4278108b587eba0a2430a1796328  automation-world/console-ui/src/ui/useTableColumnWidths.ts
dbc462224ac16e8422c52b608506ce8f028457581c2c2738539e3e5f254e611a  automation-world/semantic-mapping-agent/src/App.vue
```

## Developer handoff · rework-1

处理首轮独立核对记录的两种 REAL 缺陷，SMA-008 规格仍为 r3。Rust 从原始 JSON 数字直接判断 binary32 的有限范围，避免 f64 再转 f32 在溢出边界产生双重舍入。HTTP、历史详情和 POST 使用同一 `serde_json::RawValue` 保留数值字面量。IPC 显示和回读通过精确的 `valueText`，负零不会被 `Value` 或 JavaScript 数字转换变成正零。POST 直接序列化含原始点值的有类型正文，同会话重试继续复用原字节。Cargo.toml 启用了现有 serde_json 的 raw_value feature，锁文件和依赖版本未变。

- 纯 Rust 用例覆盖正负溢出中点减一、精确中点、中点加一和负零，分别断言接纳和拒绝以及原始数值字面量。
- 原生 HTTP 夹具真实发送、解析和回读三个特殊 REAL，验证 latest、history/1、目标正文、相同字节重试和目标历史。首发已存后断开，重发时断言发送字节与预览一致且保留 `-0`，目标仍一条。SQLite、备份和日志界线回归继续覆盖。
- 临时环境下 `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline -- --test-threads=1` 共 43 通过、1 个 dev GET 默认忽略，退出 0。单独启用自有环境后执行 `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --test acquisition_loopback_tests dev_get_only -- --exact --ignored`，实际 dev 127.0.0.1:8000 只读用例 1 通过，未执行 dev POST。
- `pnpm check`、`pnpm test`、`pnpm build`、`cargo fmt --manifest-path src-tauri/Cargo.toml --check`、`git diff --check` 退出 0，前端回归 20 通过，产物与上轮前端同摘要名。此次只改 Rust 及其测试，原浏览器证据保留。开发自有测试环境已清理。

以下是第 2 次独立复验使用的 31 行完整清单，基准 HEAD 沿用 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。与首轮候选相比仅 6 个文件发生变化，清单 SHA-256 为 `b00447cd99f229bb6826f8393e158e7ecc6200a8f7c7564704588fa56744be17`。上方首轮清单、只读依赖和验证记录用于审计。实际 dev POST 仍由 Human Owner 测试操作，不在开发执行记录中。

```text
ee876328b0ca06121b7717d81d5305d2ac9817efd93d33e04134584604dfc988  CODE_INDEX.md
4abf1f67601fe9323a893533dc5a93e61bd9d3a108585ac68314db367080b906  automation-world/semantic-mapping-agent/README.md
bbb17a41f9c981a84286abe518f1a09c45f872b81f64e05c2368959a15d43588  automation-world/semantic-mapping-agent/README.zh-CN.md
8853d90b1af1809f1458a4e58a9c612e6c1c6f0db60c380a3cccb381da227993  automation-world/semantic-mapping-agent/src-tauri/Cargo.lock
7d566240d5092bb50e21e276abe28799ce2baaa1d17e8e1066ac09f2219de8dd  automation-world/semantic-mapping-agent/src-tauri/Cargo.toml
55410c873898f6cabc183c97bbef421bc27eaf119ee3a3bbb14d7f5c4dc831d6  automation-world/semantic-mapping-agent/src-tauri/src/app.rs
bc19996f16a197f9960939465344047d027ef44d3298a2a480458d943160d2c0  automation-world/semantic-mapping-agent/src-tauri/src/commands/acquisition.rs
a8999ab970e2aa130a9c5517bc06d4679806e6d5dfc25a17616b6267a971fd68  automation-world/semantic-mapping-agent/src-tauri/src/commands/mod.rs
52a69945f83480b11d0a083118b1545ecf3a32219a3d967ba2990ede038ab485  automation-world/semantic-mapping-agent/src-tauri/src/contracts/acquisition.rs
3facdbbfcc2f3437e5394b0193bb5995f6d8270875cfc87e71e942e530103477  automation-world/semantic-mapping-agent/src-tauri/src/contracts/local_configuration.rs
8358b46c97bcb61f6254e895aea2c795a2378ae5ac33ba84c064267de48cf627  automation-world/semantic-mapping-agent/src-tauri/src/contracts/mod.rs
bac068e3f90848103a0a461cce5eb5dfe3ca770ce4881cd58803c9ae1f4054d5  automation-world/semantic-mapping-agent/src-tauri/src/domain/acquisition.rs
3dd4c4168fe8a36ee67aa07c77d3ed5d2c17eeb39e0ccc2d459fc32547514356  automation-world/semantic-mapping-agent/src-tauri/src/domain/local_configuration/validation.rs
65d725ee2744bad53521281804c8391bd7807e434ec9f17ed744e5538e45d7db  automation-world/semantic-mapping-agent/src-tauri/src/domain/mod.rs
f765f51ad860a681245c6e9552f07e9fa66bf6dd4e2e0c18631f3f75313e27c8  automation-world/semantic-mapping-agent/src-tauri/src/infrastructure/acquisition.rs
ebaf79fc9e78a08cbbf96499dd033b2c90c757c015ebd8b81ecf3751702bd9cd  automation-world/semantic-mapping-agent/src-tauri/src/infrastructure/mod.rs
ae58acffa83bc3311b2cc6dd3e18bf06f5a716c3399a13b6488f3844b2a59672  automation-world/semantic-mapping-agent/src-tauri/src/services/acquisition.rs
43b46a1a7d868329338757d81f3548cb2f449c1a7c40843d550c6011eafc9a06  automation-world/semantic-mapping-agent/src-tauri/src/services/local_configuration/mod.rs
19f510ff75e2e97b78628d5b1818fea58a40180a884ef9a6b7fe3e8a40ebd607  automation-world/semantic-mapping-agent/src-tauri/src/services/mod.rs
fb796bde4a1800ab90c89269390cef8d5fbc9227fb1725b330df9f0c561e098f  automation-world/semantic-mapping-agent/src-tauri/tests/acquisition_loopback_tests.rs
ec23b88495bda26da3801dd3466393b56e0f7e0e49638a23970d77fdafa14650  automation-world/semantic-mapping-agent/src/app/twin-facts/api/acquisition.ts
73b4b221f167a13819f3d138947c12690dbea7d45be8e9ce6ca5fd39d9141a88  automation-world/semantic-mapping-agent/src/app/twin-facts/api/localConfiguration.ts
1c0eb9b59bab5ad5c352f565dc29f53ca6eca35c4e519fbf1d9ab44249d21d98  automation-world/semantic-mapping-agent/src/app/twin-facts/components/AcquisitionLoopbackPanel.vue
d8329360789e8adfecf48e71936ffee5f2cde5702c032403940945c1e2b47e8a  automation-world/semantic-mapping-agent/src/app/twin-facts/components/AcquisitionPointsTable.vue
b99cda1cee2c7f448b3589bdbad831f8ad489a856fc1625da6db9e54a15f5efa  automation-world/semantic-mapping-agent/src/app/twin-facts/components/TwinJsonContractPanel.vue
a16cd2f36f75423c167ac2ff189289c061f5994e61788566a71e347c2e814721  automation-world/semantic-mapping-agent/src/app/twin-facts/locales/en-US.json
a83f5b40d0ae6a3bc11076766fb1c58bd9e518ec68d7df4a1c991a4b91425ae6  automation-world/semantic-mapping-agent/src/app/twin-facts/locales/zh-CN.json
51b923a686a59c4858c2677d7750def421068bb7c1334cbdc8da388eede198b1  automation-world/semantic-mapping-agent/src/app/twin-facts/store/acquisitionLoopback.ts
04b8584878db3115ac02d6513f05ccaa855d56131aea80ad4031d6585049729d  automation-world/semantic-mapping-agent/src/locales/common/en-US.json
bb5270815fd6e00650f1f3c0700147dacc05cbc415b497024edd0e535087861c  automation-world/semantic-mapping-agent/src/locales/common/zh-CN.json
6be2e688aecff30e0e15b3f4fd0eb9257d61c1b303ecdd0366ad93b2f641f8a6  automation-world/semantic-mapping-agent/tests/acquisition-loopback.browser.cjs
```
