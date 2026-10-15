Task ID: ARCH-BE-004
Revision: r2
Workflow Mode: STD
Execution Mode: agent_team_same_session
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: r2 F-001返工完成；交主协调启动新的 fresh-context 命名 Verification，保留首轮qa_failed历史；不表示 QA 或 Human Owner 验收
Updated: 2026-10-13

# 批准与工作树基线

已完整消费根 AGENTS、canonical workflow、根及触达 backend/frontend-js/app/auxiliary README/PLAN pair、获批 spec（r2 为当前合同，r1 为历史）和相关实现/测试。spec 在第一次实现写入前为 `owner_approved`，批准由主协调转递 Human Owner 原话“批准 ARCH-BE-004 r2，固定上海时区，暂不允许未来时间，进入 dev”。本角色实际为命名 Development；不记录模型容量重试为已实施证据，不授予 QA 或 Human Owner 验收。

使用 backend-arch 及 RESPONSE_CONTRACT/LAYERS/DATABASE_AND_MIGRATIONS/AUTH_SECURITY/OPERATIONS_TESTING，frontend-ui FRAMEWORK/DESIGN、i18n-workflow、code-document-indexer。没有加载不适用profile或修改skills。源码基线 HEAD `363b297bffe65e020108f5504766b4fb1ec3b381`，工作树原有大量未提交/未跟踪修改；BE002 r3 owner_accepted 是已验收基线。未创建commit、分支或worktree。

任务资源根 `/private/tmp/arch-be004-r2-dev`。首次写入前保存 `baseline-hashes.json`（801个非env源码/文档）、`baseline/`副本、`baseline-status.txt` 与 `baseline.diff`；没有复制或输出真实env。保护BE002完整bundle、原EnergyPrice Model、两旧migration，BE003草案、ARCH-MULTI-001和ROADMAP pair、其他既有dirty。主协调负责12机械PLAN/catalog索引，本角色负责允许的CODE_INDEX实现入口。

# 已实施增量

- 新 energy_price_hours Model/独立后继 b8d0f2a4c6e8，down_revision a6c8e0f2b4d6；旧表/旧Model/旧revision原样保留。唯一hour_start键、三价格/四备注约束、observed_at/hour_start及UTC DATETIME(6)/UTC_TIMESTAMP(6)。
- 保留恰好三个API；POST observedAt可省略/null，API只取一次now兜底/拒未来；显式offset ISO校验、原始JSON小数精度、read/manage独立guard保留。GET date严格单值合法日期，分页壳与filtered total；current按observed_at<=now、observed_at DESC/id DESC。
- async Service控制commit/rollback；MySQL ON DUPLICATE KEY UPDATE整组覆盖，不覆盖id/hour_start/created_at；在事务锁内读取本次完整结果并在commit前验证/序列化。只记录actor/id/result，不记录价格或备注正文。
- 页面只读三卡与刷新；历史date默认Shanghai今天、page1size24、无分页；标准新增弹窗完整三价格/四备注、picker初始空/不可手输可清空。保存锁快照/重复提交/取消关闭，失败保留；成功关闭、切响应日期并分别GET current/history，独立请求序列防迟到/卸载回写。仅从facade导入，三mock同名保持完整字段与明显marker，双语keys对称。
- 模块README pair明确小时合同、旧数据归并SQL（预检/人工gate/默认ROLLBACK/旧行校验和与所选id核对）、回退损失与运行gate。后端README pair与CODE_INDEX同步真实入口。
- 更新原回归测试来消费小时合同；增加固定钟/offset/date/未来/SQL/upsert/事务/合成归并与真实编译SFC异步行为测试。没有把fake session称作MySQL并发证明。

# 首轮精确修改文件（相对首次写入基线；F001最终指纹见末节）

