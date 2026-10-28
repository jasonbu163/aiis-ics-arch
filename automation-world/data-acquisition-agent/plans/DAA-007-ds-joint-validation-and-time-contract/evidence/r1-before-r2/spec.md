Task ID: DAA-007
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner已于2026-10-23精确批准DAA-007 r1；交唯一coordinator /root启动实际Development，依B0及原实施顺序接续；Owner手动原生、新fresh Verification及最终验收仍分别待发生
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: DAA ManagedS7到DS的双实例读取与本地SQLite闭环、必要上海时间合同整改及人工联调手册
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: aiis-ics-arch::DAA-007 r1 PM -> Human Owner scope approval -> Development -> fresh-context QA / Verification -> Human Owner final acceptance
Depends On: aiis-ics-arch::DAA-006 r3 owner_accepted import/naming baseline; finite DS protocol delivery explicitly adopted for this joint run and checked at B0
Related Task: aiis-ics-arch::ARCH-AW-005 r5; device-simulator::DS-001 r1; aiis-ics-arch::DAA-002 r2; aiis-ics-arch::DAA-003 r1; aiis-ics-arch::DAA-004 r1

# DAA–DS 联调与上海时间合同 r1 草案

## 1. 当前效力与批准摘要

2026-10-23（Asia/Shanghai），Human Owner明确请求：

> 可以，先出 DAA-007 r1 spec 和试行版操作手册，明确 DS 基线、启动配置、联调步骤、时间规则整改及验收标准。原生测试由我手动执行，只做必要增量验证，已有 SQLite 配置和历史不动，阶段 C 暂不做，批准后再改代码。

本轮只形成可审阅的范围草案与双语试行手册，**尚未取得精确 r1 实施批准**。PM只写本spec；主协调编写[中文试行手册](../../JOINT_TEST_GUIDE.zh-CN.md)和[英文试行手册](../../JOINT_TEST_GUIDE.md)、只读来源清单并机械同步索引。手册所有原生步骤均待批准和前置条件满足后，由Owner手动执行。

**必须随精确r1一起审阅的兼容取舍：**新空合成profile采用双库存储v2及固定上海时间合同；旧UTC v1或未知时间合同的profile在任何库/恢复/维护/迁入/持久日志写入之前拒绝打开。升级后旧默认profile不能直接继续采集或编辑，原配置和历史文件保留；本任务不迁移旧库、不自动另建旁库、不复制旧数据。Owner可保留原版本使用原profile，历史迁移另批；不能把本方案描述为不影响旧profile的透明升级。

本任务只补齐受控本地DS的真实S7读取到DAA本地落库闭环及其必要时间整改。DS是只读外部依赖，原生窗口、S7网络操作及合成配置录入均由Owner执行；Development和Verification不操作窗口、不启动DS/DAA监听或客户端、不直接改联调数据库。有限代码整改先通过必要DEV检查，再交Owner一次足够的人工操作记录；之后仍须新的fresh-context Verification，未取消QA。

唯一active lifecycle coordinator为主会话`/root`。实际PM采用项目`pm`角色，配置`gpt-6.1-sol / max`仅作TOML配置证据；profile为`contract_only`。角色提示、bundle与diff审计是合同控制，不宣称平台ACL、强制路由或团队激活。

## 2. 消费依据与规划来源

已消费根AGENTS、README/PLAN双语、[canonical workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)、PM角色、AW/DAA/DS及共享core最近README/PLAN、DAA app/local_store说明、完整DAA-006三文件与其接受边界、DS-001两份现有角色文档、ARCH-AW-005当前r5交付/QA4及相应历史限度。作用域未发现更近AGENTS。本任务独立分类，没有Parent Task ID，不继承旧批准或终验。

