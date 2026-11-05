Task ID: ARCH-BE-010
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: Human Owner 已精确批准 ARCH-BE-010 r2，仅按 STD 进入 r2.7 A源码阶段；PM -> Development；实际G-T采用、数据库/Docker/B、迁移执行、DAA及发布仍未批准
Task Namespace: aiis-ics-arch
Classification: root
Capability: T1 时间兼容、八类业务异步接线与完整 provider 机器合同
Owner: Backend Core 与 equipment、performance、monitor 公共业务模块
Depends On: r1 A0 源码；ARCH-BE-009 的唯一前驱迁移；实际采用另受本 Revision G-T约束
Related Task: ARCH-BE-009, ARCH-AW-008, ARCH-BE-003, ARCH-BE-006
Updated: 2026-11-04

# r2：T1 有界实现范围（待批准）

## r2.1 当前效力与 Revision 关系

Owner 选择后端 API 优先、DAA 开发与阶段 C 联调暂缓，并授权先整理无需逐项确认的准备。本次效力仅为 **PM 起草 r2**。没有收到 r2 实施批准；“好的／开始”不登记为 A0 接受、T1 提案确认或最终验收。

r1 已选择 T1，且只批准 A0。其 Development 与 fresh-context QA2 已完成：220 项测试、437 项探针、88 次边界请求通过，F-QA1-001/002 关闭；这些是 A0 证据，**A0 Owner 接受及整体最终验收仍 pending**。来源为本 bundle 的 [tasks](tasks.md) 与 [checklist](checklist.md)，不是 PM 重新执行。四项冻结旧 profile 失败仍依原记录分别归因，不宣称默认整套全绿。

下方“r1 原文保留区”完整保留已批准 spec（SHA-256 c33cd260dc74542f36436f31738e823734ae4bc75cf087a0dbb76c2d4c3dcaf9）及批准收据，不改写历史。本 r2 若获批，以下增量与明确替代项优先；r1 R01–R10、八份请求 JSON、字段／单位／缺测、业务键、两摘要、匿名边界和永久最小回执继续有效。tasks/checklist 现仍是 r1 A0 事实面；本轮不预建或修改任何 r2 Development/QA 证据。

| r2 delta | 精确改变与代价 |
| --- | --- |
| D01：拆分 G-T | 替代 r1 §3/§10“真实时间专项证明后才实施 A1–A3”的先后：r2 获批后可先实现**关闭态源码**、有限时间 adapter、迁移文件和完整合同；实际业务写入采用仍等待 G-T。源码 A 不证明真实数据库已整改。 |
| D02：冻结 T1 有界接面 | 固定 13 张既有表的 41 个日历时间列、生产日期的兼容规则和 4 个新表；只改这些表的实际已知后端读写路径，不扩成全仓时间治理。历史调查／转换／采用另批目标与窗口，unknown 不自动处置。 |
| D03：冻结接链与 A1–A3 | 明确 BE009 先、BE010 后，补齐 4 个已声明 Model 的 DDL，实际 async Service/CRUD 在关闭态完成。没有新业务副本、共享幂等平台或隐式建表。 |
| D04：补齐机器合同 | 修复 A0 OpenAPI 请求 Decimal 暗示可用字符串、200 空 schema、默认 422 壳等 provider 缺口；固定 8 路 typed 成功／错误和发布工件。冻结的业务数值与回执含义不换义。 |
| D05：采用证据门槛 | 增加默认空的模块本地采用凭据路径及有限凭据校验；单独设置 storageProfile 不能使入口 ready。凭据是受控运维证据，不能认证匿名 producer，也不构成平台 ACL。 |

本次建议一次批准 r2 的源码范围及上述兼容策略；批准后可按 r2.7 完成源码交接，不要求再无条件升 r3。真实目标／unknown 处置如超出本列集或改变字段语义，才回 PM 新 Revision。真实 DB/Docker 操作、采用、B、DAA/SMA 接线及发布都保留各自明确批准，不能由本次范围批准自动接续。

## r2.2 固定依据与相邻任务

PM 当前只做源码和文档检查，不运行项目代码或探库。输入为完整 r1 bundle、当前 A0 路由／Schema／Model／公开原语、既有 BE003/BE006 writer/reader、[AW008 bundle](../ARCH-AW-008-stage-c-facts-contract/spec.md) 与 [demand-r1](../../contracts/demands/automation-world-facts-integration.zh-CN.md)。demand-r1 当前仍为 proposed；其中单温度和简化 ACK 是语义示例，本任务继续采用完整十值温控及可靠业务回执。AW008 文档通过不表示 provider、DAA 或 SMA 软件就绪。

当前静态迁移链终点为 f6a8c0e2b4d6，迁移定义累计 64 表；A0 又声明 4 Model，metadata 为 68，但没有这 4 表的迁移。真实库 revision／行数／时区均未调查，不能据此称真实库为空或已到源码 head。

计数口径：64→71→75及metadata计数均指本仓Model／迁移管理的应用表，不含Alembic自建维护表alembic_version。B按应用表集合及各阶段表差核对，维护表单独核验，不断言information_schema全部表总数恰好75。

与实际 BE009 PM 已协调如下唯一链；双方均仍为 PM 草案，不互相授予实现许可：

| 阶段 | 精确迁移与范围 | 静态 schema／metadata 口径 |
| --- | --- | --- |
| 当前 | 既有 f6a8c0e2b4d6 | migrated 64；含 A0 声明时 metadata 68。 |
| BE009 前驱 | backend/alembic/versions/20261104_1200_0a2c4e6f8b10_add_plc_facts_integration.py；revision 0a2c4e6f8b10，down_revision f6a8c0e2b4d6 | BE009 独立 app/plc_facts 新增 7 表，schema 71；两方 Model 都在源码时 metadata 75，其中 BE010 pending4 不得算已迁移。 |
| BE010 后继 | backend/alembic/versions/20261104_1400_1b3d5f7a9c20_add_business_integration_receipts.py；revision 1b3d5f7a9c20，down_revision 0a2c4e6f8b10 | 仅新增 equipment_integration_receipts、performance_integration_receipts、performance_integration_observation_events、monitor_integration_receipts；schema 与 metadata 均75，前提是没有其他获批结构变更。 |

BE009 7表为 plc_facts_stream_state、plc_facts_source_bindings、plc_facts_batches、plc_facts_sample_receipts、plc_facts_raw_samples、plc_facts_cycles、plc_facts_latest_points；本任务不改它们、旧 monitor raw/latest 或事实清理器。不得双方从 f6 各自分叉，不重写旧迁移，不拿全量 create_all 代替 71／75 阶段断言。执行迁移仍另批；当前只固定待实现文件。

BE010 是 common/integration 的唯一 writer；BE009 使用自有 facts helper，不依赖新业务时间采用。BE009 无须等待 BE010 即可交事实源码；BE010 源码可并行准备，迁移落库与合并后的 schema 验收必须按上述顺序。若前驱未按精确文件落定，BE010 停在迁移交接前，由两 PM 协调并提交受影响 Revision，不另造 head。共享合同索引由 BE009 先增事实入口、BE010 后增业务入口，不并行覆盖；根六索引由 coordinator 维护。

## r2.3 T1 时间边界、固定列与采用

### r2.3.1 两种运行状态

1. **unadopted 且采用文件路径为空（默认）**：旧认证和 Projection 直接走原时间代码路径，不读取采用文件、不新增采用 DB 探针、不转换旧值、不改变原事务／游标／审计。新入口仍先按原模块准入拒绝 403；准入通过则 503 module.integration_not_ready，无业务对象读写。完成源码、存在新表或 env 写成任意字符串均不能绕过此状态。
2. **shanghai-v1（受控采用后）**：模块配置同时提供有效采用凭据；每个事务在业务读写前校验目标、schema、固定列 profile 和数据库时钟。新入口没有合格凭据或探针不符仍返回 not_ready。旧入口保持原认证、权限、scope 和 wire；已选择 adopted 却凭据失效时，应在任何业务写入前拒绝并保留失败事实，不能偷偷退回 UTC 写入。

新增 EQUIPMENT_INTEGRATION_ADOPTION_FILE、PERFORMANCE_INTEGRATION_ADOPTION_FILE、MONITOR_INTEGRATION_ADOPTION_FILE，默认空，仅显式绝对路径，不查找约定目录、不从真实 env 推测。三个公开 example 只追加空占位；本轮不读写真实 env。现有 enabled/scope/producer/storageProfile 规则不变。

采用凭据版本 business-time-adoption/v1，按模块记录：profile=shanghai-v1、module、数据库 serverUuid/schema、精确 schemaRevision、sourceRevision、固定列清单摘要、下述显式 basisProfile、私有调查／迁移／校验报告摘要和引用、备份引用、Owner 对目标采用的批准引用、verifiedAt（+08:00）、state=adopted。只读工具先输出 candidate，不能自行把它当批准。运行时只接受匹配本源码固定列 profile 和目标 1b3d5f7a9c20 的 adopted 凭据；后续 schema 升级需显式更新采用记录，不能默默放宽 revision。凭据不得含口令／DSN／行原文；校验失败不打印其内容。

basisProfile 是固定结构而非报告摘要的推断：profileId 固定 be010.fixed-basis/v1；equipment/monitor 必须含 legacyNaive、systemWire 两键；performance 另必须含 manualNaive、manualAuditWire。四种固定键的值仅允许 utc_wall 或 shanghai_wall，分别指无offset UTC或上海墙上值；缺键、额外键、unknown、其他offset和未识别profile均拒绝采用。此结构的取值由目标证据及Owner采用记录确定，运行时从已校验凭据读取，不从机器TZ、时间数值或sourceRefs猜测。各owner integration_storage 的静态字段/接口分组负责选键，调用方不能提供表名、列名或自定义选择规则：

| 固定分组 | 输入解释／旧wire view所用基准 |
| --- | --- |
| 原八路明确UTC的来源键／reported/observed字段、actor receipt与UTC水位语义 | 固定UTC，沿原UTC formatter／fingerprint，不受basisProfile改写；已冻结JSON result原文不转换。 |
| 旧helper原样保留的legacy naive事件/来源时间，以及旧legacy接口直接展示的对应字段 | legacyNaive；同一固定分组内必须证明该基准统一适用，读时由上海存储逆转换到该墙上基准再走原格式。aware输入须在owner原路径丢弃offset前保留其明确同瞬间，不能先去offset再当naive解释。 |
| 原func.now()/本地系统时间生成且被旧接口直接展示的created_at/updated_at | systemWire；已明确UTC生成/格式的列仍走上一固定UTC分组，新表不走legacy view。 |
| performance_main.start_time/end_time的旧人工/legacy naive pair及原直接展示 | manualNaive；不改变已有完整pair优先级，带offset输入按明确同瞬间处理。 |
| performance_main.manual_override_at的旧直接展示 | manualAuditWire；保留人工0、操作者、原因，不能用systemWire或宿主当前TZ代替其证据。 |

这些键不编码任意历史cohort或每行offset。若同一旧输出字段含不同基准，必须可由**现有且已证明可靠的来源标识和上述静态分组**唯一选定旧view；equipment_id是否NULL不能单独证明时区。没有这种判别、aware/naive来源要求不同旧wire却已丢来源、同组多个基准或任一unknown时，本r2不能保持原wire，G-T拒绝解除。不能靠填写两种enum宣称混合历史已兼容；新增来源标签/逐行映射或更复杂profile须独立维护范围/PM Revision。

凭据校验提供部署错误防护，并非密码学身份认证或对数据永久正确的证明。目标匹配还须查询数据库本身的 UUID/schema/revision；仅复制文件或修改 env 不构成 G-T。凭据持久化在采用目标所属、显式指定且由部署方保护的外部文件，原报告／备份在同目标受控私有存储，不进入公开仓或临时证据目录；采用完成后文件以只读方式供固定版本读取，替换须原子且保留旧版摘要。

源码拒绝三类误配：已选择 shanghai-v1 而凭据无效／探针不符；不认识的profile；unadopted却保留非空采用文件路径（不用读文件或探库即拒绝写）。旧入口沿其原模块失败通道拒绝，不新增认证或改变错误壳。这能防止只改profile的误回退；无法识别“旧二进制＋整份旧配置＋仍有效旧DB账号”的重新启动。因此实际采用必须先停所有能写上述业务列的旧writer/job，固定获验证二进制与只读配置／凭据，并阻止旧业务部署重新取得该列集写权。**旧CA对raw/latest的兼容writer不属于本业务停写/撤权范围**，不能笼统撤销共享DB账号使事实采集失效。如果业务writer与CA/raw共享凭据，目标采用方案必须另批精确按表权限隔离或新业务凭据及旧业务启动隔离，保留raw/latest的既有资格；当前不改账号/权限，不设计权限管理平台。无法保证这一有限部署前提时，G-T仍不解除。不能假称本框架在数据库层阻止任何旧版或越权直库写入。

