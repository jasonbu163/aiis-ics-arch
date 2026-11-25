Task ID: ARCH-OBS-007
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r1 A，交 Development 按 STD 实施；B 合同及开发仍待批准
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 能耗管理页面归并与独立登记来源写入规划
Owner: Core 能耗管理
Acceptance Chain Reference: 精确范围批准 → Development handoff → fresh-context Verification → Human Owner 最终验收
Related Task: ARCH-OBS-001、ARCH-OBS-003、ARCH-OBS-004、ARCH-OBS-005、ARCH-OBS-006、ARCH-BE-004

# 能耗管理页面归并与登记写入 · r1

## 1. 目标和本次批准边界

把现有能耗统计、单价、样本和指标配置集中到「能耗管理」。在独立的能耗域规划写入登记，使已登记来源可按通用观测报文格式上报能耗。管理员仍通过登录界面维护配置和查询。页面设计采用本规格 §3 和 §4，数据及接口边界见 §5 和 §6。

本稿分两部分：

- **A：页面归并与既有功能迁移**。§3、§4、§7.1 和 §8.1 给出可独立实施、检查与交接的具体范围。A 保留当前后端合同，Human Owner 已批准精确 r1 A 按 STD 实施。
- **B：能耗来源登记及免 Token 写入**。§5、§6、§7.2 和 §8.2 记录已确认的业务方向及待明确合同。能耗专属字段与映射尚待确定，B 当前为设计范围，须先形成明确合同并取得对应范围批准后才能实施。A 的完成不代表 B 已实现。

Human Owner 已批准 r1 A 的开发，B 的精确实现合同尚未批准。PM 不创建 Development 的 `tasks.md` 或 Verification 的 `checklist.md`。r1 A 按 STD 执行 Development、fresh-context Verification 和 Human Owner 最终验收。

## 2. 当前基线

1. 前端过程监控的能耗统计路径为 `/monitor/consumption`，页面授权键 `monitor.energy`。过程监控配置管理包含「曲线设置／表计指标配置」，数据管理包含「过程样本／能耗样本」。前端辅助管理的能耗单价路径为 `/auxiliary/price`，页面授权键 `auxiliary.price`。现有注册和守卫见 [过程 manifest](../../frontend-js/src/app/monitor/manifest.js)、[辅助 manifest](../../frontend-js/src/app/auxiliary/manifest.js) 和 [页面授权](../../frontend-js/src/config/pageAccess.js)。
2. 设备状态与过程监控已有来源登记，登记表单为来源标识、可选名称及启用状态。当前无 Token 的 `POST /api/v1/integration/observations` 使用 `sourceKey`、`target`、`taskNo`、`observedAt`、`items`，只接收 `latest` / `history`，见 [写入登记合同](../../contracts/published/http-api/observation-write-sources-v1/README.zh-CN.md)。其业务数据和回执归设备／过程域。
3. 能耗当前按表计、采样组、采样时间和指标写入 `energy_consumption_main`，指标定义在 `energy_metric_configs`，回执在 `energy_ingest_receipts`。现有 `/api/v1/integration/energy/samples` 属于 Bearer v2 合同，能耗样本不依赖任务号。单价由独立 `energy` 后端模块维护，小时价格及历史合同见 [能耗合同](../../contracts/published/http-api/equipment-observation-v2/README.zh-CN.md) 和 [单价模块](../../backend/app/energy/README.zh-CN.md)。
4. `ARCH-OBS-004`、`ARCH-OBS-005` 当前索引为 `qa_passed`，Human Owner 最终验收待完成；`ARCH-OBS-006 r2` 已 `owner_accepted`。本任务沿用当前工作树实际实现和合同，不改变既有任务验收状态。开发前重新核对活动工作树，避免覆盖并行改动。

## 3. A · 菜单和页面

### 3.1 一级菜单

新增「能耗管理」，包含「能耗统计」「能耗单价」「数据管理」「配置管理」四个入口。菜单图标、主题和排序遵循现有 manifest 与项目设计基线。新增模块拥有中英文导航与页面文案，沿用 Registry 装配和现有访问判断，不通过新模块自动授予角色或 API 权限。

沿用两个现有页面的路径、路由名和 pageId，只改变菜单归属及页面标题上下文：

