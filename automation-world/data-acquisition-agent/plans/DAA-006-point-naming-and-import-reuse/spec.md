Task ID: DAA-006
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner已于2026-10-19精确批准DAA-006 r3；交唯一coordinator /root启动实际Development，依P0a→P0b→原命名/共享执行，之后新fresh-context Verification与Owner最终验收；本轮仅记录批准，尚无Development或产品检查
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: DAA 正式入口与迁入展示收尾、六个配置helper编译警告有限清理、点位 ASCII 技术命名、显式存量转换及供 DS 独立消费的无 I/O DB/UDT 导入核心
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: aiis-ics-arch::DAA-006 r3 exact scope approval -> Development -> new fresh-context QA / Verification -> Human Owner final acceptance
Depends On: aiis-ics-arch::DAA-005 r1 owner_accepted baseline
Related Task: aiis-ics-arch::DAA-001 r1; aiis-ics-arch::DAA-002 r2; aiis-ics-arch::DAA-003 r1; aiis-ics-arch::DAA-004 r1; aiis-ics-arch::ARCH-AW-004 r2; aiis-ics-arch::ARCH-AW-005 r2

# 点位技术命名与 DB/UDT 导入能力复用准备

## 1. 当前效力、Owner 请求与固定决定

**最新批准与当前效力（2026-10-19，Asia/Shanghai）：** Human Owner已明确批准精确 **aiis-ics-arch::DAA-006 r3**，获批草案SHA-256=`b133bbfb2e44a05d5b79764afe6a7bc9988c5332f12e33beaf61a51cffdc825f`。唯一coordinator `/root`真实转交原话，并在 `/private/tmp/daa-006-r3-execution-8knyrx3c/owner-approval.json` 固定：

> 可以，批准 DAA-006 r3，按 spec 先完成迁入展示收尾和 Rust 警告有限清理，再做命名升级与共享导入核心，并完成独立核验。不用 allow(dead_code) 隐藏警告，已有 SQLite 配置和历史不覆盖，只做必要增量验证，不重复整套测试；阶段 C、DS、后端和 SMA 暂不做，真实 PLC、生产数据库/API 和现场切换不在本次范围。

当前Status为`owner_approved`，G0已满足；下一gate是由coordinator启动实际Development。PM本轮仅更新真实批准/状态/handoff；R01–R14、AC01–AC20、61实现路径、风险/排除及P0a→P0b→原P1的实施顺序合同保持原字节。尚未启动Development、创建tasks/checklist或实施/运行产品，不给予QA verdict或Owner最终验收。执行before为 `/private/tmp/daa-006-r3-execution-8knyrx3c/baseline.json`（1698路径，含4个ignored旧fixture的hash保护）；原获批草案全文为该根`approved-r3-draft.md`，不覆盖r1/r2归档，不把范围批准扩为DS/阶段C或现场操作授权。

起草背景（历史）：r3草案于2026-10-19形成。Human Owner最初要求据阶段B/DS/阶段C顺序起草命名与复用spec：

> 也就是阶段B是的还没有完成，阶段B基于DS完成之后和DAA联合调试验证，才能被完成。后续才是阶段C。这个方向对的话，请直接开始做spec吧。

Owner随后指出正式页面仍有“旧YAML迁入时记录”，要求先完成正式入口/展示整合，再推进命名升级。当前源码和DAA-004 r1明确允许折叠历史，005已接受实现也已在本仓源码；这是新的展示要求，不将旧合同重写为漏合并/实施失败。r1未获范围批准，完整52936字节归档在 `/private/tmp/daa-006-r2-spec-wxtwzx9l/r1-spec-before.md`，SHA-256=`b7a67690ecc9badb4d025bfe2579eecafd2d2d9a2182d7fb1da0f4f731afb197`；r2保留原R01–R12/AC01–AC16的命名/共享范围，新增R13/AC17–AC18并调整执行先后。

本轮Owner另明确要求：把刚才4组Rust编译警告的**有限清理**补入同一任务，放在命名升级前，不用`allow(dead_code)`隐藏警告；已有SQLite配置/历史不动，只做必要增量验证，批准后才改代码。r2也未获批准，其完整全文归档 `/private/tmp/daa-006-r3-spec-83zdc53u/r2-spec-before.md`，SHA-256=`ebbf43dfff9e1a85565737f91b57ca97a72870b28669ae55d7387a44c46c67d6`。r3仅新增R14/AC19–AC20与一个实现路径，顺序为P0a展示→P0b警告→原P1命名/共享准备；不把既有warning描述为运行失败，不扩成旧模块清扫。

Owner 将自行到 DS 会话 `codex://threads/01a14e52-eeb4-7c82-bade-bc0a237fa2ff` 接续。上述起草时授权仅包含修订草案，当时不构成展示/警告/命名/共享实施批准；当前精确r3已按本节真实决定获批，DS G0仍不在此范围。唯一 active lifecycle coordinator 为 `/root`；本实际 PM 只写此 spec，不写 tasks/checklist、实现、测试、配置、设计正文、索引，不向 DS 会话发送消息，不启动 Development / Verification。

以下固定方案已随精确r3获批，方案正文保持：

1. 先P0a核当前正式dev入口/源码版本并撤下正常态全部迁入历史展示及入口（包括既有运行配置details内）；仅unknown或仍可安全重试的当前失败保留紧凑提示和按需小Dialog。保留SQLite防重receipt、机制、owner/IPC与重试门禁，不复制未知tmp实现或重做005。随后P0b只按R14处置config/mod.rs的六symbol/四组warning，再开始原命名/共享范围。
2. 使用现有 `Point.name` 承载 ASCII 技术名；`Point.id` 继续是机器身份，`sourcePath` 保留原始路径及中文。没有 alias/code/第二套可读 key，不引入翻译、拼音、Python 或 YAML 运行模式。
3. 按旧 point-mapping 工具的路径优先、地址兜底风格生成；新导入地址仍为 null。依赖地址的点先保存为停用、技术名待生成，再随既有地址确认完成生成。
4. 旧名称默认原样保留；只有明确选中的转换或手工改名，经旧名/新名/冲突预览及确认后才改变。选择、冲突与自动状态转移由 Rust 权威判断，普通 save 不能去掉元数据伪装成 legacy。
5. 提取一个 **std-only、无 I/O 的本地 Rust 小 crate**，物理路径 `automation-world/shared/tia-import-core/`；DAA 实际改为消费它。解析、展开、纯标准布局及命名只保留一套算法；DAA 的来源证明、不可变闭包、重导保全、SQLite/CAS/激活门禁仍归 DAA。
6. 本任务通过仍不关闭阶段 B。阶段 B 还需一个独立获批并验收、满足本次联调所需能力的 DS 基线，以及后续另行批准的 DAA↔DS 真实 S7 读取到 SQLite 联调、fresh QA 与 Owner 验收；之后再推进阶段 C 可靠上报。

PM TOML 的 `gpt-6.1-sol / max` 为配置证据；profile 为 `contract_only`。主会话、精确 bundle 与 diff 审计是合同控制，不宣称平台 ACL、强制路由或团队激活。

## 2. 消费依据与当前事实

已读[根契约](../../../../AGENTS.md)、根 README/PLAN 双语、[canonical workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)、实际 `.codex/agents/pm.toml`、AW/DAA 最近 README/PLAN/catalog、DAA app/local_store README 双语、完整 [DAA-005 spec](../DAA-005-multi-db-source-import-and-nested-offsets/spec.md)/[tasks](../DAA-005-multi-db-source-import-and-nested-offsets/tasks.md)/[checklist](../DAA-005-multi-db-source-import-and-nested-offsets/checklist.md)。r2修订时已完整读取r1、[DAA-004 spec](../DAA-004-migration-notice-and-source-import-validation/spec.md)/[tasks](../DAA-004-migration-notice-and-source-import-validation/tasks.md)/[checklist](../DAA-004-migration-notice-and-source-import-validation/checklist.md)、两迁入组件、唯一owner及启动/日志源码；本次r3核当前r2与归档SHA一致，再读config/mod.rs全文、Cargo features、lib/main/两个bin入口、模块注册及全部Rust引用。作用域无更近 AGENTS；r1起草前确认本ID/目录未占用，后续仍在同一唯一spec修订。应用 `aiis`（BLUEPRINT/CONTRACTS）、`project-governance`、`plc-point-mapping`；技术实现按 §11 handoff，不由 PM 执行。

