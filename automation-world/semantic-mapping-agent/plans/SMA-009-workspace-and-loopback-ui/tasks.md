Task ID: SMA-009
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: fresh-context Verification 核对以下交付及 SMA-008 r3 旧候选关系

# SMA-009 r1 P1 开发交付

按 [批准规格](spec.md) 实施首批。批准规格 SHA-256 为 `c67ed0503dcdbcd2e709e9093d9d232d190496f012d97c930f7f0fc0313b90b9`。开发范围为事实表、手工回环、预览和回读。真实 dev 推送由 Human Owner 操作。

## 实施

- 「源事实」下新增独立「手工回环」。事实表保留已有只读查询、导出、采集最新值，并可跳转手工回环。两个工作区各持有查询状态，事实表的选择不预填回环草稿。
- 手工回环依次呈现来源、历史样本、目标配置及预览。历史区说明缺失的查询前提，从结果行「使用此样本」读取该次采集详情。保持有效草稿、筛选与样本，输入变化使旧预览失效，迟到的历史响应不能覆盖已改变的筛选。配置保存使用已有 revision，失败保留草稿。
- 预览显示源与目标身份、序号、采集时间、样本和实际请求，仅显式动作调用已有单次推送。回读共享当前对话框焦点区，区分未查到和读取错误。未知结果可先回读、稍后核对或显式重试同一预览。退回编辑前可显式放弃重试，页面保留未知请求的目标、样本标识及采集时间供会话内核对。
- 沿用现有后端采集合同、Rust IPC 校验、请求字节与收据处理。未修改 BE、Rust 或 CU。既有 SQLite 和备份格式由已有命令处理。本地新增的是会话内的 UI 状态。索引文件仅更新 SMA 对应条目，工作树中的 Quality 追加段属于其他任务。

## Development 自检

- `pnpm check`、`pnpm test`（20/20）和 `pnpm build --outDir /private/tmp/sma009-dev.DcTiCZ/standalone-dist` 退出码 0。构建存在依赖包 PURE 注释定位与大 chunk 提示。
- `cargo fmt --manifest-path src-tauri/Cargo.toml --check` 退出码 0；使用专属空环境与临时 profile 执行 `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline -- --test-threads=1`，43 通过，1 项真实 dev opt-in 测试按默认忽略。既有 Rust 采集夹具覆盖同一预览的相同身份和字节、结果不明、重复回执与回读。该测试绑定本机临时端口。
- 浏览器自检执行 `pnpm exec vite --host 127.0.0.1 --port 15208 --strictPort`，专用 Playwright Chromium 会话加载 [采集浏览器夹具](../../tests/acquisition-loopback.browser.cjs)（`run-code --filename=<绝对路径>`），退出码 0。覆盖事实表与回环分离、列宽拖拽存储和重置、全选及单点多点、`0`、`false`、坏质量与原因、缺点位、网络失败和空来源；历史缺起止、反向时间、迟到响应、超时、服务失败、无结果、分页和从行选样；返回保留选择和草稿、同目标拒绝、保存冲突、取消和修改后重新预览；显式发送、未知、回读未找到、同一预览重试后 duplicate 和目标样本回读。1280×800 中文浅色与 1024×720 英文深色，覆盖 Escape、Enter、弹窗焦点、紧凑可视区及长 JSON 独立滚动。此层由内存 IPC 模拟驱动，真实 HTTP 和请求字节由上一层的 Rust 测试独立覆盖。
- 原生开发窗口通过 `pnpm tauri build --debug --bundles app --no-sign --ci --config /private/tmp/sma009-dev.DcTiCZ/overlay.json` 构建，退出码 0。使用独立 app ID `com.aiis.aw.sma009.development`、`incognito: true`、`SMA_ENV_FILE` 指向任务空环境、`SMA_PROFILE_DIR` 指向任务 profile、`SMA_HTTP_ENABLED=true`、空 `SMA_BACKEND_BASE_URL`，运行复制到任务目录的 macOS app。实际打开临时 SQLite（revision 0）。协调者在实际 `tauri://localhost` 窗口点击两个导航，看到事实表独立的采集只读区及原有查询导出、手工回环四步及缺失前提提示。该原生检查没有保存连接、执行网络请求或发送 POST；完整流程和尺寸来自浏览器夹具。开发者第一次 CUA 原生附着返回 `unknown or expired node_repl continuation`，入口由协调者实际核验。
- 合成 HTTP 服务从先前临时测试工具复制到本任务目录，端口 18091 独立使用。服务自检 `python3 /private/tmp/sma009-dev.DcTiCZ/server.py check` 在另一个随机端口校验 GET、POST、重复、409 和回读，退出码 0；这是服务本身的检查。
- `node --check tests/acquisition-loopback.browser.cjs`、任务路径 `git diff --check` 与本文件相对链接检查退出码 0。浏览器自检首轮在两个挂载工作区中匹配到隐藏内容，之后仅在可见工作区绑定断言；再跑时弹窗动画未完，修改为待原生焦点事件后取真实尺寸。最终重跑通过。
- 沙箱限制初次本机监听，使用获准执行启动私有 Vite、夹具以及需要临时端口的 Rust 测试。无真实 dev GET/POST、默认 profile 或现有库写入。未验证真实客户目标、真实 dev 回执、设备或生产运行。

