Task ID: ARCH-BE-002
Revision: r3
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: 精确 r3 F-001 同范围返工与 DEV self-check 完成；保留首轮 qa_failed，交主协调者启动新的 fresh-context Verification；不代给 QA verdict。

Task Namespace: aiis-ics-arch
Workflow Mode: STD
Execution Mode: agent_team_same_session
Updated: 2026-10-13

# 实施事实

Development 按获批 r2 在当前共享 working tree 实施；未创建 commit、branch 或 worktree。
已读取根 AGENTS、README/PLAN pairs、canonical workflow、完整 spec（含原 r1 历史）、backend 与 app README/PLAN，未发现更近 AGENTS。使用 backend-arch 及响应/分层/迁移/Registry/认证/日志测试 references、project-governance 和 code-document-indexer。主协调者负责 notifier 与根/backend PLAN/catalog，同步不归本角色。

1. 新增 auxiliary 固定七包、无副作用 manifest（enabled=True/order=60）、三接口、Model/Schema、async CRUD/Service。响应使用共享信封与 ApiSchema，局部 serializer 保证 JSON number；精确 Decimal 校验不舍入，备注快照不拼接，拒绝 server-owned/extra 字段。
2. GET read / POST manage 权限各自独立；API 复用认证主体 username；Service 控制原子追加 commit/rollback，日志 actor/id/result，不含备注或请求体。
3. 新增 a6c8e0f2b4d6 单表后继 migration，保留十四表 root 原文；新增七项 check constraints 与 created_at/id index，无 seed/default price/implicit DDL。
4. 新聚焦 no_db tests 与五项已批准既有预期同步；根/backend/app 与模块双语边界文档，CODE_INDEX 新增实际入口。未修改 frontend/env/shared/common/session/schema-maintenance/依赖/lock/组合根/BE003。

# 工作树与保护基线

本任务资源根：`/private/tmp/ARCH-BE-002-r2-dev`。`baseline-hashes.json`、`baseline.diff`、`baseline-status.txt`、`head.txt` 记录开始时 HEAD、tracked files、BE003 草案与 env hashes。已存在的六索引和 spec 改动保留；不把其算为 Development 增量。

# r2 DEV self-check 历史（保留失败事实）

验证副本 `backend/` 排除全部 `.env*`、.venv、logs/data/build/dist/cache；仅从 Git HEAD 已跟踪的 backend 三个公开 example 与 frontend 两个公开 example 在 tmp 重建测试 fixture。没有复制真实 env 或运行数据。复用既有 backend/.venv，`UV_PROJECT_ENVIRONMENT` 指向该环境，`UV_CACHE_DIR` 指向任务 tmp；`uv run --offline --no-sync --env-file .env.example` 不安装依赖、不访问网络。完整回归显式 `TESTING=True`，no_db marker 阻止 autouse DB fixture。

- 聚焦八个测试文件：exit 0，82 passed，2.04s（focused.log）；此后补 raw non-standard NaN/Infinity wire negative，暴露默认422 handler的nonfinite回显编码错误，已在本模块Schema before model validator将nonfinite包装为JSONsafe非法值，不改共享异常处理。
- 完整 `pytest -q -m no_db`：r2 最后一次 exit 1，163 passed / 1 failed / 30 deselected，4.00s（full-no-db-baseline-failure.log，原输出保留）；仅既有 test_monitor_frontend_permissions 仍读退役 VITE_ROLE_PAGE_ACCESS_JSON，而公开模板使用两角色数组。已报告精确file/line/最小diff，请PM限定修正授权；未跳过、删除或伪称全通过。
- `alembic heads`、`history`、`upgrade head --sql`、`downgrade a6c8e0f2b4d6:base --sql`、受影响 Python compileall：均 exit 0（command-results.json 与同名 logs）。单root d4e6f8a0b2c4 / 单head a6c8e0f2b4d6；离线 SQL 不建立连接。
- 前期真实失败：首次日志重定向误用repo cwd导致sandbox拒绝（exit1，未运行项目）；默认uv cache读权限不足exit2（后改任务cache）；新test import收集exit2（后改tests package import）；完整回归fixture TESTING=False与缺frontend公开examples失败（后显式TESTING=True、重建公开fixture）。以上均未修改真实服务或数据库。

# 限制与风险

真实 MySQL upgrade、保存查询、重启后前端联调和运行状态为 r2 明确 deferred operational gate；本轮无 Docker up/down/build、online migration、DB/PLC操作、服务重启、Git/GitHub推送。未迁移DB前不能直接采用新API，manifest注册不证明live服务重载。权限不会自动配置sup/op；downgrade丢失价格历史，须另行批准。

