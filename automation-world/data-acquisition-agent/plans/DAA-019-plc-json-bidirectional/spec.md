Task ID: DAA-019
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 DAA-019 r3 及版本衔接 -> Development 记录既有事实并交接 -> fresh-context Verification 独立文档复核 -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA 双语 PLC JSON 双向交换及本次实际 v2 上报字段的有限收尾
Owner: Data Acquisition Agent
Acceptance Chain Reference: Development Lifecycle Workflow；范围批准、Development、fresh-context Verification 和 Human Owner 最终验收各自独立。
Related Task: aiis-ics-arch::ARCH-PLC-001 r7; aiis-ics-arch::ARCH-PLC-001 r8（本次分别获批）; device-simulator::DS-005 r3（本次分别获批）; aiis-ics-arch::ARCH-PLC-002 r1; aiis-ics-arch::DAA-018 r3（历史版本）; aiis-ics-arch::DAA-018 r4（本次分别获批，独立任务）; device-simulator::DS-004 r3（本次分别获批，独立任务）
Depends On: 本 r3、ARCH-PLC-001 r8 及适用版本衔接已获 Human Owner 分别精确范围批准；DS-005 等任务的状态与验收由各自任务单独记录，不自动继承。

# DAA-019 r3：基于既有记录的双向 JSON 与 v2 字段收尾（范围已批准）

## 1. 目标、现状与范围

本 r3 在不重复测试、不操作现场或现有数据的前提下，审阅已发生的双语、DAA→DS→DAA 双向 JSON 手动操作、既有独立检查及本次真实 v2 上报字段观察，以第 3 节的有限证据和第 4 节未验证风险作为本任务新的验收口径。Human Owner 已精确批准 r3 范围及版本衔接；QA 和最终验收尚未发生。

