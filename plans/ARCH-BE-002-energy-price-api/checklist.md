Task ID: ARCH-BE-002
Revision: r3
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner 于 2026-10-13 明确最终验收 ARCH-BE-002 r3；首轮失败、返工与独立通过证据保留。日期补充作为独立新需求，真实 DB/运行 gate 仍 deferred；未部署或实施新规则。

Task Namespace: aiis-ics-arch
Workflow Mode: STD
Execution Mode: agent_team_same_session
Updated: 2026-10-13

当前状态见文末“Human Owner 最终验收”。下方首轮 `qa_failed`、F-001 请求/实际结果、命令和交接均为原始历史证据，完整保留。

# 验证基准与独立性

- 精确目标：[spec.md](spec.md) 的获批 r3，完整保留的 r2 合同与 AC-r2-001..005，以及 AC-r3-001..002；Development [tasks.md](tasks.md) 状态为 `developer_handoff`。
- 工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD `363b297bffe65e020108f5504766b4fb1ec3b381`。验证的是未提交源码，不能以 HEAD 本身代表新增实现。
- 本轮由独立命名 Verification `/root/be002_r3_verification` 在 fresh context 执行；未继承 Development 对话推理。独立读取根 AGENTS、canonical workflow、根 README/PLAN pairs、backend README/PLAN pairs、app README pair、auxiliary README/PLAN/catalog pairs、完整 spec/tasks、当前实现、既有测试差异和 handoff 工件；未发现更近 AGENTS。
- 使用 `project-governance`、`aiis`、`backend-arch`（RESPONSE_CONTRACT / LAYERS / DATABASE_AND_MIGRATIONS / MODULE_REGISTRATION / AUTH_SECURITY / OPERATIONS_TESTING）及 `code-document-indexer`，只作验证。没有修改实现、测试、spec、tasks、env 或配置。
- `.codex/agents/verification.toml` 为配置证据；不把配置的 model/effort 作为独立观测的运行值。本角色为 `contract_only`，fresh context、串行 handoff、差异和本 checklist 构成合同控制，不声称平台 ACL、强制路由或正式团队激活。

# 环境与隔离

QA 独立创建 `/private/tmp/ARCH-BE-002-r3-qa-9o27ws83`，从当前工作树复制 backend 源码，排除全部 `.env*`、`.venv`、logs、data、build、dist 和 cache；随后只从 Git HEAD 重建 backend 三份公开 example、frontend 两份公开 example。`fixture-report.json` 确认仅这五份 example 进入副本，没有真实运行 env。

复用项目既有 `backend/.venv`、`pyproject.toml` 与 `uv.lock`；没有安装依赖。子进程只继承 PATH/HOME/USER/TMPDIR/LANG/LC_ALL 等运行基础变量，项目配置采用公开 example 和显式验证覆盖：`TESTING=True`、`BACKEND_MOCK_ENABLED=False`、`PROJECTION_RUNNER_ENABLED=False`；测试运行还显式关闭三个 bootstrap flag。未输出真实 env 内容，保护审计只比较文件指纹。

实际环境：Python 3.13.3；FastAPI 0.135.1、Pydantic 2.12.5、SQLAlchemy 2.0.48、Alembic 1.18.4、pytest 9.0.2、httpx 0.28.1。版本证据为 QA `versions.log`。

下表命令的 cwd 均为 QA 副本 `backend/`；统一前缀：

```text
TESTING=True BACKEND_MOCK_ENABLED=False PROJECTION_RUNNER_ENABLED=False
UV_CACHE_DIR=/private/tmp/ARCH-BE-002-r3-qa-9o27ws83/uv-cache
UV_PROJECT_ENVIRONMENT=/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend/.venv
UV_PYTHON_DOWNLOADS=never
uv run --offline --no-sync --env-file .env.example
```

所有 pytest 均选择 `-m no_db`；已核对 autouse `prepare_test_database` 在该标记下直接 yield，不进入建库/清表路径。ASGITransport 和 dependency overrides 没有发真实 HTTP 请求；fake session / SQL compilation 不等于 MySQL 持久化。

# 命令与结果

