Task ID: ARCH-BE-010
Revision: r2
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r2 B fresh independent isolated MySQL 8.4.6; candidate 2532d842
A Verdict: qa_passed (prior QA2 retained; B affected five whole files 161 passed)
B Verdict: qa_passed (approved disposable-target technical verification only)
Resource Cleanup: complete (root exact-ID cleanup; independent read-only absence verified)
Human Owner Final Acceptance: pending
Handoff: independent B technical and resource result -> Human Owner; production G-T/adoption, DAA and Human Owner final acceptance pending
Updated: 2026-11-04

# r2 B QA1：独立隔离技术验证通过；专用资源关闭已核

**本次批准的隔离 B 技术范围为 qa_passed，无开放的新产品 finding。** 实际 MySQL 8.4.6、typed ASGI→async Service/CRUD、时间采用合成夹具、并发/故障、真实断线和同一事实清理后的永久业务恢复均通过；受 B 影响的五整文件另独立运行 **161 passed**。本轮不是 Dev 自检复述，未复用 Dev 数据库、连接配置、秘密或目标。root已按精确身份清理两轮专用容器/卷/网络与私有操作凭据；本verification独立只读观察2容器/2卷/2网络及27文件均不存在（含自有13份），本轮资源关闭已完成。Human Owner 最终验收、生产目标 G-T/采用、真实历史整改、DAA/SMA/PLC、部署和发布没有获本 QA 结论代行。

下方原 A QA2 checklist 作为完整字节后缀保留，SHA256 `2e42a63552d4d377a79b397f2f74974f379784b28cdf0742cb580dedda1b5af1`，包含全部 QA1/r1 原 verdict、失败与 gate。旧 A 的335/87是该轮独立证据，不与本轮161相加；旧“B尚未批准/未执行”表示当时时点。

## 批准、独立性与固定输入

Human Owner 对具体 B 操作提案逐字批准：

> 批准 B 操作提案，按 STD 完成 ARCH-BE-009 r1 和 ARCH-BE-010 r2 的两轮隔离 MySQL 8.4.6 验证及专用资源清理。现有数据库、真实历史数据和 DAA 不动。

提案 `/private/tmp/arch-be009-r1-be010-r2-a-y34l21yd/B-operation-proposal.md`，SHA `9f2ca5f0e2cbfb0b59caed770eb2507b6f9f0f8c4392f78b0b52a4f5d540f787`。这份精确批准授权可丢弃目标上的合成转换/采用/故障/清理，不扩及现有数据库、真实历史、DAA或生产采用。完整 [spec](spec.md) r2.3.4 第5项明确允许 B 用可丢弃目标合成旧行完成真实采用夹具；生产仍受其目标独立 G-T 约束。

