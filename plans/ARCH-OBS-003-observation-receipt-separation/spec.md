# ARCH-OBS-003：观测表命名与能耗回执分离

Task ID: ARCH-OBS-003
Revision: r4
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 r4 实施与隔离复验；交 Development，dev 切换另行确认
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 保留现有数据与接口的观测表命名统一及能耗写入回执分离
Owner: Core 设备观察、过程监控与能耗数据
Acceptance Chain Reference: 本规格批准 → Development handoff → fresh-context Verification → Human Owner 最终验收；实际 dev 切换另行确认
Related Task: ARCH-OBS-001、ARCH-OBS-002、ARCH-ACQ-006

## 1. 背景、目标和当前 gate

设备状态、过程监控共用同一套指标定义和两种目标的槽位。当前五张相关表使用 `equipment_` 或 `process_monitor_` 不同前缀，且实时、过程、能耗的写入回执都位于 `metric_ingest_receipts`。Human Owner 要求统一命名，并让能耗回执独立。目标是在保留既有数据、回执 ID、去重行为和 HTTP 合同的前提下完成一次显式 Alembic 迁移。

原 r1 草拟时源码唯一 Alembic head 为 `c9e1a3b5d720`。r1 获批后的实施前预检发现，并行 ARCH-ACQ-006 已在工作树加入 `da6c32f8a701`，其 `down_revision` 为 `c9e1a3b5d720`，当前源码唯一 head 已变为 `da6c32f8a701`。该采集后继目前是尚在开发、未提交的候选，不代表独立 QA 或 Human Owner 验收完成。设备观察当前 profile 仍只接受 `c9e1a3b5d720`。ARCH-OBS-002 r1 的 dev 切换和只读复核已完成，Human Owner 最终验收仍待其原任务记录。本任务不改变相关任务的验收状态。其依据见 [ARCH-OBS-002](../ARCH-OBS-002-legacy-observation-retirement/spec.md) 与 [ARCH-ACQ-006](../ARCH-ACQ-006-acquisition-consumption-delivery/spec.md)。

Human Owner 已明确批准 r1 实施与隔离验证，但尚未授权 dev 切换。因唯一前驱已变化，按 r1 和 STD 回 PM 修订，不制造分叉；修订前本任务未开始实施、隔离验证或写入业务数据。r2 保持原业务范围和数据保留合同，将前驱调整为 `da6c32f8a701`，补充对其候选固定、采集数据保护及 dev 中间状态的要求。Human Owner 已明确批准精确 r2 的实施与隔离验证，Development 已启动。实施中发现 r2 测试 allowlist 有三处必要的当前 metadata 或 head 断言缺口，返回 PM 起草 r3；Human Owner 已明确批准 r3，且其业务范围和 dev gate 保持不变。

r3 fresh Verification 在真实隔离 MySQL 上发现同名且 `ENFORCED` 的错误 CHECK 表达式及改变后的回执 `target` 排序规则未被预检拒绝，记录 `qa_failed`。同期 ACQ 前驱固定版本发生影响 trigger 拒绝行为的实质变化，ACQ 自身独立验证亦记录 `qa_failed`、Development 当时正在返工。按 §4.2 停止沿用旧前驱的 OBS 正式验证并返回 PM；详细证据、后续验收状态及未完成项分别归 [OBS 独立验证](checklist.md) 和 [ACQ 独立验证](../ARCH-ACQ-006-acquisition-consumption-delivery/checklist.md)。r4 保留 r3 的迁移链、数据／接口和 dev 边界，明确两类预检和更新前驱的链路验证。Human Owner 已精确批准 r4 实施与隔离复验，隔离验证不代表 dev 切换已获批。

## 2. 精确范围和表映射

