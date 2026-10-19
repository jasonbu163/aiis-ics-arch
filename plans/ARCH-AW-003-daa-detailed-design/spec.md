Task ID: ARCH-AW-003
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved exact ARCH-AW-003 r3 on 2026-10-17; Development to revise only the approved DAA documentation and minimal entries, then new fresh-context Verification; r2 DEV/QA remains historical and r3 Development, independent QA and Human Owner final acceptance are pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 补充 DAA 的 CU 接入、页面布局、组件数据流、上传示例与分阶段实施设计文档
Owner: Automation World
Acceptance Chain Reference: aiis-ics-arch::ARCH-AW-003 r3 scope approval -> Development documentation handoff -> fresh-context Verification -> Human Owner final acceptance
Related Task: aiis-ics-arch::ARCH-AW-001; aiis-ics-arch::ARCH-AW-002

# DAA 详细设计 r3 文档补充规格

## 1. 当前 gate、目标与历史效力

本 r3 是同一 Task ID、同一 bundle 的小幅文档增补。已有总体组件与采集/持久补传链路继续作为设计基线；批准后仅原位修订 [DAA 详细设计](../../docs/AIIS_DAA_Detailed_Design.md)，补齐 CU 消费、页面布局和操作、控制/事实/反馈数据流、DB 包与 HTTP 批次示例及候选实施阶段，并同步最小文档入口。**不重做总体架构，不修改 SMA 正文或 AW Runtime 正文，不实施代码。**

2026-10-17（Asia/Shanghai），Human Owner 的 r3 起草请求为：

> 可以，先出 ARCH-AW-003 r3 spec，把 CU 接入、页面布局、组件数据流、上传示例和分阶段实施补充进去。只改文档，不改代码，批准后再修订 DAA 详细设计并做独立文档核验。

该起草请求当时只授权 r3 draft，不构成对尚未形成的精确范围的批准。PM 随后提交的 r3 draft SHA-256 为 `dc7869e33f2d04b2dbd71dcc130d66a45e2d4f9c9c466f1106041c8a015b6f02`。2026-10-17（Asia/Shanghai），Human Owner 对该精确 r3 明确批准：

> 可以，批准 ARCH-AW-003 r3，按 spec 修订 DAA 详细设计并完成独立文档核验。只改文档，不改代码，后端和 SMA 的具体开发仍留各自会话。

**当前状态是 r3 owner_approved，下一 gate 是 Development 文档交付。** 本次只记录真实批准与交接，R18–R28、AC21–AC35、12 路径、需求/验收/风险范围保持获批 draft 不变；不授予代码、运行或最终验收权限。本轮 PM 只写本文件；主协调可据真实角色事实机械同步第 3 节四个索引的本任务行。DAA/SMA 正文、所有其他交付入口、tasks/checklist 仍保持本轮起点原字节，不提前形成 r3 Development 或 QA 证据。

当前 [tasks.md](tasks.md) 仍为 r2 developer_handoff，[checklist.md](checklist.md) 仍为 r2 qa_passed，内含 r1 历史。这与 r3 spec 的 Revision 暂不一致，是范围批准后、Development/Verification 尚未交付的真实状态；不得为机检对齐越权改写它们。r2 独立文档 QA 通过 AC1–AC20，不代表 r3 通过，也不代表 Human Owner 已最终验收。r1/r2 的最终验收均未发生；r3 Development、fresh-context QA 与最终验收也仍 pending。

### 1.1 保留的批准、交付与核验历史

| 历史 | 效力与可审阅依据 |
| --- | --- |
| r1，2026-10-16 | Human Owner 精确批准 DAA 文档范围，R1–R12、AC1–AC14；Development 和 fresh-context 文档 QA 已交付，终验 pending。批准 spec SHA-256：`f41918ab3fc9da837e2337a75760a464b9fa79efe2236831348931d0c150b19e`。原 DEV/QA 文本与指纹保留在 tasks/checklist 的 r1 历史区。 |
| r2，2026-10-17 | Human Owner 精确批准修订 DAA、新增 SMA 与最小入口；R1–R17、AC1–AC20、16 路径为当时文档范围。批准 spec SHA-256：`a6464506e3e8d86e55cc98415e4a4af9f91ab815598411bc3ec2d26676696537`。r2 已 developer_handoff 且独立文档 qa_passed，终验 pending。 |
| r3，2026-10-17 | draft 已提交，Human Owner 按本节原话精确批准为 owner_approved。新增 R18–R28、AC21–AC35 和 12 路径范围保持不变；原 r2 allowlist 不继承为本版写权限。r3 仅接续本次触及的 DAA 文档范围，r2 既有机制继续受保护，旧 QA 不被重标为 r3；本版 Development、独立 QA 和终验仍 pending。 |

r1 Human Owner 原批准原话：

> 可以，批准 ARCH-AW-003 r1，按 spec 完成 DAA 详细设计文档和独立文档核验。只改文档，不改代码，后端和 SMA 的具体开发仍留各自会话。

r2 Human Owner 原批准原话：

> 可以，批准 ARCH-AW-003 r2，按 spec 修订 DAA 详细设计并新增 SMA 详细设计，完成独立文档核验。只改文档，不改代码，后端和 SMA 的具体开发仍留各自会话。

