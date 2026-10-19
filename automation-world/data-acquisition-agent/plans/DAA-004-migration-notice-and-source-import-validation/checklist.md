Task ID: DAA-004
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: 独立 Verification 已核验精确 DAA-004 r1 developer_handoff；交唯一 coordinator /root 转 Human Owner 最终验收，保留 R06 操作差异与全部证据；本角色停止写入
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-004 r1 独立验证

## 1. 结论与权威边界

2026-10-19，独立 verdict 为 **`qa_passed`**。AC01–AC08 的本任务目标证据充分；没有发现需要 Development 返工的产品问题或未解除的必要验证 blocker。AC06 保留一次明确的操作程序差异：首台 PLC 第一次保存为 `enabled=true`，同轮在导入前改回 `false`，不是“第一次就停用”。本节结论不覆盖或删改该原始事实，具体判定见 §5。

Human Owner 最终验收 **pending**。本结果只覆盖有限 README/展示收敛、受控手写 DB/UDT 导入观察与保护面审计，不是 DAA-002/003 的终验，也不授权阶段 C、真实 PLC/实际配置迁入、Backend/SMA/DS 实现、生产 DB/API、上传/ACK、发布、部署或 Git 操作。

实际 Verification 为 `/root/daa004_verification_1`，由唯一 coordinator `/root` 在实际 Development `/root/daa004_development` 正式 `developer_handoff` 并停止写入后，以 `agent_type=verification`、`fork_turns="none"` 调用。此上下文不继承 Development 的对话推理；从批准 spec、完整 tasks、当前实现、基于实际 before 的完整增量 patch 和 raw 独立开始。`.codex/agents/verification.toml` 的 `gpt-6.1-sol / max` 是已读取的配置证据，不冒称独立观测到的运行参数。本 profile 为 `contract_only`，不宣称平台 ACL、强制路由或团队激活。

仓内本角色只创建本 `checklist.md`。未修改 spec/tasks、实现、测试、fixture、配置、依赖/锁、角色/skills 或10个协调索引；未修复/回退任何产品内容，也未委派其他 agent、发邮件、回收资源或操作用户窗口。

## 2. 精确输入与独立审计

阅读顺序包括根 `AGENTS.md`、根 README/PLAN 双语、canonical workflow、actual Verification TOML，随后 AW/DAA README/PLAN、DAA app、local_store 和相关 fixture 的双语说明及本任务完整 spec/tasks。作用域检索无更近 `AGENTS.md`。应用 `project-governance`、`aiis`、`frontend-ui`（适用 DESIGN/FRAMEWORK，复用现有 CU）、`i18n-workflow`、`plc-point-mapping`、`desktop-tauri`、`rust-runtime` 与 `code-document-indexer`，仅用于验证现有边界。

