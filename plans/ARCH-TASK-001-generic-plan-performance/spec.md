Task ID: ARCH-TASK-001
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r3 开发范围，交 Development；实际 dev 数据库、私有 profile/证明及服务操作须按具体步骤另行批准。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 通用计划与实绩、当前字段配置和同号实绩回写
Owner: AIIS ICS Architecture 计划与实绩模块
Acceptance Chain Reference: 本规格第 5、6 节、r2 第 8、9 节及 Development Lifecycle Workflow
Related Task: ARCH-ACQ-003, ARCH-ACQ-004, ARCH-BE-010, ARCH-BE-011, ARCH-OBS-001
Created: 2026-11-18 Asia/Shanghai
Updated: 2026-11-18 Asia/Shanghai

# 通用计划与实绩 r3：后继迁移的受保护接口兼容规格

## 1. 范围、基础与状态

Human Owner 已批准 **ARCH-TASK-001 r3** 的精确开发范围。r3 在完整 r2 规格上，仅补充本任务 Alembic 后继对三个既有版本门禁的兼容、定向验收及切换条件；r2 的计划/实绩业务要求、API 示例、角色权限、原有允许范围及 R2-AC01–AC15 验收均不改变。下方 [r2 完整原文](#r2-已批准历史) 中除当时的状态、交接措辞和 r2 原允许范围须结合本 r3 增量外，其余业务与验收均是 r3 的执行依据；r3 的批准来自下方独立记录，而非从 r2 历史中的 `owner_approved` 推断。

Human Owner 于 2026-11-18 批准精确 r2 开发范围。Development 已开始临时候选，因采集版本保护超出 r2 允许路径而暂停并记录 `dev_blocked`，尚无 r2 `developer_handoff`；前端、定向回归、合同及实际 dev 操作尚未完成。[Development 记录](tasks.md) 中的候选与离线自检不构成 r2 或 r3 QA。r1 第四次交接由 [QA4](checklist.md#qa4-独立验证) 记录 `qa_passed`，r1 的 Human Owner 最终验收仍待决定。r2 和其中完整嵌套的 r1 原规格及批准记录均按原字节保留于文末。

PM 本轮仅写本 `spec.md`；任务索引由协调者按实际状态机械同步。本次批准记录不修改源码、测试、`tasks.md`、`checklist.md`、运行配置、数据库或服务。r3 已获开发范围批准，尚未完成实施或验证，现交 Development 继续。本任务仍使用用户选择的**现有 dev 库**进行后续获准验收，不要求另建隔离库。精确 r3 范围批准不自动授权实际数据库写入/迁移、私有目标配置或采用证明变更、服务切换或设备操作；这些须先提交具体方案并逐项明确批准，r1/r2 既有环境授权不自动延续。

## 2. 只读源码依据

1. Development 的 r2 临时迁移候选为 `ae20b4d6f831`，前驱为 `9d1f3a5c7e20`，尚未执行。当前正式工作树内 Alembic 迁移静态扫描得到单一源码 head `9d1f3a5c7e20`，未发现 `ae20b4d6f831` 占用；这不是对现有 dev 数据库 head 的确认。实施和切换前仍须重查正式工作树、前驱及 ID；若发生冲突或 head 变化，停止并返回 PM，而不是擅自换 ID 或改前驱。
2. [PLC Facts v2 配置](../../backend/app/plc_facts/v2_config.py) 的 `ALLOWED_REVISIONS` 当前为 `7b9d1f3a5c7e`、`8c0e2a4d6f18`、`9d1f3a5c7e20`。配置加载及[异步目标守卫](../../backend/app/plc_facts/crud/async_v2.py)和[同步维护守卫](../../backend/app/plc_facts/crud/sync_v2_maintenance.py)均要求目标 revision 在白名单中，守卫还要求实际数据库 revision 精确匹配。若同库目标启用 PLC Facts v2，迁移后沿用旧 profile 将因不匹配而未就绪；仅把 profile 改成候选 revision 也会因白名单拒绝而未就绪。由此会影响 r2 对采集接口保护的验收。
3. [设备观测 profile](../../backend/app/equipment_observation/profile.py) 当前只允许 `8c0e2a4d6f18`、`9d1f3a5c7e20`；[目标守卫](../../backend/app/equipment_observation/services/guard.py)同样要求目标与实际 revision 精确一致。profile 对 `9d1f3a5c7e20` 额外要求每台设备显式提供 `staleAfterSeconds` 和 `futureToleranceSeconds`。仅将新 ID 加入列表而不延续此要求，会使该后继绕过现有时序约束。
4. [业务时间采用凭据](../../backend/common/integration/storage.py) 的 `ALLOWED_SCHEMA_REVISIONS` 也不含候选 revision；已采用的 equipment、monitor 等路径还要求采用证明中的 `serverUuid`、`schema` 和 `schemaRevision` 与实际目标精确相符。公共解析器还支持 performance 的历史采用格式；这不恢复已退役的旧实绩集成入口。旧证明不会因为白名单扩展而自动匹配新数据库 revision，不能擅自改写或伪造采用证明。

以上是源码与 Development 记录中的条件性影响，尚未核实现有 dev 的三个功能开关、目标 profile、采用证明或实际数据库状态，不能据此称已发生故障、完成实库测试或接通设备。

## 3. r3 唯一实质范围增量

在 r2 第 8 节已有允许范围和角色归属基础上，**额外允许以下三个精确源码文件**，仅为 `ae20b4d6f831` 实现版本兼容，保留 r2 全部其他边界：

| 文件 | 允许的最小修改 |
| --- | --- |
| `backend/app/plc_facts/v2_config.py` | 仅在 `ALLOWED_REVISIONS` 增加 `ae20b4d6f831`，保留原有三个 revision；不更改配置结构、开关、来源登记或权限。 |
| `backend/app/equipment_observation/profile.py` | 在 `REVISIONS` 增加 `ae20b4d6f831`；只将原本针对 `9d1f3a5c7e20` 的两项设备时序参数必填条件扩展到该新 revision。旧 `8c0e2a4d6f18` 和 `9d1f3a5c7e20` 的行为分别保持。 |
| `backend/common/integration/storage.py` | 仅在 `ALLOWED_SCHEMA_REVISIONS` 增加 `ae20b4d6f831`，保留所有原有 revision；不改变采用证明的结构、证据校验、目标匹配或时间转换。 |

上述增量不改 `plc_facts/crud/async_v2.py`、`plc_facts/crud/sync_v2_maintenance.py`、`equipment_observation/services/guard.py` 或 equipment/monitor 的目标探针；它们继续通过现有共享常量执行原校验。MySQL 8.4、服务器 UUID、schema、上海时区、唯一且匹配的 Alembic revision、设备观测原有机器凭据与授权范围、人工访问权限、PLC Facts 现有来源准入和管理权限均不降低。PLC Facts 现行开发合同中本来免 Bearer 的样本/查询接口及需管理员权限的管理入口分别保持原样，本任务不统一改造成另一种认证。

对应定向测试可在 r2 已列入的 `backend/tests/**`、`backend/tests_mysql/**` 范围内增补；原 r2 的任务实现、迁移、前端、合同及文档允许范围不变。`LEGACY_REVISION` 所代表的旧来源配置导入属于历史格式，不因本任务扩展。若发现仍需修改第四个原 r2 未授权的源码文件、改变校验语义、扩大数据或设备范围，应停止该部分并返回 PM 审阅，不把本清单扩展成目录级许可。

Development 按已获批准的精确规格和实际工作树工作；后端使用 `backend-arch`，前端继续按 r2 使用 `frontend-ui` 与 `i18n-workflow`，真实结构变化按 `code-document-indexer`。角色文档及根索引仍依 r2 所列角色权威和主协调者机械同步边界办理。精确 r3 已获批准，交 Development 在所列范围内继续；实际环境操作仍需另行具体批准。

## 4. dev 切换、数据保护与恢复边界

Development 记录显示正常 `8000` 服务使用正式 backend 工作目录，存在源码自动重载影响。Development 应先核对当前运行状态和正式工作树；候选可以在任务所属临时位置准备，但实际向被运行服务使用的源码整合、停服/重启及环境切换，要先给 Human Owner 可审阅的具体操作方案并按仓库规则获明确批准。不能因为只改白名单就触发未经批准的正式服务变化。

申请既有 dev 操作前，应只读核对指定服务器、schema、MySQL 版本、上海时钟、实际 Alembic head、三类相关功能的启用状态、各自 profile 指向的目标及已有业务时间采用证明。记录旧配置/证明的可恢复备份、受保护数据的对账依据、应用与配置的切换次序和维护窗口，以及当前任务的合成输入与保留/清理方案。状态、路径或目标无法确认时暂停，不能假设其中一个功能已关闭、已采用或与本任务同库。

若 PLC Facts 或设备观测在同一目标库启用，迁移到 `ae20b4d6f831` 时，其目标 profile 的 `schemaRevision` 需要与实际数据库 revision 及获批应用保持一致；旧目标版本与新数据库不匹配会继续按原规则拒绝。若设备/监控业务时间功能在同库采用，除源码允许新 revision 外，采用证明与真实目标仍必须按原规则精确匹配；是否需要重新出具或审查证明、依据何种有效证据以及具体操作，须在切换前单独提案并获 Human Owner 明确批准。不得为了通过检查直接覆盖历史证明、将旧证明伪称为新目标已采用，或静默关闭相关功能。

针对获批的具体目标，在受控维护窗口暂停相关写入和受影响服务后，按已审阅方案衔接应用候选、显式迁移及相应目标配置/证明，待源码、数据库和已启用 profile 一致再恢复并验证。各操作、目标和范围须事先取得各自明确授权；此处是待审顺序，不是已执行命令。若版本、目标、时区、保护对象或采用证据不能核对，停止迁移及切换。保护原始事实、设备观测和业务数据，不操作 PLC/DAA/SMA/CA/FF 设备或运行时。

如果切换中断，先停写并辨认数据库、源码、配置和证明的实际状态，保全新旧数据及证据。MySQL DDL 可能非事务性，不盲目重试、降级、清库或只恢复其中一个组件。恢复前提出可审查的数据库/源码/profile/证明一致性及数据对账方案，并另行取得具体批准。仅当迁移尚未执行且能核实无新写入时，才可在获准后恢复原源码与原配置；迁移已经执行时，是否及如何恢复必须根据实际数据和有效备份另行决定。

## 5. 新增可验证验收标准

以下为 r3 的 Development 自检和 fresh-context Verification 要求；目前均未执行，不替代 r2 原验收。无数据库检查可使用合成 profile、目标探针和 fixture；实际 dev 写入、迁移、服务切换及验证应依第 4 节具体授权，不能用会重建或清库的旧 fixture 指向现有 dev。

| 编号 | 操作与通过标准 |
| --- | --- |
| R3-AC01 | 复核正式源码迁移链及候选：单一前驱 `9d1f3a5c7e20`、本任务后继 `ae20b4d6f831`，无重复 ID；三处源码差异仅限第 3 节。旧 r2 的业务要求、示例和 R2-AC01–AC15 继续逐项适用，未授权的其他守卫、模块和真实配置无本任务改动。 |
| R3-AC02 | PLC Facts 使用有效合成目标分别覆盖原三个 revision 和候选 revision：profile 接受，异步及同步守卫在数据库 revision 与目标精确匹配、MySQL/UUID/schema/上海时钟均正确时通过。未知 revision、已知 revision 与数据库不匹配、多 revision、错误数据库类型/版本、UUID、schema 或时区均按原规则拒绝；原禁用开关、来源和管理权限不放宽。 |
| R3-AC03 | 设备观测原 `8c0e2a4d6f18`、`9d1f3a5c7e20` 和候选 revision 的有效 profile 保持可用；新 revision 与 `9d1f3a5c7e20` 均缺任一设备 `staleAfterSeconds` / `futureToleranceSeconds` 时拒绝，`8c0e2a4d6f18` 的原有兼容行为不改变。未知/不匹配 revision、错误 UUID/schema/MySQL/时区，以及无效令牌或缺少设备/区域/指标授权仍依原合同拒绝。 |
| R3-AC04 | 对业务时间采用凭据验证全部原允许 revision 仍保留，并可用 equipment、monitor 及历史 performance 格式的完整合成证据接收新 revision；历史 performance 格式仅验证解析，不恢复退役接口。真实探针或合成探针的 UUID、schema、revision 与证明不一致均拒绝。未知 revision、缺失/错误采用证据、固定列摘要、时间 basis 及其他原校验仍拒绝；设备/监控访问权限和 token 行为不放宽。不能把改写旧证明当成实际目标采用。 |
| R3-AC05 | 审查切换前检查及恢复方案：分别识别目标是否启用 PLC Facts、设备观测、业务时间采用；对于同库启用项，计划 profile/实际 head/有效采用证据的一致处理与独立审批。未采用或关闭的项目不为通过测试擅自开启；状态不明或证据不符须在环境操作前停下。 |
| R3-AC06 | 在具体批准的现有 dev 完成迁移与切换后，按实际启用范围验证采集、设备观测、业务集成的已有允许/拒绝语义及受保护数据前后对账。未获准执行真实环境步骤时，记录精确阻碍，不将其写成实库通过或以源码 mock 冒充真实验证。 |
| R3-AC07 | 运行与范围相匹配的项目锁定后端定向测试、r2 必需回归和前端检查；记录实际命令、退出码、候选与正式树差异、环境以及未授权边界。独立 Verification 在真实 `developer_handoff` 后复核精确 r3，QA 不由本规格、源码静态检查或 Development 自检推定。 |

## 6. 风险、批准与交接

- **多守卫和采用证据风险：** 接受一个新 revision 不代表目标自动采用；每类已启用功能的目标配置/证据仍须与实际数据库一致。当前 dev 启用与采用状态未知，必须在环境操作前确认。
- **运行与数据风险：** 现有服务可能自动重载；数据库 DDL 可能非事务性。候选与正式树、配置、数据和证据必须形成经批准的一致切换及恢复方案，不覆盖其他工作或历史。
- **Human Owner 已批准的开发范围：** r2 全部原业务与验收加本稿三处最小兼容改动、精确后继 ID 及新增 R3-AC01–AC07；实际 dev 操作、私有 profile/采用证明和服务切换仍需之后按具体步骤单独批准。

| 日期 | 主体 | 决定 |
| --- | --- | --- |
| 2026-11-18 | Human Owner | 已批准精确 r2 开发范围；原批准记录与完整内容见下方 r2 原文。 |
| 2026-11-18 | PM | 依据 r2 Development 的暂停记录和当前只读源码核对，提交 r3 兼容范围草案；提交时尚无 r3 批准。 |
| 2026-11-18 | Human Owner | 对精确 `ARCH-TASK-001 r3` 确认问答明确回答「批准 r3，继续开发」。获批草稿 SHA-256：`b62da9696a4641ca159b9dba6501bf2ee75aa139a8683ff8041619660683c893`；实际 dev 环境操作仍按具体步骤另行审批。 |

下一 gate 为 Development 依据精确 r3 继续候选并记录自检；实际 `developer_handoff` 后进入 fresh-context Verification，再由 Human Owner 作最终验收。实际 dev 数据库、私有 profile/证明及服务操作仍须按具体步骤另行批准。

## r2 已批准历史

<a id="7-旧卷材一次性切换"></a>
下方保留含 r1 历史的完整 r2 获批原文件。取引用代码块正文：非空行移除 `> ` 前缀，单独的 `>` 还原为空行，即可逐字节恢复。原文件 105691 字节，SHA-256 `0a18d87f55b80a8c6c0610b8c9104ea30a5fec7ea8b41eeb63b984fb306aa0c8`。原文内 r2 的批准及 r1 的 QA4 和待终验事实仍属各自历史，不是 r3 批准或 r3 QA。

<details>
<summary>展开 r2 完整原文（含 r1 规格及批准历史）</summary>

> ```````markdown
> Task ID: ARCH-TASK-001
> Revision: r2
> Status: owner_approved
> Owner Role: PM
> Allowed Writers: PM, Human Owner
> Handoff: Human Owner 已批准精确 r2 开发范围，交 Development；指定 dev 数据库及服务操作须按具体步骤另行批准。
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Task Namespace: aiis-ics-arch
> Classification: root
> Capability: 通用计划与实绩、当前字段配置和同号实绩回写
> Owner: AIIS ICS Architecture 计划与实绩模块
> Acceptance Chain Reference: 本规格第 8、9 节及 Development Lifecycle Workflow
> Related Task: ARCH-ACQ-003, ARCH-BE-010, ARCH-BE-011, ARCH-OBS-001
> Created: 2026-11-17 Asia/Shanghai
> Updated: 2026-11-18 Asia/Shanghai
>
> # 通用计划与实绩：当前配置与简化集成 r2 规格
>
> ## 1. 目标、背景与状态
>
> MES 或第三方按任务号提交计划；CA/FF 或其他调用方按条件查询计划并自行决定后续现场处理；SMA 或第三方按同一任务号提交实绩。后端保存实绩，在存在同号计划时，同事务同步实绩当前生产状态和本次提交且配置允许回写的共享字段。两条记录也可以分别存在。
>
> Human Owner 已批准 **ARCH-TASK-001 r2 开发范围**；本规格不表示对应 API 已实现，也不是实施结果或 QA 结论。PM 本轮仅修订本 `spec.md`；协调者按任务状态机械同步根 PLAN 和 plans 目录索引。r1 的 dev 切换、合成业务流程、列表和字段设置已有独立 QA；[QA4](checklist.md#qa4-独立验证) 对 r1 第四次交接的 verdict 是 `qa_passed`，Human Owner 对 r1 的最终验收仍待决定。r1 的完整原规格和批准记录附于文末，r1 的 [Development](tasks.md) 和 [Verification](checklist.md) 记录继续是原修订事实；它们不是 r2 的实施或验收证据。索引中保留的 r1 QA4 状态不代表 r2 已实施或通过验证。
>
> 本稿依据最近讨论中用户确认的方向收敛，讨论稿中较早的领取、PLC 回执、版本绑定、完整快照和序号防迟到只作为历史背景；本稿与其冲突时，以本稿经 Human Owner 审阅批准的精确修订为准。[中文讨论稿](../../docs/generic-task-workflow-discussion.zh-CN.md) · [English discussion](../../docs/generic-task-workflow-discussion.md)
>
> ### 拟议业务流程
>
> ```mermaid
> flowchart LR
>     MES["MES / 第三方"] -->|"计划 POST"| PLAN["计划"]
>     CA["CA / FF"] -->|"计划 GET"| QUERY["普通分页查询"]
>     PLAN -. "按条件读取" .-> QUERY
>     QUERY --> FIELD["现场自行处理<br/>模块外"]
>     SMA["SMA / 第三方"] -->|"实绩 POST"| PERF["按任务号保存实绩"]
>     PERF --> MATCH{"有同号计划？"}
>     MATCH -->|有| SYNC["同步实绩当前状态<br/>和本次提交且允许回写的共享值"]
>     SYNC --> PLAN
>     MATCH -->|无| KEEP["实绩正常保存"]
>     KEEP -->|可选| SUPPLEMENT["普通计划 POST 补建<br/>默认不回填历史值"]
>     SUPPLEMENT --> PLAN
> ```
>
> 首次创建实绩时，可按当前字段配置一次性继承已有同号计划的共享订单快照。图中现场处理和各外部系统均为职责示意，不表示已经接入或验证。
>
> ### 相对于现行 r1 的实质变化
>
> | 范围 | r1 已交付或记录的口径 | r2 拟交付口径 |
> | --- | --- | --- |
> | 任务状态 | 计划有领取、回执和下发状态；生产状态较受限 | 只使用固定生产状态 `new`、`running`、`completed`、`error`；查询不领取、不锁定任务，现场处理归调用方。 |
> | 任务写入 | 已有实绩要求专用补建；实绩完整快照、绑定版本和单一登记流 | 两个 upsert 支持部分字段，普通计划 POST 可补建；实绩按处理顺序保存及回写。 |
> | 字段配置 | 任务按绑定版本读写，已保存字段不能物理删除；回写开启时计划侧只读 | 所有任务按当前启用定义读写；回写与计划编辑分别配置；仅从未被适用任务或历史批次使用的字段允许删除并释放槽位。 |
> | 目标和来源 | 目标、来源、字段版本必填并校验登记与绑定 | 选填；目标未知保持空，来源只是标签，版本只作信息；同号目标冲突仍须拒绝。 |
> | 时序 | 实绩按序号/摘要去重、防迟到，完成后拒绝后续新快照 | 不按序号或观测时间排序及去重；后端成功处理顺序决定结果，包括完成后的 `running`。 |
> | 界面 | 共用字段设置弹窗混合共享和本地，显示下发操作 | 两个本地弹窗各管本地字段，共享入口复用同一设置页；旧下发操作停用，保留列表三段及列宽偏好。 |
>
> ## 2. 范围与边界
>
> **纳入范围：** Python/FastAPI 的计划、实绩及共用字段配置；相应表约束和显式后继 Alembic 迁移；计划/实绩前端列表、详情和字段配置；相应 API、源代码自检、使用说明及合同候选；旧任务 API 的兼容停用与历史数据保护。正常网页及集成接口使用相同业务校验。项目时间按 `Asia/Shanghai`、API 时间带 `+08:00`，中英文文案对称。
>
> **排除：** 修改 DAA、SMA、CA、FF、PLC 或 C# 运行时；设备读取、PLC 写入、下发判断和接收回执；真实现场联调、生产部署、账号或其他模块认证改造；过程曲线、报表重建；可靠来源序列、防迟到/去重机制；已有历史数据按猜测时区批量转换。r2 不声明实际链路已接入。原有历史批次、人工动作、任务值、配置版本及其证据必须保留。
>
> PM 本次状态记录不改代码、合同工件、其他任务文档、数据库、服务或配置。精确 r2 已获批准，可交 Development 准备源码和无数据库检查；用户选择**现有 dev 库**进行后续验收，不要求另建隔离库。精确 r2 范围批准不等于现场操作批准：指定目标数据库的迁移或写入、测试数据/配置操作、运行服务切换和设备操作，须在各步骤前按仓库规则取得具体明确批准；r1 已批准的环境操作不自动延续到 r2。
>
> ## 3. 数据、字段和时间合同
>
> **R2-01 任务身份及存储。** `plan_main` 和 `performance_main` 各自以规范化后的 `taskNo` 唯一：去首尾空格、ASCII 英文字母转大写，再校验 1–50 位英文字母、数字、`-`、`_`、`.`；任务号建档后不改，返工使用新号。同号表示业务匹配，不在两张主表间强建外键。每表独立保存 `sync_values` 和 `local_values` 两个 JSON 对象，各最多 100 个逻辑槽位；共享、计划本地、实绩本地分别管理 100 个槽位。槽位用于存储，接口以配置的稳定 `name` 读写。`hasPlan` 是实绩查询的同号派生结果，不是外键或实绩建档条件。
>
> 每个模块内，共享字段与该模块本地字段 `name` 不得重名；计划本地与实绩本地可以同名。键以小写英文字母开头，后续为英文字母、数字或下划线，最长 64 字符，按原样区分大小写；不得与顶层固定字段冲突。定义包含组、槽位、`name`、中英文名、类型、单位、启用、可空、计划/实绩编辑与显示、顺序、实绩归属和共享回写等适用设置。`productionStatus` 是固定系统字段，不能放入 `items` 或作为自定义字段停用。
>
> 值类型沿用 r1 的边界：`string` 最长 255 Unicode 字符并保留前导零；`number` 整数部分最多 10 位、小数部分最多 4 位；`boolean` 为 JSON 布尔值。JSON 值列中有效值按约定保存为字符串，查询时按**当前定义**还原类型。`0`、`false`、`""` 是不同的合法值；未提交表示不改，字段允许清空时显式 `null` 才清空，禁止清空的字段提交 `null` 返回错误。创建时未提供的字段可以无值，即使其不允许后来显式清空；不得把 taskNo-only 新建变成所有字段必填。未知、停用、越权、类型错误、超限或不允许清空的任何一项使整包失败，无部分业务写入。
>
> **R2-02 当前配置与显示。** 每次处理按一致的一份当前配置识别和校验整个 `items`；不按任务原绑定版本或请求携带版本选择字段。普通前端及集成 GET 的 `items` 以 `name` 为键，返回该模块**全部当前启用字段**：从未赋值或已清空返回 `null`，有值按声明类型输出。停用字段在普通 GET 中不输出，但底层历史值保留；原字段重新启用后原值恢复显示。页面另读当前配置取得中英文名、类型、显示顺序和编辑权限；列表可见开关只控制展示列，不改变读写和回写。类型、单位含义、稳定键及已用槽位不得被就地改成另一字段；需要不同含义时新增字段。定义及历史版本应保留足够信息用于正确识别历史使用，不能把旧槽位误解释为新字段。
>
> **R2-03 固定事实和时间。** 两表分别保留创建和实际更新时间 `createdAt`、`updatedAt`。仅该表持久行真实发生变化时更新它的 `updatedAt`；另一表或使用证据发生变化本身不推进该表时间。实绩的 `startedAt`、`completedAt`、`lastObservedAt` 分别是来源确认的实际开工、完工和最近一次采集上报时间；不以接收、保存或 UI 刷新时间冒充。真实开工/完工时间已知时才提交相应时间；省略保留旧值，首次未知为 `null`，不接受显式 `null` 或无时区时间伪造清除。业务时间输入必须是带明确时区、最多六位小数秒的日期时间，转换一次并按上海时间保存、输出 `+08:00`；MySQL 使用 `DATETIME(6)`，页面显示 24 小时制到秒，来源与更新含义分别提示。
>
> 一次实绩集成请求若提交至少一个合法自动采集 `items` 字段，无论该值是否与旧值相同，均视为一次采集上报：带真实 `observedAt` 就把它存为 `lastObservedAt`；省略或为 `null` 时置 `null`，不能把旧时间贴给新上报。仅状态或其他固定字段、`items` 省略/为空且 `observedAt` 未提交时保留原 `lastObservedAt`；此类请求若明确提供有效时间则记录该实际时间，明确提供 `null` 则清空。该时间只描述最近一次采集上报，不证明行内每个保留值同时采到。将旧非空时间清空属于实绩行真实变化，须更新其实绩 `updatedAt`。
>
> ## 4. 写入、继承和同步
>
> **R2-04 计划 upsert。** `POST /api/v1/integration/plans/upsert` 最少只需 `taskNo`。可选 `productionStatus`、`items` 及第 5 节元数据；`items` 省略、`null` 或 `{}` 表示本次没有业务字段，不清空任何值。固定状态提交时只能是四个有效键之一，显式 `null`、空串和未知值均拒绝。不存在则创建：请求显式给状态用本次有效值，否则已有同号实绩继承其实绩当前状态，均无时使用 `new`。已存在则只合并实际提交且允许写入的字段；显式同值重发不更新本行时间。计划状态变化不反向修改实绩。
>
> 先有实绩时，普通计划 upsert 直接创建，不返回旧的 `task.plan_supplement_required`。**默认不复制历史实绩共享值**；后续有效实绩上报再按本节规则回写。按已批准的 r2 口径，创建请求可显式带 `backfillExisting: true`，一次性复制同号实绩中当前启用且开启回写的共享值；缺省或 `false` 不回填。只对尚无计划且已有同号实绩的补建有效；已有计划或不存在实绩时请求 `true` 均返回 `422 task.invalid_request`。本次 `items` 明确提交的计划值始终优先，历史值只填未提交的对应字段。该可选回填不改变实绩订单快照。页面可从实绩详情带入任务号创建计划，但不恢复旧专用补建阻断。
>
> **R2-05 实绩 upsert。** `POST /api/v1/integration/performances/upsert` 最少只需 `taskNo`。不存在则创建，未提交状态默认 `running`；已有实绩未提交状态时保持原状态。每份有效上报均以实绩处理后的**当前** `productionStatus` 检查同号计划并同步，即使本次未提交状态、实绩状态本身不变也必须检查。仅从本次 `items` 中选择当前启用且开启回写的共享字段同步，包括允许清空的显式 `null`；即使实绩的值本身未变，只要计划值不同也须回写。未提交的共享值、任一模块本地值不因本次同步被覆盖；没有计划正常保存，返回 `hasPlan: false`。实绩及计划确有变化的各自更新时间独立更新。
>
> `completed` 后有效 `running` 可以覆盖并同步计划，`error` 也无永久优先级；以最后一次有效处理为准。已有 `completedAt` 在后续 `running` 未提交该时间时保留，它是先前真实完工事实，不代表新的完成。不能因本次状态或字段与实绩原值相同而提前跳过对计划的同步检查。用户通过登录入口编辑有权限的人工反馈字段时，也只同步本次提交且启用回写的共享字段；实绩和计划的实际变化同事务提交。
>
> **R2-06 一次继承和写入归属。** 首次创建实绩时，若同号计划存在，从计划复制当前启用且实绩归属为 `order_snapshot` 的共享订单字段，包括有值的 0、false 和空字符串；无值保持无值。然后处理本次提交。`order_snapshot` 是实绩只读快照，集成或人工请求若直接提交它，整包按字段归属拒绝；若字段归属为 `automated` 或 `manual`，则不属于这一步继承，本次通过对应入口校验的提交值生效。`automated` 由实绩集成入口上报，`manual` 由具有实绩权限且配置可编辑的登录用户填写。计划侧字段启用、登录界面可编辑和共享回写是彼此独立的配置：`syncEnabled` 不自动强制计划侧只读，同一共享字段可以同时允许计划编辑和实绩回写；计划更新不反向改变实绩。补建选择回填时本次计划明确提交值优先，之后有效实绩上报仍可按最后成功处理顺序覆盖该计划值。继承与有效提交不会产生未定义的同字段优先级。
>
> 实绩先创建且没有计划时订单快照可为空。之后新建或修改计划不自动修改既有实绩快照；后续有效实绩上报只按实际提交内容更新允许的反馈。字段当前被停用时不参与继承或写回，重新启用后按照同一字段身份读取保留值。
>
> **R2-07 顺序和事务。** 同一规范化任务号的计划创建/更新、实绩创建/更新与回写必须串行化为等价于某个成功提交顺序；两条并发建档最终每表最多一行。计划先创建、后实绩提交时按实绩回写；实绩先提交、后计划创建且状态省略时继承实绩状态，计划有显式状态则按后一请求生效。并发不得漏掉按该实际顺序应发生的状态同步，不得丢失彼此提交的不同字段。实绩和同库计划回写以及相应字段使用证据必须在同一事务提交；校验失败或事务失败均不能部分提交。若提交结果不明，返回明确的未知结果，调用方先按任务号 GET 对账；本规格不承诺重试去重。
>
> `observationSeq` 可省略或为 `null`；如提供，必须是 1–9007199254740991 的 JSON 整数，只可作为来源诊断信息，不作为先后、幂等或去重依据。`observedAt` 也不控制覆盖顺序。一个迟到的旧包或重试若后成功处理，仍可覆盖较新值与状态并回写计划；上报方应尽量对同任务顺序发送。是否可靠防迟到需另立范围，不能从服务器时间或接收序号推断。
>
> ## 5. 外部 API、权限和示例
>
> **R2-08 元数据与目标。** `producerId`、`targetKey`、`fieldConfigVersion` 均可省略或为 `null`，不作为 taskNo-only 写入的阻断条件。`producerId` 若提供为 1–64 位 ASCII 字母、数字、`.`、`_`、`-`，仅是来源标签，可用于有限诊断，不是身份认证、密钥或目标绑定；空串不等于未知。`fieldConfigVersion` 若提供为正整数，只是调用方附带信息，既不选择旧定义，也不因与当前版本不一致拒绝；响应中的 `configVersion` 是后端本次实际使用的当前版本，不承诺按请求版本读写。
>
> `targetKey` 若提供采用与来源标签相同的字符/长度规则并保留大小写；未知为 `null`，不自动指定产线。新计划省略目标时为 `null`，即便实绩有目标也不自动反向填计划。新实绩省略目标时，继承同号计划已知目标；若无则 `null`。已有记录省略或传 `null` 不清除已存目标，已有实绩为空时也不因一次状态更新自动补填。提交的非空目标若与本记录或同号另一记录已知目标不同，返回 `409 task.target_conflict`，不写任何部分；历史两边已知目标互相冲突时也停下并报告，不任选一个继续回写。需要改变已知目标的情况先由 Human Owner 决定修复方案，不借普通 upsert 静默改写。以上新计划/既有实绩空目标细节为已批准的 r2 具体处理。
>
> **R2-09 入口与权限。** 以下路径相对 `/api/v1`。通用任务集成读写和集成字段配置 GET 暂不要求前端 Bearer token，也不按 `producerId` 或目标登记限制来源；这不改变 DAA 事实、设备或其他接口的认证/准入。前端入口仍要求登录及现有 `plan`、`performance` 授权；字段配置写入和删除仅 admin。`planEditable` 约束经登录的计划人工编辑，后端必须复核；它不是集成方身份授权。计划集成 upsert 可提交当前启用的共享或计划本地字段，仍受类型、空值和全包校验；不因 `planEditable` 或 `syncEnabled` 自动拒绝。实绩集成只接受归属 `automated` 的字段，登录实绩编辑只接受归属 `manual` 且 `performanceEditable` 的字段，`order_snapshot` 不接受直接写入。不要把登录角色、界面编辑开关与免 Bearer 的集成资格当作同一权限。无 Bearer 不是来源可信或网络隔离的证明，实际开放及使用环境仍由项目决定。
>
> | 方法和路径 | 用途和成功结果 |
> | --- | --- |
> | `POST /integration/plans/upsert` | 计划部分更新或创建；`data` 为 `outcome`（`created` / `updated` / `unchanged`）、本次 `configVersion` 和完整 `plan`。 |
> | `POST /integration/performances/upsert` | 实绩部分更新或创建；`data` 为实绩自身 `outcome`、本次 `configVersion`、完整 `performance` 和 `planSync`。 |
> | `GET /integration/plans` | 普通分页查询；可选 `productionStatus`、`taskNo`、`targetKey`、`createdFrom`、`createdTo`、`page`、`pageSize`、`sortOrder`。不要求任务号；省略 `targetKey` 不筛产线。无结果为 200 空列表，无领取、状态变更、字段使用证据或其他写入。 |
> | `GET /integration/plans/by-task/{taskNo}`、`GET /integration/performances/by-task/{taskNo}` | 按规范化任务号返回完整记录；不存在返回 404。 |
> | `GET /plans`、`GET /plans/{id}`、`GET /performances`、`GET /performances/{id}` | 登录列表及详情；列表与集成列表使用同样分页、固定筛选及当前字段语义。 |
> | `POST /plans/upsert`、`POST /performances/upsert` | 登录后的计划创建/编辑、已有实绩人工字段编辑；分别检查现有角色授予和字段可编辑/归属。 |
> | `GET /task-field-configs`、`GET /integration/task-field-configs` | `module=plan` / `performance` 返回共享组及对应本地组的当前定义；登录入口可见停用定义，集成入口只返回启用定义。返回 `configVersion`、十进制字符串 `configRevision`、`fields`；字段项按第 3 节属性给出。 |
> | `PUT /task-field-configs` | admin 保存 `module`（`plan`、`performance` 或 `shared`）、读取时的 `configRevision` 和 `changes`；分别仅能修改所属本地组或共享组。原子合并并返回当前版本、修订及相应完整定义，过期修订冲突。 |
> | `POST /task-field-configs/delete` | admin 提交 `scope`、`slotNo`、`name`、读取时 `configRevision`，按第 6 节事务重查；成功返回 `outcome: deleted`、身份及新的 `configVersion`/`configRevision`。 |
>
> 字段配置项固定包括 `scope`、`slotNo`、`name`、`type`、`labels`（`zh-CN` / `en-US`）、`unit`、`enabled`、`isNullable`、`syncEnabled`、`performanceOwner`、`planEditable`、`performanceEditable`、`planVisible`、`performanceVisible`、`planOrder`、`performanceOrder`；不适用的可空属性返回 `null`。每次有效配置变更推进 `configRevision`；新增、删除、启停及业务规则变化保存完整配置快照并推进 `configVersion`，仅中英文名称、显示与顺序变化不推进业务版本；无实际变更二者均不变。历史快照用于安全使用判定，不控制旧任务普通读取。
>
> 列表 `page` 从 1 起、默认 1；`pageSize` 默认 20、范围 1–100。固定筛选先执行再分页，任务号和目标精确匹配；时间区间 `createdFrom` 含、`createdTo` 不含。`sortOrder` 默认 `desc`，可为 `asc`，均按 `createdAt` 和 `id` 同方向排序。响应 `data` 完整包含 `items`、`total`、`page`、`pageSize`、`totalPages`，空结果的 `totalPages` 为 0。列表 `items` 中每条记录均有下列完整记录字段；固定时间和 ID 不由自定义字段开关控制。
>
> 计划记录为 `id`（十进制字符串）、`taskNo`、`targetKey`、`productionStatus`、`priority`（1–10，默认 5，仅业务信息、不用于领取）、`remark`、`createdAt`、`updatedAt`、`items`。实绩记录为 `id`、`taskNo`、`targetKey`、`productionStatus`、`remark`、`startedAt`、`completedAt`、`lastObservedAt`、`createdAt`、`updatedAt`、`hasPlan`、`items`。计划可选提交 `priority`、`remark`；实绩可提交真实 `startedAt`、`completedAt`。可空备注显式 `null` 清空，省略不改。未知顶层键、无效枚举和错误类型拒绝；不把 `productionStatus` 当 `items` 项。
>
> `planSync` 固定包含 `outcome`、`reason`、`statusChanged`、`fieldsChanged`。无计划为 `skipped` / `no_plan`、`false`、空数组；有计划且状态或提交的共享值使计划发生变化为 `synced` / `null`；有计划但无需修改为 `unchanged` / `null`。`fieldsChanged` 列出实际改变的稳定 `name`，`statusChanged` 指计划状态是否真实改变。实绩 `outcome: unchanged` 与 `planSync.outcome: synced` 可同时出现。
>
> 以下为独立合成示例，假设当前配置仅有共享订单 `productCode`、共享自动反馈 `completedLength`（回写开启）、计划本地 `customerOrderNo`、实绩本地自动 `currentSpeed` 和实绩本地人工可空 `inspectionPassed`。这些不是当前 Swagger 可用请求。
>
> 计划创建请求：
>
> ```json
> {"taskNo":"job-001","items":{"productCode":"PRODUCT-A","customerOrderNo":"MES-001"}}
> ```
>
> 对应完整成功响应（HTTP 200）：
>
> ```json
> {
>   "code": 200,
>   "message": "success",
>   "data": {
>     "outcome": "created",
>     "configVersion": 3,
>     "plan": {
>       "id": "1", "taskNo": "JOB-001", "targetKey": null,
>       "productionStatus": "new", "priority": 5, "remark": null,
>       "createdAt": "2026-11-17T10:30:00+08:00",
>       "updatedAt": "2026-11-17T10:30:00+08:00",
>       "items": {"productCode": "PRODUCT-A", "completedLength": null, "customerOrderNo": "MES-001"}
>     }
>   },
>   "timestamp": 1794882600000
> }
> ```
>
> 实绩上报请求和完整响应：
>
> ```json
> {"taskNo":"JOB-001","items":{"completedLength":300,"currentSpeed":0}}
> ```
>
> ```json
> {
>   "code": 200,
>   "message": "success",
>   "data": {
>     "outcome": "created",
>     "configVersion": 3,
>     "performance": {
>       "id": "1", "taskNo": "JOB-001", "targetKey": null,
>       "productionStatus": "running", "remark": null,
>       "startedAt": null, "completedAt": null, "lastObservedAt": null,
>       "createdAt": "2026-11-17T10:30:02+08:00",
>       "updatedAt": "2026-11-17T10:30:02+08:00", "hasPlan": true,
>       "items": {"productCode": "PRODUCT-A", "completedLength": 300, "currentSpeed": 0, "inspectionPassed": null}
>     },
>     "planSync": {"outcome": "synced", "reason": null, "statusChanged": true, "fieldsChanged": ["completedLength"]}
>   },
>   "timestamp": 1794882602000
> }
> ```
>
> `GET /api/v1/integration/plans?productionStatus=new` 无符合条件记录时，完整响应如下；不会创建使用记录或改变任何任务：
>
> ```json
> {
>   "code": 200,
>   "message": "success",
>   "data": {"items": [], "total": 0, "page": 1, "pageSize": 20, "totalPages": 0},
>   "timestamp": 1794882603000
> }
> ```
>
> 状态单独更新只需如下请求；缺省的业务值保持不变：
>
> ```json
> {"taskNo":"JOB-001","productionStatus":"completed"}
> ```
>
> 另一个任务先上报实绩、没有同号计划，下面是完整请求和响应（该独立例子仍使用前述五个字段配置）：
>
> ```json
> {"taskNo":"NO-PLAN","items":{"completedLength":50}}
> ```
>
> ```json
> {
>   "code": 200,
>   "message": "success",
>   "data": {
>     "outcome": "created",
>     "configVersion": 3,
>     "performance": {
>       "id": "2", "taskNo": "NO-PLAN", "targetKey": null,
>       "productionStatus": "running", "remark": null,
>       "startedAt": null, "completedAt": null, "lastObservedAt": null,
>       "createdAt": "2026-11-17T10:30:03+08:00",
>       "updatedAt": "2026-11-17T10:30:03+08:00", "hasPlan": false,
>       "items": {"productCode": null, "completedLength": 50, "currentSpeed": null, "inspectionPassed": null}
>     },
>     "planSync": {"outcome": "skipped", "reason": "no_plan", "statusChanged": false, "fieldsChanged": []}
>   },
>   "timestamp": 1794882603000
> }
> ```
>
> 随后补建计划，显式选择回填，同时请求中为同一共享字段提交 35。请求中的 35 优先于历史实绩的 50；若省略 `backfillExisting` 和该项，计划此字段为 `null`。
>
> ```json
> {"taskNo":"NO-PLAN","backfillExisting":true,"items":{"completedLength":35}}
> ```
>
> ```json
> {
>   "code": 200,
>   "message": "success",
>   "data": {
>     "outcome": "created", "configVersion": 3,
>     "plan": {
>       "id": "2", "taskNo": "NO-PLAN", "targetKey": null,
>       "productionStatus": "running", "priority": 5, "remark": null,
>       "createdAt": "2026-11-17T10:30:04+08:00",
>       "updatedAt": "2026-11-17T10:30:04+08:00",
>       "items": {"productCode": null, "completedLength": 35, "customerOrderNo": null}
>     }
>   },
>   "timestamp": 1794882604000
> }
> ```
>
> 同一实绩随后再提交已存的 `completedLength: 50` 且没有真实观测时间时，实绩的值和观测时间均不变，但仍将计划由 35 回写为 50；响应中实绩 `outcome` 为 `unchanged`，`planSync.outcome` 为 `synced`、`fieldsChanged` 为 `["completedLength"]`。这不是基于序号的去重或对历史包顺序的判断。
>
> 字段定义响应的完整字段形状如下；此独立例子假设计划仅配置这一共享字段，`planEditable` 和 `syncEnabled` 可同时为 `true`：
>
> ```json
> {
>   "code": 200,
>   "message": "success",
>   "data": {
>     "configVersion": 3, "configRevision": "4",
>     "fields": [
>       {
>         "scope": "shared_sync", "slotNo": 3, "name": "completedLength",
>         "type": "number", "labels": {"zh-CN": "已生产长度", "en-US": "Completed length"},
>         "unit": "m", "enabled": true, "isNullable": true, "syncEnabled": true,
>         "performanceOwner": "automated", "planEditable": true, "performanceEditable": false,
>         "planVisible": true, "performanceVisible": true, "planOrder": 3, "performanceOrder": 3
>       }
>     ]
>   },
>   "timestamp": 1794882604000
> }
> ```
>
> **R2-10 错误。** 成功信封为 `code`、`message`、`data`、毫秒 Unix `timestamp`。错误使用相应 HTTP 状态和 `code`、`message`、`data: null`、`errorCode`、`details`（可定位字段及原因）、`timestamp`；用户可见文字由 i18n 翻译。`401 task.unauthenticated` 表示登录入口未登录；`403 task.forbidden` 表示登录角色或字段归属不足；`404 task.not_found` 表示记录不存在；`409 task.target_conflict`、`task.config_revision_conflict`、`task.field_in_use` 分别表示目标、配置修订、字段已被使用；`422 task.invalid_request` 覆盖字段名、停用、类型、空值、范围、状态或请求形状；`503 task.unavailable` 表示未提交且不可用，`503 task.commit_unknown` 表示提交结果无法确认。退役入口按第 7 节返回 `410 task.endpoint_retired`。具体错误项必须能区分原因，非法混合请求整次回滚。
>
> 例如非数字速度（HTTP 422）：
>
> ```json
> {
>   "code": 422,
>   "message": "task.invalid_request",
>   "data": null,
>   "errorCode": "task.invalid_request",
>   "details": {"field": "items.currentSpeed", "reason": "type_mismatch"},
>   "timestamp": 1794882603000
> }
> ```
>
> ## 6. 字段设置与安全删除
>
> **R2-11 页面。** 计划和实绩列表分别保留「标题与操作、筛选、表格与分页」三段，以及任务号、目标、状态、上海时间和当前配置列；空目标或观测时间显示 `—`。计划「字段设置」弹窗只管理计划本地字段，实绩弹窗只管理实绩本地字段。两模块「共享字段设置」入口进入同一个页面或组件，读取、保存同一份后端共享定义，一边保存后另一边重新读取一致。仅 admin 编辑配置，固定生产状态不进入字段设置。字段键、中英文、类型、启停、空值、显示/顺序、写入归属和回写开关按各组适用性呈现；用户可见内容使用中英文 i18n。
>
> 普通业务表及设置表使用公共列宽能力：可拖拽、最小宽度、横向滚动，本机按应用/页面/稳定字段键隔离，翻页、筛选、刷新、页面切换及重新加载或应用重启后保留，失效偏好回退并提供恢复默认；特殊功能列可固定。恢复列宽或提示配置冲突时，不清除当前仍打开的设置弹窗中的编辑。主动取消或关闭时未保存草稿按现有交互丢弃，本规格不要求将未提交草稿跨重开或重启持久化。
>
> **R2-12 字段删除。** 定义身份至少为组、槽位、稳定 `name`。共享字段审计计划与实绩，本地字段只审计所属模块；任何历史下发批次引用包含该字段的配置版本也计使用。**只要一个适用任务曾按包含该定义的配置创建或被有效更新，就算使用**，即使字段停用、未赋值、只更新状态，或有效 POST 未改变主行值；不能仅查询 JSON 是否有值。纯 GET 和列表/详情渲染不创建使用证据、不写任务或配置。
>
> 历史 r1 任务和下发批次根据其已绑定的配置版本保守回查；迁移必须保存或补足可审计的使用证据。r2 对每个成功创建或更新，记录适用模块当时配置版本的使用证据，并与任务写入同事务；该证据不是继续按旧绑定版本读取的条件，也不单独推进任务的 `updatedAt`。若旧定义、引用或使用证据无法可靠判定，一律视为已用，保留字段，只允许停用。
>
> 管理员删除时在同一事务重查当前修订、字段身份以及所有相关历史版本和使用/批次引用，并与创建、更新和配置发布采取一致的并发串行边界。已有引用返回 `409 task.field_in_use`，不删除、不释放槽位；过期修订返回 `409 task.config_revision_conflict`。只有确定所有含该字段的版本均无适用任务和批次使用，才删除当前定义、推进配置并释放该组槽位；已用字段只能停用，重新启用是同一字段恢复，不是把旧槽复用给新字段。允许对从未使用且已删除的槽位新增不同字段，但须确保历史定义及值不会被新字段解释。删除前提示管理员核对外部 MES/SMA 映射；服务端可见的仍生效映射若引用该字段则拒绝并说明，无法观察的外部映射不冒称已检查。
>
> ## 7. r1 入口兼容、迁移与恢复
>
> **R2-13 停用而保留历史。** r2 不再提供领取、占用、下发、回执或人工下发状态流转。计划页移除领取状态、批次处理、暂停/恢复/取消和核验动作，不以历史下发状态或旧 `not_required` 限制计划 upsert、实绩 upsert 和普通 GET。旧 `POST /integration/plans/dispatch/claim`、`POST /integration/plans/dispatch/report`、`POST /plans/{id}/actions/{action}`、`POST /performances/{id}/actions/supplement-plan` 不再执行旧动作；保留不出现在新 OpenAPI 的兼容拒绝入口，直接调用返回 `410 task.endpoint_retired`，不产生写入。实绩页面若保留补建入口，只带同号进入新的计划创建流程。旧请求使用的 `syncValues` / `localValues`、强制来源/目标/版本和旧快照格式不静默解释成新 `items`；旧客户端切换须按新合同显式适配。
>
> 旧 `plan_dispatch_attempts`、`plan_action_events`、版本快照及其批次、状态、操作者和原证据保留，以供历史核对；它们不表示 r2 正在处理下发。历史 `dispatch_status`、优先级及旧列不可因退役而抹掉历史事实；可保留旧列或以可对账方式迁移，不再对新业务控制。保留已交付的 r1 合同工件字节与历史 QA；在新的 r2 合同候选和索引解释接口的不兼容变更，不把新协议写成旧客户端无需修改即可使用。业务集成其他模块、独立质量和采集接口按原合同保留。
>
> **R2-14 迁移和恢复。** 新增显式 Alembic 后继，执行前重新盘点目标身份、当前 head、两主表、当前/历史配置定义、旧绑定版本、历史下发和人工动作、值槽位、目标冲突及外部依赖，记录备份、行数和可核对的摘要；不得假设 r1 验证后库仍为空。旧计划生产状态为 `NULL` 时，若同号实绩有有效状态则迁为该状态，否则迁为 `new`；旧有效状态与其他历史时间和值保留。保留历史版本并建立第 6 节所需的保守使用证据；如旧槽位/类型不能安全对应当前定义、同号已知目标冲突、版本引用缺失、历史时区未知或发现无法确认的依赖，停止对应迁移并交 Human Owner 决定，不猜测或丢弃。目标允许为空、四种状态及选填元数据所需约束必须在迁移和模型中一致，旧 r1 migration 原字节不改。
>
> 提交实际 dev 操作前，Development 给出精确目标、备份恢复可行性、写入范围、服务停止/重启次序、现有数据和历史的前后对账、受控合成测试对象及清理/保留方案。MySQL DDL 可能非事务性；中断后先停写并核实每步、保存新增数据和证据，恢复或重试须按具体操作再获批准，不能盲目降级或清库。若无法证明不破坏既有数据或安全恢复，则该环境步骤阻塞，不将 r1 的历史空库证据当成当前事实。
>
> ## 8. 允许实施面、验收与交接
>
> Human Owner 已精确批准 r2，允许在各自角色职责内修改下列与本规格直接相关的路径；未经相应额外批准不得实际操作目标数据库或服务。清单不是 PM 本轮写入范围。
>
> | 路径 | 范围 |
> | --- | --- |
> | `backend/app/plan/**`、`backend/app/performance/**`、`backend/app/task/**` | 计划、实绩、共享字段、路由、领域规则、权限、错误和历史兼容。 |
> | `backend/alembic/versions/` | 新增明确后继；保留历史迁移。 |
> | `backend/tests/**`、`backend/tests_mysql/**` | 本规格的源码、HTTP、事务/并发、迁移和保护回归。不得把旧测试库重建 fixture 指向现有 dev。 |
> | `frontend-js/src/app/plan/**`、`frontend-js/src/app/performance/**`、`frontend-js/tests/**` | 两列表、表单、共享/本地设置、i18n、列宽与必要的定向验证。 |
> | `contracts/published/http-api/generic-task-workflow-v2/**`、`contracts/README.md`、`contracts/README.zh-CN.md` | 新的候选 OpenAPI、合成示例和说明及索引；保留 v1 原字节，不代表发布或消费者采用。 |
> | `backend/README.md`、`backend/README.zh-CN.md`、`frontend-js/README.md`、`frontend-js/README.zh-CN.md`、`frontend-js/FIELD_SETTINGS_GUIDE.zh-CN.md`、`CODE_INDEX.md` | 仅涉及受影响入口、字段指南和真实结构所必需的同步。 |
> | 本任务 `tasks.md`、`checklist.md` | 分别由 Development、fresh-context Verification 在各自 gate 更新，保留 r1 原始历史与证据。 |
> | 根 `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md` | 由主协调者按真实角色 gate 机械同步本任务聚合状态、下一步和链接；保留 r1 QA4 与待最终验收等历史，不写入本任务之外的索引内容。 |
>
> 路径不够、需要修改其他模块/配置、放宽数据保护或变更本规格实质范围时，先返回 PM 修订并重审，不由 Development 自行扩大 allowlist。Development 必须按任务表面使用 `backend-arch`、`frontend-ui`、`i18n-workflow`；真实源码结构变化时使用 `code-document-indexer`。跨端合同遵循 `aiis`、任务治理遵循 `project-governance`。角色只按已批准范围执行并如实记录实际工作树、检查、风险及交接。
>
> ### 可验证验收标准
>
> 以下是未来 Development 自检和 fresh-context Verification 的通过条件，不是本次已执行结果。数据库型验收使用经具体操作批准的现有 dev、合成任务号和明确登记的测试字段；真实历史和其他任务数据须可对账。必要检查使用项目 `uv` / `pnpm` 工具链。
>
> | 编号 | 场景与通过标准 |
> | --- | --- |
> | R2-AC01 | 两表独立唯一，任务号大小写/空格规范化，同号不依赖外键；各表两个 JSON 列均能保存 100 个共享和 100 个本地逻辑值，超限/错误形状被拒；跨模块本地同名可用，同模块与共享同名拒绝。 |
> | R2-AC02 | 计划 taskNo-only 创建为 `new`；只提交状态、仅部分 `items`、相同值重发均符合合并规则。`null`、空串、0、false、禁止清空、未知或停用字段、类型错误、非法状态分别验证，非法混合包及时间全部不部分提交。 |
> | R2-AC03 | 先无计划上报创建 `running` 实绩，再普通 POST 同号计划：省略状态继承 `running`，不报旧补建错误，默认无历史共享回填；显式状态优先。另测显式选择回填、同一可写共享字段的当次 `items` 优先及后续上报回写；无实绩时启用回填须拒绝。 |
> | R2-AC04 | 先建带订单值的计划再首次建实绩，验证启用的 `order_snapshot` 只继承一次；直接提交只读快照拒绝，自动/人工字段按归属接受，后来改计划不覆写实绩快照，无计划创建的快照仍空。 |
> | R2-AC05 | 无计划实绩保存成功；有计划时本次未提交状态仍同步实绩当前状态；实绩状态不变但计划不同也修复。重复相同共享值时，即使实绩不变而计划不同也回写；未提交共享值和两边本地值不变，逐表更新时间只因该行变化推进。 |
> | R2-AC06 | `completed` 后再提交有效 `running`，两表均变 `running`；计划 `error` 后实绩再报则按最后处理覆盖；计划单独改状态不反写实绩。`completedAt` 仅真实提交、缺省不改。 |
> | R2-AC07 | 采集 `items` 有真实 `observedAt`、省略、`null` 和同值重报分别验证 `lastObservedAt`；仅状态且未提交时间时保留，显式时间/`null` 按 R2-03 处理；不得把服务器时间冒充采集时间。跨时区输入转换和非法/超精度输入均核验。 |
> | R2-AC08 | 相同、递减、缺失或 `null` 的 `observationSeq` 及较旧 `observedAt` 均不去重、不决定顺序；按成功处理顺序验证旧包可覆盖新值。并发同号创建、计划/实绩交错、不同槽更新和回写，验证单行唯一、不漏同步及不丢合法字段；在两表更新之间注入失败证明整体回滚。 |
> | R2-AC09 | 三项元数据省略/`null` 可写，版本不匹配不阻断；目标未知不分配产线，新实绩按 R2-08 继承，目标冲突整包拒绝，历史双方冲突不能被掩盖。无 token 的任务集成接口可按合同调用，前端登录和 admin 权限仍生效，DAA/设备/其他接口准入回归不被放宽。 |
> | R2-AC10 | `GET /integration/plans?productionStatus=new` 无任务号可分页；无匹配返回约定空信封，省略目标不筛线；过滤、排序、页边界、类型和 `items`、完整响应/错误、重复读取前后数据库及使用证据不变。 |
> | R2-AC11 | 新增启用字段后旧任务缺值 GET 为 `null`；停用 GET 不输出但原值仍存，原字段复启恢复；前端和集成按当前配置及稳定键读写，旧 `fieldConfigVersion` 不决定字段。 |
> | R2-AC12 | 共享页两入口一致，本地弹窗只管各自组；中英文、真实 API、三段布局及列宽拖动、本机隔离、翻页/筛选/刷新/页面切换和重开恢复按 R2-11 验证。恢复列宽或提示配置冲突不清当前打开弹窗的编辑；主动取消或关闭丢弃未保存草稿，不要求跨重开持久化。生产状态始终可见且不可停用。 |
> | R2-AC13 | 无使用的已保存字段可删除并重用槽位；分别以计划、实绩、停用/无值、仅状态或无变化 POST、历史批次引用阻止删除；只读 GET 不形成引用。共享/本地归属分别验证，缺失历史证据保守拒绝。并发删除与创建/更新的两种先后都不允许误删已用字段。 |
> | R2-AC14 | 已批准目标的迁移前后比对任务、槽值、历史版本、批次/动作与保护对象；旧空生产状态转换按 R2-14。冲突/未知依赖预检停止；旧接口稳定 410 且无动作，旧 UI 不再触发，历史仍可核对，受保护接口和数据保持。 |
> | R2-AC15 | 后端定向检查、真实 MySQL 事务与并发、前端模块测试/构建、正常 HTTP/OpenAPI 和真实浏览器覆盖上述条目；记录命令、退出码、环境、具体授权、保留数据及限制。合同候选示例均可解析并与实际注册路径及响应一致。 |
>
> ## 9. 风险、已批准口径与批准记录
>
> - **顺序风险：** 不保证发送、采集与成功处理顺序一致；迟到包或重试可能覆盖较新的业务值和状态。`commit_unknown` 后应先查询核对，不能声称存在自动幂等或可靠去重。
> - **历史与迁移风险：** 当前配置解释旧值要求字段身份可追溯；历史版本证据不全时只能保守停用。MySQL DDL、中途失败及现有库共享服务需按第 7 节准备可审阅操作提案并单独批准。
> - **访问与覆盖风险：** 任务集成入口无前端 Bearer token、`producerId` 不认证来源；实际开放范围依赖项目的网络及部署决定，不能据此扩大其他服务的准入。同一共享字段可由计划入口写入且允许实绩回写，后续有效实绩上报可覆盖先前计划值；使用方须按业务需要设置字段权限与回写开关。
> - **Human Owner 已批准的 r2 具体口径：** (1) 计划可显式选 `backfillExisting`、默认关闭且请求值优先；(2) 已知目标冲突拒绝、已有空目标不因状态更新自动补填，以及目标修正另议；(3) 旧写入口返回 410、历史留存；(4) 状态-only 未提交观测时间保留、显式 `null` 清空；(5) 计划登录编辑开关与集成写入规则分别校验，允许共享字段既可计划写入又可被实绩回写。它们是已批准的 r2 具体口径，尚不是现有实现事实。
>
> | 日期 | 主体 | 决定 |
> | --- | --- | --- |
> | 2026-11-17 | PM | 根据最新讨论提交 ARCH-TASK-001 r2 草案；r1 原规格及批准完整保留，r1 QA4 通过和最终验收待定继续有效。 |
> | 2026-11-18 | Human Owner | 明确指示「批准 ARCH-TASK-001 r2 按该规格进入开发」。获批草稿 SHA-256：`8a2c9775d135752e9ff8c5e0d9ec90cf19eb31922252a1c7e5da1c858e4b62ea`。 |
>
> 下一 gate：Development 依据精确 r2 实施并记录自检和 `developer_handoff`；随后由 fresh-context Verification 独立验证，再由 Human Owner 决定最终验收。真实数据库写入、迁移、服务切换和现场操作仍按各自具体步骤另行批准。
>
> ## r1 获批历史
>
> <a id="7-旧卷材一次性切换"></a>
> 下方完整保留修改前的 r1 原文件及其批准记录。取引用代码块正文：非空行移除 `> ` 前缀，单独的 `>` 还原为空行，即可逐字节恢复；原文件 60422 字节，SHA-256 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`。原文中的批准和旧流程只属于 r1，不能视为 r2 批准。
>
> <details>
> <summary>展开 r1 完整原文及批准记录</summary>
>
> > `````markdown
> > Task ID: ARCH-TASK-001
> > Revision: r1
> > Status: owner_approved
> > Owner Role: PM
> > Allowed Writers: PM, Human Owner
> > Handoff: Human Owner 已批准精确 r1 源码实施，移交 Development。现有 dev 的具体切换操作按第 7 节办理。
> > Workflow Mode: STD
> > Execution Mode: agent_team_same_session
> > Task Namespace: aiis-ics-arch
> > Classification: root
> > Capability: 通用计划与实绩、可追踪的下发回执及同号实绩回写
> > Owner: AIIS ICS Architecture 计划与实绩模块
> > Acceptance Chain Reference: 本规格第 9、10 节及 Development Lifecycle Workflow
> > Related Task: ARCH-ACQ-003, ARCH-BE-010, ARCH-BE-011, ARCH-OBS-001
> > Created: 2026-11-11 Asia/Shanghai
> > Updated: 2026-11-11 Asia/Shanghai
> >
> > # 通用计划与实绩首版规格
> >
> > ## 1. 目标与已确认的范围
> >
> > MES 提交订单后保存计划。CA/FF 领取任务和冻结参数，按 PLC 接收条件下发并回报原批次。实际生产后，DAA 提供采集事实，SMA 按原任务号上报实绩。后端保存已接受的实绩，并在同一事务更新同号计划允许回写的字段。现场先生产时可独立保存实绩，之后由授权人员补建无需下发的计划。前端从计划和实绩各自的列表与详情读写业务数据。
> >
> > Human Owner 已确认主流程、§§1–9 的表和接口口径，以及总稿 §§10.2、10.3 的旧卷材一次性切换和在现有 dev 库运行模拟闭环。下文为提交审阅的 r1。第 2、3 节的合成样例和具体角色授权由本次审阅确认。讨论输入以 2026-11-11 的中文总稿为准，SHA-256 为 `08d57ab7f4563781fe3e3d3614a397dc4ed153f1a1508ce0f42c0cb61a6c0144`。总稿中的切换与验收待确认标签已由 Human Owner 本次选择收口。[总讨论稿](../../docs/generic-task-workflow-discussion.zh-CN.md)
> >
> > 交付范围包含 FastAPI 计划、实绩、共用字段配置及集成接口，正式 Alembic 后继迁移，Vue 计划和实绩列表、详情、对应操作及两个管理员字段设置入口，以及旧功能的一次性切换。通过正常启动的后端、浏览器和现有 dev MySQL 验收。MES、CA/FF、PLC 回执和 SMA 快照由测试客户端模拟。采集事实 v2 的已采用接口及页面列入迁移回归。[现有采集交付](../ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收)
> >
> > 现场联调另按各端任务推进。真实 PLC 地址和编码、接收允许值、确认序号保持及复位、超时、旧执行方隔离、末次采样保留及释放、SMA 重启续号由项目现场接入确定。DAA/SMA/CA/FF 运行时和 C# 后端、通用 XLSX 和报表重建、采集值人工更正、设备实时与过程历史、raw/latest 系统管理页均在本次软件范围之外。
> >
> > ## 2. A/B 单合成样例
> >
> > **R01 样例定义。** 两单使用合成目标 `LINE-01`、MES `mes-01`、现场执行方 `ff-01`、自动实绩来源 `sma-01`。在每次受控验证中生成一个 1–12 位大写字母或数字的 `RUN`，任务号用 `GT1-<RUN>-A` 和 `GT1-<RUN>-B`。独立场景使用不同 `RUN`，同一场景的重试沿用原身份。下文 `V` 指通过配置 API 读到的生效版本。样例须经管理员设置入口或对应 API 配置，登记为合成输入。计划领取时 `LINE-01` 只冻结 `productCode` 和 `targetLength`，另随领取返回固定的 `taskNo`。
> >
> > | 组和槽位 | name | 中文 / English | 类型 / 单位 | 值要求和写入方 | 冻结 / 回写 |
> > | --- | --- | --- | --- | --- | --- |
> > | `shared_sync` 01 | `productCode` | 产品编码 / Product code | `string` | 建计划、补建必填。MES 或获准人工在计划侧填写，实绩归属为 `order_snapshot`。 | 冻结。首次建实绩时继承，回写关闭。 |
> > | `shared_sync` 02 | `targetLength` | 目标长度 / Target length | `number` / m | 建计划、补建必填。MES 或获准人工在计划侧填写，实绩归属为 `order_snapshot`。 | 冻结。首次建实绩时继承，回写关闭。 |
> > | `shared_sync` 03 | `completedLength` | 已生产长度 / Completed length | `number` / m | 建计划时为空。每份自动快照必填，由 SMA 写入，实绩归属为 `automated`。 | 回写开启，计划侧只读反馈。 |
> > | `plan_local` 01 | `customerOrderNo` | 客户订单号 / Customer order no. | `string` | 样例可省略。MES 或获准人工在计划侧填写。 | 计划本地值。 |
> > | `performance_local` 01 | `currentSpeed` | 当前速度 / Current speed | `number` / m/min | 每份自动快照必填，0 为有效值，由 SMA 写入，实绩归属为 `automated`。 | 实绩本地值。 |
> > | `performance_local` 02 | `inspectionPassed` | 检验通过 / Inspection passed | `boolean` | 可省略或清空，实绩归属为 `manual`，有权限的人可填 `true` 或 `false`。 | 实绩本地值。 |
> >
> > 这六个字段在样例版本均启用。01、02 两个共享订单槽及计划本地 01 开启 `planEditable`，实绩本地 02 开启 `performanceEditable`。计划本地 01 和实绩本地 02 开启 `isNullable`，其他槽的清空开关关闭。计划页默认显示共享 01–03 和计划本地 01，实绩页默认显示共享 01–03 和实绩本地 01–02。首次建档时尚无值的反馈和人工字段保持空。两个订单槽在无计划的实绩中也可空，待人工补建时由授权人员填写计划值。
> >
> > | 订单 | MES 初始字段 | 正常领取冻结值 | 实绩及人工结果 |
> > | --- | --- | --- | --- |
> > | A | 优先级 1。产品 `PRODUCT-A`，目标 `1200` 米，客户订单号 `MES-ORDER-001`。 | `productCode=PRODUCT-A`，`targetLength=1200`。 | 序号 12 上报 `running`、长度 `300`、速度 `78.5`，计划目标仍为 1200，回写 300。人工填 `inspectionPassed=true`。序号 13 上报 `completed`、长度 `1200`、速度 `0`。 |
> > | B | 优先级 5。产品 `PRODUCT-B`，目标 `800` 米，客户订单号 `MES-ORDER-002`。 | `productCode=PRODUCT-B`，`targetLength=800`。 | 序号 1 上报 `running`、长度 `50`、速度 `40`，计划目标仍为 800，回写 50。人工填 `inspectionPassed=false`。 |
> >
> > 在一个正常场景中先创建 B、再创建 A，仍应先领取 A。用同优先级的独立场景核对按创建时间及 ID 升序。模拟 A 的 PLC 回执 `requestSeq=ackSeq=41`，B 回执使用 42，均保留各自的原 `dispatchId`。以 A 序号 12 的采样时刻为 `T`，A 序号 13 的采样和完工时刻均为 `T+20 秒`，B 序号 1 在 `T+30 秒` 采样。请求用上海 `+08:00` 时间。先让 B 的序号 1 入库，再提交带 A 原任务号、原时间及最终值的序号 13。A 更新为已完成并回写 1200，保留人工检验结果，B 的实绩和回写保持为 50。在 A 序号 12 后先测试序号 11、重复 12、改内容的 12，再补报 13。用序号 14 验证完工后继续自动上报的响应。
> >
> > 另在两个独立 `RUN` 中先提交 B 的序号 1 快照。此时无 B 计划，响应 `hasPlan: false`、`planSync.reason: "no_plan"`，实绩订单快照为空。普通建计划得到 `409 task.plan_supplement_required`。从 B 实绩详情补建，填写产品 `PRODUCT-B`、目标 800 米及客户订单号。第一次变体省略 `backfillExisting`，补建后计划反馈槽 03 仍空。第二次变体设 `backfillExisting: true`，反馈槽 03 为 50。两种都返回 `not_required`，保留 B 的已知生产状态且不进入领取队列。重复补建返回同一计划，补建完成后普通人工编辑限备注。再报 B 序号 2，长度 60、速度 41，两种变体均只回写共享 03，B 实绩的订单快照仍为空。
> >
> > ## 3. 人工操作权限
> >
> > **R02 角色和授予条件。** 使用现有 `admin`、`supervisor`、`operator`。admin 沿用登录后内置 API 访问权。supervisor、operator 通过 `SUPERVISOR_API_PERMISSIONS_JSON`、`OPERATOR_API_PERMISSIONS_JSON` 授予 `plan`、`performance`，浏览器通过 `VITE_SUPERVISOR_PAGE_ACCESS_JSON`、`VITE_OPERATOR_PAGE_ACCESS_JSON` 授予 `plan.list`、`performance.list`。两端各自要求 operator 的配置是 supervisor 的子集。后端独立校验操作角色、API 授予、状态及字段权限。页面按可访问入口、角色、后端查询结果及当前状态控制按钮。对于补建，先核对实绩详情和计划配置查询均可访问，再显示有权限的操作。默认进入计划列表仅适用于有该页面访问权的用户，其他用户按现有可访问页回退规则处理。[后端权限配置](../../backend/README.zh-CN.md#角色-api-权限) · [前端页面配置](../../frontend-js/README.zh-CN.md#项目页面配置)
> >
> > | 动作 | admin | supervisor | operator | 条件 |
> > | --- | --- | --- | --- | --- |
> > | 查计划列表、详情、计划字段配置 | 允许 | 持 `plan` | 持 `plan` | 详情公开正常批次摘要，核验的异常详情及最近动作证据按下一行控制。 |
> > | 查计划核验详情及人工证据 | 允许 | 持 `plan` | 禁止 | 仅登录的有核验权限人员读取 `failureKey`、`failureDetail` 和最近 20 条 `recentActionEvents`。 |
> > | 查实绩列表、详情、实绩字段配置 | 允许 | 持 `performance` | 持 `performance` | 按实绩绑定版本读值。 |
> > | 新建计划、改计划值、补计划备注 | 允许 | 持 `plan` | 禁止 | 待下发或暂停且无生产事实时改允许的订单字段。已领取、下发异常、PLC 已接收或已开工后限备注。补建完成后普通编辑限备注，已取消记录保留查询。 |
> > | 暂停、保存并恢复、取消 | 允许 | 持 `plan` | 禁止 | 按第 5 节状态流转和原因校验。 |
> > | 核验退回暂停 | 允许 | 持 `plan` | 禁止 | 原批次、原因和证据必填，旧提交已确认未生效且无开工或接收事实。 |
> > | 编辑已有实绩的人工值和备注 | 允许 | 持 `performance` | 持 `performance` | 启用、归属 `manual` 且可编辑的值可改。自动值、继承值、任务身份、开完工事实由其所属流程维护。 |
> > | 从实绩补建计划，可选回填 | 允许 | 同时持 `plan` 和 `performance` | 禁止 | 需能读取该实绩及创建计划，任务号和绑定版本从实绩取得。 |
> > | 两个字段设置入口与保存 | 允许 | 禁止 | 禁止 | admin 可在可访问模块入口维护共享组及该模块本地组。 |
> >
> > 前端缺登录认证返回 `401 task.unauthenticated`。已认证但角色、API 授予或写入归属不足返回 `403 task.forbidden`。允许调用但任务状态、版本或幂等身份冲突返回第 6 节的 `409`。整包提交中一项越权或不合法，整包不落库。管理员也受任务状态、写入归属和数据规则约束。人工动作的 `actorId` 取后端已认证主体。[后端权限实现](../../backend/core/deps.py)
> >
> > MES、CA/FF、SMA 通过各自的通用任务集成入口调用，沿用免前端登录 token 的约定。项目在受信集成边界显式开放入口并登记目标、允许的 MES 和 CA/FF、每个目标的一条自动上报流，以及按版本确定的下发字段映射。未开放或来源超出登记范围时返回 `403 task.forbidden`。后端按入口和登记来源校验，`producerId` 用于追踪和匹配来源。集成读取仅包括约定的任务、正常批次摘要和启用字段定义。人工核验、补建和管理员保存由登录入口提供。采集事实 v2 的机器凭证和采集页面读权限按其现有合同执行。[采集事实 v2](../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)
> >
> > ## 4. 表结构、索引与字段版本
> >
> > **R03 物理结构与索引。** 模块主业务表沿用 `xx_main` 约定。计划为 `plan_main`，实绩为 `performance_main`，每张主表使用两个 JSON 值列。环境按 MySQL 8.4.6、InnoDB、`DYNAMIC` 和 `utf8mb4` 设计，每个部署对应一个项目。下文 ASCII 键列采用 `ascii_bin`，任务号按第 5 节规范化后入库。`targetKey` 使用项目登记的键，`targetKey` 和 `producerId` 都为 1–64 位英文字母、数字、点、下划线或连字符，按原大小写匹配。
> >
> > 所有记录时间使用 `DATETIME(6)`，保留来源中最多六位小数秒的精度。创建和实际更新时间由数据库时钟生成，新增的这两列可用 `DEFAULT CURRENT_TIMESTAMP(6)`，后端有实际变更时才更新 `updated_at`。数据库时钟与项目 `Asia/Shanghai` 时间契约对齐。开工、完工、采样和读到确认的时间取相应实际来源，API 统一返回带 `+08:00` 的时间。
> >
> > #### 两张主表
> >
> > | 字段 | SQL 类型 | 规则 |
> > | --- | --- | --- |
> > | `id` | `BIGINT UNSIGNED` | 两表各自自增主键。 |
> > | `task_no` | `VARCHAR(50) ASCII` | 两表必填、各表唯一。 |
> > | `target_key` | `VARCHAR(64) ASCII` | 两表必填，计划领取后锁定，实绩记录上报来源所属目标。 |
> > | `field_config_version` | `INT UNSIGNED` | 两表必填，首条同号记录确定版本。 |
> > | `remark` | `VARCHAR(500)` | 两表可空。 |
> > | `created_at`、`updated_at` | `DATETIME(6)` | 两表必填，按上文的数据库时间规则。 |
> > | `production_status` | `VARCHAR(16) ASCII` | 实绩必填 `running` 或 `completed`。计划侧由后端维护，未上报时为空。 |
> > | `priority` | `SMALLINT UNSIGNED` | 计划必填，默认 5，范围 1–10，1 为最高优先级。 |
> > | `dispatch_status` | `VARCHAR(24) ASCII` | 计划必填，普通新建默认 `pending`，补建写 `not_required`。状态键见第 5 节。 |
> > | `started_at`、`completed_at`、`last_observed_at` | `DATETIME(6)` | 实绩可空，分别记录实际开始、实际完成和最近接受的采样时间。 |
> > | `observation_seq` | `BIGINT UNSIGNED` | 实绩必填，建档时取首条有效自动快照的序号。 |
> > | `observation_digest` | `BINARY(32)` | 实绩必填，与序号同时保存规范化快照的 SHA-256 摘要。 |
> > | `record_source` | `VARCHAR(32) ASCII` | 实绩必填，由后端记录建档来源 `sma` 或 `ca_ff`。 |
> > | `local_values`、`sync_values` | `JSON NOT NULL DEFAULT (JSON_OBJECT())` | 两表各两列。每组是最多 100 项的对象，用 `"01"` 至 `"100"` 定位槽位。 |
> >
> > 两张主表各有 10、14 个固定字段，再各加两个 JSON 值列。数据库用 `CHECK` 校验两组值都是对象且各最多 100 项，例如 `JSON_TYPE(local_values) = 'OBJECT' AND JSON_LENGTH(local_values) <= 100`。优先级和固定状态按表中范围校验。Service 按绑定版本校验槽位、写入方、类型和长度，把有效值保存成文本，明确清空时移除该键。数据库字段使用 snake_case，接口映射见第 6 节。已有实绩的 `hasPlan` 按同号计划派生。[MySQL CHECK 约束](https://dev.mysql.com/doc/refman/8.4/en/create-table-check-constraints.html)
> >
> > #### 字段配置
> >
> > `task_field_config_state` 是配置状态表。每个部署使用一行，`id TINYINT UNSIGNED` 为主键且固定为 1。`active_version INT UNSIGNED NOT NULL` 和 `config_revision BIGINT UNSIGNED NOT NULL` 初始化为 1，另有必填的 `created_at`、`updated_at`。业务版本供任务绑定，修订号用于校验管理员保存是否过期。
> >
> > | `task_field_definitions` 字段 | SQL 类型 | 规则 |
> > | --- | --- | --- |
> > | `id`、`config_version` | `BIGINT UNSIGNED`、`INT UNSIGNED` | 自增主键和必填的业务版本。 |
> > | `scope`、`slot_no` | `VARCHAR(24) ASCII`、`TINYINT UNSIGNED` | 组和位置必填，范围为三组及 1–100。 |
> > | `name`、`value_type` | `VARCHAR(64) ASCII`、`VARCHAR(12) ASCII` | 必填。接口键按原样匹配，以小写英文字母开头，后续允许英文字母、数字及下划线。类型见本节。 |
> > | `label_zh_cn`、`label_en_us`、`unit` | 两个 `VARCHAR(128)`、一个 `VARCHAR(32)` | 中英文名必填，单位可空。 |
> > | `is_nullable`、`enabled`、`sync_enabled` | `BOOLEAN NOT NULL DEFAULT FALSE` | 可清空、启用和回写分别保存。 |
> > | `plan_editable`、`performance_editable` | `BOOLEAN NOT NULL DEFAULT FALSE` | 分别控制计划值入口与实绩人工入口能否编辑。 |
> > | `performance_owner` | `VARCHAR(16) ASCII` | 适用于实绩的字段指定 `order_snapshot`、`automated` 或 `manual`。计划本地字段留空。 |
> > | `plan_visible`、`performance_visible` | `BOOLEAN NOT NULL DEFAULT FALSE` | 两页各自的默认可见设置。 |
> > | `plan_order`、`performance_order` | `SMALLINT UNSIGNED` | 两页各自的列顺序，可空时按槽位顺序。 |
> > | `created_at`、`updated_at` | `DATETIME(6)` | 必填，按数据库时间规则。 |
> >
> > 业务版本每次发布保存三组完整定义，包含已生效后停用的槽位。中英文及列显示设置从当前定义叠加到历史版本。仅改展示属性时只推进修订号，调整业务规则时在同一事务发布新业务版本并推进修订号。`unit` 随业务定义保存，已生效的字段若需改变单位含义，用新键和槽位替换。管理员保存按提交范围合并，修订号过期就拒绝保存。
> >
> > `sync_enabled` 仅可给 `shared_sync` 中归属为 `automated` 或 `manual` 的反馈字段开启，开启时计划侧设为只读。`performance_editable` 仅用于人工归属字段。
> >
> > 任务创建与配置发布用配置状态行串行化。创建路径在短事务内锁定该行并复查两张主表，然后采用已存在的绑定版本或当前版本。后续写实绩和回写按先计划、后实绩的固定顺序锁定同号记录，通过各自 Service 在同一次提交中合并值。
> >
> > #### 下发批次和人工动作记录
> >
> > | `plan_dispatch_attempts` 字段 | SQL 类型 | 规则 |
> > | --- | --- | --- |
> > | `dispatch_id`、`claim_request_id` | `CHAR(36) ASCII` | UUID，前者为批次主键，后者唯一，用于领单重试。 |
> > | `task_no`、`target_key`、`attempt_no` | `VARCHAR(50) ASCII`、`VARCHAR(64) ASCII`、`INT UNSIGNED` | 必填。锁定计划时按任务递增批次号。 |
> > | `field_config_version`、`producer_id` | `INT UNSIGNED`、`VARCHAR(64) ASCII` | 必填，冻结时的定义版本和领单方追踪键。 |
> > | `parameters` | `JSON` | 必填，冻结的订单参数，按 API 字段名保存类型化快照。 |
> > | `attempt_status` | `VARCHAR(24) ASCII` | 必填，初值 `claimed`。可转 `exception`、`plc_accepted` 或 `returned`。 |
> > | `active_target_key` | `VARCHAR(64) ASCII`，存储生成列 | `claimed` 或 `exception` 时取 `target_key`，其余状态取 `NULL`，用于唯一约束。 |
> > | `submission_phase` | `VARCHAR(24) ASCII` | 可空，来源实际报告的阶段。取 `not_submitted`、`possibly_submitted` 或 `acknowledged`。 |
> > | `request_seq`、`ack_seq` | `BIGINT UNSIGNED` | 可空，保存报告的原请求和确认序号。 |
> > | `ack_observed_at` | `DATETIME(6)` | 可空，首次有效读到本批次确认的时间。 |
> > | `failure_key`、`failure_detail` | `VARCHAR(64) ASCII`、`VARCHAR(500)` | 可空，记录报告的异常键和核对说明。 |
> > | `claimed_at`、`updated_at` | `DATETIME(6)` | 必填，数据库记录领取和实际更新的时间。 |
> >
> > 未结案的异常批次继续占用接收区。匹配回执或人工查明未生效后释放。生成列上的唯一索引为每个接收区限制一笔待结案批次，已结案批次可并存。CA/FF 的原序号、阶段和现场回执仍由现场执行方按第 5 节的接入约定持久保存。[MySQL 生成列](https://dev.mysql.com/doc/refman/8.4/en/create-table-generated-columns.html) · [唯一索引的 NULL 规则](https://dev.mysql.com/doc/refman/8.4/en/create-index.html)
> >
> > | `plan_action_events` 字段 | SQL 类型 | 规则 |
> > | --- | --- | --- |
> > | `id`、`action_request_id` | `BIGINT UNSIGNED`、`CHAR(36) ASCII` | 自增主键和唯一的动作请求 UUID。 |
> > | `request_digest` | `BINARY(32)` | 必填，用于确认重试与原动作内容一致。 |
> > | `task_no`、`action_key`、`actor_id` | `VARCHAR(50) ASCII`、`VARCHAR(24) ASCII`、`BIGINT UNSIGNED` | 必填，任务号、动作键和已登录操作人 ID。 |
> > | `from_status`、`to_status` | `VARCHAR(24) ASCII` | 必填，动作前后的下发状态。 |
> > | `dispatch_id`、`reason`、`evidence` | `CHAR(36) ASCII`、`VARCHAR(500)`、`TEXT` | 可空。人工核验退回时记录原批次、原因和证据。取消记录原因。 |
> > | `created_at` | `DATETIME(6)` | 必填，数据库记录动作时间。 |
> >
> > 暂停、保存并恢复、取消及核验退回成功时，计划状态和动作记录一起提交。保留旧批次及操作者信息，供计划详情核对。两张业务主表的匹配仍使用任务号。
> >
> > ### 查询和唯一索引
> >
> > | 表 | 索引 | 用途 |
> > | --- | --- | --- |
> > | `plan_main`、`performance_main` | 主键 `id`，唯一 `uq_task_no (task_no)` | 详情定位、并发建档、同号匹配。 |
> > | 两张主表 | `ix_created_page (created_at, id)` | 默认列表排序和创建时间区间。 |
> > | `plan_main` | `ix_plan_target_state_page (target_key, dispatch_status, created_at, id)` | 产线、下发状态和时间的列表组合。 |
> > | `performance_main` | `ix_perf_target_state_page (target_key, production_status, created_at, id)` | 产线、生产状态和时间的列表组合。 |
> > | `plan_main` | `ix_plan_claim (target_key, dispatch_status, production_status, priority, created_at, id)` | 按目标领取待下发计划，优先级、创建时间和 ID 依次排序。 |
> > | `task_field_definitions` | 唯一 `uq_task_field_slot (config_version, scope, slot_no)` 和 `uq_task_field_name (config_version, scope, name)` | 版本定义查询和组内唯一性。共享键与两边本地键的重名及历史占用由 Service 核对。 |
> > | `plan_dispatch_attempts` | 唯一 `claim_request_id`、`(task_no, attempt_no)`、`active_target_key` | 领单重试、定位任务最新批次、单接收区互斥。 |
> > | `plan_action_events` | 唯一 `action_request_id`，索引 `(task_no, id)` | 人工动作重试和详情追踪。 |
> >
> > 列表默认按 `created_at DESC, id DESC` 排序。领单按 `target_key`、`dispatch_status = 'pending'` 和 `production_status IS NULL` 找候选，再按 `priority ASC, created_at ASC, id ASC` 取第一条并锁定。接收区唯一约束冲突时重查原请求号或返回 `target_busy`。
> >
> > **R04 自定义字段与页面。** 共用组、计划本地组、实绩本地组分别 100 个槽位。字符串最长 255 个 Unicode 字符，保留前导零。数值是 JSON number，整数部分最多 10 位，小数部分最多 4 位，末尾零不计。布尔值用 JSON boolean。存储将类型化值转成文本，读取按任务绑定的版本复原。未设置值的槽位省略。`0`、`false`、空字符串作为独立值校验，只有允许清空的字段接受 `null` 并移除该槽位。输入键按模块和版本检查，未知、停用、超限或组别错误整次拒绝。
> >
> > 两个字段设置入口读取同一共享定义和各自的本地组，保存按提交模块和范围合并。当前名称、列可见和顺序属于显示设置，仅变更 `configRevision`。新增、启停或修改写入及回写规则发布新业务版本，任务继续按绑定版本校验。已生效的键名、类型和单位含义通过新键、新槽位替代。停用槽位仍占用容量，恢复用于原字段。保存校验当前版本、修订号、重复键和槽位，陈旧提交返回冲突，完全未变时沿用原修订号。
> >
> > 两个列表复用现有页面路径。计划显示任务号、目标、下发及生产状态、优先级、允许显示的订单或反馈、创建和更新时间。实绩显示任务号、目标、生产状态、允许显示的实际值、有无计划、创建、观测及更新时间。详情按第 6 节读取完整业务值。中文和英文标签从字段定义读，固定文案和状态由 i18n 提供。任务号和目标精确筛选，按对应状态及上海创建时间筛选，先筛选排序再分页。自定义值用于显示。普通列可拖动、横向滚动并支持最小宽度，按模块和稳定列身份保存本机偏好，可恢复默认。刷新保留筛选、分页、列宽及未保存编辑。按 `Asia/Shanghai` 显示 24 小时制秒级时间，观测和更新分列。
> >
> > ## 5. 下单、下发、实绩与回写
> >
> > **R05 任务和计划写入。** 一个部署对应一个项目，两张主表各自对规范化 `taskNo` 唯一。去掉首尾空格并将英文字母转大写后校验 1–50 位英文字母、数字、连字符、下划线或点。建档后任务号固定，返工或重做使用新号。首条同号记录确定版本。普通新建按目标和版本校验项目必填下发参数。MES 对同一任务串行提交和重试，后端按接受顺序应用绝对值。待下发或暂停且无生产事实时更新已提交的合法订单字段、目标、优先级和备注。省略字段沿用原值。同值重发保持原 ID、创建时间和更新时间。领单后、已接收或已开工后，MES 同值重发可成功，订单或备注变更返回状态冲突。获准人工仅可补备注。取消后记录保留查询，同值重发可识别为无变化。补建完成后的普通人工编辑限备注。后端生成状态及其时间。领单、状态流转和修改在同一计划行上核对并发。
> >
> > **R06 领单和报告。** 目标已配置、计划 `pending` 且无生产事实时才进入领取范围。按优先级 1 至 10、创建时间、ID 选取，领取、冻结项目映射的参数和写批次一次提交。同一区域最多一个未结案批次，`exception` 持续占用。CA/FF 首次前保存 `claimRequestId`，超时用原值重试并取得原批次、参数和当前状态。更换目标或执行者复用该 ID 返回冲突。空轮询的下一次请求使用新 ID。当前批次的确认必须与原目标、执行者、原 `requestSeq` 及匹配 `ackSeq` 一致，并保存首次有效读取时间。相同证据重报返回原结果和时间。异常可补报已核实的有效确认，旧批次或冲突证据返回冲突。PLC 接收推进下发状态，生产状态等待实际实绩。
> >
> > | 动作 | 条件和结果 |
> > | --- | --- |
> > | 领单 | `pending` 且无生产事实变为 `claimed`，写原批次。 |
> > | 匹配回执 | `claimed` 或 `exception` 变为 `plc_accepted`，关闭该批次。 |
> > | 报告异常 | 当前未结案批次报告写入异常或结果不明后为 `exception`，继续占用接收区。 |
> > | 暂停 | `pending` 且无开工事实时转 `paused`。普通保存继续暂停。 |
> > | 保存并恢复 | `paused` 且仍满足下发条件时，保存改动并转 `pending`。 |
> > | 取消 | `pending` 或 `paused` 且未被 PLC 接收、未开工时转 `cancelled`，记录原因。 |
> > | 核验退回 | 原批次仍为 `claimed` 或 `exception`，人工有证据确认旧执行停止、在途写入结案、原提交未被接纳且未开工，关闭原批次并转 `paused`。下次领取冻结新参数并生成新批次。 |
> > | 补建 | 从已有实绩生成 `not_required`，带入已知生产状态。 |
> >
> > 人工暂停、恢复、取消和退回提交原 `actionRequestId`、调用人及规范化内容摘要，与状态变更同事务记录。相同身份和内容重试返回原结果。取消及核验退回均要求原因，核验退回另需原批次及证据。证据不足时保留原批次和异常状态。现场 CA/FF 在允许接收时按 `receiveState`、`incomingTaskNo`、`requestSeq`、`ackSeq`、`activeTaskNo` 的逻辑握手执行，先暂存参数再写提交序号。现场凭据、持久记录和重启核对由接入方负责。本版验收以模拟报告覆盖这组后端行为。[现场握手与恢复](../../docs/generic-task-workflow-discussion.zh-CN.md#plc-conditions)
> >
> > **R07 实绩与回写。** SMA 按原任务和配置版本完整提交本流负责的启用自动字段。首条上报按同号计划继承启用、兼容的共享订单快照，之后冻结这份快照。没有计划仍保存实绩。每任务保持一条登记自动流，首条有效上报固定实绩目标和来源。先校验身份、完整快照、绑定版本、字段归属及类型，再按每单正整数序号比较。更大序号且未完成时接受，低序 `late`，同序同规范化内容 `duplicate`，同序不同内容冲突，已完成后更大序号 `already_completed`。`late`、`duplicate` 和 `already_completed` 保留先前业务值、更新时间及回写。完工快照可以是第一份有效实绩。序号和按槽位规范化的摘要与值同存。人工编辑按提交值合并，保留自动序号、摘要及采样时间。
> >
> > 首条和后续有效实绩将本次被接受的共享反馈按槽位同步到同号计划。每个字段按启用、回写开关、兼容定义和写入归属核对。两个本地组及共享订单目标由各自流程保存。生产状态随已接受的实绩事实推进，与下发状态分开。实绩、上报水位和允许的计划更新同一事务提交。任一保存失败全部回滚。回写响应区分有无计划、已写入槽位及跳过原因。换单后的旧快照按原任务号和原采样时间归属。自动和人工更新通过当前行合并各自的槽位，保留并发的合法写入。
> >
> > 先有实绩时，普通计划建档提示走补建。人工补建取同号实绩的绑定版本，提交计划必填项，复查同号记录并由唯一约束防止并发重复。可选回填默认关闭，启用后只从当前实绩复制兼容、启用且允许回写的共享槽位，保留当次合法人工提交。既有实绩的订单快照保持首次建档结果。后续上报按普通回写规则处理。
> >
> > ## 6. 首版 HTTP 合同
> >
> > **R08 入口和行为。** 下列规则适用于本任务的新通用接口。按第 3 节校验人工和集成入口，任务状态和写入归属按第 4、5 节执行。
> >
> > 共用技术模块 `backend/app/task` 负责两张字段配置表、两类字段配置入口、项目调用资格配置及 `task.*` 错误码。计划和实绩使用该模块在 manifest 中声明的公开接口。各模块声明模型及运行依赖，避免运行依赖成环，沿用注册器的错误命名空间校验。这个共用模块只承载已列出的功能和表。[后端模块合同](../../backend/app/MODULE_CONTRACT.zh-CN.md) · [命名空间与依赖校验](../../backend/app/module_preflight.py)
> >
> > | 调用方 | 方法与路径 | 用途 |
> > | --- | --- | --- |
> > | 前端 | `GET /api/v1/plans`、`GET /api/v1/plans/{id}` | 计划分页和详情。 |
> > | 前端 | `POST /api/v1/plans/upsert` | 新建计划或按权限和状态修改已提交的计划值。 |
> > | 前端 | `POST /api/v1/plans/{id}/actions/{action}` | 暂停、保存并恢复、取消或核验退回。 |
> > | 前端 | `GET /api/v1/performances`、`GET /api/v1/performances/{id}` | 实绩分页和详情。 |
> > | 前端 | `POST /api/v1/performances/upsert` | 按权限编辑已有实绩的人工字段与备注。 |
> > | 前端 | `POST /api/v1/performances/{id}/actions/supplement-plan` | 从已有实绩补建计划，可选择回填。 |
> > | 前端 | `GET /api/v1/task-field-configs` | 读取当前或指定版本的字段定义。 |
> > | admin | `PUT /api/v1/task-field-configs` | 保存提交范围的定义并校验修订号。 |
> > | 集成端 | `GET /api/v1/integration/task-field-configs` | 读取当前或指定版本定义。 |
> > | MES | `POST /api/v1/integration/plans/upsert` | 下单或按规则更新同号计划。 |
> > | CA/FF | `POST /api/v1/integration/plans/dispatch/claim` | 原子领取并取得冻结参数，没有待下发任务时返回无任务。 |
> > | CA/FF | `POST /api/v1/integration/plans/dispatch/report` | 报告本批次接收或异常结果。 |
> > | SMA | `POST /api/v1/integration/performances/upsert` | 创建或更新实绩。项目需要时，CA/FF 也可作为指定上报方。 |
> > | MES 或集成端 | `GET /api/v1/integration/plans/by-task/{taskNo}` | 查看订单、下发状态、PLC 接收结果及已回写的生产进度。 |
> > | MES 或集成端 | `GET /api/v1/integration/performances/by-task/{taskNo}` | 查看实际已上报的状态、时间和业务值。 |
> >
> > ### 查询和通用格式
> >
> > | 场景 | 请求与返回 |
> > | --- | --- |
> > | 前端列表 | `page` 从 1 开始，默认 1。`pageSize` 默认 20，上限 100。可选 `taskNo`、`targetKey` 精确匹配、`productionStatus`、`createdFrom`（含）和 `createdTo`（不含）。计划另支持 `dispatchStatus`。`sortOrder` 为 `desc`（默认）或 `asc`，按 `createdAt`、`id` 同方向排序。 |
> > | 列表结果 | `data` 含 `items`、`total`、`page`、`pageSize`、`totalPages`。每条返回固定摘要及配置为可见的业务值，按该条任务的版本解释。 |
> > | 前端详情与集成查询 | 前端按内部 `id` 查，集成端按规范化 `taskNo` 查。详情返回该任务已启用、已保存的全部业务值。计划详情含 `latestDispatchAttempt`，无批次时为 `null`。有批次时含 `dispatchId`、`attemptNo`、`attemptStatus`、`submissionPhase`、`requestSeq`、`ackSeq`、`ackObservedAt`、`claimedAt`。有核对权限的前端详情还含 `failureKey`、`failureDetail` 及最近 20 条 `recentActionEvents`（`actionKey`、`actorId`、`fromStatus`、`toStatus`、`dispatchId`、`reason`、`evidence`、`createdAt`）。 |
> > | 两模块返回字段 | `id`、`taskNo`、`targetKey`、`fieldConfigVersion`、`productionStatus`、`remark`、`createdAt`、`updatedAt`、`syncValues`、`localValues`。计划另带 `dispatchStatus`、`priority`，实绩另带 `startedAt`、`completedAt`、`lastObservedAt`、`observationSeq`、`recordSource` 和 `hasPlan`。 |
> > | JSON 与时间 | 固定键用 camelCase。业务值对象的 `name` 和 `labels` 中的语言键原样保留，如 `value_name`、`zh-CN`。`id`、`actorId` 和配置修订号用十进制字符串，配置版本用整数。采样序号用 1 至 9,007,199,254,740,991 的 JSON 整数，PLC 序号使用同一 JSON 安全上限和现场位宽上限中的较小值，下限为 0。时间带时区提交，保留最多六位小数秒，按上海时间保存，统一返回 `+08:00`。 |
> >
> > 值对象的键来自字段配置。按类型提交简单值，后端保存成槽位和文本，读回时还原为 JSON 字符串、数字或布尔。读到尚无值的槽位时省略该键。前端另读字段定义，根据任务的 `fieldConfigVersion` 取得类型、权限和中英文名。
> >
> > ### 计划写入与人工动作
> >
> > | 入口 | 请求 | 成功结果及限制 |
> > | --- | --- | --- |
> > | 前端或 MES 的计划 `upsert` | 必填 `taskNo`、`fieldConfigVersion`，首次建档还要 `targetKey`。可选 `priority`、`remark`、`syncValues`、`localValues`，MES 另带 `producerId`，可选 `eventId` 用于追踪。 | `data` 含 `outcome`（`created`、`updated`、`unchanged`）和计划摘要 `plan`。同号按第 3、5 节的权限和状态只改提交字段。值相同的重发保留原更新时间。已有实绩、尚无计划时，普通创建返回 `409 task.plan_supplement_required`。 |
> > | 实绩人工 `upsert` | 必填已有记录的 `taskNo`、绑定的 `fieldConfigVersion`，可选 `remark`、`syncValues`、`localValues`。 | 按提交项更新人工归属且可编辑的字段。返回 `outcome`（`updated`、`unchanged`）、`performance` 摘要和 `planSync`。自动采样、开完工事实及实绩创建走自动上报入口。 |
> > | 实绩详情「补建计划」 | 路径为实绩 `id`。必填 `targetKey` 和实绩绑定的 `fieldConfigVersion`。可提交计划值及 `remark`。`backfillExisting` 默认 `false`。 | 校验新增计划权限，按该实绩的 `taskNo` 建为 `not_required`，带入已知生产状态。已存在同号计划返回原计划。`data` 含 `outcome`（`created`、`existing`）和 `plan`。回填见第 5 节。 |
> >
> > 待下发、暂停的计划允许按第 5 节改订单，异常核对期间应用领取后的锁定规则。补建计划的订单值在创建表单提交，补建完成后普通人工编辑限备注。取消后的计划保留供查询，相同值重发仍可得到 `unchanged`。首版 MES 的可编辑值按后端接受顺序更新，调用方按任务串行提交或重试。项目的 PLC 下发映射定义要冻结的字段及其必填值，进入待下发或修改下发参数时按目标和版本校验。
> >
> > 下列动作使用 `POST /api/v1/plans/{id}/actions/{action}`，都带一次操作生成的 UUID `actionRequestId`。
> >
> > | `action` | 额外请求字段 | 后端动作 |
> > | --- | --- | --- |
> > | `pause` | 可选 `reason`。 | 待下发、无开工事实时转为 `paused`。 |
> > | `save-and-resume` | 必填 `fieldConfigVersion`，可选计划编辑字段。 | 计划暂停且仍可下发时，保存改动与恢复 `pending` 一次提交。 |
> > | `cancel` | 必填 `reason`。 | 尚未接收或开工的待下发、暂停计划转为 `cancelled`。 |
> > | `return-to-paused` | 必填原 `dispatchId`、`reason` 和文本 `evidence`。 | 人工核验后，仅对仍在领取或异常状态的原批次退回。后端复查当前批次、无接收和开工事实，关闭批次并转为 `paused`。 |
> >
> > 动作返回 `outcome`（`applied`、`duplicate`）、`taskNo` 和 `resultingDispatchStatus`。同请求号、同操作人、同内容重试时返回原动作结果。重用请求号提交不同内容时返回 `409 task.action_request_conflict`。人工核验的要求见第 5 节。
> >
> > ### CA/FF 领单、重试和报告
> >
> > | 入口 | 必填内容与条件 | `data` 的结果 |
> > | --- | --- | --- |
> > | `dispatch/claim` | `targetKey`、`producerId`、`claimRequestId`。CA/FF 在首次请求前持久保存 UUID，超时用同一 ID 重试。后端按目标从待下发且无生产事实的计划中依次选优先级 1 至 10、创建时间、ID。领取与冻结快照在一个事务提交。 | `outcome` 为 `claimed` 或 `existing_attempt` 时带 `attempt`，含 `dispatchId`、`claimRequestId`、`taskNo`、`targetKey`、`attemptStatus`、`fieldConfigVersion`、`parameters`。接收区已有未结案批次时为 `target_busy`，无符合条件计划时为 `no_task`，两者的 `attempt` 为 `null`。 |
> > | `dispatch/report` | `dispatchId`、`taskNo`、`targetKey`、`producerId`、`outcome`。`plc_accepted` 还要原 `requestSeq`、相等的 `ackSeq` 及 `ackObservedAt`。`exception` 还要 `submissionPhase`（`not_submitted` 或 `possibly_submitted`）、`reasonCode`，并在已知时提交原 `requestSeq` 与可选 `detail`。 | `outcome` 为 `accepted`、`exception_recorded` 或 `duplicate`，另带 `dispatchId`、`taskNo`、`attemptStatus` 和 `dispatchStatus`。 |
> >
> > 同一请求号已领到任务时，重试返回原批次、冻结参数与批次当前状态。同一请求号换目标或执行者时返回冲突。空轮询结果无需存记录，之后的正常轮询使用新 ID。CA/FF 拿到原批次后按本地持久记录判断是继续首次执行还是只核对和补报。已结案批次只能用于查询原结果。冻结的 `parameters` 是按项目下发映射选出的订单参数，键为绑定版本的 `name`。
> >
> > 后端用当前批次、原序号及证据核对报告。同批次同证据重试返回成功且沿用原时间。异常批次取得有效确认后可以补报接收，旧批次或冲突证据返回 `409 task.dispatch_conflict`。下发接收结果与实绩生产状态分别推进。
> >
> > ### SMA 自动写入和回写结果
> >
> > | 请求字段 | 约定 |
> > | --- | --- |
> > | `producerId`、`taskNo`、`targetKey`、`fieldConfigVersion` | 必填。首条实绩记录目标和来源。后续校验同一目标和该目标在项目中指定的上报方，进行中的任务沿用原上报流。同号计划先存在时校验其绑定版本。 |
> > | `productionStatus`、`observationSeq`、`observedAt` | 必填。状态为 `running` 或 `completed`，序号按每单递增。缺实际采样时间时 `observedAt` 传 `null`。 |
> > | `syncValues`、`localValues` | 必填对象。每组提供该流负责、启用的自动字段完整快照，无此类字段时用 `{}`。可清空字段可显式传 `null`。 |
> > | `startedAt`、`completedAt` | 来源有相应实际时间时提交。缺省沿用已有事实，首次未知则留空。`completedAt` 只用于完工快照。 |
> >
> > 先按任务锁定并核对序号及规范化快照摘要。摘要使用校验后的业务内容，按槽位归一化，忽略 JSON 键的排列次序。已接受的有效新快照返回 `created` 或 `updated`。低序返回 `late`，同序同内容返回 `duplicate`，同序不同内容返回 `409 task.observation_conflict`，完工后收到更高序号返回 `already_completed`。后三种成功的忽略结果保持原业务值、更新时间和回写。完工快照可以是第一条有效实绩。
> >
> > `data` 含 `taskNo`、`outcome`、`hasPlan`、`planSync`。`hasPlan` 按项目内同号计划查得。有实际共享值更新时 `planSync` 返回 `outcome: "synced"` 和对应 `slots`。其余返回 `outcome: "skipped"`、空 `slots` 和 `reason`，首版原因键为 `no_plan`、`no_eligible_values`、`no_value_change`、`report_ignored`、`incompatible_definition`。仅部分字段兼容时可另带 `skippedSlots`，每项含 `slot` 和 `reason`。这组结果描述共享值回写，计划的生产状态按已接受的生产事实单独更新。实绩、已接受的序号和允许的计划更新在同一事务提交。
> >
> > ### 字段配置接口
> >
> > | 入口 | 请求 | 结果 |
> > | --- | --- | --- |
> > | 前端与集成的 `GET .../task-field-configs` | 必填 `module`（`plan` 或 `performance`）。可选 `fieldConfigVersion`，缺省为当前生效版。 | `data` 含 `fieldConfigVersion`、`activeVersion`、`configRevision` 和 `fields`。返回共享组与所选模块本地组。前端可读该版本完整定义，集成端读取启用定义。 |
> > | admin `PUT /api/v1/task-field-configs` | 提交 `module`、当前 `fieldConfigVersion`、读取时的 `configRevision` 和 `changes`。每项用 `scope`、`slotNo` 定位，附实际修改属性。新增槽位须给 `name`、`type` 和 `labels`，其余按第 4 节校验和应用默认值。 | 一次合并并校验，返回更新后的当前配置。不同页面修改的是同一组共享定义，列表可见和顺序只改当前模块的属性。过期保存返回 `409 task.config_revision_conflict`。 |
> >
> > 字段项含 `scope`、`slotNo`、`name`、`type`、`labels`（`zh-CN`、`en-US`）、`unit`、`isNullable`、`enabled`、`syncEnabled`、`performanceOwner`、`planEditable`、`performanceEditable`、`planVisible`、`performanceVisible`、`planOrder`、`performanceOrder`。历史任务按绑定版本读取类型、单位并校验业务属性，中英文标签及列表展示按当前槽位设置。保存结果无实际变更时沿用原修订号。
> >
> > 例如管理员在计划页面改共享 03 的显示名。提交 `labels` 时带两个语言键。这次保存只推进 `configRevision`，实绩页面重新读取后显示相同名称。
> >
> > ```json
> > {
> >   "module": "plan",
> >   "fieldConfigVersion": 1,
> >   "configRevision": "2",
> >   "changes": [
> >     {
> >       "scope": "shared_sync",
> >       "slotNo": 3,
> >       "labels": {"zh-CN": "已生产米数", "en-US": "Metres produced"}
> >     }
> >   ]
> > }
> > ```
> >
> > ### HTTP 与错误码
> >
> > 成功使用 HTTP `200` 和项目的 `code`、`message`、`data` 响应形状。应用错误返回匹配的 HTTP 状态及稳定的 `errorCode`，前端据此显示 i18n 文案。下文示例列出业务字段，前端现有标准响应另含毫秒时间戳 `timestamp`。
> >
> > | HTTP | 错误键及触发条件 |
> > | --- | --- |
> > | `401`、`403` | `task.unauthenticated`、`task.forbidden`。前端未登录、缺对应权限，或调用方无字段写入资格。 |
> > | `404` | `task.not_found`。请求的计划、实绩或配置版本不存在。 |
> > | `409` | `task.state_conflict`、`task.field_version_conflict`、`task.config_revision_conflict`、`task.observation_conflict`、`task.dispatch_conflict`、`task.action_request_conflict`、`task.plan_supplement_required`。分别对应状态、版本、配置修订、同序快照、下发批次或请求号、人工动作请求和补建条件。 |
> > | `422` | `task.invalid_request`。字段键、类型、必填值、范围或请求形状有误时整次拒绝。 |
> > | `503` | `task.unavailable` 或 `task.commit_unknown`。服务暂不可用或提交结果未明，调用方沿用原请求身份与内容核对或重试。 |
> >
> > 例如同一实绩序号 12 被报了两份不同内容，返回 HTTP `409`。
> >
> > ```json
> > {
> >   "code": 409,
> >   "message": "task.observation_conflict",
> >   "data": null,
> >   "errorCode": "task.observation_conflict"
> > }
> > ```
> >
> > ## 7. 旧卷材一次性切换
> >
> > **R09 旧入口清退。** 下表 HTTP 路径均相对 `/api/v1`。前端同步清理旧按钮、菜单、直达路由和请求调用。计划及实绩列表、详情的现有路径切换到第 6 节的合同。清退后旧操作从注册路由与生成的 OpenAPI 消失，直接请求不会执行旧行为。模块开关、ORM 注册、服务引用、manifest 模型依赖和导出均需核对。旧代码即使由停用模块保留，运行时也不得注册退役的表或导入会访问旧表的代码。[计划旧路由](../../backend/app/plan/api/routes.py) · [实绩旧注册](../../backend/app/performance/manifest.py) · [模型加载规则](../../backend/app/module_registry.py)
> >
> > | 范围 | 清退的功能和入口 | 旧表及依赖 |
> > | --- | --- | --- |
> > | 计划 | 旧 `POST /plans`、`PUT /plans/{id}`、`DELETE /plans/{id}`。`GET /plans/xlsx/template`、`GET /plans/xlsx/export`、`POST /plans/xlsx/import`，以及 `/plans/linkage/performances/{id}` 下的 candidates、sync-observation、link、backfill。 | 旧 `plans`、固定卷材列和 Excel 映射、`performance_main.plan_id`、两个模型的关联与旧 Service。 |
> > | 实绩基本操作 | 旧 `POST /performances`、`PUT /performances/{id}`、`DELETE /performances/{id}`，旧人工建实绩和自动采集值人工更正。 | 旧 `performance_main`。同名新表按第 4 节创建。 |
> > | 分卷、合卷、追溯 | `/splits`、`/performance-transforms` 及 `/performances/{id}/effective-weight`、`/performances/{id}/lineage-summary`。 | `performance_split`、`performance_transform`、`performance_lineage`。 |
> > | 旧实绩过程、实绩下发 | `/performances/{id}/process-data`、`/performances/push-down`、`/performances/{id}/push-down`、`/performances/{id}/push-down-records`。 | `performance_process_temperature`、`performance_process_tension`、`performance_process_speed`、`performance_push_down_record`。 |
> > | 旧实绩匿名集成 | 四条 POST 路径 `/integration/performances/production-observations`、`/integration/performances/{id}/process-temperature-samples`、`/integration/performances/{id}/process-tension-samples`、`/integration/performances/{id}/process-speed-samples`。 | `performance_integration_receipts`、`performance_integration_observation_events` 及依赖旧表的 storage probe、配置装配和导出。 |
> > | 旧实绩登录版 mapping | `POST /performances/production-observations`、`GET /performances/mapping-records` 及详情、过程数据路径。`POST /performances/{id}/process-temperature-samples`、`process-tension-samples`、`process-speed-samples` 三个对应过程入口。 | `performance_mapping_receipts`、`performance_mapping_observation_state`。 |
> > | 旧报表 | `/reports`、`/assessments`、`/statistics`、`/print`、`/targets` 及报表中按旧实绩关联的质检逻辑。实绩页的分卷、打印、质检和效率入口退场。 | `quality_records`、`defect_records`、`print_records`、`production_reports`、`performance_targets`、`assessments`。独立 `app/quality` 使用的 `quality_inspections`、`quality_defect_records`、`quality_spc_measurements` 及对应 API 在迁移保护范围内。 |
> > | 旧生产首页 | `/dashboard` 旧 API 与 `dashboard.home` 页面退场。登录后按第 3 节优先进入计划列表。 | 清理对旧 `Plan.status`、旧计划字段及最近计划查询的运行依赖。首页自身的统计表不在本次 19 张清退表内。 |
> >
> > 四条设备与监控集成 `POST /integration/equipment/{drive-samples,production-parameter-samples,temperature-samples}`、`POST /integration/monitor/process-curve-samples` 继续按其合同提供。已发布业务集成 v1 的历史 schema、示例和证据保留，在新合同和契约索引标明本任务退出的四条实绩操作与通用入口。旧快照和 Projection 既有清退归原任务。[业务集成 v1 操作清单](../../contracts/published/http-api/business-integration-v1/openapi.json) · [报表模型](../../backend/app/reports/models/reports.py) · [独立质量模型](../../backend/app/quality/models/quality.py)
> >
> > **R10 切换、保护与恢复。** 2026-11-11 的只读盘点显示旧两张主表和上表 17 张配套表均为 0 行，`plan_main` 尚未建立，21 个可见的入向外键约束均来自该表组。当前已验收的采集 dev 基线是 ARCH-ACQ-003 r2，Alembic 版本 `4e6a8b0d2f14`。该记录供准备和对账，执行时重查实际版本及空表前提。[旧表盘点](../../docs/generic-task-workflow-discussion.zh-CN.md#legacy-cutover) · [当前采集基线](../ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收)
> >
> > 1. 在当前正式源码上准备单一后继 Alembic 迁移、对应应用和受控恢复步骤。以实际核对的 dev 前驱为基础，核对元数据和迁移顺序。旧模块退出前先清点同一库的调用方、活动写入方、实际启用配置和数据依赖。C# 学习切片仍映射 `plans`，核查它及其他旧客户端是否连这套 dev。发现仍需旧表的使用方、未知依赖、非空旧表、已有目标表或版本身份不符时，停在迁移前并报告。C# 源码、数据库和启用工作由其原任务负责。[C# 旧表映射](../../backend-dotnet/app/Plan/Persistence/PlanEntityConfiguration.cs)
> > 2. 在 Human Owner 明确批准指定 dev 的操作后，核对库身份、实际 Alembic head、19 张旧表、内外外键及相关记录。记录可恢复的旧 DDL 和受保护对象的切换前证据，确认旧写入方已停止。按依赖顺序先清退旧回执、缺陷、追溯和其他子表，再清退旧实绩及旧计划，建成第 4 节的六张新结构。清退范围以第 7 节的 19 张表为准。迁移记录可复查执行状态，不绕过外键保护。
> > 3. 与新 schema 同步切换应用、旧路由和权限配置。采集 v2 校验实际 Alembic 版本和指定目标，核对并同步采集目标版本登记及被采用的共享业务集成版本兼容配置。保留既有采集数据、来源、准入和权限语义。公开工件仅记录占位配置。实际 dev 私有配置及重启仅按已批准操作执行。[采集版本校验](../../backend/app/plc_facts/v2_config.py) · [业务集成目标匹配](../../backend/common/integration/storage.py)
> > 4. 记录切换前后目标 schema、旧入口退出、新入口可用、登录与采集回归。其他表按预检证据核对，区分已批准的合成采集写入和原有数据。若迁移或部署中断，暂停写入并核实已执行的 DDL、源码和配置。按恢复方案在明确批准后同步还原旧空表结构、Alembic 状态、旧版本应用及相关配置，再对账。新结构有未核实记录时先保全记录并请 Human Owner 决定恢复方案。
> >
> > ## 8. 实施写入范围和交接
> >
> > 下表界定 r1 获批后允许的源码面。实现改动限于本规格明确交付和切换要求。实质增加模块、旧表、接口或验收范围先由 PM 修订并重新提交批准。
> >
> > | 路径 | 用途 |
> > | --- | --- |
> > | `backend/app/plan/**`、`backend/app/performance/**` | 两个业务模块的路由、模型、服务和角色、字段及状态校验。 |
> > | `backend/app/task/**` | 只承接 R08 的共用字段配置、调用资格、错误码及相应 manifest 装配。 |
> > | `backend/app/reports/**`、`backend/app/dashboard/**` | 仅旧卷材报表、旧生产首页、对旧计划实绩的引用、模型和注册退出。 |
> > | `backend/alembic/versions/` | 一条显式后继迁移。历史 revision 归历史证据。 |
> > | `backend/app/plc_facts/v2_config.py`、`backend/common/integration/storage.py` | 仅为本次后继同步目标版本兼容口径。 |
> > | `frontend-js/src/app/plan/**`、`frontend-js/src/app/performance/**`、`frontend-js/src/app/dashboard/**`、`frontend-js/src/app/moduleRegistry.js`、`frontend-js/src/router/**` | 两页、详情、字段设置及双语 locale，旧页面退出、默认入口和实际受影响的路由装配。 |
> > | `backend/tests/**`、`backend/tests_mysql/**`、`frontend-js/tests/**` | 与第 9 节直接相关的源码自检、受控 fixture 和切换回归，保持使用现有 dev 的边界。 |
> > | `contracts/published/http-api/generic-task-workflow-v1/`、`contracts/README.md`、`contracts/README.zh-CN.md` | 从正常后端生成的新通用业务 OpenAPI、合成样例和说明，索引记明本次切换。发布和实际消费者采用按所属批准执行。 |
> > | 本任务 `tasks.md`、`checklist.md`，根 `CODE_INDEX.md` 及受影响的 `backend/README*`、`frontend-js/README*` | 角色事实和实际结构、入口及操作口径变化所需的最小文档同步。 |
> >
> > Development 读取获批的精确规格、实际工作树和受影响的合同。后端使用 `backend-arch`，前端使用 `frontend-ui` 和 `i18n-workflow`，源码结构变化按 `code-document-indexer` 更新索引。Development 记录实际文件、执行证据、迁移边界、已知限制及 `developer_handoff`，再由 fresh-context Verification 独立执行第 9 节。[仓库开发流程](../../.codex/workflows/development-lifecycle-workflow.md)
> >
> > ## 9. 验收
> >
> > Development 自检和独立 Verification 的数据库型验收均使用 Human Owner 指定的现有 dev，走正常 FastAPI HTTP、浏览器及已核对的 MySQL。无 DB 的源码检查可独立运行。验收写入限第 2 节前缀的任务、明确登记的测试配置和测试对象，按实际批准范围保留或清理。对主表做满槽测试可使用同一 dev 内的受控回滚事务，避免为满槽验证发布长期占用的字段定义。旧测试库重建和全表清理 fixture 继续使用自身约定，不可将其连接改指现有 dev。验证输入只用合成数据，现场执行和采集由测试客户端表示。[旧测试库保护](../../backend/tests/conftest.py)
> >
> > | 编号 | 操作 | 通过标准 |
> > | --- | --- | --- |
> > | AC01 | 对已批准 dev 执行实际 Alembic 后继迁移，读取元数据及切换前后证据。 | 核对唯一前驱和新 head。两主表、四配套表、精确列型、默认、检查、唯一约束和索引符合第 4 节。旧 19 张表的旧结构退出，保留对象对账一致。模块通过现有命名空间和依赖校验，模型注册与实际 DDL 一致。 |
> > | AC02 | 在新两表各试写满 100+100 槽，读回值并验证容量、对象形状和清空边界。用两会话分别更新一条实绩的自动和人工本地槽位。 | 200 个值在两表均可写入和正确读回，空对象合法。验证四字节 Unicode 边界。超限、非对象、非法槽位或值被相应层拒绝。两个合法写入均提交，速度和人工检验各自保留。 |
> > | AC03 | 先建 B 再建 A。规范化后重提同号、改部分订单值、重发相同值，再尝试越权、非法值和领取后改值。 | 单表同号一行，省略值保持，同值重试更新时间不变。首版按接受顺序更新，非法和锁定变更整次拒绝。 |
> > | AC04 | 同目标并发领单，检查优先级和时间/ID 次序。重试原请求号、复用到不同目标或来源、领至无符合条件的计划。 | A 优先，按相同优先级的创建时间和 ID 排序。一个区域只一笔未结案批次。重复同一请求返回相同冻结快照与批次。竞争、空队列和冲突分别返回 `target_busy`、`no_task`、约定的冲突。 |
> > | AC05 | 模拟原批次匹配回执、重复回执、错序和迟到的旧批次回执。另以结果不明报告异常，核验退回、普通保存、保存并恢复、重新领单，再核对取消及动作重试。 | 只推进当前证据匹配的下发状态。重复证据保留原时间和批次。异常保留占用，核验关闭后暂停，普通保存仍暂停。恢复后使用新的下发批次。动作记录与状态一同落库，同 ID 改内容冲突，PLC 接收后仍可能是生产未上报。 |
> > | AC06 | 用 admin、带/不带所需 grant 的 supervisor 与 operator、未登录调用，分别操作页面与直调 HTTP。用已登记、未登记的集成来源及关闭入口的配置验证集成调用。 | 第 3 节每项按有效角色、API 授予及状态执行。补建缺任一 grant 被拒，操作员可填写人工实绩但不能执行计划动作。字段配置仅 admin 可保存。核验详情按权限返回，越权混合包无部分写入。开启范围内的已登记来源免前端登录 token，超出范围或入口关闭返回 403。 |
> > | AC07 | 用 A 序号 12、11、重复 12、冲突 12，切到 B 后补交 A 的序号 13，再报 A 序号 14。用测试进程受控制造实绩和计划两次保存之间的失败。 | A 从 300 到 1200，目标一直为 1200，B 始终只接受自己的数据。迟到、同序和完工后结果及时间符合 R07。人工 `true` 和 `false` 独立保留，速度 0 可见。故障时实绩、序号和计划更新共同回滚。 |
> > | AC08 | 分别执行第 2 节 B 的默认关闭回填和开启回填变体，重复补建、检查领单并提交序号 2。 | 无计划先保存实绩，普通创建返回补建提示。两种补建结果分别为空反馈和 50 米，都是 `not_required`，保留正确任务号、版本和实际生产状态，重复补建只有一条，普通编辑限备注。序号 2 在两个变体均回写 60 米。 |
> > | AC09 | 在两个入口读取同一共享定义，分别保存仅标签修改和停用共享 03，测试旧版 A 和新任务、过期配置保存、原槽恢复及冲突键。 | 标签仅改变修订号且两页一致。业务变更发布新版本，旧任务保留其类型、归属与回写能力，新任务使用生效定义。过期保存冲突，已占用槽位和生效过的键继续受规则保护。 |
> > | AC10 | 在真实浏览器核对登录、默认页、两个列表、筛选、详情、表单、字段设置、双语、列宽和刷新。对照实际 HTTP 和数据库。 | 显示来自正常业务 API。固定字段分页排序稳定，显示字段和类型随配置和版本正确解释。页面按第 3 节显示入口，刷新保留选择和未保存编辑，拖宽、重开恢复和默认宽度可验证，时间按上海显示。 |
> > | AC11 | 核对被清退路由及 OpenAPI。对同一 dev 的登录、采集事实 v2 既有范围、独立质量、设备和监控合同做针对性回归。 | 旧卷材操作退出，旧页面及 API 访问不触发旧服务。新接口的候选合同与正常注册后的 OpenAPI 相符。允许范围内的现有采集写入和数据页面继续可用，旧数据与受保护表对账相符。设备、监控和独立质量保留既有路由和权限。 |
> > | AC12 | 执行后端针对性静态/单元检查和前端模块检查、相关测试及构建。复核恢复步骤和真实运行证据。 | 记录实际命令、退出码、输入与结果，验证 HTTP 状态、响应体、数据变化及浏览器行为。样表测试仅供设计证据，正式迁移与模拟链路需按本表独立验收。 |
> >
> > ## 10. 审阅与批准记录
> >
> > | 日期 | 主体 | 决定 |
> > | --- | --- | --- |
> > | 2026-11-11 | Human Owner | 确认两主表命名、既定业务与接口口径，以及总稿 §§10.2、10.3 的一次性旧卷材切换和现有 dev 模拟验收范围，要求按 STD 出 r1 供审阅。 |
> > | 2026-11-11 | PM | 提交 ARCH-TASK-001 r1。新增可复现的 A/B 合成字段和权限矩阵供 Human Owner 核对。 |
> > | 2026-11-11 | Human Owner | 审阅 `ARCH-TASK-001 r1` 草案，SHA-256 为 `54990209a9d4ebc6732d5ae04ecbb24216c251dd7aa419fc7c6a09024fe8a31e`，明确指示「可以开始先做一版本了，后续做完后，你把完整前端、后端、数据库、第三方对接/sma/ca全流程解释一遍。」据此批准精确 r1 源码实施。 |
> >
> > Development 依据获批 r1 实施并记录自检，再移交独立 Verification。现有 dev 用于已确认的模拟验收。候选可审查后，按第 7 节将目标 DDL、应用及配置切换和恢复方案交 Human Owner 明确批准，再执行对应的 dev 操作。最终验收由 Human Owner 决定。交付时说明前端、后端、数据库以及第三方、SMA、CA 对接的完整流程。
> > `````
>
> </details>
> ```````

</details>