- 实际命名 verification 的新 fresh context，未继承 Development 对话推理；完整读根/最近 AGENTS、README/PLAN pairs、canonical workflow、verification.toml、本 bundle 三文件、相邻 BE009 schema 合同、实现/差异及公开测试材料。使用 project-governance、aiis/BLUEPRINT/CONTRACTS、backend-arch 及其六项相关 refs、backend-script-tooling、code-document-indexer，仅验证。contract_only、角色配置和串行 handoff 不代表平台 ACL 或强制路由。
- 正式交付 HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`；共同候选 `/private/tmp/arch-be009-r1-be010-r2-b-my8s9bnu/joint-B-candidate.json` SHA `2532d8423c73f0e9c0a7ac42d616014b2ca09419588cd07a0218bd4ce080cafb`。独立逐 hash 比对157实施+2spec，运行结束仍匹配正式树及自有副本。
- 本任务 spec SHA `955877e96b4695b0c00aa81ef6e862dd6a642e82157edd05d5aeef8c175add5f`；完整 Dev B tasks SHA `d8daa5b61f4c919f67dfeeca4dd8520deb87d05bd6e084a5ccad3dc36b945224`。两文件未改。Dev100源 manifest SHA `b7246f62cd4b8e43648c40d07c6e89c84ddc36d45a6cad4f9cb415cdcfcb5387`，100项逐一匹配。
- 自有证据根 `Q=/private/tmp/arch-be010-r2-b-qa`，独立冻结870个公开输入，不含真实 dotenv/运行数据/环境；`input-manifest.json` SHA `6fc8e909e55d52b5101caf9051da4a4a149d371458517fce8d3056090b88e89e`，870副本零漂移。QA-only `source/backend/profile.json` 为显式 BE010-r2-B/75/1b3 夹具，另入每次 runtime 源 manifest，不是修改正式 profile。
- 联合 B13 delta 的 A 来源由原 A QA2 逐 hash 固定，root 保存的 `B-implementation.diff` SHA `114b8a9d4f745dd14f570eefbc4cfc01813a0778acf5393a5036a00806e23b27`；独立复核 provenance13项。本任务五产品+一 test 的独立 `B-vs-A.diff` SHA `3327272278467088d07ce1885fcda39c05943f8e4c61de2b6ff0fb744a2bff20`。六旧迁移与 A 逐字相同，三个 example env 与 A 字节相同，原91项/旧前缀不删。
- B运行期间正式870输入仅根/ backend 四份 PLAN 的 BE009/BE010 状态行被 root 机械更新；逐行差异与双快照归 `concurrent-index.diff`/`final-file-audit-report.json`，无产品、spec、tasks漂移。本 QA 仓库只写本 checklist，不修产品、正式测试、配置、spec/tasks/六索引，不 Git 写、不装依赖。

## 环境、guard 与串行资源身份

项目 `.venv` 的 CPython3.13.3；FastAPI0.135.1、Starlette0.52.1、Pydantic2.12.5、SQLAlchemy2.0.48、pytest9.0.2、httpx0.28.1、pymysql1.1.2、aiomysql0.3.2。项目行为只以 uv `--offline --frozen --no-sync` 复用正式环境，pycache/uv-cache/log/pytest窗口全归 Q；辅助文件审计使用系统 python3，无安装。MySQL8.4.6，server UUID `704cc55a-d850-11f1-a54d-7e8f718f6773`，默认session +08:00、REPEATABLE READ。

本轮使用的唯一 QA容器 `arch-be009-be010-proof-qa-mysql`，ID `4dc2c195c5d800c792684c97a61f66a4ad7bef12cc35b343d6b47c3eed906bf2`；卷 `arch-be009-be010-proof-qa-data`；网络 `arch-be009-be010-proof-qa-net`，ID `f3ae03e4c91a3fee11bce68011867d738fdde437623003eb169483a7678d2dc5`。本QA只连 `127.0.0.1:33380`、非root `be009_be010_qa` 的 `arch_be010_r2_qa_joint`/`arch_be010_r2_qa_time`，time独占，joint按明确无事务交接串行使用。facts/schema归独立QA009，未另建第三轮，也未连接Dev33379或读/复制Dev connection.json。私有凭据只由QA009的0600文件提供，不打印内容。

导入任何产品前安装 sitecustomize guard：SQLAlchemy/DBAPI/socket 只允许当前精确QA schema/endpoint/nonroot；拒绝root/primary、SQLite（含memory）、其他网络、bind/listen/sendto、真实dotenv。ordinary primary=`never_connect_primary`，root=`never_connect_root`；禁用默认dotenv。A的独立guard拒绝全部DB/网络/listener，只允测试自有public.env/synthetic.env。全部运行 **guard事件0**。没有默认破坏性 pytest、全量create_all、真实.env、PLC、Compose、API TCP listener/lifespan或生产配置操作。

QA009先移交两库 live0a2/71，joint含其原真实1批/1sample/1cycle/latest、ACK、binding、epoch和证明，非Dev复制。Q01–Q03升joint为1b3/75后明确无连接暂交QA009；其B50真实schema-only plan/apply与原POST/latest/history复验后明确归还。最后Q28/Q30冻结68非facts表335行与154永久身份后再次无连接交QA009，仅对同一原fact/proof合成到期+真实CLI cleanup，B70后明确归还；Q31–Q33已结束且不再连库。time始终仅本QA使用。

## 真实执行与验收矩阵

成功响应逐次核status、content-type、完整typed JSON/回执字段、两个独立摘要、source/committed时间及DB副作用；错误核完整模块错误壳和副作用。八份请求直接解析已批spec；独立规范JSON、固定时区和struct/Decimal IEEE754判据不以产品DTO回显作为唯一oracle。公开Dev场景骨架经独立审阅复用，QA另写oracle/全列读回/矩阵并在新QA目标运行；故障注入、原生SQL错误和真正KILL明确区分。

| 标准 | 本轮独立证据与已通过范围 |
| --- | --- |
| R2-AC01；r1 AC01–03 | Q15八类正常typed ASGI→实际async Service/CRUD→MySQL全列读回，温控十值/曲线33指标/生产十三观测/三过程父均核；首写、同投递、同业务不同身份、冲突及独立request/business摘要。A161整文件保留number/integer/闭合provider/规范数字和拒绝合同。 |
| R2-AC02；AC07 | Q13真实UUID/未知或mixed凭据拒绝；Q22三owner×7种正常应用重组：disabled、空device、空producer、unadopted空/非空文件、unknown profile、missing adoption，共21配置，403/503完整JSON；每次全75表结构/全行前后相等。未以未知负例目标宣称已采用。 |
| R2-AC03；AC08 | Q06–Q13合成旧13表41列，真实旧8POST/8GET、actor receipts/水位/人工pair及0/legacy Projection；按已证UTC/上海来源独立转换一次。原64表结构/ID/unique/FK/原值/精度/DATE/旧fingerprint和JSON result保持；不改秒列精度。宿主UTC/上海、session+08/−07、16旧GET比较一致；Q20 UTC17:30/+05:30跨午夜仅转一次，新/旧JWT wire及DATE核对。反射17表57列/新4表16列无UTC默认。 |
| R2-AC03 真实只读工具 | Q16真实CLI对equipment/performance/monitor已知阶段及unknown负例，各inspect/plan/verify，共18进程均exit0；12+24+5固定列与每阶段全64表副作用核对。输出始终candidate，不自动成为adopted凭据。后加的一条unknown legacy drive仍在time负例库，当前time不合格采用；原已知阶段报告只证其当时时点。 |
| R2-AC04；AC04–05 | Q15/Q17/Q22温控/曲线不可变；drive/参数/3过程补NULL和全68行原子冲突；生产create/update/exit/unknown/零活跃水位/前卷/重激活/历史先于stale/同刻冲突/结束父晚到子；父missing/coil/equipment/无可靠新事件拒绝。人工JWT重量0两种实际提交顺序及manual→reported→observed pair优先、总秒数准确。 |
| R2-AC04 较小目标锁序 | Q15实际life A=id3、B=id4，B活跃后重新切回较小A，目标重用与前卷退出已读回；实际owner CRUD一次current-read包含活跃和目标，`ORDER BY performance_main.id FOR UPDATE`，无分两段先锁大ID再取小ID。原receipt affectedRecordIds=[4,3]是语义结果顺序，不冒称SQL锁顺序；此查询未单独保存liveSQL trace，源/真实分支与响应归lower-id-lock-review.json。 |
| B FLOAT修复；AC02 | Q15两owner各6向量×首写/重放/同业务/异值=48请求：0.1、−0.1、0.123456789、123456.789、最小正binary32 subnormal、最大正binary32；物理CAST AS DOUBLE精确读和独立binary32摘要/全列核对，捕获实际equipment/monitor CAST SQL。Numeric域、容差、摘要profile不变，不宣称所有正负极值排列或全仓浮点治理。 |
| B Performance修复 | 新主行4个SQL null()默认观测列的flush后expired实际MySQL路径通过；显式await refresh(with_for_update)后字段读取无MissingGreenlet。Q15八路、生命周期/过程及全列读回和161源码回归覆盖，未以fake返回值替代。 |
| R2-AC05；AC06 | Q15八类真实独立Session首次同身份竞争，异身份同业务；Q17同身份异内容/异身份异内容/首水位竞争；真实RR旧快照后新会话提交，current-read恢复原receipt。原生具名1062一次→恢复，3次耗尽503；未知user unique1062→500不误重试；session真实1秒锁超时503后原身份恢复。 |
| R2-AC05 事务故障 | Q24三owner×6事务/退出故障=18，含flush/commit前/commit后/close/commit+close/rollback；另原生ASGI send丢ACK。完整68表全行（含事件/水位）在未提交故障后不变，已提交原身份恢复，无假成功。人为注入不是物理断线。 |
| R2-AC05 真实断线 | Q25三owner×commit前/driver确认commit后=6次真实own-connection KILL；核当前schema/current_user/connection ID，仅同用户同target自建请求连接。commit前原生驱动断线503 commit_unknown且68行无部分提交；已确认commit后kill可可靠200，重放稳定duplicate。未强迫已确认commit场景503或新增SQL。Q18原六例同样保留，未与Q25相加虚构覆盖。 |
| R2-AC06；AC10 | Q01–Q12真实0a2/71→1b3/75，pending4分阶段不存在/仅新4；空库及带旧64合成行升级守恒。Q20实际Model/DDL列、nullable、类型精度、unique/CHECK命名/FK/binary collation核对。Q10空新4可downgrade再升；Q29新表非空真实exit1拒绝，Q30全68与facts7不变、仍1b3。无create_all掩盖阶段。 |
| R2-AC07；AC09 | Q28冻结154身份（3receipt表全部身份集合）及8资源全业务/source/mapping/父；每个已接受新业务ref确实指QA009原sample/point_x/generation/config，私有sidecar补part/contentDigest/sourceSHA关联，不扩公开ref协议。QA009对同一fact/proof真实清理后，Q31原154请求全部稳定ACK及完整父子恢复；Q32所有永久摘要/result/来源/映射/业务值均相同，raw/proof已空且不复活。 |
| R2-AC08 旧通道/事务 | Q12旧8原actor请求稳定重放、全8GET与实际Projection前后相同；Q20跨午夜旧JWT及Q31清理后同一旧JWT ACK/完整GET一致。Q26八个真实sync Projection Services，aware+05:30→上海一次/原DATE及秒或毫秒精度；host同Session预置业务/cursor/audit，无Service内部commit；caller rollback全68行不变，caller一次commit三者同时持久化。未冒称完整daemon、真实PLC或生产Projection运行。 |
| R2-AC08/AC11/AC12 | 正常provider/模块准入/旧保护A161通过；原A QA2完整335+87和边界/安全证据保留。本轮静态preflight、app/common compile、唯一迁移链及metadata75通过。runtime setup_logger的20个JSON日志共1840行全部可解析；206 committed/137 rejected仅受控字段、无exception正文；所查日志无完整业务body/token/DSN/SQL。早期default Loguru输出与QA自己的原始请求报告不冒充该运行日志证明。 |

## 同一事实保留窗口联合结果

QA009的原fixture为1batch/1sample/1cycle/1latest，point_x值0、sourceSeq11；其原ACK/replay/latest/history和epoch来自独立QA目标。Q28/Q30冻结本任务全68非facts表 **335行/154永久投递/8资源**，Q31 replay和Q32最终三份快照逐字同SHA：

`dd4cea6bbb69ccb2320d57d566ee1a404a7c8e9376d8ce1199fb1231b9b73774`

154个所有原payload/ACK冻结件SHA `ee61945f5f45ffc716836218e84d4125877916faf0a82dc0b8a0d13698688b61`。全行snapshot对FLOAT显式CAST DOUBLE并保存binary64精确表示；不是COUNT替代值守恒。Q31 additionally恢复旧JWT原投递和完整旧GET；清理后未新增断线/跨日/业务fixture，prepare复用既存qa02用户，未偷偷插新用户污染守恒样本。

联合阶段由QA009独立执行而非本QA代做：B50 schema-only真实计划无变化，apply只更新schema_profile/verified_schema_revision/adoption_evidence/last_db_time/updated_at，原epoch/adoption/source binding/F7/6表全行/高水位不变，原POST稳定receipt/latest0/history同digest。`joint-revalidate-proof.json` SHA `d28e2332ea1f38e0255839096e3301eec85a85bc4496bda0f7e021f976ce70e7`。

B70对同一原fact/proof明确合成到期，不改系统时钟；owner CLI plan=5rows/4275bytes/2proof，apply=6rows/4275bytes/3proof/2tx，真实exit0/13.114s。raw/latest/cycle/sample/batch全0，valueBytes/proofRows均0，high1与原epoch/adoptionId/source binding保持、floor(1,1)；原tail等floor仍200空，合法unconsumed(0,0)真实410/requiresResync。68非facts表/335行前后相等，再由本QA Q31/Q32独立确认。`joint-cleanup-proof.json` SHA `60beb25f207d4a4f0211f97cb60a61123edc6211cf29fe0c870019da652d9088`。未在清理后重放facts POST制造原事实假复活，业务/最小ACK无TTL。生产聚合可演进，不声称其每个旧值有版本历史；未完成outbox不在本业务清理范围。

## 精确命令与真实退出

令`Q=/private/tmp/arch-be010-r2-b-qa`，cwd均`$Q/source/backend`。下表每行实际由`python3 $Q/run.py <tag> arch_be010_r2_qa_<joint|time> <外层参数>`启动；项目内真实argv前缀统一`uv run --offline --frozen --no-sync`，下表列出该前缀后的完整argv（`$Q`按上述绝对路径展开）。python行的外层参数是`--script <basename> [mode]`，alembic行原样。每行`<tag>-command.json`有实际绝对argv/cwd/target/exit/wall、runtime manifest与guard hash，原`.log`保留；后期runner新增harness hash，不追称早期每次已保存全部helper版本。

| tag | schema后缀 | 实际argv后缀 | exit / wall |
| --- | --- | --- | --- |
| Q01-joint-71 | joint | `python '$Q/schema_stage.py' before` | 0 / 2.249s |
| Q02-joint-upgrade-1b3 | joint | `alembic upgrade 1b3d5f7a9c20` | 0 / 7.777s |
| Q03-joint-75 | joint | `python '$Q/schema_stage.py' after` | 0 / 2.516s |
| Q04-time-71 | time | `python '$Q/schema_stage.py' before` | 0 / 1.887s |
| Q05-time-empty-to-f6 | time | `alembic downgrade f6a8c0e2b4d6` | 0 / 6.694s |
| Q06-time-seed-old | time | `python '$Q/time_matrix.py' seed` | 0 / 19.319s |
| Q07-time-old-to-0a2 | time | `alembic upgrade 0a2c4e6f8b10` | 0 / 6.648s |
| Q08-time-64-at-0a2 | time | `python '$Q/time_compare.py' 0a2` | 0 / 2.604s |
| Q09-time-old-to-1b3 | time | `alembic upgrade 1b3d5f7a9c20` | 0 / 6.473s |
| Q10-time-empty4-to-0a2 | time | `alembic downgrade 0a2c4e6f8b10` | 0 / 6.545s |
| Q11-time-empty4-reupgrade | time | `alembic upgrade 1b3d5f7a9c20` | 0 / 6.702s |
| Q12-time-convert-verify | time | `python '$Q/time_matrix.py' convert` | 0 / 17.385s |
| Q13-time-zones-rejection | time | `python '$Q/time_extra.py'` | 0 / 40.487s |
| Q14-business-full | joint | `python '$Q/business_matrix.py' business` | 1 / 22.206s |
| Q15-business-full-fixed-oracle | joint | `python '$Q/business_matrix.py' business` | 0 / 23.235s |
| Q16-time-real-readonly-cli | time | `python '$Q/tool_matrix.py'` | 0 / 29.677s |
| Q17-constraints-pairs-races | joint | `python '$Q/business_extra.py'` | 0 / 21.644s |
| Q18-own-connection-real-disconnect | joint | `python '$Q/real_disconnect.py'` | 0 / 19.456s |
| Q19-identity-scope-atomicity | joint | `python '$Q/route_matrix.py'` | 1 / 19.354s |
| Q20-midnight-live-schema | joint | `python '$Q/cross_midnight.py'` | 0 / 23.283s |
| Q21-identity-scope-atomicity-fixed | joint | `python '$Q/route_matrix.py'` | 1 / 22.981s |
| Q22-identity-scope-atomicity-complete | joint | `python '$Q/route_matrix.py'` | 0 / 219.257s |
| Q23-sync-projection-caller-transaction | joint | `python '$Q/projection_matrix.py'` | 1 / 24.364s |
| Q24-faults-complete68 | joint | `python '$Q/fault_whole_matrix.py'` | 0 / 24.892s |
| Q25-disconnect-complete68 | joint | `python '$Q/real_disconnect_whole.py'` | 0 / 22.611s |
| Q26-sync-projection-precision-correct | joint | `python '$Q/projection_matrix.py'` | 0 / 28.794s |
| Q27-retention-freeze-all68 | joint | `python '$Q/retention_freeze.py' before` | 1 / 6.612s |
| Q28-retention-freeze-all68-complete | joint | `python '$Q/retention_freeze.py' before` | 0 / 10.024s |
| Q29-nonempty-downgrade-refused | joint | `alembic downgrade 0a2c4e6f8b10` | 1 / 7.510s |
| Q30-nonempty-no-effects | joint | `python '$Q/retention_freeze.py' guarded` | 0 / 7.602s |
| Q31-retained-after-real-cleanup | joint | `python '$Q/retained_after_cleanup.py'` | 0 / 30.423s |
| Q32-retention-final-conservation | joint | `python '$Q/retention_freeze.py' after` | 0 / 7.023s |
| Q33-final-own-connections | joint | `python '$Q/final_connection_probe.py'` | 0 / 2.110s |

A统一入口`python3 $Q/run_no_db.py <tag> ...`，实际自有offline wrapper的`uv run --offline --frozen --no-sync python`：

- `affected-A`实际`python -c "import pytest,sys;sys.exit(pytest.main([...]))"`，精确5整文件为`tests/test_business_integration_service.py`、`test_business_integration_contract.py`、`test_business_integration_provider.py`、`test_business_integration_migration.py`、`test_business_integration_compatibility.py`；pytest参数`-q -m no_db -p no:cacheprovider --basetemp $Q/pytest-affected-A`，exit0/**161 passed/83.91s**、wrapper92.197s。完整argv另归all-actual-commands.json，不与旧A测试相加。
- `static-completion --script static_probe.py` exit1/1.344s（QA helper错误导入）；`static-completion-final --script static_probe.py` exit0/26.991s，实际preflight/compile/chain75及版本见static-probe-report.json。
- 文件审计`python3 $Q/final_file_audit.py` exit0：157+2/100/870、A后缀、13diff/6旧迁移/3env、四PLAN精确并发差异、秘密边界、`git diff --check`。进程/日志审计`python3 $Q/final_runtime_audit.py`首次exit1（私有helper解码无关进程非UTF8输出），保存原helper/失败记录；只修helper errors=replace后exit0，无DB。最终本checklist链接/空白和old suffix hash另复核。

Q16真实18次CLI不是stub。解释器`/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend/.venv/bin/python3`，入口`scripts/business_time_adoption/main.py`，对`M∈{equipment,performance,monitor}`、`K∈{known,unknown}`各运行下列3条，顺序先三owner known、后三owner unknown；每条共同参数`--module M --source-revision sha256:2532d8423c73f0e9c0a7ac42d616014b2ca09419588cd07a0218bd4ce080cafb`，18条均exit0，真实完整argv/output另归tool-matrix-commands.json：

```text
inspect <共同参数> --output $Q/M-K-inspection.json --env-file $Q/tool-time.private-env
plan <共同参数> --output $Q/M-K-plan.json --inspection-report $Q/M-K-inspection.json --classification-report $Q/M-K-classification.json
verify <共同参数> --output $Q/M-K-verification.json --env-file $Q/tool-time.private-env --inspection-report $Q/M-K-inspection.json
```

QA009的联合schema-only/cleanup精确真实CLI argv/exit由其checklist、B50/B70 command/log及上述两proof负责；本checklist不把他人命令当本QA运行。cleanup固定alias=`arch-be009-be010-proof-qa-mysql`、schema=`arch_be010_r2_qa_joint`、revision=`1b3d5f7a9c20`、expectedStorageEpoch=原冻结epoch、operationApproval=`Owner-approved-B-operation-proposal-2026-11-04`、confirmedBy=`BE009-Verification-B-QA1`。

## 失败历史、局限与收尾

| 原真实失败 | 归因、纠正与证据边界 |
| --- | --- |
| Q14 exit1 | QA全列oracle错误要求过程子表coilNo列，实际coil属于已核父；修私有oracle后Q15新身份完整通过。原已接受投递也归154冻结集合，不抹除部分运行。 |
| Q19 exit1 / Q21 exit1 | QA旧parent负例夹具漏必填production_date；随后私有快照helper拼写`__name__in`。原输入/日志/checkpoint与接受的parent/drive投递均保留；修helper后Q22完成全矩阵。 |
| Q23 exit1 | QA错误要求既有曲线created_at秒列保留毫秒；规范是保留原精度。事务rollback，未改变产品/DDL；修期望后Q26八真实Projection通过。 |
| Q27 exit1 | QA把fact point_ids内部JSON误当list，实际`{items:[point_x]}`；未写库，修helper后Q28/Q30/Q32通过。 |
| static初次 / runtime末次初次exit1 | 分别为私有helper错误import和ps非UTF8解码；保留原helper、退出和纠正说明，无产品改动/DB副作用。若干只读诊断拼写/路径错误未执行项目行为，不能算产品失败或隐藏为全命令0。 |
| Q29 exit1（预期） | 产品对非空4表拒绝破坏downgrade；Q30证无DDL/行变化，不归产品finding。 |
| QA009 B67/B69 exit1 | 对方清理helper错误硬编码4229（QA原冻结实际4275/3）、inspect(Session)错误，均在expiry写前失败；B68只读证六表diff={}及实际计数，B70修helper后真实cleanup通过。完整历史归对方checklist，无产品修复/新finding。 |

所有失败原日志/command与helper备份仍保留。没有修产品、skip/xfail或削弱断言。原三条冻结schema限制仍保留：mapping六表/head因本次新后继产生；一对temperature五表/e4入口原本已失败。未运行默认全仓pytest，也不宣称全仓全绿。此B只证指定合成来源/规模、限定错误/并发窗口和批准清理，不是长稳、性能、真实旧来源分类、生产权限或任意writer防护。匿名producer仍可冒用，采用凭据不是认证/平台ACL；生产writer隔离及真实G-T须各自批准与证明。

停止状态：Q33非root观察同用户joint/time其余连接为0，observer191在finally关闭；所有DB runner均exited/engines.dispose，`ps -axo pid=,ppid=,comm=,args=`无自有Python/uv runner。guard0，未启动API listener。`final-connection-report.json`只声称同QA应用用户可见范围，不冒称root全局事务检查。至此不再连接QA库。

敏感路径仅给root用途清单`sensitive-path-inventory.json` SHA `2204fd52ba90a99321928e62f1f1c1260a8d44b4d033a52f5e63e533bd497fef`：清理前实际nonroot口令仅`Q/tool-time.private-env`（0600），QA009拥有的connection.json不复制；其余Q模块adoption/invalid为合成运维配置，root已按清单删除全部13份，本QA只读核缺失。清理前本QA对自有证据扫描实际root/app/cursor secret，除上述private-env外零命中，不在本文/日志输出值。Q公开源/缓存/报告暂保留供证据核验，Owner审阅及root资源收尾确认后可按记录归属回收；关键矩阵、命令、hash、失败/结论已在本文持久化，不只在tmp。

资源清理现为 **complete**：root在双方无连接交接后按精确ID/labels执行已批回收；本QA仅做只读Docker inventory及文件缺失复核，未删除Docker/卷/网络、未重连数据库。详见下方真实资源收据与独立观察。Human Owner最终验收仍pending。

关键报告：retained-final SHA `b6a497464187c4bfe67976a61a6603f695edc844226d807c62f51a373f14b28b`；retention-after SHA `9dfe1c5edac9b8e1c1cbd7a867a755d378a9fa125f2e105610d8082e91c9a0a9`；final-file-audit SHA `eba783284778c3f782fe3442c364f49299e34a7508675634315c912ccb230476`；final-runtime-audit SHA `b1a4b6897541d22e74c0f19c864796818003022bd266b893a2248e7b9096ab36`。全部关键hash归critical-evidence-shas.json，全部36项目命令归all-actual-commands.json（SHA `0bf407c1e1d7c0e6dbf6661c579a2653c2e4ecb3b2084c4e10b0058299fc017c`），18个实际工具子进程另归tool-matrix-commands.json（SHA `54fd7a6800c1ffc4add060bd1b135b186410e47087f8843ed04667f7eeff896f`）。

## 最终资源收据与独立观察

初次B技术交接checklist SHA `c66a0acf3613b5cba68630569d55f2dd8330d543e38494d2dc607d47ae9dc3bc` 当时如实写清理pending；以下是后续完成事实，不倒填该时点。root完成于 `2026-11-04T22:10:52.665327+08:00`，只执行已批两轮专用资源，0数据库连接，未触现有数据库/真实历史/DAA。原8专用schema随其专用数据卷移除，不重连已删数据库做SQL证明。

root收据根 `/private/tmp/arch-be009-r1-be010-r2-b-my8s9bnu`：

- `cleanup-receipt.json` SHA `23048893ca4c71a6fc7ca76d0e9a466371c41e6fda15880458f8515cac5e41cb`；`owned-resource-cleanup.json` SHA `2c7df8944739811cadc1ac1286f4807b33e9b516140eb4b70b7548c25b155d95`；`sensitive-cleanup.json` SHA `230ee3c391b98001b87cdbf3e437903d7cd0c025b0fbdc8559ead7d3930e9b0a`，独立逐hash相符。
- Dev专用container ID `be0e024aaa7ffda4b9e1148b63d819c2dfa6d984b1f5d8c18958cd4f812645ae`、network ID `43cd94fb05c0599463fddf3db4a75778f4a4b90d496256736fa6e9c9cd0f680a`、volume `arch-be009-be010-proof-dev-data`（CreatedAt `2026-11-04T12:02:03Z`）。QA的精确ID/卷见环境段，CreatedAt `2026-11-04T13:05:41Z`。两轮原公开resources.json的ID、卷创建时刻、task/round labels、名称、四schema集合均与root清理记录逐项相符；未读取Dev或QA已删连接配置。
- 本verification加载docker-expert、docker-project-ops仅用于最后只读资源观察，不运行其build/run/compose示例。真实`python3 $Q/resource_closure_audit.py` exit0；其中三条实际argv均exit0：`docker ps -a --no-trunc --format '{{.ID}} {{.Names}}'`、`docker volume ls --format '{{.Name}}'`、`docker network ls --no-trunc --format '{{.ID}} {{.Name}}'`。可访问Docker daemon且两容器ID/名称、两网络ID/名称、两卷均不在清单，输出中其他资源内容未保存/打印。
- root27份唯一私有口令/key/操作配置路径均`Path.exists()==False`，其中本QA13份全部缺失；仅检查路径，不读内容。独立report `resource-closure-audit.json` SHA `c5622208ecaee6bddf1dabd0b88ba5ba6880a8e567cd22d07bba6d3eaf9fc677`，0DB连接/0Docker变更。

保留 `/private/tmp/arch-be009-r1-b-dev`、`/private/tmp/arch-be010-r2-b-dev`、`/private/tmp/arch-be009-r1-b-qa`、本Q及联合Broot的脱敏命令/日志/报告、公开源码冻结和before/diff证据，仅供QA关闭与Owner最终审阅；实际口令/key/操作配置已删。触发回收条件为Human Owner最终验收后确认无证据/运行/后续依赖，先保持关键结论在各自tasks/checklists；其他任务及A历史临时证据不在本次回收范围。

**最终独立结论：r2本轮隔离B技术 qa_passed，专用资源关闭 complete，无开放产品finding；保留A原始全文/所有失败史。** QA到此停止数据库和仓库写入，将结论交Human Owner；未代签最终验收、生产G-T/采用、发布或DAA完成。最终纯文件复核候选157+2spec仍相符、A后缀SHA保持2e42、文档链接/`git diff --check`通过；最终checklist与公开证据seal摘要由handoff固定，避免在文件中自引用自身hash。

---

# 之前完整A及r1验证历史（以下字节原样保留）

Task ID: ARCH-BE-010
Revision: r2
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r2.7 A source/no-DB only; rework-1
A Verdict: qa_passed
Overall Delivery Gate: qa_blocked
Handoff: r2 QA2 A源码结果 -> Human Owner；F-r2-QA1-001–004关闭，原失败历史保留；真实G-T/数据库/Docker/B/实际迁移/DAA与Human Owner最终验收pending
Updated: 2026-11-04

# r2 QA2：返工1独立复验

**本次仅 ARCH-BE-010 r2 A源码为 qa_passed，四项原QA1 finding已关闭。** 新fresh Verification独立运行最终九整文件：335 passed；另两整文件旧直接调用方87 passed。独立故障、精确数值、原始请求及实际读通道矩阵通过。无开放A实现finding；真实数据库/B、G-T目标采用、历史数据转换、Owner最终验收与部署均未通过或未执行，不把源码通过写成业务永久闭环/provider上线/DAA验收。

本轮仓库只写本checklist。下方原QA1全文作为完整字节后缀保留，SHA256为`8435ec32c7a6ef4ca1156afc4a232ab5f232cce067788fc7b91ab991cc3652e9`，其中r1完整后缀SHA仍为`22782910c1be604094bf07f9e2af5374e93218355f08f7d827e985da1779cb83`。QA1失败、r1既存FLOAT缺陷归因、所有旧失败/冻结断言与当时未完成gate均不改写。

## 独立性、批准与固定输入

- developer_handoff后实际命名verification的新fresh context，未继承Development或QA1的对话推理。独立读取根AGENTS、根/最近backend、app、equipment、monitor、scripts、contracts的README/PLAN pairs、verification.toml、canonical workflow、完整spec/tasks/checklist、正式树/entry/QA1差异和真实DEV输出。适用子树无更近AGENTS。
- 使用project-governance、aiis/BLUEPRINT/CONTRACTS、backend-arch及RESPONSE_CONTRACT/LAYERS/DATABASE_AND_MIGRATIONS/AUTH_SECURITY/MODULE_REGISTRATION/OPERATIONS_TESTING六refs、backend-script-tooling及code-document-indexer，仅验证。TOML的gpt-6.1-sol/max为配置证据；contract_only不代表平台ACL、强制路由或Owner接受。
- Owner精确批准r2 A源码，DB/Docker/实际迁移不执行、DAA暂缓。批准收据归[spec](spec.md)。正式交付树`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，只读HEAD仍`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，未Git写。
- 当前spec SHA256 `955877e96b4695b0c00aa81ef6e862dd6a642e82157edd05d5aeef8c175add5f`；新tasks SHA256 `c55424ff707bd3186aa7ee4e4c468a03200bdc91bcc0400d7365ca5b490061b0`。新tasks仍完整保留旧`1f2367df3f02faf02243d2fc3c94f8e8e1605ac2bccdc4b9e7afcc02ea2ee18f`任务原文后缀。
- DEV当前100文件manifest SHA256 `5499ff917411c7d84fa1e1be079f59246c11179b4d5c4ff82d589a557a2ba7b1`：独立逐项比对正式树与QA2公开副本，100项全部匹配。返工增量确为8产品文件+4正式测试；没有新公开符号。新增五个manifest成员是本Revision原允许面，不是额外范围。
- root proof `/private/tmp/arch-be009-r1-be010-r2-a-y34l21yd`的1059进入前原件全部匹配；`be010-qa2-entry.json`精确102项及`joint-source-candidate-2.json`联合162项全部匹配，后两文件SHA分别为`48506c3965449e1cdc0b42b499f2cc4b1c1e9acaaf040e5d970f0ded0a794bae`和`b65dac8e9b16b61f254ce9fc34984f5be6c3ad9ecca2d7bf5b97723146cc8d48`。BE009独占源码及其QA/B不归本轮重新验收。
- 自有证据根`/private/tmp/arch-be010-r2-verification-qa2-g4m1rbvi`。独立冻结873公开输入，input-manifest SHA256 `cd3711b47f56f0dac55f049d8bdf2013e110a5457fd6a091cbb36c893702cdf4`；entry→QA2 diff SHA256 `21a81115f992ae9a7789a176066716e83c3b61fd651555521b143d2bf06c5115`；QA1→QA2 diff SHA256 `2a66db0a4f1e81653d374d421a10459df843880309b056564aebda174afef34e`。实际核对返工diff及受影响HTTP、Service/CRUD、数值、旧时间调用链，不以DEV335自检代替本次QA。

CODE_INDEX当前`08cf4e2bdb02953a7806d17c32aa3a8b22d5812143feb2e860467f611488869a`与QA1旧`1ce62cba5f6481e06e8c92454c315f751af9ab4b9519442bef388b4a598f09a4`不同。独立逐行diff仅SMA一处说明和八行索引，BE009/BE010段不变；保留root既有scoped外部索引例外，不回退、不归因给本DEV或QA，不验收SMA。原整文件hash差异及双快照仍保留。


末轮final_audit首次exit1另观测根PLAN双语在冻结后漂移，精确仅FF-004 r2 A一行由developer_handoff更新为qa_passed；BE009/BE010行、100源码及102/162交接清单均未变。独立concurrent-plan双快照/diff与final-audit-initial-report.json保留；随后scoped审计只允许该明确外部文档增量和其固定hash，不回退、不归为本任务实现或FF软件验收。冻结873副本不变；不以外部索引变化要求重跑未变的产品检查。

## 环境与命令

macOS；项目backend/.venv的CPython3.13.3、FastAPI0.135.1、Starlette0.52.1、Pydantic2.12.5、SQLAlchemy2.0.48、pytest9.0.2、httpx0.28.1。公开副本由QA2从正式树冻结，不含真实dotenv、.venv或运行数据。只复用项目解释器，不安装/同步依赖；合成process env、TZ=UTC，pycache/uv-cache/logs/basetemp均归自有tmp。

导入项目之前部署sitecustomize/audit guard：阻断socket connect/connect_ex/bind/listen、SQLite含内存、SQLAlchemy Engine/AsyncEngine及已安装DBAPI连接，禁止真实workspace dotenv访问。默认dotenv禁用；只允许测试自有tmp显式创建的public.env/synthetic.env夹具。静态核对实际guard函数归属，全部运行0次guard事件。共享破坏性conftest仅使用no_db路径，另有导入前guard。无真实DB/连接探测、Docker、Alembic CLI/env/真实迁移、监听器/lifespan、真实HTTP/网络/PLC、真实Projection或采用。ASGI只在内存；migration recorder与MySQL DDL编译仅核结构声明。tests_mysql只编译/审阅，未执行入口。无邮件、子Agent或Git写。

统一入口为`python3 /private/tmp/arch-be010-r2-verification-qa2-g4m1rbvi/run.py <tag> ...`；实际项目argv为自有wrapper下`uv run --offline --frozen --no-sync python ...`。每个`<tag>-command.json`保存精确argv/cwd/exit/wall；`<tag>.log`保存原输出。pytest共同参数为`-q -m no_db -p no:cacheprovider --basetemp <自有pytest-tag>`，未触碰默认pytest清理窗口。

| tag / 精确输入 | 真实结果与边界 |
| --- | --- |
| focused：business_integration的contract/api/service/storage/provider/migration/compatibility、business_time_adoption、module_contract九整文件 | **exit0，335 passed/904.19s**；wrapper981.31s。不是DEV的335/801.89s，也不与其他轮次相加。 |
| legacy-direct：test_mapping_api.py、test_mapping_service.py两整文件 | **exit0，87 passed/4.76s**；wrapper12.97s。 |
| expanded-fault --script expanded_fault_probe.py | **exit0，160/160**，八路实际Service重放事务、预提交typed/提交各种Exception、完整session退出与原始ASGI send顺序；每次至多一次commit。 |
| recovery-commit --script recovery_commit_probe.py | **exit0，12/12**；业务拒绝rollback后新事务恢复已提交receipt，再遇ValueError/BusinessException/命名1062/DBAPI提交异常，三owner均保留503 commit_unknown。 |
| precision-exact --script precision_exact_probe.py | **exit0，228 helper+16实际HTTP检查通过**；独立整数/Fraction判据、256有效数字内外/正负、5种Decimal context、zero/最大值/下溢、原0.1精确JSON与固定摘要；新factory0。performance只证helper，未冒认其wire使用FLOAT。 |
| boundary --script boundary_probe.py | **exit0，137/137原始请求**；正常composition/实际Settings、128/129 refs、null/存在/重复/数值类型、64KiB及越界、亚毫秒/媒体/父id，HTTP和完整错误壳一致，新factory0。 |
| transaction --script transaction_probe.py | **exit0，12/12**；真实命名1062第三次成功/耗尽，未知key及1213不当duplicate；rollback→新probe/current-read与≤3尝试。 |
| surface --script surface_probe.py | **exit0，134/134**；preflight、全相关编译、正常8路/57闭合schema逐值等于发布工件、全模型75、4表DDL/FK/16新时间列、13表41列/纯helper/数值边界；DDL SHA `af22cf875025a636e954c61b6aaa8866a1c1352bd992cfbe6ecc24a9ab171f9d`，无执行。 |
| channels --script channel_matrix_probe.py | **exit0，93/93**；从spec精确解析13表41列、按实际HTTP/legacy字段组的旧wire逆转换、真实CRUD谓词及Projection创建来源标记。 |
| legacy-original --script legacy_basis_probe.py | **exit0**；复用QA1原主行反例输入、当前实际DTO/serializer，采用前后完整data相等；外壳Unix timestamp自然变化排除。替身给行不等于证明SQL一定命中该行。 |
| cli-help --script cli_help_probe.py | **exit0**；新解释器裸入口help前后均无app/settings模块加载，不读目标、不访问DB。 |
| f7-source --script f7_source.py | **exit0**；仅组合源码fingerprint为`sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`，liveDatabaseChecked=false；不重做BE009 QA/B。 |
| legacy-mixed --script legacy_mixed_probe.py | **exit1，26/28**；两项为QA跨通道误注入，实际可达性审计后不成立为产品finding，完整解释及原始输出保留下节。 |
| file_audit.py、history-reuse及末轮final_audit.py | 100正式树/副本、873冻结副本、1059原件、696当前受保护文件、六旧迁移、三env84字节前缀/91项、任务历史、头部/新增链接/空白和只读git diff --check均通过，guard0；末轮结果另由handoff固定。 |

关键命令/报告SHA256：focused-command=`46e10ee0f80f7cfe6b1964a9708210f924f487ff67a8417a36f610cb03c18aaa`，focused.log=`66af3178ba60daa567a5b3cb2766d6e2ca7fabc83e99e181f8bbdb9a153b6482`；expanded-fault-report=`83900ae920738211ebed6a697ec6b4149c398c71a0724f44a85ff5968bf60582`；precision-exact-report=`730cf3fb613a1dd6a26dfa8e55019049fbda74f12a57e1ccc8fd4b777a3bbaa5`；channel-matrix-report=`51b00f8812b4c5f25fec3ae974aca4d8553e5671b1ea55f33d3c97abe04b73e5`；history-reuse-report=`bc99037540a885497d1dc1e6c2a4bfe1fde250a48287507ea9612a7e30825115`。全部精确argv/输出hash还归自有evidence-summary.json；关键结果不只依赖临时路径。

## 四项 finding 的关闭

| QA1 finding | 本次独立关闭依据 |
| --- | --- |
| F-r2-QA1-001 | **closed**。完整function/request依赖与session退出后保留本owner既有503 commit_unknown；RuntimeError、DBAPIError、from None及异常抑制不能擦除未知。160矩阵和正式双scope回归通过；成功commit后的普通cleanup仍按500/503分类，无提前200。 |
| F-r2-QA1-002 | **closed**。提交阶段优先于ValueError、BusinessException、命名/非命名Integrity及其他Exception类型，均503 commit_unknown、只一次commit；12个恢复分支故障也通过。真正提交前typed错误仍422、命名1062恢复仍≤3。 |
| F-r2-QA1-003 | **closed**。对F=1/2^149，以整数构造`ceil(10^306/(2^149*999999))*10^-300`及`floor(10^306/(2^149*1000001))*10^-300`和相邻内侧值，Fraction独立比较误差；内侧接受、外侧拒绝。228+16检查保留量化值/两摘要和规范JSON。其r1 A0既存缺陷属性不改写为本r2新引入。 |
| F-r2-QA1-004 | **closed**。已知external_observation observed/reported、receipt/水位固定UTC组不受legacyNaive改写；system/manual/audit各自basis保持。原主行反例、完整data/合法mixed profile、只读输入/DATE/人工0及93通道矩阵通过。实际Projection创建固定unplanned_plc，HTTP两Service才创建external_observation；不以设备NULL或宿主TZ猜历史。 |

### QA2探针纠错：不可达的HTTP子行注入

初次legacy-mixed探针把已知旧HTTP温度子行（equipment_id=line-demo、http_zone_key=zone-1、HTTP父）直接作为替身Service返回给旧`/performances/101/process-data`及legacy嵌套view。在legacyNaive=shanghai_wall/systemWire=utc_wall的合法结构profile下，两项recordTime由`2026-11-03T17:03:00.123000`显示为`2026-11-04T01:03:00.123000`，原报告与exit1如实保留，SHA=`7cb61def31097e82742db4a98cc3dc255acd15637b40ade9088dd39a66f79c33`。

继续追到真实CRUD后核定：旧PerformanceCRUD.get_performance及三过程list_*都过滤equipment_id IS NULL；实际HTTP reader明确选设备域并使用channel=http，三过程UTC来源键正确逆转换。旧HTTP过程writer还要求对应设备域父，不能把该子行写进所注入的legacy父域。private legacy_view未公开为任意通道自动辨源接口；它的递归分支不能被替身越过取行前提后当作真实GET回归。root转达actual PM只读确认：r2约束受支持HTTP/legacy通道，不要求该私有helper处理违背通道前提的任意行；spec/Revision/允许面没有改变。

因此上述两项是**QA探针前提错误，不登记F-r2-QA2-001或要求产品返工**。未删除/改写失败输入、报告或日志；另存legacy-mixed-reachability-review.json并完成真实通道93项。原QA1 F004历史及其PM确认不改判；本次只是关闭其原反例并收窄新探针的证据含义，不宣称验证了真实目标SQL结果或所有历史来源。

## A验收与未完成gate

| 标准 | 当前A已证范围 | 仍须B/目标证据 |
| --- | --- | --- |
| R2-AC01 / r1 AC01–03 | 正常八路/57闭合schema、number/integer、typed200及收窄错误、规范JSON/两摘要/字段存在集合、137边界和精确FLOAT判据通过。 | 八类真实列/NULL/Numeric/FLOAT及持久摘要逐项读回。 |
| R2-AC02 / r1 AC07 | 默认未采用新入口403/503无factory/业务访问，旧路径原对象/原调用旁路；凭据/错profile/错目标拒绝，同会话async/sync固定probe/current-read、无跨事务ready缓存有证。 | 真实UUID/schema/DB时钟/事务可见性、writer隔离与目标采用。 |
| R2-AC03 / r1 AC08 | 精确13表41列+4表16列；实际HTTP/legacy/system/manual/audit组、offset/精度/DATE、只读view和人工0通过；monitor legacyNaive≠systemWire的不可判别created_at明确拒绝。 | 历史全列分类、unknown处置、ID/键/FK/旧摘要/pair/DATE守恒、真实不同宿主/session TZ。 |
| R2-AC04 / r1 AC04–05 | 实际async Service→CRUD及同模块receipt/sourceRefs/mapping/event/watermark源码/替身规则通过；不可变、补NULL原子冲突、补后范围、历史先于stale、零活跃、前卷/重激活、父来源/晚到及人工0；active+target统一主键顺序。无sync Service/假actor。 | 真实持久原子性、完整业务读回/生命周期及人工0两种提交顺序。 |
| R2-AC05 / r1 AC06,11 | F001/002关闭、提交前typed/序列化、全依赖退出、DEBUG脱敏、有限命名1062恢复和恢复提交分支通过。 | 真实RR旧快照、首水位竞争、并发/flush/commit/断线/丢响应恢复。 |
| R2-AC06 / r1 AC10 | 六旧迁移字节不变、唯一f6→0a2→1b3，64→71→75应用表静态差（不含alembic_version），四表Model/DDL/FK/CHECK/index及非空downgrade拒绝通过；无create_all/自动DDL执行。 | 空库/合成旧64行真实两后继升级、约束/数据保护、真实拒退。 |
| R2-AC07 / r1 AC09,11 | Core有限公开符号及owner维护export/准入、纯helper无SQL/Session代理、raw无FK/CASCADE、最小ACK无TTL、只读CLI裸help/candidate无apply通过。 | raw三自然月清理后的实际业务/source/mapping/ACK/父子恢复；生产可变聚合不承诺完整版本历史。 |
| R2-AC08 / r1 AC07,10,12 | 旧JWT/admin/permission/scope/错误壳、disabled新旧404、Projection事务/cursor/audit保护；两旧整文件87通过，QA1旧输出/冻结断言真实保留；正式树与验证输入一致。 | 完整真实旧API/Projection采用、B充分矩阵及Human Owner最终验收。 |

### 旧失败、环境纠错及组合材料

没有把旧19整文件改称全绿：QA1实际为418 passed/8 failed；其中5个自有public.env/synthetic.env节点被QA初始全禁dotenv误伤，限定只允许该QA自有合成夹具后原节点分别3与2通过。该guard纠错不是产品失败或产品修复；本QA2导入前就采用这个有限允许规则，仍禁真实dotenv。

QA2核对19文件hash均与QA1相同、真实旧输出存在；仅重跑两个直接调用方87项，其余复用QA1真实证据，不把不同轮次相加。三条旧schema断言仍开放为冻结profile限制，**未修改/削弱/skip/xfail，也未称已修**：mapping_migration固定六迁移/f6在entry原通过，被本轮获批两个后继触发当前八迁移/1b3；温控固定五迁移与固定e4 head两项在entry原已失败。QA1 entry独立结果仍1 passed/2 failed，不篡改成三项皆既存。当前64/71/75另由本次静态recorder通过。r1的四项旧失败及新增配置数量断言历史也完整留在后缀。

DEV初轮新测试6个字符串`"0"`与number0误比、其49 passed/6 failed、早期源检查失败及返工史仍按tasks保留，不改为历史全绿。QA2保留真实legacy Decimal wire并比较完整data，不修改serializer。三公开env各91项，原84项完整字节前缀不变；新增4 facts+3 adoption来源分开，原grants/英文注释及双语说明保持。

当前联合B输入只核组合源码F7=`sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`和0a2七表→1b3四表链。旧`28edcba...`是历史，未拿它当当前目标；没有连接目标或执行F7反射/schema-only采用。本QA不重复BE009自身QA2，不授予其B/清理SLA/实际采用通过。

## 资源、限制与handoff

所有运行命令已退出。保留自有公开source、bundle-before、输入/差异/历史审计、guard/wrapper/runner及独立探针、明确pytest basetemp/合成fixture、pycache/cache/logs、DDL、完整命令/日志/报告，仍供Owner审阅及后续B/采用比对；QA不执行回收。没有数据库/容器/监听/后台任务、Git分支/worktree或真实配置资源。DEV、QA1、root及并行任务证据未写。协调者在相应Owner gate后确认无运行、后续和证据依赖再按归属收尾；关键结果、输入hash、失败纠错和限制已持久化本checklist。

**本次handoff仅为A qa_passed，四项原finding关闭，交Human Owner审阅。** 整体交付仍qa_blocked：真实MySQL B、历史调查/data-only转换/G-T采用、并发/DBclock/F7反射/raw保留联合验证/清理SLA、DAA接线与Human Owner最终验收均pending，需各自精确授权和证据。QA不批准发布、部署或最终接受；root可据本A事实机械同步索引。

## Human Owner final acceptance

Pending。未记录本r2 A、整体、真实采用/运行或发布部署的Human Owner最终验收。

# r2 QA1及r1完整历史原文（以下字节未改动）

Task ID: ARCH-BE-010
Revision: r2
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: r2.7 A source/no-DB only
A Verdict: qa_failed
Overall Delivery Gate: qa_blocked
Handoff: r2 QA1 -> Development：F-r2-QA1-001–004须在已批准r2允许面返工、重新developer_handoff并启动新的fresh Verification；验证结果交Human Owner，最终验收pending
Updated: 2026-11-04

# r2 QA1：独立源码验证结论

**ARCH-BE-010 r2 的 A 源码验证为 qa_failed，四项finding开放。** 最终9个相关测试文件262项通过，但独立探针另证实：会话退出擦除提交未知、提交阶段ValueError误判为422、FLOAT精确误差边界未严格拒绝、采用态旧实绩UTC输出偏移八小时。不得用测试通过数代替这些失败。仅本checklist被QA写入；实现、测试、spec、tasks、配置及索引均未修复。

本次不是数据库/B、G-T解除、业务provider已采用、生产历史已转换或Human Owner最终验收。旧r1 checklist完整字节作为本文件末尾历史保留，原SHA256为`22782910c1be604094bf07f9e2af5374e93218355f08f7d827e985da1779cb83`；其中r1/A0结论与当时gate不改写为r2事实。

## 独立性、批准与精确输入

- developer_handoff后实际命名Verification的新fresh context，未继承Development对话推理。独立读取根AGENTS、根/backend及最近app/equipment/monitor/scripts/contracts README/PLAN、verification.toml、canonical workflow、完整spec/tasks/r1 checklist、entry原件、实现/diff及真实DEV输出。backend/contracts/plans内没有更近AGENTS.md。
- 使用project-governance、backend-arch及RESPONSE_CONTRACT/LAYERS/DATABASE_AND_MIGRATIONS/MODULE_REGISTRATION/AUTH_SECURITY/OPERATIONS_TESTING六份reference、backend-script-tooling、aiis的BLUEPRINT/CONTRACTS、code-document-indexer，仅做验证。角色TOML的gpt-6.1-sol/max是配置证据；contract_only不构成平台ACL或强制路由。
- Owner原话批准BE009 r1、BE010 r2按STD进入A，数据库/Docker/实际数据迁移不执行、DAA暂不改；以spec收据为准。交付树`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，只读基础HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`；无Git写。
- 本次spec SHA256 `955877e96b4695b0c00aa81ef6e862dd6a642e82157edd05d5aeef8c175add5f`；最终handoff tasks SHA256 `1f2367df3f02faf02243d2fc3c94f8e8e1605ac2bccdc4b9e7afcc02ea2ee18f`。
- DEV最终95文件manifest SHA256 `9b526ab8170198c3c0b144d46b040c3142fffc6d911771c99789c662db00e1f1`；逐项对照正式树及QA副本，全部匹配。不混用已撤回的ea2e manifest/6d116 tasks；锁顺序返工与其114 passed记录按历史消费，未当作本轮QA。
- root proof为`/private/tmp/arch-be009-r1-be010-r2-a-y34l21yd`；独立核对1059个entry原件hash及进入QA时联合候选156项（152实现+4角色文档），均匹配。BE009独占57项与其独立QA不纳入本业务finding；shared11以BE010最终合并为本轮输入。后续BE009自有索引/F7返工由root另外固定，不能冒称本轮已验证其新候选。
- QA证据根`/private/tmp/arch-be010-r2-verification-qa1-lklx0taj`，从正式树独立冻结873个公开输入；input-manifest SHA256 `79c5e0e1d3479f24ab42a5e317ec78cac8e47f255186e271d582d20bd69da513`，entry→handoff diff SHA256 `1955389db2b047b7a573716a0a01344dc101c9591097cad004b852cabe9fc4cf`。另建778文件entry公开副本，只用于三条旧schema断言对照。

DEV曾发生的221/24、257/1、31/1、413/13等失败及修复真实消费，不改写为历史全绿。旧19文件中的10个默认调用回归已由当前源码回归覆盖；三条冻结schema差异仍保留。DEV只报告direct-final132、cleanup1、lock-order114和静态末轮通过，没有假称曾失败的最终整组全绿；本QA的262通过属于本轮独立运行。

## 环境与执行边界

macOS，项目backend/.venv的CPython3.13.3；FastAPI0.135.1、Starlette0.52.1、Pydantic2.12.5、SQLAlchemy2.0.48、pytest9.0.2、httpx0.28.1。项目行为只经自有offline wrapper执行`uv run --offline --frozen --no-sync python ...`，不安装/同步依赖。公开副本排除真实dotenv、.venv、logs/data/dist/build等运行资源，复用正式解释器；合成process env、TZ=UTC，pycache/cache/logs/basetemp全部在自有tmp。

sitecustomize在任何项目import前阻断socket connect/connect_ex/bind/listen、SQLite（含内存）、SQLAlchemy Engine/AsyncEngine和已安装DBAPI连接入口，并审计拒绝真实workspace dotenv访问。默认/runtime dotenv禁用；为核验旧配置优先级，仅允许测试自己在QA tmp_path显式创建的`public.env`/`synthetic.env`。没有读取真实.env。独立检查guard函数归属；观测guard事件为0。

未运行Docker、Alembic CLI/env/真实迁移、数据库连接/连接探测、SQLite、监听器、lifespan、真实HTTP/网络/PLC、现场Projection或真实采用。ASGITransport仅内存；离线migration recorder只解释结构声明，不执行DDL。tests_mysql仅源码检查/编译，未执行其入口。共享破坏性conftest只在no_db标记下旁路清库，QA另有导入前guard；未使用默认pytest清理窗口。无邮件、子Agent、后台进程、branch/worktree或资源回收。

## F-r2-QA1-001：会话退出异常擦除commit_unknown（P1）

依据spec r2.4、R2-AC05：commit开始后的异常必须按503 integration_commit_unknown处理，完整可失败依赖退出不得抹掉未知事实。源码[IntegrationRoute](../../backend/common/integration/http.py)第97–114行在AsyncExitStack退出后统一捕获最终异常，第127–130行只按最终异常分类；session退出的异常覆盖Service已经抛出的commit_unknown。

独立`http_fault_probe.py`从spec提取完整合法请求，使用正常create_app及实际新路由/Service/transaction，只有采用probe、已提交receipt读取和传入Session为无DB替身。执行真实重放事务，commit抛DBAPIError；每例commit恰一次，随后rollback、完整session退出。三个owner分别验证drive、production_observation、process_curve：

| session退出 | 三owner实际HTTP/错误后缀 | 应有结果 |
| --- | --- | --- |
| 正常退出（控制） | 503 / integration_commit_unknown | 通过，3例 |
| 再抛RuntimeError | 500 / integration_internal_error | 503 / integration_commit_unknown；3例失败 |
| 再抛DBAPIError | 503 / integration_unavailable | 503 / integration_commit_unknown；3例失败 |

错误壳仍脱敏、没有200、没有盲重试，但“未知”确认语义丢失。此finding覆盖共享退出边界，不能仅以Service内部rollback失败保护已通过来关闭。返工须保留原提交未知优先级，同时覆盖普通退出失败、成功提交后退出失败、不同yield scope以及完整新session退出；不能略过退出或提前发送成功。

## F-r2-QA1-002：commit抛ValueError误报请求错误（P1）

同一独立HTTP探针令真实Service的`await db.commit()`抛ValueError，会话正常退出。equipment、performance、monitor均实际返回HTTP/code422、`<owner>.integration_invalid_request`；均已进入commit且只尝试一次。合同要求503 commit_unknown，不能建议调用方把可能已提交的冻结事件当格式错误修订。

定位：[equipment事务](../../backend/app/equipment/services/async_integration.py)第142–144行、[performance事务](../../backend/app/performance/services/async_integration_observation.py)第145–147行、[monitor事务](../../backend/app/monitor/services/async_integration.py)第142–144行：`except ValueError`未检查committing，覆盖了提交阶段。返工须按阶段保留未知，继续保证真正提交前的输入/typed结果校验仍422且不commit。

F001/F002共用`http-fault-report.json`：12例，3个控制通过、6个退出覆盖失败、3个commit ValueError失败；SHA256 `dceea677decca4b98e1d5f135240e703cecd66dd73b25a626bdb20c37523a41a`。没有把替身当作真实MySQL提交/断线证明。

## F-r2-QA1-003：256位数字被舍入跨过FLOAT误差拒绝边界（P2；r1既存缺陷）

依据r1 §5.3、r2沿用的严格数值合同：规范binary32后相对误差必须≤1e-6；合法原文预算内的超误差值应422。三份integration_domain.py与r2 entry逐字节相同，因此这是r1 A0已存在、旧QA未覆盖的缺陷，**不是本r2新引入，也不是BE009的abs/context28问题**。r2继续承诺该合同，且r2.6允许本地domain返工，故仍阻止本r2 A通过。

令F为binary32字节`00000001`，即精确分数`1/2^149`。两个合法256有效数字输入分别为：

```text
N1=1.401299865624682695606425189715105846386108327984843756600824884714675797361657963144601332963454545485795485795485795485795485795485795485795485795485795485795485795485795485795485795485795485795485795485795485795485795485795485795485795485795485795485796E-45
N2=1.401297063027754043169686413603502527777734164142351629405438878450912631773228828257809930552191029840220159779840220159779840220159779840220159779840220159779840220159779840220159779840220159779840220159779840220159779840220159779840220159779840220159779E-45
```

独立整数构造：N1=`ceil(10^306/(2^149*999999))*10^-300`，N2=`floor(10^306/(2^149*1000001))*10^-300`。用Python Fraction做精确判据`abs(F-N)*1000000 > abs(N)`，两者均严格成立；不是把被测context调大后自证预期。当前helper的`localcontext.prec=200`把差异舍为边界相等并接受，两值均规范到F。量级上下限copy_abs及context28/50/200普通边界检查通过，不等于此精确误差边界通过。

| 正常composition原始JSON | N1 / N2正文大小 | 实际 | 应有 |
| --- | --- | --- | --- |
| equipment/drive-samples，tv | 各779 bytes | 503 equipment.integration_not_ready | DTO阶段422 equipment.integration_invalid_request |
| monitor/process-curve-samples，lineSpeedSet | 各1261 bytes | 503 monitor.integration_not_ready | DTO阶段422 monitor.integration_invalid_request |

四请求均已通过数值验证才到未采用门，新session factory调用0；未称实际保存了非法测量。performance的同名helper纯函数也复现，但它的本轮wire不使用FLOAT，**不将其列为performance wire失败**。证据`precision_probe.py`、`precision_http_probe.py`及`precision-http-report.json`（SHA256 `4282065e57b95f959790740d094dfb4dfc4f218aa83c28a3b1aa38f9e9b7ae47`）。返工应精确比较整个已允许数字域，保留最大输入预算、规范值/摘要及其他数值规则，不用缩小spec或任意增大context充作证明。

## F-r2-QA1-004：采用态旧HTTP实绩观察时间被legacy basis改写（P1）

依据r2.3.1固定分组：已明确UTC的HTTP reported/observed字段不受basisProfile改写；r2.3.3要求旧wire同瞬间兼容。此例来源明确为`record_source=external_observation`的旧认证HTTP行，不是unknown历史、也不以设备NULL推断时区。合法performance凭据basis为legacyNaive=shanghai_wall、systemWire=utc_wall、manualNaive=shanghai_wall、manualAuditWire=utc_wall，结构校验接受。

独立`legacy_basis_probe.py`给实际旧GET `/api/v1/performances/101`注入受保护测试身份/无DB依赖及只读行，调用实际legacy_output→legacy_view与原DTO/序列化。原UTC行及按同瞬间转换后的上海物理行分别输出：

| data字段 | 采用前原输出 | 采用后实际输出 |
| --- | --- | --- |
| firstObservedAt | 2026-11-03T17:00:00.123000 | 2026-11-04T01:00:00.123000 |
| lastObservedAt | 2026-11-03T17:05:00.123000 | 2026-11-04T01:05:00.123000 |

两响应HTTP200，data仅上述两字段改变；DATE、createdAt/updatedAt及其他值一致。外壳Unix timestamp自然变化明确排除于比较。替身只提供行/会话及测试身份，不代替JWT或真实数据库验证。

定位[performance integration_storage](../../backend/app/performance/integration_storage.py)第19行按channel="legacy"统一选legacyNaive，第51–53行对固定列逐个转换，未使用已知HTTP来源选择固定UTC；[legacy_output](../../backend/app/performance/services/async_performance.py)被旧GET调用。现有storage测试用同一legacy_basis生成预期，未独立保护此来源分组。

原始报告`legacy-basis-report.json`保留；只比较data的复核报告`legacy-basis-reviewed-report.json` SHA256 `552e0f7235578dfab91bf9016c7486f267f7d60c211bb6b3743e79b415a7456d`。返工应在有限静态分组及已有可靠来源标识下保持旧HTTP/legacy各自wire；不能强迫全部legacyNaive=UTC规避，也不因此新增cohort/逐行offset平台。原绑定ORM不得临时改UTC；unknown或不可判别混合仍保持G-T关闭。root转达实际PM对既有条文的只读确认，无spec/Revision变更；finding本身依据本QA运行证据。

## 独立命令与实际结果

统一入口为`python3 /private/tmp/arch-be010-r2-verification-qa1-lklx0taj/run.py <tag> ...`；内部精确argv/cwd/exit/wall-time见各`<tag>-command.json`，stdout/stderr见`<tag>.log`。pytest共同参数`-q -m no_db -p no:cacheprovider --basetemp <自有目录>`。

| tag | 输入 / 实际结果 |
| --- | --- |
| focused | 9完整文件：business_integration的contract/api/service/storage/migration/compatibility/provider、business_time_adoption、module_contract。**exit0；262 passed/453.05s**。 |
| boundary | 独立spec八例，正常composition/实际Settings、原始JSON，128/129 refs、空/null/重复/unknown、bool/string/null测量、snake/duplicate key、精确65536/65537 bytes、亚毫秒/媒体/父0/负数/非数字。**exit0；137请求全通过，新factory调用0**。 |
| surface-final | preflight、全app/common/core/database/projection/scripts/tests/tests_mysql及main/run/build编译，正常8路57闭合schema逐项等于发布文件，75全模型、4表DDL/FK、16新时间列、13表41列、公开Probe、纯helper、普通数值边界。**exit0；134检查全通过**。静态DDL SHA256 `af22cf875025a636e954c61b6aaa8866a1c1352bd992cfbe6ecc24a9ab171f9d`，未执行DDL。 |
| http-fault | **exit1；12例中3控制通过、9失败**，分别属于F001/F002。 |
| precision / precision-http | **exit1**；6个helper精确分数边界均被错误接受，4个实际equipment/monitor HTTP同样通过DTO；F003。performance无FLOAT wire声明。 |
| transaction | 3owner各4情况：命名1062两失败后第3次成功、3次耗尽503、非命名1062及非1062 Integrity无恢复。**exit0；12检查全通过**，实际rollback/probe/read顺序记录；不冒充RR/真实并发。 |
| legacy-basis | **exit1**；实际旧GET对已知HTTP UTC行采用后的data观察时间+8；F004。 |
| legacy-final | 下列19完整旧文件。**exit1；418 passed/8 failed/334.64s**；5个合成dotenv节点被QA初始禁全部dotenv误伤、3个冻结schema断言，不能称全绿。 |
| legacy-explicit-env / legacy-explicit-synthetic | 只允许QA tmp_path测试显式创建的public.env/synthetic.env后，重跑受影响原节点，**exit0；分别3 passed/0.36s、2 passed/0.10s**。不改产品或断言；不把这两轮与418相加成一次全套通过。 |
| entry-three | entry独立公开副本，相同noDB guard下三条schema节点。**exit1；1 passed/2 failed/77.46s**。 |
| file_audit.py | 独立95正式树/副本hash、873冻结副本、1059 entry原件、701保护文件、六旧迁移、三example84字节前缀/91项、新增头部/链接/空白及只读git diff --check。**exit0；guard事件0**。 |

19文件为test_equipment_mapping、test_performance_mapping、test_monitor_mapping、test_mapping_api、test_mapping_compatibility、test_mapping_migration、test_equipment_temperature_api、test_equipment_temperature_service、test_equipment_temperature_config、test_equipment_temperature_migration、test_module_registry、test_module_dependencies、test_module_conflicts、test_module_admission、test_mapping_service、test_projection_runtime、test_projection_mapping_models、test_projection_failure_observability、test_projection_control_plane_registration（均.py）。没有无依据重跑全仓DB测试。

QA自有工具的非产品失败也保留：初次legacy命令误写不存在的三个Projection文件名，exit4/0 tests；改用实际rg文件清单后运行19完整文件。初次surface变量app被import语句覆盖，exit1；只修QA脚本变量后surface-final134通过。`ps`只读盘点被sandbox拒绝，未请求升级、未据此宣称进程盘点已通过。上述均不计为产品finding。

### 三条冻结schema断言的独立分类

| 原节点 | entry独立结果 | 本轮结果与边界 |
| --- | --- | --- |
| test_mapping_migration::test_six_revision_60_to_64_model_parity_and_53_protection | passed，六条/f6 | 当前八条/1b3失败；是获批两后继新触发，不是entry已有失败；原文件不在本轮允许改动面，字节保留。当前64→71→75及旧64子集另由focused静态recorder通过。 |
| test_equipment_temperature_migration::test_five_revisions_58_60_58_parity_old_bytes_and_mysql_types | failed，六条对冻结五条 | 当前八条对五条仍失败；保留原断言，未skip/xfail/削弱。 |
| test_equipment_temperature_migration::test_single_explicit_head_and_no_data_migration | failed，f6对冻结e4 | 当前1b3对e4仍失败；不把当前head说成f6，不表示实际库head。 |

A0命名fixture的重建明确删除后加facts package/两个新migration及7个新env键，只重现84项/68 metadata/models-only的历史schema/config面；其代码仍是当前源码，不冒充旧二进制。该变更在r2.6的profile分组允许面，原冻结C2/E/F/BE003/BE006断言没有被削弱。当前三example为91项，完整entry84字节前缀保持，新增BE0094+采用3，不覆盖原grants/英文标题；六旧migration字节全部保持。未发现未归属的新增公共backend/frontend/contracts路径。

## AC分阶段审计与限制

| 标准 | 本次A可证事实 / verdict | B或目标采用仍未证 |
| --- | --- | --- |
| R2-AC01 / r1 AC01–03 | 正常8路、57闭合schema、typed200/错误、number/integer、八例/摘要/存在集合及137原始HTTP边界通过；**F003数值极限失败**。 | 八类真实逐列读回、Numeric/NULL/FLOAT及持久摘要/unique。 |
| R2-AC02 / r1 AC07 | 未采用新入口403/503且不进入新factory，默认旧路径旁路；采用凭据/错profile/错目标拒绝、3组async/sync传入会话探针、无跨事务ready缓存有源码/单测证据。 | 真实UUID/schema/clock与事务current-read、目标采用及writer隔离。 |
| R2-AC03 / r1 AC08 | 13表41列、4新表16列、有限basis/Probe、纯转换、aware/naive同瞬间及DATE/精度/人工0分组有证；**F004旧HTTP观察wire失败**。monitor不可辨混合basis拒绝通过。 | 生产历史全列来源、unknown处置、ID/FK/旧摘要/DATE/pair守恒及不同实际系统/session TZ。 |
| R2-AC04 / r1 AC04–05 | 八路实际async Service→CRUD，现有业务目标及本模块receipt/事件/sourceRefs/mapping同事务源码；262组包含不可变、补NULL/原子冲突、补后范围、历史先于stale、父来源/缺失、零活跃水位、人工0、重激活。统一active OR target一次ORDER BY id FOR UPDATE源码/测试通过；无sync Service/伪actor。 | 真实并发、两提交顺序、完整生命周期/父ACK/晚到逐项落库；替身不证明持久原子性。 |
| R2-AC05 / r1 AC06,11 | 命名1062≤3/rollback后重读、预提交typed/序列化、完整退出不提前200、DEBUG脱敏及12事务探针通过；**F001/F002提交未知语义失败**。 | RR旧快照、首水位竞争、实际flush/commit/断线/丢响应恢复。 |
| R2-AC06 / r1 AC10 | 六旧字节、唯一f6→0a2→1b3、64/71/75静态差、四表Model/DDL/FK/CHECK/索引一致，非空downgrade拒绝，无create_all执行/自动DDL/seed。 | 空库/旧行两后继真实升级、约束/collation/数据保护、实际downgrade拒绝。 |
| R2-AC07 / r1 AC09,11 | 公共符号及owner维护export/准入正负例、纯helper无SQL/Session代理、raw无FK/CASCADE、业务最小回执无TTL；只读CLI help先于配置/目标，无apply，candidate不自动adopt。 | raw三自然月清理后真实业务/来源/ACK/父子恢复；生产可变聚合不承诺完整版本历史。 |
| R2-AC08 / r1 AC07,10,12 | 旧8 POST认证、模块disabled新旧404、权限/旧壳、Projection registry/事务/cursor/audit相关回归与保护hash已核；19文件/entry差异如实记录；**F004采用态兼容失败**。 | 完整旧GET/PUT/DELETE与Projection真实采用、B两轮充分矩阵及Owner最终验收。 |

已审阅两个tests_mysql独立入口的显式目标guard与现有矩阵，仅编译而未执行；它们存在不证明完整B覆盖或通过，真实竞争/故障/时间采用/保留联合材料仍须另批目标并独立验证。BE009事实七表细节及其返工F7由其独立QA/root负责。根/backend索引由coordinator同步，本QA不写。

## 资源、返工与最终handoff

本轮保留QA自有根下source、entry-source、bundle-before、guard初始/当前脚本、offline wrapper、runner/独立探针、明确pytest basetemp、pycache/uv-cache/logs、输入/差异/DDL/命令/结果与审计报告。所有运行已退出，无DB/容器/监听/后台任务/branch/worktree。未清理任务外资源；QA不回收。root在返工、后续fresh QA及Owner相应gate后核对依赖再按归属收尾。关键finding、完整向量、输入hash、命令及结果均持久化本文件，临时目录不是唯一证据。

**串行交接：本r2 QA1停止写入，A=qa_failed，F001–004开放，交实际Development在同一已批准r2有限允许面返工。** 保留本失败历史及r1全文；修复后更新tasks、冻结新输入/输出、重新developer_handoff，再调用新的fresh-context Verification。A通过后也不自动授权数据库/Docker/B、G-T采用、实际迁移、DAA、发布或部署。Human Owner最终验收仍pending，QA不代行接受。

# r1 checklist完整历史原文保留区

以下从Task ID起逐字节保留写入前r1 checklist；旧顶部元数据只表示当时r1状态，不覆盖本文件顶部r2 QA1 verdict。

Task ID: ARCH-BE-010
Revision: r1
Status: qa_blocked
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA2 A0 -> Human Owner：A0 独立复验通过，F-QA1-001/002 关闭；请审阅 A0 与待确认 T1 提案；整体 G-T / A1–A3 / 精确迁移 / B 仍阻塞，Human Owner 最终验收 pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Verification Scope: A0 only
A0 Verdict: qa_passed
Overall Delivery Gate: qa_blocked

# QA1：ARCH-BE-010 r1 A0 独立验证

## 结论与精确输入

本次 **A0 为 qa_failed**：八路的 sourceRefs 数量超限 HTTP 状态不符批准合同；Development 文档的 Allowed Writers 元数据不符 canonical bundle 合同。Verification 没有修改实现、测试、spec、tasks 或配置。上述失败须串行返回 Development；本文件不授予 Human Owner 最终验收。

即使修复 A0，**整个 ARCH-BE-010 r1 仍不可 qa_passed**：T1 时区/迁移提案待 Owner 确认，G-T 未解除，A1–A3 业务接线、精确 Alembic 后继、真实持久回执和另批 B 均未完成/未获本次实施许可。当前只有准备态，不能作为已发布、已采用的业务 provider。

- 实际命名 `verification`，fresh context，未继承 Development 对话推理；独立读取根 AGENTS、根/backend README/PLAN pairs、最近 equipment/monitor/app 规则、canonical workflow、verification.toml、完整 spec/tasks、实现、entry/diff 和可用 DEV 输出。TOML 的 `gpt-6.1-sol/max` 是配置证据，不宣称独立确认了运行模型/effort。
- 适用 skill：project-governance、backend-arch（RESPONSE_CONTRACT / LAYERS / DATABASE_AND_MIGRATIONS / MODULE_REGISTRATION / AUTH_SECURITY / OPERATIONS_TESTING）、aiis（BLUEPRINT / CONTRACTS）、code-document-indexer。仅验证，不执行修复/初始化。
- 精确 Owner 批准为 spec §12 原话：批准 r1、选择 T1、仅先 A0；时区方案先确认，数据库与 Docker 不执行，旧认证接口保持。
- 交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；基础 HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`。
- 批准 spec SHA256 `c33cd260dc74542f36436f31738e823734ae4bc75cf087a0dbb76c2d4c3dcaf9`。
- 本次消费的 developer_handoff tasks SHA256 `5830d749841be0ecff349ff1007e52b217e1ebcf9a9f603a0170af28d7c3669a`。
- Development source-manifest SHA256 `54e4bc6ad879843c2062cc3ccc6e2f679936cac585166decaf21c357ede5b7af`。独立逐项校验其 **50 个 after hash**、before/entry 对应关系及 **745 个 entry 原件 hash**，无不一致；独立校验 **715 个受保护 backend/frontend 公共文件**，无漂移。未把 DEV/root 的检查当作 QA 运行。
- 自有证据根 `/private/tmp/arch-be010-r1-a0-pxmh71r0/verification/`。`input-manifest.json` SHA256 `4139e1a23f63bae54554bc9b015e8106b681981def97b0d8b1063e24b767e240`，固定 766 个公开输入文件；独立 entry→handoff `verification.diff` SHA256 `ebfb4b6f900536912bc3b1e26880d60aebae793b0541111b66469ea697d10cfe`。关键结论、失败详情与限制持久化于本文件，不仅依赖临时目录。

