Task ID: DS-005
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 DS-005 r3、父 ARCH-PLC-001 r8 及其版本衔接 -> Development 基于既有记录交接 -> fresh-context Verification 独立文档复核 -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: root
Capability: DS 双语及双向 PLC JSON 的既有证据收尾
Owner: Device Simulator
Acceptance Chain Reference: Development Lifecycle Workflow；精确范围批准、Development、fresh-context Verification 与 Human Owner 最终验收各自独立。
Related Task: aiis-ics-arch::ARCH-PLC-001 r8（范围已批准）; aiis-ics-arch::DAA-019 r3（范围已批准，独立任务）; device-simulator::DS-004 r3（范围已批准，独立任务）; aiis-ics-arch::DAA-018 r4（范围已批准，独立任务）; device-simulator::DS-003 r5; aiis-ics-arch::DAA-017 r5; device-simulator::DS-004 r2（历史版本）; aiis-ics-arch::DAA-018 r3（历史版本）
Depends On: Human Owner 已明确批准本 r3、父 ARCH-PLC-001 r8 及版本衔接；其他关联版本同经 Owner 明确批准，不从本任务自动继承。各任务的 QA 和最终验收分别进行。

# DS-005 r3：基于既有证据的双向 PLC JSON 收尾（范围已批准）

## 1. 目标、边界与修订

本规格按 Human Owner 不再重复测试、保留历史记录及现有数据的要求，提出 DS-005 的**验收证据调整**：以既有的独立检查记录、Owner 已完成的手动 DAA→DS→DAA 往返、协调者只读观察和本次实际 v2 上报对账记录为依据，分别标示来源和证明范围。范围限 DS 的双语及双向 PLC JSON，并将 DAA 实际 v2 上报字段对账作为跨端辅助证据。实际 v2 外发属于 DAA/后端事实，不改变 DS 作为模拟器的职责。

父 [ARCH-PLC-001 r8](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md)、本 r3 和版本衔接已由 Human Owner 精确批准，原 r7 已批准记录按历史保留。DAA-019 及其他基础任务各有独立范围、QA 和最终验收；有关版本由同一 Owner 明确批准，不是从本任务自动继承。本 r3 的范围批准允许依 §4 进入 Development 文档交接，不代表 QA 通过或最终验收。r2 仍以 [checklist](checklist.md) 的 `qa_blocked` 及各轮原判定为事实。

原 r2 §2 的产品和数据保护要求继续作为收尾范围；不做产品、合同、源码、测试、手册、配置、数据库、设备或环境修改。本 r3 的实质变化是：**DS05-06 改为下文分层证据与明确列出的未验证项；DS05-01–05、07 通过审阅对应的既有记录及候选衔接来评价，不再要求重新运行测试或原生操作。** 仅在本 r3 审阅范围内评价，原 r2 已发生的失败和阻塞不能被倒改。

## 2. 应保留并区分的既有证据

