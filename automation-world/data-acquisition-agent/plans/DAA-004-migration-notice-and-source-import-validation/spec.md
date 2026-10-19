Task ID: DAA-004
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved exact DAA-004 r1 on 2026-10-19; sole coordinator /root hands the unchanged approved scope to actual Development, then new fresh-context Verification and Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: DAA 一次性迁入说明归档、日常配置界面收敛及最小 DB/UDT 普通原生导入闭环验证
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: aiis-ics-arch::DAA-004 r1 exact scope approval -> Development -> new fresh-context QA / Verification -> Human Owner final acceptance
Related Task: aiis-ics-arch::DAA-003 r1; aiis-ics-arch::DAA-002 r2

# 一次性迁入提示收敛与最小源码导入验证

## 1. 当前效力与决定

**最新批准与当前效力（2026-10-19，Asia/Shanghai）：** Human Owner 已明确批准精确 **aiis-ics-arch::DAA-004 r1**，批准前草案 SHA-256 为 `5ee40a1b1e18ef3955c30073d6a91e3b620ddbf3523090d2b485351d6d9ca67a`。唯一 active lifecycle coordinator `/root` 真实传递原话：

> 可以，批准 DAA-004 r1，按 spec 补齐中英文 README、移除常驻迁入卡片，并完成 DB/UDT 导入验证和独立核验。先用受控样例，SQLite 防重复记录、已有配置和历史不动，只做必要增量验证，不重复整套测试，阶段 C 暂不做。

当前状态为 `owner_approved`，G0 范围批准已满足，按既有默认受控样例实施。本次只补真实批准、状态和 handoff；R01–R08、AC01–AC08、16 个实现路径、10 个协调索引及全部风险/排除条款保持原样，不代表实施、QA 或最终验收已发生。当前批准记录证据仅写 `/private/tmp/daa-004-r1-hppdbt2h/pm/`；下文 §4 的旧 PM 辅助路径保留为起草阶段事实。

起草背景：Human Owner 先前要求是：

> 可以，把这套示例配置和迁入说明补到 DAA 的中英文 README，移除 PLC 配置页的常驻迁入卡片，SQLite 防重复迁入记录保留，已有配置和历史不动。先出调整 spec，批准后再改代码。db和udt是不是没有测试，我要不要搞两个简单的过来测试一下？也一起放到同一个关于移除一次性任务的spec？

本 r1 将两件事放在一个有边界的调整任务中：稳定说明归 DAA README；日常界面撤下常驻大卡片，并补一次最小 DB 引用 UDT 的普通原生导入观察。“移除”只针对常驻展示，不删除迁入器、SQLite 私有回执、初始化保护或显式安全重试。

本任务是独立 `independent_fix`，无 Parent Task ID。DAA-003 r1 与 DAA-002 r2 均为 `qa_passed`、Human Owner 最终验收 pending；它们提供当前技术基线，不提供本任务批准、QA 或终验。本请求也不构成这两个任务的最终验收。唯一 active lifecycle coordinator 为 `/root`；实际 PM 为 `/root/daa004_pm`。PM profile 为 `contract_only`；实际 PM TOML 的 `gpt-6.1-sol / max` 仅是配置证据，不宣称角色文件 ACL、强制路由或团队激活。

起草阶段仅新增本 spec 并做文档自检。本次 PM 只记录批准事实；不创建 tasks/checklist、不改产品或夹具、不运行产品构建/测试/SQL/native/PLC/API，不自行启动 Development、Verification、通知窗口或邮件。下一 gate 是由唯一 coordinator `/root` 将精确获批 r1 交实际 Development。

## 2. 当前依据与证据边界

PM 已消费根 AGENTS/README/PLAN 双语、AW/DAA 最近 README/PLAN 双语、app/local_store/现有 fixture 说明、canonical workflow、实际 PM TOML、完整 DAA-003 三文件，并核对 DAA-002 当前 QA4 AC06/AC07、现行测试和受影响前端/导入接线。作用域检索无更近 AGENTS。应用 `aiis`（含现行状态/跨端责任合同）与 `project-governance`；专门技术工作按 §8 交后续角色。

