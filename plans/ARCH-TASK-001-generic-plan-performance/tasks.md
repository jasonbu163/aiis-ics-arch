Task ID: ARCH-TASK-001
Revision: r3
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: R3-QA-F04 字段删除历史核验修复已交付。当前正式工作树和自检入口见 r3 第六次 developer_handoff。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 通用计划与实绩、当前字段配置、同号实绩回写和受保护目标兼容
Owner: AIIS ICS Architecture 计划与实绩模块
Acceptance Chain Reference: spec.md 第 5、6 节、r2 第 8、9 节及 Development Lifecycle Workflow

# r3 Development 记录

2026-11-18。Human Owner 已明确批准精确 r3。获批草稿 SHA-256 为 `b62da9696a4641ca159b9dba6501bf2ee75aa139a8683ff8041619660683c893`，含批准记录的规格 SHA-256 为 `9307a205982c6952eb155c3bf91bfb84632670262c502b98cd5e52a2214cf3ff`。继续使用 r2 临时候选并保留下方 r2 暂停及 r1 记录。

> **阅读顺序**　以下候选、离线自检、只读基线、切换提案及前置复核记录均形成于获批切换前。文中的“未整合”“未执行”和“待批准”均指当时状态。正式整合、迁移及验证的实际结果见后文“r3 获批切换和合成验收”和“developer_handoff — ARCH-TASK-001 r3”。

## 精确候选与实施面（切换前记录）

候选在 `/private/tmp/arch-task-001-r2.FeZuND/source`，正式源码基线为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。候选保存 43 个修改与 10 个新增文件，逐文件 SHA-256 清单位于 `/private/tmp/arch-task-001-r2.FeZuND/candidate-inventory.sha256`，清单 SHA-256 为 `71a4835b7c6998f031ba38a55d1d7fdfc1636e603f6fce0c773821c6ad047d3c`。在候选目录运行 `shasum -a 256 -c ../candidate-inventory.sha256` 可复核内容。正式树未整合候选，只有本任务 Development 记录由 Development 写入。

- `backend/app/plc_facts/v2_config.py`、`backend/app/equipment_observation/profile.py`、`backend/common/integration/storage.py` 是 r3 新增的三个精确许可文件。只增加 `ae20b4d6f831`，设备观测同时延续两项设备时序参数必填。三个目标守卫和设备/监控探针源码逐字节未改。
- `backend/app/plan/` 内的 `api/routes.py`、`manifest.py`、`models/plan.py`、`schemas/workflow.py`、`services/async_workflow.py` 实现查询、部分写入、目标一致性、同号补建以及回写。
- `backend/app/performance/` 内的 `api/routes.py`、`models/performance.py`、`schemas/workflow.py`、`services/async_workflow.py` 实现部分实绩上报、人工反馈、订单快照、观察时间和同事务回写。
- `backend/app/task/` 内的 `api/routes.py`、`crud/async_records.py`、`domain.py`、`errors.py`、`http.py`、`manifest.py`、`models/__init__.py`、`models/fields.py`、`schemas/fields.py`、`schemas/workflow.py`、`services/async_fields.py` 实现当前配置、分组、历史快照、使用证据及删除。任务写入与配置变更以配置单例的数据库行作为首个锁，由同一事务持有直至提交。有意采用这一较简单的串行边界，因而不同任务号写入也可能在这一行上排队，实际 MySQL 竞争与锁时延待测。
- `backend/alembic/versions/20261118_1200_ae20b4d6f831_generic_task_r2.py` 的精确前驱为 `9d1f3a5c7e20`。保留原行、字段历史和下发/动作证据，补录原绑定版本的使用记录，转换计划空状态，适配两主表约束。迁移是受控前向步骤，提供目标、历史、可见依赖检查，不提供自动降级。
- `backend/tests/` 的 `test_generic_task_source.py`、`test_generic_task_flow.py`、`test_generic_task_migration_r3.py`、`test_generic_task_revision_guards.py`、`test_business_integration_storage.py`、`test_equipment_temperature_migration.py`、`test_legacy_acquisition_retirement.py`、`test_mapping_migration.py` 覆盖业务、HTTP、历史保护、精确 head 与版本兼容。
- `frontend-js/src/app/plan/` 的 `api/index.js`、`components/TaskPage.vue`、`components/TaskConfigDialog.vue`、`locales/en-US.json`、`locales/zh-CN.json`，及 `frontend-js/src/app/performance/` 的 `api/index.js`、`locales/en-US.json`、`locales/zh-CN.json` 切换当前配置和字段写入、共享/本地设置、固定生产状态列及可调列宽，保留签入角色限制。共享设置组件使用计划模块词条，两个入口共享后端定义和本机列宽。验证入口为 `frontend-js/tests/module-registry/generic-task.test.mjs`。
- `contracts/published/http-api/generic-task-workflow-v2/` 新增 `README.md`、`README.zh-CN.md`、`examples/requests.json` 及 `openapi.json`。同步 `contracts/README.md`、`contracts/README.zh-CN.md`，`backend/README.md`、`backend/README.zh-CN.md`，`frontend-js/README.md`、`frontend-js/README.zh-CN.md`、`frontend-js/FIELD_SETTINGS_GUIDE.zh-CN.md` 和 `CODE_INDEX.md`。已逐字节确认历史 Alembic 与 v1 合同共 34 个文件保持原样。

可见的后端源码中，原任务 profile 的版本下发映射只由 r1 退役路径消费。r3 不再读取该 profile 作准入或执行下发，设备/采集守卫自身保持独立。其它使用稳定键的 MES/SMA 映射仍需操作者逐一核对，字段删除界面说明了该要求。

## DEV 自检（切换前记录）

- 后端在候选 `backend/` 以 `env -i`、127.0.0.1:1 的无效 MySQL 占位目标、`TESTING=true`、合成凭据、任务专属 `UV_CACHE_DIR` 运行。命令为 `uv run --offline --no-sync python -m pytest -q -rs -m no_db -p no:cacheprovider --tb=short`，后接 `tests/test_generic_task*.py` 和以下测试模块：`test_business_integration_storage.py`、`test_plc_facts_v2.py`、`test_acquisition_data_browse.py`、`test_acquisition_source_registry.py`、`test_equipment_observation_r10_flow.py`、`test_equipment_observation_r10.py`、`test_equipment_observation_r8.py`、`test_equipment_temperature_migration.py`、`test_legacy_acquisition_retirement.py`、`test_mapping_migration.py`、`test_business_integration_api.py`、`test_mapping_api.py`。结果 394 passed、14 skipped，退出 0；SQLite 适配器报告 1 条已有 datetime 弃用提示。14 项跳过分别是 BE-010 已退役的实绩探针/写入/GET（8 项）、BE-006 已退役的实绩映射（3 项）、仅从清退前候选运行的 BE012 B（1 项）、必须显式提供独立数据夹具的采集浏览（1 项）和只在不可变 f85bea8 基线上运行的 BE003/60（1 项）。
- 候选 `uv run --offline --no-sync python -m app.module_preflight --project-root . --check-only`、`uv run --offline --no-sync alembic heads`、`uv run --offline --no-sync python -m compileall -q` 加本任务 Python 模块与迁移文件均退出 0。正式源码唯一 head `9d1f3a5c7e20`，候选唯一 head `ae20b4d6f831`。仅静态检查 Alembic 链。
- 用进程内 HTTP 和内存 SQLite 执行合成数据端到端，覆盖三组各 100 槽、部分合并、合法零值、目标冲突、开完工/观测时间、快照、状态覆盖、无变化实绩仍回写、过期修订和历史字段保护。通过故障注入验证主事务回滚后两张主表和使用记录均保持原值。另用 MySQL 方言编译断言 `FOR UPDATE` 锁顺序，该断言只证明生成的 SQL。实际 MySQL 写入、竞争和异步事务回滚待具体批准。
- 通过正常 FastAPI 注册提取 14 个路径、15 个操作、26 个 schema。测试对比实际路由的请求、响应、认证及 schema，并以 HTTP 重放七个合成请求。四个旧入口不进 OpenAPI，仍返回 410 且不触发数据库依赖。
- 前端在候选以合成空页面授权数组、`VITE_API_BASE_URL=/api/v1`、`VITE_FRONTEND_MOCK_ENABLED=false`、`pnpm_config_verify_deps_before_run=false` 运行 `pnpm test:modules`，89 passed，退出 0。包括实际 Vue setup 的部分提交、共享与本地设置、删除、配置冲突草稿、列宽和双语词条。若需浏览器视觉与交互指标，用获批的既有 dev API/Web 做真实检查。候选 `pnpm build --outDir /private/tmp/arch-task-001-r2.FeZuND/frontend-dist-final` 退出 0，存在 Vite 大 chunk 提示。所核对候选的 10 份改动 Markdown 共有 215 个本地链接通过。
- 较早集合额外运行 `tests/test_business_module_permissions.py`，其全量权限闭包审计对当前合同已有的免 Bearer `/api/v1/acquisition-data/options` 报错。将正式跟踪的 backend 复制到独立临时目录，以同一占位环境单跑原审计，对同一路径复现同一失败，退出 1。原审计与对应权限代码均保持，失败不计入本任务定向套件。
- 逐文件白名单、内容摘要及 `git diff --no-index --check` 审计通过。真实数据库未执行测试夹具、迁移、DDL 或写入，未触碰设备。

## 现有 dev 只读证据（切换前记录）

通过正式 backend 的本机 dev 配置、连接超时和脱敏输出进行了只读核对。执行 `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python /private/tmp/arch-task-001-r2.FeZuND/readonly_dev_preflight.py`。默认沙箱内连接返回 MySQL 驱动码 2003，socket 返回 errno 1。经工具批准的只读重试退出 0。脚本启动 `START TRANSACTION READ ONLY`，只执行 SELECT（含候选 `_dependencies` 和 `_history`），最后 rollback。未运行迁移、fixture 或种子。输出仅为身份匹配、数量和聚合值。

| 只读项 | 结果 |
| --- | --- |
| 真实目标 | 本机 dev 3307，实际 schema 与 dev 配置匹配，UUID 与 schema 的脱敏指纹 `b2c2262f59e55dc2`。MySQL 8.4.6，会话上海偏移 +28800 秒，唯一实际 head `9d1f3a5c7e20`。 |
| 目标配置 | 正式 backend 的配置文件启用 PLC Facts 与设备观测。两份文件的目标 UUID、schema 及 revision 均与连接实际值匹配。设备、监控旧业务时间集成在该文件中未配置开关、采用 profile 或采用证明。运行进程对环境变量的覆盖尚未确认，须在窗口前核对，不能按文件状态推断有效状态。 |
| 任务及配置 | 计划 2、实绩 2、下发记录 2、人工动作 0、配置状态 1、旧字段定义 10（v1 空、v2 有 4 项、当前 v3 有 6 项）。新版本台账和使用表尚不存在。计划旧空状态 0，同号已知目标冲突 0。 |
| 保护数据 | 采集历史 73、采集最新 6、来源登记 3。设备状态快照、过程记录、采集回执及能耗行各 0。计数是只读瞬时快照，切换时须重做基线。 |
| 迁移预检 | 历史定义、实际值/槽位及引用的只读检查通过，三份版本可判定；可见的视图、例程、事件、触发器和外键检查通过。实际执行前还需确认维护账号依赖可见性、外部客户端和历史时间证据。当前数据库会话时钟不足以证明全部历史行的原时区。 |

发现 8000 有两个 Python 监听引用，后端工作目录为正式 `backend/`，按历史记录具备源码热更新。5190 当前没有监听。正式源码、实际配置或服务均未写入或切换，候选构建未开监听。

## 可审阅的现有 dev 切换提案（切换前记录）

以下各步仅拟议。请分别审批维护、源码整合和迁移、两份 profile 修改、启动以及受控合成数据写入。恢复、永久清理另行决定。如果任何一项身份或证据不能满足，停止在实际数据库或服务操作前。

1. **冻结与基线。** 约定一次维护窗口和具体操作者，重认确切目标为当前已只读核对的本机 3307、脱敏指纹对应的 UUID 与 schema。重验 MySQL 8.4.6、+28800、单一前驱 `9d1f3a5c7e20`。用原启动环境确认应用真正采用的 profile、读写方和是否存在额外业务时间证明。停止现有 8000 对应的正式后端及外部调用方，以原终端正常停服。若执行时发现另有 Web 或数据库写入方，核清作用域和停写边界再继续。保持数据库进程在运行，维护窗口内暂停所有相关业务读写。数据库无应用事务后，在同一个只读一致性快照重跑身份、依赖、历史及数据摘要检查。检查视图、例程、事件、触发器、外键、消费者配置和下发历史，以及既有版本的时区来源证据。任何不能确认的依赖、历史定义/值/时区或目标冲突都须暂停并报告。
2. **备份和可恢复性。** 维护批准后，用现有私有客户端配置和具备所需权限的维护账号对确切 schema 执行逻辑备份。拟用 `mysqldump --defaults-extra-file="$TASK_R3_MYSQL_CLIENT_CNF" --single-transaction --skip-lock-tables --set-gtid-purged=OFF --routines --events --triggers --databases "$TASK_R3_SCHEMA"` 将 stdout 保存到事先指定的私有目录。先确认权限、快照范围和剩余空间。备份持久化到任务范围内的受控私有路径，权限 0600，核对退出码、有效大小、完成标记和 SHA-256，确认旧 Alembic、业务表数据、约束及对象定义可提取。用户选定同一 dev，当前不准备临时数据库恢复演练。若无法确认备份完整、恢复步骤或一致停写能力，停止迁移。私密备份两份源 profile、当前后端和前端运行配置以及 53 个目的源码路径的既有内容/不存在状态，保存当前正式工作树文件摘要和配置摘要，不记凭据。对任务表、全部历史配置和采集/设备保护数据以主键排序的规范化行序列计算私有 SHA-256，记录数目和摘要，真实行数据不进任务记录。旧计划若确有空状态，额外计算只按候选规则替换计划状态后的预期摘要并单列记录。
3. **整合源码与精确后继。** 服务及调用方停住后，复核候选清单 SHA 和全部 53 文件内容，在正式树逐路径确认任何并行编辑，发现冲突先停。只将清单文件从候选整合到正式树。保留正式树中的其它差异，不覆盖 `.env`、运行数据和 profiles，不推送 Git。以 `shasum -a 256 -c` 复核，复跑正式后端模块预检、Alembic 唯一候选 head 和前端构建。经迁移批准后，在正式 `backend/` 及原有 dev 环境中设置 `TASK_R2_SERVER_UUID`、`TASK_R2_SCHEMA`、`TASK_R2_OPERATION_ID`；仅有历史来源证据时设置 `TASK_R2_HISTORY_TIME_VERIFIED=Asia/Shanghai`。明确执行 `uv run --no-sync alembic upgrade ae20b4d6f831`，记录开始/完成时间、阶段、退出码和操作 ID。等待确认唯一实际 head 为 `ae20b4d6f831`，核对 schema 约束、版本台账（当前只读基线预期 3 行）与使用证据（当前已知 2 计划、2 实绩、2 下发，共 6 个引用），并确认旧值、批次和动作、版本和保护对象的行数/摘要一致。以执行窗口的实际基线为准。
4. **采用目标同步并恢复服务。** 批准后，把仍启用且与该服务器和 schema 精确匹配的两份 profile 的 `target.schemaRevision` 分别从 `9d1f3a5c7e20` 原子替换为 `ae20b4d6f831`，应用启动前验证两份文件的其它键与安全权限逐项一致。两份 profile 始终保留可恢复原件，启用开关、鉴权和设备时序不变。若确认已存在同库设备/监控业务时间采用证明，必须先核对其固定列摘要、报告和备份证据并单独批准重新验证与采用操作。原证明保留，不能通过改写版本冒充新目标采用。未采用或关闭的集成继续保持原样。三者一致且对账完成后，根据明确批准从正常入口启动 8000 后端（正式 `backend/` 的 `uv run --no-sync run.py`），在确认实际前端采用方式后才启动获批 Web 进程（若采用宿主源码模式，则为正式 `frontend-js/` 的 `pnpm dev`，既有 dev 预期端口 5190，启动前再次核实端口和代理 8000）。设备读写和其它外部调用保持暂停，先复核基本就绪和保护 API 只读行为。
5. **合成验证。** 写入批准后，记录唯一 `GTR3-<RUN>-*` 任务号、`R3-DEMO-<RUN>` 目标和字段组/槽位/双语标签。先筛选冲突，只有空槽才登记 `r3<Run>Product`、`r3<Run>Length`、计划/实绩本地项等合成字段，避免触达已有任务。分别测试计划先于实绩、实绩先于计划的默认和显式回填、版本/状态/时间边界、权限、停用/恢复、空及有值的历史使用保护；独立 HTTP 会话并发发送同号请求，读取及 SQL 对账须证明两表单行、同步符合任一实际顺序、不同槽位更新均保留。 同一窗口用两个已登记的不同合成任务号，各执行一条顺序对照请求，再各执行一条并发请求，记录客户端单次耗时、同批总耗时及在维护连接可观察时的锁等待。该探针有意低量且短时，不施压既有任务、不预设性能阈值。前后对账用户已有任务、旧配置/历史及受保护采集设备数据，实际配置变更仅创建或停用已登记的合成字段，不修改现有业务值。实际 MySQL 失败注入若需事务连接，另批准一次独立测试进程，仅对已登记合成任务打开事务，以候选服务在实绩 flush 与计划写回之间抛出合成错误，强制回滚并对账。正式服务无需注入或改源码。使用真实浏览器核对管理员入口、两组本地/同一共享设置、双语、列宽、刷新和配置冲突。对两种已启用采集和观测按现行授权做读、匿名/未授权拒绝及已有记录摘要复核。需真实写入接口确认时再单独审批合成来源，禁止对现场设备操作。发布态证据只记录脱敏结果，完成后再恢复其余调用。
6. **合成数据与清理。** 优先保留带标记且已登记的合成任务、字段版本及使用记录供 QA 对账。只有经同一写入窗口明确批准，才对已登记的合成字段执行停用；现有字段定义维持原样。合成字段一旦被使用便按规格保留历史。任务 API 无删除入口，后续如需移除某批合成记录，先审批精确主键清单、证据的保留办法和独立清理事务。禁止清库、批量删除、回退字段历史版本或回收其它任务资源。
7. **失败恢复。** 若迁移前失败，保持停写并核对未发生任何 DDL/写入。仅在确认旧数据库仍是 `9d1f3a5c7e20` 且无已接受新写入时，另行批准原源码和旧配置复原，再按原启动方式恢复。若迁移或配置切换进行中失败，所有来源和受影响读写继续暂停；记录实际 DDL、Alembic head、两张台账及主表约束、状态/值及文件摘要，保全当前数据库和新增数据。MySQL DDL 可能已经提交部分步骤，不能用事务回滚、降级命令或盲目重试代替恢复。依现况选择经批准的向前修复或按已审阅备份恢复，同步源码、目标 profile、采用证据和实际 head，重新做完整数据对账和保护验证，才能再次恢复服务。任何 restore、DDL 修补或重试需单独明确授权。