## 环境与执行边界

2026-11-04，macOS 工作树，项目 `backend/.venv` 的 CPython 3.13.3；FastAPI 0.135.1、Starlette 0.52.1、Pydantic 2.12.5、SQLAlchemy 2.0.48、pytest 9.0.2、httpx 0.28.1。项目行为统一经 `uv run --offline --frozen --no-sync python ...`，未安装/同步依赖，未修改 pyproject/lock。

QA 自己从冻结的正式树创建 `verification/source/{backend,frontend-js}`；entry 四节点对照使用独立 `verification/entry-source/`。副本排除真实 dotenv、.venv、logs/data/dist/build 等运行资源，只复用正式项目解释器；只注入合成占位 process env。验证进程 TZ=UTC，用于核对业务时间不随宿主系统时区变化。忽略的本机 `.python-version` 和 frontend/public 资源不在 entry 公共源码审计口径，不读取/修改它们，也不将它们认作本任务新增文件。

所有 uv 子进程通过自有 wrapper 强制 offline/no-sync，并由 sitecustomize 在导入应用前拒绝 socket connect/connect_ex/bind/listen、sqlite3、SQLAlchemy Engine/AsyncEngine 及已安装 DBAPI 的连接入口。独立核对关键入口实际来自 sitecustomize；所有检查 **0 次 guard 触发**。ASGITransport 和原始 ASGI send 探针只在内存运行，未启动 lifespan、监听器、真实 HTTP、浏览器、PLC、Projection、数据库（含 SQLite/:memory:）、Alembic current 或任何 Docker 命令。Git 操作只读。

