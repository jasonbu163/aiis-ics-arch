Task ID: ARCH-ENERGY-001
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 ARCH-ENERGY-001 r2；交由 Development 按 STD 实施，交接后进入 fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 可配置能源单价及按项目小时维护
Owner: Core 能源单价
Acceptance Chain Reference: 精确范围批准 → Development handoff → fresh-context Verification → Human Owner 最终验收
Related Task: ARCH-BE-002、ARCH-BE-004、ARCH-OBS-007、ARCH-OBS-008

# 可配置能源单价 · r2

## 1. 目标与审阅边界

管理员可以自行维护单价项目，例如电能、工业用水、氢气、氩气或蒸汽。能耗单价页按启用项目生成现价卡片、录入字段和历史列，即使当前查询范围没有该项目的价格，也保留其历史列。一次可以填写一项或多项价格。2026-11-24 Human Owner 确认 [完整交互原型](../../work/energy-management-full-review.html)，并批准按 STD 起草独立规格。2026-11-25 Human Owner 确认 [v5 交互原型](../../work/energy-curves-pricing-review-v5.html)，授权修订单价规格。原型仅为本地审阅参考，实施以本规格为准，示例数据不得进入正式数据。

Human Owner 已批准 r2 范围与按 STD 启动 Development，包含本规格的数据迁移、单项更新及旧接口视图设计。允许编写迁移脚本并在隔离环境验收；本次不授权迁移真实或共享 dev 数据库、切换服务或部署。本任务使用 `backend-arch`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer`，并依 canonical workflow 执行 Development 与独立 Verification。

## 2. 当前事实

1. [现有单价页](../../frontend-js/src/app/energy/views/price.vue)的电、氢、氩项目固定；[后端价格模块](../../backend/app/energy/README.zh-CN.md)使用独立的 `energy-price-read`、`energy-price-manage` 权限。Web 请求使用登录用户 Bearer。
2. `energy_price_hours` 每小时一行，`POST /api/v1/energy` 要求三个价格并原子覆盖整组，保留同小时的 `id`、`hourStart`、`createdAt`。GET `/energy/current` 取不晚于现在的最新组，GET `/energy` 支持上海自然日和分页。备注、操作者及记录和实际修改时间已有明确语义。[已验收规格](../ARCH-BE-004-energy-price-hourly-history/spec.md)
3. `energy_price_hours` 的 `DATETIME(6)` 当前按 UTC 保存，API 输出 `+08:00`。旧追加表 `energy_prices` 独立保留。不得对来源时区不明的数据盲目转换。[历史与迁移说明](../../backend/app/energy/README.zh-CN.md)
4. [ARCH-OBS-007 r1 A](../ARCH-OBS-007-energy-management/checklist.md) 已验收能耗菜单和单价布局。能耗单价与表计采样、实时及过程数据独立。

## 3. 页面与项目配置

1. 「能耗管理 → 配置管理」上卡新增「单价项目配置」。项目表支持查询、新增、编辑、启用和停用，字段为稳定项目键 `itemKey`、中文名称、英文名称、计价单位、排序和启用状态。至少填写一个名称，另一语言可回退到已填写名称。项目键去首尾空白后非空且唯一，保存后不可变。项目已有价格时计价单位不可改，避免把历史金额解释为新单位；调整单位使用新项目。名称和顺序可改，停用后历史可查。
2. 初始化内置 `electric`、`hydrogen`、`argon`，名称和单位沿用现有电价及气价。新安装不生成价格。工业用水、蒸汽等由管理员新增，示例仅进入合成 fixture。
3. 能耗单价页根据启用项目同时生成现价卡片、录入字段和历史列。历史列对所有启用项目显示，即使项目从未录价、选定自然日没有其价格或该日无历史行。停用项目不再出现在现价卡及新增价格表单中，若查询范围内有其历史价格，则历史列仍显示，原历史值保留。列以稳定 `itemKey` 标识，按配置排序；项目少量时卡片同排等宽，项目增多时换行，卡片区两侧与独立历史卡对齐。历史行仍只反映该查询范围内实际有价格更新的小时，缺值显示 `—`，真实零显示为 `0`，空日表体显示空状态。表格继续支持列宽拖拽、本机记忆、重置和横向滚动。
4. 新增价格弹窗按启用项目生成字段，至少填写一项；本次未填写的项目保持同小时原值，允许单价为零。每项价格可选备注，沿用原总备注。时间清空时由服务端取一次当前时间；成功后切到实际记录日并独立刷新当前价和历史。失败、保存中及请求竞态沿用现有页面交互。项目新增／编辑弹窗按「项目定义」「显示设置」分组，价格录入弹窗按「记录信息」「本次单价」分组；紧凑布局、表格和按钮优先复用实时／过程现有组件。所有调整的弹窗满足根 AGENTS 第 9 节，遮罩关闭等同取消。
5. 当前价对每个启用项目分别取其不晚于查询时刻的最近记录，历史补录不因为更新时刻较新而抢占现价。查询不到的项目保持缺失。按日历史只显示该上海自然日实际有价格更新的小时，每一单元格显示该项目在该小时内的记录；当小时未写入该项目显示 `—`，不把现价填成历史值。小时归属、实际记录时间及实际修改时间分别表达，不推断分钟级价格生效时间。每项价格的记录时间、操作者和备注可在历史详情或等效可访问交互中查看。

## 4. 数据及时间合同

新增 `energy_price_items` 存项目定义；新增 `energy_price_item_hours` 存每项目、每上海民用小时的价格，`(item_key, hour_start)` 唯一。每项保存价格、项目备注、原始 `observed_at`、操作者、创建和实际更新时间。价格使用精确十进制，合法零必须保留；输入为有限非负数，超出实际可存精度明确提示，不能静默舍入。原三项的新旧写入继续使用当前 `Numeric(10,4)` 的范围和精度，使旧接口可无损往返。自定义项目的可存范围和精度不得低于原三项。

新业务时间使用 `+08:00` 口径的 `DATETIME(6)`，API 返回 `+08:00`；服务端只在接入边界转换一次。`observedAt`、`hourStart`、`createdAt`、`updatedAt` 各自保留事实含义。复用已验收的 `Asia/Shanghai` 小时归桶与历史边界处理，包括历史重复小时；沿用原 POST 对未来记录时间的拒绝。旧表 UTC 只作为待转换的历史来源，确认原始时区后转换，不向同一字段混写 UTC 与上海时间。

具体转换复用现有 `canonical_hour_start`：先按 IANA `Asia/Shanghai` 取得民用小时，回拨重复小时使用 `fold=0`，计算该小时的规范 UTC 瞬间；再把此 UTC 瞬间转换为固定 `+08:00`，剥离偏移后写入新表 `hour_start`。`observed_at`、`created_at`、`updated_at` 也由各自的 UTC 瞬间转换到固定 `+08:00` 后保存。按日筛选先用真实 `Asia/Shanghai` 计算自然日两个 UTC 边界，再转换到固定 `+08:00` 与数据库比较；不得直接把含夏令时歧义的民用墙钟时间写入新字段。旧 API 输出保持同一瞬间及 `+08:00`。例如现有 1991-09-15 的两个 `01:30` 分别是 `+09:00` 和 `+08:00`，共享规范小时 UTC `1991-09-14 16:00`，新表小时值为 `1991-09-15 00:00:00`，事件时刻分别为 `00:30` 和 `01:30`。参照现有 [重复小时测试](../../backend/tests/test_energy_price_service.py)。

对同一项目、同一小时，最后一次成功写入该项目获胜，保留该项目小时记录的身份及创建时间。一次写入多个项目在同一事务内提交；两个项目并发写入不能互相覆盖，某项校验失败整次操作不产生部分记录。对可表示的价格和时间保留原貌，包括旧备注及精度。校验限于身份权限、项目存在及启用、必要字段、数值精度和可表示的时间，不按能源种类设置额外业务规则。

## 5. API 合同

以下均以 `/api/v1` 为前缀，沿用项目响应信封。价格读取使用 `energy-price-read`，价格写入使用 `energy-price-manage`；项目增改另通过现有 admin 校验。页面可见与后台权限分别判断。项目列表供有价格读取权限的已登录用户查询，含状态以便读取历史项目。

| 方法和路径 | 行为 |
| --- | --- |
| `GET /energy/pricing/items` | 返回项目键、双语名称、单位、排序、启用状态。 |
| `POST /energy/pricing/items` | 管理员新增项目，返回项目。 |
| `PATCH /energy/pricing/items/{itemKey}` | 管理员修改名称、排序、启停及尚未使用项目的单位，项目键不可变。 |
| `GET /energy/pricing/current` | 返回启用项目各自最新的价格、单位、记录时间和备注，无价格为 `null`。 |
| `GET /energy/pricing/hours?date=YYYY-MM-DD&page=1&pageSize=24` | 返回该上海自然日按小时降序聚合的实际更新，包含各项实际值、行元数据，以及 `items,total,page,pageSize,columns`。`columns` 独立于分页，包含全部启用项目和查询范围内有价格的停用项目，即使当前页或整个查询无记录仍返回启用项目。不传 date 可分页读取全历史，查询范围为全部历史。 |
| `POST /energy/pricing/hours` | 以一个 `observedAt` 提交一个或多个项目，原子更新这些项目的同小时价格。 |

POST 的 `items` 为 `itemKey → {price, remark?}`，可选顶层 `remark` 对应旧整组备注。覆盖已有项目时省略其 `remark` 则保留该项目同小时的备注，显式传 null 或空串则清除；新项目的备注默认 null。省略顶层 `remark` 时保留已有兼容小时的总备注，显式 null 或空串清除。旧 `POST /energy` 继续按原合同整组处理备注。示例表示仅更新工业用水，本小时其余项目不改动：

```json
{
  "observedAt": "2026-11-24T12:00:00+08:00",
  "items": {
    "water": { "price": 3.6, "remark": "" }
  }
}
```

项目名称按用户当前语言显示，无法提供对应语言时显示另一名称。历史响应携带所属项目键、名称、单位、价格、备注、操作者及时间，包含有历史数据的停用项目。非法或缺失的必要字段按现有响应约定返回 422，无权限为 401/403，重复项目键为冲突。`observedAt` 的显式字符串沿用旧接口带偏移、可持久化的语法，省略/null 使用服务端捕获时间。

`GET /energy/pricing/current` 的 `data` 是按项目排序的数组，每项包含 `itemKey`、`nameZh`、`nameEn`、`unit`、`price`、`remark`、`observedAt`、`updatedAt` 和 `operator`，没有价格时后五项为 null。`GET /energy/pricing/hours` 的 `data` 包含 `columns` 和分页信息 `items,total,page,pageSize`。`columns` 为按排序及稳定项目键排列的项目定义数组，每项含 `itemKey`、`nameZh`、`nameEn`、`unit`、`sortOrder`、`enabled`，集合为所有启用项目加当前查询范围内有实际价格的停用项目，去重后确定；此集合不受页码影响。分页 `items` 每行有 `hourStart`、小时总 `remark`，以及以项目键为 key 的 `values` 对象。每个实际发生过更新的值含 `price`、`remark`、`observedAt`、`updatedAt` 和 `operator`；未在该小时发生更新的项目不出现，前端显示 `—`。查询范围没有任何价格或页码越界时，`items` 为空，`columns` 仍含所有启用项目，`total` 为查询范围实际记录小时数。新 POST 的响应返回实际归属 `hourStart`、保存的各项目及其记录时间和实际更新时间，不把未提交项目伪装为本次写入。

例如启用水价后，所选日没有任何价格记录时仍返回项目列，供页面绘制表头与空状态：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "columns": [
      {"itemKey": "water", "nameZh": "工业用水", "nameEn": "Industrial water", "unit": "元/m³", "sortOrder": 20, "enabled": true}
    ],
    "items": [],
    "total": 0,
    "page": 1,
    "pageSize": 24
  }
}
```