## 仍待执行（切换前记录）

候选整合、上述实际 dev 操作、正式 MySQL 事务与竞争、真实浏览器、保护数据前后摘要和已启用接口切换回归均未执行。两张主表的历史写入时区证据和实际进程环境覆盖须在窗口前确认，见补充复核。候选源码、精确文件摘要与自检产物保留在本任务临时目录，正式整合及证据审查结束后才回收。现阶段没有 `developer_handoff` 或独立 QA 结论。

## r3 补充 DEV 自检与切换前置复核（切换前记录）

### 候选前端 Chrome

执行 `node /private/tmp/arch-task-001-r2.FeZuND/browser/smoke.cjs`，使用本机缓存 Playwright `1.64.0-alpha-1789764292000` 和 Chrome `157.0.8103.79` 的独立浏览器上下文。脚本从冻结候选的 `frontend-dist-final` 提供临时静态服务 `127.0.0.1:18743`，用假管理员、固定合成行、字段和错误信封拦截全部 API。浏览器页面无外部请求、未访问正式 8000、现有 dev 库和真实账号。沙箱外运行使用工具的本机临时端口批准。

首轮退出 1，由中文新增按钮定位文字错误引起桌面后续步骤阻塞，且 390 px 时展开的既有应用侧栏压缩了主内容区域。仅修正临时探针的实际词条，并在窄屏操作既有侧栏收起控件。修正轮 20/20，增强轮重复核对最后一个非固定列和页面刷新后的列宽，仍为 20/20、退出 0。

两模块在 1360×900 和 390×844 四个组合均实际渲染。标题与操作、筛选、表格与分页三段按垂直顺序出现。计划和实绩各显示一项对应本地字段，两个共享设置显示相同九项字段。横向滚动到末端后，最后一个非固定的实绩列顺序表头进入可视区域。实际列宽从 190 px 拖到 235 px，页面刷新并重开后保留，恢复默认回到 190 px，保留打开的草稿。关闭再打开后草稿丢弃。合成 HTTP 409 显示配置冲突并保存当前草稿。实际点按语言按钮并双向切换中英文。增强轮 44 份请求由本机 mock 完整处理，页面异常、未知 API、外部页面请求均为 0。

脱敏结果和截图在 `/private/tmp/arch-task-001-r2.FeZuND/browser/`，`result.json` SHA-256 为 `ab03c7a573efe7105c73723b173718d25299015dba45ff0074a6af0f5b74fc19`。三轮均关闭各浏览器上下文、浏览器与自有临时静态服务。`lsof -nP -iTCP:18743 -sTCP:LISTEN -Fpcn` 退出 1且无输出，无剩余监听。真实 dev 浏览器与受保护 API 验收仍待实际批准切换后完成。

### 备份准备与历史时间

`mysql --version`、`mysqldump --version` 和 `df -h /private/tmp` 退出 0。两客户端均为 Homebrew arm64 9.3.0。验证备份客户端参数解析的命令为 `mysqldump --no-defaults --no-login-paths --single-transaction --skip-lock-tables --set-gtid-purged=OFF --no-tablespaces --hex-blob --routines --events --triggers --databases --help`，退出 0。只执行帮助，未转储 DB。

执行 `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python /private/tmp/arch-task-001-r2.FeZuND/readonly_backup_history.py`，退出 0。它对已核对的目标使用 `START TRANSACTION READ ONLY`，仅查询身份、权限、元数据、计数与时间证据，对照后 rollback。原生客户端认证探针是 `mysql --defaults-file=/dev/fd/<匿名配置读句柄> --no-login-paths --protocol=TCP --connect-timeout=4 --batch --skip-column-names --execute <只读事务 SELECT VERSION 与目标检查>`，以管道注入已配置认证，不在命令行、文件或输出中保留凭据。只读原生认证退出 0。 `SHOW GRANTS FOR CURRENT_USER()` 仅输出脱敏摘要，确认本目标 schema 的 `ALL PRIVILEGES`、全局 `USAGE`、未启用额外角色。Schema 共有 73 张可见 InnoDB 基表，可见视图、例程、事件、触发器均为 0，分区元数据未发现具名表空间，GTID 未开启。表和索引估算 2,932,736 字节，临时卷可用约 332 GiB，正式私有备份路径另在窗口确认。

当前无现成的命名备份选项文件、默认选项文件或登录路径文件。维护方案可用已验证的匿名描述符传递认证，或由授权操作者在实际窗口以 0600 私有选项文件提供同一受核对目标，备份输出同样以受控权限写入。因当前账户无全局管理权限，方案增加已验证可解析的 `--no-tablespaces` 以及 `--hex-blob`，在停写后复核无需要额外备份的表空间或不可见对象。现有 auth 探针使客户端登录可复核，实际转储成功、全对象可见性、备份落盘及恢复仍待窗口执行与核对。

历史核对使用 r1 [切换记录](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/operation.json)、[留存的 Owner A/B 探针记录](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/owner-ab-UAT49A9A1/browser-and-http.json)、r1 源码的 `DATETIME(6)` / `CURRENT_TIMESTAMP(6)`、来源时间转换和保留的已有应用日志。对应当前已存计划 2、实绩 2 与批次 2，任务身份集合与该归档测试一致，无额外批次。18 项 SQL 墙上时间与 r1 HTTP 快照一致。原带时区的实绩输入确认三个非空业务时间（两项观测、一项完工），两项开工和另一项完工仍为空；未补造。两项历史回执时间与带时区的归档响应相等，归档无该两项原始请求体，响应不算独立输入证据。

`performance_schema.variables_info` 显示最近全局时区设置为 `DYNAMIC`，设置时间早于 r1 迁移，也早于五张含时间的表的最早值。全局和此次会话为 `SYSTEM`，系统简称 `CST`，会话实测偏移 +28800 秒。r1 切换记录也为 +08。查到的 r1 应用引擎/会话源码未设置 `session time_zone`。这些事实支持正常 r1 写入使用上海时间。仍需确认现存记录的所有相关写入是否只经过该应用默认数据库会话；目前没有历史会话记录能排除覆盖、直接 SQL 或导入。保留的两条独立带时间戳的应用日志中，一条与 B 实绩最终更新时间相差 10 ms，另一条是 A 早一次更新，距最终状态约 29.88 秒。r1 HTTP 序列化会给无时区 SQL 值附上上海口径，因此只读值和 HTTP 展示一致也不能单独作为历史写入时区的证据。

| 表 | 行数与历史时间证据 | 对本次迁移的影响 |
| --- | --- | --- |
| `plan_main` | 2 行，创建、更新均非空，共 4 值。均与归档 HTTP 一致，仍无独立写入会话时间对照。 | 两主表的历史时间继续被当前 API 解释或筛选，4 值待确认。 |
| `performance_main` | 2 行，创建、更新共 4 非空值，B 最后更新时间得到独立日志印证，其余 3 待确认。来源时间有 3 个非空和 3 个空值，已按原输入对账。 | 3 个数据库生成值待确认，来源时间已有证据。 |
| `plan_dispatch_attempts` | 2 行，领取和更新共 4 个数据库生成值无独立时钟；2 个回执值匹配归档响应。 | 仅按原值保存并对账，候选不转换或重新解释历史批次时间。 |
| `plan_action_events` | 0 行，无现存历史时间。 | 核对行数和结构，保留历史表。 |
| `task_field_config_state`、`task_field_definitions` | 分别 1、10 行，创建及更新共 22 个数据库生成值；无逐值历史外部时钟。 | 候选按原值保留配置历史，以配置身份和版本建立使用证据，不解释或转换配置时间。 |

本次迁移/解释直接相关的未决时间是两主表 7 个数据库生成值。全局历史符合上海时区的旁证已找到，运行写入链仍未完全确认。执行前须通过已归档运行记录、写入者来源和数据库会话证据核定，不设置 `TASK_R2_HISTORY_TIME_VERIFIED` 以假定通过。若仍不能可靠核定，保持迁移阻塞；不调整、重置或删除任何历史行。批次、动作、旧配置等只保留的时间按原值对账，不新增独立时区验收前提。只读探针未写数据库、配置和正式服务。脱敏汇总 `/private/tmp/arch-task-001-r2.FeZuND/readonly-backup-history.json` SHA-256 为 `d772bc644be9c387ec57b5f17963490364be3e06579599ed8bb2dbe280ec24ac`。

候选根执行 `shasum -a 256 -c ../candidate-inventory.sha256`，53/53 一致、退出 0。冻结清单 SHA-256 仍为 `71a4835b7c6998f031ba38a55d1d7fdfc1636e603f6fce0c773821c6ad047d3c`。


## r3 获批切换和合成验收

2026-11-18，Human Owner 在审阅本任务的具体 dev 操作后回复“批准切换和合成验收”。已在获批本机 MySQL 8.4.6 dev 目标（端口 3307，脱敏指纹 `b2c2262f59e55dc2`）执行备份、正式源码整合、精确 Alembic 后继、两份匹配 profile 版本更新、恢复 API 和标记合成验收。保留原 2 个计划、2 个实绩、2 个下发批次及既有事实。业务合成任务和字段均走正式 API 路由。原始业务数据和环境配置未写入 Git。

### 历史时间、备份及恢复记录