采用后不得把配置改回 unadopted 而继续向已转列写 UTC；回退同样需要停写与明确方案。默认unadopted的旧路径兼容与采用后的固定版本／账户隔离是不同阶段。

### r2.3.2 固定时间列（13 张既有表／41 列）

下表是**源码 writer 事实与整改目标**，不是历史行已被证明。每个待采用列须覆盖全部行／来源，包括 equipment_id 为 NULL 的 legacy 行；按该条件只能帮助分类，不能推定时区。

| 表 | 固定列 | 原源码依据与采用策略 |
| --- | --- | --- |
| equipment_temperature_samples | sampled_at, created_at, updated_at | HTTP 来源为 UTC 毫秒，系统列 UTC_TIMESTAMP(3)；已证实 UTC 才按同瞬间转上海。完整十值、ID、业务 unique 不变。 |
| equipment_temperature_sample_receipts | sampled_at, created_at, updated_at | 同批转换物理时间；actor/sampleId、fingerprint、JSON result 中原 UTC 字符串逐字保留。 |
| equipment_drive | timestamp | HTTP UTC；sync aware 转 UTC、naive 保留；默认 CURRENT_TIMESTAMP(3) 依历史 DB 设置，其他 legacy writer 未知。所有来源先分类；不能整表推定 UTC。 |
| equipment_production_parameters | timestamp, entry_time | 同上；entry_time 是事件事实，不用到达时间替代。total_time 为分钟不转换；保留 coil binary key／NULL。 |
| equipment_mapping_receipts | sampled_at, created_at, updated_at | 现 HTTP UTC；保留旧身份、fingerprint/result，物理键转换。 |
| performance_main | reported_start_time, reported_end_time, first_observed_at, last_observed_at, start_time, end_time, manual_override_at, created_at, updated_at | reported HTTP UTC；观察含 Projection 原 collected_at；人工 pair 可有 naive/aware；manual_override_at 含 datetime.now()/func.now()；系统列旧 DB now()。后四类不能由当前代码反推历史。所有 pair 与水位同批统一，保留原精度、NULL 和人工0。 |
| performance_process_temperature | record_time, created_at, updated_at | HTTP UTC；sync aware 转 UTC、naive 保留；系统时间依 DB。与父域、zone binary key、来源毫秒一致转换。duration 为整数分钟。 |
| performance_process_tension | record_time, created_at, updated_at | 同上，min/avg/max 与 NULL 补缺规则不变。 |
| performance_process_speed | record_time, created_at, updated_at | 同上，不改速度单位或父引用。 |
| performance_mapping_receipts | sampled_at, created_at, updated_at | 来源／系统列按证据转换；actor/stream/sampleId、UTC result 与旧摘要保留。 |
| performance_mapping_observation_state | last_sampled_at, created_at, updated_at | 当前 HTTP UTC 水位；转换不能遗漏零活跃设备。状态、父id、旧兼容 cache 与已有投递证明保持。 |
| monitor_history_process_curves | sampled_at, created_at | HTTP sampled_at UTC，legacy 可NULL；created_at 含 DB now()、Projection aware→UTC/naive保留。逐来源证明；33指标和字段存在 fingerprint 不改。 |
| monitor_mapping_receipts | sampled_at, created_at, updated_at | 同业务来源键转换；旧身份、result 和摘要不改。 |

四个新表没有历史数据写入事实：三 receipt 表的 source_time/committed_at/created_at/updated_at，以及 observation_events 的 sampled_at/committed_at/created_at/updated_at，共16列，仅上海 DATETIME(3)，全部由 Service 明确赋值；不依赖 UTC 或系统 TZ 的自动 default。共计采用接面为17表57日历时间列，新增物理表仍只有4张。

performance_main.production_date 是纯 DATE：旧 HTTP 继续从原 UTC 瞬间推导上海日期；旧 Projection 继续使用原事实的日期语义，不因存储 adapter 改用转换后的墙上日期。已有 DATE 不平移；若调查证明原日期本身错误，另列具体数据修正规则、数量与批准。总秒数、过程 duration、参数 totalTime、单调时间、raw/cursor 均不机械加8。

equipment_temperature.timestamp、performance_split/transform/lineage/push_down 自有审计时间、monitor_history_energy_consumptions 不在列集。async_lineage 或 async_split 触达 performance_main／过程记录的路径只适配上述列，不改变其自有审计、推送行为或规则。若发现固定列之外的值必须同时调整才能保持业务一致，暂停受影响采用并回 PM，不能继续扩成全模块整改。

### r2.3.3 有界存储 adapter 与旧外部兼容

- 保留旧八路输入 DTO、校验、UTC 规范化／旧 fingerprint 算法与 response 表示。旧逻辑先得到原 UTC 语义，再由模块 SQL 边界转上海物理键；读后构造兼容 view 再交原 formatter。禁止改全局 serializer、全局 Engine/session TZ、ORM Base 或把已绑定 ORM 字段临时改回 UTC 导致脏写。legacy naive 输入按已证明的原字段／writer basis 解释；依据未知不得采用。
- 新 integration 时间在边界转固定 +08:00 一次；新请求来源时间与新回执始终携带 +08:00。数据库 DATETIME 写入上海无 offset 墙上值，保留既有列精度；SQLite 仅未来另议，不拿它替代本轮 MySQL 行为证据。既有秒列不扩 precision，也不伪造毫秒。
- 所有17表的已知 create/update 路径显式赋应写系统时间，覆盖旧 func.now()/UTC default/onupdate 的实际使用；不修改旧 DDL/default、不依赖宿主或 session TZ。数据库 UTC_TIMESTAMP(3) 的同瞬间只在有限公共时间原语转换到 +08:00，模块不得散落加8。旧表仍有 legacy default 不意味着允许直库 writer 继续使用：采用计划必须覆盖实际 writer，未覆盖则不采用。
- sampledAt/recordTime、reported/observed pair、人工 pair、查询起止和水位按同瞬间适配；上海日筛选用上海存储边界。旧 legacy 日筛选如原先按 UTC 墙上日期，换成对应的上海存储区间以保留原结果；不借此更改旧筛选含义。新 integration 不新增 GET。既有 HTTP 显示 API 的 UTC wire 是兼容例外，不宣称全仓 API 时区整改完成。
- 旧 actor receipt/fingerprint/result 不重算为 bi-json/v1；旧业务 fingerprint 保持原算法与 UTC view，不以新摘要覆盖其列。新 receipt 独立保存 requestDigest/businessDigest；新业务判断使用实际值、原存在集合及 owner 规则，不能直接拿两个不同算法的摘要相等来推断业务相等。新写入需要旧业务 fingerprint 时，用 owner 的 legacy 兼容 view 产生；不伪造 sampleId/actor。跨通道投递等价仍不承诺。
- 生产复用原设备水位行以串行裁定；新历史成功证明只查 integration_observation_events，不从 actor cache 造新事件。水位 cache 的 fingerprint/result 保持其 owner 旧兼容形状，typed 新回执完整结果在新表。对采用基线相同毫秒但没有新事件证明的观察不冒认历史成功；同刻冲突，旧于基线按既定 stale 裁定。切换前必须对账旧通道未完成投递和基线，不能靠删除水位实现切换。
- 人工重量非NULL（包括0）始终优先；manual pair → reported pair → first/last 的顺序、整数总秒0..2147483647和过程分钟不变。涉及系统人工审计只替换明确列的时间来源，不清除覆盖、操作者、原因或谱系快照。对所有有效 pair 先保证同一明确基准再相减。

采用探针的IO明确归各owner CRUD：已有allowlist中的 app/{equipment,performance,monitor}/crud/async_integration.py 各增加 probe_storage(db: AsyncSession)；新增对应 crud/sync_integration.py 各提供 probe_storage(db: Session)。两者返回同一纯 StorageProbe 结构（serverUuid、schema、schemaRevision、utcNow），仅在传入的当前会话执行固定只读UUID/schema/alembic_version/UTC_TIMESTAMP(3)查询；无新Engine/全局Session、业务查询、commit或rollback。revision使用当前读（共享读锁，不取排他全局锁），避免探针预先建立RR旧快照；多revision行或目标不符拒绝。每个新事务/竞争恢复事务重新探测，不能沿用上次事务或全局ready缓存。

新旧async API的本模块Service调用async探针，旧sync Projection的本模块Service调用sync探针，均先完成本地配置/凭据校验再进入业务访问；默认unadopted空路径直接旁路，完全不调用探针。Projection继续使用host传入的同一Session和business/cursor/audit事务，Service不另开事务或提交。只读维护CLI通过模块显式export的sync探针做目标核验。common/integration/storage.py及模块integration_storage始终只接收探针值和凭据做纯解析/转换/校验，禁止把SQL移入这些纯helper。

公开合同有限补齐：common.integration.storage登记StorageProbe、AdoptionContext、parse_adoption_manifest(value,module)、validate_adoption_probe(manifest,probe)、to_storage_time(value,basis)、to_legacy_time(value,basis)；各模块manifest只为维护工具显式export integration_storage:BUSINESS_TIME_COLUMN_PROFILE及crud.sync_integration:probe_storage。async探针为同owner内部调用，不成为跨模块写入口。Core PUBLIC_SYMBOLS仅增上述common符号；owner profile/probe只走各自manifest exports，不冒充Core公共CRUD。合同双语及准入正负例同步这些确切边界/纯函数行为，probe不接受任意SQL或业务字段。

### r2.3.4 G-T 的可执行后置路线

r2 源码采用 gate 不要求先有真实数据调查，避免循环；它以合成输入、离线 SQL 和拒绝路径完成 A。真实采用另批，按以下次序只处理上述13表41列及必要 DATE 核验：

1. 明确目标 schema/账号/只读操作、源码 revision 和窗口；使用有限只读工具调查 schema、时钟／默认／精度、各 writer 来源与数量。按列／可证来源分已证 UTC、已证上海、其他已知 offset、unknown；不以0行假设跳过调查。
2. 固定原值／主键／前后摘要对照、备份、停全部相关 writer、转换候选与 unique/FK/pair/水位冲突预检。unknown 只要仍在待采用列，G-T 不解除；Owner 另批证据分类或具体隔离／修复范围，r2 不授权删除、归零或推定它们。若真实规模／来源要求列集外整改，另立有界维护任务或 PM Revision，不无限扩 r2。
3. 另批精确 data-only 转换命令／输入计划和事务／恢复策略后执行；4表 schema 迁移和历史 data 转换是两项操作。本 r2 的只读工具**不实现 apply、任意 UPDATE 或自动纠错**；实际转换须由有精确目标与数据对照的独立维护范围承接。已知 UTC→上海转换一次，已知上海不再平移；所有实际混合来源均须证明处理完。保留旧JSON result字节、ID、值、字段存在、FK、旧摘要。
4. 对转换后目标做只读 verify，覆盖全列、键/水位/pair、旧请求重放、来源与系统时间，形成候选凭据。Owner 根据报告批准采用，安装 adopted 凭据并按唯一权威 writer 切入；新业务源在这之前仍关闭。只读工具不能代替实际旧 API/Projection 兼容实证。
5. 完整新业务 B 在 A1–A3 源码与专项采用测试具备后执行，另批隔离 MySQL 8.4.6。B 可在可丢弃目标用合成旧行完成真实采用夹具；这不证明生产历史已整改，生产采用仍需其目标独立 G-T。B 不是尚未实现业务源码的前置。

同设备业务域仅一个权威 writer 是数据采用规则，不认证匿名调用者。关闭匿名入口是默认回退；保留新业务、永久回执和事件证明。恢复旧 writer 前先对账新水位与未完成投递；物理时间反向转换／恢复备份另批，不自动 downgrade 或整列减8。

## r2.4 A1–A3：真实异步业务接线与提交

八路路径、所有 data 字段、0/省略/null、单位与 r1 §4–§7 完全沿用，下方8份 JSON 仍为完整请求示例。没有单温度替代接口或任意实时 upsert。

| 阶段 | 精确业务实现 | 必须直接证明的结果 |
| --- | --- | --- |
| A1 equipment | async API→本模块 async_integration Service→CRUD；写既有温控、drive、参数表，连同本模块 receipt/sourceRefs/mapping。 | 温控完整十值不可变；drive/参数仅补NULL，任一冲突整次失败；不同卷／同小时不同毫秒独立，FLOAT32与Decimal读回。 |
| A2 production | 本模块 observation Service；设备水位锁→历史新事件 current-read→按主键升序锁活跃/目标主行→写主行/前卷/水位/事件/receipt。首次水位由真实 unique 处理。 | 历史成功先于 stale；同刻冲突；零活跃退出/unknown仍有持久水位；新建/更新/退出/重激活，人工0两种提交顺序，pair来源及前卷处理正确。 |
| A2 process | 本模块 process Service，共用有限事务方式但每种 typed fields；父锁与父设备/卷验证，再写子和receipt。 | 父必须来自本通道可靠 in_production 回执；404不造父、409不匹配；父回执丢失可重放恢复，结束父可接合法晚到子；补后min/avg/max、整数分钟不破坏主用时。 |
| A3 monitor | async Service/CRUD写既有33指标曲线及receipt。 | 完整内容/字段存在不可变，整数温度不截小数，FLOAT32不静默下溢；同业务内容复用、异值409，无raw依赖。 |

