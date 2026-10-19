Task ID: DAA-005
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已于2026-10-19精确批准DAA-005 r1；交唯一coordinator /root 启动实际Development先执行P0，之后新fresh-context Verification与Owner最终验收，当前未创建tasks/checklist或实施产品
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: DAA 多 DB 源文件识别、逐块编号与有界真实语法兼容、保全式草稿导入及标准嵌套结构辅助偏移
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: aiis-ics-arch::DAA-005 r1 exact scope approval -> Development -> new fresh-context QA / Verification -> Human Owner final acceptance
Related Task: aiis-ics-arch::DAA-004 r1; aiis-ics-arch::DAA-003 r1; aiis-ics-arch::DAA-002 r2

# 多 DB 源码导入与嵌套结构辅助偏移

## 1. 当前效力与已批准的取舍

**最新批准与当前效力（2026-10-19，Asia/Shanghai）：** Human Owner 已明确批准精确 **aiis-ics-arch::DAA-005 r1**，批准前草案 SHA-256 为 `099c2698b57628d6926c4ae92b4147325a8aef2bd19c558e7f8fc9fcdf07ffe7`。唯一 active lifecycle coordinator `/root` 真实传递原话：

> 可以，批准 DAA-005 r1，按 spec 完成多 DB 自动识别、逐块编号、DB/UDT 语法兼容和嵌套结构辅助偏移，并完成独立核验。已有 SQLite 配置和历史不要覆盖，只做必要增量验证，不重复整套测试；阶段 C、DS、后端和 SMA 暂不做，真实 PLC、生产数据库/API 和现场切换不在本次范围。

当前状态为 `owner_approved`，G0范围批准已满足；P0、产品实施、自检、developer_handoff、新fresh-context Verification和最终验收均尚未发生。本轮只补真实批准、状态和handoff，R01–R11、AC01–AC13、allowlist、范围与风险原字节保持。执行前新基线为 `/private/tmp/daa-005-r1-execution-3jld50j8/baseline.json`（1687路径，含旧ignored DB及Owner真实DB），PM批准diff/文档自检仅存其 `pm/`；§2保留原起草基线事实。此批准不提供阶段C、DS/Backend/SMA、真实PLC/生产数据库/API、现场切换或发布权限。

起草背景：2026-10-19（Asia/Shanghai），Human Owner 请求：

> 可以，就按这个流程，先出 DAA-005 r1 spec，把多 DB 自动识别、逐块填写块号、真实 DB/UDT 语法兼容和嵌套结构辅助偏移纳入，明确导入预览和已有配置的处理。已有 SQLite 配置和历史不要覆盖，只做必要增量验证，阶段 C 暂不做，批准后再改代码。

本 r1 起草时为draft，现已按上述真实决定转为 **owner_approved**；下一gate由coordinator将原精确范围交实际Development。PM本轮只记录批准，不改代码、测试、配置、README/PLAN、索引或真实输入，不运行parser、SQL、构建、原生程序、PLC或项目API，不创建tasks/checklist或启动后续角色。唯一 active lifecycle coordinator 为 `/root`，实际 PM 为 `/root/daa005_pm`。PM TOML 的 `gpt-6.1-sol / max` 仅为配置证据；profile 为 `contract_only`，不宣称平台 ACL、自动路由或团队激活。

本次精确批准的固定方案（以下原方案条款保持）：

1. 在既有点位页选择目标 PLC 与 `.db/.udt` 后，**自动识别 → 每个 DB 填实际块号/勾选 → 预览差异 → 一次确认写草稿**。不加识别按钮、新页面或长向导。UDT 是类型定义，不填 DB 号。
2. 只更新明确选中并确认的草稿块。**已有 DB 改号、块改名、叶路径删除/改名，以及来源身份歧义，本 r1 保守阻断并保留旧配置**；不提供自动删点、模糊匹配、批量覆盖或 tombstone 管理。新增点和可明确匹配的类型/顺序变化按下文处理。
3. 来源原文按不可变版本保留，逐 DB 绑定具体块与 UDT 版本；未选 DB 不因同文件或同名 UDT 被间接修改。旧单 DB JSON 兼容读取，新增可选元数据不要求 DDL、不批量重写旧存储。
4. 辅助偏移扩至已证明完整、标准非优化的 STRUCT/无环 UDT/一维定长数组；先建立独立布局 oracle，再实现。预览不写地址；用户一次显式确认可保存并确认非人工地址，**不要求逐点再确认第三次**。人工地址始终受保护，真实 PLC 地址仍需现场另行校核。
5. 只验证新增解析/映射/事务/布局/界面闭环及受影响保护；不重跑阶段 B 整套采样、反复原生退出重启、DS/S7 或上传矩阵。阶段 C、Backend、SMA、DS 具体开发及真实现场动作排除。

本任务独立分类，无 Parent Task ID。DAA-004 r1 当前独立 `qa_passed`，DAA-002 r2 与 DAA-003 r1 也各自待 Human Owner 最终验收；它们提供现行技术基线，不向本任务转移批准或终验。本请求不构成旧任务验收。

## 2. 消费依据、当前事实与输入角色

PM 已读根 AGENTS、README/PLAN 双语、canonical workflow、实际 PM TOML、AW/DAA 最近 README/PLAN、DAA app/local_store 说明、完整 DAA-004 三文件及 DAA-002/003 的源导入、地址、CAS、数据保全合同；作用域检索无更近 AGENTS。应用 `aiis`（含 CONTRACTS）、`project-governance`、`plc-point-mapping`；专门实现由 §9 交 Development/Verification，PM 不替代技术执行。

入口：[根契约](../../../../AGENTS.md)、[生命周期 workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)、[DAA README](../../README.zh-CN.md)、[DAA PLAN](../../PLAN.zh-CN.md)、[DAA 详细设计](../../../../docs/AIIS_DAA_Detailed_Design.md)、[DAA-004 spec](../DAA-004-migration-notice-and-source-import-validation/spec.md) / [tasks](../DAA-004-migration-notice-and-source-import-validation/tasks.md) / [checklist](../DAA-004-migration-notice-and-source-import-validation/checklist.md)、[DAA-003 spec](../DAA-003-sqlite-only-startup/spec.md)、[DAA-002 spec](../DAA-002-local-acquisition-loop/spec.md)。本任务后续角色文件未形成，不提前创建链接。