| 页面 | 保留路径 | 保留 pageId | 访问依据 |
| --- | --- | --- | --- |
| 能耗统计 | `/monitor/consumption` | `monitor.energy` | 现有页面授权及后端能耗读取权限、表计范围 |
| 能耗单价 | `/auxiliary/price` | `auxiliary.price` | 现有页面授权及独立单价 API 权限 |
| 数据管理 | `/energy/observations/data` | `energy.observations.data` | 管理员页面 |
| 配置管理 | `/energy/observations/admin` | `energy.observations.admin` | 管理员页面 |

两个旧路径直接打开对应的新菜单归属页面。已退役的 `/monitor/energy` 继续退役。原 `/monitor/observations/admin`、`/monitor/observations/data` 继续指向过程监控相应页面。能耗数据与配置的路由名分别为 `EnergyObservationData`、`EnergyObservationAdmin`，均为管理员页面，与原能耗管理操作的管理员边界一致。新路由、菜单组、叶子路由、标题和 locale 按 `src/app/README.*` 的 manifest 合同注册；新 `energy` 模块不能要求管理员修改既有 `monitor.energy` / `auxiliary.price` 角色配置。

当用户只持其中一个旧页面授权时，只显示并允许进入该页面；未获授权的页面仍被守卫拒绝。新增能耗管理管理员页不会因为已有统计或单价授权而对普通用户开放。已登录用户通过现有 request 层携带用户 Bearer，后端权限和表计范围继续独立生效。

### 3.2 能耗统计

迁移既有统计能力，主卡从上到下分为卡头、筛选区和结果区，样式对齐温度曲线页。卡头包含页面标题及刷新；筛选项为表计、采样组、指标和上海时间范围，提供查询及恢复默认。结果区继续显示最新读数、选中指标的统计结果及当前曲线。沿用现有表计定义、样本和统计接口，不复制计算结果到前端。

累计、时段增量与瞬时指标的数值、完整／不完整原因和单位沿用现有能耗统计合同。真实零值、缺失值、异常、无数据、无可访问表计、请求失败、切换筛选及乱序响应均保持可辨认。查询、刷新、恢复默认、时间输入和曲线交互需使用真实接口或验证夹具数据。

### 3.3 能耗单价

迁移现有单价页。卡头提供「新增单价」。当前电能、氢气、氩气价格各放一张等宽卡，三卡同排时第一张左边缘、第三张右边缘与下方独立「历史记录」卡对齐。历史卡包含现有按日历史表及记录信息。窄屏允许卡片依次换行或纵向排列，卡片及表格保持可读。

继续使用现价、历史和整组小时价格写入接口。保留现有三种能源的单位、备注、记录时间、上海小时归属、同小时整组覆盖、输入校验、失败提示与读／写权限。当前价格和历史来自真实 API，不能将原型数值带入交付页面。

### 3.4 数据管理与配置管理

- 「数据管理」显示现有能耗样本，沿用表计、采样组筛选、分页、样本详情、备注和异常／已复核标记。样本值及采集时间保留现有含义，原始值不能由页面修改。
- 「配置管理」迁入现有表计指标配置，沿用表计、采样组、关键词筛选以及新增／编辑表单。现有名称、槽位、物理量、计量方式、单位、小数位、启停、列表显示／顺序及累计规则保持可用。
- A 阶段在配置管理保留紧凑类别上卡及「表计指标配置」选项，下面展示真实配置表；B 实现后在同一上卡添加「写入登记」。A 阶段不提供模拟的可保存登记数据或连接不存在接口的登记入口。
- 两个页面复用现有公共表格、列宽工具和弹窗。业务数据列可拖拽，横向溢出可滚动，列宽按应用／表／稳定字段在本机隔离并跨刷新恢复，每张表提供「重置列宽」，提示为「恢复默认列宽」。已有可兼容的列宽偏好继续读取；不能兼容的字段回退默认值。

### 3.5 过程监控迁出后的布局

「过程监控 → 配置管理」保留上卡「曲线与历史管理」，上卡只显示「曲线设置」；下卡沿用现有曲线配置操作和筛选。「过程监控 → 数据管理」保留上卡「数据管理」，上卡只显示「过程样本」；下卡继续显示过程样本。

温度、传动、清洗的曲线及过程样本与设备状态卡片继续使用既有查询与配置。抽取共用组件时，不能改变其他调用方的曲线时间定位、缺测、零值、显示或权限。

