Task ID: ARCH-PLC-002
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已精确批准 ARCH-PLC-002 r1 -> Development -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS 与 DAA 的逐 PLC JSON 导出文件命名及结果反馈
Owner: Automation World / Device Simulator 与 Data Acquisition Agent
Acceptance Chain Reference: Development Lifecycle Workflow；本任务的精确范围批准、Development、fresh-context Verification 和 Human Owner 最终验收分别记录。
Related Task: aiis-ics-arch::ARCH-PLC-001 r7; device-simulator::DS-003 r5; device-simulator::DS-005 r2; aiis-ics-arch::DAA-019 r2

# ARCH-PLC-002 r1：PLC JSON 导出命名与结果反馈（已批准）

## 1. 目标与衔接

Human Owner 希望两端导出成功时有醒目反馈，并可自定义 JSON 文件名；一次选多台时，每台分别命名和报告结果。本任务只处理 DS「实例」与 DAA「PLC 配置」现有的导出流程，不调整导入或设备配置。

当前 [DS-003 r5](../../device-simulator/plans/DS-003-plc-json-export/spec.md)、[DAA-019 r2](../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/spec.md) 的导出使用本机实例/PLC UUID 加 `.json` 固定命名；本草案获精确批准并交付后，**仅在新候选中**以本任务的可编辑文件名规则接替该文件外命名约定。旧规格、Development 和 QA 记录均作为原时点事实保留，不倒改旧任务状态。[ARCH-PLC-001 r7](../ARCH-PLC-001-shared-plc-point-json/spec.md) 的 JSON v1 内容、逐 PLC 完整性、导入、身份映射和安全边界不因文件名变化而改变。

现有两端原生文件联测及各自独立 QA 正在进行；本草案不授权更改它们的候选或中断测试。获批后，在修改共同源码前，协调者须确认现有人工联测、相关返工和该候选所需 QA 取证不再依赖被覆盖的文件，并固定候选及证据；若旧任务仍需同文件返工或复验，先协调隔离与衔接。旧任务的最终验收仍由各自 Human Owner 决定，不因本任务提前通过或自动取消。

## 2. 文件命名与用户操作

1. 在现有导出对话框中，所选每台 PLC/实例均显示一个可编辑的**完整文件名**。默认取所选保存来源中的 PLC/实例名称加 `.json`；若名称已以 `.json` 结尾（大小写不敏感）则不重复追加。单选与多选均可逐台修改；界面同时显示对应 PLC/实例名称，避免混淆。默认名本身非法或同批重复时明确提示用户修改，不静默改名、自动编号或覆盖。
2. 完整文件名须以 `.json` 结尾（扩展名大小写不敏感），扩展名前须有非空且非全空格的名称；不得超过 255 个 UTF-8 字节，包括扩展名。只允许单个文件名，不接受目录或绝对路径；拒绝 `/`、`\`、`<`、`>`、`:`、`"`、`|`、`?`、`*`、NUL、ASCII 控制字符及 DEL，拒绝扩展名前的名称以空格或点结尾，以及 Windows 保留设备名 `CON`、`PRN`、`AUX`、`NUL`、`COM1`–`COM9`、`LPT1`–`LPT9`（不区分大小写，包括带扩展名的形式）。普通中文等合法 Unicode 名称可用。具体原因在对应行以中英文提示，服务端独立校验，不能只依赖前端。
3. 同一批选择的文件名按大小写不敏感比较；重复时标出冲突项，用户修改后才能预览提交。文件名与 PLC 本机身份一一绑定，不以显示顺序或名称推断身份。目标目录已有同名项时明确标为冲突并拒绝覆盖，其他有效项仍可按既有逐项结果导出；目录、文件或权限在检查后变化时以实际原子创建结果为准，不覆盖现有文件。目标文件系统还可能识别额外的大小写或 Unicode 名称别名，发生真实冲突时对应项失败并提示，不能以预览成功冒充落盘成功。
4. 沿用两端原生目录选择、当前授权令牌、有效期、原子不覆盖落盘和临时文件清理；前端只传用户填写的单个**文件名**供服务端验证，不能传任意目录或路径。用户修改来源、选择或文件名后，旧内容预览及目录冲突检查失效；可返回修改后重新预览和核对目录。取消或关闭预览不写文件；并发、过期、路径替换或取消不得造成覆盖或冒称成功。保留现有 DS 保存版本及 selected/loaded 差异确认，DAA 保存草稿/active 来源和目标确认。
5. 文件名只决定本次所选目录中的外部文件名，不写入 PLC/DB/点 ID、origin、producer、版本、显示名或其他 JSON 内容，不更改配置或历史。落盘字节和 SHA 须与该次有效内容预览一致；不同次预览的真实导出时间可不同，不要求不同时刻的整文件 SHA 一致。仍为一台 PLC 一个完整 JSON；沿用原格式限制和不可表达内容的拒绝规则。

