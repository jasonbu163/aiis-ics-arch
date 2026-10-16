Task ID: ARCH-BE-003
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner已明确批准ARCH-BE-003 r3；交Development按STD创建tasks.md，仅实施A源码/no-DB阶段；任何数据库（含SQLite）及任何Docker命令均不执行，B具体操作待A通过后另行确认

Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: equipment完整温控样本的外部HTTP接收、持久防重及独立逐样本读回试点
Owner: aiis-ics-arch 可复用equipment温控采样切片
Acceptance Chain Reference: ARCH-BE-003 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Depends On: ARCH-BE-005 r3回迁后的equipment、模块v1合同及d2f4a6b8c0e2源码基线；不继承其批准或验收
Related Task: ARCH-BE-002, ARCH-BE-004, ARCH-MULTI-001, ARCH-AW-002
Workflow Mode: STD
Execution Mode: agent_team_same_session
Role Separation: PM -> Human Owner scope approval -> Development -> fresh-context QA / Verification -> Human Owner final acceptance
Fresh Context: required after developer_handoff
Created: 2026-10-12
Updated: 2026-10-16

# r3 范围批准收据（2026-10-16）

主协调者转递Human Owner本轮明确原话：“BE005 r3 验收通过，批准 BE003 r3，按 STD 进入开发。
数据库和 Docker 操作先不执行，等源码检查通过后再确认。”
批准对象为精确`ARCH-BE-003 r3`草案，原draft SHA256：
`208cf659cb36fc3737c4f7dddd30c581fcf85e8510bd0c03c97b70ce00aef019`。

据此将本r3记录为`owner_approved`，交实际Development按STD创建所属`tasks.md`，
仅实施本规格既有allowlist内的**A源码/no-DB阶段**，执行公开隔离源码、静态/离线/no_db检查并记录
命令、退出码、增量指纹及限制。**任何数据库（包括SQLite）均不连接、创建、读取或写入；
任何Docker命令（包括只读命令）均不执行。** B数据库/在线迁移/真实业务读写/Docker及清理动作仍未授权，
须在A源码检查通过后由主协调者另行提交精确目标、动作与清理方案，经Human Owner具体确认后才执行。
预留B验收项目保持未验证gate；A通过不替代B、独立QA或Human Owner最终验收。

Human Owner同时明确接受`ARCH-BE-005 r3`，其Owner final acceptance作为本任务回迁基线前置满足事实
记录于此；不重写下方BE005形成时的阶段事实，也不把BE005运行动作授权转移给BE003。
本次只记录批准与阶段门槛，不改变r3需求、范围、allowlist、验收、风险或后文r2/r1原文。
下方草案中的draft/待批准/未授权及BE005旧时点文字保留为形成时历史；当前批准状态以顶部元数据及本收据为准。
fresh-context Verification在developer_handoff后按STD独立执行并写checklist，Human Owner最终验收继续另经真实gate。
PM本轮仅修改本spec，不创建tasks/checklist，不实施代码、项目测试、数据库或Docker动作。

# r3 当前规格与批准边界

本节至“r2历史草案”之前是完整、当前、待批准的`ARCH-BE-003 r3`。后文r2原文及其r1盘点保留为
历史，旧的“当前无equipment/GET”、十六表head、common错误扩充、GET替换建议和待决Q-005均不再
作为执行依据；冲突以本r3为准。r1/r2均没有精确实施范围批准，不把讨论答复倒写成批准。

主协调者转递Human Owner本轮明确指令：“批准，按现有隔离 MySQL 方案完成 BE005 两轮验证及专用
资源清理；温控采用逐样本保存。同时按 STD 修订 BE003 r3，先给我确认 spec，暂不改接口代码。”
这段话确认Q-005并授权PM修订本spec；其中具体MySQL操作批准只属于BE005，不授权BE003的数据库、
Docker、实现或清理。**本r3仍为draft，待Human Owner精确范围批准。**

本轮PM只写本文件，不创建`tasks.md`/`checklist.md`，不执行项目行为测试、DB、Docker、真实API、
Projection、PLC、迁移或部署。主协调者只机械同步所属PLAN/catalog，不把索引作为第二事实源。

## 已确认选择与r3基线

| 事项 | 当前依据与结论 |
| --- | --- |
| owner与调用方 | 当前仓库`backend/app/equipment/`；第三方系统或未来SMA在调用前完成业务映射。本任务不实现SMA/调用客户端，也不复制PLC raw绑定请求。 |
| Q-001完整样本 | 五温区的设定/实际共10项，单位°C；全部必填，0有效，缺失/null拒绝且不补零。 |
| Q-002身份与时间 | 一个可配置业务设备编号，文档/合成示例`temperature-pilot-01`，不是PLC地址；稳定`sampleId`，重试不变；`sampledAt`带时区并保留毫秒；同设备同时间不同值409不覆盖。 |
| Q-003权限 | 首批POST admin-only，并检查获准设备范围及独立`equipment-temperature-ingest`；不自动给supervisor/operator授权。 |
| Q-004验证 | 保留一次性隔离MySQL `8.4.6`验证；本任务具体实例/库/迁移/业务写/清理动作仍另批，不沿用BE005批准。 |
| Q-005粒度 | **已确认逐样本保存**，同小时不同采样时刻分别保存；小时汇总/代表值/降采样另案。没有新增待问业务问题。 |
| 当前源码 | 本轮只读检出的HEAD为`1a5aa2d2fe7089b5671218865238cfaa240f9a30`；共享工作树另有AW/Console及BE005并行增量，HEAD不是运行采用或全部当前工作树的证明。 |
| BE005阶段事实 | 本r3形成时已读其r3完整spec/tasks/checklist，确认A独立通过319项源码测试及浏览器检查。2026-10-16 B具体操作获Human Owner批准；本轮后续阶段结果仅以BE005三文件为准。本文不预判B独立QA结论，不宣称BE005整体`qa_passed`或`owner_accepted`。 |
| Schema源码 | `d4e6f8a0b2c4 -> a6c8e0f2b4d6 -> b8d0f2a4c6e8 -> d2f4a6b8c0e2`，回迁fixture为58表。来自迁移/Model/静态测试源码，不是PM执行在线迁移的结果；`alembic current`也只证明选定库的版本对齐。 |

Development开始前须消费BE005最新有效handoff与当前工作树，记录实际起点指纹；若B返工改变本任务的
表、接口、公开合同或迁移head，先回PM校正Revision，不默默沿用本r3基线。

# R3-001 旧、新数据各自归属与最小实现裁定

已只读核对当前`equipment` manifest、三GET、Models、async查询、温控sync Service/CRUD、
`_sync_common.py`和`d2f4a6b8c0e2`实际建表操作。

| 链路 | 当前事实及r3边界 |
| --- | --- |
| 旧`equipment_temperature` | `id`主键、`timestamp`普通索引、10个Float温度列；没有业务设备键、sampleId、receipt或timestamp唯一约束。ORM温度列有`default=0.0`；迁移温度列非空但无补零server default。原timestamp未显式声明毫秒精度。 |
| 旧同步writer | `equipment.sync_temperature`验证既有PLC来源，good质量且至少一项值时，按精确timestamp查找加锁，新增或只覆盖非空字段；可省timestamp并用collected_at，只flush不commit。不是完整样本不可变/并发首次写入唯一保证，也没有小时取整。 |
| 旧温控GET | `GET /equipment/temperature-control`读取上述旧表，返回`heatingZones`和`temperatureHistory`；历史仅有时分秒及实际温度。当前route声明limit却未传给Service，Service实际默认10；本任务保留这一既有行为，不顺手修复。旧mock-on可生成旧表样本；本任务真实验证固定mock-off，不把诊断数据当事实。 |
| 新完整样本 | 由equipment新增`equipment_temperature_samples`持久保存完整、不可变、带业务设备键和毫秒来源时间的样本；新增`equipment_temperature_sample_receipts`保存投递身份、fingerprint、稳定结果及必要actor审计。只允许新async Service写这两表。 |
| 新读回GET | `GET /equipment/temperature-samples`只查新样本表，返回完整10项与来源时间；不union旧表、不读receipt构造假观测，也不从旧表猜设备身份。旧表已有数据不迁移、不去重、不补设备键。 |
| 前端与当前值 | 既有前端继续调用旧温控GET，**不会自动展示第三方写入的新样本**。新GET中的最近样本只代表新表该设备的来源时间排序；旧看板当前值与新样本最新值各有来源，不能混为一个current。前端接入及两链路统一另案。 |

采用两张新增表的理由是旧表的设备身份、部分字段合并、默认值、唯一性和时间精度无法同时满足新合同；
直接向旧表加键/改writer或双写会改变旧GET/存量语义。新表与receipt由同一equipment owner管理，
只增加必要持久接收面，不建设通用receipt、事件总线、时序库或采集平台。

原8个descriptor、同步Services、Projection注册/映射机制及本地同一Session的业务+cursor+audit
提交/回滚全部保留。新HTTP不调用旧sync Service、不伪造PLC provenance、不在descriptor.invoke内
调用HTTP，不修改旧表、不做双写或默认停止旧writer。两链路可以各写自己的表，本阶段不承诺同一物理
观测跨两表去重或统一；未来writer切换/旧handler退休/HTTP投递及断网恢复须另立范围和具体操作gate。

# R3-002 一个完整业务写入口及逐样本读回

新增路径均由现有`API_V1_PREFIX`挂载，公开示例为`/api/v1/equipment/temperature-samples`。
equipment manifest新增独立router入口，原`api/routes.py`与其`equipment`guard保留；新router
不能被旧顶层guard隐式叠加权限，也不能把新ingest/read授权扩大成旧三GET授权。

## POST入参与结果