各新请求独立 AsyncSession；准入及 unadopted 拒绝发生在业务依赖之前，合格采用探针后才访问业务。CRUD只select/add/flush，无commit、HTTP、业务状态机；Service拥有rollback/commit。复用纯领域函数，不调用旧sync Service、旧HTTP handler或伪User；不得把新的声明身份带入 actor receipt。

同投递优先查原receipt；业务拒绝后先rollback，再在新一致性视图恢复已提交receipt，确保异内容 event 冲突优先。仅MySQL1062且确切命名的本任务投递unique、目标自然键unique、观察事件unique或首水位unique允许竞争恢复；最多3次事务尝试（含首次），每次先rollback并重新current-read，耗尽503 integration_unavailable。死锁/锁超时/其他DB错误不转duplicate；其他Integrity映射脱敏内部错误。目标自然键沿用 r1/既有 Model 名称，不修改全局隔离级别。

真实命名集合为 uq_equipment_integration_delivery、uq_performance_integration_delivery、uq_monitor_integration_delivery、uq_performance_integration_observation_time、uq_performance_observation_equipment、uq_temperature_sample_business、uq_equipment_drive_http_business、uq_equipment_production_parameters_http_business、uq_performance_main_http_business、uq_process_temperature_http_business、uq_process_tension_http_business、uq_process_speed_http_business、uq_monitor_curve_http_business；不能按“任何1062”宽泛重试。

业务、必要来源/映射、事件索引、水位与最小回执同事务提交。sourceTime取原sampledAt/recordTime；committedAt是获胜事务在commit前最后取用的数据库时钟值，成功只在该事务commit及完整可失败依赖退出后确认；它不冒称数据库内部物理提交完成的精确采样时刻。四新表系统时间一致且首次结果稳定，回放不续期。待提交回执先完成typed校验/精确序列化校验，不能提交后才发现必填字段缺失。

commit开始后抛错／连接中断按 integration_commit_unknown 503，不能同请求盲重执行业务；重发原身份/内容恢复。commit前失败回滚；已提交但响应/日志失败也保留原身份恢复。IntegrationRoute 继续覆盖完整yield依赖退出，不因使用response_model跳过保护。日志不得使未提交操作获得成功；没有202／内存任务ACK。

新表必要sourceRefs/mapping/result永久持有，业务实际值仍在8类既有业务表。raw/latest清理和事实证明有限保留不级联此4表，业务及最小回执无自动TTL。生产主记录可演进和人工规则继续有效；本轮仍不承诺每个被覆盖值有历史版本。

## r2.5 完整 provider 机器合同

### r2.5.1 发布面与 JSON number

实现后从正常模块注册后的应用生成并校验，仅提取8路与闭合引用集到 contracts/published/http-api/business-integration-v1/openapi.json；同目录 examples.json 保存下方r1八例、成功/错误例及已冻结摘要向量，README pair解释采用gate、错误/重试与兼容。contractVersion仍 aiis.business-integration/v1，digestProfile仍bi-json/v1；r2是任务Revision，不是新的wire版本。工件注明源码/生成命令/摘要，未开发前不预发布。

请求/响应 content-type 为 application/json；请求仍拒绝压缩/错误媒体，UTF-8严格解析、64KiB原始字节、深度12、sourceRefs1..128及所有A0规则不变。所有固定对象 additionalProperties=false；动态键不经全局camelize。path record_id 为正整数；八路 operationId稳定唯一且不含旧登录security，旧路由security声明不变。

数字 schema 统一：Decimal、FLOAT测量在JSON中为number，整数字段为integer，绝不 number|string/字符串数值。省略测量不进required，也不发布default:null；运行时显式null仍拒绝。只对非在产的coilNo允许null，并用状态分支表达in_production必须有coilNo、非在产不得携十三观测。字段precision/scale、上下界、单位、至少一观测、post-merge范围和FLOAT32容差在各owner schema/扩展profile与README成对说明；不能靠description让错误机器类型继续存在。JSON schema的number无需限制成浏览器IEEE754精度；客户端需精确Decimal读取。

请求日期schema接受 r1允许的显式offset/Z，标明非零亚毫秒拒绝与一次归一；新回执sourceTime/committedAt固定+08:00三位毫秒，sourceRefs原观察时间保留精度。sourceRefs为有kind判别的plc_fact/external_event有限oneOf，字段required/optional与r1一致；不顺带接收事实schema全部字段或新增未批准定义版本字段。

### r2.5.2 成功与错误 schema

200绑定8份owner receipt具体类型，外壳固定code=200、message=success、data为该路receipt，additionalProperties=false。r1 §9例中的所有receipt键均required；recordId/performanceId各为正integer或null；affectedRecordIds为正integer数组，changedFields为该资源已冻结字段别名enum数组；不能退回dict[str,Any]、空schema或可选data。动态规则同时由Service/DTO/探针验证：重放只变outcome；stale始终decision_only、applied=false、recordId=null、affectedRecordIds=[]；生产退出/unknown可recordId=null但业务提交确认不变。普通duplicate的applied保留首次事实，不伪造再次应用。

所有403/404/409/413/415/422/503/500均显式发布新局部错误壳：code为对应HTTP整数const，message与errorCode为相同稳定模块错误字串，data恒null，不附加未经批准的retryable/persistence字段。enum按模块与HTTP组合收窄为r1 §9表的后缀；404父错误仅三过程，409观察时间冲突仅生产观察。框架自动HTTPValidationError不得成为新8路422合同，旧路由错误合同保持。

例：父设备/卷冲突、提交未知；均为完整可解析JSON，不是成功ACK。

~~~json
{"code":409,"message":"performance.integration_parent_mismatch","data":null,"errorCode":"performance.integration_parent_mismatch"}
~~~

~~~json
{"code":503,"message":"equipment.integration_commit_unknown","data":null,"errorCode":"equipment.integration_commit_unknown"}
~~~

新旧producer/event同内容重放成功沿用r1完整receipt例，只有outcome=duplicate；originalOutcome/committedAt/目标及applied不变。父missing可保留原事件重试；commit_unknown/500/丢响应同身份核实；格式/冲突修复若改变冻结内容必须是新的逻辑事件并仍服从业务键，不能换ID掩盖冲突。客户端核对整个版本、摘要、目标和confirmation，再持久ACK；200本身不说明业务永久保存。

### r2.5.3 Core／模块／消费项目的升级边界

Core仅扩充三模块实际共用的明确时间转换、采用凭据解析/校验、typed response/OpenAPI原语；不接收表名/列名/SQL或客户状态机。17表列清单与旧wire view分别归owner integration_storage，模块公共符号只显式公开维护工具需要的固定profile。新符号必须同时登记module_contract.py、MODULE_CONTRACT双语与准入正负例，不能依赖私有helper穿透。

新增模块不被强制安装这八类字段或时间列清单；它选用有限信封/回执能力并自定typed data和业务规则。消费项目仍只承担源映射、单位/资格/唯一writer采用与客户规则，SMA的outbox和DAA上传不进入本次范围。新增兼容字段要说明缺测/摘要/重放；破坏性单位、键、状态机、时间或确认变更使用新wire主版本及精确spec，不在v1换义。发现不适配及时暂停受影响扩展并PM revision/Owner确认，不承诺覆盖所有项目或永久定型。

## r2.6 逐文件有限实施 allowlist（待 r2 批准）

只有下列路径，花括号严格展开所列集合。旧路径只允许本节用途的局部时间/边界适配，旧auth依赖、permission/grants、字段及外部行为保持；不授权整目录重构。需要其他文件时先交PM说明，不能先写后补。当前PM仍只写本spec。

| 精确路径／有限集合 | 允许用途 |
| --- | --- |
| backend/common/integration/{__init__,envelope,canonical,receipt,http,storage}.py | 保留A0规范向量/严格解析；新增纯时间与采用凭据原语、完整响应/schema适配。storage为新文件；无业务表清单/任意SQL。 |
| backend/app/{equipment,performance,monitor}/integration_{config,domain,error_codes,storage}.py | 本地准入、默认空凭据路径、固定列profile与legacy/new view；storage为新文件。 |
| backend/app/{equipment,performance,monitor}/{manifest.py,models/__init__.py,api/integration.py,schemas/integration.py,models/integration.py} | 真实async接线、八路typed provider、四Model/约束精确对齐，旧模块开关行为保持。 |
| backend/app/equipment/{services/async_integration.py,crud/async_integration.py} | 新温控/drive/参数事务与SQL。 |
| backend/app/performance/services/async_integration_{observation,process}.py；backend/app/performance/crud/async_integration.py | 新生产/过程事务与SQL、事件与父来源。 |
| backend/app/monitor/{services/async_integration.py,crud/async_integration.py} | 新曲线事务与SQL。 |
| backend/app/{equipment,performance,monitor}/crud/sync_integration.py | 新增3个owner-local同步只读采用探针，供旧Projection及显式export后的维护CLI；与各已有async_integration.py的async探针分离，纯helper无SQL，不自建/提交会话。 |
| backend/app/equipment/services/{async_temperature_sample,async_drive_sample,async_production_parameter_sample,async_temperature_dashboard,async_equipment,sync_drive,sync_production_parameters,_sync_common}.py | 既有HTTP／展示及legacy实际时间边界；_sync_common新增显式采用分支，sync_temperature原路径不得被连带转换。 |
| backend/app/equipment/crud/{async_temperature_sample,async_drive_sample,async_production_parameter_sample,async_mapping_ingest,async_equipment,sync_drive,sync_production_parameters}.py；backend/app/equipment/api/routes.py | 对既定列的SQL键／日范围／显式系统时间与只读兼容输出；不改路由认证、配置、mock业务或legacy温控。 |
| backend/app/performance/services/{async_production_observation,async_process_sample,async_mapping_query,async_performance,async_lineage,async_split,sync_production_record,_sync_process_common}.py | 原HTTP和人工pair/weight、旧Projection生产/过程时间边界，nested主行只读输出；谱系/split自有审计/业务不变。 |
| backend/app/performance/services/sync_process_{temperature,tension,speed}.py；backend/app/performance/crud/{async_production_observation,async_process_sample,async_mapping_ingest,async_performance,_sync_process_common,sync_production_record,sync_process_temperature,sync_process_tension,sync_process_speed}.py | 固定列SQL键、系统时间与父域；保持Projection游标/审计同事务和原返回形状。 |
| backend/app/performance/api/{routes,lineage_routes,split_routes}.py | 如需要，仅在原DTO构造处用只读兼容view；不改变endpoint、schema字段、认证依赖或授权。 |
| backend/app/monitor/services/{async_process_curve_sample,async_temperature,sync_process_curve}.py；backend/app/monitor/crud/{async_process_curve_sample,async_mapping_ingest,async_temperature,sync_process_curve}.py | HTTP/legacy曲线时间键、既有日筛选兼容与显式系统时间；无能耗/raw/latest改动。 |
| backend/alembic/versions/20261104_1400_1b3d5f7a9c20_add_business_integration_receipts.py | 唯一后继4表DDL；只创建本4表/索引/FK/CHECK，不改旧表或运行数据转换。含数据时破坏性downgrade拒绝。 |
| backend/scripts/business_time_adoption/{main.py,.env.example,README.md,README.zh-CN.md} | 有限inspect/plan/verify只读工具，枚举equipment/performance/monitor固定列；裸入口只help，不读默认env/连接目标。仅显式目标操作可连库，默认不执行；输出脱敏JSONL及显式指定文件候选报告，无apply/SQL代理。工具环境仅占位且独立于真实backend env。 |
| backend/scripts/{README.md,README.zh-CN.md} | 只加上述只读工具入口和未授权运行说明。 |
| backend/app/module_contract.py；backend/app/MODULE_CONTRACT{,.zh-CN}.md；backend/tests/test_module_contract.py | 新实际公开符号与模块维护profile导出及准入例；BE009不写common/integration。 |
| backend/.env{,.docker.dev,.docker.prod}.example | 仅追加上述3个空采用路径；既有84项及BE009并行增量原文不覆盖，profile计数按任务来源拆分。 |
| backend/tests/test_business_integration_{contract,api,service,migration,compatibility,storage,provider}.py；backend/tests/test_business_time_adoption.py | A无DB／严格JSON／关闭态／适配／机器schema／有限CLI；新增3个storage/provider/adoption测试文件。 |
| backend/tests_mysql/{test_business_integration.py,test_business_time_adoption.py} | 完整新业务B与真实MySQL合成旧行时间采用证据；源可先写，执行另批目标。 |
| backend/tests/module_admission_fixtures.py；backend/tests/{test_mapping_compatibility,test_equipment_temperature_config,test_equipment_temperature_migration}.py | 新r2/71/75阶段profile；保留C2/E/F/BE003/BE006/A0冻结历史。仅把当前profile新增键/后继与历史固定断言明确分组，不删除旧断言或伪称旧失败已修。 |
| contracts/published/http-api/business-integration-v1/{openapi.json,examples.json,README.md,README.zh-CN.md}；contracts/README{,.zh-CN}.md | 闭合8路provider与示例/向量；共享索引在BE009后做最小新增，非本PM产物。 |
| backend/README{,.zh-CN}.md；backend/app/README{,.zh-CN}.md；backend/app/equipment/README{,.zh-CN}.md；backend/app/monitor/README{,.zh-CN}.md；CODE_INDEX.md | 仅真实稳定合同/结构索引、关闭态和采用限制。performance无既有README时不借本轮新建治理pair。 |
| 本bundle spec.md/tasks.md/checklist.md | 各角色仅写所属面：PM本spec；获批后Development记录r2并保留r1；fresh Verification独立更新checklist。根/backend PLAN和根plans catalog六索引只由coordinator做状态增量。 |

