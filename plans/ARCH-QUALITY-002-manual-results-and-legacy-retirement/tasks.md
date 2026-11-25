Task ID: ARCH-QUALITY-002
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-11-24 Asia/Shanghai
Updated: 2026-11-24 Asia/Shanghai
Handoff: 正式工作树开发自检完成，交 fresh-context Verification

# 质量结果人工新增与旧检验退役 · 开发交接

## 1. 批准与候选

Human Owner 明确批准「批准 ARCH-QUALITY-002 r1，开始开发」。精确规格 [spec.md](spec.md) SHA-256 为 `9c15350c296bdcf46ba94186b53523a3c5dad5d865b2d9e8cc15107964cc8673`。候选在正式工作树，基线 HEAD `7f654ac`，实施未提交。PM 修改规格批准状态，协调者同步 PLAN 和目录索引，这些文档变化不属于 Development 实现清单。

按 backend-arch、frontend-ui、i18n-workflow 和 code-document-indexer 实施。承接现有项目工具链和锁文件。

## 2. 实际交付

- 私有 `POST /api/v1/quality/results` 使用登录和质量权限。管理员、主管、操作员可创建。成功返回 HTTP 201 与现有成功信封 `code: 200`。事务先锁本地配置，使用现有输入校验和唯一键写入。一条任务号重复时返回 `quality.task_no_conflict`，已有行保持原值。提交回执不明确时返回 `quality.commit_unknown`，调用者可按任务号重读核对。
- 质量列表新增紧凑弹窗，任务号必填，目标可选，启用且允许编辑的字段可以录入。隐藏但可编辑的字段可填。只发送已触及值，保留空字符串、0 和 false，允许仅建任务号。错误保留草稿，提交时防双击，遮罩点击和取消都不会提交。列表刷新沿用筛选条件。
- 旧检验列表、表单、Facade、Mock、旧检验与缺陷 HTTP 入口已从正常入口移除。保留原 `quality.control` 隐藏叶子并跳到质量列表，目标继续通过现有权限守卫。旧 `view=legacy` 查询进入当前列表。现有包级导出保留空 `defect_router` 作为导入兼容，manifest 不注册它。
- 复用旧表和 ORM metadata，保留 SPC 路由、旧表历史数据与公共质量合同。四个公共集成操作的 OpenAPI 路径对象逐项与基线相同。新增私有 API 更新了精确操作、返回模型、错误枚举和合成请求示例。

## 3. 开发自检

| 检查 | 命令与结果 |
| --- | --- |
| 后端 HTTP、SQLite、权限、现有迁移版本防护 | 在 `backend/` 用 `UV_CACHE_DIR` 指向任务临时目录，设置 `PYTHONDONTWRITEBYTECODE=1 BACKEND_MOCK_ENABLED=False MYSQL_HOST=127.0.0.1 MYSQL_PORT=1`，运行 `uv run --no-sync pytest -q --basetemp=<任务临时目录>/pytest -p no:cacheprovider tests/test_quality_results.py tests/test_quality_revision_guards.py tests/test_business_module_permissions.py`。退出 0，12 通过。覆盖严格字段、HTTP 201/409、提交结果未知与重读、权限、并发、八个旧 method/path 404，SPC 与旧数据保留、OpenAPI/示例实测。 |
| 隔离 MySQL 8.4.6 | 由协调者提供明确确认的 loopback 13411、全新 `arch_quality_fixture_13411`、独立账户和 UUID 匹配。加载权限为 0600 的临时环境文件运行 `uv run --no-sync pytest -q --basetemp=<任务临时目录>/mysql -p no:cacheprovider tests_mysql/test_quality_results_mysql.py`。退出 0，1 通过。两个公共并发写保留不同字段，人工同任务号并发一成功一冲突，人工与公共竞争无重复行、无未提交字段丢失，旧检验、缺陷和 SPC 三表合成数据完整保留。 |
| 前端专项 | 在 `frontend-js/` 运行 `node --test tests/module-registry/quality-results.test.mjs`。退出 0，5 通过。覆盖四种输入、重复请求保护、草稿保留、保留筛选语义、旧视图替换、双语键一致。 |
| 模块合同和生产构建 | `pnpm check:modules` 与 `pnpm build --outDir <任务临时目录>/dist --emptyOutDir` 均退出 0。构建出现 Vite 的既有大分包提醒。浏览器构建使用合成页面授权，未加载私人配置凭据。 |
| 前端全量模块 | `pnpm test:modules` 退出 1。112 通过、3 失败。对 `git archive HEAD frontend-js` 的基线临时副本运行 `node --test tests/module-registry/*.test.mjs` 退出 1，111 通过、相同三项失败，涉及既有 Monitor 路由位置与模块排列断言。当前范围无回归。 |
| 浏览器 | Chrome Headless，Playwright CLI 隔离会话 `quality002dev`，仅任务本机静态端口 14962。通过 `open --browser=chrome about:blank`、`run-code --filename=browser.js` 执行合成 API 检查。退出 0。PC 1440 × 900 与平板横屏 1024 × 768 的浅、深主题共四种组合均确认标题 16px、正文独立滚动、页脚可达、遮罩取消不触发 HTTP 写入。合成 409 和 503 均保留草稿，503 提示按任务号核对且未自动重试，合成 201 关闭弹窗并刷新。主管旧链接跳新列表，操作员仅有旧页 grant 时经目标权限守卫回到计划列表。动画仅在几何测量时关闭。 |
| 静态审核 | `git diff --check`、改动 Python 文件 AST 解析、12 处新增或修改的相对链接、四个公共 OpenAPI operation 对象基线比较均完成，无失败。 |

