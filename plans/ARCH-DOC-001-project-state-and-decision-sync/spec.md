Task ID: ARCH-DOC-001
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner已于2026-11-05批准精确ARCH-DOC-001 r1；PM -> 命名Development按42路径及既定范围实施文档同步，完成后交新的fresh-context Verification，Owner文档终验pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_governance
Capability: 项目总体文档的当前状态、配置权威、运行链路和方案替代关系同步
Owner: AIIS ICS Architecture 项目级文档
Acceptance Chain Reference: 本 spec 第8节；PM -> Human Owner精确r1批准 -> Development文档交接 -> fresh-context Verification -> Human Owner文档最终验收
Related Task: ARCH-MULTI-001, ARCH-MULTI-002, ARCH-AW-007, ARCH-AW-008, ARCH-BE-009, ARCH-BE-010, aiis-ics-arch.aw.sma::SMA-002, aiis-ics-arch.aw.sma::SMA-003, aiis-ics-arch.aw.sma::SMA-004, FF-004, FF-005
Created: 2026-11-05 Asia/Shanghai

# 项目现状与设计决策文档同步

## 1. 目标、授权与效力

Human Owner在完整只读审计后要求：

> 好的，先同步一下。

本句授权准备本轮总体文档同步。当前只形成这份精确r1草案；Human Owner尚未审阅本Task ID、42条路径和完整验收标准，不倒填为已批准，也不推断DIRECT或BACKFILL。PM只写本spec；主协调可据本草案在根PLAN及根任务目录登记draft。当前不创建tasks/checklist，不修改其余正式文档。

