Task ID: ARCH-FE-005
Revision: r2
Workflow Mode: STD
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Development -> fresh-context Verification
Updated: 2026-11-11 Asia/Shanghai

# Development 实施与自检

## 精确候选和范围

- Human Owner 已批准 `ARCH-FE-005 r2`；当前 `spec.md` SHA-256 为 `442bffb872528ca6c4aed128a147fcf5521b513d05fad760511fd8d3616382ae`。本记录不修改规格和 Verification 的 checklist。
- 交付工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基准 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`，候选是该工作树当前未提交文件，不是新 commit。仓库在开工前已有多任务未提交工作；不得将全部工作树 diff 归属本任务。
- 本 Development 新增 `frontend-js/src/app/acquisition-data/` 中的 manifest、四 GET facade、范围 composable、实时页、历史页、详情组件和双语 locale；新增 `frontend-js/src/utils/tableColumnWidths.js` 及 `frontend-js/tests/module-registry/acquisition-data.test.mjs`；最小修改 `frontend-js/src/utils/date.js`、`frontend-js/src/utils/request.js`。本文件为 Development 的事实记录。
- 协调者负责并行任务共同触及的 `CODE_INDEX.md` 条目；既有 `frontend-js/tests/module-registry/registry.test.mjs` 和 `page-access.test.mjs` 的全量列表机械适配由并行 agent 负责，不作为本 Development 的独立源码修改。旧 System/Monitor、DAA、backend、合同、真实配置和角色 grant 未由本 Development 修改。
- 行为摘要：复用 Registry、登录及页面 grant；通过后端选项选择 PLC/DB，按代次失效处理迟到结果；历史按提交的上海半开区间、后端分页和字符串 ID 读取；按调用关闭共享全局错误提示但保留原认证和解包；三表按本机稳定字段保存和重置列宽。日期输入使用严格文本校验，避免浏览器本地夏令时改变上海墙上时间。

## DEV self-check

| 检查 | 实际命令或方法与结果 |
| --- | --- |
| 规格和差异 | `shasum -a 256 plans/ARCH-FE-005-acquisition-data-module/spec.md` 符合上述哈希；`git diff --check -- frontend-js` exit 0；Python 扫描新增文件行尾空白 exit 0；Python 检查 spec 相对文件链接无缺失（不检查锚点）。 |
| 模块独立测试 | `node --test frontend-js/tests/module-registry/acquisition-data.test.mjs` exit 0，4/4。覆盖注册顺序、单页 grant、禁用与残留 grant、双语标题、上海时间与两个进程时区、列宽隔离/最小值/过时偏好/重置。 |
| 隔离前端模块检查 | 从交付工作树复制前端至 `/private/tmp/arch-fe005-r2-dev-SxzMqn`，排除真实 `.env*`、`node_modules` 和 `dist`；使用公开合成 grant、mock=false，`node_modules` 只读消费正式树已有依赖的符号链接。`pnpm_config_verify_deps_before_run=false pnpm --dir /private/tmp/arch-fe005-r2-dev-SxzMqn check:modules` exit 0，10 组、25 条 routes。 |
| 隔离前端回归 | `pnpm_config_verify_deps_before_run=false pnpm --dir /private/tmp/arch-fe005-r2-dev-SxzMqn test:modules` exit 0，50/50。包含协调者安排的既有固定列表适配；这不是旧入口清退后的联合回归。 |
| 隔离构建 | `pnpm_config_verify_deps_before_run=false pnpm --dir /private/tmp/arch-fe005-r2-dev-SxzMqn build --outDir /private/tmp/arch-fe005-r2-dev-SxzMqn/build` exit 0，Vite 5.4.21；有 vendor chunk 大于 500 kB 的构建警告。Node v22.19.0、pnpm 11.11.0。第一次未设该 `pnpm_config` 的隔离构建触发 pnpm 的依赖状态检查，因网络失败及非交互环境退出 1；未安装或删除依赖。后续明确关闭该检查，使用工作树现有锁定依赖完成上述检查。 |
| 源码一致性 | Python SHA-256 对比本任务 12 个源码/测试文件及并行两个现有测试，正式树与隔离前端共 14 文件一致。构建和浏览器只使用隔离前端，最终改动已在正式工作树。 |
| 合成浏览器 | Chrome / Playwright CLI，`browser-check.js` 17 次合成 GET：未登录、无页面 grant、仅采集页 grant、空读范围、403/500/401、0/false/空串/缺测/坏质量、无效时间、查询失败无旧 API 回退、DB 切换迟到响应、逐点表实际拖拽及最小宽度、筛选/刷新/重开/重置、初始 24 小时、7 天上限、后端顺序、超 JS 安全整数 ID、完整详情及统一 404。`browser-extra.js` 8 次合成 GET：第二页及结果顺序、历史和详情表真实拖拽、翻页/重开保留、单表重置及详情 403 清除旧列表。以上是 DEV 自检，非独立 QA verdict。 |
| 时间边界 | 两个 Node 时区测试一致；合成 Chrome 的 `America/Los_Angeles` 对 `2026-03-08 02:30:00` 发出 `2026-03-08T02:30:00+08:00`，结束时间为 `03:30:00+08:00`。此前 Element Plus 日期控件把该值归一化为 `03:30:00`，已改为严格文本输入并复验。显示保留原始时间字符串在单元格 title，界面显示到秒。 |
| 窄屏与主题 | 合成 Chrome 390×844、手动折叠侧栏：两页及详情分别检查日/夜，实际切换中英文，时间输入宽 310px，实时表内容 980px/视口 332px 可横向滚动；详情弹窗在视口内。768×900 默认展开：主区宽 532px，页面标题 y=193，既有 header 底部 y=186，文档宽 768px。**390px 默认展开时全局侧栏占 236px、主区仅 154px，输入日期不能完整可见；需要手动折叠。这一既有壳层限制未解决，也不计为默认展开窄屏通过。** 未修改共享壳层，页面局部增加 ≤768px 标题间距及 ≤600px 标题换行。 |
| 现有 dev 只读 | 最终源码候选的隔离前端关闭 mock，用现有 admin 配置在进程内执行正常登录；未打印密码或令牌，短时 `0600` 浏览器状态文件载入后删除。浏览器 `options`、`latest`、`history`、`history/1` HTTP 均 200；`PLC-BE012-DEV-441247C3 / DB21` 的 latest 显示 `820.5`、`false`、`2026-11-10 21:56:44`，整秒半开区间 `[2026-11-10T21:56:24+08:00, 2026-11-10T21:56:51+08:00)` 显示 `102 → 101`，样本 `102` 详情显示两点。只调用正常登录和四类 GET，没有 DB 或样本写入。该 provider 当时为原 `2c4e6a8b0d12` dev。 |

## 本 Development 源文件 SHA-256

```text
a260f74e5d78e78a0646906eb8d1cbee5c0fd0c93c45fb17e52f9964af0eab17  frontend-js/src/app/acquisition-data/manifest.js
75b3726bd80055bc7bfbba92a14e0fd26a8b27735308863ffb8277c2db4446d6  frontend-js/src/app/acquisition-data/api/index.js
aadd24b5980474bb3e5c746a25b6e4c74d22111e5d5c93f3d44574f66eeb0d58  frontend-js/src/app/acquisition-data/composables/useAcquisitionScope.js
b98344b27dcb7123e12563bff6bf1d55b92ac8a95646fae368759be8932930c8  frontend-js/src/app/acquisition-data/locales/en-US.json
e0966a3c7f6112e200239c29a7c190f9fb76d532c4c9ecfef7b5b51077638fd4  frontend-js/src/app/acquisition-data/locales/zh-CN.json
0d81b686ebce19e1e48d9a7fd411eb428c8377f97b7169e2f16214b238acf94c  frontend-js/src/app/acquisition-data/views/realtime/index.vue
ed29cc930213ac09fa181fe7e2a91fffc485d37cc0c4962aaad5926330bcf66c  frontend-js/src/app/acquisition-data/views/history/index.vue
7505e3e982658c6eb545ecd09d8d8921dad895f09ae0f2e1c57e9480aa0ce434  frontend-js/src/app/acquisition-data/views/history/HistoryDetailDialog.vue
62afa2a38e7c28fce7384aa165ff295c805c048d8534567566543ae4b759e495  frontend-js/src/utils/date.js
18b45faf00c77897367494feceb7e7489768fc467b206d8ad3c23321e43fe5d9  frontend-js/src/utils/tableColumnWidths.js
a759191950ae6f2aaf68515448dcc415da8a9f886a661719ef89b6aa913fd858  frontend-js/src/utils/request.js
7bc7dbc3e2825837d19cd57fd8e017590f63acacd2cecc6f92e09a89bf8ad439  frontend-js/tests/module-registry/acquisition-data.test.mjs
```

## 限制、临时资源和精确 handoff

- 本次 dev 只读实测只有现有 admin，非 admin 的真实后端授权/拒绝、所有角色组合、更多迟到/离页路径和统一 404 的三种来源仍需 Verification 独立核对；合成测试不能代替这些真实授权证据。真实角色授权、真实设备及 DAA 新版上报与后续端到端联调不在本交付证据中。
- 保留 `/private/tmp/arch-fe005-r2-dev-SxzMqn` 供 Verification 复现：`browser-check.js`、`browser-extra.js`、`dst-check.js`、`mobile-check.js`、`dev-final.js`、合成截图、公开测试 `.env`、隔离前端和构建输出。其 `node_modules` 为指向正式前端依赖的符号链接；不得跟随链接删除正式依赖。可用 `pnpm_config_verify_deps_before_run=false pnpm --dir /private/tmp/arch-fe005-r2-dev-SxzMqn dev --host 127.0.0.1` 启动，并用已缓存 Playwright CLI 的 `run-code "$(cat browser-check.js)"` 等执行，所有 fixture 均拦截四类接口；`dev-final.js` 需要独立批准范围内的正常登录状态及可用 provider。检查该临时副本与新交付树是否一致后再使用。
- 本次创建的 Chrome 会话和 Vite 进程已停止，短时登录状态文件及临时 Playwright 日志/快照已清除。上述临时目录在独立 Verification 不再依赖、Human Owner 最终验收且协调者确认可回收后删除；不要把临时路径作为唯一结论证据。
- 请 fresh-context Verification 以本精确 r2、上述 SHA-256 和当前交付工作树为候选，独立审计允许文件与并行差异、功能/权限/浏览器矩阵、环境限制和真实 dev 读取；在自己的 `checklist.md` 写实际结果。Development 不作 QA verdict 或 Human Owner 最终验收。


## QA1 返工 · Development 新交接（2026-11-10）

QA1 已在独立 `checklist.md` 记录 `qa_failed`，返回 QA1-01 及 QA1-02；该记录和上文首次 handoff 原始证据均保留。下述是同一获批 `ARCH-FE-005 r2` 的新 Development 候选，不改变 Revision 或 QA1 结论。

- QA1-01：仅修改 `frontend-js/src/app/acquisition-data/views/realtime/index.vue` 与 `views/history/index.vue`。页面按容器实际宽度识别侧栏挤压，极窄区域增加页内顶部余量、允许标题和操作按钮换行、缩小局部表单边距，并换行显示完整已选 PLC 标识。历史页极窄区域使用两行自然换行的文本控件，与普通输入共用同一字符串、原有严格日期校验及 `+08:00` 编码；Enter 不插入换行。没有修改共享壳层、全局 CSS、访问授权或 API。
- QA1-02：本文件头部补充 `Allowed Writers: Development`。仅 Verification 可在其 checklist 中作独立复核与 verdict。
- 新候选仍是正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739` 的未提交变更。规格 SHA-256 未变，为 `442bffb872528ca6c4aed128a147fcf5521b513d05fad760511fd8d3616382ae`；QA1 checklist SHA-256 在交接时为 `433c921bc56e6b9d7b273e0e9514f2b7d20547a7ac049d2322bcfe4b797d2ce3`。两份页面的最新哈希如下，替代上文首次交接中的同名文件哈希；其余 10 个源码和测试文件仍沿用上文哈希。

