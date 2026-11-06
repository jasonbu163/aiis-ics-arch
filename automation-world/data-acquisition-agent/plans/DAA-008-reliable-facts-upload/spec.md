Task ID: DAA-008
Revision: r2
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Human Owner精确r2 A0/A1范围与恢复写入例外批准pending；r1 QA2仍qa_failed，F-QA1-001开放；当前只修订spec，不继续实现，B实际HTTP/DS/MySQL/Docker及完整阶段C终验另批
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA本地事实的有界定时上传、可靠回执、补传与重启恢复及受控阶段C端到端验收
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: 本spec第13/15节；PM -> Human Owner精确r2及阶段/恢复风险批准 -> Development -> 新fresh-context Verification -> Human Owner最终验收；r1批准原文仅作第14节历史
Depends On: aiis-ics-arch::ARCH-BE-009 r1 owner_accepted固定事实provider；aiis-ics-arch::DAA-007 r2 owner_accepted本地采集基线
Related Task: aiis-ics-arch::ARCH-AW-008 r1；aiis-ics-arch::ARCH-BE-010 r2；aiis-ics-arch::DAA-002 r2；aiis-ics-arch::DAA-006 r3
Created: 2026-11-05 Asia/Shanghai

# DAA阶段C：可靠事实上传与新profile受控热回滚恢复

## 1. 给Human Owner的审阅摘要与当前效力

本次拟实现：在既有本地采集之后，按独立上报周期，把完整本地样本按后端已固定的事实合同上传；断网时继续本地保存，恢复后最新优先并公平补历史；对重复、丢回执、结果不确定和进程重启保留原投递身份，取得并保存可靠证明后才标记已上报。工作台集中控制采集与上报，上报与存储页维护一个后端目标、周期、队列及诊断。

端到端顺序固定为：新profile采集 → 全轮样本/manifest/context本地commit → 冻结HTTP batch → POST → 严格校验可靠ACK → 同一runtime事务确认 → latest/history人工核对。网络与后端失败不撤销已经完成的本地采集提交。

**当前为r2草案，仅修改本spec，不运行程序或数据库。** r1的A0/A1已经精确批准并形成正式源码候选；新的fresh QA2仍为qa_failed，唯一开放finding为F-QA1-001：ACK未提交事务真正崩溃后，RO预检需要SQLite回滚，却因只读连接拒绝，无法进入恢复。其余三项实现finding已关闭，普通8MiB回执持久化/rollback/空间预算已有有限通过证据。r2只新增新profile的初始化凭据及受控原生热回滚路径，沿用未变的上传合同和有效证据，不重做阶段B整套。当前没有r2批准、实施、QA或Owner最终验收；实际联调目标也未获批。

**新增且须明确接受的风险边界：** 仅对本版本从全新目录完成封存、凭据/文件身份均匹配的profile，在精确SQLite扩展错误776下，可先让SQLite原生rollback写入，再重新读取SQL元数据与完整账本。该有限例外不是“始终写前零写核验”；恢复后核验失败必须报告已经/可能发生恢复写入。凭据与SHA只证明本地格式/关联完整性，不是认证，不能完全识别恶意原地篡改、伪造journal或保持文件身份的备份恢复。未知、既有v2和未封存r1 v3不进入该例外。

为保持数据保护承诺，r2沿用r1限制：**只在新空隔离profile新建runtime SQLite v3；config SQLite仍为v2，样本/manifest仍为v2，采集配置/context仍为v1。既有v2/v2 profile继续原本地功能且上传不可用，不自动升级或纳入上报。** 仅本r2新建并封存的profile增加受控热恢复；不补封未封存r1 v3。上传旧历史、升级旧schema另行立项，没有第三个业务数据库。

普通入口继续`pnpm tauri dev`。所有启动均未连接、未采集、未上报；本次新增显式开始/暂停/继续上传，不实现程序启动后的自动采集或自动上传。后端目标、schema/时区/source采用、HTTP监听、DS实例、数据库、Docker以及故障/资源清理的具体操作，须后续逐项说明并批准。SMA实现、BE010八类业务API接线均不是本任务前置。

Human Owner本轮原话明确后端`ARCH-BE-009 r1`、`ARCH-BE-010 r2`已`owner_accepted`，并要求“按STD先出DAA阶段C实施spec”；实施需在spec提交后再次确认。本任务没有Parent Task ID，不继承其他任务的范围批准、数据库动作或最终验收。

## 2. 证据基线、合同优先级与来源固定

### 2.1 已验收与当前缺口

| 表面 | 当前只读核对事实 | 本任务边界 |
| --- | --- | --- |
| [DAA-007 r2核验及Owner接受](../DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) | 受控DS/S7到本地双SQLite阶段B已接受；8590样本/4295轮与原profile保留；历史证据限制和来源未明事项继续跟踪。 | 使用其源码能力，不重做导入/命名/分组整套验收，也不打开这些历史数据库。 |
| [当前样本v2](../../src-tauri/src/domain/local_sample.rs)、[runtime持久化](../../src-tauri/src/infrastructure/local_store/runtime.rs) | r1已实现六投递表/冻结/ACK；sample_delivery仍为pending/acknowledged，原格式不变。 | r2只补恢复，不重写原点位体、原序号和完整轮语义。 |
| [SQLite schema/preflight](../../src-tauri/src/infrastructure/local_store/mod.rs) | r1已有v2/v2、v2/v3矩阵；真实hot ACK事务在RO预检失败。 | 只给r2新封存profile增加精确776恢复例外；不放宽未知/旧库或ALTER接管。 |
| [现有bootstrap](../../src-tauri/src/commands/local_acquisition.rs) | r1已有v3上传能力和停止态；原生视觉/实际HTTP未验证。 | 恢复后检成功才放行业务；浏览器/v2保持不可上传，默认停采停传。 |
| [BE009 r1最终验收](../../../../plans/ARCH-BE-009-backend-facts-integration/checklist.md) | 独立源码及两轮隔离MySQL8.4.6验证完成，2026-11-05 Owner接受；事实独立七表，专用运行资源已收尾。 | 固定消费三API；不修改后端、旧monitor表或接口，不把已回收测试目标当持续HTTP环境。 |
| [BE010 r2最终验收](../../../../plans/ARCH-BE-010-anonymous-business-integration/checklist.md) | 八类匿名typed业务入口已接受。 | 仅未来SMA/第三方业务投递背景；DAA不调用、不映射、不以业务入库作为本阶段C前置。 |
| [AW008需求](../../../../contracts/demands/automation-world-facts-integration.zh-CN.md)、[DAA详细设计](../../../../docs/AIIS_DAA_Detailed_Design.md) | 提供最新优先、历史补传、可靠确认与生命周期语义；AW008文档QA与Owner终验分层。 | 具体wire/摘要/限额以已验收BE009 provider为准；AW008未终验不新增为本spec起草或源码A的阻塞，也不代登记其验收。 |

### 2.2 固定provider材料

公开版本固定`plc-facts/v1`、`daa-local/v2`、`pf-json/v1`、`pf-cursor/v1`。下列SHA-256于2026-11-05直接读取公开源码/合同取得；不依赖tmp、部署URL或真实DB。provider pins在handoff须重算一致，语义变化返回PM。表中最后三项DAA schema/local_sample/Cargo.lock是r1实施前before pins；schema和Cargo.lock已由获批r1合法修改，r2以第2.3节after候选为起点，不因与before不同而回退。

| 根目录相对路径 | SHA-256 |
| --- | --- |
| contracts/published/http-api/plc-facts-v1/openapi.json | bec51c468ff64a8d34dbb0a2faab2fda76d2b33769ee5ef066dc81e8bca274ee |
| contracts/published/http-api/plc-facts-v1/schema.json | 60d0e285bebb1c6d24588f4d5f90e7bdd85ed0befdeab9d0b93445a94f45d4b3 |
| contracts/published/http-api/plc-facts-v1/vectors.json | 9a5ae0e90a006a7e450ec12557868e9eda20690f4853b6ae29aea2bdf714e782 |
| backend/app/plc_facts/canonical.py | c48f0957b65c4348dec4fdfd8d76d9bd29891355b302b4d189b81cad7bbf1cd9 |
| backend/app/plc_facts/source.py | a7fd7ef75149e251a47d838fbd57db00c540c7990d1f64f3d9e9a67edc1489d8 |
| backend/app/plc_facts/schemas/receipt_out.py | 14d37df54acbef48fe55eedc9d26b1c3512a422f9f4bdaac45b304b651979e40 |
| backend/app/plc_facts/services/async_ingest.py | 91b15e1842847db6612fc83753a9a9fac2caaa44a57c655ee223a12685a9a60f |
| plans/ARCH-BE-009-backend-facts-integration/spec.md | 26121323384f2b8fd590921f53c477d759b564cf5214078c05834496a4884f48 |
| plans/ARCH-BE-009-backend-facts-integration/checklist.md | d3bd116083aaf78a91c971ae1167f383ea15be021abaf9c20d15f7bc3469744e |
| plans/ARCH-BE-010-anonymous-business-integration/checklist.md | 2c5cf0efdee2ae010976873228df757b5a70585521b3719be5871f39f93c9368 |
| automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs | c8c2189bd24bc427833fbe98d2a6b8b8c1f99a00e6b7e64a46e3afe26f922d81 |
| automation-world/data-acquisition-agent/src-tauri/src/domain/local_sample.rs | 8de692e6b4ebdbce23685ed83a98ed3c5ada2783bbee2c74dbf5219677355677 |
| automation-world/data-acquisition-agent/src-tauri/Cargo.lock | 0fd260eb50278b28e6b3a2e016dcc18ed6a4030b0c95a2a828db8ddcbfc05a61 |

后端Owner接受对应固定B候选`2532d8423c73f0e9c0a7ac42d616014b2ca09419588cd07a0218bd4ce080cafb`；其checklist已区分148实现原样、后续9份Markdown变化与当前HEAD。DAA消费上述具体合同/源码，不声称整个共享工作树等于旧候选。机器JSON只读消费，不复制出可漂移的第二份provider合同。

### 2.3 r1失败保留与r2精确起点

完整获批r1已由主协调逐字归档为[evidence/r1-approved-spec.txt](evidence/r1-approved-spec.txt)，62138字节、SHA `382afd6168983fa377d5a4729bbc566e6bd49cb3142590504de353712b342eae`。它是只读、非canonical审计附件，不是第二活动spec。当前唯一spec为本r2草案；tasks/checklist保持其真实r1 Revision，PM不代改实施/QA事实。第14节原文中“当前/下一角色”为r1登记时点历史，不能解释成r2批准。