- `backend/app/auxiliary/models/energy_price_hour.py` — SHA256 `0081b4a8c70db37280479def4eab7750994dcf60e359c0e5cf86876c97d1a6e8`
- `backend/app/auxiliary/models/__init__.py` — SHA256 `52a1ab6f6ad28e3a6e70fd22c04bd21e8778b66fb9e72fff9e200c88dc48dadd`
- `backend/alembic/versions/20261013_1600_b8d0f2a4c6e8_add_energy_price_hours.py` — SHA256 `7efeba1aef3270a1f7c51b6b7bbbf2af670e49ac2ffdca342e978a03ce573d1a`
- `backend/app/auxiliary/api/energy_price.py` — SHA256 `7e6d8560cef66833f1076298f9322ef15dd8fad6ca19f9f87702ff7283de36c9`
- `backend/app/auxiliary/schemas/energy_price.py` — SHA256 `9979493972c31c57e6b3ea8668e37ce07477995ce65199a59a624aa654c5d582`
- `backend/app/auxiliary/schemas/__init__.py` — SHA256 `687b26eb0c85236ac02e5a469e6996b1ed0f7bd33f48671c8397b9b870db2bf9`
- `backend/app/auxiliary/services/async_energy_price.py` — SHA256 `86b9797a2653ac00f67b0a071e86fe80764c786ab986215238553180571ea01d`
- `backend/app/auxiliary/crud/async_energy_price.py` — SHA256 `d7b1bca17e86088eb1700749ba77aac04da883d2cd123c6fd5f8d29ee3946615`
- `frontend-js/src/app/auxiliary/views/price/index.vue` — SHA256 `15313ec0ebbb2f60145a4b41464b0138c6df90eea0f526a78b56d16080a04023`
- `frontend-js/src/app/auxiliary/api/index.js` — SHA256 `db28b5c6b77a89cd0819e2d53b78f270486595b41ec4b357ba8bef9665668c44`
- `frontend-js/src/app/auxiliary/api/mock.js` — SHA256 `e2bb55ca054bb0ec83398bd3713c87a8d3485d79d73b2ed5cb39648f41b092e0`
- `frontend-js/src/app/auxiliary/locales/zh-CN.json` — SHA256 `9673911a653d52f819c696118ed1236c2ed51090b7ff93259823eaeabeb9925a`
- `frontend-js/src/app/auxiliary/locales/en-US.json` — SHA256 `00815b16b9493e95f04c505c7994aad47f208e936c65439e52bf21e20e966b05`
- `backend/tests/test_energy_price_api.py` — SHA256 `bced24d846095458d25f677dc19a65fcaca558772da8f4f1a94a0ff490763dd2`
- `backend/tests/test_energy_price_service.py` — SHA256 `b76890790c233c7c456e8529bde100cff8fcead0360ecf698c94d8c68fb5bc64`
- `backend/tests/test_energy_price_migration.py` — SHA256 `fae961841b0cc6d6a6c833a7172d4ecc0c3ebcc578174f9d691e6fb2d40d4e00`
- `backend/tests/test_core_migration_baseline.py` — SHA256 `3c125b2b27af381b6a5d0219ce09162647d37e057b95b3d21fdfc3ef4efe1e7f`
- `frontend-js/tests/module-registry/price-page.test.mjs` — SHA256 `7aeb1ee4cd93ff08c22776d4173ff4f7b737785b802a340a88fea25fced7ad3e`
- `backend/app/auxiliary/README.md` — SHA256 `4d8a5997a31945762dcd00b2ef8ad0c28c55cf5e264e5c62d7f156f25d657843`
- `backend/app/auxiliary/README.zh-CN.md` — SHA256 `554b4a77fb899794abe22b7502ebbd1f1c7970374853f2b20ccd7b61f6b29278`
- `backend/README.md` — SHA256 `dfcf15e2252ca2efd7dd1819f1529ab0daad856f5dd6ced785e3b65cf34bf64c`
- `backend/README.zh-CN.md` — SHA256 `938c86fe6e22730efe5f21ecf6be20fe2598718b742af5167dec110682a7f6b4`
- `CODE_INDEX.md` — SHA256 `a8498f683c32a5777024ad8d69504c06c1f6214ac4db9632cfe96b5929666a0d`