```text
484e77f8b1a8cb7bc205259356ed02d7a3fe4cbd4aabcb7394aa3a2e618b99a1  frontend-js/src/app/acquisition-data/views/realtime/index.vue
2060374e24d7e66fd37ba06425c803d7c914a21e215b0a344890bc0aa7447b76  frontend-js/src/app/acquisition-data/views/history/index.vue
```

### 本轮 DEV self-check

- 先在 `/private/tmp/arch-fe005-r2-dev-SxzMqn` 修改并验证，QA1 checklist 落地后才将两页复制到正式工作树；两页正式树与隔离副本 SHA-256 一致。两页新增内容的行尾空白扫描和 `git diff --check`（适用于已跟踪文件）exit 0。
- `qa1-mobile-check.js` 在 Chrome `390 × 900`、默认展开侧栏下对中/英文、日/夜、实时/历史共 8 组合使用合成响应。页面卡头 y=313，高于共享 header 底边中文 y=290、英文 y=302；标题和按钮自身未溢出卡片。选择完整合成 PLC 后的换行标识可读；历史日期控件为 14px、两行自然换行，可用文本宽 112px，日期和时间两段分别约 76–79px、58px，且无内部纵向裁剪。输入 `2026-03-08 02:30:00` 并按 Enter 保持相同字符串，合成 history 实际请求 `from=2026-03-08T02:30:00+08:00`、`to=2026-03-08T03:30:00+08:00`；各组合打开详情且弹窗在视口内。浏览器按人工滚动可将日期放到固定 header 下方。
- `qa1-responsive-check.js` 验证侧栏折叠/展开切换时同一日期文本保留，在 `768 × 900` 和 `1280 × 900` 的两页、日夜共 8 组合中标题未被 header 遮挡；重新运行 `mobile-check.js` 覆盖 390 折叠态、实际语言/主题切换、两页和详情；`browser-check.js`、`browser-extra.js`、`dst-check.js` 分别重跑通过，覆盖现有认证、空/拒绝、逐点值、迟到响应、三表列宽、历史分页和洛杉矶夏令时输入。以上均为 Development 自检和合成接口结果。
- 在同一隔离目录重新执行 `pnpm_config_verify_deps_before_run=false pnpm check:modules`、`pnpm_config_verify_deps_before_run=false pnpm test:modules`、`pnpm_config_verify_deps_before_run=false pnpm build --outDir /private/tmp/arch-fe005-r2-dev-SxzMqn/build-qa1-final`，分别 exit 0；模块测试 50/50，构建保留 vendor chunk 超 500 kB 警告。构建使用既有锁定依赖，未安装或变更依赖。
- 390 默认展开时，中文 admin 合成账号的共享壳层 `user-menu` 曾测得右边 x=395、文档 scrollWidth=395；该 5px 溢出在本任务页面卡片之外，本轮未修改共享壳层。页面卡头、日期及按钮的本轮测量结果如上；请 Verification 独立评估此残留现象。
- 本轮未重复真实 dev 请求：上文及 QA1 的 dev 证据对应返工前候选；本轮只提供合成接口/布局回归。最终候选的真实 dev 窄屏只读检查交 fresh-context Verification，仍限制为正常登录及获准四类 GET。真实角色授权变更、DAA 联调和设备/数据库写入不在本轮范围。
- 新增临时复现脚本 `qa1-mobile-check.js`、`qa1-responsive-check.js` 及 `qa1-*.log`、合成截图与 `build-qa1-final` 均留在原临时目录供 Verification；命令方式沿用上文 Playwright CLI `run-code "$(cat 脚本名)"`。本轮 Chrome 和 Vite 已停止，临时 Playwright 会话日志已清除；目录继续按上文的 QA 与 Owner 验收后回收条件处理。

