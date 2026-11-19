Task ID: ARCH-PLC-001
Revision: r8
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 ARCH-PLC-001 r8 收尾范围及版本衔接 -> Development 记录文档交接 -> fresh-context Verification 独立文档核对 -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS 与 DAA 的逐 PLC S7 点位 JSON 双向交换设计及有界证据收尾
Owner: Automation World / Device Simulator 与 Data Acquisition Agent
Acceptance Chain Reference: Development Lifecycle Workflow；本设计与各实施任务分别精确范围批准、Development、fresh-context Verification 和 Human Owner 最终验收。
Related Task: device-simulator::DS-003 r5; aiis-ics-arch::DAA-017 r5; device-simulator::DS-004; aiis-ics-arch::DAA-018; device-simulator::DS-005; aiis-ics-arch::DAA-019; aiis-ics-arch::ARCH-PLC-002 r1

# ARCH-PLC-001 r8：既有证据的有界收尾（范围已批准）

## 1. 目标与范围

Human Owner 要求按 STD 整理验收范围及未验证边界，使用已完成的人工操作和本机真实上报证据收尾，不再重复测试，保留历史记录与现有数据。本 r8 是**文档及证据边界收尾规格**，不是新增软件开发或对原设计各项功能全部通过的声明。r7 §§2–3 及更早设计记录的产品合同继续作为设计依据；仅本次收尾的证据与验收路径改为下文。r7 A06、A08 及其他需新增实测才能满足的历史条件，不再作为本次文档收尾的必做测试；其未证明部分必须如实列出，不能改写为已通过。原 r7 及其全部更早历史和已批准事实以原字节保留于附录。

本任务不继承其他任务的 QA 或最终验收，也不以本父任务的批准替代它们的批准。实际实施面仍归各子任务；本父任务现无 `tasks.md` 或 `checklist.md`，r8 已精确批准，按 STD 分别创建。本轮不新增或运行测试、构建、GUI、IPC、数据库/profile 操作或真实上报；不要求用户重复操作、重上报或重新生成已清理工件。

## 2. 已有证据及身份

1. [DS-003 r5](../../device-simulator/plans/DS-003-plc-json-export/checklist.md) 与 [DAA-017 r5](../../data-acquisition-agent/plans/DAA-017-plc-json-import/checklist.md) 已各自记载 QA2 `qa_passed`，Human Owner 最终验收待定；其 QA1 失败及 QA2 原阻塞按原记录保留。这是各自精确历史候选的结论，不自动证明本次组合工作树或其他任务通过。
2. Human Owner 报告曾在 DS/DAA 操作中英文切换和 DAA→DS→DAA 文件往返；在 DAA 看到当前同源拒绝、选择历史新本机实例成功且自动选中、显示 4 点。运行与界面观察归 Human Owner；协调者和 Development 的各自只读比对按原 [DS-005](../../device-simulator/plans/DS-005-plc-json-bidirectional/tasks.md)、[DAA-019](../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/tasks.md) 及其 checklist 所记身份和范围引用。未截获该次原生 IPC 返回，不能把界面报告和其他次操作拼成同一 L2 的 IPC 证明。后来的前后基线只能说明该轮可比范围，不能倒证旧轮缺失的逐行前值。
3. 协调者转述 2026-11-18 一次本机只读核对：DAA dev 的 seq 91–103 共 13 条样本均有匹配 `sampleId` 的 `committed` 回执，outcome 为 `created` 或 `duplicate`，正文和回执 SHA 与存储一致；相同 13 条在本机 MySQL `plc_facts_history` 中的来源身份、正文 SHA 和点位名称/类型/值/质量均匹配。该样本配置中有一个实际点的中英显示名均非空；请求正文未见显示名字段和对应文本；服务端保存点数据未见显示名字段，所核点字段和值一致。`plc_facts_latest` 有 3 点质量为 `good`、最新 seq 103，`plc_source_registry` 绑定匹配；同期 DS 日志无 WARN/ERROR。最后 3 条在 14:39 获回执后，目标 PLC/DB 待发为 0；另有 44 条历史 local-only，不属于待发。此为**协调者报告的特定样本、环境和时点**，本 PM 未亲自核验该数据库、运行日志或界面，后续文档 QA 也不重新操作，不代表所有样本、路径或时段。私有证据定位：本机 `~/.codex/sessions/2026/11/16/rollout-2026-11-16T09-24-47-01a1e1f4-eb7e-74d2-b055-3696e1a855ec.jsonl` 约第 28239–28242 行为样本/回执及 MySQL 比对、28257–28260 行为双语排除核对；行号可能变化，应按内容定位。该会话可能含私有信息，只引用脱敏定位与归属，不得将原始业务正文、点值、地址、身份或凭据复制入仓；若后续无法访问，不得声称已复验。
4. [DS-004 r2](../../device-simulator/plans/DS-004-bilingual-point-display-names/checklist.md)、[DAA-018 r3](../../data-acquisition-agent/plans/DAA-018-bilingual-point-display-names/checklist.md)、[DS-005 r2](../../device-simulator/plans/DS-005-plc-json-bidirectional/checklist.md)、[DAA-019 r2](../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/checklist.md) 的整体 `qa_blocked` 和原 `qa_failed` 历史保留；各项局部复验通过只覆盖原记录所述范围。先前临时文件已按 Owner 要求清理，保留的 checklist 摘要是历史记录，不声称可以重新检查原始工件。[ARCH-PLC-002 r1](../ARCH-PLC-002-plc-json-export-feedback/checklist.md) 已独立 `owner_accepted`，本任务不改写其范围、证据或决定。

## 3. 明确未验证与风险

- DS-005 / DAA-019 原 r7 A06 的同一 L2 原生 IPC 返回及旧轮 context、样本其他列和 `sample_delivery` 前测逐行基线没有完整证据；上述人工观察和后续轮次比对不能补造缺失事实。不能据此宣称原 A06 整项通过或旧历史逐行前后完全不变。
- DS-004 原 QA4 的原生编辑、列宽跨重启/复位、普通入口、正常关闭与同一 profile 重开等仍未完整证明；其无保存直接交错的旧通用 F3 不声称已修复。DAA-018 原 QA2 的旧普通 native 对新字段安全拒绝、不误采/不误建空库及完整原生交互仍未证明。人工语言切换只按实际报告范围使用，不补齐未观察项。此前隔离事件的具体影响未知，原记录保留，不宣称零写。
- 上报样本不证明所有路径均不携带显示名，也不证明旧普通程序兼容、未知回执/异常时序、真实 PLC、Windows/VM、长稳、生产部署或现场采用。各任务在各自记录中保留更细的证据层级与限制。

## 4. 本次验收标准与交接

| 编号 | 文档收尾验收标准 |
| --- | --- |
| C01 | 分别列出各 Task ID、精确 Revision、当前历史 QA verdict、待决最终验收及其证据链接；保留旧批准、失败、阻塞和已接受事实，不因本修订改变原时点结论。 |
| C02 | 区分 Human Owner 界面报告、协调者本机只读上报核对、Development 自检与历史独立 QA；记录 §2 的样本边界、已清理工件和不可复验的限制，不将转述写成文档核验者亲见。 |
| C03 | 对原 r7 A06/A08 及关联任务遗留缺口标为未证明，列明 §3 的风险，不把样本、文件投影、合成测试、不同轮次或原生界面观察混称；不要求补测。 |
| C04 | 对照本 spec、现存 bundle 和文档 diff 独立核对 C01–C03 及实际交接范围；记录无法核实的来源、缺失证据和未运行项。文档事实不一致或无法满足本 r8 标准时如实给出 `qa_failed` / `qa_blocked`，不得强行通过。 |
| C05 | 明确分别申请 `device-simulator::DS-004 r3`、`aiis-ics-arch::DAA-018 r4`、`device-simulator::DS-005 r3`、`aiis-ics-arch::DAA-019 r3` 的精确范围批准及各自验收衔接；这四项须以各自 PM 草案为准，不因父 r8 获批而获批。DS-003 r5 / DAA-017 r5 的既有 QA2 可交各自 Owner 终验，不重跑，不将其 QA 传递给新候选。 |

Human Owner 已精确批准 `aiis-ics-arch::ARCH-PLC-001 r8`，Development 仅在本父任务新建 `tasks.md`，从现存任务记录与协调者提供的报告整理上述证据来源、已清理工件、候选及风险，注明未运行测试并交接；不改应用、测试、手册、配置或其他任务文件。协调者按权限和任务实际状态做必要索引机械同步。随后由 fresh-context Verification 只读审阅上述文档、证据归属及允许的文档 diff，在本父任务新建 `checklist.md` 给出**本 r8 文档收尾** verdict；不访问 `.local/dev`、数据库、GUI、原生程序、PLC 或网络，不重跑测试。文档 `qa_passed` 只表示本 r8 的 C01–C05 收尾记录通过，不表示 r7 原 A06/A08、子任务产品功能或真实场景通过；缺证据必须如实记录。

各子任务分别由其 PM 修订、精确批准、Development 记录和 fresh-context Verification 按批准范围评估；最后由 Human Owner 对各精确版本分别决定是否接受其已列风险及最终验收。本次范围批准不等于 QA、例外接受或最终验收；任何发布、部署、数据库写入、数据迁移、真实设备操作和新的外部发送另需明确授权。角色为 contract_only，不代表平台 ACL 或自动路由。PM 适用 `aiis`、`project-governance`；后续仅文档角色按实际触达面选择适用 skill，不替产品测试背书。

## 5. Human Owner 精确范围批准

2026-11-18（Asia/Shanghai），Human Owner 审阅整组收尾草案后，经协调者转达明确回复：

> 批准这组收尾草案

该决定精确批准 `aiis-ics-arch::ARCH-PLC-001 r8`、`device-simulator::DS-004 r3`、`device-simulator::DS-005 r3`、`aiis-ics-arch::DAA-018 r4`、`aiis-ics-arch::DAA-019 r3` 及其版本衔接；审阅前本 r8 草案 SHA-256 为 `a0fdfabbaeebdd95f8bc39fd9f2a0c3b974c13ec5a6b15fe39b6b834aba0eac3`。四个实施任务的批准分别在各自 `spec.md` 记录。本决定只批准已审阅的收尾范围，不是 QA 通过、未验证风险的最终接受或 Human Owner 最终验收；§2–§4 的证据层级、未验证边界和原有失败/阻塞保持。按上述 Development 文档交接、fresh-context Verification 独立文档核对及各自 Human Owner 最终验收接续，不重复测试或操作现有应用、数据库与数据。

## 附录：已批准 ARCH-PLC-001 r7 完整原文及全部历史

以下围栏内完整保留写前 r7 原始 UTF-8 字节（含末尾换行），SHA-256 为 `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`。历史时态、范围批准和状态只表示各自时点，不是 r8 已批准。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: ARCH-PLC-001
Revision: r7
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 ARCH-PLC-001 r7、device-simulator::DS-005 r2、aiis-ics-arch::DAA-019 r2 及版本衔接 -> 各任务 Development 接续 -> fresh-context Verification -> Human Owner 分别最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS 与 DAA 的逐 PLC S7 点位 JSON 双向交换详细设计
Owner: Automation World / Device Simulator 与 Data Acquisition Agent
Acceptance Chain Reference: Development Lifecycle Workflow；本设计和两个实施任务的精确范围批准、各自 Development、fresh-context Verification 与 Human Owner 最终验收分别记录。
Related Task: device-simulator::DS-005 r2; aiis-ics-arch::DAA-019 r2; device-simulator::DS-003 r5; aiis-ics-arch::DAA-017 r5; device-simulator::DS-004 r2; aiis-ics-arch::DAA-018 r3

# ARCH-PLC-001 r7：双向 PLC JSON 的安全验收衔接（已批准）

## 1. 范围与当前事实

本 r7 仅修订已批准设计的 A06 验收环境与步骤，已获 Human Owner 精确批准；原 r6 设计、两端 r1 实施范围及其批准事实保留，产品功能、数据保护和其余验收不变。用户要求：DAA「PLC 配置」页头与 DS「实例」页头均有「导入 PLC JSON」「导出 PLC JSON」；导出时按 PLC 实例勾选，一台一个完整文件；DS→DAA 已有能力须保留，新增 DAA→DS，并使从 DAA 导入的实例能够由 DS 导出相同合同。显示名未设置时留空，不能进入 DAA 实际 v2 上报。FF/CA 暂不处理。

既有 DS-003 r5 和 DAA-017 r5 各自 `qa_passed`、待 Human Owner 最终验收；它们的精确范围、QA1 失败、QA2 阻塞与通过证据保持在各自 bundle，不能把新候选的结果倒记给旧候选。DS-004 r2、DAA-018 r3 仍各自 `qa_blocked`，本设计不改变其状态。原 r5 的 JSON、双语、物理布局、来源和真实上报保护规则继续适用，但以下条款明确接替 r5 中“DAA 不导出、DS 不导入、DAA 仅接受 DS producer、历史身份一律拒绝”的本期限定。r6 及其所含 r5 完整历史按原字节封存在本文附录；子任务采用自己的 Task ID / Revision，不继承批准或验收。

本 r7 仅规定跨端合同及边界；软件实施及验收衔接分别以 [DS-005 r2](../../device-simulator/plans/DS-005-plc-json-bidirectional/spec.md)、[DAA-019 r2](../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/spec.md) 为准。此前两项 r1 已精确批准并已有 Development 候选，相关实现和自检不是独立 QA；本 r7 和两项 r2 已获 Human Owner 分别精确批准。两端候选共同组成闭环，任一侧未通过时不得宣称整体通过。

## 2. 文件和用户操作合同

1. 两端仍使用附录 A 中 r6 所封存的 r5 §4 的 `format=aiis.plc_points`、整数 `schema_version=1`，每文件一 PLC、完整 DB/点（含停用点），不制造筛选版。严格编码、1 MiB / 层级 16 / 32 DB / 4096 点、字段闭合、UUID v4、类型/地址/重叠、TSAP 和源校验继续按 r5。两端导入器均接受符合该合同的 `device_simulator` 与 `data_acquisition_agent` producer，而非用 origin 推断 producer。出现不满足合同或本地约束的内容应定位并拒绝，不静默裁剪、猜测或改名。
2. DS 导出选择真实 `saved_revision`；DAA 导出由用户选 `saved_draft` 或 `active_revision`，读取所选持久配置的实际 payload 字节、标识及 SHA，不混入尚未保存的界面编辑。DAA 普通 DB/UDT 来源与已导入 catalog 来源，只要是符合合同的已保存配置，都必须可导出；不是只支持 DS catalog。实际导出者的 `export.producer`、profile、版本、真实 `+08:00` 生成时间与所选 payload 摘要须如实填写；草稿 ETag 不称为不可变 revision。
3. `origin` 为外部 PLC 身份命名空间，DS/DAA 转发均保留既有 origin 与 DB/点外部 ID；本地独立创建的 DAA PLC 以真实 DAA profile/PLC 创建 origin。DB 和点 ID、技术名、类型、地址、启停声明、`source_path`、双语显示名、旧无语言名称及独立 description 均按各自真实配置和合同表达。DAA 的 `comment` 映射 description；不可从旧名称或另一语言猜值。DAA 导出省略 DB 层 `source_enabled`，点层取其当前 Point.enabled；DS 导出两层取自身实际 enabled。两者本地启停含义不同；导入时不据对方标志自动授予采集、模拟或写入许可。
4. 两端导出在各自页面入口提供实例勾选、版本/内容预览和显式目标目录；沿用 DS-003 r5 的无覆盖、原子发布、取消不留半文件、逐实例报告与真实版本差异提示。不得在界面数据中拼接未校验的文件，亦不静默保存/激活草稿。新文件选目录的授权仅限本次用户选择，不提供任意前端路径访问。
5. DS 导入一份 DS 或 DAA 文件，仅新建实例草稿。客户端地址只作为来源信息展示，不作为本机监听地址、也不试连；用户必须显式确认模拟监听 IP/端口及 rack/slot，冲突拒绝。新实例不自动启动，DB/点默认停用，策略/初值/权限不从 DAA 采集启用推断。按自身正常名称和布局确认及版本保存流程处理。保存原 JSON 字节/SHA、外部 origin 和逐 DB/点映射，目录来源不得冒称 TIA 源文件；导出该实例时仍保留外部 origin/ID，真实 producer 为 DS。
6. DAA 导入一份 DS 或 DAA 文件，预览原文件、外部身份、全部点、双语、description、目标地址及冲突；确认只原子提交一个新 PLC 草稿，默认停用、未分组、不连接、不采集、不上报、不自动激活。无历史/当前身份冲突时可沿用既有 DAA-017 的原 ID 新建规则。端点冲突由用户修改并重新预览；不允许覆盖、合并或重写当前实例。与当前草稿、active 或正在运行的实例为同一 origin/身份时拒绝；仅移除草稿但 active 仍有原实例时，提示先由用户按现有流程停采/断连并显式激活移除后的配置，再重试，不自动操作。

## 3. 已有历史的安全再导入

DAA 现有 `ensure_catalog_new` 还检查配置历史、runtime context、来源归档和 `plc_sources`；因此原实例删除后仍可能与历史冲突。直接复用旧本地 PLC ID 可能沿用采集 generation 或上报绑定，不能用“删除历史”或静默复用解决。

当相同外部 origin 或 PLC/DB/点身份只存在于历史，而当前草稿、active 和正在运行配置均无该实例、目标端点可用时，允许用户在预览中显式选择 **“作为新的本机实例导入”**。系统为新 PLC、DB、点及来源对象创建不与当前和历史对象冲突的全新本地 UUID，完整持久保存外部 origin、外部 DB/点 ID → 新本地 ID 映射和输入原字节/SHA；每次预览/确认以源字节、端点、草稿 ETag 及映射绑定并重验，取消、过期、并发或失败无部分写入。显示外部身份与新本地身份的含义及新旧历史分开，用户不确认则拒绝。只在历史出现相同文件 SHA 时可按真实字节校验复用物理内容归档，但不得覆盖其原 ID、元数据或历史；新的逻辑来源/映射仍须独立且可追溯。

新本机身份不继承旧 PLC 的采集 generation/sequence、样本、队列、回执、reporting binding 或已冻结正文；默认无上报绑定、未分组且停用。旧历史保持原身份并可按原有规则查询；界面不能宣称自动合并历史。之后的采集/上报须按既有显式配置和审批边界操作，导入和激活本身不发送真实请求。导出此实例时通过持久映射恢复外部 origin/DB/点 ID，并如实反映 DAA 当前自身点启用值，不能输出新本地 ID 冒充外部 ID。若现有存储、原文件完整性、映射重验、旧上报绑定隔离或原子性无法安全满足，停止并回 PM；不改变历史、不做数据库物理 DDL 或迁移来绕过。

## 4. 验收与实际测试路径

| 编号 | 必须可观察的结果 |
| --- | --- |
| A01 | DAA PLC 配置页头及 DS 实例页头均有明确中英导入/导出入口；导出按保存来源勾选实例，一台一份；旧 DB/UDT 导入不受影响，DAA 不同时挂载重复目录弹窗。 |
| A02 | DAA 原生 DB/UDT 配置及 catalog 配置均可导出完整合同；DS 导入文件并保存版本后重新导出，外部 origin、DB/点 ID、技术字段、双语、独立描述和空值真实保留；producer / 启停语义按实际导出方表达。 |
| A03 | 两端接受合规双 producer；重复键/未知字段、非法 UUID、错类型、越界/重叠、超限、缺失绑定与篡改归档按本端合同拒绝。DAA 对其当前模型不能表达的非默认 TSAP 明确拒绝；DS 对自身可表达的 TSAP 不得无故拒绝，对无法表达的值须提示并阻断，不能静默改写。DS 保留完整 256 字节旧无语言显示名不截断。 |
| A04 | 当前同源或身份、端点冲突明确阻断；历史同源仅经显式选择创建全新本地身份，双向映射、源归档、重开及再次导出保持；旧历史、来源、采样 generation/sequence、队列、回执和上报绑定保持，新实例不继承绑定。 |
| A05 | 同一保存版本多次导出、取消、同名文件及多选部分失败分别可核查；只读导出不改变配置、来源、selected/loaded 或运行。实际文件 SHA 随真实导出时间可不同，不将不同时间的整文件哈希要求相等。 |
| A06 | 按 §4.1 分别完成自有合成 profile 的真实持久化激活/历史隔离验证，以及两端 `.local/dev` 原生界面实际 DAA→DS→DAA 文件往返；另用真实 DAA 普通 DB/UDT 来源文件完成 DS 导入。三部分分别记录证据，任何必要部分不满足即 blocked；不以服务级检查、fixture 或预览冒充原生提交。 |
| A07 | 测试开始前核对应用、进程、profile、活动版本、原实例与自动连接/采集/上报；确认 DAA 原 `DEV-PLC-A` 及其配置、历史、样本、队列与回执不被修改或删除。只使用可识别合成对象、已确认的本地输出目录和 loopback 示例；无法保证旧实例不受触发时停止，不调整原有设置来强行继续。正常新草稿、revision、来源归档和审计可能增加，不能说整个 profile 零写。 |
| A08 | 既有 DS→DAA 真实文件导入及原 DB/UDT 功能做针对性回归；中英文/未设值和 DAA 实际 v2 构造路径以假 transport 证实显示名不外发，不执行真实 POST。相关构建/单元与必要的 macOS 原生页面检查由 Development 和 fresh Verification 记录；不以旧候选 QA 替代新候选。 |
| A09 | 两端用户手册按实际行为说明版本选择、地址确认、冲突、新本机身份与历史不合并、清理及实测限制；仅通过正常应用清理本任务合成对象，已成为历史的来源和记录保留。Windows、VM、真实 PLC、生产部署与真实上报不为本轮前置。 |

### 4.1 r7 已批准的三部分验证及证据边界

**A. 自有合成 profile：激活与历史隔离。** 在自有临时合成 profile 通过实际存储和应用服务保存并激活独立测试 PLC，形成旧配置与 runtime context；再移除它、保存并显式激活移除后的配置，随后实际以新本地身份导入，验证原身份、配置、样本、上报绑定、队列与回执独立保留，新 PLC/DB/点及来源本地身份不继承旧 generation/sequence 或绑定，新实例和点默认停用、未分组。合成样本及回执只能通过自有测试数据和 fake transport 制造，不连接真实设备、不发真实 POST。Development 现有针对性服务级检查若对应最终候选，可作为 Development 证据，由 fresh-context Verification 独立复核；服务级操作不称为 GUI。临时 profile 归任务所有，使用后按实际证据依赖和资源规则回收。

**B. 两端 `.local/dev`：真实原生文件往返。** 只复用前次 DAA-017 QA 中本线程建立、已实际激活且已安全移出的独立合成 PLC `e1dc3ad5-305f-4367-af1b-92333a582730` 的真实历史；其原 DS JSON 在历史来源归档，SHA-256 为 `5198f7fef382f9524b81c66275b76cbdb779deb7741df16d3005f809bf6662e3`。先只读核对该合成文件、来源 SHA、外部 origin/DB/点 ID、已保存 context 和先前 11 条 local-only 样本；可将**该确认属旧测试的合成 JSON**只读提取至本任务临时目录，不复制或修改用户旧数据库、配置或历史。旧 QA 已发生激活与采集，不得改写成本轮行为。

在核对后的 DAA 正式原生界面，从该合成 JSON 按“新本机实例”确认导入当前草稿，记录实际新本地 PLC/DB/点 ID L1；原目标端点若冲突，由用户选择经确认且未占用的 loopback 端点重新预览，不改既有实例。从 DAA 的 `saved_draft` 实际导出文件 F1。经 DS 正式原生界面使用 F1 新建测试实例、显式填写自有 loopback 监听信息、完成原有名称/布局确认并保存 DS 版本，再导出真实文件 F2。DAA 当前同源 L1 仍在草稿时对 F2 应明确拒绝；随后通过 DAA UI 只移除 L1 并保存草稿，不激活，使用 F2 真正确认新建 L2，核对 L2 与 L1 及原历史本机 ID 均不同、`importedLocalPlcId` 和选中项为 L2；外部 origin、DB/点外部 ID、类型、地址、双语及 description 保持且真实 producer/启用语义各自正确。对 L2 的 DAA 再导出按 D19-04 复核映射。记录 F1/F2 的原始文件 SHA、来源版本及逐项证据，不能用手写文件或仅预览替代实际提交。

本部分 **DAA 全程不激活、不采集、不上报**，不启动 DS 模拟或连接真实 PLC；不创建 DAA configuration revision，也不删旧版本。开始和结束核对已有 8 个配置版本的 ID / payload SHA、相关 context、原合成样本/归档和 `DEV-PLC-A` 草稿、active、来源及上报队列/回执保持；正常审计和只属于本任务的草稿/来源操作如实记录，不说整个 profile 零写。实际启动前重核应用、profile、进程、自动连接/采集/上报及未完成的 activation intent；待恢复或状态不明则停止，不通过更改用户数据绕过。DS 保存版本前核对不会裁剪任何既有历史。测试后仅通过正常应用移除 L2 与任务自建 DS 实例、保存草稿；已引用的任务历史及归档依规则保留，临时实际文件仅在无证据依赖时清理。无法安全操作或原生 GUI 无法完成即 blocked。

**C. 真实 DB/UDT 来源：DS05-02。** 在不修改 DAA `DEV-PLC-A` 的前提下，由 DAA UI 从该 PLC 的已保存普通 DB/UDT 来源只读导出一份真实完整文件；用该文件在空闲的 DS 新建**本任务测试实例**，显式确认自有 loopback 模拟监听地址，不再次提供 DB/UDT，按 DS 现有确认流程保存并重导。核对 BOOL/INT/REAL、双语、独立 description、外部身份、类型及地址满足 DS05-02/03；来源标注为该既有 DB/UDT 配置，不把其内容冒称合成，也不把 catalog 来源冒称 DB/UDT。DS 重导的实际文件交 DAA 原生界面预览时，当前 `DEV-PLC-A` 同源，应明确拒绝、不提交；该拒绝不能代替 B 的实际新实例导入。该 DS 测试实例为本任务新建对象、保持停机；不连接该文件中的原客户端地址。此有限只读输入符合 A07 对既有 `DEV-PLC-A` 的保护；A07 的任务测试对象仍需可识别、不得覆盖已有对象。实际文件仅供本次验证，不进入仓库，确认无证据依赖后安全清理。

上述 `.local/dev` 及自有临时 profile 使用、测试对象清理为用户已授权的环境范围；本 r7 及两项 r2 验收衔接已获精确批准。不能删除整个 profile、任意既有实例或历史；测试目标、端口、待恢复激活或安全隔离不明确时停止。先前界面隔离事件及未完成的基础任务验证不因本 r7 消失。

## 5. 执行边界、风险与 handoff

- Human Owner 曾分别精确批准 DS-005 r1、DAA-019 r1 和 r6 的旧任务顺序衔接；r1 候选及 Development 自检按各自 tasks 原记录保留。本次 A06 变更属于实质验收修订，Human Owner 已精确批准本 r7、DS-005 r2、DAA-019 r2 及版本衔接，Development 按各自文件 allowlist 接续；沿用原顺序，不以 DS-003 r5、DAA-017 r5、DS-004 r2 或 DAA-018 r3 的最终验收作为新任务开工前置。协调共享文件与最终组合候选；旧 QA 及各任务 Human Owner 最终验收独立保留。
- 导入更换本地身份是为隔离历史而设计的显式新建，不是原实例更新、历史恢复或自动上报续传。真实项目启用或重新绑定上报仍走既有流程与独立 gate。旧版二进制读取新增配置元数据的兼容性须实测或如实标明，不得推断；物理 DDL、迁移、真实设备、外部 POST、FF/CA、发布及生产采用均不包含在内。
- PM 使用 `aiis`、`project-governance` 收敛合同；交 Development 按各子任务加载 `plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`，Verification 以 fresh context 独立复核。项目角色为 contract_only；角色约定和 diff 审计不证明平台 ACL 或自动路由。
- 原 r6 与两项 r1 的批准事实见下节及附录；本 r7、DS-005 r2、DAA-019 r2 的精确批准见 §7。

## 6. r6 Human Owner 精确范围批准（历史）

2026-11-17（Asia/Shanghai），Human Owner 审阅协调者列明的三个精确版本后明确回复：

> 批准三个版本，继续开发

该决定精确批准 `aiis-ics-arch::ARCH-PLC-001 r6` 设计、`device-simulator::DS-005 r1` 和 `aiis-ics-arch::DAA-019 r1` 各自实施范围，以及 §5 所述旧任务时序衔接。审阅时完整草案 SHA-256：ARCH-PLC-001 r6 为 `69c744e82077e7c21dff8032ad0231d9ea0814bdb0f684e0f9630ba3d81d4180`；DS-005 r1 为 `23e9538ceab3d51ad49f05f8cb24a2aa3f6298c19ea77e06a4d738f6a9e62190`；DAA-019 r1 为 `576646f841feebf06258435a7dc0f089d7e40be5c96da6676a204eb318161529`。

当时各任务按各自已批准 allowlist 进入 Development；本次验收修订已获新版本批准，接续后进行 fresh-context Verification 和 Human Owner 最终验收。此决定不改变旧任务独立 QA / Owner 状态，不批准真实设备、真实 POST、物理 DDL、历史删除、FF/CA、发布或生产采用。


## 7. r7 修订及 Human Owner 精确批准

2026-11-17，协调者只读核对 DAA `.local/dev` 已有 8 个配置版本；当前激活的 `prune_config` 使用 `skip(8)`，继续激活可能裁剪已有用户旧版本，不能满足原 r6 A06 与 A07 同时保护历史的要求。本 r7 只把 A06 的激活与历史证明移到自有合成 profile，并以既有旧测试的真实历史和两端原生文件往返验证当前实际环境；补充真实 DB/UDT 来源文件的 DS 验证。原 A01–A05、A07–A09、产品合同和数据保护不变。原 r6、DS-005 r1、DAA-019 r1 以及其批准、Development 候选和证据不倒改。

2026-11-18（Asia/Shanghai），Human Owner 审阅三个精确版本后明确回复：

> 批准 ARCH-PLC-001 r7、DS-005 r2、DAA-019 r2 及版本衔接，继续完成联测和清理。

该决定精确批准 `aiis-ics-arch::ARCH-PLC-001 r7`、`device-simulator::DS-005 r2`、`aiis-ics-arch::DAA-019 r2` 及版本/既有实施衔接。审阅时完整草案 SHA-256：ARCH-PLC-001 r7 为 `e9ed70a41b1f7255dbc65ddbc83f4c58db1900cd4e172dddc48f39a99f170cd9`；DS-005 r2 为 `bb94ef1d1b6cc2a88deeb7e984d4e69b98d79412b711fb0c9e46ddf706c93ceb`；DAA-019 r2 为 `48721591ef64ab11100977858c58f51deea08ade5caf26bfe0618d692ed53705`。各任务 Development 接续、fresh-context Verification 和 Human Owner 最终验收仍各自独立；本批准不代表 QA 或最终验收，也不授权真实设备、真实 POST、物理 DDL、删除用户历史、FF/CA 或发布。

## 附录 A：已批准 ARCH-PLC-001 r6 完整原文（含全部历史）

写前完整 SHA-256：`0eb0c10e70507903347b216d2ac712add430fc4511b251a2ad93e00e19ce1408`。围栏内保留原始 UTF-8 字节及末尾换行，含 r5 及更早历史；本 r7 已获精确范围批准。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: ARCH-PLC-001
Revision: r6
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 ARCH-PLC-001 r6、device-simulator::DS-005 r1、aiis-ics-arch::DAA-019 r1 及旧任务时序衔接 -> 各任务 Development -> fresh-context Verification -> Human Owner 分别最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS 与 DAA 的逐 PLC S7 点位 JSON 双向交换详细设计
Owner: Automation World / Device Simulator 与 Data Acquisition Agent
Acceptance Chain Reference: Development Lifecycle Workflow；本设计和两个实施任务的精确范围批准、各自 Development、fresh-context Verification 与 Human Owner 最终验收分别记录。
Related Task: device-simulator::DS-005 r1; aiis-ics-arch::DAA-019 r1; device-simulator::DS-003 r5; aiis-ics-arch::DAA-017 r5; device-simulator::DS-004 r2; aiis-ics-arch::DAA-018 r3

# ARCH-PLC-001 r6：同一 PLC JSON 的双向交换（设计范围已批准）

## 1. 范围与当前事实

本 r6 设计范围已获 Human Owner 精确批准；本决定不代表最终验收。用户要求：DAA「PLC 配置」页头与 DS「实例」页头均有「导入 PLC JSON」「导出 PLC JSON」；导出时按 PLC 实例勾选，一台一个完整文件；DS→DAA 已有能力须保留，新增 DAA→DS，并使从 DAA 导入的实例能够由 DS 导出相同合同。显示名未设置时留空，不能进入 DAA 实际 v2 上报。FF/CA 暂不处理。

既有 DS-003 r5 和 DAA-017 r5 各自 `qa_passed`、待 Human Owner 最终验收；它们的精确范围、QA1 失败、QA2 阻塞与通过证据保持在各自 bundle，不能把新候选的结果倒记给旧候选。DS-004 r2、DAA-018 r3 仍各自 `qa_blocked`，本设计不改变其状态。原 r5 的 JSON、双语、物理布局、来源和真实上报保护规则继续适用，但以下条款明确接替 r5 中“DAA 不导出、DS 不导入、DAA 仅接受 DS producer、历史身份一律拒绝”的本期限定。r5 及其完整历史按原字节封存在本文附录；子任务采用自己的 Task ID / Revision，不继承批准或验收。