1. **独立 QA 历史：** [DS-005 checklist](checklist.md) 记录 QA1 的 Rust/Node 定向检查与实际文件比较，QA2 对 DS05-01–05、索引返修及相关候选的限定结论；F-GUIDE-004 后续双语手册定向复验为 `qa_passed`。各次 `qa_failed`、QA2 整体 `qa_blocked`、ignored/skipped、构建警告、候选和证据限制均保留。QA1 的合成 profile 证据为服务级，不是原生设备操作。英文原生语言切换、弹窗和预览为协调者观察；英文选择文件、实际提交和落盘未实测。
2. **Owner 手动往返：** [DS-005 tasks](tasks.md) 与 [DAA-019 tasks](../../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/tasks.md) 记录 Owner 的实际中文原生往返、当前同源冲突拒绝、移除旧草稿实例后新导入；Owner 报告同一次新 L2 未手工选择即显示 PLC 和 4 点，并对该 L2 再导出。协调者另报告本机新 ID 与外部 origin 不同、四点停用且未分组；两者身份不同。文件 F1/F2/F3 的 SHA 和指定字段比较由当时 Development 及独立 QA 留有记录（参见 DS checklist 的 Owner 文件段及 DAA checklist QA3）；文件字段事实、Owner 原生报告和协调者观察各自归属，不能称 QA 亲身见证原生操作。
3. **本轮数据保护对账：** [DAA-019 checklist QA3](../../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/checklist.md) 曾独立按本次前测比较所列 37 表旧行，记录旧行无缺失及相应新增行；[DS tasks](tasks.md) 记录 DS 草稿来源/版本变化。该比较只覆盖有前测的这一轮及所列字段、表，不能倒证更早一轮缺失的 `context`、`samples` 其他列和 `sample_delivery` 逐行前值；不能声称整个 profile 无写入或既有数据在任意时间全部未变。
4. **实际 v2 上报：** 2026-11-18，经用户允许，协调者只读核对本地 v2 正文/回执及服务端注册、MySQL history/latest，报告 `seq` 91–103 共 13 条：13 条可靠回执及正文字节 SHA 与 history 的对应身份、3 点信息一致；至少一个点的中文和英文显示名均非空，而 13 份请求正文无显示名字段及对应文本；后端点集中未见显示名字段，所核点字段和值一致；latest 为 3 点 `good`、seq 103。对应时段 DS 日志未见 WARN/ERROR。这是协调者对已发生上报的观察，非本任务独立 QA 的实际操作；仅说明本次一次配置和本机环境，不证明所有配置、异常、现场或旧版本，也不能倒证早一轮的缺失前值或 IPC。可追溯材料为本机会话记录 `~/.codex/sessions/2026/11/16/rollout-2026-11-16T09-24-47-01a1e1f4-eb7e-74d2-b055-3696e1a855ec.jsonl` 约第 28239–28242、28257–28260 行，行号变化时按内容定位；其中可能含私有数据，审阅时不复制原始业务值或敏感内容。若记录不可访问，应如实说明证据可用性，不重新查询数据库或发送上报、读取现场或修改数据。
5. **原始工件可用性：** 协调者按 Owner 同意清理了本任务旧 `/private/tmp/` 工件；[DS tasks](tasks.md) 与关联 DAA 记录列出的旧交换文件、基线、app/测试副本已不可再读。此前 roles 记录的哈希、命令、结论和时点仍可审阅，但不能声称本 r3 又重读、重新比对或复现了已删除原件。已保存历史及正常来源归档按原记录保留。

## 3. 修订后的验收与明确未验证项

| 编号 | r3 的既有记录审阅条件 |
| --- | --- |
| DS05-01 | 结合原 QA1/QA2 和手册定向复验，核对中英文导入/导出入口、保存版本选择与导出交互的已有记录及其候选范围；英文仅声明当时实际观察到的切换、弹窗和预览。 |
| DS05-02/03 | 审阅原普通 DB/UDT 来源、DS 导入保存、重开及重导的独立文件比较记录；同时审阅 Owner 的新一轮 F1/F2/F3 记录，区分文件检查与人工界面报告。不可要求重读已删除文件。 |
| DS05-04/05 | 审阅 QA1/QA2 原有合成正负例、默认停用及 DS 侧历史核对记录，限定当时候选与测试覆盖；不把合成结果推广为所有设备或历史全量保护的证明。 |
| DS05-06 | 用 §2 的分层证据代替原 r2 强制取得同一 L2 原生 IPC 返回及旧轮历史逐行前测的验收方式：以 Owner 报告的本轮自动选中与同一实例再导出、当时文件字段比较，以及现存独立检查和本轮数据对账作为可审阅依据。**不将其写成捕获了 IPC 返回，不将后测或新轮前测说成证明了旧轮前值。** 本标准还引用 §2.4 仅限本次实际 v2 字段的协调者报告，不将该报告升级成独立原生 QA。 |
| DS05-07 | 审阅已记录的 Rust、Node、类型/构建、语言及手册检查、失败与限制，并核对当前交付候选相对原检查候选的变化及已有验证衔接。保留 F-GUIDE-004 的限定通过，不把其作为整个 DS-005 的通过；本 r3 不执行新测试、构建、原生重放或用户 profile 操作。 |
| DS05-08 | 保留 QA1/QA2 的原结论与 QA 事实；识别 ARCH-PLC-002 等后续对共享文件的变化及其既有验收/验证记录，不能将不同字节的当前候选自动说成原 QA 检查过的候选。Development 记录当前工作树、明确文件范围、差异和能支持的衔接；fresh-context Verification 独立审阅记录和 diff。若现有证据与交接不符或不足以支持本限定结论，按事实 `qa_blocked` / `qa_failed` 并交 PM / Human Owner 决定，不运行补测或改变数据。 |

**向 Owner 明确列出的剩余风险：** 原 r2 QA2 所需原生 L2 同次 `importedLocalPlcId` 的直接返回未被截获；更早一轮旧历史的上述行级前值不可倒证。Owner 新一轮报告、合成服务/Node 结果及记录在案的对账是不同证据，不能拼成原要求曾被满足。本 r3 调整的是以后续有界证据作决策的验收口径，非宣称原缺口已被补齐；范围批准不是 QA 通过或最终验收。