**Developer handoff：** 请 fresh-context Verification 以本节新候选及两页最新哈希复验 QA1-01、QA1-02 和受影响的历史请求、主题、列宽与页面授权行为，并在既有 checklist 追加结果。Development 不作 QA verdict 或 Human Owner 最终验收。


## QA2 返工 · Development 新交接（2026-11-10）

QA2 在独立 `checklist.md` 记录 `qa_failed`，返回 QA2-01 和 QA2-02；上文首次、QA1 返工与两轮 Verification 证据均保留。本节是同一获批 ARCH-FE-005 r2 的新 Development 候选，不改变 Revision 或已有 QA verdict。

- 先在 `/private/tmp/arch-fe005-r2-dev-SxzMqn` 实施并验证，QA2 checklist 落地后整合到正式工作树；本轮仅修改 `frontend-js/src/app/acquisition-data/composables/useAcquisitionScope.js`、`views/realtime/index.vue`、`views/history/index.vue` 和本事实记录。没有修改共享壳层、全局 CSS、权限或 API。
- QA2-01：两页共用页面局部几何测量，读取现有 `main` 和 `header.header` 的实际位置，以 `ResizeObserver` 跟随宽度、语言和主题引起的布局变化计算页内顶部余量；离页时断开。去掉固定的 48px 顶部补偿和 120px 额外边距。历史日期在容器不超过 250px 时使用同一严格字符串的三行自然换行控件；完整已选 PLC 标识也在该宽度范围内换行显示。
- QA2-02：历史分页增加局部横向滚动容器，分页内容按自身所需宽度布局，窄区初始从总数/页长一侧开始；桌面仍在可用空间右对齐。原页码与页长请求逻辑不变。
- 正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的 HEAD 仍为 `bcafa89fa31bdf62329bced89baebc193323a739`，交付候选为该树未提交改动；规格 SHA-256 为 `442bffb872528ca6c4aed128a147fcf5521b513d05fad760511fd8d3616382ae`。QA2 checklist 在本交接读取时 SHA-256 为 `62e888415ad78ebb4059792d9a0348f693999e0066e6caf10814c27f73043495`。以下三项替代上文同名源文件的旧哈希，其余九项源码/测试哈希仍沿用首次交接。

