Task ID: ARCH-BE-012
Revision: r4
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Development 执行已批准的 ARCH-BE-012 r4 实施与 A 源码验证
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 后端完整 DB 样本写入、逐点最新值及原值查询
Owner: AIIS ICS Architecture Backend
Acceptance Chain Reference: 本 spec 第 5 至 7 节及 Development Lifecycle Workflow
Related Task: ARCH-ACQ-001, ARCH-BE-009, ARCH-BE-010, DAA-010, ARCH-FE-005, ARCH-ACQ-002
Created: 2026-11-10
Updated: 2026-11-10

# 简化后端采集事实存储与接口

## 1. 目标与边界

这是[根级统筹](../ARCH-ACQ-001-acquisition-data-coordination/spec.md)的第 1 项。后端交付完整 DB 样本的写入接口、两张值表和授权只读查询。后端合同固定、独立验证通过及本任务 Human Owner 最终验收后，由[主-DAA 的 DAA-010](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/spec.md)另行申请精确实施批准。[ARCH-FE-005](../ARCH-FE-005-acquisition-data-module/spec.md)承接 Web 页面。

`plc-facts/v2` 与[ARCH-BE-009 v1 合同](../../contracts/published/http-api/plc-facts-v1/README.zh-CN.md)并行，分别准入。既有 v1 及 [ARCH-BE-010 业务接口](../ARCH-BE-010-anonymous-business-integration/checklist.md)的精确 schema 核验按 §4.2 支持后继迁移。业务记录与永久回执及[设备实时状态和过程监控](../ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md)依各自任务管理。DAA SQLite/上报实现、Web 页面、SMA 接线、[旧 Projection 清退](../ARCH-ACQ-002-legacy-projection-retirement/spec.md)、发布、实际数据库采用和现场运行均为独立范围。

## 2. 写入与存储要求

**R01 单入口、单样本。** `POST /api/v1/integration/plc-facts/samples` 每次接受同一实例、一个 PLC、一个 DB 的一份已冻结样本。完整点集是样本配置中该 PLC/DB 全部启用上报的点，首版要求属于同一采集组和周期。DAA 可分段读取并保留各点实际 `observedAt`。同轮采集两个 DB 发两次 POST，各有样本 ID、事务和回执。DAA 在冻结前核对完整点集，将读失败或缺测点也写入样本。后端核验来源、字段、点集结构和点标识唯一性。后端首版没有应报点注册表。实时和补传共用此入口。

**R02 双上限与字段。** 每份样本 1–512 点，bad/missing 同样计数。实际 UTF-8 JSON 正文最多 512 KiB（524288 字节），在整体验证前有界读取，计入空白，涵盖分块传输。超任一上限两表均零写入。512 是本项目首版 HTTP 合同的上限。DAA 现行 256 点采集组约束由 DAA-010 后续承接。媒体为 `application/json`，若声明 charset 则须为 UTF-8，仅接受 identity 编码。拒绝重复 JSON 键、未知字段、无效 UTF-8、重复 `pointId`、字符串冒充数字及非有限数值。

| 层级 | 字段与约束 |
| --- | --- |
| 样本 | `contractVersion` 固定 `plc-facts/v2`。`instanceId`、`sampleId`、`plcId`、`dbNumber`、`groupId`、`configRevision`、`sourceGeneration`、`sourceSeq`、`points` 全部必填。`dbNumber` 为 JSON 整数 1–65535。`sourceSeq` 为无符号、无前导零的十进制字符串，范围 1–9223372036854775806，入库转为有符号 BIGINT。 |
| 标识 | 各 ID、`configRevision`、`sourceGeneration` 及 `pointId` 均为 1–128 UTF-8 字节，精确区分大小写，不规范化 Unicode，无首尾空白和 ASCII 控制字符。`name` 可省略或为空串，此时展示 `pointId`，提供时最多 100 UTF-8 字节。 |
| 点 | `pointId`、`dataType`、`value`、`quality`、`observedAt` 必填。`good` 提供合法类型值，`reason` 可省略或为 null。`bad` 的 `value` 必须为 null，`reason` 为 1–128 UTF-8 字节的非空原因，缺测使用 `missing`。失败点使用本次读取尝试的时刻。 |
| 时间 | `observedAt` 为带 `+08:00` 的 RFC 3339，秒的小数精度 0–6 位。超过已核验的数据库上海时钟 5 分钟、超出可存范围或超精度则整份拒绝。输出带 `+08:00` 并保留已存精度。 |