pytest 全部显式使用 `verification/pytest-<tag>` basetemp；未触碰默认 pytest 清理窗口或 DEV 证据。并行 AW/DAA/SMA/DS/FF/C# 改动保留。

## Findings 与返工要求

### F-QA1-001：sourceRefs 数量超限错误返回 422（A0 实现失败）

依据：批准 spec §5.1 将 64 KiB、深度12、sourceRefs 最多128项列为固定上限，超限为 HTTP413；§9.1 要求模块 `integration_payload_too_large` 失败壳；AC02 要求原始 HTTP 状态/错误码一致。

复现：取 spec §6 的任一完整合法请求，准入配置 enabled=true、equipmentIds=["line-demo"]、producerIds=["sma-demo"]，将 sourceRefs 替换为：

```python
[{"kind": "external_event", "sourceId": "source", "sourceEventId": str(i)}
 for i in range(129)]
```

通过正常 `create_app(testing=True)`、实际 Settings 依赖及原始 JSON ASGI 投递，无凭据。八路请求长度仅 **8931–9539 bytes**，均未触及体积/深度限制；128 项均正确返回503 not_ready，129 项均实际返回：

```json
{"code":422,"message":"<module>.integration_invalid_request","data":null,"errorCode":"<module>.integration_invalid_request"}
```