| 字段 | 合同 |
| --- | --- |
| `equipmentId` | 必填字符串，精确匹配唯一获准业务设备key；不能取PLC/raw device_id，也不接受额外地址字段。 |
| `sampleId` | 必填来源侧在首次投递前产生并持久保持的不透明字符串；长度1–128，拒绝空白值、控制字符及首尾空白，不静默trim/casefold。投递作用域为稳定`User.id + equipmentId + sampleId`，不取token jti/用户名作为身份。 |
| `sampledAt` | 必填ISO 8601来源时间且有时区；归一UTC，按毫秒持久化和判重。同一瞬间不同时区写法相等；小数超过3位且有非零尾数拒绝，不截断。整秒等价`.000`；输出统一`YYYY-MM-DDTHH:mm:ss.sssZ`。不能用到达时间替代；UTC转换后超出持久类型可表示域须422。 |
| `quality` | 必填稳定key `good`；其他质量422，不生成样本或receipt，不沿用旧writer的skipped成功。 |
| `zone1Set/zone1Act`至`zone5Set/zone5Act` | 10项全部必填的有限JSON number，单位°C，0有效；拒绝null/bool/数字字符串/NaN/Infinity/未知字段，不补零、不裁剪。`zoneNSet`是观测到的设定值，不是温控下发命令。 |

`equipmentId`的长度上限同为128并与配置使用同一精确标识规则；设备key和sampleId区分大小写，
数据库唯一键必须保持该语义，不受默认case-insensitive collation影响。JSON字段仅采用上述camelCase；
未知/重复字段或snake_case替代输入不能悄悄覆盖正确字段。持久数值类型、技术精度/可表示域由Development
在tasks中明确并以合同测试锁定；接受的值不得静默舍入/溢出。fingerprint基于规范化数值，`1`/`1.0`、
`0`/`-0`及等价时区相同；不按原始JSON字节判重，不新增无事实依据的物理温度上下限。

成功使用共享`SuccessResponse`或`StandardResponse`的`code/message/data`与camelCase规则；
已有SuccessResponse的外层`timestamp`可保留，它不是sampledAt或业务创建时间。
HTTP 200，`data`至少为`recordId/equipmentId/sampleId/sampledAt/outcome`。
首次新业务样本`outcome=created`；重放或已存在等价业务样本`outcome=duplicate`，返回原recordId、
来源时间和当前投递sampleId，不更新原样本。receipt保存首次提交的稳定结果字段；
后续重放仅把响应outcome标为duplicate，不把“original result”解释成每次必须重复created。

## GET入参、可见范围和空态

`GET /equipment/temperature-samples`接受可省的`equipmentId`（省略时用唯一配置key）、
可省正整数`recordId`和`limit`（默认100，范围1–1000，实际下推SQL）。
先验证认证/read权限及设备scope；显式设备越界403。按设备过滤后再按recordId过滤，不允许ID绕过scope。
响应`data={equipmentId, items}`；items每项包含`recordId/equipmentId/sampledAt/quality`、
完整10项温度及`createdAt`，不暴露其他actor的receipt、sampleId或认证信息。
查无数据或不属于获准设备的recordId返回`items=[]`，不泄漏该ID是否存在于其他设备。
GET无写入/seed/mock fallback；可对POST返回的recordId精确读回一项完整样本。

默认按`sampled_at DESC, id DESC`取最近limit行，输出同序。不同来源时间晚到的样本正常保存；
晚到旧样本不会取代来源时间更晚的首项。`limit=1`定义新表该设备的最近已接受样本，既不按到达时间、
id、整点小时选择，也不代表旧GET的当前值。本轮不建立小时汇总、保留期、时钟校准或额外未来时间窗口；
最新值按已接受的来源时间排序，不承诺物理设备当前状态或全量历史导出。

# R3-003 持久身份、防重与并发冲突

| 事务内结果矩阵 | 行为 |
| --- | --- |
| 同actor/设备/sampleId，内容相同 | 读已提交receipt，HTTP200 duplicate，recordId不变；不追加样本或receipt。token刷新不影响判重。 |
| 同actor/设备/sampleId，设备内来源时间、质量或任一值改变 | HTTP409 `equipment.temperature_sample_id_conflict`；原样本与receipt均不变。 |
| 不同sampleId或不同actor，同设备/同UTC毫秒且内容相同 | 复用同一业务recordId，为该新投递身份只新增一条receipt；HTTP200 duplicate，不授予读取/修改其他actor receipt的能力。 |
| 不同sampleId或不同actor，同设备/同UTC毫秒但内容不同 | HTTP409 `equipment.temperature_sample_time_conflict`，不覆盖、不留成功receipt。若同时命中同投递异payload，优先sample_id_conflict。 |
| 不同UTC毫秒，包括同小时及晚到 | 各保存一条完整新样本与对应receipt；不存在小时覆盖。 |
| 另一设备或scope为空 | 在任何样本/receipt查询写入前拒绝403；admin也不能跨设备。跨设备身份在数据结构上独立，但首批不开放第二设备或设备授权管理。 |

业务样本唯一键为`(equipment_id, sampled_at)`；投递receipt唯一键为
`(actor_user_id, equipment_id, sample_id)`。fingerprint覆盖规范化设备、UTC毫秒、quality与全部10值，
不含到达时间、actor/token/JSON字段顺序；sampleId/actor只组成投递身份，不改变同业务键内容比较。
样本保存可比较的规范化内容/fingerprint；receipt保存请求fingerprint及结果引用，不能只靠进程字典、
“先查后插”或只锁已有行保证首次并发唯一。

数据库unique是最终竞争裁决。Development须在AsyncSession中选择有界的冲突重读/事务恢复策略，
正确处理提交竞争、rollback后session状态和隔离级别可见性；不能把所有IntegrityError一概当duplicate。
竞争者只可复用已完整提交且内容相同的记录；无法完成的系统/锁失败返回安全可重试失败，客户端保持同sampleId。
同一投递不同payload、同时间不同值的并发必须有唯一胜者且另一方409，不能最后到达者覆盖。

# R3-004 新表、事务与显式迁移

| 新实体（equipment owner） | 必需持久信息与约束 |
| --- | --- |
| `equipment_temperature_samples` | 数据库生成id；equipment_id；UTC毫秒sampled_at；quality；10个非空数值且无零默认值；内容fingerprint；数据库时间created_at/updated_at。业务唯一键及设备/来源时间查询索引。成功样本不可变，不提供PATCH/PUT/DELETE。 |
| `equipment_temperature_sample_receipts` | id；actor_user_id；equipment_id；sample_id；请求fingerprint；sample_record_id外键及必要一致性校验；首次稳定结果字段；数据库时间created_at/updated_at。投递唯一键，不能出现无业务样本的成功receipt。actor使用认证User.id的审计快照，不新增会改变现有用户删除规则的user外键或用户管理行为。 |

sampled_at须使用能真实保存UTC毫秒的类型（MySQL DATETIME(3)或经同等证据的表示），不能直接沿用
旧Timestamp默认类型而丢毫秒；业务键等价性以实际MySQL读回证明。数据库接收/创建时间来自数据库UTC
时钟，与外部sampledAt分开；不修改数据库session时区或全局engine。两表Model、迁移和Schema一致，
约束名/索引/精度由Development记录；其他DB方言的现场支持不因静态编译而宣称已验证。

新业务样本、投递receipt及其中必要的actor审计在**同一数据库事务**提交，Service负责commit/rollback，
CRUD仅查询/add/flush。首次响应前须完成commit，不能只flush后依赖get_db退出时自动commit。
任一业务insert、receipt/audit持久化、flush或commit失败全部回滚，不返回成功；重复投递补receipt也必须
先提交。数据库依赖既有退出commit不得成为另一笔业务写。日志不是第三张审计表或事务真相源。

响应发送在commit之后：已提交但响应丢失时，客户端保留同sampleId重试并得到同recordId；不得追加。
commit结果未知时返回安全系统失败并允许同键重试，不在新事务“补写”不确定结果。
对业务、receipt审计、flush/commit失败分别注入验证；不得把日志写成功当作事务已提交。
同一receipt不能跨设备引用样本；不读取或修改Projection cursor/runtime audit。

只新增一条显式迁移：
`backend/alembic/versions/20261016_1600_e4f6a8b0c2d4_add_equipment_temperature_samples.py`，
`revision=e4f6a8b0c2d4`、`down_revision=d2f4a6b8c0e2`。
upgrade只建上述2表/其索引约束，完整回迁+本试点fixture为60表；原58表完整签名/记录保持，
原4条迁移字节保持。downgrade仅撤receipt再撤sample，会丢本增量样本，不能作为已投运默认回退。
不create_all/stamp、重写旧migration或导入旧温控行，不执行历史修复/清理。import/Registry/GET/启动
不运行DDL或seed。若head碰撞或变化，先回PM新Revision，不私自改接链。

# R3-005 认证、scope、模块配置及v1公共入口增量

POST复用v1公开`get_current_active_admin`和`require_permissions("equipment-temperature-ingest")`；
非admin即使人为授予ingest仍403。GET用独立`equipment-temperature-read`，沿现有admin恒权/
sup-op数组机制：首批admin可读；active supervisor/operator仅在各自有效数组显式授予read时可读，
未知角色拒绝。GET不额外要求admin或旧equipment权限；两角色默认不增加任何read/ingest grant。
旧`equipment`权限、pageId、mapping-manage、CA gate token不授予新接口；read与ingest不互相授权。
admin只绕过权限数组，仍受设备scope、入参、完整样本与防重/冲突规则约束。
所有调用者包括admin都必须通过唯一设备scope。空scope只拒绝新GET/POST，不开放所有设备，
不改变旧GET的权限或数据源。`enabled=False`经既有重启组合后统一移除equipment旧、新整组路由，
不删除两类数据；设备scope不是模块enabled开关。身份来自既有active User access-token；
无/坏/过期/refresh/撤销token、禁用用户为401，不把JWT权限声明或token jti当业务设备授权目录。

