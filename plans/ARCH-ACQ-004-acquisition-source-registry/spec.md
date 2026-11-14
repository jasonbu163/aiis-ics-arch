Task ID: ARCH-ACQ-004
Revision: r4
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 ARCH-ACQ-004 r4，交 Development 按本规格实施与自检。专用 MySQL 隔离环境待确认。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 单表登记 PLC 上报来源，DAA 与第三方共用采集数据接口
Owner: AIIS ICS Architecture 采集数据与 Automation World / DAA 上报接入
Acceptance Chain Reference: 本稿第 5、6 节及 Development Lifecycle Workflow
Depends On: ARCH-ACQ-004 r2 来源配置基线、ARCH-ACQ-003 r2 事实表和 DAA-010 单样本上报
Related Task: ARCH-ACQ-001, ARCH-TASK-001, DAA-010, DAA-013
Created: 2026-11-13 Asia/Shanghai

# 简化 PLC 来源登记

## 1. 目标与基线

管理员在 Web「采集数据 → 来源配置」为每台逻辑 PLC 登记一行。复制三个来源标识给 DAA 或第三方后，任一发送程序都可按同一套规则上报。DB 编号随样本发送。数据提交后，可按 PLC、DB 和时间读回。正常运行使用一张来源登记表、两张事实表，接入时填写四项。