| 当前名称 | 迁移后名称 | 归属与要求 |
| --- | --- | --- |
| `equipment_status_main` | `equipment_main` | 设备与任务的最新整包，所有记录与行为保留。 |
| `process_monitor_main` | `monitor_main` | 过程历史，所有记录与行为保留。 |
| `equipment_metric_groups` | `observation_metric_groups` | 设备状态与过程共用区域配置。 |
| `equipment_metric_configs` | `observation_metric_configs` | 两路共用指标定义，不复制两份。 |
| `equipment_metric_slot_bindings` | `observation_metric_slot_bindings` | 两路共用表，继续按 `target=latest/history` 分别绑定。 |
| `metric_ingest_receipts` | `observation_ingest_receipts` ＋ `energy_ingest_receipts` | 将 `latest/history` 和 `energy` 按回执自身 `target` 精确分流，详见 §3。 |

`equipment_card_configs`、`monitor_curve_group_configs`、`energy_metric_configs`、`energy_consumption_main`、`energy_prices`、`energy_price_hours` 沿用当前表名。能耗样本的回执外键指向新 `energy_ingest_receipts`；实时和过程样本的外键指向新 `observation_ingest_receipts`。两张价格表与能耗指标、样本的业务内容保留。

能耗回执的数据、唯一约束及重试查询由独立表承载。可以在现有 `equipment_observation` 实现内按目标选择对应回执模型及 service，共用纯数据处理函数不得使能耗依赖 observation 回执表；本修订不强制把能耗采样整体搬进价格模块，也不重构价格域。两条观察写入、能耗写入及所有现有读／配置接口和页面 URL、权限、输入输出保持原合同。现行 [v2 合同](../../contracts/published/http-api/equipment-observation-v2/README.zh-CN.md)及路由源码是迁移前对照基准，已发布历史 OpenAPI、示例向量和旧 migration 不改写。

不包括 SMA 自动投递、DS／DAA 调整、真实 PLC、能耗页面位置调整、表计统计口径更改、API 改名或兼容新旧表双写。前端不为表重命名改动。正在暂停的手动演示等 dev 切换后再继续，不向当前 dev 写入演示数据。

## 3. 数据和行为合同

### 3.1 表及 ID

1. 五张表采用保留原数据的表重命名。原主键、字段值、JSON、时间、备注、复核、启用状态、排序、首次使用时间、唯一性与索引语义保留；同一指标的 `latest`、`history` 槽可不同。卡片、曲线中的 `metricKey` 引用继续有效，改名不转换业务键或单位，包括 Human Owner 刚修改的温度单位。
2. 所有旧回执按自身 `target` 分流。`latest/history` 进入 `observation_ingest_receipts`，`energy` 进入 `energy_ingest_receipts`。每个旧回执保留 `id`、`target`、`producer_id`、`event_id`、32 字节 `request_digest`、`outcome`、`processed_at`、`result_record_id`、`mapping_id/revision`、`source_refs`、`task_evidence`、合同和结果版本、`result_detail` 的持久值及空值语义。分流源是回执全表，不得只复制样本当前引用的记录。
3. 所有设备、历史和能耗业务行的原 `id`、`ingest_receipt_id` 数值不变。迁移后每行外键指向正确目标表中的同 ID 回执；保留相应 `ON DELETE RESTRICT` 约束及关联索引。两张回执表各保留 `(target, producer_id, event_id)` 唯一性、对应类型与排序规则和现有默认值，按目标约束正确分域，历史 ID 在各自目标表中不变。
4. 迁移前记录旧回执表实际下一 `AUTO_INCREMENT` 水位；两张新回执表迁移后的起始水位均不低于该值，且高于各自保留的最大 ID。空表也能正常生成；若水位缺失或溢出使条件无法满足则停止。这样不会把拆表前旧命名空间已用过或已分配的较小 ID 作为新 ID 重用。拆分后两个表是独立 ID 命名空间，将来可产生同号回执；不承诺两个表未来全局 ID 唯一，也不以回执 ID 作为跨表身份。重试身份仍是目标、producer 和事件号。以后若需合表或降级，须先处理 ID 冲突、引用映射和去重对账，不能盲目逆向合并。
5. 必须原样保留未被当前业务行引用的回执。实时快照更新后，旧 `stored`、`stale`、`already_stored` 回执可以指向同一个快照 ID，只有快照当前 `ingest_receipt_id` 指向当前 owning receipt，不能要求所有旧回执反向一一匹配。历史 `no_history_metrics` 可以没有业务记录；历史缺测事件以及非空历史记录均应保留。能耗正常成功时回执和对应样本在同一事务提交。未知 `target`、未能证明归属或异常关联必须在破坏性 DDL 前停止并报告，不能猜测分流。

