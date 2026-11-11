Task ID: ARCH-ACQ-002
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 ARCH-ACQ-002 r2，移交 Development 按 §5 预检并实施 dev 九表清退，ARCH-FE-005 并行。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 清退 Core 旧 Projection 入口、v1 事实及旧快照，保全 v2 和独立业务链路
Owner: AIIS ICS Architecture
Acceptance Chain Reference: 本规格第 6、7 节及 Development Lifecycle Workflow
Depends On: ARCH-BE-012 r4 的已核对 v2 HTTP 合同、dev 验证基线和 Alembic 2c4e6a8b0d12
Related Task: ARCH-ACQ-001, ARCH-BE-009, ARCH-BE-010, ARCH-FE-005, DAA-010, ARCH-OBS-001
Created: 2026-11-10（Asia/Shanghai）

# 旧 Projection、v1 事实与快照清退

## 1. 目标与执行顺序

Human Owner 明确清退七张 v1 事实表和两张旧快照表，保留两张 v2 表。沿用 r1 的 Core 旧 Projection 清退范围。Backend 清退可在指定 dev 库先行，Web「采集数据」由 ARCH-FE-005 并行推进，DAA-010 继续等自己的实施门槛。DAA 或 Web 完成不再是本任务开工条件。现场、生产及其他现有库的切换各走独立批准。 [项目路线](../ARCH-ACQ-001-acquisition-data-coordination/spec.md) · [Web](../ARCH-FE-005-acquisition-data-module/spec.md) · [DAA](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/spec.md)

以 ARCH-BE-012 r4 已独立复核的 v2 源码合同及指定 dev 功能证据为基线。原 r4 隔离 B 矩阵及最终验收仍待完成，其 v1 兼容验证要用原候选。本任务按 ARCH-BE-010 r2 已验收的源码及隔离合同保护业务写入与回执。两个任务的批准、验收和证据各归原 bundle。 [v2 验证与 dev 记录](../ARCH-BE-012-simplified-plc-facts/checklist.md) · [BE-010 验收](../ARCH-BE-010-anonymous-business-integration/checklist.md)

Human Owner 已指认并授权在 `localhost:3307`（TCP `127.0.0.1:3307`）的 Docker MySQL 8.4.6 开发库 `industrial_level_2_system` 用 Alembic 清退九表，容器为 `aiis-ics-arch-database-only`。协调会话在起草前只读复查，Alembic 为 `2c4e6a8b0d12`，九张旧表各 0 行，v2 两表各 2 行，可见元数据中无涉及九表的外键、视图或表触发器。以上为盘点快照，实施时重新核对实际库、私下核对 server UUID、使用方与完整可见性。 [既有 dev 目标记录](../ARCH-BE-012-simplified-plc-facts/tasks.md)

## 2. 清退与保留边界

| 表面 | 清退或保留口径 |
| --- | --- |
| v1 PLC 事实 | 清退 `plc_facts_batches`、`plc_facts_cycles`、`plc_facts_latest_points`、`plc_facts_raw_samples`、`plc_facts_sample_receipts`、`plc_facts_source_bindings`、`plc_facts_stream_state`。撤掉 `/api/v1/integration/plc-facts` 下的 `POST /batches`、`GET /latest`、`GET /history`，以及旧准入、模型、F7/profile 校验、游标、服务和 v1 维护 `status`、`adopt`、`cleanup`。保留 v1 发布工件、旧 migration 和验收证据，标清适用的历史源码。 |
| 旧快照 | 清退 `plc_db_block_latest_snapshots` 和 `plc_db_block_raw_snapshots`、活跃 ORM 导出和 Alembic env 导入、仅以这两表为源的 `GET /api/v1/monitor/realtime/latest` 及 Core 专用 facade/mock。保留 `/monitor/collector/status`、`monitor_collector_states`、HMI 业务页及 `getHmiRealtimeOverview`/对应 mock、温度、能耗、曲线及其 `legacy` / `http` 读分支。 |
| 旧 Projection | 撤掉系统 `/system/dict` 的映射设置页、导航、独占文案、facade 和 `/api/v1/projection-mappings/*` 管理 API；退役 `projection-mapping`、`projection-mapping-manage` 及旧启动 catalog、registry 装配、runner 和独占日志。保留用户管理、登录、真实字典 `/sys-dict` 和 `system-dict`。保留业务模块使用的 `projection.provenance_contract` 和共享 descriptor 类型、同步适配器及历史来源字段，撤掉它们从 Core 旧 runner 自动启动的路径。 |
| Projection 元数据 | 保留 `projection_mapping_sets`、`projection_mapping_revisions`、`projection_mapping_bindings`、`projection_mapping_audit_events`、`projection_runtime_cursors`、`projection_runtime_audit_events` 及其列、约束、现有行与 ORM 声明。旧快照 ID 的历史标识留在原记录，核对无活跃查询或业务逻辑要求按这些标识回读快照；历史政策示例继续作为参考。 |
| v2 与业务集成 | 保留 `plc_facts_samples_v2` 和 `plc_facts_latest_points_v2` 的结构、精度及既有数据。继续提供 `POST /api/v1/integration/plc-facts/samples`、`/api/v1/acquisition-data` 下的 `GET /options`、`GET /latest`、`GET /history`、`GET /history/{id}`、`plc-facts-read` 和 `cleanup-v2`。保留 BE-010 八路 typed 写入、永久业务回执及严格目标采用边界，保留 `monitor`、`equipment`、`performance` 业务 API、数据及权限。 |