DAA-019 r2 的整体最新结论仍为 `qa_blocked`；QA1 的索引缺漏、QA3 的冲突文案和 QA5 的手册缺陷分别已有后续限定复验记录，原 `qa_failed`、`qa_blocked`、返工和各次证据原样保留于 [checklist.md](checklist.md) 及 [tasks.md](tasks.md)。本 r3 不改写历史 verdict。父 [ARCH-PLC-001 r8](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 和 DS-004 r3、DS-005 r3、DAA-018 r4 均由同一 Human Owner 原话分别精确批准；各任务保留独立状态及验收链，不由本任务继承或改变。

r2 的产品合同作为历史设计依据保留，现行导出文件名按已单独验收的 [ARCH-PLC-002 r1](../../../plans/ARCH-PLC-002-plc-json-export-feedback/spec.md) 接替 r2 的固定 UUID 文件名约定。该任务也修改了与 DAA-019 共用的部分文件：旧 34/35 项候选、自检及 QA 只证明各自记录时的候选；必须按两个任务的交接和证据解释现工作树，不得把旧候选、其历史原生结果或测试自动说成现候选的新验证。

## 2. r3 对原验收的明确调整

| 原 r2 要求 | r3 口径与仍未证明的事实 |
| --- | --- |
| D19-04 / D19-06 及父 r7 §4.1 B：同一次 L2 原生回导直接核对 `importedLocalPlcId`、自动选中并对该实例再导出 | 不再要求补做或补造该次原生 IPC 截获。采用已记录的 Human Owner 实际操作报告、当时实际文件的既有独立比对、服务及前端替身检查，各自按原层级审阅。Owner 后一轮报告的自动选中与四点观察只归该轮；此前 L2 与 L3 的分次观察不拼成同一次证据。原生 IPC 返回值未直接观察，仍属未验证。 |
| D19-05 / D19-07：此前用户 profile 的旧 context、样本及投递关联前后逐项保持 | 数据保护要求不放宽，但不再以补齐那一轮缺失的逐行前测作为本次收尾前置。原记录中可比较的字段和自有合成 profile 服务级检查保留原范围；当时旧 context、samples 其他列及 `sample_delivery` 缺可比逐行前测，无法证明其全部前后相等。后来另一轮的 37 表比较仅证明其所列范围和时点，不能倒证早一轮；缺口不是数据损坏结论，也不是完整保持的证明。 |
| D19-08：两种语言 sentinel 的 fake transport，不发真实 POST | 保留原假 transport 及手册记录；另审阅第 3 节已经发生的真实 v2 上报只读观察，限所列 13 条和一次本机配置。r3 不安排任何新 POST、采集或后端查询；不得将这一观察推广为所有配置、异常路径或历史兼容已验证。 |
| D19-01–03、D19-07、D19-09：原候选的功能、负例、构建和必要原生检查 | 不重跑原测试、构建或 GUI；以既有 Development / QA 实际记录为证据，按执行者、候选、测试层级和未覆盖范围归属。对于没有现存证据的原要求，保留未验证或不在本次有限收尾证明内，不将其补记为通过。 |

## 3. 既有证据与可审阅验收标准

| 编号 | r3 验收标准：只审阅现有记录 |
| --- | --- |
| R3-01 | Development 在任务事实面标明确切工作树、相关候选与 [ARCH-PLC-002 r1](../../../plans/ARCH-PLC-002-plc-json-export-feedback/checklist.md) 的先后及重叠，引用本任务原 Development 自检、QA1–QA6 和可用记录；区分原 `qa_failed`、限定复验及整体 `qa_blocked`。不把后来修改文件视为旧测试当时的原字节，也不声称完整重跑。 |
| R3-02 | 按既有记录审阅 Owner 报告的实际 DAA→DS→DAA 文件往返、当前同源拒绝、选择历史新本机实例、未手工选择即显示新实例及其 4 个点并对该实例再导出；原生 GUI 动作为 Owner 报告，QA 未亲历，不称为独立原生见证。保留 QA 当时对三份真实文件、外部身份、技术字段、双语及 description 的只读比较及其排除项，保留与 GUI 和 IPC 的证据层级差异。 |
| R3-03 | 审阅原有双语入口、空值/description、导入冲突与历史身份隔离、导出逐实例处理、fake transport 和中英文说明的已有检查；明确服务级、替身、静态检查和实际手动观察各自覆盖范围及未覆盖情形。不能把早期 QA 或自检概括为新一轮全功能通过。 |
| R3-04 | 记录协调者 2026-11-18 经用户允许后的只读观察：本机该次 v2 `seq=91–103` 共 13 条均有可靠回执；正文字节 SHA、对应身份和 3 点信息与 MySQL history 对应记录一致。该配置至少一个点的中英文显示名均非空；13 份请求正文没有显示名字段及对应文本，后端点集中未发现显示名字段，所核点字段和值一致。`latest` 为 3 点 `good`、`seq=103`；DS 对应时段日志未见 `WARN` / `ERROR`。这是协调者观察，不是本任务独立 QA、新测试或现场验证；不得复制原始业务值、密钥或私有配置。可追溯来源为本机会话 `~/.codex/sessions/2026/11/16/rollout-2026-11-16T09-24-47-01a1e1f4-eb7e-74d2-b055-3696e1a855ec.jsonl` 约第 28239–28242、28257–28260 行，行号变化时按内容定位；该私有会话不可公开提交，也不是唯一结论载体。 |
| R3-05 | 明确列出第 2 节两项无法倒证的原始缺口、R3-04 的单机单配置及 13 条样本边界，以及旧二进制兼容、Windows/VM、真实 PLC、异常情况和生产采用未验证。记录旧临时工件已按用户同意清理、原件不可再读；先前 tasks / checklist 中的结果与限制继续保留，不能假称重新读取。 |
| R3-06 | 在批准后，Development 仅按既有记录形成精确 r3 文档交接；新的 fresh-context Verification 独立审阅 r3、完整 bundle、现存交接记录与工作树 diff/候选归属，逐项写明证据及限制并自行给出文档复核 verdict。证据不足应如实 `qa_blocked` 或 `qa_failed`，不得预设通过；文档复核通过只进入 Human Owner 最终验收，不等于新做了原生、设备或上报测试。 |

## 4. 风险、排除项与数据保护

Human Owner 已批准第 2 节的验收变更；未验证风险继续保留，最终是否接受该有限交付仍由 Human Owner 在独立复核后决定。既有真实上报是过去的事实，不以其证明旧轮原始前值、当次原生 IPC、其他点集、所有异常分支或持续可靠运行。QA3 对后一轮所列 37 表的检查不是跨库同一瞬间快照，亦不覆盖未列项目。此前协调者曾误点 L1 的测试连接并报告未建立连接；英文原生观察仅覆盖入口、弹窗及预览，未证明英文实际提交或文件写出。未知提交结果仍须先读回，不能盲目重试。

本 r3 仅整理上述双语、双向 JSON 和实际 v2 上报字段的有限证据。不得重跑测试或构建，不启动或操作应用、GUI、采集、上报、设备，不重查用户 profile、后端数据库或 DS 日志；不要求用户再次测试或同意变更真实数据。保留现有配置、版本、历史、样本、队列、回执及原失败/阻塞记录；不得通过删除、迁移、回滚或数据修复制造通过。FF/CA、真实 PLC、Windows/VM、旧版二进制兼容、物理 DDL、部署、发布和生产采用均不在本次范围，且其他任务的 `qa_blocked` 不因此解除。若后续确需新增测试、技术修改或不同风险处理，先回 PM 形成新范围并由 Human Owner 决定。

## 5. 文件边界与交接

PM 本次仅写本 `spec.md`。精确 r3 及所需父衔接已获批准，Development 仅更新本任务 [tasks.md](tasks.md) 必要的 Revision / Status / Handoff 文件头并追加事实、精确候选与 handoff；fresh-context Verification 仅更新本任务 [checklist.md](checklist.md) 必要的文件头并追加独立文档复核和 verdict。两角色均须保留各自原文件头、完整历史及写前 SHA，使旧文件可逐字节重建。不得修改源码、测试、手册、配置、其他任务或索引；主协调者如需机械同步索引，须在相应角色事实存在后依其独立权限办理。

后续角色按实际审阅面使用 `aiis` 与 `project-governance`；涉及 PLC 点位/交换、Rust/IPC、桌面 UI 和中英文证据时，分别按 `plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow` 路由；涉及 v2 API/后端字段合同按 `backend-arch` 路由。角色只审阅既有材料，不因此获得实施或额外测试权限。规格批准、独立文档 QA 与最终验收分别记录；contract_only 角色约定及 diff 审计不宣称平台 ACL 或强制路由。

## 6. 修订与批准状态

2026-11-18（Asia/Shanghai），Human Owner 审阅协调者列出的五份精确收尾草案后，经协调者转达明确回复：

> 批准这组收尾草案

该原话分别精确批准 `aiis-ics-arch::DAA-019 r3`、`aiis-ics-arch::ARCH-PLC-001 r8`、`device-simulator::DS-004 r3`、`device-simulator::DS-005 r3`、`aiis-ics-arch::DAA-018 r4` 及其版本衔接。审阅前本 r3 草案 SHA-256 为 `a2e0b2bd1ad39de70bab9d6de5012a15d0bae0fe70b9bd2101dace5a16cad8d6`；父 r8 登记范围批准后的 spec SHA-256 为 `38085d5f0dd5d9db444008b9e04963371ddff3995cbb050641281ce6517931e5`。两者分别是当时文件的识别值；各任务的批准、QA 与最终验收独立记录，不由父子关联或其他任务自动继承。

该决定只批准已审阅的 r3 收尾范围与衔接，不是 QA 通过、未验证风险的最终接受或 Human Owner 最终验收。原 r1、r2 批准及其 SHA 见下方完整原文，r2 的 `qa_failed` / `qa_blocked` 等历史和证据限制保留。接续为 Development 文档交接、fresh-context Verification 独立文档复核和 Human Owner 最终验收；不重复测试或操作现有应用、数据库与数据。

## 附录 A：已批准 DAA-019 r2 完整原文（含 r1）

写前 r2 完整 SHA-256：`a87a770dcccb0aecadc10cdafb57e7449ab8e258f6c2dbdfbadceaafe0ce1a6e`；其内 r1 围栏正文 SHA-256：`1a3b5765676ecb8f0f225f6e2c41687d763bd6c270fe423fb76498e769d4555e`。外层围栏内保留原始 UTF-8 字节及末尾换行；原有批准仅适用于原 Revision。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: DAA-019
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 ARCH-PLC-001 r7、DAA-019 r2 与 DS-005 r2 及版本衔接 -> Development 接续 -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA 完整 PLC JSON 导出及保留外部身份的新本机实例导入
Owner: Data Acquisition Agent
Acceptance Chain Reference: 本任务独立遵循 Development Lifecycle Workflow 的精确范围批准、Development、fresh-context Verification 与 Human Owner 最终验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r7; device-simulator::DS-005 r2; aiis-ics-arch::DAA-017 r5; aiis-ics-arch::DAA-018 r3; device-simulator::DS-003 r5; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013
Depends On: 本任务 r2、ARCH-PLC-001 r7 和 DS-005 r2 及版本衔接已获 Human Owner 精确批准；跨端闭环需要两端最终交付候选。

# DAA-019 r2：PLC 配置页双向 JSON 与安全验收衔接（已批准）

## 1. 目标与已知状态

DAA「PLC 配置」页面标题动作区提供「导入 PLC JSON」「导出 PLC JSON」及既有新增 PLC 按钮；英文对应 `Import PLC JSON` / `Export PLC JSON`。原 JSON 导入对话框目前挂在点位/采集组的 `SourceImportPanel.vue`：迁移并复用其现有共享状态与对话框，使配置页入口可用、同一时刻不挂载两份目录弹窗；原 DB/UDT 导入及点位编辑保持。

DAA-017 r5 的 DS→DAA 新建导入已经 QA2 通过、待 Human Owner 最终验收；原 QA1 失败及 QA2 阻塞历史保留，本任务不改其三文件。DAA-018 r3 仍 `qa_blocked`，本任务不改变其判定。原 r1 已精确批准并有 Development 候选及自检；本 r2 仅修订 D19-05 的验收衔接，已获 Human Owner 精确批准。

## 2. 导出合同与用户流程

1. 按 [ARCH-PLC-001 r7](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 选择 `saved_draft` 或 `active_revision`，再勾选一个或多个 PLC；每台一份同样完整的 `aiis.plc_points` v1 文件。来源支持 DAA 普通 DB/UDT 导入的已保存配置以及 catalog 导入配置，覆盖当前 `DEV-PLC-A` 这类已确认地址的普通来源，不只支持原 DS JSON。未保存 UI 编辑不混入；真实草稿 ETag、active/loaded/used、来源 payload 原始字节及 SHA 必须如实表达，草稿不能冒称不可变版本。
2. 输出所有已经声明的 DB/点和停用点，按真实保存配置携带 PLC/DB/点技术身份、名称、类型、地址、source_path、两个语言值、独立 description 与可选旧无语言名称。DAA `comment` 映射 `description`；未设置双语输出空串，不从技术名、旧名称或另一语言猜测。DAA 自建 PLC 的 origin 为真实本机 profile / PLC；来源为 catalog 的配置以持久映射保留外部 origin 和外部 DB/点 ID。导出者及所选版本字段须为 DAA 自身事实，不以旧来源冒充；DB 层省略 `source_enabled`，每点取当前 DAA Point.enabled，见父 r7。
3. 逐实例验证完整合同、已确认地址和来源/映射；非法或不可表达值定位并拒绝该实例，不跳过点、不假造 UUID/地址/空 DB。预览客户端连接目标且由用户确认；不能因导出连接设备。每份文件以所选本地 PLC UUID 加 `.json` 命名，文件内仍按映射保留外部 origin 与 ID。选择目录、重名拒绝、原子不覆盖写入、取消及并发、逐实例结果沿用 DS-003 r5 的同等合同；不修改草稿、active、源归档、历史或运行。单个实例失败不能使其他结果冒称全部成功。
4. DAA 当前桌面清单无目录对话框依赖；拟采用与 DS 相同的 Rust `tauri-plugin-dialog = "=2.7.2"`、`default-features = false`，只更新 `src-tauri/Cargo.lock` 中必需传递闭包，不升级其他包、不增加 npm 依赖。DS 和 DAA 当前锁定 Tauri 2.11.3，本机可见插件源码缓存；这不是编译或权限通过证明。Rust 后端通过原生目录选择获得目录并以短期不可猜测令牌绑定预览/实例，前端不传任意文件系统路径。仅在确实需要时对 DAA 现有 capability 加最小权限，不授予宽泛文件系统权限；若需其他依赖或文件，停止回 PM。

## 3. 导入与历史身份处理

1. 在保留 DAA-017 原有严格格式、归档、命名预览和新建事务语义的基础上，接受合法 `device_simulator` 和 `data_acquisition_agent` producer。对 DAA producer，DB 层 `source_enabled` 必须缺省、点层必填；DS producer 则按 r5 验证 DB 和点层。DAA 当前不能表达的非默认 TSAP 明确拒绝；不静默更改。预览并显式确认客户端地址，可在确认前修改到未占用合法端点；不试连。
2. 当前草稿、active 或正在运行的 PLC 与输入外部 origin/身份相同，或目标端点在当前配置冲突时，明确拒绝且不改配置；保留现有 PLC 数量上限并明确提示容量不足。当前 native DAA 自建 PLC 的 origin 也应通过本 profile + PLC 身份识别；对已导入 PLC 使用已持久外部 origin，而非只比较显示名或本地 ID。仅从草稿移除但 active 仍含原实例时，提示用户先按既有流程停采/断连、保存并显式激活移除后的配置；不自动操作。
3. 若同源/外部身份只存在于历史、不在当前草稿、active 或正在运行配置中，提供用户明确选择的「作为新的本机实例导入」；默认不自动通过。为 PLC、每个 DB、每个点和逻辑来源生成新的、与当前及全部保留历史不冲突的本地 UUID；明确展示外部 origin 与本机新身份，并持久化原始 JSON/SHA、外部 DB/点 ID 与本地 ID 的完整一一映射。原输入、预览、端点、配置 ETag 和映射须绑定并在提交前重验；取消、冲突、并发、过期或失败不得部分写入。没有历史冲突的首次导入保持 DAA-017 的既有保留 ID 行为。
   导入确认成功的 IPC 返回原有 `ConfigurationView` 顶层字段及 `importedLocalPlcId`，该值必须来自实际已提交的本机 PLC；前端接收后以它设置 `selectedPlc`、清空所选 DB，不能继续使用外部 `origin.plc_id` 当本机身份。首次同 ID 导入继续正确选中，历史重映射时选中新 ID；提交结果未知时保留现有未知状态和先重读规则，不猜测选中或盲目重试。
4. 新本机实例默认停用、点停用、未分组、无上报绑定；不继承旧 PLC 的 `plc_sources` generation/sequence、样本、队列、回执、历史配置、冻结上报正文或原 reporting binding，也不将旧样本归到新本地 ID。对于输入 SHA 与历史归档相同的情形，只有在逐字节一致、origin 和映射可验证时，才允许底层复用原物理内容；不能覆盖原归档 ID/元数据或跳过当前实例冲突，新的逻辑来源仍与其本地实例对应。历史仍可按原有身份读取，不宣称历史自动合并。
5. 上述映射只放在可审查的配置与来源模型，不改变 SQLite 物理 DDL；现有 catalog 同 ID 分支、DB/UDT tree/leaf 匹配和双库原子性必须保持。重开、普通保存、显式激活、后续重导出均重验目录原文、SHA、外部/本地映射、点集及类型地址；伪造映射或不一致拒绝。目录点技术名、点集、地址和类型不因本任务获得覆盖能力；可继续既有双语、comment、分组、启用编辑。若不能无损隔离旧身份或需要 DDL / 迁移，停止并回 PM，不删除历史来通过测试。
6. 上报 `name` 及 Point/PointFact/v2 原键和值语义不变，双语显示名与无语言旧名不进入实际 v2 外发；对本任务新建对象可用假 transport 验证，不发真实 POST。导入、保存或显式激活不能自动连接、采样或上报。

## 4. 沿用 r1 的 Development 文件 allowlist（r2 已批准）

仅为本任务修改以下相对 `automation-world/data-acquisition-agent/` 的明确路径；花括号仅展开列出的文件。白名单外需回 PM 修订并重新批准。

| 范围 | 文件 |
| --- | --- |
| 合同与本地服务 | `src-tauri/src/domain/{mod.rs,local_configuration.rs,local_runtime.rs,plc_catalog.rs}`；`src-tauri/src/services/{mod.rs,catalog_import.rs,local_configuration.rs,local_point_naming.rs,local_supervisor.rs,local_activation.rs}`；`src-tauri/src/infrastructure/local_store/{mod.rs,configuration.rs}`；可新建 `src-tauri/src/services/catalog_export.rs` |
| 原生桥接与依赖 | `src-tauri/src/{lib.rs,commands/local_acquisition.rs}`；`src-tauri/{Cargo.toml,Cargo.lock}`（仅上述精确插件及其必需闭包）；`src-tauri/capabilities/default.json`（仅必需的最小权限）；可新建 `src-tauri/src/commands/catalog_export.rs`，并在 `src-tauri/src/commands/mod.rs` 注册 |
| 页面与文案 | `src/services/localAcquisition.ts`；`src/console/composables/useLocalAcquisitionConsole.ts`；`src/app/plc/views/diagnostics/index.vue`；`src/app/plc/components/{SourceImportPanel.vue,CatalogImportDialog.vue}`；`src/app/plc/locales/{en-US,zh-CN}.json`；`src/styles/app.css`；可新建 `src/app/plc/components/CatalogExportDialog.vue` |
| 定向测试和说明 | `src-tauri/src/infrastructure/local_store/{catalog_import_tests.rs,source_import_tests.rs,point_naming_tests.rs,sample_upload_tests.rs}`；`src-tauri/src/services/local_delivery_tests.rs`；可新建 `src-tauri/src/infrastructure/local_store/catalog_export_tests.rs`；`tests/{plc-catalog-import.test.mjs,point-editing.test.mjs}`；可新建 `tests/plc-catalog-export.test.mjs` 与 `tests/fixtures/plc-catalog-daa-v1.json`；`src-tauri/src/infrastructure/local_store/{README,README.zh-CN}.md`；`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN,CODE_INDEX}.md` |
| STD 事实 | 本 `spec.md` 仅 PM / Human Owner；精确批准后 Development 创建本任务 `tasks.md`，handoff 后 fresh-context Verification 创建本任务 `checklist.md` |

除以上路径，不改其他任务 bundle、`schema.rs`、物理迁移、`.env`、协议驱动、facts wire 或其他应用/公共合同。关联 PLAN/catalog 的机械同步由主协调依其权限处理。

## 5. 验收标准

| 编号 | 通过条件 |
| --- | --- |
| D19-01 | PLC 配置页头有两个中英文动作；JSON 导入对话框复用/迁移后不重复挂载，原 DB/UDT 和点位编辑正常。按 PLC 勾选导出分别生成文件；未保存 UI 编辑不混入。 |
| D19-02 | 普通 DB/UDT 来源及 catalog 来源各有合规导出证据，含停用点、BOOL/INT/REAL、双语（含空侧）及独立 description；当前 `DEV-PLC-A` 这类保存配置可导出，且实例、来源、历史和上报配置不改变。导出文件头、origin、DAA producer、DB 缺省启用、点 enabled、版本及原 payload SHA 准确。 |
| D19-03 | 接受 DS/DAA 两种合法 producer；非法版本、字段、编码、UUID、端点、TSAP、类型或布局阻断；目录来源映射/SHA 篡改、并发、取消和文件变化均不产生部分提交。现有 DAA-017 DS 文件与 DB/UDT 路径回归。 |
| D19-04 | 当前同源/身份或端点存在时拒绝；只有历史存在时，未选择新本机实例则拒绝，显式选择后采用全新不冲突本地 PLC/DB/点 ID 并持久映射外部身份；重开和再导出核对映射及字段。确认返回的 `importedLocalPlcId` 和界面选中的 PLC 均为实际新本地 ID（首次同 ID 导入仍可用），不是外部 origin；未知结果不猜测选择。原始归档即使 SHA 相同也不能覆盖旧数据。 |
| D19-05 | 按父 r7 §4.1 分层验证：自有临时合成 profile 中实际保存并激活测试 PLC、移出并激活移除版本，验证新本地身份与旧 generation/sequence、样本、上报绑定、队列及回执隔离；既有 Development 针对性服务测试可作为证据供 fresh QA 独立复核，不冒称 GUI。两端 `.local/dev` 则复用 DAA-017 已激活合成 PLC 的真实历史，以实际原生导入、DAA→DS→DAA 文件及两次新本地身份证明当前同源拒绝和历史重映射；本轮 DAA 不激活/采集/上报。新 PLC 和点停用、未分组；原有 `DEV-PLC-A`、8 个旧 revision、context、样本和回执逐项保持；任一必要条件无法保证即 blocked。 |
| D19-06 | 实际以 DAA 导出文件完成 DS 导入、保存、DS 导出，并用该文件在同一 DAA 中真正提交 D19-05 的新实例，核对双语/空值、description、技术字段、外部 ID 和本地新 ID；不是只解析、预览或虚构身份。验前也证明原实例仍在当前配置时导回会明确拒绝。 |
| D19-07 | 多选部分失败、同名文件、目录取消及并发均按实例报告、不覆盖或遗留半文件；导出前后配置/来源/active 和历史事实不变，真实生成时间不同不要求整文件 SHA 相同。 |
| D19-08 | 两种不同语言 sentinel 经过新目录样本和实际 v2 正文构造的假 transport 时均不外发，原程序名、value、严格字段语义保持；不发真实 POST。中英文手册说明新入口、历史分离及手工版本/地址确认。 |
| D19-09 | 正式交付候选按范围完成 Rust、Node、类型及构建检查和必要 macOS 原生操作；记录实际命令、结果、版本、两文件 SHA 与限制。原生链只使用已核对的自有合成对象与 loopback 信息；测试后仅经正常应用清理可确认的任务对象，历史按引用保留。 |

## 6. 本机验证、风险与 handoff

用户已授权两端各自 `.local/dev`、自有临时合成 profile 的受控测试及任务对象清理，具体 r2 验收衔接已获精确批准。操作前核对实际进程、profile、active 和草稿、原实例、自动连接/采集/上报、目标端口及是否存在待恢复 activation intent；状态不明则停止，不得修改意图绕过。不得修改或删除 `DEV-PLC-A`、真实配置、历史、样本、队列或回执。D19-05 的保存、激活、移除和再次激活只在自有合成 profile 执行；用户 DAA `.local/dev` 本轮不激活，复用此前 QA 的合成历史并以 UI 草稿完成真实往返，细节见父 r7 §4.1。`DEV-PLC-A` 仅只读导出供 DS 验证普通 DB/UDT 来源；不能把其配置冒称合成。新审计或受历史引用的测试来源如实保留，不能声称整个 profile 无写。

Development 按触达面读取 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer` 并按已精确批准的本 r2 沿用 r1 白名单接续；随后 fresh-context Verification 独立复核。覆盖现有 PLC、自动合并历史、原身份复用、物理 DDL、真实设备、真实 POST、FF/CA、Windows/VM、部署与发布均不在范围。Human Owner 最终验收另行决定。

## 7. r1 修订与批准（历史）

2026-11-17：为双向交换及已删除实例的历史隔离重新导入形成 r1 草案。Human Owner 审阅列明的精确版本后回复“批准三个版本，继续开发”，精确批准 `aiis-ics-arch::DAA-019 r1`、`aiis-ics-arch::ARCH-PLC-001 r6`、`device-simulator::DS-005 r1` 及父设计旧任务时序衔接。本任务审阅时完整草案 SHA-256 为 `576646f841feebf06258435a7dc0f089d7e40be5c96da6676a204eb318161529`。当时交 Development 按本白名单实施，随后 fresh-context Verification；Human Owner 最终验收仍待决定，其他任务状态不因本批准改变。

## 8. r2 修订及 Human Owner 精确批准

2026-11-17：当前用户 DAA `.local/dev` 已有 8 个配置 revision，继续激活会触发旧版本裁剪风险。按父 r7 将 D19-05 分为自有合成 profile 激活与历史验证、两端 `.local/dev` 不激活的真实原生文件往返，并用 `DEV-PLC-A` 只读文件验证 DS 的普通 DB/UDT 来源。D19-01–04、06–09、产品功能、文件 allowlist 与数据保护不变；现有 r1 代码候选和自检按原 tasks 保留，不倒记为 r2 QA 或最终验收。

2026-11-18（Asia/Shanghai），Human Owner 明确回复：“批准 ARCH-PLC-001 r7、DS-005 r2、DAA-019 r2 及版本衔接，继续完成联测和清理。”该决定精确批准 `aiis-ics-arch::DAA-019 r2`、`aiis-ics-arch::ARCH-PLC-001 r7`、`device-simulator::DS-005 r2` 及版本衔接；本任务审阅时完整草案 SHA-256 为 `48721591ef64ab11100977858c58f51deea08ade5caf26bfe0618d692ed53705`。Development 按本 r2 沿用的白名单接续，随后 fresh-context Verification；此批准不是 QA 或 Human Owner 最终验收，不改变其他任务状态。

## 附录 A：已批准 DAA-019 r1 完整原文

写前完整 SHA-256：`1a3b5765676ecb8f0f225f6e2c41687d763bd6c270fe423fb76498e769d4555e`；围栏内保留原始 UTF-8 字节及末尾换行。

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~markdown
Task ID: DAA-019
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 ARCH-PLC-001 r6 与 DAA-019 r1 -> Development -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA 完整 PLC JSON 导出及保留外部身份的新本机实例导入
Owner: Data Acquisition Agent
Acceptance Chain Reference: 本任务独立遵循 Development Lifecycle Workflow 的精确范围批准、Development、fresh-context Verification 与 Human Owner 最终验收。
Related Task: aiis-ics-arch::ARCH-PLC-001 r6; device-simulator::DS-005 r1; aiis-ics-arch::DAA-017 r5; aiis-ics-arch::DAA-018 r3; device-simulator::DS-003 r5; aiis-ics-arch::DAA-010; aiis-ics-arch::DAA-013
Depends On: 本任务和 ARCH-PLC-001 r6 已获精确范围批准；实际跨端闭环需要 DS-005 r1 的交付候选。

# DAA-019 r1：PLC 配置页双向 JSON 与安全再导入（范围已批准）

## 1. 目标与已知状态

DAA「PLC 配置」页面标题动作区提供「导入 PLC JSON」「导出 PLC JSON」及既有新增 PLC 按钮；英文对应 `Import PLC JSON` / `Export PLC JSON`。原 JSON 导入对话框目前挂在点位/采集组的 `SourceImportPanel.vue`：迁移并复用其现有共享状态与对话框，使配置页入口可用、同一时刻不挂载两份目录弹窗；原 DB/UDT 导入及点位编辑保持。

DAA-017 r5 的 DS→DAA 新建导入已经 QA2 通过、待 Human Owner 最终验收；原 QA1 失败及 QA2 阻塞历史保留，本任务不改其三文件。DAA-018 r3 仍 `qa_blocked`，本任务不改变其判定。Human Owner 已精确批准本 r1，见 §7；父设计或用户此前一般开工意向未被推断为批准。

## 2. 导出合同与用户流程

1. 按 [ARCH-PLC-001 r6](../../../plans/ARCH-PLC-001-shared-plc-point-json/spec.md) 选择 `saved_draft` 或 `active_revision`，再勾选一个或多个 PLC；每台一份同样完整的 `aiis.plc_points` v1 文件。来源支持 DAA 普通 DB/UDT 导入的已保存配置以及 catalog 导入配置，覆盖当前 `DEV-PLC-A` 这类已确认地址的普通来源，不只支持原 DS JSON。未保存 UI 编辑不混入；真实草稿 ETag、active/loaded/used、来源 payload 原始字节及 SHA 必须如实表达，草稿不能冒称不可变版本。
2. 输出所有已经声明的 DB/点和停用点，按真实保存配置携带 PLC/DB/点技术身份、名称、类型、地址、source_path、两个语言值、独立 description 与可选旧无语言名称。DAA `comment` 映射 `description`；未设置双语输出空串，不从技术名、旧名称或另一语言猜测。DAA 自建 PLC 的 origin 为真实本机 profile / PLC；来源为 catalog 的配置以持久映射保留外部 origin 和外部 DB/点 ID。导出者及所选版本字段须为 DAA 自身事实，不以旧来源冒充；DB 层省略 `source_enabled`，每点取当前 DAA Point.enabled，见父 r6。
3. 逐实例验证完整合同、已确认地址和来源/映射；非法或不可表达值定位并拒绝该实例，不跳过点、不假造 UUID/地址/空 DB。预览客户端连接目标且由用户确认；不能因导出连接设备。每份文件以所选本地 PLC UUID 加 `.json` 命名，文件内仍按映射保留外部 origin 与 ID。选择目录、重名拒绝、原子不覆盖写入、取消及并发、逐实例结果沿用 DS-003 r5 的同等合同；不修改草稿、active、源归档、历史或运行。单个实例失败不能使其他结果冒称全部成功。
4. DAA 当前桌面清单无目录对话框依赖；拟采用与 DS 相同的 Rust `tauri-plugin-dialog = "=2.7.2"`、`default-features = false`，只更新 `src-tauri/Cargo.lock` 中必需传递闭包，不升级其他包、不增加 npm 依赖。DS 和 DAA 当前锁定 Tauri 2.11.3，本机可见插件源码缓存；这不是编译或权限通过证明。Rust 后端通过原生目录选择获得目录并以短期不可猜测令牌绑定预览/实例，前端不传任意文件系统路径。仅在确实需要时对 DAA 现有 capability 加最小权限，不授予宽泛文件系统权限；若需其他依赖或文件，停止回 PM。

## 3. 导入与历史身份处理

1. 在保留 DAA-017 原有严格格式、归档、命名预览和新建事务语义的基础上，接受合法 `device_simulator` 和 `data_acquisition_agent` producer。对 DAA producer，DB 层 `source_enabled` 必须缺省、点层必填；DS producer 则按 r5 验证 DB 和点层。DAA 当前不能表达的非默认 TSAP 明确拒绝；不静默更改。预览并显式确认客户端地址，可在确认前修改到未占用合法端点；不试连。
2. 当前草稿、active 或正在运行的 PLC 与输入外部 origin/身份相同，或目标端点在当前配置冲突时，明确拒绝且不改配置；保留现有 PLC 数量上限并明确提示容量不足。当前 native DAA 自建 PLC 的 origin 也应通过本 profile + PLC 身份识别；对已导入 PLC 使用已持久外部 origin，而非只比较显示名或本地 ID。仅从草稿移除但 active 仍含原实例时，提示用户先按既有流程停采/断连、保存并显式激活移除后的配置；不自动操作。
3. 若同源/外部身份只存在于历史、不在当前草稿、active 或正在运行配置中，提供用户明确选择的「作为新的本机实例导入」；默认不自动通过。为 PLC、每个 DB、每个点和逻辑来源生成新的、与当前及全部保留历史不冲突的本地 UUID；明确展示外部 origin 与本机新身份，并持久化原始 JSON/SHA、外部 DB/点 ID 与本地 ID 的完整一一映射。原输入、预览、端点、配置 ETag 和映射须绑定并在提交前重验；取消、冲突、并发、过期或失败不得部分写入。没有历史冲突的首次导入保持 DAA-017 的既有保留 ID 行为。
   导入确认成功的 IPC 返回原有 `ConfigurationView` 顶层字段及 `importedLocalPlcId`，该值必须来自实际已提交的本机 PLC；前端接收后以它设置 `selectedPlc`、清空所选 DB，不能继续使用外部 `origin.plc_id` 当本机身份。首次同 ID 导入继续正确选中，历史重映射时选中新 ID；提交结果未知时保留现有未知状态和先重读规则，不猜测选中或盲目重试。
4. 新本机实例默认停用、点停用、未分组、无上报绑定；不继承旧 PLC 的 `plc_sources` generation/sequence、样本、队列、回执、历史配置、冻结上报正文或原 reporting binding，也不将旧样本归到新本地 ID。对于输入 SHA 与历史归档相同的情形，只有在逐字节一致、origin 和映射可验证时，才允许底层复用原物理内容；不能覆盖原归档 ID/元数据或跳过当前实例冲突，新的逻辑来源仍与其本地实例对应。历史仍可按原有身份读取，不宣称历史自动合并。
5. 上述映射只放在可审查的配置与来源模型，不改变 SQLite 物理 DDL；现有 catalog 同 ID 分支、DB/UDT tree/leaf 匹配和双库原子性必须保持。重开、普通保存、显式激活、后续重导出均重验目录原文、SHA、外部/本地映射、点集及类型地址；伪造映射或不一致拒绝。目录点技术名、点集、地址和类型不因本任务获得覆盖能力；可继续既有双语、comment、分组、启用编辑。若不能无损隔离旧身份或需要 DDL / 迁移，停止并回 PM，不删除历史来通过测试。
6. 上报 `name` 及 Point/PointFact/v2 原键和值语义不变，双语显示名与无语言旧名不进入实际 v2 外发；对本任务新建对象可用假 transport 验证，不发真实 POST。导入、保存或显式激活不能自动连接、采样或上报。

## 4. 已批准的 Development 文件 allowlist

仅为本任务修改以下相对 `automation-world/data-acquisition-agent/` 的明确路径；花括号仅展开列出的文件。白名单外需回 PM 修订并重新批准。

| 范围 | 文件 |
| --- | --- |
| 合同与本地服务 | `src-tauri/src/domain/{mod.rs,local_configuration.rs,local_runtime.rs,plc_catalog.rs}`；`src-tauri/src/services/{mod.rs,catalog_import.rs,local_configuration.rs,local_point_naming.rs,local_supervisor.rs,local_activation.rs}`；`src-tauri/src/infrastructure/local_store/{mod.rs,configuration.rs}`；可新建 `src-tauri/src/services/catalog_export.rs` |
| 原生桥接与依赖 | `src-tauri/src/{lib.rs,commands/local_acquisition.rs}`；`src-tauri/{Cargo.toml,Cargo.lock}`（仅上述精确插件及其必需闭包）；`src-tauri/capabilities/default.json`（仅必需的最小权限）；可新建 `src-tauri/src/commands/catalog_export.rs`，并在 `src-tauri/src/commands/mod.rs` 注册 |
| 页面与文案 | `src/services/localAcquisition.ts`；`src/console/composables/useLocalAcquisitionConsole.ts`；`src/app/plc/views/diagnostics/index.vue`；`src/app/plc/components/{SourceImportPanel.vue,CatalogImportDialog.vue}`；`src/app/plc/locales/{en-US,zh-CN}.json`；`src/styles/app.css`；可新建 `src/app/plc/components/CatalogExportDialog.vue` |
| 定向测试和说明 | `src-tauri/src/infrastructure/local_store/{catalog_import_tests.rs,source_import_tests.rs,point_naming_tests.rs,sample_upload_tests.rs}`；`src-tauri/src/services/local_delivery_tests.rs`；可新建 `src-tauri/src/infrastructure/local_store/catalog_export_tests.rs`；`tests/{plc-catalog-import.test.mjs,point-editing.test.mjs}`；可新建 `tests/plc-catalog-export.test.mjs` 与 `tests/fixtures/plc-catalog-daa-v1.json`；`src-tauri/src/infrastructure/local_store/{README,README.zh-CN}.md`；`{README,README.zh-CN,USER_GUIDE,USER_GUIDE.zh-CN,CODE_INDEX}.md` |
| STD 事实 | 本 `spec.md` 仅 PM / Human Owner；精确批准后 Development 创建本任务 `tasks.md`，handoff 后 fresh-context Verification 创建本任务 `checklist.md` |

除以上路径，不改其他任务 bundle、`schema.rs`、物理迁移、`.env`、协议驱动、facts wire 或其他应用/公共合同。关联 PLAN/catalog 的机械同步由主协调依其权限处理。

## 5. 验收标准

| 编号 | 通过条件 |
| --- | --- |
| D19-01 | PLC 配置页头有两个中英文动作；JSON 导入对话框复用/迁移后不重复挂载，原 DB/UDT 和点位编辑正常。按 PLC 勾选导出分别生成文件；未保存 UI 编辑不混入。 |
| D19-02 | 普通 DB/UDT 来源及 catalog 来源各有合规导出证据，含停用点、BOOL/INT/REAL、双语（含空侧）及独立 description；当前 `DEV-PLC-A` 这类保存配置可导出，且实例、来源、历史和上报配置不改变。导出文件头、origin、DAA producer、DB 缺省启用、点 enabled、版本及原 payload SHA 准确。 |
| D19-03 | 接受 DS/DAA 两种合法 producer；非法版本、字段、编码、UUID、端点、TSAP、类型或布局阻断；目录来源映射/SHA 篡改、并发、取消和文件变化均不产生部分提交。现有 DAA-017 DS 文件与 DB/UDT 路径回归。 |
| D19-04 | 当前同源/身份或端点存在时拒绝；只有历史存在时，未选择新本机实例则拒绝，显式选择后采用全新不冲突本地 PLC/DB/点 ID 并持久映射外部身份；重开和再导出核对映射及字段。确认返回的 `importedLocalPlcId` 和界面选中的 PLC 均为实际新本地 ID（首次同 ID 导入仍可用），不是外部 origin；未知结果不猜测选择。原始归档即使 SHA 相同也不能覆盖旧数据。 |
| D19-05 | 用曾激活的合成 PLC 产生真实历史后，将其移出当前配置并激活移除版本，重新导入实际 DS 文件：新 ID 不继承旧 generation/sequence、样本、上报绑定、队列或回执；新 PLC 和点停用且未分组，无自动采集/POST。旧样本、队列、回执及绑定的隔离可使用单个自有合成测试环境验证，无须为了原生闭环制造真实上报或测试样本。旧历史和原有 `DEV-PLC-A` 逐项保持；任一条件无法保证即 blocked。 |
| D19-06 | 实际以 DAA 导出文件完成 DS 导入、保存、DS 导出，并用该文件在同一 DAA 中真正提交 D19-05 的新实例，核对双语/空值、description、技术字段、外部 ID 和本地新 ID；不是只解析、预览或虚构身份。验前也证明原实例仍在当前配置时导回会明确拒绝。 |
| D19-07 | 多选部分失败、同名文件、目录取消及并发均按实例报告、不覆盖或遗留半文件；导出前后配置/来源/active 和历史事实不变，真实生成时间不同不要求整文件 SHA 相同。 |
| D19-08 | 两种不同语言 sentinel 经过新目录样本和实际 v2 正文构造的假 transport 时均不外发，原程序名、value、严格字段语义保持；不发真实 POST。中英文手册说明新入口、历史分离及手工版本/地址确认。 |
| D19-09 | 正式交付候选按范围完成 Rust、Node、类型及构建检查和必要 macOS 原生操作；记录实际命令、结果、版本、两文件 SHA 与限制。原生链只使用已核对的自有合成对象与 loopback 信息；测试后仅经正常应用清理可确认的任务对象，历史按引用保留。 |

## 6. 本机验证、风险与 handoff

用户已授权两端各自 `.local/dev` 的受控测试和任务对象清理。操作前核对实际进程、profile、active 和草稿、原实例、自动连接/采集/上报与目标端口；不得修改或删除 `DEV-PLC-A`、真实配置、历史、样本、队列或回执。为验证 D19-05 可以仅对新建、唯一标识的合成 PLC 显式激活形成历史，随后正常移除该对象并激活移除后的配置；预先无法证明不触发既有实例或真实上报时停止，不通过修改既有对象来绕过。新 revision、运行审计或受历史引用的测试来源可保留，不能声称整个 profile 无写。

Development 按触达面读取 `aiis`、`plc-point-mapping`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow`、`code-document-indexer` 并按本 r1 白名单实施；随后 fresh-context Verification 独立复核。覆盖现有 PLC、自动合并历史、原身份复用、物理 DDL、真实设备、真实 POST、FF/CA、Windows/VM、部署与发布均不在范围。Human Owner 最终验收另行决定。

## 7. 修订与批准

2026-11-17：为双向交换及已删除实例的历史隔离重新导入形成 r1 草案。Human Owner 审阅列明的精确版本后回复“批准三个版本，继续开发”，精确批准 `aiis-ics-arch::DAA-019 r1`、`aiis-ics-arch::ARCH-PLC-001 r6`、`device-simulator::DS-005 r1` 及父设计旧任务时序衔接。本任务审阅时完整草案 SHA-256 为 `576646f841feebf06258435a7dc0f089d7e40be5c96da6676a204eb318161529`。现交 Development 按本白名单实施，随后 fresh-context Verification；Human Owner 最终验收仍待决定，其他任务状态不因本批准改变。
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