## 4. A · 界面参考及适配

当前本地审阅原型为 [能耗配置与登记](../../work/energy-registration-review.html)，单价卡位置以 [单价布局](../../work/energy-price-cards-preview.html) 为参照。它们属于本地交互示意，含示例数据；实现和验收以本规格、项目现有组件及真实 API 合同为准。原型中的 B 登记界面只在 B 范围实现后成为真实能力。

桌面、窄屏、中英文及明暗主题遵循 [前端设计基线](../../frontend-js/DESIGN.zh-CN.md)。卡头、按钮、表格和弹窗使用项目已有风格，标题和操作随换行可达。模块及现有依赖的 locale 组织须确保能耗模块启用时其页面文案可解析；各可选模块的禁用不能造成活动路由、locale 或注册冲突。项目共享曲线组件被能耗和过程共用时，分别验证两个调用路径。

## 5. B · 能耗登记的已确认方向

1. **独立领域**。能耗登记、写入、样本及回执属于能耗域。实时／过程可复用交互和通用字段格式，但不能共享同一来源登记状态，也不能建立能耗到实时／过程的外键、跨域表 JOIN 或检查另一域的 `taskNo` 是否存在。业务方需要组合信息时分别 GET，再在调用方业务逻辑处理。
2. **来源登记**。能耗「配置管理 → 写入登记」参照设备状态表格和弹窗，展示来源标识、名称、状态和操作，支持新增、编辑、启停、删除、关键词查询与重置。新增只填 `sourceKey`、可选名称和启用状态。来源不区分 SMA 或第三方，也不为每个来源登记设备、表计、采样组、指标授权、机器 producer 或 Token。表计与指标使用能耗配置管理已有能力维护，表计及登录用户可读范围的现有运行配置继续按现状管理。
3. **生命周期**。参考现有登记的标识校验、大小写、停用、逻辑删除、保留历史、不可重新占用已删除标识，以及并发写入与启停／删除的事务语义。来源已登记并启用后可以发送，来源状态变化不会删除既有样本和回执。
4. **鉴权**。界面查询、指标配置、登记管理和单价管理使用登录用户 Bearer 与相应权限。登记来源的能耗机器 POST 不要求也不依赖 Authorization 头。`sourceKey` 是来源标识，当前无 Token 接入适用于访问受控的内网。原 `/integration/energy/samples` Bearer v2 合同及其发送方权限、事件身份、回执与旧数据保持可用。
5. **通用格式**。能耗入口采用独立端点，报文通用字段格式参照当前观测 POST 的 `sourceKey`、`target`、`observedAt`、`items`。当前能耗样本没有 `taskNo`，B 首批不引入该字段。能耗目标取值、表计／采样组在 `items` 中的表达、区间时间与质量语义、请求／响应和去重身份须在精确合同中明确后实施。先前会话中提出的 `eventId` 加 `data` 新登记 POST 草案已撤回。现有 Bearer v2 的 `eventId` / `data` 保持现有合同。
6. **复用现有能耗逻辑**。新来源样本应进入现有能耗样本和能耗回执体系，并复用指标类型、槽位、计量方式、数据质量、原始时间、完整性和统计规则。写入与回执须在一个事务内，重试不能造成重复样本或半写入。具体身份与冲突规则由精确合同确定。
7. **旧链路保护**。新登记、身份和去重方式不得与现有 Bearer 生产者碰撞，不改写旧样本、回执和重试结果。涉及 schema 时通过显式 Alembic 后继与目标 revision guard 设计，并对设备、过程、旧能耗路径做迁移前后回归。真实数据库采用与服务切换另按项目契约办理。

## 6. B · 需定稿的合同

以下内容需由 PM 在后续 Revision 中形成可审阅、可测试的精确请求、响应及错误约定后交 Human Owner 范围批准。该清单用于确保沿用通用格式时能落到现有能耗计算，不预先指定具体 JSON 名称或路径：