### 3.2 对外行为

1. 三路 `POST` 的路径、请求结构、认证和授权范围、响应结构及 `stored` 等结果不变。当前授权仍在重放前检查；相同目标、producer、eventId 与原请求内容重试返回原结果，不新增业务行。相同身份的不同内容返回既有事件冲突；不同目标独立去重。同一 producer 与 eventId 同时出现在两路甚至三路时不能误串数据。
2. 原子性与失败语义保持：业务行和所属回执在同一事务提交；并发相同事件只持久化一次；提交结果未知时使用原身份和原正文重试。继续保持 `stale`、`already_stored`、`no_history_metrics`、`skipped`、完整快照替换、历史质量、权限与错误码优先级的既有语义。
3. 设备和过程的指标发现、配置、卡片、曲线、管理列表及详情输出保持等价；能耗指标发现、样本、统计、管理、价格接口和权限保持等价。`sourceRefs` 保持现有可选声明语义，不因迁移验证其外部血缘。上海时区及既有 `observedAt`、时间精度、值、备注和零／false／空串均不得改写。

## 4. Alembic 与数据保护

1. 新建唯一后继 revision `d8f2a4c6b915`，`down_revision = da6c32f8a701`，迁移链为 `c9e1a3b5d720 → da6c32f8a701 → d8f2a4c6b915`。开始实施、正式 QA 和实际切换前分别重新核对源码唯一 head、目标实际 revision、目标 UUID、schema、MySQL 8.4、时区、相关表及依赖；若前驱 revision、结构／迁移语义或本修订范围变化，停止并由 PM 修订，不修改旧迁移或制造分支。依赖固定和采集保护见 §4.2。
2. 迁移前检查两张新回执表、五个新表名和中间对象不存在；检查旧表引擎、必要列、类型、排序规则、唯一键、索引、默认值、CHECK 约束的表达式和生效状态、外键的源列、目标列与删除行为。对受本迁移影响的每个 CHECK，除名称和 `ENFORCED` 外还须核对前驱应有的表达式，不能仅因同名已启用就放行。允许的 MySQL 规范化须有同义证据，不得把不同操作符或字面值归一为相同表达式。对所有受影响字符列，包括继承表默认值的列和显式 `utf8mb4_bin` 标识列，核对可信的前驱有效列排序规则与适用表默认值；明确声明并验证支持的前驱默认规则，不能仅凭当前有问题的列自证正确，未知或无法证明时停止。核对目标上可见的跨 schema FK、视图、触发器、事件、例程以及已知直接 SQL 消费者；权限不足、未知依赖或意外结构时停止。不得静默改写旧数据或规范化值来使结构通过。前后按全量主键及字段计算可复核的受控本地对账，精确覆盖源表、两个目标回执表和三类业务行。
3. 在确认三路写入方和相关直接数据库写方静默的维护窗口内执行。对复制、删源行、外键切换和重命名各阶段保持可证明的写入隔离，验证并发写方无法在迁移期间成功写入旧或新相关对象。DDL 隐式提交和元数据锁释放不能被当成整个迁移的原子事务；预检完成后重核状态。不得 `FOREIGN_KEY_CHECKS=0`、`TRUNCATE`、自动 `stamp` 或绕过冲突。
4. 默认按下列阶段执行。先建立能耗回执表，按完整字段和原 ID 复制 `target=energy` 的所有回执并对账。再把能耗样本外键切到新表。然后把旧共用回执表改名为 observation 回执表，并完成五张业务／配置表改名，核对实时与历史外键实际指向。最后在双份逐行一致且引用正确的前提下，从 observation 表精确移除已复制的 energy 行，核对两表自增水位、域约束及全部引用。各阶段保持 §4 第 3 条的维护门禁；实际 DDL 及约束顺序以隔离 MySQL 可行性和 AC05 为准，若无法满足本顺序则停止并回 PM 修订。迁移尾态必须没有 `metric_ingest_receipts` 残表、无跨域行、无丢失、无孤儿引用；这些复制、重命名和删源步骤只作为同一受控迁移的逻辑分流，不将其作为清空数据的许可。
5. 设计阶段记录每个可能部分完成的 DDL 状态、查询判别方式、备份/恢复路径和保持或重建的约束。失败或提交结果未知时，立即停止写入，禁止盲目重跑和自动回滚，报告实际 revision、表集、复制和 FK 状态。提供在隔离 MySQL 上实测的受控恢复流程。`downgrade` 默认明确拒绝自动运行；若后续需要降级，另行设计处理两个表分裂后新回执 ID 同号的策略并取得具体授权。
6. 新源码的观察 profile revision 守卫必须只接受新结构对应的 revision，不能以允许旧 revision 让新 ORM 查询不存在的表。PLC Facts 和通用 business-time adoption 的 revision 列表只做必要的兼容追加，原有限接受范围与目标身份校验保留。当前 ACQ 候选的采集写入、消费接口及过期清理分别使用仅等于 `CONSUMPTION_REVISION` 的条件判断；本后继必须同步将这些条件限定扩展到 `da6` 和 `d8`，使新 schema 仍走采集事件同事务记录、续读和受保护清理，且保留 `da6` 和更早版本既有行为。不能只追加 profile allowlist 后让新 schema 退回旧采集路径或令消费接口 503。隔离测试使用全新合成 profile；正式 dev 的实际私有 profile、目标、reload 和任何需要变更的 adoption 证据须列入后续切换方案，不能输出或提交凭据。

