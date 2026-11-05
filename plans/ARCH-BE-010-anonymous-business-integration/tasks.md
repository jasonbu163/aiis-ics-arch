Task ID: ARCH-BE-010
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: 已记录root实际资源清理收据；实施源码冻结2532不变；独立QA资源核验与Human Owner最终验收归各自角色
Updated: 2026-11-04

# r2 B Development资源收尾记录

本次仅Development事实追加，不执行数据库、Docker、测试、秘密恢复或其他角色文档/六索引写入。以下基于root提供的具体清理收据并核对文件SHA；不冒充本DEV执行清理、独立QA核验或Human Owner验收。原完整A/r1/B事实（包括当时待清理/待QA状态和全部失败史）逐字节保留于后缀，当前资源状态以本节为准。

实际执行者为root lifecycle coordinator，依据Owner已明确批准的两轮隔离B提案及专用资源清理，于`2026-11-04T22:10:52.665327+08:00`完成：按创建ID/标签归属清除Dev/QA2两个专用容器、2个卷、2个网络并核验不存在，8个专用schema随所属卷移除。收据记录两项cleanup工具exit0、清理过程DB连接0、未触现有资源/现有数据库/真实历史数据/DAA。不是本DEV运行DB或Docker后的自行判断。

root同时删除27份inventory列明的合成口令/key/操作配置并记录全部不存在，未读出/打印正文；包括本DEV的`/private/tmp/arch-be010-r2-b-dev/tool-time.private-env`及9份adopted/invalid配置。原inventory与旧路径作为清理前归属证据保留，不表示秘密文件仍可使用，不重建或恢复它们。无本DEV活动runner、事务、连接或监听。

| root收据/报告 | SHA256 |
| --- | --- |
| `/private/tmp/arch-be009-r1-be010-r2-b-my8s9bnu/cleanup-receipt.json` | `23048893ca4c71a6fc7ca76d0e9a466371c41e6fda15880458f8515cac5e41cb` |
| `/private/tmp/arch-be009-r1-be010-r2-b-my8s9bnu/owned-resource-cleanup.json` | `2c7df8944739811cadc1ac1286f4807b33e9b516140eb4b70b7548c25b155d95` |
| `/private/tmp/arch-be009-r1-be010-r2-b-my8s9bnu/sensitive-cleanup.json` | `230ee3c391b98001b87cdbf3e437903d7cd0c025b0fbdc8559ead7d3930e9b0a` |

本DEV六个实施文件已只读逐hash核对，仍为共同候选`2532d8423c73f0e9c0a7ac42d616014b2ca09419588cd07a0218bd4ce080cafb`，未改产品或正式测试源码。清理前完整tasks SHA为`d8daa5b61f4c919f67dfeeca4dd8520deb87d05bd6e084a5ccad3dc36b945224`，其完整字节在下方保留；本次新tasks SHA由外部handoff固定。

脱敏命令/log/report、公开源码冻结副本、before/diff及必要行/ACK证明仍留在两项Dev/QA的`/private/tmp/arch-be009-r1-b-dev`、`/private/tmp/arch-be010-r2-b-dev`、`/private/tmp/arch-be009-r1-b-qa`、`/private/tmp/arch-be010-r2-b-qa`及共同B根目录，供QA收尾与Owner最终审核。生成的操作秘密已移除；这些证据保留不代表专用运行资源仍在。Owner最终验收后，root再确认无证据、运行或后续任务依赖，并先把必要结论持久化至各自tasks/checklist，再按归属回收相应副本/缓存。其他任务或A历史资源未在本次B清理中回收，不擅自扩大。

后续由Verification独立核验收据/不存在事实并更新自己的checklist；Human Owner最终接受、生产历史实际采用及发布部署仍是独立gate。本Development资源记录不授予上述判定。

---

# 清理前完整A/r1/B历史（以下字节原样保留）

Task ID: ARCH-BE-010
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: B Development隔离轮及B发现修复完成；交fresh Verification独立QA第二轮（新33380）；非QA verdict/Human Owner验收
Updated: 2026-11-04

# r2 B Development handoff

## 批准、交付与输入

Human Owner逐字批准：

> 批准 B 操作提案，按 STD 完成 ARCH-BE-009 r1 和 ARCH-BE-010 r2 的两轮隔离 MySQL 8.4.6 验证及专用资源清理。现有数据库、真实历史数据和 DAA 不动。

精确提案为`/private/tmp/arch-be009-r1-be010-r2-a-y34l21yd/B-operation-proposal.md`。本DEV只完成Development轮，不将fresh Verification另一个新QA容器的第二轮预记通过。A approved spec SHA仍`955877e96b4695b0c00aa81ef6e862dd6a642e82157edd05d5aeef8c175add5f`，spec/checklist均未写；A QA2 checklist仍`2e42a63552d4d377a79b397f2f74974f379784b28cdf0742cb580dedda1b5af1`。原A/r1及B准备全文保留于后缀，旧“未授权/未运行DB”的历史不改写。

正式工作树`/Users/jason/Desktop/DreamCode/aiis-ics-arch`、只读HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`。A联合冻结SHA `46b27579731898cbd685b69664894b79a8fedf5f75eb03e5f61a9ac61c08c13d`是157实施+6角色的进入基线，B确有13个联合实施文件增量（本DEV6、BE0097），不能把A摘要单独冒称B当前源码。root现已固定157产品+2spec候选`joint-B-candidate.json` SHA `2532d8423c73f0e9c0a7ac42d616014b2ca09419588cd07a0218bd4ce080cafb`，本DEV6文件与候选逐hash不变。晚轮SOURCE_REVISION_ACK绑定该B候选；之前明确使用A基线+B delta引用，后续runner还逐次保存完整公开backend实际runtime-source清单/摘要，记录实际验证副本身份，不倒填其旧argv/env。

继续实际Development及同r2原allowlist；相关技能/角色/workflow承接A，复读提案/当前bundle/最近规则与实际实现。不写六索引、spec/checklist/BE009实现/真实env、依赖、Git。BE009独占Dev资源创建及facts/schema库；本DEV收到其0a2/71私有移交后只操作joint/time，所有资源最终由root统一清理，本DEV没有Docker/容器/卷/网络删除动作。

## B发现的两个产品问题与有限修复

1. **B-DEV-001**：真实MySQL新Performance的4个SQL null()观测默认列在flush后expired，MySQL无INSERT RETURNING；Service getattr触发MissingGreenlet而500。原red/debug保留。仅performance CRUD.add_performance在flush后显式`await db.refresh(row,with_for_update=True)`，不补0、不改global expire、不隐式lazyload，保持原锁与一次commit。正式直接回归与真实首写/全列/生命周期已通过。
2. **B-DEV-002**：MySQL FLOAT文本协议显示丢位，0.1读成Python double0.1，0.123456789→0.123457、123456.789→123457、最小/最大也丢位；直接Decimal.from_float显示值误拒合法DTO。重新binary32量化仍4/6不精确（含拒绝），所以**没有保留仅重新量化方案**。仅equipment/monitor固定CRUD列投影`CAST(col AS DOUBLE)`读真实物理binary32；对应Service用投影值做已存在冲突/新写复核，不改绑定ORM值、FLOAT量化/容差/两摘要或DECIMAL语义。实际发出SQL的CAST已捕获，正负0.1/长尾/大数/最小非零/最大两owner实际48请求及物理值精确对照通过。它是新业务持久读回复核问题，与QA1已关闭的r1 A0精确DTO边界finding不同，原关闭史不丢失。

本次正式树只有下列5产品+1正式test（当前SHA）：

| 文件 | B SHA256 |
| --- | --- |
| `backend/app/performance/crud/async_integration.py` | `ad7bad3e6aedbaabe9ff2634915931391938f9dabd83fdfdf06adb4cd2fe6563` |
| `backend/app/equipment/crud/async_integration.py` | `455196f4135d42461d14e59b195485f69cf14146916fe96f6ac33e528b7f9f7a` |
| `backend/app/equipment/services/async_integration.py` | `83241e43ba070eaf6bfdee6add2b68758a387ccea5e71421312a39fcc5d29e4c` |
| `backend/app/monitor/crud/async_integration.py` | `2610eec71be2599e22298566c7a89d34ceebea231df0a2761494cb83c39efaa6` |
| `backend/app/monitor/services/async_integration.py` | `ecf50d99d3c6233f1bc86a8755c08c152fa557ebaa25d73aec9f03575948e8e2` |
| `backend/tests/test_business_integration_service.py` | `2dadb9f718db24861f5acfd45b34be5f97974f4a25e7789be9595f7d52fe3dec` |

无新公共Core符号/表/列/依赖/新文件；CODE_INDEX无结构增量需改。BE0097个source/test修复由其独占交付，公开副本按其精确清单同步，不覆盖本DEV修改；详见final-product-delta.json。旧BE006 Service源码未改，实际旧八HTTP/重放/GET/Projection兼容在时间轮完成。

## 实际B覆盖与串行目标

MySQL8.4.6，Dev127.0.0.1:33379、专用非root be009_be010_dev，只接arch_be010_r2_dev_joint/arch_be010_r2_dev_time；默认+08/RR，真实serverUuid/schema/revision/UTC DB clock由每事务probe核验。PRIMARY使用never_connect_primary哨兵，guard拒绝它/root/其他schema/endpoint、SQLite、listener/真实dotenv；guard在应用导入前安装。uv始终offline/frozen/no-sync，复用正式.venv，不安装依赖。HTTP为真实composition/Service/CRUD/MySQL上的ASGITransport，未启动TCP API监听，不以DB替身/请求回显/skip计B通过。

- **阶段/结构**：BE009先真实0a2/71移交；joint显式1b3/75。为覆盖带旧行路线，time从未采用空71显式退f6，真实旧8POST植13表/41列及user/Projection行后保存全64表结构、行ID/值/精度，再0a2→1b3逐项守恒（并不声称64表都植行）。新4空允许退0a2后恢复1b3；joint非空downgrade按预期exit1在DDL前拒绝。最终四新表实际columns/null/type/Unique/CHECK/FK与Model核对；继承默认collation不冒充源显式差异，明确binary collation仍严格比。
- **schema-only**：joint1b3且本DEV进程/连接关闭后，明确暂交BE009 owner，真实plan/apply及三路恢复后归还。当前F7仅`sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`，原epoch/adoption/source binding/proof/水位保持由其joint-schema-only-proof.json记录；旧F7不作为目标。本DEV不冒认自己执行了BE009命令或其独立QA。
- **时间/旧行为**：13/41每个列（含NULL）按已知HTTP UTC/system/manual上海等固定来源一次转换，ID/unique/FK/值/原fingerprint与JSON result/DATE守恒；真实旧8actor请求重放与8GET完整data一致、Projection实际sync Session无内部commit/保留原日期；人工0与manual pair保留。hostUTC/Shanghai和session+08/-07的16GET一致。错UUID、unknown、monitor不可分组mixed凭据真实ASGI503无副作用；实际反射13/41+4/16=17/57。另补真实17:30Z/同瞬间+05:30→上海次日01:30，new与旧JWT HTTP生产DATE均仅取上海次日，旧wire仍UTC。
- **时间负例的最终状态**：上述已知阶段验证后，明确追加一条来源unknown的合成legacy drive负例，三owner工具真实inspect/plan/verify对全41列只产candidate；equipment_drive.timestamp列unknown未解除、verify无写/摘要守恒。因此**当前time负例目标不具备整体采用资格**，不能把先前已知夹具阶段当作生产G-T或当前未知已处置。无生产历史调查/转换/实际采用，所有文件只是隔离B合成runtime凭据/报告fixture，不冒充生产批准。
- **八业务**：8类完整字段/实际列逐项读回、NULL省略/0/JSON number/Numeric/FLOAT；首写、同身份完整ACK重放、异内容event冲突、异身份同业务、温控/33指标存在集不可变。drive/参数/三过程补NULL、补后范围/任一冲突整次回滚（无补缺部分提交）；不同业务键分别存储。
- **生产/父子**：主行/前卷/持久水位/事件/receipt同事务，零活跃退出和unknown仍有水位；创建/更新/退出/unknown/重激活、较小ID inactive目标与较大ID active的实际顺序、历史成功先于stale、同刻冲突、父missing/mismatch/可靠in_production事件、已结束父合法晚到子；真实JWT人工0两提交顺序以及manual/reported/observed pair优先。
- **竞争/错误**：8路独立Session同身份首竞争，允许真实deadlock/锁竞争503后用原身份恢复；同/异身份异内容及首次水位竞争、真实RR旧快照后的current-read。真实MySQL命名1062一次恢复成功/3次耗尽、非命名1062不重试，真实session1秒锁超时不伪duplicate。每次先rollback，新事务probe/current-read；一次请求至多一次commit。
- **故障**：3owner×6实际DB事务/flush/commit前后/rollback/close组合注入+真实ASGI发送丢ACK，保留原事件恢复；这些注入不冒充真实连接中断。随后另做6真实专用own-connection KILL，ID取本请求已核schema/同非root账号的连接，用另一个同target连接终止：commit前native断线→503unknown/无部分提交并原身份恢复；driver commit已确认后终止→可靠200且原身份duplicate，不强求503、不加第二业务commit。
- **事实清理独立**：全部已接受8资源合法plc_fact ref实际对应BE009 joint原sample/point，私有sidecar另核part1/contentDigest/sourceSha（不向公开ref加未批准字段/无raw FK）。清理前68非facts表485行全列/精确FLOAT与完整ACK/sourceRefs/mapping/父快照。明确无活动事务后交BE009 owner，仅原1批raw/latest/cycle/sample/batch120天proof真实清空并按规则推进floor，保留binding/epoch/F7；交还后120条原身份业务ACK完全恢复，68表485行完全相等，5类facts/proof均0。之后断线/跨午夜是**独立后续新增fixture**，不混作前述守恒前后比较。

## 正式A回归、运行命令与失败史

受B修复影响的正式整文件：test_business_integration_service.py、contract.py、provider.py、migration.py、compatibility.py；最终**161 passed/81.30s，exit0**，严格noDB导入前guard事件0。此前Service30、35直接轮分别记录；A原335/87和QA1四finding关闭按原QA2证据保留，未拿不同轮次相加，也未无依据重跑335/API巨矩阵。三条旧冻结schema断言仍保留：mapping六迁移/head在entry原通过，获批后继触发当前八迁移；温控五迁移/e4两条entry即失败，未删/弱化/skip/xfail。

实际入口：`python3 /private/tmp/arch-be010-r2-b-dev/run.py <tag> <精确schema> ...`，内部`uv run --offline --frozen --no-sync [python <私有script> <mode> | alembic upgrade/downgrade <精确revision>]`；不调用head/create_all/stamp。noDB入口run_no_db.py使用合成无秘密env、独立全禁DB guard及pytest -q -m no_db -p no:cacheprovider --basetemp。两原tests_mysql入口仍是A期骨架，不用其存在宣称完整B；本轮真正完整矩阵来自以下已运行private harness，均通过相同工具链/实际产品/真实DB/ASGI。完整argv/cwd/target/exit/wall/runtime-source/guard摘要在每tag-command.json，完整输出在tag.log；秘密不放argv/公共文档。

BE010_MYSQL_EXECUTION_ACK=ARCH-BE-010-r2-B、SCHEMA_ACK、ENDPOINT_ACK、RUN_ID和SOURCE_REVISION_ACK均显式；mock/Projection runner/bootstrap全false、TESTING=True。晚轮ACK绑定B2532及另存实际runtime-source摘要，前轮基线+delta/占位引用如实保留。所有配置通过process env及显式私有工具文件，不读取真实.env。

以下是各轮真实结果；exit1保留其真实含义，不因后轮绿而抹除。纯helper首审曾遗漏BE009 tests_mysql路径、noDB wrapper尚未创建、静态未初始化MySQL dialect等均为测试准备错误，已纠正且不改产品/冻结断言。工具曾返回aborted-before-dispatch但实际extra完整报告/ACK产生；原exit返回不可复核，误以未运行重试同身份且时间变化后正确409，相关原报告单独保留；只以唯一m10完整exit0形成最终明确证明。

| tag | exit / wall秒 | 实际意义 |
| --- | --- | --- |
| `actual-own-connection-kill` | 0 / 19.05 | 后续独立6真实own-connection断线：commit前503unknown/无部分提交，确认后200；均原身份恢复 |
| `affected-A-final` | 0 / 89.17 | 五整文件161 passed/81.30s；guard0 |
| `business-constraints-races-pairs` | 1 / 20.0 | 真实1062/timeout/3竞争已绿；私有manual fixture只填override未填有效值，被保留旧值规则正确挡住误断言 |
| `business-constraints-races-pairs-final` | 1 / 18.59 | 原tool返回丢失但完整26报告/ACK产生；误重试同m9时载荷时间变，正确409；本exit1日志不伪称全绿 |
| `business-extra-confirmed-m10` | 0 / 19.31 | 新唯一m10：实际1062一次成功/3耗尽/未知key不重试、锁超时、异内容首竞争、JWT manual0/pair优先、16新列全部绿 |
| `business-faults-final` | 0 / 18.85 | 3owner×6真实事务/退出注入+丢HTTP ACK恢复全部绿 |
| `business-first-debug` | 1 / 19.42 | MissingGreenlet定位red |
| `business-matrix-1` | 1 / 23.46 | 真实生产500 red |
| `business-matrix-2` | 1 / 19.79 | refresh修复后首4资源绿；私有父URL写死101导致404 |
| `business-matrix-3` | 1 / 18.96 | 私有actor username过50字符，未进行业务；后改hash短名 |
| `business-matrix-4` | 1 / 20.78 | 八路/NULL/生命周期/manual0绿；实际0.1 FLOAT读回422 red |
| `business-matrix-5` | 1 / 21.81 | CAST两owner六向量等全绿；私有不同身份竞争未允许503而止 |
| `business-matrix-6` | 1 / 22.58 | 八路/补NULL/生命周期/manual0/48 FLOAT请求/八路竞争/RR通过；私有production恢复只预期created而实际合法updated |
| `business-retained-after-real-cleanup` | 0 / 20.22 | 清理后120原身份ACK全恢复，同receipt/完整结果/source/mapping/父 |
| `cross-midnight-and-live-schema` | 1 / 18.62 | 真实跨午夜双通道已绿；私有反射把DB继承collation当显式差异而止 |
| `cross-midnight-live-schema-final` | 0 / 18.57 | new/旧JWT+05:30实际17:30Z跨上海次日/DATE一次转换；四表真实列/null/UQ/CHECK/FK全部对齐 |
| `float-wire-real` | 1 / 1.25 | 诊断遇FLOAT显示丢位被helper拒绝而止；无生产修复采用该方案 |
| `float-wire-real-complete` | 0 / 1.2 | 6组显示值/重新量化/DOUBLE实际对照；DOUBLE全精确 |
| `joint-nonempty-downgrade-refused` | 1 / 6.2 | 预期exit1：nonempty prohibit downgrade；其后1b3/75与行仍在 |
| `joint-schema75` | 0 / 6.51 | MySQL8.4.6/+08/RR；原64空基线与新4空 |
| `joint-upgrade-1b3-authorized` | 0 / 6.6 | 真实0a2→1b3成功；新4/75 |
| `joint-upgrade-1b3` | 1 / 6.52 | exit1：sandbox socket EPERM，未连/未SQL；获批escalated重试 |
| `new-row-refresh` | 0 / 9.56 | 正式Service30通过，初期未建offline wrapper时FileNotFound在项目import前；后修helper |
| `physical-float-direct` | 1 / 10.44 | 32pass/3fail：未初始化server version的静态dialect跳CAST；改为获批MySQL8.4.6方言 |
| `physical-float-direct84` | 0 / 9.34 | 正式Service35通过，包含显式await refresh/实际物理投影边界 |
| `retention-after-cleanup-and-ack` | 0 / 1.89 | 68表485行全相同；raw/latest/cycle/sample/batch proof全0 |
| `retention-before-cleanup` | 0 / 1.87 | 68非facts表485行精确FLOAT/全行冻结，8资源均关联真实sample/part/digest |
| `time-0a2-preserved64` | 0 / 2.84 | 旧64结构/行ID/值/精度逐项相同 |
| `time-convert-verify` | 0 / 17.25 | 13/41合成已知来源一次转换、8旧重放/8完整GET、Projection、ID/DATE/JSON/人工0守恒 |
| `time-empty-downgrade-f6` | 0 / 9.72 | 空未采用71显式退f6，供带旧行路线 |
| `time-empty-four-downgrade-0a2` | 0 / 7.4 | 新4空允许显式退0a2，旧行保留 |
| `time-f6-seed-old` | 0 / 21.73 | f6真实旧8POST/8GET+Projection，13/41及全64快照；首次结束未dispose应用全局engine的警告由helper补dispose，非数据失败 |
| `time-readonly-cli-negative` | 0 / 12.53 | 明确unknown负例后3owner真实inspect/plan/verify；12+24+5=41列，只candidate/unknown拒绝，不采用当前混合目标 |
| `time-reupgrade-1b3` | 0 / 6.5 | 恢复1b3后同旧64基线 |
| `time-seeded-upgrade-0a2` | 0 / 7.34 | 带合成旧行f6→0a2成功 |
| `time-seeded-upgrade-1b3` | 0 / 7.33 | 带旧行0a2→1b3成功 |
| `time-zones-rejections-profile` | 0 / 37.27 | host UTC/Shanghai及session+08/-07的16GET一致；错UUID/unknown/mixed三拒绝无副作用；反射17/57 |

## 精确清单、资源与下一gate

自有证据根`/private/tmp/arch-be010-r2-b-dev/`：公开source、bundle-before/A及B前置原文、guard/no-db-guard/offline-bin、所有private harness/runner/源码runtime清单、各轮command/log/report、显式basetemp/cache/pycache/logs、旧64/68表全行/关联/永久ACK、原失败与歧义dispatch报告，供fresh QA独立消费。所有本DEVrunner已经退出、Engine disposed，无活动DB事务/连接/监听/后台任务；未创建Git branch/worktree/子Agent/notifier/邮件。root负责最终Dev/QA专用容器/卷/网络/四库和私有口令配置回收，本DEV未执行资源删除；现有资源/真实DB/历史/DAA不动。保留必要证据直到QA/Owner gate且root确认无依赖，再按归属收尾。

敏感材料仅提供路径/用途，详见sensitive-file-inventory.json：BE009-owned `/private/tmp/arch-be009-r1-b-dev/connection.json`（Dev DB/root/cursor材料，未复制值到文档）；本DEV `/private/tmp/arch-be010-r2-b-dev/tool-time.private-env`（chmod600非root工具口令）；本目录各`*-joint-adoption.json`、`*-time-adoption.json`和`*-time-invalid.json`（合成目标采用/拒绝fixture）。完整扫描仅tool-time.private-env含非root口令；root口令/cursor key未泄漏到本DEV副本/日志。公共源码副本不含真实.env；private输出/日志不展开口令。原A/QA/BE009及root资源非本DEV回收对象。

最终本任务100文件完整manifest SHA `b7246f62cd4b8e43648c40d07c6e89c84ddc36d45a6cad4f9cb415cdcfcb5387`，其路径集合与A末轮100相同，仅本6个hash覆盖上表；未变94项的持久完整表已在后缀A handoff，因此可完整重建，不只依赖tmp。与正式树/当前公开副本一致，313保护文件及旧6迁移、spec/本QA2文档无漂移，3env91项，git diff --check通过。BE0097项单列delta，不误归本DEV。root B2532候选是后续fresh QA统一输入；tasks自身hash由外部handoff固定。

证据总清单evidence-manifest.json SHA `3f001ffa0a5704b273e7f175a11fbf816a99c42bc3ca12ca8e2da2ad0cf9b20e`（167项，不含口令/采用文件正文或缓存）；完整命令/日志/公开fixture/script均可复核。

关键证据SHA：

| 文件 | SHA256 |
| --- | --- |
| `final-product-delta.json` | `695a02e9074d4287e82e5aa4df79000aa48c55e44e3719b6c4e388477d3ad54f` |
| `final-source-manifest.json` | `b7246f62cd4b8e43648c40d07c6e89c84ddc36d45a6cad4f9cb415cdcfcb5387` |
| `final-audit-report.json` | `ba6170e0014672d25ec3d61b89afffa6787693d8672b904f3aa9c44525f54d39` |
| `affected-A-final-command.json` | `0035323772b50f0f6b6afa86fa0fd8119c955aefbbd190904c554568b23b730b` |
| `affected-A-final.log` | `f3aa55f4d73f25c5b5055e8d9c445712b3dd20b40d3d811636982b0b775b5e01` |
| `business-matrix-6-partial-report.json` | `44dd204249075dcddf4ff2b15c86c13a2e5ddd40c3c5d81b85c39089dbf826b1` |
| `business-faults-final-report.json` | `5f73c7baca5fdac27ddaa12102da9bc27ff8f3c72dc23c3db90dfe23eee98a95` |
| `business-extra-report.json` | `6f26056e2f60a3835fa68e520f2f175a21869f19330112c753242a4ae110d580` |
| `float-wire-report.json` | `c73c34222a8aea179a2096fceb16e475a30ff84cd65a274d06ed9cce2c7219aa` |
| `mysql-float-sql.json` | `11c124091150bd715ccd238de1143470eb40c3aa9ab80b4fa602a856f31ca062` |
| `time-matrix-report.json` | `95e718e3d69835efe14972d6d30e7bf33efd336930e27222c4c763074b46931d` |
| `time-extra-report.json` | `c7fc9dc5bb948cf1a911d751fcbe1bafbcb74132b93c1b437142855064ce29e7` |
| `tool-matrix-report.json` | `edde8e6e0e8dfd786d028e904c0e966f658c112110ac3a195cadb07105ba8ccf` |
| `time-negative-fixture-final.json` | `2dbbe270ced1c23f7ff435e8b60d74ac44537945a29966f641540efb3f576d48` |
| `actual-fact-business-link.json` | `f29e718db5a6dc0ffb9f4487cee58aa29fdb48022441c269aaad53a49dcc2d8b` |
| `retention-conservation-report.json` | `c64c9a7f825b74e4e3320677dbe5e449e4b8b666b513592a5d371fb22a5543da` |
| `permanent-business-proof-before-disconnect.json` | `06051b4a2564c2904101bf571d3dd3dfa83e5098b87668447fc38cbae5e3781f` |
| `real-disconnect-report.json` | `d178e60e8f29f2ef909adc968a2c98ea76fed88ccd3fc5b9c9de9c29618d8d5b` |
| `cross-midnight-and-schema-report.json` | `e1ec0fb379a82e81ec9f16ca022de5520555af65566f995c2ad678f3222ef393` |
| `sensitive-file-inventory.json` | `9b5fbe916fa9a64d1e455e50864d09f5f9ff32f6e1446fb74e4c3d2abfef111b` |

**本DEV只给Developer self-check/handoff，不授予QA或Human Owner最终验收。** fresh Verification应在全新QA33380独立完成第二轮、消费产品修复和真实失败史；root统一清理仍待完成。整体生产G-T/真实历史采用、DAA/SMA/PLC、发布部署/Git写均不在本批准内。

---

# B准备及A/r1完整历史（以下字节原样保留）

Task ID: ARCH-BE-010
Revision: r2
Status: implementation_in_progress
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: 已获具体B提案两轮授权；Development准备中，待BE009移交joint/time后执行；A QA2与原历史保留
Updated: 2026-11-04

# r2 B Development 当前事实

Human Owner逐字批准：

> 批准 B 操作提案，按 STD 完成 ARCH-BE-009 r1 和 ARCH-BE-010 r2 的两轮隔离 MySQL 8.4.6 验证及专用资源清理。现有数据库、真实历史数据和 DAA 不动。

对应`/private/tmp/arch-be009-r1-be010-r2-a-y34l21yd/B-operation-proposal.md`内两轮隔离MySQL8.4.6、必要合成fixture/故障与专用资源清理；root转达精确资源/顺序后按同r2接续。原A spec/批准与QA1/QA2历史不改写；spec顶部A阶段限定是原时点事实，本段只记录新增具体操作批准，不代PM改spec。现有DB、真实历史、DAA/PLC/真实env不动。

联合A冻结`joint-source-final.json` SHA `46b27579731898cbd685b69664894b79a8fedf5f75eb03e5f61a9ac61c08c13d`，157实施+6角色文件均在B准备前逐hash匹配。当前F7仅`sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`。原A QA2 335聚焦+87旧直接调用方及4finding关闭由独立checklist负责，本DEV不重复授予QA通过。

BE009 B Development独占Dev资源初始化及facts/schema库；joint/time只到0a2/71后移交本DEV。root明确：收到其私有目标材料及交接声明后，本DEV可在joint/time执行1b3/75及获批B测试，无须再问Owner；此前本DEV仅准备，不连接/写DB或Docker。Dev endpoint只127.0.0.1:33379，schema只arch_be010_r2_dev_joint/arch_be010_r2_dev_time，非root；QA另新33380，禁止共用。BE009负责schema-only revalidation及facts清理fixture，双方按阶段交接，root最后统一清理资源，本DEV不删除。

准备计划：先核exact target/guard和64→71→75表差/原行守恒；时间库构13表41列UTC/上海/显式offset与unknown/mixed拒绝、旧JWT/API/Projection与DATE/人工0，连4新表16列核17/57；联合库逐8类真实ASGI/全JSON+逐列DB、补NULL/冲突原子性、生命周期/父/前卷/水位/晚到与人工0两提交顺序；独立Session竞争/RR快照/flush/commit/rollback/close/丢响应；facts实际清理前后永久业务/sourceRefs/mapping/ACK/父子恢复。缺fixture不skip，不以A替身或最小骨架计B通过。

已读两现有B入口：其A期骨架未包含上述完整矩阵，正在自有private harness补齐；现阶段尚无本DEV真实B结果。自有证据根`/private/tmp/arch-be010-r2-b-dev/`仅含公开副本、bundle-before与准备记录。后续精确argv/退出码/fixture及资源身份据实追加，不输出口令。

# 之前完整A Development事实（以下字节保留）

Task ID: ARCH-BE-010
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: r2 A QA1四项finding返工完成；交独立fresh-context Verification QA2；B与Human Owner final acceptance pending
Task Namespace: aiis-ics-arch
Classification: root
Capability: T1有限时间兼容、八类业务async接线与闭合provider源码
Owner: Backend Core 与 equipment、performance、monitor 公共业务模块
Updated: 2026-11-04

# r2 A rework-1 Development handoff

## 批准与冻结输入

本次只落实已批准ARCH-BE-010 r2 A同范围返工，无新Revision。Human Owner批准spec SHA `955877e96b4695b0c00aa81ef6e862dd6a642e82157edd05d5aeef8c175add5f`不变；获批原稿SHA `4e5b0c56b1aac066458c1f24a5037bbab53c18946cd70fd79d8ab747a9342b6e`。交付正式working tree `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD仍`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`；未Git写。完整读新QA1/bundle及适用实施输入后实施；延续backend-arch/六refs、backend-script-tooling、aiis与code-document-indexer。只写r2.6原允许面和本tasks；未写spec/checklist/六indices/BE009实现或共享README段。