## 3. 结果反馈

1. 导出提交返回后，两端在导出对话框顶部的不随内容区滚动的位置，或同等无需滚动即可见的位置显示醒目的结果摘要，直到用户关闭或开始新的导出流程。摘要区分全部成功、部分成功、全部失败及存在未知结果，并展示各状态数量；不能把部分成功或未知说成全部成功。
2. 每台显示 PLC/实例名称、实际目标文件名及 `written`、`failed` 或 `unknown` 的用户可读状态；明确失败原因，成功项保留实际文件 SHA，临时文件清理未完成沿用既有提示。若整次 IPC 结果未知而没有逐项回执，只能对未确认的项报告未知，不能猜测成功或失败。未知时提示先检查所选目录和文件，再决定后续操作；不自动重试或重复写入。
3. 新增用户可见文本和错误提示均提供对应中英文；保持现有入口、版本/点位预览及取消行为，不增加命名模板、批量重命名规则、文件自动打开或其他无关功能。

## 4. Development 精确文件范围（已批准）

仅允许修改以下路径；花括号仅展开列出的文件，不是目录通配符。必要时可修改同一列中的既有测试以适配导出 IPC 参数，但不得删除其既有安全断言。若必须修改其他文件或增加依赖，停止并回 PM 修订。

| 范围 | 文件 |
| --- | --- |
| DS 导出服务及桥 | `automation-world/device-simulator/runtime/src/services/catalog_export.rs`；`automation-world/device-simulator/src-tauri/src/commands/catalog_export.rs`；`automation-world/device-simulator/src/services/deviceSimulator.ts` |
| DS 页面及文案 | `automation-world/device-simulator/src/app/simulator/components/CatalogExportDialog.vue`；`automation-world/device-simulator/src/app/simulator/locales/{en-US,zh-CN}.json`；`automation-world/device-simulator/src/styles/app.css` |
| DS 测试及手册 | `automation-world/device-simulator/runtime/tests/{plc_catalog_export.rs,plc_catalog_import.rs}`；`automation-world/device-simulator/tests/plc-catalog-export.test.mjs`；`automation-world/device-simulator/{USER_GUIDE.md,USER_GUIDE.zh-CN.md}` |
| DAA 导出服务及桥 | `automation-world/data-acquisition-agent/src-tauri/src/services/catalog_export.rs`；`automation-world/data-acquisition-agent/src-tauri/src/commands/catalog_export.rs`；`automation-world/data-acquisition-agent/src-tauri/src/commands/local_acquisition.rs`；`automation-world/data-acquisition-agent/src/services/localAcquisition.ts` |
| DAA 页面及文案 | `automation-world/data-acquisition-agent/src/app/plc/components/CatalogExportDialog.vue`；`automation-world/data-acquisition-agent/src/app/plc/locales/{en-US,zh-CN}.json`；`automation-world/data-acquisition-agent/src/styles/app.css` |
| DAA 测试及手册 | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/{catalog_export_tests.rs,catalog_import_tests.rs}`；`automation-world/data-acquisition-agent/tests/plc-catalog-export.test.mjs`；`automation-world/data-acquisition-agent/{USER_GUIDE.md,USER_GUIDE.zh-CN.md}` |
| STD 事实 | 本 `spec.md` 仅 PM / Human Owner；精确批准后 Development 创建本任务 `tasks.md`，handoff 后 fresh-context Verification 创建本任务 `checklist.md`。 |

不新增依赖、修改锁文件、数据结构 DDL、环境配置、JSON schema、导入器、PLC 协议或其他应用。关联 PLAN / catalog 的机械同步由主协调者按其权限处理，不由本 PM 修改。

## 5. 验收标准

| 编号 | 通过条件 |
| --- | --- |
| E01 | DS 和 DAA 各在现有导出流程中按所选保存来源列出每台的默认文件名；单台及多台可逐项修改，默认名不重复添加 `.json`，实际落盘使用所确认文件名。中文和英文界面均可理解。 |
| E02 | 合法中文名称可用；空名、缺扩展名、超长、路径分隔/穿越、控制字符、非法字符、尾随空格/点和保留设备名均由服务端拒绝且对应提示；同批大小写重复逐项提示，修改后可继续。绕过前端的请求不能写出选择目录之外。 |
| E03 | 预览后改文件名、改选择或取消使旧确认失效；目标已存在、预览后被创建、目录身份变更、并发与取消均不覆盖原文件或留下未报告的半文件。同批一项目标已存在或内容无效时，其他有效项可按既有流程导出并分别报告；批内重名须先按 §2.3 修改。 |
| E04 | 单项成功和多项全部成功时顶部醒目显示成功；部分失败、全部失败及结果未知均明确区分，列出每台实际文件名和状态；无回执时不猜测、不自动重试。界面滚动较长点表后仍易于看到摘要。 |
| E05 | 同一次有效预览的写出文件 SHA 与预览一致；对照相同保存来源的文件内容，外部 origin、PLC/DB/点 ID、技术字段、双语、description、来源版本及启停语义不因文件名改变。不同次 `exported_at` 可不同。两端现有完整导出、导入与新旧身份映射回归保持。 |
| E06 | 在 macOS 原生两端各以一台已保存 PLC/实例实际修改文件名、导出并观察醒目成功反馈，检查中英文文案；多台命名、部分结果、未知回执和竞争用有针对性的自动化/替身验证，不强制用户手工创建多台或重复联测。可使用已授权的各自 `.local/dev` 中已保存来源或明确的自有测试对象，也可使用应用目录内自有临时合成 profile；均须先核对实际 profile、进程和自动运行状态。按真实测试层级记录，运行与改动相称的 Rust、Node、类型及构建检查。 |
| E07 | 双语手册更新原 UUID 固定命名说法，说明自定义、冲突、部分结果与未知检查。测试只使用本任务确认的输出目录，保护既有实例、配置、来源、版本与历史；不为测试在用户 `.local/dev` 中另建配置版本或触发历史裁剪。临时资源只在确认任务归属、无运行或证据依赖后按 workflow 清理。 |

## 6. 风险、排除项和 handoff

- 仅指定跨平台保守文件名校验；现有导出落盘的非 Unix 平台实现和 Windows 原生验证不在本任务内，不因名称合法而宣称 Windows 已支持。目标目录的真实文件系统规则或并发变化仍可能导致单项失败。
- 用户已授权使用两端各自 `.local/dev` 和应用目录内自有临时 profile；若已保存来源不能安全满足单台验证，则使用自有临时合成 profile，不为方便验证改动用户旧配置。`.local/dev` 中已有来源只读导出，不能冒称合成；临时文件不进入仓库。仅可清理明确属于本任务的测试对象，已被历史引用的记录保留。不连接真实 PLC、不采集、不真实 POST，不修改或删除用户既有实例、配置、来源、版本、样本、队列与回执；不因测试在用户 profile 中保存配置版本或激活。FF、CA、VM、部署、发布和生产采用不在范围。
- Development 按触达面使用 `aiis`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer`；Verification 使用 fresh context 独立核对实际候选、文件范围、测试及证据，Human Owner 最终验收单独决定。角色是 contract_only，不宣称平台 ACL 或自动强制路由。
- 未获 Human Owner 对 **`aiis-ics-arch::ARCH-PLC-002 r1`** 的精确范围批准前，不实施或标记通过。本草案不承诺旧任务 QA 结果，不授予真实设备、上报、数据库迁移、部署或发布授权。

