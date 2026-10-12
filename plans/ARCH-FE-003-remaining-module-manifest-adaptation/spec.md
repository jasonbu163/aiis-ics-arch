Task ID: ARCH-FE-003
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已明确批准前端 ARCH-FE-003 r2 并要求进入 dev；交 Development 按当前价格页直调 API 范围实施，developer_handoff 后再次交 fresh-context Verification

Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 五个已复制模块的 Registry 接入与价格页前端依赖修复
Owner: frontend-js Core 模块框架
Related Task: ARCH-FE-002, ARCH-FE-004
Depends On: ARCH-FE-002 owner_accepted r4 的现有 Registry 与权限基线
Acceptance Chain Reference: ARCH-FE-003 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-10
Updated: 2026-10-10

# r2 当前批准范围：价格页直接使用 auxiliary API

本节为当前 r2 范围权威，替代下方从未获批或实施的补迁 store 草案。r1 完整批准规格、实施与
独立 `qa_blocked` 历史均保留；r1 的 manifest、导航、标题与权限成品继续作为只读验收基线。
r1 AC-001/002/003/005 已通过，AC-004 必需构建因价格页引用缺失 store 而未通过，不算完整交付。

## R2-001：直接 API 与页面局部状态

- 仅改 auxiliary 价格页：移除 `useEnergyPriceStore` 引用，直接从现有 `@/app/auxiliary/api`
  调用 `getCurrentPrice`、`createPrice` 与既有 `getPriceList`。状态留在现有页面，不新增 store、
  composable、Service 或共享抽象；保留当前路由、页面布局、表格、单位、备注组合和四位小数输入。
- 价格初始为空，备注为空字符串；挂载及手动刷新读取当前价格与历史。当前记录为空时显示
  “尚未设置”并允许填写；不把旧 store 的 0.85/15/3.5 当作已配置价格，也不把空值转成 0。
  当前记录的有效非负数值及非空数字字符串可归一为数字，合法 `0` 必须保留；null、空字符串、
  非数字、非有限数或负数不得变成可保存价格。表单必填/数值校验允许 0；备注沿既有字段处理。
- 当前价格、历史与保存各自有 loading 和错误反馈；现价加载/保存期间禁用会覆盖表单的编辑、
  刷新或重复提交，finally 恢复状态。加载失败保留已有表单/历史数据并提示，首次失败保持空值；
  历史空列表显示原表格空状态。成功返回但当前价格字段非法时按加载错误处理，不补默认值。

## R2-002：保存与刷新语义

- 校验通过后使用本次提交快照调用 `createPrice`，payload 保留三个价格、三个分项备注与组合
  `remark` 的既有字段；不增加后端字段或改现有 API/mock。重复保存不得形成并发提交。
- POST 成功后页面保留本次已保存值并显示成功，随后等待历史刷新；失败时保留用户输入并提示。
  历史刷新失败单独提示，不把已成功 POST 改写成保存失败，也不自动再次 POST。
- 保存后不无条件用新的 GET 覆盖刚保存的值；后续手动刷新再读取服务端现价。现有 diagnostic mock
  返回固定价格/历史，复用它验证接入，不宣称 mock 已实现持久化或价格历史新增。

## R2-003：必要双语文案与窄行为测试

- 只在 auxiliary locale pair 的 `price` 下补对称键：`currentEmpty`、`currentLoadError`、
  `historyLoadError`、`invalidPrice`，分别表达尚未设置、现价加载失败、历史加载失败、有效非负价格
  校验。保存成功/失败与 loading 沿用既有公共文案/控件，不扫描整改其他业务文案。
- 新增单个价格页行为测试，用现有 Vue/Vite/Node 工具链执行实际页面逻辑并注入 API stub，不写
  镜像实现或只断言源码字符串。覆盖有效价格含 0、数字字符串、空/非法数据、加载失败与状态恢复，
  保存 payload/成功同步/历史刷新、POST 失败保留输入、历史刷新失败及重复提交保护。

## r2 精确写入 allowlist 与保护面

Development 仅写：

1. `frontend-js/src/app/auxiliary/views/price/index.vue`
2. `frontend-js/src/app/auxiliary/locales/en-US.json`（仅上述必要 `price` 键）
3. `frontend-js/src/app/auxiliary/locales/zh-CN.json`（同上）
4. `frontend-js/tests/module-registry/price-page.test.mjs`（现有 glob 自动发现）
5. 本任务 `tasks.md` 的 r2 元数据/实施/handoff，完整保留 r1 历史。