| `dataType` | `good` 点的合法 JSON 值 |
| --- | --- |
| `BOOL` | 布尔值。 |
| `BYTE`、`USINT` | 整数 0–255。 |
| `INT` | 整数 −32768–32767。 |
| `WORD`、`UINT` | 整数 0–65535。 |
| `DINT` | 整数 −2147483648–2147483647。 |
| `DWORD`、`UDINT` | 整数 0–4294967295。 |
| `REAL` | 可解码为有限 IEEE 754 binary32 的 JSON 数字，拒绝溢出，保留 DAA 上报的原数值精度。 |
| `CHAR` | 单个 ASCII 字符。 |
| `STRING[n]` | ASCII 字符串，`n` 为 1–254 的规范十进制上限，实际长度 0–`n`。 |

合法 `0`、`false`、`""` 保留各自值。`configRevision` 是来源元数据。

**R03 两张值表。** 标识列使用按字节比较的 `VARBINARY(128)`，两表的 `db_number` 使用 `SMALLINT UNSIGNED` 并限定 1–65535，日历列使用上海本地 `DATETIME(6)`。

| MySQL 表 | 行粒度和键 | 字段与索引 |
| --- | --- | --- |
| `plc_facts_samples_v2` | 每样本一行，`id BIGINT` 自增主键。`(instance_id, sample_id)` 与 `(instance_id, plc_id, db_number, source_generation, source_seq)` 分别唯一。 | `instance_id`、`sample_id`、`plc_id`、`db_number`、`group_id`、`config_revision`、`source_generation`、`source_seq BIGINT`、`points_json JSON`、`content_hash BINARY(32)`、`sampled_at`、`stored_at`、`expires_at`。索引 `(plc_id, db_number, sampled_at, id)` 及 `(expires_at, id)`。 |
| `plc_facts_latest_points_v2` | 每 PLC/DB/点一行，`(plc_id, db_number, point_id)` 主键。 | `point_name`、`data_type`、`value_json JSON`、`quality`、`reason`、`observed_at`、`expires_at`、`instance_id`、`source_generation`、`source_seq BIGINT`、`sample_id`。索引 `(expires_at, plc_id, db_number, point_id)`。点值及观察元数据可置空，顺序水位见 R06。 |

`sampled_at` 取样本最晚的 `observedAt`，历史 JSON 保留各点实际时间。`stored_at` 记录后端数据库保存时刻。样本与最新值间无级联外键。历史 `expires_at` 取点集中最早的有效截止，latest 按各点计算。

**R04 原子提交与回执。** 后端对冻结的实际 UTF-8 JSON 正文字节计算一次 SHA-256。在一个 Service 事务中写历史、按点条件更新 latest，持久提交后才响应。有效期内，同一实例、样本 ID 和同字节正文返回 `committed / duplicate`。同身份异正文，或同实例/PLC/DB/代次下同序号另占样本 ID 返回 409。两个 DB 可共享序号。并发由数据库唯一约束裁定。结果未知或回执丢失时重传原冻结正文及身份，收到匹配的明确提交回执才能确认该样本。有效期外不承诺保存确认凭据，来源持续保证样本身份和同一 DB/代次序号唯一。

**R05 凭据与来源顺序。** `plc_facts` manifest 分别挂载 v1、v2。v2 模块本地默认 `PLC_FACTS_V2_ENABLED=False`、`PLC_FACTS_V2_PROFILE_FILE=""`。启用时读取仓外私有配置，明确目标 alias、MySQL server UUID、schema、revision，按实例列机器凭据摘要，按 PLC 显式绑定唯一当前 `(instanceId, sourceGeneration)` 和允许的 DB，另设 §3 的读范围。空准入拒绝所有，无通配。每个实例一个独立、可吊销的机器 Bearer，凭据用至少 32 随机字节生成，后端仅保存 SHA-256 摘要并作常量时间比较。不同实例的摘要必须互异。凭据通过请求头发送，真实凭据不进入日志、响应和示例。非隔离 loopback 运行须用获批的受保护传输。无效凭据为 401，有效凭据与自报实例或其 PLC、DB、代次范围不符为 403。关闭、未配置、配置无效或目标未就绪时 v2 失败关闭。

