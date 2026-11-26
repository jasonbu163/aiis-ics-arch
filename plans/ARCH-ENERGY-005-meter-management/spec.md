Task ID: ARCH-ENERGY-005
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r1，交 Development 按 STD 实施
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 能耗表计管理与既有配置兼容
Owner: Core 能耗管理
Acceptance Chain Reference: Human Owner 精确范围批准 → Development handoff → fresh-context Verification → Human Owner 最终验收
Related Task: ARCH-OBS-007、ARCH-OBS-010、ARCH-ENERGY-002、ARCH-ENERGY-003、ARCH-ENERGY-004

# 能耗表计管理 · r1

## 1. 目标和现状

管理员从「能耗管理 → 配置管理 → 表计指标配置」管理表计。新增表计后可立即选择该表、配置指标，并由已有登记来源向其写入样本。页面参照设备状态和能耗现有写入登记的表格、操作与弹窗。表计标识、名称及可读角色由管理员维护。

Human Owner 于 2026-11-25（Asia/Shanghai）针对「先整理 Swagger 分组，再把表计管理补成单独的小规格」明确表示「好的 按你的建议来做 批准」。据此按 STD 起草本规格，随后批准精确 r1 开发范围。此前已确认能耗、实时和过程各自独立，登记来源一包可写多表，页面请求使用登录 Bearer，已登记来源写入及公有读取按各自已批准合同免 Token。

现有能耗「写入登记」保存发送方 `sourceKey`。目前 `meters` 与 `meterReadScopes` 来自私有观测 profile，`energyGrants` 解析也会核对 profile 的表计。管理员在指标配置页只能从既有表计选择，不能通过页面新增表计。样本、回执和指标已有能耗独立表。相关入口见 [能耗页面](../../frontend-js/src/app/energy/components/EnergyAdmin.vue)、[profile 解析](../../backend/app/equipment_observation/profile.py)、[登记写入](../../backend/app/equipment_observation/services/energy_registered_ingest.py) 和 [旧 v2 写入](../../backend/app/equipment_observation/services/ingest_v2.py)。

## 2. 业务范围

1. 一个表计代表一个计量对象，其标识为 `meterId`。名称和登录角色可读范围用于页面查询和表计选择。采样组与指标仍在现有「表计指标配置」里维护。
2. 一个 `sourceKey` 是写入方，一次登记可向多个已存在的表计写入，不要求增加来源到表计的授权表或逐表绑定。来源的登记、启停和删除继续由现有「写入登记」处理。可读角色控制登录用户的能耗表计查询范围，不改变免 Token 公有 GET 的已批准合同。
3. 管理员可查询、新增和编辑表计。第一版使用稳定标识，无表计删除、停用、重命名标识、采集源绑定或业务数据清理。已有指标、样本及回执不因维护表计名称或可读角色而被改写。
4. 新增表计默认管理员 `admin` 可读。其他角色须由管理员明确勾选。角色继续受现有 `energy-consumption-read` 等接口权限控制，配置可读表计不授予接口、菜单、登录或其他业务权限。
5. 复用能耗样本和指标逻辑，实时／过程和能耗各自存储与查询，不建立跨域外键、JOIN 或 `taskNo` 依赖。动态单价、能耗曲线配置和 Swagger 分组由各自任务负责。

## 3. 页面交互

1. 保留「配置管理」上卡、现有「表计指标配置」及「写入登记」。在「表计指标配置」卡片标题的操作区增加「管理表计」。该入口展示表计管理列表，提供返回指标配置、关键词查询、重置、新增、编辑和重置列宽。空配置、无匹配、加载和读取失败可区分，失败后允许重试。
2. 列表显示表计标识、名称、可读角色和编辑操作。普通列使用公共列宽能力，按稳定字段保存本机偏好并提供「恢复默认列宽」；总宽度不足时横向滚动。参考现有 [写入登记组件](../../frontend-js/src/app/energy/components/EnergyWriteSources.vue) 和 [表计指标组件](../../frontend-js/src/app/energy/components/EnergyAdmin.vue)。
3. 新增／编辑弹窗复用 `standard-form-dialog`、`compact-form-dialog`、公共按钮、现有标签和中英文资源。内容按「基本信息」「可读角色」分组。基本信息包含 `meterId`、中文名称、英文名称。创建后标识不可编辑。可读角色沿用系统角色名称，新增表计默认勾选管理员，其他角色由管理员选择。已有 profile 角色要完整展示和回填，页面不因仅识别常用角色而丢弃旧角色。
4. 保存成功后关闭弹窗并刷新表计列表。返回指标配置页时不需刷新浏览器或重启后端即可在表计下拉选择新表。取消或点击弹窗遮罩不提交。超长内容时正文独立滚动、标题和页脚可达。新增及编辑表计、已保存表计的指标配置都可正常使用。
5. 管理表计操作仅管理员可见并由后端强制管理员检查。普通登录用户只通过既有接口看到其可读范围，不能访问或变更管理接口。页面设计不引入来源登记或第三方客户端配置流程。