## developer_handoff

交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基准 Git HEAD `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`，实现为以下未提交文件的当前字节。各路径相对于 SMA 目录。整个代码索引文件哈希带工作树中其他任务已有段，本任务仅修改其 SMA 一行。以下清单含末尾换行的 SHA-256 为 `d7e340d63ad35bebea9cf88a529594d5c29ff8bca12674ca62dd4901c4530fcb`。

```text
a4cc1600833ff90e065ec9b0d927fc78deac299f503a44c2a700739db951ef8b  ../../CODE_INDEX.md
8bf60af03f62754fc1cd7e099213a0e7ff9118529a22be1e556df2307d6d5750  README.md
e79d8062e8f57b2f9e20b1c0ab26439db7cda37cadcca2b1fd4c46edaf2b4fe2  README.zh-CN.md
cf63272b3f5dead18620fb4fd7a92853cbbb46ba723afc37ce277ffe95221feb  src/App.vue
d0276fd05a84e962f2a10532206d50bcb5c64c9dc0e88a6ade17b8cf147be4ea  src/app/twin-facts/components/AcquisitionLoopbackPanel.vue
fb5ac95aa348e92312972730d78ec87ee09ed0558711ef312ceec2d9bf598713  src/app/twin-facts/components/FactsTablePanel.vue
86056d6480f80f8c5a96508d5c000f25d224bc5e54b8cebc4ff9b04e708a7370  src/app/twin-facts/components/TwinJsonContractPanel.vue
79bd17186da35484d2ebadcb75b75e466c8cd05143922139dd84c8ee26cfe3b8  src/app/twin-facts/locales/en-US.json
534ecd685ab8ffcb2022936bd5f3fa8c5f8386785ac8e9a9a70ed7f953a50770  src/app/twin-facts/locales/zh-CN.json
207df322206d79a83b40f6ce26ccfbd7128f4dba8b21d6c4d5972ee6a6923c53  src/app/twin-facts/store/acquisitionLoopback.ts
841afd11c773a652194ff5eb9cc1e0a4a701ee0857f92ea322e01c76af3d853d  src/app/twin-facts/views/TwinFactsModuleView.vue
30dbc70f922502a212cddf67c9131e8756d34362eea424a68eca6ee48b128617  src/locales/common/en-US.json
0b9482648c87dbc1d896f221f7cdd229fc62ae170c0ba908718851748160632a  src/locales/common/zh-CN.json
75252ac29e07a6613446f037d753abcc9227f3c0f3d6fb58780712a136d89886  tests/acquisition-loopback.browser.cjs
```

对照 [SMA-008 r3 复验](../SMA-008-acquisition-data-get/checklist.md) 的等价面，本次修改前端入口和状态编排，Rust 合同、预览、精确请求字节、回执判定和 SQLite 写入入口仍为原实现。SMA-008 r3 rework-1 的 AC04 真实 dev 页面推送及目标历史回读仍待 Human Owner 和 Verification，本次合成结果不能替代。SMA-009 r1 由独立 Verification 基于上述候选复核。

任务临时目录 `/private/tmp/sma009-dev.DcTiCZ` 含命令日志、合成服务、专属构建及空 profile，专属运行资源停止后保留到 Verification 建立复验证据，随后回收。生成的命名 bundle `src-tauri/target/debug/bundle/macos/SMA009 Development Check.app` 同步回收，保留共享 Cargo 缓存。QA 用自己的 overlay、端口与 profile。

