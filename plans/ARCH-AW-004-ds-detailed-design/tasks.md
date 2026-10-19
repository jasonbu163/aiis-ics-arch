Task ID: ARCH-AW-004
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: exact approved r2 documentation revision and DEV self-check delivered to coordinator for new fresh-context Verification; no software or capacity proof, no final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS 首版多实例 S7 模拟器详细设计及 DAA/CU 复用依据文档
Owner: Automation World
Acceptance Chain Reference: aiis-ics-arch::ARCH-AW-004 r2 scope approved 2026-10-18 -> Development documentation handoff -> new fresh-context Verification -> Human Owner final acceptance

# DS 详细设计 Development 记录 r2

## 1. 精确批准与历史边界

2026-10-18（Asia/Shanghai），Human Owner直接批准『可以，批准 ARCH-AW-004 r2 spec，在线手改和运行值保留按推荐方案。接着更新 DS 详细设计并完成文档核验，先不改代码。』PM已在spec记录owner_approved，批准后SHA-256为`ff49d20b220bb6c45e94690ab9fa9b9c941ce761e26c65df6b42f15b3ac50874`。按R1–R23/AC1–AC29修订，仅写正文、docs双语DS唯一行和本tasks四文件；不写spec/checklist/根索引，不实现或运行DS。

r1原tasks完整101行见附录A逐行引文，可去除一层引文恢复原字节，SHA-256为`2cd8c8a317f42ba5ce2db71a96f4192afb885efdda2887e7de4dc5a914e2bc35`；r1正文367行SHA为`77216e4233c0b3c0a06fe624d93fee7f826a1a26e5f0bf497f58498aff4bd94c`。r1已真实独立文档qa_passed但Owner终验pending，r2不继承其verdict。原临时证据不改，原handoff anchor保留；附录中的当时状态/设计和相对引用属于历史，当前行为以r2正文/spec为准。

## 2. r2实施计划与验证目标

1. 完整读取批准规格、已有bundle和根/最近契约、复用适用skills；固定本角色起点 → 核对精确批准、四路径及r1历史保护。
2. 只读刷新DAA/CU实际状态/调用链并固定一次来源快照 → 复用矩阵准确标记在研/QA失败/返工及接口限制，不追逐后续并发变化。
3. 将R13–R22融入全版：连接计数/期限/面板、有界队列/输出预算与按item公平/stop、日志降级、无journal选择/幂等、一次性hold维护CAS与兼容保留 → 删除active旧冲突，保留R1–R12。
4. 补L1–L5负载/资源口径、时序及矩阵/阶段；执行Markdown链接anchors/表格围栏/双语单行delta/R-AC覆盖/算术/历史/范围审计 → 记录真实退出码、限制及精确r2 developer_handoff，交主协调启动新的fresh-context QA。

## 3. 起点、证据与当前进展

主协调基线`/private/tmp/arch-aw-004-r2-exec-ns_oqo5j/baseline-manifest.json`为files封装+absent结构，before/保存起点。Development独立起点在同目录`development/role-start.json`与`development/before/`；本轮保持当前工作树，不创建branch/worktree/commit，不回退其他任务dirty。已在修改正文前建立本r2计划。

已读根AGENTS/README/PLAN双语、docs/plans最近索引、canonical workflow、实际development TOML与当前完整bundle；本会话已消费的aiis/project-governance/desktop-tauri/rust-runtime/plc-point-mapping继续适用，本轮另读aiis CONTRACTS、RUNTIME_RESOURCE_TRIAGE及运行日志基线。只用设计规则，不借skill增加代码、DDL或依赖；更近AGENTS检索无匹配exit1，不是产品错误。角色model/effort仍只记录TOML配置事实，不声称独立运行遥测或平台ACL。

## 4. r2只读来源与固定快照

固定读时刻 **2026-10-18 19:54:59 +08:00**，`development/source-snapshot.json`保存37项摘要，`read-snapshot/`保存完整对应副本。DAA owning PLAN/checklist此刻qa_failed，tasks为implementation_in_progress；§9真实保留QA1的F-001/AC14清理保护反例不足和F-002/AC15维护空间/journal准入问题，正在同r2返工。原先已完成handoff、76份fixture样本/原生重开等历史保留，不再沿用DS r1时“尚无完整handoff/QA”的当前断言，也不提前宣布返工通过。此快照后进展不持续追逐，未来实施须刷新。