入口：[根契约](../../../../AGENTS.md)、[生命周期 workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)、[DAA README](../../README.zh-CN.md)、[DAA PLAN](../../PLAN.zh-CN.md)；DAA-003 的 [spec](../DAA-003-sqlite-only-startup/spec.md) / [tasks](../DAA-003-sqlite-only-startup/tasks.md) / [checklist](../DAA-003-sqlite-only-startup/checklist.md)；DAA-002 的 [spec](../DAA-002-local-acquisition-loop/spec.md) / [tasks](../DAA-002-local-acquisition-loop/tasks.md) / [checklist](../DAA-002-local-acquisition-loop/checklist.md)。本任务后续角色文件尚未形成，不提前建链接。

| 本轮只读核实的基线 | SHA-256 / 当前事实 |
| --- | --- |
| DAA-003 r1 spec | `bbee28344d140772340fa62ec3c7bde4fae2df09655044e6e3d5bffae24b1ef3` |
| DAA-003 tasks | `daeeac99cc302a9b976063b84e054e190d3c8d04a2d7a4ad178baca3865edcfb` |
| DAA-003 checklist | `d17a492632551f8ab20094e182f97ce2cf8d6bd0aae62077163e2552b3b39430`；QA2 通过，F-001/F-002 已解除、失败历史保留。 |
| DAA-002 r2 spec / tasks / checklist | `681b912b9920fa9ecc8ff6c22c23d2e9fb9a4aa31a761589ee1290173846681a` / `d5847fb57ded32e2419e508d0c47e74ccd3f06a11e7e8e920b19fa5e704a69a6` / `6427e2c3030d33b255bc005625b03651a4fdfc5618721ee946228e1dc731ca37`；QA4 与全部原始历史不改。 |
| 工作树 / 保护基线 | HEAD=`f85bea8bbf36b491968c3dc9a839518a1ed434a8`；当前大量既有 dirty/untracked 不是本任务增量。`/private/tmp/daa-004-spec-9qwsuxiz/baseline.json` 固定 1673 个公开路径，另固定 `flat.db` / `nested.db` / `invalid.db` 三个被忽略的公开 fixture 字节；不以 HEAD 替代当前 before。 |

现行 `diagnostics/index.vue` 在 PLC 页顶部挂载 `YamlMigrationNotice`；组件只要有 migration 摘要就显示整张 ConsoleCard，成功历史也常驻。全局 `ConfigRevisionBar.vue` 已有一个默认折叠的原生 `details`“运行配置与版本详情”，可承接历史详情，无需新页面或新框架。

DB/UDT 并非未测试：`local_store/tests.rs::offset_and_full_structure_golden` 覆盖 flat 的 12 叶 BOOL 打包/BYTE/INT/REAL 与独立 offsets golden、长度 10；nested DB+UDT 展开 ARRAY[-1..1]、ASCII STRING 共 7 叶且默认 disabled/unassigned/address-none，并拒绝复杂布局推算；invalid 覆盖多维数组定位。`public_save_cannot_forge_source_proof_and_preview_ids_match_confirm` 覆盖真实 LocalEngine 预览/确认相同 ID、公共 save 的来源证明保护及手工地址保存。DAA-002 QA4 AC06/AC07 已核这些 golden 与 9 个 file/line/path 拒绝原输出。它们不是本轮 rerun、全 TIA 编译或现场地址证明，也不能代替从当前普通界面实际选择一对新文件的专项观察。

## 3. 编号需求

### R01. 独立批准与有限增量

精确 r1 获批后才由实际 Development 创建 tasks 和实施；固定批准 SHA、完整 before/after、依赖与保护面，保留他人所有 dirty/untracked。范围、allowlist、验收或风险实质变化停止相关写入，回 PM 新 Revision。旧 bundle/失败记录/76 原样本和独立终验链保持；不把本次 QA 变成 DAA-002/003 的终验。

### R02. 双语 README 记录具体示例与迁入说明