明确排除：真实env／依赖锁／数据库全局时区／Base/session／旧migration／旧auth schema与权限／所有前端与C#／BE009实现／facts原始数据清理／DAA/SMA代码和联调／PLC与旧CA运行／Celery Redis／客户规则／通用治理平台／writer lease管理API／任意SQL与匿名CRUD／原业务表复制／原始历史转换apply程序。读取真实库、任何SQLite/Alembic运行、Docker、监听/HTTP、Git写与发布仍需另批，本轮PM全部不执行。

## r2.7 阶段、验收矩阵与 Owner 决定

| Gate | 继续条件与精确产物 | 不代表什么 |
| --- | --- | --- |
| 当前 PM draft | 只改spec、保留r1、文档/示例自检和BE009协调；交一次r2具体范围批准。 | 不批准r2实现，不提前创建Development/QA记录。 |
| r2源码 A | Owner精确批准本Revision后：先时间纯adapter／拒绝与provider，再A1→A2→A3；4表迁移源码可在BE009前驱冻结后完成；只读维护工具源码/无副作用验证。新入口持续unadopted关闭。 | 不解除真实G-T；不承诺真实业务已保存。 |
| 时间专项与采用 | Owner另批隔离或真实目标的调查、独立data-only转换范围/命令和验证，证据满足r2.3，再明确批准该目标adopted凭据和唯一writer。 | 不是默认所有环境已采用；不是匿名身份认证。 |
| 完整 B | A完成后另批可丢弃MySQL8.4.6的schema/账号/端口/卷/迁移/故障/并发/清理；先BE0097表再本4表，合成旧行可独立走采用夹具。 | 不用SQLite/替身替代；不以前置生产迁移造成循环；不证明生产历史。 |
| 独立 QA / Owner | fresh-context Verification消费同一交付源码、A与获批B，分别给阶段结论；Owner最终接受单独记录。 | A0 QA2/r2源码通过不等于整体qa_passed、Owner接受或发布/部署。 |

r1 AC01–AC12保留；本Revision将AC08的“真实G-T前不做业务源码”改为“源码可关闭态实现、实际写入前目标G-T满足”，并增加以下可核对标准。适用A/B列不能互相替代。

| AC增量 | A：无DB源码验证 | B／目标采用：另批实证 |
| --- | --- | --- |
| R2-AC01 8路provider | 正常注册应用的8个request/typed200/所有错误schema与运行JSON一一一致；只允许number/integer、不发布string/null缺测；JSON示例、闭合refs、数字规范向量和旧8路wire保护。 | 每路按真实typed响应确认实际列/值/receipt，而非请求回显或空200。 |
| R2-AC02 未采用保护 | 各模块unadopted新入口403/503且无业务读写/采用探针；旧API/Projection与基线走原时间路径。缺文件/错profile/伪revision/目标不符均不能ready；async/sync CRUD探针仅用传入会话，纯helper无IO且新事务不得复用旧探针。 | adopted凭据须匹配真实UUID/schema/revision/DB时钟；不合格采用无业务变更；探针当前读不制造RR旧快照或改变Projection事务边界。 |
| R2-AC03 时间同瞬间 | 13表41列profile精确，4新表16列无自动UTC默认；显式basisProfile固定键/enum及owner分组可核对，缺失/未知/同组混合无来源判别拒绝；旧UTC key/wire/fingerprint/JSON result不换义；offset/跨午夜/毫秒/秒列/已知naive基准/DATE/人工pair与0覆盖纯adapter。 | 合成UTC/上海/其他已知offset/unknown混合来源；完整列调查/转换后不混存，ID/unique/FK/原值及旧摘要不变；无法按来源恢复旧wire或未知未处置即拒绝采用；不同宿主/session TZ结果一致。 |
| R2-AC04 8类业务 | A1–A3 Service/CRUD替身证明调用/事务顺序、所有r1写入裁定、父来源及receipt恢复，无sync/假actor；每一类完整字段及0/省略存在集参与。 | 逐类真实读回；温控/曲线不可变，drive/参数/3过程补NULL原子冲突；生产生命周期/前卷/零活跃水位/晚到/stale/父ACK恢复/人工0与pair，非仅happy path。 |
| R2-AC05 并发与故障 | 命名unique仅有限恢复≤3次，rollback/current-read/冲突优先；提交前typed结果校验；完整依赖退出无提前成功；DEBUG脱敏。 | 独立Session同/异身份与同/异业务内容首竞争、RR旧快照/首水位、人工0两顺序、flush/commit/断线/提交后丢响应；业务/事件/水位/receipt无部分提交，unknown按原事件恢复。 |
| R2-AC06 schema分阶段 | 原6迁移字节不变；精确down链；BE009时71表+pending4，BE010后75；静态DDL/Model/FK/CHECK/索引与命名一致，无create_all。 | 空库及合成旧64表行按两后继升级，保留所有旧表/行；各阶段精确表差；非空新表破坏downgrade拒绝；不能全metadata建库掩盖pending4。 |
| R2-AC07 保留及隔离 | Core公开符号/维护profile有准入保护，模块字段不进Core；raw无FK；最小业务回执无TTL；事实/业务provider版本独立。 | 三自然月事实清理夹具后实际业务值、来源/映射与最小ACK/父子可恢复；生产可变值不假称版本历史；未完成outbox不级联。 |
| R2-AC08 旧行为与交接 | 旧认证/JWT/admin/permission/scope、模块disabled404、旧错误壳、Projection registry/事务/cursor/audit保持；旧冻结profile与当前profile分组，差异和限制准确。 | 带合成旧receipt/水位/人工pair/0/legacy来源跨日期；重放原actor请求、旧GET筛选/输出和旧Projection实际结果兼容。fresh QA及Owner分别登记，未授权测试明确列出。 |

适用skills：PM继续project-governance、aiis；Development/Verification使用backend-arch（RESPONSE_CONTRACT、LAYERS、DATABASE_AND_MIGRATIONS、AUTH_SECURITY、MODULE_REGISTRATION、OPERATIONS_TESTING），只读维护工具另用backend-script-tooling，实际结构索引用code-document-indexer。B若需Docker再加载专项且先获目标授权。没有因此扩大到Celery、UI、Rust或shared skill升级。

Owner 本次具体待决定为：**是否批准 r2 的关闭态源码范围、T1局部adapter/固定列边界、采用凭据及 BE009→BE010 接链**。推荐批准该有界源码范围；时间调查／真实转换／采用／完整B随后依据目标一次性提出具体操作审批，不要求逐接口确认。真实历史unknown或列集外依赖是采用 blocker，不能把它藏在“已就绪”状态里；源码阶段允许完成并如实以 source_ready_unadopted 交接。

| 历史／当前事实 | 状态 |
| --- | --- |
| r1 原draft e144d236d82b67a7269f3c32250b96fb3b62561c1950d97788226dcec0ba4020 | Owner实际批准T1且仅A0，原话与收据保留于下方。 |
| r1批准登记后 spec c33cd260dc74542f36436f31738e823734ae4bc75cf087a0dbb76c2d4c3dcaf9 | A0 Developer handoff / QA2通过；Owner A0接受、T1提案确认、最终接受未发生。 |
| r2本次 | draft；仅PM规格整理授权。实现、真实G-T、DB/Docker/B与发布未批准。 |

### r2 精确批准收据与当前交接（2026-11-04）

Human Owner 明确原话：

> 批准 ARCH-BE-009 r1 和 ARCH-BE-010 r2，按 STD 进入 A 源码阶段开发。数据库、Docker 和实际数据迁移先不执行，等源码检查通过后再确认；DAA 暂不改动。

本次登记其中 ARCH-BE-010 r2 的精确范围批准；批准输入 SHA-256 为 `4e5b0c56b1aac066458c1f24a5037bbab53c18946cd70fd79d8ab747a9342b6e`。本次只更新顶部 Status/Handoff 并追加真实批准收据，不改变 Revision、范围、allowlist、验收或风险。上文 draft／待批准／未批准实现的措辞保留为起草时历史，当前授权以顶部元数据、本收据及 Owner 明确阶段限制为准。

当前仅授权 r2.7 的 A源码阶段，Development 按 STD 接续并保留 r1 A0 历史；实际 G-T采用、数据库（含SQLite）、任何Docker操作、B验证、迁移执行／真实数据转换、DAA改动、实际联调及发布部署均未授权，源码检查后再提交具体操作确认。本次不是 A0或整体的 Human Owner 最终验收，也不预记 r2 Development／独立QA已完成。PM仅登记本spec，其他角色文档由对应角色后续据实更新。

## r1 原文保留区（历史授权及关键合同，不作为 r2 已批准证据）

<!-- 下方从Task ID起的UTF-8字节为批准登记后的r1完整原文；其旧当前态措辞按r2.1解释。 -->

Task ID: ARCH-BE-010
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 ARCH-BE-010 r1，选择 T1；PM -> Development 按 STD 仅实施 A0，时区兼容与迁移方案先在 tasks 中整理待 Owner 确认；G-T、业务写入接通、精确迁移接链及数据库/Docker/B操作仍未批准
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 现有八类业务的独立匿名集成入口、可靠业务回执及可复用接口接入规范
Owner: Backend Core 与 equipment、performance、monitor 公共业务模块
Acceptance Chain Reference: 本 spec 第12节；PM -> Human Owner 精确范围批准 -> Development -> fresh-context Verification -> Human Owner 最终验收
Depends On: 既有 Python Backend 模块 v1 合同及 ARCH-BE-003 r3、ARCH-BE-006 r1 源码；业务表写入采用另受第3节时间 gate 约束
Related Task: ARCH-AW-008, ARCH-BE-003, ARCH-BE-006, ARCH-BE-007, ARCH-BE-008
Created: 2026-11-04

# 后端业务匿名集成入口与新增接口规范

## 1. 目标、当前授权与源码依据

本任务把现有八类业务能力整理成独立匿名集成合同，供 SMA 或第三方提交已经完成映射的业务数据；同时提炼以后新增接口可复用的有限规范，减少每个项目复制响应、解析、防重和事务处理的成本。业务字段仍归相应模块，客户映射和工艺规则归消费项目，不承诺一套字段覆盖所有工业项目。

Human Owner 要求按 STD 先出 spec，覆盖八类能力，对齐 ARCH-AW-008，明确 JSON、写入规则、幂等、可靠回执和业务永久保存，保持现有前端认证接口，确认后再开发。本轮只新增本 spec；不创建 tasks/checklist，不改代码、测试、schema、配置或已有数据。主协调者仅机械同步根/backend PLAN 双语与根 plans catalog 双语六处索引。

2026-11-04 已只读核对根/最近作用域治理、canonical workflow、实际 PM 配置、完整 BE003/BE006 bundle、AW008 当前形成的 bundle，以及八路 router/schema/Service/CRUD/Model/manifest。结论如下；均不是本任务运行验证。

