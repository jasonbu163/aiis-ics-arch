Task ID: ARCH-OBS-004
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 r1 实施与独立验证；交 Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 设备状态与过程监控配置管理双卡片及可选筛选
Owner: Core 设备观察、过程监控与能耗数据
Acceptance Chain Reference: 本规格范围批准 → Development handoff → fresh-context Verification → Human Owner 最终验收
Related Task: ARCH-OBS-001、ARCH-OBS-003

# 设备状态与过程监控配置管理调整

## 1. 目标与当前事实

将两个模块的配置管理页按同一交互方式调整：上方卡片选择配置类别，下方卡片显示该类别的操作、筛选和表格。管理员打开槽位设置和表计指标配置时，默认查看其权限范围内的全部配置，并可按条件筛选、清除筛选。设备状态和过程监控各保留现有菜单和页面，不合并成一个新页面。

当前工作树的设备配置页有区域配置、指标设置、槽位设置、卡片设置四个页签；过程配置页有曲线设置、表计指标配置两个页签。槽位查询 `GET /equipment/metric-slot-bindings` 必须同时提供 `target` 和 `groupKey`，返回 `data.items` 与精确分区的 `data.remaining`。表计配置 `GET /energy/metric-configs` 必须提供 `meterId`，可选 `groupKey`，返回 `data` 数组，并按用户角色的表计范围鉴权。`GET /monitor/curve-configs` 已有可选 `category`。所有路径均相对于 `/api/v1`。现有实现见 [管理 API](../../backend/app/equipment_observation/api/routes.py)、[设备配置页](../../frontend-js/src/app/equipment/views/observations/admin.vue) 和 [过程配置页](../../frontend-js/src/app/monitor/views/observations/admin.vue)。

本任务独立承接本次页面及查询调整。它与 [ARCH-OBS-001](../ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md) 的实时、历史和能耗业务语义以及 [ARCH-OBS-003](../ARCH-OBS-003-observation-receipt-separation/spec.md) 的表命名、回执和已记录验证相关，但不继承或改变它们的批准、QA 或最终验收状态。

## 2. 页面范围和交互

1. **双卡片**。设备状态上卡标题为“指标与快照管理”，提供区域配置、指标设置、槽位设置和卡片设置；过程监控上卡标题为“曲线与历史管理”，提供曲线设置和表计指标配置。各页的下卡标题随选择变化，首行右侧放“新增”和“重置列宽”，第二段放筛选与“查询”“重置”，第三段放对应表格。沿用现有侧栏、路由、项目主题与共享组件；中英文、明暗主题和窄屏均可用。原型里的数据与简化弹窗仅用于说明布局，真实功能和字段以本规格及现有业务合同为准。
2. **默认与筛选**。每类表格第一次进入时条件为空并显示全部适用记录，包含已启用和已停用项。填写或选择条件后点击“查询”，各非空条件以 AND 组合；“重置”清空该表全部条件并立即恢复全部。空条件在发请求时省略相应参数，不传字符串 `all` 或自行拼接空键。切换类别再返回时保留该类别最后一次执行的条件；未提交的临时输入不应冒充已执行条件。刷新整个页面后回到各类别默认全部。筛选不更改配置数据、显示项启停或列宽。
3. **筛选字段**。区域配置按类别及区域键／中英文名称查询；指标设置按采样组及指标键／中英文名称查询；槽位设置按写入目标、采样组及指标键／中英文名称查询；卡片设置按页面及卡片键／中英文标题查询；曲线设置按类别及曲线组键／中英文标题查询；表计指标配置按表计、采样组及指标键／中英文名称查询。选择条件使用稳定键而非翻译文案；关键词去首尾空格后按包含匹配，英文不区分大小写，中文原样匹配，两个语言名称均可查。组合条件作用于完整的、当前用户可读取的记录集合，不得只筛选已显示的部分行。前端可对已取得的完整集合执行关键词匹配，不因此更改后台精确查询返回值。
4. **表格身份与时间**。槽位表增加“写入目标”和“采样组”列，同一采样组的实时、历史和不同槽位可区分；保留指标键、启用开关。现有 `firstUsedAt` 是槽位首次使用时间，列名显示“首次使用时间”，为空显示 `—`，按项目上海时区显示到秒，不能称为采集时间或用当前刷新时间补值。表计指标表增加所属表计列，至少可辨认 `meterId` 及其显示名称，保留采样组、指标键、名称、计量方式、单位及编辑入口。无对应名称时显示稳定键，不把缺失数据伪造为名称。其他列表保留现有字段和操作，曲线列表可展示已配置曲线指标以对应预览。
5. **新增与编辑**。所有现有新增、编辑、槽位启停、曲线／卡片指标及顺序、表计指标的模式、单位、规则和首次使用保护继续生效。槽位新增仍明确指定单一 `target`、`groupKey`、`slotNo` 和指标，精确筛选时可预填所选条件，全量时由用户选择或填写；不能以“全部”作为写入目标。表计新增在筛选为全部时，弹窗要求从当前账号有范围的表计中明确选择一个，选中单表计时可预填；无可访问表计时新增不可提交并说明原因。表计编辑按该行不可混淆的 `(meterId, groupKey, metricKey)` 定位，槽位启停按 `(target, groupKey, slotNo)` 定位。保存成功刷新相应表并保留已执行筛选。
6. **加载与列宽**。加载中、无配置、筛选无结果、请求失败均有可区分状态；失败不能显示为成功空表。筛选、重置、页签或页面快速切换及较慢请求乱序返回时，只允许当前选择的最新有效结果显示和操作。旧的行、弹窗和保存回执不能写入另一条配置或恢复失效表格；必要时取消、禁用或关闭过期操作。每张表复用既有公共列宽能力，普通列可拖动并有最小宽度，宽表可横向滚动；列宽按稳定字段与表各自本机保存，筛选、刷新及页面切换后保持。按钮文字“重置列宽”，提示“恢复默认列宽”，只重置当前表列宽，不清除筛选。

