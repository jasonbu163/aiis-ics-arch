Task ID: ARCH-BE-006
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner已明确批准ARCH-BE-006 r1；按STD交Development创建tasks.md，仅实施A源码阶段；数据库、Docker、浏览器具体运行/B及现场采用仍未批准，A通过后另行具体确认

Task Namespace: aiis-ics-arch
Classification: root
Capability: 原八类映射业务的HTTP写入、明确设备与来源的业务读回及现有页面接入
Owner: aiis-ics-arch equipment、performance、monitor公共业务切片
Acceptance Chain Reference: ARCH-BE-006 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Depends On: ARCH-BE-005 r3已验收的模块v1接入合同；ARCH-BE-003 r3当前qa_passed温控接口源码及e4f6a8b0c2d4迁移基线
Related Task: ARCH-BE-003, ARCH-BE-004, ARCH-BE-005, ARCH-MULTI-001
Workflow Mode: STD
Execution Mode: agent_team_same_session
Role Separation: PM -> Human Owner scope approval -> Development -> fresh-context QA / Verification -> Human Owner final acceptance
Fresh Context: required after developer_handoff
Created: 2026-10-16
Updated: 2026-10-16

# r1 范围批准收据（2026-10-16）

主协调者转递Human Owner当前turn明确原话：“批准 ARCH-BE-006 r1，按 STD 进入开发。数据库和 Docker 操作先不执行，等源码检查通过后再确认。”
批准对象为精确`ARCH-BE-006 r1`草案，原draft SHA256：`055a5e622d0c3d69830f916d43bda732a871f67a1ec17694601b9ec14334e07f`。

据此记录r1为`owner_approved`，交实际Development按本文既有allowlist创建所属`tasks.md`，仅实施A0–A3源码阶段并完成公开隔离源码/no_db/静态/离线检查。
任何数据库（包括SQLite/内存库）均不连接、创建、读取或写入；任何Docker命令均不执行。B的数据库/在线迁移/真实业务读写、测试API/浏览器具体运行目标及资源创建/清理仍未批准，须A通过后由协调者提交精确方案，经Human Owner具体确认才执行。
本收据不更改r1合同、字段、需求、验收标准、allowlist或风险，不升Revision。下文draft/待审批及“本轮只创建spec”等文字保留为草案形成时历史；当前批准状态以顶部元数据及本收据为准。
A源码通过不替代B、fresh-context Verification或Human Owner最终验收，也不授权现场采用、发布、部署或推送。PM仅更新本spec的批准元数据/历史/Handoff，不创建tasks/checklist或实施技术工作。

# 1. 审查摘要与当前授权

本任务在一份总规格中补齐原8类映射业务的写、读、页面闭环，按依赖分批实施，不为7条新POST分别建立任务bundle。
其中温控接收器已经由BE003实现；本任务保留其完整合同，补页面接入。其余7类新增业务HTTP入口，优先复用原业务表。

| 变更前 | r1推荐交付后 |
| --- | --- |
| BE003新温控POST写独立样本表；旧设备温控页面读旧表，因此新样本不会自动出现。 | 页面选择“外部上报”和获准业务设备后，通过新样本读面显示同一条已提交观测；选择“本地映射”仍读旧表。 |
| 另外7个本地同步Service可被Projection调用，缺少等价HTTP写入口。 | 增加7个async POST、对应明确读面、防重/冲突及事务规则；不把人工CRUD包装成映射入口。 |
| 设备旧表缺设备键；过程子表缺并发unique；缺测可能落成默认0。 | 新HTTP数据有明确业务设备键、来源时间和必要unique；缺测保存NULL并显示缺测。旧行及已有默认0原样保留。 |
| 页面没有新旧来源选择，部分图表把NULL转换成0。 | 仅增加来源/业务设备选择及必要空态、缺测适配；默认旧来源，不混排、不猜设备、不自动fallback。 |

Human Owner“好的，按你的建议来”授权形成这份总spec，**不等于批准尚未形成的r1实现范围**。
主协调者随后转递Human Owner已明确选择“页面按设备和数据来源切换查看”；该产品选择已决，其他推荐合同仍随完整r1一起审批。
本轮只创建本spec；不创建tasks/checklist，不改实现、测试、env、旧任务或运行资源。主协调者只机械同步根/backend PLAN及根catalog六处索引。

当前源码HEAD为`f85bea8bbf36b491968c3dc9a839518a1ed434a8`，起点工作树干净。BE005 r3已owner_accepted；
BE003 r3为qa_passed、Human Owner最终验收pending。其483源码检查和两轮各三场景是BE003历史证据，不证明BE006。
BE003的Owner状态不阻止本草案或本任务经精确批准后的独立源码工作，也不由本任务代授最终验收。
后续Development须核对实际技术前置及起点diff；若接口、head或本规格允许面实质改变，回PM新Revision。

# 2. R-001 八类能力、落表和读面

下表Service/CRUD均为当前仓库真实文件；8个`projection_handler`在各`services/sync_*.py`，不是manifest属性。
路径省略既有`API_V1_PREFIX`，公开前缀为`/api/v1`。新路由名称是r1拟定合同，不是现行可调用能力。

