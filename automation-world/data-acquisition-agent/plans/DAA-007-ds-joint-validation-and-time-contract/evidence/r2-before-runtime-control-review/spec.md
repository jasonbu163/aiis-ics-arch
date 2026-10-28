Task ID: DAA-007
Revision: r2
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> 唯一coordinator /root -> Human Owner审阅精确DAA-007 r2；YAML常驻链退役、两应用.env/profile、统一pnpm tauri dev及一条根AGENTS约定均为同一待批准草案，停止该增量实施；r1原生联调、闭库对账、fresh Verification及最终验收仍未发生
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: DAA ManagedS7到DS的双实例读取与本地SQLite闭环、上海时间合同、日常启动配置及已完成YAML迁入的常驻链退役
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: aiis-ics-arch::DAA-007 r2 PM -> Human Owner exact revision scope approval -> Development -> fresh-context QA / Verification -> Human Owner final acceptance; r1 approval and execution remain historical evidence
Depends On: aiis-ics-arch::DAA-006 r3 owner_accepted import/naming baseline; finite DS protocol delivery explicitly adopted for this joint run and checked at B0
Related Task: aiis-ics-arch::ARCH-AW-005 r5; device-simulator::DS-001 r1; aiis-ics-arch::DAA-002 r2; aiis-ics-arch::DAA-003 r1; aiis-ics-arch::DAA-004 r1

# DAA–DS 联调、上海时间与日常启动配置 r2 草案

## 1. 当前效力与批准摘要

2026-10-27（Asia/Shanghai），Human Owner在DAA `.env.example`的两项旧YAML locator旁批注，经主协调转交本实际PM：

> 一次性 迁移已经完成，这个是不是可以拉出去了，这个不应该在常驻环境中吧。这里调整一下。然后ds和daa的env都教我写一下，并且告诉我这些env内的参数有什么作用？

本r2把“退出日常YAML迁入链”和“两个应用的最小.env教学”落成可审阅范围。**两应用从自身.env选择profile的能力是本次明确提出、仍待精确r2批准的代码增量**：不能从上述批注推断该新增实施面已获批准，也不能在当前版本教程中宣称这些变量已经生效。PM本轮只写本spec；不创建或修改真实.env、profile、数据库、实现或测试。

同日Human Owner进一步纠正普通入口：

> 不，不管后面aw中agent还是工具，用tauri的，都只用pnpm tauri dev启动。DAA：调整回`pnpm tauri dev`，snap7这个参数是什么意思，为什么现在会变成这样？

本纠正直接作为当前对话与教程的入口偏好，同一未批准r2据此修订，不另升r3或创建任务。拟由DAA应用配置承担必需driver feature，并在根AGENTS持久化一条对应约定；具体文件/验证写面并入本r2，仍等待一次精确范围批准。前一版未批准r2已保留于[evidence/r2-before-standard-entry](evidence/r2-before-standard-entry/archive.json)，spec SHA-256=`87fcc74c5eaa9f746e994c90f6d7c8a9787aa6efeba9f6fc3506020633d4276f`；不是已批准或已实施的版本。

r1已于2026-10-23获精确批准并完成有限时间整改/隔离准备，Development仍为`implementation_in_progress / awaiting_owner_native`。4项Rust、3项Node、driver编译、frontend build及静态检查是r1 DEV证据；M01–M09、闭库对账、developer_handoff、fresh Verification和DAA-007最终验收均未发生。完整r1批准登记版spec与当时tasks已原字节归档为[evidence/r1-before-r2](evidence/r1-before-r2/archive.json)，分别SHA-256=`2976f02121a5f300ba7cbcb09b75f0499b098ad4af09b7993f8878fa9dcff5e5`、`9149df3fe67c7fe0d8df426142ccd4b16029159038aa8ece0f3ae99fcc5d0b44`。归档是历史证据，本spec是唯一当前范围入口；tasks暂保留r1事实，checklist尚不存在。这个待批准过渡不能靠PM改写Development元数据或预建QA记录消除。

r2保留r1的R02–R05、R07–R09时间/存储/显示/联调合同及AC04–AC14、AC16；只对候选与批准身份、R06启动方式、R10增量检查、R11文档和封闭写面作必要修订，并增加R12–R14及AC17–AC22。**旧UTC/未知profile仍写前拒绝，新空双库仍为v2，既有配置、历史、原字节SHA及私有迁入receipt/source archive不迁移、不清理、不重编码。**退出常驻迁入不等于删除迁入历史；本任务不另造YAML工具、CLI、按钮、schema或第二套迁移功能。

本任务继续只补齐受控本地DS的真实S7读取到DAA本地落库闭环。DS的已接受协议/产品基线保持；本r2仅提议在封闭写面内增补其源码开发.env读取和说明，不修改其runtime、规则、权限、协议或既有验收记录。原生窗口、S7操作及合成配置录入仍由Owner执行；Development和Verification不操作窗口、不启动DS/DAA监听或客户端、不seed联调数据库。新增代码须先获精确r2批准并通过必要DEV检查，再由Owner完成一次M01–M09；之后仍须新的fresh-context Verification。

唯一active lifecycle coordinator为主会话`/root`。实际PM采用项目`pm`角色，配置`gpt-6.1-sol / max`仅作TOML配置证据；profile为`contract_only`。角色提示、bundle与diff审计是合同控制，不宣称平台ACL、强制路由或团队激活。

## 2. 消费依据与规划来源

本r2消费根AGENTS与README/PLAN双语、[canonical workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)、实际`.codex/agents/pm.toml`、`aiis`及`project-governance` skills、AW/DAA/DS最近README/PLAN、DAA app/local_store说明、完整DAA-007现有spec/tasks和归档、相关配置/启动/迁入/界面源码及DS owning acceptance。作用域未发现更近AGENTS。r1消费记录与规划输入保留在归档；本任务仍独立分类，没有Parent Task ID，不继承其他任务的批准或终验。