| 读取文件 | r2固定快照SHA-256 |
| --- | --- |
| DAA-002 `tasks.md` | `a8a1937eebfdc027ae4925debf3b91cf35be6fc9f2757dfd6cbe28882db336b0` |
| DAA-002 `checklist.md` | `8d8112aa26dfef4a5d616e385c8346300182fb08f451679f6711a0930018be4b` |
| DAA `src/console/composables/useLocalAcquisitionConsole.ts` | `614c9c3f48f020a4c2517e966b59fc01655a5c87e95f84eb9dd936bb29b53cdf` |
| DAA `src-tauri/src/infrastructure/tia_source.rs` | `3a596853246d1fa79b96e57ca8cfafe448fe9212c49a160ef729ed1fb6727cc6` |
| CU `src/ui/index.ts` | `38dcc6404c84144a8da84fc1fc3985f028e1335443261ce68a3a487f798b39b7` |

对比r1来源37项，主要变化是DAA PLAN/tasks、新QA checklist、私有composable和local_store说明/runtime；parser/layout/type/decode/managed client/CU公共出口字节保持。重新核对composable的saveCandidate/importSources/infer/activate→localCall/invoke→commands dispatch→configuration服务链；parser仍跳过声明:=和BEGIN初值，offset仍仅完整平铺标准标量，decode不是server encode，RemotePort客户端不是服务端。正文保留受限导入/初值提示/BOOL/STRING/raw全触达/单item/多item部分成功及所有原G0路径。

DAA双库激活/采样清理不作DS直接复用；本轮DS改为单配置库selection事务，不照搬DAA journal/维护逻辑。CU-008/DAA-001已验收范围以owning checklist为依据。r1已查同日官方python-snap73.2.1 stub与native Snap7 resourceless页面，以及外部/仓内runtime.py/strict_server.py相同字节，r2保留版本、来源和候选限制，未运行或安装库；没有把接口名/外部工具当拒写或16连接容量证明。

## 5. r2实际差异与语义核对

| 文件 | 本轮相对Development before的实际delta |
| --- | --- |
| `docs/AIIS_DS_Detailed_Design.md` | r1的367行修订为r2整版497行；贯通组件/配置/连接生命周期/策略/内存协议/UI/G0/未来矩阵。增加C/H/TCP/closing与单连接close、有限队列/输出预留/公平、L1–L5及资源口径，替换旧journal/纯日志故障封写/全部apply初始化/无维护例外。 |
| `docs/README.md` | 只替换DS唯一行，补r2连接/队列/维护/兼容保值目标与未授权实施，其它行原字节保留。 |
| `docs/README.zh-CN.md` | 与英文DS行语义对应，只有同一行替换。 |
| `plans/ARCH-AW-004-ds-detailed-design/tasks.md` | 活跃r2计划/来源/自检/handoff，原r1全文在附录A可恢复且SHA保持；旧handoff anchor仍有效。 |

DEV逐节推演：

- stop取消queued/precommit而非排长队；仅不可取消段单item完成一次，关闭/期限与确定拒绝、提交后回执未知分开；读回只能证当前值/seq，后续并发不能反推原item成功，禁止自动重试。
- preserve_compatible_hold按稳定身份/布局/typed值/effective策略证明并确认逐点清单；同版already_loaded幂等、不当reset。selection已提交未loaded时禁start，旧image只诊断；无journal，不假跨媒介原子。构建前通过统一owner复制有限快照，构建/SQL不持owner；安装前复核image/seq/控制代次/值版本，防同epoch start-write-stop造成陈旧保留；失败重新清单确认，不静默初始化。
- 在线普通ui-owner写继续；client/none的hold只有默认关闭的维护开关显式允许才可一次写，revision/epoch/point seq CAS、typed确认和同入口，持续owner不变，客户端后写可覆盖；rule暂停也不可维护，未增加租约。
- 纯日志sink/轮转失败降级有界内存/丢弃缺口，不封模拟写；配置SQLite确定失败/未知与内存正确性故障分别处理。fixed无变化不反复seq/更新时间，但owner/epoch/健康检查保留。
- 负载均为设计目标：L1=320请求/s=304读+16写、60928B/s；L2/L3=121856/487424B/s。L3另批扩展profile，128会话与每连接一线程在默认64线程下不相容，不声称已验证；RSS/CPU/句柄完整进程树与逐连接公平分母明确。

