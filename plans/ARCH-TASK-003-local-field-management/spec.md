Task ID: ARCH-TASK-003
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r2 范围，交 Development 实施和自检
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 计划与实绩本地字段独立管理及原子批量删除
Owner: AIIS ICS Architecture 计划与实绩模块
Acceptance Chain Reference: 本 r2 第 4 节及 Development Lifecycle Workflow
Related Task: ARCH-TASK-002
Created: 2026-11-21 Asia/Shanghai
Updated: 2026-11-21 Asia/Shanghai

# 计划与实绩本地字段管理 r2

## 1. 范围和状态

Human Owner 澄清，本地字段管理应迁入计划管理和实绩管理各自侧栏的二级菜单。现有 r1 明确将两个管理页设为隐藏路由，并从各自列表页按钮进入。r2 把入口改为两个管理员侧栏菜单，并从列表页移除重复入口。

本 r2 仅定义上述导航增量。除本 r2 明确调整的隐藏菜单、列表按钮、菜单顺序和相关验收外，文末完整 r1 的其他页面、字段管理、权限、接口和事务要求仍是本任务依据。Human Owner 已批准精确 r2 范围，交 Development 执行。真实 developer_handoff 后由 fresh-context Verification 独立验证，再由 Human Owner 决定最终验收。