| 能力 / 现有本地Service | HTTP写入口 | 写表、业务键与新增/更新 | 指定读面 | 实际页面 / 当前调用 |
| --- | --- | --- | --- | --- |
| 温控 `equipment/services/sync_temperature.py` | **保留BE003** POST `/equipment/temperature-samples` | `equipment_temperature_samples`及原receipt；设备+UTC毫秒，完整十值不可变，created/duplicate/409；旧Service仍写`equipment_temperature` | 原GET `/equipment/temperature-samples`精确recordId；新增GET `/equipment/temperature-sample-dashboard`作窄读adapter | `equipment/views/temperature/index.vue`；当前`getTemperatureControlData`→旧`/equipment/temperature-control` |
| 传动 `equipment/services/sync_drive.py` | POST `/equipment/drive-samples` | 复用`equipment_drive`；HTTP设备+timestamp，首次新增，同键仅补此前NULL字段，相同duplicate、异值409 | 新GET `/equipment/drive-samples`，含精确items及dashboard | `equipment/views/drive/index.vue`；当前`getDriveData`→`/equipment/drive` |
| 生产参数 `equipment/services/sync_production_parameters.py` | POST `/equipment/production-parameter-samples` | 复用`equipment_production_parameters`；HTTP设备+卷号+timestamp，新增/补缺/duplicate/409；process_steps不开放自由写入 | 新GET `/equipment/production-parameter-samples`，含items及dashboard | `equipment/views/production-parameters/index.vue`；当前`getProductionParametersData`→`/equipment/production-parameters` |
| 生产观察 `performance/services/sync_production_record.py` | POST `/performances/production-observations` | 复用`performance_main`；HTTP设备+精确卷号，新增/更新/重激活/前卷退出；设备来源时间防旧状态回放，人工重量优先 | 新GET `/performances/mapping-records`、`/performances/mapping-records/{id}` | `performance/views/list/index.vue`；当前`getPerformanceList`→`/performances` |
| 过程温度 `performance/services/sync_process_temperature.py` | POST `/performances/{id}/process-temperature-samples` | 复用`performance_process_temperature`；HTTP设备+父id+zone+recordTime，新增/补缺/duplicate/409 | 新GET `/performances/mapping-records/{id}/process-data`的temperature | 同一实绩列表的过程弹窗温度tab；当前`getProcessData(row.id)`→旧`/performances/{id}/process-data` |
| 过程张力 `performance/services/sync_process_tension.py` | POST `/performances/{id}/process-tension-samples` | 复用`performance_process_tension`；同上键及新增/补缺/冲突规则 | 同上新process-data的tension | 同一弹窗张力tab |
| 过程速度 `performance/services/sync_process_speed.py` | POST `/performances/{id}/process-speed-samples` | 复用`performance_process_speed`；同上键及新增/补缺/冲突规则 | 同上新process-data的speed | 同一弹窗速度tab |
| 过程曲线 `monitor/services/sync_process_curve.py` | POST `/monitor/process-curve-samples` | 复用`monitor_history_process_curves`；HTTP设备+sampledAt，逐样本追加、等价duplicate、同刻异内容409，不覆盖曲线 | 新GET `/monitor/process-curve-samples`，含完整items及trends/latest | `monitor/views/temperature/index.vue`与Temperature/Tension/Speed/QualityCurve；当前`getTemperatureData`→`/monitor/temperature` |

设备/过程四类补缺是受限合并：新投递只可填原NULL或重复相同规范值，不能清空或改写已有观测；一次请求有任一冲突则整次409。
“updated”只表示成功补缺；不同来源时刻新增，均不按小时覆盖。曲线为不可变采样，生产主记录为有顺序的生命周期对象，两者不套用补缺规则。

# 3. R-002 七类请求字段与表示约束

## 3.1 共用边界与温控保护

新增7类均接收camelCase JSON对象，`equipmentId`、稳定`sampleId`、`quality="good"`必填。
equipmentId/sampleId采用1–128字符、区分大小写、无控制字符及首尾空白；不自动trim/casefold，不接收PLC地址、raw id、handler路径或控制命令。
设备scope见R-007。JSON重复/未知字段、snake_case替代、bool/数字字符串/NaN/Infinity拒绝422；0是真实有效值，不按truthy判断。
可选观测**省略表示未观测，显式null拒绝**；新行缺失字段必须实际落NULL，补缺时省略字段不修改原值。
至少一个观测字段的规则按下面各类执行，不要求每类完整快照。

drive/production-parameters/curve使用必填`sampledAt`；生产观察也使用`sampledAt`表示来源观察时间；过程三类使用必填`recordTime`。
这些时间及可选entryTime/startTime/endTime必须带时区、规范UTC毫秒，拒绝非零亚毫秒尾数；UTC年份1000–9999，输出ISO `...sssZ`。
不取HTTP到达时间补来源时间，不把id/到达顺序当最新；系统created/updated取数据库时间，不改变全局engine/session时区。

BE003的字段、单设备scope、原始Decimal解析、Numeric(30,10)、完整十值、receipt身份/冲突优先级、局部HTTP及依赖退出时序全部保持；
新adapter只读其样本表。不得回退为部分温控、小时覆盖、旧表双写或修改原GET响应。

## 3.2 准确字段清单

| 类别 | 除上述身份/时间外的字段 | 必填、空值、单位与范围推荐 |
| --- | --- | --- |
| drive | `tv, km, dewPointSet, dewPointActual, oxygen, mufflePressure, nh3FlowSet, nh3FlowActual, ngFlowSet, ngFlowActual, uncoilerSet, uncoilerActual, entryLooperSet, entryLooperActual, furnaceSet, furnaceActual, exitLooperSet, exitLooperActual, recoilerSet, recoilerActual`，共20项 | 20项可选但至少1项；露点°C、oxygen ppm、压力Pa、两气体流量m³/h、五组张力kN。TV/KM当前源码未定义物理单位，沿既有无单位标量，不猜测换算。露点/压力/其他观测不擅加客户物理上下限。 |
| production parameters | `coilNo`；可选`grade, entryTime, thickness, width, totalTime, weight, speed` | coilNo必填精确字符串1–50；grade 1–50；其余7项至少1项。厚度/宽度mm、totalTime分钟、weight吨、speed m/min；上述数量非负。processSteps、status、id、lastUpdate禁止输入；新行process_steps=[]，不伪造加工步骤。 |
| production observation | `observationStatus`；条件`coilNo`；可选`grade, weight, totalLength, diameter, density, spec, startTime, endTime, outputQuantity, qualifiedQuantity, efficiencyRate, qualityScore, remark`，共13项 | observationStatus必填`in_production/not_in_production/unknown`；in_production须coilNo 1–50，其他两状态coilNo省略/null且不带13项字段。grade≤20、spec≤50、remark≤500，提供时非空白。coilNo为业务字符串，`"0"`不等于停产，不沿用raw数值分类。weight吨、totalLength米、diameter毫米；density/两quantity/qualityScore当前未定义物理单位，沿既有业务标量，不宣称已核实现场量纲。efficiencyRate沿既有百分比展示；本期只限存储域，不凭名称新增0–100物理/业务阈值。 |
| process temperature | `coilNo, zone`；可选`setTemp, maxTemp, minTemp, avgTemp, duration` | coilNo须匹配路径父实绩；zone精确1–50；5项至少1项。温度°C可负；duration为该工艺段分钟，非主实绩总用时，首期只收0–9999999999整数分钟（既有MySQL未指定精度Numeric的技术域），保持现有出参duration整数合同，不作物理上限承诺。 |
| process tension | `coilNo, zone`；可选`setTension, avgTension, maxTension, minTension` | 同上父/zone；4项至少1项，单位kN、非负；同时提供min/avg/max时要求min≤avg≤max（缺失项不推算）。 |
| process speed | `coilNo, zone`；可选`setSpeed, avgSpeed, maxSpeed` | 同上父/zone；3项至少1项，m/min、非负；avg与max同时提供时avg≤max。 |
| process curve | 可选`coilNumber`及下方33项 | 至少1个测量，coilNumber省略为NULL、提供为1–50精确字符串，不要求父实绩，不自动创建实绩/能耗汇总。12个温度必须为整数°C；其余沿现有FLOAT观测域。 |