| 固定材料 | SHA-256 / 有效事实 |
| --- | --- |
| [r1 Development](tasks.md) | `287b64181b1420e888e5c4aa9d296793963500263381ff774b35487e12f1070f`；dev_blocked/部分交接，正式源码树。 |
| [QA1历史及QA2结论](checklist.md) | `eec8b82f5b444a7b125b9d4f76938ed1d4356c3ff1a790e32d4aa090f7422e84`；QA2 qa_failed，F002/003/004关闭，F001开放；原QA1 SHA `eab00b347a3b81350f64d5073f1f05bd333fdf8e6f7ba0eaa42076b545ab63f1`。 |
| candidate-r1-qa1-rework-manifest.json | `/private/tmp/daa-008-r1-a-xsm2qlrl/development/`；`df68c4eba7ae5352b1decb799cca762b3450a49c1ac085a26665d91bca7e232e`；52有限源码面、45累计改动。 |
| handoff-qa1-rework-receipt.json | 同DEV目录；`e0682b033925d48cf3aa131e42b5feb894813d6ae033adcb0029a3bc3a65ba05`；冻结`2026-11-05T11:33:12.048185+00:00`；entry HEAD `0465f45ced6a2c8f8ca271b8bbf71f9eabc99de9`。 |
| qa2-handoff-receipt.json | `/private/tmp/daa-008-r1-a-tww7ssar/`；`0680848248566d270a1297fe0be6c0f89b2042f58ca86bb45f9c9a0069dbeb31`；实际fresh角色`/root/daa008_verification_2`，52源码/spec/tasks未改。 |

关键失败、数值、SHA及结论已经持久化在tasks/checklist，不只依赖临时收据。DEV/QA1 hot journal/before、QA1反例、最终候选及DEV/QA2 27KiB/8MiB原响应和journal保持证据依赖；不重开、不封存、不恢复或复用这些SQLite。r2测试只建新r2目录。provider pins不变，获批DAA源码after不是漂移。

r1 AC12已有合法256点/32DB/32片路径、逐typed字段保守编码界及8MiB同语义JSON空白资源上限的真实保存/普通SQL rollback与预算证据；最后一项不是provider普通输出。它们不关闭真正hot重开失败。未变r1/QA2证据继续沿用，r2只补恢复及触达检查，不重跑阶段B、Backend或DS整套。

## 3. R01：阶段、批准与数据保护

| gate | 可交付/可执行内容 | 进入条件 |
| --- | --- | --- |
| 当前PM r2 | 唯一spec修订及主协调四处DAA PLAN/catalog机械索引 | r1 QA2失败后按workflow准备新Revision；只写spec，保留已有r1 tasks/checklist，不编译/测试/HTTP/SQLite/Docker/DS。 |
| A0源码与纯检查 | 第10节有限新增恢复机制/最小接线、手册和DEV self-check；未变r1代码不重构 | Owner精确批准r2 A0及R02恢复风险例外后才新增实现；不因此获得数据库或网络运行授权。 |
| A1合成SQLite验证 | 新空r2目录中的合成存储、初始化/凭据/真实崩溃/恢复/容量增量 | Owner明确批准本r2第11.1节；r1批准不自动涵盖新信任边界。原路径/env/历史及r1失败fixture排除。 |
| G-B / B受控联调 | 新隔离DAA profile、专用Backend目标、受控DS与真实HTTP的必要增量验证，Owner原生操作及独立核验 | A候选固定后，另批第11.2节精确环境/目标身份、数据库/schema采用、Docker/监听/DS/故障及收尾动作。当前没有这些操作的批准。 |
| 阶段C完成 | A0/A1与获批B均有实际Development、fresh-context Verification及Owner最终接受 | A-only不记阶段C完成；SMA、生产、真实PLC、自动启动、长期SLA与部署另项。 |

现有profile的路径、文件内容、schema、样本状态和私有回执均为保护对象：本任务不发现/扫描用户目录、不导入、不复制/挂载旧profile到测试区，不改用户.env/default profile选择，不做旧UTC/v2数据迁移。兼容验证只用本任务从零创建的合成v2夹具。对现有数据的“不动”不能由程序开启后无感升级来替代。

## 4. R02–R04：双库增量、样本与固定HTTP合同

### R02. 新空profile的精确版本方案

保持`<DAA_PROFILE_DIR>/local-acquisition-v1/{config.sqlite,runtime.sqlite}`和既有profile锁。config.sqlite application_id/PRAGMA user_version/instance_metadata/schema_migrations均保持现有v2；采集配置schemaVersion=1。**只有新空profile的runtime.sqlite显式建v3**：application_id沿用本应用runtime标识，user_version/runtime_metadata.schema_version/schema_migrations均为3；time_profile仍为`asia-shanghai-rfc3339-ms-v1`。样本与manifest的schemaVersion仍为2，原SHA算法不变。

preflight精确区分：v2 config+v2 runtime为旧本地能力；v2 config+v3 runtime且instance/time/结构完整为新可靠上传能力。旧/未知profile保持RO-before-write；其他组合、单库、WAL、symlink或未知版本写前拒绝。v2/v2不执行投递DDL/升级，不写投递设置，原本地能力保持。唯一新增例外为下文R02.1–R02.5：本r2新建封存且绑定有效、精确776的profile可先native rollback再SQL重验；不能用于旧v2、未封存r1 v3或未知结构。半初始化不自动修补/覆盖，新空封存严格按下文顺序。

新runtime v3保留原表与sample_delivery的pending/acknowledged二态，新增六张投递表，普通rowid/明确列与索引，不用ATTACH、跨库事务、触发器或第三库：

| 新表 | 持久事实与约束 |
| --- | --- |
| delivery_settings | 单例id=1，settings_revision CAS、targetId、规范后端origin、上报周期、目标交接引用/合同pins、允许的PLC声明及已核来源材料；JSON≤64KiB。初始无目标、不运行。不是采集Configuration的一部分，不改变configuration_contexts原文/revision。 |
| delivery_cycles | cycleId唯一，原manifest/context SHA、固定transportManifest/cycleDigest、targetId；引用原轮与完整样本集合。生成后不可改；定义原证据缺失/冲突为blocked。 |
| delivery_parts | unique(sampleId,part)，原source SHA/contentDigest、parts/pointIds、状态、当前batchId、可靠ACK关联；完整预期集合由delivery_cycles固定。不能把同一片同时放入两个未终结batch。 |
| delivery_batches | batchId唯一，targetId、settingsRevision、requestDigest/bodySHA、完整冻结UTF-8请求、成员集、parent关联/深度、state/attempt/nextAttemptAt/最后错误；新建冻结一次，重试不改身份/原材料/创建时间/分片。最多8个未终结冻结批。 |
| delivery_receipts | batchId唯一，成功或可靠终结拒绝的原响应UTF-8/SHA、receiptId、请求摘要、提交/证明截止及逐成员结果；先完整验证再同事务保存。每条响应≤8MiB；不会将GET结果写成ACK。 |
| delivery_events | 最多500条脱敏投递状态事件/诊断，稳定英文key和上海日历时间；与采集事件区分，普通每点值不落日志。 |

ACK、delivery_parts、sample_delivery及sample_references在**同一runtime短事务**提交，消除第三库ACK补偿。未终结batch、unknown、合法派生依赖通过sample_references保护相关样本/整轮/context。全固定片已有相符可靠证明才将该sample标acknowledged；不改payload/manifest/context原文、SHA、ID、sourceSeq、value/quality/time。单片已提交、整个sample全片已提交、整轮complete和qualityGood分别表达。

新profile的投递配置保存使用独立CAS，不生成PLC采集版本，也不重写历史context。后端origin/targetId/合同/source声明改变时，若有未终结投递则拒绝直接切换并显示受影响数量；本r1不提供跨后端搬运、人工“标已传”或丢弃旧队列按钮。

### R02.1 新profile凭据与静态schema指纹

仅对支持Unix文件身份的**新空目录**，在`local-acquisition-v1/`中增加以下辅助文件；不是第三个数据库、配置版本、上传ACK或认证凭据。旧v2和未封存r1 v3永不自动补封，包括本任务已有合成fixture。

| 文件 | 固定格式/限额 |
| --- | --- |
| `profile-contract.json` | UTF-8严格JSON，无BOM/重复键/未知字段/尾随内容，总计≤32768字节。outer仅`formatVersion:1,payloadUtf8:string,payloadSha256:string`；inner原UTF-8≤16384字节，SHA为其原字节的`sha256:`加64位小写hex，不重序列化后核。仅初始化完成时一次安装，不随业务重写。 |
| `.profile-init.json` | ≤8192字节严格JSON：`formatVersion:1,initId,canonicalStoreDir,createdAt,phase:"initializing"`。存在即初始化未完成，不凭内容续跑/恢复/认领。 |
| `.profile-contract.installing` | 与待安装outer完全相同、≤32768字节；存在即拒绝正常打开/恢复，即使最终credential也存在且内容相同。 |

inner固定字段：`contract:"daa-profile-recovery/v1"`、UUID `initId/instanceId`、上海`+08:00`且最多9位精度的`createdAt`、`timeProfile:"asia-shanghai-rfc3339-ms-v1"`、`identityProfile:"unix-dev-ino/v1"`、`canonicalProfileDir/canonicalStoreDir`、各自目录身份对象`profileIdentity/storeIdentity`（均仅`dev,ino`）、`pageSize:4096`、`journalMode:"delete"`、有序`stores`数组。stores恰为config/runtime两项，每项仅`role,fileName,applicationId,schemaVersion,schemaFingerprint,fileIdentity:{dev,ino}`：文件名固定`config.sqlite/runtime.sqlite`，applicationId分别`0x44414143/0x44414152`的JSON整数，版本分别2/3。dev/ino用规范无符号十进制字符串，inode非零；两库普通文件且nlink=1、身份不同。路径来自当前显式profile，绝对canonical UTF-8、各≤4096字节，无控制字符/NUL/父穿越/既有symlink；不依据凭据另找目录。字段/顺序/格式/时间/身份不符即拒绝，SHA不称签名。

指纹算法固定`daa-ddl-sha256/v1`：从编译内已知config2/runtime3 DDL取所有显式CREATE TABLE/CREATE INDEX/CREATE UNIQUE INDEX，组成`(type,name,sql)`记录。type为小写table/index；sql与现有verify_structure一致，仅逐语句trim和去终止分号，不另规范空白。按(type UTF-8,name UTF-8)排序；SHA输入为UTF-8 `daa-ddl-sha256/v1`加NUL，随后各记录三个字段依次加4字节大端UTF-8长度及原字节。实际sqlite_schema记录必须与已知静态集合逐项相等；额外表/索引/trigger/view、缺列/约束拒绝。排除`sqlite_`内部对象/sql=NULL自动索引（约束已在TABLE DDL）、INSERT、行值、计数、seq、mtime和动态文件SHA。凭据hash不授权未知DDL；独立golden字节及缺约束反例核算法。

### R02.2 新空目录封存时序与失败关闭

