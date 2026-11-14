Task ID: ARCH-ACQ-005
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 ARCH-ACQ-005 r1，交 Development 按本规格实施并使用第 3 节的 dev 库开展定向验证。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 管理员删除单条 PLC 来源登记，采集历史继续可查
Owner: AIIS ICS Architecture 采集数据模块
Acceptance Chain Reference: 本稿第 4、5 节及 Development Lifecycle Workflow
Depends On: ARCH-ACQ-004 r4 owner_accepted
Created: 2026-11-13 Asia/Shanghai

# 删除 PLC 来源登记

## 1. 目标

管理员在「采集数据 → 来源配置」删除一条登记。提交后该来源停止获得上报准入，已提交样本在原有效期内仍能从「采集历史」及历史 API 查询。沿用一张 `plc_source_registry` 和现有两张事实表，数据库继续使用 `7b9d1f3a5c7e`。 [ARCH-ACQ-004 r4 基线](../ARCH-ACQ-004-acquisition-source-registry/spec.md) · [最终验收](../ARCH-ACQ-004-acquisition-source-registry/checklist.md#arch-acq-004-r4-human-owner-最终验收)

## 2. 需求与接口

**R1-01 管理删除。** 沿用管理员权限和 `PATCH /api/v1/admin/acquisition-sources`。传 `action: "delete"`、`plcId`、`expected: {instanceId, sourceGeneration, registrationRevision}` 和 `confirmDelete: true`。复用登记行锁及现有事务边界，核对预期身份和版本后物理删除该行，两张事实表保持原值。成功提交后返回 HTTP `200`，`data.outcome` 为 `deleted`，`data.source` 是删除前快照，沿用现有结构化日志记录操作者、PLC 和结果。记录已不存在返回 `404 acquisition_sources.not_found`，预期不符返回 `409 acquisition_sources.revision_conflict`，缺少确认或参数非法返回 `422 acquisition_sources.invalid_request`。提交结果未知时返回 `503 acquisition_sources.commit_outcome_unknown`，先刷新来源列表核对。Web 行操作显示 PLC ID 和「停止接收该来源上报，历史按原有效期保留」，确认后执行，取消时不发请求。提交成功或发生版本冲突时刷新列表。

**R1-02 上报和代次。** 合法上报和原样本重试均按现有三个 ID 准入。上报与删除竞争同一登记行锁，先取得锁并成功提交的上报保留回执及事实，先提交删除时后续旧身份上报返回 `403 plc_facts_v2.scope_rejected`，包括重试此前已提交的样本。DAA 沿用现有来源阻断处理，冻结样本保留原身份和正文。重新登记仍检查两张事实表中可核实的代次，命中返回 `409 acquisition_sources.generation_reused`。物理删除会一并移除该行的当前身份和 `retired_generations`。若某代次从未写入事实，或相关事实与水位均已不存在，重新登记时可能无法识别该代次曾用。复用旧身份可能让旧发送方再次通过准入。重新登记同一 `plcId` 时使用从未用过的新代次，已有冻结样本仍以原身份处理。

**R1-03 历史与实时。** `GET /api/v1/acquisition-data/history` 和 `/history/{id}` 直接按未过期历史事实读取，适用于已删除及其他当前未登记 PLC。现有开发 GET 免 Bearer，这些此前不可见的有效样本也可通过接口查询。历史列表保留 PLC、DB、时间过滤、排序和分页，过滤后计数，无匹配返回 `200` 空页。详情不存在或已过期返回 `404 plc_facts_v2.not_found`。历史标签取样本写入时的值。

`GET /api/v1/acquisition-data/options?view=history` 从全部未过期历史事实提取去重的 PLC/DB，沿用 `data.items: [{plcId, dbNumbers}]` 和原排序。历史页显式传该参数，用户可选择已删除或其他未登记 PLC 及其有历史的 DB。省略 `view` 时继续汇总已登记 PLC 的有效历史和当前身份的有效最新值，实时页继续使用该默认结果。其他 `view` 值或重复传参返回 `422 plc_facts_v2.invalid_request`。实时刷新选项后不再列出已删除 PLC，两条实时 GET 保持当前身份筛选，显式请求未登记 PLC 仍返回 `403`。

## 3. 允许改动与测试目标

| 范围 | 允许改动 |
| --- | --- |
| 后端 | `backend/app/plc_facts/{api,schemas}/source_registry.py`、`{crud,services}/async_source_registry.py`、`api/v2.py`、`{crud,services}/async_v2.py`。复用管理和目标检查，限删除与读侧筛选。 |
| Web | `frontend-js/src/app/acquisition-data/` 的 `api/index.js`、`composables/useAcquisitionScope.js`、`views/{sources,history}/index.vue`、`locales/{en-US,zh-CN}.json`。 |
| 文档与合同 | `docs/acquisition-data-guide.zh-CN.md`、`backend/app/plc_facts/README{,.zh-CN}.md`、`contracts/published/http-api/plc-facts-v2/README{,.zh-CN}.md` 和同目录两份新快照 `openapi-acquisition-dev-r4.json`、`openapi-acquisition-sources-r4.json`。同步删除、历史与实时选项、错误结果及示例，保留已验收的快照。 `CODE_INDEX.md` 限受影响的入口说明。 |
| 测试 | `backend/tests/test_{acquisition_source_registry,acquisition_data_browse,plc_facts_v2}.py`、`frontend-js/tests/module-registry/acquisition-data.test.mjs` 和任务私有的临时验收材料。 |

范围排除表、列和 Alembic 变更，以及 DAA 源码、协议、配置、队列和真实设备操作。验收按用户指定使用现有 dev 库 `127.0.0.1:3307/industrial_level_2_system`。r1 批准后，先核对实际 UUID、schema、单一 revision、测试标识空闲和既有两条来源。Development 和 Verification 各用独占 PLC、实例、代次、样本标识及明确记录的行键。清理按本轮精确行键和身份核对，只移除自己创建的测试登记与事实，复查测试记录已清空、原有两条来源及历史未被本轮写入影响。沿用用户启动的 `8000/5190`，由用户负责加载候选版本。无新数据库环境或迁移。

## 4. 验收

| 项目 | 可观察结果 |
| --- | --- |
| AC01 管理操作 | 取消确认无请求，未登录和普通用户无法删除。旧版本删除返回 `409` 并保留新登记，缺少确认返回 `422`。确认后仅目标行消失，第二次删除返回 `404`。核对现有新建、编辑、接管和复制参数仍可用。 |
| AC02 并发与重登记 | 以不同 MySQL 会话验证样本先提交和删除先提交两种顺序，核对回执及两张事实表。删除后旧身份的合法新样本及原样本重试返回 `403`，冻结正文无需改动。用测试 PLC 的可核实旧代次重登记返回 `409`，用新代次可上报并读取同 PLC 历史。记录无事实代次随登记行丢失的已知限制。 |
| AC03 查询与选项 | 同一测试 PLC 先经真实上报接口写入，删除登记后在 Web 和 API 仍可筛选、分页及读取同一历史详情。由定向单元测试验证历史读取也覆盖从未登记的 PLC，以及过期、未知筛选、缺失详情和非法 `view` 的结果。默认 options 与实时页刷新后无已删除 PLC，直接请求其最新值返回 `403`。 |
| AC04 一致性与清理 | 核对中英文界面、指南、实际路由和两份 OpenAPI。记录当前 dev 目标、测试键、前后对账及精确清理结果，核对未改现有业务来源、历史和数据库结构。 |

## 5. 审批与交接

登记时间为 2026-11-13 22:57:42（Asia/Shanghai）。Human Owner 批准 ARCH-ACQ-005 r1，批准前草案 SHA-256 为 `30b09f18a86d3b512d56842c7927ce20ea0d4e8ba63d12cfe90458e99f3118af`。

> 批准 ARCH-ACQ-005 r1，按规格实施并使用 dev 库验证。不要过度设计和过度测试

Human Owner 此前已确认历史读取覆盖当前未登记 PLC 的所有未过期样本。按获批规格实施物理删除，沿用 R1-02 的代次防重限制及第 3 节的 dev 合成写入和精确清理边界。由 Development 读取 `backend-arch`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer` 的适用部分，实施并自检。交 fresh-context Verification 验证同一候选，再由 Human Owner 最终验收。 [交付流程](../../.codex/workflows/development-lifecycle-workflow.md)