这是DEV自检，不是AC独立verdict或Owner验收。R1–R23/AC1–AC29定位见正文§12；root/plans四索引归主协调，未写spec/checklist/已验收AW/DAA/SMA正文或任何源码。

## 6. r2实际命令与DEV self-check

均在仓根，辅助Python仅stdlib处理Markdown/哈希/算术/差异；不导入项目或协议库，不进行SQLite、原生、端口、设备实验。

| 实际命令/检查 | 结果与边界 |
| --- | --- |
| 多批cat/sed/rg读取契约/bundle/源，`git rev-parse HEAD`、角色起点Python快照 | exit0；精确spec SHA核准。`rg --files docs plans -g AGENTS.md`无匹配exit1。保留当前大量dirty，不reset。 |
| source-snapshot Python与r1比对、完整37份read-snapshot复制 | exit0；固定时刻、路径/符号和变动如§4；未修改来源或追逐并发进展。 |
| 一次stdin语义补丁helper；后显式`command -v python3`、`/usr/bin/python3 --version`与UTF-8声明重跑 | 首次报Non-UTF-8 SyntaxError且未写入，该组工具返回0由末尾读取命令覆盖，不能当补丁成功。核到/usr/bin/python3 3.9.6，改显式解释器与UTF-8后exit0，语义补丁已写。不是产品错误/测试。 |
| `/usr/bin/python3 /private/tmp/arch-aw-004-r2-exec-ns_oqo5j/development/check-docs.py` | exit0；本轮最终计数随receipt固定：本地链接/anchors、表格列数及header分隔、围栏/尾空白、23R/29AC及关键合同词、旧冲突句、docs仅DS行差异、spec/r1 checklist保护、r1原tasks引文恢复与原正文起点SHA均检查。首轮57链接/28表；人工发现新增矩阵行被空行分开，合并并加强header检查后57链接/27表；补齐当前tasks后最终为57链接/30表/2围栏标记，全部exit0。静态脚本不代语义QA/Markdown渲染。 |
| 同checker的精确算术断言 | exit0；L1的320/304/16/60928，L2/L3字节，L5单洪峰380=361读+19写/72352B/s及8×C/H/TCP=128/32/160一致；只是算术，不是压测。 |
| `/usr/bin/python3 /private/tmp/arch-aw-004-r2-exec-ns_oqo5j/development/audit-scope.py` | exit0；基线1660实际file+2 absent→当前1660file；9个任务allowlist变化，8个foreign DAA返工文件（README pair、tasks、local_store README/capacity/mod/runtime/tests）保留；四份既有设计正文及r1 checklist不变。最终收尾再固定delta，不认领全树dirty。 |
| `git diff --check -- docs/AIIS_DS_Detailed_Design.md docs/README.md docs/README.zh-CN.md plans/ARCH-AW-004-ds-detailed-design/tasks.md` | 已执行exit0、无输出；tracked白空检查，最终receipt逐命令复核。 |
| `git diff --no-index --check <development/before/path> <current/path>`，四路径分别运行 | 最终receipt记录真实退出码；预期各exit1且无stdout/stderr表示存在本轮差异但无空白诊断，不能写为exit0；覆盖untracked/既有dirty相对本角色before。 |

未运行pnpm/Cargo/pytest、应用/sidecar/浏览器/SQLite/协议/原生/真实PLC/负载/故障注入实验；spec明确只授权文档。没有安装依赖、写schema/config/锁文件、监听/连接或操作DAA profile。Mermaid/页面未作实际渲染，不把静态图源码核对写成UI可用或软件容量通过。

## 7. r2精确developer_handoff

Task/Revision：`aiis-ics-arch::ARCH-AW-004 r2`，批准spec SHA保持`ff49d20b220bb6c45e94690ab9fa9b9c941ce761e26c65df6b42f15b3ac50874`。工作树HEAD仍`f85bea8bbf36b491968c3dc9a839518a1ed434a8`，无commit/branch/worktree。交接仅§5四文件和本轮精确before/diff，不包括他任务源码与DAA返工。r1 QA/current checklist仍是r1，本角色未改它，不提前齐平r2或给verdict。

