Task ID: ARCH-ACQ-007
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 ARCH-ACQ-007 r2；交 Development 在隔离候选实施及验证，暂不合入正式代码
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 采集事实运行结构兼容及三表命名
Owner: AIIS ICS Architecture Backend / 采集数据模块 Human Owner
Acceptance Chain Reference: 本规格第 6 节及 Development Lifecycle Workflow
Related Task: ARCH-ACQ-004 r3, ARCH-ACQ-005 r1, ARCH-ACQ-006 r1, aiis-ics-arch.aw.sma::SMA-008 r3

# 采集事实版本解绑与表名统一

## 1. 背景与目标

质量模块新增两表的迁移不改变采集结构，但当前采集 profile 的 `target.schemaRevision` 必须等于全库 `alembic_version`，不相等返回 503。此问题来自全库版本精确比较，与 UUID、库名和数据库时钟检查无关。本任务拟在保留现有安全及数据语义下，将采集日常运行准入改为检查实际采集结构和已启用能力，并仅重命名三张表。

当前源码的样本写入、冲突重试、消费者服务和清理仍依据 `CONSUMPTION_REVISIONS` 选择路径；history 的三个数据库触发器承担事件追加、不可变与到期删除保护。设备观测还使用采集内部证据服务，且有自己的独立目标校验。本规格只处理采集侧及其内部证据调用，不修改设备观测自己的版本校验。旧 profile 的版本字段保留兼容并仅供诊断；本任务不改任何现有私有 profile。

r1 候选的隔离验证发现空库链路阻塞：历史迁移 `7b9d1f3a5c7e` 使用现役 `PlcSourceRegistry.__table__` 建表，候选将 ORM 改名后会过早创建新表名。已有库升级的分段隔离试验不能证明同一候选从空库走通完整链路，详见 [Development 记录](tasks.md)。r2 仅增加下述单一历史迁移例外及相应验收，r1 其余范围和语义保持。

## 2. 范围与需求

1. **九表全部保留。** 仅将 `plc_source_registry` → `acq_plc_source_registry`、`plc_facts_history` → `acq_plc_facts_history`、`plc_facts_latest` → `acq_plc_facts_latest`。原数据、主键、唯一约束、索引、字段、时间、语义及消费状态保留；其余六张 `acq_consumption_streams`、`acq_consumption_events`、`acq_consumers`、`acq_consumer_deliveries`、`acq_consumer_operations`、`acq_consumption_activation` 不改名、不删除。
2. **运行兼容检查。** 日常来源管理、样本写入及重试、latest/history 查询、消费 API 和设备观测的采集证据访问，不因全库出现无关后继 revision 或 profile 留存旧 revision 而拒绝。保留现有 MySQL 8.4、目标 UUID、库名、上海数据库时钟、来源登记及代次准入；不引入新的身份、时区或连接框架。检查本任务所需九表、必要列的类型/可空性、InnoDB、主键和关键唯一约束，以及 activation 的 `id=1, ready=1`；不可证明兼容时返回现有 `not_ready` 类错误并记录可定位原因，不泄露敏感内容。结构检查尽量在一次操作/事务中做一次，原有必要的数据库时间验证及事务锁不得省略。
3. **只支持已激活布局。** 不再用 profile 的全库 revision 或固定版本列表判断是否执行消费分支。对已激活布局，新样本必须保持来源锁、流锁、序号分配、事实、latest 和事件的现有同事务语义；在提交前确认该事实对应唯一事件及其流、序号和身份匹配，否则回滚。duplicate/冲突重试也必须核对相应事件，不能把无事件的事实作为成功重复；不改变已有目标绑定、租约、ACK、过期缺口或回执合同。结构未激活或不兼容时拒绝，不回退到无事件写入。
4. **触发器与权限。** 三个 history 守卫继续使用现有触发器语义及事务模型。更名的维护窗口内，由有必要权限的维护账号核对 `acq006_history_append`、`acq006_history_immutable`、`acq006_history_expiry` 的名称、所属新表、时点、事件和定义，以及对象集合；有缺失、错绑或定义不符时保持停写并报错。在线 DML 账号无需查看触发器元数据或获得 `TRIGGER`/DDL 权限，以第 2、3 项的结构/ready 和事务内事件核对提供在线保护；维护账号无法核验时不得切换。触发器变更只能在受控停写维护窗口执行；在线账号无法察觉窗口外对不可变/到期守卫的特权篡改，这是明确运行限制。
5. **前向迁移与维护。** 新增一个基于实施时核实的单一 Alembic head 的向前迁移。历史迁移唯一允许的修改为 `7b9d1f3a5c7e`：在该脚本内以独立结构冻结当期 `plc_source_registry` 旧表名及等价定义，建表、插入和对账不再引用现役 `PlcSourceRegistry` ORM；保持原列类型、可空性、默认值、主键、约束、索引、引擎和原数据处理语义。该脚本的 `revision`、`down_revision` 与其他历史 revision ID 不变，其他历史迁移不得修改。明确前驱、目标 UUID/库名、实际 revision、备份及停写窗口；停止来源变更、采集写入、清理、旧进程与直库写入并等待在途事务，保持原互斥和版本锁保护，核对三表和六张消费表、触发器与外部引用后实施。DDL/恢复及 `cleanup-v2` 等显式维护的操作确认仍须精确核对操作方提供的实际全库 revision 和目标，不能只信 profile；日常运行的旧 profile 字段不再要求与之相同。不得依赖 MySQL DDL 事务回滚、盲目 stamp 或通过删表修复。若停写、锁或对象状态不能证明安全，停止并保留现场。
6. **兼容与非目标。** 已发布 HTTP 路由、字段、授权及客户端行为不变，采集来源准入、触发器、游标、投递回执与数据保留机制不改；不增加通用能力框架、新元数据表、数据库账号权限或配置格式。不得修改设备观测自身守卫、SMA、DAA、全局授权或业务模块；不处理真实设备、实际库迁移、启停服务、发布或部署。旧环境若没有已激活布局，本候选须拒绝，另按获批迁移路径处理。