| 独立执行的命令（接统一 uv 前缀） | 退出码 / 结果 | QA 证据 |
| --- | --- | --- |
| `pytest -q -m no_db tests/test_monitor_frontend_permissions.py` | 0；1 passed，0.02s | `single.log` |
| `pytest -q -m no_db tests/test_energy_price_api.py tests/test_energy_price_service.py tests/test_energy_price_migration.py tests/test_module_structure.py tests/test_module_registry.py tests/test_openapi_router_tags.py tests/test_celery_retirement.py tests/test_core_migration_baseline.py` | 0；82 passed，1.96s | `focused.log` |
| `pytest -q -m no_db` | 0；164 passed、30 deselected，3.68s；完整当前 no_db 套件 | `full-no-db.log` |
| `python -m compileall -q app/auxiliary tests/test_energy_price_api.py tests/test_energy_price_service.py tests/test_energy_price_migration.py tests/test_monitor_frontend_permissions.py tests/test_module_structure.py tests/test_module_registry.py tests/test_openapi_router_tags.py tests/test_celery_retirement.py tests/test_core_migration_baseline.py alembic/versions` | 0 | `compileall.log` |
| `alembic heads` | 0；唯一 head `a6c8e0f2b4d6` | `heads.log` |
| `alembic history` | 0；`<base> -> d4e6f8a0b2c4 -> a6c8e0f2b4d6` | `history.log` |
| `alembic upgrade head --sql` | 0；仅离线 SQL 生成 | `upgrade-sql.log` |
| `alembic downgrade a6c8e0f2b4d6:base --sql` | 0；仅离线 SQL 生成 | `downgrade-sql.log` |
| `python -`，输入 `precision-wire-repro.py` 所保存的 ASGI 诊断代码 | 0 表示复现脚本执行完成；三项预期 422 均实际返回 200，属于验收失败 | `precision-wire-repro.py` / `.log` |
| Python pathlib/re 对 Development patch 新增 Markdown 链接核对 | 0；24 条新增链接存在；完整触达文档仍有两条原有 B11 死链 | `doclinks-audit.json` |
| `git diff --check`（真实工作树） | 0 | `diff-check.log` |
| Python hashlib 对 handoff 与验证开始/结束文件核对 | 0；40/40 handoff 文件匹配；QA 前后源码指纹无变化 | `fixture-report.json`、`verification-start-hashes.json` |

Development 的 82/164 通过记录仅作为输入；上表测试结果均为本轮独立执行。通过现有套件不能消除下方新增复现的 failure。

# 验收标准检查

| 标准 | 结果与精确证据 |
| --- | --- |
| AC-r2-001 接口 | 三条实际 ASGI 路径/方法、共享 `code/message/data`、camelCase、current null、空/越界列表、默认 1/20、size 1..100、JSON number/0、备注快照与 server-owned extra 拒绝的现有断言通过。对应 `test_asgi_wire_contract_and_pagination`；价格输入精度合同存在 F-001，不能认定整个接口合同已验收。 |
| AC-r2-002 保存/规则 | **FAIL，F-001**。现有 schema 字符串精度、最大值、备注长度与 null/空串、成功/flush/refresh/commit 失败回滚、actor/日志脱敏断言通过。真实 SQL 无 DB 编译验证 `created_at DESC, id DESC`、limit/offset/count。原始 JSON number 在 Decimal 校验前丢失超精度信息，违反不舍入/超精度 422 要求。 |
| AC-r2-003 权限/注册 | PASS（源码隔离范围）。admin、supervisor/operator 独立 read/manage、无授权、unknown、旧 auxiliary key、未认证和 disabled 路由矩阵通过；disabled 无 route/OpenAPI。manifest 仅声明 auxiliary、enabled=True、order=60、两权限；无中央列表/权限 resolver 改动；demo 仍 disabled。当前/example env 指纹保持。 |
| AC-r2-004 Migration | PASS（静态/offline 范围）。Core root SHA256 为 `f038e80badccf322292a9b4dca5bf2bb563bb5c15388f4745bc36fd02ca478f2`，与 HEAD 和 DEV baseline 相同。原十四表 recorder parity/downgrade/客户残留禁止项保留；新后继实际 recorder 操作仅 create energy_prices/index，七个 check、非空 Numeric(10,4) 无业务 default、十五表完整 metadata parity、单 root/head 与 offline SQL 均通过。未改 Alembic env、schema-maintenance 或数据库基础设施。 |
| AC-r2-005 交接/治理 | 测试、compileall、新增文档链接、diff-check 均通过。双语新增公共能力边界对应；薄 API、async Service/CRUD、Service 事务、无 mock/seed provider/隐式 DDL、关键中文说明与 CODE_INDEX 实际入口均已核对。40 文件 handoff 与当前实现一致；精确差异清单限制见下节。F-001 未关闭，不能把交接或整体源码标记完成。 |
| AC-r3-001 旧测试迁移 | PASS。两份公开 example 均读 supervisor/operator 新数组；helper 要求 key 存在、合法 JSON list，测试要求各自 `[]` 并继续排除 monitor.realtime。保留 no_db，无旧 key fallback/skip/xfail；未修改 frontend/example/真实 env。单文件及完整 no_db 已独立通过。 |
| AC-r3-002 增量保护 | 源码/测试额外增量只有 `test_monitor_frontend_permissions.py`；其余为任务事实和下节列明的机械 Revision/状态索引同步。frontend source/env、BE003、Core root、其他任务受保护，验证期间未变化。原 r1/r2 历史保留。没有据 DEV self-check 推导 QA 或 Owner acceptance。 |

