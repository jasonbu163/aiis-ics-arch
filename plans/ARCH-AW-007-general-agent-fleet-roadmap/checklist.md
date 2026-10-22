Task ID: ARCH-AW-007
Revision: r2
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner已于2026-10-21最终验收ARCH-AW-007 r2五份文档；Verification仅记录已发生决定及主协调完成的归档/资源收尾，主协调机械同步八索引；r1历史保留，暂不改代码
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA/SMA/CA 三应用职责、CA 内部连接器与全类型 AWB/AWC 健康管理路线修订
Owner: Automation World
Acceptance Chain Reference: 本任务 spec 第 12 节；PM -> Human Owner 精确范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收

# ARCH-AW-007 r2 独立文档 Verification

## 1. 输入、角色与效力

本次命名 `verification` 调用 `/root/aw007_r2_document_verification` 使用 fresh context，不继承 Development 的对话推理；独立消费完整交接输入。已分批读取根 AGENTS、README/PLAN 双语、canonical lifecycle workflow、verification.toml、docs/AW 最近 README/PLAN 与相关 catalogs、完整006/007当前 bundle 及 r1 归档。两spec与tasks中的归档先独立还原至原快照，再完整阅读；旧checklist完整阅读后仅在本文件封存。另读双语 ROADMAP 全文、三旧设计的提示及各自基线差异、可用DEV输出，并从manifest独立产生和审阅五正文diff，没有调用DEV检查脚本或把其100项断言当作本次QA证据。

使用 `aiis`（含 BLUEPRINT）与 `project-governance`；本任务只验证文档、metadata/版本、范围、双语、链接、字节保护及治理。没有新代码/配置/测试或工具依赖，不复验旧书技术合同、构建、原生GUI、吞吐、可靠投递、API/DB/PLC/现场或部署。本角色仓内只写本checklist，不修spec/tasks、五正文或索引。TOML中的`gpt-6.1-sol`/`max`仅为配置证据，没有独立运行后端/effort测量。本profile为`contract_only`；fresh context、串行handoff和diff/checklist审计是控制，不宣称平台ACL、强制路由或技术隔离。