## 3. 查询合同与权限

本节扩展管理员查询；现有精确调用、标准响应信封、写入接口和机器接入合同保持兼容。默认全部指所有符合该接口既有授权边界的**配置记录**，不生成 100 个尚未绑定的空槽位，也不查实时值或历史样本。

### 3.1 槽位查询

`GET /api/v1/equipment/metric-slot-bindings` 的 `target`、`groupKey` 均变为可省略：两者都省略返回所有绑定；只给一个则只按该项筛选；均提供时与现有精确分区语义一致。`target` 非法、显式空 `target` 或显式空／无效 `groupKey` 仍按现有校验拒绝，不因空值变成全量。结果包含已停用行，逐行保留 `target`、`groupKey`、`slotNo`、`metricKey`、`enabled`、`listVisible`、`listOrder`、`firstUsedAt` 原语义。各分区独立 100 槽，排序稳定；完整分区按既有 `slotNo` 顺序，多分区按目标、组及槽位稳定排序。

保持 `data` 对象的 `items` 与 `remaining` 字段。**两参数均存在且合法时**，`remaining` 仍是 `100 - 该目标与组已绑定行数`，包括已停用绑定；前端关键词筛选不会改变该分区剩余容量。**省略任一参数时**，`remaining` 为 `null`，表示不存在单一分区的剩余容量；不能对跨组结果相减，亦不能把 `null` 显示为零或 100。原精确请求的字段、记录、顺序与计算不回归。

```text
GET /api/v1/equipment/metric-slot-bindings
GET /api/v1/equipment/metric-slot-bindings?target=latest
GET /api/v1/equipment/metric-slot-bindings?groupKey=heatZone1
GET /api/v1/equipment/metric-slot-bindings?target=latest&groupKey=heatZone1
```

槽位及其区域／指标配置仍是现有全局管理员配置，受 admin guard 和目标就绪检查约束，不因当前设备列表为空而隐藏已配置项。空设备 profile 下仍能管理全局配置，不能据此推断获得设备数据权限。

### 3.2 表计配置查询

`GET /api/v1/energy/metric-configs` 的 `meterId` 变为可省略，`groupKey` 继续可选。省略 `meterId` 时按当前登录用户角色的 `meterReadScopes` 查询其**全部获授权表计**，可叠加 `groupKey`；授权集合为空返回空 `data` 数组。提供合法 `meterId` 时继续执行现有 `allowed_meter` 检查，只返回该表计，提供无权限或显式空 `meterId` 保留原 403 行为；`groupKey` 为空仍保持原有不筛组选项，合法非空组按原规则筛选。返回仍是标准信封内的数组，每条保留完整 `meterId`、`groupKey`、`metricKey` 等现有字段及启用／停用项；单表计原有结果和按组、槽位的排序保持，多表计以表计、组、槽位及键稳定排序。不得根据前端传入的表计列表扩大范围，也不得以静默截断替代“全部”。