产品及测试共用受控factory：先原RO预检，再取得现有ProfileLock；任何初始化/恢复写入前必须已持锁，并持续到存储关闭。旧/未知库仍按原规则写前拒绝，无测试免锁/免凭据恢复路径：

1. 原RO空目录预检；取得profile独占锁后复核canonical/dev/ino及真正为空。锁文件仍在profile根，不把任意已有store内容当空。新sealed store目录0700、辅助文件0600，无新env/feature/启动命令。
2. 先核初始化容量，用create_new/O_EXCL及无symlink保护创建sentinel；`write_all → sync_all → checked close → store目录fsync`全部成功后，才允许第一条建库DDL。initId与最终凭据一致。
3. 仅创建两个不存在的SQLite文件，按r1完整config2/runtime3初始化并分别commit；DELETE/EXTRA及固定参数不变。任一步失败保留sentinel/原件，不回删或重做已成功库。
4. 检查commit及SQLite显式close结果，关闭全部连接后同步两库/目录；完整RO核版本/实例/时间/DDL/完整性及关联，再关闭RO。写/sync/close/校验失败都保持未完成，不启动日志/业务actor/HTTP。
5. 读取最终目录/两库身份、已知指纹，生成inner原字节和outer并自检。create_new写staging，文件fsync/checked close、目录fsync。原始DB文件FD一律在SQLite连接前关闭，避免Unix关闭同inode FD释放其advisory lock。
6. 同目录硬链接`installing → profile-contract.json`原子no-replace安装；目标已存在即拒绝，不rename覆盖/truncate或沿用目标。安装后目录fsync，删除本次staging名字再fsync，最后删除sentinel再fsync。任一步失败不称完成；仅安装短阶段允许两凭据名字共用inode，正常启动要求nlink=1。
7. 重新完成全量RO preflight和绑定复核，才进入原正常打开/恢复/日志/worker。文件系统不支持可靠no-replace、目录fsync或身份读取时失败关闭，不静默改用较弱协议。

任一sentinel/staging、安装中断、损坏/冲突凭据或异常文件组合均保留并拒绝，不自动续装/认领/清理；处理另需明确运维批准，无通用修复UI。辅助文件最多3个、逻辑总量≤73728字节；初始化先预留256KiB分配预算并核实际allocated bytes，超过则拒绝。该预算计入现有初始化/物理空间及**既有32MiB恢复预留之内**，不另增配额、不绕过旧页journal/维护预算。

### R02.3 打开矩阵与精确错误门禁

| 材料/结果 | 固定行为 |
| --- | --- |
| 旧v2/v2或未封存r1 v2/v3，无hot | 保持原完整RO准入/锁/复核及正常功能，不写凭据或升级；未封存v3保留r1上传能力，无r2 hot保证。 |
| 旧/未封存/未知profile SQL读失败 | 原样拒绝；目录归属、本应用头或776都不授权补封/恢复，既有失败fixture保持。 |
| 有辅助文件/凭据 | 必须完整检查，损坏不得降级当“无凭据”。sentinel/staging存在拒绝；有效sealed绑定在cold/hot均检查。 |
| sealed且RO成功 | 仍完整SQL合同/绑定和锁内TOCTOU后正常打开，不凭credential跳过RO。 |
| sealed且原始扩展错误`SQLITE_READONLY_ROLLBACK=776` | 全部R02.4门禁成立并已获Owner批准才允许一次native恢复；格式化错误前保留`SqliteFailure.extended_code`。 |
| `SQLITE_READONLY_RECOVERY=264`或其他READONLY/BUSY/IO/CORRUPT | 不恢复；禁止匹配“readonly database”文本或只用primary READONLY。WAL/SHM、双journal、链接/身份漂移拒绝。 |

### R02.4 锁内native rollback与恢复后重新准入

先关闭失败RO连接和全部原始文件FD，核凭据原SHA/严格字段/已知指纹、目录canonical/dev/ino、两库普通nlink=1/dev/ino，以及100字节SQLite头的magic/4096页/读写版本1/applicationId/user_version。WAL/SHM或WAL头、任何symlink/hardlink、未知/损坏头、缺库、两个`-journal`同时存在均拒绝，不猜恢复顺序。单journal须为失败库同stem的普通nlink=1文件；非hot同伴库须完整RO核身份/时间/schema并关闭。应用不解析journal记录。

首次RO前后保存该受控文件集合的stat/长度及流式SHA候选；取得现有ProfileLock后完整重做并要求与候选一致，RW前最后复核目录、双库、凭据、journal及无WAL/SHM。漂移立即拒绝，不能重新取hash悄然接受。所有原始DB/journal FD在SQLite前关闭，同进程不在SQLite持锁时另开关该DB的原始FD。此门禁降低合作进程竞争风险，不承诺消除恶意非合作TOCTOU。

仅以`SQLITE_OPEN_READ_WRITE | SQLITE_OPEN_NO_MUTEX`打开失败的已存在库，**不带CREATE**；使用当前bundled SQLite/原生默认VFS，busy_timeout=1000ms，以固定只读`PRAGMA schema_version`触发最小pager访问。SQLite可执行自己的rollback；无应用DDL/DML、改journal_mode、ATTACH、immutable/nolock、自定义VFS或手工重放/截断/删除journal。至多尝试一次，busy/IO即停止；1000ms是锁等待预算，不称OS磁盘I/O硬截止。失败不清理候选journal。

检查native连接close并关闭后，重新完整RO核双库：版本/实例/时间/静态schema、integrity_check、foreign_key_check、来源/配置/activation关系；原payload/manifest/context SHA和成员关联、冻结bodySHA/requestDigest/成员、receipt与parts/sample_delivery/references原子不变量。稳定索引每页≤100行，不载入全部历史；合法activation中间态只交原既有规则，不猜修。后检失败不启业务、不补表/改版本或人工ACK。native恢复可合法改变DB文件SHA并移除journal，必须另建明确的**恢复后preflight基线**，保留前后证据，不能悄然忽略prehash差异或称文件未写；原样本内容SHA须守恒，A1另用durable before逐项核对。

全部后检/锁内复核成功后才允许原activation/delivery恢复、clean_exit和产品日志等事务；inflight按原规则转unknown，冻结batch/原请求不变，停采停传待显式继续。恢复前再次退出，下次重走同门禁；native恢复后RO前退出，如journal已消失则走sealed cold路径，但仍须执行本节同等级完整账本后检，包括原文/SHA、冻结请求和ACK原子不变量，不能只核少量metadata。Stores只能经该factory在真实锁下初始化/恢复，测试cacheflush/_exit也用同路径，无免锁旁路。

成功native恢复后若后检失败，明确报告“已执行原生恢复写入，业务准入失败”；native操作本身IO失败则报告“恢复写入可能已发生”。完整后检之前只输出脱敏stdout，不先建持久日志/actor/HTTP。凭据/SHA/文件身份不是认证，不能完全证明恶意原地编辑、伪造journal、保持inode的备份恢复或非合作进程，Owner须明确接受此风险。

### R02.5 平台、复制及回退

| 平台/材料 | 确定行为/限度 |
| --- | --- |
| Unix身份实现 | 现有`cfg(unix)`使用dev/ino/nlink、目录fsync和硬链接no-replace；本次只在实际macOS/arm64做A1。Linux走同机制，但Linux原生/文件系统/掉电证明未取得，不报告跨平台通过。 |
| 不支持该身份协议的平台，如Windows | 保持r1严格cold行为：新空仍可建config2/runtime3、无sealed凭据及776 fallback；既有未封存无hot仍可RO准入，不使普通启动全面失效。不伪造Unix身份，不声称hot保证；已有Unix凭据不能忽略/降级，只能拒绝并保留。 |
| 复制/移动/跨平台/备份替换 | 路径/目录/两库inode改变使sealed拒绝，无自动重绑/迁移；保持inode的原地恢复未必能检测。不得复制真实profile测试，拒绝反例仅用本次新A1合成夹具。 |
| 代码回退 | 不改版本/删marker/journal降级，不让旧二进制继续使用新sealed profile；新资料保留，回退用原兼容profile/版本。重绑/备份恢复/升级另批。 |

### R03. 唯一事实载体与原文约束

消费[原typed wire](../../../../backend/app/plc_facts/schemas/batch_in.py)和[source规则](../../../../backend/app/plc_facts/source.py)。DB样本包仍是一轮一个PLC/采集组在某DB的原SamplePayload；HTTP batch是可容纳若干DB包/固定片的传输容器，两者不是同一个层次。跨DB依序读取不冒称PLC物理原子帧。采集点enabled仍代表需上传的事实集合，不新增第二套上传点开关或自由JSON编辑器。

例如PLC-A同一组读DB71与DB88，得到两个原sample与一份完整轮manifest；如果实际编码在预算内，可一次HTTP携带这两个包。PLC-B也有DB71时是另一plcId的原sample，可放后续HTTP或同一有界batch，均不冲突。用户只配置后端地址和周期，上传JSON由固定合同生成，预览只读。

必须读取同一已提交轮的完整原payload/manifest/context，先核三者原SHA和关联、expectedPointIds/样本DB/定义/来源/序号/时间；只读原字符串作为payloadUtf8/manifestUtf8/contextUtf8。原UTF-8 SHA加`sha256:`前缀用于wire，原库无前缀SHA不改。每个失败点也保留definition/observedAt/bad/null/reason，不能删除、补零、替换旧good值；当前ASCII CHAR/STRING和有限PLC标量范围保持。

sourceSeq始终是原PLC代次内的十进制字符串，不转JavaScript number，不因重启、补传、组周期、目标设置变化而重置。sampleId/cycleId/pointId/plcId/instanceId/sourceGeneration/revision使用原值；中文sourcePath与原命名不重新转换，传输不替点位重命名。

原context解码后>1MiB、manifest>128KiB、payload>512KiB或无法生成合法最小请求时，该轮明确blocked并保存原因/原引用，其他PLC/轮次仍有公平机会。**不能裁剪source文档/树/失败点、重编码历史或另造“精简context”绕过合同。** 可显示需要后续配置/合同处理，不将不兼容轮退回采集线程无限重试。

### R04. 版本、规范摘要、固定分片与请求限额

固定三API：POST `/api/v1/integration/plc-facts/batches`，GET `/api/v1/integration/plc-facts/latest`和`/history`。只通过Rust HTTP adapter调用；不连MySQL、不写旧monitor表、不调用八类业务接口、不修改后端合同。新接口匿名；scope/source binding是准入而非身份认证，原前端/管理API权限保留。

pf-json/v1不能用serde_json默认f64 round-trip替代：原JSON数字须保留原数值token，按十进制符号/系数/指数精确展开，零统一0、不用指数、去不必要小数零；UTF-8字节顺序排序对象键，控制字符用小写`\\u00xx`，仅必要引号/反斜杠转义，不做Unicode normalization。重复键、BOM、非法UTF-8/surrogate、NaN/Infinity、深度>20、>256有效数字或指数绝对值>1000均拒绝。实现采用serde_json的raw_value/arbitrary_precision能力与明确的无损数值表示/重复键检查；不引入Python runtime、机器浮点canonical或第二份合同生成器。