在 DAA `README.md` / `README.zh-CN.md` 的既有迁入章节补齐下表，明确这是仓内默认脱敏 YAML 的内容。进程/env 可覆盖来源，故不能把默认示例冒称用户当前 profile 实际迁入清单；本任务不读取真实实例来推断其状态。

| 默认示例项 | 必须说明的值 |
| --- | --- |
| PLC / 连接候选 | `PLC_1`，`127.0.0.1:102`，rack 0 / slot 1。 |
| DB / 组 / 旧读取窗口 | DB1，`example_group`，start 0 / size 12，3 点；窗口不是完整 DB 长度证明。 |
| 点 1 | `example_value`，旧类型 `Real`，offset 0。 |
| 点 2 | `example_status`，旧类型 `Bool`，offset 4 / bit 0。 |
| 点 3 | `example_counter`，旧类型 `DInt`，offset 8。 |
| 退役策略示例 | 3 点均 raw/latest=true、raw_policy=`every_sample`；仅白名单归档说明，不转成新采样/上报/直库规则。 |

说明没有采样值或历史；首次空实例仅迁入停用、地址未确认、DB 不完整的候选。已有 SQLite 配置/历史优先，成功/空结果的私有 receipt 阻止自动重复扫描；源 YAML 不改。交代 YAML 一次性来源、SQLite 业务权威、`.db/.udt` 显式编辑导入的区别、迁入历史/安全重试的新位置，以及既有完整源预览/地址审阅流程。不得提供“删库/删 receipt 重新迁入”教程，不复制凭据或真实输入。保持中英文内容一致，仅更新本任务触达的稳定说明。

### R03. 从 PLC 主内容撤下常驻卡片，复用现有折叠详情

固定 UI 方案如下，不留可选分支：

1. `diagnostics/index.vue` 去掉 `YamlMigrationNotice` 挂载与导入。`ConfigRevisionBar` 的既有 `details` 保持默认关闭；在其内容内挂载改造后的 `YamlMigrationNotice`，作为有界迁入历史/重试区。组件去掉外层 ConsoleCard 与内层新增折叠，不新增独立页面、第二张迁入卡片或另一套详情容器。
2. 配置栏外侧只按下表显示一条紧凑提示和“查看迁入详情”入口；入口只打开同一个既有 `details`，不请求重试、不保存、不激活。正常成功、空来源、仅策略、已有 SQLite 等状态不占 PLC 主内容；不自动打开历史详情。

| 现有权威字段 | 折叠区外的表现 |
| --- | --- |
| `statusPersistence === 'unknown'` | 紧凑未知状态提示，说明不能宣称已持久记住、按现有修复/重开说明处理；可打开详情。 |
| `status === 'failed' && retryAllowed === true`，且非上述 unknown | 紧凑迁入失败提示，可打开详情；实际重试仍在详情内。 |
| 持久 failed 且 `retryAllowed === false` | 只保留历史详情；用户后来保存非空配置后，不永久把旧失败显示为当前故障。 |
| `imported` / `imported_with_diagnostics` / `skipped_empty` / `archived_policy_only` / `existing_sqlite_preserved` / `validation_excluded` | 只保留可展开的历史说明，无常驻大提示、无自动重迁。 |
| 摘要为 null（查询中或查询失败） | 不使用旧摘要渲染动作；保留配置栏现有真实 error/已保存但摘要未加载语义，不伪造新迁入状态。 |

3. 详情明确标成“迁入时记录”，保留既有有界来源/计数/诊断/attempt 等信息。`imported_with_diagnostics` 表示迁入时留有诊断，不能永远宣称当前配置仍待复核；迁入时全部停用/不完整的说明也不能冒称用户后续编辑后的当前配置状态。一般操作 `failed` 仍为一般“失败 / Failed”，迁入专用失败文案只用于迁入上下文。
4. 重试仅消费 Rust 返回的 `retryAllowed`；原 `busy || dirty || editing` 禁用、先保存/取消编辑、ETag/attemptId 双 CAS 和失败处理保持。成功或非空实例不出现覆盖动作。只做展示重定位和文案收敛，不改 owner、刷新时钟、IPC、Rust 状态机或重试准入。