| 验证输入 | 精确 SHA-256 / 事实 |
| --- | --- |
| Human Owner 批准前 spec | `5ee40a1b1e18ef3955c30073d6a91e3b620ddbf3523090d2b485351d6d9ca67a`；批准原话见 [spec §1](spec.md)。 |
| 当前 PM 批准记录版 spec | `c84c93612e828578f0a4a3beaa406642b7fe7401624f1af71276a470cc1d5a8e`。独立对比确认 R01–R08、allowlist、AC01–AC08、风险/排除正文原样，仅批准/状态/handoff 增量。 |
| 当前 Development tasks | `947486ea31708053fca84132a9d380d3f94396bc03c45b6929e4ea6fc23a2f21`；最新效力为 [tasks §7](tasks.md)，§4–§6 的等待/误关窗历史保留。 |
| 原 before | B=`/private/tmp/daa-004-r1-hppdbt2h`；`baseline.json` SHA=`ddd6bea54ef6320c40d134f784685cac24185fdaa2e49cc421dd85f22d404712`，有 before 副本及3个旧 ignored DB 字节；没有用 HEAD 代替 dirty before。 |
| Handoff receipt | H=`B/dev/final-handoff`；`developer-handoff-receipt.json` SHA=`991ef78b7c3dabef2c21e72f0011d201764f2d74ba043cf917875dec28b5356f`。 |
| Development manifest | H/`development-manifest.json` SHA=`3ce3844f3708882625230003f8bfac5fbbbacbee9b13c93557eec69face0937d`。 |
| 完整增量 patch | H/`development.patch` SHA=`13ebfa911c65b93db35c18f71008ca754641f8ea2c88c984715c4fc9444aea16`；独立从17份 before/after 重建，与全文精确相等，含5个新 fixture 和 tasks 全文。 |
| Evidence manifest / commands | H/`evidence-manifest.json` SHA=`d24be22424ad4e137bf67ad0e1272b7eaaeeb75af145f5c5b3e549816ed9e520`；H/`commands.json` SHA=`8ad11dd420f4fd16fb6ca301e818ffb38340caa222ba47fd9649004f82996aaa`。174个封存附件及10个只读外部引用共184份均重新核字节数与 SHA。 |
| coordinator 补充原话 | B/`owner-native-completion-relay.json` SHA=`0854d8ca568103cd209400d31266452d4b9a6ce444da5ea4ac1fd8e29a7904fd`；直接 Owner 消息“五步操作都没问题”，含额外辅助偏移尝试；与 Developer relay 分开消费。 |
| HEAD / 交接工作树 | `f85bea8bbf36b491968c3dc9a839518a1ed434a8`；本次增量处于既有 dirty working tree，没有 commit/push。 |

QA 自有证据 Q=`/private/tmp/daa-004-r1-qa1-cvksrgrl`。`static-audit.json`、`native-and-reuse.json`、`approval-scope.json` 及对应脚本、stdout/stderr/result 固定本次独立检查。Python 3.9.6/macOS 只作标准库控制器，不冒称项目 Rust 所链接的 SQLite 版本或产品运行时；未读取真实 env/profile/SQLite。

独立全树归属结果：Development **16个实现路径 + tasks = 17**，与批准的封闭面完全一致，无删除。**1651** 个其余基线公开路径及旧 `flat.db`、`nested.db`、`invalid.db` 原字节保持；全部 Rust/原测试、owner/facade/App、两默认 YAML、旧 DAA-002/003 bundle、依赖/锁/Tauri/capabilities、CU/CA/SMA/backend/frontend-js/tools/contracts 的受保护字节不变。PM 批准记录和 coordinator 索引按自己的权威单列。10索引的增量逐行只涉及 DAA-004，根4索引另有独立 DS 行；没有未知变化。

普通 native source seal 共199路径，当前 **197相同**；仅 DAA `PLAN.md` / `PLAN.zh-CN.md` 因 coordinator 机械状态行改变。可执行输入仍匹配启动时封存字节，不能写成199全等。

## 3. R ↔ AC 验收矩阵