| 依据 | 当前事实与本任务差额 |
| --- | --- |
| [BE003](../ARCH-BE-003-mapping-service-api-pilot/spec.md)、[独立结论](../ARCH-BE-003-mapping-service-api-pilot/checklist.md) | 完整十值温控已实现，独立 A/B 为 qa_passed，Owner 最终验收 pending；业务按设备+UTC毫秒不可变，回执按 actor_user_id/设备/sampleId。 |
| [BE006](../ARCH-BE-006-mapping-business-api-expansion/spec.md)、[独立结论](../ARCH-BE-006-mapping-business-api-expansion/checklist.md) | 其余七类 POST、指定 GET 与页面来源选择已实现并 qa_passed，Owner 最终验收 pending。存在补 NULL、生产水位/生命周期和父子规则，不能统一成任意 upsert。四项冻结 profile 失败历史仍保留，不能称默认全套全绿。 |
| [温控路由](../../backend/app/equipment/api/temperature_samples.py)、[设备映射路由](../../backend/app/equipment/api/mapping_samples.py)、[生产观察](../../backend/app/performance/api/mapping_observations.py)、[三过程路由](../../backend/app/performance/api/process_samples.py)、[曲线路由](../../backend/app/monitor/api/process_curve_samples.py) | POST 要求 active admin、JWT、独立 ingest permission 及模块单设备 scope；匿名不能通过去 guard 或伪造 admin 复用这些入口。 |
| [设备规则](../../backend/app/equipment/mapping_domain.py)、[实绩规则](../../backend/app/performance/mapping_domain.py)、[曲线规则](../../backend/app/monitor/mapping_domain.py)、[温控 Model](../../backend/app/equipment/models/temperature_sample.py) | HTTP 来源时间归一 UTC，MySQL DATETIME(3) 保存无 offset UTC；部分系统时间用 UTC_TIMESTAMP(3)，其他 legacy 时间采用 now()/旧含义。根 AGENTS 后续要求上海存储，存在真实不适配。 |
| [模块合同](../../backend/app/MODULE_CONTRACT.md)、[共享响应](../../backend/common/response.py)、[异步会话](../../backend/database/session_async.py) | 公开符号限制跨模块依赖；共享响应递归转换字典键；get_db 退出仍可能 commit/rollback/close。有限公共原语须正式导出，成功响应须覆盖完整依赖退出。 |
| [AW008 r1](../ARCH-AW-008-stage-c-facts-contract/spec.md) | r1 已获文档范围批准，文档 Development 正进行；事实服务、DAA/SMA 软件未因此完成。其 R12/R13 要求独立业务 typed data、producer/event、两段确认和业务独立值。当前共同需求 demand-r1 为 proposed，不是已发布 provider 实现合同。 |

ARCH-BE-010 起草前未发现同 ID bundle；ARCH-BE-009 在 AW008 中仅暂拟用于事实服务，本任务不占用它。无 Parent Task ID，不继承其他任务批准、运行动作或最终验收。

## 2. R01：三层复用与新增接口流程

| 层 | 本轮建议形成的能力 | 不放入这一层的内容 |
| --- | --- | --- |
| 公共 Core | 现有模块接入、共享响应/异常、async 事务边界；新增有限 integration 原语：严格 JSON 解析、版本化信封、规范化摘要、回执输出、局部 HTTP 适配。公共原语只有本任务三模块实际共用的部分。 | 八类业务字段、工艺状态、模块错误枚举、任意表名/列名/SQL、客户映射、通用工作流或事件总线。 |
| 可复用业务模块 | equipment/performance/monitor 拥有 typed Schema、业务键、补缺/不可变/生命周期、Model/CRUD/Service、模块回执与错误。优先复用现有八类业务表和纯领域规则。 | 将八类字段强制为所有项目必装标准；把业务规则搬入 Core；复制八套新的同义业务表作为默认方案。 |
| 消费项目 | 点位/外部字段到业务字段的映射、单位转换、设备编号、映射版本、部署采用和客户独有规则；SMA 的持久 outbox/重试由其自己的任务负责。 | 复制并随意修改 Core 响应/认证；直写业务 SQL；把客户规则提交到公开框架。 |

新增接口按以下顺序：明确业务 owner 与用例 -> 选择既有资源或新的 typed 资源 -> 写 spec 的字段/单位/缺测/写键/幂等/回执/保留/兼容矩阵 -> 精确批准 -> 模块实现和公开接入声明 -> 独立验证。纯新增可选字段也须说明省略、摘要和旧客户端行为，不能因它“可选”就改变已冻结事件的内容。

删除/改名字段、改变单位/类型/必填/自然键/覆盖/时间/确认含义属于破坏变更，使用新合同主版本及明确迁移；旧版本保留期间不可原地换义。发现来源无法提供完整温控、曲线只有小数温度、单位不适配、业务要求实时覆盖或新的状态机时，Development 停止受影响部分，交 PM 修订/Owner 确认；不靠补零、截断、万能 data 或附带配置偷偷扩范围。

本轮不升级 AIIS shared skill、模板或生成器。经过真实复用再另立沉淀任务；框架持续演进，不承诺一次定型。

## 3. R02：时区与来源采用 gate

**推荐复用业务表，但不能现在把 +08:00 墙上时间直接写进现有 UTC 列。** 以下选择随本 r1 提交 Owner 审阅；推荐 T1，不默认采用 T2。

| 选项 | 结果与代价 |
| --- | --- |
| T1：复用现有表，先完成有界时间整改/采用（推荐） | 新 integration API/新回执采用上海时间。已有 HTTP 数据和 legacy 时间先按实际来源分类；独立获批的时间整改范围负责存储、旧 writer、查询/筛选、旧读写 adapter 和必要历史迁移，证明旧 wire UTC 毫秒及业务行为兼容。避免复制业务表，但实际落库前有真实前置。 |
| T2：独立 integration 业务存储 | 可以避开同列时间混存，但须增加八类存储、读面、人工修正规则和维护成本；不在本 r1 默认范围。Owner 选择后由 PM 给出相应 Revision，不能由 Development 自行切换。 |

时间 gate G-T 的解除材料必须包含：精确批准的整改范围/源码与 schema 版本；逐字段原时区依据（未知保留未知，不盲加8）；新旧输入 -> 存储 -> 业务键/水位 -> 查询/自然日 -> API 输出的兼容证明；数据库时间源及毫秒精度；对原回执/fingerprint、生产人工起止/重量审计和旧 Projection 的影响；隔离验证与采用/回退记录。真实库调查、数据迁移和运行设置另需具体授权，本轮不探库。

G-T 未解除时，本 r1 获批后可以先做 A0 的纯解析/DTO/摘要/回执原语和默认关闭路由准备，不允许向共享业务表接通写入或以其替代 B 验证。新路由在未采用状态返回 503 `<module>.integration_not_ready`，不读取/修改业务对象；该 ready 声明只是配置与交付 gate，不是数据库整改已完成的证据。

不要求无条件再升 r2：本 r1 已准确冻结的 A0 和下文合同可在精确批准后实施。G-T 若改变本任务接口、依赖、migration 接链、allowlist、风险或验收，才先回 PM 新 Revision；若保持本合同，记录精确前置后继续原 Revision。G-T 是当前业务落库部分的技术 blocker，不能把本 draft 描述成已经可以直接上线。

来源采用另须确认：同一设备业务域的一条权威写入通道，现有 actor 回执与新 producer 回执分别保留；本期不做旧投递身份迁入、跨通道回执等价、历史归并或无缝 writer 切换。原认证 POST 与旧 Projection 的路径/授权继续保留，采用方不得让它们同时更新同一选定生产生命周期。这个约束是采用规则，不是匿名调用者的真实认证或平台强制互斥；已有设备切换须单独审查水位基线与未完成投递。

## 4. R03：精确八路新增入口与保护边界

所有路径均挂在现有 API_V1_PREFIX；下表公开前缀为 `/api/v1`。当前均为待实施合同。

| 资源 key | 新匿名 POST | 沿用业务语义 |
| --- | --- | --- |
| temperature | `/api/v1/integration/equipment/temperature-samples` | 完整五区十值、逐样本不可变。 |
| drive | `/api/v1/integration/equipment/drive-samples` | 二十指标的观测新增及只补 NULL。 |
| production_parameters | `/api/v1/integration/equipment/production-parameter-samples` | 设备+卷号+时刻，新增及只补 NULL。 |
| production_observation | `/api/v1/integration/performances/production-observations` | 有序生产生命周期、设备水位、人工优先。 |
| process_temperature | `/api/v1/integration/performances/{record_id}/process-temperature-samples` | 明确父实绩+zone+recordTime，新增及只补 NULL。 |
| process_tension | `/api/v1/integration/performances/{record_id}/process-tension-samples` | 同上父/zone/时刻和张力规则。 |
| process_speed | `/api/v1/integration/performances/{record_id}/process-speed-samples` | 同上父/zone/时刻和速度规则。 |
| process_curve | `/api/v1/integration/monitor/process-curve-samples` | 原三十三指标逐样本不可变历史。 |

新八路不要求登录、JWT、API Key 或角色，不按 User-Agent/前端来源/自称 SMA 动态绕过认证。现有八路 POST、所有展示/管理 GET、人工 PUT/DELETE、权限数组、模块开关、CA token 和旧 sync Projection 外部行为保持；不把它们改匿名，不创建机器 User，不给 actor_user_id 填 0/系统管理员，不扩大既有 read/ingest grants。

每模块新增本地 integration 配置：enabled 默认 false；设备 key 明确集合默认空（最多256个，精确且区分大小写）；允许的 producer 声明默认空；storageProfile 默认 unadopted。未启用/空 scope 拒绝，未完成 G-T 拒绝业务落库。设备资格来自部署审阅过的业务 key，不从 PLC IP/raw id 猜测；公开示例只使用合成值。此集合是数据准入范围，不构成设备所有权证明。

producerId、sourceRefs 和映射版本均是客户端声明。任何能访问匿名入口的人都可能冒用它们，并对准入设备提交业务数据；Owner 需接受当前匿名取舍。首期不附带身份平台、设备目录/授权 CRUD、网络部署或 rate-limit 平台。

## 5. R04：有限外层、严格解析与时间/数值

### 5.1 外层字段

每次只提交一个逻辑业务事件，不提供混合批量、任意 CRUD 或 SQL 代理。HTTP Content-Type 必须为 application/json；UTF-8 对象，不接受压缩请求。建议首版上限固定为64 KiB、嵌套深度12、sourceRefs最多128项，超限413；后续改变上限须更新合同/验证。

| 字段 | 合同 |
| --- | --- |
| contractVersion | 必填，精确 `aiis.business-integration/v1`；未知版本422，不猜测旧 schema。 |
| producerId / eventId | 必填精确标识，1–128字符，无控制字符、首尾空白，不 trim/casefold；eventId 在首次冻结前持久生成，网络重试/进程重启不变。 |
| mappingId / mappingRevision | 必填精确标识，同上范围；声明这次转换的稳定身份与版本，不用当前“最新配置”替代。第三方也声明自己的转换版本。 |
| sourceRefs | 必填非空数组；见下方两种有限类型。只保必要引用，不嵌入 raw 原文、PLC地址、SQL或任意嵌套对象。 |
| data | 必填对象，按目标资源选唯一 typed schema；不得由请求传入表名、handler import path 或任意列。 |

sourceRefs 的两种类型：`kind=plc_fact` 必填 instanceId/plcId/sampleId/pointId，已知 sourceGeneration/configRevision/observedAt 时必须随引用带上；`kind=external_event` 必填 sourceId/sourceEventId，已知 observedAt 时带上。标识规则同上，时间遵守5.2；缺少真实时间时省略，不编造。PLC pointId 原样保留，不把显示名或中文路径当程序执行。完全相同引用拒绝422；引用集合在摘要中按规范化内容排序，因此排列变化不产生新事件。

Backend 校验引用结构和业务对应，不要求 raw 仍存在，不追访 URL、不通过 raw 外键读取缺失业务值，也不声称验证了源设备真实性。SMA 必须列出实际用到的来源；十温度来自十点时，引用十点，不能只写其中一点冒充完整来源。

### 5.2 严格规则

- 所有静态字段只收 camelCase；重复 JSON key（包括嵌套）、未知字段、snake_case 替代、bool 当数值、数字字符串、NaN/Infinity、非法 UTF-8、不可表示 Decimal/极端指数或过深 JSON均拒绝。原文数字先按 Decimal 解析，不能先转 float 丢精度。格式错误422，无业务/成功回执。
- 0/-0 是真实零，不按 truthy 判缺测。除生产非在产 coilNo 的明确例外，显式 null 拒绝；可选指标省略表示未观测，新行实际保存 SQL NULL，补缺时不修改原值。
- sampledAt/recordTime 及可选业务时间必须有 offset，接入边界转换一次到 Asia/Shanghai；输出 `YYYY-MM-DDTHH:mm:ss.sss+08:00`，保存 MySQL DATETIME(3) 的上海墙上时间。允许带其他 offset 的同瞬间输入；非零亚毫秒尾数拒绝，不截断，上海归一后年份1000–9999。sourceRefs 的事实时间保留其原有必要精度，不能为业务毫秒键改写原始事实。
- 不用 HTTP 到达/刷新时间替代来源时间。sampledAt/recordTime 超过接收端数据库当前时间5分钟拒绝422；过去独立样本不受 raw 三月窗口限制，生产旧观察仍遵守水位。start/end 的业务次序和总秒数另按第7节判断。
- 系统 committedAt/createdAt/updatedAt 取已经确认上海时间的数据库时间源；不修改全局 engine/session offset，不散落 Python now() 或机械加8。共享外层 Unix timestamp 如保留，仍是 Unix 时间，不改成墙上时间。
- 摘要前将时间、数值规范化；1/1.0、0/-0、等价 offset 表示相等。字段存在集合参与业务比较，遗漏和零不同。普通文本保留原空格/Unicode，不暗中改写 key。
- sourceRefs、字段名清单等采用对象数组/字符串值，不引入按 pointId/样本ID为动态 key 的 map。新增公共 serializer 对显式数据 key 原样保护；不得使现有 serialize_api_data 的旧行为全局变化。