## 6. 旧接口兼容与单一价格事实

本节兼容选择已纳入 Human Owner 批准的 r2 范围。切换成功后，新旧 HTTP 路由都由同一份 `energy_price_item_hours` 价格事实提供数据。旧 `energy_price_hours` 和 `energy_prices` 保留作为迁移前历史来源，新写入不再将它们作为另一套价格事实。新增 `energy_price_hour_meta` 保存每个有价格写入小时的总备注，以及旧三价整组投影所需的稳定 `id`、小时、记录时间、创建／修改时间、operator 和是否曾写入内置项目的标记。自定义项目先写入的小时也可以保存总备注，首次写入内置项目时记录其旧接口兼容时间和操作者。元数据不复制价格值。

1. 旧 `POST /energy` 仍要求电、氢、氩三价，沿用权限、数值与时间合同，在一个事务内写入三项对应小时记录并更新兼容小时元数据。返回原 `HourlyPriceRecord` 字段与 JSON number 格式。
2. 新 POST 更新三项中的任一项时，同时为该小时创建或更新兼容小时元数据。该小时已有旧接口兼容记录时保留其 `id`、`hourStart` 和 `createdAt`，`observedAt` 与 operator 记录本次成功写入，`updatedAt` 表示本次实际修改；省略总备注时原总备注保留。新增小时元数据分配稳定 ID，不能与已导入的旧 ID 冲突。只更新自定义项目时可保存本小时元数据，但不会产生可见的三价兼容记录，也不会改变已有三价价格和时间。若显式提交总备注且该小时已有三价兼容记录，旧 GET 同步显示这次对总备注的修改及实际修改时间。
3. 对每个兼容小时 H，旧 GET 从三项价格各自 **H 或更早小时**的最近记录组合一组。若 H 当小时写入某项则取该小时记录，未写入则取先前最近值；某项在 H 之前从未有值时该兼容小时暂不返回。后续补入历史可使该小时成为完整组，原有兼容小时 ID 保持稳定。已有旧行本身三项齐全，因此逐项导入后其旧响应、备注和身份可逐行对照。按小时补录只影响需要继承该值的后续兼容视图，不覆盖后续小时已经明确写入的项目。兼容视图的 `operator`、`observedAt` 表示该小时最近一次直接写入，`updatedAt` 取小时元数据与构成当前三价的实际记录的最晚修改时间，确保较早小时被修正后，依赖它的视图显示真实修改时间。
4. 旧 `GET /energy/current` 仍按完整兼容小时的 `observedAt <= now`、`observedAt DESC, id DESC` 返回一组或 null。旧 `GET /energy` 仍按原日期、排序和分页合同返回完整组。全新空库先仅录入一项时，新 current 显示该项，旧 current 返回 null；三个内置项均有适用价格后，旧接口返回完整组。未启用的内置项仍保留在旧协议投影中，旧 POST 沿用原三项合同，状态控制新页面显示及新接口选项。
5. 新旧 POST 并发及历史补录均以数据库事务一致的先后顺序生效。旧请求整组三项不会被另一请求拼成部分成功，新请求只更新所提交项目。兼容 GET 在一致快照下构造完整组。当前价和旧接口的 `updatedAt` 不使用界面刷新时刻。