# F-001：原始 JSON number 超精度被接受

规格 R2-002 明确要求：三价格最多四位有效小数，超精度返回 HTTP 422，不舍入、不截断；范围上限为 `999999.9999`。对真实 ASGI POST `/api/v1/energy` 发送原始 JSON 文本，认证/session 使用与现有 API 用例相同的 overrides，Service 以 AsyncMock 捕获进入参数：

```json
{"electricPrice":1.23450000000000001,"hydrogenPrice":1,"argonPrice":2}
```

| 原始 electricPrice 数字字面量 | 预期 | 实际 HTTP | Service 收到的 Decimal |
| --- | --- | --- | --- |
| `1.23450000000000001` | 422；不得保存 | 200 | `1.2345` |
| `999999.99990000001` | 422；同时超过精度及数值上限 | 200 | `999999.9999` |
| `0.000100000000000000001` | 422；不得保存 | 200 | `0.0001` |

定位：[schemas/energy_price.py](../../backend/app/auxiliary/schemas/energy_price.py) 的 `validate_price()` 使用 `Decimal(str(value))`；FastAPI 请求 JSON 解析已先把 number 变为 Python float，丢失的信息无法由后置校验恢复。现有 long-decimal 用例使用字符串，未覆盖这些原始数字字面量。该复现仅证明非法输入进入成功处理路径，不声称已写入真实数据库。

复现入口是在上述 QA backend cwd/环境中运行 `uv run --offline --no-sync --env-file .env.example python - < ../precision-wire-repro.py`。脚本使用现有 `tests.test_energy_price_api.app_for` 与 ASGITransport，实际返回和捕获值保存在 `.log`。本节原始 body、预期/实际和定位保留于 checklist，不依赖 tmp 作为唯一失败说明。

返工要求：在已批准三价格输入边界内消除原始 JSON number 的精度丢失绕过，补充相应原始 HTTP body 回归，仍接受合法四位价格和无损十进制字符串，并保留共享 serializer/异常平台/前端/env/依赖边界。具体实现归 Development；若其方案需要超 allowlist 文件或改变批准的数值规则，应回 PM，而不是由 QA 放宽验收。

# 差异与证据清单审计

- 独立核对 DEV `handoff-files.json` 的 40 个 SHA256，均匹配当前文件；`developer-incremental.patch` 的 40 个路径与 handoff 集合一致，覆盖新增文件，排除 PM spec、主协调六索引和 BE003。
- DEV baseline 指纹比较未发现超出完整 r2/r3 allowlist、PM spec 与协调六索引的源码变化；保护文件包括五份真实 backend/frontend env、公开 examples、BE003 spec 和旧 Core root，均保持。没有输出这些真实 env 内容。
- `r3-from-r2-files.json` 不能作为完整差异清单：与 `r2-implementation-hashes.json` 实比，还存在 auxiliary PLAN pair 和模块 plans README pair 的四处机械同步。反向替换验证 SHA 精确吻合：PLAN 仅 `r2/in_progress -> r3/developer_handoff`；catalog 仅 `r2 -> r3`。40 文件 handoff 已包含四文件，无附加业务变化。初次严格 audit helper 因未列这四个元数据文件 exit 1；随后根据实际内容和反向 hash 将其识别为机械同步，未修改实现或隐藏该工具结果。
- 两条 B11 链接在 HEAD 的 backend/app README pair 已存在；本轮 24 条新增链接均存在。保留既有死链，不能宣称整个仓库所有历史文档链接均通过。
- QA 本轮唯一仓库写入为本 `checklist.md`。创建 checklist 前，相对 QA 开始指纹未观察到任何源码变化。根/模块索引未来状态同步由对应 owner/协调者承担，QA 不修改索引。