### R04. 保存已有配置、历史与防重复迁入合同

迁入 adapter/service/repository、私有 `__daa_yaml_migration_v1__` receipt、source 裁剪保护、已有 SQLite 优先、首次空资格、schema/ledger/事务/门禁/驱动/来源发现完全保护。现有真实 `.env`、YAML、profile、SQLite、配置与历史不读不写；不删除、重建、迁移或清空任何已有实例。新 UI 不因为收起历史而改变 receipt 或重扫源。

`useLocalAcquisitionConsole` 保持原字节：保存成功后清旧摘要再查询权威状态、查询失败仍承认保存成功、未保存输入/CAS 冲突保持、后台刷新不替换编辑 ETag。原 DAA-003 F-001/F-002 解除保护均须在新组件位置继续成立。受控原生验证只对本任务新建 tmp profile 做普通配置 DML；runtime 的 active/样本/投递/来源身份保持空，不运行连接或采集。

### R05. 一对明确的受控 DB/UDT 与独立期望

默认实施输入无需等待 Human Owner 文件：获批后才在 §4 的精确 fixture 位置新增一对 UTF-8 脱敏文本，`minimal.db` 声明 `DATA_BLOCK "MinimalImport"`，显式标准访问，并以唯一字段 `payload` 引用 `"MinimalPayload"`；`minimal.udt` 定义该 UDT 的三个简单叶字段。界面明确填写 `.db` 的 `dbNumber=21`，不从声明名猜编号。

| 固定 sourcePath | 类型 | 新导入默认期望 |
| --- | --- | --- |
| `payload.ready` | `BOOL` | `enabled=false`、`groupId=null`、`address=null`。 |
| `payload.count` | `INT` | 同上。 |
| `payload.temperature` | `REAL` | 同上。 |

独立 `expected.json` 由本表和人工审阅声明先行编写，不能由被测 parser/preview 反向生成；它是验证清单，不是运行时配置。固定 2 个编辑来源、1 个 DB、3 个点、0 个组；来源/DB/点均绑定实际所选的同一 PLC ID，DB number=21、complete=true、flat=false，有完整引用展开树。只检查地址未确认，不给 UDT 推算 offset 或把默认 length 当实证长度；现有 complex 拒绝辅助布局边界保持。UUID 实际值由服务产生，独立期望检查引用关系和后续稳定性，不预填随机 UUID。

fixture 双语 README 说明其归 DAA PLAN、本任务验证用途、固定期望、手写来源和限制；手写样例只称“受控源码导入验证”，不称 TIA 实际导出兼容、PLC 地址或真实设备验证。`.gitignore` 只为本任务的一个 `minimal.db` 精确路径增加 negation，保留 `automation-world/**/*.db` 及 SQLite/用户数据库普遍忽略规则；不顺带放开原三个 ignored fixture、不追认旧交付。

若 Human Owner 后续提供 TIA 脱敏导出对，先只读审查格式/脱敏和现有语法支持，固定采用的精确路径、SHA 与独立叶表，再决定是否在“一 DB 引用一 UDT、3 个 BOOL/INT/REAL 简单叶、既有支持范围与同一闭环”内采用并记录在 tasks。未提供不构成 blocker；不安装 TIA、不改 parser 迁就输入。扩大语法、类型、布局、叶数或兼容目标，须回 PM 新 Revision。

### R06. 一次最小普通 native 导入闭环与必要反例

只用本任务新建归属明确的绝对 tmp `DAA_ENV_FILE` / `DAA_PROFILE_DIR`，移除继承的业务覆盖；read gate=false，两个 YAML 来源显式指向自身空文件，避免默认示例干扰。普通 `pnpm tauri dev` 无 `local-validation`/fixture feature、默认不编 Snap7 驱动。15191 若被用户窗口占用，只能为自己的进程使用 tmp Tauri override 的 dev port/devUrl，记录与普通配置的差别；不停止现有窗口、不改产品端口。