摘要域分别为原文SHA、`sample-part`、`cycle`、`batch`、`definition`、`definition-set`；按provider的`plc-facts/v1 + NUL + domain + NUL + canonical`生成，不能混用。nameMode省略/空值、definition只取规定字段、context定义集包含停用点、requestDigest排除自身并规定数组排序，均直接对齐source.py；合法原时间文本/原points不改。**先通过固定vectors及独立反例，再接任何HTTP。**

分片固定：原pointId按UTF-8字节序，下一点使本片超过512点或规范points 128KiB则开下一片，最多16片；sampleId不变，片身份为(instanceId,sampleId,part)，part从1开始。每片仍携带完整原payload，完整transportManifest固定原轮所有预期样本/片/contentDigest；同轮跨多个HTTP批时重复携带同一manifest/context与完整清单，不把当前批子集冒充完整轮。

| 项目 | r1/r2共同固定预算 |
| --- | --- |
| 每HTTP请求 | 实际编码后UTF-8≤4MiB；≤16 cycles、32 sample-parts、8 PLC，DAA原有4 PLC上限不扩大；不压缩。实际转义后的body字节决定是否可装包。 |
| 冻结与内存 | 单HTTP在途；最多8个未终结冻结batch；一次只读取/构建一个≤4MiB请求与一个≤8MiB响应，不预载整个积压。达到8批后停止新冻结，已存在恢复继续。 |
| HTTP连接/时限 | connect≤3s，完整请求/响应≤15s；GET≤8s；关闭自动redirect、cookie、透明重试与环境代理；标准TLS校验，不提供跳过证书选项。只访问保存的规范origin+固定三路径。 |
| 成功/失败ACK读取 | header/Content-Length提前检查，stream累计≤8MiB，超限中止；strict JSON、深度≤20。32片×512点×最坏128-byte ID的转义列表上界<4.3MiB，另留metadata余量；8MiB覆盖合法完整回执，测试必须覆盖该上界而非截断JSON。 |
| latest/history读取 | stream≤2MiB；客户端latest每页最多8点、history projection/changes每页最多8项、original每页1项（provider limit默认100/最大500不改变）。这些小页容纳原512KiB文本经JSON转义及128KiB片和envelope，不请求接近provider上限的大页。按hasMore/空页/scanBudgetReached/cursor继续；单次人工校对最多20页，超出显示未完成和可继续，不冒称全部。 |
| 重试 | 1/2/4/8/16/30秒指数退避，上界30秒，再加0..20% jitter；合法Retry-After优先，限制1..300秒；墙钟跳变不导致紧循环。每批attempt和nextAttemptAt持久，有界计数/最后错误，无无限日志列表。 |

reqwest 0.13.4已存在当前Cargo.lock，未来允许以该固定版本提升为直接依赖，使用blocking/标准TLS所需features；确切feature与锁图差异由Development在任何依赖解析前记录，不能顺带升级全锁或安装辅助依赖。serde_json只增加上述必要feature。HTTP工作在独立单worker，采集actor/SQLite队列/UI不等待网络。

## 5. R05–R07：设置、最新优先和容量

### R05. 一个目标和独立上报周期

首版只有一个后端origin和一个全局上传周期，默认5秒，允许1..3600秒整数；采集组现有500..3600000ms周期不变。origin只允许http/https、明确host/可选端口，无用户信息/query/fragment，API路径固定，不开放任意method/header/template/SQL。目标设置、来源交接引用和节拍存新runtime delivery_settings，真实URL不提交仓库，也不要求写进.env。保存设置不发HTTP、不连接PLC、不启采、不启传。

显式“开始上报”仅打开上传调度，不主动连接/采集；“暂停上报”禁止新dispatch，当前请求在15秒总预算内收尾并持久已取得结果，未决则unknown；“继续上报”先遵公平恢复规则。程序退出先停派发、处理在途已得结果并保留未决身份，再关闭存储/锁；重开只恢复本地状态，**不会因上次running自动发HTTP**。收集和上报可各自暂停，不要求PLC一直在线才能上传已落盘材料。

读取模式的“测试接口”固定GET latest，必须选择已有PLC、limit=1，显示返回状态及准入诊断；它是读取测试，不写测试点、不证明事实POST已提交。包预览只生成只读摘要/折叠JSON，不自动发送。真实POST只由明确开始/继续上报后的调度触发。

### R06. 有积压时最新优先，但历史不饥饿

采样轮完整提交后才进入可选集合，按本地collection_cycles/sample_order索引分页，每次最多扫描200轮；冻结前复核原哈希、target/设置revision及唯一片归属。每个已配置PLC/组的一轮是最新候选，取当前未冻结的最高sourceSeq**整轮**，不把不同轮的点值拼成一个新样本。旧轮都保留待补，不覆盖本地历史。

上传显式启动或网络恢复时，首个可派发新批选最新候选；之后最多连续3次最新通道派发，就必须给历史/到期unknown恢复通道1次机会。两个通道各按PLC轮询；历史优先最老未确认sourceSeq，同一批最多装入各轮合法片，不要求按所有PLC全局时间排序。无最新候选时连续补历史；无历史时不空等。due unknown原批按原身份重发，不重新入新批；其退避期间其他合法PLC可以前进。调度游标/3:1计数和已冻结成员持久，重启不能永远重置为最新而饿死历史。

尚未可靠终结的旧批不允许被拆散或换batchId规避；与其无成员重叠的新最新批可以先发。最多8未终结批或容量不足时停止新冻结，转为已冻结恢复；不能声称在永久unknown/硬容量耗尽下仍能无限采集/最新上报。UI分别呈现新样本待传、已冻结/不确定、需处理与已确认，不靠总待传下降制造成功。

### R07. 保留已有容量门禁，预留可靠确认空间

新runtime的表、索引、请求原文、回执及事件均计入原runtime.sqlite+rollback journal物理配额；默认quota1GiB、日志32MiB及既有90%停止/70%恢复、可用盘/旧页journal保守预算保持。config库原64MiB限制独立，不能把delivery设置塞入采集源context扩大每个包。

在现有保守预留之外，**再保留32MiB的ACK/状态恢复页预算**，计入capacity.reservedBytes。每次新采样/新冻结前核物理空间与该预留，不把“未来可能删除已确认请求”当空闲。一次至多8MiB回执，短事务含其页/索引及旧页journal；测试须核最坏响应和rollback预算。新采样/新冻结达到门禁即暂停；已冻结HTTP发送可继续，ACK确认与拒绝证明保存使用专用预留，不以普通90%门禁把恢复永久挡住。真实ENOSPC/IOERR仍可能发生，失败不丢原批、不标已传，关闭新派发并显示storage_fault。

确认完成后，冗余的完整冻结请求可在同一可靠确认事务中释放，只保留bodySHA/requestDigest、完整成员绑定和可靠回执；未知或有效父拒绝链仍有依赖时不释放其恢复材料。新metadata/回执随**新profile既有的已确认整轮保留规则**有界回收，先确认无active batch/unknown/派生/校对引用，再原子删除关联投递metadata，才能沿用原cleanup_acknowledged的已过本地保留期/整轮全确认/无引用条件。不得放宽原清理条件，不删除pending/blocked/expired_unconfirmed，不修改原历史内容或把后端三月到期当本地删除许可；既有v2库不增加任何清理动作。

credential/sentinel/staging逻辑与allocated占用按R02.2有界计量，初始化/恢复不得绕过物理空间、旧页journal及32MiB恢复预留；不为辅助文件删样本或扩大历史清理。UI显示原样本字节、冻结请求/回执/投递metadata及总库/journal预算，不能只计payload。积压可占满配额，处理为暂停/恢复或后续明确运维决定，不能换身份/删未确认样本。

## 6. R08–R11：状态机、ACK、unknown与错误矩阵

### R08. 持久状态与崩溃边界

sample_delivery仍保留原二态；下表为新delivery_parts/batches的细状态，不回写payload。

| 状态 | 进入依据 | 合法后续 |
| --- | --- | --- |
| pending | 完整轮已落盘，未冻结 | 有空间且原材料有效时prepared；不可编码为blocked。 |
| prepared | 原请求/成员/目标/digest及references已一次事务落盘 | 先持久inflight，再离开事务发送；从未发送不等于可以随意重写冻结批。 |
| inflight | 已持久dispatch标记，HTTP结果尚未可靠落本地 | 完整ACK同事务到acknowledged；可靠终结拒绝到rejected；结果不明到unknown。重启一律按unknown恢复。 |
| retry_wait | 完整可验证失败表明本次none且可重试，原批保留 | 到期原字节原身份重发；不能由此否认更早提交。 |
| unknown | 超时/连接中断/坏响应/显式unknown/ACK持久化失败/崩溃 | 原批重试收回原结果；有效证明到已确认或可靠拒绝；超过证明/准入/来源边界仍不确定则needs_review。 |
| rejected | 完整有效persistence=rejection_recorded且retirementAllowed=true | 保存原拒绝与token；按R10创建原成员合法子集的派生批，不改父批。 |
| acknowledged | 所有相关固定片的可靠提交证明已原子持久 | 不再派发；历史查看仍读取原样本/SHA。 |
| blocked / expired_unconfirmed / needs_review | 不能编码、冲突、来源/合同/时间/证明过窗或无法确定结果 | 原样本及证据保留；暂停受影响成员，其他PLC公平继续。无“忽略即成功”或自动删除。 |

冻结事务成功前绝不发送。标inflight失败则不发送；其提交结果本地不确定时，先按batchId/bodySHA查询本地表而不是立刻创建新批。HTTP结束后关闭网络资源再提交ACK，不持SQLite事务等待15秒网络。正常暂停/退出不杀掉正在提交的SQLite事务；新sealed profile异常退出按R02受控native rollback恢复完整旧/新态，不留半个sample acknowledged。旧/未封存profile仍严格拒绝需要写入才能读取的hot材料，不把拒绝称恢复成功。

### R09. 严格可靠回执与本地原子确认

必须同时校验：HTTP200、application/json、完整typed success envelope的code/message、版本、instanceId/batchId/requestDigest、status/persistence=committed、confirmation=facts_committed、receiptId/committedAt/proofExpiresAt，以及**results与冻结batch成员集恰好一致且无重复/缺项/额外项**；逐片part/parts/sourceSha256/contentDigest/position相符；cycles恰为所含轮、cycleDigest及expectedParts相符，receivedParts/complete/qualityGood逻辑相容。latestAdvancedPointIds只能来自该片，允许为空；outcome/confirmation/originalOutcome/newFactsCommitted/commitSerial按provider规则校验，duplicate或historical_committed同样是可用历史提交证明，不误记成新写入或当前值可读。