| r3 起点保护项 | 当前 SHA-256 |
| --- | --- |
| r2 tasks，194 行 | `2e2a0f4e04a22d0bb633698e680d78fbd6c94006613e78b3d03a546031d3f611` |
| r2 checklist，278 行 | `a6f2abb69280d5732f62deda901b3d27918a5eaa0f95cecbca53f52406683cf8` |
| r2 DAA 正文，616 行 | `55a7f8d28548e2e3c95618098086d7e63270b57f49c11ed1dfeb8d5d8b46c22d` |
| r2 SMA 正文，385 行 | `e849bec4a4e29e587f16915b99b7e29d3774355b5d649be3b2f89ac724ea94b7` |
| AW Runtime 正文 | `1d4b34e10c72555fcdbc2850d5ee54ecb43b2507b5c102e1414e35f0ec8d59fa` |

旧 spec 的完整演进默认由 Git 历史追溯；当前外置基线 `/private/tmp/arch-aw-003-r3-pm-mg6i13te/before/plans/ARCH-AW-003-daa-detailed-design/spec.md` 是 r2 原字节审计材料，指纹同上表所述批准 spec。长期批准、DEV/QA 及机制依据仍由本节、现有 tasks/checklist 和设计正文承载，不在仓库另建 r2 副本、归档正文或第二事实源。旧 spec/QA 只作为其精确快照历史，不提供 r3 批准、风险接受或写权限。

本任务保持 `Task Namespace: aiis-ics-arch`、`Classification: root`、`Owner: Automation World`，无 Parent Task ID；相关任务和 CU 后续协作均不转移审批/验收权。

## 2. 必消费依据、现状与设计目标

写入前已读根 AGENTS、README/PLAN 双语、实际 pm TOML、canonical lifecycle workflow、完整 r2 spec/tasks/checklist，docs/AW/DAA/CU 最近 README/PLAN（存在者）、DAA 全文与 SMA 相关边界；使用 `aiis`、其 BLUEPRINT/CONTRACTS 边界及 `project-governance`。docs 由根 PLAN 管理；不为本次补建 docs/DAA/SMA 的 PLAN 或任务目录。技术实现 skill 仅列后续 handoff，不代替对应角色执行实现或运行核验。

以下为本轮只读确认的源码/文档事实，不是本 r3 新能力已实现的证明：

| 入口 | 确认到的现状及正文必须分清的边界 |
| --- | --- |
| [CU 公共代码入口](../../automation-world/console-ui/src/ui/index.ts)、[公共样式入口](../../automation-world/console-ui/src/ui/styles/index.css) | 已导出壳层、顶栏、侧栏、卡片、按钮、状态和主题/语言控件；公共导入不挂载 app、不读偏好、不调用 IPC。消费端负责应用、状态、翻译和业务。 |
| [CU 展示类型](../../automation-world/console-ui/src/ui/types.ts)、[AgentSidebar](../../automation-world/console-ui/src/ui/components/AgentSidebar.vue) | NavigationItem 只有 id/label/icon；侧栏只渲染平铺 ElMenuItem，尚无公共二级导航。r3 只记录 CU 独立能力补齐依赖，不声明已支持 children，不代替 CU 审批。 |
| [CU 公共说明](../../automation-world/console-ui/README.zh-CN.md)、[CU PLAN](../../automation-world/console-ui/PLAN.zh-CN.md) | 公共源码编译消费，宿主运行自身 dist，无需 CU 在线；workbench/locales/草稿/私有样式应用通道不属于消费入口。CU-001–007 的已验收事实不包含 DAA 接入或二级导航。 |
| [公共设计源](../../automation-world/console-ui/src/ui/styles/design-profile.json) | 本轮 cardPaddingPx=18，是当前公共样式快照；不得回写、复制为 DAA 私有默认或把总体设计永久锁死为该数值。以后随明确公共版本消费。 |
| [DAA App](../../automation-world/data-acquisition-agent/src/App.vue)、[既有布局](../../automation-world/data-acquisition-agent/src/layouts/AgentLayout.vue) | 当前仍消费 DAA 自有旧壳层和运行/采集/诊断/授权页面，尚未实际接入 CU 公共出口；既有 YAML/直库、新长连接/双库/API 未实施的效力见 DAA 正文 §1。 |
| [DAA 总体/上传/页面/阶段](../../docs/AIIS_DAA_Detailed_Design.md) | §2 总体链路可沿用；§8–10 已有有界批次与幂等机制；§12 尚未落 CU 两级导航/逐页流程；§16 尚未把 CU 迁移放首阶段。本版只补这些缺口及必要交叉指向。 |
| [SMA 正文](../../docs/AIIS_SMA_Detailed_Design.md) | r2 HTTP 绑定/可靠业务投递设计保持原文；仅作为 DAA 事实上传与 SMA 业务映射的对读依据，不重交付或全量重核验 SMA。 |

聊天预览仅帮助沟通页面与流程；其中点击状态、假数据、像素、频率/容量等数值不是生产默认、API/PLC 证据或获批实现。工作树存在并发修改，各角色须以任务起点基线识别自己的差异，不 reset、整文件回退或整理他人 dirty。

## 3. 分阶段精确 allowlist

