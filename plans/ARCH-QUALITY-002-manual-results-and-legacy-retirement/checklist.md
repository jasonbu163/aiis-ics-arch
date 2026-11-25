Task ID: ARCH-QUALITY-002
Revision: r1
Status: owner_accepted
Owner Role: Verification
Allowed Writers: Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session
Updated: 2026-11-24 Asia/Shanghai
Handoff: Human Owner 已完成最终验收

# 独立验证记录

在正式工作树独立复核 HEAD `7f654ac` 对应未提交候选。规格 SHA-256 为 `9c15350c296bdcf46ba94186b53523a3c5dad5d865b2d9e8cc15107964cc8673`，开发交接为 `f5e3c7e04f85cf87fe040c4f74ba5b235a9c76a6bdf8ebf805c36ef0cb7dc62d`。对 tasks.md 中 36 条路径校验 SHA-256 或删除状态，全部一致。逐项对照规格第 5 节；其余 tracked diff 仅涉及审批规格、双语根 PLAN 和双语任务索引。git diff HEAD --check 通过。

## 必须返工

**AC04 失败。** 生产前端以合成管理员身份打开质量列表，新增任务号 `QA-DRAFT-401` 后单击保存。合成 API 对唯一一次 POST 返回 HTTP 401。Chrome 导航到 `/login`，原弹窗销毁，localStorage 和 sessionStorage 均无该任务号。正常重新登录也没有草稿恢复入口。规格 §3 要求权限错误和其他保存失败时保留草稿。观察到的失败属于身份在表单打开后过期的正常交互路径。

`frontend-js/src/app/quality/api/index.js` 的 createQualityResult 使用全局 request。`frontend-js/src/utils/request.js` 的 401 分支清 token 并执行整页导航。suppressErrorMessage 仅控制消息展示。QualityList.vue 的 identity 和 draft 仅在组件内存中。现有组件测试替换了 API facade，无法观察此导航。其他使用相同真实 HTTP 客户端的质量查询、编辑、字段配置和 SPC 请求也经过该拦截器。本轮失败判定对应人工新增。交 Development 在批准范围内保留身份校验，并验证登录过期后可恢复原草稿、重读后由用户决定是否再次提交。

## 验收记录

| 标准 | 核验结果 |
| --- | --- |
| AC01 | 通过。定向 ASGI 用例使用无计划与实绩依赖的 fixture，人工新增返回 201 和成功信封，读回一致。 |
| AC02 | 通过。服务端字段校验及客户端专项覆盖 hidden/editable、四种类型、0、false、空文本、未触及字段及配置变化，非法写入具备原子性。 |
| AC03 | 通过。专用 MySQL 8.4.6 实际运行，同号人工并发与人工／公共竞争用例通过，既有值和新值按事务顺序读回。 |
| AC04 | 失败。服务端角色、直接字段写权限和结果不明重读用例通过。浏览器 401 丢失草稿，见上。 |
| AC05 | 通过。专项检查 8 个旧 method/path，SPC 及旧模型继续可用，MySQL 合成旧数据保留。 |
| AC06 | 通过。隐藏 quality.control 仍为可授权组件叶子；组件按 QualityList 命名导航并再次经过目标守卫，未消费旧 ID 或旧列表 query。对照开发浏览器主管／操作员深链记录，本轮独立检查为源码及模块测试。 |
| AC07 | 布局及遮罩通过。合成管理员、30 个可编辑字段，四种 PC/平板横屏浅深主题组合均能滚动正文并到达页脚，四次遮罩关闭共零次写入。失败反馈中 401 分支随页面销毁，见 AC04。 |
| AC08 | 通过。发布合同与运行时比较测试通过；对 HEAD 四个公共路径的整个 OpenAPI 对象逐一比较，全相等。现有部分更新及并发保留字段验证通过。 |
| AC09 | 通过。候选没有模型、迁移或私有配置改动。本轮所有写入测试使用合成环境。部署前外部旧调用方、日志、历史数据处置和现场切换仍待部署方核实。 |

## 命令、环境与限制

- macOS 正式源码目录，在 backend 使用已有 uv 锁定环境。`uv run --no-sync pytest -q --basetemp=<QA目录>/sqlite -p no:cacheprovider tests/test_quality_results.py tests/test_quality_revision_guards.py tests/test_business_module_permissions.py`，退出 0，12 passed。设置 BACKEND_MOCK_ENABLED=False、MYSQL_HOST=127.0.0.1、MYSQL_PORT=1。
- 从协调者的 0600 临时文件加载隔离 fixture，`uv run --no-sync pytest -q --basetemp=<QA目录>/mysql -p no:cacheprovider tests_mysql/test_quality_results_mysql.py`，退出 0，1 passed in 4.50s。脚本在写入前检查 loopback 13412 的 UUID、空 schema、账户、上海时差和 MySQL 8.4 版本。多情境历史整合脚本没有独立运行。
- frontend-js 中 `node --test tests/module-registry/quality-results.test.mjs` 5/5；`pnpm check:modules` 和 `pnpm build --outDir <QA目录>/dist --emptyOutDir` 均退出 0。全量 `node --test tests/module-registry/*.test.mjs` 112 通过、3 失败，分别是角色路由菜单、Core 路由标识、模块顺序断言，与 Development 的 HEAD 对照同名。
- Playwright + Chrome Headless，生产构建、匿名本机静态端口、独立上下文、拦截全部 API 使用合成响应。通过 node 标准输入运行浏览器断言并退出 0。1440×900 两种主题正文可视/内容高 750/1424，页脚底部 887；1024×768 两种主题对应 618/1424 和 755（CSS px）。模拟 401 后最终 URL 为 /login，POST 次数 1，草稿存储检查 false。未访问真实 8000 或用户浏览器。结论限于本次构建和模拟视口。
- 实施问题退回 Development；修复后需要新交接和 fresh-context 复核。Human Owner 最终验收待定。