auxiliary manifest/API/mock、其余页面与目录内容、r1 九实现文件、MainLayout/Registry/权限、真实与
example env、package/依赖/lock、CODE_INDEX、004 与其他既有改动受保护；不迁 store 或创建其测试。
本轮不改 backend/DB/设备、Docker/部署或 Git refs，不新增生产价格规则、权限或配置。
后端衍生问题由独立 PM spec 定义，不是本前端范围的实施面或默认获批依赖。

## r2 验收与交付

| 标准 | 必需证据 |
| --- | --- |
| AC-r2-001 | 价格页仅通过现有 auxiliary facade 读取/保存，缺失 store 引用消失；局部状态、0/空值、错误与 loading、保存/历史刷新符合 R2-001/002，实际页面行为 stub 测试通过且无真实请求。 |
| AC-r2-002 | 新四键双语对称、可解析，price 页所有本次可见状态有翻译；原 auxiliary manifest/API/mock 与其他文案保持，测试不新增依赖。 |
| AC-r2-003 | module checker、完整 test:modules、排除真实 env 的公开隔离完整 pnpm build 均 exit 0；保留 r1 九组导航、15 个目标路由身份、隐藏详情、双语标题及权限负例回归。 |
| AC-r2-004 | 相对 r2 开始基线的 diff 限于 allowlist，受保护内容未变，r1 历史完整；git diff --check 与任务本地链接检查通过。新的 fresh-context Verification 独立记录 verdict，Human Owner 最终验收仍待真实决定。 |

公开 fixture 与构建 outDir 使用本任务 `/private/tmp`，排除 `.env*` 并清除继承 VITE_*；沿用既有
依赖与锁，可用已记录的进程级 pnpm 选项防止自动安装。必要公开浏览器复核也不访问真实 backend。
未消除的后续源码/构建缺口须如实记录并回 PM，不跳过必需 build 或自行扩大范围。

风险：前端移除虚构默认价及保留零值改变旧 store 的回退行为，须以上述正反例确认；既有 API 的
真实返回、持久化、费用计算与并发业务语义未由 fixture 验证。回退只处理本轮自有增量，不 reset
或删除用户模块；破坏性回退、部署与资源回收继续遵守独立授权。

Development / Verification 使用 `frontend-ui`、`i18n-workflow`；后端合同修改另行 handoff。
PM 仅写 spec，Verification 在新 developer_handoff 后更新 checklist 并保留 r1 `qa_blocked`，
主协调者机械同步索引。本轮不改 tasks/checklist 或实现，不冒称角色 ACL、强制路由或最终验收。

2026-10-10：Human Owner 明确要求“调整r2，价格页直接调用auxiliary的API，不再补store”，且后端
先不动。PM 据此修订 r2 草案，当时新增状态/验收/allowlist 细节尚待精确 r2 审阅批准；旧 r2 补 store
方案未获批、未实施，以下保留为方案变更历史，不授予其写入权。

2026-10-10：Human Owner 对当前精确价格页直调 API 方案明确回复“批准前端 003 r2，进入 dev”。
主协调者转交该真实决定，本 spec 据此记录 owner_approved 并 handoff Development；范围、allowlist、
验收与风险不变。批准仅适用当前 r2 前端范围，不包括旧补迁 store 草案或后端衍生任务，也不等于
QA verdict、Human Owner 最终验收或发布/部署授权。

# 未批准、未实施的 r2 补迁 store 旧草案（仅历史，以下原文保留）

Task ID: ARCH-FE-003
Revision: r2
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: pending；r1 独立 verdict 为 qa_blocked，交 Human Owner 批准精确 r2 的 energyPrice store 最小补迁，批准后由 Development 实施并再次交 fresh-context Verification

Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 五个已复制模块的 Registry 接入及必需构建依赖补齐
Owner: frontend-js Core 模块框架
Related Task: ARCH-FE-002, ARCH-FE-004
Depends On: ARCH-FE-002 owner_accepted r4 的现有 Registry 与权限基线
Acceptance Chain Reference: ARCH-FE-003 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-10
Updated: 2026-10-10

# r2 当前草案：补回已确认缺失的 energyPrice store