新增非秘密设置`EQUIPMENT_TEMPERATURE_PILOT_ID`由`app/equipment/config.py`的模块本地BaseSettings
拥有，只接受一个业务key，缺省`""`；未配置/无效scope时新GET/POST拒绝403。
使用模块依赖懒加载，不在manifest/Model import创建设备配置实例、不触发额外连接；
支持显式测试注入并隔离不同应用，不能用共享缓存把另一应用设备范围带入。
读取现有唯一运行.env：源码`backend/.env`、冻结制品可执行文件同目录.env、Docker既有`/app/.env`；
process env覆盖dotenv，测试显式临时env或`_env_file=None`，不读本机真实文件。
配置变更按重启采用，不宣称热卸载/自动授权；文档与合成测试使用`temperature-pilot-01`，
三公开example实际保持安全`EQUIPMENT_TEMPERATURE_PILOT_ID=''`，英文标题/注释及已有值/grants保留。

当前v1仅公开`settings.BACKEND_MOCK_ENABLED`，不能假定新业务字段已被允许，也不能改成私有Settings读取。
本r3提出一个**待Owner批准的加法公共入口**：在`app/module_contract.py::PUBLIC_SYMBOLS["settings"]`
仅补现存`resolve_env_file`；双语MODULE_CONTRACT说明其`() -> Path`签名及源码/冻结路径语义。
该helper当前已存在于settings.py和C0，函数本身只计算路径；settings模块仍有既有模块级Settings初始化，
不能把导入整个模块写成完全env-free。无需修改helper、Core Settings字段、private-setting预检规则或版本号；
不新增配置平台/动态注册/legacy豁免。新增字段只归equipment本地配置。
公开入口正例与仍拒绝其他私有Settings的负例，以及源码/冻结路径、dotenv/process优先级、
空scope/new-API拒绝/旧GET不受影响均需源码阶段证据。

# R3-006 async分层、外部HTTP与安全错误合同

新调用链仅`async API -> async Service -> async CRUD -> AsyncSession`，使用现有v1的database、
schema_base、response、BusinessException、core.deps与log_event公开符号。禁止async请求中调用同步DB
Service/Session，不增加Celery/Redis/Worker前置条件或HTTP长任务队列；未来SMA仅是调用方。

新增`equipment/error_codes.py`自有StrEnum，值使用以下equipment命名空间并在manifest.error_codes声明：

| HTTP | `errorCode` | 范围 |
| --- | --- | --- |
| 401 | `equipment.temperature_unauthenticated` | 本新router认证失败，保留WWW-Authenticate语义。 |
| 403 | `equipment.temperature_forbidden` | 新接口role/permission/设备scope拒绝；不泄漏其他设备状态。 |
| 422 | `equipment.temperature_invalid_sample` | JSON、参数、字段/quality、时间/数值不可表示或未知/重复字段；可返回受控字段名，不能回显原输入/异常全文。 |
| 409 | `equipment.temperature_sample_id_conflict` | 同投递身份改payload。 |
| 409 | `equipment.temperature_sample_time_conflict` | 同设备UTC毫秒不同内容。 |
| 503 | `equipment.temperature_unavailable` | 已知DB不可用、可重试竞争/提交结果未知；同sampleId重试。 |
| 500 | `equipment.temperature_internal_error` | 未预期内部失败；脱敏，提交前失败不留成功receipt，提交后响应失败按同sampleId重试恢复已提交结果。 |

Service使用共享BusinessException接收模块StrEnum；Service/CRUD/纯规则不导入Request/Response/
HTTPException。新router的局部APIRoute/adapter处理整个本地请求和依赖阶段的BusinessException、
HTTPException、RequestValidationError及系统异常，输出真实HTTP与同值`code`，
失败壳`{code,message,data:null,errorCode}`、稳定英文message。
特别覆盖缺Bearer和DEBUG=True失败，避免落入旧全局HTTP200或回显SQL/连接串。
局部adapter只作用于新两条method/path；**不修改Core全局错误枚举/BusinessException/handler或认证行为**，
旧GET与其他模块响应不变，不让两个error owner冲突。无需新响应SDK或全局中间件。
系统失败不得被当409/duplicate；未注册/disabled模块仍由既有路由返回404。

继续既有JSON Lines日志机制，必要事件为接收成功/duplicate/冲突、认证或scope拒绝、事务失败，
带稳定event及必要actor/业务标识/结果；不记录完整10值请求体、token、Authorization、秘密、SQL或连接串。
receipt中的actor/结果是持久审计；日志失败不得伪造业务结果。普通GET不制造逐行日志或样本。

# 后续Development精确allowlist（仅r3获批后生效）

本轮唯一写入仍为本spec。下表不授权现在实施，也不是`backend/**`或旧equipment整目录授权。
花括号仅展开列出的有限集合；所有新增源码保持中文头部或既有风格。

| 精确路径/有限集合 | 获批后允许用途 |
| --- | --- |
| `backend/app/equipment/manifest.py` | 保留现有enabled/order/旧router/models/permission，追加新router、两permission和本地错误声明；依赖按v1如实保留，不中央补名单。 |
| `backend/app/equipment/api/temperature_samples.py`、`backend/app/equipment/api/temperature_http.py` | 新POST/GET及本router局部HTTP适配；不改原`api/routes.py`。 |
| `backend/app/equipment/schemas/temperature_{sample_in,sample_query,sample_out}.py` | 完整输入、只读查询与输出Schema；不改变旧equipment_query。 |
| `backend/app/equipment/models/temperature_sample.py`、`backend/app/equipment/models/__init__.py` | 两个新实体及薄导出；保留旧3实体同class/同Table，不改`models/equipment.py`。 |
| `backend/app/equipment/crud/async_temperature_sample.py`、`backend/app/equipment/services/async_temperature_sample.py`、`backend/app/equipment/temperature_sample_domain.py` | 唯一新async写读事务与纯规范化规则；不改旧async_equipment/sync_*。 |
| `backend/app/equipment/config.py`、`backend/app/equipment/error_codes.py` | 一个模块本地scope配置、自有StrEnum；不加机器身份或设备管理。 |
| `backend/app/module_contract.py` | 仅PUBLIC_SYMBOLS的settings项补已存在resolve_env_file；不增业务字段/错误/legacy清单。 |
| `backend/app/MODULE_CONTRACT.md`、`backend/app/MODULE_CONTRACT.zh-CN.md` | 仅同步上述公共helper、模块本地配置边界及真实运行gate，不重写v1其他合同。 |
| `backend/.env.example`、`backend/.env.docker.dev.example`、`backend/.env.docker.prod.example` | 仅增一个空scope及英文说明；原英文大标题/注释、grants/值全留，不写任何真实env。 |
| `backend/alembic/versions/20261016_1600_e4f6a8b0c2d4_add_equipment_temperature_samples.py` | 唯一d2后继，限两表及其约束/索引；旧4迁移不动。 |
| `backend/tests/test_equipment_temperature_{api,service,migration,config}.py` | no_db公开输入/权限/兼容/事务与迁移静态/配置测试；不改公共DB fixture。 |
| `backend/tests/test_module_contract.py` | 只补helper公共入口、签名/路径及私有设置仍拒绝的定向证据，保留其余原合同断言。 |
| `backend/tests/module_admission_fixtures.py` | 仅给generate_full_profile增加显式的profile名称/表数/目标revision元数据参数供本任务使用，并允许run_python将显式UV_CACHE_DIR/PYTHONPYCACHEPREFIX指向本任务tmp；不改C0/C2/E组成、DB拒绝guard、原F/58默认或其历史事实。 |
| `backend/tests_mysql/test_equipment_temperature.py` | 独立显式MySQL8.4.6迁移/POST→GET/约束/并发/回滚入口，不依赖共享破坏性conftest；执行另批。 |
| `backend/app/equipment/README.md`、`backend/app/equipment/README.zh-CN.md`、`backend/app/equipment/PLAN.md`、`backend/app/equipment/PLAN.zh-CN.md`、`backend/app/equipment/plans/README.md`、`backend/app/equipment/plans/README.zh-CN.md` | 稳定模块说明及本根任务的索引链接；不另造第二Task ID或复制spec正文，PLAN/catalog由协调者依角色事实机械同步。 |
| `backend/README.md`、`backend/README.zh-CN.md`、`backend/app/README.md`、`backend/app/README.zh-CN.md`、`CODE_INDEX.md` | 仅新旧温控来源、两表/迁移、permission/scope/public helper说明及结构索引；配置逐项表与新增key数量同步。 |
| `plans/ARCH-BE-003-mapping-service-api-pilot/tasks.md`、`plans/ARCH-BE-003-mapping-service-api-pilot/checklist.md` | Development在精确批准后才创建tasks；fresh-context Verification在developer_handoff后才创建checklist，各写所属面。PM不预建。 |

根/backend PLAN pairs、根plans catalog pairs继续由主协调者机械同步。现有七package入口已经存在，
不为对称新增无用mock/seed/导出，不新增第9个descriptor。
禁止修改settings.py、Core deps/registrar/role resolver、app/router、module_registry/module_preflight、
database/engine、common错误/响应、Projection/runtime、旧Models/Services/CRUD/GET、旧任务bundle、
前端/AW/CA/PLC、依赖/lock、Compose/CI/打包或共享测试conftest。
现有BE005四revision/58表和C2/E回归已使用有界子集，不必为新两表改成全仓永久60表上限或削弱原断言。
若真实实现仍需越界，先回PM新Revision，不能用“全量测试通过”理由扩写。

## 既有测试与fixture的精确影响

本轮只读确认`test_business_module_migration.py`和`test_business_module_reintegration.py`只重放原
四revision，要求58表签名与当前metadata对应子集一致；Core/价格测试同样验证自己的14/16表子集和
单root/head。新增两表无需修改这些旧断言、旧任务bundle或QA证据，也不能把其58改成60替代保护。
新`test_equipment_temperature_migration.py`单独重放五条链：原四条达到58，追加本后继达到60，撤第五条
仅去两表而恢复原58完整签名；精确核对四旧revision指纹、五条接链、唯一root/head及新约束。

