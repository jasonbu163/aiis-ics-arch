Task ID: SMA-005
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Development -> fresh-context Verification
Workflow Mode: STD

# Development 记录

Human Owner 已批准的 [SMA-005 r1](spec.md) SHA-256 为 `730b6adc9fee5ee19f48f9428e4542d8565fef0d1e0404279e8ab366a6dbb8e5`。在交付工作树实施连接测试和保存分离，以及运行入口状态修正。

## 实施计划

1. 连接页区分草稿测试和显式保存，校验请求地址并处理失效响应。
2. 运行页和映射列表说明可用范围，保留预览、诊断与适用的暂停和停止。
3. 执行定向回归、项目检查和构建，并登记可复现的开发证据与候选身份。

## 默认 profile 意外写入

2026-11-16 14:26–14:27（Asia/Shanghai），开发自检误用 bundle ID 绑定窗口。CUA 因裸 Tauri dev 进程未注册为 app，另行启动了旧版已打包应用，PID 73944。该进程没有继承临时 profile。开发在其窗口输入合成地址 `saved.invalid:9000` 并保存，然后输入 `127.0.0.1:59564` 并点击旧版「测试 OpenAPI」。旧版测试先保存，故发生第二次提交。旧进程使用的 HTTP 准入关闭，本次测试未到达临时 HTTP 服务。该进程已退出。

受影响文件为 `~/Library/Application Support/com.aiis.aw.semanticmappingagent/configuration.sqlite3`。只读日志显示误启动时 revision 为 0，两次提交后为 2，最终连接是 `http://127.0.0.1:59564`。只读查询显示 catalog、materials、targetApis、mappingValueRules、mappings、sourceMetadata 当前计数均为 0。默认日志目录追加了启动、读取和提交记录。2026-11-14 的日志显示该数据库打开时为 revision 0，源码的新建数据库也从默认文档初始化 revision 0，但没有误操作前内容快照，不能将默认值推定为可恢复原值。未尝试恢复或覆盖默认 profile。以上窗口交互不作为隔离自检证据。

## 开发实现与自检

- 连接页面以点击时草稿发起 OpenAPI GET，独立显示测试地址、测试反馈和保存反馈。地址修改同步失效旧响应；显式保存继续使用已观察的 revision。材料目录沿用原有已保存地址调用入口和 fetch 行为。
- 运行页和映射列表显示配置与预览可用的提示。页面入口不提供启动、恢复、单次测试和自动启动设置；状态、日志、已保存配置预览及适用的暂停与停止保留。
- `pnpm --config.verify-deps-before-run=false --config.update-notifier=false check`，退出码 0。
- `pnpm --config.verify-deps-before-run=false --config.update-notifier=false test`，退出码 0，20/20。包含内存 IPC fixture 下的无写入、地址校验、测试先后响应、超时、禁用 HTTP 保存和冲突，以及材料预览原入口回归。该层证据不等同 SQLite 或真实网络。第一次完整测试的旧 literal-key 检查将 `labels.some` 误认作文案键，已将主机标签局部变量改名后重跑通过。
- `pnpm --config.verify-deps-before-run=false --config.update-notifier=false build --outDir /private/tmp/sma005-dev-build`，退出码 0；任务专用 Tauri 构建的 `pnpm run build --outDir /private/tmp/sma005-dev.jmJkKx/dist` 再次通过。Vite 给出依赖 PURE 注释及大于 500 kB 的 chunk 提示。
- `git diff --check` 对本任务触达源码与测试退出码 0；本文件相对链接检查退出码 0。`pnpm test` 同时核对中英文键一致及静态文案键解析。
- 原生开发自检使用 `pnpm tauri build --debug --bundles app --config /private/tmp/sma005-dev.jmJkKx/overlay.json` 生成的当前候选。临时 overlay 设置测试专用 bundle ID `com.aiis.aw.sma005.development`、测试标题、完整窗口配置及 `incognito: true`，并把前端产物指向临时目录。复制的测试 app 通过明确的 `SMA_PROFILE_DIR`、`SMA_ENV_FILE`、空 Backend 环境地址及独立本机 HTTP 服务启动。实际 PID、app 路径和其打开的临时 SQLite 经进程及 `lsof` 核对。
- 在该隔离窗口中，保存 A `saved.invalid:9000` 后输入 B `127.0.0.1:59564` 并测试。页面显示 B、OpenAPI 3.1.0 与未保存状态。受控服务记录一次 `GET /openapi.json`，SQLite 查询仍为 A、revision 1。映射运行页显示「当前仅支持配置和预览，映射投递未启用」及空闲计数。隔离窗口、服务随后退出。误写事件之后至隔离窗口结束，默认 SQLite SHA-256 保持 `e8b92c30e123cac80115a5cf24e970f2a1681124a0f3dbd504c206a0d32cdd84`。
- Human Owner 随后表示希望自己操作测试，测试仅进行 GET，POST 暂不进行。后续原生窗口的重开确认、尺寸、明暗、双语、键盘以及其他现场操作由 Human Owner 执行；本次开发没有对这些步骤宣称通过，也没有发送目标 POST。
- 原生拒绝代码仍在 `src-tauri/src/services/local_configuration/mod.rs`，本候选未修改 Rust；其直接 IPC 行为仍需由独立 Verification 按现有证据和允许范围核对。