本节为 r2 范围权威；下方 r1 完整批准规格与历史原文保留。r1 的 manifest、标题、导航及权限合同
继续作为功能验收基线，其成品本轮只读保护；r2 不重新授予 r1 九实现文件写权。

## 依据与精确范围

已完整读取当前 r1 spec、Development handoff 及新落盘的独立 checklist。r1 的 AC-001/002/003/005
通过，28 项测试通过；必需隔离构建因 auxiliary 价格页第 133 行引用不存在的 `@/store/energyPrice`
而失败，AC-004 未通过，独立 verdict 为 `qa_blocked`。r1 实施记录不等于完整交付或最终验收。

只读核对确认旧源码存在：
`/Users/jason/Desktop/DreamCode/vibe-l2-front-end/frontend-next-js/src/store/energyPrice.js`，
SHA-256 为 `355d2c090f8cf1bbe3ddf53c46ce86cb0c5512a4a88b2783d0616f5a9bd9e506`。
其直接依赖仅为当前已安装的 pinia、vue，以及当前 auxiliary API 已导出的 getCurrentPrice/createPrice。
此次只补迁该已确认文件；解除首个缺口后出现的其他错误按真实证据另行定范围。

## R2-001：保留业务行为的最小补迁

- 新增当前 `frontend-js/src/store/energyPrice.js`，沿旧共享位置满足现有 import，保留导出名称、
  Pinia store ID、默认价格、公开 state/actions、请求 payload、错误返回、loading 及成本计算行为。
  允许修正文件头路径与尾随空白；不重构或顺手修改默认值、零值回退、精度或错误策略。
- 保留通过 `@/app/auxiliary/api` 调用现有 facade；不增加直接 HTTP、长期 mock、后端接口或权限。
  auxiliary 的页面、API、manifest 与全部既有内容不改，不为“模块归属优化”迁移其 import。
- `CODE_INDEX.md` 仅增加该 store 的真实入口项，保留其中 004 及其他已有修改。

## R2-002：独立 store 行为验证与完整构建

- 新增一份被现有 `test:modules` glob 自动发现的窄测试；使用真实 Pinia/Vue 与隔离 API stub，
  不发网络请求、不改正式 API/mock/env。覆盖默认值与 setter、单项及总成本的两位小数字符串，
  fetch 成功/失败/loading 复位及原回退语义，以及 save payload、成功更新/true、失败保留/false。
- 复跑现有 module checker、完整 test:modules 与公开隔离 `pnpm build`，沿用既有依赖/锁文件。
  fixture 排除真实 `.env*` 并清除继承的 VITE_*，公开配置与 outDir 限本任务 `/private/tmp` 目录。
  可使用 r1 已记录的进程级 pnpm 依赖检查选项避免自动安装；不修改项目配置或安装依赖。

## r2 精确新增写入 allowlist

Development 仅写 `frontend-js/src/store/energyPrice.js`、
`frontend-js/tests/module-registry/energy-price-store.test.mjs`、`CODE_INDEX.md` 的该 store 单项，
以及本任务 `tasks.md` 的 r2 元数据/实施/handoff；完整 r1 Development 历史必须保留。
PM 仅写 spec；新的 fresh-context Verification 更新 checklist 的 r2 元数据/验证，完整保留 r1
`qa_blocked` 与原证据。主协调者只机械同步索引。角色文档在各 gate 形成，短期 Revision 不同属阶段事实。

排除 r1 九实现文件、auxiliary 全目录、其他模块业务/API、MainLayout/Registry/权限、真实与 example
env、依赖/package/lock、backend/DB/设备、Docker/部署、004 及其他任务。不得用 shim、禁用模块、
删除 import 或绕过 build 消除错误。Git 发布、正式 dist 与真实业务调用继续不在范围。

## r2 验收、风险与回退

| 标准 | 必需证据 |
| --- | --- |
| AC-r2-001 | 补迁 store 与上述指纹来源的行为一致，差异仅文件头路径/空白；独立 API-stub 行为测试通过且无真实请求。来源文件若漂移，停止受影响写入并重新确认来源。 |
| AC-r2-002 | module checker、完整 test:modules 与公开隔离完整 pnpm build 均 exit 0；r1 九组导航、15 个目标路由身份、隐藏详情、双语标题、权限负例继续通过。构建必需，不继承 r1 局部 pass 为 r2 verdict。 |
| AC-r2-003 | 增量 diff 在 r2 allowlist 内，r1 九实现文件、auxiliary、env 与 004 相对 r2 开始基线未变；CODE_INDEX 只有 store 单项增量，`git diff --check` 与任务本地链接检查通过，r1 全部历史保留。 |