### 5.3 数值表示域（技术域，不是现场物理上限）

| 字段组 | 合同 |
| --- | --- |
| 完整温控十值 | 精确 NUMERIC(30,10)，abs < 10^20，最多10位有效小数；非整数 JSON number 往返十进制值不变，不能舍入。 |
| drive、生产参数数量、曲线21项 | 沿既有 FLOAT/binary32 测量语义：有限、abs ≤ 3.4028234663852886e38；单次规范为 binary32，非零不得下溢成0；相对误差≤1e-6、绝对误差≤max(1e-6,abs(input)×1e-6)。摘要与冲突用同一存储规范值。 |
| 主实绩 weight/outputQuantity/qualifiedQuantity | 非负 NUMERIC(10,4)：<10^6、最多4位小数。 |
| totalLength / diameter / density | 非负，分别 NUMERIC(10,2)/(8,2)/(5,3)：<10^8/<10^6/<10^2，最多2/2/3位小数。 |
| efficiencyRate / qualityScore | 非负 NUMERIC(5,2)：<10^3、最多2位小数；不擅加≤100阈值。 |
| 过程四温度；张力/速度 | 温度 NUMERIC(8,2)，abs<10^6；张力/速度非负 NUMERIC(10,2)，<10^8；最多2位小数。 |
| 曲线十二温度；过程 duration | 温度必须整数，-2147483648..2147483647；duration 是0..9999999999的整数分钟，非主实绩总用时。 |

所有 Decimal 超 scale/范围拒绝，不裁剪；FLOAT 仅按上述明确近似合同，不能声称逐位精确。采用前须确认 TV/KM、density、quantity、qualityScore 的实际量纲；源码未定义时明确“未定义”，不猜换算。

## 6. R05：八类 typed data 与可解析 JSON

下面八份均是完整请求对象、合成示例，不是现有认证路由可直接使用的 body，不是现场已发布合同。示例省略的可选字段按缺测处理。所有 set 值均为观测，不能下发设备命令。

### 6.1 完整温控

data 必填 equipmentId、sampledAt、quality=`good` 及 zone1Set/zone1Act 至 zone5Set/zone5Act 十个 °C 数值。十项必须完整；任一坏值/缺失/null，整次拒绝，不用旧成功值或0补齐。

```json
{
  "contractVersion": "aiis.business-integration/v1",
  "producerId": "sma-demo", "eventId": "temperature-001",
  "mappingId": "temperature-five-zones", "mappingRevision": "r3",
  "sourceRefs": [{"kind": "external_event", "sourceId": "demo-temperature-frame", "sourceEventId": "frame-001", "observedAt": "2026-11-04T10:00:00.123+08:00"}],
  "data": {
    "equipmentId": "line-demo", "sampledAt": "2026-11-04T10:00:00.123+08:00", "quality": "good",
    "zone1Set": 200, "zone1Act": 199.5, "zone2Set": 210, "zone2Act": 209.5,
    "zone3Set": 220, "zone3Act": 219.5, "zone4Set": 230, "zone4Act": 229.5,
    "zone5Set": 0, "zone5Act": 0
  }
}
```

### 6.2 传动

data 必填 equipmentId/sampledAt/quality=`good`；下列20项至少1项：tv/km（单位未定义）；dewPointSet/dewPointActual（°C）；oxygen（ppm）；mufflePressure（Pa）；nh3FlowSet/nh3FlowActual/ngFlowSet/ngFlowActual（m³/h）；uncoilerSet/uncoilerActual/entryLooperSet/entryLooperActual/furnaceSet/furnaceActual/exitLooperSet/exitLooperActual/recoilerSet/recoilerActual（kN）。不擅加原合同没有的客户物理阈值。

```json
{
  "contractVersion": "aiis.business-integration/v1",
  "producerId": "sma-demo", "eventId": "drive-001", "mappingId": "drive-observation", "mappingRevision": "r2",
  "sourceRefs": [{"kind": "plc_fact", "instanceId": "daa-demo", "plcId": "plc-demo", "sampleId": "sample-142", "pointId": "tv", "sourceGeneration": "generation-a", "configRevision": "config-3", "observedAt": "2026-11-04T10:00:00.123+08:00"}],
  "data": {"equipmentId": "line-demo", "sampledAt": "2026-11-04T10:00:00.123+08:00", "quality": "good", "tv": 0}
}
```

### 6.3 生产参数

data 必填 equipmentId/sampledAt/quality=`good`/coilNo（精确1–50字符）；grade（非空白1–50）、entryTime、thickness/width（mm）、totalTime（分钟）、weight（吨）、speed（m/min）七项至少1项。五个数量非负。processSteps/status/id/lastUpdate 禁止输入，新增 process_steps=[]，不生成工序。

```json
{
  "contractVersion": "aiis.business-integration/v1",
  "producerId": "sma-demo", "eventId": "parameters-001", "mappingId": "coil-parameters", "mappingRevision": "r1",
  "sourceRefs": [{"kind": "external_event", "sourceId": "demo-coil-frame", "sourceEventId": "frame-002"}],
  "data": {"equipmentId": "line-demo", "sampledAt": "2026-11-04T10:01:00.123+08:00", "quality": "good", "coilNo": "COIL-DEMO-01", "grade": "DEMO", "entryTime": "2026-11-04T10:00:00.000+08:00", "thickness": 0.8, "width": 1200, "totalTime": 1, "weight": 0, "speed": 60}
}
```

### 6.4 生产观察

data 必填 equipmentId/sampledAt/quality=`good`/observationStatus。状态为 in_production/not_in_production/unknown；在产须精确 coilNo（1–50），十三项观测可选：grade（1–20）、weight（吨）、totalLength（米）、diameter（mm）、density（量纲未定义）、spec（1–50）、startTime/endTime、outputQuantity/qualifiedQuantity（量纲未定义）、efficiencyRate（沿百分比展示）、qualityScore（量纲未定义）、remark（1–500）。文本提供时非空白。

非在产状态 coilNo 只能省略或 null，禁止携带十三项字段；字符串 `"0"` 是在产卷号，不等于停产。生产日期取来源时刻上海日期。

```json
{
  "contractVersion": "aiis.business-integration/v1",
  "producerId": "sma-demo", "eventId": "production-start-001", "mappingId": "production-lifecycle", "mappingRevision": "r4",
  "sourceRefs": [{"kind": "external_event", "sourceId": "demo-production-frame", "sourceEventId": "frame-003"}],
  "data": {"equipmentId": "line-demo", "sampledAt": "2026-11-04T10:02:00.123+08:00", "quality": "good", "observationStatus": "in_production", "coilNo": "COIL-DEMO-01", "grade": "DEMO", "weight": 1.25, "totalLength": 100, "diameter": 500, "density": 7.85, "spec": "0.8x1200", "startTime": "2026-11-04T10:00:00.000+08:00", "endTime": "2026-11-04T10:02:00.000+08:00", "outputQuantity": 1, "qualifiedQuantity": 1, "efficiencyRate": 95, "qualityScore": 98, "remark": "demo observation"}
}
```

### 6.5–6.7 三类过程

共同 data 必填 equipmentId/recordTime/quality=`good`/coilNo/zone；coilNo/zone 精确1–50字符。路径正整数 record_id 必须来自同设备在产生产观察的可靠回执；下例假定该回执返回 recordId=101，不表示真实库存在101。不得用列表最大ID、猜号、raw id 或人工/legacy父代替。父回执丢失先按原事件重放恢复；调用方持久保存父id后才创建子事件，父id 纳入请求摘要。

温度 setTemp/maxTemp/minTemp/avgTemp（°C）/duration（工艺段整数分钟）至少1项；张力 setTension/avgTension/maxTension/minTension（kN）至少1项；速度 setSpeed/avgSpeed/maxSpeed（m/min）至少1项。min/avg/max 同时存在的两两顺序必须成立，速度 avg≤max；补缺后完整行也须满足，不能两次合法 patch 拼成非法范围。

POST `/api/v1/integration/performances/101/process-temperature-samples`：

```json
{
  "contractVersion": "aiis.business-integration/v1",
  "producerId": "sma-demo", "eventId": "process-temperature-001", "mappingId": "process-temperature", "mappingRevision": "r1",
  "sourceRefs": [{"kind": "external_event", "sourceId": "demo-process-frame", "sourceEventId": "frame-004"}],
  "data": {"equipmentId": "line-demo", "recordTime": "2026-11-04T10:03:00.123+08:00", "quality": "good", "coilNo": "COIL-DEMO-01", "zone": "zone-1", "setTemp": 200, "minTemp": 198, "avgTemp": 199, "maxTemp": 201, "duration": 0}
}
```

POST `/api/v1/integration/performances/101/process-tension-samples`：

```json
{
  "contractVersion": "aiis.business-integration/v1",
  "producerId": "sma-demo", "eventId": "process-tension-001", "mappingId": "process-tension", "mappingRevision": "r1",
  "sourceRefs": [{"kind": "external_event", "sourceId": "demo-process-frame", "sourceEventId": "frame-005"}],
  "data": {"equipmentId": "line-demo", "recordTime": "2026-11-04T10:03:00.123+08:00", "quality": "good", "coilNo": "COIL-DEMO-01", "zone": "zone-1", "setTension": 2, "minTension": 0, "avgTension": 1, "maxTension": 2}
}
```

POST `/api/v1/integration/performances/101/process-speed-samples`：

```json
{
  "contractVersion": "aiis.business-integration/v1",
  "producerId": "sma-demo", "eventId": "process-speed-001", "mappingId": "process-speed", "mappingRevision": "r1",
  "sourceRefs": [{"kind": "external_event", "sourceId": "demo-process-frame", "sourceEventId": "frame-006"}],
  "data": {"equipmentId": "line-demo", "recordTime": "2026-11-04T10:03:00.123+08:00", "quality": "good", "coilNo": "COIL-DEMO-01", "zone": "zone-1", "setSpeed": 60, "avgSpeed": 0, "maxSpeed": 60}
}
```

### 6.8 过程曲线

data 必填 equipmentId/sampledAt/quality=`good`，可选 coilNumber（1–50）；33项测量至少1项。十二整数 °C 温度为 z1TempSet/z1TempAct 至 z6TempSet/z6TempAct；其他21项的单位和完整字段在下例中逐项列出：lineSpeed* 为m/min，unc/rec *TensionP 为%，四个 *TensionKg 沿旧标签kg（不换成kN），coolFan* 为Hz，n2Total为累计m³，electConsum为累计kWh，h2Flow/n2Flow为m³/h，oxygenContent为ppm，dewPoint为°C，mufflePressure为Pa。累计量只是样本观测，不计算差分/重置/财务能耗，不写能耗汇总或自动创建父实绩。

```json
{
  "contractVersion": "aiis.business-integration/v1",
  "producerId": "sma-demo", "eventId": "curve-001", "mappingId": "process-curve", "mappingRevision": "r2",
  "sourceRefs": [{"kind": "external_event", "sourceId": "demo-curve-frame", "sourceEventId": "frame-007"}],
  "data": {
    "equipmentId": "line-demo", "sampledAt": "2026-11-04T10:04:00.123+08:00", "quality": "good", "coilNumber": "COIL-DEMO-01",
    "z1TempSet": 200, "z1TempAct": 199, "z2TempSet": 210, "z2TempAct": 209,
    "z3TempSet": 220, "z3TempAct": 219, "z4TempSet": 230, "z4TempAct": 229,
    "z5TempSet": 240, "z5TempAct": 239, "z6TempSet": 0, "z6TempAct": 0,
    "lineSpeedSet": 60, "lineSpeedAct": 59.5,
    "uncSetTensionP": 10, "uncActTensionP": 9.5, "recSetTensionP": 11, "recActTensionP": 10.5,
    "uncSetTensionKg": 100, "recSetTensionKg": 110, "furnSetTensionKg": 120, "furnActTensionKg": 119,
    "coolFan1SetFre": 30, "coolFan1ActFre": 29.5, "coolFan2SetFre": 31, "coolFan2ActFre": 30.5,
    "n2Total": 1000, "electConsum": 2000, "h2Flow": 3, "n2Flow": 4,
    "oxygenContent": 5, "dewPoint": -20, "mufflePressure": 0
  }
}
```

## 7. R06：业务键、写入、生产生命周期与父子

| 能力 | 自然键与写入裁定 |
| --- | --- |
| 温控 | equipmentId+规范来源毫秒；完整内容相同复用原行，异值409；不同瞬间分别保存，晚到不覆盖最新来源。 |
| drive | equipmentId+来源毫秒；新行缺测为NULL；同键仅补NULL，已有同值可重复，任一已有异值整次409，无部分补缺。 |
| 生产参数 | equipmentId+精确coilNo+来源毫秒；同上补缺规则；不按小时合并不同卷。 |
| 生产观察 | 聚合根为equipmentId+精确coilNo；设备水位按来源毫秒串行裁定，事件键equipmentId+来源毫秒。相同时刻不同状态/卷/存在字段/值409；已成功旧事件仍可恢复原结果；尚未应用的旧观察为stale，不倒退水位。 |
| 三过程 | equipmentId+父record_id+精确zone+recordTime；新行/补NULL/同值duplicate/异值409。父缺失404，无成功回执，可按原eventId重试；设备/卷不匹配409。不自动造父，不因子记录重激活已结束父，不把duration写主用时。 |
| 曲线 | equipmentId+来源毫秒；含coilNumber/字段存在集合的完整内容不可变；新事件同键同内容复用原行，异内容409。不把缺失测量追加成同刻patch。 |

