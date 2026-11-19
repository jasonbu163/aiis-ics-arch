Task ID: DS-004
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 device-simulator::DS-004 r3、aiis-ics-arch::ARCH-PLC-001 r8 及版本衔接 -> Development 仅整理既有资料并更新 tasks.md -> fresh-context Verification 仅独立文档复核并更新 checklist.md -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: root
Capability: DS 本机点位中英文显示名称基础的既有证据收尾
Owner: Device Simulator
Acceptance Chain Reference: Development Lifecycle Workflow；本任务独立按精确 Revision 范围批准、Development、fresh-context Verification 和 Human Owner 最终验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r8; aiis-ics-arch::DAA-018; device-simulator::DS-005; aiis-ics-arch::DAA-019
Depends On: Human Owner 已在同一决定中分别精确批准本 r3、ARCH-PLC-001 r8 及版本衔接；本任务批准并非由父任务自动继承，二者最终验收仍各自独立。

# DS-004 r3：既有本机双语证据的有界收尾（范围已批准）

## 1. 目标、范围与状态

Human Owner 要求按 STD 使用已完成的手动验证和实际上报证据收尾，不再重复测试，并保留历史记录和现有数据。本 r3 是对 DS 本机双语点位基础功能**既有证据及限制**的已批准文档收尾范围：只整理 Owner 报告的本机操作、Development 和独立 QA 原有记录，以及与之相关但不能相互替代的跨应用证据。验收只讨论已完成的本机双语基础和历史记录审阅，不增加代码、运行验证或新的产品能力。本 r3 的范围批准不代表问题已修复、`qa_passed` 或 Human Owner 最终验收。

原 r2 对 DS4-01～15 的完整验证，尤其 DS4-07 原生检查及真实关闭/重开，仍有未完成部分。已批准的本 r3 **改变本次收尾的验收口径**：不要求为填补这些缺口重新执行测试，但必须逐项标记证据等级和未证明边界，再由 Human Owner 明确决定是否接受这些缺口及其风险。不能把原条件描述为已满足、已延期完成或原 r2 产品 QA 已通过。本次最终决定只可针对被批准的有界范围，不能外推到完整 r2 合同或全场景。

