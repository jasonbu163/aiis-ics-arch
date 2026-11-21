Task ID: SMA-008
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 SMA-008 r3；交 Development 按本规格实施，交接后由 fresh-context Verification 独立验证
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch.aw.sma
Classification: child_inherited
Capability: SMA HTTP映射桌面应用的分阶段交付
Owner: AIIS Automation World / SMA 模块 Human Owner
Acceptance Chain Reference: SMA-001 总交付链：各任务精确 Task ID / Revision 范围批准 -> Development developer_handoff -> fresh-context Verification -> Human Owner 分阶段及总体最终验收
Scope Slice: 使用现有采集 API 的选点、手动 GET、映射预览、单次 POST 和回读
Parent Task ID: SMA-001
Same Capability: yes
Same Owner: yes
Same Acceptance Chain: yes
Depends On: SMA-004；目标环境提供现有 plc-facts/v2 采集 GET 和样本 POST
Related Task: SMA-005, SMA-006, SMA-007, aiis-ics-arch::ARCH-ACQ-006 r1

# SMA-008 现有采集 API 手动映射回环

## 1. 目标和背景

在 SMA 选择后端已有 PLC、DB 和点位，手动测试 GET 并显示数据。将选定的同一次采集样本按映射生成一个目标 JSON，在页面预览；由用户显式触发一次 POST，展示真实回执，再用现有 GET 查询结果。这个阶段连接用户现有的 dev 采集接口，使用该接口当前的免 Bearer 开发合同。用户可按界面提示自己完成回环测试。

SMA 的 SQLite 仅保存配置，包括后端连接、选点、目标与映射。GET 返回值、预览正文、POST 正文、回执和每次提交身份仅保留在当前会话内，不写入 SQLite、配置备份、本地持久缓存或日志正文。后端继续保存采集历史和最新值。

Human Owner 已批准 [SMA-008 r2](evidence/r2-approved-before-r3/spec.md)，随后澄清「用这一套就行，带token的后续再说，先不管」，并批准本 r3 现有开发接口手动闭环范围。r2 的连续投递与重启恢复设计保留为后续目标，不由 r3 手动测试证明。r2 批准后 Development 已开始部分 Rust 工作，尚无 Development handoff 或独立 QA；暂停前一次 cargo check 退出 101，出现两处 E0308。现有未完成工作须逐项评估、复用或按需要调整，不将其视为已交付。

## 2. 已有接口和工作边界

| 接口 | 本阶段用途 |
| --- | --- |
| `GET /api/v1/acquisition-data/options` | 加载当前可选 PLC 和 DB。 |
| `GET /api/v1/acquisition-data/latest` | 按 PLC/DB 读取最新点位并展示，也可用于回读目标最新值。各点可能来自不同样本。 |
| `GET /api/v1/acquisition-data/history` | 按 PLC、DB、时间范围与分页查找历史摘要。 |
| `GET /api/v1/acquisition-data/history/{id}` | 按历史摘要的 `id` 读取同一次采集的完整点集。 |
| `POST /api/v1/integration/plc-facts/samples` | 用户确认后发送一个目标 PLC/DB 的采集样本，读取 `committed` 回执。 |

接口以现有 [plc-facts/v2 开发合同](../../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md)为准。后端目前对上述开发接口免 Bearer，SMA 本阶段不要求用户配置 token。来源类型不影响 SMA 选择 PLC、DB 和点位。界面可展示后端返回的来源类型，不能根据点名猜测来源。

本阶段继续沿用现有 `SMA_HTTP_ENABLED` 外部 HTTP 准入与已保存的后端连接。目标环境现成接口的可达性和实际响应须核对。开发、测试或本草案都不授权数据库迁移、服务重启、修改后端接口或后端配置。已有 [ARCH-ACQ-006 r1 验收](../../../../plans/ARCH-ACQ-006-acquisition-consumption-delivery/checklist.md)及其源码历史保留，本阶段不调用 acquisition-consumers 接口、不要求其 token，也不把它作为单次回环的前提。

## 3. 使用流程