```text
e1e6e54b158b86cc68a176861de0cdc8a91dcaf52db5f4a32f3c42ac055682eb  frontend-js/src/app/acquisition-data/composables/useAcquisitionScope.js
c73f139ff3990b42dc815f7057f7ac7839fc8a5fd9b326cb99562eabebd1c189  frontend-js/src/app/acquisition-data/views/history/index.vue
f6fcfd5d147a3afb08b36369fe49f283f5f0ccad17aa9098d5dba5bf1eb60668  frontend-js/src/app/acquisition-data/views/realtime/index.vue
```

### 本轮 DEV self-check

- Chrome 合成浏览器 `qa2-layout-check.js`：360、390、460 × 中文/英文 × 日/夜 × 实时/历史共 24 组合，卡头均在实际共享 header 底边下至少 9px；日期输入、完整 PLC 标识及卡头按钮检查通过。三个宽度的两种语言在亮色下真实选择 20 条/页并点击下一页，捕获 `pageSize=20` 和 `page=2` 的合成请求。360px 英文日期可用宽 82px，日期段约 84px 时自然分三行，控件 clientHeight/scrollHeight 均 75px；390px 分页容器 clientWidth 128px、scrollWidth 385px、初始 scrollLeft 0、总数相对起点 x=4px。
- `qa2-breakpoints-check.js` 以 360、375、390、460、480、500、520、768、1280px × 两页逐项测量，标题与重置按钮中心的 `elementFromPoint` 均命中页面控件；在已打开页面上改变视口、切换中英文及主题后继续测量。`qa2-observer-check.js` 在滚动中调整视口、折叠/展开侧栏后保留日期原字符串，实际观测页面间切换时旧 observer disconnect、新 observer 注册。`qa2-measure-check.js` 补充 360/390/460 的日期和分页尺寸；均为本轮 Development 自检。
- 原 `browser-check.js`、`browser-extra.js`、`mobile-check.js`、`dst-check.js`、`qa1-responsive-check.js` 重新通过，覆盖既有合成授权、失败、迟到响应、实时值、三表列宽、分页、390 折叠、768/1280 与洛杉矶夏令时输入。合成接口请求继续保留 `+08:00` 和字符串样本 ID。
- 正式树的本轮三个文件与隔离副本 SHA-256 一致。隔离副本执行 `pnpm_config_verify_deps_before_run=false pnpm check:modules`、`pnpm_config_verify_deps_before_run=false pnpm test:modules` 和 `pnpm_config_verify_deps_before_run=false pnpm build --outDir /private/tmp/arch-fe005-r2-dev-SxzMqn/build-qa2-final2` 均 exit 0，模块测试 50/50；构建继续提示 vendor chunk 超 500 kB。三文件逐行空白扫描及 `git diff --check`（已跟踪文件）exit 0。
- QA2 的现有 dev 四类 GET 属于返工前候选；本轮没有重复真实 dev 操作，仅有合成浏览器及前端构建/测试。请 Verification 在其获准的范围内决定并记录新候选的真实只读复验；不得将旧实读表述为本轮实读。中文 admin 窄屏下共享用户菜单曾有约 5px 外溢，属页面卡片外现象，仍供独立评估，未改变共享壳层。
- 保留原临时目录内 `qa2-layout-check.js`、`qa2-breakpoints-check.js`、`qa2-observer-check.js`、`qa2-measure-check.js`、对应 `qa2-*.log` 和 `build-qa2-final2` 供独立复现；合成请求由浏览器拦截。Chrome 会话与本轮 Vite 已停止，临时 Playwright 会话日志清除。其余临时目录回收条件沿用上文，`node_modules` 符号链接指向正式依赖，不得跟随删除。