一次观察覆盖：新建并保存一台停用的 loopback PLC → 在点位页经现有 `<input type=file accept=".db,.udt" multiple>` 实际选择文件 → 明确 `.db` 编号 → 预览 → 确认导入即持久保存 → 重载。完整配对、预览无 issues 时才按本验证流程确认。预览阶段草稿/ETag/active 不变；确认后新 ETag、固定 3 叶/2 来源/1 DB、引用及默认状态符合 R05；重载后同库来源原文 SHA、source/DB/point ID、PLC 绑定和 ETag 稳定，私有空来源 receipt 原字节保持。现有真实 LocalEngine 预览/确认同 ID 的定向测试提供补充，不能拿纯函数或编译替代本次实际文件选择。

只补必要反例：仅选择 DB 而缺其 UDT时有明确定位诊断；此错误预览本身不自动提交；取消文件选择或确认对话框不写草稿/active、不部分提交来源/点。**当前 confirm 可以保存带诊断的候选草稿，本任务不新增 confirm 拦截、不修改该草稿语义，也不承诺所有来源 issues 必然阻断激活。** 本验证不确认带 issues 的预览，不执行激活或其门禁试验。若实际观察发现额外实现问题，记录事实并回 PM 定义新的获批范围，不把 parser/保存服务扩进本 r1。

不重复退出重开、EN/深色/窄窗、采样/历史/容量/Snap7 等阶段 B 矩阵；正常结束并盘点自己的进程。工具确实不能取得 native 观察时，可按原 R19 同类方式由 Owner 一次实际操作加同库证据补足；不预设多轮人工清单，不使用假 bridge/fixture 冒充原生。必要证据确实缺失则如实 `qa_blocked`，不降格为通过。

### R07. 与改动匹配的检查

新 UI 只验证 R03 的状态分支、打开同一详情、双语历史/普通失败语义和原编辑/重试 guard；使用现有 Vue/compiler/函数能力在 task tmp 做定向检查，不安装框架或新增长期 mock。保留保存成功但摘要查询失败无旧动作、仍空可重试、保存非空无重试等原反例，按实际源/hash/raw 核用原未变 owner/Rust 证据。

Development 在 tasks 固定实际命令、cwd、环境、退出码与 raw：前端 `pnpm build --config vite.validation.config.ts --outDir <本任务绝对tmp-dist> --emptyOutDir`；现有两个 Rust 定向函数 `offset_and_full_structure_golden`、`public_save_cannot_forge_source_proof_and_preview_ids_match_confirm` 可按当前源码与原输出核用，若运行则只过滤这两个并用既有 Cargo/锁文件及自有 tmp target。新增输入的原生闭环另按 R06 记录；不以旧测试冒称测试过新文件。所有检查先核无外发边界，不运行旧 B 全套、native transport 或任意真实 SQL。

### R08. 文档与串行交接

仅更新 §4 允许的 DAA README/app 说明 pair、common 双语键与 CODE_INDEX 的真实 DAA 局部说明。Development 写 tasks，给出完整增量 diff（含 untracked 新文件全文）、R↔AC 对应、批准 SHA、旧 bundle/保护面审计和资源清单后 `developer_handoff`；随后由唯一 coordinator 启动新的实际 fresh-context Verification（工具支持时 `fork_turns="none"`），只验证和写 checklist。失败回 Development；实质范围变化回 PM 新 Revision。`qa_passed` 后只进入 Human Owner 最终验收，不授权部署/发布/真实配置迁入或旧任务终验。

## 4. 封闭 allowlist 与角色权威

下表是 **精确 r1 范围批准之后** 才可交 Development 的全部实现面。除标明仓根外，路径相对 `automation-world/data-acquisition-agent/`。M=既有最小修改，N=新文件，D=删除；未使用 M 不必改，M 不授权删/移；N 若已存在或需要额外路径，先回 PM。**D 为空**，没有产品文件删除或迁入机制退役。

