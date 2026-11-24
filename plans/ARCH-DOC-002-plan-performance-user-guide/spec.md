Task ID: ARCH-DOC-002
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 等待 Human Owner 批准精确 r1；批准后交 Development 更新手册并自检，再交 fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 计划与实绩列表、字段管理及业务接口的双语操作手册
Owner: AIIS ICS Architecture 计划与实绩模块
Acceptance Chain Reference: 本规格第 5 节及 Development Lifecycle Workflow
Related Task: ARCH-TASK-001, ARCH-TASK-002, ARCH-TASK-003, ARCH-TASK-004, aiis-ics-arch.aw.sma::SMA-008
Created: 2026-11-23 Asia/Shanghai

# 计划与实绩操作及接口手册 r1

## 1. 目标和状态

更新现有计划与实绩交互手册，让页面使用者、第三方接口开发者和 SMA 后续接入人员能够按同一份说明完成字段设置、查单、模拟下单、上报和结果核对。内容只围绕计划／实绩列表、字段管理和业务交互 API，使用易懂说明、流程图和可核对的示例。

手册位于根目录 `docs/`，因为它横跨前端、后端与外部调用方；公开接口合同仍由 `contracts/` 承载。现有 `docs/README.*` 和 `frontend-js/README.*` 已链接此手册，本次不改这些索引。

本文件是待审范围，未获得 Human Owner 对 ARCH-DOC-002 r1 的精确批准。此前对其他 DIRECT 工作的批准不替代本任务批准。现有两个手册可作起点；其未包含最新 `snapshot_auto`，不能单凭旧手册推断当前行为。

## 2. 交付范围

Development 的产品文档写入仅限：

1. `docs/generic-plan-performance-guide.zh-CN.md`
2. `docs/generic-plan-performance-guide.md`

按实际作用域补充和校正两个现有文件，保持中英文关键规则、接口、例子、操作步骤与限制一致。保留有用的原有页面、删除保护、补建及错误说明；重组时保留可用的用户入口。STD 的 `tasks.md` 和 `checklist.md` 由各自角色在对应 gate 创建。主协调按仓库规则维护任务目录状态，不借此修改 `docs/README.*` 或前端 README。

不修改源码、测试、数据库结构或数据、API 合同、SMA 代码／配置和部署资源；不启动、重启或切换服务，不触发真实 PLC／SMA、写入 dev 数据、发消息或推送 Git。若文档正确性需要上述变更，停止扩展并提交 PM 另行处理。

## 3. 功能说明要求

### R01 页面与字段

- 按当前页面说明计划／实绩列表、筛选、详情、计划人工新建、允许的人工编辑和无同号计划时的补建；说明计划与实绩 GET 是各自记录，`hasPlan` 的意义。区分页面登录权限与字段开关。
- 覆盖计划本地、实绩本地、共享字段三组各 100 个槽位。说明稳定字段键、双语名称、类型、单位、槽位、启用／可清空、页面可见／可编辑、列顺序、实绩归属和回写；共享定义相同但两侧的值分别保存。
- 写清新增、单项／批量编辑、停用、重新启用、删除与槽位复用。已使用或使用证据不足时以后端检查为准，停用保留历史并占槽；批量删除有受保护项时整批拒绝。只读 GET 不构成使用；按含字段的配置创建或有效更新任务可能构成使用，即使未提交该字段值。停用或删除前提醒核对外部映射。管理操作须管理员权限。
- 比较 `manual`、`automated`、`order_snapshot`、`snapshot_auto` 四种归属的实绩取值、人工／集成写入和回写条件；后者仅共享字段可用。页面展示开关与接口读写权限分别解释。

### R02 接口速查与写入规则

列出当前已注册路径、方法、用途、参数及登录要求。至少覆盖：

| 场景 | 集成路径 |
| --- | --- |
| 字段定义 | `GET /api/v1/integration/task-field-configs?module=plan` 或 `module=performance` |
| 计划创建或部分更新 | `POST /api/v1/integration/plans/upsert` |
| 查询计划列表或单号 | `GET /api/v1/integration/plans`；`GET /api/v1/integration/plans/by-task/{taskNo}` |
| 实绩创建或部分更新 | `POST /api/v1/integration/performances/upsert` |
| 查询实绩单号 | `GET /api/v1/integration/performances/by-task/{taskNo}` |

不将不存在的实绩集成列表 GET 写成可用接口。列出当前集成任务接口不需前端 Bearer 的边界，区分需要登录／授权的页面、人工编辑和管理员配置接口；以目标环境 OpenAPI 与实际字段配置为准。

说明 `taskNo` 的规范化和同号匹配；首次计划及实绩默认状态、重复提交只更新本次携带的值、缺省与显式 `null`、数值／布尔／字符串的 JSON 类型、生产状态、`created`／`updated`／`unchanged` 和 `data.planSync`。可选 `producerId`、`targetKey`、`fieldConfigVersion`、`observationSeq`、`observedAt` 按现有实现说明：不自动分配目标，不将观测序号或采样时间当成去重和排序裁决。字段值上报未带采样时间时，最近采样时间可能变为缺失；不伪造采样时间。成功处理顺序决定覆盖，`completed` 后有效 `running` 可再次覆盖。

### R03 新归属与可操作示例