正文SHA-256 `0eb3c149bf7093bbdce2f0b7a07af71e769fe24cb04a542c7f4dc43e6979eecb`；docs英文`dac64c0e769aa159942f57edcc53e325855828e5377be5afb38ba85953b836f0`、中文`10fb91f5159a9b17202e8c4e7aaea12a55ca6082a5498b344425783b700d66cb`。本tasks最终SHA在`development/handoff-receipt.json`，避免自引用；receipt同时含检查退出码、最终计数与scoped-diff.patch摘要。

下一gate：主协调在本次handoff后启动**新的**命名verification、fork_turns=none，独立读批准r2 spec、整版正文、本tasks及r1历史、r1 checklist、四文件delta/指纹/来源快照与当前树，重新核整版AC1–AC29并由QA接续checklist保留r1结论。QA通过后只进入Human Owner最终设计验收，不自动实施。Development此后停止四路径写入；若QA失败保留失败记录返工，新范围则回PM。

已知未验证技术项：server写前拒绝/全部来源收口、BOOL/STRING编解码与item真实回执，C/H/closing/输出缓冲/公平/期限和原生退出可控点，语言/库/平台分发、L1–L5资源和负载。数字是设计目标，G0/实施/压测另行获批；候选不能控制预算或满足16目标时回评审，不静默降级。持久运行值/热应用/临时租约/强持久审计/Modbus/响应模拟仍排除。

本轮临时资源只在`/private/tmp/arch-aw-004-r2-exec-ns_oqo5j/development/`：before、完整read-snapshot、role/source snapshot、修改/检查/审计脚本、JSON与精确patch/receipt；暂保留供fresh QA/终验。r1/tmp和r2 PM旧证据不改，r1原正文副本/引文继续承担历史追溯；无服务、socket、tab、数据库、构建、分支或worktree，DAA原生进程/profile及他任务资源不属于本角色。最终验收后由唯一coordinator按依赖盘点资源，不在本handoff自动删除。


<a id="r1-development-history"></a>
## 附录 A：r1 完整 Development 历史

以下逐行引文为r2起点完整r1 tasks，保留其批准、实施、自检、限制、指纹和handoff事实；不把历史journal/全部apply初始化等旧设计当作r2 active合同。