现有`generate_full_profile`复制调用时全树但把profile.json硬记为F/58；BE003不得把含新表的副本继续
冒称BE005的58表F证据。其上述窄参数扩充后，本任务显式标记`profile=BE003`、expected_table_count=60、
target_revision=e4f6a8b0c2d4，输出独立task/source指纹；旧F/58只用于冻结的BE005源码，不能将新表
去掉后跑缩减套件。C2/E仍保留14/15/16表与原清理/接入负例，公共helper的加法patch如实反映在新指纹。
BE005两个tests_mysql入口的F/58/逐库ACK保持，BE003真实B只运行自己的入口及专用schema。
新源码阶段及嵌套uv子进程的cache/pycache显式落本任务tmp，保留原DB拒绝guard与测试选择，
不复用/重建已清理或仍承担证据用途的BE005资源。

# 验收标准与独立验证

下表是r3获批后的交付要求，**不是本轮已执行证据**。A为公开源码/no_db阶段，B为另批的真实MySQL阶段；
Development self-check与fresh Verification结果分别写自己的权威文件。

| AC / 需求 | 必需证据 |
| --- | --- |
| AC-001 / R3-001 | A：新旧Model/GET/Service归属与diff；旧3GET及响应/limit既有行为、8descriptor和本地business+cursor+audit回归保持。B：预置旧温控行/原58表代表记录，经新POST和迁移后旧GET结果与校验和保持；新GET只回新表，旧前端无自动改源。 |
| AC-002 / R3-002 | A：真实ASGI原始JSON覆盖10项/0、未知/重复字段、snake_case、缺失/null/bool/字符串/非有限数、质量、时间时区/等价瞬间/毫秒/非零高精度尾数及技术边界；断言真实HTTP、camelCase和稳定错误。B：精度/0/所有10项逐值POST→GET按recordId读回，不只stub。 |
| AC-003 / R3-003 | A+B：同投递重放、同id异payload、不同id同业务键同/异值、不同actor/token刷新、跨设备/空scope矩阵。B：真实数据库两个unique及独立session并发首次相同/冲突投递，最终样本/receipt条数、原值/recordId稳定，不只串行先查后插。 |
| AC-004 / R3-002..004 | A+B：同小时多时刻全部保存、晚到旧样本保留、GET实际limit/来源排序/精确recordId/空态；不同timezone表示的同一毫秒冲突一致，UTC和毫秒真实读回。原旧GET不参与新current。 |
| AC-005 / R3-004 | A+B：对业务写、receipt持久审计、flush/commit分别注入失败，全事务回滚；已提交后故意丢响应再同sampleId重试得到原recordId；无孤立receipt或失败成功响应。async链无同步DB I/O，CRUD不commit。 |
| AC-006 / R3-004 | A：一条新后继单head、五条接链、两表Model/Schema/recorder/offline DDL签名一致；原四条58表子集断言不改，新BE003 profile明确60表/e4来源，C2/E原14/15/16及旧4迁移字节保持。B：空库base→新head以及d2带合成旧数据→新head，60表完整约束/索引/精度反射一致、旧记录不变；获批可丢弃副本中downgrade仅撤2表并再upgrade。MySQL DDL非事务，失败传播不冒称中途DDL自动回滚。 |
| AC-007 / R3-005..006 | A+B：新接口无/坏/过期/refresh/revoked/inactive身份401；非admin即使有ingest仍403；read-only/ingest-only/旧equipment/mapping/CA不能互授；两个admin的投递身份隔离；所有角色scope越界403；manifest disabled后新旧equipment整组404。未改真实grants或user行为。 |
| AC-008 / R3-005 | A：helper仅新增一个公共符号，源码/冻结路径签名正确、private-setting负例仍失败；模块本地显式参数/process env/合成dotenv优先级、空scope拒新API、不创建跨应用缓存、三example空值/英文说明及双语文档一致。未读写真实env，Settings/private-setting规则字节保持。 |
| AC-009 / R3-006 | A：新的2条method/path独立声明、v1预检/冲突/exports/errors通过；模块StrEnum用共享BusinessException，真实HTTP401/403/409/422/500/503及DEBUG=True脱敏；旧全局HTTP200与其他API合同不变，JSON Lines只含受控必要字段。 |
| AC-010 / 全范围 | A：项目uv/lock环境完整no_db、触达compileall、现有模块/迁移/价格/Projection回归与文档链接/diff检查，未缩套件/删断言。精确批准Revision、增量指纹、命令/退出码/限制/资源交fresh Verification；B必需证据缺失时保留qa_blocked，不以A替代。Human Owner最终验收独立记录。 |

# 运行gate、风险、排除项与handoff

## 阶段与具体操作gate

1. 当前PM只交付本r3供审查；**唯一待Human Owner的业务/范围决定为精确`ARCH-BE-003 r3`批准**。
   Q-001至Q-005全部已收敛，不要求再选设备仓库、设计SQL或提供秘密。
2. r3批准后，由实际Development消费完整bundle、当前工作树/BE005最新交接，创建tasks；先在专属
   `/private/tmp`公开副本中用仓库uv/uv.lock、占位Settings、no_db/dependency override和DB连接拒绝
   guard执行A。schema/mock/Projection/bootstrap关闭；不把`TESTING=True`当隔离保证。
3. B执行前由协调者提交BE003自己的精确disposable MySQL8.4.6 project/container/schema/volume/
   loopback端口/受限账号身份、起始revision、合成fixture、命令、回退和专用资源清理清单供具体批准。
   不复用BE005或现有database-only的库/卷/账号，不读写真实env；秘密不进入spec、命令输出或仓库。
   真实API的认证与CRUD前先完成该场景所需Alembic到新head；旧head场景先准备合成旧记录再upgrade。
4. B只能使用独立显式tests_mysql入口，不进入现有tests/conftest的建库/GRANT/DROP/create_all fixture；
   实际并发/约束/回滚与旧数据保护用MySQL证明，SQLite/stub/offline不替代。具体操作批准未到可完成A，
   但本任务整体不能qa_passed/owner_accepted。BE005两轮授权不转移。
5. Development交精确developer_handoff后实际启动fresh-context Verification；独立复建/验证A及获准B，
   checklist记录verdict和未解gate，Human Owner最终验收仍待真实决定。资源归属/证据保留/清理由协调者
   按明确批准执行；QA不擅自回收其他任务资源。上线/真实设备写入/发布部署仍须后续独立授权。

## 风险与回退

- 新旧两数据源并存是明确兼容边界，旧页面不展示新数据；不能通过临时union、双写或停止旧writer
  “修复”这一设计。以后统一前端/读取或writer切换需另案，先核对部分采样和存量数据语义。
- 毫秒截断、case-insensitive唯一键、数值静默舍入和并发先查后插会损坏幂等；以规范化、DB unique、
  存储精度及独立session竞争/失败矩阵控制。回执只证明接收端去重，不承诺端到端exactly-once或断网队列。
- 公开resolve_env_file是本r3新增公共合同风险面：只公开原纯路径计算，不泄漏Core Settings私有字段，
  不承诺设置模块完全无导入副作用。模块本地配置与原.env来源/优先级须一致，避免shell-only配置分叉。
- 新样本持续增长，保留周期/分区/小时统计未定义；本任务不自动清理或承诺现场吞吐/长稳。
- 共享工作树含并行AW/Console与BE005；Development必须建立本任务baseline，PM/DEV/QA只写各自面，
  不reset/覆盖他人增量。profile为contract_only，bundle与diff审计是必要控制，不声称平台ACL/强制路由。
- 源码回退仅撤本任务增量；真实采用后的回退优先关闭新入口并保留两表数据/receipt、旧GET继续原链路。
  不以downgrade默认删除已投运观测；任何部署/停机/数据撤回需审查实际状态并另批。

排除其余7项HTTP ingest、旧温控表/部分upsert改造、小时覆盖或汇总、前端接入、设备目录/机器身份、
批量平台、通用receipt/audit、历史迁移/清理、现场物理阈值、外置mapping runtime/队列/ack/lease、
新采集writer、SMA/DAA实现、Celery/Redis/Worker、PLC raw绑定与控制命令、CA/PLC配置、
能源价格改造、依赖/锁/Compose/打包、未经具体批准的DB/Docker/设备操作、部署/发布/推送。

PM应用project-governance与aiis/CONTRACTS，只读参考backend-arch的分层、响应、数据库迁移、
MODULE_REGISTRATION、AUTH_SECURITY、DATA_GOVERNANCE、OPERATIONS_TESTING。
后续Development/Verification必须使用backend-arch上述适用references；新增结构/索引用
code-document-indexer；真正展示新增错误文案时才加载i18n-workflow。
本轮没有UI改动，不加载frontend-ui；B实际涉及Docker时再加载docker-expert与docker-project-ops。
新增backend/scripts、Rust runtime或PLC点位工作不在allowlist，需要新Revision并路由对应skill，
PM不替Development/Verification执行这些技术工作。

## 当前源码与角色证据入口

- 治理：[AGENTS](../../AGENTS.md)、[workflow](../../.codex/workflows/development-lifecycle-workflow.md)、
  [backend说明](../../backend/README.zh-CN.md)、[app说明](../../backend/app/README.zh-CN.md)。
- 回迁事实：[BE005 spec](../ARCH-BE-005-backend-business-module-reintegration/spec.md)、
  [Development](../ARCH-BE-005-backend-business-module-reintegration/tasks.md)、
  [Verification](../ARCH-BE-005-backend-business-module-reintegration/checklist.md)；后续B结论只以其新记录为准。
- 旧温控：[manifest](../../backend/app/equipment/manifest.py)、[三GET](../../backend/app/equipment/api/routes.py)、
  [Models](../../backend/app/equipment/models/equipment.py)、[async Service](../../backend/app/equipment/services/async_equipment.py)、
  [async CRUD](../../backend/app/equipment/crud/async_equipment.py)、[sync温控](../../backend/app/equipment/services/sync_temperature.py)、
  [sync CRUD](../../backend/app/equipment/crud/sync_temperature.py)、[原规范化](../../backend/app/equipment/services/_sync_common.py)。