**Developer handoff：** 请 fresh-context Verification 以本节的新候选、三项哈希和正式未提交工作树，复核 QA2-01、QA2-02 及受影响的时间、分页、切换、主题和授权行为，并在既有 checklist 追加结论。Development 不作 QA verdict 或 Human Owner 最终验收。


## QA3 返工 · Development 新交接（2026-11-11）

QA3 在独立 `checklist.md` 记录 `qa_failed`，返回 QA3-01 和 QA3-02；上文 Development 与 QA1/QA2/QA3 的原始记录保留。本节仍为获批 ARCH-FE-005 r2 的新 Development 候选，不改变 Revision 或已有 QA verdict。

- 仅在 `frontend-js/src/app/acquisition-data/views/realtime/index.vue` 和 `views/history/index.vue` 改动：筛选栅格按实际内容宽度自动排列，去除按 viewport 固定切列的覆盖；页面卡头的标题、动作容器和按钮可随可用宽度自然换行。选择 PLC 后完整标识始终作为可换行文本显示，控件同时提供完整 title，不依赖悬浮提示读取。共享壳层、全局 CSS、API、时间编码和授权逻辑未改。
- 先在 `/private/tmp/arch-fe005-r2-dev-SxzMqn` 实施并验证，正式 QA3 checklist 落地后整合两页至正式工作树。交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的 HEAD 为 `bcafa89fa31bdf62329bced89baebc193323a739`，候选为该树未提交文件。规格 SHA-256 `442bffb872528ca6c4aed128a147fcf5521b513d05fad760511fd8d3616382ae`；读取时 QA3 checklist SHA-256 `fa2b6f183332de8f595669b10050cb823d6ac5bd891477810338158d31f96ddc`。以下两项替代上文同名页面的旧哈希；其余十项源码/测试仍沿用上文最新哈希。