| 操作 | 精确路径 | 唯一用途 |
| --- | --- | --- |
| M | `src/app/plc/views/diagnostics/index.vue` | 去掉迁入卡片挂载/导入及对应头部描述。 |
| M | `src/components/console/ConfigRevisionBar.vue` | 在原 details 内承接组件；有限外侧提示/打开同一详情。 |
| M | `src/components/console/YamlMigrationNotice.vue` | 改成折叠区内的有界历史/重试内容，移除独立卡片/内部额外折叠。 |
| M | `src/locales/zh-CN/common.json` | 本任务提示/历史措辞，保通用 failed 与既有稳定码。 |
| M | `src/locales/en-US/common.json` | 对称英文键/占位符/语义。 |
| M | `README.md` | R02 具体示例、机制及新位置，链接已形成示例。 |
| M | `README.zh-CN.md` | 对称中文。 |
| M | `src/app/README.md` | 迁入展示位置与既有 owner/导入责任说明。 |
| M | `src/app/README.zh-CN.md` | 对称中文。 |
| M | 仓根 `.gitignore` | 仅新增 `!automation-world/data-acquisition-agent/src-tauri/tests/fixtures/source-import-minimal/minimal.db`，不改既有忽略项。 |
| M | 仓根 `CODE_INDEX.md` | 仅本次真实 DAA 组件职责/fixture 条目。 |
| N | `src-tauri/tests/fixtures/source-import-minimal/minimal.db` | R05 的唯一受控 DB 文本。 |
| N | `src-tauri/tests/fixtures/source-import-minimal/minimal.udt` | R05 引用的唯一 UDT 文本。 |
| N | `src-tauri/tests/fixtures/source-import-minimal/expected.json` | 先行独立的结构/默认值/引用关系期望。 |
| N | `src-tauri/tests/fixtures/source-import-minimal/README.md` | 结构性 fixture 说明，不新增独立 PLAN。 |
| N | `src-tauri/tests/fixtures/source-import-minimal/README.zh-CN.md` | 对称中文。 |

| 角色 / gate | 仓根相对精确路径 | 权威 |
| --- | --- | --- |
| PM / Human Owner | `automation-world/data-acquisition-agent/plans/DAA-004-migration-notice-and-source-import-validation/spec.md` | 本轮唯一 PM 写入；以后真实范围/Revision/批准记录。 |
| Development，批准后 N | `automation-world/data-acquisition-agent/plans/DAA-004-migration-notice-and-source-import-validation/tasks.md` | 实施/DEV self-check/精确 handoff。 |
| 新 fresh-context Verification，handoff 后 N | `automation-world/data-acquisition-agent/plans/DAA-004-migration-notice-and-source-import-validation/checklist.md` | 独立证据/verdict 与真实 Owner 终验。 |

以下 10 个索引只归 coordinator `/root` 在角色事实存在后机械同步本任务行/指针/阶段，不由 PM、Development 或 Verification 写；不把后续未形成文档写成已有链接：

| 操作 | 仓根相对精确路径 |
| --- | --- |
| M | `PLAN.md` |
| M | `PLAN.zh-CN.md` |
| M | `plans/README.md` |
| M | `plans/README.zh-CN.md` |
| M | `automation-world/PLAN.md` |
| M | `automation-world/PLAN.zh-CN.md` |
| M | `automation-world/data-acquisition-agent/PLAN.md` |
| M | `automation-world/data-acquisition-agent/PLAN.zh-CN.md` |
| M | `automation-world/data-acquisition-agent/plans/README.md` |
| M | `automation-world/data-acquisition-agent/plans/README.zh-CN.md` |

其余均保护：特别是 `useLocalAcquisitionConsole.ts`、`localAcquisition.ts`、`App.vue`、点位页、全部 Rust 实现/测试、原 fixture/expected/marker、两个 YAML 示例原字节、`.env.example`、真实 env/profile/库、依赖/锁文件、Tauri 配置/capabilities、旧 bundle/设计、根治理/角色/workflow/skills，以及 CU/CA/SMA/DS/backend/frontend-js/tools/contracts。PM 辅助文件只写 `/private/tmp/daa-004-spec-9qwsuxiz/pm/`；获批后 DEV/QA 分别新建自有系统 tmp 证据区，不改旧资源或向其他工具目录传递输入。

## 5. 实施顺序与验收