r1 已在 [checklist.md](checklist.md#独立验证-qa2) 记录 QA2 通过，Human Owner 对 r1 的最终验收仍待决定。r2 尚未实施或验证，r1 的 QA 结果不自动成为 r2 的 QA，也不推断两次 Revision 的最终验收。r1 规格及批准记录在本文后部逐字保留。

## 2. 导航调整

- 计划管理侧栏按「计划列表」「本地字段管理」「共享字段管理」排列。实绩管理侧栏按「实绩列表」「本地字段管理」「共享字段管理」排列。此顺序是本 r2 的精确口径，两个字段管理入口为同一层级。
- 两个「本地字段管理」菜单只对已登录 admin 可见，分别指向现有 /plan/local-fields 和 /performance/local-fields，继续使用原 pageId、管理员守卫、页面组件和各自字段范围。两个「共享字段管理」入口与权限维持现有合同。
- 当前列表菜单 order 为 10，共享字段菜单 order 为 20。建议本地字段菜单使用 order 15、Setting 图标，保留已有菜单项的相对顺序和默认登录落点。使用各模块已有的 workflow.fieldSettings 作为路由标题，使侧栏与面包屑显示「本地字段管理」，管理页面主卡仍使用既有的计划/实绩本地字段标题。中英文沿用现有双语键。
- 从计划和实绩列表的顶部操作区移除「本地字段管理」按钮。进入本地管理页后保留既有「返回计划列表」或「返回实绩列表」操作，返回时恢复列表原筛选、分页、列宽并重新读取字段配置和列表。
- 保持原 route name、URL、pageId、权限及现有 grants 语义。管理员从菜单、直达或浏览器前进后退均可访问相同页面。未登录用户、supervisor、operator 及未知角色看不到这两个菜单，也不能经直达 URL 绕过管理员守卫。不能将管理页作为非管理员角色授权项。

## 3. 实施边界

Human Owner 已批准精确 r2，Development 可以按最小必要范围修改以下内容。

| 允许范围 | 用途 |
| --- | --- |
| frontend-js/src/app/plan/manifest.js、frontend-js/src/app/performance/manifest.js | 将原本地字段路由加入各自侧栏，设置顺序、图标和已有双语标题键。 |
| frontend-js/src/app/plan/components/TaskPage.vue | 移除两个列表共用的本地字段管理按钮，清理因此失去用途的引入或状态；保留列表其他行为。 |
| frontend-js/tests/module-registry | 更新与路由、菜单、管理员可见性、默认入口及列表按钮变化直接相关的测试，并增加必要的回归。 |
| frontend-js/README.md、frontend-js/README.zh-CN.md、frontend-js/FIELD_SETTINGS_GUIDE.zh-CN.md、docs/generic-plan-performance-guide.md、docs/generic-plan-performance-guide.zh-CN.md | 将本地字段入口说明更新为各模块侧栏，保留返回列表及其他操作的现有说明。 |
| 本任务 tasks.md、checklist.md | Development 与独立 Verification 分别追加实际 r2 证据，保留 r1 历史。 |
| 根 PLAN.md、PLAN.zh-CN.md、plans/README.md、plans/README.zh-CN.md | 主协调者依实际批准、交接和 QA 状态机械同步索引，保留并行工作。 |

本 r2 不修改后端、API、数据库模型、表结构、Alembic、历史数据、字段定义与业务规则。实际数据库写入、服务切换、部署、发布、Git refs 和设备操作仍须相应授权。不能以本 r2 调整其他模块菜单、现有角色授权或默认页面。若实际实现需要扩大上述文件范围或改变验收与风险，返回 PM 处理新范围。

## 4. r2 验收标准

以下为未来 Development 自检及 fresh-context Verification 的通过条件。

| 编号 | 可观察结果 |
| --- | --- |
| R2-AC01 | 管理员在计划和实绩侧栏分别看到本地字段管理，顺序均为列表、本地字段、共享字段；中文和英文菜单、面包屑、页面主卡名称与既有 locale 一致。菜单点击分别进入原有正确 URL 及本地 scope，重复进入与直接刷新可用。 |
| R2-AC02 | supervisor、operator、未知角色和未登录用户均看不到两个管理员菜单；分别尝试已登录非管理员直达和未登录直达，现有守卫予以拒绝或跳转。原 shared-fields 管理员权限与非管理员不可见保持。 |
| R2-AC03 | 计划和实绩列表顶部均无本地字段管理按钮，其他按钮、筛选、分页、表格与权限保持。菜单进入后返回列表恢复原筛选、分页、列宽并重新读取字段配置和数据；浏览器前进/后退及重载可用。 |
| R2-AC04 | Registry 装配和访问合同通过，管理员默认登录路径仍为原列表，非管理员既有 grants、默认落点、侧栏及其他模块顺序保持。两语言、宽屏及窄屏检查侧栏激活状态、内容无遮挡及实际页面导航。 |
| R2-AC05 | 计划、实绩本地页及两个共享入口的既有管理操作可正常访问。比较实际候选与 r1 QA2 的文件摘要及其后变化，逐项说明可沿用的 r1 证据，并针对受本次改动影响的交互独立复验；不能把旧 QA 直接作为 r2 verdict。 |
| R2-AC06 | 运行前端相关专项测试、pnpm check:modules、角色/路由检查和 pnpm build，检查修改的中英文文档链接。记录命令、退出码、环境限制和既有无关失败。核对正式交付源码与验证候选一致，说明临时资源回收。 |

## 5. 决策和版本记录

| 日期 | 角色 | 记录 |
| --- | --- | --- |
| 2026-11-21 | Human Owner | 澄清本地字段管理应作为计划和实绩的二级菜单入口。 |
| 2026-11-21 | PM | 起草 ARCH-TASK-003 r2 导航增量，等待 Human Owner 对精确 r2 的范围批准。 |
| 2026-11-21 | Human Owner | 明确回复「好的，批准 ARCH-TASK-003 r2，按 STD 开发。计划和实绩都把『本地字段管理』移到左侧二级菜单，放在列表和共享字段管理之间，仅管理员可见。列表顶部的按钮去掉，后端和数据表不动，做完走独立验证。」批准精确 r2。批准前规格 SHA-256 为 4cb5cbb661437150ab93c63d8cd23cf43ec78ee9985ae18dc72bd6bdb0c2c1f7。 |

## r1 已批准历史

以下保留批准前后形成的完整 r1 原文。若其中隐藏路由和列表按钮要求与本 r2 第 2 节冲突，以已获批准的 r2 为准。

Task ID: ARCH-TASK-003
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r1 范围，交 Development 实施和自检
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 计划与实绩本地字段独立管理及原子批量删除
Owner: AIIS ICS Architecture 计划与实绩模块
Acceptance Chain Reference: 本规格第 7 节及 Development Lifecycle Workflow
Related Task: ARCH-TASK-002
Created: 2026-11-21 Asia/Shanghai
Updated: 2026-11-21 Asia/Shanghai

# 计划与实绩本地字段管理 r1

## 1. 目标与状态

管理员从计划列表和实绩列表的「本地字段管理」进入各自独立页面，使用与共享字段管理一致的列表、筛选、分页、单项和批量操作。两页分别管理计划本地字段及实绩本地字段。批量编辑复用当前字段配置保存接口，批量删除由两页共用一个新接口，在数据库事务内完成整批校验和删除。

Human Owner 已确认会话中展示的本地字段管理预览及本任务方向，明确要求采用 STD。预览包含的示例字段、可删除状态与顶部计划/实绩切换仅用于演示，不是实际业务数据或产品导航合同。Human Owner 已批准本 r1 的精确实现和验收范围，交由 Development 创建 tasks.md 并实施；真实 developer_handoff 后，由 fresh-context Verification 创建 checklist.md 独立验证，最后由 Human Owner 决定最终验收。

[ARCH-TASK-002 r1](../ARCH-TASK-002-shared-field-management/spec.md) 的共享字段能力已通过 [QA2](../ARCH-TASK-002-shared-field-management/checklist.md#独立验证-qa2)，其 Human Owner 最终验收仍待决定。之后的共享页面 DIRECT 样式调整按当前工作树处理，不将其写成 QA2 已验证或已最终验收。本任务与 ARCH-TASK-002 分别保有任务范围和验收。实施时以交付工作树的实际源码、未提交改动及旧任务记录为依据，不能覆盖并行工作或把旧 QA 结果冒充新候选验证。

## 2. 当前实现依据

1. [计划与实绩列表](../../frontend-js/src/app/plan/components/TaskPage.vue)复用 TaskPage。管理员可在配置可用后打开 [本地字段管理弹窗](../../frontend-js/src/app/plan/components/TaskConfigDialog.vue)，其编辑表由 [TaskFieldEditor](../../frontend-js/src/app/plan/components/TaskFieldEditor.vue) 承载。列表按模块和用户名保存在本机的筛选、分页等状态，并在加载时同时读取配置和列表。
2. [共享字段管理页](../../frontend-js/src/app/plan/views/shared-fields/index.vue)由计划和实绩两个管理员入口共同使用。当前源码已提供名称拆列、固定右侧操作列、筛选、分页、跨页选择、编辑/删除弹窗、列宽偏好及版本标签。相关逻辑应按本 r1 的适用范围提取复用，并保留共享页行为。
3. [现有字段接口](../../backend/app/task/api/routes.py)通过 GET 的 module 读取当前共享定义及该模块本地定义，通过 PUT 的 module、configRevision 和 changes 保存指定组的一个或多个变化；单项删除使用完整身份与修订号。批量删除现有路径只接受 shared_sync。已保存字段的键、槽位、类型和单位不可直接修改。
4. [字段服务](../../backend/app/task/services/async_fields.py)的计划本地和实绩本地分别使用 plan_local、performance_local。每组槽位 1–100。计划本地无实绩归属。实绩本地归属限定 automated 或 manual，只有 manual 可启用实绩可编辑；本地字段不支持共享字段的回写计划。当前定义和历史使用证据由现有配置、历史快照及使用记录共同保护。
5. 字段版本和配置修订号是同一份全局配置状态。仅名称、可见性及顺序等显示设置变化时，现有保存只推进修订号。业务设置变化、新增或删除发布新字段版本并推进修订号。未发生实际变化时二者不变。单次批量删除成功时应按下述合同发布一次快照并分别推进一次。
6. 现有 GET 不返回字段是否可删。现有单项删除按本地 scope 分别检查计划或实绩及历史下发批次，包含历史定义完整性和使用证据。配置单例是业务写入和配置更新的首个写锁。历史证据本身不可观察的损坏及未知外部调用方不因本任务而变成可自动证明。

## 3. 页面、交互和复用要求

### R01 入口、导航和权限

- 计划列表现有「本地字段管理」按钮进入 /plan/local-fields，实绩列表对应按钮进入 /performance/local-fields。两个地址作为本任务的明确候选路由。继续使用各模块原有标题、面包屑和登录外壳，不通过示例预览中的切换按钮跨模块。
- 两个页面均为 Registry 登记的管理员页面，仅已登录 admin 可访问。按钮按现有管理员和配置可用条件显示；未登录、supervisor、operator 和未知角色不能通过直接 URL、历史记录或手工导航进入。页面访问控制不替代后端管理员授权。
- 两个管理路由不新增侧栏菜单项，管理员经列表按钮进入。页面提供明确的「返回计划列表」或「返回实绩列表」操作，直接 URL 加载、刷新和浏览器前进/后退也能工作。路由及 pageId 采用稳定且互不冲突的模块归属。
- 返回列表时沿用现有按模块和用户名保存的筛选、页码、每页条数与已有列宽偏好，并重新读取字段配置和当前列表。字段变化可立即反映列表动态列。无配置变更的返回也保持原列表状态。只依赖现有本机偏好合同，不新建 URL 参数或偏好格式。
- 新增隐藏管理路由后，不改变默认登录落点、已存在侧栏顺序、活动路由判定与现有 pageId grants。角色配置检查不得把管理员专用页面授予 supervisor 或 operator。需核对自动装配、菜单、授权与正常路由的相关测试及文档。

### R02 主表和筛选

- 两页的主卡标题分别标识「计划本地字段管理」和「实绩本地字段管理」。标题帮助、字段版本/配置修订号胶囊、顶部「新增字段」「重置列宽」「刷新」、筛选和数据表的风格、字号、操作尺寸与当前共享字段管理页面一致。版本信息来自响应，是只读事实。
- 主表每行一个字段，展示选择框、稳定字段键、中文名称、英文名称、槽位、类型、单位、启用状态和右侧固定「编辑」「删除」。实绩页另显示实绩归属，计划页不展示实绩归属。表格数据只来自当前模块对应 scope，包含停用字段，不能混入共享字段或另一个模块本地字段。
- 两页筛选字段键、中文名或英文名（大小写不敏感）及启用状态；实绩页增加自动/人工归属筛选。提供查询和重置、加载失败及重试、空列表和无匹配结果。读取失败时不能将旧数据说成已刷新。
- 客户端先筛选后按槽位升序分页，默认每页 20 条，提供 10、20、50、100 及总数和翻页；选择与当前页全选、半选状态、跨页勾选、筛选及刷新行为与共享页一致。查询或重置筛选清空勾选并回第一页；页大小或翻页保留跨页勾选。刷新后修订号变化则清空选择并提示重新选择，修订号不变时保留仍存在的完整身份。删除或筛选使当前页越界时回到有效页。
- 当前页、批量弹窗中的普通业务列允许拖动并设合理最小宽度，超宽容器局部横向滚动；选择和操作列可固定。使用项目公共列宽工具，计划主表、计划批量表、实绩主表、实绩批量表和共享字段各表的本机偏好分离；按钮为「重置列宽」，提示为「恢复默认列宽」。已存本地弹窗列宽在语义相同且键合法时可复用，失效或结构变更项按默认回退，不能把一个模块的偏好应用到另一个模块或改写业务配置。
- 使用中文和英文 i18n，键结构对称。浅色、深色、宽屏和窄屏均可操作；帮助、筛选、表头选择、分页、弹窗及按钮可通过键盘操作。版本标签色彩使用现有主题 token。

### R03 新增、单项编辑和批量编辑

- 顶部「新增字段」打开单字段弹窗，行内「编辑」只打开所选字段。确认前为草稿，取消或 Esc 关闭不写入。弹窗右下角为有间距的「取消」「保存」，取消入口不与右上角关闭按钮重复；保存中禁止关闭和重复提交，错误恢复后保留草稿。批量编辑及删除确认弹窗采用同样的右下角布局和键盘原则。
- 单字段弹窗按对应组展示字段键、槽位、类型、中英文名、单位、启用、可清空与该模块可见、可编辑及列顺序。实绩页还提供自动/人工归属及适用联动。计划页不提供实绩设置；实绩页不提供计划设置。共享回写及订单快照不适用于本地字段。
- 新建建议当前模块的空槽，提交前检查该 scope 的完整字段集合，包括停用、未显示和其他页。占用槽无论填同名或异名都不得发送 PUT，保留草稿并提示；其他 scope 的同号槽不算本组占用。稳定键还须遵守现有同模块共享键与本地键不可重名、保留名、类型和长度规则；两模块本地键可按既有合同同名。并发修改由 configRevision 冲突处理。
- 已保存字段的稳定键、槽位、类型和单位只读。启停、归属、编辑权限、可见与顺序遵守现有语义。停用保留历史值。实绩归属切为自动时，实绩可编辑关闭且不可勾选；切为人工后允许选择是否可编辑。空顺序沿用按槽位的既有含义，显式清空 null 与未修改必须区分。
- 勾选后的「批量编辑」展示所选全部字段的逐行草稿，包括跨页选择；只显示本模块适用设置。一次 PUT changes 只包含当前选中且实际变化的定义。单项编辑只提交当前字段的变化，其他组和未勾选字段不被提交。无变化不推进版本或修订。PUT 按现有合同处理权限、校验和修订冲突。
- 保存或删除期间保留相应输入和选择。权限/校验错误或修订冲突显示原因并保留草稿供用户核对。取消草稿后用户可刷新权威配置并重新编辑；不得静默覆盖并发变更。读取失败允许重试，不能把未加载或旧配置当成已更新。

### R04 删除和结果核对

- 单项「删除」使用现有单项接口。批量删除对所选全部身份展示二次确认，确认前不写入，确认后以一次新接口请求提交当前组。确认内容指出字段身份和数量，提示人工核对系统外 MES/SMA 等映射。
- 任一字段不存在、身份不匹配、存在受保护使用或历史证据不足，或 configRevision 冲突时整批不生效。后端按请求顺序返回首个可定位阻塞项，界面显示实际返回的身份和原因，保留已选项供调整或重新确认；全局历史问题不伪称特定字段可删。不能根据 GET 预先给出已验证的可删除状态。
- 网络中断、响应丢失或 task.commit_unknown 表示结果未明。前端禁用重复提交，保留待核对身份及编辑草稿，重新读取权威配置、版本与修订，显示字段是否存在及本次提交的属性是否与当前值相符。不得把当前事实直接推断为该请求成功或失败，也不得自动重放。读取失败时显示无法核对，用户可重试读取后自行决定下一步。
- 成功删除后刷新当前组的列表和版本、移除已删除选择并修正分页。保存成功后重新读取或采用权威响应。无论从哪一个页面返回，两组及共享定义均按实际返回呈现。

### R05 复用与兼容

- 从现有共享字段管理实现中提取或参数化真实共用的主表、筛选/分页/选择、编辑与确认弹窗、列宽和版本反馈。计划、实绩和共享三种模式共用这些能力，并由显式 scope 决定差异。不得逐页复制三套维护逻辑或将本地请求误发为 shared。
- 计划及实绩共享字段原有路由、菜单、读写权限、筛选、主表、编辑/批删、独立列宽、错误和未知结果处理继续可用。保存/删除后版本规则、历史保护和目标组行为继续遵守现有合同。
- 原计划/实绩列表筛选、分页、列宽、业务详情、新建/补建和权限行为继续可用。旧本地字段弹窗入口迁移后不得保留同一按钮再打开另一套旧编辑流程。TaskFieldEditor 中仍被共享批量编辑使用的部分需保留兼容；可以删除因本任务而无调用者的旧本地弹窗代码，不能删除其他现有职责。

## 4. 本地字段原子批量删除接口

路径相对 /api/v1。新增 POST /task-field-configs/local/batch-delete，只供已登录管理员使用，沿用 task HTTP 响应与错误信封。此接口是本 r1 待批准的具体合同。

### 4.1 请求

~~~json
{
  "module": "plan",
  "configRevision": "14",
  "fields": [
    { "scope": "plan_local", "slotNo": 2, "name": "workNote" },
    { "scope": "plan_local", "slotNo": 4, "name": "workInstruction" }
  ]
}
~~~

- module 只能为 plan 或 performance。plan 请求的所有 scope 必须为 plan_local，performance 请求的所有 scope 必须为 performance_local，拒绝 shared_sync、跨模块混合、空缺或额外字段。
- configRevision 是现有正整数十进制字符串；fields 长度 1–100。每项必须包含 scope、严格整数 slotNo（1–100）及符合现有稳定键语法的 name。重复槽位或重复身份、数组为空、超过上限、额外键或类型错误均返回 422 task.invalid_request，整包不写入。
- 请求范围和每项身份必须匹配，不能由槽位或名称猜测。请求顺序定义返回的 deleted 顺序和错误索引。GET、PUT、单项删除及 shared 批量删除的路径、输入/输出、作用域和已有调用方继续兼容。

### 4.2 成功响应

~~~json
{
  "code": 200,
  "message": "success",
  "data": {
    "outcome": "deleted",
    "deleted": [
      { "scope": "plan_local", "slotNo": 2, "name": "workNote" },
      { "scope": "plan_local", "slotNo": 4, "name": "workInstruction" }
    ],
    "configVersion": 15,
    "configRevision": "15"
  },
  "timestamp": 1795170000000
}
~~~

实绩请求及响应以 performance_local 表示；数字和字段名称是合成示例。成功返回完整的已删除身份及最新版本，仅发布一次完整配置快照，版本和修订号各加一次，记录有界管理员审计事件。未选定义、另一模块和共享定义保持现值及相对身份。历史快照、使用证据、计划/实绩业务值和历史下发记录保留，成功删除的当前槽位按原规则可重新使用。

### 4.3 失败与事务

- 未登录返回 401 task.unauthenticated，非管理员返回 403 task.forbidden。请求格式或 module/scope 不一致返回 422 task.invalid_request。当前完整身份不存在或不匹配返回 404 task.not_found，修订过期返回 409 task.config_revision_conflict，已用或证据不足返回 409 task.field_in_use。
- 继承 ErrorEnvelope 的字符串 details。可定位到请求项时使用零基路径 fields.N.name 或 fields.N.scope 及稳定 reason；重复槽位可使用 fields.N.slotNo。全局历史完整性问题的 field 可为 fields，并沿用相应原因码。按请求顺序只需返回首个阻塞项，不暴露未验证项的可删除资格。
- 服务在一次事务中先锁当前配置单例，再依现有锁序检查修订、当前身份、历史快照及各字段使用证据。计划本地检查计划和历史 dispatch，实绩本地检查实绩和历史 dispatch。全部通过后才一次发布快照并提交。不能循环调用单项 HTTP、逐项提交或先删可用项。
- 校验、保护、已知提交前错误及回滚不得留下部分字段删除、部分新快照或额外版本/修订。并发计划或实绩写入、字段保存、单删、共享批删及本地批删时，结果与某个串行提交顺序一致，不能删掉已经按其定义被有效使用的字段。
- 提交结果未知返回现有 503 task.commit_unknown。该状态不代表服务端一定回滚，客户端执行 R04 核对。其他服务不可用沿用 task.unavailable。后端每个事务只能全部提交或全部不提交。
- 不增加资格预检接口，也不更改数据库模型、字段、DDL、Alembic 或历史数据。

## 5. 实施范围与排除项

经 Human Owner 批准精确 r1 后，Development 在实际需要的最小范围内可修改以下文件或目录。

| 范围 | 授权用途 |
| --- | --- |
| frontend-js/src/app/plan、frontend-js/src/app/performance 的 manifest、views、components、api、locales | 两条模块路由、入口及范围参数、共享组件抽取复用、页面/弹窗、接口调用和中英对称文案。按实际引用处理旧本地弹窗；保留共享页及本地以外的行为。 |
| frontend-js/src/app/moduleManifest.js、frontend-js/src/config/pageAccess.js、frontend-js/scripts/check-module-manifests.mjs、frontend-js/scripts/check-page-access.mjs | 仅当隐藏管理员路由的登记、默认入口、权限检查或正常装配确实需要时修改；不能放宽其他路由的权限。 |
| frontend-js/tests/module-registry | 本任务所需的页面、路由、注册、权限、状态和回归测试。 |
| backend/app/task/api/routes.py、schemas/fields.py、services/async_fields.py | 本地批删的请求、响应、路由与事务服务，安全复用原保护。仅为兼容验证所需时调整本任务直接关联的错误适配。 |
| backend/tests/test_generic_task_*.py、backend/tests_mysql/test_generic_task_*.py | 本任务接口、隔离和并发所需测试。 |
| contracts/published/http-api/generic-task-workflow-v2 | 双语 HTTP 合同、注册后的 OpenAPI 快照和合成请求示例。 |
| docs/generic-plan-performance-guide.md、docs/generic-plan-performance-guide.zh-CN.md、frontend-js/FIELD_SETTINGS_GUIDE.zh-CN.md、frontend-js/README.md、frontend-js/README.zh-CN.md | 只更新本地字段入口、操作和接口相关说明，保留其他工作中的变更。 |
| CODE_INDEX.md | 有新增源码或真实结构变化时，仅更新对应条目。 |
| 本任务 tasks.md、checklist.md | 分别由 Development 与独立 Verification 在实际 gate 创建和维护。 |
| 根 PLAN.md、PLAN.zh-CN.md、plans/README.md、plans/README.zh-CN.md | 主协调者按真实 gate 机械同步索引并保留并行改动。 |

本任务不含数据库模型、表结构、迁移及既有数据库历史数据变更；不授权对现有 dev 或生产数据库执行写入、真实字段删除、服务切换、部署、发布、版本 refs 或现场设备操作。测试仅使用本任务专属隔离数据与实例。Docker up/down/build 和其他受仓库契约约束的外部操作须有对应具体授权。现有共享字段和本地字段的业务规则均保持；不扩展自动发现外部映射，也不新增与任务无关的页面及功能。

临时源码副本、构建与数据库必须标明归属、用途、实例身份和清理条件。若使用隔离候选，交付前整合至正式工作树并核对内容、构建和实际入口。必要结论写入对应角色文档，不能只留在临时目录。

## 6. 风险和恢复

- 配置单例由三个组共用，批量删除须严格核对 module/scope，保证其他组不会因同名或同槽被删除。一次保存或删除可能使另外页面持有的修订过期，必须明确提示并保留草稿或选择。
- 现有使用保护包括按包含字段的配置进行有效任务创建/更新，即使字段未赋值或已停用仍可能构成使用；历史 dispatch 也参与检查。若历史证据不完整，沿用保守拒绝。系统不能发现全部外部映射，应由操作者确认。
- ARCH-TASK-002 QA 已记录不可观察的历史证据损坏限制。本任务不能保证重建不可观察的事实。必须在测试中区分有效的拒绝证据和无法判定的信息。
- 权限、隐藏路由及组件复用可能影响已有菜单、登录默认页、共享字段和列表筛选状态。以真实入口及 Registry 回归覆盖，不能只以静态组件渲染代替。
- 未部署时可撤回本次源码差异而不覆盖其他并行工作。若以后在获授权环境已提交字段变更，恢复须先只读核对当前版本及影响，另行确定具体处理，不以源码回退覆盖业务数据。

## 7. 验收标准

以下为未来 Development 自检和 fresh-context Verification 条件，不表示本规格已执行产品验证。

| 编号 | 可观察结果 |
| --- | --- |
| AC01 | 管理员从计划/实绩列表按钮进入各自独立路由；直接访问、刷新、前进/后退和返回列表均正确。返回时恢复原列表筛选、分页及列宽，重新读取字段配置和列表，显示更新后的动态列。两页仅管理员可访问。未登录、supervisor、operator 和未知角色被现有守卫拒绝；后端独立拒绝非管理员写操作。 |
| AC02 | 两新页面不增加侧栏项，不改变默认登录落点、现有 grants 与菜单顺序。模块自动装配、隐藏路由和 pageId 的合法性及双语 title 均通过。两个既有共享入口与计划/实绩列表业务操作回归。 |
| AC03 | 每页只展示对应 scope，含停用项，筛选、组合条件、空态和失败重试正确。中文/英文名称为独立列，实绩有归属，计划无归属；主表操作固定在右侧。界面在中英文、明暗主题及桌面/窄屏下不重叠，键盘可完成关键操作。 |
| AC04 | 至少 21 项测试默认 20 条、10/20/50/100 页大小、总数及页码收敛。表头只选本页，跨页勾选进入批量操作；查询/重置清空勾选，翻页和改页大小保留勾选。刷新同修订保留有效选择，新修订清空选择并提示。四张本地表与共享表列宽隔离、拖拽、刷新/切页/重启恢复及各自重置。 |
| AC05 | 新增、单项和批量弹窗设置及保存正确。两个 scope 的占用槽同名/异名、停用及被筛掉字段均阻止 PUT 并保留草稿；另一 scope 同槽不误阻止。对共享键重名或非法键保留既有后端拒绝。空槽新增、已存字段单项编辑、跨页选中项批量变化和显式 null 均正确。 |
| AC06 | 实绩只有 automated/manual，只有 manual 可实绩编辑，自动时关闭该开关；计划无归属及实绩开关，两页均无共享回写。已存身份只读，停用保留历史值。显示类修改只加修订，业务设置/新增加版本和修订，无变化二者不变。 |
| AC07 | 每个页面调用原 GET/PUT/单删及一个新批删接口，批量操作仅发送所选本组身份。两组分别测试 1 项、多项及 100 项成功，核对完整响应、顺序、一次快照、版本/修订各加一次、其他组及既有数据不变。 |
| AC08 | 未登录、非管理员、坏 module/scope、混组、shared、重复、空/超限/非法数据、错误身份、过期修订均按合同拒绝并保持全量状态。原 shared 批删继续只接受 shared_sync，单删和所有现有路径及信封兼容。 |
| AC09 | 对计划/实绩已有引用、无值但已使用、停用但已使用、历史 dispatch 引用、历史定义不完整、使用证据缺失和可删项混合，以不同顺序测试整批拒绝。验证错误定位、实际原因及不推断其他字段资格，其他模块和共享组不受影响。 |
| AC10 | 以任务专属隔离 MySQL 8.4.6 验证本地批删与本模块任务创建/有效更新、配置保存、单删、共享批删以及另一模块批删的先后顺序。证明真实配置首锁等待、串行一致性、无误删和提交前故障回滚；记录目标身份、版本、时区与清理。隔离实例不可用则记录 blocker，不能用 SQLite 冒充 MySQL 并发通过。 |
| AC11 | 注入修订冲突、保护拒绝、提交前失败、响应丢失和 task.commit_unknown，确认无自动重放或部分删除，保留/展示草稿及身份，重新读权威配置供核对。新增、单项编辑和批量编辑的未知结果也需覆盖。 |
| AC12 | 运行项目锁定环境的后端定向测试、前端专项、pnpm check:modules、pnpm test:modules 和 pnpm build，核对公开合同、OpenAPI、示例和文档链接。记录真实命令、退出码、既有无关失败及限制，核对正式交付树与验证候选一致并回收本任务资源。 |

Development 和 Verification 按角色分别使用 frontend-ui、i18n-workflow、backend-arch、code-document-indexer、project-governance 与 aiis 的适用部分。前端可见内容接入既有 locale，后端接口/业务规则归 task 模块，公开合同归 contracts。测试独立性、角色权限和每项证据按 canonical workflow 记录。

## 8. 批准口径与版本记录

本 r1 固定两个管理员隐藏路由、列表返回操作、20 条默认分页和一个本地批删接口。字段数量、错误处理及事务规则以第 3、4、7 节为准。

| 日期 | 角色 | 记录 |
| --- | --- | --- |
| 2026-11-21 | PM | 根据 Human Owner 确认的界面方向和当前源码起草 ARCH-TASK-003 r1；等待对该 Revision 的范围批准。 |
| 2026-11-21 | Human Owner | 明确回复「批准 ARCH-TASK-003 r1，按 STD 开始开发。批量删除只给登录的 admin 用，数据表不动，做完走独立验证。」批准精确 r1 范围。批准前草稿 SHA-256 为 `600aca42713edaea46122b481cdc2c6eaa80dbd2ed8df715a9b1b33f8645c72e`。 |