过程温度同时提供minTemp/avgTemp/maxTemp时同样校验min≤avg≤max；温度set值是观测，不是执行命令。
曲线33项精确为：`z1TempSet/z1TempAct`至`z6TempSet/z6TempAct`（12）；
`lineSpeedSet, lineSpeedAct`（m/min）；`uncSetTensionP, uncActTensionP, recSetTensionP, recActTensionP`（%）；
`uncSetTensionKg, recSetTensionKg, furnSetTensionKg, furnActTensionKg`（沿旧标签kg，不转换成kN）；
`coolFan1SetFre, coolFan1ActFre, coolFan2SetFre, coolFan2ActFre`（Hz）；`n2Total`（累计m³）、`electConsum`（累计kWh）；
`h2Flow, n2Flow`（m³/h）、`oxygenContent`（ppm）、`dewPoint`（°C）、`mufflePressure`（Pa）。
累计量只是本样本观测，不计算增量、重置或财务能耗；不是`monitor_history_energy_consumptions`的写入口。

## 3.3 数值精度

| 当前类型 / 本任务采用 | 新HTTP接收和读回要求 |
| --- | --- |
| 设备两表及曲线21项原FLOAT | 保留既有列及近似测量语义，不全表改Decimal/DOUBLE。只接收有限JSON number，绝对值≤3.4028234663852886e38；接受后读回相对误差≤1e-6，绝对误差≤max(1e-6,abs(input)×1e-6)。0须读回0；非零读回0或超容差必须拒绝并回滚，不能伪造成功。冲突/幂等以同一明确的存储精度规范值比较，不能一处原始JSON、一处浮点文本；Development在tasks固定此有界实现及边界例，不新增通用数值平台。 |
| 主实绩weight/collected/override/effective与两quantity | 既有Numeric(10,4)：绝对值<10^6，最多4位小数；本HTTP数量非负。缺失quantity落NULL，不沿旧default补0。 |
| 主实绩totalLength / diameter / density | 分别Numeric(10,2)/(8,2)/(5,3)：非负且分别<10^8/<10^6/<10^2，最多2/2/3位小数。 |
| efficiencyRate / qualityScore | Numeric(5,2)：绝对值<10^3、最多2位小数；非负，不静默裁剪到100。 |
| 过程温度四值；过程张力/速度 | 分别Numeric(8,2)与Numeric(10,2)：绝对值<10^6/<10^8、最多2位小数；温度允许负，张力/速度非负。 |
| 曲线12整数温度 | 有限JSON整数，MySQL signed INTEGER范围-2147483648..2147483647；不把小数温度取整。 |

Numeric字段按原始十进制解析，超scale/范围422、不舍入；`1/1.0`、`0/-0`等价。JSON输出不得再引入合同外精度丢失。
FLOAT容差是公开的近似测量合同，不能冒称BE003式逐位精确；不得用很小输入归0或很大输入溢出后还返回成功。

# 4. R-003 防重、晚到与冲突

新增7类的投递身份为`(actor User.id, equipmentId, stream, sampleId)`，token刷新不改变身份。
每个模块只新增一张有限stream receipt表，不建立跨模块通用receipt服务；fingerprint包含规范设备、来源时间、业务键、质量及**字段存在集合**和规范值，排除actor/token/到达时间。

| 情况 | 合同 |
| --- | --- |
| 同投递身份、同内容 | HTTP200 duplicate，返回原业务recordId及来源时间，不再执行补缺或状态流转。 |
| 同投递身份改时间/键/字段集合/任一值 | 409 `<module>.mapping_sample_id_conflict`；此冲突优先于业务键冲突，原receipt/业务数据不变。 |
| drive/production parameters/过程三类，不同投递同业务键 | 锁定本HTTP域业务行；相同字段值可重复，原NULL可补缺，任何已存在异值409 `mapping_value_conflict`。无改动duplicate，有补缺updated；整次原子提交receipt。 |
| curve不同投递同设备同UTC毫秒 | 内容及存在集合等价duplicate并补该投递receipt；否则409 `mapping_sample_time_conflict`；原样本不改。 |
| 独立采样的晚到 | 保存新行；最新/曲线排序用来源时间及id作稳定次序，不因到达较晚替换较新的来源观测。 |
| production同设备同UTC毫秒 | 作为同一生产观察事件，等价duplicate；不同状态/卷/字段409 `mapping_observation_time_conflict`。不得两个请求各创建一条在产主记录。 |
| production晚到旧时刻 | receipt尚无该投递时记录`outcome=stale`，不创建/重激活/退出或修改主记录，不倒退设备水位。返回受影响id空集或当前可见关联id，不能假称已应用旧观测。相同旧时刻已有成功事件则按其内容判重/冲突。 |

业务unique及投递unique是数据库裁决；只锁已存在行不能保证首次并发，必须覆盖新行竞争、rollback后新事务快照和有界重读。
只把确实命中本任务命名unique的重复键视作竞争，其他Integrity错误不是duplicate。
每个并发请求独立AsyncSession；失败不留下成功receipt。成功前完成Service commit及可失败的依赖退出；提交未知503，已提交后丢响应/日志失败按同sampleId重试恢复。
对生产状态顺序所需的最小设备水位行见R-005；它是业务状态，不是writer开关、租约或管理API。

# 5. R-004 生产父子、人工修改与主记录状态

新生产观察以HTTP业务equipmentId+精确coilNo定位`performance_main`，不借用旧PLC `device_id`或raw id。
新行plan_id=NULL、parent_coil_no=coilNo、record_source=`external_observation`；不自动关联/修改Plan，不触发split/merge/下推/质量判定。
production_date取sampledAt在Asia/Shanghai的日期；新记录first/last_observed_at及设备水位保存规范UTC毫秒。

in_production：无该卷新增；已有该卷更新其明确提供的13项并置在产，已退出的同卷可重激活；同设备此前在产/unknown卷一并退出。
not_in_production/unknown：只使该HTTP设备当前活跃主记录退出/转unknown；无活跃记录时不制造空卷，但仍持久化设备观察水位，避免晚到旧卷重新启动。
同设备事件在水位锁下串行裁定，主记录、前卷状态、水位、receipt同事务；来源更晚才推进状态。

人工重量优先级沿现有`manual_override_weight -> collected_weight -> unavailable`：新HTTP weight只更新collected_weight，
manual override存在时（含0）不改weight/effective_weight、其source或人工审计。没有override时使用采集重量；不提供清除人工覆盖的新API。
既有人工编辑仍通过原performance权限和入口；HTTP read/ingest不授予人工编辑权。人工重量更新和新观察须锁同一主行，验证两种提交顺序均保留人工优先。