以下共 **12 个具体仓库文件**，按角色和 gate 使用；任何阶段均不得仅因文件在表中就跨角色写入。不使用目录通配，不继承 r2 的 16 路径范围。

| 精确路径 | 写入者、时点与允许改动 |
| --- | --- |
| `plans/ARCH-AW-003-daa-detailed-design/spec.md` | PM/Human Owner；PM 起草与真实批准/范围历史。本轮 PM 唯一仓库写入。 |
| `docs/AIIS_DAA_Detailed_Design.md` | 精确 r3 批准后 Development；原位增补本版五项主题及必要导航/效力/交叉引用，保护既有机制，不重写总体。 |
| `docs/README.md` | r3 批准后 Development；仅 DAA 设计行的最小用途/入口说明，保留 SMA 和其他条目。 |
| `docs/README.zh-CN.md` | r3 批准后 Development；与英文 DAA 行对称的最小用途/入口说明。 |
| `automation-world/data-acquisition-agent/README.md` | r3 批准后 Development；仅已有 DAA 目标设计段的 CU/页面/阶段入口说明，保留现状、身份、命令和配置行为。 |
| `automation-world/data-acquisition-agent/README.zh-CN.md` | r3 批准后 Development；与英文目标设计段对称，边界同上。 |
| `plans/ARCH-AW-003-daa-detailed-design/tasks.md` | r3 批准后 Development；增补 r3 计划、实际差异/自检/交接；保留 r1/r2 DEV 历史和指纹，不先写 QA。 |
| `plans/ARCH-AW-003-daa-detailed-design/checklist.md` | 精确 r3 developer_handoff 后，新 fresh-context QA / Verification；增补本版核验/verdict，保留 r1/r2 QA，不继承旧通过结论；Human Owner 可记录真实终验。 |
| `PLAN.md` | 主协调；仅 ARCH-AW-003 唯一行的 Revision/聚合状态/最近验证/下一 gate 机械同步，其他内容保留。 |
| `PLAN.zh-CN.md` | 主协调；同一任务行的中文对应同步。 |
| `plans/README.md` | 主协调；仅 ARCH-AW-003 唯一行，起草阶段标 r3 draft，现按真实批准同步 owner_approved；tasks/checklist 仍为 r2 历史且终验 pending，之后随真实 gate 同步。 |
| `plans/README.zh-CN.md` | 主协调；同一 catalog 行的中文对应同步。 |

**本轮 PM 批准记录只写 spec，主协调可机械同步四索引；正文及角色记录仍由对应角色在其 gate 写入。** 现已获得 r3 精确批准，Development 下一阶段允许写 6 文件（DAA 正文、四个最小入口、tasks），Verification 仍须等精确 developer_handoff 后只写 checklist；这些归属是合同控制，不宣称平台 ACL 或强制路由。

明确字节保护：`docs/AIIS_SMA_Detailed_Design.md`、`docs/AIIS_AW_Runtime_Design.md`、SMA/CU/AW README/PLAN、其他任务 bundle 与全部源码/配置/测试。不得修改白皮书/ROADMAP、AGENTS、角色/workflow/skills、contracts、CODE_INDEX、env/YAML/SQLite、依赖/锁文件、正式 schema/DDL/Alembic；不新增示例工程、UI 原型产物或项目内历史副本。若确有与本版内容不可分的范围冲突，先反馈 PM 修订/重新审批，不顺手扩展 allowlist。

## 4. 本 r3 编号需求

R1–R17 和 AC1–AC20 是 r2 精确文档交付/核验的历史编号，事实保留在原批准快照及 tasks/checklist；本 r3 使用以下新增编号，不将旧通过自动重标。本次只对 DAA 受影响机制按 R26 做语义回归；未改 SMA 的完整重交付/全量重新核验不是本版前置。

### R18. 小幅文档增补与真实 Revision

DAA 正文更新内容修订和本版效力，区分已决定目标、推荐机制、未决正式合同、当前代码和候选未来阶段。保留既有组件/存储/调度设计，仅扩展本版五项主题；不据聊天预览宣称实现。保留第 1 节历史/批准/DEV/QA/终验边界；SMA/AW Runtime 仍为其 r2 设计效力，指向同一 bundle 的旧 r2 链接由历史说明解释，不重写其正文或制造新副本。

### R19. CU 编译期消费及公共能力依赖

DAA 编译时经 CU 唯一公共 `src/ui/index.ts` 与 `src/ui/styles/index.css` 消费 AgentLayout、AgentTopbar、AgentSidebar、ConsoleCard、ConsoleActionButton、StatusCapsule、ThemeToggle、LanguageSwitch 及展示类型；正文标明完整仓库入口与各自职责，示意导入不是本轮源码改动。宿主创建 app、提供 props/slots/事件、拥有状态/IPC/i18n、主题语言偏好与生命周期；通用表格/表单/弹窗按 CU 公共作用域和 Element Plus 约定组合。

不导入 CU 私有 workbench、CU 私有 locale/i18n、草稿/localStorage 或源码写入通道；不复制一套独立公共样式，也不让 CU 承载业务状态、SQLite 或 PLC。宿主可拥有页面布局/业务样式但沿用公共 tokens，不能靠覆盖 CU 组件造第二套设计源。编译需要可访问公共源码和宿主依赖，已构建 DAA 只运行自身产物，不需要 CU 进程或 node_modules 在线；公共源变化经明确版本/同步、宿主刷新或重构建进入 DAA。