DAA（含 SQLite、原有配置、积压与补传）、冻结 `control-agent`、SMA、独立工具、消费项目源码及其运行环境均在范围外。升级后的 Core/dev 不提供 v1 DAA 上传，旧直库采集程序也失去两张快照表，既有 DAA 数据的处置和恢复上传归其自己的任务。旧读写的替代路径由各消费方独立采用。本任务不重映射旧授权，不新增兼容写入，不重建旧表，也不顺带清理其他空表。 [v1 历史合同](../../contracts/published/http-api/plc-facts-v1/README.zh-CN.md) · [v2 合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md) · [monitor 合同](../../backend/app/monitor/README.zh-CN.md) · [typed 业务合同](../../contracts/published/http-api/business-integration-v1/README.zh-CN.md)

## 3. 需求

- **R01 调用方和开工证据。** Development 在改正式源码前固定工作树、受影响文件基线及 ARCH-BE-012 r4 QA3 公开候选。旧 v1、F7、2c4/77 表和两个 B runner 的原测试入口及候选摘要须可复现。保留原独立证据和可核验的旧源码副本，记录保留归属和后续清理门槛，不只留下临时路径。若无法保全，先交回协调者确认原 r4 后续验证材料。盘点 repo 内静态/动态注册、消费应用、业务适配器、后端进程、旧 v1 DAA、冻结 CA 和可能的直库连接。已在消费方源码看到旧快照/Projection 引用，须核实这些调用方未连接本次 dev 库或依赖本次 Core 候选；源码命中与环境采用分别登记。旧 writer 或仍依赖旧入口的调用方实际在用、归属不明或无法确认时，停止受影响的清退，保持其现役路径并报证据与下一门槛。 [r4 QA3 候选摘要](../ARCH-BE-012-simplified-plc-facts/evidence/development-r4-qa2-fix-hashes.txt)
- **R02 撤下无现役依赖的入口。** 删除 §2 中已核对的 Core route、API、专用配置及运行装配，使旧调用明确落入现有无路由/权限处理，不返回伪造的空结果或改读业务接口。删除 v1 专用维护及表声明。移除 runner 后普通启动仍要正确装配字典、登录、各业务与 v2，保留通用权限、日志、连接清理和共享来源/时间适配；过时授权按现有规则过滤，不修改真实权限配置。对仍有业务写入依赖的运行路径，另行确认单一 writer 与切换，不能以本清退授权替代。
- **R03 新 Alembic 迁移。** 在 `2c4e6a8b0d12` 后新增唯一后继 `3d5f7a9c1e23`，保留现有迁移文件原字节。在线 MySQL 8.4 迁移在执行 DDL 的连接上确认目标、表清单和九表均为空，在无并发 writer 的维护窗口仅对九表执行 DDL，应用表由 77 张变为 68 张，`alembic_version` 另计。保护所有保留表及其对象，不用 ORM 自动建表、手动删表、关闭外键检查、离线 SQL 绕过预检或手工 stamp。新 revision 是前向清退点，降级明确拒绝并指向另行批准的恢复流程。
- **R04 精确 revision 接续。** `v2_config.REVISION`、HTTP target probe 和 `cleanup-v2` 的 sync probe 与新 head 同步。保留 server UUID、schema、单一精确 revision、MySQL 版本、上海时钟和私有 profile 守卫。对指定 dev 的原 v2 私有 profile，在确认进程、文件归属与旧目标身份后只原子更新 `target.schemaRevision`，保留原权限和脱敏前后校验记录。凭据、sources、readScopes、目标别名及其他设置保持。复核已指认的本机 `127.0.0.1:8000` Core 开发后端已加载新源码和 profile。必要的缓存刷新或受控重载限于此进程及同一维护窗口，进程归属不明则停在预检。UI 侧约定维护窗口内可能暂时得到 503，窗口结束须恢复原访问范围及四个 GET 的成功响应。禁止通过放宽匹配、回退旧源或更改前端 API 来掩盖错配。
- **R05 保持 BE-010 原准入。** 只在 `backend/common/integration/storage.py` 的已知 revision 集合增加 `3d5f7a9c1e23`，保留 `1b3d5f7a9c20` 和 `2c4e6a8b0d12` 的历史精确档位，实际凭据的 revision、server UUID、schema 与数据库仍须逐项精确相同。三 owner 在新 head 拒绝旧凭据，经合成的同目标新凭据后八路仍可写，升级前的永久回执及旧业务读语义仍可复验。指定 dev 现有未采用/关闭状态保持，禁止生成虚假的采用证据、改真实 BE-010 配置或做时间/数据回填。如果发现该 dev 的 BE-010 已采用或在写，停在预检并报证据。
- **R06 并行交付。** ARCH-FE-005 消费同一五路 v2 源码合同中的四个 GET。新模块、manifest、导航、授权和其测试由前端任务交付，ARCH-ACQ-002 只退役旧 System 页和旧快照 facade/mock。两个任务各自交接，`CODE_INDEX.md` 的相关条目由协调者串行合并。dev 两张 v2 表的既有行来自后端模拟上报，只供 dev 功能和对账验证。DAA 上报与正式跨端链路验收由原任务交付。 [FE-005 规格](../ARCH-FE-005-acquisition-data-module/spec.md)