# r3 批准与修复

Human Owner 明确“批准 r3，一并修复旧测试并完成验证”；PM 将 spec 标记为 r3 owner_approved 后才修改新增文件。批准规格 SHA256：`aa6771d65d5696f892150b75bedbf518770307819d922e252b38c1916b5c365e`。
仅新增修复 `backend/tests/test_monitor_frontend_permissions.py`：读取两个公开 example 的 supervisor/operator 新数组，各自必须存在、为合法 JSON list 且等于 []；继续覆盖 monitor.realtime 无默认授权，并拒绝活动旧 key。缺键、非法JSON、错误类型或非空授权均导致断言失败，未加 fallback/skip/xfail，也未改 frontend 或 env。

# r3 首轮 DEV self-check（后由 QA 证实尚不足）

以下运行 cwd 均为 `/private/tmp/ARCH-BE-002-r2-dev/backend`；环境前缀为 `TESTING=True UV_CACHE_DIR=/private/tmp/ARCH-BE-002-r2-dev/uv-cache UV_PROJECT_ENVIRONMENT=/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend/.venv`。公开 examples 是 Git HEAD 公共 fixture，不是当前真实运行配置。

| 实际命令 | 退出码 / 结果 | 证据 |
| --- | --- | --- |
| `uv run --offline --no-sync --env-file .env.example pytest -q -m no_db tests/test_monitor_frontend_permissions.py` | 0；1 passed，0.05s | r3-single.log |
| `uv run --offline --no-sync --env-file .env.example pytest -q -m no_db` | 0；164 passed，30 deselected，3.59s；未删测试或缩小 no_db 套件 | r3-full-no-db.log |
| `uv run --offline --no-sync --env-file .env.example python -m compileall -q app/auxiliary tests/test_energy_price_api.py tests/test_energy_price_service.py tests/test_energy_price_migration.py tests/test_monitor_frontend_permissions.py tests/test_module_structure.py tests/test_module_registry.py tests/test_openapi_router_tags.py tests/test_celery_retirement.py tests/test_core_migration_baseline.py alembic/versions` | 0；最终受影响 Python 编译通过 | r3-compileall.log |
| `uv run --offline --no-sync --env-file .env.example alembic heads` / `history` / `upgrade head --sql` / `downgrade a6c8e0f2b4d6:base --sql` | 各 0；沿用 r2 同一未改迁移的离线证据 | command-results.json、heads.log、history.log、upgrade-sql.log、downgrade-sql.log |
| 增量 Markdown 本地链接脚本（Python pathlib/re，解析新增 diff 与新文件链接） | 0；24 条增量链接均存在；完整触达文件扫描73条发现2条原有B11死链（backend/app README pair），按主协调者明确边界保留，未伪称全部旧链通过 | doclinks-delta.json、doclinks.json |
| `git diff --check` | 0 | diff-check.log |
| SHA256 / 角色增量审计脚本 | 0；十四个 env/BE003/root 保护文件及 r2完整历史均不变；r3代码增量仅旧测试单文件，其余差异为PM spec与协调者六索引 | r3-protected-check.json、r3-from-r2-files.json、developer-incremental.patch、handoff-files.json |

原 Core root SHA256：`f038e80badccf322292a9b4dca5bf2bb563bb5c15388f4745bc36fd02ca478f2`，最终一致。原十四表 parity/downgrade 与客户残留禁止项保留，新增 recorder 检查十五表 metadata、7 check constraints、Numeric无业务default、单root/head均通过。82项最终聚焦（含raw NaN/Infinity HTTP422、共享最终JSON number与zero）为 exit0，2.17s（focused-final.log），完整164项已再次覆盖。

# 精确变更文件

