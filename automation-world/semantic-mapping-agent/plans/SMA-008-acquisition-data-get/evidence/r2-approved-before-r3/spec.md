Task ID: SMA-008
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 SMA-008 r2；交 Development 按本规格实施，交接后由 fresh-context Verification 独立验证
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch.aw.sma
Classification: child_inherited
Capability: SMA HTTP映射桌面应用的分阶段交付
Owner: AIIS Automation World / SMA 模块 Human Owner
Acceptance Chain Reference: SMA-001 总交付链：各任务精确 Task ID / Revision 范围批准 -> Development developer_handoff -> fresh-context Verification -> Human Owner 分阶段及总体最终验收
Scope Slice: 采集来源选点、显式 GET/POST 测试，以及单目标持续映射、失败恢复与重启续跑
Parent Task ID: SMA-001
Same Capability: yes
Same Owner: yes
Same Acceptance Chain: yes
Depends On: SMA-004；aiis-ics-arch::ARCH-ACQ-006 r1 rework-1（源码精确候选及隔离验证已获 Human Owner 验收）
Related Task: SMA-005, SMA-006, SMA-007

# SMA-008 采集数据持续映射与投递

## 1. 目标与当前事实

SMA 连接后端，选择一个 PLC、一个 DB 和其中一个或多个点位，在配置时分别测试 GET 和 POST。用户启动任务后，SMA 按稳定续读位置持续读取采集样本，将所选数据按配置映射为目标请求，确认 GET 成功后 POST 到一个目标业务接口。目标确认成功后才推进进度。暂时失败可恢复，应用重启后可接续未完成样本。每个任务有一个源范围和一个目标，同一应用可配置多个相互隔离的任务；本次先以单任务顺序处理和一个受控目标验收。

SQLite 只承载 SMA 配置。采集值、完整样本和待发送正文在 SMA 的本次运行内存中使用，不写入 SMA SQLite、配置备份、本机持久缓存或日志正文。可恢复进度、待确认投递的身份、固定配置版本标识和请求指纹由后端拥有并持久化；SMA 保留不可变配置版本，后端继续拥有原始采集事实。[ARCH-ACQ-006 r1 rework-1](../../../../plans/ARCH-ACQ-006-acquisition-consumption-delivery/checklist.md) 的精确源码候选及隔离验证已获 Human Owner 验收。SMA 按 [acquisition-consumers/v1 已发布合同](../../../../contracts/published/http-api/acquisition-consumers-v1/README.zh-CN.md)接入；目标环境的接口和数据状态需按实际核实。