| 2026-10-19 只读事实 | 来源、限度及本任务处理 |
| --- | --- |
| 当前正常态历史的出处 | [ConfigRevisionBar.vue](../../src/components/console/ConfigRevisionBar.vue)在既有details挂载[YamlMigrationNotice.vue](../../src/components/console/YamlMigrationNotice.vue)，后者在有摘要时显示标题/来源/计数/attempt。DAA-004 R03/AC03明确采用这个折叠历史方案；README pair已含默认示例。本r2改变日常展示，不修改004/005原事实。 |
| 正式dev源码绑定 | [package.json](../../package.json)普通`pnpm tauri dev`→[tauri.conf.json](../../src-tauri/tauri.conf.json)的`pnpm dev`/devUrl15191→[vite.config.ts](../../vite.config.ts)、[index.html](../../index.html)的`/src/main.ts`→本仓App；原生由本仓`src-tauri/src/main.rs`/lib运行。dev不从tmp或静态dist挑一份“待接受后覆盖”的实现；验收状态本身没有自动合并机制。打包frontendDist另属构建，不据dev日志证明旧安装包已更新。 |
| 005实现已在本仓 | coordinator只读报告 `/private/tmp/daa-006-r2-spec-wxtwzx9l/daa005-source-presence.json`：按005最终implementation-manifest的41个afterSha逐一核当前正式源码，全41匹配、无差异；PM已读报告。当前HEAD=`0af5b91177f3bca63f9f3c2bef9f14004ea49944`，唯一worktree为本仓main。不是等待从tmp复制/无条件merge的005实现；后续按本任务精确增量处理。 |
| Owner提供的普通dev日志 | Owner报告`cargo run --no-default-features`、4组dead_code警告、`yaml_migration_skipped`伴随`imported_with_diagnostics`/persisted、`runtime_started`结果stopped及`runtime_stopped`结果clean。该日志是Owner提供的观察，PM未启动程序、独立重放或核真实profile。 |
| 日志的源码解释 | [local_yaml_migration::startup](../../src-tauri/src/services/local_yaml_migration.rs)在已有state.status非not_attempted时直接记录skipped并return，不再次discover；result可保留先前imported_with_diagnostics，persisted是持久化状态，均不证明本次重迁。[LocalEngine](../../src-tauri/src/services/local_supervisor.rs)以stopped记录启动意图、以clean记录正常shutdown；Owner所报warning不是运行失败/漏合并证据。r2未授权清理helper；本r3只新增R14六symbol例外，日志事件/level及其他代码继续保留。 |
| 四组warning的当前引用范围 | [config/mod.rs](../../src-tauri/src/config/mod.rs)定义三项AgentConfig方法及三个free helper；[services/mod.rs](../../src-tauri/src/services/mod.rs)/[infrastructure/mod.rs](../../src-tauri/src/infrastructure/mod.rs)未注册旧plc_collection/plc_diagnostics/runtime_snapshot/authorization_gate/plc_points/plc_snapshot_policy/logging。五symbol的外部引用仅在这些退役源；resolve_output_path另有本文件有效isolation_test。见R14逐项处置。 |
| 所有入口和features的只读边界 | 默认lib/main、退役runtime bin和feature-gated daa-local-validation bin均走当前lib模块图；[Cargo.toml](../../src-tauri/Cargo.toml)的default为空，rust-snap7-driver只启用驱动依赖，local-validation启用debug fixture，单独或组合均不注册上述旧模块。profile_dir仍被local_bootstrap调用，不能删除。PM仅核源码/引用，没有Cargo编译或运行证据。 |
| 新点目前 `name=path`、`address=None`，重导保留已有 name | [reconcile.rs](../../src-tauri/src/infrastructure/tia_source/reconcile.rs)；[Point](../../src-tauri/src/domain/local_configuration.rs) 的 name 只有既有 100 UTF-8 字节上限，尚无 ASCII 约束/名称 namespace。本草案是新合同，不能写成已实现。 |
| 身份与显示字段分开 | point.id 是 opaque UUID，样本字典按 ID；sourcePath 是原完整路径。当前 name 可编辑；本任务只调整其技术名语义，不替换 ID 或重绑样本。 |
| 实际 UI 路径与 owner | [plc/views/points/index.vue](../../src/app/plc/views/points/index.vue)、[SourceImportPanel.vue](../../src/app/plc/components/SourceImportPanel.vue)；唯一 [useLocalAcquisitionConsole](../../src/console/composables/useLocalAcquisitionConsole.ts)。不是旧 collection/views/points 路径。 |
| 当前支持的类型 | `width()`：BOOL/BYTE/USINT/CHAR/INT/UINT/WORD/DINT/UDINT/DWORD/REAL/STRING[1..254]；命名不改变采集 dataType、宽度或解码。 |
| 解析/布局尚为 DAA 私有 | [parser.rs](../../src-tauri/src/infrastructure/tia_source/parser.rs)、reconcile、[plc_layout.rs](../../src-tauri/src/infrastructure/plc_layout.rs) 依赖私有 Configuration/SourceDocument/FieldNode；没有已发布公共 crate，不能称为 DS 现成 SDK。 |
| 已验收的 DAA-005 | checklist `8915876b210aa4dc5ff270b9d91a11630f0941884e2e56060dee05112f04290e`；spec `6b0ea0b3a2d62bc5907a8a4263b70850f4d7a495f06027b6f0c291250d13fbbe`；tasks `d04e9a28d4d82396b0ec0d7fb4ce93a996bf9b7573549994b05d7f3bc55a77df`。QA2 与 Owner acceptance 保留，不重开/降级。 |
| 布局依据不变 | 原 [layout-oracle.json](../../src-tauri/tests/fixtures/source-import-multi-db/layout-oracle.json) SHA `2f2f6fe79eea60b48357b72f8a4f352016da4c8d95220ba2e06005133c24e633`，4 例/65 叶、明确标准非优化 profile；本任务不重算或修订该 oracle。 |
| 旧命名参考 | canonical 为本仓 [converter.py](../../../../tools/plc/point-mapping/src-python/converter/converter.py) 的 `_new_point_name/_address_name/_resolve_global_name_collisions` 及 [test_generate_yaml_naming.py](../../../../tools/plc/point-mapping/tests/test_generate_yaml_naming.py)，均已只读核对。只复用命名规则和最终碰撞拒绝策略，不复用工具跳过未知类型等行为，不读客户点表或运行工具。DAA 有多 PLC/null 地址，不能原样搬其全列表覆盖行为。 |
| DS 旧快照与当前 G0 | [DS 设计 §2](../../../../docs/AIIS_DS_Detailed_Design.md#reuse) 固定于 2026-10-18，flat-only/DAA-002 当时状态已落后当前 005；不修改其历史正文。当前 [ARCH-AW-005 r2](../../../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md) 为 draft，等待该会话的执行范围批准；本 spec 不代批。 |

DAA-001 r1、DAA-005 r1 已 `owner_accepted`；DAA-002 r2、DAA-003 r1、DAA-004 r1 各自 `qa_passed`、Owner 最终验收 pending。它们的状态不由本请求、005 的接受或阶段汇总倒推改变。本任务独立分类，无 Parent Task ID，不继承批准或终验。

文件角色固定：DB/UDT 是显式结构输入；SQLite 是 DAA 配置/历史权威；共享 fixture/manifest JSON 是期望及版本清单；不新增 XLSX/YAML 入口。`:=`/`BEGIN` 仍跳过，不导入初值、不执行表达式；DS 自行定义初值、服务端编码、变化规则、权限和内存。

## 3. 编号需求

### R01. 精确范围、保护面与数据兼容

精确 r3 获 Owner 批准后才由实际 Development 创建 tasks、固定批准 SHA/当前 before/受保护文件，按§6先R13展示收尾、再R14有限警告清理，之后实施原命名/共享范围。保留并发变化、旧失败/原生证据，不以 HEAD 代替实际 before。范围、风险、AC、allowlist 有实质变化返回 PM 新 Revision。

不修改已有 immutable source、revision/context/sample/manifest 原字节、point/source identity/generation/sequence、pending/delivery/reference、active/previous 或私有 YAML receipt；不重新导入全库、不删点换 ID、不使读取旧 JSON 自动写回。仅显式目标草稿 delta 写既有 config 事务；active 仍按原版本运行。双库 v1、DELETE/EXTRA、profile 锁、唯一 owner/1Hz 刷新、原 actor/driver/read gate、容量/日志故障规则保持。

限额保持：4 PLC、每 PLC 32 DB/4096 叶/8 组、每组 256 启用点、周期≥500ms；单源1MiB/单次4MiB、展开≤8层、一维数组≤1024元素、sources≤128、配置16MiB及原写预算。当前任务验证只用自有 tmp env/profile 和公开手写输入，不使用真实/default/旧76样本 profile、现场 DB/UDT、真实 `.env` 或数据库。

### R02. 确定的命名语法与类型后缀

命名 profile 固定为 `tia-point-name-v1`。合法源路径的**每个原始字段段**满足 `^[A-Za-z0-9_]+$`，保留大小写；数组下标是独立 Index 段，含 Index 的路径不走语义名。必须来自解析器的结构化段，不能把有引号字段内的点号错误拆成层级、删 `[]` 或用字符串清洗伪造合法段。

路径名为 `DB{number}_{字段段用下划线连接}_{suffix}`。完整名只含 ASCII，长度1–100字节；100可用、101及以上整名转地址兜底，不截断。字段段可数字开头，完整名已有 DB 前缀。DB号使用已明确的1–65535，不能从 PLC 显示名/IP/源文件名猜号。

| 原 dataType | 固定 suffix | 原 dataType | 固定 suffix |
| --- | --- | --- | --- |
| BOOL | Bool | BYTE | Byte |
| USINT | USInt | CHAR | Char |
| INT | Int | UINT | UInt |
| WORD | Word | DINT | DInt |
| UDINT | UDInt | DWORD | DWord |
| REAL | Real | STRING[n]，1≤n≤254 | String |

未知/不支持类型明确拒绝，不生成 Unknown 或改变类型。非法段、超长、语义 flatten 碰撞走地址：非 BOOL `DB{number}_B{byte}_{suffix}`；BOOL `DB{number}_B{byte}_{bit}_Bool`，bit必为0–7。旧点缺少可重证的结构化路径时只能走地址，不拆sourcePath猜层级；没有可用确认地址则pending，存量转换不得确认。仅消费已通过既有地址确认及边界规则的地址；offset0不是无地址的默认替代。不得用翻译/拼音/删字/行号/随机ID后缀兜底。此名是 PLC 技术标识，不是 SMA/业务字段名称。

### R03. namespace、碰撞集合与确定顺序

唯一性为 **同 PLC 的全部点，包括停用、跨 DB/组、legacy/manual/auto 点**；跨 PLC 可以同技术名，依靠 plcId/point.id 消歧。比较为大小写敏感的完整 ASCII 字节；源声明重复/歧义仍沿 parser 的原大小写规则拒绝，不能靠命名修复源错误。

每次操作先冻结当前 PLC 全点清单。可改名集合仅为本次新点、显式选中转换/手工编辑的点，或本次已获确认的地址/类型变更直接影响的已管理点；其他点是不可改的名称保留项。稳定排序为 DB号、结构化路径段、point.id（只用于对应/排序，绝不进入生成名）。结果不能取决于表格页码、输入文件顺序、HashMap 顺序或遍历时抢占名字。

固定批处理规则：

1. 对同 PLC 所有能重证结构化路径的点计算合法、≤100字节的路径 primary。**不同路径 flatten 为同 primary 的整个集合**标记为必须地址兜底；既存点不因此自动改名，但本次可改名成员不能抢到 primary。这也使先后确认地址、重开和重导不丢失碰撞原因。
2. 为可改名集合计算 path 或 address 候选；地址未确认者给 pending。与不可改名称保留项或本次其他候选同名时，尚用 path 的可改名成员同时改用地址；已用 address 者不换格式。只执行这一次 fallback，不连环改写别的旧点。
3. 最终非空候选对保留项/彼此仍冲突，整次提交拒绝，显示冲突 point.id/原路径/名称；不选赢家、不覆盖、不加盐。尚缺地址是 pending，不冒称已有可用最终名。显式存量转换的任一 selected 仍 pending 时不得确认。

既存 legacy 的历史重复名/非ASCII不在读取或无关保存/原激活时追溯判错；但它们仍保留自己的实际字符串，新的 managed/manual 名不能与其相撞。不能为“全点唯一”偷偷重命名旧点或让旧库全部激活失败。

### R04. 最小持久状态与无地址流程

只新增一个可选 JSON 字段 `Point.nameMode`，Rust 使用 Option/serde(default, skip_serializing_if=Option::is_none)，不加 DDL/列/表/版本：

| 存储状态 | name 内容与含义 | 允许来源 |
| --- | --- | --- |
| 字段缺失（None） | 原 name 原样；UI“旧名称/待显式转换” | 旧JSON、既有一次性YAML候选；不是供客户端选择的降级模式 |
| pending | 空字符串；UI“待地址确认生成技术名”并始终展示sourcePath | 新导入需地址兜底，或既有 managed 地址名因本次定义变更失去确认 |
| auto_path | R02/R03生成的最终ASCII路径名 | Rust受控导入/转换/直接相关定义更新 |
| auto_address | R02/R03生成的最终ASCII地址名 | 既有人工地址保存确认或非人工偏移确认后由Rust完成 |
| manual | 用户明确输入的ASCII技术名 | 显式手工改名预览/确认 |

pending 的 name 为空是明确状态，不存“待生成”等中文、原路径或临时假key。待生成原因由当前只读计划给出，不再存第二字段。新英文合法路径导入即可 auto_path，但地址仍null/停用；中文、空格、标点、数组和过长路径无需逐点另填英文，复用现有人工地址保存或“确认非人工偏移”时在**同一草稿事务**完成最终名。仅预览建议地址不生成已确认地址名，不额外增加每点英文必填步骤或第三次地址确认。

pending 可以作为草稿保存；**沿既有point.enabled门禁，只有pending且enabled=true的点在待激活配置准入时返回 `point_name_pending`**，不允许它作为有效启采点。enabled=false的pending点可以随其他合法配置激活，不以全库存在pending阻断无关配置；不自动关用户开关掩盖问题。旧 None 点的原准入不被新 ASCII 规则全局追溯阻断。受影响 managed 点的无效/缺名问题可见，未选 legacy 保持原值。普通读取/重启不生成或保存名称；已保存模式及名称原样恢复。

### R05. 状态保护、手工名与后续定义变化

`nameMode` 是服务认定状态。普通 `daa_save_draft` 必须核旧值：不能删掉/置null已有模式、把pending伪装None、伪造auto_path/auto_address、直接改name逃过预览，或以同名字符串冒充已生成。仅有旧JSON本来缺字段才兼容None；不根据字符串看似ASCII猜它是auto。新导入模式由Rust产生；普通save不能新造点/来源。

手工技术名规则 `^[A-Za-z_][A-Za-z0-9_]*$`、1–100字节且满足R03；不强制手工名仿造DB前缀。改过的名字设manual；合法旧手工名默认仍None，未经显式选择不自动认领。manual/None在重导、地址改变、数据类型改变后保持名字和模式；不悄悄追加新suffix。需要回到生成名时走同一个显式转换预览，不加mode下拉或另一套alias表单。

auto_path在无关地址变更后不变；路径/类型直接变化时在原导入预览中重算，列出旧→新（旧路径删除/改名/DB改号仍按005阻断）。auto_address在地址或类型失去确认后变pending；再次确认时重算，显示将更名的事实；其ID不变。既有auto因新点占名不会被隐式重算；冲突让本次新操作失败或pending，需另显式选择旧点才可转换。无变化重导保留ID/name/nameMode/ETag，不制造空版本。

定义变化只影响新草稿/后续显式激活产生的配置版本。旧sample/context/revision/manifest/pending/receipt保持当时定义；不拿新name重解释旧样本或自动重绑SMA。

### R06. 显式存量转换、预览和原子确认

在现有点位页按稳定point.id明确勾选（跨页保留，最多同一PLC的4096点），打开技术名预览；全库/过滤结果不能默认为已选。选择取消、关闭、冲突、过期token或stale ETag均零配置/来源写入，取消保留当前选择。预览逐点显示旧名、拟新名/模式、原路径、地址是否已确认、fallback原因与冲突；None/人工名被改也必须显著展示。批量转换只动所选name/nameMode，不动地址/理由、备注、组、开关或来源。

新增两个具名IPC `daa_preview_point_names` / `daa_confirm_point_names`，不得增加任意文件/SQL/网络接口。请求冻结expectedEtag、同PLC去重pointIds、intent（generate或edit）；generate只取所选已存点。edit限一个明确点，可带现有编辑器的有限用户字段patch（name可选、comment/enabled/groupId/address），以支持原弹窗一次保存；服务器从旧配置克隆并应用白名单，身份/来源/类型不由该patch改变。不是让客户端提交一份任意新Configuration或state。

preview返回旧→新行、readiness/冲突、canConfirm、inputDigest与随机token；只缓存一份有界候选，300s过期。confirm须同输入/token/digest/ETag，服务重核namespace、源/地址证明、模式转移、限额及写预算，再以既有config短事务/CAS提交并读回。任何一项selected不能完成、冲突/事务失败整次拒绝，不部分改名；unchanged保持原ETag。save/reload/导入/偏移/选择或编辑变化使确认失效，轮询不更新编辑基线。

现有点位弹窗的名称或地址编辑自动取得该只读预览，在原“保存草稿”最终动作前展示旧→新/待生成结果；同一次保存原子提交用户编辑与派生名称，失败保留输入，取消零写，不先保存其他字段再弹名称确认。已有偏移Dialog的预览同时展示将生成的名称，其原一次“确认非人工偏移”即可同事务保存地址与名字，不再要求额外名字确认。普通save若将诱发未预览的managed改名须返回 `name_preview_required`；不得提供绕过路径。

### R07. 确定的共享 crate 物理边界和 public 合同

提取 `automation-world/shared/tia-import-core/`，包名 `aiis-tia-import-core`、初始version `0.1.0`、edition2021、`publish=false`。只用Rust标准库，无生产/测试第三方依赖，无async runtime/SQL/Tauri/IPC/文件系统/网络/环境变量/随机数/时钟/PLC I/O，不依赖DAA/DS/backend/CU。没有循环依赖。DAA `src-tauri/Cargo.toml` 增加本地 `path = "../../shared/tia-import-core"`；不新建workspace或移动现有crate。

确定以下 Rust 公共入口及 DTO 信息责任（实现在以下确定结构内，不留“共享库还是复制”架构选择）：

| public API | 输入/输出合同 |
| --- | --- |
| `scan_sources(inputs: &[SourceInput], profile: ImportProfile) -> Result<SourceCatalog, Vec<Diagnostic>>` | SourceInput为调用方提供的InputId/显示文件名/原UTF8字节，不读取路径。严格UTF8/BOM/CRLF原样；catalog保留DB/TYPE声明引用、定位、可安全分界的逐块诊断；文件边界不安全拒绝。InputId仅一次调用的对应键，不是持久point/source身份。 |
| `expand_db(catalog: &SourceCatalog, db: &DeclarationRef, udt_closure: &[DeclarationRef]) -> Result<ExpandedDb, Vec<Diagnostic>>` | 显式逐DB依赖集合，不把同名不同版本全局合并。输出完整树、声明顺序、原路径及 `PathSegment::Field(String)/Index(i32)`、标量类型、数组界、注释/文件/行/路径诊断及明确优化状态；不带采集组、SQLite ID/ETag或初值。 |
| `layout_standard(db: &ExpandedDb, profile: LayoutProfile) -> Result<LayoutPlan, Vec<Diagnostic>>` | 固定 `siemens-step7-v20-standard-word-v1`，完整树到逐叶byte/bit/总长；不确认/写地址、覆盖manual或声称已验证真实PLC。DS自行校验自身region/内存范围。 |
| `plan_names(batch: &NameBatch) -> Result<NamePlan, Vec<Diagnostic>>` | 单个消费namespace、全点结构化路径/保留名、本次可改集合、明确已确认地址及固定profile；输出相关键对应的Resolved(path/address)/Pending和冲突原因。按R02/R03；不生成UUID、不写配置。 |
| `validate_manual_name`、`type_suffix`及profile常量 | 同一ASCII/长度/12类suffix规则；DTO使用独立Rust值对象，DAA/DS在薄adapter中转换。 |

`ImportProfile::TiaSubsetV1`沿005有界语法/预算，不新开放动态profile绕过。结构化路径不替换DAA现有sourcePath编码；调用方适配须证明原字符串、树、顺序、定位、完整/flat分类及错误语义不变。无serde依赖；JSON fixture由消费方现有serde读取，不为std-only库安装JSON解析器。

### R08. DAA 必须实际消费核心，保留来源和事务边界

`tia_source/parser.rs`改为调用核心的薄适配，移除旧算法重复实现但不删文件；`reconcile.rs`继续拥有逻辑source版本、逐DB不可变UDT闭包、source raw/hash重证、稳定DB/point身份、保全delta和005保守重导准入。`verify_db`继续按已绑定具体版本重证后才能向纯布局入口传入结构；普通save/客户端不能伪造ExpandedDb成为来源证明。

`plc_layout.rs`只将经重证结构送入共享布局、将结果转为DAA预览/确认，保留人工地址保护、完整集合/长度条件、layoutDigest/CAS和不启用/不激活语义。DB/UDT、地址/名字变更使用原草稿事务；双库、采样、历史、receipt、activation/recovery/scheduler/transport绝不为共享而搬走。

旧8层/9层拒绝、负/非零一维数组、嵌套数组拒绝、STRING可导入但整DB不推算、优化/未知/不完整整DB拒绝、源证明/人工保护/事务合同不放宽。移动算法时不得“修正”005官方oracle或用新实现反向生成期望。

### R09. 独立可消费黄金样例与版本清单

共享crate附独立手写 `fixtures/names.db` / `names.udt`、`expected-v1.json` 和说明pair，覆盖R02–R06例表。DB号为显式合成映射，文件无客户/端点/真实源内容。核心合同测试只用std；DAA现有serde测试读取JSON交叉核对，DS无需加载DAA应用才能取得源和固定期望。

将005原 `layout-oracle.json` **精确镜像**为共享 `fixtures/daa005-layout-oracle.json`，两者必须同为SHA `2f2f6fe79eea60b48357b72f8a4f352016da4c8d95220ba2e06005133c24e633`。原文件仍是该profile的单一规则版本；镜像不可独立修订或重新排版。两处不一致立即停止。新增命名fixture独立版本为v1，不混改旧布局期望；更多语法/布局另立版本任务。

Development交付时在tasks固定可移植清单：当前源码commit（有则记录，没有不虚构）、dirty工作树增量/完整crate路径与逐文件SHA、crate/name/layout/fixture版本、原parser来源SHA、005oracle双份SHA、DAA path dependency/lock差异、public API/支持矩阵、实际命令/raw及限制。该清单随共享README给出可定位入口；不执行Git tag/发布。消费者冻结完整清单或后续真实Git ref，不能只引用“最新DAA”。

### R10. UI、双语和稳定说明

点位主列展示“技术名称 / Technical name”，原路径始终作为独立次行/详情，pending显示明确状态且不以空白行代替。None显示“旧名称 / Legacy name”，不假称已符合新规则。现有编辑弹窗显示旧→新、auto/manual/pending语义和地址影响；保留sourcePath搜索，同时支持name搜索。导入Dialog增加新名/待生成摘要，offsetDialog显示对应拟名，批量转换完整差异进入独立私有预览Dialog。

复用CU/Element Plus及既有Console适配；只在现点位区域增加有限选择/入口，长差异按需弹窗、10/20/50分页，勾选跨页稳定。中英label/诊断/占位符对称，窄窗footer/取消/确认可见，正常间距，不堆新不可用表单、常驻大通知或全局视觉改造；state仍归唯一owner，组件无parser/第二轮询/IPC。

DAA/app/local_store README pair准确说明新name语义、legacy无自动迁移、地址待生成、人工名/历史/旧binary风险与共享入口。DAA/app pair同时按R13替换旧“迁入历史仍在details”描述，说明正常界面不展示历史、当前故障按需处理、正式dev入口和上述日志含义；保留默认脱敏示例，不能把当前私有receipt内容复制进README。R14的有限helper清理仅更新确受影响的既有稳定职责说明，不新增警告治理文档；CODE_INDEX只同步真实config职责及已触达模块，不扩为退役模块清扫。共享crate README/PLAN/catalog各有唯一归属，链接本任务唯一bundle，不造第二DAA-006或空角色文件。

### R11. 最少必要验证与证据边界

只验证新命名/状态/转换、共享提取后的受影响解析/布局证明，以及必要UI/存储保护。R13前置P0a只做正式源码/入口绑定/hash核对、现有Vue能力的受控组件状态分支与文档检查；R14的P0b只新增默认编译检查及现存config isolation_tests，feature编译核对与最终Rust必要检查合并，不启动程序。不另起native或重做005；迁入展示实窗检查合并到下述同一次命名原生增量记录。核用005的旧B/UI/store/原生证据须先固定其对应候选SHA并说明影响。**不重跑整个B、双库故障/维护/容量矩阵，不重采旧76样本，不做DS/S7/上传/长稳**。

最少增量：核心命名例表/拒绝和独立消费者compile；共享入口对005同一4例65叶oracle逐项相等及原8/9层/跨文件UDT定位/闭包证明的受影响过滤器；真实Engine/Stores路径下旧JSON零写、显式选中取消/确认/CAS/stale/最终冲突拒绝、模式伪造/降级负例和一次事务失败回滚；自有历史种子对原bytes/ID/receipt不变；前端构建、双语键与实际受影响Dialog/分页/窄窗检查。测试验证合同，不给每个薄wrapper补镜像测试或新增测试框架。

取得**一次足够的普通原生增量操作记录**：自有绝对tmp env/profile、旧来源指向自有空文件、read=false、不编Snap7/local-validation；先核同一普通入口的四页及运行配置details均无正常态迁入历史/入口（generic配置版本详情仍可用）→选择公开命名样例→合法英文即得名/中文数组待生成→现有偏移预览及一次确认后自动成名→明确选少量legacy种子点预览取消零写、再确认→重载/正常退出一次并同库对账。legacy样本仅由cfg(test)在自有双库中准备并固定原JSON/hash，seed结束释放所有连接后才普通原生打开，不增加产品SQL/seed入口。unknown/failed安全重试/摘要查询失败与normal状态分支在受控组件/原owner证据检查，不为展示额外造故障库/重启矩阵。不可绑定窗口可核用同轮Owner实际操作＋同库证据；缺必要证据如实blocked，不以浏览器假桥代替。无需额外反复重启或要求重做005操作。

批准后计划使用现有工具链：共享crate `cargo test --manifest-path automation-world/shared/tia-import-core/Cargo.toml --locked`；DAA同一Cargo工具链的 `--lib infrastructure::tia_source::tests`、`infrastructure::plc_layout::tests`、新 `infrastructure::local_store::point_naming_tests` 及确受影响的来源证明过滤器。既有store矩阵只核用对应证据；前端复用现有 `vite.validation.config.ts` 构建到自有绝对tmp dist，format为只读check。具体argv/结果由Development真实记录，PM当前不运行这些命令。

记录真实argv/cwd/exit/raw、精确候选和新旧期望SHA、一次操作观察限度；检查通过后只因新变更/失败/未决疑点重跑受影响部分。保留既有失败，所有辅助产物归自有tmp，验收后由coordinator核归属/依赖收尾，不清旧任务证据。

### R12. 串行交付、DS 接续与阶段归属

Development在tasks记录精确批准、R↔AC↔diff/新增全文、版本清单、必要自检、所有限制/资源和developer_handoff；coordinator随后实际启动新的fresh-context Verification，后者只写checklist并给独立verdict。QA失败返Development，实质范围改变返PM新Revision。qa_passed后才交Owner最终验收；本任务名/复用验收不等于DS已实现、阶段B已完成或阶段C已授权。DS与阶段依赖按§9，不通过本bundle修改其计划/批准。

### R13. 前置正式入口核对与正常态迁入展示收尾

R13作为批准后P0a，**先于R14警告清理及命名/共享代码修改完成**。固定当前正式根目录、HEAD/dirty增量、package→Tauri→Vite15191/src与src-tauri入口、005最终41文件来源清单及两组件挂载点；记录源码版本绑定，不推断Owner未知窗口/旧安装包的实时binary/hash。不更换入口、复制未知tmp代码、无条件合并005、覆盖配置或改变15191；发现所核入口与源码不符先报告精确差异，不能以“尚待验收才覆盖”解释。

展示方案固定为：从ConfigRevisionBar既有details中撤下迁入历史section；既有active/loaded/used/ETag/phase及reload/rollback等运行版本功能保留。将原YamlMigrationNotice复用为仅当前故障可打开的可关闭小Dialog，仍inject同一owner。ConfigRevisionBar只持有临时open状态，不新增迁入owner、轮询/IPC或持久隐藏偏好；正常态不挂载Dialog、无历史入口。四页共享配置栏均采用同一规则，不到各页复制提示。

| owner当前权威摘要 | 紧凑提示/入口及Dialog唯一内容 |
| --- | --- |
| `statusPersistence === 'unknown'`（优先） | 明示持久化未知，保留紧凑处理入口；Dialog只说明当前故障、必要错误码、修复存储/日志后重开。不给重试/覆盖动作，不能把关窗当修复或已记住。 |
| 非unknown且`status === 'failed' && retryAllowed === true` | 紧凑当前失败提示/处理入口；Dialog显示必要故障说明和原安全重试动作，消费Rust权威retryAllowed、attemptId/ETag，不展示整份旧回执。 |
| imported/imported_with_diagnostics/skipped_empty/archived_policy_only/existing_sqlite_preserved/validation_excluded/not_attempted，以及持久failed且retryAllowed=false | 正常态无迁入标题、源路径/SHA/计数/attempt/诊断历史、入口或隐藏在details中的历史表；不因skipped_empty或policy-only的历史retryAllowed为true就额外开放入口。说明继续归README。 |
| migration=null（查询中/查询失败） | 不显示旧摘要或旧重试动作；保留owner现有真实error及“已保存、摘要未加载”的语义，不伪造正常/成功或吞掉故障。 |

Dialog打开/关闭零写，不自动重试/激活；关闭后当前故障提示仍在，不能永久dismiss未知状态。权威摘要转为正常/null时关闭并卸载Dialog；同一个open状态不能延续显示旧attempt。失败仍可重试时保留当前错误，重试只调原`local.retryMigration()`，沿busy/dirty/editing guard及expectedEtag/expectedAttemptId双CAS；前端不据旧receipt自算可重试。源路径、SHA、attempt等传输字段可继续在内存用于既有门禁，不因此渲染为历史表。

P0a只修改§7的两既有组件、既有README/app pair/i18n/CODE_INDEX有限说明及相应中文头部；该阶段owner/facade、全部Rust/driver/数据库/日志事件与level/配置helper保持原字节。之后P0b仅按R14对config/mod.rs作六symbol有限处置；不能把此例外套用到P0a或其他Rust源。后续原R01–R12的获批allowlist不因此扩大。保存成功后摘要查询失败仍承认已保存、先清旧动作；未知持久化不能因取消展示隐藏成正常。保留一次性自动机制、防重receipt、所有旧配置/历史和Rust/IPC/retry准入；不删除或重写receipt、扫描源、增表或提供覆盖动作。

P0a必要检查仅用实际两SFC/现有Vue能力覆盖上表、normal→fault→normal/null关闭、开/关零写及busy/dirty/editing禁用，并核用未变owner的保存后摘要失败/双CAS原证据。最终迁入展示实窗观察并入R11同一次命名native，不单独启动/重做旧B或005导入矩阵。README准确说明Owner提供日志与源码的解释边界，不将4组dead_code视为运行失败；当前r3的清理授权范围仍待精确批准且仅为R14六symbol。

### R14. 展示收尾后的六symbol/四组编译警告有限清理

本需求是新增P0b，只在R13的P0a收尾之后、原P1命名/共享准备之前执行。目标仅是Owner所报DAA本包的四组dead_code诊断：一组三个AgentConfig方法，以及三个free function各一组，共六symbol。固定以下最小方案，不以可见性/无意义调用/恢复退役模块制造使用：

| 精确symbol（均在config/mod.rs） | 当前只读调用事实 | 获批后唯一处置 |
| --- | --- | --- |
| `AgentConfig::raw_value` | 引用只在未注册的旧services/plc_collection.rs | 删除该方法完整定义。 |
| `AgentConfig::non_empty_value` | 引用只在未注册的旧infrastructure/plc_points.rs | 删除该方法完整定义。 |
| `AgentConfig::is_configured` | 引用只在未注册的旧plc_collection/runtime_snapshot/authorization_gate | 删除该方法完整定义。 |
| `parse_u16_or_default` | 引用只在未注册的旧infrastructure/plc_points.rs | 删除该free function完整定义。 |
| `parse_u64_or_default` | 引用只在未注册的旧plc_collection/plc_diagnostics/authorization_gate/plc_snapshot_policy | 删除该free function完整定义。 |
| `resolve_output_path` | 旧logging未注册；当前有效调用为原`config::isolation_tests::relative_contract_paths_are_anchored_to_this_application` | 给现定义加`#[cfg(test)]`，保留原实现及已有测试断言；不另造测试来让helper看起来有用。 |

上述判断覆盖当前lib/main、退役runtime bin、debug local-validation bin及rust-snap7-driver/local-validation单独或组合的模块图；这些features不会重新注册旧调用源。实施前再核同候选引用/注册清单；若发现真实活动调用，停止该symbol的删除/裁剪，记录具体入口、feature、file:line与为何不能按表处置，返PM界定有限保留条件。不能把调用者迁回执行图或扩展为退役源重构。本r3不承诺未注册旧模块可单独重新编译；将来恢复它们须独立范围。

仅M `src-tauri/src/config/mod.rs`：删除上述五个无活动调用定义，保留resolve_output_path为test-only，可对本文件现有头部作准确的最小职责更新。`profile_dir`仍服务local_bootstrap，及AgentConfig加载、configured_keys/locator/value_or_default/bool_or_default、env白名单/优先级/引号处理、application_root/resolve_runtime_path等活动实现保持原字节；不改profile/env/门禁/驱动/日志、local_bootstrap或任何旧模块。原两个isolation_tests及其有效断言保留，最多仅本文件必要编译适配，不能删断言、加测试框架或用新测试为无用helper制造用途。

不得新增/扩大/借用`allow(dead_code)`、`expect(dead_code)`、crate/global lint关闭、RUSTFLAGS `-A`或改pub可见性来隐藏目标诊断；不得假调用、重注册旧模块、关闭检查目标、升级依赖/安装工具。既有local_bootstrap上的其他cfg_attr lint属性是受保护旧字节，不改它、不把本六symbol移过去借其抑制。也不引入全局`-Dwarnings`，不追求仓库或依赖全量zero-warning。正常runtime事件/level及其他warning继续如实记录。

**最少新增验证（当前计划阶段不运行）：** P0b用现有锁和Cargo，执行一次 `cargo check --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --locked --no-default-features`（编译检查、不启动程序）及一次 `cargo test --manifest-path automation-world/data-acquisition-agent/src-tauri/Cargo.toml --locked --no-default-features --lib config::isolation_tests -- --nocapture`（现有两测试，仅纯配置/路径断言，不初始化SQLite/PLC）。分别启用rust-snap7-driver和local-validation的debug编译兼容核对，合并至原任务最终Rust必要检查、每profile一轮；已有同候选同features的最终构建可核用，不为R14重复编译。不能用两feature同时启用的fixture路径代替driver-only分支，也不新增release/local-validation已知拒绝矩阵。

最终tasks保留默认check原日志、现存两测试结果，以及两个feature profile实际argv/exit/raw与精确候选；核六symbol四组目标诊断消失并说明原五定义删除/test-only一项，无全局抑制。其他编译/依赖warning仍原样记录，不扩大修复；依赖缓存/链接等限制如实给出精确未验范围，必需编译证据缺失不得写通过。没有新增native启动/GUI/采集、真实PLC、配置写入或整套B验证；R11原一次原生命名记录保持。

## 4. 正反例与确定处理

下表的DB号/路径/地址都是合成验证数据；有地址的“生成”均指已通过既有确认，不是仅显示推算值。

| 输入/场景 | r3唯一预期（命名合同沿用r1/r2） |
| --- | --- |
| DB28 `ActTemp_Z1: INT`，address=null | `DB28_ActTemp_Z1_Int`、auto_path；地址仍null、disabled。 |
| DB28 `Driver_W.Unc_1.ActTemp: INT` | `DB28_Driver_W_Unc_1_ActTemp_Int`；大小写保留。 |
| DB28 字段 `1_Act: REAL` | `DB28_1_Act_Real`合法，不加下划线、不翻译。 |
| DB60 `卷材编号: STRING[20]`，address=null | name=""/pending，完整中文原路径可见；手工确认byte0后`DB60_B0_String`，不推算含STRING的DB。 |
| DB47 `整机复位: BOOL`，确认byte12/bit0 | `DB47_B12_0_Bool`；缺bit、bit8、未确认均不得冒充最终地址名。 |
| 含空格/`a-b`/引号内`a.b`，或数组`items[-1].Value` | 非法段/Index走地址；不删符号/下标拼成语义名。未确认则pending。 |
| DB1、INT路径单段92个a / 93个a | 完整名分别100/101字节：前者path可用，后者转地址（不是截成100）。 |
| DB28 `A_B.C`与`A.B_C`，均INT | flatten同`DB28_A_B_C_Int`；本次可改两点均走各自地址，如byte0/2得`DB28_B0_Int`/`DB28_B2_Int`。无地址的成员pending，不能先到先得。 |
| 上例两点最终同byte0/INT | 最终名仍同，整次确认拒绝；不加1/随机后缀，不覆盖旧配置。启用地址重叠校验同样保持。 |
| 新候选与未选旧手工`DB28_A_B_C_Int`撞名 | 只使新候选地址兜底，旧名原字节不变；兜底再撞则整次拒绝。 |
| PLC-A、PLC-B均DB28 `Value: REAL` | 两者均可`DB28_Value_Real`；以不同plcId/id区分，不拼显示名/IP。 |
| 同PLC跨DB/组/停用点保留了目标最终名 | 同一namespace仍冲突；不得因停用/过滤隐藏而覆盖。 |
| 同DB重复字段或真正歧义UDT/路径 | 源解析拒绝，命名不能把坏源修成有效配置。 |
| 旧JSON name=`卷材编号`且无nameMode | 读/启动/无关保存/原激活不改名、不写回、不全面阻断；显式选中且确认地址后才可转换。 |
| 存量选择→预览→取消；其后以旧ETag确认 | 取消不写；stale/token失效拒绝，旧ID/名称/ETag/历史保持。 |
| 手工名`Roll_Code`，后来地址/类型改变 | name/manual保持；重新选择自动生成必须另预览，不能悄悄跟suffix变化。 |
| 普通save把pending的nameMode删除、或直接写auto_address | 拒绝；None兼容不是新请求的逃生通道。 |
| 已生成点重启/相同来源重导 | 相同name/nameMode/id；无有效变化同ETag。不重新分配UUID或重写旧历史。 |
| 自动地址名的确认被源布局变化撤销 | 同目标草稿变pending；该点enabled=true时阻断待激活配置，enabled=false可随无关合法配置激活。旧active及旧样本解释保持，重新确认地址再生成。 |

## 5. 排除项与风险

明确不做：第二套alias/code/key或SMA业务命名、翻译服务/拼音、Python运行时、XLSX/YAML新模式、全库自动迁移、模糊匹配/删点换ID、005禁止的删叶/改叶或块名/DB改号迁移、新TIA语法/类型/STRING推算/优化布局、初值执行、DS产品/服务端编码/内存/权限/规则/G0实施、真实S7/PLC联调、Backend/SMA/Stage C/上传/ACK/补传、改双库/DDL/采样编码/恢复调度、依赖升级、workspace重建、实机/现场/生产DB/API、Docker、Git写入/refs/发布部署、跨平台打包或长稳。

| 待Owner随精确r3批准接受的风险/取舍 | 约束与停止条件 |
| --- | --- |
| 现有name语义变为技术名，旧数据仍有非ASCII/重复 | 单字段legacy保留；显式选择转换；新managed只在本PLC唯一。不能承诺一升级全库已规范。 |
| 中文等新点需先确认地址 | pending明确可见、禁用新启采；沿现人工/非人工确认自动生成。不能造地址或强制逐点另填英文。 |
| 碰撞/定义变更可阻断本次提交或使managed名待生成 | 全量namespace预览、固定fallback、同事务；不能静默改未选点解冲突。 |
| 可选JSON使旧binary不兼容 | 新程序读旧数据无自动写回；旧deny_unknown_fields程序可能拒绝新mode。降级需独立证明，不承诺原二进制可直接回退。 |
| 公共提取触及已接受解析/布局算法 | 无依赖核心、DAA实际消费、保留005proof与原oracle同SHA；发现边界/定位/事务回归先停止，不改期望求绿。 |
| DS消费时点误判或范围无限扩大 | draft只对齐；接受后才交精确代码清单。B所需DS基线限定联调必需能力，不把DS所有长期扩展/容量profile作为无限前置。 |
| 原生工具/临时证据限制 | 一次操作＋同库记录，缺必需证据blocked；真实限制保留。tmp非唯一永久结论，tasks/checklist写可复核事实。 |
| 撤历史时把unknown/摘要查询错误一并隐藏，或误认为正式实现待merge | R13/P0a仅撤正常历史；unknown/可重试当前失败及已有真实error仍可见。入口/source清单先核，005原41文件已在正式源码；不复制tmp或改迁入机制。随后warning清理只限R14/P0b。 |
| helper删除误伤活动配置或以cfg/lint掩盖真实调用 | R14逐symbol核模块/feature入口；profile_dir及活动加载/路径保留。五删除、一项已有测试专用；真实活动引用出现即停该处置返PM。不顺手清理仍引用它们的未注册旧源，也不宣称这些旧模块现可重新启用。 |

恢复只针对本任务自有增量/隔离实例，在核before/diff/后续引用后按明确授权处理。不清真实库/receipt/journal、重置序号、复制tmp库到正式profile或擅自回退旧binary；本草案不授予回滚/删除权限。

## 6. 实施顺序与gate

| 阶段 | 必须完成 | 下一gate/停止条件 |
| --- | --- | --- |
| G0 | Owner批准精确DAA-006 r3及其范围/风险/allowlist | 2026-10-19已满足，获批草案SHA与原话见§1；r1/r2历史不变。下一gate为实际Development，PM本轮不创建tasks/checklist或运行产品。 |
| P0a | 先固定实际before/批准SHA/005保护SHA及正式入口绑定→R13正常态撤历史、当前故障小Dialog、README日志说明→受控组件分支/hash/文档检查 | 先完成展示收尾；该阶段owner/Rust机制不动，不独立启动native/重做005，不处理未知tmp合并或warning清理。 |
| P0b | R14六symbol引用复核→仅config/mod.rs五删除/一test-only→默认cargo check及已有isolation_tests原日志 | 先于原P1；不抑制lint、不清退役源/改活动配置。features编译并入最终Rust必要检查，不增加启动/采集。 |
| P1 | 冻结原r1的新命名期望、核心DTO/单字段状态转移与旧JSON零写方案 | 不增加R04之外持久字段/依赖或改oracle；无法满足先返PM。 |
| P2 | 无I/O核心提取＋DAA薄适配，保留完整来源重证/闭包/定位/布局 | 共享/旧入口同合同；不修改DS。 |
| P3 | 命名/碰撞/pending/manual/legacy、预览/CAS/原子确认、普通save防降级 | 先核心/真实service-store必要增量；无隐藏全库改名。 |
| P4 | 现点位UI/导入与offset弹窗、双语/README；合并R13正常展示的一次命名原生增量记录 | 不重复旧B/005矩阵，形成精确候选/清单。 |
| G1 | Development developer_handoff→新fresh-context Verification | 失败保留、返工后新handoff/新fresh QA；缺证据不伪造通过。 |
| G2 | qa_passed→Owner最终验收 | 接受的只是本任务展示/有限warning清理/命名/共享准备；此时才可交DS精确可消费版本。 |
| 后续独立gate | DS可联调基线＋DAA↔DS真实协议读取/SQLite联调→fresh QA→Owner B阶段验收 | 由另立spec批准，不在本任务执行；随后阶段C。 |

## 7. 精确文件 allowlist 与角色责任

下表为**未来精确r3获批后的封闭实现面，共61条（39M＋22N）**：原r1的58路径保留，r2只增两既有迁入组件M，r3再仅增config/mod.rs一个M及既有说明的R14有限责任；不扩大driver/数据库或其他UI表面。不代表本轮PM获得这些写权限。M=既有有限修改，N=新增（已存在须先核归属，不覆盖未知内容），不允许删除/移动文件；R14仅删除表内五个函数/方法定义。所有路径均相对仓根；目录不是递归授权。无需修改的允许路径可以保持不动，新增路径必须真实需要，不为凑清单造文件。

| 操作 | 精确路径 | 唯一责任 |
| --- | --- | --- |
| N | `automation-world/shared/README.md` | 结构性共享目录地图，归AW/DAA计划，不成为新事实源。 |
| N | `automation-world/shared/README.zh-CN.md` | 对称中文。 |
| N | `automation-world/shared/tia-import-core/Cargo.toml` | std-only/publish=false小crate，无第三方依赖。 |
| N | `automation-world/shared/tia-import-core/Cargo.lock` | standalone检查的唯一local package记录；无registry包。 |
| N | `automation-world/shared/tia-import-core/src/lib.rs` | 有限public入口/re-export/profile常量。 |
| N | `automation-world/shared/tia-import-core/src/model.rs` | 独立纯DTO/结构化路径/诊断，无DAA身份模型。 |
| N | `automation-world/shared/tia-import-core/src/parser.rs` | 受限scan/parse/expand单一算法。 |
| N | `automation-world/shared/tia-import-core/src/layout.rs` | 已接受profile的纯布局，不做确认/来源SQL。 |
| N | `automation-world/shared/tia-import-core/src/naming.rs` | R02/R03单一生成/碰撞/人工名校验。 |
| N | `automation-world/shared/tia-import-core/tests/contract.rs` | std-only核心合同与独立消费者编译调用；不启动DS。 |
| N | `automation-world/shared/tia-import-core/fixtures/names.db` | 新手写公开命名样例。 |
| N | `automation-world/shared/tia-import-core/fixtures/names.udt` | 新手写公开嵌套/数组依赖。 |
| N | `automation-world/shared/tia-import-core/fixtures/expected-v1.json` | 独立命名/状态固定期望和合成DB映射。 |
| N | `automation-world/shared/tia-import-core/fixtures/daa005-layout-oracle.json` | 只可精确镜像原SHA，不另改期望。 |
| N | `automation-world/shared/tia-import-core/fixtures/README.md` | fixture版本/原oracle单一权威/消费说明。 |
| N | `automation-world/shared/tia-import-core/fixtures/README.zh-CN.md` | 对称中文。 |
| N | `automation-world/shared/tia-import-core/README.md` | public API、profile、支持/拒绝、来源版本清单、DS薄适配。 |
| N | `automation-world/shared/tia-import-core/README.zh-CN.md` | 对称中文。 |
| M | `automation-world/data-acquisition-agent/src-tauri/Cargo.toml` | 仅新增本地path依赖；已有包版本/features不变。 |
| M | `automation-world/data-acquisition-agent/src-tauri/Cargo.lock` | 仅新增本地package及DAA依赖边；已有registry包/version/checksum不变。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/config/mod.rs` | 仅R14五symbol定义删除、resolve_output_path加cfg(test)、必要本文件头部/原测试编译适配；活动加载/env/路径/profile逻辑及原测试有效断言不改。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/domain/local_configuration.rs` | 可选nameMode/分层准入、legacy兼容；原schema/ID不变。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/domain/mod.rs` | 仅新point_naming模块注册。 |
| N | `automation-world/data-acquisition-agent/src-tauri/src/domain/point_naming.rs` | 状态/命名预览DTO与纯核心模型适配；无SQL/I/O。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/domain/source_import.rs` | import预览中有限名称delta/待生成信息。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/tia_source.rs` | 原入口接线保持。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/tia_source/parser.rs` | 变薄适配，不残留第二套算法或删文件。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/tia_source/reconcile.rs` | 来源重证/闭包保持，新点命名和已管理直接定义变化。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/tia_source/tests.rs` | 受影响解析/重导/命名回归；旧人工/legacy种子准确表达，不删保护断言。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/plc_layout.rs` | 共享纯布局适配、原地址确认及相应名称同事务。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/plc_layout/tests.rs` | 原oracle及受影响证明/人工保护定向检查，不改oracle。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/mod.rs` | 仅cfg(test)新名称测试模块注册。 |
| N | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/point_naming_tests.rs` | 真实Engine/Stores模式/CAS/取消/回滚/历史原字节测试。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/source_import_tests.rs` | 受影响生成名/legacy人工种子及原保全断言，不重写旧store矩阵。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/yaml_migration.rs` | 仅Point构造nameMode=None；发现/receipt/归档算法不变。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/services/mod.rs` | 仅local_point_naming模块注册。 |
| N | `automation-world/data-acquisition-agent/src-tauri/src/services/local_point_naming.rs` | 有界preview/confirm、namespace/状态准入/既有store调用，不写SQL。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/services/local_configuration.rs` | save防伪造/降级、预览失效、导入/offset命名接线，原CAS/来源保护。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/services/local_supervisor.rs` | 仅一份命名preview缓存/init；不改actor/采集调度。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/commands/local_acquisition.rs` | 两具名IPC薄DTO/dispatch/macro接线。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/lib.rs` | 仅两新命令注册，不动启动/门禁。 |
| M | `automation-world/data-acquisition-agent/src/services/localAcquisition.ts` | 对称DTO/两具名IPC，无browser假桥。 |
| M | `automation-world/data-acquisition-agent/src/console/composables/useLocalAcquisitionConsole.ts` | 唯一owner的选择/预览/状态失效/保存流程。 |
| M | `automation-world/data-acquisition-agent/src/components/console/ConfigRevisionBar.vue` | R13撤details内迁入历史，仅当前故障紧凑入口/Dialog接线，保留原配置版本功能及中文头部。 |
| M | `automation-world/data-acquisition-agent/src/components/console/YamlMigrationNotice.vue` | R13复用为受限当前故障小Dialog；不再渲染正常历史，不另建owner/IPC，更新中文头部。 |
| M | `automation-world/data-acquisition-agent/src/app/plc/views/points/index.vue` | 技术名语义、有限选择、原编辑/offsetDialog。 |
| M | `automation-world/data-acquisition-agent/src/app/plc/components/SourceImportPanel.vue` | 原导入Dialog名称/待生成摘要。 |
| N | `automation-world/data-acquisition-agent/src/app/plc/components/PointNamePreviewDialog.vue` | 纯展示差异/冲突/分页，状态仍归唯一owner。 |
| M | `automation-world/data-acquisition-agent/src/styles/app.css` | 仅本命名表/弹窗局部间距和窄窗类。 |
| M | `automation-world/data-acquisition-agent/src/locales/zh-CN/common.json` | 本次名称状态/错误及R13紧凑当前故障/Dialog中文。 |
| M | `automation-world/data-acquisition-agent/src/locales/en-US/common.json` | 对称英文键/占位符。 |
| M | `automation-world/data-acquisition-agent/src/app/plc/locales/zh-CN.json` | 点位/导入名称label和说明。 |
| M | `automation-world/data-acquisition-agent/src/app/plc/locales/en-US.json` | 对称英文。 |
| M | `automation-world/data-acquisition-agent/README.md` | 稳定名称/兼容/复用/阶段边界，R13正式入口/正常展示/日志含义；不复制当前私有receipt。 |
| M | `automation-world/data-acquisition-agent/README.zh-CN.md` | 对称中文。 |
| M | `automation-world/data-acquisition-agent/src/app/README.md` | 单owner/名称Dialog/预览与原子保存，R13正常无历史和当前故障Dialog位置。 |
| M | `automation-world/data-acquisition-agent/src/app/README.zh-CN.md` | 对称中文。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.md` | 可选JSON/历史保护/降级限制，无DDL。 |
| M | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md` | 对称中文。 |
| M | `.gitignore` | 仅精确放行新shared fixture names.db，不放开其他DB/真实输入。 |
| M | `CODE_INDEX.md` | 本次实际新crate/模块、R13两组件与R14 config有限职责，不扩退役模块整理。 |

角色/索引另行明确，不计为实现文件：

- PM/Human Owner：本 `automation-world/data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/spec.md`；r1创建后本轮仅在此唯一文件修订r2。
- Development批准后才N：同目录 `tasks.md`；新fresh-context Verification在handoff后才N：同目录 `checklist.md`，当前不创建/链接未来角色文件。
- coordinator `/root` 独占10个既有索引的本任务机械同步：根 `PLAN.md`/`PLAN.zh-CN.md`、`plans/README.md`/`plans/README.zh-CN.md`；`automation-world/PLAN.md`/`PLAN.zh-CN.md`；DAA `PLAN.md`/`PLAN.zh-CN.md`、`plans/README.md`/`plans/README.zh-CN.md`。
- **未来实施后** coordinator才N共享crate的四个索引：`automation-world/shared/tia-import-core/PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`。均相对crate目录，唯一链接本DAA-006 bundle及DAA owning PLAN，不创建第二bundle。当前不生成空共享目录/索引。

其他全部保护：root AGENTS/workflow/角色/skills、旧bundle和长设计正文、所有旧fixture/真实源（包括005原oracle）、schema/SQL/activation/runtime ledger/context/sample编码/恢复/scheduler/managed_s7/driver、Tauri配置/capabilities、package/pnpm锁、真实env/YAML/profile、CU/CA/SMA/DS/backend/frontend-js/tools/contracts。Cargo.lock仅上述局部包关系例外；发现需要升级registry依赖、加DDL或额外持久字段先停报PM。

## 8. 验收标准

以下均为批准后的义务，当前未实施/未验证；PM文档自检不记为pass。

| AC | 可核完成条件 | 对应需求/最少证据 |
| --- | --- | --- |
| AC01 | 独立身份/精确批准/封闭路径与串行角色链成立，旧接受和pending状态不被改写。 | R01/R12；实际before/批准SHA/diff/新全文/保护hash。 |
| AC02 | 12类suffix、数字开头段/大小写、100/101边界及原始结构化路径规则精确。 | R02；例表固定期望，类型/采集解码不变。 |
| AC03 | 中文/空格/标点/数组/长名按已确认地址兜底，BOOL位准确，无翻译/截字/随机名。 | R02/R04；无地址/未确认/非法bit负例。 |
| AC04 | 同PLC全部点namespace、跨PLC同名、flatten全碰撞集合/保留旧名及最终冲突拒绝，顺序稳定。 | R03；同/跨PLC、输入置换/跨页/先后确认、最终再撞反例。 |
| AC05 | 单字段None/pending/auto_path/auto_address/manual合同成立；读取旧JSON不写、旧非ASCII/重复不使旧库全面失效。 | R01/R04；自有旧JSON read/无关save/原准入、原字节对账。 |
| AC06 | pending且enabled=true的点阻断待激活配置；停用pending不阻断无关合法配置。既有人工/非人工地址确认同事务自动成名，无额外逐点英文/第三次确认。 | R04/R06；enabled正反例、preview不作最终地址，成功/失败原子对账。 |
| AC07 | 普通save不能删除mode、伪造auto或直接绕过改名；None兼容与状态转移分开。 | R05/R06；缺字段/null/伪状态/伪地址/未preview负例。 |
| AC08 | 显式selected旧→新/冲突预览、取消零写、token/digest/ETag/期限和selected集合原子性成立。 | R06；真实Engine/Stores、stale/重放/混PLC/重复IDs/一次中途失败回滚。 |
| AC09 | manual/legacy保名，auto直接定义变更按规则更新；重启/同源重导稳定，旧历史/人工配置不变。 | R01/R05；ID/name/mode/ETag及自有历史/receipt原bytes，未选点逐值对账。 |
| AC10 | std-only核心在确定物理路径及public DTO/API可独立编译调用，DAA实际path消费，无第二套算法/循环/运行I/O。 | R07/R08；依赖图、核心consumer、DAA受影响编译和源码差异。 |
| AC11 | 源重证/闭包/UDT定位/8与9层/数组/STRING/人工保护及原布局结果不退化。 | R08/R11；原oracle4例65叶逐项、实际来源证明与受影响过滤器；不重做全B。 |
| AC12 | 共享黄金源/期望/版本清单可由DS独立取得，两份原oracle同固定SHA，无另生规则。 | R09；逐文件SHA、fixture版本、core API/DAA适配清单。 |
| AC13 | 技术名/原路径/legacy/pending中英准确，旧点转换与原编辑/导入/offset交互有序、分页选择和窄窗可用。 | R10；实际组件观察/键占位符/必要前端构建，状态唯一owner。 |
| AC14 | 一次普通native新命名→地址确认→显式存量取消/确认→重载/退出及同库记录足够。 | R11；自有profile/read=false、真实操作/ID/ETag/hash，不冒称DS/实机。 |
| AC15 | 文档/索引/头部准确，最少必要增量与旧证据核用边界完整；交付清单精确。 | R09–R12；真实命令/raw/限制/保护审计/双语链接/资源。 |
| AC16 | 新fresh QA与Owner终验分层；DS两个接续时点、B剩余gate与C依赖不混淆。 | R12/§9；无DS/阶段C实施和未经批准消息，旧任务状态保持。 |
| AC17 | 正常态四页及运行配置details无迁入历史/入口；仅unknown优先、failed且retryAllowed的当前故障有紧凑提示与可关闭小Dialog，null无旧动作；原owner/重试guard不退化。 | R13；实际SFC状态分支/打开关闭零写/normal转换/dirty-editing-busy、保存成功摘要查询失败原证据核用；不重做Rust重试矩阵。 |
| AC18 | 正式普通dev入口与本仓源码/005精确来源清单可核，README说明日志/示例及当前界面，不把验收当自动merge/覆盖或warning当失败。R13实窗检查合入同一次命名native。 | R13/R10/R11；入口/hash及Owner日志来源边界、005原SHA保持、两组件限定增量、一次原生记录，无tmp复制/配置改写/新增启动或广泛清理。 |
| AC19 | 六symbol按R14逐项五删除/一cfg(test)，原resolve测试有效断言及活动profile_dir/env/路径实现保持；没有lint压制/假调用/旧模块重注册或额外源清扫。 | R14；同候选入口/feature引用表、config/mod.rs精确diff、其余配置/旧模块保护SHA；发现活动引用停止对应删除返PM。 |
| AC20 | 默认no-default-features的locked check及已有两isolation_tests通过，本包目标四组/六symbol warning消失；两个feature编译兼容与最终Rust检查合并、原日志及限制可核。 | R14/R11；真实argv/cwd/features/exit/raw、精确候选、无新增抑制flags/依赖变更；不要求全包/依赖零warning，无新增native/采集/旧B矩阵。 |

## 9. DS 接续清单与 Stage B / Stage C 依赖

### 9.1 两个接续时点

**现在：** Owner可将本spec链接交给既有DS会话，对齐命名/导入边界并按该会话自身批准推进独立G0。现在只有draft，没有可复制的新命名实现/公共SDK；DAA-006未批准或实施不能成为DS已交付依赖。ARCH-AW-005 r2执行批准、go/no_go与后续产品gate仍归DS会话，不由此文代理。

**DAA-006实现→新fresh QA→Owner接受之后：** 才交本任务精确代码/manifest/fixture版本给DS消费。收件材料为本spec、届时真实tasks/checklist、共享crate README/public入口、完整文件SHA/源版本/锁差异、固定黄金输入与期望/原oracle镜像、支持/拒绝矩阵和未验证边界。当前不建立指向未形成文档的假链接，也不向该线程发送消息。

| DS接续项 | 消费边界/其独立验收 |
| --- | --- |
| 解析/展开/布局/命名 | 通过共享crate public API消费固定版本；无须另造同规则parser/name generator。不整页复制DAA，不承诺整个配置零适配。 |
| 薄适配 | DB/TYPE声明/原路径/type/建议地址映射为DS自己的instance/DB-region/point配置；DS自有ID、标识符、profile/env/存储，不能复用DAA profile、receipt或样本ID。 |
| 初值/encode/内存/权限/变化规则 | 共享解析不提供初值；DS明确设置初值并实现大端编码、region边界/bit覆盖、写前权限、单内存owner和生命周期。不得用DAA跳过BEGIN称导入初值。 |
| G0与产品基线 | DS会话独立批准/实施/验证/接受所需gate；本任务不代替其native ABI、写前拒绝、协议或资源证据。 |
| 接入验收 | DS在其任务记录固定crate/fixture SHA，跑自身薄适配及独立golden/实际协议必要检查，列明差异；兼容失败不自行fork共享期望或静默放宽DAA边界。 |

### 9.2 Stage B aggregate remaining gates

| 汇总层 | 当前事实 | 剩余退出条件 |
| --- | --- | --- |
| 阶段A/005局部能力 | DAA-001与005已Owner接受；不降级/重开 | 保留其原范围与失败/接受记录。 |
| 受控本地闭环/SQLite/导入增量 | 002r2/003r1/004r1已有各自qa_passed及受控证据 | 各自Owner最终验收pending，按原bundle独立处理；不从本spec代验收。 |
| 本任务展示收尾、有限warning清理、命名与复用 | DAA-006 r3 owner_approved；Development待启动 | 精确批准→P0a/R13展示/入口核对→P0b/R14六symbol清理→原命名/共享实施→fresh QA→Owner接受；完成仍不关闭B。 |
| DS可联调基线 | G0/产品gate独立进行 | 取得DS自身获批并验收、满足后续联调约定的受控本地基线：所需S7读服务、明确端口/TSAP、DB/类型/长度/初值及资源边界。不是要求DS所有长期扩展/全部容量profile完成。 |
| DAA↔DS闭环 | 尚无本任务授权/完成证据 | **另立精确spec批准**：DAA真实ManagedS7驱动（local-validation关闭）、非102等约定端口/受控DB实际读取→解码→完整轮SQLite样本/解释/manifest/pending及必要停止/重连，独立fresh QA与Owner接受。fixture transport或Python客户端不替代该链路。 |
| 阶段B整体关闭 | 仍未关闭 | 上述有界剩余gate齐备并由Owner明确接受阶段B；模拟DS证明不等于实体PLC/现场投产或安全验证。 |

### 9.3 Stage C dependencies

阶段C是后续可靠事实上传，不在本任务实施。可并行讨论/形成后端API合同：fact/manifest身份、配置解释引用、幂等、ACK含义、超时/重试/补传/顺序与pending保留；不得因此启用HTTP/后台上传、ACK/清队列或新后台运行任务。开始C实施前需B汇总退出条件、稳定Backend合同及独立精确spec/范围批准；SMA业务映射继续独立。DS联调、本任务或旧QA通过均不授予生产数据库/API、真实设备或现场切换权限。

## 10. 修订历史与 PM 文档检查

- 2026-10-19，r1 draft：按Owner“直接开始做spec”请求起草。R01–R12/AC01–AC16、技术名状态与碰撞顺序、std-only共享crate/DS两个接续时点、B剩余gate与C依赖形成；r1未获批准、未实施。原文全文归档 `/private/tmp/daa-006-r2-spec-wxtwzx9l/r1-spec-before.md`，52936字节，SHA=`b7a67690ecc9badb4d025bfe2579eecafd2d2d9a2182d7fb1da0f4f731afb197`，只作精确历史附件，不成为第二当前spec。
- 2026-10-19，r2 draft：按Owner新steering加入R13/AC17–AC18，先正式入口与正常态迁入展示收尾，再原命名/共享；原58路径只增两既有组件为60（38M/22N）。DAA-004允许折叠历史的原合同与QA事实、005接受及41文件在正式源码的事实保持；不向旧bundle回填“漏合并”。PM读Owner日志及当前源码作解释，没有独立启动或QA。
- 2026-10-19，r3 draft：Owner明确要求先出四组编译warning有限清理spec、批准后改代码；新增R14/AC19–AC20和唯一config/mod.rs路径，总61（39M/22N），顺序P0a展示→P0b六symbol→原P1。r2未批准/未实施，完整原文归档 `/private/tmp/daa-006-r3-spec-83zdc53u/r2-spec-before.md`、SHA=`ebbf43dfff9e1a85565737f91b57ca97a72870b28669ae55d7387a44c46c67d6`；不在本spec复制其全文。原13R/18AC的功能目标保留，R13/P0a继续Rust不动，R14是随后唯一有限例外，其他旧helper/warning不清理。
- 2026-10-19，r3 owner_approved：Human Owner按§1完整原话精确批准草案SHA=`b133bbfb2e44a05d5b79764afe6a7bc9988c5332f12e33beaf61a51cffdc825f`。本次只记录批准/状态/handoff；R01–R14、AC01–AC20、61实现路径、风险/排除及实施顺序合同不变。r1/r2历史原样，无继承批准。
- Human Owner对精确r3范围批准：**已取得**；下一gate为实际Development，不需重复询问未变化的r3范围。
- Development/tasks/代码/产品测试/原生观察：**未发生**。
- 新fresh-context Verification/checklist/verdict：**未发生**。
- Human Owner最终验收：**pending**。

PM仅核当前引用/入口及本spec身份、R↔AC/例表/allowlist/角色权威、现有链接、r1/r2全文归档与004/005保护SHA，不是产品QA或DEV self-check；本轮没有运行Cargo/测试/原生。r2文档before保留于 `/private/tmp/daa-006-r2-spec-wxtwzx9l/baseline.json`，当前r3 fresh1694文件before由coordinator固定在 `/private/tmp/daa-006-r3-spec-83zdc53u/baseline.json`，不重设已有事实。最终SHA由外部handoff给出，避免自引用。完整文档检查结果随PM交接报告；机械索引仅由coordinator同步。

## 11. Skill 路由与正式 handoff

| 批准后真实表面 | 对应角色需使用的skill |
| --- | --- |
| 点位/DB/UDT/布局/命名/原oracle | `plc-point-mapping`，保留本spec明确GUI→SQLite偏离通用XLSX/YAML SOP的选择。 |
| Rust核心/DTO/服务/来源证明/有界缓存/日志 | `rust-runtime`；无I/O核心与runtime adapter分层，遵循其语言无关工程标准。 |
| 新增P0b/R14配置helper/既有isolation_tests及编译诊断 | `rust-runtime`；仅config/mod.rs六symbol有限清理，保留配置/feature/入口边界，不用lint压制或扩成退役源治理。 |
| Tauri具名IPC/普通原生增量观察 | `desktop-tauri` + `rust-runtime`，不扩capabilities或真实传输权限。 |
| 前置R13两组件/故障Dialog、后续点位页/组件/弹窗/分页 | `frontend-ui`（适用DESIGN/FRAMEWORK）；可见文案同时`i18n-workflow`，P0不改owner/Rust机制。 |
| 新文件头/实际职责与CODE_INDEX | `code-document-indexer`，只触达§7有限面。 |
| task/共享目录治理、跨工程边界 | `project-governance` + `aiis`；保持唯一bundle/各角色事实owner。 |

精确 **aiis-ics-arch::DAA-006 r3 已获Human Owner范围批准**，交唯一coordinator `/root` 启动实际Development，无需重复请求未变化的r3批准。依原合同先P0a入口核对/正常展示收尾，再P0b四组warning六symbol清理，随后原命名/共享实施；developer_handoff后必须新fresh-context Verification；qa_passed后Owner决定最终验收。PM本轮只记录批准并完成文档/正文不变核对，停止全部写入，不执行后续实现/测试、不代批DS、不发送跨线程消息、不自行调用角色；10索引同步与实际Development调用归coordinator。