## 4. 数据模型与历史兼容方案

本 r1 建议用一个能耗独立表 `energy_meters` 保存页面创建及覆盖配置。`meter_id` 为大小写敏感主键，保存中英文名称、`read_roles` JSON 数组、创建时间和实际更新时间。名称、标识沿用现有 profile 的数据类型与有效范围。角色使用系统角色稳定键，禁止按翻译显示文案匹配。以能耗表为目标，不建立跨域外键。

每次需要解析表计身份或登录用户可读范围时，合并只读的原 profile 和数据库配置。对于同一 `meterId`，存在数据库记录时使用数据库名称及角色清单，缺少数据库记录时沿用 profile 中的名称及 `meterReadScopes`。数据库新记录和仍在 profile 中的表计均可作为有效表计。数据库更新提交后下一次请求读取新值，不把数据库表计写回全局 profile 缓存。跨请求不缓存表计与角色变更，避免页面保存后仍需重启。

新增 `meterId` 与现有 profile 或数据库表计重名时返回冲突；管理员可编辑已有 profile 表计。首次编辑 profile 表计时，以当前 profile 的完整名称和角色集合为基线，在事务内创建一行覆盖配置并应用用户实际提交的更改。未提交的字段、原有的自定义角色键和顺序无关的角色集合须保留；显式提交可读角色时，以提交的角色集合为准。首次编辑相同 profile 表计并发时由唯一键与事务串行处理，不能覆盖已提交的其他字段或生成两行。已经存在数据库记录时，以该行的最新提交值合并部分更新。请求中标识从不变化。

迁移只新增表，不自动复制 profile、生成测试表计或修改样本、指标和来源。升级后即使表为空，所有旧 profile 表计及每个角色的可读范围与升级前一致，既有名称和样本读取结果不变。管理员列表可显示全部表计配置供维护，表计本身的数据读取仍遵守该角色的有效范围。含历史数据但尚未被当前 profile 使用的标识经管理员新建后，原标识关联的历史指标和样本继续属于该标识，不重写记录。

## 5. API 草案

路径均以 `/api/v1` 为前缀，成功响应使用既有 `{code, message, data}`。管理接口使用登录用户 Bearer 和现有 `get_current_active_admin` 检查。以下方法和字段属于获批准的 r1 合同。

| 方法与路径 | 行为 |
| --- | --- |
| `GET /energy/meters` | 返回按 `meterId` 稳定排序的有效表计定义数组，合并数据库与 profile。每项含 `meterId`、`nameZh`、`nameEn`、`readRoles`。 |
| `POST /energy/meters` | 创建表计。提交 `meterId`、`nameZh`、`nameEn`，可提交 `readRoles`。省略角色时默认 `["admin"]`，响应为完整表计定义。 |
| `PATCH /energy/meters` | 以请求体 `meterId` 指明已有表计，部分更新 `nameZh`、`nameEn`、`readRoles`。未提交字段保留原值，响应为完整表计定义。 |

PATCH 使用请求体标识以支持现有标识合同允许的中文、斜杠和点等字符。`meterId` 长度、首尾空白和字符合法性沿用现有 `identifier(..., 64)`，名称沿用现有 profile 的 1–128 字符规则。角色值使用稳定角色键，去重后保存。空角色集合表示没有登录角色可读，管理接口仍可由管理员编辑该定义。空更新、非法字段或格式返回既有稳定错误信封 422，未登录或 Token 无效返回 401，非管理员返回 403，未知表计编辑返回 404，重复标识返回 409。数据库不可达或目标不匹配返回清晰 503。