### 4.1 用户允许的旧演示数据例外

Human Owner 明确说，若之前写入的演示数据影响 Alembic，可以清理并重新建立。**本修订的默认和验收要求仍是保留旧数据、所有回执 ID 和去重行为**。清理只能处理已查明属于此前演示且确实阻碍迁移的精确记录，不能清理归属不明、能源价格、PLC 事实、其他业务数据或整表；不能以清理替代非空保留测试，不能作为迁移脚本中的自动 fallback。

若未来 dev 预检发现这类阻碍，切换方案列明原因、精确主键及引用、将失去的历史／回执重试效果、备份和具体操作，纳入 Human Owner 对该 dev 切换的确认。其影响必须如实记录，未受影响数据仍按本节保留。本 r4 的隔离 QA 必须在不清理夹具数据的情况下通过全部保留验收。

### 4.2 采集前驱、隔离链路和 dev 中间状态

1. `da6c32f8a701` 来自并行 ARCH-ACQ-006。r3 验证期间发现已固定的 ACQ 前驱候选发生实质变化，且 ACQ 独立验证当时记录 `qa_failed` 并进入返工；后续状态以 ACQ 任务记录为准，不得将瞬态工作树文件或旧固定摘要当作 r4 最终前驱。Development 须取得 ACQ 返工后的精确候选正式交接、该任务的文件清单、迁移及依赖摘要、隔离迁移自检和实际验证状态，再固定可核验的字节、保留并行改动，并从该候选重新运行本任务完整链路和所列验收。不得把本任务链路测试写成 ACQ 已通过独立 QA 或已被 Human Owner 验收；ACQ 其余业务验收属于 ACQ 自身任务，不扩大为本 r4 的新业务范围。固定后前驱候选或依赖字节再变化时停止正式 QA，重新对账并返回 PM 审查；若 revision、schema、迁移语义或范围变化须修订并重新批准。
2. OBS 非空隔离夹具先在 `c9e1a3b5d720` 上用当期旧观察源码生成三路真实 HTTP 请求、业务数据及回执，记录原响应和全量对账。随后按 ACQ 精确候选的目标身份／维护窗口 guard 和其验证过的步骤进入 `da6c32f8a701`，保留非空观察数据并核对其未被前驱迁移改变，再实施 OBS 后继。`da6` 迁移会新增采集消费结构、历史 trigger 和事件回填；OBS 前后必须核对其表、约束、触发器、回填结果、采集事实、来源及非空消费者／投递等合成状态，证明本任务未更改其数据或行为。ACQ 阶段使用该任务已有合同和候选，不由本任务改写 ACQ 迁移或自行扩充其业务范围；§4 第 6 条所列的继承 revision 判别兼容属于本任务必要衔接。
3. 在当前源码中旧观察 profile 只接受 `c9e1a3b5d720`，数据库若单独进入 `da6c32f8a701`，不能假设观察服务可用。隔离验证以 `c9` 原接口结果和 `da6` 迁移前后的数据对账为基线，完成 OBS 后再用新源码重放；不得临时放宽旧源码守卫冒充已验证兼容。
4. dev 执行本 OBS 后继前，必须先由 ACQ 任务**另行获得针对该 dev 的具体批准并成功完成** `da6c32f8a701` 迁移及保护核验，或者由 Human Owner 另行批准明确的联动切换计划。联动计划必须明确分别批准的 ACQ、OBS 各阶段、源目标身份、备份、写方静默、次序、私有 profile、验证及失败恢复，不能由 OBS 的 Alembic 命令隐式执行 ACQ 迁移。只有 ACQ 阶段成功核对到 `da6` 后才可执行 OBS 阶段，且 OBS dev 切换仍需用户单独确认。
5. 如前驱已被单独采用，服务可在 `da6` 阶段恢复必须先有 ACQ 另行交付并验证的观察兼容版本及匹配 profile。否则，采集和观察的相关服务保持静默，使用经分别批准的单一维护窗口完成两个阶段并核对目标；任何 schema／源码／profile 不匹配或前驱未成功时都不得恢复相关服务。上述安排不授权本任务修改 ACQ 实现、启动或停止现有服务，也不视为当前 dev 已完成 ACQ 采用。