fresh QA1结论是A qa_failed，不改写为已通过。checklist SHA `8435ec32c7a6ef4ca1156afc4a232ab5f232cce067788fc7b91ab991cc3652e9`仍不变。返工前95文件manifest SHA `9b526ab8170198c3c0b144d46b040c3142fffc6d911771c99789c662db00e1f1`及tasks SHA `1f2367df3f02faf02243d2fc3c94f8e8e1605ac2bccdc4b9e7afcc02ea2ee18f`为历史冻结证据；root另存qa1-history。下方整份该tasks字节原样保留，连同r1、r2初始、A2锁序和全部失败史。本顶部是当前事实，后缀中的旧状态/checklist/F7/95冻结陈述均是相应时点历史。

## 四项修复与直接调用方

- F-r2-QA1-001：IntegrationRoute在执行handler的内部捕获本owner既有503 COMMIT_UNKNOWN，完整function/request yield退出后仍优先保留该事实。清理RuntimeError/DBAPIError（含from None）及异常抑制不能改为500、普通unavailable或成功；正常commit后的cleanup仍按原500/503分类。仅新增私有helper，无新公开Core符号或失败字段。
- F-r2-QA1-002：三个真实Service事务处理先按committing阶段分相；BusinessException、ValueError、命名IntegrityError/其他异常在提交开始后均503 commit_unknown，无盲重提交，每请求最多一次commit尝试。未提交前业务拒绝/422及命名1062最多3次恢复保留。正式回归同时证明1062第三次成功、第三次耗尽、未知1062和1213不冒充竞争。
- F-r2-QA1-003：三owner float_number保留原float→IEEE754 binary32量化和两种摘要语义，误差比较改为Decimal精确整数比的交叉相乘；既有256位/指数1000预算界定整数规模，无任意context精度猜测。独立Fraction判据覆盖最小binary32两侧256有效数字的边界内/外、正负、zero、最大值、下溢和5种Decimal context。该缺陷在r1 A0已存在，并非r2新引入；实际FLOAT wire仅equipment drive.tv与monitor curve.lineSpeedSet，performance只核helper一致性。
- F-r2-QA1-004：performance静态只读legacy view按可靠record_source区分：external_observation first/lastObserved使用既有固定UTC组；reported start/end和旧mapping receipt/state也保持固定UTC。真实legacy观察列仍取legacyNaive，manual pair/audit/system各取原basis，合法混合profile继续支持。正式旧GET核完整data、纯DATE、人工0、createdAt及不修改绑定行，未增标签/列或强迫legacyNaive=UTC。

本次实际新增diff为8个产品文件与4个正式tests（列表下文）；公共接口、provider与schema无扩张；A2锁顺序及原三参apply/两参state/default bypass等在九整文件直接调用方回归内保持。

## DEV自检：先红后绿与真实边界

证据仅归自有`/private/tmp/arch-be010-r2-development/rework-1/`。原QA脚本/report/log未写；只复制到自有目录独立复现，红报告先保存red-reports再运行green。源码公开副本排除真实dotenv/.venv/运行数据；复用正式backend/.venv，process env仅合成占位、TZ=UTC，缓存/log/basetemp全部在自有tmp。导入前sitecustomize拒绝DBAPI、SQLAlchemy连接、sqlite含内存、socket connect/bind/listen及workspace真实dotenv；全程guard事件0，无数据库/Alembic执行、Docker、真实网络/listener/PLC、依赖安装或DAA操作。

所有项目行为命令使用`python3 /private/tmp/arch-be010-r2-development/rework-1/run.py <tag> ...`；实际内部argv为该目录offline-bin/uv下`run --offline --frozen --no-sync python ...`。完整argv/cwd/env说明/exit/wall在各`<tag>-command.json`，完整输出在`<tag>.log`。pytest统一`-q -m no_db -p no:cacheprovider --basetemp <本目录pytest-tag>`，未全局pytest/共享清库。APP_NAME沿用复制探针的合成标签，仅为输入占位，不赋予Development独立Verification身份。

独立红灯：red-http exit1，12检查中3控制通过/9失败；red-precision exit1，6helper错误接受；red-precision-http exit1，4请求错误503not_ready而非422且DB factory0；red-legacy exit1，first/lastObserved +8。源码修复后green-http12/12、green-precision6/6、green-precision-http4/4、green-legacy完整data、green-transaction12/12均exit0。

首个正式定向轮focused-regressions是真实exit1：49 passed、6 failed、214 deselected。6失败均为新测试额外把既有legacy Decimal wire字符串`"0"`断言为整数0；完整data一致断言已通过。只把测试该附加断言改为Decimal数值比较，未改旧wire实现/序列化。随后补完整异常/竞争参数并执行以下九整文件；不把首轮写成全绿，不将各轮数目相加。

**最终九文件：** `test_business_integration_contract.py`, `test_business_integration_api.py`, `test_business_integration_service.py`, `test_business_integration_storage.py`, `test_business_integration_provider.py`, `test_business_integration_migration.py`, `test_business_integration_compatibility.py`, `test_business_time_adoption.py`, `test_module_contract.py`。结果以full-r2真实日志为准：

```text
335 passed in 801.89s (0:13:21)
```

