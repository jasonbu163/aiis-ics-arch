Task ID: SMA-009
Revision: r1
Status: qa_passed
Owner Role: Verification
Handoff: Human Owner 对 r1 P1 rework-1 作最终验收

# QA1 · P1 · 2026-11-24

交付工作树 HEAD 为 `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`。从 [Development 交接](tasks.md) 提取 14 行清单，逐项读取文件重算 SHA-256，14/14 匹配，清单摘要为 `d7e340d63ad35bebea9cf88a529594d5c29ff8bca12674ca62dd4901c4530fcb`。本轮依据[批准规格](spec.md) P1 和根 AGENTS §8 检查。

| 验收项 | 检查与结果 |
| --- | --- |
| AC01 | 八个导航目标与页面标题映射存在。浏览器及原生窗口检查事实表和回环分别显示；事实表已有查询和导出仍连接原处理函数。 |
| AC02 | 浏览器覆盖来源读取失败、空来源、单点、多点、全部、0、false、坏质量、缺点，GET 阶段发送数为零。HTTP 关闭与缺材料提示另核对分支，原生空配置观察到连接与材料提示。 |
| AC03 | 浏览器检查缺起止、反向范围、空、失败、超时、延迟历史、分页及从行选择详情；源条件另在来源步骤检查。 |
| AC04 | 浏览器检查返回保留时间、样本与目标草稿，保存冲突及输入保留；取消和改序号后重新预览。源码核对连接、配置、点位、详情和序号的失效路径与异步返回时的 epoch 检查。 |
| AC05 | 浏览器检查 DB 21 → 61421 预览、同源目标拒绝和显式发送。Rust 合成 HTTP 检查请求、成功、回执不匹配、冲突与回读；序号前后端边界一致。 |
| AC06 | Chromium 模拟未知、首次未查到、显式重试、duplicate 和目标点；发送身份均为 preview-8。真实 HTTP 字节与提交后丢回执由本地 Rust 夹具检查。 |
| AC07 | 对照旧候选 IPC、Rust、SQLite 与备份入口，复跑 Rust 配置和采集套件。步骤及预览使用内存状态，保存需显式调用。 |
| AC08 | **失败**。回环最新值表将点位标识列从 140 拖至 186，进入事实表点击该页最新值表的「恢复默认列宽」，回环偏好键由含 pointId=186 变为 null。两页分别挂载组件，AcquisitionLoopbackPanel.vue 第 242 行向两者传入同一个 acquisition.latest 表标识，重开时无法恢复该回环偏好。请按页面隔离并验证双向拖拽、重开与重置。其余已跑的夹具包括中文浅色 1280×800、英文深色 1024×720、弹窗边界、键盘、长 JSON、读回。没有将这两个组合外推为完整交叉矩阵。 |
| AC09 | 候选和下列命令已核对。SMA-008 的真实 dev AC04 保留待办。 |

## 执行记录

macOS 15.7.7，pnpm 11.11.0，rustc 1.89.0。SMA 目录运行 `pnpm check`、`pnpm test`（20/20）、`pnpm build --outDir <qa>/dist`、`cargo fmt --manifest-path src-tauri/Cargo.toml --check`，均退出 0。`cargo test --manifest-path src-tauri/Cargo.toml --locked --offline -- --test-threads=1` 首次在原生并行构建时因 rustdoc 找不到共享 target 中的 rusqlite rlib 退出 101。原生构建结束后串行重跑完整命令退出 0，43 项通过、1 项 dev opt-in 忽略、0 个 doctest。

专用 Vite 监听 127.0.0.1:15209。Playwright 启动独立 Chromium 上下文，对交付 browser.cjs 仅在内存替换 Vite 端口后执行，退出 0。另在专属夹具副本中复用截至拖宽的相同步骤，然后切事实表、重置、读取回环键，实测结果为 `{loopbackWidth:186, afterResetOnFacts:null}`。模拟 IPC 及 Rust 的随机本地 HTTP 端口独立；未使用用户 18081 或 dev 写入。相对文件链接、`node --check tests/acquisition-loopback.browser.cjs` 与 `git diff --check` 通过。