## 4. 批准后允许的写入面

表中花括号表示括号内列出的有限文件。当前工作树已有并行改动，Development 先记录基线，按职责逐个合并。表外源码或实质扩大需求、验收、风险，返回 PM 修订并取得精确 Revision 批准。

| 表面 | 仓库相对路径与改动限制 |
| --- | --- |
| 新迁移和装配 | 新增 `backend/alembic/versions/20261110_2215_3d5f7a9c1e23_retire_legacy_acquisition.py`；修改 `backend/alembic/env.py` 的旧快照导入、`backend/core/registrar.py` 的 Projection 专属装配、`backend/app/module_contract.py` 的旧 System 独占依赖、`backend/app/module_registry.py` 的相关说明。 |
| Projection 和 System | `backend/app/system/manifest.py`，退役同模块 `api/projection_mapping.py`、`crud/async_projection_mapping.py`、`schemas/projection_mapping.py`、`services/async_projection_mapping.py`；`backend/projection/{__init__,registry}.py` 仅调整说明和专用 discovery，退役 `backend/projection/{input_resolver,policy_catalog,runner,runtime,failure_observability}.py`；`backend/{common/log.py,common/error_codes.py,settings.py,.env.example,.env.docker.dev.example,.env.docker.prod.example}` 仅删旧专属日志、错误和配置，保留通用设置校验。现有 `backend/config/plc_snapshot_policy.yaml` 保留为历史示例。 |
| monitor 快照 | `backend/app/monitor/{manifest.py,api/routes.py,models/__init__.py,models/monitor.py,schemas/__init__.py}` 的旧快照部分，以及退役 `backend/app/monitor/{api/realtime.py,crud/async_realtime.py,services/async_realtime.py,schemas/realtime.py}`。 |
| v1 退役及后继守卫 | `backend/app/plc_facts/{manifest.py,models/__init__.py,v2_config.py}`；退役同目录 `{canonical,config,cursors,error_codes,retention,source}.py`、`api/{batches,dependencies,history,http,latest,routes}.py`、`crud/{async_ingest,async_query,sync_maintenance}.py`、`services/{async_ingest,async_query,sync_maintenance}.py`、`models/{facts,receipts,state}.py`、`schemas/{batch_in,query,read_out,receipt_out,source}.py` 中经确认的 v1 独占文件；`backend/scripts/plc_facts_maintenance/main.py` 去掉 v1 子命令，保留 v2 子命令与安全检查；`backend/common/integration/storage.py` 仅接续精确 revision。 |
| 旧 Web 入口 | `frontend-js/src/app/system/{manifest.js,views/dict/index.vue,api/index.js,api/projectionMapping.js,locales/en-US.json,locales/zh-CN.json}`，`frontend-js/src/locales/{en-US,zh-CN}/breadcrumb.json` 的旧映射页专属键，`frontend-js/src/app/monitor/api/{index,mock}.js` 的旧快照专属导出。 |
| 活跃回归 | `frontend-js/tests/module-registry/{registry,page-access}.test.mjs`；`backend/tests/test_{aiis_demo_module,business_integration_compatibility,business_integration_migration,business_integration_storage,business_module_migration,business_module_reintegration,core_migration_baseline,energy_price_migration,equipment_temperature_migration,logging,mapping_migration,module_registry,openapi_router_tags,plc_facts_v2}.py` 仅调整当前入口、声明及迁移断言；`backend/tests/module_admission_fixtures.py` 仅区分当前候选与已冻结 C0/C2、BE-010 A0 的输入，旧 CRUD、快照表和 model export 由原候选提供，保留原历史断言。退役 `backend/tests/app/monitor/test_realtime.py`、`backend/tests/test_projection_{control_plane_registration,failure_observability,runtime}.py`、`backend/tests/test_plc_facts_{api,compatibility,contract,cursor,maintenance,migration,ordering,retention,source}.py` 中只服务退役入口的活跃测试。新增 `backend/tests/test_legacy_acquisition_retirement.py` 和 `backend/tests_mysql/test_legacy_acquisition_retirement.py` 分别覆盖迁移护栏、隔离 MySQL 升级及后继合同。 |
| 现行文档 | 根 `README.md`、`README.zh-CN.md`、`CODE_INDEX.md`，`backend/{README.md,README.zh-CN.md,app/README.md,app/README.zh-CN.md,app/MODULE_CONTRACT.md,app/MODULE_CONTRACT.zh-CN.md}`、`backend/app/{monitor,plc_facts}/README.md` 及其 `README.zh-CN.md`，`backend/scripts/{plc_facts_maintenance,business_time_adoption}/README.md` 及其 `README.zh-CN.md`，`contracts/{README.md,README.zh-CN.md,published/http-api/plc-facts-v1/README.md,published/http-api/plc-facts-v1/README.zh-CN.md}`，只同步退役说明、现行入口及精确后继。历史任务、旧迁移及 v1/v2、BE-010 的 OpenAPI、schema、vectors 不改。有效 Dockerfile/PyInstaller 入口及共享 `projection` 包的打包包含项只核对。PLAN 与任务索引由协调者按角色证据机械同步。 |