startTime/endTime是来源报告的生产起止，不伪称人工输入：新增nullable `reported_start_time/reported_end_time`保存它们。
原start_time/end_time继续归既有人工作业；两个人工时间都有效时总用时优先人工时间，其次完整reported pair，再次first/last来源观察，否则NULL。
负时间范围422并回滚；单位输出总秒数，稳定duration source分别`manual_time/reported_time/external_observed/unavailable`，新增key归performance本地。
HTTP读adapter按上述优先级提供现有页面所需有效起止/总用时，并保留来源字段；旧legacy显示不改。其他13项没有新人工覆盖机制：较新观察中明确提供的字段更新，省略保留。

过程三类必须引用POST生产观察返回的真实父id，并同时校验equipmentId与coilNo；父缺失404 `performance.mapping_parent_not_found`，设备/卷不匹配409 `mapping_parent_mismatch`，越scope403。
不按卷号模糊寻找legacy/manual父、不自动造父；失败无receipt，父就绪后可用原sampleId重试。
已结束的匹配父可接收晚到过程记录，不重激活父；子表duration不写主total_duration。三类NULL指标在表格为缺测、图表为断点。

# 6. R-005 复用业务表的最小显式Schema增量

legacy定义为本任务HTTP设备键NULL；新增HTTP数据键非NULL且明确匹配scope。旧行不回填设备身份、不去重、不归并、不补新观测。
旧数值、默认0、原始时间及已有来源审计全留；旧不完整观测不能推断为新完整观测。原8个sync Service及Projection调用/提交链字节保持；旧CRUD仅增加HTTP键NULL过滤以防误更新新域行。

| 精确表 | 允许增量与legacy兼容 |
| --- | --- |
| `equipment_drive` | 新nullable equipment_id（精确字符串）；HTTP unique `(equipment_id,timestamp)`；timestamp无损扩为DATETIME(3)。20个测量列允许NULL，新HTTP INSERT显式NULL绕过旧ORM零默认；legacy默认及旧值保持。新域查询索引设备+来源时间。 |
| `equipment_production_parameters` | 同上设备键/时间/测量NULL；新增nullable二进制http_coil_key保存精确UTF-8卷号，unique `(equipment_id,http_coil_key,timestamp)`；grade新行可NULL，entry_time保留可空、扩毫秒；process_steps仅新行空数组。旧coil_no collation/default不重写。 |
| `performance_main` | 新nullable equipment_id、http_coil_key；HTTP unique `(equipment_id,http_coil_key)`，原device_id+coil_no unique保留。新HTTP device_id/plc_key/db_number/group/raw审计为NULL；reported_start/end为nullable DATETIME(3)，first/last_observed时间无损扩毫秒。output/qualified_quantity允许NULL，旧0/default保留，新HTTP显式NULL；原人工重量列/规则不删除。 |
| `performance_process_temperature/tension/speed` | 各增nullable equipment_id、二进制http_zone_key；HTTP unique `(equipment_id,performance_id,http_zone_key,record_time)`；record_time扩DATETIME(3)。原parent FK保留，新HTTP子行必须引用同HTTP域父；legacy设备键NULL，旧重复键不清理也不阻止HTTP域unique。 |
| `monitor_history_process_curves` | 新nullable equipment_id、sampled_at DATETIME(3)、请求内容fingerprint；HTTP unique `(equipment_id,sampled_at)`。device_id改为可空供HTTP行，不填假PLC id；旧值保持。HTTP created_at取DB时间，来源时间专列；旧created_at不转换或猜时区。33列原类型/nullable保持。 |
| `equipment_mapping_receipts` | 仅drive/production_parameters两stream；投递unique、fingerprint、来源时间、actor审计、结果；两个明确nullable目标FK按stream恰好选一个，不能跨设备引用。 |
| `performance_mapping_receipts` | 仅production_observation/process_temperature/process_tension/process_speed四stream；投递unique、fingerprint、来源时间、稳定结果及必要主/子id引用；生产状态事件可影响多个主id，结果如实保留；receipt不向GET暴露其他actor/sampleId。 |
| `monitor_mapping_receipts` | 仅process_curve stream；投递unique与曲线目标FK/设备一致性、fingerprint及actor/稳定结果。 |
| `performance_mapping_observation_state` | 唯一equipment_id、last_sampled_at、事件fingerprint及当前主id/状态；用于零主记录时的水位与首次并发序列化，不是租约或writer管理表。首插race由该unique处理；所有更新与业务/receipt同事务，无独立管理入口。 |

所有声明区分大小写的HTTP身份键均须由DDL显式保证精确比较：equipment_id、receipt的equipment_id/sample_id/stream、设备水位equipment_id及其unique/FK使用一致的binary collation或二进制类型，不能依赖MySQL默认collation。
stream只接受本规格列出的精确小写枚举，大小写变体不算同名。业务coil/zone同样精确；为避免改旧coil/zone collation与历史unique，HTTP二进制键只从已校验业务字符串生成，legacy为NULL；
卷/zone最多50字符、UTF-8最多200字节。新增receipt目标FK须保证设备/父一致，不能依赖多态裸id；所需支持unique仅限上述已列目标表。
receipt不加User FK改变删除账号规则。成功receipt关联的HTTP记录不得被旧DELETE级联清除；有限保护应返回明确业务拒绝，不影响legacy删除行为。

只新增一条显式后继：`backend/alembic/versions/20261016_1900_f6a8c0e2b4d6_expand_mapping_business_api.py`，
revision=`f6a8c0e2b4d6`、down_revision=`e4f6a8b0c2d4`。新增4表，BE006完整fixture为64表；旧60表中仅上表7个目标允许列/约束增量，其余53表签名和全部旧行保持。
原5条migration字节保持，Core C2/E14/15/16、冻结BE005 F/58及BE003/60历史断言不改写成64；新增BE006 profile单独标识来源/表数/head。
Model、Schema、migration同步；import/Registry/启动/GET不DDL、seed、自动迁移。timestamp扩毫秒不作时区换算，NULL新键不猜配。

downgrade只供另批可丢弃副本演练：有HTTP业务行/receipt或不能无损恢复旧NOT NULL/秒精度时必须安全拒绝，不自动删除、补零或截毫秒。
默认业务回退为停止新HTTP写入、页面选旧来源、保留所有已接收数据；真实部署/停机/数据撤回另批。MySQL DDL非事务，不宣称中途失败能自动恢复全部DDL。

# 7. R-006 页面、业务GET与来源切换

Human Owner已决定按设备和来源切换。设备3页、实绩列表/过程弹窗、monitor过程曲线页只增加必要控件，
来源枚举`legacy/http`，显示“本地映射 / Local mapping”“外部上报 / External reporting”；HTTP模式显示业务设备编号输入。
默认legacy，因为当前页面/已保存环境消费旧读面；不把这一定义成物理权威默认。legacy设备身份无法识别时明确“旧数据未标识业务设备”，
不提供虚假的逐设备筛选，不借PLC id猜业务身份。HTTP设备为空时不发业务查询，提示选择编号；编号必须经后端scope校验。