独立 `pnpm tauri build --debug --bundles app --no-sign --ci --config <qa>/overlay.json` 退出 0。专用标识 com.aiis.aw.sma009.verification、incognito 窗口、空环境文件、专属 SMA_PROFILE_DIR 启动实际 app。QA 的 CUA 附着报 unknown or expired continuation；协调者实际附着本次 QA bundle，见证在 tauri://localhost 点击事实表与手工回环、独立活动导航、已有查询下载、四步、缺连接及材料提示。该窗口仅操作导航。原生和 Vite 已停止。

## SMA-008 与交接

重新从仓库根逐项计算 [SMA-008 QA2](../SMA-008-acquisition-data-get/checklist.md) 的 31 项。20 项相同，包括清单内所有 Rust 文件与锁文件、前端 acquisition/localConfiguration API、AcquisitionPointsTable。11 项不同，包括 CODE_INDEX、两份 README、AcquisitionLoopbackPanel、TwinJsonContractPanel、acquisitionLoopback store、两份模块和两份 common locale、浏览器夹具。新增工作区涉及此旧清单外的 App、FactsTablePanel 和 TwinFactsModuleView。SMA-008 r3 rework-1 仍为 qa_blocked，AC04 待 Human Owner 显式 dev POST 并核对回执和目标历史后交 Verification。本轮缺陷返回 Development；最终接受由 Human Owner 决定。

## QA2 · r1 P1 rework-1 · 2026-11-24 · qa_passed

独立 Verification 在同一交付工作树、同一 HEAD 逐个重算 14 个文件，全部匹配 [rework-1 交接](tasks.md)，清单 SHA-256 为 `e303073134c271c8dfce829bf2506815b36a513e9d2b545d8226d8b42b14268c`。对照 QA1 清单，变更仅涉及 AcquisitionLoopbackPanel.vue 和浏览器夹具。在内存中将最新值表的动态表标识还原为原单行静态属性，完整 Vue 文件重新得到 QA1 哈希 `d0276fd05a84e962f2a10532206d50bcb5c64c9dc0e88a6ade17b8cf147be4ea`。

**AC08 通过，QA1 缺陷关闭。** 独立运行 `pnpm exec vite --host 127.0.0.1 --port 15218 --strictPort`，使用 Playwright 驱动全新 Chrome 上下文。交付夹具仅在内存替换 Vite 端口，完整运行退出 0。事实表从旧键恢复 210px，拖宽后切回环，回环拥有独立初值。拖宽回环后事实表偏好保持。页面重载后实测两页表头分别恢复各自宽度；先在事实表重置，再设置事实表新宽度并在回环重置，两个方向都只清除本表键。完整夹具同时复验 1280×800 中文浅色与 1024×720 英文深色、弹窗、焦点及长内容滚动。QA1 的真实 Tauri 窗口证据用于入口与导航，两个入口、壳和命令均不受本轮唯一生产源码差异影响。QA2 在新候选重建前端并操作实际渲染表格，未另开原生窗口。

**AC01–AC07、AC09 通过。** 完整夹具重新覆盖两页切换、空与异常来源、点位过滤、历史时间与分页、迟到响应、草稿与冲突、预览、未知结果、回读和同身份重试。HTTP 字节、回执及 SQLite 兼容性沿用 QA1 同一 Rust 实现的 43 项通过、1 项 opt-in 忽略证据。SMA-008 旧清单关系同 QA1；其 AC04 继续等待 Human Owner 实际 dev 推送与目标历史核对。

本轮在 macOS 的 SMA 模块运行 `pnpm check`、`pnpm test`（20/20）、`pnpm build --outDir /private/tmp/sma009-qa2-final-dist`、`node --check tests/acquisition-loopback.browser.cjs`、`cargo fmt --manifest-path src-tauri/Cargo.toml --check` 和 `git diff --check`，均退出 0。生产构建沿用依赖 PURE 注释及 chunk 大小提示。QA2 浏览器与服务已关闭，临时 dist 已回收。测试使用内存 IPC，用户 18081 服务、真实 dev 和用户 profile 均未使用。交 Human Owner 最终验收 r1 P1。