- 两主表原有四行的 8 个非空 `created_at`、`updated_at` 均与已归档 r1 A/B 行身份和响应一致。只读检查 MySQL ROW/FULL binlog 的四个日志（7,850,460 字节），匹配 14 个相关行事件。以 `TZ=UTC` 读取，使用行事件对应事务的原始 `SET TIMESTAMP` epoch 交叉核对，再按上海偏移转换一次。4 个创建时间与对应 INSERT 匹配，4 个更新时间与相应行事件匹配，最接近的独立对照绝对误差为 435–971 ms，处于事件秒级精度以内。由此证实上文 7 个待定值的上海口径。binlog 无行查询标注，无法据此确认旧数据的客户端身份。此检查不落原始行或日志，也未写库。第一次全量读取遇非 UTF-8 输出，退出 1，按原始事件解析允许替换无关坏字节后成功。最终 `binlog_history_readonly.py --metadata-only` 及 `binlog_history_readonly.py` 退出 0，脱敏汇总 SHA-256 为 `e14487273077a2ffce7efb4d52169cda1ab3da3d3da3f60adcea185b1cd99452`。
- 首次短时停写时，普通账号备份受权限限制。维护账号 `retry_dump.py` 原生退出 2，MySQL 1109 指向 `information_schema.LIBRARIES`。在源码、配置和数据库均未改动时，以原命令 `uv run --offline --no-sync run.py` 恢复 8000，并核对 /health 为 200、旧 head 与数据仍一致。再在在线只读窗口用 `verify_dump_compatibility.py` 复现客户端 9.3.0 对 MySQL 8.4.6 的 `--routines` 兼容错误（原生退出 2）。维护账号确认有完整可见性且目标无 routines 后，改用 `--skip-routines`，保留 `--triggers --events`，结合 `--single-transaction --skip-lock-tables --set-gtid-purged=OFF --no-tablespaces --hex-blob`。修正后的在线一致转储及验证原生退出 0，预演 SQL 摘要为 `8169dbe680063fe8efdfcab0dff94fc5d3508b50629dbc6a6e285902776e75ac`。
- 再次验证 8000 原运行身份并暂停，`pause_final_backup.py` 退出 0。目标无其他连接工作，正式一致转储前后均确认 73 表、13 非空表，views、triggers、events、routines 均 0，摘要一致。SQL 文件 260,584 字节，包含 73 表定义、13 个非空表的 INSERT 和正常结束标记，SHA-256 `9fa873221a3bf5c6c637603dcad65312c625ec22b97f6540e648bd547a48dae8`。未执行还原演练。
- 在迁移和 profile 改动之前，以 `persist_verified_backups.py` 将数据库转储、两个 profile 原件、现有环境配置备份、43 个修改文件的原字节和 10 个原本不存在的路径清单复制到受控持久目录 `backend/data/maintenance-evidence/arch-task-001-r3-dev3307/`。目录为 0700、文件为 0600，逐项复制前后散列一致，命令退出 0。正式源码前像清单 SHA-256 为 `7d1095be0d7429f281a47cbd03c1a213f708e0b2eb5a2bf873dfa3115abda4f2`。该目录受 Git 忽略。恢复需要先停止任务写入、核验目标指纹和备份，以及另行批准实际恢复操作。MySQL DDL 非事务，迁移异常后以日志、版本和结构判断停写保全，不自动降级或重跑。
- `integrate_candidate.py` 仅复制获批 53 个源码文件，退出 0。在正式树核对工作树基线 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`、53 文件逐字节等同候选，无任务外源码改动。可从项目根运行 `shasum -a 256 -c backend/data/maintenance-evidence/arch-task-001-r3-dev3307/development-delivery-files.sha256`，交付清单 SHA-256 `71a4835b7c6998f031ba38a55d1d7fdfc1636e603f6fce0c773821c6ad047d3c`。正式 `uv run --offline --no-sync python -m app.module_preflight --project-root . --check-only`、编译、`uv run --offline --no-sync alembic heads` 与 `pnpm build --outDir /private/tmp/arch-task-001-r2.FeZuND/dev-window-20261118/formal-dist` 均退出 0。Vite 报已有的大块体积提示。
- 维护操作 `ARCH-TASK-001-R3-DEV3307` 以 `migrate_exact_r3.py` 运行 `uv run --offline --no-sync alembic upgrade ae20b4d6f831`，退出 0。实际唯一前驱 `9d1f3a5c7e20`，唯一现行 head `ae20b4d6f831`。启动命令才设置进程级 `TASK_R2_HISTORY_TIME_VERIFIED=Asia/Shanghai`。切换前紧邻 DDL 的只读查询确认历史计划无 NULL 状态。DDL 时间为 07:44:57.021842–07:44:59.604063 UTC。紧邻迁移前后逐表散列的 72 张旧数据表全部一致，旧 `alembic_version` 仅变上述一行。迁移建立 3 个旧配置版本与 6 条历史任务/批次引用使用证据。日志与 `migration-operation.json` 均已持久化，SHA-256 分别为 `e12e4e347de46918b33a26385221238a45ed02c389a5039c0f87f2df62e721dc` 与 `6ffcaeb668275a16cea4ee48e1122c61eb56ecdb5827222306c65c4d118e16e7`。
- `adopt_profiles_resume.py` 退出 0，逐项确认实际 server 指纹、schema、MySQL、时钟、唯一迁移 head 和进程启用配置匹配。两份已启用的 PLC Facts 和设备观测 profile 仅变更 `target.schemaRevision`。未启用的独立业务时间采用仍保留原状。恢复后的同项目 8000 以原 `run.py` 启动方式运行并验证 /health 200。既有 5190 Vite 已确认属于正式项目，保持运行并验证首页 200。合成运行产物与浏览器会话用完已关闭，临时 mock 端口 18743 已回收。保留候选和临时探针至独立 QA 复核完毕，开发备份目录按任务证据长期保全。

### DEV 自检覆盖

下列实时报告在上述受控目录下。开发执行脚本位于 `/private/tmp/arch-task-001-r2.FeZuND/`，以项目 `backend/.venv/bin/python` 运行。真实 dev 检查只以 GTR3 标记的三单及字段为测试输入。独立测试进程只注入内存等待或故障。

| 验收 | DEV 自检证据与限制 |
| --- | --- |
| R3-AC01 | 正式迁移、唯一前驱与后继、两份 profile 生效、53 文件交付散列和历史迁移/合同的原字节核对完成。三处兼容只增加精确 head，设备观测沿用现有参数要求。 |
| R3-AC02–AC04 | 候选与正式树内容逐文件比对一致。合成定向 suite 核查各原有/新增 revision、未知、多 head、版本匹配、数据库类型、目标与时区。设备观测覆盖两项时序参数及原权限。业务时间证明覆盖设备、监控、历史实绩格式，以及目标、固定列与时基等拒绝条件。实际 dev 未启用的业务时间采用保留原态。 |
| R3-AC05–AC06 | 已通过获批备份、切换、只读保护回归和真实 8000 的准入对照。认证设备组读 200，匿名受限读 401，已登记采集浏览与选项正常读 200，管理与机器探测继续受认证保护。无真实设备或采集写入。并行设备配置的只读对账另见下文。 |
| R3-AC07、R2-AC15 | 冻结候选后端 394 passed、14 skipped，前端 89 项通过和正式树 Vite 构建成功。跳过原因见上文，同环境旧权限审计对采集 options 期待 403，但既有匿名语义为 200，原基线可独立复现，不计入 394 项通过。正式 8000 OpenAPI 与候选定义逐项相符，14 路径、15 操作、26 schema。 |
| R2-AC01 | 本轮定向 SQLite 通过各组三类 100 槽、规范化、同号唯一、JSON 形状和重名语义。r1 独立 QA1 的 MySQL 历史试验证明两主表 JSON 每列可容纳 100 个逻辑值。本轮现有 dev 未填满 100 槽，未占用现有字段做满容量测试。 |
| R2-AC02–AC04 | 定向 suite 涵盖部分更新、省略/清空/边界值及拒绝整包。真实 HTTP 验证首次创建、标准计划过滤、0、false、可空字段、无计划先实绩、可选历史回填、真实一次性快照和非法混合包回拒。 |
| R2-AC05–AC08 | 定向 suite 验证独立时间戳、观察时间与序号、同步语义和处理顺序。实际 dev 正常 API 验证同号状态/值回写、同号并发创建和不同字段更新。无负载假设的两单并发 API 用时 23.24、25.87 ms，批次 26.06 ms，串行基准 14.87、14.74 ms，各写事务共用配置行锁。通过进程内故障钩子在已 flush 实绩后、写计划前令真实 MySQL 请求返回 503，正常 API 两表详情与只读台账均相同。 |
| R2-AC09–AC11 | 真实无 token 的集成路径、合法/冲突目标、普通 GET、null/停用/恢复及受保护设备权限。管理员保存匿名 401、操作员 403。定向测试涵盖分页、形状、时区、排序、版本无阻断。GET 不改变业务内容及使用台账。 |
| R2-AC12 | 冻结候选真实 Chrome mock 20 项覆盖双语、草稿取消、冲突保留、末列可滚动及拖动后 190→235→190 的本机列宽恢复。正式 5190/8000 以真实 Chrome 157 在 1360 与 390 px 访问计划与实绩，各 2 次，覆盖三段布局、共享和本地设置、合成记录筛选及双语。两次 admin 登录 200，实际发出 26 个真实 API 请求，浏览器未执行业务写入。 |
| R2-AC13 | 真实 admin API 拒绝已用共享字段删除 409，未用的两个独有探针分别成功删除并重新使用同一 `plan_local` 100 槽。真实 MySQL 两种先后在 `performance_schema.data_locks` 看到配置行等待，更新先行并发删已引用的 GTR3 字段为 200→409，合成字段及写入保留，用时 55.93 ms。删除先行并发尝试填写已删除的未用探针为 200→422，原任务保持已写值且没有被删除字段，槽位空闲，用时 25.29 ms。旧依赖、欠缺历史证据、停用及其它引用语义由定向 suite 覆盖。 |
| R2-AC14 | 实际迁移前后原 2 计划、2 实绩、2 批次、动作历史、历史配置、采集事实和其它受保护行按原值对账。实际旧动作返回 410，前端旧入口无调用。依赖异常/空状态路径以定向迁移测试补充，现有 dev 没有空状态。 |

实际 HTTP 脚本 `dev_http_acceptance.py` 最终退出 0（前两次仅只读/认证探测，分别修正通配符参数绑定和登录响应字段后继续）。`api_fault_and_used_field.py`、`browser/run-live-r3.py`、`delete_probe_and_reconcile.py`、`dev_delete_commit_races.py`、`final_runtime_protected_reads.py` 最终分别退出 0。留存合成三单 `GTR3-C9EF6A-A/B/C` 及三项已用配置 `gtr3C9EF6AActual`、`gtr3C9EF6ANote`、`gtr3C9EF6AInspection`。证据对应 `dev-api-acceptance.json`、`live-api-fault-and-delete-protection.json`、`dev-browser-r3.json`、`dev-api-delete-reuse.json`、`dev-api-delete-concurrency.json`、`final-registered-contract-and-reads.json`。本轮探针释放其临时槽位。

### 最终对账

最终 `final_reconcile_r3.py` 退出 0。直接对账发现两张设备配置空表在正式恢复后增加了 3 行。它们与 16:17:02 的 `POST /api/v1/equipment/metric-groups` 及 16:19:40、16:20:12 的两个 `POST /api/v1/equipment/metric-configs` 在相同目标时钟对应，HTTP 均 200。只读 binlog 确认是 3 次 INSERT，事件和 HTTP 记录的时间差分别为 85、671、334 ms。时间晚于本轮并发探针，探针未请求设备写路径。保留这 3 条并行配置记录，未判断具体操作者。未落原始 binlog 或行值。其余 67 个整表与合成前相同。两主表非 GTR3 各 2 行、原 2 批次、6 历史引用、3 历史版本、10 历史定义和 6 项原生效语义一致，登记的 GTR3 合成各 3 行，10 条合成引用。当前业务版本与配置修订号均为 14，53 文件一致，两个手动示例在两表均无记录。8000 和 5190 均复查 HTTP 200。脱敏报告 `dev-protected-data-reconciliation-final.json` SHA-256 为 `4b5988a7c83006d784df558a4937f46e9421ded7eef7afdd52014bde3d46a640`。

### 留给 Human Owner 的两个手动示例

以下两个订单在交付对账时从未提交。访问本机 8000 的 docs，向 `POST /api/v1/integration/plans/upsert` 传入 `Content-Type: application/json`，无需 Bearer。通过 API 建单。

```json
{"taskNo":"R3-MANUAL-9BDF-A","items":{"productCode":"DEMO-01","targetLength":120,"customerOrderNo":"0001"}}
{"taskNo":"R3-MANUAL-9BDF-B","items":{"productCode":"DEMO-02","targetLength":180,"customerOrderNo":"0002"}}
```

可先调 `GET /api/v1/integration/plans?productionStatus=new` 或 `GET /api/v1/integration/plans/by-task/{taskNo}`。用同一 API 服务模拟 SMA，向 `POST /api/v1/integration/performances/upsert` 各提交以下 JSON，不调用现场实例。

```json
{"taskNo":"R3-MANUAL-9BDF-A","items":{"completedLength":45,"currentSpeed":0}}
{"taskNo":"R3-MANUAL-9BDF-B","productionStatus":"completed","items":{"completedLength":180,"currentSpeed":0}}
```

重查 `GET /api/v1/integration/plans/by-task/{taskNo}`，A 应为 `running` 且已完成 45，B 应为 `completed` 且已完成 180。

## developer_handoff — ARCH-TASK-001 r3

精确交接为正式工作树基线 `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 上清单所列 53 文件及当前 Development 记录，未创建 commit。获批规格 SHA-256 `9307a205982c6952eb155c3bf91bfb84632670262c502b98cd5e52a2214cf3ff`，源码清单 SHA-256 `71a4835b7c6998f031ba38a55d1d7fdfc1636e603f6fce0c773821c6ad047d3c`。目标 dev 实跑 head `ae20b4d6f831`，8000 和 5190 可用。请 fresh-context Verification 按 r3 和继承的 R2-AC01–AC15 复核这一精确交付。须保留已有失败基线、满槽证据来源区别、并行设备配置写入记录、无恢复演练/现场设备操作及共享配置锁风险。最终验收由 Human Owner 在独立 Verification 后决定。

## 第二次 developer_handoff — ARCH-TASK-001 r3

2026-11-18，独立 Verification 首次退回缺陷 R3-QA-F01，记录 SHA-256 为 `14085a57b6f556343e954d610f9f7c7e88a64a743944ddb829aa977127607bf2`。该返工沿用已批准 r3 的 R2-03、R2-AC07、R2-AC12 及既有 dev 合成验收范围。以下为当前精确交付。上方第一次交接和迁移操作是历史证据。

- `backend/app/task/domain.py` 改用公共 `BUSINESS_TIMEZONE` 的固定东八区。三项实绩输入经共用转换规范化为 MySQL `DATETIME(6)` 墙钟值，输出附 `+08:00`。计划和实绩时间筛选沿用这一共用转换。保留显式偏移、精度、上下文空值与存储范围的原校验。
- `frontend-js/src/app/plan/components/TaskPage.vue` 的计划/实绩共用列表和详情显示 API 返回的墙钟秒值，避免再次套用地区历史夏令时。日期控件既有固定 `+08:00` 提交格式不变。公共日期工具及其他模块无本次改动。两份现有定向测试 `backend/tests/test_generic_task_flow.py` 与 `frontend-js/tests/module-registry/generic-task.test.mjs` 补回归。
- 测试先在原冻结副本添加后端与前端断言。后端新断言修复前 4 failed、2 passed，退出 1。夏季 UTC 和非 UTC 偏移输入存入错误墙钟，时间边界被历史本地平太阳时偏移，筛选同链路输出偏移错误。前端 Vue setup 独立复现把 API 的 `1990-07-01T08:00:00.123456+08:00` 显示为 `09:00:00`，退出 1。最初后端复现运行还补齐了仅测试用的环境占位值。已修正测试的 SQLite 同秒更新条件及实绩列表路由，按实际端点验证。
- 后端以项目 `.venv/bin/python -B -m pytest -q -m no_db -p no:cacheprovider --tb=short` 运行本文件首轮列出的同一测试范围，`env -i`、`TESTING=true` 与回环端口 1 的合成占位配置隔离现有库。HTTP/SQLite 文件 15 passed，整个定向集 400 passed、14 skipped，均退出 0；跳过原因及已存在的权限基线审计限制沿用上文。新测试涵盖 1990 夏/冬和当前，`-04:00` 输入，微秒，存储下界及低于下界的拒绝，两模块的日期区间包含下界、排除上界。前端 `TZ=America/New_York pnpm test:modules` 90/90，候选和正式 `pnpm build --outDir <专用临时目录>` 均退出 0，保留既有大块提示。
- 仅四份文件在正式树整合前后发生内容变化。基线仍为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，无新 commit。以原交接逐文件摘要守卫 preimage，再将四份文件写入。新正式清单 `backend/data/maintenance-evidence/arch-task-001-r3-dev3307/development-delivery-r3-f01-files.sha256` SHA-256 `e35290177b913b9327096305461a5e18ac5f119dfac059d2ecae517726e849ee`。候选副本与正式树 53/53 核对通过，首轮清单保留为历史。规格 SHA-256 仍为 `9307a205982c6952eb155c3bf91bfb84632670262c502b98cd5e52a2214cf3ff`。
- 正式 8000 由原父进程自动 reload，子进程 60664 接续监听。5190 原进程保持运行。两服务 HTTP 200、已注册 OpenAPI 仍与候选合同一致，dev 唯一 head 仍为 `ae20b4d6f831`。无 DDL、profile 改动、服务手工启停、真实设备调用或清理。
- 经正常免 Bearer API，仅对原合成 `GTR3-C9EF6A-C` 实绩提交时间。夏季 UTC、冬季 UTC 与夏季 `-04:00` 分别得到 `1990-07-01T08:00:00+08:00`、`1990-01-01T08:00:00+08:00` 和 `1990-07-01T08:30:00.123456+08:00`。只读 MySQL 核对三个 DATETIME 墙钟值一致，同号计划完整响应保持，重发是 `unchanged`，七位小数秒 422 且未改数据。两真实登录列表的 UTC、`+08:00`、`-04:00` 同瞬间筛选结果相同。HTTP 保护回归包括管理员配置、采集、设备及机器读接口。初次验证脚本因使用历史清单退出 1，当时无业务写入；首次实际提交后脚本发现合法新增的一条 v14 合成使用引用，调整脱敏断言后幂等复验退出 0。开完工及观测值保留在该合成实绩，以便独立 Verification 复查。全程无直接 SQL 业务写入。
- 只读再次核对旧计划 2、实绩 2、下发 2、动作、配置与历史使用记录，以及本次被保护的采集事实。两个预留手动订单在两模块仍共返回 4 次 404。3 个既有合成计划和 3 个实绩保持数量。合成使用证据 10→11，逐项核定新增仅为 C 实绩的当前 v14 引用。实时探针 `r3-f01-live.py` 退出 0，脱敏 `r3-f01-live-time-and-protection.json` SHA-256 `973da0bfddbad50e54706a303846ebe526bd53dfd0b035c1ca46badcf45f5653`。
- 真实 Chrome 157 使用两个独立上下文分别设 `Asia/Shanghai` 和 `America/New_York`，从正式 5190/8000 过滤 C 合成行。两上下文列表均显示 `1990-07-01 08:00:00`，详情三个历史值正确，无业务写入，浏览器已退出。命令为 `.venv/bin/python -B /private/tmp/arch-task-001-r2.FeZuND/browser/run-live-r3-f01.py`，退出 0，`r3-f01-browser-time.json` SHA-256 `b116bc2fbf1c75eea0e3a4032732eb2347b147ef06d31228537e879f9e50d005`。后续可清理返工临时构建与探针，时点为独立 Verification 确认不再依赖，持久日志与备份在任务原证据目录。
- 本次同规格重新交付给 fresh-context Verification。真实 MySQL 本轮仍无满槽测试，旧权限审计基线、共享配置行串行风险、无恢复演练及无现场设备操作的证据边界沿用第一次交接。此次只修复上述时区路径。Human Owner 最终验收待独立 Verification 完成。

## 第三次 developer_handoff — ARCH-TASK-001 r3

2026-11-18，独立 Verification 第二次退回 R3-QA-F02，记录 SHA-256 为 `2cf7f94ae1340e3662ed038771eb68bd1b2f12cafb69e03f43510a4e78d23025`。同一已批准 r3 的返工按 R2-01 和 R2-AC02 修正原始 JSON 数值精度。先前两次交接和切换证据保留。此节给出当前精确交付。