## 7. Human Owner 精确范围批准

2026-11-18（Asia/Shanghai），Human Owner 明确回复：

> 批准 ARCH-PLC-002 r1，继续开发

该决定精确批准 `aiis-ics-arch::ARCH-PLC-002 r1` 的范围、文件 allowlist、验收与本规格所述衔接；审阅时完整草案 SHA-256 为 `ce9ec4848957d6d1e4f28e4c969451e0c017a814bde658ca055fa6ec3422c39b`。Development 按本版本接续，随后由 fresh-context Verification 独立验证；此批准不表示 QA 通过或 Human Owner 最终验收，也不改变其他任务状态。

## 附录 A：批准前 r1 草案完整原文

围栏内保留批准前草案的原始 UTF-8 字节及末尾换行，SHA-256 为 `ce9ec4848957d6d1e4f28e4c969451e0c017a814bde658ca055fa6ec3422c39b`。

~~~~markdown
Task ID: ARCH-PLC-002
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 待 Human Owner 精确批准 ARCH-PLC-002 r1 -> Development -> fresh-context Verification -> Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS 与 DAA 的逐 PLC JSON 导出文件命名及结果反馈
Owner: Automation World / Device Simulator 与 Data Acquisition Agent
Acceptance Chain Reference: Development Lifecycle Workflow；本任务的精确范围批准、Development、fresh-context Verification 和 Human Owner 最终验收分别记录。
Related Task: aiis-ics-arch::ARCH-PLC-001 r7; device-simulator::DS-003 r5; device-simulator::DS-005 r2; aiis-ics-arch::DAA-019 r2