| 当前只读事实 | 证据及其限度 |
| --- | --- |
| 底层已有多声明扫描，尚无完整多 DB 编号流程 | `infrastructure/tia_source.rs::Parser::blocks` 可返回多个 DATA_BLOCK/TYPE，但导入对每块都读取同一个 `SourceDocument.db_number`。前端点位页也是每个 `.db` 文件一个编号框，不能据此宣称已有逐块流程。 |
| 当前真实语法缺口 | header 限优化标志/VERSION，缺 `NON_RETAIN`；字段解析在名字后立即期待冒号，不能处理所提供的 `S7_SetPoint` 属性段。静态对读不等于已经在产品导入真实文件。 |
| 当前地址与保存边界 | `plc_layout::preview` 拒 `!complete || !flat`，因此受控 UDT 已展开仍不能推算；预览对象的 proposed.confirmed=true 不代表已持久确认。当前 source confirm 可以保存带 issues 草稿，本 r1 仅对新选中导入集合增加严格提交准入，不把旧行为误写成已严格拦截。 |
| 原保护 | 双 SQLite v1、DELETE/EXTRA、单 owner/串行写、草稿 ETag/派生证明、显式激活、immutable revision/context/sample、pending 与 YAML 私有 receipt 均保持。普通启动已是 SQLite；不恢复 YAML 运行模式。 |
| 已核 DAA-004 bundle | spec `c84c93612e828578f0a4a3beaa406642b7fe7401624f1af71276a470cc1d5a8e`；tasks `947486ea31708053fca84132a9d380d3f94396bc03c45b6929e4ea6fc23a2f21`；checklist `61cd7ab3442d4fc47fcebd231508e3064092a8024acd92d1565eaff655a0059e`。只核用其原通过范围与真实限制，不重做旧终验。 |
| 当前工作树 | HEAD=`f85bea8bbf36b491968c3dc9a839518a1ed434a8`；存在大量其他任务 dirty/untracked。coordinator before=`/private/tmp/daa-005-r1-spec-qo_ufkpo/baseline.json`，固定 1683 路径；不得以 HEAD 代替当前 before 或回退他人变化。 |

Human Owner 已提供两个真实文本，位于 DAA `src-tauri/tests/fixtures/source-import-minimal/`：

| 输入 | 磁盘原字节 SHA-256 / 已读事实 |
| --- | --- |
| `DB_20260701.db` | `691617444859a39364613f263e724b84a230d366fe5f7c1910003d82b23b3680`，40649 B，UTF-8 BOM/CRLF；6 个命名 DATA_BLOCK，没有声明实际数字块号，含 NON_RETAIN、字段 S7_SetPoint、UDT 引用和一维数组。 |
| `UDT_20260701.udt` | `939e3754acb1ec1d72e9dcf39b7212ab8506160fda8ea443a58ee5452aafa1f2`，709 B，UTF-8 BOM；3 个 TYPE。 |

这两个文件属于 Human Owner 私有输入，不是 DAA-004 或本任务公开 fixture：只读参考，未来可在自有 tmp/内存作显式隔离解析；不修改、移动、复制进公开示例、取消其忽略、stage/commit，亦不导入真实 profile。上述 SHA 是原文件字节，不冒称当前 `File.text()` 已将相同字节保存到 SQLite。公开验证必须另写小型脱敏样例，不能复制这两个文件或以它们作为唯一可复现 gate。

文件角色固定：SQLite 是配置/历史权威；DB/UDT 是用户显式选取的结构输入；source SHA、识别计划和验证 JSON 是来源/中间/期望材料，均不是新采样值或后端合同。`BEGIN` 及字段初始化表达式不执行、不变成实际采样或 DS 初值。`plc-point-mapping` 的通用 XLSX/YAML SOP 仅参考结构/校核边界，本任务已由 Owner 明确选择 GUI→SQLite，不引入 XLSX 或 YAML 配置入口。

## 3. 编号需求

### R01. 精确批准、已有数据与工程不变量

精确 r1 获 Human Owner 范围批准后，才由实际 Development 创建 tasks 并实施。写前固定已批准 spec SHA、当前完整 before、源/锁/输入/保护面；只在 §6 封闭路径写入，保留旧失败记录和所有他人改动。需求、allowlist、验收或风险实质变化回 PM 新 Revision，不从已批准旧任务扩权。

本任务不清空/替换用户草稿，不回写 active/previous、已有 immutable revision、历史解释、sample/manifest 原字节、point/source generation/seq、pending/reference 或 `__daa_yaml_migration_v1__` 私有 receipt。导入只是当前草稿中的显式目标 delta；运行 active 若存在，继续拥有自己的原版本，不被导入暗换。验证只用本任务新建或可核归属的隔离 tmp 实例，不使用旧 DAA-002 live76、用户默认 profile、真实 env/YAML/数据库。新二进制读取旧存储不产生兼容性写回。

保持4 PLC、每PLC8组/32 DB/4096叶、每组256启用点、周期≥500ms、每文件1MiB/每次4MiB、展开深度≤8、每个一维数组≤1024元素、配置JSON≤16MiB、现有总对象/来源上限（sources≤128）及物理写预算。历史来源版本也计入限额，不能无限留存。沿用锁/恢复、v1 DDL、SQL适用边界、单 owner/单刷新、actor/driver/read gate、容量/日志故障锁存；不升级依赖或重过不相关 B0。

### R02. 自动识别与简单页面流程

选择目标 PLC 后，在现有“来源文件与完整结构”区域一次选 `.db/.udt`，自动调用 Rust 只读识别，不另加识别按钮、导航页、永久通知卡片或多层向导。未选择 PLC、存在未保存编辑或编辑弹窗时，按既有 guard 提示先处理；选择器取消保持现有输入与已存配置，不伪造空导入。

显示文件数、识别 DB/UDT 数及逐块行表。每个 DATA_BLOCK 一行：勾选、来源文件/块名、DB编号、将新增/更新/冲突的摘要、诊断/可展开叶数；TYPE 单独作为依赖摘要，不显示编号框。默认勾选所有已识别 DB（有问题的行明确错误），可取消部分；0个选中不能确认。DB多时表格默认每页10条、支持10/20/50、勾选与编号跨页稳定；只看当前页不等于只导入当前页。结构与完整差异默认折叠，诊断定位到文件/行/块/路径；不得一次展开所有树造成长页面。

自动识别只是安全分界与清单，不冒称所有块均完整解析成功。可明确分界的单块错误保留在该行；取消选中问题块后可预览其他合法块。文件级引号/注释/声明边界损坏、无法确定安全分界则整文件阻断，不以正则跳过未知字段恢复成假完整。所有选择/编号校验和完整结构展开的权威在 Rust，不在 UI 实现第二套 parser。

### R03. 逐块编号、身份与旧单 DB 兼容

块身份以所选 PLC、来源 lineage 与声明 kind+原始块名的结构化 key 表示；filename、声明顺序、行号和 DB 数字都不是独立持久身份。原名/行号供展示定位，符号比较沿现有受限大小写规则，重复/歧义明确拒绝，不用字符串拼接猜路径。源版本由原文 SHA/内容验证，DB/point 继续 stable opaque ID。