```text
GET /api/v1/energy/metric-configs
GET /api/v1/energy/metric-configs?groupKey=electricity
GET /api/v1/energy/metric-configs?meterId=meter1&groupKey=electricity
```

两个 GET 均继续由后端校验登录及 admin，机器 Bearer 不能替代人类管理权限。表计 POST/PATCH 必须明确具体表计，继续由后端按该表计授权并执行既有使用后保护。表计选项本身仅返回当前用户授权范围。表计与任务号无关的能耗样本及统计口径保持原合同。

## 4. 交付范围和边界

精确 r1 获批后，Development 可修改以下与需求直接相关的文件：

| 范围 | 允许文件与用途 |
| --- | --- |
| 后端 | `backend/app/equipment_observation/api/routes.py`、`backend/app/equipment_observation/services/configuration.py`，实现两项管理员 GET 的可选条件、稳定排序和现有授权。保留业务写入及机器端路由。 |
| 前端 | `frontend-js/src/app/equipment/views/observations/admin.vue`、`frontend-js/src/app/monitor/views/observations/admin.vue`、`frontend-js/src/app/monitor/components/observations/EnergyAdmin.vue` 中配置页所需改动；仅必要时调整对应 `frontend-js/src/app/{equipment,monitor}/api/observations.js`。共享 `EnergyAdmin.vue` 的 `kind=samples` 数据管理行为不得回归。 |
| 文案与说明 | `frontend-js/src/app/equipment/locales/{zh-CN,en-US}.json`、`frontend-js/src/app/monitor/locales/{zh-CN,en-US}.json`；双语操作手册 `docs/equipment-status-process-monitoring-guide{,.zh-CN}.md` 中与两配置页操作直接相关的说明。 |
| 测试 | `backend/tests/test_equipment_observation_r10_flow.py` 或新增 `backend/tests/test_observation_config_query.py`；`frontend-js/tests/module-registry/equipment-observation.test.mjs`、`equipment-observation-columns.test.mjs` 或新增 `observation-config-management.test.mjs`，仅覆盖本规格行为及受影响既有合同。必要的浏览器合成验证材料放任务独占临时目录，不作为唯一证据。 |
| 角色记录 | PM 只维护本 `spec.md`；获批后 Development、Verification 分别维护本任务 `tasks.md`、`checklist.md`。主会话机械同步根 `PLAN` 与 `plans/README` 双语索引。 |

本规格不要求数据库表、索引、迁移或业务数据变化；不修改 SMA、DAA、PLC、采集和机器上报合同，不调整实时卡片、过程曲线、数据管理或能耗统计业务规则。`EnergyAdmin.vue` 共享样本页时，只有配置视图重排及所必需的隔离逻辑在范围内。现有 `CODE_INDEX.md` 仅在实际新增源码文件或结构变化时按项目规则更新；如需要不在上述清单的文件、数据迁移或扩大权限，停止该部分并回 PM 修订。开发和验证使用隔离合成 fixture，不在真实／dev 数据库写入测试数据，不自动切换或重载用户服务；交付工作树若存在后端自动重载，应先核对影响并采用受控候选。生产部署、真实数据库迁移及其他未包含动作另依项目契约处理。

## 5. 验收标准