后端核验目标 MySQL 8.4 的 server UUID、schema、单一 Alembic revision 和会话 UTC 偏移 `+08:00`。私有配置及实际目标的 revision 都须为 §4.2 的 `2c4e6a8b0d12`。用该数据库时钟判定未来容差及过期。配置版本只作来源元数据，同来源代次逐点按 `sourceSeq` 比较。较旧样本可追加历史，较大序号才可覆盖同代次 latest。活跃代次可从 1 开始替换旧代次值。写入以数据库原子条件裁定，bad/missing 可以成为更新后的质量。只返回活跃代次的 latest，授权范围内旧代次历史仍可查。

换实例、换代次或 SQLite 序号重置前，暂停相关写入，排空或对账旧待确认和在途样本，统一更新私有准入并使所有后端进程采用同一配置，再恢复写入。旧代次从切换起拒绝写入，每次采用新代次。轮换或吊销凭据无需重置仍有效来源的序号。

**R06 保留与清理。** 每点物理清除上限是其原采集时刻加三个上海自然月，目标月不存在同一日时收敛至最后有效日。有效截止 `expires_at` 为该上限提前 24 小时。数据库上海时钟达到有效截止时，立即隐藏原值，补传或原样重试均返回 `expired_unconfirmed`。历史整样本按最早截止判定。以上判定与物理清理进度独立。补传、重试及查询不延长留存。

在现有 `plc_facts_maintenance` 新增 `cleanup-v2 --plan|--apply`。裸命令仅显示帮助。命令显式指定目标 alias、schema、预期 server UUID、精确 revision、批准标识及确认人。核对实际目标及上海时钟，apply 另要求维护开关和精确确认串。按截止时间及键排序，跳过被锁行，写入时复核截止及行版本，避免擦除刚推进的 latest。整行删除过期历史。latest 清空值、名称、类型、质量、原因、观察时间、样本标识及 `expires_at`，只保留点键、实例、代次、序号以阻止旧样本使过期值复现。

外部每分钟执行一次。每事务最多 200 行及 2 MiB 待清数据。每次执行累计最多 2000 行、20 MiB 和 2 秒处理预算，任一先达即停止继续取批，事务和锁等待有界。工具输出脱敏 JSON Lines，含处理行/字节数、最早仍到期时间和成功完成时刻。10 分钟无成功执行或最早积压超过 1 小时告警，空跑成功也计心跳。24 小时供正常清理、告警与恢复使用，无法覆盖超过余量的停运。范围限在线新版事实表。备份、存储日志、离线副本及现场调度和告警接线由独立运行批准管理。

**R07 查询边界。** 两张值表只交付逐点最新状态和采集时间历史。发布序号、发布状态表和按提交顺序续读归独立任务。若需自首份 v2 样本起覆盖可靠提交回放，须在启用前确定并批准回放合同。

## 3. 查询与合同工件

**R08 浏览器只读面。** 复用现有登录和角色权限，声明 `plc-facts-read`，不加入默认非 admin 权限列表。私有配置按现有角色显式列出可见 `(plcId, dbNumber)`，默认空，适用于 options、latest、history 和 detail。admin 沿用 Core 权限键豁免，也须有显式 PLC/DB 读范围。读范围独立于机器当前写入范围。未登录或失效登录为 401，登录后无权限或指定越权 PLC/DB 为 403。详情的不存在、过期及越范围 ID 统一为 404。空范围的合法 options 查询返回空选项，合法范围无数据返回空列表。读面只返回未达有效截止的原值，latest 还须满足 R05 的活跃代次条件。