1. 能耗独立 POST 的精确路径、`target` 值、必填／可选字段及 `items` 如何定位表计、采样组和已启用指标。确认一次请求承载一组或多组的边界。
2. 累计、时段增量和瞬时指标的数据质量及真实时间语义，尤其是时段增量的起止边界如何表达。现有统计对质量和覆盖范围有要求，不能把缺失质量、缺失边界或缺口当作合格用量，也不能以接收时刻冒充采集时刻。
3. 不由发送方提交 v2 `eventId` 时，样本重试身份、同身份异文冲突、同一时刻合法多次采样、提交结果未知后的重试、回执内容和并发一致性。不得导致两个合法样本被静默合并。
4. 新登记表或等效独立持久化结构、内部来源身份与旧 producer 隔离、与 `energy_ingest_receipts` / `energy_consumption_main` 的同域衔接、Alembic revision 与 guard、登录用户对旧样本和新样本的可见范围。
5. 登记管理 API、无 Token POST 的响应和错误、OpenAPI 及中文／英文使用说明。真实运行需要的全局目标配置与表计配置必须说清楚，登记来源本身不要求配置 Bearer 或 profile producer。
6. 核对业务方独立 GET 能耗的读取场景。现有用户能耗 GET 使用登录权限；如需提供第三方无 Token 的能耗 GET，在精确合同中定义查询范围、响应和可见性，其查询只涉及能耗域，不关联实时／过程表。

## 7. 允许改动范围

### 7.1 A · 已批准的源码与文档范围

- `frontend-js/src/app/energy/` 下与四个能耗入口、双语 locale、业务 API facade 和必要组件有关的文件。
- `frontend-js/src/app/monitor/manifest.js`、`api/observations.js`、`views/observations/{admin,data,energy}.vue`、`components/observations/{EnergyAdmin,CurveChart,EmptyAxes}.vue` 与 `locales/{zh-CN,en-US}.json` 中与迁出和安全复用直接相关的改动。
- `frontend-js/src/app/auxiliary/manifest.js`、`views/price/index.vue`、`api/index.js` 和 `locales/{zh-CN,en-US}.json` 中与单价迁出及复用直接相关的改动。
- `frontend-js/tests/module-registry/` 下页面授权、Registry、能耗／过程组件及价格页面的受影响回归测试，必要时新增本任务聚焦测试。
- `frontend-js/README.md`、`frontend-js/README.zh-CN.md`、`docs/equipment-status-process-monitoring.md`、`docs/equipment-status-process-monitoring.zh-CN.md`、`docs/equipment-status-process-monitoring-guide.md`、`docs/equipment-status-process-monitoring-guide.zh-CN.md` 中受本迁移影响的现行入口和使用说明。实际新增／移动代码结构时按项目规则更新 `CODE_INDEX.md`。协调者机械维护根 PLAN 和 plans 索引。
- 本任务 Development 的 `tasks.md` 和 Verification 的 `checklist.md` 分别由对应角色在各自 gate 创建。A 不修改后端代码、公开机器接口、数据库或其他应用源码。

如实际实施需要本清单以外的改动，记录具体原因和影响并返回 PM 确定范围。实现尽量复用已有组件和 API，不为了目录迁移重写业务计算或增加新依赖。

### 7.2 B · 待定实现范围

预计涉及能耗登记前端、`backend/app/equipment_observation/` 内的登记、路由、模型、服务、guard 与测试、显式 Alembic 后继，以及 `contracts/` 和 `docs/` 中的新合同。具体文件 allowlist、接口路径、schema 和验收向量在 §6 定稿后进入对应 Revision。本稿不构成对这些写入的开发授权。

## 8. 验收标准

### 8.1 A · 可独立验收