| 需求 / AC | 独立结果 | 证据与实际边界 |
| --- | --- | --- |
| R01 / AC01 | 通过 | 精确批准、`independent_fix` 身份、actual Development → fresh Verification 串行成立。当前17路径/完整 patch/保护字节与分权符合 spec；旧 DAA-002/003 原链不升格。外部3路径按 §6 精确归属。 |
| R02 / AC02 | 通过 | 中英文 README 与原 YAML 对读：PLC_1、127.0.0.1:102、rack0/slot1；DB1/example_group、start0/size12、3点；Real@0、Bool@4.0、DInt@8；3点 raw/latest=true、every_sample 仅退役归档。明确默认源码不是当前 profile 清单、无采样值/历史、已有 SQLite 优先、receipt 防重复、源不改、YAML/SQLite/DB-UDT 角色和重试新位置。无删库/删 receipt 重迁教程。 |
| R03 / AC03 | 通过 | diagnostics 无迁入组件挂载/导入；ConfigRevisionBar 仍唯一既有、默认关闭 details；YamlMigrationNotice 为其内有界 section，无 ConsoleCard/额外 details。外提示精确 unknown 优先，其次 failed 且 retryAllowed===true；持久不可重试 failed 和正常历史/null 无常驻入口。实际编译SFC双语SSR及host handler共21项原输出与当前源码/封存一致，打开同一details且0保存/重试/激活动作。 |
| R04 / AC04 | 通过 | 全 Rust/owner 原字节、receipt SQL、source 裁剪、空资格、动态 retryAllowed、ETag/attempt 双CAS保持。重试按钮保留 busy/dirty/editing 禁用；null 无旧动作。审查13+9 owner 反例的实际脚本和raw，保存成功但摘要查询失败仍 saved、清旧摘要、保留输入与编辑基线/CAS保护。新受控库每阶段 receipt 整行原字节不变，active/业务账本空。 |
| R05 / AC05 | 通过 | 先行 expected 证据与 R05 独立叶表/声明一致；minimal.db 单字段payload引用MinimalPayload、显式标准访问，UI编号21；minimal.udt只3简单叶。native结果为2源/1DB/3点/0组、完整引用树、complete=true/flat=false及disabled/group=null/address=null。唯一精确ignore例外与旧3DB/一般DB/SQLite反例通过。无复杂布局或 TIA/真实地址承诺。 |
| R06 / AC06 | 通过，保留操作程序差异 | Owner实际五步确认 + 同一普通构建binary/同库7阶段/final + 未变控制流及旧LocalEngine proof支持文件选择、缺UDT预览未确认、配对无issues、确认取消再保存、重载/正常退出。首PLC enabled=true→false不隐去，导入前停用基线与导入/最终不变量均成立；判定理由与观察限制见 §5。无逐点击抓包或预览ID直接观察声明。 |
| R07 / AC07 | 通过 | 必要前端构建/双语SFC/guard真实argv/env/exit/raw齐全；独立复核710个assembled键、176个literal键及占位符/26本地链接。仅核用旧golden/proof函数与相关分支/输入hash及原exit0，不冒称覆盖新pair。QA新增仅hash/源/文档与只读库对账，不重跑Cargo/GUI/旧B矩阵或安装依赖。 |
| R08 / AC08 | 通过 | README/app pair、i18n、三个修改组件头部及CODE_INDEX局部内容与实际变更一致；完整DEV handoff后才创建本checklist。QA终态只交Owner终验；资源归属、旧非零/外部变更和限制均保留。 |

## 4. 实际命令与核用方式

### 4.1 本次独立执行

