Task ID: ARCH-DOC-001
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA2 -> Human Owner：ARCH-DOC-001 r1 rework1纯文档qa_passed，F-QA1-001/002对当前候选关闭，QA1失败原文保留；Owner文档最终验收pending
Workflow Mode: STD
Execution Mode: agent_team_same_session

# ARCH-DOC-001 r1 独立文档 Verification QA1

2026-11-05（Asia/Shanghai），当前结论为 **qa_failed**。AC02、AC07未通过，两个同源问题组尚未关闭；其余12项在下述纯文档范围及限制内通过。没有环境blocker，不以qa_blocked或DEV自检代替正文失败。本轮没有修复候选。Human Owner仅批准了精确r1实施，**文档最终验收pending**；产品、现场、采用、迁移、发布和部署没有获得新接受或许可。

## 1. 独立性、治理与写面

本实际命名`verification`角色为`/root/document_sync_verification_1`，在真实Development handoff及协调四索引固定后以fresh context消费输入；没有继承Development对话推理、委派子agent或代行PM/Development/Owner。独立读取根AGENTS、README/PLAN pair、最近作用域README/PLAN、verification TOML、canonical workflow、完整本任务spec/tasks、39件当前文档及diff、有关当前源码和所属任务最新有效QA/Owner段。应用`aiis`、`project-governance`、`code-document-indexer`，仅验证。角色profile仍为contract_only；配置中的model/effort不冒充运行遥测，不宣称平台ACL或强制路由。

唯一仓库写面为本checklist；创建发生于handoff后，进入时文件不存在。spec/tasks和39件候选在本轮内容审查期间固定。根PLAN/catalog四件归主协调，不算Development排除面漂移。没有修改其他任务证据、机器合同或产品文件；没有Git写入、分支/worktree、reset/revert/clean。通知执行窗及后续资源协调归唯一主协调，本角色没有重复计时、发送邮件或消息给外部人员。