例如，11 点旧接口保存电 `0.80`、氢 `3.00`、氩 `4.00`。12 点新接口只更新电为 `0.90` 后，新历史 12 点只显示电的实际更新，旧 current 的 12 点完整投影为电 `0.90`、氢 `3.00`、氩 `4.00`。11 点原记录及其 ID 保持原样。

## 7. 迁移、采用与回退

通过显式 Alembic 后继创建项目、小时价格及兼容元数据结构。现有小时行逐项导入三项，价格、备注、操作者和时间保留，兼容小时 ID 与原 `energy_price_hours.id` 相同；后续新 ID 从不冲突的空间分配。旧小时记录依据已验收合同的 UTC 来源转换为上海本地 DATETIME，API 返回的时间瞬间和 `+08:00` 表达保持一致。`energy_prices` 继续作为历史表独立保留，本任务不把其未归并旧行静默混入当前价格。

在空库和含非空小时历史的隔离 MySQL 上实施迁移，逐行核对原小时 ID、三项数值、备注、actor、时间、查询结果及行数。切换前完成写入窗口内的最终对账，使旧 API 和新 API 切换到同一权威价格数据；中断或失败可重新检查并安全恢复，不能因 MySQL DDL 部分提交而误报采用完成。实际数据库、备份、具体目标、写入窗口、迁移与服务切换由 Human Owner 另行批准，本规格的开发批准不等于真实库操作批准。