Human Owner 已批准 r3，随后批准 DAA-013 r1 按每台本机 PLC 保存完整上报身份。r4 草案沿用 r3 的后端、Web、API、迁移和根采集指南范围，更新 DAA 接入分工与联合验收。r2 的六表隔离产品验证及指南复验保存在现有角色记录中，r3 原文及批准记录完整保存在文末。 [DAA-013 r1](../../automation-world/data-acquisition-agent/plans/DAA-013-multi-plc-reporting-identity/spec.md) · [r2 验证](checklist.md) · [r3 规格原文](#r3-获批历史)

## 2. 登记和接口

**R4-01 单表登记。** 在事实库使用 MySQL InnoDB 表 `plc_source_registry`，`plc_id` 为主键。四项业务输入如下。

| Web / API 字段 | 数据库列 | 含义 |
| --- | --- | --- |
| `plcId` | `plc_id` | 逻辑 PLC 标识，创建后固定，用于归集不同来源代次的历史 |
| `instanceId` | `instance_id` | 当前发送方标识，同一实例可上报多台 PLC |
| `sourceGeneration` | `source_generation` | 当前采样代次，更换发送方或需要重起采样序号时启用新值 |
| `sourceType` | `source_type` | `daa` 或 `external`，由管理员选择，供标注和展示 |

三个标识沿用原 1–128 UTF-8 字节规则，精确比较，保留大小写及原始字节。系统继续维护 `registrationRevision`、`createdAt` 和 `updatedAt`，并在同一行用 JSON 字符串数组记录已退役代次，用于接管时防重。系统字段无需在登记表单填写。来源标签可以单独修改，同一实例在其他 PLC 的标签由各行管理。表内只有当前登记及必要的系统记录，DB 读写清单从登记结构删除。

**R4-02 管理 API。** 沿用 `GET/POST/PATCH /api/v1/admin/acquisition-sources`、现有管理员登录权限及 `code / message / data` 信封。列表沿用分页与 PLC 字节序，每项返回四个业务字段、登记版本和时间。写操作成功提交后返回 HTTP `200`，`data` 包含 `outcome` 与提交后的 `source`。新增和更新在同一数据库上提交即生效，无需重启。管理请求、响应和表单移除 `dbNumbers`、`readDbNumbers`、`addDbNumbers`、`addReadDbNumbers` 和 DB 追加动作。提交后的结构化审计记录操作者、PLC、变化及结果。

| 操作 | 请求和结果 |
| --- | --- |
| POST 新增 | JSON 正文为四项业务字段。新 PLC 返回 `created`，四项完全一致的重试返回 `unchanged`。已存在 PLC 的不同登记返回 `409 acquisition_sources.source_conflict`，变更使用 PATCH。 |
| PATCH 编辑标签 | 正文传 `plcId`、`expected: {instanceId, sourceGeneration, registrationRevision}`、`action: "edit"`、`sourceType`。有变化返回 `updated`，相同标签返回 `unchanged`。 |
| PATCH 接管 | 正文传 `plcId`、同样的 `expected`、`action: "takeover"`、`replacement: {instanceId, sourceGeneration, sourceType}`、`confirmTakeover: true`。替换实例或重起采样序号时，必须使用该 PLC 的新代次。提交成功返回 `replaced`。 |

在行锁内核对 `expected`。实际变化更新版本及修改时间。预期版本相符且值相同的操作保留原版本和时间。找不到 PLC 返回 `404 acquisition_sources.not_found`，预期不符返回 `409 acquisition_sources.revision_conflict`。首次登记和接管检查该 PLC 可核实的已用代次。接管时检查当前和退役代次，以及两张事实表中仍可核实的代次，命中返回 `409 acquisition_sources.generation_reused`。操作员选择从未使用的新代次。字段非法或缺少接管确认返回 `422 acquisition_sources.invalid_request`。管理提交结果未知时沿用 `503 acquisition_sources.commit_outcome_unknown`，先 GET 核对当前登记再操作。

**R4-03 同一套上报规则。** 保留 `POST /api/v1/integration/plc-facts/samples` 和 `plc-facts/v2`。合法样本按 `plcId` 查当前一行，只匹配 `plcId`、`instanceId`、`sourceGeneration`。来源不存在或身份不符返回 `403 plc_facts_v2.scope_rejected`。`dbNumber` 仍是必填的样本字段，沿用 1–65535 的整数规则。只要身份与样本合规，同一来源可分别上报多个 DB。`groupId`、`configRevision` 对所有发送方均可省略、填 `null` 或有效标识。发送方使用现有样本正文，提交额外的 `sourceType` 返回 `422`。后端按登记值标注新样本历史，标签不参与准入和样本字段校验。

样本与逐点最新值沿用同事务提交。`sampleId`、每个实例/PLC/DB/代次的 `sourceSeq`、正文摘要、原采集时间、有效期及幂等回执沿用现行合同。符合准入且未过期的原字节重试返回 `duplicate`。接管在同一登记行内更新当前身份并记录退役代次，样本提交与接管按行锁顺序结算，重复样本路径同样核对准入。接管提交后的旧身份请求返回 `403`。同一 PLC 的旧历史继续可查。 [现行开发上报合同](../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev.json)

**R4-04 按已登记 PLC 查询。** 保留 `/api/v1/acquisition-data` 下五条 GET 的路径、参数、分页和成功信封。后端按登记表中的 PLC 和实际事实取值，在计数与分页前应用登记范围、查询筛选和有效期条件。当前开发阶段采集 GET 和样本 POST 均免 Bearer。采用单表登记后，已登记 PLC 的所有符合读取条件的 DB 都可通过采集 GET 查询，包括旧版未勾选读取但已有事实的 DB。

| 路径 | 读取口径 |
| --- | --- |
| `/options` | 沿用 `{plcId, dbNumbers}` 项。按已登记 PLC 汇总未过期历史样本和当前身份下有效最新点位中的实际 DB。PLC 按原字节排序，DB 按数值去重升序。没有符合条件事实的 PLC 暂无选项。 |
| `/latest`、`/latest/browse` | 读取当前实例及代次的有效点值，`sourceType` 展示当前登记标签。保留现有点筛选与排序。 |
| `/history`、`/history/{id}` | 读取同一已登记 PLC 各代次未过期的历史，`sourceType` 取样本写入时的记录，既有 `null` 原样返回。保留现有时间筛选、排序和完整样本详情。 |

对最新值或列表显式查询未知 PLC 返回 `403 plc_facts_v2.scope_rejected`。有效查询没有匹配事实时返回 `200` 空结果，包括已登记但尚未上报或选定 DB 无数据。历史详情不存在、过期或所属 PLC 未登记统一返回 `404 plc_facts_v2.not_found`。目标不可用沿用 `503`。仅有旧读取授权且无活跃登记的 PLC 不自动获得上报身份。历史事实保留，通过本规格的采集 GET 读取前需有真实来源登记。迁移预检列明这类记录和将新开放读取的 DB。

## 3. Web、DAA 与说明同步

**R4-05 Web 接入与 DAA 分工。** 来源配置表单使用四项，去掉读写 DB 输入和相关提示。编辑标签可直接保存，变更身份须展示同一 PLC 的旧、新身份并明确确认接管。`409` 后刷新并核对。在已成功保存的 PLC 对应行打开「接入参数」，显示并一键复制仅含 `instanceId`、`plcId` 和 `sourceGeneration` 的 JSON。三个字段的值取自该行已提交记录，按原样显示和复制，供 DAA 或第三方粘贴。实时与历史页面继续用 `/options` 的 `dbNumbers` 提供筛选，并更新受影响的空结果或拒绝提示。复用现有菜单、权限、列宽和时间规则。改动文案中英同步。

DAA-013 r1 负责逐台本机 PLC 填写、粘贴并保存 `plcId`、`instanceId`、`sourceGeneration`。两台 PLC 的 `instanceId` 可以相同或不同，每份新样本使用采样时所属 PLC 的完整三项。粘贴也可读取附带旧 `dbNumbers` 的 JSON，仅使用三项。本地设置、IPC、运行时、双语文案、定向测试及两份 Stage C 指南的现行接入段落由 DAA-013 实施和验证。ARCH-ACQ-004 按已提交的 PLC 行提供接入参数，并用两个任务的候选核对从 Web 复制到样本上报的链路。 [DAA-013 实施范围](../../automation-world/data-acquisition-agent/plans/DAA-013-multi-plc-reporting-identity/spec.md#3-实施范围与风险) · [Web 来源配置](../../frontend-js/src/app/acquisition-data/views/sources/index.vue)

**R4-06 指南和合同。** 同步根目录 [采集数据指南](../../docs/acquisition-data-guide.zh-CN.md)、[事实接口合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md) 及其英文版。采集数据指南按一张登记表、三标识上报、两事实表和实际 DB 读回更新图示、操作步骤、样本示例和错误说明。沿用 r3 已指定的两份 OpenAPI 工件名，更新链接，保留既有版本工件的原字节。指南按目标是否已采用单表登记说明读写规则，并按所用 DAA 是否已包含 DAA-013 说明接入步骤。逐台填写和粘贴的操作链接到 DAA-013 维护的对应版本 Stage C 指南。 [DAA 阶段 C 指南](../../automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md)

## 4. 允许改动与交付边界

### 4.1 迁移与恢复

**R4-07 前向迁移。** 以 `6a8c0e2b4d16` 为前驱增加一个 Alembic 后继，保留 r2 迁移原字节及从其前驱升级的可运行性。r2 迁移引用的六表定义可供历史迁移使用，从当前运行 ORM 和 Alembic 活跃 metadata 移除。后继部署沿用目标校验及单一 revision 机制。

1. 只读核对目标实例、schema、revision、六张表、初始化状态和旧私有配置。r2 已初始化时，以当前数据库登记为准。仅建表且旧登记还在 JSON 时，以核实的旧配置为迁移输入。核对六张登记表无数据且确认从空登记开始时，以空登记为输入。状态未知或材料不齐时留存对账结果，等待明确来源。当前 dev 处于哪种状态以执行前的只读证据为准。
2. 切换时暂停相关登记、上报和事实清理，先留存可恢复的目标备份及旧配置。更早的目标按既有路径升级到 r2。旧 JSON 仍是来源时，在后继迁移前用冻结的 r2 维护入口和前驱目标配置预览、导入并对账。已初始化的登记用同一 r2 入口导出。随后运行本任务的 Alembic 后继，逐行归并 PLC、当前实例、代次、标签、版本和时间，保留可核实的退役代次，逐字节对账身份。经预检确认的空登记直接生成空表，无需先初始化 r2。无活跃登记的旧只读范围和 DB 授权差异随迁移证据留存。对账两张事实表结构、原样本、最新点位及水位，确认新表数据后清理六张旧表。完成后的运行只读取新表，空表可直接通过 Web 新增首行。
3. 更新私有目标配置的 revision 及维护清理、现有业务集成的已知 revision 核验。切换候选核对登记、回执和读回后恢复服务。若 MySQL DDL 中断，先核对实际表、内容和 revision；用可验证的前驱备份恢复或按已知状态前向修复。恢复核对包含旧登记、事实和水位。切换后已有新数据时，先保全并对账新提交再决定恢复路径。恢复前驱需要能无损重放这些数据和登记，无法表达单表登记的变化时采用前向修复。 [r2 迁移](../../backend/alembic/versions/20261113_0800_6a8c0e2b4d16_acquisition_source_registry.py) · [维护说明](../../backend/scripts/plc_facts_maintenance/README.zh-CN.md)

### 4.2 实施允许范围

| 归属 | 限定路径与变更 |
| --- | --- |
| 后端 | `backend/app/plc_facts/` 内 `{api,schemas,models}/source_registry.py`、`models/__init__.py`、`{crud,services}/async_{source_registry,v2}.py`、`services/sync_source_registry_import.py`、`v2_config.py`、`{api,schemas}/v2.py`、`crud/sync_v2_maintenance.py`。限单表登记、原采集接口受影响的查询和准入，以及旧登记运行引用的移除。`backend/alembic/versions/` 只增加本任务后继。`backend/scripts/plc_facts_maintenance/{main,source_registry}.py` 限旧登记命令处置及目标校验，`backend/common/integration/storage.py` 限已知 revision 更新。 |
| Web | `frontend-js/src/app/acquisition-data/` 内 `views/sources/index.vue`、`api/index.js`、`locales/{en-US,zh-CN}.json`。限来源表单、合同及相应提示。 |
| 说明与合同 | `docs/acquisition-data-guide.zh-CN.md`、`backend/app/plc_facts/README{,.zh-CN}.md`、`backend/scripts/plc_facts_maintenance/README{,.zh-CN}.md`、`contracts/published/http-api/plc-facts-v2/README{,.zh-CN}.md`，同合同目录新增 `openapi-acquisition-dev-r3.json` 和 `openapi-acquisition-sources-r3.json`。`CODE_INDEX.md` 限变更的真实结构。 |
| 验证 | `backend/tests/test_{acquisition_source_registry,acquisition_data_browse,plc_facts_v2}.py`、`backend/tests_mysql/test_acquisition_source_registry.py`、`backend/tests/test_{mapping_migration,equipment_temperature_migration,legacy_acquisition_retirement}.py`（仅更新迁移 head、继承和活跃表断言）、`frontend-js/tests/module-registry/acquisition-data.test.mjs` 及专用合成环境。 |

允许范围覆盖后端和 Web 源码、构建和隔离合成验证。DAA-013 按其允许范围独立维护 DAA 项目内的设置、IPC、运行时、双语文案、定向测试及两份 Stage C 指南。DAA 驱动、采集算法、Rust 告警清理、认证体系调整、SMA/CA/FF、发布及实际环境采用另归各自任务。真实数据库、原有 profile、真实历史和设备操作按具体目标另行批准。 [r3 的原允许范围见历史记录](#r3-获批历史)

## 5. 验收

| 编号 | 可复核结果 |
| --- | --- |
| R4-AC01 Web 与管理 API | 管理员登记四项后即时可用。分别打开两条已保存的 PLC 登记，逐项核对显示和一键复制的 JSON 仅含三个标识，字段值与各自已提交记录一致。验证同值重复登记幂等、匿名与非管理员被拒绝、标签可单改、不同身份需显式接管、并发编辑的旧版本返回 `409`。 |
| R4-AC02 通用上报与回执 | 用独立 HTTP 客户端对两台登记 PLC 上报合成样本，分别覆盖同实例和不同实例，每台上报 DB21、DB22。核对 `committed` 回执与原样本匹配，历史样本和逐点最新值归属正确的 PLC、DB 及代次。以登记为 `daa` 的身份省略 `groupId` 和 `configRevision`，合法样本成功。将一台 PLC 与另一台的代次错配，或使用错误实例、未知 PLC，分别得到 `403`。非法 DB 编号仍为 `422`，原字节重发得到 `duplicate`。 |
| R4-AC03 读取与可见性 | 由 Web 和五条 GET 验证实际 DB 选项、按 PLC/DB 筛选、分页总数、未登记 PLC、已登记无数据、过期及不可见详情。验证已登记 PLC 的原未开放 DB 可读，旧只读且未登记 PLC 不在读取范围。接管前后可查同一 PLC 的旧历史，实时显示当前代次，标签修改后历史仍返回原记录。 |
| R4-AC04 联合接入与接管 | 用两任务的精确候选在 Web 分别登记两台 PLC，将各自已保存的三项一键复制到 DAA 对应行，保存并重开核对，显式开始上报。分别覆盖同实例、不同实例及两台各多个 DB，核对隔离环境中候选 API 的样本回执和正确归属。迁移前已有队列在原身份仍匹配且样本有效时，按原身份及原正文取得正确回执。用隔离 MySQL 验证上报与接管并发、接管后旧身份拒绝及已用代次拒绝。DAA 的逐行编辑、旧 DB 参数粘贴、绑定校验、保存与旧队列保护以 DAA-013 自己的验收为准。 |
| R4-AC05 迁移与指南 | 隔离验证 r2 已初始化、待导入旧 JSON、空登记直接迁移三种路径，证明原事实、水位和身份对账一致，完成后只保留新登记表及其活跃登记模型。空表可由 Web 新增首行。复验历史迁移及失败恢复路径。独立按新版指南走一次 Web 登记、复制、粘贴、两 DB 上报、回执与读回，另跑第三方示例。核对指南、运行路由、两份 OpenAPI、字段与错误说明一致。 |

ARCH-ACQ-004 可先用项目锁定工具链完成后端、Web 源码、定向单测和构建。DAA-013 按自身规格在合成 SQLite 和回环 HTTP 环境独立验证，各任务分别记录开发、自检、独立 Verification 与 Human Owner 验收。联合验收由 ARCH-ACQ-004 固定双方候选、隔离目标和同一批样本，在本任务记录 Web 复制、DAA 粘贴、采集 API 回执和数据读回的实测证据，并引用对应的 DAA-013 候选与验证记录。专用 MySQL 隔离环境由 Human Owner 稍后确认，实库迁移、接管与联合上报证据在环境可用后补齐。

## 6. 修订与交接

2026-11-13（Asia/Shanghai），Human Owner 批准 ARCH-ACQ-004 r4。获批草案 SHA-256 为 `4ad65226641f16b66c1f39dc8d27cca154e758a6af5e50792d590f6e7bc681c7`。审批问题原文如下。

> r4 调整了 DAA 文件归属和联合验收，项目 AGENTS.md 的 STD 流程要求范围或验收变化后批准新版本。是否批准已写好的 ARCH-ACQ-004 r4，继续后续实施与验证？隔离 MySQL 仍按你的安排稍后处理。

Human Owner 选择「批准 r4（推荐）」。

交 Development 按本规格实施并记录自检，专用 MySQL 隔离环境待 Human Owner 确认。`tasks.md` 和 `checklist.md` 的现有记录归原修订，r4 的实施与独立 Verification 按各自阶段记录，再交 Human Owner 终验。 [Development Lifecycle Workflow](../../.codex/workflows/development-lifecycle-workflow.md)

## r3 获批历史

下方保留获批 r3 原文件，内含 r2 和 r1 历史。取代码块正文，非空行去掉 `> ` 前缀，单独的 `>` 还原为空行，可逐字节恢复原文件。原文件 61266 字节，SHA-256 `a5e6c374b466ff62b188d848a3db7f6e0dbf1a90518e9560d82afeb01f81c2db`。

<details>
<summary>展开 r3 完整原文及批准记录</summary>

> `````markdown
> Task ID: ARCH-ACQ-004
> Revision: r3
> Status: owner_approved
> Owner Role: PM
> Allowed Writers: PM, Human Owner
> Handoff: Human Owner 已批准 ARCH-ACQ-004 r3，交 Development 按精确规格实施并完成规格内隔离验证。
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Task Namespace: aiis-ics-arch
> Classification: root
> Capability: 单表登记 PLC 上报来源，DAA 与第三方共用采集数据接口
> Owner: AIIS ICS Architecture 采集数据与 Automation World / DAA 上报接入
> Acceptance Chain Reference: 本稿第 5、6 节及 Development Lifecycle Workflow
> Depends On: ARCH-ACQ-004 r2 来源配置基线、ARCH-ACQ-003 r2 事实表和 DAA-010 单样本上报
> Related Task: ARCH-ACQ-001, ARCH-TASK-001, DAA-010
> Created: 2026-11-13 Asia/Shanghai
>
> # 简化 PLC 来源登记
>
> ## 1. 目标与基线
>
> 管理员在 Web「采集数据 → 来源配置」为每台逻辑 PLC 登记一行。复制三个来源标识给 DAA 或第三方后，任一发送程序都可按同一套规则上报。DB 编号随样本发送。数据提交后，可按 PLC、DB 和时间读回。正常运行使用一张来源登记表、两张事实表，接入时填写四项。
>
> r2 的六表实现已经过隔离产品验证及指南复验。本稿收敛同一任务的范围。`tasks.md` 和 `checklist.md` 仍记录 r2 的实施与独立验证，r3 的角色记录在相应交接阶段更新。下方保留 r2 精确规格及批准记录。 [r2 验证](checklist.md) · [r2 规格原文](#r2-获批历史) · [DAA-010 规格](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/spec.md)
>
> ## 2. 登记和接口
>
> **R3-01 单表登记。** 在事实库使用 MySQL InnoDB 表 `plc_source_registry`，`plc_id` 为主键。四项业务输入如下。
>
> | Web / API 字段 | 数据库列 | 含义 |
> | --- | --- | --- |
> | `plcId` | `plc_id` | 逻辑 PLC 标识，创建后固定，用于归集不同来源代次的历史 |
> | `instanceId` | `instance_id` | 当前发送方标识，同一实例可上报多台 PLC |
> | `sourceGeneration` | `source_generation` | 当前采样代次，更换发送方或需要重起采样序号时启用新值 |
> | `sourceType` | `source_type` | `daa` 或 `external`，由管理员选择，供标注和展示 |
>
> 三个标识沿用原 1–128 UTF-8 字节规则，精确比较，保留大小写及原始字节。系统继续维护 `registrationRevision`、`createdAt` 和 `updatedAt`，并在同一行用 JSON 字符串数组记录已退役代次，用于接管时防重。系统字段无需在登记表单填写。来源标签可以单独修改，同一实例在其他 PLC 的标签由各行管理。表内只有当前登记及必要的系统记录，DB 读写清单从登记结构删除。
>
> **R3-02 管理 API。** 沿用 `GET/POST/PATCH /api/v1/admin/acquisition-sources`、现有管理员登录权限及 `code / message / data` 信封。列表沿用分页与 PLC 字节序，每项返回四个业务字段、登记版本和时间。写操作成功提交后返回 HTTP `200`，`data` 包含 `outcome` 与提交后的 `source`。新增和更新在同一数据库上提交即生效，无需重启。管理请求、响应和表单移除 `dbNumbers`、`readDbNumbers`、`addDbNumbers`、`addReadDbNumbers` 和 DB 追加动作。提交后的结构化审计记录操作者、PLC、变化及结果。
>
> | 操作 | 请求和结果 |
> | --- | --- |
> | POST 新增 | JSON 正文为四项业务字段。新 PLC 返回 `created`，四项完全一致的重试返回 `unchanged`。已存在 PLC 的不同登记返回 `409 acquisition_sources.source_conflict`，变更使用 PATCH。 |
> | PATCH 编辑标签 | 正文传 `plcId`、`expected: {instanceId, sourceGeneration, registrationRevision}`、`action: "edit"`、`sourceType`。有变化返回 `updated`，相同标签返回 `unchanged`。 |
> | PATCH 接管 | 正文传 `plcId`、同样的 `expected`、`action: "takeover"`、`replacement: {instanceId, sourceGeneration, sourceType}`、`confirmTakeover: true`。替换实例或重起采样序号时，必须使用该 PLC 的新代次。提交成功返回 `replaced`。 |
>
> 在行锁内核对 `expected`。实际变化更新版本及修改时间。预期版本相符且值相同的操作保留原版本和时间。找不到 PLC 返回 `404 acquisition_sources.not_found`，预期不符返回 `409 acquisition_sources.revision_conflict`。首次登记和接管检查该 PLC 可核实的已用代次。接管时检查当前和退役代次，以及两张事实表中仍可核实的代次，命中返回 `409 acquisition_sources.generation_reused`。操作员选择从未使用的新代次。字段非法或缺少接管确认返回 `422 acquisition_sources.invalid_request`。管理提交结果未知时沿用 `503 acquisition_sources.commit_outcome_unknown`，先 GET 核对当前登记再操作。
>
> **R3-03 同一套上报规则。** 保留 `POST /api/v1/integration/plc-facts/samples` 和 `plc-facts/v2`。合法样本按 `plcId` 查当前一行，只匹配 `plcId`、`instanceId`、`sourceGeneration`。来源不存在或身份不符返回 `403 plc_facts_v2.scope_rejected`。`dbNumber` 仍是必填的样本字段，沿用 1–65535 的整数规则。只要身份与样本合规，同一来源可分别上报多个 DB。`groupId`、`configRevision` 对所有发送方均可省略、填 `null` 或有效标识。发送方使用现有样本正文，提交额外的 `sourceType` 返回 `422`。后端按登记值标注新样本历史，标签不参与准入和样本字段校验。
>
> 样本与逐点最新值沿用同事务提交。`sampleId`、每个实例/PLC/DB/代次的 `sourceSeq`、正文摘要、原采集时间、有效期及幂等回执沿用现行合同。符合准入且未过期的原字节重试返回 `duplicate`。接管在同一登记行内更新当前身份并记录退役代次，样本提交与接管按行锁顺序结算，重复样本路径同样核对准入。接管提交后的旧身份请求返回 `403`。同一 PLC 的旧历史继续可查。 [现行开发上报合同](../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev.json)
>
> **R3-04 按已登记 PLC 查询。** 保留 `/api/v1/acquisition-data` 下五条 GET 的路径、参数、分页和成功信封。后端按登记表中的 PLC 和实际事实取值，在计数与分页前应用登记范围、查询筛选和有效期条件。当前开发阶段采集 GET 和样本 POST 均免 Bearer。采用 r3 后，已登记 PLC 的所有符合读取条件的 DB 都可通过采集 GET 查询，包括旧版未勾选读取但已有事实的 DB。
>
> | 路径 | 读取口径 |
> | --- | --- |
> | `/options` | 沿用 `{plcId, dbNumbers}` 项。按已登记 PLC 汇总未过期历史样本和当前身份下有效最新点位中的实际 DB。PLC 按原字节排序，DB 按数值去重升序。没有符合条件事实的 PLC 暂无选项。 |
> | `/latest`、`/latest/browse` | 读取当前实例及代次的有效点值，`sourceType` 展示当前登记标签。保留现有点筛选与排序。 |
> | `/history`、`/history/{id}` | 读取同一已登记 PLC 各代次未过期的历史，`sourceType` 取样本写入时的记录，既有 `null` 原样返回。保留现有时间筛选、排序和完整样本详情。 |
>
> 对最新值或列表显式查询未知 PLC 返回 `403 plc_facts_v2.scope_rejected`。有效查询没有匹配事实时返回 `200` 空结果，包括已登记但尚未上报或选定 DB 无数据。历史详情不存在、过期或所属 PLC 未登记统一返回 `404 plc_facts_v2.not_found`。目标不可用沿用 `503`。仅有旧读取授权且无活跃登记的 PLC 不自动获得上报身份。历史事实保留，通过 r3 采集 GET 读取前需有真实来源登记。迁移预检列明这类记录和将新开放读取的 DB。
>
> ## 3. Web、DAA 与说明同步
>
> **R3-05 Web 与 DAA。** 来源配置表单使用四项，去掉读写 DB 输入和相关提示。编辑标签可直接保存，变更身份须展示同一 PLC 的旧、新身份并明确确认接管。`409` 后刷新并核对。在已成功保存的 PLC 对应行打开「接入参数」，显示并一键复制仅含 `instanceId`、`plcId` 和 `sourceGeneration` 的 JSON。三个字段的值取自该行已提交记录，按原样显示和复制，供 DAA 或第三方粘贴。实时与历史页面继续用 `/options` 的 `dbNumbers` 提供筛选，并更新受影响的空结果或拒绝提示。复用现有菜单、权限、列宽和时间规则。改动文案中英同步。
>
> 同一 DAA profile 共用一个 `instanceId`。在「上报设置 → 上报来源」选择本机 PLC，逐台手填或粘贴 Web 登记的 `plcId` 与 `sourceGeneration`。每台本机 PLC 绑定不同的 `plcId`。代次按 PLC 管理，不同 PLC 可以使用相同的代次字符串。切换选择只切换当前编辑项。共用实例不变时，编辑一台 PLC 保留其他绑定。显式保存时提交全部绑定，重开原 profile 后读回。
>
> 每份新样本使用采样时的共用 `instanceId` 和对应本机 PLC 绑定的 `plcId`、`sourceGeneration`。`dbNumber` 标识此次采集的 DB。未绑定 PLC 采得的样本沿用现有规则，仅存本地。粘贴接受新三标识 JSON，也接受附带旧 `dbNumbers` 的 JSON。解析使用三标识，旧清单忽略。保留本机 DB 配置、设置 IPC、SQLite 结构、采样和发送逻辑。已有队列沿原身份、原序号和已冻结正文续传，按实际回执结算。接管前先用旧身份处理可补传队列和未知结果，旧身份被接管后保留未结算记录供核对。 [Web 来源配置](../../frontend-js/src/app/acquisition-data/views/sources/index.vue) · [DAA 粘贴入口](../../automation-world/data-acquisition-agent/src/components/console/FactsDeliveryDialog.vue)
>
> **R3-06 指南和合同。** 实施时同步 [采集数据指南](../../docs/acquisition-data-guide.zh-CN.md)、[DAA 阶段 C 操作说明](../../automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md) 及其英文版、[事实接口合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md) 及其英文版。采集数据指南按一张登记表、三标识上报、两事实表和实际 DB 读回更新图示、操作步骤、样本示例和错误说明。生成当前数据 API 与管理 API 的 r3 OpenAPI，更新链接，保留既有版本工件的原字节。迁移说明区分已采用 r3 和仍按前驱运行的环境。
>
> ## 4. 允许改动与交付边界
>
> ### 4.1 迁移与恢复
>
> **R3-07 前向迁移。** 以 `6a8c0e2b4d16` 为前驱增加一个 Alembic 后继，保留 r2 迁移原字节及从其前驱升级的可运行性。r2 迁移引用的六表定义可供历史迁移使用，从当前运行 ORM 和 Alembic 活跃 metadata 移除。后继部署沿用目标校验及单一 revision 机制。
>
> 1. 只读核对目标实例、schema、revision、六张表、初始化状态和旧私有配置。r2 已初始化时，以当前数据库登记为准。仅建表且旧登记还在 JSON 时，以核实的旧配置为迁移输入。核对六张登记表无数据且确认从空登记开始时，以空登记为输入。状态未知或材料不齐时留存对账结果，等待明确来源。当前 dev 处于哪种状态以执行前的只读证据为准。
> 2. 切换时暂停相关登记、上报和事实清理，先留存可恢复的目标备份及旧配置。更早的目标按既有路径升级到 r2。旧 JSON 仍是来源时，在后继迁移前用冻结的 r2 维护入口和前驱目标配置预览、导入并对账。已初始化的登记用同一 r2 入口导出。随后运行 r3 Alembic 后继，逐行归并 PLC、当前实例、代次、标签、版本和时间，保留可核实的退役代次，逐字节对账身份。经预检确认的空登记直接生成空表，无需先初始化 r2。无活跃登记的旧只读范围和 DB 授权差异随迁移证据留存。对账两张事实表结构、原样本、最新点位及水位，确认新表数据后清理六张旧表。完成后的运行只读取新表，空表可直接通过 Web 新增首行。
> 3. 更新私有目标配置的 revision 及维护清理、现有业务集成的已知 revision 核验。切换候选核对登记、回执和读回后恢复服务。若 MySQL DDL 中断，先核对实际表、内容和 revision；用可验证的前驱备份恢复或按已知状态前向修复。恢复核对包含旧登记、事实和水位。切换后已有新数据时，先保全并对账新提交再决定恢复路径。恢复前驱需要能无损重放这些数据和登记，无法表达 r3 的变化时采用前向修复。 [r2 迁移](../../backend/alembic/versions/20261113_0800_6a8c0e2b4d16_acquisition_source_registry.py) · [维护说明](../../backend/scripts/plc_facts_maintenance/README.zh-CN.md)
>
> ### 4.2 实施允许范围
>
> | 归属 | 限定路径与变更 |
> | --- | --- |
> | 后端 | `backend/app/plc_facts/` 内 `{api,schemas,models}/source_registry.py`、`models/__init__.py`、`{crud,services}/async_{source_registry,v2}.py`、`services/sync_source_registry_import.py`、`v2_config.py`、`{api,schemas}/v2.py`、`crud/sync_v2_maintenance.py`。限单表登记、原采集接口受影响的查询和准入，以及旧登记运行引用的移除。`backend/alembic/versions/` 只增加本任务后继。`backend/scripts/plc_facts_maintenance/{main,source_registry}.py` 限旧登记命令处置及目标校验，`backend/common/integration/storage.py` 限已知 revision 更新。 |
> | Web | `frontend-js/src/app/acquisition-data/` 内 `views/sources/index.vue`、`api/index.js`、`locales/{en-US,zh-CN}.json`。限来源表单、合同及相应提示。 |
> | DAA | `automation-world/data-acquisition-agent/` 内 `src/components/console/FactsDeliveryDialog.vue` 和 `src/locales/{en-US,zh-CN}/common.json`。限粘贴及相应文案。 |
> | 说明与合同 | `docs/acquisition-data-guide.zh-CN.md`、`automation-world/data-acquisition-agent/STAGE_C_GUIDE{,.zh-CN}.md`、`backend/app/plc_facts/README{,.zh-CN}.md`、`backend/scripts/plc_facts_maintenance/README{,.zh-CN}.md`、`contracts/published/http-api/plc-facts-v2/README{,.zh-CN}.md`，同合同目录新增 `openapi-acquisition-dev-r3.json` 和 `openapi-acquisition-sources-r3.json`。`CODE_INDEX.md` 限变更的真实结构。 |
> | 验证 | `backend/tests/test_{acquisition_source_registry,acquisition_data_browse,plc_facts_v2}.py`、`backend/tests_mysql/test_acquisition_source_registry.py`、`backend/tests/test_{mapping_migration,equipment_temperature_migration,legacy_acquisition_retirement}.py`（仅更新迁移 head、继承和活跃表断言）、`frontend-js/tests/module-registry/acquisition-data.test.mjs`、`automation-world/data-acquisition-agent/tests/facts-delivery.test.mjs` 和专用合成环境。 |
>
> 允许范围覆盖源码、构建和隔离合成验证。DAA 驱动、采集算法、Rust 告警清理、本机存储、认证体系调整、SMA/CA/FF、发布及实际环境采用另归各自任务。真实数据库、原有 profile、真实历史和设备操作按具体目标另行批准。 [r2 的原允许范围见历史记录](#r2-获批历史)
>
> ## 5. 验收
>
> | 编号 | 可复核结果 |
> | --- | --- |
> | R3-AC01 Web 与管理 API | 管理员登记四项后即时可用。分别打开两条已保存的 PLC 登记，逐项核对显示和一键复制的 JSON 仅含三个标识，字段值与各自已提交记录一致。验证同值重复登记幂等、匿名与非管理员被拒绝、标签可单改、不同身份需显式接管、并发编辑的旧版本返回 `409`。 |
> | R3-AC02 通用上报与回执 | 在同一 DAA profile 中用同一个 `instanceId` 绑定两台本机 PLC。两台 PLC 采用不同的 `plcId` 和测试代次，各上报 DB21、DB22 的合成样本，核对 `committed` 回执与原样本匹配，历史样本和逐点最新值归属正确的 PLC、DB 及代次。用独立 HTTP 客户端以登记为 `daa` 的身份省略 `groupId` 和 `configRevision`，合法样本成功。将一台 PLC 与另一台的代次错配，或使用错误实例、未知 PLC，分别得到 `403`。非法 DB 编号仍为 `422`，原字节重发得到 `duplicate`。 |
> | R3-AC03 读取与可见性 | 由 Web 和五条 GET 验证实际 DB 选项、按 PLC/DB 筛选、分页总数、未登记 PLC、已登记无数据、过期及不可见详情。验证已登记 PLC 的原未开放 DB 可读，旧只读且未登记 PLC 不在读取范围。接管前后可查同一 PLC 的旧历史，实时显示当前代次，标签修改后历史仍返回原记录。 |
> | R3-AC04 旧接入与接管 | 在 Web 为两台 PLC 分别登记，使用同一实例。DAA 切换本机 PLC，将 Web 一键复制的参数分别粘贴至对应 PLC，并验证附带旧 DB 清单的参数仍可粘贴。保存并重开后核对两条绑定。共用实例不变时，修改一条绑定并保存重开，另一条仍可用。验证不同 PLC 可用相同代次字符串，同一 `plcId` 重复绑定时拒绝保存。迁移前已有队列在原身份仍匹配且样本有效时，按原身份及原正文取得正确回执。用隔离 MySQL 验证上报和接管并发、接管后旧身份拒绝及已用代次拒绝。核对原本机配置和采样记录。 |
> | R3-AC05 迁移与指南 | 隔离验证 r2 已初始化、待导入旧 JSON、空登记直接迁移三种路径，证明原事实、水位和身份对账一致，完成后只保留新登记表及其活跃登记模型。空表可由 Web 新增首行。复验历史迁移及失败恢复路径。独立按新版指南走一次 Web 登记、复制、粘贴、两 DB 上报、回执与读回，另跑第三方示例。核对指南、运行路由、两份 r3 OpenAPI、字段与错误说明一致。 |
>
> Development 使用项目锁定工具链做定向后端、Web 和 DAA 前端检查，记录精确候选和实际命令结果。Verification 在新的上下文中按同一候选独立核验，隔离运行结论按实测范围记录。
>
> ## 6. 修订与交接
>
> 2026-11-13（Asia/Shanghai），Human Owner 明确批准当前 ARCH-ACQ-004 r3。获批草案 SHA-256 为 `1acca25e2ae5d309cd8bbb9960b1f892251b37dfaa0dddbc08e4bf4bf62e153f`。批准原文如下。
>
> > 批准 ARCH-ACQ-004 r3 按当前 spec 实施，并完成规格内隔离验证。
>
> 现交 Development 按 `backend-arch`、`backend-script-tooling`、`frontend-ui`、`i18n-workflow` 与 `code-document-indexer` 的适用范围实施并记录自检。Development 交接后由独立 Verification 核验，再交 Human Owner 终验。 [Development Lifecycle Workflow](../../.codex/workflows/development-lifecycle-workflow.md)
>
> 在 r3 实施及独立验证交接前，`tasks.md` 和 `checklist.md` 仍保留 r2 记录。旧治理检查器会报告两处 Revision 不一致，阶段状态以本稿和各自原始记录为准。
>
> ## r2 获批历史
>
> 下方保留获批 r2 原文件，内含 r1 历史。取代码块正文，非空行去掉 `> ` 前缀，单独的 `>` 还原为空行，可逐字节恢复原文件。原文件 41699 字节，SHA-256 `5b0128bce357d8b14cab7566fa410c2c0ffb408c0718327e1d9bde0fc434deb8`。
>
> <details>
> <summary>展开 r2 完整原文及批准记录</summary>
>
> > ````markdown
> > Task ID: ARCH-ACQ-004
> > Revision: r2
> > Status: owner_approved
> > Owner Role: PM
> > Allowed Writers: PM, Human Owner
> > Handoff: Human Owner 已批准 ARCH-ACQ-004 r2，交 Development 按获批规格实施并记录自检。
> > Workflow Mode: STD
> > Execution Mode: agent_team_same_session
> > Task Namespace: aiis-ics-arch
> > Classification: root
> > Capability: Web 统一登记、编辑和切换采集来源，DAA 与第三方使用登记身份上报
> > Owner: AIIS ICS Architecture 采集数据与 Automation World / DAA 上报接入
> > Acceptance Chain Reference: 本稿第 5、6 节及 Development Lifecycle Workflow
> > Depends On: ARCH-ACQ-003 r2 的已接受事实基线及第 1 节所列现行合同和 DAA 源码
> > Related Task: ARCH-ACQ-001, ARCH-TASK-001, DAA-010
> > Created: 2026-11-13 Asia/Shanghai
> >
> > # 采集来源登记、切换与上报设置
> >
> > ## 1. r2 范围
> >
> > 先在 Web「采集数据 → 来源配置」登记。管理员把已提交的接入参数交给 DAA 或第三方。DAA 在现有「上报设置」保存，第三方填入自己的发送程序。两者继续通过 `POST /api/v1/integration/plc-facts/samples` 提交一份 PLC/DB 样本，以匹配的 `committed` 回执确认，按显式开放的范围读回。登记和切换在已采用新 schema 的后端进程内提交后即时生效。 [当前开发 OpenAPI](../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev.json) · [ARCH-ACQ-003 r2 验收](../ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收)
> >
> > 下文是已获 Human Owner 批准的 r2 增量。文末 r1 原文中 R01–R04、R06–R08 和 AC01–AC07 提供既有登记、写读、迁移、回退和验证要求，以 r2 明确修改的管理更新、接管、Web 流程、允许文件及验收为准。r1 R05 由 r2 第 2 节取代。r1 里的 DAA 生成身份反向提供给 Web、新增后只能补充 DB，以及 DAA 源码排除项由本稿第 2–4 节更新。r1 的批准记录归历史。实施按第 6 节已批准的精确 r2 交接。
> >
> > 依赖 DAA-010 当前 v2 单样本上报、冻结和回执路径。其既有原生验收、QA 发现及实际采用由原任务处理。本任务使用冻结工作树和合成夹具证明本稿的接入增量。 [DAA-010 规格](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/spec.md) · [DAA-010 验证记录](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/checklist.md)
> >
> > ## 2. Web 登记、编辑与接管
> >
> > **R2-01 管理页面及接入参数。** 保留 r1 的 Vue 模块入口、普通列表、「新增来源」、登录和管理员保护。每个活跃 PLC 一行，显示类型、PLC ID、实例 ID、代次、上报 DB、读取 DB 和登记时间。行内提供「编辑」「接入参数」。新增时两类来源都由管理员填 `sourceType`、稳定的逻辑 `plcId`、`instanceId`、`sourceGeneration` 和 DB。编辑时逻辑 `plcId` 固定，用于连续查询同一 PLC 的历史。增加上报 DB 或显式勾选读取时保留既有权限，包括导入的独立读 DB。默认勾选集合仅体现已有授权，每个未开放 DB 默认不勾选，并提示开发阶段的采集 GET 可以读取新增的 PLC/DB。继续复用前端权限、双语、列宽和时间规范。
> >
> > 「接入参数」提供当前成功登记的 JSON，形状为 `{instanceId, plcId, sourceGeneration, dbNumbers}`。按原字节显示和复制标识，`dbNumbers` 为实际登记的上报 DB 集合，按升序。该资料供手填或粘贴，提交样本仍传单个 `dbNumber`。身份变更时弹出确认，清楚展示同一 PLC 的旧、新类型、实例、代次及影响的 DB，说明旧身份会被拒绝及处理旧队列的步骤。取消保留现有登记，409 后刷新核对当前登记再编辑。
> >
> > **R2-02 管理更新合同。** 现有 active admin guard 同时保护 `GET`、`POST` 和同路径新增的 `PATCH /api/v1/admin/acquisition-sources`。GET 按 r1 列出活跃 PLC，行及写入回执增一个不透明字符串 `registrationRevision`。POST 保留 r1 的创建和同身份幂等追加语义，永远只增授权，遇到不同身份继续冲突。Web 的普通编辑和接管统一使用 PATCH。通过 JSON 正文传精确 `plcId`，覆盖含斜杠、大小写或非 ASCII 的合法 ID。请求携带 `expected: {instanceId, sourceGeneration, registrationRevision}`，后端在事务内核对预期值。
> >
> > | PATCH 动作 | 请求增量与提交结果 |
> > | --- | --- |
> > | `action=extend` | 可传 `addDbNumbers`、`addReadDbNumbers`。缺省或空数组表示无增量。新增读取范围须在操作后允许上报的 DB 内。两项按集合并入，旧身份和全部旧权限保留。 |
> > | `action=takeover` | 提交 `replacement: {sourceType, instanceId, sourceGeneration}` 和 `confirmTakeover: true`。`sourceGeneration` 必须是该逻辑 PLC 的新代次，即使只换实例。可同时提交与 `extend` 同义的 DB 增量。已有实例的类型固定，接管可改用另一类型的新实例或已登记实例。 |
> > | 成功 | HTTP 200，沿用 `code / message / data`。`data` 含 `outcome`（`extended`、`replaced` 或 `unchanged`）和提交后的 `source`。有实际变化的 POST、PATCH 均推进登记版本和更新时间，无变化保留。 |
> >
> > 验证失败沿用 r1 错误信封。无活跃记录返回 `404 acquisition_sources.not_found`，预期身份或版本不符返回 `409 acquisition_sources.revision_conflict`，该 PLC 的已知代次重复返回 `409 acquisition_sources.generation_reused`。缺接管确认或字段非法返回 `422 acquisition_sources.invalid_request`。实例类型冲突和提交未知沿用 r1 稳定错误码。重复确认或响应遗失时，先 GET 核对接管目标和实际授权。旧版本重发不能覆盖已发生的新编辑。Web 不自动重提接管。管理 OpenAPI 覆盖三个操作，采集 OpenAPI 的六条现行操作及原工件继续沿用。
> >
> > **R2-03 接管的事务与数据边界。** MySQL 以每个逻辑 PLC 的唯一活跃绑定作准入。管理接管的预期检查、绑定变化、已知代次登记和 DB 增量在同一事务。样本准入读取与样本提交之间保持对同一绑定的事务保护，并覆盖重复提交分支。已获旧绑定锁的样本先结算，接管提交后新发出的旧身份请求返回原 `403 plc_facts_v2.scope_rejected`。第二个接管或并发编辑需满足最新预期。保留初始化时的活跃代次及后续登记、退下的代次，按 `(plcId, sourceGeneration)` 精确防重。现有事实或最新水位中仍可核到的旧代次也应拒绝重用。旧清理已抹去的历史无法穷举，操作员须选该 PLC 从未使用的新代次。每条样本依旧只查当前绑定和 DB。
> >
> > 接管不改写历史、回执或既有读范围。实时页按新活跃身份读取，在新代次收到首条对应点位之前可为空。既有未过期历史继续用同一 `plcId` 查询，保留写入时的来源类型。r1 迁移和导入含初始登记代次，回退先导出当前登记及接管记录，保存全部有效读写范围及事实水位。若恢复为前驱候选，保留接管记录供后续再采用时防重。管理员日志记录操作人、逻辑 PLC、前后绑定、DB 增量和结果。登记校验属于现行开发准入，数据端仍无 Bearer，任何旧发送方拿到新参数后的物理身份验证属于其他任务。
> >
> > ## 3. DAA 上报设置与 SQLite
> >
> > **R2-04 操作与保存。** 在现有「上报与存储 → 上报设置」的「查看接入材料」位置改为「上报来源」。同一 profile 一份上报 `instanceId`，按本机 PLC 设上报 `plcId` 和 `sourceGeneration`。界面从当前生效的采集配置显示各 PLC 的上报 DB，DB 号在此处只读。同一 profile 内两台本机 PLC 不能同时绑定同一上报 PLC ID。地址、路径、间隔保留现行设置。手填与粘贴 Web JSON 共用字段验证和保存，ID 采用后端 1–128 UTF-8 字节合同。由对应 DAA 类型的 Web 记录复制参数，粘贴须覆盖所选本机 PLC 的上报 DB，只填表单。界面展示实例 ID 修改影响所有已绑定 PLC 的新样本，未重新匹配新代次的相关行需明确补齐或保持未绑定。新 profile 上报字段留空，未绑定的 PLC 可采集和查本地历史。某 PLC 的上报 PLC ID 与代次全空表示该 PLC 未绑定，任一字段缺失、已填写 PLC 绑定却缺少 profile 实例 ID 或映射重复均提示修正。
> >
> > 沿用 Rust 上报设置入口和设置版本检查，在同一 profile 的 `runtime.sqlite` 用同一事务保存地址、路径、间隔和上报绑定，重开读回。保存不调用网络、不启动采集或发送。身份变更保存后暂停后续派发，已有在途请求仍按原尝试结算。开始或继续上报仍是显式操作，保存结果只表明本机设置已提交。取消、校验失败、并发设置冲突或持久化失败不能部分生效。 [现有设置事务与样本账本](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/sample_upload.rs) · [上报设置与启动服务](../../automation-world/data-acquisition-agent/src-tauri/src/services/local_delivery.rs)
> >
> > **R2-05 采样时绑定与续传。** `config.sqlite` 的本机 profile 实例及配置键、`runtime.sqlite` 的 `plc_sources` 本机代次与序号继续作为本机运行事实。可编辑的报文字段独立保存。每轮在开始采样时确定当时有效的上报绑定，随样本持久化。先开始后遇到保存的采样轮用原绑定，保存后新开始的轮才用新绑定。未绑定时的样本只保存在本地，详情显示「仅本地记录」，保存绑定前采得的记录不会自动排入待发队列。保留现有容量、保留期及未确认保护语义，继续以有效回执区分已确认样本。
> >
> > 已有且可打开的 runtime4 保留原设置和来源。升级前记录按其原始采样和冻结证据推导原身份，升级后的未绑定记录须可明确区分。已采样的待传、冻结、在途、未知和已确认记录继续用原 `instanceId`、`plcId`、`sourceGeneration`、`dbNumber`、`sampleId`、`sourceSeq`、原采集时刻及现有目标规则。已冻结正文按原字节及 SHA 核验，结果未知按原身份重试，仅匹配的回执确认。新绑定不能把旧记录重签、改投或标为已确认。若旧身份已由后端拒绝，旧样本留在原上报记录中，显示需核对原因及当次投递身份，遵守原有效期和回执规则。 [采样落库事务](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs) · [上报正文与回执校验](../../automation-world/data-acquisition-agent/src-tauri/src/domain/sample_upload.rs)
> >
> > 序号按现行 `(instanceId, plcId, dbNumber, sourceGeneration)` 采样流递增。同一 profile 重开、正常采样和补传保持已证明的序号连续性，补传沿用原序号。全新代次可从 `1` 起，也可沿用同一 DAA 已持久分配的更大本机序号。新 profile、接管者或无法证明原序号连续时，必须先在 Web 登记新代次，禁止沿旧代次从头发号。常规接管按「暂停旧来源新采样并补传旧队列 → 核对回执和未知结果 → 停止旧发送方 → Web 确认接管同一逻辑 PLC → 新发送方填新值并显式开始」执行。DAA 应提示实例 ID 改动影响的本机 PLC 和尚未结算的旧记录，保留旧记录供对账。
> >
> > **R2-06 本地存储兼容范围。** 当前 runtime4 的 `sample_upload_settings` 只有版本、地址、路径和间隔。原样本、采集配置 context 和 v1 投递设置均有既定类型及校验用途。Development 在现有上报设置事务中选定独立的持久位置，以受识别的最小兼容变更承载上报绑定和样本绑定证据。保持原采集配置、context、样本和回执的存量原字节及 SHA。新记录的旧格式缺省字段不能经重编码改变旧摘要。冻结验证以当次样本绑定和原字节为依据。 [本地 schema 定义](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs) · [profile 锁与 seal 校验](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/profile_contract.rs)
> >
> > 若需 DDL 或 seal 合同更新，仅对通过原结构、身份和完整性检查的 runtime4 提供版本可识别的同目录兼容路径。保留 Unix 路径、设备号／inode、锁、原生恢复和 schema 指纹约束，并验证原格式能读、升级后重开及旧程序对新格式安全处理。中断后可按已知状态恢复，或者保持受保护状态并明确报告，禁止以删文件、替换库、重新封装未知状态或换新目录代替同目录兼容。支持原打开条件的 runtime2/3 继续本地采集及历史查看，按原版本处理。schema 的内部表名和具体版本实现由 Development 在上述边界内确定。
> >
> > ## 4. 允许改动与交付边界
> >
> > | 表面 | r2 允许范围 |
> > | --- | --- |
> > | 后端、MySQL、Web | 沿用 r1 §5 精确路径，含原单一 Alembic 后继 `6a8c0e2b4d16`。限本稿登记版本、接管记录、数据库准入事务、PATCH、编辑、确认和复制。管理 OpenAPI 工件改为 `contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r2.json`。冻结的采集、历史和现行开发 OpenAPI 按 r1 保留。 |
> > | DAA 界面与 IPC | `automation-world/data-acquisition-agent/` 下 `src/components/console/FactsDeliveryDialog.vue`、`src/console/composables/useLocalAcquisitionConsole.ts`、`src/services/factsDelivery.ts`、`src/locales/{en-US,zh-CN}/common.json` 和 `tests/facts-delivery.test.mjs`。`src/components/console/FactsDeliveryPanel.vue`、`src/components/console/LocalSampleDetail.vue`、`src/services/localAcquisition.ts` 限上报来源入口、原投递身份/拒绝及仅本地记录的状态展示和现有查询类型。Rust 限 `src-tauri/src/` 下 `commands/local_delivery.rs`、`domain/sample_upload.rs`、`services/local_delivery.rs`、`services/local_delivery_tests.rs`。 |
> > | DAA 采样与持久化 | `automation-world/data-acquisition-agent/src-tauri/src/` 下 `domain/local_sample.rs`、`services/local_supervisor.rs`、`infrastructure/local_store/` 的 `sample_upload.rs`、`sample_upload_tests.rs`、`runtime.rs`、`capacity.rs`、`mod.rs`、`tests.rs`。如确需兼容 schema，可调整同目录 `schema.rs`、`profile_contract.rs`、`profile_contract_tests.rs`、`delivery.rs` 的对应检查和版本识别；`infrastructure/local_store/configuration.rs`、`domain/local_configuration.rs`、`infrastructure/tia_source/reconcile.rs`、`services/local_activation.rs`、`services/local_configuration.rs` 仅允许为沿用 runtime4 行为而调整版本分支。允许按需新建 `infrastructure/local_store/reporting_sources.rs`，范围限绑定及兼容存储。 |
> > | 指南与记录 | 沿用 r1 §5 文档和角色记录，额外允许 DAA `STAGE_C_GUIDE.md` / `STAGE_C_GUIDE.zh-CN.md` 与 `src-tauri/src/infrastructure/local_store/README.md` / `README.zh-CN.md`。整理 Web 登记 → 填参 → 单样本 → 回执及读回的一条操作链，说明当前可运行版本与 r2 候选差异，保留历史段落及已验收证据。仅协调者机械同步任务索引，DAA-010 的规格和角色记录归原任务。 |
> >
> > 范围覆盖源码、构建和隔离合成验证。沿用 r1 MySQL 独立目标的限制。DAA 仅用独立测试 profile、Rust/SQLite 合成采样、回环 HTTP 和针对上报设置的前端验证。现有 dev、生产、现有本机 profile、真实历史、真实设备、用户正在运行的服务、原生 Windows 及现场联调由各自操作批准处理。DAA 驱动、采集算法、CU、SMA、DS、应用打包、Rust warnings 整理、权限体系重构、删除及批量登记均为独立范围。
> >
> > ## 5. 验收
> >
> > 按 r1 AC01–AC07 验证权限、幂等、即时上报、读写兼容、迁移与回退。r1 的 Web 验收动作以 R2-01、R2-04 代替。以下增量必须有可复跑证据。
> >
> > | 编号 | 可复核结果 |
> > | --- | --- |
> > | R2-AC01 Web 与管理合同 | 浏览器用真实管理员 API 新增 DAA、第三方并复制实际接入参数。验证同身份补充 DB、显式读权限、不撤销既有 DB、逻辑 PLC 锁定、双语、列宽和接管确认。直接请求覆盖匿名、普通用户、缺确认、带斜杠的 PLC ID、过期预期、已知代次重复和实例类型冲突。用两个并发编辑者证明旧版本无法覆盖，提交未知后可核对结果。 |
> > | R2-AC02 MySQL 接管与第三方 | 用隔离 MySQL 和两个预先启动的后端实例，复验同进程和跨进程登记前同一合法请求 403，登记后原字节 200 `committed/created`，重试 `duplicate`。用受控重叠请求证明旧样本提交和接管串行，接管后旧身份 403，新代次原样本以当前身份提交成功。核对活跃代次下最新值、旧历史、原读授权和独立只读 DB，记录进程未重启。 |
> > | R2-AC03 DAA 设置与新样本 | 用隔离 DAA 的设置界面验证手填、粘贴、取消、DB 不匹配和冲突提示，以实际 Rust 设置入口和 SQLite 验证一次提交、原路径关闭重开读回、无隐式发送。新空 profile 未绑定仍采样，配置前的样本留本地。显式开始后让绑定后的合成样本通过原 POST，核对实际请求、匹配回执、本地确认和可选 GET。跨保存的在途采样轮保留旧绑定，保存后新轮使用新值。 |
> > | R2-AC04 DAA 旧库和队列 | 合成既有可打开的 runtime4 覆盖已采未冻、已冻结、在途恢复后的未知及已确认样本。比较保存前后及重开后的原身份、序号、正文 SHA、回执、历史和本机键。相同绑定续号，变更后新绑定只用于新样本。旧身份仍可用时按原字节续传，后端已切换时旧样本保留并显示可处理状态。验证迁移前旧格式、兼容中断/复开、异常拒绝和 runtime2/3 原能力，兼容结论限实际已测结构。 |
> > | R2-AC05 合同、恢复与交付 | 按 r1 验证新 Alembic head、旧 JSON 预览/导入、读范围和事实数据守恒、目标拒绝与维护守卫。合成回退包含新增/接管后的登记、代次记录和样本，前驱的有效授权及数据对账可复现。按项目锁文件运行后端、Web 和 DAA 的定向测试、两端前端构建及 Rust 格式/定向测试，核对指南链接及 r1 原文摘要。记录候选、命令、退出码、依赖边界和未运行项。 |
> >
> > Development 先固定 provider、前端和 DAA 的实际候选，保全并行差异。DAA 前端合成测试、Rust 本地落盘与回环请求、MySQL 与浏览器的证据分别记录，缺必要独立目标时报明该验收项及解除条件。 [项目交付流程](../../.codex/workflows/development-lifecycle-workflow.md)
> >
> > ## 6. r2 批准与交接
> >
> > 2026-11-13（Asia/Shanghai），Human Owner 要求暂停实施并补充 r2 规格。同日，Human Owner 在当前会话明确批准下述范围。获批草案 SHA-256 为 `f17437cf58ec92b51a2e977f803b9d81e25f7169214652c9f9735410ce515b05`。批准原文如下。
> >
> > > 批准 ARCH-ACQ-004 r2 按 STD 实施采集来源管理 API、MySQL 登记与受控迁移、Web 来源配置及显式接管、DAA 上报设置与 SQLite 兼容、第三方接入和规格内隔离合成验证。
> >
> > 现交 Development。后端加载 `backend-arch`、`backend-script-tooling`，DAA 加载 `rust-runtime`、`desktop-tauri`，两端界面加载 `frontend-ui`、`i18n-workflow`，新增源码及索引按 `code-document-indexer`。完成精确候选和自检后交 fresh-context Verification，独立结论再交 Human Owner 终验。真实目标操作按 r1 及本稿第 4 节分别批准。
> >
> > ## r1 获批历史
> >
> > 2026-11-13 获批后的 r1 文件共 21335 字节，SHA-256 为 `619148a651c465f1f091b7439f285b57fc44ad9cadeb0f73fa0e41f14fe8e0b0`。下方完整保留原文。去掉每行 Markdown 引用前缀可恢复原字节。仅 r2 首部是当前规格的元数据。
> >
> > <details>
> > <summary>展开 r1 完整原文及批准记录</summary>
> >
> > > Task ID: ARCH-ACQ-004
> > > Revision: r1
> > > Status: owner_approved
> > > Owner Role: PM
> > > Allowed Writers: PM, Human Owner
> > > Handoff: Human Owner 已批准 ARCH-ACQ-004 r1，交 Development 按获批规格实施并记录自检。
> > > Workflow Mode: STD
> > > Execution Mode: agent_team_same_session
> > > Task Namespace: aiis-ics-arch
> > > Classification: root
> > > Capability: DAA 与第三方共用采集来源登记，提交后由运行中的采集事实服务即时采用
> > > Owner: AIIS ICS Architecture 采集数据模块（`plc_facts` / `acquisition-data`）
> > > Acceptance Chain Reference: 本规格第 6、7 节及 Development Lifecycle Workflow
> > > Depends On: ARCH-ACQ-003 r2 已接受的采集事实基线及本规格列出的当前开发合同
> > > Related Task: ARCH-ACQ-001, ARCH-TASK-001
> > > Created: 2026-11-13 Asia/Shanghai
> > >
> > > # 采集数据来源登记与即时生效
> > >
> > > ## 1. 目标与依据
> > >
> > > 交付一个任务内的管理员登记 API、MySQL 来源登记及 Web「采集数据 → 来源配置」。管理员每个 PLC 登记一次活跃来源和允许上报的 DB，之后仅在增加 DB 时补登。MySQL 提交成功后，新发出的样本请求直接使用该登记，所有后端进程都无需重启、重载或编辑文件。DAA 与第三方沿用同一条样本 POST。 [现行开发 OpenAPI](../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev.json) · [ARCH-ACQ-003 r2 验收](../ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收)
> > >
> > > 当前开发源码从仓外 JSON 加载 `target`、`instances`、`sources`、`readScopes` 并在进程内缓存。现行样本 POST 和五个采集数据 GET 均无需 Bearer，GET 使用各组 PLC/DB 的有效并集；其中部分可读对可能没有对应的上报授权或活跃来源。登记身份是开发环境的上报准入条件。知道这些 ID 的程序可以构造请求，因此登记本身无法验证设备或程序的真实身份。 [配置与准入源码](../../backend/app/plc_facts/v2_config.py) · [读写服务](../../backend/app/plc_facts/services/async_v2.py) · [开发合同说明](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)
> > >
> > > ## 2. 登记与采集事实
> > >
> > > **R01 MySQL 登记。** 由 FastAPI `plc_facts` 模块持有，复用事实目标所在的 MySQL 8.4 InnoDB。存储实例及其 `sourceType`、PLC 的活跃实例及 `sourceGeneration`、精确 PLC/DB 上报授权和独立的 PLC/DB 读取范围。数据库约束保证 `instanceId` 唯一且类型一致、`plcId` 至多一个活跃绑定、授权对唯一、上报授权引用有效绑定。实例可服务多个 PLC。读取对可独立存在。三个 ID 沿用样本合同的 1–128 UTF-8 字节、禁止首尾空白及 ASCII 控制字符规则。索引、唯一约束和查询按精确字节比较，大小写与不同 Unicode 字节形式保留各自身份。DB 号为 1–65535 的整数。登记时间按数据库上海时钟保存，API 带 `+08:00`。
> > >
> > > **R02 提交与并发。** 登记、授权增加和可选读范围增加在同一事务内完成，成功响应只在提交之后发送。样本写入服务在其事实事务内按精确键查登记并确定 `sourceType`；重复样本分支若重新开启事务，同样核验目标与准入。对同一 PLC 或实例的并发登记由数据库约束和事务仲裁。相同登记安全重复，互补 DB 增量全部保留，互斥身份请求明确冲突，失败事务无部分授权。提交后的新请求从同一 MySQL 主库读取已提交状态，采集 GET 同样从数据库取所需范围。切换完成后，数据库未就绪时拒绝服务；进程缓存仅可用于静态目标配置，登记的读、写、恢复均以 MySQL 为准。样本请求只查询本次身份和 DB，禁止每条样本全表扫描或加载完整登记。常规请求及应用启动不建表、不导入旧文件、不自动登记来源。
> > >
> > > **R03 采集合同兼容。** 样本仍用 `POST /api/v1/integration/plc-facts/samples`、`plc-facts/v2` 和现有开发认证口径。一份样本只有一个 PLC/DB；后端匹配 `instanceId`、`plcId`、`sourceGeneration`、`dbNumber`，未登记或不匹配为 `403 plc_facts_v2.scope_rejected`。`daa` 必须提供 `groupId`、`configRevision`，`external` 仍允许分别省略或传 `null`，正文中 `sourceType` 仍为 422。保持现有正文验证、回执、原字节幂等、两张事实表及其已有行、原值精度、顺序水位、迟到补传、有效期和清理规则。
> > >
> > > 五个 `GET /api/v1/acquisition-data/*` 路径、免 Bearer 访问、筛选分页和历史合同沿用当前开发版本。`options`、历史和详情按读范围查询；实时读取还要匹配当前活跃实例和代次。读面以独立读授权为准，包含符合实时来源和有效期条件、但当前没有写 DB 授权的既有最新值。旧历史 `sourceType=null` 保持原事实。注册成功只确认配置已提交；样本送达由原 `committed` 回执确认。
> > >
> > > ## 3. 管理 API 和 Web
> > >
> > > **R04 管理 API。** 在 `plc_facts` manifest 装配 `GET` 和 `POST /api/v1/admin/acquisition-sources`，两者复用现有登录 access token 和 `get_current_active_admin`。匿名、无效或过期 token、撤销 token 和已禁用账号按现有认证约定返回 HTTP 401；有效的非管理员返回 HTTP 403。Web 页面权限或其他模块授权不能授予这两个接口。管理业务成功使用 HTTP 200 和 `code / message / data`；业务失败使用实际 HTTP 状态和 `code / message / data=null / errorCode`。认证、授权失败沿用框架响应，保留 401 的 Bearer 认证提示。
> > >
> > > | 操作 | 请求及成功结果 |
> > > | --- | --- |
> > > | `GET` 查看登记 | 按 `plcId` 精确字节序分页，沿用 `page`、`pageSize`（默认 1、50，页长 1–100）。`data` 含 `items / total / page / pageSize / totalPages`。每个活跃 PLC 一行，返回 `sourceType`、`instanceId`、`plcId`、`sourceGeneration`、`dbNumbers`、`readDbNumbers`、`createdAt`、`updatedAt`，DB 升序。`readDbNumbers` 含该 PLC 导入的独立读 DB。无活跃绑定的旧只读对仍由采集数据 GET 按原规则读取。 |
> > > | `POST` 登记或增加 DB | 一次提交 `{sourceType, instanceId, plcId, sourceGeneration, dbNumbers}`，可选 `readDbNumbers`。类型精确为 `daa` 或 `external`。`dbNumbers` 非空，数组内的 DB 必须唯一；`readDbNumbers` 省略或为空即不新增读范围，给出时须为此次提交的 `dbNumbers` 的子集。仅增加请求明确列出的项，已有 DB、已开放读取的 DB 及登记身份均保留。`data` 含 `outcome`（`created`、`extended` 或 `unchanged`）和 `source`（该 PLC 最新已提交的登记，形状同列表行）。无增量的重复请求返回 `unchanged`，也不改变更新时间。 |
> > >
> > > | HTTP | `errorCode` | 条件 |
> > > | --- | --- | --- |
> > > | 422 | `acquisition_sources.invalid_request` | 字段无效或未知、非法类型、空上报 DB 列表、重复 DB、读 DB 超出本次申请或非法分页参数。 |
> > > | 409 | `acquisition_sources.source_conflict` | PLC 已绑定其他实例或代次。保留当前绑定及全部权限。 |
> > > | 409 | `acquisition_sources.instance_type_conflict` | 已存在的实例登记为另一类型。若两种冲突同时满足，优先返回 `source_conflict`。 |
> > > | 503 | `acquisition_sources.not_ready` | 功能关闭、目标或登记未就绪、数据库不可用或未提交的事务失败。 |
> > > | 503 | `acquisition_sources.commit_outcome_unknown` | 提交结果无法确认。按 GET 核对后可原样重试。 |
> > >
> > > 管理 POST 记录操作者、来源、DB 增量和结果的结构化事件，必要的拒绝和异常有稳定标识。日志、合同示例和测试输出排除 token、Authorization header、连接串、完整导入文件或真实现场材料。管理员 API OpenAPI 显示登录认证。采集接口的六条开发 OpenAPI 操作及其历史工件继续独立可用。
> > >
> > > **R05 Web「来源配置」。** 在现有「采集数据」菜单下通过 manifest 新增管理员页面 `acquisition-data.sources`，路由 `/acquisition-data/sources`，使用 `requiresAdmin`，复用登录、菜单、路由守卫和请求封装。列表读取真实 GET，展示来源类型、PLC、实例 ID、来源代次、允许上报 DB、已开放读取 DB 和登记时间。提供「新增来源」「增加 DB」和刷新。已有登记的身份字段在增加 DB 时固定。读取选项按 DB 显式勾选，默认不勾选，并提示勾选后当前开发采集数据 GET 可读取该 PLC/DB。业务列遵循公共列宽工具的拖拽、最小宽度、横向滚动、本机记忆和恢复默认规则。时间按上海显示到秒。中文、英文文案及错误反馈成对。
> > >
> > > - **DAA。** 在「上报设置 → 查看接入材料」复制现有 v2 JSON（`schemaVersion: 1`、`contractVersion: plc-facts/v2`、`instanceId`、`sources: [{plcId,dbNumber,sourceGeneration}]`）。粘贴后选择一个 PLC，核对原实例、代次和本次 DB，再保存。每次保存只登记一个 PLC。空材料、旧协议材料、同一选定 PLC 内不一致的代次或无有效 DB 时提示修正。登记沿用 DAA 生成的身份，DAA 本地的采集、上报启停、补传及回执流程由自身管理。 [DAA 接入材料](../../automation-world/data-acquisition-agent/STAGE_C_GUIDE.zh-CN.md#6-登记来源并开始上报)
> > > - **第三方。** 选择 `external`，填写稳定的实例 ID、PLC ID、代次和 DB。保存成功后页面显示并可复制实际登记值，发送方将其填入现行样本 POST。每份样本继续用自身 `sampleId`、`sourceSeq` 和采集时间。
> > > - **反馈。** 提供加载、空列表、校验失败、未登录、无权访问、保存中、提交成功和服务不可用反馈。遇到 409 显示「该 PLC 已有其他活跃来源或代次」或「该实例已登记为其他类型」，保留表单，可刷新核对当前记录。结果未知时提示先核对登记再原样重试；在得到成功响应或核实本次目标状态前，页面不显示保存成功。
> > >
> > > ## 4. 一次性升级、导入和回退
> > >
> > > **R06 Schema 与目标。** 当前源码 Alembic 唯一 head 为 `5f7a9c1e3b25`。增加唯一后继 `6a8c0e2b4d16`，只创建登记所需表、约束及索引，保存现有事实及业务表。既有 migration 原字节保留。以同一连接核验实际 schema、server UUID、精确单一 revision、MySQL 8.4、上海时钟及目标对象状态，控制锁等待。MySQL DDL 中断后先核对实际表、约束与 revision，提供可重跑的已知状态或可复核的恢复路径，未知或冲突形态停止。 [当前前驱](../../backend/alembic/versions/20261111_1400_5f7a9c1e3b25_generic_task.py)
> > >
> > > `PLC_FACTS_V2_ENABLED` 保持缺省关闭。仓外运行配置独立保留 `target`（alias、server UUID、schema、精确新 revision），各登记和采集请求在实际数据库核对目标。登记资料不能改变部署目标。v2 清理 CLI 使用目标配置并在实际库精确匹配新 revision，保持原操作守卫和清理逻辑。BE-010 采用凭据仅增加已知后继支持，继续精确比对实际 UUID、schema、revision 和采用证据。旧凭据的目标匹配条件继续适用；真实目标凭据更新另行批准。 [清理入口](../../backend/scripts/plc_facts_maintenance/main.py) · [BE-010 目标验证](../../backend/common/integration/storage.py)
> > >
> > > **R07 一次性受控导入。** 交付显式维护命令，用仓外旧 JSON 作为一次性输入，提供只读预览和带明确确认的执行。预览核对明确目标、前驱 profile 及源文件摘要；执行前重新核对同一输入、目标和新 revision。严格校验旧结构、重复 JSON 键、实例引用、类型、精确标识、单活跃约束及 DB 范围。导入内容限 `instances`、`sources` 和各组 `readScopes` 的有效 PLC/DB 并集，包含独立实例、零写 DB 的活跃绑定、无当前写权限的读对、无活跃来源的读对和空配置。历史可选 `credentials` 继续忽略其内容。迁移保留有效权限及来源分类，历史来源空值和样本保持原状。
> > >
> > > 执行以单一事务提交登记数据和初始化记录。首次只向未经初始化的空登记导入，导入前及提交后分别核对实例、活跃绑定、上报对、读取对的数量及逻辑摘要。相同输入重复执行可核实原提交且无新增写入，即使随后已有 Web 增量也保持原登记；不同输入或目标不符停止，避免覆盖。预览、冲突、部分失败和提交未知均给出脱敏证据，提交未知先对账再决定是否重试。裸命令仅显示帮助。新空目标也通过显式空配置初始化。
> > >
> > > **R08 切换与回退。** 受控切换按「暂停该目标相关写入和清理 → 留存备份与旧 profile → 从精确前驱执行 Alembic → 预览、确认、导入并对账 → 使用只含目标身份的运行配置切换全部后端进程 → 核对管理、上报、读回后恢复」执行。迁移未完成或未显式初始化时拒绝开放新流程。切换为一次部署操作。此后每次日常 Web 登记的生效点是 MySQL 提交。
> > >
> > > 需要回退时，先暂停登记、采集写入和维护，记录两张事实表水位，备份并导出当前完整登记（含 Web 增量、实例及独立读取对）。Alembic 采用前向迁移，回退通过受控恢复演练完成。按前驱 profile 格式从完整导出生成恢复材料，在隔离恢复目标以精确前驱备份恢复 schema，补齐切换后的事实数据。确认前驱能解析该 profile，并对账全部样本、逐点水位及有效读写范围后，才可采用恢复候选。保留导出、恢复材料和提交证据。若无法无损恢复，保留 MySQL 数据和现有登记，暂停相关写入并采用经批准的前向修复。此版本交付可复核的恢复步骤和隔离演练，真实 dev 或生产的备份、DDL、导入、切换、回退及重启各归另行批准的目标操作。
> > >
> > > ## 5. 允许改动与范围边界
> > >
> > > | 表面 | 获批后允许的文件和变更 |
> > > | --- | --- |
> > > | 后端 `plc_facts` | `manifest.py`、`v2_config.py`、`api/v2.py`、`services/async_v2.py`、`crud/async_v2.py`、`crud/sync_v2_maintenance.py`、`models/__init__.py`，限接线、读写授权及精确 revision 守卫。新增同一模块的 `api/source_registry.py`、`schemas/source_registry.py`、`models/source_registry.py`、`services/async_source_registry.py`、`crud/async_source_registry.py`，可按需增加 `source_registry_domain.py`、`services/sync_source_registry_import.py`、`crud/sync_source_registry.py`。 |
> > > | 迁移与维护 | 只新增 `backend/alembic/versions/20261113_0800_6a8c0e2b4d16_acquisition_source_registry.py`。`backend/scripts/plc_facts_maintenance/main.py` 及按需新增的同目录 `source_registry.py` 限导入和清理目标加载。`backend/common/integration/storage.py` 限已知 revision 追加。 |
> > > | Web | `frontend-js/src/app/acquisition-data/` 的 `manifest.js`、`api/index.js`、`locales/{en-US,zh-CN}.json`，新增 `views/sources/index.vue`。现有实时、历史和共享基础设施沿用现行入口。 |
> > > | 合同与用法 | 新增 `contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r1.json`，该目录双语 README 补登记用法。`backend/app/plc_facts/`、`backend/scripts/plc_facts_maintenance/` 双语 README 限目标、导入、回退和运行指引；`backend/scripts/business_time_adoption/` 双语 README 限新精确 revision；`docs/acquisition-data-guide.zh-CN.md` 限来源配置使用说明。`CODE_INDEX.md` 限本任务新增结构。 |
> > > | 验证及治理 | 后端新增 `backend/tests/test_acquisition_source_registry.py`、`backend/tests_mysql/test_acquisition_source_registry.py`。`backend/tests/` 的 `test_plc_facts_v2.py`、`test_acquisition_data_browse.py`、`test_business_integration_storage.py`、`test_mapping_migration.py`、`test_equipment_temperature_migration.py`、`test_legacy_acquisition_retirement.py`、`test_business_integration_migration.py` 限本任务和图断言适配。`backend/tests_mysql/` 的 `test_plc_facts_v2.py` 与 `test_legacy_acquisition_retirement.py` 限夹具和候选绑定兼容，历史合同及历史 schema 验证保留在其精确候选。前端限 `frontend-js/tests/module-registry/acquisition-data.test.mjs`。当前任务三文件按角色分阶段维护，根 PLAN 和 plans 目录索引双语条目由协调者机械同步。 |
> > >
> > > r1 只支持查看、新增和补充 DB。活跃实例/代次替换、删除、撤销已有授权、批量多 PLC 登记、公开登记、样本自动登记、新采集协议、设备鉴权方案、现有登录权限重构、DAA/SMA/CU 源码和原生联调均留待另行任务。待批准范围覆盖源码和隔离合成验证。既有 dev、生产、客户库、真实设备、配置、历史和运行服务的操作，以及容器启停/构建、部署、发布或推送，均须具体授权。复用已有独立测试 MySQL，或由 Human Owner 明确批准新的可丢弃目标；只使用专用 schema、合成数据及不触及其他库的账号。
> > >
> > > ## 6. 验收标准
> > >
> > > | 编号 | 可复核结果 |
> > > | --- | --- |
> > > | AC01 管理权限 | 实际登录的 active admin 可列出和登记；缺 token、无效、过期或已撤销 token、禁用账号均按认证约定拒绝；有效 supervisor/operator 直调 GET、POST 为 403。记录状态、错误及无登记增量。OpenAPI 管理路径显示认证，现行六条采集操作的开发认证声明一致。 |
> > > | AC02 登记与竞争 | MySQL 验证新登记、原样重试、增加 DB、未知提交后核对和重试。用并发同值、互补 DB、冲突实例/代次、跨 PLC 同实例不同类型验证唯一性、完整提交和明确 409。错误字段、精确大小写与 Unicode 字节比较、DB 边界、事务中断均有覆盖。拒绝前后对比登记，证明没有隐式覆盖或部分授权。 |
> > > | AC03 保存后即时上报 | 在同一已启动候选进程，分别以 DAA 形状及第三方形状的合法合成样本先 POST 得 403；管理员保存后原正文字节再次 POST 得 HTTP 200，匹配 `contractVersion`、`instanceId`、`sampleId` 且 `status=committed`、`outcome=created`，再发得 `duplicate`。同步核对事实行和最新水位。再用两个事先已启动且连同一 MySQL 的独立后端进程，验证一端登记、新请求在另一端立即可用。记录进程、目标及请求时序，验证期间无重启、重载或文件改动。 |
> > > | AC04 读范围和回归 | 保存写授权时不勾选读取，样本仍可提交，`options`/显式读取不扩大；显式添加读范围后，立即通过最新值、历史和详情回读。导入的只读对继续可读且不能上报，包括有活跃 PLC 但未授权写的 DB 的既有实时及历史记录，以及无活跃来源的历史。覆盖五个 GET、实时来源分类、历史 `null`、DAA 条件字段、第三方空元数据、错身份/代次/DB、原字节冲突、迟到和清理的定向回归。 |
> > > | AC05 Web | 用隔离候选和真实管理 API 做浏览器验收。管理员可进入、粘贴现有 DAA v2 材料、单独选择 PLC 与 DB、登记第三方、复制结果并增加 DB；普通账号无菜单且直接访问受阻。核对默认不开读取、提交后列表刷新、双语、窄屏、列宽持久化与恢复、冲突和未就绪提示。`pnpm check:modules`、模块测试和 `pnpm build` 通过。 |
> > > | AC06 升级与导入 | 在含合成事实的独立 MySQL 从 `5f7a9c1e3b25` 升到唯一后继，对账事实和其他表，核对模型/迁移一致性。预览无写，错误或错目标无部分授权，导入前后有效来源及读写权限一致；重复导入无变化；已保存 Web 增量后重复导入仍保留增量。验证 DDL 中断处理、未初始化、目标不符、登记库不可用和仍可访问旧 JSON 的情况下均按约定关闭准入。同步复核 cleanup plan 与 BE-010 精确 revision 守卫。 |
> > > | AC07 回退与交付 | 隔离演练覆盖切换后新增 Web 登记及已提交样本，核对当前登记导出、前驱兼容恢复和样本/水位守恒；模拟缺少可核恢复材料时拒绝退回。核对定向源码测试、合约、文档链接、冻结工件及改动范围，证据含精确候选和合成目标身份、命令、退出码、结果及未运行项。 |
> > >
> > > ## 7. 批准与交接
> > >
> > > 2026-11-13（Asia/Shanghai），Human Owner 在当前会话明确批准 ARCH-ACQ-004 r1。获批草案 SHA-256 为 `1bf9f57ce75cf0b7f38dda3b7366db38b314d5b145543b3b901f7546ece2b98f`。批准原文如下。
> > >
> > > > 批准 ARCH-ACQ-004 r1 按规格实施采集来源登记 API、MySQL 登记与受控迁移、Web「来源配置」及隔离合成验证。
> > >
> > > 批准后由 Development 加载 `backend-arch`、`backend-script-tooling`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer` 的适用部分，先核对现行合同、精确 Alembic 图及并行工作树，再按允许范围实施并在 `tasks.md` 交付自检。协调者将精确候选、差异和运行证据交 fresh-context Verification，在 `checklist.md` 记录独立验收，最后交 Human Owner。范围、验收、风险或允许改动发生实质变化时提交新 Revision 批准。 [项目交付流程](../../.codex/workflows/development-lifecycle-workflow.md)
> >
> > </details>
> > ````
>
> </details>
> `````

</details>