# ARCH-PLC-002 r1：PLC JSON 导出命名与结果反馈（待批准）

## 1. 目标与衔接

Human Owner 希望两端导出成功时有醒目反馈，并可自定义 JSON 文件名；一次选多台时，每台分别命名和报告结果。本任务只处理 DS「实例」与 DAA「PLC 配置」现有的导出流程，不调整导入或设备配置。

当前 [DS-003 r5](../../device-simulator/plans/DS-003-plc-json-export/spec.md)、[DAA-019 r2](../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/spec.md) 的导出使用本机实例/PLC UUID 加 `.json` 固定命名；本草案获精确批准并交付后，**仅在新候选中**以本任务的可编辑文件名规则接替该文件外命名约定。旧规格、Development 和 QA 记录均作为原时点事实保留，不倒改旧任务状态。[ARCH-PLC-001 r7](../ARCH-PLC-001-shared-plc-point-json/spec.md) 的 JSON v1 内容、逐 PLC 完整性、导入、身份映射和安全边界不因文件名变化而改变。

现有两端原生文件联测及各自独立 QA 正在进行；本草案不授权更改它们的候选或中断测试。获批后，在修改共同源码前，协调者须确认现有人工联测、相关返工和该候选所需 QA 取证不再依赖被覆盖的文件，并固定候选及证据；若旧任务仍需同文件返工或复验，先协调隔离与衔接。旧任务的最终验收仍由各自 Human Owner 决定，不因本任务提前通过或自动取消。

## 2. 文件命名与用户操作

1. 在现有导出对话框中，所选每台 PLC/实例均显示一个可编辑的**完整文件名**。默认取所选保存来源中的 PLC/实例名称加 `.json`；若名称已以 `.json` 结尾（大小写不敏感）则不重复追加。单选与多选均可逐台修改；界面同时显示对应 PLC/实例名称，避免混淆。默认名本身非法或同批重复时明确提示用户修改，不静默改名、自动编号或覆盖。
2. 完整文件名须以 `.json` 结尾（扩展名大小写不敏感），扩展名前须有非空且非全空格的名称；不得超过 255 个 UTF-8 字节，包括扩展名。只允许单个文件名，不接受目录或绝对路径；拒绝 `/`、`\`、`<`、`>`、`:`、`"`、`|`、`?`、`*`、NUL、ASCII 控制字符及 DEL，拒绝扩展名前的名称以空格或点结尾，以及 Windows 保留设备名 `CON`、`PRN`、`AUX`、`NUL`、`COM1`–`COM9`、`LPT1`–`LPT9`（不区分大小写，包括带扩展名的形式）。普通中文等合法 Unicode 名称可用。具体原因在对应行以中英文提示，服务端独立校验，不能只依赖前端。
3. 同一批选择的文件名按大小写不敏感比较；重复时标出冲突项，用户修改后才能预览提交。文件名与 PLC 本机身份一一绑定，不以显示顺序或名称推断身份。目标目录已有同名项时明确标为冲突并拒绝覆盖，其他有效项仍可按既有逐项结果导出；目录、文件或权限在检查后变化时以实际原子创建结果为准，不覆盖现有文件。目标文件系统还可能识别额外的大小写或 Unicode 名称别名，发生真实冲突时对应项失败并提示，不能以预览成功冒充落盘成功。
4. 沿用两端原生目录选择、当前授权令牌、有效期、原子不覆盖落盘和临时文件清理；前端只传用户填写的单个**文件名**供服务端验证，不能传任意目录或路径。用户修改来源、选择或文件名后，旧内容预览及目录冲突检查失效；可返回修改后重新预览和核对目录。取消或关闭预览不写文件；并发、过期、路径替换或取消不得造成覆盖或冒称成功。保留现有 DS 保存版本及 selected/loaded 差异确认，DAA 保存草稿/active 来源和目标确认。
5. 文件名只决定本次所选目录中的外部文件名，不写入 PLC/DB/点 ID、origin、producer、版本、显示名或其他 JSON 内容，不更改配置或历史。落盘字节和 SHA 须与该次有效内容预览一致；不同次预览的真实导出时间可不同，不要求不同时刻的整文件 SHA 一致。仍为一台 PLC 一个完整 JSON；沿用原格式限制和不可表达内容的拒绝规则。