以上23个实现文件全部在r2 allowlist内，本tasks为第24个本角色写入文件。test_openapi_router_tags未产生BE004增量：原三路径不变，既有该文件dirty属于BE002，完整套件仍覆盖它。根/PLAN/catalog其它改动不归本角色新增。完整before/after指纹为 `implementation-hashes.json`，精确任务差异为 `implementation-delta.patch`；不能将git整体diff归为BE004。

# 首轮 DEV self-check 实际命令与结果

公开隔离副本排除所有.env*、.venv、node_modules、logs/data/dist/build/cache；公开example从Git HEAD重建，frontend仅在tmp把公开.env.example复制为.env供build。复用现有backend/.venv和frontend/node_modules软链，不安装依赖。后端公共前缀环境：`TESTING=True UV_CACHE_DIR=/private/tmp/arch-be004-r2-dev/uv-cache UV_PROJECT_ENVIRONMENT=/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend/.venv`。前端PATH前置现有Node `/Users/jason/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin`，`--config.verify-deps-before-run=false` 禁止pnpm自动安装。

`run-checks.py`真实逐命令捕获退出码，`command-results.json`记录完整argv/cwd；最终一次结果如下：

| cwd | 命令 | exit | 结果 |
| --- | --- | --- | --- |
| `/private/tmp/arch-be004-r2-dev/backend` | `uv run --offline --no-sync --env-file .env.example pytest -q -m no_db` | 0 | 205 passed / 30 deselected，4.98s；完整no_db套件；`full-no-db.log` |
| `/private/tmp/arch-be004-r2-dev/backend` | `uv run --offline --no-sync --env-file .env.example python -m compileall -q app/auxiliary tests/test_energy_price_api.py tests/test_energy_price_service.py tests/test_energy_price_migration.py tests/test_core_migration_baseline.py alembic/versions` | 0 | 触达Python源码/测试及所有active revisions编译通过；`compileall.log` |
| `/private/tmp/arch-be004-r2-dev/backend` | `uv run --offline --no-sync --env-file .env.example alembic heads` | 0 | 唯一head b8d0f2a4c6e8；`heads.log` |
| `/private/tmp/arch-be004-r2-dev/backend` | `uv run --offline --no-sync --env-file .env.example alembic history` | 0 | 单root d4e6f8a0b2c4 -> a6c8e0f2b4d6 -> b8d0f2a4c6e8；`history.log` |
| `/private/tmp/arch-be004-r2-dev/backend` | `uv run --offline --no-sync --env-file .env.example alembic upgrade head --sql` | 0 | 完整离线upgrade SQL含新DATETIME(6)、UTC默认、唯一键；`upgrade.log` |
| `/private/tmp/arch-be004-r2-dev/backend` | `uv run --offline --no-sync --env-file .env.example alembic downgrade b8d0f2a4c6e8:a6c8e0f2b4d6 --sql` | 0 | 离线仅DROP energy_price_hours，原energy_prices保留；`downgrade.log` |
| `/private/tmp/arch-be004-r2-dev/frontend-js` | `pnpm --config.verify-deps-before-run=false check:modules` | 0 | 9 active modules / 23 routes / 9 groups；`frontend-check.log` |
| `/private/tmp/arch-be004-r2-dev/frontend-js` | `pnpm --config.verify-deps-before-run=false test:modules` | 0 | 38 passed；包含10项实际编译SFC行为/竞态测试；`frontend-tests.log` |
| `/private/tmp/arch-be004-r2-dev/frontend-js` | `pnpm --config.verify-deps-before-run=false build` | 0 | 成功；仅既有chunk大小警告；`frontend-build.log` |