应为 HTTP/code **413**、`<module>.integration_payload_too_large`、data=null。无数据库依赖或写入。

定位：[envelope.py](../../backend/common/integration/envelope.py) 第107行 `Field(max_length=128)` 产生 Pydantic 列表超限；[http.py](../../backend/common/integration/http.py) 第122–123行将全部 RequestValidationError 转为422，丢失本合同的数量超限413语义。当前测试未覆盖129项。

证据：`independent-probe-report.json` 437项中435通过，同一缺陷的 status/shell 两断言失败；`limit-matrix-report.json` 八路×128/129共16行，8个129项节点均重现，命令 exit1。请求生成器和完整结果分别为 `independent_probe.py`、`limit_matrix.py`，未调用 DEV 请求 fixture 生成预期。

返工验收：在已批 A0 面恢复 sourceRefs>128 的413及对应模块错误壳；为八路覆盖128/129和既有 malformed/duplicate/unknown 等422边界，保持64 KiB/深度/匿名准入/旧认证及无DB保护。不通过改变 spec、放宽限制或削弱旧断言消除失败。返工后需新 handoff 和新的 fresh QA。

### F-QA1-002：tasks Allowed Writers 元数据不符 canonical bundle 合同

[tasks.md](tasks.md) 第5行为 `Allowed Writers: Development, Human Owner`。已加载 project-governance 的 PLAN Spec Bundle v2 表格规定 tasks 为 `Development`；其 canonical `scripts/check-governance-bundle.sh` 第367–382行也按精确值 `Development` 检查，否则报 `invalid Allowed Writers`。