当前公共侧栏只有一级。二级/折叠/选中展示能力先在 CU 独立获批任务补齐，再由 DAA 消费；本 r3 只记录需求、依赖和交接，不冻结新 props/type API、不修改 CU、不新建其任务 bundle。cardPaddingPx=18 仅现状说明，不作永久设计常量。

### R20. 固定导航与右侧页面边界

正文应展示以下导航树：

```text
工作台
配置中心（可折叠展开）
 ├─ PLC 配置
 ├─ 点位与采集组配置
 └─ 上报与存储
```

工作台是一级直达页；配置中心是分组入口，展开后子项各在右侧打开独立页面并保持可识别的选中项/标题。不能把配置内部横向一级 tabs 当作这三项侧栏层级的替代；页面内必要的次级分区不扩张为新的主入口。顶部复用 CU 顶栏、主题/语言和必要运行状态；窄窗仍可到达每个子页、操作与日志，不规定固定像素/断点或完整视觉稿。既有诊断/授权门禁等能力应在合适页面或附属面板保持可达，具体旧新入口映射由未来 UI 任务据基线明确，不因导航收敛删功能。

### R21. 四个页面的职责与简单工作流程

正文至少包含逐页的对象、可编辑内容、操作、反馈/准入与不产生的副作用：

| 页面 | 主要对象与操作 | 必须解释的反馈/边界 |
| --- | --- | --- |
| 工作台 | PLC 列表、逐台/勾选/全选连接和采集控制；实例级启动/暂停上报；关键积压/存储概览；采集日志与上报日志同屏，窄窗上下排列 | 连接、采集、上传各自期望/实态/运行准入；逐 PLC 部分成功；待执行/完成/失败有区分；最近可靠确认不等于数据新鲜或历史完整。 |
| PLC 配置 | 稳定 PLC 身份/显示名、IP/端口/rack/slot 等连接配置；保存草稿/校验/应用；逐台连接测试 | 测试复用受管理连接并串行调度；人工断开取消重连；参数变更按版本/轮次边界应用。编辑/保存不自动连接或启动采集，测试不得另开第二连接。 |
| 点位与采集组配置 | 先选 PLC，导入完整 DB/UDT 与来源；手动辅助推算/差异预览和人工修正；点位表唯一 enabled 开关、所属组；组周期与启用；单点诊断 | 完整结构和已采选择分开；一组一个 PLC 可跨 DB、每点最多一组；未分组不采；支持/推算限制明确；诊断不注入生产事实，关闭点不删除历史待传。 |
| 上报与存储 | 一个固定事实 API、凭据引用、独立上传周期；采样保留天数/容量/余量及配置独立保留职责；自动只读 JSON/批次预览和上报测试 | 被采即进上报链路，不再选上报点，不提供任意事实 JSON 编辑；测试用已保存原样本/身份，隔离预览不外发；天数清理不删除配置、未确认或仍被引用材料。批次限额等高级项可收起，不要求用户逐包排程。 |

首次操作流程为“配置并测试 PLC → 导入/编辑点位与组并诊断 → 配置事实 API/存储并校验 → 工作台启动所选本地采集 → 可选的原样本上报测试或直接启动正式上报”；允许先采集本地缓冲再配置/启用上报，不把 API 可用性当采集启动的统一前置。连接准入未满足时明确提示原因/待完成动作；若提供组合操作，须明确表达所请求意图，不暗中把采集、连接和上传三者绑定。

真实上报测试是可选操作，不是配置保存或采集启动的前置。全新实例尚无已持久样本时，只做配置校验/只读预览，明确提示先采样及当前不能进行真实上报测试的原因；不能用诊断或合成数据补成生产样本。启动本地采集产生已持久真实样本后，用户可选原身份/时间/内容测试，也可直接启动正式上报；既有工作台操作路径应支持这一选择，不强制为测试多次往返配置页。此流程不要求新增健康检查 API 或专用测试 endpoint。

日常可停留工作台：暂停采集保留连接和历史上传；暂停上传继续本地采样至有界容量；人工断开只影响该 PLC 的后续读取；已保存队列保留。保存、应用和运行已使用的 revision 分别反馈，不把按钮点击或界面缓存当成功。首版不新增第二套上报点开关、不要求先编辑业务 JSON、不引入流程画布或逐步审批向导。

### R22. 组件职责与控制、事实、状态反馈流

沿用 DAA §2 的总体组件，补一张可独立理解的目标图和配套职责/箭头说明（可一图分区或多图），至少可追踪：

1. **控制流**：CU 组件承载的 DAA UI → Tauri IPC adapter → Rust 配置/运行管理/诊断服务。服务校验准入并执行，CU 只发意图和展示；不冻结 command/event 名称或目录级实现。
2. **配置流**：配置草稿/校验 → config.sqlite → 活跃版本/摘要及激活屏障 → Rust 运行管理；与 runtime.sqlite 解释引用的可恢复步骤一致，不宣称跨库整体原子。
3. **事实流**：PLC 受管理连接 → 按组读取/解码/时间质量 → 采样写入协调器 → runtime.sqlite 本地提交 → 上传器冻结批次 → 一个 Backend 事实 API → 可靠回执与本地确认；容量管理对采样准入/安全清理的控制保持可见。
4. **反馈流**：运行实态/版本、诊断结果、有界采集与上报日志、积压/容量/缺片及可靠确认进度 → 状态快照或事件 → IPC → DAA UI；图中明确回执先由运行时校验持久，再作为反馈，不由 UI 确认事实。