## 3. 允许触达的后续实施面

- `backend/app/plc_facts/v2_config.py`；`crud/async_v2.py`、`crud/async_consumption.py`、`crud/sync_v2_maintenance.py`；`models/v2.py`、`models/source_registry.py`；`services/async_v2.py`、`services/async_consumption.py`、`services/async_source_registry.py`、`services/observation_evidence.py`、`services/sync_v2_maintenance.py`、`services/sync_source_registry_import.py`。
- `backend/scripts/plc_facts_maintenance/main.py`、`source_registry.py` 及其 `README.md`、`README.zh-CN.md`；`backend/app/plc_facts/README.md`、`README.zh-CN.md`；`docs/acquisition-data-guide.md`、`docs/acquisition-data-guide.zh-CN.md`；`contracts/published/http-api/plc-facts-v2/README.md`、`README.zh-CN.md`。仅更新与新表名、日常检查及维护确认直接相关的文字；历史步骤保留历史时态，已发布 JSON 工件不变。
- `backend/alembic/versions/` 下唯一新后继迁移及唯一历史例外 `20261113_1600_7b9d1f3a5c7e_plc_source_registry_single.py`，后者仅限第 2.5 条；`backend/tests/` 下 `test_plc_facts_v2.py`、`test_acquisition_data_browse.py`、`test_acquisition_source_registry.py`、`test_acquisition_consumption_contract.py`、`test_generic_task_revision_guards.py`、`test_quality_revision_guards.py`、`test_equipment_observation_r8.py`、`test_legacy_acquisition_retirement.py`、`test_observation_retirement.py`、`test_observation_receipt_separation.py`、`test_generic_task_migration_r3.py`、`test_equipment_temperature_migration.py`、`test_mapping_migration.py`；`backend/tests_mysql/` 下 `test_plc_facts_v2.py`、`test_acquisition_consumption.py`、`test_acquisition_source_registry.py`、`test_legacy_acquisition_retirement.py`、`test_observation_receipt_separation_mysql.py`；确有必要时各目录可新增一个本任务专用测试文件。历史迁移断言按历史对象保留，不机械改写。
- Development 创建本 bundle 的 `tasks.md`，Verification 在 handoff 后创建 `checklist.md`；协调者按 workflow 处理状态索引。其余路径不在本 Revision 实施 allowlist；发现必要增项或工作树并行冲突时停下并返回 PM 修订，不覆盖他人改动。

## 4. 风险与恢复

同库改名会影响直接 SQL、外部报表、维护脚本和缓存 ORM；切换前须列出已知引用，未知外部直查需由目标 Owner 确认，禁止假定兼容。MySQL DDL 可部分提交：失败后继续停写，记录实际三表、触发器、六表状态及 revision，对照备份和已提交事实决定经另行授权的前向修复或恢复；已有新数据不能安全重放时不得直接回滚覆盖。不同源码/表名不能混跑；恢复时间和可重放性须在目标操作批准时核实。

