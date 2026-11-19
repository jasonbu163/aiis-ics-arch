Task ID: ARCH-OBS-001
Revision: r12
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已要求整理设备状态与过程监控操作手册；交命名 Development 按 §14 文档范围实施，随后 fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 配置驱动的设备状态、过程历史及独立能耗数据与统计
Owner: AIIS ICS Architecture
Acceptance Chain Reference: 本稿第 14 节与 Development Lifecycle Workflow；第 13 节为已批准 r11，第 12 节为已批准 r10，第 10 节为已批准 r8，第 11 节为未批准候选
Related Task: ARCH-ACQ-001, ARCH-ACQ-003, ARCH-ACQ-004 r4, ARCH-ACQ-005 r1, ARCH-TASK-001, ARCH-BE-010, aiis-ics-arch.aw.sma::SMA-004
Created: 2026-11-07
Updated: 2026-11-18

# 配置优先的设备状态与过程监控方案

> **版本提示：本次待审设计请阅读 [§12 r10](#r10-source-independent-energy)。标题后的原引言和 §1–10 保留历史设计与 r8 批准记录，§11 r9 是未批准候选；其中的采集事实、PLC 点位和任务证据依赖不是 r10 草案建议的准入要求；当前 r8 实现仍有相关限制，r10 尚未实施。r10 本身仍是未批准草案。**

SMA 和前端共用稳定的 `metricKey`，后端按写入目标和采样组把指标转成各自的本地槽位。采样按现场证据归属生产任务，设备状态四页查询当前任务的实时快照，过程监控单独追加需要长期保存的样本。管理员通过两个列表查看采集数据并补充管理信息。新项目优先通过设备、点位绑定、展示和历史采样配置接入，超出通用行为的需求再立模块范围。

## 1. 首版范围

本稿按从 0 到 1 的新建项目设计。首版按一个部署对应一个项目。项目先装配首版配置，实时快照和过程历史从空库开始。本文给出原理、物理表建议和候选接口供评审。DDL、OpenAPI 发布、软件实施及现场采用各有独立范围。

DAA 采集现场事实和任务归属证据，SMA 映射业务指标并通过两条写入接口分别投递实时快照和过程历史。后端校验并持久化，前端通过业务 API 查询结果。源码实施、受控验证和首次现场采用各有明确范围。 [AIIS 运行边界](../../README.zh-CN.md#运行边界) · [SMA 计划](../../automation-world/semantic-mapping-agent/PLAN.zh-CN.md)

一份来源样本只做一次业务指标映射。SMA 按目标发送同结构请求，后端按请求路径选择目标并找到该组各指标的本地槽位。实时按设备、任务及组保存最新快照，历史按来源采样逐次追加。读取时按各自绑定把槽位还原为指标键，再按当前名称、单位与展示配置呈现。两个值表各用一组 `local_values`，共享指标定义，各自分配槽位和写入，不设同步值组。

## 2. 设备状态四页

**R01** 设备状态查询外部上报的最新快照。四个页面共用查询接口、指标登记和同一个可配置卡片组件，按设备已确认的当前任务、页面和卡片绑定选择数据。

下表是建议的首版项目预设。工位、炉区和传动位置按项目已核实的点位配置。

| 页面 | `pageKey` | 建议卡片中英文标题与值 |
| --- | --- | --- |
| 生产参数 | `production` | 采用单指标卡片。「卷号 / Coil No.」绑定可选字符串 `coilNo`，「已生产长度 / Produced length」绑定 `producedLength`，「产线状态 / Line state」绑定 `lineState`。已确认的规格、进线时间和工序可各配一张卡。「实际线速度 / Actual line speed」可引用传动组的 `lineSpeedAct`。 |
| 清洗工艺 | `cleaning` | 按工位配卡，例如「清洗工位 1 / Cleaning Station 1」。按来源绑定该工位的实测与设定温度、实测液位，以及可取得的刷辊或就绪状态。温度、液位取自 `cleaning`，动作取自 `cleaningMotion`。碱洗工位可用同一结构。 |
| 温控工艺 | `temperature` | 每个已确认炉区配一张温度卡，例如「加热区 1 / Heating Zone 1」绑定 `furnaceZone1Actual` 和 `furnaceZone1Set`，即后文炉区 1 的合成示例。 |
| 传动工艺 | `drive` | 「线速度 / Line speed」绑定 `lineSpeedAct` 和 `lineSpeedSet`。「开卷张力 / Uncoiler tension」和「收卷张力 / Recoiler tension」分别绑定对应位置的实测张力与已确认设定张力。其他已确认位置可复用此结构，转矩按需另配卡。 |

卷号和卷状态按需在 `production` 组登记，各自从 `values` 读取并绑定卡片。任务号沿用固定字段 `taskNo`，卷号是业务指标值，示例见第 3.2 节和第 5 节。

卡片配置包含项目内稳定的 `cardKey`、`pageKey`、中英文标题、启用开关和排序。卡内 `items` 按顺序引用已登记的 `metricKey`，每项有独立启用开关。后端校验每卡最多 10 个启用指标，同一卡内的指标引用须唯一。生产参数页可只绑定一个值，其他页面也可按需选择单项或多项，同一组件按配置渲染。

页面显示本页启用且含有启用、可查看指标项的卡片。没有可显示的卡片时使用页面空态。当前任务未确认、现场无在制任务或当前任务的某组尚无快照时，相关指标显示缺测。已启用且有权查看的缺测项保留位置并显示 `—`，当前任务的已知旧值按该项实际采集时间标注陈旧。数值 `0` 和布尔 `false` 按有效值显示。

页面按语言取配置标题，固定菜单及状态文案走双语 i18n。过程监控首版由温度曲线、传动监控、清洗监控三个历史页组成，曲线组预设见第 4.2 节。

## 3. 指标定义、实时快照与过程历史

**R02** 指标键在项目内唯一。同一键的类型、单位口径和业务含义贯穿两个写入目标，物理含义变化时登记新键。`sourceGroupKey` 决定指标归属的采样组。后端用目标和组的槽位绑定读写 `local_values`，对外用稳定指标键。卡片和曲线组通过展示绑定引用指标。传动与生产参数页各自配置的卡片可引用 `lineSpeedAct`，从同一份传动快照读值。

`nameZh` 和 `nameEn` 分别保存指标的中文和英文名称，两种语言共用指标定义中的 `unit`。`unit` 可留空。管理员可调整中英文展示名称与显示小数位，卡片和曲线组的中英文标题各自可编辑。

首版每个 `metricKey` 对应一个标量。写入使用 JSON 数字、布尔值或字符串，枚举与业务时间使用经校验的字符串。`values` 可容纳同一次采样中的多个标量。实测值和设定值各用稳定指标键上报，设备就绪等来源状态也各有自己的标量键。

**R03** 本版以 `equipmentId` 表示稳定的产线业务键。`groupKey` 标识可独立提交的一组采样。同一工艺类别可以配置多个独立采样组，页面按指标配置合并它们。快变线速度与按换卷更新的当前卷信息可以分别刷新。组内以来源和采集时序均可核验的一次采样为准。

实时接口首次为设备、任务及组建立快照。同一身份只接受采集时间较新的样本整份替换采集字段，行 `id` 和备注保留。较早样本返回 `stale`，同一采集时间且采集内容一致时确认已保存，同一采集时间且采集内容不同则返回冲突。同组本次确认的值随包提交，省略项在新快照中表现为缺测。`0` 和 `false` 是有效值。前端用缺测状态和采集时间区分缺值与陈旧值，保留实际采集时间。

可选的 `coilState` 是独立于任务号和产线运行状态的字符串指标。`present` 表示现场确认有卷，取得卷号时同时提供 `coilNo`。`absent` 表示当前无卷，`unknown` 表示来源暂未确认，两种状态均省略卷号。生产组新帧整体替换，换卷或清空时原子更新该组值。暂停中的产线仍可有在制卷。

**R04** 清洗、温控和传动的历史样本独立追加，已接收的历史数据永久保留，无自动到期清理。产线启用后从首份符合准入、任务归属和历史选样条件的样本开始累积。符合条件的迟到样本按原任务和原采集时间追加。以原来源样本身份、设备、任务、组与原采集时间识别同一份历史，结合持久回执去重。历史页按 `taskNo`、类别、设备、组、时间段及选定指标读取。卡片隐藏、实时值覆盖与 DAA 原始事实到期均独立于业务历史的保留。生产组卷号只在实时展示，正式卷重、起止时间和其他生产实绩归实绩业务。

**R05** `sampledAt` 表示实际来源采集时间，业务时间统一用 `Asia/Shanghai` 口径，API 携带 `+08:00`。接入其他时区时在边界转换一次。MySQL 业务时间按上海本地日历保存，保存时间和采集时间分别记录。首次启用前用受控样本核验来源采集、存储、查询与显示的时间口径。 [时间契约](../../AGENTS.md#7-时间与时区)

### 3.1 首版采样组与历史指标

下表是首版建议配置。以点表和现场采样能力确认各组的实际边界、指标键、数据精度、单位和可用频率。实时周期指快照投递的起始配置，历史间隔指选样间隔，端到端时延以第 7.3 节的实测为准。

| 采样组 | 实时快照建议周期 | 历史建议间隔 | 首版历史白名单候选 |
| --- | --- | --- | --- |
| `production` | 2 秒 | 仅实时 | — |
| `drive` | 1 秒 | 5 秒 | `lineSpeedAct`、`lineSpeedSet`，以及开卷、炉区、收卷已核实的实测张力和设定张力对。 |
| `temperature` | 5 秒 | 10 秒 | 已核实炉区的实测温度和配对的已确认设定温度。 |
| `cleaning` | 5 秒 | 10 秒 | 已核实清洗、碱洗工位的实测温度、可取得的设定温度和有数值测量的液位。 |
| `cleaningMotion` | 2 秒 | 仅实时 | — |

历史白名单按产线和组配置，只登记经过来源与语义核验的指标键。实测与设定指标分别登记，单位、设定点可用性及精度以现场核实为准。辅助状态、转矩、原始标志和生产上下文默认只进入实时快照。同一类别下的独立慢信号可另设采样组。

SMA 对每条产线的每个历史组，在每个采样间隔最多选一份来源质量合格的真实样本。有样本时按原采集时间和指标子集投递，无合格样本时留空。选样完成后，重试继续使用该样本和事件身份。按三组每 5、10、10 秒各写一行且全天连续计算，约为每产线每天 34,560 行。组进一步拆分时重新估算，实施前结合索引、回执、查询和备份核对容量。

### 3.2 任务归属和换单

**R12** 任务身份沿用通用任务方案。两张值表都有固定列 `task_no`，API 使用 `taskNo`。去除首尾空格并将英文字母统一为大写，长度为 1–50 个字符，允许英文字母、数字、连字符、下划线和点。规范化后的任务号在项目内唯一识别一次生产任务，同一任务可以有多组快照和多条历史，各记录由内部 `id` 区分。两路通过任务号关联业务身份。计划和实绩的状态、业务值及回写由各自入口管理。 [任务号规则](../../docs/generic-task-workflow-discussion.zh-CN.md#task-identity)

`coilNo` 按来源字符串保存，例如 `"000042"` 的前导零保留。一个任务对应一卷的项目可约定任务号和卷号取同一文本，满足各自字段校验即可。返工或再次生产分配新 `taskNo`，可继续使用原 `coilNo`。历史按任务号区分每次生产，卷号无需固定列、专用响应上下文或查询索引。

PLC 在实际开工或换单时更新 `activeTaskNo`。DAA 在采样时取得可核验的任务归属证据并随原事实保留，SMA 按该事实的原任务号投递。现场证实空闲时显示空闲，缺少或无法确认的归属暂留来源事实以供核对。任务型实时和历史写入以可确认归属的样本为准。 [现场任务号来源](../../docs/generic-task-workflow-discussion.zh-CN.md#plc-conditions)

设备当前任务以现场确认的任务状态及其来源时序判定，包括空闲状态。状态事实的读取入口和接线在实施合同定稿时确定。收到晚到的 A 单样本时，实时写入仅定位 A 单自己的快照组，符合历史规则的样本也追加至 A 单。卡片在确认换到 B 单后只查询 B 单快照，缺组显示缺测。归属不明或现场无任务时显示对应空态。上报到达顺序只反映投递时机，采样归属以同次来源证据为准。

### 3.3 本地槽位与物理表

**R14** 首版建议每个 `target + groupKey` 有 100 个本地槽位，目标取 `latest` 或 `history`。槽位号在配置中为整数 1–100，存到 JSON 对象时使用键 `"01"` 至 `"100"`。同一个指标键可在两个目标使用不同的槽位。两张值表各有一列 `local_values`，存原类型 JSON 标量，缺测项省略。有效的 `0`、`false` 和带前导零的字符串直接保存。这个设计沿用计划／实绩的本地槽位思路，实时与历史各自保存业务值。 [通用任务的本地槽位](../../docs/generic-task-workflow-discussion.zh-CN.md#field-capacity-types)

| 拟定配置表 | 列型与约束 |
| --- | --- |
| `equipment_metric_configs` | `metric_key VARCHAR(64)` 主键，`source_group_key VARCHAR(64)`，`category VARCHAR(32)`，`name_zh VARCHAR(128)`、`name_en VARCHAR(128)`，`value_type VARCHAR(16)` 限 `number`、`boolean`、`string`，`unit VARCHAR(24)` 和 `decimals TINYINT UNSIGNED` 可空。 |
| `equipment_metric_slot_bindings` | `target VARCHAR(7)` 限 `latest`、`history`，`group_key VARCHAR(64)`，`slot_no TINYINT UNSIGNED` 限 1–100，`metric_key VARCHAR(64)` 引用登记表，`enabled BOOLEAN`，`first_used_at DATETIME(6)` 可空。主键 `(target, group_key, slot_no)`，唯一键 `(target, group_key, metric_key)`。后端校验组归属与容量。 |

同一目标与组内，每个槽位和指标只绑定一次。首次成功存值随写入登记 `first_used_at`，自此该槽位绑定固定。某个指标任一目标开始存值后，指标键、类型和单位口径在两路均固定。停用只关闭目标的新写入，槽位仍占用并保留原值解码能力，恢复沿用原关联。变更业务含义时用新指标键和空余槽位。名称、显示小数位及卡片和曲线标题仍可编辑，改标题只改变界面显示。卡片和曲线组独立引用指标，历史还需满足产线白名单与间隔。它们的配置存放结构随实施规格定稿。

下表列出两张值表共用的物理列建议。除标明可空外均须有值。

| 列 | MySQL 候选类型 | 说明 |
| --- | --- | --- |
| `id` | `BIGINT UNSIGNED` | 各表生成的行主键。 |
| `equipment_id`、`group_key` | 各 `VARCHAR(64)` | 产线和采样组。 |
| `task_no` | `VARCHAR(50)` | 已规范化的业务任务号。 |
| `sampled_at` | `DATETIME(6)` | 现场采集时间，按上海时间。 |
| `quality` | `VARCHAR(16)` | 来源采集质量。 |
| `source_sample_key` | `BINARY(32)` | 规范化原来源样本身份的摘要。 |
| `ingest_receipt_id` | `BIGINT UNSIGNED` | 写入该份采集数据的持久回执，详情由回执读取来源引用和映射版本。 |
| `local_values` | `JSON` | 本目标和组的槽位号到原类型值，空对象为 `{}`。 |
| `remark` | `TEXT` 可空 | 管理员备注，独立于采集字段。 |
| `created_at`、`updated_at` | 各 `DATETIME(6)` | 行首次保存及最后实际修改时间，按上海时间。采集更新与管理编辑均按实际变动维护 `updated_at`。 |

| 值表 | 写入行为、特有列与索引 |
| --- | --- |
| `equipment_latest_snapshots` | 唯一键 `(equipment_id, task_no, group_key)`，只用较新采集值更新同一行的采集字段。管理列表可用 `(task_no, id)` 索引。 |
| `monitor_history_samples` | 独立生成每次追加的 `id`。唯一键 `(equipment_id, task_no, group_key, sampled_at, source_sample_key)` 用于同源样本去重。索引 `(task_no, sampled_at, id)` 支持任务查询和稳定分页，`(equipment_id, group_key, sampled_at, id)` 支持按产线与组查时段。另有可空的 `review_mark VARCHAR(16)`，保存管理员标记 `abnormal` 或 `reviewed`。 |

来源样本身份取可核验的同一采样帧。PLC 事实按实例、PLC 和样本 ID 识别，外部事件按来源 ID 和来源事件 ID 识别。点位顺序、目标事件号和选入历史的指标集合均独立于原样本身份。历史中同源且内容一致的提交只确认现有记录，内容冲突时保留原行并返回冲突。

持久回执拟存 `metric_ingest_receipts`。列包括 `id BIGINT UNSIGNED` 主键、`target VARCHAR(7)`、`producer_id VARCHAR(64)`、`event_id VARCHAR(128)`、`request_digest BINARY(32)`、`outcome VARCHAR(24)`、`processed_at DATETIME(6)`、可空的 `result_record_id BIGINT UNSIGNED`、`mapping_id VARCHAR(64)`、`mapping_revision VARCHAR(32)` 和 `source_refs JSON`。以 `(target, producer_id, event_id)` 唯一识别投递。同一事务保存接收结果与对应写入，按第 5 节的规则确认及重试。写入确认时间取关联回执的 `processed_at`，卡片时序和历史横轴使用 `sampled_at`。历史引用的回执随原记录保留，保证来源可查。实际索引选择和容量在受控 MySQL 样本上验证。

## 4. 前端查询和管理接口

**R06** 前端接口使用登录态与业务权限。普通读用户在获准设备上查看配置选定的卡片、曲线和历史。设备状态提供指标登记、槽位绑定和卡片配置入口，过程监控提供曲线组配置入口。指标、卡片与曲线组共用中英文名称编辑与指标信息展示，卡片和曲线组复用指标选择、启用与排序交互。前端仅对 admin 显示配置入口，后端对配置查询与编辑校验登录和 admin 权限。采集数据管理另按第 4.3 节授权。

与计划／实绩对齐字段设置交互和稳定键、中英文名、类型、单位等公共元数据。指标的 `metricKey` 对应计划／实绩 API 中 `name` 的用途。指标名称使用 `nameZh`、`nameEn`，卡片及曲线组标题使用各自的 `titleZh`、`titleEn`。展示开关与排序由各自配置管理，槽位开关只控制对应目标是否接收该指标，历史白名单与间隔按产线和采样组独立设置。计划／实绩的业务值编辑与回写归本域业务合同，设备／过程的采集、存储和展示由本方案配置。 [计划与实绩的字段设置衔接](../../docs/generic-task-workflow-discussion.zh-CN.md#field-config-alignment)

| 拟定路径 | 输入与响应 |
| --- | --- |
| `GET /api/v1/equipment/latest-cards` | 按 `equipmentId`、`pageKey` 查询设备已确认的当前任务。返回 `taskNo`、任务状态和获准卡片的有序指标项。每项按 `metricKey` 表示，携带自身来源组、采集时间及数据状态。生产参数页卷号作为普通卡片指标返回。 |
| `GET /api/v1/equipment/metric-configs` | 管理员读取完整指标定义。 |
| `POST /api/v1/equipment/metric-configs` | 管理员登记指标键、所属组和类别、名称、类型与单位。 |
| `PATCH /api/v1/equipment/metric-configs/{metricKey}` | 管理员更新名称、小数位等展示元数据。物理含义变化时登记新键。 |
| `GET /api/v1/equipment/metric-slot-bindings` 与 `POST /api/v1/equipment/metric-slot-bindings` | 管理员按目标和组读槽位或登记新绑定，详见第 4.4 节。 |
| `PATCH /api/v1/equipment/metric-slot-bindings/{target}/{groupKey}/{slotNo}` | 管理员启用、停用或恢复该目标的原绑定。 |
| `GET /api/v1/equipment/card-configs` 与 `POST /api/v1/equipment/card-configs` | 管理员按页读取或建立卡片配置，含启用和停用项。 |
| `PATCH /api/v1/equipment/card-configs/{cardKey}` | 管理员更新页面、标题、开关、排序及有序指标引用，提交时校验引用唯一和 10 项上限。 |
| `GET /api/v1/monitor/history-samples` | 支持按 `taskNo`、`equipmentId`、`groupKey` 或 `category`、采集时间范围和指标键筛选并分页。返回任务号、采样时间和按 `metricKey` 还原的值，附展示元数据。 |
| `GET /api/v1/monitor/history-curves` | 按设备、工艺类别及采集时间范围查询，可按 `taskNo` 筛选。返回获准的启用曲线组、有序指标及对应采集时间和值。 |
| `GET /api/v1/monitor/curve-configs` 与 `POST /api/v1/monitor/curve-configs` | 管理员按工艺类别读取或建立曲线组配置，含启用和停用组。 |
| `PATCH /api/v1/monitor/curve-configs/{curveGroupKey}` | 管理员更新标题、开关、排序和有序历史序列引用。 |

例如 `GET /api/v1/monitor/history-samples?equipmentId=line-01&groupKey=temperature&taskNo=000042` 只查该任务在这条产线和组的历史。后台先按固定字段过滤，再按 `sampled_at` 和 `id` 同向排序分页。曲线按原采集时间顺序返回，业务卡片、历史与曲线接口统一使用指标键。

### 4.1 卡片配置和响应

以下以合成验证用的炉区 1 为例。三项的 `sourceGroupKey` 和 `category` 均为 `temperature`。预设将实际与设定温度纳入历史白名单，加热就绪按需登记并仅进入实时快照。

| `metricKey` | `nameZh` / `nameEn` | `valueType` | `unit` | `decimals` | 样例标量 |
| --- | --- | --- | --- | --- | --- |
| `furnaceZone1Actual` | 实际温度 / Actual temperature | `number` | `°C` | `1` | `810.2` |
| `furnaceZone1Set` | 设定温度 / Setpoint temperature | `number` | `°C` | `1` | `815.0` |
| `furnaceHeatingReady` | 加热就绪 / Heating ready | `boolean` | 留空 | 省略 | `true` |

实际温度的登记内容如下。

```json
{
  "metricKey": "furnaceZone1Actual",
  "sourceGroupKey": "temperature",
  "category": "temperature",
  "nameZh": "实际温度",
  "nameEn": "Actual temperature",
  "valueType": "number",
  "unit": "°C",
  "decimals": 1
}
```

温控工艺页的一张卡片绑定两项指标。

```json
{
  "cardKey": "furnaceZone1Temperature",
  "pageKey": "temperature",
  "titleZh": "加热区 1",
  "titleEn": "Heating Zone 1",
  "enabled": true,
  "sortOrder": 10,
  "items": [
    {"metricKey": "furnaceZone1Actual", "enabled": true},
    {"metricKey": "furnaceZone1Set", "enabled": true}
  ]
}
```

看板响应 `data.cards` 中的一张卡片如下。各项采集时间和新鲜度由其自身来源决定，缺测项的值返回 `null` 并标记 `missing`。

每项响应分开提供当前语言的名称 `label` 和可选的 `unit`。有单位时，前端在指标项标题附加单位，例如「实际温度（°C）」与「Actual temperature (°C)」。单位留空或省略时，指标项标题只显示名称。卡片组标题由卡片配置提供，指标值区只显示格式化后的值。

```json
{
  "cardKey": "furnaceZone1Temperature",
  "title": "加热区 1",
  "items": [
    {
      "metricKey": "furnaceZone1Actual",
      "label": "实际温度",
      "value": 810.2,
      "valueType": "number",
      "unit": "°C",
      "decimals": 1,
      "sourceGroupKey": "temperature",
      "sampledAt": "2026-11-07T09:30:00.123+08:00",
      "dataState": "fresh"
    },
    {
      "metricKey": "furnaceZone1Set",
      "label": "设定温度",
      "value": 815.0,
      "valueType": "number",
      "unit": "°C",
      "decimals": 1,
      "sourceGroupKey": "temperature",
      "sampledAt": "2026-11-07T09:30:00.123+08:00",
      "dataState": "fresh"
    }
  ]
}
```

### 4.2 过程监控曲线组

**R11** 管理员为温度、传动及清洗历史页设置曲线组。`curveGroupKey` 是项目内稳定的展示键，`category` 确定所属工艺页，`series` 按顺序引用该类别已登记的数值型指标。每组可设置中英文标题、启用开关和排序，序列可独立启用。组内序列使用同一物理量和单位，炉区 1 的实际温度和设定温度可以用两条 °C 曲线并列显示。

| 过程监控页面 | 建议曲线组中英文标题 | 已存序列 |
| --- | --- | --- |
| 温度曲线 | 加热区 1 温度曲线 / Heating Zone 1 temperature history | `furnaceZone1Actual` 和 `furnaceZone1Set`。每个已核实的炉区按同样结构配置。 |
| 传动监控 | 线速度曲线 / Line speed history | `lineSpeedAct` 和 `lineSpeedSet`。各传动位置的实际与设定张力配在独立组，例如「开卷张力曲线 / Uncoiler tension history」。 |
| 清洗监控 | 清洗工位 1 温度曲线 / Cleaning Station 1 temperature history | 该工位实测温度及可取得的设定温度。实测液位按工位单独成组，例如「清洗工位 1 液位曲线 / Cleaning Station 1 level history」。 |

曲线共用同单位的纵轴时，在纵轴标注一次单位。单位为空或省略时，纵轴省略单位标注。

```json
{
  "curveGroupKey": "furnaceZone1History",
  "category": "temperature",
  "titleZh": "加热区 1 温度曲线",
  "titleEn": "Heating Zone 1 temperature history",
  "enabled": true,
  "sortOrder": 10,
  "series": [
    {"metricKey": "furnaceZone1Actual", "enabled": true},
    {"metricKey": "furnaceZone1Set", "enabled": true}
  ]
}
```

曲线按原采集时间读取已存过程样本。第 5 节的 SMA 历史示例在同一时刻提供 810.2 °C 的实际温度和 815.0 °C 的设定温度。缺少已存值的时段留空或断线。曲线组的启用、隐藏与编辑只影响展示，历史写入及永久留存由独立白名单和采样策略决定。

### 4.3 实时快照与过程历史管理

**R13** 实时快照管理与过程历史管理共用列表交互。实时快照列表置于「设备状态」，过程历史列表置于「过程监控」。前端仅对 admin 显示管理入口。两页按 `taskNo`、`equipmentId` 及 `groupKey` 筛选，过程历史另支持采集时间范围。后端分页。固定列显示任务号、设备、采样组、采集时间和数据状态。详情按槽位绑定还原指标键，展示名称、单位及采集值，并提供来源、采集质量和管理信息。后端对两个管理列表的查询、详情和修改分别校验登录、admin 与设备访问范围。普通卡片与曲线查询沿用业务读权限。

| 候选管理资源 | 首版编辑白名单 |
| --- | --- |
| `/api/v1/equipment/admin/latest-snapshots` | 仅备注 `remark`。SMA 更新同一设备、任务与组的采集字段时，保留该记录的管理员备注。 |
| `/api/v1/monitor/admin/history-samples` | 备注 `remark` 及管理标记 `reviewMark`，可标记异常或已复核。管理标记与来源采集质量分别显示。 |

两个候选资源以 `GET` 查询分页列表，在资源后附 `/{id}` 提供 `GET` 详情和 `PATCH` 管理字段更新。`id` 使用对应值表的行主键，API 按字符串输出。采集值、原采集时间、任务号、来源、质量和投递回执归各自采集链路。备注和管理标记独立保存，管理员提交编辑白名单外的字段时后端拒绝。原始值更正列入后续范围。

### 4.4 槽位配置管理

管理员在字段设置中选择目标和组。读取返回 `slotNo`、`metricKey`、启用状态、首次使用时间及该组剩余容量，停用槽位也计入占用。新建绑定提交 `target`、`groupKey`、`slotNo`、`metricKey`、`enabled`，后端验证目标、指标组归属、空余槽位和同组同目标的唯一性。PATCH 修改原关联的 `enabled`，停用或恢复保持原槽位。修改中英文标签走指标定义，卡片和曲线标题走各自配置。

## 5. SMA 指标发现和写入接口

**R07** SMA 与获准的第三方共用以下集成接口。后端凭集成凭据识别调用方，从准入配置确定调用方是 SMA 还是第三方直连，并校验设备、采样组、目标和指标。`producerId` 用于身份关联和回执，不能凭请求体中的 `producerId` 取得权限。生产环境采用的凭据机制由实施合同确定。前端显示权限、管理员权限和集成准入分别校验。

| 拟定路径 | 语义 |
| --- | --- |
| `GET /api/v1/integration/metric-definitions` | 以 `equipmentId`、`groupKey`、`target` 查询该 SMA 或第三方获准上报的已启用指标键、类型和可选单位。历史目标另取该产线与组的白名单。 |
| `POST /api/v1/integration/equipment/latest-snapshots` | 校验任务归属、采样组与指标类型，写入相应任务的实时快照。 |
| `POST /api/v1/integration/monitor/history-samples` | 校验任务归属、工艺组与指标类型，按原任务追加选择留存的样本。 |

两个 POST 接收 `application/json`，共用 `aiis.metric-ingest/v1` 信封，请求路径决定写入目标。SMA 提交完整信封，每次发送 `contractVersion`、`producerId`、`eventId`、`mappingId`、`mappingRevision`、`sourceRefs` 和 `data`，`data` 中的 `equipmentId`、`taskNo`、`groupKey`、`sampledAt`、`quality`、`values` 均须提供。SMA 可在连接及映射配置中一次设定固定的协议版本、写入方、映射标识和版本，以及固定设备和组，由程序随每次请求发送。`plc_fact` 引用保留实际的实例、PLC、样本、点位及采样时的任务号证据。第三方直连按下文规则省略允许缺省的字段，后端补齐后进入同一写入流程。 [现有来源类型参考](../../backend/common/integration/envelope.py)

两类调用方均在 `values` 中按 `metricKey` 提交符合登记类型的 JSON 数字、布尔值或字符串。有单位的指标按登记的业务单位上报。后端按写入准入及槽位绑定整包校验后转换为 `local_values`。回执保留写入身份、事件、来源引用和映射信息。采集数据模块继续使用自己的事实查询与写入合同。

### 指标发现示例

`equipmentId`、`groupKey` 和 `target` 是必传的查询参数，`target` 取 `latest` 或 `history`。调用方必须通过集成身份认证，且已启用并获准向指定设备、采样组和目标写入。未认证返回 `401`，身份已认证但未启用或越权返回 `403`，不返回字段定义。已准入但没有可写指标时返回空的 `definitions`。固定设备和组只可在符合下文条件的 POST 请求体中省略。

GET 只返回当前可写的指标定义，包括 `metricKey`、`valueType` 和有定义时的 `unit`。结果按调用方的指标准入、目标的已启用槽位与组归属取交集，`history` 再取该设备及组的历史白名单。此权限只用于字段发现和相应范围的写入。已存实时值、历史值和内部槽位均不在此响应中。业务读和管理员权限见第 4 节。

请求 `GET /api/v1/integration/metric-definitions?equipmentId=line-01&groupKey=temperature&target=history`，在该产线的历史白名单中发现两项温度指标。

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "equipmentId": "line-01",
    "groupKey": "temperature",
    "target": "history",
    "definitions": [
      {"metricKey": "furnaceZone1Actual", "valueType": "number", "unit": "°C"},
      {"metricKey": "furnaceZone1Set", "valueType": "number", "unit": "°C"}
    ]
  }
}
```

调用方同时获准写入 `latest` 时，同一请求换用 `target=latest` 会另返回布尔型 `furnaceHeatingReady`，该项无单位。POST 再次校验写入准入。新事件遇到未登记、目标禁用、组错配或类型错误的指标时，整包拒绝并返回可定位到字段的错误。

<a id="third-party-ingest-fields"></a>

### 第三方直连字段

接入时为第三方启用机器身份，配置来源标识、可写设备与采样组、目标及指标范围，并登记接入配置的标识和版本。固定绑定一个设备和组的调用方可让后端补齐设备和组。多组或多设备的调用方在每次 POST 中指定两项。绑定到同一身份的来源标识及固定设备和组保持稳定。需要换绑时使用新的接入身份，以免把重试送入其他组。

下表的「省略」表示请求里不出现该键。除实时的 `data.quality` 外，表内字段显式传入 JSON `null` 时后端拒绝。标识字段的空字符串也无效。

| JSON 字段 | 第三方直连要求 | 后端处理 |
| --- | --- | --- |
| `sourceRefs`、`sourceRefs[0].kind`、`sourceRefs[0].sourceEventId` | 每次必传，提供一条 `kind` 为 `external_event` 的引用，事件号使用原来源的稳定标识。 | 用 `sourceId` 和 `sourceEventId` 识别原样本。同一来源的同一次采集在两路和重试中沿用原事件号。 |
| `data`、`data.taskNo`、`data.sampledAt`、`data.values` | 每次必传。提交采样时确认的任务号、带时区的原采集时间和至少一个获准指标。 | 按第 3.2 节校验任务归属，按 R05 规范化采集时间。归属无法确认时拒绝，不从当前任务或接收时间补值。按登记类型校验指标。 |
| `data.quality` | 实时可省略或传 `null`，也可据实传 `good`、`bad` 或 `unknown`。历史必须明确传来源质量 `good`。 | 实时的省略或 `null` 均记为 `unknown`。历史缺字段、`null`、`bad` 或 `unknown` 时返回质量字段错误，不追加样本。 |
| `data.equipmentId`、`data.groupKey` | 固定单设备和组的身份可省略。其他身份每次均须提供两项。 | 从固定绑定补齐缺项。显式值须符合绑定及准入，后端按最终设备、组和请求目标校验。 |
| `producerId`、`sourceRefs[0].sourceId` | 可省略，由接入时的配置提供。 | 分别使用认证得到的写入身份及其绑定的来源标识，若显式提交须与绑定一致。 |
| `mappingId`、`mappingRevision` | 可一起省略，也可一起提交。 | 使用已登记的第三方接入配置标识和版本记录追溯信息。显式值须匹配该次投递所用的配置。 |
| `contractVersion` | 可省略。 | 使用 `aiis.metric-ingest/v1`。显式传值须为该版本。 |
| `eventId` | 可省略。显式提交时须为该目标的稳定投递标识，重试时沿用。 | 缺省时按写入方、设备、组、`sourceId`、`sourceEventId` 和目标生成稳定的投递标识。每路回执返回实际采用的 `eventId`。 |

`values` 中缺测的单项指标直接省略该键，显式 `null` 会使整包被拒绝。`0` 和 `false` 是有效值。新实时快照对省略项显示缺测，历史样本对省略项不记录值。数据库行号、内部槽位、管理员备注、复核标记、显示名称和单位均由系统管理，POST 不接收这些字段。历史写入仍须满足来源、任务归属、白名单与历史选样规则。

后端先确认调用身份、解析缺省设备与来源并校验目标准入，再定位投递事件。缺省生成的 `eventId` 与接收时间、指标值及映射版本无关。命中已有回执时用回执记载的映射信息补齐该事件的缺省版本，按规范化后的内容比较并复用原结果，内容不同则返回冲突。新事件使用当前配置并执行完整写入校验。调用方应对同一逻辑投递一直沿用原来的 `eventId` 或一直省略它，保留原事件号和原采样内容分别重试两路。

以下两例使用已启用的第三方身份，其接入绑定固定为 `line-01`、`temperature` 和一个外部来源，且同时获准写入两个目标。两条请求引用同一个外部样本，分别产生各自的投递标识和回执。

<a id="third-party-latest-example"></a>

### 第三方实时快照最简请求

`POST /api/v1/integration/equipment/latest-snapshots`。省略采集质量，后端记为 `unknown`。

```json
{
  "sourceRefs": [{"kind": "external_event", "sourceEventId": "vendor-sample-42"}],
  "data": {
    "taskNo": "000042",
    "sampledAt": "2026-11-11T09:30:00.123+08:00",
    "values": {"furnaceZone1Actual": 810.2}
  }
}
```

<a id="third-party-history-example"></a>

### 第三方历史追加最简请求

`POST /api/v1/integration/monitor/history-samples`。本次实际采集质量合格，显式传入 `good`。

```json
{
  "sourceRefs": [{"kind": "external_event", "sourceEventId": "vendor-sample-42"}],
  "data": {
    "taskNo": "000042",
    "sampledAt": "2026-11-11T09:30:00.123+08:00",
    "quality": "good",
    "values": {"furnaceZone1Actual": 810.2}
  }
}
```

以下两个请求来自合成产线首次启用后的同一温控采样。SMA 对该样本执行一次指标映射，再按目标拆分请求。两路携带同一个 `taskNo`，均引用采样时的任务号证据。按第 4.1 节预设登记指标，实际温度和设定温度各以一个标量上报，两者被选入当次历史样本，加热就绪状态仅进入实时快照。

### 实时快照请求

```json
{
  "contractVersion": "aiis.metric-ingest/v1",
  "producerId": "sma-line-01",
  "eventId": "temperature-42-latest",
  "mappingId": "temperature-metrics",
  "mappingRevision": "r1",
  "sourceRefs": [
    {"kind": "plc_fact", "instanceId": "daa-01", "plcId": "plc-01", "sampleId": "sample-42", "pointId": "point-zone1-temp-act"},
    {"kind": "plc_fact", "instanceId": "daa-01", "plcId": "plc-01", "sampleId": "sample-42", "pointId": "point-zone1-temp-set"},
    {"kind": "plc_fact", "instanceId": "daa-01", "plcId": "plc-01", "sampleId": "sample-42", "pointId": "point-active-task-no"},
    {"kind": "plc_fact", "instanceId": "daa-01", "plcId": "plc-01", "sampleId": "sample-42", "pointId": "point-ready"}
  ],
  "data": {
    "equipmentId": "line-01",
    "taskNo": "000042",
    "groupKey": "temperature",
    "sampledAt": "2026-11-07T09:30:00.123+08:00",
    "quality": "good",
    "values": {
      "furnaceZone1Actual": 810.2,
      "furnaceZone1Set": 815.0,
      "furnaceHeatingReady": true
    }
  }
}
```

### 历史追加请求

```json
{
  "contractVersion": "aiis.metric-ingest/v1",
  "producerId": "sma-line-01",
  "eventId": "temperature-42-history",
  "mappingId": "temperature-metrics",
  "mappingRevision": "r1",
  "sourceRefs": [
    {"kind": "plc_fact", "instanceId": "daa-01", "plcId": "plc-01", "sampleId": "sample-42", "pointId": "point-zone1-temp-act"},
    {"kind": "plc_fact", "instanceId": "daa-01", "plcId": "plc-01", "sampleId": "sample-42", "pointId": "point-zone1-temp-set"},
    {"kind": "plc_fact", "instanceId": "daa-01", "plcId": "plc-01", "sampleId": "sample-42", "pointId": "point-active-task-no"}
  ],
  "data": {
    "equipmentId": "line-01",
    "taskNo": "000042",
    "groupKey": "temperature",
    "sampledAt": "2026-11-07T09:30:00.123+08:00",
    "quality": "good",
    "values": {
      "furnaceZone1Actual": 810.2,
      "furnaceZone1Set": 815.0
    }
  }
}
```

### 生产组上报示例

生产组使用实时接口。下例为同种信封中的 `data`，卷号和可选卷状态作为指标写入。

```json
{
  "equipmentId": "line-01",
  "taskNo": "000042",
  "groupKey": "production",
  "sampledAt": "2026-11-07T09:30:00.123+08:00",
  "quality": "good",
  "values": {
    "coilNo": "000042",
    "coilState": "present"
  }
}
```

例如生产组实时槽位 `01` 绑定 `coilNo`、`02` 绑定 `coilState`，落库值为 `{"01":"000042","02":"present"}`。「卷号 / Coil No.」卡片仍按指标键取字符串 `"000042"`。

### 同源样本的落库结果

两条温控请求均来自 `sample-42`，任务号为 `000042`，采样组为 `temperature`，采集时间为 `2026-11-07T09:30:00.123+08:00`。这组指标的槽位按目标分别配置。

| 指标键 | 实时槽位 | 历史槽位 |
| --- | --- | --- |
| `furnaceZone1Actual` | `01` | `07` |
| `furnaceZone1Set` | `02` | `08` |
| `furnaceHeatingReady` | `03` | — |

| 目标值表 | 同一次采样保存的 `local_values` |
| --- | --- |
| `equipment_latest_snapshots` | `{"01":810.2,"02":815.0,"03":true}` |
| `monitor_history_samples` | `{"07":810.2,"08":815.0}` |

前端读取时，两个温度槽位分别还原为 `furnaceZone1Actual` 和 `furnaceZone1Set`，卡片显示当前任务的最新值，曲线读按采集时间追加的值。加热就绪只在实时目标。

**R08** SMA 对每份来源一致的样本执行一次指标映射，再按各自的投递周期和目标指标集合组装实时或历史请求，历史按独立白名单选样。两路共用同源事实和采样时确定的任务归属，各自用稳定的 `eventId`。按写入目标、`producerId` 和 `eventId` 识别重试，同一身份携带不同内容时返回冲突。新写入与回执同事务提交，SMA 逐目标核对持久回执与请求身份，分别确认与重试。对已授权调用者，原事件按相同内容重试时返回保存结果，包括实时 `stale` 或历史同源已保存的处理结果。已有回执时复用原结果，后续配置变动独立处理。

两个写入接口采用同一回执形状。以下示例确认一条历史记录。

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "target": "history",
    "producerId": "sma-line-01",
    "eventId": "temperature-42-history",
    "outcome": "stored",
    "recordId": "542"
  }
}
```

`recordId` 为对应值表的行主键，带结果记录时按字符串返回。除 `stored` 外，候选成功结果含 `already_stored` 和实时 `stale`。同事件重试复用原回执，`already_stored` 表示另一次合法提交找到一致的已存样本。

## 6. 配置和新模块的边界

**R09** 同类项目接入优先配置。用 DAA 的点位配置确定来源，用 SMA 映射将点位转换到已登记的指标键，用目标与采样组的绑定决定入库槽位，用卡片和曲线组决定展示，用历史白名单和间隔决定留存内容与频率。第二条产线换 PLC 地址、单位换算参数或留存策略时，复用相同页面、存储和接口。

以下需求应单独评估代码范围。

- 需要新的生产状态机、实绩结算、跨对象事务或特有报表时，归相应业务模块。
- 需要新的采集协议、设备动作或现场编排时，归对应的 DAA、CA 或 Field Flow 范围。
- 需要通用卡片、趋势或表格无法表达的专用交互时，先核对能否复用同一数据合同，再确定消费项目的页面范围。

类似能力已有产品先例。ThingsBoard 使用命名指标上报，并能分别设置最新值与历史的保存策略。Ignition 通过 UDT 参数复用标签结构，按标签选择历史记录。WinCC Unified 用 Faceplate 标签接口复用画面。这些先例支持配置优先的取舍，AIIS 的表结构和接口语义由本方案单独定义。 [ThingsBoard 上报](https://thingsboard.io/docs/reference/http-api/telemetry/) · [ThingsBoard 保存策略](https://thingsboard.io/docs/reference/rule-engine/nodes/action/save-timeseries/) · [Ignition UDT](https://www.docs.inductiveautomation.com/docs/8.3/platform/tags/user-defined-types-udts) · [Ignition 历史配置](https://docs.inductiveautomation.com/docs/8.3/ignition-modules/tag-historian/configuring-tag-history) · [WinCC Unified Faceplate](https://docs.tia.siemens.cloud/r/en-us/v21/configuring-screens-rt-unified/configuring-faceplates-rt-unified/example-creating-and-using-faceplates-rt-unified/example-using-a-dynamic-tag-as-an-interface-property-rt-unified)

## 7. 首次启用、实施顺序与后续议题

### 7.1 首次启用与数据起点

**R10** 每条产线先准备指标、两路槽位、卡片、曲线组、DAA 点位和 SMA 映射，首次获准启用时开启对应的写入准入。快照及过程历史从空库开始。启用后，首份通过校验且归属已确认任务的样本建立相应组的实时快照，首份同时符合历史白名单与采样策略的样本追加为历史。首次采集前及无合格样本的查询显示空态或缺测。后续样本保留原采集时间和任务归属，换单与迟到按第 3.2 节处理。

### 7.2 首版实施与验证顺序

1. 定稿首版接口、准入、回执和错误码，确认数据表、槽位、项目预设及合成炉区 1 样本。样本覆盖实际温度、设定温度、可选就绪和任务切换。
2. 后端建立配置、快照、历史与持久回执，提供业务读写、管理列表和权限校验。
3. 前端与 SMA 在同一获批合同下并行。前端实现看板、历史和管理员入口，SMA 接入 DAA 来源并实现一次映射、两路投递及独立重试。
4. 在隔离环境验证从空库到首个样本、槽位上限、任务换单、重复投递和管理字段保护。首次现场启用另按真实产线的范围批准和验证。

### 7.3 现场确认与后续优化

- 首次现场启用前核实点表、`activeTaskNo` 与空闲值、采样时任务证据、成帧能力、单位、状态枚举、实际采样周期和历史白名单。以项目现场数据确认首版预设与容量。
- 能耗统计和原始值更正另立范围。能耗专题从核实独立计量来源及累计读数的增量口径开始。
- Redis 放入后续性能优化。先测从采集到屏幕显示的 P95、P99，分别归因采样、上报、SMA 投递、后端读写和浏览器刷新。重复热点读取成为瓶颈时再评估 Redis。数据库负责业务持久记录与回执。 [仓库运行边界](../../AGENTS.md#3-运行与安全边界)

### 7.4 长期阅读指南

中文讨论稿与英文配对解释首版职责、数据流、本地槽位、项目预设与实施顺序，并从双语文档索引进入。表字段、接口、JSON 示例和实施验收条目由本任务规格维护。 [中文讨论稿](../../docs/equipment-status-process-monitoring.zh-CN.md) · [English discussion draft](../../docs/equipment-status-process-monitoring.md)

D-01 至 D-05 按原修订保留。当前接入说明的更新范围见 D-06。

#### r3 D-01 讨论稿交付

2026-11-07，Human Owner 明确给出下列交付指令。

> 那就按 r3 在 docs 下面也整理一份 Markdown 讨论稿吧，和通用任务／实绩那份一样。把管理员怎么配置卡片和曲线、SMA 怎么上报、历史怎么留存写清楚，具体接口引用 spec，先不改代码。

该授权适用于 r3 第 7.4 节已经列明的讨论稿。Development 按 STD 实施 D-01，Verification 对 D-01 独立验证。r3 的软件方案继续处于 `draft`，其实施与现场采用分别等待对应范围批准。

讨论稿写入范围如下。

- 新建 `docs/equipment-status-process-monitoring.zh-CN.md`。
- 新建英文配对 `docs/equipment-status-process-monitoring.md`。
- 在 `docs/README.zh-CN.md` 和 `docs/README.md` 各增加该讨论稿的一条索引。

角色记录由 Development 写入同一 bundle 的 `tasks.md`，交接后由 fresh-context Verification 写入 `checklist.md`，两者均以 D-01 为范围。授权交付面仅涵盖上述讨论稿、索引行及角色记录，其他规格修订、代码、数据库和运行操作属于独立范围。

| 验收项 | 可观察结果 |
| --- | --- |
| D01-AC01 文档与链接 | 中英文讨论稿互链，双语文档索引可发现。两稿链接本 r3 规格，并标明讨论稿与实施范围的关系。 |
| D01-AC02 管理员配置 | 写清设备状态卡片与过程监控曲线组的配置步骤。说明每卡最多 10 个启用指标，用同一炉区的实际温度和设定温度示例串起卡片及历史曲线。 |
| D01-AC03 上报与留存 | 写清 SMA 用稳定指标键上报标量，区分实时快照覆盖与过程历史追加。说明历史指标与采样策略独立于曲线启用、隐藏和编辑。 |
| D01-AC04 权威边界 | 具体接口、字段和 JSON 示例引用本 r3 规格。文档改动落在上述允许范围，交付状态按 D-01 单独记录。 |

#### r3 D-02 单位规则补充

2026-11-07，Human Owner 明确给出下列指令。

> 那就按这个来，把单位规则补到 r3 的 spec 和 docs 讨论稿里吧。unit 可以留空，有单位就拼到中英文指标标题上，值区只显示值，SMA 还是按 metricKey 上报原类型的值。曲线共用同单位的纵轴时标一次就行。先改文档，不改代码。

D-02 是 r3 的单位说明补充。PM 在本规格记录单位口径与验收，Development 更新现有 `docs/equipment-status-process-monitoring.zh-CN.md` 和 `docs/equipment-status-process-monitoring.md`，在本 bundle 的 `tasks.md` 追加 D-02 证据。fresh-context Verification 在现有 `checklist.md` 追加 D-02 独立验证记录。D-01 的验收以原候选和记录为准，r3 软件方案状态为 `draft`。

| 验收项 | 可观察结果 |
| --- | --- |
| D02-AC01 指标单位与卡片 | 本规格和中英文讨论稿均说明两种语言共用可留空的 `unit`，名称与单位分别保存。有单位时前端组合指标项标题，示例为「实际温度（°C）」和「Actual temperature (°C)」。空单位标题只显示名称，值区只显示值。 |
| D02-AC02 曲线轴 | 两稿与本规格一致说明同单位序列共用纵轴时只标注一次单位，空单位的纵轴省略单位标注。曲线组按同一物理量和单位组织。 |
| D02-AC03 上报合同 | 两稿与本规格一致说明 SMA 按 `metricKey` 上报原类型的 JSON 标量，实时和历史共用登记的业务单位。看板示例分开保留名称 `label` 与 `unit`，原有 JSON 示例逐字节一致。 |
| D02-AC04 文档范围 | 两稿继续引用 r3 的接口与示例，现有文档链接和锚点可解析。工作树差异落在单位说明、对应验收及追加的 D-02 角色记录，D-01 记录可复核。 |

#### r4 D-03 任务归属和管理列表讨论稿

2026-11-09，Human Owner 明确给出下列指令。

> 那就按这个来，把 task_no 归属、SMA 分两路写入，以及实时快照和过程历史这两个 admin 列表一起补到 spec 和 docs 讨论稿里。首版实时只改备注，历史可以加备注、标记异常或已复核，原始值的更正后面再做。先改文档，不改代码。

D-03 是 r4 的文档范围授权。PM 在本规格登记方案与验收，Development 更新现有 `docs/equipment-status-process-monitoring.zh-CN.md` 和 `docs/equipment-status-process-monitoring.md`，在本 bundle 的 `tasks.md` 追加 D-03 证据。fresh-context Verification 在现有 `checklist.md` 追加 D-03 独立核验。协调者按交接事实同步索引。D-01 的 Owner 验收与 D-02 的文档 QA 结论各归原候选记录。r4 软件方案状态为 `draft`，实施按精确范围另行审批。

| 验收项 | 可观察结果 |
| --- | --- |
| D03-AC01 任务归属 | 规格和两稿一致说明数据库 `task_no`、接口 `taskNo`、项目内规范化唯一任务号及采样时 `activeTaskNo` 证据。按设备、任务和组定位实时快照，卡片只读已确认当前任务。换单后晚到的 A 单仍归 A 单，空闲与归属不明有明确空态。历史按原采样任务留存和查询。 |
| D03-AC02 SMA 两路 | 规格与两稿一致说明对同一来源样本执行一次指标映射，再按目标拆分请求，保留同一来源任务、两路独立周期、历史白名单、确认与重试。规格的两段写入 JSON 含相同 `taskNo` 和原采集时间，事件身份区分写入目标。指标值保持原类型标量。 |
| D03-AC03 管理列表 | 两稿和规格均说明两个 admin 列表的筛选、分页、详情与固定列，后端校验管理权限。历史额外按采集时间范围筛选，详情按指标配置显示名称与单位。实时仅改备注，SMA 更新采集字段时保留备注。历史限备注及异常或已复核标记，标记与来源质量分开，原始值更正列入后续范围。 |
| D03-AC04 文档与历史证据 | 两稿引用 r4 规格及相应锚点，原有链接、单位、时区和留存规则可核对。变更限于本次方案、两份讨论稿、角色记录及必要索引同步。D-01 和 D-02 历史授权及角色证据可复核。 |

#### r5 D-04 从零开始的总体方案讨论稿

2026-11-09（Asia/Shanghai），Human Owner 明确给出下列指令。

> 不用考虑以前的兼容，这次的设计和讨论都是0到1的开始。那么你的完整总体建议整理一下吧，是否现在就可以整理到md？可以的话开始吧。

D-04 授权总体方案与 Markdown 讨论稿更新。PM 修订本规格，Development 更新现有 `docs/equipment-status-process-monitoring.zh-CN.md` 和 `docs/equipment-status-process-monitoring.md`，在本 bundle 的 `tasks.md` 记录 D-04。fresh-context Verification 在 `checklist.md` 记录 D-04 独立核验。协调者同步双语根 PLAN、任务目录和文档索引的对应条目。D-01 至 D-03 的验收状态各归原候选和角色记录。r5 软件方案继续处于 `draft`，代码、数据库、运行及首次现场启用按各自精确范围审批。

| 验收项 | 可观察结果 |
| --- | --- |
| D04-AC01 首次启用 | 规格与两稿均采用从 0 到 1 的首版范围，说明空库、首次准入、首份合格任务样本建立实时与历史数据，以及缺测与晚到样本按原任务处理。 |
| D04-AC02 项目预设 | 规格与两稿对应四个设备状态页的中英文卡片标题、指标值及三个过程监控页的曲线组。生产参数单指标预设与固定卷上下文各有归属。炉区 1 的合成示例串起指标登记、实际值与设定值、可选的实时就绪以及同单位的历史曲线。 |
| D04-AC03 共用规则 | 规格与两稿一致说明稳定指标键、原类型标量、可选单位、展示与留存分开、SMA 一次映射两路投递、任务归属和两个管理列表的编辑边界。接口与 JSON 样例继续由规格维护。 |
| D04-AC04 顺序与范围 | 两稿互链并链接 r5 规格。实施顺序从合同与合成样本到后端、前端与 SMA 并行、受控验证和另行批准的首次现场启用。差异限于本规格、两份讨论稿、角色记录与对应索引，历史授权和证据可核对。 |

#### r6 D-05 完整方案审阅稿

2026-11-09（Asia/Shanghai），Human Owner 明确给出下列指令。

> 给出一套完整的 包括原理 表 接口 和解释 的md 整理出来给我看看

D-05 授权 Markdown 审阅稿。PM 修订本规格，Development 更新现有 `docs/equipment-status-process-monitoring.zh-CN.md` 和 `docs/equipment-status-process-monitoring.md`，在本 bundle 的 `tasks.md` 记录 D-05。fresh-context Verification 在现有 `checklist.md` 记录 D-05 独立核验。协调者同步双语根 PLAN、任务目录和文档索引的对应条目。D-01 至 D-04 的结论归原候选和角色记录。r6 软件方案处于 `draft`，DDL、OpenAPI 发布、实现和运行按各自精确范围审批。

| 验收项 | 可观察结果 |
| --- | --- |
| D05-AC01 原理与表 | 规格给出两张值表的固定列、类型、唯一键和查询索引，以及共用指标登记、独立槽位绑定和目标回执。两稿解释每目标每组 100 个槽位、两表各自的 `local_values`、首次使用固定绑定和停用占位，并链接表定义。 |
| D05-AC02 接口与样例 | 规格给出指标发现请求与响应、两条同结构 POST、生产组指标示例及对应落库内容。同一次温控采样的任务号、来源和时间一致，两路使用各自事件号与槽位。发现的键与各目标准入和类型相符，前端查询与管理员操作的范围可区分。两稿链接这些合同与示例。 |
| D05-AC03 任务与卷号 | 规格与两稿一致说明 `task_no` 是固定业务任务号，`id` 是行主键，`coilNo` 是可选字符串指标，前导零保留。历史按任务号查找，返工使用新任务号，晚到样本归原任务。保留四页卡片、三页曲线、历史留存与两个管理列表的权限边界。 |
| D05-AC04 新建与交付范围 | 从空库和首次准入开始的采用顺序保留，软件状态仍为草案。两稿互链并链接 r6 规格，D-01 至 D-04 授权与验收文本可核对。差异限本规格、两份讨论稿、角色记录及必要索引。 |

#### r6 D-06 第三方与 SMA 接入说明

2026-11-11（Asia/Shanghai），Human Owner 指定在 r6 规格和 docs 讨论稿中补充第三方与 SMA 的接入字段、后端缺省处理、GET 权限及实时和历史各一份最简 JSON。随后明确重点是第三方直连的请求字段能否省略或传 `null`。本轮授权限于该 Markdown 更新。

PM 修订本规格，Development 更新 `docs/equipment-status-process-monitoring.zh-CN.md`、`docs/equipment-status-process-monitoring.md` 并在 `tasks.md` 记录交接，fresh-context Verification 在 `checklist.md` 记录独立文档核验。协调者只同步双语根 PLAN、任务目录和文档索引的对应条目。D-01 至 D-05 的授权与结果归各自候选。r6 软件仍为 `draft`，具体凭据机制、代码、数据库及正式 OpenAPI 发布由后续实施范围确定。

| 验收项 | 可观察结果 |
| --- | --- |
| D06-AC01 字段规则 | 规格和两稿均可区分 SMA 每次提交的完整信封、第三方必传的采样字段、接入时固定的配置和实际可省略的 JSON 键。第三方缺测指标省略键，`0` 与 `false` 保留。只有实时 `quality` 接收显式 `null` 并记为 `unknown`，历史需要明确的合格质量。 |
| D06-AC02 权限与发现 | GET 必传设备、采样组和目标，要求已认证且启用的写入身份具备对应准入，仅返回可写指标键、类型及可选单位，历史应用白名单。未认证及越权无定义泄露，业务读和管理权限分别校验，POST 复核准入。 |
| D06-AC03 最简请求与回执 | 两份第三方最简 JSON 可解析并符合固定接入示例的字段规则，共用原任务、时间和来源事件，历史显式含 `quality: good`。按目标独立识别重试，已存在的事件不因映射版本更新改变结果，内容变化可检出。双语讨论稿分别链接字段规则和两个样例，原 SMA 完整示例和原 POST 路径可核对。 |
| D06-AC04 文档边界 | 软件状态为草案，D-01 至 D-05 原范围、DEV 和 QA 历史保留。差异限本规格、双语讨论稿、角色记录及对应索引条目。 |

## 8. 后续验收口径与修订记录

以下场景供后续实施规格定稿和验证，当前状态为方案评审。

| 验收项 | 可观察结果 |
| --- | --- |
| AC01 配置复用 | 两条合成产线采用不同点位绑定，仅改配置即可通过同一套接口与四个页面查看各自数据。跨页线速度引用同一条实时事实，管理员编辑卡片的标题、排序、开关和指标绑定，写入方按稳定键和准入范围上报。 |
| AC02 实时一致性 | 独立采样组分别刷新，清洗动作组可独立于清洗温度与液位组。按设备、任务及组创建与覆盖快照，较旧的同身份采样保留较新值。缺测、`0`、`false` 和陈旧状态能明确区分。切卷原子替换，验证有卷、无卷和未知状态。 |
| AC03 历史独立性 | 各历史组按白名单和配置间隔选择真实样本，每间隔最多一份，缺样的间隔保持空白。生产参数与清洗动作组只更新实时。重试与同源样本重复提交只产生一条历史记录，按原任务、设备、组和时间可查，实时覆盖及卡片关闭后仍能查到历史。 |
| AC04 接口与权限 | 两路示例携带同一来源任务并按各键的标量类型校验。越权设备、未登记键、目标停用、组错配与类型错配得到可区分错误。普通读用户可查看获准设备的卡片、曲线和历史，管理列表及指标、槽位、卡片与曲线组配置由后端校验 admin 权限。历史及实时回执各自可追溯。 |
| AC05 首次启用 | 装配项目预设后，空库的实时查询显示缺测或空态，历史查询返回空序列。产线启用前写入准入关闭。启用后送入一份符合双路条件的合成炉区 1 样本，核对 1 条相应任务和组的实时快照、1 条历史及各自回执。无任务证据的来源样本不能建立任务记录。真实产线按独立批准的启用范围验证。 |
| AC06 共用卡片 | 四页使用同一组件，支持单项和多项。保存 10 个启用指标的卡片通过，第 11 个启用指标或重复引用得到明确校验错误。来自不同组的指标项各自保留来源、采集时间和新鲜度，缺测、`0` 与 `false` 可辨。两种语言的指标项标题按可选单位组合，值区只显示值。 |
| AC07 曲线组 | 炉区 1 的实际温度和设定温度按配置顺序从已存历史显示，缺样时断线。同单位的共用纵轴只标注一次单位，空单位省略标注。启用、隐藏或调整曲线序列后，历史白名单、写入和已存记录保持独立。 |
| AC08 任务与卷号 | 按来源证据从 A 单换到 B 单后，迟到的 A 单只归 A 单。B 单缺组时显示缺测，现场空闲或归属未确认时显示空态。卷号 `"000042"` 按字符串原样读回。任务和卷可取相同字符串，返工同卷使用新任务号，按两个任务号各自查询其历史。 |
| AC09 管理元数据 | 管理员可按任务、设备和组筛选两类列表，历史还支持时间筛选。两个列表均可分页，详情按指标配置显示名称、单位和采集值。普通读用户的管理请求被拒绝。实时只接受备注，下一次 SMA 覆盖保留原备注。历史只接受备注与管理标记，采集质量和原始值保持可核对。超出编辑白名单的字段被拒绝。 |
| AC10 槽位与名称 | 每目标每组可占用 100 个槽位，第 101 个绑定和重复关联被拒绝。停用仍占位，恢复保留原关联。已用绑定、类型及单位口径不能重配。同一温控样本分别进入实时 `01/02/03` 与历史 `07/08`，读回一致的原类型值。改中英文名称或标题只改变界面展示。 |
| AC11 发现与回执 | 发现响应的每个键均通过当前目标的写入资格校验，历史发现遵循产线与组的白名单。相同事件同内容重试返回原回执，同事件异内容报冲突。一次仅有一路提交成功时，另一路可独立重试；历史同源重复保持一行，较早实时样本产生 `stale` 回执。 |

| 修订 | 日期 | 范围与状态 |
| --- | --- | --- |
| r1 | 2026-11-07 | 形成四页共用指标配置、实时与历史独立存储、前端与 SMA 接口的方案草案。 |
| r2 | 2026-11-07 | 补充首版采样与历史白名单、旧数据和能耗切换建议、管理员字段设置、标量规则及两种固定卡片模板。交 Human Owner 评审。 |
| r3 | 2026-11-07 | 四页采用同一可配置卡片，每卡最多 10 项。过程监控新增独立曲线组展示配置。交 Human Owner 评审。 |
| r4 | 2026-11-09 | 补充来源任务归属、SMA 两路投递及两个管理员管理列表。D-03 限文档交付，软件方案待评审。 |
| r5 | 2026-11-09 | 从 0 到 1 定义首版启用、项目预设与验证顺序。D-04 限文档交付，软件方案待评审。 |
| r6 | 2026-11-09 | 补齐固定列、本地槽位、任务与卷号、两路写入和查询配置接口。D-05 限文档审阅，软件方案待评审。 |

实施范围、文件 allowlist、依赖与验收按实际决策定稿后进入精确 Revision 批准，随后由 Development 实施并交 fresh-context Verification，再由 Human Owner 最终验收。后续按表面使用 `frontend-ui`、`i18n-workflow`、`backend-arch`，SMA 运行时和 PLC 点位映射分别适用 `rust-runtime` 与 `plc-point-mapping`。 [开发工作流](../../.codex/workflows/development-lifecycle-workflow.md)

<a id="r7-implementation"></a>

## 9. r7 首版业务闭环

2026-11-11（Asia/Shanghai）。首版软件范围已获 Human Owner 批准，见 §9.5。§2–5 定义卡片、曲线、任务归属、槽位及接口语义。r7 以本节确定实现方式、隔离环境和验收口径，替代 §7.2 中首版与 SMA 产品并行实施的建议。D-01 至 D-06 属于原候选的文档记录。

### 9.1 交付面和前置事实

首版在隔离环境交付可运行的 Vue Web、FastAPI、MySQL 8.4.6 和两种集成调用。`GET /api/v1/integration/metric-definitions` 供接入方发现获准指标，`POST /api/v1/integration/equipment/latest-snapshots` 覆盖快照，`POST /api/v1/integration/monitor/history-samples` 追加历史。两种身份共用这三条路径。SMA 身份提交完整信封，第三方按 §5 省略由后端补齐的字段。两路独立提交与重试。

| 面向 | 首版交付 |
| --- | --- |
| 设备状态 | 生产参数、清洗、温控、传动四页共用配置化卡片与 `latest-cards`。选择获准设备后按现场已确认任务查询。支持加载、缺测、陈旧、空闲、任务未确认和请求失败状态。 |
| 过程监控 | 温度、传动、清洗三页共用配置化曲线，支持设备、任务号及采集时段查询。使用已有 ECharts 和主题，按原采集时间绘图，缺测留断点。 |
| 管理员 | 指标登记、槽位启停、卡片及曲线配置，实时与历史两套独立分页列表和详情。实时仅改备注，历史限备注及异常／已复核标记。表格沿用 AGENTS §8 列宽、记忆和恢复默认规则。 |
| 服务与库 | 模块 `equipment_observation` 通过 manifest 独占新接口和表，按 §3.3 保留快照、历史、各目标回执、指标及槽位。新增 `equipment_card_configs`、`monitor_curve_group_configs`，分别保存稳定键、页／类别、双语标题、开关、排序及有序引用 JSON。原表和原 writer 保留。 |
| 集成交付 | 提供两种可复跑 HTTP 调用和脱敏请求、响应、状态码及确认重试示例。用已入库的合成 v2 事实构造完整 SMA 信封，用独立第三方调用端走最简请求。SMA 产品运行和真实 DAA 接线按各自已获批准的范围接续。 |

Web 通过现有模块 manifest 将 `equipment.production-parameters`、`equipment.drive`、`equipment.temperature` 接到共用卡片页面，新增 `equipment.cleaning`。将 `monitor.temperature` 接到共用曲线页面，新增 `monitor.drive`、`monitor.cleaning`，撤下旧 `monitor.realtime` 路由和菜单入口。四个已沿用的 pageId 与 URL 保持，新增功能各只显示一个入口，独立的能耗与采集数据功能沿用原入口。两个模块分别增加管理入口。隔离环境的页面授权清单使用当前 pageId，移除退役 ID，实际项目授权的采用随运行切换审批。既有后端 API 维持原合同。

新页面使用所属模块的业务 facade 和实际 HTTP 响应。读取权限键为 `equipment-observation-read`、`monitor-observation-read`，分别覆盖设备状态和过程历史。两域的 `GET /api/v1/equipment/observation-options`、`GET /api/v1/monitor/observation-options` 分别返回当前登录身份获准设备的 ID 和双语名称，供本域页面筛选。详情、曲线和管理列表服务端先限制设备范围再查询。管理入口用现有 admin guard 并单独校验所选设备，机器凭据仅授权 §5 集成接口。页面采用既有 `requiresAdmin`、中英文 locale 及本机列宽机制。新业务读与写入使用持久数据。

工作基线为 `main` 工作树 `bcafa89fa31bdf62329bced89baebc193323a739` 及 [ARCH-ACQ-003 r2 验收](../ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收) 对应的实际 v2 源码。当前工作树中的 v2 迁移与路由尚有未提交文件，仅复制 HEAD 会缺失依赖。Development 建立脱敏基线清单，记录纳入的 v2 迁移、模型、服务和合同文件摘要及与验收记录的差异。发现依赖差异时先对读已核验候选，确认其合同和行为后再继续。通用计划／实绩仍按自己的实现规格推进。本版复用 [通用 `taskNo` 规则](../../docs/generic-task-workflow-discussion.zh-CN.md#task-identity)，以 v2 采样事实证明归属，不接入计划／实绩表或状态机。 [采集接线顺序](../ARCH-ACQ-001-acquisition-data-coordination/spec.md#3-两条业务线和最终接线) · [SMA 后续阶段](../../automation-world/semantic-mapping-agent/plans/SMA-001-cu-integration-and-scope-cleanup/spec.md#4-后续阶段仅目标与依赖)

### 9.2 任务事实、权限与写入

每台设备在服务端项目配置中明确绑定 `plcId`、`dbNumber`、`taskPointId`、一个精确空闲值和正数 `maxTaskAgeSeconds`。绑定点是现场 `activeTaskNo` 的稳定键，受控例用 `point-active-task-no`、`STRING[50]` 和空字符串空闲值。`plc_facts` 提供所属模块内的只读查询并通过 manifest 导出，`equipment_observation` 声明该依赖。只读查询使用 v2 现有有效期、登记实例、代次和目标探针语义。公开采集 GET 仍由原 provider 和原权限维护。 [v2 源码合同](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)

| 查询或投递 | 归属依据 |
| --- | --- |
| Web 当前任务 | 按设备绑定查询该点的有效最新记录并校验采集年龄。合法任务号为 `active`，已确认空闲值为 `idle`，未登记、过期、质量不良或值无效时为 `unknown`。卡片仅在 `active` 时选择该任务的快照。 |
| SMA 完整信封 | `plc_fact` 引用须指向同一份存储样本。用 §5 的 `(instanceId, sampleId)` 定位，从存储样本取得 DB、来源代次及序号，核对绑定的 PLC／DB、获准来源、引用点及 `data.sampledAt`。引用须包含绑定任务点，质量合格且在该时刻有效，值规范化后等于 `taskNo`。若引用另有 `sourceGeneration`、`configRevision` 或 `observedAt`，也须与所引用事实相符。 |
| 第三方直连 | 从绑定范围内查找 `sampledAt` 当时及之前最近的一份有效任务点观测。按原采集时间和同代次来源序号裁定顺序，并用该点自己的时间校验最大年龄。最近观测为空闲、无效、过期或不匹配即拒绝，不能跳过它借更早任务填值。查询限定配置窗口和来源范围。 |

无法证明任务或原采集时刻不一致时拒绝新事件，并返回可定位原因。已确认的迟到 A 单仍按 A 单保存，B 单界面只读 B 单快照。已持久确认的合法重试先在身份和目标准入内核对回执，事实过期不会丢失已存业务数据或回执。换用新的现场绑定或采集代次时，旧证据只有在仍能按获准范围证明时可接收新的业务事件。

`OBSERVATION_ENABLED` 默认 `false`，`OBSERVATION_PROFILE_FILE` 默认空。沿用后端设置解析入口，运行时从仓库外只读 profile 获取明确的目标 UUID／库名／revision、设备来源绑定、角色设备读范围、写入身份与按设备／采样组的历史规则。每个写入身份配置独立随机 Bearer 的 SHA-256 摘要、调用类型、接入映射标识及版本、允许的 `(equipmentId, groupKey, target, metricKeys)`，第三方另绑定 `sourceId`。采用 `plc_facts` 已有的摘要比较方式，独立验证本业务 profile，凭据或私有配置内容不进入仓库、浏览器和日志。显式授权成功才处理写入，缺少或无效凭据为 401，已认证但停用或越权为 403，配置／存储未就绪为 503。

请求严格校验 §5 的省略、`null`、类型和白名单。带偏移的采集时间统一转换为 `+08:00`，保留最多六位小数秒。新事件因输入或字段错误返回 422，事件身份和内容冲突及任务证据未获证实返回有明确原因的 409。历史 `good` 和设备组白名单由后端校验，§3.1 的选样间隔由发送端按原采集时间执行，合成 SMA 调用端和第三方接入说明均演示按间隔选样。看板按每组配置的陈旧阈值和实际采集时间判定新鲜度。服务端每次只保存请求明确选择的目标。快照覆盖保留行 ID 和管理员备注，历史只追加。持久回执和相应采集写入同事务提交，提交结果未知为 503，发送方凭相同事件及内容核对回执。后端分别验证 `stored`、`already_stored` 和实时 `stale` 的可重试行为。

### 9.3 数据库后继和运行范围

显式 Alembic revision `5f7a9c1e3b26` 接在当前唯一 head `4e6a8b0d2f14` 后。仅新增两张值表、两张指标和槽位表、两张展示配置表及一张回执表。沿用 §3.3 的键、索引、JSON 标量、`DATETIME(6)` 和 100 槽规则。回执另以 `task_evidence` JSON 留存已核验任务点的实例、样本、点位及原观测时间，便于原事实到期后追踪接受依据。首次迁移和应用启动不自动填入项目配置或采集数据。合成预设由可复跑的隔离测试步骤显式装配。

当前 v2 async 探针、sync 维护探针和 profile 解析固定要求 `4e6a8b0d2f14`。BE-010 另有采用 revision 白名单。为使同库新增观察表后采集与既有 typed 业务仍能使用，本版只将 `5f7a9c1e3b26` 添加为明确兼容版本，并继续要求 profile 与实际 revision 精确相等，同时保留目标 UUID、schema、MySQL 和时区校验。旧 profile 连到新 revision 仍拒绝。旧 profile 与旧 revision、更新后的隔离 profile 与新 revision 均须回归证明。采集表结构、v2 HTTP 合同、既有 typed 合同及维护数据口径由原任务继续维护。 [v2 async 探针](../../backend/app/plc_facts/crud/async_v2.py) · [v2 sync 探针](../../backend/app/plc_facts/crud/sync_v2_maintenance.py) · [BE-010 采用验证](../../backend/common/integration/storage.py)

交付源码指定为仓库内独立目录 `runtime/arch-obs-001-r7/source`。仅从明确批准的源码路径复制依赖，排除真实 `.env`、profile、数据库、日志、缓存和构建产物。当前共享树有后端／前端监听进程，开发、构建和验证均在该隔离交付目录完成。交接保存脱敏基线清单、可重建的源码补丁、候选摘要及启动入口，独立核验与最终交付指向同一源码目录。保留该目录供评审和后续整合，整合至当前运行树、切换运行和回收交付源码在另外确认后处理。项目工作树的任务三文件保留职责记录。

r7 的范围批准涵盖两个轮次各自新建的可丢弃 MySQL 8.4.6 测试资源（Development、Verification），包含在本机独立实例上创建、迁移、合成数据写读、隔离降级和回收。可用本机原生隔离实例或本机 `mysql:8.4.6` 镜像创建仅回环可达的新容器，容器名、数据目录／卷、schema、专用账号和端口均标明任务及轮次。DB 使用独立的 `13395`（DEV）／`13396`（QA），Web/API 使用另行核实空闲的回环端口。迁移和测试前核对新实例 UUID、精确 schema、专用账号、目标 revision 和环境来源。无可用隔离资源或缺主机权限时，记录实际缺项并继续源码可用检查；现有 `3307` dev 库、已运行的 `8000`／`5190` 服务、现场 PLC、DAA／SMA 产品配置、生产部署及 Git 发布不属于本轮操作范围。清理仅限本轮创建且核对归属的测试资源，保留验收所需脱敏证据。

### 9.4 文件范围与顺序

下列软件路径相对于隔离交付源码根目录。`**` 仅用于所列新模块或页面，既有文件只变更直接相关的项目。原共享工作树的本轮写入限于本 bundle 的角色记录、`evidence/r7-source.patch` 和 `evidence/r7-source-baseline.json`，以及协调者同步根 `PLAN.*`、`plans/README.*` 中的 ARCH-OBS-001 索引行。两份证据只含源码差异和文件摘要。

| 归属 | r7 文件范围 |
| --- | --- |
| FastAPI 业务 | `backend/app/equipment_observation/**`（新模块及双语模块说明）；`backend/app/plc_facts/manifest.py`、`services/observation_evidence.py`（新查询入口）、`crud/async_v2.py`、`crud/sync_v2_maintenance.py`、`v2_config.py`、`README.md`、`README.zh-CN.md`（路径均在 `backend/app/plc_facts/` 下）；`backend/common/integration/storage.py` 仅登记新兼容版本。 |
| DDL 与验证 | `backend/alembic/versions/20261111_1800_5f7a9c1e3b26_add_equipment_observation.py`；`backend/tests/test_equipment_observation*.py`、`backend/tests_mysql/test_equipment_observation*.py`；既有 `backend/tests/test_equipment_temperature_migration.py`、`test_legacy_acquisition_retirement.py`、`test_mapping_migration.py` 仅同步 head 断言并保留原 revision 链断言。 |
| Web | `frontend-js/src/app/equipment/` 的 `manifest.js`、`api/observations.js`、`locales/{zh-CN,en-US}.json`、`views/observations/**`、`components/observations/**`；`frontend-js/src/app/monitor/` 同名路径；`frontend-js/tests/module-registry/equipment-observation.test.mjs`。 |
| 合同与说明 | `contracts/published/http-api/equipment-observation-v1/**`（新的 OpenAPI、请求与响应向量及双语说明），`contracts/README.md`、`contracts/README.zh-CN.md` 的本合同索引，`docs/equipment-status-process-monitoring.md`、`docs/equipment-status-process-monitoring.zh-CN.md` 的首版走读，`CODE_INDEX.md` 对应新源码条目。历史合同文件原字节保留。 |

1. 固定隔离交付基线，先定请求、回执、配置及采样任务证据的验证夹具。
2. 编写迁移和后端事务，验证 v2 与既有 typed API 在新旧对应 revision 的行为，再接通新业务 HTTP。
3. 接入 Web 页面和管理配置，用合成事实、第三方最简请求及 SMA 完整信封分别完成写入到展示的验证。
4. 以同一候选运行独立 Verification，并用任务 `000042` 的炉区实际值和设定值完成可复跑走读。两种调用方式使用该任务的不同合成采样，每种调用内部的实时和历史共用同一来源样本。走读依次提供事实样本、指标发现、两路请求与回执、MySQL 记录及前端截图或定位证据，区分已验证的第三方 HTTP、SMA 协议兼容和后续 SMA 产品联调。

Development 应采用 `backend-arch`、`frontend-ui` 和 `i18n-workflow`，针对新模块执行 manifest 预检、受影响的 Python 测试、Alembic 链与新增段 `4e6a8b0d2f14:5f7a9c1e3b26` 的 offline SQL 检查、明确目标的隔离 MySQL 验证、`pnpm check:modules`、`pnpm test:modules`、`pnpm build` 及真实浏览器业务流。`rust-runtime` 和 `plc-point-mapping` 由后续 SMA／DAA 任务按其范围使用。

<a id="r7-acceptance"></a>

### 9.5 验收与批准

| 验收项 | 独立可观察结果 |
| --- | --- |
| R7-AC01 源码与隔离 | 交付目录的基线和候选可逐项复核。两轮证据标明各自实例 UUID、schema、迁移前后 revision、进程端口和资源回收情况。实际源码路径、允许差异、静态检查及构建结果可核对。 |
| R7-AC02 迁移和兼容 | 空隔离库可升级，已有 v2 受控样本的隔离库可从 `4e6a8b0d2f14` 升级；旧采集与 typed 数据不变。旧 profile／旧 revision 和新 profile／新 revision 通过各自读写及受控维护只读检查，错配和未知 revision 拒绝。隔离降级只撤 r7 新表。 |
| R7-AC03 接入合同 | 两种已授权身份实际调用共同的发现 GET 与两路 POST，核对字段、类型、历史白名单和实际入库。错误凭据、越权、第三方省略与 `null`、SMA 完整字段、禁用指标、坏质量历史和不合法类型覆盖。验证后端省略补齐信息只对第三方身份生效。 |
| R7-AC04 任务证据 | 使用 v2 真实 HTTP 接收的合成样本证明 A／B 换单、晚到 A、空闲、未知、过期或错绑与前导零卷号。SMA 伪造引用或错误原时刻被拒绝，第三方未获证实的任务号无法入库。B 单缺组显示缺测，已存 A 单按原 `taskNo` 可查。 |
| R7-AC05 数据与重试 | 独立真实 MySQL 核对新建、覆盖、持久回执、旧包 `stale`、同事件异内容冲突、同源历史去重、断开重试及两路只成功一路后的独立补投。两路同一次映射写入各自槽位，保留 `0`、`false` 和卷号文本，首次使用锁定及槽位上限可观察。 |
| R7-AC06 页面与权限 | 实际浏览器核对四页共用卡片、三页曲线、同单位纵轴、缺测、两类列表及相应编辑白名单、双语切换和列表列宽。既有四个 pageId 对应配置化页面，新增清洗和传动入口，旧过程实时监控退役且能耗、采集数据入口可用。两条受控产线复用同一套实现。普通读权限与机器权限不能操作管理接口，admin 仍受设备范围限制。 |
| R7-AC07 交接与复跑 | 以任务 `000042` 对照现场合成事实、请求、回执、库值和页面。第三方 HTTP 两路及合成 SMA 完整信封各有实际请求和数据库证据。明确后续 SMA 取数身份、产品投递及 DAA-010 的联调范围和前置条件，便于沿实际数据解释完整流程。 |

Human Owner 批准精确 `ARCH-OBS-001 r7` 及 §9.3 的隔离动作后，Development 才开始源码实施和写入 r7 `tasks.md`，交接后由 fresh-context Verification 写入 r7 `checklist.md`。r6 及之前的角色记录保留在各自历史区。r7 软件核验和最终验收只覆盖上述交付候选。 [项目 STD 规则](../../AGENTS.md#4-写入任务治理)

#### 9.5.1 r7 实施范围批准

2026-11-11（Asia/Shanghai），Human Owner 明确批准 `ARCH-OBS-001 r7` §9。批准前规格 SHA-256 为 `4ad249aaff31cdfd8077e9db044a2eb0957060565900e2c8136746ed74f3ecc1`。

> 批准 ARCH-OBS-001 r7，按 §9 在隔离环境实施并验证

本批准覆盖 §9 的源码交付和 §9.3 的隔离动作。当前状态为 `owner_approved`，交命名角色 `development` 按本节实施。软件独立核验与 Human Owner 最终验收依交付候选记录。

<a id="r8-dev-integration"></a>

## 10. r8：采集适配、管理列表与 dev 接入草案

2026-11-16（Asia/Shanghai）。本节是新的、待批准的精确实施范围；与 §1–9 有冲突时，以本节为准。§1–9 及 §9.5.1 是原方案和 r7 精确批准的历史，r7 的批准仅覆盖隔离候选和当时的隔离动作，不延伸到本节、正式工作树整合或真实 dev 数据库。r7 隔离候选的 QA3 为 `qa_passed`，Human Owner 最终验收待决定；它不能证明本节已实施、dev 已接入或实际 SMA 产品已联调。原 [Development 交接](tasks.md) 与 [Verification 记录](checklist.md) 保留 r7 状态和证据，r8 获批后再由对应角色分别记录新一轮工作。

**r7 原稿复核。** 原 r7 spec 的 SHA-256 为 `3ca7a9ec910a21ad141e349f15f2ea0df61a79cbf979f2e660d59fb55b530631`。本修订只改变顶部六条元数据并在原文之后追加本节；删除 r8 锚点前的空行及其后全部内容，再将顶部六条恢复为 `Revision: r7`、`Status: owner_approved`、`Handoff: r7 §9 已获 Human Owner 精确批准，交命名角色 `development` 实施`、`Acceptance Chain Reference: 本稿第 9 节及 Development Lifecycle Workflow`、`Related Task: ARCH-ACQ-001, ARCH-ACQ-003, ARCH-BE-010, aiis-ics-arch.aw.sma::SMA-004`、`Updated: 2026-11-11`，即可还原原稿并按该摘要校验。

### 10.1 交付结果与边界

| 部分 | r8 交付目标 |
| --- | --- |
| 设备状态 | 生产参数、清洗工艺、温控工艺、传动工艺四页共用指标和卡片配置，每卡最多 10 项；显示项目按稳定 `metricKey` 取值。 |
| 过程监控 | 温度、传动、清洗三页展示管理员配置的曲线组；曲线是否显示与是否保留历史相互独立，同单位共用纵轴时单位标一次。 |
| 管理数据 | 两个 admin 列表分别面向实时快照和过程历史，参考计划／实绩字段设置，管理员可配置并直接在列表显示指标列；各有分页、筛选和详情。编辑仅限实时备注、历史备注及异常／已复核标记，不能改采集原值。 |
| 接入 | SMA 与第三方继续共用 §5 的发现 GET 和两条写入路径，实时与历史分别请求、独立回执和重试。外部字段仍为 `metricKey`，不暴露本地槽位。 |
| 基线整合 | 在核对正式工作树现状与并行修改后，将 r7 候选所需范围适配并整合至项目正式交付工作树，接入已采用的采集来源登记模型，形成可核验的源码候选和迁移计划。 |

`id` 是各主表的行主键；`task_no` 是跨系统业务任务号，按原合同保留字符串和前导零，用于筛选和关联，不代替 `id`。卷号是生产参数里的普通指标值；任务事实由采集点证明，不以计划／实绩表或状态机推断。实时以 `equipment_id + task_no + group_key` 定位并整组覆盖，保留行 ID 和管理员备注：本次该组未提交的指标从新快照中移除并显示缺测，不沿用上次值；其他组不受影响。历史以新行追加、同源样本按 §3.3 去重。实时可含比历史更多的指标；两路不自动复制或同步，历史留存仅由历史接入白名单及发送侧采样间隔决定。已写入的过程历史不随采集事实 TTL 清理，首版不配置自动到期删除；后续容量治理另行决策。

本次只修订 spec。r8 未批准实施；SMA/DAA 产品源码、实际 PLC、生产部署及发布不在本范围。实际 dev DDL、profile／凭据变更、合成写入、服务切换与测试数据清理均须先取得针对目标和操作的明确授权；本稿不会触发或代替该授权。Human Owner 可以在同一条指令中分别明确批准 r8 软件范围、指定 dev 目标及具体物理操作，不要求为每项操作另发一轮消息；未明确授权的动作不执行。Redis、原采集值更正和新的 PLC 跨 DB 任务归属协议均不在首版。

### 10.2 七张表、槽位及可恢复迁移

首版为新建表，不回填或删除计划、实绩、采集事实及旧业务数据。保持 §3.3 的类型、键、回执与约束；下表的两个主表名替代 §3.3 的旧候选名，API 路径保持原样。

| 物理表 | 职责及关键约束 |
| --- | --- |
| `equipment_status_main` | 实时快照；`id` 主键，`(equipment_id, task_no, group_key)` 唯一；采集时间、质量、来源样本键、回执、`local_values JSON`、备注及创建／更新时间。较新采样整组替换，旧包不倒退；同时间不同内容冲突，管理备注不被覆盖。 |
| `process_monitor_main` | 过程历史；独立 `id` 主键、任务／设备／组／采集时间、质量、来源样本键、回执、`local_values JSON`、备注与 `review_mark`。同一 `(equipment_id, task_no, group_key, sampled_at, source_sample_key)` 唯一；保留 §3.3 的任务及设备组时间索引。 |
| `equipment_metric_configs` | 唯一 `metric_key`、来源组、类别、中英文名、`number/boolean/string` 类型、可空单位与小数位；名称可改，已用指标物理含义、类型和单位口径不重定义。 |
| `equipment_metric_slot_bindings` | `(target, group_key, slot_no)` 主键、同目标组内 `metric_key` 唯一、写入开关 `enabled`、首次使用时间；按下述增加列表开关和顺序。 |
| `equipment_card_configs` | 卡片稳定键、页面、中英文标题、开关、顺序和有序指标引用；最多 10 项。 |
| `monitor_curve_group_configs` | 曲线组稳定键、类别、中英文标题、开关、顺序和有序历史指标引用。 |
| `metric_ingest_receipts` | 两路各自的 `(target, producer_id, event_id)` 唯一回执、请求摘要、结果、映射、来源引用及 `task_evidence JSON`。业务写入与对应回执同一事务提交。 |

每目标、每组各有 100 个本地槽，`local_values` 的键为 `"01"`–`"100"`，值是原类型 JSON 标量；没有同步槽位。初次存值后绑定固定，停用仍占槽并用于解码旧记录。新业务含义使用新指标键和空槽。实时与历史可使用不同槽号；同槽号也可在不同组指向不同指标，绝不能仅凭槽号解释。

列表配置不新建表：在 `equipment_metric_slot_bindings` 增加 `list_visible BOOLEAN NOT NULL DEFAULT false` 与可空的非负 `list_order INT`。字段归属该目标、组及槽位，`NULL` 表示使用默认顺序；保存时服务端校验范围及既有绑定。指标列可选自该目标已登记且有绑定的指标；`list_visible` 控制该目标管理列表是否出现，`enabled` 只控制该目标的新值准入，两者互不隐含。历史指标停写后，若列表仍选中它，历史旧值继续按原绑定显示；不能清除旧值或隐藏整列。列表开关、卡片开关、曲线开关和历史白名单彼此独立。未配置任何指标列时只显示固定列。

迁移必须正面处理分叉：r7 隔离迁移 `4e6a8b0d2f14 → 5f7a9c1e3b26` 与现有计划／采集链是两个后继，不能将旧 patch 原样套用、`stamp` 版本或修改已存在的迁移历史。当前源码链为 `4e6a8b0d2f14 → 5f7a9c1e3b25 → 6a8c0e2b4d16 → 7b9d1f3a5c7e`。r8 拟新增单一前向 revision `8c0e2a4d6f18`，明确 `down_revision = 7b9d1f3a5c7e`，新建本节七表和上述列表列；不登记 r7 的 `5f7a9c1e3b26` 到正式链。实施与真实执行前分别重新核对源码及目标均为预期唯一 head，若共享树或目标已变化则停止并回 PM 调整修订，不猜测后继或另造第二 head。

迁移需保留现有表、数据、索引、来源、水位、访问及已采用的 typed 业务合同。MySQL DDL 可能部分成功而 Alembic revision 未前进：失败时停止应用、保全执行前后 schema 与日志，按实际对象逐一核对、制定有数据保护的恢复或修复步骤；不得盲目重试、删表、强行标记或重写旧 revision。现有可用恢复材料及恢复方式在执行前如实核对，并向 Owner 说明实际可恢复性；不假定存在备份，也不强制新建备份或新库。不得把尚未验证的降级称作 dev 恢复方案。

### 10.3 管理列表、字段设置与 API

管理员从两个管理页的字段设置选择本目标已绑定指标的列表显示和排序，复用指标的 `nameZh`、`nameEn` 和可空 `unit`；有单位时表头显示“名称 (单位)”，单元格只显示值。两个目标各自配置，不改写指标定义；已有 [计划／实绩列表](../../frontend-js/src/app/plan/components/TaskPage.vue) 和 [字段显示顺序](../../backend/app/task/services/async_fields.py) 仅作为交互与 `visible/order` 思路参考。首版不照搬其按槽位拼接前端列键的方式，也不把停写指标从已选列表排除。

固定列至少显示 `id`、设备、任务号、采样组、采样时间、采集质量，历史另有复核标记；指标列按目标统一配置顺序显示。支持设备、任务号、组筛选，历史另支持采集时间范围；列表查询先按当前 admin 的设备范围约束再过滤、计数和分页，不能用未经授权的设备汇总或通过总数泄漏。各行是一台设备、一个任务、一个采样组的一条主表记录，非跨组聚合；跨组未采集的指标显示“—”。`0`、`false`、空字符串是有效值，按自身类型保留显示，不以真假值判断缺测。

| 方法与路径 | r8 合同 |
| --- | --- |
| `GET /api/v1/equipment/observation-list-columns?target=latest` 或 `?target=history` | admin 查询该目标所有已绑定指标及各自的 `groupKey`、`slotNo`、`metricKey`、写入开关、列表显示与顺序、中英文名、类型和单位，供配置和展示；不是机器指标发现接口。按非空 `listOrder` 升序、空值在后，相同顺序再按 `groupKey`、`metricKey` 升序，结果确定且两目标独立。 |
| `GET /api/v1/equipment/metric-slot-bindings?target=...&groupKey=...` | 在原返回字段上增加 `listVisible`、`listOrder`，继续包含停用绑定。 |
| `PATCH /api/v1/equipment/metric-slot-bindings/{target}/{groupKey}/{slotNo}` | 在原 `enabled` 外允许部分提交 `listVisible` 和 `listOrder`。未提交字段不变；`listOrder: null` 恢复默认排序，其余 `null`、非法类型、越界、未知字段或不存在的绑定拒绝；只改变对应绑定及其显示设置，不迁移或改写原值。 |
| `GET /api/v1/equipment/admin/latest-snapshots` | admin 读取实时分页；支持 `equipmentId`、`taskNo`、`groupKey`、`page`、`pageSize`。只读 `equipment_status_main`。 |
| `GET /api/v1/monitor/admin/history-samples` | admin 读取历史分页；除以上筛选，还支持 `from`、`to`。只读 `process_monitor_main`。 |
| 两个资源的 `GET /{id}`、`PATCH /{id}` | 按对应主表 ID 及设备范围读详情或更新白名单；实时只可 `remark`，历史只可 `remark`、`reviewMark`。非法字段服务端拒绝，管理标记与来源质量分开。 |

`observation-list-columns` 成功响应的 `data` 形状示例；即使 `enabled=false`，这里仍可配置和返回旧值列：

```json
{
  "target": "history",
  "items": [
    {
      "groupKey": "temperature",
      "slotNo": 7,
      "metricKey": "furnaceZone1Actual",
      "enabled": false,
      "listVisible": true,
      "listOrder": 10,
      "nameZh": "加热区1实际温度",
      "nameEn": "Heating zone 1 actual temperature",
      "valueType": "number",
      "unit": "°C",
      "decimals": 1
    }
  ]
}
```

例如向 `PATCH /api/v1/equipment/metric-slot-bindings/history/temperature/7` 提交 `{"listVisible": true, "listOrder": 10}`，只改变历史列表显示；成功响应返回更新后的该条绑定（包括 `enabled`、`listVisible`、`listOrder`），不得因此开启写入、增删数据或改变实时列表。

列表沿用 r7 响应外壳 `{code, message, data: {items, total, page, pageSize, totalPages}}`。每个 `items[]` 带固定字段及 `values: [{metricKey, nameZh, nameEn, value, valueType, unit, decimals}]`，按当前记录的目标和 `groupKey` 解析本行实际存有的槽位，允许返回该行全部已存指标；前端只按列配置选择显示。停用绑定仍参与解码，未存的指标不出现在 `values`；不根据其他组或另一目标的同槽号补值。示例：`temperature` 组 01 为 `temperatureActual`，`drive` 组 01 为 `driveSpeed` 时，两行各只在自身指标列显示对应值。

实时按 `id DESC`、历史按 `sampled_at DESC, id DESC` 稳定分页；`page >= 1`、`pageSize 1–100`，无结果返回空页，时间端点遵循项目上海时间合同，`from`／`to` 均包含边界且起始不得晚于结束。确定的排序在数据集不变时稳定；并发写入可使 offset 分页的行位置变化，不承诺跨请求固定快照。首版不承诺按动态指标排序或筛选；固定排序由服务端执行，不在已分页结果中伪造全局排序。前端以 `metricKey` 为列和列宽稳定标识，并按应用、两张表分别保存本机列宽；语言切换、筛选、翻页、刷新及重开后保留，可恢复默认，失效配置回退默认。切换目标、筛选或列配置后的异步响应不得覆盖新页面的数据或造成跨页、跨组串值。

### 10.4 采集登记、任务证据与接入

基线为已最终验收并在 dev 采用的 [ARCH-ACQ-004 r4](../ARCH-ACQ-004-acquisition-source-registry/checklist.md)；[ARCH-ACQ-005 r1](../ARCH-ACQ-005-acquisition-source-deletion/checklist.md) 已通过独立 QA，最终验收仍待 Human Owner。正式源码中的 `plc_source_registry` 是 PLC 当前 `(plcId, instanceId, sourceGeneration)` 的事实来源；采集 profile 是 target-only，DB 号属于采样事实，不再采用 r2 `readDbNumbers` 或按旧三元 sources tuple 猜测 DB 准入。OBS 自己的受控 profile 仍需设备绑定 `plcId`、`dbNumber`、`taskPointId`、精确空闲值和正的最大任务年龄，并分别限制角色设备及写入身份、目标、组和指标。采集公开 GET 沿用其现有权限和行为；OBS 通过 `plc_facts` manifest 导出的内部只读服务取证，不能把该服务当作公开无授权接口。

实时当前任务只采纳登记的当前实例和代次、匹配 PLC/DB/点位、质量 `good`、有效且不超龄的任务事实；合法任务号为 active，精确空闲值为 idle，未登记、错绑、过期、坏质量或无效值为 unknown。active 才读取该任务快照，不能用旧值假装当前任务。来源切换或删除后，新的任务判断不得继续使用旧身份的 latest；ACQ-005 的公开历史仍可在原有效期内按其合同查询，不得为此删除旧事实。已经保存的 OBS 历史和回执按业务权限持续可查。

新写入在同一事务内以当前来源登记为准验证任务证据，并与来源切换／删除协调登记行锁；先提交的合法事件与删除／切换后的新事件必须各自有确定结果，避免校验后换代仍入库。SMA 的 `plc_fact` 引用必须能在实际已入库 v2 样本中核验：任务点和映射点来自同一份样本、同一 PLC/DB/实例/代次及原采集时刻；可选引用字段如代次、配置版本和观测时间若提供亦须一致。该前提只覆盖同 DB 同样本场景：现场任务点与工艺点跨 DB 时，本稿不假定可按同一帧证明，也不编造跨帧关联；应先确定证据和顺序合同并另行修订后实施。

第三方仍按 §5 以外部事件证明自身样本；任务归属另从绑定来源在其 `sampledAt` 当时或之前最近的合格任务观测证明，按原时刻及来源序号确定顺序，空闲、无效、过期或任务不匹配时拒绝，不跳过较新观测回借旧任务。迟到但证据仍可按当前准入核验的 A 单写 A，B 页不会显示 A。新事件不可证明时拒绝；在认证、目标准入和内容相同的前提下，已持久回执的重试可先核对既有回执，不因任务事实后来过期而丢失结果。伪造引用、代次不匹配和不同内容复用事件号均不得新增业务记录。

SMA 和第三方使用同一三接口：`GET /api/v1/integration/metric-definitions` 按设备、组、目标返回获准且启用的指标；`POST /api/v1/integration/equipment/latest-snapshots` 写实时；`POST /api/v1/integration/monitor/history-samples` 写历史。机器 Bearer 和授权范围独立于管理员／业务读权限。SMA 每次提供完整信封及可核验 `plc_fact`；第三方只按 §5 的明确省略规则，由已配置身份补齐可省字段，并每次提交外部事件、任务号、原采集时间和非空指标。实时省略质量按 `unknown`，历史必须明确 `good`；`null` 与缺项按 §5 区分。每个 `values` 项是稳定指标键对应的单一数字、布尔或字符串；每路可选择不同指标，分别上报并原事件重试。可复用 §5 已有的 [实时最简 JSON](#third-party-latest-example) 和 [历史最简 JSON](#third-party-history-example)，完整示例和错误码以本 spec 与后续获批合同为准。

### 10.5 dev 接入准备、切换及恢复

2026-11-16 协调者对本机 `127.0.0.1:3307 / industrial_level_2_system` 所做**只读事务快照**：MySQL 8.4.6、上海 `+08:00`，唯一 revision `7b9d1f3a5c7e`；`plan_main`、`performance_main`、`plc_facts_history`、`plc_facts_latest`、`plc_source_registry` 存在；两张新主表、r7 两旧名和五张观察配置／回执表均不存在。已采用采集 profile 为 target-only 且与该时点 UUID／schema／revision 匹配；latest 共 6 行，有效 `good STRING` 任务点 0。API `8000` 和 Web `5190` 已有监听。此为时点证据，不是新任务 QA 或可直接写入的许可；不得将该快照当作未来条件保证。

1. **可先只读准备**：核对仓库及并行工作、r7 补丁／候选来源和当前源码单一 head；通过只读方式重查目标服务身份、server UUID、schema、MySQL 版本与会话时区、实际 `alembic_version`、新旧候选表名碰撞、目标 profile 路径与权限、任务点质量／类型、已有数据和来源登记。只记录脱敏摘要，不输出密钥。核对当前 reader／writer 和用户启动进程；无任务点时页面应是 unknown，不能补造事实称已接通。
2. **形成待审批执行包**：确定源代码和候选摘要、明确目标和操作者、升级 SQL 及预期七表、适配后的采集与 OBS 目标 revision、按顺序的维护窗口／reader writer 协调、配置启用、回归方案、失败处置及现有可用恢复材料。明确是否采用现有经授权的测试资源和进程；不要求为了本任务另建隔离库或强制重启用户进程。
3. **仅在目标和动作获明确批准后**：按执行前复核的状态协调写入者，在指定 dev 目标执行唯一后继迁移及经批准的私有配置变更；重新校验 UUID、库、单一 revision、七表结构／索引、两套 profile 的版本匹配与 guard。保留原采集登记、事实、计划／实绩数据及原私有配置；不把示例凭据提交到仓库。真实服务由已授权的负责人在确认窗口切换，未授权时不停止、替换或重启现有服务。
4. **仅在明确授权目标及合成写入动作后**：预先检查测试设备／组、任务、PLC／实例／代次／样本和事件标识不会撞到已有数据；记录本次创建的精确主键与受影响对象，走两种身份、两路和页面读取。使用有明确所有权及回收条件的测试数据，结束后仅按获准范围清理本次对象并对账；不得删除、覆盖或重置原业务来源、事实、管理信息或他人资源。每次证据说明读取的是哪个源码、profile、数据库与进程。
5. **失败处理**：任何版本不符、对象碰撞、未知写入者或部分 DDL 均停止，按第 10.2 节核对现场和恢复材料后提报处理，不自动 stamp／降级。实际 profile 指向新 revision 前旧服务、采集维护与 typed 业务的版本守卫和可用性须经过验证并协调，避免把短暂错误误报为数据库损坏。

后端实现需同时适配采集 `v2_config.py` profile 校验、async 与 sync／维护目标 revision 守卫、OBS 自身 profile、[typed 业务的版本白名单](../../backend/common/integration/storage.py) 等全部相关入口：旧目标使用与之相配的旧 profile，已迁移目标使用明确允许的新 revision 且 profile、实际库、UUID、schema 与时区严格一致；错配或未知 revision 拒绝，不使用无条件放宽。验证原采集写读、删除来源后的历史查询和维护入口，以及既有 typed 业务访问与数据保全。

### 10.6 实施顺序、允许范围与交接

Human Owner 批准精确 `ARCH-OBS-001 r8` 后，Development 才在下列范围实施并记录 `tasks.md`。本修订是待审工作合同，不是本轮实际改代码许可；具体 dev DDL、配置、服务切换和合成数据动作按 §10.5 再确认目标及授权。新旧并行任务触及相同文件时先核对其未提交修改并协调，不能覆盖别人的工作。原 r7 冻结候选与 QA3 证据保持可复核；正式交付工作树才是后续源码整合和启动入口，不能仅留临时副本。

| 范围 | r8 未来获批后允许的直接相关文件 |
| --- | --- |
| 后端与迁移 | `backend/app/equipment_observation/**` 新模块；`backend/alembic/versions/*_8c0e2a4d6f18_*.py` 新后继；`backend/app/plc_facts/{manifest.py,v2_config.py,crud/async_v2.py,crud/sync_v2_maintenance.py,services/observation_evidence.py,README.md,README.zh-CN.md}` 的 OBS 适配和守卫；`backend/common/integration/storage.py` 的明确兼容版本。其他已采用采集业务和合同保持现状。 |
| Web | `frontend-js/src/app/equipment/` 与 `frontend-js/src/app/monitor/` 各自的 `manifest.js`、`api/observations.js`、`locales/{zh-CN,en-US}.json`、`views/observations/**`、`components/observations/**`。不扩大到无关页面，复用现有公共列宽工具。 |
| 受影响测试 | `backend/tests/test_equipment_observation*.py`、`backend/tests_mysql/test_equipment_observation*.py`；`backend/tests/test_business_integration_migration.py`、`test_legacy_acquisition_retirement.py`、`test_mapping_migration.py`、`test_equipment_temperature_migration.py`、`test_acquisition_source_registry.py`、`test_acquisition_data_browse.py`、`test_plc_facts_v2.py`；`frontend-js/tests/module-registry/{equipment-observation.test.mjs,page-access.test.mjs,registry.test.mjs}` 及本功能定向测试。只调整受本修订影响的断言，保留原版本链、表／路由保护与其他覆盖。 |
| 合同与文档 | `contracts/published/http-api/equipment-observation-v1/**` 新合同及向量、`contracts/README{,.zh-CN}.md` 对应索引、`docs/equipment-status-process-monitoring{,.zh-CN}.md` 及直接相关索引、`CODE_INDEX.md` 的相关条目；不覆盖既有已发布采集合同快照。 |
| 角色记录 | Development 仅按其职责写本任务 `tasks.md`；交接后 fresh-context Verification 写 `checklist.md`。它们各自保留 r7 历史，不改写先前 QA 结果。 |

1. 固定工作树、r7 候选和 ACQ-004/005 实际差异，确定单一 head 与源码整合清单；先做无数据库写入的接口、任务证据和迁移检查。
2. 按 10.2／10.4 补齐新迁移、版本守卫、后端事务与按组解码；验证旧业务与采集合同。按项目 `backend-arch` skill 开发，涉及接口和来源事实遵循对应采集合同。
3. 实现两套列表动态指标列及字段设置，接上四个卡片页和三类曲线页；遵循 `frontend-ui` 与 `i18n-workflow`，核对中文英文和实际接口。
4. 先完成可在当前获准资源上执行的验证，准备 10.5 执行包及实际目标授权；在授权范围内再完成 dev 迁移、合成两种调用和端到端读取。Development 记录命令、结果、差异与资源归属，fresh-context Verification 针对同一候选独立验证，再交 Human Owner 最终验收。SMA 产品或真实设备联调由后续相应任务批准。

### 10.7 r8 验收标准

| 编号 | 可独立观察的结果 |
| --- | --- |
| R8-AC01 基线与迁移 | 交付树与 r7 可追溯；唯一前向 head 是获批后继，七表及键、100 槽、列表字段与索引符合 10.2。带既有计划／实绩和采集数据的获准目标迁移前后对账，旧数据、登记、索引和 typed 行为不变；实际目标、版本与恢复能力如实记录。 |
| R8-AC02 列表与列设置 | 两个 admin 列表独立配置指标列和顺序，直接显示实时及历史各自行值；同一槽号不同组与两目标不同绑定不串值，停写历史指标后已选列仍显示旧值。覆盖缺测、`0`、`false`、空字符串、双语单位、列宽记忆与复位、筛选分页、请求竞态和固定排序。 |
| R8-AC03 权限与管理 | 服务端验证管理配置需 admin；涉及设备的列表、详情和 PATCH 还须验证该 admin 的设备范围。普通用户、机器身份或越权设备无法读取管理数据及总数或修改。实时只可改备注、历史只可改备注／标记，非法字段拒绝且采集原值和回执不变。 |
| R8-AC04 采集适配 | 当前登记三身份、指定 DB 和任务点、真实有效期、质量、idle／unknown、来源切换与删除都可观察；采集公开历史保留原合同。核对同样本 SMA 引用真伪、迟到换单、前导零、已确认回执重放及写入与接管／删除的事务顺序；跨 DB 未被冒充为已支持。 |
| R8-AC05 外部 HTTP | SMA 完整信封和第三方最简请求分别实际调用同一发现 GET 和两路 POST；核对补齐、鉴权、类型、单位、历史白名单、间隔、整组覆盖且遗漏项变缺测、其他组不变、增量历史、质量、同源去重、重复事件及独立重试与持久回执。HTTP、数据库和管理页面对得上。 |
| R8-AC06 页面闭环 | 四个设备卡片页和三类曲线页按配置显示、缺测和空闲／未知正确；单卡不超 10 项，曲线显示与留存可分别启停，同单位纵轴标识正确；旧过程实时入口按 r7 退役，既有采集和能耗入口可用。 |
| R8-AC07 兼容和测试 | 旧、新配套 revision 分别可用，错配和未知版本拒绝；采集 async、sync／维护和 typed 业务回归。r7 QA3 记录的两项后端、四项前端旧断言在 r8 允许按实际新 head、七表与退役路由修正并重跑，保留有效保护；任何剩余失败、跳过或未执行须如实记录，不以局部 QA 替代全套通过。 |
| R8-AC08 交接和 dev 边界 | 验证证据区分源码测试、经授权的 dev 物理变更、合成 SMA 信封、SMA 产品实际投递和真实设备；列出版本、目标、记录及清理结果。未获 dev 物理操作授权时保持待执行，不能声称已接入。独立 QA 结果不等于 Human Owner 最终验收或生产投运。 |

Human Owner 审阅并明确批准本精确 revision 后，按项目 STD 顺序交由 Development 和 fresh-context Verification；真实 dev 操作仍依 §10.5 的目标与动作授权。对外说明按实际已验证范围区分规格、软件候选、dev 接入、SMA 产品和现场设备。

<a id="r8-approval"></a>

### 10.8 r8 Human Owner 精确批准与交接

2026-11-16（Asia/Shanghai），Human Owner 明确批准 `ARCH-OBS-001 r8` §10，并对具体 dev 目标与操作给出以下指令。批准前 r8 规格 SHA-256 为 `bd661411267b8b1b13368ad298a93f8492200aaea3ef0ebbe27321d15b0b29ce`。

> 批准 ARCH-OBS-001 r8 §10，按方案实施并验证。同时授权对 dev 库 127.0.0.1:3307 / industrial_level_2_system 执行迁移、必要配置和合成数据联调，保留现有数据，只清理本次测试数据。完成后告诉我如何验收。

本批准覆盖 §10 的软件实施和验证，以及指定 `127.0.0.1:3307 / industrial_level_2_system` 的迁移、必要配置、合成数据联调和仅清理本次测试数据，按 §10.2、§10.5 与 §10.6 的核对、保全及恢复边界执行。现有数据必须保留。§10.1 和 §10.6 中关于“本次只修订 spec”“r8 未批准实施”“待审工作合同”的文字记述批准前状态；本段不改变原有范围、验收标准或历史记录。

当前规格状态为 `owner_approved`，交实际命名角色 `development` 按获批范围实施，在 `tasks.md` 记录源码与 dev 目标的真实操作、自检和 `developer_handoff`。交接后由 fresh-context 命名 `verification` 对精确候选及授权动作独立验证并写 `checklist.md`，再由 Human Owner 进行最终验收。本批准不视为已实施、已完成 dev 接入、QA 通过或最终验收；未明确授权停止、替换或重启现有用户服务，也不扩展到实际 PLC、DAA/SMA 产品运行、生产部署或发布。

<a id="r9-mapping-declaration"></a>

## 11. r9 候选：SMA 指标映射点声明与回执

2026-11-16（Asia/Shanghai）。**本节是待审阅的 `draft`，不是 Human Owner 对技术形式或实施范围的批准。** 依据 [r8 独立验证 R8-QA-001](checklist.md#r8-qa-001sma-映射用点引用可全部省略)，本节提出一个较小的候选：由 SMA 在请求中显式声明本次指标映射使用的点。Human Owner 的选择和对精确 r9 的批准仍待确认；如选择其他表达或不接受声明的可信边界，应先调整本节再实施。与 §1–10 冲突时，本节在获批后对 r9 范围优先；§10.8 是 r8 的批准历史，不把其原先 `owner_approved` 文字解释成 r9 已获批准。

已发生的 r8 事实继续由 [Development 交接](tasks.md) 与 [Verification 记录](checklist.md) 分别维护：指定 dev 库已从 `7b9d1f3a5c7e` 迁至 `8c0e2a4d6f18`，r8 独立 QA 为 `qa_failed`，R8-QA-001 及未完成的验证保留。r9 不回滚或重做该迁移，也不表示已有数据、既有部署或 r8 验收状态发生变化。

### 11.1 问题和可信边界

现行 SMA 请求的 `sourceRefs` 有同一样本中的真实任务点时，后端可以核实任务归属，但请求本身没有区分哪些点被用于业务指标。QA 的两条真实请求只引用任务点，仍成功写入实时和历史；现有合同又要求引用映射用点，因此“只引用任务点”无法区分**漏报映射点**、**任务点本身兼作指标点**及**指标全部由常量产生**。不得推断后二者不合法，也不得把一个任意添加的真实点当成逐指标映射已经得到证明。

本候选只让发送方声明本次指标所用事实点的集合。后端可核验声明格式、声明点被引用、实际样本和采集来源身份，但没有可信的 `metricKey → pointId` 映射登记，也不重算 SMA 的映射或转换。声明某个点、声明为空数组或提供映射 ID 都不能证明该点确实参与运算、结果由该点算出、其他点未参与或整包确实全为常量。这是发送方自报及可验证来源引用，不是逐指标血缘或防伪证明；需要可信映射及运算核验时另行设计并批准。

现有 SMA 产品在本任务期间不修改，其已接受范围是配置和纯预览，正常投递尚未启用。本地配置已有 `fact` 与 `constant` 绑定；本节不声称已存在目标合同的自动组包、单位换算或实际产品投递。将来如果 SMA 支持事实转换或单位换算，仍应声明实际参与映射的原始事实点；后端不通过比较原始点值与指标值来猜测映射是否正确。SMA 产品自动生成声明和真实 DAA/SMA 接线另归其任务。

### 11.2 候选请求与准入

两条写入路径和 `aiis.metric-ingest/v1` 信封保留。在新 SMA 事件中新增信封顶层 `mappedPointIds`，与 `sourceRefs` 和 `data` 同级；它是本次 `data.values` 涉及的事实点 `pointId` 集合，不是每个 `metricKey` 的逐项绑定。SMA 继续提供已配置任务点的 `plc_fact` 引用，其他声明的点各自也须在 `sourceRefs` 中有引用。指标值仍为按 `metricKey` 上报的 JSON 标量，实时与历史分别提交和确认。因现有 v1 接收端不认识该字段、修订后新 SMA 事件又要求显式提供该字段，这是 **SMA 新事件的合同收紧**；不能把旧发送程序视为已适配。旧已持久回执及第三方按下文处理，不声明本修订已发布或真实 SMA 已接入。

例如炉区 1 的实际温度绑定采集点、设定温度由发送方配置为常量：

```json
{
  "contractVersion": "aiis.metric-ingest/v1",
  "producerId": "sma-line-01",
  "eventId": "temperature-42-latest",
  "mappingId": "temperature-metrics",
  "mappingRevision": "r1",
  "sourceRefs": [
    {"kind": "plc_fact", "instanceId": "daa-01", "plcId": "plc-01", "sampleId": "sample-42", "pointId": "point-active-task-no"},
    {"kind": "plc_fact", "instanceId": "daa-01", "plcId": "plc-01", "sampleId": "sample-42", "pointId": "point-zone1-temp-act"}
  ],
  "mappedPointIds": ["point-zone1-temp-act"],
  "data": {
    "equipmentId": "line-01",
    "taskNo": "000042",
    "groupKey": "temperature",
    "sampledAt": "2026-11-16T09:30:00.123+08:00",
    "quality": "good",
    "values": {"furnaceZone1Actual": 810.2, "furnaceZone1Set": 815.0}
  }
}
```

上例的设定值为示例中的发送方常量，不能从数字 `815.0` 或字段名推断它是常量。候选准入规则如下：

1. **新 SMA 事件显式声明。** `mappedPointIds` 必须是 JSON 字符串数组，最多 128 个互不重复的有效 `pointId`；`null`、缺失、非法元素、重复或超限返回 HTTP 422 和稳定的 `equipment_observation.mapped_points`。集合顺序不代表语义，进入摘要和持久记录前以确定顺序归一。空数组可用，不得把缺失自动补为 `[]`。
2. **事实点及任务点。** 非空数组中的每个点必须有对应的 `plc_fact` 引用，否则返回 422；任务点始终必须有引用，即使数组为空也须按 §10.4 核验合法任务。所有引用继续来自同一个已持久、未到期、采样时间吻合的 PLC/DB 样本，并满足设备绑定、当前 `plcId`/`instanceId`/`sourceGeneration`、来源切换与任务点质量／年龄规则。引用或证据错误按既有 `source_refs`／`task_evidence` 合同拒绝，实时与历史均不得写业务行或新回执。其他被引用点不因未列入声明就被推定为映射点。
3. **同点兼用。** 如果绑定的任务点也用于指标，`sourceRefs` 中只引用该点一次，并把该点的 `pointId` 列入 `mappedPointIds`；后端可以核验该点和任务，但其指标用途仍是发送方声明。不能以“数组元素必须不同于任务点”拒绝该情况。
4. **常量和混合。** `mappedPointIds: []` 是发送方声明本次指标全部为常量，仍需真实任务点证据；事实点与常量混合时只列发送方声明实际使用的事实点，常量不伪造 PLC 引用。例如全部指标均为常量时，仍使用上述真实任务引用，发送 `"mappedPointIds": []`；任务点本身还用于某指标时，发送 `"mappedPointIds": ["point-active-task-no"]`。后端不能仅据请求核实这些用途是否真实。
5. **第三方不变。** 第三方仍按 §5 提交一条 `external_event` 和原有数据字段，不增加 `mappedPointIds`，也不因 SMA 新规则改变缺省、认证、归属、质量、回执或错误行为。调用身份由凭据和服务端配置判定，不由请求中自称的角色判定。

收到请求时先执行原有机器认证、媒体类型／大小和语法保护，并校验设备、组与目标的现行授权。根据持久回执区分旧事件和新事件后，再执行新事件的声明必填与来源核验；不得因新的字段要求跳过认证、泄漏无权限的回执或破坏 §10.4 的来源切换／删除事务顺序。声明点不属于当前真实引用、任务证据无效、指标越权或质量不合格时，不产生新的业务写入或回执。

### 11.3 持久声明与新旧事件幂等

新 SMA 事件成功时，在已有 `metric_ingest_receipts.task_evidence` JSON 中保留任务事实字段，并另增 `mappingDeclaration: {"declaredBy": "sender", "mappedPointIds": [...]}`。该子对象明确是发送方声明：其中每个所列点的存在及样本身份可按准入结果核对，**用途与数值运算未由后端验证**。`source_refs` 继续保存原来源引用数组；历史回执不回填、不改写，缺少声明的旧回执解释为“旧事件未记录声明”，不能解释成“全常量”。管理员详情既有 `taskEvidence` 原字段继续可读；新增子对象不改变管理员或机器权限。复用现有 JSON，不新增表、列或数据库 revision。

按原有 `(target, producerId, eventId)` 定位回执。认证、目标和设备组准入仍先于返回任何回执；基础 JSON 格式须合法。**命中回执后先比较其对应版本的规范化内容，再处理新事件准入**：

- 对已保存的 r8 SMA 回执，原请求不含 `mappedPointIds` 时，沿用 r8 原摘要算法；内容一致返回原回执，采集事实之后到期或来源删除不改变已确认结果。为旧事件补上声明、改动其他已指纹化内容或复用事件号发送不同内容时返回 409，不重写旧回执；需要新的声明时使用新事件号。
- 对 r9 新 SMA 回执，摘要包括规范化的 `mappedPointIds`，并区分字段缺失与明确的 `[]`。相同事件和相同声明／数据重试返回原回执；同一事件改动声明或内容返回 409。声明集合仅顺序变化按同一规范化集合比较，重复元素不是合法声明。实时和历史各自独立回执及重试。
- 没有旧回执的新 SMA 事件才应用 §11.2 的声明必填规则；无字段或 `null` 返回 422，不能从任务点推断用途或缺省为空数组。解析 schema 与 OpenAPI 必须允许服务端识别“字段缺失”以接入旧回执重放，但文档须明确标注新 SMA 事件有条件必传、第三方不传；不能让通用请求模型在查询回执前无条件拒绝合法旧重试。

历史同源样本去重、实时同组整体覆盖且漏传项缺测、来源保留及时间合同继续按 r8；新声明不能改变另一目标结果或绕过指标/历史白名单。`mappingDeclaration` 和指纹都不能替代逐指标真实性核验。

### 11.4 候选实施范围与执行边界

本节待 Human Owner 选择并批准后才允许 Development 动手。只处理 R8-QA-001 所需的后端入参、来源核验编排、原回执兼容、错误码、机器合同与对应测试和说明。拟定直接范围为：

| 范围 | 允许的直接相关路径和用途 |
| --- | --- |
| 接口与服务 | `backend/app/equipment_observation/{api/routes.py,schemas.py,error_codes.py,manifest.py,services/ingest.py,services/reads.py}`；必要时 `backend/app/plc_facts/services/observation_evidence.py`。只为声明解析、校验、回执和已有详情读取作必要修改，不改变采集公开 HTTP 合同。 |
| 测试 | `backend/tests/test_equipment_observation*.py` 和 `backend/tests_mysql/test_equipment_observation*.py`；只新增或调整本问题、旧回执兼容及受影响断言，保留原测试保护。 |
| 机器合同与说明 | `contracts/published/http-api/equipment-observation-v1/{openapi.json,README.md,README.zh-CN.md,vectors.json,walkthrough.py}`、`backend/app/equipment_observation/README{,.zh-CN}.md` 和 `docs/equipment-status-process-monitoring{,.zh-CN}.md` 的直接相关内容；真实结构变化时相应维护 `CODE_INDEX.md`。 |
| 角色记录 | Development 更新本任务 `tasks.md` 并保留 r8 交接；实际 handoff 后由 fresh-context Verification 更新 `checklist.md`，保留 r8 `qa_failed`、已经完成的 dev 迁移和此前证据。 |

不改前端页面、SMA/DAA 产品、其他业务合同或数据库结构；不启用 Redis、PLC 操作、生产部署或发布。新合同只声明产品运行方的责任，不能把合成 HTTP 客户端冒充 SMA。已授权 dev 数据库仍是 `127.0.0.1:3307 / industrial_level_2_system`，仅在批准的目标、测试对象和动作内使用：执行前重查 server UUID、schema、revision `8c0e2a4d6f18`、已有数据和配置；使用唯一合成设备、来源、任务、指标、producer 和事件身份，事先核对无碰撞，记录主键，结束时只清理本次测试对象并对账。不得删除、覆盖或重置他人记录、原来源、真实历史或既有配置；未经明确授权不停止、替换或重启现有用户服务。旧回执兼容测试应保留可复核的 r8 真实规范化输入和已保存合成回执，验证完成后按测试对象范围清理；不能伪造一条新摘要冒充 r8 原结果。

### 11.5 候选验收标准

| 编号 | 可独立观察的结果 |
| --- | --- |
| R9-AC01 两路缺声明负例 | 对 QA 复现中的真实同源任务和指标样本，以新事件分别调用实时和历史；只有任务引用且缺 `mappedPointIds` 均得 422 `equipment_observation.mapped_points`，两张主表与回执均不产生对应新变化。不能把缺字段自动视为 `[]`。 |
| R9-AC02 格式与来源负例 | 两路覆盖 `null`、非数组、无效或重复点、点不在引用中，以及错误样本、PLC/DB/实例/代次、过期样本、任务点缺失和无效任务。按 §11.2/既有合同拒绝；核对无新的业务行或回执。 |
| R9-AC03 正常与混合 | 一份真实入库的合成样本同时含任务点和映射点，数组列映射点；指标事实值和常量混合时两路各自成功，来源、槽位、持久回执及标明发送方声明的子对象正确。修改显示配置不改变写入或声明。 |
| R9-AC04 常量和同点 | 全常量显式 `[]` 及任务点兼作指标点显式 `[taskPointId]` 在其他准入条件满足时均可使用；前者仍核验真实任务样本。明确观察两种情况均为发送方声明，未证明实际映射的真实性。 |
| R9-AC05 新旧重放 | 已存 r8 原请求不含声明可重放同一结果；后续事实到期或来源删除仍可按既有授权返回。旧事件增加声明或更改内容冲突；r9 新事件同内容同声明重放成功，声明改变／省略冲突，`[]` 与缺失不同。两路独立验证。 |
| R9-AC06 身份与第三方 | 未认证、停用、越权设备／组／目标等不暴露或返回别人的回执；第三方原始最简请求和缺省、质量、授权、错误及重试行为与 r8 对照一致。 |
| R9-AC07 已有数据和 dev | 无新数据库迁移或版本改变；两张主表、配置、既有采集事实及其他业务记录不被修改。真实 dev 验证仅触及拥有明确主键的本次合成对象，清理后对账与资源归属可复核。 |
| R9-AC08 合同和交接 | OpenAPI、双语说明、向量、最简/完整示例及回执字段一致；明确 SMA 新事件的字段要求、旧回执兼容与声明不可证明映射。Development 自检和 fresh-context Verification 证据分开，补充与该返工相关的 r8 未覆盖项；已发生迁移、合成客户端、真实 SMA/DAA/PLC、Owner 最终验收分别报告。 |

本草案仅供审阅和选择；无需现在执行代码、数据库写入或运行测试。确认技术表达及可信边界后由 Human Owner 批准精确 r9，再按 STD 角色顺序实施、验证与验收。

<a id="r10-source-independent-energy"></a>

## 12. r10 草案：通用来源写入与独立能耗

2026-11-16（Asia/Shanghai）。**本节是未批准的 `draft`；除按 canonical workflow 机械同步任务状态索引外，本轮只修订 spec，不改代码、数据库、配置或运行进程。** Human Owner 要求设备状态与过程监控不限制数据来源，能耗有独立主表且不关联订单，并询问过程页面卡住是否会在后续修复。Human Owner 已确认设备状态默认显示最近采样任务、可手动切换且管理列表默认全部，能耗按各表计指标配置计量方式；本轮进一步确认设备／任务多区域整包和三路统一 `observedAt`。具体现场参数由 admin 逐项配置。**这是产品原则的确认，不是对 r10 实施或数据库迁移的批准；r10 尚未实施。**

§1–10 保留其历史合同与批准记录，§11 r9 的 `mappedPointIds` 是曾提出但未批准的候选；若 Human Owner 明确批准精确 r10，发生冲突时本节在 r10 范围内优先。采集事实、PLC 点位、`sourceRefs`、`mappedPointIds`、DAA／SMA 身份或数据库内事实查询都**不是**业务写入与 `taskNo` 准入的前提。来源声明仅为可选元数据，不证明指标取值的真实血缘。现有 SMA 产品的投递仍未启用，不因本节改变，也不把合成请求说成真实产品联调。

已发生事实不可改写：dev 库原先已按 r8 迁至 `8c0e2a4d6f18`；r8 独立 QA 为 `qa_failed`、其失败及未覆盖项见 [checklist](checklist.md#r8-独立-verificationqa_failed)，实施事实见 [tasks](tasks.md)。r10 不将原 QA 失败改判通过；新合同获批后由 Development 重新实现与交接，由 fresh-context Verification 对新合同及受影响的 r8 未尽项目独立验证。r8 原批准及其目标操作授权仍是历史记录，不自动扩大为本次文档修改允许实施；本轮不撤销或重新执行已有迁移。

### 12.1 原理、时间与边界

```text
可信 SMA / 第三方 / 其他获授权写入方
        │ 同一设备/任务多区域整包，分别请求、确认和重试
        ├─ 设备状态 ─→ equipment_status_main（设备+任务一行最新整包）
        ├─ 过程监控 ─→ process_monitor_main（每个采样整包追加一行）
        └─ 能耗 ─────→ energy_consumption_main（表计样本追加，无订单）
                              ↑
区域/指标/槽位、卡片/曲线和回执等辅助配置 ─→ 解释、显示、校验与幂等
```

三个主表是各自业务值的持久真相；配置表保存含义、展示和槽位绑定，回执负责接收与幂等，不是另一份业务值。`id` 是行主键；`task_no` 是设备状态与过程历史贯穿系统的任务／卷业务关联键，按字符串保留前导零，不替代 `id`，也不强制要求计划／实绩行或 PLC 任务点。`coilNo` 若要显示，是普通字符串指标。能耗按表计、时刻及事件识别，不传、不存 `task_no` 或订单外键，按单分摊另立范围。

设备／任务整包的 `groups` 容纳生产参数和动态清洗、温度、传动区域；组键、指标键稳定，值为单个数字／布尔／字符串。同一完全授权且已登记的完整请求可分别发实时和历史两路；实时按整包覆盖，历史按留存配置选项追加，两路回执和重试独立。区域与卡片由配置驱动，每卡至多 10 个指标，不固定实际值／设定值数量，不自动生成偏差或状态。指标单位可留空；有单位时拼入中英文指标标题，值区只显示原类型的值；同单位曲线纵轴标一次单位。过程显示曲线与历史留存独立。

**统一时间合同**：三个新业务请求都必须非空携带 `data.observedAt`，为这份业务样本唯一、真实且有明确来源语义的原采集／样本代表时刻；不使用发送、接收、创建、更新或 UI 刷新时间冒充，也不对缺失时间自动补当前时间。API 接收含时区偏移的 ISO 8601，统一换算到 `Asia/Shanghai`／`+08:00`，三个主表均以 `observed_at DATETIME(6)` 保存，不截秒或静默丢掉六位内有效小数。超过六位且不能无损表达时明确拒绝并提示，不能偷截或四舍五入伪造精度；如需更高精度另定合同。`created_at` 是记录创建时刻，`updated_at` 是实际内容更新时刻（包含备注／管理标记），各自独立且都不得冒充采集时刻。这里的强制非空只适用于新的监控与能耗事件；通用实绩合同的 `observedAt` 仍可为 `null`，不因同名而更改该合同。

**DAA / SMA 的已核对事实，不是准入依赖**：DAA 当前按读取块记录完成时间并赋给有关点，跨块点时刻可能不同（[scheduler](../../automation-world/data-acquisition-agent/src-tauri/src/services/local_scheduler.rs)）；采集后端对一份完整 PLC／DB 样本以该样本各点采集时间的最大值形成唯一 `sampledAt` 摘要（[写入](../../backend/app/plc_facts/crud/async_v2.py)、[摘要](../../backend/app/plc_facts/services/async_v2.py)）。如果 SMA 实际使用这一完整 DB 样本，可以原样将其摘要作为业务 `observedAt`；它是该样本**最晚点位观测／读取时间**，最大值覆盖包括 `bad` 点在内的全部点的真实读取尝试时间；不保证是最后一次成功值，不表示所有点同刻或全部有效。不能仅因摘要时间存在就把业务质量推断为 `good`；发送方须按实际采样质量与业务规则据实填报。逐点 latest 可能跨轮，不能把它们伪装成同批。

跨多个 DB／独立来源样本拼一个业务整包时，发送方须先有可追溯的同一有效批次及真实代表时刻规则；具体取法和上游可否提供属于实施／联调前待确认项，不把它写成当前 DAA／SMA 已有能力。无法成立时不得拼为一份声称同步的样本，也不能用发送／接收时间代替；历史可按各真实批次独立上报，实时仍按整包覆盖，缺少的组会显示缺测。业务服务不要求调用者提供 DAA 或 PLC 事实作为接受条件。

### 12.2 三张主表、存储与旧数据迁移

设备状态和过程的 `local_values` 采用嵌套 JSON：第一层为稳定 `groupKey`，第二层为该目标／区域的本地槽号 `"01"`–`"100"`。每目标、每区域最多 100 槽；能耗仍按 `(meter_id, group_key)` 各 100 槽。不是 100 个物理列，也不是系统总共 100 项；外部只传 `metricKey`。槽首次使用后不改绑，停用不释放历史含义，编辑标题不改变键或物理单位。

| 主表 | 拟定字段与索引 | 行为 |
| --- | --- | --- |
| `equipment_status_main`（r8 已存在，需改造） | `id`；`equipment_id`、`task_no`、`observed_at DATETIME(6)`、`quality`、嵌套 `local_values`、当前回执／来源样本键、备注、`created_at`／`updated_at`；新唯一键 `(equipment_id, task_no)`。不再以 `group_key` 将一个任务拆成多行。 | 同设备／任务最新**整包**仅一行。更晚 `observedAt` 替换整包，保留该行 ID 和备注；更早返回 `stale`，同刻同内容确认已存、同刻不同内容冲突。缺省组、`{}` 组和缺省指标在新包中都是缺测，绝不沿用上一包；`0`、`false`、空字符串保留。 |
| `process_monitor_main`（r8 已存在，需改造） | `id`；`equipment_id`、`task_no`、`observed_at DATETIME(6)`、`quality`、嵌套 `local_values`、来源样本键／回执、备注／`review_mark`、`created_at`／`updated_at`；查询索引按设备、任务和 `observed_at`。 | 每个被允许的真实历史采样整包追加一行；只保留已开启历史留存的已授权指标，迟到按原时刻追加。不同真实样本即使同一 `observedAt` 也都保留；同事件重试不新增。原值永久保留，admin 只改备注／异常或已复核标记。 |
| `energy_consumption_main`（拟新增） | `id`；`meter_id`、`group_key`、`observed_at DATETIME(6)`、`quality`、`local_values`；可空 `interval_start_at`／`interval_end_at`、采集方／事件与回执或摘要、备注／复核标记、`created_at`／`updated_at`；按表计、组及 `observed_at` 建查询索引，无任务／订单外键。 | 按表计样本追加，事件防重；读数或趋势按 `observed_at` 而不是抵达／更新时间判新。管理更改只更新管理字段和真实 `updated_at`，不修改原始采集值与 `observed_at`。 |

例如对下文虚构的设备整包，实时主表一行 `local_values` 可为 `{"production":{"01":"000042","02":0},"heatZone1":{"01":810.2,"02":815.0},"driveRoll1":{"01":false}}`；每个 `01` 的语义由其各自区域和目标的槽绑定决定，不同组不会串值。空区域可规范化为未存的键，但读取须一致显示缺测。

过程曲线横轴与样本先后**只按 `observed_at`**，迟到样本按其原 `observed_at` 插入图上；不得以 `created_at`、`updated_at`、到达顺序或 `id` 冒充采样时间。相同 `observed_at` 的不同真实样本不得丢弃，也不能靠 `id` 猜测先后；分页可使用 `(observed_at, id)` 等稳定次序仅作为**同刻技术分页**，须覆盖查询快照内每个点，并对同刻点避免画出虚假的先后关系。迟到插入既有游标之前时按查询快照／重新查询规则可见，不能声称 ID 顺序是时间。具体点的质量与缺测保留；查询必须逐个真实整包的 `observed_at` 为所选指标返回值或明确缺测（也可返回等价的明确缺测段），缺区域或部分指标缺失均在该时刻形成断点，不可只查询有值记录而把前后点误连，更不能复制上一值。只对读取结果可用 `value: null` 与 `present: false` 表达缺测；写入请求中的指标值仍不接受 `null`。

**r8 到 r10 的显式保全迁移，待批准后执行**：r8 现有实时每设备／任务／组一行，列名为 `sampled_at`；过程也按组一行。此段的旧列名仅描述历史迁移，**不是新接口字段**。实施前核验目标、快照、行数、旧时间语义／时区、所有相关写入方、回执、备注与配置；旧 `sampled_at` 的确为真实采集时刻且时区有证据时，才无损映射为 `observed_at`，不得盲目加减八小时，无法确认则保持旧原文并阻止该部分切换。

1. 实时旧组数据只有在有可信的同一原采集批次身份、相同真实采集时刻，且字段、备注及回执可完整保全时，才可以合并成一个整包；禁止简单取最大时间把不同时间组拼成一轮。不能证明同批同刻时，原始行、原组槽配置及管理信息保留为持久、可读／可恢复的旧版本归档；新实时表等待下一次真实整包，UI 明确等待新整包，不能用旧组伪装为当前整包。归档不是第四张业务主表、不是临时备份，也不能作为不可访问的唯一证据；须以受控只读方式核查旧值、原时刻与原配置并可恢复。是否需要旧档页面入口依实施前实际数据和管理需要决定，不自动新增。归档具体结构、旧／新 ID 映射、权限和恢复步骤在实施前定稿及对账；旧归档和新表可能出现相同数字 ID，必须结合结果版本与映射定位，不能把旧回执指向重号的新记录。
2. 过程旧组行无可信同包证据时，各自转换／呈现为只含原组的独立历史样本，其他组缺测，保持原时间、值、备注、复核和可追溯原 ID；不按时间邻近猜测合并。相同时间不同事件不因新索引互相覆盖。旧配置及槽语义保留，可解码停用指标。
3. 新增明确 Alembic 后继，保全已有行、回执与旧指纹；变更旧实时唯一键和两张旧表的时间列，校验数量、逐项值、事件、备注、时区和可追溯映射，明确中断写入窗口、回退和恢复。已有 `source_sample_key`、`ingest_receipt_id` 不是 PLC 准入条件；新事件用已认证发送方和事件身份生成。旧 v1 已确认事件仍按旧信封和旧指纹重放、返回其原回执，不重新入库或将旧样本拼成新事件。新增 archive／转换目标、不可逆冲突、目标环境与授权需在执行前具体核定；本轮不执行。

能耗包含任一时段增量指标时，`data.intervalStartAt`／`intervalEndAt` 必须真实存在，开始含、结束不含且开始早于结束，保存在能耗主表并进入事件摘要；多个增量指标的区间必须一致，否则分事件。没有增量指标的包不填写区间。同表计／组同包可混合累计、瞬时与增量：区间只解释增量，累计与瞬时仍按业务 `observedAt` 记录。

### 12.3 区域、指标、卡片与辅助配置

以下五张为 r8 已有配置／回执表，职责沿用并按整包合同调整；除此之外拟新增区域定义 `equipment_metric_groups`，以及下文的能耗指标配置表。辅助表不是新的业务值主表。

| 表 | 主要职责 |
| --- | --- |
| `equipment_metric_groups`（拟新增） | 稳定 `group_key`、所属 `production`／`temperature`／`cleaning`／`drive` 类别、中英文区域名、显示启停和排序；admin 可新增／命名／启停／排序。停用显示不删除历史，也不暗示停止留存；已使用的区域键和类别不能改绑其他含义。 |
| `equipment_metric_configs`（现有） | 全局稳定 `metric_key`、所属区域、类型、双语名、可选单位和小数显示；名称可改，已使用的键不得换含义。当前模型以指标键为主键，不默认同一键可以绑定多个区域；示例以 `zone1Actual`、`zone2Actual` 区分。 |
| `equipment_metric_slot_bindings`（现有） | `(target, group_key, slot_no)` 分别绑定实时／历史槽；目标写入启用与管理列表列显示／排序独立，展示开关不等于留存开关。同区域同一指标在两目标可有不同槽号。已使用绑定不得改绑，停用仍可解码旧值。 |
| `equipment_card_configs`（现有） | 四设备页的卡片、页面、双语标题、排序、启停以及有序指标；区域可配实际、设定等任意已登记指标，一卡最多 10 项，不写死两个值或区域数量。 |
| `monitor_curve_group_configs`（现有） | 三个过程页配置同单位图框、可选区域及区域下数值指标／系列；选择哪些区域只影响显示，不修改历史留存。不同单位使用分图或明确区分的轴，空配置不伪造区域。 |
| `metric_ingest_receipts`（现有） | `(target, producer_id, event_id)` 内容摘要、处理结果、主表／旧归档定位与历史跳过信息；与写入同事务。当前映射、来源和任务证据等列非空，需明确迁移以允许通用新事件；保留旧回执内容及旧指纹解释，不凭空要求 PLC。 |

管理员在温度、清洗、传动分类下配置区域及其 `groupKey`，配置区域内指标及 `metricKey`，分别设置实时／历史绑定和列表／卡片／曲线可见性；生产参数同样使用已登记组。区域是否显示、指标是否写实时、是否留历史及曲线是否勾选是独立设置。`enabled` 为展示开关时不能静默变成删除或越权；目标写入开关定义为目标是否保存，账号的设备／目标／区域／指标授权另行判定。机器发现接口返回指定目标、被授权的组／指标及两目标状态，供发送方组装整包；服务端不信任客户端自述授权。

**能耗配置：按表计的每个指标独立配置。** 拟新增一张 `energy_metric_configs`，首版以 `(meter_id, group_key, metric_key)` 为业务主键，`(meter_id, group_key, slot_no)` 唯一，`slot_no` 范围 1–100；同一 `meter_id` 的每个组有独立的 100 槽，不同表计可使用相同组名、指标键和槽号而互不串值。业务行用自身 `meter_id + group_key` 定位配置，再把 `local_values` 的槽位还原为 `metricKey`；接入方不传槽号。已有 `equipment_metric_slot_bindings` 的 CHECK 只允许 `latest`／`history`，现状不支持能耗；本方案使用单独配置表，须通过明确迁移建立，不伪称当前已存在。

| 配置字段／约束 | 作用 |
| --- | --- |
| `meter_id`, `group_key`, `metric_key` | 三者共同标识一个表计的一个指标；`metricKey` 是对外稳定键，不以可编辑名称代替。相同键在不同表计可有不同配置，读写、授权和展示均先按三者定位。 |
| `slot_no`, `first_used_at` | 对应该表计组的 `local_values` 键 `01`–`100`；同一表计和组内槽号唯一，首次成功存值与使用标记同事务生效。 |
| `value_type`, `quantity_key`, `measurement_mode` | 首版计量指标为 JSON 数值；`quantity_key` 描述电量、功率、流量等物理量；模式分别为 `cumulative` 累计读数、`interval` 时段增量、`instantaneous` 瞬时量。每条指标独立设置，启用写入前必须明确其类型与模式；不能假设一块表全部为同一模式。 |
| `unit`, `decimals`, 中英文名称 | `unit` 可为空；为空时可原样展示数值，但不能把未知单位当作 kWh 或 m³，也不能据此进行依赖已知单位的汇总。`decimals` 是显示精度；持久值须采用不会静默损失所需精度的表达，不能把显示四舍五入写回原值。名称和非空单位用于对应语言的标题。 |
| `enabled`, `list_visible`, `list_order` | 控制新写入及展示／列表顺序；禁用后不删除原样本，历史查询仍能按旧绑定还原。 |
| 现场规则 | 预留该指标的采样／缺口、区间、重置／换表等配置或关联；不推定具体数值。计算所需规则未明确时返回缺失／不完整，不猜测、也不伪装成 0。 |

为防止已有值被重新解释，首次成功写入后，本行的表计、组、指标键、槽位、数值类型、物理量、**物理计量单位与模式**不可原位改成另一含义；显示名称、展示顺序、显示小数位和启停可改，但不改原始值。空单位已有样本也不能直接改成一个假定单位并追认历史；如实际需要新模式／单位，应新建新 `metricKey` 和未用槽，旧配置保留用于解码，或另立有证据的历史更正／版本迁移范围；不能无记录覆盖旧配置或重用槽。变更与写入并发时须在事务中保证绑定、首次使用和样本一致。现场逐个表计由 admin 配置对应指标；名称、模式、单位、采样周期与重置策略均不替任何真实表计预设。

以下仅是演示配置，不表示现场已有这些表计；最后一行说明相同 `metricKey` 在不同表计可以有不同模式，前面三行说明同一表计可同时有累计、瞬时和时段增量指标：

| `meterId` | `groupKey` | `metricKey` | `slotNo` | 模式 | 单位 |
| --- | --- | --- | --- | --- | --- |
| `meter-01` | `electricity` | `energyReading` | `01` | `cumulative` | `kWh` |
| `meter-01` | `electricity` | `electricPower` | `02` | `instantaneous` | `kW` |
| `meter-01` | `electricity` | `energyInterval` | `03` | `interval` | `kWh` |
| `meter-02` | `electricity` | `energyReading` | `01` | `interval` | `kWh` |

能耗事件去重优先复用可安全扩展的现有回执；若选择在能耗主表以 `(producer_id, event_id)` 唯一键加摘要实现相同语义，也可不增加能耗回执表，但必须说明目标隔离、旧回执兼容及事务原子性。首版从原始样本按请求计算统计，不预建日／月汇总表；真实性能或长期存储压力经测量后再另定缓存、汇总和保留策略。Redis 不在本轮范围。

### 12.4 最近采样任务与手动选择

Human Owner 已确认设备状态默认显示所选设备的**最近采样任务**，可手动切换；实时和过程 admin 管理列表默认全部任务，可筛选 `taskNo`。这不表示该设备仍在生产或处于空闲，也不是 r10 已实施。

1. 在身份有权查看的指定设备实时主表中比较每任务整包 `observed_at`，最大者为最近采样；不同任务同刻并列时按 `task_no` 二进制升序确定默认展示、提示并列并列出获准候选，不按到达或 ID 伪造时间先后。无样本显示“暂无采样任务”；数据过期标注真实时间和“已过期”。
2. 页面打开期间手动选择其他获准任务后，数据轮询／刷新及新样本到达不覆盖手选；“跟随最近采样”恢复自动。切换设备回到新设备最近采样；重载或再次进入按默认跟随，不要求跨浏览器重启保存手选。手选任务不可用／失权时提示重新选择，不悄悄跳到其他任务。
3. 所选任务某区域或指标缺失就显示缺测，不向其他任务或上一包借值。原 A 单迟到包若 `observedAt` 早于 B 的当前样本，不能因最后到达使自动选择回 A；若 A 的真实业务采集时刻更晚，它只能被称作最近采样任务。
4. 同一设备／任务的较旧实时包返回 `stale`；同一时刻整包内容不同返回冲突。多写入方需约定可信时钟；允许的未来偏差及整包过期阈值由项目配置，不能将时间戳之外的 ID 或接收时间当作时钟。发现时钟不可靠须标示，不能声称任务正在生产。页面不以 PLC 点事实判断任务；跨发送方同一物理样本使用不同事件号时无法自动保证去重。

### 12.5 SMA／第三方接口与整包示例

以下为未实施的候选；当前 r8 仍是旧按组合同。SMA、第三方与其他受信任程序使用同一业务格式和接口：先配置机器 Bearer 与 producer、设备／目标／区域／指标授权，再以稳定键发送，不要求 PLC／DAA 事实。`eventId` 每次必传且在同一 producer／目标范围稳定，实时和过程可使用同一个事件号但分别确认；`observedAt` 每包必传且非空。可选 `contractVersion` 缺省为拟定 `aiis.metric-ingest/v2`，可选 `producerId` 必须与认证身份一致；`mappingId`／`mappingRevision` 可一起省略，`sourceRefs` 可省略，提供时仅按合同验格式及记录，不作为准入、任务证明或真实性保证。

| 方法／路径（以下均在 `/api/v1`） | 契约与权限 |
| --- | --- |
| `GET /integration/metric-definitions?equipmentId=...` | 机器发现自身授权的区域、指标、类型、可选单位及实时／历史目标启用状态；不得枚举越权范围。供构造一份可投两路的整包。 |
| `POST /integration/equipment/latest-snapshots` | 同一设备／任务整包覆盖，必须有对该设备**全部可替换实时区域和指标**的授权，包括省略时将被清空的部分；部分范围授权不能借整包清空越权字段。 |
| `POST /integration/monitor/history-samples` | 相同的整包结构和公共事件身份，须有设备／历史目标及每个提交区域／指标的授权；服务端选出已启用历史的项追加，不因另一些已授权项未留存而拒绝。 |
| `GET /integration/energy/metric-definitions?meterId=...&groupKey=...` | 只发现机器有权访问且已启用的该表计／组指标及各自单位和计量模式。 |
| `POST /integration/energy/samples` | 每次一表计／组样本，`observedAt` 必填；按 `(meterId, groupKey, metricKey)` 校验授权与模式，无订单／任务关联。 |

设备两路 `data` 都要求 `equipmentId`、字符串 `taskNo`、`observedAt` 和 `groups` 对象；每个 `groups[groupKey]` 是 `{metricKey: 单值}`。已登记且有权访问的组可以省略或写 `{}`，已登记指标可以省略；顶层 `groups: {}` 也有效，表示此次所有组缺测，实时会清空该设备／任务原整包。空组与省略在存储和展示上均表示缺测；可按同一缺测语义读取，但**先校验空组的登记和权限**；未知组／指标、越权、`null` 值或类型错误整包拒绝，不得先写一部分。`0`、`false` 和空字符串是有效值。实时接受 `quality: good/bad/unknown`，缺省或 `null` 记 `unknown`；历史沿用现有规则，须明确 `quality: good` 才追加。不能因为空组、缺测或留存过滤省略／编造 `observedAt`。

对每个显式提交的指标，先按设备、当前 producer、目标接口及已登记组／指标验证权限与类型；**授权不等于目标留存开关**。对已登记且完全授权的指标，目标绑定启用则保存，目标绑定未启用则跳过并在回执指出；历史因此可以接受完整实时包而只保留历史启用项，实时未开启的目标项也不保存并列明跳过。未知、非授权或类型不符仍是错误，不能伪装为跳过。被过滤的指标和省略／空组都不会沿用旧快照。若设备存在已开启历史留存的指标，本次为符合质量及授权规则的真实采样，即使过滤后该整包所有历史指标都缺测，也要追加一条保留原 `observedAt` 的空／缺测历史样本，用于显示断点；这是实际缺测事件，不是补造数值。只有该设备完全没有开启任何历史留存指标时，才不创建过程样本，并原子保存结果为 `no_history_metrics` 的回执及已授权跳过项；重试返回同结果。允许空整包实时覆盖的调用者仍必须具有全部替换范围权限。

两个目标分别以 `(target, producerId, eventId)` 持久去重；调用方必须以同一事件 ID 重试原请求；相同事件和相同内容返回原回执，异内容复用返回 409。v2 指纹区分显式空组与省略组的提交形式，二者虽都表示缺测，不能在重试时改写正文后假设仍幂等；JSON 对象键顺序不代表内容变化。整个合法请求、目标过滤结果、行写入及回执同事务；提交状态不明时原事件重试。事件 ID 不是时钟，不决定业务先后。同一时刻的两个真实历史事件使用不同事件身份并各存一行；跨发送方使用不同事件号的同一物理样本无法自动可靠判重。收到已存 r8 v1 事件时，先认证并校验旧范围，再按旧 schema、旧时间字段和旧指纹比较，必要时用原规则及保存的旧认证／默认值上下文推导缺省事件 ID；不得先按新 schema 必填项拒绝原重试。相同原请求返回原结果，即使旧结果在保全归档中也可按旧版本定位，不重新写入；已撤销身份的权限不因兼容而恢复。新请求用 v2 整包／`observedAt`；显式 v1 的新事件不承诺继续接收，返回明确升级错误，不将兼容限制静默冒充旧合同不变。

**机器指标发现**的 `data` 示例；以下均为虚构配置，账户只有对应完整范围授权才能提交后面的实时整包：

```json
{
  "equipmentId": "line-01",
  "groups": [
    {"groupKey": "production", "metrics": [
      {"metricKey": "coilNo", "valueType": "string", "latestEnabled": true, "historyEnabled": false},
      {"metricKey": "lineSpeed", "valueType": "number", "latestEnabled": true, "historyEnabled": false}
    ]},
    {"groupKey": "heatZone1", "metrics": [
      {"metricKey": "zone1Actual", "valueType": "number", "latestEnabled": true, "historyEnabled": true},
      {"metricKey": "zone1Set", "valueType": "number", "latestEnabled": true, "historyEnabled": true}
    ]},
    {"groupKey": "washTank1", "metrics": []},
    {"groupKey": "driveRoll1", "metrics": [
      {"metricKey": "driveReady", "valueType": "boolean", "latestEnabled": true, "historyEnabled": false}
    ]}
  ]
}
```

**实时整包**，数字、区域及时间仅为示例：

```json
{
  "eventId": "sample-000042-001",
  "data": {
    "equipmentId": "line-01",
    "taskNo": "000042",
    "observedAt": "2026-11-17T10:30:00.123+08:00",
    "quality": "good",
    "groups": {
      "production": {"coilNo": "000042", "lineSpeed": 0},
      "heatZone1": {"zone1Actual": 810.2, "zone1Set": 815.0},
      "washTank1": {},
      "driveRoll1": {"driveReady": false}
    }
  }
}
```

**历史请求**发到另一条 POST；可以逐字复用同一完全授权的请求，后端决定哪些项留存，而不是要求 SMA 重新裁剪：

```json
{
  "eventId": "sample-000042-001",
  "data": {
    "equipmentId": "line-01",
    "taskNo": "000042",
    "observedAt": "2026-11-17T10:30:00.123+08:00",
    "quality": "good",
    "groups": {
      "production": {"coilNo": "000042", "lineSpeed": 0},
      "heatZone1": {"zone1Actual": 810.2, "zone1Set": 815.0},
      "washTank1": {},
      "driveRoll1": {"driveReady": false}
    }
  }
}
```

假设上例只开启 `heatZone1` 两个指标的历史留存，历史回执的 `data` 候选如下；被跳过的是已登记且授权但未开启留存的项，并非未知或越权：

```json
{
  "target": "history",
  "eventId": "sample-000042-001",
  "outcome": "stored",
  "recordId": "42",
  "stored": [{"groupKey": "heatZone1", "metricKeys": ["zone1Actual", "zone1Set"]}],
  "skipped": [
    {"groupKey": "production", "metricKey": "coilNo", "reason": "history_disabled"},
    {"groupKey": "production", "metricKey": "lineSpeed", "reason": "history_disabled"},
    {"groupKey": "driveRoll1", "metricKey": "driveReady", "reason": "history_disabled"}
  ]
}
```

**后续实时整包缺测示例**：`heatZone1` 为空，清洗和传动组省略；覆盖后这些位置均缺测，不沿用上一个包。设备和空组仍需事先登记并授权：

```json
{
  "eventId": "sample-000042-002",
  "data": {
    "equipmentId": "line-01",
    "taskNo": "000042",
    "observedAt": "2026-11-17T10:30:01.123+08:00",
    "quality": "good",
    "groups": {"production": {"coilNo": "000042", "lineSpeed": 0}, "heatZone1": {}}
  }
}
```

前端 `GET /equipment/latest-cards` 和 `GET /monitor/history-curves` 等人类接口使用人类业务读权限、设备范围及配置还原稳定键。以下是前端曲线 GET 的 `data` 候选：两个不同真实事件可以有同一个 X 坐标，必须都返回；`recordId` 仅定位或技术分页，不代表真实采样先后；第 103 行是原始真实整包在该指标上的缺测断点，读取时 `null` 不代表允许写入 `null`：

```json
{
  "equipmentId": "line-01",
  "taskNo": "000042",
  "curveGroupKey": "heating-temperature",
  "unit": "°C",
  "series": [
    {
      "groupKey": "heatZone1",
      "metricKey": "zone1Actual",
      "points": [
        {"recordId": "101", "observedAt": "2026-11-17T10:30:00.123+08:00", "value": 810.2},
        {"recordId": "102", "observedAt": "2026-11-17T10:30:00.123+08:00", "value": 810.3},
        {"recordId": "103", "observedAt": "2026-11-17T10:30:01.123+08:00", "present": false, "value": null},
        {"recordId": "104", "observedAt": "2026-11-17T10:30:02.123+08:00", "value": 811.5}
      ]
    }
  ]
}
```

**能耗示例**：以下是 §12.3 的虚构表计；`GET /integration/energy/metric-definitions?meterId=meter-01&groupKey=electricity` 返回的 `data` 中，同表计不同指标可独立配置模式：

```json
{
  "meterId": "meter-01",
  "groupKey": "electricity",
  "definitions": [
    {"metricKey": "energyReading", "valueType": "number", "measurementMode": "cumulative", "unit": "kWh"},
    {"metricKey": "electricPower", "valueType": "number", "measurementMode": "instantaneous", "unit": "kW"},
    {"metricKey": "energyInterval", "valueType": "number", "measurementMode": "interval", "unit": "kWh"}
  ]
}
```

同包的区间仅解释增量指标；`observedAt` 依然是此次样本的真实代表采集时刻，不能从 `intervalEndAt` 代填：

```json
{
  "eventId": "meter-01-20261117-0900",
  "data": {
    "meterId": "meter-01",
    "groupKey": "electricity",
    "observedAt": "2026-11-17T09:00:00+08:00",
    "intervalStartAt": "2026-11-17T08:00:00+08:00",
    "intervalEndAt": "2026-11-17T09:00:00+08:00",
    "quality": "good",
    "values": {"energyReading": 1006.0, "electricPower": 10.0, "energyInterval": 6.0}
  }
}
```

第二块表计对相同 `energyReading` 键设置 `interval` 时，按它自己的配置解释：

```json
{
  "eventId": "meter-02-20261117-0800-0900",
  "data": {
    "meterId": "meter-02",
    "groupKey": "electricity",
    "observedAt": "2026-11-17T09:00:00+08:00",
    "intervalStartAt": "2026-11-17T08:00:00+08:00",
    "intervalEndAt": "2026-11-17T09:00:00+08:00",
    "quality": "good",
    "values": {"energyReading": 5.0}
  }
}
```

### 12.6 能耗统计和旧数据衔接

统计必须基于 admin 为每个 `(meterId, groupKey, metricKey)` 配置的**物理含义、单位、计量模式与真实区间**，禁止仅根据指标名、数字大小、`currentPower` 名称或其他模块字段推断；同一表计的不同指标、不同表计的同名键均分别解释。跨表计汇总必须先确认物理量、单位、时间区间及计量口径兼容，不对累计读数和增量混算。即使同一表计同时给出累计读数和时段增量，也可能是同一份用量的两种表达；须按确定的统计来源择一使用，不能把二者加倍。总表和其分表也不得未经确认直接相加。下面数字是口径示例，不代表现场设备配置：

| 上报模式 | 示例与计算 | 边界 |
| --- | --- | --- |
| 累计表计读数 | 同一有效电表 08:00 为 `1000 kWh`，09:00 为 `1006 kWh`，确认期间无重置／换表时该区间用量为 `6 kWh`。 | 前后读数必须有相同表计／指标和一致单位、质量可用且覆盖所需边界；下降、重置、回卷、换表或无法确认的间断显示异常／不完整，不能简单当负数或自行猜补。 |
| 时段增量 | 同一表计两个不重叠、各自边界明确的时段分别为 `2 kWh` 与 `3 kWh`，完整覆盖目标区间时总量为 `5 kWh`。 | 防止重叠、重复和漏段；跨日段没有真实边界数据时不得任意分摊成两天。 |
| 瞬时功率／流量 | 某时刻功率 `10 kW` 或流量 `10 m³/h` 是速率，不是 `10 kWh` 或 `10 m³` 的用量，不能直接逐条相加。 | 未来若用 `功率 × 时间` 等积分，须另行确认插值、有效采样间隔、缺口与换表规则；首版不暗算。 |

日、月按 `Asia/Shanghai`，日范围为当地 `[00:00, 次日 00:00)`，月范围同理；API 输入带时区并在边界统一转换一次。日初／日末缺必要累计读数，或增量跨界无法归属时，返回缺失／不完整及原因，不能当作零；有合法读数且算出 0 才显示 0。`bad`／`unknown`、无采样、迟到、缺口、重置、换表、重复重放、不同表计或不同单位分别处理；无现场确定的间断容忍时间、采样节奏与跨界分配规则之前，不猜测其完整性。明确区分最新读数、实际用量、速率和统计完整性；校验时间排序、样本重放和并发，不能重复计费或因迟到自动覆盖原始事实。计算精度及舍入依单位与现场计量要求确认，不用浮点近似冒充计费精度。

**现有代码事实**：`monitor_history_energy_consumptions` 记录按卷结束时的电／氮增量，现有 `/api/v1/monitor/energy` 对此按时间求和；`monitor_history_process_curves` 另有 `elect_consum`／`n2_total` 曲线字段，旧接口的实时趋势从该表读取，其 `currentPower` 只是最后一条 `elect` 值，不能由名称推断为功率。现有接口对无汇总值回填 0；r10 的新统计要区分缺失与实际零，不能把旧行为直接当成已经具备新口径。`energy_prices` 与 `energy_price_hours` 是能源**价格**配置／历史，不是能源用量，既有价格 API 和数据不因新主表更名或删除；金额计算若需与分时价格联动，须另定价格有效区间、计量区间、单位与舍入，不能把价目直接加到用量。

协调者于 2026-11-16 对已授权 dev 做只读核对：旧能耗量表及旧曲线表当时均为 0 行，价格表已有记录。此为时点事实而非永久前提；实施前须重查数据、写入方、权限和备份。旧数据不自动迁移、删除或按未知语义混算；旧统计入口保持可用，先并行验证真实样例与新口径，明确切换点和旧表读写衔接后再切换，避免新旧重复计数或无数据时虚报零。旧表退役、历史转换和任何有损清理须有单独明确的范围、对账与授权；已有数据必须保留。

### 12.7 页面、菜单、管理和读取

沿用现有左侧**两级模块／子页面**结构，管理入口放在各自模块内；数据管理和配置管理仅 admin 可见，且对应 API 必须由服务端校验 admin 及设备／表计范围。下列为候选菜单名称，现有路由或菜单尚未因此改动；实施时中英文文案对称：

```text
设备状态
  生产参数 / 清洗工艺 / 温度工艺 / 传动工艺
  数据管理（admin：设备实时主表）
  配置管理（admin：区域、指标、目标绑定及设备卡片）
过程监控
  温度曲线 / 传动曲线 / 清洗曲线 / 能耗统计
  数据管理（admin：过程主表、能耗主表分别列示）
  配置管理（admin：历史显示、曲线和能耗表计指标）
```

- **设备状态**：四页从所选设备／任务的同一实时整包按已启用卡片显示区域及最多 10 个指标；没有的区域或指标显示缺测，`0`、`false` 和空字符串不隐藏。默认最近采样任务、页面内手选和过期行为按 §12.4；admin 可配置区域、指标、目标绑定、卡片和列表列。
- **过程监控**：温度、传动、清洗三页按 admin 配置的同单位图框读取过程主表，可按设备、`taskNo`、时间筛选。每个图框支持区域全选／多选，各区域显示配置的实际、设定等数值系列；不同单位分图或使用明确区分的纵轴。勾选只影响本次显示，不改变历史留存或其他用户配置；横轴、迟到及同刻多点按 §12.2 的 `observedAt` 规则。已配置图框无样本或所选区域无点时仍显示空 X/Y 轴、所选时间范围、配置单位和“暂无数据”，不绘假零；未选择设备、没有可选设备或尚未配置曲线时显示一个通用空 X/Y 占位、明确原因和下一步提示，不伪造炉区、曲线、单位、时间或数值刻度。只有用户确实选定时间范围才可据实标注；请求失败显示错误与重试，不冒充“暂无数据”。
- **管理列表**：实时和过程各有仅 admin 的分页管理列表，参考计划／实绩，默认全部任务，支持配置指标列、设备／任务／区域／时间筛选及项目公共列宽偏好。实时每设备／任务一行，过程每个历史事件一行；区域筛选作用于嵌套值和配置，不假设主表仍有 `group_key`。实时只编辑备注，过程只编辑备注与异常／已复核标记；旧实时组归档须可受控只读核查原值及原时刻，不得伪装成新整包，是否需要页面入口按实施前实际数据和管理需要决定。过程模块内分别管理过程和能耗主表。
- **能耗统计与管理**：过程菜单中的能耗统计页按表计、指标与时段查看最新读数、真实用量及完整性；能耗趋势在配置存在但无样本时也按所选范围为每个已配置组显示带单位的空 X/Y 轴与“暂无数据”；尚未选择表计、没有可选表计或尚无指标配置时，显示一个通用的空 X/Y 坐标占位和对应原因，不伪造指标、曲线、单位或时间。只有用户确实选定时间范围时才可据实标注，否则只显示轴线而不编造时间或数值刻度；读取失败则显示错误与重试，均不以零代替缺失。admin 按表计／组／指标分别配置名称、模式、单位和列表列；查看样本及标注备注／异常／复核，不能修改原始采样值。页面与统计按所选 `meterId + groupKey + metricKey` 展示和解释，同名指标在不同表计的模式和单位各自生效；同组不同单位／物理量的指标按单位分图或使用明确区分的纵轴，不把 `kWh` 与 `kW` 混作一个轴。原能耗页面现有价格功能仍按原权限保留，不能将统计读权限视为价格管理权限。

人类读取分别使用设备状态和过程监控既有业务读权限与后端设备范围约束；能耗引入独立的统计读取／管理权限及表计范围，精确权限键以实施合同列出。配置与管理列表服务端必须检查 admin 及相应设备／表计范围；页面隐藏不是授权。机器 GET 仅发现获准字段，不能读取历史样本或管理列表，除非另明确授予只读接口范围。admin 区域配置候选为 `GET`／`POST /equipment/metric-groups` 和 `PATCH /equipment/metric-groups/{groupKey}`；既有指标、目标槽位、卡片与曲线配置需支持动态区域及多区域系列。人类 GET 包括：`/equipment/latest-cards`，`/monitor/history-samples`、`/monitor/history-curves`，以及 admin 的 `/equipment/admin/latest-snapshots`、`/monitor/admin/history-samples`；拟新增人类 `GET /energy/consumption/samples` 和 `/energy/consumption/summary`，支持按获准表计、组与时间范围查询原始值或读数／用量／完整性；拟新增 admin `GET /energy/admin/consumption-samples` 与 `PATCH /energy/admin/consumption-samples/{id}`，后者仅改备注／管理标记；`GET /energy/metric-configs?meterId=...&groupKey=...`、`POST /energy/metric-configs` 及 `PATCH /energy/metric-configs/{meterId}/{groupKey}/{metricKey}` 供 admin 在权限范围内维护能耗指标配置，写入后不能更改受锁定的语义。它们是待实现合同候选，详细参数及响应须在交付的 API 合同中登记；以上路径均在 `/api/v1` 下，现有机器端和人类端权限不可互相推导。

### 12.8 页面卡住的已知现象与后续修复范围

Human Owner 报告中断执行后过程模块界面卡住。2026-11-16，协调者对用户现有 Chrome 页面只读观察到：从过程菜单进入时，温度／传动／清洗共用的 `src/app/monitor/views/observations/curves.vue` 及 `src/app/monitor/views/energy/index.vue` 都出现 `TypeError: Failed to fetch dynamically imported module`，Vue Router 报导航未捕获错误。随后只读请求这两个模块 URL 均返回 HTTP 200、`Content-Type: text/javascript`，后端 8000 的 OpenAPI 返回 200、进程仍在。协调者再在新开的独立 Chrome 标签直接访问 `/monitor/temperature`，也观察到白屏及相同的 `curves.vue` 动态导入失败；直接 HTTP GET 入口、`CurveChart.vue` 与 ECharts 顶层依赖均为 200 JavaScript；对入口响应涉及的 55 个本地静态 ES 模块作只解析／链接、不执行的检查也通过。**这说明问题不只在既有标签复现；HTTP 可达及静态链接通过不等于浏览器执行已恢复。具体原因尚未定位，不能据此认定缓存、服务、数据库或空配置为根因，也不代表已修复。**

后续获批准的 r10 实施应先在不破坏现有数据和用户启动进程的前提下复现、记录实际入口与网络／控制台证据并定位根因，再修复属于本任务触达的路由、模块加载、接口或空状态问题；需要服务切换时遵守现有授权与协调。若根因属于任务外独立模块，记录证据并反馈归属，不冒称已修。交接和独立验收须在真实浏览器从菜单及直接路由分别进入温度、传动、清洗、能耗四页，检查模块及传递依赖加载、正常数据、无设备／空配置／空数据、请求失败的可理解提示与恢复，导航不得长期卡住或产生未捕获异常。未选择设备／表计、没有可选对象或尚无配置时，须验证通用空 X/Y 坐标占位及准确原因，且不伪造指标、单位、数据或时间；配置存在但无样本时须验证每个实际图表的空 X/Y 轴、所选 X 轴时间范围、Y 轴单位及“暂无数据”，再通过真实接口数据到达或重试观察曲线恢复；还须验证同单位图框的区域全选／多选、各系列、缺测断点及按 `observedAt` 排列的真实曲线；不能只以 DOM 存在或截图冒充图表／请求闭环。不得为修界面删除业务数据、重置数据库、遮盖 API 错误或伪造数据。本轮不刷新、重启或停止用户进程。

### 12.9 范围、实施顺序、验收与开放项

**获批准后的有界交付**：调整 OBS 后端鉴权／规范化／回执／查询及相关合同；新增能耗主表、必要配置、接口、统计与可验证的前端页面和 admin 管理；修复 §12.8 范围内页面可用性；提供显式迁移、现有数据保全和受影响版本守卫；更新对应 API 合同及双语使用说明。执行角色按需加载 `backend-arch`、`frontend-ui`、`i18n-workflow`；涉及结构索引按 `code-document-indexer`，沿用项目既有迁移与数据边界。不得改 SMA/DAA 产品，不启用 Redis／后台采集或 PLC 操作，不部署生产或发布，不自动退役旧能耗表、不改价格合同，不为按单能耗分摊造模型。确需扩大范围时先回到 PM 修订。

未来获得精确 r10 批准后的直接文件范围如下；路径以交付工作树为准，碰到并行修改先协调，不覆盖他人工作。此表是范围候选，不授权本轮实施。

| 范围 | 允许触达的直接责任面 |
| --- | --- |
| 后端与迁移 | `backend/app/equipment_observation/**`；`backend/app/monitor/**` 与 `backend/app/energy/**` 中仅限本节能耗读写、统计和页面问题所需部分；`backend/alembic/versions/` 下新增后继迁移，不改写既有 migration；OBS 迁移导致版本守卫变化时限 `backend/app/plc_facts/{v2_config.py,crud/async_v2.py,crud/sync_v2_maintenance.py,services/observation_evidence.py}` 及 `backend/common/integration/storage.py` 中必要兼容。 |
| Web | `frontend-js/src/app/equipment/**` 与 `frontend-js/src/app/monitor/**` 中配置、卡片、曲线、能耗和管理列表的直接相关页面、组件、API、路由及中英文文案；尽可能复用现有公共表格，不扩大到无关模块。 |
| 验证 | `backend/tests/`、`backend/tests_mysql/` 下 equipment observation、monitor、energy 和受迁移影响的采集版本守卫定向测试；`frontend-js/tests/` 中对应模块与路由测试。测试须保留已有业务保护，不借更新断言掩盖失败。 |
| 合同、说明与交接 | `contracts/published/http-api/` 下新增／更新与本节精确对应的机器合同和必要索引；`docs/equipment-status-process-monitoring{,.zh-CN}.md` 及直接相关能耗使用说明；真实结构变化时的 `CODE_INDEX.md`；Development、Verification 在各自职责内更新本任务 `tasks.md`／`checklist.md`。已发布 v1 的语义与历史证据不得静默改写。 |

建议顺序：① Human Owner 审阅并批准精确 r10 后，核对现状、旧组样本／回执／时间、调用者和页面失败；② 定稿保全式后继迁移、归档／回执映射、整包和跨来源时刻边界，并设计按表计配置的合同；③ 用合成数据实现／验证两路整包、真实缺测断点、能耗与时间合同；④ 接通区域配置、菜单、曲线多选和三个管理视图，定位并修复导航问题；⑤ 对隔离与获准 dev 目标做可复核验证，保留现有数据，仅清理本次有明确主键的合成对象；Development 写自检和 handoff，fresh-context Verification 独立复核，再由 Human Owner 最终验收。软件设计和合成验证不必等待收齐所有现场表计资料；每项实际启用前由 admin 配置并确认该表计的计量方式、单位及其依赖的现场规则。此前对指定 dev 库及短暂重载的授权是具体历史事实；执行任何动作仍须核对该授权适用的精确目标／动作及当前写入者，未覆盖的新动作不可自行扩权。

| 编号 | 可独立验收的结果 |
| --- | --- |
| R10-AC01 来源无关与授权 | SMA、第三方和其他授权方以同一多区域整包结构分别调用两路，无 DAA／PLC 点／事实前提；机器、设备、目标、区域和指标均由服务端鉴权。未知组／指标（包括未知空组）、越权及类型错误拒绝且无部分写入；实时整包替换要求对所有受覆盖范围授权，省略不能清除越权数据。 |
| R10-AC02 整包与缺测 | 同设备／任务的多组值只占一条实时行，较新整包替换全部区域；省略组、空组、缺省指标均缺测，0、false 和空字符串按类型保留。相同完整授权请求可分别提交实时与历史，历史只保存已启用项并在回执标明跳过；历史启用但整包全缺时保留空／缺测历史样本，设备完全无历史启用指标才返回 `no_history_metrics`。旧包 stale、同刻异值冲突、`groups: {}` 及好质量历史准入可观察。 |
| R10-AC03 幂等和旧回执 | 同目标／producer／事件 ID 原请求重试返回原回执，异内容冲突，显式空组与省略组虽同为缺测但不得改写后假定同一请求；两路独立且原子。r8 旧回执按旧指纹重放，旧新结果／归档位置可定位、不二次写入，事件 ID 不当时钟；两份同刻真实历史事件均保留。 |
| R10-AC04 三表与配置 | 实时唯一键 `(equipment_id, task_no)`；过程一包一行；三主表均有真实 `observed_at`、`created_at`、`updated_at`。设备每目标每区域、能耗每表计每组各 100 槽；区域／指标稳定键和锁定绑定可解码旧值。能耗两表相同键可分别为累计／增量，同表指标可分别为累计／瞬时；模式、物理单位与槽用后不可改写历史。能耗不含订单／任务外键。 |
| R10-AC05 任务选择 | 默认按设备整包 `observed_at` 显示最近采样任务，管理列表默认全部；验证真实时刻、迟到、过期、同刻并列、设备范围及不可伪称生产／空闲。页面打开期间手选不受轮询或新样本覆盖，“跟随最近采样”恢复自动；切换设备和页面重载按规则回到新设备最新，不跨任务或跨包借值。 |
| R10-AC06 能耗口径 | 两块合成表计按各自 `(meterId, groupKey, metricKey)` 发现、授权、写入和解释；累计 `1006−1000=6`、不重叠增量 `2+3=5`，瞬时功率不能直接求和。同包混合时真实区间只属于增量并保存，增量不同区间分事件，同一消耗不重复相加；覆盖空单位、0、缺测、质量、跨日、去重、乱序、重置／换表、缺边界和上海时区。 |
| R10-AC07 页面与权限 | 两级菜单中管理入口位于各自模块且只允许 admin；过程数据管理区分过程／能耗主表。管理员新增、命名、启停、排序多个区域，设置稳定指标键、两目标绑定及卡片；单卡至多 10 项。温度／传动／清洗的同单位图框支持全选／多选区域及多条实际／设定等系列，切换不改变历史留存，异单位不混用无区别纵轴；普通业务读、设备／表计范围和机器权限独立验证。 |
| R10-AC08 卡顿修复与空图 | 在真实浏览器从菜单和直接路由进入温度、传动、清洗、能耗；定位动态导入／导航失败，验证模块依赖、未选择／未配置的通用空 X/Y 与明确原因、已配置无样本的各图空轴和单位、选择区域无点、失败重试及真实数据到达后恢复。不可虚构时间／数值、以截图或 DOM 检查冒充端到端；任务外根因如实记录，不报已修。 |
| R10-AC09 无损迁移与旧能耗 | 先核查旧时间语义／时区、按组行、配置、回执、备注及写入者。新唯一键切换时，不把不同时刻组拼成一轮；旧实时原行和配置可持久、受控只读核查及恢复，旧过程未证同批的各组保留各自时刻和数据；对账原 ID／值／回执／管理信息并验证回退。保全旧能耗量、曲线及两价格表，旧统计切换前可用，不重复统计、不将缺失充零。旧档 UI 依需要决定，历史转换／退役不自动执行。 |
| R10-AC10 交接边界 | 新合同、公开示例与配置及双语页面一致，记录授权目标、实际迁移、检查、合成数据清理及浏览器结果；区分合成 HTTP、SMA 产品、真实设备、独立 QA 和 Human Owner 验收。未获精确 r10 实施批准不进行代码／DB 变更，不以局部成功代替整体通过。 |
| R10-AC11 原采集时间与曲线断点 | 三路新事件的 `observedAt` 缺失、null、无偏移或无法无损存 DATETIME(6) 时拒绝；先保存 T2，再补传较早 T1，随后修改 T1 备注使其 `updated_at` 晚于 T2，温度／传动／清洗历史和曲线仍按 `observedAt` 呈现 T1→T2，与创建、更新、到达和 ID 无关。同一时刻不同真实事件均保留在同一 X 坐标，ID 仅技术分页且不漏点；T0 有值、T1 合法真实包全部历史值缺测、T2 有值时，T1 保存缺测并在所选指标处画断点，不把 T0 与 T2 误连。验证 DAA 完整 DB 摘要的最晚点含 bad 的语义，跨 DB 不虚构时刻；实绩既有可空合同保持不变。 |

**后续逐项配置／确认**：① 每个设备的整包过期阈值、允许未来时间偏差及各写入方时钟来源；最近采样和同刻并列已在 §12.4 确定。② 跨多个 DB／独立样本拼包时，由实际发送方在实施／联调前明确有效批次和真实代表采集时刻规则；单 DB 完整样本可使用其已存在摘要，不推断所有点同刻，也不声称 SMA 已实现自动投递。③ 实施前根据真实旧数据确定持久保全形式、旧／新 ID 与回执映射、只读核查和恢复流程；不能将不同批次合并成单个时刻。④ admin 在每个实际表计／组／指标启用前配置物理量、模式、可选单位及适用区间／采样／重置／换表／缺口规则；未知规则不得猜测。⑤ 能耗保留时长、统计精度／费用及旧统计切换点仍需项目确认；任何删除和历史转换须在相应授权与对账范围内进行。这些现场字段可以随项目逐项配置，不要求收齐所有真实表计资料才能审阅设计、实施软件或执行合成验证。

本节为审阅稿，不是本轮软件或数据库操作指令。Human Owner 审阅并批准精确 r10 后，才进入 Development → fresh-context Verification → Human Owner 最终验收；产品原则已确认，不要求所有真实表计资料先到齐。各角色仅维护各自文档，不倒写既有 QA 结论。

<a id="r10-approval"></a>

### 12.10 r10 Human Owner 精确批准与交接

2026-11-17（Asia/Shanghai），Human Owner 对 `ARCH-OBS-001 r10` §12 明确批准实施和独立验证，并授权指定 dev 目标上的必要操作。批准前 spec SHA-256 为 `683e9e3cc5fcfbc242eccc22ab6a2bedbb0c9a7d7bbd6aee68774c3d8f3ce111`。Human Owner 原文：

> 批准 ARCH-OBS-001 r10 §12，按当前 spec 实施并进行独立验证。授权对 dev 库 127.0.0.1:3307 / industrial_level_2_system 执行必要的保全迁移、配置和合成数据联调；保留现有数据，只清理本次测试数据。必要时可短暂重载后端，先核对现有写入方。

批准覆盖本节其余内容既定的范围、验收、文件 allowlist 和约束，以及指定 `127.0.0.1:3307 / industrial_level_2_system` 的必要保全迁移、配置和合成数据联调；现有数据须保留，仅清理可确认属于本次测试的对象。仅在必要时可短暂重载后端，操作前核对现有写入方并遵守既有数据和用户进程边界。审批不自动扩大至其他数据库、真实设备或 PLC、DAA／SMA 产品改造和现场投递、生产部署、发布或其他未明确授权的动作。跨多个来源的代表采集时刻和实际表计参数仍按 §12 逐项核定，不将未确认的上游能力写成已实现。

标题后版本提示及 §12 中“未批准”“待审”“本轮只修订 spec”“未来获批”之类文字均保留为**批准前历史状态**；本记录和文件头 `Status: owner_approved` 表示上述精确 r10 范围现已获批，不改写原范围、验收标准、allowlist 或风险。r8 的已迁事实与 `qa_failed`、r9 未批准候选和此前所有 QA 证据保持原样；本次范围批准不表示软件已完成、dev 迁移已执行、独立 QA 已通过或 Human Owner 最终验收。

**交接**：实际命名 `development` 按本 spec §12.1–12.9、既有任务 bundle 和已授权目标实施并在 `tasks.md` 记录准确操作、自检、限制及 `developer_handoff`；随后由 fresh-context 命名 `verification` 对精确候选和已授权操作独立验证并在 `checklist.md` 记录结论，再交 Human Owner 最终验收。涉及冲突或批准范围实质变化，按 canonical workflow 回 PM 修订，不以推断扩大授权。

<a id="r11-isolated-recovery"></a>

## 13. r11：隔离迁移复验与前端双语说明修正草案

2026-11-17（Asia/Shanghai）。**本节为 `draft`，尚未获得 Human Owner 批准；本轮只准备可审阅的续办规格，不启动或改动容器、不操作数据库或服务、不改实现和说明文档。** r10 §12 及其 §12.10 的批准、已完成的指定 dev 迁移和各轮 QA 历史仍为原事实；r11 不撤销 r10 的批准，也不把任何旧 verdict 改写为通过。顶端版本提示及 §1–12 的版本／状态用语保留各时点原文，应以本节和各角色记录确定当前状态。

### 13.1 缘由和基线

[r10 QA4](checklist.md#r10-qa4-独立-verificationqa_blocked) 为 **`qa_blocked`**：已关闭 QA-008／009 的原复现，但 R10-AC03 的旧回执重放和 R10-AC09 的带旧数据迁移／恢复仍缺获准的独立目标。dev 中旧 OBS 行与回执在核验时为空，已执行的空数据迁移、SQL 改名预演及合成 HTTP 不能替代带数据的实际在线迁移／恢复。其他尚未穷尽的 AC01–11 条件依 QA4 原记录保留；不得因补测两项就自动改判全部通过。

本节起草前：r10 已批准 spec SHA-256 为 `667eb48607afe9300e675fdc5a2b6152631b58705e2cd18a994bd843ec3df623`；Development 交接 [tasks.md](tasks.md) SHA-256 为 `5cf8f8b6d79998ec1f507202e45c6306bbaee47d4026b2f220c8ebb5cf87287b`，QA4 [checklist.md](checklist.md) SHA-256 为 `7599d30b39d3b1b98e915bc06348b0e83e23f17b4bad8ee16fbb5e4e1e704830`。r10 候选是 `main` 工作树的未提交交付，HEAD `21cd789277695bbafaa55c24e39261fc7247f9b0`，63 项有序清单整体 SHA-256 `8512aaecbd8610cae2d44cf02014b7bb643dddea48bf0876d4866d5eb41fb6ea`；以 Development 交接逐项文件摘要为准，不能将并行工作纳入候选或覆盖。r11 增加的两份 README 不在原 63 项中，修改前以实际工作树和冲突复核为准。

QA4 另记录 [frontend-js/README.md](../../frontend-js/README.md#business-observation-source-selection) 与 [中文配对](../../frontend-js/README.zh-CN.md#业务观测来源选择) 仍把 `dataSource=legacy|http` 和默认 legacy 描述为当前设备／曲线页面行为；现有设备和过程路由已指向 r10 observation 页面。该问题当时不在 r10 §12.9 的直接责任面内，QA 未擅自修改。r11 拟仅同步该部分说明，不能因此推断软件行为或 API 合同改变。

### 13.2 待批准的隔离目标和资源边界

本机 2026-11-17 的只读预检显示已存在 `mysql:8.4.6` 镜像，镜像 ID 为 `sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`、架构 `linux/arm64`；拟用容器名 `arch-obs-r10-qa-20261117-a1` 当时未见同名，宿主 `127.0.0.1:13316` 当时未监听。这些只是时点事实，**不表示容器已创建、目标已验证或 Docker 操作已获批**。

拟在获批后仅为本任务新建一次性 MySQL 8.4.6 独立容器，以精确镜像 ID 启动、宿主端口仅绑定 `127.0.0.1:13316`；容器名为 `arch-obs-r10-qa-20261117-a1`，datadir 使用容器独有临时存储，不挂载已有数据库、项目真实 `.env`、profile 或其他人的卷。测试用空 schema 限该容器内 `obs_r11_main`、`obs_r11_guard`、`obs_r11_recovery`，专用临时凭据和辅助文件限本任务拥有的 `/private/tmp/arch-obs-r11-*`，权限最小且不输出、提交或记录明文。若使用容器桥接网络，不能把宿主回环端口绑定描述为容器网络完全隔离；仍须使用随机强凭据，不连接其他服务。不得拉取新镜像、使用 Compose、修改其他容器／卷或复用已有实例。

启动前复核镜像 ID／架构、容器名称、回环端口和临时目录均符合上述条件并无冲突；不同则停止并报告，不覆盖、替换、自动拉取或自行换目标。创建后记录本次容器 ID、镜像 ID、端口绑定、挂载／存储归属、随机测试身份及新 MySQL 的 UUID、版本、时区；确认其不属于且不指向 `127.0.0.1:3307 / industrial_level_2_system`。每次迁移、写入、恢复或清理前均以实际连接、UUID、schema、容器 ID 和仅本任务拥有的凭据核对目标，任何不符立即停止。不得连接、复制、迁移、降级或清理现有 dev 数据；不修改用户 `.env`、持久 profile、角色配置及运行中的 3307／8000／5190 服务，不操作 SMA／DAA／PLC。离线或临时运行配置必须明确覆盖所有 DB 指向且不得意外读取真实配置；需要源码副本时仅复制必要源码并排除 `.env`、profile、Git 和真实数据，核对与交付候选一致，不以副本取代交付源码。

本节拟请求的 Docker 生命周期仅限**该新建容器**的创建／启动、核对、停止及删除，以及容器内上述合成 schema 的创建、迁移、读写、受控恢复与回收；不授权对现有 Docker 服务做 up/down/build 或对其他数据库执行 DDL。由执行者记录拥有关系、容器 ID、专属临时文件和清理条件；完成验证后协调者先确认身份、无后续依赖和证据已写入角色记录，再只回收该容器及明确归属的临时文件。异常中断时先核对实际容器和目录的归属及状态，再按本节处理；不能因名称相同、时间相近或脚本失败就删除未知资源。关键脱敏证据持久写入本 bundle，不以 `/private/tmp` 的文件为唯一依据。

### 13.3 待批准工作和独立验证

1. **说明修正**：Development 仅在上述两份前端 README 的“业务观测来源选择 / Business observation source selection”中，替换设备状态／过程监控当前 `dataSource` 及默认 legacy 的过时描述；与 r10 的四设备页、过程曲线、配置驱动读取和来源无关上报一致，并链接 [r10 双语使用说明](../../docs/equipment-status-process-monitoring.zh-CN.md#r10-guide)及 [v2 机器合同](../../contracts/published/http-api/equipment-observation-v2/README.zh-CN.md)。英文文档链接英文配对。保留与此无关的通用计划／实绩、部署及历史说明，不能把设备／过程历史合同静默改写成已删除事实。仅作文字及链接检查，不修改页面、接口、权限、迁移或其他源码。
2. **纯合成准备**：使用空的独立目标，通过项目正式 Alembic 链建立到 r8 `8c0e2a4d6f18`；仅构造本轮独有且可逐行追溯的 r8 多组不同时刻实时记录、同刻不同真实事件的过程记录、指标／槽位／卡片／曲线配置、备注／复核标记、旧回执、旧能耗量／曲线和价格行。所有时间是自造、语义明确的上海原采集时间。旧回执须采用原 r8/v1 真实指纹与结果语义并在 MySQL 持久化，保留原请求和基线；不能把新 v2 回执或仅内存模拟说成 r8 旧回执。
3. **迁移与重放**：独立 Verification 核对当前任务唯一写入方已静默、目标旧时间与时区明确、归档目标不存在；再在独立 schema 对实际 r10 迁移 `8c0e2a4d6f18 → 9d1f3a5c7e20` 执行受控在线升级。按旧表逐行核对主键、值、原采集时刻、备注、复核、配置、约束／索引、旧能耗及价格保全；不合并未证明同批的旧组。以真实 MySQL 和 r10 接口重放合成 r8 旧原请求，核对旧指纹、原结果、版本／归档定位与业务行／回执数均正确，重试不产生重复；测试新旧数值 ID 重叠时不混淆位置。
4. **恢复及失败防护**：在该独立目标写入并核对 r10 新样本，确认保全后按迁移既有 guard 执行受控恢复，核验 r8 原表及配置和 r10 保全行／配置均可定位。对该容器内独立空测试 schema，分别验证写入方未静默、旧时间未确认、归档或恢复目的地已存在等条件下的拒绝；对受控 DDL 中断验证停下、对象状态可核查且不会盲目重试／stamp／删除。只运行经审阅的合成流程，按实际结果报告，不能把验证失败自动修补成通过。
5. **职责和交接**：Human Owner 批准精确 r11 后，实际命名 Development 只修改两份 README、创建所需的本任务临时测试材料并更新 `tasks.md`，记录基线、校验、限制与精确 `developer_handoff`；涉及 Docker 与数据库材料按 `docker-expert`、`docker-project-ops`、`backend-arch`，文档按 `project-governance`。其自检不代替独立试验。随后 fresh-context 命名 Verification 独立核对交付身份及中英文说明，并在 §13.2 指定目标自行执行上述合成 MySQL 实测与对账，更新 `checklist.md`；验证完整证据链时复核既有 R10-AC01–11 的已证和未证条件，按真实结果给 verdict。核验受阻或发现实现缺陷时保留证据并交回，**不能在本 r11 内擅自修改实现或扩展文件范围**；需修实现、改变目标或扩展验收时回 PM 修订并重新批准。

### 13.4 允许范围与验收

| 归属 | r11 直接范围 |
| --- | --- |
| PM、角色记录和索引 | PM 只维护本 `spec.md`；获批后 Development、Verification 分别维护 `tasks.md`、`checklist.md` 并保留全部历史；协调者只机械同步对应 PLAN／目录状态。 |
| Development | `frontend-js/README.md`、`frontend-js/README.zh-CN.md` 中 §13.3 指定的来源说明；以及本任务 `/private/tmp/arch-obs-r11-*` 下的临时合成验证材料。其他源码、配置、文档、真实数据及既有服务不变。 |
| Verification | 对交付工作树和上述两份说明只读验证，在 §13.2 明确的独立实例／schema 上执行合成在线迁移、重放和恢复；仅写本任务 checklist 与本任务私有临时测试材料。 |

| 验收项 | 可观察结果 |
| --- | --- |
| R11-AC01 范围与隔离 | Human Owner 精确批准本节及目标后才执行。创建前／后、每次写入和销毁前均有镜像、容器 ID、回环端口、schema、UUID、来源配置及所有权核对；任何碰撞或不一致停止。独立目标只含合成数据，无现有 dev 连接／挂载／修改。 |
| R11-AC02 带旧行升级 | 正式在线迁移从 r8 到 r10；旧实时多组原行及配置可独立核查，旧历史按真实各自采样时刻保留，不拼接不同批次；旧 ID、指标值、回执、备注／复核、配置、约束／索引及旧能耗／价格按各自语义对账。 |
| R11-AC03 旧回执 | 基于真实 MySQL 中的合成 r8/v1 回执，用原请求重放后返回原结果，旧／新 ID 重叠可区分归档位置；对照重放前后业务行和回执数量，证明没有二次写入；不得把来源声明当作已验证血缘。 |
| R11-AC04 保全恢复及保护 | 受控恢复后，r8 原行与配置可核验，r10 新业务行及配置保全可查；未静默、时间未确认、目标冲突及模拟中断均按各自 guard 或受控恢复流程处理，不盲目降级、stamp 或清理。 |
| R11-AC05 双语说明 | 两份前端 README 的当前设备／过程说明和现有页面及 v2 合同一致，不再把 URL 来源切换或默认 legacy 当作现行实现；中英文对应，相关链接与锚点可解析，无关章节保留。 |
| R11-AC06 交接与资源 | Development 和 fresh-context Verification 分开记录实际命令、结果、数据与目标范围、未覆盖项；QA4 和更早失败／阻塞证据保留。任务独有资源清点并按身份回收，真实用户数据、现有服务和配置不受影响；最终验收仍由 Human Owner 决定。 |

原 R10-AC01–11 继续有效；本节只针对已记录缺口提出补验和说明修正，不将 QA4 标为通过、不豁免其余未覆盖条件。真实生产数据迁移、真实 PLC／SMA／DAA、设备动作、现场联调、Redis、生产部署、发布和其他 Docker／数据库操作均不在本续办范围。

### 13.5 建议的精确批准用语

> 批准 ARCH-OBS-001 r11 §13，按方案修正两份前端说明并进行独立验证；授权仅为本次测试在 127.0.0.1:13316 创建、使用和回收指定的一次性 MySQL 8.4.6 容器及其合成数据库，不访问或修改现有 dev 数据库和其他容器。

该句仅为待 Human Owner 决定的建议，不是已获批准；在实际明确批准之前不得实施、启动测试容器或改两份 README。

<a id="r11-approval"></a>

### 13.6 r11 Human Owner 精确批准与交接

2026-11-17（Asia/Shanghai），Human Owner 对协调者的 r11 方案确认问题作出明确答复。该问题指定本规格 §13、两份前端说明修正，以及在 `127.0.0.1:13316` 创建、使用和回收指定一次性 MySQL 8.4.6 容器及其合成数据库，现有 dev 和其他容器不受影响。问题上下文在此转述；Human Owner 的答复原文为：

> 批准 r11，按方案继续

批准前 spec SHA-256 为 `94d18d3945c342b8fb30dfd573033fd713a224b66ee1a00c91e7884ede4fd90c`。该答复批准 `ARCH-OBS-001 r11` §13 的精确范围和其中所列的指定一次性隔离目标、动作及回收，不扩大到其他数据库、现有容器、SMA／DAA／PLC、生产部署或源码实现变更。r10 既有批准、已执行的 dev 迁移及 QA4 `qa_blocked` 与之前全部证据保持原状；本次范围批准不表示隔离验证已执行或通过，也不是 Human Owner 最终验收。

§13 标题及前文的 `draft`、待批准和不得实施措辞保留批准前状态；本记录和文件头的 `Status: owner_approved` 表示本节所列 r11 范围现已获批。实际命名 `development` 按 §13.3–13.4 交付两份说明并在 `tasks.md` 记录自检和精确 `developer_handoff`；其后 fresh-context 命名 `verification` 在 §13.2 指定隔离目标独立验证并更新 `checklist.md`。若目标、范围、验收或风险发生实质变化，停止越界动作并按 canonical workflow 回 PM 修订，不因本批准推断额外授权。

<a id="r12-user-guide"></a>

## 14. r12：设备状态、过程监控和能耗操作手册

2026-11-18（Asia/Shanghai）。Human Owner 接受上一轮关于单独整理一份按实际页面操作的手册的建议：从新增加热区、配置卡片和曲线，到手动 POST、查看列表及能耗配置，步骤简洁但完整。Human Owner 本轮原话为：

> 好的，整理吧。步骤描述简介，但是要完整。

用户明确授权整理这份手册。`r12` 是 PM 为这次文档切片分配的内部编号；用户没有说过该编号，也未逐字审阅本节或作最终验收。本节将其已授权的具体工作落实为下面的文件和验收口径；不推断任何代码、数据库、运行、发布或现场操作授权。顶端 `owner_approved` 表示这项具体文档工作的范围授权，非其他修订的最终验收。

### 14.1 背景和权威边界

现有 [设备状态与过程监控讨论稿](../../docs/equipment-status-process-monitoring.zh-CN.md#r10-guide) 已保留 r10 使用摘要及 r6–r8 历史讨论；新手册单独面向使用者按步骤操作，不替换讨论稿、[r10 规格](#r10-source-independent-energy)或 [v2 机器合同](../../contracts/published/http-api/equipment-observation-v2/README.zh-CN.md)。具体步骤和名称以正式工作树实际前后端为准；合同、程序或页面不一致时标明实际限制，不编造入口、字段、权限或已完成联调。

本节起草前，spec SHA-256 为 `b84a907c6fbf31508816373c165ba70194f89919bac2b99c4f22a8127f33a8ff`，Development [tasks.md](tasks.md) 为 `ca0e06030c2507fdea23e8e141752736d9ba866639d06d6c4b31bf3c8b1b5ffe`，Verification [checklist.md](checklist.md) 为 `5de37a7bbfb528d897f17458ab85ce6825b266c85b676aa14c5c75c58904bcea`。r10 的有界合成 `qa_passed`、r11 §13 的 scoped `qa_passed`、一次可恢复并发死锁／503 和未穷尽项均按 checklist 保留；它们不等于 Human Owner 已最终验收或真实 SMA／DAA／PLC、现场和生产部署已完成。该文档切片不改变上述结论。

### 14.2 交付内容与操作主线

新增一对互链的短步骤指南：

- `docs/equipment-status-process-monitoring-guide.zh-CN.md`：中文操作手册。
- `docs/equipment-status-process-monitoring-guide.md`：英文配对，步骤、示例、限制和链接与中文对应。

两份 `docs/README` 各增加同一手册入口；保留已有讨论稿及其历史。文档按下面顺序组织，语句简洁，必要时用小表提供示例字段及预期结果。示例值均为虚构值，不声称任何现场设备、账号或实时配置已经存在。

1. **准备和权限**：说明从已获授权的目标环境和现有服务开始，admin 管理入口、人类读取权限与设备／表计范围、机器 Bearer 及其目标／区域／指标授权各自独立。明确设备和表计身份及机器授权来自后端仓库外的私有 profile；页面配置区域、指标等不能代替登记设备／表计或赋予机器权限。profile 由环境负责人按实际合同配置和协调加载，不能把示例占位符当成可用凭据或 UUID；设备／表计选项为空、尚无指标或图表时说明实际空态。
2. **加热区和指标**：从“设备状态 → 配置管理 → 区域配置”新增温控类别的合成 `heatZone1`，填写实际界面要求的中英文名称、排序和启用；在“指标设置”登记 `zone1Actual`、`zone1Set` 两个数字指标，按实际控件选择所属区域，填写中英文名、可选 `°C` 和小数位。依实际界面解释“指标键”在区域／卡片表单中对应各自稳定键，“采样组”在槽位表单中需要输入区域键；展示标题可编辑，上报仍使用稳定键。
3. **槽位、卡片和历史**：在“槽位设置”为两个指标分别新增 `latest` 与 `history` 绑定并启用；具体示例逐项列出目标、采样组、槽位和指标。说明每目标每区域独立 1–100 槽，首次使用后绑定和物理含义受保护，实时专用指标可只绑定实时。再在“卡片设置”新增温控页面的双语卡片并添加两指标；一张卡最多 10 项。显示配置、实时写入和历史留存是独立设置，曲线可见不等于已经启用历史写入。
4. **曲线和多区域**：在“过程监控 → 配置管理 → 曲线设置”新增温度类别、同单位的图框及实际／设定两条数值指标；根据实际可用控件解释添加第二个区域及其不同指标键，再在温度曲线页选择设备、任务和采集时间范围，点击“查询”，使用“选择区域”／“全选区域”查看单区或多区。无数据时保留空轴并提示原因；历史横轴按 `observedAt`，不是 `updatedAt`。
5. **手动发现与上报**：给出与步骤 2–4 键名相互对应的可阅读合成 JSON 和必要的手工 HTTP 请求：机器发现 GET、实时 POST、历史 POST。设备两路请求采用同一整包结构、各自发送及核对结果；历史用 `quality: good`，实时更晚采样整包覆盖、缺项变缺测，历史按启用槽追加。说明 `eventId` 是单目标重试身份、相同事件原文重试、不同样本用新事件；`taskNo` 为字符串、`observedAt` 为真实采样时间且带偏移，标量不带单位，未传不等于 `null`，`0`／`false` 有效。必须提示示例中的设备、授权、键和时间先替换为本人获准的配置；通过 curl 等工具使用机器凭据时不得把真实令牌写入文档或仓库。机器 GET 只返回获准定义，不等同于读取历史样本；完整字段、错误码及可省略项链接 v2 合同。
6. **查看与能耗**：按实际侧栏说明四设备卡片、三个过程曲线页，以及各自 admin“数据管理”如何筛选、在“指标列设置”选择显示列、查看详情。实时只可改备注；过程与能耗只可改备注及异常／已复核标记，不在手册中虚构原始值编辑或删除入口。另说明“过程监控 → 配置管理 → 表计指标配置”的实际表计选择、组、指标键、槽位、名称、物理量、计量方式、单位和适用规则；从机器 GET／能耗 POST 到能耗统计／样本列表给出一个简洁示例。能耗按表计独立于 `taskNo`；累计读数、时段增量、瞬时量不可混为一谈，增量样本应按合同携带真实区间，缺边界或连续性未知不补零。
7. **排查与收尾**：简要区分无可访问设备／表计、无配置、无样本、无权限、参数错误、事件冲突、服务未就绪及同一事件重试；提示 503 可出现提交结果未知或竞争失败，按 v2 合同核对后以原事件和原文重试，不误说全部 503 原因相同。测试数据如需清理，应先核实对象归属、引用和授权，由环境负责人按精确记录处理；不提供整表删除、清库或虚构前端删除功能。手动 HTTP／模拟发送方不等于 SMA 产品或真实 PLC 已接入。

### 14.3 范围、验收与角色交接

| 归属 | 允许范围 |
| --- | --- |
| PM | 仅本 `spec.md` 的 §14 和相应元数据；保留 r10／r11 及更早历史原文。 |
| Development | 上述两份新手册、`docs/README.md` 与 `docs/README.zh-CN.md` 的对应索引行，以及本任务 `tasks.md` 自检与交接；不修改现有讨论稿或其他源码／配置。 |
| Verification | 精确交接后使用 fresh context 独立检查工作树及合同，在本任务 `checklist.md` 记录证据和 verdict，保留所有历史。 |

| 验收项 | 可观察结果 |
| --- | --- |
| R12-AC01 实际界面与前置 | 中英文手册从服务和权限前提开始，以真实侧栏、表单标签和操作顺序覆盖 §14.2 的区域、指标、两目标槽位、卡片、曲线和多区域；解释空设备／表计、私有 profile 与界面配置的区别。 |
| R12-AC02 端到端示例 | 一套一致的虚构区域、指标、卡片和曲线样例可贯穿页面与机器请求；至少有一份实时／历史共用正文、各自路径、按原类型传值及采样时间／任务号／事件号说明，足以让读者理解如何自行用获准设备重复；机器 GET 不被描述为业务值读取。 |
| R12-AC03 列表、能耗和异常 | 根据当前界面写明两个设备／过程列表和能耗样本的列显示、筛选及允许编辑内容；给出表计指标配置与独立能耗上报／统计示例，区分三种计量方式、时间区间、缺测及异常处理。 |
| R12-AC04 正确性与边界 | 两稿对应、互链，双语文档索引可达；引用现行 v2 合同及 r10 操作基础，核对新增路径、锚点和 JSON 示例可解析。示例无真实地址、口令、token 或客户数据；明确测试条件和清理责任，不声称真实 SMA／DAA／PLC 或生产部署已完成。 |
| R12-AC05 范围与记录 | 差异限本节和列出的两份手册、两行索引、对应角色记录；其他并行工作和既有 QA 原事实不被覆盖。文档编写和静态核验不执行 POST、数据库写入／迁移、项目配置修改、服务切换、Docker 操作或设备动作。 |

Development 使用 `project-governance` 和 `aiis`，对操作步骤、接口与当前实现分别核对 `frontend-ui`／`backend-arch` 的适用边界；此处是阅读与文档整理，不授权 UI 或后端代码改动。完成后由实际命名 Development 在 `tasks.md` 记录具体文件、静态检查、限制和 `developer_handoff`，再交 fresh-context 命名 Verification 核对并更新 `checklist.md`。范围若实质扩展，按 canonical workflow 返回 PM。独立 QA 通过后仍须 Human Owner 决定手册的最终验收。
