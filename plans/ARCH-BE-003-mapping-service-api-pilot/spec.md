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