生产观察 in_production：不存在该卷则新增，plan_id=NULL、parent_coil_no=coilNo、record_source=external_observation，不填假PLC审计；已有卷可更新明确提供的十三字段，省略保留，退出卷可重激活；同设备前一活跃卷退出。not_in_production/unknown 只改变该设备活跃记录，零活跃时仍保存水位，不制造空卷。主行、前卷、设备水位、业务事件索引及回执同事务。

HTTP weight 只更新 collected_weight；manual_override_weight 非NULL时（包括0）保持人工 effective/weight/source/审计优先。人工修改继续既有受保护模块入口。生产人工起止有效 pair 优先，其次完整 reported_start/end，再次 first/last observed，否则用时NULL；总秒数0..2147483647，负范围422。过程duration单位分钟与该总秒数分开。匿名接口不提供清除人工覆盖、人工删除、Plan关联、split/merge或下推。

本版没有“任意实时覆盖”接口。未来 current-state/upsert 是独立用例和版本，不能把历史采样路径原地改成最后到达者覆盖。

## 8. R07：两层摘要、投递幂等与事务

### 8.1 身份及摘要

新投递唯一身份为 `(module, producerId, eventId)`；module由路由确定，同模块内改资源/设备/父id仍是同eventId异内容，不靠换路由逃避冲突。数据库精确比较，不受默认大小写/尾空格排序影响。producer是声明身份，不是 User；actor回执不迁入、不共用该唯一键。

新 body 不再重复 sampleId：旧业务接口的 sampleId 是其 actor 投递标识；本通道由 eventId 承担该责任。DAA sampleId 只在 sourceRefs 指原始事实。一次输入可派生多个目标事件；每个目标首次冻结自己的eventId，重试不变，不能每次轮询重造ID。

区分两种 SHA-256 摘要：

1. requestDigest 覆盖 contractVersion、路由资源/父id、producerId/eventId、mappingId/revision、sourceRefs集合及完整typed data/存在集合；用于冻结请求确认。同身份改来源或映射版本也409。
2. businessDigest 只比较资源/父id及规范业务data/存在集合，排除 producer/event/mapping/sourceRefs/接收时刻；不同映射来源可以证明相同业务内容，不能把元数据差异误判成温控异值。生产历史事件按业务摘要判断，不查actor回执冒充匿名事件索引。

规范化 profile 固定为 `bi-json/v1`：验证后使用精确 camelCase 字段；对象键按UTF-8字节升序；引用数组按其规范化JSON字节升序；标识/文本原样UTF-8；时间统一上述上海表示；Decimal去无效尾零、无指数、零统一0；FLOAT先binary32再用该值的精确十进制规范值；JSON无额外空白，无ASCII转义强制。摘要值编码为 `sha256:` 加64位小写hex；请求不含客户端自报摘要，避免自引用。Development须在实现前于tasks固定正反测试向量与精确数字输出，验证不同语言调用方可复现，不依赖未经说明的默认float打印。

### 8.2 结果矩阵与并发

| 情况 | 裁定 |
| --- | --- |
| 同投递身份同requestDigest | 重放稳定原recordId/父id/结果，不重新补缺或推进生命周期；响应outcome=duplicate，originalOutcome保持首次值。 |
| 同投递身份异requestDigest | 409 `<module>.integration_event_conflict`，优先于业务键冲突；不覆盖旧回执/业务。 |
| 新投递、同业务键同内容 | 按第7节返回duplicate并提交该新投递回执及必要来源；不增加业务行。 |
| 新投递、补缺或更新生命周期 | 按第7节一次原子提交，created/updated；并非通用覆盖许可。 |
| 新投递、业务键异内容 | 409 `<module>.integration_value_conflict` 或 production 的 `integration_observation_time_conflict`；不留成功回执。 |
| 新的旧生产观察且无历史成功事件 | 持久裁定stale，applied=false、decision_only；不能假称其值已永久写入业务。已有成功旧事件须先判重/冲突，不能被当前高水位直接吞为stale。 |

每请求独立AsyncSession；数据库业务unique、投递unique及生产事件unique是最终并发裁决，不靠先查后插或只锁已存在行。锁顺序/新事务可见性必须有界：仅本任务真实命名unique竞争允许恢复；其他Integrity不是duplicate。参考既有真实发现，覆盖 RR旧快照、锁等待后的投递冲突优先级、current-read refresh、设备水位首次竞争、人工0两提交顺序；不改全局隔离级别。

真实 async API -> Service -> CRUD；CRUD只select/add/flush，Service拥有一次业务事务的commit/rollback。不调用旧sync Service、不在Projection内回调HTTP。业务insert/update、source/mapping追溯、事件索引、水位及成功回执必须同库同事务；不能业务先commit再单独补回执。

提交成功后且完整可失败依赖退出结束，才发送成功。提交前失败回滚且无成功回执；commit结果未知/断线为503，不假称未提交，不在同请求盲目重做。发送后丢响应、日志失败、客户端本地ACK失败均保持冻结身份重试；唯一键恢复已提交原结果。日志不是持久提交证明，200/202、内存入队或flush不是ACK；本期不返回202任务接收。

## 9. R08：可靠回执、恢复与永久保存

### 9.1 成功与失败合同

沿共享 code/message/data 成功信封；新路由真实HTTP status与code一致。以下是回执完整形状，digest字符串仅为格式占位，不是上一请求的计算测试向量。

```json
{
  "code": 200, "message": "success",
  "data": {
    "contractVersion": "aiis.business-integration/v1", "digestProfile": "bi-json/v1",
    "producerId": "sma-demo", "eventId": "temperature-001", "resource": "temperature",
    "equipmentId": "line-demo", "mappingId": "temperature-five-zones", "mappingRevision": "r3",
    "requestDigest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "businessDigest": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
    "receiptId": 501, "recordId": 101, "performanceId": null, "affectedRecordIds": [101],
    "sourceTime": "2026-11-04T10:00:00.123+08:00", "committedAt": "2026-11-04T10:00:01.000+08:00",
    "status": "committed", "confirmation": "business_committed", "applied": true,
    "outcome": "created", "originalOutcome": "created", "changedFields": [],
    "businessRetention": "no_auto_ttl"
  }
}
```

recordId 是这次业务目标ID，三过程另返回真实performanceId；生产退出/unknown可能recordId=null，affectedRecordIds保存实际影响集合。changedFields只含静态字段别名数组，updated明确补缺范围。sourceTime为该请求sampledAt或recordTime；committedAt固定为首次可靠提交数据库时间，不因重试续期。receiptId在模块范围唯一，与resource一起解释；跨资源裸recordId不通用。

重放outcome=duplicate，originalOutcome/applied/confirmation/recordId/父id/affectedRecordIds/committedAt保持首次事实；applied 表示原事务是否改变业务对象，不表示当前这次重放又执行了一次。原stale重放仍confirmation=decision_only、originalOutcome=stale、applied=false、recordId=null，不冒充业务保存。回执证明原提交的范围，不证明此刻业务行未被后续合法观察/人工规则修改。

| HTTP | 稳定模块错误后缀 | 确认与重试边界 |
| --- | --- | --- |
| 403 | integration_scope_rejected | 未启用/设备或producer声明不在准入范围；无新提交，不隐含账号权限拒绝。 |
| 404 | integration_parent_not_found | 父不存在，无新提交；恢复父回执/父提交后可按原事件重试。 |
| 409 | integration_event_conflict / integration_value_conflict / integration_observation_time_conflict / integration_parent_mismatch | 请求或业务冲突，不覆盖，不换eventId盲重试；修正映射需新逻辑事件并仍受业务键规则约束。 |
| 413/415/422 | integration_payload_too_large / integration_media_type / integration_invalid_request | 请求不满足合同，无成功回执；修复后是修订过的新请求，不能修改已经可能提交的冻结事件。 |
| 503 | integration_not_ready / integration_unavailable / integration_commit_unknown | not_ready为采用前拒绝；commit_unknown必须以原身份/内容核实，不推断rollback。 |
| 500 | integration_internal_error | 脱敏；可能发生于已提交后的响应/日志阶段，客户端保留原事件恢复。 |

错误使用模块自有StrEnum、共享异常组件及局部HTTP adapter，失败壳 `{code,message,data:null,errorCode}`；不改旧全局HTTP200业务失败合同。DEBUG也不回显SQL、输入、连接串或token。503等不得用错误正文“未提交”覆盖未知事实。

### 9.2 两段确认与回执保留窗口

DAA事实ACK与本业务ACK不同；SMA须校验版本、producer/event/摘要/目标/confirmation，再持久保存业务确认和父id，才把对应outbox标已确认。接收cursor、处理checkpoint、冻结请求和各目标ACK不混为一个进度。

本版**业务幂等重放保证窗口为业务及其最小回执保留期间，默认无自动到期**。最小永久回执只保身份、两摘要、必要来源/映射版本、稳定结果/业务引用及提交时间，不永久保存整份raw或完整HTTP原文。没有调用方ACK API，Backend无法知道对方是否已保存回执，故本期不设一个会删除未恢复回执的自动TTL。

如后续需要有限回执窗口/压缩，须独立定义最短恢复期限、已确认与未确认区分、超窗错误/人工对账及生产历史事件证明；不能因业务永久就假定任何过窗event可再次安全执行，也不能因raw到期删除回执。本期无需新增GET回执平台：重发相同POST恢复稳定结果。

### 9.3 业务默认永久保存及必要Schema增量

业务永久保存指默认没有自动TTL清理；保存实际业务值、事件时间及必要来源/映射解释，raw/latest三自然月到期不影响已确认业务。追溯元数据可在模块自有回执/业务事件中持有并与业务一致关联，不仅保存raw外键，不永久复制所有原始事实。无raw FK级联至业务/回执/未完成outbox。

不可变温控/曲线保留各已接受样本；补缺表保留观测行；生产主记录是可演进聚合，后续合法观察/人工修正可能改变当前值，**本版不承诺覆盖前的每个值都有自动历史版本**。人工修正/删除仍受模块规则和回执引用保护；不新增匿名修正/DELETE。真正业务删除、审计历史/归档、备份和生产恢复另定，不把“永久”说成介质永不损坏。

建议新增且仅新增三张模块integration回执表：equipment_integration_receipts（temperature/drive/production_parameters）、performance_integration_receipts（四stream）、monitor_integration_receipts（curve）；不修改旧actor receipt身份。各自以producer/event唯一，保存上文稳定结果/摘要/必要sourceRefs/mapping，不存用户伪身份；明确目标FK+设备/父一致性与stream CHECK，禁止多态裸id跨表引用。

另增performance_integration_observation_events：设备+来源毫秒unique、businessDigest、稳定结果/目标引用及必要来源，用于历史生产事件判重与水位裁定，不靠当前水位或只查actor receipt。该索引是有限业务机制，不是事件总线。业务/watermark继续复用既有表，G-T前不接通；旧身份/记录不自动回填。Model/Schema/Alembic一致，不自动DDL/seed。

## 10. R09：实施批次、有限allowlist与排除项

### 10.1 本轮与后续顺序

| 阶段 | 范围与继续条件 |
| --- | --- |
| 当前PM起草 | 只新增本spec；Root同步六索引；只做文档/JSON自检。等待精确r1批准，不创建后续角色证据。 |
| A0 源码/no-DB准备 | 获批后Development创建tasks，先做有限Core原语/公开符号、八类DTO/默认关闭router、模块回执Model及静态迁移设计。以严格JSON、摘要向量、认证保护及未ready拒绝验证。 |
| G-T解除 | 主协调提交有界时间整改/采用范围和具体运行方案，按第3节获得真实证据。未解除时只交A0结果和具体blocker，不继续业务落库，不标整体通过。 |
| A1 equipment | 完整温控/drive/参数业务接线，复用纯规则，稳定不可变/补缺/来源/receipt，再继续。 |
| A2 performance | 生产生命周期/事件索引/水位/人工0和时间，再三类父依赖过程；不逐路重复完整全套。 |
| A3 monitor及源码收尾 | 曲线33字段/不可变/精度；集中完整相关no_db、compile、模块准入/旧链路和文档检查。 |
| B 隔离真实MySQL | A通过且G-T就绪后，Owner另批本任务精确目标、账号/schema/端口/卷、迁移/故障/并发/清理。独立tests_mysql入口，不使用共享破坏性conftest；无SQLite替代。 |
| 独立验证与Owner | developer_handoff后实际fresh-context Verification消费同一源码/diff/输出独立A及获批B；qa_passed后由Owner最终验收，部署/现场采用另批。 |