static exit0：整仓v1 preflight、compileall、正常composition 75 metadata、8路径/57闭合schema与已发布provider逐值一致、4表MySQL DDL静态编译。DDL SHA `62c97c58544bef68d490e49fbb147ddf39a56819908ac863ddc7db1e1de929c5`。audit exit0：100文件交付副本无漂移、313保护文件/旧6迁移不变、链接/新增空白/头部及git diff --check通过、三example各91项、guard0。f7-source仅调用纯源码fingerprint，无连接/SQL执行。

| tag | exit | wall秒 | command.json SHA256 | log SHA256 |
| --- | --- | --- | --- | --- |
| `red-http` | 1 | 89.79 | `8f452d10fa1c350c21908fd8d6a93f0432e46c9246b5f69f928926b99d691390` | `e6c09cb8e11c29407c140fefabf6f83784b54563957eea1ef120459599fcf766` |
| `red-precision` | 1 | 1.69 | `5f4a4807b88c6fbd8b6c659e6308526a061326bb7a246241d29f16c695964c92` | `5c9d3ee506dc25186936a18535b5f47868d2ea8469f1f2bf2dd8abcdb7991bb3` |
| `red-precision-http` | 1 | 17.3 | `cc694da8bfd3e6726c71bd742d6015667bf80deb1b4c947484f887d496f0c78a` | `7fc797c4acee93a94f370a4071aa606f0cb202a0b7937ca9dc674fb907a91086` |
| `red-legacy` | 1 | 7.85 | `0217e5962603ea59964791aaee61101f6f39048802f0238d96be79794184f571` | `5d1cb634c197c3b2f1c2c9fcdd4354368b082e55edae24e834c95c2d9cb40937` |
| `focused-regressions` | 1 | 289.61 | `293ab30da8e96a8484f5675c9f6c6c9da4d25ce6ef04d3d0f322713080c275c1` | `1e074a83ca509bc54a5c299e8a82ae904eb58fc20fdd5b97898a3a56ca3266a1` |
| `green-http` | 0 | 119.44 | `8a179a01f6ed5488c89b425fe295dfb889bd666e37559f73943f45adeffc4f86` | `56d2677455344eb9a327932a880a2d05031f8a84db1e21766f715da91d5c4971` |
| `green-precision` | 0 | 1.59 | `fa5f0af0cbcb517fd09f0f5987f36ec739905c363f99fef63008f72fc1dabb7f` | `12956df90bfbe78ac62122803b85ebf91512060dacb948e2ef7b6384663b873f` |
| `green-precision-http` | 0 | 15.8 | `da72856faa8309a825c059dc969293a79fd49fc3eca06d1a8cadf177afc5b690` | `2fa68525310c6762bd99b9d89ed0bbffd3a6c325b0230f3ad2564706d70391e8` |
| `green-legacy` | 0 | 6.68 | `000a2b80041fbf97e55c0d4ae87446e88e8b130e8e225d66adf400bc99cb9545` | `ec1474065af24924989cf9b90b52476947ba448b92245235ae92ade3d0dce955` |
| `green-transaction` | 0 | 2.04 | `11e663c2b5f42408af665abf15aeccc45e87f4ea09aeb7c18ded94cf4beff278` | `3e7f6b657fa3fa88ee9e123e10227c261f1018c5746de6bd6631a1a8b615c6e9` |
| `full-r2` | 0 | 811.13 | `0a4bcc02ba2975b227b95eca29ce11a2c9b63fc55939d20b6a49639a98aea0fd` | `b7eb0e32869b26a6d2ac2c62304e05df21f3458f438ac42986ae885e65501e1e` |
| `static` | 0 | 59.19 | `7ba841d6f1d06ab2aeba24c78c8c11259fd9d9308b8172f770a8bab307ae8b1a` | `7073f2696d7e1984defc2c4f41b9b274f6c03736a434ae2247178081b25369c7` |
| `f7-source` | 0 | 1.71 | `b8c8397c4da82117405893be86ede6838d8dc62663a1f5871216b12093d0226c` | `7d798be39d9aa5e183d88d8680e6d84d927dc1229bcc567e27763a1b36e077f5` |

旧三条冻结schema断言仍按QA1/前handoff分类保留，本轮未为其放宽/skip/xfail：mapping_migration六迁移/旧head断言在entry通过，获批0a2+1b3后八迁移触发，不能称entry已有失败；temperature五迁移/e4 head两条entry即失败，当前仍冻结不适用。旧文件不在本次改动中。当前64→71→75/唯一1b3→0a2→f6由新静态测试证明；不是实际库迁移或B证明。未无依据重复19旧suite，原413/13及QA1结果完整保留于历史。

## 当前联合B提案输入（只文档，未执行）

本次源码F7更新为`sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`，来自BE009批准范围cycle索引修正，f7-source-report确认liveDatabaseChecked=false。后缀旧`28edcba...`只代表原QA1/旧handoff时点，不是当前B目标。当前必须先BE009独立0a2/71，再BE010 1b3/75；保存F7/epoch/source binding/proof与旧64数据前后证据，schema-only重验不是任意重新采用。两轮隔离目标/卷/schema/运行ID，第一轮合成旧64行及T1，第二轮空schema；T1为可丢弃合成夹具，不冒充生产历史采用。

从另行获批临时BE010-r2-B/75/1b3 profile的backend目录，显式PYTHONPATH，实际入口仍为：

```text
uv run --offline --frozen --no-sync python tests_mysql/test_business_time_adoption.py
uv run --offline --frozen --no-sync python tests_mysql/test_business_integration.py --suite business
uv run --offline --frozen --no-sync python tests_mysql/test_business_integration.py --suite retained
uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py adopt --plan --revalidate-schema-only --target-alias <alias> --schema <schema> --expected-schema-revision 1b3d5f7a9c20 --expected-storage-epoch <既有epoch> --expected-adoption-id <原采用ID> --operation-approval <精确批准引用> --confirmed-by <批准者引用>
```

每轮待批准的合成env：BE010_MYSQL_EXECUTION_ACK=ARCH-BE-010-r2-B、BE010_MYSQL_SCHEMA_ACK、BE010_MYSQL_ENDPOINT_ACK=127.0.0.1:<批准端口>、BE010_MYSQL_RUN_ID、BE010_SOURCE_REVISION_ACK；合成MYSQL_*和TEST_MYSQL_DATABASE=arch_be010_r2_*（不同于primary）、非root、TESTING=True/PRIMARY_DATABASE=mysql/全部mock-runner-bootstrap=False。BE009先用其PLC_FACTS_B_OPERATION_APPROVAL/TARGET_ALIAS/SCHEMA/EXPECTED_REVISION=0a2c4e6f8b10/STORAGE_EPOCH/CONFIRM独立完成71阶段。真实schema-only apply另须PLC_FACTS_MAINTENANCE_ENABLED=True、操作批准和精确APPLY确认；当前一概未运行。各轮矩阵/故障注入/目标guard仍交fresh QA和Owner后续判断，不以脚本存在预记B通过。

## 文件、资源与交接

本次12文件：

- `backend/common/integration/http.py`
- `backend/app/equipment/integration_domain.py`
- `backend/app/performance/integration_domain.py`
- `backend/app/monitor/integration_domain.py`
- `backend/app/equipment/services/async_integration.py`
- `backend/app/performance/services/async_integration_observation.py`
- `backend/app/monitor/services/async_integration.py`
- `backend/app/performance/integration_storage.py`
- `backend/tests/test_business_integration_api.py`
- `backend/tests/test_business_integration_contract.py`
- `backend/tests/test_business_integration_service.py`
- `backend/tests/test_business_integration_storage.py`

CODE_INDEX当前完整SHA `08cf4e2bdb02953a7806d17c32aa3a8b22d5812143feb2e860467f611488869a`取代旧`1ce62cba5f6481e06e8c92454c315f751af9ab4b9519442bef388b4a598f09a4`；root/BE009 QA2独立确认只SMA local_configuration段+8行索引，BE009/BE010段未变。本DEV未写该外部增量，按root串行协调保留而不回退。当前100文件是完整允许面联合源码/合同清单，不把共享BE009/SMA事实计作本DEV独立实现。

自有rework-1保留bundle-before/implementation-before、公开source、guard/offline-bin/run与独立探针、red-reports、所有命令/日志/报告、pytest basetemp、logs/pycache/uv-cache和静态SQL/manifest，供fresh QA2复现及历史审计；原开发目录资源依赖按后缀原归属保留。所有runner已退出，无后台任务/DB/容器/监听/Git worktree或独立notifier。未清理他人或QA资源；经QA消费/Owner相应gate且主协调确认无证据依赖后回收自有副本/缓存，必要事实已持久化在本tasks。

当前源码manifest SHA `5499ff917411c7d84fa1e1be079f59246c11179b4d5c4ff82d589a557a2ba7b1`；下表为100文件完整持久副本。tasks最终自身SHA由外部handoff固定，避免自引用。DEV自检仅支持再次交接fresh Verification QA2，不给QA verdict/Human Owner验收；B、真实采用、迁移及历史生产数据操作均pending。

| 文件 | SHA256 |
| --- | --- |
| `CODE_INDEX.md` | `08cf4e2bdb02953a7806d17c32aa3a8b22d5812143feb2e860467f611488869a` |
| `backend/.env.docker.dev.example` | `ea2886aa84c88b28d019ea3518c5714eca43c45efc7310862674c324569d1800` |
| `backend/.env.docker.prod.example` | `54c3fc39f69833c9f49e9c4d71e22ef2282a84b25f3c633dc3d5b12a0afb8c7c` |
| `backend/.env.example` | `33021261d511c17930445c8d0ff9596cd5b645dc1d3e8c1250ba7fed7a5e6bf9` |
| `backend/README.md` | `2e259c4eb7e9bdcc4a788a0506b263a8b31bfb719342f51141e43144d0677b5d` |
| `backend/README.zh-CN.md` | `216ac6421e9a1634c27bf68152d52653be5ddddc381bc3d4707bfb74a70a5f92` |
| `backend/alembic/versions/20261104_1400_1b3d5f7a9c20_add_business_integration_receipts.py` | `202b17e2f43b3b2c1505ac03876fb75147044cccd54cf1845e0545f5503bab27` |
| `backend/app/MODULE_CONTRACT.md` | `59df0919940179652d8e6719ee74d2e31e0bbcdb9d91f431690e54249b73b4fd` |
| `backend/app/MODULE_CONTRACT.zh-CN.md` | `14a6b3cf0d49133c6664cd234835f375f5113f243c0b398be489d076e87e57e1` |
| `backend/app/README.md` | `13c2171a32930fa69bb9e40bff63988d27544d480901139cd4d5be74c1a067da` |
| `backend/app/README.zh-CN.md` | `eeb606e726592326e1d109e7d2222d15f46c365b60203103a08ece93febdc9b8` |
| `backend/app/equipment/README.md` | `ef4fbaec9734432cd81380ec596aeb9e1b17c6acd7876b6f65e167e17609999a` |
| `backend/app/equipment/README.zh-CN.md` | `41107610645b2005db09210d42dc79186ad7e724c9f8b74bbe1d7539043650c0` |
| `backend/app/equipment/api/integration.py` | `e0fdc402de486b19ada1464b1c23d2e88e82a20a9790d528af1807e72f1ecd9e` |
| `backend/app/equipment/crud/async_integration.py` | `47e67877e6c8932f670e9c2a4415f200e19284bdb21a748193ae91324a927ec0` |
| `backend/app/equipment/crud/sync_integration.py` | `4d67f548ec8df8b68fe2afb47dffb119a20806b7b0374240979717c318334f36` |
| `backend/app/equipment/integration_config.py` | `4a881944d5d7959b2ca8d50eaf02d50fa83c6217aedbec8422d3785aac998cc7` |
| `backend/app/equipment/integration_domain.py` | `06200d5faff0a36f257d9044adae95514928a0479423268ac4a535983e3794a5` |
| `backend/app/equipment/integration_storage.py` | `111200d0cc7e981dac6e9a3265306e4e57dd6fbb75bf207c369473ce750eb9ab` |
| `backend/app/equipment/manifest.py` | `fa36a5d5b2d477174b9b1e89fcd545661507bc78acbabea0a35249e818bcbea1` |
| `backend/app/equipment/schemas/integration.py` | `5fe2966208f8a9d1055e87eb1999de32ab3cee643dd349096ebaae36529db61c` |
| `backend/app/equipment/services/async_drive_sample.py` | `cd8a8a6da6108f8984428597a5849005942b779667a2a6065576c067d7f712f0` |
| `backend/app/equipment/services/async_equipment.py` | `3179d7d210970376bfa77f9da5be6110aa6ef8f8b24bf2b723f191aed83e1ebe` |
| `backend/app/equipment/services/async_integration.py` | `cc177d1584e4c5cb818fe085435027361cbe95446b17d922f1a073513f6ced02` |
| `backend/app/equipment/services/async_production_parameter_sample.py` | `93fe3be87d1ed65d80e783d28e6044b5210ef6a174e172979394be8e900587df` |
| `backend/app/equipment/services/async_temperature_dashboard.py` | `7d1e949ccd2cb2f54dd54e22b0f7cfa8d26d3c434bc0f74aec8dd6b74b80d371` |
| `backend/app/equipment/services/async_temperature_sample.py` | `c7710b960480c5e5ff6fc5124b2d27c80f733cd2687d43df1573a1d3fa172d62` |
| `backend/app/equipment/services/sync_drive.py` | `80e64666759d450c9709c3dd64e0af53e983c80e563e3a5f70c31d5922a5f74e` |
| `backend/app/equipment/services/sync_production_parameters.py` | `51162f1135abeb2e5cdbc14e44f8ff7e43615ffb18c7d4cc078a38fbc3006abb` |
| `backend/app/module_contract.py` | `d91c98d46f526af8e87502685833dd00570f45c090c40949938ae689cfd84778` |
| `backend/app/monitor/README.md` | `cc47ae0ada0301e6be7e47c01bef90d136742f2cdf11e98c78b8c3ea55139a2c` |
| `backend/app/monitor/README.zh-CN.md` | `72be0c1d0b2896796ba669f3481b9448d083a05de42d68b9217101a020927db5` |
| `backend/app/monitor/api/integration.py` | `addaaa4bae3faa28436a43f302ea3085cff09b904ace334486c88d679473790d` |
| `backend/app/monitor/crud/async_integration.py` | `238ac3cd26b01054493a772dfe24ce80bb8105e87baebae2024874930ef05f68` |
| `backend/app/monitor/crud/async_process_curve_sample.py` | `e14099d6a58d241d60140998989f16d871f3722fff2e07ecc1edefaf06324209` |
| `backend/app/monitor/crud/async_temperature.py` | `561ab18e0e238baf08e8f09ac06953b177f54d42c40bbb92e6c7be9bb494defc` |
| `backend/app/monitor/crud/sync_integration.py` | `7ff3326c415459aa551a56e124919155604b6cdc9418a760bcc73894f8989eb6` |
| `backend/app/monitor/integration_config.py` | `c5cf1167945b23f2b9385784e4c5bdfcb446755f7f5f9184af0c35baddf7bc44` |
| `backend/app/monitor/integration_domain.py` | `08c36ef4f40645589738beb4453b68534c81f328531fe7480f54e497307927a9` |
| `backend/app/monitor/integration_storage.py` | `d86f1693c962e5c15cca2aa225de9095035724ebca76be1e6f3e3a983fcef20a` |
| `backend/app/monitor/manifest.py` | `571e95bcf0867318d817d0ef57c185c39cf649f9730260254b484f722ef3034d` |
| `backend/app/monitor/schemas/integration.py` | `b1aff4e6c1f47248fe985ac588b05fa09fd739b7bbb2763d774f4c357ef3867b` |
| `backend/app/monitor/services/async_integration.py` | `7cfd58f169aa127bfb27d1623a26d7681cd4255cfa96a623ae93dfa9de40a421` |
| `backend/app/monitor/services/async_process_curve_sample.py` | `6375b82799a114da5fbec57d7bac05cdea55d5754df3289fc25544472e7e4304` |
| `backend/app/monitor/services/async_temperature.py` | `fdad7a71870cfe1a1bb0f35d728dbc542ec5720e6e306a5143cc76c9f045ea7e` |
| `backend/app/monitor/services/sync_process_curve.py` | `7d3acff48c672b28b379d45a7ef68a7c0f02b22a4d2f746869a117fcdb533abc` |
| `backend/app/performance/api/integration.py` | `2a767b4525ea526095c0fe158ed13f133b8a7aeb2e5d648fc3802ffc1a8102e4` |
| `backend/app/performance/api/lineage_routes.py` | `6585de694dff7ecdab5eb1d7c81d717c5ea59ee54070edc5d9e0d1abe2180b7a` |
| `backend/app/performance/api/routes.py` | `deb50f94d9de87955051f078ec2bb24b97961d57644e8a81452afa1811a23dcd` |
| `backend/app/performance/crud/async_integration.py` | `952b57c86cc0bdb949717b69622e74dea6063b4184a7a3d3dcac9df5b2ff8faf` |
| `backend/app/performance/crud/async_performance.py` | `556eb5b0c9274f5a5d73ea390cabaf1b8b7fd8033f71df5a62175009158596a5` |
| `backend/app/performance/crud/async_production_observation.py` | `af54927b1cc3e59c47ff5052624c15adb04ed5409628c9d7695f552eab56dfb6` |
| `backend/app/performance/crud/sync_integration.py` | `870a6dc271a5853c3a76058bc22be8ead6ae9d424c3ec280c51a761e95f6c4d5` |
| `backend/app/performance/integration_config.py` | `9937fe42fecb377d28a358a49a1cbbefa390d526df6c9cbcc1498928e64f2c94` |
| `backend/app/performance/integration_domain.py` | `aa2d687dae37c319859407b58ce70297d4b26d24390ec28cb60c72ed8eb273f8` |
| `backend/app/performance/integration_storage.py` | `a598e5cec96c69cd016a2eb121a0276bc5c6b047f1378046ce2f1405c032898d` |
| `backend/app/performance/manifest.py` | `ca0af830639b9a758bf2bedf01581f4d8431e89f6e2a476c1b3aa279b8ea25e8` |
| `backend/app/performance/schemas/integration.py` | `79d3032c1dbed1e5517727eabf761bc69f3e5e2c8a733ec3ae98c6f51118bb66` |
| `backend/app/performance/services/async_integration_observation.py` | `368187b6a3d90d59cdceede6508dc5e0edc3858c3bdc5208eab0121608f43e34` |
| `backend/app/performance/services/async_integration_process.py` | `00f97d6b8487526d7889ce29f5a95f93907b9e36d5c32a1c8a2452e1ffa147d5` |
| `backend/app/performance/services/async_lineage.py` | `6b66513de9970905a369430dcadede2662da3249d7732dcc91f4533e2f58f159` |
| `backend/app/performance/services/async_mapping_query.py` | `e67ffd9f69289a68fc59399236acdd660225b25eafc64057660b3eb983d92063` |
| `backend/app/performance/services/async_performance.py` | `dd7db59f35e8b1840bdfaadd8044c8bee1bce232357acb532aaaaaa87c15db51` |
| `backend/app/performance/services/async_process_sample.py` | `9229f5e57765da1b78ea1bd2e3c0cb65bc9d8081ae01181f32edfc1d8afd3247` |
| `backend/app/performance/services/async_production_observation.py` | `3de0ec117781e5ad0229dc5aeded2b157aee0e89495054956ecb9d24b42b4000` |
| `backend/app/performance/services/async_split.py` | `c6d9ba71263f6f725c96cb4199a8640e46aae6c337bdeab066e10c8d9d0f0a6f` |
| `backend/app/performance/services/sync_process_speed.py` | `f2e3bed65e58f45cadb9b4e228252588a8b8bed8ad77773691a9ff0d558ab47d` |
| `backend/app/performance/services/sync_process_temperature.py` | `381054ff429b32f033c2076065bb8c08430c8ccd99509744a08475afcf2f2dca` |
| `backend/app/performance/services/sync_process_tension.py` | `a3750a577d9b60821d655924f9a409a780d1224756007e3dd11ac0e781b2bd51` |
| `backend/app/performance/services/sync_production_record.py` | `1b228dcf166931bb8619602bf950a206df0734e2ab1289184896445a4534a84e` |
| `backend/common/integration/envelope.py` | `428c8e995fd02ae87f9e2b81835ab2757411dce3d1e10c93be9c35a2092d6c10` |
| `backend/common/integration/http.py` | `170dff1c33a9f733f634f7bd99721d5e00abd9a2c20bc48956bcdfd60f0887bf` |
| `backend/common/integration/receipt.py` | `33bda91fb9ccd0d36580ebe4236ebaa9e915abdc7f0c5ba1d09539ff5aa16b07` |
| `backend/common/integration/storage.py` | `ca4791093b2a72b275ba9453ebb83811ffd01cea0c1ea0a6aa94d584d082164f` |
| `backend/scripts/README.md` | `a5be1347fdb43ebfaa6d5e823c8bf84e1ddc88fbaffd88d77e3a1ce27a2baf6b` |
| `backend/scripts/README.zh-CN.md` | `3cdca450c50354bbb826dfcd987e1f5af5c47cb289b4fafd491d39c24824eb87` |
| `backend/scripts/business_time_adoption/.env.example` | `35c687a61cfb8910fba513c31760db89ec5f79defba4f9749e2e5f98a6dd6a52` |
| `backend/scripts/business_time_adoption/README.md` | `c5af6cad7d8825b996f1557fed529d7028ed05e76c6e765c2aae8e60e87d0e3d` |
| `backend/scripts/business_time_adoption/README.zh-CN.md` | `13a8222d190ebea93c588d44bb60e9d6afc31404b32eb06bc39fe85564450032` |
| `backend/scripts/business_time_adoption/main.py` | `aeb5aa553065c87e8694499ed0cd3d2c03ef89956eb50ea0bfc32ba14ff36a36` |
| `backend/tests/module_admission_fixtures.py` | `cd3c399657aaf5444d2fd718192016c7df6f76db87985bdd2fbfa8aa9786ecc9` |
| `backend/tests/test_business_integration_api.py` | `ad2a052697b4e798a3484a27e9aa1d2c91e6463f80056fad81efcbca1b6ecdc4` |
| `backend/tests/test_business_integration_compatibility.py` | `8ee66757ed69bb792a357ed06be257e0b1ffa56ce68be82f749fe5b4b364f354` |
| `backend/tests/test_business_integration_contract.py` | `185327419a0b3f4ecfd7fabf8ea719ae4ee5b20c787513d491de6e7a8e2e08b1` |
| `backend/tests/test_business_integration_migration.py` | `b629890e194abbbfe2a06142c933f6f693e03013097201f63407c60959d98978` |
| `backend/tests/test_business_integration_provider.py` | `f084b26227b03bc3e8479f2b8040fca4990554af8b443e240eaff4214335b17c` |
| `backend/tests/test_business_integration_service.py` | `c0d3c0c6c0e2fba8cb2a4638ad320e2c050d25ee6031c61a464648790482373b` |
| `backend/tests/test_business_integration_storage.py` | `4f232c64db75f19a393d93fbfc406b42c9124d73942d21c2189ca5f89b0cf8b5` |
| `backend/tests/test_business_time_adoption.py` | `6eda5b5df7965d326fec8e85d7f18fa3bf58e69de723ca7b2cfb5d23e60bd9e2` |
| `backend/tests/test_equipment_temperature_config.py` | `2d9c5aa5d5dcd85fdd77a42e87d83f0545295b31a60a3a583b0999978f21498b` |
| `backend/tests/test_mapping_compatibility.py` | `e30429c559c426949c5b4337157d2a21e8b5d767a4b95ed2cf0f1236a69b6ca2` |
| `backend/tests/test_module_contract.py` | `1ee4d9c2032fd1355a5cb6f133b805648a3588f98b57e2c5b63b5d76c4f455fb` |
| `backend/tests_mysql/test_business_integration.py` | `6262e07edd77d8e6ae93c90e78a5df25f04d3856967c812ccfae66293afd5600` |
| `backend/tests_mysql/test_business_time_adoption.py` | `1abf8a3e05df2fcf2977bbb0603bf570734aff1dba9dd0ea103f9e92e66fa92c` |
| `contracts/README.md` | `0d22882ba1aeb589bdd4e76dc162a5560ab402943a1ee7cd37cf17772ec4f700` |
| `contracts/README.zh-CN.md` | `ac1677444bed7182703f58626eec88ff0809c767226f033a9dbe40d1d69aaab1` |
| `contracts/published/http-api/business-integration-v1/README.md` | `c190e77bfbf2a5bcf2bfab410b30bd88824a493bb3573f12d89efc497a9784cf` |
| `contracts/published/http-api/business-integration-v1/README.zh-CN.md` | `1d6fc9be55c0e8e7c1880f21108dd556ec2191be0943bcc8dc79b801091b3e7a` |
| `contracts/published/http-api/business-integration-v1/examples.json` | `2255e6752cb8079d813ddc65773f07460cbfdedc0c00d10faaec63064d7cc724` |
| `contracts/published/http-api/business-integration-v1/openapi.json` | `d92bf03a9e8b3e4575fddc9caa68233e6b415210a6965c0a29b6b99264727562` |