按原请求与已存回执建立局部不变量：源样本只有所有固定片已可靠确认且集合/摘要完整才acknowledged；整轮complete另外统计全transportManifest，不用单个batch的results数量替代expected集合。provider首次部分回执的complete字段在原批重放时保持历史值，不能要求它随其他批片到齐而改写。客户端依据全部已验证片集合展示本地确认完整性，与服务端回执当时完整性分列。

所有严格校验通过后，在一个runtime事务保存原回执/SHA、片确认、样本二态、批终态与引用释放；原回执服务器日历时间保留原字符串/最高9位精度，不经过现有毫秒normalize截断。事务失败/未知时只读核本地原批/receiptId完整状态；无法证明全事务提交即unknown，不向UI报上传成功。上报成功计数是本地可靠确认数，不以发送次数/HTTP200次数或newFactsCommitted代替。

### R10. unknown与可靠拒绝的恢复

unknown的首要对账就是**重发完全相同target、batchId、batchCreatedAt、requestDigest、请求字节**，恢复provider的原稳定成功/拒绝结果；重试不重采、不重算新值、不把新batchId当幂等重试。三自然月原值过期但120天证明仍有效时，原批恢复historical_committed，可确认历史提交但valueReadable=false，不重建raw/latest。

只有完整可靠拒绝绑定当前原批/摘要/稳定receiptId，且newFactsCommitted=false、retirementAllowed=true、token/截止与各成员diagnostics完整，才允许自动派生：保持sample/cycle/part/原文/内容摘要，只选原成员中eligible/duplicate_proven的未确认合法子集，新batchId与创建时间，parent引用原batchId/requestDigest/rejectionToken。子批完整轮manifest/transportManifest仍保留；父链最多8层，token永不记日志。expired_unproven/conflict/source_rejected成员转需处理，不删；空合法子集不造空请求。拒绝proof、父token缺失/过窗或unknown父都不派生。

batchCreatedAt的新准入为24小时。原批已知committed/rejected时可在120天证明期内恢复；未到达后端或无证明的旧prepared批可能得到batch_admission_expired。先恢复原批，只有可靠终结拒绝才合法派生新的子批；不能把“已过24小时”本身当作未提交证明。proof_expired/parent_proof_expired保留原身份/证据转needs_review，不无限换父/重置期限。

GET latest/history只是核对事实值、来源、摘要和完整性，不是batch ACK查询。latest被更高seq覆盖、history空页/过滤/到期gap、cursor过窗或覆盖声明不完整均不能证明旧POST没有提交；有匹配fact也不能替代绑定原batch的可靠回执。人工“结果核对”只保存read_result作为诊断，不能直接把sample_delivery设已确认。

### R11. 失败分类、退避及不确定边界

| 结果 | DAA固定处理 |
| --- | --- |
| 网络无响应、超时、重定向、非JSON/超限/截断/错壳/成员摘要不符的HTTP200 | 视为unknown；原批保留，停止该错误循环并显示诊断；可按有界退避原批恢复，连续5次协议失败转needs_review。 |
| 完整429 busy / Retry-After | 不新确认；按1..300秒Retry-After/退避保留原批，其他PLC公平继续，不并发灌请求。 |
| 503 unavailable/capacity_exceeded/clock_invalid/not_ready | 完整none仍原批retry_wait，容量/时钟/采用诊断可定位目标，不能自改后端；连续5次not_ready/clock_invalid暂停目标待处理。 |
| 503/500，persistence=unknown或无法完整判断 | 原批unknown优先恢复；500不能无依据称未提交。 |
| 403 scope_rejected | 暂停目标并保留队列，请检查批准的scope；不加伪token或修改客户端UA。 |
| 403 source_rejected、409 batch/sample/cycle/binding conflict | 无可靠终结证明则blocked/needs_review；有可靠终结证明按R10仅处理合法子集；不能修改源ID、definition、seq或换generation绕过。 |
| 410 sample_expired/batch_admission_expired | 有可靠拒绝按R10；无证明转expired_unconfirmed/needs_review，不造ACK、不改observedAt/创建时间续期。 |
| 410 proof_expired/parent_proof_expired | 失去足够证明，保留未知边界并需人工审查，不标已传；其他合法新样本可继续。 |
| 413/415/422 payload/media/invalid_request/digest_mismatch | 冻结后不能随意改包；blocked并定位合同/字节/digest；已有可靠拒绝才允许原成员同内容合法派生。已满足固定4MiB仍413属于目标/合同差异，不能无限递归拆包。 |
| GET cursor_expired/gap/mismatch | 明确展示校对未完成/范围缺口；经人工明确选earliest或固定range重做只读校对，不保存SMA消费checkpoint或偷用tail跳过缺口。 |

## 7. R12–R14：来源交接、时间/保留与重启

### R12. 后端采用与目标变化不由DAA猜测

运行前由后端责任方在另批环境完成schema/上海DB时钟、准入PLC集合、HMAC key和source binding采用，交付非秘密targetId、origin、源码/机器合同pins、schema profile/revision、采用引用及与DAA当前instanceId/plcId/generation/definitionSetDigest/contextSHA/seq窗口的核对材料。允许使用BE009-B的0a2或BE009-BE010-JOINT的1b3已知profile；不要求为DAA先接通BE010业务写入。DAA无MySQL凭据、HMAC key、维护CLI调用或来源管理API。

界面“查看接入材料”返回当前新profile只读来源JSON和digest，供后端按其批准流程采用；生成/查看不发HTTP、不改DB来源、不新造PLC。context/定义变化后，builder对新轮definitionSetDigest与已核材料比较：仅周期/注释/其他PLC变化且本PLC定义不变可继续；定义变化/代次变化的受影响轮暂停，等后端另行明确采用及原raw-only窗口，不能按revision UUID大小抢占latest。

公开ReceiptData/ReadBase**没有storageEpoch/adoptionId字段**，latest只有bindingRevision、cursor为opaque。DAA可冻结已知targetId/来源资料、已观察bindingRevision变化与响应矛盾，暂停受影响队列要求复核；不能发明HTTP字段或宣称自动识别同URL悄然换库/恢复备份/重置采用。计划目标变更必须先停传并核原未决投递；未被告知且外部抹掉证明的静默换库风险保留，由运行交接和目标持久性约束承担。

### R13. 时间、值与期限

本地原采集/保存毫秒+08:00事实保持，服务端返回最多9位小数按原精度保存；UI默认上海`YYYY-MM-DD HH:mm:ss`，诊断才展开精度。重试deadline/周期使用单调时钟，持久nextAttemptAt为上海日历时间；重启时重建有限剩余等待并限制1..300秒，不用系统TZ决定业务时间。sourceSeq排序与原observedAt/HTTP到达时间独立。

后端raw/latest默认最多三自然月（可1/2月），每点从原observedAt起算；原样本按最早成员保守到期，latest按点到期；120天最小证明不含原值、不续期。DAA本地retentionDays不自动等同后端期限，不修改旧时间/重采作为补传。后端拒绝过期不授本地删除权；本r1没有“过期后自动丢弃待传”功能。服务端clock_invalid或原未来时间拒绝只能诊断，不将源时间替换成接收时间。

### R14. 重启恢复与单实例

产品/测试共用R02受控factory，现有ProfileLock从初始化/TOCTOU/native恢复/后检到Stores与worker生命周期连续持有；不能先开Stores后补锁，不能以单测免锁证明恢复。沿用StoreHandle串行队列及唯一upload worker；重复开始/继续幂等。启动只在完整准入后重读v3状态，prepared保留原文，inflight→unknown；完整receipt/sample_delivery原子核对后不重复派发；冲突/缺列/不完整批不猜修。

恢复读取只做有界索引扫描，每页100batch/part，不加载全部历史或重建所有批。目标/成员/原文SHA不一致暂停。上次running/意图/env都不自启，用户显式继续才发。原崩溃点仍为冻结前/后、inflight后、发送无回执、得回执未写库、ACK事务中及commit后UI前。r2另覆盖真实hot、恢复前/native后RO前/RO后业务前的第二次进程退出；已知提交前kill须恢复完整旧态，已知commit后kill须保留完整新态，不用“任一旧或新”掩盖checkpoint。文件SHA变化与原样本内容SHA守恒分开记录。

## 8. R15–R16：页面、IPC与日志

### R15. 保持CU布局，最小可用交互

一级工作台/配置中心，二级仍为PLC配置、点位与采集组配置、上报与存储。工作台新增独立“上报运行”卡：目标摘要、停止/上传中/退避/不确定/需处理、待传/已确认/需处理数、最近可靠确认时间、开始/暂停/继续；原PLC控制不变。无需在多个配置页来回找运行按钮。

上报与存储页：上报设置卡（origin、周期、已核目标引用，保存/读取测试/只读包预览）、队列摘要和需处理列表、本地历史与现有存储策略折叠。编辑目标/详细回执/原包预览采用弹窗；不把完整JSON和编辑区堆在列表下。普通行默认20条、可10/20/50，后端有界分页；拖拽列宽/最小列宽/横滚/本机稳定字段偏好/恢复默认使用已有公共工具。明暗、ZH/EN、窄窗间距和弹窗可达均需增量检查。

样本详情继续顶部摘要+点位结果表+折叠格式化JSON。新投递详情只追加关联batch/片/ACK/重试原因，原payload/manifest/context与SHA不变；“已确认”只来自本地原子ACK，historical_committed明确“历史提交已确认，原值已到期”，unknown明确“结果待核实”。采集日志与上传日志分开入口/筛选，不做每点滚动刷屏。

新增具名IPC固定：`daa_get_delivery_settings`、`daa_save_delivery_settings`（expectedRevision CAS）、`daa_get_delivery_snapshot`、`daa_set_delivery`（显式start/pause/resume）、`daa_preview_delivery`（原轮只读/有界）、`daa_test_facts_endpoint`（仅GET）、`daa_list_deliveries`、`daa_get_delivery`、`daa_get_facts_source_material`。参数deny_unknown_fields、UUID/数量/字符串上限及原profile能力门禁；没有任意URL请求/SQL/文件执行、人工ACK或删队列IPC。现有IPC envelope=1，新增DTO有明确schemaVersion；Bootstrap.uploadAvailable改为能力布尔，不代表正在上传或后端已就绪。

### R16. 可追溯但有界的日志

复用既有stdout/持久JSON Lines日志与32MiB保留，不新增daemon/日志平台。稳定事件包括delivery_prepared/started/acknowledged/retry_scheduled/unknown/rejected/blocked/recovered/paused；只记录受控身份/digest/计数/状态/耗时/稳定errorCode，不记值/body/context/私有路径/token/HMAC/凭据/SQL。常规无变化轮询不逐条落盘；事件500条和文件轮转有界。r2新增profile_recovery_started/completed/business_admission_failed及稳定错误key，后检前仅stdout；区分已/可能恢复写与业务拒绝，不先创建持久日志。日志成功不当ACK，已提交ACK不称回滚。

