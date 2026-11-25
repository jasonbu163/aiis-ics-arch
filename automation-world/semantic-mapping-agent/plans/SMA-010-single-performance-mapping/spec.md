Task ID: SMA-010
Revision: r2
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM → Human Owner 审阅并决定是否批准 SMA-010 r2；当前仅起草规格
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch.aw.sma
Classification: child_inherited
Capability: SMA HTTP映射桌面应用的分阶段交付
Owner: AIIS Automation World / SMA 模块 Human Owner
Acceptance Chain Reference: SMA-001 总交付链：各任务精确 Task ID / Revision 范围批准 -> Development developer_handoff -> fresh-context Verification -> Human Owner 分阶段及总体最终验收
Scope Slice: 一份采集历史样本经已保存映射单次写入实绩并按任务号回读
Parent Task ID: SMA-001
Same Capability: yes
Same Owner: yes
Same Acceptance Chain: yes
Depends On: SMA-004 r1 已验收的本地配置和纯预览基线；实施时选定的采集与实绩 dev HTTP 合同及测试数据可用
Related Task: SMA-008 r3, SMA-009 r1, aiis-ics-arch::ARCH-TASK-001, aiis-ics-arch::ARCH-ACQ-006

# SMA-010：炉温 → 实绩单次闭环

## 1. 目标与本次授权

在 SMA 选定一份采集历史样本，用已保存的映射把其中的炉温点和该点原始采集时间写入一条实绩。`taskNo` 与其他目标参数一样，可以绑定同次样本中的任务号点位，也可以选择固定值；正常使用按配置读取每次样本的任务号，首轮 dev 测试可选固定值。用户先查看实际 POST 地址和 JSON，再显式点一次推送，随后按本次预览中的任务号 GET 实绩回读。

本次请求是“先在 SMA-001 下起草‘炉温 → 实绩’单次闭环的子规格，我先看看，暂时不改代码”。随后 Human Owner 澄清，正常使用时 `taskNo` 应可来自 DAA 写入的 GET 样本，固定值是首轮测试可选择的绑定方式。PM 将未获批准的 r1 草案修订为 r2；本 r2 仅为草案，未获得实施范围批准。新任务使用既有 [SMA-001 r2 总规格](../SMA-001-cu-integration-and-scope-cleanup/spec.md)阶段④的能力、Owner 与验收链。父子关系复用背景，每个 Revision 的批准、实施、独立验证和最终验收分别记录。

此前 SMA-008 r3 的验收对象是采集样本写回，SMA-009 r1 首批包含该入口。两者既有 Development、QA 和等待 Human Owner 的历史按原 bundle 保留。Human Owner 后续要求撤走临时手工回环及事实表上的入口，现工作树已发生对应 DIRECT 变更。本任务以当前工作树为基线，采用实绩作为新目标；本草案不追认 SMA-008、SMA-009 通过或改变其历史状态。 [SMA-008](../SMA-008-acquisition-data-get/spec.md) · [SMA-009](../SMA-009-workspace-and-loopback-ui/spec.md)

## 2. 合同与当前可复用能力

| 输入或能力 | 本阶段使用方式 |
| --- | --- |
| `GET /api/v1/acquisition-data/options` | 用户显式加载 PLC 和 DB，选定一个来源。若需要先查看候选点，可使用现有 `latest` GET。 |
| `GET /api/v1/acquisition-data/history` | 按当前 PLC、DB 和采集时间查历史摘要及分页。后端合同允许按最近记录或合法时间区间查询。 |
| `GET /api/v1/acquisition-data/history/{id}` | 以用户所选历史行的 `id` 取一份完整样本，读取 `data.sampleId`、`data.plcId`、`data.dbNumber` 和 `data.points`。全部动态点值来自这份详情。 |
| `GET /api/v1/integration/task-field-configs?module=performance` | 只读确认目标环境的 `configVersion`、字段 `name`、类型、启用状态、`performanceOwner` 与 `syncEnabled`。实绩集成上报字段须符合目标环境的可写条件。 |
| `POST /api/v1/integration/performances/upsert` | 人工确认后发送一个实绩请求。响应检查 HTTP、业务 `code`、`data.outcome` 和 `data.performance.taskNo`。候选合同的 outcome 为 `created`、`updated` 或 `unchanged`。 |
| `GET /api/v1/integration/performances/by-task/{taskNo}` | 读取提交任务的实绩记录。核对 `data.taskNo`、`data.items` 中实际配置的字段键及 `data.lastObservedAt`。 |