---

# 历史完整tasks：QA1前r2 handoff（以下字节原样保留）

Task ID: ARCH-BE-010
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: r2 A源码 source_ready_unadopted -> fresh-context Verification；DEV检查及冻结允许面已交接，3个冻结schema断言限制保留；G-T/数据库/Docker/B/实际迁移及DAA未执行
Task Namespace: aiis-ics-arch
Classification: root
Capability: T1有限时间兼容、八类业务async接线与闭合provider源码
Owner: Backend Core 与 equipment、performance、monitor 公共业务模块
Updated: 2026-11-04

# r2 A 源码 Development handoff

## 精确批准、交付与角色边界

Human Owner明确批准ARCH-BE-010 r2，仅进入STD A源码阶段，数据库、Docker、实际数据迁移和DAA暂缓；原话及收据归spec。批准spec SHA256为`955877e96b4695b0c00aa81ef6e862dd6a642e82157edd05d5aeef8c175add5f`，批准原稿SHA为`4e5b0c56b1aac066458c1f24a5037bbab53c18946cd70fd79d8ab747a9342b6e`。

本轮是实际命名Development，直接交付`/Users/jason/Desktop/DreamCode/aiis-ics-arch` working tree；只读HEAD仍`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，未建commit/branch/worktree、未Git写。根AGENTS、canonical workflow、development.toml、根/最近README与PLAN、完整bundle及相关实现为实施输入；使用backend-arch及六份必读refs、backend-script-tooling、aiis的BLUEPRINT/CONTRACTS、code-document-indexer。角色TOML的模型/effort是配置证据；本profile是contract_only，不宣称平台ACL/强制路由。

只写r2.6允许面与本tasks。没有修改spec/checklist、根/backend PLAN或plans catalog。下方r1全文逐字节保留，checklist仍为r1 A0直到fresh Verification。BE009负责独立facts实现，先行释放3 env、fixture和README/合同/CODE_INDEX共享路径后才由本DEV按段合并；其4个新键、事实入口和F7记录保留。允许面manifest含共享文件的联合增量，不把BE009独占代码算作本任务实现。

## 已实现源码面

- **有限时间与采用**：Core纯StorageProbe/AdoptionContext、凭据解析/探针校验及上海存储/旧wire转换；StorageProbe公开字段精确serverUuid/schema/schemaRevision/utcNow，内部snake只读别名。三个owner静态13表41列profile及只读legacy view；async/sync探针只用传入会话，revision共享锁current read，不自建/提交session。默认unadopted不读取采用文件、不探DB、不转换旧值；不认识profile、残留路径、无效凭据、错目标均拒绝。basisProfile固定键/enum，不猜宿主TZ或按行时区。
- **旧时间边界**：旧HTTP先保留UTC fingerprint/原DTO，再复制物理键/时间；旧显示仅构造只读view，不临时改绑定ORM。Projection在同一host会话中先探针再转换固定fact字段，保留原DATE语义、cursor/audit/事务。人工pair/审计及系统列显式取DB时钟，人工重量非NULL包括0优先。旧温控sync路径不连带转换。monitor曲线created_at同时含系统/Projection来源且旧reader没有可靠来源标签，legacyNaive≠systemWire时owner-local明确拒绝采用；未新增cohort/profile或凭NULL猜来源。
- **A1**：温控十值不可变、drive/参数仅补NULL，完整冲突先验证再改；实际既有业务表、来源/映射与新equipment receipt同事务，无伪actor/sampleId。
- **A2**：生产按设备水位锁、新历史事件current read、活跃/目标行、主行/前卷/水位/事件/receipt同事务；新历史成功证明不取旧actor cache。同刻无新事件证明不冒认成功，旧观察stale持久decision_only。三过程校验本通道可靠在产事件父、设备/卷、完整补后范围，不造父/重激活父。
- **A3**：33指标曲线不可变，保存实际值和字段存在语义；新receipt独立永久保存sourceRefs/mapping，raw无FK/级联/TTL。
- **事务/HTTP**：命名MySQL1062仅最多3次恢复，其他Integrity不冒充duplicate；业务拒绝rollback后新current read恢复投递冲突优先。commit开始后异常为commit_unknown，cleanup失败不能抹掉未知事实；不在同请求盲重做。typed结果和精确序列化在commit前验证，committedAt为获胜事务commit前最后取用DB时钟。DTO/父路径/准入/采用通过后，准备yield依赖才`async with await get_db_session()`；Service独占commit，完整session退出由IntegrationRoute保护。
- **Schema/provider/工具**：精确1b3后继接BE009 0a2，只新增4表且新表16个日历列无UTC自动默认；非空新表拒绝破坏downgrade。正常注册应用提取8路/57个闭合schema，JSON number/integer、8种typed200、按资源收窄错误、状态分支/数值域及示例/冻结向量。只读inspect/plan/verify工具裸入口只help、显式目标配置、脱敏JSONL/candidate，无apply/任意SQL。三example当前91项（旧69+BE0063+A0 12+BE0094+采用3），原84字节前缀不覆盖；双语说明与索引同步。

## DEV self-check 环境、真实命令与结果

项目行为仅在排除真实dotenv/.venv/logs/data/dist/build的公开副本运行，复用正式backend/.venv，不安装/同步依赖。所有runner实际argv均为自有offline wrapper下`uv run --offline --frozen --no-sync python ...`；process env仅合成占位、TZ=UTC，PYTHONPYCACHEPREFIX/UV_CACHE_DIR/LOG_DIR和pytest basetemp显式置于自有tmp。sitecustomize在导入应用前阻断socket connect/connect_ex/bind/listen、sqlite3（含内存）、SQLAlchemy Engine/AsyncEngine及已安装DBAPI连接。静态末轮核对关键函数归属，所有运行guard事件均0。

主runner为`python3 /private/tmp/arch-be010-r2-development/run.py <tag> ...`；最终副本为同目录`run-final.py <tag> ...`。每轮精确argv/cwd/exit/wall time在`<tag>-command.json`、完整stdout/stderr在`<tag>.log`。pytest统一`-q -m no_db -p no:cacheprovider --basetemp <owned-tag>`，没有全局pytest或共享清库。ASGI全部进程内，不运行lifespan/listener/真实HTTP、DB/Alembic命令/Docker/PLC。

| tag / 实际输入 | 真实结果与适用边界 |
| --- | --- |
| `pure2 --noconftest`：contract/service/storage 3文件 | exit0；114 passed/4.75s。初轮15失败因该独立pure入口未导入Plan关系目标；补显式导入后通过。不是DB证明。 |
| `r2-focused2`：contract/api/service/storage/migration/compatibility/adoption/module_contract | exit1；221 passed/24 failed/485.79s。非法refs本应422却平级DB依赖先失败；修为先完成DTO/准入，再创建session。未放宽断言。 |
| `dependency-fix --noconftest`：3个正常composition非法refs节点+provider当时9项 | exit0；12 passed/35.72s。该轮仍为中间get_db准备链；后续改公开get_db_session避免退出再commit，并覆盖实际新factory拒绝探针。 |
| `final-r2`：最终9完整相关文件（含provider） | exit1；257 passed/1 failed/365.80s。唯一失败为新增离线迁移测试使用无add_column的Core Recorder；换既有BE006 Recorder后暴露generic/variant声明签名差异。没有伪称本轮整组全绿。 |
| `final-targeted`：migration/storage/service/adoption 4文件 | exit1；31 passed/1 failed/1.82s。新migration原用dialect类型，MySQL DDL一致但通用声明类型与Model不一致；新迁移已按Model改为精确with_variant，未动六旧迁移。 |
| `legacy`：原14文件+mapping_service及4个Projection文件，共19整文件 | exit1；413 passed/13 failed/234.38s。3条冻结schema断言如下；另10是本轮旧production默认路径传新增kwargs导致的真实回归，已修为未采用调用原3参apply/2参state。旧测试不改弱。 |
| `direct-final`：migration/storage/service/adoption/provider 5文件、3个正常composition非法refs节点、旧mapping_api+mapping_service两完整文件 | **exit0；132 passed/91.61s**。包含generic/variant修复、13表41列/纯view、StorageProbe公开字段+camel/snake只读别名、3组async/sync探针、monitor混合basis拒绝、正常注册八路typed成功/退出顺序、真实新factory前非法请求拒绝、已修10个旧默认路径回归/人工0/父/生命周期。 |
| `cleanup-fault`：failed_cleanup_cannot_erase_commit_unknown | **exit0；1 passed/0.34s**。实际commit抛错且rollback也失败，仍503 commit_unknown，仅一次commit尝试。 |
| `frozen-final`：下列3个精确旧schema节点 | exit1；3 failed/12.80s；原断言完整保留，不纳入当前75阶段通过结论。 |
| `static-last --script static.py` | **exit0**；整仓preflight、app/common/core/database/projection/scripts/tests/tests_mysql及main/run/build compileall、正常composition完整75 metadata、8路57schema与发布工件逐项相同、4表MySQL静态DDL和guard归属均通过。仅编译B源码，未执行B。DDL SHA256=`62c97c58544bef68d490e49fbb147ddf39a56819908ac863ddc7db1e1de929c5`。 |
| `python3 .../audit.py`；只读`git diff --check` | exit0；95允许面文件；正式树与final-source逐字节一致；313保护文件/6旧迁移不变；spec/checklist固定、r1任务原文后缀不变；新增链接/空白/文件头无问题、guard0。继承旧行的尾空白保留，审计首轮把其误报后改为与entry逐行区分，不批量格式化。 |

以上不同输入/轮次不相加，不把257/1改写为“最终全套通过”。最终代码变化的直接调用方已有132项+cleanup单节点和末轮静态证据；fresh Verification仍须独立消费同一当前源码，不复用DEV结论作QA。

### 三条冻结schema断言的精确分类

| 节点 | 当前/entry归因 |
| --- | --- |
| `tests/test_mapping_migration.py::test_six_revision_60_to_64_model_parity_and_53_protection` | entry六迁移/f6时可适用；本轮获批两个后继使当前8迁移/1b3，故其固定6/head=f6断言不适用。**这是本轮新增后继触发，非原有entry失败，也未修复**。该文件不在allowlist，未修改。当前64→71→75 recorder及原64子集/六旧字节保护另行通过。 |
| `tests/test_equipment_temperature_migration.py::test_five_revisions_58_60_58_parity_old_bytes_and_mysql_types` | r1 entry已有第六f6而冻结期望5，历史已有失败；当前8比5仍失败。原测试文件/断言与entry一致，不伪称已修。 |
| `tests/test_equipment_temperature_migration.py::test_single_explicit_head_and_no_data_migration` | r1 entry head=f6对冻结e4已有失败；当前head=1b3仍与冻结e4不同。保留原断言及新旧差异，未称当前head仍是f6。 |

公开配置历史69/72/84与当前91按任务来源显式分组，原前缀SHA和冻结数量要求保留；A0 named fixture重建其84配置/68 metadata/schema面，并明确实现源码仍来自当前树，不冒充旧二进制。当前另命名BE010-r2-A/B、75及1b3。

## A2交接前自审返工：统一活跃/目标锁顺序

前次95文件冻结manifest为`ea2eae40bdb94629ea485a5f3d67df670d1ef312d01a0444216c4b051f2cc63d`，tasks为`6d1161f82b37d6fd35b173832936b79cc8e04f129469af56122e7bd274675416`。自审发现先锁active再独立by_coil时，较小ID inactive目标可能在较大ID active之后锁定，未满足r2统一主键升序。真实撤回前次handoff，经主协调确认在同r2允许面返工，BE010 QA尚未启动；未改spec、共享或Core，也未干扰已启动BE009 QA。

修复仅performance新CRUD/Service和对应2测试文件：水位和历史事件仍先锁，随后同设备(active OR精确目标coil)一次current read，统一ORDER BY id FOR UPDATE；Service从已锁集合分选active/target，不再另锁target。覆盖较小ID inactive目标+较大ID active、原先新/活跃目标顺序、来源/事件/receipt恢复和人工0等原规则。无新增业务/配置/公共接口。原manifest/tasks完整副本留在自有tmp的*-pre-lock-order文件，原真实各轮结果上文保留，不将原冻结改写成最终输入。

`run-final.py lock-order tests/test_business_integration_service.py tests/test_business_integration_storage.py tests/test_mapping_api.py tests/test_mapping_service.py`：**exit0，114 passed/4.65s**，包括统一current-read SQL排序断言、较小ID inactive重激活及旧路径/人工0/父/恢复整文件回归。`run-final.py static-lock-order --script static.py`：**exit0**，整仓preflight/全部相关编译、75 metadata、8路57 schema发布一致、四表DDL及导入前guard再次通过。最终audit exit0，4个文件之外的91允许面文件与前次冻结hash一致；共享/Core/BE009独占不变，guard仍0。前次各批结果不累加或覆写，此返工后使用下方新95文件manifest交接。

## 尚未执行的边界与已知风险

本handoff仅A源码，**不是QA verdict、整体完成或Owner最终验收**。无任何数据库（包括SQLite/:memory:）、Docker、Alembic CLI/current/upgrade/downgrade、真实历史调查/转换/采用、真实HTTP listener/网络/PLC、依赖安装、Git写或发布；未读写真实.env；DAA不改。

真实RR/首水位/同异投递竞争、DB故障/提交后丢响应、字段逐项真实持久化/NULL/FLOAT、旧人工pair/0两提交顺序、旧HTTP/Projection目标兼容、真实时间分类/ID/FK/旧摘要/DATE守恒、raw到期后恢复及性能均仍需要另批MySQL B/目标证据。无DB替身不代替它们。所有unknown/同组混合不可辨别历史继续阻止G-T；凭据不是producer身份认证、数据库ACL或永久正确证明。无法隔离旧业务writer（同时保留CA/raw资格）就不能实际采用。业务/最小回执无TTL会增长，生产聚合不承诺覆盖前每个值有自动版本历史。

## 后续两轮隔离B提案输入（仅交接，绝未执行）

每轮先由Owner批准明确独立MySQL8.4.6 alias/schema/非root账号/loopback端口/卷、上海/RR设置、故障/清理及回收。仅临时公开`BE010-r2-B`源码profile和合成process env，无真实dotenv；两个轮次不共用schema/卷/运行ID。外层建立并保存原64表ID/值/精度hash，然后**显式f6→0a2（71）→1b3（75）**，不以head或全metadata create_all跳过阶段。BE009先完成其独立0a2 B；1b3后旧64和事实7表的逐表结构/值hash应再对照。

- 第一轮：带合成旧64行，经两个精确后继，空新表可退/非空拒退；BE010合成13表41列T1夹具只用于该可丢弃目标，不冒充生产历史采用。另核对真实旧API/Projection、日期/人工pair/0及两顺序。
- 第二轮：独立空schema重复两后继与业务/故障/并发/丢响应/恢复；改变合成宿主/session时区但不得改真实DB时钟或DAA/旧事实日期。两轮均保留业务/receipt/event/watermark/来源及F7前后证据，另批清理。

本任务独立B实际入口（从已批准profile backend目录，显式`PYTHONPATH=<profile>/backend`）：

```text
uv run --offline --frozen --no-sync python tests_mysql/test_business_time_adoption.py
uv run --offline --frozen --no-sync python tests_mysql/test_business_integration.py --suite business
uv run --offline --frozen --no-sync python tests_mysql/test_business_integration.py --suite retained
```

执行前每轮必设`BE010_MYSQL_EXECUTION_ACK=ARCH-BE-010-r2-B`、`BE010_MYSQL_SCHEMA_ACK=<本轮schema>`、`BE010_MYSQL_ENDPOINT_ACK=127.0.0.1:<批准端口>`、`BE010_MYSQL_RUN_ID=<本轮唯一简单ID>`、`BE010_SOURCE_REVISION_ACK=<冻结源码manifest>`；合成MYSQL_HOST/PORT/USER/PASSWORD/DATABASE、TEST_MYSQL_DATABASE（须arch_be010_r2_前缀且与primary不同）、TESTING=True、PRIMARY_DATABASE=mysql及全部mock/runner/bootstrap=False。入口只接受临时BE010-r2-B/75/1b3和非root账号/精确endpoint，不建库/清库/跑迁移。B源码尚未运行，其矩阵充分性/目标guard与故障注入仍需运行前独立审阅；这里只交可具体化的源码入口，不宣称已证明完整B。

facts联合gate：先按BE009 tasks的`PLC_FACTS_B_OPERATION_APPROVAL/TARGET_ALIAS/SCHEMA/EXPECTED_REVISION=0a2c4e6f8b10/STORAGE_EPOCH/CONFIRM`完成独立71阶段。1b3后保存并核对原F7=`sha256:28edcba4298a164389965c6f7d05b29e8e6494a1ace48d141d83c5edbd1d8e2e`、epoch、source binding、proof/水位不变，另批执行：

```text
uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py adopt --plan --revalidate-schema-only --target-alias <alias> --schema <schema> --expected-schema-revision 1b3d5f7a9c20 --expected-storage-epoch <既有epoch> --expected-adoption-id <原采用ID> --operation-approval <精确批准引用> --confirmed-by <批准者引用>
```

真正apply还须独立批准、`PLC_FACTS_MAINTENANCE_ENABLED=True`及`--apply --confirm APPLY:adopt:<alias>:<schema>:<epoch>`，不得由A或本段文本代行授权。按BE009批准清理夹具做事实三月/证明前缀过期后，再运行BE010 `--suite retained`核业务/来源/ACK/父子恢复；只核schema revision不等于F7及原epoch/proof已保持。完整B还需补足所有r2列出的真实竞争/故障/旧wire材料后由fresh QA裁定，不能因脚本存在而预记通过。

## 资源、冻结清单与精确交接

自有根`/private/tmp/arch-be010-r2-development/`保留公开`source/{backend,frontend-js}`（早期/整组输入）、`final-source/{backend,frontend-js}`（最终交付一致副本）、guard/offline-bin、build/setup/publish/audit/static/runner脚本、显式pytest basetemp、logs/cache/pycache、各轮完整命令/输出、静态DDL及hash/report。所有本轮命令已退出；无DB/容器/监听/后台任务/独立notifier/邮件/branch/worktree。未清理他人资源。保留至fresh QA消费与Owner相应gate后，由主协调按归属/依赖回收；联合entry/before、PM、BE009及旧A0证据均不归本DEV清理。

最终95允许面实现/合同文件SHA清单在下表，并同存`source-manifest.json`；manifest SHA256为`9b526ab8170198c3c0b144d46b040c3142fffc6d911771c99789c662db00e1f1`。后者和audit report为方便机器复核，以下持久表为其完整副本，不依赖tmp存续。tasks最终文件自身SHA由外部handoff固定，避免自引用。六旧migration、user/CA/database/DAA等313保护文件、批准spec和原r1 checklist无漂移；原r1 tasks后缀原样保留。

| 文件 | SHA256 |
| --- | --- |
| `CODE_INDEX.md` | `1ce62cba5f6481e06e8c92454c315f751af9ab4b9519442bef388b4a598f09a4` |
| `backend/.env.docker.dev.example` | `ea2886aa84c88b28d019ea3518c5714eca43c45efc7310862674c324569d1800` |
| `backend/.env.docker.prod.example` | `54c3fc39f69833c9f49e9c4d71e22ef2282a84b25f3c633dc3d5b12a0afb8c7c` |
| `backend/.env.example` | `33021261d511c17930445c8d0ff9596cd5b645dc1d3e8c1250ba7fed7a5e6bf9` |
| `backend/README.md` | `2e259c4eb7e9bdcc4a788a0506b263a8b31bfb719342f51141e43144d0677b5d` |
| `backend/README.zh-CN.md` | `216ac6421e9a1634c27bf68152d52653be5ddddc381bc3d4707bfb74a70a5f92` |
| `backend/alembic/versions/20261104_1400_1b3d5f7a9c20_add_business_integration_receipts.py` | `202b17e2f43b3b2c1505ac03876fb75147044cccd54cf1845e0545f5503bab27` |
| `backend/app/MODULE_CONTRACT.md` | `59df0919940179652d8e6719ee74d2e31e0bbcdb9d91f431690e54249b73b4fd` |
| `backend/app/MODULE_CONTRACT.zh-CN.md` | `14a6b3cf0d49133c6664cd234835f375f5113f243c0b398be489d076e87e57e1` |
| `backend/app/README.md` | `13c2171a32930fa69bb9e40bff63988d27544d480901139cd4d5be74c1a067da` |
| `backend/app/README.zh-CN.md` | `eeb606e726592326e1d109e7d2222d15f46c365b60203103a08ece93febdc9b8` |
| `backend/app/equipment/README.md` | `ef4fbaec9734432cd81380ec596aeb9e1b17c6acd7876b6f65e167e17609999a` |
| `backend/app/equipment/README.zh-CN.md` | `41107610645b2005db09210d42dc79186ad7e724c9f8b74bbe1d7539043650c0` |
| `backend/app/equipment/api/integration.py` | `e0fdc402de486b19ada1464b1c23d2e88e82a20a9790d528af1807e72f1ecd9e` |
| `backend/app/equipment/crud/async_integration.py` | `47e67877e6c8932f670e9c2a4415f200e19284bdb21a748193ae91324a927ec0` |
| `backend/app/equipment/crud/sync_integration.py` | `4d67f548ec8df8b68fe2afb47dffb119a20806b7b0374240979717c318334f36` |
| `backend/app/equipment/integration_config.py` | `4a881944d5d7959b2ca8d50eaf02d50fa83c6217aedbec8422d3785aac998cc7` |
| `backend/app/equipment/integration_storage.py` | `111200d0cc7e981dac6e9a3265306e4e57dd6fbb75bf207c369473ce750eb9ab` |
| `backend/app/equipment/manifest.py` | `fa36a5d5b2d477174b9b1e89fcd545661507bc78acbabea0a35249e818bcbea1` |
| `backend/app/equipment/schemas/integration.py` | `5fe2966208f8a9d1055e87eb1999de32ab3cee643dd349096ebaae36529db61c` |
| `backend/app/equipment/services/async_drive_sample.py` | `cd8a8a6da6108f8984428597a5849005942b779667a2a6065576c067d7f712f0` |
| `backend/app/equipment/services/async_equipment.py` | `3179d7d210970376bfa77f9da5be6110aa6ef8f8b24bf2b723f191aed83e1ebe` |
| `backend/app/equipment/services/async_integration.py` | `848af1fd8a71d345a9da8b4090d08650e6420780ffd591943beb9784d4edd307` |
| `backend/app/equipment/services/async_production_parameter_sample.py` | `93fe3be87d1ed65d80e783d28e6044b5210ef6a174e172979394be8e900587df` |
| `backend/app/equipment/services/async_temperature_dashboard.py` | `7d1e949ccd2cb2f54dd54e22b0f7cfa8d26d3c434bc0f74aec8dd6b74b80d371` |
| `backend/app/equipment/services/async_temperature_sample.py` | `c7710b960480c5e5ff6fc5124b2d27c80f733cd2687d43df1573a1d3fa172d62` |
| `backend/app/equipment/services/sync_drive.py` | `80e64666759d450c9709c3dd64e0af53e983c80e563e3a5f70c31d5922a5f74e` |
| `backend/app/equipment/services/sync_production_parameters.py` | `51162f1135abeb2e5cdbc14e44f8ff7e43615ffb18c7d4cc078a38fbc3006abb` |
| `backend/app/module_contract.py` | `d91c98d46f526af8e87502685833dd00570f45c090c40949938ae689cfd84778` |
| `backend/app/monitor/README.md` | `cc47ae0ada0301e6be7e47c01bef90d136742f2cdf11e98c78b8c3ea55139a2c` |
| `backend/app/monitor/README.zh-CN.md` | `72be0c1d0b2896796ba669f3481b9448d083a05de42d68b9217101a020927db5` |
| `backend/app/monitor/api/integration.py` | `addaaa4bae3faa28436a43f302ea3085cff09b904ace334486c88d679473790d` |
| `backend/app/monitor/crud/async_integration.py` | `238ac3cd26b01054493a772dfe24ce80bb8105e87baebae2024874930ef05f68` |
| `backend/app/monitor/crud/async_process_curve_sample.py` | `e14099d6a58d241d60140998989f16d871f3722fff2e07ecc1edefaf06324209` |
| `backend/app/monitor/crud/async_temperature.py` | `561ab18e0e238baf08e8f09ac06953b177f54d42c40bbb92e6c7be9bb494defc` |
| `backend/app/monitor/crud/sync_integration.py` | `7ff3326c415459aa551a56e124919155604b6cdc9418a760bcc73894f8989eb6` |
| `backend/app/monitor/integration_config.py` | `c5cf1167945b23f2b9385784e4c5bdfcb446755f7f5f9184af0c35baddf7bc44` |
| `backend/app/monitor/integration_storage.py` | `d86f1693c962e5c15cca2aa225de9095035724ebca76be1e6f3e3a983fcef20a` |
| `backend/app/monitor/manifest.py` | `571e95bcf0867318d817d0ef57c185c39cf649f9730260254b484f722ef3034d` |
| `backend/app/monitor/schemas/integration.py` | `b1aff4e6c1f47248fe985ac588b05fa09fd739b7bbb2763d774f4c357ef3867b` |
| `backend/app/monitor/services/async_integration.py` | `54b38d8ba095fdd89d6f6042dbbff459a66f00487d4f14ed4e44b093fa7d4d5b` |
| `backend/app/monitor/services/async_process_curve_sample.py` | `6375b82799a114da5fbec57d7bac05cdea55d5754df3289fc25544472e7e4304` |
| `backend/app/monitor/services/async_temperature.py` | `fdad7a71870cfe1a1bb0f35d728dbc542ec5720e6e306a5143cc76c9f045ea7e` |
| `backend/app/monitor/services/sync_process_curve.py` | `7d3acff48c672b28b379d45a7ef68a7c0f02b22a4d2f746869a117fcdb533abc` |
| `backend/app/performance/api/integration.py` | `2a767b4525ea526095c0fe158ed13f133b8a7aeb2e5d648fc3802ffc1a8102e4` |
| `backend/app/performance/api/lineage_routes.py` | `6585de694dff7ecdab5eb1d7c81d717c5ea59ee54070edc5d9e0d1abe2180b7a` |
| `backend/app/performance/api/routes.py` | `deb50f94d9de87955051f078ec2bb24b97961d57644e8a81452afa1811a23dcd` |
| `backend/app/performance/crud/async_integration.py` | `952b57c86cc0bdb949717b69622e74dea6063b4184a7a3d3dcac9df5b2ff8faf` |
| `backend/app/performance/crud/async_performance.py` | `556eb5b0c9274f5a5d73ea390cabaf1b8b7fd8033f71df5a62175009158596a5` |
| `backend/app/performance/crud/async_production_observation.py` | `af54927b1cc3e59c47ff5052624c15adb04ed5409628c9d7695f552eab56dfb6` |
| `backend/app/performance/crud/sync_integration.py` | `870a6dc271a5853c3a76058bc22be8ead6ae9d424c3ec280c51a761e95f6c4d5` |
| `backend/app/performance/integration_config.py` | `9937fe42fecb377d28a358a49a1cbbefa390d526df6c9cbcc1498928e64f2c94` |
| `backend/app/performance/integration_storage.py` | `00fbf2c189a7386e32bc0056704c4a64970d1ada4a630ee6a7df68b2ded2336a` |
| `backend/app/performance/manifest.py` | `ca0af830639b9a758bf2bedf01581f4d8431e89f6e2a476c1b3aa279b8ea25e8` |
| `backend/app/performance/schemas/integration.py` | `79d3032c1dbed1e5517727eabf761bc69f3e5e2c8a733ec3ae98c6f51118bb66` |
| `backend/app/performance/services/async_integration_observation.py` | `c44f7913bbd1f983bc842e5df20aeb5637c3c99987560a935abe491a43546f5c` |
| `backend/app/performance/services/async_integration_process.py` | `00f97d6b8487526d7889ce29f5a95f93907b9e36d5c32a1c8a2452e1ffa147d5` |
| `backend/app/performance/services/async_lineage.py` | `6b66513de9970905a369430dcadede2662da3249d7732dcc91f4533e2f58f159` |
| `backend/app/performance/services/async_mapping_query.py` | `e67ffd9f69289a68fc59399236acdd660225b25eafc64057660b3eb983d92063` |
| `backend/app/performance/services/async_performance.py` | `dd7db59f35e8b1840bdfaadd8044c8bee1bce232357acb532aaaaaa87c15db51` |
| `backend/app/performance/services/async_process_sample.py` | `9229f5e57765da1b78ea1bd2e3c0cb65bc9d8081ae01181f32edfc1d8afd3247` |
| `backend/app/performance/services/async_production_observation.py` | `3de0ec117781e5ad0229dc5aeded2b157aee0e89495054956ecb9d24b42b4000` |
| `backend/app/performance/services/async_split.py` | `c6d9ba71263f6f725c96cb4199a8640e46aae6c337bdeab066e10c8d9d0f0a6f` |
| `backend/app/performance/services/sync_process_speed.py` | `f2e3bed65e58f45cadb9b4e228252588a8b8bed8ad77773691a9ff0d558ab47d` |
| `backend/app/performance/services/sync_process_temperature.py` | `381054ff429b32f033c2076065bb8c08430c8ccd99509744a08475afcf2f2dca` |
| `backend/app/performance/services/sync_process_tension.py` | `a3750a577d9b60821d655924f9a409a780d1224756007e3dd11ac0e781b2bd51` |
| `backend/app/performance/services/sync_production_record.py` | `1b228dcf166931bb8619602bf950a206df0734e2ab1289184896445a4534a84e` |
| `backend/common/integration/envelope.py` | `428c8e995fd02ae87f9e2b81835ab2757411dce3d1e10c93be9c35a2092d6c10` |
| `backend/common/integration/receipt.py` | `33bda91fb9ccd0d36580ebe4236ebaa9e915abdc7f0c5ba1d09539ff5aa16b07` |
| `backend/common/integration/storage.py` | `ca4791093b2a72b275ba9453ebb83811ffd01cea0c1ea0a6aa94d584d082164f` |
| `backend/scripts/README.md` | `a5be1347fdb43ebfaa6d5e823c8bf84e1ddc88fbaffd88d77e3a1ce27a2baf6b` |
| `backend/scripts/README.zh-CN.md` | `3cdca450c50354bbb826dfcd987e1f5af5c47cb289b4fafd491d39c24824eb87` |
| `backend/scripts/business_time_adoption/.env.example` | `35c687a61cfb8910fba513c31760db89ec5f79defba4f9749e2e5f98a6dd6a52` |
| `backend/scripts/business_time_adoption/README.md` | `c5af6cad7d8825b996f1557fed529d7028ed05e76c6e765c2aae8e60e87d0e3d` |
| `backend/scripts/business_time_adoption/README.zh-CN.md` | `13a8222d190ebea93c588d44bb60e9d6afc31404b32eb06bc39fe85564450032` |
| `backend/scripts/business_time_adoption/main.py` | `aeb5aa553065c87e8694499ed0cd3d2c03ef89956eb50ea0bfc32ba14ff36a36` |
| `backend/tests/module_admission_fixtures.py` | `cd3c399657aaf5444d2fd718192016c7df6f76db87985bdd2fbfa8aa9786ecc9` |
| `backend/tests/test_business_integration_api.py` | `59fb436acc51786be0df4dd2e2d914f658e64dcc06980b0183ffabafa43e1399` |
| `backend/tests/test_business_integration_compatibility.py` | `8ee66757ed69bb792a357ed06be257e0b1ffa56ce68be82f749fe5b4b364f354` |
| `backend/tests/test_business_integration_migration.py` | `b629890e194abbbfe2a06142c933f6f693e03013097201f63407c60959d98978` |
| `backend/tests/test_business_integration_provider.py` | `f084b26227b03bc3e8479f2b8040fca4990554af8b443e240eaff4214335b17c` |
| `backend/tests/test_business_integration_service.py` | `0227f3ca441e03aae5a73c04df82170f4b08066b344662397a69f6b49c1bb396` |
| `backend/tests/test_business_integration_storage.py` | `9c2521f0b4e2a61c95c2029b746bb93e6f8b9ec6b882129c537d18e3057cdc30` |
| `backend/tests/test_business_time_adoption.py` | `6eda5b5df7965d326fec8e85d7f18fa3bf58e69de723ca7b2cfb5d23e60bd9e2` |
| `backend/tests/test_equipment_temperature_config.py` | `2d9c5aa5d5dcd85fdd77a42e87d83f0545295b31a60a3a583b0999978f21498b` |
| `backend/tests/test_mapping_compatibility.py` | `e30429c559c426949c5b4337157d2a21e8b5d767a4b95ed2cf0f1236a69b6ca2` |
| `backend/tests/test_module_contract.py` | `1ee4d9c2032fd1355a5cb6f133b805648a3588f98b57e2c5b63b5d76c4f455fb` |
| `backend/tests_mysql/test_business_integration.py` | `6262e07edd77d8e6ae93c90e78a5df25f04d3856967c812ccfae66293afd5600` |
| `backend/tests_mysql/test_business_time_adoption.py` | `1abf8a3e05df2fcf2977bbb0603bf570734aff1dba9dd0ea103f9e92e66fa92c` |
| `contracts/README.md` | `0d22882ba1aeb589bdd4e76dc162a5560ab402943a1ee7cd37cf17772ec4f700` |
| `contracts/README.zh-CN.md` | `ac1677444bed7182703f58626eec88ff0809c767226f033a9dbe40d1d69aaab1` |
| `contracts/published/http-api/business-integration-v1/README.md` | `c190e77bfbf2a5bcf2bfab410b30bd88824a493bb3573f12d89efc497a9784cf` |
| `contracts/published/http-api/business-integration-v1/README.zh-CN.md` | `1d6fc9be55c0e8e7c1880f21108dd556ec2191be0943bcc8dc79b801091b3e7a` |
| `contracts/published/http-api/business-integration-v1/examples.json` | `2255e6752cb8079d813ddc65773f07460cbfdedc0c00d10faaec63064d7cc724` |
| `contracts/published/http-api/business-integration-v1/openapi.json` | `d92bf03a9e8b3e4575fddc9caa68233e6b415210a6965c0a29b6b99264727562` |

**Development至此停止写入，实现状态source_ready_unadopted，交实际fresh-context Verification。** QA消费精确r2/spec、正式working tree、上述95文件hash、全部真实失败/修复/通过记录及B/采用限制；不得把DEV self-check代为QA/Owner接受。root继续负责串行QA与机械索引，不以本handoff授予DB/Docker/B/DAA或发布操作。

# r1 A0 完整历史保留区

Task ID: ARCH-BE-010
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: Development rework-1 -> 新 fresh-context Verification QA2；仅 A0 F-QA1-001/002 返工，G-T / A1–A3 / B 不变

# A0 Development 事实记录

精确批准 spec SHA256: `c33cd260dc74542f36436f31738e823734ae4bc75cf087a0dbb76c2d4c3dcaf9`。
Human Owner 批准采用 T1，仅先做 §10 A0；时区兼容和迁移方案先确认，数据库与 Docker 暂不执行，旧认证接口保持。
角色为实际 `development`；读取 `.codex/agents/development.toml` 配置（gpt-6.1-sol/high）是配置证据。
交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；不执行 Git 写入。并行其他任务改动保留。
根 coordinator 固定 entry 基线；本任务证据目录 `/private/tmp/arch-be010-r1-a0-pxmh71r0/development/`，供 Development / fresh Verification 核对，Owner gate 后由 coordinator 确认无依赖再清理。无真实配置或秘密复制。

## 实施顺序与验证

1. 先固定 bi-json/v1 正负向向量 → 纯函数及 typed DTO 无 DB 测试。
2. 添加关闭/unadopted 路由、模块模型与公开合同 → ASGI 内存传输、依赖退出/脱敏、静态 MySQL DDL、模块准入。
3. 提交源码逐列时间提案和精确文件/命令/限制 → 哈希与链接检查；只交 A0 developer_handoff。

## 实现前固定规范化向量

对象键按 UTF-8 字节排序，保留 Unicode/文本原貌，数字为 JSON number（不是字符串）；不使用默认 float repr。
Decimal 去尾零、无指数，零为0。FLOAT 输入0.1先binary32，精确值为 `0.100000001490116119384765625`。
时间 `2026-11-04T02:00:00.123Z` 与 `2026-11-04T10:00:00.123+08:00` 统一为后者。
规范业务对象固定 `{resource,parentRecordId,data}`，非过程 parentRecordId=null；data 仅含实际提供字段，因此存在集合直接由键集合表达。
规范请求对象为已验证信封（sourceRefs按完整规范字节排序）加 resource / parentRecordId。两摘要均 `sha256:`+hex；同业务不同producer/event/sourceRefs/mapping只改变requestDigest。父id变化同时改变两摘要。

| 向量 | 精确规范UTF-8内容 | SHA256 |
| --- | --- | --- |
| number | `{"n":1,"z":0}` | `11beb7b10beec1509e9c51e46aaa2445ba87a6134074c358144a087207082403` |
| float32 | `{"n":0.100000001490116119384765625}` | `d4d96540b7d99146547dfeab9f1221fe2415923836236a983603ea908e766146` |
| keys | `{"A":"中文","a":"x_y"}` | `f0b76ee71d3de40923891c395d4e603c0fcebc252ea86253ed61734fe286d0a6` |
| missing | `{"tv":0}` | `9c1c218ce4add43c3f840dd4eb0cf69f705072f1ec4c769427f7f8d6136e7c1d` |
| present | `{"km":0,"tv":0}` | `453518df18533b1e0041930af76c8e4ee5e4e4e0ace547e04ef9b2038d3e9e37` |

正向：1/1.0/1e0一致；0/-0一致；引用排列不改变摘要；中文和 `x_y` 原样；同瞬间offset一致；FLOAT32规范值与写入比较一致。
反向：省略与零不同（上表missing/present）；改变父id、resource、任一存在字段/值改变业务摘要；改变映射/来源/身份改变请求摘要。
必须拒绝：重复key（嵌套也拒绝）、snake_case、未知字段、显式null（仅非在产coilNo例外）、bool/字符串数值、非法UTF8、NaN/Infinity、极端指数、64KiB以上、深度12以上、压缩/错误媒体、重复引用；非零亚毫秒、超范围/scale、binary32非零下溢、过程非法min/avg/max、非在产携带十三观测。

## 实施与 DEV self-check

实际实现、DEV self-check 与精确交接见下文；不是整体 QA verdict。

## T1 时区兼容/迁移提案（待 Human Owner 确认，未执行）

源码逐列方案已记录于下方 T1 节；G-T 尚未解除。不探真实库、不猜历史时区、不批量加8小时。

## 补充完整摘要向量（实现后独立标准 JSON 构造交叉核对）

请求规范字节：

```json
{"contractVersion":"aiis.business-integration/v1","data":{"equipmentId":"line-demo","quality":"good","sampledAt":"2026-11-04T10:00:00.123+08:00","tv":0},"eventId":"event-1","mappingId":"mapping","mappingRevision":"r1","parentRecordId":null,"producerId":"sma-demo","resource":"drive","sourceRefs":[{"kind":"external_event","sourceEventId":"event","sourceId":"源_x"}]}
```

requestDigest: `sha256:8ce846b2554fb5a2d0e74c9c70da5be7aa9bfa2d528c69f76a81b8784dd83f58`。

业务规范字节：

```json
{"data":{"equipmentId":"line-demo","quality":"good","sampledAt":"2026-11-04T10:00:00.123+08:00","tv":0},"parentRecordId":null,"resource":"drive"}
```

businessDigest: `sha256:b045713d63eea8316ec0e81cb6054ede59d15efec94cacf587bb33d5adb81a5a`。该补充向量由 stdlib json（所有数值均整数）独立构造，非调用被测 canonical 生成预期。

## T1 可审阅方案：源码时间清单与迁移/采用顺序

**状态：待 Human Owner 确认；没有执行数据库调查、连接、DDL、数据迁移、Docker 或采用。** 以下“UTC”是当前源码 writer 的约定，不证明真实库每行符合该约定；真实历史须另批目标与只读调查。`unknown` 不能自动当成 UTC，也不能直接当成上海。A0 不修改以下旧源码。

源码依据：`app/equipment/{mapping_domain,temperature_sample_domain}.py`、`app/performance/mapping_domain.py`、`app/monitor/mapping_domain.py` 的 source-time/UTC formatter；三个模块 `models/{temperature_sample,mapping_ingest,equipment,performance,business_history}.py`（按实际存在的owner文件）；`database/base.py` 的 Timestamp；`equipment/services/_sync_common.py`、`performance/services/_sync_process_common.py`、`monitor/services/sync_process_curve.py` 的时区处理；`performance/services/{async_production_observation,async_mapping_query,async_performance,async_lineage,sync_production_record}.py` 及各既有 HTTP Service/CRUD。完整 source-map 与哈希交接清单在下节固定。

| 表 | 精确列 | 当前源码事实 / 兼容风险 | T1 待批处理 |
| --- | --- | --- | --- |
| equipment_temperature_samples | sampled_at | BE003输入强制归一无offset UTC，DATETIME(3)，设备+来源毫秒unique；旧wire `...sssZ`。 | 已证实UTC行按同瞬间转上海毫秒；保留ID和unique；新旧adapter边界一次转换。 |
| equipment_temperature_samples | created_at, updated_at | 两列显式 UTC_TIMESTAMP(3)。 | 已证实UTC行转换，未来使用已确认上海DB时间源；旧wire仍按原UTC格式。 |
| equipment_temperature_sample_receipts | sampled_at | actor投递绑定原UTC来源毫秒，与样本外键ID+设备一致。 | 与样本同批转换；actor/sampleId唯一身份保持；新producer身份不迁入。 |
| equipment_temperature_sample_receipts | created_at, updated_at | UTC_TIMESTAMP(3)。 | 同上按已证实语义转换；原回执不可因新接入续期。 |
| equipment_drive | timestamp | DATETIME(3)/CURRENT_TIMESTAMP(3)默认；HTTP明确UTC；legacy Projection接受自有timestamp/collected_at，aware转UTC、naive保留；旧自动插入DB默认与历史来源unknown。 | 先分HTTP equipment_id非NULL与legacy，再按实际证据；不能整表+8。HTTP业务键与旧查询参数同步转换；默认值采用另批确认DB时区。 |
| equipment_production_parameters | timestamp | 同drive，设备+http_coil_key+来源毫秒unique。 | 保留卷binary key/ID与所有省略NULL，转换前后冲突预检，不按小时归并。 |
| equipment_production_parameters | entry_time | HTTP归一UTC；legacy normalize_timestamp允许naive保留；历史unknown。 | 分类转换；不把到达/更新时间写入entryTime。total_time是分钟，不转换。 |
| equipment_temperature | timestamp | legacy Timestamp的func.now()默认；Projection aware转UTC/naive保留；无HTTP设备来源标识。 | 非新温控业务表；默认保留，若旧Projection整改触及则先取实际来源证据并明确新Revision。 |
| equipment_mapping_receipts | sampled_at | BE006 UTC来源时间。 | 同目标业务行一次转换；保留actor/stream/sampleId、稳定result与fingerprint含义。 |
| equipment_mapping_receipts | created_at, updated_at | UTC_TIMESTAMP(3)。 | 已证实UTC转上海；旧result里的UTC wire不机械替换。 |
| performance_main | reported_start_time, reported_end_time | HTTP规范为无offset UTC，DATETIME(3)。 | 已证实UTC转上海，保持同瞬间和毫秒；旧HTTP仍接收offset并回UTC，不改字段语义。 |
| performance_main | first_observed_at, last_observed_at | HTTP写UTC；旧sync生产直接接fact.collected_at，未统一按时区规范化，因此Projection/legacy历史unknown。 | 按record_source/设备域和证据分类；同一生命周期的水位、前卷退出与起止成组验证。 |
| performance_main | start_time, end_time | 人工/legacy pair优先；schema可接datetime；sync可保留naive或带offset；实际存储原时区unknown。 | 不推断旧人工值；先查业务来源/操作界面/历史配置，确认后转换。不得把unknown pair同新Shanghai observed pair直接相减。 |
| performance_main | manual_override_at | async_performance/async_lineage使用Python datetime.now()，跟宿主旧配置相关，unknown。 | 保留人工重量、操作者和原因；时间有证据才转换，未来改由统一上海DB时间源的有界任务处理。人工0仍优先。 |
| performance_main | created_at, updated_at | DateTime + func.now()/onupdate，实际DB时区unknown，默认秒精度。 | 先确认源DB时区，保留精度，不臆造毫秒；范围/precision变化先PM锁定。 |
| performance_main | production_date | 纯日期；HTTP明确从UTC瞬间转上海日期；sync直接fact.collected_at.date()，legacy含义待查。 | 不给DATE加8；逐来源核对上海跨午夜，必要修复日期派生需独立规则与证据。 |
| performance_process_temperature | record_time | HTTP UTC毫秒；legacy sync normalize_record_time接受naive保留，aware归一UTC。 | 按父域/来源分类；父ID、equipment、zone binary key与来源毫秒unique完整保持。 |
| performance_process_temperature | created_at, updated_at | func.now()/onupdate，DB原时区unknown。 | 有证据才迁移；duration为整数分钟，无时区转换，不写主用时。 |
| performance_process_tension | record_time | 同过程温度的UTC/legacy混合风险。 | 与父/自然键联合验证；min/avg/max及缺测不变。 |
| performance_process_tension | created_at, updated_at | func.now()/onupdate，unknown。 | 同上按实际DB证据。 |
| performance_process_speed | record_time | 同过程温度的UTC/legacy混合风险。 | 同上；不改速度量纲或补缺规则。 |
| performance_process_speed | created_at, updated_at | func.now()/onupdate，unknown。 | 同上。 |
| performance_mapping_receipts | sampled_at | HTTP UTC来源毫秒；result保存旧UTC字符串。 | 来源列与业务域一致迁移，result旧wire语义保持；恢复旧投递仍返回首次业务引用/结果。 |
| performance_mapping_receipts | created_at, updated_at | UTC_TIMESTAMP(3)。 | 按已证实UTC转换，不改actor身份。 |
| performance_mapping_observation_state | last_sampled_at | HTTP设备UTC水位；不可仅看水位替代历史事件证明。 | 停writer后与业务/回执同批转换；保留状态、fingerprint、result、父id；零活跃水位也要迁。 |
| performance_mapping_observation_state | created_at, updated_at | UTC_TIMESTAMP(3)，updated另UTC onupdate。 | 上海DB时间源与旧水位adapter同时采用，不仅改列默认。 |
| monitor_history_process_curves | sampled_at | HTTP UTC DATETIME(3)，legacy通常NULL；设备+来源毫秒unique。 | 只按证实来源转换；NULL保持；33项完整值和字段存在fingerprint保持。 |
| monitor_history_process_curves | created_at | HTTP创建省略时DB func.now()；legacy sync将aware collected_at转UTC、naive保留；旧GET以created_at日期查询，因此可能混合。 | 与来源时间区分；HTTP上海日查询从存储上海边界直接过滤，旧wire仍UTC；legacy日筛选兼容先确认。 |
| monitor_mapping_receipts | sampled_at | HTTP UTC来源时间。 | 同业务sampled_at迁移，ID/设备FK保护保持。 |
| monitor_mapping_receipts | created_at, updated_at | UTC_TIMESTAMP(3)。 | 已证实UTC转上海，旧result不改义。 |
| performance_split | created_at, updated_at | 人工/legacy func.now()，unknown。 | 附属审计，不在本A0改；若采用证明依赖，PM明确纳入精确时间整改范围。 |
| performance_push_down_record | created_at, updated_at, completed_at | defaults func.now()，completed_at有datetime.now()；unknown。 | 不因时区采用触发外部下推；审计保留并另定范围。 |
| performance_transform | created_at, updated_at, confirmed_at | func.now()/人工confirm；unknown。 | 重量谱系快照不改，确认时间按真实来源证据；另定范围。 |
| performance_lineage | created_at | func.now()；unknown。 | 谱系引用与有效重量快照保留；另定范围。 |
| monitor_history_energy_consumptions | created_at | func.now()，业务聚合/legacy时间unknown。 | 非新curve写入目标，不新增能耗写入/差分；如影响旧读面在专门时间整改任务处理。 |
| equipment_integration_receipts / performance_integration_receipts / monitor_integration_receipts | source_time, committed_at, created_at, updated_at | A0仅新声明，DATETIME(3)且无自动default；不存在本任务写入事实。 | future Service以规范Shanghai来源及一次已确认DB上海时间填入；committedAt首次commit固定，不因重放改变。 |
| performance_integration_observation_events | sampled_at, committed_at, created_at, updated_at | A0仅新声明；equipment+来源毫秒unique。 | 仅在G-T/迁移/接线后写入；事件先恢复原结果再裁stale，不从actor回执自动回填。 |

### 建议一次确认的兼容策略

1. **证据与分类**：另批精确非生产调查目标后，先只读核对实际schema revision、DB GLOBAL/SYSTEM/session时区、DATETIME精度、默认表达式、源码/历史writer版本和分域记录数。按列/来源将历史分类为已证实UTC、已证实Shanghai、其他已知offset、unknown；unknown维持冻结/隔离，不以 `equipment_id IS NULL` 单一条件推定时区。保留原时间/主键/hash对照清单与备份，不把真实行复制入公开仓。
2. **输入与存储**：新匿名入参offset只在边界规范一次到固定东八区上海（无历史DST/LMT变义），校验毫秒且不截亚毫秒。未来写MySQL前取Shanghai墙上值，API始终输出+08:00；提交/创建/实际更新时间来自已核实的数据库时钟，纯函数 `validate_source_clock(value,database_now)` 只验证注入时钟，不提供数据库ready证据。旧HTTP入参继续原offset接受/UTC wire，通过局部存储adapter转上海，读时再还原UTC wire，不改全局serializer或全局session时区。
3. **摘要与旧回执兼容**：原BE003/BE006 fingerprint包含UTC规范化、字段存在集合和旧算法。转换物理存储不应重新解释为新bi-json/v1；保留旧receipt的fingerprint/result和actor/sampleId，旧请求按原UTC算法验同后由storage adapter定位新Shanghai键；必要旧业务fingerprint需按原逻辑从同瞬间重算并与冻结旧摘要比对。新双摘要独立，包含规范Shanghai和存在键；不迁入旧actor身份、不承诺跨通道投递等价。普通文本/精确coil/zone/point键原样，FLOAT32容差与精确Decimal不因时间改动变化。
4. **键、水位与生命周期**：温控/drive/参数/curve来源键、三个过程record_time、所有receipt来源列和生产last_sampled_at须在同一停writer窗口转换/采用。先计算候选映射并验证唯一冲突、范围1000–9999/跨日、非零毫秒及父FK；不得仅移动主表或仅修改默认。旧production_date是纯日期按来源核对，不平移DATE。新生产事件索引不从当前水位/actor receipt假造历史；原有未完成投递以旧通道恢复，完成对账再切权威writer。
5. **Projection与人工优先**：原sync Projection仍拥有business/cursor/audit同事务。采用期每设备业务域只保一权威writer，新旧不可并发推动同一生产生命周期；cursor/raw collected_at不随业务列盲迁。若旧Projection继续写同列，其normalize_timestamp/record_time/生产fact时间与查询adapter必须一起纳入精确有界Revision；否则保持匿名关闭。manual_override_weight非NULL（包括0）及source/by/at/reason和effective/weight保持；起止优先 manual pair -> reported pair -> first/last，所有pair先统一明确时区，再按同瞬间相减，秒数0..2147483647；过程duration仍分钟，不参与时区偏移。
6. **精确迁移接链待冻结**：当前源码静态revision链为 d4e6f8a0b2c4 -> a6c8e0f2b4d6 -> b8d0f2a4c6e8 -> d2f4a6b8c0e2 -> e4f6a8b0c2d4 -> f6a8c0e2b4d6；本轮未执行Alembic current/heads/history，也不据此猜真实库。新migration的路径/revision/down_revision尚未获批；PM须依将来实际源码head和批准时区范围一次性锁定。A0只声明四Model及静态DDL，不创建Alembic文件、不启用create_all/seed。未来升级保护原64表/旧行，新增精确binary投递unique、业务事件unique、stream CHECK和设备/父/目标FK；禁止raw FK或ON DELETE CASCADE到业务/回执。
7. **分阶段隔离验证和采纳建议**：所有数据库验证先另批可丢弃MySQL8.4.6目标、账号/schema/端口/卷/操作。G-T前置只验证获批时间整改本身：合成旧UTC/Shanghai/unknown分类、迁移保留ID/值/精度、旧认证保护与UTC wire、旧fingerprint/回执、来源自然键/水位同瞬间兼容、上海跨午夜日筛选、人工0及已知时区pair用时、旧Projection/cursor/audit，以及宿主/容器不同系统TZ仍一致。精确整改范围、上述真实时间专项证据及采用/回退记录齐备后，才可申请解除G-T并按批准顺序进入A1–A3。**完整新业务B矩阵是A1–A3接线完成且A检查通过后的后置gate**：空库/合成旧行升级、新FK和unique、同异投递并发、RR旧快照、水位首次竞争、人工0两提交顺序、新生命周期退出晚到、flush/commit/丢响应恢复、raw到期后业务/最小回执恢复；这组新业务证据不作为尚未实施A1–A3的循环前置，仍须另批并由独立Verification消费。G-T解除不等于完整B通过，A0不代表整体qa_passed。
8. **回退建议**：默认关闭匿名入口并保留已确认业务/最小回执/事件证明，恢复唯一旧writer前完成水位/未完成投递对账。不得自动downgrade、删四新表或把全部时间减8；若必须恢复物理存储须另批反向迁移和备份恢复，按同一来源分类、冲突/毫秒/旧回执验证。历史unknown不能通过回退被自动“确定”。

同一待采用列若仍存在时区未定的历史，“冻结/隔离”不等于允许向同列写入上海值；在取得具体证据、获批处置并证明不会同列混存前，G-T继续不解除，不能仅保留unknown就宣告整列已采用上海存储。本提案不新增业务表或执行任何历史数据处置。

建议Owner先确认上述分类/旧wire兼容/权威writer停切及保留数据回退原则；随后PM锁定有界时区代码、schema与精确migration allowlist。该提案不新增本轮实施许可，真实库情况、采用日期、成本与运维窗口仍未知。


## 最终 A0 实现事实（初次交接，QA1 输入）

- `common/integration` 只承载有限纯信封/时间规范化、精确JSON/两摘要、typed回执和局部HTTP适配。没有业务字段表、任意SQL/动态handler或业务事务实现；全局响应/camelize未修改。raw JSON 在 DTO 前直接Decimal解析，重复key、未知/snake/null/bool/string/nonfinite/UTF8/技术数值域严格拒绝，64KiB与深度12有界。binary32摘要使用其精确十进制值。
- 八份data/请求DTO和八份owner-local结果DTO明确字段；完整温控十值、drive二十值、生产参数七项、生产十三观测、三过程min/avg/max、曲线十二整数+二十一FLOAT均归模块。来源引用保持必要小数精度；新业务时间统一固定东八区毫秒。未来时钟检查只有显式DB时间注入的纯函数，没有接真实DB时钟。
- 三模块integration配置新增12项公开默认关闭/空scope/unadopted键。设备集合最多256，精确case；producer为声明身份。八路不注入User/admin/actor=0，也不调用旧auth handler、Service或CRUD。关闭/空/越界403；准入合格仍503。即使把storageProfile设为其他字符串，也不能绕过A0未接线状态；无get_db或业务读取。模块enabled=False重组后新旧整组404。
- 三张永久最小回执Model及performance观察事件Model只加入metadata，身份producer/event以完整UTF8 VARBINARY(512)精确唯一，目标设备/父复合FK、stream CHECK和观察来源毫秒unique明确，无raw FK或级联。稳定result/sourceRefs/mapping/两摘要可独立持有；没有自动TTL、UTC default或DDL/seed。数据库时间列需未来Service注入已确认时间。只静态编译MySQL DDL，不把它当作migration已实施。
- 新 `BE010-A0` fixture明示68 metadata表、84公开配置、target_revision=null和models_only_unadopted_no_migration；旧C2/E/F/BE003/BE006生成器与冻结断言未改。新compatibility测试证明三个公开env的完整旧72项原文前缀SHA不变，仅新增12个默认关闭键。
- 旧认证route/schema/Service/CRUD、Projection、数据库会话、真实env、六条既有Alembic及依赖/锁文件没有更改。715个allowlist外backend/frontend公共文件逐文件对照entry无漂移（排除root协调者机械维护的backend PLAN pair）。原始并行AW/DS/DAA/SMA/FF/C#改动未回退。

## DEV self-check 命令、结果与精确归因（初次交接）

所有项目行为在排除真实dotenv、.venv、logs/data等运行资源的公开源码副本执行，复用正式 `backend/.venv`；使用合成占位process env，未安装/同步依赖。主命令为 `uv run --offline --frozen --no-sync python -c <guarded code>`，guard同时拒绝 `socket.socket.connect`、`sqlite3.connect`、SQLAlchemy `Engine.connect/raw_connection` 与 `AsyncEngine.connect`；ASGITransport只走内存，不监听socket。后续wrapper对继承helper的uv调用也强制UV_OFFLINE=true。完整精确argv、cwd、exit保存在各 `*-command.json`；以下摘要与源清单持久保存在本tasks，临时目录不是结论唯一来源。

| 检查 | 实际命令/输入 | 结果 |
| --- | --- | --- |
| 最终A0/公共合同 | `python3 /private/tmp/arch-be010-r1-a0-pxmh71r0/development/check.py handoff-final`；内部uv guarded `pytest.main(['tests/test_business_integration_contract.py','tests/test_business_integration_api.py','tests/test_business_integration_migration.py','tests/test_business_integration_compatibility.py','tests/test_module_contract.py','-q','-m','no_db','-p','no:cacheprovider','--basetemp',<development/pytest-handoff-final>])` | exit0；**180 passed / 51.86s**；最终源码输入49个backend变更文件逐字节与正式树一致。 |
| 八路HTTP/保护 | 上述整文件ASGI用例：全部八路关闭/越界403、unadopted/伪profile503；旧八POST无凭据401；三个模块关闭后新旧404；JSON错误真实413/415/422；DEBUG/yield退出Runtime错误500、DBAPI错误503均脱敏，成功不能提前发送 | 全部通过；无DB guard触发。 |
| 纯规则/回执 | 同组测试覆盖严格原文、数值域、毫秒/offset/历史DST不变义、来源精度、存在集合、两摘要、独立完整向量、补缺输入范围、stale/duplicate固定首次回执及原样键 | 全部通过；不证明任何真实commit。 |
| 命名profile | `check.py a0-profile-final tests/test_business_integration_compatibility.py -q -m no_db -p no:cacheprovider` | exit0；2 passed；包含84项/68表准备态标识、旧前缀SHA保护；最终180组也覆盖这两项。 |
| 相关旧整文件 | `check.py related tests/test_equipment_mapping.py tests/test_performance_mapping.py tests/test_monitor_mapping.py tests/test_mapping_api.py tests/test_mapping_compatibility.py tests/test_mapping_migration.py tests/test_equipment_temperature_api.py tests/test_equipment_temperature_service.py tests/test_equipment_temperature_config.py tests/test_equipment_temperature_migration.py tests/test_module_registry.py tests/test_module_dependencies.py tests/test_module_conflicts.py tests/test_module_admission.py -q -m no_db -p no:cacheprovider` | **exit1；362 passed / 4 failed / 232.50s**，不是全绿；精确归因见下表。 |
| entry失败对照 | `baseline_check.py baseline-four`加下表四个精确pytest节点，使用entry独立公开副本，相同noDB guard和uv环境 | exit1；**3 failed / 1 passed / 1.08s**；未改弱/skip/xfail任何旧断言。 |
| 静态/编译/DDL | `python3 <development>/static_checks.py`，内部uv guard下 `check_source(Path.cwd())`、`compileall` app/common/core/database/projection/scripts/tests及main/run/build、`create_app(testing=True)`仅composition、`CreateTable(...).compile(mysql.dialect())` | exit0；preflight、compileall、68表metadata及四表DDL静态编译通过。初次静态脚本仅导普通manifest模型，遗漏显式user/安全入口而在68断言exit1；补齐正常composition后通过，未修改产品绕过断言。保留初次static.log。 |
| 早期增量 | `check.py a0-first`、`check.py a0-refined`、`check.py a0-final` | 分别exit0：173 /175 /179 passed；最终180组替代这些早期输入作为handoff依据。 |
| 差异/链接 | `python3 <development>/audit.py`；`git diff --check -- backend CODE_INDEX.md plans/ARCH-BE-010-anonymous-business-integration/tasks.md`；新增/未跟踪文件另按entry增量检查空白和新增本地链接 | exit0；修复自有route签名尾空白后通过；无断链/范围外文件漂移；Git只读，无mutation。 |

| 精确节点 | entry事实 | A0当前事实 / 归因 |
| --- | --- | --- |
| `tests/test_mapping_compatibility.py::test_69_original_public_assignments_preserved_plus_three_empty_scopes` | passed；72项 | failed；84≠72。**本轮附加12默认关闭配置新触发**的冻结数量断言，不归入BE006既有四项失败。原前缀SHA检查仍通过，独立BE010-A0新增84项profile覆盖。 |
| `tests/test_equipment_temperature_config.py::test_three_examples_add_only_empty_scope_with_english_comment` | failed；72≠69 | failed；84≠69。entry已存在的冻结数量不适配，本轮再附加12项；未修改旧test。 |
| `tests/test_equipment_temperature_migration.py::test_five_revisions_58_60_58_parity_old_bytes_and_mysql_types` | failed；已有六条/f6，对比冻结五条 | 同一失败；六旧migration字节保留，本轮没有增加migration。 |
| `tests/test_equipment_temperature_migration.py::test_single_explicit_head_and_no_data_migration` | failed；源码head f6，对比冻结e4 | 同一失败；只读ScriptDirectory源图，不是Alembic current或实际库查询。 |

没有把“4 failed”整体说成历史失败，也没有把新增配置引发的固定72断言称为已修复。旧测试路径不在本轮可写面，本次保留真实失败并将命名profile和原文保护证据交独立Verification判断；若需调整旧断言，须PM给精确有限allowlist，不能由Development静默扩写。旧GET/PUT/DELETE全链运行、G-T真实数据及完整新业务B都未在本A0证明。

## 精确 source-map 与 Developer handoff（初次冻结，QA1 输入）

交付工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基础HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，本轮未创建commit/branch/worktree或执行Git写入。
批准spec SHA256仍为 `c33cd260dc74542f36436f31738e823734ae4bc75cf087a0dbb76c2d4c3dcaf9`。
实现源清单 `development/source-manifest.json` SHA256：`54e4bc6ad879843c2062cc3ccc6e2f679936cac585166decaf21c357ede5b7af`。
715文件保护映射规范JSON SHA256：`b1c2d53d0239e392e94d6f8bab1dea64c4da111b0def45c28e60de92727dccb8`，逐文件无漂移。
四表静态DDL SHA256：`5a9ef6f08a744a519c2b35edb9791e032e241128b840a55eefbfeab8ee426826`；不包含任何DDL执行事实。

以下为初次冻结的全部50个实现面变更及当时SHA256；另有本tasks（Development事实面）。六个计划/目录索引由root协调者维护，spec批准收据由PM维护，不列为本Development实施。

| 精确文件 | 最终 SHA256 |
| --- | --- |
| `CODE_INDEX.md` | `f063a54b864dd7480e25ddd284822052705e1811f769c29c510835e6f7effa99` |
| `backend/.env.docker.dev.example` | `f542e8deabdf79739f244ff6b8ed4d2a8662759a54fd50d4e92a36a05c0e02e8` |
| `backend/.env.docker.prod.example` | `5a1e73007c33154ddc42088178bce50bc98d0c2a6522023359d8a7d397ff4610` |
| `backend/.env.example` | `7729eb755e5f28502db2fe4692c7f0fd3c5966b458c56afc5c4e9f3995512286` |
| `backend/README.md` | `6f235fd75d806f7cabafe2337f714252b7016e4f3ae611ea185bbf248e3a7fe3` |
| `backend/README.zh-CN.md` | `e6551322ec8c80164970c9559dd9a23d8b8b299b212fa1774e77ee58909a639a` |
| `backend/app/MODULE_CONTRACT.md` | `b306c346693691a0daada456c87ed077dbba1a5d6ae477d62f05eed76e6ea6bf` |
| `backend/app/MODULE_CONTRACT.zh-CN.md` | `c596fa214bd581cb307550011f814a7abd7713cd3a75c6c85bcb4676f27c9f6d` |
| `backend/app/README.md` | `09495cbb98970dbe8803af8fac562f23446a0da1bdc4cfb56bc7703deae6fee1` |
| `backend/app/README.zh-CN.md` | `a72703450ab11809adaf641e41136855476fc57e57c608df19d3c6806aa8f487` |
| `backend/app/equipment/README.md` | `80c9b94fc04a2f9b2a2ddcba9cb05c6f12f2a3a54a5b505c38de1be6f73fd554` |
| `backend/app/equipment/README.zh-CN.md` | `e1b44fe1657b7bfa84b4492a7a81b613a306c3169309a7c53a991115658ad9ce` |
| `backend/app/equipment/api/integration.py` | `41b733f891109a37ac943763964b1b287857489e8c44ef6b5a78ea87a0428c62` |
| `backend/app/equipment/integration_config.py` | `e48c3bfa3dc684e1f21148979ac0215a5e30c3843b57dfda873ba1a07fd255f3` |
| `backend/app/equipment/integration_domain.py` | `1719341ca59d9fccc2065f4bdd4872b50cd2845cfbeb63c33b0ebe7b2ec0c9ac` |
| `backend/app/equipment/integration_error_codes.py` | `93d2480388570214d23484267e62a6ba6f83230a1fcc0a01113a419000e84d4a` |
| `backend/app/equipment/manifest.py` | `8a49408a7a3d156d298c6642a8ad97dfb3de7dfd4043536c29288078980cff05` |
| `backend/app/equipment/models/__init__.py` | `127befff83010a6f52a1442c1227f55678e4ddc115763cbb9b564205b431c4cf` |
| `backend/app/equipment/models/integration.py` | `1f07a65025c8741a428c6bfe180376bc3696af23478db3041b1bd304a79931d6` |
| `backend/app/equipment/schemas/integration.py` | `0b7c40913806792e0d37e538117b8964d4d8970c1c58dc83b8696ccbca88ffbf` |
| `backend/app/module_contract.py` | `197428341592b0d295534af458e83a376825e2d47df428495826d8309eab5ad3` |
| `backend/app/monitor/README.md` | `dbc3054e68a18bfbfb68aa81af69ea1374b1930d4d9a836403035e8a78a7b467` |
| `backend/app/monitor/README.zh-CN.md` | `468ecf44c6c03cd23174ab8e46d1686e3fbb072d5d1e95bfc4c530a6fccbe37b` |
| `backend/app/monitor/api/integration.py` | `29be7fadb1d8d66e07678b5de220750851bec21cc764967ea627909cfd83ffde` |
| `backend/app/monitor/integration_config.py` | `46226ec83aae860b0ebea8c2140ee80be950ff4f1048f072d2e0597487e46b1e` |
| `backend/app/monitor/integration_domain.py` | `de3acbe3c5137ea93bed59aa7985d0c6db46c5f34863d625607c30e3ab306e12` |
| `backend/app/monitor/integration_error_codes.py` | `5f24c7417322882c8743fc775284381be2461fe545e3c5ca8534a21a7189a303` |
| `backend/app/monitor/manifest.py` | `364d8c4d7800d220d7c68c5d55de3c21b91127aacc710b3efea6ff653e199ccb` |
| `backend/app/monitor/models/__init__.py` | `f0d8df47e2e9ef028e1f0d6779e97dc92bea82b8edfa619019bd3696d336d7af` |
| `backend/app/monitor/models/integration.py` | `a6b7e2ef95520d726bd8d1475b0cc840c315057bd9154e3454c9191e16994a20` |
| `backend/app/monitor/schemas/integration.py` | `b339066285466ca32ded19290404c0205afc8056065e37610683b7bc75997c46` |
| `backend/app/performance/api/integration.py` | `6eb3061792a8150295567b58457d791589b525ca35e04eff3a72ea7a2dfe2236` |
| `backend/app/performance/integration_config.py` | `5c8a9608d6cc8d2ae48e3ac762c2984e6d1d659fb96b0fcda8642e7e3caa27ed` |
| `backend/app/performance/integration_domain.py` | `b2471916956a5aab4a15038419ebeaa80596f6c6f95df07f7784c9848db6492d` |
| `backend/app/performance/integration_error_codes.py` | `893b5b1cf1cf849e947e1db778a9ff7653b0333d6a0303012c411e2753c9245e` |
| `backend/app/performance/manifest.py` | `e7c7d560b4888a6f66bf266f1d50bc1783e69194a80d16e6e7acbb6a0e1d1144` |
| `backend/app/performance/models/__init__.py` | `e29686e78b4aa6fe5132dacdf49aa4e5eb8982c70d6f10cf9911fc4ebc19c3a9` |
| `backend/app/performance/models/integration.py` | `408cdcfbea7af8b0875ac564ae6759377f354bd5e3102c86b5ee44663759f287` |
| `backend/app/performance/schemas/integration.py` | `69958d10b9c37d4454bb1aeb69cb1c1a0c6385602328e25d62be6a7f1379b0c1` |
| `backend/common/integration/__init__.py` | `e11a6effe140030f472a657e0ff9e10257ce955e750d3d738840380cfc56e613` |
| `backend/common/integration/canonical.py` | `9b91baf90aa5c5800294af920709a6e17d9c39fb126aa3704daf66bddc4ac583` |
| `backend/common/integration/envelope.py` | `6d2ecdc93930f9cfbc08f223bcde8db9f9911f8bdfc35d4ebc41d77e8a7c7621` |
| `backend/common/integration/http.py` | `7b8ea52ab23d9e79ed54161afa8ed25183ea87f9cbf42f1a7fb89d4dedee6f47` |
| `backend/common/integration/receipt.py` | `a8e103f993028cfd3acd1970a6ec62f9e20ff55db00165b23ab6918eb0e40dd7` |
| `backend/tests/module_admission_fixtures.py` | `811d9294da7467d7211a7d6801ea39b3850694e2aecf764f4553f66e796bd230` |
| `backend/tests/test_business_integration_api.py` | `023b60c41363acaf527f97fe32a3cd5e21750df35f5032a905ccff83d97abc9e` |
| `backend/tests/test_business_integration_compatibility.py` | `3ea504844dbb500415f4be5a893a1563514ba67925ba2f64f859f527e0bf9aeb` |
| `backend/tests/test_business_integration_contract.py` | `3ad80ecdea5ca2e1b66b43b1a7dc6bc4f5fef5b0fe2de74bfd5385c81e14e133` |
| `backend/tests/test_business_integration_migration.py` | `775ea79a5d1865e2591ceedafa5ff3cf66046c51475fc7516f8c402b61a60761` |
| `backend/tests/test_module_contract.py` | `33b29b1a3196ac61b5cb8776efef72c8f19816bcef6faaf57262c7019f7c5de2` |

### 限制、已知风险与下一 gate

- 本状态仅 **A0 developer_handoff（非终态）**。没有A1–A3业务Service/CRUD接线、没有写入/读回真实业务数据或持久回执，也没有完成整任务AC01–AC12；Development不授予QA verdict或Human Owner最终验收。
- G-T未解除，时区/迁移方案必须先交Owner确认；存在unknown同列时不能直接写Shanghai。精确Alembic文件/Revision/down_revision尚未获批；没有创建该文件，也不以当前源head猜真实库。不得自动接续业务写入或采用。
- 新匿名来源可冒用，scope只是部署准入；生产权威writer、旧UTC wire/fingerprint、人工0及历史未知来源仍须后续有界整改与真实证据。最小回执永久保留会增长；A0不提供容量/长稳/备份承诺。
- 相关旧suite4项失败真实保留，其中一项是本轮新增默认关闭配置触发的72数量断言。独立QA需明确区分A0范围、该兼容检查限制与整体G-T/B，不可把180个A0测试冒充完整任务通过。
- 实际fresh-context Verification由root串行启动（`agent_type=verification, fork_turns=none`），消费本r1/spec、tasks、正式源码、entry/diff、源清单和真实输出，独立写checklist。后续G-T时间专项证据先行；A1→A2→A3再按批准顺序；完整B在接线/A通过后另批精确MySQL目标与动作。Owner最终验收、发布部署、真实DB/Docker/API监听/PLC均是分开的后续gate。

### 临时资源与可回收条件

`/private/tmp/arch-be010-r1-a0-pxmh71r0/development/` 全部属本Development：`candidate/backend`为最终公开验证副本，`static-candidate/backend`为静态副本，`baseline/backend`为entry失败对照副本；`pytest-handoff-final`和`pytest-a0-profile-final`为显式basetemp，另有pycache/uv-cache/offline-bin/logs、构建/检查helper、命令JSON/日志、静态SQL、source-manifest/protected-audit/verified-input-consistency、development.diff及链接/空白证据。所有公开副本都排除真实env与运行数据，没有安装到项目环境。

早期pytest未显式basetemp所建的三份自有公开fixture已在测试退出后归集到 `development/legacy-pytest-runs/{pytest-25,pytest-26,pytest-27}`；原 `/private/var/folders/k5/gb101k5j2nddcgfgrtsn0p300000gn/T/pytest-of-jason/` 下对应25/26/27仅保留指向这些目标的别名以保持原证据路径可解析。详细归属见pytest-resource-relocation.json；其他pytest目录/共享pytest-current未修改。最早173轮的旧自动pytest副本已按pytest自身保留机制回收，必要结果已持久化于tasks和a0-first.log；未清理任务外资源。

上述资源仍供fresh Verification复核，当前不回收；Owner gate后由root协调者核实无运行/后续证据依赖再清理，包含三个自有别名与相应目标。无监听、数据库、Docker容器、真实配置、后台任务、分支或worktree资源需要收尾。root管理唯一long-task-notifier窗口，本Development未另开窗口或发送邮件。


## QA1 → Development rework-1（同一已批准 r1 A0）

已完整读取实际 fresh-context QA1 checklist（冻结SHA256 `01bb9dfe872b4a7a48f3c1fb2cf30a610049e603357489add716991aa6390ea0`）、spec/tasks及相关实现。QA1历史A0 qa_failed、整体G-T等qa_blocked仍由checklist权威记录，本Development不修改或覆盖该结论。

本次仅修F-QA1-001：sourceRefs>128应HTTP/code413及模块integration_payload_too_large，原128项仍按准入后503；在公共严格解析边界最小修复，不逐路复制；保留Schema max_length=128及所有普通格式/字段422、raw Decimal、体积/深度/退出/脱敏行为。先增加正常create_app composition的八路128/129及普通错误回归，复现失败，再修实现并运行完整A0相关文件和compile/preflight。

F-QA1-002：本tasks第5行已按project-governance Spec Bundle v2纠正为 `Allowed Writers: Development`。这项机械元数据不改变Human Owner实际批准/最终验收权。初次tasks和两项待改实现的原件保存在 `development/rework-1/before/`；初次DEV source-manifest与QA1所有证据只读保留，本轮不覆盖。新证据只写rework-1目录。

OpenAPI Decimal的number|string、自动200空schema与错误response schema均仍是A0未发布provider准备态的文档能力限制；本轮不以其冒充完整可消费接口、不扩大到DTO/接线修改。G-T、时区方案待Owner确认、精确migration与A1–A3/B等gate保持。


### rework-1 实际修复与 DEV self-check

F-QA1-001 的产品修复仅 `backend/common/integration/http.py` 三行：在严格JSON解析、原始Decimal/重复键/Unicode/深度/根对象检查之后，单独取得顶层sourceRefs；**仅它为list且数量大于128**时抛既有 `IntegrationPayloadError(413,"payload_too_large")`，复用模块局部适配输出。没有将所有Pydantic too_long转413，没有改变普通RequestValidationError的422处理，没有改变 `IntegrationEnvelope.source_refs` 的 `max_length=128`、公开符号、旧认证/全局异常、其他限制或任何Service/DB接线。

`backend/tests/test_business_integration_api.py` 新增40个正常 `create_app(testing=True)` / ASGITransport节点（8路×5情况），通过实际模块本地Settings懒依赖读取合成process scope，未覆盖该Settings依赖；只有get_db设置为一旦进入就失败的防护。128项为503 not_ready、129项为413 payload_too_large，引用均为唯一合法external_event且body<64KiB；未知引用字段、引用错误类型、sourceId为129字符分别仍422 invalid_request。逐项断言真实HTTP、body.code、message/errorCode与data=null。未启动lifespan/监听，未伪造User或业务提交。

F-QA1-002 的tasks第5行已固定为 `Allowed Writers: Development`；下方机械metadata审计检查通过。此处只是Development修复/自检事实，QA1失败历史仍保留，F项是否独立关闭由新fresh Verification裁定。

所有项目检查使用 `development/rework-1/source/{backend,frontend-js}` 公开副本，只按entry公共文件集合及已批准A0文件复制，不读取/复制真实dotenv、.venv、运行数据或ignored本机资源；复用项目原 `.venv`。自有run.py借鉴只读QA1运行脚手架，guard/sitecustomize及uv wrapper明确部署于本轮目录，仍然是 **Development自检**。`uv run --offline --frozen --no-sync`、synthetic process env、TZ=UTC、显式basetemp；sitecustomize和audit hook拒绝socket connect/connect_ex/bind/listen、sqlite3、SQLAlchemy和已安装DBAPI连接。wrapper向继承的uv子进程继续传递本轮guard路径与guard日志；本轮全部检查0 guard事件，无数据库/网络/监听操作。

以下命令共同前缀 `python3 /private/tmp/arch-be010-r1-a0-pxmh71r0/development/rework-1/`；各命令JSON/日志均同目录单独保留，不覆盖初次DEV或QA1证据。

| 命令 | 真实结果 |
| --- | --- |
| `run.py red tests/test_business_integration_api.py -k 'source_reference_limit and (128 or 129)'`（产品修复前，新增回归先运行） | exit1：8 failed /8 passed /96 deselected，78.37s；8个129项均实际422导致失败，8个128项为503通过，真实复现QA1。 |
| `run.py a0 tests/test_business_integration_contract.py tests/test_business_integration_api.py tests/test_business_integration_migration.py tests/test_business_integration_compatibility.py tests/test_module_contract.py`（产品修复后） | **exit0：220 passed，215.62s**。这是初次180完整A0相关节点加本轮40新节点的单次结果，不与红灯或旧轮次相加。所有原严格JSON/数值/摘要/回执/退出/脱敏/默认拒绝/旧八POST认证/模块关闭回归保留。 |
| `run.py surface --script inspect_surface.py` | exit0：preflight、全量相关compileall、正常composition/OpenAPI 428 refs零未解析、8条integration path、显式全模型metadata68、四表静态MySQL DDL及已声明目标unique/FK核对通过；即时composition模型63不冒充全量。未执行DDL。 |
| `metadata_audit.py`（最终handoff metadata） | exit0：spec/tasks共12项必要字段核对通过，tasks Allowed Writers精确Development。 |
| `audit.py` + 内部 `git diff --check -- backend/common/integration/http.py backend/tests/test_business_integration_api.py plans/ARCH-BE-010-anonymous-business-integration/tasks.md` | exit0：只两实现文件及tasks相对QA1变化；49个backend实现文件与测试输入逐字节一致；715个entry保护文件无漂移；新增链接/空白检查通过；spec/QA1 checklist/初次DEV manifest SHA保持。 |

旧14整文件及entry四节点本轮没有重跑：QA1已独立记录362 passed /4 failed及entry 3 failed /1 passed，且对应旧实现、旧断言、公开env/迁移在本轮全部未变。原有4项的精确归因继续保留，尤其新增12默认关闭键导致72数量断言失败，不称旧suite全绿，不弱化/skip/xfail。

### rework-1 最新精确冻结交接

工作树仍为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基础HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`；无Git写入/新commit。批准spec SHA保持 `c33cd260dc74542f36436f31738e823734ae4bc75cf087a0dbb76c2d4c3dcaf9`，QA1 checklist SHA保持 `01bb9dfe872b4a7a48f3c1fb2cf30a610049e603357489add716991aa6390ea0`。