- 公共合同：[v1](../../backend/app/MODULE_CONTRACT.zh-CN.md)、[机器符号](../../backend/app/module_contract.py)、
  [源码预检](../../backend/app/module_preflight.py)、[env路径helper](../../backend/settings.py)、
  [公开认证依赖](../../backend/core/deps.py)、[异常](../../backend/common/exceptions.py)、
  [共享响应](../../backend/common/response.py)、[全局handler](../../backend/core/registrar.py)。
- 事务与保护：[get_db](../../backend/database/session_async.py)、[Projection runner](../../backend/projection/runner.py)、
  [d2迁移](../../backend/alembic/versions/20261014_1600_d2f4a6b8c0e2_reintegrate_business_module_schema.py)、
  [58表回归](../../backend/tests/test_business_module_migration.py)、[测试fixture风险](../../backend/tests/conftest.py)。
  以上均为本轮静态读取，未运行App、项目测试或在线验证。

## 修订与批准轨迹

| Revision | 日期 | 记录及有效状态 |
| --- | --- | --- |
| r1 | 2026-10-12 | 原8项API缺口盘点draft，未取得精确实施批准；正文随r2历史保留。 |
| r2 | 2026-10-14 | 仓库/10项/单设备身份/admin写入/隔离MySQL四问已答；小时分析完成但Q-005及整份r2未批准。原文SHA256 `c402a2ff931847d134ef0d2be7b63d28ab12630c8b72fe270be4dc39657fa1e6`，下方逐字保留，不作为当前基线。 |
| r3 | 2026-10-16 | Human Owner确认逐样本保存，授权STD修订spec并要求先确认。本r3更新回迁后的GET/Models/d2基线，裁定独立两表/读回、完整样本/receipt事务与并发/权限/局部HTTP合同，拟公开现存env路径helper；**draft/pending exact Human Owner approval**，无实现/测试/运行授权。 |

PM -> Human Owner：审查并批准精确`ARCH-BE-003 r3`后，才移交实际Development。
本轮没有其他待决业务项；后续具体运行批准与最终验收按上述独立gate，不由本draft授予。

PM规格自检只检查本文件metadata、39个相对文档/源码链接、旧r2原文字节SHA和staged role文件仍缺省；
`python3`文档检查与`git diff --check -- plans/ARCH-BE-003-mapping-service-api-pilot/spec.md`均exit0。
这不是项目技术测试、Development self-check、独立QA或运行证据。

---

# r2 历史草案（以下原文逐字保留，含r1盘点；已由上方r3替代，不单独生效）

Task ID: ARCH-BE-003
Revision: r2
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: pending；位置与四项业务选择已确认，已补小时覆盖分析；Q-005温控逐样本/小时代表值待决，r2为spec-only draft，完整范围批准后再交Development

Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 现有 Projection 目标 Service 的业务写 API 缺口盘点及设备温控采样试点契约
Owner: aiis-ics-arch 可复用 equipment 温控采样切片
Acceptance Chain Reference: ARCH-BE-003 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Related Task: ARCH-BE-002, ARCH-BE-004, ARCH-MULTI-001
Workflow Mode: STD
Execution Mode: agent_team_same_session
Role Separation: PM -> Human Owner scope approval -> Development -> fresh-context QA / Verification -> Human Owner final acceptance
Fresh Context: required after developer_handoff
Created: 2026-10-12
Updated: 2026-10-14

# 目标与当前授权

Human Owner 在 r1 盘点后明确：“继续 ARCH-BE-003，就在当前仓库的 backend/app/equipment 中实施。
先按 STD 梳理采样字段、设备标识、权限和验证环境需要我确认的事项，再更新 spec，暂不改代码。”
本 r2 记录已经确定的实施位置、Human Owner 四项业务答复和后续最小合同；没有 API、Schema、数据库、
映射发布或运行切换的实施授权。四项答复确认业务选择，不构成对尚待提交的完整 r2 Revision 的范围批准。
新增 API 面向第三方与后续映射 Agent，接收其已转换好的业务采样记录；现有 backend 映射机制、
descriptor、同步 Service 调用和本地 business+cursor+audit 事务保留。外部调用方本身不在本次实现内。
本任务不继承其他任务批准；[ARCH-BE-002](../ARCH-BE-002-energy-price-api/spec.md) 的能源价格
current/history/create 属于独立辅助管理能力，不是这八个采集 handler 的写入入口，也不阻塞本试点。

当前写入面仅本 `spec.md`；主协调者机械同步所属双语 PLAN / catalog。PM 不创建 tasks/checklist。
当前根 AGENTS 与 README 已允许可复用领域模块；本次位置选择沿用该边界，限定公共温控采样切片。
不再要求重新选择消费仓库，也不重复要求定位变更批准；客户规则、真实设备标识/数据、旧设备全模块
恢复仍不在范围内。下述实现 allowlist 只有精确 Revision 获批后才生效。

## r2 当前事实与业务答复

| 事项 | 当前状态 |
| --- | --- |
| 仓库与 owner | **已确定**：`/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend/app/equipment/`，只做可复用温控采样切片。 |
| 本轮写入 | **已授权**：PM 修订本 spec；主协调者机械同步索引。当前 bundle 只有 spec，不预建 tasks/checklist。 |
| 四类决策 | **已确认**：Q-001十项完整°C采样记录；Q-002单设备key/来源持久sampleId/含时区毫秒时间/异值409；Q-003写API admin-only且强制设备scope/独立ingest；Q-004预留隔离MySQL8.4.6验证。 |
| 新增小时分析 | **待决定Q-005**：已分析九类数据；温控推荐保留逐采样记录，小时代表值/聚合不默认实施，不把用户要求分析解读为全部数据小时化。 |
| 后续实施 | **未授权**：提交完整 r2 给 Human Owner 精确范围批准，再交 Development；独立 QA 和最终验收分别经过后续 gate。数据库/容器具体运行目标仍另行授权。 |

r1 的 2026-10-12 八项盘点保留为历史依据，以下盘点表不重复制作。r2 于 2026-10-14 只读复核：
当前 HEAD 仍为 `363b297bffe65e020108f5504766b4fb1ec3b381`，工作树已有其他任务的多项未提交改动，
不以 HEAD 代表全部当前源码；当前仍无 `backend/app/equipment/` 或温控 GET。旧源 HEAD 仍为
`49e7f1798111154a52f1aadd33075b556659168c`，equipment 目录无 dirty diff；温控的部分 upsert、
默认零值和只读 GET 行为与下表一致。未读取真实 env、DB、Docker、已发布映射或现场。

当前迁移源码链为 `d4e6f8a0b2c4`（原十四表 Core root）→ `a6c8e0f2b4d6`（energy_prices）→
`b8d0f2a4c6e8`（energy_price_hours）；完整 metadata 已为十六表。此事实来自当前迁移文件与静态
测试源码，不是本轮执行迁移的结果；r1 的十四表时点不覆盖后继变化。

新增写 API 不必然改表；是否迁移取决于现有表能否承载合同。本仓库目前没有温控表，本草案选择
持久采样与receipt/唯一约束，因此后续实施包含显式schema增量。隔离MySQL仅用于验证这些新增表、
并发和回滚，不是接口必须另配一个运行数据库，也不表示现在操作现有数据库。

# r1 盘点依据与证据等级（2026-10-12 历史）

本次于 2026-10-12 只读核对两个源码树：

| 对象 | 本次确认 | 限制 |
| --- | --- | --- |
| 当前 `aiis-ics-arch`，HEAD `363b297bffe65e020108f5504766b4fb1ec3b381` | `backend/app/` 无业务 `projection_handler` 声明；保留 Core Registry、mapping 控制面和 runner 宿主。 | 不能把旧源 handler 称为当前 Core 的 active handler。 |
| 旧源 `/Users/jason/Desktop/DreamCode/vibe-l2-front-end`，HEAD `49e7f1798111154a52f1aadd33075b556659168c` | README 声明归档迁移；相关 equipment/performance/monitor 源码目录无 dirty diff。检出 8 个 descriptor，均经 `run_projection_handler` 调用下表同步 Service。 | 只作兼容与试点候选材料，未写旧仓，也未据此选择继任项目为实施目标。 |
| 数据库与运行环境 | 未读取真实 `.env`、数据库、已发布 mapping revision、runner 状态或现场。 | 当前实际发布哪些映射、哪些启用、输入绑定和真实触发频率均未知；8 项是源码可声明目标清单。 |

Registry 只扫描 enabled manifest owner 下 `services/sync_*.py` 导出的 descriptor；文件存在不等于
映射已发布。八项均声明 `snapshot_source="raw"`，由 primary raw 观察触发；部分 handler 可使用
policy-derived latest 辅助输入，这不把触发语义变成 latest 事件。当前 runner 在本地同一 Session 内
执行 `descriptor.invoke`，随后提交业务写、cursor 和 runtime audit；本试点保留这条本地事务链。

## 八个目标的 API 缺口

下表路径均相对上述旧源 `backend/app/`；“需补”指未来通过 HTTP 接收映射结果所需的独立业务入口，
不表示八项均进入首批实施。所有同步 Service 只 flush，提交/回滚由 Projection host 负责。