1. **选择来源和测试获取。** 在现有 SMA 来源页通过 options 选择一个 PLC、一个 DB，加载当前点位并单选、多选或明确选择全部。点「测试获取」实际调用 latest，展示点位 ID、名称、类型、原值、质量、原因和真实采集时间。`0`、`false` 必须原样展示。options 或 latest 无数据时显示空状态。
2. **选取同次样本。** 历史查询按原采集时间及现有 API 限制填写时间范围，选中列表项后以 `history/{id}` 获取完整样本。目标 POST 的 `points[]` 从同一次样本中选出的点位生成。latest 中不同 `sampleId` 的点不合并成同一历史样本；界面提示选择具体历史样本。当 latest 的已选点确属同一条样本时，也须依据实际历史详情核对后生成完整请求。
3. **配置目标与映射。** 用户配置当前后端上已登记的测试目标 PLC、DB、实例和来源代次，并选择目标字段与点位之间的映射、必要常量和类型。测试目标可使用不同的 external PLC，也可使用同一已登记 external PLC 下明确专用于测试的不同 DB；源和目标不得为完全相同的 PLC/DB。保留选定点的值、类型、质量及原采集时间。必要时支持目标点名、标识和常量映射，`points[]` 为本次目标配置的完整所选点集。
4. **预览和单次推送。** GET 成功、所需点齐全且目标字段有效后，预览实际 POST URL 和 JSON，包括待投递 `sampleId`、`sourceSeq`。用户明确点击「测试推送」后发送一次 POST。没有有效 GET、选择或配置已变、字段缺失、类型不符、质量不满足目标合同，均停止发送并显示原因。独立 GET 测试不触发 POST。
5. **显示和回读。** 根据目标合同核对 HTTP 和业务响应。`committed/created`、`committed/duplicate` 还须匹配合同版本、目标实例和本次样本 ID。显示成功、失败或结果未知。提供目标 PLC/DB 历史或最新值的只读查询，让用户核对样本 ID、点值及质量。历史时间范围按原采集时间填写。
6. **结果未知。** POST 超时、连接中断、`commit_outcome_unknown` 或丢回执时显示「结果未知」。当前会话仍持有完全相同的 UTF-8 请求字节和身份时，用户可显式重试同一请求并查看 duplicate 回执。关闭应用后不持久化正文或待投递状态；需要由用户按目标历史、样本 ID 和时间核对，再决定后续操作，不能自动换身份重发。

## 4. 身份、配置与复用

- 一个目标样本使用唯一 `sampleId`，由客户端基于 UUID 生成并在预览中展示。目标 `sourceSeq` 由用户为所选目标实例、PLC、DB 和来源代次明确填写一个未使用的十进制正整数字符串，范围为 `1`–`9223372036854775806`，不带前导零。现有 latest/history 无法保证推断安全的下一序号，页面不自动声称已找到下一个可用值。若要更新目标最新值，序号还须大于该目标流先前对应点的序号；否则可通过历史回读。身份和正文一旦用于本次预览即固定；服务端返回 `409` 时展示冲突，不悄悄换号重发。
- 用户先前的开发后端手工测试使用已登记 external 来源 `PLC-BE012-DEV-441247C3`，从 DB 21 读取并写入测试 DB 61421。此记录是人工 API 回环证据；正式 SMA 测试仍需由用户在当前页面选择并确认目标及可用序号。
- 选点及当前采集值可复用现有 Web acquisition-data 页的接口语义，以及 SMA 从 DTB TSS 移植的事实表格、映射和 HTTP 基础。页面与弹窗沿用 SMA 已接入的 CU 组件，按 DAA 的间距、反馈和交互模式组织。
- 连接、来源选择、目标 API 和映射配置继续复用 SMA-004 的本地配置、版本冲突保护和备份。新增配置兼容已有 v1 SQLite 文档及备份，不因打开旧配置清空数据或自动增加 revision。用户可保存 PLC、DB、目标与映射；每次提交的真实采集值、样本正文、回执和执行进度不保存到 SMA 本地持久化位置。
- 目标接口只覆盖本节的现有采集样本 POST；其他业务目标的字段、鉴权和回执在后续明确需求时处理。历史列表按 API 的查询范围与分页规则工作，不作为可靠续读游标。

## 5. 实现范围与不包含事项

实施表面限于 SMA 现有连接、材料、事实表、目标配置、映射、单次测试和结果展示的前端、Rust 配置及服务入口；相应测试和双语文案；必要的 SMA README 与仓库 CODE_INDEX。为本规格必需的既有 Rust 依赖声明和 Cargo.lock 调整可包括在交付中，具体由 Development 说明。保留其他既有页面和配置。