# Acceptance Audit、限制与资源

| 表面 | 当前结论 / 后续 gate |
| --- | --- |
| 原始 JSON number 校验 | 未通过；F-001 返 Development，不能由 164 tests passed 替代。 |
| 其他当前源码/隔离 HTTP/Service/SQL/migration 证据 | 上表通过项作为本轮证据保留；整体 r3 仍 qa_failed。 |
| 真实 MySQL upgrade、保存/查询、DB check 实际执行 | 按获批 r2/r3 为 deferred operational gate；未执行，不阻塞本轮源码验证，但本轮源码失败另有 F-001。 |
| 重启后当前前端联调、进程重载与运行状态 | 按规格 deferred；未重启或验证 live 服务。enabled manifest 只表示源码注册，采用前须先显式准备 schema。 |
| 发布/部署/生产/PLC/容器/真实 env 授权变更 | 不在本轮授权；未执行，不作完成声明。 |
| Human Owner final acceptance | 未发生；qa_failed 不进入通过后的最终验收。 |

没有创建数据库、容器、服务进程、分支或 worktree；没有联网安装、在线 migration、真实数据操作、服务重启、Git/GitHub 推送。真实 MySQL driver 行为、持久化和并发快照均未由 fake session 证明；downgrade 会删除价格历史，实际回退需独立审查。

保留 DEV `/private/tmp/ARCH-BE-002-r2-dev`（基线/差异/历史失败与 DEV 证据）和 QA `/private/tmp/ARCH-BE-002-r3-qa-9o27ws83`（独立副本、日志、离线 SQL、精度复现、指纹和链接审计），供返工和下一轮 fresh QA。既有项目 `.venv` 只复用；QA 不回收资源。安全清理由主协调者在验证/最终验收及依赖盘点后处理。

# Verdict 与 handoff

**Verdict：qa_failed。** 唯一已确认实现 failure 为 F-001；没有环境 blocker 被冒充为通过，也没有把规格已 deferred 的运行 gate 改成新阻塞。

已即时把原始请求、HTTP 200/预期 422、捕获 Decimal、定位及 QA 工件路径交主协调者返回 Development。Development 完成同范围返工和真实 self-check 后，需要新的 fresh-context Verification turn；本轮失败历史应保留。最终通过结果只能 handoff 给 Human Owner 决定最终验收。

# 第二轮返工验证（2026-10-13）

## 精确目标、独立性与环境

独立命名 Verification `/root/be002_r3_reverification` 以 fresh context 消费获批 ARCH-BE-002 r3、完整 r2/r1 历史、最新第二次 `developer_handoff` 和本 checklist；未继承 Development 对话推理。重新读取根 AGENTS/canonical workflow/角色合同、根与最近 backend/app/auxiliary 的 README/PLAN、实现、全部既有测试增量及最新完整/返工 patch。使用 `project-governance`、`aiis`、`backend-arch` 及六项上述 references、`code-document-indexer`；另按 `i18n-workflow` 确认返工沿用既有 success/校验错误语义，没有新增展示文案。角色继续为 `contract_only`，不宣称 ACL、强制路由或独立观测配置中的 model/effort。

本轮独立副本为 `/private/tmp/ARCH-BE-002-r3-reqa-j6nttyeh`：从当前工作树复制 backend 源码，排除全部 `.env*`、`.venv`、logs/data/build/dist/cache；再仅从 HEAD 重建三份 backend、两份 frontend 公开 example。没有读取或复制真实 env。使用原项目 `.venv`、uv/lockfile，没有安装依赖；Python 3.13.3、FastAPI 0.135.1、Pydantic 2.12.5、SQLAlchemy 2.0.48、Alembic 1.18.4、pytest 9.0.2、httpx 0.28.1（`versions.log`）。已复核 no_db autouse fixture 直接 yield；ASGI 使用 dependency overrides，没有真实网络/DB/容器/服务操作。