创建示例。新增表计后可在页面继续配置 `electricity` 采样组与指标，`sourceKey` 仍在另一页面登记。

```json
{
  "meterId": "meter-01",
  "nameZh": "1号电表",
  "nameEn": "Meter 01",
  "readRoles": ["admin", "operator"]
}
```

登录用户的 `GET /energy/consumption/options`、`/energy/consumption/definitions`、`/energy/metric-configs`、`/energy/consumption/samples`、`/energy/consumption/summary` 和样本管理接口继续使用原路径、权限、响应字段和错误语义，其表计范围统一按上述有效配置解析。新管理 API 的 OpenAPI 和中英文合同由实施同步。

## 6. 写入和既有权限兼容

1. 能耗登记 POST 继续先检查来源状态和已有回执，再对新包按当前有效表计集合、已启用指标、真实区间等既有规则检查。管理新表计后无需修改 profile 或重启，就可由一个已登记来源按 `ARCH-OBS-010 r1` 发送单表／多表包。已有回执的等价重试及不同正文冲突语义保持原合同。
2. profile 及其旧 `meters`、`meterReadScopes`、`energyGrants` 在本任务继续原样加载。旧机器 Bearer v2 的 producer、表计／组／指标授权不因页面新增表计或更改登录角色自动扩大。对已存在的合法 profile，原已授权旧 v2 写入及重放按原合同继续可用。v2 新增 producer 授权及其 profile 维护不在本任务范围。
3. 现有 `energyGrants` 的解析依赖 profile 的 `meters`。不能为了页面管理直接删除或改写旧 profile 表计，也不能把数据库集合静默写入原缓存或放宽现有 producer 授权。涉及新表计的免 Token 登记写入从有效集合判断表计存在，旧 v2 仍按已配置 grant 判断。
4. 同一个有效表计的选项、指标列表／编辑、样本列表、详情、备注／复核和统计均使用一致的可读范围。旧角色不因简单升级自动增加或减少访问；管理员显式保存角色变更后，下一请求按新范围执行。正在进行的请求按其已读取的配置完成，不能产生部分写入或不一致的表计定义。
5. [能耗公有 GET](../ARCH-ENERGY-003-public-energy-reads/spec.md) 已有合同继续按保存的样本与指标定义返回，不增加 Token、角色过滤或 `sourceKey` 参数。过程／实时的设备、来源、指标及读写链路不因本任务改变。

## 7. 迁移、顺序和回退

仅增加一个显式 Alembic 后继，前驱在实施时确认当前唯一 head，并协调其他已批准的后继。迁移验证目标库和既有能耗依赖，创建 `energy_meters`，不得自动修改真实 profile 或导入业务数据。按根契约验证无关后继 revision 后实际结构兼容时的正常读写，不把全库 revision 变成能耗启动或日常读写门槛，也不对每次请求统一扫描表结构。

包含此功能的服务采用前应先在目标库应用经独立批准的该迁移，再切换服务源码。新表缺失或数据库不可达时，依赖表计管理的能耗请求返回清晰失败，不以旧 profile 静默替代已保存的数据库覆盖权限。实时／过程和与表计无关的入口继续按实际业务依赖运行。真实 dev／生产目标、备份、数据库迁移和服务切换均另行授权。

回退应用前保留新增数据库表及其配置。回退旧应用后，新建表计和对 profile 表计的数据库覆盖不会由旧代码识别。需要继续使用这些配置时应先导出、核对并明确采用方式，不能宣称旧应用已读取新定义。禁止通过删除样本、指标、回执或编辑原 profile 来伪装回退完成。历史数据迁移与旧 v2 原有 grants 保持独立处理。

## 8. 实施边界