| ID | 可验证结果 |
| --- | --- |
| A01 菜单与权限 | 新一级菜单有四个对应页面。旧统计和价格 URL、路由名及 pageId 保持可用；只授予统计或只授予价格的 supervisor/operator 各自只能看见及访问获授页面。两项管理页仅 admin 可访问，页面授权不增加后端权限或表计范围。未知、未登录及无权限用户被现有守卫拒绝。 |
| A02 统计 | 使用隔离 fixture 和真实页面请求，切换表计／组／指标／时间并查询，结果、单位、完整性原因及曲线与既有 API 一致；检查 0、缺测、错误、并发切换与恢复默认。样式为卡头／筛选／结果三栏。 |
| A03 单价 | 三张等宽价格卡在桌面左右与历史卡对齐，历史被独立卡片包裹；窄屏可用。用夹具验证现价、选日历史、写入、同小时覆盖、时间与单位、输入错误和读写权限。 |
| A04 数据与配置 | 能耗样本可按现有方式筛选、分页、查看详情和保存备注／复核；表计指标配置可查询、新增和编辑并保留各字段与显示顺序；调用既有后台 API，A 不出现虚假登记入口。 |
| A05 过程与设备回归 | 两张过程管理上卡存在且各只有对应过程选项；曲线配置和过程样本仍可用。温度、传动、清洗曲线及设备实时卡片的既有任务定位、缺测和零值行为回归通过。 |
| A06 样式与工程 | 中英文键对称；明暗和桌面／窄屏可操作；普通列拖拽、刷新恢复及重置各表独立。`pnpm check:modules`、受影响模块回归和构建通过；用合成授权配置测试独立可选模块装配，活动能耗页面的文案及依赖可解析。 |
| A07 数据与兼容 | 原能耗样本、指标配置、单价、API 路径及读取语义不因 A 改变。对旧统计／价格页面地址、原角色授权配置及旧过程页地址执行路由、守卫和对应 API 回归；无真实数据库写入。 |

### 8.2 B · 合同定稿后形成精确验收向量

最低验收范围包括：管理员 Bearer 登记管理；完全省略 Authorization 的已启用登记来源写入；未知、停用及删除来源拒绝；配置字段非法拒绝；合法样本、对应回执、重试与并发一致；数据管理及统计按当前计量规则读取结果；不传 Token 的第三方入口与需要 Bearer 的前端入口分别验证；旧 Bearer 能耗 v2、设备状态、过程监控和旧数据回归。精确断言及样本向量随 §6 合同定稿，不能以本段占位认定 B 已通过。

## 9. 风险、验证和回退

- **授权与导航**。用户角色配置使用稳定 pageId，删除或重命名会使环境校验失败。A 保留两个已有 pageId 和原 URL，新菜单组合不改变后端权限。
- **共享组件**。过程曲线与能耗统计共用曲线组件；能耗配置和样本共用现有组件。修改前检查所有调用方，并以独立页面回归覆盖。
- **本地时间与单价**。统计按上海时间查询。价格沿用已验收小时合同，页面调整不能用刷新时间冒充价格事件或修改时间，也不改变原价格字段存储口径。
- **登记去重与质量**。B 的能耗真实区间、质量与事件身份直接影响统计和数据一致性。§6 未定稿前不实施 B。仅凭已存在的来源标识无法证明发送方身份，免 Token 接入按用户确定的内网模式设计。
- **回退**。A 的可交付代码可通过回退本任务对应源码差异恢复原菜单和页面，旧路径与数据无需迁移。B 的 schema、历史和数据回退随精确合同及迁移方案确定；不能通过删除样本或回执掩盖兼容问题。
- **验证环境**。A 的构建、模块测试与浏览器交互采用合成授权和隔离数据，必要时写 `/private/tmp`。不触发真实数据库迁移、真实设备操作、部署、发布或实际环境配置变更。临时资源的归属、保留条件及回收由后续执行角色按 workflow 记录。

## 10. 排除项与角色交接

本任务不实现 SMA、DAA、CA 或第三方客户端，不创建能耗与设备／过程间的业务绑定，不建设费用计算、能耗自动分摊、生产报表或任务号关联能力。真实设备、PLC 联调、dev 数据库迁移和发布部署按各自明确授权处理。

A 的 Development 使用 `frontend-ui`、`i18n-workflow` 和 `code-document-indexer`；如需追查页面到接口的绑定，使用 `interface-lineage-audit`。B 后续涉及后端 API、模型和迁移时使用 `backend-arch`；其他 skill 按实际触达面确定。Development 完成自检后交 fresh-context Verification，QA 通过后由 Human Owner 最终验收。

## 11. 修订与批准记录

| 日期 | 修订 | 记录 |
| --- | --- | --- |
| 2026-11-23 | r1 draft | 用户授权起草规格。A 的开发批准、B 的精确合同及开发批准均待 Human Owner 确认。 |
| 2026-11-24（Asia/Shanghai） | r1 A owner_approved | Human Owner 原话：“批准 ARCH-OBS-007 r1 A，按 STD 启动 Development。” 本次批准仅覆盖 r1 A；B 的精确合同及开发仍待批准。 |