正式工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`。现成系统工具：macOS15.7.7 arm64、Python3.9.6标准库、Git2.50.1（Apple Git-155）、zsh/bash。QA辅助脚本只解析本地文件、SHA、Markdown和只读Git输出，不导入产品模块，不读取真实env/profile/数据库，不安装依赖。

## 2. 精确输入与范围审计

| 输入 | 独立重算SHA256 / 结果 |
| --- | --- |
| HEAD | `0465f45ced6a2c8f8ca271b8bbf71f9eabc99de9` |
| [owner_approved spec](spec.md) | `98abeb870ca9b864d68dcaca5518252dca982cd7fb70d7918e7af135b71e80a3`；精确r1批准登记与42路径/R01–R11/AC01–AC14相符 |
| [developer_handoff tasks](tasks.md) | `9460a50d416ce598373bfb786bddee7327af886147d24ed603e0e510c7554040` |
| DEV/candidate35.json | `d3b78a35c8808672e9af380972b6f0bf49a95b72697f3851bd059dbc2fedf66b`；35当前after逐件匹配 |
| DEV/baseline.json | `b1f320a7ceda7cec4cf352554620a8aa0f358f8b434765241d0f7468821ebe18`；35个before原件与记录及HEAD字节均匹配 |
| PLAN.md（协调handoff） | `4b5cb1c4228ce7e869411fbe6e12e6c94c089bfcc5dc3304b3992b8cd1aa86f0` |
| PLAN.zh-CN.md（协调handoff） | `42c097b06892ac1a5aa32e752f6ab6a2354a75135dfefe0192fafb885e5eb942` |
| plans/README.md（协调handoff） | `9c57500a978406f20ecb59ca4638419157da7c8fb0ce6a21c50b5bbcb2dd72e0` |
| plans/README.zh-CN.md（协调handoff） | `95b8b598078a87f29e7f8151cf4bafb8655b29ab55d5d5525f9347b0b88a2516` |
| QA/candidate39.json | `888e8d63da67a8ec78bf6a91f2f924a6841e93b9f29ea2549125184c76d97b53`；按路径排序、UTF-8缩进JSON及末尾LF，固定39件实际候选 |

DEV=`/private/tmp/arch-doc001-r1-dev-8wce1wan`；QA=`/private/tmp/arch-doc001-r1-qa-77if5iew`。以上manifest实际读取并重算，不只复述tasks。35件前后SHA已在tasks逐件持久记录，协调四件如上独立固定。

从spec表重新解析42条唯一精确路径：39件既有MD＋3个分阶段角色文档。`git diff --name-only`恰为前39件，3506件tracked全集恰为39候选＋3467保护文件。3467件当前SHA逐件吻合DEV基线，覆盖产品源码/测试/脚本/依赖/机器JSON/schema/旧任务证据/既有发布事实；没有新增或删除tracked文件。进入时未跟踪项恰为本spec/tasks，之后只由本角色新增本checklist。此证明限定tracked源码保护面，不假称检查或重算过真实配置、数据库及历史数据。

AGENTS diff独立核实只有原第21/33行两次单行替换：FE装配及验收层级、DAA/冻结CA/FF职责；其余长期条款字节保持。39件diff均属获批事实/状态/图文/入口同步；`git diff --numstat`为429新增/310删除，没有任务外顺手改造。正文一致性失败见下一节，不能由allowlist和静态检查通过替代。

## 3. 必须返工的finding

### F-QA1-001：正式provider合同在当前正文仍被列为待定或让位于proposed需求（P2，R06/R09，AC02）

当前同一文档体系已写明BE009/010正式源码合同固定、隔离A+B验证通过，但以下现行正文没有历史标签，仍提供相反的决策入口：

| 位置（本候选行号） | 仍生效的残留 | 与当前事实的冲突 |
| --- | --- | --- |
| [Runtime设计](../../docs/AIIS_AW_Runtime_Design.md) §12，第241行 | 把事实匿名入口的正式schema/摘要/限额/混合批次矩阵，以及SMA HTTP目录/latest/raw编码与回执列为待决项 | 同文§5及provider已固定上述后端合同；真实采用、客户端实现与新扩展可以待定，既有provider字段/算法不能继续整体待定 |
| [DAA设计](../../docs/AIIS_DAA_Detailed_Design.md) §6.1，第263行 | “具体字节编码及摘要算法待 Backend 合同确认” | 同文§10.3第479行已说三类摘要/规范化/测试向量由provider固定；未来DAA编码器应消费该版本，不重新等待后端算法 |
| 同文§6.4，第304行 | 将历史已接收重复回执、批次退休与人工缺口接受合写为须另行定稿 | BE009历史确认/拒绝退休/派生矩阵已经固定；DAA本地处置、人工接受与产品实现仍可另批，不能一并推回后端待定 |
| [SMA设计](../../docs/AIIS_SMA_Detailed_Design.md) §7.2，第204行 | 新增模块typed入口信封“以业务投递需求与JSON为准” | 该链接的demand仍proposed；BE010正式OpenAPI/规范请求与摘要向量才是现行provider源码合同，需求只作来源/责任说明 |
| 同文§12.2，第322行 | “已接收历史回执与混合新/过期批次策略由 Backend 定稿” | 同Runtime/DAA问题，未指出BE009现行正式合同已经定稿，易把已完成合同工作误判为下一前置 |

独立源码旁证：[canonical.py](../../backend/app/plc_facts/canonical.py)第7/50/75–76行固定4MiB、pf-json/v1规范字节与域分离SHA；[batch_in.py](../../backend/app/plc_facts/schemas/batch_in.py)固定版本/摘要/片结构；[async_ingest.py](../../backend/app/plc_facts/services/async_ingest.py)第39–75、87–145行已区分historical_committed、proof_expired、全批拒绝/retirementAllowed及parent拒绝证据。两份[事实provider](../../contracts/published/http-api/plc-facts-v1/README.zh-CN.md)/[业务provider](../../contracts/published/http-api/business-integration-v1/README.zh-CN.md)及各自机器工件已有具体合同；本轮只读，未重新执行软件QA。

复现：仓根执行`python3 /private/tmp/arch-doc001-r1-qa-77if5iew/reproduce_findings.py`，真实exit1，F-QA1-001列出上述5处正文命中；不以helper匹配代替人工语义判断。相反当前说明可用`rg -n '现已由provider固定|已固定后端合同|正式provider字段/分页已固定' docs/AIIS_DAA_Detailed_Design.md docs/AIIS_SMA_Detailed_Design.md`复核。

原r1内的解除条件：在上述当前机制段原位引用正式provider，区分“既有合同已固定”与“DAA/SMA客户端、真实采用、人工缺口/扩展仍另立”；proposed需求保留自身状态和来源效力。无需修改机器合同或旧bundle，也不能只在页首再加一条免责声明。上述问题原先存在也不豁免本任务明确承诺闭合的当前冲突。

### F-QA1-002：DS总配置流仍将普通CAS保存直接连到新版本（P2，R07，AC02/AC07）

[DS设计](../../docs/AIIS_DS_Detailed_Design.md) §3第91行仍为：`页面草稿 → 服务结构校验 → CAS 保存 → 新 saved_revision → 用户选择实例并显式 apply`。缺少“保存同一草稿”与“另行保存为版本/清单确认”两阶段，仍使普通保存看起来隐式生成不可变版本；与本轮已改§4.1第107行、§4.2第115行及§15的当前语义冲突。

独立核对[当前手册](../../automation-world/device-simulator/USER_GUIDE.zh-CN.md)第53及128–135行：草稿保存不增加版本；显式保存为版本确认后才创建，随后停机加载，再独立启动。[configuration.rs](../../automation-world/device-simulator/runtime/src/services/configuration.rs)第67行只调用store.save；[transactions.rs](../../automation-world/device-simulator/runtime/src/infrastructure/config_store/transactions.rs)第8–73行只更新draft并返回原latest revision，另一个revise的publish分支才插入configuration_revisions；[versions.rs](../../automation-world/device-simulator/runtime/src/services/versions.rs)第142行另有preview_publish。均为源码读取，没有打开SQLite或启动DS。

同一复现helper真实exit1，F-QA1-002定位第91行。解除条件仅为原位补齐“编辑→CAS保存同一草稿→显式保存为版本并确认→停机加载→另行启动”，保留现有保护和重复内容规则，以及10月29日DIRECT仅DEV交付/手工确认边界，不修改或追认10月27日旧接受。

## 4. AC01–AC14独立结果

| AC | QA1 | 本轮证据与实际边界 |
| --- | --- | --- |
| AC01 | pass | 精确r1批准、STD/实际角色串行、42唯一路径、39当前diff、真实handoff后才创建本文件；spec/tasks固定，无替Owner接受 |
| AC02 | **fail** | tasks有逐R01–R11改写/保留映射，主要入口已同步；F-QA1-001/002证明当前正文冲突仍未闭合，不能接受“均已完成”的总体声明 |
| AC03 | pass | 原DAA007受控B接受及uploadAvailable:false；BE009/010最新隔离B+A证据与Owner/采用pending；SMA父draft/002003accepted/004QA2及正常执行拒绝；FF004r2 A QA3/005r1 A接受等状态核对一致。合同正文残留另由AC02失败约束 |
| AC04 | pass | 根/ROADMAP/Runtime/DAA/SMA将旧CA→monitor raw/latest→Projection与新plc_facts provider分开；虚线上传/可靠运行未接，两段ACK及业务/设备完成不混同；新CA/AWB/AWC/AIW未冒称交付 |
| AC05 | pass | 所有本轮当前SMA配置入口/图为Rust/单SQLite完整快照revision；UI/启动偏好独立，无Backend-held/localStorage多权威、正常fallback或Simulation复活；active/previous、outbox/运行库、GET→POST与新点身份适配保留后续 |
| AC06 | pass | AW007 r2原spec/Owner接受与本轮图文一致：FOA及合并宿主已替代，三应用独立，共享Core/画布/中央管理非近期前置；未擅自取消DS002/FF003/CA-CONFIG等未批准方向 |
| AC07 | **fail** | F-QA1-002使DS当前总流程仍冲突；其余10/27旧接受、10/29人工确认、加载/启动/保护及FF完整hold_ack/旧UTC、DS旧UTC和Backend真实时间采用限制均保留，未声称已修或迁移 |
| AC08 | pass | FE001第二轮QA、BE008 QA2与ARCH001 Owner原记录均支持索引纠偏；demand仍proposed，provider技术QA/Owner/真实采用分开；contracts K0–K3、旧head/阻塞/路径历史化，未给旧CA补造现场资格。正式合同引用残留仍为F-QA1-001/AC02失败 |
| AC09 | pass | 16 pair逐对审阅能力/状态/日期/gate/方法路径与本轮命令；状态与命令对称，日期中文短式与英文ISO上下文相符；INITIALIZATION旧注释翻译差异非新改。AGENTS中文canonical与五份中文设计无新副本 |
| AC10 | pass | 候选41 MD（39＋spec/tasks）离线1084本地文件/目录目标、120相关锚点，0缺失；标准reference-style定义0，引用扫描覆盖，白皮书来源标签按来源表核对；原隐式锚点无丢失，兼容显式ID保留 |
| AC11 | pass，静态限定 | 9 Mermaid块节点/边/状态图例/子图及围栏人工与helper静态核对；上传/SMA未来线、Backend隔离QA节点及旧兼容链分层一致。无mmdc/项目Mermaid依赖，未parse/render/视觉验证，不安装工具 |
| AC12 | pass | diff --check为0；独立治理checker当前385/root368既有诊断，0本新bundle诊断；根四索引实diff支持22条旧格式问题消失。3467保护文件及35before/after、4协调输入哈希通过；不要求全仓exit0 |
| AC13 | pass | INITIALIZATION每语13围栏原字节保持，其中8个操作命令块不变，只补6行关闭态/采用gate/手册；两provider目录只有README文字diff；正式机器工件/产品/旧证据/发布事实tracked不变；未运行产品/DB/Docker/网络或外发 |
| AC14 | pass | 本独立QA与DEV自检分离，失败/退出码/限制/资源明确；没有以QA授予Owner接受或产品、部署、发布终态；下一步返工和新fresh QA明确 |

原证据核对重点包括：[DAA007 Owner](../../automation-world/data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2)、[SMA002](../../automation-world/semantic-mapping-agent/plans/SMA-002-scope-cleanup/checklist.md)/[003 Owner](../../automation-world/semantic-mapping-agent/plans/SMA-003-cu-integration/checklist.md#owner-acceptance-r1)/[004 QA2](../../automation-world/semantic-mapping-agent/plans/SMA-004-local-configuration/checklist.md)、[BE009最新B](../ARCH-BE-009-backend-facts-integration/checklist.md)/[BE010最新B](../ARCH-BE-010-anonymous-business-integration/checklist.md)、[AW007 r2接受](../ARCH-AW-007-general-agent-fleet-roadmap/checklist.md)/[AW008 QA2](../ARCH-AW-008-stage-c-facts-contract/checklist.md)、[FF004 QA3](../../field-flow/plans/FF-004-plc-json-catalog-and-multi-plc/checklist.md)/[FF005 Owner](../../field-flow/plans/FF-005-basic-and-advanced-examples/checklist.md)、[FE001第二轮](../ARCH-FE-001-frontend-module-auto-assembly/checklist.md)/[BE008 QA2](../ARCH-BE-008-csharp-backend-plan-slice/checklist.md)/[ARCH001接受](../ARCH-001-public-architecture-baseline-extraction/checklist.md)。原失败和旧pending按时点读取，不以较早段覆盖最新有效结论；本轮未重算产品raw或重做原产品QA。

源码交叉检查另见SMA正常执行local_configuration::admit_execution/reject_execution及mapping_runtime正常manual/start/resume入口、启动自动入口，DAA bootstrap的uploadAvailable:false，FF Loaded::load→capability→State::open及Modbus拒绝，frontend moduleRegistry/glob与router共同装配，以及Projection input_resolver仍消费monitor旧raw/latest标量输入。它们是静态旁证，不是本轮产品测试结果。

16 pair库存：根README/PLAN/ROADMAP/INITIALIZATION；plans README；AW README/PLAN；docs README；contracts README/PLAN；plc-facts/business-integration provider README；backend README/PLAN；frontend PLAN；FF PLAN。9图库存：ROADMAP EN/ZH各2、Runtime1、DAA2、SMA1、DS1。每组实际读取；没有把“文件存在”当成语义通过。

## 5. 实际命令、退出码及旧诊断

所有命令cwd为正式仓根。QA指上述绝对临时根，不是项目运行环境。

| 实际命令/检查 | 退出及独立结果 |
| --- | --- |
| `git rev-parse HEAD`、`git status --short`、`git diff --name-only`、`git diff --numstat`及按文件分组`git diff --unified=0 -- ...` | 均0；实际39件diff、角色文件和受保护面按§2核对；只读 |
| `shasum -a256`批准spec/tasks、35manifest/baseline和四协调索引 | 0，全部固定输入与§2相符 |
| `python3 /private/tmp/arch-doc001-r1-qa-77if5iew/verify_scope.py` | 0；独立重算42/39/35before/35after/3467，AGENTS恰两行；创建checklist前再次0 |
| `python3 /private/tmp/arch-doc001-r1-qa-77if5iew/verify_documents.py` | 候选41文件最终0，1084目标/120锚点/9图/16pair/0失效；自身helper，不调用DEV检查器 |
| `python3 /private/tmp/arch-doc001-r1-qa-77if5iew/reproduce_findings.py` | **1**；F-QA1-001五处、F-QA1-002一处当前正文残留，与人工核对相符；是文档失败复现，不是产品测试 |
| `git diff --check` | 0，无空白错误 |
| `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch automation-world backend frontend-js contracts` | **1**，385既有诊断；原输出SHA `4e9cfa340e8a7ab8155f24e043103042e97963781a3069d294a4524d8f8b5596` |
| 同checker仅仓根参数，不带四模块 | **1**，368既有诊断；原输出SHA `d301285a580e7c7032f9c764020acd115f3d164e14f1321358206cc30311d1c9` |
| `command -v mmdc`；`rg -n '"(?:mermaid|@mermaid-js/mermaid-cli)"' --glob package.json --glob 'pnpm-lock.yaml' --glob '!**/node_modules/**' --glob '!**/dist/**' .` | 各1（无结果），无现成工具/项目依赖；未parse/render/视觉验证 |
| QA独立Python inline根索引归因及INITIALIZATION围栏对照 | 0；HEAD→当前根PLAN两语各5个非spec引用变为0；catalog两语各6个旧锚点链接改为checker所需角色文件实链；INITIALIZATION每语旧围栏保持 |

385分类为：364条旧重复metadata count、4条旧Allowed Writers、8条旧missing plans task link、6条旧missing模块catalog、3条旧find。root-only368=364＋4。两份输出均0条涉及ARCH-DOC-001；对应旧bundle与checker字节均受保护。全仓exit1不是本任务失败原因，也没有为了全绿批量修旧任务。

**407历史基线的证据限制：**407=364＋12旧role链接＋10 PLAN非spec＋8＋6＋4＋3，是协调提供的当时实测分类输入，未保存完整原诊断文件；本QA没有独立重跑当时环境或宣称完成407原始集合逐条差分。当前385/368由本QA独立运行并逐类核对；根4实际diff另证实10＋12项格式变化与减少22相符。此归因不替代正文一致性审阅。

QA辅助过程也如实保留：初版链接正则过宽及白皮书相邻来源标签造成计数偏低/4条undefined_reference假阳性，核对原文后仅修QA helper，最终重新扫描1084/120且0错误；INITIALIZATION旧翻译注释和中文短日期使结构counter出现false，人工确认原块不变及日期语义一致。若干只读定位命令先猜错模块路径产生No such file（rg exit2或被head管道掩为0），随后以rg --files取得真实路径并读取；一次zsh无匹配glob未读取目标，随后改用真实路径。治理分类初稿6条未分类，实际逐行核对为旧模块catalog缺失后归类。均无产品运行、候选写入或失败掩盖；findings来自最终实际正文，不来自这些辅助误判。

没有运行pnpm/uv/Cargo/pytest、应用/编译/软件测试、SQLite/MySQL或任何DB、Docker、真实env/profile/设备、HTTP或其他网络、迁移、依赖安装、Git提交/推送/refs、发布/部署和外部发送。

## 6. QA资源与串行handoff

QA唯一自有根`/private/tmp/arch-doc001-r1-qa-77if5iew`保留environment、独立scope/link/fence/pair helper、39候选manifest、41文件输入报告、findings.json及复现helper、两份治理原输出和归因JSON。无临时源码副本、venv/依赖、产品二进制、运行库、监听进程、设备或DB资源。关键哈希、最小复现、命令/退出、数量、verdict和限制已持久于本checklist，不以临时路径为唯一解释。DEV资源只读，未回收任何自身或他人目录。

保留条件：原候选/失败需供同r1返工、新fresh QA和Owner追溯；其依赖消失后由唯一主协调核实精确归属、占用、后续任务和证据保留，再定点回收QA/DEV自有资源，禁止按前缀批量清理。不能因本轮qa_failed而抹掉原候选或失败证据。

**QA1 -> 主协调 -> Development：**在原r1允许文档面一次性处理F-QA1-001/002，保持本QA1失败记录和原产品证据；完成后固定新的精确developer_handoff，再启动新的fresh-context Verification。两项都是已批准R06/R07的文档闭合问题，无需通过本QA扩大范围或重做产品QA。主协调可仅据本真实verdict把本任务四索引行推进为qa_failed并链接实际checklist；这种正常阶段/实链变化不自动触发全套重跑，本QA只读补核有据的四行变化及原候选保护。**Human Owner文档最终验收pending**。

## 7. 实际verdict后的索引补核与停止写入

本QA1完整失败结论创建后，协调仅把四索引中的本任务各1行改为qa_failed、实际checklist链接和同r1返工下一gate；没有启动正文返工。QA只读比较写前整文件快照与当前文件，独立确认每件恰1行替换，其他所有行保持。另一次PLAN pair用词校正仅将DS diagram/DS配置图精确称为DS configuration flow/DS配置流程；F-QA1-002指§3第91行文字链，不是Mermaid解析或图形失败。

| 正常阶段推进后的索引 | 独立核定最终SHA256 |
| --- | --- |
| PLAN.md | `7392c2f5485d15299b7eebc904f58c00727e7a68a630098c90c53ca637a9a217` |
| PLAN.zh-CN.md | `b20d40c2942a3b9b1d7e11c6088d5b041ee8c81be6fb315cae4f7dcc3e9ab302` |
| plans/README.md | `1c09b2ca0a843f1285440313158965a46b767d375ccad620bbff47265ba70310` |
| plans/README.zh-CN.md | `f7fc2a7e00ad44171d73aede2408d6ba60403e3e843d8c806d13f38c24bbf445` |

这些是§2原handoff输入之后有据的阶段变化，不覆盖或篡改原输入指纹。QA/final-index-audit.json记录确切行差及新SHA，35件Development正文、3467保护文件、HEAD和本spec/tasks再次通过只读SHA复核，exit0。无需因四行正常推进重跑整个产品或正文QA。

新checklist初建、catalog尚待同步时，同参数治理checker真实exit1/389：原385之外恰4条本catalog缺checklist实链（两语各重复2）。一次“应与385完全相等”的QA辅助断言因此真实exit1，随后逐行差分识别为阶段先后，不隐去或称旧基线。协调接入真实链接后再次运行同参数checker，真实exit1/**385**；输出字节与初始385完全相同，SHA仍为`4e9cfa340e8a7ab8155f24e043103042e97963781a3069d294a4524d8f8b5596`。阶段新增4条均消失，0新增可归因诊断。上述两个流程用词更正不改任何链接/metadata。

创建本checklist后，独立链接检查先得42 MD/1112本地目标/122锚点，协调catalog实链后为42 MD/**1114本地目标/122锚点**，均exit0/0失效；9图/16pair和旧锚点保全不变。`git diff --check`再次0，本checklist另由标准库检查14条AC、唯一metadata及尾空白为0，exit0。最终追加仅为本节实际收尾事实，不改变两个open finding或qa_failed。

QA资源仍按§6保留；没有删除资源、改变候选正文、追加产品验证或外发。**本QA1至此停止仓库写入，正式交主协调按F-QA1-001/002返工，再由新的fresh-context Verification独立核验。Human Owner文档最终验收pending。**


## 8. QA2：rework1 的新 fresh-context 独立文档复验（2026-11-05）

**当前独立 verdict 为 `qa_passed`，仅针对 ARCH-DOC-001 r1 rework1 的文档一致性；AC01–AC14 在本节列明的静态边界内通过。F-QA1-001、F-QA1-002 对当前候选关闭，无新的文档 failure 或环境 blocker。Human Owner 文档最终验收仍为 pending。**

本节是另一位实际命名 Verification `/root/document_sync_verification_2` 在新的 `fork_turns="none"` fresh context 中、真实 rework1 developer_handoff 及协调四索引固定之后独立执行的结果。没有继承 Development 对话推理，没有委派。上方 QA1 标题、§1–§7全部正文、原 `qa_failed` 判断、AC02/AC07失败及原输入SHA逐字保留为历史；只更新本文件顶层当前 Status/Handoff 两行并追加本节。旧 QA1 的“当前失败/停止写入”指它自己的候选与时点，不能误作本次新候选结论，也不能据本节把旧失败改成通过。

### 8.1 读取、独立性与精确输入

独立读取根 AGENTS、README/PLAN pairs、最近作用域 README/PLAN、verification.toml、canonical workflow、完整批准 spec、tasks §1–§13、QA1 checklist、正式候选及实际 diff，核对关联任务的最新有效 QA/Owner 段和相关源码文本。应用 `aiis`、`project-governance`、`code-document-indexer`，只验证文档。原产品 QA 作为已存在证据引用，没有重做产品、原生、协议或数据库验证。角色 TOML 的 model/effort 是配置证据；profile 为 contract_only，串行 handoff 和 diff/checklist 审计不表示平台 ACL、强制路由或新的产品许可。

正式树仍为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD 为 `0465f45ced6a2c8f8ca271b8bbf71f9eabc99de9`。系统 macOS 15.7.7 arm64、Python 3.9.6 标准库、Git 2.50.1（Apple Git-155）、zsh/bash；无环境或依赖安装。Python 只解析文件/JSON/SHA/Markdown及只读 Git 输出，不导入项目模块。

| 固定输入 | 本轮独立核算 SHA256 / 结果 |
| --- | --- |
| [批准 spec](spec.md) | `98abeb870ca9b864d68dcaca5518252dca982cd7fb70d7918e7af135b71e80a3`，27554 bytes；owner_approved r1，原42路径/R01–R11/AC01–AC14未变 |
| [当前 tasks](tasks.md) | `9e0447f0732e3af3b8a61cde0c52d63a0afa89bda1236c684a33b5f0953b523f`，32717 bytes；developer_handoff，§8–§13才是rework1，§1–§7历史正文核为未变 |
| QA1进入原全文 | `20aeb54cf5c95830555ef6a2e02228b52491cfd2fb07bac1cfaa34472f38c2fd`，23231 bytes；写入前已完整保存到QA2自有根的input-checklist.md |
| rework1 candidate35-rework1.json | `c28ab1140c42a3308957714425dd937671d321031cca29a5d14535ef9be7ae17`；35当前after全匹配，恰4变/31保持 |
| 原DEV baseline / 35 manifest | `b1f320a7ceda7cec4cf352554620a8aa0f358f8b434765241d0f7468821ebe18` / `d3b78a35c8808672e9af380972b6f0bf49a95b72697f3851bd059dbc2fedf66b`；35 before原字节、HEAD及3467保护文件逐项匹配 |
| rework1进入baseline | `50d8b67d8c3b092d666c68b1ea88642c006a0bd12dbf781e16895bc21577bb3a`；四件before实际原件匹配QA1候选，不用当前改后树反推旧稿 |
| QA2 candidate39.json | `f2e545b9f59f00e63b26bec1c3ee8903414a04459134f6ca690dd5352649ec90`；39路径排序的UTF-8缩进JSON及末尾LF，固定本轮内容核验输入 |
| Runtime 当前正文 | `c9ebd307c45932a52ee179b914552a1858d0bd181e8e53efd6ec61529b0af94f` |
| DAA 当前正文 | `bc179da342d6eef0ac7d9abe1d4c229eb2e6fa5629304dcadb03dc17912334c3` |
| SMA 当前正文 | `36bb4bf847009cedfccb19c61f2cc64dbaf4c4c4810ddf077cfbcfb39ac380c8` |
| DS 当前正文 | `ad13e9132c56a26324e9081f66873ab0659c7d4b899f622e4d067ff424bac2ba` |

进入QA2时协调四索引的精确输入如下；它们是同一批准范围内据真实 rework1 handoff 的正常阶段推进，不计为 Development 越界，也不替代 QA verdict：

| 索引 | 当前输入 SHA256 |
| --- | --- |
| PLAN.md | `d90f8eb719a4787d2a5ea7253637580137693c2ac53fe351e970becd82aac596` |
| PLAN.zh-CN.md | `b117012a8f2f66ae9002fe3d8b5c2b09b8b8eed145a50b63e2c87812fdf6d0a6` |
| plans/README.md | `2a49cf3c09b3a714ae2b08f45bdff779b17471319140bbd2b3c126d021c23f93` |
| plans/README.zh-CN.md | `3cdd8e9b9d0cd03512de421651e30ea8797f07d544e5253e989a877c2ab63dc1` |

从spec重新解析42条唯一路径，3506 tracked正好等于39既有候选与3467保护文件，当前diff恰为39件既有MD、437新增/316删除；未跟踪项只有本bundle三文件，无staged差异。35个before均与原件及HEAD匹配；当前35与DEV新manifest匹配。AGENTS只有原第21/33行两项获准事实澄清，其余长期规则字节保持。四件返工相对QA1恰六处正文变化，四件的5块Mermaid原字节未动；另外31件与QA1候选逐字节一致。QA2输入39全文和完整diff已另存自有根供机械索引推进后的有界复核。保护证明限于tracked源码/机器工件/旧任务证据，不声称读取过真实配置、SQLite、数据库或历史数据。

### 8.2 两个finding的独立关闭证据

以下结论来自原位正文、邻近上下文、正式provider及源码/手册交叉核对；旧字符串零命中仅为补充复现。

| QA1 finding / 位置 | QA2当前闭合依据 | 结论 |
| --- | --- | --- |
| F-QA1-001 Runtime §12，第241–243行 | 正式事实schema/编码/摘要/限额/latest/history、历史确认/混合批次拒绝/退休/派生归plc-facts/v1，typed业务归business-integration/v1；后段只将受控范围外协议、客户端本地处置/人工缺口及新扩展列待决。与§5已固定provider及§11候选分期一致，Owner/provider-ready/真实采用及DAA/SMA接线仍未授予 | closed |
| 同finding DAA §6.1，第263行 | 明确OpenAPI/schema/vectors与pf-json/v1规范字节/域分离摘要已固定，未来DAA编码/校验/持久重试消费同一版本；与§10.3及当前未接上传器一致，不再把后端算法整体列为待定 | closed |
| 同finding DAA §6.4，第304行 | 正式provider拥有历史重复回执、有限proof、整批拒绝、拒绝证明和退休/父批派生矩阵；未实施DAA本地终结/释放引用及人工接受另立。原冻结内容、unknown先核、拒绝不假ACK、不复活过期事实和满额停采约束保持 | closed |
| 同finding SMA §7.2，第204行 | 正式信封/闭合字段/规范请求/摘要/回执直接引用business-integration-v1的OpenAPI、examples与README；demand保留proposed需求/责任来源，示意业务内容不能替代正式信封。邻近稳定身份、sourceRefs、旧POST认证与actor边界保留 | closed |
| 同finding SMA §12.2，第322行 | 历史回执、有限proof和混合批次拒绝/退休/派生明确以plc-facts/v1为固定权威；DAA本地处置、SMA缺口接受/重同步及可靠运行仍后续，raw/latest不因历史ACK复活或延长 | closed |
| F-QA1-002 DS §3，第91行文字配置链 | 显式CAS保存同一草稿/ETag且不产版本→用户保存为版本并核工作区/清理清单确认→不可变版本（相同内容不增）→目标停止/连接释放后的预览确认加载→保持停止→另行start。与§4.1/4.2、§15操作顺序及保护语义一致，不是Mermaid解析修复；10月27日接受和10月29日DEV/待人工确认保持分开 | closed |

正式事实旁证为[canonical.py](../../backend/app/plc_facts/canonical.py)的4MiB、pf-json/v1字节及域分离SHA，[BatchIn](../../backend/app/plc_facts/schemas/batch_in.py)的固定版本/片/请求结构，以及[async_ingest.py](../../backend/app/plc_facts/services/async_ingest.py)的restore/historical_committed、proof_expired、拒绝证明retirementAllowed、parent核验和unknown不得退休分支。只用标准库读取正式OpenAPI/schema/vectors及业务OpenAPI/examples，确认为事实三operation和业务八POST的既有机器合同；没有执行生成器、改变机器文件或复制新的竞争合同。

DS旁证为[手册五动作和§2.5](../../automation-world/device-simulator/USER_GUIDE.zh-CN.md#save-and-load)、[configuration::save](../../automation-world/device-simulator/runtime/src/services/configuration.rs)、[transactions::save/revise](../../automation-world/device-simulator/runtime/src/infrastructure/config_store/transactions.rs)和[versions::preview_publish](../../automation-world/device-simulator/runtime/src/services/versions.rs)：普通save更新configuration_draft并返回原latest_revision，明确发布另走revise/publish与预览清理清单；手册明确停机加载且另行启动。latest/selected/loaded/有效预览保护及previous放弃规则仍在当前手册/§15，未新造运行证明或追认旧接受。

### 8.3 AC01–AC14当前独立结果

| AC | QA2 | 当前证据与限制 |
| --- | --- | --- |
| AC01 | pass | 精确批准r1及STD串行、实际命名fresh角色、42唯一写面；spec/tasks输入固定，QA仅写checklist；39现有diff及本bundle无越界 |
| AC02 | pass | tasks逐R01–R11映射保留；本轮六处当前正文及邻近语义按§8.2闭合，两finding关闭；原QA1失败与有日期历史未删除/改写 |
| AC03 | pass | 原任务最新有效段核准DAA007受控B/上传未接，BE009/010隔离A+B/Owner与真实采用pending，SMA父draft/002003接受/004 QA2及关闭正常执行，FF004 r2 A QA3/005 r1 A接受等；31未变候选与QA1一致，新6处未扩大能力 |
| AC04 | pass | 根/ROADMAP/Runtime/DAA/SMA区分旧CA→monitor→Projection、新plc_facts与未接上传/业务链；事实ACK、业务ACK和设备完成继续分层，新CA/AWB/AWC/AIW仍未来 |
| AC05 | pass | 当前SMA Rust/SQLite完整单快照revision/CAS、UI与技术偏好分离；正常manual/start/resume源码均在client/spawn前reject_execution，正常准入admit_execution同样拒绝。旧TSS仅来源/显式fixture，无Simulation/fallback复活；可靠runtime/outbox/版本发布及新身份适配仍后续 |
| AC06 | pass | AW007 r2原Owner接受/替代关系与当前图文相符，FOA及合并宿主已替代，共享Core/画布/中央管理非近期前置；DS002/FF003/CA-CONFIG等未批准方向没有被擅自取消 |
| AC07 | pass | §8.2关闭DS文字流程冲突；草稿/发布/加载/启动与保护引用统一。10/27旧接受、10/29待人工确认、FF完整hold_ack及FF/DS旧UTC、Backend实际时间采用限制全部保留，未宣称已修/迁真实历史 |
| AC08 | pass | FE001第二轮源码装配QA、BE008 QA2和ARCH001 Owner原记录支持索引纠偏；AW008 QA2/proposed与后续provider隔离QA分开；K0–K3旧root阻塞/head/路径保留为历史，不给旧CA新增现场资格 |
| AC09 | pass | 16既有pair语义/状态/gate/日期/方法路径及命令核对；本轮返工四件均为中文设计，不改变pairs。日期短写沿上下文与英文ISO同义，INITIALIZATION旧注释翻译不同但各自原块未动；AGENTS仍唯一中文契约，五设计无新语言副本 |
| AC10 | pass | 当前42 MD独立离线检查：写QA2前1123本地目标、122相关锚点、0失效，reference-style定义实际0且扫描覆盖；旧隐式锚点无丢失、兼容ID保持。写后数字见收尾，不以旧计数冒充新全文结果 |
| AC11 | pass，静态限定 | 9 Mermaid（ROADMAP两语各2、Runtime1、DAA2、SMA1、DS1）围栏/节点/边/子图/class/图例及当前/未来语义核对；四返工文档5块原字节不变。无mmdc/项目Mermaid依赖；未parse/render或做视觉验证，无工具安装 |
| AC12 | pass | git diff --check为0；当前checker385/root368均独立复跑且与QA1原输出逐字节相等，0本任务或新索引可归因诊断；42写面/35before及after/3467保护与metadata唯一通过；不要求全仓exit0 |
| AC13 | pass | INITIALIZATION两语各13个围栏原字节保持（其中8操作命令块），仅新增边界/手册导航；provider目录只有README文字差异，机器JSON/源码/旧任务/已发布事实保持；没有产品/DB/Docker/网络/外发 |
| AC14 | pass | DEV自检与本fresh QA分开，真实命令/退出/辅助错误/限制/资源完整；QA2通过只进入Owner文档终验，产品、部署、发布和真实采用无新增接受/许可 |

原记录读取包括DAA007 Owner登记、SMA004 QA2/父001及002003状态、BE009/010当前B段（旧A/失败尾部不覆盖当前）、FF004 QA3及FF005 Owner/hold_ack/UTC限制、FE001第二轮、BE008 QA2、ARCH001 Owner、AW007 r2 Owner及AW008 QA2。没有重新核算旧产品raw或把原QA引用写成本轮新运行结果。

### 8.4 实际命令、治理诊断及辅助限制

下列命令cwd均为正式仓根。Q2=`/private/tmp/arch-doc001-r1-qa2-wwmuvnz9`。

| 实际命令/检查 | 退出及本轮结果 |
| --- | --- |
| stdlib Python进入快照/SHA、`git rev-parse HEAD`、`git status --short`/`git diff --name-only`/`git diff --numstat`及分组diff | 0；精确输入、39候选、正文/索引角色、437/316及保护面如§8.1 |
| `python3 /private/tmp/arch-doc001-r1-qa2-wwmuvnz9/verify_scope.py` | 0；42/39/35前后/3467、31未改及4件原Mermaid、tasks历史及单份metadata均通过 |
| `python3 /private/tmp/arch-doc001-r1-qa2-wwmuvnz9/verify_documents.py` | 0；42 MD/1123目标/122锚点/9图/16pair/0失效，旧锚点无丢失；日期/注释counter差异另人工核准，未把counter作为语义oracle |
| `python3 /private/tmp/arch-doc001-r1-qa2-wwmuvnz9/reproduce_findings.py` | 0，no_listed_residue；先读QA1 helper，因其会写findings.json，复制后仅改输出根为Q2，未运行或覆写QA1原helper输出；正文/源/手册审阅另见§8.2 |
| `git diff --check` | 0，无空白错误 |
| `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch automation-world backend frontend-js contracts` | 1，385条既有诊断；原输出SHA `4e9cfa340e8a7ab8155f24e043103042e97963781a3069d294a4524d8f8b5596`，与QA1同参数385输出逐字节相等 |
| 同checker仅仓根参数 | 1，368条既有诊断；SHA `d301285a580e7c7032f9c764020acd115f3d164e14f1321358206cc30311d1c9`，与QA1 root输出逐字节相等 |
| `command -v mmdc`；仅package.json/pnpm-lock的Mermaid依赖`rg` | 各1且无输出，无现成工具；未parse/render，不能从静态核对声称视觉通过 |
| stdlib JSON读取两个正式provider及SHA/图库存、关联源码`sed`/`rg` | 0；只读，不导入业务模块、不执行生成器或产品QA |

385分类独立重算为364重复metadata、4旧Allowed Writers、8旧missing plans task link、6旧missing模块catalog、3旧find；root368=364+4。当前两份输出均无ARCH-DOC-001诊断。原407完整日志不存在，本轮继续保留QA1已经说明的历史证据限度，只确认当前385逐字节相等，不重新构造407原始集合或宣称全仓通过。QA2写入只改变两个允许的当前metadata值且新增段无重复metadata；机械索引推进再做有界复核。

辅助过程如实记录：初次写入后QA1恢复helper误在已含末尾LF的前缀再加一个LF，断言真实exit1；随后只改QA2自有审计算法，去掉额外LF即恢复23231 bytes及原SHA，原QA1正文无需修改。一次只读FF源码定位先猜错`src/runtime/bootstrap.rs`及`src/plc_catalog.rs`，rg真实exit2；随后用rg --files找到实际config/runtime catalog并读取，未据失败形成产品结论。若干批次工具输出被长度截断，改用分文件/分段和六处before原件差异继续审阅；未以截断结果充作完整差异或失败证据。没有候选编辑、产品运行或工具安装。

### 8.5 资源、验收审计及handoff

QA2唯一自有根Q2保存输入spec/tasks/QA1完整原件、39候选文本及完整diff、candidate39/entry/scope/governance-audit、复制且只改输出位置的离线helper、六处四件最小diff、链接/图/pair库存、findings空结果及两份治理原输出。没有临时源码工作树、venv/依赖、产品二进制、运行库、监听进程、设备或数据库资源。旧DEV根、rework1 DEV根及QA1根仅只读消费，均未回收或覆写；关键输入SHA、证据、结论和限制已持久在本checklist。

保留Q2用于Owner文档终验和追溯新旧候选/失败；待唯一主协调核实精确归属、无运行/后续/证据依赖后定点回收，QA不执行资源删除。通知执行窗由主协调管理，本角色不另启计时或外发。

| 验收层级 | 当前事实 / 下一gate |
| --- | --- |
| 原QA1候选 | qa_failed及F-QA1-001/002失败永远保留；不因返工通过倒改旧结论 |
| 当前r1 rework1文档 | 新fresh QA2 qa_passed，AC01–AC14静态范围通过，两finding对当前候选关闭 |
| Human Owner文档最终验收 | pending，唯一下一接受gate；本角色不代授或推断 |
| 产品/真实采用/现场/长稳/发布部署 | 本任务没有运行或新增许可；各自原任务状态与独立gate保持 |

**QA2 -> 主协调 -> Human Owner：**当前文档候选可交Owner文档终验，无实现返工项或环境blocker。主协调只能据本真实verdict机械同步根PLAN/catalog的本任务各1行及真实QA2链接；QA随后只读有界核准这四行有据变化，追加收尾后停止写入，不无条件重跑产品或整套文档QA。Owner文档最终验收pending。


## 9. QA2实际verdict后的四索引补核与停止写入

QA2当前verdict保存并交主协调后，主协调仅机械推进四件索引的本任务各1行。QA2用进入时保存的整文件原件对照，独立确认每件恰1行替换、其余所有行原字节保持；当前两语均为r1 QA2 qa_passed、14项文档标准通过、两finding关闭、QA1失败保留及Owner文档终验pending。PLAN仍指spec，catalog保留三份实际角色文件实链；新旧目标列表完全相同，无链接或metadata结构变化。

| 正常推进后的索引 | QA2独立核准 SHA256 |
| --- | --- |
| PLAN.md | `9ba39f9f06373ec562929dcaab384f148feae9b964e5bb5a799b6ca0321e92e2` |
| PLAN.zh-CN.md | `dd19e210f807eecb3b663812bd1dfb52e36d70f77a4b464eb7e9b057ea0c3150` |
| plans/README.md | `a404959210f2bf7b73ef91eb447918c76ac9f1a41c2e83b674e4a956f4776337` |
| plans/README.zh-CN.md | `70c83b7fac14648e27e8e3e9e71d00cb48d6f652b44485c95e3267c4d274ee1f` |

这四项有据的阶段变化不覆盖§8.1原输入。当前39最终索引态manifest SHA为`7c7354657b27d2d50e605c936549f04f26885294946ef5c4d6c7385935e5cc4b`，保存在Q2/candidate39-after-index-sync.json；原candidate39.json和原全文快照保持。35件Development正文、3467保护文件、HEAD、批准spec及当前tasks再次全部SHA匹配，原QA1全文逆转两项metadata仍精确恢复23231 bytes及`20aeb54cf5c95830555ef6a2e02228b52491cfd2fb07bac1cfaa34472f38c2fd`。

写入QA2正文后实际离线检查为42 MD、1132本地目标、123相关锚点、0失效、9图/16pair；本次四行目标不变且本收尾不增链接，数量保持。`python3 /private/tmp/arch-doc001-r1-qa2-wwmuvnz9/final_audit.py`实际exit0，记录精确行差、目标、保护和历史恢复；`git diff --check`再次exit0。顶层八项metadata仍各唯一、14条QA2 AC均pass、checklist无尾空白。治理385/root368既有诊断的原输出及相等证据保持；本次只校验既有合法metadata值及不变链接结构，没有重跑产品或全仓检查以制造新的资格。

QA2资源按§8.5保留，没有清理或更动他人资源，没有运行应用、软件测试/编译、DB（含SQLite）、Docker、真实配置/设备、网络/外发或Git写。**QA2至此停止仓库写入，交主协调转Human Owner文档最终验收：ARCH-DOC-001 r1 rework1为qa_passed，F-QA1-001/002当前closed，原QA1失败保留；Human Owner文档最终验收pending。**