本 r6 仅规定跨端合同及边界；软件实现分别以 [DS-005 r1](../../device-simulator/plans/DS-005-plc-json-bidirectional/spec.md)、[DAA-019 r1](../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/spec.md) 为准。两端均为独立拥有者和验收链；Human Owner 本次已分别精确批准两项 r1。两端候选共同组成闭环，任一侧未通过时不得宣称整体通过。

## 2. 文件和用户操作合同

1. 两端仍使用附录 r5 §4 的 `format=aiis.plc_points`、整数 `schema_version=1`，每文件一 PLC、完整 DB/点（含停用点），不制造筛选版。严格编码、1 MiB / 层级 16 / 32 DB / 4096 点、字段闭合、UUID v4、类型/地址/重叠、TSAP 和源校验继续按 r5。两端导入器均接受符合该合同的 `device_simulator` 与 `data_acquisition_agent` producer，而非用 origin 推断 producer。出现不满足合同或本地约束的内容应定位并拒绝，不静默裁剪、猜测或改名。
2. DS 导出选择真实 `saved_revision`；DAA 导出由用户选 `saved_draft` 或 `active_revision`，读取所选持久配置的实际 payload 字节、标识及 SHA，不混入尚未保存的界面编辑。DAA 普通 DB/UDT 来源与已导入 catalog 来源，只要是符合合同的已保存配置，都必须可导出；不是只支持 DS catalog。实际导出者的 `export.producer`、profile、版本、真实 `+08:00` 生成时间与所选 payload 摘要须如实填写；草稿 ETag 不称为不可变 revision。
3. `origin` 为外部 PLC 身份命名空间，DS/DAA 转发均保留既有 origin 与 DB/点外部 ID；本地独立创建的 DAA PLC 以真实 DAA profile/PLC 创建 origin。DB 和点 ID、技术名、类型、地址、启停声明、`source_path`、双语显示名、旧无语言名称及独立 description 均按各自真实配置和合同表达。DAA 的 `comment` 映射 description；不可从旧名称或另一语言猜值。DAA 导出省略 DB 层 `source_enabled`，点层取其当前 Point.enabled；DS 导出两层取自身实际 enabled。两者本地启停含义不同；导入时不据对方标志自动授予采集、模拟或写入许可。
4. 两端导出在各自页面入口提供实例勾选、版本/内容预览和显式目标目录；沿用 DS-003 r5 的无覆盖、原子发布、取消不留半文件、逐实例报告与真实版本差异提示。不得在界面数据中拼接未校验的文件，亦不静默保存/激活草稿。新文件选目录的授权仅限本次用户选择，不提供任意前端路径访问。
5. DS 导入一份 DS 或 DAA 文件，仅新建实例草稿。客户端地址只作为来源信息展示，不作为本机监听地址、也不试连；用户必须显式确认模拟监听 IP/端口及 rack/slot，冲突拒绝。新实例不自动启动，DB/点默认停用，策略/初值/权限不从 DAA 采集启用推断。按自身正常名称和布局确认及版本保存流程处理。保存原 JSON 字节/SHA、外部 origin 和逐 DB/点映射，目录来源不得冒称 TIA 源文件；导出该实例时仍保留外部 origin/ID，真实 producer 为 DS。
6. DAA 导入一份 DS 或 DAA 文件，预览原文件、外部身份、全部点、双语、description、目标地址及冲突；确认只原子提交一个新 PLC 草稿，默认停用、未分组、不连接、不采集、不上报、不自动激活。无历史/当前身份冲突时可沿用既有 DAA-017 的原 ID 新建规则。端点冲突由用户修改并重新预览；不允许覆盖、合并或重写当前实例。与当前草稿、active 或正在运行的实例为同一 origin/身份时拒绝；仅移除草稿但 active 仍有原实例时，提示先由用户按现有流程停采/断连并显式激活移除后的配置，再重试，不自动操作。

## 3. 已有历史的安全再导入

DAA 现有 `ensure_catalog_new` 还检查配置历史、runtime context、来源归档和 `plc_sources`；因此原实例删除后仍可能与历史冲突。直接复用旧本地 PLC ID 可能沿用采集 generation 或上报绑定，不能用“删除历史”或静默复用解决。

当相同外部 origin 或 PLC/DB/点身份只存在于历史，而当前草稿、active 和正在运行配置均无该实例、目标端点可用时，允许用户在预览中显式选择 **“作为新的本机实例导入”**。系统为新 PLC、DB、点及来源对象创建不与当前和历史对象冲突的全新本地 UUID，完整持久保存外部 origin、外部 DB/点 ID → 新本地 ID 映射和输入原字节/SHA；每次预览/确认以源字节、端点、草稿 ETag 及映射绑定并重验，取消、过期、并发或失败无部分写入。显示外部身份与新本地身份的含义及新旧历史分开，用户不确认则拒绝。只在历史出现相同文件 SHA 时可按真实字节校验复用物理内容归档，但不得覆盖其原 ID、元数据或历史；新的逻辑来源/映射仍须独立且可追溯。

新本机身份不继承旧 PLC 的采集 generation/sequence、样本、队列、回执、reporting binding 或已冻结正文；默认无上报绑定、未分组且停用。旧历史保持原身份并可按原有规则查询；界面不能宣称自动合并历史。之后的采集/上报须按既有显式配置和审批边界操作，导入和激活本身不发送真实请求。导出此实例时通过持久映射恢复外部 origin/DB/点 ID，并如实反映 DAA 当前自身点启用值，不能输出新本地 ID 冒充外部 ID。若现有存储、原文件完整性、映射重验、旧上报绑定隔离或原子性无法安全满足，停止并回 PM；不改变历史、不做数据库物理 DDL 或迁移来绕过。

## 4. 验收与实际测试路径

| 编号 | 必须可观察的结果 |
| --- | --- |
| A01 | DAA PLC 配置页头及 DS 实例页头均有明确中英导入/导出入口；导出按保存来源勾选实例，一台一份；旧 DB/UDT 导入不受影响，DAA 不同时挂载重复目录弹窗。 |
| A02 | DAA 原生 DB/UDT 配置及 catalog 配置均可导出完整合同；DS 导入文件并保存版本后重新导出，外部 origin、DB/点 ID、技术字段、双语、独立描述和空值真实保留；producer / 启停语义按实际导出方表达。 |
| A03 | 两端接受合规双 producer；重复键/未知字段、非法 UUID、错类型、越界/重叠、超限、缺失绑定与篡改归档按本端合同拒绝。DAA 对其当前模型不能表达的非默认 TSAP 明确拒绝；DS 对自身可表达的 TSAP 不得无故拒绝，对无法表达的值须提示并阻断，不能静默改写。DS 保留完整 256 字节旧无语言显示名不截断。 |
| A04 | 当前同源或身份、端点冲突明确阻断；历史同源仅经显式选择创建全新本地身份，双向映射、源归档、重开及再次导出保持；旧历史、来源、采样 generation/sequence、队列、回执和上报绑定保持，新实例不继承绑定。 |
| A05 | 同一保存版本多次导出、取消、同名文件及多选部分失败分别可核查；只读导出不改变配置、来源、selected/loaded 或运行。实际文件 SHA 随真实导出时间可不同，不将不同时间的整文件哈希要求相等。 |
| A06 | 在经确认的两端 `.local/dev` 通过应用完成一次**真实文件** DAA→DS→DAA：使用独立合成 PLC，先保存并显式激活一次以形成历史，但不连接、不采集、不上报；DAA 导出；DS 导入并保存，DS 导出；DAA 通过正常 UI 移除该测试 PLC、保存并显式激活移除后的配置，保留历史，再以新本机身份实际导入 DS 原文件并核对完整内容与身份映射。先证明当前同源拒绝；非手写 fixture、非只解析/预览。若测试环境/历史冲突无法安全处理，明确 blocked。 |
| A07 | 测试开始前核对应用、进程、profile、活动版本、原实例与自动连接/采集/上报；确认 DAA 原 `DEV-PLC-A` 及其配置、历史、样本、队列与回执不被修改或删除。只使用可识别合成对象、已确认的本地输出目录和 loopback 示例；无法保证旧实例不受触发时停止，不调整原有设置来强行继续。正常新草稿、revision、来源归档和审计可能增加，不能说整个 profile 零写。 |
| A08 | 既有 DS→DAA 真实文件导入及原 DB/UDT 功能做针对性回归；中英文/未设值和 DAA 实际 v2 构造路径以假 transport 证实显示名不外发，不执行真实 POST。相关构建/单元与必要的 macOS 原生页面检查由 Development 和 fresh Verification 记录；不以旧候选 QA 替代新候选。 |
| A09 | 两端用户手册按实际行为说明版本选择、地址确认、冲突、新本机身份与历史不合并、清理及实测限制；仅通过正常应用清理本任务合成对象，已成为历史的来源和记录保留。Windows、VM、真实 PLC、生产部署与真实上报不为本轮前置。 |

上述 `.local/dev` 使用与本任务合成对象清理已有用户授权；执行前必须重新核对现状。不能删除整个 profile、任意既有实例或历史；测试目标、端口或安全隔离不明确时停止。先前界面隔离事件及未完成的基础任务验证不因本 r6 消失。

## 5. 执行边界、风险与 handoff

- Human Owner 已分别精确批准 DS-005 r1、DAA-019 r1 及本 r6 的顺序衔接，两项新任务可按各自范围实施，不以 DS-003 r5、DAA-017 r5、DS-004 r2 或 DAA-018 r3 的最终验收作为开工前置。各任务按自己的文件 allowlist、风险和独立 QA 执行；涉及相同工作树时协调共享文件和最终组合候选，不能覆盖并行变更。两项原 r5 QA 和最终验收独立保留，不因新 r1 被自动验收或作废。
- 导入更换本地身份是为隔离历史而设计的显式新建，不是原实例更新、历史恢复或自动上报续传。真实项目启用或重新绑定上报仍走既有流程与独立 gate。旧版二进制读取新增配置元数据的兼容性须实测或如实标明，不得推断；物理 DDL、迁移、真实设备、外部 POST、FF/CA、发布及生产采用均不包含在内。
- PM 使用 `aiis`、`project-governance` 收敛合同；交 Development 按各子任务加载 `plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`，Verification 以 fresh context 独立复核。项目角色为 contract_only；角色约定和 diff 审计不证明平台 ACL 或自动路由。
- 本 r6 于 2026-11-17 先形成草案；当时用户“开搞吧”未被记录为对尚未审阅的 r6 / r1 的精确批准。其后 Human Owner 作出的精确批准见下节。

## 6. Human Owner 精确范围批准

2026-11-17（Asia/Shanghai），Human Owner 审阅协调者列明的三个精确版本后明确回复：

> 批准三个版本，继续开发

该决定精确批准 `aiis-ics-arch::ARCH-PLC-001 r6` 设计、`device-simulator::DS-005 r1` 和 `aiis-ics-arch::DAA-019 r1` 各自实施范围，以及 §5 所述旧任务时序衔接。审阅时完整草案 SHA-256：ARCH-PLC-001 r6 为 `69c744e82077e7c21dff8032ad0231d9ea0814bdb0f684e0f9630ba3d81d4180`；DS-005 r1 为 `23e9538ceab3d51ad49f05f8cb24a2aa3f6298c19ea77e06a4d738f6a9e62190`；DAA-019 r1 为 `576646f841feebf06258435a7dc0f089d7e40be5c96da6676a204eb318161529`。

各新任务按各自已批准 allowlist 进入 Development，之后进行 fresh-context Verification 和 Human Owner 最终验收。此决定不改变旧任务独立 QA / Owner 状态，不批准真实设备、真实 POST、物理 DDL、历史删除、FF/CA、发布或生产采用。

## 附录 A：ARCH-PLC-001 r5 原文与历史（仅历史，非当前活动规格）

写入前完整 SHA-256：`5d27670905ad0ab3cda4490292299e6ace21906a9593191de319a47b887083cf`。围栏内按写前原始 UTF-8 字节及末尾换行保留，内含更早批准与历史；r6 条款与其冲突处以本次已批准的 r6 为接续。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: ARCH-PLC-001
Revision: r5
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 ARCH-PLC-001 r5、DS-003 r4、DAA-017 r4 及下游顺序调整 -> 各任务 Development -> fresh-context Verification -> 各自 Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS 与 DAA 的逐 PLC S7 点位 JSON 双向交换详细设计
Owner: Automation World / Device Simulator 与 Data Acquisition Agent
Acceptance Chain Reference: 本任务遵循 Development Lifecycle Workflow；Human Owner 审阅精确设计 Revision，后续 Development、fresh-context Verification 和 Human Owner 最终验收各为独立 gate。
Related Task: device-simulator::DS-004 r2; aiis-ics-arch::DAA-018 r3; device-simulator::DS-003 r4; aiis-ics-arch::DAA-017 r4; device-simulator::DS-002; aiis-ics-arch::DAA-005; aiis-ics-arch::DAA-006; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013

# DS 与 DAA 点位双语显示及逐 PLC JSON 详细设计 r5

## 1. 本次请求、范围与状态

2026-11-17（Asia/Shanghai），Human Owner 反馈已在 DS、DAA 各自的 .local/dev 手工测试中英切换及 display_name，结果没问题；该反馈是用户手工观察，不等于独立 QA 通过或最终验收，两基础任务当前仍为 qa_blocked。用户明确授权后续 JSON 互通直接使用各应用各自的 .local/dev，无需另建 profile；环境授权与实施范围批准为不同事实；下文记录本次对精确版本的批准。

本版 r5 设计范围已获 Human Owner 精确批准。Human Owner 希望尽快完成 DS 按实例导出一份完整 JSON，再导入 DAA，不需要再次处理 DB/UDT；两端保留中英文点位显示名，DAA 既有上报不带显示名。本次 DAA 只新建 PLC：已有来源或身份冲突明确拒绝，不做既有 PLC 合并、覆盖或重导更新；这些相对已批准 r4 的收窄已一并获得本次范围批准。FF、CA、虚拟机、Windows 验证和现场设备不属于本轮。JSON 格式和完整点集不变；DS 反向导入、DAA 导出和其他方向为后续设计。

原 r4 设计已获精确批准，并要求 DS-004、DAA-018 各自独立 QA 和 Owner 最终验收后，才分别审批和实施 DS-003、DAA-017。DS-004 r2 和 DAA-018 r3 的实施范围已批准，当前各自 QA 均为 qa_blocked、最终验收未发生。原 r4 及其全部批准和历史完整封存在附录；原 r4 门槛在 r5 批准前有效，本次 Owner 明确批准其下游顺序调整。

本次 Owner 明确批准的时序变更是：本 r5 设计、DS-003 r4、DAA-017 r4 实施范围及本段版本衔接精确获批后，两个 JSON 任务可按各自范围开发和自检，不再等待两基础任务的最终验收。两个基础任务的自身功能、验收、风险、历史和 qa_blocked 状态不因时序变化被调整或标记通过；各任务仍各自独立 Verification 和 Owner 最终验收。整体结论只能按真实完成的双语、上报与同一文件互通证据表述。

DS-004 r2 和 DAA-018 r3 的活动规格亦写有原下游时序，本次 Owner 已明确批准仅对其下游开工 gate 的后续衔接，不改变两份基础规格的自身验收或风险。原门槛在本次批准前有效；PM 在原规格追加可追溯的 Owner 决定并保留原文。若需要改变基础任务自身 AC、范围或风险，必须另提各自新 Revision 和批准。此次 PM 登记阶段仅修改规格；Development 可按各自已批准白名单和 gate 实施。

## 2. 已核现状与设计目标

- DS 可配置多个实例、导入 DB/UDT，并区分草稿、保存版本、selected 和实际 loaded；DS 的点位 JSON 导入/导出仍是提案，不能声称已实现。[DS 使用手册](../../device-simulator/USER_GUIDE.zh-CN.md) · [DS-002 设计](../../device-simulator/plans/DS-002-multi-protocol-simulation-and-device-debugging/spec.md) · [DS 配置模型](../../device-simulator/runtime/src/domain/configuration.rs)
- DAA 现有来源导入入口为 .db/.udt；点位源、地址、分组、草稿和采集配置均有既有验证与持久化边界。[DAA 导入入口](../../data-acquisition-agent/src/app/plc/components/SourceImportPanel.vue) · [DAA 配置校验](../../data-acquisition-agent/src-tauri/src/domain/local_configuration.rs) · [DAA-005](../../data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md) · [DAA-006](../../data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/spec.md)
- DAA 配置、source_documents、runtime context、样本、上报与回执各有权威；现有相同正文的物理归档去重不能当作重写本地身份或历史的授权。[本地存储说明](../../data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md) · [存储 schema](../../data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs)
- DS 当前 Point 有 `display_name`，未标记语言，TIA 导入还会以源注释初始化它；DAA Point 有独立 `comment`，且 `PointFact.definition` 复制整个 Point，`facts_wire::definition_check` 对键严格闭合。两者不能推断已拥有带语言标记的名称或将注释当作双语名。
- 只读检索本仓产品源码及公开 contracts 未发现 `aiis.plc_points` 生产器、消费者或已发布公共合同；r2 是获批设计，不能证明仓外人工文件不存在。首批落地仍拟采用 schema_version 1，兼容 r2 文档的可选无语言 `display_name`，新增可选 `display_names`；若发现真实既有消费方/数据，则停止并回 PM 评估版本与迁移，不宣称旧解析器可读取新字段。
- FF 当前不能直接消费本候选完整 JSON，其后续适配另行处理。

设计覆盖 DS 和 DAA 各自按 PLC/实例导入、导出同一种完整 S7 点位 JSON，支持 BOOL、INT、REAL 等可表达类型和多 DB；多选时每台各生成一个文件，不因目标程序删除或另行生成子集。核心路径为 DS→DAA 无须再次提供 DB/UDT、DAA→DS 按显式模拟监听地址建立配置，以及 DAA→DAA 的按目标预览与导入。三条路径均是拟议功能，离线文件交换不要求源程序在线或共享 SQLite。

## 3. 文件边界与交互

- 一个 JSON 恰含一个逻辑 PLC、一个客户端连接描述、一个或多个 DB 和每个 DB 已声明点位。导出可多选实例，分别生成每台一个文件；不把多个 PLC 合并在同一 JSON。
- 文件携带完整已确认声明，包括停用点及其类型/地址；不包含实时值、凭据、环境文件、本机路径、DS 模拟初值/规则/写权限、DAA 采集组/周期/历史/上报数据。逻辑 source_path 可保留有事实的 TIA 路径，不代表文件系统路径。
- 导出针对所选持久配置预览完整信息，显式选择目录并处理重名；每份文件完整校验后原子落盘，失败不留下半文件。多选逐实例报告成功/失败/取消，不伪装全体成功。
- 本次 DAA 选择文件后只新建 PLC，预览连接、版本和全部点位；已有来源或身份冲突直接拒绝，确认后仅原子提交新草稿，不自动激活、连接、采集、上报或覆盖其他实例。已有 PLC 合并、差异更新与点位覆盖是后续范围。
- 两应用不共用 SQLite、可写目录或运行状态；导出文件只是快照，导入不构成现场地址、设备值、业务状态或写权限的证明。

## 4. 候选 JSON v1：单台 S7 PLC

本节是供 Human Owner 审阅的 DS/DAA 首次落地候选 v1，正式跨运行时合同发布需另项审批，本轮不修改根 contracts。r2 的 v1 是历史设计示意，不能当作已存在生产者/消费者或对旧生产文件的兼容证明。下例所有 ID、摘要、名称和端口均为合成示例，摘要仅展示词法。