以下 cwd 均为仓根 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`。完整实际argv、退出码、时长与解释分别在 Q/`static-audit.result.json`、Q/`native-and-reuse.result.json`，stdout/stderr 同名；不是重复产品测试。

| 命令 | 结果 |
| --- | --- |
| `/Library/Developer/CommandLineTools/usr/bin/python3 Q/qa-static.py` | exit0，约0.47秒；封存184附件/17路径/patch/保护面/精确ignore/索引行/locale/链接/expected独立审计。 |
| `/Library/Developer/CommandLineTools/usr/bin/python3 Q/qa-native-and-reuse.py` | exit0，约0.26秒；独立原raw和函数/分支hash复核，7阶段+final与新受控冻结双库逐表对账。SQLite 只用 `mode=ro&immutable=1`、query_only，前后数据库SHA保持。 |
| `git rev-parse HEAD`；对17份自有tmp副本逐一 `git diff --no-index --check -- <before> <after>` | HEAD匹配；各diff命令只允许0/1且stdout/stderr空，无空白错误。before/after副本只在Q。 |
| `git check-ignore --no-index -v <精确路径>` | minimal.db命中唯一negation；旧3DB、Owner真实DB、user.db/sqlite/sqlite3仍由一般规则ignore。保留各实际exit/stdout，不将negation的exit0误作仍ignored。 |
| `lsof -nP -iTCP:49194 -sTCP:LISTEN`；`lsof -nP N/profile/.daa-runtime.lock` | 两者exit1、stdout/stderr空；当前无自有listener/profile锁持有者。只读，不删锁或终止进程。 |
| `pgrep -fl '[p]ython.* /private/tmp/daa-004-r1-hppdbt2h/dev/native-watch.py'` | exit3：`sysmon request failed ... sysmond service not found` / `Cannot get process list`，当前环境不能枚举进程；原raw在 Q/`watcher-process-check.json`。未据此宣称当前watcher不存在，也未升级权限绕过；其正常退出依据为已核原session84888 exit0及stop控制记录，端口/锁另有独立lsof。 |

另已实际只读 `cat/sed/rg` 检查治理、bundle、完整实现增量、两SFC、owner/facade、点位页文件输入/确认与取消接线、Rust LocalEngine预览缓存/确认、receipt/保护SQL和flat-only guard；批准核心正文独立比较结果在 Q/`approval-scope.json`。没有读取用户真实profile。

### 4.2 审核 Development 当前增量原输出，未重复执行

D=`B/dev`，N=`D/native-r06`，S=`D/resume-window-1792379112`，C=`D/closeout-1792380367`。本表列的是已审查的真实历史执行，**不记为本次QA rerun**。

| 原命令 / raw prefix | 已核结果 |
| --- | --- |
| `pnpm build --config vite.validation.config.ts --outDir /private/tmp/daa-004-r1-hppdbt2h/dev/dist --emptyOutDir` / D/`frontend-build` | exit0、5.67秒；实际 `vue-tsc --noEmit && vite build`、1676模块、Vite5.4.21。原PURE与大chunk警告保留；没有为警告改依赖/打包配置。 |
| `node D/component-directed.cjs` / `component-directed` | exit0；现有Vue compiler真实编译两个SFC，21项双语SSR/host handler；UI替身只隔离呈现，不是原生桥。 |
| `node D/owner-rework-reviewed.cjs` / `owner-rework` | exit0，13项；通用失败双语、非空/仍空、pending/失败清旧摘要、保存成功摘要失败、失败保输入、双CAS和editor/dirty零retryIPC。 |
| `node D/owner-regression-reviewed.cjs` / `owner-regression` | exit0，9项；无桥零IPC/零timer、快照首次未载/后来陈旧、poll不替换编辑ETag及retry冲突/成功。 |
| `pnpm tauri dev --config N/tauri.port.json` / N/`launch-escalated.*` | 获准后普通cargo `run --no-default-features` 真实构建17.33秒并启动；无local-validation/fixture/Snap7，read=false。只覆写自有dev port/devUrl为49194；用户15191不动，产品Tauri配置不动。首开普通会话退出exit0。 |
| `pnpm dev --port 49194` + `N/frozen/aiis-data-acquisition-agent` / S/`process.json` 与 native/vite raw | Owner误关首个空窗后按明确重开请求启动相同封存普通binary、同env/profile；这次直接binary+Vite，未再次CLI/Cargo编译、无Tauri watcher，不能写成第二次完整tauri dev。最后native exit0、自有Vite组SIGTERM后exit=-15。 |
| `python3 C/snapshot.py final-closed`、`python3 C/native-reconcile.py` | 原closeout exit0；只读取同一自有库并冻结关闭后的双库。QA未再运行这些会写旧附件的脚本。 |

Development控制器已审查：剥离继承DAA_/VITE_/TAURI_/CARGO_/Rust/SQLite相关覆盖，使用自己的绝对关闭env/profile与target；native.env只有read=false及两个空YAML路径，无mode/storage。两空YAML不是仓内默认示例。native frozen binary SHA=`3ffc6ed4efedbd59d3aae7c657de88dda7ae5c92168a78e1d672b825b4a42805`，恢复记录和实际封存字节匹配。

### 4.3 两个既有 Rust 证明的有限核用

| 既有函数 | 独立核用证据 |
| --- | --- |
| `offset_and_full_structure_golden` | 函数字节与DAA-002冻结源一致，函数SHA=`9f8aaa3d3d2d71af147da27b47834ec94ff733d6baa6ef5b779f1a31008988df`。旧 `cargo test --offline --locked --lib infrastructure::local_store::tests --manifest-path <DAA>/src-tauri/Cargo.toml -- --test-threads=1` 原 `local-runtime-closed-2.stdout/.stderr/.result.json` exit0；只核该golden相关旧fixture，非重跑15项。stdout SHA=`211595f9727b4324d4154341aa627bd4c49949b0154235b7d0affa10ceb91e0d`。 |
| `public_save_cannot_forge_source_proof_and_preview_ids_match_confirm` | 函数字节与DAA-003冻结源一致，函数SHA=`255c8f12091b351d3e2a61ca689206b1ec000ae49dee1fd1a70a89ca47057c1c`。旧 `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --lib public_save_cannot_forge_source_proof_and_preview_ids_match_confirm -- --test-threads=1` 的 `directed-proof.*` exit0，stdout SHA=`cb6156c8da62309a0c73b5d8cb9bc362c7368ac71c62cbad0505769446c1a393`。证明真实LocalEngine预览/确认同ID及公共保存来源保护。 |

当前所有相关 Rust/owner 与DAA-003最终冻结版本相等。DB/UDT parser定义及展开分支与旧B逐字相同，layout、domain和相关fixture也相同；**`tia_source.rs` 整文件与旧B并不相同**，DAA-003退役的YAML编辑分支diff已独立对读并与 D/`prior-tia-yaml-retirement.diff`精确相等。两个旧函数均不使用本轮minimal pair，不能冒称它们测试过新文件、实际文件选择或当前native点击。

## 5. 普通 native 闭环、程序差异与限制

### 5.1 逐阶段持久事实

N/`observed-000.json`至`006.json`、C/`final-closed.json`原样核对；Q/`native-and-reuse.json`重新计算全部字段。C/`frozen-profile/config.sqlite` SHA=`3146378645712720a36eddb2ad1cbbe4f719c3cf858dce4c8a023eb9503dd842`，`runtime.sqlite` SHA=`0dc43608197a4d98fa69e84ee813e853e09d8d64327db707c97d8d0687d2ef2b`；两库只读重查与final原快照逐表相同，integrity=ok、user_version=1、journal=delete，读取前后字节保持。

| 阶段 | 独立核实的配置状态 |
| --- | --- |
| 000首开、001误关、002同库重开 | 全config表相等；0PLC/DB/点/组/编辑源；ETag=`018ed7e5-7e71-4f34-8717-0f344b5699b2`。误关不算导入验证。 |
| 003第一次PLC保存，03:08:40.995UTC | loopback PLC `DAA004-Owned`，**enabled=true**，无DB/点/来源；ETag=`036f14ae-f631-44de-9de6-01e911665b8d`。 |
| 004纠正，03:08:51.410UTC | 同PLC ID **enabled=false**，仍无DB/点/来源；ETag=`3f4fd0c3-508f-4629-bf78-626f4497c745`。 |
| 005完整pair确认保存，03:14:23.468–471UTC | 1停用PLC/DB21/3停用点/2编辑源/0组，issues=[]；ETag=`c7db1116-2738-479c-8f13-4f6c65cab9a5`。 |
| 006正常退出、final-closed | 与005**全部config表逐值相等**，ID/ETag/源原文/树保持；runtime clean_exit=1，只增加正常退出事件。 |

PLC ID=`1ae7d756-f2cb-471e-b98c-cc1a327d03ae`；DB ID=`207988f5-0f34-4f01-b99e-e531ba26feed`，MinimalImport、number21、complete=true/flat=false，唯一payload引用MinimalPayload、完整3叶。point IDs依次为 `d1170f17-3d81-4e0e-a92b-ecca928b681e`、`fce6b6d2-9512-4928-bbd6-e18786dac847`、`70eb8ef6-3bcf-4b8c-91c3-a41774d04a74`，分别是 ready/BOOL、count/INT、temperature/REAL；均绑定同PLC/DB、disabled/groupId=null/address=null。

| 来源 | 稳定ID | 原文SHA-256 |
| --- | --- | --- |
| minimal.db，dbNumber=21 | `9492ca76-e061-4c48-bd35-8a2bb4c0520c` | `ce75a52c2a7806c406bcec3354d2e50ebd0188b7ee9c4f03c09a5250ad752d6b` |
| minimal.udt，dbNumber=null | `d30b6a39-ef2f-4e82-b175-21ca80508e22` | `1967d3e0b55550560a218cf8e969fd690da3e5ec18ae8f9609bf1c41cbd62a31` |

source_documents的原文逐字等于选定样例，DB.sourceId指向DB来源；引用与原文在重载/关闭后稳定。先行expected SHA=`d1c89e7fb9c301c46cab954a4117ef1aab7c00923845b6ba06041a99515292cf`，与早于源码存在的 D/`expected-first.json`冻结证据相同；没有调用被测parser反向生成叶表。

所有7阶段及final的私有receipt **整行/原文字节相同**：ID=`0b91c0fe-1fa7-45d2-bed2-6228a9560637`，内容SHA=`4dd59ab487c1c22a7c3a86d16113cd4386c3518e4a2cb17694b192d223ca4b74`，skipped_empty。其内容记录的是当时摘要；当前retryAllowed仍由Rust结合空资格重新计算，不把历史receipt中的true当当前准入。

各阶段 active/previous=null，configuration_revisions/activation_intents为空；runtime的plc_sources、configuration_contexts、activation_journal、collection_cycles、samples、sample_delivery、sample_references均空，used_revision=null。持久事件只有两次started/stopped、3次draft_saved、1次sources_imported；恢复原stdout亦无激活/连接/采样事件。新env read=false。

### 5.2 R06 操作程序差异的独立判断

R06“新建并保存一台停用PLC”的首保存步骤未逐字遵循：003保存true，约10.4秒后004保存false。QA没有把这两次保存抹成一次停用保存，没有把Owner“五步没问题”解释成原始记录全无偏差。

此差异在**同轮源导入之前**已纠正；004仍无任何DB/点/来源，之后一次完整pair提交从停用PLC基线开始，最终PLC和全部导入点保持停用。全程read=false、无active、无连接/采样/业务账本，未触及真实profile或现场权限；没有改变产品实现、导入确认语义或要求。独立判断它是同轮已纠正的人工步骤差异，**不使AC06的受控导入/重载/无副作用目标失效，不构成产品返工或必要证据blocker**。这里不宣称首保存步骤本身原样通过，不作新的风险豁免；保留给Human Owner在最终验收时审阅。

### 5.3 无变化步骤与额外辅助偏移

Owner直接确认：“前面的5个步骤我都做好了，5步操作都没问题。”依据该实际观察，涵盖文件选择取消、仅DB缺UDT诊断且不确认、完整pair无issues、确认框先取消再保存、重载及正常CmdQ。独立审查未变UI/owner/Rust控制流：文件输入accept=.db,.udt/multiple，预览confirm=false不调用保存；确认对话框取消不发confirm=true；Rust缓存预览按ETag/source hash确认，旧真实LocalEngine proof补充同ID不变量。最终账本只有完整pair一次import提交，无部分来源/点提交。

这是spec允许的“工具无法绑定native窗口时Owner实际观察+同库证据”路径。**没有每次点击的IPC/截图、缺UDT具体file/line/path屏幕或本次预览ID抓包**。0.5秒变更watcher只看持久配置/clean_exit变化，不能观察每个预览/取消，QA没有把poll无变化伪写为逐点击记录；这几项由Owner实际观察与未变控制流/旧proof组合支撑，而非单靠SQLite证明。

Owner另尝试“推算DB”并见不支持：实际DB complete=true/flat=false；未变 `plc_layout.rs::preview` 在 `!d.complete || !d.flat` 早退，源码错误码为 `offset_inference_unsupported`。**本次没有单独捕获runtime错误码**，这里只报告Owner观察与源码guard吻合。005→006/final所有config/ETag/ID不变、地址全null。DB length=65536是既有默认界限，不是实际长度；不推算UDT地址、不扩大parser/layout/确认语义或补做现场测试。

## 6. 外部变更、真实非零与资源

B/`external-change-supplement.json` SHA=`2de4965cb90ac626043b9c091798adea507f9993cea89784c39c0ffb0ccb360f` 只覆盖以下3条外部归属；QA重新核定精确SHA/字节，不读取Owner真实来源正文，不把它们纳入DEV patch或新样例验证。

| 外部路径 | 精确保留事实 |
| --- | --- |
| fixture目录内 `DB_20260701.db` | Owner本轮自行放入；40649B，SHA=`691617444859a39364613f263e724b84a230d366fe5f7c1910003d82b23b3680`；继续被一般DB规则ignore，没有本次导入/修改。 |
| 同目录 `UDT_20260701.udt` | Owner自行放入、untracked；709B，SHA=`939e3754acb1ec1d72e9dcf39b7212ab8506160fda8ea443a58ee5452aafa1f2`；没有本次导入/修改。 |
| `plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md` | 独立DS会话Owner授权P0/r2文档变更；beforeSHA=`00171a46325c1b28359e77b3d2a42434e1ad43ac825b16cdb84f1708695c4c84`，当前131375B/SHA=`fc0ab9a11b4145b994bc3586e014ef87b98148b87c3d2f6a53a65204f4d6379b`。B/`parallel-ds-thread-observation.json`为只读归属证明；未向该会话发消息。 |

C/`raw-global-scope.json`、`raw-global-scope-final.json` **仍为passed=false**，outside仍是Owner UDT与DS spec；Owner DB因一般ignore不出现在公开路径outside，但另核SHA。首个closure helper真实exit1/AssertionError及原stdout/stderr都保留。后续closure-audit-final exit0与本次独立审计pass表示**明确归属后的Development边界匹配**，不重设baseline、不改写原全树false，也不放行其他未知变化。

其他真实非零原样保留：首个普通native在sandbox绑定49194 EPERM/exit1；随后同获批命令正常escalation获准、未见自动审批拒绝。两次evidence-reuse helper exit1分别源于旧owner版本和旧B整文件假设错误；own-diff-check helper exit1源于误解no-index差异退出码。只修自有审计后通过，产品没有为掩盖失败而改动。它们是环境/helper事实，不记为产品检查已失败后被静默覆盖。

资源已独立核对：native session68833原记录exit0，runtime_stopped/clean在03:22:06.982UTC、clean_exit=1；自有Vite由其wrapper终止自有进程组，exit=-15；watcher84888按原控制文件正常退出，原记录exit0/7次变化。独立lsof确认49194及本profile锁无持有；当前进程枚举因上述sysmond限制未取得，不伪写成pgrep成功。QA没有删除锁或停止用户15191，也没有回收任何证据/target/profile。

应继续保留B全根的baseline/before、PM/DEV/checkpoint/旧失败raw、native/resume/closeout全部快照、冻结机器码及关闭双库、dist/target/自有env/端口override/marker和Q独立证据，供Owner终验和可恢复追溯。旧DAA-002 live76与DAA-003原证据也保持。之后仅由sole coordinator按归属/依赖盘点安全收尾，临时证据路径不是永久保存承诺；本checklist保留关键结果/命令/对象ID/SHA以便审阅。

## 7. 验收审计与最终 handoff

| 类别 | 当前事实 / 下一 gate |
| --- | --- |
| 已独立验证的本任务基线 | 有限双语说明/迁入历史展示、精确提示与guards、唯一新DB ignore例外、先行3叶期望、普通native受控配对导入/取消观察/重载和保护面。 |
| 待Human Owner | 精确DAA-004 r1最终验收；请结合§5程序差异和观察限制决定，不把“五步操作没问题”自动写成终验。DAA-002/003各自最终验收仍独立pending。 |
| 延后/范围外 | 实际TIA导出兼容、多DB映射、UDT/复杂布局地址/长度、真实设备/真实配置/生产库/API、阶段C/上传ACK、Backend/SMA/DS、跨平台打包签名、发布部署。 |
| 历史与回退 | 旧失败/原raw/receipt防重复机制及旧bundle保留；不授权删除库/receipt、回滚或清空数据。 |

正式 handoff：独立 **`qa_passed`** 交唯一 coordinator `/root`，由其在本权威事实形成后机械同步索引并转Human Owner最终验收。QA没有产品失败项需返回Development，没有必要验证blocker；若随后产品字节或批准范围实质变化，需要新的精确handoff和新的fresh-context核验。本角色完成checklist/manifest与最终hash审计后停止全部写入，不执行Owner终验、发布、部署或资源回收。

Human Owner final acceptance: **pending**。