- `AGENTS.md`
- `CODE_INDEX.md`
- `README.md`
- `README.zh-CN.md`
- `backend/README.md`
- `backend/README.zh-CN.md`
- `backend/alembic/versions/20261013_1200_a6c8e0f2b4d6_add_public_energy_prices.py`
- `backend/app/README.md`
- `backend/app/README.zh-CN.md`
- `backend/app/auxiliary/PLAN.md`
- `backend/app/auxiliary/PLAN.zh-CN.md`
- `backend/app/auxiliary/README.md`
- `backend/app/auxiliary/README.zh-CN.md`
- `backend/app/auxiliary/__init__.py`
- `backend/app/auxiliary/api/__init__.py`
- `backend/app/auxiliary/api/energy_price.py`
- `backend/app/auxiliary/api/routes.py`
- `backend/app/auxiliary/crud/__init__.py`
- `backend/app/auxiliary/crud/async_energy_price.py`
- `backend/app/auxiliary/manifest.py`
- `backend/app/auxiliary/mocks/__init__.py`
- `backend/app/auxiliary/models/__init__.py`
- `backend/app/auxiliary/models/energy_price.py`
- `backend/app/auxiliary/plans/README.md`
- `backend/app/auxiliary/plans/README.zh-CN.md`
- `backend/app/auxiliary/schemas/__init__.py`
- `backend/app/auxiliary/schemas/energy_price.py`
- `backend/app/auxiliary/seeds/__init__.py`
- `backend/app/auxiliary/services/__init__.py`
- `backend/app/auxiliary/services/async_energy_price.py`
- `backend/tests/test_celery_retirement.py`
- `backend/tests/test_core_migration_baseline.py`
- `backend/tests/test_energy_price_api.py`
- `backend/tests/test_energy_price_migration.py`
- `backend/tests/test_energy_price_service.py`
- `backend/tests/test_module_registry.py`
- `backend/tests/test_module_structure.py`
- `backend/tests/test_monitor_frontend_permissions.py`
- `backend/tests/test_openapi_router_tags.py`
- `plans/ARCH-BE-002-energy-price-api/tasks.md`

# r3 首轮 developer_handoff（已由 qa_failed 退回）

- Task / Revision：ARCH-BE-002 r3（包含未变的 r2 实现与验收合同）。
- Working tree：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；基线 HEAD `363b297bffe65e020108f5504766b4fb1ec3b381`，未创建 commit/branch/worktree。精确 Development 文件和 SHA256 见 `handoff-files.json`，增量 diff 含新增文件见 `developer-incremental.patch`。PM spec 与主协调者六索引不归本角色，不混入 Development patch；BE003 保持原样。
- DEV self-check：上述真实通过与历史失败；无独立 QA verdict、无 Human Owner final acceptance。
- 限制：源码/ASGI fake-session/SQL compilation/metadata/offline SQL 证据不证明真实 MySQL 持久化、DB约束执行、服务重载、当前前端联调或部署；这些 operational gate 按获批 r3/r2 deferred。两个既有B11文档死链保留，新增链接全部通过。
- 已知风险：enabled manifest 下一次真实reload会暴露路由，采用前须先显式迁移；sup/op默认未授权，前端可见不等于API权限；downgrade丢失历史。事务fake不证明真实驱动行为或并发快照。
- 资源：唯一新建任务tmp `/private/tmp/ARCH-BE-002-r2-dev` 包含隔离backend、两份frontend公开example、uv-cache、write_tests.py、baseline/r2快照、命令日志、离线SQL、diff/hash/link审计文件。验证需继续使用，暂保留；无新进程/分支/worktree/容器/数据库/真实服务。既有 `.venv` 只复用，无安装。资源回收由主协调者在独立验证与最终验收后核对；本角色未删除他人资源。
- 下一 gate：主协调者实际启动 fresh-context Verification，读完整 r3 spec、tasks、实现、working tree/diff与上述证据，独立创建 checklist.md。Development 不代写 checklist/spec。

# r3 F-001 同范围返工事实与第二次 developer_handoff

首轮独立 Verification 已在 `checklist.md` 记录 `qa_failed`：原始 JSON 数字 `1.23450000000000001`、`999999.99990000001`、`0.000100000000000000001` 先被框架解析为 float，再由 Schema 转 Decimal，丢失超精度信息而错误返回200。首轮164通过不能证明该边界；失败历史与独立复现路径 `/private/tmp/ARCH-BE-002-r3-qa-9o27ws83/precision-wire-repro.py` / `.log` 保留。本角色只读 checklist，不修改失败 verdict、spec 或验收标准。

主协调者按已批准 r3 触发同范围返工，没有新授权、依赖或规则收窄。实际修改：