回退时先保护切换后的新数据并停止写入，评估把当前可表示的三价小时重新投影到旧格式及核对 ID。自定义项目和单项价格历史在旧三列格式中无法完整表达，须另行备份和处理。禁止直接回切旧程序后继续写原表并宣称新记录已被保留。回退步骤在隔离 fixture 验证并交付说明。

全库 Alembic revision 的无关前进不能让本模块日常读写拒绝。价格迁移的隔离验证检查设备实时、过程曲线和能耗样本读取回归。实际采用前核对目标环境的观测运行兼容状态，避免无关迁移再次触发 503。此检查不要求本任务依赖能耗登记 B 的实现。[现有观测兼容任务](../ARCH-OBS-008-runtime-compatibility/spec.md)

## 8. 实现范围

- `backend/app/energy/` 中项目定义、价格模型、schema、API、Service、CRUD、模块注册、日志和双语 README；`backend/alembic/versions/` 中本任务显式后继；必要的隔离维护入口仅用于本任务迁移对账和恢复。
- `frontend-js/src/app/energy/` 中配置类别、项目设置、单价页、价格 API facade、双语 locale 与复用组件。`frontend-js/src/app/auxiliary/api/index.js` 仅作现有单价调用迁移所需调整。与能耗统计空态和登记写入并行任务共享文件时，基于当前树合并，不能重写对方改动。
- `backend/tests/`、`backend/tests_mysql/` 以及 `frontend-js/tests/module-registry/` 中价格、迁移、权限、配置和页面行为所需的定向测试；`backend/README.*`、`frontend-js/README.*`、`docs/` 与 `CODE_INDEX.md` 中直接受影响的现行说明。新增公开 API 合同及示例归 `contracts/`。
- A 阶段旧地址、页面权限和已验收功能继续可用。能耗采样、写入登记、多表 POST、SMA/DAA/第三方客户端、成本核算和订单分摊均属各自范围。