Rust 长运行时拥有连接、采样时钟、写入/上传/容量与恢复；UI 切页/挂载状态不成为采集时钟、事实权威或 queue owner。UI 不直连 PLC、SQLite 或 Backend 事实写入口；凭据不因预览/log 暴露。事件可丢失/合并时由运行快照补齐显示，不能由显示缺失倒退运行事实；日志与订阅有界，不将每轮完整载荷无限推送。窗口关闭、进程退出和后台托管仍按原待决 gate，不由“切页不中断”推定进程退出后持续采集。

### R23. 三个 DB 逻辑包与一个有界 HTTP 批次的示例

正文增补可解析的占位 JSON 和身份/完整性说明，至少覆盖：

| 逻辑包 | 轮次/来源语义 | 本批携带关系 |
| --- | --- | --- |
| PLC_A / DB10 | A 的组 A1 本轮 cycle-A、sourceGeneration-A、sourceSeq-A；稳定 sample-A10 | 与 A/DB20 同组同轮，但各有原实际观察时间/质量和独立 sampleId。 |
| PLC_A / DB20 | 同 A1/cycle-A/sourceSeq-A；稳定 sample-A20 | manifest 明示 A 本轮预期两包或固定片段，不能只确认一包就称轮次完整。 |
| PLC_B / DB10 | B 的组 B1、自己的 cycle-B/代次/序号/原时间；稳定 sample-B10 | 相同 DB 号不冲突；B 的裸 sourceSeq 不与 A 比大小。 |

三个逻辑包在计数/字节限额内可以放入同一冻结 HTTP 批次；超过限额则拆为顺序调度的多个批次，稳定包/片身份和完整轮次仍保持。若单包本身过大，使用正式合同规定的固定分片/manifest，不能临时截断 JSON、改 sampleId 或把每次 HTTP 当新采样。示例列清 cycle、sample/片、pointId 点结果及 batch 四类身份，不丢中间样本，不把跨组/DB/PLC 组合冒充同一物理瞬时帧。

字段是语义占位，清楚标示“非可执行 schema、API 路径或限额承诺”；不把示例包装和数值发布为正式合同。每点仍用单份自描述 points 字典；没有新增持久无值目录。预览和重试都保原事实身份、时间、版本与内容，批次一旦冻结成员/内容不变。

### R24. 在途请求、可靠确认与后端责任

首版推荐全实例一个 HTTP 请求在途；常规扫描/组批由上报周期与样本数/字节/速率预算驱动，采集周期另设。等待回执有界；失败/超时结束本次等待并记录结果/退避后，给其他 PLC/组/合格批次调度机会，不在坏批次中无限阻塞。此为客户端并发/调度建议，不证明超时的服务端工作已取消。

正文给出“HTTP 响应/可靠持久确认/DAA 本地状态”的对应表：仅 HTTP 200/202、发送完成或易失入队不使样本已确认；校验可靠回执覆盖身份/内容/范围后，本地短事务更新单调 ack。无可靠回执/本地确认提交失败保原身份重试，后端已保存丢回执仍去重。整批原子确认沿用 r2 首版建议；混合持久成功/重复/拒绝/过期、逐成员 ACK、历史回执和批次退休的最终矩阵由 Backend 正式合同定稿，DAA 不从一个状态码猜结果或修改旧冻结批次。

最新优先与历史公平继续适用。raw 去重、同 ID 异内容拒绝、来源/定义条件推进 latest 与旧包防倒退由 Backend 合同保证，不能用客户端“按顺序发送”替代。DAA 只投一个事实入口，SMA 映射后的业务请求按目标规则/API 组织，可跨 DB 绑定但受其质量/时效/多源策略约束；不强制跟随 DB 拆包。本版仅说明分层，不新增或开发 SMA 机制。

### R25. CU 迁移在先的三个候选实施阶段

正文以“范围/依赖/完成证据/回退边界”表表达未来阶段，均为以后需独立 spec 批准的候选，不是本 r3 自动实施授权：