## 5. 实施范围与交接

获得本 r4 的精确批准后，Development 可改动以下交付面，仅限完成上述合同所需的最小变更：

正式工作树存在并行任务，包含正在修改的 `backend/app/plc_facts/v2_config.py`、`backend/common/integration/storage.py` 和 ACQ 前驱文件。实施前逐文件核对当前内容和归属，以语义合并保留已有并行变更，不重置、覆盖或回退。若其他任务新增迁移而使唯一 head 不再为 `da6c32f8a701`，或 §4.2 的前驱及依赖冻结后发生变化，按相应规则停止并交 PM 审查，不私自替换 predecessor 或制造分叉。

- 新增 `backend/alembic/versions/*_d8f2a4c6b915_observation_receipt_separation.py`；旧 revision 原样保留。
- `backend/app/equipment_observation/models/records.py`、`models/__init__.py`、`services/ingest_v2.py`、`services/reads.py`、`services/energy_reads.py`、`profile.py` 及确有引用需要的同模块 `api/routes.py`、`services/guard.py`；不得改公开 API 合同。
- `backend/app/plc_facts/v2_config.py`、`backend/common/integration/storage.py` 中仅与新 revision 准入相关的必要位置；`backend/app/plc_facts/services/async_v2.py`、`async_consumption.py`、`sync_v2_maintenance.py` 中仅与已启用 ACQ 机制的 revision 判别相关的必要位置，保持 §4 第 6 条语义。上述并行文件的固定交接版本和后续 diff 必须按 §4.2 合并及核对，不改变 ACQ 迁移、路由、业务逻辑或其所属任务记录。
- 新增本任务的 `backend/tests/test_observation_receipt_separation.py` 和 `backend/tests_mysql/test_observation_receipt_separation_mysql.py`，以及仅在受影响断言确需适配时修改 `backend/tests/test_equipment_observation_r10.py`、`test_equipment_observation_r10_flow.py`、`test_equipment_observation_domain.py`、`test_business_integration_storage.py`、`test_generic_task_revision_guards.py`、`backend/tests_mysql/test_equipment_observation_mysql.py`。`backend/tests/test_observation_retirement.py`、`test_generic_task_migration_r3.py`、`test_legacy_acquisition_retirement.py`、`test_mapping_migration.py`、`test_equipment_temperature_migration.py` 允许更新指向当前 Alembic head 的断言；其中 `test_observation_retirement.py` 和 `test_legacy_acquisition_retirement.py` 还允许按 §5.1 精确适配当前 ORM metadata 表名断言。原有旧 revision、旧表和历史行为断言保持事实不变。`backend/tests/test_acquisition_consumption_contract.py` 仅允许按 §5.1 适配唯一当前 head 断言。
- 必需的当前事实同步限 `backend/app/equipment_observation/README.md`、`README.zh-CN.md`、`backend/README.md`、`README.zh-CN.md`、`contracts/published/http-api/equipment-observation-v2/README.md`、`README.zh-CN.md`、`docs/equipment-status-process-monitoring.zh-CN.md` 和结构实际变化时的根 `CODE_INDEX.md`。明确标注历史讨论，不改历史规格事实或已发布 OpenAPI／向量。
- Development 创建本任务 `tasks.md`；fresh Verification 创建 `checklist.md`。主协调者在角色事实存在后仅机械同步根 `PLAN.md`、`PLAN.zh-CN.md` 及 `plans/README.md`、`plans/README.zh-CN.md` 的本任务索引，保留并行修改。