> Task ID: ARCH-AW-004
> Revision: r1
> Status: developer_handoff
> Owner Role: Development
> Allowed Writers: Development
> Handoff: approved r1 documentation and DEV self-check delivered to the active coordinator for new fresh-context Verification; no software implementation or final acceptance
> Workflow Mode: STD
> Execution Mode: agent_team_same_session
> Task Namespace: aiis-ics-arch
> Classification: root
> Capability: DS 首版多实例 S7 模拟器详细设计及 DAA/CU 复用依据文档
> Owner: Automation World
> Acceptance Chain Reference: aiis-ics-arch::ARCH-AW-004 r1 scope approval -> Development documentation handoff -> fresh-context Verification -> Human Owner final acceptance
>
> # DS 详细设计 Development 记录
>
> ## 1. 批准、角色与边界
>
> 2026-10-18（Asia/Shanghai）读取 [spec.md](spec.md) 的 `owner_approved` r1；精确批准原话和来源标识归 PM spec §1/§9。此次 Development 只写 `docs/AIIS_DS_Detailed_Design.md`、`docs/README.md`、`docs/README.zh-CN.md` 与本文件。根索引由主协调机械同步。实施是文档写入和只读核对，不创建 DS 工程、不改变 DAA/CU 或已验收 AW 正文、不运行应用、协议、数据库或原生实验。
>
> 实际命名角色为 `development`；已读 `.codex/agents/development.toml`。该文件的 model/effort 属于配置证据，不冒充独立运行观测；profile 为 `contract_only`，角色归属依靠串行 handoff 与差异审计，不宣称平台 ACL 或强制路由。
>
> ## 2. DEV 顺序与成功标准
>
> 1. 读取根与最近 README/PLAN、canonical workflow、完整现有 bundle 和适用 skills；固定角色起点与既有 dirty → 核对精确批准与四路径写入边界。
> 2. 只读跟踪 DAA/CU 当前状态和导入/配置/页面调用链、外部模拟器及官方资料 → 复用矩阵含路径、符号、限制和未来 gate。
> 3. 编写独立中文设计正文与 docs 双语单行入口 → R1–R12 / AC1–AC15 覆盖可定位，所有生命周期、策略与原子边界一致。
> 4. 检查 Markdown 链接/anchors、围栏、表格、双语入口、差异和指纹 → 记录实际命令、退出码、限制并交新 fresh-context Verification。
>
> ## 3. 起点与资源
>
> - 主协调起点：`/private/tmp/arch-aw-004-r1-ss_k14lh/baseline-manifest.json` 与 `before/`。
> - Development 独立起点：同目录 `development/role-start.json` 与 `development/before/`；记录四路径起点 SHA-256，正文与 tasks 起点不存在。大量其他 dirty 已存在，不回退或认领。
> - HEAD：`f85bea8bbf36b491968c3dc9a839518a1ed434a8`；在当前工作树写文档，不创建分支/worktree/commit。
>
> ## 4. 实施与核验
>
> ### 4.1 只读消费与证据
>
> 已消费根 AGENTS、README/PLAN双语、docs/plans最近双语索引、canonical workflow、实际development role、完整r1 spec及本角色任务记录。docs/plans内未发现更近AGENTS；`rg --files ... -g AGENTS.md` 无匹配退出1仅表示不存在更近文件，不是产品错误。技术核对还读取AW/DAA/CU README/PLAN、DAA-001/CU-008终验段落、DAA-002当时tasks、相关源码。应用的skills：`aiis`、`project-governance`、`desktop-tauri`、`rust-runtime`、`plc-point-mapping`，另读aiis BLUEPRINT；它们只约束设计，没有借skill新增工程、数据库DDL或UI代码。
>
> 读时快照固定为 **2026-10-18 17:40:28 +08:00**，`development/source-snapshot.json`保存37项文件摘要。DAA正在并发推进，本轮初读至§6.13，写成正文后刷新至§6.15；最终快照已看到两owned fixture采样/暂停/历史Owner回执和76轮/样本/pending对账，但仍`implementation_in_progress`、完整B6/交接/独立QA待续。正文不持续追逐后续小节，也不把fixture说成DS/S7或现场数据。关键读取指纹：
>
> | 文件 | SHA-256 |
> | --- | --- |
> | `automation-world/data-acquisition-agent/plans/DAA-002-local-acquisition-loop/tasks.md` | `49373fa6edd9552c54e6c2af09e0e5c1f9b1ea4c1a3319c1eb070963c1e37239` |
> | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/tia_source.rs` | `3a596853246d1fa79b96e57ca8cfafe448fe9212c49a160ef729ed1fb6727cc6` |
> | `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/plc_layout.rs` | `17f3c0f01349e1b5913d718b149cf11320d2653bfb2d6488384988b5a9f9ffee` |
> | `automation-world/console-ui/src/ui/index.ts` | `38dcc6404c84144a8da84fc1fc3985f028e1335443261ce68a3a487f798b39b7` |
>
> DAA导入路径已跟到页面`confirmImport/confirmOffsets/editLocalPoint` → `useLocalAcquisitionConsole` → `localCall/invoke` → `commands/local_acquisition.rs::dispatch` → `LocalEngine::import/save/offsets/confirm_offsets` → `tia_source/plc_layout`。确认`Parser::fields`跳过声明内`:=`、`blocks`跳过BEGIN赋值；没有初值模型；受限完整平铺标量偏移不含UDT/数组/STRING。`local_decode::decode`只是客户端类型解码；`ManagedS7`为读客户端，虽有RemotePort代码，不作DS server证明。正文§2逐项列路径、符号、复用等级和未来gate。
>
> 只读对比外部Vibe工具及仓内同路径两个文件：`runtime.py` SHA `edaabff54785097130095e8e717feb7a38228269cac57940cd4056ea51f7efd1`；`strict_server.py` SHA `54afe2ca3a02500c58fd3cbd8a28917e1ff6c76713d495cdc538db29290755ba`，两侧逐字节相同，证据`development/tool-comparison.json`。前者`refresh_areas`每tick调用`write_value`，后者strict TSAP后复用`_process_request`，均不证明写保护。外部tools/pyproject声明`python-snap7>=3.0,<4`不是本地安装或DS锁版事实。
>
> 通过web只读打开官方python-snap7 **3.2.1** Server API与native Snap7 resourceless页面（正文§10链接与读取日期），确认前者同名callback为stub、后者是不同native实现方向；没有安装/导入/运行库。服务端写前失败回执、回调内存时机、系统操作白名单、编码/原子/退出全部保留G0和后续验证，不能由资料接口名推断成功。
>
> ### 4.2 实际交付
>
> | 本角色变更文件 | 精确delta与正文定位 |
> | --- | --- |
> | `docs/AIIS_DS_Detailed_Design.md` | 新建独立中文正文：12节、组件流图、37项来源快照对应的复用矩阵；多实例/revision/SQLite概念/生命周期/导入初值/策略/协议item并发/逐页UI/原型及验证矩阵。 |
> | `docs/README.md` | 相对本角色起点仅新增一行DS文档入口和非实施说明，其他行字节保留。 |
> | `docs/README.zh-CN.md` | 与英文新增行语义对应；相对本角色起点仅一行新增。 |
> | `plans/ARCH-AW-004-ds-detailed-design/tasks.md` | 本角色首次创建，先implementation_in_progress后记录真实DEV检查与handoff。 |
>
> 具体决定：同进程stop/start保留值与模拟时间；跨进程重开、reset/apply从配置初始化且stopped；pause冻结含fixed的全部规则且不让权；apply只stopped，SQLite selection与内存非跨媒介原子，失败关闭准入按journal恢复。所有raw字节触达bit（含padding）审查，BOOL同字节RMW在单owner内；单item原子、多item逐项可部分成功，确定拒绝与已提交后回执未知分开。DB号/数量/区域均用户可编辑，不固定两个DB。
>
> ## 5. DEV self-check（非独立QA）
>
> 以下操作工作目录均为仓根；辅助Python只用stdlib读Markdown/哈希/差异，产物写本任务私有tmp，不是项目运行验证。
>
> | 实际命令/操作 | 真实结果与限制 |
> | --- | --- |
> | `pwd && rg -n 'ARCH-AW-004\|DAA-002\|CU-008' /Users/jason/.codex/memories/MEMORY.md` | exit0；轻量上下文检索。CU状态随后以当前checklist/source重核，历史记忆不作为现况证明。 |
> | 多批`cat`、`sed -n`、`rg -n`读取上述契约/源码/角色记录；`git status --short`、`git rev-parse HEAD` | 正常读取exit0；更近AGENTS无匹配exit1如上已说明。无修改源码或运行入口。 |
> | 角色起点Python快照；后续工具双路径字节对比、37项source快照Python命令 | 各exit0；起点、source-snapshot、read-snapshot与tool-comparison已保存。 |
> | `python3 /private/tmp/arch-aw-004-r1-ss_k14lh/development/check-docs.py` | exit0；4文件56个本地链接/anchors、20表（初次任务记录未补齐时为17表）、2围栏标记闭合、12个R与15个AC引用存在、12个显式审阅anchor、两个索引均只加一行；`doc-check-result.json`。只是静态与引用检查，语义仍需独立审阅。 |
> | `git diff --check -- docs/AIIS_DS_Detailed_Design.md docs/README.md docs/README.zh-CN.md plans/ARCH-AW-004-ds-detailed-design/tasks.md` | exit0；tracked差异无空白错误。另对两个untracked新文件执行`git diff --no-index --check /dev/null <path>`，避免仅检查tracked。首次最终检查tasks尾部多余空行返回exit3，已仅移除本角色新增尾空行；重跑两个no-index命令均exit1且stdout/stderr为空，表示新增文件存在差异而无空白诊断；tracked检查exit0。逐命令结果另记最终receipt。 |
> | `git diff --numstat -- docs/README.md docs/README.zh-CN.md` | exit0；相对HEAD各3行新增（含此前他任务2行）；独立起点检查证明本角色只新增DS一行，不认领既有diff。 |
> | 基于主协调`baseline-manifest.json`与`git ls-files --cached --others --exclude-standard -z`的Python哈希审计 | exit0；1656→1658文件，9条任务allowlist变化，唯一allowlist外变化是并发DAA-002/tasks；`development/scope-audit.json`。与协调侧`midpoint-delta.json`归属一致；本角色仅四路径。 |
>
> 手工DEV语义自检：R1–R12/AC1–AC15定位已列正文§12；逐节交叉核对配置保存/应用/启动、停止保值/重开初始化、fixed与初值/暂停、所有来源owner、padding/BOOL/多item、未知回执、UI权限与未来验证矩阵，无发现需扩大r1范围的问题。该记录是Development自检，不给AC的独立QA verdict。
>
> 未运行`pnpm build`、Cargo检查/测试、pytest、应用/sidecar、SQLite/协议/原生/设备实验；本次只有Markdown设计和索引，spec明确禁止上述运行，无需也不能借验证扩大实施。Markdown图表未进行浏览器渲染，围栏/表格/链接静态检查已做，独立Verification继续审阅语义与显示结构。
>
> ## 6. 限制、风险与后续gate
>
> - G0尚未验证任何server候选的提交前拒写、真实协议失败、所有写路径收口、callback线程/内存生命周期、多item错误与关闭。语言/库未定不阻塞本版具体设计，但阻塞未来声称软件满足的实现结论。
> - DAA解析器是受限私有实现，无公共crate；TIA初值跳过、复杂地址人工确认和decode非encode必须在未来适配中保留。DAA-002仍在研，实施前刷新来源字节/状态，不修改其任务或代码。
> - 首版运行值只在当前进程保留；关闭重开初始化并停机。持久值、Modbus、响应/握手/状态机、生产运行不在r1；源代码/依赖/配置/schema/真实环境均未更改。
> - 表中的内存/实例/日志预算是首版设计建议，后续批准实施spec依G0/负载预算固定；不是已测性能或支持保证。文档不得当现场证据。
>
<a id="7-精确-developer_handoff"></a>

> ## 7. 精确 developer_handoff
>
> - Task / Revision：`aiis-ics-arch::ARCH-AW-004 r1`，精确范围批准归`spec.md`，未改变R1–R12/AC1–AC15/allowlist/风险。
> - 工作树：当前仓根，HEAD `f85bea8bbf36b491968c3dc9a839518a1ed434a8`；没有commit/branch/worktree。交接范围仅§4.2四文件，PM spec与根四索引由其他相应角色维护；完整全树dirty不是本任务delta。
> - 正文SHA-256：`77216e4233c0b3c0a06fe624d93fee7f826a1a26e5f0bf497f58498aff4bd94c`；docs英文索引 `128b07ab87607703ef19554d3a56042da28d079dac6c4606d6572085618fc41d`；中文索引 `9503d826b265baae5ab7e219174b7c62abb44934eff4d1df7c90c0464299acb3`。本tasks最终字节摘要由外部`development/handoff-receipt.json`固定，避免自引用哈希。
> - 交付输入：获批spec、本tasks、正文/双语入口、§4来源路径/符号/37项指纹、`development/scoped-diff.patch`、`role-start.json`、`before/`、`read-snapshot/`、`doc-check-result.json`、`scope-audit.json`、`handoff-receipt.json`与协调全树基线；重要结论/命令/限制同时记录仓内，不以易失tmp作唯一事实。
> - 下一gate：由唯一主协调在本handoff之后启动全新命名`verification`、`fork_turns=none`，独立读spec/tasks/实现/差异/当前树，核验AC1–AC15并仅写checklist。Development不创建或修改checklist，不代授QA/Owner验收；QA通过后仍等待Human Owner最终设计验收，不自动开始实现。
>
> 临时资源归属：本角色只创建`/private/tmp/arch-aw-004-r1-ss_k14lh/development/`内before、read-snapshot、脚本、JSON与patch；没有服务、端口、浏览器tab、数据库、构建产物、分支或worktree。本子目录与主协调同任务基线目前保留供fresh QA和最终验收审计；未经依赖盘点不删除。其他DAA原生profile/进程及全树dirty均非本角色资源，不触碰；最终Owner验收后由主协调按canonical workflow盘点，不在本handoff自动回收。