此前 1 秒存储回执为 `unknown` 的风险仍须先读回、不可盲目重试。旧二进制读取新增元数据、英文文件提交/落盘、Windows/VM、真实 PLC、全部失败/并发场景、长稳及生产采用未由上述证据证明。协调者曾误点 L1 测试连接且报告未建立连接，保留原记录，不能称从未尝试连接。一次本机实际 v2 上报不代表真实 PLC 验证或现场部署。

## 4. 文件权限、handoff 与排除项

- 本规格仅由 PM / Human Owner 写入本 `spec.md`。批准后，Development 只可在本任务 `tasks.md` 基于既有记录追加证据分层、精确候选及差异、限制和 `developer_handoff`；fresh-context Verification 仅在本任务 `checklist.md` 记录独立**文档复核**、verdict 和未验证项。须保留 r1/r2 的完整历史、已发生的 `qa_failed` / `qa_blocked` 及原证据，不倒填、覆盖或删除；如更新文件头，保留原头、历史内容及写前摘要。PLAN / catalog 机械同步由主协调者依其权限另行处理，不属于本角色写入。
- 以 `project-governance`、`aiis` 约束角色与工业边界；后续角色按实际审阅表面分别采用 `plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer`，涉及 DAA v2 / 后端合同的事实审阅时采用 `backend-arch`。这些路由只约束相应角色按需读取，不授权新增技术实现。
- 不重跑测试、构建、界面联测或现场步骤，不要求 Owner 再测试；不重新读取已清理原件。不得修改历史数据、现有 profile、真实数据库或实例，不要求用户接受任何真实数据变更。任何证据不足依 STD 如实交回，不以清理、重建或新现场操作消除缺口。
- FF/CA、真实 PLC、数据库 DDL/迁移、兼容旧版宣称、跨平台验证、部署、发布和新上报均排除。DS-003、DS-004、DAA-017、DAA-018、DAA-019 及父设计各自状态不被本任务自动改写；整体跨端完成与否须依各自批准和验收结果说明。

Human Owner 已精确批准本 r3 及父 r8 的版本衔接，现可启动上述 Development 文档交接；随后 fresh-context Verification 基于可用记录独立作出有界 verdict，最后由 Human Owner 自行决定本任务最终验收。`qa_passed` 仅代表其实际审阅的 r3 范围，不推导全部现场能力、旧任务通过或生产部署许可。

## 5. Human Owner 精确范围批准

2026-11-18（Asia/Shanghai），Human Owner 在审阅所列五份精确收尾草案后明确回复：

> 批准这组收尾草案

该决定分别精确批准 `device-simulator::DS-005 r3`、`aiis-ics-arch::ARCH-PLC-001 r8`、`device-simulator::DS-004 r3`、`aiis-ics-arch::DAA-018 r4`、`aiis-ics-arch::DAA-019 r3` 及其版本衔接；这些版本由此条明确决定分别获批，不从本任务自动继承。本任务审阅时的完整 r3 草案 SHA-256 为 `cc316e6ce921aa974cb8aab6029e233d37e0980e32269e9aa632b6eea9648c04`；父 r8 登记批准后的完整 spec SHA-256 为 `38085d5f0dd5d9db444008b9e04963371ddff3995cbb050641281ce6517931e5`。附录所列 r2/r1 摘要为形成时的历史事实，不因本次批准改变。

本决定允许 Development 按 §4 整理已有记录并交接，之后依次进行 fresh-context 独立文档复核与 Human Owner 最终验收；不代表 QA 通过、原有证据缺口已补齐或最终验收。原 `qa_failed` / `qa_blocked` 及其证据继续保留。

## 附录 A：已批准 DS-005 r2 的完整原文（含 r1 历史）

写前 r2 完整 SHA-256：`f9ec8c6941f61b50b31d02a8526c8d53c907486190dd48ae0cc1c374d94851b7`；其内部 r1 原文 SHA-256：`fe007553288adbdd426b1ce7edf9ebd8a2d6d0bfa72a549deeb3fb8341975c75`。以下围栏内保留 r2 原始 UTF-8 字节及末尾换行，连同其中已批准 r1、原批准与历史；本次 r3 的批准另见 §5。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: DS-005
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 ARCH-PLC-001 r7、DS-005 r2 与 DAA-019 r2 及版本衔接 -> Development 接续 -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: root
Capability: DS 导入完整 PLC JSON 并从保存版本保留外部身份导出
Owner: Device Simulator
Acceptance Chain Reference: 本任务独立遵循 Development Lifecycle Workflow 的精确范围批准、Development、fresh-context Verification 与 Human Owner 最终验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r7; aiis-ics-arch::DAA-019 r2; device-simulator::DS-003 r5; device-simulator::DS-004 r2; aiis-ics-arch::DAA-017 r5
Depends On: 本任务 r2、ARCH-PLC-001 r7 和 DAA-019 r2 及版本衔接已获 Human Owner 精确批准；跨端闭环需要两端最终交付候选。

