Task ID: ARCH-BE-009
Revision: r1
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner 已于2026-11-05接受本次获批源码及隔离MySQL A+B交付；原独立qa_passed与全部历史保留；本角色登记完毕并释放写入，协调者机械同步索引
Workflow Mode: STD
Execution Mode: agent_team_same_session
Independent QA Verdict: qa_passed
Owner Accepted At: 2026-11-05 Asia/Shanghai
Record Purpose: Owner final-acceptance receipt only; no new QA run

# Human Owner最终验收登记（2026-11-05）

Human Owner在本会话引用[主-DAA](codex://threads/01a143e5-5616-76c0-9df7-13b487bc9c26)的验收建议，明确表示“可以作为我我的验收语句，我授权”。当前lifecycle coordinator核对该会话最新答复后，转交Owner采用的完整原句如下：

> 验收 ARCH-BE-009 r1、ARCH-BE-010 r2 在本次获批源码及隔离 MySQL A+B 范围内的交付，接受独立核验结果和已记录限制。请完成验收登记及无依赖临时资源收尾，保留必要证据。已有数据库和真实历史不动，实际环境采用、DAA/SMA 联调及生产部署另行批准。

本记录只登记上述真实Owner决定在ARCH-BE-009 r1的效力；ARCH-BE-010 r2由其所属checklist分别登记。独立A+B结论保持`qa_passed`，当前本任务状态为`owner_accepted`。此前“Owner pending”、A/B各阶段批准与失败/返工内容均保留为其发生时点的事实，不回写历史，不新增验证结论。

| 验收对象与边界 | 本次登记 |
| --- | --- |
| 精确获批交付 | 固定B候选`joint-B-candidate.json` SHA-256 `2532d8423c73f0e9c0a7ac42d616014b2ca09419588cd07a0218bd4ce080cafb`，及下方完整A/B独立证据、失败历史和已记录限制；本任务[spec](spec.md)仍为r1。 |
| 当前工作树关系 | closeout entry记录当前HEAD为`0465f45ced6a2c8f8ca271b8bbf71f9eabc99de9`，区别于QA时的`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`。本次只读哈希核对：候选157实现条目中148份原样，2份获批spec均原样；另9份是后续Markdown文档变化，全部保留且不纳入本次验收，不声称当前159项/HEAD整体等于旧候选。 |
| 后续文档差异 | `CODE_INDEX.md`、`backend/README.md`及`.zh-CN.md`、`contracts/README.md`及`.zh-CN.md`、两个published provider目录各自的`README.md`及`.zh-CN.md`；精确前后SHA见closeout entry。 |
| 仍独立推进的gate | 实际目标schema/时间采用、准入启用、DAA上传器与阶段C实际接线、DAA/SMA联调、生产部署、现场/真实PLC及生产长期SLA继续按各自范围另批；本次接受不改变默认关闭/未采用的运行边界。已有数据库、真实历史和DAA配置/历史保持不动。 |

## 已授权资源收尾与保留证据

此前专用运行资源已按具体B批准完成回收并由独立QA核验：2容器、2卷、2网络、8个随专用卷移除的schema，以及27份生成口令/key/操作配置均已清理。其原收据和独立缺失观察完整保留在下方；本次没有重建资源、Docker/数据库查询或读取/恢复秘密配置。

本次实际收尾执行者仍为当前lifecycle coordinator。其只读自有进程盘点为0个B进程；在确认无运行依赖后清理115个自有`__pycache__`/`.pytest_cache`/`uv-cache`目录，共438份缓存文件、2,229,142 bytes。9,763份非缓存证据在清理前后的SHA逐项一致，冻结源码副本、原始命令/日志/报告、diff和失败证据均保留。Verification本次只读消费该收据，没有执行删除或新增运行验证。

五个B证据根继续保留：`/private/tmp/arch-be009-r1-b-dev`、`/private/tmp/arch-be010-r2-b-dev`、`/private/tmp/arch-be009-r1-b-qa`、`/private/tmp/arch-be010-r2-b-qa`、`/private/tmp/arch-be009-r1-be010-r2-b-my8s9bnu`。用途为已接受基线审计和DAA阶段C交接；待这些证据依赖结束、必要结论已持久化后，由协调者确认归属再回收重复临时证据。closeout根`/private/tmp/arch-be009-be010-owner-closeout-4iqs6drx`仅为本次验收/一致性/资源审计保留，同样在交接证据依赖结束后回收。关键QA结论、限制、命令结果、定量守恒、资源身份及本次收尾数量均已在任务checklist中持久化。

| 本次只读输入 | SHA-256 |
| --- | --- |
| closeout根`entry.json` | `91a9b5b6600df44334ad261f33938011fe749e9c6f8c02c3f11c41999c7519f0` |
| closeout根`resource-closeout.json` | `e46a6d45385305f1d29eba8ef6e8bba43c440f38953e64a9e42890a4d15fd379` |
| 原B专用运行资源`cleanup-receipt.json` | `23048893ca4c71a6fc7ca76d0e9a466371c41e6fda15880458f8515cac5e41cb` |
| 下方验收前完整checklist原文 | `01803851a120c38c083290b30b42e0c5adac106c7edec618622195a4156d431c`，66,252 bytes，作为完整原始字节后缀保留。 |

本次沿用原实际Verification角色，仅使用project-governance核对验收文档归属；复读适用契约与完整bundle，使用stdlib `python3 -B -`进行文件SHA、元数据、UTF-8、前置段链接/空白及原文后缀检查，exit0。不重跑A/B测试或扩大原QA结论，不改spec/tasks/实现/测试/配置/索引，不进行数据库、Docker、DAA、真实环境/历史、邮件或Git动作。写入仅限本checklist前置收据；此前66,252 bytes完全不变，完成后向协调者报告最终SHA并停止写入。

---

# 验收前B/A原始完整记录（历史，以下字节原样保留）

Task ID: ARCH-BE-009
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: fresh B QA1 -> Human Owner：r1 A回归及获批隔离B通过；主协调已按具体批准回收专用资源且QA独立核缺失；最终验收pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Stage: approved isolated MySQL 8.4.6 B; A regression
Verification Iteration: B QA1, fresh context after B Development handoff
Verified At: 2026-11-04 Asia/Shanghai

# B QA1独立验证结论

**本轮 ARCH-BE-009 r1 获批隔离 B 的独立 verdict 为 `qa_passed`；A181及旧44回归、公开MySQL整9零skip、47具名扩展与补充矩阵、1b3 schema-only及最终联合清理/retained均完成。没有新的产品failure或B blocker。Human Owner最终验收、provider-ready、部署、DAA/阶段C和生产长期SLA未由此取得；专用资源已由主协调回收并经QA只读独立核验，见资源关闭收据。**

本轮真实Verification身份为`/root/be009_r1_b_verification_qa1`。由主协调以fresh context在BE009 B完整developer_handoff后启动，不继承Development对话推理。本profile为contract_only；任务bundle、串行handoff、diff/checklist审计是合同控制，不宣称平台ACL或强制路由。verification.toml声明gpt-6.1-sol/max只是配置证据。

Owner原话：“批准 B 操作提案，按 STD 完成 ARCH-BE-009 r1 和 ARCH-BE-010 r2 的两轮隔离 MySQL 8.4.6 验证及专用资源清理。现有数据库、真实历史数据和 DAA 不动。”本轮完整读取具体`B-operation-proposal.md`。QA只执行其专用QA资源和四schema；root最后统一资源回收。普通验证只使用非root/当前schema，未读取Dev秘密配置。

| 固定输入/环境 | 已独立确认事实 |
| --- | --- |
| 正式工作树/HEAD | `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，共享未提交工作树。QA不修产品/测试/spec/tasks/索引。 |
| 共同候选 | `joint-B-candidate.json` SHA-256 `2532d8423c73f0e9c0a7ac42d616014b2ca09419588cd07a0218bd4ce080cafb`；157实现+2获批spec全部逐项匹配正式源，640份公开backend/contracts源码复制到QA目录，未携带真实dotenv/SQLite/环境。 |
| BE009 B handoff | tasks SHA-256 `d303f4ab8354cc60954aa85aed6c329b9809e68477d3661ffbb803bdd54fb743`；7文件manifest `36df6af4caafea3fac278f8a350ce092808f05e0f34ab66b6025f0cc73bb9307`已读，DEV自检仅为输入。 |
| 原A记录 | 以下完整保留38789 bytes、SHA-256 `9028135809c9963a9e3967bff441710b364f5d9ecafe9cc24a2cc3dcc27d3385`原文；包括A QA2通过和QA1失败，不改写历史未批准边界。 |
| QA专用容器 | `arch-be009-be010-proof-qa-mysql`；ID `4dc2c195c5d800c792684c97a61f66a4ad7bef12cc35b343d6b47c3eed906bf2`；127.0.0.1:33380→3306。名称/端口均确认空闲才创建，未复用/删除未知资源。 |
| QA专用卷/网络 | 卷`arch-be009-be010-proof-qa-data` CreatedAt `2026-11-04T13:05:41Z`；网络`arch-be009-be010-proof-qa-net` ID `f3ae03e4c91a3fee11bce68011867d738fdde437623003eb169483a7678d2dc5`；全部标签`aiis.task=ARCH-BE-009-r1-ARCH-BE-010-r2`、`aiis.round=qa`。 |
| 镜像/账号 | 已有固定mysql:8.4.6，imageID `sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`；nonroot `be009_be010_qa`权限仅四库。root仅创建/授权这些库并已关闭。 |
| 四schema | `arch_be009_r1_qa_schema`、`arch_be009_r1_qa_facts`、`arch_be010_r2_qa_joint`、`arch_be010_r2_qa_time`。joint/time后续显式串行交QA010，无交接不修改joint。 |
| 真实运行设置 | VERSION=8.4.6、global/session time_zone=+08:00、REPEATABLE-READ、CURRENT_TIMESTAMP/UTC_TIMESTAMP实际差28800秒。普通项目命令用既有uv环境，offline/frozen/no-sync，无依赖安装、API TCP listener或现有数据库连接。 |

证据目录`/private/tmp/arch-be009-r1-b-qa`（0700）；`resources.json`脱敏保存完整资源身份。独立随机root/app口令、四epoch、cursor key、runID只在本轮`connection.json`/`docker.env`0600，inventory仅列路径。本轮guard在产品导入前阻断真实dotenv/SQLite/listener及非精确33380/当前schema/本轮nonroot连接，primary使用never_connect_primary哨兵。MySQL loopback/Docker使用Owner已批具体动作的sandbox升级，不扩展范围。

本轮中期真实记录（最终联合收尾已经完成，见下文）：公开B整文件9 passed/12.45s，零skip/warning；最终正式树九个A整文件181 passed/30.27s；旧认证/权限/CA/Projection/模块/response六整文件44 passed/9 deselected/53.26s。preflight、metadata75/pending4、唯一迁移链、Model/DDL、独立F7/9摘要、OpenAPI/ref闭包、24链接/3JSON及targeted compile均exit0。

独立六份矩阵共47个具名场景已完成（含自然月纯规则与真实存储结合；不把纯规则冒称DB年月自然流逝）。B45/B46/B47分别exit0：逐点1005/1001/坏值、来源代次/定义CAS、跨批固定片、父token换key、真实T1 rawID commit/rollback/disconnect、Decimal/纳秒/大小写Unicode、全typed ASGI/四在途429、flush/commit/close/rollback确认丢失、2001位置扫描、混合原文到期及value/proof满配额恢复。B53 exit0：historical ACK不复活/不续120d、历史proof+新事实、合成proof/父proof过窗、24h新批终结、floor两ordinal及binding分页失效。

B49真实SQL已经清掉201条原文，随后QA私有报告用wire canonical序列化float耗时而TypeError，exit1保留。未改产品/测试；B51用新命名fixture及标准JSON报告重跑exit0。201条原文分116/85/0行、348/255/0bytes、3事务清完，实际已提交持锁87.982/63.058/10.933ms；200引用proof前缀不饿死尾proof、2MiB事务留800000bytes、3次SQL后故障真实rollback/counter/degraded/恢复、NOWAIT28ms和完整serial前缀均通过。B52 exit0：2001积压分1079/922行，两tick各10事务，壁时1.093/0.957秒；实际API写优先于cleanup（NOWAIT34ms）；两次一次性tick相隔60.00286秒，无OS调度。26小时合成积压触发SLA告警；不建立生产长期SLA证明。

QA010明确交入joint后，B50 schema-only exit0：live1b3/75/F7=1ba...，原state/六事实表逐行匹配0a2冻结；未再核验前latest503。plan逐字无变，apply只改schema_profile/verified_schema_revision/adoption_evidence/last_db_time/updated_at；原epoch/adoptionId/source binding/六表/proof/水位/counter不变。真实原POST恢复同receiptId、latest值0、history同contentDigest，全部200/json；进程exit0/双engine dispose后明确交还QA010。后续已按其明确无连接/事务交接完成B70同fact/proof合成到期清理、68非facts全行守恒及QA010原154请求retained；详见最终联合记录。

B48非空downgrade为预期exit1（明确all seven tables empty and unadopted保护），B54后验0a2/71及旧64全结构/两条合成旧行ID/值/精度保持。B55 facts全部操作后旧64结构/行摘要不变。B56/B57最终独占库只读审计exit0：facts valueBytes/proofRows=1074886/5307、schema=4229/9，均等于实际SQL统计，cleanupFailures=0；两库0a2/71/F7/上海时钟/RR正确，除当次审核自己无其他facts/schema连接，随后dispose退出。joint/time连接由QA010负责，不用此断言它们已停止。

## AC01–AC12最终验收审计

| AC | 本轮独立证据与当前结论 |
| --- | --- |
| AC01 | 真实ASGI三路200、403/409/410/413/415/422/429/503/500，Content-Type、完整typed JSON、原身份/摘要/上海时间与DB副作用核对通过。B43/B44/B46/B50/B63；无API TCP listener。 |
| AC02 | 独立encoder构造原材料/贪心片，不用产品canonical生成expected；真实UTF8 BLOB、>28位Decimal、9位时间/789ns、Case/case/中_文及Sample/sample完整二进制键通过，精确REAL越界422整批零副作用。A181与B45/B46。 |
| AC03 | 同批稳定ACK及原raw/cycle/feed/latest/batch原子，真实commit后丢ACK、commit后close失败、真实flush后rollback确认丢失均unknown并按原身份恢复；全JSON/脱敏、不假rollback。B44/B46/B63。 |
| AC04 | 完整固定片跨批收齐及首次partial ACK稳定；混合无证明过期全拒无部分事实，父token换key仍持久同token、合法子集继续、篡改/缺父/过期父拒绝。历史proof+新事实只增新raw。B45/B53。 |
| AC05 | 1005点A/1001点B、同点旧序/等序冲突、新bad替good、相同定义换context/revision保留旧点、禁用撤资格/旧窗口只raw、代次切换清空后从1开始；两PLC同DB及单PLC两DB/组。B62两真实会话首次采用同expected0，一方NOWAIT3572，旧CAS重试409，旧latest/counter不变。 |
| AC06 | 三真实独立Session场景T1已rawID停commit、T2不能发布、reader不越H，commit/rollback/断线后原身份恢复/后页不漏；晚观察时间新serial、2000扫描预算空页续、range冻结H/original原字节、24h/15m/30s过窗、floor序号/ordinal与key/filter/binding失效均通过。 |
| AC07 | 自然月/月末/闰年纯规则结合真实ns持久；真实SQL同microsecond ns788/789/790截止前/等/后；混合成员raw原文最早到期但其他latest保留，物理未删时不泄漏；120天不续期/historical不复活/过窗410。真实DB+08/RR、进程UTC/DB时钟倒退拒绝。合成到期并非改变系统时钟或自然等待120天。 |
| AC08 | 独立真实201饥饿/引用proof、2MiB/200行/10事务/2000行/20MiB/100ms/2s边界、3故障rollback/计数/降级恢复、26h告警、两次60.00286秒tick与写优先NOWAIT已过；B59真实CLI SQL后故障为预期exit1/failed JSON，B60同确认串exit0恢复。最后B70仅原1fact/proof真实清理，68表335行结构/完整行不变；QA010原154请求retained后仍逐字不变，跨owner不级联通过。 |
| AC09 | 四新库明确f6/64→0a2/71，空七表回退/重建、非空回退拒绝及旧64结构/全行/ID/Decimal守恒；独立反射新F7=1ba...。joint已真实1b3/75、schema-only显式再核验及epoch/source/proof/水位守恒。B64实际DB unknown/multiple revision仅在当前未提交事务造fixture并拒503后rollback，无DDL/stamp/未知迁移；实际36长度反射对临时37长度内存预期拒绝，finally还原且最终F7正常，不冒称修改了物理列。 |
| AC10 | 旧六migration和640公开backend/contracts依赖未改；旧六整文件44 passed/9 deselected、真实旧monitor未登录401，facts操作后旧64全结构/行摘要不变。新facts不写旧owner或读取PLC；联合68表335行及业务引用经B70清理和对方154原请求复验后守恒；本QA独立读取其154条完整状态/JSON/sourceRefs/mapping并核对前后68快照字节相同。 |
| AC11 | A default-off/空scope/profile/key保护及真实scope/媒体/格式/容量/来源拒绝；4个真实在途reader的第5请求429/Retry-After1，释放归0。DB门闩、来源first-adopt/CAS与同批并发均真实裁定；错误无密码/key/SQL泄漏，scope不是认证。 |
| AC12 | A181+44、B公开整9零skip、47具名扩展与CLI/CAS/HTTP/profile补充、preflight/compile/JSON/ref/链接/7文件逐字diff/159候选及2718全entry审计已完成。只写本checklist；完整A历史保留。最终联合收尾完成，本轮verdict为qa_passed并只进入Human Owner最终验收gate；QA通过与Owner终验/部署/DAA分别处理。 |

本轮没有新的产品failure。原QA1产品失败、A QA2通过和DEV的B三项修复历史均保留，DEV自检不替代本轮新QA。当前B63真实HTTP409/410及旧monitor401完成；B64用未提交SQL metadata fixture验证未知/多revision拒绝并rollback，用临时内存model长度预期对真实MySQL反射验证不匹配拒绝并finally还原；没有DDL、stamp或未知迁移，也没有采用未知真实库。

QA辅助失败真实保留：B49已完成201行实际SQL后，报告错误地使用wire canonical序列化float耗时而exit1；B51用新命名fixture及标准JSON报告通过。audit01把协调者PLAN更新误纳冻结运行依赖比较而exit1；audit02把三份B entry原字节不变的旧performance文件49行尾空白纳全文断言而exit1；精确归因/缩到本B7与checklist后audit03 exit0且git diff --check所有候选exit0，未改旧文件或断言。最终joint B67错误固定另一短fixture的4229bytes而exit1，B68只读证明原QA冻结就是4275/3、实际计数相等、六表diff={}；B69误用inspect(Session)在快照读前exit1。两者均未进入expiry或cleanup写入。只修QA自有helper为原冻结预期及current Connection，B70完整真实执行exit0。所有失败helper原字节、log和退出码保存，没有修产品/正式测试/spec/tasks或静默改变verdict。对方retained报告实际为154份HTTP记录加2份汇总（共156项）；初版QA reader把总项数误断言为154而exit1，未进入记录检查。分开HTTP与汇总后独立读取全部156项，154份status/Content-Type/完整wire/JSON/sourceRefs/mapping检查均通过，原失败及新reader结果保留。

## 最终联合清理、串行交接与业务独立保留

QA010在完成业务/故障/Projection及68表冻结后，明确joint无事务/连接并暂交本角色；time从未由本角色再次连接。B70先核live1b3/75/F7=1ba...、原epoch/adoptionId/highSerial1、原六表逐字与QA冻结相同、value/proof=4275/3等于实际，然后只给这原1batch/1sample/1cycle/1latest及其有限proof建立明确合成到期。没有改系统时钟、原材料/摘要/来源/业务值或运行DDL。

真实owner CLI plan预测5行/4275bytes/2proof；apply实际6行/4275bytes/3proof、2事务、整体57ms（最后空事务5ms），exit0。raw/latest/cycle/sample/batch全清，value_bytes/proof_rows=0并等于实际，floor从(0,0)到(1,1)；highSerial1、原epoch/adoptionId/source binding/F7保持。68张非facts应用表的完整结构与335行（FLOAT用CAST DOUBLE后精确hex）前后逐项相同；没有业务级联。原实际tail cursor的after恰等floor，仍200空；合成有效未消费(0,0)cursor得到410/requiresResync。清后没有重放近期原facts wire制造合成expiry下的不真实复活。

B70进程exit0且双engine.dispose后，立即明确交还joint给QA010，之后本角色不再连接。QA010 Q31使用完全相同154个永久业务原请求及旧JWT原请求/完整GET retained，exit0/30.42s；Q32最终68结构/335行、154身份/独立摘要/sourceRefs/mapping/父子守恒exit0/7.02s。其清前、replay后、最终68快照原字节SHA均为`dd4cea6bbb69ccb2320d57d566ee1a404a7c8e9376d8ce1199fb1231b9b73774`。本角色独立读取154份完整实际HTTP200/application-json/duplicate/no_auto_ttl原wire/响应，核对sourceRefs均指向本轮原sample/point及mapping；独立比较对方清前/后68快照原字节相等。该输入只关闭本任务跨owner清理边界，不替BE010授最终QA verdict或Owner验收。

## 实际命令、环境与退出码

W=`/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend`；Q=`/private/tmp/arch-be009-r1-b-qa`。项目环境Python3.13.3、uv0.7.8；无install/sync。普通B命令完整前缀为`cwd=W UV_CACHE_DIR=Q/uv-cache PYTHONPYCACHEPREFIX=Q/pycache uv run --offline --frozen --no-sync python Q/run.py <精确schema>`，guard切至冻结Q/source/backend。逐条展开后的真实argv、schema、exit、耗时和唯一tag/log见Q/commands.json（另有commands-classified.json）；A及stdlib审计完整argv见auxiliary-commands.json，不省略真实失败。

| 真实命令组（前缀后argv） | 实际结果 |
| --- | --- |
| stdlib`python3 -B Q/create_resources.py`；既有项目uv运行Q/provision.py | 0；Docker名称/端口空闲后只建QA专用三资源；固定镜像已存在，未pull；root仅建/授权四库，非root核版本/+08/RR/28800/四grant后关闭root。 |
| 四精确schema各`-m alembic upgrade f6a8c0e2b4d6`、Q/snapshot.py baseline64、`-m alembic upgrade 0a2c4e6f8b10`、Q/snapshot.py snapshot71；schema库seed64/空downgrade/reupgrade | B10–B35全部0，64→71及旧64结构/合成行守恒；schema库2行旧ID/Unicode/0.0001/12.3456/999999.9999保持。 |
| Q/adopt.py；三个精确schema分别schema/facts/joint，time未采用交QA010 | B40–42均0；独立反射对冻结A语义逐对象相同、singleton无AUTO_INCREMENT、CLI plan无控制行写入，apply显式采用；原context SHA/expectedBinding0/seqFrom1。 |
| Q/formal.py；实际pytest argv为`-q --tb=short --confcutdir=tests_mysql --basetemp=Q/formal-temp -o 'markers=mysql: dedicated isolated MySQL B' -p qa_formal_fixture -p no:cacheprovider tests_mysql/test_plc_facts.py`，只在schema库 | B44 exit0，9 passed/12.45s，零skip/warning；06/09的明确合成expiry/120d fixture由QA外层建立，没有shared破坏性conftest。 |
| Q/qa_extended.py、Q/http_precision.py、Q/bounds_capacity.py、Q/qa_cleanup.py新fixture、Q/cleanup_load_ticks.py、Q/expiry_restore.py | B45/B46/B47/B51/B52/B53均0；47具名报告，关键真实结果如AC矩阵。B49 helper exit1不覆盖。 |
| Q/cli_fault_exit.py、Q/cli_recover.py、Q/cas_race.py、Q/http_remaining_status.py、Q/profile_faults.py | B59预期exit1且failed JSON/真实rollback；B60/B62/B63/B64均0，分别重入、两会话CAS、409/410/旧401及可回滚profile拒绝补充。 |
| schema库`-m alembic downgrade f6a8c0e2b4d6`；Q/snapshot.py postRefused | B48预期exit1，明确all seven empty/unadopted保护且无DDL；B54 exit0确认0a2/71、旧64全结构/两旧行守恒。 |
| Q/snapshot.py postCleanup；Q/final_db_audit.py；Q/guard_probe.py | B55/B56/B57/B58/B61/B65/B66均0；10个拒绝探针在IO前阻断外部/Dev端口/root/错schema/primary哨兵/SQLite/listener/真实dotenv；CLI裸/help不导入settings/database。最终独占库详情如下。 |
| joint库Q/joint_pre.py、Q/joint_revalidate.py、Q/joint_cleanup.py | B43/B50/B70 exit0；0a2原事实冻结→QA010升1b3→schema-only plan/apply及三路→QA010业务冻结→同fact/proof cleanup→QA010 retained，均逐次明确交接。B67/B69 helper前置exit1、B68纯读0保留。 |
| `cwd=W UV_CACHE_DIR=Q/uv-cache uv run --offline --frozen --no-sync python Q/a/guard.py Q/a/run_suite.py focused`；同前缀Q/a/surface.py；Q/a/run_suite.py legacy | A01/A02/A03均0；181 passed/30.27s、static/compile/preflight/contract/link通过、旧44 passed/9 deselected/53.26s。正式测试副本逐字匹配，产品直接导入正式树，A完全拒DB/网络/SQLite。 |
| stdlib Q/audit.py及whole-entry核验 | 最终0；159候选与640副本完整匹配、六旧迁移不变、2718 entry中2695不变，23变更恰为13获批B产品delta、4角色文档、6协调索引；含215份DAA公开文件不变，未读SQLite/真实env。 |

maintenance的真实CLI参数均为显式`--target-alias arch-be009-be010-proof-qa-mysql --schema <当前四库之一> --expected-schema-revision <0a2c4e6f8b10或joint的1b3d5f7a9c20> --expected-storage-epoch <本轮该库独立epoch> --operation-approval Owner-approved-B-operation-proposal-2026-11-04 --confirmed-by BE009-Verification-B-QA1`。adopt含明确context-file/SHA、plc/instance/generation/config、expected-binding-revision/seq-from；schema-only另含`--revalidate-schema-only --expected-adoption-id <原ID>`且无source参数。先`--plan`，后`--apply --confirm APPLY:<action>:<alias>:<schema>:<同epoch>`。完整展开私有argv保存在各schema-adopt-argv.json、joint-revalidate-proof.json、joint-cleanup-proof.json、cli-fault-proof.json；公开记录不复制私有运行标识/key/口令。

最终B65/B66独占库：facts live0a2/71，valueBytes/proofRows=1073096/5306与实际一致、high2231/floor(1,2)、6条合成source binding；schema live0a2/71，4229/9与实际一致、high6/floor(5,1)。均F7=1ba...、VERSION8.4.6、session+08、RR、实际UTC差28800、cleanupFailures0；除了当次审计自己无其他facts/schema连接，随后dispose退出。保留的raw/latest/proof是本轮仍有效合成fixture，不假称全库过期。joint最后B70已双engine.dispose并交QA010，其最终停止/无连接由该角色和主协调统一核验；本角色无运行runner、HTTP listener或调度。

## 证据摘要与资源handoff

| Q内证据 | SHA-256 |
| --- | --- |
| `resources.json` | `5998efaa748e04a5c2b45da262d411e7c470ccbb8e561a94206fd1a439851a1e` |
| `commands.json` | `f7861e0f81c6df4ed7dc64ef8dc397d6f364a24b2bcab3253a51f3e283f543c2` |
| `source-audit.json` | `9cd80e6693ff11e69c7b57b533e0c334a6b618e4ac64127bdfb68d377acf2425` |
| `whole-entry-audit.json` | `d16f0ad7549d011d8e9cb9121f181c7d5080926a05b23ac53cc00fedba23a8dc` |
| `independent-7-B.diff` | `6c377796240ccdb9bbf4dd045a67dad572a346e6fea287b32c78a334a2ae8b03` |
| `B44-formal9.log` | `36959deb650f32cfd1630c4c96826d7f6bb25b2fcdaf41e641ef8a3f2cf842fd` |
| `A01-regression181.log` | `449c6880fe88cf4e563109dfd9e6a8ec05f0baa9a7b3e190658a00ba5e50be69` |
| `A03-legacy.log` | `df66b3195e6c2683e55afc2a7e07c30ea0977b0803b91bc7c6caa4dd85c63896` |
| `a/surface-report.json` | `290ef14bb70dde5108a887b7c52444a54ca1de1aa52f4b58f41724b72bdb1681` |
| `cleanup-report.json` | `28610423d0b31d44219b34d61b3fb436ec7b21523aacd59545f2ee0c106da328` |
| `cleanup-transactions.json` | `da573de464c99eb6174ef54c32eedb43f7fb331aba4e387802e029c38df9b538` |
| `cleanup-load-report.json` | `75e805a5bad929a65c04fb53ef04237c9645b70402d76c85db70420cd2cc1f1b` |
| `joint-revalidate-proof.json` | `d28e2332ea1f38e0255839096e3301eec85a85bc4496bda0f7e021f976ce70e7` |
| `joint-precleanup-diagnosis.json` | `72a1951c5b4c5775daf1623998389c3d799f11f813777671aed57e84e2a6808d` |
| `joint-cleanup-proof.json` | `60beb25f207d4a4f0211f97cb60a61123edc6211cf29fe0c870019da652d9088` |
| `peer-retained-evidence.json` | `e936c5de4acd330b518d04da103410fa84e3850d59c1eea6f80a1ac4ee96fa38` |

关键输入、实际命令/退出码、AC结论、定量守恒、失败归因与资源身份已经持久化于本checklist，不只依赖临时路径。原A38789字节完整保留；本轮唯一仓库写入为本文件，没有写spec/tasks/产品/测试/配置/六索引。正式未提交交付树/HEAD及共同candidate2532...与已验证公开副本一致，不把临时副本当唯一交付。

QA自有资源仅Q：640公开源副本、逐字测试副本、独立helper/fixture、原失败helper/log、argv/反射/全表快照/报告、pytest basetemp/cache/pycache/log。无branch/worktree/commit；无依赖安装、真实DB/历史/配置、DAA/SQLite/PLC、Compose或外部服务操作。专用QA容器/卷/网络在QA交接时按顶部resources身份保留；现已由主协调在两角色无后续连接/运行依赖后，核ID/labels/CreatedAt按Owner具体批准与Dev轮资源统一回收，QA未执行删除，独立核验见下方收据。镜像为原有资源，不属于新建回收对象。

敏感文件原inventory仅路径：`Q/connection.json`、`Q/docker.env`，生成时均0600，现已由主协调删除并经QA独立核缺失；独立root/app口令、cursor key、epoch/runID未进入仓库或公开日志。Q本身0700，运行proof/argv仍为私有证据；主协调清理时保留必要脱敏证据并回收不再依赖的自有副本/缓存。PM/A/其他角色资源不归本QA删除。

| Gate | 最终结论/下一步 |
| --- | --- |
| ARCH-BE-009 r1 B QA1 | `qa_passed`；A回归和本次获批独立隔离B通过，无新的产品finding/blocker；原A QA1失败/QA2通过和DEV修复史不覆盖。 |
| Human Owner | 接收本独立结论并决定精确后端范围的最终验收；**final acceptance pending**，QA不代授。 |
| 专用资源回收 | 已由主协调按已有具体批准统一完成；QA独立核精确ID不存在、端口无监听及27配置路径缺失，零DB连接/零QA删除。 |
| provider-ready/生产/DAA/阶段C | 仍需Owner范围接受及各自独立运行采用/部署/DAA软件与双方联调gate。无现有数据库/真实历史迁移或DAA改动；不把两次受控tick和合成expiry冒充生产调度、24小时长期SLA、备份/介质擦除或现场证明。 |

## 主协调资源关闭收据与QA独立复核（2026-11-04）

主协调按Owner原先精确批准于`2026-11-04T22:10:52.665327+08:00`完成清理；这只是资源关闭事实，不授QA verdict或Human Owner最终验收。`cleanup-receipt.json` SHA-256=`23048893ca4c71a6fc7ca76d0e9a466371c41e6fda15880458f8515cac5e41cb`，`owned-resource-cleanup.json`=`2c7df8944739811cadc1ac1286f4807b33e9b516140eb4b70b7548c25b155d95`，`sensitive-cleanup.json`=`230ee3c391b98001b87cdbf3e437903d7cd0c025b0fbdc8559ead7d3930e9b0a`；三份收据位于主协调B根目录`/private/tmp/arch-be009-r1-be010-r2-b-my8s9bnu`，本QA逐字重算SHA相符。

QA只读命令`python3 -B Q/observe_cleanup.py`真实exit0，未连接已删数据库、未执行删除或读取敏感文件内容：核QA原containerID/networkID/volumeName/CreatedAt与创建记录及root收据相同；分别对Dev/QA精确containerID和容器名、networkID及volumeName运行`docker <type> inspect <精确身份> --format <Id或Name>`，共8项均预期exit1且为No such/not found。对33379/33380各运行`lsof -nP -iTCP:<端口> -sTCP:LISTEN`，均预期exit1且输出空，两个端口无listener。原有`mysql:8.4.6`镜像仍为`sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`，未回收既有镜像。

因此两专用容器、两卷、两网络已不存在，八专用schema随其数据卷回收；没有再尝试SQL探库。root报告清理数据库连接数0、未触其他资源/现有数据库/历史或DAA；本QA自身复核同样0数据库连接/0资源删除。27份清单生成口令/key/操作采用配置路径逐项exists和symlink都为false，包含本QA原connection.json/docker.env两项；不是只复述收据。准确只读argv/exit/输出、27个路径及QA身份核对在`cleanup-independent-observation.json`，不包含秘密值。

必要脱敏证据、公开源码/测试副本及before/diff仍保留于BE009/BE010各Dev/QA四个自有临时目录和上述主协调B根，供Human Owner最终审阅及证据追溯；没有可运行的专用DB、口令或后续运行依赖。收据固定回收触发为Human Owner最终接受、且确认无证据/后续任务依赖后由主协调再回收这些自有目录；A历史/其他任务资源不归本B回收。关键定量结果、verdict及关闭事实已在本checklist，保留的tmp不是唯一结论载体。

本轮最终仍为`qa_passed`，无新产品failure/blocker，**Human Owner final acceptance pending**。专用测试资源清理完成不等于生产部署、真实时间采用、DAA上传/联调或现场验收。

清理后Development只在tasks末尾追加本次root资源收据，当前tasks SHA-256=`4ebf8fe3d8cf98c136256c3b962ad14f730d423b6fad9d899fd71c553573f4f6`；QA独立重算证实前66677 bytes仍逐字重建本轮输入`d303f4ab8354cc60954aa85aed6c329b9809e68477d3661ffbb803bdd54fb743`，仅追加2901 bytes收尾事实，产品候选不变。

QA独立资源观察证据`Q/cleanup-independent-observation.json` SHA-256=`a01d3ece8e39465cb694e3dc50bf58374062410623105098018e2ef0314bcace`；清理后只读source/checklist/path审计再次核159候选、640副本、原A后缀、Git空白和27路径缺失，零新凭据读取/零DB连接。最终资源/Owner gate以本收据为准，之前“仍保留/待回收”均为各自执行时点的历史。

---

# 既有A QA2/QA1原始完整记录（历史，以下字节原样保留）

Task ID: ARCH-BE-009
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA2 -> Human Owner：仅r1 A返工1源码/no-DB独立通过，F-QA1-001/F-QA1-002在A范围关闭；B/G-B、provider-ready及Human Owner最终验收pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Stage: A source/no-DB only
Verification Iteration: QA2, fresh context after Development rework-1
Verified At: 2026-11-04 Asia/Shanghai

# QA2：r1 A返工1独立结论

**本次精确候选的A源码/no-DB verdict为`qa_passed`。** 九个完整正式任务测试文件178 passed；QA2自建、未写入项目测试目录的70项独立检查通过。F-QA1-001的三类清理饥饿与F-QA1-002的精确REAL边界均在A范围关闭。没有新增产品failure或A blocker；这不是B、真实持久化/并发/DB时间/物理清理SLA、provider-ready、部署、DAA上传或阶段C验收。

本角色为`/root/be009_r1_a_verification_qa2`，在Development返工1重新handoff并停写后开启新fresh context，独立读取文件、实现、diff与测试输出，没有继承Development对话推理，也不是QA1继续验证。项目verification.toml声明gpt-6.1-sol/max；这是配置证据，不冒充本角色独立观测到的运行模型值。profile为contract_only，串行handoff、精确输入、checklist/diff审计是合同控制，不宣称平台ACL或强制路由。

**QA1原全文20646 bytes完整保留在本文最后，原SHA-256为`acf3620e7198e22aabec4f06d4e4f7c1a45a093cac26d188c3e1683535c9a246`。** 其失败结论、六反例、旧候选F7和未运行边界都不改写。以下QA2结论仅对应新候选；QA1原文中的“未关闭”描述仍是旧候选历史。

## 精确输入、范围与并行例外

| 输入 | QA2核对结果 |
| --- | --- |
| 正式交付树 | `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`；共享未提交工作树，无新commit/worktree。产品始终直接导入正式树。 |
| 获批spec | `26121323384f2b8fd590921f53c477d759b564cf5214078c05834496a4884f48`；r1顶部与第15节收据匹配，A源码/no-DB获批；数据库/Docker/实际迁移/B与DAA未批准。 |
| 本次tasks | `83ce92402ef694a8043d809818565ecdb3368e72f2ab340b3fa15ff7a0ccdde1`，返工1已developer_handoff；QA未改写。 |
| 新57文件manifest | `/private/tmp/arch-be009-r1-a-dev/rework-1/implementation-manifest.json`，SHA `4f7b57c21fb512bf2cb8c0eb6a9cb43599a3bd9656b6cff890d0d3a85e9e0776`；57项逐个匹配正式源。相对QA1仅7实现/测试文件改变，另有tasks更新；其余50及全部3份机器JSON保持原hash。 |
| 本次原70文件入口 | 主协调`be009-qa2-entry.json`及QA2原样副本`candidate-entry.json`，SHA `a79153da882392964e5a75dea454cda0fc2274ebd1cf28bdf27efb168a825562`；开始70项全部匹配。收尾69项保持，CODE_INDEX例外见下文。 |
| 原始基线/保护面 | 主协调`entry-manifest.json`和`before/`保存1059文件。QA2独立选定DAA272、database5、user21、CA9、Projection8与旧六migration共321文件，均匹配原entry。只声明此选定保护范围。 |
| 共享example | 三份原84项的完整字节前缀保持；当前91项=84+BE009四key+BE010三采用路径。facts仍False/[]/unadopted/空key，逐项英文注释与双语说明已核，未读取实际dotenv。 |

验证期间CODE_INDEX发生外部SMA local_configuration说明和8行索引更新：原冻结SHA `1ce62cba5f6481e06e8c92454c315f751af9ab4b9519442bef388b4a598f09a4`，最终SHA `08cf4e2bdb02953a7806d17c32aa3a8b22d5812143feb2e860467f611488869a`。QA立即报告主协调；其明确接受这一外部非BE009段例外，不覆盖原70入口。QA2按精确差异反向替换SMA段，可逐字重建并验证原1ce SHA，BE009/BE010能力段未变；未回退或代写SMA内容，也不接受SMA功能。主协调的`be009-qa2-scoped-index-exception.json`及双方旧/新完整快照、精确diff保留。该单一文档例外不改变实现候选或A验收口径。

独立读取根AGENTS/README/PLAN双语、backend及app最近README/PLAN、scripts与facts/维护/provider双语说明、contracts README/PLAN、完整spec/tasks/QA1 checklist、verification.toml与canonical workflow；backend/plans/contracts未发现更近AGENTS.md。按同等表面使用project-governance、aiis（BLUEPRINT/CONTRACTS）、backend-arch（RESPONSE_CONTRACT/LAYERS/DATABASE_AND_MIGRATIONS/MODULE_REGISTRATION/AUTH_SECURITY/OPERATIONS_TESTING/DATA_GOVERNANCE）、backend-script-tooling；code-document-indexer仅审文件头和结构索引。未运行初始化或索引改写，不加载无关UI/Worker/Rust/Tauri专项。

## 环境、实际命令与证据

Q=`/private/tmp/arch-be009-r1-a-qa2-fhzw6m9j`。项目行为使用backend既有uv环境，Python3.13.3、uv0.7.8，无sync/install/依赖变更。QA2自行编写guard，在任何项目导入前清除继承配置、注入合成process env、禁真实dotenv和SQLite文件读取，阻断socket连接/监听、SQLite两connect、各DBAPI及SQLAlchemy Engine/Connection/AsyncEngine/AsyncConnection执行入口。18个对已替换函数的guard探针均在guard内拒绝，未发出真实操作。ASGI仅内存transport。

九个正式测试逐字复制到Q/focused，hash同时匹配交付树；`--confcutdir`隔离共享破坏性conftest、关闭pytest cache。所有pycache/cache/basetemp/log在Q；没有运行项目全套pytest或B入口。如下项目命令的完整公共前缀为：

```text
cwd=/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend
UV_CACHE_DIR=/private/tmp/arch-be009-r1-a-qa2-fhzw6m9j/uv-cache
PYTHONPYCACHEPREFIX=/private/tmp/arch-be009-r1-a-qa2-fhzw6m9j/pycache
uv run --offline --frozen --no-sync python /private/tmp/arch-be009-r1-a-qa2-fhzw6m9j/guard.py
```

| 公共前缀后的完整argv/检查 | 真实退出码与结果 |
| --- | --- |
| `Q/run_suite.py focused` | 0；九个完整test_plc_facts文件，**178 passed in28.78s**。未削旧断言。 |
| `Q/run_suite.py independent`，最终扩展 | 0；自建`independent/test_rework.py`，**70 passed in3.19s**。首轮67项exit0/1.01s，追加相邻raw/latest纳秒与单次tick预算后再跑。 |
| `Q/surface.py`，最终版 | 0；preflight、正常composition三路、metadata75/pending4、8条唯一源码接链、七表静态DDL/Index/Model、独立F7、typed OpenAPI逐对象快照/ref闭包、24本地链接/3 JSON、独立9摘要及>28位canonical、targeted compile全部通过。 |
| `Q/guard_and_help.py` | 0；18个guard拒绝探针；在全新进程中裸CLI及--help均exit0，前后settings/database仍未导入。未执行status/plan/apply或任何目标访问。 |
| `python3 -B Q/audit.py`（stdlib文件审计，不运行项目） | 0；69冻结项、CODE_INDEX外部例外、321保护项、公开example完整前缀、9测试副本、QA1全文、UTF-8/逐行空白与`git diff --check -- <70候选路径> <checklist>`核验通过。未跟踪正文由逐行检查覆盖。 |
| QA1已有旧回归与相邻双故障证据复核 | 本轮未重跑：QA1六文件44 passed/9 deselected及4 commit/close双故障HTTP通过。六正式文件逐字等于QA1真实副本，相关事实API/事务退出实现未变；原runner/guard/log SHA匹配QA1记录。当前178项另包含这些表面所需事实用例，未声称重新执行旧44/4。 |

run_suite的精确pytest argv：`-q --tb=short -p no:cacheprovider -o asyncio_mode=auto -o 'markers=no_db: prohibits database access' -c /dev/null --confcutdir=Q/<suite> --basetemp=Q/<suite>-temp -m no_db Q/<suite>`，suite仅focused或independent。这里Q均展开为上方绝对路径；argv原文也保存于各log首行。

QA helper纠错如实保留：surface首轮exit1，初版AST只识别Assign，漏读旧Core root的AnnAssign而触发迁移数量断言；独立查源后仅补QA helper的AnnAssign读取，最终8条接链通过，首失败log保留。入口审计首次因CODE_INDEX真实漂移停止并上报；旧回归曾误与最初entry而非QA1候选比较，改QA helper采用QA1真实副本后确认六文件未变。这些均未改产品或测试，不作为产品failure。shell的Homebrew `/bin/ps: Operation not permitted`提示不影响表中项目退出码。

## F-QA1-001：A范围独立关闭

新CRUD以`coalesce(octet_length(blob),0)>0`构造三列实际原值资格，在LIMIT之前过滤；全NULL/空bytes的OR为确定false，proof的NOT不会因SQL UNKNOWN遗漏全NULL行。Cycle proof同时要求已满120天、三原文零字节、NOT EXISTS任何同`instance_id/cycle_id`的sample receipt。独立selector解释实际SQLAlchemy WHERE/ORDER/LIMIT及相关EXISTS，保留SQL三值逻辑；期望结果直接按人工fixture的应存/应清集合断言，不调用产品predicate生成expected。

| 独立反例/相邻边界 | QA2实际结果 |
| --- | --- |
| 200条三列NULL/b''前缀，后第201条过期原文 | 8种NULL/空bytes组合均只清尾部1行13bytes，保留201份未到期proof；value_bytes精确归0，status不再报过期原值积压。 |
| 已空200前缀+201条有值Cycle，多tick | 四tick分别清200/1/0/0行与2600/13/0/0bytes，不再卡住第201个有值Cycle。 |
| 200条仍被receipt引用的到期Cycle proof，尾部无引用proof | 仅删除尾部1份proof；200份被引用Cycle和200 receipt全留，proof_rows从401到400，floor仍(0,0)。 |
| 相关引用完整键 | 同instance+cycle保留；另一instance同cycle和同instance另一cycle均不误关联，可删除；没有把任一单键当全局引用。 |
| 200条尚有未过期原值proof前缀+空尾proof | 原值全部保留，仅删除空尾proof；计数不伪清零。 |
| 每一blob单独非空、部分字段已清、有限byte预算 | 预算不足不丢整blob；剩余容量可分字段继续，最后原值清完后才允许proof删除；实际blob计数与state逐次相等。2MiB预算下三份800000bytes仅清1600000，再留800000。 |
| Cycle及相邻raw/latest纳秒 | 同wall但expiry ns晚于asOf不清；等于及早于可清；status与候选资格一致。原值未到期不因proof状态被删。 |
| sample proof完整serial前缀 | 任一成员未到期则整个serial和后继不动；剩余行预算不足不部分删；全到期先删serial1两ordinal、floor=(1,2)，下一tick再删serial2、floor=(2,1)。 |
| 有界预算/plan | 0行/0byte或100ms已耗尽时不推进；plan不改内容/counter；真实_execute在替身事务中最多10事务/2000行，保留第2001行。未放宽120天、三自然月或配额。 |

新增非unique `ix_pf_cycle_receipts(instance_id,cycle_id)`与相关NOT EXISTS实际相等键一致，完整VARBINARY合计1024bytes，未用前缀/hash-only。Model与同一0a2迁移同步，无新表/revision。上述仅关闭源码算法反例；真实MySQL索引计划、查询/锁耗时、事务回滚计数及24h SLA仍归B，替身时钟不冒称这些运行证据。

## F-QA1-002：A范围独立关闭

REAL使用`Decimal(v).copy_abs()`保留精确幅值，原范围上界3.4028234663852886e38、非零下界1.401298464324817e-45未改。QA2以Fraction整数/分数独立判据给出预期，不以Decimal上下文运算或产品条件生成expected。48种组合覆盖precision7/28/100、正负上/下恰等、极小内外差、0/-0及普通1；输入先strict_json再typed PointFact，合格仍为原精确数字，非法均422 plc_facts.invalid_request。

QA1三条精确越界（正/负`3.402823466385288600000000000000000000001e38`、`1.401298464324816999999999999999999999999e-45`）及负下界均拒绝；恰等和内部相邻值均接收。canonical往返与原Fraction相等，>28位数字/Unicode/control字节与QA2独立encoder一致。没有重新binary32量化、改原payload原文或套用BE010 business摘要规则。

## AC01–AC12当前A验收审计

| AC | 当前A结论与证据 | 未通过本轮取得的运行证明 |
| --- | --- | --- |
| AC01 | pass：正常composition正好三路匿名、typed输入/200及全部失败schema、严格query与原Map键、机器快照/ref闭包一致；178项与surface。 | 无真实HTTP→七表→读回。 |
| AC02 | pass：F002关闭；原v2唯一点位体、SHA、manifest/reads/context/definitions/归属、固定贪心片、类型/bad/null/0及parser预算拒绝；独立9摘要复算命中。 | BLOB/精确键/9位真实存取及整批真实回滚未证。 |
| AC03 | pass：锁→原批恢复→身份/source/父证明检查→persist/终结拒绝→flush→commit；真实Service替身和ASGI验证完整退出后send、unknown及脱敏。QA1四双故障原证据核对未变。 | 无真实commit/rollback/close/断线/丢响应矩阵。 |
| AC04 | pass：多PLC同DB/多DB/组、完整expected与缺片不假complete、全批拒绝/父token持久SHA及换key子集恢复；178项和源码。 | 跨Session竞争/持久拒绝/公平补传未证。 |
| AC05 | pass：sourceEpoch内逐点seq、bad替good、来源/定义维护CAS、代次切换清值、同源未变定义保留旧值；原源码/正式替身通过。 | 真锁/CAS竞争、来源换代及1005/1001并发未证。 |
| AC06 | pass：门闩内highSerial+1/ordinal，同snapshot H/feed不取raw.id；MAC/filter/epoch/floor/TTL、过滤空页/扫描预算、range H/半开区间、latest binding分页已审并通过相关noDB。 | T1晚commit/rollback/断线与T2/reader真实可见性未证。 |
| AC07 | pass：自然月/月末/闰年/9位、最早成员raw/cycle保守到期与latest单点、120天最小proof不续期/无值、历史回执不复活值；正式用例与独立纳秒相等通过。 | 真DB上海时间、宿主TZ与纳秒持久边界未证。 |
| AC08 | pass：F001关闭；单次维护help/精确目标门槛、行/字节/时间/tick/完整前缀、status/counter和无调度/DDL/业务级联源码已核。 | 真预算/锁/故障重入/3次失败降级/24h SLA未证。 |
| AC09 | pass：同一0a2接f6七表，Model/DDL/Index一致，完整metadata75=71+pending4，唯一1b3后继；0a2/1b3有限profile、显式再核验/CAS/F7规则已审。 | 未执行upgrade/downgrade/反射live F7，独立B只到0a2；1b3联合运行属BE010后续gate。 |
| AC10 | pass：321选定保护项含旧六migration/monitor/CA/Projection，事实兼容固定hash与disabled隔离测试通过；旧44证据复核。 | 无旧CA/Projection/业务真实运行验收，BE010业务实现不由本QA接受。 |
| AC11 | pass：默认关闭/空及越界403、合格但未采用/profile/key不ready503均在session前；disabled重组后事实三路移除而monitor保留；错误脱敏。 | live schema/source/time准入与并发/锁/容量真实裁定pending。 |
| AC12 | pass：正式树导入/副本hash、全部必要A测试、静态preflight/composition/DDL/compile/OpenAPI/JSON/链接/diff、历史保留与并行例外可复核。 | A通过不授Owner终验、provider-ready、部署/DAA或B授权。 |

新候选静态F7独立复算为`sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`。QA1的28ed…指纹只属于旧结构；新增索引有明确diff，不能以旧F7拒绝新候选。后续B须反射核验此新F7，BE010联合材料不得继续拿旧28ed作为当前结构预期。

## 持久证据、资源与最终handoff

全部自有辅助资源仅在Q：9个逐字测试副本、独立70项helper/guard/runner、测试basetemp、uv/pycache/log、静态SQL/语义JSON、审计diff/快照及报告。没有临时源码worktree、HTTP listener、后台服务、数据库/SQLite、Docker实例/卷、真实env/profile读取、依赖安装、Git写入、PLC/DAA操作或外发邮件。QA不执行回收；保留至主协调/Owner及未来B消费后，确认不再承担证据/运行依赖时由主协调处理。QA1/DEV/root/BE010资源不归本QA回收。

| Q内证据 | SHA-256 |
| --- | --- |
| guard.py | `a36fd8ffe9e3e969582bbbf882f0e65116a47956a7862caa83558058b9d47e29` |
| run_suite.py | `91921114240242368bbe4253921618541b2d3edbeb51a2aedb6535acba88b358` |
| independent/test_rework.py | `26545bdaad06e475a30ea1be62fd23118061ee1b078280e3f02763118d5b5d07` |
| surface.py | `d99d4171a5fa45ced71e3f75834376a0da20675ec45de8ec9f79bd8a9f8591ad` |
| audit.py | `4923420258c7228a1798534ad1124034bd1a054d3d1bfea34c3104aef223d0b0` |
| focused.log | `1d0a37607e92286d2506e4686425dd67a2db26b7179a69cd5fce7743f5875d4d` |
| independent-final.log | `88cc03b757a1f5b9ff2c576c738bd62b584cb1cb94dffda4b914dd62d488f644` |
| surface-final.log | `de620426475bcf72b5523e20f1763fe96dc33fb7f3650e0da2f84dca78714698` |
| surface-report.json | `290ef14bb70dde5108a887b7c52444a54ca1de1aa52f4b58f41724b72bdb1681` |
| semantic-F7.json | `1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed` |
| candidate-selects.sql | `c5c24b17405bdfac6b9e7ab6d432bd49e4d60f9907bd1f518ef82c3c65952787` |
| guard-and-help.log | `c2b1113a74ea4ed8a78976478d75dbf8837f4af0dd72fe06c0dbaffc30076e2a` |
| CODE_INDEX.external-parallel.diff | `2c8c6a04732ed7656b4c716b9b24e915a8f4e78bd4134bb1fa602fa698d33570` |

关键输入、命令、失败关闭依据、AC和边界已写入本checklist，不只依赖临时路径。QA2唯一仓库写入为本文件，方式是添加本轮记录并保留QA1原始完整字节；spec/tasks/实现/测试/配置/共享索引均未写入。

| Gate | 最终状态 |
| --- | --- |
| r1 A返工1 QA2 | `qa_passed`，F001/F002在A范围独立关闭；原QA1失败和原反例不覆盖。 |
| Human Owner | 接收本次A独立结论并决定最终接受；**final acceptance pending**，无代授或推断。 |
| B/G-B | 未授权、未运行；真实MySQL8.4.6/七表迁移、事务/并发、DB时间/精度、反射新F7、清理计数/锁预算/SLA均pending，另批具体目标/操作后才可进行。 |
| BE010联合1b3/75 | 其后续独立运行gate，须新F7与epoch/proof不变、显式再核验后事实三路正常；本QA不验收BE010业务实现或授权其迁移。 |
| provider-ready/部署/DAA/阶段C | 均pending；A通过不代表后端完整就绪、已上线、永久业务闭环或DAA验收。 |

---

# QA1原始完整记录（历史，以下字节原样保留）

Task ID: ARCH-BE-009
Revision: r1
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA1 -> Development：修复F-QA1-001/F-QA1-002并重新developer_handoff；随后由新的fresh-context Verification复核。Human Owner接收本独立失败结论；最终验收pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Stage: A source/no-DB only
Verification Iteration: QA1
Verified At: 2026-11-04 Asia/Shanghai

# QA1结论与精确候选

**ARCH-BE-009 r1 A为`qa_failed`。** 原九文件129项与六个旧文件44项no_db回归通过；独立追加六个断言全部失败，确认两项实现缺陷：Cycle清理候选在LIMIT之前没有排除暂不可处理行，导致后续过期原文/可删proof饥饿；REAL数值边界使用会受Decimal上下文精度影响的`abs()`，接受精确越界值。QA没有修复产品、测试或配置，失败已交主协调转Development。

本次由命名Verification身份`/root/be009_r1_a_verification_qa1`在Development正式停止写入后开始；不继承Development对话推理，独立消费批准spec、tasks、当前正式源码、entry/before差异与DEV输出。主协调负责实际fresh调用及串行控制证据；项目`verification.toml`配置为`gpt-6.1-sol`/`max`，配置不冒充本角色独立观测到的运行模型值。profile为`contract_only`，不宣称文件ACL、自动路由或平台强制隔离。

| 固定输入 | 核验结果 |
| --- | --- |
| 正式交付源码 | `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，未提交共享脏树；本次不创建Git对象/工作树。 |
| Human Owner批准 | spec第15节保存2026-11-04精确批准BE009 r1/BE010 r2 A源码；B、数据库、Docker、实际数据迁移和DAA改动未授权。 |
| 当前spec SHA-256 | `26121323384f2b8fd590921f53c477d759b564cf5214078c05834496a4884f48`；批准收据记载的原稿为`157932dfd6432b972ed73c327ba47bffd4b7c43f32c6e68f772c5cbef458eb86`，本轮未改spec。 |
| 正式tasks SHA-256 | `434c58278610002164ddb610cdfb82ff9d6a43c44b0f601cf1b90333d24c45e5`；`developer_handoff`，本轮未改tasks。 |
| DEV独占57文件manifest | `/private/tmp/arch-be009-r1-a-dev/implementation-manifest.json`，SHA `b79bcee3e4b002e993e862f40a5abacf77180f1177b9df5fd4b880fe40b58382`；每文件持久hash见tasks，未以DEV自检替代QA。 |
| 本次冻结70文件 | 主协调`/private/tmp/arch-be009-r1-be010-r2-a-y34l21yd/be009-qa-entry.json`，SHA `4decf60e095ce243a7f71b4d891f237c73ae489b49435703c967797d8d4ed130`；57独占+11共享+spec/tasks，开始及收尾全部hash相符。 |
| 进入前基线 | 同目录`entry-manifest.json`及`before/`，1059公共源码文件。11个共享文件按before差异审查，不把BE010获批段落认作BE009越界。 |
| 保护面 | QA独立选定321个entry文件：DAA272、database5、user21、CA9、Projection8及六旧migration，全部hash未变；没有将协调535文件报告冒称QA独立全量复核。 |
| 共享公开example | 三份example逐字保留原84项的完整字节前缀；当前91项=原84+BE009四key+BE010三采用路径。facts默认False/[]/unadopted/空key。真实dotenv未读取。 |

已完整读取根AGENTS、根README/PLAN双语、backend及app最近README/PLAN、scripts及plc_facts/维护目录README双语、contracts README/PLAN双语与provider README、完整spec/tasks、role TOML和canonical workflow。`backend/`、`plans/`、`contracts/`未发现更近AGENTS.md。按实际表面读取project-governance、aiis及BLUEPRINT/CONTRACTS、backend-arch及RESPONSE_CONTRACT/LAYERS/DATABASE_AND_MIGRATIONS/MODULE_REGISTRATION/AUTH_SECURITY/OPERATIONS_TESTING/DATA_GOVERNANCE、backend-script-tooling、code-document-indexer；未运行初始化、安装、修复或全仓索引生成。DAA公开Rust的SamplePayload/CycleManifest/Point/Address仅作原合同字段来源对照，未运行或修改DAA。

## 环境与实际命令

使用backend既有项目环境：Python3.13.3、uv0.7.8；无依赖安装/sync。QA证据归属`/private/tmp/arch-be009-r1-a-qa1-6almbxjk/`。测试副本只有九个任务测试及六个旧回归文件，原字节hash与正式源相同；产品实现始终从正式交付树导入。`--confcutdir`隔离共享破坏性conftest，pytest cache关闭，basetemp/pycache/uv cache/log路径都在自有临时目录。

独立审阅DEV的check.py后自建`guard.py`，在项目import前清除继承配置、注入合成process env、禁真实dotenv读取及真实.env/SQLite文件访问；阻断socket connect/connect_ex/bind/listen/create_connection、sqlite3两入口、SQLAlchemy Engine/Connection/AsyncEngine连接执行、pymysql/aiomysql/psycopg2/asyncpg连接。ASGITransport只在进程内运行。guard未用于放宽项目checker。

下文`Q`精确为`/private/tmp/arch-be009-r1-a-qa1-6almbxjk`；每个项目命令实际在`/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend`执行，完整公共前缀为：

```text
UV_CACHE_DIR=/private/tmp/arch-be009-r1-a-qa1-6almbxjk/uv-cache
PYTHONPYCACHEPREFIX=/private/tmp/arch-be009-r1-a-qa1-6almbxjk/pycache
uv run --offline --frozen --no-sync python /private/tmp/arch-be009-r1-a-qa1-6almbxjk/guard.py
```

| 前缀后的精确argv/检查 | 退出码与真实结果 |
| --- | --- |
| `Q/run_suite.py tests` | 0；`focused.log`：129 passed in30.01s。九个完整test_plc_facts文件，包含严格parser/值、片、真实Service替身、依赖退出、回执/父token、query、迁移静态及关闭模块。 |
| `Q/run_suite.py regressions` | 0；`regressions.log`：44 passed/9 deselected in56.51s。明确文件test_module_registry、test_module_contract、test_response_contract、test_projection_runtime、test_control_agent_authorization、test_role_api_authorization；DB用例未选。 |
| `Q/run_suite.py independent`，最终六断言（数值先经strict_json） | 1；`adversarial-final-parsed6.log`：6 failed in0.33s；三种清理候选饥饿+正/负REAL上界与下界，详见失败章节。未把失败改为预期通过。此前`adversarial-final6.log`为等价Decimal直接构造版，6 failed in0.30s。 |
| `Q/run_adjacent.py` | 0；`adjacent-http-final.log`：4 passed in0.49s。真实ingest commit的ValueError/RuntimeError × dependency.close的RuntimeError/OperationalError四组合，完整ASGI响应均503/commit_outcome_unknown/unknown、newFactsCommitted=null、retryable=true、retirementAllowed=false，脱敏且inflight归零。 |
| `Q/surface.py`，最终版 | 0；`surface-final.log`/`surface-report.json`：整仓check_source、正常composition、metadata75/pending4、七表MySQL CreateTable/CreateIndex静态编译、唯一迁移链AST、targeted compileall、typed OpenAPI与发布快照逐对象一致、24本地链接及3 JSON解析通过；9个摘要由QA独立encoder复算命中。 |
| stdlib entry/diff/公开example审计 | 0；70冻结文件无漂移；1059进入前文件有75个当前差异（联合DEV+协调改动，非QA写入计数）；321选定保护文件无变化；三example完整entry字节前缀保留。 |
| `git diff --check --`本候选路径及checklist；未跟踪文件另作UTF-8/逐行空白检查 | 0；未以Git对untracked文件的空输出冒充正文检查。 |

`run_suite.py`统一pytest argv为`-q --tb=short -p no:cacheprovider -o asyncio_mode=auto -o 'markers=no_db: prohibits database access' -c /dev/null --confcutdir=Q/<suite> --basetemp=Q/<suite>-temp -m no_db Q/<suite>`。两个通过suite没有削弱旧断言或执行DB测试；本轮没有全套pytest或旧BE010 220/437/88重复验证。

QA辅助脚本纠错历史保留：首轮清理probe把首次SQL编译446ms导致的零进展作为首tick固定200行断言，随后修改QA自己的断言检查后续累计进展；产品仍未改变。后续首tick7ms清200行，后续3/3/4ms均零进展，稳定定位LIMIT饥饿，不据这些替身耗时宣称真实DB预算/SLA通过。surface首轮假设vectors.expected包含projectionDigest而KeyError，改QA helper使用spec已固定`b6b7…`预期后通过；未改vectors或被测编码器。补充相邻双故障时一次传`run_suite.py independent -k adjacent`，runner不消费额外argv，实际6 failed/4 passed；其后使用单文件run_adjacent.py，四项独立通过，未把该次多选当作单文件通过。初版与终版日志均保留。shell启动有Homebrew `/bin/ps: Operation not permitted`提示；项目命令实际退出码如表。

## AC01–AC12独立审阅结果

本表是本次失败候选的A核验记录，不把局部通过写成整项B关闭；发现两项实质failure后不为凑齐通过反复扩大测试。返工后的新fresh QA仍须消费完整规格和候选。

| AC | A源码/无DB结果与证据 | B及尚未证明的边界 |
| --- | --- | --- |
| AC01 | 三路正常注册、typed请求/三读/200及403/409/410/413/415/422/429/503/500失败闭包、schema refs、匿名无伪actor及原数据键已审；129suite和源码快照一致。 | 无真实API→七表→读回。 |
| AC02 | **failed：F-QA1-002**。其余原文SHA、v2字段/manifest/reads/context/点组DB关联、bad/null/0、UTF8/重复key/深度与固定片已有noDB证据；QA独立9摘要命中。 | 非法原材料真实回滚、BLOB/精确二进制键/纳秒存取未证。 |
| AC03 | 已审锁→原批恢复→片/cycle/source校验→可靠拒绝或persist→flush→commit；真实Service替身验证create/replay/conflict/commit unknown，ASGI验证commit→完整close→send及close失败unknown。追加四项ASGI同时commit异常+二次close异常仍保留unknown/不授retirement。DEBUG错误未回显秘密。 | 无真实commit/rollback/close/断线故障矩阵；不能由替身断言持久可靠。 |
| AC04 | 固定贪心片、完整expected集合、两个PLC同DB/多DB组/缺片fixture及拒绝父token换key恢复/子集规则已审并有noDB测试。partial不称sample/cycle complete。 | 混合批真实全回滚、跨Session父proof竞争及公平进展未证。 |
| AC05 | 逐点seq/sourceEpoch比较、bad替换good、维护CAS、generation切换清值与同generation定义未变保留值已审；noDB采用/顺序测试通过。 | 1005/1001、同点竞争、定义/移组/禁用/CAS完整真实矩阵均pending；本轮不宣称穷尽关闭。 |
| AC06 | 锁内分配serial/ordinal与同snapshot H/feed算法已审；H不来自raw.id。MAC/filter/epoch/floor/TTL、显式tail、过滤空页、range H/半开point投影与original资格、latest binding分页有源码/noDB证据。 | 独立Session T1先分rawID后晚commit、T2/reader及rollback/断线均未运行。 |
| AC07 | 三自然月/闰年/月末、9位时间与offset、到期相等、原payload最早成员及latest独立、120天proof不续、historical不重建值已审。 | 真MySQL时间/宿主TZ/亚微秒和到期读窗未证；物理清理另见F001。 |
| AC08 | **failed：F-QA1-001**。裸CLI/--help在settings/DB前退出、显式plan/apply、仅七表/无Worker或DDL、counter增减规则已审；清理无法保证对后续合格行前进。 | 真锁/预算/计数/中断恢复/负载、3次失败和24h SLA均未验证。 |
| AC09 | 七表迁移静态DDL与Model逐表/索引一致，0a2接f6、BE010另接1b3单head；75metadata=71+明确pending4，旧六migration hash不变；有限profile/F7/CAS再核验源码已审。 | 无upgrade/downgrade/反射live F7或真实71/75表证明；B独立只到0a2，1b3联合gate另属BE010。 |
| AC10 | 旧monitor realtime、Projection输入及旧六migration固定SHA通过；旧认证/CA/Projection/response/registry六文件44noDB通过。新事实不调用旧业务writer/DB/设备。 | BE010获批业务改动独立验收；没有旧CA/Projection真实运行兼容证明。 |
| AC11 | default-off/空及越界403、合格但unadopted/任意profile503在session前、模块disabled三路移除404边界有ASGI/装配证据；guard实际拦真实连接。 | 当前profile/key合格后的schema/source/time live验证及并发/锁/容量真实裁定pending。 |
| AC12 | 正式树直接导入、70hash一致、compile/preflight/OpenAPI/JSON/链接/差异检查真实执行，独立失败无静默修复；共享归属及历史suite未改判。 | A整体验证失败，B和provider-ready仍未成立，必须返工再fresh QA。 |

静态F7独立复现为`sha256:28edcba4298a164389965c6f7d05b29e8e6494a1ace48d141d83c5edbd1d8e2e`。七表结构SQL在QA临时static-ddl.sql；没有运行任何Alembic命令或连接反射。四张pending表为equipment_integration_receipts、performance_integration_receipts、monitor_integration_receipts、performance_integration_observation_events。

QA encoder独立从spec第5.3节原JSON及原材料构造规范字节，没有调用被测canonical生成expected；复算原source/manifest/context、content、cycle、request、definition、definition-set、query-projection共9摘要，分别与spec及已有vectors预期比对。projectionDigest使用spec精确`sha256:b6b7bb6c66ce92107e76841cfdb5637d8682314f08094e5d77b6416794936de0`。相邻检查确认canonical对`1.0000000000000000000000000000000000001`及Unicode/control字节保持精确，F002定位在bounds的abs而非规范编码普遍丢精度。

## F-QA1-001：Cycle候选LIMIT造成清理饥饿

严重性：高；关联R10/AC08。位置为`backend/app/plc_facts/crud/sync_maintenance.py:86`、`:92`与`backend/app/plc_facts/services/sync_maintenance.py:114`、`:119`、`:151`、`:155`。

实际原文清理查询为`SELECT … FROM plc_facts_cycles WHERE expires_at <= :now ORDER BY expires_at LIMIT 200`，未在LIMIT前排除manifest/context/transport都已NULL的Cycle。Service读取这200行后对payload_size==0仅continue；这些行仍需保留120天proof，因此下tick仍取得相同前缀。结果是后续过期原文可持续遗留，即使每分钟tick、负载很低且没有DB异常。读时expiry guard仍在，本缺陷不证明过期值可由API读到；它破坏物理有限清理和配额恢复。

独立probe直接调用真实CRUD生成的SELECT与真实`cleanup_batch`，只以有限Select执行替身解释其实际WHERE/ORDER/LIMIT；没有数据库或SQL迁移执行。准备201条Cycle：每条三份原文各1字节，最早已过期26小时，proof尚余20天，state.value_bytes=603。首tick结果200行/600bytes；其后三次均0行/0bytes，cycleId=`200`仍有3bytes，state.value_bytes=3。另从初始200条已NULL的前缀出发，后面1条可清3bytes，实际仍返回0行，而期望是清1行并value_bytes归0。

相同候选顺序问题也存在于最小cycle proof：`:92`先取到期前200条，再在`:152–155`跳过含原文或仍有receipt的行。独立准备200条仍被有效receipt引用的到期cycle proof和第201条已无引用/无原文的合格proof，真实service返回0行，201条全部保留；第201条应可删除。不能通过删仍有效引用/原值或放宽完整serial前缀规则解决饥饿。

邻近审阅：status的`oldest_expired`对Cycle显式过滤非NULL原文，而清理候选没有，资格不一致；`blob_bytes`仍准确计入遗留原文，所以该失败持续占用逻辑预算。当前proof_rows包含保留Cycle本身；修复必须同时核对候选资格、状态和counter，不能通过清零计数伪造已清理。真实SQL时间、计数并发、SLA仍归B，以上只证明源码选择算法失败。

返工验收：保留有界行/字节/时间预算及安全proof前缀；201+混合空/非空、被引用/可删除、部分清空原文场景中后续合格行必须前进，状态/字节/proof计数与实际一致；新增针对性回归，不削既有约束。实现由Development负责，QA未作修改。

## F-QA1-002：REAL严格范围被Decimal abs舍入放宽

严重性：中；关联R04/AC02。位置为`backend/app/plc_facts/source.py:78`。

`abs(Decimal)`会按当前Decimal context（默认precision28）舍入后再比较。下列JSON number经过严格parser/typed PointFact后以good REAL交给真实`value_check`，实际均未抛FactsError；按规格精确上下界应422 invalid_request：

```text
 3.402823466385288600000000000000000000001e38
-3.402823466385288600000000000000000000001e38
 1.401298464324816999999999999999999999999e-45
```

QA用独立`localcontext(prec=100)`和不依赖context舍入的`Decimal.copy_abs()`先证明三者严格越界，再对`value_check(validate(PointFact,fact))`断言抛FactsError，三项均`DID NOT RAISE`。这些小数位在parser允许的256位内，并非被输入预算排除的数据。示例复算核心为：

```python
magnitude = Decimal(text).copy_abs()
assert magnitude > Decimal('3.4028234663852886e38') or magnitude < Decimal('1.401298464324817e-45')
# 实际被测：value_check(validate(PointFact, {...合格definition、quality:'good', reason:None, value:Decimal(text)}))
# 期望FactsError(invalid_request)，实际三者全部正常返回。
```

相邻canonical未发现同类normalize/quantize/float重规范，独立高精度字节比对通过；不能因此忽略本入口校验放宽。返工需在正负上下界、恰等于边界/0、内外极小差值及不同Decimal precision下验证精确数值政策，不重新binary32量化原payload。QA没有给产品打补丁。

## 证据、写入审计与资源

本次QA仅创建本checklist.md。所有probe、复制测试、日志/缓存位于自有Q目录；无HTTP listener、Docker/DB/SQLite/PLC、临时源码工作树、volume或后台服务。未读取真实.env/配置/profile，未执行安装、Alembic命令、Git写入、真实网络或外发邮件。

| QA证据（均在Q内） | SHA-256 |
| --- | --- |
| guard.py | `7db1fd033b1e81cbb5ceeb3eccf7adff02b83a6d2098b7992da7f395d5406356` |
| run_suite.py | `4f807ea0eda464ddea8f1e8a9fa3e412bc9b55aaca6d8140932167f0b3016481` |
| surface.py | `a0a3ccb306caae81deda9e39b472c2a32e98464794bf39be8824e8ba3103e6ec` |
| independent/test_adversarial.py | `0fe77d67015bdc57b9099b7bb5dd18489ffdc8d4a152d6e0f7e3419face0984a` |
| independent/test_adjacent_http.py | `090c88e4cd3be05e5800aab2f507e413f9ff96296b205a5303ed10b35c770376` |
| run_adjacent.py | `60de5575c9ec2476905b4f25bece23d76c3425e10cae31360fa50d7810aa0b9d` |
| focused.log | `ee304445b7fdb976a78d63d9d27fd1a6c41cfb8982eaec3c6d42a57bbcef77e3` |
| regressions.log | `6abdf0a736b4bed43d1f3543bd747113411e4767221a42d8b7ea400b62a33033` |
| adversarial-final6.log | `ac8ca0ba12fc1dfe4b100414cee78f86c23906d820c4544e7211abe5cff8833f` |
| adversarial-final-parsed6.log | `ae9dca62a00dabaa0101838a55ee72ab4605a64e409252fe1cd492ca5f1c94e8` |
| adjacent-http-final.log | `d659bd6603166793c084fa55538154b1e66dc1fb0a6b6de0f8bdd839943321ed` |
| surface-final.log | `015d5484b218e3538d777ba05925329dde372cc678bae2ba177559c604b6e07e` |
| surface-report.json | `61d41845c852d6954f95bf010ccd329b28cfed9ef14791e9957e4b589f094afd` |

entry-audit.json记录70候选及测试复制hash，entry-diff-audit.json记录1059基线比较和公开example前缀，protected-audit.json记录321保护文件。详细输出保留供Development/新fresh QA消费；关键输入hash、命令结果、失败条件与反例已经在本checklist持久化，不只依赖临时路径。不得由QA清理这些资源；待返工/后续QA/Owner已消费且无证据依赖时由主协调确认归属后回收。DEV及主协调/PM/BE010目录不归本QA回收。

## 后续gate与Human Owner验收

| Gate | 当前事实/下一步 |
| --- | --- |
| A QA1 | `qa_failed`，F-QA1-001/F-QA1-002未关闭；准确失败经主协调交Development。 |
| 返工 | 同r1已批准范围内Development修复并记录tasks真实差异/回归/新SHA，重新developer_handoff；不得覆盖本QA1历史。 |
| 新fresh Verification | 消费新冻结候选、完整bundle及QA1反例，复核修复和完整必要A范围；不能用本角色继续验证自己的实现。 |
| B / G-B | 未授权、未运行。实际MySQL8.4.6迁移/纳秒/DB时间/锁与并发/故障/反射F7/cleanup计数和SLA均pending；B入口源码/替身不是provider-ready。 |
| BE010联合1b3 | 独立task/gate；本次不接受其业务实现，也不授权其迁移；七表F7、epoch和历史proof不变仍须未来联合运行证据。 |
| Human Owner最终验收 | **pending，无最终接受记录。** QA只提供独立失败结论；不表示全部业务永久保存、上线、DAA上传或阶段C验收。 |

本候选尚不能进入provider-ready或完整后端验收。既有路径保留，当前事实功能默认关闭；发布、部署、数据库/真实配置/设备操作及资源删除仍按各自具体授权处理。