| 来源 | 当前可用事实与边界 |
| --- | --- |
| [DAA-006接受记录](../DAA-006-point-naming-and-import-reuse/checklist.md#owner-acceptance-r3)及[接受源码清单](../DAA-006-point-naming-and-import-reuse/evidence/accepted-source-manifest.json) | r3命名/导入复用已接受；core为0.1.0，profile为tia-subset-v1、siemens-step7-v20-standard-word-v1、tia-point-name-v1。三文件、原oracle和DIRECT overlay证据分层保留。 |
| [DS历史QA4](../../../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md) | r5候选`306a09d5317931482a59f45da5eafcb9d3ee739199799f475ade1891fb0b00b4`历史qa_passed，原Owner终验pending；其ManagedS7协议实证不是DAA应用SQLite闭环。 |
| [DS-001交接](../../../device-simulator/plans/DS-001-policy-table-and-usability/tasks.md) | 当前developer_handoff；Owner按文字手册人工验收pending，独立QA例外只属于DS-001，不转移到DAA-007。 |
| DS会话`01a14e52-eeb4-7c82-bade-bc0a237fa2ff`后续DIRECT | 时间/展示及13表列宽改动与r5候选不同；当前只读清单不是这些增量已QA或终验的声明。B0须核有限采用决定和实际交付；不要求先完成DS-001全部终验或新开DS任务，本任务不发消息、不接管其写入。 |
| [planning-source-baseline.json](evidence/planning-source-baseline.json) | 主协调于`2026-10-23T15:09:14+08:00`固定的规划输入，SHA-256=`568fecb0bd3ce89c095999fda9df9746bb38d49163860e5dd2df32bd2c13b067`；HEAD=`1fa1ce50a521ebd51c2c43389db011a76f2d74bf`，交付仍为dirty工作树。不是获批执行baseline。 |

规划清单按其定义固定DS227源、DAA158源、core12源；aggregate SHA依次为`9378b7aa24c16c5454652d99380b37cb51b48092f3db7eee67516da599e99ba3`、`ed10ea9638ee6aedff7071519ddce73b0f8fdd62fa8fa21654d5cbab02113461`、`2be84cf7a1720067797c1d78b5b204616d1d1f11d571da36ceea9a6ac045a1d7`。它排除实际env、库、日志和产物，不从HEAD推断并行工作归属；执行前重核逐文件身份和影响。

主协调后续只读报告：DAA158/core12仍匹配；DS仅`src/app/simulator/views/points/index.vue`在并行DIRECT中发生新变化。保留原规划快照，不追改其hash、不倒记为当前passed。P00须在相关修改停止后核实际差异及采用候选；尚未进行的执行B0不能由这份快照代替。

只读源码事实：`domain/local_sample::now()`产UTC Z；SQLite saved_at、事件和migration ledger使用strftime Z，history/retention以规范文本比较；历史UI按本机时区和toISOString处理；现有schema含v1 CHECK，Stores::open在版本核对前已有可写打开和PRAGMA。只改显示或now()会混存、漏查并破坏旧合同，故下列新库初始化和启动前门禁是明确实施范围。

## 3. 前置决定与停止条件

| 编号 | 执行前必须成立的条件 |
| --- | --- |
| D01 | Owner明确批准精确`aiis-ics-arch::DAA-007 r1`，包括旧UTC profile拒绝打开的取舍、新空库v2初始化、文件allowlist及人工执行/独立QA分工。草案请求不满足此gate。 |
| D02 | Owner可随精确r1批准明确采用本节快照及B0所记录、未超本范围的候选作为本次有限DS基线，也可引用DS会话已有明确采用决定；记录原话/来源/时间/范围，不额外强制向DS会话确认或先完成DS产品终验。B0在相关并发修改停止后固定当前DS/DAA/core/fixture逐SHA、features、工作树和命令链。所需能力限双实例、端口/TSAP、两DB/类型/初值、启停/规则暂停和只读S7服务，不要求长期容量/全部扩展完成。 |
| D03 | 当前DS与历史r5/规划快照有差异须逐项归因。纯展示且不影响所需操作、协议、依赖、风险的变化，可在B0记录受影响hash和对应证据；协议/接口/依赖/语义/风险/allowlist实质变化返PM新Revision及Owner批准，不静默改成“任意最新DS”。 |
| D04 | 使用正式交付源码，不复制一套临时工程。隔离的是新建绝对合成env/profile与可再生产物。DS、DAA分别拥有profile，DAA双库同属一个实例；不使用默认/真实/历史profile、旧76样本或客户输入。 |
| D05 | Owner核15194（DS）、15191（DAA）及30102/30103归属、可用性和已有窗口；冲突保留他人进程并停该步骤，不能回退102、扫描替代口或改固定端口求通过。 |
| D06 | 时间整改和必要DEV检查先完成、候选被冻结后，手册才进入人工执行；试行手册不是已运行证明。DS基线未确认只阻塞依赖DS的动作，不伪造其已满足。 |
| D07 | 正常退出后才由DEV/QA只读核本次合成profile；mode=ro/query_only、明确绝对路径、无seed/DML/DDL/ACK。证据缺口保留并只补受影响条目，不重跑整套B/DS矩阵或固定三次关窗。 |

## 4. 编号需求

### R01. 精确候选、原数据保护与角色归属

批准后Development创建tasks，先固定批准spec SHA、执行before、任务增量/新增全文和保护面；不把整个dirty HEAD差异归因本任务。读取旧bundle不改其记录或状态。原source/revision/context/sample/manifest/receipt、ID/generation/sequence/delivery/reference及旧76样本不读写、不重采；DS源码、core/oracle和当前并行改动保留。

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

DS由Owner在正式DS目录以`DS_PROFILE_DIR=<本次绝对新合成profile> pnpm tauri dev`启动；DAA在正式DAA目录以进程显式`DAA_ENV_FILE=<本次绝对合成env>`、`DAA_PROFILE_DIR=<独立新合成profile>`、`DAA_PLC_READ_ALLOWED=true pnpm tauri:dev:snap7`启动。两应用dev/build不会自动隔离数据；禁止照普通默认目录运行本次联调。DAA不启local-validation、不传其fixture CLI，实际编译仅rust-snap7-driver路径。普通`pnpm tauri dev`无driver时返回driver_unavailable是另一个入口事实，不拿它作本闭环成功证据。

合成env中的两个旧YAML locator显式指向本次拥有的空/缺省不存在文件，避免默认样例迁入；env和profile不提交，不改真实.env/default SQLite。read gate为true不自动连接/采集；保存、激活、连接、开始采集仍逐步显式。DS/DAA的SQLite数据目录、日志、features与实际命令链在记录中可定位，不新增运行脚本、任意SQL/文件/网络IPC或日常无用按钮。

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

Development只运行受影响的fmt/locked编译、有限时间/门禁/存储查询与维护测试、前端build及少量现有Node/TS通道的时间/列宽断言、双语键/占位符/文档链接检查，不升级依赖/锁或新装框架。legacy/v2测试库是DEV自建的单元/集成测试材料，与Owner本次联调profile隔离；不能seed Owner同库或重跑DS协议/16连接/全B容量/76样本/完整导入矩阵。

批准后的最小命令基线如下，cwd为DAA正式目录；当前一项也未执行。定向测试的default编译结果可同时覆盖默认编译，不再机械追加同候选同features的check；若测试过滤0项必须失败处理，不能计通过。

| 计划检查 | 批准后命令/边界 |
| --- | --- |
| Rust格式 | `cargo fmt --manifest-path src-tauri/Cargo.toml --check`，不使用写入式fmt。 |
| 默认分支的有限时间/Stores验证 | `cargo test --manifest-path src-tauri/Cargo.toml --locked --no-default-features --lib time_contract`；新用例命名包含time_contract，仅读写自己的测试临时库，不启S7/native。 |
| 真实驱动分支编译 | `cargo check --manifest-path src-tauri/Cargo.toml --locked --no-default-features --features rust-snap7-driver`；不启动进程。 |
| 前端类型/构建 | `pnpm build --config vite.validation.config.ts --outDir <本次绝对owned-dist> --emptyOutDir`；输出为可再生产物。 |
| 时间/列宽合同 | `node --test tests/time-and-history-preferences.test.mjs`，包含UTC及一个非上海宿主TZ子进程；不更改系统时区、不开窗口。 |
| 文档/locale/差异 | 复用现有工具及有限内联只读检查，记录真实argv、键/占位符/本地链接与allowlist结果，不造通用治理脚本。 |

Owner完成手册P00与M01–M09，记录实际输入、动作、时刻、值/错误、正常退出、候选/features及必要截图/日志；允许一次连贯记录，无固定截图张数。Development可在退出后只读对账，再交精确developer_handoff。新的fresh-context Verification独立核批准spec、tasks、before/diff/候选、必要自测和Owner操作/同库记录，独立运行有必要的受影响纯检查；不驱动窗口、不重新建联调链、不重跑无变更矩阵。Owner报告与QA直接核得的字节/查询结果分别标识，缺必要证据为blocked、实际失败为failed，均保留历史；仅复核失败影响项。

### R11. 文档交付、风险和阶段门禁

双语试行手册写清前置freeze、真实启动/features/env/profile、上述模型/分组、时间整改限制、逐步按钮/输入/预期/恢复和空白结果表；本轮明确未执行。批准后Development据真实候选更新事实，不提前填写pass。README/app/local_store说明同步新旧时间存储边界与来源；索引仅由主协调机械同步，权限链不因文档存在自动执行。

DAA-007 QA通过只进入Owner最终验收。其接受不代验DS-001、ARCH-AW-005或DAA-002/003/004；整体B还须有限DS基线确认、本闭环全部必要gates及Owner明确“接受整体阶段B”的决定，旧任务pending按各bundle独立处理。C仍需B整体接受、稳定Backend合同及另行批准；本任务不启上传、补传、ACK、Backend/SMA或现场行为。

## 5. 实施顺序与人工步骤映射

| 顺序 | 责任与退出条件 |
| --- | --- |
| G0 | Owner批准精确r1；当前pending。 |
| B0 / P00 | Development只读核正式源码、features/fixtures/依赖保护、并行差异；主协调收齐DS有限基线确认和本次资源归属。freeze未满足不启动联调。 |
| P1 | Development先实现新空v2/旧库只读preflight与可说明拒绝；以自建legacy fixture证实零写后，再做统一时间生成/查询/维护与UI有限接入。 |
| P2 | 必要fmt/build/定向测试/locale/docs通过，固定精确候选/命令/限制；发布待Owner执行的手册版本，未启动任何产品。 |
| P3 | Owner按同一候选/同一新合成profile完成下表M01–M09；失败只停受影响分支并保留事实。 |
| G1 | Development核Owner记录及正常退出后的同库只读对账，形成developer_handoff；不得自行写QA verdict。 |
| G2 | 主协调实际调用新的fresh-context Verification；qa_passed后Owner决定DAA-007最终验收，整体B决定另明示，C不自动放行。 |

| 手册步骤 | 范围及对应AC |
| --- | --- |
| P00 | 精确批准、DS有限baseline及features/env/profile/端口检查；AC01–AC02。 |
| M01 | 从正式源码启动DS及DAA各自新合成profile，driver/new v2及停止初态；AC03–AC04。 |
| M02 | DS_A的Alpha/Beta/Measure、71/88、地址/初值/策略及启动后暂停；B后于M06同样创建；AC05。 |
| M03 | DAA_A导入、地址/命名、Fast_500/Slow_1000分组、激活；AC05–AC06。 |
| M04 | A连接/单点核对、暂停规则静态首次采集；AC07–AC08。 |
| M05 | 规则恢复/ready变化、DS普通UI写111/13.25、周期及再暂停静态对照；AC07–AC08。 |
| M06 | 第二PLC及同号DB异值隔离、双连接/采集与A单点诊断复用；AC05–AC07。 |
| M07 | DS_A断线/DS_B继续/恢复与缺口解释；AC09。 |
| M08 | 上海历史筛选/分页/原字节详情及历史列宽；AC10–AC12。 |
| M09 | 正常退出、同profile重开stopped与旧历史保留，退出后只读对账；AC13–AC14。 |

## 6. 封闭文件allowlist

以下`D=`仓根`automation-world/data-acquisition-agent/`。M为既有有限修改，N为必要新增；列为可改不表示必须写，不允许删除/移动或递归扩展。**本轮PM唯一写入仍是本spec**；下表实施面只有精确r1获批后由Development消费。

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

任务文档另按角色分阶段形成：PM/Human Owner只写本spec；批准后Development才创建同目录tasks.md；developer_handoff后新的Verification才创建checklist.md。主协调可维护本bundle真实evidence附件和仓根CODE_INDEX.md中上述实际新文件导航，并机械同步根PLAN/catalog、AW PLAN、DAA PLAN/catalog双语的本任务行；不复制第二任务。其他路径不在写面。

保护面包括根AGENTS/workflow/角色/skills、旧bundle/证据/76样本、DS全部工程、共享core/fixture/oracle、CA/CU/SMA/backend/frontend-js/tools/contracts、真实env/YAML/profile、package/pnpm/Cargo依赖及所有锁、Tauri配置/capabilities/图标、ManagedS7/driver/decoder、local_scheduler及actor业务策略。发现需改传输/解码/调度、额外DDL/数据迁移或更多路径，停止对应工作返PM新Revision；不能用本allowlist顺手重构。

## 7. 验收标准

以下是批准后待满足标准，当前全部未运行；文档自检不是产品pass。

| AC | 可核完成条件 | 需求/最少证据 |
| --- | --- | --- |
| AC01 | 精确r1批准、实际before/增量/新增全文和保护审计成立，角色链未被手册替代。 | R01/R10；批准原话/SHA、封闭diff。 |
| AC02 | DS有限交付被精确freeze并有Owner有限确认；历史306a QA、DS-001及DIRECT的证据层次/漂移归因准确。 | D02–D03；P00记录、当前逐SHA/接口/feature。 |
| AC03 | 正式源码与独立绝对合成env/profile、driver on/local-validation off和read gate可核，启动不自动连接/采集，无默认/旧库操作。 | R06；Owner命令/候选/启动记录及静态入口。 |
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
| AC15 | 必要fmt/locked编译/定向测试/build/locale/docs真实通过或明确阻塞，未重跑旧全B/DS矩阵；手册中英完整且运行事实与计划分开。 | R10–R11；实际argv/cwd/feature/exit/raw、候选关联。 |
| AC16 | 新fresh Verification独立审阅/必要检查与Owner报告/字节实证分层，资源证据持久化；qa_passed/Owner接受/整体B/C gate互不代替。 | R10–R11；独立checklist及真实Owner决定。 |

## 8. 对账、风险、排除与收尾

闭库只读账以本次绝对profile、instance ID、Owner运行片段和候选为共同键：先核双库schema2/time_profile/身份，再核保存的两PLC/两组/六点及active/context；逐个cycle核expectedPointIds与所涉两DB、各sample的plc/group/revision/generation/seq、唯一delivery/pending和SHA。按原UTF-8字节核payload/manifest/context，区分样本2与context/envelope1；不重新序列化再hash。按PLC/generation核next_seq接续、组筛选自然跳号；只统计实际提交轮，不用计划tick数补样。

正常退出后的首次账与重开再正常退出后的账比较配置/不可变样本原字节、源身份/序号、业务样本计数；允许真实runtime生命周期事件/clean_exit变化，不要求全文件hash永远相同。未知保存/未知事件、Owner记忆及精确值缺口分别列出，不能由正确最终态倒推未观察的所有中间步骤成功。raw证据中原UTC文字/历史文件只保留，不改写成新+08以求一致。

| 风险/取舍 | 约束、停止或回退 |
| --- | --- |
| 新binary不能使用旧UTC profile继续采集/编辑 | 审批首屏明示；写前拒绝、保留原件。无自动迁移；原版本只使用原profile，新v2不可无证明交旧binary读取。 |
| 新schema初始化/事务时钟链影响已有存储路径 | 仅新空profileDDL；新库identity/CHECK/time_profile与定向Stores测试闭合。不能沿用时间v1隐性改语义、放宽不匹配准入。 |
| DS产品正在并行改动，历史QA不是当前QA | B0有限确认/逐SHA/组件影响，实质漂移返PM；只读依赖不由本任务修DS或补其终验。 |
| 人工动态时刻、断线缺口与工具可见性有限 | 同轮原账＋Owner记录；缺必要证据blocked，只补受影响项，不补造PLC历史/截图或假桥。 |
| 串端口/默认profile/未知进程 | 显式新profile与异值、Owner核端口归属；冲突停步，不扫描、kill他人或回退102。 |
| 时间校正/retention误删或格式混合 | 固定毫秒与同offset参数、单调耗时/序号另用；pending/incomplete/reference保护和物理预算不放宽，维护只在自造fixture验证。 |

排除：阶段C、Backend/SMA、事实上传/ACK/清pending/补传、真实PLC/现场/生产DB/API、旧UTC/真实数据迁移、DS修复/发布或复跑协议容量矩阵、全DAA表格/公共CU重构、更多TIA语法/初值解释/新oracle、依赖/锁升级、额外IPC/任意脚本执行、headless采集入口、Docker/安装签名/跨平台/长稳、Git写入/refs/发布部署、业务邮件及跨会话外发。canonical workflow的long-task-notifier当前本人通知决策仍按其合同适用；不由本spec取消，也不把它扩成业务通知或跨会话授权。

Development在handoff列本任务自有env/profile、target/dist、日志/只读摘要及用途，Owner正常关闭后记录端口/句柄事实。QA只核证据依赖，不回收。Owner最终接受后，主协调先持久归档必要合成账/raw/候选和hash，再核归属、无占用/后续依赖后回收明确可再生资源；不得清默认库、旧76样本、DS并行资源或历史bundle。回滚仅限有before/diff可识别的本任务源码增量，需对应授权，不reset整个dirty工作树。

## 9. Skill路由、草案自检与handoff

| 后续实际表面 | 责任角色与适用skill |
| --- | --- |
| 新存储v2、preflight、时间helper/查询/维护、有限测试 | Development/Verification：`rust-runtime`；记录新空schema-maintenance边界，不载入backend业务栈。 |
| 原生入口/错误传播/具名IPC | `desktop-tauri` + `rust-runtime`；Owner执行原生，DEV/QA核静态/记录，不扩capabilities。 |
| 历史表/时间控件/列宽与可见文案 | `frontend-ui`（适用DESIGN/FRAMEWORK）+ `i18n-workflow`；仅本表和列明时间视图。 |
| 点位/DB/UDT/标准布局及S7解码对账 | `plc-point-mapping`；只消费既有core/手写fixture，传输/算法故障超当前写面返PM。 |
| 文件头/真实结构导航、bundle/跨工程门禁 | `code-document-indexer`；治理使用`project-governance` + `aiis`，唯一事实owner不变。 |

2026-10-23，r1 draft：按Owner草案请求形成上述R01–R11、AC01–AC16、D01–D07及封闭写面；旧库拒绝与新空v2是待Owner明确接受的实施方案，不是已经完成的修复。PM仅做文档身份、R/AC/手册映射、路径/链接和diff检查，真实结果随本次交接报告；未运行构建、测试、SQL、native、监听或S7。

当前没有tasks.md/checklist.md，没有开发交接、产品QA或Owner最终接受。交主协调relay本精确`aiis-ics-arch::DAA-007 r1`及试行手册，等待Human Owner范围批准；批准前停止实现/运行写入。批准后实际Development按G0→B0→P1/P2→Owner M01–M09→developer_handoff→新fresh Verification串行接续。若任何范围/版本矩阵/验收/风险/allowlist需要实质改变，返回PM新Revision，不从沉默或方向同意推定批准。

## 10. 2026-10-23 精确r1批准登记

Human Owner已明确批准精确`aiis-ics-arch::DAA-007 r1`。真实决定由唯一coordinator `/root`转交给本实际PM，批准对象为本spec草案SHA-256=`5ccff5d81eb64c9cad99ed87d360a84e055fe26696056dc1d2bec84933652bf8`，逐字原话：

> 可以，批准 DAA-007 r1，按 spec 完成时间规则整改和联调准备。使用新的隔离 profile，已有 SQLite 配置和历史不动；原生测试由我按试行手册手动执行，只做必要增量验证和独立核验，不重复整套测试，阶段 C 暂不做。

据此当前Status为`owner_approved`，G0精确范围批准已满足。此前正文中的draft、approval pending、待批准及未发生描述保留为草案时点历史；当前批准效力以本节和metadata为准。R01–R11、AC01–AC16、D01–D07、版本矩阵、allowlist、风险/排除及实施顺序保持获批草案原字节，本次不修订技术范围、不新增Revision。

下一gate由coordinator `/root`实际调用Development，先核B0采用候选/并发差异及隔离资源，再按原P1/P2实施、自检，之后由Owner按手册操作原生；developer_handoff后仍须新的fresh-context Verification和Owner最终验收。批准不表示B0、时间整改、联调、QA、DAA-007终验或整体阶段B已完成；阶段C及旧库迁移继续排除。

本轮PM只更新Status/Handoff并追加此真实批准记录，未创建tasks/checklist、改实现/测试/配置/锁/手册/索引，未启动或运行产品。行政记录后已核获批正文原字节保持；停止全部写入，批准记录版SHA由外部handoff报告以免自引用。当前execution window的notifier finish/decision由主协调负责，本PM不另开窗口或发送通知。