```text
9e2ca2dc41a57555615e6bd8b71cf2d3edcbbd24e0901934ea46fc4ff5da715a  frontend-js/src/app/acquisition-data/views/history/index.vue
e0f40778e111f035efc5d7ab407d1b8d659095d6726e558a524a9f44a5fe0516  frontend-js/src/app/acquisition-data/views/realtime/index.vue
```

### 本轮 DEV self-check

- `qa3-grid-check.js` 在 Chrome 默认展开、英文暗色、先选有效合成 PLC/DB 后，逐一检查 360、375、390、420、440、450、460、480、500、510、520、550、580、600、601、620、640、650、680、700、720、768、800、900、1024、1280px 的实时及历史页。卡头标题完整，动作边框处于卡片内并可命中；实时页各宽度实际点击重置与刷新并观察新 latest 请求。部分大于 768px 的视口沿用 QA3 已记录的共享 body 最小宽度，需先文档级横向滚动才能命中远侧按钮，本轮未改该壳层样式。
- `qa3-grid-matrix.js` 在 600、601、640、650、680、700、768px × 中英文 × 日夜 × 两页共 56 组合核验完整 PLC 文本、标题、日期和动作边框/命中，并实际点击实时刷新及重置。601px 历史筛选实际为单列，日期输入可用 269px，640px 为 308px；测试日期文本按实际字体约 146.6px。测试额外选择超过 80 字符的合成 PLC，确认完整换行文本和 title 均保留；较短值在控件下方也会显示完整文本。
- 重新运行 `qa2-layout-check.js` 和 `qa2-breakpoints-check.js`，前两轮的 360/390/460 中文英文日夜布局、分页实际操作及 360–1280 断点页头命中回归通过。原计划的附加批量回归在完成这两项后按协调者要求停止，未将尚未运行或未完成的脚本记为通过。
- 在隔离前端执行 `pnpm_config_verify_deps_before_run=false pnpm check:modules`、`pnpm_config_verify_deps_before_run=false pnpm test:modules` 和 `pnpm_config_verify_deps_before_run=false pnpm build --outDir /private/tmp/arch-fe005-r2-dev-SxzMqn/build-qa3-final` 均 exit 0；模块测试 50/50，构建仍提示 vendor chunk 超 500 kB。两页正式树与隔离副本哈希一致，仍使用原锁定依赖，没有安装依赖。
- QA3 的现有 dev 四类 GET 对应返工前候选；本轮未重复真实 dev 请求，以上接口验证为浏览器合成响应。请 fresh-context Verification 在授权范围内独立决定并记录新候选的真实只读复验。共享中文 admin 窄屏 5px 外溢以及部分 viewport 的共享 body 最小宽度仍由共享壳层决定，本轮未改动。
- 本次 Chrome/Vite 已停止。`qa3-grid-check.js`、`qa3-grid-matrix.js`、对应 `qa3-*.log`、合成截图与 `build-qa3-final` 留在原临时目录供独立复核；浏览器会话日志已清除。原目录与 `node_modules` 符号链接仍按前述 QA、Human Owner 终验后由协调者确认回收的条件处理。