| 编号 | 可观察的通过条件 |
| --- | --- |
| AC01 双卡片 | 两个原菜单路径分别出现上方类别选择和下方当前设置；设备四类、过程两类均可切换，下卡标题、右上操作、筛选区和表格对应当前类别。原路由、权限、主题和中英文可用；桌面和窄屏无重叠、不可达按钮或空白页。 |
| AC02 筛选与重置 | 每类默认全部，按 §2 字段单项和组合查询、空值及中英文关键词匹配正确；重置恢复全部，切换类别和刷新按规定处理。无配置、无匹配、加载和失败状态区分，不隐瞒禁用记录或截断数据。 |
| AC03 槽位兼容 | 合成夹具至少含两个组、实时和历史、已启用／停用和未使用绑定。四种参数组合返回正确的完整行集及身份，`remaining` 在精确分区保持数值、其余为 null；空值和非法 target 依合同拒绝。现有新增、启停和精确查询不回归，首次使用时间含真实值与空值。 |
| AC04 表计权限 | 合成至少三个表计，当前 admin 只授权其中两个。默认全量与组筛选只返回两个授权表计的相关行，零授权返回空数组；显式无权或空表计拒绝，单表计精确结果与旧合同相同。非 admin 和机器凭据不能读取配置。新增显式选表计，编辑与写入按当前行精确身份授权，不可误改另一表计。 |
| AC05 并发交互与既有功能 | 模拟查询慢返回、快速筛选／重置／切换、操作弹窗期间选择变化和保存回执乱序；错误结果不能覆盖当前表或指向其他配置。原区域、指标、卡片、曲线和表计表单字段及校验、槽位启停、曲线／卡片指标、已使用绑定保护不回归；能耗样本数据管理保持原行为。 |
| AC06 列宽、时间与文案 | 各表普通列拖拽、最小宽、持久化和当前表独立重置通过；筛选／刷新／切页后的列宽符合项目规则。`firstUsedAt` 以首次使用时间显示并按上海时区到秒，空值为缺失。中英文文案对称，单位和稳定键不被翻译。 |
| AC07 验证与范围 | 项目 `uv`／`pnpm` 锁定工具链下完成有意义的隔离后端 HTTP 与前端交互回归、模块检查及前端构建；用真实页面交互核对两页默认、筛选、重置与编辑身份，记录夹具、实际命令、结果和环境限制。检查双语文档链接和本规格范围，无真实数据／服务副作用。Development 自检与 fresh-context Verification 分开记录。 |

## 6. 实施和风险

建议先补足两类管理员 GET 的可选参数、授权集合和原精确请求回归，再接两页布局及筛选，最后核验现有配置和双语手册。必须从当前正式工作树确认并发修改，不能覆盖其他任务；交付对象和验证对象须一致。真实后端使用热重载时，不得以隔离副本的验证替代正式源码交付，也不得擅自切换运行中的用户服务。若运行入口与源码整合有冲突，应保留证据并说明需要的明确操作。

风险包括全量查询量随配置增长、表计权限漏过滤、无单一分区时误算容量，以及共享能耗组件影响数据管理。通过完整结果、后台表计作用域、`remaining: null`、隔离测试和旧调用回归控制；不引入数据库结构或权限配置更改。后续如有分页、跨用户配置管理或大规模性能需求，应另定范围。

Development 遵循 `frontend-ui`、`i18n-workflow`、`backend-arch` 及适用的 `code-document-indexer`，使用项目 `pnpm` 和 `uv`。`qa_passed` 不代表 Human Owner 最终验收。

## 7. 修订与批准

| Revision | 状态 | 记录 |
| --- | --- | --- |
| r1 | `draft` | 根据两版交互预览，合并设备状态与过程监控配置管理调整；待 Human Owner 审阅。 |

建议批准用语：

> 批准 ARCH-OBS-004 r1，按 spec 实施并进行独立验证。设备状态和过程监控配置管理采用双卡片，槽位与表计指标默认显示授权范围内全部，支持筛选和重置，保留现有数据及精确查询行为。

批准前本任务只形成 PM 规格；不创建 Development 或 Verification 记录，不改实现、配置、数据库或运行服务。

### r1 Human Owner 批准与交接

Human Owner 对精确 `ARCH-OBS-004 r1` 范围和独立验证作出明确批准，原话为：

> 批准 ARCH-OBS-004 r1，按 spec 实施并进行独立验证。两页按预览做双卡片，槽位和表计指标默认显示权限范围内的全部，支持筛选和重置。做完告诉我怎么验收。

批准前规格 SHA-256 为 `8b82a685468cf12ba21e03c302f00f6517c267b5da3e42a164bb88eaa5ded1e5`。上方 `draft` 和批准前限制保留为当时的历史状态；本记录及文件头 `owner_approved` 表示 r1 已获范围批准，不代表实施、独立 QA 或 Human Owner 最终验收已经完成。r1 的范围、验收、文件清单和约束不变。

实际命名 Development 按本规格实施并在 `tasks.md` 记录自检与 `developer_handoff`，随后由 fresh-context 命名 Verification 独立核验并记录 `checklist.md`，再向 Human Owner 说明验收方法。若发生范围或风险实质变化，按项目工作流返回 PM。