~~~json
{
  "format": "aiis.plc_points",
  "schema_version": 1,
  "origin": {
    "kind": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "plc_id": "22222222-2222-4222-8222-222222222222"
  },
  "export": {
    "producer": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "config_state": "saved_revision",
    "revision_id": "33333333-3333-4333-8333-333333333333",
    "payload_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "exported_at": "2026-11-16T11:00:00+08:00"
  },
  "plc": {
    "name": "PLC_A",
    "protocol": "s7",
    "connection": {
      "host": "127.0.0.1",
      "port": 31281,
      "rack": 0,
      "slot": 1
    }
  },
  "dbs": [
    {
      "id": "44444444-4444-4444-8444-444444444444",
      "name": "MinimalImport",
      "number": 21,
      "size_bytes": 8,
      "source_enabled": true,
      "points": [
        {
          "id": "55555555-5555-4555-8555-555555555555",
          "name": "DB21_payload_ready_Bool",
          "display_name": "旧名称",
          "display_names": {
            "zh-CN": "就绪",
            "en-US": "Ready"
          },
          "description": "模拟设备就绪",
          "source_path": "payload.ready",
          "data_type": "BOOL",
          "byte_offset": 0,
          "bit": 0,
          "source_enabled": true
        },
        {
          "id": "66666666-6666-4666-8666-666666666666",
          "name": "DB21_payload_count_Int",
          "display_names": {
            "zh-CN": "计数",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.count",
          "data_type": "INT",
          "byte_offset": 2,
          "source_enabled": true
        },
        {
          "id": "77777777-7777-4777-8777-777777777777",
          "name": "DB21_payload_temperature_Real",
          "display_names": {
            "zh-CN": "",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.temperature",
          "data_type": "REAL",
          "byte_offset": 4,
          "source_enabled": true
        }
      ]
    }
  ]
}
~~~

### 4.1 字段与验证

1. 编码为 UTF-8 无 BOM；恰一顶层对象；拒绝重复 key、未知字段、非法 UTF-8、非整数词法用于整数、隐式转换和未明确允许的 null。必须是精确 format 和整数 schema_version 1；未知主版本拒绝，不猜兼容。文件上限 1 MiB，层级上限 16；单 PLC 最多 32 DB、4096 点，DB/点数量与文件大小都纳入导出预览。超预算整份文件失败，不静默截断。
2. origin 是 PLC 及其 DB/点身份的命名空间：kind 恰为 device_simulator 或 data_acquisition_agent，profile_id 为最初建立该命名空间的 DS 工作区 profile ID 或 DAA 本机实例 ID，plc_id 为该命名空间中的稳定 PLC 身份。它不表示每个点都是该应用创建，也不表示实际物理设备的作者或来源；export 单独记录本次实际导出者。三个字段均必填；ID 使用规范小写 UUID v4。文件名、显示名称、网络地址及 DAA 上报身份都不是 PLC 身份。导入后再从另一应用导出，保留 origin 和已映射的 DB/点身份；经本地显式新增的 DB/点可使用不冲突的本地 UUID v4 作为该命名空间下的新 ID，不改写既有 ID。若 ID 已冲突则阻断并经显式身份处理，不能在只读导出时悄悄换 ID。文件不声明逐点创建者，界面不得把 origin 当成所有点的创建者。
3. export.producer 是本次实际导出应用，v1 恰为 device_simulator 或 data_acquisition_agent；profile_id 是导出方自身的稳定 profile/instance 标识；exported_at 是真实生成时间，RFC 3339 且 +08:00。config_state 对 DS 是 saved_revision；对 DAA 是 active_revision 或 saved_draft。revision_id 对 DS/DAA 已保存版本为原版本 ID，对 DAA 草稿为导出时持久草稿 ETag；payload_sha256 是该应用实际选中保存内容的原始字节 SHA-256，小写 64 位十六进制。草稿 ETag 不冒充不可变 revision。导出者改变后的字段不伪称原程序导出。SHA 是完整性/追溯，不证明来源可信或物理设备正确。
4. plc.name 是非空显示名称，UTF-8 最多 100 字节；protocol 首期固定 s7。connection 为客户端目标：规范 IPv4 单播地址、port 1..65535、rack 0..7、slot 0..31。可选 local_tsap 与 remote_tsap 分别为客户端 calling/called，整数 1..65535；省略时 client local TSAP 为 0x0100，remote TSAP 为 0x0100 加 rack×32 加 slot。DS 监听地址及 TSAP 必须经客户端视角转换和用户确认；通配监听地址不能作为目标，loopback 只对同机有效。DAA 当前无自定义 TSAP 模型，遇非默认值应明确报不兼容并禁止导入执行，不可忽略。
5. dbs 必填且非空。每 DB id 是 UUID v4，number 为 1..65535 且同一 PLC 唯一，name 非空最多 100 UTF-8 字节，size_bytes 为 1..65536；points 必填且非空。DB ID、点 ID 在同一文件全局唯一，不能跨类别复用。每点 id 为 UUID v4，name 为同一 PLC 内唯一且稳定的 ASCII 程序引用名，最多 100 字节且须符合现有命名规则；显示名和语言切换不改变 name。可选 source_path、display_name、description 分别至多 512/256/500 UTF-8 字节；display_name 是无语言标记的原有单条值，须独立保留，不能归入双语任一字段。description 是独立的可选说明，最多 500 UTF-8 字节，非空时来自 DS 操作者显式编辑的独立描述或可核实的来源；不能用无语言 display_name 或双语名冒充注释。其他 producer 可以缺省该字段；缺省表示来源未提供，显式空串表示提供了空说明。
6. data_type 首期显式枚举 BOOL、BYTE、USINT、CHAR、INT、UINT、WORD、DINT、UDINT、DWORD、REAL 和 STRING[n]（n=1..254）。整数/REAL 按 S7 大端，REAL 为 IEEE 754 单精度，STRING 最大长度和编码须明确为 S7 STRING[n] 的 n 与 ASCII；CHAR 为单字节 ASCII。BOOL 必须有 bit=0..7，其他类型禁止 bit；字节宽按类型确定，STRING 占 n+2。必须满足 offset + 宽度不超过 DB 长度，同 DB 的物理占位不能重叠；不同 BOOL 可占同一字节的不同 bit。规则对禁用点也成立，不强推未获证明的 TIA 偏移或优化块布局。
7. source_enabled 只记录本次导出应用的启用事实，其解释依据 export.producer，而不是 origin.kind。DB 层的 source_enabled 是依导出者分型的可选布尔值：DS 导出时必填且如实取该 DB 的 enabled；DAA 当前的 DB 没有独立 enabled 事实，因此 DAA 导出必须省略该字段，不能从 PLC、采集组或点位状态推测。v1 消费者应验证此分型；DB 层缺失表示导出方没有提供此事实，不等于 true 或 false，显式 null 非法。点位层的 source_enabled 在 v1 对 DS 和 DAA 均为必填布尔值：分别取本次导出者的 Point.enabled；点层缺失或 null 为格式错误，不作 true/false 兜底。DS 点位启用与 DAA 的点位采集启用、分组语义不同。DS 文件经 DAA 导入并由 DAA 重新导出时，即使 origin.kind 仍为 device_simulator，也须按实际 export.producer=data_acquisition_agent 表达：DB 层省略，点位层为 DAA 本地实际 enabled；不能把旧 DS DB 启用状态冒称为 DAA 事实。
   这些字段既不是通用写权限，也不自动分配 DAA 采集组或改变 DS 模拟策略；消费者展示导出方、字段实际值或“未提供”，本地启用与引用由本地明确配置决定。点缺少地址、命名未确认、类型未知、物理重叠或不满足本合同：导出器列出具体问题并阻止该实例文件，不丢点、不把它标成默认地址、不因禁用而隐藏错误。首版不提供跳过点的导出模式。
8. 只输出本应用当前实例已经声明并确认的点，包括禁用点；不是对物理 PLC 全部地址的发现。无点的空洞不伪造成点。实际设备布局、源版本、访问许可及连接目标仍由使用者核对；模拟成功不证明真实 PLC 的布局或许可。
9. 可选观察信息和结构树不在 v1 必需合同。DS 可在导出预览显示实际 selected/loaded 事实，但不能据此伪造所选 saved revision。原始 DB/UDT 文件全文或模拟规则不进入该文件。未来如增加可选结构树，必须另定版本与消费者兼容，不能将当前点列表宣称为完整 TIA 源树。

10. 每点可选 display_names，存在时必须是严格对象且恰有 zh-CN、en-US 两个字符串，各最多 256 UTF-8 字节；空串为未设置，缺整个对象在新建目标表示两侧为空；null、非字符串、缺键或未知键拒绝。导出端输出两键，不能由 name、路径、comment、另一语言或旧单条值推测。已有目标三方比较与重导更新不在本期。
11. 可选 display_name 独立保留为语言未标记的单条值，不归入双语或 comment；原 JSON 字节与字段存在性均归档。source_path 是逻辑路径，不是本机文件系统路径。

### 4.2 来源版本选择

DS：用户选择一个真实、不可变的 saved revision 及其一个或多个实例；每个文件取该 revision 中对应实例切片。界面同时显示每实例当前 selected 和 actual_loaded 的版本及缺失状态；如果所选 revision 与实际加载不同，突出差异并要求明确确认。不得将 latest、草稿或 selected 冒充 actual_loaded，也不混入未保存编辑或运行值。用户可选择与已验证 actual_loaded 相同的 saved revision；直接从各实例不同 loaded 版本逐个导出的专用模式是后续扩展。

DAA：用户明确选择 active_revision 或已保存的 saved_draft，显示实际标识、来源和活动版本差异；未保存界面编辑不能混入。active 与 runtime loaded/used 分别显示，有差异如实提示。导出并不激活草稿或更改活动版本。两应用导出同一 origin 时，producer、版本和摘要描述当前导出者真实事实。

## 5. 首次新建与身份冲突

本次 DAA 只新建一台 PLC，只接受 DS 的 device_simulator producer。用户预览连接、全部 DB/点、双语、旧名称和描述后确认，原子写入草稿及原文件。文件的 PLC、DB 和点 UUID 在本地均未使用时沿用；任一身份已占用、origin 已存在或同文件重导，均明确拒绝整份，不分配替代身份、不覆盖、不合并；原草稿、ETag 和来源不变。

同一 PLC 多 DB 共用真实目录 source_id，并将原字节和 SHA 归档、完整映射点集。新点默认不采集，由用户完成新 PLC 的分组、启用、保存和激活。双语与 comment 可按现有流程编辑；目录点集、技术名、地址及类型覆盖、已有 PLC 匹配、差异重导和三方合并均移后，尝试修改受约束项须阻断。

取消或已知提交前失败无部分写入；并发更改草稿时重新预览，结果未知先查草稿及来源，不盲目重试。已有 PLC、样本及上报身份保持。

## 6. DS 导出与导入设计

### 6.1 DS 导出

导出入口以实例列表为起点，可多选并选择同一 saved revision，预览所选实例的来源版本、实际 loaded、连接目标、每个 DB/点及问题。源自 DS 的 id、name、type、byte/bit、DB number/length、来源路径及双语值按所选版本实际事实映射；真实存在的旧 display_name 作为未标记语言的独立字段保留，不能自动当作 description 或任何语言的显示名。DS 导出器对每点输出 `description` 字符串：非空原样取所选版本由用户显式填写的独立描述，缺省/空输出 `""`；不从旧显示名或注释猜测。所有点含停用点均按合同验证；确认或地址缺失时给出 DB/点定位并阻止该实例。初值、规则、权限、在线值不进入交换合同。

用户提供或确认采集客户端可达的 client host/port；不能把 0.0.0.0 作为远端连接目标，跨机器不能把 127.0.0.1 误当远端地址。TSAP 显示服务端与客户端方向并按既有合同核对。文件的导出成功不证明目标已连接、模拟正在运行或点值正确。

### 6.2 DS 从目录导入

输入可为 DS 或 DAA 导出的同格式文件。用户选择新建或匹配现有 DS 实例，预览并确认映射、DB/点、已有策略及冲突；只写 DS 草稿，按 DS 原有版本保存、加载流程处理，不启动。该能力尚未实现，可作为独立实施切片，与 DS→DAA 路径分别验证。

交换合同保留未标记 `display_name` 至多 256 UTF-8 字节，但当前 DS 本地旧 `displayName` 校验至多 200 字节。后续 DS 导入遇 201–256 字节的值，必须先有另行批准且验证过的无损承载方案，否则明确阻断该文件；不能截断、替换、混入双语字段或声称未来往返已实现。

文件中的 connection 是 client 连接目标，尤其 DAA 导出的地址可能是真实 PLC：**不得把它自动作为 DS 本机监听地址，也不得连接该地址。** 用户必须显式填写并确认自己的模拟监听 IP/端口及 rack/slot；冲突时拒绝。新实例默认不启动；模拟初值、规则、客户端读取/写入许可分别由用户在 DS 确认，不从 DAA 采集启用状态推导。目录点的来源被明确标记为 catalog，缺少原 TIA 结构时不伪造 DB/UDT 文件或完整来源树；维护一致的本地/外部身份映射及 DS 自身布局/命名确认。现有实例的规则、初值、权限和历史版本默认保留，冲突先预览，不能覆盖无关对象。


DS 的目录导入实施还需形成明确的 catalog 来源分型：保存并哈希用户选中的原始 JSON；同一实例的多个 DB 可引用同一份源版本，各 DB 分别绑定 sourceVersionId、原字节 SHA、originDbId 以及外部点 ID → 本地点 ID 的映射。外部 origin 和映射随工作区草稿/版本持久保存；catalog 绑定与既有 TIA SourceBinding 分型明确且不相互冒充。验证时重验源版本、SHA、origin、DB/点身份、完整点集、类型与物理地址；缺失、重复、越界、点集冲突或来源不一致阻断，不能退回未校验的手工点路径。没有原 TIA 文件时不伪造 DB/UDT 来源、结构树或初始值；DS 自身的名称/地址签名及加载前确认仍须由用户完成。

导入目录后若在 DS 修改目录 DB 的点集或地址，须显式预览并确认，生成绑定前一来源 SHA 的不可变内部点集快照；该快照标识为 DS 本地生成，不冒充外部交换文件，也不包含当前配置自身的 revision/SHA，避免自引用。新草稿以新快照重新建立完整映射，其他 DB、原始输入和历史版本保留；新点使用不冲突 UUID、原点身份不变。重新导出仍是同一个候选交换格式，并如实记录 DS 作为本次 producer。

优先评估使用现有 source_versions 和可选配置元数据且保持原 DDL；新旧二进制、已保存版本/原 SHA、selected/loaded 与回退必须单独验证。若需要修改物理库结构或迁移已用 profile，停止对应实现并另立明确的 schema-maintenance 与采用审批。

### 6.3 两端显示名基础

DS 点配置增加可选 `displayNames`（含 `zh-CN`、`en-US` 两个字符串）和独立可选 `description`；原 `displayName` 保持原值和“语言未标记”语义。用户可为手工点和 TIA 点显式填写/编辑描述，缺省或空为未设置；既有单条显示名和 TIA 注释不自动填充，旧值和历史保持。DAA 不在 Point 加双语字段，而在 schema 1 配置顶层新增可省略 `pointDisplayNames`，以当前本地点 UUID 对应相同两键对象；目录导入以后还需可省略 `pointLegacyDisplayNames` 单独保存未标记单条值，不能放在 `comment` 或 PointFact 中。字段缺省在内存显示两种语言均为空；两值都为空时新保存配置可省略对应可选字段/映射项，任一非空则保存两键完整对象，不因读取旧草稿或旧版本产生写回。所有字符串均按 §4.1 字节上限验证，非法类型/null/多余键拒绝，不做隐式转换。

两端点位列表保留程序 `name`，另显示**唯一由顶栏当前语言**选取的显示名；当前语言为空时显示空白或明确未设置占位，不回退 name、另一语言、comment 或旧 displayName。编辑框可同时编辑两个语言值；切换顶栏语言只改变显示，不修改配置、ETag、版本或上报。旧单条值如展示须标明语言未标记，保持原样，操作者可手工填写双语值但不得自动复制。

DAA 的映射键必须是配置中唯一存在的本地点 UUID，不能跨 PLC/引用不存在点；对同一身份重导、改名、分组、地址更新保留映射。明确删除点/DB/PLC 时仅在对应草稿事务移除已删除点的映射，旧版本/样本不重写；点 ID 改变或重绑必须显式预览，不能悄悄将旧点名称附到新身份。新的显示名字段不进入 `Point`、`PointFact.definition`，也不合并进 name、comment、value 或上报的其他字段。

## 7. DAA 导入：无需再提供 DB/UDT

### 7.1 来源分型和完整性

DAA 的 Db.source_id 仍须引用本 PLC 的真实来源。用户确认的完整 JSON 原始字节及 SHA 保存为目录 SourceDocument；一个新 PLC 的多个 DB 共用该逻辑 source，并各自绑定 DB 和点身份。目录分支严格重验原文、SHA、origin、DB/点成员、类型和布局，点集一一对应；不能伪造 .db/.udt 或 TIA 树。原 DB/UDT 的 source、tree、leaf_matches 和 UDT 校验保持。

本次只接受来源和 PLC/DB/点身份均无冲突的首次新建；目录点技术名、地址、类型及点集不提供覆盖，分组、周期和采集启用仍可设置。优先使用 schema 1 可省略目录元数据，不改物理 schema；不能做到无原 DB/UDT 地保存、激活和采集则回 PM。旧二进制原生兼容未验证，不声称通过；已授权的 .local/dev 可通过应用正常操作新增测试对象，不覆盖既有配置或历史。

### 7.1.1 事实和上报的双语边界（r4）

当前采集器直接 `point.clone()` 形成 `PointFact.definition`，`facts_wire::definition_check` 拒绝定义中的未知键。本设计仍将双语显示名放在配置顶层映射，不改变 Point 和严格校验；产品实际可达的所有外发正文均不得包含新增中英文显示名，也不得将其混入 name/value/comment 或其他字段。v2 Point 的 `name` 按原值上报，v2 正文原本没有 comment；本地 comment 与显示名保持独立，不修改后端或公共合同。

Development 的受控合成测试复现：历史 v1 测试构造链 `commit_cycle → build_delivery_cycle → freeze_cycle` 的 `Cycle.contextUtf8` 包含完整配置原文，所以本地冻结正文可包含双语 sentinel；这不是实际网络外发。只读源码显示，旧 v1 新建/冻结/选取及旧 `Transport::post` 在 `cfg(test)` 下，普通产品通过 runtime4 的 `next_sample_upload_ready` / `post_sample` 发送 v2，runtime3 的上报 start/resume 拒绝。生产代码仍可用 `facts_wire::build_cycle` / `schema.rs` 对旧账本做本地重构和完整性校验；不得误称该校验为 test-only 或删除。

保留 v1 原合同、完整 context、原摘要及旧冻结正文：test-only 合成构造应如实验证正文可能包含两个显示名，记录未外发，不能冒称 v1 零泄露通过。不得启用或暴露旧 v1 产品发送；未来重新启用须另立设计解决显示名外发、原文/摘要及历史兼容并独立批准。禁止裁剪上下文、重算旧摘要或改写原有冻结/排队记录和回执。

对产品实际可达的 v2 外发逐路径使用不同的中文、英文 sentinel 核验：新采样、已有 v2 冻结和重试，以及 `legacy_status` 判定从未发送的旧样本按原规则生成的新 v2 正文；不符合旧样本准入的状态继续复核或阻断。使用受控假 transport 截获正文且不发真实 POST，证明显示名不进入任何外发字段，原始 name/value 与既有字段存在/缺失语义不变；runtime3 禁止启动旧发送、产品特性/入口构建和源码闭包须验证。若发现产品可达旧 v1 发送或 v2 正文泄露显示名则阻断并回 PM。

测试还须对照旧样本、manifest、上下文、冻结正文、ACK 和历史 bytes/SHA；旧记录不重写，新的 configRevision、采样时间及摘要可正常变化。此边界是对 r3 §7.1.1 和 DAA-018 r2 DA18-06 的**实质验收修订**，Human Owner 已精确批准 ARCH r4 和 DAA-018 r3；仍须完成 Development、独立验证和最终验收，不将旧验收记为通过。DS-004 r2 已批准的基础实施独立继续；本 r5 在未获批准时不授权导出/导入。

### 7.2 DAA 导入体验与采集准入

用户选择 DS 实际导出的文件，仅新建 PLC；预览连接、全部 DB/点与双语信息，来源或身份冲突明确拒绝、不覆盖。新点默认不采集，用户设置分组、周期及启用，保存并显式激活。文件目标需确认，导入不自动连接。

验证不再提供 .db/.udt，使用自有 DS loopback S7 读取 BOOL、INT、REAL 并核对身份、地址、值及质量。解析文件或合成 fixture 不等于真实互通。

### 7.3 DAA 导出

按 PLC 多选、每台一文件，从用户选择的 saved_draft 或 active_revision 生成上述共同合同；仅导出该配置中已声明且可通过合同完整性检查的 DB/点。未确认地址或类型问题必须逐点报告并阻止该实例，不能用停用状态掩盖。重导本地由目录输入的配置时保留外部 origin 和稳定 ID 映射，并如实记录 DAA 作为导出者及选定配置版本；未绑定外部命名空间的 DAA 自建 PLC 以自身 profile/PLC 建立稳定身份，已绑定 origin 下新增点沿用该命名空间但不冒称来源。DAA 的 DB 没有独立启用字段，导出时省略该层 source_enabled；每个点的 source_enabled 必须取当前 DAA 配置中的 Point.enabled，即使来源命名空间是 DS 也不能沿用源文件的旧启用值。采集组、周期、运行历史、队列、上报设置及凭据不进入 JSON。



## 8. 拟议实施次序与任务归属

| 阶段 | 拟议范围 | 独立 gate |
| --- | --- | --- |
| P0 | 本 r5 与两个 JSON 实施任务 | Human Owner 已精确批准 ARCH-PLC-001 r5、DS-003 r4、DAA-017 r4 及下游时序衔接。 |
| P1 | DS-004 r2、DAA-018 r3 双语基础 | 保留已批准范围、原 QA 失败和当前 qa_blocked；各自完成原独立验证与最终验收，不能由 JSON 测试代替。 |
| P2 | DS-003 r4 实际导出；DAA-017 r4 仅新建 PLC 并导入同一文件 | P0 各项明确批准后可开发自检；来源或身份冲突拒绝，既有 PLC 合并、重导更新和覆盖移后。 |
| P3 | 受控本机互通及验收 | DS 导出一个合成实例的完整文件，DAA 不再提供 DB/UDT，完成导入、分组、保存和激活并读取合成 S7 值；双语切换和模拟 v2 上报不携带显示名各有真实证据。两个 JSON 任务分别 fresh-context QA、Owner 最终决定。 |
| 后续 | 既有 PLC 合并、重导更新和点位覆盖；DAA 导出、DS 导入、FF/CA、其他协议及现场采用 | 分别另定范围，不属于本期。 |

DS-004 r2、DAA-018 r3 原下游 gate 已由 Owner 明确批准的上述后续决定接续；其余基础功能和验收不变。综合结论要说明两基础任务当时的实际状态，不能将 JSON 验收当作两基础已通过。跨应用证据必须使用 DS 实际导出的原文件，不以手写样例冒称闭环。

## 9. 验收标准（待执行）

下列为已批准设计的软件验收口径，不是已完成证据；各切片确定精确 AC 和真实验证环境。

| 编号 | 可观察标准 |
| --- | --- |
| AC01 | 选择一个 PLC 实例，生成一份完整 JSON；文件、DB 和点属于所选实例，取消及失败不留下半文件。 |
| AC02 | 候选示例及多 DB 正例按冻结的格式验证；重复键、未知版本/字段、非法编码/类型/UUID、超限、缺字段、BOOL bit、STRING 宽度、越界与重叠有可复现负例。 |
| AC03 | DS saved/selected/actual_loaded 与 DAA saved_draft/active/loaded/used 各自准确呈现；实际版本和原 payload SHA 如实追溯，不混未保存编辑。 |
| AC04 | DS 包含 BOOL、INT、REAL、STRING 及停用点时导出完整声明；地址或名称未确认、未知类型、结构错误均定位并阻断该实例，无默认值和静默漏点。 |
| AC05 | 在核对后的 DAA .local/dev 中导入 DS 实际导出文件，仅新增本次测试 PLC，无须再提供 .db/.udt；用户显式分组、保存和激活后仅连接自有 DS loopback S7，读取 BOOL/INT/REAL 并核对 ID、地址、类型、值与质量，不触发既有设备或上报。 |
| AC06 | DAA 目录来源原字节/SHA、source_id、DB 和点位映射完整一致；伪造源、错 hash、错成员/类型/地址和重复绑定拒绝；旧 DB/UDT 的 tree/leaf_matches 验证不减弱。 |
| AC07 | 本次只从 DS 文件新建 PLC，来源或身份已存在时拒绝且不改草稿；DAA→DAA 后续。 |
| AC08 | DAA 导出保留为后续设计，不作为本次验收条件。 |
| AC09 | DS 的 DB 和点 source_enabled 按实际来源保留，DAA 不因此自动启用或分组；无效或缺失必填值拒绝。 |
| AC10 | DS JSON 导入及 DAA→DS 是后续范围。 |
| AC11 | PLC/DB/点身份冲突、origin 已存在或同文件重导均明确拒绝，原草稿、ETag 和来源不变；不合并覆盖。 |
| AC12 | 采集组、周期、DS 规则与历史版本、DAA 既有本地 ID、样本、generation/sequence、上报绑定、pending/ACK 及未选实例不被静默覆盖或改写。 |
| AC13 | 本次目录点集、技术名、地址或类型不可覆盖；允许新 PLC 设置组、周期与启用，源字节不变。 |
| AC14 | 已授权使用两应用各自 .local/dev；仅通过应用正常流程新增可识别测试对象与必要草稿/版本，不覆盖既有 PLC、配置内容、样本或历史，不改物理 schema。正常启动可能追加运行审计与更新 metadata，保存/激活可能产生新 revision 或改变 active 指针，不能声称整个 profile 零写。旧版原生兼容未验证不得声称通过；两基础原 AC 不变。 |
| AC15 | 无效或通配目标、重复身份、取消及并发有明确阻断或提示；仅使用确认的自有 loopback，不外推真实 PLC。 |
| AC16 | 中文、英文界面和本次导出导入流程可操作，既有启动、草稿、版本行为不被本次破坏；不将列宽跨重启、Windows、虚拟机或其他平台验证作为本次 JSON 主线前置。 |
| AC17 | 两端点表当前语言分别显示精确双语值；一侧空、一侧非空、两侧空和顶栏切换均可验证，切语言不写配置/ETag；旧 displayName 明示无语言且不混入两语言。 |
| AC18 | 一份完整 JSON 保留双语、旧无语言名称、独立 description 和全部启停点；新点缺失语言显示空，不由其他字段推测。 |
| AC19 | DAA 原 Point、PointFact 严格键集、comment 和上报 name 不被双语值污染；旧样本/manifest/队列/回执不重写，新配置 context、样本和现存上报链通过原合同，允许正常新 configRevision。 |
| AC20 | r5 与 DS-003 r4、DAA-017 r4 各自获精确批准及下游时序衔接明确批准后，JSON 开发无需等待两项基础最终验收；使用真实 DS 导出文件完成 DAA 导入及受控采集，验证双语和模拟 v2 不带显示名。双语原任务结果、JSON 独立 QA 和 Owner 最终决定分别记录，合成单测不得冒称跨应用闭环。 |
| AC21 | 新目录采集样本用模拟 v2 transport 核对中英文显示名不进入正文且程序名、值语义不变；DAA-018 原有验收与 qa_blocked 独立保留。 |

## 10. 边界、风险和待审事项

- 提前开发可能与尚未最终验收的双语候选修改相同模型或页面；按任务保存已存在改动，记录基础候选与最终组合候选，冲突时协调整合，在正式交付树对最终候选复核。基础 QA 若针对旧候选，不得自动当成新组合候选的通过证据。
- 此前原生隔离事件及 GUI/CUA/native 暂停历史继续记录；用户现已授权直接使用两应用各自 .local/dev。测试前核对实际进程、profile、实例和 loopback 目标，只新增可识别的测试对象，不按应用名重绑；无法确认目标或避免影响既有配置、设备和真实上报时停止。WebKit 或系统缓存并未因使用 .local/dev 得到完全隔离证明；不要求 VM、Windows 或完整系统层排查。

- 同一完整文件不等于物理 PLC 全部地址已被发现，也不证明设备实际布局。地址和可达目标必须用户核对；不含凭据或授予写权限的信息。
- 目录身份和生产运行身份不同。不同 origin 的 PLC 不自动归并；历史样本、回执、DB/UDT 归档和旧任务已批准状态保持。
- DAA 可选字段、目录来源分型及 DS 目录绑定均为设计候选，须以产品源码和隔离闭环验证；若需物理 DDL/旧 profile 迁移，另立 schema-maintenance 和采用 gate。
- 按 Human Owner 本轮要求，设计包含两端导入和导出；具体实施顺序仍在精确实施任务中决定。合成/本机验证不等于跨平台、现场、生产部署或长期运行验收。

Human Owner 已批准 r2、r3 和 r4 各自的设计范围，也已批准 DS-004 r2 和 DAA-018 r3 的独立实施范围。本次 r5 及两个 JSON r4 均已获精确范围批准；各自开发、独立 QA 和最终验收仍须真实完成。当前 PM 不创建 Development tasks 或 Verification checklist。

## 11. 修订、批准历史和 PM handoff

### r5 设计、实施及顺序调整批准记录

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 ARCH-PLC-001 r5、DS-003 r4 和 DAA-017 r4 及顺序调整，直接开始开发。使用各自的 .local/dev 完成 DS 导出、DAA 导入测试，测试后清理并更新手册。

本决定精确批准 ARCH-PLC-001 r5 设计范围、DS-003 r4 和 DAA-017 r4 实施范围及两基础任务原下游门槛的顺序衔接，并授权按各自规格使用 .local/dev 测试、清理本任务资源和更新手册。用户审阅、登记前完整草案 SHA-256：ARCH r5 为 b6fb01da81d63841f84d7e15215c09fc5e25fd24563436828609cf165471e40f；DS-003 r4 为 47278826db4c3e5e9ee65ed428236ca9bc957ffb0fb9193950af486215d12ec8；DAA-017 r4 为 efece638b647a04c82a9116df463d6cfe9a8d7d278cb0835b3c580e196ead966。两基础任务仍为 qa_blocked，本决定不是独立 QA 或最终验收，不授权真实设备、外部上报、物理 DDL、已有 profile 迁移、FF/CA 或发布。

2026-11-16（Asia/Shanghai）Human Owner 原话：“可以，批准 ARCH-PLC-001 r2 设计范围。接下来按 STD 拆分 DS 和 DAA 的实施任务，优先考虑 DS 导出、DAA 导入；FF 后续单独适配，暂不修改代码。”该决定仍是 r2 设计范围的真实批准，不是代码或最终验收批准。用户审阅、登记前 r2 原始 SHA256 为 `48d2415e9d6a6e41ff0996f8da1c64ca748067b28975be81382ae455c605987c`；登记批准后的完整 r2 写前 SHA256 为 `4928ac9697b6dc334d828d6f24596a6982798df4668111d3ab9a1d9fafc5d6b0`；其内部封存的 r1 原文 SHA256 为 `2b242fad628e2b67ca61f44c58f195485315a204e58fe1c497d3984656734de6`。

### r3 设计范围批准记录

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 ARCH-PLC-001 r3 设计范围。请按 STD 记录批准，暂不改代码。

该决定仅批准 `aiis-ics-arch::ARCH-PLC-001 r3` 设计范围；批准前完整草案 SHA256 为 `fe52bdf36335d2dc955920892194787884782a852209de3efd3d6ce74c88aee4`。此决定不批准最终验收、代码、测试、合同、数据库或设备实施；DS-004 r1、DAA-018 r1、DS-003 r2、DAA-017 r2 的实施规格仍为 draft，须各自获得 Human Owner 精确批准。DS-004 和 DAA-018 分别完成 STD 至 Human Owner 最终验收后，方可进入另经批准的 DS-003 / DAA-017 实施。

2026-11-17 依 Human Owner 新要求先形成 r3 草案；本轮未执行产品、数据库或设备操作。PM 将实际静态检查结果交给协调者；后续 Development 和 fresh-context Verification 各自记录真实证据。

### DAA 双语基础版本衔接

2026-11-17（Asia/Shanghai），Human Owner 在审阅问题中明确回复：“批准 DAA-018 r2 及版本衔接”。§8 的 P1 原文记录当时的 DAA-018 r1 计划：r1 实施范围虽获批准，Development 在改代码前因白名单缺少命名预览 DTO/服务而记录阻塞。当时由已批准的 `aiis-ics-arch::DAA-018 r2` 作为同一 DAA 双语基础任务的活动实施版本，r1 阻塞与批准历史保留；随后因 r2 验收冲突提出 r3，当时尚待批准。

后续导出/导入必须先满足 DAA-018 r2 自身 fresh-context 独立 QA 与 Human Owner 最终验收，以及 DS-004 自身 Human Owner 最终验收，并分别取得导出/导入实施批准；不能把未来 r2 的验收记为 r1 已验收。该版本衔接不更改 r3 的能力范围、原 P1/AC 文字或上报、导出/导入安全边界。


### r4 修订与批准 gate

2026-11-17（Asia/Shanghai），DAA-018 r2 Development 在合成测试中发现历史 v1 本地冻结正文包含完整上下文及双语 sentinel；该正例不代表真实外发。因 r3 §7.1.1 对历史构造的验收需实质修订，按 STD 先形成 ARCH r4 草案，并与 DAA-018 r3 一并提交 Human Owner 精确审批；r3 原设计批准、r1/r2 及任务阻塞历史均保留，任何 QA 或最终验收均未推断。r4 不影响 DS-004 r1 已获批准的独立实施，不批准后续导出/导入、真实 profile、DDL 或现场行为。

### r4 设计范围与版本衔接批准记录

2026-11-17（Asia/Shanghai），Human Owner 明确回复：

> 批准两份规格及版本衔接

该决定精确批准 `aiis-ics-arch::ARCH-PLC-001 r4` 的设计范围、`aiis-ics-arch::DAA-018 r3` 的实施范围及两者版本衔接。用户审阅的 ARCH r4 草案 SHA256 为 `e5b5cfa9cbfc0556aea79089c81af0d012f6213b75dc87e03af0669cd8ef6d90`，DAA-018 r3 草案 SHA256 为 `7f8761c47d04eb5a6162c58aaeb07d920fd68d2cda99cc654be73febede3005a`。DAA r3 和 DS-004 r1 仍分别需要 Development、fresh-context 独立验证及 Human Owner 最终验收；其完成前不得启动分别另批的导出/导入实施。此决定不批准真实 profile、DDL、现场设备、发布或最终验收。

### DS 双语基础版本衔接（后续 Owner 决定）

2026-11-17（Asia/Shanghai），Human Owner 明确回复：“批准 DS-004 r2 及版本衔接”。用户审阅的 `device-simulator::DS-004 r2` 草案 SHA256 为 `e4a7ac7e6feed1172955bce34875d8ed2a2364fc3246ad6959a288b12318832d`。§8 P1 和本规格先前提及的 DS-004 r1 记录当时计划及批准事实；r1 的 QA1–QA3 原失败记录保留。已获实施范围批准的 DS-004 r2 作为同一 DS 双语基础任务的活动实施版本，继续 Development、fresh-context Verification 和 Human Owner 最终验收；不能把历史 r1 写成已验收。

该衔接不改变 ARCH-PLC-001 r4 设计范围、原 P1/AC 或 DAA 实施边界。DS-004 r2 和 DAA-018 各自完成独立 STD 最终验收后，DS-003 / DAA-017 仍须各自获得精确实施批准；本决定不批准导出/导入、真实 profile、DDL、现场设备、发布或最终验收。

### 两项 JSON 实施任务的后续版本衔接

2026-11-17（Asia/Shanghai），Human Owner 对列明 DS-003 r5 和 DAA-017 r5 的批准请求明确回复：

> 批准两个 r5

该决定精确批准 DS-003 r5（同名文件安全拒绝而非覆盖）和 DAA-017 r5（增加目录点原命名预览所需服务文件及直接验收）。审阅前完整草案 SHA-256：DS-003 r5 为 2e2bfa448fcb59fcc3dbb6648df406f49f1dc735552a73beae1195b059b49734；DAA-017 r5 为 956b786d8b82a03404f80c5344a2894cfa7a622ab9347636c186a9bb0e69f0ba。§8 P2 的 r4 文字记录当时已批准的实施计划；现由同一任务各自已批准的 r5 接续。此衔接不修改 ARCH-PLC-001 r5 共同格式、范围或验收，原 r4 审批与历史保留；两项双语基础的 qa_blocked、独立 QA 和 Human Owner 最终验收状态不因本决定改变。各 JSON 任务仍须各自开发、fresh-context Verification 和最终验收。

## 附录 A：完整 r4 原文（含全部历史，非本草案）

写前 SHA-256：7b2c37a6aa37ffcd03403a435c106da5c3a9f81e12b3a2ffcab04f68ec3a11cc；围栏内保留原始 UTF-8 字节和末尾换行。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: ARCH-PLC-001
Revision: r4
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: ARCH-PLC-001 r4 设计范围及 DAA-018 r3 实施范围已获 Human Owner 精确批准；DS-004 r1 独立实施不受影响；两端基础各自完成 STD 最终验收后，方进入分别另批的导出/导入实施
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS 与 DAA 的逐 PLC S7 点位 JSON 双向交换详细设计
Owner: Automation World / Device Simulator 与 Data Acquisition Agent
Acceptance Chain Reference: 本任务遵循 Development Lifecycle Workflow；Human Owner 审阅精确设计 Revision，后续 Development、fresh-context Verification 和 Human Owner 最终验收各为独立 gate。
Related Task: device-simulator::DS-004 r1; aiis-ics-arch::DAA-018 r3; device-simulator::DS-003 r2; aiis-ics-arch::DAA-017 r2; device-simulator::DS-002; aiis-ics-arch::DAA-005; aiis-ics-arch::DAA-006; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013

# DS 与 DAA 点位双语显示及逐 PLC JSON 详细设计 r4

## 1. 本次请求、范围与状态

Human Owner 于 2026-11-17（Asia/Shanghai）明确要求：“按 STD 让 PM 修订规格：先统一 DS、DAA 点位中英文显示名，再做 DS 导出和 DAA 导入；显示名跟随顶栏语言切换，未设置留空，DAA 上报不带显示名，暂不改代码。”该设计形成 r3 并获 Human Owner 范围批准；随后因旧 v1 测试批次与实际 v2 外发验收边界需实质修订，形成 **r4**，Human Owner 已精确批准其设计范围。r4 不改变 DS-004 r1 已批准的实施，不授权最终验收、真实数据库、设备操作或导出/导入实施。

2026-11-16 Human Owner 批准了 **r2 设计范围**，该事实和当时范围不被撤销，也不自动批准 r3 或任何实施。r2 完整原始文件（含先前 r1 原文和批准登记）按字节封存在本文末附录，登记前审核摘要和 r1 摘要均保留；封存不是当前规则。先在两个独立基础任务各自完成 STD，包括独立 Verification 和 Human Owner 最终验收；再分别审批、实施 DS 导出和 DAA 导入。本文只修订 PM 规格，未改应用、配置、数据库、公开合同或索引，不创建 tasks/checklist。
## 2. 已核现状与设计目标

- DS 可配置多个实例、导入 DB/UDT，并区分草稿、保存版本、selected 和实际 loaded；DS 的点位 JSON 导入/导出仍是提案，不能声称已实现。[DS 使用手册](../../device-simulator/USER_GUIDE.zh-CN.md) · [DS-002 设计](../../device-simulator/plans/DS-002-multi-protocol-simulation-and-device-debugging/spec.md) · [DS 配置模型](../../device-simulator/runtime/src/domain/configuration.rs)
- DAA 现有来源导入入口为 .db/.udt；点位源、地址、分组、草稿和采集配置均有既有验证与持久化边界。[DAA 导入入口](../../data-acquisition-agent/src/app/plc/components/SourceImportPanel.vue) · [DAA 配置校验](../../data-acquisition-agent/src-tauri/src/domain/local_configuration.rs) · [DAA-005](../../data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md) · [DAA-006](../../data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/spec.md)
- DAA 配置、source_documents、runtime context、样本、上报与回执各有权威；现有相同正文的物理归档去重不能当作重写本地身份或历史的授权。[本地存储说明](../../data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md) · [存储 schema](../../data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs)
- DS 当前 Point 有 `display_name`，未标记语言，TIA 导入还会以源注释初始化它；DAA Point 有独立 `comment`，且 `PointFact.definition` 复制整个 Point，`facts_wire::definition_check` 对键严格闭合。两者不能推断已拥有带语言标记的名称或将注释当作双语名。
- 只读检索本仓产品源码及公开 contracts 未发现 `aiis.plc_points` 生产器、消费者或已发布公共合同；r2 是获批设计，不能证明仓外人工文件不存在。首批落地仍拟采用 schema_version 1，兼容 r2 文档的可选无语言 `display_name`，新增可选 `display_names`；若发现真实既有消费方/数据，则停止并回 PM 评估版本与迁移，不宣称旧解析器可读取新字段。
- FF 当前不能直接消费本候选完整 JSON，其后续适配另行处理。

设计覆盖 DS 和 DAA 各自按 PLC/实例导入、导出同一种完整 S7 点位 JSON，支持 BOOL、INT、REAL 等可表达类型和多 DB；多选时每台各生成一个文件，不因目标程序删除或另行生成子集。核心路径为 DS→DAA 无须再次提供 DB/UDT、DAA→DS 按显式模拟监听地址建立配置，以及 DAA→DAA 的按目标预览与导入。三条路径均是拟议功能，离线文件交换不要求源程序在线或共享 SQLite。

## 3. 文件边界与交互

- 一个 JSON 恰含一个逻辑 PLC、一个客户端连接描述、一个或多个 DB 和每个 DB 已声明点位。导出可多选实例，分别生成每台一个文件；不把多个 PLC 合并在同一 JSON。
- 文件携带完整已确认声明，包括停用点及其类型/地址；不包含实时值、凭据、环境文件、本机路径、DS 模拟初值/规则/写权限、DAA 采集组/周期/历史/上报数据。逻辑 source_path 可保留有事实的 TIA 路径，不代表文件系统路径。
- 导出针对所选持久配置预览完整信息，显式选择目录并处理重名；每份文件完整校验后原子落盘，失败不留下半文件。多选逐实例报告成功/失败/取消，不伪装全体成功。
- 导入选择文件与目标实例，预览连接、版本、点位和差异，确认后仅原子提交目标应用草稿；不自动激活、连接、启动、采集、上报或覆盖其他实例。预览和取消不写入配置或原文件。
- 两应用不共用 SQLite、可写目录或运行状态；导出文件只是快照，导入不构成现场地址、设备值、业务状态或写权限的证明。

## 4. 候选 JSON v1：单台 S7 PLC

本节是供 Human Owner 审阅的 DS/DAA 首次落地候选 v1，正式跨运行时合同发布需另项审批，本轮不修改根 contracts。r2 的 v1 是历史设计示意，不能当作已存在生产者/消费者或对旧生产文件的兼容证明。下例所有 ID、摘要、名称和端口均为合成示例，摘要仅展示词法。

~~~json
{
  "format": "aiis.plc_points",
  "schema_version": 1,
  "origin": {
    "kind": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "plc_id": "22222222-2222-4222-8222-222222222222"
  },
  "export": {
    "producer": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "config_state": "saved_revision",
    "revision_id": "33333333-3333-4333-8333-333333333333",
    "payload_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "exported_at": "2026-11-16T11:00:00+08:00"
  },
  "plc": {
    "name": "PLC_A",
    "protocol": "s7",
    "connection": {
      "host": "127.0.0.1",
      "port": 31281,
      "rack": 0,
      "slot": 1
    }
  },
  "dbs": [
    {
      "id": "44444444-4444-4444-8444-444444444444",
      "name": "MinimalImport",
      "number": 21,
      "size_bytes": 8,
      "source_enabled": true,
      "points": [
        {
          "id": "55555555-5555-4555-8555-555555555555",
          "name": "DB21_payload_ready_Bool",
          "display_name": "旧名称",
          "display_names": {
            "zh-CN": "就绪",
            "en-US": "Ready"
          },
          "description": "模拟设备就绪",
          "source_path": "payload.ready",
          "data_type": "BOOL",
          "byte_offset": 0,
          "bit": 0,
          "source_enabled": true
        },
        {
          "id": "66666666-6666-4666-8666-666666666666",
          "name": "DB21_payload_count_Int",
          "display_names": {
            "zh-CN": "计数",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.count",
          "data_type": "INT",
          "byte_offset": 2,
          "source_enabled": true
        },
        {
          "id": "77777777-7777-4777-8777-777777777777",
          "name": "DB21_payload_temperature_Real",
          "display_names": {
            "zh-CN": "",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.temperature",
          "data_type": "REAL",
          "byte_offset": 4,
          "source_enabled": true
        }
      ]
    }
  ]
}
~~~

### 4.1 字段与验证

1. 编码为 UTF-8 无 BOM；恰一顶层对象；拒绝重复 key、未知字段、非法 UTF-8、非整数词法用于整数、隐式转换和未明确允许的 null。必须是精确 format 和整数 schema_version 1；未知主版本拒绝，不猜兼容。文件上限 1 MiB，层级上限 16；单 PLC 最多 32 DB、4096 点，DB/点数量与文件大小都纳入导出预览。超预算整份文件失败，不静默截断。
2. origin 是 PLC 及其 DB/点身份的命名空间：kind 恰为 device_simulator 或 data_acquisition_agent，profile_id 为最初建立该命名空间的 DS 工作区 profile ID 或 DAA 本机实例 ID，plc_id 为该命名空间中的稳定 PLC 身份。它不表示每个点都是该应用创建，也不表示实际物理设备的作者或来源；export 单独记录本次实际导出者。三个字段均必填；ID 使用规范小写 UUID v4。文件名、显示名称、网络地址及 DAA 上报身份都不是 PLC 身份。导入后再从另一应用导出，保留 origin 和已映射的 DB/点身份；经本地显式新增的 DB/点可使用不冲突的本地 UUID v4 作为该命名空间下的新 ID，不改写既有 ID。若 ID 已冲突则阻断并经显式身份处理，不能在只读导出时悄悄换 ID。文件不声明逐点创建者，界面不得把 origin 当成所有点的创建者。
3. export.producer 是本次实际导出应用，v1 恰为 device_simulator 或 data_acquisition_agent；profile_id 是导出方自身的稳定 profile/instance 标识；exported_at 是真实生成时间，RFC 3339 且 +08:00。config_state 对 DS 是 saved_revision；对 DAA 是 active_revision 或 saved_draft。revision_id 对 DS/DAA 已保存版本为原版本 ID，对 DAA 草稿为导出时持久草稿 ETag；payload_sha256 是该应用实际选中保存内容的原始字节 SHA-256，小写 64 位十六进制。草稿 ETag 不冒充不可变 revision。导出者改变后的字段不伪称原程序导出。SHA 是完整性/追溯，不证明来源可信或物理设备正确。
4. plc.name 是非空显示名称，UTF-8 最多 100 字节；protocol 首期固定 s7。connection 为客户端目标：规范 IPv4 单播地址、port 1..65535、rack 0..7、slot 0..31。可选 local_tsap 与 remote_tsap 分别为客户端 calling/called，整数 1..65535；省略时 client local TSAP 为 0x0100，remote TSAP 为 0x0100 加 rack×32 加 slot。DS 监听地址及 TSAP 必须经客户端视角转换和用户确认；通配监听地址不能作为目标，loopback 只对同机有效。DAA 当前无自定义 TSAP 模型，遇非默认值应明确报不兼容并禁止导入执行，不可忽略。
5. dbs 必填且非空。每 DB id 是 UUID v4，number 为 1..65535 且同一 PLC 唯一，name 非空最多 100 UTF-8 字节，size_bytes 为 1..65536；points 必填且非空。DB ID、点 ID 在同一文件全局唯一，不能跨类别复用。每点 id 为 UUID v4，name 为同一 PLC 内唯一且稳定的 ASCII 程序引用名，最多 100 字节且须符合现有命名规则；显示名和语言切换不改变 name。可选 source_path、display_name、description 分别至多 512/256/500 UTF-8 字节；display_name 是无语言标记的原有单条值，须独立保留，不能归入双语任一字段。description 是独立的可选说明，最多 500 UTF-8 字节，非空时来自 DS 操作者显式编辑的独立描述或可核实的来源；不能用无语言 display_name 或双语名冒充注释。其他 producer 可以缺省该字段；缺省表示来源未提供，显式空串表示提供了空说明。
6. data_type 首期显式枚举 BOOL、BYTE、USINT、CHAR、INT、UINT、WORD、DINT、UDINT、DWORD、REAL 和 STRING[n]（n=1..254）。整数/REAL 按 S7 大端，REAL 为 IEEE 754 单精度，STRING 最大长度和编码须明确为 S7 STRING[n] 的 n 与 ASCII；CHAR 为单字节 ASCII。BOOL 必须有 bit=0..7，其他类型禁止 bit；字节宽按类型确定，STRING 占 n+2。必须满足 offset + 宽度不超过 DB 长度，同 DB 的物理占位不能重叠；不同 BOOL 可占同一字节的不同 bit。规则对禁用点也成立，不强推未获证明的 TIA 偏移或优化块布局。
7. source_enabled 只记录本次导出应用的启用事实，其解释依据 export.producer，而不是 origin.kind。DB 层的 source_enabled 是依导出者分型的可选布尔值：DS 导出时必填且如实取该 DB 的 enabled；DAA 当前的 DB 没有独立 enabled 事实，因此 DAA 导出必须省略该字段，不能从 PLC、采集组或点位状态推测。v1 消费者应验证此分型；DB 层缺失表示导出方没有提供此事实，不等于 true 或 false，显式 null 非法。点位层的 source_enabled 在 v1 对 DS 和 DAA 均为必填布尔值：分别取本次导出者的 Point.enabled；点层缺失或 null 为格式错误，不作 true/false 兜底。DS 点位启用与 DAA 的点位采集启用、分组语义不同。DS 文件经 DAA 导入并由 DAA 重新导出时，即使 origin.kind 仍为 device_simulator，也须按实际 export.producer=data_acquisition_agent 表达：DB 层省略，点位层为 DAA 本地实际 enabled；不能把旧 DS DB 启用状态冒称为 DAA 事实。
   这些字段既不是通用写权限，也不自动分配 DAA 采集组或改变 DS 模拟策略；消费者展示导出方、字段实际值或“未提供”，本地启用与引用由本地明确配置决定。点缺少地址、命名未确认、类型未知、物理重叠或不满足本合同：导出器列出具体问题并阻止该实例文件，不丢点、不把它标成默认地址、不因禁用而隐藏错误。首版不提供跳过点的导出模式。
8. 只输出本应用当前实例已经声明并确认的点，包括禁用点；不是对物理 PLC 全部地址的发现。无点的空洞不伪造成点。实际设备布局、源版本、访问许可及连接目标仍由使用者核对；模拟成功不证明真实 PLC 的布局或许可。
9. 可选观察信息和结构树不在 v1 必需合同。DS 可在导出预览显示实际 selected/loaded 事实，但不能据此伪造所选 saved revision。原始 DB/UDT 文件全文或模拟规则不进入该文件。未来如增加可选结构树，必须另定版本与消费者兼容，不能将当前点列表宣称为完整 TIA 源树。

10. 每点可选 `display_names`，存在时必须是严格对象且恰有 `zh-CN`、`en-US` 两个字符串，各最多 256 UTF-8 字节；字符串原样保留，不从 name、source_path、comment、另一语言或未标记单条值推测、复制或翻译。`""` 是该语言未设置，null、非字符串、缺一个键或未知键拒绝。缺少整个 `display_names` 表示来源未提供：新目标两种语言均为空，已有目标默认保留本地值；对象存在时两值含空串均为明确输入，重导差异按 §5 逐语言预览和确认。导出端总是输出两个键，空值明确为 `""`。旧 r2 示例缺字段时可按这一缺省语义处理，但这不是旧生产者已存在的证明。
11. 可选 `display_name` 保留历史无语言标记的单条值，允许空串且不得为 null；消费者展示时标“语言未标记”，不用于当前语言的双语列。导入原文件、后续目录绑定和未来导出保留其确切值；缺省不自动清空已有值。DAA 原有 `comment` 与此独立，不能借用或覆盖以保存它。任何 source_path 是点位逻辑路径，不是本机路径。

### 4.2 来源版本选择

DS：用户选择一个真实、不可变的 saved revision 及其一个或多个实例；每个文件取该 revision 中对应实例切片。界面同时显示每实例当前 selected 和 actual_loaded 的版本及缺失状态；如果所选 revision 与实际加载不同，突出差异并要求明确确认。不得将 latest、草稿或 selected 冒充 actual_loaded，也不混入未保存编辑或运行值。用户可选择与已验证 actual_loaded 相同的 saved revision；直接从各实例不同 loaded 版本逐个导出的专用模式是后续扩展。

DAA：用户明确选择 active_revision 或已保存的 saved_draft，显示实际标识、来源和活动版本差异；未保存界面编辑不能混入。active 与 runtime loaded/used 分别显示，有差异如实提示。导出并不激活草稿或更改活动版本。两应用导出同一 origin 时，producer、版本和摘要描述当前导出者真实事实。

## 5. 身份映射、重复导入及冲突

1. 可跨文件追溯的外部身份为 origin(kind, profile_id, plc_id) + db.id + point.id；本地身份是 DS/DAA 各自现有 UUID。首次导入新目标时若 ID 在目标 profile 全局可用，可保留；冲突则生成新本地 UUID 并建立持久外部→本地映射，预览清楚显示。用户选择映射到现有 PLC/DB/点时，必须预览并显式确认；不能仅因名称、IP、DB 号或相似地址自动认定为同一身份。
2. 后续来自同一 origin 的导入优先按既有映射识别，稳定保留本地 PLC/DB/点 ID、DAA 采集组、周期、上报配置、样本与历史引用。相同文件且本地映射和名称未变时再次导入无变化，原草稿 ETag 和版本保持；本地已编辑显示名时先按下述三方差异处理，不能冒称无变化。同外部身份改地址、类型、名称、启用事实或 DB 号均列明前后差异和影响，不能仅因 ID 相同当作无变化。相同 ID 对应不同来源/成员、未知重名、非法范围和物理冲突必须阻断并说明。
3. 文件缺少匹配目标 DB 中原来存在的任一点，或目标 DB 含文件未声明的手工/额外点，首期均作为点集冲突阻断该 PLC 整份导入并保持原草稿，不因其是否已有历史引用而放宽。界面列出具体差异；由使用者先在来源整理一致的目录，或另行申请多来源合并方案。不得在确认后留下无法满足目录点一一对应的配置，也不自动删除、停用、重绑或覆盖旧点。改 DB 号同样先阻断，未选实例和其他 DB 不变。外部地址变化涉及连接目标或物理效果时显式确认，不能改变历史样本的解释。
4. 持久映射必须随目标配置版本保存；预览绑定所选文件原字节 hash、目标、映射、当前 ETag 和有效期。确认时重验，过期、目标变更或并发编辑返回冲突，不产生部分配置、来源归档或半份映射。一个文件不覆盖另一应用的数据库文件。
5. DAA 本地 PLC ID、采集 generation/sequence、样本 ID，以及 HTTP 上报 instanceId/plcId/sourceGeneration 是不同事实；导入目录不创建或替换外部上报绑定、不改历史/队列/原始样本/回执。DAA 样本继续引用本地稳定 ID；外部与本地映射只用于追溯，不声称两个不同历史 ID 自动等价。
6. v1 的一个导出 PLC 只有一个 origin 命名空间；同一目标 PLC 已持久绑定另一外部 origin 时，禁止自动合并、覆盖或将两个 origin 伪装成一个。不同来源均要纳入同一 PLC 时须另立可追溯身份归并设计。此前从未建立外部身份的本地 PLC，可在逐点一一匹配并明确确认后绑定首次输入的 origin；原本地 ID 与历史仍保持。DS/DAA 未建立外部身份的原生 PLC 首次导出以自己的 profile 和本地 PLC ID 构造稳定命名空间。

7. 显示名逐语言做可追溯三方比较：来源基准为上次确认的原始目录及其 SHA，另外展示当前本地值和此次输入（含字段缺失或显式空串）；无前次来源的已有本地目标也必须展示当前值。输入与本地不同或本地自基准编辑后再导入时，用户逐语言选择保留本地或采用输入；缺失字段默认保留，显式空串若要清空已有值须确认。选择和相应基准同源绑定、草稿一起原子提交；只预览/取消无写入。同文件、来源基准未变且未选择改变的重导保持 ETag；若新文件 bytes/SHA 变化，即使保留本地值，来源归档或绑定基准变化也会正常改变草稿 ETag；用户明确选择恢复/清空同样产生正常草稿变化。无语言 `display_name` 另行按相同缺失/冲突规则处理，不能算作 zh-CN/en-US 的值。`description` 缺失表示不提供、不清空现有 DAA comment；提供非空时新点经确认写入 comment，已有 comment 差异须展示来源基准、现值和输入，由用户选择保留或采用；显式空串若将清空非空 comment 必须明确确认。原文件与历史版本不改写。description、comment 与所有显示名各自独立，不改变上报字段。并发编辑使预览失效，不允许静默覆盖。

## 6. DS 导出与导入设计

### 6.1 DS 导出

导出入口以实例列表为起点，可多选并选择同一 saved revision，预览所选实例的来源版本、实际 loaded、连接目标、每个 DB/点及问题。源自 DS 的 id、name、type、byte/bit、DB number/length、来源路径及双语值按所选版本实际事实映射；真实存在的旧 display_name 作为未标记语言的独立字段保留，不能自动当作 description 或任何语言的显示名。DS 导出器对每点输出 `description` 字符串：非空原样取所选版本由用户显式填写的独立描述，缺省/空输出 `""`；不从旧显示名或注释猜测。所有点含停用点均按合同验证；确认或地址缺失时给出 DB/点定位并阻止该实例。初值、规则、权限、在线值不进入交换合同。

用户提供或确认采集客户端可达的 client host/port；不能把 0.0.0.0 作为远端连接目标，跨机器不能把 127.0.0.1 误当远端地址。TSAP 显示服务端与客户端方向并按既有合同核对。文件的导出成功不证明目标已连接、模拟正在运行或点值正确。

### 6.2 DS 从目录导入

输入可为 DS 或 DAA 导出的同格式文件。用户选择新建或匹配现有 DS 实例，预览并确认映射、DB/点、已有策略及冲突；只写 DS 草稿，按 DS 原有版本保存、加载流程处理，不启动。该能力尚未实现，可作为独立实施切片，与 DS→DAA 路径分别验证。

交换合同保留未标记 `display_name` 至多 256 UTF-8 字节，但当前 DS 本地旧 `displayName` 校验至多 200 字节。后续 DS 导入遇 201–256 字节的值，必须先有另行批准且验证过的无损承载方案，否则明确阻断该文件；不能截断、替换、混入双语字段或声称未来往返已实现。

文件中的 connection 是 client 连接目标，尤其 DAA 导出的地址可能是真实 PLC：**不得把它自动作为 DS 本机监听地址，也不得连接该地址。** 用户必须显式填写并确认自己的模拟监听 IP/端口及 rack/slot；冲突时拒绝。新实例默认不启动；模拟初值、规则、客户端读取/写入许可分别由用户在 DS 确认，不从 DAA 采集启用状态推导。目录点的来源被明确标记为 catalog，缺少原 TIA 结构时不伪造 DB/UDT 文件或完整来源树；维护一致的本地/外部身份映射及 DS 自身布局/命名确认。现有实例的规则、初值、权限和历史版本默认保留，冲突先预览，不能覆盖无关对象。


DS 的目录导入实施还需形成明确的 catalog 来源分型：保存并哈希用户选中的原始 JSON；同一实例的多个 DB 可引用同一份源版本，各 DB 分别绑定 sourceVersionId、原字节 SHA、originDbId 以及外部点 ID → 本地点 ID 的映射。外部 origin 和映射随工作区草稿/版本持久保存；catalog 绑定与既有 TIA SourceBinding 分型明确且不相互冒充。验证时重验源版本、SHA、origin、DB/点身份、完整点集、类型与物理地址；缺失、重复、越界、点集冲突或来源不一致阻断，不能退回未校验的手工点路径。没有原 TIA 文件时不伪造 DB/UDT 来源、结构树或初始值；DS 自身的名称/地址签名及加载前确认仍须由用户完成。

导入目录后若在 DS 修改目录 DB 的点集或地址，须显式预览并确认，生成绑定前一来源 SHA 的不可变内部点集快照；该快照标识为 DS 本地生成，不冒充外部交换文件，也不包含当前配置自身的 revision/SHA，避免自引用。新草稿以新快照重新建立完整映射，其他 DB、原始输入和历史版本保留；新点使用不冲突 UUID、原点身份不变。重新导出仍是同一个候选交换格式，并如实记录 DS 作为本次 producer。

优先评估使用现有 source_versions 和可选配置元数据且保持原 DDL；新旧二进制、已保存版本/原 SHA、selected/loaded 与回退必须单独验证。若需要修改物理库结构或迁移已用 profile，停止对应实现并另立明确的 schema-maintenance 与采用审批。

### 6.3 两端显示名基础

DS 点配置增加可选 `displayNames`（含 `zh-CN`、`en-US` 两个字符串）和独立可选 `description`；原 `displayName` 保持原值和“语言未标记”语义。用户可为手工点和 TIA 点显式填写/编辑描述，缺省或空为未设置；既有单条显示名和 TIA 注释不自动填充，旧值和历史保持。DAA 不在 Point 加双语字段，而在 schema 1 配置顶层新增可省略 `pointDisplayNames`，以当前本地点 UUID 对应相同两键对象；目录导入以后还需可省略 `pointLegacyDisplayNames` 单独保存未标记单条值，不能放在 `comment` 或 PointFact 中。字段缺省在内存显示两种语言均为空；两值都为空时新保存配置可省略对应可选字段/映射项，任一非空则保存两键完整对象，不因读取旧草稿或旧版本产生写回。所有字符串均按 §4.1 字节上限验证，非法类型/null/多余键拒绝，不做隐式转换。

两端点位列表保留程序 `name`，另显示**唯一由顶栏当前语言**选取的显示名；当前语言为空时显示空白或明确未设置占位，不回退 name、另一语言、comment 或旧 displayName。编辑框可同时编辑两个语言值；切换顶栏语言只改变显示，不修改配置、ETag、版本或上报。旧单条值如展示须标明语言未标记，保持原样，操作者可手工填写双语值但不得自动复制。

DAA 的映射键必须是配置中唯一存在的本地点 UUID，不能跨 PLC/引用不存在点；对同一身份重导、改名、分组、地址更新保留映射。明确删除点/DB/PLC 时仅在对应草稿事务移除已删除点的映射，旧版本/样本不重写；点 ID 改变或重绑必须显式预览，不能悄悄将旧点名称附到新身份。新的显示名字段不进入 `Point`、`PointFact.definition`，也不合并进 name、comment、value 或上报的其他字段。

## 7. DAA 导入：无需再提供 DB/UDT

### 7.1 来源分型和完整性

DAA 现有配置的 Db.source_id 指向逻辑 SourceDocument，启用点还要匹配 Db.tree 中的叶及 type；SourceDocument 内容须与 SHA 一致。这是当前事实，不能只把目录点转成空树并关闭校验，也不能伪造 .db/.udt 内容、文件名或 TIA 源行。

拟议做法优先复用 DAA-005/006 的 **schema 1 可选字段、旧 DDL 不变**先例：

- 在配置 JSON 添加可选 catalog bindings，字段缺失表示原有 DB/UDT 或旧配置，读取旧 payload 不写回；按本地 DB ID 关联实际 catalog 逻辑 source ID、源原字节 SHA、外部 origin/DB ID 及外部点 ID → 本地点 ID 映射。保留原有 Point 的稳定身份和样本字段结构，避免把绑定元数据塞入每个 PointFact。
- 实际导入 JSON 作为明确的 catalog SourceDocument，保存用户所选原始 UTF-8 内容及 SHA。一个 PLC 导入的一份文件建立一个逻辑 source；该 PLC 多个 DB 的 source_id 可以共同指向此 source，由每个 DB 的 catalog binding 精确标识文件中的对应 DB。不同 PLC 的逻辑 source 各自独立；同 SHA、同字节的物理归档按现有策略复用，不覆盖旧归档。共享单一逻辑 source 避免每 DB 重复一份大 JSON 而突破配置容量。source_id 始终指向真实目录源，而非伪造 TIA 源。
- 对有 catalog binding 的 DB 执行目录专用完整性验证：解析并重验文件版本、原字节 SHA、origin、DB/点 ID、名称、类型、地址及占位；本地映射必须一一对应，不允许缺失、重复、跨 PLC、改写绑定或引用文件未声明的点。当前 DB 关联源校验中对 db_number/原 importBinding 的要求，在 catalog 分支以完整的目录 DB 关联校验替代；旧来源分支的原逻辑不变。source_path 如文件没有该事实则保持缺失语义，不伪装为 TIA 路径；目录点可在本地视图展示有事实的来源路径和单独的目录身份。
- catalog 的完整性表示“已完整验证该 JSON 声明的点集”，不表示已验证 TIA 工程完整树。目录分支可将 Db.complete 用作目录完整性准入，Db.tree 可以为空；UI 明示来源是目录点列表，不生成假树或声称可恢复原源文件。对原 DB/UDT 来源，原 Db.tree、leaf_matches、source/UDT 闭包和地址校验完全保留；只在显式 catalog 分型下使用等强度的目录成员核对。
- 导入确认后地址及确认依据明确记录为目录来源与用户确认；若现有 origin 枚举无法如实表达，需在后续受批实现中增加清晰的 catalog 类型并核对样本定义和上报兼容，不能谎写为 TIA 自动推算。对后续手工改地址/类型，必须要求明确的本地覆盖确认，保留原目录和修改前值；激活校验对照原目录加明确覆盖，而不是绕开校验。覆盖及其重新导出语义须在实施切片冻结并有负例。
- 只新增可选配置元数据并不能自动证明兼容：现有 serde deny_unknown_fields 的旧二进制可能拒绝新 payload。必须验证新版本零写读取旧草稿/版本/样本、原字节/hash 不变；旧版本碰到新 catalog 元数据须安全拒绝，不得静默启动错误配置或生成空库。降级前停止自有采集并保留完整 profile；只在证明兼容的副本或原备份上回退，禁止覆盖真实历史。
- 当前 configuration_revisions 和 configuration_contexts 的物理 schema 对配置 payload schema_version 均有 CHECK=1。若验证证明上述 v1 可选字段方案不能满足完整性、性能或兼容性，则停止该实现切片，提出独立的 schema-maintenance Revision，明确双库兼容、升级前备份、中断恢复、旧记录不重写、回退和真实 profile 采用审批；不得把 schema 2 或 DDL 当成本设计已授权的自动迁移。

拟议的 DAA 配置 JSON 扩展是可省略的 catalogBindings 列表。每项包含 localDbId、sourceId、sourceSha256、sourceKind、originDbId 和 pointMappings；每个 pointMapping 包含 localPointId、catalogPointId，可选 localOverride。sourceKind 明确区分外部 exchange_json 和下文的 local_snapshot，按对应封闭格式分别校验。其所属本地 PLC 从 localDbId 关联到本地 DB 后核对，不信任输入另填的 PLC。逐语言显示名及无语言单条值保留于本地配置级映射，字段的存在性、最后确认来源 SHA、逐语言冲突选择须与目录绑定及草稿一同保存，不写入 Point。sourceId 必须属于同一 PLC，sourceSha256 必须等于该 SourceDocument 原字节摘要，originDbId 必须在相应外部文件或内部快照中唯一存在；所有 localPointId/catalogPointId 在本映射中分别唯一，且两侧点集必须完整一一对应。两个 DB 不得引用同一 originDbId；同一外部文件的一次导入在一个本地 PLC 只使用同一逻辑 sourceId，跨 PLC 则分别持有逻辑来源。

localOverride 仅用于使用者在 DAA 显式修改目录点的地址或类型：含该次确认所依据的 sourceSha256、修改后的 dataType/offset/可选 bit、用户确认原因。无 override 时本地点的类型/地址必须与归档 JSON 一致；有 override 时必须匹配已确认覆盖，且重新执行类型、DB 长度、bit 和跨点重叠校验。源文件重新导入后若原点类型/地址与覆盖基准发生变化，预览列出冲突并暂停该点更新，由用户明确保留覆盖或采用新值；不得悄悄以旧覆盖套用新源。DAA 导出采用所选已保存配置中的实际有效点位，保留 origin 和点 ID，并以本次 DAA 配置 revision/SHA 如实标明新的 exporter 来源，不把覆盖值谎称来自旧原始文件。名称、显示信息和分组的变更仍分别走既有命名及草稿保护。

在已导入 catalog 的 DB 里新增本地点时，不得仅修改 pointMappings 而继续指向不含该点的旧文件。拟提供明确的本地目录修订操作：在预览确认后基于当前已验证目录、有效覆盖和新点生成该 DB 的不可变内部点集快照，格式标记为 daa.catalog_snapshot，含 origin、originDbId、原 source SHA 和完整点集，单独算 SHA 并归档；新草稿内该 DB binding 指向此快照且重新建立完整一一对应。该快照是 DAA 生成的内部来源材料，不冒充原 DS 文件或 DB/UDT，不携带当前配置自身的 revision/SHA，因此不产生配置与自身摘要的循环引用。其他 DB 可以继续指向原交换文件；更新源、绑定及草稿在同一事务提交。追加点沿用原命名空间但不声称由 DS 创建；用不冲突的本地 UUID v4 作外部点 ID，既有映射不变。导出时才从所选已保存 DAA 配置生成统一交换 JSON，并正确填写 DAA 的实际版本/SHA。内部快照不作为跨应用合同公开，也不覆盖先前原始文件或历史 revision。

为支持无需 DB/UDT 导入的有效地址，目录导入经用户预览确认后，Address.confirmed 才为 true，拟议新增 origin 值 catalog 和明确的确认原因；手工覆盖仍保留独立的手工来源。此值只能用于具备有效 catalog binding 的点。因 PointFact 包含 Address 定义，新值会出现于后续新样本的本地定义中：实施时必须验证 DAA 原有历史解码及事实 v2 上报契约兼容，保留所有既有样本字节和已冻结上报内容；若外部合同不接受该值，返回 PM 另定范围。读取和解析目录本身不构成对真实 PLC 布局的验证。保存前还要核算单个源、完整配置 JSON、归档和容量预算；超限时明确拒绝且无部分写入，不能因为单文件小于 1 MiB 就假定目标配置一定可容纳。

### 7.1.1 事实和上报的双语边界（r4）

当前采集器直接 `point.clone()` 形成 `PointFact.definition`，`facts_wire::definition_check` 拒绝定义中的未知键。本设计仍将双语显示名放在配置顶层映射，不改变 Point 和严格校验；产品实际可达的所有外发正文均不得包含新增中英文显示名，也不得将其混入 name/value/comment 或其他字段。v2 Point 的 `name` 按原值上报，v2 正文原本没有 comment；本地 comment 与显示名保持独立，不修改后端或公共合同。

Development 的受控合成测试复现：历史 v1 测试构造链 `commit_cycle → build_delivery_cycle → freeze_cycle` 的 `Cycle.contextUtf8` 包含完整配置原文，所以本地冻结正文可包含双语 sentinel；这不是实际网络外发。只读源码显示，旧 v1 新建/冻结/选取及旧 `Transport::post` 在 `cfg(test)` 下，普通产品通过 runtime4 的 `next_sample_upload_ready` / `post_sample` 发送 v2，runtime3 的上报 start/resume 拒绝。生产代码仍可用 `facts_wire::build_cycle` / `schema.rs` 对旧账本做本地重构和完整性校验；不得误称该校验为 test-only 或删除。

保留 v1 原合同、完整 context、原摘要及旧冻结正文：test-only 合成构造应如实验证正文可能包含两个显示名，记录未外发，不能冒称 v1 零泄露通过。不得启用或暴露旧 v1 产品发送；未来重新启用须另立设计解决显示名外发、原文/摘要及历史兼容并独立批准。禁止裁剪上下文、重算旧摘要或改写原有冻结/排队记录和回执。

对产品实际可达的 v2 外发逐路径使用不同的中文、英文 sentinel 核验：新采样、已有 v2 冻结和重试，以及 `legacy_status` 判定从未发送的旧样本按原规则生成的新 v2 正文；不符合旧样本准入的状态继续复核或阻断。使用受控假 transport 截获正文且不发真实 POST，证明显示名不进入任何外发字段，原始 name/value 与既有字段存在/缺失语义不变；runtime3 禁止启动旧发送、产品特性/入口构建和源码闭包须验证。若发现产品可达旧 v1 发送或 v2 正文泄露显示名则阻断并回 PM。

测试还须对照旧样本、manifest、上下文、冻结正文、ACK 和历史 bytes/SHA；旧记录不重写，新的 configRevision、采样时间及摘要可正常变化。此边界是对 r3 §7.1.1 和 DAA-018 r2 DA18-06 的**实质验收修订**，Human Owner 已精确批准 ARCH r4 和 DAA-018 r3；仍须完成 Development、独立验证和最终验收，不将旧验收记为通过。DS-004 r1 已批准实施独立继续，不能据此实施导出/导入。

### 7.2 DAA 导入体验与采集准入

选择文件后，新建 PLC 或选择现有 PLC，预览同一文件的连接、DB、所有点、来源、变更、不可支持项及映射。导入确认可复用文件中已确认地址，但仍须本地明确用户确认；目标真实 PLC 地址需现场资料核对。首次新建的点默认不自动开始采集。用户可以在导入预览中选择现有采集组，或显式新建组并填写周期，一次批量分配选中的受支持点；同 PLC/DB 的启用点遵守现有 DAA runtime 分组规则、资源预算与数量上限。未选择的点保留并显示为未分组/停用。

确认仅提交到草稿；用户可随后显式激活配置、连接并采集。端到端验收必须证明：**文件和 DAA 新空隔离 profile 足够，不额外提供或重新导入 .db/.udt**；由 DS 受控模拟器提供 BOOL、INT、REAL 可读值，DAA 一次分组后保存、激活、真实读取并核对采样点 ID、地址、类型、值和质量。失败有具体原因；不能以解析 JSON 或纯内存单测代替此闭环。旧配置和运行任务按原路径工作。

### 7.3 DAA 导出

按 PLC 多选、每台一文件，从用户选择的 saved_draft 或 active_revision 生成上述共同合同；仅导出该配置中已声明且可通过合同完整性检查的 DB/点。未确认地址或类型问题必须逐点报告并阻止该实例，不能用停用状态掩盖。重导本地由目录输入的配置时保留外部 origin 和稳定 ID 映射，并如实记录 DAA 作为导出者及选定配置版本；未绑定外部命名空间的 DAA 自建 PLC 以自身 profile/PLC 建立稳定身份，已绑定 origin 下新增点沿用该命名空间但不冒称来源。DAA 的 DB 没有独立启用字段，导出时省略该层 source_enabled；每个点的 source_enabled 必须取当前 DAA 配置中的 Point.enabled，即使来源命名空间是 DS 也不能沿用源文件的旧启用值。采集组、周期、运行历史、队列、上报设置及凭据不进入 JSON。



## 8. 拟议实施次序与任务归属

| 阶段 | 拟议范围 | 进入和退出边界 |
| --- | --- | --- |
| P0 | ARCH-PLC-001 r4 双语与同一完整 JSON 设计 | Human Owner 已精确批准 r4 设计范围；r2/r3 原批准保留历史效力。 |
| P1 | `device-simulator::DS-004 r1` 和 `aiis-ics-arch::DAA-018 r3` 各自实现本地双语点位 | 各自精确批准并独立 Development、fresh-context Verification 和 Human Owner 最终验收；可并行，但两项都完成才能进入 P2。 |
| P2 | `device-simulator::DS-003 r2` 导出 + `aiis-ics-arch::DAA-017 r2` 导入 | 两项基础均完成 STD 后，各自仍需精确实施批准；同一 DS 实际导出文件交 DAA 使用，验证无原 DB/UDT 的受控采集。 |
| P3 | DAA 导出及 DAA→DAA；DS 导入及 DAA→DS | 后续各立范围；DS 明确模拟监听地址，不自动启动。 |
| 后续 | 正式跨运行时合同、FF/CA、其他协议和现场采用 | 分别立项批准；本轮不修改 contracts、FF 或 CA。 |

两个应用的基础任务和导入/导出任务各有独立 owner 与验收链，不继承不同模块的实施批准。合成 JSON 验证不能冒称 DS 实际导出→DAA 导入→采集闭环。受批 Development 按触达面使用 aiis、plc-point-mapping、rust-runtime、desktop-tauri、frontend-ui、i18n-workflow 和 code-document-indexer；如需物理 schema 则另走维护 gate。

## 9. 验收标准（待执行）

下列为未来经批准的软件范围设计口径，不是已完成证据；各切片确定精确 AC 和真实验证环境。

| 编号 | 可观察标准 |
| --- | --- |
| AC01 | 一台 PLC 一份完整 JSON；多选两台分别生成，实例、DB、点不串；取消、冲突和部分失败正确报告且无半文件。 |
| AC02 | 候选示例及多 DB 正例按冻结的格式验证；重复键、未知版本/字段、非法编码/类型/UUID、超限、缺字段、BOOL bit、STRING 宽度、越界与重叠有可复现负例。 |
| AC03 | DS saved/selected/actual_loaded 与 DAA saved_draft/active/loaded/used 各自准确呈现；实际版本和原 payload SHA 如实追溯，不混未保存编辑。 |
| AC04 | DS 包含 BOOL、INT、REAL、STRING 及停用点时导出完整声明；地址或名称未确认、未知类型、结构错误均定位并阻断该实例，无默认值和静默漏点。 |
| AC05 | DS JSON 导入全新隔离 DAA profile 无须 .db/.udt；显式分组、保存和激活后，以隔离 DS S7 模拟完成 BOOL/INT/REAL 真实读取，核对 ID、地址、类型、值与质量。 |
| AC06 | DAA 目录来源原字节/SHA、source_id、DB 和点位映射完整一致；伪造源、错 hash、错成员/类型/地址和重复绑定拒绝；旧 DB/UDT 的 tree/leaf_matches 验证不减弱。 |
| AC07 | DAA→DAA 使用同一完整文件，在新目标预览和确认，保留身份来源、完整点集；分组和周期由目标用户选择，确认前不修改草稿或连接设备。 |
| AC08 | DAA 按实例支持 saved_draft/active_revision 导出，多选分别生成；来源为 DS 时仍以 DAA 作为实际 producer，DB 层无 source_enabled，点位层取 DAA 实际 Point.enabled。 |
| AC09 | DS DB/点启用分别取 DS 实际值；DAA DB 层缺失表示未提供，不能默认 true/false；两应用的点位 source_enabled 必填，缺失、null 和与 producer 不相容的字段拒绝。 |
| AC10 | DAA 导出文件导入 DS 时不得复用文件中的客户端目标作为模拟监听；操作者显式确认新的本机监听地址，之后按 DS 版本流程配置，导入本身不启动或连接。 |
| AC11 | 对已有目标，无本地变更且无冲突的重复导入保持 ETag 与本地 ID；显示名本地编辑后按三方差异显式选择，缺点、额外点、跨 origin、ID 冲突或变更地址等均按规定阻断或确认；整 PLC 提交原子。 |
| AC12 | 采集组、周期、DS 规则与历史版本、DAA 既有本地 ID、样本、generation/sequence、上报绑定、pending/ACK 及未选实例不被静默覆盖或改写。 |
| AC13 | 已导入目录的 DS 或 DAA 本地点集变更产生对应应用的可核验内部快照和稳定映射，外部原文件及历史 revision 原字节保留；来源变化、地址修改与手工覆盖冲突先预览。 |
| AC14 | 新版本读取旧 payload 零写回；旧二进制遇新目录元数据不会静默运行错误配置；任何必须的物理 DDL、迁移和真实 profile 采用先取得独立批准并验证中断/回退。 |
| AC15 | wildcard、loopback、非默认 TSAP、取消/并发、路径、文件替换和多个实例有可观察负例；模拟结果不外推真实 PLC。 |
| AC16 | 两端原有启动、草稿、版本和权限行为保持；新增可见文案双语对称，表格列宽遵循公共规则；项目测试、原生/跨平台/现场证据如实分层。 |
| AC17 | 两端点表当前语言分别显示精确双语值；一侧空、一侧非空、两侧空和顶栏切换均可验证，切语言不写配置/ETag；旧 displayName 明示无语言且不混入两语言。 |
| AC18 | 单个完整 JSON 同时保留两语言、旧无语言单条值、可选真实 description 及全部启停点；缺失 display_names、显式空串、错误类型/未知键、重导三方差异和本地编辑冲突均有明确可测结果。 |
| AC19 | DAA 原 Point、PointFact 严格键集、comment 和上报 name 不被双语值污染；旧样本/manifest/队列/回执不重写，新配置 context、样本和现存上报链通过原合同，允许正常新 configRevision。 |
| AC20 | 两基础任务各自完成 STD 最终验收后才开始 DS-003/DAA-017 实施；真实 DS 导出文件用于 DAA 隔离端到端，禁止以合成单测替代。 |
| AC21 | 产品所有实际可达的 v2 外发包括新采样、既有冻结/重试、符合 legacy_status 从未发送条件的旧样本转 v2，双语 sentinel 不进入正文；旧 v1 test-only 本地构造按原合同可含 sentinel，明确未外发，生产旧账本重构及原文/摘要完整性保持。旧发送入口若在产品可达则阻断。 |

## 10. 边界、风险和待审事项

- 同一完整文件不等于物理 PLC 全部地址已被发现，也不证明设备实际布局。地址和可达目标必须用户核对；不含凭据或授予写权限的信息。
- 目录身份和生产运行身份不同。不同 origin 的 PLC 不自动归并；历史样本、回执、DB/UDT 归档和旧任务已批准状态保持。
- DAA 可选字段、目录来源分型及 DS 目录绑定均为设计候选，须以产品源码和隔离闭环验证；若需物理 DDL/旧 profile 迁移，另立 schema-maintenance 和采用 gate。
- 按 Human Owner 本轮要求，设计包含两端导入和导出；具体实施顺序仍在精确实施任务中决定。合成/本机验证不等于跨平台、现场、生产部署或长期运行验收。

Human Owner 已批准 r2、r3 和 r4 各自的设计范围，也已批准 DAA-018 r3 实施范围及版本衔接；DS-004 r1 已获的独立实施批准保持。后续导出/导入实施仍须各自精确批准，独立验证和最终验收仍待完成。当前 PM 不创建 Development tasks 或 Verification checklist。

## 11. 修订、批准历史和 PM handoff

2026-11-16（Asia/Shanghai）Human Owner 原话：“可以，批准 ARCH-PLC-001 r2 设计范围。接下来按 STD 拆分 DS 和 DAA 的实施任务，优先考虑 DS 导出、DAA 导入；FF 后续单独适配，暂不修改代码。”该决定仍是 r2 设计范围的真实批准，不是代码或最终验收批准。用户审阅、登记前 r2 原始 SHA256 为 `48d2415e9d6a6e41ff0996f8da1c64ca748067b28975be81382ae455c605987c`；登记批准后的完整 r2 写前 SHA256 为 `4928ac9697b6dc334d828d6f24596a6982798df4668111d3ab9a1d9fafc5d6b0`；其内部封存的 r1 原文 SHA256 为 `2b242fad628e2b67ca61f44c58f195485315a204e58fe1c497d3984656734de6`。

### r3 设计范围批准记录

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 ARCH-PLC-001 r3 设计范围。请按 STD 记录批准，暂不改代码。

该决定仅批准 `aiis-ics-arch::ARCH-PLC-001 r3` 设计范围；批准前完整草案 SHA256 为 `fe52bdf36335d2dc955920892194787884782a852209de3efd3d6ce74c88aee4`。此决定不批准最终验收、代码、测试、合同、数据库或设备实施；DS-004 r1、DAA-018 r1、DS-003 r2、DAA-017 r2 的实施规格仍为 draft，须各自获得 Human Owner 精确批准。DS-004 和 DAA-018 分别完成 STD 至 Human Owner 最终验收后，方可进入另经批准的 DS-003 / DAA-017 实施。

2026-11-17 依 Human Owner 新要求先形成 r3 草案；本轮未执行产品、数据库或设备操作。PM 将实际静态检查结果交给协调者；后续 Development 和 fresh-context Verification 各自记录真实证据。

### DAA 双语基础版本衔接

2026-11-17（Asia/Shanghai），Human Owner 在审阅问题中明确回复：“批准 DAA-018 r2 及版本衔接”。§8 的 P1 原文记录当时的 DAA-018 r1 计划：r1 实施范围虽获批准，Development 在改代码前因白名单缺少命名预览 DTO/服务而记录阻塞。当时由已批准的 `aiis-ics-arch::DAA-018 r2` 作为同一 DAA 双语基础任务的活动实施版本，r1 阻塞与批准历史保留；随后因 r2 验收冲突提出 r3，当时尚待批准。

后续导出/导入必须先满足 DAA-018 r2 自身 fresh-context 独立 QA 与 Human Owner 最终验收，以及 DS-004 自身 Human Owner 最终验收，并分别取得导出/导入实施批准；不能把未来 r2 的验收记为 r1 已验收。该版本衔接不更改 r3 的能力范围、原 P1/AC 文字或上报、导出/导入安全边界。


### r4 修订与批准 gate

2026-11-17（Asia/Shanghai），DAA-018 r2 Development 在合成测试中发现历史 v1 本地冻结正文包含完整上下文及双语 sentinel；该正例不代表真实外发。因 r3 §7.1.1 对历史构造的验收需实质修订，按 STD 先形成 ARCH r4 草案，并与 DAA-018 r3 一并提交 Human Owner 精确审批；r3 原设计批准、r1/r2 及任务阻塞历史均保留，任何 QA 或最终验收均未推断。r4 不影响 DS-004 r1 已获批准的独立实施，不批准后续导出/导入、真实 profile、DDL 或现场行为。

### r4 设计范围与版本衔接批准记录

2026-11-17（Asia/Shanghai），Human Owner 明确回复：

> 批准两份规格及版本衔接

该决定精确批准 `aiis-ics-arch::ARCH-PLC-001 r4` 的设计范围、`aiis-ics-arch::DAA-018 r3` 的实施范围及两者版本衔接。用户审阅的 ARCH r4 草案 SHA256 为 `e5b5cfa9cbfc0556aea79089c81af0d012f6213b75dc87e03af0669cd8ef6d90`，DAA-018 r3 草案 SHA256 为 `7f8761c47d04eb5a6162c58aaeb07d920fd68d2cda99cc654be73febede3005a`。DAA r3 和 DS-004 r1 仍分别需要 Development、fresh-context 独立验证及 Human Owner 最终验收；其完成前不得启动分别另批的导出/导入实施。此决定不批准真实 profile、DDL、现场设备、发布或最终验收。

### DS 双语基础版本衔接（后续 Owner 决定）

2026-11-17（Asia/Shanghai），Human Owner 明确回复：“批准 DS-004 r2 及版本衔接”。用户审阅的 `device-simulator::DS-004 r2` 草案 SHA256 为 `e4a7ac7e6feed1172955bce34875d8ed2a2364fc3246ad6959a288b12318832d`。§8 P1 和本规格先前提及的 DS-004 r1 记录当时计划及批准事实；r1 的 QA1–QA3 原失败记录保留。已获实施范围批准的 DS-004 r2 作为同一 DS 双语基础任务的活动实施版本，继续 Development、fresh-context Verification 和 Human Owner 最终验收；不能把历史 r1 写成已验收。

该衔接不改变 ARCH-PLC-001 r4 设计范围、原 P1/AC 或 DAA 实施边界。DS-004 r2 和 DAA-018 各自完成独立 STD 最终验收后，DS-003 / DAA-017 仍须各自获得精确实施批准；本决定不批准导出/导入、真实 profile、DDL、现场设备、发布或最终验收。

## 附录 A：已批准 r3 完整原文（含 r2/r1 历史）

写前完整 r3 SHA256：`b4cf0636e0d5a0f7b2b090712e4c457b154474ce1631fde876156b60b61234f4`。下方围栏内是完整原始 UTF-8 字节及原末尾换行，含原批准、版本衔接与嵌套 r2/r1 原文；历史批准不自动延伸至 r4。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: ARCH-PLC-001
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: r3 设计范围已获 Human Owner 批准；双语基础 DS-004 / DAA-018 待各自精确批准并完成 STD 最终验收后，方进入各自另批的 DS-003 / DAA-017 实施
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS 与 DAA 的逐 PLC S7 点位 JSON 双向交换详细设计
Owner: Automation World / Device Simulator 与 Data Acquisition Agent
Acceptance Chain Reference: 本任务遵循 Development Lifecycle Workflow；Human Owner 审阅精确设计 Revision，后续 Development、fresh-context Verification 和 Human Owner 最终验收各为独立 gate。
Related Task: device-simulator::DS-004 r1; aiis-ics-arch::DAA-018 r1; device-simulator::DS-003 r2; aiis-ics-arch::DAA-017 r2; device-simulator::DS-002; aiis-ics-arch::DAA-005; aiis-ics-arch::DAA-006; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013

# DS 与 DAA 点位双语显示及逐 PLC JSON 详细设计 r3

## 1. 本次请求、范围与状态

Human Owner 于 2026-11-17（Asia/Shanghai）明确要求：“按 STD 让 PM 修订规格：先统一 DS、DAA 点位中英文显示名，再做 DS 导出和 DAA 导入；显示名跟随顶栏语言切换，未设置留空，DAA 上报不带显示名，暂不改代码。”本次实质变更形成 **r3**；Human Owner 已批准其设计范围，不批准代码、最终验收、真实数据库或设备操作。

2026-11-16 Human Owner 批准了 **r2 设计范围**，该事实和当时范围不被撤销，也不自动批准 r3 或任何实施。r2 完整原始文件（含先前 r1 原文和批准登记）按字节封存在本文末附录，登记前审核摘要和 r1 摘要均保留；封存不是当前规则。先在两个独立基础任务各自完成 STD，包括独立 Verification 和 Human Owner 最终验收；再分别审批、实施 DS 导出和 DAA 导入。本文只修订 PM 规格，未改应用、配置、数据库、公开合同或索引，不创建 tasks/checklist。
## 2. 已核现状与设计目标

- DS 可配置多个实例、导入 DB/UDT，并区分草稿、保存版本、selected 和实际 loaded；DS 的点位 JSON 导入/导出仍是提案，不能声称已实现。[DS 使用手册](../../device-simulator/USER_GUIDE.zh-CN.md) · [DS-002 设计](../../device-simulator/plans/DS-002-multi-protocol-simulation-and-device-debugging/spec.md) · [DS 配置模型](../../device-simulator/runtime/src/domain/configuration.rs)
- DAA 现有来源导入入口为 .db/.udt；点位源、地址、分组、草稿和采集配置均有既有验证与持久化边界。[DAA 导入入口](../../data-acquisition-agent/src/app/plc/components/SourceImportPanel.vue) · [DAA 配置校验](../../data-acquisition-agent/src-tauri/src/domain/local_configuration.rs) · [DAA-005](../../data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md) · [DAA-006](../../data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/spec.md)
- DAA 配置、source_documents、runtime context、样本、上报与回执各有权威；现有相同正文的物理归档去重不能当作重写本地身份或历史的授权。[本地存储说明](../../data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md) · [存储 schema](../../data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs)
- DS 当前 Point 有 `display_name`，未标记语言，TIA 导入还会以源注释初始化它；DAA Point 有独立 `comment`，且 `PointFact.definition` 复制整个 Point，`facts_wire::definition_check` 对键严格闭合。两者不能推断已拥有带语言标记的名称或将注释当作双语名。
- 只读检索本仓产品源码及公开 contracts 未发现 `aiis.plc_points` 生产器、消费者或已发布公共合同；r2 是获批设计，不能证明仓外人工文件不存在。首批落地仍拟采用 schema_version 1，兼容 r2 文档的可选无语言 `display_name`，新增可选 `display_names`；若发现真实既有消费方/数据，则停止并回 PM 评估版本与迁移，不宣称旧解析器可读取新字段。
- FF 当前不能直接消费本候选完整 JSON，其后续适配另行处理。

设计覆盖 DS 和 DAA 各自按 PLC/实例导入、导出同一种完整 S7 点位 JSON，支持 BOOL、INT、REAL 等可表达类型和多 DB；多选时每台各生成一个文件，不因目标程序删除或另行生成子集。核心路径为 DS→DAA 无须再次提供 DB/UDT、DAA→DS 按显式模拟监听地址建立配置，以及 DAA→DAA 的按目标预览与导入。三条路径均是拟议功能，离线文件交换不要求源程序在线或共享 SQLite。

## 3. 文件边界与交互

- 一个 JSON 恰含一个逻辑 PLC、一个客户端连接描述、一个或多个 DB 和每个 DB 已声明点位。导出可多选实例，分别生成每台一个文件；不把多个 PLC 合并在同一 JSON。
- 文件携带完整已确认声明，包括停用点及其类型/地址；不包含实时值、凭据、环境文件、本机路径、DS 模拟初值/规则/写权限、DAA 采集组/周期/历史/上报数据。逻辑 source_path 可保留有事实的 TIA 路径，不代表文件系统路径。
- 导出针对所选持久配置预览完整信息，显式选择目录并处理重名；每份文件完整校验后原子落盘，失败不留下半文件。多选逐实例报告成功/失败/取消，不伪装全体成功。
- 导入选择文件与目标实例，预览连接、版本、点位和差异，确认后仅原子提交目标应用草稿；不自动激活、连接、启动、采集、上报或覆盖其他实例。预览和取消不写入配置或原文件。
- 两应用不共用 SQLite、可写目录或运行状态；导出文件只是快照，导入不构成现场地址、设备值、业务状态或写权限的证明。

## 4. 候选 JSON v1：单台 S7 PLC

本节是供 Human Owner 审阅的 DS/DAA 首次落地候选 v1，正式跨运行时合同发布需另项审批，本轮不修改根 contracts。r2 的 v1 是历史设计示意，不能当作已存在生产者/消费者或对旧生产文件的兼容证明。下例所有 ID、摘要、名称和端口均为合成示例，摘要仅展示词法。

~~~json
{
  "format": "aiis.plc_points",
  "schema_version": 1,
  "origin": {
    "kind": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "plc_id": "22222222-2222-4222-8222-222222222222"
  },
  "export": {
    "producer": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "config_state": "saved_revision",
    "revision_id": "33333333-3333-4333-8333-333333333333",
    "payload_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "exported_at": "2026-11-16T11:00:00+08:00"
  },
  "plc": {
    "name": "PLC_A",
    "protocol": "s7",
    "connection": {
      "host": "127.0.0.1",
      "port": 31281,
      "rack": 0,
      "slot": 1
    }
  },
  "dbs": [
    {
      "id": "44444444-4444-4444-8444-444444444444",
      "name": "MinimalImport",
      "number": 21,
      "size_bytes": 8,
      "source_enabled": true,
      "points": [
        {
          "id": "55555555-5555-4555-8555-555555555555",
          "name": "DB21_payload_ready_Bool",
          "display_name": "旧名称",
          "display_names": {
            "zh-CN": "就绪",
            "en-US": "Ready"
          },
          "description": "模拟设备就绪",
          "source_path": "payload.ready",
          "data_type": "BOOL",
          "byte_offset": 0,
          "bit": 0,
          "source_enabled": true
        },
        {
          "id": "66666666-6666-4666-8666-666666666666",
          "name": "DB21_payload_count_Int",
          "display_names": {
            "zh-CN": "计数",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.count",
          "data_type": "INT",
          "byte_offset": 2,
          "source_enabled": true
        },
        {
          "id": "77777777-7777-4777-8777-777777777777",
          "name": "DB21_payload_temperature_Real",
          "display_names": {
            "zh-CN": "",
            "en-US": ""
          },
          "description": "",
          "source_path": "payload.temperature",
          "data_type": "REAL",
          "byte_offset": 4,
          "source_enabled": true
        }
      ]
    }
  ]
}
~~~

### 4.1 字段与验证

1. 编码为 UTF-8 无 BOM；恰一顶层对象；拒绝重复 key、未知字段、非法 UTF-8、非整数词法用于整数、隐式转换和未明确允许的 null。必须是精确 format 和整数 schema_version 1；未知主版本拒绝，不猜兼容。文件上限 1 MiB，层级上限 16；单 PLC 最多 32 DB、4096 点，DB/点数量与文件大小都纳入导出预览。超预算整份文件失败，不静默截断。
2. origin 是 PLC 及其 DB/点身份的命名空间：kind 恰为 device_simulator 或 data_acquisition_agent，profile_id 为最初建立该命名空间的 DS 工作区 profile ID 或 DAA 本机实例 ID，plc_id 为该命名空间中的稳定 PLC 身份。它不表示每个点都是该应用创建，也不表示实际物理设备的作者或来源；export 单独记录本次实际导出者。三个字段均必填；ID 使用规范小写 UUID v4。文件名、显示名称、网络地址及 DAA 上报身份都不是 PLC 身份。导入后再从另一应用导出，保留 origin 和已映射的 DB/点身份；经本地显式新增的 DB/点可使用不冲突的本地 UUID v4 作为该命名空间下的新 ID，不改写既有 ID。若 ID 已冲突则阻断并经显式身份处理，不能在只读导出时悄悄换 ID。文件不声明逐点创建者，界面不得把 origin 当成所有点的创建者。
3. export.producer 是本次实际导出应用，v1 恰为 device_simulator 或 data_acquisition_agent；profile_id 是导出方自身的稳定 profile/instance 标识；exported_at 是真实生成时间，RFC 3339 且 +08:00。config_state 对 DS 是 saved_revision；对 DAA 是 active_revision 或 saved_draft。revision_id 对 DS/DAA 已保存版本为原版本 ID，对 DAA 草稿为导出时持久草稿 ETag；payload_sha256 是该应用实际选中保存内容的原始字节 SHA-256，小写 64 位十六进制。草稿 ETag 不冒充不可变 revision。导出者改变后的字段不伪称原程序导出。SHA 是完整性/追溯，不证明来源可信或物理设备正确。
4. plc.name 是非空显示名称，UTF-8 最多 100 字节；protocol 首期固定 s7。connection 为客户端目标：规范 IPv4 单播地址、port 1..65535、rack 0..7、slot 0..31。可选 local_tsap 与 remote_tsap 分别为客户端 calling/called，整数 1..65535；省略时 client local TSAP 为 0x0100，remote TSAP 为 0x0100 加 rack×32 加 slot。DS 监听地址及 TSAP 必须经客户端视角转换和用户确认；通配监听地址不能作为目标，loopback 只对同机有效。DAA 当前无自定义 TSAP 模型，遇非默认值应明确报不兼容并禁止导入执行，不可忽略。
5. dbs 必填且非空。每 DB id 是 UUID v4，number 为 1..65535 且同一 PLC 唯一，name 非空最多 100 UTF-8 字节，size_bytes 为 1..65536；points 必填且非空。DB ID、点 ID 在同一文件全局唯一，不能跨类别复用。每点 id 为 UUID v4，name 为同一 PLC 内唯一且稳定的 ASCII 程序引用名，最多 100 字节且须符合现有命名规则；显示名和语言切换不改变 name。可选 source_path、display_name、description 分别至多 512/256/500 UTF-8 字节；display_name 是无语言标记的原有单条值，须独立保留，不能归入双语任一字段。description 是独立的可选说明，最多 500 UTF-8 字节，非空时来自 DS 操作者显式编辑的独立描述或可核实的来源；不能用无语言 display_name 或双语名冒充注释。其他 producer 可以缺省该字段；缺省表示来源未提供，显式空串表示提供了空说明。
6. data_type 首期显式枚举 BOOL、BYTE、USINT、CHAR、INT、UINT、WORD、DINT、UDINT、DWORD、REAL 和 STRING[n]（n=1..254）。整数/REAL 按 S7 大端，REAL 为 IEEE 754 单精度，STRING 最大长度和编码须明确为 S7 STRING[n] 的 n 与 ASCII；CHAR 为单字节 ASCII。BOOL 必须有 bit=0..7，其他类型禁止 bit；字节宽按类型确定，STRING 占 n+2。必须满足 offset + 宽度不超过 DB 长度，同 DB 的物理占位不能重叠；不同 BOOL 可占同一字节的不同 bit。规则对禁用点也成立，不强推未获证明的 TIA 偏移或优化块布局。
7. source_enabled 只记录本次导出应用的启用事实，其解释依据 export.producer，而不是 origin.kind。DB 层的 source_enabled 是依导出者分型的可选布尔值：DS 导出时必填且如实取该 DB 的 enabled；DAA 当前的 DB 没有独立 enabled 事实，因此 DAA 导出必须省略该字段，不能从 PLC、采集组或点位状态推测。v1 消费者应验证此分型；DB 层缺失表示导出方没有提供此事实，不等于 true 或 false，显式 null 非法。点位层的 source_enabled 在 v1 对 DS 和 DAA 均为必填布尔值：分别取本次导出者的 Point.enabled；点层缺失或 null 为格式错误，不作 true/false 兜底。DS 点位启用与 DAA 的点位采集启用、分组语义不同。DS 文件经 DAA 导入并由 DAA 重新导出时，即使 origin.kind 仍为 device_simulator，也须按实际 export.producer=data_acquisition_agent 表达：DB 层省略，点位层为 DAA 本地实际 enabled；不能把旧 DS DB 启用状态冒称为 DAA 事实。
   这些字段既不是通用写权限，也不自动分配 DAA 采集组或改变 DS 模拟策略；消费者展示导出方、字段实际值或“未提供”，本地启用与引用由本地明确配置决定。点缺少地址、命名未确认、类型未知、物理重叠或不满足本合同：导出器列出具体问题并阻止该实例文件，不丢点、不把它标成默认地址、不因禁用而隐藏错误。首版不提供跳过点的导出模式。
8. 只输出本应用当前实例已经声明并确认的点，包括禁用点；不是对物理 PLC 全部地址的发现。无点的空洞不伪造成点。实际设备布局、源版本、访问许可及连接目标仍由使用者核对；模拟成功不证明真实 PLC 的布局或许可。
9. 可选观察信息和结构树不在 v1 必需合同。DS 可在导出预览显示实际 selected/loaded 事实，但不能据此伪造所选 saved revision。原始 DB/UDT 文件全文或模拟规则不进入该文件。未来如增加可选结构树，必须另定版本与消费者兼容，不能将当前点列表宣称为完整 TIA 源树。

10. 每点可选 `display_names`，存在时必须是严格对象且恰有 `zh-CN`、`en-US` 两个字符串，各最多 256 UTF-8 字节；字符串原样保留，不从 name、source_path、comment、另一语言或未标记单条值推测、复制或翻译。`""` 是该语言未设置，null、非字符串、缺一个键或未知键拒绝。缺少整个 `display_names` 表示来源未提供：新目标两种语言均为空，已有目标默认保留本地值；对象存在时两值含空串均为明确输入，重导差异按 §5 逐语言预览和确认。导出端总是输出两个键，空值明确为 `""`。旧 r2 示例缺字段时可按这一缺省语义处理，但这不是旧生产者已存在的证明。
11. 可选 `display_name` 保留历史无语言标记的单条值，允许空串且不得为 null；消费者展示时标“语言未标记”，不用于当前语言的双语列。导入原文件、后续目录绑定和未来导出保留其确切值；缺省不自动清空已有值。DAA 原有 `comment` 与此独立，不能借用或覆盖以保存它。任何 source_path 是点位逻辑路径，不是本机路径。

### 4.2 来源版本选择

DS：用户选择一个真实、不可变的 saved revision 及其一个或多个实例；每个文件取该 revision 中对应实例切片。界面同时显示每实例当前 selected 和 actual_loaded 的版本及缺失状态；如果所选 revision 与实际加载不同，突出差异并要求明确确认。不得将 latest、草稿或 selected 冒充 actual_loaded，也不混入未保存编辑或运行值。用户可选择与已验证 actual_loaded 相同的 saved revision；直接从各实例不同 loaded 版本逐个导出的专用模式是后续扩展。

DAA：用户明确选择 active_revision 或已保存的 saved_draft，显示实际标识、来源和活动版本差异；未保存界面编辑不能混入。active 与 runtime loaded/used 分别显示，有差异如实提示。导出并不激活草稿或更改活动版本。两应用导出同一 origin 时，producer、版本和摘要描述当前导出者真实事实。

## 5. 身份映射、重复导入及冲突

1. 可跨文件追溯的外部身份为 origin(kind, profile_id, plc_id) + db.id + point.id；本地身份是 DS/DAA 各自现有 UUID。首次导入新目标时若 ID 在目标 profile 全局可用，可保留；冲突则生成新本地 UUID 并建立持久外部→本地映射，预览清楚显示。用户选择映射到现有 PLC/DB/点时，必须预览并显式确认；不能仅因名称、IP、DB 号或相似地址自动认定为同一身份。
2. 后续来自同一 origin 的导入优先按既有映射识别，稳定保留本地 PLC/DB/点 ID、DAA 采集组、周期、上报配置、样本与历史引用。相同文件且本地映射和名称未变时再次导入无变化，原草稿 ETag 和版本保持；本地已编辑显示名时先按下述三方差异处理，不能冒称无变化。同外部身份改地址、类型、名称、启用事实或 DB 号均列明前后差异和影响，不能仅因 ID 相同当作无变化。相同 ID 对应不同来源/成员、未知重名、非法范围和物理冲突必须阻断并说明。
3. 文件缺少匹配目标 DB 中原来存在的任一点，或目标 DB 含文件未声明的手工/额外点，首期均作为点集冲突阻断该 PLC 整份导入并保持原草稿，不因其是否已有历史引用而放宽。界面列出具体差异；由使用者先在来源整理一致的目录，或另行申请多来源合并方案。不得在确认后留下无法满足目录点一一对应的配置，也不自动删除、停用、重绑或覆盖旧点。改 DB 号同样先阻断，未选实例和其他 DB 不变。外部地址变化涉及连接目标或物理效果时显式确认，不能改变历史样本的解释。
4. 持久映射必须随目标配置版本保存；预览绑定所选文件原字节 hash、目标、映射、当前 ETag 和有效期。确认时重验，过期、目标变更或并发编辑返回冲突，不产生部分配置、来源归档或半份映射。一个文件不覆盖另一应用的数据库文件。
5. DAA 本地 PLC ID、采集 generation/sequence、样本 ID，以及 HTTP 上报 instanceId/plcId/sourceGeneration 是不同事实；导入目录不创建或替换外部上报绑定、不改历史/队列/原始样本/回执。DAA 样本继续引用本地稳定 ID；外部与本地映射只用于追溯，不声称两个不同历史 ID 自动等价。
6. v1 的一个导出 PLC 只有一个 origin 命名空间；同一目标 PLC 已持久绑定另一外部 origin 时，禁止自动合并、覆盖或将两个 origin 伪装成一个。不同来源均要纳入同一 PLC 时须另立可追溯身份归并设计。此前从未建立外部身份的本地 PLC，可在逐点一一匹配并明确确认后绑定首次输入的 origin；原本地 ID 与历史仍保持。DS/DAA 未建立外部身份的原生 PLC 首次导出以自己的 profile 和本地 PLC ID 构造稳定命名空间。

7. 显示名逐语言做可追溯三方比较：来源基准为上次确认的原始目录及其 SHA，另外展示当前本地值和此次输入（含字段缺失或显式空串）；无前次来源的已有本地目标也必须展示当前值。输入与本地不同或本地自基准编辑后再导入时，用户逐语言选择保留本地或采用输入；缺失字段默认保留，显式空串若要清空已有值须确认。选择和相应基准同源绑定、草稿一起原子提交；只预览/取消无写入。同文件、来源基准未变且未选择改变的重导保持 ETag；若新文件 bytes/SHA 变化，即使保留本地值，来源归档或绑定基准变化也会正常改变草稿 ETag；用户明确选择恢复/清空同样产生正常草稿变化。无语言 `display_name` 另行按相同缺失/冲突规则处理，不能算作 zh-CN/en-US 的值。`description` 缺失表示不提供、不清空现有 DAA comment；提供非空时新点经确认写入 comment，已有 comment 差异须展示来源基准、现值和输入，由用户选择保留或采用；显式空串若将清空非空 comment 必须明确确认。原文件与历史版本不改写。description、comment 与所有显示名各自独立，不改变上报字段。并发编辑使预览失效，不允许静默覆盖。

## 6. DS 导出与导入设计

### 6.1 DS 导出

导出入口以实例列表为起点，可多选并选择同一 saved revision，预览所选实例的来源版本、实际 loaded、连接目标、每个 DB/点及问题。源自 DS 的 id、name、type、byte/bit、DB number/length、来源路径及双语值按所选版本实际事实映射；真实存在的旧 display_name 作为未标记语言的独立字段保留，不能自动当作 description 或任何语言的显示名。DS 导出器对每点输出 `description` 字符串：非空原样取所选版本由用户显式填写的独立描述，缺省/空输出 `""`；不从旧显示名或注释猜测。所有点含停用点均按合同验证；确认或地址缺失时给出 DB/点定位并阻止该实例。初值、规则、权限、在线值不进入交换合同。

用户提供或确认采集客户端可达的 client host/port；不能把 0.0.0.0 作为远端连接目标，跨机器不能把 127.0.0.1 误当远端地址。TSAP 显示服务端与客户端方向并按既有合同核对。文件的导出成功不证明目标已连接、模拟正在运行或点值正确。

### 6.2 DS 从目录导入

输入可为 DS 或 DAA 导出的同格式文件。用户选择新建或匹配现有 DS 实例，预览并确认映射、DB/点、已有策略及冲突；只写 DS 草稿，按 DS 原有版本保存、加载流程处理，不启动。该能力尚未实现，可作为独立实施切片，与 DS→DAA 路径分别验证。

交换合同保留未标记 `display_name` 至多 256 UTF-8 字节，但当前 DS 本地旧 `displayName` 校验至多 200 字节。后续 DS 导入遇 201–256 字节的值，必须先有另行批准且验证过的无损承载方案，否则明确阻断该文件；不能截断、替换、混入双语字段或声称未来往返已实现。

文件中的 connection 是 client 连接目标，尤其 DAA 导出的地址可能是真实 PLC：**不得把它自动作为 DS 本机监听地址，也不得连接该地址。** 用户必须显式填写并确认自己的模拟监听 IP/端口及 rack/slot；冲突时拒绝。新实例默认不启动；模拟初值、规则、客户端读取/写入许可分别由用户在 DS 确认，不从 DAA 采集启用状态推导。目录点的来源被明确标记为 catalog，缺少原 TIA 结构时不伪造 DB/UDT 文件或完整来源树；维护一致的本地/外部身份映射及 DS 自身布局/命名确认。现有实例的规则、初值、权限和历史版本默认保留，冲突先预览，不能覆盖无关对象。


DS 的目录导入实施还需形成明确的 catalog 来源分型：保存并哈希用户选中的原始 JSON；同一实例的多个 DB 可引用同一份源版本，各 DB 分别绑定 sourceVersionId、原字节 SHA、originDbId 以及外部点 ID → 本地点 ID 的映射。外部 origin 和映射随工作区草稿/版本持久保存；catalog 绑定与既有 TIA SourceBinding 分型明确且不相互冒充。验证时重验源版本、SHA、origin、DB/点身份、完整点集、类型与物理地址；缺失、重复、越界、点集冲突或来源不一致阻断，不能退回未校验的手工点路径。没有原 TIA 文件时不伪造 DB/UDT 来源、结构树或初始值；DS 自身的名称/地址签名及加载前确认仍须由用户完成。

导入目录后若在 DS 修改目录 DB 的点集或地址，须显式预览并确认，生成绑定前一来源 SHA 的不可变内部点集快照；该快照标识为 DS 本地生成，不冒充外部交换文件，也不包含当前配置自身的 revision/SHA，避免自引用。新草稿以新快照重新建立完整映射，其他 DB、原始输入和历史版本保留；新点使用不冲突 UUID、原点身份不变。重新导出仍是同一个候选交换格式，并如实记录 DS 作为本次 producer。

优先评估使用现有 source_versions 和可选配置元数据且保持原 DDL；新旧二进制、已保存版本/原 SHA、selected/loaded 与回退必须单独验证。若需要修改物理库结构或迁移已用 profile，停止对应实现并另立明确的 schema-maintenance 与采用审批。

### 6.3 两端显示名基础

DS 点配置增加可选 `displayNames`（含 `zh-CN`、`en-US` 两个字符串）和独立可选 `description`；原 `displayName` 保持原值和“语言未标记”语义。用户可为手工点和 TIA 点显式填写/编辑描述，缺省或空为未设置；既有单条显示名和 TIA 注释不自动填充，旧值和历史保持。DAA 不在 Point 加双语字段，而在 schema 1 配置顶层新增可省略 `pointDisplayNames`，以当前本地点 UUID 对应相同两键对象；目录导入以后还需可省略 `pointLegacyDisplayNames` 单独保存未标记单条值，不能放在 `comment` 或 PointFact 中。字段缺省在内存显示两种语言均为空；两值都为空时新保存配置可省略对应可选字段/映射项，任一非空则保存两键完整对象，不因读取旧草稿或旧版本产生写回。所有字符串均按 §4.1 字节上限验证，非法类型/null/多余键拒绝，不做隐式转换。

两端点位列表保留程序 `name`，另显示**唯一由顶栏当前语言**选取的显示名；当前语言为空时显示空白或明确未设置占位，不回退 name、另一语言、comment 或旧 displayName。编辑框可同时编辑两个语言值；切换顶栏语言只改变显示，不修改配置、ETag、版本或上报。旧单条值如展示须标明语言未标记，保持原样，操作者可手工填写双语值但不得自动复制。

DAA 的映射键必须是配置中唯一存在的本地点 UUID，不能跨 PLC/引用不存在点；对同一身份重导、改名、分组、地址更新保留映射。明确删除点/DB/PLC 时仅在对应草稿事务移除已删除点的映射，旧版本/样本不重写；点 ID 改变或重绑必须显式预览，不能悄悄将旧点名称附到新身份。新的显示名字段不进入 `Point`、`PointFact.definition`，也不合并进 name、comment、value 或上报的其他字段。

## 7. DAA 导入：无需再提供 DB/UDT

### 7.1 来源分型和完整性

DAA 现有配置的 Db.source_id 指向逻辑 SourceDocument，启用点还要匹配 Db.tree 中的叶及 type；SourceDocument 内容须与 SHA 一致。这是当前事实，不能只把目录点转成空树并关闭校验，也不能伪造 .db/.udt 内容、文件名或 TIA 源行。

拟议做法优先复用 DAA-005/006 的 **schema 1 可选字段、旧 DDL 不变**先例：

- 在配置 JSON 添加可选 catalog bindings，字段缺失表示原有 DB/UDT 或旧配置，读取旧 payload 不写回；按本地 DB ID 关联实际 catalog 逻辑 source ID、源原字节 SHA、外部 origin/DB ID 及外部点 ID → 本地点 ID 映射。保留原有 Point 的稳定身份和样本字段结构，避免把绑定元数据塞入每个 PointFact。
- 实际导入 JSON 作为明确的 catalog SourceDocument，保存用户所选原始 UTF-8 内容及 SHA。一个 PLC 导入的一份文件建立一个逻辑 source；该 PLC 多个 DB 的 source_id 可以共同指向此 source，由每个 DB 的 catalog binding 精确标识文件中的对应 DB。不同 PLC 的逻辑 source 各自独立；同 SHA、同字节的物理归档按现有策略复用，不覆盖旧归档。共享单一逻辑 source 避免每 DB 重复一份大 JSON 而突破配置容量。source_id 始终指向真实目录源，而非伪造 TIA 源。
- 对有 catalog binding 的 DB 执行目录专用完整性验证：解析并重验文件版本、原字节 SHA、origin、DB/点 ID、名称、类型、地址及占位；本地映射必须一一对应，不允许缺失、重复、跨 PLC、改写绑定或引用文件未声明的点。当前 DB 关联源校验中对 db_number/原 importBinding 的要求，在 catalog 分支以完整的目录 DB 关联校验替代；旧来源分支的原逻辑不变。source_path 如文件没有该事实则保持缺失语义，不伪装为 TIA 路径；目录点可在本地视图展示有事实的来源路径和单独的目录身份。
- catalog 的完整性表示“已完整验证该 JSON 声明的点集”，不表示已验证 TIA 工程完整树。目录分支可将 Db.complete 用作目录完整性准入，Db.tree 可以为空；UI 明示来源是目录点列表，不生成假树或声称可恢复原源文件。对原 DB/UDT 来源，原 Db.tree、leaf_matches、source/UDT 闭包和地址校验完全保留；只在显式 catalog 分型下使用等强度的目录成员核对。
- 导入确认后地址及确认依据明确记录为目录来源与用户确认；若现有 origin 枚举无法如实表达，需在后续受批实现中增加清晰的 catalog 类型并核对样本定义和上报兼容，不能谎写为 TIA 自动推算。对后续手工改地址/类型，必须要求明确的本地覆盖确认，保留原目录和修改前值；激活校验对照原目录加明确覆盖，而不是绕开校验。覆盖及其重新导出语义须在实施切片冻结并有负例。
- 只新增可选配置元数据并不能自动证明兼容：现有 serde deny_unknown_fields 的旧二进制可能拒绝新 payload。必须验证新版本零写读取旧草稿/版本/样本、原字节/hash 不变；旧版本碰到新 catalog 元数据须安全拒绝，不得静默启动错误配置或生成空库。降级前停止自有采集并保留完整 profile；只在证明兼容的副本或原备份上回退，禁止覆盖真实历史。
- 当前 configuration_revisions 和 configuration_contexts 的物理 schema 对配置 payload schema_version 均有 CHECK=1。若验证证明上述 v1 可选字段方案不能满足完整性、性能或兼容性，则停止该实现切片，提出独立的 schema-maintenance Revision，明确双库兼容、升级前备份、中断恢复、旧记录不重写、回退和真实 profile 采用审批；不得把 schema 2 或 DDL 当成本设计已授权的自动迁移。

拟议的 DAA 配置 JSON 扩展是可省略的 catalogBindings 列表。每项包含 localDbId、sourceId、sourceSha256、sourceKind、originDbId 和 pointMappings；每个 pointMapping 包含 localPointId、catalogPointId，可选 localOverride。sourceKind 明确区分外部 exchange_json 和下文的 local_snapshot，按对应封闭格式分别校验。其所属本地 PLC 从 localDbId 关联到本地 DB 后核对，不信任输入另填的 PLC。逐语言显示名及无语言单条值保留于本地配置级映射，字段的存在性、最后确认来源 SHA、逐语言冲突选择须与目录绑定及草稿一同保存，不写入 Point。sourceId 必须属于同一 PLC，sourceSha256 必须等于该 SourceDocument 原字节摘要，originDbId 必须在相应外部文件或内部快照中唯一存在；所有 localPointId/catalogPointId 在本映射中分别唯一，且两侧点集必须完整一一对应。两个 DB 不得引用同一 originDbId；同一外部文件的一次导入在一个本地 PLC 只使用同一逻辑 sourceId，跨 PLC 则分别持有逻辑来源。

localOverride 仅用于使用者在 DAA 显式修改目录点的地址或类型：含该次确认所依据的 sourceSha256、修改后的 dataType/offset/可选 bit、用户确认原因。无 override 时本地点的类型/地址必须与归档 JSON 一致；有 override 时必须匹配已确认覆盖，且重新执行类型、DB 长度、bit 和跨点重叠校验。源文件重新导入后若原点类型/地址与覆盖基准发生变化，预览列出冲突并暂停该点更新，由用户明确保留覆盖或采用新值；不得悄悄以旧覆盖套用新源。DAA 导出采用所选已保存配置中的实际有效点位，保留 origin 和点 ID，并以本次 DAA 配置 revision/SHA 如实标明新的 exporter 来源，不把覆盖值谎称来自旧原始文件。名称、显示信息和分组的变更仍分别走既有命名及草稿保护。

在已导入 catalog 的 DB 里新增本地点时，不得仅修改 pointMappings 而继续指向不含该点的旧文件。拟提供明确的本地目录修订操作：在预览确认后基于当前已验证目录、有效覆盖和新点生成该 DB 的不可变内部点集快照，格式标记为 daa.catalog_snapshot，含 origin、originDbId、原 source SHA 和完整点集，单独算 SHA 并归档；新草稿内该 DB binding 指向此快照且重新建立完整一一对应。该快照是 DAA 生成的内部来源材料，不冒充原 DS 文件或 DB/UDT，不携带当前配置自身的 revision/SHA，因此不产生配置与自身摘要的循环引用。其他 DB 可以继续指向原交换文件；更新源、绑定及草稿在同一事务提交。追加点沿用原命名空间但不声称由 DS 创建；用不冲突的本地 UUID v4 作外部点 ID，既有映射不变。导出时才从所选已保存 DAA 配置生成统一交换 JSON，并正确填写 DAA 的实际版本/SHA。内部快照不作为跨应用合同公开，也不覆盖先前原始文件或历史 revision。

为支持无需 DB/UDT 导入的有效地址，目录导入经用户预览确认后，Address.confirmed 才为 true，拟议新增 origin 值 catalog 和明确的确认原因；手工覆盖仍保留独立的手工来源。此值只能用于具备有效 catalog binding 的点。因 PointFact 包含 Address 定义，新值会出现于后续新样本的本地定义中：实施时必须验证 DAA 原有历史解码及事实 v2 上报契约兼容，保留所有既有样本字节和已冻结上报内容；若外部合同不接受该值，返回 PM 另定范围。读取和解析目录本身不构成对真实 PLC 布局的验证。保存前还要核算单个源、完整配置 JSON、归档和容量预算；超限时明确拒绝且无部分写入，不能因为单文件小于 1 MiB 就假定目标配置一定可容纳。

### 7.1.1 事实和上报的双语边界

当前采集器直接 `point.clone()` 形成 `PointFact.definition`，而 `facts_wire::definition_check` 会拒绝定义中任何未知键。仅给 Point 增加 displayNames 会破坏既有本地样本验证；本设计用配置顶层映射避开该路径，Point 字段和严格校验保持原样。配置上下文可能包含此映射，但不得作为外发正文发送：独立检查既有 `sample_upload` 的 plc-facts/v2 点列表、历史 `facts_wire` 批次/冻结、transport 及所有现存上报路径，确认中文/英文及未标记值均不出现，原始 `name` 原样上报，不能混入 name/value/comment 或其他字段；不改后端和公共合同。

测试使用自有隔离合成 profile 对照旧样本、manifest、上下文、待发/冻结正文、ACK 和历史原 bytes/SHA，证明旧记录不重写；新配置下采集的新样本、manifest、上下文和两条实际构造路径都须通过原校验及原合同。用户明确保存并激活新配置可正常产生新 configRevision 和新时间/样本 ID，不能要求新旧样本或上报的所有字节相同；验证字段/身份语义及严格契约，而不是伪造相同摘要。若真实链路仍携带双语文本或旧程序不能安全拒绝新配置，则阻塞并返回 PM，不能改弱事实校验。

### 7.2 DAA 导入体验与采集准入

选择文件后，新建 PLC 或选择现有 PLC，预览同一文件的连接、DB、所有点、来源、变更、不可支持项及映射。导入确认可复用文件中已确认地址，但仍须本地明确用户确认；目标真实 PLC 地址需现场资料核对。首次新建的点默认不自动开始采集。用户可以在导入预览中选择现有采集组，或显式新建组并填写周期，一次批量分配选中的受支持点；同 PLC/DB 的启用点遵守现有 DAA runtime 分组规则、资源预算与数量上限。未选择的点保留并显示为未分组/停用。

确认仅提交到草稿；用户可随后显式激活配置、连接并采集。端到端验收必须证明：**文件和 DAA 新空隔离 profile 足够，不额外提供或重新导入 .db/.udt**；由 DS 受控模拟器提供 BOOL、INT、REAL 可读值，DAA 一次分组后保存、激活、真实读取并核对采样点 ID、地址、类型、值和质量。失败有具体原因；不能以解析 JSON 或纯内存单测代替此闭环。旧配置和运行任务按原路径工作。

### 7.3 DAA 导出

按 PLC 多选、每台一文件，从用户选择的 saved_draft 或 active_revision 生成上述共同合同；仅导出该配置中已声明且可通过合同完整性检查的 DB/点。未确认地址或类型问题必须逐点报告并阻止该实例，不能用停用状态掩盖。重导本地由目录输入的配置时保留外部 origin 和稳定 ID 映射，并如实记录 DAA 作为导出者及选定配置版本；未绑定外部命名空间的 DAA 自建 PLC 以自身 profile/PLC 建立稳定身份，已绑定 origin 下新增点沿用该命名空间但不冒称来源。DAA 的 DB 没有独立启用字段，导出时省略该层 source_enabled；每个点的 source_enabled 必须取当前 DAA 配置中的 Point.enabled，即使来源命名空间是 DS 也不能沿用源文件的旧启用值。采集组、周期、运行历史、队列、上报设置及凭据不进入 JSON。



## 8. 拟议实施次序与任务归属

| 阶段 | 拟议范围 | 进入和退出边界 |
| --- | --- | --- |
| P0 | ARCH-PLC-001 r3 双语与同一完整 JSON 设计 | Human Owner 已批准 r3 设计范围；r2 原批准保留历史效力，软件实现另行批准。 |
| P1 | `device-simulator::DS-004 r1` 和 `aiis-ics-arch::DAA-018 r1` 各自实现本地双语点位 | 各自精确批准并独立 Development、fresh-context Verification 和 Human Owner 最终验收；可并行，但两项都完成才能进入 P2。 |
| P2 | `device-simulator::DS-003 r2` 导出 + `aiis-ics-arch::DAA-017 r2` 导入 | 两项基础均完成 STD 后，各自仍需精确实施批准；同一 DS 实际导出文件交 DAA 使用，验证无原 DB/UDT 的受控采集。 |
| P3 | DAA 导出及 DAA→DAA；DS 导入及 DAA→DS | 后续各立范围；DS 明确模拟监听地址，不自动启动。 |
| 后续 | 正式跨运行时合同、FF/CA、其他协议和现场采用 | 分别立项批准；本轮不修改 contracts、FF 或 CA。 |

两个应用的基础任务和导入/导出任务各有独立 owner 与验收链，不继承不同模块的实施批准。合成 JSON 验证不能冒称 DS 实际导出→DAA 导入→采集闭环。受批 Development 按触达面使用 aiis、plc-point-mapping、rust-runtime、desktop-tauri、frontend-ui、i18n-workflow 和 code-document-indexer；如需物理 schema 则另走维护 gate。

## 9. 拟议验收标准

下列为未来经批准的软件范围设计口径，不是已完成证据；各切片确定精确 AC 和真实验证环境。

| 编号 | 可观察标准 |
| --- | --- |
| AC01 | 一台 PLC 一份完整 JSON；多选两台分别生成，实例、DB、点不串；取消、冲突和部分失败正确报告且无半文件。 |
| AC02 | 候选示例及多 DB 正例按冻结的格式验证；重复键、未知版本/字段、非法编码/类型/UUID、超限、缺字段、BOOL bit、STRING 宽度、越界与重叠有可复现负例。 |
| AC03 | DS saved/selected/actual_loaded 与 DAA saved_draft/active/loaded/used 各自准确呈现；实际版本和原 payload SHA 如实追溯，不混未保存编辑。 |
| AC04 | DS 包含 BOOL、INT、REAL、STRING 及停用点时导出完整声明；地址或名称未确认、未知类型、结构错误均定位并阻断该实例，无默认值和静默漏点。 |
| AC05 | DS JSON 导入全新隔离 DAA profile 无须 .db/.udt；显式分组、保存和激活后，以隔离 DS S7 模拟完成 BOOL/INT/REAL 真实读取，核对 ID、地址、类型、值与质量。 |
| AC06 | DAA 目录来源原字节/SHA、source_id、DB 和点位映射完整一致；伪造源、错 hash、错成员/类型/地址和重复绑定拒绝；旧 DB/UDT 的 tree/leaf_matches 验证不减弱。 |
| AC07 | DAA→DAA 使用同一完整文件，在新目标预览和确认，保留身份来源、完整点集；分组和周期由目标用户选择，确认前不修改草稿或连接设备。 |
| AC08 | DAA 按实例支持 saved_draft/active_revision 导出，多选分别生成；来源为 DS 时仍以 DAA 作为实际 producer，DB 层无 source_enabled，点位层取 DAA 实际 Point.enabled。 |
| AC09 | DS DB/点启用分别取 DS 实际值；DAA DB 层缺失表示未提供，不能默认 true/false；两应用的点位 source_enabled 必填，缺失、null 和与 producer 不相容的字段拒绝。 |
| AC10 | DAA 导出文件导入 DS 时不得复用文件中的客户端目标作为模拟监听；操作者显式确认新的本机监听地址，之后按 DS 版本流程配置，导入本身不启动或连接。 |
| AC11 | 对已有目标，无本地变更且无冲突的重复导入保持 ETag 与本地 ID；显示名本地编辑后按三方差异显式选择，缺点、额外点、跨 origin、ID 冲突或变更地址等均按规定阻断或确认；整 PLC 提交原子。 |
| AC12 | 采集组、周期、DS 规则与历史版本、DAA 既有本地 ID、样本、generation/sequence、上报绑定、pending/ACK 及未选实例不被静默覆盖或改写。 |
| AC13 | 已导入目录的 DS 或 DAA 本地点集变更产生对应应用的可核验内部快照和稳定映射，外部原文件及历史 revision 原字节保留；来源变化、地址修改与手工覆盖冲突先预览。 |
| AC14 | 新版本读取旧 payload 零写回；旧二进制遇新目录元数据不会静默运行错误配置；任何必须的物理 DDL、迁移和真实 profile 采用先取得独立批准并验证中断/回退。 |
| AC15 | wildcard、loopback、非默认 TSAP、取消/并发、路径、文件替换和多个实例有可观察负例；模拟结果不外推真实 PLC。 |
| AC16 | 两端原有启动、草稿、版本和权限行为保持；新增可见文案双语对称，表格列宽遵循公共规则；项目测试、原生/跨平台/现场证据如实分层。 |
| AC17 | 两端点表当前语言分别显示精确双语值；一侧空、一侧非空、两侧空和顶栏切换均可验证，切语言不写配置/ETag；旧 displayName 明示无语言且不混入两语言。 |
| AC18 | 单个完整 JSON 同时保留两语言、旧无语言单条值、可选真实 description 及全部启停点；缺失 display_names、显式空串、错误类型/未知键、重导三方差异和本地编辑冲突均有明确可测结果。 |
| AC19 | DAA 原 Point、PointFact 严格键集、comment 和上报 name 不被双语值污染；旧样本/manifest/队列/回执不重写，新配置 context、样本和现存上报链通过原合同，允许正常新 configRevision。 |
| AC20 | 两基础任务各自完成 STD 最终验收后才开始 DS-003/DAA-017 实施；真实 DS 导出文件用于 DAA 隔离端到端，禁止以合成单测替代。 |

## 10. 边界、风险和待审事项

- 同一完整文件不等于物理 PLC 全部地址已被发现，也不证明设备实际布局。地址和可达目标必须用户核对；不含凭据或授予写权限的信息。
- 目录身份和生产运行身份不同。不同 origin 的 PLC 不自动归并；历史样本、回执、DB/UDT 归档和旧任务已批准状态保持。
- DAA 可选字段、目录来源分型及 DS 目录绑定均为设计候选，须以产品源码和隔离闭环验证；若需物理 DDL/旧 profile 迁移，另立 schema-maintenance 和采用 gate。
- 按 Human Owner 本轮要求，设计包含两端导入和导出；具体实施顺序仍在精确实施任务中决定。合成/本机验证不等于跨平台、现场、生产部署或长期运行验收。

Human Owner 已批准 r2 和 r3 各自的设计范围；所有软件实施均待各自精确批准。当前不创建 Development tasks 或 Verification checklist。

## 11. 修订、批准历史和 PM handoff

2026-11-16（Asia/Shanghai）Human Owner 原话：“可以，批准 ARCH-PLC-001 r2 设计范围。接下来按 STD 拆分 DS 和 DAA 的实施任务，优先考虑 DS 导出、DAA 导入；FF 后续单独适配，暂不修改代码。”该决定仍是 r2 设计范围的真实批准，不是代码或最终验收批准。用户审阅、登记前 r2 原始 SHA256 为 `48d2415e9d6a6e41ff0996f8da1c64ca748067b28975be81382ae455c605987c`；登记批准后的完整 r2 写前 SHA256 为 `4928ac9697b6dc334d828d6f24596a6982798df4668111d3ab9a1d9fafc5d6b0`；其内部封存的 r1 原文 SHA256 为 `2b242fad628e2b67ca61f44c58f195485315a204e58fe1c497d3984656734de6`。

### r3 设计范围批准记录

2026-11-17（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 ARCH-PLC-001 r3 设计范围。请按 STD 记录批准，暂不改代码。

该决定仅批准 `aiis-ics-arch::ARCH-PLC-001 r3` 设计范围；批准前完整草案 SHA256 为 `fe52bdf36335d2dc955920892194787884782a852209de3efd3d6ce74c88aee4`。此决定不批准最终验收、代码、测试、合同、数据库或设备实施；DS-004 r1、DAA-018 r1、DS-003 r2、DAA-017 r2 的实施规格仍为 draft，须各自获得 Human Owner 精确批准。DS-004 和 DAA-018 分别完成 STD 至 Human Owner 最终验收后，方可进入另经批准的 DS-003 / DAA-017 实施。

2026-11-17 依 Human Owner 新要求先形成 r3 草案；本轮未执行产品、数据库或设备操作。PM 将实际静态检查结果交给协调者；后续 Development 和 fresh-context Verification 各自记录真实证据。

### DAA 双语基础版本衔接

2026-11-17（Asia/Shanghai），Human Owner 在审阅问题中明确回复：“批准 DAA-018 r2 及版本衔接”。§8 的 P1 原文记录当时的 DAA-018 r1 计划：r1 实施范围虽获批准，Development 在改代码前因白名单缺少命名预览 DTO/服务而记录阻塞。现由已批准的 `aiis-ics-arch::DAA-018 r2` 作为同一 DAA 双语基础任务的活动实施版本，r1 阻塞与批准历史保留。

后续导出/导入必须先满足 DAA-018 r2 自身 fresh-context 独立 QA 与 Human Owner 最终验收，以及 DS-004 自身 Human Owner 最终验收，并分别取得导出/导入实施批准；不能把未来 r2 的验收记为 r1 已验收。该版本衔接不更改 r3 的能力范围、原 P1/AC 文字或上报、导出/导入安全边界。

## 附录 A：完整 r2 已批准设计原文（含 r1 历史，非当前合同）

原文 SHA256: `4928ac9697b6dc334d828d6f24596a6982798df4668111d3ab9a1d9fafc5d6b0`。围栏首行之后至闭合围栏之前为原始 r2 文件字节，包含原末尾换行；其中 r1 再按其内部围栏无损提取。

~~~~~~~~~~~~~~~~markdown
Task ID: ARCH-PLC-001
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: r2 设计范围已批准；DS-003 / DAA-017 实施规格各自待精确批准，设计独立验证与最终验收另行推进
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS 与 DAA 的逐 PLC S7 点位 JSON 双向交换详细设计
Owner: Automation World / Device Simulator 与 Data Acquisition Agent
Acceptance Chain Reference: 本任务遵循 Development Lifecycle Workflow；Human Owner 审阅精确设计 Revision，后续 Development、fresh-context Verification 和 Human Owner 最终验收各为独立 gate。
Related Task: device-simulator::DS-002; data-acquisition-agent::DAA-005; data-acquisition-agent::DAA-006; data-acquisition-agent::DAA-007; data-acquisition-agent::DAA-010; data-acquisition-agent::DAA-013

# DS 与 DAA 逐 PLC 点位 JSON 详细设计 r2

## 1. 本次请求、范围与状态

Human Owner 本轮明确要求：先保持一份完整 JSON，将设计任务调整到 Automation World 目录，范围只包含 DS 和 DAA，按 STD 先由 PM 修订，暂不改代码。本任务保留唯一 Task ID ARCH-PLC-001、项目命名空间与一份活动规格，归属调整到 Automation World；因范围和归属实质变化，批准前修订为 r2 draft，不继承 r1 批准；当前 r2 设计范围已获批准。原 r1 未获批准，其原文完整封存在本文件末尾，仅供历史追溯。

本轮仅迁移并修订 PM 的本 spec，由主协调按实际事实更新必要索引；不修改产品、测试、配置、公开合同、其他任务或数据，不创建 tasks/checklist。此 r2 的设计范围已获批准；用户尚未批准任何代码、独立 QA、最终验收、发布、已有数据库迁移、真实设备或现场操作。Human Owner 批准设计范围不自动授权实现；具体软件切片、正式跨运行时合同发布及真实 profile/现场采用需分别明确范围与批准。

## 2. 已核现状与设计目标

- DS 可配置多个实例、导入 DB/UDT，并区分草稿、保存版本、selected 和实际 loaded；DS 的点位 JSON 导入/导出仍是提案，不能声称已实现。[DS 使用手册](../../device-simulator/USER_GUIDE.zh-CN.md) · [DS-002 设计](../../device-simulator/plans/DS-002-multi-protocol-simulation-and-device-debugging/spec.md) · [DS 配置模型](../../device-simulator/runtime/src/domain/configuration.rs)
- DAA 现有来源导入入口为 .db/.udt；点位源、地址、分组、草稿和采集配置均有既有验证与持久化边界。[DAA 导入入口](../../data-acquisition-agent/src/app/plc/components/SourceImportPanel.vue) · [DAA 配置校验](../../data-acquisition-agent/src-tauri/src/domain/local_configuration.rs) · [DAA-005](../../data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md) · [DAA-006](../../data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/spec.md)
- DAA 配置、source_documents、runtime context、样本、上报与回执各有权威；现有相同正文的物理归档去重不能当作重写本地身份或历史的授权。[本地存储说明](../../data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md) · [存储 schema](../../data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs)
- FF 当前不能直接消费本候选完整 JSON，其后续适配另行处理。

设计覆盖 DS 和 DAA 各自按 PLC/实例导入、导出同一种完整 S7 点位 JSON，支持 BOOL、INT、REAL 等可表达类型和多 DB；多选时每台各生成一个文件，不因目标程序删除或另行生成子集。核心路径为 DS→DAA 无须再次提供 DB/UDT、DAA→DS 按显式模拟监听地址建立配置，以及 DAA→DAA 的按目标预览与导入。三条路径均是拟议功能，离线文件交换不要求源程序在线或共享 SQLite。

## 3. 文件边界与交互

- 一个 JSON 恰含一个逻辑 PLC、一个客户端连接描述、一个或多个 DB 和每个 DB 已声明点位。导出可多选实例，分别生成每台一个文件；不把多个 PLC 合并在同一 JSON。
- 文件携带完整已确认声明，包括停用点及其类型/地址；不包含实时值、凭据、环境文件、本机路径、DS 模拟初值/规则/写权限、DAA 采集组/周期/历史/上报数据。逻辑 source_path 可保留有事实的 TIA 路径，不代表文件系统路径。
- 导出针对所选持久配置预览完整信息，显式选择目录并处理重名；每份文件完整校验后原子落盘，失败不留下半文件。多选逐实例报告成功/失败/取消，不伪装全体成功。
- 导入选择文件与目标实例，预览连接、版本、点位和差异，确认后仅原子提交目标应用草稿；不自动激活、连接、启动、采集、上报或覆盖其他实例。预览和取消不写入配置或原文件。
- 两应用不共用 SQLite、可写目录或运行状态；导出文件只是快照，导入不构成现场地址、设备值、业务状态或写权限的证明。

## 4. 候选 JSON v1：单台 S7 PLC

本节是供 Human Owner 审阅的 DS/DAA 候选，正式跨运行时合同发布需另项审批，本轮不修改根 contracts。下例所有 ID、摘要和端口均为合成示例，摘要仅展示词法，不声称与任何实际数据对应。

~~~json
{
  "format": "aiis.plc_points",
  "schema_version": 1,
  "origin": {
    "kind": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "plc_id": "22222222-2222-4222-8222-222222222222"
  },
  "export": {
    "producer": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "config_state": "saved_revision",
    "revision_id": "33333333-3333-4333-8333-333333333333",
    "payload_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "exported_at": "2026-11-16T11:00:00+08:00"
  },
  "plc": {
    "name": "PLC_A",
    "protocol": "s7",
    "connection": {
      "host": "127.0.0.1",
      "port": 31281,
      "rack": 0,
      "slot": 1
    }
  },
  "dbs": [
    {
      "id": "44444444-4444-4444-8444-444444444444",
      "name": "MinimalImport",
      "number": 21,
      "size_bytes": 8,
      "source_enabled": true,
      "points": [
        {
          "id": "55555555-5555-4555-8555-555555555555",
          "name": "DB21_payload_ready_Bool",
          "source_path": "payload.ready",
          "data_type": "BOOL",
          "byte_offset": 0,
          "bit": 0,
          "source_enabled": true
        },
        {
          "id": "66666666-6666-4666-8666-666666666666",
          "name": "DB21_payload_count_Int",
          "source_path": "payload.count",
          "data_type": "INT",
          "byte_offset": 2,
          "source_enabled": true
        },
        {
          "id": "77777777-7777-4777-8777-777777777777",
          "name": "DB21_payload_temperature_Real",
          "source_path": "payload.temperature",
          "data_type": "REAL",
          "byte_offset": 4,
          "source_enabled": true
        }
      ]
    }
  ]
}
~~~

### 4.1 字段与验证

1. 编码为 UTF-8 无 BOM；恰一顶层对象；拒绝重复 key、未知字段、非法 UTF-8、非整数词法用于整数、隐式转换和未明确允许的 null。必须是精确 format 和整数 schema_version 1；未知主版本拒绝，不猜兼容。文件上限 1 MiB，层级上限 16；单 PLC 最多 32 DB、4096 点，DB/点数量与文件大小都纳入导出预览。超预算整份文件失败，不静默截断。
2. origin 是 PLC 及其 DB/点身份的命名空间：kind 恰为 device_simulator 或 data_acquisition_agent，profile_id 为最初建立该命名空间的 DS 工作区 profile ID 或 DAA 本机实例 ID，plc_id 为该命名空间中的稳定 PLC 身份。它不表示每个点都是该应用创建，也不表示实际物理设备的作者或来源；export 单独记录本次实际导出者。三个字段均必填；ID 使用规范小写 UUID v4。文件名、显示名称、网络地址及 DAA 上报身份都不是 PLC 身份。导入后再从另一应用导出，保留 origin 和已映射的 DB/点身份；经本地显式新增的 DB/点可使用不冲突的本地 UUID v4 作为该命名空间下的新 ID，不改写既有 ID。若 ID 已冲突则阻断并经显式身份处理，不能在只读导出时悄悄换 ID。文件不声明逐点创建者，界面不得把 origin 当成所有点的创建者。
3. export.producer 是本次实际导出应用，v1 恰为 device_simulator 或 data_acquisition_agent；profile_id 是导出方自身的稳定 profile/instance 标识；exported_at 是真实生成时间，RFC 3339 且 +08:00。config_state 对 DS 是 saved_revision；对 DAA 是 active_revision 或 saved_draft。revision_id 对 DS/DAA 已保存版本为原版本 ID，对 DAA 草稿为导出时持久草稿 ETag；payload_sha256 是该应用实际选中保存内容的原始字节 SHA-256，小写 64 位十六进制。草稿 ETag 不冒充不可变 revision。导出者改变后的字段不伪称原程序导出。SHA 是完整性/追溯，不证明来源可信或物理设备正确。
4. plc.name 是非空显示名称，UTF-8 最多 100 字节；protocol 首期固定 s7。connection 为客户端目标：规范 IPv4 单播地址、port 1..65535、rack 0..7、slot 0..31。可选 local_tsap 与 remote_tsap 分别为客户端 calling/called，整数 1..65535；省略时 client local TSAP 为 0x0100，remote TSAP 为 0x0100 加 rack×32 加 slot。DS 监听地址及 TSAP 必须经客户端视角转换和用户确认；通配监听地址不能作为目标，loopback 只对同机有效。DAA 当前无自定义 TSAP 模型，遇非默认值应明确报不兼容并禁止导入执行，不可忽略。
5. dbs 必填且非空。每 DB id 是 UUID v4，number 为 1..65535 且同一 PLC 唯一，name 非空最多 100 UTF-8 字节，size_bytes 为 1..65536；points 必填且非空。DB ID、点 ID 在同一文件全局唯一，不能跨类别复用。每点 id 为 UUID v4，name 为唯一 ASCII 技术名，最多 100 字节且须符合现有命名规则；可选 source_path、display_name、description 分别至多 512/256/500 UTF-8 字节，缺少事实时省略，不从显示名猜原 TIA 名称。
6. data_type 首期显式枚举 BOOL、BYTE、USINT、CHAR、INT、UINT、WORD、DINT、UDINT、DWORD、REAL 和 STRING[n]（n=1..254）。整数/REAL 按 S7 大端，REAL 为 IEEE 754 单精度，STRING 最大长度和编码须明确为 S7 STRING[n] 的 n 与 ASCII；CHAR 为单字节 ASCII。BOOL 必须有 bit=0..7，其他类型禁止 bit；字节宽按类型确定，STRING 占 n+2。必须满足 offset + 宽度不超过 DB 长度，同 DB 的物理占位不能重叠；不同 BOOL 可占同一字节的不同 bit。规则对禁用点也成立，不强推未获证明的 TIA 偏移或优化块布局。
7. source_enabled 只记录本次导出应用的启用事实，其解释依据 export.producer，而不是 origin.kind。DB 层的 source_enabled 是依导出者分型的可选布尔值：DS 导出时必填且如实取该 DB 的 enabled；DAA 当前的 DB 没有独立 enabled 事实，因此 DAA 导出必须省略该字段，不能从 PLC、采集组或点位状态推测。v1 消费者应验证此分型；DB 层缺失表示导出方没有提供此事实，不等于 true 或 false，显式 null 非法。点位层的 source_enabled 在 v1 对 DS 和 DAA 均为必填布尔值：分别取本次导出者的 Point.enabled；点层缺失或 null 为格式错误，不作 true/false 兜底。DS 点位启用与 DAA 的点位采集启用、分组语义不同。DS 文件经 DAA 导入并由 DAA 重新导出时，即使 origin.kind 仍为 device_simulator，也须按实际 export.producer=data_acquisition_agent 表达：DB 层省略，点位层为 DAA 本地实际 enabled；不能把旧 DS DB 启用状态冒称为 DAA 事实。
   这些字段既不是通用写权限，也不自动分配 DAA 采集组或改变 DS 模拟策略；消费者展示导出方、字段实际值或“未提供”，本地启用与引用由本地明确配置决定。点缺少地址、命名未确认、类型未知、物理重叠或不满足本合同：导出器列出具体问题并阻止该实例文件，不丢点、不把它标成默认地址、不因禁用而隐藏错误。首版不提供跳过点的导出模式。
8. 只输出本应用当前实例已经声明并确认的点，包括禁用点；不是对物理 PLC 全部地址的发现。无点的空洞不伪造成点。实际设备布局、源版本、访问许可及连接目标仍由使用者核对；模拟成功不证明真实 PLC 的布局或许可。
9. 可选观察信息和结构树不在 v1 必需合同。DS 可在导出预览显示实际 selected/loaded 事实，但不能据此伪造所选 saved revision。原始 DB/UDT 文件全文或模拟规则不进入该文件。未来如增加可选结构树，必须另定版本与消费者兼容，不能将当前点列表宣称为完整 TIA 源树。

### 4.2 来源版本选择

DS：用户选择一个真实、不可变的 saved revision 及其一个或多个实例；每个文件取该 revision 中对应实例切片。界面同时显示每实例当前 selected 和 actual_loaded 的版本及缺失状态；如果所选 revision 与实际加载不同，突出差异并要求明确确认。不得将 latest、草稿或 selected 冒充 actual_loaded，也不混入未保存编辑或运行值。用户可选择与已验证 actual_loaded 相同的 saved revision；直接从各实例不同 loaded 版本逐个导出的专用模式是后续扩展。

DAA：用户明确选择 active_revision 或已保存的 saved_draft，显示实际标识、来源和活动版本差异；未保存界面编辑不能混入。active 与 runtime loaded/used 分别显示，有差异如实提示。导出并不激活草稿或更改活动版本。两应用导出同一 origin 时，producer、版本和摘要描述当前导出者真实事实。

## 5. 身份映射、重复导入及冲突

1. 可跨文件追溯的外部身份为 origin(kind, profile_id, plc_id) + db.id + point.id；本地身份是 DS/DAA 各自现有 UUID。首次导入新目标时若 ID 在目标 profile 全局可用，可保留；冲突则生成新本地 UUID 并建立持久外部→本地映射，预览清楚显示。用户选择映射到现有 PLC/DB/点时，必须预览并显式确认；不能仅因名称、IP、DB 号或相似地址自动认定为同一身份。
2. 后续来自同一 origin 的导入优先按既有映射识别，稳定保留本地 PLC/DB/点 ID、DAA 采集组、周期、上报配置、样本与历史引用。相同文件再次导入无变化，原草稿 ETag 和版本保持；同外部身份改地址、类型、名称、启用事实或 DB 号均列明前后差异和影响，不能仅因 ID 相同当作无变化。相同 ID 对应不同来源/成员、未知重名、非法范围和物理冲突必须阻断并说明。
3. 文件缺少匹配目标 DB 中原来存在的任一点，或目标 DB 含文件未声明的手工/额外点，首期均作为点集冲突阻断该 PLC 整份导入并保持原草稿，不因其是否已有历史引用而放宽。界面列出具体差异；由使用者先在来源整理一致的目录，或另行申请多来源合并方案。不得在确认后留下无法满足目录点一一对应的配置，也不自动删除、停用、重绑或覆盖旧点。改 DB 号同样先阻断，未选实例和其他 DB 不变。外部地址变化涉及连接目标或物理效果时显式确认，不能改变历史样本的解释。
4. 持久映射必须随目标配置版本保存；预览绑定所选文件原字节 hash、目标、映射、当前 ETag 和有效期。确认时重验，过期、目标变更或并发编辑返回冲突，不产生部分配置、来源归档或半份映射。一个文件不覆盖另一应用的数据库文件。
5. DAA 本地 PLC ID、采集 generation/sequence、样本 ID，以及 HTTP 上报 instanceId/plcId/sourceGeneration 是不同事实；导入目录不创建或替换外部上报绑定、不改历史/队列/原始样本/回执。DAA 样本继续引用本地稳定 ID；外部与本地映射只用于追溯，不声称两个不同历史 ID 自动等价。
6. v1 的一个导出 PLC 只有一个 origin 命名空间；同一目标 PLC 已持久绑定另一外部 origin 时，禁止自动合并、覆盖或将两个 origin 伪装成一个。不同来源均要纳入同一 PLC 时须另立可追溯身份归并设计。此前从未建立外部身份的本地 PLC，可在逐点一一匹配并明确确认后绑定首次输入的 origin；原本地 ID 与历史仍保持。DS/DAA 未建立外部身份的原生 PLC 首次导出以自己的 profile 和本地 PLC ID 构造稳定命名空间。

## 6. DS 导出与导入设计

### 6.1 DS 导出

导出入口以实例列表为起点，可多选并选择同一 saved revision，预览所选实例的来源版本、实际 loaded、连接目标、每个 DB/点及问题。源自 DS 的 id、name、type、byte/bit、DB number/length 和来源路径按实际事实映射。所有点含停用点均按合同验证；确认或地址缺失时给出 DB/点定位并阻止该实例。初值、规则、权限、在线值不进入交换合同。

用户提供或确认采集客户端可达的 client host/port；不能把 0.0.0.0 作为远端连接目标，跨机器不能把 127.0.0.1 误当远端地址。TSAP 显示服务端与客户端方向并按既有合同核对。文件的导出成功不证明目标已连接、模拟正在运行或点值正确。

### 6.2 DS 从目录导入

输入可为 DS 或 DAA 导出的同格式文件。用户选择新建或匹配现有 DS 实例，预览并确认映射、DB/点、已有策略及冲突；只写 DS 草稿，按 DS 原有版本保存、加载流程处理，不启动。该能力尚未实现，可作为独立实施切片，与 DS→DAA 路径分别验证。

文件中的 connection 是 client 连接目标，尤其 DAA 导出的地址可能是真实 PLC：**不得把它自动作为 DS 本机监听地址，也不得连接该地址。** 用户必须显式填写并确认自己的模拟监听 IP/端口及 rack/slot；冲突时拒绝。新实例默认不启动；模拟初值、规则、客户端读取/写入许可分别由用户在 DS 确认，不从 DAA 采集启用状态推导。目录点的来源被明确标记为 catalog，缺少原 TIA 结构时不伪造 DB/UDT 文件或完整来源树；维护一致的本地/外部身份映射及 DS 自身布局/命名确认。现有实例的规则、初值、权限和历史版本默认保留，冲突先预览，不能覆盖无关对象。


DS 的目录导入实施还需形成明确的 catalog 来源分型：保存并哈希用户选中的原始 JSON；同一实例的多个 DB 可引用同一份源版本，各 DB 分别绑定 sourceVersionId、原字节 SHA、originDbId 以及外部点 ID → 本地点 ID 的映射。外部 origin 和映射随工作区草稿/版本持久保存；catalog 绑定与既有 TIA SourceBinding 分型明确且不相互冒充。验证时重验源版本、SHA、origin、DB/点身份、完整点集、类型与物理地址；缺失、重复、越界、点集冲突或来源不一致阻断，不能退回未校验的手工点路径。没有原 TIA 文件时不伪造 DB/UDT 来源、结构树或初始值；DS 自身的名称/地址签名及加载前确认仍须由用户完成。

导入目录后若在 DS 修改目录 DB 的点集或地址，须显式预览并确认，生成绑定前一来源 SHA 的不可变内部点集快照；该快照标识为 DS 本地生成，不冒充外部交换文件，也不包含当前配置自身的 revision/SHA，避免自引用。新草稿以新快照重新建立完整映射，其他 DB、原始输入和历史版本保留；新点使用不冲突 UUID、原点身份不变。重新导出仍是同一个候选交换格式，并如实记录 DS 作为本次 producer。

优先评估使用现有 source_versions 和可选配置元数据且保持原 DDL；新旧二进制、已保存版本/原 SHA、selected/loaded 与回退必须单独验证。若需要修改物理库结构或迁移已用 profile，停止对应实现并另立明确的 schema-maintenance 与采用审批。

## 7. DAA 导入：无需再提供 DB/UDT

### 7.1 来源分型和完整性

DAA 现有配置的 Db.source_id 指向逻辑 SourceDocument，启用点还要匹配 Db.tree 中的叶及 type；SourceDocument 内容须与 SHA 一致。这是当前事实，不能只把目录点转成空树并关闭校验，也不能伪造 .db/.udt 内容、文件名或 TIA 源行。

拟议做法优先复用 DAA-005/006 的 **schema 1 可选字段、旧 DDL 不变**先例：

- 在配置 JSON 添加可选 catalog bindings，字段缺失表示原有 DB/UDT 或旧配置，读取旧 payload 不写回；按本地 DB ID 关联实际 catalog 逻辑 source ID、源原字节 SHA、外部 origin/DB ID 及外部点 ID → 本地点 ID 映射。保留原有 Point 的稳定身份和样本字段结构，避免把绑定元数据塞入每个 PointFact。
- 实际导入 JSON 作为明确的 catalog SourceDocument，保存用户所选原始 UTF-8 内容及 SHA。一个 PLC 导入的一份文件建立一个逻辑 source；该 PLC 多个 DB 的 source_id 可以共同指向此 source，由每个 DB 的 catalog binding 精确标识文件中的对应 DB。不同 PLC 的逻辑 source 各自独立；同 SHA、同字节的物理归档按现有策略复用，不覆盖旧归档。共享单一逻辑 source 避免每 DB 重复一份大 JSON 而突破配置容量。source_id 始终指向真实目录源，而非伪造 TIA 源。
- 对有 catalog binding 的 DB 执行目录专用完整性验证：解析并重验文件版本、原字节 SHA、origin、DB/点 ID、名称、类型、地址及占位；本地映射必须一一对应，不允许缺失、重复、跨 PLC、改写绑定或引用文件未声明的点。当前 DB 关联源校验中对 db_number/原 importBinding 的要求，在 catalog 分支以完整的目录 DB 关联校验替代；旧来源分支的原逻辑不变。source_path 如文件没有该事实则保持缺失语义，不伪装为 TIA 路径；目录点可在本地视图展示有事实的来源路径和单独的目录身份。
- catalog 的完整性表示“已完整验证该 JSON 声明的点集”，不表示已验证 TIA 工程完整树。目录分支可将 Db.complete 用作目录完整性准入，Db.tree 可以为空；UI 明示来源是目录点列表，不生成假树或声称可恢复原源文件。对原 DB/UDT 来源，原 Db.tree、leaf_matches、source/UDT 闭包和地址校验完全保留；只在显式 catalog 分型下使用等强度的目录成员核对。
- 导入确认后地址及确认依据明确记录为目录来源与用户确认；若现有 origin 枚举无法如实表达，需在后续受批实现中增加清晰的 catalog 类型并核对样本定义和上报兼容，不能谎写为 TIA 自动推算。对后续手工改地址/类型，必须要求明确的本地覆盖确认，保留原目录和修改前值；激活校验对照原目录加明确覆盖，而不是绕开校验。覆盖及其重新导出语义须在实施切片冻结并有负例。
- 只新增可选配置元数据并不能自动证明兼容：现有 serde deny_unknown_fields 的旧二进制可能拒绝新 payload。必须验证新版本零写读取旧草稿/版本/样本、原字节/hash 不变；旧版本碰到新 catalog 元数据须安全拒绝，不得静默启动错误配置或生成空库。降级前停止自有采集并保留完整 profile；只在证明兼容的副本或原备份上回退，禁止覆盖真实历史。
- 当前 configuration_revisions 和 configuration_contexts 的物理 schema 对配置 payload schema_version 均有 CHECK=1。若验证证明上述 v1 可选字段方案不能满足完整性、性能或兼容性，则停止该实现切片，提出独立的 schema-maintenance Revision，明确双库兼容、升级前备份、中断恢复、旧记录不重写、回退和真实 profile 采用审批；不得把 schema 2 或 DDL 当成本设计已授权的自动迁移。

拟议的 DAA 配置 JSON 扩展是可省略的 catalogBindings 列表。每项包含 localDbId、sourceId、sourceSha256、sourceKind、originDbId 和 pointMappings；每个 pointMapping 包含 localPointId、catalogPointId，可选 localOverride。sourceKind 明确区分外部 exchange_json 和下文的 local_snapshot，按对应封闭格式分别校验。其所属本地 PLC 从 localDbId 关联到本地 DB 后核对，不信任输入另填的 PLC。sourceId 必须属于同一 PLC，sourceSha256 必须等于该 SourceDocument 原字节摘要，originDbId 必须在相应外部文件或内部快照中唯一存在；所有 localPointId/catalogPointId 在本映射中分别唯一，且两侧点集必须完整一一对应。两个 DB 不得引用同一 originDbId；同一外部文件的一次导入在一个本地 PLC 只使用同一逻辑 sourceId，跨 PLC 则分别持有逻辑来源。

localOverride 仅用于使用者在 DAA 显式修改目录点的地址或类型：含该次确认所依据的 sourceSha256、修改后的 dataType/offset/可选 bit、用户确认原因。无 override 时本地点的类型/地址必须与归档 JSON 一致；有 override 时必须匹配已确认覆盖，且重新执行类型、DB 长度、bit 和跨点重叠校验。源文件重新导入后若原点类型/地址与覆盖基准发生变化，预览列出冲突并暂停该点更新，由用户明确保留覆盖或采用新值；不得悄悄以旧覆盖套用新源。DAA 导出采用所选已保存配置中的实际有效点位，保留 origin 和点 ID，并以本次 DAA 配置 revision/SHA 如实标明新的 exporter 来源，不把覆盖值谎称来自旧原始文件。名称、显示信息和分组的变更仍分别走既有命名及草稿保护。

在已导入 catalog 的 DB 里新增本地点时，不得仅修改 pointMappings 而继续指向不含该点的旧文件。拟提供明确的本地目录修订操作：在预览确认后基于当前已验证目录、有效覆盖和新点生成该 DB 的不可变内部点集快照，格式标记为 daa.catalog_snapshot，含 origin、originDbId、原 source SHA 和完整点集，单独算 SHA 并归档；新草稿内该 DB binding 指向此快照且重新建立完整一一对应。该快照是 DAA 生成的内部来源材料，不冒充原 DS 文件或 DB/UDT，不携带当前配置自身的 revision/SHA，因此不产生配置与自身摘要的循环引用。其他 DB 可以继续指向原交换文件；更新源、绑定及草稿在同一事务提交。追加点沿用原命名空间但不声称由 DS 创建；用不冲突的本地 UUID v4 作外部点 ID，既有映射不变。导出时才从所选已保存 DAA 配置生成统一交换 JSON，并正确填写 DAA 的实际版本/SHA。内部快照不作为跨应用合同公开，也不覆盖先前原始文件或历史 revision。

为支持无需 DB/UDT 导入的有效地址，目录导入经用户预览确认后，Address.confirmed 才为 true，拟议新增 origin 值 catalog 和明确的确认原因；手工覆盖仍保留独立的手工来源。此值只能用于具备有效 catalog binding 的点。因 PointFact 包含 Address 定义，新值会出现于后续新样本的本地定义中：实施时必须验证 DAA 原有历史解码及事实 v2 上报契约兼容，保留所有既有样本字节和已冻结上报内容；若外部合同不接受该值，返回 PM 另定范围。读取和解析目录本身不构成对真实 PLC 布局的验证。保存前还要核算单个源、完整配置 JSON、归档和容量预算；超限时明确拒绝且无部分写入，不能因为单文件小于 1 MiB 就假定目标配置一定可容纳。

### 7.2 DAA 导入体验与采集准入

选择文件后，新建 PLC 或选择现有 PLC，预览同一文件的连接、DB、所有点、来源、变更、不可支持项及映射。导入确认可复用文件中已确认地址，但仍须本地明确用户确认；目标真实 PLC 地址需现场资料核对。首次新建的点默认不自动开始采集。用户可以在导入预览中选择现有采集组，或显式新建组并填写周期，一次批量分配选中的受支持点；同 PLC/DB 的启用点遵守现有 DAA runtime 分组规则、资源预算与数量上限。未选择的点保留并显示为未分组/停用。

确认仅提交到草稿；用户可随后显式激活配置、连接并采集。端到端验收必须证明：**文件和 DAA 新空隔离 profile 足够，不额外提供或重新导入 .db/.udt**；由 DS 受控模拟器提供 BOOL、INT、REAL 可读值，DAA 一次分组后保存、激活、真实读取并核对采样点 ID、地址、类型、值和质量。失败有具体原因；不能以解析 JSON 或纯内存单测代替此闭环。旧配置和运行任务按原路径工作。

### 7.3 DAA 导出

按 PLC 多选、每台一文件，从用户选择的 saved_draft 或 active_revision 生成上述共同合同；仅导出该配置中已声明且可通过合同完整性检查的 DB/点。未确认地址或类型问题必须逐点报告并阻止该实例，不能用停用状态掩盖。重导本地由目录输入的配置时保留外部 origin 和稳定 ID 映射，并如实记录 DAA 作为导出者及选定配置版本；未绑定外部命名空间的 DAA 自建 PLC 以自身 profile/PLC 建立稳定身份，已绑定 origin 下新增点沿用该命名空间但不冒称来源。DAA 的 DB 没有独立启用字段，导出时省略该层 source_enabled；每个点的 source_enabled 必须取当前 DAA 配置中的 Point.enabled，即使来源命名空间是 DS 也不能沿用源文件的旧启用值。采集组、周期、运行历史、队列、上报设置及凭据不进入 JSON。



## 8. 拟议实施次序与任务归属

| 阶段 | 拟议范围 | 进入和退出边界 |
| --- | --- | --- |
| P0 | 本 AW 规格：同一完整 S7 JSON、两应用导入导出、来源及兼容设计 | r2 设计范围已批准；没有代码批准 |
| P1 | DS 按实例导出 + DAA 按实例导入，并验证 DS→DAA 无原 DB/UDT 的受控采集 | 先有精确实施任务/Revision、allowlist 与 Human Owner 批准 |
| P2 | DAA 按实例导出及 DAA→DAA 目标导入 | 同格式、完整点集、已保存状态与来源身份独立验证 |
| P3 | DS 按实例导入同格式文件，包括 DAA→DS 和 DS→DS | 显式模拟监听端点；独立验证，不自动启动或连接 |
| 后续 | 共享合同正式发布或其他协议、真实设备及现场采用 | 分别立项、精确批准；不修改本轮根 contracts |

P1/P2/P3 可据最终审批切片推进；设计覆盖两端导入和导出，但某切片的实现/验证不替代其他切片。仅有格式测试或单端导入不构成 DS→DAA 采集闭环。实际实现继续遵循 STD，按受影响表面使用 aiis、plc-point-mapping、rust-runtime、desktop-tauri、frontend-ui、i18n-workflow 和 code-document-indexer；若修改产品持久 schema，须先处理独立维护 gate。

## 9. 拟议验收标准

下列为未来经批准的软件范围设计口径，不是已完成证据；各切片确定精确 AC 和真实验证环境。

| 编号 | 可观察标准 |
| --- | --- |
| AC01 | 一台 PLC 一份完整 JSON；多选两台分别生成，实例、DB、点不串；取消、冲突和部分失败正确报告且无半文件。 |
| AC02 | 候选示例及多 DB 正例按冻结的格式验证；重复键、未知版本/字段、非法编码/类型/UUID、超限、缺字段、BOOL bit、STRING 宽度、越界与重叠有可复现负例。 |
| AC03 | DS saved/selected/actual_loaded 与 DAA saved_draft/active/loaded/used 各自准确呈现；实际版本和原 payload SHA 如实追溯，不混未保存编辑。 |
| AC04 | DS 包含 BOOL、INT、REAL、STRING 及停用点时导出完整声明；地址或名称未确认、未知类型、结构错误均定位并阻断该实例，无默认值和静默漏点。 |
| AC05 | DS JSON 导入全新隔离 DAA profile 无须 .db/.udt；显式分组、保存和激活后，以隔离 DS S7 模拟完成 BOOL/INT/REAL 真实读取，核对 ID、地址、类型、值与质量。 |
| AC06 | DAA 目录来源原字节/SHA、source_id、DB 和点位映射完整一致；伪造源、错 hash、错成员/类型/地址和重复绑定拒绝；旧 DB/UDT 的 tree/leaf_matches 验证不减弱。 |
| AC07 | DAA→DAA 使用同一完整文件，在新目标预览和确认，保留身份来源、完整点集；分组和周期由目标用户选择，确认前不修改草稿或连接设备。 |
| AC08 | DAA 按实例支持 saved_draft/active_revision 导出，多选分别生成；来源为 DS 时仍以 DAA 作为实际 producer，DB 层无 source_enabled，点位层取 DAA 实际 Point.enabled。 |
| AC09 | DS DB/点启用分别取 DS 实际值；DAA DB 层缺失表示未提供，不能默认 true/false；两应用的点位 source_enabled 必填，缺失、null 和与 producer 不相容的字段拒绝。 |
| AC10 | DAA 导出文件导入 DS 时不得复用文件中的客户端目标作为模拟监听；操作者显式确认新的本机监听地址，之后按 DS 版本流程配置，导入本身不启动或连接。 |
| AC11 | 对已有目标，重复导入保持 ETag 与本地 ID；文件缺点、额外点、跨 origin、ID 冲突或变更地址等均可见并按规定阻断或明确确认；整 PLC 提交原子。 |
| AC12 | 采集组、周期、DS 规则与历史版本、DAA 既有本地 ID、样本、generation/sequence、上报绑定、pending/ACK 及未选实例不被静默覆盖或改写。 |
| AC13 | 已导入目录的 DS 或 DAA 本地点集变更产生对应应用的可核验内部快照和稳定映射，外部原文件及历史 revision 原字节保留；来源变化、地址修改与手工覆盖冲突先预览。 |
| AC14 | 新版本读取旧 payload 零写回；旧二进制遇新目录元数据不会静默运行错误配置；任何必须的物理 DDL、迁移和真实 profile 采用先取得独立批准并验证中断/回退。 |
| AC15 | wildcard、loopback、非默认 TSAP、取消/并发、路径、文件替换和多个实例有可观察负例；模拟结果不外推真实 PLC。 |
| AC16 | 两端原有启动、草稿、版本和权限行为保持；新增可见文案双语对称，表格列宽遵循公共规则；项目测试、原生/跨平台/现场证据如实分层。 |

## 10. 边界、风险和待审事项

- 同一完整文件不等于物理 PLC 全部地址已被发现，也不证明设备实际布局。地址和可达目标必须用户核对；不含凭据或授予写权限的信息。
- 目录身份和生产运行身份不同。不同 origin 的 PLC 不自动归并；历史样本、回执、DB/UDT 归档和旧任务已批准状态保持。
- DAA 可选字段、目录来源分型及 DS 目录绑定均为设计候选，须以产品源码和隔离闭环验证；若需物理 DDL/旧 profile 迁移，另立 schema-maintenance 和采用 gate。
- 按 Human Owner 本轮要求，设计包含两端导入和导出；具体实施顺序仍在精确实施任务中决定。合成/本机验证不等于跨平台、现场、生产部署或长期运行验收。

Human Owner 已批准 r2 的设计范围；后续软件实施必须有各自单独的精确范围与批准。当前不创建 Development tasks 或 Verification checklist。

## 11. 修订与 PM 检查

### r2 设计范围批准记录

2026-11-16（Asia/Shanghai），Human Owner 明确表示：

> 可以，批准 ARCH-PLC-001 r2 设计范围。接下来按 STD 拆分 DS 和 DAA 的实施任务，优先考虑 DS 导出、DAA 导入；FF 后续单独适配，暂不修改代码。

该决定批准 ARCH-PLC-001 精确 r2 的设计范围。用户审阅时、登记前完整规格原始 SHA256 为 48d2415e9d6a6e41ff0996f8da1c64ca748067b28975be81382ae455c605987c；本记录仅更新 PM 状态与批准说明，不改变已批准设计范围、验收、风险或 r1 原文。DS-003 与 DAA-017 各为独立实施规格草案，仍需 Human Owner 逐项精确批准后才可进入 Development；设计独立验证及 Human Owner 最终验收仍未发生。此决定不批准源码、测试、合同发布、真实数据库迁移或现场设备动作。

r1 为未获批准的跨应用草案。本轮按 Human Owner 指示移入 AW、收敛至 DS 与 DAA 并形成 r2 draft；原 r1 逐字节封存于下方附录，封存内容及其中路径均为历史，不是当前规则。此轮不执行软件、数据库、真实设备或项目测试；文档静态核验由 PM 在交接时如实报告。

## 附录 A：r1 未批准草案完整原文（历史，非当前合同）

原始 spec.md SHA256: 2b242fad628e2b67ca61f44c58f195485315a204e58fe1c497d3984656734de6。下方围栏首行之后至闭合围栏之前为原始 UTF-8 字节；保留原末尾换行，可按此边界无损提取。

~~~~~~~~~~~~markdown
Task ID: ARCH-PLC-001
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS、DAA 与 FF 的逐 PLC 点位 JSON 交换合同和兼容详细设计
Owner: AIIS ICS 跨运行时合同 / DS、DAA、FF 各自模块
Acceptance Chain Reference: 本任务遵循仓库 Development Lifecycle Workflow；Human Owner 审阅精确设计 Revision，后续文档 Development、fresh-context Verification 和 Human Owner 最终验收各为独立 gate。
Related Task: device-simulator::DS-002; data-acquisition-agent::DAA-005; data-acquisition-agent::DAA-006; data-acquisition-agent::DAA-010; data-acquisition-agent::DAA-013; field-flow::FF-004

# 跨 DS、DAA、FF 的逐 PLC 点位 JSON 详细设计

## 1. 当前请求、任务状态和决策范围

2026-11-16，Human Owner 要求先将 DS、DAA 和 FF 共用的 PLC 点位 JSON 格式、按实例导入导出及 FF 兼容方案整理成详细设计，按 STD 先走 PM，暂不改代码。目标是：DS 已导入 DB/UDT、确认地址并完成模拟后，可选 PLC 实例逐台导出；同一份文件导入 DAA、交 FF 加载；DAA 也能按实例导入及导出。DAA 整理真实 PLC 时也可导出给 FF，减少重复录入。

本文件是 PM 的具体设计提案，状态 draft；所有示例、接口、模型调整、测试和分阶段实施均为拟议，不能冒称功能已存在。此轮只写本任务 spec，计划索引由主协调按实际状态机械同步；不写其他现有任务、代码、配置、合同、数据库或真实数据。不创建 tasks/checklist，不启动应用、设备或联网。用户已允许 PM 设计，尚未批准本 Revision、实现、QA、生产采用或任何真实数据库操作。

**设计任务与软件实施分开。** 本 Revision 只提交设计和候选合同供审阅；合同正式公开、DS/DAA/FF 代码、可能需要的 SQLite schema-maintenance、已有 profile 采用、设备/现场和部署分别需未来明确范围与批准。设计审阅或文档最终验收不自动批准任何代码、schema 变更、发布或设备行为。各实施切片需要自己的精确文件范围、验收和 STD gate；若在本任务后续 Revision 承担实施，须先明确 allowlist 并重新批准，不从本文件示例推断授权。

选择本根任务是因为合同与消费方跨 automation-world 和 field-flow，不继承 DS-002、DAA-005/006、DAA-010/013 或 FF-004 的既有批准和验收。本任务只引用它们作为相关现状，不改写其权威记录。

## 2. 当前事实与设计目标

| 事实 | 可观察依据及边界 |
| --- | --- |
| DS 可配置多个实例、DB 和点位，可导入 DB/UDT，分别保存草稿、保存不可变工作区版本、选择并实际加载实例版本；当前无 FF 目录导出器 | [DS 操作手册](../../automation-world/device-simulator/USER_GUIDE.zh-CN.md)、[DS-002 设计](../../automation-world/device-simulator/plans/DS-002-multi-protocol-simulation-and-device-debugging/spec.md)、[DS 模型](../../automation-world/device-simulator/runtime/src/domain/configuration.rs)；DS-002 是 draft，导出属于后续设计 |
| DAA 当前导入入口是 .db/.udt，已有多 DB 和偏移确认；每个启用点需要来源、地址和采集组 | [DAA 导入入口](../../automation-world/data-acquisition-agent/src/app/plc/components/SourceImportPanel.vue)、[DAA 配置模型及校验](../../automation-world/data-acquisition-agent/src-tauri/src/domain/local_configuration.rs)、[DAA-005](../../automation-world/data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md)、[DAA-006](../../automation-world/data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/spec.md) |
| DAA source_documents、配置草稿/版本和 runtime 上下文是独立持久事实；已存在相同内容的全局物理归档去重及逻辑来源隔离先例 | [本地存储说明](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md)、[存储 schema](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs)；样本、上报、回执及 ID 有自身历史合同 |
| FF-004 r2 A 的 Rust 仅接收旧 ff.plc v1 严格封闭格式，S7 仅 INT16，所有声明包括禁用/未引用点均校验；Modbus 仅结构校验 | [FF 格式说明](../../field-flow/field-flow-rust/config/plcs/README.zh-CN.md)、[FF-004](../../field-flow/plans/FF-004-plc-json-catalog-and-multi-plc/spec.md)；Python/C# 新目录加载与 DS 导出不在已接受切片 |
| 根 contracts 是跨运行时合同中心 | [合同说明](../../contracts/README.zh-CN.md)；此 spec 中的 JSON 仍是拟议合同，不是已发布 schema |

验收目标是两个明确的离线交换路径：

1. DS 导出一个包含 BOOL、INT、REAL 等已确认点位的 PLC JSON；DAA 不再要求 .db/.udt 原文件，完成必要采集组配置后，能保存、激活、连接受控模拟器并采集。
2. 同一文件可由扩展后的 FF Rust 直接加载、列示全部点位，并对已支持的 INT 点正常引用；DAA 导出同合同文件也可被相同 FF 消费。文件交接不要求源程序在线或共享 SQLite。

DS 从 DAA 导出的文件反向导入在本设计内给出方案，作为独立后续实施切片；不作为前两条路径的前置条件。首期合同为 S7 标准 DB；Modbus 及其运行、Python/C# 新格式加载、真实 PLC、现场运行均不由本设计承诺。

## 3. 文件边界与整体工作流

- 一个 JSON 文件恰包含一个逻辑 PLC、一个协议连接描述、一个或多个 DB 和每个 DB 已声明的点位。导出界面可勾选多个实例，分别生成每实例一个文件；不把多个 PLC 包进同一 JSON。
- 同一文件是离线交换材料，携带已整理的点位声明，不是实时值、采集计划、模拟脚本、后端事实或控制指令。DS 与 DAA 各自管理自己的草稿、不可变版本、配置数据库和执行状态；不存在共享写库或跨程序自动同步。
- 导出是对所选已持久状态的静态快照；用户显式选目录、核对文件名和来源版本。每份文件先完整生成并校验再原子落盘；重名逐项给出覆盖选择，取消/失败不能留下半文件。批量操作逐实例报告成功/失败和原因，不把部分成功标为全部成功。
- 导入按文件及目标实例预览、确认，显示设备与连接、版本、DB 数、点数、类型和变化。单个目标的提交是原子操作；批量导入逐目标报告。预览不写，确认只修改目标应用的草稿，不自动连接、启动、激活、上报或更改其余实例。
- JSON 不含密码、token、环境文件、数据库路径、在线值、DS 初值/规则/写授权、DAA 采集周期/队列/历史/上报凭据或 FF 业务逻辑。各端维护自身配置；文件来源或某模拟设置不授予真实 PLC 写权限。

## 4. 候选 JSON v1：单台 S7 PLC

本节是供 Human Owner 审阅的候选，格式标识与现有 FF 的 ff.plc 不同。正式合同拟在后续获批时归根 contracts，发布前须有结构定义、规范样例、错误向量与消费者兼容证据；本轮不创建正式文件。下例所有 ID、摘要和端口均为合成示例，摘要仅展示词法，不声称与任何实际数据对应。

~~~json
{
  "format": "aiis.plc_points",
  "schema_version": 1,
  "origin": {
    "kind": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "plc_id": "22222222-2222-4222-8222-222222222222"
  },
  "export": {
    "producer": "device_simulator",
    "profile_id": "11111111-1111-4111-8111-111111111111",
    "config_state": "saved_revision",
    "revision_id": "33333333-3333-4333-8333-333333333333",
    "payload_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "exported_at": "2026-11-16T11:00:00+08:00"
  },
  "plc": {
    "name": "PLC_A",
    "protocol": "s7",
    "connection": {
      "host": "127.0.0.1",
      "port": 31281,
      "rack": 0,
      "slot": 1
    }
  },
  "dbs": [
    {
      "id": "44444444-4444-4444-8444-444444444444",
      "name": "MinimalImport",
      "number": 21,
      "size_bytes": 8,
      "source_enabled": true,
      "points": [
        {
          "id": "55555555-5555-4555-8555-555555555555",
          "name": "DB21_payload_ready_Bool",
          "source_path": "payload.ready",
          "data_type": "BOOL",
          "byte_offset": 0,
          "bit": 0,
          "source_enabled": true
        },
        {
          "id": "66666666-6666-4666-8666-666666666666",
          "name": "DB21_payload_count_Int",
          "source_path": "payload.count",
          "data_type": "INT",
          "byte_offset": 2,
          "source_enabled": true
        },
        {
          "id": "77777777-7777-4777-8777-777777777777",
          "name": "DB21_payload_temperature_Real",
          "source_path": "payload.temperature",
          "data_type": "REAL",
          "byte_offset": 4,
          "source_enabled": true
        }
      ]
    }
  ]
}
~~~

### 4.1 字段与验证

1. 编码为 UTF-8 无 BOM；恰一顶层对象；拒绝重复 key、未知字段、非法 UTF-8、非整数词法用于整数、隐式转换和未明确允许的 null。必须是精确 format 和整数 schema_version 1；未知主版本拒绝，不猜兼容。文件上限 1 MiB，层级上限 16；单 PLC 最多 32 DB、4096 点，DB/点数量与文件大小都纳入导出预览。超预算整份文件失败，不静默截断。
2. origin 是 PLC 及其 DB/点身份的命名空间：kind 恰为 device_simulator 或 data_acquisition_agent，profile_id 为最初建立该命名空间的 DS 工作区 profile ID 或 DAA 本机实例 ID，plc_id 为该命名空间中的稳定 PLC 身份。它不表示每个点都是该应用创建，也不表示实际物理设备的作者或来源；export 单独记录本次实际导出者。三个字段均必填；ID 使用规范小写 UUID v4。文件名、显示名称、网络地址及 DAA 上报身份都不是 PLC 身份。导入后再从另一应用导出，保留 origin 和已映射的 DB/点身份；经本地显式新增的 DB/点可使用不冲突的本地 UUID v4 作为该命名空间下的新 ID，不改写既有 ID。若 ID 已冲突则阻断并经显式身份处理，不能在只读导出时悄悄换 ID。文件不声明逐点创建者，界面不得把 origin 当成所有点的创建者。
3. export.producer 是本次实际导出应用，v1 恰为 device_simulator 或 data_acquisition_agent；profile_id 是导出方自身的稳定 profile/instance 标识；exported_at 是真实生成时间，RFC 3339 且 +08:00。config_state 对 DS 是 saved_revision；对 DAA 是 active_revision 或 saved_draft。revision_id 对 DS/DAA 已保存版本为原版本 ID，对 DAA 草稿为导出时持久草稿 ETag；payload_sha256 是该应用实际选中保存内容的原始字节 SHA-256，小写 64 位十六进制。草稿 ETag 不冒充不可变 revision。导出者改变后的字段不伪称原程序导出。SHA 是完整性/追溯，不证明来源可信或物理设备正确。
4. plc.name 是非空显示名称，UTF-8 最多 100 字节；protocol 首期固定 s7。connection 为客户端目标：规范 IPv4 单播地址、port 1..65535、rack 0..7、slot 0..31。可选 local_tsap 与 remote_tsap 分别为客户端 calling/called，整数 1..65535；省略表示 FF-004 既定默认值。DS 监听地址及 TSAP 必须经客户端视角转换和用户确认；通配监听地址不能作为目标，loopback 只对同机有效。DAA 当前无自定义 TSAP 模型，遇非默认值应明确报不兼容并禁止导入执行，不可忽略；FF Rust 当前运行亦只支持默认 TSAP。
5. dbs 必填且非空。每 DB id 是 UUID v4，number 为 1..65535 且同一 PLC 唯一，name 非空最多 100 UTF-8 字节，size_bytes 为 1..65536；points 必填且非空。DB ID、点 ID 在同一文件全局唯一，不能跨类别复用。每点 id 为 UUID v4，name 为唯一 ASCII 技术名，最多 100 字节且须符合现有命名规则；可选 source_path、display_name、description 分别至多 512/256/500 UTF-8 字节，缺少事实时省略，不从显示名猜原 TIA 名称。
6. data_type 首期显式枚举 BOOL、BYTE、USINT、CHAR、INT、UINT、WORD、DINT、UDINT、DWORD、REAL 和 STRING[n]（n=1..254）。整数/REAL 按 S7 大端，REAL 为 IEEE 754 单精度，STRING 最大长度和编码须明确为 S7 STRING[n] 的 n 与 ASCII；CHAR 为单字节 ASCII。BOOL 必须有 bit=0..7，其他类型禁止 bit；字节宽按类型确定，STRING 占 n+2。必须满足 offset + 宽度不超过 DB 长度，同 DB 的物理占位不能重叠；不同 BOOL 可占同一字节的不同 bit。规则对禁用点也成立，不强推未获证明的 TIA 偏移或优化块布局。
7. source_enabled 只记录本次导出应用的启用事实，其解释依据 export.producer，而不是 origin.kind。DB 层的 source_enabled 是依导出者分型的可选布尔值：DS 导出时必填且如实取该 DB 的 enabled；DAA 当前的 DB 没有独立 enabled 事实，因此 DAA 导出必须省略该字段，不能从 PLC、采集组或点位状态推测。v1 消费者应验证此分型；DB 层缺失表示导出方没有提供此事实，不等于 true 或 false，显式 null 非法。点位层的 source_enabled 在 v1 对 DS 和 DAA 均为必填布尔值：分别取本次导出者的 Point.enabled；点层缺失或 null 为格式错误，不作 true/false 兜底。DS 点位启用与 DAA 的点位采集启用、分组语义不同。DS 文件经 DAA 导入并由 DAA 重新导出时，即使 origin.kind 仍为 device_simulator，也须按实际 export.producer=data_acquisition_agent 表达：DB 层省略，点位层为 DAA 本地实际 enabled；不能把旧 DS DB 启用状态冒称为 DAA 事实。
   这些字段既不是通用写权限，也不自动分配 DAA 采集组、改变 DS 模拟策略或成为 FF 的引用许可；消费者展示导出方、字段实际值或“未提供”，本地启用与引用由本地明确配置决定。点缺少地址、命名未确认、类型未知、物理重叠或不满足本合同：导出器列出具体问题并阻止该实例文件，不丢点、不把它标成默认地址、不因禁用而隐藏错误。首版不提供跳过点的导出模式。
8. 只输出本应用当前实例已经声明并确认的点，包括禁用点；不是对物理 PLC 全部地址的发现。无点的空洞不伪造成点。实际设备布局、源版本、访问许可及连接目标仍由使用者核对；模拟成功不证明真实 PLC 的布局或许可。
9. 可选观察信息和结构树不在 v1 必需合同。DS 可在导出预览显示实际 selected/loaded 事实，但不能据此伪造所选 saved revision。原始 DB/UDT 文件全文或模拟规则不进入该文件。未来如增加可选结构树，必须另定版本与消费者兼容，不能将当前点列表宣称为完整 TIA 源树。

### 4.2 来源版本选择

DS：用户选择一个真实、不可变的 saved revision 及其一个或多个实例；每个文件取该 revision 中对应实例切片。界面同时显示每实例当前 selected 和 actual_loaded 的版本及缺失状态；如果所选 revision 与实际加载不同，突出差异并要求明确确认。不得将 latest、草稿或 selected 冒充 actual_loaded，也不混入未保存编辑或运行值。用户可选择与已验证 actual_loaded 相同的 saved revision；直接从各实例不同 loaded 版本逐个导出的专用模式是后续扩展。

DAA：用户明确选择 active_revision 或已保存的 saved_draft，显示实际标识、来源和活动版本差异；未保存界面编辑不能混入。active 与 runtime loaded/used 分别显示，有差异如实提示。导出并不激活草稿或更改活动版本。两应用导出同一 origin 时，producer、版本和摘要描述当前导出者真实事实。

## 5. 身份映射、重复导入及冲突

1. 可跨文件追溯的外部身份为 origin(kind, profile_id, plc_id) + db.id + point.id；本地身份是 DS/DAA 各自现有 UUID。首次导入新目标时若 ID 在目标 profile 全局可用，可保留；冲突则生成新本地 UUID 并建立持久外部→本地映射，预览清楚显示。用户选择映射到现有 PLC/DB/点时，必须预览并显式确认；不能仅因名称、IP、DB 号或相似地址自动认定为同一身份。
2. 后续来自同一 origin 的导入优先按既有映射识别，稳定保留本地 PLC/DB/点 ID、DAA 采集组、周期、上报配置、样本与历史引用。相同文件再次导入无变化，原草稿 ETag 和版本保持；同外部身份改地址、类型、名称、启用事实或 DB 号均列明前后差异和影响，不能仅因 ID 相同当作无变化。相同 ID 对应不同来源/成员、未知重名、非法范围和物理冲突必须阻断并说明。
3. 文件缺少匹配目标 DB 中原来存在的任一点，或目标 DB 含文件未声明的手工/额外点，首期均作为点集冲突阻断该 DB 的导入并保持原草稿，不因其是否已有历史引用而放宽。界面列出具体差异；由使用者先在来源整理一致的目录，或另行申请多来源合并方案。不得在确认后留下无法满足目录点一一对应的配置，也不自动删除、停用、重绑或覆盖旧点。改 DB 号同样先阻断，未选实例和其他 DB 不变。外部地址变化涉及连接目标或物理效果时显式确认，不能改变历史样本的解释。
4. 持久映射必须随目标配置版本保存；预览绑定所选文件原字节 hash、目标、映射、当前 ETag 和有效期。确认时重验，过期、目标变更或并发编辑返回冲突，不产生部分配置、来源归档或半份映射。一个文件不覆盖另一应用的数据库文件。
5. DAA 本地 PLC ID、采集 generation/sequence、样本 ID，以及 HTTP 上报 instanceId/plcId/sourceGeneration 是不同事实；导入目录不创建或替换外部上报绑定、不改历史/队列/原始样本/回执。DAA 样本继续引用本地稳定 ID；FF 使用合同外部点 ID，映射是可追溯关系，不声称两个不同历史 ID 自动等价。
6. v1 的一个导出 PLC 只有一个 origin 命名空间；同一目标 PLC 已持久绑定另一外部 origin 时，禁止自动合并、覆盖或将两个 origin 伪装成一个。不同来源均要纳入同一 PLC 时须另立可追溯身份归并设计。此前从未建立外部身份的本地 PLC，可在逐点一一匹配并明确确认后绑定首次输入的 origin；原本地 ID 与历史仍保持。DS/DAA 未建立外部身份的原生 PLC 首次导出以自己的 profile 和本地 PLC ID 构造稳定命名空间。

## 6. DS 导出及反向导入设计

### 6.1 DS 导出

导出入口以实例列表为起点，可多选并选择同一 saved revision，预览所选实例的来源版本、实际 loaded、连接目标、每个 DB/点及问题。源自 DS 的 id、name、type、byte/bit、DB number/length 和来源路径按实际事实映射。所有点含停用点均按合同验证；确认或地址缺失时给出 DB/点定位并阻止该实例。初值、规则、权限、在线值不进入交换合同。

用户提供或确认 FF/DAA 可达的 client host/port；不能把 0.0.0.0 作为远端连接目标，跨机器不能把 127.0.0.1 误当远端地址。TSAP 显示服务端与客户端方向并按既有合同核对。文件的导出成功不证明目标已连接、模拟正在运行或点值正确。

### 6.2 DS 从目录导入：独立拟议切片

输入可为 DS 或 DAA 导出的同格式文件。用户选择新建或匹配现有 DS 实例，预览并确认映射、DB/点、已有策略及冲突；只写 DS 草稿，按 DS 原有版本保存、加载流程处理，不启动。不得声称该能力已实现，也不以它阻塞 DS→DAA/FF。

文件中的 connection 是 client 连接目标，尤其 DAA 导出的地址可能是真实 PLC：**不得把它自动作为 DS 本机监听地址，也不得连接该地址。** 用户必须显式填写并确认自己的模拟监听 IP/端口及 rack/slot；冲突时拒绝。新实例默认不启动；模拟初值、规则、客户端读取/写入许可分别由用户在 DS 确认，不从 DAA 采集启用状态推导。目录点的来源被明确标记为 catalog，缺少原 TIA 结构时不伪造 DB/UDT 文件或完整来源树；维护一致的本地/外部身份映射及 DS 自身布局/命名确认。现有实例的规则、初值、权限和历史版本默认保留，冲突先预览，不能覆盖无关对象。

## 7. DAA 导入：无需再提供 DB/UDT

### 7.1 来源分型和完整性

DAA 现有配置的 Db.source_id 指向逻辑 SourceDocument，启用点还要匹配 Db.tree 中的叶及 type；SourceDocument 内容须与 SHA 一致。这是当前事实，不能只把目录点转成空树并关闭校验，也不能伪造 .db/.udt 内容、文件名或 TIA 源行。

拟议做法优先复用 DAA-005/006 的 **schema 1 可选字段、旧 DDL 不变**先例：

- 在配置 JSON 添加可选 catalog bindings，字段缺失表示原有 DB/UDT 或旧配置，读取旧 payload 不写回；按本地 DB ID 关联实际 catalog 逻辑 source ID、源原字节 SHA、外部 origin/DB ID 及外部点 ID → 本地点 ID 映射。保留原有 Point 的稳定身份和样本字段结构，避免把绑定元数据塞入每个 PointFact。
- 实际导入 JSON 作为明确的 catalog SourceDocument，保存用户所选原始 UTF-8 内容及 SHA。一个 PLC 导入的一份文件建立一个逻辑 source；该 PLC 多个 DB 的 source_id 可以共同指向此 source，由每个 DB 的 catalog binding 精确标识文件中的对应 DB。不同 PLC 的逻辑 source 各自独立；同 SHA、同字节的物理归档按现有策略复用，不覆盖旧归档。共享单一逻辑 source 避免每 DB 重复一份大 JSON 而突破配置容量。source_id 始终指向真实目录源，而非伪造 TIA 源。
- 对有 catalog binding 的 DB 执行目录专用完整性验证：解析并重验文件版本、原字节 SHA、origin、DB/点 ID、名称、类型、地址及占位；本地映射必须一一对应，不允许缺失、重复、跨 PLC、改写绑定或引用文件未声明的点。当前 DB 关联源校验中对 db_number/原 importBinding 的要求，在 catalog 分支以完整的目录 DB 关联校验替代；旧来源分支的原逻辑不变。source_path 如文件没有该事实则保持缺失语义，不伪装为 TIA 路径；目录点可在本地视图展示有事实的来源路径和单独的目录身份。
- catalog 的完整性表示“已完整验证该 JSON 声明的点集”，不表示已验证 TIA 工程完整树。目录分支可将 Db.complete 用作目录完整性准入，Db.tree 可以为空；UI 明示来源是目录点列表，不生成假树或声称可恢复原源文件。对原 DB/UDT 来源，原 Db.tree、leaf_matches、source/UDT 闭包和地址校验完全保留；只在显式 catalog 分型下使用等强度的目录成员核对。
- 导入确认后地址及确认依据明确记录为目录来源与用户确认；若现有 origin 枚举无法如实表达，需在后续受批实现中增加清晰的 catalog 类型并核对样本定义和上报兼容，不能谎写为 TIA 自动推算。对后续手工改地址/类型，必须要求明确的本地覆盖确认，保留原目录和修改前值；激活校验对照原目录加明确覆盖，而不是绕开校验。覆盖及其重新导出语义须在实施切片冻结并有负例。
- 只新增可选配置元数据并不能自动证明兼容：现有 serde deny_unknown_fields 的旧二进制可能拒绝新 payload。必须验证新版本零写读取旧草稿/版本/样本、原字节/hash 不变；旧版本碰到新 catalog 元数据须安全拒绝，不得静默启动错误配置或生成空库。降级前停止自有采集并保留完整 profile；只在证明兼容的副本或原备份上回退，禁止覆盖真实历史。
- 当前 configuration_revisions 和 configuration_contexts 的物理 schema 对配置 payload schema_version 均有 CHECK=1。若验证证明上述 v1 可选字段方案不能满足完整性、性能或兼容性，则停止该实现切片，提出独立的 schema-maintenance Revision，明确双库兼容、升级前备份、中断恢复、旧记录不重写、回退和真实 profile 采用审批；不得把 schema 2 或 DDL 当成本设计已授权的自动迁移。

拟议的 DAA 配置 JSON 扩展是可省略的 catalogBindings 列表。每项包含 localDbId、sourceId、sourceSha256、sourceKind、originDbId 和 pointMappings；每个 pointMapping 包含 localPointId、catalogPointId，可选 localOverride。sourceKind 明确区分外部 exchange_json 和下文的 local_snapshot，按对应封闭格式分别校验。其所属本地 PLC 从 localDbId 关联到本地 DB 后核对，不信任输入另填的 PLC。sourceId 必须属于同一 PLC，sourceSha256 必须等于该 SourceDocument 原字节摘要，originDbId 必须在相应外部文件或内部快照中唯一存在；所有 localPointId/catalogPointId 在本映射中分别唯一，且两侧点集必须完整一一对应。两个 DB 不得引用同一 originDbId；同一外部文件的一次导入在一个本地 PLC 只使用同一逻辑 sourceId，跨 PLC 则分别持有逻辑来源。

localOverride 仅用于使用者在 DAA 显式修改目录点的地址或类型：含该次确认所依据的 sourceSha256、修改后的 dataType/offset/可选 bit、用户确认原因。无 override 时本地点的类型/地址必须与归档 JSON 一致；有 override 时必须匹配已确认覆盖，且重新执行类型、DB 长度、bit 和跨点重叠校验。源文件重新导入后若原点类型/地址与覆盖基准发生变化，预览列出冲突并暂停该点更新，由用户明确保留覆盖或采用新值；不得悄悄以旧覆盖套用新源。DAA 导出采用所选已保存配置中的实际有效点位，保留 origin 和点 ID，并以本次 DAA 配置 revision/SHA 如实标明新的 exporter 来源，不把覆盖值谎称来自旧原始文件。名称、显示信息和分组的变更仍分别走既有命名及草稿保护。

在已导入 catalog 的 DB 里新增本地点时，不得仅修改 pointMappings 而继续指向不含该点的旧文件。拟提供明确的本地目录修订操作：在预览确认后基于当前已验证目录、有效覆盖和新点生成该 DB 的不可变内部点集快照，格式标记为 daa.catalog_snapshot，含 origin、originDbId、原 source SHA 和完整点集，单独算 SHA 并归档；新草稿内该 DB binding 指向此快照且重新建立完整一一对应。该快照是 DAA 生成的内部来源材料，不冒充原 DS 文件或 DB/UDT，不携带当前配置自身的 revision/SHA，因此不产生配置与自身摘要的循环引用。其他 DB 可以继续指向原交换文件；更新源、绑定及草稿在同一事务提交。追加点沿用原命名空间但不声称由 DS 创建；用不冲突的本地 UUID v4 作外部点 ID，既有映射不变。导出时才从所选已保存 DAA 配置生成公开交换 JSON，并正确填写 DAA 的实际版本/SHA。内部快照不作为跨应用合同公开，也不覆盖先前原始文件或历史 revision。

为支持无需 DB/UDT 导入的有效地址，目录导入经用户预览确认后，Address.confirmed 才为 true，拟议新增 origin 值 catalog 和明确的确认原因；手工覆盖仍保留独立的手工来源。此值只能用于具备有效 catalog binding 的点。因 PointFact 包含 Address 定义，新值会出现于后续新样本的本地定义中：实施时必须验证 DAA 原有历史解码及事实 v2 上报契约兼容，保留所有既有样本字节和已冻结上报内容；若外部合同不接受该值，返回 PM 另定范围。读取和解析目录本身不构成对真实 PLC 布局的验证。保存前还要核算单个源、完整配置 JSON、归档和容量预算；超限时明确拒绝且无部分写入，不能因为单文件小于 1 MiB 就假定目标配置一定可容纳。

### 7.2 DAA 导入体验与采集准入

选择文件后，新建 PLC 或选择现有 PLC，预览同一文件的连接、DB、所有点、来源、变更、不可支持项及映射。导入确认可复用文件中已确认地址，但仍须本地明确用户确认；目标真实 PLC 地址需现场资料核对。首次新建的点默认不自动开始采集。用户可以在导入预览中选择现有采集组，或显式新建组并填写周期，一次批量分配选中的受支持点；同 PLC/DB 的启用点遵守现有 DAA runtime 分组规则、资源预算与数量上限。未选择的点保留并显示为未分组/停用。

确认仅提交到草稿；用户可随后显式激活配置、连接并采集。端到端验收必须证明：**文件和 DAA 新空隔离 profile 足够，不额外提供或重新导入 .db/.udt**；由 DS 受控模拟器提供 BOOL、INT、REAL 可读值，DAA 一次分组后保存、激活、真实读取并核对采样点 ID、地址、类型、值和质量。失败有具体原因；不能以解析 JSON 或纯内存单测代替此闭环。旧配置和运行任务按原路径工作。

### 7.3 DAA 导出

按 PLC 多选、每台一文件，从用户选择的 saved_draft 或 active_revision 生成上述共同合同；仅导出该配置中已声明且可通过合同完整性检查的 DB/点。未确认地址或类型问题必须逐点报告并阻止该实例，不能用停用状态掩盖。重导本地由目录输入的配置时保留外部 origin 和稳定 ID 映射，并如实记录 DAA 作为导出者及选定配置版本；DAA 自建点以自身来源建立稳定身份。DAA 的 DB 没有独立启用字段，导出时省略该层 source_enabled；每个点的 source_enabled 必须取当前 DAA 配置中的 Point.enabled，即使来源命名空间是 DS 也不能沿用源文件的旧启用值。采集组、周期、运行历史、队列、上报设置及凭据不进入 JSON。

## 8. FF Rust 新格式兼容及旧格式保全

为同一份混合类型文件增加新的 aiis.plc_points v1 解析/适配分支，采用不依赖 DS/DAA 进程及数据库的独立文件读取。不能把它直接冒充 ff.plc v1：旧格式拒未知字段、S7 只允许 int16、source 只有 manual/device_simulator，原入口和校验行为均保持。

新分支对整份文件逐点完整做结构、ID、类型词法、地址、位、重叠、长度、容量与来源验证，包括未启用/未引用点；无效文件一律启动前拒绝。对结构有效的混合类型文件，保留全部点的元数据：当前 Rust 运行只支持 S7 INT→int16 的现有句柄，BOOL、REAL、STRING 和其他已知类型列为“格式支持、当前运行类型不支持”，不伪装成 INT、不丢弃、不产生设备读取或默认值。

同一份文件若只被 flow 引用 INT 且其他类型未引用：允许配置 preflight 通过并运行既有 INT 只读调用和既有 demo01 的受控 INT target；CLI/报告列出不支持的点 ID、类型、总数及已展示数量。若任何 flow 引用不支持类型或连接能力不支持，必须在状态库打开/恢复写入、日志创建、owner/flow 创建和网络连接前阻断，给出设备/点 ID、类型和稳定原因；不能先启动其他流再发现错误。有效但未引用的 unsupported 点与无效点不同，前者在新格式下可报告并保留，后者始终拒绝。目录的 source_enabled 仅为源应用事实，不自动赋予运行写权限。

单文件 validate 和整组 validate 分别报告作用域：单文件仅说明文件格式及类型能力，不能证明 flow 可运行；整组按实际 flow 引用给出可运行结论。完整报告应可取得全部不支持点；若任何展示被限制，必须显示总数和截断状态，提供剩余明细访问方式。旧 ff.plc v1 的 CLI 字段语义、禁用/未引用点的全量校验、YAML v1/v2、既有三种 v1 flow、状态结构和失败方式不因本新分支放宽。

适配只生成内存中的设备、点句柄及能力诊断，不以静默丢点生成另一个 ff.plc 文件。设备和点的外部 ID 来源于 origin，按现有 FF 约束验证；加载后复用既有 owner/连接和队列。只引用点不代表自动读取；条件、轮询、HTTP、写入归属仍由 FF 自有流程配置。

对于与旧配置物理目标完全等价的 INT 流，需按现有摘要规则证明配置身份与持久资源兼容；目录路径、JSON 字段顺序、导出时间和展示文本不能制造新效果。若原手写 FF 设备/点 ID 与交换文件身份不同，不能假设可直接接替已有状态：先明确映射及 identity 冲突，保全 pending/in_flight/unknown/confirmed 并按既有唯一 writer 与恢复规则处理。真实地址、数据类型或物理目标发生变化必须可见并阻断不安全恢复。Python/C# 的目录加载和 Modbus wire/读写为另批阶段。

## 9. 预计阶段、依赖与交付归属

| 阶段 | 拟交付与进入条件 | 不继承的批准 |
| --- | --- | --- |
| P0 本 Revision | 跨端详细设计及候选 JSON；核对已存在实现、风险和实现切片 | 只有设计草案，未批准代码 |
| P1 共同合同与样例 | 根据审阅结果形成根 contracts 的 proposed 机器可验证 schema、正反例与版本策略；明确正式合同发布条件 | contract published、Git refs、软件与生产另批 |
| P2 DS 导出 + DAA 导入 | 显式保存版本选取、逐 PLC 文件和 DAA 可核验 catalog 分型；实现同文件、无原 .db/.udt 的合成采集闭环 | 真实设备、既有 profile schema 维护/迁移及现场采用另批 |
| P3 FF Rust 新格式适配 | 完整文件校验、部分类型可用报告及 INT 引用；旧 ff.plc 行为不变；同 P2 文件联调 | Python/C#、Modbus 及扩展数据类型读取另批 |
| P4 DAA 导出 | 选择 saved_draft/active_revision，多选逐台导出同合同；同文件供 FF/DAA 使用 | DS 反向导入不由此隐含实现 |
| P5 DS 导入 DAA 文件 | 明确模拟监听端点、来源和策略确认；需独立批准 | 真实 PLC 地址不自动监听或连接 |

P2/P3/P4 可在共同合同冻结后按精确范围并行设计；任何实现必须先有对应 Task ID、Revision、文件 allowlist、审批、Development 和 fresh-context Verification。不得把 P1 合同样例或单端格式测试宣传成跨端采集成功。必要的原生验证、Windows、长期运行和现场由对应任务的验收矩阵和 Human Owner 决定。

## 10. 拟议验收矩阵

以下为未来设计审查和各实施切片应落实的可观测标准，**不是已完成证据**。

| 编号 | 验收标准 |
| --- | --- |
| AC01 | 一台 PLC 一份 JSON；多选两台分别导出，实例、DB、点不串，全部成功/局部失败/取消和重名处理均有准确结果；失败无半文件。 |
| AC02 | 本规格合成混合类型样例按正式 schema 可验证；编码、重复键、未知版本/字段、大小/深度、重复 ID、空 DB、非法类型、bit/长度/越界/同位重叠均有正反例。 |
| AC03 | DS saved/selected/actual_loaded 不一致和不存在时准确显示；DAA saved_draft/active/loaded/used 分开，导出的 payload SHA 和来源来自真实所选事实，不混入未保存草稿。 |
| AC04 | DS 可从合成多 DB/UDT 或手工配置得到含 BOOL、INT、REAL、STRING 及禁用点的声明；确认完整后导出，未确认地址、未知类型或缺名分别报问题且无丢点。 |
| AC05 | 不携带 DB/UDT 的 DS JSON 在新空 DAA profile 完成预览、确认、分组、保存、激活；受控 DS 本地 S7 确认 BOOL/INT/REAL 的 ID、地址、类型、值和质量；不启动真实设备或使用用户 profile。 |
| AC06 | DAA catalog SourceDocument 原字节/SHA、source_id、DB 映射和点成员一一核验；伪造来源、错 hash、错 point/DB/type/offset、重复映射全部阻断；原 DB/UDT 的 tree/leaf_matches 校验不能被削弱。 |
| AC07 | DAA 从 DB/UDT 创建的旧版本、原始历史、历史样本与 queued/ACK 数据读取不重写；导入目标增量、预览取消、重复导入、ETag 冲突、失败事务及冷重开正确。 |
| AC08 | 以现有 DAA PLC 为目标时，映射/冲突/删除候选明确；目录缺点或目标 DB 有目录外点均阻断且原草稿不变；采集组、周期、点 ID、上报绑定、generation/sequence、原有样本/回执及未选实例不被导入静默覆盖。 |
| AC09 | DAA active 和 saved_draft 可按实例导出；DS 来源导入再 DAA 导出保留 origin/点映射并如实记录实际 exporter/版本。DS 导出 DB/点启用状态取 DS 实际字段；DAA 重导时 DB 层 source_enabled 缺失、点层为 DAA 实际 Point.enabled，即使 origin.kind 为 device_simulator；DB 层缺失不默认 true/false，点层缺失/null 拒绝。目录内新增点使用单独可核验内部快照、稳定 ID 和无自引用摘要，历史源不变；不同 origin 禁止静默归并。 |
| AC10 | 同一 BOOL/INT/REAL 文件供 FF Rust 加载：全点验结构，完整报告未支持类型；仅引用 INT 的流可运行，引用 BOOL/REAL 在状态/日志/网络前明确阻断；坏的未引用点同样拒绝。 |
| AC11 | 旧 ff.plc v1/YAML v1/v2 原测试和旧 disabled/未引用点校验不变；旧状态等价目标不重复执行，身份/地址改变与 unknown 冲突按 FF-004 既有规则处理。 |
| AC12 | DS 反向导入阶段把 DAA 文件里的真实 client 目标与独立模拟监听端点区分；未显式确认监听不允许提交，导入不连接、不启动、不复制采集组/写权限。 |
| AC13 | DAA 新版读取旧 payload 零写回；旧二进制遇到新 catalog 元数据实际测试安全拒绝或阻断，配置/运行双库完整；不得无证承诺降级可用。任何必要 DDL 另有独立 schema-maintenance 批准及中断/回退证据。 |
| AC14 | 可达 host、loopback、wildcard、非默认 TSAP、用户取消/并发、带空格路径、文件替换和多个实例均有可观察测试；格式 hash 不冒充真实来源或现场设备验证。 |
| AC15 | 各应用均保留原独立启动、草稿、版本、采集、规则和已有合同；中文/英文文案对称、表格列宽按仓库公共规则。文件可含点位逻辑 source_path，但无实时值、口令、本机文件系统/SQLite/profile 私有路径或授予写权限。 |
| AC16 | Development/QA 只在各自批准范围、合成数据和专用隔离资源中记录实际命令、退出、限制；新鲜 Verification 及 Human Owner 验收独立于 PM 静态文档检查。 |

## 11. 风险、边界与后续复核

- 同文件完整点表与 FF 能执行的点不同。按 §8 对全部点验证、对不支持类型报告并按引用准入；不允许以“未使用”跳过坏地址，也不允许以“可解析”声称可读取全部类型。
- 目录来源是明确的新来源，不冒充原 TIA 文件。DAA catalog binding 的局部覆盖、来源完整性和现有样本/上报合同相容性必须经实现期测试证明；若影响已发布事实格式或要求额外 schema 迁移，返回 PM 修订并另批，不能靠本草案扩权。
- 配置快照只能证明导出方曾声明地址；对真实设备的非优化 DB、访问、字序及偏移仍需实际资料核对。仅限合成 loopback 的验证不能外推到现场、Windows、Linux 或长期运行。
- 禁止覆盖已有用户数据、强行重绑身份、清空 pending/unknown/回执，禁止把导入当作激活、自动采集、发送或授权写 PLC。回退以停止自有运行、保留完整原 profile/版本与证据为先；旧二进制可能拒绝新数据，不能靠删表或改 schema 掩盖。
- 正式共享合同归根 contracts，软件实施分别归 DS、DAA、FF 的精确任务，不修改历史任务验收。用户可见文案遵循 i18n；Tauri、Rust runtime 和 PLC 点位任务在实施时分别加载 desktop-tauri、rust-runtime、frontend-ui、i18n-workflow、plc-point-mapping 和 code-document-indexer。后端或 Worker 不在当前设计的默认改动范围。
- 本设计默认 S7 与上述类型集合，不承诺所有 DS/DAA 私有类型或未来协议自动兼容。若现有实例存在本合同无法表达的点，列问题并阻断导出；禁止静默缩小“整个实例”的点集。

## 12. 需要 Human Owner 审阅的取舍和下一 gate

1. 是否接受首期逐 PLC 单文件、S7 多类型的共同 JSON，以及 DS、DAA 的离线交接；是否保留多选后每台分别生成文件。
2. 是否接受 FF 新格式对未引用的已知不支持类型完整保留并报告、仅在被引用时阻断；旧 ff.plc v1 不变。其他类型的真实读取仍需后续实现。
3. 是否接受 DAA 新建导入先明确分组/周期，导入只进草稿；DAA 保留已有来源、历史和上报身份；DAA 草稿或活动版本由用户显式选择导出。
4. DS 反向导入作为独立后续切片，导入时另填模拟监听端点；是否需要提前到首个实施阶段。
5. 上述 DAA catalog 可选字段方案作为优先候选；如确需物理 SQLite schema 改动，另立 schema-maintenance 任务与真实 profile 采用 gate。

Human Owner 对本 draft 的审阅不等于批准软件。若认可设计方向，请明确对 ARCH-PLC-001 r1 的设计意见；后续可依实际决定冻结共同合同和拆分独立实施 Revision。未有明确批准前，不创建 Development tasks 或 QA checklist，不启动实现。

## 13. PM 静态自检

PM 已只读核对根契约、workflow、项目现有 DS/DAA/FF 设计入口、DAA 来源/点位和 FF 目录源码；本文件中的类型支持和旧格式边界均限当前静态事实。以 Python 标准库解析文中合成 JSON，并检查 format/version、UUID v4、摘要词法、DB 地址范围、BOOL/INT/REAL 占位互不重叠、12 个本地文件链接和 16 个 AC 编号，命令退出 0。补充以 Python 构造 DAA 重导出但 origin 属于 DS 的示例，检查 producer 分型、DAA 的 DB 字段省略、点位 false，以及五种缺失/null/错误层级负例，退出 0。脚本检查示例和拟议规则子集，不是正式 schema 实现，也不证明三个产品可读取。git diff --no-index --check 对新文件无空白警告，但因文件不同退出 1，不能记作 exit 0。用户 profile、数据库、真实设备、服务、项目测试及构建均未操作。本段仅记录 PM 审阅，不是 Development 自检、独立 QA、Human Owner 范围批准或最终验收。
~~~~~~~~~~~~
~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