**Developer handoff：** 请 fresh-context Verification 使用本节两页新哈希及正式未提交工作树复核 QA3-01、QA3-02、选中后可操作性、标题与日期，并在既有 checklist 追加结果。Development 不作 QA verdict 或 Human Owner 最终验收。

## Human Owner 页面反馈 · Development 新交接（2026-11-11）

- Human Owner 指出实时数据和采集历史选中 PLC 后的重复标识会推移筛选布局，并要求将时间与保留说明放在标题右侧的问号。此次按已批准 r2 的页面、双语文案与 AC05 可读性范围修正，保留上文及 QA4 的历史证据。无筛选条件时展示授权数据属于另行协调的查询合同变化。
- 两页去除下拉框后的重复文本，选中值继续通过下拉框 `title`、包含完整标识的无障碍名称及可换行的选项读取。标题右侧使用 Element Plus 问号提示，悬停、焦点和触摸可打开，Escape 可关闭。历史提示包含原有上海时间和保留说明，实时提示保留原有时间说明。新增 `help`、`selectedPlc` 中英文对称键。
- 交付是 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 未提交工作树，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。规格 SHA-256 `442bffb872528ca6c4aed128a147fcf5521b513d05fad760511fd8d3616382ae`。本次四个最终文件及隔离副本 SHA-256 均一致：