选择持有在本页URL query `dataSource/equipmentId`，刷新/返回可复现；缺省legacy，非法来源给受控提示且不查询，不能静默改HTTP到legacy。
同一来源/设备贯穿刷新、轮询、分页、日期和过程弹窗；切换时清空前来源数据，晚返回请求不能覆盖新选择。
沿现有布局、菜单、pageId、主题和路由；不新增设备目录/来源管理控制面或VITE开关，不改真实frontend env/grants。

| GET合同 | r1限定行为 |
| --- | --- |
| 原equipment三GET | drive/production查询仅equipment_id IS NULL；温控仍只读未改造的equipment_temperature。既有响应和limit未转发行为保留；不隐式读取HTTP行或把两表union。 |
| 新drive/production-parameter GET | equipmentId必填；recordId可选正整数，limit默认100、1–1000，SQL先设备/HTTP域再recordId，按timestamp DESC,id DESC实际limit。`data={equipmentId,items,dashboard}`；items含recordId、来源时间及真实可空字段；dashboard由同一选中行生成既有页面形状，缺测不计算虚假偏差/normal。 |
| 温控dashboard adapter | equipmentId必填、recordId/limit同原sample GET范围；只读BE003样本表，heatingZones取最新来源，temperatureHistory按选中样本升序，并附recordId及完整来源时间。沿既有read/scope；原POST/GET合同不变。 |
| 原performance读面 | legacy列表、原GET `/performances/{id}`及原过程读面仅HTTP键NULL；HTTP id通过这些旧读路径返回404。新HTTP精确id读取只经mapping-records读面及其scope/read检查。不能将共用CRUD的所有id访问一律加NULL过滤后封死下述必要人工重量入口。 |
| 新mapping-records读面 | equipmentId必填，列表沿page/pageSize、coilNo/grade/observationStatus/date筛选、响应items/total/page/pageSize形状；精确id及过程GET先设备过滤。不属于所选设备的id统一404，不泄漏其他设备。列表/详情使用R-004有效重量/时间及来源字段，过程数组含原id/performanceId/zone/recordTime和可空测量。 |
| 原monitor温度GET | 只读equipment_id IS NULL的legacy曲线，保留既有created_at日期语义；不把HTTP来源时间与旧无时区时间隐式合并。energy/collector/realtime不改源。 |
| 新curve GET | equipmentId和合法date=`YYYY-MM-DD`必填；按Asia/Shanghai自然日边界转UTC过滤sampled_at；recordId可选、limit默认1000且1–1000，取来源时间最近limit再升序返回。`data={equipmentId,items,trends,latest}`，items完整33项；trends/latest由同一HTTP行窄适配现有四图字段并带recordId/sampledAt标识；无数据items/trends=[]、latest={}。 |

新GET不写库、不seed、不mock fallback；新设备/monitor facade只选择明确source的路径、解包dashboard，不在前端重做snake/camel或业务映射。
API→表→读adapter→页面每层保留可核对recordId/父id/来源时间；无需为了显示增加新“接收成功”假行。
HTTP缺测显示缺测符号/断点，不能`Number(x)||0`或保留组件初始demo值。新完整温控十值不会缺测，但空结果仍须清空五温区旧数值。
legacy已有默认0不能被本任务识别为实测或伪零；原值保留并明确历史局限。布局/图表品类/非相关i18n不重做。

既有人工重量入口仍为PUT `/performances/{id}`，须持有原`performance`人工权限，不能用新read/ingest替代。
legacy请求保持原行为并仅定位NULL域；修改HTTP主行须显式携带query `dataSource=http&equipmentId=<所选设备>`，经过同一模块设备scope后，以设备+id锁定HTTP行。
HTTP分支只接受非空weight及可选remark（沿原人工原因用途），按R-002精度/非负及原人工覆盖规则处理；其他字段不在本次人工扩展内，拒绝422。
HTTP页面的同一编辑入口因此只提交weight/remark，其余信息只读；不增加新重量路由或新人工权限。持有原人工权限者可在获准设备scope内修改，不额外把新read权限当作写权限。
旧GET/PUT的legacy请求命中HTTP id、显式HTTP修改命中legacy/其他设备id均404；空/越配置scope先403，admin仍受scope约束。
DELETE `/performances/{id}`仅legacy分支维持原行为；显式HTTP分支在原人工权限及scope校验后，对本设备HTTP主行返回409 `performance.mapping_delete_forbidden`，不执行删除或级联receipt。
如此分别控制读、人工重量修改、删除，既不靠猜id绕过scope，也不把原get_performance的NULL过滤误当作所有入口的通用授权。

# 8. R-007 async、权限与写入所有权

新调用链必须是真实`async API -> async Service -> async CRUD -> AsyncSession`；Service负责业务、状态、水位、receipt的commit/rollback，CRUD只SQL/add/flush。
不能调会自行commit的旧人工CRUD拼装新事务，不能在async def直接运行同步DB；纯校验/规则可以模块内复用，不新建公共响应平台。
旧Projection继续本地sync Service/CRUD及同一Session的业务+cursor+audit事务，不改调自身HTTP，不恢复Celery/Redis/Worker，不伪造PLC provenance。

同一持久目标只能由所属域写入：旧sync CRUD限定HTTP设备键NULL，新HTTP CRUD限定明确设备非NULL；过程子写同父域；新HTTP表/receipt只由新async Service写。
**不新增writer gate/lease表或管理API，不修改旧sync Service。** 这种过滤与unique隔离保存和读取，不能证明同一物理设备没有同时被两条采集链观察。
单一Projection writer的原Runner部署约束保留；同物理设备权威切换、旧writer退休、跨域去重/数据合并、mapping发布及现场采用均为后续独立任务。

| 表面 | 认证/权限与scope |
| --- | --- |
| BE003及温控adapter | 原POST admin-only + equipment-temperature-ingest；原GET/adapter equipment-temperature-read；原EQUIPMENT_TEMPERATURE_PILOT_ID单设备scope完全保持。 |
| drive/production参数新POST、GET | POST active admin + `equipment-mapping-ingest`；GET独立`equipment-mapping-read`；新本地`EQUIPMENT_MAPPING_INGEST_ID`，安全缺省空。 |
| performance四POST、新GET | POST active admin + `performance-mapping-ingest`；GET独立`performance-mapping-read`；本地`PERFORMANCE_MAPPING_INGEST_ID`缺省空；不授予原performance人工CRUD/Plan权限。 |
| monitor新POST、GET | POST active admin + `monitor-curve-ingest`；GET独立`monitor-curve-read`；本地`MONITOR_MAPPING_INGEST_ID`缺省空；不互授monitor或monitor-business-read。 |