| 阶段 | 候选范围与依赖 | 后续完成证据与回退边界 |
| --- | --- | --- |
| A：CU 接入与既有界面迁移 | 先记录现有 DAA 构建/启动、功能入口和外部 I/O gate 基线；CU 独立任务补公共二级导航，DAA 另项消费公共壳/组件/样式并按 R20 归位既有功能。正式事实/回执合同可在此期间由 Backend 会话并行收敛。 | 自身构建/启动、主/子导航、主题/语言、适配及既有功能/gate 可用的定向证据；缺失的新保存/采集/上传功能明确标示，不能假保存/假成功。回退仅恢复获批 UI 差异与既有接口映射，不迁移/重置用户配置或队列，不改采集语义。 |
| B：本地采集闭环 | SQLite 配置权威/草稿激活、完整 DB/UDT 与受限地址支持、多 PLC 唯一连接/采集组、全结果本地事务保存、容量/重启恢复；驱动/类型/规模/最小周期及存储参数由本阶段技术 spec 确认。 | 用获批的脱敏/受控夹具证明界面配置可真实保存/生效、独立采集和本地历史/待传队列恢复，容量有界；不要求 Backend 或 SMA 实现完成。新旧配置/库不静默互写，二进制/schema 回退须兼容证据。 |
| C：可靠事实上传闭环 | Backend 正式请求/身份/manifest/回执/拒绝/限额合同先稳定；DAA 上传器与 Backend 新事实 API 分别获批实现，再联调最新优先/补传、去重/latest、过期/缺口。 | 受控断网恢复/重启/丢回执/乱序和公平补传对账证据；接口、持久边界与双方实现核对。旧直库/新 API 不对同一来源同时有效写入，切换/回退另有批准和在途/进度核实。 |

CU 能力未补齐不阻塞本 r3 文档，也不阻止阶段 A 的基线/映射准备；但不能宣称最终两级导航已完成。SMA 具体实现不作为 DAA 首版前置。真实 PLC/TIA、长期性能/资源、原生打包/分发、后台托管、生产数据库迁移和旧链路切换仍独立批准；每阶段自检、独立验证和 Human Owner 验收分层。首阶段不趁 UI 迁移同时引入新采集/上传/SQLite 语义。

### R26. r2 DAA 关键不变量回归保护

只读对照 r2 起点及共同接口边界，确保本次图文/示例/操作/阶段调整不改变以下语义；不是重新实现或全量重交付 SMA：

| 保护面 | 不得被本次补充削弱的约束 |
| --- | --- |
| 多 PLC/连接 | 一个实例多 PLC、每 PLC 一个受管理连接，采集/诊断串行共享且有界公平；人工停连/异常重连、采集/上传意图分开。 |
| 结构/组 | 完整 DB/UDT 导入、手动受限辅助推算与人工差异确认；组单 PLC 可跨 DB、点最多一组、唯一 enabled；组独立周期、不重入、不补造错过数据。 |
| 双库/激活 | config/runtime 分开、短事务与单写协调、可恢复激活屏障；配置回退不删样本/倒退序号/ack；内存加载与持久 active 不混为成功。 |
| 全样本/容量 | 实际结果本地提交起受持久保证；未确认/需处理及冻结/未完整引用保护，满额暂停新增采集、上传继续，低水位只恢复原运行意图；WAL/日志/索引/维护余量计预算。 |
| 身份/重试 | 原 sample/point/cycle/batch 身份与内容稳定，冻结批次可交叠、ack 单调；丢回执不假确认，安全清理不毁重试材料；最新优先仍给历史公平机会。 |
| 来源/顺序/完整性 | 代次受控交接、PLC 内 sourceSeq 持久、跨 PLC 不比较；manifest/分片完成、质量失败/缺片及组过滤跳号区分；B 完整前缀不是 M 最大序号；Backend 安全 feed 不因并发晚提交漏读。 |
| points/目录/定义 | 单份自描述 points、pointId 原样保留；目录查询派生、多组聚合、无永久无值目录；显式成员/定义变更，旧历史不倒灌当前；SMA 签名排除值/质量/时间，无关 revision 不全停，物理 PLC 未上报变更不可自动证明。 |
| 保留/业务/兼容 | UTC 原采集时间加最多三自然月，逐点到期、不按接收续期；到期拒绝不假 ack/自动删保护；业务可靠持久确认/独立 outbox 不被源 TTL 级联清；旧标量适配、唯一 writer 和切换另批。 |

保留原 F01–F30 的编号、有效场景与三方共同责任语义；可在相关行补指向新页面/例子，但不借 UI/CU 增补改写 SMA 设计或要求其重新全量核验。r2 R12–R15 的 SMA 内部细节仍由未改 SMA 正文及历史 QA 承载，本版只核对 DAA 共享边界和字节保护。

### R27. 文档质量与本版独立核验

正文至少包含导航树/逐页职责、首次及日常操作流程、组件/控制/事实/反馈图、三包入批 JSON/身份说明、响应语义表和阶段表；可以按现有章节嵌入，不建立第二份平行设计。图、表、示例和文字互相一致，术语与来源/完整性/可靠确认分层；示意 JSON 可解析但不声称符合未定正式 schema。

Development 记录本版 self-check/实际命令/退出码/限制/指纹/差异和 r1/r2 历史保存；fresh-context Verification 对新增 AC、R26 受影响关键不变量、本地链接/显式锚点、双语最小入口、围栏/表格、JSON 语法、允许路径及保护字节独立审阅。检查未跟踪全文，不以空 Git diff、关键词或旧 QA 替代语义审查。Mermaid 如仅检查文本须如实说明，不能声称已渲染；不为纯文档检查安装依赖或运行应用。

### R28. 串行 handoff 与技术边界

当前止于 PM draft 和 Human Owner 范围批准；批准后实际 Development 只做文档和 tasks，形成精确 r3 developer_handoff；主协调随后显式启动新的 `verification`、fresh context（支持时 `fork_turns="none"`），只核验并写 checklist。r3 qa_passed 后才进入 Human Owner 最终验收。不得用 r2 QA、主会话自检或角色提示替代本版独立文档核验，不伪造批准/验收/角色执行。

