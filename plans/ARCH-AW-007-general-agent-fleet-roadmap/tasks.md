Task ID: ARCH-AW-007
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: ARCH-AW-007 r2 五正文与DEV self-check已交接；新的fresh-context Verification核验精确工作树/SHA并封存r1 checklist；独立verdict与Human Owner最终验收pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# r2 文档实施与 DEV self-check

## 1. 依据、角色与精确范围

Human Owner 于2026-10-20明确批准：“批准 ARCH-AW-006 和 ARCH-AW-007 的 r2 spec，按新方向同步双语 ROADMAP 和相关设计文档，保留 r1 历史和验证记录，暂时不改代码。”实施/检查发生于2026-10-21（Asia/Shanghai；UTC仍2026-10-20），不追改批准时序。

批准 [007 r2 spec](spec.md#r2-design) SHA-256 `39041b334483e15d88b00f1ec1e65be07c8d583c982136f7659baa8e8feb297d`；关联 [006 r2 设计](../ARCH-AW-006-unified-flow-agent-design/spec.md#r2-design) SHA-256 `63ac134d8a1b75cf1a78815bf11ad53689106269d3556007d99162db1ec4ff73`。依据007 §2/§9，仅写双语ROADMAP、三旧设计既有方向提示块和本tasks。spec/checklist只读，八索引由主协调机械维护；006不创建tasks/checklist。冻结CA/CAF不解冻，软件/迁库/运行均另批。

实际使用命名development角色，读取development.toml、根AGENTS/README/PLAN双语、canonical lifecycle workflow、docs README双语、AW README/PLAN、完整006/007 bundles及五正文、SMA当前README/表格批量与启停入口/顺序调度和DAA当前README。采用aiis（含BLUEPRINT）和project-governance；仅处理文档，未加载实现skill。profile为contract_only，主会话、完整bundle、串行handoff和diff审计是必要控制，不宣称ACL/强制路由或技术隔离。

## 2. 工作树、基线与实施顺序

正式工作树`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD `0af5b91177f3bca63f9f3c2bef9f14004ea49944`加本轮未提交文档增量。未创建源码副本、分支或worktree，没有commit/push。

主协调基线`/private/tmp/aiis-aw007-r2-doc-sync-20261020-xbp7s_1j/manifest.json`保存17原文件bytes和1893任务外保护hash，SHA `89ff1e2421262de41207a2fa64392180871aa6b9f6d8ccbb30a6f988a69c1571`；`approved-spec-snapshot.json`保存批准后两spec，SHA `22372b70b4078450e8ac952be40d7b36a93c36f7af961e1b105be21a18c62066`。旧r1基线`/private/tmp/aiis-aw007-doc-sync-20261020-gz1hgdga`继续保留，不删除。两目录只供文档比对/验证，不是源码交付副本。

1. 先把本tasks真实推进r2 implementation_in_progress，原r1逐行加固定前缀完整封存；原checklist不改。
2. 双语ROADMAP主改§4/5/7/8；§1/3/6/9只协调本方向直接矛盾，§2原bytes保留，由§7明确SQLite总述对各App的适用范围。三旧设计只替换各一条原007 r1提示行，原修订日期、DS增补、来源、章节全部保留。
3. 对照spec §9英中拟文逐段审阅，核对代码现状与未来分期、链接/anchors、fences、metadata/versions和r1还原SHA。主协调提出最小澄清后，§7.1明确flowId/flowRevision仅CA使用，DAA/SMA分别用采集/点定义和映射版本；两语言已同步。
4. 记录下述DEV自检、精确SHA与范围审计，冻结五正文供新的fresh-context Verification。独立QA和Human Owner最终验收均未发生。

## 3. 实际变更与 AC01–AC14 自检对应

下列是Development self-check，不能作为QA verdict。

| AC | 实际文件/核对结果 |
| --- | --- |
| AC01 | 本tasks为唯一活动r2 metadata；两spec保持批准后bytes/owner_approved，未虚构批准或Parent。spec §10对draft时序的解释按§12真实批准判定。仅五正文及本tasks写入，后续gate明确。 |
| AC02 | ROADMAP双语§4三App分工、CA可做简单映射、SMA同构批量工作方式、独立配置/可写状态/队列/凭据/lifecycle明确；不设数量阈值或未实证吞吐承诺。 |
| AC03 | 五正文活动方向不含FOA工作名，CA新目标不等同冻结旧CA；006/007链接均指r2-design。r1历史中的旧名、真实r1 QA/final pending原样保留。 |
| AC04 | 双语§4/§6与三提示说明SMA已过滤TSS、现有表格/批量/启停和逐项await/fresh Facts→POST；新增源码链接可解析。子集/逐行常驻、任意GET、并发/隔离容量与SQLite/outbox分别分期，rowVersion非完整历史库。 |
| AC05 | 双语§5明确连接器归CA、首版HTTP GET/POST/明确受支持S7/无登录，后续PLC/WS/DB逐项矩阵；WS连续性/背压、DB凭据/参数化/事务/owner/幂等/unknown、PW Service/API及非跨系统原子性齐备。 |
| AC06 | 双语§3/§7分别说明DAA当前SQLite且上传未接入、SMA当前Backend-held、CA目标存储；三App不强制一起迁移。§2保留，§7显式限定其SQLite总述，不扩写三界表。 |
| AC07 | 双语§7.1 agentKind与dutyProfile分开、三类型登记/心跳、实际能力/配置/工作版本、instance/boot/seq及克隆冲突；flowId/flowRevision仅CA，不要求DAA/SMA都有流程。 |
| AC08 | 双语§7.2分别列DAA采样/磁盘/补传、SMA读取/投递/延迟/积压、CA流程/节点/unknown；上传未接入与未有持久outbox均显式不可用，不伪造零指标。 |
| AC09 | 双语§7.2/7.3 receivedAt TTL、有效boot/seq、旧代次/重复/倒序/历史回放隔离、阈值顺序和有界latest心跳；unknown/online/stale/offline/conflict与独立degraded齐备。 |
| AC10 | 双语§7 AWC经AWB，存活不等于工作/PLC/业务成功；失联本地继续与资格/租约/fencing/重启按App合同，CA首版stopped/recovery_required；先只读后配置/远程，首版无登录及未来信任分期，现有认证/actor改造另立范围。 |
| AC11 | 双语§8保留S0–S4和001旧证据，三应用/CA连接器/平台按真实依赖分别推进，无AWB/所有协议/全部共享Core/统一存储前置；无新增日期或支持完成声明，PW/AIW/PG/Redis/HA/SA/OS方向保留。 |
| AC12 | 逐段核对spec §9与双语§4/5/7/8，技术inline字段集、表行及Mermaid边对称；§4/5/7/8表行分别为[8]/[]/[8,9,6,7,5,6]/[8]。§2与原TSS可靠性/切换段bytes保留；三旧设计去提示后与原bytes一致。 |
| AC13 | 两spec的完整r1及本tasks r1按指定前缀恢复原SHA；原r1 metadata/状态/正文不改。原checklist整文件SHA不变，由后续Verification按真实r2交接封存。r1 qa_passed不继承为r2，r1 final一直pending。 |
| AC14 | 活动链接/anchors、fences、LF、唯一metadata及versions核验；风险/待决、恢复/资源与handoff见下。全仓checker分阶段兼容诊断如实记录，未修checker/旧任务，也不把self-check称独立QA。 |

## 4. DEV self-check 命令与实际结果

工作目录均为正式交付树；临时Python仅使用bundled Python 3.12 stdlib处理Markdown/JSON/bytes/SHA，不是项目runtime验证，不安装依赖或修改依赖文件。

| 实际命令 | 退出码与结果 |
| --- | --- |
| `shasum -a 256 plans/ARCH-AW-00{6,7}*/spec.md plans/ARCH-AW-007*/{tasks,checklist}.md` | exit0；写入前两批准spec、原tasks/checklist SHA与§1及历史段一致。 |
| `git rev-parse HEAD` | exit0；与§2 HEAD一致。 |
| `/Users/jason/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /private/tmp/aiis-aw007-r2-doc-sync-20261020-xbp7s_1j/sync-docs-r2.py` | exit0；五正文从manifest原bytes核对后同步。随后只补中英SMA现状证据/分期、认证/心跳限制、独立凭据与flowId仅CA的最小澄清；以正式五正文最终SHA为准。 |
| `/Users/jason/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /private/tmp/aiis-aw007-r2-doc-sync-20261020-xbp7s_1j/check-docs-r2.py` | 初轮及flowId澄清后均exit0；100项机械断言零失败，62个活动本地链接/anchors有效。2026-10-20 16:06:19 UTC扫描：1893保护路径1891一致，2项并行005变化。最终tasks完成后收尾复检另记下节。 |
| `git diff --check -- ROADMAP.md ROADMAP.zh-CN.md docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md docs/AIIS_AW_Runtime_Design.md docs/AIIS_SMA_Detailed_Design.md plans/ARCH-AW-007-general-agent-fleet-roadmap/tasks.md` | exit0，无空白错误。 |
| `git diff --check` | exit0；该时点全工作树无空白错误，不据此判断其它任务正确性。 |
| `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch > /private/tmp/aiis-aw007-r2-doc-sync-20261020-xbp7s_1j/governance-development-r2.log 2>&1` | 初次exit1、312行；007有4行（重复两遍）：旧checklist r1/r2 Revision不一致、旧checklist遇r2 implementation_in_progress的requires developer_handoff。批准/Development已真实推进，旧证据不伪升；最终handoff后收尾复跑另记下节。 |

主协调起点`governance-before.log`为exit1、312行；007当时6行兼容诊断（重复两遍的tasks/checklist Revision不一致及draft spec批准状态要求）。checker不能识别同文件历史与新Revision的串行过渡。本次不改checker、spec或旧checklist以消除诊断；全库历史问题仍不等于本任务通过/失败或已修复。

三旧设计仅去掉各自唯一旧/新提示行（原空行均保留）后的共同原文SHA；此处的哈希口径是本r2基线与候选之间去提示行，不与r1去两行插入块的旧哈希口径混用：

| 文档 | 保留原bytes SHA-256 |
| --- | --- |
| AW白皮书 | `e565cda3dd0dc4059259f283bbcd49a6dc1345133d30a608a17f9b19d8014892` |
| AW Runtime | `1c02120b5ff60655282c7042036dee944838a107a9cedcfa2532c6d072f5f681` |
| SMA详细设计 | `497a3569a39cfa977834d6cebcfa9262818990a166c212ccce75b03058f2e6d4` |

## 5. 任务边界、并行变化与限制

Development只写五正文和本tasks。批准后spec全bytes与approved snapshot保持；原checklist仍为r1原文件。1893保护清单在16:06:19 UTC仅观察到005 `tasks.md`与`evidence/evidence-index.json`变化；随后git路径盘点另有两个清单外新文件：005 `evidence/protocol-baseline.json`、`evidence/resource-closeout.json`。已报告主协调，均非本角色写入，不回退、不评价005结果；这是时点观察，不保证并行树持续静止。八索引由主协调维护，不能把它们或所有git dirty归本角色。

本任务没有运行构建、原生Tauri/GUI、服务/监听、API、数据库、PLC、Docker或安装依赖；无提交、推送、部署或发布。文档一致不证明连接器、AWB/AWC、容量/持久恢复或现场能力。未决仍为CA落点/OS/生命周期、连接器矩阵、正式API/schema/登记信任/阈值、SMA扩展/容量/可靠存储、中央配置权威、远程管理/租约/fencing与现场合同，分别另立实施任务；不由本文授予权限。

原文保留意味着旧设计中的SQLite/共享Core/角色节点等仍按当时目标解释；三处新提示和当前ROADMAP给出r2方向，后续精确实施spec须声明采用/替代条款，不能任意拼接旧句成新运行合同。文档回退仅处理007确切增量，保留可还原r1与并行dirty；不reset整树、不清配置/数据、不撤销已发生外部效果。

## 6. 精确 Developer handoff 与冻结候选

**ARCH-AW-007 r2：developer_handoff。** 正式工作树及HEAD见§2，五正文自下列SHA冻结供新的fresh-context Verification；Development任务面仅本文件，QA verdict及Human Owner最终验收均pending。006 r2仅作为已批准关联设计基线，不新增其角色文件或转移验收。

| 五正文 | 冻结SHA-256 |
| --- | --- |
| `ROADMAP.md` | `b1b89f9b9268c57c833e597fff94b83ca08a086be58fb62db146a1e88edc2fb2` |
| `ROADMAP.zh-CN.md` | `847e544f1cc39a918ac04131bbd144e3e9c2af057d0bcb4b3cf14ed66e653947` |
| `docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md` | `46e1de05709867c76720aa2b8bbf6bcc0c0665df75e1d5b2581923bcc3ff3d67` |
| `docs/AIIS_AW_Runtime_Design.md` | `b75e829233c9d5ed638adc88646d8074bcc6a62fc773e7b34ca63aedea6758b9` |
| `docs/AIIS_SMA_Detailed_Design.md` | `502ea342ed86008b657d6e2cdbfe8f00f8028bff0546ceb265ca166a86690d07` |

交接输入：完整approved spec与006设计、本tasks、原checklist、五正文、manifest/批准snapshot、原r1 tasks/checklist/spec快照、当前diff、文档检查脚本/JSON及前后checker日志。主协调下一步只机械跟随真实handoff，再显式启动新的`verification`、`fork_turns="none"`；该角色独立复核AC01–AC14、保护历史并真实推进checklist，不继承r1 verdict。最终Human Owner gate保持待定。

## 7. 临时资源归属与保留条件

主协调创建本轮基线目录、manifest/批准snapshot/原r1快照与before日志。Development在该目录创建`sync-docs-r2.py`、`check-docs-r2.py`、`finalize-tasks-r2.py`、`development-doc-check-r2.json`、`development-path-scan-r2.json`、`development-scope-r2.diff`、`governance-development-r2.log`、`governance-handoff-r2.log`、`development-checker-comparison-r2.json`及最终复核快照，供开发审计、fresh QA与Owner审阅。没有新进程、服务、端口、环境、worktree或分支。它们不是唯一证据：关键命令、结果、AC、原文/交付SHA与限制已持久记录于本tasks。

当前仍有fresh QA/最终验收依赖，暂保留新旧两个基线目录；最终验收后由主协调确认归属、无运行/后续任务/证据依赖再按workflow清理，不在开发交接前删除旧r1证据或其它任务资源。

## 8. 收尾复核记录

2026-10-20 16:08:31 UTC（2026-10-21 00:08:31 +08:00），精确handoff metadata形成后复跑§4的`check-docs-r2.py`：**exit0，100项断言零失败、62个本地活动链接/anchors有效**；五正文仍为§6冻结SHA，两批准spec、r1还原和原checklist保护均通过。1893保护路径仍1891一致，2项005并行变化；该时点事实已报告主协调。

handoff后执行`bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch > /private/tmp/aiis-aw007-r2-doc-sync-20261020-xbp7s_1j/governance-handoff-r2.log 2>&1`：**exit1、310行**，日志SHA `4f68a3eb376bd84c8b5ce5c66b5b4ccac776a7f715fe2c7cd52cbfda86469fa0`。007仅剩旧checklist r1/r2 Revision不一致两行（全库两轮扫描重复），本tasks的Revision/批准/handoff要求已消失；旧checklist由后续新Verification按真实r2阶段封存，Development不代改。

相对主协调前置312行的多重集合比较：移除6条（007 tasks Revision/批准状态各2条、两AW PLAN各缺失plans链接1条）；新增4条为根`plans/README.md`对006 tasks/checklist的`missing honest pending task stage`（各重复2条）。006只交设计且由007统一记录实施/QA，没有伪造006后续角色文件；已报告主协调检查其索引措辞/旧checker兼容，Development未修索引或checker。其余诊断保持；不能宣称全库治理通过或将历史诊断记为007修复。

最后任务范围`git diff --check -- ROADMAP.md ROADMAP.zh-CN.md docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md docs/AIIS_AW_Runtime_Design.md docs/AIIS_SMA_Detailed_Design.md plans/ARCH-AW-007-general-agent-fleet-roadmap/tasks.md`：**exit0**。本轮没有追加软件/项目测试。scope内无待实施正文项，交新的fresh-context Verification；self-check与旧r1 QA都不构成r2 verdict或Human Owner最终验收。

主协调随后修正四catalog的006机械阶段措辞，明确文档实施/QA统一在007 r2，软件另立范围及待批准，不创建006角色文件。仅针对该索引变更复跑治理checker，输出`governance-handoff-final-r2.log`：**exit1、306行**，SHA `d0bcb73bee2df11e6e774ed842b2ec1e5898309572fd975c56ceea5c6c888397`。与前置312行比较**新增0、移除6**；007仍仅旧checklist Revision不一致2条，006 pending措辞兼容4条已消失。这个最终全库未通过结果和分阶段限制保持；未重跑软件/项目测试，也未再改五正文。该最终日志为本次handoff的有效checker结果，前述310行记录保留真实过程。

<a id="r1-history"></a>
## r1 完整 Development 历史

原r1为developer_handoff，原独立QA为qa_passed，Human Owner final acceptance始终pending。它们只覆盖r1；本文件归档不改变旧结论、原证据或当前r2 gate。下面每一原行（含空行）仅加`r1|`，去前3字符可还原原bytes，SHA-256 `e8dfad1584329c1e2a92595854992683ff920b7a34eb9c632ca4b2e361f2d2de`。旧checklist此阶段整文件保持SHA `9d268a7dfc21d0f0ecd06831d2e0989703247901c6f11fa4bbf9de3d61097279`，后续仅由新Verification真实推进并封存其r1。

<details>
<summary>展开 ARCH-AW-007 r1 tasks 原文（只读历史）</summary>

<!-- ARCH-AW-007:tasks:r1:BEGIN -->
````text
r1|Task ID: ARCH-AW-007
r1|Revision: r1
r1|Status: developer_handoff
r1|Owner Role: Development
r1|Allowed Writers: Development
r1|Handoff: ARCH-AW-007 r1 五正文与 DEV self-check 已完成，精确交付工作树交新的 fresh-context Verification；独立 verdict 与 Human Owner 最终验收待后续
r1|Workflow Mode: STD
r1|Execution Mode: agent_team_same_session
r1|Task Namespace: aiis-ics-arch
r1|
r1|# r1 文档实施与 DEV self-check
r1|
r1|## 1. 执行依据与边界
r1|
r1|依据 [spec.md](spec.md) §14 的精确批准，仅实施 §2.2 五份正文并记录本文件；八份机械索引由主协调维护。批准 spec SHA-256：`083d64b9ad274eed1a41380ad62e0d58757457a57a090eaffd880f8be1a0b494`。不修改 PM spec、独立 Verification checklist、006 或任务外文件。实际采用 development 角色；profile 为 contract_only，串行 handoff 与 diff 审计是必要控制，不宣称 ACL 或自动路由。
r1|
r1|已读取根 AGENTS、README/PLAN 双语、canonical workflow、development TOML、完整 spec 与当前 bundle、docs README 双语及五份正文；docs 无独立 PLAN/AGENTS。应用 aiis / project-governance skill；仅作文档检查，不加载实现 skill。
r1|
r1|## 2. 实施顺序
r1|
r1|1. 双语 ROADMAP §4/5/7/8 同步通用宿主、连接器、身份与健康；协调 §1/3/6/9 的直接矛盾。验证：逐段中英文和 AC01–AC12 走读。
r1|2. 三份旧设计各单次插入方向提示。验证：去掉新增提示后与本轮基线逐字节一致，覆盖 AC13。
r1|3. 检查新增链接、metadata、allowlist、006/任务外保护及空角色文件。记录真实命令/退出码并交接，覆盖 AC14。
r1|
r1|## 3. 基线与资源
r1|
r1|交付工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `0af5b91177f3bca63f9f3c2bef9f14004ea49944`；不提交/push。本轮主协调基线：`/private/tmp/aiis-aw007-doc-sync-20261020-gz1hgdga/manifest.json`，含五份正文与八份索引原 bytes、1808 任务外 tracked/untracked 文件 SHA；`git-status-before.txt` 保留初始 dirty。必须据此区分既有 DS/DAA 等变更，不能以 Git 总 diff 归属本任务。
r1|
r1|该临时目录由主协调创建，供本轮自检与 fresh QA；本文将持久保存必要证据摘要。主协调在独立 QA 和 Human Owner 最终验收完成且无后续依赖后核实清理，不在开发交接前删除。
r1|
r1|## 4. 实际变更与 AC 对应
r1|
r1|| 文件/范围 | 实际变更 | DEV 对应 |
r1|| --- | --- | --- |
r1|| `ROADMAP.md`、`ROADMAP.zh-CN.md` §1/3/6/9 | 增加007路线权威；目标链路标FOA的SMA/CA场景；普通HTTP→HTTP/PLC→PLC可直达而业务状态保留Service/API；更正DAA SQLite本地采集/上传未接通；保留CAF兼容、006 draft及后续范围门槛 | AC01–AC03、AC12、AC14 |
r1|| 同上 §4/5 | FOA工作名、内部连接器、可组合SMA/CA场景、多实例与专用DAA；架构图/责任表；HTTP/S7首版无登录与后续PLC/WS/外部集成DB支持矩阵、参数化/事务/幂等/unknown恢复 | AC02–AC05、AC10、AC12 |
r1|| 同上 §7 | 保留aw_所有权/事实合同；完整身份/职责/capability/assignment/config字段表、配置权威与ACK分层、提议URL、心跳字段/代次/seq/接收TTL/限额、四层健康与状态、失联/重启/fencing | AC06–AC10、AC12 |
r1|| 同上 §8 | S0–S4 gate与分支推进，保留PW/AIW、PG/Redis、HA/SA及OS托管边界；原TSS可靠性与切换段落不变 | AC11–AC12 |
r1|| 三份旧设计 | 每份单次插入同一方向提示及双语ROADMAP/007链接；明确精确批准/交付/独立QA/最终验收状态归bundle记录；原字节完整保留 | AC13–AC14 |
r1|| 本 tasks | 真实Development记录、检查与精确handoff | AC01、AC14 |
r1|
r1|手工逐段对照 spec §10 与中英 §4/5/7/8；每节表行数、技术inline字段和Mermaid节点标识机械对称。翻译过的DAA链路/构建示意文案作语义走读，不以字面英文相等冒充翻译验证。§2（PW/AW/AIW职责）与原TSS可靠性/切换段落逐字节对照未变；§1/3/6/9只做规格允许的一致性协调。各未来接口/能力均标为目标/提议或未实现，未将DAA底座、目录、007批准或006草案写成通用Core/心跳交付。
r1|
r1|## 5. DEV self-check 命令与真实结果
r1|
r1|工作目录均为交付工作树。辅助Python只处理Markdown/JSON/字节/hash，不是项目运行时验证；未改依赖清单或安装工具。
r1|
r1|| 命令 | 退出码/结果 |
r1|| --- | --- |
r1|| `shasum -a 256 plans/ARCH-AW-007-general-agent-fleet-roadmap/spec.md` | 0；精确批准SHA与§1一致 |
r1|| `git rev-parse HEAD` | 0；`0af5b91177f3bca63f9f3c2bef9f14004ea49944` |
r1|| `/Users/jason/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /private/tmp/aiis-aw007-doc-sync-20261020-gz1hgdga/sync-docs.py` | 0；五正文从manifest原bytes核对后同步；脚本为临时开发辅助，交付以实际文件为准 |
r1|| `git diff --check` | 0；首次五正文实施后全工作树检查无空白错误 |
r1|| `git diff --check -- ROADMAP.md ROADMAP.zh-CN.md docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md docs/AIIS_AW_Runtime_Design.md docs/AIIS_SMA_Detailed_Design.md plans/ARCH-AW-007-general-agent-fleet-roadmap/tasks.md` | 0；当前任务范围无空白错误 |
r1|| `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch` | 前置由主协调运行exit1、314行历史诊断；开发首次复跑exit1、314行：007的4条重复诊断为已创建tasks尚待主协调补目录链接，另有005并行/索引变化；不修历史任务、不伪称全库通过，最终复跑记录见下 |
r1|
r1|自检初轮发现并纠正：中文§10.8拟文提取未在下个二级标题截断，短暂混入spec尾部§11–14，主协调走读指出后已仅保留§6预定单段；增加双语ROADMAP二级章节必须恰为1–9的断言。技术inline提取初版把fenced Mermaid和译文示意误当字段比较，修为排除fence/译文示意并保留字段集、表行数和节点标识检查。未改变已批准规格。§1另最小澄清shared UI integration/共享UI集成，避免把已存在CU源码表述为尚无源码。
r1|
r1|临时检查脚本 `check-docs.py` 与 JSON输出 `development-doc-check.json` 位于同一任务基线目录。检查包括批准spec hash、三旧文单次纯插入、1808保护路径、§2及可靠性段原文、中英字段/表行/节点、fence、21处新增/替换行本地链接、006原hash/draft、无提前checklist，以及全库checker中007诊断。开发首轮退出1的原因与纠正如上；以最后一次独立命令执行结果为有效自检，见下。
r1|
r1|## 6. 限制、风险与资源
r1|
r1|- 本次仅文档，不运行构建、API、DB、PLC、原生Tauri、服务、Docker或依赖安装，不提交/push；文档self-check不证明任何未来连接器、FlowCore、AWB/AWC或现场健康功能。
r1|- FOA工作名未最终确定；006仍draft，首版无登录及HTTP/受支持S7范围不变。正式URL/schema/身份信任/阈值、目标OS托管、连接器产品矩阵、中央权威切换、远程操作/HA与DAA替换等价仍需各自精确规格。
r1|- 保护扫描发现005 `spec.md` 与 `tasks.md` 发生并行变化，已报告主协调；Development未写这两文件，其余保护路径应按最终扫描如实记录。不能把跨任务活跃工作树称为静止、也不回退这些变化。
r1|- 自有临时资源为基线目录下 `sync-docs.py`、`check-docs.py`、`development-doc-check.json`、`governance-after-development.log`；基线manifest和before日志由主协调创建。用途为开发对照与fresh QA，保留到独立验证/最终验收后由主协调核实清理；必要证据与hash在本文持久记录，无进程、服务、端口、新worktree/分支或安装依赖。
r1|- 如需文档回退，只撤销007的具体增量，保留历史任务和原dirty，不reset工作树。QA verdict与Human Owner最终验收由后续角色/Owner记录。
r1|
r1|## 7. 精确 Developer handoff
r1|
r1|- **Task / Revision：ARCH-AW-007 r1**；批准spec SHA与§1一致，未改spec；本文件状态`developer_handoff`，不代表QA verdict或最终验收。
r1|- **交付候选：**当前正式工作树`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `0af5b91177f3bca63f9f3c2bef9f14004ea49944` 加本轮未提交增量；无commit/push，无临时源码副本。
r1|- **Development实际写入：**五份正文（下表）与本`tasks.md`。八索引由主协调机械同步，不是Development写入；spec归PM，checklist仅待新的fresh-context Verification创建。
r1|- **验证输入：**完整approved spec、本tasks、当前五正文、manifest保存的原始bytes、初始status和前后checker日志、临时check-docs脚本/JSON。QA应从manifest区分本轮与大量既有dirty，并独立审阅AC01–AC14；当前self-check不替代该核验。
r1|
r1|| 五份正文 | 交接 SHA-256 |
r1|| --- | --- |
r1|| `ROADMAP.md` | `a295be9e6c035f7509649c2d4f1f91552f4acfa6f904f260ef1ce27d4b3163c5` |
r1|| `ROADMAP.zh-CN.md` | `cf3e433bc5f951a39fab7512d724d6de7d8d29c09423b4badfe8221435592330` |
r1|| `docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md` | `e184158a3c2966905b6a8af7ed7f336a9d99213ceeec1e534b11c94613eadaa1` |
r1|| `docs/AIIS_AW_Runtime_Design.md` | `cb136a6a0513f78ca6e6eb616b5f83ce589f01ef1214ef8f74d11d35a7476dbf` |
r1|| `docs/AIIS_SMA_Detailed_Design.md` | `fa9179b715f992afe07756fd9ac9a7c7649c22b5b389a81394f7850023a17619` |
r1|
r1|保护检查的时点限制：主协调已复核原1808清单最初仅005 spec/tasks变化并保存`parallel-document-changes.json`，元数据对应005 r4，不含007；本任务各角色操作未写005。随后开发扫描观察到另九项任务外并行变化：`docs/AIIS_DS_Detailed_Design.md`、`docs/README.md`、`docs/README.zh-CN.md`，以及`automation-world/device-simulator/g0/server/`下`main.cpp`、`owner.cpp`、`owner.hpp`、`protocol_hooks.cpp`、`protocol_hooks.hpp`、`resource_sample.cpp`。Development未写这些路径，已报告主协调并保留当前bytes，不将它们归属007、不回退、不评价005批准内容。保护计数随并行任务推进会变化，最终差异应由主协调/独立QA按实际时点记录；不能宣称全工作树恒定。
r1|
r1|开发scope内未遗留待实施项。已知风险/未授权边界见§6与spec §12–13；主协调下一步应同步真实developer_handoff索引并启动新的fresh-context Verification，传入精确r1与本工作树/基线，最终Owner gate保持待定。
r1|
r1|
r1|## 8. 最后有效自检与冻结点
r1|
r1|五正文最后仅将动态“交接中”提示收敛为稳定的“r1方向更新；精确批准、交付、独立QA和最终验收状态由bundle记录”，动态阶段保留在本tasks/索引及后续checklist；§7上表为这一冻结点后的最终hash。
r1|
r1|- 最后独立执行 `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch > /private/tmp/aiis-aw007-doc-sync-20261020-gz1hgdga/governance-after-development.log 2>&1`：**exit1**，302行；007诊断为0，无新增诊断；前置314行中005/并行索引相关12行已不再出现，不归本任务修复或验收。
r1|- 最后独立执行 `/Users/jason/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /private/tmp/aiis-aw007-doc-sync-20261020-gz1hgdga/check-docs.py`：**exit0，72项开发文档断言无失败**；21处新增/替换行的本地链接可解析；中英§4/5/7/8技术字段/表行、Mermaid节点及§1–9结构一致；三旧文各一处纯插入，去增量后与manifest原bytes一致；006原hash/draft不变，spec批准hash/本tasks唯一metadata一致，未提前创建checklist。
r1|- 同次1808保护扫描：11处为上节已报告且主协调确认的任务外并行变化，其余**1797处与基线SHA一致**；本任务写入面只有五正文与本tasks，未回退或修改并行005/DS文档/源码。扫描是该时点观察，不冻结其他任务。
r1|- 最后执行 `git diff --check`：**exit0**。不新增永久测试/脚本/evidence.md；构建/API/DB/PLC/原生/现场均未运行且不在文档验收口径内。
r1|
r1|以上为Development self-check，独立QA及Human Owner最终验收均pending。五正文自此冻结供fresh-context Verification；八索引由主协调跟随真实handoff阶段。
````
<!-- ARCH-AW-007:tasks:r1:END -->

</details>