所有caller含admin都必须匹配该模块唯一配置业务设备；首期不提供多设备授权目录。旧源模式的旧权限保持，pageId不等于API权限。
新scope BaseSettings只使用既有公开resolve_env_file，支持公开注入、process>dotenv、每应用懒固定和隔离；不读私有Settings、不建跨应用缓存。
三份backend公开example只追加上述3个空scope及英文说明；全部原英文标题/注释/值/grants保留，真实.env不读写、不自动增加sup/op或页面授权。
manifest.enabled=False经重组/重启关闭所属新旧整组路由，admin亦404；不删除表/数据、不改变Alembic/model metadata。

仅新增router局部适配真实HTTP200/401/403/404/409/422/500/503，失败共享壳含同值code、data:null及模块自有StrEnum errorCode，
对应`<module>.mapping_unauthenticated/forbidden/invalid_sample/unavailable/internal_error`和前述冲突/父错误；不向Core错误/状态枚举追加业务key。
旧全局HTTP200业务失败合同保持；完整依赖退出先于成功发送，须继承BE003暴露的真实生命周期风险要求，不复制其已通过结论。
JSON Lines只记录受控actor/stream/equipment/record/outcome、状态old/new及拒绝/失败；不记录完整payload、token、SQL/DSN或真实配置。

# 9. 分批实施和验证门槛

| 批次 | 范围与继续条件 |
| --- | --- |
| A0 合同/隔离准备 | Development消费本r1、完整BE003/BE005当前事实与实际工作树；建立精确公开输入/diff。先落分域Schema/receipt和公共新路由局部边界，证明旧域过滤及migration recorder/offline保护；无需运行数据库。 |
| A1 equipment | 温控读adapter/来源选择，drive与production参数POST→GET→页面及NULL/补缺/冲突；定向稳定后继续。 |
| A2 performance | 主生产观察、来源水位及人工重量/时间，再接三类父依赖过程POST和实绩来源选择；父/并发/晚到规则定向稳定后继续。 |
| A3 monitor及集中源码收尾 | 曲线POST/GET/页面来源、精度/缺测；集中执行完整no_db、触达compileall、前端模块/构建与所有静态兼容检查。避免每加一路重跑全部套件。 |
| B 真实数据库与页面闭环 | A通过后提交BE006自己的disposable MySQL8.4.6、schema/账号/loopback端口/卷、迁移/回退/故障/并发、测试API和浏览器运行目标及清理清单，由Human Owner具体批准。独立tests_mysql入口不使用共享破坏性conftest。 |
| 交接与独立QA | Development完整handoff后必须新fresh-context Verification消费同一最终源码/diff，自行完成A及获批B的必要独立复验；B缺失保持qa_blocked，不因赶进度取消真实证据或独立性。QA通过后再Human Owner最终验收。 |

一个bundle记录上述批次，不为每条API制造重复3MD。批次不是独立最终验收；A通过不替代B。
项目行为采用uv/uv.lock及pnpm/lock，公开隔离副本/合成配置、mock/runner/bootstrap关闭；no_db阶段阻断所有DB（含SQLite）/网络/listener。
旧验证资源及具体运行批准不自动复用；真实env、生产数据、设备/PLC、Projection实际运行、发布/部署/Git refs/push仍排除。

# 10. 验收标准（以下均为后续要求，尚未执行）

| AC | 必需证据 |
| --- | --- |
| AC-01 八类闭环 | 八行矩阵逐类用真实API/业务Service写入，在指定GET按recordId/父id/设备读回，再在对应页面实际选“外部上报”及该设备/日期看到同一条数据。完整温控十值、其余所有已报字段逐项核对，FLOAT按公开精度，Numeric精确；仅POST200、回显请求、stub或receipt不算落库/页面证明。 |
| AC-02 字段与缺测 | 原始JSON的必填/条件字段、未知重复/snake/bool/string/非有限数、null/省略/0、时间时区/毫秒、各Numeric尺度/FLOAT边界/整数、单位及min/avg/max；缺字段持久NULL，页为缺测/断点，无demo/伪零。legacy已有0保持。 |
| AC-03 防重与补缺 | 每类同投递同/异内容，不同actor/sampleId同业务键同/补缺/冲突；重复无多行/多效果，conflict无部分补缺；提交后丢响应、未知commit及同id重试稳定recordId。真实独立Session首次并发验证unique与有界恢复，不只串行先查后插。 |
| AC-04 主子与人工优先 | 生产新增/更新/退出/unknown/重激活/新卷退出前卷、无活跃时水位、晚到不倒退、同刻事件冲突；missing/mismatch/跨设备父失败，父就绪原id重试，已结束父晚到过程成功。经原PUT实际修改HTTP主行重量含0，与HTTP观察并发两顺序保持优先；原人工权限/显式来源及scope、其他字段拒绝、旧读404与HTTP删除409分别验证。人工/来源起止及总秒数/来源准确，不改Plan或总用时为过程duration。 |
| AC-05 分域与兼容 | 新旧同timestamp/卷/zone可共存但旧CRUD不能更新HTTP行、新CRUD不能更新NULL域；legacy/API/页面不混排，跨设备recordId不泄漏。原8 descriptor/sync Service、业务+cursor+audit同事务回归；温控旧两表/原POST/GET字节及行为保护。energy两表、三API、小时/时间/权限和前端价格页全部保持。 |
| AC-06 事务/故障/HTTP | 业务insert/update、receipt、设备水位、flush/commit、依赖commit/rollback/close分别失败：无成功假响应、无部分业务/孤立receipt；已提交后失败可同键恢复。真实async链/CRUD不commit；新局部HTTP及DEBUG脱敏，旧全局响应不变。 |
| AC-07 权限与模块 | 实际JWT无/坏/过期/refresh/revoked/inactive401；非admin即使有ingest仍403；read/ingest/旧模块/CA/mapping/pageId不互授；空/跨scope所有caller403；disabled整组404。角色grants/真实env未改，公开英文标题/注释/值保持、三个空scope及双语说明一致。 |
| AC-08 MySQL迁移保护 | 空库base→f6、e4有合成旧行→f6；完整64表Model/DDL/反射类型/null/default/fsp/PK/FK/unique/check/index一致。旧60全部旧行校验和不变、7表只允许列增量，其他53表签名不变、旧5 migration字节保持；大小写/NULL键与legacy重复共存。可丢弃空HTTP副本downgrade/re-upgrade，含HTTP/不可逆精度副本拒绝破坏性downgrade，保留原数据。 |
| AC-09 页面来源与可用性 | 5个页面入口的default legacy、明确来源/设备、URL刷新/返回、切换清空与过期请求隔离、同选择分页/轮询/日期/过程弹窗；HTTP空scope/空数据/403/故障不fallback，旧不可识别设备说明明确。日夜/窄屏与中英切换必要控件可用，不改菜单/布局或授权。 |
| AC-10 有界交付 | 定向稳定后集中完整backend no_db+compile、原模块/迁移/Projection/价格/BE003回归、前端check:modules/test:modules/build及必要浏览器真实闭环；保留原断言、不缩套件。任务/源码/diff/命令退出码/限制/资源锁定交fresh QA，QA结果与Owner验收分别记录。 |