## 9. 实施顺序、分工与必要验证

| 步骤 | Development未来工作 | 验证/门槛 |
| --- | --- | --- |
| P0 | 取得精确r2 A0/A1及R02写入例外批准，固定第2.3节r1候选/QA2、provider pins及保护边界。 | 未批不实现；DAA已批after与before不同不误认漂移，不读取真实profile。 |
| P1 | pf-json无损表示、SHA/固定片/完整轮/请求及ACK纯合同；HTTP adapter替身接口。 | 独立provider vectors全对；非法/大小/precision反例；无HTTP/DB。 |
| P2 | 新空runtime v3、六表/配置CAS、同库冻结/ACK/引用、容量恢复与单worker状态机。 | 仅另明确批准的A1合成目录；v2格式原表/原串/状态逐项守恒；故障后无半ACK。 |
| P3 | 单目标HTTP、3:1最新/补传、unknown原批恢复/拒绝派生、启动停态与IPC/CU/i18n。 | 传输替身覆盖网络/响应矩阵；需要真实loopback listener也转B批准，不借“mock”名义先监听。 |
| P4 | P1–P3已有r1有限证据；r2只加凭据/封存/锁内factory/恢复/诊断及双语说明，再交精确候选给新的fresh Verification。 | 先pure格式/指纹/门禁，再新r2 A1初始化/真实hot/二次退出；只做触达回归并复用r1/QA2，不重跑整套。A-only不代表阶段C完成。 |
| G-B | 提交精确操作提案；后端责任方按已验收代码准备持续HTTP目标，Owner明确批准。 | 无批准不连接/探库/建库/开Docker/操作DS；记录target/source/合同与资源生命周期。 |
| P5 | Owner按手册做最短原生链路，Development闭库核账；独立Verification消费双方候选和实际证据。 | 完成AC18–AC20与全部前置后才交Owner阶段C终验；必要返工后新的fresh QA。 |

后端负责部署/准入/schema/时间/source采用与事实查询；DAA负责原样本到可靠本地确认。DS只提供受控S7数据。SMA以后负责事实到业务映射及业务ACK，当前没有SMA checkpoint/outbox、业务表写入或页面业务展示验收。

## 10. 精确候选allowlist与排除

**本轮PM唯一写入为本spec。** 主协调机械同步四处DAA PLAN/catalog。下表保留r1总体allowlist；r2新增文件仅local_store/profile_contract.rs及profile_contract_tests.rs。既有路径只允许为恢复最小触达local_store的mod/schema/capacity/tests/delivery_tests/time_contract_tests、local_supervisor、两组README、STAGE_C_GUIDE pair、locale及DAA-owned CODE_INDEX段。其余r1源码冻结并复用QA2，不重构上传/UI。花括号仅展开所列名字，当前不授权实现。

| 相对DAA根的路径 | 未来责任/有限修改 |
| --- | --- |
| `plans/DAA-008-reliable-facts-upload/spec.md` | PM/Human Owner范围、批准与Revision。 |
| `plans/DAA-008-reliable-facts-upload/tasks.md` | 批准后Development创建，自检/完整diff/资源/hand-off。 |
| `plans/DAA-008-reliable-facts-upload/checklist.md` | developer_handoff后fresh Verification创建，分A/B结论与Owner验收。 |
| `src-tauri/Cargo.toml`、`src-tauri/Cargo.lock` | 仅reqwest0.13.4直接依赖/必要feature及serde_json无损解析feature；实际锁diff审计，无批量升级。 |
| `src-tauri/src/domain/{mod,local_runtime,local_delivery,facts_wire,facts_canonical}.rs` | DTO/纯合同/状态；不修改local_sample或点位/命名/共享导入核心。 |
| `src-tauri/src/infrastructure/{mod,facts_http}.rs` | HTTP adapter及其模块注册；无直库、旧CA或任意执行。 |
| `src-tauri/src/infrastructure/local_store/{mod,schema,runtime,capacity,delivery,delivery_tests,time_contract_tests,tests}.rs` | 显式新空v3、v2/v2兼容、投递事务/引用/容量、必要单元夹具；runtime原payload/seq/manifest写入和旧清理条件原样。 |
| `src-tauri/src/infrastructure/local_store/{profile_contract,profile_contract_tests}.rs` | r2唯一两个新增源码：严格凭据/静态指纹/封存/受控恢复及必要测试；不增加SQLite版本/表/第三库。 |
| `src-tauri/src/infrastructure/local_store/README.md`、`README.zh-CN.md` | 精确v2/v3矩阵/表与事务边界，不混写任务证据。 |
| `src-tauri/src/services/{mod,local_supervisor,local_queries,local_delivery}.rs` | 唯一worker生命周期/快照/有界调度/退出；不改PLC协议或新建第二采集actor。 |
| `src-tauri/src/commands/{mod,local_acquisition,local_delivery}.rs`、`src-tauri/src/lib.rs` | 新具名IPC/能力DTO及注册；原PLC门禁/旧入口拒绝不变。 |
| `src-tauri/src/domain/facts_canonical_tests.rs`、`src-tauri/src/services/local_delivery_tests.rs`、`src-tauri/src/infrastructure/facts_http_tests.rs` | 新公开行为/向量/状态/响应/传输替身测试，通过模块cfg(test)注册；不生成生产fixture fallback。 |
| `src/services/localAcquisition.ts`、`src/services/factsDelivery.ts`、`src/console/composables/useLocalAcquisitionConsole.ts` | 新DTO/IPC facade/状态接线；HTTP不放浏览器，不保存业务真相到localStorage。 |
| `src/app/collection/views/storage/index.vue`、`src/app/runtime/views/overview/index.vue` | 既有两页增加真实上传卡/设置/队列；PLC/点位编辑页不扩功能。 |
| `src/components/console/{FactsDeliveryPanel,FactsDeliveryDialog}.vue`、`src/components/console/LocalSampleDetail.vue`、`src/components/shell/AgentTopbar.vue` | 有限上传组件、弹窗、原详情附加关联及能力/状态显示。 |
| `src/console/{tableWidths,types}.ts`、`src/styles/app.css`、`src/locales/{en-US,zh-CN}/common.json` | 复用公共列宽/最小间距和对称文案，只限上传触达面。 |
| `tests/facts-delivery.test.mjs`、`tests/sample-details.test.mjs`、`tests/time-and-history-preferences.test.mjs` | 上传可见交互及触达详情/时间/列宽的必要增量断言，不复制实现做镜像测试。 |
| `README.md`、`README.zh-CN.md`、`STAGE_C_GUIDE.md`、`STAGE_C_GUIDE.zh-CN.md` | 当前能力及分门禁操作手册；原阶段B JOINT_TEST_GUIDE pair保留。 |

r2不增加依赖、Cargo/Tauri feature、env键、CLI/IPC或修复按钮，直接复用现有ProfileLock，不改local_profile_lock.rs或provider wire。r1 archive.txt归主协调只读附件，不得修改。四处DAA索引由主协调同步，CODE_INDEX仅Development最小改DAA段。除此不改根设计/合同、后端/DS/SMA/FF、旧bundle、AGENTS/skills/workflow/角色、启动/构建入口、pnpm依赖、旧writer/权限、真实env或profile。新增风险/写面超表须返PM重批。

排除自动启动/自启恢复采集、后台服务/daemon、OS调度、生产清理SLA、真实PLC/现场切换、打包签名/发布部署、生产DB迁移、旧profile升级/历史上传、任意目标JSON映射、SMA业务投递、跨后端队列迁移、多目标/多HTTP并发、客户端身份认证平台、Celery/Redis/Python Worker、Git commit/push/tag/分支发布和外发消息。

## 11. 运行提案与Owner试行手册要求

### 11.1 r2 A1有限合成SQLite增量提案（待精确批准）

此为本r2待批提案，**现在不执行**。r1目录/证据保持，不复用、补封或恢复其数据库。若Owner明确批准本r2及本节，Development/Verification各自在全新`/private/tmp/daa-008-r2-a-<随机后缀>/`私有目录生成合成v2/v3 SQLite、凭据/sentinel/staging及故障子进程。不运行GUI/DS/HTTP监听/MySQL/Docker；路径先canonicalize，拒绝symlink/既有文件。夹具从公开结构/合成值生成，不读取/复制用户profile、原8590样本或.env。

只在这些新目录允许建库/读写/BEGIN/commit/rollback、凭据/身份/链接/替换反例、no-replace/fsync/close故障、真实cacheflush后_exit86及恢复各边界二次退出、空间计量和自有可再生夹具回收。native写先于SQL元数据重读仅限R02新sealed分支；不能扩大到默认/旧路径。DEV固定目录/版本/argv/exit及durable before/after原串/账本，结束子进程无连接；必要证据持久化后由主协调收尾。只批A0不授A1，未执行不能记通过。

### 11.2 B操作提案的必需字段（当前不选目标）

A候选固定后，在tasks中向Owner提交一个具体、可审阅的操作提案，至少列：新隔离DAA profile绝对路径与不得存在旧数据的前置；后端候选/三机器合同SHA、专用MySQL8.4.6实例alias/schema/账号/最小权限/端口、schema精确revision及F7/时区/retention、source采用计划/seq边界；API绑定地址/监听进程/目标origin；受控DS实例ID/端口/版本/合成值；Docker镜像/容器/卷/网络精确新名称与归属、创建和清理动作；故障注入/响应丢失/停止恢复范围；凭据不公开；保留证据/profile与资源收尾条件。

如复用已运行DS或已有后端目标，只读检查也须按具体批准，不能因为Owner曾同意阶段B而重新操作同实例。本任务不重建BE009已回收的QA容器或恢复其口令。实际schema/时间/source采用由后端责任方实施和交接，DAA不增后端写面。没有上述具体批准就停留于A-only交接，阶段C联调未完成。

### 11.3 未来最短手动步骤与证据

手册需给“开始条件/一次配置/按顺序操作/预期现象/失败停在哪里/交给谁核账”，URL和路径在B批准后填具体受控值；普通启动始终`pnpm tauri dev`。只做以下增量，不重复阶段B导入/命名/分组整套：