当前完整50文件实现源清单为 `development/rework-1/source-manifest.json`，SHA256 **311d8f5f7faa92b8a69ad613e5aeffa21fd65b12823ae37783ba5648ef3152cf**；其中49个backend文件与当前自检源码副本逐字节一致，CODE_INDEX无本轮变化。715保护映射SHA仍为 `b1c2d53d0239e392e94d6f8bab1dea64c4da111b0def45c28e60de92727dccb8`。初次 `development/source-manifest.json` /SHA `54e4bc6ad879843c2062cc3ccc6e2f679936cac585166decaf21c357ede5b7af` 保留供对照，初次50文件表中仅下列两个after值由本轮更新；其余48项保持。

| 本轮精确变更面 | 当前 SHA256 / 范围 |
| --- | --- |
| `backend/common/integration/http.py` | `36092809df8246ff4395847e599217d761309d54b67244e0b84e9f4a74a689b6`；仅sourceRefs数量cap三行。 |
| `backend/tests/test_business_integration_api.py` | `18f596f51731cda0168a130982b81c300aee17c212ac78b746c6a928bf33f491`；40个正常composition边界回归。 |
| `plans/ARCH-BE-010-anonymous-business-integration/tasks.md` | metadata纠正、初次交接标识及本返工记录；本文件最终hash由root handoff另固定，避免自引用。 |