本任务把已存在的实现、QA、Owner决定及明确取舍同步到总体入口，解决“当前”描述与所属事实源不一致。它不重新设计三界、补做产品、不重算旧产品raw、不改变旧任务状态或验收，也不授予真实采用、发布或部署。正式交付工作树为`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，PM起点HEAD为`0465f45ced6a2c8f8ca271b8bbf71f9eabc99de9`；写入前git status为空。

本任务无Parent，不继承任何关联任务的批准、QA或最终接受。现有README、PLAN、ROADMAP与中文长期设计正文的归属不变；不新建第二份总路线、状态报告或合同中心。

## 2. 已核事实与权威入口

以下为2026-11-05起草时的文档/源码读取依据，不是本PM重新执行软件QA。Development开始时重核最新有效段及当前源码；日期明确的旧快照继续作为历史，不以历史中的pending覆盖后来真实决定。

| 事实组 | 当前应表达的边界 | 唯一来源/核对入口 |
| --- | --- | --- |
| 三应用与取消方案 | DAA、SMA、CA独立；FOA命名及SMA/CA合并宿主已被r2替代；共享Flow Core/画布/中央管理不作为近期前置，未明确取消的未来能力仍保持其原状态。 | [ARCH-AW-007 r2 spec](../ARCH-AW-007-general-agent-fleet-roadmap/spec.md)、[Owner/QA记录](../ARCH-AW-007-general-agent-fleet-roadmap/checklist.md) |
| DAA | DAA-001至007已接受；阶段B只在10月30日受控DS联调范围完成。唯一SQLite入口、全样本本地保存及历史限制保持；当前没有可靠上传/ACK。后端优先、DAA暂缓是实施顺序，不是漏项。 | [DAA PLAN](../../automation-world/data-acquisition-agent/PLAN.zh-CN.md)、[DAA-007 Owner决定](../../automation-world/data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2)、[uploadAvailable=false](../../automation-world/data-acquisition-agent/src-tauri/src/commands/local_acquisition.rs)、[BE010 r2顺序](../ARCH-BE-010-anonymous-business-integration/spec.md) |
| CU | CU-001至008已接受；分组/二级导航已存在，DAA与SMA的接入各归其自身任务，不再表述为只有平铺。 | [CU PLAN](../../automation-world/console-ui/PLAN.zh-CN.md)、[CU-008记录](../../automation-world/console-ui/plans/CU-008-grouped-sidebar-navigation/checklist.md) |
| SMA | SMA-002职责清理、003 CU接入已接受；004本地配置/纯预览QA2通过、Owner终验pending；父SMA-001仍draft。业务配置为Rust管理的单SQLite完整快照/revision，UI偏好与技术启动偏好独立。正常manual/start/resume/auto-start拒绝，旧HTTP算法仅兼容fixture，不fallback。 | [SMA PLAN](../../automation-world/semantic-mapping-agent/PLAN.zh-CN.md)、[SMA-004取舍](../../automation-world/semantic-mapping-agent/plans/SMA-004-local-configuration/spec.md)、[QA2](../../automation-world/semantic-mapping-agent/plans/SMA-004-local-configuration/checklist.md)、[正常执行准入](../../automation-world/semantic-mapping-agent/src-tauri/src/services/local_configuration/mod.rs) |
| 事实provider | BE009 r1 A及获批隔离MySQL B已独立通过、Owner终验及provider-ready待定。独立plc_facts七表/三路与旧monitor/Projection兼容链分开；默认关闭、空scope/unadopted及显式采用门槛保持。 | [BE009 spec](../ARCH-BE-009-backend-facts-integration/spec.md)、[最新B verdict](../ARCH-BE-009-backend-facts-integration/checklist.md)、[provider](../../contracts/published/http-api/plc-facts-v1/README.zh-CN.md)、[源码owner](../../backend/app/plc_facts/README.zh-CN.md) |
| 业务provider | BE010 r2八类typed业务接线、可靠回执及隔离MySQL B已独立通过，Owner终验/真实采用待定。四新表、有限13张旧表41时间列T1兼容及旧wire保留由原规格解释；真实历史未迁移，不能把隔离合成采用外推为生产整改。 | [BE010 spec](../ARCH-BE-010-anonymous-business-integration/spec.md)、[最新B verdict](../ARCH-BE-010-anonymous-business-integration/checklist.md)、[provider](../../contracts/published/http-api/business-integration-v1/README.zh-CN.md) |
| 共同需求 | AW008 r1文档QA2通过、Owner文档终验pending；demand仍proposed。需求状态与后续provider实现/验证是不同事实，不据proposed声称不存在provider，也不擅自提升demand状态。 | [AW008 checklist](../ARCH-AW-008-stage-c-facts-contract/checklist.md)、[共同需求](../../contracts/demands/automation-world-facts-integration.zh-CN.md) |
| DS | 10月27日DS-001/005 r5接受保留；10月29日DIRECT草稿/版本管理增量是DEV自检交付，手工确认边界保持。普通保存草稿不隐式发布版本，发布、停机加载、启动分开。DS历史UTC字段不因UI上海显示而完成迁移。 | [DS README](../../automation-world/device-simulator/README.zh-CN.md)、[DS-001 Owner决定](../../automation-world/device-simulator/plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001)、[版本服务](../../automation-world/device-simulator/runtime/src/services/versions.rs) |
| FF | FF-005 r1 A已接受；FF-004 r2 A QA3通过、Owner终验pending，Rust每PLC JSON/YAML v2/多PLC S7 int16为有限交付。Modbus只有结构校验，运行拒绝；DS导出、Python/C#加载未交付。FF-001/002 QA通过待终验，FF-003草案未实施；原完整hold_ack强收限制与旧UTC producer/schema保留。 | [FF PLAN](../../field-flow/PLAN.zh-CN.md)、[FF-004 QA3](../../field-flow/plans/FF-004-plc-json-catalog-and-multi-plc/checklist.md)、[FF-005 Owner/限制](../../field-flow/plans/FF-005-basic-and-advanced-examples/checklist.md) |
| 其他状态纠偏 | FE001 r3第二轮QA通过，不能继续写draft/handoff待QA；BE008 C# Plan QA2通过、Owner终验pending；ARCH001已接受，backend计划的“下一步QA”是旧时点。 | [FE001 checklist](../ARCH-FE-001-frontend-module-auto-assembly/checklist.md)、[BE008 checklist](../ARCH-BE-008-csharp-backend-plan-slice/checklist.md)、[ARCH001 checklist](../ARCH-001-public-architecture-baseline-extraction/checklist.md) |

## 3. 编号需求及同步问题映射

| 编号 | 必须完成的文档处理 | 主要落点 |
| --- | --- | --- |
| R01 证据层级 | 对仍承担当前入口的每个状态/能力，区分源码存在、DEV自检、独立QA、Owner终验、真实采用/现场/长稳；来源不足时保留unknown/待核。不得因本次同步重写旧bundle、补造接受、重新授予产品权限或把任务数量换算完成率。 | 根/模块PLAN、README、provider说明及长期设计的现状表 |
| R02 根总览与图 | 用注明日期和来源的当前状态更新根ROADMAP现状表/图/链路；DAA本地已接受、新后端隔离B通过、SMA配置阶段及正常投递关闭、FF实际源码和C#学习切片分别表达。冻结CA→旧raw/latest→Projection仍作为兼容参考，新链未接通的箭头保持目标/待接线。S0–S4能力阶段及各自gate保留，不把局部成果写成整阶段完成。 | 根README/PLAN/ROADMAP、CODE_INDEX |
| R03 长期契约最小澄清 | AGENTS仅澄清新采集由DAA承接、旧CA冻结兼容、FF为独立现场runtime，以及FE001现有装配能力与验收层级；不改变STD/DIRECT/BACKFILL、角色、权限、发布、工具链、时区、表格规则或业务边界。 | AGENTS第2/3节相关句；根README导航 |
| R04 AW现状 | 清退AW README中作为当前事实的“仅S2初始化”、Simulation启动、DAA普通YAML来源及特殊启动别名要求。统一普通pnpm tauri dev、应用隔离、本地配置权威；补事实/业务provider依赖入口。AW PLAN的CU行与已接受CU008一致，SMA子阶段不被父draft遮蔽。 | AW README/PLAN |
| R05 SMA已采用与未采用 | 在白皮书、运行原理、SMA/DAA设计当前正文与图中，原位替换已过时Backend-held配置/正常Facts→POST描述。明确SQLite单文档配置已实现、004 QA通过待终验；localStorage/多JSON业务权威未采用；完整关系配置库、active/previous发布系统、运行库/outbox及GET→POST执行仍为后续范围。历史TSS来源和兼容fixture保留；来源身份适配尚未实施，本任务不补做。 | AW两总体设计、DAA/SMA设计、docs索引 |
| R06 provider进度与合同引用 | 将“A/source-only/B待批”等当前说明更新为实际隔离A+B验证范围和下一gate；不能写provider-ready或已部署。已经冻结的正式字段/摘要/DDL/游标/限额引用provider源码合同，不继续全部列为待定，也不复制或改动机器schema。旧monitor/Projection和新plc_facts七表、业务四表的owner及迁移顺序分别解释；不暗示已迁真实库。 | 两provider README、contracts README/PLAN、backend README/PLAN、CODE_INDEX、DAA/SMA设计 |
| R07 DS操作语义 | 协调DS设计§4.2、配置对象和流程中“保存即产不可变版本”与§15显式发布的冲突。当前顺序为编辑→保存同一草稿→显式保存为版本→停机加载→另行启动；重复内容、保留/删除及selected/loaded保护只引用当前手册和源码，不扩展新功能。10月29日增量不追认为旧QA或旧Owner接受。 | DS详细设计及docs导航 |
| R08 FF与状态索引 | 根总览补FF005已接受及FF004 r2 A的有限QA交付；field-flow PLAN中仍使FF004 r1看似当前执行范围的邻接说明按历史关系澄清。保留三基础kind与v1兼容、Rust主线/Python原型、Modbus结构与通信区别、hold_ack及UTC限制。FE001、BE008、ARCH001仅按原有效记录机械同步状态和下一gate。 | 根PLAN/catalog/README/ROADMAP、frontend/backend/FF PLAN |
| R09 取消、替代与后移 | FOA及合并宿主按AW007 r2明确替代；共享Flow Core/画布/中央管理标为非近期前置，未来可选内容不擅自删为已取消。带明确日期/历史标签的旧事实保留来源和历史效力；处理仍以“当前”出现的冲突，不能只加顶层免责声明而让正文两套口径并行生效。 | ROADMAP、AW两总体设计及DAA/SMA设计 |
| R10 运维入口与历史 | contracts PLAN的旧root授权阻塞、旧head和旧路径标明历史，并链接当前owner/证据；BE009/010验证不得代替旧CA取得现场接受。INITIALIZATION仅补默认关闭、schema/time采用gate与手册链接，不新增生产/迁移/容器可复制操作命令，不改原已发布版本事实。 | contracts PLAN、INITIALIZATION、backend说明 |
| R11 双语与索引职责 | 既有EN/ZH pair语义、日期、状态及下一gate对称；现有中文设计正文不另造英文副本。README保留稳定入口，PLAN保留短索引，具体映射/命令/结果写本任务tasks和checklist；本任务不创建docs PLAN或重复台账。 | 第4节全部pair及本任务bundle |

## 4. 精确allowlist与角色

共**42条精确路径：39件现有Markdown＋本任务3件分阶段文件**。编号只用于写面审计，不是要求把所有允许文件都改一遍。无须改变的文件保留字节，并在tasks对应R项说明；未列路径不因相邻或链接而获得写权限。

当前PM只可写第40项。精确r1批准后，Development可写下表标记的文档及第41项；根PLAN/catalog四件由主协调根据角色事实机械同步。第42项只在真实developer_handoff后由新的fresh-context Verification创建/更新。AGENTS的可写范围还受R03约束。

| # | 精确路径（仓根相对） | 角色/允许处理 |
| --- | --- | --- |
| 01 | `AGENTS.md` | Development；仅R03事实/owner澄清 |
| 02 | `README.md` | Development；当前结构/运行边界/入口 |
| 03 | `README.zh-CN.md` | Development；对应中文 |
| 04 | `PLAN.md` | 主协调；本任务及R01/R02/R08真实状态、来源和下一gate |
| 05 | `PLAN.zh-CN.md` | 主协调；对应中文 |
| 06 | `ROADMAP.md` | Development；当前快照/图/依赖及历史替代说明 |
| 07 | `ROADMAP.zh-CN.md` | Development；对应中文 |
| 08 | `INITIALIZATION.md` | Development；仅R10导航与采用边界说明 |
| 09 | `INITIALIZATION.zh-CN.md` | Development；对应中文 |
| 10 | `CODE_INDEX.md` | Development；有限现有能力及来源/gate说明，不重排无关索引 |
| 11 | `plans/README.md` | 主协调；本任务目录及R08现有任务真实状态/实际角色链接 |
| 12 | `plans/README.zh-CN.md` | 主协调；对应中文 |
| 13 | `automation-world/README.md` | Development；R04配置/入口/当前阶段 |
| 14 | `automation-world/README.zh-CN.md` | Development；对应中文 |
| 15 | `automation-world/PLAN.md` | Development；仅已核当前阶段/跨工程依赖摘要 |
| 16 | `automation-world/PLAN.zh-CN.md` | Development；对应中文 |
| 17 | `docs/README.md` | Development；同步本次现状/设计及证据导航 |
| 18 | `docs/README.zh-CN.md` | Development；对应中文 |
| 19 | `docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md` | Development；R02/R05/R06/R09当前表述与直接冲突 |
| 20 | `docs/AIIS_AW_Runtime_Design.md` | Development；对应运行图、配置权威与能力边界 |
| 21 | `docs/AIIS_DAA_Detailed_Design.md` | Development；当前事实provider及SMA协作/未接线上传边界 |
| 22 | `docs/AIIS_SMA_Detailed_Design.md` | Development；当前本地配置、关闭执行与未来可靠运行区分 |
| 23 | `docs/AIIS_DS_Detailed_Design.md` | Development；仅R07及其直接关联语句 |
| 24 | `contracts/README.md` | Development；现有provider验证层级和demand关系 |
| 25 | `contracts/README.zh-CN.md` | Development；对应中文 |
| 26 | `contracts/PLAN.md` | Development；历史K阶段/旧路径与当前证据导航 |
| 27 | `contracts/PLAN.zh-CN.md` | Development；对应中文 |
| 28 | `contracts/published/http-api/plc-facts-v1/README.md` | Development；只同步实际技术验证/采用gate，不换合同 |
| 29 | `contracts/published/http-api/plc-facts-v1/README.zh-CN.md` | Development；对应中文 |
| 30 | `contracts/published/http-api/business-integration-v1/README.md` | Development；同上业务provider |
| 31 | `contracts/published/http-api/business-integration-v1/README.zh-CN.md` | Development；对应中文 |
| 32 | `backend/README.md` | Development；当前模块/兼容链/集成gate导航 |
| 33 | `backend/README.zh-CN.md` | Development；对应中文 |
| 34 | `backend/PLAN.md` | Development；R06/R08有限状态/下一gate纠偏 |
| 35 | `backend/PLAN.zh-CN.md` | Development；对应中文 |
| 36 | `frontend-js/PLAN.md` | Development；仅R08 FE001等直接矛盾 |
| 37 | `frontend-js/PLAN.zh-CN.md` | Development；对应中文 |
| 38 | `field-flow/PLAN.md` | Development；仅R08当前Revision与历史关系说明 |
| 39 | `field-flow/PLAN.zh-CN.md` | Development；对应中文 |
| 40 | `plans/ARCH-DOC-001-project-state-and-decision-sync/spec.md` | PM/Human Owner；范围、修订及真实批准 |
| 41 | `plans/ARCH-DOC-001-project-state-and-decision-sync/tasks.md` | 批准后Development；R项到文件的改写/保留映射、实际检查和交接 |
| 42 | `plans/ARCH-DOC-001-project-state-and-decision-sync/checklist.md` | handoff后fresh Verification；独立文档结论及真实Owner决定 |

### 排除与保护

不修改任何产品/测试/脚本/依赖/锁/配置/env/YAML/JSON/OpenAPI/schema/DDL/Alembic、数据库/profile/历史数据、机器合同状态正文、其他任务bundle及其证据、CHANGELOG、LICENSE、Git refs、`.codex`/角色/workflow/skills。不得新建附加状态报告、任务级双语文件、evidence.md或空未来bundle；不复制/重编码旧证据。

本任务不运行应用/监听、软件测试或编译，不读取真实配置/库、不执行任何DB（含SQLite）或Docker动作、不连接PLC/第三方服务，不安装项目或全局helper，不提交/推送/发布/部署、不发送消息或邮件给外部人员。PM草案/等待不启动长任务通知执行窗；后续协调者按现行workflow处理文档实施执行窗。

## 5. 批准后的实施顺序与交接

1. **固定进入快照**：完整读本bundle、根/最近治理入口及第2节最新有效证据；记录HEAD、工作树、39件文档before哈希及排除面保护清单。与本r1语义有关的真实后续Owner状态，可按同一范围机械同步并记来源/日期；能力、风险或allowlist实质改变返回PM，不猜测取消决定。
2. **形成R项映射并同步**：tasks逐R项列“原位改写/只加历史标签/保留字节”及理由；先对齐当前状态、owner/配置与source引用，再协调正文/图/导航。Development不得直接替旧任务作新QA或接受；根四索引由主协调据实际角色handoff同步。
3. **必要静态检查**：运行第6节检查，修复本任务造成的文档问题。检查产物只用自有`/private/tmp`目录；关键摘要、真实命令/退出码和限制写tasks，不把临时路径当唯一证据。发现旧checker或任务外问题，分类记录，不扩面修复。
4. **Development交接**：给出精确r1、全部改写/保留文件、diff与输入/结果哈希、R项覆盖、检查结果、资源及未渲染等限制，状态developer_handoff。
5. **独立Verification**：实际命名verification以`fork_turns="none"`消费完整输入，独立复核第6节AC，仅写checklist；失败交Development返工，范围变化交PM。文档qa_passed仅进入Owner文档终验，不接受产品或现场。

适用skill为`aiis`、`project-governance`；Development/Verification触及CODE_INDEX时加`code-document-indexer`。纯文字/图的事实同步不要求无差别加载技术实施skill或运行技术栈。若发现必须改程序/机器合同才能解决，记录后停止该部分并回PM另定范围。

## 6. 文档验收标准与检查边界

| AC | 可检查的通过条件 | 对应需求 |
| --- | --- | --- |
| AC01 | Task ID/Revision/STD阶段和角色正确；42路径唯一，实际差异只在获批角色写面；tasks/checklist按真实gate创建，未伪造事前批准或产品结果。 | R01/R11 |
| AC02 | tasks逐R01–R11给出原位改写或保留理由及文件/章节；全部作为当前入口的已核冲突闭合，日期明确的历史不被误删/改写。 | 全部 |
| AC03 | DAA受控B接受、上传未接；Backend隔离A+B通过与Owner/真实采用pending；SMA子阶段与父draft、004配置QA/正常执行关闭；FF各Revision与有限能力，均与所属最新有效记录一致。 | R01/R02/R04/R06/R08 |
| AC04 | 冻结CA兼容链、新事实provider和未接通数据/业务链分别呈现；事实ACK不当作业务ACK、接口成功不当作设备完成；新CA/AWB/AWC/AIW等未来能力不冒充已实现。 | R02/R03/R06 |
| AC05 | 所有现行SMA配置说明/图统一为Rust/SQLite单文档revision；UI/技术偏好独立；旧TSS仅来源/显式fixture；旧正常投递、Simulation、事实生产/帮助不复活，未来outbox/active版本/GET→POST不假实现。 | R04/R05 |
| AC06 | FOA/合并宿主明确替代；共享Core/画布/中央管理为可选未来而非近期硬前置；未明确取消的草案和旧源/验证/接受链接均保留。 | R09 |
| AC07 | DS当前保存草稿与发布版本分离，加载/启动及保护引用保持；旧接受与10月29日增量人工确认边界一致。FF hold_ack、FF/DS旧UTC及Backend真实时间采用限制没有被抹去或写成已修。 | R07/R08/R10 |
| AC08 | FE001/BE008/ARCH001纠偏有原checklist/Owner依据；合同需求proposed与provider技术验证层级区分；旧contracts阻塞/head/路径明确历史化，不为旧CA或生产补造通过。 | R01/R06/R08/R10 |
| AC09 | 现有16组EN/ZH pair在能力、状态、日期、gate、方法/路径和本轮修改的命令块上语义对称；AGENTS仍中文唯一契约，五份中文长期设计无新语言副本。 | R11 |
| AC10 | 对全部实际修改Markdown及本spec的本地文件/目录链接、reference-style目标和相关锚点做离线检查；新增/修改目标存在，原锚点改变时同步allowlist内引用，范围外反向引用需保留兼容锚点或返回PM。 | R02/R11 |
| AC11 | 新改Mermaid图逐节点/箭头、状态图例、子图/引用及围栏完成静态核对；有现成独立parser/render则记录实际结果。当前已知无mmdc/项目Mermaid依赖，不因缺工具安装到项目；未parse/render必须明示，不能冒称视觉验证通过。 | R02/R04/R05 |
| AC12 | `git diff --check`通过；使用现有只读治理checker核对本新bundle及索引（按其staged gate能力），本任务及所改索引不新增可归因诊断；全仓既有诊断分类保留，不以全仓exit 0为本任务条件，不批量修旧bundle或改checker。排除面hash/diff无本任务改动。 | 全部 |
| AC13 | INITIALIZATION只增加关闭态/采用gate和现有手册入口，没有新增DB/生产操作命令；公开合同目录仍仅README文字变化，所有机器JSON/源码/旧任务证据不变。没有运行产品、DB/Docker或外发。 | R06/R10/保护 |
| AC14 | Development自检与fresh-context文档QA分开；命令/退出码/环境限制真实记录，资源归属/保留理由明确；qa_passed和Owner文档终验分开，任何产品/部署/发布终态未由本任务授予。 | R01/R11/第5节 |

16组pair为：根README/PLAN/ROADMAP/INITIALIZATION四组、根plans目录一组、AW README/PLAN两组、docs索引一组、contracts README/PLAN两组、两provider README两组、backend README/PLAN两组、frontend PLAN一组、FF PLAN一组；实际以第4节展开路径核算，不以文字计数替代检查。

协调侧在新bundle创建前的只读预检已返回exit 1和407条既有诊断，包含历史多轮metadata、旧任务/索引链接形式、Allowed Writers及find相关问题；这是checker兼容/既有状态基线，不是本PM或后续文档QA宣称全仓通过。Development与Verification须保留本轮可归因差异、旧问题分类和真实退出码；不得为了全绿改写旧bundle或失败史。

可执行检查限于文件读取、哈希、文本/链接/锚点与图静态核对、Git只读diff/status以及现有治理只读checker。不得运行旧initialize/upgrade/bootstrap apply。不得为了文档变更运行pnpm/Cargo/pytest全量回归、真实环境探测或数据库验证。既有产品QA仅作引用；本次结论是文档一致性。

## 7. 风险、兼容与回退

- **历史与当前混淆**：旧正文有已接受的日期快照；以当前入口原位协调、历史标签/来源链接保留其效力，不重标旧QA候选。原任务bundle和Git历史是历史事实，不复制整份旧稿制造新权威。
- **状态扩大**：源码/隔离B QA不等于provider-ready、Owner接受、真实采用或全链完成；demand状态也不因同步自动变化。不得把一个任务的通过转移给另一个任务。
- **改变规则的风险**：AGENTS只允许第3节所述事实澄清，其余长期条款逐字保护；实际发现新安全/治理取舍回PM新Revision。
- **并行修改**：本任务不独占整个仓库；每次写入前核对before，按段合并已知并行改动。保护真实配置、旧库、分支/worktree和任务外资源，不reset/revert/clean。
- **回退**：仅回退确认属于本任务的文档patch，保留并行修改、已发生的真实决定和原证据；不移动tag、回退程序/配置或撤销外部动作。若需扩大回退面，先由Human Owner另行决定。

## 8. 批准点、PM自检与当前handoff

Human Owner需要审阅的是本**ARCH-DOC-001 r1**的文档-only范围、42路径、R01–R11、AC01–AC14和上述限制。精确批准后才创建tasks并由命名Development实施；真实handoff后才启动新的fresh-context Verification。Owner文档最终验收继续独立，不借“同步一下”推断其已发生。

PM当前只新增本spec，未改其余文档/索引/产品，未创建tasks/checklist、运行产品或DB/Docker、重做旧QA、发送消息给外部人员或执行Git写入。2026-11-05实际以stdlib Python inline只读自检确认42路径唯一、39文档存在、16组pair、staged角色文件未建、metadata/R01–R11/AC01–AC14及30个本地路径/显式锚点均合法，exit 0；另执行`git diff --check`和`git status --short`均exit 0，状态仅本新任务目录。未在PM阶段运行治理checker或Mermaid/product验证；第6节407条是协调侧预检输入，不冒充本PM结果。上述只是PM草案自检，不是Development自检或独立QA。若自检发现文字/计数问题，PM仅修订本draft后重新给出SHA；技术范围变化先形成新Revision。

当前交接：**PM -> Human Owner审阅精确r1；Development、Verification、Owner文档终验均pending。**

### Human Owner精确范围批准登记（2026-11-05，Asia/Shanghai）

唯一主协调`/root`转递Human Owner通过本会话对精确范围问题的实际答复：

> 批准 ARCH-DOC-001 r1，按 STD 实施

批准对象为本r1完整草案，批准前SHA-256为`4cf69dc1037b569b3e5dfb251ec0cf7c68f81b70eecf126327aad632331c79f4`。本PM据此只更新顶层Status/Handoff并追加本收据；Revision仍为r1，第4节42路径、R01–R11、AC01–AC14、实施顺序、风险和排除项全部不变，不新增或缩减技术范围。

**时间效力：**上文“当前只形成草案”“尚未审阅/批准”“批准后才交接”及末尾原“当前交接”均保留为批准前历史时点；当前范围批准及handoff由本节和顶层元数据覆盖。旧语句不能撤销本次明确批准，本次批准也不表示Development已实施、QA通过或Owner文档最终验收已经发生。

**当前交接：PM -> 命名Development。**由唯一主协调实际调用Development按本r1创建tasks并实施；真实developer_handoff后另启新的fresh-context Verification创建checklist，最后仍交Human Owner文档终验。PM本次未修改其他文件、创建tasks/checklist、运行产品/DB/Docker或执行Git写入；主协调四处根索引及其他并行改动保持。