首次后端聚焦Service隔离测试40 passed。前端初次pnpm脚本触发自动依赖检查，因tmp node_modules指向repo而拒绝移除（ERR_PNPM_UNSAFE_MODULES_DIR，子进程exit1，未安装）；禁自动检查后首次缺Node PATH（子进程127），随后用已有Node PATH解决。首轮build缺公开role数组（exit1），仅在tmp提供公开example .env后通过。保留真实失败说明，不把这些称为实现成功。部分shell读取日志命令自身exit0不能替代其子进程退出码；最终runner提供独立returncode。

## 页面fixture

仅tmp fixture入口/临时API stub合成价格，导入真实页面、ElementPlus、BaseCard/ActionButton和theme.css，不访问真实API。临时Vite仅监听127.0.0.1:5294，sandbox第一次EPERM（exit1）后通过自动审批允许启动；初fixture runtime template和扫描多入口问题仅在tmp修正。浏览器实际核对：桌面日间只读卡片/0值/独立记录时间与修改时间；中文切换；390x844深色下document宽380、dialog宽342、表格允许横向滚动；主picker与popup日期/时间input均readonly；取消关闭。证据为browser-results.json、browser-desktop-light.png、browser-narrow-dark.png。已重置viewport、关闭标签并Ctrl-C退出唯一fixture进程（预期130）。无真实服务重启。

## 差异与链接审计

git diff --check exit0；新触达README相对链接0缺失；两旧revision、旧Model、BE002三文档SHA256与首次基线一致。audit-results.json记录这些结果，implementation-delta.patch当前SHA256 `cc5ba9c65abf331e4fe423c105a672387eb30a15a79bb2df0856e202249f0515`。首次审计时非本角色实现面的基线后改动为0；随后唯一确认的非本角色变化为PM拥有spec的同合同澄清。已存在dirty仍按baseline保留，不代表主协调之后不能机械更新其拥有索引。

# r2 同合同时间澄清与针对修正

最终审计曾发现历史IANA上海夏令时回拨日可有25个真实小时、UI附固定+08会错位，已报告主协调并停止该处待定写入；未通过slice或收窄历史掩盖。主协调交PM判断，PM依据现行“同业务小时覆盖”“日最多24”和指定参考time_buckets.floor_observed_at_to_site_hour的显式fold=0，明确同r2合同解释C：业务身份为IANA上海民用日期+小时，重复小时先floor再fold=0转UTC作唯一key，observed_at保留真实instant。wire可用固定+08或Z表达同一瞬间，显示/picker仍按IANA；不限制年份。PM经主协调授权将解释记入spec，不记录为新Human Owner批准。

Development只读核对PM澄清后的有效spec SHA256 `ddc6cc09834f07de39cd822b03520900d866b574f7254826ee2ab8535b4c17ae`，未修改spec。Service归桶显式fold=0；picker用Intl解析上海民用字段、重复选最早instant、gap提示且不POST，发送UTCZ；四输出统一+08仍表示真实instant，避免历史LMT秒offset使浏览器Date解析失败。README归并SQL也按相同民用小时/fold0身份选winner，命名时区表真实行为仍需运行gate核对。

新增代表回归：1991-09-15同民用01:30的+09与+08输入得到同UTC hour_start 1991-09-14T16:00Z，实际observed分别16:30Z/17:30Z；该日25个真实小时仅24key。UI覆盖夏令+09、重复fold0、春季不存在时间校验不POST、year1000历史LMT转换；统一wire +08可被JS读取。修正后完整必要套件205/38通过，未扩展时间库或依赖。此前204/37与browser证据保留为前轮真实结果；最后编译SFC行为回归包含本次picker修正，不重复扩展浏览器范围。

# 首轮精确 Developer handoff（F001后由末节接续）

