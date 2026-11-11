Task ID: ARCH-FE-005
Revision: r2
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA / Verification -> Human Owner 最终验收 ARCH-FE-005 r2
Workflow Mode: STD
Execution Mode: agent_team_same_session
Updated: 2026-11-11 Asia/Shanghai

# 独立 Verification · QA1

## 验证对象与环境

- 串行交接后由命名 `verification` 在 fresh context 核验。独立读取根目录与 `frontend-js/` 的工程约定、模块手册、任务两份已有文档、正式候选源码和差异，按 `project-governance`、`frontend-ui`、`i18n-workflow`、`backend-arch`、`code-document-indexer` 和 `playwright` 的相关验证约定执行。角色控制为 `contract_only`。 [项目契约](../../AGENTS.md) · [开发工作流](../../.codex/workflows/development-lifecycle-workflow.md) · [前端手册](../../frontend-js/src/app/README.zh-CN.md)
- 正式树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。`spec.md` SHA-256 `442bffb872528ca6c4aed128a147fcf5521b513d05fad760511fd8d3616382ae`，`tasks.md` SHA-256 `ac7484652763d5e915fbc4378a8db828102e0d552b5cf09989b7e1817e4bf50a`。两者与交接相符。Development 的 12 个源码和测试摘要在正式树及隔离副本均匹配。 [获批规格](spec.md) · [Development handoff](tasks.md)
- Darwin arm64，Node `v22.19.0`、pnpm `11.11.0`、Vite `5.4.21`、Chrome `157.0.8103.39`。在 `/private/tmp/arch-fe005-r2-qa-Phy9qfyC` 从正式树复制前端，排除 `.env*`、`node_modules`、`dist`，随后克隆正式树已有的锁定依赖到隔离目录。端口 `5199` 代理到现有 dev，`5200`、`5201` 用公开合成页 grant 及浏览器拦截，代理目的为 `127.0.0.1:9`。真实前端 `.env` 未用于任何验证。三套环境的 mock 均关闭，登录演示开关为关闭态。

## 验收结果

| 标准 | 结果 | 独立证据 |
| --- | --- | --- |
| AC01 装配与禁用 | 通过 | 实际 Registry 有 10 组、25 条 route，采集组顺序 100，实时与历史稳定 pageId 为 `acquisition-data.realtime`、`acquisition-data.history`，顺序 10、20。生产 Registry 装配算法在隔离复制中关闭此模块后为 9 组、23 条 route，移除该组、叶页、默认入口候选和双语 namespace，两项残留 grant 各自被拒绝。两种单页 grant 均独立核验导航与路由判定。Chrome 验证 admin 默认 `/dashboard/home`、只有实时 grant 时默认实时且历史直达回落实时、仅业务页 grant 时直达实时回落 `/dashboard/home`。 |
| AC02 双层权限 | 通过 | Chrome 覆盖未登录、过期会话 401 清 token 并跳登录、admin 有范围和空范围、非 admin 单页 grant 加后端允许、仅业务页 grant、采集页 grant 加后端 403、有合成 API 读权限但无采集 grant。后两类分别观察页面本地化拒绝和页面被路由守卫拦下。已选 PLC/DB 从可读变为越范围后，实时及历史列表的 403 清掉旧行并显示拒绝。三种合成详情 404（越范围、过期、不存在）返回不同内部键，但 UI 提示相同。实际鉴权见下节。 |
| AC03 实时与切换 | 通过 | 合成同一 DB 展示 `123.75`、`0`、`false`、空字符串 `""`、缺测和坏质量。空点名回退到 pointId，缺失与不可解析时间均显示缺失。按点名或 pointId 查找、刷新保留采集时刻和原始精度，刷新在途时按钮禁用。两次挂起响应跨 DB 再跨 PLC 返回后未覆盖新数据，离页回页和较新 401 后释放旧响应也未复现旧值。403、500、重试、空结果各自呈现。 |
| AC04 历史与时间 | 通过 | 默认 24 小时和每页 50 条，两种时区下 7 天整可提交、7 天加一秒在本地拒绝。上海与洛杉矶浏览器均发 `from=2026-03-08T02:30:00+08:00`、`to=2026-03-15T02:30:00+08:00`，覆盖洛杉矶夏令时跳变小时。合成 provider 在起点返回样本、在终点排除样本，页面维持同时间后端顺序，下一页实际请求 `page=2`。`9007199254740995` 按原字符串直达详情，保留完整点集。`2026-03-07T18:30:00.123456Z` 两种时区均显示 `2026-03-08 02:30:00`，原值完整保存在 DOM title。空结果和三类 404 均已观察。 |
| AC05 双语与列宽 | **失败 QA1-01** | 46 个中英文叶子键结构一致，静态文案和 manifest 标题键均能从装配消息解析。Chrome 实际切换中文、英文的菜单、标题、拒绝、空态，点质量和时间缺失文案可见。三张表的真实拖拽均复验通过，实时验证刷新、重开和最小宽度，历史首列 `260 → 330` 并翻页保留，详情首列 `190 → 260` 并关闭重开恢复。单表重置独立，过时键回退由定向模块测试覆盖。390px 折叠后可横向滚动，桌面和 768px 默认展开的历史筛选可读。390px 默认展开的亮暗两态均有阻断可读性的剪裁，见下节。 |
| AC06 两类读取证据 | 通过 | 独立合成夹具记录 33 个采集 GET，均附合成 Bearer，覆盖空、拒绝、迟到、异常和值。仅在进入原默认 dashboard 时有 18 个原页面请求，被本地浏览器拦截，未发至 dev。采集错误路径未观察到旧数据源请求。独立真实 dev 权限和读数见下节。 |
| AC07 源码交付 | 源码、构建通过；交接治理需补齐 QA1-02 | 正式工作树与隔离候选一致，正常 `pnpm dev` 入口实跑。`check:modules`、`test:modules`（50/50）、`build` 均 exit 0。`git diff --check` 通过。任务新增模块、工具、测试及现有 `date.js`、`request.js` 的改动均在 r2 allowlist，`CODE_INDEX.md` 中本任务仅两条。共享 request diff 仅增加按调用关闭错误提示的分支，维持既有认证与解包。两个既有列表测试为并行差异，只排除采集模块条目，仍由独立采集测试验证该模块。任务相对链接及锚点有效。 |

## QA1-01 · 390px 默认展开时页面时间及操作不可完整读取

使用 Chrome `390 × 900`、新装载页面、默认展开侧栏。在采集历史选择合成 PLC/DB 并输入 `2026-03-08 02:30:00`，回到页面顶部。亮暗两态分别截图和测量。真实 dev 历史在相同视口的 `2026-11-10 21:56:24` 也复现，同一浏览器调整尺寸时没有新增业务请求。

| 视口与侧栏 | `main` 宽度 | 全局 `header.header` 底边 | 页面 `main .data-card .base-card__header` 顶边 | 日期 `.el-input__inner` 可见宽度 |
| --- | ---: | ---: | ---: | ---: |
| 1280 默认展开，日夜 | 1044px | y=84 | y=91 | 180px |
| 768 默认展开，日夜 | 532px | y=186 | y=193 | 199px |
| 390 默认展开，日夜 | 154px | y=302 | y=193 | 74px |
| 390 手动折叠，日夜 | 390px | y=186 | y=188–193 | 310px |