- `frontend-js/src/app/energy/` 下表计管理入口、列表、表单、API、状态和中英文 locale。优先复用现有源登记和指标管理的组件与交互。按项目公共组件支持列宽、本机偏好、紧凑弹窗及主题。
- `backend/app/equipment_observation/` 下能耗表计模型、schema、服务、路由和使用表计范围的直接调用点。仅为兼容旧 profile 与 v2 而作必要调整，不改实时／过程语义。`backend/alembic/versions/` 增加一个表计后继。
- 相应 `backend/tests/`、`backend/tests_mysql/`、`frontend-js/tests/module-registry/` 聚焦回归和合成夹具。允许更新直接相关的公开接口合同、`contracts/README.*`、相关模块 README、`docs/` 及 `CODE_INDEX.md`。Development 使用 `backend-arch`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`，遵循 `uv`／`pnpm`。
- 保留其他并行任务文件、指标样本和现有授权。若需新增第二张表、修改旧历史迁移、改造 v2 授权或增加表计删除功能，须先返回 PM 修订范围。

## 9. 验收标准

| ID | 可验证结果 |
| --- | --- |
| AC01 页面新增 | 空 profile 表计场景下，管理员进入管理表计新增测试表计并默认赋予 admin，返回指标配置后无需重启即可选中、保存指标。列表、搜索、空状态、失败重试、列宽记忆和恢复可用。 |
| AC02 编辑与角色 | 编辑名称和角色后下一次请求生效。管理员可维护表计定义，未授予表计的角色不能通过表计选项、指标、样本、详情、复核或统计访问。被授予角色仍须有现有能耗接口权限。非管理员访问管理接口失败。 |
| AC03 旧配置兼容 | 含多个旧 profile 表计及不同角色范围的隔离场景升级后，原名称、选项、指标、样本和可读角色逐项一致。首次编辑旧表计仅覆盖实际更改字段，保留未改名称及全部旧角色；并发首次编辑和重复创建不丢失配置、不生成重复标识。 |
| AC04 单源多表与旧 v2 | 登记来源在一个请求写入新表和旧表，逐组回执及样本可读。旧 v2 producer 的合法 grant、POST 和重放保持原行为，未授权表计／指标仍拒绝。更改登录角色不会扩大或撤销机器 grant。 |
| AC05 公有与数据边界 | 公有最新和历史 GET 的免 Token、结果及数据来源符合原合同。维护表计前后旧样本、指标、回执及实时／过程数据未被改写，互不产生跨域外键、JOIN 或任务号依赖。 |
| AC06 标识与异常 | 大小写、非 ASCII、斜杠和点等符合既有 identifier 的标识可新增并编辑；冲突、未知表计、非法字段和无权限按 API 合同返回。数据库缺表／不可达时提供清晰失败，不能回退放宽已保存角色；无关模块继续工作。 |
| AC07 迁移及时间 | 空库和有旧表计及历史样本的隔离 MySQL 升级，仅新增表计表，旧事实与配置逐项比对一致。再应用无关后继 revision，表计、登记、样本及现有过程／实时的兼容读写继续可用。实际时间字段和 API 以项目上海时区合同处理。 |
| AC08 交付验证 | 中英文、浅／深色，PC 1440×900 和平板横屏 1024×768 下列表及弹窗可操作，遮罩取消不保存。`uv`／`pnpm` 聚焦测试、模块注册、构建、OpenAPI 与文档链接检查通过。验证和交付工作树一致，真实库采用状态单独记录。 |

## 10. 审阅和交接

Human Owner 已批准本方案的兼容选择。旧 profile 继续作为未覆盖表计和旧 v2 grant 的来源，管理员首次编辑某旧表计时才创建数据库覆盖。登录用户的可读角色由表计管理维护，公有 GET 和已登记来源写入保持原合同。第一版以新增、编辑为限。

| 日期 | 记录 |
| --- | --- |
| 2026-11-25（Asia/Shanghai） | Human Owner 同意先整理 Swagger 分组并起草表计管理小规格。PM 按 STD 起草 r1，未记录精确开发批准。 |
| 2026-11-25（Asia/Shanghai） | Human Owner 明确表示「批准 ARCH-ENERGY-005 r1，按 STD 启动 Development。」据此批准精确 r1。 |

Development 按获批准的精确 r1 创建 `tasks.md` 并实施、自检，再交 fresh-context Verification。最终验收由 Human Owner 决定。本次规格起草无临时资源。

---

## ARCH-ENERGY-005 r2 · 上卡切换与三栏卡片

Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r2，交 Development 按 STD 实施

### 依据和范围

Human Owner 指出「为什么管理表计页面不能放在上卡？」以及「而且 卡片三栏风味也不对」。r1 §3.1 将表计管理设置为指标配置卡片中的入口及返回操作。r2 将表计管理改为上卡同级工作区，并调整表计管理下卡的纵向三栏布局。r1 规格原文和已形成的 Development、Verification 记录继续保留；Human Owner 已批准本节的精确 r2 范围。

### 界面行为

1. 在「能耗管理 → 配置管理」既有上卡复用 `card-action-segmented`，按「表计管理」「表计指标配置」「写入登记」排列三个同级工作区。初始仍选「表计指标配置」。选择哪个选项，下卡即显示对应标题、操作、筛选与内容。移除指标配置卡片中的「管理表计」入口和表计管理卡片中的「返回」按钮，避免同一导航重复出现。
2. 从表计管理新增或编辑保存后切到「表计指标配置」，重新取得当前可读表计，刚保存的可读表计可在下拉框中选择。切换三个工作区时保留各自既有的查询、配置、登记和错误处理行为。
3. 表计管理下卡按项目 [页面布局基线](../../frontend-js/DESIGN.zh-CN.md#页面布局与工作区切换) 从上到下分三栏。第一栏为标题和右侧「新增」「重置列宽」。第二栏为独立的全宽筛选区，关键词输入可伸展，「查询」「重置」靠右，筛选区左右边距与表格内容对齐，底部有主题分隔线。第三栏放表格或空态、加载和失败信息。
4. 参考现有 [能耗写入登记](../../frontend-js/src/app/energy/components/EnergyWriteSources.vue) 及设备／过程配置页使用 `BaseCard`、`ActionButton`、`table-actions`、`row-actions` 和主题 token。表格及表头填满可用内容区，普通列在空间充足时分配剩余宽度，操作列按公共行操作样式布局。窄视口允许筛选换行和表格横向滚动。继续使用当前按表格和字段隔离的列宽偏好、拖拽和重置入口。
5. 表计新增、编辑与角色表单沿用 r1 已批准的字段、校验、弹窗布局和遮罩取消行为。既有接口、权限、样本及数据库合同继续按 r1 运行。

### 实施边界

- 仅调整 `frontend-js/src/app/energy/views/admin.vue`、`frontend-js/src/app/energy/components/EnergyAdmin.vue`、`frontend-js/src/app/energy/components/EnergyMeters.vue`，以及直接需要的能耗中英文 locale。
- 仅增加或调整 `frontend-js/tests/module-registry/` 中对该工作区切换、现有表计交互和布局回归必要的测试。采用 `frontend-ui`、`i18n-workflow` 和 `code-document-indexer` 的适用规范。
- 后端、API、权限、数据库结构、迁移和实际数据均沿用 r1。`EnergyWriteSources.vue`、设备和过程配置页作为视觉及组件参考。独立的能耗曲线和单价任务仍按其各自规格推进。

### 验收

| ID | 可验证结果 |
| --- | --- |
| R2-AC01 | 上卡三个工作区顺序与所选状态正确，初始为表计指标配置。点击表计管理直接显示其下卡，指标卡没有重复入口，表计卡没有返回按钮。写入登记与指标配置可正常切换。 |
| R2-AC02 | 表计管理是标题／操作、筛选、表格或状态三栏。PC 1440×900 和平板横屏 1024×768 的浅色／深色、中英文均检查下卡左右边距、分隔线、关键词和查询按钮对齐。默认表格／表头填满内容区，操作列清楚可用，无多余右侧空白列或控件重叠。 |
| R2-AC03 | 狭窄视口工具区可换行，宽表可横向滚动。表计列宽拖拽后切换工作区及重新加载保持本机偏好，重置后恢复默认；行内编辑保持公共按钮样式。 |
| R2-AC04 | 合成页面验证新增或编辑表计后切到指标配置，刚保存且可读的表计出现在选项中。表计查询、保存、错误与空态、遮罩取消，以及写入登记和既有指标操作回归通过。 |
| R2-AC05 | 项目声明的 `pnpm` 聚焦测试、模块检查、构建和文档链接检查通过。浏览器验证使用隔离或合成数据，记录实际视口和主题。交接明确正式源码整合情况与目标环境采用状态。 |

2026-11-25（Asia/Shanghai），PM 根据 Human Owner 的上卡位置和三栏样式反馈起草 r2。Human Owner 随后明确表示「批准 ARCH-ENERGY-005 r2，按 STD 启动 Development」，据此批准精确 r2。Development 按本节实施、自检，再交 fresh-context Verification。r1 原有验收记录保持原貌。本次规格起草无临时资源。