如实现确需超出以上 allowlist，先停止该部分并回 PM 修订；不修改真实 `.env`、真实 profile 或白名单以外的模块。隔离验证可创建任务专用临时数据库、容器、profile、脚本与证据，固定身份和生命周期，仅使用可确认归属的隔离资源。不得连接 dev、生产或真实设备执行验证。

Development 应遵循 `backend-arch` 的数据库／接口规范。若新增或修改 `backend/scripts`，另行修订 allowlist 并使用 `backend-script-tooling`；本 r4 不授权交付新的 backend 脚本。治理依据为 `project-governance`、`aiis` 和项目 workflow。测试脚本及敏感夹具放任务专用临时路径，证据摘要写入角色文档，不提交真实配置。

### 5.1 r3 测试断言范围及并行证据保护

1. `test_observation_retirement.py::test_old_operations_absent_from_routes_openapi_and_metadata` 中，当前 `Base.metadata.tables` 必须包含的表名集合更新为本任务迁移后的主表及两张新回执表。保留 `RETIRED_TABLES` 不在 metadata、22 个旧接口退出、现有接口保留和其他检查；不得为通过测试改动历史迁移常量。
2. `test_legacy_acquisition_retirement.py::test_single_head_and_metadata_retire_only_nine_tables` 中，仅对最终比较当前 `Base.metadata.tables` 的预期集合应用本任务映射及回执拆分。保留根据旧迁移计算历史表集、旧 revision 链、九张退役表与 ACQ 六张现役表的断言；历史阶段的旧表名称仍作为历史事实保留。
3. `test_acquisition_consumption_contract.py::test_single_forward_successor` 中，仅将唯一当前 head 断言适配为 `d8f2a4c6b915`，并断言该后继的 `down_revision` 是 `da6c32f8a701`。继续保留 `da6c32f8a701` 自身 `down_revision == c9e1a3b5d720` 的断言及 ACQ 迁移原文件字节证据；该文件其余测试和已发布合同保持原样。
4. 以上文件在并行 ACQ 工作和 QA 中可能是固定证据。记录各文件精确 preimage 与摘要，先在本任务候选中制作有限 diff。若 ACQ Development／QA 正在使用原文件作为验证对象，期间不得改写其工作树验证对象；待其交接或确认不再占用，再对照 preimage 和当前并行修改整合，保留非本任务内容。如 preimage 漂移，重新对账，不覆盖。正式验证时将上述允许的测试断言 diff 与已冻结的 ACQ 前驱实现／迁移字节分开列示，不能把已修改的测试文件冒充 ACQ 原证据。所有权、候选摘要和核对结果由 Development 在 `tasks.md` 记录，Verification 独立核验。

## 6. 验收标准