- Task/Revision：ARCH-BE-004 r2；最终批准spec及PM同合同解释SHA256如上。
- 工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `363b297bffe65e020108f5504766b4fb1ec3b381`；未创建commit。既有dirty保留。
- 实现面：上述23文件相对首次基线的精确delta；本tasks为第24文件。`implementation-hashes.json`列每个before/after；`implementation-delta.patch` SHA256 `cc5ba9c65abf331e4fe423c105a672387eb30a15a79bb2df0856e202249f0515`。
- DEV self-check：完整no_db205passed/30deselected、frontend38passed、模块check/build、compileall、单root/head/history、离线upgrade/downgrade和链接/diff全部exit0；详见真实命令表与command-results.json。
- 后续：主协调现在启动fresh-context命名Verification，提供spec/tasks/实现/基线diff/hash/logs；由Verification独立记录checklist，本角色不写QA verdict或Human Owner acceptance。

# 限制、独立运行gate与资源

没有真实MySQL持久化/唯一键并发竞争、备份恢复、旧历史归并、命名时区表/服务DB时钟核验或运行联调证据；这些仍为独立operational gate。SQL仅生成离线与文档方案，合成归并测试验证选最后整组/旧行不变/冲突停止，不执行MySQL SQL，不证明数据库版本实运行。没有读取真实env、客户截图价格/导出，不进行DB/容器/部署/发布/refs/推送或安装依赖。

唯一新任务资源为 `/private/tmp/arch-be004-r2-dev`，含baseline、隔离源码/公开fixture、uv-cache、命令日志、patch/hashes/audit、临时浏览器fixture与PNG/JSON。QA需要这些精确证据，暂保留；无新常驻进程、分支、worktree、容器或数据库。资源回收由主协调在QA与Human Owner后核对，不清理归属不明资源。

后续gate：当前 developer_handoff -> 主协调启动fresh-context命名Verification -> Human Owner final acceptance。DEV self-check不是QA verdict或最终验收。


# F-001 同 r2 返工与第二次 Developer handoff

主协调正式转递首轮fresh-context Verification的 `qa_failed` 后启动本轮。完整只读消费当前spec/tasks/checklist及QA脚本 `/private/tmp/arch-be004-r2-qa/backend/qa_lower_bound.py` 和 `f001-asgi.log`。首轮205/38通过和原handoff仍是历史，不能消除QA发现的F-001，也不修改或覆盖checklist失败结论。

复现原因：observedAt=1000-01-01T00:00:00Z本身可写MySQL，但上海历史LMT取民用08:00/fold0后UTC桶为0999-12-31T23:54:17，不能持久化。本轮只修这个派生边界，不把正常可录历史年份一并拒绝。

修正：schemas中的纯函数canonical_hour_start同时计算IANA/fold0规范桶、校验事件UTC及最终桶UTC的MySQL下界；显式POST由PriceCreate调用并通过原422验证合同拒绝，Service复用同一函数，在进入CRUD/事务前验证。没有再次取now，保留真实observed瞬间、fold0重复小时、原始number精度与独立权限。未修改API路径、Model、migration、前端或依赖。

## 本轮精确修改面

- `backend/app/auxiliary/schemas/energy_price.py`：pre-F001 `9979493972c31c57e6b3ea8668e37ce07477995ce65199a59a624aa654c5d582` → final `d971557b6d479b5c0de7c1c8399626d4d759416106568e19b694f0c21c43ed7b`。
- `backend/app/auxiliary/services/async_energy_price.py`：pre-F001 `86b9797a2653ac00f67b0a071e86fe80764c786ab986215238553180571ea01d` → final `21afae0093b353195156202643d34cac777b4317dcd4bd79b06350b59a0582e4`。
- `backend/tests/test_energy_price_api.py`：pre-F001 `bced24d846095458d25f677dc19a65fcaca558772da8f4f1a94a0ff490763dd2` → final `7b3e9a0a2cb1afc10a4591d8d598b944091a91c08920fdfff541c58477c480de`。
- `backend/tests/test_energy_price_service.py`：pre-F001 `b76890790c233c7c456e8529bde100cff8fcead0360ecf698c94d8c68fb5bc64` → final `cd30bd85825c83c2994f6e06a9b945154eb9bdb0ebd22f799c16ea2c92c79fec`。