## 3. 结果反馈

1. 导出提交返回后，两端在导出对话框顶部的不随内容区滚动的位置，或同等无需滚动即可见的位置显示醒目的结果摘要，直到用户关闭或开始新的导出流程。摘要区分全部成功、部分成功、全部失败及存在未知结果，并展示各状态数量；不能把部分成功或未知说成全部成功。
2. 每台显示 PLC/实例名称、实际目标文件名及 `written`、`failed` 或 `unknown` 的用户可读状态；明确失败原因，成功项保留实际文件 SHA，临时文件清理未完成沿用既有提示。若整次 IPC 结果未知而没有逐项回执，只能对未确认的项报告未知，不能猜测成功或失败。未知时提示先检查所选目录和文件，再决定后续操作；不自动重试或重复写入。
3. 新增用户可见文本和错误提示均提供对应中英文；保持现有入口、版本/点位预览及取消行为，不增加命名模板、批量重命名规则、文件自动打开或其他无关功能。

## 4. Development 精确文件范围（待批准）

仅允许修改以下路径；花括号仅展开列出的文件，不是目录通配符。必要时可修改同一列中的既有测试以适配导出 IPC 参数，但不得删除其既有安全断言。若必须修改其他文件或增加依赖，停止并回 PM 修订。

| 范围 | 文件 |
| --- | --- |
| DS 导出服务及桥 | `automation-world/device-simulator/runtime/src/services/catalog_export.rs`；`automation-world/device-simulator/src-tauri/src/commands/catalog_export.rs`；`automation-world/device-simulator/src/services/deviceSimulator.ts` |
| DS 页面及文案 | `automation-world/device-simulator/src/app/simulator/components/CatalogExportDialog.vue`；`automation-world/device-simulator/src/app/simulator/locales/{en-US,zh-CN}.json`；`automation-world/device-simulator/src/styles/app.css` |
| DS 测试及手册 | `automation-world/device-simulator/runtime/tests/{plc_catalog_export.rs,plc_catalog_import.rs}`；`automation-world/device-simulator/tests/plc-catalog-export.test.mjs`；`automation-world/device-simulator/{USER_GUIDE.md,USER_GUIDE.zh-CN.md}` |
| DAA 导出服务及桥 | `automation-world/data-acquisition-agent/src-tauri/src/services/catalog_export.rs`；`automation-world/data-acquisition-agent/src-tauri/src/commands/catalog_export.rs`；`automation-world/data-acquisition-agent/src-tauri/src/commands/local_acquisition.rs`；`automation-world/data-acquisition-agent/src/services/localAcquisition.ts` |
| DAA 页面及文案 | `automation-world/data-acquisition-agent/src/app/plc/components/CatalogExportDialog.vue`；`automation-world/data-acquisition-agent/src/app/plc/locales/{en-US,zh-CN}.json`；`automation-world/data-acquisition-agent/src/styles/app.css` |
| DAA 测试及手册 | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/{catalog_export_tests.rs,catalog_import_tests.rs}`；`automation-world/data-acquisition-agent/tests/plc-catalog-export.test.mjs`；`automation-world/data-acquisition-agent/{USER_GUIDE.md,USER_GUIDE.zh-CN.md}` |
| STD 事实 | 本 `spec.md` 仅 PM / Human Owner；精确批准后 Development 创建本任务 `tasks.md`，handoff 后 fresh-context Verification 创建本任务 `checklist.md`。 |

不新增依赖、修改锁文件、数据结构 DDL、环境配置、JSON schema、导入器、PLC 协议或其他应用。关联 PLAN / catalog 的机械同步由主协调者按其权限处理，不由本 PM 修改。

## 5. 验收标准

| 编号 | 通过条件 |
| --- | --- |
| E01 | DS 和 DAA 各在现有导出流程中按所选保存来源列出每台的默认文件名；单台及多台可逐项修改，默认名不重复添加 `.json`，实际落盘使用所确认文件名。中文和英文界面均可理解。 |
| E02 | 合法中文名称可用；空名、缺扩展名、超长、路径分隔/穿越、控制字符、非法字符、尾随空格/点和保留设备名均由服务端拒绝且对应提示；同批大小写重复逐项提示，修改后可继续。绕过前端的请求不能写出选择目录之外。 |
| E03 | 预览后改文件名、改选择或取消使旧确认失效；目标已存在、预览后被创建、目录身份变更、并发与取消均不覆盖原文件或留下未报告的半文件。同批一项目标已存在或内容无效时，其他有效项可按既有流程导出并分别报告；批内重名须先按 §2.3 修改。 |
| E04 | 单项成功和多项全部成功时顶部醒目显示成功；部分失败、全部失败及结果未知均明确区分，列出每台实际文件名和状态；无回执时不猜测、不自动重试。界面滚动较长点表后仍易于看到摘要。 |
| E05 | 同一次有效预览的写出文件 SHA 与预览一致；对照相同保存来源的文件内容，外部 origin、PLC/DB/点 ID、技术字段、双语、description、来源版本及启停语义不因文件名改变。不同次 `exported_at` 可不同。两端现有完整导出、导入与新旧身份映射回归保持。 |
| E06 | 在 macOS 原生两端各以一台已保存 PLC/实例实际修改文件名、导出并观察醒目成功反馈，检查中英文文案；多台命名、部分结果、未知回执和竞争用有针对性的自动化/替身验证，不强制用户手工创建多台或重复联测。可使用已授权的各自 `.local/dev` 中已保存来源或明确的自有测试对象，也可使用应用目录内自有临时合成 profile；均须先核对实际 profile、进程和自动运行状态。按真实测试层级记录，运行与改动相称的 Rust、Node、类型及构建检查。 |
| E07 | 双语手册更新原 UUID 固定命名说法，说明自定义、冲突、部分结果与未知检查。测试只使用本任务确认的输出目录，保护既有实例、配置、来源、版本与历史；不为测试在用户 `.local/dev` 中另建配置版本或触发历史裁剪。临时资源只在确认任务归属、无运行或证据依赖后按 workflow 清理。 |

## 6. 风险、排除项和 handoff

- 仅指定跨平台保守文件名校验；现有导出落盘的非 Unix 平台实现和 Windows 原生验证不在本任务内，不因名称合法而宣称 Windows 已支持。目标目录的真实文件系统规则或并发变化仍可能导致单项失败。
- 用户已授权使用两端各自 `.local/dev` 和应用目录内自有临时 profile；若已保存来源不能安全满足单台验证，则使用自有临时合成 profile，不为方便验证改动用户旧配置。`.local/dev` 中已有来源只读导出，不能冒称合成；临时文件不进入仓库。仅可清理明确属于本任务的测试对象，已被历史引用的记录保留。不连接真实 PLC、不采集、不真实 POST，不修改或删除用户既有实例、配置、来源、版本、样本、队列与回执；不因测试在用户 profile 中保存配置版本或激活。FF、CA、VM、部署、发布和生产采用不在范围。
- Development 按触达面使用 `aiis`、`rust-runtime`、`desktop-tauri`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer`；Verification 使用 fresh context 独立核对实际候选、文件范围、测试及证据，Human Owner 最终验收单独决定。角色是 contract_only，不宣称平台 ACL 或自动强制路由。
- 未获 Human Owner 对 **`aiis-ics-arch::ARCH-PLC-002 r1`** 的精确范围批准前，不实施或标记通过。本草案不承诺旧任务 QA 结果，不授予真实设备、上报、数据库迁移、部署或发布授权。
~~~~