| 接口 | 参数与响应 data |
| --- | --- |
| `GET /api/v1/acquisition-data/options` | 返回 `items`，元素为 `plcId`、`dbNumbers`，来自账号角色的允许范围。 |
| `GET /api/v1/acquisition-data/latest` | 必填 `plcId`、`dbNumber`，返回 `items`，按精确 `pointId` 排列。每点含名称、类型、原值、质量、原因、观察时间及来源实例/代次/序号/样本 ID。 |
| `GET /api/v1/acquisition-data/history` | 必填 `plcId`、`dbNumber`、`from`、`to`。上海半开区间 `[from,to)`，时间格式同 R02，`to > from`，跨度最多 7 天。`page` 默认 1，`pageSize` 默认 50、上限 100。按 `(sampled_at DESC, id DESC)` 排序，返回统一分页 `items / total / page / pageSize / totalPages`。摘要含 ID、样本/来源元数据、`sampledAt`、`storedAt`、点数。 |
| `GET /api/v1/acquisition-data/history/{id}` | 同一授权范围和截止检查，返回摘要及完整 `points`。请求路径和摘要、详情响应中的 `id` 均为无前导零的正整数十进制字符串，以保存 BIGINT 精度。 |

**R09 回执与合同工件。** 使用现有 `code / message / data` 信封。机器请求错误含稳定 `errorCode`，实际 HTTP 状态与 `code` 一致。非成功结果不含提交状态或成功类型，客户端保留待确认事实。

| HTTP 状态 | `errorCode` | 处理口径 |
| --- | --- | --- |
| 401 / 403 | `plc_facts_v2.invalid_credential` / `plc_facts_v2.scope_rejected` | 准入失败，无本次写入。纠正授权或配置后可重试原样本。 |
| 409 | `plc_facts_v2.sample_content_conflict` | 样本身份或流内序号占用与原正文不符，无本次写入。对账后由操作方处理。 |
| 410 | `plc_facts_v2.expired_unconfirmed` | 达有效截止，无本次写入、无成功凭据。DAA 后续记录未确认过期。 |
| 413 / 415 / 422 | `plc_facts_v2.payload_too_large` / `plc_facts_v2.media_type` / `plc_facts_v2.invalid_request` | 正文超限、媒体编码不符、字段/点数/类型/时间不合法。无本次写入。 |
| 503 | `plc_facts_v2.not_ready` / `plc_facts_v2.commit_outcome_unknown` | 前者为目标或服务未就绪、已知无本次提交。后者为无法判定，保持待确认并重试同一身份和原正文。网络无响应同按未知处理。 |

在 `contracts/published/http-api/plc-facts-v2/` 固定 OpenAPI、JSON Schema、脱敏请求/回执及失败向量、双语说明。与类型化 Schema、迁移和实际 HTTP 对照。读错误使用项目通用响应约定。合同工件固定与 Git 发布、实际部署分开。

### 3.1 PLC-A DB21 样本链路

DAA 从 SQLite 取已冻结样本，用 `Authorization: Bearer <instance-machine-token>` 发 POST。以下为温控组两个应采点的合成请求。

```json
{
  "contractVersion": "plc-facts/v2",
  "instanceId": "daa-a",
  "sampleId": "sample-102-db21",
  "plcId": "PLC-A",
  "dbNumber": 21,
  "groupId": "temperature",
  "configRevision": "rev-12",
  "sourceGeneration": "gen-a",
  "sourceSeq": "102",
  "points": [
    {
      "pointId": "furnace_temp",
      "name": "炉温",
      "dataType": "REAL",
      "value": 820.5,
      "quality": "good",
      "observedAt": "2026-11-10T10:00:02.120+08:00"
    },
    {
      "pointId": "heating_ready",
      "name": "加热就绪",
      "dataType": "BOOL",
      "value": false,
      "quality": "good",
      "observedAt": "2026-11-10T10:00:02.125+08:00"
    }
  ]
}
```

通过校验后在一笔事务内写历史和可更新的 latest。假设历史行 `id=501`，其 `sampled_at` 为上海时间 `2026-11-10 10:00:02.125`，`points_json` 保存完整点集。历史有效截止为 `2027-02-09 10:00:02.120`，物理清除上限为 `2027-02-10 10:00:02.120`。

| 最新值行 | 原值 | 点采集时间（上海） | 有效截止（上海） | 来源序号 |
| --- | --- | --- | --- | --- |
| PLC-A / DB21 / `furnace_temp` | `820.5` | `2026-11-10 10:00:02.120` | `2027-02-09 10:00:02.120` | `102` |
| PLC-A / DB21 / `heating_ready` | `false` | `2026-11-10 10:00:02.125` | `2027-02-09 10:00:02.125` | `102` |