# DS-005 r2：实例页双向 PLC JSON 与安全验收衔接（已批准）

## 1. 目标与范围

DS「实例」页面标题动作区并排提供「导入 PLC JSON」「导出 PLC JSON」及既有新增按钮。英文对应 `Import PLC JSON` / `Export PLC JSON`。导出复用现有 DS-003 r5 的选择保存版本、勾选实例及预览/落盘流程；不以当前草稿冒充保存版本。导入一份符合 [ARCH-PLC-001 r7](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 的 DS 或 DAA producer 文件，预览后新建一个 DS 实例草稿；不覆盖、匹配或合并已有实例。

DS-003 r5 的独立 QA2 已通过、待 Owner 最终验收，原失败与阻塞历史保持；本任务不更改其 spec、tasks 或 checklist。DS-004 r2 当前 `qa_blocked`，其独立验收不因本任务变更。本任务 r1 已获批准并有 Development 候选及自检；本 r2 只修订 DS05-06 的验收衔接，已获 Human Owner 精确批准。

## 2. 产品及合同要求

1. 复用 r7 所沿用的 r6 / 已批准 r5 的单 PLC `aiis.plc_points` v1 字段、限制、完整性及严格解析；两种 producer 均应受支持，包括 DAA producer 缺省 DB 层 `source_enabled`。无语言 `display_name` 可达 256 UTF-8 字节，DS 现有 200 字节上限须在本范围内扩展到 256 并保持原值；点编辑器不能加载后静默截断，超限清晰阻断。双语缺省表示两侧空，不从技术名、旧名称、描述、另一语言或 TIA 注释填充。
2. 预览输入原始字节/SHA、外部 origin、来源版本、客户端目标、所有 DB/点、双语、无语言旧名、独立 description、地址和源启用标志。DS 将输入文件仅作为目录来源，不伪造 DB/UDT 及 TIA 结构树。多个 DB 可以绑定同一份原始 JSON；保存并重开后仍能验证原字节/SHA、外部 DB/点身份及逐点本地映射，不能把目录数据降为未经校验的手工点。已保存版本及原有 TIA 来源、确认、历史保持。
3. 文件连接信息只作客户端目标展示；使用者必须单独填写并确认 DS 本机模拟监听 IP、端口及 rack/slot，不能自动拿源 PLC 地址监听或试连。TSAP 显示来源与模拟监听的方向及实际值；DS 自身可表达的非默认 TSAP 不得一律拒绝，不能表达的值须明确提示并阻断，不静默改写。非法、重复端点、实例上限、身份与来源冲突须明确拒绝，不覆盖其他实例。默认不启动，DB 和点默认停用；模拟初值、规则和读写策略不从外部 `source_enabled` 推断。导入只生成草稿，用户按 DS 既有流程完成必要的名称/布局确认并保存版本；运行、加载和启动仍由用户显式操作。
4. 输入文件、所填监听地址、草稿 ETag 和预览结果绑定；文件改变、取消、过期、并发或提交失败时不产生部分实例、来源或映射。对已绑定目录点的技术身份、点集、地址和类型，本期不做差异重导或覆盖；可调整既有允许的显示名、描述及启用/模拟策略，不能削弱源完整性校验。若编辑需要变更目录点集或物理布局，明确拒绝并另立范围。
5. 从已保存的 DS 原生实例及目录导入实例导出都使用现有一份完整合同；后者保留外部 origin、DB/点外部 ID 与本地映射，`export.producer=device_simulator`，payload SHA/版本/时间取 DS 真实保存版本。DB、点的 `source_enabled` 取 DS 当前配置事实；不要求与 DAA 的采集启用值相等。多选每实例一份，重名拒绝、不覆盖、原子发布、逐项结果和取消清理均不弱化 DS-003 r5。
6. 不修改物理 DDL 或迁移已有 profile。若目录绑定无法利用现有存储安全承载，或需白名单外文件/新依赖，停止并回 PM。旧版读取新增可选元数据的结果没有证据时如实标明；不能将导入/导出说成设备布局或运行许可证明。

## 3. 沿用 r1 的 Development 文件 allowlist（r2 已批准）

仅为本任务修改以下相对 `automation-world/device-simulator/` 的明确路径；花括号仅展开所列文件，不是目录通配符。额外文件需回 PM 修订及重新批准。

| 范围 | 文件 |
| --- | --- |
| 运行时数据和来源 | `runtime/src/domain/{mod.rs,configuration.rs,source.rs,layout.rs,plc_catalog.rs}`；`runtime/src/infrastructure/config_store/{mod.rs,queries.rs,transactions.rs}`；`runtime/src/services/{mod.rs,configuration.rs,source_import.rs,catalog_export.rs,layout.rs,naming.rs,versions.rs}`；`runtime/src/app.rs`；可新建 `runtime/src/services/catalog_import.rs` |
| 桌面桥接 | `src-tauri/src/{lib.rs,app.rs}`；`src-tauri/src/commands/{mod.rs,import.rs,catalog_export.rs}`；可新建 `src-tauri/src/commands/catalog_import.rs`；不增加依赖或修改锁文件 |
| 页面与文案 | `src/services/deviceSimulator.ts`；`src/console/composables/useDeviceSimulator.ts`；`src/app/simulator/views/instances/index.vue`；`src/app/simulator/components/{CatalogExportDialog.vue,PointEditor.vue}`；`src/app/simulator/locales/{en-US,zh-CN}.json`；`src/styles/app.css`；可新建 `src/app/simulator/components/CatalogImportDialog.vue` |
| 定向测试和说明 | `runtime/tests/{plc_catalog_export.rs,source_import.rs,configuration_store.rs,point_display_names.rs}`；可新建 `runtime/tests/plc_catalog_import.rs` 和 `tests/plc-catalog-import.test.mjs`；可改 `tests/{plc-catalog-export.test.mjs,point-display-names.test.mjs}`、`tests/{README,README.zh-CN}.md`、`runtime/{README,README.zh-CN}.md`、`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN,CODE_INDEX}.md` |
| STD 事实 | 本 `spec.md` 仅 PM / Human Owner；精确批准后 Development 创建本任务 `tasks.md`，handoff 后 fresh-context Verification 创建本任务 `checklist.md` |

除以上路径，不改现有其他任务 bundle、DDL/migration、环境文件、协议驱动、DS/DAA 之外工程或公共合同。关联 PLAN/catalog 的机械同步由主协调依其权限处理，不视为本角色写入。

## 4. 验收标准

| 编号 | 通过条件 |
| --- | --- |
| DS05-01 | 实例页头可见两种中英文入口；导出勾选保存版本中的实例，旧 DS-003 导出/取消/同名拒绝、多选结果和 selected/loaded 差异提示保持。 |
| DS05-02 | 用 DAA 实际导出且含 DB/UDT 来源、BOOL/INT/REAL、双语、独立 description 的同一文件完成 DS 预览、新建、手动指定 loopback 模拟监听、必要确认及保存；不提供 DB/UDT，不启动实例或连接源 PLC。 |
| DS05-03 | 保存重开后 DS 实际重新导出该实例；原始外部 origin、外部 DB/点 ID、技术名、地址、类型、双语/空值、旧名、description 和 source_path 无损，producer、source_enabled、版本、时间和 payload SHA 反映实际 DS 版本；交 DAA 使用实际文件。 |
| DS05-04 | 双 producer、缺省 DB 启用、可表达及不能表达的非默认 TSAP、同源/身份/端点冲突、原文字节变化、伪造来源、错误类型/长度/地址、禁用点非法布局、并发及取消有针对性正负例；非法整份拒绝，既有对象不变。256 字节无语言旧名可保存、重开并无损导出，超限拒绝。 |
| DS05-05 | 新实例及 DB/点默认停用，用户可按既有流程显式设置模拟策略；输入 DAA 的源启用不等于 DS 授权。既有 DS 原生实例、TIA 导入、版本、确认与其他历史不被改写。 |
| DS05-06 | 按父 r7 A06 与 §4.1：独立复核 DAA 自有合成 profile 的真实持久化激活/历史隔离服务级证据；在两端经核对的 `.local/dev` 原生界面完成以既有合成历史为源的实际 DAA→DS→DAA 文件闭环，记录 F1/F2 SHA、旧外部身份、两次新本机 ID 及真实提交；本轮 DAA 不激活、不采集或上报。另以 DAA `DEV-PLC-A` 的普通 DB/UDT 来源只读导出文件完成 DS05-02/03，不冒称该来源为 catalog 或合成内容。保护两端既有历史，必要条件不满足即 blocked；服务级/fixture/预览不能冒称原生提交。 |
| DS05-07 | 运行与改动相称的 Rust、前端及构建验证，检查中文/英文交互和手册；记录候选、命令与限制。测试后只清理本任务可确认的合成对象，已保存历史按实际保留。 |

## 5. 风险、排除项与 handoff

采用 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer` 的相应规则，交 Development 按触达面读取，之后交 fresh-context Verification。原 r1 与本 r2 验收衔接均已获批准。测试使用经核对的两应用 `.local/dev`、自有临时合成 profile 和明确的本任务文件；保护 DAA 原 `DEV-PLC-A` 与两端原有历史，若必要条件不能保证则停止。历史目录点集覆盖、FF/CA、真实设备、外部上报、物理 DDL、Windows/VM、部署与发布均不在范围。合成 GUI 验证和新任务 QA 不构成旧任务最终验收。

## 6. r1 修订与批准（历史）

2026-11-17：为用户新增两端页头入口及 DAA→DS 方向提出 r1 草案。Human Owner 审阅列明的精确版本后回复“批准三个版本，继续开发”，精确批准 `device-simulator::DS-005 r1`、`aiis-ics-arch::ARCH-PLC-001 r6`、`aiis-ics-arch::DAA-019 r1` 及父设计旧任务时序衔接。本任务审阅时完整草案 SHA-256 为 `23e9538ceab3d51ad49f05f8cb24a2aa3f6298c19ea77e06a4d738f6a9e62190`。当时交 Development 按本白名单实施，随后 fresh-context Verification；Human Owner 最终验收仍待决定，其他任务状态不因本批准改变。

## 7. r2 修订及 Human Owner 精确批准

2026-11-17：因 DAA 当前 `.local/dev` 继续激活会触发既有 8 版本裁剪风险，按父 r7 将 DS05-06 分为自有 profile 激活验证、两端 `.local/dev` 不激活的真实文件往返及普通 DB/UDT 来源验证。DS05-01–05、07、产品功能、文件 allowlist 与原有数据保护均不变。原 r1 实施候选和自检由 Development 原 tasks 保留，未获独立 QA 或最终验收。

2026-11-18（Asia/Shanghai），Human Owner 明确回复：“批准 ARCH-PLC-001 r7、DS-005 r2、DAA-019 r2 及版本衔接，继续完成联测和清理。”该决定精确批准 `device-simulator::DS-005 r2`、`aiis-ics-arch::ARCH-PLC-001 r7`、`aiis-ics-arch::DAA-019 r2` 及版本衔接；本任务审阅时完整草案 SHA-256 为 `bb94ef1d1b6cc2a88deeb7e984d4e69b98d79412b711fb0c9e46ddf706c93ceb`。Development 按本 r2 沿用的白名单接续，随后 fresh-context Verification；此批准不是 QA 或 Human Owner 最终验收，不改变其他任务状态。

## 附录 A：已批准 DS-005 r1 完整原文

写前完整 SHA-256：`fe007553288adbdd426b1ce7edf9ebd8a2d6d0bfa72a549deeb3fb8341975c75`；围栏内保留原始 UTF-8 字节及末尾换行。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: DS-005
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 ARCH-PLC-001 r6 与 DS-005 r1 -> Development -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: root
Capability: DS 导入完整 PLC JSON 并从保存版本保留外部身份导出
Owner: Device Simulator
Acceptance Chain Reference: 本任务独立遵循 Development Lifecycle Workflow 的精确范围批准、Development、fresh-context Verification 与 Human Owner 最终验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r6; aiis-ics-arch::DAA-019 r1; device-simulator::DS-003 r5; device-simulator::DS-004 r2; aiis-ics-arch::DAA-017 r5
Depends On: 本任务和 ARCH-PLC-001 r6 已获精确范围批准；实际跨端闭环需要 DAA-019 r1 的交付候选。

# DS-005 r1：实例页双向 PLC JSON（范围已批准）

## 1. 目标与范围

DS「实例」页面标题动作区并排提供「导入 PLC JSON」「导出 PLC JSON」及既有新增按钮。英文对应 `Import PLC JSON` / `Export PLC JSON`。导出复用现有 DS-003 r5 的选择保存版本、勾选实例及预览/落盘流程；不以当前草稿冒充保存版本。导入一份符合 [ARCH-PLC-001 r6](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 的 DS 或 DAA producer 文件，预览后新建一个 DS 实例草稿；不覆盖、匹配或合并已有实例。

DS-003 r5 的独立 QA2 已通过、待 Owner 最终验收，原失败与阻塞历史保持；本任务不更改其 spec、tasks 或 checklist。DS-004 r2 当前 `qa_blocked`，其独立验收不因本任务变更。Human Owner 已精确批准本 r1，见 §6；其他任务范围或验收不自动转移到本任务。

## 2. 产品及合同要求

1. 复用 r6 / 已批准 r5 的单 PLC `aiis.plc_points` v1 字段、限制、完整性及严格解析；两种 producer 均应受支持，包括 DAA producer 缺省 DB 层 `source_enabled`。无语言 `display_name` 可达 256 UTF-8 字节，DS 现有 200 字节上限须在本范围内扩展到 256 并保持原值；点编辑器不能加载后静默截断，超限清晰阻断。双语缺省表示两侧空，不从技术名、旧名称、描述、另一语言或 TIA 注释填充。
2. 预览输入原始字节/SHA、外部 origin、来源版本、客户端目标、所有 DB/点、双语、无语言旧名、独立 description、地址和源启用标志。DS 将输入文件仅作为目录来源，不伪造 DB/UDT 及 TIA 结构树。多个 DB 可以绑定同一份原始 JSON；保存并重开后仍能验证原字节/SHA、外部 DB/点身份及逐点本地映射，不能把目录数据降为未经校验的手工点。已保存版本及原有 TIA 来源、确认、历史保持。
3. 文件连接信息只作客户端目标展示；使用者必须单独填写并确认 DS 本机模拟监听 IP、端口及 rack/slot，不能自动拿源 PLC 地址监听或试连。TSAP 显示来源与模拟监听的方向及实际值；DS 自身可表达的非默认 TSAP 不得一律拒绝，不能表达的值须明确提示并阻断，不静默改写。非法、重复端点、实例上限、身份与来源冲突须明确拒绝，不覆盖其他实例。默认不启动，DB 和点默认停用；模拟初值、规则和读写策略不从外部 `source_enabled` 推断。导入只生成草稿，用户按 DS 既有流程完成必要的名称/布局确认并保存版本；运行、加载和启动仍由用户显式操作。
4. 输入文件、所填监听地址、草稿 ETag 和预览结果绑定；文件改变、取消、过期、并发或提交失败时不产生部分实例、来源或映射。对已绑定目录点的技术身份、点集、地址和类型，本期不做差异重导或覆盖；可调整既有允许的显示名、描述及启用/模拟策略，不能削弱源完整性校验。若编辑需要变更目录点集或物理布局，明确拒绝并另立范围。
5. 从已保存的 DS 原生实例及目录导入实例导出都使用现有一份完整合同；后者保留外部 origin、DB/点外部 ID 与本地映射，`export.producer=device_simulator`，payload SHA/版本/时间取 DS 真实保存版本。DB、点的 `source_enabled` 取 DS 当前配置事实；不要求与 DAA 的采集启用值相等。多选每实例一份，重名拒绝、不覆盖、原子发布、逐项结果和取消清理均不弱化 DS-003 r5。
6. 不修改物理 DDL 或迁移已有 profile。若目录绑定无法利用现有存储安全承载，或需白名单外文件/新依赖，停止并回 PM。旧版读取新增可选元数据的结果没有证据时如实标明；不能将导入/导出说成设备布局或运行许可证明。

## 3. 已批准的 Development 文件 allowlist

仅为本任务修改以下相对 `automation-world/device-simulator/` 的明确路径；花括号仅展开所列文件，不是目录通配符。额外文件需回 PM 修订及重新批准。

| 范围 | 文件 |
| --- | --- |
| 运行时数据和来源 | `runtime/src/domain/{mod.rs,configuration.rs,source.rs,layout.rs,plc_catalog.rs}`；`runtime/src/infrastructure/config_store/{mod.rs,queries.rs,transactions.rs}`；`runtime/src/services/{mod.rs,configuration.rs,source_import.rs,catalog_export.rs,layout.rs,naming.rs,versions.rs}`；`runtime/src/app.rs`；可新建 `runtime/src/services/catalog_import.rs` |
| 桌面桥接 | `src-tauri/src/{lib.rs,app.rs}`；`src-tauri/src/commands/{mod.rs,import.rs,catalog_export.rs}`；可新建 `src-tauri/src/commands/catalog_import.rs`；不增加依赖或修改锁文件 |
| 页面与文案 | `src/services/deviceSimulator.ts`；`src/console/composables/useDeviceSimulator.ts`；`src/app/simulator/views/instances/index.vue`；`src/app/simulator/components/{CatalogExportDialog.vue,PointEditor.vue}`；`src/app/simulator/locales/{en-US,zh-CN}.json`；`src/styles/app.css`；可新建 `src/app/simulator/components/CatalogImportDialog.vue` |
| 定向测试和说明 | `runtime/tests/{plc_catalog_export.rs,source_import.rs,configuration_store.rs,point_display_names.rs}`；可新建 `runtime/tests/plc_catalog_import.rs` 和 `tests/plc-catalog-import.test.mjs`；可改 `tests/{plc-catalog-export.test.mjs,point-display-names.test.mjs}`、`tests/{README,README.zh-CN}.md`、`runtime/{README,README.zh-CN}.md`、`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN,CODE_INDEX}.md` |
| STD 事实 | 本 `spec.md` 仅 PM / Human Owner；精确批准后 Development 创建本任务 `tasks.md`，handoff 后 fresh-context Verification 创建本任务 `checklist.md` |

除以上路径，不改现有其他任务 bundle、DDL/migration、环境文件、协议驱动、DS/DAA 之外工程或公共合同。关联 PLAN/catalog 的机械同步由主协调依其权限处理，不视为本角色写入。

## 4. 验收标准

| 编号 | 通过条件 |
| --- | --- |
| DS05-01 | 实例页头可见两种中英文入口；导出勾选保存版本中的实例，旧 DS-003 导出/取消/同名拒绝、多选结果和 selected/loaded 差异提示保持。 |
| DS05-02 | 用 DAA 实际导出且含 DB/UDT 来源、BOOL/INT/REAL、双语、独立 description 的同一文件完成 DS 预览、新建、手动指定 loopback 模拟监听、必要确认及保存；不提供 DB/UDT，不启动实例或连接源 PLC。 |
| DS05-03 | 保存重开后 DS 实际重新导出该实例；原始外部 origin、外部 DB/点 ID、技术名、地址、类型、双语/空值、旧名、description 和 source_path 无损，producer、source_enabled、版本、时间和 payload SHA 反映实际 DS 版本；交 DAA 使用实际文件。 |
| DS05-04 | 双 producer、缺省 DB 启用、可表达及不能表达的非默认 TSAP、同源/身份/端点冲突、原文字节变化、伪造来源、错误类型/长度/地址、禁用点非法布局、并发及取消有针对性正负例；非法整份拒绝，既有对象不变。256 字节无语言旧名可保存、重开并无损导出，超限拒绝。 |
| DS05-05 | 新实例及 DB/点默认停用，用户可按既有流程显式设置模拟策略；输入 DAA 的源启用不等于 DS 授权。既有 DS 原生实例、TIA 导入、版本、确认与其他历史不被改写。 |
| DS05-06 | 经核对的两应用 `.local/dev` 中与 DAA-019 完成父 r6 A06 的实际文件闭环；保留待 DAA 导入文件及 SHA，结果归两任务各自独立验证。不可用静态 fixture 或预览冒充提交。若环境不安全则记录 blocker。 |
| DS05-07 | 运行与改动相称的 Rust、前端及构建验证，检查中文/英文交互和手册；记录候选、命令与限制。测试后只清理本任务可确认的合成对象，已保存历史按实际保留。 |

## 5. 风险、排除项与 handoff

采用 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer` 的相应规则，交 Development 按触达面读取，之后交 fresh-context Verification。本 r1 已获单独精确批准。测试只用经核对的两应用 `.local/dev` 和明确的自有文件；保护 DAA 原 `DEV-PLC-A` 与两端原有历史，若必要条件不能保证则停止。历史目录点集覆盖、FF/CA、真实设备、外部上报、物理 DDL、Windows/VM、部署与发布均不在范围。合成 GUI 验证和新任务 QA 不构成旧任务最终验收。

## 6. 修订与批准

2026-11-17：为用户新增两端页头入口及 DAA→DS 方向提出 r1 草案。Human Owner 审阅列明的精确版本后回复“批准三个版本，继续开发”，精确批准 `device-simulator::DS-005 r1`、`aiis-ics-arch::ARCH-PLC-001 r6`、`aiis-ics-arch::DAA-019 r1` 及父设计旧任务时序衔接。本任务审阅时完整草案 SHA-256 为 `23e9538ceab3d51ad49f05f8cb24a2aa3f6298c19ea77e06a4d738f6a9e62190`。现交 Development 按本白名单实施，随后 fresh-context Verification；Human Owner 最终验收仍待决定，其他任务状态不因本批准改变。
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