## 9. 验收

| 项目 | 判定方式 |
| --- | --- |
| AC01 项目配置 | 隔离环境创建工业用水项目，编辑名称／排序、停用／启用；稳定键、单位、历史价格、双语显示和已有单价保持正确。非管理员不能修改。 |
| AC02 动态页面 | 新增并启用水价后，水价卡、录价字段和历史列同时出现。水价尚未录入、所选日无水价及所选日无任何行时均保留历史列，缺值显示 `—`；录入零显示 `0`。只保存水价后同小时其他项目不变。停用项目从卡片与录价字段隐藏，其有记录的查询范围仍显示历史列。桌面等宽齐边，多项目换行，历史列拖拽／刷新恢复／重置及横向滚动可用。 |
| AC03 新 API | 真实隔离 HTTP 覆盖 Bearer、read/manage 分权及 admin 配置，单项／多项、精度、零、无效数值、重复键、时间和原子提交。覆盖空日、未录价的启用项目、停用项目在查询范围内有／无价格、不同页与越界页，确认 `columns` 与分页独立，实际小时数据不被虚构。当前价与选日历史符合第 3、4 节。 |
| AC04 三价兼容 | 原三路 API 按旧请求及响应回归。旧全组写入后新页面和旧 GET 一致；新单项写入后旧 GET 按第 6 节组合完整组。新自定义项目不改变旧响应；空库只填一项不伪造另两项。旧历史 ID、字段及分页在迁移前后逐项一致。 |
| AC05 并发和补录 | 同小时相同项目并发、不同项目并发、新旧 POST 交错及补录更早小时；事务不混淆价格，已明确写入的后续价格不被覆盖，当前价由真实记录时间决定。 |
| AC06 迁移与时间 | 空库及有价旧库执行显式后继，核对全部行、ID、价格、备注和时间，重复尝试及失败恢复无重复。覆盖非上海宿主机、上海自然日跨界和现有历史小时边界。模拟无关后继迁移后价格和观测读取仍工作。 |
| AC07 页面细节 | 中英及明暗主题，PC `1440×900`、平板横屏 `1024×768` 验证价格和项目弹窗的业务分组、标题页脚、正文滚动及遮罩取消不提交。构建、模块注册、受影响单测及文档链接通过。 |
| AC08 交付 | 数据／证据不只留在临时路径，明确迁移、兼容限制、源工作树一致性及临时资源回收。真实库、部署和发布未因软件验收自动执行。 |

## 10. Human Owner 决定与批准历史

Human Owner 已将第 6 节的兼容投影语义与 r2 一并批准，包括三项尚未齐全时旧 current 返回 null，以及新单项历史补录对后续旧视图的继承方式。该选择解决新旧调用同时使用同一份价格数据的场景。真实库采用目标和时点另行确定。

| 日期 | 修订 | 记录 |
| --- | --- | --- |
| 2026-11-24（Asia/Shanghai） | r1 draft | Human Owner 确认交互原型并授权起草独立单价规格；开发和实际数据库采用待后续批准。 |
| 2026-11-25（Asia/Shanghai） | r2 draft | Human Owner 确认 v5 原型并授权修订规格，明确启用的项目同时生成现价卡、录价字段和历史列；数据缺失显示 `—`。新增业务分组及分页独立的历史列合同；r2 精确范围与开发待 Human Owner 批准。 |
| 2026-11-25（Asia/Shanghai） | r2 owner_approved | Human Owner 明确指示「继续 001，批准 001任务 按std启动dev」，取消此前暂停并批准 ARCH-ENERGY-001 r2 按 STD 启动 Development；开发交付后进入独立 Verification。获批前 r2 草稿的 SHA-256 为 `7be38b512016212fa02dce14b8fdbe94cfec9afe0e8307cef6a6e23e607cfe6f`。允许编写迁移脚本及隔离环境验收；真实或共享 dev 数据库迁移、服务切换和部署未获本次授权。 |