持久提交后的 HTTP 200 回执如下。

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "contractVersion": "plc-facts/v2",
    "instanceId": "daa-a",
    "sampleId": "sample-102-db21",
    "status": "committed",
    "outcome": "created"
  }
}
```

丢失回执后，在有效期内重发相同正文取得 `committed / duplicate`，历史仍为一行。保留期内迟到的 `101` 追加历史，示例两点最新值保持 `102`。有效截止起，原样重试返回 410，不论物理清理进度。Web 最新查询可看到两行，历史列表包含摘要行 `501`，`GET /api/v1/acquisition-data/history/501` 返回完整点集，三处均执行读范围检查。

## 4. 实施范围与既有版本兼容

### 4.1 精确文件范围

以下为 r4 的文件允许范围。现有文件只允许本表所列的局部修改。路径或范围变化须返回 PM 修订后重新批准。

| 允许的文件 | 修改边界 |
| --- | --- |
| `backend/app/plc_facts/manifest.py`、`backend/app/plc_facts/models/__init__.py` | 注册新版路由、权限和错误键，导入新版 Model。既有 v1 路由、权限默认值和七表 `TABLES` 保持。 |
| `backend/app/plc_facts/v2_config.py`、`backend/app/plc_facts/v2_domain.py`、`backend/app/plc_facts/api/v2.py`、`backend/app/plc_facts/schemas/v2.py`、`backend/app/plc_facts/models/v2.py` | 模块本地 typed 设置、规则、API、Schema 和两值表。私有配置范式仅在新版说明给脱敏样例。 |
| `backend/app/plc_facts/crud/async_v2.py`、`backend/app/plc_facts/services/async_v2.py`、`backend/app/plc_facts/crud/sync_v2_maintenance.py`、`backend/app/plc_facts/services/sync_v2_maintenance.py` | 新版异步写读、同步清理。Service 持有事务，CRUD 提供有界数据库操作。 |
| `backend/alembic/versions/20261110_2000_2c4e6a8b0d12_add_plc_facts_v2.py` | 唯一增量迁移，精确后继见 §4.2。 |
| `backend/app/plc_facts/crud/sync_maintenance.py`、`backend/common/integration/storage.py` | 仅 §4.2 的两处已知后继兼容。 |
| `backend/scripts/plc_facts_maintenance/main.py`、`backend/scripts/plc_facts_maintenance/README.md`、`backend/scripts/plc_facts_maintenance/README.zh-CN.md` | 新增 R06 显式子命令及说明，旧 `status/adopt/cleanup` 入口保留。 |
| `backend/tests/test_plc_facts_v2.py`、`backend/tests_mysql/test_plc_facts_v2.py` | 新版离线和独立 MySQL/HTTP 验收入口。 |
| `backend/tests/test_business_integration_migration.py`、`backend/tests/test_business_integration_storage.py`、`backend/tests_mysql/test_business_integration.py` | 固定 BE-010 的 75 表基线前缀，添加精确后继兼容覆盖。旧夹具目标、既有断言的旧版含义和原验收记录保留。 |
| `contracts/published/http-api/plc-facts-v2/README.md`、`README.zh-CN.md`、`openapi.json`、`schema.json`、`vectors.json`（同目录） | 仅新增 R09 工件。 |
| `contracts/README.md`、`contracts/README.zh-CN.md`、`contracts/PLAN.md`、`contracts/PLAN.zh-CN.md` | 新版合同索引和唯一源码后继说明。 |
| `backend/app/plc_facts/README.md`、`backend/app/plc_facts/README.zh-CN.md`、`backend/PLAN.md`、`backend/PLAN.zh-CN.md`、`CODE_INDEX.md` | 新版模块、当前迁移链和关键源码索引。 |
| `plans/ARCH-BE-012-simplified-plc-facts/tasks.md`、`checklist.md`、`evidence/`（同目录） | 分阶段交接与脱敏证据，写入按 STD 角色。 |
| `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md` | 由协调者机械同步本任务行。 |

复用现有登录、角色权限、数据库会话、时间工具及基础响应。主 `.env` 示例、真实配置和依赖锁不动。实现与验证按 `backend-arch`，维护工具叠加 `backend-script-tooling`，跨端错误、状态与文案交接按 `i18n-workflow`。测试使用项目 `uv` 与锁定依赖。

### 4.2 精确迁移与旧接口

- 源码后继固定为 `1b3d5f7a9c20 → 2c4e6a8b0d12`，单一 head。增量迁移仅创建 R03 的两表、键和索引，既有迁移文件、表定义与行保持。新 head 应用表 77 张，不计 `alembic_version`。无历史回填、搬迁或 `stamp`。空表降级守卫先核对两表均为空再 drop，仅在获批可丢弃库演练。非空或无法检查时拒绝。
- v1 的 `0a2c4e6f8b10`（71 表）及 `1b3d5f7a9c20`（75 表）profile 保留。新 profile 精确期望旧 75 表加两张 v2 表。原七表 `TABLES` 和 F7 指纹算法保留。已采用的 v1 在新 head 与旧证据失配时拒绝服务，需获准运行原 `adopt --revalidate-schema-only`，匹配原 adoption ID 和 storage epoch，只更新 schema 及其证据/时钟字段，保留 F7、epoch、来源、值和回执。此前未采用的目标继续未采用。
- BE-010 只在采用证据校验中接受旧 `1b3d5f7a9c20` 与新 `2c4e6a8b0d12` 两个明确 revision。运行时 server UUID、schema、revision 仍与证据逐项精确匹配，保留固定列摘要、时间基准及原审批证明要求。已采用业务模块的旧 manifest 在新 head 失配，需获批的目标专属新 revision 外部证据才能恢复。此前未启用的入口继续关闭。八路合同、业务表、数据、永久回执及旧证据保留。隔离验证使用合成证据，源码不签发或重写现有 manifest。

## 5. 验收

| 标准 | 验证口径 |
| --- | --- |
| AC01 单样本和双上限 | 400 点、512 点合规样本成功，正文 524288 字节接收、524289 字节拒绝，分块传输也受限。正文合规的 513 点拒绝，超限对两表零写入。同轮两个 DB 独立提交和确认，另一个 PLC 同号 DB 隔离。对照合法 0、false、空串和 bad/missing，覆盖值域、标识字节数、重复键/点、非法时间和未来容差边界。 |
| AC02 原子、重试和结果未知 | 样例对账一行历史、两点 latest，独立连接看到两表同时提交。提交前故障无部分写入，提交后丢回执、结果未知及同身份并发重传按持久状态裁定。有效期内同正文确认，异正文及同序占用 409，两 DB 同序各自提交。 |
| AC03 准入与顺序 | 默认关闭、空范围、错目标/时钟、无效或吊销凭据、有效凭据冒用实例、越 PLC/DB/代次均拒绝。验证 102 后补 101、旧新并发、重启、配置修订、代次换新、bad/missing 及过期水位。切换后旧代次写失败，授权旧历史可查，新代次可从 1 起写。 |
| AC04 截止与物理清理 | 固定时钟验证截止前、相等、截止后、月末/闰年、混合点时间、补传、重复和清理前后 410。验证预览零写入、错目标失败、清理预算、并发更新、最小 latest 水位、积压及心跳输出。两张新版表仅清理到期原值，在物理上限前完成规定隔离样本，旧事实、旧数据和 BE-010 永久回执守恒。 |
| AC05 只读授权 | 覆盖未登录、无独立权限、无读范围的 admin、越范围和获准账号。选项不泄漏，命名范围越权 403，过期、不存在及越界详情 404。对照样例和空结果，验证页长、同时间并列、过期过滤、迟到样本和上海半开区间。 |
| AC06 迁移与兼容 | MySQL 空库全链和带合成旧数据的 75→77 升级，核对唯一 head、metadata、两表定义及旧表定义/行。v1 三路原行为、旧 profile 和精确后继均验证，旧采用证据先失败，再经获批的 schema-only 复核恢复。BE-010 八路在旧目标和精确后继验证，后继旧证据拒绝，合成新证据恢复。旧 monitor/Projection 路由、状态及数据保留。验证空库降级及非空或无法核对时拒绝。 |
| AC07 可消费工件 | 新增恰为两张值表，无第三张状态/游标表。OpenAPI、Schema、样例和正反向量与真实 HTTP 对照。交付机器准入/请求/回执与错误决策、读面参数和授权约定。 |
| AC08 稳态与清理容量 | 同一获批隔离实例走正常 FastAPI HTTP，2 个模拟 PLC 各每秒 1 份 64 点样本持续 30 分钟，成功接收端到端 P95 ≤500 ms。同期每分钟执行标准维护命令，预置 10000 行达到有效截止但未达物理上限的代表行，含历史与 latest，单份样本正文最高约 16 KiB。15 分钟内清理完成，无错清或原值复现。记录吞吐、样本分布、P95、失败、清理预算和滞后。该门槛适用于此隔离夹具。 |
| AC09 独立交接 | 锁定正式后端候选和迁移，记录实际命令、版本、退出码、限制、夹具及脱敏证据。Development 与 fresh-context Verification 各自独立复现。交接列出合同工件摘要、实际检查覆盖、QA 和 Owner 证据链接。 |

## 6. 数据库与执行门禁

**A 源码验证。** 使用正式工作树和仓库锁定的 `uv` 环境检查配置、模型、文档链接、合同、迁移图，并定向执行 `no_db` 单测及旧面回归，显式阻断数据库连接。B 使用独立入口，避开 `backend/tests/conftest.py` 中删表再建表的共享夹具。旧冻结 profile 测试的固有基线差异按实际输出记录。

**B 隔离验证。** Development 和 fresh-context Verification 分别使用可丢弃的 MySQL 8.4.6 实例、数据卷、临时非 root 账号与 schema。每轮含空库和带合成旧数据的升级库。仅发布隔离 loopback，使用正常 FastAPI 入口与合成发送器，通过明确的进程环境覆盖设置。隔离源码排除真实 `.env`、真实配置和数据。执行前提交独立操作计划，列明镜像、容器/卷/网络标识、端口、库名、账号/权限、server UUID 核验方式、时钟/故障夹具、迁移、压测、清理和回收步骤。Docker、数据库 DDL/DML、故障注入及回收只在获准的隔离目标执行，使用最小权限并保存足够的脱敏证据。

**现有 dev 库。** 上述隔离验证通过后，项目当前的专用 dev 库可用于另批的增量升级及兼容冒烟。升级前只读核验实际配置所指 server UUID、schema、版本、Alembic revision、上海时钟、其他使用方及 v1/BE-010 采用状态，验证备份及恢复路径，准备 §4.2 的兼容复核和切换窗口。先确认上一 head 匹配再执行增量。清空、故障注入、批量到期清理和降级演练限定在 B 的可丢弃库。本次规格审阅不需要连接、操作或识别实际 dev 库。

**回退。** 错目标、时间不符、错清或 latest 倒退时暂停新版准入及发送，保全新版事实及待确认样本，按提交结果对账后再选择旧链。恢复备份、删表、非空迁移降级及实际环境操作均需精确授权。本任务合同固定、独立 QA 通过及 Human Owner 最终验收后，才转 DAA-010 申请实施。

## 7. 修订与交接

| 日期（Asia/Shanghai） | Revision | 记录 |
| --- | --- | --- |
| 2026-11-10 | r1 | PM 将单入口、两值表、Web 只读面及 DAA 前置条件落为草案，供 Human Owner 审阅。 |
| 2026-11-10 | r2 | 补齐两表字段和键、DB21 请求、事务结果、回执及 Web 对账，收敛提交顺序续读范围。 |
| 2026-11-10 | r3 | 固定单 PLC、单 DB、单样本提交，每份 1–512 点及 512 KiB，补充独立提交和边界验证。 |
| 2026-11-10 | r4 | 固定首版字段及准入，每个 DAA 实例独立机器凭据、24 小时清理余量、精确后继与兼容、实施范围和隔离验收，提交 Human Owner 审阅。 |

### 7.1 r4 范围批准

Human Owner 于 2026-11-10（Asia/Shanghai）批准 `ARCH-BE-012 r4` 精确实施范围。获批的审阅稿 SHA-256 为 `db0f1d68168baf35bee9135f48e19086e663f72ed7c3376e81cd74ad3ee9fa0f`。

> 批准 ARCH-BE-012 r4 实施范围，先做后端，DAA 等后端验收后再做。

按 [STD 流程](../../.codex/workflows/development-lifecycle-workflow.md)交接 Development 执行后端实施及 A 源码验证。§6 的 B 隔离操作计划和现有 dev 库操作仍须分别批准。DAA-010 在后端合同固定、独立验证通过及 Human Owner 最终验收后才进入实施批准。