r3 实现不要求连续轮询、后台任务、投递队列、自动重试、持久游标、重启自动续投或对每条采集样本的无漏投承诺。用户已表达最终需要持续可靠投递，后续须另行确定适用的接口合同和验收范围。本阶段不更改采集后端、数据库结构、来源登记、CU 源码或其他业务接口，不自动修改用户现有 profile 或历史。用户确认的测试 POST 会在 dev 后端写入目标测试样本。

Development 和 Verification 根据具体改动遵循 `frontend-ui`、`desktop-tauri`、`rust-runtime`、`i18n-workflow` 和 `code-document-indexer`。界面和弹窗考虑中英文、明暗主题、键盘操作及业务表格列宽规则。

## 6. 验收标准

| ID | 通过标准 |
| --- | --- |
| AC01 | 使用现有 dev 后端选择 PLC、DB 和单点、多点、全部点位。显式 GET 显示后端返回的 `0`、`false`、类型、质量和采集时间；空值、无数据、HTTP/业务错误及超时如实反馈，GET 不发送 POST。 |
| AC02 | history 列表和 `history/{id}` 可取得单次完整样本。latest 混合不同样本 ID 时不合并为一条目标样本，用户可转到历史详情选定同次样本。 |
| AC03 | 配置目标和映射后可预览实际 URL、目标身份、sampleId、用户填写的 sourceSeq 及目标 JSON。允许同一 external PLC 的不同测试 DB，拒绝源目标相同 PLC/DB；字段缺失或配置变化使旧预览失效。 |
| AC04 | 用户显式推送后请求当前普通 samples POST，采用免 Bearer 的现有开发合同。HTTP 200 与业务回执、实例和 sampleId 匹配时显示结果；通过现有 GET 回读目标历史，点位值、类型、质量和采集时间一致。 |
| AC05 | 响应丢失时显示结果未知；同会话用户触发重试发送相同身份和完全相同字节，目标已提交时返回 duplicate 且目标历史只有一条。身份冲突和失效来源显示错误，不以新身份自动重发。重启后的情况提示用户人工对账。 |
| AC06 | 用户填写的 sourceSeq 原样使用，正整数与范围校验通过；已占用序号冲突不被当作成功。无有效 GET、空点集、坏类型、HTTP 禁用和已更改配置均不能 POST。 |
| AC07 | 旧 SQLite 配置及备份可读取、导入、导出和重开，既有设置保留。GET、预览和 POST 前后检查 SQLite、备份与日志，均无采集值、请求正文或回执。 |
| AC08 | 页面与弹窗在 `1280×800` 和 `1024×720` 检查中英文、明暗主题、键盘操作、错误反馈与列宽调整；提供可跟随的 dev GET、单次 POST 与回读步骤。记录实际操作人员和测试来源、目标范围。 |

Development 记录必要的前端检查、构建、Rust 检查、定向测试和文档链接检查。独立 Verification 核对同一候选和真实测试结果；API 回环成功不能替代持续投递及恢复的未来验收。

## 7. 历史与批准

| 日期（Asia/Shanghai） | Revision | 实际记录 |
| --- | --- | --- |
| 2026-11-19 | r1 | 草案覆盖 PLC/DB/点位选择与手动 GET。 |
| 2026-11-20 | r2 | Human Owner 明确批准持续投递和恢复范围。完整获批规格原样保存在 [r2 快照](evidence/r2-approved-before-r3/spec.md)，SHA-256 为 `07c424a35d5f52abc9cadc5775b99871a6cf96e4bbe8b452ae485709389f61f4`；快照内部相对链接以本任务目录为原始基准。后端 ARCH-ACQ-006 r1 rework-1 的精确候选和隔离验证已获验收。 |
| 2026-11-20 | r3 | Human Owner 澄清先用现有采集接口，不挂 token。PM 据此提出手动回环草案；当时未取得 r3 批准。 |
| 2026-11-20 | r3 | Human Owner 明确表示「批准 SMA-008 r3」。批准前规格 SHA-256 为 `4971f0a5f0b455a0786f3c97756ce579e36ac180587463f76e1446e685f2262f`。交 Development 按本规格实施，交接后由 fresh-context Verification 独立验证；批准不代表完成实施、验证或最终验收。 |

Human Owner 另表示「不用隔离吧，直接用dev的接口就行」。本规格按现有 dev HTTP 接口组织联调，是否写入由用户在测试操作时明确执行。r2 原审批及已开始但未交接的开发事实保留；对应实现写入此前在 r3 获批前暂停。