# 11. 后续Development有限allowlist

本表仅在**精确r1获批后**生效；花括号只展开列出的有限文件。不授权整模块/整backend、自动修改真实环境或其他任务bundle。

| 精确路径 / 有限集合 | 允许用途 |
| --- | --- |
| `backend/app/{equipment,performance,monitor}/manifest.py`、`backend/app/{equipment,performance,monitor}/models/__init__.py` | 新router/permission/error及新Model薄导出；保持v1、既有依赖/owner，无新增descriptor。 |
| `backend/app/equipment/api/{mapping_samples,mapping_http,temperature_dashboard}.py` | drive/production POST/GET和温控窄adapter，独立局部HTTP。 |
| `backend/app/equipment/schemas/{drive_sample_in,production_parameter_sample_in,mapping_sample_query,mapping_sample_out,temperature_dashboard_out}.py` | 有界输入/查询/输出。 |
| `backend/app/equipment/models/{equipment,mapping_ingest}.py`、`backend/app/equipment/{mapping_config,mapping_error_codes,mapping_domain}.py` | 仅R-005设备增量、两stream receipt、本地scope/规则/错误。 |
| `backend/app/equipment/services/{async_drive_sample,async_production_parameter_sample,async_temperature_dashboard}.py`、`backend/app/equipment/crud/{async_drive_sample,async_production_parameter_sample,async_mapping_ingest}.py` | 新async事务/读adapter，不调用旧sync执行。 |
| `backend/app/equipment/crud/{async_equipment,sync_drive,sync_production_parameters}.py` | 旧查询/更新仅增加HTTP设备键NULL过滤；不改旧limit/部分写语义。 |
| `backend/app/performance/api/{mapping_observations,mapping_http,process_samples,routes}.py`、`backend/app/performance/schemas/{production_observation_in,process_sample_in,mapping_query,mapping_out}.py` | 新4 POST/业务GET；旧读路径分域/scope及必要人工入口拒绝适配。 |
| `backend/app/performance/models/{performance,mapping_ingest}.py`、`backend/app/performance/{mapping_config,mapping_error_codes,mapping_domain}.py` | R-005主子列/unique/receipt和设备观察水位、R-004纯规则；不改其他实绩领域。 |
| `backend/app/performance/services/{async_production_observation,async_process_sample,async_mapping_query,async_performance}.py`、`backend/app/performance/crud/{async_production_observation,async_process_sample,async_mapping_ingest,async_performance}.py` | 新async读写；旧人工重量更新仅同主行加锁/保留新duration/receipt目标删除保护；不重构人工CRUD。 |
| `backend/app/performance/crud/{sync_production_record,_sync_process_common,sync_process_temperature,sync_process_tension,sync_process_speed}.py`、`backend/app/performance/schemas/performance_all.py` | 旧CRUD加NULL域过滤；仅旧输出数量可空的必要兼容，原人工Create/Update入参不放宽。 |
| `backend/app/monitor/api/{process_curve_samples,mapping_http}.py`、`backend/app/monitor/schemas/{process_curve_in,process_curve_query,process_curve_out}.py` | 新曲线POST/GET及局部HTTP。 |
| `backend/app/monitor/models/{business_history,mapping_ingest}.py`、`backend/app/monitor/{mapping_config,mapping_error_codes,mapping_domain}.py`、`backend/app/monitor/services/async_process_curve_sample.py`、`backend/app/monitor/crud/{async_process_curve_sample,async_mapping_ingest}.py` | R-005曲线/receipt及新async事务、完整读面/adapter。 |
| `backend/app/monitor/crud/async_temperature.py` | 原温度GET仅增加legacy NULL域过滤；旧energy/Core事实不改。 |
| `backend/alembic/versions/20261016_1900_f6a8c0e2b4d6_expand_mapping_business_api.py` | 唯一e4后继，严格R-005。 |
| `backend/.env.example`、`backend/.env.docker.dev.example`、`backend/.env.docker.prod.example` | 只追加3空scope和英文说明；其他原文/值不动。 |
| `frontend-js/src/app/equipment/{api/index.js,api/mock.js,views/drive/index.vue,views/temperature/index.vue,views/production-parameters/index.vue,locales/en-US.json,locales/zh-CN.json}` | 来源选择、对应新读面、缺测/空态；成对诊断mock仅保持接口，不作验收。 |
| `frontend-js/src/app/performance/{api/performance.js,api/mock/performance.js,views/list/index.vue,views/list/performance-presentation.mjs,locales/en-US.json,locales/zh-CN.json}` | 实绩/过程来源选择、scope与既有展示必要兼容，新增来源/总用时key。 |
| `frontend-js/src/app/monitor/{api/index.js,api/mock.js,views/temperature/index.vue,components/TemperatureCurve.vue,components/TensionCurve.vue,components/SpeedCurve.vue,components/QualityCurve.vue,locales/en-US.json,locales/zh-CN.json}` | 新曲线读面、来源/设备与NULL显示，不改energy/realtime/HMI。 |
| `frontend-js/src/components/BusinessDataSourceSelect.vue`、`frontend-js/src/utils/businessDataSource.mjs`、`frontend-js/src/locales/{en-US,zh-CN}/common.json` | 可选最小共享选择原语/URL解析，只有来源与设备输入，不调用业务API、不做配置/设备目录平台；业务翻译仍归模块。 |
| `backend/tests/test_mapping_{api,service,migration,compatibility}.py`、`backend/tests/test_equipment_mapping.py`、`backend/tests/test_performance_mapping.py`、`backend/tests/test_monitor_mapping.py`、`backend/tests_mysql/test_mapping_business_api.py` | 本任务公开合同/故障/迁移/并发/读写闭环，MySQL入口执行另批；不改共享conftest。 |
| `backend/tests/module_admission_fixtures.py` | 只新增明确BE006/64/f6的profile调用支持，不改变C2/E及冻结F/BE003保护，缓存落任务tmp。 |
| `frontend-js/src/app/equipment/api/mapping-source.test.mjs`、`frontend-js/src/app/monitor/api/mapping-source.test.mjs`、`frontend-js/src/app/performance/views/list/performance-presentation.test.mjs`、`frontend-js/src/utils/businessDataSource.test.mjs` | 来源路由/NULL/异步切换与必要展示合同，不添加镜像实现的无效测试。 |
| `backend/README.md`、`backend/README.zh-CN.md`、`backend/app/README.md`、`backend/app/README.zh-CN.md`、`backend/app/equipment/README.md`、`backend/app/equipment/README.zh-CN.md`、`backend/app/monitor/README.md`、`backend/app/monitor/README.zh-CN.md`、`frontend-js/README.md`、`frontend-js/README.zh-CN.md`、`CODE_INDEX.md` | 仅新稳定读写/来源/scope/Schema入口与真实结构索引；不补无关文档套件。 |
| 本任务`tasks.md`、`checklist.md` | 精确批准后Development创建tasks；developer_handoff后fresh Verification创建checklist，各角色只写自己面。 |