| 步骤 | Owner手动动作 | DEV/QA应取得的证据 |
| --- | --- | --- |
| M01 | 用获批全新profile启动，核停止态；按手册准备最小PLC/点组及后端接入材料，不动原profile。 | 新instance/generation/seq/合同pins、后端采用引用；原运行环境没有被替换。 |
| M02 | 保存目标/周期并GET测试；预览一轮JSON，显式开始采集与上报。 | DS已知值→本地原样本→POST→可靠ACK→本地已确认→latest/history逐项对照，覆盖BOOL false、整数0、REAL和bad/null；两PLC同DB互不串。 |
| M03 | 在批准的方式下暂使API不可达，保持有限采集；随后恢复。 | 本地积压增长、未伪ACK；恢复首批最新、3:1历史继续；旧seq只补raw，不覆盖较新latest。 |
| M04 | 保留积压并正常Cmd+Q退出；同新profile重开，不点任何运行按钮，查看历史/队列；然后显式继续。 | 重开无自动采集/上传，原payload/manifest/context/ID/SHA及冻结batch不变；继续恢复同身份，确认后不重复落事实。 |
| M05 | 打开任意上传/需处理详情，按手册查询后端核对；结束后正常退出。 | 完整身份/值/质量/观察/保存/提交时间/摘要、完整轮、队列和后端事实账闭环；真实错误和未覆盖项如实保留。 |

丢ACK、ACK本地事务失败、进程崩溃位置、409/混合拒绝/父token、120天证明与三自然月截止、32片大回执、竞争/分页/容量等难稳定手工制造的情况由必要自动化承担；不要求Owner重复点击数轮同一功能，也不靠口头“正常”代替双方数据账。

## 12. 编号验收标准与证据归属

以下为r2验收要求。相同源码/条件上未变的r1条款可复用第2.3节QA1/QA2有效证据，不改写原qa_failed；新增恢复尚未实施/验证。DEV在tasks固定真实命令/输入/exit，由新的fresh Verification独立判定。参数/allowlist/主要风险变化返PM。

| AC | 需证明的结果 | 最小验证面/关联 |
| --- | --- | --- |
| AC01 范围与来源 | 后端pins/版本/路由一致，r1 archive/候选/QA2可追溯，r2不继承批准；当前只spec。 | 静态SHA/本地链接/metadata及archive原字节；R01/第2节。 |
| AC02 既有数据保护 | 未发现/读取/复制/挂载/升级真实profile或env；真实旧库schema/历史/状态不受本任务操作。 | 路径guard+仅合成v2的配置/原样本/ID/seq/delivery/表结构before-after；原有正常启动/退出lifecycle变化单列，不误称整个SQLite文件在打开后字节不变；R01/R02。不能用打开真实库去证明未打开。 |
| AC03 双库版本 | 新空config2/runtime3正确；v2/v2保留本地且无投递DDL；未知/半库/时区/WAL/链接/身份异常拒绝，恢复例外仅R02精确776新sealed，不补封旧库。 | 新r2夹具的cold/hot矩阵、元数据/版本/表集合及凭据/头绑定；R02、AC21–26。 |
| AC04 原材料与数值 | 原文三SHA/关联完整，中文key/name、missing nameMode、整数0/false、REAL边界/长十进制/指数/负零及9位时间不变义；坏值完整。 | provider vectors+独立lexical预期，禁止同一canonical实现生成唯一oracle；R03/R04/R13。 |
| AC05 固定片与限额 | 两PLC同DB/跨DB同轮、全manifest/片集合、512点/128KiB/16片/4MiB边界成立；单context/最小包超限blocked且其他PLC继续。 | 纯构建+替身和A1持久冻结；不裁剪/重写原文；R03/R04。 |
| AC06 冻结与幂等 | batch成员/原请求bytes/digests/创建时间仅冻结一次；同片不能进入两个未终结批。 | 原字节重发/重启/唯一约束，后端B duplicate无新增事实；R08/R10。 |
| AC07 调度公平 | 最新优先首批、3:1历史机会、各PLC轮询、采集周期独立、单HTTP在途/最多8冻结批，存储/UI/采集不等网络。 | 注入单调时钟+有限负载/慢传输，无长时间sleep；R05–R07。 |
| AC08 严格ACK | 状态/媒体/完整壳/版本/身份/各片摘要/完整成员/轮次都匹配才确认；合法重复/历史确认可用，HTTP200错壳/缺片/多片/截断不成功。 | 完整typed正反响应矩阵、8MiB上限与最坏合法32片回执；R09/R11。 |
| AC09 本地原子确认 | receipt/parts/sample_delivery/references全成或全不成，原文/ID/SHA不变；样本确认、轮complete/qualityGood分开。 | 既有SQL故障/partial ACK证据加新sealed cacheflush/_exit热恢复；R02/R09、AC23/25。 |
| AC10 unknown恢复 | 无响应/丢ACK/本地ACK失败/崩溃保原batch，空history/缺latest不充证明。 | 替身及新sealed真实/二次退出矩阵；实际POST丢响应同receipt仍属B；R02/R08–R10。 |
| AC11 拒绝与过窗 | 错误完整分类；可靠拒绝才同成员子集派生，unknown父禁止，token换key仍按provider恢复；proof/父/24h过窗不假ACK、不删材料。 | 合成403/409/410/413/415/422/429/503/500及父深度8边界；B有限代表例；R10/R11。 |
| AC12 容量与保留 | 请求/ACK/metadata/journal计物理预算，32MiB确认预留；高水停采/新冻结但允许恢复；IO失败unknown；有引用/pending/unknown历史不清。 | A1空间meter与真实SQL故障/rollback、合法大ACK/恢复、fresh-profile已确认有界清理；R07。 |
| AC13 目标与source | 设置CAS/不随采集版本改写；未决不能换目标；受影响定义/source变化暂停，未知静默换库不能声称自动检测。 | 设置竞争/同URL风险说明/无新增wire字段；B target/source采用交接；R02/R12。 |
| AC14 启停/重开 | start/pause/resume单worker，正常/异常退出无半批；新sealed按受控factory恢复，重开停采停传待显式继续。 | 真实hot/二次退出+M04，已知commit位置决定完整旧/新账；退出无自有HTTP/线程/锁；R02/R05/R14。 |
| AC15 CU与文案 | 两页最小真实控件、弹窗间距、默认20条/分页/公共列宽记忆、ZH/EN与明暗窄窗可用；详情原文/SHA保持。 | pnpm build/新增Node行为断言、必要视觉与Owner M05增量；R15。 |
| AC16 安全边界 | 仅Rust固定三API，URL无凭据/query/任意路径、标准TLS/无redirect；无MySQL/PLC新行为/业务映射/认证改造/自动启动。 | adapter/IPC guard正负例、源码allowlist、浏览器无桥门禁；R04/R12/R15。 |
| AC17 日志与真实交接 | 有界JSON Lines/稳定key/时间语义，token/值/body/DSN无泄漏；正式交付树与验证候选一致、资源归属清楚。 | 相关编译/测试/JSON/i18n/link/diff结果；R16/第10节，DEV self-check不充QA。 |
| AC18 真实正常事实链 | 具体B批准后，Owner原生DS→DAA→SQLite→真实HTTP→后端独立facts七表→latest/history及本地ACK逐项一致。 | 固定双方候选/目标/真实请求响应摘要、完整轮、值/quality/time/ID/原SHA；M01/M02/M05。 |
| AC19 真实补传与重启 | API不可达缓冲/恢复最新先行并历史补传；较旧结果不倒灌latest；积压退出重开原文/冻结身份不变且不自启，继续不重复事实。 | M03/M04与闭库前后双方完整数据账；新增样本区间单独固定，不补造早期基线。 |
| AC20 完整阶段C终验 | A0/A1/B各有实际证据，新的fresh Verification覆盖确切候选，所有必需finding关闭或按Owner决定记录；Owner最后接受受控范围。 | A-only/B未批时明确整体未完成；生产/长期SLA/真实PLC/SMA/自动启动仍另项。 |
| AC21 原子初始化 | 新sealed凭据只按sentinel→双commit/close/RO→staging fsync/no-replace→sentinel最后移除产生，半态不自动完成。 | 各durable步骤中断、sync/close故障、目标竞争/已存在、尺寸/分配预算；R02.1/2。 |
| AC22 凭据/旧库保护 | strict字段/原SHA/静态指纹/路径/双文件身份生效；无效不降级，v2及未封存r1 v3不认领。 | 缺失/损坏/超限/BOM/重复/未知字段、错ID/版本/时间/schema/头、替换/链接/WAL/双journal拒绝before-after；R02.1/3。 |
| AC23 真正热ACK恢复 | 新sealed formal factory的真实未提交ACK经cacheflush成功后_exit86，恢复完整旧账；提交后崩溃保留完整新账，原串/SHA守恒。 | durable before/journal、精确776/native rollback/全RO后检、同frozen batch unknown停态；R02.4/R09/R14。 |
| AC24 精确错误/排他 | 仅原始extended776且全部门禁满足才一次native RW；264/其他错误/锁竞争/漂移不恢复。 | structured错误分支、真实锁竞争及有界TOCTOU注入；无CREATE/DML/手删journal/测试旁路，1000ms busy；R02.3/4。 |
| AC25 二次退出/失败语义 | 恢复前、native后RO前、RO后业务前再次真实退出，下次仍完整后检/停止态；后检失败不称零写。 | 新子进程退出、durable before/after完整账、已恢复写而拒绝业务诊断；这是阶段crash证据，不是SQLite pager内部掉电证明；R02.4。 |
| AC26 平台/容量/回退 | Unix绑定、辅助文件/256KiB预算计入原32MiB；未知平台无hot fallback且unsealed cold保持，复制/移动不自动重绑。 | macOS实际A1、cfg静态/纯分支测试及双语说明；Linux/Windows原生证据未有则保留限制；R02.2/5、R07。 |

建议未来命令：Cargo `fmt --check`、`test --locked`仅本新增canonical/delivery/storage受影响模块，Node仅facts-delivery/sample-details/time-and-history-preferences三文件及`pnpm build`。实际完整argv、features/环境/新目录和退出码由DEV固定后交QA；合成SQLite/监听门禁与第3/11节一致。无必要不重跑整个阶段B、后端A/B或DS整套，已有测试失败按entry/本次差异如实归因，禁止削断言、allow(dead_code)掩盖或用skip冒充通过。

## 13. 风险、回退、开放门禁与PM交接