## developer_handoff

交接 SMA-005 r1，交付工作树根为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基准 Git HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，交付为以下未提交文件的当前内容。各行 SHA-256 固定交接候选，路径相对 `automation-world/semantic-mapping-agent/`。

```text
34bc0e01ca77175d40e365e2e8473b09cd80ef166a0b64e198bd67b39d2ef3a7  src/app/connection/api/index.ts
5a55037f5bd6c41e9512c8f870d226fce3e03cbc3ee136edc70773eb56bfd732  src/app/connection/components/BackendConnectionPanel.vue
ee8bfe72766ddb3380d158aef82c38dffcad90a2ba3f0859634f0aac649a71e6  src/app/connection/locales/en-US.json
8f2facc9a1663352a582ecf03d519828a1a6f27c2b54deee26494d6e3856f326  src/app/connection/locales/zh-CN.json
b1de2895d8de5cba7cb4c3108b129174f5c78c1d3ecc301c162a1846732a7ed8  src/app/connection/views/ConnectionModuleView.vue
407604baca356d88258f87bcf313e3b288b80f7779623be22521d6b28a7e2627  src/app/twin-facts/components/ApiFirstMappingRuntimePanel.vue
ac7ba03e8e62c9e9046289bd3e1351181f95f59b0c29239f5d5ef94ad6cded00  src/app/twin-facts/components/MappingConfigurationsPanel.vue
fe837e309154c3e9a098dfadcf29178e90990934679ed992c052d037be1cd7b9  src/app/twin-facts/components/TwinJsonContractPanel.vue
e6f11ae26837c502dfb2a12f584b13a1a4884c9cd0e644cf1430dbf1689e0d04  src/app/twin-facts/locales/en-US.json
b9d478ede60d770a28dde2e051180f3afe3e3d720423009347a4dab1704a3713  src/app/twin-facts/locales/zh-CN.json
83920e71802456b0b680c6b487f16f49572b09f4c1f2afd7d157056556d91ac8  src/app/twin-facts/store/apiFirstMappingRuntime.ts
1bca53fbf7023bf394010d5848c5bccabfb113b1bbe1987746517dea73b56951  tests/local-configuration.test.mjs
```

`/private/tmp/sma005-dev.jmJkKx` 含此任务临时 overlay、构建、服务请求记录和隔离 profile，供交接核对；服务和 app 已停止，独立验证及 Human Owner 所需证据持久化后回收。生成的 `src-tauri/target/debug/bundle/macos/SMA-005 Development Check.app` 为本任务独有构建产物，同样在交接后回收。`/private/tmp/sma005-dev-build` 为首次构建产物，交接后回收。