| ID | 必须达成的验收 |
| --- | --- |
| AC01 结构与保护 | 在真实 MySQL 8.4 隔离实例从精确 `da6c32f8a701` 升级到新唯一 head；§2 表集、分域、列、类型、排序规则、默认、索引与外键符合约定。五表全量数据、业务行、指标配置、卡片、曲线、能源价格、采集事实、ACQ 结构及非空状态和任务外数据的字段值与主键保持。 |
| AC02 全量回执 | 非空合成夹具包含三个目标、多个 producer、跨目标同事件号、旧实时多回执指向同一快照、`stored/stale/already_stored`、历史 `no_history_metrics` 和有记录的历史事件及能耗样本。逐 ID、逐字段对账两个新表与原表分流集合，包括未被业务行引用的旧回执、请求摘要、JSON／NULL、结果和来源元数据；业务引用数值与指向正确。 |
| AC03 真实 HTTP 与去重 | 先在 `c9` 用旧源码和真实 MySQL 建立有效机器身份、权限、合成设备及表计，实际提交三路事件并保存请求和响应；按 §4.2 经固定 ACQ 前驱对账后运行 OBS，迁移后用新源码和新 profile 对三路逐一按原身份、原正文重试，结果一致且不新增行。改变正文验证 409，撤销权限验证先鉴权，跨目标同事件独立，新事件写入正确回执表。验证并发同事件及两表自增水位均不低于迁移前旧表下一水位、空表情况、事务回滚和提交未知重试。 |
| AC04 实时、过程和能耗使用 | 含非空真实槽位、卡片、曲线、不同单位及测值的隔离夹具，验证指标发现、实时整包替换与授权、历史质量与追加、列表详情、卡片和曲线；核对能耗指标发现、样本、统计、管理和能源价格查询与迁移前等价。登录用户和机器 scope 不串用。保留既有 0、false、空字符串、JSON、时间精度和备注。 |
| AC05 防护、失败和恢复 | 验证新名称占用、未知 target、错类／孤儿回执、错误目标身份／revision、未知外键或不可见元数据、写入竞争在破坏性步骤前拒绝或受维护门禁阻断。真实 MySQL 负例至少覆盖：把 `equipment_metric_configs.ck_obs_r10_metric_type` 替换为同名且 `ENFORCED=YES` 的 `CHECK (char_length(value_type)>0)`，以及在源 `utf8mb4_0900_ai_ci` 的夹具把 `metric_ingest_receipts.target` 单列改为 `utf8mb4_0900_as_cs`。两例均在任何改名、复制或其他迁移 DDL 前拒绝，revision 和故障注入后的表结构、数据及回执保持；正确的原生前驱表达式与排序规则正例可升级，已声明支持的其他表默认排序规则须各有真实 MySQL 正例和迁移前后比较。分别在复制、改外键、删源行、重命名和版本登记等实际可中断阶段注入故障，记录状态，无盲目 `stamp`／重跑／清理；在任务隔离实例按文档恢复并重跑、对账通过。 |
| AC06 空库与源码交付 | 在独立空 MySQL 从 root 按既有历史迁移经 `c9 → da6 → d8` 正常走到新 head，遵守各迁移要求并提供各自合成 target/window 参数；在另一非空精确 `da6` 前驱夹具验证数据保留。使用 ACQ 返工后已交接的精确候选及依赖清单，按 §4.2 冻结并核对。针对 ACQ 预检变更，在隔离 `c9 → da6` 负例中核对已有 trigger 的名称、正文、事件、时点及所属表，构造名称及正文看似一致但事件／时点／表错误的 MySQL 可建冲突，确认前驱拒绝激活且原事实保留；正常前驱可完成回填。OBS 前后 ACQ 六张消费表、三个历史 trigger 及其非空合成状态一致。真实 HTTP／MySQL 验证 `da6` 与 `d8` 采集新样本同事务追加事件、同样本 duplicate 不新增事件、消费者续读／状态及过期清理仍可用，旧 `c9` 按原未启用语义处理；不得以 503 或绕过 trigger 算兼容。项目 locked 工具链的定向后端测试、编译、模块 preflight、单一 head、文档链接检查通过；正式交付工作树与独立验证对象一致并记录证据与限制。 |
| AC07 独立核验 | Development 在 `tasks.md` 如实列变更、命令、结果、目标身份、临时资源及 handoff；fresh-context Verification 使用独立任务资源复核上述 AC 和允许范围，记录真实 verdict；QA 通过后仍须 Human Owner 最终验收。 |