- 用同一合成任务演示：计划写入设定温度 `180`；首次实绩 POST 省略字段，实绩继承 `180` 且继承本身不触发字段回写；后续实绩显式上报 `200`，在开启回写及同号计划存在时，两侧读取均为 `200`。再交代关闭回写、首包显式给值、无计划或无初值、计划之后改单、状态完工的预期。
- `snapshot_auto` 首包显式给值优先于继承值，允许实绩集成接口后续写入；未提交的字段保留原值。普通 `order_snapshot` 在创建实绩时复制一次，不能由实绩接口修改或回写；`automated` 不继承计划初值。补建计划不会重做已有实绩的快照。
- Swagger 和普通 HTTP 客户端均应能按文档填写目标地址、`Content-Type: application/json`、已配置的稳定键与请求体。每个 JSON 示例须是完整有效 JSON，说明先配置哪些启用字段、作用域、类型、归属和开关。先用两侧按单号 GET 确认测试号未使用，说明 POST 会创建或更新目标库记录，普通接口不提供测试单删除；示例值与任务号是占位演示，不声称在读者环境已存在。
- 至少提供 MES 下单、CA/FF 查询、SMA／第三方实绩首次及后续 POST、单号 GET 对账、完工状态的可执行或可直接在 Swagger 使用的示例，以及响应中 `data.outcome`、`data.performance.items` 和 `data.planSync` 的关键检查。已配置字段的 GET 响应和写入效果按实际源码／合同说明，不虚构完整回包。
- 说明 `403 task.forbidden / field_owner`、未知或停用字段、类型／空值错误、目标冲突、修订冲突及提交结果未知时的可操作排查；收到 `task.commit_unknown` 或响应丢失先 GET 对账再决定是否重试。

### R04 SMA 交付边界

Swagger 手动发送相同请求只验证后端接口，不能表述成 SMA 已完成投递。手册给 SMA 和第三方的是**后端目标接口与映射要求**：具体任务号、字段键、类型及回读预期；SMA 实际可用的配置、手动执行和持续投递能力，以其当前 [README](../../automation-world/semantic-mapping-agent/README.zh-CN.md)、[PLAN](../../automation-world/semantic-mapping-agent/PLAN.zh-CN.md) 和所属任务事实为准。不得把 SMA-008 的采集事实手动回环写成已完成计划／实绩投递，也不得凭本任务宣称实际联调、现场 PLC 或连续运行已验收。

## 4. 证据和验证要求

Development 在改文档前重新核对当前交付工作树的前端页面和字段选项、后端路由／schema／业务逻辑，以及 [v2 合同](../../contracts/published/http-api/generic-task-workflow-v2/README.zh-CN.md)；涉及 SMA 状态时核对其 README／PLAN 和对应实际任务记录。源码、合同或 SMA 状态发生漂移且无法在两份手册内如实说明时，停止并报告，不擅自改代码或合同。

完成后记录文档路径及实际验证命令与结果，至少验证：中英文关键语义和示例对应；JSON 代码块均可解析，关键样例与 schema、当前接口方法及预期响应一致；文档内本地链接存在；`git diff --check` 通过。只使用离线或任务自有隔离验证；验证不依赖向现有 dev 数据库发写请求。保留其他会话在工作树中的改动。

## 5. 验收和交接

| 编号 | 验收标准 |
| --- | --- |
| AC01 | 两份手册可从原入口访问，中英文范围、内容和操作顺序一致；读者能找到列表、详情与三种字段管理入口。 |
| AC02 | 操作说明覆盖新增、编辑、停用、恢复、删除、批量删除和槽位保护，四种实绩归属与页面可见／可编辑规则无矛盾。 |
| AC03 | 六类集成接口的路径、方法、用途及权限符合当前实现；无虚构实绩集成列表；页面／管理 API 与免 Bearer 的任务集成接口边界清楚。 |
| AC04 | JSON 可解析、字段前提明确，可独立按步骤模拟下单、查单、上报、回写、完工并按单号 GET 核对；已有任务和测试字段的持久影响已说明。 |
| AC05 | `snapshot_auto` 继承、首包显式覆盖、后续回写、回写关闭、无计划与原 `order_snapshot`／`automated` 对比正确；值继承与 `planSync` 状态同步不混淆。 |
| AC06 | 可选元数据、时间、部分更新、清空、生产状态与错误恢复符合当前合同；SMA 尚需依据其所属任务完成投递联调，手册不将 Swagger 手测等同于实际投递。 |
| AC07 | 文档链接、示例解析、合同对照及 diff 检查结果被 Development 如实记录；本次不改实现、配置、真实数据库、设备或服务。 |

精确 r1 经 Human Owner 批准后由命名 Development 实施并记录自检；`developer_handoff` 后由 fresh-context Verification 独立核对本规格、实际文档及证据。QA 结论不等于 Human Owner 最终验收，也不授权 SMA 联调或现场执行。

## 6. 风险、回退和修订

- 运行服务、源码、候选合同和 SMA 功能可能并非同一版本。手册须提示按目标实际 OpenAPI、字段配置和 SMA 任务状态核对，不把本地示例当作产品已部署证据。
- 测试任务及字段可能留下历史和占用槽位；使用未占用的合成名称，通过接口操作，由操作者决定实际目标环境。
- 这是文档修订，回退只对本任务交付的两份手册作定向恢复；不得覆盖并行会话的无关变更。
- r1 草案：PM 整理范围与验收，待 Human Owner 审阅；未创建 Development 或 Verification 的事实记录。