保留旧 `||` 零值回退及价格默认值是本次兼容选择，未评估真实业务价格规则；stub/build 不证明
真实 API、业务保存、设备或生产行为可用。后续 copied-page 依赖缺口须如实记录 blocker 并回 PM，
不得自动扩大范围或记为 deferred complete。回退仅针对 r2 自有增量，不删除用户模块或 reset 共享工作树；
实际破坏性回退及资源回收遵守独立授权。

Development 使用 `frontend-ui` 与 `code-document-indexer`；本次不新增界面文案或修改 API 合同。
新 fresh-context Verification 读取完整 r1/r2 bundle、当前实现及两阶段增量 diff，独立复核以上标准。

2026-10-10：PM 依据 r1 独立 `qa_blocked` 及只读来源核对形成 r2 draft；仅此最小补迁等待 Human Owner
精确范围批准。r1 的“批准”不扩展为 r2 批准，r1 未最终验收；r2 暂未授权 Development 写入。

# r1 历史批准规格（以下原文完整保留）

Task ID: ARCH-FE-003
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已明确批准精确 ARCH-FE-003 r1；交 Development 按本 Revision allowlist 实施并创建 tasks.md，developer_handoff 后交 fresh-context Verification

Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 五个用户已复制模块与现有前端 Registry 的 manifest、导航及标题兼容
Owner: frontend-js Core 模块框架
Related Task: ARCH-FE-002, ARCH-FE-004
Depends On: ARCH-FE-002 owner_accepted r4 的现有 Registry、页面权限与 dashboard/plan 接入基线
Acceptance Chain Reference: ARCH-FE-003 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-10
Updated: 2026-10-10

# 目标与现状

Human Owner 已手动复制 auxiliary、performance、monitor、equipment、quality、maintenance 六个模块，
并已自行完成 auxiliary manifest 适配，要求协助调整其余模块。本任务只修正其余五个 manifest 的
当前 Registry 合同及必要静态标题，不把这次接入扩展为全部业务页面、依赖或 API 迁移。

写入前已读取根 AGENTS、README/PLAN pairs、canonical workflow、pm.toml、frontend README/PLAN
pairs、app README pairs、plans 目录手册及 ARCH-FE-002 完整三文件。002 r4 已独立通过并由
Human Owner 接受；当前 host 权限保持 supervisor 3 / operator 2，Docker dev 0 / 0。
002 历史旧授权不构成本任务恢复授权的依据。ARCH-FE-004 r3 已接受，其工作树变更仍需保留。

当前五个 manifest 仍使用旧全局 `breadcrumb.*` / `nav.*`，缺少显式 enabled 与自动导航 metadata。
当前 MainLayout 通过 ModuleNavigation 消费 Registry；旧版
`vibe-l2-front-end/frontend-next-js/src/layouts/MainLayout.vue` 仅用于核对图标和可见页面。
分组顺序继续以现有 module order 为准，不复制旧版手写菜单 DOM 顺序。

# 范围与需求

## R-001：五个 manifest 按现有合同接入

- performance、monitor、equipment、quality、maintenance 显式 `enabled: true`，新增模块 navigation，
  module title/parent title 使用各自既有 `<module>.title`；保留具名导出及原模块 name/order。
- 保留所有 route path、name、pageId、component import、原 routes 数组及其他既有 metadata。
  普通页面显式声明 `meta.navigation.visible: true`、有限 numeric order 和表中 icon。
- 两个带参数详情页显式 `visible: false`，仍注册并受各自 pageId 权限检查；不得制造无参数详情入口。
- 新格式 titleKey/parentTitleKey 必须由所属模块的中英文 namespace 提供。manifest 保持静态、无副作用。

| 模块 | 保留 module order | group icon | group titleKey |
| --- | --- | --- | --- |
| performance | 30 | DataLine | performance.title |
| monitor | 40 | Monitor | monitor.title |
| equipment | 50 | Monitor | equipment.title |
| quality | 70 | CircleCheck | quality.title |
| maintenance | 90 | Notebook | maintenance.title |

以下 path 均为 manifest 内相对 path；name 与 component 路径沿用当前源码。