历史质量测试 fixture 使用精确历史修订及其前驱，源仓当前 Alembic head 为 `a1c307f8d2e4`。本实现没有创建迁移或改 schema。MySQL 业务模块整合历史脚本中更新了旧接口断言，该独立多情境脚本未运行，其专用授权 fixture 与本次质量 fixture 不同。旧接口退役、旧数据保护和新接口已由上述定向检查覆盖。

## 4. 精确文件清单

以下摘要覆盖正式工作树的实施及测试文件。删除标识指对应路径已不存在。

| 状态 | 路径 | SHA-256 |
| --- | --- | --- |
| M | `CODE_INDEX.md` | `649f1996caa0f35604ffad0204539cd5259c74de5861ce2954fa40b37562d90a` |
| M | `backend/README.md` | `ada969d2416edc2c061504ea577df8f03739d2465b7fe10b4e245741524043b5` |
| M | `backend/README.zh-CN.md` | `5a5dc18a10b9f9a75d7217c8d6640afdabf2dc17d2f15e5b6fb9bb90a9b33cd0` |
| M | `backend/app/quality/api/results.py` | `7c16df2fe34cdc68a0f4a6075b37fdfe7c9dd46b6b4586679c27657264982382` |
| M | `backend/app/quality/api/routes.py` | `ab0b2b5d41b91f0555532ffa2e1ec96e354d1a8308fc6a0b667fbfb9b16cd8e6` |
| M | `backend/app/quality/crud/async_quality.py` | `7a479ee90f41030a6d3cedad2f6d1a60656a8c69e7befb05f5b3cef215c4019f` |
| M | `backend/app/quality/domain.py` | `cbed22ff777827f7b96211af00349ae5f8a32c3a03cb12c71d4331f0091fca82` |
| M | `backend/app/quality/manifest.py` | `7866976eaadd4375b4833a0da39b73e9e56185bbba49695d7aa23cd03b980a9d` |
| M | `backend/app/quality/schemas/__init__.py` | `4cf566864bcd5f6caaa0a8f2797d83e2aedc2dceb3fc166775ff33a4fa0a2011` |
| D | `backend/app/quality/schemas/quality_in.py` | — |
| M | `backend/app/quality/schemas/quality_out.py` | `61d1bd54a53ee7f6f1cd7eb69740d5ed07648ae04633cb5601d7a4c047573582` |
| M | `backend/app/quality/schemas/results.py` | `114acc6672161795187ccc595628c626bc4f6f7895850edf18b4f10fc4411b9c` |
| M | `backend/app/quality/services/async_quality.py` | `96a1a5a9182d1f330cba8c2aa30e046ffd572bfef4bf2ce6c8b114bc7110f8fe` |
| M | `backend/app/quality/services/results.py` | `64bd9c4ca775ff7300324d846c3190d15bed5785a82e6a55a641ac145f62585c` |
| M | `backend/tests/test_business_module_permissions.py` | `de0097285cf3266811e77a7cfd25e19b6bedffa04dceb1636a2712ef55f85671` |
| M | `backend/tests/test_quality_results.py` | `fca1b9f351675e1be1dceace6f0ba38892b6440c8db770ea116c0c4fd70ae907` |
| M | `backend/tests_mysql/test_business_module_reintegration.py` | `97d9b3151ffd5266cb337c76186bcd03d77a40749e3f4fa33f1adcb968baf41b` |
| M | `backend/tests_mysql/test_quality_results_mysql.py` | `02ddde20f7bd2c59ede997bd1f095b970a1c8e989ba23938659cb5fe96835b9f` |
| M | `contracts/published/http-api/quality-results-v1/README.md` | `0b2c0281548ecc0b418604c79bed9bad7fede81ae290c970e161c5511b9dfcf6` |
| M | `contracts/published/http-api/quality-results-v1/README.zh-CN.md` | `6a19491b0abeab55c6da8da1571aac5213010154965cb3ec9d90e933257a997b` |
| M | `contracts/published/http-api/quality-results-v1/examples/requests.json` | `ed016349f462539d39c0085d2b904ecf1f002b784c8f51effb398ce28198bf48` |
| M | `contracts/published/http-api/quality-results-v1/openapi.json` | `b80f2f8aadf681a299c81c76176a517527449573147b0badee2115bc068116a2` |
| M | `frontend-js/README.md` | `3e72fed92e383d806ff08532f0948b1e1434065fab4607a726125f3f296b0d99` |
| M | `frontend-js/README.zh-CN.md` | `0188099519dfbb800f1b9a02ef8d824141a2cd31b3ea7891de02e1dd989c7064` |
| D | `frontend-js/src/app/performance/views/quality/index.vue` | — |
| M | `frontend-js/src/app/quality/api/index.js` | `8839abb3fd17ef27bd0044e8c5c7b06d2156f9cf94d0f43d268b73d2f7f78a1b` |
| M | `frontend-js/src/app/quality/api/mock.js` | `b8f64bc6342b50f71d4ae38d4f423f8707a8f9192b510f34bd2333f174e0ca68` |
| M | `frontend-js/src/app/quality/locales/en-US.json` | `73669edf45cbdb99e0db9ca9bac7dc7f88770620976093ffa503efef17823ff6` |
| M | `frontend-js/src/app/quality/locales/zh-CN.json` | `d1beb6154bcc2099676c01e800e0773b9557a31d7bd0b1aeafc5c7047b123b5f` |
| M | `frontend-js/src/app/quality/manifest.js` | `a8e344d5a619e28d7899cd67641ab1d2684dae7e11bfd9c9b873035b66d463f3` |
| M | `frontend-js/src/app/quality/views/control/index.vue` | `5d2bf151aea3ac788a2ac641abe79b99b941dedf73b72dba3e6334a511f06107` |
| D | `frontend-js/src/app/quality/views/list/index.vue` | — |
| M | `frontend-js/src/app/quality/views/results/QualityList.vue` | `5da7813cfc6ecf310f8d5689d1e7982153c8811b1aaac9feb1475a9658038950` |
| M | `frontend-js/src/app/quality/views/results/index.vue` | `402cdf5142c2f9303fdcddc95fd50bcb3bf78b6e2567f0a3388508c54ab47f6e` |
| M | `frontend-js/tests/module-registry/quality-results.test.mjs` | `7865f25899467bb38adf659a5d3b9cd5bf85f4d97e0cb54f0cfaf36b76307f07` |
| M | `frontend-js/tests/module-registry/registry.test.mjs` | `86b2677c3738e5bbddd631724e083862d85b0c24bfb09d16359941e848c0a33d` |