独立 `python3 verification/metadata_audit.py` 对 spec/tasks 的12个必要字段检查，仅此字段失败，exit1；实际/期望保存在 `metadata-audit-report.json`。请 Development 在自己的 tasks 面纠正为 canonical 元数据，保留真实实施/失败记录。此项不改变 Human Owner 的范围审批或最终验收权，QA 不代写该文件。

## 独立命令与结果

执行入口为自有 `python3 /private/tmp/arch-be010-r1-a0-pxmh71r0/verification/run.py <tag> ...`；该 helper 只准备/编排公开副本，项目行为实际 argv 为 `uv run --offline --frozen --no-sync python ...`。各 `<tag>-command.json` 固定精确 argv/cwd/exit；日志为 `<tag>.log`。

| QA 检查 / tag | 实际输入 | 结果 |
| --- | --- | --- |
| `a0` | `pytest.main`：完整 `test_business_integration_{contract,api,migration,compatibility}.py` 与 `test_module_contract.py`；`-q -m no_db -p no:cacheprovider --basetemp verification/pytest-a0` | **exit0；180 passed / 40.99s**。不是整体任务通过。 |
| `independent` | `--script independent_probe.py`；独立解析 spec 八份 JSON；正常 composition、原始 JSON、数值/时间/摘要及 native ASGI send | **exit1；437 checks，435通过，2失败均属 F-QA1-001**。 |
| `limit-matrix` | `--script limit_matrix.py`；八路正常 composition、128/129个唯一合法引用 | **exit1；8/16状态符合，8个129项均触发 F-QA1-001**。 |
| `related` | 下列14个完整旧测试文件，no_db 与独立 basetemp | **exit1；362 passed / 4 failed / 164.16s**；归因见下表。 |
| `baseline-four` | entry 独立公开副本，运行下表四个精确节点，完全相同 guard/项目解释器 | **exit1；3 failed / 1 passed / 0.80s**。 |
| `surface-final` | `--script inspect_surface.py`；preflight、全量相关 compileall、正常 composition/OpenAPI 引用递归解析、显式 Model package metadata、四表静态 MySQL DDL/FK | **exit0**；428个 `$ref` 全可解析，8路 requestBody 有 typed schema；正常路由组合即时metadata为63，显式加载所有模型包后为68；四表FK所引列均有已声明唯一约束，无DDL执行。 |
| `log-and-guard` | `--script log_and_guard_probe.py`；实际 guard函数归属、独立 JSON Lines 新路由503日志与合成敏感标记 | **exit0**；受控 producer/event/resource/equipment/errorCode 存在，完整body、Authorization、source/mapping合成私有标记未进入日志。 |
| 元数据 | `python3 verification/metadata_audit.py` | **exit1**；仅 F-QA1-002。 |
| 文件/链接/空白/冻结 | `python3 verification/file_audit.py`；内部 `git diff --check -- <50文件> <tasks>`、新增本地链接与新文件头检查、输入与正式树hash | 最终 **exit0**；无范围外公共新文件、源码/副本漂移、尾空白、缺新文件头或新增本地断链；三env旧完整前缀保持，六条旧migration字节保持。 |