| pageId | 保留 path | titleKey | 侧栏 order / icon |
| --- | --- | --- | --- |
| performance.list | performance/list | performance.list | 10 / List |
| performance.split | performance/split | performance.split | 20 / Scissor |
| performance.print | performance/print | performance.print | 30 / Printer |
| performance.quality | performance/quality/:id | performance.modules.qualityControl | 隐藏 |
| performance.efficiency | performance/efficiency | performance.modules.efficiency | 40 / TrendCharts |
| monitor.realtime | monitor/realtime | monitor.realtime.menu | 10 / Monitor |
| monitor.temperature | monitor/temperature | monitor.temperature | 20 / TrendCharts |
| monitor.energy | monitor/energy | monitor.energy | 30 / Cpu |
| equipment.production-parameters | equipment/production-parameters | equipment.productionParameters | 10 / DataLine |
| equipment.drive | equipment/drive | equipment.drive | 20 / Odometer |
| equipment.temperature | equipment/temperature | equipment.temperature | 30 / Operation |
| quality.list | quality/list | quality.list | 10 / List |
| quality.control | quality/control/:id | quality.control.routeTitle | 隐藏 |
| quality.spc | quality/spc | quality.spc | 20 / DataAnalysis |
| maintenance.log | maintenance/log | maintenance.log.title | 10 / Document |

## R-002：必要标题键与用户已有代码保护

- 复用表中既有双语键；仅在 quality locale pair 添加 `control.routeTitle`，中文“质量控制”、
  英文“Quality Control”，供不传参数的面包屑使用。原 `quality.control.title` 的 `{coilNo}`
  插值及业务页面用法保留；不为本任务扫描修复所有业务文案。
- auxiliary 作为用户已适配参考，只读复核，其完整目录保持本任务开始时的内容。
  dashboard、plan、system 与默认关闭的 aiis_demo 均不改。
- 六个目录目前为用户已复制的未跟踪内容；Development 先记录本轮允许文件的内容基线，
  用逐文件增量 diff 区分用户复制内容与本任务改动，不覆盖目录、不重新复制旧 Core。

## R-003：更新真实 Registry 集成断言

- 两份既有测试含 dashboard/plan/system 首批范围的固定断言；只最小更新真实源码 Registry 的
  active modules、route identity、导航和 admin 可达页面预期，增加本次五模块标题/顺序/隐藏详情验证。
- 验证 admin 具有所有已启用有效页面访问权；未获 pageId grant 的 supervisor/operator 不因模块
  enabled 自动获得访问。公开 fixture 可显式授予新 pageId，验证菜单、路由、默认入口共同决策；
  参数详情授权后可达但无侧栏 leaf。未知角色 fail closed，demo 继续不可达。
- 保留原 malformed/duplicate/unknown/disabled/admin-only/subset 与 mode 覆盖负例。
  原 dashboard/plan literal i18n 回归保留；不把它扩展为六模块全量业务整改。

# 精确写入 allowlist 与排除项

Development 仅可修改以下实现面及本任务 tasks.md：

1. `frontend-js/src/app/performance/manifest.js`
2. `frontend-js/src/app/monitor/manifest.js`
3. `frontend-js/src/app/equipment/manifest.js`
4. `frontend-js/src/app/quality/manifest.js`
5. `frontend-js/src/app/maintenance/manifest.js`
6. `frontend-js/src/app/quality/locales/en-US.json`
7. `frontend-js/src/app/quality/locales/zh-CN.json`
8. `frontend-js/tests/module-registry/registry.test.mjs`
9. `frontend-js/tests/module-registry/page-access.test.mjs`
10. `plans/ARCH-FE-003-remaining-module-manifest-adaptation/tasks.md`（批准后由 Development 创建）。

PM 仅写本 spec；checklist.md 仅由 developer_handoff 后的 fresh-context Verification 创建。
主协调者按真实阶段机械同步根/frontend PLAN pairs 与 plans README pairs 的本任务索引；
这不授予 PM 或 Development 修改其他角色文档。角色合同不是平台 ACL 或强制路由声明。

排除业务 views/components/API/mock、共享 MainLayout/ModuleNavigation/router/Registry/locale loader、
权限实现、全部真实与 example env、backend/DB/设备、依赖/package/lock、Docker/Compose/Nginx、
ARCH-FE-004 系统名称/小标题改动及其他任务文件。现有 CODE_INDEX 与其他脏文件不借本任务重写。
不执行 Git stage/commit/push/tag、源码发布、正式 dist 覆盖或部署；不判断用户复制业务已适合公开发布。

