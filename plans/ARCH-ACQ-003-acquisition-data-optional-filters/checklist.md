Task ID: ARCH-ACQ-003
Revision: r2
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner 已验收精确 r2 候选和指定 dev 交付。新版 provider 合同交接至 DAA-010，后续工作由该任务记录。
Workflow Mode: STD
Execution Mode: agent_team_same_session

# QA1 独立验证

2026-11-11 Asia/Shanghai。`/root/acq003_r2_qa` 以 `verification` 角色在 fresh context 接收确切交接。读取根 `AGENTS.md`、README/PLAN、最近目录文档、项目 Verification TOML 与 canonical workflow。按 `project-governance`、`backend-arch`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer` 复核。核对 [批准规格](spec.md) SHA-256 `3133b706f2b16ede3ef675399ea138e626b77bdeef8459820369970371e2e5c1` 与 [Development handoff](tasks.md) SHA-256 `3ce70e0077d7b8496c8a8d6391541da5c8ec2850dc030b798fd85de11f009130`。

正式未提交工作树基于 `bcafa89fa31bdf62329bced89baebc193323a739`。独立校验 40 个批准路径的交付清单，正式与候选全部同字节。33 个变更文件的原摘要与切换前副本匹配，7 个新增文件与允许路径匹配。核对十个旧迁移及原三份 v2 合同的 13 个冻结摘要，全部一致。以切换前副本生成任务 diff 并复核修改面，BE-010 公共 helper 仅追加后继版本。项目 diff 空白检查通过。检查任务改动文档、规格、交接及索引中的 188 个本地相对路径，全部存在。计划行仍显示较早的 `owner_approved` 进度，由协调者按本记录机械同步。[交付清单](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/delivery-manifest.json) · [冻结摘要](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/frozen-baseline.json)

## 验收矩阵

| 条目 | 结果 | 独立证据 |
| --- | --- | --- |
| AC01 来源与鉴权 | 通过 | 真实 MySQL ASGI DAA/external 分别写入，读到各自来源。错误、吊销凭据为 401，实例冒用为 403，吊销后授权读取仍成功。定向 ASGI 与配置测试覆盖错误 PLC、DB、代次、重复活跃来源、未登记实例和正文伪造 `sourceType`。 |
| AC02 写入与保留 | 通过 | 真实 MySQL 中按原始字节重复确认为 200 `duplicate`，省略改 null 为 409，DAA 缺元数据拒绝，外部可省略或显式 null。另在前驱 `qa_guard` 写入带原字节 SHA-256 的合成旧行，升级后原字节重试为 200 `duplicate`，加一个尾空格为 409，旧行来源保持 NULL。清理 plan/apply 对账含可空元数据的预算，保留逐点序号水位。REAL 精度、迟到水位、到期和提交异常分别由真实样本与离线事务测试验证。 |
| AC03 迁移与恢复 | 通过 | 在四个 QA 独占 schema 从非空精确前驱复跑 6 项。两表原列摘要、唯一键、主键、索引、自增水位 100、其他表和退役状态一致。复现 RENAME 后与 ALTER 后的中断状态，缺失／错误证据拒绝，正确证据恢复。登记后重复升级成功且无迁移动作，downgrade 拒绝。错目标、混名、可见依赖、约 5 秒锁等待、离线和映射错键回滚实测通过，混列与授权覆盖另有定向离线检查。 |
| AC04 授权读取 | **失败，QA-F01** | 多 PLC、交叉 DB、supervisor／admin／空范围的 SQL 和 ASGI 验证覆盖先授权后计数及分页、精确点位大小写、字面 `%`／`_`／反斜线、源类型、可空历史及旧代次。正式 GET 复核了过滤、排序、普通超页、越权及精确点位 0／1 行。两个分页接口在更大的有效页码返回 503，详见下节。 |
| AC05 Web | 通过 | Chrome 157.0.8103.39 在独立构建上完成中文浅色 1280、英文深色 390 两页，以及英文 390 历史触摸。检查每次列表动作一次 GET、默认 50 条、实际翻页、DB 升序并集、PLC 清除保留有效 DB、切 PLC 清除失效 DB、长标识与布局、实时字面搜索、24 小时上海默认窗口、7 天及超限、详情来源实例。标题问号 24×24，hover、焦点和触摸可展开，Escape 关闭。前端模块测试覆盖迟到列表及详情响应、列宽偏好和页长。正式 5190 两页各一次首屏 GET，再各一次 PLC 筛选 GET。 |
| AC06 兼容与交付 | 通过 | 冻结文件与 40 个交付路径对账。已发布 r2 六条 OpenAPI 路径及对应 schema 与正式运行时逐项一致，独立运行候选合同测试验证请求 schema 和向量。同步真实目标检查通过，错 UUID、schema 或 revision 为 503，异步目标和无效旧 profile 由离线测试覆盖。BE-010 精确后继合成采用、旧证据失配拒绝，monitor、equipment、performance 实际为 disabled／unadopted／无采用文件。 |
| AC07 指定 dev | 通过，限定正常只读复核 | 验证同实例 MySQL 8.4.6、上海偏移 28800、`industrial_level_2_system`、精确后继 `4e6a8b0d2f14`。事实表各 2 行，原列摘要与切换前证据相符，历史自增 5，66 张其他应用表的当前 DDL SHA、行数与 checksum 和切换前一致。历史来源均为 NULL，当前来源登记 `external`。8000 正常只读、5190 两页及样本详情、来源和筛选通过。切换前备份及演练依据协调者留存证据复核，QA 独立对账当前只读状态。 |

## QA-F01 分页超界返回 503

R06 要求超页返回空项及本次总数。公开 OpenAPI 中 `page` 是下限 1 的整数。使用短期本地登录令牌，在 8000 对以下两个接口分别发 GET。历史请求同时携带当前时间前 24 小时的合法上海 `from` 与 `to`。

| 端点 | `page=1000000` | `page=1000000000000000000000000` |
| --- | --- | --- |
| `/api/v1/acquisition-data/latest/browse` | `200`，`items=[]`，`total=2`，`pageSize=50` | `503 plc_facts_v2.not_ready` |
| `/api/v1/acquisition-data/history` | `200`，`items=[]`，`total=2`，`pageSize=50` | `503 plc_facts_v2.not_ready` |

两条查询先得到授权总数，仍把 `(page - 1) * page_size` 传给 MySQL `OFFSET`。大页码的偏移超出 MySQL 可表示范围，异常走 `not_ready` 响应。请 Development 在有授权总数后处理任意超页，并为两条路径补可复现回归。修复后由新的 fresh-context QA 针对交付差异复验，覆盖普通分页、空授权与两个大页码请求。[实时分页 SQL](../../backend/app/plc_facts/crud/async_v2.py#L117) · [历史分页 SQL](../../backend/app/plc_facts/crud/async_v2.py#L127)

## 命令与环境

- 隔离候选以项目现有锁定环境执行，`uv 0.7.8`、Python `3.13.3`、`pnpm 11.11.0`、Node `22.19.0`。检查 `settings`、`app`、`database` 及 v2 API 模块均解析到候选，候选缺省合成 MySQL 端口为 1。`uv run --offline --frozen --no-sync python -m compileall -q app/plc_facts` 退出 0。
- `uv run --offline --frozen --no-sync python -m pytest -q -m no_db -p no:cacheprovider --basetemp=<QA 临时目录>/pytest-offline tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_acquisition_facts_migration.py tests/test_legacy_acquisition_retirement.py tests/test_mapping_migration.py tests/test_equipment_temperature_migration.py tests/test_business_integration_migration.py tests/test_business_integration_storage.py` 退出 0，142 passed、3 skipped。历史 BE-012 B 与 BE-003 固定旧源码两个跳过保留，第三项本次专属 MySQL 写读在下一条单独运行。
- `uv run --offline --frozen --no-sync python -m pytest -q --tb=short -p no:cacheprovider --basetemp=<QA 临时目录>/pytest-mysql tests_mysql/test_acquisition_facts_r2.py` 退出 0，6 passed。`ARCH_ACQ003_LIVE_READ_WRITE=ACQ003-ISOLATED` 与 `TEST_MYSQL_DATABASE=arch_acq003_qa_upgrade` 下同命令切换 basetemp 为 `pytest-live`，选择 `tests/test_acquisition_data_browse.py::test_mysql_authorized_ingest_browse_and_cleanup`，退出 0，1 passed。首次默认沙箱拦截 localhost TCP，未触达数据库，使用获批的限定本机通道重跑成功。
- QA 专属账号的 `SHOW GRANTS` 核对全局仅 `USAGE` 与四个 QA schema 授权，尝试连接业务 schema 得到 1044。由私有 0600 JSON 传入子进程，校验 MySQL 版本、UUID、端口、账号、schema、上海偏移及 ACK。额外以 `uv run --offline --frozen --no-sync python <QA 临时目录>/legacy_replay.py` 在 `qa_guard` 验证旧字节重试和代次切换，退出 0。临时 ASGI 夹具进程退出时 aiomysql 对已关闭事件循环输出析构提示，测试断言已完成。
- `pnpm_config_verify_deps_before_run=false pnpm check:modules` 和 `pnpm_config_verify_deps_before_run=false pnpm test:modules` 均退出 0，后者 55/55。构建首次缺候选显式角色数组，退出 1。用 `VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' VITE_FRONTEND_MOCK_ENABLED=false VITE_API_BASE_URL=/api/v1 pnpm_config_verify_deps_before_run=false pnpm build --outDir <QA 临时目录>/dist` 重跑退出 0，出现 Vite 产物目录及 chunk 大小提示。
- `node <QA 临时目录>/browser.cjs` 的独立构建浏览器夹具退出 0，五个组合分别发出 8、8、8、8、6 个列表请求，逐动作核对。正式 backend 以 `uv run --offline --frozen --no-sync python -u <QA 临时目录>/formal_read.py <QA 临时目录>/browser.cjs --actual` 运行，直接数据库会话显式只读，浏览器只放行采集 GET。首次浏览器夹具匹配范围误拦 Vite 源码，再次复跑误用了合成历史的来源预期。修正夹具后最终退出 0，两页分别 2 个列表 GET，无 pageerror，数据库、合同和 QA-F01 观察结果复现。令牌仅在本机进程内传递。