cwd 为该副本 `backend/`。uv 命令统一使用以下前缀；仅继承运行基础环境，另显式关闭三个 bootstrap flag：

```text
TESTING=True BACKEND_MOCK_ENABLED=False PROJECTION_RUNNER_ENABLED=False
ADMIN_BOOTSTRAP_ENABLED=False SUPERVISOR_BOOTSTRAP_ENABLED=False OPERATOR_BOOTSTRAP_ENABLED=False
UV_CACHE_DIR=/private/tmp/ARCH-BE-002-r3-reqa-j6nttyeh/uv-cache
UV_PROJECT_ENVIRONMENT=/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend/.venv
UV_PYTHON_DOWNLOADS=never PYTHONDONTWRITEBYTECODE=1
uv run --offline --no-sync --env-file .env.example
```

## 本轮独立命令与结果

| 命令（接上述 uv 前缀） | 退出码 / 结果 | 本轮证据 |
| --- | --- | --- |
| `pytest -q -m no_db tests/test_monitor_frontend_permissions.py` | 0；1 passed，0.03s | `single.log` |
| `pytest -q -m no_db` | 0；200 passed、30 deselected，5.63s；完整套件包含 API/Service/migration/权限/OpenAPI 回归 | `full-no-db.log` |
| `python -m compileall -q app/auxiliary tests/test_energy_price_api.py tests/test_energy_price_service.py tests/test_energy_price_migration.py tests/test_monitor_frontend_permissions.py tests/test_module_structure.py tests/test_module_registry.py tests/test_openapi_router_tags.py tests/test_celery_retirement.py tests/test_core_migration_baseline.py alembic/versions` | 0 | `compileall.log` |
| `python - < ../precision-wire-verify.py` | 0；独立构造 ASGI app/认证与 session overrides，52 项原始 body 检查及 OpenAPI 断言通过 | `precision-wire-verify.py`、`.log`、`precision-wire-results.json`、`openapi.json` |
| Python hashlib / unified-hunk 反向重构与角色差异审计；真实工作树 `git diff --check` | 各 0；40/40 与 6/6 SHA 匹配，40/6 patch 均重构原基线，unknown=0；24 新增链接通过 | `handoff-diff-audit.json`、`doclinks-audit.json`、`diff-check.log` |

本轮命令、cwd、退出码另存 `commands.json`；Development 的 97/200 自测仅为输入，没有替代上述独立执行。

## F-001 关闭证据与验收复核

`PriceJSONRequest.json()` 在本模块路由内使用 `json.loads(parse_float=Decimal)`；Schema 保留价格十进制字面量进入范围/有效小数校验，其他 Decimal/非有限值保持非法且可序列化。未改变 shared/common、FastAPI 异常平台、权限 resolver、前端或依赖。

| 原始 JSON 数字（分别放入三个价格字段） | 本轮实际 HTTP | 保存 Service |
| --- | --- | --- |
| `1.23450000000000001` | 三项均 422 | 均未调用 |
| `999999.99990000001` | 三项均 422 | 均未调用 |
| `0.000100000000000000001` | 三项均 422 | 均未调用 |

独立脚本另验证：18 项合法输入（三字段各覆盖 0、四位 number、最大值 string、长尾零 string/number、指数 number）返回 200，Service 收到精确 Decimal，最终价格输出仍为 JSON number；21 项 bool/null/空串/list/object/NaN/超范围输入均 422 且不调用 Service。数字备注、extra 中极大 Decimal、嵌套 Decimal/NaN 错误与畸形 JSON 四项均返回可解析 422，未变成编码异常/500。OpenAPI 保留恰好三条 energy 方法、camelCase 必填价格与 `additionalProperties=false`。