每行由用户填写实际 DB 号，范围1–65535、整数；唯一性为 `(plcId, dbNumber)`，不同 PLC 可以同号。本 r1 不解析/推断数字声明号：无论名字、排序、文件名日期或相似后缀，都不能猜号。已核的旧绑定可建议原块号，但必须在预览中可见；新文件行无可信旧绑定时为空。数字声明若不在本 r1 明确语法集合则诊断，不悄悄当名称或自动号。

已有绑定的建议必须同时验证目标 PLC、既存 source lineage/version、旧 source 中唯一原块 key、DB.sourceId/原编号与结构路径关系；不是新文件同名就绑定旧DB。旧 JSON 没有新元数据时，仅在旧 source 可完整识别为唯一单DB、`source.dbNumber==Db.number`、块名与DB关系唯一时作内存兼容映射；未知/多义不猜、不更改旧正文。旧来源缺完整结构时允许作为诊断查看，不能冒充可信重导关系。

跨文件重复块定义、同一选中块重复映射、重复编号、占用其他 lineage 的既有编号、跨PLC targetId、伪造 source/blockId 一律阻断本次选中集合。已绑定 DB 改号/改块名不作为普通重导操作；本 r1 显示原因并保留旧，后续另定明确迁移范围。用户可取消冲突行；不能靠覆盖按钮将陌生块强绑到旧身份。

### R04. 有界真实 DB/UDT 语法兼容

在现有受限 parser 上支持多 DATA_BLOCK/多 TYPE、引用集合与下表，不实现完整 TIA 编译器：

| 范围 | r1 合同 |
| --- | --- |
| 文本读取 | `.db/.udt` UTF-8/UTF-8 BOM、LF/CRLF、现有行注释/字符串/有引号名称；严格解码，非UTF-8拒绝，不猜编码或安装编码依赖。文件选择使用原字节读取及严格UTF-8解码，保留BOM/CRLF；parser只在解析视图忽略BOM。 |
| 原文与hash | `SourceDocument.content` 保留实际选取文本，现有sha256定义为其UTF-8字节摘要；识别输入另带原字节hash/bytes，经Rust复算与严格解码的字节等价核验，不接受客户端自报hash。原字节hash与解析视图hash分开命名；不归一化换行再冒称原文。 |
| DB header | 支持显式 `S7_Optimized_Access := 'FALSE'`、VERSION、NON_RETAIN/RETAIN；保留声明顺序。缺失/未知/TRUE优化标志不能给可推算的完整证明。保持属性/保持性仅来源描述，不赋予读写权限或运行策略。 |
| 字段属性 | 支持所提供格式的字段名后、冒号前 `{ S7_SetPoint := 'False' }`，允许该白名单布尔值大小写变化；不计算属性表达式。与既有优化标志分别解析；未知属性/值/位置给明确诊断，不能无界跳过花括号。 |
| 结构和类型 | 完整保留 STRUCT、无环多级 UDT、现有一维常量范围 `ARRAY[a..b] OF 标量/UDT/STRUCT` 的节点、路径、上下界、声明顺序、注释/源定位；a≤b可为负/非零下界。保留现有受支持标量/STRING结构导入。 |
| 明确拒绝 | 缺/循环/同一依赖集合内重复UDT、重名字段/路径碰撞、截断声明、动态/多维/展开后嵌套数组、AT/指针/VARIANT/FB实例、未知类型/语法、超限或整数溢出定位拒绝；不得忽略字段后推算后续地址。 |

只读识别可返回问题行；选中块必须完整展开且依赖无致命错误才可确认。UDT无DB号，可同文件定义多个；解析其类型闭包只取选中块明确绑定的新/旧源版本。完整树包含未启用字段，不按采集开关截断布局。BEGIN/初值不执行、不填点值，不修改PLC或源文件。真实文件尚未证明的语法不得包装为全 TIA 导出兼容。

### R05. 来源版本、共享 UDT 与无 DDL 兼容

持久模型最小扩展为新版本可选、带 serde default 且缺省省略的 JSON 元数据；不改变本地DDL/application_id/user_version、ledger编码或样本schema。精确字段名可按现有camelCase实现，但必须保持以下信息责任：

- SourceDocument 仍保存原 `id/name/content/sha256/plcId/dbNumber/diagnostics`；新增可选稳定 lineage 标识。`id` 指 Configuration 内按PLC区分的逻辑来源版本，旧来源缺lineage时以内存中的旧id作起点。原 `dbNumber` 只作旧单DB兼容输入；新多块来源不以单值代表全部DB。
- Db 继续保存实际数字 `number`、具体版本 `sourceId` 和稳定 DB id；新增可选 import binding：明确 block key、来源 lineage 与所用 UDT source版本ID闭包。绑定由 Rust 识别/确认流程产生，普通 save 不得伪造或改写。
- 相同来源原文/绑定的重导复用原版本/DB/point ID；没有有效变化时返回 unchanged、原ETag，不生成空历史版本。原文改变时新增不可变 source版本并只重绑已选DB，不 UPDATE 旧source正文或原hash。物理归档去重遵循下段，不得用 INSERT OR IGNORE 掩盖同id异内容、hash/内容冲突。
- 同一PLC/显示filename可出现不同不可变版本；本 r1 取消“仅凭 `(plcId,name)` 替换全部来源”的算法，将其降为展示/候选提示，使用 lineage+version 区分。名称相同的历史 UDT 版本不合并进全局类型字典；按每个目标DB的显式版本闭包解析，闭包内同名异定义才冲突。

区分 Configuration 内按PLC的逻辑来源/binding与 `source_documents` 按全库 UNIQUE sha256 去重的物理内容归档：两个PLC或不同显示filename可合法导入完全相同源字节，各自JSON保留自己的逻辑id/PLC/lineage/version绑定。命中相同hash时必须核content完全一致，随后复用已有归档，保持其原row.id/name/diagnostics/content不变；不要求该物理row.id等于每个逻辑SourceDocument.id，不将逻辑id/name不同误报冲突。真正同一逻辑id或物理row.id指向不同content、或hash/content不符时才拒绝；无DDL、不覆盖旧归档来“修复”重复。

同文件未选块、未选DB引用的旧UDT、其他PLC均保持其原 source引用、树、点、开关、地址与确认状态。若某次 UDT 修改还被未选DB使用，预览明确“仅所选DB使用新版本，其他DB保留旧版本”；不能为复用一个文件名把旧出处换掉。配置中保留所有仍被草稿/版本需要的source；沿现有引用/版本回收规则处理不再被引用者，不新增无限版本服务或新GC。超sources/16MiB/写预算则整次拒绝，不能通过删除未选来源腾空间。