原BE003实现（含两Model、原router/adapter/domain/config/errors/Service/CRUD）、5条旧migration、其他模块及已验收energy全部保护。
不改Core Settings/deps/响应/错误/registry/preflight/database、Projection/runtime、任何sync Service、依赖/lock/Compose/CI/打包、AW/CA/PLC或根工具。
旧sync CRUD的变化仅域过滤，不允许新增同步HTTP流程。若这些边界仍不能实现合同或发现新跨模块依赖，先回PM修订，不扩白名单或削弱测试。
根/backend PLAN及根catalog由协调者机械同步；本轮不预建module PLAN或其他bundle。

# 12. 风险、排除项、skill handoff与批准历史

主要风险是FLOAT近似冲突、旧NULL/默认0误解释、同卷跨域碰撞、生产状态首次并发/晚到、父子顺序、人工覆盖竞态、依赖退出后假成功与MySQL非事务DDL。
控制归前述明确数值域、存在集合、HTTP二进制键、设备业务水位/unique、同事务receipt、读面分域及真实B矩阵；不以文档约定声称技术互斥。
三scope虽预留三个模块，均首期单设备；未指定物理单位的TV/KM/density/quantity/qualityScore不做换算或现场正确性承诺，现场量纲确认属采用gate。

排除：Flow/映射编辑器或调用客户端、SMA/DAA/AW facts、PLC raw绑定、现场点表/设备控制、通用响应/receipt平台、writer管理/租约/权威切换、跨域union/双写/归并、
能源小时合同/能耗结算、全模块人工CRUD改造、菜单/布局重做、多设备目录/机器身份、历史导入/去重/清理/保留期/聚合/吞吐长稳、任何未具体批准DB/Docker/浏览器运行/现场/发布部署推送。

PM已按任务使用project-governance、aiis（BLUEPRINT/CONTRACTS），只读参考backend-arch分层/响应/迁移/注册/认证/数据治理/运行测试，
frontend-ui（FRAMEWORK相关API/模块/展示规则）、i18n-workflow及interface-lineage-audit。
本轮使用源码直接溯源而未生成审计报告；已读本地lineage工具README/PLAN，未运行或改造scanner。
Development/Verification必须按上述技术面使用对应skill；结构索引用code-document-indexer。B涉及Docker时再加载docker-expert+docker-project-ops；
无Worker/Rust/PLC/scripts/tools实现，不加载这些技术skill。PM不替Development或Verification执行技术工作。

源码复核入口（相对本spec）：

- 治理：[AGENTS](../../AGENTS.md)、[workflow](../../.codex/workflows/development-lifecycle-workflow.md)、[模块公共合同](../../backend/app/MODULE_CONTRACT.zh-CN.md)。
- 既有任务：[BE003 spec](../ARCH-BE-003-mapping-service-api-pilot/spec.md)、[tasks](../ARCH-BE-003-mapping-service-api-pilot/tasks.md)、[checklist](../ARCH-BE-003-mapping-service-api-pilot/checklist.md)、[BE005](../ARCH-BE-005-backend-business-module-reintegration/spec.md)、[BE004](../ARCH-BE-004-energy-price-hourly-history/spec.md)。
- 设备：[Model](../../backend/app/equipment/models/equipment.py)、[读Service](../../backend/app/equipment/services/async_equipment.py)、[读CRUD](../../backend/app/equipment/crud/async_equipment.py)、[route](../../backend/app/equipment/api/routes.py)、[页面facade](../../frontend-js/src/app/equipment/api/index.js)。
- 实绩：[Model](../../backend/app/performance/models/performance.py)、[生产sync](../../backend/app/performance/services/sync_production_record.py)、[过程父查找](../../backend/app/performance/services/_sync_process_common.py)、[人工及读Service](../../backend/app/performance/services/async_performance.py)、[CRUD](../../backend/app/performance/crud/async_performance.py)、[页面](../../frontend-js/src/app/performance/views/list/index.vue)。
- 曲线：[Model](../../backend/app/monitor/models/business_history.py)、[sync](../../backend/app/monitor/services/sync_process_curve.py)、[读Service](../../backend/app/monitor/services/async_temperature.py)、[读CRUD](../../backend/app/monitor/crud/async_temperature.py)、[页面facade](../../frontend-js/src/app/monitor/api/index.js)。
- 事务：[Projection runner](../../backend/projection/runner.py)、[descriptor发现](../../backend/projection/registry.py)、[get_db](../../backend/database/session_async.py)。以上是源码事实，不是在线/现场证明。

最近作用域检查：equipment已有README/PLAN pairs并已消费；monitor只有README pair、performance无README/PLAN，均回到backend/app及backend文档。
frontend三个模块无自己的README/PLAN，使用frontend-js与src/app说明/PLAN；未发现更近AGENTS。不为本任务自动补这些缺失文档。

| Revision / 日期 | 决定及状态 |
| --- | --- |
| r1草案形成 / 2026-10-16 | Human Owner授权形成总spec，并明确页面按设备与来源切换；PM提出本有界合同。形成时为draft，精确范围批准、Development、独立QA及最终验收当时均未发生。 |
| r1范围批准 / 2026-10-16 | Human Owner明确“批准 ARCH-BE-006 r1，按 STD 进入开发。数据库和 Docker 操作先不执行，等源码检查通过后再确认。”据顶部收据记录owner_approved，仅交Development进入A源码阶段；B具体运行及最终验收仍分别待批准/验证。 |

PM -> Development：消费精确已批准`ARCH-BE-006 r1`及完整相关bundle、实际工作树/diff，按既有allowlist创建tasks并实施A源码阶段；记录真实自检结果及限制后交fresh-context Verification。
具体B运行目标、数据库/Docker/浏览器运行动作及清理仍另批；Human Owner最终验收尚未发生。
本profile为contract_only；主会话、角色文档、串行handoff和diff审计是必要控制，不宣称平台ACL/强制路由。