相关14整文件为：`test_equipment_mapping.py`、`test_performance_mapping.py`、`test_monitor_mapping.py`、`test_mapping_api.py`、`test_mapping_compatibility.py`、`test_mapping_migration.py`、`test_equipment_temperature_api.py`、`test_equipment_temperature_service.py`、`test_equipment_temperature_config.py`、`test_equipment_temperature_migration.py`、`test_module_registry.py`、`test_module_dependencies.py`、`test_module_conflicts.py`、`test_module_admission.py`。未无依据重复其他历史全套483/604。

初次自有 surface 命令 exit1 是探针误把“路由组合即时metadata”当成“全模型metadata”：只得到63；显式 `import_model_packages()` 后静态核对为68，后续通过，未修改产品。初次文件盘点把三项已被 `.gitignore` 排除的本机资源当成未知新增而 exit1；按与entry相同公共源码口径区分后通过，不把未受基线覆盖的本机资源宣称为已验证源码。若干只读探索命令因猜测的 monitor 文件名不存在而 exit1/2，随后用 rg --files 找到实际 `async_process_curve_sample.py` 等路径完成核对；均非产品运行失败。

### 四项旧测试失败的精确归因

| 精确节点 | entry 独立事实 | A0 独立事实与裁定 |
| --- | --- | --- |
| `test_mapping_compatibility.py::test_69_original_public_assignments_preserved_plus_three_empty_scopes` | **passed，72项** | **failed，84≠72；本轮新增12默认关闭键新触发**。不能列为 BE006 既有失败。旧原文前缀未变，新命名 BE010-A0 84项/68表 profile 自检通过。 |
| `test_equipment_temperature_config.py::test_three_examples_add_only_empty_scope_with_english_comment` | failed，72≠69 | failed，84≠69；entry已有冻结数量差异，本轮又追加12项。 |
| `test_equipment_temperature_migration.py::test_five_revisions_58_60_58_parity_old_bytes_and_mysql_types` | failed，六条/f6对比冻结五条 | 同一失败；六条旧migration哈希保持，A0未增migration。 |
| `test_equipment_temperature_migration.py::test_single_explicit_head_and_no_data_migration` | failed，f6对比冻结e4 | 同一失败；只是静态源图，不是实际库状态。 |

QA核对这12项均在批准A0 allowlist内，默认False/空集合/unadopted，三env完整旧72项前缀SHA保持，旧权限/grants未变，独立命名profile没有改写历史fixture。该有界配置增量符合A0准备范围；旧数量断言失败仍真实保留，既未 skip/xfail/改弱，也不宣称相关suite全绿或另授例外批准。

## AC01–AC12 分阶段审计

| AC | 本次 A0 已证范围 | 未证 / 后续 gate |
| --- | --- | --- |
| AC01 八路合同 | 精确八个 POST、八个 owner-local 输入/结果DTO；十温度、20 drive、参数七项、生产13项、三过程、曲线33项字段核对；八份spec JSON均能验证；OpenAPI输入引用全可解析。 | API→业务DB逐项读回、实际receipt引用没有实现；OpenAPI provider 输出能力限制见下文。 |
| AC02 严格JSON/缺测 | **失败 F-QA1-001**；其余原始重复（含转义同名/嵌套）、未知/snake、bool/string/null、0、UTF8/nonfinite/极端Decimal、精度/范围/FLOAT32下溢、64KiB/深度/媒体/压缩检查通过。 | sourceRefs超限413须返工；真实NULL、Numeric/binary32持久化仍需B。 |
| AC03 身份/摘要 | 两摘要纯函数、独立规范向量、UTF8原样key/值、字段存在集合、身份/来源/mapping与业务摘要分离、父id/resource参与、等瞬间offset及引用排序已证。 | 持久unique、真实409优先级和重放稳定原提交结果待A1–A3/B。 |
| AC04 写入矩阵 | 只证输入存在集合、数值域/过程输入顺序/缺测；无任意handler/表名/SQL接线。 | 不可变/补NULL/冲突原子性、补后整行范围与晚到持久行为没有新实现证明。 |
| AC05 生命周期/父子 | in_production卷号、非在产字段限制、输入起止次序/秒范围和三过程输入范围检查；旧规则源码与相关回归供兼容依据。 | 新水位/历史事件/退出重激活/父ACK/人工0两提交顺序没有实际接线或DB证明；不能以旧测试代替。 |
| AC06 并发/故障 | 局部adapter native ASGI验证同步/异步 yield、request/function 两依赖scope：退出失败只发送一次500/503；DEBUG不泄露，不提前发送200。 | RR/current read、首次水位竞争、flush/commit/unknown/丢响应、独立Session均待另批真实B。 |
| AC07 认证/准入 | 正常composition无凭据有效scope八路均503，默认/空/越设备/producer为403，伪profile不能绕过；旧八POST无凭据401；模块关闭并重组后新旧POST404；无get_db。旧实现/权限/Projection保护hash无变。 | 所有旧GET/PUT/DELETE全链运行未重新证明；成功准入写入须后续。scope只是匿名声明准入，不是设备/producer身份认证。 |
| AC08 时间/采用 | 上海毫秒、等瞬间offset、非零亚毫秒拒绝、事实observedAt必要精度、DB时钟显式注入纯函数和UTC宿主下稳定规范值已证；T1源码提案审计见下文。 | **G-T仍blocked**；未确认历史/真实DB时区，未执行转换，未来时钟未接实际DB，不得称同列已采用。 |
| AC09 永久业务/恢复 | 三receipt+事件Model无TTL、无raw FK/CASCADE、必要source/mapping/稳定结果可声明持有；纯receipt stale/duplicate原事实输出检查通过。 | 没有持久receipt或raw到期后的真实恢复/父子/outbox证明；不承诺可变生产聚合的自动历史版本。 |
| AC10 模块/Schema/兼容 | 68表完整metadata；四新表静态DDL的stream CHECK、完整VARBINARY投递unique、设备/父/目标FK和已声明目标unique核对；无自动default/UTC时钟/DDL/seed；六旧migration不变。 | 精确后继未批准、Model≠已迁移Schema；空库/旧行升级、真实FK/collation/unique和破坏性downgrade拒绝待B。 |
| AC11 公共复用/安全 | 21个有限新增公开符号正式登记；无业务字段/错误/SQL进入Core；旧全局serializer不变；模块StrEnum、真实错误壳、依赖退出脱敏和受控JSON Lines已证。 | 实际已提交成功日志、回执HTTP及provider完整机器合同尚未证明。 |
| AC12 真实交接 | 独立运行、输入冻结/diff/链接/头部/compile、相关全文件和entry对照真实记录；无削弱旧断言。 | **F-QA1-002元数据失败**；本次qa_failed，需新DEV handoff+新的fresh QA；Owner最终验收pending。 |

### Provider 文档能力限制（不是上述实现 finding 的替代或已通过声明）

正常 OpenAPI 的428个 `$ref` 均可解析，typed requestBody可定位，但 **不能称完整 provider 响应合同已完成**：八路自动生成的200 schema仍为 `{}`，422仍指框架HTTPValidationError，当前实际403/413/415/422/503局部失败壳尚未逐operation建模；owner-local receipt DTO尚未绑定已实现成功HTTP路径。Decimal默认输入schema显示 number|string，严格运行时已独立确认拒绝数字字符串。

后续接通/发布业务provider前，必须按已批准合同补齐并核对：只收JSON number的机器schema、成功信封/八结果DTO、模块失败壳与各真实HTTP状态、完整引用可解析性、生成样例与原始ASGI行为一致。当前A0的source/运行时检查不替代该后续可消费合同，也不证明业务ACK已经存在。这里只记录准备态能力限制，不要求QA静默修复或以其掩盖 F-QA1-001/002。

## T1 源码提案与 gate 审计

[tasks 的逐列提案](tasks.md)是**待Owner确认的源分析**。独立对照现有 Models、domain、HTTP Service/CRUD 与 sync helpers，可确认：旧HTTP source-time规范化为naive UTC/旧wire毫秒Z；BE003/006 receipt系统列为UTC_TIMESTAMP(3)；drive/参数有CURRENT_TIMESTAMP(3)默认；Projection aware→UTC/naive原样，生产fact时间可直接写入；人工及legacy时间、DB func.now() 的真实时区不能从源码断定。manual_override_at同时存在Python now()与DB func.now()路径，均需未来来源/DB证据；不能仅凭某一writer推定全列。

提案正确保留了以下待批约束：

1. 逐列/来源分类UTC、Shanghai、其他已知offset、unknown；unknown冻结/隔离也不允许向同列混写Shanghai，G-T继续不解除。
2. 保持旧UTC wire、旧fingerprint算法/存在集合和原actor回执；物理时间转换不把旧摘要/result重新解释为bi-json/v1，不自动迁入producer身份。
3. 来源自然键、父/设备FK、receipt来源列、生产水位在同一停writer/采用窗口成组转换验证；DATE不机械加8，保持毫秒、ID及业务值。
4. 人工重量非NULL（含0）及审计优先；manual pair→reported pair→first/last之前先确认同一时间语义，unknown pair不与新Shanghai值直接相减；过程duration仍为分钟。
5. 旧Projection business/cursor/audit同事务与每设备业务域唯一权威writer保持；不能新旧同时推进同一生命周期，也不盲迁raw/cursor时间。
6. G-T的前置是真实且独立获批的时间专项证明/采用回退材料；**A1–A3完成后的完整新业务B** 是后置gate，不循环要求尚未实现的新业务B来解除G-T。
7. 当前静态源链六条至f6不代表实际库版本；精确新migration路径/revision/down_revision仍待PM按将来head及已批时间范围锁定。A0不得创建/接链或执行数据库动作。

本次未发现需要把该提案当作已执行整改的证据；也未授予提案批准。Owner仍需确认兼容/分类、停切writer和保留数据回退原则，再由PM冻结有界时间范围/精确迁移及相应真实目标与动作。后续若改变本spec的范围、allowlist、风险或验收，按workflow回PM新Revision。

## Acceptance Audit、资源与最终 handoff

| 层次 | 当前事实 / 下一 gate |
| --- | --- |
| 本次 A0 | `qa_failed`；F-QA1-001与002开放，返回Development，不授予准备态通过。 |
| 后续未完成 | G-T未解除，A1–A3未接线，实际持久业务/回执/水位/并发/恢复与精确迁移均未证。 |
| 另批运行gate | 数据库/Docker/隔离MySQL B、现场采用/监听/PLC、发布部署仍须具体批准。 |
| 旧链路 | 旧认证API和sync Projection作为保留兼容/回退路径；无停writer、切流或已采用证据。 |
| Human Owner | 时区提案确认与最终验收均pending；QA不代行批准。 |

QA 创建/写入的仓库文件只有本 checklist。自有 `verification/` 中保留两公开源码副本、显式pytest basetemp/合成fixture、pycache/uv-cache、guard/wrapper/helpers、OpenAPI、静态DDL、diff/hash与命令/日志/报告，均无真实配置或数据；所有进程已退出，没有监听、数据库、容器、后台任务、Git分支/worktree资源。DEV与root既有证据只读保留。

这些临时资源仍供Development修复和下一轮fresh QA对照，当前不清理。协调者在修复/后续QA与Owner gate后，确认无运行、后续或证据依赖再按归属回收；保留本文件中失败重现、命令结果和冻结hash作为持久证据。不清理他人资源，不另开root唯一notifier窗口，不发邮件。

**串行handoff：** QA1到此停止写入；主协调将 F-QA1-001/002交实际Development，仅在已批准A0面返工并更新其tasks，随后冻结新源码/输出，调用新的fresh-context Verification。当前失败历史保留，不覆写成已通过。结果待真实QA gate后才交Human Owner做最终验收。

## Human Owner final acceptance

Pending。未记录 Human Owner 对A0、时区方案、整体任务、真实运行或发布部署的最终验收。

# QA2：ARCH-BE-010 r1 A0 rework-1 独立复验

## 当前结论与独立性

**本次 A0 子结论为 qa_passed，F-QA1-001 与 F-QA1-002 已独立关闭；整个 ARCH-BE-010 r1 仍为 qa_blocked。** 这里只通过批准的源码/no-DB 准备范围，不代表八路业务写入、持久回执、完整 provider、G-T 或 B 已完成。上方 QA1 正文及失败证据原样保留；顶部元数据表示当前 QA2 状态，QA1 当时的 Status/A0 Verdict 仍为 qa_failed。

本轮是 developer_handoff 后实际命名 `verification` 的新 fresh context，未继承 Development 对话推理。独立完整读取根 AGENTS、根/backend README/PLAN pairs、app/equipment/monitor 最近说明和 equipment PLAN、canonical workflow、verification.toml、spec/tasks/QA1 checklist、相关实现/diff/DEV 输出；backend/plans/contracts 内未发现更近的 AGENTS.md。使用 project-governance、backend-arch 的 RESPONSE_CONTRACT/LAYERS/DATABASE_AND_MIGRATIONS/MODULE_REGISTRATION/AUTH_SECURITY/OPERATIONS_TESTING、aiis 的 BLUEPRINT/CONTRACTS、code-document-indexer，仅做验证。TOML 的 `gpt-6.1-sol/max` 是配置证据；本 profile 为 contract_only，不宣称平台 ACL、强制路由或 Owner 验收。

## 精确输入、范围及并行索引审计