## SMA-009 r1 rework-1 开发交付 · 2026-11-24

[QA1](checklist.md) 将 AC08 返回 Development，因为事实表和手工回环最新值表共用 `acquisition.latest`，使拖拽和恢复默认列宽跨页影响。本轮只改两处。事实表沿用原 `acquisition.latest` 键，已有用户偏好直接恢复。手工回环最新值使用独立稳定键 `acquisition.loopback.latest`，未改 CU 公共实现、SQLite、API 或 Rust。

- 新浏览器用例在修改前复现 `Loopback inherited Facts column width`，退出码 1。修改后退出 0，事实表预置旧键值 210 并恢复，两个工作区分别拖出不同的列宽。重载页面并切换导航后，两张表分别恢复实测宽度。逐个重置时只删除当前工作区的存储键。后续历史、目标、弹窗及合成回环覆盖保留。
- 专用 Vite 15209 与 Playwright Chromium 会话执行 `run-code --filename=<fixture>`。测试副本相对于交付文件仅把浏览器访问端口 15208 改成 15209；使用内存 IPC，未接入真实 dev。 `pnpm check`、`node --check tests/acquisition-loopback.browser.cjs`、本次范围 `git diff --check` 及交接相对链接检查退出码 0。上一候选完整构建、Rust 夹具及原生验证记录保留，rework-1 本轮未重新构建原生 app。
- 交回独立 Verification。SMA-008 r3 AC04 实际 dev 推送和目标历史复核仍由 Human Owner 发起。临时浏览器会话和开发服务在自检后停止，`/private/tmp/sma009-dev.DcTiCZ/rework-{before,after,check}.log` 随前次证据保留至 Verification 建立复验证据后一起回收。

本轮基准 Git HEAD 与工作树同上。复核使用下表替代初次清单作为最新候选，保留上面的初次交接用于 QA1 追溯。最新清单含末尾换行的 SHA-256 为 `e303073134c271c8dfce829bf2506815b36a513e9d2b545d8226d8b42b14268c`。

```text
a4cc1600833ff90e065ec9b0d927fc78deac299f503a44c2a700739db951ef8b  ../../CODE_INDEX.md
8bf60af03f62754fc1cd7e099213a0e7ff9118529a22be1e556df2307d6d5750  README.md
e79d8062e8f57b2f9e20b1c0ab26439db7cda37cadcca2b1fd4c46edaf2b4fe2  README.zh-CN.md
cf63272b3f5dead18620fb4fd7a92853cbbb46ba723afc37ce277ffe95221feb  src/App.vue
eca7fec8dc701dc47d07c61f5128ae45c51b24149c02d7307c7e2cf414941498  src/app/twin-facts/components/AcquisitionLoopbackPanel.vue
fb5ac95aa348e92312972730d78ec87ee09ed0558711ef312ceec2d9bf598713  src/app/twin-facts/components/FactsTablePanel.vue
86056d6480f80f8c5a96508d5c000f25d224bc5e54b8cebc4ff9b04e708a7370  src/app/twin-facts/components/TwinJsonContractPanel.vue
79bd17186da35484d2ebadcb75b75e466c8cd05143922139dd84c8ee26cfe3b8  src/app/twin-facts/locales/en-US.json
534ecd685ab8ffcb2022936bd5f3fa8c5f8386785ac8e9a9a70ed7f953a50770  src/app/twin-facts/locales/zh-CN.json
207df322206d79a83b40f6ce26ccfbd7128f4dba8b21d6c4d5972ee6a6923c53  src/app/twin-facts/store/acquisitionLoopback.ts
841afd11c773a652194ff5eb9cc1e0a4a701ee0857f92ea322e01c76af3d853d  src/app/twin-facts/views/TwinFactsModuleView.vue
30dbc70f922502a212cddf67c9131e8756d34362eea424a68eca6ee48b128617  src/locales/common/en-US.json
0b9482648c87dbc1d896f221f7cdd229fc62ae170c0ba908718851748160632a  src/locales/common/zh-CN.json
545e818606d97178957ff4b0ea7fa801c596b66437314e925cc9dde0fd52e22a  tests/acquisition-loopback.browser.cjs
```
