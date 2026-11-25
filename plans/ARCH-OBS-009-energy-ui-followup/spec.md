Task ID: ARCH-OBS-009
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r1，交 Development 按 STD 实施
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 能耗统计空态与能耗样本筛选体验
Owner: Core 能耗管理
Acceptance Chain Reference: 精确范围批准 → Development handoff → fresh-context Verification → Human Owner 最终验收
Related Task: ARCH-OBS-006、ARCH-OBS-007

# 能耗统计与样本页面跟进 · r1

## 1. 目标与依据

根据 Human Owner 确认的[能耗完整交互原型](../../work/energy-management-full-review.html)，调整能耗统计空态和能耗样本筛选区，让两页的状态反馈及视觉布局与既有过程监控页面一致。原型用于审阅布局与交互，使用本地示例数据。规格和现有真实 API 是后续实施依据。

[ARCH-OBS-007 r1 A](../ARCH-OBS-007-energy-management/spec.md) 的四页归并已于 2026-11-24 获 Human Owner 最终验收，见[验收记录](../ARCH-OBS-007-energy-management/checklist.md#human-owner-最终验收)。本任务仅针对其验收后的两项页面反馈另列范围，不改变 007 r1 A 的验收事实。

当前[能耗统计页](../../frontend-js/src/app/energy/views/consumption.vue)在未选表计、未配指标或未选时间时显示 `EmptyAxes`，空白坐标覆盖较大区域。无真实值可画时，图表区域也缺少与过程页一致的页面级提示。正常曲线已使用[共享 CurveChart](../../frontend-js/src/app/monitor/components/observations/CurveChart.vue)；[过程曲线页](../../frontend-js/src/app/monitor/views/observations/curves.vue)以文字说明加载、空结果或失败状态。

当前[能耗样本页](../../frontend-js/src/app/energy/components/EnergyAdmin.vue)使用表计和采样组筛选，两项会拉伸以占满工具栏。在表计选项成功返回空数组时，样本区容易显示为「暂无数据」，与已选择表计后的空查询结果难以区分。

## 2. 范围和需求

### 2.1 能耗统计

1. 保留已验收的主卡、标题、表计／采样组／指标／上海时间范围、查询、恢复默认和刷新入口。沿用现有选项、指标、样本和汇总 API，保留原有权限及数据语义。
2. 按过程曲线页风格显示简洁文字状态。加载中、无可访问表计、所选表计无指标、需要填写时间／尚未完成查询、查询成功但没有可绘制的样本，以及读取失败各自可辨认。失败状态提供重试，重试成功后显示新结果。
3. 上述无可绘制数据状态不显示空坐标轴。查询返回汇总时，仍显示后端返回的最新读数、用量、完整性及原因。缺测保持缺测，数值 `0` 按有效值显示。
4. 有可绘制数据时继续使用共享 `CurveChart`，曲线框、坐标、图例、主题和交互沿用该组件。每条曲线按真实采样时间绘制，原有缺测断点、相同时间样本、单位与数值处理继续有效。不得以页面刷新时间代替采集时间。
5. 选择、查询、刷新或离开页面时，较旧请求的返回不得覆盖当前选择或重建已离开的页面。错误、无表计和空结果不能互相冒充，也不能展示旧请求的结果作为当前结果。

### 2.2 能耗样本

1. 保留「表计」「采样组」、查询和重置。以过程样本工具栏和确认原型为参考，桌面与平板横屏下两项筛选采用紧凑宽度，避免为填满整行而分别拉伸成大输入框。按钮与输入控件底边对齐，窄屏允许换行，控件及标签完整可达。建议单项宽度约 180–240 CSS 像素，实际以双语内容完整和容器空间为准。
2. 表计选项成功返回空数组时，清楚显示「暂无可访问表计，请联系管理员配置」及对应英文。选项有值且成功查询到零条样本时显示空结果。选项或样本读取失败时显示失败信息及重试入口，不能将失败显示为零条结果。加载中的状态可辨认。
3. 继续使用现有默认表计选择、采样组、分页、列显示与排序、详情、备注及异常／已复核操作。样本值只读。筛选、换页、重试和重置保留正确表计与采样组，重复请求或乱序返回不能使旧记录覆盖当前结果。
4. 列宽使用既有公共工具，普通列可拖动，刷新、筛选及翻页后恢复，重置入口只重置当前表。字段标识、现有偏好键及最小列宽保持兼容。

### 2.3 共同要求

- 用户可见文案走能耗模块中英文 i18n；查询错误、零值和缺测在两个语言下均能区分。
- 统计旧地址 `/monitor/consumption`、路由名 `MonitorEnergy`、pageId `monitor.energy` 与管理员样本地址 `/energy/observations/data` 的现有访问控制继续生效。前端沿用用户 Bearer 请求层及后端既有权限。
- 保持实时／过程与能耗各自的数据与接口边界。温度、传动、清洗曲线使用共享图表的其他调用路径不得因本次界面调整发生回归。
- 侧栏中能耗统计与温度曲线当前均声明 `TrendCharts`，本任务无需调整菜单图标。
- 点击遮罩关闭等弹窗规范按根 `AGENTS.md` §9 执行。仅在本任务实际触达弹窗时调整并验证其布局与关闭行为。

## 3. 允许修改范围

- `frontend-js/src/app/energy/views/consumption.vue`，限统计空态、图表呈现、所需加载和错误状态协调。
- `frontend-js/src/app/energy/components/EnergyAdmin.vue`，限 `kind="samples"` 的筛选布局、状态及所需重试协调。该组件也服务表计指标配置，必须保留 `kind="config"` 的查询、表单、启停、显示顺序和保存行为。
- `frontend-js/src/app/energy/locales/zh-CN.json` 与 `frontend-js/src/app/energy/locales/en-US.json`，限本任务文案。
- `frontend-js/tests/module-registry/equipment-observation-columns.test.mjs` 及该目录下为统计／样本状态新增的聚焦测试。
- 如既有页面操作说明因本次状态反馈确需调整，可只修改 `frontend-js/README.md`、`frontend-js/README.zh-CN.md`、`docs/equipment-status-process-monitoring-guide.md`、`docs/equipment-status-process-monitoring-guide.zh-CN.md` 中相应段落。实际源码结构变化时按项目规则核对 `CODE_INDEX.md`。
- 本任务 Development 的 `tasks.md`、Verification 的 `checklist.md` 分别在各自 gate 创建。根 PLAN 与 plans 索引由协调者按角色事实同步。

保留共享 `CurveChart` 和 `EmptyAxes` 既有文件，能耗页面通过自身调用适配完成空态。若实施发现必须改动上述清单之外的文件或修改共享过程曲线行为，应交回 PM 核定范围。

## 4. 验收标准

| ID | 可验证结果 |
| --- | --- |
| AC01 统计空态 | 用隔离 API 夹具分别模拟加载、无可访问表计、无指标、未选时间、有效查询无样本、样本无可绘制值和读取失败。状态清晰、无装饰坐标；失败后重试成功恢复结果。 |
| AC02 统计有值 | 可绘制样本显示共享 `CurveChart`，样式与过程曲线一致。`0` 可画可读，缺测仍为缺测，后端返回的不完整结果及原因保留。上海时间范围、数据单位、刷新／恢复默认和无效时间提示保持既有语义。 |
| AC03 样本状态 | 选项成功但为空、有效表计返回零条、选项或样本请求失败三种情况分别显示正确反馈。失败可重试，状态切换后不显示前一请求的过时内容。 |
| AC04 筛选与列表 | PC 和平板横屏下表计／采样组紧凑，查询／重置与控件对齐；窄屏可换行且不截断。查询、重置、换页、列宽拖拽与重置、详情、备注及复核沿用现有功能，表计指标配置页回归通过。 |
| AC05 权限与共享组件 | 中英文在明暗主题均可读；原统计路由和管理员样本路由保留权限，前端请求仍使用现有用户 Bearer。温度、传动、清洗过程曲线的有效值、零值、缺测和时间查询回归通过。 |
| AC06 异步与工程 | 隔离夹具覆盖切换表计／时间时乱序响应、失败后重试和离页。`pnpm check:modules`、受影响模块测试、构建及 `git diff --check` 记录真实结果。全量模块测试中的既有失败按运行前基线逐项区分，不因本任务产生新增失败。 |
| AC07 浏览器 | 使用合成数据及隔离 API，在 PC `1440 × 900`、平板横屏 `1024 × 768` 的浅色和深色主题逐项核对 AC01、AC03、AC04。额外检查窄屏下筛选区换行、内容与操作可达。若调整弹窗，按根契约验证标题／页脚可达、正文滚动和遮罩取消无提交。 |

## 5. 限制、风险与交接

Human Owner 已批准精确 r1。Development 按 `frontend-ui`、`i18n-workflow` 和 `code-document-indexer` 实施与自检，再由 fresh-context Verification 独立检查。真实数据、部署和服务切换遵循项目契约。

页面反馈通过隔离 fixture 验证，fixture 必须区分实际 HTTP 失败、成功空数组和成功空结果。页面正常数据来自既有服务。既有工作树有并行改动，Development 应先核对目标文件和测试基线，避免覆盖其他任务。

后端、数据库、表计运行配置、机器接口、写入登记、多表上报、自定义单价、历史数据迁移及实时／过程 `503` 处置均在本任务范围之外。用户已说明实时／过程读取故障已修复，本任务只做共享图表相关回归。

验收证据应写入角色拥有的任务文档，明确临时测试目录、保留用途与清理触发条件。开发与独立验证不得以临时副本替代正式源码交付。

## 6. 修订与批准记录

| 日期 | 修订 | 记录 |
| --- | --- | --- |
| 2026-11-24（Asia/Shanghai） | r1 draft | Human Owner 确认能耗完整原型并授权按 STD 起草规格。精确 r1 开发范围等待 Human Owner 批准。 |
| 2026-11-24（Asia/Shanghai） | r1 owner_approved | Human Owner 原话：“批准 ARCH-OBS-009 r1，按 STD 启动 Development。” |