- 日期 DOM 为 `main .filter-form input.el-input__inner[placeholder="YYYY-MM-DD HH:mm:ss"]`。在 390px 默认态，输入文字按当前字体约需 105px，合成 `scrollWidth=147px`，真实 dev `scrollWidth=135px`，可见宽度仅 74px。截图中两个时间框只可见日期开头，PLC 值也被截短。
- `.base-card__header` 属于页面，承载标题和 `.table-actions` 内的列宽重置。390px 默认态下该区域宽 128px、`scrollWidth=193px`，高度范围 y=193–296 完全被共享 `header.header` 的 y=0–302 区域遮住，截图无页面标题和重置按钮。共享壳层初始展开为 236px。 [历史页模板](../../frontend-js/src/app/acquisition-data/views/history/index.vue) · [共享壳层](../../frontend-js/src/layouts/MainLayout.vue)
- 390px 手动折叠后，两页和样本详情在亮暗主题下均可操作。实时表体可视 332px、总宽 980px，实际将 `scrollLeft` 调至 200px。历史表体同状态为 332px/880px，详情弹窗留在视口内。这些通过项不解除默认态失败。

## AC06 · 现有 dev 独立只读证据

使用已运行 `127.0.0.1:8000`，对应交接指定的 3307 dev 和 Alembic `2c4e6a8b0d12`。数据库身份采用已存在的 ARCH-BE-012 独立核验证据，本轮通过 HTTP 核对样本与合同，未另开数据库连接。常规登录仅使用进程内 settings，短时 token 经管道传给隔离 Chrome 上下文，不输出密码、账号名、令牌、认证头或写入浏览器状态文件。匿名 `GET options` HTTP 401，现有 admin 和 operator 登录 HTTP 200，已认证 operator 的 `GET options` HTTP 403。 [后端 dev 独立证据](../ARCH-BE-012-simplified-plc-facts/checklist.md#独立-verification现有-dev-功能验收)

| admin 浏览器请求 | HTTP | 显示及对账 |
| --- | ---: | --- |
| `GET /api/v1/acquisition-data/options`，实时及历史页各一次 | 200 | 可选择 `PLC-BE012-DEV-441247C3 / DB21`。 |
| `GET /api/v1/acquisition-data/latest?plcId=PLC-BE012-DEV-441247C3&dbNumber=21` | 200 | `furnace_temp=820.5`、`heating_ready=false`，均为 Good，显示 `2026-11-10 21:56:44`。各自 DOM title 保留 `.308915+08:00`、`.313915+08:00`。 |
| `GET /api/v1/acquisition-data/history`，同一 PLC/DB，`from=2026-11-10T21:56:24+08:00`、`to=2026-11-10T21:56:51+08:00`、`page=1`、`pageSize=50` | 200 | 顺序为 `be012-dev-441247c3-102` → `be012-dev-441247c3-101`。 |
| `GET /api/v1/acquisition-data/history/1` | 200 | 样本 102 的详情完整显示两点及原值、质量和采集时刻。 |

浏览器使用 `America/Los_Angeles` 时区，以上为全部实际采集请求，未观察到尝试访问其他业务 API。dev 取证仅使用正常登录和获准的 GET。非 admin 正向后端授权的不同范围组合使用合成矩阵，实际 operator 拒绝由 HTTP 证实。

## 命令、治理与收尾

- 隔离目录执行 `pnpm_config_verify_deps_before_run=false pnpm check:modules`、同环境的 `pnpm test:modules` 与 `pnpm build`，最终均 exit 0。构建有 vendor chunk 超 500 kB 的警告。首次公开 fixture 的 operator grant 超出 supervisor 子集，Vite 拒绝启动与构建。改正隔离 `.env` 后重跑通过，未改项目配置。
- `shasum -a 256 -c` 对交接中的 12 项摘要核对通过。`git diff --check -- frontend-js CODE_INDEX.md` exit 0，Python 检查新增文件行尾与 bundle 的 24 条相对链接及适用锚点，exit 0。`node verify-registry.mjs` exit 0。浏览器入口 `pnpm dev --host 127.0.0.1 --strictPort`，锁定依赖与临时服务同上。`node run-fixture.cjs fixture.js`、`node run-fixture.cjs layout.js`、`node run-fixture.cjs widths-realtime.js`、`node run-fixture.cjs widths-history.js` 最终均 exit 0，其中 layout 探针断言并复现预期失败。两份宽度脚本基于公开合成夹具，重新验证并等到详情关闭和重开动画完成后读尺寸。业务页 grant 夹具单独启动 Vite 缓存，避免两个实例共用预优化缓存影响导航。
- 在 `backend/` 执行 `PYTHONDONTWRITEBYTECODE=1 FE_QA_DIR=/private/tmp/arch-fe005-r2-qa-Phy9qfyC uv run --offline --frozen --no-sync python /private/tmp/arch-fe005-r2-qa-Phy9qfyC/verify-dev.py`，由 Python 3.13.3 的 HTTPX 正常登录及检查权限，再调用 Chrome 脚本，最终 exit 0。宿主默认沙箱不允许本机网络，回环 Vite、HTTP 和 Chrome 使用经审查的本机执行。
- **QA1-02**。`bash .../project-governance/scripts/check-governance-bundle.sh "$PWD"` exit 1。`tasks.md` 的 `Allowed Writers` 字段预期 1 项、实际 0 项，由 Development 在新 handoff 补 `Allowed Writers: Development`。仓库检查同时报告与本交付无关的旧 bundle 问题。双语目录的 QA 链接和聚合状态由协调者在本记录生成后机械同步。 [Development handoff](tasks.md) · [任务目录](../README.zh-CN.md)
- 三个 QA Vite 进程和 QA Chrome 会话均已停止。隔离临时目录包含公开合成脚本、脱敏结果、视口截图、独立依赖副本和构建产物。核心测量、命令和读数已记入本文件。供返工复现，待新 QA 结论和 Human Owner 终验后由协调者盘点回收。Development 的 `/private/tmp/arch-fe005-r2-dev-SxzMqn` 按其交接条件管理。项目交付文件本轮只写本 checklist。首次 Vite 沙箱探测使用依赖软链接，在正式依赖下观察到空的忽略目录 `node_modules/.vite`，随后改用独立依赖副本。现场设备、数据库写入、Docker、DAA、部署及清退隔离候选未进入本轮操作。

## Verdict 与 handoff

**`qa_failed`。** QA1-01 返回 Development，按 r2 已批准文件范围修复并提交新交接。若需要修改共享壳层或缩小窄屏验收范围，先由 PM 修订范围并取得 Human Owner 批准。QA1-02 随新 Development handoff 关闭。新候选由 fresh-context Verification 复验，保留本轮失败记录。

Human Owner 最终验收待定。清退切换后同合同 provider 冒烟和 DAA-010 受控样本正式联调各依所属任务门槛。 [清退任务](../ARCH-ACQ-002-legacy-projection-retirement/spec.md) · [后续联调范围](spec.md#2-开工依据与只读合同)

# 独立 Verification · QA2

## 候选与环境

- 2026-11-10（Asia/Shanghai），命名 `verification` fresh context 核验同一获批 ARCH-FE-005 r2 新交接，角色控制为 `contract_only`。复核项目契约、开发工作流、前端手册、完整 bundle、两页实现及差异。采用 `project-governance`、`frontend-ui`、`i18n-workflow`、`backend-arch`、`code-document-indexer` 和 Playwright 的适用约定。 [项目契约](../../AGENTS.md) · [工作流](../../.codex/workflows/development-lifecycle-workflow.md)
- 正式树 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`，候选是未提交文件。规格 SHA-256 为 `442bffb872528ca6c4aed128a147fcf5521b513d05fad760511fd8d3616382ae`，新 `tasks.md` 为 `92f1d66e8b8180862a51f96dcb79e8ffbfbf6e639483c7f86df67414fc6e7580`，追加前 QA1 checklist 为 `433c921bc56e6b9d7b273e0e9514f2b7d20547a7ac049d2322bcfe4b797d2ce3`。12 个源码/测试文件的 SHA-256 在正式树、QA2 隔离副本和新交接间一致。与 QA1 副本相比，12 个文件只有实时页和历史页变化，最新摘要分别为 `484e77f8b1a8cb7bc205259356ed02d7a3fe4cbd4aabcb7394aa3a2e618b99a1`、`2060374e24d7e66fd37ba06425c803d7c914a21e215b0a344890bc0aa7447b76`。两页与交接元数据均在 r2 允许范围。共享壳层、全局主题、API facade、locale 和鉴权装配无本轮变更。 [获批规格](spec.md) · [新 Development handoff](tasks.md#qa1-返工--development-新交接2026-11-10)
- macOS arm64，Node `v22.19.0`、pnpm `11.11.0`、Vite `5.4.21`、Chrome `157.0.8103.39`。在 `/private/tmp/arch-fe005-r2-qa2-AlZ8aHQI` 从正式树复制前端，排除真实 `.env*`、`dist` 和 `node_modules`，克隆 QA1 已隔离的锁定依赖。5224 为公开合成夹具，5225 关闭 mock 并代理到现有 dev，5226 为仅业务 grant 的公开夹具。QA 脚本、截图和构建产物在临时目录，核心证据写在本节。

## 验收结果

| 标准 | QA2 结果 | 独立证据 |
| --- | --- | --- |
| AC01 装配与禁用 | 通过 | QA1 的 Registry、默认入口、单页、禁用和残留 grant 证据仍适用。候选装配检查为 10 组、25 条 route，50 项回归包含采集模块及 grant 测试。 |
| AC02 双层权限 | 通过，沿用 QA1 矩阵 | 两页返工未改权限与失败处理。QA1 独立验证实际匿名 401、operator 403、admin 允许及完整合成矩阵。QA2 实读复核 admin 正向路径。 |
| AC03 实时与切换 | 通过 | 合成回归重跑通过标量、缺测、异常时间、原始时间、切换和迟到、403/500/401、重试与空态。390px 两语言和日夜主题都完成刷新，实时表内部滚动容器可从 0 滚到 200px（可见 120px、表宽 980px）。 |
| AC04 历史与时间 | 通过 | 合成回归在上海和洛杉矶复核 7 天边界、稳定后端顺序、三类 404、原始精度与超安全整数 ID `9007199254740995`。390px 两语言和日夜主题均能查询、打开详情，Enter 后日期字符串保持，实际请求仍为 `from=2026-03-08T02:30:00+08:00`、`to=2026-03-08T03:30:00+08:00`。分页请求可到第 2 页，分页控件的视觉缺陷归 AC05。 |
| AC05 双语与列宽 | **失败 QA2-01、QA2-02** | QA1 指出的 390px 日期、标题和操作剪裁通过复验。390px 默认展开两页 × 两语言 × 两主题下，卡头 y=313，英文共享页头底边 y=302、中文 y=290。标题与重置可见，实时刷新可点，PLC 完整标识可读。历史两个日期控件文本宽 112px，日期段约 84px、时间段约 58px，内部高度和 scrollHeight 同为 54px。手动折叠后保留同一输入值，日期输入宽 310px。历史在 768px、1280px 的日期和标题抽查通过。实时、历史与详情三表重新通过拖拽及各自的刷新、翻页或重开回归。默认展开在其他窄宽仍遮住标题，390px 的历史分页控制另有裁剪，见下节。 |
| AC06 两类读取证据 | 通过 | QA1 的合成失败及实际权限证据仍适用。QA2 用最终候选在默认展开的 390px Chrome 独立复测现有 dev，见下节。 |
| AC07 源码交付 | 通过，QA1-02 关闭 | `Allowed Writers: Development` 补齐。源文件、diff、相对文件链接和正常 Vite 入口复核通过。隔离 `check:modules`、`test:modules`（50/50）、`build` 均 exit 0。全仓治理检查仍因其他 bundle 问题 exit 1，输出无 ARCH-FE-005 条目。 |

## QA2-01 · 相邻窄宽的页面标题或操作仍被固定页头遮住

Chrome `157.0.8103.39`，英文亮色，侧栏默认展开，打开合成采集历史，页面保持在顶部。设置下表视口宽度，逐项比较卡头坐标并用 `document.elementFromPoint` 检查标题及重置按钮中心的命中元素。360px 与 460px 的截图也显示相同遮挡。中文在 460px 同样测得共享页头底边 y=290、卡头 y=193。

| 宽度 × 高度 | 共享页头底边 / 卡头顶边 | 页面标题中心命中 | 恢复默认列宽按钮中心命中 |
| --- | --- | --- | --- |
| 360 × 900、375 × 900 | y=354 / y=313 | 共享 `.header-shell` | 页面按钮 |
| 390 × 900 | y=302 / y=313 | 页面标题 | 页面按钮 |
| 460 × 900、480 × 900 | y=290 / y=193 | 共享语言切换按钮 | 共享角色标签 |
| 500 × 900、520 × 900 | y=238 / y=193 | 共享用户信息区 | 页面按钮 |
| 768 × 900、1280 × 900 | y=186 / y=193，y=84 / y=91 | 页面标题 | 页面按钮 |

容器宽度超过 180px 后页面顶部补偿取消，460px 默认展开历史恢复单行输入，同一合成字符串 `2026-03-08 02:30:00` 的 Chrome 文本宽约 147px、输入可用宽 144px。360px 的双行输入文字区宽 82px、日期段约 84px。标题遮挡和命中结果独立复现。返工需在已批准页面范围处理默认展开的窄屏过渡，并让标题、重置和日期在可用宽度内完整可读。 [历史页面](../../frontend-js/src/app/acquisition-data/views/history/index.vue)

## QA2-02 · 390px 历史分页总数及每页条数被裁掉

Chrome `390 × 900` 默认展开，在两种语言及日夜主题查询 51 条、2 页的公开合成结果。历史 `.pagination` 的可见宽度和 `scrollWidth` 均为 128px。英文的总数位于容器相对 x=-236…-184，每页条数位于 x=-168…-40，上一页按钮位于 x=-24…8。设置 `scrollLeft` 为 -1000 和 1000 后均返回 0。截图仅显示页码等剩余部分，无法横向滚到总数或每页条数。实际点击下一页请求 `page=2` 并显示第二页合成样本，问题位于结果区分页布局。 [历史页面](../../frontend-js/src/app/acquisition-data/views/history/index.vue)

390px 默认展开中文时，采集历史与同一上下文的计划列表 `/plan/list` 都测得共享用户菜单右边 x=395、文档宽 395px。采集卡片最右 x=377、主区最右 x=390。这个共享页头溢出未妨碍本轮中文采集页按钮和日期的交互，分页缺陷单独计入 QA2-02。

## 最终候选 · 现有 dev 只读复验

使用现有 `127.0.0.1:8000` provider，其 3307 dev 和 Alembic `2c4e6a8b0d12` 身份沿用后端独立记录。QA2 未另连数据库。Chrome 从 390px、英文暗色、默认展开开始，浏览器时区 `America/Los_Angeles`。现有 admin 常规登录 HTTP 200，短时 token 仅经进程管道给浏览器。只允许下列 URL 和查询值，拦截记录为空。 [后端 dev 证据](../ARCH-BE-012-simplified-plc-facts/checklist.md#独立-verification现有-dev-功能验收)

| 实际采集 GET | HTTP | 对账 |
| --- | ---: | --- |
| `/api/v1/acquisition-data/options`，两页各一次 | 200 | `PLC-BE012-DEV-441247C3 / DB21` 可选。实时和历史卡头顶边分别 y=313、314，共享页头底边 y=302。 |
| `/api/v1/acquisition-data/latest`，同一 PLC/DB | 200 | `furnace_temp=820.5`、`heating_ready=false`，均 Good，显示 `2026-11-10 21:56:44`，DOM title 分别保留 `.308915+08:00`、`.313915+08:00`。 |
| `/api/v1/acquisition-data/history`，同一 PLC/DB，`from=2026-11-10T21:56:24+08:00`、`to=2026-11-10T21:56:51+08:00`、`page=1`、`pageSize=50` | 200 | 两个时间通过 390px 双行控件录入，结果顺序为样本 102 → 101。 |
| `/api/v1/acquisition-data/history/1` | 200 | 在同一窄屏由结果行打开样本 102，详情显示两个原值、质量及采集时刻。 |

## 命令与限制

- 以 `pnpm_config_verify_deps_before_run=false` 执行 `pnpm check:modules`、`pnpm test:modules`、`pnpm build`，退出码均 0。构建仍提示 vendor chunk 超 500 kB。以 Python 核对 12 个文件 SHA-256、新文件行尾、bundle 元数据与相对文件链接，`git diff --check -- frontend-js CODE_INDEX.md`，均 exit 0。
- `bash <project-governance>/scripts/check-governance-bundle.sh "$PWD"` exit 1，已有其他 bundle 元数据和目录项仍有报告，输出无 ARCH-FE-005 条目。QA2 核对任务三文件同为 r2，`tasks.md` 的 `Allowed Writers` 为唯一的 Development 声明，关闭 QA1-02。
- 使用前端锁定 Vite 的 `vite --host 127.0.0.1 --strictPort --port <port>` 入口与 Node Playwright 的 Chrome 通道。`node layout-qa2.cjs`、`node narrow-findings.cjs` 最终输出 390px 通过及两项窄屏缺陷复现。QA1 公开夹具迁移端口后重跑 `node run-fixture.cjs widths-realtime.js`、`node run-fixture.cjs widths-history.js` 均 exit 0。`node run-fixture.cjs fixture.js` 中实时与历史行为组通过，首轮组合脚本的 admin 默认入口等待超时，完整权限浏览器矩阵沿用 QA1；最终候选仍通过独立模块与授权测试。真实 dev 以 `PYTHONDONTWRITEBYTECODE=1 FE_QA_DIR=<qa2-dir> uv run --offline --frozen --no-sync python <qa2-dir>/verify-dev.py` 在后端项目环境执行，exit 0。回环服务与浏览器通过经审查的本机执行。
- QA2 的三个 Vite 进程和 Chrome 会话已停止，5224–5226 无监听。临时 QA2 目录含公开夹具、脱敏结果、截图、依赖副本及构建产物，供 Development 重现两个问题；后续 QA 和 Human Owner 最终验收后由协调者盘点回收。现场设备、DAA、Docker、数据库写入、真实角色授权、部署和旧表清退均属其他操作门槛。

## QA2 Verdict 与 handoff

**`qa_failed`。** 390px 的 QA1 标题与日期问题通过指定场景复验，QA1-02 已关闭。AC05 仍有 QA2-01（相邻窄宽标题与操作遮挡）和 QA2-02（390px 历史分页控件裁剪）。两项交 Development 按已批准页面范围返工，随后交新 fresh-context Verification。若返工必须改变共享壳层或接受范围，先交 PM 新 Revision 与 Human Owner 批准。Human Owner 收到本轮独立结论，最终验收待定。 [获批验收标准](spec.md#5-验收标准)


# 独立 Verification · QA3

## 候选与环境

- 2026-11-11（Asia/Shanghai），命名 `verification` fresh context 串行核验获批 ARCH-FE-005 r2。复核根契约及工作流、前端与模块文档、完整任务 bundle、正式源码、与 QA2 候选的差异和可用输出。按 `project-governance`、`frontend-ui`、`i18n-workflow`、`backend-arch`、`code-document-indexer` 及 Playwright 的相关约定核验。角色控制为 `contract_only`。 [获批规格](spec.md) · [Development 交接](tasks.md#qa2-返工--development-新交接2026-11-10)
- 正式工作树 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`，候选为未提交文件。规格 SHA-256 `442bffb872528ca6c4aed128a147fcf5521b513d05fad760511fd8d3616382ae`，Development 记录 `1780c84d5b3ff9bf6cff4b1b3483d859d29d5cc0c88d42c6d26dca1798c7c3aa`，追加前 QA2 checklist `62e888415ad78ebb4059792d9a0348f693999e0066e6caf10814c27f73043495`。12 个源码和测试的摘要与正式树、隔离副本和交接一致。相对 QA2 本任务只有共用 composable、历史页和实时页变化，依次为 `e1e6e54b158b86cc68a176861de0cdc8a91dcaf52db5f4a32f3c42ac055682eb`、`c73f139ff3990b42dc815f7057f7ac7839fc8a5fd9b326cb99562eabebd1c189`、`f6fcfd5d147a3afb08b36369fe49f283f5f0ccad17aa9098d5dba5bf1eb60668`。本轮三处实现均在获批范围内。
- macOS arm64，Node `v22.19.0`、pnpm `11.11.0`、Vite `5.4.21`、Chrome `157.0.8103.39`。从正式树复制前端至 `/private/tmp/arch-fe005-r2-qa3-jHqL1DD0`，排除正式环境文件、依赖和构建目录，复制已隔离的锁定依赖。5244 使用公开合成配置并由浏览器拦截 API，5245 关闭 mock 并代理至现有 dev。核心复现步骤、读数和结论在本文件留存。

## 验收结果

| 标准 | QA3 结果 | 独立证据 |
| --- | --- | --- |
| AC01 装配与禁用 | 通过 | 本轮装配检查确认 10 个组、25 条路由。Registry、默认入口、单页 grant、禁用及残留 grant 的 QA1/QA2 独立证据仍适用。 |
| AC02 双层权限 | 通过 | 本轮模块权限测试及实际管理员正向读取通过。拒绝和组合矩阵采用 QA1/QA2 独立证据。复用的 Development 综合夹具期望 operator 无采集 grant，和本轮 QA2 公共配置授予 operator 实时页冲突，因此未将该脚本超时当成产品结果。 |
| AC03 实时与切换 | 通过 | 独立合成回归复核原值、失败及切换，390px 两种语言与主题下实际刷新并将表内滚动到 200px。更宽处的刷新按钮视觉缺陷计入 AC05。 |
| AC04 历史与时间 | 通过 | 合成历史请求保留 `+08:00`、提交区间和超安全整数 ID。390px 实际改变页长及翻页，打开详情检查布尔值。QA1/QA2 的两时区、7 天边界和不可用详情证据仍适用。 |
| AC05 双语与列宽 | **失败 QA3-01、QA3-02** | 双语结构及三表宽度独立回归通过。QA2 的固定页头纵向遮挡和历史分页裁剪按原场景关闭。扩测发现英文实时刷新操作横向裁剪，以及历史两列布局截断标题、日期和已选 PLC。 |
| AC06 两类读取证据 | 通过 | 公开合成状态及无旧源回退沿用 QA1/QA2 独立证据，本轮复跑可用回归。最终候选另在现有 dev 完成四类实际读取。 |
| AC07 源码交付 | 通过 | 12 个候选摘要匹配，新增文件行尾、bundle 元数据、相对文件链接及 Git diff 检查通过。隔离 `check:modules`、`test:modules`、`build` 均 exit 0。 |

## QA2 缺陷复验

- 两页在 360、375、390、460、480、500、520、768、1280px 默认展开，中英文及日夜主题均复核卡头与共享页头、标题和重置按钮。静止顶部的卡头至少低 9px，标题与重置中心命中页面元素。390px 手动折叠后主区宽 390px，卡头 y=195，页头底边 y=186，标题和重置按钮可点。滚动中 390 → 460px，英文主区保留 `scrollTop=170`，卡头自然位置 y=299、页头底边 y=290。折叠和展开后日期保持同一原字符串，历史切换到实时从观察器 1 断开并注册观察器 2。
- 360、375、390、460、480、500、520px 历史选定 PLC 后核验日期。360px 两个日期的文本宽 82px，高度与 scrollHeight 同为 75px，日期自然换行，无纵向裁剪。390px 的文本宽 112px，高度及 scrollHeight 同为 75px。520px 输入切回单行，可用宽 204px。
- 390px 默认展开，历史分页容器可见宽 128px，总宽英文 348px、中文 347px。初始 scrollLeft 为 0，总数从容器 x=4px 开始，两种语言均读到 51 条。中英文和日夜共四组实际选择每页 20 条再滚到末尾点击下一页，分别捕获 `page=1&pageSize=50`、`page=1&pageSize=20`、`page=2&pageSize=20`，各保留同一 `[from,to)` 并正确显示响应样本。
- 中文 390px 仍可见共享用户菜单右缘 x=395。QA2 在计划列表也记录同一共享现象。本轮额外抽样 1000/1001px 时页面采用共享 `body` 的 1280px 最小宽度，需要文档级横向移动才可命中最右控件。两项属共享壳层，本轮变更及以下两项模块缺陷均不涉及该样式。 [共享样式](../../frontend-js/src/styles/theme.css)

## QA3-01 · 英文实时刷新在默认展开的相邻窄宽被卡片裁剪

Chrome `460 × 900`、默认展开、英文亮色。打开实时页，选择合成 PLC 和 DB21，等待逐点结果，回到主区顶部。卡头 y=299，低于共享页头底边 y=290，标题和重置按钮命中。刷新已启用，按钮的范围是 x=452–540，卡片在 x=448 结束，按钮中心命中失败，无法从卡头刷新。441、450、470、480、500px 同样无法命中刷新按钮中心。510、520、540px 可命中中心，按钮右部仍越过卡片右边界。390 和 440px 的动作组已换行，555 和 560px 的动作组可完整容纳按钮，四处均通过命中。英文暗色的初始几何探针也在 460、480、500px 复现中心命中失败。页面局部动作组的换行边界和卡头顶部补偿分别起作用。 [实时页面](../../frontend-js/src/app/acquisition-data/views/realtime/index.vue)

## QA3-02 · 历史两列筛选截断已选 PLC、日期和部分标题

Chrome 默认展开，打开历史并选择 `PLC-BE012-DEV-441247C3 / DB21`。关闭下拉后，600px 单列可完整阅读。601px 切为 150px + 150px 两列，PLC 标签可用 106px，实测 scrollWidth 187px。620、640、660、680、700、720、768px 抽样仍复现截断，对应可用宽 106、113、123、133、143、153、177px。601 和 640px 复验了中英文和日夜四组，截图显示 601、640 和 768px 英文确实出现省略。已选标签使用 `overflow: hidden` 和 `text-overflow: ellipsis`，模块内完整标签为 `display: none`。601、640、768px 英文选定值无原生 title，悬停 800ms 无可见提示。

601 和 620px 的两个日期单行输入实际可用 128px，实测 scrollWidth 138px 和 135px，截图显示尾部被裁。640px 两个输入各可用 135px，其中开始时间仍需 138px。660px 该日期样例可完整读。测量使用当次初始 24 小时窗口 `2026-11-10 00:07:43` 至 `2026-11-11 00:07:43`，使用 DOM 原生宽度及实际字体复核。英文标题在 601、620px 的可用宽为 112、131px，内容宽 145px，601px 截图显示 `Acquisition …`，640px 标题完整。三个现象均发生在固定页头下方。 [历史页面](../../frontend-js/src/app/acquisition-data/views/history/index.vue)

## 最终候选现有 dev 只读证据

现有 `127.0.0.1:8000`，对应 3307 dev 及 Alembic `2c4e6a8b0d12` 的身份沿用后端独立记录。通过后端项目环境在进程内正常管理员登录 HTTP 200，短时令牌仅经管道传入隔离浏览器。Chrome 390px、默认展开、英文暗色，浏览器时区 `America/Los_Angeles`。 [后端 dev 证据](../ARCH-BE-012-simplified-plc-facts/checklist.md#独立-verification现有-dev-功能验收)

| 实际 GET | HTTP | 页面及响应对账 |
| --- | ---: | --- |
| `/api/v1/acquisition-data/options`，两页各一次 | 200 | 可选择 `PLC-BE012-DEV-441247C3 / DB21`。 |
| `/api/v1/acquisition-data/latest`，同一 PLC/DB | 200 | `furnace_temp=820.5`、`heating_ready=false` 均为 Good，显示 `2026-11-10 21:56:44`，DOM title 保留 `.308915+08:00`、`.313915+08:00`。 |
| `/api/v1/acquisition-data/history`，同一 PLC/DB，`from=2026-11-10T21:56:24+08:00`、`to=2026-11-10T21:56:51+08:00`、`page=1`、`pageSize=50` | 200 | 390px 双行输入录入的区间一致，保留样本顺序 102 → 101。 |
| `/api/v1/acquisition-data/history/1` | 200 | 从结果行打开样本 102，显示两个原值、质量及采集时刻。 |

浏览器获准 URL 白名单之外的拦截记录为空，无浏览器错误。QA1 独立实际匿名 401、operator 403 的证据仍适用。

## 命令、限制与收尾

- 隔离前端执行 `pnpm_config_verify_deps_before_run=false pnpm check:modules`、同环境的 `pnpm test:modules` 和 `pnpm build`，均 exit 0，测试 50/50。构建仍提示 vendor chunk 超过 500 kB。Python 核对 12 项 SHA-256、新增文件行尾、bundle 元数据和相对文件链接，`git diff --check -- frontend-js CODE_INDEX.md` exit 0。全仓 `check-governance-bundle.sh "$PWD"` 因其他 bundle exit 1，输出无 ARCH-FE-005 条目。
- `pnpm dev --host 127.0.0.1 --strictPort --port 5244` 与 `pnpm dev --mode devread --host 127.0.0.1 --strictPort --port 5245` 分别为公开和实际读取入口。`node verify-qa3.cjs` exit 1，记录两语言两主题交互成功及窄宽裁剪。`node probe-final.cjs` exit 0 并记录预期的裁剪、字体测量和悬停观察。通过 `node run-fixture.cjs` 分别执行 `widths-realtime.js`、`widths-history.js`、`browser-extra.js` 及 `dst-check.js`，均 exit 0。DST 复用脚本先加载隔离登录页以获取同源 storage，然后确认洛杉矶跳时区间原样转换到上海 `+08:00`。
- 在 `backend/` 执行 `PYTHONDONTWRITEBYTECODE=1 FE_QA_DIR=<qa3-dir> uv run --offline --frozen --no-sync python <qa3-dir>/verify-dev.py`，exit 0。回环及 Chrome 经审查使用本机执行。数据库身份采用既有独立证据，本轮通过 HTTP 对账。
- QA3 的 Chrome 会话均已关闭，两个 Vite 进程已停止并复核 5244、5245 无监听。临时目录保存公开夹具、截图、脱敏读数和构建产物，供返工后复现。归属和回收条件交协调者在新 QA 结论与 Human Owner 终验后盘点。现场设备、DAA 上报、Docker、数据库写入、角色授权及清退 provider 切换仍按各自任务门槛。项目写入限本 checklist。

## QA3 Verdict 与 handoff

**`qa_failed`。** QA2-01 的共享页头纵向遮挡及 QA2-02 的历史分页裁剪关闭。AC05 的 QA3-01 和 QA3-02 返回 Development，按获批 r2 范围处理后交下一轮 fresh-context Verification。Human Owner 收到独立结果，最终验收待定。 [获批验收标准](spec.md#5-验收标准)


# 独立 Verification · QA4

## 候选与环境

- 2026-11-11（Asia/Shanghai），命名 `verification` 在 fresh context 独立复验获批 ARCH-FE-005 r2，角色控制为 `contract_only`。核对项目契约、前端与模块约定、完整任务 bundle、正式源码、QA3 候选差异和测试输出。 [获批规格](spec.md) · [Development 新交接](tasks.md#qa3-返工--development-新交接2026-11-11)
- 正式树 HEAD 为 `bcafa89fa31bdf62329bced89baebc193323a739`，交付候选为该树未提交文件。规格 SHA-256 为 `442bffb872528ca6c4aed128a147fcf5521b513d05fad760511fd8d3616382ae`，Development 记录为 `0855f2e83080ab9c974a34a51625b0e2535bdeff37c498eafc9960a5b3dc9f82`，本轮写入前 checklist 为 `fa2b6f183332de8f595669b10050cb823d6ac5bd891477810338158d31f96ddc`。12 个源码和测试摘要与交接、正式树及 QA4 隔离副本一致。对照 QA3 副本，本任务源码差异只有实时页（`e0f40778e111f035efc5d7ab407d1b8d659095d6726e558a524a9f44a5fe0516`）及历史页（`9e2ca2dc41a57555615e6bd8b71cf2d3edcbbd24e0901934ea46fc4ff5da715a`），均在 r2 范围内。
- Darwin arm64，Node `v22.19.0`、pnpm `11.11.0`、Vite `5.4.21`、Chrome `157.0.8103.39`。从正式树创建 `/private/tmp/arch-fe005-r2-qa4-63nzxGxL`，排除正式环境文件、构建目录和依赖目录，再克隆现有锁定依赖。5264 使用公开合成 grant 和浏览器接口拦截。5265 关闭 mock 与登录演示并代理到现有 dev。

## 验收结果

| 标准 | QA4 结果 | 独立证据 |
| --- | --- | --- |
| AC01 装配与禁用 | 通过 | 模块检查为 10 组、25 条路由，Registry、默认入口、单页授权、禁用及残留 grant 沿用 QA1–QA3 的独立证据。 |
| AC02 双层权限 | 通过 | 本轮现有 dev 管理员正向验证通过。页面 grant、空读范围、过期会话、实际匿名 401 和 operator 403 沿用 QA1–QA3 独立证据。 |
| AC03 实时与切换 | 通过 | 本轮在两语言、两主题及 18 个宽度共 72 个组合实际点击刷新并收到当前 PLC/DB 的 latest。标量、迟到结果和失败回归沿用 QA1–QA3 独立证据。 |
| AC04 历史与时间 | 通过 | 本轮实跑 390px 下查询、改页长、翻页和详情。保留 `+08:00` 与字符串 ID `9007199254740995`。两时区、7 天边界、同时间顺序和详情到期的独立证据沿用 QA1–QA3。 |
| AC05 双语与列宽 | **通过，关闭 QA3-01 和 QA3-02** | 两页共 128 个已选范围的视口、主题、语言组合均通过内容宽度、按钮命中和选中值检查。360/390px 日期、390px 分页及切换侧栏通过复验。双语消息和三表拖拽、恢复、重置、横向滚动沿用既有独立证据。 |
| AC06 两类读取证据 | 通过 | 本轮有独立合成浏览器读证据，失败分支沿用前三轮。当前候选再用现有 dev 成功核对四类 HTTP 与页面结果。 |
| AC07 源码交付 | 通过 | 12 项摘要、两页差异、任务元数据、相对文件链接和新增文件空白检查均通过。正常隔离 Vite 入口实跑，`check:modules`、`test:modules`、`build` 均 exit 0。 |

## QA3 缺陷复验

- **QA3-01 已关闭。** Chrome 默认展开侧栏，先选合成 `QA4-SYNTHETIC-PLC-441247C3 / DB21` 并取得数据，再分别复验 360、390、440、441、450、460、470、480、500、510、520、540、555、560、601、640、768、1280px。中英文日夜均核对按钮两端和中心的命中、实际点击重置与刷新，并观察每次刷新发出同一范围的新请求。英文暗色 460px 卡片 x=248–448，刷新 x=340–429。500px 卡片右缘 x=488，刷新 x=380–469。540px 卡片右缘 x=528，刷新 x=420–509。标题、动作组与筛选区均随实际内容宽度布局。 [实时页](../../frontend-js/src/app/acquisition-data/views/realtime/index.vue)
- **QA3-02 已关闭。** 历史在同一合成范围及中英文日夜复验 360、390、460、600、601、620、640、650、660、680、700、720、768、1280px。英文暗色 601/640px 筛选为 291/330px 单列，日期实际可用 269/308px。768px 为两个 221px 栅格，日期实际可用 199px。此次日期文字实际需要约 135.5–138.3px。标题无横向截断并通过命中。已选 PLC 在控件下方持续显示可换行的完整标识，控件原生 title 也保留同值。390px 另选 95 字符合成标识，文字在 120px 宽区域自然换行，按文字范围量测均在栅格内。 [历史页](../../frontend-js/src/app/acquisition-data/views/history/index.vue)
- **窄屏回归。** 128 组在主区滚动归零后，页面卡头均低于共享页头底边 9px。历史 360/390px 两个日期实际可用 82/112px，自然换行，`clientHeight=scrollHeight=75px`。390px 手动折叠侧栏切换成单行输入，展开后原字符串保持。默认展开的 390px 历史分页可见宽 128px，总宽中文 347px、英文 348px，初始滚动为 0 且两种语言都可读到总数 51。四个语言主题组合均实际选择每页 20 条、滚至末端点击下一页并打开详情。捕获 `page=1&pageSize=50` → `page=1&pageSize=20` → `page=2&pageSize=20`，区间保持 `[2026-03-08T02:30:00+08:00, 2026-03-08T03:30:00+08:00)`，详情 ID 保持原字符串。

## 当前候选现有 dev 只读复验

Chrome 390 × 900、侧栏默认展开、英文暗色，浏览器时区为 `America/Los_Angeles`。对现有 `127.0.0.1:8000` 正常管理员登录，HTTP 200。令牌仅在进程管道传递，浏览器仅放行已批准范围及时间区间内的四类 GET。数据库身份沿用既有独立记录。 [后端 dev 证据](../ARCH-BE-012-simplified-plc-facts/checklist.md#独立-verification现有-dev-功能验收)

| 实际 GET | HTTP | 页面与合同对账 |
| --- | ---: | --- |
| `/api/v1/acquisition-data/options`，两页各一次 | 200 | 两页均可选择 `PLC-BE012-DEV-441247C3 / DB21`。 |
| `/api/v1/acquisition-data/latest`，同一 PLC/DB | 200 | `furnace_temp=820.5`、`heating_ready=false`，质量 Good，显示 `2026-11-10 21:56:44`，原始 title 分别保留 `.308915+08:00`、`.313915+08:00`。 |
| `/api/v1/acquisition-data/history`，同一 PLC/DB | 200 | 窄屏录入 `[2026-11-10T21:56:24+08:00, 2026-11-10T21:56:51+08:00)`，请求 `page=1&pageSize=50`，页面保持样本顺序 102 → 101。 |
| `/api/v1/acquisition-data/history/1` | 200 | 打开样本 102 详情，核对完整两点及值、质量和采集时刻。 |

浏览器对账无非白名单尝试和页面错误。本轮实读只复验现有管理员路径，实际拒绝证据沿用 QA1。清退切换后的同合同 provider 冒烟，以及 DAA-010 的受控样本对账仍各按其任务门槛。 [清退任务](../ARCH-ACQ-002-legacy-projection-retirement/spec.md) · [后续联调范围](spec.md#2-开工依据与只读合同)

## 命令、限制与收尾

- 隔离目录执行 `pnpm_config_verify_deps_before_run=false pnpm check:modules`、同环境的 `pnpm test:modules` 和 `pnpm build`，均 exit 0，测试 50/50。构建继续提示 vendor chunk 超过 500 kB。`git diff --check -- frontend-js CODE_INDEX.md`、Python 摘要和新增文件行尾检查，以及写入前 bundle 元数据和 39 个相对文件链接检查均 exit 0。
- 在同目录运行 `pnpm dev --host 127.0.0.1 --strictPort --port 5264` 和 `pnpm dev --mode devread --host 127.0.0.1 --strictPort --port 5265`。默认沙箱拒绝回环监听，经审查用本机执行。`node qa4-layout.cjs` 最终 exit 0，128 组测量无失败。首次合成探针 glob 同时拦截了源码模块路径，调整隔离夹具为只匹配根 `/api/` 后重跑。在 `backend/` 执行 `PYTHONDONTWRITEBYTECODE=1 FE_QA_DIR=<qa4-dir> uv run --offline --frozen --no-sync python <qa4-dir>/verify-dev.py`，exit 0。
- 已记录的共享用户菜单在中文 390px 的少量文档级横向外溢，以及 769–1023px 的共享最小宽度约束仍适用。360px 英文抽样文档宽 380px，页面卡片结束于 x=348，模块控件仍完整命中。此次模块验收使用主区内控件可读与可操作作为判定，保留共享壳层限制。 [共享样式](../../frontend-js/src/styles/theme.css)
- QA4 两个 Chrome 会话已关闭，5264 和 5265 的 Vite 服务均已停止。独立临时目录保存合成夹具、脱敏日志、截图和构建产物，待 Human Owner 最终验收后由协调者盘点回收。项目写入限本 checklist。

## QA4 Verdict 与 handoff

**`qa_passed`。** QA3-01 和 QA3-02 关闭，ARCH-FE-005 r2 的 AC01–AC07 独立验证完成。交 Human Owner 最终验收。 [获批验收标准](spec.md#5-验收标准)

# 独立 Verification · QA5（页面反馈复验）

## 候选与范围

- 2026-11-11（Asia/Shanghai），命名 `verification` 在 fresh context 串行复验获批 ARCH-FE-005 r2 的最新 Development handoff，角色控制为 `contract_only`。独立核对项目契约、工作流、根与前端约定、完整任务 bundle、正式源码与 QA4 候选的差异、Development 自检输出。按 `project-governance`、`frontend-ui`、`i18n-workflow`、`backend-arch` 的适用约定核验，并用 Playwright 驱动隔离 Chrome。 [获批规格](spec.md) · [最新 Development 交接](tasks.md#human-owner-页面反馈--development-新交接2026-11-11)
- 正式工作树 HEAD 为 `bcafa89fa31bdf62329bced89baebc193323a739`，候选是正式树未提交文件。规格 SHA-256 为 `442bffb872528ca6c4aed128a147fcf5521b513d05fad760511fd8d3616382ae`，Development 记录为 `42c276eeb814e002678d7b57167a85b5db34627c04b35323020e871595fce137`，追加前 checklist 为 `85683e0deaecce848fdbc8f0430e2c1ea736385b7ac453c8fad878cb2e217b63`。12 个任务源码与测试文件的摘要在正式树、隔离副本和最新交接间一致。相对 QA4，仅实时页、历史页和双语 locale 四份文件变化，均在获批范围。两页只改标题说明、PLC 选择控件和相应样式，查询逻辑、facade、授权、三表列宽及共享壳层仍适用 QA4 独立证据。并行 System manifest 清退使全前端 route 数由 25 变为 24，采集模块的两条路由与稳定 pageId 仍在。 [实时页](../../frontend-js/src/app/acquisition-data/views/realtime/index.vue) · [历史页](../../frontend-js/src/app/acquisition-data/views/history/index.vue)
- Darwin arm64，Node `v22.19.0`、pnpm `11.11.0`、Vite `5.4.21`、Chrome `157.0.8103.39`。从正式树复制前端至 `/private/tmp/arch-fe005-r2-qa5-NYOFYfLi/source`，排除正式环境文件、依赖目录和构建目录，再克隆 QA4 隔离的锁定依赖。使用公开空 grant，关闭 mock 和登录演示。5284 的采集 API 由独立浏览器夹具拦截，5285 代理到现有 dev。

## 验收结果

| 标准 | QA5 结果 | 独立证据 |
| --- | --- | --- |
| AC01、AC02 | 通过 | 本轮模块检查为 10 个组、24 条路由，50 项回归通过。现有 dev 管理员读取通过，页面授权矩阵、禁用、匿名 401 和 operator 403 沿用 QA1–QA4 的独立证据。 |
| AC03、AC04 | 通过 | 合成浏览器选中 102 字符 PLC 和 DB21 后，实时展示 `false`，历史按手动输入的上海半开区间发出请求，保留样本 ID `9007199254740995` 并打开详情。实际 dev 的四类读取见下。时间边界、迟到结果和失败处理沿用 QA1–QA4 的独立证据。 |
| AC05 | 通过 | 两页在 390、601、640、768、1280px 下各测中文亮色和英文暗色，共 20 个合成组合。选择前后的全部筛选项 x、y、宽、高读数一致，筛选区仅出现一份选中 PLC 文本，控件 title 和可访问名称保留完整标识。390px 下拉选项分 5 行，文字在可视范围内。两份 locale 的 48 个叶键对称。三表列宽的拖拽、恢复、重置及滚动沿用 QA1–QA4。 |
| AC06 | 通过 | 本轮独立合成请求与浏览器断言，以及现有 dev 四类读取对账均通过。合成失败与拒绝路径沿用 QA1–QA4。 |
| AC07 | 通过 | 正常隔离 Vite 入口、12 项候选摘要、四份反馈差异、bundle 元数据、相对链接和新增文件行尾检查通过。`check:modules`、`test:modules`、`build` 均 exit 0。 |

## 反馈项复验

- **筛选布局。** 1280px 历史页的 PLC、DB、起止时间四个筛选项选中前后均为 62px 高、顶部 y=181。390px 默认展开侧栏，历史和实时的 PLC、DB 筛选项高度均为 59.59px，选中前后相邻项及历史起止时间、查询按钮的位置一致。英语暗色的历史长选项在 360/390px 的宽度为 239px、高度约 110px，动画结束后文字横向范围分别为 x=140–322.25、x=170–352.25，均落在视口内。
- **标题说明。** 悬停问号、用 Tab 聚焦、用 Escape 关闭键盘打开的说明，20 个合成组合均通过。两页说明均含上海时间，历史还显示三个上海自然月、物理清除上限前 24 小时以及样本最早截止点的原有说明。问号具有本地化按钮名称并通过 `aria-describedby` 关联说明。390px 触摸上下文中，两页点击问号均能打开。按 Escape 会取消按钮焦点，下一次 Tab 继续到列宽重置按钮。只悬停且按钮未获焦点时，移开指针会关闭说明，Escape 不关闭。这一观察限定了本轮通过的 Escape 交互。
- **脱敏截图。** `/private/tmp/arch-fe005-r2-qa5-NYOFYfLi/history-help-1280.png` 显示 1280×900 中文亮色历史页、已选合成 PLC 和展开的时间及保留说明。SHA-256 为 `fc826b7ae686c67879c632ad3093b1404e237cbf46ce4ea40382a42a33699bb5`。截图只使用合成上下文。

## 当前候选现有 dev 只读复验

Chrome 390×900，侧栏默认展开，英文暗色，浏览器时区 `America/Los_Angeles`。对现有 `127.0.0.1:8000` 正常管理员登录 HTTP 200。令牌仅经进程管道传入浏览器，业务请求采用四类 GET 白名单。页面说明的焦点与 Escape 在两页同时复验。 [后端 dev 证据](../ARCH-BE-012-simplified-plc-facts/checklist.md#独立-verification现有-dev-功能验收)

| 实际 GET | HTTP | 页面与合同对账 |
| --- | --- | --- |
| `/api/v1/acquisition-data/options`，两页各一次 | 200 | 选中既有合成范围 `PLC-BE012-DEV-441247C3 / DB21`。 |
| `/api/v1/acquisition-data/latest` | 200 | 两行分别为 `furnace_temp=820.5`、`heating_ready=false`，均为 Good，采集时刻显示 `2026-11-10 21:56:44`，DOM title 分别保留 `.308915+08:00` 与 `.313915+08:00`。 |
| `/api/v1/acquisition-data/history` | 200 | 实际请求区间为 `[2026-11-10T21:56:24+08:00, 2026-11-10T21:56:51+08:00)`，`page=1&pageSize=50`，页面按 102 → 101 显示两份样本。 |
| `/api/v1/acquisition-data/history/1` | 200 | 从样本 102 打开详情，核对两点原值、质量和采集时刻。 |

浏览器没有非白名单尝试和页面错误。真实拒绝场景沿用 QA1 的证据。清退切换后的同合同 provider 冒烟和 DAA-010 样本联调各按所属任务门槛。 [清退任务](../ARCH-ACQ-002-legacy-projection-retirement/spec.md) · [后续联调范围](spec.md#2-开工依据与只读合同)

## 命令、限制与收尾

- 隔离源码目录执行 `pnpm --config.verify-deps-before-run=false run check:modules`、同选项的 `run test:modules` 及 `run build --outDir <QA5-dir>/build`，均 exit 0，模块回归 50/50。构建报告既有 500 kB chunk 提示。`git diff --check -- frontend-js CODE_INDEX.md` 与 Python 检查任务文件 SHA-256、四份变更文件行尾、任务元数据、48 个 locale 叶键及追加前 48 条相对文件链接均 exit 0。
- 两个隔离入口均使用 `pnpm --config.verify-deps-before-run=false run dev --host 127.0.0.1 --strictPort --port <5284 或 5285>`。回环与 Chrome 使用经审查的本机执行。`QA5_DIR=<QA5-dir> node qa5-feedback.cjs` 最终 exit 0。首次夹具以 DOM 顺序推断 Tab 前置位置，断言失败，改为真实 Tab 逐次导航后重跑通过。补充 `qa5-viewport.cjs` 与 `qa5-screenshot.cjs` 均 exit 0。在 `backend/` 执行 `PYTHONDONTWRITEBYTECODE=1 FE_QA_DIR=<QA5-dir> uv run --offline --frozen --no-sync python <QA5-dir>/verify-dev.py`，exit 0。
- QA5 Chrome 已关闭，两个隔离 Vite 已停止，现有 5190 和 8000 继续运行。本轮临时目录留有合成脚本、脱敏日志、截图和构建结果，供 Human Owner 验收，待验收后由协调者盘点回收。此前共享页头的窄屏文档级外溢和共享最小宽度约束仍适用。项目写入限本 checklist。 [共享样式](../../frontend-js/src/styles/theme.css)

## QA5 Verdict 与 handoff

**`qa_passed`。** ARCH-FE-005 r2 的页面反馈复验完成。交 Human Owner 最终验收。 [获批验收标准](spec.md#5-验收标准)