## 运行证据与交接

- 正式操作记录 SHA-256 `467b0202905364fbd9d9b3e85afc08e4cd11dfa66f1598ec3912bde1e4296164`，候选清单 `bbe014e50b62e1e19dabd5951b12a892102f4523b52eaa5263b3c62385af1094`，备份演练 `23a6e8f60e2697b41baff8e41c9c6fd14b94dda4739664d0a004082b3715e1e6`。独立读取正式仓外 profile，模式 0600，SHA-256 `a27955bfefe3c56b93ad2ba91e9277d53377294fffd5026b8b24def073449ed7`。原凭据摘要、来源范围和读范围相同，登记为 `external` 并采用新 revision。正式两表原列摘要分别为 `6fbd3a2d942dec2b11334890109a68745b8a80a4b1bf50d37c0b07a22935ea3b` 与 `d9e8990eb519c8e9a2e62cc5189ccb3c59355bcaab6014f0016efd3a99392c30`。本次没有业务库旧历史来源回填。 [操作记录](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/dev-operation.json) · [备份演练](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/dev-backup-rehearsal.json)
- 同实例隔离 DML、DDL 和清理只在 QA 专属 schema；已复验 MySQL 对超长 `external ` 的多余尾空格可先截断再检查，实际存值是 `external`，仓外登记和 HTTP 边界仍分别拒绝非法分类及正文 `sourceType`。旧严格历史读取者须接受 `groupId`、`configRevision` 和 `sourceType` 的 JSON null。当前结论覆盖获批 dev、公开候选与合成 schema，生产、现场、DAA/SMA 接线及历史独立任务验收仍待各自批准。
- QA 临时目录 `/private/tmp/arch-acq003-r2-qa-7iT8I5Rk` 的构建、脚本、diff 和合成截图供复查。独立 Chrome 与临时静态服务器已退出。私有候选前后证据、QA 专属账号及四库由根协调者保留给返工后的独立验证，并按验收和恢复依赖清点回收。业务 dev 的 8000 与 5190 继续服务，真实 profile 与备份留在既有私有位置。验证结论及复现输入已在本文件持久化。