Human Owner于2026-10-20的真实批准原话：“批准 ARCH-AW-006 和 ARCH-AW-007 的 r2 spec，按新方向同步双语 ROADMAP 和相关设计文档，保留 r1 历史和验证记录，暂时不改代码。”007 [spec](spec.md#r2-design) §2/§9/§10/§12是本次范围/AC/批准依据；[006 r2设计](../ARCH-AW-006-unified-flow-agent-design/spec.md#r2-design)仅作关联批准设计基线。文档实施及独立验证统一由007的[tasks](tasks.md)与本文记录，不创建006 tasks/checklist。批准时序仍为10-20；本次执行为上海10-21、UTC10-20，不倒填更早批准或验收。AC01/AC03中的draft按spec §10/§12显式阶段说明判定，获批后的owner_approved是正确状态。

## 2. 环境、基线和固定候选

- 正式交付工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `0af5b91177f3bca63f9f3c2bef9f14004ea49944`加未提交文档增量；无源码副本、新worktree/分支、commit或push。
- 文档辅助环境：macOS 15.7.7 / Darwin24.6.0 arm64；`/Users/jason/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`，Python3.12.14 stdlib。它只处理Markdown/JSON/bytes/SHA，不代表项目runtime测试。
- 主协调r2基线：`/private/tmp/aiis-aw007-r2-doc-sync-20261020-xbp7s_1j/manifest.json` SHA `89ff1e2421262de41207a2fa64392180871aa6b9f6d8ccbb30a6f988a69c1571`；独立解码17原文件bytes及1893保护hash。
- 批准后snapshot：同目录`approved-spec-snapshot.json` SHA `22372b70b4078450e8ac952be40d7b36a93c36f7af961e1b105be21a18c62066`；两spec当前与其逐字节相同。r1基线`/private/tmp/aiis-aw007-doc-sync-20261020-gz1hgdga`继续保留，未清理。
- QA首次独立保护扫描：2026-10-20 16:13:51 UTC（2026-10-21 00:13:51 +08:00），`verification-start-r2.json` SHA `0a74b244a9959d35a76463dcca7f0dc9b6f201596318991cd4ed88c6a40704cd`。

以下SHA均独立重算并匹配developer_handoff-final-r2.json、批准snapshot及实际工作树；最终增量复核再次保护这些固定输入：

| 固定输入/五正文 | SHA-256 |
| --- | --- |
| 007 approved spec.md | `39041b334483e15d88b00f1ec1e65be07c8d583c982136f7659baa8e8feb297d` |
| 006 approved spec.md | `63ac134d8a1b75cf1a78815bf11ad53689106269d3556007d99162db1ec4ff73` |
| 007 developer_handoff tasks.md | `4e684dbd7312e154a4f723fee7f36aeebdde395234c1bb79a44d6596fa06ae6d` |
| ROADMAP.md | `b1b89f9b9268c57c833e597fff94b83ca08a086be58fb62db146a1e88edc2fb2` |
| ROADMAP.zh-CN.md | `847e544f1cc39a918ac04131bbd144e3e9c2af057d0bcb4b3cf14ed66e653947` |
| docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md | `46e1de05709867c76720aa2b8bbf6bcc0c0665df75e1d5b2581923bcc3ff3d67` |
| docs/AIIS_AW_Runtime_Design.md | `b75e829233c9d5ed638adc88646d8074bcc6a62fc773e7b34ca63aedea6758b9` |
| docs/AIIS_SMA_Detailed_Design.md | `502ea342ed86008b657d6e2cdbfe8f00f8028bff0546ceb265ca166a86690d07` |

## 3. AC01–AC14 独立结果

`EN`指[英文ROADMAP](../../ROADMAP.md)，`ZH`指[中文ROADMAP](../../ROADMAP.zh-CN.md)。以下逐项结论来自独立语义走读、当前源代码引用核对及字节/结构审计；计数不能代替翻译或边界审阅。未将旧r1同号AC结果继承给r2。

| AC | 独立证据与判定 | 结果 |
| --- | --- | --- |
| AC01 | 两spec唯一r2 owner_approved、tasks唯一r2 developer_handoff，身份/namespace/owner/writers和批准/交接链一致，无Parent；批准snapshot逐字节保持，五正文和角色写入面明确。§10对draft时序的显式解释与§12真实批准相符，未把批准当QA/终验。 | pass |
| AC02 | EN/ZH:70–103的三App、图和责任表逐项对齐：DAA大量持续采集、SMA独立表格/批量/工作台、CA通用节点且可做简单映射。各应用/实例独立配置、可写状态、凭据、队列和生命周期；不以数量阈值/未经实证吞吐分界，不依赖另一App存活。 | pass |
| AC03 | 五正文无FOA活动产品名；spec中的旧名只用于变更对照/原话/归档。EN/ZH:11、74、99和三提示区分冻结CAF/旧CA与新CA目标；006/007均明确链接r2-design和真实owner_approved，未解冻旧CA、建新目录或冒充实现。 | pass |
| AC04 | EN/ZH:101–103、§6及SMA README相符。已核对映射表/JSON-XLSX批量弹窗/启停入口，scheduler:135–155、651–744、779–895确认Backend配置与逐项await/fresh绑定Facts。来源DTB服务`list_mapping_runtime_configurations`:1237–1262仅取enabled映射和enabled POST目标；本仓无TSS Backend，该HTTP在线面仍需兼容Backend。当前Facts→POST集合运行/单行测试与未来任意GET、子集/逐行常驻、容量/隔离、本地SQLite/outbox明确分期，rowVersion不冒充完整历史库。 | pass |
| AC05 | EN/ZH:105–113将连接器归CA，HTTP GET/POST、明确受支持S7与无登录为首版设计；后续PLC/WS/获准外部DB分别按协议/CPU/访问/驱动版本/OS/类型/读写矩阵验收。WS身份/快照增量/重连/缺口/背压有界；DB凭据/参数化/池/事务/owner/只读写入/幂等/unknown齐备；PW Service/API边界、无任意SQL/DDL首版或跨系统原子/物理恰好一次承诺。 | pass |
| AC06 | EN:131–156 / ZH:132–157和§3分别说明DAA当前SQLite/上传未接入、SMA当前Backend-held及独立技术偏好、CA目标版本化存储；SMA近期整理不强制先迁库。§2原bytes保留，§7显式限定其SQLite方向总述，aw_示例不形成第二可写权威。未来发布/激活/ACK分层，回退保留pending/unknown/outbox/cursor/audit。 | pass |
| AC07 | EN:158–179 / ZH:159–180明确agentKind为DAA/SMA/CA、dutyProfile为该类型内职责，均非登录角色/ACL。三类共享登记/心跳概念，实际能力、软件、配置/工作版本及instance/boot/seq齐备；DAA采集/点定义、SMA映射、CA flowId/flowRevision分开，流程字段明确仅CA。克隆恢复/新ID、冲突instance/boot/kind保留，不last-write-wins。 | pass |
| AC08 | EN:187–197 / ZH:188–198类型化摘要分别为DAA采样/质量/磁盘/补传、SMA读取/投递/错误/延迟/可观测积压、CA流程/节点/unknown/资源。上传未接入报告unavailable；无持久outbox不伪造可靠backlog为零；不要求三类都报告流程数。 | pass |
| AC09 | EN:187–211 / ZH:188–212定义observedAt与AWB receivedAt/lastSeen、当前有效boot/seq、旧代次/重复/倒序/历史回放隔离、重连当期快照、正值有序阈值、有界latest心跳且不挤业务空间。管理存活、App工作、外部连接、数据/进度分层；unknown/online/stale/offline/conflict与独立degraded，online可降级、offline不证明进程死亡。 | pass |
| AC10 | EN:152–156、176、211–212 / ZH:153–157、177、212–213及§4区分CU/本机工作台/中央AWC。AWC经AWB读取，先只读健康、再配置/远程；失联只继续本机已激活且不依赖在线资格的工作，租约/fencing/重启各依App合同，CA首版stopped/recovery_required不自动新写。心跳不授接管/设备权，未决用原身份核实；无登录与未来登记信任分期，现有认证/actor改造另批，不默关全仓认证。 | pass |
| AC11 | EN:214–227 / ZH:215–228保留S0–S4及001原前置证据，三App/连接器/平台按窄合同依赖分支推进，无AWB、所有协议、所有共享Core、统一存储或另一App进程前置。无日期/新支持完成声明；PW/AIW、PG/Redis、HA/SA与目标OS托管仍各依独立gate。 | pass |
| AC12 | 独立逐段对照spec §9双语拟文与EN/ZH全文、阶段表及600行五正文diff。两文§1–9结构完整；主改§4/5/7/8，§1/3/6/9只协调名称、现状/权威、链路与r2引用。§4/5/7/8表行组为[8]/[]/[8,9,6,7,5,6]/[8]，两语言同构；§7技术inline字段44个同集，Mermaid节点/边对齐；译文链路另作语义核对。§2、TSS可靠性与切换原段bytes不变。三提示各一行替换，不改原书技术/来源或DS增补。 | pass |
| AC13 | 两spec、tasks及本checklist的完整r1按指定marker/四反引号text fence/每行r1|（含空行）独立还原，分别601/364/98/126行，SHA见§4全部匹配原文件快照。旧metadata/Revision/状态/命令/限制和qa_passed保留，r1 final始终pending；本次r2从新交接独立验证，没有追改或继承r1 verdict。 | pass |
| AC14 | spec §11–12、tasks §5–8及本文保留风险/未决、精确增量回退、资源归属、权限和handoff。五正文60处本地链接/anchors、当前bundle及最终checklist活动链接有效，fences/LF/metadata通过；006仍仅spec，007同一固定三文件。八索引由主协调机械跟随真实qa_in_progress，四catalog真实三角色链接共12个存在、四PLAN只链接spec。checker结果和历史/并行限制如§6，不宣称全库通过。 | pass |

源码引用核对仅用于判断文档“当前事实”是否准确，不重新验收SMA/DAA功能。无登录设计并不表示当前Backend认证/actor依赖已移除；来源DTB过滤也不表示本仓有该Backend或接口已部署。

## 4. 历史还原与原文保护

| r1原文 | 还原行数 | 去每行前三字节后SHA-256 |
| --- | --- | --- |
| 006 spec | 601 | `7a96361040684832c9e78ae9ac9717e6cce90e6ed08a443a44a0dcc79fedff92` |
| 007 spec | 364 | `083d64b9ad274eed1a41380ad62e0d58757457a57a090eaffd880f8be1a0b494` |
| 007 tasks | 98 | `e8dfad1584329c1e2a92595854992683ff920b7a34eb9c632ca4b2e361f2d2de` |
| 007 checklist | 126 | `9d268a7dfc21d0f0ecd06831d2e0989703247901c6f11fa4bbf9de3d61097279` |

r2基线与候选的三旧设计，`difflib.SequenceMatcher(..., autojunk=False)`分别只有一个一行→一行`replace`，位置为白皮书13行、Runtime6行、SMA6行；没有插入/删除其他字节。仅移除该唯一提示行（保留其余空行）后，两边bytes完全相同，包含所有原修订日期、来源、历史说明和DS增补。此口径是r2基线“去一条原/新提示行”，不混用r1“去两条新增行”的旧口径。

| 三旧设计 | 去提示后保留bytes数 | 共同SHA-256 |
| --- | --- | --- |
| AW白皮书 | 61765 | `e565cda3dd0dc4059259f283bbcd49a6dc1345133d30a608a17f9b19d8014892` |
| AW Runtime | 32563 | `1c02120b5ff60655282c7042036dee944838a107a9cedcfa2532c6d072f5f681` |
| SMA详细设计 | 39632 | `497a3569a39cfa977834d6cebcfa9262818990a166c212ccce75b03058f2e6d4` |

ROADMAP §2原bytes的EN SHA `84ba7f846d3dbdad768320a9092319f182b6e1aab00d5fc656066a14e8dab568`，ZH SHA `afbb72ba81c723c8522dbdbb4de8ec409b665a9ed48efa7edc792f533a397a3f`。原TSS可靠性及切换两段在两语言各精确出现一次且bytes未改；旧设计的原原则只按当时范围参考，未来实施spec须明确采用/替代，不拼接成新的未批准运行合同。

## 5. 任务范围与并行时点

16:13:51 UTC起点与16:19:24 UTC主审计均为**1891/1893**保护路径SHA一致。两条变化仅005 `tasks.md`与`evidence/evidence-index.json`；manifest外三条新增为005 `checklist.md`、`evidence/protocol-baseline.json`、`evidence/resource-closeout.json`。已报告主协调，它们属于DS并行生命周期观察，不归007、不回退或评价其验收。此计数只描述各扫描时点。

八索引相对r2 manifest，排除006/007行后只在四份根索引另见005由implementation_in_progress到developer_handoff的并行行变化；四份AW索引其余bytes相同。相对QA自己的起点，16:19:24 UTC只变更本checklist与主协调八索引，其他路径hash未变；没有把工作树总体dirty归属007或宣称长期静止。根AGENTS/README/CODE_INDEX、DAA/DS实现、其他历史bundle等受清单保护路径不因本QA改变。最终时点另记§7。

## 6. 真实命令、结果与治理限制

工作目录均为正式交付树。独立检查器和JSON/diff写在主协调任务tmp目录，不安装依赖；构建、原生GUI、服务/监听、API/DB/PLC/Docker、commit/push、部署/发布和资源清理均**not_run，范围排除**，不是隐含pass或本次blocker。

| 检查 | 实际命令/方式 | 退出码和结果 |
| --- | --- | --- |
| 环境/固定候选 | `git rev-parse HEAD`；`uname -srm`；`sw_vers`；bundled `python3 --version`；stdlib SHA/批准snapshot解码 | exit0；HEAD、平台/Python和八个固定文件SHA见§2，批准spec逐字节一致 |
| r1归档/保护起点 | bundled Python heredoc独立提取marker/fence、每行去r1|，并重算manifest与git tracked/untracked文件 | exit0；四份r1原文件SHA匹配；生成verification-start-r2.json，1891/1893及三个005新增见§5 |
| 独立文档审计 | `/Users/jason/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /private/tmp/aiis-aw007-r2-doc-sync-20261020-xbp7s_1j/verification-r2-audit.py` | 16:19:24 UTC首次exit0：153项机械核对零失败、94处当前活动本地链接零错误（其中五正文60处）；另完成AC逐段语义走读。最终本文增量后的复核另记§7 |
| 范围diff | 自行解码manifest原bytes，使用stdlib difflib生成并分批审阅`verification-five-document-r2.diff`（600行）与`verification-roadmap-coordination-r2.diff`（155行）；独立比较八索引排除006/007行后的diff | exit0；三旧文单提示替换、ROADMAP允许章范围/PW-AIW保护、并行005行变化见§3–5 |
| 来源核对 | `rg`/`sed`读取当前SMA README、映射/批量/启停组件、实际mapping_runtime/mod.rs；按DTB来源读取`data-twin-backend/backend/app/tss/services/async_tss_api_configuration.py`的配置过滤函数；读取DAA README当前SQLite/上传说明 | 仅静态读取，无API/服务/项目运行。定位曾遇两个不存在的猜测路径，随后以实际SMA mod.rs及已声明DTB外部来源核对；不把本仓不存在TSS Backend写成已接通 |
| 正文空白 | `git diff --check -- ROADMAP.md ROADMAP.zh-CN.md docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md docs/AIIS_AW_Runtime_Design.md docs/AIIS_SMA_Detailed_Design.md` | exit0，无输出 |
| QA首次治理 | `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch > /private/tmp/aiis-aw007-r2-doc-sync-20261020-xbp7s_1j/governance-verification-r2-in-progress.log 2>&1` | exit1、306行，SHA `09884b80dede954e55dc1aa3c737a3b05d21212edd80fe6b3dfa72944ad17bc4`；006/007诊断均0；完整多重集合比较如下 |

QA首次306行相比DEV最终306行：**新增4、移除4**。移除007旧checklist r1/r2 Revision不一致2条、005中文catalog旧pending阶段2条；新增005新checklist目录链接缺失4条（英/中各重复两次）。相比协调前置312行：**新增4、移除10**，另移除007 tasks Revision/批准状态及两AW PLAN链接过渡项。不把005创建checklist/索引推进记作007修复。该次306行类别为290 metadata count、12 missing task document link、4 Allowed Writers；都是全库历史/并行诊断，未修复、未宣称全仓治理通过。007本地完整metadata/r1前缀/真实角色路径另由独立审计验证；checker只作现有机械校验，不理解全部自然语言handoff或提供ACL。

## 7. 最终增量复核

本checklist完整r2正文和r1归档写入后，2026-10-20 **16:24:45 UTC**（2026-10-21 00:24:45 +08:00）再次独立执行§6审计命令：**exit0，153项机械核对零失败，99处活动本地链接/anchors零错误，其中五正文60处**。新增5处是本文指向当前spec/tasks/006与双语ROADMAP的链接；旧r1在fence中保持，不以历史链接解释当前结论。两批准spec、tasks及五正文仍为§2冻结SHA，四份r1还原SHA/行数不变；三旧文去提示原bytes、双语字段/表/图、LF/fences、角色metadata与三文件形状均通过。主协调八索引当时为真实qa_in_progress，四catalog的12个角色链接与四PLAN spec链接实际存在。

| 最后必要检查 | 真实结果 |
| --- | --- |
| `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch > /private/tmp/aiis-aw007-r2-doc-sync-20261020-xbp7s_1j/governance-verification-r2-final.log 2>&1` | exit1、306行，SHA仍为`09884b80dede954e55dc1aa3c737a3b05d21212edd80fe6b3dfa72944ad17bc4`；006/007诊断0，与首次QA日志多重集合新增0/移除0。相对DEV/协调前置差异仍如§6，不宣称全库通过 |
| `git diff --no-index --check /dev/null plans/ARCH-AW-007-general-agent-fleet-roadmap/checklist.md` | exit1、无输出；no-index相对空文件有内容差异，不冒报exit0。随后bundled stdlib逐行扫描exit0：0行行尾空格/tab、0个CR、结尾LF；差异退出码不作为空白错误 |
| bundled Python治理多重集合/空白结果汇总heredoc | exit0；生成`verification-governance-comparison-r2.json`，时间16:25:12 UTC，保存上述真实诊断增减与空白结果 |

16:24:45 UTC范围扫描仍为1891/1893保护SHA一致，只有§5已列005两项变化、三个新增；相对本QA起点除本checklist与主协调八索引外其余文件hash未变。并行时点均保留，不冻结或验收DS。独立代码检查器SHA仍为`d1ed83a6be5981ddb1d3d1092be6d6c9fcbc5d9a6a2dd8dc96b5640e3ef5a297`，未更改检查器或DEV输出以消除诊断。完成本节真实记录后才将r2状态签为qa_passed；只进入Human Owner最终文档验收gate。

## 8. Acceptance Audit、verdict与handoff

| 面 | 本次验收层次 |
| --- | --- |
| 007 r2 五正文/治理/历史 | AC01–AC14与最后checklist增量复核通过，r2独立qa_passed；Human Owner最终文档验收pending |
| 006 r2 | 精确设计owner_approved基线；文档实施/QA统一007，没有006新角色文件；不授软件实施/终验 |
| r1历史 | 原范围、DEV、独立qa_passed及final pending完整保留；不继承为r2证据 |
| 新CA/SMA优化/三类型fleet/连接器/可靠存储/容量 | 规划或目标；软件/原生/运行/长期/现场能力不在本次QA，分别需获批实施合同和实证 |
| 冻结兼容/切换/回退 | CAF/旧CA、来源TSS与历史依据继续按各自原范围；真实writer切换/数据迁移/外部动作另批，文档回退只处理007确切增量 |

**Verdict：qa_passed。AC01–AC14全部通过精确ARCH-AW-007 r2文档核验，无本范围failure或blocker，无需Development返工。** 全库历史/并行治理诊断如§6–7保留，未修复或宣称全绿。QA -> Human Owner：审阅§2固定五正文并决定最终文档验收；主协调只据本真实verdict机械同步八索引，不代改PM/Development事实或扩大006/旧任务验收。Human Owner final acceptance一直为**pending**，QA不授予owner_accepted。CA落点/OS/生命周期、SMA任意GET/子集/调度容量/可靠存储、连接器矩阵、正式API/schema/阈值/登记信任、单一配置权威迁移和远程/租约/fencing/现场合同仍依各自后续规格，不因文档通过获得运行或发布权限。

## 9. 资源与后续Human Owner gate

本角色仓内唯一写入为本checklist。QA临时资源在r2基线目录：`verification-start-r2.json`、`verification-r2-audit.py`、`verification-r2-audit.json`、`verification-five-document-r2.diff`、`verification-roadmap-coordination-r2.diff`、checklist写入辅助稿与两个QA治理日志/比较JSON，分别用于独立基线重算、可重放审计和Owner审阅。检查器SHA `d1ed83a6be5981ddb1d3d1092be6d6c9fcbc5d9a6a2dd8dc96b5640e3ef5a297`；固定候选、原文SHA、AC及真实命令/限制已持久保存于本文，tmp不是唯一证据。

新旧两个任务tmp目录仍有独立QA、Human Owner最终验收及必要证据核对依赖，最终验收前保留。无自建服务/进程/端口、环境、worktree/分支；Verification不运行资源回收。最终验收后由当前active lifecycle coordinator核对归属、运行/后续任务/证据依赖再按workflow处理，不动未知或并行DS/DAA资源。

<a id="owner-acceptance-r2"></a>
## 10. 2026-10-21 Human Owner最终验收与资源收尾

Human Owner于**2026-10-21（Asia/Shanghai）**已明确最终验收，原话：

> ARCH-AW-007 r2 文档验收通过，更新相关状态并做资源收尾，保留 r1 历史和验证记录，暂时不改代码。

本节仅由原Verification owner记录已经发生的Owner决定，当前状态据此为`owner_accepted`。范围为§2冻结SHA对应的007 r2五份文档：`ROADMAP.md`、`ROADMAP.zh-CN.md`、AW白皮书、AW Runtime设计及SMA详细设计。AC01–AC14、153项检查、99处活动链接和原checker结果仍归§3–7原QA时点，没有重新QA、追加测试或重跑全仓checker。§1–9的final pending、资源保留和handoff文字保留为当时快照；当前终验状态以本节为准。r1完整前缀封存字节、原QA结论及r1自身final pending历史不追改。006仅保留设计`owner_approved`，不创建其角色文件，不扩展软件、运行、API/DB/PLC或发布授权。

主协调已先完成逐成员bytes/hash核对归档，再按workflow完成资源清理，事实见[完整文档验证历史归档](evidence/document-verification-history-r1-r2.tar.gz)与[资源收尾回执](evidence/resource-closeout.json)。归档保留64个成员：49份原临时文件、9份验收候选快照、5份r1交付正文快照及归档manifest；共1316252字节，SHA-256 `eaa260ad03a08aa5715bbe2086821bec346312a7131b27ef27759ab6e903f732`。其中`accepted-r2/plans/ARCH-AW-007-general-agent-fleet-roadmap/checklist.md`保存原QA版完整bytes，SHA `d6923eb82fa2dd9050957bb3f95e0ec2a6a197bd3b8236a6659a493f8246d0a5`；`r1-baseline/`与`r2-baseline/`分别保存原两个临时根的相对文件，原临时路径改从此归档恢复/审计，不再是唯一证据。

回执SHA-256为`91e6a9f82d7b2361f2d245a3206be5b08ef455853b630288ce2c8c5d8af5ffbb`，记录`cleanup.status=completed`，在2026-10-21 07:32:38 UTC（15:32:38 +08:00）完成删除49个普通文件与2个精确归属目录。依回执，协调清理前已确认无任务外引用、两根lsof无打开句柄、无symlink/不明文件，且目录仅在空后删除。清理执行者是主协调，Verification本轮未执行删除；本轮仅读取现成归档/回执及原QA稿，核对工件SHA和所存原QA bytes后记录验收事实，未启动任何软件或项目测试。正式五正文、spec/tasks和并行FieldFlow/DAA/DS资源未由本轮改写或回退。

主协调后续仅据本真实Owner决定机械同步八索引007行为`owner_accepted`并关闭状态；原STD、完整r1/r2证据和既有未实施边界保留。

<a id="r1-history"></a>
## r1 完整 Verification 历史

以下仅为真实r1独立qa_passed与final pending记录，不覆盖r2。每一原行（含空行）固定添加`r1|`三字节前缀；提取四反引号text fence内各行并去掉前三字节，可精确还原原UTF-8 bytes/LF及§4 SHA，不改原metadata、结论、命令、限制或证据。

<details>
<summary>展开 ARCH-AW-007 r1 checklist 完整原文（只读历史）</summary>

<!-- ARCH-AW-007:checklist:r1:BEGIN -->
````text
r1|Task ID: ARCH-AW-007
r1|Revision: r1
r1|Status: qa_passed
r1|Owner Role: QA / Verification
r1|Allowed Writers: QA / Verification, Human Owner
r1|Handoff: ARCH-AW-007 r1 AC01–AC14 独立文档核验 qa_passed；主协调可机械同步八索引，再交 Human Owner 最终验收；未授权代码、运行、设备、数据库、部署或发布
r1|Workflow Mode: STD
r1|Execution Mode: agent_team_same_session
r1|Task Namespace: aiis-ics-arch
r1|Classification: root
r1|Capability: AW 通用执行宿主、类型化连接器与 AWB/AWC 实例健康管理的全项目路线修订
r1|Owner: Automation World
r1|Acceptance Chain Reference: 本任务 spec 第 14 节；PM -> Human Owner 精确范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
r1|
r1|# ARCH-AW-007 r1 独立文档 Verification
r1|
r1|## 1. 输入、角色和验证边界
r1|
r1|2026-10-20，命名 `verification` 子调用 `/root/aw007_document_verification` 以 `fork_turns="none"` 的新上下文接续精确 r1 developer_handoff；未继承 Development 对话推理。独立阅读根 AGENTS、README/PLAN 双语、docs README 双语、根与 AW 任务目录、AW README/PLAN 双语、`.codex/agents/verification.toml`、canonical lifecycle workflow、完整 [spec.md](spec.md)（364 行）与 [tasks.md](tasks.md)（98 行）、五份交付正文和基线差异。另核对当前 DAA README 的 SQLite/上传未接入说明、006 metadata/范围及案例索引；这些现状引用不是新的运行证明。
r1|
r1|采用 `aiis`（含 BLUEPRINT）与 `project-governance`。本轮是文档核验，不加载实现 skill，也不运行构建、原生应用、服务、HTTP API、数据库、PLC、Docker、依赖安装或发布命令。读取到的 TOML 配置为 `gpt-6.1-sol` / `max`，仅作为配置证据；本上下文没有独立运行后端/effort 测量。本 profile 为 `contract_only`，依靠 fresh context、串行 handoff 和差异审计，不宣称平台 ACL、强制路由或技术隔离。
r1|
r1|Human Owner 的真实批准原话及其时序保留在 spec §14：“那就按这个方向，批准 ARCH-AW-007 r1，先同步双语 ROADMAP 和相关设计文档。连接器归 FOA 内部，DAA 继续保留做大量采集，SMA 和 CA 作为 FOA 的应用场景，暂时不改代码。”这是精确文档范围批准；最终验收尚未发生。
r1|
r1|## 2. 环境与固定候选
r1|
r1|- 正式交付工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD `0af5b91177f3bca63f9f3c2bef9f14004ea49944` 加本任务未提交增量。无临时源码副本、新分支、worktree、commit 或 push。
r1|- 文档辅助环境：macOS 15.7.7 arm64；`/Users/jason/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`，Python 3.12.14 stdlib。它只计算 Markdown、bytes、hash 和差异，不代表项目 runtime 验证。
r1|- 对照基线：`/private/tmp/aiis-aw007-doc-sync-20261020-gz1hgdga/manifest.json`，SHA-256 `c70f59de7d401a41fc4c1698deed5310597ae6cedcca90bc5ee872ebcd8cf364`。独立解码其中五正文、八索引 original bytes，并重算 1808 条保护路径；不以 Git 总 dirty 判定任务归属。
r1|- 首次独立扫描时间：2026-10-20 09:47:53 UTC（17:47:53 +08:00）。交接 hash、独立起点和以下候选一致。
r1|
r1|| 固定输入/交付正文 | SHA-256 |
r1|| --- | --- |
r1|| approved spec.md | `083d64b9ad274eed1a41380ad62e0d58757457a57a090eaffd880f8be1a0b494` |
r1|| developer_handoff tasks.md | `e8dfad1584329c1e2a92595854992683ff920b7a34eb9c632ca4b2e361f2d2de` |
r1|| ROADMAP.md | `a295be9e6c035f7509649c2d4f1f91552f4acfa6f904f260ef1ce27d4b3163c5` |
r1|| ROADMAP.zh-CN.md | `cf3e433bc5f951a39fab7512d724d6de7d8d29c09423b4badfe8221435592330` |
r1|| docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md | `e184158a3c2966905b6a8af7ed7f336a9d99213ceeec1e534b11c94613eadaa1` |
r1|| docs/AIIS_AW_Runtime_Design.md | `cb136a6a0513f78ca6e6eb616b5f83ce589f01ef1214ef8f74d11d35a7476dbf` |
r1|| docs/AIIS_SMA_Detailed_Design.md | `fa9179b715f992afe07756fd9ac9a7c7649c22b5b389a81394f7850023a17619` |
r1|| protected ARCH-AW-006 spec.md（仍 draft） | `7a96361040684832c9e78ae9ac9717e6cce90e6ed08a443a44a0dcc79fedff92` |
r1|
r1|## 3. AC01–AC14 独立结果
r1|
r1|以下行号来自上述冻结候选。`EN` 为 [ROADMAP.md](../../ROADMAP.md)，`ZH` 为 [ROADMAP.zh-CN.md](../../ROADMAP.zh-CN.md)。每项由实际语义走读与独立 bytes/结构检查共同判断，未将 Development 72 项 self-check 当作 QA verdict。
r1|
r1|| AC | 独立检查与精确证据 | 结果 |
r1|| --- | --- | --- |
r1|| AC01 | spec/tasks 的唯一 metadata、Task ID/r1、PM/Development owner/status 与 spec §14 的真实批准顺序一致；spec §1–2 区分 PM 起草九路径、获批五正文、后续角色文件，无 Parent 继承或虚构批准。批准 spec 和 handoff tasks hash 均匹配。 | pass |
r1|| AC02 | EN/ZH:70–99 明确 FOA 按身份、职责版本、实际 capabilities 与固定流程配置；SMA/CA 是场景/模板，标签不增加驱动或权限。DAA 保留为大量持续采集专用独立应用，完整 PLC→本地样本→未来 HTTP 确认链及替换 profile 的身份/历史/容量/原生/迁移等价门槛明确。EN:105、241 / ZH:105、242 保留 006 无登录、HTTP GET/POST/受支持 S7 的 draft 首版；006 hash 不变。 | pass |
r1|| AC03 | EN/ZH:76–97 的 Mermaid 与责任表覆盖 FOA、DAA、PW/Backend、AWB、AWC、CU/本机工作台；AWB/AWC 和事实确认边标未来。DAA 锁/SQLite/导入/诊断只作为工程参考（74 行），目录或初始化不被视为通用 Core/连接器/心跳交付。 | pass |
r1|| AC04 | EN/ZH:105–118 区分首版与后续多 PLC/HTTP/WS/外部 DB，可组合 DB→HTTP、WS→PLC、PLC→DB、HTTP→WS；连接器为 FOA 内部能力。协议/CPU/驱动及版本/OS/类型/读写矩阵与 planned/implemented/verified 分层明确，没有通配全部 PLC/数据库承诺。 | pass |
r1|| AC05 | EN/ZH:107、113–118 包含 WS 身份/快照增量/缺口/重连/游标/背压，DB 只读与写入、owner、表/操作、参数化查询、连接池/凭据、事务/隔离、幂等及 unknown 核实；任意 SQL/DDL 不在首版。EN/ZH:62–66、136、165/166 明确 PW Service/API 与获准外部集成 DB 连接器两类边界，不恢复 legacy 直写业务表。 | pass |
r1|| AC06 | EN:169–181 / ZH:170–182 七组字段逐项对照：稳定/部署/进程代次、duty、实际能力、assignment、configSource/desired/applied。克隆冲突不 last-write-wins；本机 SQLite 单一可写权威，中央迁移另定；received/validated/applied/failed 的 ACK 不等于执行，版本激活/降级/回退保留旧任务、unknown、outbox、游标与审计。 | pass |
r1|| AC07 | EN:183–202 / ZH:184–203 四种 register/heartbeat/query/assignment-ack 接口均标未实现、未冻结；五组心跳信息含身份/boot/seq、职责/版本、流程/积压/资源与 observedAt/receivedAt/lastSeen。当前有效代次的合格新心跳才刷新接收 TTL，旧 boot/重复/倒序/历史回放不恢复在线；周期、阈值顺序与有界 latest/离线保留可逐项走读。 | pass |
r1|| AC08 | EN:204–215 / ZH:205–216 将 Agent/管理链路、流程、外部连接、数据/进度四层分开，定义 unknown/online/stale/offline/conflict 与独立 degraded；online 可 degraded，offline 不证明进程死亡。原时间/质量、最后成功确认、缺口、lastSeen、pending 容量/最老年龄保留。 | pass |
r1|| AC09 | EN:163、215 / ZH:164、216 的管理失联仅继续本机已生效且不依赖在线资格的任务；重启 stopped/recovery_required 不自动执行。设备写租约按自身 fencing/续租/失联合同；心跳不是执行授权/HA 锁/写租约，备用实例不凭超时接管，unknown 继续用原身份核实。 | pass |
r1|| AC10 | EN/ZH:72、95–97、163–165/164–166 区分 CU、本机工作台与中央 AWC，AWC 经 AWB API/事件读取健康，不逐台直连 PLC/DB。只读健康先行，职责/配置发布、远程启停、自动运维分别另立合同；未来注册信任/通信保护不倒灌登录/JWT 到 006 首版，也不承诺永久匿名。 | pass |
r1|| AC11 | EN:219–234 / ZH:220–235 的 S0、S1、S2 前置、S2、S3、S4 有各自准入/完成 gate；保留 001 原初始化证据而不扩大验收。FOA 本地首版、连接器与 AWB 合同可并行；无新日期/支持完成声明，PG/Redis、HA/SA、OS 托管、PW/AIW 不成为心跳一揽子前置。 | pass |
r1|| AC12 | 独立逐段读完双语全文，对照 spec §10 的 §4/5/7/8 拟文及新增表格。两文均为 §1–9；§4/5/7/8 表行数分别 8/6/36/8，两语言对应一致；§7 的 43 个技术 inline 字段/URL/状态完全同集，Mermaid 节点标识相同。DAA 链路和构建关系的译文示意另作语义比对。§1/3/6/9 协调只针对本方向；§2 三界职责、TSS 可靠性及旧 writer 切换段逐字节未变。正文没有混入 spec AC、审批表或动态任务状态。 | pass |
r1|| AC13 | 白皮书:13、Runtime:6、SMA:6 均仅一次插入相同方向提示，去除两条新增行后与 manifest 原 bytes 完全相同（见 §4）。旧 SMA HTTP/表单/不连 PLC、两宿主和角色节点限制明确为当时范围；原原则继续参考，由后续实施 spec 明确替代。006 仍 draft、原 hash 不变，产线/实验室案例归 006（EN:241 / ZH:242），007 未复制客户案例或改写历史任务。 | pass |
r1|| AC14 | spec §12–14 和 tasks §6–8 具有风险、精确增量回退、待决、资源与后续 handoff；本任务无空角色文件或额外事实面。五正文新增/替换行的 21 处本地链接全部存在，fence/章节与 metadata 通过。checklist 创建后四 catalog 共 12 个真实角色链接有效，四 PLAN 仍只链接 spec；最终 checker 零 007 诊断且无新增历史诊断（§6）。 | pass |
r1|
r1|## 4. 原正文与允许变更审计
r1|
r1|独立以 `difflib.SequenceMatcher(..., autojunk=False)` 比较 manifest 原 bytes 与正式交付文件，并输出完整范围 diff。三份旧设计各只有一个 `insert` opcode，没有 delete/replace；白皮书新增行 12–13，Runtime/SMA 新增行 5–6。去增量后重算结果如下，不依赖“内容看起来相同”：
r1|
r1|| 原文 | manifest 原 bytes 与去新增提示后共同 SHA-256 |
r1|| --- | --- |
r1|| 白皮书 | `ac9d7d64d952eae999100eccd49e7b48a59cc590b306fbe66f96faf28836d8a4` |
r1|| Runtime | `1bda9d195609dba3540698813436f62b24fb1111d2500e6cb0ceaec9ff73676f` |
r1|| SMA | `e849bec4a4e29e587f16915b99b7e29d3774355b5d649be3b2f89ac724ea94b7` |
r1|
r1|双语 ROADMAP 的变化局限于 spec §2.2 允许的 §4/5/7/8 及必要 §1/3/6/9 协调。八索引的 007 行在核验起点均为 developer_handoff，PLAN 只链接 spec；四 catalog 已链接真实 tasks，未提前链接 checklist。排除 007 行后，四份根索引只另有并行 005 行更新，四份 AW 索引其余内容与本轮基线一致。
r1|
r1|1808 条任务外保护路径在首次独立扫描时：**1790 条 SHA 一致，18 条发生任务外并行变化**。具体为：
r1|
r1|- 005 `spec.md`、`tasks.md`；`docs/AIIS_DS_Detailed_Design.md` 与 `docs/README.md` / `docs/README.zh-CN.md`。
r1|- `automation-world/device-simulator/g0/` 的 `CMakeLists.txt`、`native_abi_probe.cpp`；`server/` 的 `main.cpp`、`owner.cpp`、`owner.hpp`、`protocol_hooks.cpp`、`protocol_hooks.hpp`、`resource_sample.cpp`。
r1|- `g0/vendor/snap7-1.4.2/controlled/src/` 的 `core/s7_isotcp.cpp`、`core/s7_server.cpp`、`sys/snap_msgsock.cpp`、`sys/snap_msgsock.h`、`sys/snap_tcpsrvr.cpp`。
r1|
r1|另有 manifest 外新增 77 条路径，全部位于 `automation-world/device-simulator/`。主协调确认 DS 并行工作继续推进；本角色未写或回退这些文件，不评价 005 的实施结果，不将工作树总体 diff 归于 007。上述计数仅为时间点观察，不能证明其他任务一直静止。历史 MULTI/002/003 bundle、006 及根 AGENTS/README/CODE_INDEX 等非本任务保护路径在该次扫描未变。
r1|
r1|## 5. 独立命令与结果
r1|
r1|工作目录为正式交付工作树。以下脚本为本 Verification 从基线独立编写的临时字节/Markdown 检查器，没有调用 Development 的 `check-docs.py`，也没有生成项目测试或修改依赖。
r1|
r1|| 检查 | 实际命令 | 结果 |
r1|| --- | --- | --- |
r1|| 交付 HEAD | `git rev-parse HEAD` | exit0；与 §2 HEAD 一致 |
r1|| 独立文档/metadata/bytes/链接/保护扫描 | `/Users/jason/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /private/tmp/aiis-aw007-doc-sync-20261020-gz1hgdga/verification-doc-audit.py` | 首轮 exit0，82 项机械检查零失败，21 本地链接零错误；spec/tasks/五正文/006 hash 全部匹配。此后补充三角色 Allowed Writers/namespace 检查，最终轮另记 §6 |
r1|| 正文空白检查 | `git diff --check -- ROADMAP.md ROADMAP.zh-CN.md docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md docs/AIIS_AW_Runtime_Design.md docs/AIIS_SMA_Detailed_Design.md` | exit0，无输出 |
r1|| checklist 创建前全仓治理 | `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch > /private/tmp/aiis-aw007-doc-sync-20261020-gz1hgdga/governance-verification-before-checklist.log 2>&1` | exit1，302 行；007 诊断 0，完整诊断多重集合与开发最后 302 行完全相同，新增/移除均 0。日志 SHA `c4ef6ede8d6276980000591879e71d3e3cd14cd201891057720c6500e8590bd6` |
r1|
r1|全仓 checker 不通过的事实保留：其历史/任务外诊断包括 005 归档 metadata 的重复计数和其他既有任务问题，不能宣称全库治理通过。本轮起点 302 行与 Development 末次一致；主协调原始前置 314 行的 12 行减少属于并行任务/索引变化，不记为 007 修复。最终 verdict 只覆盖精确 r1 文档范围，未修历史问题。
r1|
r1|## 6. 最终增量复核
r1|
r1|本 checklist 真实创建后，唯一主协调只机械更新八索引 007 行为 qa_in_progress 并补四 catalog 的链接；Verification 未代写索引。2026-10-20 09:53:20 UTC（17:53:20 +08:00）独立复跑 §5 文档审计命令，**exit0，119 项机械检查零失败**：包括三角色唯一 metadata/Allowed Writers/namespace、12 个 catalog 角色文档链接、四 PLAN 只链接 spec、本 checklist 的本地链接、21 处正文链接、三旧文单次纯插入及全部冻结 hash。spec、tasks、五正文与 006 均仍为 §2 的 SHA。
r1|
r1|同轮执行以下必要收尾检查：
r1|
r1|| 命令 | 退出码与结果 |
r1|| --- | --- |
r1|| `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch > /private/tmp/aiis-aw007-doc-sync-20261020-gz1hgdga/governance-verification-final.log 2>&1` | **exit1，302 行**；007 诊断为 0，与 Development 最后日志比较新增 0、移除 0，SHA 仍为 `c4ef6ede8d6276980000591879e71d3e3cd14cd201891057720c6500e8590bd6`。因此明确保留全仓未通过的限制，精确 007 范围无治理回归 |
r1|| `git diff --no-index --check /dev/null plans/ARCH-AW-007-general-agent-fleet-roadmap/checklist.md` | **exit1，无输出**；`--no-index` 相对空文件存在新文件差异，不是空白错误通过的 exit0。另以 stdlib 逐行扫描确认 0 条行尾空格/tab、文件以 LF 结尾（扫描命令 exit0） |
r1|
r1|独立检查器 SHA 为 `80ed56d1f0316b95888e7f1aaa07bed4ab2ffb376eaa6e77611f115bbdb30dea`。机械对称只用于技术字段/结构；14 项 pass 还依赖 §3 逐项语义核验，不能用计数代替双语阅读。
r1|
r1|并行时点观察在 09:53:20 UTC 更新为：**1785/1808 保护路径 SHA 一致，23 条任务外变化；87 条 manifest 外新增路径全部在 DS 内**。比 §4 首次扫描另观察到 DS README 双语、g0 README 双语和根 `CODE_INDEX.md` 变化，已通知主协调。这些是并行 DS 工作观察，不属于 007 的写入或本次验收；初始 18/77 与后续 23/87 两个时点均保留，不声称全工作树恒定。
r1|
r1|## 7. Verdict、限制与 handoff
r1|
r1|**Verdict：qa_passed。AC01–AC14 全部通过精确 r1 文档核验，无本范围 failure 或 blocker。** 全仓历史治理失败如 §5–6 保留，不记作本任务修复或全仓通过。
r1|
r1|QA → Human Owner：可以审阅 §2 固定候选并决定最终文档验收。主协调只据本 verdict 机械同步八索引；不改 PM/Development 事实，不将 006 draft 或旧任务验收追认为新范围批准。Human Owner 最终验收仍 **pending**，Verification 不授予 owner_accepted。
r1|
r1|本范围只验收路线及历史提示文档的一致、可审阅与可追溯性。后续 FOA 名称/目录/OS、连接器支持矩阵、正式 API/schema/身份信任/阈值、中央配置权威、远程操作/fencing/HA、DAA profile 替代等价和一切构建/原生/容量/现场证据仍依各自精确规格；006 首版不扩权，不创建 FOA 软件或中央平台。
r1|
r1|## 8. 资源归属与 Human Owner gate
r1|
r1|本角色在仓内只新增/更新本 checklist；本任务五正文、spec、tasks、源码、配置和测试均未写。独立临时资源位于主协调任务目录，归本 QA 的文件为 `verification-doc-audit.py`、`verification-doc-audit.json`、`verification-start-snapshot.json`、`verification-scope.diff`、`verification-audit-run.log`、`governance-verification-before-checklist.log`、`governance-verification-final.log`。用途为基线重算、范围审计、可重放检查和主协调复核；`verification-start-snapshot.json` SHA 为 `2c61fda95f906eeb7082aacba3823730393805d0ad26181c321fdbca82158614`。
r1|
r1|原 manifest、开发脚本/日志和 git-status-before 仍归主协调/Development。保留条件是独立 QA、Human Owner 最终验收及必要后续证据核对尚未完成；最终验收后由主协调确认无依赖再按 workflow 清理。Verification 不执行资源回收。本 checklist 已持久保存关键命令、结果、14 项依据、哈希和限制，临时路径不是唯一证据；没有自建进程、服务、端口、环境或安装依赖。
r1|
r1|Human Owner final acceptance：**pending**。仅 Human Owner 可记录真实最终决定；`qa_passed` 也不提供代码、设备、数据库、部署或 Git 发布授权。
````
<!-- ARCH-AW-007:checklist:r1:END -->

</details>