### 10.2 后续有限源码允许面

本表是待精确r1批准后的有限候选范围，不授权现在写入；花括号只展开所列集合。不授权backend/**或其他bundle。G-T自己的旧时间整改不借此表扩大实施。新migration的精确文件名/Revision及down_revision须在进入该文件实施前由PM依据实际head补定；这是目前尚未冻结的一项具体实现参数，不允许Development随意接链或重写旧迁移。

| 精确路径/有限集合 | 用途 |
| --- | --- |
| `backend/common/integration/{__init__,envelope,canonical,receipt,http}.py` | 有限纯信封/摘要/输出和局部HTTP解析适配；无业务表、无动态handler。 |
| `backend/app/module_contract.py`、`backend/app/MODULE_CONTRACT.md`、`backend/app/MODULE_CONTRACT.zh-CN.md`、`backend/tests/test_module_contract.py` | 仅新增上述实际公共符号、签名/版本与准入正负例；不泄露其他private Settings，不泛化legacy豁免。 |
| `backend/app/{equipment,performance,monitor}/manifest.py`、`backend/app/{equipment,performance,monitor}/models/__init__.py` | 三新router/错误/Model薄导出，保留原路由/权限/依赖与enabled行为。 |
| `backend/app/{equipment,performance,monitor}/api/integration.py`、`backend/app/{equipment,performance,monitor}/schemas/integration.py` | 八路模块typed输入/结果，独立匿名边界，路径父id与scope。 |
| `backend/app/{equipment,performance,monitor}/integration_{config,domain,error_codes}.py` | 有限本地准入/ready声明、纯业务规则和模块StrEnum。 |
| `backend/app/{equipment,performance,monitor}/models/integration.py` | 三receipt及performance业务事件索引；不重新定义八个业务Table。 |
| `backend/app/equipment/services/async_integration.py`、`backend/app/equipment/crud/async_integration.py` | 温控/drive/参数的模块事务及SQL。若复杂度达到分层阈值，先向PM提交有限拆文件Revision，不放大目录白名单。 |
| `backend/app/performance/services/async_integration_{observation,process}.py`、`backend/app/performance/crud/async_integration.py` | 生产/过程真实异步事务，父/水位/事件索引/人工优先。 |
| `backend/app/monitor/services/async_integration.py`、`backend/app/monitor/crud/async_integration.py` | 曲线事务与SQL。 |
| `backend/.env.example`、`backend/.env.docker.dev.example`、`backend/.env.docker.prod.example` | 仅新增模块integration默认关闭/空scope/未采用的英文占位配置；既有值/标题/grants保留。具体key在A0配置设计中固定，不读写真实env。 |
| `backend/tests/test_business_integration_{contract,api,service,migration,compatibility}.py`、`backend/tests_mysql/test_business_integration.py` | 八路公开行为、故障/并发/来源/时区/保留保护；B入口运行另批。 |
| `backend/tests/module_admission_fixtures.py` | 仅新增明确标识本任务来源/schema的公开fixture；不改冻结C2/E/F/BE003/BE006历史事实或放宽DB guard。 |
| `backend/README.md`、`backend/README.zh-CN.md`、`backend/app/README.md`、`backend/app/README.zh-CN.md`、`backend/app/equipment/README.md`、`backend/app/equipment/README.zh-CN.md`、`backend/app/monitor/README.md`、`backend/app/monitor/README.zh-CN.md`、`CODE_INDEX.md` | 仅稳定新合同入口、匿名/认证差别、ready/时间采用限制及真实结构索引。 |
| 本任务`tasks.md`、`checklist.md` | 精确批准后Development创建tasks；handoff后fresh Verification创建checklist，各自只写归属面。 |

**待补定的migration不是现有可写路径**；在PM给出精确后继并取得范围批准前，不写Alembic文件、不宣称migration实现面已完全冻结。最短路线为：Owner审阅本r1推荐 -> A0纯准备与时间整改范围收敛 -> PM一次性锁定实际接链/补充允许面 -> 业务接线及另批B。若Owner希望一次批准全部数据库实现，必须先完成这两项前置，不以模糊allowlist替代。

排除：任何前端/UI改造和新匿名GET平台、SMA/DAA/facts软件、DAA Stage C前置、C#移植、客户规则/真实配置、旧时间与历史数据批量迁移、旧auth/权限/用户修改、通用CRUD/SQL代理、万能receipt/事件平台、writer lease/管理API、实时覆盖新用例、raw保留清理器、通用鉴权/网络部署、依赖/lock/Compose/CI/打包/共享skill或生成器，以及未经具体批准的DB/Docker/API listener/PLC/Projection运行、现场切换、Git写/发布部署。

## 11. R10：验收标准与风险

下列均为未来交付要求，当前未执行技术测试或独立QA。A为source/no_db，B为另批真实隔离MySQL；A替身和offline SQL不代替B。

| AC | 可独立核对的标准 |
| --- | --- |
| AC01 八路完整合同 | 精确八个新匿名method/path、所有typed字段和单位与本spec一致；温控完整十值、曲线33项、生产十三观测、三过程父id明确。每类真实API -> 业务DB逐项读回及receipt引用一致；不只回显请求或200。 |
| AC02 严格JSON/缺测 | 原始ASGI覆盖未知/重复/蛇形/bool/string/null/0/非法UTF8/NaN/深度/体积/媒体类型/极端Decimal，真实HTTP与稳定模块errorCode；B确认NULL、Numeric精度、binary32容差、整数与0，不静默补值。 |
| AC03 身份/摘要 | 同producer/event跨设备/资源/父/来源/mapping异内容409；同内容重放稳定原结果；新事件同业务内容可复用；request/business两摘要边界及规范化向量可复现。标识大小写/源key原样，字段存在集合不丢。 |
| AC04 八类写入矩阵 | 温控/曲线不可变；drive/参数/过程新建/补NULL/同值/任一异值原子409，补后范围合法；同小时多时刻/不同卷/晚到保留；不存在任意实时覆盖或未知字段写SQL。 |
| AC05 生命周期与父子 | 新增/更新/退出/unknown/零活跃水位/重激活/前卷退出；历史成功事件恢复先于stale裁定，同刻冲突/晚到不倒退。父missing/mismatch/跨设备失败，父ACK丢失重放恢复，结束父晚到子成功；人工重量含0两种提交顺序优先，起止/总秒数来源准确，不动Plan。 |
| AC06 持久并发/故障 | B真实独立Session首次并发覆盖同/异投递与同/异业务内容、首水位竞争、RR旧快照/current读、投递冲突优先级；唯一胜者与有界恢复。业务/receipt/事件索引/水位/flush/commit/依赖退出故障无部分提交或假成功，commit未知/已提交丢响应同身份恢复。 |
| AC07 认证与准入保护 | 新路由无需凭据且有效scope才可写；未启用/空/越设备/producer拒绝，未ready503无业务变化。旧八POST及所有旧GET/PUT/DELETE保持其JWT/admin/permission/scope与响应；新声明不授旧权。disabled模块经重组新旧整组404。无伪User/admin、真实grants/env变更。 |
| AC08 时间与采用 | G-T真实材料齐备，既有UTC/legacy未被假称已整改；新API/DB上海毫秒、其他offset等瞬间、边界日期/未来时钟/亚毫秒/服务器不同系统TZ均正确。旧wire与业务键/水位兼容；无同列混存/盲加8/双写伪造。G-T未满足时整体不得qa_passed。 |
| AC09 永久业务/恢复 | raw/latest按三自然月清理的隔离夹具中，业务实际值/必要sourceRefs/mapping/稳定ACK与父子可独立恢复，未完成outbox不被级联。业务/最小回执默认无自动TTL；stale明确decision_only。人工/后续观察可变聚合与不可变样本的历史承诺准确。 |
| AC10 模块/Schema/兼容 | 显式新后继和三receipt/事件索引Model、Schema、约束/精度/FK/index一致；无启动DDL/seed。B空库和带合成旧行升级保护原表/行，旧migration字节、旧Projection事务、认证接口及其他模块保持。含业务数据的破坏性downgrade拒绝；默认回退关闭新入口并保留数据。 |
| AC11 公共复用与安全输出 | common/integration仅有限共用原语且在v1公开符号/文档/准入测试登记；模块字段/错误不进入Core。局部真实HTTP覆盖整个依赖退出，DEBUG脱敏；JSON Lines保留受控producer/event/resource/equipment/record/结果/失败，不存完整body、token、SQL/DSN或raw。 |
| AC12 真实交接 | 完整相关no_db/compile、模块准入/旧行为回归、JSON/链接/diff检查记录命令/退出码/限制；冻结profile旧失败如实区分，不削断言冒充全绿。最终源码/工作树/diff/基线与实际验证输入一致，独立fresh Verification及Owner最终验收各有真实gate。 |

主要风险：匿名来源可冒用；永久业务/最小回执持续增长；FLOAT量纲与近似误读；同设备双writer、旧UTC/legacy未知时间、生产RR并发、人工覆盖及commit未知。控制为明确准入/采用、领域限制、独立摘要/数据库unique、故障矩阵、G-T和B实证。没有吞吐/长稳/备份/生产可用性承诺；不能以本草案替代现场采用评估。

回退默认停新匿名写入口、保留业务/回执/事件证明、保留旧路径；不自动downgrade删除已接受数据。共享工作树含AW/SMA/DS/DAA/C#等并发增量，所有角色先固定自身基线，不reset、覆盖或把他人差异归己。临时源码的有效修改须整合交付树；必要证据持久化，资源只由协调者按归属和依赖收尾。

## 12. 当前决定、skill handoff与批准历史

Owner此次需审阅的具体建议：采用T1（复用八类业务表，新增三模块回执及必要生产事件索引）；接受有限统一外层和本版幂等/永久最小回执；保留匿名声明风险及旧认证保护；先批可准确实施的A0，业务落库等待G-T与精确migration接链，再进入另批B。不把“先出spec”推断为对本正文的批准。

适用技能：PM用project-governance、aiis/BLUEPRINT/CONTRACTS；技术边界只读参考backend-arch的RESPONSE_CONTRACT/LAYERS/DATABASE_AND_MIGRATIONS/MODULE_REGISTRATION/AUTH_SECURITY/OPERATIONS_TESTING。Development/Verification按相同技术面使用backend-arch，真实结构索引用code-document-indexer；若错误进入界面展示再用i18n-workflow；B需要Docker时再加载Docker专项。前端、Rust、PLC点位或shared skill升级均不在本轮，不能通过skill路由获得额外范围。

| 日期/Revision | 事实与效力 |
| --- | --- |
| 2026-11-04 r1 | Owner要求STD先规格，PM创建本draft；精确范围批准、Development、独立QA与最终验收均未发生。 |
| 2026-11-04 r1 范围批准 | Human Owner 精确批准本 r1，明确采用 T1 复用现有业务表，按 STD 仅先做 A0；时区兼容及迁移方案先提交确认，数据库/Docker 暂不执行，现有认证接口保持不变。 |

本轮PM自检只负责metadata、八份请求JSON与回执JSON语法、文档链接和有限写入，不替代软件测试或独立QA。主协调复核后将精确r1及其限制交Human Owner；本profile为contract_only，任务bundle、串行handoff及diff审计仍是必要控制，不宣称平台ACL/强制路由。

### r1 精确批准收据与当前交接

Human Owner 明确原话：

> 批准 ARCH-BE-010 r1，采用 T1 复用现有业务表，按 STD 先做 A0 开发。时区兼容和迁移方案先整理给我确认，数据库与 Docker 操作暂不执行，现有认证接口保持不变。

本次批准对应的原 draft SHA-256 为 `e144d236d82b67a7269f3c32250b96fb3b62561c1950d97788226dcec0ba4020`；主协调已固定批准输入。本次仅登记真实批准、T1 选择与阶段 handoff，不改变 R01–R10、AC01–AC12、allowlist、风险或 Revision。上文 draft/待审批/尚未发生批准的表述保留为起草时历史，当前效力以顶部元数据、本收据和 Owner 明确阶段限制为准。

当前只授权第10.1节 A0 源码/no-DB 准备。Development 按 STD 创建所属 tasks，基于源码在 tasks 中整理时区兼容与迁移方案供 Owner 确认；该提案不是已获批或已执行的方案。G-T 尚未解除，实际接通业务写入、A1–A3、精确 Alembic 文件/Revision/接链、数据库（含 SQLite）、任何 Docker 操作、B 验证、现场采用及发布部署均未由本批准授权，不因 A0 开发自动接续。

PM 本轮仅写本 spec，不创建 tasks/checklist 或其他提案，不实施代码/测试/配置/索引。主协调随后交实际 Development 仅执行 A0；其自检交接后的 fresh-context Verification、整体业务验收和 Human Owner 最终验收分别待真实 gate，不预记通过。