`rework.diff` 固定QA1→本轮的三文件增量；`development.diff` 固定entry→本轮完整实现/tasks增量；`audit-report.json` 固定输入一致性、保护文件/旧证据保留及0 guard事件。静态DDL本轮工具按显式四表顺序输出，artifact SHA见surface-report.json；与初次工具的表排序不同，不以跨工具字节差异冒充Model变化，四个Model源码hash均未变。

状态仅 **rework-1 developer_handoff**，不是QA verdict或Owner验收。默认关闭/unadopted与禁止业务接线保持；OpenAPI number|string、空200/旧422错误schema等准备态provider文档限制仍待后续接通/发布阶段补齐；G-T、unknown同列禁止混存、时区提案待确认、精确migration及A1–A3/B等gate完全保持。root随后实际启动新的fresh-context Verification QA2消费最新源码/本tasks/QA1失败历史/新证据，独立决定F-QA1-001/002，不将本220项自检称为独立QA或整体通过。

### rework-1 资源

本轮所有新资源在 `development/rework-1/`：before原件及before.json、source公开副本、guard/offline-bin/run/inspect_surface/metadata_audit/audit工具、red/a0/surface命令JSON与日志、显式pytest-red/pytest-a0、logs/pycache/uv-cache、OpenAPI/静态SQL/surface-report、metadata报告和当前source-manifest/增量diff/audit报告。无真实配置/数据，无默认pytest目录写入；旧DEV、QA1、root证据和初次pytest归集/别名未触碰。

所有本轮检查进程退出后供QA2复核，当前不回收；root在QA/Owner gate后确认无运行/后续/证据依赖再按归属清理。无监听/数据库/容器/后台任务/分支/worktree资源；未新开notifier窗口或发送邮件。