```text
a07fd3b4e59de3e30772009d246d01b7c2eda51a1cb04adb94ab73108a85f72c  frontend-js/src/app/acquisition-data/views/history/index.vue
afc6ef9e12dc79c37db2dae06f52404c86852e89bf5bb78165d3570499b99726  frontend-js/src/app/acquisition-data/views/realtime/index.vue
c25e8104d3153bb64f9693f08a9aa450762b1e73517c32c4d5bf2b33973ab39d  frontend-js/src/app/acquisition-data/locales/zh-CN.json
102e23d476c2153eb3e7a6079280dacd1d09e0df21fc85451234a3464cc5594b  frontend-js/src/app/acquisition-data/locales/en-US.json
```

### 本轮 DEV self-check

- 在排除真实 `.env*` 的隔离前端副本使用合成登录和 `GET /api/v1/` 浏览器拦截，执行 Chrome 布局与交互检查，最终两轮分别为 **24/24、16/16**，覆盖两页、中英文、日夜主题和 390、601、640、768、1280px。核对选 PLC 前后筛选项坐标和高度一致、无重复标识、长标识在下拉完整换行、`title` 和输入无障碍名称保留完整值。问号悬停、焦点、Escape 和 390px 触摸上下文通过，选 DB 后实际触发合成 latest/history 请求并显示返回结果。
- 协调者在已有 5190 服务的独立浏览器页观察到两页 PLC 控件选中前后均为 62px，历史 DB 与日期位置一致；标题说明可打开，实际实时页显示 `820.5` 和 `false`，历史页查询显示两份现有样本。该只读观察发生在最后补充 Escape 处理之前，本轮独立测试使用合成响应。
- 隔离副本执行 `pnpm --config.verify-deps-before-run=false run check:modules`、`pnpm --config.verify-deps-before-run=false run test:modules`、`VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' VITE_FRONTEND_MOCK_ENABLED=false VITE_LOGIN_DEMO_ACCOUNTS_ENABLED=false pnpm --config.verify-deps-before-run=false run build --outDir /private/tmp/arch-fe005-r2-feedback-dev-eQBZUHeg/dist-final`，均 exit 0；模块测试 **50 passed**，构建报告既有超 500 kB chunk 提示。两份 locale 共 48 个叶键，键集相同。`git diff --check` 和四份新增源码的尾随空白检查均 exit 0。
- 本任务测试浏览器 `fe005-feedback` 已关闭，临时 Vite 5274 已停止并核对无监听，已有 5190 保持运行。`/private/tmp/arch-fe005-r2-feedback-dev-eQBZUHeg/` 留有合成测试脚本、日志、构建结果与展开的历史说明截图 `history-help.png`（SHA-256 `8151eb4c3011f3f53c89f0d76eac6cf2f23a034804c10a8fc534d50d8672c2d6`），供独立复核及 Human Owner 验收。副本 `node_modules` 是指向既有隔离依赖的符号链接，回收时不可跟随。

**Developer handoff：** 请 fresh-context Verification 使用上述精确 r2、正式工作树和四项摘要，复核两页选择后布局、长标识、帮助触发及关联查询。Development 自检及协调者观察不构成 QA verdict 或 Human Owner 最终验收。