| 阶段 | 完成条件 | 对应 |
| --- | --- | --- |
| G0 | Human Owner 于 2026-10-19 明确批准精确 DAA-004 r1；已满足。 | R01 / AC01 |
| S1 | 固定完整 before → README 具体示例/说明 → 原卡片撤下并复用详情。 | R02–R04 / AC02–AC04 |
| S2 | 独立 expected 先行 → 新小样例/双语说明/唯一 ignore 例外 → 定向 UI 检查与构建。 | R05/R07 / AC05/AC07 |
| S3 | 一次受控普通 native 导入/取消/重载与同库证据 → 完整 diff/资源/DEV handoff。 | R06/R08 / AC06/AC08 |
| G1 | 新 fresh-context Verification 独立审查精确 handoff；失败返工后重新交接。 | R01–R08 / AC01–AC08 |
| G2 | qa_passed 后由 Human Owner 决定本任务终验，旧任务终验独立。 | R08 / AC08 |

以下均为批准后的义务，当前没有实施或 QA pass 事实：

| AC | 可核完成条件 | 必要证据 |
| --- | --- | --- |
| AC01 | 独立身份、精确批准、有限增量与角色顺序成立，DAA-002/003 原链不升格。 | 批准 SHA、当前 before/after/新增全文、16 实现路径与10协调索引分权、旧 bundle/三 ignored fixture/其余保护 hash。 |
| AC02 | README 双语具体示例与 R02 全项一致，区别默认源码与实际实例，文件角色/保留/重试位置准确。 | 双语对读、3 点/策略逐项对照原 YAML；无真实输入、采样值或“删 receipt 重迁”说明。 |
| AC03 | PLC 主内容无常驻迁入卡片；只复用原默认关闭 details；外侧提示严格按 R03 两条件，历史状态不冒充当前故障。 | 实际组件/页面挂载及定向状态渲染：unknown、failed/retry true与false、成功/空/已有、null；展开入口只打开同一详情，中英文历史/通用 failed 正确。 |
| AC04 | receipt/初始化/现存配置历史与 owner 原字节保持，编辑/双 CAS/保存后摘要异常保护不退化。 | 全量保护审计、原对应 hash/raw核用；新组件位置下 busy/dirty/editing 与无旧摘要动作检查；只对新 tmp 实例取证。 |
| AC05 | 新受控 pair 与先行独立期望一致，正确展开3叶/引用/default；复杂布局不新增支持，ignore只放行一个新DB路径。 | 原声明/expected人工独立对读、SHA、git check-ignore精确正反例、旧fixture字节；若采用Owner输入另有只读兼容/脱敏结论与冻结清单。 |
| AC06 | 实际普通 native 文件选择→编号→预览→完整pair确认保存→重载成立，缺UDT有诊断、预览/取消无自动提交。 | 一次真实操作观察和同一自有库前后/重载对账、ID/ETag/sourceSHA/PLC关系；私有receipt不变，active/runtime业务表空。端口override与工具限制如实写明，函数/fixture不冒充native。 |
| AC07 | 只做必要 UI 分支、前端构建、已有解析/proof原证据核用及新输入闭环，命令和未执行边界真实。 | 实际argv/cwd/exit/raw、locale键/占位符/链接；原golden不冒称新文件测试，不扩大B矩阵或依赖。 |
| AC08 | README/app pair/i18n/CODE_INDEX与实际改动一致；完整DEV handoff→新fresh QA→Owner终验分层，资源归属明确。 | 角色文件实际gate、R↔AC、完整diff/有限allowlist/保留资源；无旧bundle/用户窗口/真实数据修改。 |

## 6. 风险、恢复与排除

| 风险 / 取舍 | 处理与恢复边界 |
| --- | --- |
| 旧历史被解释为当前状态，或收起详情导致故障不可发现 | 用 R03 精确可见性与历史措辞；unknown/仍可处理的failed保留紧凑入口，安全重试在同一详情内。 |
| 小样例被包装成 TIA/offset/现场兼容承诺 | 明示手写来源、独立3叶期望、non-flat/地址未确认；不推算 UDT 地址，不扩 parser、布局或激活语义。 |
| `.db` 通用忽略误伤示例或顺手放开实际库 | 只放行唯一新文本DB路径，旧3 fixture和SQLite/用户数据库忽略保持；不自动stage/commit。 |
| native自动化不可用、端口被占用或额外实现疑点 | 保留真实限制，只操作自有tmp/端口；允许一次Owner实际操作＋同库证据。缺必要证据则blocked；额外产品修复回PM获批范围。 |