| 风险/限制 | 本r2决定与回退 |
| --- | --- |
| 新profile限定 | 原v2历史不能直接上传；仅r2新sealed可受控hot恢复，未封存r1 v3不补封，失败夹具保留；升级/旧历史另spec。 |
| native先写再SQL重验 | 仅初始化凭据/文件绑定/头/精确776允许；后检仍可失败但不能声称从未写。Owner须明确接受此例外，未知/旧profile不适用。 |
| 本地凭据非认证 | SHA/devino不能完整识别恶意原地编辑、伪造journal、同inode备份恢复或非合作TOCTOU；不交付认证/通用repair平台。 |
| fsync/平台/双journal | 初始化中断为未完成拒绝；依赖OS/文件系统sync/no-replace语义，不称掉电全证明。双journal拒绝，macOS实测不等于Linux/Windows通过。 |
| 路径/文件绑定 | 移动/复制/换inode可能使sealed拒绝，无自动重绑/删除marker；旧二进制不继续用新sealed资料，运维修复另批。 |
| v3旧二进制兼容 | 只支持runtime2的旧版会拒绝3；r1已支持runtime3且忽略额外marker，r2不能强迫未修改的r1拒绝sealed资料。运维明确禁止用旧r1打开新sealed profile，不回写版本/删marker或降级DDL；回退使用原兼容profile/版本，新v3保留，部署回滚另批。 |
| 原context/样本过大 | blocked并保持原件；其他PLC继续。需要缩小将来的采集配置或新provider版本时另审，不改已持久材料。 |
| 有限proof/目标持久性 | 120天后、外部丢证明或同URL静默换库可能无法再证明旧提交；保留needs_review，不承诺无限exactly-once/自动对账消除一切未知。 |
| 长断网与磁盘耗尽 | 只在有限quota/恢复预留下继续；满盘暂停，不删未确认数据。真实底层IO故障仍可让ACK未知。 |
| 匿名集成 | producer/plc/source为声明可被冒用；本次按Owner已选匿名边界使用，不以client字段当认证，网络部署另批。 |
| 后端全局门闩/有界预算 | 首版单在途降低压力；真实吞吐靠B有限数据证明，不外推长稳或现场规模。 |
| 脏工作树/临时副本 | 默认直接改正式DAA源码工作树，按文件/段审计并保留他人修改；用临时验证副本时交付前必须核一致，不能把成果仅留tmp。 |

源码回退只识别本任务自有增量，保留所有新profile投递事实/ACK，不reset共享树、不删已确认/未知材料。临时源码/缓存/构建产物有任务归属、保留原因及清理触发；最终必要结果持久到tasks/checklist，Owner接受后只回收无运行/后续/证据依赖的自有可再生资源。**已有SQLite配置、历史及阶段B联调profile始终保留。**

当前待Owner决定：精确r2 A0及R02先native恢复写的有限风险例外、本r2第11.1节新目录/新增合成故障验证、后续具体B操作提案和阶段C终验。r1批准不授r2新信任边界。算法/版本/预算/平台选择已定，不推给编码时决定；旧历史上传、自动启动、多目标或新协议仍须另修spec。第15节提供可复制的待批语句。

后续技能路由：治理/范围使用aiis与project-governance；Rust runtime/SQLite/HTTP worker使用rust-runtime，桌面入口/IPC使用desktop-tauri；Vue/CU/样式使用frontend-ui，文案使用i18n-workflow，真实结构索引使用code-document-indexer；协议对账仅消费现有S7能力，必要时plc-point-mapping；实际B涉及后端采用由后端责任方使用backend-arch，Docker确实获批后才用docker-expert/docker-project-ops。PM不替Development/Verification执行上述技术工作；本profile为contract_only，不宣称平台ACL/自动路由或团队激活。

| 日期/Revision | 真实事件与效力 |
| --- | --- |
| 2026-11-05 r1 | 起草后Owner精确批准A0/A1（第14节），实际DEV及两轮fresh QA已发生；QA2仍qa_failed，F001开放，无Owner终验，完整原批准稿只读归档。 |
| 2026-11-05 r2 | F001暴露RO写前准入与hot恢复冲突；实际PM新增最小凭据/受控恢复合同为draft。r2未批/未实现/未QA，B与整体阶段C终验开放。 |

本轮PM只消费公开材料、完整r1 bundle和收据并写唯一spec；未打开SQLite/真实.env/profile、运行产品/编译/HTTP/DS/Docker或安装依赖。已有r1 tasks/checklist原样保留，不代写r2事实。主协调提交**DAA-008 r2**给Owner精确批准；实施交接后必须新的fresh Verification，QA2不自动成为r2通过。最终SHA/真实文档自检在外部handoff固定，避免自引用。

### r1起草时PM文档自检历史（非本r2检查或独立QA）

2026-11-05，在仓根以stdlib `python3 -B -`执行本spec专用检查，真实exit0：身份/状态/角色/STD元数据、11个本地链接及显式anchor、13项文件SHA、3份provider机器JSON完整解析、13张表139行列数、AC01–AC20顺序、UTF-8/行末空白及目录仅spec均符合。随后`git diff --check -- automation-world/data-acquisition-agent/plans/DAA-008-reliable-facts-upload/spec.md`真实exit0；新未跟踪文件正文空白由前述stdlib直接检查，未以Git忽略新文件冒充验证。检查不导入或执行项目，无真实数据/数据库/HTTP/设备副作用。

## 14. r1精确批准收据与A0/A1交接（2026-11-05）

Human Owner对精确`aiis-ics-arch::DAA-008 r1`的明确原话，由唯一主协调`/root`转交本实际PM登记：

> 批准 DAA-008 r1，按 STD 完成 A0 源码实施及第 11.1 节有限合成 SQLite 验证，并完成对应独立核验。已有 SQLite 配置、历史及原联调 profile 不迁移、不清理、不覆盖，只做必要增量验证，不重复阶段 B 整套测试。实际 HTTP／DS／MySQL 联调环境及 Docker 操作另提具体方案批准；自动启动策略、旧历史上传、SMA 和真实现场验证暂不做。完整阶段 C 待实际联调及最终验收后再确认完成。

批准对象是本次登记前完整`Revision: r1 / Status: draft`正文，SHA-256为`f407532ff91d8ec5aa8df4d1cfaad4ca99700dc2095a1ebeba816d75f2f0e3e2`。本实际PM写入前已完整读入并核对正式spec与主协调before原件均匹配。登记仅修改顶部Status/Handoff并追加本收据，**原r1全部正文、需求、版本/参数、allowlist、AC及风险保持原字节**。前文“当前草案”“未批准”“待Owner决定”等保留为获批原稿的起草时点事实；当前批准效力以本收据及顶部状态为准，不回写历史。

现已明确通过的范围门禁为：第3节A0源码与纯检查，及第11.1节限定的A1新建私有临时目录/合成v2与v3 SQLite验证。A1仅可使用本任务从零生成的合成夹具与已列故障/容量/恢复动作；不读取、复制、挂载、迁移、清理或覆盖任何既有SQLite配置、历史或原联调profile。原schema/样本/回执保护、必要增量验证和不重复阶段B整套的限制持续有效。

**B仍未批准。** 实际HTTP或loopback监听、DS/MySQL联调目标、数据库/schema/source采用及Docker资源/故障/清理操作必须另提第11.2节具体方案并批准；不能从A0/A1批准推断该运行授权。自动启动策略、旧历史上传、SMA、真实PLC/现场及生产部署继续排除；A0/A1实施或核验通过均不把完整阶段C记为完成。

下一实际角色为Development：在本spec原有限allowlist内创建自己的tasks.md，记录正式交付树、精确实现/命令结果、A0/A1输入/副作用边界、已知限制与资源归属；形成developer_handoff后，由唯一主协调启动新的fresh-context Verification。当前没有Development完成、独立QA或Owner最终验收结果，本PM不预建tasks/checklist，不代其书写事实，不另开notifier或执行产品/数据库/网络动作。后续完整阶段C仍须获批实际联调、相应独立核验及Human Owner最终确认。

本次批准登记使用aiis/project-governance核对范围与角色归属，并复读根AGENTS/README/PLAN、最近DAA文档、workflow/pm角色及完整原spec。stdlib文件比较/哈希、metadata、链接/空白与恢复原稿检查，以及本文件`git diff --check`均用于文档自检，不冒充Development检查或独立QA。登记版最终SHA及精确差异检查结果在handoff输出固定，避免本文件自引用。

## 15. r2待批范围、最小验证与PM交接

**r2尚无Human Owner范围/风险批准。** 第14节逐字保留的是r1历史收据，不授权新增实现。r1 archive、tasks/checklist的失败/已关闭finding和有限通过均不被本草案覆盖。批准后仅实施第10节限定恢复增量，DEV固定r2候选/影响diff/命令/新profile/durable before，再由新的fresh Verification核对应AC和证据复用。完整阶段C仍须获批B、真实证据及Owner终验。

| 最小增量 | 必须保留的证据 |
| --- | --- |
| 格式/指纹 | 内外原字节/SHA、两份静态DDL golden，重复/未知/超限/损坏反例；row/计数变化不改变指纹。 |
| 初始化中断 | 各durable边界的sentinel/staging/两库/credential状态，no-replace竞争、sync/close失败；半态无业务准入、不自动续装。 |
| cold兼容/拒绝 | 新合成v2/未封存r1 v3 cold正常、hot拒绝；坏credential不降级；替换/链接/WAL/双journal/未知平台守卫。 |
| 真实hot ACK | cacheflush返回0、子进程_exit86、journal与durable before、正式factory精确776/native rollback/完整RO后检及同身份unknown停止态；不得正常Drop替代。 |
| 锁/第二次退出 | 真实锁竞争、TOCTOU注入，恢复前/native后RO前/RO后业务前独立进程退出，下次仍后检，无半ACK/自启。 |
| 失败/物理预算 | 区分已/可能恢复写与业务拒绝，无持久日志提前写；辅助文件/256KiB与既有32MiB分账，必要SQL/容量触达回归。 |

仅选新增/触达测试、Rust编译/fmt及说明/i18n/link检查；相同源码的上传canonical、F002–004、8MiB普通SQL等QA2证据可复用并核候选SHA，不因Revision变化机械重跑全套。macOS真实进程阶段退出不等于SQLite pager内部断电；Linux/Windows原生、实际HTTP/DS/MySQL/Docker、原生视觉及B手册仍分开。未批准不新建fixture、不启执行notifier窗口。

供Owner复制的**范围批准语句（尚未发生的批准）**：

> 批准 DAA-008 r2，按 STD 仅完成本 spec 新增的新空 profile 初始化凭据和受控 SQLite 原生热回滚恢复，并执行第 11.1 节有限合成 SQLite 增量验证及新的独立核验。明确接受 R02 所列有限例外：只对凭据、文件身份、已知头及精确错误 776 均符合的新封存 profile，原生恢复写入可以先于 SQL 元数据重新读取；恢复后必须完整核验，本地凭据不构成认证或完整防篡改证明。已有 SQLite 配置、历史、原联调 profile 及 r1 未封存/失败夹具不迁移、不封存、不清理、不覆盖；沿用未变 r1/QA2 有效证据，不重复阶段 B 或整套测试。实际 HTTP／DS／MySQL 联调环境与 Docker 操作另提具体方案批准；自动启动、旧历史上传、SMA、真实现场及完整阶段 C 最终验收仍另行推进。

PM本轮只写spec，不改只读r1 archive、tasks/checklist、源码/配置/索引；主协调负责四处索引机械同步及无依赖资源收尾，必要旧hot/原文/候选证据保持且不复用。文档工具首次UTF-8输入失败、首次补丁上下文未匹配均未写文件，随后用apply_patch完成；不当作产品失败或新增验证。最终文档自检只核文字/链接/SHA/范围/元数据及第14节逐字保持，不称产品或独立QA；真实结果在handoff固定。