| 来源 | 当前可用事实与边界 |
| --- | --- |
| [DAA-006接受记录](../DAA-006-point-naming-and-import-reuse/checklist.md#owner-acceptance-r3)及[接受源码清单](../DAA-006-point-naming-and-import-reuse/evidence/accepted-source-manifest.json) | r3命名/导入复用已接受；core为0.1.0，profile为tia-subset-v1、siemens-step7-v20-standard-word-v1、tia-point-name-v1。三文件、原oracle和DIRECT overlay证据分层保留。 |
| [DS历史QA4及Owner接受](../../../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5) | r5候选`306a09d5317931482a59f45da5eafcb9d3ee739199799f475ade1891fb0b00b4`历史qa_passed；Human Owner已于2026-10-27接受r5/当前DS。原协议证据不是DAA应用SQLite闭环；本r2新增DS启动配置代码不能倒记为旧QA4或旧接受内容。 |
| [DS-001接受](../../../device-simulator/plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001)及[tasks](../../../device-simulator/plans/DS-001-policy-table-and-usability/tasks.md) | r1及当前DS已于2026-10-27 owner_accepted；tasks保留原Development时点。独立QA豁免只属于DS-001，不转移到DAA-007 r2。无需重新索取该产品接受。 |
| DS会话`01a14e52-eeb4-7c82-bade-bc0a237fa2ff`后续DIRECT | 时间/展示及13表列宽随“当前DS”已接受，原DIRECT和旧QA证据仍分层。B0继续固定实际候选并归因差异，不发跨会话消息，不接管旧bundle。 |
| [planning-source-baseline.json](evidence/planning-source-baseline.json) | 主协调于`2026-10-23T15:09:14+08:00`固定的规划输入，SHA-256=`568fecb0bd3ce89c095999fda9df9746bb38d49163860e5dd2df32bd2c13b067`；HEAD=`1fa1ce50a521ebd51c2c43389db011a76f2d74bf`，交付仍为dirty工作树。不是获批执行baseline。 |

规划清单按其定义固定DS227源、DAA158源、core12源；aggregate SHA依次为`9378b7aa24c16c5454652d99380b37cb51b48092f3db7eee67516da599e99ba3`、`ed10ea9638ee6aedff7071519ddce73b0f8fdd62fa8fa21654d5cbab02113461`、`2be84cf7a1720067797c1d78b5b204616d1d1f11d571da36ceea9a6ac045a1d7`。它排除实际env、库、日志和产物，不从HEAD推断并行工作归属；执行前重核逐文件身份和影响。

r1的规划→执行漂移归因、已实施时间合同和检查见[tasks](tasks.md)及[准备候选](evidence/prepared-candidate.json)。冻结的32路径实现aggregate SHA-256为`011c3238f02211125b6a3f4c23affc4614bf58cb40188d32c40cf11c600c2486`，源输入397项；这些是原r1候选事实，r2实施前后分别留存新的before/增量/候选，不能覆盖旧清单或套用旧pass。

2026-10-27只读源码确认：DAA普通bootstrap仍构造默认两个`MigrationPaths`，`LocalEngine::open`会调用迁入startup；既有私有receipt防重，新空profile仍可自动引入仓内`PLC_1`候选，删掉.env两行不能取消该行为。composable在reload及成功save后仍查询migration，ConfigRevisionBar仍挂接unknown/failed故障与retry弹窗。DAA自有.env白名单尚不消费`DAA_PROFILE_DIR`，profile只读进程覆盖；DS bootstrap目前也只读进程`DS_PROFILE_DIR`，其.env.example明确无自动加载。两应用Vite均`envDir:false`；不能把Vite当作Rust启动配置加载器。R12–R14只针对这些已定位事实。

DAA当前`package.json`的`tauri`脚本只是Tauri CLI；两个自定义dev别名另传`--features rust-snap7-driver`，而Cargo `default=[]`、Tauri `build`尚未配置features，所以两种命令的编译图不同。`rust-snap7-driver`启用已有可选`rust-snap7`依赖及ManagedS7的真实S7驱动分支；缺少它时显式连接返回`driver_unavailable`。它是编译配置，既不是选择DS/真实PLC的运行参数，也不能由`DAA_PLC_READ_ALLOWED=true`补编出来。DS已有Tauri `build.features=[native-s7]`，正常`pnpm tauri dev`会携带所需feature；r2沿该最小既有做法修正DAA，不改变Cargo默认features、驱动代码或依赖。

## 3. 前置决定与停止条件

| 编号 | 执行前必须成立的条件 |
| --- | --- |
| D01 | Owner明确批准精确`aiis-ics-arch::DAA-007 r2`，含YAML常驻链退役、两应用源码开发.env/profile、统一普通入口及一条根AGENTS约定、修订allowlist/AC/风险。r1批准继续是历史事实，不授权本增量；当前草案等待一次完整r2批准。 |
| D02 | DS-001 r1及ARCH-AW-005 r5已有真实Owner接受，可引用所属记录，不另索取DS旧产品终验。B0在相关并发修改停止后固定当前DS/DAA/core/fixture逐SHA、features、工作树与命令链；DS新增.env行为单列为本r2 delta。所需联调能力仍限双实例、端口/TSAP、两DB/类型/初值、启停/规则暂停和只读S7，不要求长期容量/全部扩展完成。 |
| D03 | 当前DS与历史r5/规划快照有差异须逐项归因。纯展示且不影响所需操作、协议、依赖、风险的变化，可在B0记录受影响hash和对应证据；协议/接口/依赖/语义/风险/allowlist实质变化返PM新Revision及Owner批准，不静默改成“任意最新DS”。 |
| D04 | 使用正式交付源码，不复制临时工程。联调继续使用r1为Owner建立的独立合成profile，在Owner/协调者核归属及仍符合本次新空前置后沿用；不因r2重建、切换、seed或复制数据。两个应用各自.env由Owner按批准后教程自行建立/编辑一次，本草案不触达现有真实.env。默认/真实/历史profile、旧76样本或客户输入不属本次联调。 |
| D05 | Owner核15194（DS）、15191（DAA）及30102/30103归属、可用性和已有窗口；冲突保留他人进程并停该步骤，不能回退102、扫描替代口或改固定端口求通过。 |
| D06 | r2精确批准、必要增量实施/检查及新候选freeze先完成，手册才进入Owner执行。未变r1证据按受影响面复用，不重复整套B/DS矩阵。实际DS/DAA来源漂移未解释或所选profile不符合前置时停止相关动作，不静默切换目录。 |
| D07 | 正常退出后才由DEV/QA只读核本次合成profile；mode=ro/query_only、明确绝对路径、无seed/DML/DDL/ACK。证据缺口保留并只补受影响条目，不重跑整套B/DS矩阵或固定三次关窗。 |

## 4. 编号需求

### R01. 精确候选、原数据保护与角色归属

精确r2批准后Development在现有tasks中保留完整r1事实，再建立r2段与匹配元数据，固定批准spec SHA、执行before、任务增量/新增全文和保护面；PM不代改tasks。未批准前tasks继续是r1历史，不把两者暂时Revision不同误写为r2已经handoff。读取旧bundle不改其记录或状态，不把整个dirty HEAD差异归因本任务。旧source/revision/context/sample/manifest/receipt、ID/generation/sequence/delivery/reference及76样本不读写、不重采；仅R12/R13测试可用DEV自造v2材料核私有receipt原字节保护，不能借此打开真实/默认旧库。DS只限§6列明启动配置与文档delta，其余源码、core/oracle和并行改动保留。

### R02. 新空profile的显式时间存储合同

新空profile沿现定位`local-acquisition-v1/config.sqlite`、`runtime.sqlite`初始化**存储schema v2**；目录名保留为定位兼容，不代表库版本仍为1。两库`user_version=2`，instance_metadata/runtime_metadata的schema_version=2；分别新增固定`time_profile TEXT NOT NULL CHECK(time_profile='asia-shanghai-rfc3339-ms-v1')`。application ID、匹配instance ID、DELETE/EXTRA、profile独占锁、有限队列、容量预留及fail-closed规则保持。

只允许新空库的完整CREATE及初始化：schema_migrations直接记version2和上海applied_at，不在旧库执行ALTER/UPDATE/迁移ledger回填，不自动复制/改目录规避检查。现有schema中的版本字段按责任区分：

| 表面 | r1固定版本与时间含义 |
| --- | --- |
| 双库user_version、instance_metadata/runtime_metadata.schema_version、schema_migrations.version | 2；两库time_profile完全匹配固定常量。 |
| samples.schema_version及SamplePayload.schemaVersion | 2；采集/保存时间为固定毫秒`+08:00`；原字段形状和SHA算法保持。 |
| CycleManifest.schemaVersion | 2；轮/读取/保存日历时间同新合同，成员与摘要仍覆盖原字节。 |
| Configuration JSON、configuration_revisions.schema_version及configuration_contexts.schema_version | 1；只承载既有配置结构，不因存储版本改名/改ID或重编码旧context。created_at作为新库独立日历列采用新时间合同。 |
| ConfigurationView、snapshot/history/raw等普通IPC envelope | 保持原外形及既有版本；其新产生的业务日历字段为`+08:00`。raw字段里的样本/manifest自身为2，不能与envelope版本混淆。 |
| 新profile内YAML receipt/原source归档 | 原receipt结构版本不变，新committedAt遵循profile时间合同；输入source字节及其协议/文字日期不做时间替换。旧receipt不迁入、不重写。 |

### R03. 旧UTC、未知或不匹配profile在写入前拒绝

在ProfileLock可能建文件、任何RW SQLite连接、PRAGMA持久变化、hot-journal恢复、双库recovery、clean_exit更新、日志目录/文件、迁入和actor启动前，以只读连接/元数据探测两个已存在库。legacy v1、time_profile缺失/未知/不一致、单库或身份异常均拒绝；无法无写读取的异常journal也拒绝，不以immutable忽略journal。不能先可写打开再检查版本。

只对合格v2或真正空目录取得原独占锁，并在任何RW打开前再次核身份/版本/time_profile及文件变化；竞争/漂移拒绝。旧profile拒绝分支不得创建替代库、清日志、恢复意图或写回任何旧记录。DEV用自己构造的legacy/未知/错配fixture核前后文件内容和目录清单，不为门禁访问默认旧库。

零写证据须精确区分：legacy/未知合同在前置探测即拒绝时，尚未取ProfileLock，profile目录及全部原件不变；合格v2/新空profile才允许创建锁文件，若锁后复核发现漂移则在RW前停止、原业务库不变，如实记录已形成的锁文件，不把这个不同分支写成目录从未发生变化。

采用稳定`time_profile_unsupported`错误及明确原因。Tauri可显示无engine的诊断壳：具名bootstrap返回该错误，业务动作不可用，前端中英提示“此profile的时间合同不受支持，旧配置和历史已保留；请使用新的隔离profile，旧数据迁移需另行批准”。不提供自动迁移/清库/换profile按钮，不panic成无说明退出；持久日志未启动时只向stderr/stdout写结构化拒绝，不能用日志写入破坏拒绝边界。

### R04. 统一时间helper、查询和维护语义

Rust与前端各有一个集中时间工具，固定`Asia/Shanghai`及`asia-shanghai-rfc3339-ms-v1`，复用已有chrono/JS能力，不加依赖。新产生的业务日历时间一律规范为`YYYY-MM-DDTHH:mm:ss.SSS+08:00`：读轮/逐段/观察/保存、配置版本和activation intent、migration ledger/新receipt、runtime event、snapshot generatedAt及诊断testedAt。SQLite defaults/初始化、参数写入与维护不能再暗产Z或依赖宿主localtime；保存时间在同一事务内生成一次并被该轮样本/manifest/索引列复用，明确它是持久化事务时间，非PLC事件发生时间或精确COMMIT后时刻。

结构化stdout与持久JSONL的日历时间同为`+08:00`，保留各自既有毫秒或更高诊断精度，不降为UI秒。当前LocalLog::new的tracing_subscriber默认timer会另产UTC，须用集中工具的FormatTime适配替换；文件`at`与stdout`timestamp`各自是日志生成时刻，不保证逐字相同，也不冒充PLC保存时间。只改时区/格式适配及必要定向断言，原轮转mutex/32MiB预算/失败锁存与事件level保持。

外部RFC3339边界先解析一次、转换为同一上海固定毫秒格式，随后比较；非法/逆序区间拒绝。新+08文本不能与转换后的UTC Z边界直接SQL比较。history依既有saved_at筛选和sample_order游标；retention截止值、版本排序和恢复时created_at比较采用同一合同。此r1 retention_days沿用滚动days时长，不新增自然日/班次统计；测试包含上海跨日、同瞬间不同offset、毫秒边界和宿主TZ不同的结果一致。

sourceSeq/sample_order仍表示持久顺序，单调时钟仍用于deadline/调度/耗时，Unix值按其语义处理；系统校时回退不能伪造未来日历值或重排源序号来掩盖。新存储不能写入混合offset或无offset的业务时间。不会对历史rawpayload/manifest/context进行重新序列化、替换Z或重算SHA。

### R05. 业务时间显示、筛选与历史列宽

历史savedAt、最老pending及陈旧snapshot提示按上海24小时`YYYY-MM-DD HH:mm:ss`显示，页面统一解释时区与事实语义。历史日期控件的墙上时间固定按上海解释，不能随本机Date默认时区变化；选择起止秒时from为该秒`.000`、to为该秒`.999`并保留原后端闭区间语义。无真实时间显示缺失，不用界面刷新冒充保存/更新。底层/IPC与诊断JSON及原日志继续保留毫秒；原字节详情不拿格式化视图替换。若显示已提供的UTC诊断原文，只在独立view转换一次，原文/SHA保留；不因此承诺旧profile可在新runtime查询。

仅本次历史业务表接入应用内公共列宽工具：普通列可拖拽且有合理min-width/横滚，操作列可固定；按应用/表/稳定字段ID保存本机偏好，翻页/筛选/刷新/切页及重开恢复；有“恢复默认列宽”，无效字段/损坏偏好回默认。此偏好不进SQLite业务配置/配置版本，不以翻译标题作key；不改CU公共接口、DS或全DAA表格。日志原文面板属于精度诊断，本任务不借时间整改重做其表格结构。

### R06. 正式入口与合成启动配置

本r2获批并实施后，Owner在各应用自身根.env中一次写好明确的本次独立绝对profile；DAA与DS的普通启动均仅执行`pnpm tauri dev`。DAA在`src-tauri/tauri.conf.json`的`build.features`配置`["rust-snap7-driver"]`，让标准Tauri CLI链携带已有真实S7驱动；DS沿用其`native-s7`配置。用户不再选择驱动别名或手填feature；`local-validation`与DS `test-automation`均关闭。read gate仍默认false，驱动可用不自动连接/启采，更不开放写入。

DAA Cargo `default=[]`及依赖/锁/ManagedS7实现保持，直接Cargo的DEV合成/validation检查仍可不编真实驱动。`package.json`仅在统一入口确有必要时收敛重复dev别名，不改依赖、版本、其他build/headless脚本或批量清理历史命令。Tauri配置只改`build.features`；本次不授权安装包、发布构建、签名或跨平台支持。真正运行路径须由后续Owner M01的普通命令和M04的S7读取证实，显式feature编译通过不能替代它。

配置优先级、三个日常键、继承变量检查与一次性教学见R13–R14。联调read gate须由Owner明确设true；模板仍false。true不自动连接/采集，保存、激活、连接、启采仍显式。r1为阻止样例迁入设置的两个空YAML locator不再是r2启动前置，不以替换路径/缺失文件伪装退役。env/profile不提交；DEV/QA不编辑真实.env或Owner profile。两应用开发/构建不会自动隔离数据；本次仅用原Owner合成profile，不回默认目录，不新增启动脚本、任意SQL/文件/网络IPC。

### R07. 双实例、同布局异值与两个跨DB组

DS_A（显示名B007-A）=`127.0.0.1:30102`，DS_B（B007-B）=`127.0.0.1:30103`，rack0/slot1，Calling TSAP0x0100（256）、Called TSAP0x0101（257）；两台DS独立UUID/内存，DAA独立plcId/point.id。只读输入为现有[multi.db](../../src-tauri/tests/fixtures/source-import-multi-db/multi.db)及[types.udt](../../src-tauri/tests/fixtures/source-import-multi-db/types.udt)，只选Alpha/Beta，Beta仅绑定Measure闭包，显式映射DB71/88；不选Gamma等其他声明，不改fixture/oracle。

| DB/完整长度 | 叶、类型与标准地址 | DS_A显式初值 | DS_B显式初值 | DAA组 |
| --- | --- | --- | --- | --- |
| Alpha / DB71 / 4B | ready BOOL byte0 bit0 | false | false | Fast_500 |
| Alpha / DB71 / 4B | count INT byte2 | 101 | 202 | Slow_1000 |
| Beta / DB88 / 8B | unit.running BOOL byte0 bit0 | false | true | Fast_500 |
| Beta / DB88 / 8B | unit.value REAL byte2 | 12.5 | 25.0 | Slow_1000 |
| Beta / DB88 / 8B | bytes[3] BYTE byte6 | 18 | 86 | Slow_1000 |
| Beta / DB88 / 8B | bytes[4] BYTE byte7 | 52 | 120 | Slow_1000 |

每PLC恰6启用点，地址按完整非优化结构预览并确认，保留原sourcePath/技术名/opaque ID。Fast_500=500ms、仅两BOOL；Slow_1000=1000ms、其余4点；每点只属本PLC一个组，无重复/遗漏。每组都跨两DB：每个完整Fast轮为2个单点样本，Slow轮为DB71一个点＋DB88三个点两个样本；同一轮不是两个独立成功提交，跨DB读取也不构成PLC原子快照。DB号/端口/值是本任务合成实例，不成为产品固定拓扑。

DS六点clientRead=true；ready为toggle、rule owner、halfPeriodMs=1000（每半周期翻转，完整周期2000ms），通用periodMs=2000、phase=0，其余规则参数保留既定默认，三类写入禁止。false是显式初值，不是规则base字段；count及unit.value为hold、UI owner，仅允许Owner普通UI写；unit.running和两个BYTE为hold、owner none、三类写入禁止。未列权限保持false，不开放S7客户端写入。启动后先暂停规则，ready可能已翻转，以暂停实际快照为静态对照。技术名依次为DB71_ready_Bool、DB71_count_Int、DB88_unit_running_Bool、DB88_unit_value_Real、DB88_B6_Byte、DB88_B7_Byte，两端按路径/地址对齐，不比较UUID。

DS显式确认初值/策略并保存→停止时加载→显式启动；`:=7`、BEGIN和RETAIN不导入/执行、不代表重开保值。DAA亦经导入预览→确认地址/技术名→分组启用→保存→激活后另行连接/启采。所有值来自真实ManagedS7大端读取/解码，不来自DS UI对象、fixture transport、缓存猜值或另写Python客户端。

### R08. 稳态、暂停规则、断线与恢复

Owner先只配置并连接A、做单点核对和约10秒静态采集，再验证变值，之后按M06加入B；新增B并激活时保留A身份/历史，依工作台实际状态显式重连/启采。两台稳定后在A再做一次单点诊断，B继续；诊断复用A的同一会话/串行actor，保留真实值/质量/时刻。双实例稳定段须两台每组至少两个完整good轮、两个周期的实际节奏及各自不同值；不要求固定每tick样本总数，也不把低负载试验当吞吐保证。

暂停的是DS规则推进，实例仍通信；暂停后以当前实际值为静态对照，DAA继续有新good轮。M05恢复规则并在约15秒段观察ready的true/false；Owner在DS_A以普通UI写入将count101→111、REAL12.5→13.25，DAA只经S7读到新值，旧样本保持。之后再次暂停规则，按实际快照核新good轮；不新增ramp或其它规则。Fast/Slow稳定轮间隔接近500/1000ms、轮数约2:1，按实际轮时刻/耗时解释，非1Hz界面刷新或某页行数证明，动态截图相邻时刻不要求相等。

只停止DS_A，DS_B及其两组继续有good新轮；DAA_A真实反映disconnected/reconnecting或读取失败，不把旧值标成新good。重启DS_A后按既有退避收敛：当前backoff最大30s加0–20% jitter，连同connect1s/round5s及1Hz界面预算，在无额外故障条件下以45s为一次人工观察窗；超窗保存事实并只处理受影响项，不改阈值求绿。恢复后产生新good历史，source generation/seq和revision身份按本实例事实连续可核，不补造断线期间PLC真实值。

通信失败的已提交轮保留null与bad_read/bad_timeout等原因，sample/cycle质量按原good/partial/bad规则；无连接时可能不落每tick失败样本。记录缺失区间与实际失败轮是不同事实，不能以“没有每tick坏行”改写为有完整现场历史或凭空造行。

### R09. 同轮SQLite、历史与正常退出重开

链路为ManagedS7→真实decode→精确组成员→同一runtime事务的collection_cycles、两DB samples、manifest、pending和next_seq。origin必须`s7`；snapshot外层origin不是样本来源证明。每PLC同generation的sourceSeq十进制严格前进、跨组共享序列可自然跳号，重开不重置；样本/manifest/context的原字节SHA与引用一致，pending每样本一条，无ACK/清队列。

Owner使用PLC/组/质量/上海时间边界及分页查历史、打开原样本/manifest/context；对照同一合成库。正常停止采集/断开→正常退出DAA→同一profile重开一次，连接/采集意图均stopped，旧配置、active/loaded解释、已落样本及原SHA保留，尚未显式启采前不新增业务样本。不要求反复三窗，不做强杀/断电/长稳或重新故障矩阵。

### R10. 必要DEV检查、Owner操作与独立核验

Development只运行受影响的fmt/locked编译、有限配置/退役/时间门禁测试、DAA前端build及双语键/占位符/链接检查，不升级依赖/锁或新装框架。r1未变的4项时间测试、3项Node时间/列宽结果及原raw/hash可按候选与影响复用；若改动实际影响其断言，再只补该影响项，不为了换Revision机械重跑。legacy/v2测试库均为DEV自建材料，与Owner联调profile隔离；不能seed Owner同库或重跑DS协议/16连接/全B容量/76样本/完整导入矩阵。

批准后的检查以实际受影响面为准。下表中的r2检查尚未执行；r1已执行结果只见tasks，不重标为r2 pass。定向测试可同时覆盖相同features的默认编译，不机械追加同候选同features的check；过滤0项不能计通过。使用既有Cargo/Node通道和锁文件，记录真实argv/cwd/features/exit/raw与候选。

| 计划检查 | 批准后命令/边界 |
| --- | --- |
| Rust格式 | DAA和DS各自目录`cargo fmt --manifest-path src-tauri/Cargo.toml --check`，不使用写入式fmt。 |
| 两应用配置合同 | 各自目录`cargo test --manifest-path src-tauri/Cargo.toml --locked --no-default-features --lib startup_env`；仅现有config模块内有限用例，覆盖R13选择/解析/失败与验证分支隔离，不启产品/native/S7。 |
| DAA退役与receipt保护 | DAA目录`cargo test --manifest-path src-tauri/Cargo.toml --locked --no-default-features --lib resident_retirement`；DEV自造v2 profile/receipt，核普通engine无迁入、兼容只读和retry写前拒绝。保留旧迁入算法/测试，必要时仅调整原有受影响启动假设。 |
| 标准入口与正式编译图 | 静态核`pnpm tauri dev`→package `tauri`脚本→Tauri `build.features`→Cargo feature/dependency/cfg；DAA仅配置已有rust-snap7-driver，Cargo default仍为空。DAA使用`cargo check --manifest-path src-tauri/Cargo.toml --locked --no-default-features --features rust-snap7-driver`；DS原生图已有证据按受影响面复用，若本r2 bootstrap影响该图才补同式`--features native-s7`。只编译、不启动监听；直接Cargo合成/validation通道保留无真实驱动的选择，受影响保护分支只补必要编译，不运行旧全矩阵。 |
| DAA前端类型/构建 | `pnpm build --config vite.validation.config.ts --outDir <本次绝对owned-dist> --emptyOutDir`；或记录既有envDir:false配置与显式outDir的真实等价argv。仅验证迁入UI解绑相关类型和构建。DS前端未改，不为.env文档再重建其前端。 |
| r1时间/列宽合同 | 未变代码及raw/SHA复用；若实际受影响，仅补`time_contract`过滤或`node --test tests/time-and-history-preferences.test.mjs`所需项，不更改宿主时区。 |
| 文档/locale/差异 | 复用现有工具及有限内联只读检查，记录真实argv、键/占位符/本地链接与allowlist结果，不造通用治理脚本。 |

Owner完成手册P00与M01–M09，记录实际输入、动作、时刻、值/错误、正常退出、候选/features及必要截图/日志；允许一次连贯记录，无固定截图张数。Development可在退出后只读对账，再交精确developer_handoff。新的fresh-context Verification独立核批准spec、tasks、before/diff/候选、必要自测和Owner操作/同库记录，独立运行有必要的受影响纯检查；不驱动窗口、不重新建联调链、不重跑无变更矩阵。Owner报告与QA直接核得的字节/查询结果分别标识，缺必要证据为blocked、实际失败为failed，均保留历史；仅复核失败影响项。

### R11. 文档交付、风险和阶段门禁

双语联调手册保留前置freeze、真实启动/features/profile、模型/分组、时间兼容限制、逐步动作/预期/恢复和空白结果表；据R14补最短.env教程。DAA/DS的README pair、DS USER_GUIDE pair及两.env.example同步实际已交付配置行为；DAA app/local_store说明只更新退出常驻迁入与历史receipt保留的相关段落。批准前和实施后状态分开，不能把未来.env能力或未发生的Owner操作写成pass。索引仅由主协调机械同步，权限链不因文档存在自动执行。

DAA-007 QA通过只进入Owner最终验收。其接受不代验DS-001、ARCH-AW-005或DAA-002/003/004；整体B还须有限DS基线确认、本闭环全部必要gates及Owner明确“接受整体阶段B”的决定，旧任务pending按各bundle独立处理。C仍需B整体接受、稳定Backend合同及另行批准；本任务不启上传、补传、ACK、Backend/SMA或现场行为。

### R12. 已完成YAML迁入退出普通常驻链

普通源码开发启动不再构造/发现两个YAML locator，不调用迁入startup/discover/execute或读取/散列默认/显式YAML。移除.env.example的`DAA_PLC_CONFIG_PATH`与`DAA_PLC_SNAPSHOT_POLICY_PATH`；这两个旧键即使仍存在于Owner文件或进程环境，也不决定普通启动、不触发迁入、不输出其值，不自动编辑Owner文件。新的真正空profile完成既有v2初始化后保持空业务配置，不出现`PLC_1`，也不为表示“已退役”新增/改写receipt、source_documents或草稿ETag。R02/R04中receipt时间语义仅约束历史保留/DEV自造材料；r2普通启动不产生新迁入receipt。

解除`useLocalAcquisitionConsole`的reload、成功save与迁入summary/retry调用链，ConfigRevisionBar不再挂接迁入故障入口/弹窗。保存成功不能因退役summary查询失败再显示迁入错误；原草稿/CAS/激活/错误、快照陈旧、导入和时间显示不变。不增加迁入历史页、迁入开关、独立工具或新CLI。现有私有receipt、白名单source archive及前缀保护继续保留，普通保存/导入/裁剪不删改它们；不改DDL、保留前缀或既有记录格式。

可保留现有具名兼容IPC以免无关扩大注册变更，但语义必须最小且真实：仅显式`daa_get_yaml_migration`可从已准入的本profile SQLite读取原私有摘要，不探测YAML、不写receipt/ETag。无receipt时使用既有真实DTO表达`not_attempted`或`existing_sqlite_preserved`，不能伪装`validation_excluded`、成功、失败或已经迁移；现有receipt摘要的历史字段/原字节保留，只在返回视图强制`retryAllowed=false`。`daa_retry_yaml_migration`无条件返回稳定`yaml_retry_forbidden`，在storage写任务/配置变更/文件读取前拒绝。普通界面不自动调用这两个兼容入口；不为兼容保留可执行迁入路径。

不要求删除旧YAML样例、算法和测试。为避免退出运行链后产生新的production dead_code/unused警告，可在列明domain/infrastructure/service/store文件对仅历史迁入使用的类型/导入/函数作必要`cfg(test)`编译隔离，保留可追溯的历史测试；不能用新增`allow(dead_code)`、空壳调用或假locator遮掩问题。已有test-only `empty_for_test`警告不在本轮清理范围。若需要修改更多算法、依赖或路径，先返PM，不把退役扩成整树清理。

### R13. 两应用最小源码开发.env/profile合同

只面向本仓正式源码普通开发启动，复用各应用原有入口和依赖。DAA读取既有自身根.env或进程显式绝对`DAA_ENV_FILE`所选文件；DS仅新增读取自身源码根.env，不新增`DS_ENV_FILE`或共享配置库。源码根由本应用既定`CARGO_MANIFEST_DIR`定位，不依赖调用者cwd，不扫描父目录、仓根、CA、Backend或另一个应用.env；Vite `envDir:false`保持，不把Rust启动参数暴露到VITE变量。安装包的.env发现、分发、热重载及跨平台打包保证不在本次验收范围；除R06标准入口的build.features接线外，不为.env增加打包或资源寻址配置。

| 键 | r2拟交付优先级/缺省 | 作用与限制 |
| --- | --- | --- |
| `DAA_PROFILE_DIR` | 非空进程值 > 所选DAA自有.env非空值 > 原独立应用默认目录 | 选择DAA profile根，双库/产品日志仍按既有相对位置；不是PLC配置或数据迁移指令。选定值必须为绝对路径，不自动复制/移动数据。 |
| `DAA_PLC_READ_ALLOWED` | 进程值 > 所选DAA自有.env值 > false | 仅允许后续显式S7读取；不启用PLC写入、连接自启、采集自启、上传或ACK。模板false；联调由Owner明确改true。空/不识别值按原保守布尔合同回false。 |
| `DS_PROFILE_DIR` | 非空进程值 > DS自身源码根.env非空值 > Tauri原app_local_data_dir | 选择DS profile根及原有SQLite/日志/WebView身份；空配置是新目录的事实，保存/加载/启动仍分开。 |

`DAA_ENV_FILE`仍只由进程选择DAA env文件，是高级可选项，不写入日常.env模板的有效键，不从.env递归选另一个文件。不存在默认.env时允许按原缺省；有意指定的env文件必须是有效可读UTF-8普通文件且绝对定位，失败在profile锁/开库/日志之前明确拒绝，不退回默认.env。默认.env存在却不可读或含非UTF-8时也明确拒绝；不吞成配置缺失。只返回稳定错误码/键名/来源，不在IPC、错误或日志中转储env正文、凭据或任意变量值。

两个profile键的缺失/空白模板值视为未设置；一旦选择了非空显式值，必须先校验绝对路径、父目录穿越及既有symlink拒绝边界，再进入原profile/时间合同准入、锁和数据库打开。错误值明确拒绝，禁止静默改用默认profile或建立旁库；不能通过canonicalize到另一目录来“修正”Owner选择。DS复用其现有runtime profile resolver；DAA在当前config/bootstrap内最小补齐选值校验，不改底层锁策略或时间preflight。合法未存在目录仍由原正式打开链处理，不由env加载器预建或seed。

解析仅使用现有简单`KEY=VALUE`形态：trim键和值、忽略空行/行首`#`、可去一层成对单/双引号，重复键沿用首项生效并说明。只消费上述本应用活动键及DAA原mode退役识别所需键；旧YAML值不再作为locator消费，其他未知值不保存或传播。不得shell source/eval、执行命令、展开`$VAR`/`${VAR}`/`~`或跨文件插值；不为此新增dotenv依赖/锁变更。相对路径、变量表达式及示例占位符都不能被误当作可用profile。

DAA debug `local-validation`的固定显式参数、owner marker、继承DAA变量拒绝、fixture/release保护保持；DS `test-automation`仍以原显式manifest profile为权威，不让源码.env覆盖/逃出测试边界。原测试宿主、runtime配置和协议不加入.env加载；只在普通桌面bootstrap接入。必要测试在自有临时env/目录或纯选择函数运行，串行隔离进程env并恢复，不能读取真实.env、Owner目录或系统默认应用数据。

### R14. 三个日常键的短教程与原Owner profile沿用

双语.env.example/README、DS USER_GUIDE及DAA JOINT_TEST_GUIDE说明文件的准确位置、如何手工复制`.env.example`为`.env`并编辑、每个活动参数含义、优先级、绝对路径与无shell展开规则。教程区分“当前r1”与“r2获批并实施后”，后者交付前不得指示Owner依赖尚未支持的.env profile。既有真实.env不覆盖，已有内容由Owner核对后只改自己的活动键；不要求source/env导出整份文件，不新建启动脚本。DAA旧`DAA_RUNTIME_MODE`兼容语义保留在说明，不列为正常使用必填项。

普通安全模板只呈现三个日常键：DAA的可选`DAA_PROFILE_DIR`与`DAA_PLC_READ_ALLOWED=false`，DS的可选`DS_PROFILE_DIR`。空profile配置值表示原默认选择，与“新空profile目录”不同；须直接说明两应用dev/build与安装版不会自动隔离数据。DAA默认目录若含旧UTC/未知时间库仍由r1门禁拒绝，不能以教程让用户反复启动/更换目录规避。PLC端点、点位、组、规则和初值保存在各自SQLite/UI中，不进入.env；YAML一次迁入已退出普通常驻链，receipt/source archive仍在原库保留。

本次联调示例一次填实r1已建立的`/private/tmp/daa-007-r1-exec-e6s14xue/owner-joint-run/daa-profile`与同根`ds-profile`，只有在P00确认路径归属/状态仍符合原前置后才沿用；不创建第三套profile、不把DEV测试库/fixture复制过去。原`RUN_ROOT/daa.env`是r1准备历史，本r2不自动改写/删除它；Owner若仍有进程`DAA_ENV_FILE`或PROFILE覆盖，教程说明其优先级并一次核对/按需unset，以免误以为应用根.env生效。后续同一终端正常启动两个应用均只需`pnpm tauri dev`，无需每次重复长profile路径或驱动feature。重开仍用同一配置/同一profile，不重做全流程。

联调专属DAA.env由Owner明确写read gate=true，旁边解释安全模板为什么仍false，以及true之后还须在UI显式激活/连接/启采。P00/M01/M09记录解析后的实际profile、候选/features/配置来源及停止初态，不把短命令等同于默认profile。日志或bootstrap只使用原有安全定位/门禁输出，不增加env全量展示或新IPC。

根AGENTS仅新增一条长期约定，拟文为：“本仓使用Tauri的AW agent与工具，面向使用者的普通开发启动统一使用`pnpm tauri dev`。应用运行所需Cargo features由该应用Tauri配置统一传递，不要求使用者改换启动别名或手填驱动feature；专用测试、编译与打包命令在相应任务文档另行说明。”本r2只将DAA实际配置和现有DS说明对齐，不批量修改冻结CA、SMA或其他工具，不更改shared AIIS skills、workflow、角色或其他治理条款。两应用README/手册/模板不再把驱动别名作为日常入口；仅在必要说明中简短解释Snap7是现有S7通信实现与编译feature。

## 5. 实施顺序与人工步骤映射

| 顺序 | 责任与退出条件 |
| --- | --- |
| G0 | r1批准及实施记录已存在；本次只等待精确r2新增范围批准，不重新索取r1批准。未批准前不实施R12–R14或扩展写面。 |
| B0 / P00 | Development保留r1历史并固定r2 before/正式源码/features/fixtures/依赖与并行差异；引用DS已有接受记录，核原Owner合成profile归属/前置，不新建或切换目录。freeze未满足不启动联调。 |
| P1 | Development只实施R12–R14：退出YAML常驻/GUI链、最小.env/profile、DAA标准Tauri入口所需features接线、一条根AGENTS约定及准确教程；保留已实施r1时间/存储/actor/driver实现，不借新增Revision重做旧范围。 |
| P2 | 必要增量fmt/编译/定向配置与退役测试/build/locale/docs通过；逐项标明复用的未变r1证据，固定新候选/命令/限制。此时尚未启动产品。 |
| P3 | Owner按同一r2候选/原Owner独立合成profile完成一次下表M01–M09；失败只停受影响分支并保留事实。 |
| G1 | Development核Owner记录及正常退出后的同库只读对账，形成developer_handoff；不得自行写QA verdict。 |
| G2 | 主协调实际调用新的fresh-context Verification；qa_passed后Owner决定DAA-007最终验收，整体B决定另明示，C不自动放行。 |

| 手册步骤 | 范围及对应AC |
| --- | --- |
| P00 | 精确r2批准、DS已有接受/当前候选及features/.env来源/原profile/端口检查；AC01–AC02、AC19–AC22。 |
| M01 | 两个应用均按`pnpm tauri dev`从正式源码启动，记录实际命令、Tauri features及原Owner合成profile，driver/new v2及停止初态；AC03–AC04、AC17、AC21。 |
| M02 | DS_A的Alpha/Beta/Measure、71/88、地址/初值/策略及启动后暂停；B后于M06同样创建；AC05。 |
| M03 | DAA_A导入、地址/命名、Fast_500/Slow_1000分组、激活；AC05–AC06。 |
| M04 | A连接/单点核对、暂停规则静态首次采集；AC07–AC08。 |
| M05 | 规则恢复/ready变化、DS普通UI写111/13.25、周期及再暂停静态对照；AC07–AC08。 |
| M06 | 第二PLC及同号DB异值隔离、双连接/采集与A单点诊断复用；AC05–AC07。 |
| M07 | DS_A断线/DS_B继续/恢复与缺口解释；AC09。 |
| M08 | 上海历史筛选/分页/原字节详情及历史列宽；AC10–AC12。 |
| M09 | 正常退出、同profile重开stopped与旧历史保留，退出后只读对账；AC13–AC14。 |

## 6. 封闭文件allowlist

以下`D=`仓根`automation-world/data-acquisition-agent/`，`S=`仓根`automation-world/device-simulator/`。第一表保留r1原32路径封闭写面；N/M是r1时点，r2不要求重写已实施文件。第二表是本r2拟新增的精确路径；列为可改不表示必须写，不允许删除/移动或递归扩展。**本轮PM唯一写入是本spec；R12–R14实施面仅在精确r2批准后由实际Development消费。**

| 操作 | D相对精确路径 | 有限责任 |
| --- | --- | --- |
| N | `src-tauri/src/domain/business_time.rs` | 集中时间常量、生成/解析/规范化与边界计算，复用chrono；必要纯测试。 |
| M | `src-tauri/src/domain/mod.rs`、`src-tauri/src/domain/local_sample.rs` | 注册helper；now薄转调与样本/manifest v2合同说明，不另造时钟。 |
| M | `src-tauri/src/infrastructure/local_store/schema.rs` | 仅新空v2 CREATE/metadata time_profile/版本CHECK及新库ledger；无旧库迁移脚本。 |
| M | `src-tauri/src/infrastructure/local_store/mod.rs` | 无写preflight、锁后复核、v2初始化/准入、事件时间；保持原队列/资源保护。 |
| M | `src-tauri/src/infrastructure/local_store/runtime.rs` | 规范saved_at、样本/manifest v2、history与retention同合同；保留同轮原子性/原字节查询。 |
| M | `src-tauri/src/infrastructure/local_store/configuration.rs` | 新版本/intent时间及排序所需最小适配，配置/context JSON仍v1。 |
| M | `src-tauri/src/infrastructure/local_logging.rs` | 仅集中时间helper/FormatTime适配及既有stdout/file诊断精度；不改轮转、mutex、限额、失败锁存或level。 |
| N | `src-tauri/src/infrastructure/local_store/time_contract_tests.rs` | 真实Stores路径的legacy零写、新v2、查询/维护边界与payload/SHA定向验证。 |
| M | `src-tauri/src/infrastructure/local_store/tests.rs`、`src-tauri/src/infrastructure/local_store/source_import_tests.rs` | 仅受新存储版本/规范时间影响的已有断言与测试fixture适配，不改旧oracle/放宽保护。 |
| M | `src-tauri/src/services/local_supervisor.rs` | engine打开前preflight与拒绝传播；既有actor/调度/退避/传输逻辑不改。 |
| M | `src-tauri/src/lib.rs`、`src-tauri/src/commands/local_acquisition.rs` | 无engine诊断壳、bootstrap稳定错误、可选shutdown接线；不新增IPC/capability。 |
| M | `src/services/localAcquisition.ts` | bootstrap具体错误保留与现有envelope/raw内部版本区分；不加假桥。 |
| N | `src/console/time.ts` | 上海墙上时间输入/秒显示及IPC毫秒边界唯一前端工具。 |
| N | `src/console/tableWidths.ts` | 本机列宽持久化、隔离、最小宽和重置公共工具，仅历史表消费。 |
| M | `src/components/console/LocalHistoryPanel.vue` | 时间输入/显示、原详情保持、稳定列ID/拖拽/恢复默认。 |
| M | `src/components/console/ConfigRevisionBar.vue`、`src/app/collection/views/storage/index.vue` | 仅陈旧snapshot与最老pending的秒级上海视图；不改日志/其它表格。 |
| M | `src/styles/app.css` | 仅历史表横滚/时间筛选及有限动作布局。 |
| M | `src/locales/zh-CN/common.json`、`src/locales/en-US/common.json` | 新时间/拒绝/列宽文案键及占位符对称。 |
| N | `tests/time-and-history-preferences.test.mjs` | 既有Node/TypeScript通道的TZ/秒边界与列宽隔离/恢复有限用例，无新框架。 |
| M | `README.md`、`README.zh-CN.md`、`src/app/README.md`、`src/app/README.zh-CN.md` | 新旧profile、启动/显示/角色与联调入口稳定说明。 |
| M | `src-tauri/src/infrastructure/local_store/README.md`、`src-tauri/src/infrastructure/local_store/README.zh-CN.md` | v2矩阵、原字节/时间/旧库拒绝及维护边界。 |
| N/M | `JOINT_TEST_GUIDE.md`、`JOINT_TEST_GUIDE.zh-CN.md` | 本轮主协调出试行版；批准后Development只据实际候选/限制校正，不冒记Owner操作通过。 |

| 操作 | r2新增精确路径 | 仅允许责任 |
| --- | --- | --- |
| M | D `.env.example` | 两个日常键、安全false、移除两旧YAML locator及准确注释；不修改真实.env。 |
| M | D `src-tauri/src/config/mod.rs`、`src-tauri/src/config/local_bootstrap.rs` | 活动键白名单、来源/简单解析/profile选择与写前拒绝；普通启动不再构造MigrationPaths，保留原validation/mode保护；有限startup_env内联测试。 |
| M | D `src-tauri/src/domain/yaml_migration.rs`、`src-tauri/src/infrastructure/mod.rs` | 仅迁入退役后必需的cfg/import/type隔离；保留私有名称、receipt/摘要格式及历史算法/测试，不新增DTO状态。 |
| M | D `src-tauri/src/infrastructure/local_store/yaml_migration.rs` | 保留私有receipt只读/前缀保护，迁入mutator作必要test-only隔离；不改schema/历史字节或添加生产写路径。 |
| M | D `src-tauri/src/services/local_yaml_migration.rs` | 兼容summary最小只读、retry写前拒绝，历史startup/execute必要test-only隔离；有限resident_retirement测试。 |
| M | D `src-tauri/src/infrastructure/yaml_migration_tests.rs` | 仅适配普通engine已退出迁入的旧测试假设，以及自造v2 receipt保护/写前拒绝的有限用例；保留历史失败/算法测试，不扩全矩阵。 |
| M | D `src/console/composables/useLocalAcquisitionConsole.ts`、`src/components/console/YamlMigrationNotice.vue` | 解除普通reload/save迁入调用与返回消费；旧notice仅作解绑所需类型适配，不删文件/新入口。 |
| M | S `src-tauri/src/config/bootstrap.rs` | 在普通桌面bootstrap最小加入自有源码.env及profile优先级；复用原resolver，保留test-automation边界，有限startup_env内联测试；不改runtime。 |
| M | S `.env.example`、`README.md`、`README.zh-CN.md`、`USER_GUIDE.md`、`USER_GUIDE.zh-CN.md` | 准确说明源码开发的DS_PROFILE_DIR、一遍配置/短启动命令及默认/隔离/旧数据边界，不改其他功能或旧验收。 |
| M | D `src-tauri/tauri.conf.json` | 仅将已有必需`rust-snap7-driver`接入`build.features`，标准`pnpm tauri dev`带驱动；其余build字段、bundle、窗口、identifier、capabilities与资源保持。 |
| M | D `package.json` | 仅在必要时收敛重复的普通dev别名，保留`tauri`标准CLI入口；不改依赖/版本/锁、build/headless等其他脚本。 |
| M | 仓根 `AGENTS.md` | 仅新增R14逐字列明的一条Tauri普通启动约定；其他治理正文保持，不批量改其他应用或shared skills。 |

r1表中重叠路径的r2职责只增加：`local_supervisor.rs`解除普通startup/migration_state依赖；`commands/local_acquisition.rs`、`lib.rs`仅必要兼容错误/文案接线；`services/localAcquisition.ts`、`ConfigRevisionBar.vue`及两common.json仅迁入消费解绑/必要稳定错误中英说明；README/app/local_store与JOINT_TEST_GUIDE pairs仅R11/R14说明。其余原32路径保留既有r1交付；若未变，复用其证据，不能顺手调整时间/存储/布局/导入/调度。旧YAML解析源文件可通过已列`infrastructure/mod.rs`作test-only注册，不为删除历史源码扩大路径。

任务文档按角色形成：PM/Human Owner只写本spec；精确r2批准后Development在同目录tasks.md保留r1历史再记录r2；developer_handoff后新的Verification才创建checklist.md。主协调可维护本bundle真实evidence与仓根CODE_INDEX.md中实际结构导航，并机械同步根PLAN/catalog、AW PLAN、DAA PLAN/catalog及DS PLAN/catalog pairs中的本任务关系链接。DS索引仅链接唯一`aiis-ics-arch::DAA-007`，不新建DS bundle、不改旧任务验收。其他路径不在写面。

保护面包括根AGENTS除R14单条新增外的正文、workflow/角色/skills、旧bundle/证据/76样本、DS除第二表外的全部工程、共享core/fixture/oracle、CA/CU/SMA/backend/frontend-js/tools/contracts、真实env/YAML/profile、package依赖/版本与非列明脚本、pnpm/Cargo依赖/default features及所有锁、DAA Tauri除build.features外的配置/其他应用Tauri配置/capabilities/图标、ManagedS7/driver/decoder、local_scheduler及actor业务策略。发现需改传输/解码/调度、额外DDL/数据迁移、更多路径或打包寻址，停止对应工作返PM修订；本r2未批准前的本次入口纠正只修改同一草案，不创造r3或独立任务。

## 7. 验收标准

以下为精确r2批准后标准。r1必要DEV结果按tasks原时点保留，不等于这些AC已全部通过；Owner联调和独立QA仍未运行。文档自检不是产品pass。

| AC | 可核完成条件 | 需求/最少证据 |
| --- | --- | --- |
| AC01 | 精确r2新增范围获批准，r1原批准/实施历史保留；实际before/增量/新增全文和保护审计成立，角色链未被手册替代。 | R01/R10；新批准原话/SHA、封闭diff，不重复索取r1批准。 |
| AC02 | DS已有接受记录与本次有限候选精确可核；历史306a QA、DS-001/DIRECT及本r2新增.env delta分层，不要求重验旧DS产品。 | D02–D03；owning acceptance、P00逐SHA/接口/feature。 |
| AC03 | 正式源码下DAA/DS均由普通`pnpm tauri dev`启动，Tauri配置传递既有必需driver feature，无额外CLI feature；原Owner绝对profile、driver on/local-validation off/test-automation off及read gate可核，启动不自动连接/采集，不触达默认/旧库。 | R06/R13–R14；静态脚本/config/Cargo接线及Owner M01实际命令/配置来源、M04真实S7读取。 |
| AC04 | 新双库user_version/metadata/time_profile与样本/manifest版本矩阵准确；自造legacy/未知/错配在ProfileLock及持久写前拒绝，原件/目录不变、UI有具体拒绝语义；合格v2/新空取得锁后的复核分支另如实记录锁文件事实、业务库未RW。 | R02–R03；DEV定向测试/差异，QA独立核，不读默认库。 |
| AC05 | 双实例30102/30103、TSAP、两个同号DB/6点/长度/类型/地址与显式异值准确；BEGIN不作初值，保存/加载/启停分开。 | R07；M02/M03/M06的配置、Owner记录与闭库只读配置。 |
| AC06 | 每PLC fast500/2BOOL、slow1000/4点，全部单一组归属且跨两DB，无未选声明；地址与技术名已确认后才启用/激活。 | R07；同库草稿/revision/context成员对账。 |
| AC07 | 两台真实S7稳定采集，无假值；每台每组至少两个good完整轮，origin=s7、异值不串线、周期与源顺序合理；A诊断复用会话、B继续。 | R08–R09；M04–M06、原样本/manifest/seq及DS连接事实。 |
| AC08 | DS规则暂停时仍通信且DAA有新good轮，静态当前值可比；恢复后ready双态及111/13.25有真实新轮，旧样本不改；动态时刻差异诚实标明。 | R08；M04/M05 Owner暂停/恢复/普通UI写记录与同库时刻。 |
| AC09 | 停A不阻B的新good轮，A质量/断线/退避真实；恢复观察窗内新good历史出现，无断线真实值回填。无每tick行与已落bad轮区分。 | R08；M07分段记录、故障/恢复事件和样本。 |
| AC10 | 新库/IPC日历字段全为规范+08毫秒，生成/default/metadata/query/maintenance统一；stdout/file日志为+08且原诊断精度保留；不同offset同瞬间、上海跨日/毫秒边界及宿主TZ用例通过。 | R02/R04；实际Stores/helper/日志formatter有限测试，不只截图。 |
| AC11 | 历史/最老pending/陈旧快照按上海秒显示、事实语义明确；日期筛选含所选终止秒的毫秒，分页/质量过滤正确，原JSON/SHA不改。 | R04–R05；M08、TS断言及闭库结果。 |
| AC12 | 仅历史表普通列拖拽/min-width/横滚、跨筛选/刷新/切页/重开恢复、稳定key隔离及恢复默认成立；偏好不进业务SQLite。 | R05；工具有限用例及M08/M09 Owner记录。 |
| AC13 | 每完整轮exact成员、两DB样本、manifest/原SHA/context、pending与next_seq一致，无孤样本/半轮/重复delivery或ACK。 | R09；同一关闭profile的只读独立账。 |
| AC14 | 正常退出clean、同profile一次重开stopped；历史payload/manifest/context/SHA、ID/generation/seq及配置保持，未显式启采不新增业务样本。 | R09；M09 Owner记录、正常关闭后两次只读状态比较。 |
| AC15 | 必要r2增量fmt/locked编译/配置与退役测试/DAA build/locale/docs及标准Tauri feature解析核对真实通过或明确阻塞；未变r1证据按SHA复用，未重跑旧全B/DS矩阵；中英手册区分当前/拟交付/实测。 | R06/R10–R11；实际argv/cwd/feature/exit/raw、静态配置及候选关联，无DEV原生。 |
| AC16 | 新fresh Verification独立审阅/必要检查与Owner报告/字节实证分层，资源证据持久化；qa_passed/Owner接受/整体B/C gate互不代替。 | R10–R11；独立checklist及真实Owner决定。 |
| AC17 | 普通bootstrap/engine不构造/读取/散列/执行YAML迁入；默认样例和旧locator均不生效；DEV新空v2配置为空、无PLC_1/新迁入receipt/因退役改变的ETag。 | R12；真实engine有限resident_retirement用例与调用图，不能只删.env两行。 |
| AC18 | reload/save无migration summary/retry调用或故障弹窗，save成功不因退役查询变失败；显式兼容summary只读且retryAllowed=false，retry在写入/探测前拒绝。合成既有v2 receipt/source原bytes/hash受保护。 | R12；有限调用图/类型build、DEV自造receipt前后账与错误断言，不读取真实库。 |
| AC19 | DAA process > 所选自身.env > 原默认选择及进程专用DAA_ENV_FILE成立；DS process > 自身源码.env > 原Tauri默认成立；空可选值视未设，选中非法/不可读显式定位写前失败，不降级默认或旁建。 | R13；两应用非零startup_env选择/解析/错误用例及锁/库/日志未创建断言。 |
| AC20 | 简单字面解析、不扫描cwd/父/其他app、不执行/展开shell；不新增依赖/IPC/env全量泄漏；DAA Cargo default仍为空，直接Cargo合成/validation可保持driver-free，DAA validation与DS test-automation原profile/fixture边界保持，正式driver编译图无新增退役dead_code/unused警告。 | R06/R12–R13；自造env隔离用例、cfg/实际编译及只改允许配置字段的保护diff。 |
| AC21 | 两.env.example/README、DS USER_GUIDE及DAA JOINT_TEST_GUIDE pairs给出三日常键含义、优先级、安全false与联调true区别，一次手工配置后普通启动统一为`pnpm tauri dev`；根AGENTS仅新增R14所列一条约定。实际复用原Owner profile，不覆盖env/切库/seed，不宣称r1已具新行为，不批量改CA/SMA/工具。 | R14；文档/链接/键和单条规则diff核对，Owner P00/M01/M09同profile事实。 |
| AC22 | r1 spec/tasks归档字节及原DEV候选/失败/限制保留；r2实际Development记录与fresh QA纳入新配置合同，原生仍由Owner一次连贯M01–M09及闭库checkpoint/同profile重开完成；无DS旧验收豁免转移或B/C越级。 | R01/R10–R14；归档SHA、角色handoff/新候选、Owner记录、独立checklist。 |

## 8. 对账、风险、排除与收尾

闭库只读账以本次绝对profile、instance ID、Owner运行片段和候选为共同键：先核双库schema2/time_profile/身份，再核保存的两PLC/两组/六点及active/context；逐个cycle核expectedPointIds与所涉两DB、各sample的plc/group/revision/generation/seq、唯一delivery/pending和SHA。按原UTF-8字节核payload/manifest/context，区分样本2与context/envelope1；不重新序列化再hash。按PLC/generation核next_seq接续、组筛选自然跳号；只统计实际提交轮，不用计划tick数补样。

正常退出后的首次账与重开再正常退出后的账比较配置/不可变样本原字节、源身份/序号、业务样本计数；允许真实runtime生命周期事件/clean_exit变化，不要求全文件hash永远相同。未知保存/未知事件、Owner记忆及精确值缺口分别列出，不能由正确最终态倒推未观察的所有中间步骤成功。raw证据中原UTC文字/历史文件只保留，不改写成新+08以求一致。

| 风险/取舍 | 约束、停止或回退 |
| --- | --- |
| 新binary不能使用旧UTC profile继续采集/编辑 | 审批首屏明示；写前拒绝、保留原件。无自动迁移；原版本只使用原profile，新v2不可无证明交旧binary读取。 |
| 新schema初始化/事务时钟链影响已有存储路径 | 仅新空profileDDL；新库identity/CHECK/time_profile与定向Stores测试闭合。不能沿用时间v1隐性改语义、放宽不匹配准入。 |
| DS已有接受与本r2新增配置delta混淆 | 原接受保持，本r2单列bootstrap/.env增量、逐SHA与影响；不修改DS runtime/规则/权限/协议，不把新代码倒记为旧QA/接受。 |
| 人工动态时刻、断线缺口与工具可见性有限 | 同轮原账＋Owner记录；缺必要证据blocked，只补受影响项，不补造PLC历史/截图或假桥。 |
| 串端口/默认profile/未知进程 | 显式新profile与异值、Owner核端口归属；冲突停步，不扫描、kill他人或回退102。 |
| 时间校正/retention误删或格式混合 | 固定毫秒与同offset参数、单调耗时/序号另用；pending/incomplete/reference保护和物理预算不放宽，维护只在自造fixture验证。 |
| .env看似生效却仍选了进程覆盖或错误目录 | 明确来源优先级、一次核对继承覆盖；非法显式路径先拒绝，不自动退回默认。原Owner profile只在前置仍满足时沿用，不因r2切换或复制数据。 |
| 普通启动已带真实驱动被误当作采集授权 | driver是编译可用性；read gate仍false且无启动自动连接/启采。静态feature/编译证据不代替Owner普通命令下的M01/M04运行实证；不为统一入口启动DEV原生或重跑协议矩阵。 |
| 退役时损伤receipt或新空库造假状态 | receipt/source archive和保留前缀保持，兼容读取不写，retry写前拒绝；新空库保持真实未迁入，不写retired/migrated状态，不借cfg清理历史算法。 |
| 源码.env说明被理解为安装包保证 | 本r2仅验收正式源码开发启动；不修改打包/安装/资源寻址、不承诺安装版.env发现，额外需求返PM。 |

排除：阶段C、Backend/SMA、事实上传/ACK/清pending/补传、真实PLC/现场/生产DB/API、旧UTC/真实数据迁移、真实.env与Owner profile的Agent写入、DS除封闭bootstrap/.env说明外的修复/功能/发布或协议容量矩阵复跑、全DAA表格/公共CU重构、更多TIA语法/初值解释/新oracle、新YAML工具/UI/CLI/迁入开关、依赖/锁升级、额外IPC/任意脚本执行、headless采集入口、Docker/安装版.env支持/签名/跨平台/长稳、Git写入/refs/发布部署、业务邮件及跨会话外发。canonical workflow的long-task-notifier当前本人通知决策仍按其合同适用；PM draft不另开Development执行窗口，也不扩大外发授权。

Development在handoff列本任务自有env/profile、target/dist、日志/只读摘要及用途，Owner正常关闭后记录端口/句柄事实。QA只核证据依赖，不回收。Owner最终接受后，主协调先持久归档必要合成账/raw/候选和hash，再核归属、无占用/后续依赖后回收明确可再生资源；不得清默认库、旧76样本、DS并行资源或历史bundle。回滚仅限有before/diff可识别的本任务源码增量，需对应授权，不reset整个dirty工作树。

## 9. Skill路由、草案自检与handoff

| 后续实际表面 | 责任角色与适用skill |
| --- | --- |
| 新存储v2、preflight、时间helper/查询/维护、有限测试 | Development/Verification：`rust-runtime`；记录新空schema-maintenance边界，不载入backend业务栈。 |
| DAA/DS普通源码.env/profile与迁入链退役 | Development/Verification：`rust-runtime` + `desktop-tauri`；只消费既有入口/错误/锁边界，无新依赖/任意IPC/运行脚本。PM本轮仅定义合同，不执行技术实现或验证。 |
| 原生入口/错误传播/具名IPC | `desktop-tauri` + `rust-runtime`；Owner执行原生，DEV/QA核静态/记录，不扩capabilities。 |
| 历史表/时间控件/列宽与可见文案 | `frontend-ui`（适用DESIGN/FRAMEWORK）+ `i18n-workflow`；仅本表和列明时间视图。 |
| 点位/DB/UDT/标准布局及S7解码对账 | `plc-point-mapping`；只消费既有core/手写fixture，传输/算法故障超当前写面返PM。 |
| 文件头/真实结构导航、bundle/跨工程门禁 | `code-document-indexer`；治理使用`project-governance` + `aiis`，唯一事实owner不变。 |

2026-10-27，本实际PM只修订现有spec为r2 draft，核对现有文档/任务身份/源码调用图/allowlist/本地引用与归档原字节；具体文档检查与最终spec SHA由handoff报告。未运行编译、产品测试、SQL、native、监听或S7，未更改实现、真实.env、Owner profile、tasks或创建checklist。`.codex/agents/pm.toml`声明`gpt-6.1-sol / max`仅是配置证据，不冒称独立观测的运行值；profile仍为contract_only。

主协调relay本精确`aiis-ics-arch::DAA-007 r2`的新增范围、AC17–AC22和风险给Human Owner。精确r2批准前停止增量实施；批准后实际Development保留r1历史，按G0→B0→P1/P2→Owner一次M01–M09→闭库账/developer_handoff→新fresh Verification串行接续。验收须覆盖两应用新的配置合同与退役行为，DS-001的QA例外不适用本任务。任何范围/版本矩阵/验收/风险/allowlist实质改变均返PM新Revision，不从方向同意或沉默推定批准。

## 10. 批准与Revision历史

### r1：已批准的历史事实

2026-10-23，Human Owner明确批准精确`aiis-ics-arch::DAA-007 r1`。唯一coordinator `/root`曾转交给实际PM的批准对象为r1草案SHA-256=`5ccff5d81eb64c9cad99ed87d360a84e055fe26696056dc1d2bec84933652bf8`；登记版SHA见§1归档。逐字原话：

> 可以，批准 DAA-007 r1，按 spec 完成时间规则整改和联调准备。使用新的隔离 profile，已有 SQLite 配置和历史不动；原生测试由我按试行手册手动执行，只做必要增量验证和独立核验，不重复整套测试，阶段 C 暂不做。

该批准与r1后续实施事实保留在[原spec](evidence/r1-before-r2/spec.md)、[原tasks](evidence/r1-before-r2/tasks.md)及当前[tasks](tasks.md)，不被本r2改写或撤销。r1已批准不表示Owner原生、独立QA、DAA-007终验或整体B已通过；也不授权当时排除的DS/env新增代码写面。

### r2：草案待精确批准

2026-10-27，根据§1批注提出R12–R14、AC17–AC22及必要关联修订；同日按Owner“统一pnpm tauri dev”纠正修订R06/R10/R14、闭合allowlist与关联AC，仍为同一未批准r2。r2 scope approval=`pending`，metadata保持`draft`，没有r2 Development/QA/Owner最终接受结果。前一版r2归档只保留草案演变，不形成批准或第二事实源。最终可审阅版本SHA由外部handoff固定；Human Owner一次明确批准精确r2后才恢复新增实施，不重新要求未变r1范围批准或DS旧产品验收。