回退只针对本任务自己的 UI/文档/新示例增量，须按完整 diff 保护他人改动并遵循具体回退授权；**不得把删除/修改 SQLite receipt、数据库、历史或原 YAML 当回退方案**。测试失败保留证据，不清库掩盖；停止并正常释放自己的进程，由 coordinator 在实际归属/证据依赖确认后盘点资源，不删未知锁或停止他人窗口。

明确排除阶段 C、上传/ACK、Backend/SMA/DS 联调、真实 PLC/实际配置迁入、真实 profile/生产 DB/API/现场、数据库 schema/ledger/迁入服务改造、来源发现/门禁/驱动变化、全 TIA 兼容/复杂布局、依赖/测试框架、长期采样/容量/跨平台签名、Docker、Git refs/提交/推送/发布/部署。旧设计/QA历史保持。真实TIA导出兼容与现场地址核验可另立范围，不阻断默认受控样例起草/实施；本次必要native导入证据不能延期后仍称通过。

## 7. 修订与批准历史

- 2026-10-19，r1 draft：只整理本次 UI 收尾、README 示例说明和最小源码导入观察；无继承批准/终验。
- 2026-10-19，r1 owner_approved：Human Owner 按 §1 原话明确批准草案 SHA-256 `5ee40a1b1e18ef3955c30073d6a91e3b620ddbf3523090d2b485351d6d9ca67a`；只补批准事实和当前 handoff，不改变需求、验收、allowlist 或风险范围。
- Development / tasks / 产品与夹具变更 / self-check / developer_handoff：**未发生**。
- 新 fresh-context Verification / checklist / verdict：**未发生**。
- Human Owner 最终验收：**pending**；DAA-002/003 自身最终验收仍独立 pending。

## 8. Skill 路由与 PM handoff

| 后续实际表面 | 对应 Development / Verification skill |
| --- | --- |
| 现有 Vue 组件定位、详情/紧凑提示/编辑guard | `frontend-ui` 的适用 DESIGN/FRAMEWORK；复用现有 CU 视觉系统。 |
| 用户可见历史/失败/unknown提示与双语说明 | `i18n-workflow`；通用失败与迁入上下文分开。 |
| 最小DB/UDT输入、叶点/PLC引用/地址未确认边界 | `plc-point-mapping`；不扩大偏移或语法支持。 |
| 普通Tauri启动、原生文件选择、tmp隔离及同库证据 | `desktop-tauri` + `rust-runtime`；只消费现有实现，不新增Rust业务/SQL入口。 |
| 真实局部结构说明、头部与CODE_INDEX | `code-document-indexer`，仅§4有限面。 |
| 独立任务、角色链与机械索引 | `aiis` + `project-governance`。 |

PM 自检仅为元数据、独立分类、现有引用/旧SHA、R01–R08↔AC01–AC08、16精确实现路径/零删除/10索引分权、必要边界及仅新增spec的文档/保护审计；不是DEV self-check或独立QA。辅助附件只存本任务 `pm/` 系统tmp，最终spec SHA由交接消息给出，不自引用。

正式 handoff：精确 **DAA-004 r1** 已获范围批准，交唯一 coordinator `/root` 顺序启动实际 Development，消费本 spec、完整已形成 bundle、批准前后 SHA 和当前工作树 before，在原有限面实施并形成精确 developer_handoff；之后由 coordinator 启动新的 fresh-context Verification，最后 Human Owner 决定终验。PM 完成本次有限状态更新自检后停止全部写入，不改索引/后续角色文件/产品，不自行启动角色或通知，不补发历史邮件。无需再次请求本 r1 范围批准，DAA-002/003 的最终验收仍各自 pending。
