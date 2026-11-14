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