- 正式交付树仍为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，只读 HEAD 为 `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`。精确 Owner 批准仍只包括 r1/T1/A0；时区方案先确认，数据库/Docker 不执行，旧认证保持。
- 批准 spec SHA256：`c33cd260dc74542f36436f31738e823734ae4bc75cf087a0dbb76c2d4c3dcaf9`；本次 tasks SHA256：`17d3871af2916a6edc250fc89069f8de5de4f35bd99e86c219878b49f69e5286`；写入前 QA1 checklist SHA256：`01bb9dfe872b4a7a48f3c1fb2cf30a610049e603357489add716991aa6390ea0`。均与精确 handoff 一致。
- 最新 DEV 50 文件 source-manifest SHA256：`311d8f5f7faa92b8a69ad613e5aeffa21fd65b12823ae37783ba5648ef3152cf`；rework.diff：`5505d8249924df4828fd8afc53397ceb5449d2b0ca69aaf196fd997aa629aa4c`；DEV audit-report：`1565912cec48f09812895795dc08f250b3d046b3c0c07b6e807d40fe502b89cf`。独立逐项比对全部 after 与 entry before，在开始冻结时 50 项均匹配；745 个 entry 原件及 715 个受保护公共文件全部匹配，保护映射 SHA256 仍为 `b1c2d53d0239e392e94d6f8bab1dea64c4da111b0def45c28e60de92727dccb8`。
- 相对 QA1 实现仅 `common/integration/http.py` 的三行顶层 list 数量 cap 及 API 测试 40 节点变化；tasks 修正 writer 并追加返工事实。当前 http.py SHA256 为 `36092809df8246ff4395847e599217d761309d54b67244e0b84e9f4a74a689b6`，API 测试为 `18f596f51731cda0168a130982b81c300aee17c212ac78b746c6a928bf33f491`。完整旧 DEV manifest 和 QA1 输出只读保留，不冒充本轮运行。
- QA2 自有证据根为 `/private/tmp/arch-be010-r1-a0-pxmh71r0/verification-qa2/`。从正式树独立冻结 766 个公开输入并创建 `source/{backend,frontend-js}`；input-manifest SHA256：`ded15b5fa18979ec5b2d4833af266d4afed876984ee1abe41955325619b0c0d4`；entry→QA2 verification.diff：`4edd4bb653b40775ae426ae1ff4530a8751fb92bde25354fdf763360d7502f84`。最终 49 个 backend 实现文件与实际验证副本及正式树逐字节一致，766 项验证输入副本无漂移。

首次 `file_audit.py` **exit1** 是共享 `CODE_INDEX.md` 在冻结后发生整文件 hash 漂移：原 handoff 为 `f063a54b864dd7480e25ddd284822052705e1811f769c29c510835e6f7effa99`，当前为 `95e9407cf1adc13bed24c6afdd3a9e709f9a2d446156f922789bc3d627e9aff5`。没有掩盖该差异或改写原 manifest。独立重建冻结索引并逐行比较，差异严格只有 SMA 的 `src/console/uiPreferences.ts` 与 `tests/cu-integration.test.mjs` 两条索引，BE010 整段原字节保持，段 SHA256 为 `7182ab4e92089e645e48ed312bc14fabcce25cb28ba217a1cbdef931b1422620`。

功能/范围归属依据为 [SMA PLAN](../../automation-world/semantic-mapping-agent/PLAN.md) 的 SMA-003 实施中行、[已批准 SMA-003 r1 allowlist](../../automation-world/semantic-mapping-agent/plans/SMA-003-cu-integration/spec.md) 的 console helper/tests/根索引最小同步，以及 [SMA README](../../automation-world/semantic-mapping-agent/README.md) 的 CU 主题/语言说明；两文件实际存在。协调者也确认该功能范围归并行 SMA 工作流；**具体写入进程作者未独立确认**。QA 未修改/回退 SMA 或根索引，未把 SMA 软件纳入本轮验收。`file-audit-initial-report.json`、冻结/当前索引与 `concurrent-code-index.diff` 保留；随后严格验证“仅这两行外部增量 + BE010 段不变”的 scoped 审计 exit0，原始整文件漂移仍在报告中列出。此文档并行变化不改变已验证 backend 行为，无须重跑产品测试。

## 环境、命令与本轮真实结果

2026-11-04，macOS；正式 `backend/.venv` 的 CPython 3.13.3、FastAPI 0.135.1、Starlette 0.52.1、Pydantic 2.12.5、SQLAlchemy 2.0.48、pytest 9.0.2、httpx 0.28.1。复用经审阅的 QA1 公开探针方法，但脚手架/guard/产物均在 QA2 目录重新建立，输入由 QA2 冻结，不复用 DEV 测试结果充当 QA。

主入口 `python3 /private/tmp/arch-be010-r1-a0-pxmh71r0/verification-qa2/run.py <tag> ...` 的实际项目 argv 为自有 wrapper 下 `uv run --offline --frozen --no-sync python ...`，精确 argv/cwd/exit/wall-time 记录在 `<tag>-command.json`。公开副本不含真实 dotenv/运行资源；只注入合成占位 process env、TZ=UTC，未安装或同步依赖。导入应用前部署 sitecustomize/audit guard，拒绝 socket connect/connect_ex/bind/listen、sqlite3、SQLAlchemy 与已安装 DBAPI 连接；独立核对关键函数确来自 sitecustomize，**观测 guard 事件为0**。ASGI 只走内存，未运行 lifespan、监听、真实 HTTP、浏览器、PLC、数据库（含 SQLite/:memory:）、Alembic current 或任何 Docker 命令。Git 仅只读。

| QA2 命令 / tag | 精确验证面 | 真实结果 |
| --- | --- | --- |
| `run.py a0 tests/test_business_integration_contract.py tests/test_business_integration_api.py tests/test_business_integration_migration.py tests/test_business_integration_compatibility.py tests/test_module_contract.py` | 五个完整相关文件；`-q -m no_db -p no:cacheprovider --basetemp verification-qa2/pytest-a0` | **exit0；220 passed / pytest 251.14s**（wrapper wall 257.93s）。不与其他轮次相加。 |
| `run.py independent --script independent_probe.py` | 从冻结 spec 独立解析八份 JSON，正常 composition/真实 Settings、原始 ASGI、DTO/数值/时间/双摘要及 native ASGI yield send 顺序 | **exit0；437 checks，0失败**。原 QA1 两个 F001 失败断言现均通过；同步/异步、request/function scope 的退出失败不提前发成功。 |
| `run.py boundary --script boundary_matrix.py` | 新独立八路×11情况：128/129、引用未知字段/错误类型、sourceId/eventId 129字符、重复/空/null引用、65537字节/深度13；逐项断言 HTTP、完整错误壳及 application/json | **exit0；88 requests，0失败**。八个129项请求仅8931–9539 bytes，均413；八个128项均503。其余普通格式422、体积/深度413均保持。 |
| `run.py surface --script inspect_surface.py` | preflight、app/common/core/database/projection/scripts/tests 与 main/run/build compileall、正常 composition/OpenAPI、显式全模型、四表静态 MySQL DDL/FK | **exit0**；428 refs 全解析，8条 typed 输入路径；即时metadata63、显式全量68；四表所引列均有已声明 unique。DDL SHA256 `1405abf947a207c22dd2e666c42af96d791d79f70b14604df2d1ecf9aed65ffd`，未执行DDL。 |
| `run.py log-and-guard --script log_and_guard_probe.py` | guard 实际归属、独立新路由503 JSON Lines及合成敏感标记 | **exit0**；受控 producer/event/resource/equipment/errorCode 存在，完整body、Authorization、source/mapping私有标记未泄漏。 |
| `python3 verification-qa2/metadata_audit.py` | spec/tasks 12个必要字段，含 tasks 精确 writer | **exit0；12项通过**，Allowed Writers 为 Development。 |
| `python3 verification-qa2/file_audit.py` | 正式源码/副本、公共新文件、新文件头/链接/空白、三env旧完整前缀、六旧迁移与 `git diff --check -- <50实现文件> <tasks>` | 首次 **exit1** 的共享索引漂移如上；归属和精确两行差异核定后 scoped 审计 **exit0**。无未知公共新文件、backend漂移、断链、缺头部、尾空白或guard事件。 |

QA2 未重跑未变的旧14整文件/entry四节点，更未无依据重复历史483/604或默认全套。独立对照其14文件 hash、QA1 766项输入和实际旧输出：相对 QA1 只有 backend PLAN pair、http.py、API新增测试四项不同；旧业务实现、旧14文件断言、三env与六迁移不变。`history-reuse-report.json` SHA256 为 `7d64f76e69ceec520140068b4b9bec3a9a592f3a49e0acd279bafbfe38bfbd95`。

因此保留的真实 QA1 结果仍是：**related exit1，362 passed /4 failed /164.16s；entry exit1，3 failed /1 passed /0.80s**，不是 QA2 重跑，也不是相关 suite 全绿。其中 mapping_compatibility 固定72项在entry通过、被本轮新增12个关闭键触发84≠72，仍是本任务新快照差异；其余三项entry已有。三env旧72项完整原文前缀SHA和 BE010-A0 的84项/68表/no-migration profile 本轮220组再次通过；没有修改/弱化/skip/xfail旧断言，不将四项整体称为历史失败。

## Finding 关闭与 AC 当前审计

| Finding | QA2 裁定及证据 |
| --- | --- |
| F-QA1-001 | **closed**。公共 raw parser 仅对顶层 sourceRefs 为 list 且 len>128 抛既有413 payload_too_large。八路128→503/not_ready；129且body<64KiB→HTTP/code413、模块 integration_payload_too_large、data=null；普通标识超长、引用类型/unknown/duplicate仍422。完整A0、437探针与88矩阵通过。 |
| F-QA1-002 | **closed**。tasks 第5行精确 `Allowed Writers: Development`；独立12字段 metadata审计通过。未改变Owner审批/最终验收权。 |

| AC | 当前 A0 已证 / 未证边界 |
| --- | --- |
| AC01 | 八路method/path、owner-local typed输入/回执声明和spec八JSON通过；实际API→业务DB读回/回执引用仍未实现。 |
| AC02 | F001已关闭；严格raw/重复/未知/snake/null/bool/string/数值域/0/UTF8/nonfinite/Decimal及413/415/422边界通过；真实NULL/精度持久化待B。 |
| AC03 | 双摘要、独立向量、存在集合、来源/mapping/身份分离、offset等瞬间通过；真实unique/409优先级/持久重放待接线与B。 |
| AC04 | 输入缺测/数值/过程范围通过，无任意SQL接线；不可变/补NULL/原子409/补后完整行规则待业务实现。 |
| AC05 | 生产/过程输入规则通过；新生命周期/水位/历史事件/父ACK/人工0两提交顺序待接线与B。 |
| AC06 | 可失败yield完整退出先于唯一500/503发送、DEBUG脱敏通过；真实RR/current-read/flush/commit/unknown/丢响应仍未证。 |
| AC07 | 正常composition有效scope无凭据仍503、关闭/空/越界403、伪profile不可绕过，旧八POST401、disabled重组新旧404通过，无DB依赖；所有旧GET/PUT/DELETE全链未重跑。 |
| AC08 | 上海毫秒/必要事实精度/注入DB时钟纯函数及UTC宿主稳定值通过；T1提案仍待Owner确认，G-T未解除，真实旧列时区/迁移/采用未证。 |
| AC09 | 最小receipt/事件Model及纯重放语义可声明，无raw FK/CASCADE/自动TTL；没有实际永久业务、持久ACK或raw到期后恢复证明。 |
| AC10 | 全模型68、四表静态DDL/unique/FK/CHECK及六旧migration字节保护通过；精确Alembic后继未批准，Model不等于已迁移Schema，升级/回退真实验证待另批。 |
| AC11 | 有限公开符号/准入正负例、模块StrEnum、原样键、局部HTTP和日志脱敏通过；provider机器输出合同/真实业务ACK仍未完成。 |
| AC12 | F002已关闭，正式backend输入与独立运行一致；并行共享索引漂移和旧suite失败已如实披露；QA1历史保留，整体与Owner验收继续分gate。 |

## 保留的 provider / T1 / 运行 gate

本轮 `provider-limit-report.json` 再次确认 QA1 的准备态限制：Decimal输入OpenAPI仍为 number|string；八路200 schema为 `{}`、422为HTTPValidationError，实际403/413/415/422/503模块壳未完整按operation建模。后续接通/发布provider前须补齐只收JSON number的机器schema、成功信封/八结果DTO、模块错误壳与真实HTTP状态并验证样例一致；当前不冒充完整provider或业务ACK。

T1逐列提案没有改为已批准/已执行。独立复核旧source-time/UTC_TIMESTAMP、Projection collected_at及人工Python now()/DB func.now()关键来源，与QA1审计一致；源码约定不能证明真实历史每行时区。unknown不得同列混写Shanghai，旧UTC wire/旧fingerprint及actor回执须保持；来源键、父/设备、receipt和生产水位成组迁移，人工非NULL含0和已知时区pair优先，DATE/耗时/过程分钟不机械平移。精确migration文件/Revision/down_revision仍未获批，本轮未创建或执行。

整体解除条件仍依次为：Owner先确认有界T1兼容/分类/权威writer停切与保留数据回退原则；PM据实际源码head冻结时区整改与精确迁移允许面并获得相应批准；另批具体数据库/运行目标与动作后取得真实时间专项/采用回退证据以解除G-T；再按Owner批准进入A1→A2→A3，完成源码A后另批完整隔离MySQL B。**G-T时间专项是前置，接线后的完整新业务B是后置**，不能循环互代。整体独立QA及Human Owner最终验收仍待真实发生；发布/部署/现场/监听/PLC另批。

## 资源与最终 handoff

本轮仓库仅写本 checklist。自有 `verification-qa2/` 保存公开source、bundle-before、guard/wrapper/helpers、显式pytest-a0/合成fixture、pycache/uv-cache/logs、OpenAPI/静态DDL、输入/历史/差异/命令/结果报告及并行索引审计。所有本轮检查进程均已退出；无数据库、监听、容器、后台任务、Git分支/worktree或真实配置资源。未触碰默认pytest清理窗口，未覆盖QA1/DEV证据，未新开root唯一notifier或发信。

这些临时资源当前仍供Owner审阅、后续G-T/Development/fresh Verification比对，QA不执行回收；由协调者在相应Owner gate后确认无运行、后续及证据依赖，再按归属清理。关键结果、精确输入hash、finding关闭依据、历史失败及限制均已持久化本文件，不以临时路径作为唯一证据。

交接前 `python3 verification-qa2/final_audit.py` exit0：当前bundle元数据/本文件链接与空白、QA1正文原样保留、spec/tasks hash、49 backend文件/766验证副本/715保护文件及既有证据hash均符合；五个runtime命令exit均0、guard事件0，checklist的只读 `git diff --check` 通过。完整最终checklist SHA由该临时报告与主协调handoff固定，避免在本文件自引用。

**QA2至此停止写入并交Human Owner：A0 qa_passed；整体 qa_blocked；T1提案确认与A0/整体最终验收均 pending。** 当前没有需返工的A0实现finding；后续门槛不因本子阶段通过自动获得实施或运行授权。主协调可据此机械同步索引，不能把整体写为qa_passed或owner_accepted。