新版本能读旧JSON，不表示旧二进制能读含新增字段的新JSON（现有 deny_unknown_fields）。不得承诺无条件降级、启动时“修复”旧revision或重新编码既有sample/context；向后程序兼容/现场回退需单独证明。`yaml_migration.rs` 仅为新增可选字段填默认值而作构造器适配，其发现/空资格/CAS/receipt/归档原字节/策略不变。

### R06. 预览、CAS 与所选集合原子提交

复用具名 `daa_import_sources`，在原 `sources/expectedEtag/confirm` 基础上增加有界可选 `stage`（identify/preview/confirm）、目标PLC、逐块映射和预览token/digest；不新增任意文件路径读取、SQL、HTTP或通用执行命令。stage缺省时仅兼容旧单DB请求，不能将旧dbNumber广播到多DB；多DB须逐块映射。stage/confirm矛盾请求拒绝。

| 阶段 | 权威输出 / 副作用 |
| --- | --- |
| identify | 文件/hash/声明清单、每块key和定位、DB/UDT计数、可核旧绑定建议/诊断；不分配持久身份、不写库、不改ETag。完整问题与“识别到”明确区分。 |
| preview | 针对冻结源字节、目标PLC、勾选集合、块号/旧目标映射和expectedEtag生成完整树、依赖版本、ID/差异、致命问题、readiness提示、canConfirm及有界token/digest。原 draft/active/历史不写；候选随机ID留在现有单份预览缓存，不能每次confirm重新分配。 |
| confirm | 必须对应同一缓存/token/输入digest/ETag且canConfirm=true；服务重核目标、派生证明、限额和容量。只按缓存计划作目标delta，一次config短事务写新来源/草稿/新ETag；事务失败整份回滚。结果从SQLite权威读回，不仅替换页面对象。 |

文件内容/PLC/编号/勾选/旧目标绑定变化或草稿保存、重载/冲突，立即清除UI确认资格；服务端digest包含全部上述输入，缓存缺失/过期/不一致均拒绝，不能仅依靠按钮灰态。选中任一块或其依赖/映射有致命错误，则本次整体不能提交；允许取消问题行重新预览，不能静默跳坏块部分成功。未选块的可定位错误仅作旁注；文件无法安全分界仍阻断。

致命导入问题与草稿可激活性分开：旧草稿已有未分组/停用/待确认、selected旧人工地址需重审等不是强制补齐全项目的理由；它们保持原值并以readiness提示呈现。选中结构/映射完整不等于可激活。取消文件选择/预览/确认、所有拒绝或CAS冲突无新source/DB/point/ETag半份，不清缓存外编辑输入；并发轮询仍不更新编辑ETag。busy/dirty/editing原guard、保存成功/读回失败区分、无桥零写保持。

### R07. 重导差异与已有配置处理

预览按DB及point稳定ID展示新增、类型/顺序/布局依赖变化、注释变化、拟保留人工地址/开关/组、失效确认数量和阻断原因。以旧完整声明语义比对，不将行号/换行/注释变化当布局变化；UI不只给一串“changed”。

| 变化 | 本 r1 的明确处理 |
| --- | --- |
| 新DB/新叶 | 新opaque ID；新叶disabled、groupId=null、address=null。不自动创建组/启用/激活。 |
| 已核同lineage/块key/号且结构相同 | 保留DB/point ID、用户点名、组、开关、地址/理由/确认及原DB长度；原文/注释有变可新source版本，保留旧版本/历史解释。 |
| 新增叶、既有路径类型改变、重排或其UDT布局改变，且无删叶 | 原路径明确匹配则保留point ID/用户配置；新增叶按新叶处理。为保守覆盖padding/stride/后续点依赖，**整个该选中DB的既有地址确认重置为false**，值/人工来源/理由保留并展示；其他DB不失效。不得只重置直接改类型的那一个点。 |
| 移除/改名旧叶、改块名、改既有DB号、来源/路径身份歧义 | selected该行阻断，列出删除/重命名候选及旧引用，旧配置完整保留；本 r1不自动删、模糊匹配、换ID复用、解除分组或级联清历史。取消该行后可导入其他行。 |
| 文件中未出现/未选的既有DB或类型版本 | 全部保留，不推断为删除，不标它们 incomplete，也不重新解析成新来源。 |

结构变化确认不表示地址已确认：原人工地址仍可手工修正/重新确认，辅助推算也不批量覆盖它。已选草稿更新之外的配置原值、active与全部历史保持。对任一保存路径的新增派生字段保护必须同步，不能从普通save绕过来源/完整结构证明或制造跨PLC绑定。

### R08. 标准嵌套布局支持矩阵与独立 oracle gate

只对**整个目标DB完整、明确非优化、引用闭包完整**的结构作辅助推算，使用完整声明顺序而非仅enabled叶。非优化证明必须重核绑定版本原文的header及hash，或消费Rust导入流程产生且普通save不可伪造的派生layout profile；不能只凭complete/flat或前端声明判定。移除flat-only总拒绝，但flat只是结构分类，不把复杂DB伪标flat。拟支持集合：BOOL；BYTE/USINT/CHAR；INT/UINT/WORD；DINT/UDINT/DWORD/REAL；嵌套STRUCT和无环UDT；一维定长数组（元素可上述标量/STRUCT/UDT，展开元素后不再含数组）。保留既有类型解码，不增加新协议类型。

下列算法规则先用独立期望固定，再实现；oracle不能从被测parser/layout或UI preview反向生成：

| 规则面 | 必须证实的行为 |
| --- | --- |
| BOOL/标量 | 连续BOOL从低bit打包并正确跨byte；遇非BOOL结束bit域，8bit用下一byte，16/32bit按标准word边界和实际宽度；不混用优化1500的BOOL/对齐规则。 |
| STRUCT/UDT | 容器起始与尾padding遵循标准非优化word边界；内部递归按声明顺序；容器后字段从含padding的结束位置继续，不能简单把叶宽相加。UDT按其完整布局实例化。 |
| 数组 | 声明下界决定路径，实际元素序从lower到upper，不把下界直接乘成起始offset；证明标量stride、BOOL数组bit打包/跨byte、STRUCT/UDT元素含尾padding的stride以及数组整体边界。 |
| DB末端/预算 | DB尾对齐、总长度、bit/byte/乘法溢出、每点读段、既有配置DB长度和65536字节界同时校核；不足则整体拒绝预览，不截断结果。 |

STRING[n]可继续导入/人工地址/现有解码，但**不纳入本 r1 嵌套辅助偏移**；含STRING、未知/优化/缺定义/循环/不完整/unsupported数组/类型的整个DB不得跳字段后给后续地址。原人工地址和其他DB不变。推算失败返回定位的结构/类型/布局错误，不能只给不明“失败”或返回部分可信地址。

独立依据为 Siemens STEP 7/TIA V20（11/2024）官方文档，2026-10-19只读查阅：