隔离验证和源码交付不等于正式 dev 切换、生产部署、SMA/DAA 联调或最终验收。先提交候选和隔离结果，给 Human Owner 审阅具体 dev 库身份、ACQ 前驱采用状态、备份、静默窗口、私有 profile revision 变更、恢复和任何 §4.1 例外。按 §4.2 分别取得所需确认，用户确认前不得对 dev 迁移、清理、停服、重启或写业务数据。保持原有并行任务和用户服务状态。

## 7. 风险与记录

- MySQL DDL 不具跨多步事务回滚；恢复依赖事先核对的备份和阶段证据，不能假设一条反向重命名能撤销全部操作。
- 两张新表以后可出现相同数字 ID；跨表回退、手工 SQL、报表或外部消费者须按目标和表区分。动态 SQL 或不可见外部依赖需要维护方确认，静态扫描不能证明不存在。
- 旧实时回执与当前快照非一一所有权关系，迁移按回执自身目标全量分流。当前权限可能已撤销，验证重放前的授权检查不能省略。
- 目标服务的 profile 缓存和新 revision 需要与数据库切换同步；实际文件、凭据及运行中服务由维护窗口单独处理。
- ACQ 前驱仍在并行开发，迁移新增的触发器、采集写入约束和回填状态属于独立事实；观察服务在 `da6` 中间状态的兼容未获本任务证明。按 §4.2 固定候选、验证链路并处理维护窗口。

## 8. 修订和批准记录

| Revision | 日期 | 记录 |
| --- | --- | --- |
| r1 | 2026-11-19 | PM 草拟表重命名、回执分离、非空数据保留和隔离验证。Human Owner 明确批准实施和隔离验证，dev 切换等其确认；实施前发现并行前驱变化，遵守 r1 停止并返回 PM，本任务没有开始实施。 |
| r2 | 2026-11-19 | 调整至 ACQ 候选 `da6c32f8a701` 的线性后继，补充前驱冻结、非空采集保护、隔离完整链路及 dev 中间状态；Human Owner 已批准实施和隔离验证，dev 切换另行确认。 |
| r3 | 2026-11-19 | 为两个现役 ORM metadata 断言和一个 ACQ 当前唯一 head 断言补充精确 allowlist，明确并行验证证据保护；Human Owner 已批准，独立验证 `qa_failed`，前驱变化后停止正式验证，dev 切换另行确认。 |
| r4 | 2026-11-19 | 明确 CHECK 表达式及字符排序规则预检、两个真实 MySQL 负例，以及 ACQ 返工前驱重新冻结和完整链路复验；Human Owner 已批准实施和隔离复验，dev 切换另行确认。 |

Human Owner 对 r1 的原话为：“批准 ARCH-OBS-003 r1 实施和隔离验证。按规格保留旧数据、回执 ID 和去重行为，接口不变。隔离 MySQL 验证完把结果给我，dev 切换等我确认，演示等改完再继续。”

Human Owner 对 r2 的原话为：“批准 ARCH-OBS-003 r2 实施和隔离验证。按新版迁移链保留旧数据、回执 ID 和去重行为，接口保持不变，也验证采集写入、续读和清理正常。隔离 MySQL 验证完把结果发我，dev 切换等我单独确认，演示等切换复核通过再继续。”

Human Owner 对 r3 的原话为：“批准 ARCH-OBS-003 r3。按规格修正这三处测试断言，跑完回归和独立复核后把结果发我。旧数据、回执 ID、去重行为和接口都保持不变，dev 切换等我单独确认，演示等切换复核通过后再继续。”

Human Owner 对 r4 的原话为：“批准 ARCH-OBS-003 r4 实施和隔离复验。等采集前驱返工交接并固定版本后，验证两处预检修复，重跑完整迁移链和独立复核，把结果发我。旧数据、回执 ID、去重行为和接口保持不变，dev 切换等我单独确认，演示等切换复核通过后再继续。”
