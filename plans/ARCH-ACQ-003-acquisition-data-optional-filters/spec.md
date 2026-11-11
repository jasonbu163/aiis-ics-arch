Task ID: ARCH-ACQ-003
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 ARCH-ACQ-003 r2 实施，PM -> Development 按获批范围交付候选和自检，再交 fresh-context Verification。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 统一采集事实表名、登记上报来源并提供默认授权浏览及可选筛选
Owner: AIIS ICS Architecture 采集事实与 Web 读面
Acceptance Chain Reference: 本规格第 6、7 节及 Development Lifecycle Workflow
Depends On: ARCH-BE-012 r4 已验证的 v2 合同基线、ARCH-ACQ-002 r2 的 3d5f7a9c1e23 后继及 ARCH-FE-005 r2 QA5 Web 候选
Related Task: ARCH-ACQ-001, ARCH-ACQ-002, ARCH-FE-005, ARCH-BE-012, ARCH-BE-010, DAA-010
Created: 2026-11-11 Asia/Shanghai
Updated: 2026-11-11 11:36:40 Asia/Shanghai

# 采集事实表、来源登记与默认浏览

## 1. 目标和基线

统一采集事实的两张表名。保留整份 DB 样本历史和逐点最新值的现有行粒度。允许已登记的外部程序上报完整样本，记录来源类型和实例。实时页进入即分页读授权点位，历史页进入即分页查授权范围内最近 24 小时。PLC、DB 和实时点位搜索用于筛选。 [后端现有合同](../ARCH-BE-012-simplified-plc-facts/spec.md) · [Web QA5 证据](../ARCH-FE-005-acquisition-data-module/checklist.md)

协调者于 2026-11-11 只读核对现有 `127.0.0.1:3307` dev 的 MySQL 8.4.6、上海会话偏移 +28800 和 `3d5f7a9c1e23` 精确 revision。两张 InnoDB 原表各有 2 行，来自已记录的一个模拟发送实例。目标表名均未占用。历史的 `group_id` 和 `config_revision` 为 `VARBINARY(128) NOT NULL`，无 `source_type`。本次快照只供规划，执行前重核。Core、Automation World、tools、vibe-l2 和 data-twin 的当前活动源码中，核到采集数据 GET 的调用方为 Core Web facade。源码清点仅覆盖已检查的仓库。 [既有 dev 验证](../ARCH-ACQ-002-legacy-projection-retirement/checklist.md) · [当前 Web facade](../../frontend-js/src/app/acquisition-data/api/index.js)