| 验收项 | 第二轮结果 |
| --- | --- |
| AC-r2-001 / AC-r2-002 | PASS（源码/隔离 HTTP/假 session/SQL 编译范围）；F-001 已关闭。原有 current null、历史/分页、备注/extra、事务回滚、actor/脱敏日志、稳定排序断言随完整 200 项重新通过。 |
| AC-r2-003 | PASS；独立 read/manage、admin/supervisor/operator/unknown、未认证和 disabled route/OpenAPI 矩阵通过；无授权配置/权限平台增量。 |
| AC-r2-004 | PASS（静态/offline 范围）；本轮完整套件重新验证 recorder parity、约束及图；Core root hash 仍为 `f038e80badccf322292a9b4dca5bf2bb563bb5c15388f4745bc36fd02ca478f2`，后继 migration 与首轮独立 QA 副本同 hash。heads/history/offline upgrade/downgrade 使用上文已独立执行的未变源码证据，不重复在线操作。 |
| AC-r2-005 / AC-r3-001 / AC-r3-002 | PASS；完整 no_db、编译、链接、diff-check 与精确 allowlist 审计通过；旧公开配置测试保持两角色空数组/no_db、无 fallback/skip/xfail。首轮失败与 r1/r2 历史保留。 |

## 差异审计、限制与 handoff

最新 `handoff-files.json` 的完整 40 文件及 `F001-handoff-files.json` 的 6 文件均匹配当前源码。完整 `developer-incremental.patch` 逐 hunk 反向重构后全部吻合 `baseline-hashes.json`；返工 patch 的 6 文件也分别吻合 `pre-F001-handoff-files.json`。本次真实返工仅 API、Schema、API 测试、auxiliary README pair 和 tasks。修正后的 `r3-from-r2-files.json` 与本轮独立重算一致，包含先前遗漏的模块 PLAN/catalog 四处机械变动；PM spec、QA checklist、主协调六索引已按 writer 分开，未知/越界文件为 0。BE003、Core root、组合根、共享组件与依赖/lock 均受保护；QA 写入 checklist 前源码指纹无变化。本轮未读取真实 env，其既往保护 hash 属 DEV 输入，不伪称重新验证了运行配置内容。

两个 HEAD 已存在的 B11 死链保留；只声明本任务 24 条新增链接通过。结果发布后的六索引及模块 PLAN/catalog 状态/已有 checklist 链接由对应 owner 机械同步，QA 不越权修改。首轮 QA tmp、DEV tmp 和本轮 QA tmp 继续保留，供 Human Owner 审阅；清理归主协调者在依赖盘点后处理。

**第二轮 Verdict：qa_passed（获批 r3/r2 的源码验收范围）。Blocker：无。** F-001 已独立关闭，首轮 `qa_failed` 保留为历史。真实 MySQL upgrade/保存查询/约束实际执行、进程重载、当前前端联调、部署/生产/PLC 操作继续为规格明确的 deferred operational gate；本轮没有执行，也不由 fake session 或静态检查证明。采用前仍须显式准备 schema；权限不会自动授予，downgrade 丢失历史的风险保留。

交 Human Owner 最终验收；目前未收到或记录 Human Owner final acceptance。Verification 的唯一仓库写入为本 checklist，没有修复实现、修改其他角色事实或收回资源。

# Human Owner 最终验收（2026-10-13）

主协调者转递 Human Owner 明确回复：“当前任务我看起来没问题，我验收了。这个日期补充是新的想法。”据此记录 ARCH-BE-002 r3 为 `owner_accepted`，验收基于本任务已批准源码范围和上述独立 QA；用户观察属于用户报告，不记为 Verification 执行了 live DB/前端联调。此前首轮失败、返工和第二轮通过历史保持。

日期补充属于独立新需求，交主协调者另建 spec；没有并入本次验收或实施新小时规则。最终验收未改变真实 DB/运行 deferred gate，也不表示部署、发布或数据库操作已发生。

资源复核：DEV `/private/tmp/ARCH-BE-002-r2-dev`、首轮 QA `/private/tmp/ARCH-BE-002-r3-qa-9o27ws83`、第二轮 QA `/private/tmp/ARCH-BE-002-r3-reqa-j6nttyeh` 均仍存在，并承载本 checklist 引用的基线、完整/返工 diff、失败复现与独立测试原始证据。暂保留供验收追溯与后续任务边界核对；本角色未删除资源，后续回收由主协调者确认依赖及证据保存方式后处理。