| Handler → 实际 Service | 输入、持久化与业务副作用 | 现有 API 与等价判断 | 建议 |
| --- | --- | --- | --- |
| `equipment.sync_temperature` → `equipment/services/sync_temperature.py::sync_temperature` | `timestamp` 可省略并取 collected_at；10 个 zone1–5 set/act 可选数值。good quality 且至少一项测量；按 timestamp 查找并新增/更新 `equipment_temperature`，仅覆盖非空字段；返回 action/record_id，坏质量/无测量可 skipped。 | 仅 GET `/equipment/temperature-control`，没有写 API。 | **首批试点**：温控采样写 API；区分旧部分字段 upsert 与本草案建议的完整采样记录合同。 |
| `equipment.sync_drive` → `equipment/services/sync_drive.py::sync_drive` | timestamp + 20 项工艺/张力数值；good quality、至少一项；按 timestamp upsert `equipment_drive`，仅覆盖非空字段；返回 action/record_id/skipped_reason。 | 仅 GET `/equipment/drive`，没有写 API。 | 后续需独立驱动采样入口；字段较多，复用试点经验后再立范围。 |
| `equipment.sync_production_parameters` → `equipment/services/sync_production_parameters.py::sync_production_parameters` | 必填 coil_no；可选 timestamp、grade、entry_time、thickness/width/total_time/weight/speed；按 coil_no + timestamp upsert `equipment_production_parameters`；新增 process_steps=[]，不自由映射工序 JSON；返回 action/record_id/skipped_reason。 | 仅 GET `/equipment/production-parameters`，没有写 API。 | 后续需设备生产参数采样入口；它不等同于生产实绩创建或总生产用时。 |
| `performance.sync_production_record` → `performance/services/sync_production_record.py::sync_production_record` | 必填 coil_no、13 项可选主表字段；按 device + coil 更新 `performance_main`，处理 in_production/not_in_production/unknown、同卷重激活与前卷退出，raw id 防旧事实回放；派生总用时、保留人工重量优先级；返回 action/performance_id。不读写 Plan。 | POST/PUT `/performances` 是人工记录/修改；async create 固定 manual_entry，重量走 manual_override。它没有等价的来源顺序、观察状态流转和 raw 幂等合同。 | 后续需独立“生产观察”API，不能直接复用人工 CRUD、push-down、split/merge 或 Plan API。 |
| `performance.sync_process_temperature` → `performance/services/sync_process_temperature.py::sync_process_temperature` | 必填 coil_no/zone；set_temp/max_temp/min_temp/avg_temp/duration 至少一项，record_time 可省；先锁定已存在父 Performance，再按 parent + zone + record_time upsert `performance_process_temperature`；返回 action/performance_id/record_id。 | GET `/performances/{id}/process-data` 只有读面；无对应过程采样写 API。 | 后续需温度过程采样入口；父实绩缺失与晚到顺序须另定，不在试点自动创建父记录。 |
| `performance.sync_process_tension` → `performance/services/sync_process_tension.py::sync_process_tension` | 同上父记录/zone/record_time 键；set_tension/avg_tension/max_tension/min_tension 至少一项；upsert `performance_process_tension`，返回 action/performance_id/record_id。 | 同上过程数据查询，无等价写 API。 | 后续需张力过程采样入口。 |
| `performance.sync_process_speed` → `performance/services/sync_process_speed.py::sync_process_speed` | 同上父记录/zone/record_time 键；set_speed/avg_speed/max_speed 至少一项；upsert `performance_process_speed`，返回 action/performance_id/record_id。 | 同上过程数据查询，无等价写 API。 | 后续需速度过程采样入口；虽字段少，仍依赖父实绩。 |
| `monitor.sync_process_curve` → `monitor/services/sync_process_curve.py::sync_process_curve` | 可选 coil_number + 12 项整数温度 + 21 项数值测量；good quality 且至少一项；每次追加 `monitor_history_process_curves`，created_at 取来源 collected_at，Service 自身不按 raw id 去重；返回 action/record_id/skipped_reason。 | GET `/monitor/temperature` 和 `/monitor/energy` 为曲线/聚合读面；无曲线追加写 API。 | 后续需历史采样追加入口及持久去重；不能沿用仅靠 runner cursor 的防重方式处理 HTTP 重试。 |

旧设备表 timestamp 只有普通索引，三种过程子表也没有上述复合业务键的 unique 约束；锁定查找
已有行不能据此证明并发首次插入安全。设备模型测量字段还有 `default=0.0`：缺失观测落成零值与
“实测为零”不同。上述缺口是新 API 必须收敛的规则，不能因旧 Service 有同步方法就忽略。

## 试点选择

选择 `equipment` 模块的温控采样切片：一张表、10 个平铺字段、无父 Performance / Plan / 能源价格
依赖，并已有温控查询可验证读写闭环。drive 有 20 项测量；production_parameters 有卷号/工序边界；
performance 主表有状态机和人工覆盖规则；三种 process Service 依赖父记录；monitor 曲线有 33 项
测量且为 append，HTTP 去重改造面更大。

旧 `B6.10 r1` bundle 只有 spec/tasks：Development 已交接，checklist 尚不存在；不能称其已独立 QA
或最终验收。本次只确认源码行为，不继承该任务批准，也不对真实点位、单位或数据完整性作证明。

# r2 试点合同（业务选择已确认，精确范围待批准）

这里“完整采样记录”指同一采样时刻的十项温度，不是映射配置，也不是一次映射发布。
下列防重合同仍按逐采样保存；Q-005小时策略决定前不将它改为覆盖同小时其他时刻的值。

## R-001：一个业务写入口

建议新增 POST `/equipment/temperature-samples`，完整 URL 使用当前 `API_V1_PREFIX`（公开示例为
`/api/v1`）。当前仓库没有温控 GET；建议只引入旧路径 GET `/equipment/temperature-control` 的
最小真实读面以验证闭环，不称为保留当前已有接口，不复制旧 drive/production-parameters API。
入口只接受已经映射为业务含义的观测数据，不轮询
PLC、不接受 PLC 地址/DB 编号/offset/bit/group 或任意 handler import path，不替设备下发温度设定。
`zoneNSet` 仅表示观测到的设定温度，不是控制命令。

| 请求字段 | r2 合同 |
| --- | --- |
| `equipmentId` | 必填稳定业务 key；首批一个可配置逻辑设备，文档/测试示例 `temperature-pilot-01`。不依赖不存在的设备目录，也不把 PLC key / raw device_id 当业务身份。真实 key 由后续运行设置，不写入公开源码。 |
| `sampleId` | 来源侧在首次投递前产生并持久保持的非空、不透明采样标识；重试不变，服务端不按到达时间重新生成。作用域为稳定 User.id + equipmentId，token 刷新不改变该身份。 |
| `sampledAt` | 必填来源采样时间，ISO 8601 且含时区，归一化 UTC；毫秒精度，超过三位的非零小数拒绝而不截断。不用 HTTP 到达时间代替；同一时刻的不同时区写法归一为同一键。 |
| `quality` | 首批只接受稳定 key `good`；其他质量不写温控业务表，返回明确 422 / 稳定错误 key。 |
| `zone1Set` / `zone1Act` 至 `zone5Set` / `zone5Act` | 首批 **10 项全部必填的完整采样记录**，单位 °C，有限且可持久化的 JSON number，0 有效；缺失/null/bool/数字字符串/NaN/Infinity/未知字段拒绝，不补零。 |

完整采样记录是**Q-001 已确认**的首批缩窄合同：旧 handler 支持同 timestamp 合并部分字段；新 API 首批
不提供部分 patch 或未知值占位。未来若来源只能提供部分 zone，先由 PM 修订覆盖、unknown/null、读面兼容
和验收口径，不能由 Development 暗中补零。不要求本轮提供真实 PLC 值或工艺上下限；DEV 选择
能够无静默溢出/舍入的存储与规范化方案并说明精度，不擅加客户温度范围或裁剪观测。

成功统一使用目标项目共享 `code/message/data`，`data` 至少含 `recordId/equipmentId/sampleId/
sampledAt/outcome`，outcome 为 `created` 或 `duplicate`。相同采样的重试返回原 recordId，不追加
第二行；外部业务 API 使用真实 HTTP 状态，成功建议 200，认证401、无权403、校验422、冲突409，
系统失败5xx，失败有稳定 errorCode。复用共享响应；当前全局 BusinessException 返回 HTTP200，
HTTPBearer 缺 token 可能返回403，不能直接当作本集成 API 的目标语义。DEV 在本切片的 API adapter
内局部适配 401/403/409/422 及稳定错误 key，不改共享认证/全局异常对既有接口的行为。
Service/CRUD 不导入 HTTP 对象。内部 snake_case、wire camelCase 由后端负责。

建议 GET 只读取获批设备：可省 equipmentId 并使用唯一配置 key，显式传入其他设备仍403；limit
为1–1000且实际生效。保留 `heatingZones` 五项 `setTemp/actualTemp` 与 `temperatureHistory` 的
`time/zone1…zone5` 命名，并为历史项附加完整 `sampledAt`，不以仅时分秒判断业务键。按 sampledAt
降序选择最近 limit 行，历史展示再按升序；无记录返回两空数组，不 seed、不补零、不生成 mock。
此为新温控读面合同，未证明旧前端全部兼容，也不包括前端接入。

## R-002：两种身份与持久防重

- 投递身份为“认证写入主体 + equipmentId + sampleId”；业务采样键建议“equipmentId + sampledAt”。
  两者分别受数据库唯一约束保护；请求规范化后计算 fingerprint，包含设备、采样时间、质量和十项值。
- 相同投递身份、相同 fingerprint：返回已提交结果，不重复写入。相同投递身份、不同 fingerprint：
  409 `temperature_sample_id_conflict`，原行和原 receipt 不变。
- 不同 sampleId 命中同一业务采样键：相同采样内容可返回原 recordId 并记录该投递 receipt；不同采样内容
  默认409 `temperature_sample_time_conflict`。首批不隐式覆盖已保存的观测；修正采样另立业务规则。
- 不同采样时间的晚到采样记录正常保存；查询按来源采样时间排序，晚到旧样本不取代时间更晚的当前值。
  禁止用 Python 进程内字典、缓存或“先查后插”作为并发唯一保证。
- equipmentId/sampleId 精确、区分大小写匹配；数据库 collation/unique 不能把两个不同标识合并。
  fingerprint 使用规范化后的时间、质量与数值；数值1/1.0及等价时区应得相同语义，禁止按原始 JSON
  字节或 token jti 判重。DEV 选择 hash、键长和并发冲突恢复策略，必须用公开行为矩阵验证。

