Task ID: ARCH-OBS-001
Revision: r7
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: r7 §9 已获 Human Owner 精确批准，交命名角色 `development` 实施
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 配置驱动的设备状态看板与独立过程历史
Owner: AIIS ICS Architecture
Acceptance Chain Reference: 本稿第 9 节及 Development Lifecycle Workflow
Related Task: ARCH-ACQ-001, ARCH-ACQ-003, ARCH-BE-010, aiis-ics-arch.aw.sma::SMA-004
Created: 2026-11-07
Updated: 2026-11-11

# 配置优先的设备状态与过程监控方案

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