## 5. Verification 交接和环境边界

从正式工作树按第 4 节复核文件。独立核验包括实际接口与合同、另一套明确隔离的 MySQL 合成目标、桌面和平板横屏浏览器回归，以及旧 ACL 兼容。当前运行的真实服务、数据库和私人配置保持原样。部署前仍须核对外部旧接口调用方、访问日志及旧记录处置。

## 6. 临时资源收尾

- Playwright 隔离会话已关闭并清理会话数据，14962 静态服务已退出。Development 已回收 `/private/tmp/arch-quality-002-dev-0BdFg5Wy`，其中含合成 SQLite、构建、基线副本、浏览器脚本和日志。验收事实已保存在本文件。
- 13411 隔离 MySQL fixture 已结束使用，容器和临时凭据由协调者回收。Verification 独立 fixture 由协调者安排。


## 7. F01 返工与第二次开发交接

Verification 第一轮记录了 AC04 的 HTTP 401 失去草稿。按批准 r1 原范围修复，保留首轮证据。新增操作使用独立的 Axios 调用，复用现有 API 基址、超时和 Bearer 头，保留真实 HTTP 状态给当前弹窗处理。共享请求拦截器、全局登录行为和服务端鉴权继续沿用。新增接口返回 401 时，弹窗保留任务号和字段草稿，提示在另一个标签页登录并核对任务号。草稿只在组件内存，刷新或离开不会写入浏览器存储。用户主动再次提交时读取当时的凭据，无自动重试。