- `backend/app/auxiliary/api/energy_price.py`：模块局部 PriceRoute/PriceJSONRequest 通过标准库 `json.loads(parse_float=Decimal)` 在 float 转换前保留原始十进制数字；使用 Request 子类的公开 body/receive/scope 接口，继承 FastAPI 路由及原有异常处理，未更改全局 parser/shared/common。
- `backend/app/auxiliary/schemas/energy_price.py`：价格 Decimal 保持无损进入已有精度/范围校验；非法非价格 Decimal、NaN/Infinity 等输入安全表示为不被字段接受的值，保证既有 HTTP422 错误可JSON序列化。数字备注仍拒绝，未把它误转为合法文案；有效数字字符串、camelCase/snake_case、备注/extra限制仍保留。
- `backend/tests/test_energy_price_api.py`：新增36项原始 HTTP body 回归：QA三个失败值及其它非法精度/范围×三种价格，合法零/四位/最大值/长尾零/指数数字，数字备注、非法额外字段、NaN备注与畸形JSON。断言非法值422且Service未调用；合法值200且Service收到精确Decimal。所有原有测试保留。
- auxiliary README 双语 pair：补充本模块原始数字先按Decimal解析的边界说明；没有拓扑新增，未扩大 CODE_INDEX/依赖或修改其它实现。
- tasks：保留首轮DEV及QA失败事实，更新本次命令、限制和handoff。没有其他代码、migration、env、权限、组合根或前端修改。

## 本次实际验证

继续复用既有公开隔离副本 `/private/tmp/ARCH-BE-002-r2-dev/backend`；排除真实env/运行数据规则不变，不改项目环境或安装依赖。统一命令前缀仍为 `TESTING=True UV_CACHE_DIR=/private/tmp/ARCH-BE-002-r2-dev/uv-cache UV_PROJECT_ENVIRONMENT=/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend/.venv uv run --offline --no-sync --env-file .env.example`。

| 实际命令（接统一前缀） | 退出码 / 结果 | 证据 |
| --- | --- | --- |
| `pytest -q -m no_db tests/test_energy_price_api.py tests/test_energy_price_service.py` | 0；97 passed，2.59s | F001-focused.log |
| `pytest -q -m no_db` | 0；200 passed、30 deselected，4.86s；包括既有OpenAPI、权限与原始数字回归 | F001-full-no-db.log |
| `python -m compileall -q app/auxiliary tests/test_energy_price_api.py tests/test_energy_price_service.py tests/test_energy_price_migration.py tests/test_monitor_frontend_permissions.py tests/test_module_structure.py tests/test_module_registry.py tests/test_openapi_router_tags.py tests/test_celery_retirement.py tests/test_core_migration_baseline.py alembic/versions` | 0 | F001-compileall.log |
| `git diff --check` 与增量Markdown链接/指纹脚本 | 0；增量24条链接通过，34个spec/checklist/env/原Core root等受保护文件无变化 | F001-diff-check.log、doclinks-delta.json、F001-protected-check.json |

迁移从首轮到本次未变，继续沿用已记录及独立QA验证通过的heads/history/offline SQL/parity；没有理由重复运行或执行online migration。两个既有B11死链仍保留，不能宣称全仓库历史链接全部通过。

## 清单修正与精确第二次 handoff

QA指出旧 `r3-from-r2-files.json` 在生成后又发生辅助模块PLAN pair/catalog pair的机械同步，清单漏列四文件。该旧工件已备份为 `r3-from-r2-files-before-F001.json`；现已按 `r2-implementation-hashes.json` 与当前全部文件逐项重算，补齐四机械文件、任务事实以及QA新建checklist（分清实际writer），不再以旧快照声称完整。角色分类及本次相对pre-F001增量见 `F001-diff-audit.json`；未知/越界文件计数为0。

精确交接：ARCH-BE-002 r3，working tree `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD仍为 `363b297bffe65e020108f5504766b4fb1ec3b381`，无新commit/branch/worktree。更新后的 `handoff-files.json` 为全部40个Development文件SHA，`developer-incremental.patch` 含全部新增/修改实现与tasks，排除PMspec、QAchecklist、主协调六索引和BE003。本次返工单独patch与hash为 `F001-incremental.patch` / `F001-handoff-files.json`；首轮hash清单/patch已保留为pre-F001版本。

当前 `developer_handoff` 只表示本角色返工与self-check完成，不覆盖仍为qa_failed的首轮独立结论。请主协调者实际启动新的fresh-context Verification，完整复核r3/r2与F-001；QA给出新verdict，Human Owner继续保留最终验收。真实DB/服务/前端联调/部署/运行 gate、权限采用及downgrade数据风险沿用前述限制，无新操作授权。

资源仍只有本任务DEV tmp与首轮QA tmp（后者归QA）；新增pre-F001指纹、tasks快照、各日志与修正清单保留供新QA，不清理他人资源或长期证据。无新常驻进程/容器/数据库；既有.venv只复用。通知与最终回收归主协调者。