- `backend/app/task/http.py` 仅对使用 `Upsert` 派生请求模型的计划和实绩路由，用 Decimal 解码原文 JSON 的小数与科学计数形式。正常整数仍为 int。超长整数和超出 Decimal 指数表示范围的业务数字保留为可拒绝值，避免丢失原始范围信息。JSON 类型协商、语法错误、参数模型、权限依赖和异常信封继续由原路由处理。
- `backend/app/task/domain.py` 在数值转定点前按十进制数量级确认整数部分最多十位，对四位小数做等值检查，返回原约定的规范化字符串。超精度既不舍入保存也不下溢变零。极端非零指数直接按范围拒绝，校验过程中不展开长定点字符串。响应仍由原类型还原规则返回标准 JSON number。
- `backend/tests/test_generic_task_flow.py` 增加计划与实绩各自的集成、登录入口原始 HTTP 字节矩阵。验证原文 `9999999999.0001001`、`1e-400`、超界长整数（含 5,001 位）、正负极端指数、畸形 JSON、权限拒绝、布尔和数字字符串误用。每个拒绝同时核对备注与任务前后完全相等。合法绝对值边界、负值、科学计数、0、false、前导零字符串及显式 null 以原始字节提交，核对实际 JSON 类型和 SQLite 中的规范值。严格的顶层整数参数语义保留。
- 在无实库的旧候选先运行 `tests/test_generic_task_flow.py -k 'raw_http_numbers or raw_task_upserts'`，四个入口都把超精度包误收为 HTTP 200，结果 4 failed、1 passed，退出 1。候选修复的初次试验发现当前 FastAPI ModelField 应从 `field_info.annotation` 读取类型。限定实际请求类型后全套原始字节测试 5/5，整份业务 HTTP/SQLite 文件 20/20，退出 0。
- 后端继续使用首轮同一套模块，以 `/bin/zsh /private/tmp/arch-task-001-r2.FeZuND/run-r3-time-tests.sh .` 调用项目 `.venv/bin/python -B -m pytest -q -m no_db -p no:cacheprovider --tb=short`，以合成环境和回环端口 1 隔离现有库，405 passed、14 skipped、1 条原 SQLite datetime 适配警告，退出 0。F01 固定时区和日期区间仍通过；正式树以同命令重跑 F01、F02 及配套选择共 11 passed，退出 0。14 项跳过原因及原权限审计失败沿用首轮记录。前端 `TZ=America/New_York pnpm test:modules` 90/90；正式模块预检与 `pnpm build --outDir /private/tmp/arch-task-001-r2.FeZuND/r3-f02-formal-dist` 成功，均退出 0，保留 Vite 大块提示。
- 正式工作树基线为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb` 的未提交工作树。以第二次清单守卫正式树的 53 个 preimage，仅替换上述三个文件，另外 50 个摘要相同。正式树与返工候选逐项一致 53/53。`git diff --check` 退出 0。新清单 `backend/data/maintenance-evidence/arch-task-001-r3-dev3307/development-delivery-r3-f02-files.sha256` 的 SHA-256 为 `eb36d9abbfd7e9622b8cd5ec6944a1c20e2bea4f61eb5f154e041b27c6669158`。规格仍为 `9307a205982c6952eb155c3bf91bfb84632670262c502b98cd5e52a2214cf3ff`。
- 8000 原父进程自动 reload，子进程 73105 接续。5190 原进程保持运行。两服务均 HTTP 200，注册 OpenAPI 的 14 路径、15 方法及 26 schema 与原候选合同相同，dev 唯一 head `ae20b4d6f831`，没有迁移、profile 或设备改动。
- 真实 dev 仅针对已有 `GTR3-C9EF6A-A` 发原始字节边界探针。集成计划、集成实绩与登录计划共 18 次越界数值与 3 次畸形 JSON 均返回 422，两条人工入口匿名均 401。登录实绩的合法数字和拒绝场景由原始 HTTP/SQLite 逐项验证，无需在 dev 新增人工数字字段。实库验证无被接受的业务写入。两侧详情与备注逐次检查均不变，任务、字段配置和台账的全行快照前后相同，并保留 QA2 留存合成号。已核对原 2 计划、2 实绩、2 下发、采集事实、历史配置和 6 条原使用证据。正常采集读取 200、受保护采集管理和机器接口 401。用户预留两单共 4 次 404，未提交。命令为 `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -B /private/tmp/arch-task-001-r2.FeZuND/r3-f02-live.py`，退出 0。持久报告 `r3-f02-live-number-precision.json` SHA-256 `3a3f0d5474f7a6b6ee583d0e2bae0d1809aea7f2600bd1f90f4c63299857f19c`。
- 交 fresh-context Verification 复查精确 r3 和受影响入口。本轮无真实 MySQL 满槽、恢复演练或硬件验证，字段配置首锁和历史权限审计边界保持。返工临时日志和构建在独立复验确认无依赖后可回收。最终验收待 Human Owner。

## 第四次 developer_handoff — ARCH-TASK-001 r3

2026-11-18，独立 Verification 第三次退回 R3-QA-F03，记录 SHA-256 `f09042ae6caf12e6d5a4b6f3651bd2da19e91576fbc1ffb63637fe393dbfd30c`。同一获批 r3 按 R2-03、R2-04、R2-05 以及 R2-AC02/AC05 修复数值零的等值更新。此前交接和实际切换是历史证据，本节为当前精确交付。

- `backend/app/task/domain.py` 的 number 规则把数值零统一编码成 `0`，包括带负号、补小数、科学计数表示。字符串槽仍保留原文字，数值槽仍拒绝数字字符串，正负非零按原值区分。保留 F02 的边界和精确解析规则。
- 固定并核对目标、真实 head 和两份 profile 后，以 `START TRANSACTION READ ONLY` 查询两主表四个业务 JSON 列。按槽遍历，仅聚合完全等于 `-0` 的数量，并交叉核对当前和历史字段类型；上线修复前四列均 0 匹配，包括可归属历史 number 的槽。无负零存量需要转写，未执行数据归一化 SQL。实库合成复验后再次核对，四列结果仍完全相同。运行 `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -B` 加临时目录中的 `r3-f03-zero-inventory.py` 及 `r3-f03-zero-inventory-post.py`，两次退出 0。持久报告 `r3-f03-zero-inventory.json` 和 `r3-f03-zero-inventory-post.json` 的相同 SHA-256 为 `915b7f27d730408722e78da6b8549d3e9412fd648026e4b41a9cab5e1e8cb6a7`，未记录单条业务值。
- `backend/tests/test_generic_task_flow.py` 新增原始 HTTP 字节回归。五个零表示 `0`、`-0`、`-0.0`、`0.0000`、`-0e-400` 在计划、实绩与共享回写均保持原行及双方 `updatedAt`，每次实绩请求携带同一个微秒级 `observedAt`。正/负非零确实改变两侧时间，实绩同值而计划有真实差异仍只更新计划。验证数值槽拒绝 `"0"` 和 `"-0"`，字符串槽两者可区分。
- 先在修复前候选运行 `tests/test_generic_task_flow.py -k equivalent_raw_zero`，新回归复现 `updated`（期望 `unchanged`），1 failed，退出 1。修复后该业务 HTTP/SQLite 文件 21 passed，退出 0。仍以 `/bin/zsh /private/tmp/arch-task-001-r2.FeZuND/run-r3-time-tests.sh .` 调用首轮同范围定向集，项目虚拟环境、`TESTING=true`、回环端口 1 占位、pytest `no_db`、禁缓存，406 passed、14 skipped、1 条原 datetime 适配警告，退出 0。正式候选 F01、F02、F03 和接口测试选集 12 passed，退出 0。前端 `TZ=America/New_York pnpm test:modules` 90/90，正式模块预检及 `pnpm build --outDir /private/tmp/arch-task-001-r2.FeZuND/r3-f03-formal-dist` 均退出 0，沿用 Vite 大块提示。
- 正式工作树 HEAD 仍为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，未提交。以第三次清单逐文件验证整合前置内容，只更新领域规则和定向测试两份文件，其他 51 个源码/文档摘要同第三次。新清单 `backend/data/maintenance-evidence/arch-task-001-r3-dev3307/development-delivery-r3-f03-files.sha256` SHA-256 为 `b32cf52e8e76245adfff149804d480552a199f31909ff67570122bb18df19822`，候选与正式树 53/53 一致，`git diff --check` 退出 0。规格 SHA-256 `9307a205982c6952eb155c3bf91bfb84632670262c502b98cd5e52a2214cf3ff` 保持。
- 正式 8000 原父进程自动 reload，子进程 84077 接续监听；5190 为原 Vite 进程。两服务实际 HTTP 200，OpenAPI 的 14 路径、15 方法、26 个 schema 与候选合同一致。dev 唯一 head `ae20b4d6f831`，无 DDL、profile 改动、真实设备调用和清理。
- 业务写入仅用正常 API，在已有 `GTR3-C9EF6A-A` 实绩提交数值 0 建立同号计划与实绩零基线，保留该行的原观察时间和其他字段。随后两模块各 5 次原文数值零写入及共享回写均 `unchanged`，逐次完整读回的双方 `updatedAt`、观察时间和详情保持，四次将字符串零提交数值槽均 422。通过只读事务检查两个共享槽实际保存 `0`。正负非零和实绩同值时修复计划差异已由隔离 HTTP 回归验证。没有直接 SQL 业务写入。命令 `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -B /private/tmp/arch-task-001-r2.FeZuND/r3-f03-live.py` 退出 0，持久报告 `r3-f03-live-equal-zero.json` SHA-256 `1242d2d77d43e47735cd60a00815ab80d2e227d4b472be2d499f8d81d6c8a6e9`。
- 只读复核其他任务行、原 2 计划/2 实绩/2 下发、历史配置、引用、PLC 数据及 F01 既有合成时间不变。任务列表登录要求、匿名采集只读、受保护管理和设备机器读入口的状态均一致，两个预留手工例仍为 4 次 404。保留其它 QA 合成证据。
- 交 fresh-context Verification。已存在的旧全局权限审计失败、实际 MySQL 满槽证据来源、无恢复演练和现场验证及配置首锁的范围继续沿用。返工临时脚本、日志和构建待独立复验确认无依赖后回收。Human Owner 最终验收待独立 Verification 完成。

## 第五次 developer_handoff — ARCH-TASK-001 r3

2026-11-18，Human Owner 在真实页面澄清“两个模块本地字段设置按钮 都叫 本地字段管理；共享字段设置叫 共享字段管理，在计划管理和实绩管理下”。协调者与 PM 确认为获批 R2-11 的呈现纠正，沿用 r3。此前独立 Verification 已在源码交接边界暂停，记录 SHA-256 `b138a65826030964ea45fdbe5a97c2d0a1c2997f2f1fececebb1864e58d70690`。本节为当前交付，先前四次交接和 r2/r1 记录保留。

- `frontend-js/src/app/plan/manifest.js` 与 `frontend-js/src/app/performance/manifest.js` 分别注册 `/plan/shared-fields`（`PlanSharedFields`、`plan.shared-fields`）和 `/performance/shared-fields`（`PerformanceSharedFields`、`performance.shared-fields`）。各自侧栏、面包屑和标题使用本模块的双语命名空间。两个条目都声明 `requiresAdmin: true`，与直链共同复用现有 Registry 门禁。全局路由、注册器和角色授予机制未改动。
- 两入口动态加载同一个 `frontend-js/src/app/plan/views/shared-fields/index.vue`，用页面卡片显示配置。模块参数变化时重建 `TaskFieldEditor.vue`，从现有配置 API 拿最新定义并仅编辑 `shared_sync`。保存/删除沿用原接口；成功保存使用返回的新版本和字段定义，过期冲突保留草稿。取消丢弃草稿并重新读取，离开页面后再次进入重新读取。两个共享入口使用同一套本机列宽偏好。
- `TaskPage.vue` 移除列表共享按钮及共享弹窗实例，本地按钮统一为“本地字段管理” / “Local Field Management”。`TaskConfigDialog.vue` 继续用独立本地弹窗，复用同一张编辑表，只显示对应组。关闭销毁编辑器，保存成功关闭并重读列表，删除与修订冲突沿用原语义。四个现有 locale 文件对称更新文案及共享页标题。字段操作指南与 `CODE_INDEX.md` 同步实际入口和结构。
- Vue 与 Registry 定向测试覆盖两入口、共享定义、同源保存、草稿/冲突、列宽，以及两种单模块启用的装配。即使给 supervisor/operator 的 route-access consumer 提供显式 pageId grant，菜单和路由仍拒绝；真实配置解析器拒绝向非管理员配置该 pageId。改动测试文件为 `generic-task.test.mjs`、`page-access.test.mjs` 和 `registry.test.mjs`。候选初次测试因 VM fixture 的 import 处理及旧路由清单断言失败，按新增两条路由与既有 admin 顺序修正后重新执行。正式 `TZ=America/New_York pnpm test:modules` 92/92，`pnpm build --outDir /private/tmp/arch-task-001-r2.FeZuND/shared-page-final-dist` 含模块预检，均退出 0。构建保留已存在的 Vite 大块提示。后端文件无本轮更新，沿用第四次交接中 F01/F02/F03 与 406/14 的隔离自检证据。
- 正式 Chrome 157 对现有 5190/8000 运行四个管理员场景（1360/390 px 各中英文），从两个侧栏菜单打开独立页，共享定义与配置修订一致。两个路由均横滚到底验证末列可见，桌面实拖 190→235 px，切换保留 235 px 并恢复到 190 px。重载和切换重读，浏览器内拦截 409 后保留草稿，取消和切换后未带走草稿。四组均重开各自本地弹窗验证分组与取消。两个真实非管理员账户均看不到入口且两个直链均拒绝。验证初期发现 390 px 固定顶栏遮挡标题（旧卡片 y=144、标题 y=164、顶栏底 y=186）。将原任务列表的顶部位置计算提取到任务作用域 `useTaskPagePadding.js`，两类页面共用。复测 390 px 卡片顶 y=194、标题 y=214，标题可命中且页面不横向溢出。探针在 Element Plus 表头同步、可拖动目标及侧栏动画结束后测量。记录 64 次真实 API GET、6 次真实登录、4 次仅浏览器拦截的合成 409，真实业务写入为 0。命令为 `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -B /private/tmp/arch-task-001-r2.FeZuND/browser/run-live-shared-page.py`，退出 0，独立 Chrome 已关闭。脱敏证据 `dev-browser-shared-field-page-final.json` SHA-256 为 `cde2da8c8085cda1b2fbee6d2749885fbc1e824cc982384aaf8d5ce218555f52`。
- 8000/5190 都返回 200，原监听进程均保持。通过只读 HTTP 复核两个手工示例在两接口仍为 4 次 404。未连接数据库、执行 SQL、修改后端或 private profile，页面配置仅通过当前 API 正常读取。字段真实写入与发布未在本次呈现纠正中重新执行。
- 工作树 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，未提交。整合前以第四次清单逐个核验原 53 路径，四个此前清单外现有 manifest/测试路径与 HEAD 同字节，三个新增文件确认原不存在。两次整合共涉及获批的 16 个路径，首轮 59 路径清单保留作布局修正前证据。新清单 `backend/data/maintenance-evidence/arch-task-001-r3-dev3307/development-delivery-r3-shared-page-final-files.sha256` SHA-256 `ec18f34757a115dc3d5a4e3c61d9c71dd2eabbb710af62e459c02bbe82d5a6ae`，比第四次增加四个既有路径及两个新 SFC 和页面布局函数，共 60/60 一致。候选与正式逐项复核，`git diff --check` 退出 0。批准规格 SHA-256 `9307a205982c6952eb155c3bf91bfb84632670262c502b98cd5e52a2214cf3ff` 与独立 checklist 保持。
- 当前精确交付交 fresh-context Verification。旧权限审计基线、实库容量证据来源、配置首锁、无恢复演练和现场操作的证据边界保持。可在独立复验确认无需临时脚本后清理本轮候选构建与浏览器脚本。Human Owner 最终验收待独立 Verification。

## 第六次 developer_handoff — ARCH-TASK-001 r3

2026-11-18，独立 QA5 在第五次交付中发现 R3-QA-F04，checklist SHA-256 `ad6a213c69522b3bd1df6e33e1bf81c8f0ecb9bbfe6a8c1c6e8435a495d46516`。协调者与 PM 确认按已批准 R2-12/R2-AC13 返工。第五次的两个共享页面入口、浏览器和前三项缺陷证据仍在原节，本节为当前交付。

- `backend/app/task/services/async_fields.py` 继续在同一事务中先锁配置单例，核对修订、连续版本、定义快照和字段身份，然后查询适用历史版本的使用台账。已有使用证据直接 409。台账查询不能证明未用时进一步核对两张主表和历史下发批次。共享组检查两模块，本地只检查所属模块，历史批次始终检查。
- 对仍绑定含当前定义的历史版本、无法解释的绑定版本、缺失对应创建或批次使用行、持久槽值等证据，拒绝删除。较旧任务的创建版本未包含当前字段，但主行实际变更时间不早于该定义最近一次连续发布区间的起点时，缺少使用证据同样拒绝。历史定义曾删除并在间隔后重新发布时，以当前连续区间判定后续行变更。真实无使用记录且独立引用完整的旧任务不会阻止新字段删除。核验使用当前锁定读，查询失败返回 503，继续保留旧配置。
- 有效但主行未变的 POST 仍按规范记录使用台账，台账存在时仍按原语义拒绝删除。若旧任务缺少某次同值 POST 的使用行、其较早创建使用行还在，且任务、槽值、状态和时间均没有独立痕迹，现行持久模型无法将该选择性丢失与未发送 POST 区分。仍依赖同事务台账和迁移时已核实的历史基线，不宣称能检测无独立证据的数据损坏。此限制已回报协调者与 PM。没有新迁移、历史使用行改写或批量修复。
- QA5 的原始注入仅令 `FROM task_field_config_uses` 的查找为空，计划和原槽仍在。以 `/bin/zsh /private/tmp/arch-task-001-r2.FeZuND/f04-repro.sh /private/tmp/arch-task-001-r2.FeZuND/source/backend` 同环境复现原版为正常 409、注入后 200、计划值不再可见，断言退出 1；修复后为正常 409、注入后 409、计划值保留，退出 0。此为隔离 ASGI/内存 SQLite，注入不改真实台账。扩展红组在原版 11 failed、2 passed。
- `backend/tests/test_generic_task_flow.py` 覆盖两主表和历史下发、共享/各自本地、有效值与无值、未知/缺失创建证据、旧单后续值或状态写、旧单同值 POST 有台账和纯 GET 对照，以及配置查询失败 503、空槽删除后重用和先删后写拒绝。新增断言核对读回数据、修订号及无后续业务行。原有 MySQL 方言锁顺序检查继续通过，并增加三个历史源的 `FOR UPDATE` 语句检查。候选 HTTP/SQLite 文件 38 passed，退出 0。实际 MySQL 两种竞争结果沿用首轮已落盘的相同配置首锁证据，本轮没有重新执行实库写入或竞争。
- 候选运行 `/bin/zsh /private/tmp/arch-task-001-r2.FeZuND/run-r3-time-tests.sh .` 加首轮的同一后端定向集合，使用项目虚拟环境、`no_db`、端口 1 占位和 SQLite/合成依赖。423 passed、14 skipped、1 条既有 SQLite datetime 适配警告，退出 0。正式 F04 重放及定向 重放为正常 409、注入 409 且原值保留，退出 0。正式 `tests/test_generic_task_flow.py tests/test_generic_task_source.py` 为 50 passed，退出 0。前端正式 `TZ=America/New_York pnpm test:modules` 92/92，模块预检和 `pnpm build --outDir /private/tmp/arch-task-001-r2.FeZuND/r3-f04-formal-dist` 均退出 0，保留已有大块提示。已知旧权限全局审计和满容量证据来源沿用原记录。
- 模块边界核验以任务域的 SQLAlchemy Core 持久表合同选择历史主体，无对计划或实绩 ORM 的反向导入，也不改 Registry 或依赖声明。正式 `/bin/zsh /private/tmp/arch-task-001-r2.FeZuND/f04-preflight.sh backend` 源码 AST 和 manifest 预检退出 0。禁用后端 performance 或两模块均通过装配检查。仅关闭 plan 时，backend performance 依旧按原 `requires` 被拒绝。保留的历史表仍供删除时核对，表缺失或不可访问时拒绝删除。新增审计可能在少见的删除请求中扫描相关表，仍在首个配置锁内执行。
- 正式树 HEAD `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，无提交。整合前校验第五次 60 路径的逐字节散列，只有两个获批后端文件有变化。候选与正式树核对 60/60，`git diff --check` 退出 0。新清单 `backend/data/maintenance-evidence/arch-task-001-r3-dev3307/development-delivery-r3-f04-files.sha256` 的 SHA-256 为 `223220e938ac3a6360658e60a53b96b5474cb71bbafd0ff9470774151df9d8f1`。过往清单、spec 和独立 checklist 保留。
- 8000 原父进程 27134 自动热载入新子进程 15757，5190 的 Vite 仍为 85234，未手动重启。/health、OpenAPI 和 Web 均 HTTP 200，两个预留示例在两接口仍共 4 次 404。 本轮未执行真实字段删除、直接数据库连接、DDL、profile 更新或现场设备操作。两条预留手工任务无业务写入。开发交接给 fresh-context Verification，Human Owner 终验待独立复验。临时探针和构建以独立复验结束且不再依赖为回收时点。