用户已在 SMA 保存 `GET /api/v1/acquisition-data/latest` 材料。当前入选只保存 OpenAPI 定义；事实页仍调用旧 `collection-facts`，SMA-004 的配置和纯预览已接受，手动、启动和恢复投递仍被运行时拒绝。SMA-005 为 `qa_blocked`，SMA-006 为草案，SMA-007 独立 QA 通过且待 Owner 决定。本草案以当前工作树和 SMA-004 为基线，重叠文件保留现有候选，各任务状态不因此改变。 [材料选择](../../src/app/twin-facts/store/apiMaterials.ts) · [事实 API](../../src/app/twin-facts/api/index.ts) · [运行拒绝](../../src-tauri/src/services/mapping_runtime/mod.rs) · [SMA-004 验收](../SMA-004-local-configuration/checklist.md#owner-acceptance-r1) · [总规格](../SMA-001-cu-integration-and-scope-cleanup/spec.md)

## 2. 后端合同核对与外部依赖

| 能力 | 当前源码事实 | 本任务所需 |
| --- | --- | --- |
| PLC、DB 与实时选点 | `GET /api/v1/acquisition-data/options` 提供候选，`GET /api/v1/acquisition-data/latest` 按 PLC、DB 读取逐点最新值，可选 `pointId`。各点可以来自不同样本。 | 直接复用作选点与实时 GET 测试。 [v2 路由](../../../../backend/app/plc_facts/api/v2.py) |
| 历史查询 | `GET /api/v1/acquisition-data/history` 接受 `from`、`to`、PLC/DB 和 `page/pageSize`，按采样时间、ID 倒序及 offset 分页，查询时间跨度最多七天，仅返回未过期记录。详情 `history/{id}` 使用列表的 `id` 并返回完整样本。 | 复用历史展示和单条样本核对。当前没有连续消费游标；新提交、DAA 延迟补传会改变页次或落入更早的采样时间，不能保证逐条续读。 [历史查询](../../../../backend/app/plc_facts/crud/async_v2.py) |
| 采集 POST | `POST /api/v1/integration/plc-facts/samples` 支持匹配身份与原始请求内容的去重，提交成功返回 `committed` 和 `created` 或 `duplicate`。相同 ID 与不同正文冲突，接管或样本过期会使重试受限。 | 可以作为受控测试目标。必须保留身份并能恢复完全一致的 UTF-8 正文字节，核对回执中的合同、实例和样本 ID。 [公开合同](../../../../contracts/published/http-api/plc-facts-v2/README.zh-CN.md) · [写入 Service](../../../../backend/app/plc_facts/services/async_v2.py) |
| 稳定续读与投递状态 | 原有 v2 读取接口未提供上述续读合同，旧集成路由已退役。 [退役测试](../../../../backend/tests/test_legacy_acquisition_retirement.py) | [ARCH-ACQ-006 r1 rework-1](../../../../plans/ARCH-ACQ-006-acquisition-consumption-delivery/checklist.md) 已交付并在隔离环境验收本节及 §3.2 所列后端能力。SMA 接入其[公开合同](../../../../contracts/published/http-api/acquisition-consumers-v1/README.zh-CN.md)。单靠 `latest`、历史 offset、采样时间、`sourceSeq` 或未证明提交顺序的自增 ID 均不作为无漏读证明。 |

后端任务需提供基于已提交事实的稳定、有界、可续读顺序。并发事务可能先分配 ID 后提交，简单 `MAX(id)` 不能保证提交顺序；可采用同一事实事务中经过验证的串行提交序列或等价机制。续读合同须定义源范围、首次起点、空结果、下一位置、已过期或无法续读的缺口、来源代次切换与稳定样本身份，并提供与现有事实一致的点位数据。具体路径、字段、存储和迁移由后端独立规格固定，不能在 SMA 中臆造现有接口。

后端另需提供按任务持久化的运行状态和单活动执行者协调，能原子记录或核对待投递身份、源位置、配置版本、目标流序号、正文指纹及确认结果，并只在匹配回执后推进连续位置。映射配置版本及生成规则须可在重启后恢复；仅以引用加指纹为前提的重构方案须证明从保留的源样本得到完全相同的请求字节。若事实过期、配置或生成器版本不可用、重构哈希不符或目标去重条件失效，则标记待人工确认并停止推进。后端存储不复制 SMA 的采集正文作为默认前提；具体合同与原子性由后端任务验收。

上述两个后端能力由已验收的 ARCH-ACQ-006 r1 rework-1 交付。后端实现、数据库迁移和真实环境操作不包含在 SMA-008 写入范围；正式接入按已发布合同及目标环境实际状态验证，不能以隔离后端验证代替 SMA 的持续闭环、无漏读或恢复验收。

## 3. r2 范围与流程

### 3.1 配置、选点和测试

1. **连接和来源。** 继续复用已保存的 Backend 地址和 HTTP 准入，选用已入选的 latest GET 材料，不自动创建目标 API。缺失或删除材料时保留配置并提示处理。显式加载 options，选一个 PLC 和 DB，再加载点位候选；按稳定 `pointId` 单选、多选或明确选择全部。最新候选只表示后端当前可见数据，空结果要如实提示。
2. **GET 测试。** 「测试获取」重新调用当前范围的 GET，展示点位 ID、名称、类型、值、质量、原因和真实 `observedAt`。`0` 和 `false` 保持原值，坏质量及缺失点可见。HTTP 状态、应用状态、响应结构、超时和空结果分别反馈。连接、来源或选点改变后，旧测试结果和基于它的 POST 预览立即失效，迟到响应不能覆盖新选择。
3. **目标与映射。** 用户选择并配置一个 POST 目标、字段映射、常量和必要类型转换，预览实际 URL、方法及请求 JSON。复用既有 OpenAPI 材料、映射配置和 CU 控件，补齐本目标需要的对象和数组映射，包含采集样本 `points[]`。业务接口的请求结构、成功回执及幂等规则依接口合同确定。缺少必填点位、类型错误或质量不满足目标合同须阻断并显示原因，不把失败值当作有效值。
4. **独立测试。** 配置页分别提供「测试获取」和「测试推送」。测试推送必须使用当前配置下最近一次成功且未失效的 GET 数据和预览，用户显式触发才发出；GET 失败、无所需数据或选项变化后不能 POST。独立测试使用受控目标，不推进持续任务位置；HTTP 关闭时零外部请求。测试后显示目标 HTTP 状态、业务回执及失败原因，响应丢失标为结果未知。
5. **采集目标回环。** 若以采集 POST 作为首个目标，先按后端 history 列表中的 `id` GET 单条完整样本详情，以同一次样本生成 `points[]`；配置独立登记的 `external` 测试来源及其 PLC/DB、实例和代次，目标样本 `sampleId` 与递增 `sourceSeq` 有独立稳定身份，目标源排除在本任务消费范围之外，防止回环。`latest` 可以预览点位，不将不同采样时刻的逐点结果冒充一条完整样本。

### 3.2 持续执行与恢复

6. **启动与有界读取。** 用户保存配置，按后端合同选择从启动时开始或从当前仍保留的历史开始，明确展示起点及保留范围，启动前校验后端续读和目标回执/幂等能力。任务按配置的轮询间隔有界获取后端已提交样本，按源顺序逐条处理。空页等待后再 GET；不可恢复缺口或已过期位置显示阻断，不能静默跳到最新位置。启动和停止采用明确状态，多个任务隔离。
7. **GET → 映射 → POST。** 每条样本的 GET 必须 HTTP 和应用成功、结构有效并包含映射必需的数据；重启后重构也须重新 GET 并校验保留的源样本。映射产生目标正文后才发送。先取得后端持久待投递记录，固定源样本、配置版本、目标地址及影响业务语义的参数、目标流、目标唯一身份、序号与正文指纹；后端未确认该状态时不发 POST。日志记录状态与标识，不记录采集值或完整正文。
8. **确认与推进。** 目标回执须通过该目标合同的 HTTP、业务状态和身份核对，后端原子记录确认并推进该任务位置，再取下一条。采集 POST 的 `committed/created` 或 `committed/duplicate` 均须匹配 `contractVersion`、`instanceId`、`sampleId`。未知回执、错误身份和错误业务状态不推进。
9. **失败与重试。** GET 超时或临时不可用以有界退避重试，不 POST。POST 已发出后超时、连接中断、丢回执或 `commit_outcome_unknown` 均视为结果未知；在目标合同支持原身份幂等、登记和有效期仍满足时，验证重构正文指纹后使用原身份与原字节重发。`409` 身份/内容冲突、`403` 来源不匹配、`410` 过期、无法重构、重试条件失效或目标不支持安全重试时停止自动投递并显示原因，保留待确认状态。后台重试有界退避，避免紧循环；人工确认或重置必须明确作用范围，不伪造成功或越过缺口。
10. **停止和重启。** 同一任务仅一个有效执行者。竞争或执行者失联时，后端以经验证的租约和代次校验使过期执行者无法再分配新投递或推进进度；接管前先处理未确认投递。若过期执行者的在途请求与接管重发重叠，二者使用相同投递身份，由目标幂等合同防止重复写入。用户手动停止的任务在重启后保持停止；此前运行中的任务在 HTTP 准入、配置版本、后端和目标合同仍满足时恢复。SMA 应用关闭期间不投递，重启后从后端已确认位置和待确认身份继续。编辑中的新配置不改变在途请求的固定版本，保存冲突保留草稿并提示处理。
11. **运行界面。** 现有「映射执行」提供启动、停止、恢复及状态，区分运行中、等待数据、退避重试、停止、阻断和结果未知。展示当前源/目标、进度位置、最近一次成功、失败原因及待确认标识；时刻标明真实语义。配置页和执行页的反馈、表格列宽、键盘使用、中英文与明暗主题沿用项目及 CU 规范。

### 3.3 安全保证与范围边界

对具备本规格所需续读、保留、原文幂等和回执合同的源与目标，在相应保留期内，单目标按确认顺序处理；相同投递在丢回执恢复时可以得到重复确认而不产生第二条采集目标记录。对任意业务 POST、不支持去重或查询的目标、已过期的来源和目标，不能承诺自动恢复或目标恰好一次，必须明确阻断与人工对账。

本草案不定义高吞吐性能目标、并发批量优化、多目标事务、跨主机高可用、任意目标通用去重、生产部署、真实 PLC 操作或真实数据迁移。以上可在明确需求后另定范围。停止任务不删除源事实、目标记录或历史配置。

## 4. 复用、配置兼容与实现边界

- DTB TSS 的事实表格、筛选与 HTTP 处理已部分移植到 SMA，可复用组件和局部逻辑。旧 `snapshot_facts` 调用旧 POST 快照合同，不能据此宣称已支持新续读。架构仓采集数据 Web 已有 options/latest 与范围选择，借鉴其语义时须接入 SMA 的桌面连接和 CU，不整套覆盖。 [SMA 事实表](../../src/app/twin-facts/components/FactsTablePanel.vue) · [采集 Web API](../../../../frontend-js/src/app/acquisition-data/api/index.js) · [CU 出口](../../../console-ui/src/ui/index.ts)
- 保留 SMA-004 配置备份、原子写入、版本冲突处理和纯预览。当前 `ConfigurationDocument` 对未知字段严格校验，新增来源/目标/执行设置必须兼容已有 v1 文档和备份，打开旧数据不自动增加 revision 或清空配置。记录新配置对旧程序的可读性和回退方式，不以删除用户配置解决兼容问题。 [本地配置合同](../../src-tauri/src/contracts/local_configuration.rs)
- 用户显式保存的连接、选点、目标和映射等配置进入 SMA SQLite。源样本值、`quality`、`observedAt`、响应和请求正文、待发送副本、游标与回执不进入 SMA 本地数据库、备份、持久缓存或日志正文。后端的样本事实和运行状态按其另立合同管理，界面临时显示不产生本机持久化。
- HTTP 准入继续遵循现有配置，草案本身不改变运行门禁。用户精确批准本 revision 并实施后，Development 和 Verification 可在隔离 profile、受控目标和依赖就绪的环境中启用 GET/POST 与持续运行以完成验收。真实 profile、现场和生产环境的启用依项目规则和 Human Owner 对具体环境与操作的决定，不由独立 QA 自动授权。

批准后可能触达的 SMA 交付面限于完成本规格所必需的文件：`src/app/connection/`、`src/app/twin-facts/` 的连接、材料、来源、目标、映射、执行 UI/API/store/locale；`src-tauri/src/contracts/`、`commands/`、`services/`、`domain/`、`infrastructure/config_store/` 与 `main.rs` 中相应配置和运行入口；为实现本规格所需 SHA-256 和 UUID 合同而必要调整的 `src-tauri/Cargo.toml` 及 `src-tauri/Cargo.lock`；配套 `tests/`、`src-tauri/tests/`；必要的 SMA `README.md`、`README.zh-CN.md` 和仓库 `CODE_INDEX.md`。新增文件须属于上述功能路径。后端、DAA、DTB、CU 源码、真实环境和数据库迁移均由各自独立范围处理。

Development 和 Verification 在实现期按 `frontend-ui`、`desktop-tauri`、`rust-runtime`、`i18n-workflow` 与 `code-document-indexer` 处理适用部分。后端依赖任务负责 `backend-arch` 和迁移合同。日志及持续运行应遵守项目时间与运行日志约定，敏感值不进入日志正文。

## 5. 验收标准

| ID | 操作与通过标准 |
| --- | --- |
| AC01 | 隔离 profile 中使用已入选 latest 材料配置 PLC/DB、单点、多点及全部点位。测试 GET 每次实际取数并如实显示 `0`、`false`、坏质量、原因与 `observedAt`。切换选项、迟到请求、HTTP 关闭、超时、错误结构和空数据均有正确反馈；失效测试不可触发 POST。 |
| AC02 | 目标 API 的必填字段、常量、数据类型和 `points[]` 可配置并预览；显式测试 POST 使用当前成功 GET 的数据并显示真实回执，目标未请求或返回失败/未知时如实展示。测试动作不推进持续任务位置。 |
| AC03 | 隔离后端续读合同下，连续提交三条以上源样本，持续任务顺序处理并在目标确认后逐一推进；空页继续等待。覆盖同一采样时间、DAA 延迟上传旧采样时间、并发事务分配 ID 后乱序提交和分页边界，提交的有效样本均按合同被看到，不因倒序或 offset 漏读。 |
| AC04 | 目标在首次提交成功后丢失响应，SMA 保留待确认状态并以完全一致的身份和正文重发，接收匹配的 `duplicate`；采集测试来源回读恰有一条目标历史记录。错误 `sampleId`、`instanceId`、合同版本、HTTP 或业务回执均不能推进。 |
| AC05 | 在发送前、目标提交后确认前、进度提交前及重试等待中终止并重启应用，依据后端状态接续；两个执行者竞争同一任务时最多一个有效执行者推进；原执行者在租约失效后恢复，不能推进或分配新投递，其在途请求与接管重发重叠时目标仍只有一条记录。手动停止的任务重启后保持停止，此前运行任务满足准入条件时恢复。 |
| AC06 | 依次覆盖 `409`、`403`、`410`、源保留过期或缺口、目标不支持幂等、配置版本或生成器不可恢复、正文指纹不匹配与后端状态不可用；界面显示原因，位置不越过未确认项，也不以新身份盲目补发。 |
| AC07 | 原 v1 SQLite 配置与备份隔离读取、导出、导入、重开及并发编辑冲突保留原内容；测试与持续运行前后检查 SMA SQLite、备份、本机持久缓存和日志正文，没有采集值、响应/请求正文、游标或回执。SMA 保留的固定配置版本与后端待确认元数据可支撑重启后的确定性重构。 |
| AC08 | 在 `1280×800`、`1024×720` 验证中英文、明暗主题、键盘使用、运行状态和错误反馈。隔离环境中完成 GET、手动 POST、连续投递、目标回读、停止和恢复；界面表格按项目规范支持列宽调整和恢复。 |

后端续读及状态合同须先在其独立任务中验证事务并发、保留和丢回执。SMA Development 记录定向测试、`pnpm check`、`pnpm test`、`pnpm build`、适用 Rust 测试、差异及文档链接检查；fresh-context Verification 独立复核。实际 DAA 和真实业务环境能否采用、真实现场运行及容量仍由其具体证据决定。Human Owner 自己操作真实 GET/POST 的意愿与环境范围在实际测试时明确。

## 6. 风险、依赖与交接

- 可续读和投递状态已在后端精确源码候选及隔离验证范围验收。SMA 接入时仍需验证目标环境中的提交顺序、过期缺口和状态原子性，方能声明其完整消费及重启恢复通过。
- 后端 `samples` 重试受登记身份、原始请求字节和有效期约束。固定身份及原字节的恢复、目标序号分配和来源样本保留期均须通过端到端受控测试。
- 单次与持续任务使用的 GET 成功条件、目标成功规则和点位缺失策略必须在 UI 与合同中一致。映射变更与在途重试使用固定版本，避免同一身份发送不同内容。
- 实际目标可能并非采集 POST，只有其自身提供可核对的成功、幂等或查询合同才能自动处理未知结果。测试目标隔离及源范围过滤须防止自己读取自己写回的样本。
- 配置文件、数据库表结构与实际运行入口须在 Development 交接中明确；本规格不提供独立后端任务批准、真实数据写入、迁移、部署或现场设备操作授权。

## 7. 修订与批准历史

| 日期（Asia/Shanghai） | Revision | 实际状态 |
| --- | --- | --- |
| 2026-11-19 | r1 | 草案仅含 PLC/DB/点位选择及显式 GET，SQLite 只存配置，POST 和自动运行关闭；未获范围批准、未进入 Development 或 Verification。 |
| 2026-11-19 | r2 | Human Owner 要求先核对 history 游标和采集 POST 安全重试，再起草持续运行、失败重试、重启恢复的完整流程，SQLite 仍只存配置，暂不改代码。当前为 PM 草案，后端依赖 ARCH-ACQ-006 r1 另行等待批准、实施和验收；尚无 r2 批准、实现、独立验证或最终验收。 |
| 2026-11-20 | r2 | Human Owner 明确表示「批准 SMA-008 r2」。ARCH-ACQ-006 r1 rework-1 的精确源码候选及隔离验证此前已获验收。本次批准前 spec 的 SHA-256 为 `d4cd11390a88df8eb887b2bfe3bb63782eb3933d57ff78acb268bcb7ddd428b6`。批准覆盖本规格范围，交 Development 实施，再交 fresh-context Verification；本条不代表 SMA 已实现或最终验收。 |
| 2026-11-20 | r2 | PM 机械澄清实现交付面可对 `src-tauri/Cargo.toml` 与 `Cargo.lock` 作本规格 SHA-256 和 UUID 合同必需的依赖声明调整。现有锁文件已包含 `sha2` 与 `uuid`，具体依赖特性及锁文件变动由 Development 记录。功能范围、验收标准和批准 Revision 不变。 |

Human Owner 随后表示「不用隔离吧，直接用dev的接口就行」。开发联调可使用现有 dev HTTP 接口，按实际合同、来源和目标状态核验，并保护已有配置及非测试数据；本表述本身不授权数据库迁移或服务重启。原有隔离 profile、隔离场景及验收条目保留，dev 联调结果与其各自能覆盖的验收项如实记录。