[ARCH-PLC-001 r8](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 是同一收尾事项的关联父设计；本 PM 形成草案时读取的父文件 SHA-256 为 `a0fdfabbaeebdd95f8bc39fd9f2a0c3b974c13ec5a6b15fe39b6b834aba0eac3`，当时状态为 `draft`。此后 Human Owner 在同一决定中明确批准父 r8、本 r3 及版本衔接，父 r8 的批准不是本任务批准的自动继承。本任务仍有独立 Task ID、批准与最终验收链，其他任务的 QA 不能转移给 DS-004。r1/r2 原批准、QA1–QA3 的 `qa_failed`、r2 QA4 的 `qa_blocked` 和隔离事件均作为历史保留；本任务尚未最终验收。写前 r2 全文及其内的 r1 原文按原字节保存在本文附录。

## 2. 可引用的现有事实与证据身份

1. **Owner 本人报告。** Human Owner 报告曾在 DS/DAA 各自 `.local/dev` 中操作中英文切换和 `display_name`，并在后续实际操作 DAA→DS→DAA 文件往返。本 PM 未亲历或独立截获这次界面操作或 IPC；只按 Owner 实际报告的范围引用，不能推成每个编辑、保存/重开、字段格式或所有异常分支均已验证。用户使用的 `display_name` 是此处对报告用词的引用，不据此断定它具体指旧无语言 `displayName` 还是新双语 `displayNames` 的所有状态。
2. **原 DS-004 Development 与 QA。** [tasks.md](tasks.md) 记录 r2 精确候选、自检及其内存/合成边界；[checklist.md](checklist.md) 保留 QA1 F1、QA2 F2、QA3 F3/F4 失败及各轮复核。QA4 对当时精确候选的 Rust、内存 UI、故障注入和合成 profile 等局部检查有其限定结果；整体仍为 `qa_blocked`。这些原时点证据不能自动覆盖后来叠加的工作树或代替原生 IPC 和 GUI。QA4 中受控合成兼容探针不等于旧普通原生程序和所有 profile 的兼容证明。
3. **跨应用文件记录。** [DS-005 checklist](../DS-005-plc-json-bidirectional/checklist.md) 和 [DAA-019 checklist](../../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/checklist.md) 记载各自的历史观察、实际文件比较和局部核验；DAA-019 QA3 记录三份文件按规定去除导出头、连接目标及两端启用字段并按外部身份排序后，技术字段、双语与描述相同。该记录属于当时的特定文件和归一化范围；Owner 报告的自动选中及原生界面操作不能与其他轮次结果拼成同一次 IPC 返回的独立直接证据。旧临时工件已按 Owner 要求清理，后续只能引用现存记录；不能宣称重新核验已删除原件。
4. **协调者转述的上报观察。** 父 r8 §2 记录协调者对 2026-11-18 一次本机 DAA dev 只读核对的转述：seq 91–103 共 13 条 v2 样本各有匹配 `sampleId` 的 `status=committed` 回执，`outcome` 为 `created` 或 `duplicate`；所核服务端历史的来源身份、正文 SHA 和点位名称/类型/值/质量匹配；指定时点 latest 有 3 点质量 `good`。该样本配置中一实际点的中英显示名均非空；13 份请求正文均未见中英文显示名字段和对应文本。服务端所核点数据未见显示类字段，指定点字段及值一致；未对服务端任意字段字符串进行通用搜索。私有证据定位、身份和详细限定见父 r8 §2；本 PM 未亲自读取应用、数据库、网络、日志或原始回执。这只是特定 DAA 样本和时点的受控观察，不证明 DS 未测行为、全部上报路径、旧程序兼容或旧数据历史前值。不得把私有正文、点值、地址、身份或凭据复制进仓库。

## 3. 未验证边界与风险，由 Human Owner 评估

- QA4 时真实 macOS 原生编辑、顶栏切换、列宽拖动、跨重启记忆/复位、普通入口和正常关闭后同一 profile 重开未完成独立验证。后续 Owner 的本人报告只证明其报告的操作；不能把它扩大为独立 QA 对全部原生 UI、跨重启或异常关闭的验证。崩溃、强制退出、实际 Tauri IPC/JoinError、跨进程原子性及无法确定终结的保存/释放回执也没有完整原生证明。
- QA3 的 F3 无本次保存直接交错的旧通用 apply/write/preview 未知结果清除风险，r2 明确没有声称修复。QA1–QA3 的失败历史及 QA4 所测范围的复核均须保留；不得因为缩小验收范围而将 F3、未覆盖时序或原先 `qa_failed`/`qa_blocked` 改写为整体通过。
- 另一任务的原生隔离事件影响未知；原记录并未证明无写入或无影响。历史数据、profile、版本、原有配置和任何真实记录须保全；后续可比基线不能倒证较早一轮缺失的逐行前值，也不把某轮允许新增的记录称为零写。
- 单个旧二进制合成 probe 的结果不代表旧版普通原生应用的全部兼容、错误恢复或不误开空 profile 已获证明；本 r3 不触及旧 profile、DDL、迁移或修复。无法证明的具体资料和已清理工件必须明确列出，不制造替代证据。
- 真实 PLC、FF/CA、现场、Windows/其他平台、长期稳定性、生产采用、发布或部署均在本范围外。样本上报不代表上述场景或所有点位/时序已验证。

Human Owner 已批准本 r3 所列以既有资料整理替代原 r2 尚缺新增实测的有界收尾范围及对上述缺口和风险的记录、独立文档复核路径；这不表示问题已修复或隔离事件影响已经确定。是否最终接受该有界收尾、对旧 F3 和隔离事件是否另行处理，仍由 Human Owner 决定，不能由 PM、Development 或 QA 推定；最终验收需在新的独立文档 verdict 后单独决定。

## 4. 文档收尾要求与验收标准

本 r3 的判定对象是证据归属和文档交接；下列标准不要求证明原 r2 各项产品验收已通过。

| 编号 | 待独立文档核对的验收标准 |
| --- | --- |
| R3-01 | 指明 `device-simulator::DS-004 r3`、关联父 `aiis-ics-arch::ARCH-PLC-001 r8` 的精确批准状态和独立验收链；列出历史 r1/r2 的批准、QA1–QA3 `qa_failed`、QA4 `qa_blocked` 与尚待 Owner 决定的最终验收，保留历史原文及其时态。 |
| R3-02 | 以 Owner 报告、Development 自检、历史独立 QA、协调者转述分别标注来源；记录本机语言切换/显示名、文件往返及 13 条 DAA 上报观察各自的具体范围，不写成 PM 或本轮 QA 亲见，不以报告代替缺失 IPC。 |
| R3-03 | 审阅现存 DS-004 tasks/checklist、相关跨任务历史记录及本 r3 文档 diff，明确 QA4 合成检查的精确候选与未完成原生检查；记录旧 F3、未知结果、隔离事件影响未知、旧版原生兼容和旧历史前值等缺口，不用后续事实倒证旧轮。 |
| R3-04 | 确认本次只使用既有资料，不运行、重跑或要求用户重复任何测试；不启动或附着应用、GUI/CUA、访问 `.local/dev`、profile、数据库、PLC 或网络，也不重发数据或重新生成已清理工件。现有资料不足时保留未知，不伪造证据。 |
| R3-05 | 审核下述角色各自写入范围与 handoff：Development 在既有 tasks 追加真实资料来源、工作树/diff 身份、未运行项和风险，fresh-context Verification 在既有 checklist 追加独立文档核验、verdict 与未证明边界；历史批准、失败、阻塞及事件不删除、不覆盖。 |
| R3-06 | 如文档与现有证据不一致、将不可访问的资料误称已复验、证据来源无法识别、风险描述不足或 R3-01～05 不能满足，Verification 如实给出 `qa_failed` 或 `qa_blocked`；若通过，`qa_passed` 仅代表本 r3 文档收尾要求通过，不代表 r2 全面产品 QA、原生 gate、现场或最终验收通过。 |

## 5. 写入范围、角色 handoff 与排除项

- **PM 本阶段：**仅修订本任务 `spec.md` 形成 r3 并记录范围批准，不修改既有 `tasks.md`、`checklist.md`、任何实现、测试、手册、配置或计划索引。原 r2、r1 在附录中完整保全。
- **Human Owner 范围 gate：**Human Owner 已在同一明确决定中分别精确批准 `device-simulator::DS-004 r3`、`aiis-ics-arch::ARCH-PLC-001 r8` 及二者版本衔接，原话和本任务审阅前草案摘要见 §6；不是以其他任务批准推断本任务批准。批准只授权此处文档交接，不授权产品更改、补测或最终验收。
- **Development（仅在本 r3 精确批准及衔接后）：**只在本任务既有 `tasks.md` 追加文档整理、既有证据引用、身份/差异检查、限制和 `developer_handoff`，保留原文。禁止修改代码、测试、手册、配置、数据库、profile、历史或其他任务；不运行任何产品测试、构建或应用，不要求用户重复操作。若现有材料不足，记录缺口并交回，不扩大写入范围。
- **fresh-context Verification（handoff 后）：**独立对照本 spec、原始任务记录、可取得的既有文档与文档 diff，只在本任务既有 `checklist.md` 追加 R3-01～06 复核与真实 verdict；不得访问应用、profile、数据库、GUI/CUA、设备或网络，不重新测试或声称亲见 Owner 操作。历史 `qa_failed`/`qa_blocked` 不得删除；证据无法取得时如实标注并据标准判定，不强行通过。
- **Human Owner 最终 gate：**在审阅该精确 r3 文档 verdict、已有人工报告及全部未证明风险后单独决定是否接受此有界收尾；不代表完整 r2、两端 PLC、FF/CA、现场或发布已接受。任何范围、验收、风险或允许路径实质变化均先回 PM 新 Revision 和精确批准。

本 PM 使用 `aiis` 与 `project-governance`。后续仅文档工作按触达面选择相应 skill；如另行提出 Rust/Tauri、前端/i18n 或 PLC 点位技术改动，须另立批准范围并交相应技术角色使用 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`plc-point-mapping` 等适用 skill，本 r3 不替其实施或验证。角色为 `contract_only`，主会话、任务 bundle 与 diff 审计仍是必要控制，不宣称平台 ACL 或强制路由。

## 6. Human Owner 精确范围批准与衔接

本次会话中，Human Owner 在审阅该组收尾草案后明确回复：

> 批准这组收尾草案

该决定精确批准 `device-simulator::DS-004 r3`、`aiis-ics-arch::ARCH-PLC-001 r8`、`device-simulator::DS-005 r3`、`aiis-ics-arch::DAA-018 r4`、`aiis-ics-arch::DAA-019 r3` 及其版本衔接；父 r8 与本 r3 均为同一决定明确包含的版本，不是相互自动继承批准。Human Owner 审阅前本 r3 完整草案 SHA-256 为 `fec0ebdc1af202aad5d8cd6ff4886665f945187f9bb4ebb275b7a0d7649f99c6`。本批准只进入本任务 Development 的既有资料文档交接及后续独立文档复核，不改变 §2–5 的验收、证据和数据保护边界；历史 `qa_failed`、`qa_blocked` 与隔离事件保持原事实，新的 QA verdict 与 Human Owner 最终验收尚未发生。

## 附录：已批准 r2 完整原文及嵌套 r1 历史

以下围栏内为写前完整 r2 UTF-8 原始字节（含末尾换行），SHA-256：`4f5ff981cf28f6734b2bc2409189157cad7b102510715d2712f745710d026f3c`。r2 内嵌的完整 r1 原文字节 SHA-256：`322b2be3639d124f02a0585a1cfaf1b3eb34e1a519f18b145f551ac1fa856ae4`。历史时态、旧批准、旧 allowlist 和当时 gate 只属于相应历史 Revision，不构成本 r3 的批准或 QA 结论；本 r3 的范围批准见 §6。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: DS-004
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 DS-004 r2 实施范围及版本衔接 -> Development 基于完整既有 bundle 返工和更新 tasks.md -> fresh-context Verification 更新 checklist.md -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: root
Capability: DS 点位独立中英文显示名称与顶栏语言联动
Owner: Device Simulator
Acceptance Chain Reference: 本任务独立履行 STD，不继承其他任务的实施批准、QA 或最终验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r4; aiis-ics-arch::DAA-018 r3; device-simulator::DS-003 r2
Depends On: aiis-ics-arch::ARCH-PLC-001 r4 精确设计批准；本 r2 实施范围已获 Human Owner 精确批准；DS-003 / DAA-017 在本任务及 DAA-018 均完成 STD 最终验收并各自另批后才启动实施；此前下游开工时序已由 2026-11-17 的 Owner 后续决定调整，见下方顺序衔接说明。

# DS-004 r2：点位中英文显示名与保存结果保护

## 1. 状态与范围

Human Owner 于 2026-11-17（Asia/Shanghai）要求先统一 DS/DAA 点位中英文显示名、再做 DS 导出和 DAA 导入，顶栏语言切换、未设置留空、DAA 上报不带显示名。父设计 [ARCH-PLC-001 r4](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 已获设计范围批准；本任务 r1 实施范围曾获批准，但 QA1、QA2、QA3 均记录 `qa_failed`，最终验收未发生。r1 完整原文及批准事实保存在本文附录，既有 tasks/checklist 的历史不变。因保存未知回执及关闭时交错暴露未明示的实质可用性和数据保护风险，本任务形成 r2 草案；Human Owner 随后已精确批准 r2，r1 的批准本身并不自动批准 r2。DS-004 的双语和描述功能不变，只增加与本任务保存直接交错的受限保护。

本任务涉及 DS 点位的保存配置、点位列表、双语名和独立可选描述编辑，以及 §3.1 中与本任务保存直接交错的未知结果和单窗口关闭保护。JSON 导入导出、FF/CA、公共合同、协议行为、真实设备、数据库 DDL、已有 profile 迁移和通用命令回执系统均不在本任务。本次 PM 阶段仅修订本 spec；已存在的 tasks/checklist 不由 PM 改动。r2 实施范围已获 Human Owner 精确批准，Development 可按下列 allowlist 返工并更新 tasks，随后 fresh-context Verification 独立更新 checklist。父设计 P1 对 DS-004 r1 的文字记录当时计划；已获批准的 r2 作为本任务活动实施版本接续，双语基础和先双端最终验收、后分别审批导出/导入的 gate 不变。


### 后续 Owner 决定：JSON 任务顺序衔接

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 ARCH-PLC-001 r5、DS-003 r4 和 DAA-017 r4 及顺序调整，直接开始开发。使用各自的 .local/dev 完成 DS 导出、DAA 导入测试，测试后清理并更新手册。

该决定精确批准 ARCH-PLC-001 r5 设计、DS-003 r4 与 DAA-017 r4 实施及顺序调整。本文此前记录的“两个双语基础均最终验收后才审批、启动 JSON 实施”是当时有效的下游门槛；自本次决定起，DS-003 r4 和 DAA-017 r4 可依各自已批准规格开展 Development，不再等待两个双语基础最终验收。原门槛文字保留用于历史追溯。本任务自身实施范围、文件白名单、验收和风险不变，原失败历史保留，当前独立 QA 仍为 qa_blocked，Human Owner 最终验收未发生；任何 JSON QA 均不能冒充本任务通过。互通测试仅在各自已授权 .local/dev 范围进行，不能影响既有数据或真实设备。

## 2. 当前事实与字段语义

[DS PointConfig](../../runtime/src/domain/configuration.rs) 有既有 `name` 和 `displayName`（源码 `display_name`），旧 `displayName` 无语言标记、上限 200 UTF-8 字节；[TIA 导入](../../runtime/src/services/source_import.rs)会用叶注释初始化新点的该旧字段。用户可能已手工修改该字段，因此它既不能默认是中文/英文，也不能一律断言仍是源注释。旧字段、旧版本及旧值必须保留；旧值如展示，标注“语言未标记”，不作为新语言已设置值。既有 comment→旧字段行为不作为填充中英文的理由。

每点拟新增可省略 `displayNames` 闭合对象：`{"zh-CN":"...","en-US":"..."}`。两键均必填为字符串，各 ≤256 UTF-8 字节；缺整个对象等价于两值 `""`，两值都空时显式保存可省略对象，任一非空时保存两键，单侧可以为空。输入对象缺键、null、非字符串、额外键、超字节数不得被静默修正。保留合法字符串原值，包括 Unicode 和首尾空格；不自动翻译、不从旧 displayName、技术 name、TIA 路径或注释复制，也不从一种语言回填另一种。

每点另有可选 `description` 独立字符串，最多 500 UTF-8 字节；用户可为手工点和 TIA 点显式编辑，缺失或空表示未设置，保存空值可省略。不能从旧 displayName、双语名、TIA 路径或注释自动填充；旧历史与源字段均不变。它是描述，不是双语字段、程序名或启用权限。

`name` 仍是唯一稳定的程序引用名，与界面显示语言独立；普通现有命名工具的显式操作仍按既有规则，不能因显示名变化改写 name、ID、sourcePath、类型、地址、采集启用、策略或读写权限。旧 displayName 独立保留，除操作者通过既有明确编辑操作修改外不变；复制其内容到任一新字段必须由人手工填写，不能自动执行。

## 3. 操作、持久化和兼容

- 点位列表新增当前顶栏语言对应的显示名列，`zh-CN` 取对应中文值，`en-US` 取英文值；未设置显示空白或明确占位。技术 name 仍可见，不以它、另一语言或旧 displayName 做 fallback。顶部唯一语言开关驱动响应式显示；切换语言不写草稿、ETag、版本、source 或历史，不触发保存/应用/运行。编辑弹窗同时提供中文、英文、独立可选描述输入及可辨认的旧无语言字段；取消不写，现有保存/确认流程只在用户选择时提交，保留其他点值。
- 复用配置 JSON schema_version 1 的可选字段，不修改 SQLite schema。读取旧草稿、revision 和 source archive 时不能重写原 payload/摘要；新配置值只能在用户显式保存后进入新草稿/新 revision，不能改写已发布版本及 selected/actual_loaded 或擅自加载。保留已选择实例的隔离和现有并发 ETag 冲突行为；读取、locale 切换、取消和只读预览不会触发写入。
- 保留 DB/UDT 重导时同一 ID 点的两语言及旧字段；重导新增点的两种语言为空；点删除/替换、ID 变动依现有显式预览与身份规则，不把旧名字附给新身份。地址/命名/策略预览、草稿冲突和并发更新不得清空或跨点复制新字段。实际数据/历史版本及 UUID 始终不作为迁移对象。
- 因现有反序列化 `deny_unknown_fields`，旧程序遇带新 `displayNames` 的配置**可能拒绝**；须在隔离副本分别验证旧配置可用、新字段配置安全拒绝且不误开空 profile/不修改 bytes。不得声称旧版兼容或覆盖历史；若无法安全拒绝、需要 DDL 或迁移已用 profile，停止并回 PM 另行批准。回退只用事先保全的自有合成 profile 或证明兼容的停机副本。

### 3.1 r2：保存未知结果与直接交错的限定保护

**事实与分类。** 仅把本次点位配置保存及其直接交错纳入本节；旧操作是否成功必须依据各自事实，不能从另一个操作的结果推断。原 r1 的字段、显式确认、ETag、历史与实例隔离要求及 DS4-01～07 全部保留。

1. 保存的**正常 service envelope** 若返回 `save_receipt_unknown` 或 `save_commit_unknown`，可能已提交，也可能没有；既有 `Store` 对已入队工作使用同一 worker FIFO。只有证明该保存 job 已进入同一 profile、同一 Store 队列后，且其后的配置 Load 成功返回，才可把它作为该 job 已处理的顺序屏障；这不证明原保存成功或失败。`queries::save` 涉及实例删除后的收尾时，读草稿本身不证明相关收尾完成，须按既有事实另行核对；拿不到证明继续显示未决。Development 须核对源码闭包并用受控并发/故障验证，不能把一次或两次内容相同当成提交回执。
2. `ipc_transport_unknown` 来自 `invoke` 拒绝，不能证明请求已入队、已终结或未执行；`runtime_task_receipt_unknown` 来自执行任务的 JoinError，不能把它等同于 transport 断开或断言闭包仍运行。后者即使闭包已结束，先前提交到 Store 的工作及相关收尾仍须证明结束。两类只有在各自可靠的终结与副作用边界被证实时才可解除冲突写保护；当前没有可查询的持久 operationId 完成回执。仅等待固定时间、两次相同读回或人工点击确认均不是终结证明；不能自动重试、以日志当作持久回执、伪报成功/失败或静默清除未决状态。
3. 发起保存时保留本地编辑、提交工作区、原 ETag 和本次 `confirmPoints`；校验反馈与保存结果须区分已知成功、已知未变、已知拒绝和未知。服务端 `Configuration::prepare` 可合法保留或更新地址/命名/初值/策略确认，实际候选不一定逐字等于前端提交的 workspace。读取结果应同时呈现可核对的实际持久草稿、ETag、相关确认及本地输入，不能因对象不全相等而强行覆盖本地值，或为制造相等清除确认。已知保存成功后仅后续读回失败，应如实区分已知保存事实与读取未知；不得把保存成功误称失败。
4. 未决期间保留本地中英文、描述和其他未保存输入；只读检查先放在独立快照，不隐式替换编辑稿。禁止再次保存、发布、应用和其他会与该未决保存冲突的写入；必要的 Stop 不因该保护被禁止，其他运行控制按原安全准入处理。Stop/暂停或预览释放若与本次保存直接交错产生未知结果，应保留各已知的动作/实例及未知事实；已知拒绝、后台读取、其他结果或保存核对不得覆盖它们。核对当前运行事实不等于证明过去操作的结果。取消、读失败、失效 ETag、并发编辑、编辑器仍打开或事实变化时不得静默解冻、丢名或盲目重试；确需采用持久草稿而放弃本地输入时，须先展示差异、明确告知并取得用户当次确认。没有可靠证明时保持未决，不承诺一定能在当前窗口恢复。
5. [App.vue](../../src/App.vue) 的保存关闭当前只看 `save()` 布尔值再 emit close；页面卸载/异步完成可经 [releasePreview](../../src/console/composables/useDeviceSimulator.ts) 绕过 busy 发起释放。QA3 F4 在合成异步边界复现保存期间的交错，真实原生调度未验证。r2 在**单窗口前端**提供有限关闭门禁：普通关闭、保存并关闭和明确放弃关闭应协调已有在途释放；从作出关闭决定前的检查到发出关闭决定，阻止新增未跟踪释放并复核已知未决状态。未决或在途状态不得被自动关闭静默抹去；用户可以取消关闭，或在看见保存事实、可能仍未释放的预览票据、其他已知未决结果和本地未保存输入可能丢失的说明后，显式选择放弃内存记录并关闭。未被发出的释放不能说成已释放。保存已知成功但票据释放未知时，不得把保存整体称作失败。
6. 预览释放只涉及临时 token 及可能的版本引用保护，不代表草稿提交、apply 或设备动作；现有 token 过期规则不等于已经确认释放。该门禁不声称跨 IPC/Tauri、崩溃、强制退出或窗口消失后的强原子保证，也不构建跨页面通用回执账本。若发现必须改动 Tauri 或增加持久回执/DDL 才能满足本节，停止并回 PM 新 Revision，不能把未证明行为写成通过。
7. 对无法证明终结的 transport/runtime-task unknown，可由用户在了解后选择保留窗口及手动记录输入，或明确放弃内存记录并尝试正常关闭；关闭本身不是结清证明，也不保证未保存值和未决状态跨重启保留。不自动关闭、重启或重试。若需继续，以自有合成 profile 验证旧进程**确实终止**、原独占锁已释放，并确认新进程打开的是**同一 profile 身份**而非空库/回退路径，再读取草稿和相关当前事实、由用户按保留的输入人工比对；不能宣称这证明原请求结果。若进程未退出、锁未释放、身份不一致、读取失败或缺少原输入，保持无法证明/不可恢复状态，不得宣称安全完成。此退路的实现与原生行为目前均待验证，不授权接触真实 profile。

**F3 范围说明。** QA3 的“apply unknown → stop unknown → 核对控制 → 普通预览/重读清除 apply unknown → save”序列没有本次保存 unknown 交错；HEAD 已有通用 action 清除未知标志的行为。收回超出范围的通用 F2 控制恢复后，本任务不声称修复全部无保存交错的 apply/write/preview 旧行为，也不把本段写成 QA 通过。与本任务保存**确有交错**且已知的其他未知结果仍须按上条保留；旧通用风险和 QA1–QA3 原 verdict 继续公开记录，后续是否另立任务由 Owner 决定。

**容量与安全。** 保留既有每实例最多 4096 点和整个工作区序列化不超过 16 MiB 的规则；不承诺多个实例同时满额后必然低于总上限。QA1 的单实例 4096 点、5,926,517 字节样本观察到一次保存已提交而回执未知；另一样本正常成功。二者不是确定性超时或容量耗尽，也不能据此降低点数或字段长度。不得用截断、丢字段、覆盖历史或回退真实 profile 规避风险。

## 4. 已批准的 r2 Development 文件 allowlist

以 `automation-world/device-simulator/` 为根；花括号只展开列出的名字。r2 相对 r1 **唯一新增现有产品文件是 `src/App.vue`**，供上述单窗口关闭门禁；其他路径不变。超出即停止并回 PM 新 Revision；PM 阶段只写本任务 spec，后续角色按已批准的本 r2 和各自 gate 行事。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| 领域与导入 | `runtime/src/domain/configuration.rs`；`runtime/src/services/{configuration.rs,source_import.rs}` | 无 |
| UI、语言和样式 | `src/App.vue`；`src/services/deviceSimulator.ts`；`src/console/composables/useDeviceSimulator.ts`；`src/app/simulator/views/points/index.vue`；`src/app/simulator/components/PointEditor.vue`；`src/app/simulator/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | 无 |
| 验证与说明 | `runtime/tests/{owner_contract.rs,configuration_store.rs,source_import.rs,versions.rs}`；`tests/{presentation.test.mjs,import-feedback.test.mjs}`；`tests/ui/{native_driver.js,scenarios.json}`；`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN,CODE_INDEX}.md`；`runtime/{README,README.zh-CN}.md`；`tests/{README,README.zh-CN}.md` | `runtime/tests/point_display_names.rs`；`tests/point-display-names.test.mjs` |
| 角色记录 | 本 spec 仅 PM/Owner | r2 精确批准后 Development 更新既有 `tasks.md`；handoff 后独立 Verification 更新既有 `checklist.md`，均保留历史 |

不修改配置文件、Cargo/pnpm 依赖或锁、DDL/迁移、其他模块、根 contracts、其他任务、`.env` 或用户 profile。新文案中英文成对；点位表采用公共列宽能力，普通列可拖拽、最小宽/横向滚动、按稳定键持久化并可恢复默认，特殊功能列例外。

## 5. 保留的 r1 验收标准（r2 须重新验证）

| 编号 | 可验证通过标准 |
| --- | --- |
| DS4-01 | 新点中文/英文均空；分别录入、只填一侧、清空、保存/重开各场景精确保留 Unicode 值；无效对象键/类型/null/超 256 字节被拒绝，非法值不变成空。 |
| DS4-02 | 顶栏切换时列表显示对应语言；空语言只显示空/占位，技术 name 稳定；切换前后 ETag、draft bytes、版本、loaded 及来源无变化；编辑取消不写。 |
| DS4-03 | 含非空旧 displayName 的旧版本读取后旧值不变且明确标识语言未标记，中英文仍空；用户手工设置一侧不会改变另一侧、旧值或 name；既有 TIA 叶注释初始化旧字段不自动充当双语名。 |
| DS4-04 | 旧配置/历史 revision 读取零写回、旧 bytes/SHA 不变；对含新字段配置，旧二进制安全拒绝且不误创建空库；显式保存只影响新草稿/新版本，模拟配置及版本指针按原行为保持。 |
| DS4-05 | DB/UDT 同身份重导保留双语和旧值；新增、移除或替换点不串 ID；并发 ETag、命名/地址预览、取消/失败和其他实例不丢名或误写。 |
| DS4-06 | 手工点及 TIA 点可单独填写、清空并保存描述；旧显示名/注释不自动变描述，双语和技术名不变，旧 payload 零写回；超过 500 UTF-8 字节或非法类型拒绝。 |
| DS4-07 | 真实 macOS 原生界面验证双语编辑、顶栏切换、表列宽拖动/持久化/重置；Rust、Node、类型检查及项目入口回归记录真实结果。未测平台/真实设备不声称通过。 |

### 5.1 r2 新增验收矩阵

| 编号 | 必须验证的结果 |
| --- | --- |
| DS4-08 | 使用自有合成数据验证单实例 4096 点、中文/英文各 256 UTF-8 字节与描述 500 字节且总量小于 16 MiB 的有效配置；记录实际保存、提交、超时和读回，不把一次结果外推为所有时序成功/失败。超出既有点数或总字节限制的请求明确拒绝、不丢旧数据；不降低上限或截断。 |
| DS4-09 | 区分 service `save_receipt_unknown`、`save_commit_unknown`、`runtime_task_receipt_unknown` 和 `ipc_transport_unknown`。通过有屏障的受控故障/并发场景证明分类、原保存仅调用一次、正确提示、原 ETag 和本地输入保留。对 service 返回后的同 Store FIFO 进行入队顺序证明；读取只证明当前事实，不能冒称原请求成功或失败。读失败、FIFO/副作用未证、过期或变化 ETag 及并发编辑均不能静默解除保护。 |
| DS4-10 | transport unknown 时，在重读两次相同草稿后才让先前保存入队/修改确认的可控时序中，仍保留 unknown 并阻止冲突保存，不自动重试；runtime-task 路径须单独证明终结/入队/副作用边界，否则同样保持保护。不得以固定睡眠或草稿相等作为完成证明。 |
| DS4-11 | 涵盖 `confirmPoints` 非空且服务端候选改变初值/策略确认、以及地址/命名确认被合法调整的样本；本地中英文、描述与实际草稿可逐点核对，不截断或复制到其他点。不把实际候选与 submitted 不相等误称保存失败，也不为相等删改确认；用户明确选择放弃本地输入时需有准确提示。 |
| DS4-12 | 重现 QA2 的保存 unknown → stop unknown → pause 已知拒绝，再核对保存的顺序；每项已知直接交错的未决事实仍可见，读取或已知失败不覆盖它们、保存不被错误放行，必要 Stop 可用。本地草稿、其他实例及 ETag 保持正确；检查当前控制状态不冒称旧控制成功。 |
| DS4-13 | 重现 QA3 F4 合成屏障，并增加保存成功返回前后、页面卸载/异步释放及 close emit 交错；单窗口门禁不得静默丢失已知未决或在途状态。保存已知成功与释放未知分别提示；明确取消关闭和用户知情放弃记录关闭两种选择。限定证明为前端已跟踪动作，不将其冒充原生退出或跨 IPC 原子保证。F3 无保存交错的旧通用行为按 §3.1 保留事实和范围，不伪称已修复。 |
| DS4-14 | 无可靠终结证明时，禁用冲突写入并保留本窗口编辑和未决状态；检查、locale 切换及取消不写。当验证用户或合成测试显式选择正常关闭/重开退路，仅对自有合成 profile 分别证明旧进程终止、锁释放及新进程同一 profile 身份，再由用户比对当前事实；旧进程仍在、锁未释放、身份错误、数据未记录或读失败均不冒称可恢复。正常关闭失败、崩溃及强制退出不推断已安全结束；提示内存输入可能丢失。 |
| DS4-15 | 中英文提示成对；复用原表列宽能力；原 r1 所有兼容、历史、点身份、并发及原生 DS4-01～07 仍需按各自证据独立验证。无真实 profile、真实设备、真实网络、JSON 导入/导出或发布；不得对既有 profile 执行 DDL/迁移。新建自有合成 profile 可运行项目既有初始建库 DDL，须如实记录；验证使用精确候选和自有合成数据。 |

## 6. 验证、风险与 gate

r2 精确批准后 Development 在既有 `tasks.md` 追加返工和自检，保留 r1 全部历史；使用自有新合成 profile 和隔离构建目录，保留旧版本样本/源码快照；交付正式树、记录具体命令、退出码、版本和未执行项。fresh-context Verification 独立检查并在既有 `checklist.md` 追加新 verdict，保留 QA1–QA3 原文，Human Owner 决定最终验收。示例检查：`cargo test --manifest-path runtime/Cargo.toml --locked --offline --test point_display_names`、`node --test tests/point-display-names.test.mjs`、`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir "$RUN_DIR/ui"`，`CARGO_TARGET_DIR`/`RUN_DIR` 均指向自有临时目录；真实命令由 Development 依据工具链确认。不得运行用户现有 profile 或真实设备。

仅修改显示名的保存可以形成新配置 revision，但不等于更改物理 PLC 或自动加载；版本容量、旧二进制读取和 DDL 假设需实测，不能满足就停止回 PM。transport/runtime-task 结果可能无法在当前窗口证明终结，用户可能长期不能再次保存；显式放弃并关闭可能丢失本地输入和未知记录，进程未终结或无法确认同一 profile 时没有安全重开结论。该可用性和恢复风险已随 r2 的精确范围获 Owner 批准，不代表最终验收，也不以缩小原验收掩盖。DS-003 和 DAA-017 的实施均依赖本任务及 DAA-018 各自完成包含 Human Owner 最终验收的 STD，之后还需各自精确批准；不能以本任务验证声称 JSON 已实现。

### 6.1 原生验证暂停

由于另一任务的原生隔离事件，当前所有 GUI/CUA 启动与附着继续暂停。DS4-07 和涉及真实原生关闭/重开的证明均未完成；只能在协调者明确解除暂停、并已证明使用独立环境、唯一自有合成 profile、应用/WebKit 身份及 OS 数据落点后执行，不能使用现有用户 profile。合成 VM/JS 屏障不能冒称真实 WebView 或 Tauri/native 通过。临时资源归属、保留和最终回收继续按原 tasks/checklist 处理，不影响其他任务资源。

## 7. skill 与角色 handoff

本 PM 规格使用 `aiis`、`project-governance`、`plc-point-mapping`，未实施代码或验证产品。Development 按触达面使用 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer`；Verification 在 fresh context 独立复核。QA 通过不等于最终验收或现场授权。

## 8. r1 Human Owner 实施范围批准记录（历史）

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 DS-004 r1 和 DAA-018 r1 的实施范围。请按 STD 先完成两端双语显示名的开发和独立验证，导出、导入功能暂不实施。

此决定批准当时本任务 `DS-004 r1` 的精确实施范围，批准前完整草案 SHA256 为 `7d1a821922e5c8330740eba3889ce775c93eda6506a71aa92a30cd436328ecf3`；当时允许按 r1 开展 Development 自检及 fresh-context Verification，不自动批准 r2。该批准不代表 Human Owner 最终验收，不授权 JSON 导出/导入、FF/CA、真实 profile、DDL、现场设备或发布；两项基础任务各自完成 STD 最终验收后，导出/导入仍须独立精确批准。

## 9. r2 修订依据、批准和交接

- r1 的 [Development 记录](tasks.md) 和 [Verification 记录](checklist.md) 分别保留精确候选、自检及 QA1 F1、QA2 F2、QA3 F3/F4 的真实失败 verdict。QA3 的 service 故障注入与 UI/控制合成边界不能外推成原生窗口、真实 IPC 或现场验证。
- 本 r2 在原功能和 DS4-01～07 上增加 §3.1 与 DS4-08～15，明确不同 unknown 的证明边界、用户可见结果、有限单窗口关闭及不可恢复风险；新增 `src/App.vue` 是文件 allowlist 的唯一增量。排除通用命令跟踪、Tauri 代码、持久回执、DDL、导出/导入、真实 profile/设备和发布。
### r2 Human Owner 实施范围与版本衔接批准记录

2026-11-17（Asia/Shanghai），Human Owner 明确回复：

> 批准 DS-004 r2 及版本衔接

该决定精确批准 `device-simulator::DS-004 r2` 的实施范围及所列保存未知结果、关闭和恢复风险，并同意其作为父设计中 DS 双语基础的活动实施版本。用户审阅、登记前完整 r2 草案 SHA256 为 `e4a7ac7e6feed1172955bce34875d8ed2a2364fc3246ad6959a288b12318832d`。Development 可按本 r2 白名单返工，自检并交接 fresh-context Verification；QA1–QA3 的历史失败、原生隔离暂停和 r1 批准原文继续保留。该批准不等于 QA 通过或 Human Owner 最终验收，不批准 JSON 导入/导出、DAA/FF/CA、真实 profile/设备、DDL 或发布；两端基础分别完成最终验收后，导出/导入仍须另行精确批准。

## 附录：已批准的 r1 完整原文（历史，非活动规格）

写前 r1 整份 UTF-8 原始字节 SHA-256：`322b2be3639d124f02a0585a1cfaf1b3eb34e1a519f18b145f551ac1fa856ae4`。以下围栏之间的内容是可逆原文，末尾原有换行属于原文；包含当时 r1 批准记录。该历史不代替 r2 的批准或 QA。

~~~~~~text
Task ID: DS-004
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: DS-004 r1 实施范围已获 Human Owner 批准 -> Development tasks.md / developer_handoff -> fresh-context Verification checklist.md -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: root
Capability: DS 点位独立中英文显示名称与顶栏语言联动
Owner: Device Simulator
Acceptance Chain Reference: 本任务独立履行 STD，不继承其他任务的实施批准、QA 或最终验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r3; aiis-ics-arch::DAA-018 r1; device-simulator::DS-003 r2
Depends On: aiis-ics-arch::ARCH-PLC-001 r3 精确设计批准；DS-003 / DAA-017 在本任务及 DAA-018 均完成 STD 最终验收后才启动实施

# DS-004：点位中英文显示名

## 1. 状态与范围

Human Owner 于 2026-11-17（Asia/Shanghai）要求先统一 DS/DAA 点位中英文显示名、再做 DS 导出和 DAA 导入，顶栏语言切换、未设置留空、DAA 上报不带显示名，当时要求暂不改代码。[ARCH-PLC-001 r3](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 设计范围已获 Human Owner 批准；本任务 r1 实施范围已获 Human Owner 批准；r2 设计批准是历史事实，最终验收仍待独立验证后决定。DS-004 只定义 DS 本地可维护、可显示的双语基础；与 DAA-018 分别按 STD 通过独立验证和 Human Owner 最终验收后，才可启动需另行批准的 DS-003 / DAA-017 实施。

只涉及 DS 点位的保存配置、点位列表、双语名和独立可选描述编辑。JSON 导入导出、FF/CA、公共合同、协议行为、真实设备、数据库 DDL 或已有 profile 迁移均不在本任务。本次 PM 阶段仅写规格，不创建 tasks/checklist、不改产品；Development 按已批准 gate 和下列 allowlist 实施并创建 tasks，Verification 在交接后创建 checklist。

## 2. 当前事实与字段语义

[DS PointConfig](../../runtime/src/domain/configuration.rs) 有既有 `name` 和 `displayName`（源码 `display_name`），旧 `displayName` 无语言标记、上限 200 UTF-8 字节；[TIA 导入](../../runtime/src/services/source_import.rs)会用叶注释初始化新点的该旧字段。用户可能已手工修改该字段，因此它既不能默认是中文/英文，也不能一律断言仍是源注释。旧字段、旧版本及旧值必须保留；旧值如展示，标注“语言未标记”，不作为新语言已设置值。既有 comment→旧字段行为不作为填充中英文的理由。

每点拟新增可省略 `displayNames` 闭合对象：`{"zh-CN":"...","en-US":"..."}`。两键均必填为字符串，各 ≤256 UTF-8 字节；缺整个对象等价于两值 `""`，两值都空时显式保存可省略对象，任一非空时保存两键，单侧可以为空。输入对象缺键、null、非字符串、额外键、超字节数不得被静默修正。保留合法字符串原值，包括 Unicode 和首尾空格；不自动翻译、不从旧 displayName、技术 name、TIA 路径或注释复制，也不从一种语言回填另一种。

每点另有可选 `description` 独立字符串，最多 500 UTF-8 字节；用户可为手工点和 TIA 点显式编辑，缺失或空表示未设置，保存空值可省略。不能从旧 displayName、双语名、TIA 路径或注释自动填充；旧历史与源字段均不变。它是描述，不是双语字段、程序名或启用权限。

`name` 仍是唯一稳定的程序引用名，与界面显示语言独立；普通现有命名工具的显式操作仍按既有规则，不能因显示名变化改写 name、ID、sourcePath、类型、地址、采集启用、策略或读写权限。旧 displayName 独立保留，除操作者通过既有明确编辑操作修改外不变；复制其内容到任一新字段必须由人手工填写，不能自动执行。

## 3. 操作、持久化和兼容

- 点位列表新增当前顶栏语言对应的显示名列，`zh-CN` 取对应中文值，`en-US` 取英文值；未设置显示空白或明确占位。技术 name 仍可见，不以它、另一语言或旧 displayName 做 fallback。顶部唯一语言开关驱动响应式显示；切换语言不写草稿、ETag、版本、source 或历史，不触发保存/应用/运行。编辑弹窗同时提供中文、英文、独立可选描述输入及可辨认的旧无语言字段；取消不写，现有保存/确认流程只在用户选择时提交，保留其他点值。
- 复用配置 JSON schema_version 1 的可选字段，不修改 SQLite schema。读取旧草稿、revision 和 source archive 时不能重写原 payload/摘要；新配置值只能在用户显式保存后进入新草稿/新 revision，不能改写已发布版本及 selected/actual_loaded 或擅自加载。保留已选择实例的隔离和现有并发 ETag 冲突行为；读取、locale 切换、取消和只读预览不会触发写入。
- 保留 DB/UDT 重导时同一 ID 点的两语言及旧字段；重导新增点的两种语言为空；点删除/替换、ID 变动依现有显式预览与身份规则，不把旧名字附给新身份。地址/命名/策略预览、草稿冲突和并发更新不得清空或跨点复制新字段。实际数据/历史版本及 UUID 始终不作为迁移对象。
- 因现有反序列化 `deny_unknown_fields`，旧程序遇带新 `displayNames` 的配置**可能拒绝**；须在隔离副本分别验证旧配置可用、新字段配置安全拒绝且不误开空 profile/不修改 bytes。不得声称旧版兼容或覆盖历史；若无法安全拒绝、需要 DDL 或迁移已用 profile，停止并回 PM 另行批准。回退只用事先保全的自有合成 profile 或证明兼容的停机副本。

## 4. 已批准的 Development 文件 allowlist

以 `automation-world/device-simulator/` 为根；花括号只展开列出的名字。超出即回 PM；PM 阶段只写本任务 spec，后续角色按各自 gate 行事。

| 类别 | 已有文件 | 可新建文件 |
| --- | --- | --- |
| 领域与导入 | `runtime/src/domain/configuration.rs`；`runtime/src/services/{configuration.rs,source_import.rs}` | 无 |
| UI、语言和样式 | `src/services/deviceSimulator.ts`；`src/console/composables/useDeviceSimulator.ts`；`src/app/simulator/views/points/index.vue`；`src/app/simulator/components/PointEditor.vue`；`src/app/simulator/locales/{en-US,zh-CN}.json`；`src/styles/app.css` | 无 |
| 验证与说明 | `runtime/tests/{owner_contract.rs,configuration_store.rs,source_import.rs,versions.rs}`；`tests/{presentation.test.mjs,import-feedback.test.mjs}`；`tests/ui/{native_driver.js,scenarios.json}`；`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN,CODE_INDEX}.md`；`runtime/{README,README.zh-CN}.md`；`tests/{README,README.zh-CN}.md` | `runtime/tests/point_display_names.rs`；`tests/point-display-names.test.mjs` |
| 角色记录 | 本 spec 仅 PM/Owner | 精确批准后 Development 创建 `tasks.md`；handoff 后独立 Verification 创建 `checklist.md` |

不修改配置文件、Cargo/pnpm 依赖或锁、DDL/迁移、其他模块、根 contracts、其他任务、`.env` 或用户 profile。新文案中英文成对；点位表采用公共列宽能力，普通列可拖拽、最小宽/横向滚动、按稳定键持久化并可恢复默认，特殊功能列例外。

## 5. 验收标准（拟议，均未执行）

| 编号 | 可验证通过标准 |
| --- | --- |
| DS4-01 | 新点中文/英文均空；分别录入、只填一侧、清空、保存/重开各场景精确保留 Unicode 值；无效对象键/类型/null/超 256 字节被拒绝，非法值不变成空。 |
| DS4-02 | 顶栏切换时列表显示对应语言；空语言只显示空/占位，技术 name 稳定；切换前后 ETag、draft bytes、版本、loaded 及来源无变化；编辑取消不写。 |
| DS4-03 | 含非空旧 displayName 的旧版本读取后旧值不变且明确标识语言未标记，中英文仍空；用户手工设置一侧不会改变另一侧、旧值或 name；既有 TIA 叶注释初始化旧字段不自动充当双语名。 |
| DS4-04 | 旧配置/历史 revision 读取零写回、旧 bytes/SHA 不变；对含新字段配置，旧二进制安全拒绝且不误创建空库；显式保存只影响新草稿/新版本，模拟配置及版本指针按原行为保持。 |
| DS4-05 | DB/UDT 同身份重导保留双语和旧值；新增、移除或替换点不串 ID；并发 ETag、命名/地址预览、取消/失败和其他实例不丢名或误写。 |
| DS4-06 | 手工点及 TIA 点可单独填写、清空并保存描述；旧显示名/注释不自动变描述，双语和技术名不变，旧 payload 零写回；超过 500 UTF-8 字节或非法类型拒绝。 |
| DS4-07 | 真实 macOS 原生界面验证双语编辑、顶栏切换、表列宽拖动/持久化/重置；Rust、Node、类型检查及项目入口回归记录真实结果。未测平台/真实设备不声称通过。 |

## 6. 验证、风险与 gate

精确批准后 Development 创建本任务 `tasks.md`，使用自有新合成 profile 和隔离构建目录，保留旧版本样本/源码快照；交付正式树、记录具体命令、退出码、版本和未执行项。fresh-context Verification 独立检查并创建 `checklist.md`，Human Owner 决定最终验收。示例检查：`cargo test --manifest-path runtime/Cargo.toml --locked --offline --test point_display_names`、`node --test tests/point-display-names.test.mjs`、`pnpm exec vue-tsc --noEmit`、`pnpm exec vite build --outDir "$RUN_DIR/ui"`，`CARGO_TARGET_DIR`/`RUN_DIR` 均指向自有临时目录；真实命令由 Development 依据工具链确认。不得运行用户现有 profile 或真实设备。

仅修改显示名的保存可以形成新配置 revision，但不等于更改物理 PLC 或自动加载；版本容量、旧二进制读取和 DDL 假设需实测，不能满足就停止回 PM。DS-003 和 DAA-017 的实施均依赖本任务及 DAA-018 各自完成包含 Human Owner 最终验收的 STD，之后还需各自精确批准；不能以本任务验证声称 JSON 已实现。

## 7. skill 与角色 handoff

本 PM 规格使用 `aiis`、`project-governance`、`plc-point-mapping`，未实施代码或验证产品。Development 按触达面使用 `rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer`；Verification 在 fresh context 独立复核。QA 通过不等于最终验收或现场授权。

## 8. Human Owner 实施范围批准记录

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 DS-004 r1 和 DAA-018 r1 的实施范围。请按 STD 先完成两端双语显示名的开发和独立验证，导出、导入功能暂不实施。

此决定批准本任务 `DS-004 r1` 的精确实施范围，批准前完整草案 SHA256 为 `7d1a821922e5c8330740eba3889ce775c93eda6506a71aa92a30cd436328ecf3`；允许按本规格开展 Development 自检及 fresh-context Verification。该批准不代表 Human Owner 最终验收，不授权 JSON 导出/导入、FF/CA、真实 profile、DDL、现场设备或发布；两项基础任务各自完成 STD 最终验收后，导出/导入仍须独立精确批准。
~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