本任务角色文档按 STD 各自写入。仓外写入仅限 §5 获批夹具、候选与恢复证据和 §3 的 dev 私有 v2 profile 单键更新。私有文件保留本机原权限或更严权限，正式 `.env`、访问令牌、数据库凭据及实际记录不进入 diff、命令输出或公共证据。

`backend/pyproject.toml` 的 pytest 默认 `testpaths = ["tests"]` 保持。现行后继 MySQL 矩阵显式运行新增测试入口，单独验目标后才导入项目配置。历史 `backend/tests_mysql/test_plc_facts.py`、`test_plc_facts_v2.py`、`test_business_integration.py` 及 `test_mapping_business_api.py` 保留原入口及门禁，仅从对应固定源码和原目标协议运行。r4/B 的 `1b3`、`2c4` 兼容验证沿用原脚本，不在新 head 导入已退役模块或套用旧夹具。

## 5. Dev 预检、迁移及恢复

1. **先验证隔离候选。** Development 先在获准的 MySQL 8.4.6 一次性夹具上完成空库全链、合成旧库升级、拒绝及恢复矩阵，再进入 3307 预检。fresh QA 在 Development 交接后独立复现。两轮各自使用显式登记的独占 loopback 目标/临时 schema，固定容器或 server UUID、非 root 账号、schema、revision 及资源回收范围。任何临时 Docker 操作须有具体授权，测试和故障注入不得落到 3307 既有库；无合规测试目标时停在待环境门槛。
2. **锁定已有 dev。** 使用正常后端指向的既有非 TESTING 目标核对主机/端口、容器、server UUID、schema、MySQL 8.4.6、上海会话偏移与唯一前驱。读核九表实际存在且逐表 0 行，确认均为 InnoDB。核对跨 schema 外键、视图、触发器、routine/event、直接和间接调用以及写连接的可见性；同库无运行中的旧 reader/writer、无未决事务和不可控重连，迁移窗口能阻止并发写入。在可见性不足、出现任一非零行、实际调用、意外依赖、表结构或目标不符时停止，保留脱敏证据。既有 v2 样本按主键、身份、值/质量、时间精度和 latest 水位记录数量与稳定摘要，按需抽查保留业务数据及回执；保留表结构和行数作为对账基线。
3. **建立恢复材料并实施。** 保存九张空表的可复建 DDL、目标 revision、保留对象清单、数据摘要及旧私有 profile 摘要，记录校验值。用隔离合成库证明这些空表定义可精确恢复，按第 4 步复现未登记的 DDL 状态。3307 既有库仅用于一次实际清退和前后只读对账。通过预检后执行 `uv run --offline --frozen --no-sync alembic upgrade 3d5f7a9c1e23`，配套按 R04 切换 profile。Dev 验收只读核对两张 v2 表和对应 GET。v2 新写入、过期清理、权限反例和 BE-010 写入/回执使用隔离合成夹具。
4. **区分 DDL 与版本登记。** MySQL DDL 隐式提交，表删除和 Alembic 的版本更新可能分别落地。用同一条固定清单的 InnoDB DDL 删除九表，逐次记录实际 revision、表集合及错误。若前驱且九表全在，重新完成预检才可受控重跑。若前驱且九表全不在，仅在有此次操作的删除证据、完整保留表对账及明确恢复确认时，允许经同一迁移的受控入口重跑以完成版本登记。后继且九表全无时仅核验结果。部分缺表、证据不全、其他 revision、目标或保留数据漂移一律停，禁止盲重跑、手工 stamp 和回退。若需要恢复真实 dev 的旧表、旧进程或旧私有配置，按已核验材料另行申请执行，恢复完成后确认唯一写入方。 [MySQL DDL 隐式提交](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html) · [MySQL InnoDB 原子 DDL](https://dev.mysql.com/doc/refman/8.4/en/atomic-ddl.html)

## 6. 验收标准

| 编号 | 独立可核对结果 |
| --- | --- |
| AC01 范围与调用方 | 存在精确 r2 批准及实际环境、候选指纹和授权范围。逐项给出旧入口的调用、目标、退出依据或 blocker，复核旧 DAA/CA 对升级后 dev 的不兼容交接、r4/B 历史候选可复现、未触达消费方与其他库。 |
| AC02 旧入口与业务保全 | 正常启动与 OpenAPI 无旧 Projection、v1 三路和旧快照路由，真实字典、认证、collector 状态及 monitor/其他业务权限与查询回归通过。旧映射页从两种语言菜单、路由和默认入口去除，旧直链按现有守卫处理，v2 和 HMI 业务链可用。旧表引用的搜索命中限于迁移、隔离验证、冻结兼容或注明用途的历史引用。Core 无已删表读写或旧维护入口。 |
| AC03 两种升级 | 隔离 MySQL 空库从根 migration 到后继；合成旧库先到 `2c4e6a8b0d12`，九张旧表为空，设置 v2 样本、历史 Projection 元数据、业务记录及永久回执，再升级后继。两者均只有唯一后继，表清单为 68 张应用表且没有九张旧表，活动 ORM metadata 与实际表对齐，保留对象结构、合成行和摘要一致，旧 Alembic 文件哈希不变。 |
| AC04 预检与恢复 | 任一旧表非空、残留依赖、错误目标或异常表集合均在首条 DDL 前拒绝；隔离演练覆盖 DDL 前失败、DDL 后版本登记前失败及安全重跑，展示状态、实际 DDL/版本更新与数据守恒。对已完成状态重复核验无副作用，降级明确拒绝。 |
| AC05 v2 与并行 Web | 五个 v2 API 和错误/授权合同逐项比对，隔离用例验证写入、重复、冲突、latest/history/detail/options、默认关闭、越权拒绝以及 `cleanup-v2` 仍按精确目标工作。指定 dev 迁移后四个 GET 对账同一已知样本，旧 profile/错误目标拒绝，新 profile 正常服务且字段、凭据与权限范围保持。 |
| AC06 BE-010 与历史 | 隔离旧库升级后，旧凭据对三个 owner 均因精确 revision 失配被拒；同一目标的新凭据验证八路及旧永久回执，证明无时间/权限/历史转换。保留真实 dev 的既有关闭/未采用配置，原 BE-010 A+B 与 BE-012 r4 隔离 B 的证据范围各自独立。 |
| AC07 指定 dev 对账与交接 | 真实 dev 的迁移前后目标核对、九表零行和无运行引用的证据可追溯。后继 revision、九表不存在、68 张应用表、v2 两表各 2 行及精确摘要、保留表结构与约定摘要一致；意外数据/旧调用/权限不明记录为阻塞。报告恢复证据位置及保留期限，记录无其他库、生产、现场、DAA、SMA 或冻结 CA 写入。 |

Development 和 Verification 分别使用项目锁定 `uv` 环境、合成配置的后端编译及定向 pytest、正常 app/OpenAPI 与无连接 guard、`pnpm check:modules`、`pnpm test:modules`、`pnpm build`、文档链接和 diff 检查，附实际命令、退出码、源码与目标标识。独立 QA 用自己的隔离 MySQL 复现 AC03–AC06，对 3307 只做只读检查并复核 Development 的前置及迁移证据。实际环境缺失记录为 blocker。Development 与 Verification 使用 `interface-lineage-audit` 核对调用链，使用 `backend-arch` 处理迁移与 API 守卫，使用 `backend-script-tooling` 处理维护 CLI，使用 `frontend-ui` 和 `i18n-workflow` 处理旧前端入口，使用 `code-document-indexer` 同步实际结构。另获准的隔离 Docker 操作使用 `docker-project-ops` 和 `docker-expert`。如发现需要改实际打包边界，按 `backend-packaging` 另定范围。

## 7. 修订与交接

| 修订 | 状态与变更 |
| --- | --- |
| r1 | 2026-11-10（Asia/Shanghai）起草源码 Projection 清退，依赖前三项验收，旧表另立范围。 |
| r2 | 2026-11-10（Asia/Shanghai）根据 Human Owner 对九张旧表、旧快照、dev Alembic 和前端并行的决定修订。Human Owner 已批准精确 r2 实施范围。 |

Human Owner 于 2026-11-10（Asia/Shanghai）批准精确 ARCH-ACQ-002 r2。审阅稿 SHA-256 为 `44413482237ea3a369725bbd1b7f1891a757fb2d91aed516fb5d641dec874de5`。

> 批准 ARCH-ACQ-002 r2 和 ARCH-FE-005 r2 实施。旧表清退和前端并行做，按规格用 Alembic 清退 dev 库的 9 张旧表，DAA 先不动。

§5 预检通过后，Development 可执行已指认的 dev 九表清退，同一目标和操作无需再次确认。Development 记录候选、前置、实际操作、自检、受保护数据对账和已知限制，再交 fresh-context Verification。独立 QA 记录核验与剩余门槛，Human Owner 决定最终验收。 [Development Lifecycle Workflow](../../.codex/workflows/development-lifecycle-workflow.md)