## r2 与 r1 Development 历史原文

Task ID: ARCH-TASK-001
Revision: r2
Status: dev_blocked
Owner Role: Development
Allowed Writers: Development
Handoff: 返回协调者和 PM 审阅采集保护范围；未进入 fresh-context Verification。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 通用计划与实绩、当前字段配置和同号实绩回写
Owner: AIIS ICS Architecture 计划与实绩模块
Acceptance Chain Reference: spec.md 第 8、9 节及 Development Lifecycle Workflow

# r2 Development 记录

2026-11-18。获批草稿 SHA-256 为 `8a2c9775d135752e9ff8c5e0d9ec90cf19eb31922252a1c7e5da1c858e4b62ea`。含 Human Owner 批准记录的规格 SHA-256 为 `0a18d87f55b80a8c6c0610b8c9104ea30a5fec7ea8b41eeb63b984fb306aa0c8`。实际 Development 角色已启动，协调者发现规格纳入的采集保护无法在当前允许写入路径内完成后，指示暂停源码写入。

## 阻塞与解除条件

r2 新 Alembic 修订候选为 `ae20b4d6f831`，前驱为 `9d1f3a5c7e20`。PLC Facts v2 的 [版本白名单](../../backend/app/plc_facts/v2_config.py#L14) 只接受到当前前驱；[API 守卫](../../backend/app/plc_facts/crud/async_v2.py#L26) 和[同步维护守卫](../../backend/app/plc_facts/crud/sync_v2_maintenance.py#L21) 要求目标库 Alembic 修订等于采用 profile 的修订，且在源码白名单内。旧采用 profile 与迁移后目标不一致；仅更新 profile，新修订仍会被源码拒绝。这阻塞 R2-AC09、R2-AC14 和 R2-AC15 的采集保护验证。PLC Facts v2 源码和实际采用 profile 均超出 r2 允许写入范围。协调者安排 PM 准备最小必要修订，须获 Human Owner 批准后恢复 Development。现有 dev 的迁移、profile 操作、服务切换和测试写入仍须各自具体授权。

## 候选源码与进度

正式工作树基线为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`，已有其他任务未提交改动。只读检查发现 127.0.0.1:8000 的正式后端监听仍在，进程 cwd 为正式 `backend/`，按 r1 记录存在源码热更新。为保持现有服务未授权不变，候选写入位于 `/private/tmp/arch-task-001-r2.FeZuND/source`。候选使用从正式树复制的 Git 跟踪文件，链接复用现有后端虚拟环境和前端依赖目录，未复制私有 `.env`，未创建 Git 分支或 Git worktree。候选尚未整合到正式工作树。

| 候选路径 | 已写入的内容 |
| --- | --- |
| `backend/app/plan/api/routes.py`、`manifest.py`、`models/plan.py`、`schemas/workflow.py`、`services/async_workflow.py` | 普通计划读取、部分写入、同号状态继承与可选回填，保留旧历史列，隐藏旧动作入口并固定返回 410。 |
| `backend/app/performance/api/routes.py`、`models/performance.py`、`schemas/workflow.py`、`services/async_workflow.py` | 实绩部分上报与人工字段入口，订单快照、观测时间、同事务计划状态/字段回写，保留旧诊断列。 |
| `backend/app/task/api/routes.py`、`crud/async_records.py`、`domain.py`、`errors.py`、`http.py`、`manifest.py`、`models/__init__.py`、`models/fields.py`、`schemas/fields.py`、`schemas/workflow.py`、`services/async_fields.py` | 当前配置、分页和输入校验、字段组修订与删除、历史快照存在及使用证据。候选按配置单例行先加锁，串行化任务写入和配置发布，MySQL 实际并发与锁竞争待验证。 |
| `backend/alembic/versions/20261118_1200_ae20b4d6f831_generic_task_r2.py` | 显式后继候选。在线预检目标、时区、历史版本/槽及依赖后补录历史引用，转换计划空状态并调整两主表约束。MySQL DDL 非事务性，未在数据库执行。 |

前端、定向回归套件、合同候选、使用说明、代码索引以及实际 dev 操作与恢复提案仍待完成。现有 r1 源码测试引用旧请求和动作实现，未运行，恢复后需按 r2 正常入口更新相应断言，同步保留历史合同与记录。当前候选也尚未验证安全删除证据、旧数据兼容、历史时区、权限、实际合并和回写、故障回滚或两类并发先后。服务器仍生效的映射核查留待后续，外部 MES/SMA 映射需由操作者确认。

## 已执行的 DEV self-check

- 候选 `backend/` 内项目现有 uv 虚拟环境的 `.venv/bin/python -m compileall -q app/plan app/performance app/task alembic/versions/20261118*` 退出 0。
- 候选 `.venv/bin/python -m app.module_preflight --project-root . --check-only` 初次检出旧错误枚举与 manifest 不一致，更新后重新执行退出 0。
- 候选 `.venv/bin/alembic heads` 退出 0，仅输出 `ae20b4d6f831 (head)`，未执行 upgrade。
- 候选以 `env -i` 启动 Python 和 `create_app(testing=True)`，使用 `API_V1_PREFIX=/api/v1`、MySQL 占位地址 `127.0.0.1:1` 和合成凭据，通过 HTTPX ASGITransport 执行，不启动监听且显式替换 `get_db`。首次缺少 `API_V1_PREFIX` 导致设置校验失败，补齐后退出 0。OpenAPI 包含普通集成计划列表及字段删除，四条旧入口隐藏且对无效请求体仍返回 410，数据库依赖调用次数为 0。非法状态 null、开工时间 null、布尔序号和旧 `syncValues` 请求均返回 422 且包含字段定位。该检查只覆盖路由装配与请求拒绝。
- 逐字节比对正式树与候选确认 18 个已存在文件及 3 个新文件有源码差异，均位于上表路径。三份任务文件原始摘要分别核对，r1 `tasks.md` 的原字节保留在本节之后，原 SHA-256 为 `6f4f6a7f9d21b225c81891d2a4ab74f59f5cdd8dba16be2fe58c5d391d445bcd`。

没有连接 dev 数据库，未运行可建表、清库的 pytest fixture，也未改动服务、配置、现有数据、历史迁移、旧合同或 Verification 记录。候选保留以便按获批修订恢复，确认整合并核对有效证据后再回收。当前未形成 `developer_handoff`。

## r1 Development 历史原文

Task ID: ARCH-TASK-001
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: fresh-context Verification（第四次精确交接见文末；前三次交接保留）
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 通用计划与实绩、可追踪的下发回执及同号实绩回写
Owner: AIIS ICS Architecture 计划与实绩模块
Acceptance Chain Reference: spec.md 第 9、10 节及 Development Lifecycle Workflow

# Development 记录

获批准规格：`spec.md` SHA-256 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`。Human Owner 批准记录见规格第 10 节。本记录只表示 Development 进展，不是 QA 或最终验收。

候选：`/private/tmp/arch-task-001-r1-coordination.UaaX27/source`，候选 Git 基线 `bbb5c372b92f455105a9eaf7bc304b73ed044181`，创建时包含正式工作树中相关未提交源码；任务代码先在该候选中修改，正式任务目录只写本文件。正式 dev 的 API/Web 正在使用源码热更新，禁止在候选审阅及明确批准切换前修改正式实现、连接或写 dev、运行 DDL、重启进程或更改私有配置。

## 工作计划

1. 新建任务字段配置、资格与错误 owner，替换计划与实绩模型、事务及 HTTP 合同；验证注册、序列化和领域规则。
2. 编写单一后继迁移并保护 19 张旧空表外的对象；源码验证前驱、约束和保护条件，不连接数据库。
3. 切换两页与旧路由，配置字段、权限与双语、列宽；运行前端检查及构建。
4. 更新合同和操作说明，记录离线结果、候选差异及摘要，提交协调者审阅切换方案。实际 dev 验证及正式 handoff 待明确批准后进行。

## 准备证据

- 2026-11-11：核对当前规格 SHA-256，结果与获批准交接一致；原先无 `tasks.md` 和 `checklist.md`。
- 协调者只读复核 dev：MySQL 8.4.6、上海偏移 +28800、唯一前驱 `4e6a8b0d2f14`、68 个应用表，19 张旧表为空、21 个组内外键、组外无引用、新表名未占用。脱敏临时记录位于 `/private/tmp/arch-task-001-r1-coordination.UaaX27/dev-baseline-read.json`；这不是操作授权，切换时重新核查。

## 未完成与限制

实现和离线自检进行中。当前尚未执行迁移、合成 HTTP 闭环、浏览器验证或现场操作。

## 候选源码进展与离线证据（切换前）

- 计划、实绩及共用 `task` 候选覆盖字段版本和修订、按项目目标/版本登记的调用资格、`task.*` 错误、下发批次/人工动作、完整自动快照、人工值和同事务计划反馈。旧卷材入口与首页/报表不再注册；独立质量、设备、监控和采集模型保留。后继为 `5f7a9c1e3b25 <- 4e6a8b0d2f14`，没有执行 DDL。`TASK_INTEGRATION_ENABLED` 默认关闭；登录计划写入仍按私有项目 profile 验证目标版本和冻结字段。
- 页面仍使用 `plan.list`、`performance.list`，由 API 按绑定版本解释字段；管理员字段设置、上海时间、本机列宽与草稿、角色/状态按钮已接入。旧 dashboard、分卷、打印、旧质量及效率页面退出装配；API 角色和页面 grants 依旧分别生效。
- 正常 `create_app(testing=True)` 的 16 个本任务路径和引用 schema 已提取到 `contracts/published/http-api/generic-task-workflow-v1/openapi.json`；同目录有真实字段、A/B、领单/回执、快照、人工值及补建的合成 JSON 和双语走法。开放 API、数据采用及现场 agent 实施不由此推定。
- `UV_CACHE_DIR=/private/tmp/arch-task-001-r1-coordination.UaaX27/uv-cache uv run --no-sync python -m app.module_preflight --project-root . --check-only` 在候选 `backend/` 退出 0；公开占位环境 `import_model_packages()` + `create_app(testing=True)` 成功，元数据仅注册六张新任务表，未注册旧附属表；保护的独立质量模型仍注册。协调者将候选正常 OpenAPI 与切换前 dev 的 171 操作离线比较，候选当时 115 操作、69 个规范化旧方法退出且落在规格族内，抽样 23 个保护方法保留；此项为只读准备证据，不是运行验收。
- `UV_CACHE_DIR=... uv run --no-sync alembic heads` 输出唯一 `5f7a9c1e3b25 (head)`；候选关键 Python 与迁移 `compileall`、迁移 `py_compile` 退出 0；`git diff --check` 退出 0。协调者以 MySQL 方言编译对照冻结迁移与六个 ORM：12 条 DDL/索引语句结构差异 0。
- 候选公开占位环境 `localhost:1`、`TESTING=True` 的受保护无库集合（`tests/test_plc_facts_v2.py`、`test_acquisition_data_browse.py`、`test_business_integration_storage.py`、`test_generic_task_source.py`、`test_business_integration_migration.py`、`test_equipment_mapping.py`、`test_mapping_api.py`、`test_mapping_compatibility.py`、`test_mapping_service.py`）最近一次为 207 passed、29 skipped，日志 `.../dev-offline-tests2.log`。跳过项明确对应退出的历史卷材实现或未提供的旧公开样本；设备、监控和采集保留场景继续执行。另一组新合同/权限/四条保护集成入口为 83 passed、3 skipped，日志 `.../final-task-tests.log`。这些组存在重叠，不相加。
- 项目环境的 `pytest --collect-only -q -p no:cacheprovider` 收集 1085 项、0 收集错误。一次更早的全量 `-m no_db --maxfail=30` 在后续回归修正之前得到 722 passed、36 skipped、28 deselected、11 failed、19 errors；旧 fixture Git/历史源码输入缺失和退役前断言混在其中，不能解释为当前全集通过。协调者从 ARCH-ACQ-002 QA3 恢复公开历史 fixture；其定向历史检查中 2 passed、1 failed，失败为历史 QA3 profile 与当前 preflight 的 `system -> projection.policy_catalog:SnapshotPolicyCatalog` 私有导入规则冲突，未解决。历史检查不替代新流程验证。
- `pnpm_config_verify_deps_before_run=false VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' VITE_FRONTEND_MOCK_ENABLED=false VITE_API_BASE_URL=/api/v1 pnpm test:modules`：57 passed、0 failed；相同合成权限环境执行 `pnpm build --outDir /private/tmp/arch-task-001-r1-coordination.UaaX27/frontend-dist2` 退出 0，存在 Vite 大 chunk 提示。早期未设置权限数组的构建被配置校验拒绝；初次直接 `pnpm build` 的依赖预检查因网络/非 TTY 中止，未安装或删除依赖。两个模块中 47 个静态业务文案键对中英文均可解析；八份受影响 Markdown 的相对文件链接检查无缺失。
- 协调者只读检查了现有 dev：127.0.0.1:3307 MySQL 8.4.6、数据库时钟 +28800 秒、唯一前驱 `4e6a8b0d2f14`，19 张旧表空、21 个组内 FK、无可见组外 FK/依赖；维护账号读到无活跃事务和旧表活动语句。候选 `_target` / `_preflight` 的一次只读检查通过，新版候选加入数据库版本和时区自身护栏后，协调者再次在只读事务复核通过；没有调用 upgrade。切换前仍须重跑。正式 API 为 `backend/` 中 `uv -> run.py -> Uvicorn reload`、127.0.0.1:8000；Web 为 `frontend-js/` 中 `pnpm -> Vite`、0.0.0.0:5190 并代理 8000。PID 非稳定身份，执行时重新核对。
- 未执行迁移、真实 dev 写入、角色账户变更、真实 API/browser 模拟闭环、并发 MySQL 测试或设备操作。服务内 A/B 合成数据演练和内存并发重试仅是源码自检，不能证明 MySQL 锁、事务回滚、生产运行或现场 PLC 行为。

## 一次性 dev 切换与恢复提案（仅供 Human Owner 审阅；尚未授权执行）

1. 在指定维护窗口重认目标的 server UUID、schema、MySQL 8.4.6、上海时钟和单一 Alembic 版本 `4e6a8b0d2f14`；逐项重查旧表为空、新名称无表或视图占用、入向 FK、可见视图/例程/事件/触发器和旧客户端，包含仍映射 `plans` 的 C# 学习切片。查到依赖、写入者、非空表或身份不符则停在 DDL 前。保存批准记录、有效权限与配置的私有快照，以及旧 DDL/外键/保护对象证据。
2. 对现有 8000 API 和 5190 Vite，以端口、cwd 与进程父子链重新辨认，在其原终端停止；先停止旧写入方并确认数据库无活动旧语句。协调者仅在双方停止后将候选白名单整合到正式源码，逐路径比对本记录 SHA-256 并在正式入口重跑必要检查；不使用 `git reset --hard` 或覆盖其他任务改动。
3. 私有备份采集 profile 后仅把其 `target.schemaRevision` 从 `4e6a8b0d2f14` 改到 `5f7a9c1e3b25`；本次确认设备/监控业务集成开关关闭、无采用文件，若实际状态变化先停下。为受控模拟单独登记 `LINE-01`、`mes-01`、`ff-01`、`sma-01`，按合成 profile 并行配置 v1–v4，旧版本映射不改。实际文件路径、凭据和私有内容不写入仓库。仅在确认网络边界后按批准打开测试集成入口；不扩大现有真实账户的持久授权。
4. 候选迁移内建目标 UUID/schema/操作 ID、单前驱、MySQL/时钟、19 旧表为空、目标名与外部依赖检查。批准后在正式 `backend/` 且使用已核对的项目环境运行下列命令，其中三个值由操作者依据真实目标填写，不打印私有配置：

   ```sh
   TASK_CUTOVER_SCHEMA='<已核对 schema>' \
   TASK_CUTOVER_SERVER_UUID='<已核对 server UUID>' \
   TASK_CUTOVER_OPERATION_ID='arch-task-001-r1-dev' \
   uv run alembic upgrade 5f7a9c1e3b25
   ```

   迁移不禁用 FK 检查，按组内依赖拓扑清退且逐表输出进度；MySQL DDL 非事务性。旧表清单精确为 `plans`、`performance_main`、`performance_split`、`performance_transform`、`performance_lineage`、`performance_process_temperature`、`performance_process_tension`、`performance_process_speed`、`performance_push_down_record`、`performance_integration_receipts`、`performance_integration_observation_events`、`performance_mapping_receipts`、`performance_mapping_observation_state`、`quality_records`、`defect_records`、`print_records`、`production_reports`、`performance_targets`、`assessments`。独立质量三表及采集、设备、监控等保护表不在清单内。
5. 按原入口恢复 API（正式 `backend/` 执行 `uv run python run.py`）及 Web（正式 `frontend-js/` 执行 `pnpm dev --host 0.0.0.0 --port 5190`），重核 8000/5190 监听和代理。角色矩阵使用协调者只读确认可登录、角色匹配的现有 admin/supervisor/operator 测试账户，以及仅本次进程的 supervisor/operator grants；不创建新账户、不修改现有账户或持久授权。普通实际用户的既有访问不擅自增加。
6. 经批准后，按合同中的合成 `GT1-<RUN>-A/B` 及不同 RUN 的补建、并发和重试变体写入；配置六个字段，确认实际 v3，再按 AC09 发布 v4。登录管理员、supervisor/operator 的权限测试、两会话自动/人工合并、异常退回、序号重试、满 100+100 槽的受控回滚事务和采集页面/可授权样本回归均需记录请求、响应与数据侧证据。字段配置、目标和采集 fixture 的精确登记、保留或清理方式须在批准中明确；默认不清理既有数据。设备/监控集成先验证路由/当前关闭语义，若需真实采用或额外写入则另行批准。
7. 若任何 DDL 或启动中断，先停止全部写入，逐表核实完成阶段与 Alembic 版本，保全新结构中可能已有的记录并请 Human Owner 决定，不盲目重试或删除。仅在另获明确恢复批准、确认新结构无需保全记录后，按记录的逆依赖顺序移除本次新表，以已审阅旧 DDL 的父表优先顺序恢复旧空表和其 FK，再核对并恢复 Alembic 前驱、正式源码以及采集/业务 profile，最后启动旧 API/Web 并对账。任何非空或身份不确定情况先保全证据。

本次协调者保存的私有 `dev-preview-legacy-ddl.json`（19 DDL、21 FK）、`dev-preview-legacy-create-order.json` 和脱敏 `dev-preview-schema-evidence.json` 位于 `/private/tmp/arch-task-001-r1-coordination.UaaX27/`，只用于切换准备；保留至切换、必要核对及独立 Verification 不再依赖，之后由协调者按资源收尾规则确认回收。不得将恢复依据仅留在临时路径：切换获批后必须将实际步骤及必要脱敏证据持久写入本任务记录。

## 候选冻结前最终 Development 自检

- 最后一次候选 `backend/`：上述公开占位环境运行 `python -B -m pytest -q -m no_db -p no:cacheprovider tests/test_generic_task_source.py tests/test_business_module_permissions.py`，20 passed；其中包含 `commit_unknown` 在 commit、rollback、yield 依赖退出同时故障时保持、动作非法附加字段整包拒绝、PLC 序号不匹配返回 409，以及已持配置锁后的定义 `FOR UPDATE` 当前读构造。真实 MySQL 并发与故障回滚仍待运行时验证。
- 最后一次候选前端：同上合成环境 `pnpm test:modules` 57 passed；`pnpm build --outDir /private/tmp/arch-task-001-r1-coordination.UaaX27/frontend-dist3` 退出 0（仅大 chunk 提示）。候选 `app.module_preflight --project-root . --check-only`、针对本任务 Python 的 `compileall`、`git diff --check` 和未跟踪文本行尾空白检查均退出 0。
- 协调者在只读事务复核新版候选迁移 `_target` / `_preflight`：MySQL 8.4.6、+28800、前驱 `4e6a8b0d2f14` 与 19 旧表通过；未调用 `upgrade`。其三类现有测试账户只读登录结果为 admin/supervisor/operator 均 200 且角色匹配；未修改用户或输出凭据。
- 候选开发期间，递归删除三个旧模块目录的命令被自动审批拒绝，原因是可能覆盖并行未提交工作；命令未执行。后续保留未使用文件，仅定向替换被注册入口及必要模型，不对正式工作树作覆盖。
- `eventId` 在 MES 请求成功提交后写入有界结构化追踪：短且可编码的值及其 SHA-256，其他仅摘要；不记录业务值和完整报文。日志失败不改变提交响应。

以下仅为**源码候选可审阅**，不是最终 `developer_handoff`、QA 结论或 Human Owner 验收。待批准的切换、正式源码整合一致性和实际 dev 自检完成后，Development 才能补全正式交接并移交 fresh-context Verification。

## 冻结候选逐文件 SHA-256

候选基线 `bbb5c372b92f455105a9eaf7bc304b73ed044181`；以下是相对候选的 101 个变更路径及最终文件字节摘要。已独立复核路径集合与逐文件摘要均一致（差异 0），均在 r1 §8 allowlist；与正式树对应路径漂移 0。协调者生成的 `candidate-digests.json` SHA-256 `3c0f74dc50845551daec07ad8f0958ec13a3324edf02b9dc3f392ea1f0200ba5`，`approved-source-candidate.patch` SHA-256 `90a8aff9863c6bfef9571c33ac0b49e5dc84fb6e00fe721f48d08fff1b640cf6`；两者位于 `/private/tmp/arch-task-001-r1-coordination.UaaX27/`，仅为等待审阅与整合的候选文件。

```text
8a183e8c138a895372598d45f5102aaa7e4cf310940dc0a1172194a608e1bad9  CODE_INDEX.md
6578f0806e00220ea403afa79a10f49c98502b00fdced9734a554966894d11ff  backend/README.md
2e73c1e1953ce691efcb343e7ab908ca6580bbf988a81fdfe294230551b49d19  backend/README.zh-CN.md
ac4888c5766d79f3ef837fe91f9498c9c38cd799064e5a731dfed532c48cf799  backend/alembic/versions/20261111_1400_5f7a9c1e3b25_generic_task.py
8285c162d22106720da503ea57a1909828de9a01c456557c7d92967e8b21ba66  backend/app/dashboard/manifest.py
983f5da6d06d916fa5f58afd82385856dfc40d155df8b4c0c1af898afadd4192  backend/app/performance/api/__init__.py
4648d0630009dd76c92a3ce99cb16f21534d193b581a79e563d6478cb297c114  backend/app/performance/api/routes.py
801f9fd786fe126af6fd4aa939707a0454456a813d93fc3157a002b3146ac418  backend/app/performance/manifest.py
45dd627e58355c7dea6f827814fec5e5a51d218c60b4de1815195a88be888b6d  backend/app/performance/models/__init__.py
3da396afd115d713dbd4e14ebcfc1d52d58abd1269f3f3a0b1e31f5d672fbf40  backend/app/performance/models/integration.py
c754cf1058b9a8071c7843eef302528f98296ff0b6e6035ba476e248f4526d76  backend/app/performance/models/mapping_ingest.py
e89ae4f9ba04df04afdc2b67a7aaa7e74d410315c08ecb99dd74a6f9a43cf0c8  backend/app/performance/models/performance.py
ae2733d9674c8bceeffd3a318bb8df8757666a241bd1bf2e57d043142fa6951e  backend/app/performance/schemas/__init__.py
c5e50db91fe711bfc556e46911a681fa76db250e954232cc7341d99aa74baea2  backend/app/performance/schemas/workflow.py
d3ec8d9b98698e29ff463cc67bcf997eeacb0a771aa3060d10938c5020c65189  backend/app/performance/services/__init__.py
260c00326d8d91bd4c4a79a5a21346080a119a17aad201a4d2da31704b9a779a  backend/app/performance/services/async_workflow.py
2a433db348795dd7cdc8f8cb1695cd90001ae9d09fe99a1e75bad33d1bac0a81  backend/app/plan/api/__init__.py
f5bf55b0c6eec39f338e5c99bca9f6604e4c6d4d485e012c486317611517f312  backend/app/plan/api/routes.py
962118a689a142fc7319f6bb6a0976becae07c27c462a50047bce455f1e3281f  backend/app/plan/manifest.py
3987c81ea8568c25e595d327e096656e7d24cea5424fd3b92bdd46b5fdfe918b  backend/app/plan/models/__init__.py
28ca78ab3b2b3cddcbd04b63034c06125fe6d800ad0f6ccd4b962c8e10e51892  backend/app/plan/models/plan.py
d08c988cc24084c5c338f9f6155431c15e8599afff81226359662ab102e4a198  backend/app/plan/schemas/__init__.py
84e231b4460049a4808c73437fd4b2806673534b6c112d7c6cf511f099ba12d4  backend/app/plan/schemas/workflow.py
482257af792488d83a8e0bdd3ef3cea4f88b9c11ba88989a1ef10ccadc2e532b  backend/app/plan/services/__init__.py
3d4d7795725c9ded737cf3ef70010d832d787d7fbdff8d96497b3f101cb0eb44  backend/app/plan/services/async_workflow.py
3b29442ef6bb912f38bf6045f8ca621debac8ec031f56dfc60bfa8b5f705c492  backend/app/plc_facts/v2_config.py
348e3f2c1e93cbd88a5b522d3ed192d77f43a63dc99c2c099877252d21620543  backend/app/reports/manifest.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  backend/app/task/__init__.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  backend/app/task/api/__init__.py
3c612c424ae1ed732b7f778f26929320f7e99aba168e33c2ee990b8b02cfc1d2  backend/app/task/api/routes.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  backend/app/task/crud/__init__.py
371a86588ffb50878d2711528629fc029cb808cc42a7ea8ac478af05b86fe498  backend/app/task/domain.py
5547f6352f7c3e82ab0979b6d200b1fc3cdc199dc3d52923ce6927e7fe657119  backend/app/task/eligibility.py
45829f5d46f0fe6f18a6fa89291145c1f601f5f0deeb80f7779d67fcbeb17d02  backend/app/task/errors.py
ba10c5d70c05a018ebe829fb3ae6f6866b37a8e83d3c341943f55519a55601de  backend/app/task/http.py
9f8c378b0938c33273105f479783dee857187c5b71c5e4b910ddee57e75131d2  backend/app/task/manifest.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  backend/app/task/mocks/__init__.py
129c4d85bb8476ed74749436ed353a4dff8dcd8304a62256c3ee21146b3414e3  backend/app/task/models/__init__.py
d0a72bec6228dec49ca54fe5d18a4c9c061bea8f48e6ab5e9042067eb18a9f8f  backend/app/task/models/fields.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  backend/app/task/schemas/__init__.py
edced729a1bba159b64bf84fa1716b14c68cb524479892631dacb377e2ffb219  backend/app/task/schemas/fields.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  backend/app/task/seeds/__init__.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  backend/app/task/services/__init__.py
9fd56f332428d11a24df933a0cfe8f07199180700ed4a8833384dd8e4dc9fbbc  backend/app/task/services/async_fields.py
1ca498a87428dc916b7ff5a78187b87da2d70f60851b67c3f778507375e1e5fa  backend/common/integration/storage.py
316a64e5a356d5c15b443508174f805b7b9290dafbf19d7b5861976f1e5c226f  backend/tests/mapping_fixtures.py
edf0feababe91b4039905f819a21a98d1d5b90cb8a1d794f2cba387c26fdaec1  backend/tests/test_acquisition_data_browse.py
3f751e9a0db92ce6fe3d63e807c661d7e63e6677133846d57a7eeb2e6d1a359c  backend/tests/test_business_integration_api.py
1329d9cc144f1b803a5bfdd39d425ce6391c65cf56e909d0ee2726d94275a99c  backend/tests/test_business_integration_compatibility.py
bfb5a1e6511fa96e9e5d0fa7bbf3caf7f6a01cc4026af24770a7ba82da507b9d  backend/tests/test_business_integration_migration.py
ba49fa3c2f065699abb056ffbf0e33410b432693ba9e9f4b03d2d0bfd0bacca8  backend/tests/test_business_integration_provider.py
0186af3dd075a16fb851412cdaef1d89965e67ca7149f94b9af49d5b5fa6f9cb  backend/tests/test_business_integration_service.py
c5ef1d6812f1a2a5bc6efbc2d724bb3c5a6f28ddea3cc3a672769a2d411014d0  backend/tests/test_business_integration_storage.py
5d918b5037a7598ca151b2c3599c7616b8c865a5db2aa8f26b36d162ad030b58  backend/tests/test_business_module_permissions.py
0dbc0c7545881d4f32a427c3cff5133acf1f9f50bb9c1015a3ea4f60484f32d3  backend/tests/test_equipment_mapping.py
f6866d3f04bc42dce204e98804a2711a094a5ce7d485ff8d04a63f408fa35ad2  backend/tests/test_generic_task_source.py
434b6c18007da5d2b1d4c19c2a870f4fb470600d1e34fad9237052a730061072  backend/tests/test_mapping_api.py
5de2372deb90808f369f52b33af27ecf51aaf8165007c0b5a4e7c8dd969abce7  backend/tests/test_mapping_compatibility.py
5261b4198b11c65178aef76ca94deb7ba3674892227cc25f08672b29c0f94aa8  backend/tests/test_mapping_service.py
d79a90214de6c035772a7ae2118fca166043af20051a386b129ed621d3577f1a  backend/tests/test_module_registry.py
157f716341bdf212904fbce4ec6e62ed37535b65bcf0a33b3c4f2b574719c23e  backend/tests/test_openapi_router_tags.py
7605ce3dbb98901b01c3a85fe22b353f9f08ad113c531918fcbfc7bb29b1c8cf  backend/tests/test_performance_mapping.py
1afb94af4d3c8166de529f50b2c6e4cf1281e79915587d02e93976ec6c9a1c23  backend/tests/test_plc_facts_v2.py
39a408716ee86c3188f05ff169522f181a2f48728fa491b93601cfe937f72afd  contracts/README.md
dd814450b1609cfe1bb217a6f42277a97eb9e7fc66e93f2fdbdaafc14fe45108  contracts/README.zh-CN.md
83162321b73f52dbbe2efe384888e9cae632d6fc687d09a1ca36cc0379240df5  contracts/published/http-api/generic-task-workflow-v1/README.md
fad4164e6299ff46813501a3ba0fe37ed45f3fc8538b219c98226e8d9fc38a63  contracts/published/http-api/generic-task-workflow-v1/README.zh-CN.md
c26152c8505cff86e2eb6fe2bd0dd0fabdf43890c03898958b6f5be00c021261  contracts/published/http-api/generic-task-workflow-v1/examples/ack-a.json
d2fc3f6eb923d3f576c285ff5c85bcd4aa057d32dbf6b1aa533c1237cc30a708  contracts/published/http-api/generic-task-workflow-v1/examples/ack-b.json
2139ccb5ebe1bee47f16d117d572eaf5c08b9ffd08d23a2035369aa1860fb39c  contracts/published/http-api/generic-task-workflow-v1/examples/claim-a.json
0aa355dfa2b2ddbfba89c0faff6b60b5bac315a4fa502dcacd26150750526ee5  contracts/published/http-api/generic-task-workflow-v1/examples/claim-b.json
9a8486ea77b7f2e87c028e86efec12a432f3cfa85ba617eac19236f00be3c06c  contracts/published/http-api/generic-task-workflow-v1/examples/config-performance.json
eb00e4a1d04b7072f8968074d1d369a0f41213953e874478049e4f611a0ac1ac  contracts/published/http-api/generic-task-workflow-v1/examples/config-plan.json
2fc259b5c0c05f4498a4201bf29cf7dba2af4b656c64eb090e29b58620b78ebf  contracts/published/http-api/generic-task-workflow-v1/examples/manual-a.json
c5019bcadfc003151dc00a95363c6c1169f4720fe745ba47d591cf5af944aad1  contracts/published/http-api/generic-task-workflow-v1/examples/manual-b.json
f5fae74144320e8eca395acf216ba9bc5eb826566f862d5ebcc88d344bb90c34  contracts/published/http-api/generic-task-workflow-v1/examples/plan-a.json
940c5a92b5c8102460f57aa10cd2779d1971282af9ea778416fbf618c0bd66dc  contracts/published/http-api/generic-task-workflow-v1/examples/plan-b.json
f76e73cf036e5bbcd8e9ba4e020e130d5251c1d838328157e4ade780dc3b9e65  contracts/published/http-api/generic-task-workflow-v1/examples/private-project-profile.json
cea2be17773a3f8c3e6162c049c178edda45d5cdfed72e75d6acd1ebdcd0502f  contracts/published/http-api/generic-task-workflow-v1/examples/snapshot-a12.json
a9a6cfee6c0c26d2486bf45235322b08eeba283d324ab44b4dca1c9c5467e3fe  contracts/published/http-api/generic-task-workflow-v1/examples/snapshot-a13.json
921b55a16dfe06e3401a4361a25c382603919141c069e45b947af238af256800  contracts/published/http-api/generic-task-workflow-v1/examples/snapshot-b1.json
77f1d38267ec0fcee358f8e1dade9b4455886d3a2b2ae50d2c7914fdf1bd8b82  contracts/published/http-api/generic-task-workflow-v1/examples/supplement-b.json
dd2b7a0bd6b86c8e5355dcff8e0774295dfe2ede142a3f8788950012fe637c4e  contracts/published/http-api/generic-task-workflow-v1/openapi.json
bcdf3dec67957a7476846d015f7290912912c988ae1aebce10b3e4ebcc7a5ee6  frontend-js/README.md
c8949b41174f274b80781cd301eba833e2ce0e4f5f69e34c0d3fb990e8f10ee5  frontend-js/README.zh-CN.md
a08ac0d572fbee0b51366fcd0145cd158fce1832101153361a6625d3d9842949  frontend-js/src/app/dashboard/manifest.js
fbdf492f5d29d145b97b1f4f846f10ac1ecd567d3381c4c6250b22954de3baff  frontend-js/src/app/performance/api/index.js
950bb4ba3e1b3037fb81a072461604d1c4dff50c75b678123851b844002e9728  frontend-js/src/app/performance/locales/en-US.json
7dc1093b4906f3f474ef8a408df475888f3a78231dc096775fa9d0c0f001022b  frontend-js/src/app/performance/locales/zh-CN.json
35c44806c11da9753e019632a11fa24c57fa1a0ad37f7def07184f41a2ab0a44  frontend-js/src/app/performance/manifest.js
dca9a99c4045e46025f489c5a465fb3b97467f577ed23fd6d865070d4cb002ee  frontend-js/src/app/performance/views/list/index.vue
ed61c92e90d6e9e8f9e6c474f6012cd3af25171ee9508821c1c457c5bb36ef75  frontend-js/src/app/plan/api/index.js
ee16840453cc4f532678adc24cd1d4bca55b6caf7855fbcf2feea6508f503302  frontend-js/src/app/plan/components/TaskConfigDialog.vue
fa913badcd9d1573f061bfbee92c33e565fe4ff88aa631ffd0f95bc4b512e9af  frontend-js/src/app/plan/components/TaskPage.vue
470f758f0d3b6eed13e0d1737557ab68f738ae7563fa5037bf361bea94988b6f  frontend-js/src/app/plan/locales/en-US.json
b95c9d6d276abda23a5b6773e39bfe82210ed9ec2ce3275ede23bbf90c4c46c3  frontend-js/src/app/plan/locales/zh-CN.json
7afcd7dd418a3102b640a81476d9d29fafde46e19ba5df6f32aa464a9e151c95  frontend-js/src/app/plan/views/list/index.vue
e45ffcf515cd7bd9b2a874ebd2f92a1250fbe449baed32cf0b1cabdfa98efa4c  frontend-js/tests/module-registry/acquisition-data.test.mjs
1fae4de0003fe5bc7b6b6c1bf98b16a27819f665db2cf3a9b6fdaf88b03fa6d8  frontend-js/tests/module-registry/generic-task.test.mjs
34f29eae252e2924167dc28a260bd2b09a0e075a7a37b0d40f18f55958d4a94c  frontend-js/tests/module-registry/page-access.test.mjs
ba48ba239eff2f0850977054fdb1034381ba0793708e2fa653600403d9489415  frontend-js/tests/module-registry/registry.test.mjs
```

## Human Owner 切换与合成验收批准

- Human Owner 当前会话明确指示：**「批准切换和合成验收」**。授权对象为既有本机 3307 dev：复查并备份 19 张空旧表后从 `4e6a8b0d2f14` 切换至 `5f7a9c1e3b25`，协调者整合源码、更新采集 profile 的目标版本并恢复 API 8000 / Web 5190，使用现有三类测试账号和临时进程 grants，执行 `GT1` 合成任务及合成采集样本验收后按标记清理。
- Development 现在只准备私有窗口中的受控验证脚本与执行步骤；在协调者完成切换并明确通知就绪前不执行数据库或 HTTP 写入、不自行执行 DDL、不修改真实 profile、不停止或启动正式服务。验证和清理会逐项核对目标身份、测试标识、配置版本和实际数据，记录真实结果；批准不等于测试通过或最终验收。

## 2026-11-11 已批准切换后的 Development 验证进度

- 上述「准备」阶段已结束。协调者报告并记录：既有本机 dev MySQL `3307` 在切换前再次核对服务器身份、MySQL `8.4.6`、上海偏移 `+28800`、前驱 `4e6a8b0d2f14`、19 张旧表为空与无组外依赖，保存 DDL 后执行一次迁移至 `5f7a9c1e3b25`；候选 101 条路径合入正式工作树且逐项字节一致，正常 API `8000` / Web `5190` 已恢复。实际迁移、六张表元数据、50 张保护表结构和 11 张保护表内容摘要记录于 `backend/data/maintenance-evidence/arch-task-001-r1-dev3307/` 的 `operation.json` 与 `migrated-table-metadata.json` 等文件。该路径位于本机运行数据目录，不作为公开源码。
- Development 在正式 `backend/` 目录以其 `.venv/bin/python -B` 调用私有窗口 `dev-validation/launch.py preflight`，只读核对同一服务器身份摘要、schema、`3307`、MySQL `8.4.6`、上海时区、迁移 head、新旧表、六张表的列与索引、JSON/字符集/时间精度及约束，确认 `GT1-DEVFB8B5B-*` 未占用，退出 `0`。
- `launch.py exercise` 实际调用临时测试 API `127.0.0.1:18000`，以独立 profile 和临时授权完成、退出 `0`：空字段 v1/rev1 经管理员 API 发布至 v3/rev3；实际授权、未登录和缺授予拒绝；A/B 的计划重试、越权整包拒绝、优先级领取、并发同请求领取、冻结参数、接收报告与冲突；序号 12/11/12/13/14、重复与冲突、A/B 隔离、`0` / `false`；暂停、恢复、异常、人工核验退回、重新领取、取消；自动与人工并发；同优先级时间/ID 顺序；显示修订、停用共享槽后新旧版本并存和 v5/rev6 恢复。主 RUN 为 `DEVFB8B5B`，具体合成任务后缀 `A,B,S0,S1,X,Y,F,T1,T2,V4`。程序保存脱敏结果 `dev-validation/DEVFB8B5B-http-evidence.json`；首次尝试仅做只读权限请求时错误预期了 operator 在临时 plan grant 下应被拒绝，实际得到 200，未发生写入，原失败结果单独保留并修正测试假设后重跑；正常 `8000` 的未授予角色确实返回 403。
- `launch.py capacity` 在同一 dev 的显式事务内分别验证计划和实绩各 `100+100` 个 JSON 值及 255 个四字节 Unicode 字符的往返、`0` / `false` / 空串，以及非 object 和超过 100 键被 MySQL CHECK 拒绝；所有探针事务回滚，再查询确认容量行不存在，退出 `0`。
- `launch.py failure-server` 仅在 loopback `18001` 临时进程对标记的 F 单监听，`launch.py failure-check` 在第一条真实 SQL 更新后受控抛错；HTTP 为 `503 task.unavailable`，前后查询确认计划和实绩均未部分提交，向正常测试 API 原包重试得到更新，退出 `0`；该临时进程已停止。此为合成故障注入，不代表真实 PLC 故障或真实网络断连。
- 为严格符合 R01 的独立场景，另用独立 RUN `DEVFB8BS0` / `DEVFB8BS1` 的 B 单分别实际验证无回填 / 回填补建、重试与随后反馈，独立 RUN `DEVFB8BC` 的 A 单验证两个并发同一动作请求分别返回 `applied` / `duplicate`，改内容返回 409。临时 `18002` 只授予 supervisor/operator `performance` 相关权限，验证可读实绩配置但不可补建计划；admin 正例通过。该进程使用私有 profile 副本，v5 合成映射复制 v4，原 profile 未更改；进程已停止。命令 `launch.py independent-check` 退出 `0`。
- 协调者另以已登记机器来源提交与主 A 同号的合成采集事实：创建、同 ID 重报 duplicate、改内容 409、三点 latest 与一条历史及详情可读；正常 `8000` 既有两点可读而合成来源被拒绝。独立质量 GET、23 项保护方法、16 个新增 OpenAPI 路径对照及三个旧入口 404 的结果在同目录 `dev-acquisition-and-routes.json` / `operation-runtime.json`。该采集样本暂留给独立 Verification，Development 不清理。
- 协调者独立浏览器自检记录在 `backend/data/maintenance-evidence/arch-task-001-r1-dev3307/dev-browser.json`：正常登录及默认页、两列表/精确筛选、详情草稿刷新、表列拖宽/刷新恢复/重置、管理员设置入口与无变化保存、英文切换，A 的 `0` / `1200`、B 的 `50` / `false`，operator 列表和人工值及按钮权限。未调用 logout。Development 曾在共享 Chrome 窗口看到本机测试实绩列表，发现界面发生外部切换后停止操作；上述浏览器证据为协调者在独立 context 的补充检查。
- `launch.py final-checks` 退出 `0`：空格/大小写规范化同值重试保持 ID 与更新时间；跨目标重用领取请求号返回 409；未登记的 MES/SMA 与正常 `8000` 关闭状态下的三个集成读取入口返回 403；非法布尔类型与未知字段返回 422 且不改变原值；合成 B 的可空人工字段提交 `null` 后，实际数据库 JSON 的 `02` 键被移除，随后恢复 `false`。再次发布合成 v6 以停用共享 `03` 时，对既有 F(v3) 提交后续快照，计划反馈仍实际更新为 35；随后恢复配置至合成 v7/rev8。结果留在私有窗口 `dev-validation/DEVFB8B5B-final-evidence.json`。
- 上述 v7/rev8 为清理前状态。协调者停止临时 `18000` / `15190` 写入后，Development 先只读核对四个 RUN 的精确集合以及 v7/rev8 全部 34 条字段定义与预期快照，再执行受控事务：删除合成计划 13、实绩 8、下发批次 6、动作 6，删除 34 条本次合成字段定义并恢复验收前 seed `activeVersion=1` / `configRevision=1`。随后只读确认四个 RUN 在四张业务表内均为零、字段定义为零、head 仍是 `5f7a9c1e3b25`。`cleanup-tasks`、`cleanup-config`、`verify-clean` 均退出 `0`。脱敏记录分别为本机证据目录中的 `DEVFB8B5B-cleanup-tasks.json`、`DEVFB8B5B-cleanup-config.json`、`DEVFB8B5B-cleanup-verification.json`。协调者的 DAA 合成采集样本未由 Development 清理，暂供独立 Verification 使用。

## developer_handoff — ARCH-TASK-001 r1

- **交付对象。** 精确规格 SHA-256 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`；正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，当前 Git HEAD `bcafa89fa31bdf62329bced89baebc193323a739`，本任务实现是该工作树中的未提交变更，并保留其他任务的既有变更。创建候选时的 Git 基线为 `bbb5c372b92f455105a9eaf7bc304b73ed044181`。上方逐文件表即 101 条实施路径及 SHA-256；合入后的正式 101 条路径再次逐项计算，与冻结候选 101/101 一致，差异 0。候选摘要文件 SHA-256 `3c0f74dc50845551daec07ad8f0958ec13a3324edf02b9dc3f392ea1f0200ba5`，候选 patch SHA-256 `90a8aff9863c6bfef9571c33ac0b49e5dc84fb6e00fe721f48d08fff1b640cf6`。本任务没有暂存、提交或推送。
- **实施范围。** 计划、实绩、共用字段定义及资格、事务和 `task.*` HTTP 错误；六表模型与保护性 Alembic 后继；旧卷材路由/模型退出；保留的质量、设备、监控与采集能力；Vue 两列表、详情、字段设置、角色、双语、本机列宽；正常注册的 OpenAPI、A/B 示例与端到端接入说明。详细路径和源码 SHA 见本文件的冻结表，完整变更由正式工作树和候选 patch 共同定位。
- **DEV self-check。** 上文保留各离线命令与退出结果；实际 MySQL 迁移、元数据和正式服务记录、正常 FastAPI 合成闭环、受控事务故障、满槽回滚、角色与来源、独立 RUN、字段版本演进和协调者独立浏览器检查均在上节逐项列出。脱敏持久证据集中于 `backend/data/maintenance-evidence/arch-task-001-r1-dev3307/`，包括 `operation.json`、`migrated-table-metadata.json`、`operation-runtime.json`、`dev-acquisition-and-routes.json`、`dev-browser.json` 及各 `DEVFB8B5B-*-evidence.json` / `DEVFB8B5B-cleanup-*.json`。该目录为本机 ignored 运行数据，不进入源码。
- **当前环境与资源。** 正常 `8000` / `5190` 由协调者恢复并保留正常授权与默认关闭的任务集成；临时 `18000` / `15190` 为清理而暂停，协调者将按既定私有合成 profile 恢复，供 fresh Verification 重新从空配置开始。故障 `18001`、缺授权 `18002` 已停止。协调者的 DAA 合成样本仍留在 dev，随后由协调者按精确机器身份清理。私有窗口 `/private/tmp/arch-task-001-r1-coordination.UaaX27/` 包含候选源码、patch/逐路径摘要、合成 profile、临时角色 token、受控验证脚本及运行证据，仅为后续 Verification 和回收使用；其凭据不写入源码和任务记录。协调者应在独立验证、证据持久化、采集样本清理及使用进程退出后，核对归属并回收该任务窗口；不可覆盖真实配置或其他任务资源。
- **限制与后续。** 旧版历史 QA3 profile 与当前私有导入 preflight 的一项交叉样本仍未解决；早期全量 no-DB 探查并非通过结果，具体数量和限制见上文。浏览器证据为协调者补充的实际检查，不替代独立 QA；真实 PLC、SMA、CA/FF 程序、现场设备、生产数据、持续运行和部署未验证。该 handoff 仅表示 Development 已实施并记录自检；请协调者按 lifecycle 显式启动 fresh-context Verification，对精确 r1、正式工作树和 dev 执行独立检查并由 Verification 写 `checklist.md`。最终接受仍由 Human Owner 决定。

## QA1 返回后的 Development 返工

独立 Verification 的 `checklist.md` SHA-256 `a9e72c9e907c99e068b69301913481d5a5ff4889450d19b4587e8173abd18772`，verdict `qa_failed`。协调者于同一 r1 下返回 QA-F01 配置修订冲突优先级、QA-F02 时间输入边界和 QA-F03 目标键精确过滤；本轮只修改已批准的相应源码与必要回归，保留 QA1 原文、原证据及 dev 合成夹具，完成后重新交接。

- **QA-F01：** 管理员保存先检查 `configRevision`，再检查业务版本。两者均过期返回 `task.config_revision_conflict`；只有业务版本过期、修订号新鲜时返回 `task.field_version_conflict`。两种情况和仅修订过期都有无数据库回归及实际 HTTP 检查。
- **QA-F02：** 共用 `TaskDateTime` 在 Pydantic datetime 转换之前对两列表的 `createdFrom` / `createdTo`、现场回执 `ackObservedAt`、实绩 `observedAt` / `startedAt` / `completedAt` 校验原始输入：必须是带明确时区的日期时间字符串，小数秒最多六位。有效输入仍由 Pydantic 解析，原有上海转换保持；`+08:00` 与相同瞬间 `Z` 在实际列表得到相同结果。查询和请求体保留 `string` / `date-time` OpenAPI 形状。共享类型通过 `task` manifest 显式导出给依赖模块。
- **QA-F03：** 两列表对 `targetKey` 先调用既有 ASCII `identifier` 校验，再使用原样等值查询；尾空格及其他非法键返回 `422 task.invalid_request`，合法大小写不被规范化。
- **回归。** 新增针对配置冲突优先级、四个请求体时间字段、两个列表的两个时间参数及目标键的无数据库测试。修复前定向探针分别复现时间/筛选五项失败及配置错误键一项失败；第一次组合回归为 `129 passed, 10 skipped, 1 failed`，唯一失败是新增测试桩遗漏模拟返回的 `dispatchId`，补齐后该测试独立通过。正式 `backend/` 以 `TESTING=True MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 PYTHONDONTWRITEBYTECODE=1`、已提供历史公开 fixture 和专用 `/private/tmp` basetemp，运行 `.venv/bin/python -B -m pytest -q -m no_db -p no:cacheprovider ... tests/test_generic_task_source.py tests/test_business_module_permissions.py tests/test_business_integration_storage.py tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_openapi_router_tags.py --tb=short`，结果 **130 passed、10 skipped，退出 0**。`.venv/bin/python -B -m app.module_preflight --project-root . --check-only` 退出 0；`git diff --check` 和本轮未跟踪文件逐行空白检查无错误。原历史 QA3 私有导入规则的已知限制仍如首次交接所述，本轮不宣称全量测试通过。
- **实际 dev 复验。** 协调者重启 loopback `18000` / `15190` 后，Development 在保留的 QA1 v5/rev6 和 `GT1-QA92A69E81-A` 上，仅执行读取及必然拒绝的请求：两类过期修订和仅业务版过期分别返回预期 409；两列表的数字时间、缺时区、七位小数、非法偏移和尾随垃圾均为 422；合法 `+08:00` / `Z` 时间均命中相同合成记录；非法 targetKey 为 422、`LINE-01` 命中而 `line-01` 为空；四个请求体时间字段对数字、无时区、过精度和非法偏移均为 422。复验前后计划、实绩和字段配置内容一致。命令 `.venv/bin/python -B /private/tmp/arch-task-001-r1-coordination.UaaX27/dev-validation/rework_http.py` 退出 0，脱敏证据 `backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-dev-rework-http.json` SHA-256 `b4cb876edda204f8da020ff4a4aeaf2cf1f32b682667505de41e4a8de324d5ca`。正常 `8000` 与测试 `18000` 的运行中 OpenAPI 均为 200，16 条已发布任务路径和 12 个引用 schema 差异 0；未修改合同文件或执行迁移。

## 第二次 developer_handoff — ARCH-TASK-001 r1

规格和 QA1 checklist SHA-256 仍分别为 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`、`a9e72c9e907c99e068b69301913481d5a5ff4889450d19b4587e8173abd18772`。正式交付仍为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的未提交工作树，HEAD `bcafa89fa31bdf62329bced89baebc193323a739`；没有暂存、提交或推送。相对第一次交接的 101 条实施路径，91 条 SHA 不变、以下 10 条改变，没有新增实施路径。每行依次是路径、第一次交接 SHA 和第二次交接 SHA：

```text
backend/app/performance/api/routes.py 4648d0630009dd76c92a3ce99cb16f21534d193b581a79e563d6478cb297c114 d693a228c359d7b52245217bef3007ceaed24f92aa680095c588edc5097f5634
backend/app/performance/schemas/workflow.py c5e50db91fe711bfc556e46911a681fa76db250e954232cc7341d99aa74baea2 3723a0fbb4ff5bc102ccab8dbfef0b1cae4f512735d660a5cea229e114a94fe6
backend/app/performance/services/async_workflow.py 260c00326d8d91bd4c4a79a5a21346080a119a17aad201a4d2da31704b9a779a 2fe9c6d323ef27520ff2d761311b9f9fb41b6fd5fa320b1b750c02645534e520
backend/app/plan/api/routes.py f5bf55b0c6eec39f338e5c99bca9f6604e4c6d4d485e012c486317611517f312 c85a5c4e8d6ebe7740d7b430c82e51f9b5c3cf0eb658f54fb074473fe89358f6
backend/app/plan/schemas/workflow.py 84e231b4460049a4808c73437fd4b2806673534b6c112d7c6cf511f099ba12d4 675b68b456a7d05565a2fa168d5d013a73106cbd82d5cbbaa18beda222551f74
backend/app/plan/services/async_workflow.py 3d4d7795725c9ded737cf3ef70010d832d787d7fbdff8d96497b3f101cb0eb44 367b8400d59c503a507ea7807967a5e91b82a4b7bec38bf3efbc0f69c8681006
backend/app/task/manifest.py 9f8c378b0938c33273105f479783dee857187c5b71c5e4b910ddee57e75131d2 0d0eba571eada4f094a00d9dfb85a523dcd111e60705c1eae37bc480936ad4fd
backend/app/task/schemas/fields.py edced729a1bba159b64bf84fa1716b14c68cb524479892631dacb377e2ffb219 b496296ad66d828e4bf0461a99497d1a31e89d061d5758fd68432a3991b52f84
backend/app/task/services/async_fields.py 9fd56f332428d11a24df933a0cfe8f07199180700ed4a8833384dd8e4dc9fbbc cfdd4fa02dbface43d824e0b602384851d10f69cf0a4e6ffdaa139d3923418fd
backend/tests/test_generic_task_source.py f6866d3f04bc42dce204e98804a2711a094a5ce7d485ff8d04a63f408fa35ad2 ac16c4216b2946c1776a88465ec14504343fc9c4b5e9cf4edc763f0fbaadb8ce
```

协调者已保存第二次累积 101 路径摘要 `backend/data/maintenance-evidence/arch-task-001-r1-dev3307/handoff2-source-digests.json` SHA-256 `5c8b9cda15bbca659100679abc01dc8819fd3b94e1fcd42e9b82215a534170c3`，对应 patch `handoff2-source.patch` SHA-256 `65814e55dc9d09549c15edd7861be14be8dce51030b2d8b4e077d537a321d96e`；协调者报告反向适用性检查通过。

QA1 的七条合成任务、v5/rev6 配置与已登记 DAA 合成样本暂保留，`18000` / `15190` 临时验收进程由协调者管理，供 fresh-context Verification 复验；其后按精确 RUN 和采集身份统一停写与清理。首次交接列出的临时源码、私有凭据/配置、旧表 DDL、测试构建和证据资源仍按其保留/回收条件管理。请独立 Verification 复核此精确工作树和三项返工、保持已通过范围的必要保护回归，并独立更新 `checklist.md`。本记录不改变 QA1 verdict，不构成 QA2 结论、现场联调或 Human Owner 最终验收。

## 第三次 developer_handoff — ARCH-TASK-001 r1 共用列表布局

Human Owner 在实际计划页提出两项界面纠正：恢复「标题及操作、筛选工具、表格与分页」三段结构，并将上海时区说明移到第一段标题旁问号，以鼠标悬停显示。两列表共用 `TaskPage.vue`，因此计划和实绩一并调整；保留原 API、筛选语义、按钮及 `workflow.timeZone` 双语键。此为已批准 r1 AC10 的界面纠正，不修改规格或扩大旧打印能力的范围。

- **实现。** 标题使用 `BaseCard` 的 `#title`，在原标题旁复用 `QuestionFilled` 和 hover/focus 提示；筛选区采用自适应紧凑网格、底部分隔线，桌面查询/重置靠右、窄屏可换行，日期输入约束在网格内；表格与分页分别支持横向滚动。按现有采集页面范式读取 main、header 与页面根的实际几何，以 `ResizeObserver` 更新所需顶距，加回 `main.scrollTop` 防止滚动时重复增加留白，并在卸载时断开观察器，避免窄屏标题被壳层遮挡。
- **精确差异。** 正式工作树 HEAD 仍为 `bcafa89fa31bdf62329bced89baebc193323a739`，实施保持未提交。相对第二次 handoff 的 101 条路径，仅 `frontend-js/src/app/plan/components/TaskPage.vue` 改变，另 100 条不变；该文件 SHA 从 `fa913badcd9d1573f061bfbee92c33e565fe4ff88aa631ffd0f95bc4b512e9af` 经布局候选 `7bbbfaaee5516375ae8cb36f262d288cd09b2281ec35432e5fbeb766c33f3ac0` 变为最终 `a7e6f0d63893190efa45af8bb1ceaa34764682e24ddad8dfbd6906d37416c748`。协调者已机械同步到正式树；Development 复算第三次 101 条路径摘要，101/101 一致，并执行正式树 `git apply --reverse --check` 退出 0。累积摘要 `backend/data/maintenance-evidence/arch-task-001-r1-dev3307/handoff3-source-digests.json` SHA-256 `0c7bf1422c1e3638581af87ac1184bb7adba9a543dd01224b8ad3fc59f1a94e1`，对应 patch `handoff3-source.patch` SHA-256 `19703fb48d7df6b18e610b4d3e01240ba2b690bd103933460b549859235055da`。
- **Development 自检。** 在私有候选 `frontend-js/` 执行 `pnpm_config_verify_deps_before_run=false pnpm check:modules`，退出 0；`pnpm_config_verify_deps_before_run=false pnpm test:modules`，退出 0、57 passed、0 skipped；以 `VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' VITE_FRONTEND_MOCK_ENABLED=false VITE_API_BASE_URL=/api/v1` 执行同一 pnpm 的 `build --outDir /private/tmp/arch-task-001-r1-coordination.UaaX27/ui-padding-build`，退出 0，保留 Vite 已有的大 chunk 提示。模块测试中现有 setup 假夹具未模拟 `onBeforeUnmount`，日志有两条无活动组件实例的 Vue 警告；57 项全部通过，未因此修改测试文件。单独执行实际 SFC setup 的合成几何检查：header 底部 186、自然顶部 144 时留白 50px；主区滚动 80px 后留白不累加，模拟 header 底部增加后留白更新为 64px，桌面示例留白 0，卸载时 observer 断开。初版 SFC 对照还确认既有脚本行为、`v-model`、按钮事件和日期格式不变，中英文时区键均存在。两个构建/测试日志与临时构建目录留在任务私有窗口供复核，不进入源码。
- **实际浏览器证据。** 协调者在正式 `5190` 使用独立 Chrome 运行 `PYTHONPATH=. .venv/bin/python -B <WINDOW>/run-browser-task-layout.py <WINDOW> <EVIDENCE> after`，退出 0。`1280×900` 的计划和实绩页，中英文均为四列筛选、筛选段高度 164px、表格起始 y=325；正文不常驻时区说明，标题问号 hover/focus 提示通过。`430×920`、公共侧栏收起时，两页筛选单列且位于视口内，卡片顶部 y=194，位于 header 底部 y=186 之下；鼠标实际命中问号且 hover/focus 通过。前后脱敏证据 `task-list-layout-before.json` SHA-256 `283c6c59853d7a7c1f8344dd17b3f1fa00b80ba21f6002580a543d83e7f2564d`，`task-list-layout-after.json` SHA-256 `17632466b04a385140368d685d5a0b650e650feb971dc9a5004f0ed738b5985e`，均在上述本机 ignored 证据目录。
- **交接边界。** 规格 SHA-256 仍为 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`。QA2 checklist SHA-256 `d90e366168a618bf11dd1e00ebb93598f8dfde8fffe269878ab066e3d7a58b06`，其 `qa_passed` 只针对第二次交接；该共用页面文件调整后的第三次交接须由 fresh-context Verification 独立核对。QA1 合成任务、字段配置、临时验收进程和 DAA 样本暂由协调者保留并负责最终按标记清理；此前已记录的历史测试限制、真实设备及生产边界不变。本交接不代替新一轮 QA verdict 或 Human Owner 最终验收。

## 2026-11-14 字段设置弹窗与使用说明返工

Human Owner 在 r1 验收中指出字段设置弹窗右侧控件被裁、缺少弹窗本机列宽恢复，并要求说明勾选项、停用/退出及提供使用 MD。协调者确认按既有 R04/AC09–10 同范围处理：不新增已保存字段物理删除、不改后端接口或迁移、不写数据库。当前正式工作树 HEAD `fd999224a8756feda314a33148304b4bf3461876`，并行任务已修改其他采集及文档路径，不能沿用旧 101 文件无漂移假设；本轮实施前的精确允许路径摘要记录于 `/private/tmp/arch-task-001-field-settings.Av8Vy2/dev-preimages.json`。浏览器验证由协调者使用独立 context，限制为读取及拦截写请求/模拟响应。

## 第四次 developer_handoff — ARCH-TASK-001 r1 字段设置

- **改动与边界。** 共用 `TaskConfigDialog.vue` 增加弹窗专用宽度和内部滚动、常显横向滚动条，数字输入按单元格限宽；列顺序支持 0–65535，清空显式提交 `null` 并显示“按槽位”。复用 `useTableColumnWidths`，以稳定列 `prop` 和计划/实绩各自的弹窗 key 保存本机列宽，弹窗内恢复默认不清草稿或主列表列宽。桌面固定最左稳定字段键以便右滚时识别行；窄屏解除固定以免遮挡末列。仅 `_new` 的未保存行显示“移除草稿”；移除后若其余内容与原配置相同则清除无变化草稿，其他未提交修改及取消保留草稿的行为继续保留。已保存行仍通过取消“启用”并保存来停用，未增加物理删除、后端/API、迁移或数据库写入。
- **说明与翻译。** 两模块中英文各补同一组弹窗提示键；新增 [字段设置使用说明](../../frontend-js/FIELD_SETTINGS_GUIDE.zh-CN.md)，两份 frontend README 分别链接。说明覆盖字段组、全部勾选项、三种实绩归属、列顺序与个人列宽、展示修订与业务版本、停用/复启/替代键，以及 PLC 必填映射、版本登记和 DAA/SMA/CA/FF 的职责与联动。根 `CODE_INDEX.md` 已有共用组件所属条目，本轮未覆盖并行任务对该文件的修改。
- **自检。** 正式 `frontend-js/` 执行 `pnpm_config_verify_deps_before_run=false pnpm check:modules`，退出 0；`pnpm test:modules` 退出 0、62 passed、0 skipped；以 `VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' VITE_FRONTEND_MOCK_ENABLED=false VITE_API_BASE_URL=/api/v1` 运行同一 pnpm 的 `build --outDir /private/tmp/arch-task-001-field-settings.Av8Vy2/dev-dist-final`，退出 0，保留 Vite 大 chunk 提示。既有列表测试假夹具未模拟 `onBeforeUnmount`，测试日志有两条 Vue 无活动实例警告。`node /private/tmp/arch-task-001-field-settings.Av8Vy2/dev-component-check.mjs` 对实际 SFC setup 的无数据库检查退出 0，覆盖桌面/窄屏固定列切换和监听器移除、已保存行不可本地移除、未保存行移除与重开、其他草稿保留、计划/实绩弹窗及主列表列宽隔离、恢复默认、65535 和 `null` 保存载荷。首次运行该临时检查时，mock 的 `structuredClone` 无法复制 Vue proxy 而退出 1；改为模拟 HTTP 的 JSON 序列化后通过，应用源码未因该夹具问题改变。两模块 workflow 中英各 87 个键对齐，说明与两份 README 的相对链接均存在；`git diff --check` 和新说明逐行空白检查通过。
- **独立浏览器补充自检。** 协调者在正式 `5190` 以独立 Chrome context 读取真实 dev 的 v3/rev3 定义，分别检查计划/实绩的 `1470×796` 中文日间及 `430×920` 英文夜间四组。末列 65535、输入和表头左右边缘命中均通过；桌面列宽 190→236→页面重载后 236→恢复默认 190，主列表列宽不受影响，恢复默认保留编辑；移除草稿后重开未复活，清空后显示按槽位。浏览器拦截四次模拟保存，覆盖两页顺序与停用；停用载荷仅提交 `enabled:false`，实际业务写请求转发 **0**。首版实测发现窄屏固定键列遮挡末列左侧，随后改为窄屏解除固定并完成上述重测。浏览器结果是协调者补充证据，不代表已对真实业务配置执行保存。持久脱敏 `field-settings-20261114/baseline.json` SHA-256 `40645916b9030a9fd20c4daf22c38bb4d292a47fc2cbdc0e36bfdacea82835df`，`browser.json` SHA-256 `68452395c7516fb772757817264f4f3601e5da905f2dc9485c155fec1d3bb0d5`，同目录包含桌面与窄屏截图。
- **精确工作树差异。** 以当前 HEAD `fd999224a8756feda314a33148304b4bf3461876` 和本轮实施前实测摘要为基线，仅以下 8 条本任务源码/文档路径发生变化；第二列是 preimage SHA-256，第三列是 postimage SHA-256，`<new>` 表示原来不存在。另有本 Development 文档自身变更；所有范围外并行改动保留。

```text
frontend-js/src/app/plan/components/TaskConfigDialog.vue ee16840453cc4f532678adc24cd1d4bca55b6caf7855fbcf2feea6508f503302 84f4691cb6fcd9cab3936b8e6a572cbc7c3294dff5a8d0adfe65a79984787d54
frontend-js/src/app/plan/locales/zh-CN.json b95c9d6d276abda23a5b6773e39bfe82210ed9ec2ce3275ede23bbf90c4c46c3 3a899285f7a83176f43e2870d5077ce7491908b4f8125cf874014dd69057f1e9
frontend-js/src/app/plan/locales/en-US.json 470f758f0d3b6eed13e0d1737557ab68f738ae7563fa5037bf361bea94988b6f 1333521deb537973d3256ff9cfe7912f90771a5f6f9b44b1641eab51fff17a85
frontend-js/src/app/performance/locales/zh-CN.json 7dc1093b4906f3f474ef8a408df475888f3a78231dc096775fa9d0c0f001022b de019c6295fc9ab901d2e0181a7bd84a34be5b6bad9442d402ed82cc1ea4a0d9
frontend-js/src/app/performance/locales/en-US.json 950bb4ba3e1b3037fb81a072461604d1c4dff50c75b678123851b844002e9728 a357c5fe008454614e1e9d610de2a733e606bd15a39b8f25e50ad008fffaef9e
frontend-js/README.md bcdf3dec67957a7476846d015f7290912912c988ae1aebce10b3e4ebcc7a5ee6 278676a0a906191ae914ae9a0a6be1752461648b99c921ba9d9be8952e0d1fb3
frontend-js/README.zh-CN.md c8949b41174f274b80781cd301eba833e2ce0e4f5f69e34c0d3fb990e8f10ee5 3da20e53ea822abc1b0912599ebfad5794e04edb1f1d8cce642b039657c9a7a3
frontend-js/FIELD_SETTINGS_GUIDE.zh-CN.md <new> 13bc619dffee96b48b8734a2dc7a9228edc319215c0286bd50770e66d18389f9
```

本轮 scoped manifest `backend/data/maintenance-evidence/arch-task-001-r1-dev3307/field-settings-20261114/dev-scoped-manifest.json` SHA-256 `62d5e4bcf902766c09ce272320c43e5f6dcde2ea488b39a78fae101ac3f4a866`，对应 `dev-scoped.patch` SHA-256 `35a4ade8fb10660b08c101cfc2b6079034772cc6a83ec8acb9ffcb801fd6894f`；复算 8/8 postimage 一致，正式树 `git apply --reverse --check --whitespace=error-all` 退出 0。规格 SHA-256 仍为 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`，现有 QA3 checklist SHA-256 `9ceac9dfb4dcfdbf23293c0666ab61343dd07accf80b784312fab81a93d959c4`，二者均未修改。当前任务实施未暂存、提交或推送。

QA3 的 `qa_passed` 针对第三次交接；本轮修改须由 fresh-context Verification 独立核对后更新其 checklist，Human Owner 最终验收仍待其决定。临时脚本、前后构建和日志位于 `/private/tmp/arch-task-001-field-settings.Av8Vy2/`，仅供独立复核，持久脱敏浏览器与 scoped diff 证据位于本机 ignored evidence 目录；验证结束后由协调者核对归属并回收临时资源。保留现有 dev 配置、字段、并行任务和用户浏览器，未执行数据库写入或真实设备联调。