接口依据 [plc-facts/v2 读取合同](../../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md#读取接口)及 [任务／实绩 HTTP v2 候选合同](../../../../contracts/published/http-api/generic-task-workflow-v2/README.zh-CN.md)。本仓候选 OpenAPI 的性能读写路径见 [OpenAPI](../../../../contracts/published/http-api/generic-task-workflow-v2/openapi.json)。这些文件是源码候选，不能证明当前 dev 已部署对应版本。实施和真实联调时按选定地址只读核对实际 OpenAPI、字段配置和响应。既有开发合同使用无 Bearer 的集成接口；如果实际部署合同不同，显示实际失败并据证据确定后续处理，不修改后端。

`furnace_temp` 是本任务的采集示例点位。`items` 的实绩字段键来自目标环境启用且允许集成写入的配置，不能预设 `furnaceTemp` 已存在。目标字段一般选择 `type=number` 且 `performanceOwner=automated` 或目标合同允许的 `snapshot_auto` 字段；若无可用字段，由页面显示原因。测试使用的 `temperatureValue`、`heatingReady` 只是隔离夹具中的字段名。

现有 SMA 具备本地 SQLite 配置 revision/CAS、OpenAPI 材料、目标 API、值规则、字段绑定、固定值和纯预览。TSS 派生的纯映射 domain 已有类型、合法值、必填／可选和组包语义。当前已保存映射的本地预览不带采集事实，正常 manual/start/resume 入口仍拒绝投递。复用现有 domain、HTTP 和历史查询能力时，以实际调用链及本任务验收为准，不恢复对旧 `/api/tss/v1` claim、租约和远端配置的依赖。 [SMA 使用说明](../../README.zh-CN.md) · [本地配置 spec](../SMA-004-local-configuration/spec.md)

## 3. 本次功能范围

### 3.1 配置、来源与样本

1. 继续使用已保存的 SMA Backend 地址和 `SMA_HTTP_ENABLED` 门禁。选择已有 GET 材料、PLC、DB 和炉温点位，按历史 API 查询并从列表选择一行。页面可使用现有只读入口的必要组件和交互。若恢复历史筛选或点位表能力，使用当前工作树的采集只读实现作为基础，不恢复采集写回入口。
2. 按选中行的十进制 `id` 显式 GET 一次 `history/{id}`，核验详情所属 PLC、DB 与所选行一致，展示 `sampleId`、炉温点 `pointId`、值、类型、质量及该点 `observedAt`。同一映射中的其他动态点位必须从同一详情的 `data.points` 获取。`latest` 可用于查找和查看最新值，不得把不同 `sampleId` 的最新点拼成一次样本。历史详情失败、过期、无效或身份不匹配时清除本次有效选择。
3. `taskNo` 在映射参数处沿用现有事实值／固定值两种绑定。选择事实值时，配置来源身份与任务号点位，每次从当前选中的同一份历史详情 `data.points` 取字符串任务号，随样本切换而变化。选择固定值时，保存并使用用户输入的任务号，首轮 dev 人工测试采用此方式。任务号须符合目标合同，候选合同对 ASCII 任务号去首尾空格并转大写，规范化后的结果须匹配 `^[A-Z0-9._-]{1,50}$`。预览显示本次绑定方式、来源值以及规范化后用于发送和回读的任务号。动态任务号点位缺失、质量不可用、类型错误、值为空或格式无效时，标明该参数及原因，阻断整次推送；不回退到此前样本、固定值或其他映射。绑定目标 `items.<实际字段键>` 的炉温来自所选详情中用户配置的炉温点。`observedAt` 来自同一个炉温点的原始 `observedAt`，保留真实瞬时和精度，界面按上海时间展示。其他动态参数如有配置，仍从这份样本取值。
4. 一个映射可包含多个目标参数，按已有绑定语义选择固定值或样本点位，可按参数引用已有同类型合法值规则。固定值保留字符串、数字、布尔等 JSON 类型。`0`、`false` 和空字符串依合同与字段类型分别处理。配置和临时事实适配须沿用已有本地 revision、引用和类型校验，不能把未验证来源呈现为已验证。

### 3.2 组包、预览、推送与回读

1. 用户显式选择一条已保存映射后，使用该映射的目标参数、固定值、选中样本和关联规则生成预览。单次测试目标须为已保存 Backend base URL 下的 `POST /api/v1/integration/performances/upsert`；其他方法或路径在 Rust 准入处拒绝。预览显示配置 revision、来源 PLC／DB、历史样本 ID／sampleId、本次任务号及绑定方式、实际 POST URL、完整 JSON 和逐参数诊断。请求按当前目标合同组织 `taskNo`、炉温字段、`observedAt` 等参数；没有配置的可选参数不自动写值。
2. 必填属性或本映射标为必填的炉温、任务号和 `observedAt` 缺失、质量不可用、类型错误或不满足关联合法值规则时，展示对应参数及原因，不能产生可发送预览或发 POST。可选参数出现同类问题时，记录可见诊断并从最终请求中移除该参数。即使目标 body template 中有该参数的旧默认值，也须从最终请求删除，不以 `null`、空字符串或旧值代替。未显式选择值规则时沿用已有类型兼容的直接绑定行为。
3. 成功预览由 Rust 服务持有本次有效请求，绑定已保存 revision、源、样本、该样本解析出的任务号、目标和实际字节。打开或关闭预览、做 GET、修改表单和纯预览均不发送业务 POST。连接、已保存配置或 revision、来源、所选样本、绑定或规则发生变化时，旧预览失效并提示重新生成；迟到的旧请求结果不能替换新的用户选择。确认动作仅使用当前有效预览，不能由前端传入被替换的任意正文或目标路径，回读使用该预览冻结的任务号。
4. 用户显式点「测试推送」后，使用同一份预览向配置中的实绩 `upsert` 发送一次 HTTP POST。进行中防双击和并发重复发送，取消、返回和点击遮罩关闭不发送。该次预览已发送或结果未知后不能重复使用；后续操作需要重新预览并由用户决定是否确认，未知时先执行只读回读。无需填写采集样本写回用的 target PLC、DB、实例、代次或 `sourceSeq`。本单次入口不放开普通 mapping 的全局 start／resume／auto-start。
5. 显示 HTTP 状态及业务回执。仅当响应结构与候选合同相符、业务 `code=200`、`data.outcome` 是允许值且 `data.performance.taskNo` 等于预览任务号时显示提交结果；同时展示 `planSync` 以便观察同号计划影响。HTTP 成功但业务错误、回执身份不符或响应结构异常均不得显示成功。
6. 提供「按任务号回读」。使用预览里的任务号请求实绩 by-task GET，以本次预览字段键展示回读 `items`，对照炉温 JSON 数值及 `lastObservedAt` 与炉温点 `observedAt` 的同一瞬时，显示一致、不一致、未找到和查询失败。不要用页面刷新时刻代替采集时间。对于未发送的可选字段，回读时显示其实际现值；保留旧值的验证使用事先建立的隔离夹具和写入前快照。
7. 超时、断连、`task.commit_unknown`、无效或丢失回执等无法判明目标是否提交时显示“结果未知”，允许按同一任务号查询后由操作人判断。回读值恰好一致也可能是既有值或其他写入，界面应展示读到的实际状态而不凭数值自动声称本次请求一定成功。本阶段不自动重试、不在重启后自动补发，也不向用户暗示该实绩 upsert 有样本身份级去重。

### 3.3 存储与实际数据边界

- 延续 SMA-004 的 SQLite 配置与备份合同。连接、目标和映射的固定参数可存为配置。选中样本、点值、完整请求、推送回执和会话结果仅用于当前会话，不写入配置库、备份或日志正文。本阶段不建立本地最新值缓存、采集历史、游标、持久待发队列或运行表。后续本地最新值缓存另行设计。
- 现有 v1 配置库和配置备份须能按原行为读取和显式保存；新入口不能因打开应用改写或丢失旧材料、规则、映射和已存在的历史字段。涉及新配置形态时先证明旧文档可读及显式写入的兼容方式，不自动迁移用户真实库或历史数据。
- 用户此前明确表示希望自己点推送。Development 与 Verification 对自有隔离 HTTP 夹具和临时 profile 执行 POST；真实 dev POST 由 Human Owner 在 SMA 界面明确操作，先只读确认实际目标、测试任务号和字段。选择专用测试任务号并先查询同号实绩及计划。实绩 upsert 可能创建或更新实绩，并可能同步同号计划状态和满足配置的共享字段；回执中的 `planSync` 及预先读取结果用于核对。已有真实业务任务和历史不能作为随意覆盖的测试载体。
- 当前 API 示例中的 `productionStatus` 默认为 `running`；创建实绩本身和同号计划同步有业务影响。测试请求只发送本映射有意配置的字段，并在预览显示任务号和最终正文。允许用户在 dev 自己对已确认的测试任务发一次 POST；无需额外创建计划或更改后端字段配置。若目标测试任务或启用的可写炉温字段不存在，报告实际状态并另行处理数据准备。

## 4. 实施面、复用与排除

范围限于 `automation-world/semantic-mapping-agent/` 下完成本流程直接需要的 `src/App.vue`、`src/app/twin-facts/{api,components,store,views,locales}/`、`src/locales/common/`、`src/console/` 的界面、国际化、既有表格及本地状态适配，`src-tauri/src/{app.rs,commands,services,domain,contracts}/` 的采集详情、映射计算、单次性能上报和回读，以及相关定向 `tests/`。允许新增与本切片直接相关的组件或模块，必要时调整 SMA 双语 README、模块 README 及根 `CODE_INDEX.md`。现有目标字段引用、规则和纯预览应复用，SMA UI 消费 `automation-world/console-ui/` 共享组件和设计 token。

本次拟交付的是指定实绩目标的显式单次测试。持续采集与上报、批量启动、自动定时、失败自动重试、重启恢复、可靠历史续读、实时／过程目标、通用 GET 编排、本地最新值表、配置管理页面和新的批量导入／导出均为后续范围。当前普通自动运行门禁保持有效；不更改 backend、DAA、DS、CU 源码、真实数据库 schema、真实来源注册及业务配置，不引入 consumer 服务 Bearer 作为本阶段的新依赖。

Development 与 Verification 按实际改动使用 `frontend-ui`、`desktop-tauri`、`rust-runtime`、`i18n-workflow`、`code-document-indexer`；涉及外部 API 语义核对时参照现有合同与 `backend-arch`。使用项目 `pnpm` 和 Cargo 工具链。中英文、明暗主题、键盘操作、稳定列宽偏好、遮罩关闭语义与业务时间口径按根 `AGENTS.md` 和 SMA 现有 CU 能力处理。界面只增加完成本单次流程所需操作，后续全应用重排以独立范围确定。

## 5. 验收夹具与标准

下列值为自有夹具，不代表已存在于 dev。源历史 `H1` 对应 `PLC-DEMO / DB21 / sample-001`，`furnace_temp` 为 `REAL`、`820.5`、`quality=good`、`observedAt=2026-11-10T21:56:44.308915+08:00`；可选 `heating_ready` 为 `BOOL`、`false`、`quality=good`，点时间与炉温点不同但属于同一 `H1`。任务号点 `task_number` 为 `STRING[50]`、`quality=good`，H1 的值为 `TEST-SMA-HEAT-001`，另一采样 H2 的值为 `TEST-SMA-HEAT-002`，且 H2 具有不同炉温和时间。夹具实绩字段启用 `temperatureValue:number` 与 `heatingReady:boolean`，写入权限属于 `automated`，目标事先可读取一条任务为 `TEST-SMA-HEAT-001` 的实绩，其中 `heatingReady=true`。固定值验收使用 `taskNo=TEST-SMA-HEAT-001`；动态值验收将 `taskNo` 绑定到上述 `task_number`。炉温对应 `items.temperatureValue`，可选点对应 `items.heatingReady`。以测试自有 profile 和隔离服务计数、记录请求、预置目标状态。

| ID | 验收标准与可观察证据 |
| --- | --- |
| AC01 选择与只读 | 选一条 GET 材料、PLC、DB 和点，历史列表实际返回摘要，选择 H1 后读取 H1 的详情并显示 `sampleId`、点类型、值、质量和点时间。空列表、无详情、404、超时、错误和门禁关闭均给出原因；只读操作期间 POST 计数为 0。 |
| AC02 同次采样 | 构造 latest 中炉温来自 H1、布尔点来自 H2。页面以用户选中 H1 的 `history/{id}` 生成预览，预览中的所有动态值均来自 H1，`observedAt` 等于 H1 炉温点时间。切换 H2 后旧 H1 预览无效。详情返回不同 PLC／DB／sampleId 或过期时不能继续推送。 |
| AC03 固定值与类型 | 配置并保存固定 `taskNo=TEST-SMA-HEAT-001`。重新加载后预览任务号不变，同一 JSON 的 `items.temperatureValue` 是数值 `820.5` 而非字符串；另一组夹具确认数字 `0` 和布尔 `false` 原样保留。身份和数据类型可从预览及接收端记录核对。 |
| AC04 必填失败 | 分别让任务号未配置或无效、炉温缺失、类型不兼容、质量 bad、炉温点时间缺失或非法，以及必填值触发不匹配的合法值规则。每次显示具体参数与原因，不能确认推送，隔离目标 POST 计数始终为 0。固定值不匹配所选规则时保存／预览须报错。 |
| AC05 可选失败 | 以 H1 和目标预置的 `heatingReady=true` 为基础，分别模拟可选点缺失、类型不兼容、质量 bad、合法值规则不通过。每个预览显示省略原因，最终 JSON 无 `items.heatingReady`；即使模板含旧的默认值或 `null` 也无该键。用户确认后隔离目标收到的字节与预览一致，回读仍为预置 `true`，`temperatureValue` 为 `820.5`。 |
| AC06 显式确认与竞态 | GET、预览、取消、关闭／遮罩和返回时 POST 均为 0。一次有效确认产生且只产生 1 次 POST；发送中双击或并发调用、发送后重用旧预览均不能多发。依次改变连接、本地 revision、来源、点位、样本、绑定和规则，旧预览失效且不能发送；延迟返回的旧结果不覆盖当前样本。以不同 HTTP 方法、目标路径或替换正文直接调用单次入口时拒绝，目标接收数为 0。 |
| AC07 回执和回读 | 隔离目标返回 HTTP 200、`code=200`、允许的 `outcome` 与匹配 `data.performance.taskNo`；页面显示实际结果与 `planSync`。以预览任务号读 by-task，显示 `items.temperatureValue=820.5`，`lastObservedAt` 解析为炉温点 `observedAt` 的同一瞬时，并按上海时间展示到秒。修改目标返回值或时间时显示不一致。 |
| AC08 错误与未知 | 覆盖 HTTP／业务非成功、200 但业务 code／outcome／taskNo 不匹配、请求超时、服务提交后断开及 503 `task.commit_unknown`。失败或未知状态清楚，不能显示推送成功，不自动重复 POST。未知结果的只读回读展示实际状态；仅凭回读相同不能自动确认本次请求已提交。 |
| AC09 配置与数据 | SMA-004 v1 配置及旧备份可重开、读取与显式保存，现有映射、规则和材料保持；对自有隔离 profile 检查仅有配置被持久化，采集点值、请求正文、回执和提交状态不进入 SQLite、备份或日志正文。普通 start／resume／auto-start 仍拒绝运行。 |
| AC10 界面与回归 | 人工测试路径经应用正常入口可达，保留既有只读采集、目标配置、映射和值规则操作；无手工采集写回入口。中文／英文、浅色／深色在 1280×800 与 1024×720 覆盖可读状态、错误、键盘、预览与回读弹窗和长内容滚动，表格列宽调整与恢复按现有 CU 规则验证。Development 记录 `pnpm check`、`pnpm test`、`pnpm build`、适用 Cargo 检查及链接／diff 检查。 |
| AC11 dev 人工证据 | 用户自行检查实际 OpenAPI、字段与专用任务号，记录采集样本身份、实际固定任务号及字段键；在 SMA 预览后自己点击一次 POST，记录 HTTP／业务回执、`planSync`，按同号回读比对炉温和原点时间。仅当有隔离证据及该真实 dev 证据、fresh Verification 复核后，才交 Human Owner 最终验收。dev 不具备目标字段或样本时报告缺项，不能用夹具冒充真实证据。 |
| AC12 动态任务号 | 将 `taskNo` 绑定为任务号点位，先选 H1、后选 H2，两次预览分别显示 `TEST-SMA-HEAT-001` 与 `TEST-SMA-HEAT-002`，炉温、任务号均来自各自同一次详情。切换后 H1 的预览不得推送；确认 H2 时，隔离目标的 POST 正文、回执身份及 by-task 回读均使用 H2 规范化后的任务号，不发送 H1。分别覆盖任务号点缺失、bad、非字符串、空值及非法格式，显示原因且 POST 计数为 0，不使用上一条样本或固定值回退。该项通过隔离夹具验证，无需追加真实 dev POST。 |

验证需区分夹具中的产品能力、用户的 dev 写入与最终验收；不得将 Swagger 手工 POST 或原采集回环当作本任务通过。测试只针对本阶段单次映射，不证明每条历史样本均投递或连续运行可靠。

## 6. 风险、约束与回退

- 候选后端合同与当前 dev 的启用字段可能不同。以实际只读字段定义和响应为联调输入，不能通过编造字段名或改变后端配置掩盖不匹配。真实数据写入范围和 `planSync` 需在测试前明确。
- latest 的每个点可能来自不同样本；本次只把 `history/{id}` 选中详情作为单次组包输入。炉温点和样本汇总时间含义不同，目标 `observedAt` 以该点原时间为准。
- upsert 是部分更新，同号目标的非本次字段可能有既值或来自其他写入。未知结果先查询并展示，不能把回读状态推断成本次提交的证明。生产投递的幂等、可靠续读、持久进度和重启恢复另行确定。
- 实施遇到不兼容的现有 profile 或失效引用时，停止该写入并保留原配置，避免修复性自动覆盖。若本任务需额外 schema 迁移、改变后端合同、扩大可调用目标或引入自动上报，返回 PM 修订范围。
- 交接与验收时按根 `AGENTS.md` 记录测试自有临时资源、用途及清理条件，不能清理仍属于用户或其他任务的进程和数据。回退已交付代码的动作与任何真实数据处理另行按当时授权执行。

## 7. 后续与待确认事项

第一条完成后再审议本地最新点值覆盖缓存、采集／上报独立启停和多映射调度；需要每个历史样本完整送达时再确定续读、幂等和重启恢复。统一 JSON／XLSX 配置管理、实时／过程目标及整个 SMA 的页面重排由后续任务负责。各阶段使用各自的明确范围与验收。

dev 的炉温字段键、可用源样本及专用测试任务号在实施或人工验收前由环境实际只读查询确认；这里不把示例名称当成现存数据。操作人应同时核对该任务号是否已有同号计划及可能的同步影响。

## 8. 修订与批准

| 日期（Asia/Shanghai） | Revision | 真实状态 |
| --- | --- | --- |
| 2026-11-24 | r1 | Human Owner 请求起草「炉温 → 实绩」单次闭环，明确固定 `taskNo`、同次采样、预览后人工 POST、按任务号回读、必填失败阻断与可选失败省略。PM 形成本草案，等待 Human Owner 审阅。 |
| 2026-11-24 | r2 | Human Owner 澄清任务号通常随 DAA 写入的采样数据变化，固定值作为首轮测试可选项。新增同次样本动态绑定、任务号无效阻断和两样本隔离验收，r1 草案未获批准；r2 等待 Human Owner 审阅。 |

Human Owner 批准精确 Revision 后再交 Development。Development 交接后由 fresh-context Verification 建立并填写 checklist，最终验收由 Human Owner 明确决定。