当前/未来文档治理用 `aiis`、`project-governance`；具体 Rust/SQLite/采样/上传实现交 `rust-runtime`，Tauri 壳/IPC/原生生命周期交 `desktop-tauri` 并结合 Rust，PLC 点位/导入/偏移交 `plc-point-mapping`，CU/DAA Vue 与用户文案交 `frontend-ui`/`i18n-workflow`，正式 Backend API/数据库交 `backend-arch`。只在对应任务表面适用时加载，不为本版设计预先实施这些内容；不恢复 Celery/Redis，不联系其他会话或代其接受任务。

## 5. r3 文档验收标准

以下均为批准后的 r3 文档标准，尚无本版 Development/QA 通过事实。AC21–AC35 为新增编号；AC1–AC20 只保留 r2 历史，不要求未改 SMA 完整重交付。

| AC | 可独立审阅的结果 | 对应需求 |
| --- | --- | --- |
| AC21 | 正文为小幅 r3 增补，现状/目标/推荐/未决/未来效力清晰；r1/r2 批准、交付、QA、终验 pending 可追溯，未继承旧批准/QA。 | R18 |
| AC22 | CU 两个公共入口、八组件/展示类型与宿主 app/state/IPC/i18n/样式分工明确；未导入私有内容、复制公共样式或引入在线 CU 前置；18 仅现状。 | R19 |
| AC23 | 当前平铺侧栏与目标可折叠二级能力分清，CU 独立任务前置/责任清楚，无已实现或本轮 CU 实施/审批声明。 | R19–R20 |
| AC24 | 一级工作台/配置中心及三个二级独立页面准确，右侧页面/选中标题关系和窄窗到达性明确，不以内部 tabs 替代；既有能力保持可达。 | R20–R21 |
| AC25 | 首次配置测试到采集/上传、日常独立控制可完整推演；部分成功/待执行/实际状态分清，暂停/断开/队列影响及允许先本地采集明确。 | R21 |
| AC26 | PLC/点位组/上报存储各页字段职责、草稿/应用/实际版本、共享诊断连接、唯一启用开关、只读 JSON 和保护清理边界完整。上报测试可选且须已有持久样本：无样本只校验/预览并提示先采样，采样后可原身份测试或直接上报，不强制多次往返；无假保存、诊断/合成生产样本、任意事实编辑或新增测试 endpoint。 | R21 |
| AC27 | 总体图与职责说明可追踪 CU UI→IPC→Rust 控制、配置版本屏障、PLC读取解码→本地提交→上传→Backend，以及回执/容量管理；无跳过本地持久或跨库整体原子暗示。 | R22 |
| AC28 | 实态/有界日志/积压/确认进度快照或事件回 UI 完整；UI 不是采样时钟/队列/事实权威，无浏览器直连PLC/SQLite/事实写入，切页与进程退出/托管边界不混。 | R22 |
| AC29 | 存在可解析的三包合批 JSON：A DB10/DB20同组同轮、B DB10独立；包内自描述点和包/批/轮次/点身份可核对；示例明确非正式协议。 | R23 |
| AC30 | 限额拆批/超大固定分片和 manifest 完整性可推演，不丢中间样本、不造同步帧、不比较跨PLC裸序号，冻结/重试保持身份内容。 | R23/R26 |
| AC31 | 单在途首版建议、超时/退避释放调度、可靠提交与HTTP200/202区别和本地ack单调明确；混合/过期/部分确认待正式合同，latest防倒退/去重归Backend。 | R24 |
| AC32 | 三阶段范围、依赖、未来完成证据与回退边界齐全；CU独立能力与DAA迁移在先、合同可并行但上传前稳定、SMA不作前置，现场/长稳/原生/切换仍另批。 | R25 |
| AC33 | 按R26逐项对读起点与修改后DAA：连接/组、双库激活、容量、冻结身份、来源完整性、三自然月、单份points/目录/漂移、单writer等无回归；F01–F30及SMA共享边界保持。 | R26 |
| AC34 | 本地链接/锚点、双语最小入口、围栏/表格、JSON语法与图文一致通过并有真实结果/限制；不把语法或文档QA当正式schema/运行通过。 | R27 |
| AC35 | 12路径按阶段/角色审计通过，SMA/AW Runtime及其他保护面字节不变，历史保留；r3 DEV self-check、新fresh QA、Human Owner gate分别真实记录，无越界实现。 | R18/R28/第3节 |

## 6. 未来文档核验的反例输入

以下只要求设计可解释，不执行运行/故障实验；在保留 F01–F30 的基础上覆盖本版容易引入的误解：