# 验收标准

| 标准 | 必需证据 |
| --- | --- |
| AC-001：身份与装配 | 五 manifest 符合 R-001；15 个 pageId、path/name/component 及 module order 与本轮基线相同，module/route/parent titles 均在两语言解析。`pnpm --dir frontend-js check:modules` exit 0。 |
| AC-002：导航与详情 | Registry 自动生成 dashboard、plan、performance、monitor、equipment、auxiliary、quality、system、maintenance 九组，顺序依现有 order；五目标模块共 13 个可见 leaf，表中 icon/order 对应。两参数详情注册但无菜单项；aiis_demo 仍关闭。由真实 Registry 集成断言证明。 |
| AC-003：权限保留 | 三角色与未知角色矩阵通过；当前 host sup3/op2 与 Docker0/0 的既有授权语义不变，新模块不自动扩权；公开 fixture 单独验证新页面 grant/deny、参数详情与默认入口。严格权限负例保留。 |
| AC-004：测试与编译 | `pnpm --dir frontend-js test:modules` exit 0；使用排除真实 env 的公开隔离源码 fixture 执行项目 `pnpm build --outDir /private/tmp/<本任务专属目录>` exit 0，记录命令、退出码和告警。使用既有依赖与锁文件，不安装项目外辅助依赖或改正式 dist。 |
| AC-005：范围审计与交接 | 本轮 diff 限于 allowlist；auxiliary、真实 env、004 及其他既有改动受保护，quality 插值标题未改。`git diff --check` 与任务本地链接检查通过，tasks 列明真实执行结果、遗留问题和临时资源；fresh-context Verification 独立记录 verdict。 |

浏览器仅在菜单/标题渲染仍存在待解风险时，使用 `/private/tmp` 公开隔离 fixture 复核；不输入真实
凭据、不调用真实 backend，不把 fixture 结果当作真实业务 API、生产数据或现场运行验收。
构建若遇到用户已复制业务的缺失依赖、组件或文案问题，记录精确文件/错误与归因，区分本轮 manifest
缺陷和既有业务问题。范围外 blocker 交 PM 新 Revision / 独立任务处理；不得静默扩大 allowlist、
绕过构建或把未完成必需验收记为通过。

# 风险与回退

- opt-in 新格式会启动模块自有标题校验，遗漏键可导致 Registry 初始化失败；以完整 checker 与
  双语集成断言发现。quality 参数标题单设静态键，避免无参数面包屑泄漏插值。
- 用户复制页面可能存在导入、API 或运行时差异；本任务编译与 Registry 接入不证明全部页面业务可用。
  真实 API/CRUD、数据血缘、完整业务 i18n、跨模块依赖整改与公开安全审核保留为后续范围。
- 共享工作树包含用户复制内容和 004 已有差异；只按本轮文件基线反向撤销本任务增量，不 reset、
  删除整个模块或撤销他人改动。实际破坏性回退、发布/部署与资源删除遵守独立授权。

# Handoff、批准与修订历史

Development 必须按 `frontend-ui`（含 FRAMEWORK 的 manifest 合同）与 `i18n-workflow` 实施；
Verification 从 fresh context 读取精确获批 spec、完整 tasks、实现和本轮 diff，按相同适用合同
验证。本次不触发后端、设备、Docker 或完整界面血缘技术工作；超出范围时先回 PM。

2026-10-10：PM 形成 ARCH-FE-003 r1 draft。Human Owner 的“剩下的你帮我调整好吧”确认调整意愿；
草案阶段尚未批准本精确 Revision，未创建 tasks.md/checklist.md 或预填实施、QA 证据。

2026-10-10：主协调者向 Human Owner 提交精确 ARCH-FE-003 r1 范围批准请求后，Human Owner 明确
回复“批准”；主协调者将该真实决定交 PM 记录。本 spec 状态据此改为 owner_approved，Revision、
范围、allowlist、验收和风险保持 r1 原文，交 Development 实施。本次批准不等于 QA verdict、
Human Owner 最终验收、扩权、发布或部署授权。

默认交付链为 PM -> Human Owner 范围批准 -> Development -> fresh-context Verification
-> Human Owner 最终验收；实质范围、allowlist、验收或风险改变须新 Revision 并重新批准。