这比旧温控 Service 的部分字段 upsert 更窄，**不能作为旧 handler 已完成一对一替换的证明**。
未来迁移必须另行核对部分采样、同时间修正、跨设备身份和历史数据语义。

## R-003：事务、归属与兼容

- API 使用 async Service -> async CRUD -> AsyncSession。不能在 async def 中直接调用旧同步 DB
  Service，也不能伪造 PLC provenance 来绕过旧 handler；纯业务规则可按批准范围提取复用。
- 同一数据库事务原子提交温控业务行、幂等 receipt 和必要业务审计；任一失败全部回滚。receipt
  保存原结果、fingerprint 和来源身份。服务端接收/创建时间取数据库时钟，与 sampledAt 分开。
- 持久化归本仓库 equipment owner；建议仅新增温控样本与模块内 receipt 两张表，receipt 同时保留
  actor、原结果、fingerprint、数据库接收时间等必要持久审计，不建设通用 receipt/audit 平台。
  沿用温控领域字段含义，补业务设备键和唯一约束，不照搬旧表默认零值。当前不迁移任何旧数据；
  旧表无设备键、无 unique、可能有时间重复，不能借新表任务擅自清理/回填旧库。
- Schema 仅新增 `b8d0f2a4c6e8` 后的一条显式 Alembic successor，不改十四表 root 和已存在两条
  价格迁移，不复制旧迁移图、不用 create_all/stamp。Model/Schema/migration 同步，已有十六表
  的结构与数据保持。import、Registry、启动和 GET 不执行 DDL、seed 或默认值写入。
- 读后验证使用 mock-off 的真实业务读链；不把 mock 样例或 stub 的 HTTP200 当作落库闭环。

## R-004：权限与第一阶段边界

manifest 声明独立写权限 `equipment-temperature-ingest`；最小 GET 建议独立读权限
`equipment-temperature-read`。读权限不自动获得写入权，页面 pageId、
mapping 管理权限和 CA gate token 也不授予该权。复用目标项目认证与权限机制，显式限制设备范围；
当前认证主体是 User access-token；权限策略为 admin 恒权与 supervisor/operator 角色数组，
没有机器身份或设备授权目录，也不能通过角色数组只授权某个指定用户。

Q-003 已确认首批仅 admin 调用 POST，并复用现有 require_permissions 与 admin guard；
supervisor/operator 即使测试配置中人为加入 ingest，首批也不得绕过写入的 admin-only 边界。
GET 按独立 read permission 检查，不把“写入admin-only”的业务答复扩大为已确认的读取角色限制；
两角色默认均不自动增加read/ingest grants。所有调用者包括 admin 仍经过设备范围检查，仅允许
唯一配置 key。最小新增非秘密设置
`EQUIPMENT_TEMPERATURE_PILOT_ID`，安全缺省为空（未配置时拒绝读写），公开示例使用
`temperature-pilot-01`；不默认启用真实设备。具体 key 和运行 grant 由后续 gate 设置。
不改通用 role resolver/user 表，不新建机器账户、设备管理 CRUD 或完整授权系统。未来开放非 admin
写入须先明确角色/设备范围并修订规格；仅声明 ingest 不意味着本阶段已允许配置开放写入。

第一阶段只准备目标项目 API 和隔离验证。现有 Projection 继续本地调用、提交业务+cursor+audit；
不在 descriptor.invoke 内调用 HTTP，不发布真实 mapping，不启用并行写入。本地 Projection 与新
API 不得同时对同一获批试点目标承担有效业务写入。开发验证只使用唯一标识的隔离目标。

未来外置 mapping runtime、HTTP 投递、持久队列、重试/ack/lease、单 writer 切换和旧 handler 退休
另立获批任务。HTTP 目标提交无法与原本地 cursor 共用 SQL 事务；新 API 有 receipt 也不表示已经
实现端到端 exactly-once、断网恢复或切换安全。

# 后续实施验收标准

以下基于已确认业务选择及本 r2 完整合同；本 r2 不宣称已获范围批准或已经执行。

| 标准 | 必需证据 |
| --- | --- |
| AC-001 / R-001 | 真实 ASGI JSON 与最小温控 GET：10 项温度、零值、时区/毫秒精度、质量、未知字段、缺失/null/bool/数字字符串/非有限数失败；GET设备/limit/空态/来源时间排序；禁止 PLC 技术字段和伪造来源。 |
| AC-002 / R-002 | 同投递重放、同id异payload、同业务键同/异采样内容、并发首次投递、晚到样本矩阵；数据库唯一约束与 receipt 保证单记录、稳定recordId，不只测串行查找。 |
| AC-003 / R-003 | 对业务写/receipt/审计分别注入失败，证明原子回滚；commit 后丢响应再重试仍取原结果；async 请求链不执行同步 DB I/O。 |
| AC-004 / R-003 | 模型/Schema/migration 一致、新successor单head及offline SQL；保留原十四表root及价格两后继；获批可丢弃MySQL中的upgrade/downgrade、并发及读后写验证；无隐式seed/DDL，未改旧库。 |
| AC-005 / R-004 | 无/坏/过期/refresh/撤销token、禁用用户401；非admin POST即使有ingest仍403；GET独立read矩阵；所有角色设备越权/空scope403；disabled manifest404；读/ingest不互相授权，真实env/grants未改；只写温控行与receipt审计。 |
| AC-006 / R-004 | diff 与隔离测试证明原 Projection 本地事务不变，无 HTTP handler 替换、真实映射发布、runner启动、并行writer、CA/PLC操作或部署。 |
| AC-007 | Development 记录精确批准Revision、增量diff、命令/退出码/环境限制；fresh-context Verification 独立验证并写 verdict，Human Owner 最终验收另有真实记录。 |

源码验证使用目标项目 uv/lockfile、显式占位配置、no_db/dependency override；真实持久化、并发与
migration 证明需要另批唯一标识的可丢弃数据库及清理方案。TESTING=True 不是隔离保证；不能以
stub/SQLite/source-only 结果冒充目标数据库验证。必要运行证据缺失时保留明确 gate。

## 最小实现 allowlist（待精确 r2 范围批准后生效）

下表花括号仅表示列出的有限文件集合；`README.*`/`PLAN.*`只指英文`.md`与`.zh-CN.md` pair。
仅这些路径可用于后续实现，不授权写整个 backend 或复制整个旧 equipment。

| 文件/边界 | 后续候选用途 |
| --- | --- |
| `backend/app/equipment/__init__.py`、`manifest.py` | import-safe 普通模块与两项permission；只暴露本温控POST/GET，无Projection descriptor。 |
| 该模块 `api/{__init__,routes,temperature_samples}.py` | 聚合与局部HTTP适配、现有认证依赖、admin/设备范围边界。 |
| 该模块 `schemas/{__init__,temperature_sample,temperature_query,temperature_out}.py` | 分离采样输入、查询与输出。 |
| 该模块 `models/{__init__,temperature_sample}.py` | 仅样本与receipt两实体，稳定唯一键/时间精度。 |
| 该模块 `crud/{__init__,async_temperature_sample}.py`、`services/{__init__,async_temperature_sample}.py` | 只创建真实async通道；事务/防重/查询/脱敏日志。 |
| 该模块 `mocks/__init__.py`、`seeds/__init__.py` | 固定package，只有无副作用入口，不实现mock/seed。 |
| 该模块双语 `README.*`、`PLAN.*` 与 `plans/README.*` | 稳定切片/验证gate及本任务链接；不另建第二Task ID或复制任务正文。 |
| `backend/settings.py`、`backend/.env.example`、`backend/.env.docker.dev.example`、`backend/.env.docker.prod.example` | 仅增上述一个scope setting及安全示例；不读写真实env，不改已有key/grants。 |
| `backend/common/error_codes.py` | 只增本切片稳定业务错误key；不改共享异常/认证行为。 |
| `backend/alembic/versions/20261014_1200_c0e2f4a6b8d0_add_equipment_temperature_samples.py` | 只一条新revision，`down_revision=b8d0f2a4c6e8`；DEV开始前若head变动，先返回PM校正范围。 |
| `backend/tests/test_equipment_temperature_{api,service,migration}.py` | noDB合同/业务/迁移静态测试；真实并发测试只在另批隔离目标运行。 |
| `backend/tests_mysql/test_equipment_temperature.py` | 显式选择的真实MySQL验证入口，位于共享破坏性conftest作用域外；执行仍经过具体目标授权。 |
| `backend/tests/test_module_{registry,structure}.py`、`test_openapi_router_tags.py`、`test_celery_retirement.py`、`test_core_migration_baseline.py`、`test_energy_price_migration.py` | 仅适配已批准温控模块/两表/新head断言，保留其他客户模块禁入、原Core与价格parity检查。 |
| `backend/README.*`、`backend/app/README.*`、`CODE_INDEX.md` | 仅补公共温控切片、permission/scope/迁移边界；索引文件由主协调者按角色事实机械同步。 |

禁止扩大到 app/router、module_registry、core/deps、core/role_permissions、core/registrar、
Projection/runtime、旧源、前端、依赖、锁文件、Compose 或测试公共DB fixture。若实现发现这些边界
必须改，先返回 PM 修订；不能为了让全量测试通过而削弱原Core/安全/客户模块隔离断言。

## 验证环境与授权门槛

- **本轮**只检查规格metadata、链接和增量diff，未执行项目测试、DB访问、Docker或在线迁移。
- **源码阶段**：由后续获批Development使用仓库uv/lockfile、全部显式占位Settings、`no_db`
  和依赖override；避免加载本机真实env。当前conftest在非no_db用例会建库/用户/授权、DROP所有表
  再create_all，且test_client依赖DB fixture；不能直接用普通全量pytest或TESTING=True宣称隔离。
  新测试不得依赖共享破坏性fixture做迁移证明。