| 反例 | 文档必须给出的边界 |
| --- | --- |
| CU 已停止、DAA 切页或 UI 暂时断开订阅 | 已构建产物不依赖CU在线；运行状态由Rust保持并可重新取快照，不能把切页等同进程退出后继续运行。 |
| 配置中心二级未完成或新字段尚无持久服务 | 不宣称公共侧栏已支持；阶段A缺口显式显示，不假保存/假启采，旧能力/gate仍可达。 |
| PLC_A DB10与PLC_B DB10同批；A的DB20被拆到下一批 | 来源/包身份不冲突；A轮次仍等待预期成员，不因前一请求完成就声称完整。 |
| 后端已存但HTTP回执丢失、或仅200/202入队 | 原身份内容重试/核实，未获可靠确认不ack；旧包不能靠到达顺序覆盖latest。 |
| 一个批次拒绝/过期或某PLC持续故障 | 退避/隔离释放合法调度，历史有公平预算；拒绝不假ack、不自动删本地保护，混合结果待正式合同。 |
| 点位关闭、上传暂停或保护数据满额 | 关闭不删旧队列；上传暂停仍采至额度；满额安全停新采样并显式缺口，不能无限断网无损。 |
| 把DAA包当SMA业务请求、或先等SMA全建完 | 事实包与目标业务API边界分层，SMA实现不阻塞DAA本地/事实上传阶段。 |
| UI迁移时顺带换旧直库、新API或重置配置 | 阶段A只迁UI与既有接口组合；新语义和单writer切换各有独立范围与回退gate。 |

## 7. 风险、待决与回退

- **公共CU与宿主版本不匹配**：正文要求消费明确公共源码/样式版本，二级能力独立交接，宿主构建验证；不复制私有实现绕过依赖，也不在本版冻结新组件API。
- **界面就绪被误认采集链路就绪**：逐页区分既有能力与尚未实施功能、请求与实际状态；阶段A有旧功能映射和缺口说明，页面预览不作生产证据。
- **图文弱化可靠性**：控制/事实/确认/反馈分层，R26及反例逐项回归；包/轮次/请求、HTTP/持久ack、最新/完整性分别说明。
- **新例子被误当正式schema或默认规模**：占位字段/ID及限额均标示语义；Backend正式合同在上传实施前由其任务确认，不向后端或SMA代发开发指令。
- **文档修订扩散或历史误判**：12路径/阶段/指纹审计，SMA/AW Runtime字节保护；r2通过只保历史，r3 QA须fresh context，Human Owner终验待真实决定。

原驱动/CPU/访问/类型/导入支持矩阵、最小周期/规模、SQLite选型/schema/额度/水位、凭据/备份、正式字段/manifest/回执/错误码/身份代次/去重窗口、安全feed/TTL清理SLA、平台后台生命周期等继续由对应实施spec定稿；SMA内部参数维持其r2待决。本版不把这些工程选择全部推回Human Owner逐按钮决策，也不以它们未定为由继续无限扩张总体架构。

文档回退仅针对本任务实际新增/修改段落，保留当前并发内容、历史QA与指纹；不执行未知归属整文件覆盖/删除。未来UI与运行/schema回退分别按阶段候选说明另批，文档通过不授权真实回滚或切换。

## 8. 当前交接与批准后的顺序

1. **已完成的起草阶段**：PM提交r3 draft，主协调仅机械同步四索引本任务行；当时等待Human Owner精确范围批准，r2正文/DEV/QA保持原字节历史。
2. **当前精确批准交接**：Human Owner已于2026-10-17按第1节原话批准r3，PM如实记录owner_approved与历史，需求/验收/风险及12路径不变。主协调下一步调用实际Development，消费完整bundle、当前正文/基线和批准指纹，在6文件范围内完成文档及DEV self-check；本次PM批准记录不代表该交付已经发生。
3. **r3 developer_handoff后**：主协调显式调用新的fresh-context Verification；独立核验AC21–AC35、R26受影响回归、指纹/diff/历史/入口，保留旧checklist后记录本版verdict，不修实现。
4. **r3 qa_passed后**：进入Human Owner最终验收。未来CU/DAA/Backend实现任务、真实设备/数据库/发布动作不随文档批准或验收自动启动。

本任务只进行文档/本地文本检查，不安装依赖，不构建/启动工程，不跑项目测试/PLC/HTTP/API/数据库/迁移/Docker，不推送/发布、联系其他会话或操作真实profile。需要外部技术事实时由对应后续文档角色在批准范围内核对官方来源；本版新增结论主要依据当前本地CU和DAA源码。

### 修订记录

- r1 draft/owner_approved/developer_handoff/qa_passed，2026-10-16：原DAA文档交付与独立核验；Human Owner未终验，历史见第1节和tasks/checklist。
- r2 draft/owner_approved/developer_handoff/qa_passed，2026-10-17：DAA修订与新增SMA，独立文档QA通过AC1–AC20；Human Owner终验pending，原批准/指纹见第1节。
- r3 draft，2026-10-17：起草本spec，新增CU/导航页面/数据流/上传例子/三阶段要求，收窄12路径；起草阶段正文与tasks/checklist未改，当时精确范围批准、r3 Development、fresh QA及最终验收均pending。
- r3 owner_approved，2026-10-17：Human Owner按第1节原话精确批准r3；本次PM仅记录元数据、批准/起草历史和当前交接，R18–R28、AC21–AC35、12路径及需求/验收/风险内容保持不变。r3 Development、新fresh-context文档QA和Human Owner最终验收仍待各自gate。

本profile为contract_only；主协调、完整bundle、精确handoff和diff审计是必要合同控制，不宣称平台ACL、强制路由或完整Agent Team激活。