QA1 verdict `qa_failed`，失败项为 AC04 的 QA-F01。无额外环境 blocker。Development 接收返工，Human Owner 最终验收待定。

# QA2 独立复验

2026-11-11 Asia/Shanghai。`/root/acq003_r2_qa2` 以 `verification` 角色在 fresh context 接收 Development 重新交接。读取根 `AGENTS.md`、README／PLAN、最近作用域文档、角色 TOML、canonical workflow 和完整 bundle，按 `project-governance`、`backend-arch` 核对返工表面。正式未提交工作树基于 `bcafa89fa31bdf62329bced89baebc193323a739`。规格 SHA-256 为 `3133b706f2b16ede3ef675399ea138e626b77bdeef8459820369970371e2e5c1`，重新交接 SHA-256 为 `3584f9ca5a4a3cda3b5b1257672af6cd50e1c77976f42098a44bb792019f49e5`。本节追加前 QA1 原记录 SHA-256 为 `496b901f3f455a2425b38eea64fae5c4b4399d41b3261340930beb7d22c1ef1e`，上方 QA1 正文、失败结论与证据完整保留。[批准规格](spec.md) · [Development 重新交接](tasks.md#qa1-返工与再次交接)

## 候选、改动与证据沿用

- 重新计算 QA1 清单 SHA-256 `bbe014e50b62e1e19dabd5951b12a892102f4523b52eaa5263b3c62385af1094` 和 QA2 清单 SHA-256 `6ff79de385309b86753d1c549626a503120fd177f315dc836bb6e52afa697a76`。QA2 候选内副本和持久清单逐字节一致。40 个路径的基线项相同，QA1 候选逐项匹配旧摘要，QA2 候选和正式工作树逐项匹配新摘要。两候选、正式工作树及冻结清单的 13 个摘要均一致。另对两个候选的后端、前端、合同相关源码、测试和锁文件逐项比较，768 对文件仅有下表两项不同。[QA1 清单](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/delivery-manifest.json) · [QA2 清单](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/delivery-manifest-qa2.json) · [冻结摘要](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/frozen-baseline.json)

| 文件 | QA1 SHA-256 | QA2 SHA-256 |
| --- | --- | --- |
| `backend/app/plc_facts/crud/async_v2.py` | `6f04c2bded73a61c76f011352316dbc61039a3c6a707ceac3eea50f67153da6c` | `89483004833e50bd72893645e81fa7e2161975a8c3af5c4ee0306039e082442b` |
| `backend/tests/test_acquisition_data_browse.py` | `03a46892f9fc457c4a85a760ad256d5376785dce92388b1e44cd6db7f58a5a23` | `79e605ad7eac8316619c50cec3ec207343972edae58c370a59eebe50618b19e4` |

- `diff -u` 确认唯一生产改动位于两条分页查询，先用原授权、来源、有效期及搜索／时间条件计数，再判断 `(page - 1) * page_size >= total`。超页与零计数直接返回 `total` 和空列表。正常页的筛选、排序和偏移计算保持原样。回归覆盖两条 CRUD、正常页、恰好越界、零计数、极大页以及两条 HTTP 响应的原页码、总数、页长和总页数。[实时查询](../../backend/app/plc_facts/crud/async_v2.py#L117) · [历史查询](../../backend/app/plc_facts/crud/async_v2.py#L130) · [分页回归](../../backend/tests/test_acquisition_data_browse.py#L431)

| 条目 | QA2 结果与证据 |
| --- | --- |
| AC01、AC02、AC03 | 通过。逐项核对写入与准入、清理、迁移和恢复的源码、夹具与合同摘要，沿用 QA1 独立 MySQL／ASGI 证据。 |
| AC04 | 通过。QA-F01 由本节新离线测试、空授权 ASGI 验证和指定 dev 的 28 次 GET 关闭。其余授权交集、字面搜索、精确点位、时间和旧代次证据沿用 QA1，重跑的后端定向测试再次覆盖相应离线场景。 |
| AC05 | 通过。Web 八文件摘要与 QA1 相同，沿用其 55 项模块测试、构建、独立 Chrome 与正式 5190 证据。QA2 在 8000 复验两页使用的首屏与后续分页响应。 |
| AC06 | 通过。沿用冻结合同、目标护栏和 BE-010 隔离采用的 QA1 证据。QA2 再次核对 13 个冻结摘要，并将 8000 OpenAPI 与新版合同的 6 条路径和 19 个 schema 逐项比对一致。 |
| AC07 | 通过，限指定 dev。沿用 QA1 的备份复核、原列及 66 张其他表对账和 5190 浏览器证据。QA2 另以只读事务核对同一服务器 UUID 摘要、MySQL 8.4.6、3307、`industrial_level_2_system`、上海偏移 28800 和 `4e6a8b0d2f14`。两张事实表各 2 行，历史 2 行的来源仍均为 NULL，仓外 profile 权限 0600、摘要与 QA1 和切换记录相符。8000 与 5190 监听进程的工作目录对应正式源码。 |

## 命令与运行结果

- 候选 `/private/tmp/arch-acq003-r2-candidate-qa2-92fLZKdv/backend`，macOS arm64、`uv 0.7.8`、Python `3.13.3`。清空继承的应用环境，设置候选 `PYTHONPATH`、测试变量和本机合成 MySQL 端口 1，核对 `settings`、`database`、v2 API 与 CRUD 均从候选导入，候选无运行 `.env`。`uv run --offline --frozen --no-sync python -m compileall -q app/plc_facts` 退出 0。
- `uv run --offline --frozen --no-sync python -m pytest -q -rs -m no_db -p no:cacheprovider --basetemp=<QA2 临时目录>/pytest-focused tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py` 退出 0，83 passed、2 skipped。跳过项为 BE-012 的固定旧 B runner，以及须启用任务专属真实 MySQL 的集成夹具，后者沿用 QA1 独立结果。
- 同一隔离环境运行 `uv run --offline --frozen --no-sync python <QA2 临时目录>/empty_scope.py`，退出 0。两接口对空授权各发送默认页、极大页、显式 DB 三次合成 ASGI GET。两种页码均为 200，`items=[]`、`total=0`、`totalPages=0`，各只执行含 `WHERE false` 的计数查询。显式 DB 均为 403。
- 正式 backend 工作目录执行 `uv run --offline --frozen --no-sync python -u <QA2 临时目录>/dev_paging_read.py`，退出 0。通过限定本机连接执行只读 MySQL 查询，短期登录令牌仅在进程内使用。对 `/api/v1/acquisition-data/latest/browse` 和 `/api/v1/acquisition-data/history` 各发 14 次 GET，历史携带最近 24 小时上海时间窗口。两条路径默认页均为 200、2 项、`total=2`、`pageSize=50`。`page=2&pageSize=1` 均返回排序后的第 2 项和 `total=2`，第 3 页为空。`page=1000000` 与 `page=1000000000000000000000000` 均为 200、0 项、`total=2`、`pageSize=50`、`totalPages=1`，且回显请求的页码。PLC／DB 单项与组合筛选保留正确总数和顺序，组合筛选的极大页亦为 200、空项、`total=2`。显式越权与 `page=0` 分别为 403、422。`GET /openapi.json` 合同复核另外通过。[指定 dev 切换证据](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/dev-operation.json) · [Development 分页复验对照](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/dev-http-qa2.json)
- `git diff --check` 与 bundle 本地相对链接检查通过。QA2 唯一仓库写入为本 checklist。

## Verdict 与交接

`qa_passed`。AC01–AC07 通过，QA-F01 关闭，无环境 blocker。QA2 的新运行证据为定向后端复验及指定 dev 只读观察。生产、现场、DAA／SMA 接线及既有独立任务的验收仍由各任务处理。

独立脚本和临时输出在 `/private/tmp/arch-acq003-r2-qa2-verify-UtsbWpDJ`，复现输入、结果和候选摘要已记录在本文件。QA2 无存续测试进程，对 8 个专属 schema 与 2 个专属账号无后续验证依赖，资源交协调者按规格及实际依赖处理。指定 dev 的 8000／5190 和既有私有 profile、恢复备份仍用于正常服务或恢复。精确 r2 验证结果交 Human Owner 最终验收。

## Human Owner 最终验收

2026-11-11 Asia/Shanghai，Human Owner 在本会话明确表示「验收 ARCH-ACQ-003 r2，把状态更新一下。」`/root/acq003_r2_qa2` 以原 Verification 角色代录决定。验收对应 QA2 核对的正式工作树 40 文件交付清单，SHA-256 `6ff79de385309b86753d1c549626a503120fd177f315dc836bb6e52afa697a76`。验收前 QA2 清单 SHA-256 为 `f88c5a5c102a5c271b62ef9398a1e576183bf8abf7a7dab1a94903d3b4f113a2`。[QA2 正式交付清单](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/delivery-manifest-qa2.json)

`owner_accepted` 覆盖获批 r2 的新版 PLC 事实 provider 与合同，以及已验证的指定 dev 交付。该 dev 使用 3307 `industrial_level_2_system`、Alembic `4e6a8b0d2f14`、8000 API 和 5190 Web。Human Owner 将带新版上报合同前往「主-DAA」会话继续 DAA-010。DAA 上传、补传、确认及其联调和验收证据归 DAA-010。[新版上报合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md) · [DAA-010 规格](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/spec.md)