## 5. 验收标准

| ID | 验收 |
| --- | --- |
| AC01 | 同一正式候选在隔离 MySQL 从当前已激活布局及有数据、已存在消费状态的单一前驱执行新迁移；逐项对照九表的登记、事实、latest 水位、事件、游标、待投递、操作和 activation，证明三表改名、其余六表保留且数据与关键约束不变。维护账号检查三触发器的表、时点、事件、定义及守卫行为；异常定义、名称冲突或部分状态拒绝切换。 |
| AC02 | 同一候选不改旧 profile，在隔离目标应用与采集无关的后继迁移后，来源管理、普通样本 POST/duplicate、latest/history、消费 API、受控清理及采集内部证据仍可运行；错误 UUID、库名、MySQL 版本或时钟继续拒绝。设备观测自己的 guard 仍按原规则。 |
| AC03 | 分别构造缺表/列、关键类型或唯一约束不兼容、`ready` 缺失或为 0 的目标；读取/写入明确拒绝且不产生部分事实或事件。在线账号无 `TRIGGER` 权限时，正常事务仍工作；隔离测试移除或破坏追加触发器，使事件缺失或不匹配时，新写入和 duplicate 不得成功，事实、latest 与流序号回滚或保持不变。 |
| AC04 | 验证同流并发、回滚、同字节重试、来源失配、消费租约/pending/ACK、过期清理和缺口保护与现有合同一致；使用维护账号模拟三守卫的错误所属表、时点、事件、定义及不能读取元数据，均不得通过维护核验。显式维护提供错误实际 revision/目标时拒绝。 |
| AC05 | 同一正式候选在隔离空库从 Alembic 根 revision 连续执行完整迁移链至新后继，经过 `7b9d1f3a5c7e` 时创建等价的旧名登记表，后继再完成三表改名；不得分阶段替换源码、手工补表或 stamp。核对该历史迁移仅有第 2.5 条例外，revision ID 和前驱不变、旧表结构及原迁移语义等价；检查已发布合同 JSON 不变，以及受影响 ORM、维护 CLI、采集 API 和设备观测内部证据回归。记录检查命令、环境、结果、仍需确认的外部直查及中断恢复限制。独立隔离 MySQL 若尚不可用，其创建或 Docker 生命周期操作另行批准。 |

## 6. 审批与交接

Human Owner 已批准 ARCH-ACQ-007 r2 按本规格实施和隔离验证：空库安装、已有库升级、无关迁移后采集仍能读写三项均须验证；只用专用 MySQL 和合成数据，测试后清理所属资源。暂不合入正式代码，不动 dev 库、8000 服务及私有配置。现有 r1 Development 记录保留为历史证据，不视为 r2 交接或验证。由 Development 读取 `backend-arch`、`backend-script-tooling`、`code-document-indexer` 并按本 Revision 实施、记录自检；随后 fresh-context Verification 独立复核同一候选，Human Owner 再作最终验收。源码和隔离验证获批不等于批准真实数据库迁移、清理或服务切换；这些动作须另行指定目标和授权。

| 日期 | Revision | 记录 |
| --- | --- | --- |
| 2026-11-24 | r1 | PM 草案：采集运行结构兼容、三表前向改名和隔离验证；等待范围批准。 |
| 2026-11-24 | r1 | Human Owner 明确回复“好的 批准这个spec”，批准精确 r1 范围；批准版 SHA-256 为 `a31d8603b704445d3775f0ba08317c7c1173e69772ce36a946073faa7d3ea9f7`。真实数据库迁移、清理、服务切换及未授权 Docker 操作仍须另行批准。 |
| 2026-11-24 | r2 | PM 草案：仅新增 `7b9d1f3a5c7e` 历史迁移例外，明确同一候选的空库全链、已有库升级及无关后继验收；等待 Human Owner 批准精确 r2。 |
| 2026-11-24 | r2 | Human Owner 明确批准按当前规格实施及隔离验证；批准前规格 SHA-256 为 `e370aed4f0f22039674d7368d4e6f32f886322cd41391a962789619815e78d60`。仅使用专用 MySQL 和合成数据，验证空库、已有库升级及无关迁移后采集读写，测后清理；暂不合入正式代码，不动 dev 库、8000 服务和私有配置。 |