- **已预留真实闭环阶段**：一次性隔离MySQL8.4.6，仅合成温控数据和测试用户；经迁移准备全链schema，
  独立session真实并发、失败回滚、丢响应重放及POST→GET验证。SQLite或stub不替代该证据。
  Q-004已确认预留此阶段，不授权创建/启动Docker、建库、迁移、清理。执行前另给精确实例/库/
  volume/端口身份、可丢弃声明、权限、schema起点、命令与清理清单，由Human Owner授权具体动作。
- 具体运行授权尚未到达时，可先做已批准的源码阶段；AC-002/003/004的真实DB部分保持未验证gate，
  不标整个试点已具备并发持久化证明，也不据此跳过已预留的真实MySQL验证。
  PM无需口令或连接串；配置秘密仍由运行授权入口安全处理。

# Human Owner 业务决定、后续 gate、风险与 handoff

| 决定 | 推荐默认方案与解除条件 |
| --- | --- |
| Q-001 采样字段（已确认） | Human Owner选择五温区set/act十项完整°C采样记录，缺失/null拒绝、不补零。若未来只采部分，须PM新Revision，不沿用旧部分upsert。 |
| Q-002 设备与采样身份（已确认） | Human Owner接受单个可配置业务设备编号，文档/测试temperature-pilot-01；稳定sampleId、带时区毫秒sampledAt；同设备同时间异值409且不覆盖。真实key留作部署输入。 |
| Q-003 认证与权限（已确认） | Human Owner选择写接口首批admin专用并强制设备范围；独立equipment-temperature-ingest声明，supervisor/operator不授权写入。GET独立read权限为r2最小读面方案，待整份scope批准。 |
| Q-004 验证环境（已确认） | Human Owner选择预留一次性隔离MySQL8.4.6真实验证阶段；本轮不执行Docker/DB。具体运行目标与创建/迁移/清理动作仍另行授权。 |
| Q-005 温控存储粒度（新增待决定） | Human Owner追加要求分析哪些数据应同小时覆盖、跨小时新增。下表建议温控保留逐采样记录、小时统计另行定义；尚未指定温控按小时覆盖。若改为小时代表值，先明确代表值、来源时间/晚到覆盖和receipt冲突，再冻结实施合同。 |

上述业务选择由Human Owner本轮四问直接答复确认。模型类型与数值规范化、hash算法、
case-sensitive索引、事务竞争恢复和测试分层由DEV在已批准合同内选型并记录，PM不替DEV实施。
本r2已列具体migration文件与有边界allowlist；数值仅要求有限与可持久化，未定义现场物理阈值，
不要求用户提前设计SQL、提供真实设备key或报告口令。具体DB资源是后续运行目标，不是新增业务blocker。

## 同小时覆盖、跨小时新增的适用性分析

“小时”指选定业务时区的自然小时桶，例如10:00–10:59:59.999；不是距上一条记录滚动满60分钟。
只读复核旧源八类sync Service/CRUD及时间规范化链，没有把timestamp/record_time取整到小时的逻辑。
八类仍是旧源能力，不因本表而成为当前Core活动handler；当前能源价事实由主协调者复核现行源码。

| 数据类型 | 当前源码新增/更新键与行为 | 是否采用小时覆盖：分析建议，非本轮实施 |
| --- | --- | --- |
| 设备温控 `equipment.sync_temperature` | 精确timestamp相等时补写非空字段，换时刻新增；旧表不含设备键。 | **建议逐采样保留**，温控曲线依赖每个时刻；小时仅保留一行会抹掉波动和峰值。新API防重用业务equipmentId+sampledAt，见Q-005。 |
| 传动 `equipment.sync_drive` | 精确timestamp相等时补写非空字段，换时刻新增。 | **建议逐采样保留**，速度/张力变化不等于每小时一个值；如需小时统计应独立定义min/max/avg等。 |
| 设备生产参数 `equipment.sync_production_parameters` | coil_no+timestamp相等时补写非空字段，换卷或时刻新增。 | **建议保留卷号和采样时间**；同一小时可能多卷，不能按小时把不同卷或工艺阶段合并。 |
| 生产实绩 `performance.sync_production_record` | device_id+coil_no定位，按raw_snapshot_id防旧事实，更新在产/退出等生命周期。 | **不适用小时键**：同卷跨小时仍更新同业务对象；新卷即使在同小时也有独立记录。 |
| 过程温度 `performance.sync_process_temperature` | 找已存在的device+coil父实绩，按performance_id+zone+record_time补写/新增。 | **保留父实绩/温区/工艺时刻**；max/min/avg/duration是来源传入字段，源码未自动按小时聚合。 |
| 过程张力 `performance.sync_process_tension` | 同上父实绩+zone+record_time等值upsert。 | **保留工艺记录或已定义窗口**；不能把来源set/avg/max/min直接解释成自然小时统计。 |
| 过程速度 `performance.sync_process_speed` | 同上父实绩+zone+record_time等值upsert。 | **保留工艺记录或已定义窗口**；跨小时并不自动结束同一加工过程。 |
| 历史过程曲线 `monitor.sync_process_curve` | 每次追加；created_at取来源collected_at，Service自身无raw-id持久防重。 | **建议逐样本保留并单独补HTTP防重**；小时覆盖会丢曲线轨迹，不能靠hour桶替代重试幂等。 |
| 能源小时价格 `energy_price_hours` | 当前BE004：observedAt归上海自然hour_start，唯一hour_start；同桶整组覆盖，跨桶新增。current按observed_at<=now选值。 | **已采用小时覆盖**，是已验收价格阶段值合同；不扩成采集通用规则，不在BE003修改。 |

建议本试点保留逐采样温控记录；小时报表如需最新值、均值、极值，应基于明确定义的窗口另立范围。
若Human Owner选择每小时只保留一份温控代表值，需要确定业务时区、何种样本胜出（来源时间最新、
最后到达或统计值）、晚到旧样本是否覆盖、同小时多次sampleId的receipt如何返回原结果，以及同精确
sampledAt异值409是否保留。小时键可能需要新字段/唯一约束；这些与原逐时刻保存是实质合同变化。
本分析不启动小时迁移、不改原handler；Q-005和完整r2范围批准前不能进入Development。

主要风险：把源码候选当成已发布映射；把人工CRUD当采集语义；沿用零默认值伪造观测；跨设备/时间
精度碰撞；并发重复写；将HTTP调用放入原本地SQL事务后丢失原子性。以证据等级、完整采样记录、数据库
唯一约束/receipt、隔离验证和独立writer切换任务收敛。后续结构回退不得默认删除已投运观测或receipt；
保留业务数据后关闭新入口/恢复旧路径的操作须审查真实部署状态及单writer，并单独授权。

排除：其余七项API/旧设备整模块恢复、能源价格、前端整改、部分采样patch/改样、历史迁移与清理、
完整设备管理/机器身份/通用receipt平台、外置mapping runtime、采集配置、Celery/Redis/Worker、
依赖与Compose、未经后续具体授权的真实DB/PLC、发布部署；保留周期/自动清理另立范围。

PM 本次使用 `aiis`、`project-governance`，只读参考 `backend-arch` 的分层与响应边界。
后续 Development/Verification 必须使用 `backend-arch`，按需读取 RESPONSE_CONTRACT、LAYERS、
DATABASE_AND_MIGRATIONS、MODULE_REGISTRATION、AUTH_SECURITY、OPERATIONS_TESTING；稳定错误key
需展示时使用 `i18n-workflow`；真实结构变化使用 `code-document-indexer`。未触发脚本/Docker/runtime
实现时不加载对应技术skill。各角色仅写各自权威面，PM 不执行实现或独立Verification。

Q-005收敛后，PM提交完整 `ARCH-BE-003 r2` 给Human Owner精确范围批准，再进入Development。
后续需求/allowlist/验收/风险实质变化时提升Revision；四问答复不直接冒充完整Revision批准。
本profile是contract_only；主会话协调、任务bundle、diff审计仍是必要控制，不宣称平台ACL或强制路由。

## 源码复核入口

- 当前 [backend 边界](../../backend/README.zh-CN.md)、[Registry](../../backend/projection/registry.py)、
  [runner](../../backend/projection/runner.py)；当前Core没有equipment业务模块。
- r2认证/角色证据：[deps](../../backend/core/deps.py)、[role permissions](../../backend/core/role_permissions.py)、
  [registrar](../../backend/core/registrar.py)；测试隔离证据：[conftest](../../backend/tests/conftest.py)、
  [noDB ASGI前例](../../backend/tests/test_energy_price_api.py)；迁移/完整metadata证据：
  [Core基线静态测试](../../backend/tests/test_core_migration_baseline.py)、
  [价格后继静态测试](../../backend/tests/test_energy_price_migration.py)。以上为源码复核，未执行技术验证。
- 旧源八个handler为上表 `services/sync_*.py`，其 `projection_handler.invoke=run_projection_handler`；
  equipment与process子表的keys由同名 `crud/sync_*.py` 确认，共享规则为
  `equipment/services/_sync_common.py`、`performance/services/_sync_process_common.py`。
- API证据为旧源 `equipment/api/routes.py`、`performance/api/routes.py`、
  `performance/services/async_performance.py::create/update`、`monitor/api/routes.py` 及其子router；
  Model证据为 `equipment/models/equipment.py`、`performance/models/performance.py`；append证据为
  `monitor/crud/sync_process_curve.py`。旧 `backend/plans/B6.10-equipment-projection-handlers/` 已完整读取
  真实存在的spec/tasks；没有checklist，未补造。

## 批准与修订记录

| Revision | 日期 | 记录 |
| --- | --- | --- |
| r1 | 2026-10-12 | PM依据源码盘点与“选一个模块试点，落spec，不改代码”形成draft；精确实施范围批准、Development、独立QA和Human Owner最终验收均未发生。 |
| r2 | 2026-10-14 | Human Owner指定当前仓库equipment并确认四项业务选择；追加要求分析小时覆盖。PM修订spec-only draft、十六表当前链、allowlist/验收及九类更新策略分析；外部API与原backend映射隔离。Q-005温控存储粒度与完整r2范围批准仍pending；无代码、测试、env或运行写入。 |