交付包括候选源码、迁移、HTTP 合同、两页和验证。实际 dev 切换见第 6 节。原 v1 和旧快照继续退役。BE-012 原 B 验证、ACQ-002 与 FE-005 各自最终验收、业务数据与接线、DAA 和 SMA 实现、现场和生产由各自任务处理。DAA-010 继续等待其新版 provider 的独立验证及 Human Owner 最终验收，交接使用最终生效合同。 [DAA-010 交接条件](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/spec.md#2-开工前置与交接)

## 2. 存储、上报和来源

**R01 两张事实表。**

| 原表 | 目标表 | 数据口径 |
| --- | --- | --- |
| `plc_facts_samples_v2` | `plc_facts_history` | 一个 PLC 的一个 DB 完整样本一行。保留主键、两组去重唯一键、原始点集 JSON、正文摘要、身份和顺序、采集／保存／有效截止时间及索引。仅新增可空 `source_type VARCHAR(8)`，限定精确值 `daa` 或 `external`，并将 `config_revision`、`group_id` 的原 `VARBINARY(128)` 改为可空。 |
| `plc_facts_latest_points_v2` | `plc_facts_latest` | 每个 `(plc_id, db_number, point_id)` 一行。保留全部列、值、来源身份、顺序水位、主键、检查和截止索引。 |

**R02 请求、字段与回执。** 保留 `POST /api/v1/integration/plc-facts/samples` 和 `contractVersion=plc-facts/v2`。一次提交同一来源、PLC、DB 的一份完整样本。

| 字段 | 要求和归属 |
| --- | --- |
| 样本必填 | 发送方提供 `contractVersion`、`instanceId`、`sampleId`、`plcId`、`dbNumber`、`sourceGeneration`、`sourceSeq`、`points`。身份、DB 号范围、十进制序号和点数沿用 BE-012 r4。 |
| 采集组与配置版本 | `daa` 必须提供合法非空的 `groupId`、`configRevision`。已登记的 `external` 可各自省略或显式传 JSON `null`，入库为 SQL `NULL`。提供非空值时沿用原标识规则，空字符串无效。 |
| 每个点 | 必填 `pointId`、`dataType`、`value`、`quality`、`observedAt`。`name` 可省略。正常点的 `reason` 省略或为 `null`。坏质量点的 `value` 为 `null`，`reason` 提供非空原因，缺测沿用 `missing`。值域、同样本唯一点标识、上海 `+08:00`、微秒精度、未来容差、512 点与 524288 字节上限沿用原约定。 |
| 后端生成 | 历史主键 `id`、正文 `content_hash`、样本采集时刻 `sampledAt`、保存时刻 `storedAt`、原值有效截止、入库时的 `sourceType`、提交回执由后端产生。HTTP 正文出现 `sourceType` 按未知字段拒绝。 |

校验仍使用实际发送的 UTF-8 字节并计算 SHA-256。省略与显式 `null` 即使持久化结果相同，也对应不同正文。有效期内按原身份和原字节重发返回既有重复确认，同一身份改正文返回 409。首次成功、冲突、未知提交、过期未确认、事务边界、迟到顺序及原有错误码保持。点的有效截止仍为原采集时刻加三个上海自然月再减 24 小时，历史取整份样本最早的点截止，最新值按点截止。清理历史删整行，最新清理保留原点水位，继续防止旧样本复现。清理预算计入新增历史元数据字节。 [样本与保留期原约定](../ARCH-BE-012-simplified-plc-facts/spec.md#2-写入与存储要求)

**R03 私有实例登记和权限。** 在 v2 仓外 profile 新增必填 `instances` 数组，每项精确为 `{instanceId, sourceType}`，实例 ID 唯一，类型仅 `daa`、`external`。现有 `credentials` 仍为 `{instanceId, tokenSha256}`，当前 `sources` 仍为 `{plcId, instanceId, sourceGeneration, dbNumbers}`。两者均引用已登记实例。每个 PLC 仍只允许一个活跃实例及代次，可配置允许的 DB 集合。不同 PLC 可由不同类型实例服务。每个实例使用独立随机 Bearer，后端按原规则查摘要、认出实例并取其登记类型。有效令牌只授权登记实例在获准 PLC、DB、代次写入。未认证为 401，身份／范围冒用为 403，获准实例的不合法正文为 422。缺失或无效的精确目标配置沿用 503。

`instances` 与凭据各自管理。吊销令牌移除相应 `credentials` 项，保留实例分类和活跃来源供原授权读取。变更真实生产者类型使用新的登记实例和按原合同切换代次。历史保存写入时的分类。实时读取先核对当前来源的实例和代次，再按该实例登记返回类型。最新表沿用原身份列。历史尚未核实的来源保留 SQL `NULL`。当前登记及实例名称均不足以给旧样本自动定性。 [既有准入基线](../../backend/app/plc_facts/README.zh-CN.md)

## 3. 迁移与恢复

**R04 唯一后继。** 新增 `backend/alembic/versions/20261111_1030_4e6a8b0d2f14_finalize_plc_facts_tables.py`，`revision=4e6a8b0d2f14`，`down_revision=3d5f7a9c1e23`。现有 Alembic 文件保留原字节，原应用表数保持，已退役九表继续缺席。迁移在在线 MySQL 8.4 目标的同一 Alembic 连接核验 schema、server UUID、上海偏移、确切前驱、两表名称／InnoDB／列／键／依赖及操作标识，按下表从经过验证的阶段继续。有界等待元数据锁，超时停在当前可核状态。切换窗口暂停采集 API 写入、维护清理和相关直库写入方。

首先用一条多表 `RENAME TABLE` 改名，然后用一条 `ALTER TABLE` 改历史两列空性、增加可空来源及类型约束，最后由 Alembic 登记 revision。两条 DDL 分别提交，登记也须核验。核对表级授权和有效账号访问，因为 MySQL 的旧表名专属授权不随改名自动转到新名。 [MySQL RENAME TABLE](https://dev.mysql.com/doc/refman/8.4/en/rename-table.html) · [MySQL DDL 隐式提交](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html) · [MySQL 原子 DDL](https://dev.mysql.com/doc/refman/8.4/en/atomic-ddl.html)

| 核到的状态 | 允许的后续动作 |
| --- | --- |
| 前驱版本，旧名两张齐全，新名均无，列和约束为基线 | 核对备份、守护目标、写入暂停和有效权限后执行两条 DDL，再登记后继。 |
| 前驱版本，新名两张齐全，旧名均无，列和约束仍为基线 | 核对同次改名记录、两表原列内容摘要、行数、键和目标后，通过同一 `alembic upgrade 4e6a8b0d2f14` 仅执行未完成的 ALTER 与登记。 |
| 前驱版本，新名两张齐全，旧名均无，历史三项元数据变更完整且新增来源仍为空 | 核对同次 DDL 记录、原列摘要、行数、键及目标后，通过同一升级入口完成登记。 |
| 后继版本，两张新名及新列定义完整，旧名均无 | 核对数据、权限和 profile，继续切换或结束。 |
| 任意其他名称、列、引擎、依赖、版本组合，或操作证据不符 | 保持维护窗口并报告实际状态，核清后再决定处置。 |

在线守卫按目标接收 `ACQ_FACTS_EXPECTED_SERVER_UUID`、`ACQ_FACTS_EXPECTED_SCHEMA` 和 `ACQ_FACTS_OPERATION_ID`。部分状态重跑还要求与本次记录匹配的 `ACQ_FACTS_RECOVERY_STAGE`（`renamed` 或 `altered`）和 `ACQ_FACTS_RECOVERY_EVIDENCE_SHA256`，先复算对账再使用。操作者保存阶段、目标身份、结构、行数、主键顺序的原列逻辑 SHA-256、历史自增水位、索引、权限和恢复材料。守卫重新核对真实数据库形态，恢复证据由执行和独立复核记录证明。只走受控在线升级，拒绝离线 DDL、手工 stamp 或自动重建。前向迁移的自动 downgrade 明确拒绝。需要回退时先隔离读写并核对新增记录和空值，按获批备份恢复或前向修复保全已有及新增事实。

**R05 既有来源采用。** 新迁移给原历史的 `source_type` 留空。若目标操作同时明确批准一份经核实的旧样本映射，可在完成 Alembic 登记后、恢复应用写入前执行一次有界的 DML。私有映射逐样本记录目标及操作 ID、原行主键、`instanceId`、`sampleId`、原正文摘要、核实类型和证据引用，先只读比对全部键和行数。执行时按上述行键和原摘要加 `source_type IS NULL` 参数化更新，仅赋值 `source_type`。事务内逐条核对恰好匹配一行、确认预期来源及原列摘要，任何不符整批回滚。若提交结果未知，先只读对账完整映射，全为空才可按原范围重试，全部匹配预期即记录完成，其他状态停在维护窗口。没有明确映射的行继续为空。3307 模拟来源可在已记录的发送证据能关联到指定样本且操作者明确审核映射时标 `external`。映射可与迁移同一份精确目标操作批准一并列出。证据中只留脱敏标识及摘要，原私有凭据和资料不进入仓库或日志。

## 4. 读合同和 Web

**R06 读入口、授权和查询。** 下表路径相对于 `/api/v1/acquisition-data`。沿用既有登录、`plc-facts-read`、HTTP 错误和 `code / message / data` 信封。实时报当前登记的 `sourceType`。历史摘要及详情的 `sourceType` 为 `daa`、`external` 或 JSON `null`，`groupId` 与 `configRevision` 为字符串或 JSON `null`。历史响应始终含这些键以及现有 `instanceId`。

| 接口 | 请求与返回 |
| --- | --- |
| `GET /latest` | `plcId`、`dbNumber` 必填。可传精确 `pointId`，按三列现有主键及来源、有效期查询，返回最多一个点。精确键无有效数据时为 200、`items: []`。仅给 PLC 和 DB 时仍返回该对按 `pointId` 排序的有效点。继续使用 `data.items`，实时点条目增加 `sourceType`。 |
| `GET /latest/browse`，operation ID `plc_facts_v2_latest_browse` | `plcId`、`dbNumber`、`pointSearch` 可分别省略。每行返回现有逐点字段和 `plcId`、`dbNumber`、`sourceType`。按 `plcId ASC, dbNumber ASC, pointId ASC` 排序，标识保持精确字节顺序。 |
| `GET /history` | `plcId`、`dbNumber` 可分别省略。必填上海 `+08:00` 的 `from`、`to`，按 `[from,to)` 查询，跨度大于 0 且不超过 7 天。沿用分页与样本摘要，按 `sampledAt DESC, id DESC` 排序。可查授权范围内未过期的旧代次历史。 |
| `GET /options`、`GET /history/{id}` | 选项沿用角色范围。详情保留字符串 ID 与完整点集，使用上述历史元数据。不存在、无效 ID、过期或越权详情统一 404。 |

后端对当前角色的精确授权 `(plcId, dbNumber)` 对与筛选求交集，管理员也限其显式 `readScopes`。单选 DB 号可覆盖拥有该授权 DB 的多个 PLC。均不传时读取全部授权对，空授权返回 200 空页。显式条件在授权对集合中无匹配为 403。登录失败为 401，缺读权限为 403，非法参数沿用 422。实时沿用当前实例、代次及逐点有效期。条件须在 SQL 计数与分页前生效，浏览器每个列表动作只发一次分页 GET。分页接口统一 `items / total / page / pageSize / totalPages`，默认第 1 页、50 条，页长 1–100，超出页返回空项及本次总数。实时搜索去首尾空白，空串等同省略，最多 128 字符，点名或 ID 按不区分大小写的字面子串匹配，`%`、`_`、反斜线按原字符处理。精确 `pointId` 沿用原 ID 规则和区分大小写的精确比较。

**R07 页面行为。** 未选 PLC、DB 时，实时显示授权范围有效点位的首屏。历史自动查进入时最近 24 小时。DB 下拉在未选 PLC 时显示授权 DB 号的去重升序并集，选 PLC 后显示该 PLC 的 DB。换 PLC 时清掉对新 PLC 不可用的旧 DB。清除 PLC 时保留仍有效的 DB。清除条件按剩余条件重查。两页新增 PLC、DB 和来源类型列，保留可调列宽、横向滚动、双语、PLC 选择布局和标题问号帮助。历史详情显示 PLC、DB、来源类型和实例 ID，未记录的来源显示「来源未记录」，为空的采集组和配置版本使用空值呈现。实时保留点名或 ID 搜索及刷新。历史沿用查询按钮／Enter 提交时间，PLC 或 DB 变化时按当前有效窗口重查。筛选和页长变化回到第 1 页，翻页沿用已提交条件。请求变更清掉旧结果及详情，只有当前请求可更新列表，空权限、空结果、查询失败及未登录保持各自反馈。

**R08 合同工件与兼容。** 旧 `openapi.json`、`schema.json`、`vectors.json` 原字节冻结。新增 `openapi-acquisition-r2.json`、`schema-acquisition-r2.json`、`vectors-acquisition-r2.json`，记录新运行时、通用正文形态、来源条件和回执／读取向量。鉴权后的条件字段由服务按 R02、R03 校验。旧历史的 `groupId`、`configRevision` 原为非空字符串，兼容性变化是相同历史路由可以返回 JSON `null`，实时和历史条目也新增 `sourceType`。既有严格类型读取方需支持新版读模型。Core Web 与候选一起验证。dev 切换前结合可见运行使用方重核实际影响，若存在仍依赖旧字段模型的调用方则先明确切换安排。沿用现有路径、机器协议标识和旧回执字段，另增加 R06 分页实时读入口。 [冻结 v2 工件](../../contracts/published/http-api/plc-facts-v2/openapi.json)

## 5. 允许改动

| 表面 | 文件与边界 |
| --- | --- |
| 存储与 API | `backend/app/plc_facts/` 下 `models/v2.py`、`v2_config.py`、`v2_domain.py`、`schemas/v2.py`、`api/v2.py`、`services/async_v2.py`、`crud/async_v2.py`、`crud/sync_v2_maintenance.py`。限 R01–R06、精确目标护栏和清理字段预算。只新增 R04 指定的 Alembic 文件。 |
| BE-010 兼容 | `backend/common/integration/storage.py` 仅追加已知 revision `4e6a8b0d2f14`，保留旧允许项。目标 UUID、schema、实际 revision 和采用证据必须精确相符。 |
| Web | `frontend-js/src/app/acquisition-data/` 下 `api/index.js`、`composables/useAcquisitionScope.js`、`views/realtime/index.vue`、`views/history/index.vue`、`views/history/HistoryDetailDialog.vue`、`locales/zh-CN.json`、`locales/en-US.json`，在 QA5 候选上实现 R07。 |
| 合同与手册 | `contracts/published/http-api/plc-facts-v2/` 下 R08 三个新增工件及 `README.md`、`README.zh-CN.md`。`backend/app/plc_facts/` 和 `backend/scripts/plc_facts_maintenance/` 的 `README.md`、`README.zh-CN.md` 更新表、来源、精确 head、清理和操作指引。`backend/scripts/business_time_adoption/` 双语 README 仅补上述允许 revision。`backend/` 双语 README 仅增当前后继和迁移指向。 |
| 定向回归 | `backend/tests/` 下 `test_plc_facts_v2.py`、`test_legacy_acquisition_retirement.py`、`test_mapping_migration.py`、`test_equipment_temperature_migration.py`、`test_business_integration_migration.py`、`test_business_integration_storage.py`，限当前后继、模型、精确采用及新版合同适配。新增 `backend/tests/test_acquisition_data_browse.py`、`backend/tests/test_acquisition_facts_migration.py`、`backend/tests_mysql/test_acquisition_facts_r2.py`。前端限 `frontend-js/tests/module-registry/acquisition-data.test.mjs`，浏览器夹具和构建输出放任务临时目录。冻结的 ACQ-002 MySQL 入口和旧 B runner 在其固定候选运行。 |
| 记录和索引 | 本 bundle 的三个角色文档按阶段维护。协调者机械同步根 PLAN、backend PLAN、frontend-js PLAN、contracts PLAN 及任务目录的现行条目与双语对应项。共用 `CODE_INDEX.md` 限本任务路径和入口。既有任务批准、QA 证据和历史合同留在原处。 |

后端按 `backend-arch`、页面按 `frontend-ui` 与 `i18n-workflow`，关键源码头部及索引按 `code-document-indexer`。获准的隔离环境运行按实际环境采用 `docker-project-ops` 与 `docker-expert`。仅在本节允许的源码面作变更。

## 6. 验收、隔离与 dev 切换

| 编号 | 可核对结果 |
| --- | --- |
| AC01 源与鉴权 | 两种实例各有正常入库及独立来源类型。错误或吊销凭据为 401，错实例、PLC、DB 或代次为 403。证明每 PLC 单活跃、不同 PLC 可用不同来源，以及吊销 token 后获准读取现有实时数据。输入 `sourceType`、伪造或不合法的来源配置 fail closed。 |
| AC02 写入与保留 | DAA 两项元数据都合法才可写，缺项或 `null` 为 422。外部两项分别支持缺省及 JSON `null`，合法实值按原值保存，空串为 422。同正文重试与保留期内旧样本原字节重试按既有规则重复确认，省略改成 `null` 的重发为 409。核对冲突、回执、有效截止、原值格式和点水位。在隔离目标对含空元数据的外部样本验证清理 plan、apply 及字节预算。 |
| AC03 迁移与恢复 | 在非空隔离目标从精确前驱升级，对账原列、两组唯一键、主键／索引、最新水位、历史自增、其他表和已退役表状态。分别在 RENAME 后、ALTER 后、登记后中断并核验 R04 各恢复结果。错目标、未授权阶段、混合名称或列、外部依赖及锁超时停在合法阶段。核对旧来源为空与证据映射 DML 的限定列、错键和原子回滚。 |
| AC04 授权读取 | 用多 PLC、交叉 DB 和至少两种角色合成证据核对缺省、部分／完整筛选与显式越权，含管理员显式范围、空范围、总数、排序、分页、过期及旧代次。精确点位 0／1 行，大小写、字面通配字符、REAL 精度和历史空值均符合合同。 |
| AC05 Web | 首入两页均有对应默认查询。核对 SQL 页与显示来源／PLC／DB、24 小时上海窗口、7 天边界、DB 并集和筛选清除、迟到响应、详情实例与来源、未记录的历史来源。复核 QA5 已通过的标题帮助、PLC 选择、双语和窄屏，验证一页一次列表请求。 |
| AC06 兼容与交付 | 原冻结三工件哈希与旧 migration 字节守恒，新 OpenAPI／Schema 与运行时相符。固定旧合同和新版差异可追溯。同步、异步目标守卫核对精确后继，旧 profile 或错目标闭合。BE-010 保留全部已知 revision，旧实际凭据失配仍拒绝。正例只用隔离合成采用材料，保持 dev 现有 business owners 的关闭／未采用状态。 |
| AC07 指定 dev | 仅在精确切换授权后，复核第 6 节目标、许可、备份、候选、维护窗口及最终正式工作树。在原列数据和实际表对账一致后，通过 8000 API 和 5190 Web 只读复核已知样本、来源和筛选。列明采用的真实 profile 摘要及操作范围。 |

**源码及隔离证据。** 使用项目锁定 `uv`、`pnpm`。在无真实配置的隔离源码副本进入 `backend/`，设置候选 `PYTHONPATH` 并核对关键模块解析位置，执行 `uv run --offline --frozen --no-sync python -m compileall -q app/plc_facts` 和 `uv run --offline --frozen --no-sync python -m pytest -q -m no_db` 定向测试第 5 节的八个后端离线文件。合成 ASGI 与 MySQL SQL 构造验证路由和权限。前端在 `frontend-js/` 执行 `pnpm check:modules`、`pnpm test:modules`、`pnpm build` 与实际浏览器夹具。另在本次明确指定的 dev MySQL 实例专属 schema 中定向执行 `tests_mysql/test_acquisition_facts_r2.py`，实证 DDL、真实写读、清理及恢复。所有实际命令、退出码、环境、候选摘要、兼容差异及限制记入角色记录。

**本次隔离目标。** Human Owner 指定直接复用 `127.0.0.1:3307` 现有 MySQL 8.4.6。Development 独占 `arch_acq003_dev_upgrade`、`arch_acq003_dev_renamed`、`arch_acq003_dev_altered`、`arch_acq003_dev_guard`，fresh-context Verification 独占对应的 `arch_acq003_qa_upgrade`、`arch_acq003_qa_renamed`、`arch_acq003_qa_altered`、`arch_acq003_qa_guard`。两轮分别使用只授权各自四库的非 root 账号。连接前核对同实例 UUID、端口、实际 schema 和账户权限，合成写入、迁移、锁竞争、故障和清理限各自专属 schema 及连接。该执行方式使用同实例 schema 隔离，沿用现有 MySQL 服务。测试完成后由根协调者回收八个专属 schema 和两个专属账户，保留脱敏证据。具体账户、凭据和 UUID 保存在仓外私有操作记录，公共角色记录使用目标名及摘要。

**指定 dev 切换。** 本次原业务目标为 `127.0.0.1:3307` 的 `industrial_level_2_system`，对应 `127.0.0.1:8000` 后端、5190 Web。Human Owner 对后续任务使用 dev 库和 Alembic 的持续授权、本 r2 实施批准及此次直接使用 dev 的指示共同作为执行依据。8000 已知使用正式后端工作树并自动重载，Development 先在隔离候选开发验证。隔离验证通过后，由根协调者记录唯一服务端 UUID、schema、进程和账号、预期前驱／后继、备份、可见使用方、写入暂停、采用的旧样本映射及恢复方法，按本授权组织同窗切换。操作时重新验证两张原表在位、新名未占用、依赖和元数据可见性、旧表专属与数据库级有效权限、新名可用的同等应用权限，以及备份可恢复。任何需要实际改授的权限在具体操作记录中列明。

在同一窗口暂停受影响运行入口，保留旧候选及旧 profile 的私有备份。逐项核实新 `instances` 对凭据和活跃来源的覆盖及真实来源分类，准备仓外私有 r2 profile，权限 0600。保留原目标 UUID、schema、角色范围、实例、代次和凭据摘要，将 `target.schemaRevision` 改为精确后继。已启用的既有来源分类由操作者按证据或明确登记决定，原采集事实仍按 R05 确认。执行 Alembic、对账并按批准采用映射后，将正式源码、数据库和新 profile 同窗接齐并重新加载。校验 HTTP 和同步清理目标守卫，恢复前只读验证 8000 与 5190。原业务 schema 按 R04、R05 执行获准迁移及经审核的来源采用，功能验收使用其已有记录与正常只读查询。合成样本写入、故障注入和到期清理在上述专属 schema 完成。正式交付必须核对正式工作树与已验证候选的内容一致。

## 7. 修订、边界和交接

| Revision | 日期（上海） | 内容和状态 |
| --- | --- | --- |
| r1 | 2026-11-11 | 默认授权浏览与可选筛选草案，SHA-256 `9f78bba3e61cb9fe2574a1033830877124c2be48b889535658bba4d9af668a9a`。未获实施批准，由 r2 吸收原浏览范围。 |
| r2 | 2026-11-11 | 纳入两表改名、外部来源可空元数据、实例登记、精确点位查询、历史恢复及兼容验证。Human Owner 已明确批准实施，状态为 `owner_approved`。 |

跨设备读取采用服务端授权交集和分页。严格依赖旧历史非空字段的读取方须在目标切换前核清。迁移失败按 R04 留在经核验阶段，恢复过程继续暂停写入。新版 Web、后端、数据库和 profile 作为同一目标的切换组。Development 按本获批范围记录候选和自检，交 fresh-context Verification。Human Owner 依据实际候选和运行证据决定最终验收。 [开发工作流](../../.codex/workflows/development-lifecycle-workflow.md)

### 7.1 r2 实施范围批准

Human Owner 于本会话明确表示「批准 ARCH-ACQ-003 r2 实施」。PM 于上海时间 2026-11-11 11:09:58 将该批准登记到本规格。获批待审稿 SHA-256 为 `bc2a50cd56e536d9f8e54789e6fa322b4da53e133a46220bba04b1745bc6683d`，本次仅补充批准和交接状态。主协调者为 `/root`，后续按第 6 节实施与验证，最终验收归 Human Owner。

### 7.2 本次 dev 执行方式与运行授权

Human Owner 在资源讨论中先指示暂不开容器，随后明确「直接用dev的库就好了，本来就是开发用的」。结合此前「批准你直接用 alembic即可，后续任务直接用dev的库」及第 7.1 节 r2 批准，本次执行使用第 6 节已指定的同实例专属 schema 及原业务 schema。根协调者负责资源建立、两个角色的权限隔离、隔离验证后的原库 Alembic 和源码／profile 同窗切换，以及专属资源回收。

根协调者在资源分配时报告两专属账号连接 `industrial_level_2_system` 均以 MySQL 1044 拒绝，原业务库仍为 `3d5f7a9c1e23`，原两表各 2 行。该报告属于协调者的实际操作记录，后续独立验证依各角色证据归档。PM 于上海时间 2026-11-11 11:36:40 补记运行方式。补记前规格 SHA-256 为 `20bfb16926e7c3869e1766478ab60cb88fa061828cf7083a8e13050b46ceb744`，第 2–5 节功能、允许文件及 AC01–AC07 验收仍按已获批 r2 执行，原待审稿和批准登记摘要均保留。