## 临时资源

已关闭测试 Chrome 及临时 HTTP 服务，已回收 QA 自有目录 /private/tmp/quality002-independent-verify（构建、缓存、SQLite）。协调者已确认回收 13412 fixture 与其凭据目录。无待清理的本次 QA 自有资源。

## 第二轮独立验证 · QA2

**qa_passed。** F01 关闭。AC04 的登录过期和 AC07 的失败反馈经本轮生产客户端复测通过。连同首轮未受影响的结果，AC01–AC09 满足本修订标准。交 Human Owner 最终验收。

- 正式工作树 HEAD `7f654ac`，spec 摘要与首轮相同。第二次 tasks.md SHA-256 为 `a83ffc3268bd6268fce471a04477929e11c3b3421cc9c4edad085c8f0f7f808a`，QA1 清单原始摘要为 `725ba199cc3f536421217ef02845f05650bd0df23d21921bae4a5486ad55e50d`。以 Python hashlib 逐项校验 §4，应用 §7 的五处覆盖，36/36 文件内容或删除状态吻合。`git diff HEAD --check` 退出 0。
- macOS，frontend-js 正式源码，`VITE_FRONTEND_MOCK_ENABLED=false`、`VITE_API_BASE_URL=/api/v1`、主管和操作员使用合成空授权数组。`pnpm build --outDir <QA2目录>/dist --emptyOutDir`、`pnpm check:modules`、`node --test tests/module-registry/quality-results.test.mjs` 全部退出 0，质量专项 5/5；生产构建有既有分包体积提示。
- 通过 Node 标准输入运行独立 Playwright 断言。Chrome Headless 158.0.8127.37 新上下文拦截全部请求，静态文件来自上述构建，HTTP 状态和数据由合成端点返回。沙箱首次启动 Chrome 被阻止，获准后运行。首次合成字段缺少正式合同的 labels 对象导致输入定位超时，修正 fixture 后完整运行退出 0。
- 合成管理员在质量列表录入任务号 `QA2-F01-EXPIRED`、目标和一项文本。首次点击保存只产生一个 POST，401 后仍在同一 URL，页面文档加载总数为 1；可见提示要求在另一个标签页重新登录并核对任务号。三个输入逐项保留，localStorage 和 sessionStorage 均无三个草稿值。
- 同源第二标签页写入模拟重新登录的新 token 并关闭。逐次手动点击保存，依次获得 409、503、201。捕获的四个请求头按顺序使用旧、新、新、新 Bearer，四个请求体都与原输入相等。每次失败提示出现后各等待 600 ms，POST 次数未增加。409 显示重复提示，503 提示按任务号查询核对，两个状态均保留全部输入。201 关闭弹窗，列表额外读取一次并显示上述任务号。随后分别点击取消和遮罩，额外 POST 共 0 次。
- 首轮后端、SQLite／MySQL 测试、合同、路由和布局证据继续适用。五处变更集中在新增请求、失败文案和专项测试；后端及测试摘要与首轮完全一致。本轮未重跑后端、已回收的 MySQL fixture、全量模块或四种主题尺寸矩阵；既有三项模块断言和未运行的多情境历史整合脚本见首轮记录。验证使用合成登录态，未接触真实服务、用户标签页或 8000／3307。

### QA2 资源收尾

独立 Chrome 已关闭，已回收自有目录 `/private/tmp/quality002-qa2.3i8Vf5XI`（构建和日志）。无待清理的 QA2 临时资源。

## Human Owner 最终验收

2026-11-24（Asia/Shanghai），Human Owner 明确确认「验收通过 ARCH-QUALITY-001 r2 和 ARCH-QUALITY-002 r1」。本清单据此登记 ARCH-QUALITY-002 r1 为 `owner_accepted`。

据 Human Owner 手工验证反馈，在 dev 环境通过质量列表新增 `TEST-P-01`，随后通过 Swagger 调用公共 POST 上报，并通过公共 GET 读回。响应中 `defectCount` 为 7，包含报告 URL，`targetKey` 为 null。此次手工反馈覆盖 UI 创建及公共接口上报、读回。刷新后列表的浏览器观察见上文 QA2 合成环境记录。

本次仅登记验收，无复测或数据写入。无临时资源。