- [结构化类型 padding](https://docs.tia.siemens.cloud/r/en-us/v20/programming-basics/serializing-structures-for-data-exchange/padding-bytes-when-using-structured-data-types)：非优化结构/尾padding；其官方单BYTE与ARRAY[7]BYTE例给出独立对照位置。
- [STRUCT布局](https://docs.tia.siemens.cloud/r/en-us/v20/data-types/struct-data-structure-anonymous-structures/structure-of-a-struct-tag?contentId=ctJX~CZBYT3zIP8aHvSUbA)：声明顺序、bit/byte/word与容器边界。
- [ARRAY布局](https://docs.tia.siemens.cloud/r/en-us/v20/data-types/array/structure-of-an-array-tag)及[BOOL](https://docs.tia.siemens.cloud/r/en-us/v20/data-types/binary-numbers/bool-bit?contentId=ucSz0IzZkeB4DBeTCMGyGw)：用于交叉核对，优化/非优化分别处理。ARRAY英语正文一处word/even描述自相矛盾，不作唯一算法依据。

Development在P0记录采用的标准布局profile、资料版本/段落、oracle每例原声明/人工独立offset/bit/长度及其依据，冻结 `layout-oracle.json` 后才编写新增算法。可用官方明确例、可核的TIA地址表/导出作独立依据；不安装TIA、不连接真实PLC，不能拿现有Python工具或新Rust的结果互相自证。缺某拟支持形态的充分独立依据时停止该形态实现/验收并交PM，不默默降低r1支持矩阵，也不以一次样例通过宣称所有CPU/固件布局兼容。本轮资料核对不是TIA编译、真实PLC或runtime实证。

### R09. 辅助偏移两步确认与人工地址保护

保留 `daa_preview_offsets` / `daa_confirm_offsets` 两步，预览展示每叶旧/建议byte.bit、完整路径、人工保护、计算长度与当前DB长度；注明建议来自标准布局profile和源版本。预览不写配置、ETag或confirmed，候选对象的confirmed值不得冒充持久状态。UI名称改为“预览标准布局偏移”等准确双语，不再写仅平铺。

预览必须绑定目标DB、源/依赖布局摘要及编辑ETag；新增可选expectedEtag/digest供新版UI传入，confirm重核同一计划，缺/过期/源变/DB变拒绝。显式“确认非人工偏移”可一次保存并确认该预览的全部非人工地址；不要求额外逐叶第三次点击。手工地址不得被纳入批量覆盖，即使未确认亦受保护；恶意请求带人工pointId、重复ID、跨DB ID均整次拒绝，不部分保存。

理论布局游标从完整结构计算，不以人工地址重新定位后续字段。与理论布局冲突的人工地址保留原值/来源/理由并可见诊断；后续采集准入仍校验长度、重叠/位范围。只有全部地址均属本次可确认的非人工完整集合时才可按原合同更新DB长度；存在人工地址/不完整选择时保留旧配置长度，计算长度仅显示建议，不自动缩小破坏人工范围。所有确认只写草稿，不改变组/开关、不激活或采集。

### R10. 受控样例、最小增量验证与原生观察

公开样例为§6新目录内手写脱敏文本：一个小文件包含6个DB、一个文件含3个UDT，覆盖NON_RETAIN、字段S7_SetPoint、共享UDT、多块选择；名字/内容使用通用新示例，不复制真实源。另有小型layout输入覆盖R08矩阵，`expected.json`及先行 `layout-oracle.json`独立给出识别/树/路径/默认状态和地址期望。必要负例以内联测试小文本生成，不复制真实数据/旧fixture。README pair说明来源、数字号均为合成测试值、oracle引用和边界，`.gitignore`只精确放行两个新文本DB路径。

可对原Owner文件在原hash匹配且本机仍可用时追加一次只读内存识别/解析预览，核6DB/3UDT、已知语法无致命问题，数字号用明确的合成编号，不宣称真实号/现场地址。不将原文写入公开产物、日志或真实profile，不新造可连接端点。缺私有文件不以它作为唯一公共交付gate，必须以公开同语法小样例证明；hash漂移先报告，不能静默采用不同现场资料。

增量证据至少包括：

1. parser识别/实际支持语法、完整树与受限拒绝，UTF8/BOM/CRLF原文hash，以及两文件多块/依赖/部分选择；文件级破坏拒绝与单块问题可取消的区别。
2. 真实 LocalEngine/Stores 路径的identify/preview/取消零写、全选/子集提交、坏selected整次拒绝、CAS/过期token/篡改映射拒绝、新source与草稿单事务回滚、reload稳定、无变化重导ID/ETag保持、来源同名多版本与共享UDT隔离；两个PLC以不同显示filename导入相同字节成功，逻辑绑定独立且复用归档原行不变。
3. 自有tmp v1原配置及历史种子的before/after：相同结构保全、增叶/类型/顺序变更整DB确认失效、删叶/改名/改号阻断、未选DB/其他PLC/旧source/receipt/active/context/sample/delivery原值保持，公共save不能伪造binding。种子只在既有cfg(test)能力，不新增产品SQL/ACK后门。
4. R08全部拟支持形态的独立oracle逐叶offset/bit/总长、边界/unsupported整DB拒绝、人工保护与显式确认/CAS。原平铺golden、现有source-proof函数仅在受影响处定向回归；不重跑整个local_store/B矩阵。
5. 现有工具链前端构建、双语键/占位符/可见状态、准确动态诊断及关键交互。用现有能力作UI/owner定向检查，不安装测试框架、长期mock API或假native桥。

取得**一次最小普通原生确认**：新建自有绝对tmp env/profile，两个迁入来源指向自有空文件、read=false、不编Snap7/local-validation；在当前普通 `pnpm tauri dev` 的真实页面选择公开小样例→自动出现多DB清单→填合成号/取消一行→预览及一次取消确认→重新预览确认→重载核只有所选DB→对一个受支持嵌套DB预览并确认非人工偏移→重载核结果。对重复编号先提示再纠正即可同轮完成，不要求再次整套重做。后台只读同库记录与实际操作观察配对；自动工具不可绑定时允许一次Owner实际操作确认，不用browser/fixture冒充native。最后正常退出一次并释放自有进程；无需反复重开、重采旧76样本或DS。端口冲突仅用自己的tmp Tauri port/devUrl覆盖，不改产品15191、不停他人窗口。

记录真实argv/cwd/env/退出码/raw、before/after/ID/ETag/SHA和必要观察限制，失败输出保留。检查通过后只因新变更/失败/实质疑点重跑受影响部分；QA可独立核用冻结raw/源码证据并选取必要定向执行，不重复整套测试。必需证据缺失如实blocked，不降格为通过。

### R11. 文档、诊断与串行交接

DAA及app/local_store README pair准确说明新流程、保守重导规则、布局支持/拒绝、人工保护和无DDL/旧binary风险；不声称全TIA或现场兼容。所有新增按钮/表头/计数/状态/诊断进中英文i18n，复用CU/Element Plus/既有Console组件，不做整体页面重设计或不可用按钮。CODE_INDEX仅同步本次真实局部模块拆分/职责/公开样例。

导入拒绝/提交、偏移确认复用原有界JSONL/stdout，稳定event/process/resource/result/error_code；安全元数据可含DB/点opaque ID、版本hash、数量/耗时，不输出源全文/真实地址/凭据。识别和普通轮询不制造逐点日志；日志故障仍按原准入锁存。

Development在tasks记录R↔AC、批准SHA、实际实施顺序、完整自身增量diff（含新文件全文）、所有限制/非零/资源后developer_handoff；coordinator随后真实调用新的fresh-context Verification（工具支持时fork_turns="none"），只验证写checklist。QA失败回Development；实质范围变化回PM新Revision。qa_passed只进入Human Owner最终验收，不代表旧任务终验、部署或现场切换。

## 4. 决策与排除项

本 r1 选择标准非优化结构的有限支持，不建立通用PLC语言/全CPU布局引擎。包含多DB识别/逐块号、所提供语法的有界兼容、显式依赖版本/保全式草稿导入、nested辅助布局和必要交互；不把来源文件计数当成完整编译证明。

明确排除：既有DB改号/块或旧叶重命名/删叶自动迁移、任意相似名映射、优化DB/符号访问、STRING辅助偏移、多维/动态/展开后嵌套数组、全TIA编译/程序执行、XLSX集成、PLC写入/读取实机、真实profile配置迁入/切换、生产数据库/API、阶段C/上传/ACK/批次/补传、Backend/SMA/DS/CA/CU/tools/contracts实现、后台托管、依赖/锁文件升级、新DDL/schema维护、跨平台签名/性能长稳/Docker/Git提交推送/refs/发布部署。旧保留天数/容量/历史浏览/采集循环不借题重构。

## 5. 实施顺序与停止条件

| 阶段 | 必须先完成的内容 | 证据 / 下一 gate |
| --- | --- | --- |
| G0 | Human Owner于2026-10-19明确批准精确DAA-005 r1；已满足。 | 下一步由coordinator启动实际Development先执行P0；本轮PM不启动角色。 |
| P0 | 固定before/保护面/批准SHA；完整模型向后解码与旧原文不写回方案；冻结独立布局profile/oracle/引用。 | 无DDL/新依赖/未知来源；oracle不足或allowlist不够先返PM，不先猜算法。 |
| P1 | 有界扫描/逐块诊断、真实语法、严格UTF8与源原文/hash，独立结构期望。 | R02–R04；未运行实机。 |
| P2 | block映射、版本/UDT闭包、delta预览/严格selected准入、CAS/事务及保守重导保护。 | R01/R03/R05–R07；数据库只在自有tmp做DML。 |
| P3 | 依据oracle实现nested布局、完整拒绝、两步确认和人工保护。 | R08–R09；不存在未知字段后的部分地址。 |
| P4 | 在原区域接UI与双语/文档、必要构建/定向测试、一次普通native及同库对账，形成精确handoff。 | R10–R11；不重跑B/C/DS矩阵。 |
| G1 | 新fresh-context Verification审查精确handoff并给verdict。 | 失败保留原记录，返工后新handoff/新fresh QA。 |
| G2 | qa_passed后Human Owner决定最终验收。 | 不继承任何旧批准/终验，不授权真实设备/发布。 |

任一实现需要新表/列/版本、修改旧immutable编码、重写真实库/私有receipt、静默改变未选DB、放宽不支持布局、增加依赖或越出§6路径时，停止该部分并回PM；不得将它当例行修复自行扩张。布局matrix必需项缺oracle是必要gate未满足，不以标注deferred后宣称完整r1通过。

## 6. 封闭 allowlist 与角色权威

下表仅为**精确r1批准后**Development的允许实现面。除“仓根”外相对 `automation-world/data-acquisition-agent/`。M=既有有限修改，N=新增且若已存在先核归属；M不授权删/移，N按需要使用，零删除。不得用无限glob扩大工程。

| 操作 | 精确路径 | 唯一用途 |
| --- | --- | --- |
| M | `src-tauri/src/domain/local_configuration.rs` | 可选lineage/binding、兼容旧decode、派生字段/范围/引用校验；不改样本schema。 |
| M | `src-tauri/src/domain/mod.rs` | 仅新source_import类型模块注册。 |
| N | `src-tauri/src/domain/source_import.rs` | 有界识别/映射/预览与binding DTO，纯domain，不放SQL/文件I/O。 |
| M | `src-tauri/src/infrastructure/tia_source.rs` | 有界解析/来源版本与所选delta入口；按职责拆分，不扩全TIA。 |
| N | `src-tauri/src/infrastructure/tia_source/parser.rs` | 从现parser拆出扫描/lex/受限语法和逐块定位。 |
| N | `src-tauri/src/infrastructure/tia_source/reconcile.rs` | 显式版本闭包/稳定身份/保全式diff，避免入口膨胀。 |
| N | `src-tauri/src/infrastructure/tia_source/tests.rs` | 该解析/映射纯函数定向测试。 |
| M | `src-tauri/src/infrastructure/plc_layout.rs` | R08–R09完整标准布局/建议/显式确认与定位错误。 |
| N | `src-tauri/src/infrastructure/plc_layout/tests.rs` | 独立oracle及边界/人工保护定向测试。 |
| M | `src-tauri/src/services/local_configuration.rs` | identify/preview/confirm准入、digest/CAS、protect_derived和两步offset。 |
| M | `src-tauri/src/services/local_supervisor.rs` | 仅新增有界预览计划/cache类型接线，不改actor/调度/恢复。 |
| M | `src-tauri/src/commands/local_acquisition.rs` | 原具名IPC可选字段/稳定拒绝码，不加任意执行入口。 |
| M | `src-tauri/src/infrastructure/local_store/configuration.rs` | 仅原表DML/不可变来源一致性/所选delta同事务及兼容读取，不改激活/裁剪策略。 |
| M | `src-tauri/src/infrastructure/local_store/mod.rs` | 仅cfg(test)新测试模块注册，不改连接/PRAGMA/队列。 |
| M | `src-tauri/src/infrastructure/local_store/tests.rs` | 既有受影响构造器/定向source-proof、flat golden；不重写旧全套矩阵。 |
| N | `src-tauri/src/infrastructure/local_store/source_import_tests.rs` | 真实engine/store新导入、事务/CAS/保全、旧JSON及seed历史测试。 |
| M | `src-tauri/src/infrastructure/yaml_migration.rs` | **仅SourceDocument/Db构造器给新增可选字段默认值**，迁入算法/receipt不变。 |
| M | `src/services/localAcquisition.ts` | 对称DTO/原具名IPC，不增加browser假桥或HTTP。 |
| M | `src/console/composables/useLocalAcquisitionConsole.ts` | 唯一owner的严格读文件/识别、逐块映射、预览失效和确认接线；旧刷新/编辑/历史保护不改。 |
| M | `src/app/plc/views/points/index.vue` | 现区域多DB清单/预览/offset交互与guard，不新增路由。 |
| N | `src/app/plc/components/SourceImportPanel.vue` | 可按需拆出的本模块私有导入表/折叠预览，复用CU，状态仍归唯一owner。 |
| M | `src/styles/app.css` | 仅本导入区域表格/窄窗的局部类，不改全局CU视觉或其他页。 |
| M | `src/locales/zh-CN/common.json` | 本次可见导入/布局/诊断中文键。 |
| M | `src/locales/en-US/common.json` | 对称英文键/占位符。 |
| M | `src/app/plc/locales/zh-CN.json` | 仅既有PLC模块导入/布局说明的准确语义。 |
| M | `src/app/plc/locales/en-US.json` | 对称英文。 |
| M | `README.md` | 稳定流程/支持矩阵/保守重导/数据保护/风险说明。 |
| M | `README.zh-CN.md` | 对称中文。 |
| M | `src/app/README.md` | 单owner/同区域流程/预览无写说明。 |
| M | `src/app/README.zh-CN.md` | 对称中文。 |
| M | `src-tauri/src/infrastructure/local_store/README.md` | 可选JSON兼容与来源版本，保留v1及旧binary边界。 |
| M | `src-tauri/src/infrastructure/local_store/README.zh-CN.md` | 对称中文。 |
| N | `src-tauri/tests/fixtures/source-import-multi-db/multi.db` | 手写6块的小型公开语法/选择fixture。 |
| N | `src-tauri/tests/fixtures/source-import-multi-db/types.udt` | 手写3类型/共享依赖fixture。 |
| N | `src-tauri/tests/fixtures/source-import-multi-db/layout.db` | 小型嵌套/数组布局输入，不含真实源。 |
| N | `src-tauri/tests/fixtures/source-import-multi-db/expected.json` | 人工独立的结构/默认状态/映射期望。 |
| N | `src-tauri/tests/fixtures/source-import-multi-db/layout-oracle.json` | P0先行的官方依据/独立逐叶offset/bit/长度表。 |
| N | `src-tauri/tests/fixtures/source-import-multi-db/README.md` | 归DAA PLAN的结构性fixture说明/合成编号/引用。 |
| N | `src-tauri/tests/fixtures/source-import-multi-db/README.zh-CN.md` | 对称中文，不建fixture PLAN。 |
| M | 仓根 `.gitignore` | 仅精确新增上述multi.db与layout.db两路径negation，不放开真实/SQLite/旧DB。 |
| M | 仓根 `CODE_INDEX.md` | 仅真实触达DAA职责/新模块/公开fixture条目。 |

| 角色 / gate | 仓根相对唯一权威路径 |
| --- | --- |
| PM / Human Owner | `automation-world/data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md`；当前仅本文件。 |
| Development，批准后才N | `automation-world/data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/tasks.md`。 |
| 新fresh-context Verification，handoff后才N | `automation-world/data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/checklist.md`。 |

coordinator `/root` 独占以下10个既有索引的本任务机械行/指针同步，PM/Development/Verification不写：仓根 `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`；`automation-world/PLAN.md`、`automation-world/PLAN.zh-CN.md`；`automation-world/data-acquisition-agent/PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`。只链接已存在角色文档，不预造后续证据。

其余路径均保护，尤其root AGENTS/角色/workflow/skills、旧bundle/设计、真实两源/旧fixture/原golden、receipt迁入adapter/SQL、schema.rs/runtime ledger/context/sample编码、activation/recovery/scheduler/managed_s7/driver/门禁、App/shell/其他页面、依赖/锁/Tauri配置/capabilities、env/YAML/profile及CU/CA/SMA/DS/backend/frontend-js/tools/contracts。新fixture不与真实输入共用目录。辅助报告/构建产物放获批角色自有系统tmp，不进入源码或他人资源。

## 7. 验收标准

下表是批准后的义务，当前均未实施/未验证；PM自检不能填成pass。

| AC | 可核完成条件 | 必要证据 / 对应需求 |
| --- | --- | --- |
| AC01 | 独立身份、精确批准、P0与串行角色链、有限allowlist成立；旧任务/现场权限不升格。 | 批准SHA、实际before/完整新增全文/diff/保护hash、R01/§5–6与角色handoff。 |
| AC02 | 选择后自动列每DB、计数/UDT摘要、逐块号与分页勾选稳定；无额外页面/识别按钮，cancel不清旧输入。 | 当前页面/owner/真实识别响应与UI定向检查，至少6DB/3TYPE示例；R02。 |
| AC03 | 编号整数范围及(PLC,number)唯一，跨PLC同号可用；无号不猜，同名/来源/映射歧义/改号阻断。 | 单DB旧JSON内存兼容、两个PLC/同号、重复/陌生占用/伪造target/改号/无号反例；R03。 |
| AC04 | 白名单真实语法、UTF8/BOM/CRLF、完整树/原文hash准确，初始化不当值；未知语法/依赖/资源限额定位拒绝。 | 公开手写源与独立结构表、非UTF8/截断/单块错误/文件级错误/循环/数组界负例；Owner原文件附加检查如有单列；R04/R10。 |
| AC05 | 新来源版本和逐DB依赖闭包保存；旧同名版本共存不全局冲突，不换未选DB的来源/UDT/树。 | source raw/hash/ID/lineage/Db binding闭环、共享UDT只更新所选、其余逐值不变；两个PLC/不同filename/同字节成功且物理归档原行不变；sources/16MiB准入；R05。 |
| AC06 | identify/preview不写，输入/ETag/token失效有效；selected任一致命问题整次拒绝，合法子集单事务提交/取消/失败无半份。 | 真实LocalEngine/Stores前后对账与一次事务中途失败回滚，CAS/缓存/篡改/重载；readiness不强制修未选对象；R06。 |
| AC07 | 相同结构保全ID/用户名/组/开关/人工地址；无变化重导无新ETag。新增/类型/顺序依赖变化整目标DB确认失效。 | delta逐项核对；未选/其他PLC不失效；地址值/理由保留；R07。 |
| AC08 | **删叶/叶或块改名/已有DB改号本r1明确阻断**，不执行隐式删除、错绑或覆盖旧配置。 | 有分组/人工地址旧对象的原值与失败/取消后ETag不变，预览阻断原因可见；R03/R07。 |
| AC09 | R08矩阵有先行独立oracle且逐叶byte/bit/stride/长度吻合；unsupported/越界整个DB拒绝无部分可信地址。 | 官方profile/引用/手写oracle时序，BOOL跨byte、UDT/STRUCT边界、数组负下界/元素stride/尾padding、长度和溢出负例；无oracle项不能称完整通过；R08。 |
| AC10 | offset预览无持久确认，显式一次确认保存非人工集合；人工地址/跨DB/CAS保护、DB长度条件有效。 | preview/confirm/reload真实路径，人工冲突保原值/理由、伪造IDs整次拒绝、无自动启用/激活；R09。 |
| AC11 | 新版读旧v1无DDL/自动写回，旧receipt/active/context/sample/manifest/pending原值不变，普通save不能伪造binding。 | 自有tmp旧JSON+历史种子逐表/原字节与hash before/after、schema/user_version/依赖锁hash；同字节逻辑来源可复用归档，真正同id异content或hash/content冲突仍拒绝；派生字段负例；R01/R05–R07。 |
| AC12 | 一次普通native实际文件选择→自动识别→编号/勾选→预览取消/确认→重载→nested偏移两步闭环成立。 | 真实观察与同一自有库ID/ETag/hash对账、read=false/stopped、原生/浏览器限制准确，无反复旧B矩阵；R10。 |
| AC13 | 必要定向测试/前端构建/双语/文档/索引准确，资料/fixture不泄露真实源；完整DEV handoff→新fresh QA→Owner终验分层。 | 实际argv/cwd/exit/raw、oracle/支持限制/locale/链接、双语对读、完整diff、旧证据核用范围与资源清单；R10–R11。 |

## 8. 风险、恢复与延后问题

| 风险 / 取舍 | 处理与停止条件 |
| --- | --- |
| 多块计数被当全部解析成功，或错误块污染合法块 | 逐块diagnostic与文件级分界失败分开；只选合法完整块，严格集合提交，未知字段不跳。 |
| 同名来源/UDT替换伤到未选DB | 不可变版本＋显式闭包；未选原树/source/确认原值对照。无法实现不重写的模型时返PM，不能放宽。 |
| 重导错误复用身份或删除旧点 | 明确source/块/路径证据；删叶/改名/改号/歧义r1阻断，不以更多按钮绕过。 |
| 辅助偏移把容器/数组padding算错 | 先oracle后算法，完整DB拒绝，布局profile局限显著展示；无独立依据停止，不凭工具互相自证。 |
| layout变化仅改一个点确认，后续地址仍旧可信 | 保守使整个选中DB地址确认失效，保留人工值/理由，其他DB不受影响。 |
| 新可选JSON旧binary不识别 | 明确单向decode兼容；旧不可变内容不写回，二进制降级/现场回退另核，不用清库重置解题。 |
| 原文/hash不一致或真实源泄露 | 严格字节/文本定义与服务器复算；真实源只读、私有tmp摘要不含正文，公开手写样例独立。 |
| 来源版本积累或事务写失败 | 版本计入既有限额/写预算，失败整次回滚；不删未选源/历史腾空间，不填宿主盘验证。 |
| native工具不能绑定/被占用 | 同轮Owner实际操作＋同库证据、仅自有端口覆盖；必要证据缺失blocked，不重复全部清单或假桥代证。 |

恢复仅针对本任务自有增量/临时实例，在保留原始before、diff和证据后按具体授权处理；不删除用户SQLite/receipt/journal、重置序号、覆盖历史、复制测试profile到正式目录或恢复旧YAML模式。失败保留raw并停止自有操作，正常释放自己创建的进程/句柄，不清未知锁或关他人窗口。任务临时证据/target/profile供fresh QA及Owner审阅，验收后由coordinator核归属/依赖收尾，不将临时路径当唯一永久证据。

以后可另定范围：删点/重命名/DB改号迁移、更多TIA语法/STRING或其他布局profile、真实TIA地址校核、DS/真实S7联调、后端上报与SMA。均不作为本r1隐含实施内容。

## 9. Skill 路由、修订历史与 PM handoff

| 批准后实际表面 | Development / Verification适用skill与责任 |
| --- | --- |
| PLC源/结构/offset/oracle/人工保护 | `plc-point-mapping`；不照搬其通用XLSX/YAML输出或客户点表，DAA仍GUI/SQLite。 |
| Rust解析/domain/service/store/线程与受限IPC | `rust-runtime`，分层/资源/JSONL；必要结构拆分遵循其语言无关工程标准，不把SQL放command/service。 |
| 普通Tauri/本地文件/真实桥/自有tmp原生观察 | `desktop-tauri` + `rust-runtime`；无任意路径/SQL/真实transport新权限。 |
| 点位页/私有组件/选择表/分页与窄窗 | `frontend-ui`适用DESIGN/FRAMEWORK，复用CU；唯一owner不复制状态机/parser。 |
| 可见状态/按钮/错误/限制与双语说明 | `i18n-workflow`；稳定英文key和对称占位符。 |
| 文件头/实际模块与CODE_INDEX | `code-document-indexer`，仅§6真实有限面。 |
| 任务身份/role链/索引、边界规划 | `project-governance` + `aiis`；coordinator决定执行窗口/通知，不由PM起草累计。 |

- 2026-10-19，r1 draft：按当前Human Owner请求建立本spec；只授权起草，不推断范围批准。
- 2026-10-19，r1 owner_approved：Human Owner按§1原话精确批准草案SHA-256 `099c2698b57628d6926c4ae92b4147325a8aef2bd19c558e7f8fc9fcdf07ffe7`；只补批准事实/状态/handoff，不改变R/AC、allowlist、范围或风险。
- Development/tasks/实现/测试/原生观察/developer_handoff：**未发生**。
- 新fresh-context Verification/checklist/verdict：**未发生**。
- Human Owner最终验收：**pending**，旧任务终验仍独立。

PM仅做本spec元数据/身份/引用、R01–R11↔AC01–AC13↔阶段、有限路径/角色分权、保护/支持/拒绝/风险和文档差异自检，不是DEV self-check或独立QA。最终spec SHA由交接消息给出，避免自引用。

正式handoff：**精确 aiis-ics-arch::DAA-005 r1 已获范围批准，无需重问未变化的r1。** 交唯一coordinator `/root` 启动实际Development，消费批准前后SHA、完整已形成bundle与当前before，先执行P0及其oracle/兼容/保护gate，再按原范围实施；精确developer_handoff后启动新的fresh-context Verification，独立qa_passed后交Human Owner最终验收。保守重导阻断、来源版本/旧binary兼容、独立布局oracle gate与必要增量验证均保持。PM本次批准记录/文档自检后停止全部写入，不改索引、后续角色文件或产品，不自行启动角色/通知；机械索引同步和实际角色调用归coordinator。