### 返工验证

- 在 `frontend-js/` 运行 `node --test tests/module-registry/quality-results.test.mjs`，退出 0，5 通过。新增一个 401 回归断言，验证提示、草稿和发送次数。运行 `pnpm check:modules` 及合成授权的 `pnpm build --outDir <返工临时目录>/dist --emptyOutDir`，均退出 0。Vite 继续提示既有大分包。
- 使用非 mock 的正式生产构建，`VITE_API_BASE_URL=/api/v1`、`VITE_FRONTEND_MOCK_ENABLED=false`。Playwright CLI Chrome Headless 隔离会话 `quality002rework`，本机静态端口 14964，`open --browser=chrome about:blank` 后 `run-code --filename=browser.js`，退出 0。已测试实际前端 facade 发送首个 Bearer 和 HTTP 401，保持质量列表 URL、弹窗、任务号和字段值，只有一次 POST，localStorage/sessionStorage 均无草稿。另一个同源标签页写入模拟重新登录后的凭据，下一次用户显式提交使用更新后的 Bearer。随后模拟 409 和 503 仍保留草稿，模拟 201 关闭并刷新列表。四个 PC/平板横屏、浅／深主题组合里点击遮罩均关闭且零写入。
- `git diff --check` 通过。后端、API 合同、数据库、权限与迁移源码不属于此次返工。初次开发交接的后端与 MySQL 证据见第 3 节。

### 第二次 developer_handoff

以正式工作树和本节摘要为准。第 4 节保留第一次候选的检验记录。以下 5 项摘要覆盖同名路径，其余 31 项摘要或删除状态与第一次候选一致。

| 状态 | 路径 | SHA-256 |
| --- | --- | --- |
| M | `frontend-js/src/app/quality/api/index.js` | `9498606974531c62c21475eefeba853ab724537080892210920340a5833899f8` |
| M | `frontend-js/src/app/quality/locales/en-US.json` | `fdd94c6e52eb9fe40318be0590396c179c99b9b0af944ed9a5d7912e59c6b65d` |
| M | `frontend-js/src/app/quality/locales/zh-CN.json` | `75fbc1843b1d53ad3cdbcec07bee552e472a414fcfed7e34cca20d1a1682584b` |
| M | `frontend-js/src/app/quality/views/results/QualityList.vue` | `efcf034891e6e53693ac6dcc92acecf39e546484ae87bf3dacd1f40bd2ed28a4` |
| M | `frontend-js/tests/module-registry/quality-results.test.mjs` | `81e8897378ed02de7538705a159479bbc13615fe0710bd17dc0ed5656df5d2c5` |

### 返工临时资源

已关闭独立 Chrome 会话并清理会话数据，已停止 14964 静态服务。已回收自有 `/private/tmp/arch-quality-002-rework-3b78Ld4F`，包含临时构建和测试脚本日志。无待清理的本次返工临时资源。