第5个写入文件仅本tasks。`pre-F001-hashes.json`和`pre-F001/`保存本轮写入前实现及三bundle指纹/副本；`pre-F001-evidence/`保存首轮实现manifest、patch、audit与tasks指纹。spec SHA256 `ddc6cc09834f07de39cd822b03520900d866b574f7254826ee2ab8535b4c17ae` 与checklist SHA256 `526b6b59876f5d525aa9754e4879882111f13e4cc06aa11d0290a05378fc5849` 本轮均未变化；23实现面除以上4文件全部与pre-F001一致。旧Model、旧revision及其他既有dirty继续受保护。

## 本轮 DEV self-check

仍使用首轮同一公开隔离backend副本及既有uv环境，不复制真实env、不安装、不操作真实DB。命令cwd `/private/tmp/arch-be004-r2-dev/backend`；环境前缀仍为TESTING=True、原UV_CACHE_DIR/UV_PROJECT_ENVIRONMENT。`F001-command-results.json`逐命令保存实际argv/cwd/returncode：

| 命令 | exit | 结果 |
| --- | --- | --- |
| `uv run --offline --no-sync --env-file .env.example pytest -q -m no_db tests/test_energy_price_api.py tests/test_energy_price_service.py` | 0 | 107 passed，2.98s；F001-focused.log |
| `uv run --offline --no-sync --env-file .env.example pytest -q -m no_db` | 0 | 211 passed / 30 deselected，5.21s；F001-full-no-db.log |
| `uv run --offline --no-sync --env-file .env.example python -m compileall -q app/auxiliary/schemas/energy_price.py app/auxiliary/services/async_energy_price.py tests/test_energy_price_api.py tests/test_energy_price_service.py` | 0 | F001-compileall.log |
| `git diff --check`及pre-F001保护指纹审计 | 0 | F001-audit-results.json |

新增回归使用真实Router/Schema/Service，仅替换CRUD/认证/session。原复现、等价offset以及临界前1微秒均422且CRUD/commit/rollback未调用；临界00:54:17Z及后一秒正常200、归同合法桶1000-01-01T00:54:17Z，三价格精度/0不退化。另测直接Service在未调用CRUD/commit前拒绝非法桶。完整no_db继续覆盖IANA/DST/fold0、数字精度及权限回归。

未变前端沿用首轮38项/check/build与DEV浏览器证据，未声称本轮重新运行。未变migration沿用既有离线SQL/metadata证据。首轮QA停止浏览器独立复验的事实保留；新fresh QA需完成其剩余浏览器检查。本轮无真实MySQL/并发/归并或部署证明，operational gates不变。

## 最终精确交接

- Task/Revision仍为ARCH-BE-004 r2，HEAD仍为363b297bffe65e020108f5504766b4fb1ec3b381，工作树实现，未创建commit。
- 仅本轮4实现文件与tasks；`F001-delta.patch` SHA256 `a0b506a4c8745478105751b153fcdfe98b1a6f7d686aba11ce8529514243f14a`，`F001-hashes.json`列pre/post。
- 全任务相对首次baseline的最新23文件manifest为implementation-hashes.json，完整implementation-delta.patch SHA256 `53b4f79c05ace8c9deb405343baa854ba91e4b918a8975ead6f00751b31059ad`。前文首轮patch/指纹作为历史保留，以本节作为当前handoff。
- 当前Status为developer_handoff；请主协调启动新的fresh-context命名Verification，消费当前spec/tasks/checklist、最新实现、F001增量/完整delta及真实日志。Development不写QA verdict或Human Owner验收。
- 资源仍仅原DEV tmp，新增pre-F001快照与F001日志/patch/audit供复验，QA tmp属QA继续保留。没有新进程、标签、分支、worktree、容器、DB或运行服务操作。
