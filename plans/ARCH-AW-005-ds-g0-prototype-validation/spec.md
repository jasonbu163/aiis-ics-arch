Task ID: ARCH-AW-005
Revision: r5
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner accepted ARCH-AW-005 r5 and the current DS delivery on 2026-10-27 after historical QA4 and subsequent DS-001/manual acceptance; acceptance-only closeout recorded in Appendix C and the owning checklist; DAA–DS SQLite separately gated, Stage C excluded
Owner Final Acceptance: owner_accepted, 2026-10-27 (Asia/Shanghai), Appendix C
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA派生独立DS产品MVP，演进既有Rust单owner/Snap7桥，完成导入、配置SQLite、运行控制和在线值闭环、自动化核验及验证后G0退役
Owner: Automation World
Acceptance Chain Reference: r1 approved; r2 never approved; r3 approved then stopped; r4 approved/DEV handoff/partial independent QA, not accepted; exact r5 scope approved by Human Owner 2026-10-21 -> Development -> fresh-context Verification -> Human Owner final acceptance
Depends On: aiis-ics-arch::ARCH-AW-004 r2 accepted design with 005 r4 design additions; aiis-ics-arch::DAA-006 r3 accepted tia-import-core 0.1.0/fixtures v1
Related Task: aiis-ics-arch::ARCH-AW-002; aiis-ics-arch::ARCH-AW-003; aiis-ics-arch::DAA-002; aiis-ics-arch::DAA-003; aiis-ics-arch::DAA-005

# DS产品纠偏、正常开发入口与G0退役规格 r5

## 1. 当前决定、历史事实与批准gate

2026-10-21（Asia/Shanghai），Human Owner明确方向，逐字原话：

> 补充，你前面几次的关闭三次窗口的测试都是正常能完成的，你可以看看日志。你给的后续的方向建议，我表示同意，就按这个方向推进。保留已有 Rust runtime，在 DAA 派生工程上按 DS 设计完成导入、配置、启停和运行值界面对接，测试尽量自动化，别再反复让我关窗口。DAA–DS SQLite 联调另批，阶段 C 暂不开展。G0这个由于是之前没有给你交代清楚，开发出来的偏差，调整好之后给我清理掉。还有，我叫你把daa直接先复制，还有一个原因，就是这个软件的还有一些现成的ui做好了，包括图标。我自己额外又用pnpm tauri dev执行，无法正常启动，日志我也引用给你了。

据此固定：**保留并演进现有Rust runtime；在DAA适用工程装配/CU/UI/图标上完成DS产品MVP；正常入口无需G0环境；自动化验证；调整且验证后退役废弃G0。** 不再询问是否复制DAA或是否保持Rust。相较r4只读概览/G0，本r5实质新增产品导入、配置SQLite/版本应用、可配置运行拓扑、管理UI及自动原生测试/清理，按根AGENTS §4形成精确新Revision供批准；方向同意不是对本草案全部文件、schema、自动控制入口和风险的提前批准。**前述PM-only/approval pending是草案时点限制；精确r5现已于2026-10-21获Human Owner批准，当前gate交Development按本spec原范围执行。本次PM只登记批准，不代实施、构建、监听、写DB、清理或QA。**

| 固定事实 | 当前读时结论及证据边界 |
| --- | --- |
| r4精确规格 | SHA `4f1b03ec618bd0a40295bf273339538bc1491f8082380a009449f681ef56c2fc`，2026-10-20已获精确批准；附录A保存完整原字节，含r3/r2/r1及批准/中止历史。不能以r5覆盖其原发生事实。 |
| r4 DEV | [tasks](tasks.md)为developer_handoff，source候选`ba08e83eb3c13ece431c87b304c8bdc2d0e1f8122e24c2477acc2ea9863b9b3e`、180 source/108 readonly input，DEV原19case为18适用pass、X02条件N/A；只是DEV自检。PM本轮逐SHA核180/108无漂移。 |
| 人工三窗实际完成 | DEV dev-0019及dev-0067两组三次code0/clean均有效；旧UI语言/主题/刷新观察只按其对应未变输入引用。fresh QA qa-0004也已三次正常关闭：PID16495/11435/11462，code0/两真实IPC/CloseRequested/ExitRequested/shutdown_joined，退出上界251470000/211383000/213544000ns；scaffold SHA `68fbd54f553411d0dd32ba99928d26821f490c92fb0dddc920458bdf020c0807`。旧0/3是当时checkpoint，不是当前阻塞。 |
| r4独立核验边界 | 独立重建、静态/原件审计、六测及AC31三窗pass已发生；最终归因修正checklist SHA `2ba72a739b27a5374e372164eaed656d7956de1f0148be17bafbc2ce14be3e64`（仅收准“本次不追加旧矩阵”的协调来源，原899547补记/859receipt仍保留）。QA全部协议矩阵仍not_run/整体incomplete，r4未获G0/产品最终接受。QA9保存旧checklist原文，A4/qa-run-0009 inventory SHA `a6cdd4926e1041a5a99fef2bcc59adbbc3165e62de76e11d8c3acb0f1edaa25c`；QA4 inventory SHA `79135a8fa1d3fbfa0dd0df2a53d4bcdadf9783362a2e4578f450544ac55dea0f`。不把Owner本次总确认扩成协议QA接受，本次不追加旧矩阵也不是以后同类回归豁免。 |
| 用户启动输出 | 附件《已粘贴的文本.txt》与本轮副本SHA均`aa183bd56b72cfbebe5e000553639e93f1471e003f43d7dbd95f6bb28f2797e5`；内容到Compiling aiis-tia-import-core截断，无error/panic/退出码。不能据此编造编译失败。源码确有bootstrap强制三个DS/G0路径、marker，desktop默认feature空、native链接需DS_G0_NATIVE_LIB_DIR；这是普通入口受限的**只读推断**，不是该次截断输出已证根因。 |

本r5交付称“DS产品MVP/有限S7协议基线”，不是完整PLC、完整长负载或现场软件。DS是AW归属的独立S7模拟器，无DAA/SMA/Backend运行依赖；DAA只作只读来源和受限测试客户端。真实DAA应用S7→SQLite联合验证仍另批/fresh QA/Owner，整体B不因本次接受自动关闭，C暂不开展。

## 2. 产品边界、来源与派生方式

### 2.1 产品依据与明确偏差

唯一canonical依据为[DS详细设计](../../docs/AIIS_DS_Detailed_Design.md)当前552行§4–9/§13及[004 r2接受记录](../ARCH-AW-004-ds-detailed-design/checklist.md#owner-acceptance-r2)。本r5批准后DEV同步同一正文的实施阶段/入口/产品已实现与未验收边界，不改004 bundle或倒记其QA。本任务旧目录slug保留，不创建第二bundle/新Task ID。

| r4现状 → r5目标 | 本次完成 | 明确保留的限制/后续gate |
| --- | --- | --- |
| 固定A/B、DB41/57、两1088B fixture → 配置驱动 | Rust manager改UUID实例集合；DB map/typed point/coverage/规则及初值从selected revision编译，无硬编码两个实例/DB/端口/64点。8实例、每实例32DB/4096叶、DB号1–65535/长度1–65536为准入上限。 | 配置边界不等于最大拓扑/8×16同时吞吐；实际资源预算仍能拒新连接，不降阈值或隐含无界扩展。 |
| 链接core而无消费者 → 真导入/手工建模 | 多文件、多DB、受限UDT/数组、重导、地址/命名确认、DS初值/策略、保存/显式apply。 | 不执行TIA初值，不支持优化DB/未知类型/多维数组；非完整TIA编译器，人工地址不是实机证明。 |
| 无产品配置库 → DS单SQLite | 稳定身份/不可变来源与revision、CAS草稿、selected/loaded分离、停机apply、兼容hold保留、重开stopped。 | 无DAA样本/历史/outbox/上传、无跨进程运行值持久化、无持久apply journal/命令服务。 |
| 单只读概览 → 产品操作闭环 | 工作台；实例/DB点位/策略配置；在线值；连接面板；日志与存储状态。同一runtime/真实DTO，无模拟成功。 | 不增加低代码画布、任意脚本、生产账号/授权、后台托盘/守护。绑定首版限IPv4 loopback，远端/wildcard/IPv6另批。 |
| G0专用启动 → 正常工程入口 | `cd automation-world/device-simulator && pnpm tauri dev`可用；工程自动构建/链接受控Snap7；缺省真native、空配置stopped，图标和CU装配复用。 | 本轮目标macOS15.7.7/arm64；三平台发布/安装器/签名/系统注册/部署不在范围。 |
| 人工三窗串行阻塞 → 自动风险验证 | 同runtime测试宿主独立跑协议；native专用隔离profile跑真实UI/IPC/保存重开/正常close，按受影响项复测。 | 自动DOM行为不等于人工视觉审美或物理鼠标/OS标题栏点击；Owner在成品上作一次正常验收，不机械重复三窗。 |
| G0产品/实验混放 → 迁移后退役 | 保留有效Rust/native；原协议回归向量迁正式tests；验证/封存后删除原G0专用源码/脚本/fixtures/入口依赖。 | 004/旧bundle/原件/失败史与必要A4证据永久留其真实层次；不整树rm，不清未知资源。 |

本MVP覆盖详细设计D1/D2/D3的本节有限功能，不再以“以后D1另批”拒交这些已明确的产品闭环；D4中原G0短程协议/资源回归纳入r5。004的L1/L2长负载（5min+60min）、L4/L5长期故障、L3扩展8×16、三平台和现场仍deferred，不宣称完整容量合同已满足。classic S7仍为PDU480/frame512/≤4items/单item≤256B/AMQ1；长STRING[254]可作为完整256B item，不能据DB长度上限宣称任意长包/系统指令支持。

### 2.2 固定来源、UI与图标

core固定`automation-world/shared/tia-import-core` **0.1.0/Rust2021/std-only/publish=false**，六API/profile/v1样例及各SHA与附录A r4 §2.1逐字相同；accepted-source-manifest SHA `8d9d62457baa32aac8134df77773ea5cae23a0401e403ef1d4c267cdafc02ee7`、coreDeliveryManifest SHA `205f00ecf946246dfc7c2268eb60912733fb7fb1e52405e9174a5ea5996b1812`不改。接受清单保持60/61技术原字节+CODE_INDEX导航例外，不能把新增UI/资产说成已获DAA006共享接受。名字/布局/oracle不fork、不重写expected。

沿附录A r4 §2.8的37个DAA工程输入（digest `55e84aef4f28029da474c2eecb9e29a8e463e8e92564d4c79b31920bf4c75cac`）、17个CU公共输入（digest `062406ddb19f99d6485a7ee953bc1f8e9e85d752b6d1db961c637713e96a090d`）复用装配。r5补以下15个DAA只读UI模式，digest `e84e9301ab18c4666395f409eed9817916ef5468e454beecc4e7dc37a8151280`；前缀均`automation-world/data-acquisition-agent/`，每行是独立新增来源pin而非共享接受声明：

| 额外只读UI来源 | SHA-256 |
| --- | --- |
| src/components/common/MetricGrid.vue | 24ba5f1f679056aa599ce66b8d938b7ee1c05588a2bc530496bdae3505bfbed4 |
| src/components/console/ConsoleActionButton.vue | 876f6cb72d1e840c86d7417f3de19afd5fb9cd4172391f445efe43cabbbe0731 |
| src/components/console/ConsoleCard.vue | 33b48846dd63507f9a44d33abc4006c1324fdac6bbd8feff02d39961304c7bcb |
| src/components/console/ConsoleInfoGrid.vue | 15b27a2f6ef44e7238de34f78dd9eba5955e9621b9c987887f8b3851d778b8b0 |
| src/components/console/ConsoleMetricCard.vue | c31ef1e22be34c471538294d1ed02f63811b8bd3f6191d8c978e6f8ed9b5a663 |
| src/components/console/ConsoleOperationDialog.vue | 6b44e2879ceb4bd420999b1e22b8af9f8618ed00ea8205540ec34c0b46b71f6e |
| src/components/console/ConsoleTableShell.vue | f9654ae8877afbc09dda9cad6448fe6fd663e4d1d082380de6e5565f547de7c0 |
| src/components/console/ConfigRevisionBar.vue | 843aa0a23e222b5981199b32d044163f354c76647b0ccbe264502cccd4254c56 |
| src/components/console/LocalLogPanel.vue | f3828bad126027d6864566898c71420475f3f334fa6b7ae56b847f2dd1c19ee1 |
| src/components/console/ReadinessGrid.vue | 963d9607373f7a06c8e9f494bd446a763bd1344bf36dc9e6a2da9d0aeaff0b3e |
| src/app/plc/components/SourceImportPanel.vue | 7d9509c203d47443442490a34d8f30be5a11e59e046c2e385c93ce60a9a0678a |
| src/app/plc/components/PointNamePreviewDialog.vue | f94dd11e3cc39a2d3b771ef7c2e2a6087e4879d078f52a45d850b6449b3cc154 |
| src/app/plc/views/points/index.vue | 333927927e556f7a1557ec02ff8010e0c6e43fe229e6b2f736d3308eee8d824d |
| src/app/plc/views/diagnostics/index.vue | 27dd7a75245acc080ca070de35a6e2e0579969ee017316143b452f2456714746 |
| src/app/runtime/views/overview/index.vue | 187f7d753e23d268822d4afbf0d3e38d176d14bf93f83db12c32a6059cce5b5b |

现DS五枚`src-tauri/icons/{32x32.png,128x128.png,128x128@2x.png,icon.icns,icon.ico}`与DAA逐SHA已相同；具体SHA在附录A r4 §2.8，不称缺失/占位、不重画。Tauri配置icon五路径实际存在。组织标识/导航/主题/语言链为`src/App→layouts/AgentLayout→shell wrappers→@aw-ui`、`sections.icon→@element-plus/icons-vue`及CU sidebar-footer brand文本；当前DAA/CU这条链未引用独立src/public组织logo图片，不臆造缺失logo。保留既有组织AIIS身份/图标及布局，只把应用标题/语义换DS，不改CU源码或把DAA名当组织名；系统Dock/窗口/开发态图标要按平台实测，文件同SHA本身不是呈现证明。

### 2.3 从DAA直接派生的可审查流程

批准后先在T5/stage/<role>/daa-source/复制**隔离的DAA公共工程源码快照**，保持原目录装配，绝不在DAA原树删改。输入闭集是本轮1913文件baseline中DAA下：7根工程文件（package/pnpm-lock/pnpm-workspace/index/vite/两tsconfig）、全部`src/`、`src-tauri/src/`、icons/及Cargo.toml/Cargo.lock/build.rs/tauri.conf.json/capabilities/default.json，共**196文件**，按完整仓内path排序`path<TAB>SHA<LF>` digest `4751262a5c68aa28f037f9214b43d980587059663e762de096f9b5462bf855e9`。执行前按同规则重算并输出逐文件清单，不一致blocked回协调，不自动取latest。此闭集不含真实.env、profile/SQLite/日志/凭据、node_modules/target/dist/gen、DAA plans/tests/config YAML；不在暂存中构建/运行DAA。导入/日志/点位页仅取可用展示/控件模式，全部换DS DTO和单状态owner，不照搬私有DAA业务。

再按§5正式allowlist组合到D：保持有效Rust/native不被覆盖；已同字节壳/图标保持不动，保留main.ts的适用EP注册/样式顺序/分页overlay、App配置provider/真实owner/主题作用域；删除暂存DAA collector/history/upload/migration/backend/store/旧IPC依赖边，装配DS service/页面。不把暂存整个DAA tree覆盖D后留下可执行业务。每个目标记录source path/SHA、copy/adapt/new/kept及必要差异；适用资产和UI复用核的是完整链而非只37个文件计数。源工程/共享核心全部只读。

## 3. 产品合同与新增编译面

### 3.1 运行架构、拓扑与类型

D=`automation-world/device-simulator/`、R=`D/runtime/`继续交付。产品业务唯一Rust owner：Tauri薄IPC→DS应用服务→配置/导入/policy编译→每instance唯一owner；native Snap7只协议解析/编码/IO/连接hooks/真实pthread_join。Rust拥有所有DB image、六来源准入、CAS/epoch/point seq、规则、逐item公平、连接/字节预算和控制；不另建Vue规则、C++业务image或SQLite运行值副本。

manager用UUID索引实例，DB用稳定db_id+db_number查找；同端口/同DB号仅在对应实例约束，不以A/B字符或数组下标代表身份。新建默认empty/unconfigured；已加载各selected revision也一律stopped，不自动bind/恢复running意图。首版提供手工新增/改名/删除instance/DB/point及导入，用户DB号/长度/端口不由名称、文件顺序或默认DB41推断。运行内存按实际DB长度有界分配，point版本/coverage按已编译字段/区间保存，不把原8192-bit固定元数据数组乘进全部64KiB DB；实际容量/拷贝/节点/线程都纳入预算，不能仅把类型改Vec而无上限。

容量沿设计：最多8实例；每实例32DB/4096叶（对多个DB聚合）；DB1–65535且实例内唯一、长度1–65536。单源≤1MiB、批次≤4MiB、128输入、深度8、数组1024，命名1–100 ASCII bytes。runtime配置总序列化payload（含源版本/树）≤16MiB；保存前计source/revision写入与journal及空闲空间，配置库main+journal+待写保守预留总≤128MiB且volume空闲≥512MiB，不足明确storage_full、不删历史腾空间。本MVP不自动修剪revision/source，不作长期无限历史承诺。运行image/coverage/metadata构建须在512MiB核心预算内先计实额，超限拒apply并保留旧版，不能截DB或降leaf数。

类型完整落实设计：BOOL；BYTE/USINT/CHAR；WORD/UINT/INT；DWORD/UDINT/DINT/REAL；STRING[1..254]，其余明确拒绝。大端、signed范围、finite IEEE754 f32、ASCII CHAR/STRING及完整n+2包；BOOL mask不改邻位；partial scalar/STRING、错误头/NaN/Inf/溢出/非ASCII在commit前拒绝。原raw协议不需声称point类型，按完整触达coverage+typed stage校验。DS类型默认全零/false/CHAR NUL、STRING max=n/actual0+零填充；DS显式初值优先。TIA :=/BEGIN始终不导入，RETAIN不改变同进程/跨进程保值合同。

规则实现fixed/ramp/sine/seeded random及BOOL toggle，不加脚本/响应状态机。min/max/period/phase/seed有类型化范围、period≥100ms；整数ramp/sine以clamp后floor向负无穷取整，REAL转有限f32；random以SHA256(instance UUID/point UUID/配置seed/模拟时间桶)首8B大端模整数闭区间，REAL用高24位映到[min,max]，不是密码学随机/无偏分布承诺。toggle以half_period桶奇偶翻转。统一monotonic模拟时间，pause/stop冻结、resume不补跑；fixed无变化不递增seq/值时间但仍持续rule owner。自动区client/UI包括维护都禁写，pause不让权。

### 3.2 DS单配置SQLite v1与版本/CAS

本r5明确授权的**新本地DS schema**不是Backend数据库迁移，也不迁入DAA任何表/数据。仅`<profile>/device-simulator-v1/config.sqlite`；profile默认Tauri独立`app_local_data_dir()`，可选绝对`DS_PROFILE_DIR`显式覆盖，无必需G0键、不搜索父目录.env/DAA目录。同profile OS锁`.ds-profile.lock`用fs2，持有到正常shutdown/DB关闭；第二进程明确profile_in_use，不自动抢锁/改目录。只创建自身空目录；symlink、已有未知appID/版本/坏库、异常WAL/SHM、缺关键文件/引用一律报错停机，不删库重建/迁DAA。

schema首版为以下普通rowid表/完整普通索引；application_id=`0x44535631`，user_version=1，format=`ds-config-v1`。显式`migrations/0001_initial.sql`由DS store在**新空库**单事务执行并登记；以后版本迁移不在本次自动执行面。初始化失败保留失败证据/可恢复文件，不把半库当新空库再覆盖。新库DELETE/synchronous=EXTRA、foreign_keys=ON、busy_timeout=1000ms、page_size4096、mmap0、trusted_schema=OFF、禁extension/任意SQL；不启WAL、FTS/SQLJSON/复杂索引或DAA双库/journal合同。

| 表 | 最小字段、约束与责任 |
| --- | --- |
| schema_migrations | version INTEGER PK、migration_sha256、applied_utc（SQLite时间）；只记录已执行v1。 |
| workspace_metadata | singleton=1 PK、profile_id UUID UNIQUE、format_version、created_utc；身份不可被普通save改写。 |
| source_blobs | sha256 TEXT PK、utf8 BLOB、byte_len；核实际原UTF-8/BOM/CRLF bytes，不按规范化文本算hash。 |
| source_versions | version_id UUID PK、lineage_id、blob_sha256 FK、logical_name、import_profile、metadata BLOB；不可变来源/闭包证明；同hash可共享blob但不合并lineage。 |
| configuration_draft | singleton=1 PK、etag UUID、canonical_payload BLOB、sha256、updated_utc；完整workspace草稿CAS。 |
| configuration_revisions | revision_id UUID PK、saved_seq INTEGER UNIQUE、payload BLOB、sha256、created_utc；保存产生不可变workspace revision，内容摘要可核，引用来源版本。 |
| instance_selection | instance_id UUID PK、revision_id FK、slice_sha256、previous_revision_id nullable FK、selection_etag；每instance选中不可变revision内自己的切片；无loaded/运行值列。 |

source/version insert+draft CAS+不可变revision在同一短SQLite事务，未变化保存返回unchanged且ETag/revision不增；格式/重复身份硬错误拒绝，合法但未确认的候选可保存并标issue，不能apply。派生hash/tree/coverage/name证明只由服务生成，普通保存不能伪造。UI保留dirty编辑副本，冲突返回currentEtag供比较，不自动覆盖。SQL在独立有限worker（1执行+4等待，单查询≤100条/1s预算）处理，不能持内存owner锁等待磁盘；stop独立控制不排其后。提交/ack未知查询真实draft/selected事实，不确定不自动重试，不虚报回滚/成功。SQLite3.46.0已知版本风险沿DAA原评估保留，本任务仅窄查询/普通表/DELETE，并对自有事务故障独立实证，不把已有DAA接受当DS库安全证明。

### 3.3 导入、重导、手工地址与命名

流程：选择instance→读取多.db/.udt原字节→scan_sources一次catalog→每DB显式DeclarationRef/UDT闭包/目标DB绑定→expand_db→差异预览→确认仅保存candidate；layout_standard/plan_names是独立显式预览/确认，不start。DeclarationRef只在本catalog定位；source_lineage_id/version_id/db_id/point_id由DS UUID持久化，db_number/文件名/下标不是主键。完全相同source+绑定+闭包重导为unchanged；同名不同lineage/重名UDT须用户选择，不自动hash合并身份。

继承结构化Field/Index路径的同点保ID；删除/改名/类型/地址/DB号/长度变化列完整diff并确认，受影响DB地址证明与受影响点初值/策略确认失效；旧初值仅待比较候选、不自动转换。改名/跨结构不可证明同身份者按删除+新增列明，不用相同offset偷偷续ID。未选DB/其它instance来源、ID、确认不改；同名UDT新版本不污染已绑定旧闭包。手工建DB/point或转手工结构明确标manual，保留原源但不冒充其派生证明。

导入/地址/命名preview token有界≤8个/profile、300s，绑定ETag/输入hash/闭包/选择/候选摘要，编辑或stale后重预览；确认重证后单事务，不拿前端confirmed=true当证明。layout只对完整明确非优化受限树，含STRING整DB拒推；手工地址/理由不被批量覆盖。core只给leaves{path,byte,bit}+length，DS编译完整bit coverage、padding reserved读零/禁写、无重叠/溢出、末端≤DB长度；不另造stride或跳过未知叶。应用要求全部启用DB结构/叶地址/名称/初值/策略确认有效，不能只选几叶猜完整布局。

每instance一次完整NameBatch，包括未选/停用/legacy/manual保留名；与core原字符串大小写敏感碰撞一致，禁止casefold/逐DB先生成。数组/非ASCII pending保留原路径，地址由用户确认后由同core一次地址兜底；启用pending阻断apply。固定v1 names.db/udt/expected-v1/layout-oracle用于**DS消费者**独立测试，原oracle不变；产品合成权限回归DB41/57只是另一个测试workspace，非v1导出/产品默认拓扑。

### 3.4 保存、停机apply、保值和恢复

saved/selected/loaded及lastServedRevision分列：保存不应用；apply仅完全stopped且callback/连接/队列已释放的实例。owner内取有界typed旧值快照（image身份/epoch/seq/control_generation），锁外构建candidate+兼容清单；UI确认摘要→控制序列复核→**owner外**单SQLite事务CAS selected→安装新image/new epoch→loaded、仍stopped；start独立。其间start/pause/resume/stop/reset或值/模拟时钟变化使generation/seq复核失效，重新预览确认，不能安装陈旧快照。

| 场景 | r5默认行为（逐项集成测试） |
| --- | --- |
| 同进程stop→start | 全值/规则模拟时间保留；断连重连也不reset。 |
| 同布局仅名称/显示/连接限额 | 停机apply；稳定ID/布局/类型/确认/effective值语义兼容者含规则点可保值/时间，不恢复连接。 |
| 规则参数/周期/seed变 | 兼容hold保留，全部规则和统一规则时钟t=0。 |
| 初值变 | 受影响点新初值，其它兼容hold保留，全部规则t=0。 |
| mode/owner/读写/维护权限变 | 受影响点初始化，其它兼容hold保留，全部规则t=0；取消旧epoch积压。 |
| DB号/长度/结构/地址/类型/增删点 | 受影响DB整体初始化，其它DB仅严格兼容hold保留；新增初始化、删除丢弃，全部规则t=0。 |
| 显式reset | stopped确认丢值；当前loaded全初始化/new epoch/seq归零/规则t=0，仍stopped。 |
| 跨进程重开/崩溃 | 按真实selected完整校验、全部初始化/规则t=0/stopped；不恢复连接、运行意图或运行值。 |
| 回旧revision | 默认全部初始化且用户确认；不从日志恢复运行值。 |

混合变更合并更严格影响。保留以typed值重新编码，不复制旧bytes到新布局；证明/编码失败在selection前拒绝、旧版/值保留，用户可明确改选initialize_all，不静默丢值。同selected且loaded内容一致的apply重试返回already_loaded、不换epoch/初始化；selected同但未loaded只重建加载，不重复选择。预校验/SQL确定rollback旧selection不变；commit未知查询、不确定selection_unknown禁start；selected已提交而安装失败为load_failed且新selected真实存在，旧image仅诊断禁服务；安装后ack丢失刷新loaded，不回滚/盲重试。无跨SQLite/RAM原子承诺或额外持久journal。重开selected坏/缺不自动用latest saved/旧版代替。

### 3.5 页面、IPC、配置和运行值的闭环

沿DAA的Element Plus/CU公共壳及弹层，默认工作台；配置中心分组保留，增加“在线值”“日志”正常导航，桌面/窄窗/中英/主题均可用。DS状态胶囊显示真实instance聚合运行/错误与IPC/配置状态，不沿用“上传待接入”或两枚硬编码StoppedG0。标题/组织标识分离，ds.theme/ds.locale/DS反馈容器独立。

| 页面与真实动作 | DTO/服务与可观察结果 |
| --- | --- |
| 工作台 | 实例表/卡显示endpoint、saved/selected/loaded/epoch、state/C/H/TCP/closing/queue/错误；逐项start/pause/resume/stop/reset，批量只逐项结果，不全局原子。无实例为真实empty并有创建入口，不用demo卡。 |
| 配置中心→实例 | CRUD/限额/端口/rack-slot-TSAP；保存/加载版本/apply预览确认；运行中保存candidate可以，apply禁用且指向stop；删除先释放资源并列引用。 |
| 配置中心→DB点位 | 逐instance/DB多源导入预览确认、完整树、DB号/长度、手工增删、address preview/confirm、命名批次preview/confirm、初值提示/确认。10/20/50分页跨页选择，取消零写/保留输入。 |
| 配置中心→模拟与读写策略 | instance→DB→不重叠policy region→point逐属性effective来源；owner/mode/read/write/ui_maintenance/初值/rule参数，冲突到具体bit/字段；默认hold/owner none/读开/写及维护关。 |
| 在线值 | 单页≤100点、≤1Hz同owner读快照，标epoch/seq/time/source/stale；普通typed UI仅ui owner，client/none hold的显式一次性维护默认关，确认new/old/revision/epoch/pointSeq及“客户端随后可覆盖”；CAS冲突重确认，rule即使pause也拒绝。不改配置初值、不另开S7自读连接。 |
| 连接/日志/存储 | 连接面板列真实阶段/占额/peer/last IO/inflight/bytes/关闭原因，确认单close；有界日志分页过滤、配置路径/容量/observability_degraded/丢弃缺口，不复制DAA采样历史/清库/ACK/上传。 |

Rust IPC白名单：`ds_get_bootstrap`、`ds_get_runtime_snapshot`、`ds_get_configuration`、`ds_save_configuration`、`ds_preview_import`、`ds_confirm_import`、`ds_preview_layout`、`ds_confirm_layout`、`ds_preview_names`、`ds_confirm_names`、`ds_preview_apply`、`ds_apply_revision`、`ds_control_instance`（start/pause/resume/stop/reset）、`ds_write_point`（ordinary/maintenance来源白名单）、`ds_close_connection`、`ds_query_logs`。不用任意raw-write/SQL/文件路径/进程执行命令；导入输入为受大小限制的所选文件名与bytes，不从前端路径递归读文件。配置CRUD通过有类型的DS草稿及派生字段保护；所有变更经服务，前端只提交意图。

请求/响应严格DTO/deny_unknown_fields，后端序列化camelCase，UI不自行猜映射；`operationId/instanceId/expectedEtag/expectedLoadedRevision/epoch/pointSeq`按操作必须项复核；结果含明确`result/errorCode/committed/receiptState`，u64 seq/epoch/version以十进制字符串经IPC避免JS失真。参数/许可/冲突/保存失败与提交未知分别有稳定errorCode+i18n，不把String异常直接当成功。可见窗口一个宿主状态owner/≤1Hz轮询，隐藏暂停，失败保留stale，不产生配置写/start。browser无Tauri仅unavailable，不走mock保存。

### 3.6 正常启动、依赖与native构建

普通用户（已安装README列出的Rust/Node/pnpm/CMake/clang/SDK后）在D运行`pnpm install --frozen-lockfile`和`pnpm tauri dev`，无需DS_PROFILE_DIR、DS_G0_PROFILE_JSON、DS_G0_RUN_ROOT、marker、DS_G0_NATIVE_LIB_DIR或私有/tmp/source/cache。`tauri.conf.json build.features=["native-s7"]`显式传Cargo（[官方features配置](https://v2.tauri.app/reference/config/#features)），不能只依赖Cargo default：用户原日志有`cargo run --no-default-features`，正常Tauri argv/实际feature图须仍含native-s7，普通dev/build都是真native、不可退stub。构建脚本负责`R/build.rs -> ../native/CMakeLists.txt -> OUT_DIR/native-build与OUT_DIR/native`，相同flags/source/SDK变化触发重建，失败给可诊断错误。保留动态链接形态：runtime Cargo `links="ds_s7_native"`输出native libdir metadata，desktop build.rs消费DEP元数据自动配置rpath；普通dev/正式build均核file/otool及实际链接，不要求用户设DYLD/PATH替代库。受控native/bridge名去G0语义，ABI行为不放宽。macOS arm64是本轮实证目标；其它目标缺支持明确失败，不静默stub。

固定工具/源版本沿r4：Rust1.89.0/Cargo1.89.0、Node22.19.0/pnpm11.11.0、CMake4.0.2/clang17/SDK26.1、Snap7 1.4.2包SHA `1f4270cde8684957770a10a1d311c226e670d9589c69841a9012e818f7b9f80e`、r4受控patch SHA `3c3fa385e760f4f9549b14d70545962f0ebebe121d0c4d7401048840fc850ed9`为迁移起点。Rust业务不能退C++，原八文件controlled边界/上游只读/许可材料及int FFI保持；真需表外native/改协议主循环/换候选则回PM，不因产品化获得重写栈权限。

新增直接依赖只从DAA锁定548 registry bank取既有包，bank digest `cca1d6efbbdd7767a2475f786bf5a67fa64056bca17bff66d4113d4f40615cfa`：R在原serde1.0.228/json1.0.150/sha2 0.10.9/libc0.2.186/tracing0.1.44/subscriber0.3.23/appender0.2.5上加**rusqlite=0.32.1(bundled)、uuid=1.23.3(v4)、fs2=0.4.3、path core=0.1.0**（R/Cargo.toml的path="../../shared/tia-import-core"）；libsqlite3-sys0.30.1/SQLite3.46.0是原锁传递面。desktop仍tauri2.11.3/tauri-build2.6.3/serde与ds-runtime，原未用的直接core根可由R消费收口；不引SQL插件/sqlx/sea-orm/Tokio业务调度或DAA app依赖。Pure test可明确`--no-default-features`但不能作为产品入口通过。真实DAA兼容client仍独立六根+原五模块/core（附录A §2.5），不改DAA。

前端依赖/lock/integrity沿r4/DAA：Vue3.5.38、EP2.14.2/icons2.3.2、i18n9.14.5、Tauri API2.11.1/CLI2.11.3、Vite5.4.21/plugin5.2.4、TS5.9.3/vue-tsc2.2.12；不新增UI测试框架/插件依赖。本r5不执行Cargo解析/编译；未来受控离线锁定时runtime/desktop/兼容client分别出实际feature图/子集，不能把old54/430/60包数当新增SQLite后已证值。缓存缺包可用原锁/hash匹配的既有cache，需新增集合外版本/依赖或无法闭合就blocked回PM，不自动升级。

## 4. 自动化验证、原生退出与协议门槛

### 4.1 已核官方能力与选择

2026-10-21只读核[Tauri官方测试](https://v2.tauri.app/develop/tests/)、[WebDriver](https://v2.tauri.app/develop/tests/webdriver/)、[capabilities](https://v2.tauri.app/security/capabilities/)、[icons](https://v2.tauri.app/develop/icons/)与[配置/CLI](https://v2.tauri.app/reference/cli/)。当前官方已说明macOS可用额外embedded WebDriver插件；直接tauri-driver仍只有Windows/Linux，不能沿用“macOS无法任何自动化”结论。本任务选择**锁内Tauri原生API+有限内部测试driver**，不新增WebDriver server/付费服务/plugin，也不借浏览器mock代native。

锁内tauri2.11.3源码`webview/webview_window.rs` SHA `00b40c71c0462ea3a714be638d5b76ab47ceddf5f6043e1188ab1e9ea2dcea69`，2216行close()明确先发CloseRequested，destroy()强制无该事件；2403行eval()评估当前WebView JS。`path/desktop.rs` SHA `11bb4f74c6053cc0eca33a54da00a4a31aff85c5164e7260cd573b5efec18ebc`的app_local_data_dir按identifier隔离。版本化docs.rs读取失败已如实记录，以冻结官方crate源码实核API，不借latest文档宣称已有运行证据。[官方JS close/destroy差异](https://v2.tauri.app/reference/javascript/api/namespacewebviewwindow/)同为辅助依据。API存在仅证明方案有真实入口，实际UI/退出仍须DEV与fresh QA实证。

### 4.2 非默认自动测试入口

新增desktop/R的非默认`test-automation` feature与显式绝对`--ds-test-manifest <T5/profile/role/scenario.json>`；必须两者同时满足，manifest有owned marker/run id/source候选/场景白名单/显式隔离DS_PROFILE_DIR及允许端口，禁止默认用户profile、真实.env、symlink/目录越界。普通`pnpm tauri dev`/`tauri build`没有此feature，不注册test命令/不包含测试driver/不响应该参数；不能单凭Vite模式/环境键在产品中开启控制。测试build用T5内生成配置固定identifier=`com.aiis.aw.devicesimulator.validation`，与产品com.aiis.aw.devicesimulator分开，macOS metadata同配置一致；记录实际WebView数据路径/新建归属，不能借真实DS/DAA偏好或profile作测试隔离。测试build不用于最终用户交付，产品与测试build分别有SHA及feature/测试identifier这两项必要差异对账。

测试driver从本任务固定`tests/ui/native_driver.js`编入test-only Rust模块，通过主WebView eval注入，等待实际UI ready/元素可交互，再以稳定data-testid/role驱动**真实DOM输入/change/click/分页/确认**并等待真实`ds_*` IPC/DTO/渲染结果。导入用固定合成File/DataTransfer，不读取任意真实文件；不直接改Vue state/内存或mock IPC。唯一test-only `ds_test_report`只接收已知step/status/断言摘要，Rust核case/id并存证；不接受任意JS/SQL/shell/socket指令。driver自身可访问真实DOM、故不能被称外部物理输入/视觉完整证明。

测试末由Rust主窗口**Window.close()**请求，走与用户关闭相同的CloseRequested→脏编辑保存/丢弃/取消→服务停止/真实join→日志有界flush→SQLite/锁释放→正常退出。测试脚本只通过真实弹窗按钮选择预定答案；不调用destroy()/process exit()/TERM代正常退出，也不自动跳过dirty确认。记录CloseRequested、shutdown gate/各实例joined、SQLite关闭/锁释放/Exit、wait code0和退出后PID/端口；从最终确认关闭意图到清理完成保守≤5s。超时blocked/fail后仅资源收尾可按owned PID TERM/KILL并记中断失败；不得把它改记成功。

本机native自动场景固定三轮但不请Owner反复关窗：N1普通入口/空profile不监听+编辑导入保存后正常关闭；N2同隔离profile重开、验证selected恢复初始化/stopped、显式start及在线值/规则/真实客户端、正常关闭；N3再次重开值恢复初值/stopped，覆盖dirty取消/丢弃与连接关闭/正常退出。UI语言/明暗/刷新/导航/图标检查纳入一次有意义UI回归，变化按影响复测；未变源可精确引用已有视觉事实，但不拿旧binary充新入口/native/退出结果。成品Owner审阅一次，不作每个协议case前置。

正常入口与自动测试build分别实测：普通`pnpm tauri dev`使用owned DS_PROFILE_DIR（只为了保护用户数据，不是启动必需）证明beforeDevCommand/Vite15194/Cargo实际argv/feature图中的native-s7、实际native/SQLite/IPC；此项结束dev watcher属于开发进程收尾，不冒称正常UI关闭、不制造人工关窗gate。release `pnpm tauri build --no-bundle`后测试feature版跑N1–N3，证明真实WebView正常Window.close及active listener释放。无DS_PROFILE_DIR的默认解析以固定Tauri API及路径解析测试核实，不能用测试manifest作为普通入口必需项；所有本轮native写入都用新owned profile，不读取/修改已有DS/DAA数据、不改HOME。默认路径调用实际由普通startup同一代码消费，若未在真实默认用户路径启动，明确这一观察限制，不把纯解析测试写成默认路径native实测。不宣称no-bundle裸Mach-O必被CUA绑定或产生已验证Dock品牌，需实际平台观察，不能拿IPC alone补视觉结论。

### 4.3 协议、资源与受影响复测

原19个W01–W09/C01–C06/D01/D02/X01/X02向量原行在§7保留，不缩时长/轮数/offered/阈值。迁入正式tests并通过**同R产品runtime**的test-only薄宿主运行，合成workspace由产品配置编译器/typed初值构建，DB41/57只是回归profile；不在产品启动自动加载它，也不以old G0编译产物替代新runtime。W02 overlay/W09 barrier/小预算故障仅`test-automation`下已知hook，不放普通产品准入策略。新业务页面/SQLite/规则还须§8产品矩阵，不把19case当全部产品验收。

协议测试独立于Tauri窗口三轮，只以来源/新构建ABI/ownership/B0及相应配置前置为gate，可先Rust/SQLite/import tests→无端口ABI→真实loopback协议，与UI测试串行复用端口，不等Owner手动操作。原G0运行时80/300秒等数字不降；配置/规则变化必须复测W/C/D/X受影响功能，最终稳定候选DEV完整适用矩阵、新fresh QA独立重建/完整适用矩阵。仅改文档/未变前端不用机械重复主题/人工关窗；新binary正常退出/资源证据不能省。源或测试方法再改要记录新candidate、依赖影响及必要复测，不伪称继承旧QA。

C01保留**独立产品runtime测试宿主全树**口径：不启动Tauri/WebView；平均CPU≤单逻辑核100%、RSS≤512MiB/300s净增≤16MiB、≤64线程/≤1024句柄；C06 B0+16MiB/末五中位差≤8MiB及增长判据沿原文。Tauri/WebView/SQLite/profile/N场景资源另外全树报告，不能套C01 headless阈值或漏成零；产品关闭≤5s及所有listener/worker/队列释放必须满足。长存活核心/客户端1Hz+状态采样完整；短于1s负例单样本CPU均值null/不可评估，采样峰不冒充全寿命峰，不强填0。真实SO_RCVBUF/SO_SNDBUF≤16KiB用于C04，未读FIONREAD/历史广告credit/TCP窗口另列，不能把SO当kernel物理硬限；标准peer选项不改原offered/native约束，真实send阻塞是必证。所有时间Rust/native同CLOCK_MONOTONIC，100夹点探针；Python只同源clock/校准区间，不比较不同绝对原点。

## 5. 精确路径、允许动作和源码迁移

### 5.1 当前PM与未来角色

当前仓内唯一可写是本spec；私有辅助只在`/private/tmp/arch-aw-005-r5-correction-umza_thx/pm/`。不改tasks/checklist/DS正文/实现/依赖/索引/P、不复制工程/建schema/运行产品/清理G0。主协调仅机械同步根PLAN pair及plans/README pair本任务既有行r5 draft。

以下是**已获Human Owner精确r5批准的DEV执行allowlist**。D/R为前述正式树；N=`D/native/`、V=`N/vendor/snap7-1.4.2/`、J=`D/tests/`，不保留产品S=g0路径依赖。所有括号展开为精确成员，非任意目录通配；vendor仅原固定34-member各自闭集/八受控源可改。当前没有这些新增产品文件，不预建。

| 正式路径（相对D，特别标注除外） | r5允许的动作与责任 |
| --- | --- |
| README/README.zh-CN、PLAN/PLAN.zh-CN（均.md）、BUILD.md/BUILD.zh-CN.md、plans/README.md/README.zh-CN.md；R README pair；新增N与J README pair；src/app/README.md/README.zh-CN.md | DEV写独立产品身份、正常dev/build、profile/schema/能力限制、同唯一根005归属；无重复bundle/新ID。 |
| .gitignore、.env.example、package.json、pnpm-lock.yaml、pnpm-workspace.yaml、index.html、vite.config.ts、tsconfig.json、tsconfig.node.json、source-inputs.json | 沿DAA装配、只批依赖、忽略target/dist/node_modules/DB/logs/gen；Vite15194/preview14194 strictPort/envDir:false；环境例仅DS可选profile/日志，不带真实信息/G0必需键。 |
| src/{App.vue,main.ts,env.d.ts}、src/styles/app.css、src/layouts/AgentLayout.vue、src/components/shell/{AgentSidebar.vue,AgentTopbar.vue,RuntimeStatusCapsule.vue} | 保留适用DAA/CU壳/EP/provider/主题overlay，改DS真实状态；不重写已有效相同壳/图标。 |
| src/components/common/MetricGrid.vue；src/components/console/{ConsoleActionButton.vue,ConsoleCard.vue,ConsoleInfoGrid.vue,ConsoleMetricCard.vue,ConsoleOperationDialog.vue,ConsoleTableShell.vue,ConfigRevisionBar.vue,LocalLogPanel.vue,ReadinessGrid.vue} | 明确15来源中适用控件适配，剔除DAA DTO/IPC/采样业务；ConfigRevisionBar/LogPanel只消费DS配置/日志。不复制LocalHistoryPanel/YamlMigrationNotice。 |
| src/console/{types.ts,sections.ts}、src/console/composables/{useAgentConsoleShell.ts,useAgentLocale.ts,useAgentTheme.ts,useDeviceSimulator.ts}；src/services/deviceSimulator.ts；src/locales/index.ts及src/locales/{en-US,zh-CN}/{common.json,navigation.json} | 纯壳偏好、DS单状态owner与16项IPC facade/DTO/错误/i18n，业务文案入simulator模块；不得注册daa_*。 |
| src/app/simulator/manifest.ts、src/app/simulator/locales/{en-US,zh-CN}.json、src/app/simulator/views/{overview,instances,points,policies,values,logs}/index.vue；src/app/simulator/components/{SourceImportPanel.vue,PointNamePreviewDialog.vue,InstanceEditor.vue,PointEditor.vue,PolicyEditor.vue,ApplyPreviewDialog.vue,ConnectionPanel.vue,ValueWriteDialog.vue} | 6类正式页面与有限业务组件，复用已有UI范式/引用，真实DS导入/配置/控制/值闭环；无长期demo/mock成功。 |
| src-tauri/{Cargo.toml,Cargo.lock,build.rs,tauri.conf.json,capabilities/default.json}、icons/{32x32.png,128x128.png,128x128@2x.png,icon.icns,icon.ico} | 后一icons均在src-tauri；独立DS身份、正常dev real native、锁内依赖/自动rpath；保持既有5图标，不新增signing/install/remote capability/plugin。bundle.active=false，no-bundle不承诺系统注册。 |
| src-tauri/src/{main.rs,lib.rs,app.rs}、commands/{mod.rs,runtime.rs,configuration.rs,import.rs,queries.rs}、config/{mod.rs,bootstrap.rs}、testing/{mod.rs,native_driver.rs} | 薄装配/16IPC/有序shutdown；testing仅非默认feature+owned manifest，无普通测试surface/任意eval命令。各子目录在src-tauri/src下。 |
| R/{Cargo.toml,Cargo.lock,build.rs}；R/src/{lib.rs,app.rs}；config/{mod.rs,workspace.rs,profile.rs}；domain/{mod.rs,image.rs,policy.rs,request.rs,result.rs,configuration.rs,source.rs,layout.rs,typed_value.rs,rule.rs} | R/src下配置/领域文件；现有Rust保留演进，替换固定A/B/DB/点数组、typed codec/policy/规则与新SQLite根，不创建第二owner。 |
| R/src/services/{mod.rs,owner.rs,scheduler.rs,lifecycle.rs,configuration.rs,source_import.rs,layout.rs,naming.rs,apply.rs,queries.rs}；R/src/infrastructure/{mod.rs,native_ffi.rs,clock.rs,logging.rs,resource_sample.rs,profile_lock.rs} | 真实业务用例/停机apply/保值/连接/日志，SQL/网络不在owner等待；来源证明由服务生成，不fork core。 |
| R/src/infrastructure/config_store/{mod.rs,schema.rs,queries.rs,transactions.rs}及migrations/0001_initial.sql（同config_store下） | 仅§3.2新DS本地schema与查询，初始化/身份/事务测试；不改DAA/Backend schema，不建采样库/存值历史。 |
| R/src/bin/ds-test-host.rs；R/src/testing/{mod.rs,hooks.rs}；R/tests/{owner_contract.rs,ffi_contract.rs,clock_contract.rs,configuration_store.rs,source_import.rs,layout_naming.rs,typed_rules.rs,apply_retention.rs,lifecycle_protocol.rs} | test-host/hooks仅required-features=test-automation，复用真实App/服务的隔离测试入口/有界故障注入；默认产品无此CLI/stdio/barrier/overlay。 |
| N/CMakeLists.txt、bridge/{ds_s7_bridge.h,ds_s7_bridge.cpp}；V/{upstream,controlled}/原34成员、upstream-manifest.json、controlled-manifest.json、native.patch、NOTICE.md | 从原g0迁移有效native源/许可，bridge重命名不改ABI/ownership；仅controlled core/s7_server.{h,cpp},core/s7_isotcp.{h,cpp},sys/snap_msgsock.{h,cpp},sys/snap_tcpsrvr.{h,cpp}八文件可修有限hook。原库无新协议栈/线程框架/表外改动。 |
| J/protocol/{reference_main.cpp,wire_cases.hpp,wire_cases.cpp,resource_sample.cpp,CMakeLists.txt}；J/compatibility/daa-client/{Cargo.toml,Cargo.lock,src/main.rs,src/domain/mod.rs,src/infrastructure/mod.rs} | 迁移参考client/原始wire及真实ManagedS7消费，独立于product link；不修改DAA/core。core相对`../../../../shared/tia-import-core`；mod.rs到DAA为`../../../../../../data-acquisition-agent/src-tauri/src/{domain,infrastructure}/...`，必须realpath/dep-info核层数。 |
| J/fixtures/{product-workspace.json,protocol-workspace.json,invalid-cases.json,typed-vectors.json,rules-vectors.json,README.md,README.zh-CN.md}；J/ui/{native_driver.js,scenarios.json} | 手写合成输入/独立期望，协议workspace按§7原DB41/57/marker；产品另用共享v1和非41/57的手工多DB，不重写shared expected/oracle。无真实DB/现场源。 |
| scripts/{derive_daa.py,build_native.py,run_validation.py,run_protocol.py,collect_evidence.py,verify_evidence.py,retire_g0.py} | Python3.9 stdlib工程编排/证据，不做产品业务owner；裸入口帮助无写；显式source/run/profile/role，受限owned列表，自动native测试不新增HTTP/控制端口。 |
| 旧g0所有**当前已列原文件**；R/src/{bin/ds-g0-server.rs,bin/ds-g0-abi-probe.rs,commands/mod.rs,commands/stdio.rs,config/g0_profile.rs} | 只在§9先封存/迁移/验证/引用闭合后移除废弃G0源；runtime有用逻辑移入上列正式路径，不能整目录rm/删新源；保留任何仍被引用者即列未完成阻断清理。 |
| 仓根docs/AIIS_DS_Detailed_Design.md、docs/README.md/README.zh-CN.md、CODE_INDEX.md | DEV仅DS r5产品实施/验证分层及真实新结构，DS索引行；其它AW/DAA/SMA/006/007正文和004 bundle原字节保护。 |
| 本bundle tasks.md / checklist.md；新P5下五JSON | DEV只追加r5 tasks与实现/证据manifest；独立QA只追加checklist。P4旧五文件不改；主协调仅按实际checklist机械状态/事实链接同步P5、根4索引。 |

正式allowlist不含DAA/CU/core或任何真实profile/env/DB；DAA196快照仅T5暂存只读来源，不赋给D整树覆盖权。新增文件若只是上表已列实现的合理拆分但超精确成员，先回PM/Owner审具体增量，不用目录通配自行扩大。

### 5.2 临时、持久证据与端口

T5=`/private/tmp/arch-aw-005-r5-exec/`，DEV/QA各`stage/{dev,qa}`、`build/{dev,qa}/{native,runtime,desktop,daa,frontend}`、`cache/{dev,qa}/{cargo-home,pnpm-store}`、`tmp/{dev,qa}`、`profile/{dev,qa}/{normal,native,protocol}`、`runs/{dev,qa}-NNNN`。A5=`/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r5-evidence/`，dev-run-NNNN/qa-run-NNNN及r4-stop-snapshot。P5=`plans/ARCH-AW-005-ds-g0-prototype-validation/evidence/r5/`仅input-manifest.json、delivery-source-manifest.json、protocol-baseline.json、evidence-index.json、resource-closeout.json。此刻不创建T5/A5/P5。

默认正常构建产物可在D忽略target/dist/node_modules/gen；实验角色用T5派生OUT_DIR与隔离cache/锁，不改HOME/home/CODEX_HOME，只用任务专用DS_TEST_RUN_ROOT、TMPDIR/CARGO_HOME/CARGO_TARGET_DIR。正式交付源码始终D/R/N/J，不能只tmp通过。source-inputs排除自身/P/A/build/downstream；delivery hash源+source-inputs；build/evidence索引按无环方向引用。A的raw种类沿r4 commands/stdout/stderr/events/wire/images/resources/processes/results/ABI/clock/build/cleanup/summary及逐成员inventory，增UI steps/DOM断言与SQLite前后hash/只读查询、schema/source-pin/cleanup-map。原DB原件只限owned合成profile，含私有内容则不进公开仓；公开P只紧凑事实/hash，不放raw日志/bin/运行DB。

验证网络只允许127.0.0.1:30102/30103作为A/B可配置样例，30104无listener负例，冲突socket复用A；Vite15194/preview14194仅对应实际需要的UI入口，串行角色前一run完全释放后再用。S7不开102/wildcard/外网，不扫端口/杀占用者/自动换口；执行前精确lsof冲突即fail/blocked，不把旧空快照当预约。普通产品用户可编辑loopback端口1–65535，低位端口实际权限不满足则start失败，不请求提权或回退。无新自动化listener，真实DAA client仅这两个owned端点，不打开DAA应用或SQLite。

### 5.3 未来构建与验证命令合同

所有命令仅在精确r5批准后由DEV/QA执行，当前PM未执行。产品普通入口为D下`pnpm tauri dev`，产品前端`pnpm build`，产品本机产物`pnpm tauri build --no-bundle --features native-s7`；不能把第三条专用构建成功当第一条已测。角色验证入口固定`/usr/bin/python3 -B <D>/scripts/run_validation.py --project-root <D绝对> --run-root <T5> --role <dev|qa> --suite <all|build|core|protocol|native|cleanup-check>`，裸入口帮助；suite只编排本spec列动作，无自动外部服务/端口选择。

Rust为`cargo fmt --manifest-path <R>/Cargo.toml --check`及`cargo test --offline --locked --manifest-path <R>/Cargo.toml --features native-s7,test-automation`，使用该role隔离CARGO_HOME/TARGET_DIR/TMPDIR；build.rs从正式N自动构建，无旧G0库变量。native UI测试build显式`pnpm exec tauri build --no-bundle --features native-s7,test-automation --config <T5>/profile/<role>/tauri.test.json`，再从该role实际记录的target产物启动`aiis-device-simulator --ds-test-manifest <该role场景manifest绝对路径>`；生成配置只替换测试identity/前端输出路径与beforeBuildCommand，由正式源构建，不装插件/签名/注册。.test.json在T5生成，不进入公开源。

`run_protocol.py --project-root <D> --run-root <T5> --role <role> --case <W01..X02>`使用该role新built ds-test-host/reference/真实DAA-client及已固定B0；Rust测试宿主显式读取测试workspace、required feature与owned marker，普通产品不含该入口。兼容client `cargo build --offline --locked --release --manifest-path <J>/compatibility/daa-client/Cargo.toml --no-default-features --features rust-snap7-driver`，不运行整个DAA/core或加载真实配置；J/protocol CMake只独立参考client，源来自N/V/upstream。每实际命令/路径/flags/feature/退出码/hash进入A5，锁解析只允许冻结bank子集。

## 6. 编号需求

R1–R21沿r4身份保留能力与逐项映射，产品范围/入口/验证方法变更明确由r5覆盖；原技术全文在附录A可恢复。R22–R29是本次产品增量。

### R1. 交付有功能的独立DS产品MVP

按§2/§3实现导入、SQLite配置/版本、控制和在线值，沿005承接，不再只有只读概览；保持有限S7与后续B/C边界。

### R2. 来源、构建和B0先闭合

精确source/deps/SDK/实际ABI/int传播/借用/预算/clock/二进制链接闭合后才协议运行；normal/native测试构建分别留SHA。旧r4 build只作历史，新增SQLite/native路径要重新证明，缺项blocked。

### R3. 真实写前拒写与有限native边界

保持原8文件控制点、Rust正确int callback；禁void高层S7Server/RegisterArea直写/事后补偿。系统dispatch/全PDU预算可控点缺失即停止，不借产品化重写栈。

### R4. 单owner和拒写证据

每instance一个Rustimage owner，静默/提交屏障下全触达DB bytes/hash/seq/point版本/时间不变+真实失败+无commit/恢复事件；并发按item/result及合法范围对账，不要求合法规则运行时全image hash冻结。

### R5. BOOL/typed/raw/item边界

按§3.1类型、大端/finite/全包及§7全部合法负例，每item原子、多item保序部分成功。非DB/CPU/clock/块/SZL等未列操作拒绝或关闭，无成功空操作/DS控制副作用。

### R6. 六写来源和普通/维护CAS

client/rule/UI/ui_maintenance/init/reset同入口，普通UI仅ui owner；维护默认关闭，仅client/none hold显式允许且revision/epoch/pointSeq CAS，rule暂停不让权。init/reset/apply安装只封gate维护，未提交拒绝与已提交未知分开。

### R7. 16会话与真实连接资源

默认C16/整数1–64（>16未验证）、H4/1–16、TCP=C+H；global128/32/160、实际全runtime≤64threads/1024handles。pre-accept reserve/握手晋升/closing到真join后归还，满额不抢占，MaxClients不能替代，拓扑不外推128吞吐。

### R8. 期限、整PDU和字节预算

握手5s/半frame2s/预commit2s/send首次尝试2s，idle踢出默认关；1执行+2等待/64KiB每conn、64PDU/1024items/1MiB每instance、256PDU/4MiB global、UI4/control8/tick1。整PDU预留Q与新实际副本/OS资源先计再item0；owner不等网络/SQL/日志，deadline不能滴流续命。

### R9. 逐item公平/规则合并/stop控制

protocol→rule→UI非空类轮转，protocol内连接RR每item让出、同PDU保序；tick最多1待并记录missed/coalesced。C05正常A/B各120请求及UI60成功，不能靠全拒低频绕过公平；stop及时封准入取消未入段，只完成当前不可取消item。

### R10. 真实ManagedS7模块互操作

字节冻结五模块+core、driver on/local-validation off、RemotePort/rack/slot/原connect/read/read_bounded/disconnect，两个端口240reads；新路径真实消费/dep-info核，不改DAA或用FixtureTransport代替，无DAA应用/SQLite联调。

### R11. 真释放、同进程保值与未知

正常close/stop≤2s、积压≤5s，Rust join/native pthread_join与callback归零后才释放/复绑，超时不假stopped；stop-start保值、reset分开、已提交ack丢失unknown不重试。单进程native崩溃可能波及全DS，不承诺实例OS崩溃隔离。

### R12. 可关联证据/完整分母/真实资源

source/build/run/instance/conn/item/result/epoch/seq/clock可联，offered/accepted/completed/rejected/timeout/unknown齐；1Hz资源与状态采样、逐连接分位数、rawitem/完整bytes/错误/关闭均留。日志介质降级不改已提交结果；缺证据不能pass，raw持久A5、公开P5仅五索引。

### R13. gate与状态不混同

精确r5批准→派生/正常入口与通用Rust/SQLite/core→B0→协议/产品/native自动矩阵→退役/受影响复核→DEV handoff→new fresh QA→Owner接受。pass/fail/blocked/not_run/deferred分开；X02无sidecar才N/A，必证不能defer。r4部分QA不继承为r5通过。

### R14. 角色和dirty保护

PM只spec，DEV只获批实现/任务事实，QA fresh context独立重建/验证写checklist；主协调机械索引；所有其它任务/旧证据不回滚不重写，不用角色名称宣称ACL。

### R15. 共享来源和命名唯一

固定core0.1.0/v1/accepted-source与新增DAA UI各自pin；直接消费六API，禁fork parser/name/oracle。完整NameBatch、来源hash/结构化路径/受限布局边界及真实DAA模块闭包可核。

### R16. canonical设计与产品差异

同一DS正文准确同步r5已批增量/实现与未验收面；§2限制/长负载/产品MVP与004全文区别清楚，不把旧文档接受当产品实施证据。

### R17. 正式源码和正常工程入口

有效实现落D/R/N/J，build入口无需tmp/G0环境，自动编译native、默认非stub；完整source→lock→binary→运行证据闭合，README/索引与实际结构一致。

### R18. 有限协议基线交接

DS-MVP-S7-v1含真实版本/source/构建启动、profile配置revision、端口/TSAP/DB布局/编码/权限、原19case+产品矩阵、限制/QA/Owner事实；未齐仍candidate。真实DAA–DS读取至SQLite另批，C排除。

### R19. Rust业务所有权与FFI

保留实际Rust runtime演进，C++只协议/IO/hooks/生命周期，无双image/规则；正确c_int/packedTag/同步borrow/稳定上下文/异常边界、callback0+真join后destroy。不得以Rust壳包装C++业务owner。

### R20. 完整适用DAA装配与身份隔离

按196源隔离暂存/明确适配，保留现成组件/图标/main/provider/theme/EP装配，剔除DAA业务；DS identifier/数据/偏好/IPC/端口独立，无DAA依赖运行。

### R21. 原件、时钟与历史诚实

完整r4/r3/r2/r1可逆保存、已成功三窗不抹；统一monotonic/100夹点/受影响复测，不把截断日志写成error或旧binary通过写新binary。

### R22. 新DS单SQLite schema/稳定身份/CAS

落实§3.2/profile锁/只初始化空库/来源版本与不可变revision/草稿CAS及容量。坏库/未知版本/忙/权限/commit未知有真实状态；无DAA迁移/采样/运行值存储/任意SQL。

### R23. 导入、手工建模和重导身份

落实§3.3多文件多DB/UDT闭包/稳定UUID/preview token/CAS及重导diff；未选对象保护，删除/结构变化确认失效，manual不伪造来源证明。

### R24. 地址覆盖、命名与应用就绪

完整树理论layout/STRING整DB拒推/手工依据保护、reserved/bit coverage、全instance NameBatch与pending准入；共享原v1期望验证真实DS消费者。

### R25. typed初值、层级策略和规则

落实§3.1/§3.5全类型/范围/编码/默认与explicit、instance→DB→region→point继承/唯一持续owner、5类规则/时钟/取整/seed及fixed无变化。UI不跑业务规则。

### R26. 停机apply/兼容保值/恢复

完整执行§3.4九行、控制代次/CAS/单selection事务、loaded失败/unknown/幂等/重开初始化stopped。无跨介质原子承诺、热apply或持久运行值。

### R27. 页面到真实DTO的可用闭环

6页面/8编辑或确认组件/连接日志，保存/应用/启停/普通维护写各显式权限/反馈，取消零写/失败保留输入；i18n/主题/分页/stale与实体ID一致，不用demo DTO。

### R28. 自动原生/风险集成验证

按§4非默认feature+显式owned manifest、真实DOM/IPC/Window.close生命周期、保存重开与资源三轮；协议测试不以人工窗前置、不拿TERM/mock证明，最终fresh QA独立复现。

### R29. 验证后G0清理与可恢复交付

按§9逐文件保留/迁移/退役，先有效产品验证+原字节持久封存+引用闭合，再删旧专用入口/依赖/脚本，清后必要复核；不删旧plans/失败史/必要A4或未知用户资源。

## 7. 保留的19个协议/并发/资源回归case

以下表格原行逐字来自r4，仅执行入口迁移为§4/§5的产品runtime测试宿主。W02 offset56 test-only未确认overlay、W09屏障撤除边界按附录A r4 §5原文；确定性向量各独立reset至少3轮，BOOL竞争100轮。DB41=1024/DB57=64、DSG0A001/DSG0B001 marker及原绝对point向量保持为**回归夹具**，不作产品默认/固定拓扑；完整typed/规则产品另§8验证。原19个case标识保留用于证据追溯，完成后不再交付G0产品CLI。

| Case / 需求 | 输入与动作 | 可判定预期与必须保存证据 |
| --- | --- | --- |
| W01 · R3/R4/R5 | 真实client向自己8B槽写两个完整DINT的非旧值，raw读回；再读64B marker。 | item成功、逐字节/typed值一致，唯一commit且seq+1；raw请求/回执/读回、owner trace及完整前后image。不能只看client函数无异常。 |
| W02 · R4/R5 | 静默屏障下依次向rule字段、reserved、越权bit、未确认coverage、未知DB写；未确认coverage固定采用本节DB41 offset56的test-only overlay及撤除边界。 | 每item真实失败；全部可能触达范围bytes/hash/点版本及全image/seq不变，拒绝前无commit/裸指针写，回调/dispatch顺序可复查。自动字段即使rules_paused仍拒绝。 |
| W03 · R5/R6 | byte0.bit0合法bit写；向同byte整byte写（含rule/reserved，即使相应值没变）；byte1两个不同client位由双连接同步竞争100轮；byte1合法整byte写。 | bit写只改mask、邻位保留；byte0整byte失败且不变；byte1两位更新均保留，无RMW丢失，合法整byte成功。保存各轮item/seq与目标byte前后，不拿不同并发顺序当失败。 |
| W04 · R4/R5/R8 | 部分INT/REAL、越过client槽末端触及reserved、末端1023+2、0长度、count溢出/transport单位不符/短payload、NaN/Inf REAL及超frame/PDU；合法大端有符号/有限REAL对照。 | 非法输入在提交前失败/无可编码item时关该连接；无越界/分配爆量/其他实例变化，合法typed值可读回。保存每向量原始长度/规范化触达、错误码、全范围bytes及预算变化；格式错误与权限item失败分开。 |
| W05 · R5 | STRING[8]写完整`08 03 41 42 43`加5零字节；STRING[254]完整256B对照；错误max头、actual>max、非ASCII、只写头/截断包/部分包。 | 合法包精确读回；其余整item失败、整个STRING包及全触达字段不变，不截断后报成功。保存原始包/布局、item返回、typed解码与hash。 |
| W06 · R4/R5/R9 | 单PDU顺序3items：合法8B、禁止rule写、合法STRING；其间允许另一已准入连接/规则插入，另做静默对照。 | 真实逐item成功/失败/成功、内部顺序保留，成功各提交一次，失败范围不变；无全PDU回滚/全成功伪造。保存原PDU/result数组与逐item调度/seq，混合结果按触达范围对账。 |
| W07 · R4/R6 | 六写来源各一合法及一非法/陈旧操作：rule对hold/paused/旧epoch，UI及维护CAS冲突，维护默认关和rule即使暂停，运行中init/reset；合法维护后client再次写。 | 全部进入同owner/maintenance模式；非法无commit，合法来源和seq正确。维护不改持续owner/初值、后续client可覆盖；reset仅stopped换epoch，stop-start保值。保存源入口调用图、每操作结果与revision/epoch/point seq，harness不等于UI。 |
| W08 · R3/R5 | 对owned server发非DB区、CPU start/stop、clock、块上传下载、非白名单SZL/未知功能各一请求。 | 明确协议拒绝或有界关闭，无image/DS状态/宿主时钟变化，不能以库默认成功空操作通过。记录dispatch白名单、原请求/结果/前后状态；若库自动处理无法阻止，候选no_go。 |
| W09 · R3/R4/R11 | 在precommit及不可取消提交段用确定harness屏障分别触发timeout/stop/close；另在commit后故意丢回执；复查callback指针引用/注销顺序。 | precommit取消不变；已入段item完成一次，后项取消，已提交丢ack为unknown且不自动重试；旧epoch不能触达新image。保存call/commit/return/close/join/释放时序、引用计数及wire可达结果；禁止释放仍使用buffer。注入屏障是实验工具，不可带入产品owner等待逻辑。 |

| Case / 需求 | 有界输入、次数/时长 | 判据及证据 |
| --- | --- | --- |
| C01 · R7/R8/R12 | 单实例16已建立S7 sessions；预热30s后300s。各连接1轮/s，每轮2请求、各1item：DB57读64B+自己DB41槽写8B；8规则=6动态+2fixed，100ms到期。 | 32请求/s=16读+16写，应用payload1152B/s；测量段共9600请求=4800读+4800写、345600B，不含协议头；每连接600请求。按offered全量核完成，非故意错误/错写/越权/BOOL丢更新=0；每连接p95≤100ms/p99≤250ms，排队p99≤100ms，规则missed≤1%（24000到期机会，动态/fixed分列，无变化fixed不虚增commit）。 |
| C02 · R7/R11 | C01的16会话仍读写时，第17个S7连接尝试20次，间隔100ms；再关闭一条并重连，重复close通知。 | 新来者被拒，不抢占/重置原16；关闭直到真释放才腾C/TCP，重连新ID。逐时C/H/TCP/closing/实际established及OS socket、原会话成功item、拒绝阶段/原因均对账，无负计数/重复归还。 |
| C03 · R7/R8 | 另有16已建立时保持4个未完成握手TCP，第5未完成握手尝试20次；随后半frame每500ms滴一byte；另一session idle30s后正常读。每种绝对期限试3次。 | C16/H4/TCP20不超，5th握手无额外持久对象；握手accept后≤5.5s、半frame首byte后≤2.5s完成关闭/清理（含≤0.5s观察裕量，不延长配置期限）。老会话继续；idle不误踢。保存时间起点、阶段、bytes/名额/句柄释放。 |
| C04 · R8/R9 | 单连接超协商in-flight及1执行/2等待边界；另用P0声明的小预算/确定reservation故障触发每连接、实例、全局输入+最大输出预留失败；恢复后重试。慢读peer的实际收/发socket buffer各≤16KiB，20次/s发256B读取且不消费响应，最多30s，须实际观察send阻塞。 | 超额完整PDU在第一item前失败/关该连接、无commit；所有阶段数量/bytes含预留不超实额，幂等归还。发生阻塞的该响应从首次发送尝试起≤2.5s关闭（2s配置期限加≤0.5s观察裕量，不从阻塞时重置），其他连接/规则/stop继续。若只触发队列拒绝而没观察send阻塞，该subcase仍not_run/blocked，不能算send期限pass；不能以注入替代所有真实socket证据。 |
| C05 · R9/R11/R12 | 同实例F/A/B3个活跃连接、其余13个idle：F20 PDU/s、每PDU4个64B read items，A/B各用C01每连接profile；8规则100ms、UI维护1次/s，持续60s。再用小预算制造积压并从及时通道stop，3次；恢复基准观察5s。 | F offered80items/s，A/B合4items/s，规则80次到期/s，UI1次/s；PDU数与item数分别计。正常60s段A/B各60轮=120请求全部按offered完成，60次合法UI维护均有成功结果，不得把低频工作拒于准入外绕过公平；F的完成/拒绝/超时单列。仅随后明确小预算故障积压段允许按真实结果计低频拒绝。按R9轮转/时限判，保存各连接/类资格、dispatch、等待/完成/拒绝、missed/coalesced和stop各阶段；F大PDU不独占、普通控制不饿死业务，过载stop≤5s，恢复队列回落。 |
| C06 · R7/R11 | 16条连接各10轮断开/重连，共160次；每轮含一次正常close、半关闭或异常之一，轮转+100–1000ms固定seed抖动；随后20次start-stop，每次建立16session并各读/写1次，stop后等10s采样。显式reset另3次。 | 正常close/stop≤2s、故意积压stop≤5s，所有owned listener/socket/callback/工作timer/队列PDU/item/bytes/输出预留回0；stopped保留image/值不算泄漏，reset独立初始化。停止后同owned端口可重新bind，无隐形worker/旧epoch写。保留完整cycle序列，不把10轮写成004 L4每连接100次。 |

| Case / 需求 | 输入与动作 | 预期与证据 |
| --- | --- | --- |
| D01 · R2/R10 | 两个owned非102端口、A/B各自固定called TSAP/rack/slot和不同DB marker；字节冻结的真实ManagedS7各持1会话，60s、每连接1轮/s，每轮读取两个DB各1次；参考client改变允许hold值后再DAA读取。 | 两模块累计240次真实db_read，连接复用，能按marker/bytes/变化值区分实例，RemotePort实值与COTP/S7协商、调用trace相符。提交源/feature/native摘要、raw字节/DAA结果及server connection ID；fixture/标签/截图不能替代。只证明模块级S7，不证明完整DAA采集或GUI。 |
| D02 · R7/R10 | 错rack/slot产生错误called TSAP、owned无listener端口、A参数误指B端口；每负例3次；另用owned冲突listener阻止A启动，重复start。 | 错TSAP明确失败，不能同端口隐式复用/接受任意身份；错端口不回退102/扫描其他地址；冲突只使后来A failed、占用者和B继续、无第二listener。每次记录真实COTP、RemotePort、失败阶段/错误与名额释放；若候选默认接受错TSAP，必须先取得可控adapter证据或判不满足。 |
| X01 · R4/R11 | A/B均在服务时只关闭A一条连接；另在W09屏障处stop A，B持续读；超时注入后再观察实际清理及同端口重绑。 | 关闭只影响指定对象；未提交取消/已入段完成/已提交丢ack未知分开，B不变。正常2s/故障5s，超时不报stopped；只有callback/socket/worker真实归零后才释放/重绑。保存进程/OS/库计数和owner事件关联。 |
| X02 · R2/R11 | 若选择sidecar/每实例进程：父管理harness正常退出、父异常终止、A子进程异常退出，各3次；同时观察B，随后新run重开。 | 正常有序stop；异常时≤5s无owned孤儿/残留listener，A子崩不误报clean且B继续；重开只初始化fixture、停机，不恢复旧连接/未知写。完整进程树/PID起止/退出码/socket证据。未选sidecar则明确not_applicable理由，不宣称该能力；进程内native硬崩风险单列，完整Tauri退出与三平台发布仍deferred。 |

原C06完整B0/趋势口径：依赖加载/image分配/sink与采样启动、无listener/连接的稳定stopped为基线，首轮热身后固定；每次stop10s transport/callback/工作timer/queue/reserve归0，线程句柄按项回B0；RSS≤B0+16MiB，最后5次中位数比最先5次≤8MiB，连续4组（每5次）严格增长且总增>8MiB失败。全核心平均CPU≤单核100%、RSS≤512MiB、线程64/句柄1024，C01净增16MiB。A16+B至多1、DAA各1，不是2×16/8×16容量；完整L1–L5不在此短程证明。

## 8. 产品新增验证矩阵与AC

每项DEV写真实命令/退出码/原证据，fresh QA独立按同源重建及新profile重现。测试SQL/源/客户端全部自有合成，不启动真实DAA或写真实用户profile。以下K01–K10是本r5增量回归组，不另建任务ID。

| 产品组 | 输入/动作和必证结果 |
| --- | --- |
| K01 正常派生/启动 | 重建源pin/196暂存/目标差异；普通pnpm tauri dev清除DS_G0_*且default native，owned空profile启动真实native/SQLite/IPC、0listener；build no-bundle；图标5同SHA/实际配置与主题locale/组件链接/DS身份核实，无DAA业务IPC/依赖。 |
| K02 配置库/身份 | 首次空profile v1/schema/hash/锁；两个进程争同profile失败，源/revision原字节保留；CAS并发一个成功一个conflict、unchanged不增；坏库/外来appID/未知version/异常WAL/空间不足/只读/事务前后failpoint/commit未知全部不自动删重建。用真实ownedSQLite，不mock成功。 |
| K03 core消费者/重导 | 原v1 names.db/udt/expected/oracle一次多DB、负/非零数组下界与UDT；增叶/删叶/改名/改类型/DB号/布局/同名UDT新version、unchanged和歧义lineage；确认前零写、确认后ID/invalidations正确、未选DB/其它instance保护；缺UDT/循环/未知/优化/多维/超预算阻apply。 |
| K04 地址/命名/手工 | 完整嵌套理论layout与原oracle；STRING整DB拒推；manual理由保护；末端/overflow/bit0–7/alias/reserved；全instance停用/manual/pending冲突、原字符串大小写规则、地址确认后同core兜底。新增manual DB/point真实保存，不能借manual绕过优化源证明。 |
| K05 全类型/规则/policy | 每支持类型min/0/max及错误边界、finiteREAL/ASCII/STRING1和254、BOOL邻位、encode/decode固定手写bytes；5规则t=0/两个周期/pause-resume/seed重现/取整/fixed不变seq；层级region/point覆盖、分割标量/冲突owner拒绝；默认初值/显式优先/TIA提示。 |
| K06 apply九场景 | §3.4九行各至少一正反例及混合结构+权限变更；controlGeneration快照竞态、旧epoch、保留编码失败/用户改initialize_all、selected提交前后/安装前后/ack丢失；already_loaded不换epoch/丢保留值，selected/loaded不同禁start，重开真实DB按selected全初始化stopped。 |
| K07 通用多实例/资源 | 手工配置非41/57至少3DB的A和不同DB/port的B，真实S7写/读并互不污染，A reset/stop/apply B继续；8实例/32DB/4096叶/64KiB边界无端口编译及+1拒绝；C/H有效域/预算同时约束，normal产品不是固定2实例。协议短程C01–06不缩。 |
| K08 UI/DTO | 实际native DOM做6页面导航/实例DB创建/多源选择分页/导入预览取消确认/地址命名/策略/保存apply/control/值普通维护CAS/单close/日志；每动作关联真实IPC/DTO/SQLite或owner读回，不只静态文本或直接服务调用。中英/明暗/窄窗/弹窗scope/取消dirty/stale错误/无bridge均真实断言。 |
| K09 原生自动保存重开退出 | §4 N1–N3自动driver，实际startup/build不同SHA清楚，保存重开/选中恢复/初值stopped、真实listener已start后的正常close/5s/PID/三端口/DB锁释放齐；普通入口不含test命令/driver，release非test binary拒测试参数；不拿旧人工三窗代替新产品结果。 |
| K10 日志/封存/退役 | stdout partial/failed与文件sink/轮转/环满丢弃可见、不重放commit/不封普通模拟；配置SQL失败单列；全部必要raw校SHA A5/P5索引/原r4关闭及失败史保存；清前迁移map/引用扫描、清后normaldev/build/核心/协议/原生受影响项通过，正式树无G0生产依赖。 |

| AC | 对应需求/验证 | 可核验通过条件（均待未来执行） |
| --- | --- | --- |
| AC1 | R1/R14/§1 | r5 draft/方向授权/精确审批分层，当前PM仅spec，完整旧历史和已有成功窗口事实真实，无r5实施/QA接受预填。 |
| AC2 | R2/R17/K01 | 真实正式source/lock/工具链/依赖与生成bin/dylib/hash/link/ABI/预算/100clock夹点闭合；B0先于协议，实际normaldev无需G0环境/native预构建。 |
| AC3 | R3/R13 | Snap7/8文件限定与正确int链不变，未列dispatch/潜在裸写受控；缺入口/需重写则blocked回PM，无写后恢复豁免。 |
| AC4 | R4/R5/W01 | 真item成功、唯一commit/seq与raw/typed读回相符。 |
| AC5 | R4/W02/W09 | 失败item在静默屏障下完整bytes/hash/seq/时间不变、调用链无commit/恢复，真正失败；并发按合法触达对账。 |
| AC6 | R6/W07 | 六来源同owner、普通/维护CAS/默认关闭/客户端后写/规则暂停不让权、init/reset停机/旧epoch实证。 |
| AC7 | R5/W03 | BOOL mask/100轮两bit竞争无丢更新、允许整byte与越权整byte拒绝均有原wire。 |
| AC8 | R5/R8/W04 | 部分标量/跨权限/边界/单位/count/短payload/REAL/frame等全负例真实失败且不变，无漏预算。 |
| AC9 | R5/W05 | STRING8/254完整包精确读回，头/ASCII/长度/截断/部分包负例全不变。 |
| AC10 | R3/R5/W06/W08 | 逐item成功/失败/成功保序与其他连接可交错，系统未列操作拒绝无副作用，不用成功空操作。 |
| AC11 | R7/C01/C02 | 16真实会话读写、第17条20次拒不抢占，C/H/TCP/closing/释放逐态/原成功对账，>16不外推。 |
| AC12 | R7/R8/C03/C04 | H满/5s/2s/idle30s/真实send阻塞与截止、实际SO和未读TCP分列、真实释放。 |
| AC13 | R8/C04 | 整PDU输入/描述符/实际copies/最大输出预留先于item0、三层故障准入与幂等归还；owner无IO等待，未触达大容量不伪称已满载。 |
| AC14 | R9/C05 | 正常60s A/B各120完成、UI60成功，逐类/逐连接RR轨迹及p99/分母/规则合并/stop恢复，不能全拒低频。 |
| AC15 | R10/D01 | 固定真实DAA5模块/core/driver/原RemotePort调用链240次db_read，正确TSAP/端口/marker/变化值，无DAA SQLite或fixture替代。 |
| AC16 | R7/R10/D02 | 错TSAP/空口/误端点/冲突/重复start有原始负例且不回退/抢占，B继续。 |
| AC17 | R4/R9/R11/W09/X01 | stop/close封准入、未入段取消、已入段仅一次/未知不重试，旧epoch不能污染，B持续读；超时不假stopped。 |
| AC18 | R7/R11/C06 | 原160重连/20启停/3reset/10s采样、socket/worker/callback/timer/queue/预留回B0和原RSS趋势/线程句柄阈值均实证。 |
| AC19 | R11/X02 | 无sidecar仅条件N/A与单进程硬崩风险清楚，不宣称崩溃隔离；共通close/stop/native退出不豁免。 |
| AC20 | R12/全矩阵 | 全source/item/原bytes/事件/错误/完整offered/逐连接分位数/1Hz资源/状态采样关联，短命null与未知项如实，证据缺口不得pass。 |
| AC21 | R13/R14 | 阶段pass与DEV/QA/Owner接受严格分层，新fresh QA独立重建/新profile全适用验证，旧QA部分结果不转整体验收。 |
| AC22 | R15/R20 | shared accepted/core/v1/5DAA源及新增15UI/196暂存pin分别可核，不扩大accepted61、无来源漂移/DAA改动/近似client。 |
| AC23 | R16/R23/K03 | canonical与实现多文件/UDT闭包/逐DB绑定/稳定UUID/重导/预算一致，不以DeclarationRef/DB号/数组下标作稳定身份。 |
| AC24 | R5/R15/R24/K04/K05 | 真core消费者/完整布局与命名/原v1 oracle、typed全类型/初值/ASCII/BOOL/STRING边界实证，不只是设计QA。 |
| AC25 | R6/R11/R26/K06 | saved/selected/loaded/单事务/九保值场景/幂等/未知与日志分层真实运行，UI状态与DB/owner一致，无热更新/持久值。 |
| AC26 | R2/R17/R19/§5 | 正式D/R/N/J/精确路径、native8文件/桥/锁/DAA真实path/构建启动与DEV/QA候选闭合，无tmp-only或旧G0binary替代。 |
| AC27 | R13/R18 | protocol基线含新产品profile/config revision/类型/限制/构建入口/全部证据；QA/Owner未齐candidate，DAAapp→SQLite/C仍排除。 |
| AC28 | R12/R14/R17/R29/K10 | raw逐SHA持久A5、P5仅5紧凑文件、P4/A4/失败史保护；临时/用户资源归属真实，无hash-only后删原件或公开raw。 |
| AC29 | R4/R6/R9/R19 | 新拓扑所有image/rule/CAS/fairness/control/budget仍Rust唯一owner，native/CU/SQLite无另一业务image/规则，调用图+tests+wire可核。 |
| AC30 | R3/R8/R11/R19 | 新C/Rust桥int0/37、Tag20/align1/offset、table大小版本/回调borrow/异常/真pthread_join+Rust join不降，移路径后独立ABI/时钟/实际buffer重证。 |
| AC31 | R20/R27/R28/K01/K08/K09 | 原人工三窗成功保留；本r5真实派生UI/普通入口/native自动3场景/真实IPC/保存重开/正常close与≤5s/无残留，不再要求Owner每次关闭，也不以TERM/IPC-only/旧binary替代。 |
| AC32 | R21/R29/K10 | r4完整spec/源180/inputs108/P4/必要DEV与QA原件、旧3层历史可逐SHA恢复；clock同源/100探针/影响复测可核，G0验证后退役且不丢证据。 |
| AC33 | R22/K02 | DS新空库初始化schema v1/appID/identity/PRAGMA/OS锁；第二进程/坏库/外来版本/异常WAL/路径拒绝，无自动覆盖或DAA迁入。 |
| AC34 | R22/K02 | 真SQLite CAS并发/immutable source-revision/unchanged和source dedup身份、容量/只读/失败/提交未知查询正确，SQL外owner/有界worker。 |
| AC35 | R23/K03 | 真实多DB/UDT/core v1消费者、重导新增/删除/改名/类型/闭包/unchanged及unselected保护和preview过期/CAS正确，原golden不变。 |
| AC36 | R24/K04 | 手工DB/point可保存与确认；full coverage/overlap/reserved/边界/STRING拒推/manual保护、全namespace命名/地址兜底/pending阻apply实证。 |
| AC37 | R25/K05 | 全支持类型min/max/默认/显式初值golden bytes，5规则确定性/两周期/取整/seed/暂停时钟/fixed无变化与层级owner冲突正确。 |
| AC38 | R26/K06 | 九保留场景及混合/影响清单确认、typed重编码/失败保旧、control generation竞态、already_loaded/重开selected初始化停止、selection安装各故障均有真实状态。 |
| AC39 | R1/R7/R17/K07 | 至少两instance/非41/57多DB的真实S7与隔离；8/32/4096/64KiB及+1边界编译通过/拒绝，不靠固定A/B G0数组或UI改名冒充通用拓扑。 |
| AC40 | R27/K08 | 六页面真实DOM→IPC→SQLite/owner结果覆盖配置/导入/策略/apply/control/值普通维护/单close/日志，取消零写/失败保输入/双语主题窄窗/分页stale正确。 |
| AC41 | R17/R20/K01 | normal pnpm tauri dev清G0键仍能构建/真native/SQLite/2及新增IPC、默认stopped/无自启；native缺失明确build错误不stub，profile可选和独立默认路径可核。 |
| AC42 | R28/K09 | test-automation非default+owned manifest双gate，测试脚本真实DOM/IPC和Window.close同正常生命周期，3自动场景/保存重开/5s清理完整；普通非test产品不存在test命令/driver/任意控制。 |
| AC43 | R12/R25/K10 | stdout partial/lost、file/rotation/memory ring丢弃降级可见，已提交成功不改失败/重放/全封写；SQL保存失败/unknown与runtime fault分别处理。 |
| AC44 | R29/K10 | 每旧G0文件/依赖/构建引用有keep-migrate-retire map，原字节已存A5/校inventory，产品必要验证后清理、清后入口/链接/受影响测试仍通过，无用户/DAA/旧plans误删。 |
| AC45 | R13/R18/R29 | 最终handoff清楚MVP已测/未测/长负载与平台deferred/rollback/清理保留项；checklist新fresh verdict与Owner最终接受未提前填，有限协议baseline不授权联合SQLite/C/发布。 |

## 9. G0清理顺序、风险和回退

“调整好之后清理”分三个先后边界：**第一次改源码前**把r4原字节闭集先持久A5并核inventory；然后DEV在正式产品路径完成/通过正常入口、核心/配置/导入/保留、协议和native必要验证；**其后**按以下闭集引用审计/退役，再重建并复测受影响项，交fresh QA的必须是清后正式候选。不是现在删除，也不是先删可复用runtime再重写。若未迁移测试仍是必要依赖，清理标未完成/blocked，不整目录删掉求零匹配。

| 原路径/引用 | 保留/迁移/退役及先决条件 |
| --- | --- |
| runtime/src/app/domain/services/infrastructure有效实现 | 保留原字节起点/逐差异演进通用拓扑；image/owner/queues/FFI/clock/logging/resource不作G0垃圾删除。 |
| g0/vendor、native/ds_g0_bridge.h/.cpp、CMake原受控target | 迁N/V+bridge ds_s7命名，保留8-file patch/许可/原上游SHA、ABI/链接/预算证明；旧位置所有消费改后才移除，不删有效native。 |
| g0/client、daa-harness、run_cases向量/采样/证据算法 | 仅必要测试能力迁J/protocol、J/compatibility和scripts/run_protocol.py等，真实DAA path重证；测试私有入口而非产品独立G0服务。 |
| g0/fixtures/g0的两个raw image/TSV/profile、prepare_data | 先按相同绝对布局/原bytes转换J/protocol-workspace、并以旧raw SHA+独立期望证明等价，再删除原专用模板/生成器；正式产品默认不含G0 marker/预配置。 |
| runtime/bin/ds-g0-server、ds-g0-abi-probe、commands/stdio、config/g0_profile及g0/native_abi_probe | 有用逻辑移正式服务/无端口FFI测试/限定ds-test-host；默认产品不编这些probe/CLI，功能等价测试通过后退役旧入口。 |
| g0/scripts五脚本及README pair、剩余G0空目录 | 构建/原生自动/协议/收证/核证迁scripts与J/readme；旧env/命令/引用扫描清零、源manifest更新后逐文件删除；仅自有已枚举空目录可rmdir，不递归rm其它资源。 |
| D/R/README/BUILD/设计/索引、Cargo/package/CMake引用 | 同步实际迁移路径/默认native、无DS_G0_*正常必需项/旧G0生产命令；历史spec/tasks/checklist原引文与P4路径不可为扫描清零改写。 |

开工前先持久到A5/r4-stop-snapshot：r4完整spec、最新r4 tasks/checklist与P4原五文件、正式D180源/108输入清单及**原字节**（只公开源，不复制依赖/bin/env/用户DB）、旧DEV/QA必要证据原件/现有A4 inventory引用。协调已逐SHA复制288项/3416737B到本轮base/r4-source-full/，manifest=r4-source-snapshot.json；这只是方便的临时输入，不能是以后删除G0唯一证据，DEV仍须先复制持久A5并核SHA再改源。A4原sealed raw/113-member r3 archive继续原位保留，核原SHA可访问，不以仅hash删除其raw。特别保存旧失败/blocked/checkpoint及三组成功窗口，历史结论不重写为pass。snapshot自排inventory并记录source/导出时间/非接受事实。先逐成员二次核SHA再退役；有缺失先blocked，不用新源重算expected消漂移。

| 主要风险 | 已纳入的限制和回退 |
| --- | --- |
| 产品范围明显大于G0；通用DB/规则/SQLite联动 | 按§10阶段串行，先纯配置编译/故障/单owner再UI，不借旧18DEV通过省产品验证。长容量/平台明确未测。新Revision精确审批后才实施。 |
| native扩展/FFI/库硬崩和版本许可 | 原8文件/ABI/预算/真join不放宽；当前r4局部DEV已证能力并非所有产品布局适用。遇栈重写/表外扩展回PM；单进程崩溃全DS风险保留，发布许可/跨平台另核。 |
| SQLite3.46.0与RAM安装/unknown | DELETE窄查询/普通表/无WAL、故障前后恢复实证；只初始化新库/未知不自动迁。不得宣称SQLite-RAM原子/硬件断电安全，selected已变而loaded失败按真实状态恢复。 |
| 自动native driver被误带普通入口 | 双gate/非default feature/固定script与manifest/无新增socket/任意执行；正常编译图与IPC表审计。真native环境失败如实blocked，不重启人工三窗循环来规避方案缺陷。 |
| DAA派生覆盖Rust或带入采集/真实配置 | 196源暂存不执行、闭合目标清单/对账，新旧同字节不重写；Rust/native保护，DAA/CU/core只读，不迁真实.env/profile/DB。 |
| G0清理不可恢复/引用尚在 | 先原字节A5/等价迁移+产品验证，再逐文件退役/清后检查；不清未知tmp/系统WebKit/真实用户profile。必要A4/A5保留到另批联合验收后主协调再复核。 |

回退只撤本r5拥有的实现delta：封新listener/完成不可取消item/真join，保存当前source与证据，再从A5闭集恢复旧源到受控候选，重建并明确恢复的是**未接受r4研究候选**，不是产品回滚已证明。配置回退只选择本schema可读的旧revision并按§3.4初始化，不降级打开用户新库/覆盖持久数据；恢复不了要stopped+备份/人工决定。无Git reset/他任务回滚/删除真实配置。临时build/stage/cache由协调在无运行/QA/后续依赖且原件已持久后按owned清单回收；不是QA自行清理，也不按路径前缀推定归属。

排除：真实DAA应用→DS→SQLite联合采集/整体验收B、阶段C/上传/Backend/API/SMA/CA、真实PLC/现场网络/生产DB、Modbus/完整CPU/响应状态机/任意脚本、跨进程运行值/后台守护/账户权限系统、L1–L5长期容量与8×16扩展、三平台安装器/签名/分发/系统注册/部署、Git refs/commit/push、外部消息/邮件。DS自有配置SQLite与自动验证profile属本MVP，不能误写成被联合SQLite排除。用户已跳过邮件，不发送。

## 10. 实施顺序、角色handoff与本轮自检

| 阶段 | 退出gate与后续角色 |
| --- | --- |
| PM本轮 | r5草案/完整历史/来源与允许面/AC/文档自检已交付，2026-10-21 Owner精确范围/风险批准已满足；当前移交Development。本次PM只登记事实，无新实现或QA。 |
| DEV 1 | 原件封存、DAA暂存/派生、默认正常入口/native自动构建、真实profile路径/空库初始化；无无关UI/库升级。 |
| DEV 2 | 通用Rust配置编译/单SQLite/CAS/core导入与手工编辑/规则/保值；纯内存/SQLite与无端口ABI/clock/预算B0通过再允许真实S7。 |
| DEV 3 | 真S7原19case+产品K组、UI/IPC/native自动N1–3、错误/资源；最终稳定source/locks/bin可核，失败保留原件和明确rework。 |
| DEV 4 | 迁移验证后G0逐项退役，清后normaldev/build/受影响核心/协议/native复核，P5五工件/源与证据/保留资源和限制→developer_handoff。 |
| 新fresh QA | 实际verification且fork_turns=none；读完整r5/tasks/实现diff/锁/P5/A，独立重建新profile与端口原19适用case/K01–K10/N1–N3，审清理/来源/UI、原件；只checklist verdict，不修实现/不清资源。 |
| Owner终验 | 精确r5 MVP/协议profile及已列限制/清理结果最终接受，之前candidate；协调依checklist机械状态同步并完成安全资源收尾。DAA–DS联合SQLite仍另批，C不开展。 |

适用skills：PM实际消费aiis/project-governance及rust-runtime/desktop-tauri/frontend-ui/i18n-workflow/plc-point-mapping，backend-arch仅取本地DB/DTO/分层概念，不把FastAPI/Alembic/命令Worker强搬进Rust本地SQLite。后续DEV同技术路由，新增源码/结构再code-document-indexer；plc-point-mapping通用XLSX/YAML SOP不替代用户已定DB/UDT+SQLite/core0.1.0/v1；不加载/启动Celery。串行角色+diff是合同控制，不宣称平台ACL/强制routing。

本轮来源/检查辅助在`/private/tmp/arch-aw-005-r5-correction-umza_thx/pm/`，关键事实与执行合同已在本spec，不以tmp独占权威。PM检查仅stdlib Markdown/本地link/anchor/表/围栏/29R→45AC覆盖/19case原行/算术、完整r4及嵌套历史恢复、源保护/本角色单spec delta；命令/退出码/receipt如实记录。不执行应用/安装/Cargo解析/构建/ABI/监听/协议/UI/SQLite/清理或后续角色工作。

实际PM文档自检：`/usr/bin/python3 -B /private/tmp/arch-aw-005-r5-correction-umza_thx/pm/check_spec.py`退出0；19项检查通过（15表、3本地链接/锚点、围栏/空白、29R/45AC覆盖、19case原行、算术/路径、r4/r3/r2/r1原文SHA、180source/108readonly/196DAA暂存输入保护）。1913文件起点中PM只认领本spec；checklist的实际QA行政补记与四根索引协调变化单列foreign/shared，未回退或认领。后续追加本摘要/精确命令后重跑同检查，最终spec指纹/结果固定在pm/receipt.json；这些仅文档自检，不能记作产品或独立QA通过。

### 10.1 精确r5批准登记（2026-10-21，Asia/Shanghai）

Human Owner在本轮明确批准**精确ARCH-AW-005 r5**，对应批准前草案SHA `e8e4462a6be3b0b23c4f28c074b0c7ab98cc61d51aed151b51fb8e5d34db2522`，逐字原话：

> 可以，批准 ARCH-AW-005 r5 spec。保留已有 Rust runtime，从 DAA 派生并复用现成 UI 和图标，修复 pnpm tauri dev，完成导入、配置、启停和运行值界面对接。按 spec 完成自动化验证和独立核验，验证后清理废弃 G0，不要再反复让我关窗口。DAA–DS SQLite 联调另批，阶段 C 暂不开展。

本次仅记录真实批准、Status/Handoff与当前执行gate，不修改已批准的29R、45AC、19case、allowlist、依赖/数值/风险或任何r4/r3/r2/r1历史。原草案阶段的PM-only、待批准及AC1中的draft审计措辞保留其当时时序；当前执行前提已由本次精确批准满足，不能据历史措辞阻断已批准Development，也不能将授权写成已实现/测试通过/QA或最终接受。DAA–DS应用读取至SQLite仍另批，阶段C不开展；邮件继续跳过。

Human Owner r5 direction: **authorized, 2026-10-21, exact quote §1**。

Human Owner exact ARCH-AW-005 r5 scope/execution/risks approval: **approved, 2026-10-21**，对应原草案SHA `e8e4462a6be3b0b23c4f28c074b0c7ab98cc61d51aed151b51fb8e5d34db2522`及本节逐字原话；以本次明确批准为依据，不从方向同意、旧r4或三窗证据推断。

At approval recording: r5 Development / new fresh-context Verification: **not_started**；r5 product / protocol-baseline final acceptance: **pending**。当前PM交已批准精确r5指纹/行政delta与保护检查后停写，唯一主协调串行启动Development；后续真实实施、自动验证、清理与独立verdict只由tasks/checklist如实记录，不提前填写通过或接受。

## 附录A. r4已批准与部分核验的完整原文（内含r3/r2/r1）

本附录仅历史，不授予当前r5执行许可；原状态/限制/链接为当时事实，当前范围只读上方active r5。外层原文可按标记逐字提取，SHA-256 4f1b03ec618bd0a40295bf273339538bc1491f8082380a009449f681ef56c2fc；包含全部旧批准/停点和嵌套历史，不以新r5结论覆盖。

<!-- BEGIN R4 EXACT SNAPSHOT -->
```````text
Task ID: ARCH-AW-005
Revision: r4
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved exact r4 on 2026-10-20; hand off to Development for DS design sync, minimal DAA-derived scaffold, Rust runtime with bounded Snap7 adapter and B0/G0, then new fresh-context Verification and Owner final acceptance; DAA–DS S7-to-SQLite separately gated, Stage C excluded
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA派生DS骨架、Rust唯一模拟runtime与有限native S7 adapter的G0；保留既有保护/16会话/公平/资源及可交接协议基线门槛
Owner: Automation World
Acceptance Chain Reference: r1 scope approved -> r2 unapproved -> r3 approved then stopped for Owner route correction -> Human Owner exact r4 approved 2026-10-20 -> Development scaffold/Rust B0/G0 -> new fresh-context Verification -> Human Owner final acceptance; DAA–DS S7-to-SQLite remains separate, Stage C excluded
Depends On: aiis-ics-arch::ARCH-AW-004 r2 accepted design; aiis-ics-arch::DAA-006 r3 accepted source manifest
Related Task: aiis-ics-arch::ARCH-AW-002; aiis-ics-arch::ARCH-AW-003; aiis-ics-arch::DAA-002; aiis-ics-arch::DAA-003; aiis-ics-arch::DAA-004; aiis-ics-arch::DAA-005

# DS Rust runtime、派生骨架与G0技术原型规格 r4

## 1. Owner路线纠正、r3停点与r4当前gate

2026-10-20（Asia/Shanghai），Human Owner先后明确：

> 搞什么，为什么ds是用cpp写的？你其实可以直接先复制daa过来，然后把不是ds需求的删掉就好了啊？

> s7服务端不能用rust实现吗？我想保存runtime用rust来搞，如果你引用的snap7库或者组件是c或者别的，这个我不关心。

按上下文“保存”指**保持runtime用Rust**。确定方向为从DAA的Tauri+Vue+Rust工程派生独立DS，复用适用工程基础、共享CU与已验收导入core；DS模拟业务runtime由Rust承载，底层协议库可为C/C++，不要求纯Rust重写S7栈。本r4草案将具体复制/剔除/新增、ABI、依赖和验证面提交Owner审阅；上述路线纠正在当时不是对尚未形成r4全部细节的批准。**精确r4现已获Owner批准，当前交接Development；本次PM仅登记批准事实，不执行实现/构建/监听。**

r3确曾获批：2026-10-20 Owner原话“可以，按独立 S7 PLC 模拟器定位。批准 ARCH-AW-005 r3 spec，接着同步 DS 详细设计，完成 G0 实现、验证和独立核验，形成可供联调的协议基线；DAA–DS 读取至 SQLite 联调另批，阶段 C 暂不开展。”批准草案SHA bd2df8339f904aec4744b6d0d254fa9becc2bdd0ac53a5e90c43447261341379；登记后r3 SHA `7ec38de52749257b61cc9eb23db25733cd52d0f82657efa8e88110c741012a81`。该完整原文及嵌套r2/r1在附录A逐字保留。r1原范围获批、r2始终未批准、r3批准后实际中止、r4草案随后获批各自成立，不互相转移。

**r3实际停点**：主协调2026-10-20 16:42 +08停点记录固定，正式g0目录99文件存在；原native/reference/真实DAA harness仅做过编译、无端口ABI与配置诊断，B0未closed，source-inputs/final manifests/P/A未完成；从未启动listener/协议，19case全not_run，无owned服务PID/端口。旧runner直接比较C++steady_clock与系统Python3.9 monotonic的原点缺口未解决；旧编译/ABI不证明Rust runtime、拒写、16会话或可联调server。Development随后仅行政追加tasks停点，读时Revision=r3/Status=revision_required，SHA `ccd40b68dc3f14aa95829493200ade87fb1450910853d4dda56355da6ac2bc98`；未重跑诊断/代码，PM不改其metadata凑r4。后续精确获批后DEV追加真实r4实施/中止承接。无r3 QA/终验。

本r4保留r3的18R/28AC能力门槛及**19个W/C/D/X case原行**，不降16会话、整PDU预留、逐item公平、BOOL/STRING、真实ManagedS7、pthread_join、offered分母、时长/阈值；新增R19–R21与AC29–AC32，具体约束Rust ownership/正确FFI、最小骨架/隔离及旧产物迁移/时钟校准。新增可构建启动的骨架，未新增完整产品页面、业务配置SQLite、导入消费者或D1–D4；G0 headless server与Tauri骨架共用同一Rust库，C01只测独立Rust server全树，骨架/WebView资源另记，不改变原负载合同。

| r3→r4的实质delta | 本精确r4已批准范围 / 保持项 |
| --- | --- |
| C++业务owner→Rust | R3/R4/R6/R9与R19固定Rust库承担原业务；6个旧业务源先持久归档再退役，native仍只八vendor扩展，不降写前/公平/stop门槛。 |
| FFI/探针 | 新2文件C bridge与Rust adapter/双向探针、异常/指针/clock门槛；保留原int失败传播和全部protocol case，旧无端口ABI不当新证明。 |
| DAA派生工程 | §2.8保留壳/构建/CU/core，剔除业务启动链；新增单概览/2只读IPC及native3次启动退出，产品配置/页面D1–D4仍排除。 |
| 精确源码/依赖 | §3.2增加D/src-tauri、R库/测试及骨架文件，原66client闭包单列；新runtime/Tauri仅冻结548 bank必要子图和原前端lock，无DAA/core修改。 |
| 测试入口/预算 | C++ server入口改Rust bin，19原case向量/时长/数字/分母不变；新增Rust节点/copy实额另计，C01同独立server tree，骨架资源单列。 |
| 证据/迁移 | 新T4/A4、旧99源/10诊断原件持久闭集、r3原批准/中止全文可恢复；不把中间构建写成Rust/协议/QA通过。 |

DS仍是AW工程归属的独立S7 PLC模拟器，无DAA/SMA/Backend运行依赖；其它兼容S7程序仅可消费后续经过G0/fresh QA/Owner接受的有限profile。DAA共享输入前置已解除，**技术上可在精确r4获批后开始迁移/B0；native候选仍未go**。DAA真实应用→SQLite联调另批/fresh QA/Owner才可能关闭整体B，C不开展。

2026-10-20（Asia/Shanghai），Human Owner明确批准**精确ARCH-AW-005 r4**，对应批准前草案SHA `bdd354dd9716a55289953d6d8cb3b46457877101d93550843aaaf250125fee4b`，逐字原话：

> 可以，批准 ARCH-AW-005 r4 spec。接着同步 DS 详细设计，从 DAA 派生精简工程，runtime 保持 Rust，底层使用 Snap7，完成 G0 实现、验证和独立核验，形成可供联调的协议基线；DAA–DS 读取至 SQLite 联调另批，阶段 C 暂不开展。

本次批准覆盖已形成的r4精确范围、执行面与风险，当前gate转实际Development；技术段落中“尚待Owner批准”“获批后”等草案阶段前提已由本次满足，B0/19case/独立QA/最终接受各gate仍按原合同串行，不改技术条款。批准登记时r4骨架/Rust构建/ABI/native启动/G0仍not_run，后续真实执行与独立核验以tasks/checklist为准；授权不等于已实现、通过或最终接受。原r3停止及r1/r2/r3历史保留；DAA–DS应用读取至SQLite另批，阶段C不开展。Owner本次明确跳过邮件，不发通知或重试。

## 2. 来源刷新、选型约束及整体设计增补

### 2.1 固定设计、已验收共享来源与读时事实

[004 spec](../ARCH-AW-004-ds-detailed-design/spec.md)、[tasks](../ARCH-AW-004-ds-detailed-design/tasks.md)和[接受记录](../ARCH-AW-004-ds-detailed-design/checklist.md#owner-acceptance-r2)保持原样。原004正文SHA `0eb3c149bf7093bbdce2f0b7a07af71e769fe24cb04a542c7f4dc43e6979eecb`仍是已验收历史；r3 Development已同步[同一DS正文](../../docs/AIIS_DS_Detailed_Design.md)，本轮读取SHA `d6379c0393939835f79fb340e2fa90d12979b46fdfcdba0abc87d40c4e7008f6`。当前正文含r3增补但未获本G0 QA/Owner接受，尤其C++ runtime方向已被本r4提案替换。PM此轮不改正文；r4批准后DEV仅同步§2.7–§2.9与Rust/G0骨架边界，明确005 r4来源，不重开004或倒记旧验收。

[DAA-006 accepted-source-manifest](../../automation-world/data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/evidence/accepted-source-manifest.json) SHA固定为`8d9d62457baa32aac8134df77773ea5cae23a0401e403ef1d4c267cdafc02ee7`；r4逐项只读核对为**60/61原字节匹配，1项CODE_INDEX.md导航元数据差异**：接受时SHA 971235e01214e1dc135d11b9ee575ed6a35764149881344d3dea35d538073837，当前读时SHA c5de00cb1cd3e419cfe810c4e48e1efb5e1079bf9e20f518fc54559fbefadaf9，为r3已允许的G0结构索引增补。manifest原61项仍是DAA006接受历史，不改其原指纹；CODE_INDEX不是本server编译输入，r4只许可§3已列DS导航同步并记录前后hash，其余60项及实际DAA/core/CU技术输入严格逐字固定，不自动采用latest技术源。本r4对61项复核须保留该例外对账，不再称当前61/61全匹配。它包含独立AC01–AC20 QA、另行DIRECT UI层和2026-10-20 Owner接受事实，各层不混称。本spec冻结**该清单的脏工作树文件**，不是HEAD/tag；其中HEAD `0af5b91177f3bca63f9f3c2bef9f14004ea49944`不能单独还原验收交付。源漂移即blocked并回PM，不自动采用latest DAA。

直接复用[共享core](../../automation-world/shared/tia-import-core/README.zh-CN.md)：aiis-tia-import-core **0.1.0 / Rust2021 / publish=false / std-only**，coreDeliveryManifest SHA `205f00ecf946246dfc7c2268eb60912733fb7fb1e52405e9174a5ea5996b1812`。六API为scan_sources、expand_db、layout_standard、plan_names、validate_manual_name、type_suffix；profiles固定tia-subset-v1、siemens-step7-v20-standard-word-v1、tia-point-name-v1，fixtures v1。不fork parser/命名/oracle，不复制DAA业务存储/ID/运行系统当共享能力。

| 固定共享输入（前缀automation-world/shared/tia-import-core/） | SHA-256与用途 |
| --- | --- |
| `Cargo.toml` / `Cargo.lock` | `a82f221d1d6baab2aa9bfb0c5cf084847768d0d5d34d747c912420d549bd5cb1` / `4ac1935bee10dde4638df61833f07d95008ae5853f8e630afc2019ee76769502`；无registry依赖。 |
| `src/lib.rs` / `src/model.rs` | `d69e0cabfec5c1cb98334fd3a3038d21c318a30687d155d8ade8f1d0e6fc5d5f` / `1347c9a2cb6ba102861229432f602ff7bebb4e83fc1e75cee387c901f24bca31`。 |
| `src/parser.rs` / `src/layout.rs` / `src/naming.rs` | `1513cef43324868f73a191c5b15cc4398ac0fc6fab400de516f95f7e0fa5a6e9` / `316ce3ae0c3511e12291dd460702cedfe403ec7e2120b4314dce0b6fe8bf793e` / `122ceb9b88fad2bb10ae495985fee3b6b4d5cc5ce3460b207d9c2ab26e968fe2`。 |
| `fixtures/names.db` / `fixtures/names.udt` | `769ebebc825bfa321de71a0a931012f5d6d0f1fe135da4b028cc6e9b78cf2586` / `8a5e470b2668f85aff8b7ba01c22c06b341ef044fbd4d31d1ec8e0f48ec02250`；共享导入样例Names28/60/47映射28/60/47。 |
| `fixtures/expected-v1.json` / `fixtures/daa005-layout-oracle.json` | `397fb68d8053f2adef41aa5a63cd8e53673e90174532a0def6db985aca913977` / `2f2f6fe79eea60b48357b72f8a4f352016da4c8d95220ba2e06005133c24e633`；[v1说明](../../automation-world/shared/tia-import-core/fixtures/README.zh-CN.md)，逐字固定，不用tested code再造期望。 |

**两套夹具分层**：上述v1用于未来D1的DS导入/命名消费者验收；G0继续使用§5的专门DB41/57权限、并发、资源合成夹具，不声称由v1导出。G0 Rust client因domain闭包链接core只是消费真实DAA模块的编译前提，不证明DS已实现六API导入。共享core不含初值、encode、存储/稳定ID/reimport/runtime；STRING解析可用但layout_standard遇STRING使整DB失败，不能跳过该叶继续推算。

宿主完整硬件/clang/CMake/SDK资料仍为r2的**2026-10-19历史快照**：macOS15.7.7(24G720)/arm64、Apple M4（proc 10:4:6/逻辑10）、RAM32GB、clang17.0.0、SDK26.1、CMake4.0.2/Make3.81、Python3.9.6；SSD/内核动态端口段未核。本轮2026-10-20 14:44 +08窄刷新：绝对stable rustc/cargo仍1.89.0、aarch64-apple-darwin/原commit未变，lsof三口exit1空输出，仅未观察LISTEN，不是预约/bind证明。执行前B0仍须复核工具链/完整资源和背景负载，冲突即失败，不自动换口。

### 2.2 精确候选、包来源、许可与推荐顺序

本节及§2.3/§2.4承接2026-10-19 r2的冻结源码研究；其中下载/403/cache等“本轮”指该次历史采集，r3/r4 PM未重复该官方包研究；r3后续仅有上述未闭合B0的编译/无端口诊断。固定包/ABI/八文件门槛保留，未来有效源码路径已改为§3正式S，不执行旧tmp源码方案。仍无已合格候选。

| 顺序 / 精确输入 | 只读证据与决定 | 后续边界 |
| --- | --- | --- |
| 首选试验候选：官方Snap7 **1.4.2** 源包 `snap7-full-1.4.2.7z`，20591252B，SHA `1f4270cde8684957770a10a1d311c226e670d9589c69841a9012e818f7b9f80e` | 本轮从[官方SourceForge包](https://sourceforge.net/projects/snap7/files/1.4.2/snap7-full-1.4.2.7z/download)只读下载，完整包SHA与发布页相符；只提取源码/许可为数据，未提取/加载发布二进制。选旧版的明确理由是能核到真实resourceless返回链且与DAA固定crate内关键native文件同字节；不是宣称它是最新版或已支持arm64。 | **原样版本no_go；有限扩展方案仅proposed_for_B0，尚非adopt/go**。只允许§2.4的server私有副本改动；先B0可编译/ABI及有限性审查，再P1。不能用源码下载成功当ABI/安全/性能通过。 |
| 至多一个备选：python-snap7 **3.2.1** sdist `python_snap7-3.2.1.tar.gz`，295424B，SHA `15748f8423e3726457f6c4d0202aabde4ad65f2b809c2c1e7ee4f2f776509c2b` | 本轮[PyPI元数据](https://pypi.org/pypi/python-snap7/3.2.1/json)与其sdist的SHA吻合；[版本化API](https://python-snap7.readthedocs.io/en/3.2.1/API/server.html#snap7.server.Server.set_rw_area_callback)及冻结源码均显示rw callback为stub。`_handle_write_area`直接改registered memory并构造单item成功，stop先报STOPPED再有限join/清列表；源码尚无本合同的多item/完整预算/释放保证。 | **该精确备选no_go，不进入构建或运行**。修成合格服务端需改写超出小adapter的处理面，本r4不授权。首选失败后无自动合格备选；回PM决定新Revision，不偷偷改Python/DAA或自研协议栈。 |

官方项目当前[1.4.3说明](https://sourceforge.net/projects/snap7/files/1.4.3/)指向[官方GitHub](https://github.com/davenardella/snap7)，其可变main/新版本不在本r4选用面；未来换版须新Revision。官方[resourceless](https://snap7.sourceforge.net/res_servers.html)、[server规格](https://snap7.sourceforge.net/snap7_server.html)与[API](https://snap7.sourceforge.net/snap7_api_ref.html)仅辅助说明；实际决策以本节冻结1.4.2源码为准。

许可材料：原生源头声明LGPL-3.0-or-later，包内`lgpl-3.0.txt` SHA `ea7d049c7705dc13afc202dd18e1827f3484f8212fd3fa7b82fc4a0c363432c9`、`gpl.txt` SHA `0b383d5a63da644f628d99c33976ea6487ed89aaa59f0b3257992deac1171e6b`；Python包LICENSE为MIT、SHA `3c88a113fc8ffbc81cf9f7fd8a4bd040f39ad1b88e099e8173eea1dc6df14544`。DAA所用rust-snap7包manifest声明MulanPSL-2.0（LICENSE SHA `89591a592b25a07a294c67c0767bb2b061a60e544d76f4bbc438192882f34e92`），其build.rs头另写GPL-3.0-or-later、native另有LGPL，B0保留全部原许可/源材料及链接清单，不据顶层单一license字段作分发许可结论。本G0仅owned本地实验，不发布/再分发。

以下为官方包内**必须保持原始起点指纹**的关键源码；整个包SHA固定其余文件，B0另生成全source manifest及有限patch的before/after/diff，不能只交这些摘要。`src/`以下路径相对`S/vendor/snap7-1.4.2/upstream/`。

| 相对原生路径 | SHA-256 |
| --- | --- |
| `src/core/s7_server.h` | `ebfe5f185c904624cc74b10419c454001c27b37a3ffbec7b0232ae2c494c1ecc` |
| `src/core/s7_server.cpp` | `e1007486fbf2c738e01628dd4e394de32af08a772227f3e3d07dc4437b128ad3` |
| `src/core/s7_types.h` | `feb97ffb241494f13db231e39fcb48a879efda74e7e240caddcb07139a92f300` |
| `src/core/s7_isotcp.h` | `313c5167f3769367b38073c62da6d1a1c49b63a7016016caf3743666639a2c5f` |
| `src/core/s7_isotcp.cpp` | `7c06fa33f0e34afe88962322c5fa946f3072ceeb1a0cc5d2cbdb71c7ac43e6b7` |
| `src/sys/snap_platform.h` | `d7f4e9dc2e5af523258437ae22c6109c98aa5b263881db16479fa5dfed884b47` |
| `src/sys/snap_msgsock.h` | `570f97d27da11dcc08650897a5dd27bc939a53598dc15d45c85b64366ca1e0c3` |
| `src/sys/snap_msgsock.cpp` | `bded0cc9e642aaff22b8a16e0bfae5f5eca7e346769ec6f8ba582b00bae9ba51` |
| `src/sys/snap_tcpsrvr.h` | `0a2d8d354b2d78a3155633b5e4bcd7b4f88937aa8ed7afe3a1d832995feafba4` |
| `src/sys/snap_tcpsrvr.cpp` | `b6365fddff816d4c3faf6b7d40c56e394e8ca0aa7c2bca16b3431d12d11eb747` |
| `src/lib/snap7_libmain.cpp` | `3e4a186471b41ead3a80e2d6ce94cec1e7ccc17920b6936a07ead14b274bd643` |
| `release/Wrappers/c-cpp/snap7.h` | `3e2a4edd86b5adfa4a73f64c81d0e0f1316df1da54785fa61dd293f728c4c401` |

Python关键文件`snap7/server/__init__.py` SHA `d17a8c1a5a9b96154d9882d3fc3766fb2c53c35af5f5b7c5aebf95b8f2c40e72`只作no_go证据，不是未来改动路径。

### 2.3 原生C ABI、提交时序与尚未通过项

冻结头`s7_server.h`定义`extern "C"`内的`int (S7API *)(void *usrPtr, int Sender, int Operation, PS7Tag PTag, void *pUsrData)`；macOS的`S7API`为空，按目标C调用约定，Windows分支`__stdcall`不在本次验证。`s7_types.h`在`#pragma pack(1)`内定义TS7Tag五个int：Area/DBNumber/Start/Size/WordLen；目标**待r4 B0复测（r3局部probe不替代新桥）**的sizeof(int)=4、Tag size20/align1、offset0/4/8/12/16、pointer8。OperationRead=0/Write=1。C++ adapter使用原native头；DS自己的Rust adapter按§2.9以extern "C"/c_int、正确TS7Tag packed布局消费**返回int**的callback，禁止复用返回void的高层S7Server。C++与Rust双探针比对，不符即blocked/no_go，不能调整期望掩盖ABI差异。

已核1.4.2源码链为`TIsoTcpWorker::ExecuteRecv -> TS7Worker::IsoPerformCommand -> PerformPDURequest -> PerformFunctionWrite -> WriteArea -> TSnap7Server::DoWriteArea -> OnRWArea(...) == 0`。resourceless下callback返回0才使WriteArea生成0xFF item成功，非0走`WA_NotFound/Code7ResItemNotAvailable` item失败；PerformFunctionWrite逐item填结果，再isoSendBuffer响应。**callback非0不能精确映射自定义权限错误细分码**，G0接受真实item失败而非假成功；W06仍要求逐item部分成功。read链使用DoReadArea/callback填worker响应stage再编码；RegisterArea路径会直接mask/memcpy共享区，G0必须禁止注册image/裸指针。events是在处理之后，不能当拒写入口。

Tag是callback栈对象，pUsrData为该worker的请求/响应buffer借用，均只在同步callback返回前有效；写数据必须在预算内复制成owner请求，不把Tag/原指针交给异步队列；读快照复制回原stage后才返回。usrPtr及hook上下文存活到所有callback归零且worker已join；异常不得跨C边界，失败返回非0，不能在commit后因日志失败改回失败。Sender来源是peer地址/ClientHandle，**不是连接唯一ID**；同loopback多连接必须用accept分配的connection ID、worker上下文及受控TLS item/PDU关联，不按IP或Sender授权/计数。

rust-snap7 **1.142.2**固定crate SHA `8c4d43b3a99825abd300d57a0888eda7b625b7cdbf56ee7766bd02331ac58243`已从现有cache完整包计算，与冻结DAA Cargo.lock checksum相同；关键native server/type/socket文件与官方包相同。其`src/server.rs` SHA `e46c5f1400e1e36a65dcfff9810e39f338cf959f85675145041225ae5dbd9ee2`中的FnMut/trampoline及`src/ffi.rs` SHA `3b64e4ea1aa470ad6f37e9672c070a96fb1f60bda76d964f6b1636e406a0f465`的pfn_RWAreaCallBack返回void，不能传回native所需int。**不采用该高层server、不在DAA依赖内修FFI**；该crate只用于原DAA真实client。crate缓存完整性与冻结项目锁相符，独立crates.io元数据获取403，未声称已获第二注册表证明或已可构建；该限制保留，B0仅可用匹配既有锁的包，不能联网换版本。

### 2.4 未修改上游的缺口及有限扩展提案

原样native虽有写前int链，但公开MaxClients只数TCP worker（0还代表无限），DoReadArea/DoWriteArea的全局CSRWHook包住callback；ISO连接默认回CC、S7协商原样echo AMQ，系统分支会处理CPU/clock/SZL等；SendPacket一次send/RecvPacket分段超时不能提供本合同绝对期限；TerminateAll超时会KillAll并清ClientsCount，Stop随后直接报stopped。因此**原样native no_go**，不能靠set_param/一个写callback进入P1。以下指r4 Rust bridge接入后需重新复核的有限扩展提案，尚未实施或证明足够；r3已存在99个正式源和未完成G0验证的八文件patch，保留研究事实，不把它当r4已通过。

未来只在`S/vendor/snap7-1.4.2/controlled/`修改表中八个原生文件；调用点附近增加guard/hook及server限定IO/生命周期修复，不改wire format、S7 item编解码或建立另一处理循环。全PDU descriptor/typed准入/公平在Rust runtime中完成，native原有解析/编码继续复用。**若实际需要迁移/替换ISO/S7主循环、修改本表外原生文件/DAA crate、重写TSnapThread框架或自行补完整协议栈，该候选停止no_go/blocked，回PM新Revision；不得以“adapter”称呼掩盖重构。**B0先出完整diff/调用图/控制点覆盖，未能证明有限性不得开始协议运行。

| 精确文件与原有函数/位置 | 最小必要改动及可审查结果 | B0/P1以后仍须证明 |
| --- | --- | --- |
| `src/core/s7_server.{h,cpp}`：TIsoTcpWorker::ExecuteRecv；TS7Worker::IsoPerformCommand/PerformPDURequest/PerformPDUUsrData/PerformFunctionNegotiate | 在原路径前加入受控server hooks：COTP CR的calling/called TSAP检查后才CC；S7 setup前C/H转换容量检查及AMQ=1、PDU≤480；只白名单setup/read/write及有界disconnect，其他系统分支拒绝/关闭且不调用原处理函数。 | 握手真实C提升时机、错TSAP、所有系统请求均到guard，不能以函数名称或CC已发当会话成功。 |
| 同两文件：TS7Worker::IsoPerformCommand/PerformFunctionRead/PerformFunctionWrite，TSnap7Server::DoReadArea/DoWriteArea | 第一item前对整个PDU做边界/最多4items/最坏响应检查与原子预留，再让原item循环调用hook；item上下文记录connection/PDU/index。仅G0受控resourceless分支不持CSRWHook等待owner；配置callback只在封闭gate，native非G0行为不变。 | 预留失败item0也未提交；逐item结果/内部顺序及跨连接公平；所有byte仍只由owner提交，callback解除外锁不制造并发image写。 |
| `src/core/s7_isotcp.{h,cpp}`：TIsoTcpSocket::isoRecvPDU/isoRecvFragment/IsoConfirmConnection/isoSendBuffer | 透传server限定的frame/PDU绝对deadline与剩余额度；每frame≤512、重组总量≤480，分片不重置起点；暴露完整COTP参数给guard，不另写ISO解析/确认循环。 | 畸形/滴流、多个fragment、输入预算及错TSAP；若必须重写这些函数的协议处理算法即越界停止。 |
| `src/sys/snap_msgsock.{h,cpp}`：TMsgSocket::SendPacket/RecvPacket/WaitForData及server上下文 | server专用有界部分send/recv循环，monotonic绝对期限、停止唤醒/非阻塞剩余等待，首byte/首次send尝试采样；socket buffers设定并读回。client/default分支不改。 | 真慢接收send阻塞、短IO、断连、首次发送2s deadline；不能只设置SO_RCVTIMEO/每次调用相对timeout。 |
| `src/sys/snap_tcpsrvr.{h,cpp}`：TMsgListenerThread::Execute，TCustomMsgServer::CanAccept/Incoming/CreateWorkerSocket/Delete/TerminateAll/Stop，TMsgWorkerThread构造/Execute | 在原listener现有loop的SckAccept之前先预留H/TCP及全局额度；accept失败/准入关闭/创建worker失败均归还一次，不重写loop；成功后分配唯一ID并转交Incoming。受控worker保持FreeOnTerminate=false，在Execute内同步记录本线程pthread_self；reaper等其完成通知后，以该ID执行真实pthread_join，返回后才销毁worker/socket/回调上下文和归还名额；新增字段/方法仅在本行已列两文件内。stop先封准入和cancel未提交，已入段单item完成，唤醒网络并有期限退出；受控分支禁KillAll/提前清零/无条件stopped。 | macOS原创建分支为joinable，但TSnapThread的WaitFor/Closed仅为状态等待，不能作为join或释放证明，不读取unix_threads.h私有th、不改线程框架。真实pthread_join返回后才归还；超时保留stopping/failed/closing及所有权，B继续；重复close幂等。无法在这八文件边界完成即B0阻断，不把断连event/移出表当线程已退出。 |

预留公式在此固定：对PDU p，`Q(p)=I(p)+D(p)+S(p)+K(p)+O(p)`；I为保留输入（≤480B），D为每item固定描述符（最多4×64B，无隐藏动态成员），S为typed stage（总≤480B），K为额外payload复制（总≤480B），O为最坏响应frame预留（≤512B，含失败码/填充，成功与失败取较大者），即每PDU显式池上限2208B，第一item前全额原子预留。若native实额要求额外副本/descriptor超64B，必须增加实际charge且仍满足原上限，不能沿用2208隐藏存储。每连接Bconn=未完frame实际capacity+native固定/临时protocol storage+Σ已预留Q+其他实际副本且≤64KiB；native源已有4096B IsoPayload和4096B Answer，不能只按协商480B计。socket实际SO_RCVBUF/SO_SNDBUF另作受限OS资源预留/观测并在C04均≤16KiB，线程stack另列RSS。实例/全局协议bytes分别汇总全部未完/执行/queued/待发阶段的实际buffer和输出预留（≤1MiB/4MiB），不能只计queued；等待数量另限64/256PDU、实例1024items；同一backing跨阶段只转归属一次，新增副本新增charge。活动native buffer、OS socket与等待池分类列账，不能互相漏记。B0必须以sizeof/capacity/调用点核表并给活动+等待合计峰值，协议阶段再按真实socket读回/阶段事件核对；超限即阻断，不伪造尚未发生的实测值。

Rust内存owner不能等待网络/磁盘；native worker等待Rust结果也不能持库global hook/list锁。每连接最多1个native执行PDU，可不启用额外等待PDU（上限2不是必须填满），OS未读bytes/socket buffer仍实计；不能用该实现选择减少r1 offered吞吐/公平目标。控制点缺失、预算无法观察或大范围改动都是阻断，不以测得最终值相同替代。

### 2.5 真实DAA新增编译闭包与实际消费路径

当前最小原字节模块闭包为以下**五文件+共享core crate**，不能保留r2“三文件足够”的结论。ManagedS7本身未改：RemotePort/PingTimeout/SendTimeout/RecvTimeout -> connect_to(host,rack,slot)；原read/read_bounded/disconnect/connected/Drop照用，driver开启/local-validation关闭/cfg(test)关闭，无FixtureTransport、截取Plc或近似重写client。

| 仓内只读源（前缀automation-world/data-acquisition-agent/src-tauri/） | SHA-256及真实新增边 |
| --- | --- |
| `src/infrastructure/managed_s7.rs` | `4ce9a9bfbe81c63453a6444d9b8e719fce6afa8e72ea84e0ca561dda8b48ca0e`；依赖local_configuration::{LocalResult,Plc}、rust_snap7。 |
| `src/domain/local_configuration.rs` | `af64ca7f52d336b096a4744dcf3f0398776204a0e86939eba1bbd8693e07d22d`；Db.import_binding引用source_import::ImportBinding，Point.name_mode/校验引用point_naming::NameMode与core::validate_manual_name，另调用local_sample::digest。 |
| `src/domain/local_sample.rs` | `a30a1909bd7b50ae26aa0cde27e9b193c82760ad7f940457107c31688f44f06a`；原serde/serde_json/sha2/chrono及local_configuration回边。 |
| `src/domain/source_import.rs` | `35f32c26eb3eb13e89c211354c6fdbfb9ecf94db379a8aef87138000f5b73654`；local_configuration/serde，ImportPreview又引用point_naming::NameChange。 |
| `src/domain/point_naming.rs` | `d60cab560b2f2047cc299b7ea62ba8b1978c754930af9d965aa444467332276b`；local_configuration/serde/std/aiis_tia_import_core，不依赖SQL/文件I/O。 |
| `Cargo.toml` / `Cargo.lock` | `6ca767c287b9118449027671684b3fd4dea5d4503d266d09a5d8cc22bd92c88e` / `0fd260eb50278b28e6b3a2e016dcc18ed6a4030b0c95a2a828db8ddcbfc05a61`；core path新边是实际依赖，不是仅更新hash。 |

正式G0 Rust入口位于`automation-world/device-simulator/g0/daa-harness/`。`src/main.rs`加载外部module domain/infrastructure；两个`src/{domain,infrastructure}/mod.rs`以外部`#[path]`直接消费上表仓内五文件，**不复制/编辑它们**。从domain/mod.rs到真实domain文件为`../../../../../data-acquisition-agent/src-tauri/src/domain/<上述四文件>.rs`；从infrastructure/mod.rs到ManagedS7为`../../../../../data-acquisition-agent/src-tauri/src/infrastructure/managed_s7.rs`。Cargo.toml的core依赖精确`version="=0.1.0", path="../../../shared/tia-import-core"`。B0须realpath核这些层数、原SHA及rustc dep-info；同crate pub(crate)可调用是原只读边界，r3已完成该client的局部build；r4仍须按新正式树/锁复核，不能据旧client build证明新Rust server/bridge。任何字段/私有API或新依赖不满足则blocked，不擅改DAA/core或用stub凑编译。

feature仍为`rust-snap7-driver=[dep:rust-snap7]`、default=[]，local-validation声明但关闭；只构建独立binary ds-g0-daa，不执行cargo test或整个DAA应用。不加载domain/mod.rs总入口或LocalRuntime/服务/store/SQLite/Tauri/上传/Backend模块。五模块闭包中的导入/命名DTO被编译不代表本任务执行DS导入。

真实连接参数固定A=127.0.0.1:30102/rack0/slot1，B=:30103/rack0/slot2；原native client默认PG=1、calling0x0100、called=(1<<8)+(rack*0x20)+slot，所以期望0x0101/0x0102，仍须wire核。connect_timeout=1000ms、io_timeout=500ms、deadline_ms=5000；D01每轮原read(57,0,64)及原read_bounded(41,512,8,400ms remaining)，后者设置remaining/2截1–500ms的原socket超时；两连接60s共240次db_read。仅显式内存Plc，不自动读配置/真实.env/default profile、不启动应用/建DB。进程白名单只传DS_G0_RUN_ROOT、TMPDIR、CARGO_HOME、CARGO_TARGET_DIR和必要PATH/locale/绝对工具链，不改HOME/CODEX_HOME；不包含业务授权/DB/Backend/上传变量或这些模块。

### 2.6 语言/依赖冻结及静态闭包限制

G0改为**Rust2021独立server+同一Rust runtime库的Tauri/Vue骨架**；C++17只保留冻结Snap7协议/IO/生命周期hooks、小C ABI bridge和独立reference client，无业务image/规则/公平队列。Python3.9.6 stdlib仍仅编排/数据/证据。C++依赖仅SDK libc++/libSystem/pthread与冻结Snap7；Rust runtime使用std线程/同步和下表锁定日志/序列化组件，不引入Tokio业务调度或第二owner。下面66registry集合仍只属于真实DAA client闭包，不能冒充新增runtime/Tauri工程全部依赖。

Rust六个registry直接根保持精确`=`：rust-snap7=1.142.2、serde=1.0.228(derive)、serde_json=1.0.150、uuid=1.23.3(v4)、sha2=0.10.9、chrono=0.4.45(default-features=false/clock)；新增path根aiis-tia-import-core=0.1.0。从**新锁**静态追踪得到66个registry+1个path package；66个registry的name/version/checksum与r2逐项相同，新增core无registry依赖。以下列完整精确registry集合，checksum由上述新锁SHA固定；这是r3前期静态清单而非当时已执行的feature图；r3随后真实DAA client局部build已成功、整体B0仍未闭合。该历史成功不证明r4新锁/Rust runtime/Tauri/bridge已构建或67包全实际链接，r4须重新核各自实际feature图。

| 静态闭包分组（全部名称+精确版本） |
| --- |
| aho-corasick=1.1.4；android_system_properties=0.1.5；anyhow=1.0.102；autocfg=1.5.1；block-buffer=0.10.4；bumpalo=3.20.3 |
| cc=1.2.65；cfg-if=1.0.4；chrono=0.4.45；const-oid=0.9.6；core-foundation-sys=0.8.7；cpufeatures=0.2.17 |
| crypto-common=0.1.7；digest=0.10.7；find-msvc-tools=0.1.9；futures-core=0.3.32；futures-io=0.3.32；futures-macro=0.3.32 |
| futures-sink=0.3.32；futures-task=0.3.32；futures-util=0.3.32；generic-array=0.14.7；getrandom=0.4.3；iana-time-zone=0.1.65 |
| iana-time-zone-haiku=0.1.2；itoa=1.0.18；js-sys=0.3.102；libc=0.2.186；libm=0.2.16；log=0.4.33 |
| memchr=2.8.2；num-traits=0.2.19；once_cell=1.21.4；pin-project-lite=0.2.17；proc-macro2=1.0.106；quote=1.0.46 |
| r-efi=6.0.0；regex=1.12.4；regex-automata=0.4.14；regex-syntax=0.8.11；rust-snap7=1.142.2；rustversion=1.0.22 |
| serde=1.0.228；serde_core=1.0.228；serde_derive=1.0.228；serde_json=1.0.150；sha2=0.10.9；shlex=2.0.1 |
| slab=0.4.12；subtle=2.6.1；syn=2.0.118；typenum=1.20.1；unicode-ident=1.0.24；uuid=1.23.3 |
| version_check=0.9.5；wasm-bindgen=0.2.125；wasm-bindgen-macro=0.2.125；wasm-bindgen-macro-support=0.2.125；wasm-bindgen-shared=0.2.125；windows-core=0.62.2 |
| windows-implement=0.60.2；windows-interface=0.59.3；windows-link=0.2.1；windows-result=0.4.1；windows-strings=0.5.1；zmij=1.0.21 |

rust-snap7原build.rs SHA `62aa125e5ecf01b3d2690bd3360b39aa83e525836d7f7d93bddff20b08ed00f7`，会以cc编包内native；其chrono默认features可能被统一，B0保留实际tree。未来只复制既有匹配包/索引到任务owned cache，离线派生**正式G0**Cargo.lock，允许条目仅此66 registry+该path core；新包/换版/MSRV/解析失败即blocked，不联网补包、不改DAA Cargo或共享cache。B0实际binary SHA、链接/ABI与正式树源manifest生成后方可运行协议；当前不编造产物digest。

### 2.7 DS整体设计刷新提案（仅设计，产品实现另批）

本节沿用r3的整体设计增补，承接canonical正文§2/§4/§6/§9/§10–11；r4仅更正Rust runtime/派生骨架及开工顺序。精确r4获批后Development同步**同一**docs/AIIS_DS_Detailed_Design.md的005增补及引用：标明r4取代C++业务runtime方向，不重写004接受事实。docs索引只改DS行，CODE_INDEX仅真实DS骨架/runtime/G0结构，无第二正文/新bundle。

**多文件/多DB和身份流程**：选择目标instance -> 读所选公开或用户授权的.db/.udt原UTF-8字节并建source lineage/version/hash -> scan_sources一次catalog枚举多个DATA_BLOCK/TYPE及诊断 -> 用户逐DB明确UDT DeclarationRef闭包 -> expand_db -> 每DB显式绑定(instance_id, memory_region_id, db_id, db_number, length) -> 地址/命名/初值/策略预览 -> 用户确认后仅保存候选revision -> stopped显式apply，start独立。memory_region为该DB唯一image区域，area=DB；policy_region是该DB内bit子区间，二者身份分开，不把一份DB隐式拆成别的端口/DB。

DeclarationRef(input_id,declaration_index)只在本catalog定位，**不是跨重导稳定ID**。DS持有稳定source_lineage_id、不可变source_version_id、DB lineage/db_id、point_id及结构化Field/Index叶身份，DB号/端口/文件名/文件序号均非主键。一个文件可有多DB，每DB独立目标/编号；同instance DB号唯一，UDT可被多个DB引用但各DB固定其source version闭包。重复原字节在同lineage/映射/闭包下为unchanged预览，不生成第二组ID或重复DB；相同内容但新lineage/同名声明有歧义时须显式选择，不能按序号、同名或hash自动合并。

重导入先preview/CAS（expected saved etag+输入hash/闭包+一次性token），显示新增/删除/类型/结构/地址/DB号和引用影响，confirm前不写。仅注释/显示变化且结构/类型/地址/effective policy一致可保留ID/DS初值和确认依据；结构化路径/类型/DB号/长度/地址改变取消受影响地址/初值/策略确认，旧初值仅候选，不强转/截断。移除项列受影响规则/策略，确认前不删；同名UDT新版本不污染仍绑定旧版的DB。运行中仅产生saved候选，禁止直接改变loaded布局，停止/资源释放后才能apply。

**地址与命名**：将004“flat-only、UDT/数组不推算”刷新为core当前支持的**完整非优化标准树**，可对受限嵌套STRUCT、无环UDT、一维常量数组（负/非零下界）调用layout_standard提供理论预览；优化/未知标准性、不完整/缺失/循环UDT/未知类型/多维或嵌套数组拒绝。STRING叶可解析，含STRING的**整个DB不推算**，全部地址需有明确人工依据，不跳过STRING猜其后地址。只选若干叶不能推整DB。实际LayoutPlan只返回leaves{path,byte,bit}与length；padding由DS完整coverage列为reserved，数组stride只能据已返回叶布局展示，不另造推算规则或声称API返回stride。始终由DS校边界/全bit coverage、保护人工地址并让用户显式确认模型/摘要/依据；ConfirmedAddress由消费者负责，不能把oracle或建议写成已确认/实际PLC地址。

core扫描预算≤128输入、单文件1MiB/批次4MiB、展开深度8/数组1024/4096叶；DS另外聚合检查既有每instance≤32DB/4096叶及最多8instance目标，不能每DB各4096累乘。DB长度1–65536、编号1–65535，BOOL位0–7、标量不得带bit、checked算术及末端边界，BOOL不同bit合法，任何同bit/标量别名重叠拒绝，padding reserved默认读零/禁写。

技术名统一调用plan_names，**每个instance一次完整NameBatch**，包含全部DB、未选/停用/legacy/手工保留名；只对可变选中项应用结果，不能逐DB分批逃过碰撞。用真实结构化segments，不拆sourcePath字符串；type_suffix/validate_manual_name保持core规则及1–100 ASCII bytes，名称冲突按core原字符串比较，不自行casefold。数组/非ASCII/扁平碰撞无法命名可pending，地址经DS确认后再由同core一次地址兜底，不造另一套拼名规则；pending不能作为可应用启用点。DS消费者要在D1用原v1样例/oracle及完整namespace碰撞、重导/身份case独立验收，不改expected来迎合实现。

**初值/编码**：core跳过:=和BEGIN赋值；常驻提示“仅结构，TIA初值未导入”。DS typed初值缺省BOOL=false、整数/REAL=0、CHAR=NUL、STRING空串（max=n/actual=0，其余零）；显式DS输入优先，未经类型/范围/用户确认不能apply。BYTE/USINT 0..255、WORD/UINT 0..65535、DWORD/UDINT 0..4294967295，INT -32768..32767、DINT -2147483648..2147483647；多字节大端，REAL为有限IEEE754 f32、转换溢出拒绝，BOOL只更新对应mask不写邻位。CHAR限ASCII单byte（NUL默认合法），STRING[1..254]全n+2包/max头/actual≤n/ASCII/确定零填充，拒WSTRING、非ASCII、截断/超长、部分包与部分多字节标量。类型黄金字节/roundtrip和错误路径由DS自己验证，DAA decode可作对读，sharedcore不含encode，Python参考不是已完成Rust/C++编解码。

**配置/值及恢复**：沿用004单DS SQLite配置、不可变saved revision、单事务CAS selected、进程内loaded和唯一image owner；保存不运行、不逐tick存运行值，无持久apply journal/样本库/outbox。core接受RETAIN/NON_RETAIN语法不等于DS跨进程保值，不能据TIA保留标记改变本节恢复合同。apply仅stopped且旧callback/连接释放：有界typed旧值快照 -> owner外构建/兼容影响清单 -> 用户确认 -> 控制代次/epoch/seq/CAS复核 -> SQLite选中 -> 安装新epoch -> 独立start。selected已提交但安装失败不能报事务回滚；selected/loaded不一致禁start；commit/ack未知查询事实不自动重试。同版selected+loaded内容一致重复apply为already_loaded，不换epoch/重初始化；reset独立。

| 场景 | 推荐默认及确认边界（承接004，非本G0实施） |
| --- | --- |
| 同进程stop→start | 保留所有当前值/规则模拟时间，连接重建；stop不是reset。 |
| 同布局仅显示/连接限额 | 停机apply；稳定点ID、DB/地址/类型/确认摘要/effective值语义全部兼容者可保留typed值，含规则值/时间；不恢复连接。 |
| 规则参数/seed/周期 | 兼容hold保留，全部规则点/统一时钟初始化t=0。 |
| 初值改变 | 受影响点按新初值，其它兼容hold保留，全部规则统一t=0。 |
| mode/owner/读写/维护权限改变 | 受影响点初始化，其它兼容hold保留，全部规则t=0，取消旧epoch积压。 |
| DB结构/号/长度/地址/类型/增删点 | 受影响DB整体初始化；其它DB仅严格兼容hold保留，新增初始化、删除丢弃，规则t=0；绝不旧bytes拷新布局。 |
| 显式reset | stopped确认丢值；当前loaded全部初始化、新epoch/规则t=0。 |
| 跨进程重开/崩溃恢复 | 按真实selected重新校验并全部初始化、stopped，无值/连接/运行意图持久恢复。 |
| 回旧revision | 默认全部初始化并确认；不从日志复活历史运行值。 |

混合变更按更严格影响合并，保留需稳定ID/确认布局/owner/类型/初值/权限一致；保留证明或typed编码失败则选中事务前失败，旧版/值保留，用户可明确改选初始化，不能静默丢值。单一配置DB保存失败仍保旧/明示失败；可选日志sink故障只告警+有界环/丢弃计数，不封全部模拟写、不将已提交成功改失败/回放。

**页面到服务的实际责任**：D3工作台显式start/pause/resume/stop/reset与连接单close；配置中心的实例、DB/点位、多源预览/重导、地址确认、全instance命名、typed初值/owner/规则、saved/selected/loaded及保留清单；在线值只显示当前image，普通UI仅ui-owner，client/none hold维护须显式默认关开关+revision/epoch/point seq CAS确认，规则暂停不让权，维护后client可覆盖。页面刷新/筛选/导入预览不bind或写运行值；保存只持久草稿，apply后仍stopped。Tauri commands只解析DTO/意图并调用Rust应用服务；共享core负责纯导入/布局/名，存储/实例控制/策略编译由DS服务负责。协议adapter、规则/UI/init/reset必须进入同一个runtime image owner，不能Rust一份image+C++裸共享区另一份。

确定DS业务runtime使用Rust：DS/runtime库唯一承载image、policy/CAS、六写来源、规则时钟、队列/逐item公平、C/H/TCP/bytes预算、stop/close与资源状态。Tauri薄IPC与G0独立Rust入口复用该库，native仅协议/IO/线程释放adapter，不能Rust包一层仍由C++拥有业务。本G0采用同进程C ABI，未选sidecar；Rust server承载A/B独立owner，native硬崩仍可波及两者，不把Rust语言或逻辑实例等同内存/进程隔离。任何未来sidecar选型另spec，X02条件N/A不免共通资源证据。main/lib只装配，UI不跑规则时钟。

开工顺序：r4精确批准→持久归档r3停点→DAA派生最小骨架/设计更正→Rust owner+native bridge及B0/时钟→骨架构建启动→G0 P1/P2/P3→fresh QA/Owner。骨架不等于D3完整产品；core消费者/SQLite配置D1、完整产品运行D2、管理页D3与长负载D4各另spec，既有设计目标不作为已实施。有限native控制点失败仍no_go/blocked回PM，不以改C++业务owner或补全协议栈绕过。

### 2.8 DAA派生骨架、保留/剔除及新增依赖

“复制DAA再删减”采取**固定源白名单派生**：目标D=`automation-world/device-simulator/`，不从已安装app/dist/node_modules/target复制，不覆盖DAA或把其真实.env/profile/SQLite/历史带入DS。下面37个DAA输入按当前脏工作树原字节冻结；其中无需修改的构建/图标可原字节复制，其它按下表明确改名/剔除，不能把继承业务入口暂留可执行。inventory算法为按完整仓内path排序的`path<TAB>sha256<LF>`，37文件digest `55e84aef4f28029da474c2eecb9e29a8e463e8e92564d4c79b31920bf4c75cac`；这不是HEAD/tag或DAA整产品复制许可。

| 相对DAA源路径 | 原SHA-256 |
| --- | --- |
| `package.json` | `3b14096b606fe9bc893175ea962c188e3aa6257d9a43dbfaad5b76cb1bbe085f` |
| `pnpm-lock.yaml` | `0417e47e58e19974d9bde4f3866164e88ffe1c1c22eb2ade356e48f12464d44c` |
| `pnpm-workspace.yaml` | `67911a16c29fe89e70d7417448cd2339a8ae81b176b7d9c39aed31421bf3b1ce` |
| `index.html` | `8b1580fec7014d2ad0d4acc1d2c73fa961d88cef7f03b2cd3a3732c72126149d` |
| `vite.config.ts` | `232167229353e2848c17258405d9b47bae8fb76d7bd42c5c33db1569bd61479e` |
| `tsconfig.json` | `58e692e4591675f7d020c32602b34569714c82ea8495f5345a01142587c35fc6` |
| `tsconfig.node.json` | `6b995c799112bf9561f0fe0005b594943a03e1a36b1deabc64d050c2929b8d66` |
| `src/main.ts` | `0cd19b1406e9b82e8ee064d3f4f6811c4b980c22ab665577a2aa1bee8cee9d2b` |
| `src/App.vue` | `4284d71a05828f6f24c275404250eb3233a7636b9b04a49cc53648235c54fba8` |
| `src/env.d.ts` | `f42866b149a18e230423934fbbfd2c36d166295b8a25146bf112650667e9d47b` |
| `src/styles/app.css` | `9e40bd8265c486b2c3ace07776b2bdbeb53a0e567e39066fb183efe402000a62` |
| `src/layouts/AgentLayout.vue` | `b8c95fb0a31b78edebc030144a1e028d5bf98e627c57621e1829809245780a94` |
| `src/components/shell/AgentSidebar.vue` | `afb9ebbeb8fd63cec3ce57b80c042b36f2558b2b8881e0e44bd92e6f083e2d1a` |
| `src/components/shell/AgentTopbar.vue` | `ba1e48cfdb34acebc6b2e406fc2192e245a7efdded534b68749753df76456aab` |
| `src/components/shell/RuntimeStatusCapsule.vue` | `0ef573b2cb93755c5859721b1c0ac3e57a5c4ef3dd7ecae23c38b9b5429b8b64` |
| `src/console/composables/useAgentConsoleShell.ts` | `03d7db8a36aacbb0933e3abfc6e5db17146471b854516b0f834814a23c926114` |
| `src/console/composables/useAgentLocale.ts` | `08da73ce3616ebb02e3c800b039640184216250449ee14c9c92eba88ab2a473b` |
| `src/console/composables/useAgentTheme.ts` | `8b6291e2bb607237213f24ab2cb9a2aadcd93f8cfe0485ba4b52893336dc6633` |
| `src/console/sections.ts` | `cd79f0d18d4a6fba0c6a09efe6967e980174d185fb525d6a4611049a53a49c71` |
| `src/console/types.ts` | `27b1395813a07c93d1711ef64cfeb35a6f103618f2963d2b42d185c52306f404` |
| `src/locales/index.ts` | `918151963c40710ab1de68a86e86b05ea6d0dbc9a62d1d575f7c9211f44d6c37` |
| `src/locales/en-US/common.json` | `3a93a3540629e938fa5127a02d7bcae25c6ea9ec499ee4940fe93797e1d52ff1` |
| `src/locales/zh-CN/common.json` | `828b8f39e48ec74c0d14578f9abda2fc1f2d39fbc9e80392eb5115c8ef2a1249` |
| `src/locales/en-US/navigation.json` | `cfae2e6f8ce0cf39eeb7752f39bef3091f422b57ed6ebc335d2806306c346c74` |
| `src/locales/zh-CN/navigation.json` | `10840adf1a3db01aa4298f5e057d6c74cdb03bfb22ecaeb5eba7736ec48da303` |
| `src-tauri/Cargo.toml` | `6ca767c287b9118449027671684b3fd4dea5d4503d266d09a5d8cc22bd92c88e` |
| `src-tauri/Cargo.lock` | `0fd260eb50278b28e6b3a2e016dcc18ed6a4030b0c95a2a828db8ddcbfc05a61` |
| `src-tauri/build.rs` | `065679b5d19d0da3b7fe8375841f95fc6fa777223f62d3a9ce2ffe60a084233b` |
| `src-tauri/tauri.conf.json` | `671d82938af01841032a667629316ecb4f8e8b5f42aaf0143fd81ef48397689f` |
| `src-tauri/capabilities/default.json` | `f41d131054632cf41229cd5b2bc546811f94ed6eccc983ca5fd7e1a12481a02c` |
| `src-tauri/src/main.rs` | `a973ae0ad26220e03d26d20e5e8fc4ef891857e0005eaf80b0a84e7be97b88c5` |
| `src-tauri/src/lib.rs` | `42685d3265a3e8439990a1907f041d8ce5f820ee54ef4a0a69ff3fd32f4906b7` |
| `src-tauri/icons/32x32.png` | `8aba00b65669faa01f4d12d9e4b52d51515ec8d05a0b16173e55760bc2e99ef7` |
| `src-tauri/icons/128x128.png` | `694c289092da1f5492e253d788c46c4a841471a8ed0a71ed97857f8eda91f4df` |
| `src-tauri/icons/128x128@2x.png` | `7765ee5cd8918def7301b968b0bd5ecf96dfcd9adb4cfcafc54ff38aaf4266e6` |
| `src-tauri/icons/icon.icns` | `a39a873617794f6e2ef478ce9a807f87a28bd5d2d7cf40c4e11f2abff1c43bac` |
| `src-tauri/icons/icon.ico` | `ef844f046ac649f05e146ea9153bbb9d6da53aae3d4b3823696f4db6a28af2ff` |

| 派生决定 | 精确目标/变更和明确剔除 |
| --- | --- |
| 保留工程基础 | D的package.json/pnpm-lock.yaml/pnpm-workspace.yaml、index.html、vite.config.ts、tsconfig.json/tsconfig.node.json、src/env.d.ts和src-tauri构建基础源自上表。只调整DS名称/脚本、dev/preview端口、目标产物路径/alias、薄DS入口与依赖；不迁入DAA旧命令别名。pnpm锁原依赖包不升级。 |
| 保留CU壳能力 | 派生src/layouts/AgentLayout.vue、components/shell的AgentSidebar/AgentTopbar/RuntimeStatusCapsule、console/composables的useAgentConsoleShell/useAgentLocale/useAgentTheme、console/types.ts/sections.ts及src/styles/app.css；只删DAA状态/四页导航/反馈ID、换DS键和单一G0概览。CU原公共入口/样式直接引用，不fork组件或CU参数页。 |
| 重写薄宿主 | D/src/App.vue、main.ts、locales/index.ts及四个common/navigation JSON只留骨架启动/状态/语言主题/刷新/错误；新增services/deviceSimulator.ts、console/composables/useDeviceSimulator.ts、app/simulator/manifest.ts、app/simulator/views/overview/index.vue及app/simulator/locales/{en-US,zh-CN}.json。无配置编辑、导入、采集、样本历史、上传菜单或伪数据。浏览器无桥显示unavailable，不模拟Rust成功。 |
| 剔除DAA业务源码 | 不复制DAA src/app/{collection,plc,runtime,gates}/、services/localAcquisition.ts、useLocalAcquisitionConsole.ts、components/console/**、components/common/MetricGrid.vue、vite.validation.config.ts、config/*.yaml、.env/example业务内容、任何DAA tests/plans/gen输出；选中壳的import/locale须同步收窄，不能留下可触发采集/IPC的死引用。 |
| 剔除DAA native业务 | 只借用main/lib/build/Cargo/config的结构；不复制其commands/config/domain/infrastructure/services模块、bin目录、DB/store/migration/collector/authorization/client/logging实现或测试。尤其local_recovery::open、prepare_runtime、daa_* IPC、--ca-*入口、自动DB发现/连接/上传不注册不编译。真实ManagedS7五模块仅保留在独立S/daa-harness外部path，不能进入DS产品server。 |
| 重写DS薄Rust壳 | D/src-tauri/src/main.rs/lib.rs/app.rs、commands/{mod.rs,runtime.rs}、config/{mod.rs,bootstrap.rs}。只注册ds_get_bootstrap/ds_get_runtime_snapshot两个只读IPC，持有同一runtime库的停止态实例，无UI写入口/自动start；ExitRequested/Exit走runtime shutdown/join。 |
| 保留共享导入核心 | core0.1.0、六API/profile/v1原pin不变；D/src-tauri/Cargo.toml用`path="../../shared/tia-import-core",version="=0.1.0"`，不是复制parser/DTO/SQLite消费者。G0合成DB与未来D1共享样例消费仍分层，链接依赖不算导入已实现。 |
| 应用/数据隔离 | package与binary=aiis-device-simulator，Rust lib=aiis_device_simulator_lib，productName/window/title=AIIS Device Simulator，identifier=com.aiis.aw.devicesimulator，pref=ds.theme/ds.locale，feedback容器ds-feedback。Vite dev15194/preview14194、strictPort/envDir:false，无DAA/SMA/CA数据迁移。5枚原AIIS通用图标固定复制，不新增产品logo设计。 |
| G0路径和安全 | 本G0 native启动必须显式绝对DS_PROFILE_DIR与DS_G0_PROFILE_JSON及owned marker，不读真实.env/DAA_PROFILE_DIR/业务DB；只在自有profile写日志。Tauri独立identifier隔离WebView本机目录，记录实际路径与可逆清理归属；WebView内部缓存不等于DS配置SQLite。当前无DS/DAA业务SQLite。源码.env.example仅说明进程/CLI键及空/关闭默认，不承诺本阶段读取.env。 |

CU复用的闭集为当前`automation-world/console-ui/src/ui/`以下17文件，aggregate digest `062406ddb19f99d6485a7ee953bc1f8e9e85d752b6d1db961c637713e96a090d`（同inventory算法）。全部只读，DS/CU既有身份独立：

| 相对CU src/ui路径 | SHA-256 |
| --- | --- |
| `components/AgentLayout.vue` | `177f6fe8e009c73fb08a629929ea5260dcffc6bb2210b8acde6ab70941ec85b9` |
| `components/AgentSidebar.vue` | `b53495b30e589aed06ba51b470c582fcc1d7984a590c9b0d811e9bb0de629533` |
| `components/AgentTopbar.vue` | `25b334b9c88b223d1bd069407f13a517db9cac04527b01bcc15f06c2903f9157` |
| `components/ConsoleActionButton.vue` | `7ec106be7d3e3789fcd93e966a5a25bfb1c58e528ca51f3556cf04daf46b7fdb` |
| `components/ConsoleCard.vue` | `54e2ce46d726e0eb424aacd5f28df3d5921e5f61a81b0c799ccfac4ddcabf3b4` |
| `components/LanguageSwitch.vue` | `e36844e9f693eb6527e76603e6b6d04e8f93f2c3ccabf9013f6b831a99f8c5a1` |
| `components/StatusCapsule.vue` | `62e605544f911759b6134482c9c251575fd24a9505d8dd1e336a8b62262439ed` |
| `components/ThemeToggle.vue` | `a7429753eee5abb9b8cc04b4a201f4230004c236176ff49bc8c378d73c95c1a2` |
| `design-profile.d.ts` | `b21ba90f57fa92e98c61bed14e3922eacb12c167c53c96049dccc95c69f828cf` |
| `design-profile.js` | `c36901caa5048df7f6a94fe26cabeec7ea9e527a98ca9c84ebd203d426f4f2c0` |
| `index.ts` | `38dcc6404c84144a8da84fc1fc3985f028e1335443261ce68a3a487f798b39b7` |
| `styles/components.css` | `734cd1402a71ffe1e3500c128d392c38bcdf8404bc1d008e8098b06268206fbb` |
| `styles/design-profile.generated.css` | `ac270f6c0658fe400d356497727bfae865472cdb307d6fb28234cda8c1fb70f2` |
| `styles/design-profile.json` | `9591913678f8fd22d6455456c63c8697df68d1210d926475ad4f6271c8d96bf3` |
| `styles/index.css` | `4d7113c32d88e12e85a598076eb608e395ef578e5417aeccbe351d4b0e6acdc5` |
| `styles/theme.css` | `1c631f285a29f98db9778644c4e95f7311ca1c9ea7bc65b1a62160769914a160` |
| `types.ts` | `b0ea3bd1e8d31e4cf26b2068fde4d8199dcf82e23d2112d29db34187b50ae18f` |

**依赖分层**：原66registry+core只约束S/daa-harness。新增DS runtime的直接registry固定serde=1.0.228(derive)、serde_json=1.0.150、sha2=0.10.9、libc=0.2.186、tracing=0.1.44、tracing-subscriber=0.3.23(env-filter/fmt/json)、tracing-appender=0.2.5；std线程/Mutex/Condvar/有限容器自行落实既有调度，不引入通用actor/消息库。D/src-tauri直接tauri=2.11.3、serde=1.0.228，build-dep tauri-build=2.6.3，path ds-runtime=0.1.0（../runtime）及上述core。runtime/build.rs只链接显式冻结native库，无cc/cmake Cargo包/下载动作；tauri build.rs只Tauri metadata与明确rpath。

从DAA Cargo移除dirs、serde_yaml、sea-orm及所有sqlx-mysql/runtime-tokio业务feature、rusqlite、uuid、fs2、rust-snap7-driver/local-validation等DS不需直接依赖。transitive若Tauri/平台本身仍需同名包如Tokio/uuid，不把“移除直接业务依赖”误报所有传递包不存在；须按实际feature图证明无DAA/store/collector启动边。S/daa-harness独立仍保留原六根含rust-snap7，绝不复用其void callback server。

新增runtime/desktop锁以冻结DAA Cargo.lock的**548个registry精确name/version/checksum**为只读候选库，集合digest `cca1d6efbbdd7767a2475f786bf5a67fa64056bca17bff66d4113d4f40615cfa`（按name/version排序的三列TSV/LF）；B0从上述精确根静态审查后离线解析、交付各自正式Cargo.lock及实际feature图，必须是该冻结集合的所需子集，路径包仅DS/core。不得为解MSRV/缓存缺包升级或新增集合外版本；不闭合即blocked回PM。此刻只是读锁/源码，未运行Cargo解析/构建；旧66集合不再代表新增Tauri图。

feature固定：R的default=[]、native-s7=[]，关闭时只能纯内存测试/停止态，不创建native server；D/src-tauri的default=[]、native-s7=["ds-runtime/native-s7"]。本r4 headless G0及native骨架都显式开启native-s7并复用同R库，默认不监听；S/daa-harness的rust-snap7-driver只是client feature，与DS server feature分开，local-validation始终关闭。

前端直接包保持锁定解析结果：@element-plus/icons-vue2.3.2、@tauri-apps/api2.11.1、element-plus2.14.2、vue3.5.38、vue-i18n9.14.5；dev @tauri-apps/cli2.11.3、@vitejs/plugin-vue5.2.4、typescript5.9.3、vite5.4.21、vue-tsc2.2.12；保留原pnpm-lock全部integrity、pnpm11.11.0及workspace esbuild allowBuilds。Node22.19.0来自DAA006既有QA环境记录，本轮未执行node/pnpm；未来B0核目标版本与可用cache，不复制DAA node_modules。runtime/desktop/前端新增依赖编译面均是r4需Owner批准的增量，不写成已证可构建。

Tauri identifier/路径、commands/invoke、capability和--no-bundle/--config语义已于2026-10-20只读核[官方配置](https://v2.tauri.app/reference/config/)、[调用Rust](https://v2.tauri.app/develop/calling-rust/)、[capability](https://v2.tauri.app/security/capabilities/)和[CLI](https://v2.tauri.app/reference/cli/)；固定源码版本决定实际行为。只保留main窗口/core:default，无shell/fs/sql/http/updater插件、remote capability或任意命令执行。此核对不等于native启动或安全/三平台证明。

### 2.9 Rust唯一runtime与受控C ABI

正式Rust库R=`D/runtime/`，crate ds-runtime0.1.0/Rust2021。依赖方向为Tauri commands或G0 stdio→Rust application service→domain image/policy/request→native infrastructure；一个instance一个Rust owner及固定规则模拟时间，Rust manager持有C/H/TCP/全局资源令牌。六来源、读快照、CAS/epoch/seq、BOOL/STRING准入、三类轮转/连接RR、tick合并、控制及时通道、取消/提交边界全部在Rust。G0两实例A/B不另复制实现；C++中不得残留owner/image/规则/业务队列/限额真相，native TLS仅关联conn/PDU/item和借用buffer。

新桥`S/native/ds_g0_bridge.h/.cpp`仅包装受控Snap7对象/整数句柄、socket、callback及生命周期。C ABI version=1：opaque DsG0Server*；exports ds_g0_create/start/request_stop/poll_stop/close/destroy、ds_g0_abi_probe与ds_g0_clock_ns。create只构造不bind；request_stop非阻塞封native准入/唤醒，poll_stop报告真实joined状态，destroy仅callback=0且所有native join成功后允许。Rust先取消/完成当前item再驱动native关闭，不能跨FFI持owner锁等worker导致互锁。

callback table用`#[repr(C)]`/固定u32长度、u64 ID与c_int状态，禁止Rust bool/String/Vec/trait object或C++对象布局穿ABI；首字段abi_version/struct_size。accept_reserve(user,out_token)->c_int、accept_cancel、accepted(user,token,fd,out_conn)、cotp/setup、begin_pdu(user,conn,bytes,len,out_pdu)、item(user,conn,pdu,index,operation,tag,data,len)->c_int、end_pdu、active/closing/joined/io；只有Rust准入成功才预留/晋升，native以非0拒绝。ID在Rust单调分配；joined只有真实pthread_join返回0才释放令牌，create失败无thread单独归还一次。回调表和user以稳定Box/Arc backing维持至callback归零+native worker真实join，不把Sender/IP当connection ID。

读/写item继续严格匹配原TS7Tag五个c_int、packed20B/align1、offset0/4/8/12/16；Rust按unaligned安全复制读取字段，不造aligned引用。原native RW callback由C++静态int函数调用Rust item c_int，0→原item成功，非0→原真实item失败；禁止rust-snap7高层void callback或仅事后events。write入参先在全PDU预算内复制给Rust请求，read由Rust单epoch快照复制到当前native响应stage；Tag/data只在同步callback内有效，不跨线程留裸指针或把native buffer注册成共享image。

第一item前native begin_pdu交Rust完成全PDU校边界/descriptor/最坏响应原子预留，随后native原item循环逐项等待Rust公平dispatch，不把PDU当不可取消业务单元。native线程/帧/消息/OS缓冲与Rust队列/复制/事件环按一次归属计账，Q(p)2208B保留为该有限PDU backing合同；新FFI envelope/请求节点/对齐/临时copy须额外列明，不能把Rust新增占用隐藏在旧C++sizeof内。正常profile原64KiB/1MiB/4MiB与线程句柄预算不增加；若新增真实占用超预算，先减冗余副本或blocked，不抬阈值。

Rust回调用非unwind C ABI，user只指稳定Send+Sync上下文并以内部同步访问，不跨并发回调制造独占&mut引用/重复from_raw释放；入参/预算/分配在commit前校验。Rust unwind panic由边界内catch_unwind转明确故障，C++异常在桥内捕获，均不得跨语言传播。不可取消commit段须为预校验后的不可失败有界更新；若异常已在commit后发生，按既有已提交/未知回执边界关闭并保留receipt，不能改报item失败/回滚/重试。panic=abort/segfault不声称catch可恢复，只记进程故障风险与未通过case。[Rust FFI官方约束](https://doc.rust-lang.org/nomicon/ffi.html)仅解释边界，真实int/布局/线程重入/指针有效期仍须r4双向无端口探针与W矩阵。

**统一时钟**：r4 Rust和native在macOS使用明确clock_gettime(CLOCK_MONOTONIC)纳秒源，所有事件标clock_id/run_id及boot/run anchor；native绝对IO期限和Rust准入期限用同源，Rust Instant仅允许本进程内elapsed。Python3.9 monotonic/参考client steady_clock只算各自持续时长，不直接比较绝对值或据其过滤Rust资源/规则窗口。runner使用Rust返回measurement_begin/end事件及逻辑phase ID取C01窗口；跨进程相关性用request/item ID和有界ping夹点校准、记录offset区间/不确定度，阈值用同源差值或保守上界，区间跨阈值不得判pass。B0重复100次Rust→native→Rust无端口clock探针确认native时刻落在夹点区间且无回退；Python ping校准给原始前后时刻/区间，不编造相同原点。原r3对比缺口必须消除后才进入G0。

## 3. 精确r4写入边界、源码与执行入口

### 3.1 本次仅PM批准登记；下一gate为Development

本次PM仓内只写`plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md`；草案辅助证据保留原`/private/tmp/arch-aw-005-r3-refresh-ii4zqye9/execution-coordinator/pm-r4/`，批准登记辅助证据只写`/private/tmp/arch-aw-005-r3-refresh-ii4zqye9/execution-coordinator/r4-approval/pm/`。不改tasks/checklist/设计正文/源码/依赖/P/索引，不复制工程、归档/删除旧源码、构建/安装/加载库/ABI/启动/native/监听/连接或SQLite。主协调在PM批准登记handoff后只机械同步根PLAN.md/PLAN.zh-CN.md及plans/README.md/README.zh-CN.md既有005行owner_approved并启动实际Development；r3后续执行保持停止，按已批准r4承接，不把r3进展当r4已实现。

### 3.2 批准后正式路径与封闭allowlist

D=`automation-world/device-simulator/`为独立DS工程；R=`D/runtime/`，S=`D/g0/`，P=`plans/ARCH-AW-005-ds-g0-prototype-validation/evidence/`。D新增持续工程最小README/PLAN/plans索引pair，全部链接唯一根005 bundle；不复制bundle或另造Task ID，当前根owner/namespace/acceptance chain不迁移。S/R各README pair由D/root PLAN管辖，不额外建PLAN。

临时T=`/private/tmp/arch-aw-005-r4-exec/`，raw持久A=`/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r4-evidence/`。DEV/QA串行使用固定正式树，T/build/{dev,qa}/{cmake,native,runtime,daa,desktop,frontend}、cache/{dev,qa}/{cargo-home,pnpm-store}、tmp/{dev,qa}、profile/{dev,qa}、runs/{dev,qa}-NNNN；A同名dev-run-NNNN/qa-run-NNNN。未知已有目录/占用即blocked，不覆盖/kill/换端口。编译产物仅T；node_modules及src-tauri/gen/schemas为D内明确忽略的可再生临时依赖/生成物，不进源码清单，角色依次建立/核归属/重建，不借用DAA依赖目录。

| 精确正式文件集（路径相对D，另有说明除外） | 批准后责任/限定 |
| --- | --- |
| README.md/README.zh-CN.md、PLAN.md/PLAN.zh-CN.md、plans/README.md/plans/README.zh-CN.md；R和S各README pair | DEV只记录DS独立身份/工程入口/当前005及未批准产品阶段，单bundle引用不复制事实。主协调只根4索引机械同步。 |
| .gitignore、.env.example、package.json、pnpm-lock.yaml、pnpm-workspace.yaml、index.html、vite.config.ts、tsconfig.json、tsconfig.node.json | DEV按§2.8冻结源派生；忽略node_modules/dist/target/gen-schemas，无真实env。源依赖不升级，DS dev15194/preview14194 strictPort；本G0 native骨架使用嵌入前端不启动这两个HTTP端口。 |
| src/App.vue、main.ts、env.d.ts、styles/app.css、layouts/AgentLayout.vue；components/shell/{AgentSidebar.vue,AgentTopbar.vue,RuntimeStatusCapsule.vue} | DEV源白名单壳派生及单停止态概览，不复制业务页面。 |
| src/console/{types.ts,sections.ts}、composables/{useAgentConsoleShell.ts,useAgentLocale.ts,useAgentTheme.ts,useDeviceSimulator.ts}（均在src/console/下）；src/services/deviceSimulator.ts | DEV纯壳偏好/薄只读IPC；无DAA bootstrap/业务poller、伪造成功或隐式listener。 |
| src/locales/index.ts、{en-US,zh-CN}/{common.json,navigation.json}（均在src/locales/下）；src/app/simulator/manifest.ts、views/overview/index.vue、locales/{en-US,zh-CN}.json（后两组均在src/app/simulator/下） | DEV精简i18n键/单概览，双语对称，沿CU公共API；不新增配置/import/history页面。 |
| src-tauri/{Cargo.toml,Cargo.lock,build.rs,tauri.conf.json,capabilities/default.json}；icons/{32x32.png,128x128.png,128x128@2x.png,icon.icns,icon.ico}（icons在src-tauri/下） | DEV独立identity/薄壳与最小权限，bundle.active=false，不发布/签名/installer/sidecar；锁子图按冻结bank，不拷DAA source graph。 |
| src-tauri/src/{main.rs,lib.rs,app.rs}；commands/{mod.rs,runtime.rs}、config/{mod.rs,bootstrap.rs}（均在src-tauri/src/下） | DEV注册仅两个只读IPC、显式owned profile、同R库装配和退出shutdown；无SQLite/collector/DAA app依赖。 |
| R/Cargo.toml、Cargo.lock、build.rs；R/src/lib.rs、app.rs、bin/{ds-g0-server.rs,ds-g0-abi-probe.rs} | DEV Rust唯一runtime0.1.0与两个薄独立入口；默认无自启/扫描/env读，bare CLI帮助；native-s7 feature仅选择adapter，不改变owner/业务语义。 |
| R/src/commands/{mod.rs,stdio.rs}；config/{mod.rs,g0_profile.rs}；domain/{mod.rs,image.rs,policy.rs,request.rs,result.rs}；services/{mod.rs,owner.rs,scheduler.rs,lifecycle.rs}；infrastructure/{mod.rs,native_ffi.rs,clock.rs,logging.rs,resource_sample.rs} | DEV全部Rust业务/队列/控制/CAS/预算/规则与安全FFI、结构日志/采样；命令不持image，native无业务owner。各目录相对R/src，非任意通配扩展。 |
| R/tests/{owner_contract.rs,ffi_contract.rs,clock_contract.rs} | DEV有限纯内存/无端口ABI/时钟测试，覆盖真实保护/危险边界；QA可独立执行并核实际wire，不凭单元测试替代19case。 |
| S/CMakeLists.txt；native/{ds_g0_bridge.h,ds_g0_bridge.cpp}；native_abi_probe.cpp；client/{reference_main.cpp,wire_cases.hpp,wire_cases.cpp,resource_sample.cpp} | DEV native仅原库12cpp+小C桥、双向探针及独立reference；CMake不再生成C++ ds-g0-server，不链接旧server/owner。resource_sample.cpp从旧server版本限定迁入client后按新clock schema校对，非DS业务。 |
| S/vendor/snap7-1.4.2/{upstream,controlled}/src/**、各自release/Wrappers/c-cpp/snap7.h及gpl.txt/lgpl-3.0.txt；upstream-manifest.json、controlled-manifest.json、native-g0.patch、NOTICE.md | DEV原包封闭同集，upstream只读；controlled仍只§2.4八文件可改，不扩线程框架/完整协议栈。r3既有patch只是待复核输入，不当已通过能力。 |
| S/daa-harness/{Cargo.toml,Cargo.lock,src/main.rs,src/domain/mod.rs,src/infrastructure/mod.rs} | DEV保持真实DAA五模块/core外部path、原66registry闭包与两个非102端口；无DS server业务/DAA应用/SQLite。 |
| S/scripts/{prepare_data.py,run_cases.py,collect_evidence.py,verify_evidence.py,build_skeleton.py}；S/fixtures/g0/{limits.tsv,points.tsv,fixture-a.bin,fixture-b.bin,profile.json}；D/source-inputs.json | DEV只19case/骨架编排/校准与原合成夹具；source-inputs涵盖D/R/S及只读来源，排除自身/其它派生manifest/T/P/A，禁止自哈希。 |
| S/server/{main.cpp,owner.cpp,owner.hpp,protocol_hooks.cpp,protocol_hooks.hpp,resource_sample.cpp} | **只允许在§3.5先校SHA持久归档后退役删除这6个自有未采用源文件**；不迁入Rust产品依赖、编译/运行/备用owner，不删除其它source/vendor/fixture。r4 PM当前不删除。 |
| 仓根docs/AIIS_DS_Detailed_Design.md、docs/README.md/README.zh-CN.md、CODE_INDEX.md；本根bundle tasks.md/checklist.md | DEV只更正005 r3→r4 Rust runtime/派生骨架并保持§2.7设计，其它正文/004 bundle/DAA/CU/core不变；tasks由DEV真实追加r4，checklist只fresh Verification创建/更新，不伪改r3原证据。 |
| P/input-manifest.json、protocol-baseline.json、delivery-source-manifest.json、evidence-index.json、resource-closeout.json | DEV只5类紧凑manifest/结果索引/hash，不放raw日志、图、bin；QA只核DEV工件写checklist。Owner终验后协调按checklist机械同步acceptance/status/事实链接且保留verifiedCandidateSha256及delta，代码/协议字段不变。 |

S/vendor通配仅指冻结官方包原成员，不授权任意新文件。全部DAA/CU/core/004只读；“剔除DAA文件”指不复制到D，不能删除源工程。实际新增路径超封闭表或依赖/端口/风险实质改变回PM新Revision。正式D/R/S全source manifest不含构建/日志/生成schema/node_modules，临时副本如确需须由此manifest复制且重建核同，不能仅tmp源码通过。

A每个dev-run/qa-run保存的闭集沿r3：commands.jsonl/source-manifest.json/native-g0.patch/dependency-graph.json/build-manifest.json/abi.json/limits.json/fixture-manifest.json/events.jsonl/wire.jsonl/results.jsonl/resources.jsonl/processes.jsonl/summary.json/cleanup.json/stdout.txt/stderr.txt/inventory.json及images/{case}-{step}-{instance}-{epoch}.bin；新增clock-calibration.json、scaffold.json和依赖安装/骨架启动原输出（并入commands/stdout/stderr），只公开合成输入。T→逐成员SHA持久A→P引用inventory/hash→tasks/checklist，不仅记hash后删raw。各inventory排除自身，source→D/source-inputs→P/delivery-source-manifest→A build/inventory→P evidence/protocol引用无环；checklist接受事实不与protocol互相内容哈希。

### 3.3 获批后B0/骨架/G0构建启动动作

以下已获**Owner精确r4批准**，批准登记时尚未执行；本次PM不代Development执行。0：先§3.5持久归档r3；1：源pin/61 acceptedFiles/37骨架源/17CU/99旧G0、工具链/cache/端口检查；2：正式D派生骨架和R业务，停用删除旧6文件，审native8文件+新桥有限diff/调用图；3：无端口B0/clock；4：骨架能构建启动；5：19case；6：fresh QA重建/复现后Owner接受。

CMake从正式S，source仍controlled/upstream原12cpp列表（sys snap_msgsock/snap_sysutils/snap_tcpsrvr/snap_threads；core s7_client/s7_isotcp/s7_partner/s7_peer/s7_server/s7_text/s7_micro_client；lib snap7_libmain），受控target另加native/ds_g0_bridge.cpp；不链接server六文件。命令保持`cmake -S <S绝对> -B <T>/build/<role>/cmake -G "Unix Makefiles" -DCMAKE_MAKE_PROGRAM=/usr/bin/make -DCMAKE_CXX_COMPILER=/usr/bin/clang++ -DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_OSX_SYSROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk -DCMAKE_BUILD_TYPE=RelWithDebInfo -DDS_G0_OUTPUT_DIR=<T>/build/<role>/native`再`cmake --build <同build> --parallel 2`。C++17/-O2/-g/-fno-omit-frame-pointer；输出libds_g0_native.dylib（bridge+controlled）、libds_g0_reference.dylib、ds-g0-reference、ds-g0-native-abi-probe。native dylib用@rpath，reference自有@loader_path，禁system install/DYLD变量替代源。

Rust固定绝对stable rustc/cargo1.89.0/aarch64-apple-darwin，CARGO_HOME=T/cache/role/cargo-home、CARGO_TARGET_DIR=T/build/role/runtime或desktop、TMPDIR=T/tmp/role、DS_G0_NATIVE_LIB_DIR=T/build/role/native。R/build.rs校目录/manifest并输出冻结native link-search/link-lib和所需rpath，src-tauri/build.rs对最终app明确同rpath；otool -L/LC_RPATH验证，不依赖PATH旧lib。runtime/desktop以冻结548 bank、client以66闭包离线生成各自正式锁，校子集后`cargo tree --offline --locked -e features`，以后`cargo build --offline --locked --release --target aarch64-apple-darwin --manifest-path <R>/Cargo.toml --features native-s7 --bins`；输出T/build/role/runtime/aarch64-apple-darwin/release/{ds-g0-server,ds-g0-abi-probe}。pure/FFI测试仅R三个test文件，以同manifest/locked/offline/features执行，不跑DAA/core全量测试。

真实DAA client仍从正式S/daa-harness、外部五模块构建，core相对三级path和domain五级#[path]不变；使用T/build/role/daa及原`--no-default-features --features rust-snap7-driver --bin ds-g0-daa`、offline/locked/release/target命令。DS server不得依赖DAA app/runtime；client单独进程的编译模块复用不是服务器运行依赖。

B0须保存所有新bin/dylib SHA、file/otool/nm/SDK/flags、native/C/Rust ABI双向int返回/Tag20B布局、callback表version/size/offset、实际copy/capacity/budget和Rust调用链、feature图/正式树hash及§2.9时钟100夹点。运行无端口native与Rust probe，成功仅关闭相应B0项；任一有限控制/ABI/clock/依赖未闭合，不启动listener。r3旧ABI数值不复用作r4新结构/owner节点的证明。

骨架依赖：固定Node22.19.0/pnpm11.11.0，D下`pnpm install --offline --frozen-lockfile --store-dir <T>/cache/<role>/pnpm-store`，写自身忽略node_modules且不借DAA目录；cache缺包则blocked，不在线升级/下载。Vite从进程显式DS_FRONTEND_OUT_DIR=<T>/build/<role>/frontend取outDir；`pnpm build`运行vue-tsc/vite。`/usr/bin/python3 <S>/scripts/build_skeleton.py --project-root <D绝对> --run-root <T> --role <dev|qa>`只编排上述构建及T/profile/role/tauri.g0.json（frontendDist为该绝对frontend、beforeBuildCommand=null、bundle.active=false），在D调用`pnpm exec tauri build --no-bundle --target aarch64-apple-darwin --features native-s7 --config <该JSON>`，CARGO_TARGET_DIR=T/build/role/desktop。最终native app路径T/build/role/desktop/aarch64-apple-darwin/release/aiis-device-simulator；不打包installer/app/dmg/签名/发布。

骨架启动使用该实测SHA binary，显式DS_PROFILE_DIR=T/profile/role/native、DS_G0_PROFILE_JSON=T/profile/role/profile.json和DS_G0_RUN_ROOT=T；typed profile只读原合成模板，应用初始stopped且不bind30102/30103，IPC只快照/刷新。原生可见窗口、版本/DS标题、主题语言/无DAA菜单、两个真实只读IPC、退出shutdown及3次启动关闭记录scaffold.json/commands/进程树，每次退出5s内无owned app/worker残留，截图只辅助；无桥浏览器预览不是成功。骨架/WebView/cache资源单独记录，不套C01 server阈值；不以骨架证明完整Tauri产品/跨平台。

B0与骨架检查闭合后，`prepare_data.py --source-root <S> --run-root <T> --role <role>`复制核原模板；`run_cases.py --source-root <S> --runtime-root <R> --run-root <T> --role <role> --b0-run <T>/runs/<role>-NNNN --case <原19case>`严格用该role Rust server与native ref/DAA client路径/SHA，传limits/points/fixture/profile显式路径、`--port-a 30102 --port-b 30103`。协议进程不启动Tauri/WebView；stdin沿用原start/stop/pause/resume/reset/close/write/barrier/overlay/budget有限harness意图，全部交Rust服务。裸入口帮助；不创建额外API/HTTP端口。DEV/QA各自build/cache/profile/run串行，固定30102–30104仅前run真实退出释放后fresh复绑，不当端口已预约。

### 3.4 有限协议baseline（功能合同保留）

| 固定项 | ds-g0-s7-v1候选合同（无产品UI/SQLite，不是发布版本） |
| --- | --- |
| 端点 | A 127.0.0.1:30102，rack0/slot1/called0x0101/calling0x0100；B :30103，rack0/slot2/called0x0102/calling0x0100；30104无listener负例。owned冲突socket仅临时占A；禁SO_REUSEPORT隐式分流/wildcard/102/换口/抢占。今天lsof未观察占用不是预约，run前再查，foreign占用即fail/block。 |
| 内存/标识 | 每instance DB41=1024B、DB57=64B；DB57首8B为ASCII DSG0A001或DSG0B001，其后56B零，read-only。DB号/绝对布局只属该有限profile，不固定产品DB拓扑；与v1 Names28/60/47样例无派生关系。 |
| DB41明确布局 | byte0.bit0 client BOOL、bit1 fixed-rule TRUE，其余reserved；byte1八个client BOOL；offset2 INT、4 REAL；offset48 ui-owner DINT、56 client-hold DINT（维护开关默认false）；64 STRING[8]占10B，128 STRING[254]占256B；400/404/408/412/416/420六个dynamic DINT、424 fixed-rule DINT；512..639为16个8B client槽，每槽两个完整DINT。其余reserved读零/禁写。各点无重叠。 |
| 类型/规则/初值 | 本G0实际typed范围仅该DB41的BOOL/INT/DINT/REAL/STRING[8]/[254]，另有DB57 marker raw bytes；§2.7的BYTE/USINT/WORD/UINT/DWORD/UDINT/CHAR是产品设计，不并入G0已验收类型矩阵，超profile另spec。全数值0、BOOL false、STRING的max/actual=n/0和零填充；start前rule t=0将byte0.bit1设TRUE、DINT424设7，6动态DINT在100ms桶k用(k+j)%101（j=0..5）给受控入口，非通用脚本引擎。BOOL mask、大端完整字段、有限f32和完整ASCII STRING按原19case；DB57 marker是明确只读合成初值。 |
| 权限与可读范围 | DB41/57完整范围client_read=true；DB41只有上述client BOOL/INT/REAL/STRING/16槽及56的client-hold可依coverage写，48仅ui-owner；rule/marker/reserved全触达写拒绝。C05/W07专门profile可在stopped显式开启56的一次性维护、revision/epoch/CAS及证据可见，不能在默认baseline暗开；W02 overlay只在该负例启用/撤除。 |
| 协议和限额 | classic DB read/write单/多item、BOOL/byte规范化；PDU480/frame512、≤4items且实际装得下、单item≤256B、AMQ1，C16/H4/TCP20及原全球/队列/bytes/期限不变。不能用“连上”代C01/C05吞吐；>16/全局峰值/完整PLC/SZL/CPU操作不支持或未验证。 |

W/C/D/X全部适用必证case与AC通过、无blocked、真实cleanstop/pthread_join/复绑/资源回B0，**正式源码/模板/依赖/生成binary与fresh QA验收候选一致**，并获Owner最终接受后，才可交接该有限standalone baseline。交接包protocol-baseline.json须含profile_id、Task ID/Revision/spec SHA、正式source/八文件patch/五DAA/core/样例pin、build/start/stop命令/工具链/SDK/bin SHA、端口/TSAP/DB/编码/权限/marker、case原证据/负例/16会话/资源限制和未覆盖能力；DEV时QA/Owner为pending，只能链接预定角色记录，不能预填未来通过。最终接受以checklist为唯一权威，主协调仅按§3.2机械同步该工件接受字段并保留已核候选SHA/原始内容证据；无事实仍candidate/not_run。no_go研究可以被接受，但不得同时宣称已有可联调server。

该baseline若满足下一任务对这些**合成绝对DB/类型/有限规则**的需求，可供另行批准的真实DAA应用S7→SQLite联合验证使用，不必为了读这些DB先实现全DS UI/配置库。G0真实ManagedS7 harness不是应用采集/SQLite落库证据，也不关闭B；联合任务须独立spec/原应用profile/版本/源/SQL证据、fresh QA、Owner接受。若DAA所需DB/类型/持续时长/运行行为超出本profile，先另spec扩并验收DS baseline，不拿004目标充当已有能力。阶段C/Backend/SMA/上传始终排除。

### 3.5 r3原件归档、资源与清理

未来DEV迁移前必须先把停点99个S文件**原字节**与已批准r3全文、r3 tasks/DS正文停点快照、原构建/诊断证据持久到A/r3-stop-snapshot/，归档后逐成员SHA/inventory并引用P/input/evidence-index；此后才允许删明确的6个未采用C++业务文件。原99-file inventory digest `6fa308482bf4e1d771613b57fec0dfd3be42025817e29f7cf06832c766c211e8`（按完整仓内path排序的path<TAB>SHA<LF>）为封闭起点；复核不符先blocked，不以新文件重算消除漂移。A/r3-stop-snapshot/sources/保留该99闭集的原相对路径/bytes，A/r3-stop-snapshot/approved-r3-spec.md=7ec38de5…完整SHA见§1；r3-stop-snapshot.json原SHA `19b73bc0b101260d9b6465b2bfad4648eceb1559fb52dd1701f7d18962487b75`作为读时停点，不是G0通过。

旧T3=/private/tmp/arch-aw-005-r3-exec的必要raw闭集：runs/dev-0001/{dependency-graph.json,source-manifest.json,stderr.txt,stdout.txt}与runs/dev-0002/{abi.json,commands.jsonl,events.jsonl,limits.json,stderr.txt,stdout.txt}，持久A/r3-stop-snapshot/diagnostics/保持原字节；r3 tasks行政停点SHA见§1、DS正文读时SHA见§2.1，若发生新变化回协调核来源。archive清单/inventory排除自身，P只紧凑指向A，不公开raw。不复制旧可执行/dylib构建产物、.env/DB/依赖缓存；合成fixture*.bin作为99源码输入仍保留。不把未闭合诊断sealed成pass；旧T3在归档校验前不清理。当前PM不执行归档/删除。

r4 Rust server单进程承载A/B，各唯一Rust owner；native listener/worker/reaper、Rust owner/control/规则/采样/日志writer及内部缓冲全部计DS tree，reference/ManagedS7/Python客户端和骨架/WebView另列。Rust线程JoinHandle::join与native真实pthread_join均须返回，WaitFor/Closed/Drop/移出表不是证明；停止先封Rust/native准入并request_stop唤醒IO，Rust取消未入段/只完成当前item且上下文继续存活；callback归零/native workers真实join后Rust接收joined归还预算，再owner退出/Rust join及native destroy/stopped。不得先退出owner令callback等已结束线程，等待期间不持owner锁。正常2s/故障5s边界与原case不变，超时保留失败/closing/所有权，拒假stopped。native硬崩同进程风险/X02条件N/A不变。

日志使用tracing JSONL stdout+有界异步文件sink，稳定顶层event/run_id/clock_id/monotonic_ns与request/item/phase字段供runner解析，不套旧C++绝对at筛选；stdio结果按request ID关联，不把任意日志行当回执。事件只在owner外写盘；降级/丢弃计数不改提交结果，缺证据case blocked另run。r4 A/各run保留必要原证据至另批DAA–DS联合验收后再复核，不自动过期；正式D/R/S/P及r3 archive不当临时清理。主协调在Owner接受后才按已确认归属/无运行/无验证或后续依赖/证据已持久条件清理owned T3/T4、忽略node_modules/gen/cache；QA不清理。native骨架产生的独立WebView本机数据路径记录实际归属，只清本任务新建且无依赖的DS材料，不碰DAA/CA/SMA/CU或真实profile。失败实验仅已核PID先TERM、5s后仍不退才KILL并记失败，不按名批量kill。

## 4. 编号需求


### R1. 保持G0交付小范围

只交DAA派生可构建启动的最小DS骨架、Rust唯一内存/准入runtime、有限native候选及真实S7/DAA模块互操作、资源原始证据与限制。所有以下“运行/测试”均指未来获批执行；本轮不执行。沿用004目标，不实现产品UI、DB/UDT导入、SQLite保存/apply、完整规则引擎或完整DAA采集应用。规则、普通UI、一次性维护、init/reset可由标明来源的harness触发；它们验证受控入口，不宣称产品页面/IPC已实现。

### R2. P0来源冻结、B0构建/ABI与执行面

本r4的精确来源、工具链、文件/动作面以§2/§3为准；进入协议运行前须完成B0并有可审查的manifest：候选库精确版本/commit或发布包SHA、完整源码manifest与本地改动patch、native二进制SHA/动态静态链接/编译flags/ABI/目标架构；client版本/源与编译feature；OS/build、CPU物理核/逻辑线程、RAM、背景负载与采样工具口径；主/子进程资源模型、所有写入口/系统dispatch/阻塞点；第3节源码与依赖/输出/端口/动作精确表。参考主机至少4物理核、16GiB RAM、SSD，仅报告本次一个明确OS/架构结果，不外推三平台。

G0建议固定classic S7 PDU上限480B、单frame上限512B、单item应用payload≤256B、每PDU≤4items且实际请求/响应均可装入协商PDU；COTP分片累计重组也限480B且绝对期限不重置。协商AMQ、最大错误响应、描述符/stage/copy及系统socket buffer实额须从冻结实现计算，列完整最坏输入+输出预留公式。数值只是这个G0有限profile，不缩改004产品容量合同；不能静默降PDU/请求或用不可控库内队列冒充有界。无法控制/观察者在对应gate blocked或判候选不满足，先回PM决定。

### R3. Rust runtime固定，协议候选先证明可拒写

按第2节逐候选给证据支持的adopt/reject/blocked及原因，核回调时机、错误传播、线程/ABI/指针生命周期及未列操作。写前入口必须能阻止image更新并让客户端收到真实S7 item失败；无入口即淘汰，不得降为写后报警/回滚、tick修复或仅UI禁用。本r4固定Rust业务runtime，只提出§2.4/§2.9有限原生扩展与DS正确int FFI，尚待Owner批准；不采用rust-snap7高层void callback server、C++业务owner或Python sidecar。B0未证ABI与有限扩展可行性前不进行协议运行。

### R4. 单owner、提交事件与拒写证明

每实例唯一Rust image owner，所有读复制、来源准入、coverage/type/CAS复核和单item提交可追踪。非法写的静默测试先暂停规则并封其他合法写/排空在途，在同一epoch、同一已确认布局下保存**全部可能触达DB的完整bytes/hash、全image hash、instance seq、点版本/来源/更新时间**；失败后逐字节相同，客户端有真实失败。未知DB/越界/未列系统操作还核所有已分配DB，不能只看第一个点。

仅最终读回相同不足以证明写前拒绝：同时给冻结源码调用链与`request_received -> admission/type/owner_decision -> rejected(no commit) -> item_response`事件顺序；合法路径为`accepted -> commit_begin -> committed(seq) -> response`。在实际mutation入口计数/记录写前写后，证明拒绝item无任何commit/裸buffer写，再无“恢复旧值”动作。并发测试另按item/result ID、触达点版本与获准写范围对账，允许其他合法提交改变实例seq/hash，不能要求规则运行时全image绝对不变。观测本身不能改内存。

### R5. 原始bit/byte、typed包及item结果

覆盖BOOL邻位与整byte、全触达跨权限、部分标量、边界/长度/transport-size/count、有限REAL、大端整数、STRING完整包/长度头/ASCII与多item部分成功。每write item原子，失败全item不变；读item来自单epoch/seq复制，多item按内部顺序逐项并允许连接/规则交错。不同PDU/DB/实例无全局原子承诺。未列非DB区/CPU控制/clock/块操作/任意SZL不可绕过入口或映射为DS控制；必要最小握手元数据按P0白名单逐项列出，不接受库默认“成功但无作用”当拒绝。

### R6. 六种写来源收口与权限/CAS

client、rule、普通UI、一次性ui_maintenance、initialize、reset均从harness进入同一owner或同锁封闭maintenance模式。普通UI仅ui-owner；一次性维护只对显式允许的client/none hold，默认关，不改变持续owner，后续合法client可覆盖；rule暂停仍不让权。UI/维护带expected loaded revision/epoch/point last_seq，在提交边界CAS，冲突不写/不自动重试。init/reset仅封闭gate/stopped，非法运行中调用拒绝；reset为新epoch/初始化，stop-start保值。这里只验证入口合同，不新增持久apply/保留算法或租约。

### R7. 16会话与C/H/TCP/closing计数

一个PLC=一个server实例，C为**已建立S7 sessions**，非进程/IP/TCP accept数量。沿用默认C16、整数1–64（>16未验证）、H4整数1–16、accepted TCP=C+H默认20；closing直到socket/callback/worker真释放仍占先前C或H和TCP。全局C/H/TCP128/32/160、全树≤64线程/≤1024句柄均为硬预算，启用实例配置和不得超预算，0/负/小数/无限拒绝，修改只stopped显式载入；G0仅运行单实例16及两实例各少量兼容连接，不跑2×16/8×16。配置域边界/全局加总可由无端口的harness校验，不冒充64/128会话容量。

满额拒后来者、不抢占老连接、不重置hold、不提前虚减closing，不在同socket阶段转换重复计数。库MaxClients参数不能替代真实C/H/TCP各阶段准入及计数，短命超额accept句柄也须列入实际OS资源，不隐去。连接快照须有instance/connection ID、peer、阶段、建立与最近收发完成时间、执行/等待/bytes、拒绝/超时/关闭原因；无需产品面板，但独立QA能核逐连接事实。全局上限不代表与线程/CPU预算能同时打满；每连接一线程候选不得由本次16会话外推128或静默提高64线程预算。

### R8. 期限与有限队列/输入输出预算

沿用握手5s（accept起算）、半frame2s（首byte起算）、待提交2s（完整PDU准入/等待起算且commit复核）、send2s（响应开始发送起算）；滴流不续期，正常idle踢出默认关闭。每连接≤1执行+2等待PDU及64KiB全部协议bytes；实例等待≤64PDU/1024items及1MiB；全局等待≤256PDU及4MiB；UI等待4、普通控制8、每规则待tick1。bytes包含未完frame、执行/等待、描述符、stage/copy及最坏响应预留，转阶段不重计、复制新增计、closing仍计。

整个PDU输入/输出先原子预留，再执行第一item；预算不足真实失败或关闭该连接，无item已提交。单个写callback不能替代整PDU入队/最坏响应预留或逐item结果/内部顺序；P0若无法观察控制这些阶段，须判不满足或回PM改方案，不默许重写协议栈。PDU/item超协商/超限、send阻塞、未完握手和半报文均有明确结果。G0对未能由16会话/480B profile触达的实例/全局大上限，以**标明test-only的更小预算或确定的reservation故障注入**验证相同准入控制点及归还，不声称填满4MiB/1024items；正常profile硬上限不提高。协商AMQ较小时如实列实际可达状态，不伪称已实测1+2并行。网络收发/解析/编码、磁盘及证据写入均在owner临界区外。

### R9. 公平、规则合并与控制可达

沿用协议→规则→UI非空类轮转，协议内连接round-robin每次最多1item，同PDU保序；规则按point轮转且每规则最多1待tick、合并计missed/coalesced。用F洪峰、A/B低频、8规则及UI维护同时存在的60s场景验证。已经准入且持续可调度的F/A/B三连接，每次protocol类轮转至多3次dispatch让各方一次；三个工作类持续非空时每3次工作类dispatch各获一次。保存调度轨迹/资格时刻，不能把库锁外看不见的等待从统计中删掉。

正常低频请求p99≤250ms，无连续1s完全不服务的已准入A/B；规则与1Hz UI请求可达。过载可真实拒绝，但已预留工作/stop不能饿死；恢复基准5s内等待队列回零或稳定基准，无无界补跑。stop走及时通道，先关准入/accept，取消未进不可取消段者，当前已进段单item完成一次；不得等完整PDU或长积压提交完才处理stop。

### R10. 真实DAA自定义端口兼容

未来必证使用固定版本DAA **真实ManagedS7::connect/read/read_bounded/disconnect**，`rust-snap7-driver`开启、`local-validation`关闭，不以Python参考client、FixtureTransport或origin标签替代。推荐最小隔离harness消费**字节相同的ManagedS7及所需DAA domain依赖快照**，保留原RemotePort/rack/slot/超时调用；精确源清单/依赖/编译入口及feature见§2.5/§2.6及§3，r4批准后按B0核验。若私有API/feature/安全profile无法这样消费，结果blocked，回协调申请独立DAA范围，不能修改原DAA/改成重写近似client后声称兼容。

G0证明层级为真实DAA客户端模块对候选server的S7互操作，不覆盖完整DAA GUI/SQLite采集/历史/上传/native窗口。推荐harness不创建DAA业务库，不读任何env或默认profile，只从批准的owned内存Plc参数调用；若实际入口必须创建隔离DAA profile/数据库，其路径/动作须先另列获批执行面，禁止擅自走生产启动。明确禁上传、Backend/direct DB/授权服务/旧采集/auto-start；连接/读取仅两个owned endpoints。

### R11. 关闭、资源释放与未知回执

单连接close与全实例stop都先关相应准入，取消未进入不可取消段者，让已进段单item完成一次，然后join回调/worker、关socket/listener、停timer/清队列并幂等释放。正常单连接close/stop≤2s，故意积压/慢连接stop≤5s；超时保留closing/stopping/failed及实际名额，不假报stopped或释放仍被callback使用的buffer。未提交超时/取消=拒绝不变；已提交但回执丢失=结果未知，无回滚/自动重试/exactly-once。

记录全进程树CPU/RSS/线程/句柄及分项socket/listener/callback/timer/队列bytes/输出预留；client进程单列，不藏入或混同DS指标。检查同端口重绑、20次start-stop、16连接各10轮重连、重复关闭通知。若选sidecar，父进程正常退出/崩溃、子进程异常退出与A/B隔离必须实测，5s内无owned孤儿和占用端口；G0管理harness不等于Tauri原生退出。进程内native硬崩溃可能波及全进程须如实给隔离风险，不能靠逻辑instance ID宣称崩溃隔离。

### R12. 证据、统计与可复现交接

原始JSONL按run/candidate/build/instance/connection/request/item/result/epoch/seq及monotonic时刻关联；保存raw协议item结果/有界报文、完整合成fixture前后bytes/hash、决策/commit/response顺序、错误与预算变化、版本摘要、资源1Hz采样及状态转换采样、复现命令/退出码/环境。raw payload仅限本任务公开合成数据，不采集真实私有报文。报告offered/accepted/completed/rejected/timeout/unknown分母，逐连接p50/p95/p99/max和队列等待，不能删失败或用聚合平均掩盖饥饿。

运行raw证据先在T产生、必要原件须按§3校SHA持久化至非repo的A，P只保留5类紧凑索引/清单，不是产品日志/正式schema；证据丢失或关联不全不能判pass/go。沿用004纯日志故障降级原则：可选sink失败不把已提交成功改失败/回放；记录observability_degraded/丢弃，并将该段无法证明的case标blocked后另做新run，不把缺证据当内存已回滚。不要为G0增加强持久审计/SQLite journal。

### R13. 分阶段go/no-go及状态诚实

r4获批且B0通过后，按P1写前拒绝/全来源及item→P2连接/队列/公平/释放→P3真实DAA及最终全矩阵独立复现顺序推进；不能先建产品以待补保护。场景状态为pass/fail/blocked/not_run/deferred，以及严格条件项的not_applicable：pass有实际证据；fail为已运行不符；blocked为必要来源/环境/接口/证据不能取得；not_run为尚未执行或被早期淘汰阻断；deferred只限本spec明确排除的后续阶段；not_applicable仅用于未选sidecar时X02的父子进程专属分支，须给实际进程模型理由，不免除共通stop/资源释放及进程内native风险说明。必证项不能为凑go改deferred或not_applicable。

候选只有全部适用必证case通过、无未解除blocker、清理证据完整才可go；失败候选的后续case可not_run并给停止原因，不冒充通过。可信no_go是允许的研究结论，须指出不满足的实际控制点和复现证据；它阻止后续采纳该候选，不强迫实现完整协议栈。QA独立审核方法/复现和结论，原case fail不得被改pass；即使研究报告被Owner接受，也不代表候选能力通过。更换未列候选、放宽保护/16会话/预算/阈值、增源码/依赖/端口/DAA动作、扩OS/长负载均回PM新Revision和Owner批准。

### R14. 保留工作树与角色权威

本轮PM仅修订本spec；004 bundle/设计、DAA/core等起点保护文件及旧证据保持；只允许本任务精确角色delta。主协调只机械同步四根索引本任务既有行，保留DAA/CU等并发修改。后续Development只写获批执行面和tasks，精确handoff后新的fresh-context Verification只验证并写checklist，Owner保留最终接受与风险例外。当前profile为contract_only，串行角色/diff审计是合同控制，不宣称ACL、自动路由或团队激活。本draft文档自检不作G0、QA或Owner接受。

### R15. 已验收共享输入与真实编译闭包

按§2.1/§2.5/§2.6固定accepted-source-manifest原61项历史与当前60项同字节、1项已明列CODE_INDEX导航差异、core版本/API/profile/v1样例、新锁及五个原DAA模块；DAA006接受只解除该输入前置，不证明server或DS导入已完成。G0只使用合成DB41/57，sharedcore编译闭包与未来DS六API消费者D1分开；源漂移、依赖不闭合不自动用latest/改DAA/改expected。

### R16. 整体设计增补与后续产品边界

§2.7的多文件/逐DB闭包、instance/region/DB映射、稳定lineage/point ID、保守重导、理论地址/全实例命名、显式typed初值/编码、SQLite配置与内存保值矩阵、页面动作/薄IPC/单owner架构和开工顺序，须在获批后同步canonical DS正文及相关索引，独立核文档一致性。当前只是设计要求，D1/D2/D3/D4完整产品实现及DAA联合SQLite/C不在此范围；本r4只新增最小派生骨架与Rust G0，不借设计增补扩页/配置库。

### R17. 正式源码、构建入口及持久证据交付

有效源码/脚本/锁/vendor八文件扩展/合成模板必须交付§3.2正式D/R/S；T只派生，A持久保存必要raw，P仅5类紧凑清单/索引。B0、DEV及fresh QA须核正式树输入/生成binary/实际启动入口与验收候选一致，临时验证不得代正式交付。遵当前AGENTS§2/§6，raw日志/构建产物不入公开repo；先持久r3原件再退役6个旧源，确认来源/无占用/必要证据在A且P可定位后才由协调清T3/T4；A按联合验收后复核触发保留，不动任务外资源。

### R18. 有限协议基线的可交接性与B/C门槛

§3.4固定profile版本、正式source/入口/端口/绝对DB布局/类型/权限/marker、所有负例/16会话/公平/真实join/释放、独立QA及Owner接受，满足后才标accepted G0 standalone protocol baseline。可信no_go不等于已有server。G0模块client不代真实DAA应用S7→SQLite；后者另批spec/fresh QA/Owner接受才可能关闭整体B；超profile先扩并验收DS，C排除。

### R19. Rust唯一业务owner与正确native边界

按§2.9/§3由R库拥有唯一image/六来源/CAS/epoch/规则/队列公平/控制与预算，Tauri和G0复用，不留下可执行C++业务owner/第二份image或rules。原18R的所有协议保护适用于Rust路径；C/C++只协议/IO/有限lifecycle hooks。正确int ABI、packed Tag、借用时限/上下文注销、panic/exception、整PDU预算和单item顺序均双向探针+真实wire证明，不用返回void的高层server。

### R20. 最小DAA派生骨架与工程/依赖隔离

§2.8的37源/17CU/core冻结、保留/剔除/新增与548 registry bank/前端锁精确生效；实际编译图不含DAA业务/store/采集/历史/上传。骨架只需能派生、构建、native启动3次并退出、DS身份/偏好/own profile隔离、两个真实只读IPC；默认stopped/零listener，不以无桥浏览器、copy目录或仅cargo check代native成功。Tauri窗/前端不承担规则/队列，无配置SQLite/import消费者/完整产品页。

### R21. r3停点保护、时钟与独立复现

§3.5先持久99原件/必要诊断/原r3 spec后才退役6文件；r3编译/ABI与19not_run不迁成r4通过。r4独立B0/时钟100夹点、C01逻辑窗口/同源duration及跨进程校准原证据，无法可靠计时即blocked，不抬阈值。DEV和fresh QA从同一正式D/R/S源与新锁分别重建/新profile/同固定端口独立复现原19case；骨架资源单列，保留r1/r2/r3原文、既有任务/设计与dirty，不提前填r4批准/QA/接受。

## 5. P1写入/协议场景矩阵

以下仅定义未来输入/动作/预期。**DEV逐行实现harness/自检，在T采集、校SHA向A持久保存必要原证据，并在P留紧凑索引；fresh QA从固定handoff自行执行并独立解码item/比较bytes，不调用DEV总结冒充复现**。每个确定性向量至少独立重置后重复3次；BOOL竞争另为100轮。失败静默测试按R4关其他写并排空；并发单列，不能混用不变口径。

冻结合成fixture定义（B0生成raw manifest，不建正式schema）：每实例测试DB41长1024B、DB57长64B，后者为实例身份只读marker；DB号/两个DB仅夹具，不是产品固定拓扑。DB41 byte0.bit0=client BOOL、bit1=rule fixed TRUE、其余reserved；byte1八个client BOOL；offset2 INT、4 REAL；64处STRING[8]全10B、128处STRING[254]全256B；512起16个8B client hold槽（每槽两DINT）。普通ui-owner DINT在48、显式维护client-hold DINT在56；规则为400起6个动态DINT及1个fixed DINT，加byte0.bit1共8规则。未列空位reserved/read-zero/write-denied；A/B初值marker不同、image独立。规则参数仅够触发入口，不实现通用引擎。

W02的未确认coverage负例固定为既有DB41 offset56的4B client-hold DINT：在同一已确认布局/epoch、规则和其他合法写均经屏障排空后，harness仅对该范围启用test-only admission overlay，使owner coverage复核返回unconfirmed，再由真实client写完整4B，必须在commit前失败。它不改变已加载布局/owner/bytes/seq，不承诺产品允许未确认布局启动。保存overlay开启/拒绝/关闭事件与完整不变证据后，先撤掉overlay再解除屏障；不靠reset或回写旧bytes“恢复”。overlay只限本W02负例，不出现在C/D正常profile或默认准入策略。

| Case / 需求 | 输入与动作 | 可判定预期与必须保存证据 |
| --- | --- | --- |
| W01 · R3/R4/R5 | 真实client向自己8B槽写两个完整DINT的非旧值，raw读回；再读64B marker。 | item成功、逐字节/typed值一致，唯一commit且seq+1；raw请求/回执/读回、owner trace及完整前后image。不能只看client函数无异常。 |
| W02 · R4/R5 | 静默屏障下依次向rule字段、reserved、越权bit、未确认coverage、未知DB写；未确认coverage固定采用本节DB41 offset56的test-only overlay及撤除边界。 | 每item真实失败；全部可能触达范围bytes/hash/点版本及全image/seq不变，拒绝前无commit/裸指针写，回调/dispatch顺序可复查。自动字段即使rules_paused仍拒绝。 |
| W03 · R5/R6 | byte0.bit0合法bit写；向同byte整byte写（含rule/reserved，即使相应值没变）；byte1两个不同client位由双连接同步竞争100轮；byte1合法整byte写。 | bit写只改mask、邻位保留；byte0整byte失败且不变；byte1两位更新均保留，无RMW丢失，合法整byte成功。保存各轮item/seq与目标byte前后，不拿不同并发顺序当失败。 |
| W04 · R4/R5/R8 | 部分INT/REAL、越过client槽末端触及reserved、末端1023+2、0长度、count溢出/transport单位不符/短payload、NaN/Inf REAL及超frame/PDU；合法大端有符号/有限REAL对照。 | 非法输入在提交前失败/无可编码item时关该连接；无越界/分配爆量/其他实例变化，合法typed值可读回。保存每向量原始长度/规范化触达、错误码、全范围bytes及预算变化；格式错误与权限item失败分开。 |
| W05 · R5 | STRING[8]写完整`08 03 41 42 43`加5零字节；STRING[254]完整256B对照；错误max头、actual>max、非ASCII、只写头/截断包/部分包。 | 合法包精确读回；其余整item失败、整个STRING包及全触达字段不变，不截断后报成功。保存原始包/布局、item返回、typed解码与hash。 |
| W06 · R4/R5/R9 | 单PDU顺序3items：合法8B、禁止rule写、合法STRING；其间允许另一已准入连接/规则插入，另做静默对照。 | 真实逐item成功/失败/成功、内部顺序保留，成功各提交一次，失败范围不变；无全PDU回滚/全成功伪造。保存原PDU/result数组与逐item调度/seq，混合结果按触达范围对账。 |
| W07 · R4/R6 | 六写来源各一合法及一非法/陈旧操作：rule对hold/paused/旧epoch，UI及维护CAS冲突，维护默认关和rule即使暂停，运行中init/reset；合法维护后client再次写。 | 全部进入同owner/maintenance模式；非法无commit，合法来源和seq正确。维护不改持续owner/初值、后续client可覆盖；reset仅stopped换epoch，stop-start保值。保存源入口调用图、每操作结果与revision/epoch/point seq，harness不等于UI。 |
| W08 · R3/R5 | 对owned server发非DB区、CPU start/stop、clock、块上传下载、非白名单SZL/未知功能各一请求。 | 明确协议拒绝或有界关闭，无image/DS状态/宿主时钟变化，不能以库默认成功空操作通过。记录dispatch白名单、原请求/结果/前后状态；若库自动处理无法阻止，候选no_go。 |
| W09 · R3/R4/R11 | 在precommit及不可取消提交段用确定harness屏障分别触发timeout/stop/close；另在commit后故意丢回执；复查callback指针引用/注销顺序。 | precommit取消不变；已入段item完成一次，后项取消，已提交丢ack为unknown且不自动重试；旧epoch不能触达新image。保存call/commit/return/close/join/释放时序、引用计数及wire可达结果；禁止释放仍使用buffer。注入屏障是实验工具，不可带入产品owner等待逻辑。 |

## 6. P2连接、队列、公平与资源短程profile

每个数值均为r1已批准且本r4不降低的G0目标，不是实测支持。每个最终候选DEV完整运行一轮，独立QA从新run/profile/端口依同一冻结输入重现一轮；静态早期淘汰者不强行跑后续。不得将这些短程结果替代004 L1–L5。

| Case / 需求 | 有界输入、次数/时长 | 判据及证据 |
| --- | --- | --- |
| C01 · R7/R8/R12 | 单实例16已建立S7 sessions；预热30s后300s。各连接1轮/s，每轮2请求、各1item：DB57读64B+自己DB41槽写8B；8规则=6动态+2fixed，100ms到期。 | 32请求/s=16读+16写，应用payload1152B/s；测量段共9600请求=4800读+4800写、345600B，不含协议头；每连接600请求。按offered全量核完成，非故意错误/错写/越权/BOOL丢更新=0；每连接p95≤100ms/p99≤250ms，排队p99≤100ms，规则missed≤1%（24000到期机会，动态/fixed分列，无变化fixed不虚增commit）。 |
| C02 · R7/R11 | C01的16会话仍读写时，第17个S7连接尝试20次，间隔100ms；再关闭一条并重连，重复close通知。 | 新来者被拒，不抢占/重置原16；关闭直到真释放才腾C/TCP，重连新ID。逐时C/H/TCP/closing/实际established及OS socket、原会话成功item、拒绝阶段/原因均对账，无负计数/重复归还。 |
| C03 · R7/R8 | 另有16已建立时保持4个未完成握手TCP，第5未完成握手尝试20次；随后半frame每500ms滴一byte；另一session idle30s后正常读。每种绝对期限试3次。 | C16/H4/TCP20不超，5th握手无额外持久对象；握手accept后≤5.5s、半frame首byte后≤2.5s完成关闭/清理（含≤0.5s观察裕量，不延长配置期限）。老会话继续；idle不误踢。保存时间起点、阶段、bytes/名额/句柄释放。 |
| C04 · R8/R9 | 单连接超协商in-flight及1执行/2等待边界；另用P0声明的小预算/确定reservation故障触发每连接、实例、全局输入+最大输出预留失败；恢复后重试。慢读peer的实际收/发socket buffer各≤16KiB，20次/s发256B读取且不消费响应，最多30s，须实际观察send阻塞。 | 超额完整PDU在第一item前失败/关该连接、无commit；所有阶段数量/bytes含预留不超实额，幂等归还。发生阻塞的该响应从首次发送尝试起≤2.5s关闭（2s配置期限加≤0.5s观察裕量，不从阻塞时重置），其他连接/规则/stop继续。若只触发队列拒绝而没观察send阻塞，该subcase仍not_run/blocked，不能算send期限pass；不能以注入替代所有真实socket证据。 |
| C05 · R9/R11/R12 | 同实例F/A/B3个活跃连接、其余13个idle：F20 PDU/s、每PDU4个64B read items，A/B各用C01每连接profile；8规则100ms、UI维护1次/s，持续60s。再用小预算制造积压并从及时通道stop，3次；恢复基准观察5s。 | F offered80items/s，A/B合4items/s，规则80次到期/s，UI1次/s；PDU数与item数分别计。正常60s段A/B各60轮=120请求全部按offered完成，60次合法UI维护均有成功结果，不得把低频工作拒于准入外绕过公平；F的完成/拒绝/超时单列。仅随后明确小预算故障积压段允许按真实结果计低频拒绝。按R9轮转/时限判，保存各连接/类资格、dispatch、等待/完成/拒绝、missed/coalesced和stop各阶段；F大PDU不独占、普通控制不饿死业务，过载stop≤5s，恢复队列回落。 |
| C06 · R7/R11 | 16条连接各10轮断开/重连，共160次；每轮含一次正常close、半关闭或异常之一，轮转+100–1000ms固定seed抖动；随后20次start-stop，每次建立16session并各读/写1次，stop后等10s采样。显式reset另3次。 | 正常close/stop≤2s、故意积压stop≤5s，所有owned listener/socket/callback/工作timer/队列PDU/item/bytes/输出预留回0；stopped保留image/值不算泄漏，reset独立初始化。停止后同owned端口可重新bind，无隐形worker/旧epoch写。保留完整cycle序列，不把10轮写成004 L4每连接100次。 |

C01及上述所有阶段分别保存全DS核心/管理器/sidecar进程树的平均CPU、RSS峰值/净增、线程/句柄及分类；**client/采样进程单列**。G0目标：平均CPU≤单逻辑核100%（CPU时间/墙钟，不除主机核数）、RSS≤512MiB、线程≤64、句柄≤1024；C01测量段RSS净增≤16MiB。这是短程可行性阈值，不声称004的60min增长或长稳定性已满足。

C06资源基线为依赖已加载、image已分配、证据sink/采样器已启动但无listener/连接的稳定stopped状态B0；首轮热身后固定B0。每次stopped10s时owned transport/callback/工作timer/queue/reserve=0，线程/句柄按分项回B0；明确保留的单一库全局设施须P0计入B0，不能逐cycle追加。RSS允许allocator保留但每次≤B0+16MiB，最后5次中位数相对最先5次≤8MiB；若出现连续4组（每5次一组）严格增长且总增>8MiB则失败。原始曲线与峰值均交付，这些口径不能证明永不泄漏。

两个实例仅为端口/故障隔离对照：A16会话场景时B至多1参考会话；真实DAA场景各1。该组合ΣC默认配置32、ΣH8、ΣTCP40，仍受128/32/160及64线程/1024句柄联合预算；不能用名额配置推断2×16吞吐。>16实际会话、8×16、全局极限、大布局以及完整L1/L2的5min预热+60min和L4/L5长故障均明确deferred到D4或另批扩展任务，不在G0凑齐。

## 7. P3真实DAA与退出边界矩阵

责任同第5节：DEV提供精确非fixture入口与原证据，fresh QA独立运行、核source/feature、协议和OS状态。r4执行面未批准及B0未闭合前以下均不执行。

| Case / 需求 | 输入与动作 | 预期与证据 |
| --- | --- | --- |
| D01 · R2/R10 | 两个owned非102端口、A/B各自固定called TSAP/rack/slot和不同DB marker；字节冻结的真实ManagedS7各持1会话，60s、每连接1轮/s，每轮读取两个DB各1次；参考client改变允许hold值后再DAA读取。 | 两模块累计240次真实db_read，连接复用，能按marker/bytes/变化值区分实例，RemotePort实值与COTP/S7协商、调用trace相符。提交源/feature/native摘要、raw字节/DAA结果及server connection ID；fixture/标签/截图不能替代。只证明模块级S7，不证明完整DAA采集或GUI。 |
| D02 · R7/R10 | 错rack/slot产生错误called TSAP、owned无listener端口、A参数误指B端口；每负例3次；另用owned冲突listener阻止A启动，重复start。 | 错TSAP明确失败，不能同端口隐式复用/接受任意身份；错端口不回退102/扫描其他地址；冲突只使后来A failed、占用者和B继续、无第二listener。每次记录真实COTP、RemotePort、失败阶段/错误与名额释放；若候选默认接受错TSAP，必须先取得可控adapter证据或判不满足。 |
| X01 · R4/R11 | A/B均在服务时只关闭A一条连接；另在W09屏障处stop A，B持续读；超时注入后再观察实际清理及同端口重绑。 | 关闭只影响指定对象；未提交取消/已入段完成/已提交丢ack未知分开，B不变。正常2s/故障5s，超时不报stopped；只有callback/socket/worker真实归零后才释放/重绑。保存进程/OS/库计数和owner事件关联。 |
| X02 · R2/R11 | 若选择sidecar/每实例进程：父管理harness正常退出、父异常终止、A子进程异常退出，各3次；同时观察B，随后新run重开。 | 正常有序stop；异常时≤5s无owned孤儿/残留listener，A子崩不误报clean且B继续；重开只初始化fixture、停机，不恢复旧连接/未知写。完整进程树/PID起止/退出码/socket证据。未选sidecar则明确not_applicable理由，不宣称该能力；进程内native硬崩风险单列，完整Tauri退出与三平台发布仍deferred。 |

资源/异常测试只操作获批本任务owned进程和loopback socket；不停止DAA原生会话、不修改其profile、不向任何真实设备或生产DB/API发动作。若不能在准确进程树中区分归属，先blocked，不批量kill或清理未知资源。

## 8. AC与可审阅覆盖

下表是未来**研究交付及选型判断**的验收口径，非本轮结果。每一行均须有DEV原始证据和fresh QA独立观察；候选go必须满足对应功能预期。充分证明的no_go可以交Owner作为研究结论，但失败case原样保留，不能写成“所有功能通过”；必要项无证据仍为blocked/not_run。

| AC | 对应需求/场景 | 可核验标准 |
| --- | --- | --- |
| AC1 | R1/R14、§1/§3 | 独立namespace/Task ID/Capability/接受链、draft及五路径准确；004文档接受不移作G0批准；当前只spec，无空tasks/checklist/工程/执行。 |
| AC2 | R2/R3、P0 | §2/§3的精确source/package/hash、工具链、依赖、入口、端口与动作取得r4批准后才创建/构建；B0记录生成binary SHA、实际链接/ABI、完整预算公式后才进行协议运行。未齐或漂移则blocked，不编造当前binary hash、不自动更新依赖。 |
| AC3 | R3/R13、§2 | 候选比较与推荐顺序有primary/冻结源码依据；明确Rust wrapper/Python stub、系统dispatch及资源控制不足，给可复现adopt/reject/blocked及最终go/no_go；不自写完整协议栈或放宽保护。 |
| AC4 | R4/R5、W01 | 合法真实写成功、唯一commit/seq及原始bytes/typed读回一致；独立QA可从raw item和image核实。 |
| AC5 | R3/R4、W02/W09 | 静默/屏障下全触达bytes/hash/seq/版本/时间不变，真实失败且调用/提交顺序证明无先写后恢复；并发另按合法item范围和点版本对账，不要求全局hash冻结。 |
| AC6 | R4/R6、W07 | 六来源全部收口，普通UI/一次性维护范围及CAS、rule暂停不让权、init/reset停机权限/旧epoch均实证；harness与产品UI/持久功能边界准确。 |
| AC7 | R5、W03 | 合法bit邻位保留、100轮同byte两bit无丢失、合法全byte与含禁bit整byte拒绝均可重现。 |
| AC8 | R5/R8、W04 | 部分标量、跨权限/边界/长度/transport/count/载荷与REAL负例逐项真实失败，不越界/无隐藏分配；合法大端/有限REAL对照可读回。 |
| AC9 | R5、W05 | STRING[8]/[254]全包成功及头/长度/ASCII/截断负例不变，raw包、item结果及完整包hash齐全。 |
| AC10 | R3/R5、W06/W08 | 多item部分成功/保序、失败范围不变且非PDU全原子；非白名单系统操作明确拒绝/关闭、无DS/宿主副作用，不接受“成功空操作”替代。 |
| AC11 | R7、C01/C02 | 16真实S7会话同时读写、第17条20次拒绝不抢占；计数从TCP/H到C/closing/释放逐态对账；1–64/>16未测及全局128/32/160与64线程关系准确。 |
| AC12 | R7/R8、C03/C04 | H满/握手、绝对半报文、正常idle、真实慢接收send及释放期限均有起算和原证据；未实际触发send不报通过。 |
| AC13 | R8、C04 | per-connection/instance/global数量和所有阶段bytes/最坏输出预留先准入，超限无item执行且归还一次；小预算/故障注入与实际大上限未触达准确分层，owner无网络/磁盘等待。 |
| AC14 | R9、C05 | 连接与工作类按item轮转/保序、规则合并、A/B低频及UI/普通控制/stop可达；正常60s内A/B各120请求全完成、60次合法UI全成功，不能靠准入外全拒绕过公平。有资格和调度轨迹、逐连接分位数/拒绝分母及恢复回落，不能仅总吞吐。 |
| AC15 | R2/R10、D01 | 精确DAA ManagedS7真实feature、RemotePort/rack/slot/COTP/读链与240次db_read可定位；不改DAA、不读真实env/profile、上传关闭；模块级与完整产品界限清楚。 |
| AC16 | R7/R10、D02 | 错TSAP/端口、双端口身份隔离/端口冲突/重复start负例均可复现，不回退102/抢占/隐式复用；私有API/feature不满足时blocked而非换fixture。 |
| AC17 | R4/R9/R11、W09/X01 | stop/单close先封准入取消未入段，仅当前不可取消item完成；未知回执与确定拒绝分开，无回滚/自动重试，超时不假stopped，其他连接/实例继续。 |
| AC18 | R7/R11/R12、C06 | 160重连、20启停、3reset有原始序列；socket/callback/worker/timer/队列/预留回B0且可同端口重绑，重复释放幂等，RSS/线程/句柄按定义无超额增长，保值/初始化语义不混同。 |
| AC19 | R2/R11、X02 | 若选sidecar则父子正常/异常退出与A/B崩溃隔离3轮证据满足5s边界；不选时理由与进程内native风险可审阅，不把G0管理harness当Tauri原生/三平台证明。 |
| AC20 | R2/R12、全矩阵 | 每run source/ABI/环境、raw item/bytes/事件/错误、1Hz资源和状态转换可关联，offered全分母、逐连接p50/p95/p99/max、CPU/RSS/线程句柄/队列/规则missed/stop均报告；C01/C05算术正确，证据缺口不算pass。 |
| AC21 | R1/R13/R14、§9/§10 | go/no_go与case/QA/Owner层次分开，fail/blocked/not_run/deferred真实；候选失败或改范围回PM，不把004/G0/文档检查当产品批准；既有文档/并行dirty/旧receipts保护，DEV与新fresh QA逐角色真实建立。 |
| AC22 | R2/R10/R15、§2.1/§2.5/§2.6 | accepted manifest SHA、60/61同字节与1项CODE_INDEX允许导航差异、core0.1.0/API/profile/v1及五DAA模块/新增引用图可核；新锁静态66registry+1path与未运行解析图分开，路径真实消费、无stub/DAA改动。 |
| AC23 | R16、§2.7设计验收 | canonical增补明确多文件/逐DB UDT闭包和绑定；DeclarationRef非稳定ID，DB号/文件序号非主键；lineage/ID/reimport/CAS/结构停机变更及每instance32DB/4096叶聚合限制可逐项审核。产品消费者case留D1，不伪称G0已实现。 |
| AC24 | R5/R15/R16、§2.7设计验收 | 受限嵌套标准布局理论辅助与STRING整DB拒推、人工确认/coverage/完整instance NameBatch、原字符串碰撞规则/v1样例pin准确；初值零缺省/显式优先、数值范围/大端/BOOL/CHAR/STRING边界齐全，无TIA初值/实机地址/自造oracle承诺。 |
| AC25 | R6/R11/R16、§2.7设计验收 | saved/selected/loaded分离、停机apply/同版幂等/commit未知、九场景typed保值/初始化、页面动作→服务→单owner路径及日志降级一致；D1–D4与Tauri/FFI单owner待独立实施门槛明确，无双image/双规则。 |
| AC26 | R2/R14/R17/R19/R20、§3.2/§3.3 | 正式D/R/S文件/八vendor限制、实际五模块路径/core三级相对依赖、Rust库/桥/CMake源/role build/bin路径可核，正式source全manifest与DEV/QA候选/生成产物SHA闭合；无仅tmp交付或旧PATH/C++业务server替代。 |
| AC27 | R13/R18、§3.4/§10 | protocol-baseline交接具版本/入口/固定端口DB编码权限marker/限制及全部适用G0证据、fresh QA/Owner事实；未齐仍candidate，no_go不能伪称server。真实DAA应用→SQLite另批，超profile先另spec扩并验收，整体B/C边界准确。 |
| AC28 | R12/R14/R17/R21、§3.2/§3.5 | 必要raw/原命令/build/失败证据由T校SHA持久到A及逐成员inventory，P只5类紧凑清单/索引并被tasks/checklist定位，无raw日志/构建产物入公开repo或仅记hash后删raw；A保留至联合验收后复核，资源归属/回收依赖真实，正式D/R/S与旧证据不当tmp清理；当前仅PM spec，r1/r2/r3可逐字恢复、1820读时起点保护及foreign/shared delta如实分类。 |
| AC29 | R4/R6/R9/R19、W01–W09/C05 | 真实调用图/修改diff与Rust测试+wire表明所有image mutation、来源/CAS/规则/公平/控制/预算只在同R库；C++6源已按归档后退役且不在link/source图，无第二image/业务scheduler；Tauri与Rust独立server消费同一库。 |
| AC30 | R2/R3/R8/R11/R19、B0/W06/W09 | 新C/Rust桥双向int0/非0、Tag20B/align1/字段offset、callbacks version/size、借用/回调计数、异常边界、pthread_join与Rust join证据齐全；全PDU输出预留/逐item顺序/真实失败不降。缺入口/有限性失败no_go，不重写协议栈。 |
| AC31 | R2/R14/R17/R20、骨架检查 | 37DAA源/17CU/core/新Rust roots/548-bank子图及前端integrity固定；DS名称/identifier/keys/profile/dev端口隔离、无采集/SQLite/旧IPC；前端build+真实Tauri native3次启动关闭及只读IPC成功，无自动S7监听，资源独立留证据。完整产品/installer/三平台仍排除。 |
| AC32 | R12/R13/R17/R21、B0/C01/C06 | r3原99源/原spec/必要诊断先A持久校SHA，6旧源再退役，不只留hash；r3停止/19not_run事实与r4独立运行分开。Rust/native100次同clock夹点、Python跨进程区间/phase窗口、失败保守计时无伪比较；原case/算术/阈值不变、新fresh QA独立重建可复现。 |

## 9. 风险、回退与明确排除

| 风险/未决gate | 处置与Owner需审阅的取舍 |
| --- | --- |
| native回调、ABI或默认系统命令不满足 | §2已完成只读筛选；有限扩展先经B0审查/ABI，未闭合不开始协议。返回值/内存入口/拒绝不可控即淘汰，不以回写或成功空操作豁免。 |
| native hook锁/线程/缓冲隐藏，16能连但不公平/不能退出 | C/H/queue/资源可控点是必证；任何不能有界释放/观测的关键面阻止go。通过16也不证明>16或L1–L5。 |
| DAA真实入口与fixture隔离机制不兼容 | 推荐固定真实模块的隔离消费，不改当前DAA；无法安全调用则blocked并申请独立DAA范围。不能利用默认env/生产profile或同名重写client消除blocker。 |
| 原生库/sidecar崩溃影响其他实例 | 先明确实际进程边界；选sidecar须X02，进程内硬崩风险保留并由Owner决定后续隔离。不能用逻辑隔离作OS崩溃隔离。 |
| 静默拒写试验被规则/合法并发污染，或先写后恢复伪通过 | 屏障、不变基线、mutation入口事件及源码链同时使用；并发按item/范围对账，证据无顺序或丢失则blocked重做新run。 |
| 单OS/短程和缓存包被当跨平台/长期能力 | r3仅编译/无端口诊断且未闭合，r4新增Rust/骨架构建/ABI/native/19case尚not_run。G0只报告冻结OS与有限profile，目标平台/发布及长负载另批。 |
| Rust FFI/骨架新增风险 | packed字段/整数ABI/线程重入/错误传播/生命周期必须B0与wire证明；无Rust所有权证明不采纳。Tauri新增依赖/本机WebView/cache需要独立观测，不抬server资源阈值或带入DAA业务。 |
| 选型趋向大规模协议重写/依赖升级/产品实现 | 当前draft不实施；未来超小adapter/两候选/指定矩阵的工作回PM新Revision，不继续扩写。no_go可以是可信交付。 |

回退只处理本任务明确delta或未来获批owned实验资源；本轮仅spec可逆修订，不reset/覆盖已有工作树；未来迁移仅已获批且先归档后退役6个自有C++业务源。未来实验失败先封准入、按真实提交边界退出、保留错误与原证据；只清理已确认归属且不再承担证据/后续依赖的资源，由主协调收尾，QA不回收。端口冲突不碰占用者；旧004/DAA证据不得删除或改写。

以下排除实施，§2.7设计增补不授予产品权限：超出§2.8最小骨架的完整DS产品工程/页面/安装包、导入器/点位编辑/配置SQLite/schema/迁移/持久apply/运行值保留九场景、完整DAA采集/历史/上传及DAA修改、Backend/SMA/CA/真实PLC/现场网络、生产数据库/API/上传、Modbus/完整PLC执行或协议栈、长期服务/后台守护、完整L1–L5/8×16扩展、三平台native/发布部署、Git refs/提交/推送、外部消息。G0可用合成内存fixture证明init/reset/stop保值路径；不能把它扩成配置恢复实施。

## 10. 当前批准事实、历史与角色交接

| gate | 当前事实与下一步 |
| --- | --- |
| Owner路线约束 | runtime必须Rust，底层C/C++协议库允许；DAA工程基础派生、独立S7模拟器定位明确，无纯Rust协议栈选择待问。 |
| 本精确r4执行许可 | **approved, 2026-10-20**。Owner按§1逐字原话批准草案SHA bdd354dd9716a55289953d6d8cb3b46457877101d93550843aaaf250125fee4b的精确r4，当前交接Development；本次PM只登记，不代实施/QA。 |
| r3原件与停点 | r3已批准且执行后安全中止，99正式G0源/必要诊断保留，B0未closed、无listener/PID，19case全not_run。既有tasks为r3读时事实，不能被PM伪同步。 |
| Rust/native可行性 | 输入已足够形成此具体r4方案，可获批后开始B0；原样native/Python no_go，Rust正确int bridge+八文件扩展仅proposed，Rust业务与新依赖/native骨架均未证实。写前/预算/资源不可控则no_go，不以骨架或共享core已接受替代。 |
| 接受链 | Owner精确r4范围/风险批准→实际Development先归档/派生/Rust及设计同步/B0/骨架/G0→developer_handoff→新的fresh-context Verification→Owner最终接受。协议baseline未齐仍candidate，研究no_go可接受但无可交接server。 |
| 后续B/C与产品 | D1共享导入消费者/配置SQLite、完整D2/D3/D4另spec；真实DAA应用S7→SQLite另批/独立核验/Owner关闭整体B；C不开展。 |

历史：r1批准SHA00171a…、r2未批准SHAfc0ab9…均在附录内完整；r3批准原话/草案SHA与已登记SHA见§1，r3仅编译/诊断后被Owner路线纠正中止。r4草案已于2026-10-20获上述精确批准；所有r3既有编译/诊断作为未采用研究保留，不倒写为未发生或Rust实现/QA/终验。附录A的r3全文SHA固定，可逆提取后其嵌套r2/r1继续原字节恢复。

PM实际读取aiis/project-governance、rust-runtime、desktop-tauri及相应跨语言/日志/官方基线，当前contract_only；串行角色/精确范围/diff审计是合同控制，不宣称ACL/强制路由。未来DEV按此r4实际面继续rust-runtime+desktop-tauri；派生Vue/文案须frontend-ui+i18n-workflow，新增源码/索引遵code-document-indexer，点/地址/类型用plc-point-mapping但命名/样例仍精确core0.1.0/v1，不引入通用XLSX/YAML合同。无backend/Celery/真实DB维护范围。

PM交唯一主协调已批准精确r4/SHA/批准delta与自检后停写；协调机械同步根4索引并串行启动实际Development。Development只按已批准正式D/R/S/角色路径新增r4 tasks事实，保留r3原历史与输入；完整developer_handoff后新的fresh-context Verification（fork_turns=none）独立重建/原case复现/骨架核验并创建checklist。QA只验证不修实现/DEV工件，Owner最终接受及P机械状态同步按原接受链。不得把r3批准、004设计接受或DAA006接受充当r4执行/QA/产品批准。

Human Owner exact ARCH-AW-005 r1 scope approval: **approved, 2026-10-19**。

Human Owner exact ARCH-AW-005 r2 execution approval: **never granted; historical draft**。

Human Owner exact ARCH-AW-005 r3 scope/execution approval: **approved, 2026-10-20; execution stopped for Owner route correction, not accepted**。

Human Owner exact ARCH-AW-005 r4 scope/execution/risks approval: **approved, 2026-10-20**；逐字原话及原草案SHA见§1。

At approval recording: r4 scaffold/Rust build/ABI/native startup/G0 19cases: **not_run**；r4 Development / fresh Verification: **not_started**；r4 protocol baseline / Owner final acceptance: **pending**。后续执行/独立verdict以tasks/checklist实际记录为准，本批准不提前填写结果。

## 11. r4草案阶段PM自检与未执行项（历史）

以下保留草案交接时的检查/未执行快照及旧receipts，不能因取得执行批准而倒写成实现或QA通过。

本轮以pm-r4/role-start.json的1820文件读时SHA及spec-r3-original.md为起点，辅助readonly-source-audit.json固定37DAA派生源、17CU、548 registry bank、99原G0、r3停点及真实pin；重要事实/路径/限制已在正文，tmp不是唯一执行依据。完整消费当前AGENTS、根/最近README/PLAN、完整005现bundle与DS正文、DAA真实入口/包锁与所需shared/CU源、实际pm TOML/canonical workflow和四skill。PM只写spec及指定pm-r4辅助材料；所有后续实现/索引/接受仍属对应角色/协调。

必要文档自检限stdlib：R1–R21/AC1–AC32映射与19原case逐字保护、所有原数值profile/算术、r3完整235629B全文SHA与嵌套r2/r1恢复、local links/anchors/表头宽度/围栏/尾空白、source pins/相对依赖路径、D/R/S/T/P/A及未来命令清单一致性、当前工作树单spec delta及旧输入保护。实际命令/退出码/限制、差异/原文恢复指纹及最终SHA在pm-r4/document-self-check.json、spec-r3-to-r4.diff和receipt.json。仅PM文档检查，不是G0 verdict或独立QA。

本轮未复制/删除/归档正式源，不创建R/T4/A4/骨架/依赖/锁/P/schema/SQLite，不改tasks/checklist/正文/代码/索引；未安装/构建/运行Cargo解析/ABI/native/浏览器/监听/PLC/DB/API或联调，不启动其他角色，不清理旧资源/其它任务或发送其它会话。r3停止事实与本轮只读/文档自检严格分开。

### 11.1 精确r4批准登记检查

本次仅改批准元数据、当前gate和真实批准历史，不改Revision/技术范围。以`execution-coordinator/r4-approval/protected-start.json`的1822文件/12份before为起点，在其`pm/`保存批准delta、必要一致性/链接/空白检查及receipt，确认21R/32AC/19case、全部技术正文与r3/r2/r1原文保护。旧pm-r4及所有旧证据不改；本次未实现、构建、安装、ABI、监听或启动后续角色，Owner跳过邮件的要求保持。完成后PM停写，主协调按既有批准链交Development。

## 附录A. r3已批准后中止的完整原文（内含r2/r1）

以下六反引号text围栏内为批准登记后r3完整原字节，SHA `7ec38de52749257b61cc9eb23db25733cd52d0f82657efa8e88110c741012a81`，235629B、1235行、UTF-8/LF含末尾换行。其r3批准/当前时态为当时事实，后续路线纠正与停止见active§1；不能把历史C++方向继续当r4许可。原五反引号r2/四反引号r1嵌套内容与指纹可逐字恢复，不修改历史迎合新路线。

<!-- BEGIN R3 EXACT SNAPSHOT -->
``````text
Task ID: ARCH-AW-005
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved exact r3 on 2026-10-20; hand off to Development for the approved DS design sync, formal-source B0 and bounded G0, then fresh-context Verification and Owner final acceptance; DAA–DS S7-to-SQLite integration remains separately gated and Stage C excluded
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS G0 有界技术原型、正式源码交付及可交接有限S7基线；附整体设计刷新要求，不含产品D1–D4实施
Owner: Automation World
Acceptance Chain Reference: ARCH-AW-005 r1 scope approved -> r2 unapproved draft -> Human Owner exact r3 approved 2026-10-20 -> Development design sync/B0/G0 -> new fresh-context Verification -> Human Owner acceptance; DAA–DS S7-to-SQLite joint validation requires a separate approval and QA/acceptance chain
Depends On: aiis-ics-arch::ARCH-AW-004 r2 accepted design; aiis-ics-arch::DAA-006 r3 accepted source manifest
Related Task: aiis-ics-arch::ARCH-AW-002; aiis-ics-arch::ARCH-AW-003; aiis-ics-arch::DAA-002; aiis-ics-arch::DAA-003; aiis-ics-arch::DAA-004; aiis-ics-arch::DAA-005

# DS G0 技术原型与整体设计增补规格 r3

## 1. 本轮授权、增量与当前gate

2026-10-20（Asia/Shanghai），Human Owner在本唯一协调会话要求的范围由主协调转交为：DAA-006 r3已最终验收，DS直接复用已固定的shared/tia-import-core及样例；先刷新G0旧指纹/依赖、补齐DS整体细节并重新分析开工条件；G0/可联调协议基线走DS审批，DS验收后另批真实DAA应用S7读取至SQLite及fresh QA关闭整体B，C排除。本段是草案形成时的授权摘要，非编造逐字引文；当时只授权PM形成具体r3草案，后续精确批准见下文。

批准关系保持真实：2026-10-19 Owner原话“可以，批准 ARCH-AW-005 r1 spec。接着完成 P0 只读核查，明确候选服务端版本、ABI、依赖、真实 DAA 入口和端口，补齐精确执行范围并整理成 r2 spec，先不改代码、不运行原型。”对应r1 SHA `00171a46325c1b28359e77b3d2a42434e1ad43ac825b16cdb84f1708695c4c84`。r2 SHA `fc0ab9a11b4145b994bc3586e014ef87b98148b87c3d2f6a53a65204f4d6379b`始终未获执行批准，未创建tasks/checklist或运行原型；本r3草案形成时同样待明确批准，已于下述日期获得精确批准。附录A原字节保留710行r2，内含可恢复的283行r1；历史批准/未批准不相互转移。

本r3保留原14R、21AC和19case的写前拒写、16会话、全PDU预留/公平及真实pthread_join门槛，增加R15–R18/AC22–AC28：固定共享来源/真实新增编译闭包、具体设计增补、正式源码及持久证据、有限协议基线交接。任务仍为root/无Parent Task ID，接受链独立；004文档接受及DAA-006接受均不是本G0已通过。原样Snap7 1.4.2不满足，有限扩展仍仅proposed_for_B0，不承诺必然可用；不因Tauri预设Rust协议核心、不把参考Python当Rust实现。

**DAA技术输入前置已解除，精确r3已获Owner批准，当前交接Development；服务端候选仍未go。** Development可创建tasks、同步§2.7设计增补并先执行§3的正式源码/B0；B0闭合后才W/C/D/X有限G0，不再等待DAA同一输入任务。D1导入/配置、D2产品运行核心、D3页面/native及D4长负载各须后续独立spec；本r3只定义其设计/前置，不实现UI/SQLite/完整DS。批准登记时全部19个运行case、ABI/构建和协议能力仍not_run；后续真实执行与独立核验由tasks/checklist记录。

2026-10-20（Asia/Shanghai），Human Owner在本唯一协调会话明确批准**精确ARCH-AW-005 r3**，对应批准前草案SHA `bd2df8339f904aec4744b6d0d254fa9becc2bdd0ac53a5e90c43447261341379`，逐字原话：

> 可以，按独立 S7 PLC 模拟器定位。批准 ARCH-AW-005 r3 spec，接着同步 DS 详细设计，完成 G0 实现、验证和独立核验，形成可供联调的协议基线；DAA–DS 读取至 SQLite 联调另批，阶段 C 暂不开展。

“独立S7 PLC模拟器”澄清既有有限standalone方向：工程归属AW，运行不依赖DAA/SMA/Backend；其它兼容S7程序可在经实证的有限profile内使用，不新增客户端/类型/完整PLC支持承诺或扩大G0。上述批准覆盖既有精确r3范围与风险，不等于已实现、运行通过、独立QA或Owner最终接受。技术正文中的“获批后”前提已由本次满足，B0/协议/QA/最终接受各gate仍按原合同串行；“本轮不执行”“当前draft”等草案阶段/PM角色叙述保留其原时点事实，不阻断获批Development，也不扩大本次PM登记权限。

## 2. 来源刷新、选型约束及整体设计增补

### 2.1 固定设计、已验收共享来源与读时事实

[004 spec](../ARCH-AW-004-ds-detailed-design/spec.md)、[tasks](../ARCH-AW-004-ds-detailed-design/tasks.md)和[接受记录](../ARCH-AW-004-ds-detailed-design/checklist.md#owner-acceptance-r2)保持原样。497行[DS正文](../../docs/AIIS_DS_Detailed_Design.md) SHA `0eb3c149bf7093bbdce2f0b7a07af71e769fe24cb04a542c7f4dc43e6979eecb`是004已验收设计快照；本轮不修改。§2.7是005 r3的增补提案，批准后Development才在同一canonical正文标明005来源同步，不重开004、不将新增内容倒记为004旧QA/验收。

[DAA-006 accepted-source-manifest](../../automation-world/data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/evidence/accepted-source-manifest.json) SHA固定为`8d9d62457baa32aac8134df77773ea5cae23a0401e403ef1d4c267cdafc02ee7`；本轮逐文件只读核对61/61 acceptedFiles与live SHA相同。它包含独立AC01–AC20 QA、另行DIRECT UI层和2026-10-20 Owner接受事实，各层不混称。本spec冻结**该清单的脏工作树文件**，不是HEAD/tag；其中HEAD `0af5b91177f3bca63f9f3c2bef9f14004ea49944`不能单独还原验收交付。源漂移即blocked并回PM，不自动采用latest DAA。

直接复用[共享core](../../automation-world/shared/tia-import-core/README.zh-CN.md)：aiis-tia-import-core **0.1.0 / Rust2021 / publish=false / std-only**，coreDeliveryManifest SHA `205f00ecf946246dfc7c2268eb60912733fb7fb1e52405e9174a5ea5996b1812`。六API为scan_sources、expand_db、layout_standard、plan_names、validate_manual_name、type_suffix；profiles固定tia-subset-v1、siemens-step7-v20-standard-word-v1、tia-point-name-v1，fixtures v1。不fork parser/命名/oracle，不复制DAA业务存储/ID/运行系统当共享能力。

| 固定共享输入（前缀automation-world/shared/tia-import-core/） | SHA-256与用途 |
| --- | --- |
| `Cargo.toml` / `Cargo.lock` | `a82f221d1d6baab2aa9bfb0c5cf084847768d0d5d34d747c912420d549bd5cb1` / `4ac1935bee10dde4638df61833f07d95008ae5853f8e630afc2019ee76769502`；无registry依赖。 |
| `src/lib.rs` / `src/model.rs` | `d69e0cabfec5c1cb98334fd3a3038d21c318a30687d155d8ade8f1d0e6fc5d5f` / `1347c9a2cb6ba102861229432f602ff7bebb4e83fc1e75cee387c901f24bca31`。 |
| `src/parser.rs` / `src/layout.rs` / `src/naming.rs` | `1513cef43324868f73a191c5b15cc4398ac0fc6fab400de516f95f7e0fa5a6e9` / `316ce3ae0c3511e12291dd460702cedfe403ec7e2120b4314dce0b6fe8bf793e` / `122ceb9b88fad2bb10ae495985fee3b6b4d5cc5ce3460b207d9c2ab26e968fe2`。 |
| `fixtures/names.db` / `fixtures/names.udt` | `769ebebc825bfa321de71a0a931012f5d6d0f1fe135da4b028cc6e9b78cf2586` / `8a5e470b2668f85aff8b7ba01c22c06b341ef044fbd4d31d1ec8e0f48ec02250`；共享导入样例Names28/60/47映射28/60/47。 |
| `fixtures/expected-v1.json` / `fixtures/daa005-layout-oracle.json` | `397fb68d8053f2adef41aa5a63cd8e53673e90174532a0def6db985aca913977` / `2f2f6fe79eea60b48357b72f8a4f352016da4c8d95220ba2e06005133c24e633`；[v1说明](../../automation-world/shared/tia-import-core/fixtures/README.zh-CN.md)，逐字固定，不用tested code再造期望。 |

**两套夹具分层**：上述v1用于未来D1的DS导入/命名消费者验收；G0继续使用§5的专门DB41/57权限、并发、资源合成夹具，不声称由v1导出。G0 Rust client因domain闭包链接core只是消费真实DAA模块的编译前提，不证明DS已实现六API导入。共享core不含初值、encode、存储/稳定ID/reimport/runtime；STRING解析可用但layout_standard遇STRING使整DB失败，不能跳过该叶继续推算。

宿主完整硬件/clang/CMake/SDK资料仍为r2的**2026-10-19历史快照**：macOS15.7.7(24G720)/arm64、Apple M4（proc 10:4:6/逻辑10）、RAM32GB、clang17.0.0、SDK26.1、CMake4.0.2/Make3.81、Python3.9.6；SSD/内核动态端口段未核。本轮2026-10-20 14:44 +08窄刷新：绝对stable rustc/cargo仍1.89.0、aarch64-apple-darwin/原commit未变，lsof三口exit1空输出，仅未观察LISTEN，不是预约/bind证明。执行前B0仍须复核工具链/完整资源和背景负载，冲突即失败，不自动换口。

### 2.2 精确候选、包来源、许可与推荐顺序

本节及§2.3/§2.4承接2026-10-19 r2的冻结源码研究；其中下载/403/cache等“本轮”指该次历史采集，r3未重复官方研究或运行库。固定包/ABI/八文件门槛保留，未来有效源码路径已改为§3正式S，不执行旧tmp源码方案。仍无已合格候选。

| 顺序 / 精确输入 | 只读证据与决定 | 后续边界 |
| --- | --- | --- |
| 首选试验候选：官方Snap7 **1.4.2** 源包 `snap7-full-1.4.2.7z`，20591252B，SHA `1f4270cde8684957770a10a1d311c226e670d9589c69841a9012e818f7b9f80e` | 本轮从[官方SourceForge包](https://sourceforge.net/projects/snap7/files/1.4.2/snap7-full-1.4.2.7z/download)只读下载，完整包SHA与发布页相符；只提取源码/许可为数据，未提取/加载发布二进制。选旧版的明确理由是能核到真实resourceless返回链且与DAA固定crate内关键native文件同字节；不是宣称它是最新版或已支持arm64。 | **原样版本no_go；有限扩展方案仅proposed_for_B0，尚非adopt/go**。只允许§2.4的server私有副本改动；先B0可编译/ABI及有限性审查，再P1。不能用源码下载成功当ABI/安全/性能通过。 |
| 至多一个备选：python-snap7 **3.2.1** sdist `python_snap7-3.2.1.tar.gz`，295424B，SHA `15748f8423e3726457f6c4d0202aabde4ad65f2b809c2c1e7ee4f2f776509c2b` | 本轮[PyPI元数据](https://pypi.org/pypi/python-snap7/3.2.1/json)与其sdist的SHA吻合；[版本化API](https://python-snap7.readthedocs.io/en/3.2.1/API/server.html#snap7.server.Server.set_rw_area_callback)及冻结源码均显示rw callback为stub。`_handle_write_area`直接改registered memory并构造单item成功，stop先报STOPPED再有限join/清列表；源码尚无本合同的多item/完整预算/释放保证。 | **该精确备选no_go，不进入构建或运行**。修成合格服务端需改写超出小adapter的处理面，本r3不授权。首选失败后无自动合格备选；回PM决定新Revision，不偷偷改Python/DAA或自研协议栈。 |

官方项目当前[1.4.3说明](https://sourceforge.net/projects/snap7/files/1.4.3/)指向[官方GitHub](https://github.com/davenardella/snap7)，其可变main/新版本不在本r3选用面；未来换版须新Revision。官方[resourceless](https://snap7.sourceforge.net/res_servers.html)、[server规格](https://snap7.sourceforge.net/snap7_server.html)与[API](https://snap7.sourceforge.net/snap7_api_ref.html)仅辅助说明；实际决策以本节冻结1.4.2源码为准。

许可材料：原生源头声明LGPL-3.0-or-later，包内`lgpl-3.0.txt` SHA `ea7d049c7705dc13afc202dd18e1827f3484f8212fd3fa7b82fc4a0c363432c9`、`gpl.txt` SHA `0b383d5a63da644f628d99c33976ea6487ed89aaa59f0b3257992deac1171e6b`；Python包LICENSE为MIT、SHA `3c88a113fc8ffbc81cf9f7fd8a4bd040f39ad1b88e099e8173eea1dc6df14544`。DAA所用rust-snap7包manifest声明MulanPSL-2.0（LICENSE SHA `89591a592b25a07a294c67c0767bb2b061a60e544d76f4bbc438192882f34e92`），其build.rs头另写GPL-3.0-or-later、native另有LGPL，B0保留全部原许可/源材料及链接清单，不据顶层单一license字段作分发许可结论。本G0仅owned本地实验，不发布/再分发。

以下为官方包内**必须保持原始起点指纹**的关键源码；整个包SHA固定其余文件，B0另生成全source manifest及有限patch的before/after/diff，不能只交这些摘要。`src/`以下路径相对`S/vendor/snap7-1.4.2/upstream/`。

| 相对原生路径 | SHA-256 |
| --- | --- |
| `src/core/s7_server.h` | `ebfe5f185c904624cc74b10419c454001c27b37a3ffbec7b0232ae2c494c1ecc` |
| `src/core/s7_server.cpp` | `e1007486fbf2c738e01628dd4e394de32af08a772227f3e3d07dc4437b128ad3` |
| `src/core/s7_types.h` | `feb97ffb241494f13db231e39fcb48a879efda74e7e240caddcb07139a92f300` |
| `src/core/s7_isotcp.h` | `313c5167f3769367b38073c62da6d1a1c49b63a7016016caf3743666639a2c5f` |
| `src/core/s7_isotcp.cpp` | `7c06fa33f0e34afe88962322c5fa946f3072ceeb1a0cc5d2cbdb71c7ac43e6b7` |
| `src/sys/snap_platform.h` | `d7f4e9dc2e5af523258437ae22c6109c98aa5b263881db16479fa5dfed884b47` |
| `src/sys/snap_msgsock.h` | `570f97d27da11dcc08650897a5dd27bc939a53598dc15d45c85b64366ca1e0c3` |
| `src/sys/snap_msgsock.cpp` | `bded0cc9e642aaff22b8a16e0bfae5f5eca7e346769ec6f8ba582b00bae9ba51` |
| `src/sys/snap_tcpsrvr.h` | `0a2d8d354b2d78a3155633b5e4bcd7b4f88937aa8ed7afe3a1d832995feafba4` |
| `src/sys/snap_tcpsrvr.cpp` | `b6365fddff816d4c3faf6b7d40c56e394e8ca0aa7c2bca16b3431d12d11eb747` |
| `src/lib/snap7_libmain.cpp` | `3e4a186471b41ead3a80e2d6ce94cec1e7ccc17920b6936a07ead14b274bd643` |
| `release/Wrappers/c-cpp/snap7.h` | `3e2a4edd86b5adfa4a73f64c81d0e0f1316df1da54785fa61dd293f728c4c401` |

Python关键文件`snap7/server/__init__.py` SHA `d17a8c1a5a9b96154d9882d3fc3766fb2c53c35af5f5b7c5aebf95b8f2c40e72`只作no_go证据，不是未来改动路径。

### 2.3 原生C ABI、提交时序与尚未通过项

冻结头`s7_server.h`定义`extern "C"`内的`int (S7API *)(void *usrPtr, int Sender, int Operation, PS7Tag PTag, void *pUsrData)`；macOS的`S7API`为空，按目标C调用约定，Windows分支`__stdcall`不在本次验证。`s7_types.h`在`#pragma pack(1)`内定义TS7Tag五个int：Area/DBNumber/Start/Size/WordLen；目标**待B0实测**的sizeof(int)=4、Tag size20/align1、offset0/4/8/12/16、pointer8。OperationRead=0/Write=1。C++harness直接使用原native头和**返回int**的callback，不手写另一套FFI布局；任何不符即blocked/no_go，不能调整探针期望掩盖ABI差异。

已核1.4.2源码链为`TIsoTcpWorker::ExecuteRecv -> TS7Worker::IsoPerformCommand -> PerformPDURequest -> PerformFunctionWrite -> WriteArea -> TSnap7Server::DoWriteArea -> OnRWArea(...) == 0`。resourceless下callback返回0才使WriteArea生成0xFF item成功，非0走`WA_NotFound/Code7ResItemNotAvailable` item失败；PerformFunctionWrite逐item填结果，再isoSendBuffer响应。**callback非0不能精确映射自定义权限错误细分码**，G0接受真实item失败而非假成功；W06仍要求逐item部分成功。read链使用DoReadArea/callback填worker响应stage再编码；RegisterArea路径会直接mask/memcpy共享区，G0必须禁止注册image/裸指针。events是在处理之后，不能当拒写入口。

Tag是callback栈对象，pUsrData为该worker的请求/响应buffer借用，均只在同步callback返回前有效；写数据必须在预算内复制成owner请求，不把Tag/原指针交给异步队列；读快照复制回原stage后才返回。usrPtr及hook上下文存活到所有callback归零且worker已join；异常不得跨C边界，失败返回非0，不能在commit后因日志失败改回失败。Sender来源是peer地址/ClientHandle，**不是连接唯一ID**；同loopback多连接必须用accept分配的connection ID、worker上下文及受控TLS item/PDU关联，不按IP或Sender授权/计数。

rust-snap7 **1.142.2**固定crate SHA `8c4d43b3a99825abd300d57a0888eda7b625b7cdbf56ee7766bd02331ac58243`已从现有cache完整包计算，与冻结DAA Cargo.lock checksum相同；关键native server/type/socket文件与官方包相同。其`src/server.rs` SHA `e46c5f1400e1e36a65dcfff9810e39f338cf959f85675145041225ae5dbd9ee2`中的FnMut/trampoline及`src/ffi.rs` SHA `3b64e4ea1aa470ad6f37e9672c070a96fb1f60bda76d964f6b1636e406a0f465`的pfn_RWAreaCallBack返回void，不能传回native所需int。**不采用该高层server、不在DAA依赖内修FFI**；该crate只用于原DAA真实client。crate缓存完整性与冻结项目锁相符，独立crates.io元数据获取403，未声称已获第二注册表证明或已可构建；该限制保留，B0仅可用匹配既有锁的包，不能联网换版本。

### 2.4 未修改上游的缺口及有限扩展提案

原样native虽有写前int链，但公开MaxClients只数TCP worker（0还代表无限），DoReadArea/DoWriteArea的全局CSRWHook包住callback；ISO连接默认回CC、S7协商原样echo AMQ，系统分支会处理CPU/clock/SZL等；SendPacket一次send/RecvPacket分段超时不能提供本合同绝对期限；TerminateAll超时会KillAll并清ClientsCount，Stop随后直接报stopped。因此**原样native no_go**，不能靠set_param/一个写callback进入P1。以下只是可审查的有限扩展提案，尚未实施或证明足够。

未来只在`S/vendor/snap7-1.4.2/controlled/`修改表中八个原生文件；调用点附近增加guard/hook及server限定IO/生命周期修复，不改wire format、S7 item编解码或建立另一处理循环。全PDU descriptor/typed准入/公平在独立harness中完成，native原有解析/编码继续复用。**若实际需要迁移/替换ISO/S7主循环、修改本表外原生文件/DAA crate、重写TSnapThread框架或自行补完整协议栈，该候选停止no_go/blocked，回PM新Revision；不得以“adapter”称呼掩盖重构。**B0先出完整diff/调用图/控制点覆盖，未能证明有限性不得开始协议运行。

| 精确文件与原有函数/位置 | 最小必要改动及可审查结果 | B0/P1以后仍须证明 |
| --- | --- | --- |
| `src/core/s7_server.{h,cpp}`：TIsoTcpWorker::ExecuteRecv；TS7Worker::IsoPerformCommand/PerformPDURequest/PerformPDUUsrData/PerformFunctionNegotiate | 在原路径前加入受控server hooks：COTP CR的calling/called TSAP检查后才CC；S7 setup前C/H转换容量检查及AMQ=1、PDU≤480；只白名单setup/read/write及有界disconnect，其他系统分支拒绝/关闭且不调用原处理函数。 | 握手真实C提升时机、错TSAP、所有系统请求均到guard，不能以函数名称或CC已发当会话成功。 |
| 同两文件：TS7Worker::IsoPerformCommand/PerformFunctionRead/PerformFunctionWrite，TSnap7Server::DoReadArea/DoWriteArea | 第一item前对整个PDU做边界/最多4items/最坏响应检查与原子预留，再让原item循环调用hook；item上下文记录connection/PDU/index。仅G0受控resourceless分支不持CSRWHook等待owner；配置callback只在封闭gate，native非G0行为不变。 | 预留失败item0也未提交；逐item结果/内部顺序及跨连接公平；所有byte仍只由owner提交，callback解除外锁不制造并发image写。 |
| `src/core/s7_isotcp.{h,cpp}`：TIsoTcpSocket::isoRecvPDU/isoRecvFragment/IsoConfirmConnection/isoSendBuffer | 透传server限定的frame/PDU绝对deadline与剩余额度；每frame≤512、重组总量≤480，分片不重置起点；暴露完整COTP参数给guard，不另写ISO解析/确认循环。 | 畸形/滴流、多个fragment、输入预算及错TSAP；若必须重写这些函数的协议处理算法即越界停止。 |
| `src/sys/snap_msgsock.{h,cpp}`：TMsgSocket::SendPacket/RecvPacket/WaitForData及server上下文 | server专用有界部分send/recv循环，monotonic绝对期限、停止唤醒/非阻塞剩余等待，首byte/首次send尝试采样；socket buffers设定并读回。client/default分支不改。 | 真慢接收send阻塞、短IO、断连、首次发送2s deadline；不能只设置SO_RCVTIMEO/每次调用相对timeout。 |
| `src/sys/snap_tcpsrvr.{h,cpp}`：TMsgListenerThread::Execute，TCustomMsgServer::CanAccept/Incoming/CreateWorkerSocket/Delete/TerminateAll/Stop，TMsgWorkerThread构造/Execute | 在原listener现有loop的SckAccept之前先预留H/TCP及全局额度；accept失败/准入关闭/创建worker失败均归还一次，不重写loop；成功后分配唯一ID并转交Incoming。受控worker保持FreeOnTerminate=false，在Execute内同步记录本线程pthread_self；reaper等其完成通知后，以该ID执行真实pthread_join，返回后才销毁worker/socket/回调上下文和归还名额；新增字段/方法仅在本行已列两文件内。stop先封准入和cancel未提交，已入段单item完成，唤醒网络并有期限退出；受控分支禁KillAll/提前清零/无条件stopped。 | macOS原创建分支为joinable，但TSnapThread的WaitFor/Closed仅为状态等待，不能作为join或释放证明，不读取unix_threads.h私有th、不改线程框架。真实pthread_join返回后才归还；超时保留stopping/failed/closing及所有权，B继续；重复close幂等。无法在这八文件边界完成即B0阻断，不把断连event/移出表当线程已退出。 |

预留公式在此固定：对PDU p，`Q(p)=I(p)+D(p)+S(p)+K(p)+O(p)`；I为保留输入（≤480B），D为每item固定描述符（最多4×64B，无隐藏动态成员），S为typed stage（总≤480B），K为额外payload复制（总≤480B），O为最坏响应frame预留（≤512B，含失败码/填充，成功与失败取较大者），即每PDU显式池上限2208B，第一item前全额原子预留。若native实额要求额外副本/descriptor超64B，必须增加实际charge且仍满足原上限，不能沿用2208隐藏存储。每连接Bconn=未完frame实际capacity+native固定/临时protocol storage+Σ已预留Q+其他实际副本且≤64KiB；native源已有4096B IsoPayload和4096B Answer，不能只按协商480B计。socket实际SO_RCVBUF/SO_SNDBUF另作受限OS资源预留/观测并在C04均≤16KiB，线程stack另列RSS。实例/全局协议bytes分别汇总全部未完/执行/queued/待发阶段的实际buffer和输出预留（≤1MiB/4MiB），不能只计queued；等待数量另限64/256PDU、实例1024items；同一backing跨阶段只转归属一次，新增副本新增charge。活动native buffer、OS socket与等待池分类列账，不能互相漏记。B0必须以sizeof/capacity/调用点核表并给活动+等待合计峰值，协议阶段再按真实socket读回/阶段事件核对；超限即阻断，不伪造尚未发生的实测值。

内存owner不能等待网络/磁盘；worker等待owner也不能持库global hook/list锁。每连接最多1个native执行PDU，可不启用额外等待PDU（上限2不是必须填满），OS未读bytes/socket buffer仍实计；不能用该实现选择减少r1 offered吞吐/公平目标。控制点缺失、预算无法观察或大范围改动都是阻断，不以测得最终值相同替代。

### 2.5 真实DAA新增编译闭包与实际消费路径

当前最小原字节模块闭包为以下**五文件+共享core crate**，不能保留r2“三文件足够”的结论。ManagedS7本身未改：RemotePort/PingTimeout/SendTimeout/RecvTimeout -> connect_to(host,rack,slot)；原read/read_bounded/disconnect/connected/Drop照用，driver开启/local-validation关闭/cfg(test)关闭，无FixtureTransport、截取Plc或近似重写client。

| 仓内只读源（前缀automation-world/data-acquisition-agent/src-tauri/） | SHA-256及真实新增边 |
| --- | --- |
| `src/infrastructure/managed_s7.rs` | `4ce9a9bfbe81c63453a6444d9b8e719fce6afa8e72ea84e0ca561dda8b48ca0e`；依赖local_configuration::{LocalResult,Plc}、rust_snap7。 |
| `src/domain/local_configuration.rs` | `af64ca7f52d336b096a4744dcf3f0398776204a0e86939eba1bbd8693e07d22d`；Db.import_binding引用source_import::ImportBinding，Point.name_mode/校验引用point_naming::NameMode与core::validate_manual_name，另调用local_sample::digest。 |
| `src/domain/local_sample.rs` | `a30a1909bd7b50ae26aa0cde27e9b193c82760ad7f940457107c31688f44f06a`；原serde/serde_json/sha2/chrono及local_configuration回边。 |
| `src/domain/source_import.rs` | `35f32c26eb3eb13e89c211354c6fdbfb9ecf94db379a8aef87138000f5b73654`；local_configuration/serde，ImportPreview又引用point_naming::NameChange。 |
| `src/domain/point_naming.rs` | `d60cab560b2f2047cc299b7ea62ba8b1978c754930af9d965aa444467332276b`；local_configuration/serde/std/aiis_tia_import_core，不依赖SQL/文件I/O。 |
| `Cargo.toml` / `Cargo.lock` | `6ca767c287b9118449027671684b3fd4dea5d4503d266d09a5d8cc22bd92c88e` / `0fd260eb50278b28e6b3a2e016dcc18ed6a4030b0c95a2a828db8ddcbfc05a61`；core path新边是实际依赖，不是仅更新hash。 |

正式G0 Rust入口位于`automation-world/device-simulator/g0/daa-harness/`。`src/main.rs`加载外部module domain/infrastructure；两个`src/{domain,infrastructure}/mod.rs`以外部`#[path]`直接消费上表仓内五文件，**不复制/编辑它们**。从domain/mod.rs到真实domain文件为`../../../../../data-acquisition-agent/src-tauri/src/domain/<上述四文件>.rs`；从infrastructure/mod.rs到ManagedS7为`../../../../../data-acquisition-agent/src-tauri/src/infrastructure/managed_s7.rs`。Cargo.toml的core依赖精确`version="=0.1.0", path="../../../shared/tia-import-core"`。B0须realpath核这些层数、原SHA及rustc dep-info；同crate pub(crate)可调用不等于已编译。任何字段/私有API或新依赖不满足则blocked，不擅改DAA/core或用stub凑编译。

feature仍为`rust-snap7-driver=[dep:rust-snap7]`、default=[]，local-validation声明但关闭；只构建独立binary ds-g0-daa，不执行cargo test或整个DAA应用。不加载domain/mod.rs总入口或LocalRuntime/服务/store/SQLite/Tauri/上传/Backend模块。五模块闭包中的导入/命名DTO被编译不代表本任务执行DS导入。

真实连接参数固定A=127.0.0.1:30102/rack0/slot1，B=:30103/rack0/slot2；原native client默认PG=1、calling0x0100、called=(1<<8)+(rack*0x20)+slot，所以期望0x0101/0x0102，仍须wire核。connect_timeout=1000ms、io_timeout=500ms、deadline_ms=5000；D01每轮原read(57,0,64)及原read_bounded(41,512,8,400ms remaining)，后者设置remaining/2截1–500ms的原socket超时；两连接60s共240次db_read。仅显式内存Plc，不自动读配置/真实.env/default profile、不启动应用/建DB。进程白名单只传DS_G0_RUN_ROOT、TMPDIR、CARGO_HOME、CARGO_TARGET_DIR和必要PATH/locale/绝对工具链，不改HOME/CODEX_HOME；不包含业务授权/DB/Backend/上传变量或这些模块。

### 2.6 语言/依赖冻结及静态闭包限制

G0仍为C++17 standalone受控server、原生reference client，加Rust2021真实DAA最小入口；Python3.9.6 stdlib只负责编排/数据/证据，不作S7server。C++依赖仅SDK libc++/libSystem/pthread及冻结Snap7，不引入通用JSON/DB/队列包。Tauri薄IPC与后续Rust配置服务不是本轮G0实现面。

Rust六个registry直接根保持精确`=`：rust-snap7=1.142.2、serde=1.0.228(derive)、serde_json=1.0.150、uuid=1.23.3(v4)、sha2=0.10.9、chrono=0.4.45(default-features=false/clock)；新增path根aiis-tia-import-core=0.1.0。从**新锁**静态追踪得到66个registry+1个path package；66个registry的name/version/checksum与r2逐项相同，新增core无registry依赖。以下列完整精确registry集合，checksum由上述新锁SHA固定；不是已执行cargo解析/feature图/构建，尚不能称67个全部实际链接。

| 静态闭包分组（全部名称+精确版本） |
| --- |
| aho-corasick=1.1.4；android_system_properties=0.1.5；anyhow=1.0.102；autocfg=1.5.1；block-buffer=0.10.4；bumpalo=3.20.3 |
| cc=1.2.65；cfg-if=1.0.4；chrono=0.4.45；const-oid=0.9.6；core-foundation-sys=0.8.7；cpufeatures=0.2.17 |
| crypto-common=0.1.7；digest=0.10.7；find-msvc-tools=0.1.9；futures-core=0.3.32；futures-io=0.3.32；futures-macro=0.3.32 |
| futures-sink=0.3.32；futures-task=0.3.32；futures-util=0.3.32；generic-array=0.14.7；getrandom=0.4.3；iana-time-zone=0.1.65 |
| iana-time-zone-haiku=0.1.2；itoa=1.0.18；js-sys=0.3.102；libc=0.2.186；libm=0.2.16；log=0.4.33 |
| memchr=2.8.2；num-traits=0.2.19；once_cell=1.21.4；pin-project-lite=0.2.17；proc-macro2=1.0.106；quote=1.0.46 |
| r-efi=6.0.0；regex=1.12.4；regex-automata=0.4.14；regex-syntax=0.8.11；rust-snap7=1.142.2；rustversion=1.0.22 |
| serde=1.0.228；serde_core=1.0.228；serde_derive=1.0.228；serde_json=1.0.150；sha2=0.10.9；shlex=2.0.1 |
| slab=0.4.12；subtle=2.6.1；syn=2.0.118；typenum=1.20.1；unicode-ident=1.0.24；uuid=1.23.3 |
| version_check=0.9.5；wasm-bindgen=0.2.125；wasm-bindgen-macro=0.2.125；wasm-bindgen-macro-support=0.2.125；wasm-bindgen-shared=0.2.125；windows-core=0.62.2 |
| windows-implement=0.60.2；windows-interface=0.59.3；windows-link=0.2.1；windows-result=0.4.1；windows-strings=0.5.1；zmij=1.0.21 |

rust-snap7原build.rs SHA `62aa125e5ecf01b3d2690bd3360b39aa83e525836d7f7d93bddff20b08ed00f7`，会以cc编包内native；其chrono默认features可能被统一，B0保留实际tree。未来只复制既有匹配包/索引到任务owned cache，离线派生**正式G0**Cargo.lock，允许条目仅此66 registry+该path core；新包/换版/MSRV/解析失败即blocked，不联网补包、不改DAA Cargo或共享cache。B0实际binary SHA、链接/ABI与正式树源manifest生成后方可运行协议；当前不编造产物digest。

### 2.7 DS整体设计刷新提案（仅设计，产品实现另批）

本节覆盖canonical正文§2复用判定、§6导入/地址、§4配置/保值、§9动作与§10/11分层的具体增补。批准后Development同步**同一**docs/AIIS_DS_Detailed_Design.md：以005 r3标识新依据，保持004已验收行为与历史，不伪称旧004 QA验证了新增部分；docs索引只改DS行，CODE_INDEX只增真实G0结构。无新设计正文副本、无004 bundle修改。

**多文件/多DB和身份流程**：选择目标instance -> 读所选公开或用户授权的.db/.udt原UTF-8字节并建source lineage/version/hash -> scan_sources一次catalog枚举多个DATA_BLOCK/TYPE及诊断 -> 用户逐DB明确UDT DeclarationRef闭包 -> expand_db -> 每DB显式绑定(instance_id, memory_region_id, db_id, db_number, length) -> 地址/命名/初值/策略预览 -> 用户确认后仅保存候选revision -> stopped显式apply，start独立。memory_region为该DB唯一image区域，area=DB；policy_region是该DB内bit子区间，二者身份分开，不把一份DB隐式拆成别的端口/DB。

DeclarationRef(input_id,declaration_index)只在本catalog定位，**不是跨重导稳定ID**。DS持有稳定source_lineage_id、不可变source_version_id、DB lineage/db_id、point_id及结构化Field/Index叶身份，DB号/端口/文件名/文件序号均非主键。一个文件可有多DB，每DB独立目标/编号；同instance DB号唯一，UDT可被多个DB引用但各DB固定其source version闭包。重复原字节在同lineage/映射/闭包下为unchanged预览，不生成第二组ID或重复DB；相同内容但新lineage/同名声明有歧义时须显式选择，不能按序号、同名或hash自动合并。

重导入先preview/CAS（expected saved etag+输入hash/闭包+一次性token），显示新增/删除/类型/结构/地址/DB号和引用影响，confirm前不写。仅注释/显示变化且结构/类型/地址/effective policy一致可保留ID/DS初值和确认依据；结构化路径/类型/DB号/长度/地址改变取消受影响地址/初值/策略确认，旧初值仅候选，不强转/截断。移除项列受影响规则/策略，确认前不删；同名UDT新版本不污染仍绑定旧版的DB。运行中仅产生saved候选，禁止直接改变loaded布局，停止/资源释放后才能apply。

**地址与命名**：将004“flat-only、UDT/数组不推算”刷新为core当前支持的**完整非优化标准树**，可对受限嵌套STRUCT、无环UDT、一维常量数组（负/非零下界）调用layout_standard提供理论预览；优化/未知标准性、不完整/缺失/循环UDT/未知类型/多维或嵌套数组拒绝。STRING叶可解析，含STRING的**整个DB不推算**，全部地址需有明确人工依据，不跳过STRING猜其后地址。只选若干叶不能推整DB。实际LayoutPlan只返回leaves{path,byte,bit}与length；padding由DS完整coverage列为reserved，数组stride只能据已返回叶布局展示，不另造推算规则或声称API返回stride。始终由DS校边界/全bit coverage、保护人工地址并让用户显式确认模型/摘要/依据；ConfirmedAddress由消费者负责，不能把oracle或建议写成已确认/实际PLC地址。

core扫描预算≤128输入、单文件1MiB/批次4MiB、展开深度8/数组1024/4096叶；DS另外聚合检查既有每instance≤32DB/4096叶及最多8instance目标，不能每DB各4096累乘。DB长度1–65536、编号1–65535，BOOL位0–7、标量不得带bit、checked算术及末端边界，BOOL不同bit合法，任何同bit/标量别名重叠拒绝，padding reserved默认读零/禁写。

技术名统一调用plan_names，**每个instance一次完整NameBatch**，包含全部DB、未选/停用/legacy/手工保留名；只对可变选中项应用结果，不能逐DB分批逃过碰撞。用真实结构化segments，不拆sourcePath字符串；type_suffix/validate_manual_name保持core规则及1–100 ASCII bytes，名称冲突按core原字符串比较，不自行casefold。数组/非ASCII/扁平碰撞无法命名可pending，地址经DS确认后再由同core一次地址兜底，不造另一套拼名规则；pending不能作为可应用启用点。DS消费者要在D1用原v1样例/oracle及完整namespace碰撞、重导/身份case独立验收，不改expected来迎合实现。

**初值/编码**：core跳过:=和BEGIN赋值；常驻提示“仅结构，TIA初值未导入”。DS typed初值缺省BOOL=false、整数/REAL=0、CHAR=NUL、STRING空串（max=n/actual=0，其余零）；显式DS输入优先，未经类型/范围/用户确认不能apply。BYTE/USINT 0..255、WORD/UINT 0..65535、DWORD/UDINT 0..4294967295，INT -32768..32767、DINT -2147483648..2147483647；多字节大端，REAL为有限IEEE754 f32、转换溢出拒绝，BOOL只更新对应mask不写邻位。CHAR限ASCII单byte（NUL默认合法），STRING[1..254]全n+2包/max头/actual≤n/ASCII/确定零填充，拒WSTRING、非ASCII、截断/超长、部分包与部分多字节标量。类型黄金字节/roundtrip和错误路径由DS自己验证，DAA decode可作对读，sharedcore不含encode，Python参考不是已完成Rust/C++编解码。

**配置/值及恢复**：沿用004单DS SQLite配置、不可变saved revision、单事务CAS selected、进程内loaded和唯一image owner；保存不运行、不逐tick存运行值，无持久apply journal/样本库/outbox。core接受RETAIN/NON_RETAIN语法不等于DS跨进程保值，不能据TIA保留标记改变本节恢复合同。apply仅stopped且旧callback/连接释放：有界typed旧值快照 -> owner外构建/兼容影响清单 -> 用户确认 -> 控制代次/epoch/seq/CAS复核 -> SQLite选中 -> 安装新epoch -> 独立start。selected已提交但安装失败不能报事务回滚；selected/loaded不一致禁start；commit/ack未知查询事实不自动重试。同版selected+loaded内容一致重复apply为already_loaded，不换epoch/重初始化；reset独立。

| 场景 | 推荐默认及确认边界（承接004，非本G0实施） |
| --- | --- |
| 同进程stop→start | 保留所有当前值/规则模拟时间，连接重建；stop不是reset。 |
| 同布局仅显示/连接限额 | 停机apply；稳定点ID、DB/地址/类型/确认摘要/effective值语义全部兼容者可保留typed值，含规则值/时间；不恢复连接。 |
| 规则参数/seed/周期 | 兼容hold保留，全部规则点/统一时钟初始化t=0。 |
| 初值改变 | 受影响点按新初值，其它兼容hold保留，全部规则统一t=0。 |
| mode/owner/读写/维护权限改变 | 受影响点初始化，其它兼容hold保留，全部规则t=0，取消旧epoch积压。 |
| DB结构/号/长度/地址/类型/增删点 | 受影响DB整体初始化；其它DB仅严格兼容hold保留，新增初始化、删除丢弃，规则t=0；绝不旧bytes拷新布局。 |
| 显式reset | stopped确认丢值；当前loaded全部初始化、新epoch/规则t=0。 |
| 跨进程重开/崩溃恢复 | 按真实selected重新校验并全部初始化、stopped，无值/连接/运行意图持久恢复。 |
| 回旧revision | 默认全部初始化并确认；不从日志复活历史运行值。 |

混合变更按更严格影响合并，保留需稳定ID/确认布局/owner/类型/初值/权限一致；保留证明或typed编码失败则选中事务前失败，旧版/值保留，用户可明确改选初始化，不能静默丢值。单一配置DB保存失败仍保旧/明示失败；可选日志sink故障只告警+有界环/丢弃计数，不封全部模拟写、不将已提交成功改失败/回放。

**页面到服务的实际责任**：D3工作台显式start/pause/resume/stop/reset与连接单close；配置中心的实例、DB/点位、多源预览/重导、地址确认、全instance命名、typed初值/owner/规则、saved/selected/loaded及保留清单；在线值只显示当前image，普通UI仅ui-owner，client/none hold维护须显式默认关开关+revision/epoch/point seq CAS确认，规则暂停不让权，维护后client可覆盖。页面刷新/筛选/导入预览不bind或写运行值；保存只持久草稿，apply后仍stopped。Tauri commands只解析DTO/意图并调用Rust应用服务；共享core负责纯导入/布局/名，存储/实例控制/策略编译由DS服务负责。协议adapter、规则/UI/init/reset必须进入同一个runtime image owner，不能Rust一份image+C++裸共享区另一份。

推荐后续Rust配置/导入/控制服务与G0验证后的C++ runtime边界复用；究竟进程内opaque FFI或受管理sidecar须D2精确ABI/进程合同及独立验证，不能据本G0预先称Rust协议核心/完整Tauri实现。改为Rust owner也须重新证明所有写前/调度/退出边界。入口仅composition root，服务不混进Tauri command，UI不跑规则时钟。G0当前一个C++主进程承载A/B，native硬崩可波及两者；X02未选sidecar的条件N/A不证明未来sidecar释放能力。

开工顺序：r3批准→设计正文同步和B0有限源码/ABI→G0 P1/P2/P3→fresh QA/Owner；core前置已可供D1**另立精确spec**，纯导入/配置设计可并行，产品实现仍需其批准；D2真实server保护路径须等G0 go，D3依赖D1/D2稳定合同，D4 L1/L2/L4/L5另批，L3扩展再另批。若有限原生控制点失败，研究no_go可接受但没有可交接server，必须回PM；不继续产品功能掩盖保护缺口。

## 3. PM文档边界与已批准的正式执行面

### 3.1 本轮仅PM spec；索引由协调机械同步

| 精确仓内路径 | 当前责任/内容 |
| --- | --- |
| `plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md` | PM唯一写路径，r3批准记录/来源/增补/执行面与完整历史。 |
| `PLAN.md` / `PLAN.zh-CN.md` | 主协调在PM批准登记handoff后仅同步既有005行owner_approved/下一Development gate。 |
| `plans/README.md` / `plans/README.zh-CN.md` | 主协调同一既有005目录行，不链接尚不存在的tasks/checklist。 |

草案阶段PM辅助报告保留在`/private/tmp/arch-aw-005-r3-refresh-ii4zqye9/pm/`；本次批准登记的辅助receipt仅写`/private/tmp/arch-aw-005-r3-refresh-ii4zqye9/execution-coordinator/pm-approval/`。当前不写下表任何文件，不改004 bundle/DS正文/DAA/core/依赖，不创建工程/tasks/checklist，不安装/构建/加载ABI/监听/原型/SQLite/联调。AW PLAN本轮不新增005行；所有并行dirty均保留。

### 3.2 正式源码、临时派生与持久证据

以下精确r3的Development/QA范围**已获Owner批准**，按角色和阶段gate串行执行；它们不属于本次PM批准登记的写权限。正式源码root `S=automation-world/device-simulator/g0/`（相对仓库根）；所有有效改动必须在此及下面列明的正式文档交付，不能只留tmp。新`automation-world/device-simulator/README.md`/README.zh-CN.md说明当前仅G0受限源码支撑、链接唯一根005和根PLAN，README-only是因本阶段无产品runtime工程/独立PLAN owner；D1另spec建立持续DS工程治理，不在本轮预造局部bundle/ID。G0自身README pair记录精确build/start/限制，裸入口只帮助。

临时root固定`T=/private/tmp/arch-aw-005-r3-exec/`，仅build/cache/profile/run输出/必要上游下载暂存；未知已有内容即blocked，不覆盖。DEV与QA串行使用相同S只读候选、各自`T/build/{dev,qa}/`、`T/cache/{dev,qa}/`、`T/tmp/{dev,qa}/`、`T/profile/{dev,qa}/`和`T/runs/{dev,qa}-NNNN/`。实现/脚本/fixture模板不在T编辑；若必须临时源码副本，仅由下面正式源码+封闭manifest复制，无额外改动，交付前逐文件核其与S一致、从S独立重建，不能用tmp候选代正式交付。

仓内摘要root `P=plans/ARCH-AW-005-ds-g0-prototype-validation/evidence/`，**只存下表5类紧凑清单/结果索引/哈希，raw日志/协议转储/图片和构建产物不入公开仓**。raw的非tmp/非repo持久root固定为`A=/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r3-evidence/`，DEV/QA分别dev-run-NNNN/qa-run-NNNN。T产出→逐文件校SHA复制至A→P/evidence-index索引A inventory及路径/摘要→tasks/checklist引用，之后才允许回收T可再生材料；不能仅记hash然后删raw。raw只含公开合成数据，不放真实配置/设备地址，binary仍只T；P/A不是第四权威文档/额外bundle。

| 正式精确路径/封闭文件集 | 未来责任与限定内容 |
| --- | --- |
| `plans/ARCH-AW-005-ds-g0-prototype-validation/tasks.md` | 获批后实际Development创建，记录设计同步/B0/G0及精确自检/handoff，不能给QA verdict。 |
| 同目录`checklist.md` | developer_handoff后实际fresh-context Verification创建；只验证/记录，Owner最终接受单列。 |
| `docs/AIIS_DS_Detailed_Design.md` | DEV仅同步§2.7及本r3源/边界/次序，明确旧004快照与005增补，不能记G0未运行已通过。 |
| `docs/README.md` / `docs/README.zh-CN.md` | DEV只更新DS条目说明新增设计来源/未实施边界，其它行保持。 |
| `CODE_INDEX.md` | DEV仅新增实际S源码/入口与来源导航，不重排/改任务外结构。 |
| `automation-world/device-simulator/README.md` / `README.zh-CN.md`；S`README.md` / `README.zh-CN.md` | DEV上述README-only身份、唯一root任务链接及build/start/STOP/限制双语说明，无空PLAN/task/产品承诺。 |
| S`CMakeLists.txt`；`server/main.cpp`、`server/owner.hpp`、`server/owner.cpp`、`server/protocol_hooks.hpp`、`server/protocol_hooks.cpp`、`server/resource_sample.cpp` | DEV C++17最小composition root、单owner/六来源/typed准入/轮转与有限native hooks/自采样，无产品UI/配置库。 |
| S`client/reference_main.cpp`、`client/wire_cases.hpp`、`client/wire_cases.cpp`、`native_abi_probe.cpp` | DEV原native client API及所列19case有限raw vectors/独立item解码、无端口ABI probe；不是通用协议栈。 |
| S`vendor/snap7-1.4.2/{upstream,controlled}/src/**`、各自`release/Wrappers/c-cpp/snap7.h`、`gpl.txt`、`lgpl-3.0.txt` | DEV复制冻结官方包的原有src文件集（12cpp与原header/includes）；**不是任意通配许可**，只限该包原有这些成员。upstream全只读；controlled同集，仅§2.4八文件受限扩展，其余原字节；不复制发布二进制/整包样例产品。 |
| S`vendor/snap7-1.4.2/upstream-manifest.json`、`controlled-manifest.json`、`native-g0.patch`、`NOTICE.md` | DEV完整source hash/差异、原许可和来源/限制；补丁不扩表外函数/线程框架，源码与生成器一致。 |
| S`daa-harness/Cargo.toml`、`Cargo.lock`、`src/main.rs`、`src/domain/mod.rs`、`src/infrastructure/mod.rs` | DEV六registry根+core path的正式最小crate；五原DAA模块按§2.5外部path只读消费，不复制/编辑；模块及core保持原SHA。无Tauri/build.rs/应用启动。 |
| S`scripts/prepare_data.py`、`run_cases.py`、`collect_evidence.py`、`verify_evidence.py` | DEV stdlib-only、显式S/T/role/run参数，合成数据/受控启动/停止/证据核算；无下载/安装/默认env。QA审查可复用并独立解码，不照抄汇总作结论。 |
| S`fixtures/g0/limits.tsv`、`points.tsv`、`fixture-a.bin`、`fixture-b.bin`、`profile.json`；S`source-inputs.json` | DEV按§3.4/§5定义生成的正式公开协议夹具/输入清单，版本ds-g0-s7-v1；scripts从这些模板在T复制角色profile，不能从tmp反向补造未经验证源码。source-inputs pin本spec/原生包、61-file清单、五DAA源、core/v1/新锁及S内源/脚本/固定模板；排除自身、其它生成manifest及所有临时/下游产物，禁止自哈希。 |
| P`input-manifest.json`、`protocol-baseline.json`、`delivery-source-manifest.json`、`evidence-index.json`、`resource-closeout.json` | DEV保存真实输入/候选/入口/协议有限合同和持久证据索引；Verification只核其与精确handoff/正式树一致并写checklist，不改实现/该DEV工件。protocol-baseline的QA/Owner字段在DEV交接为pending及预定记录路径；Owner终验后仅主协调按checklist机械同步acceptance/status/事实链接，代码/协议字段不变，保留verifiedCandidateSha256及前后delta。不新测，不给DEV预填未来结论；checklist是唯一接受权威，无发布/ref。 |
| A`{dev,qa}-run-NNNN/`内`commands.jsonl`、`source-manifest.json`、`native-g0.patch`、`dependency-graph.json`、`build-manifest.json`、`abi.json`、`limits.json`、`fixture-manifest.json`、`events.jsonl`、`wire.jsonl`、`results.jsonl`、`resources.jsonl`、`processes.jsonl`、`summary.json`、`cleanup.json`、`stdout.txt`、`stderr.txt`、`inventory.json`及`images/{case}-{step}-{instance}-{epoch}.bin` | DEV/QA各自产生/持久化，不覆盖旧run/失败；NNNN从0001单调追加，文件种类限本表。inventory逐成员记路径/大小/SHA、排除自身，不放binary；P只索引该inventory的SHA/路径与紧凑结果，角色摘要仍归tasks/checklist。 |

只读输入还包括§2.1 accepted manifest封闭61文件及§2.5五文件、新DAA Cargo.toml/lock；共享v1样例直接读`automation-world/shared/tia-import-core/fixtures/`，不在S维护另一份expected。manifest引用方向无环：外部固定输入/非manifest源文件→source-inputs；正式S全文件（包含source-inputs，但不含P/T/A）→P/delivery-source-manifest；该源manifest与T内真实binary→A中对应run的build-manifest；再由P的protocol/evidence紧凑索引引用A的run inventory。各清单均排除自身/下游，QA/Owner接受只引用checklist事实，不让checklist与protocol工件做互相内容哈希循环。正式源码冻结是工作树全manifest+原包/五DAA/core字节，不以HEAD/tag取代。审批前后或QA前漂移均需重新精确handoff，触及范围/输入实质变化回PM新Revision。

临时派生精确种类：T/cache/{dev,qa}/cargo-home/registry/{cache,src,index}仅66包及其原索引、T/cache/snap7-full-1.4.2.7z只冻结原包暂存；T/build/{dev,qa}/{cmake,native,daa}仅CMake/Cargo派生.o/.a/.dylib/.d、bin/锁/日志；T/tmp/{dev,qa}/编译临时；T/profile/{dev,qa}/只复制并核SHA上述g0五个模板（role/run/输出路径字段可不同）；T/runs/{dev,qa}-NNNN/只同A的run证据种类。不能在这些目录新增实现/新source/任意依赖。必要源/脚本/锁在S，所有编译产物不提交仓库。

### 3.3 B0、构建启动入口与正式树一致性

下列动作已获精确r3批准，批准登记时尚未执行。DEV先同步design/文档并在正式S建立表内源码/八文件受控补丁；先出source/控制点diff，若要迁移ISO/S7主循环/改线程框架/超表即no_go/blocked，不转为完整协议重写。B0先校accepted manifest61/61和五模块/新锁/core、host/工具链/有限backlog/AMQ/最坏PDU预留，不能用MaxClients或单callback代控制。

CMake的source根明确为仓库绝对`<repo>/automation-world/device-simulator/g0`，native路径从`${CMAKE_CURRENT_SOURCE_DIR}/vendor/snap7-1.4.2/{controlled,upstream}/src`取；server/ref分别用controlled/upstream的同一12translation units（sys的snap_msgsock/snap_sysutils/snap_tcpsrvr/snap_threads；core的s7_client/s7_isotcp/s7_partner/s7_peer/s7_server/s7_text/s7_micro_client；lib的snap7_libmain），头从相应sys/core/lib。`cmake -S <S绝对> -B <T>/build/<role>/cmake -G "Unix Makefiles" -DCMAKE_MAKE_PROGRAM=/usr/bin/make -DCMAKE_CXX_COMPILER=/usr/bin/clang++ -DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_OSX_SYSROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk -DCMAKE_BUILD_TYPE=RelWithDebInfo -DDS_G0_OUTPUT_DIR=<T>/build/<role>/native`，再`cmake --build <该build目录> --parallel 2`；C++17/-O2/-g/-fno-omit-frame-pointer/libc++/pthread，命名libds_g0_snap7.dylib、libds_g0_reference.dylib、ds-g0-server、ds-g0-reference、ds-g0-abi-probe输出该native目录，使用@loader_path相对rpath，禁系统install/DYLD替代源。

Rust从**正式S/daa-harness**构建，core相对path和五模块#[path]按§2.5，不从T/source或副本取源。使用绝对stable cargo/rustc1.89.0，CARGO_HOME=<T>/cache/<role>/cargo-home、CARGO_TARGET_DIR=<T>/build/<role>/daa、TMPDIR=<T>/tmp/<role>；不repurpose HOME/CODEX_HOME。DEV以新DAA冻结锁为种子`cargo generate-lockfile --offline --manifest-path <S>/daa-harness/Cargo.toml`，校验66registry+core的name/version/source/checksum封闭后把**派生锁交付S**；随后`cargo tree --offline --locked --manifest-path <同manifest> --no-default-features --features rust-snap7-driver -e features`及`cargo build --offline --locked --release --target aarch64-apple-darwin --manifest-path <同manifest> --no-default-features --features rust-snap7-driver --bin ds-g0-daa`。QA只读同一S/lock，用其独立cache/target重建，不编辑锁。执行路径固定为<T>/build/<role>/daa/aarch64-apple-darwin/release/ds-g0-daa；不跑整个DAA、cargo test/all-features或local-validation，不联网补包。

B0产物真实生成后先记每bin/dylib SHA、file/otool -L/nm/SDK/flags、rustc dep-info/feature图、正式S全manifest及五原文件/core摘要；仅运行**无端口**ds-g0-abi-probe核§2.3 Tag/返回int/调用约定、各固定buffer/capacity/预留公式，不能据其代真实item/16连接。输入/有限性/构建/ABI任一未闭合禁止协议运行；新产物digest是本冻结source/动作的生成结果，当前不编造。

B0闭合后从S/scripts运行`prepare_data.py --source-root <S> --run-root <T> --role <dev|qa>`，复制核对正式profile模板；`run_cases.py --source-root <S> --run-root <T> --role <dev|qa> --case <19case之一>`校已冻结bin SHA/输入/端口，调用<T>/build/<role>/native/ds-g0-server，显式传--limits/--points/--fixture-a/--fixture-b为<T>/profile/<role>/对应文件、--port-a 30102/--port-b 30103。reference和DAA二进制同样从**该role**上述明确build路径取，禁止发现PATH中同名程序/旧tmp二进制。control仅owned stdin/stdout，无额外API端口；裸入口帮助，无默认文件/env/启动。从只读正式树独立rebuild/启动原证据及source/binary映射持久A并由P紧凑索引，不能只有tmp候选曾通过。

### 3.4 有限协议baseline的固定profile与交接门槛

| 固定项 | ds-g0-s7-v1候选合同（无产品UI/SQLite，不是发布版本） |
| --- | --- |
| 端点 | A 127.0.0.1:30102，rack0/slot1/called0x0101/calling0x0100；B :30103，rack0/slot2/called0x0102/calling0x0100；30104无listener负例。owned冲突socket仅临时占A；禁SO_REUSEPORT隐式分流/wildcard/102/换口/抢占。今天lsof未观察占用不是预约，run前再查，foreign占用即fail/block。 |
| 内存/标识 | 每instance DB41=1024B、DB57=64B；DB57首8B为ASCII DSG0A001或DSG0B001，其后56B零，read-only。DB号/绝对布局只属该有限profile，不固定产品DB拓扑；与v1 Names28/60/47样例无派生关系。 |
| DB41明确布局 | byte0.bit0 client BOOL、bit1 fixed-rule TRUE，其余reserved；byte1八个client BOOL；offset2 INT、4 REAL；offset48 ui-owner DINT、56 client-hold DINT（维护开关默认false）；64 STRING[8]占10B，128 STRING[254]占256B；400/404/408/412/416/420六个dynamic DINT、424 fixed-rule DINT；512..639为16个8B client槽，每槽两个完整DINT。其余reserved读零/禁写。各点无重叠。 |
| 类型/规则/初值 | 本G0实际typed范围仅该DB41的BOOL/INT/DINT/REAL/STRING[8]/[254]，另有DB57 marker raw bytes；§2.7的BYTE/USINT/WORD/UINT/DWORD/UDINT/CHAR是产品设计，不并入G0已验收类型矩阵，超profile另spec。全数值0、BOOL false、STRING的max/actual=n/0和零填充；start前rule t=0将byte0.bit1设TRUE、DINT424设7，6动态DINT在100ms桶k用(k+j)%101（j=0..5）给受控入口，非通用脚本引擎。BOOL mask、大端完整字段、有限f32和完整ASCII STRING按原19case；DB57 marker是明确只读合成初值。 |
| 权限与可读范围 | DB41/57完整范围client_read=true；DB41只有上述client BOOL/INT/REAL/STRING/16槽及56的client-hold可依coverage写，48仅ui-owner；rule/marker/reserved全触达写拒绝。C05/W07专门profile可在stopped显式开启56的一次性维护、revision/epoch/CAS及证据可见，不能在默认baseline暗开；W02 overlay只在该负例启用/撤除。 |
| 协议和限额 | classic DB read/write单/多item、BOOL/byte规范化；PDU480/frame512、≤4items且实际装得下、单item≤256B、AMQ1，C16/H4/TCP20及原全球/队列/bytes/期限不变。不能用“连上”代C01/C05吞吐；>16/全局峰值/完整PLC/SZL/CPU操作不支持或未验证。 |

W/C/D/X全部适用必证case与AC通过、无blocked、真实cleanstop/pthread_join/复绑/资源回B0，**正式源码/模板/依赖/生成binary与fresh QA验收候选一致**，并获Owner最终接受后，才可交接该有限standalone baseline。交接包protocol-baseline.json须含profile_id、Task ID/Revision/spec SHA、正式source/八文件patch/五DAA/core/样例pin、build/start/stop命令/工具链/SDK/bin SHA、端口/TSAP/DB/编码/权限/marker、case原证据/负例/16会话/资源限制和未覆盖能力；DEV时QA/Owner为pending，只能链接预定角色记录，不能预填未来通过。最终接受以checklist为唯一权威，主协调仅按§3.2机械同步该工件接受字段并保留已核候选SHA/原始内容证据；无事实仍candidate/not_run。no_go研究可以被接受，但不得同时宣称已有可联调server。

该baseline若满足下一任务对这些**合成绝对DB/类型/有限规则**的需求，可供另行批准的真实DAA应用S7→SQLite联合验证使用，不必为了读这些DB先实现全DS UI/配置库。G0真实ManagedS7 harness不是应用采集/SQLite落库证据，也不关闭B；联合任务须独立spec/原应用profile/版本/源/SQL证据、fresh QA、Owner接受。若DAA所需DB/类型/持续时长/运行行为超出本profile，先另spec扩并验收DS baseline，不拿004目标充当已有能力。阶段C/Backend/SMA/上传始终排除。

### 3.5 资源、日志和收尾

一个G0 C++主进程承载A/B、各自唯一owner；accepted native连接各worker，listener/reaper/owner/control/采样均计DS资源。reference/真实DAA client/Python采样另列，CPU按时间/墙钟、RSS/线程/FD与Mach ports分项，不用仅FD冒充全部句柄。无产品sidecar，X02条件N/A仅该分支，native硬崩可波及A+B；正常close/stop/退出和主程序PID清理仍必证，不冒充Tauri窗口退出。

DEV/QA分别登记owned PID/起时/可执行SHA/子进程；正常stop先封准入/取消未入段，只完成当前不可取消单item，实际pthread_join返回及socket/callback释放后才stopped/归还。超时保留failed/stopping/closing和unknown/OS dump；仅核实归属的失败实验，SIGTERM后5s仍不退出才可SIGKILL作失败清理，保留信号/退出码，不能算正常资源通过，不按名字批量kill。三端口只有先前run退出并释放后才fresh复绑，冲突失败不影响他人。

纯日志故障有界降级/丢弃，不将成功改失败；本研究证据缺口使对应case blocked，另run补证据，不补写/回放内存。handoff前先校A持久raw与T原件SHA一致、inventory/P索引及角色文档可定位，QA复核正式树一致性及资源依赖；Owner最终接受后协调只回收无占用/无后续及证据依赖的owned T材料，保留S/P/A。A属本DS线程，至少保留到另批DAA–DS联合验收后再复核用途/完整性/清理条件，不自动到期删除；resource-closeout明确路径/用途/归属/保留原因与复核触发。需继续留T则记路径/原因/触发清理时点，旧004/005/DAA材料不动。临时binary不是交付源码，正式source不是临时资源，raw日志也不是公开仓源码。

## 4. 编号需求


### R1. 保持G0交付小范围

只交候选决策、最小统一内存/准入harness及真实S7/DAA模块互操作、资源原始证据与限制。所有以下“运行/测试”均指未来获批执行；本轮不执行。沿用004目标，不实现产品UI、DB/UDT导入、SQLite保存/apply、完整规则引擎或完整DAA采集应用。规则、普通UI、一次性维护、init/reset可由标明来源的harness触发；它们验证受控入口，不宣称产品页面/IPC已实现。

### R2. P0来源冻结、B0构建/ABI与执行面

本r3的精确来源、工具链、文件/动作面以§2/§3为准；进入协议运行前须完成B0并有可审查的manifest：候选库精确版本/commit或发布包SHA、完整源码manifest与本地改动patch、native二进制SHA/动态静态链接/编译flags/ABI/目标架构；client版本/源与编译feature；OS/build、CPU物理核/逻辑线程、RAM、背景负载与采样工具口径；主/子进程资源模型、所有写入口/系统dispatch/阻塞点；第3节源码与依赖/输出/端口/动作精确表。参考主机至少4物理核、16GiB RAM、SSD，仅报告本次一个明确OS/架构结果，不外推三平台。

G0建议固定classic S7 PDU上限480B、单frame上限512B、单item应用payload≤256B、每PDU≤4items且实际请求/响应均可装入协商PDU；COTP分片累计重组也限480B且绝对期限不重置。协商AMQ、最大错误响应、描述符/stage/copy及系统socket buffer实额须从冻结实现计算，列完整最坏输入+输出预留公式。数值只是这个G0有限profile，不缩改004产品容量合同；不能静默降PDU/请求或用不可控库内队列冒充有界。无法控制/观察者在对应gate blocked或判候选不满足，先回PM决定。

### R3. 先证明可拒写再选语言与库

按第2节逐候选给证据支持的adopt/reject/blocked及原因，核回调时机、错误传播、线程/ABI/指针生命周期及未列操作。写前入口必须能阻止image更新并让客户端收到真实S7 item失败；无入口即淘汰，不得降为写后报警/回滚、tick修复或仅UI禁用。本r3只提出§2.4的有限原生扩展及C++服务端harness，尚待Owner批准；不采用Rust高层server或Python sidecar。B0未证ABI与有限扩展可行性前不进行协议运行。

### R4. 单owner、提交事件与拒写证明

每实例唯一image owner，所有读复制、来源准入、coverage/type/CAS复核和单item提交可追踪。非法写的静默测试先暂停规则并封其他合法写/排空在途，在同一epoch、同一已确认布局下保存**全部可能触达DB的完整bytes/hash、全image hash、instance seq、点版本/来源/更新时间**；失败后逐字节相同，客户端有真实失败。未知DB/越界/未列系统操作还核所有已分配DB，不能只看第一个点。

仅最终读回相同不足以证明写前拒绝：同时给冻结源码调用链与`request_received -> admission/type/owner_decision -> rejected(no commit) -> item_response`事件顺序；合法路径为`accepted -> commit_begin -> committed(seq) -> response`。在实际mutation入口计数/记录写前写后，证明拒绝item无任何commit/裸buffer写，再无“恢复旧值”动作。并发测试另按item/result ID、触达点版本与获准写范围对账，允许其他合法提交改变实例seq/hash，不能要求规则运行时全image绝对不变。观测本身不能改内存。

### R5. 原始bit/byte、typed包及item结果

覆盖BOOL邻位与整byte、全触达跨权限、部分标量、边界/长度/transport-size/count、有限REAL、大端整数、STRING完整包/长度头/ASCII与多item部分成功。每write item原子，失败全item不变；读item来自单epoch/seq复制，多item按内部顺序逐项并允许连接/规则交错。不同PDU/DB/实例无全局原子承诺。未列非DB区/CPU控制/clock/块操作/任意SZL不可绕过入口或映射为DS控制；必要最小握手元数据按P0白名单逐项列出，不接受库默认“成功但无作用”当拒绝。

### R6. 六种写来源收口与权限/CAS

client、rule、普通UI、一次性ui_maintenance、initialize、reset均从harness进入同一owner或同锁封闭maintenance模式。普通UI仅ui-owner；一次性维护只对显式允许的client/none hold，默认关，不改变持续owner，后续合法client可覆盖；rule暂停仍不让权。UI/维护带expected loaded revision/epoch/point last_seq，在提交边界CAS，冲突不写/不自动重试。init/reset仅封闭gate/stopped，非法运行中调用拒绝；reset为新epoch/初始化，stop-start保值。这里只验证入口合同，不新增持久apply/保留算法或租约。

### R7. 16会话与C/H/TCP/closing计数

一个PLC=一个server实例，C为**已建立S7 sessions**，非进程/IP/TCP accept数量。沿用默认C16、整数1–64（>16未验证）、H4整数1–16、accepted TCP=C+H默认20；closing直到socket/callback/worker真释放仍占先前C或H和TCP。全局C/H/TCP128/32/160、全树≤64线程/≤1024句柄均为硬预算，启用实例配置和不得超预算，0/负/小数/无限拒绝，修改只stopped显式载入；G0仅运行单实例16及两实例各少量兼容连接，不跑2×16/8×16。配置域边界/全局加总可由无端口的harness校验，不冒充64/128会话容量。

满额拒后来者、不抢占老连接、不重置hold、不提前虚减closing，不在同socket阶段转换重复计数。库MaxClients参数不能替代真实C/H/TCP各阶段准入及计数，短命超额accept句柄也须列入实际OS资源，不隐去。连接快照须有instance/connection ID、peer、阶段、建立与最近收发完成时间、执行/等待/bytes、拒绝/超时/关闭原因；无需产品面板，但独立QA能核逐连接事实。全局上限不代表与线程/CPU预算能同时打满；每连接一线程候选不得由本次16会话外推128或静默提高64线程预算。

### R8. 期限与有限队列/输入输出预算

沿用握手5s（accept起算）、半frame2s（首byte起算）、待提交2s（完整PDU准入/等待起算且commit复核）、send2s（响应开始发送起算）；滴流不续期，正常idle踢出默认关闭。每连接≤1执行+2等待PDU及64KiB全部协议bytes；实例等待≤64PDU/1024items及1MiB；全局等待≤256PDU及4MiB；UI等待4、普通控制8、每规则待tick1。bytes包含未完frame、执行/等待、描述符、stage/copy及最坏响应预留，转阶段不重计、复制新增计、closing仍计。

整个PDU输入/输出先原子预留，再执行第一item；预算不足真实失败或关闭该连接，无item已提交。单个写callback不能替代整PDU入队/最坏响应预留或逐item结果/内部顺序；P0若无法观察控制这些阶段，须判不满足或回PM改方案，不默许重写协议栈。PDU/item超协商/超限、send阻塞、未完握手和半报文均有明确结果。G0对未能由16会话/480B profile触达的实例/全局大上限，以**标明test-only的更小预算或确定的reservation故障注入**验证相同准入控制点及归还，不声称填满4MiB/1024items；正常profile硬上限不提高。协商AMQ较小时如实列实际可达状态，不伪称已实测1+2并行。网络收发/解析/编码、磁盘及证据写入均在owner临界区外。

### R9. 公平、规则合并与控制可达

沿用协议→规则→UI非空类轮转，协议内连接round-robin每次最多1item，同PDU保序；规则按point轮转且每规则最多1待tick、合并计missed/coalesced。用F洪峰、A/B低频、8规则及UI维护同时存在的60s场景验证。已经准入且持续可调度的F/A/B三连接，每次protocol类轮转至多3次dispatch让各方一次；三个工作类持续非空时每3次工作类dispatch各获一次。保存调度轨迹/资格时刻，不能把库锁外看不见的等待从统计中删掉。

正常低频请求p99≤250ms，无连续1s完全不服务的已准入A/B；规则与1Hz UI请求可达。过载可真实拒绝，但已预留工作/stop不能饿死；恢复基准5s内等待队列回零或稳定基准，无无界补跑。stop走及时通道，先关准入/accept，取消未进不可取消段者，当前已进段单item完成一次；不得等完整PDU或长积压提交完才处理stop。

### R10. 真实DAA自定义端口兼容

未来必证使用固定版本DAA **真实ManagedS7::connect/read/read_bounded/disconnect**，`rust-snap7-driver`开启、`local-validation`关闭，不以Python参考client、FixtureTransport或origin标签替代。推荐最小隔离harness消费**字节相同的ManagedS7及所需DAA domain依赖快照**，保留原RemotePort/rack/slot/超时调用；精确源清单/依赖/编译入口及feature见§2.5/§2.6及§3，r3批准后按B0核验。若私有API/feature/安全profile无法这样消费，结果blocked，回协调申请独立DAA范围，不能修改原DAA/改成重写近似client后声称兼容。

G0证明层级为真实DAA客户端模块对候选server的S7互操作，不覆盖完整DAA GUI/SQLite采集/历史/上传/native窗口。推荐harness不创建DAA业务库，不读任何env或默认profile，只从批准的owned内存Plc参数调用；若实际入口必须创建隔离DAA profile/数据库，其路径/动作须先另列获批执行面，禁止擅自走生产启动。明确禁上传、Backend/direct DB/授权服务/旧采集/auto-start；连接/读取仅两个owned endpoints。

### R11. 关闭、资源释放与未知回执

单连接close与全实例stop都先关相应准入，取消未进入不可取消段者，让已进段单item完成一次，然后join回调/worker、关socket/listener、停timer/清队列并幂等释放。正常单连接close/stop≤2s，故意积压/慢连接stop≤5s；超时保留closing/stopping/failed及实际名额，不假报stopped或释放仍被callback使用的buffer。未提交超时/取消=拒绝不变；已提交但回执丢失=结果未知，无回滚/自动重试/exactly-once。

记录全进程树CPU/RSS/线程/句柄及分项socket/listener/callback/timer/队列bytes/输出预留；client进程单列，不藏入或混同DS指标。检查同端口重绑、20次start-stop、16连接各10轮重连、重复关闭通知。若选sidecar，父进程正常退出/崩溃、子进程异常退出与A/B隔离必须实测，5s内无owned孤儿和占用端口；G0管理harness不等于Tauri原生退出。进程内native硬崩溃可能波及全进程须如实给隔离风险，不能靠逻辑instance ID宣称崩溃隔离。

### R12. 证据、统计与可复现交接

原始JSONL按run/candidate/build/instance/connection/request/item/result/epoch/seq及monotonic时刻关联；保存raw协议item结果/有界报文、完整合成fixture前后bytes/hash、决策/commit/response顺序、错误与预算变化、版本摘要、资源1Hz采样及状态转换采样、复现命令/退出码/环境。raw payload仅限本任务公开合成数据，不采集真实私有报文。报告offered/accepted/completed/rejected/timeout/unknown分母，逐连接p50/p95/p99/max和队列等待，不能删失败或用聚合平均掩盖饥饿。

运行raw证据先在T产生、必要原件须按§3校SHA持久化至非repo的A，P只保留5类紧凑索引/清单，不是产品日志/正式schema；证据丢失或关联不全不能判pass/go。沿用004纯日志故障降级原则：可选sink失败不把已提交成功改失败/回放；记录observability_degraded/丢弃，并将该段无法证明的case标blocked后另做新run，不把缺证据当内存已回滚。不要为G0增加强持久审计/SQLite journal。

### R13. 分阶段go/no-go及状态诚实

r3获批且B0通过后，按P1写前拒绝/全来源及item→P2连接/队列/公平/释放→P3真实DAA及最终全矩阵独立复现顺序推进；不能先建产品以待补保护。场景状态为pass/fail/blocked/not_run/deferred，以及严格条件项的not_applicable：pass有实际证据；fail为已运行不符；blocked为必要来源/环境/接口/证据不能取得；not_run为尚未执行或被早期淘汰阻断；deferred只限本spec明确排除的后续阶段；not_applicable仅用于未选sidecar时X02的父子进程专属分支，须给实际进程模型理由，不免除共通stop/资源释放及进程内native风险说明。必证项不能为凑go改deferred或not_applicable。

候选只有全部适用必证case通过、无未解除blocker、清理证据完整才可go；失败候选的后续case可not_run并给停止原因，不冒充通过。可信no_go是允许的研究结论，须指出不满足的实际控制点和复现证据；它阻止后续采纳该候选，不强迫实现完整协议栈。QA独立审核方法/复现和结论，原case fail不得被改pass；即使研究报告被Owner接受，也不代表候选能力通过。更换未列候选、放宽保护/16会话/预算/阈值、增源码/依赖/端口/DAA动作、扩OS/长负载均回PM新Revision和Owner批准。

### R14. 保留工作树与角色权威

本轮PM仅修订本spec；004 bundle/设计、DAA/core等起点保护文件及旧证据保持；只允许本任务精确角色delta。主协调只机械同步四根索引本任务既有行，保留DAA/CU等并发修改。后续Development只写获批执行面和tasks，精确handoff后新的fresh-context Verification只验证并写checklist，Owner保留最终接受与风险例外。当前profile为contract_only，串行角色/diff审计是合同控制，不宣称ACL、自动路由或团队激活。本draft文档自检不作G0、QA或Owner接受。

### R15. 已验收共享输入与真实编译闭包

按§2.1/§2.5/§2.6固定accepted-source-manifest的61个工作树文件、core版本/API/profile/v1样例、新锁及五个原DAA模块；DAA006接受只解除该输入前置，不证明server或DS导入已完成。G0只使用合成DB41/57，sharedcore编译闭包与未来DS六API消费者D1分开；源漂移、依赖不闭合不自动用latest/改DAA/改expected。

### R16. 整体设计增补与后续产品边界

§2.7的多文件/逐DB闭包、instance/region/DB映射、稳定lineage/point ID、保守重导、理论地址/全实例命名、显式typed初值/编码、SQLite配置与内存保值矩阵、页面动作/薄IPC/单owner架构和开工顺序，须在获批后同步canonical DS正文及相关索引，独立核文档一致性。当前只是设计要求，D1/D2/D3/D4产品实现及DAA联合SQLite/C不在此范围。

### R17. 正式源码、构建入口及持久证据交付

有效源码/脚本/锁/vendor八文件扩展/合成模板必须交付§3.2正式S；T只派生，A持久保存必要raw，P仅5类紧凑清单/索引。B0、DEV及fresh QA须核正式树输入/生成binary/实际启动入口与验收候选一致，临时验证不得代正式交付。遵当前AGENTS§2/§6，raw日志/构建产物不入公开repo，确认来源/无占用/必要证据在A且P可定位后才由协调清T；A按联合验收后复核触发保留，不动任务外资源。

### R18. 有限协议基线的可交接性与B/C门槛

§3.4固定profile版本、正式source/入口/端口/绝对DB布局/类型/权限/marker、所有负例/16会话/公平/真实join/释放、独立QA及Owner接受，满足后才标accepted G0 standalone protocol baseline。可信no_go不等于已有server。G0模块client不代真实DAA应用S7→SQLite；后者另批spec/fresh QA/Owner接受才可能关闭整体B；超profile先扩并验收DS，C排除。

## 5. P1写入/协议场景矩阵

以下仅定义未来输入/动作/预期。**DEV逐行实现harness/自检，在T采集、校SHA向A持久保存必要原证据，并在P留紧凑索引；fresh QA从固定handoff自行执行并独立解码item/比较bytes，不调用DEV总结冒充复现**。每个确定性向量至少独立重置后重复3次；BOOL竞争另为100轮。失败静默测试按R4关其他写并排空；并发单列，不能混用不变口径。

冻结合成fixture定义（B0生成raw manifest，不建正式schema）：每实例测试DB41长1024B、DB57长64B，后者为实例身份只读marker；DB号/两个DB仅夹具，不是产品固定拓扑。DB41 byte0.bit0=client BOOL、bit1=rule fixed TRUE、其余reserved；byte1八个client BOOL；offset2 INT、4 REAL；64处STRING[8]全10B、128处STRING[254]全256B；512起16个8B client hold槽（每槽两DINT）。普通ui-owner DINT在48、显式维护client-hold DINT在56；规则为400起6个动态DINT及1个fixed DINT，加byte0.bit1共8规则。未列空位reserved/read-zero/write-denied；A/B初值marker不同、image独立。规则参数仅够触发入口，不实现通用引擎。

W02的未确认coverage负例固定为既有DB41 offset56的4B client-hold DINT：在同一已确认布局/epoch、规则和其他合法写均经屏障排空后，harness仅对该范围启用test-only admission overlay，使owner coverage复核返回unconfirmed，再由真实client写完整4B，必须在commit前失败。它不改变已加载布局/owner/bytes/seq，不承诺产品允许未确认布局启动。保存overlay开启/拒绝/关闭事件与完整不变证据后，先撤掉overlay再解除屏障；不靠reset或回写旧bytes“恢复”。overlay只限本W02负例，不出现在C/D正常profile或默认准入策略。

| Case / 需求 | 输入与动作 | 可判定预期与必须保存证据 |
| --- | --- | --- |
| W01 · R3/R4/R5 | 真实client向自己8B槽写两个完整DINT的非旧值，raw读回；再读64B marker。 | item成功、逐字节/typed值一致，唯一commit且seq+1；raw请求/回执/读回、owner trace及完整前后image。不能只看client函数无异常。 |
| W02 · R4/R5 | 静默屏障下依次向rule字段、reserved、越权bit、未确认coverage、未知DB写；未确认coverage固定采用本节DB41 offset56的test-only overlay及撤除边界。 | 每item真实失败；全部可能触达范围bytes/hash/点版本及全image/seq不变，拒绝前无commit/裸指针写，回调/dispatch顺序可复查。自动字段即使rules_paused仍拒绝。 |
| W03 · R5/R6 | byte0.bit0合法bit写；向同byte整byte写（含rule/reserved，即使相应值没变）；byte1两个不同client位由双连接同步竞争100轮；byte1合法整byte写。 | bit写只改mask、邻位保留；byte0整byte失败且不变；byte1两位更新均保留，无RMW丢失，合法整byte成功。保存各轮item/seq与目标byte前后，不拿不同并发顺序当失败。 |
| W04 · R4/R5/R8 | 部分INT/REAL、越过client槽末端触及reserved、末端1023+2、0长度、count溢出/transport单位不符/短payload、NaN/Inf REAL及超frame/PDU；合法大端有符号/有限REAL对照。 | 非法输入在提交前失败/无可编码item时关该连接；无越界/分配爆量/其他实例变化，合法typed值可读回。保存每向量原始长度/规范化触达、错误码、全范围bytes及预算变化；格式错误与权限item失败分开。 |
| W05 · R5 | STRING[8]写完整`08 03 41 42 43`加5零字节；STRING[254]完整256B对照；错误max头、actual>max、非ASCII、只写头/截断包/部分包。 | 合法包精确读回；其余整item失败、整个STRING包及全触达字段不变，不截断后报成功。保存原始包/布局、item返回、typed解码与hash。 |
| W06 · R4/R5/R9 | 单PDU顺序3items：合法8B、禁止rule写、合法STRING；其间允许另一已准入连接/规则插入，另做静默对照。 | 真实逐item成功/失败/成功、内部顺序保留，成功各提交一次，失败范围不变；无全PDU回滚/全成功伪造。保存原PDU/result数组与逐item调度/seq，混合结果按触达范围对账。 |
| W07 · R4/R6 | 六写来源各一合法及一非法/陈旧操作：rule对hold/paused/旧epoch，UI及维护CAS冲突，维护默认关和rule即使暂停，运行中init/reset；合法维护后client再次写。 | 全部进入同owner/maintenance模式；非法无commit，合法来源和seq正确。维护不改持续owner/初值、后续client可覆盖；reset仅stopped换epoch，stop-start保值。保存源入口调用图、每操作结果与revision/epoch/point seq，harness不等于UI。 |
| W08 · R3/R5 | 对owned server发非DB区、CPU start/stop、clock、块上传下载、非白名单SZL/未知功能各一请求。 | 明确协议拒绝或有界关闭，无image/DS状态/宿主时钟变化，不能以库默认成功空操作通过。记录dispatch白名单、原请求/结果/前后状态；若库自动处理无法阻止，候选no_go。 |
| W09 · R3/R4/R11 | 在precommit及不可取消提交段用确定harness屏障分别触发timeout/stop/close；另在commit后故意丢回执；复查callback指针引用/注销顺序。 | precommit取消不变；已入段item完成一次，后项取消，已提交丢ack为unknown且不自动重试；旧epoch不能触达新image。保存call/commit/return/close/join/释放时序、引用计数及wire可达结果；禁止释放仍使用buffer。注入屏障是实验工具，不可带入产品owner等待逻辑。 |

## 6. P2连接、队列、公平与资源短程profile

每个数值均为r1已批准且本r3不降低的G0目标，不是实测支持。每个最终候选DEV完整运行一轮，独立QA从新run/profile/端口依同一冻结输入重现一轮；静态早期淘汰者不强行跑后续。不得将这些短程结果替代004 L1–L5。

| Case / 需求 | 有界输入、次数/时长 | 判据及证据 |
| --- | --- | --- |
| C01 · R7/R8/R12 | 单实例16已建立S7 sessions；预热30s后300s。各连接1轮/s，每轮2请求、各1item：DB57读64B+自己DB41槽写8B；8规则=6动态+2fixed，100ms到期。 | 32请求/s=16读+16写，应用payload1152B/s；测量段共9600请求=4800读+4800写、345600B，不含协议头；每连接600请求。按offered全量核完成，非故意错误/错写/越权/BOOL丢更新=0；每连接p95≤100ms/p99≤250ms，排队p99≤100ms，规则missed≤1%（24000到期机会，动态/fixed分列，无变化fixed不虚增commit）。 |
| C02 · R7/R11 | C01的16会话仍读写时，第17个S7连接尝试20次，间隔100ms；再关闭一条并重连，重复close通知。 | 新来者被拒，不抢占/重置原16；关闭直到真释放才腾C/TCP，重连新ID。逐时C/H/TCP/closing/实际established及OS socket、原会话成功item、拒绝阶段/原因均对账，无负计数/重复归还。 |
| C03 · R7/R8 | 另有16已建立时保持4个未完成握手TCP，第5未完成握手尝试20次；随后半frame每500ms滴一byte；另一session idle30s后正常读。每种绝对期限试3次。 | C16/H4/TCP20不超，5th握手无额外持久对象；握手accept后≤5.5s、半frame首byte后≤2.5s完成关闭/清理（含≤0.5s观察裕量，不延长配置期限）。老会话继续；idle不误踢。保存时间起点、阶段、bytes/名额/句柄释放。 |
| C04 · R8/R9 | 单连接超协商in-flight及1执行/2等待边界；另用P0声明的小预算/确定reservation故障触发每连接、实例、全局输入+最大输出预留失败；恢复后重试。慢读peer的实际收/发socket buffer各≤16KiB，20次/s发256B读取且不消费响应，最多30s，须实际观察send阻塞。 | 超额完整PDU在第一item前失败/关该连接、无commit；所有阶段数量/bytes含预留不超实额，幂等归还。发生阻塞的该响应从首次发送尝试起≤2.5s关闭（2s配置期限加≤0.5s观察裕量，不从阻塞时重置），其他连接/规则/stop继续。若只触发队列拒绝而没观察send阻塞，该subcase仍not_run/blocked，不能算send期限pass；不能以注入替代所有真实socket证据。 |
| C05 · R9/R11/R12 | 同实例F/A/B3个活跃连接、其余13个idle：F20 PDU/s、每PDU4个64B read items，A/B各用C01每连接profile；8规则100ms、UI维护1次/s，持续60s。再用小预算制造积压并从及时通道stop，3次；恢复基准观察5s。 | F offered80items/s，A/B合4items/s，规则80次到期/s，UI1次/s；PDU数与item数分别计。正常60s段A/B各60轮=120请求全部按offered完成，60次合法UI维护均有成功结果，不得把低频工作拒于准入外绕过公平；F的完成/拒绝/超时单列。仅随后明确小预算故障积压段允许按真实结果计低频拒绝。按R9轮转/时限判，保存各连接/类资格、dispatch、等待/完成/拒绝、missed/coalesced和stop各阶段；F大PDU不独占、普通控制不饿死业务，过载stop≤5s，恢复队列回落。 |
| C06 · R7/R11 | 16条连接各10轮断开/重连，共160次；每轮含一次正常close、半关闭或异常之一，轮转+100–1000ms固定seed抖动；随后20次start-stop，每次建立16session并各读/写1次，stop后等10s采样。显式reset另3次。 | 正常close/stop≤2s、故意积压stop≤5s，所有owned listener/socket/callback/工作timer/队列PDU/item/bytes/输出预留回0；stopped保留image/值不算泄漏，reset独立初始化。停止后同owned端口可重新bind，无隐形worker/旧epoch写。保留完整cycle序列，不把10轮写成004 L4每连接100次。 |

C01及上述所有阶段分别保存全DS核心/管理器/sidecar进程树的平均CPU、RSS峰值/净增、线程/句柄及分类；**client/采样进程单列**。G0目标：平均CPU≤单逻辑核100%（CPU时间/墙钟，不除主机核数）、RSS≤512MiB、线程≤64、句柄≤1024；C01测量段RSS净增≤16MiB。这是短程可行性阈值，不声称004的60min增长或长稳定性已满足。

C06资源基线为依赖已加载、image已分配、证据sink/采样器已启动但无listener/连接的稳定stopped状态B0；首轮热身后固定B0。每次stopped10s时owned transport/callback/工作timer/queue/reserve=0，线程/句柄按分项回B0；明确保留的单一库全局设施须P0计入B0，不能逐cycle追加。RSS允许allocator保留但每次≤B0+16MiB，最后5次中位数相对最先5次≤8MiB；若出现连续4组（每5次一组）严格增长且总增>8MiB则失败。原始曲线与峰值均交付，这些口径不能证明永不泄漏。

两个实例仅为端口/故障隔离对照：A16会话场景时B至多1参考会话；真实DAA场景各1。该组合ΣC默认配置32、ΣH8、ΣTCP40，仍受128/32/160及64线程/1024句柄联合预算；不能用名额配置推断2×16吞吐。>16实际会话、8×16、全局极限、大布局以及完整L1/L2的5min预热+60min和L4/L5长故障均明确deferred到D4或另批扩展任务，不在G0凑齐。

## 7. P3真实DAA与退出边界矩阵

责任同第5节：DEV提供精确非fixture入口与原证据，fresh QA独立运行、核source/feature、协议和OS状态。r3执行面未批准及B0未闭合前以下均不执行。

| Case / 需求 | 输入与动作 | 预期与证据 |
| --- | --- | --- |
| D01 · R2/R10 | 两个owned非102端口、A/B各自固定called TSAP/rack/slot和不同DB marker；字节冻结的真实ManagedS7各持1会话，60s、每连接1轮/s，每轮读取两个DB各1次；参考client改变允许hold值后再DAA读取。 | 两模块累计240次真实db_read，连接复用，能按marker/bytes/变化值区分实例，RemotePort实值与COTP/S7协商、调用trace相符。提交源/feature/native摘要、raw字节/DAA结果及server connection ID；fixture/标签/截图不能替代。只证明模块级S7，不证明完整DAA采集或GUI。 |
| D02 · R7/R10 | 错rack/slot产生错误called TSAP、owned无listener端口、A参数误指B端口；每负例3次；另用owned冲突listener阻止A启动，重复start。 | 错TSAP明确失败，不能同端口隐式复用/接受任意身份；错端口不回退102/扫描其他地址；冲突只使后来A failed、占用者和B继续、无第二listener。每次记录真实COTP、RemotePort、失败阶段/错误与名额释放；若候选默认接受错TSAP，必须先取得可控adapter证据或判不满足。 |
| X01 · R4/R11 | A/B均在服务时只关闭A一条连接；另在W09屏障处stop A，B持续读；超时注入后再观察实际清理及同端口重绑。 | 关闭只影响指定对象；未提交取消/已入段完成/已提交丢ack未知分开，B不变。正常2s/故障5s，超时不报stopped；只有callback/socket/worker真实归零后才释放/重绑。保存进程/OS/库计数和owner事件关联。 |
| X02 · R2/R11 | 若选择sidecar/每实例进程：父管理harness正常退出、父异常终止、A子进程异常退出，各3次；同时观察B，随后新run重开。 | 正常有序stop；异常时≤5s无owned孤儿/残留listener，A子崩不误报clean且B继续；重开只初始化fixture、停机，不恢复旧连接/未知写。完整进程树/PID起止/退出码/socket证据。未选sidecar则明确not_applicable理由，不宣称该能力；进程内native硬崩风险单列，完整Tauri退出与三平台发布仍deferred。 |

资源/异常测试只操作获批本任务owned进程和loopback socket；不停止DAA原生会话、不修改其profile、不向任何真实设备或生产DB/API发动作。若不能在准确进程树中区分归属，先blocked，不批量kill或清理未知资源。

## 8. AC与可审阅覆盖

下表是未来**研究交付及选型判断**的验收口径，非本轮结果。每一行均须有DEV原始证据和fresh QA独立观察；候选go必须满足对应功能预期。充分证明的no_go可以交Owner作为研究结论，但失败case原样保留，不能写成“所有功能通过”；必要项无证据仍为blocked/not_run。

| AC | 对应需求/场景 | 可核验标准 |
| --- | --- | --- |
| AC1 | R1/R14、§1/§3 | 独立namespace/Task ID/Capability/接受链、draft及五路径准确；004文档接受不移作G0批准；当前只spec，无空tasks/checklist/工程/执行。 |
| AC2 | R2/R3、P0 | §2/§3的精确source/package/hash、工具链、依赖、入口、端口与动作取得r3批准后才创建/构建；B0记录生成binary SHA、实际链接/ABI、完整预算公式后才进行协议运行。未齐或漂移则blocked，不编造当前binary hash、不自动更新依赖。 |
| AC3 | R3/R13、§2 | 候选比较与推荐顺序有primary/冻结源码依据；明确Rust wrapper/Python stub、系统dispatch及资源控制不足，给可复现adopt/reject/blocked及最终go/no_go；不自写完整协议栈或放宽保护。 |
| AC4 | R4/R5、W01 | 合法真实写成功、唯一commit/seq及原始bytes/typed读回一致；独立QA可从raw item和image核实。 |
| AC5 | R3/R4、W02/W09 | 静默/屏障下全触达bytes/hash/seq/版本/时间不变，真实失败且调用/提交顺序证明无先写后恢复；并发另按合法item范围和点版本对账，不要求全局hash冻结。 |
| AC6 | R4/R6、W07 | 六来源全部收口，普通UI/一次性维护范围及CAS、rule暂停不让权、init/reset停机权限/旧epoch均实证；harness与产品UI/持久功能边界准确。 |
| AC7 | R5、W03 | 合法bit邻位保留、100轮同byte两bit无丢失、合法全byte与含禁bit整byte拒绝均可重现。 |
| AC8 | R5/R8、W04 | 部分标量、跨权限/边界/长度/transport/count/载荷与REAL负例逐项真实失败，不越界/无隐藏分配；合法大端/有限REAL对照可读回。 |
| AC9 | R5、W05 | STRING[8]/[254]全包成功及头/长度/ASCII/截断负例不变，raw包、item结果及完整包hash齐全。 |
| AC10 | R3/R5、W06/W08 | 多item部分成功/保序、失败范围不变且非PDU全原子；非白名单系统操作明确拒绝/关闭、无DS/宿主副作用，不接受“成功空操作”替代。 |
| AC11 | R7、C01/C02 | 16真实S7会话同时读写、第17条20次拒绝不抢占；计数从TCP/H到C/closing/释放逐态对账；1–64/>16未测及全局128/32/160与64线程关系准确。 |
| AC12 | R7/R8、C03/C04 | H满/握手、绝对半报文、正常idle、真实慢接收send及释放期限均有起算和原证据；未实际触发send不报通过。 |
| AC13 | R8、C04 | per-connection/instance/global数量和所有阶段bytes/最坏输出预留先准入，超限无item执行且归还一次；小预算/故障注入与实际大上限未触达准确分层，owner无网络/磁盘等待。 |
| AC14 | R9、C05 | 连接与工作类按item轮转/保序、规则合并、A/B低频及UI/普通控制/stop可达；正常60s内A/B各120请求全完成、60次合法UI全成功，不能靠准入外全拒绕过公平。有资格和调度轨迹、逐连接分位数/拒绝分母及恢复回落，不能仅总吞吐。 |
| AC15 | R2/R10、D01 | 精确DAA ManagedS7真实feature、RemotePort/rack/slot/COTP/读链与240次db_read可定位；不改DAA、不读真实env/profile、上传关闭；模块级与完整产品界限清楚。 |
| AC16 | R7/R10、D02 | 错TSAP/端口、双端口身份隔离/端口冲突/重复start负例均可复现，不回退102/抢占/隐式复用；私有API/feature不满足时blocked而非换fixture。 |
| AC17 | R4/R9/R11、W09/X01 | stop/单close先封准入取消未入段，仅当前不可取消item完成；未知回执与确定拒绝分开，无回滚/自动重试，超时不假stopped，其他连接/实例继续。 |
| AC18 | R7/R11/R12、C06 | 160重连、20启停、3reset有原始序列；socket/callback/worker/timer/队列/预留回B0且可同端口重绑，重复释放幂等，RSS/线程/句柄按定义无超额增长，保值/初始化语义不混同。 |
| AC19 | R2/R11、X02 | 若选sidecar则父子正常/异常退出与A/B崩溃隔离3轮证据满足5s边界；不选时理由与进程内native风险可审阅，不把G0管理harness当Tauri原生/三平台证明。 |
| AC20 | R2/R12、全矩阵 | 每run source/ABI/环境、raw item/bytes/事件/错误、1Hz资源和状态转换可关联，offered全分母、逐连接p50/p95/p99/max、CPU/RSS/线程句柄/队列/规则missed/stop均报告；C01/C05算术正确，证据缺口不算pass。 |
| AC21 | R1/R13/R14、§9/§10 | go/no_go与case/QA/Owner层次分开，fail/blocked/not_run/deferred真实；候选失败或改范围回PM，不把004/G0/文档检查当产品批准；既有文档/并行dirty/旧receipts保护，DEV与新fresh QA逐角色真实建立。 |
| AC22 | R2/R10/R15、§2.1/§2.5/§2.6 | accepted manifest SHA、61/61工作树文件、core0.1.0/API/profile/v1及五DAA模块/新增引用图可核；新锁静态66registry+1path与未运行解析图分开，路径真实消费、无stub/DAA改动。 |
| AC23 | R16、§2.7设计验收 | canonical增补明确多文件/逐DB UDT闭包和绑定；DeclarationRef非稳定ID，DB号/文件序号非主键；lineage/ID/reimport/CAS/结构停机变更及每instance32DB/4096叶聚合限制可逐项审核。产品消费者case留D1，不伪称G0已实现。 |
| AC24 | R5/R15/R16、§2.7设计验收 | 受限嵌套标准布局理论辅助与STRING整DB拒推、人工确认/coverage/完整instance NameBatch、原字符串碰撞规则/v1样例pin准确；初值零缺省/显式优先、数值范围/大端/BOOL/CHAR/STRING边界齐全，无TIA初值/实机地址/自造oracle承诺。 |
| AC25 | R6/R11/R16、§2.7设计验收 | saved/selected/loaded分离、停机apply/同版幂等/commit未知、九场景typed保值/初始化、页面动作→服务→单owner路径及日志降级一致；D1–D4与Tauri/FFI单owner待独立实施门槛明确，无双image/双规则。 |
| AC26 | R2/R14/R17、§3.2/§3.3 | 正式S文件/八vendor限制、实际五模块路径/core三级相对依赖、CMake源/role build/bin路径可核，正式source全manifest与DEV/QA候选/生成产物SHA闭合；无仅tmp交付或用旧PATH二进制替代。 |
| AC27 | R13/R18、§3.4/§10 | protocol-baseline交接具版本/入口/固定端口DB编码权限marker/限制及全部适用G0证据、fresh QA/Owner事实；未齐仍candidate，no_go不能伪称server。真实DAA应用→SQLite另批，超profile先另spec扩并验收，整体B/C边界准确。 |
| AC28 | R12/R14/R17、§3.2/§3.5 | 必要raw/原命令/build/失败证据由T校SHA持久到A及逐成员inventory，P只5类紧凑清单/索引并被tasks/checklist定位，无raw日志/构建产物入公开repo或仅记hash后删raw；A保留至联合验收后复核，资源归属/回收依赖真实，正式S与旧证据不当tmp清理；当前仅PM spec，r1/r2可逐字恢复、85起点保护及foreign/shared delta如实分类。 |

## 9. 风险、回退与明确排除

| 风险/未决gate | 处置与Owner需审阅的取舍 |
| --- | --- |
| native回调、ABI或默认系统命令不满足 | §2已完成只读筛选；有限扩展先经B0审查/ABI，未闭合不开始协议。返回值/内存入口/拒绝不可控即淘汰，不以回写或成功空操作豁免。 |
| native hook锁/线程/缓冲隐藏，16能连但不公平/不能退出 | C/H/queue/资源可控点是必证；任何不能有界释放/观测的关键面阻止go。通过16也不证明>16或L1–L5。 |
| DAA真实入口与fixture隔离机制不兼容 | 推荐固定真实模块的隔离消费，不改当前DAA；无法安全调用则blocked并申请独立DAA范围。不能利用默认env/生产profile或同名重写client消除blocker。 |
| 原生库/sidecar崩溃影响其他实例 | 先明确实际进程边界；选sidecar须X02，进程内硬崩风险保留并由Owner决定后续隔离。不能用逻辑隔离作OS崩溃隔离。 |
| 静默拒写试验被规则/合法并发污染，或先写后恢复伪通过 | 屏障、不变基线、mutation入口事件及源码链同时使用；并发按item/范围对账，证据无顺序或丢失则blocked重做新run。 |
| 单OS/短程和缓存包被当跨平台/长期能力 | 本轮包/源码已按§2只读校验，构建/ABI实测仍not_run。G0只报告冻结OS与有限profile，目标平台/发布及长负载另批。 |
| 选型趋向大规模协议重写/依赖升级/产品实现 | 当前draft不实施；未来超小adapter/两候选/指定矩阵的工作回PM新Revision，不继续扩写。no_go可以是可信交付。 |

回退只处理本任务明确delta或未来获批owned实验资源；本轮仅spec可逆修订，不reset/覆盖已有工作树。未来实验失败先封准入、按真实提交边界退出、保留错误与原证据；只清理已确认归属且不再承担证据/后续依赖的资源，由主协调收尾，QA不回收。端口冲突不碰占用者；旧004/DAA证据不得删除或改写。

以下排除实施，§2.7设计增补不授予产品权限：完整DS工程/Tauri壳/CU页面/安装包、导入器/点位编辑/配置SQLite/schema/迁移/持久apply/运行值保留九场景、完整DAA采集/历史/上传及DAA修改、Backend/SMA/CA/真实PLC/现场网络、生产数据库/API/上传、Modbus/完整PLC执行或协议栈、长期服务/后台守护、完整L1–L5/8×16扩展、三平台native/发布部署、Git refs/提交/推送、外部消息。G0可用合成内存fixture证明init/reset/stop保值路径；不能把它扩成配置恢复实施。

## 10. 开工评估、批准历史与角色交接

| 门槛 | 本轮事实 / 解除后下一步 |
| --- | --- |
| DAA共享输入 | DAA-006 r3已Owner接受，manifest61/61匹配，真实五模块+core及新锁静态闭包明确；这项输入依赖解除，不是G0运行通过。 |
| 当前执行许可 | Owner已于2026-10-20批准精确r3范围/执行/风险，现交接Development；批准登记时DEV/QA尚未启动、正式工程/构建/ABI/监听/协议尚未执行。真实DAA–DS读取至SQLite联调仍另批。 |
| 原生候选/资源可控性 | 原样Snap7/Python均no_go；native有限八文件扩展仅proposed_for_B0，可编译/ABI/整PDU/C/H/期限/公平/真实join仍not_run。获批后可开始有界B0，不等于全DS服务端具备生产实现条件。 |
| G0协议baseline | 只有正式S交付+全部适用W/C/D/X/AC+独立fresh QA+Owner接受才能交接§3.4；失败no_go返回PM，不绕过保护写全产品。 |
| D1/D2/D3/D4 | core可供另批D1原生导入/配置消费者；D2协议owner选型等G0，D3薄Tauri/UI等稳定合同；D4长负载另批。当前只在正文增补设计，不建立这些产品工程。 |
| DAA整体B与C | 有限G0若足供所需DB可先交接，不必强迫全DS；真实DAA应用S7→SQLite须另spec/fresh QA/Owner接受，超profile先扩DS baseline；B整体未关闭，C排除。 |

| 日期/Revision | 真实历史 |
| --- | --- |
| 2026-10-18 r1 draft | 原G0草案形成，未执行。 |
| 2026-10-19 r1批准 | Owner按§1原话批准精确r1，仅后续只读P0与r2文档修订授权。 |
| 2026-10-19 r2未批准draft | P0来源/ABI缺口/旧三模块闭包/全tmp执行面提案及自检；原完整710行保留附录，不改历史。没有构建/原型许可或运行事实。 |
| 2026-10-20 r3 draft | 根据已验收DAA-006刷新五模块/core/锁，正式源码交付、整体设计增补与有限协议baseline提案；草案交接时待r3精确批准。 |
| 2026-10-20 r3批准 | Owner按§1逐字原话批准SHA bd2df8339f904aec4744b6d0d254fa9becc2bdd0ac53a5e90c43447261341379的精确r3；独立模拟器定位澄清既有方向，当前进入Development，未运行事实及最终接受不提前填写。 |

当前PM使用aiis/project-governance；角色profile为contract_only，精确spec/串行角色/diff审计不宣称平台ACL。未来Development按实际面加载rust-runtime（真实DAA Rust入口/长连接资源/FFI）、plc-point-mapping（点/地址/类型核对，**命名/样例精确以已选core0.1.0为准，不额外引入通用XLSX/YAML流程**），遵aiis跨语言结构/日志与资源基线。desktop-tauri/frontend-ui/i18n-workflow留未来明确批准的D3；此G0不加桌面工程。无backend/Celery/DB维护范围。

PM向唯一主协调交已批准精确r3/SHA、批准delta及自检，随后停写；协调只机械同步四根既有005索引行并启动实际Development创建tasks，从正式S/设计同步/B0串行推进。r1/006批准不替代本次精确r3批准或后续运行gate。精确developer_handoff后实际新fresh-context Verification（fork_turns=none）创建checklist，独立核正式树/协议/字节/失败/资源及文档设计增补，再交Owner最终接受。QA通过不自动授权联合SQLite/C/发布/真实设备。

Human Owner exact ARCH-AW-005 r1 scope approval: **approved, 2026-10-19**。

Human Owner exact ARCH-AW-005 r2 execution approval: **never granted; historical draft**。

Human Owner exact ARCH-AW-005 r3 scope/execution/risks approval: **approved, 2026-10-20**；原话及批准前草案SHA见§1。

At approval recording: B0 build/ABI and G0 19 runtime cases: **not_run**；Development / Verification: **not_started**。后续实际执行/独立verdict以tasks/checklist为准，本批准记录不提前填写结果。

Human Owner final acceptance of ARCH-AW-005 / usable protocol baseline: **pending**。

## 11. r3草案形成阶段PM自检与未执行项（历史）

以下为草案交接时的真实自检与未执行快照，保留原结果/证据，未因本次批准重写为实现或QA通过。

起点为`/private/tmp/arch-aw-005-r3-refresh-ii4zqye9/` before/13文件及protected-baseline.json/85文件；PM role-start逐项确认85相同，accepted manifest61/61匹配；静态source import/新锁闭包为66registry+1path，66个registry name/version/checksum与r2相同，未运行Cargo解析。正式事实、路径及方案均在正文，tmp附件不是唯一依据。已消费当前AGENTS§6、根README/PLAN、AW与shared/core/fixtures说明、完整005 spec和004设计、实际pm TOML/canonical workflow及所需真实源码，旧004/005/DAA receipts不改。

必要自检`/usr/bin/python3 /private/tmp/arch-aw-005-r3-refresh-ii4zqye9/pm/check-spec.py`为exit0：R1–R18、AC1–AC28全覆盖，19个W/C/D/X原case行与r2逐字相同；31个本地链接（含历史、11带锚点）、17张active表、外层历史围栏/全文件尾空白、C01/C05/C06/D01/2208B预算算术通过。r2原710行/131375B和嵌套r1原283行/50843B均可恢复且SHA与输入相同。85起点文件按spec/共享索引/保护分类，保护项及accepted61/61保持；实际五模块相对路径/core三级path依赖核对通过，66registry+1path只是静态闭包。当前S/T/A及tasks/checklist均不存在，公开P只5类索引/仓外A保存raw边界与无环manifest已检查。`git diff --check -- plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md`为exit0；`git diff --no-index --check /dev/null plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md`为exit1、stdout/stderr空，表示untracked文档有差异且无空白诊断。完整命令/退出码、保护/全仓delta分类、历史指纹及最终SHA在本轮pm/document-self-check.json、spec-r2-to-r3.diff与receipt.json；PM不认领或回退共享/foreign delta。这些只是PM文档/事实自检，不是实现、编译/运行或独立QA。

本轮仅PM文档修订与stdlib事实/链接/哈希/算术/恢复/范围检查；没有工程/产品代码/测试/依赖/锁/profile/tasks/checklist写入，没有编译/安装/库加载/ABI/程序或原型/监听/连接/SQLite/联调/设备/API动作，没有新增运行服务/端口/后台进程/浏览器/worktree。S/T/A当前均不创建，不回收任务外或旧证据；将来开发验证/资源收尾仅按获批精确范围。当前自检不是DEV或独立QA，不给r3 verdict/Owner接受。

### 11.1 精确r3批准登记自检

本次仅登记§1批准事实、当前执行gate和Development handoff，不改Revision或技术范围。以`execution-coordinator/protected-start.json`及其before快照为起点，辅助`pm-approval/check-approval.py`核对原18R全文、28AC、19case、S/T/P/A技术表、风险/排除和附录r2/r1原字节，检查Markdown链接/锚点/表格/围栏/空白、精确批准字段及单spec delta；实际命令、退出码、保护哈希、差异和最终spec SHA固定在同目录`document-self-check.json`、`approval-only.diff`与`receipt.json`。旧PM/QA/DAA证据未改。此为PM文档自检，未构建、运行、加载native、监听、创建正式S/T/A或后续角色文件；批准登记不授予PM实施/QA权限，后续由主协调按已获批链激活对应角色。

## 附录A. 未批准r2完整原文（内含r1原文）

以下五反引号text围栏内是r2完整710行/131375B，SHA `fc0ab9a11b4145b994bc3586e014ef87b98148b87c3d2f6a53a65204f4d6379b`，UTF-8/LF含末尾换行。原字节提取即可恢复；其中四反引号内另有r1完整283行/50843B及其获批SHA。旧来源/三模块闭包/tmp工程/未批准gate及自检是历史，不构成当前执行许可或r3事实；保留原文，不改写历史来迎合本轮方案。

<!-- BEGIN R2 EXACT SNAPSHOT -->
`````text
Task ID: ARCH-AW-005
Revision: r2
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: P0 read-only source/ABI/dependency/DAA/port findings recorded; exact r2 execution surface awaits Human Owner approval; no Development, Verification, build, library load or prototype execution authorized by this draft
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS G0 服务端可行性、写前拒写、16会话、真实DAA端口兼容及资源释放的有界技术原型验证
Owner: Automation World
Acceptance Chain Reference: aiis-ics-arch::ARCH-AW-005 r1 scope approved -> P0 read-only / r2 draft -> Human Owner exact r2 execution approval -> Development B0 then bounded prototype handoff -> new fresh-context Verification -> Human Owner final acceptance
Depends On: aiis-ics-arch::ARCH-AW-004 r2 accepted detailed-design baseline
Related Task: aiis-ics-arch::ARCH-AW-002; aiis-ics-arch::ARCH-AW-003; aiis-ics-arch::DAA-002; aiis-ics-arch::DAA-003; aiis-ics-arch::DAA-004

# DS G0 技术原型验证规格 r2

## 1. 目标、批准事实与当前gate

本任务身份、Capability、Owner和独立接受链不变，Classification为root、无Parent Task ID；004的详细设计接受不能转移为G0运行或选型通过。本r2补齐r1要求的P0来源/ABI/依赖、真实DAA模块、端口及未来精确执行面，**不降低r1的14项需求、19个case和21项AC的功能目标或数值**。当前权威为本r2正文；附录A可逐字恢复r1及当时未批准/未冻结的历史，不将其旧gate解释为当前事实。

2026-10-19（Asia/Shanghai），Human Owner在唯一主协调会话`01a14e52-eeb4-7c82-bade-bc0a237fa2ff`直接明确：

> 可以，批准 ARCH-AW-005 r1 spec。接着完成 P0 只读核查，明确候选服务端版本、ABI、依赖、真实 DAA 入口和端口，补齐精确执行范围并整理成 r2 spec，先不改代码、不运行原型。

该批准对应283行、50843B的r1，SHA-256 `00171a46325c1b28359e77b3d2a42434e1ad43ac825b16cdb84f1708695c4c84`。它批准r1范围并授权本次只读研究/PM文档修订，**不批准尚未形成的r2原型执行**。本轮仅PM写spec；不创建tasks/checklist、工程、源码/测试、依赖/lock/profile，不安装/编译/加载native库、不监听/连接/跑协议或负载。本r2完整执行面须Owner审阅；批准后由实际Development先做B0，再逐gate推进，正常生成的binary digest由B0真实记录，不要求事前编造。

交付目标仍是可信的候选go/no_go及限制，为DS后续实施提供依据；no_go可以是有效研究交付。G0不实现完整PLC协议栈、产品UI/SQLite/采集应用，不授权D1–D4、L1–L5、三平台发布或真实设备动作。本次完成的是**P0只读事实和可审阅执行方案**，不是P0/B0运行通过或QA verdict；全部19个运行case当前`not_run`。

## 2. P0只读定版与选型决策

### 2.1 已验收依据与本次读时快照

已消费[004 r2 spec](../ARCH-AW-004-ds-detailed-design/spec.md)、[Development](../ARCH-AW-004-ds-detailed-design/tasks.md)及[Owner接受](../ARCH-AW-004-ds-detailed-design/checklist.md#owner-acceptance-r2)。497行[DS详细设计](../../docs/AIIS_DS_Detailed_Design.md) SHA为`0eb3c149bf7093bbdce2f0b7a07af71e769fe24cb04a542c7f4dc43e6979eecb`；直接继承[§5.2/§5.4生命周期](../../docs/AIIS_DS_Detailed_Design.md#lifecycle)、[§7/§8内存/协议](../../docs/AIIS_DS_Detailed_Design.md#protocol-memory)、[§10选型](../../docs/AIIS_DS_Detailed_Design.md#selection)和[§11分阶段验收](../../docs/AIIS_DS_Detailed_Design.md#verification-stages)，不重开004。

DAA输入冻结于**2026-10-19 10:47:27 +08:00**的一次快照，之后不追逐并发会话/索引：当时DAA-002 tasks为developer_handoff/checklist为qa_passed（QA4文档闭环），DAA-003 tasks为developer_handoff/checklist为qa_passed（QA2），DAA-004 spec为owner_approved且尚无tasks/checklist；这些独立任务的最终接受不由本spec推断。当前README已说明003后的普通应用SQLite-only启动；本G0不调用应用启动/迁移/导入流程。r1旧DAA状态完整保留为附录历史。

宿主只读快照为2026-10-19 10:46:25 +08:00：macOS15.7.7(24G720)/arm64，Apple M4，`number_processors=proc 10:4:6`、逻辑CPU10、RAM32GB；Apple clang17.0.0(clang-1700.4.4.1)、macOS SDK26.1（`/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk`）、CMake4.0.2、GNU Make3.81；直接工具链rustc1.89.0(29483883eed69d5fb4db01964cdf2af4d86e9cb2)/cargo1.89.0(c24e10642)，target `aarch64-apple-darwin`；`/usr/bin/python3`为3.9.6，只供stdlib编排/证据。sysctl硬件/动态端口段读取被sandbox拒绝，未升级权限；硬件由system_profiler选定非敏感字段替代，SSD介质/内核动态段未核，实际run前必须记录介质和背景负载。只报告这个明确OS/架构，不外推Windows/Linux；工具存在不等于能构建。

### 2.2 精确候选、包来源、许可与推荐顺序

| 顺序 / 精确输入 | 只读证据与决定 | 后续边界 |
| --- | --- | --- |
| 首选试验候选：官方Snap7 **1.4.2** 源包 `snap7-full-1.4.2.7z`，20591252B，SHA `1f4270cde8684957770a10a1d311c226e670d9589c69841a9012e818f7b9f80e` | 本轮从[官方SourceForge包](https://sourceforge.net/projects/snap7/files/1.4.2/snap7-full-1.4.2.7z/download)只读下载，完整包SHA与发布页相符；只提取源码/许可为数据，未提取/加载发布二进制。选旧版的明确理由是能核到真实resourceless返回链且与DAA固定crate内关键native文件同字节；不是宣称它是最新版或已支持arm64。 | **原样版本no_go；有限扩展方案仅proposed_for_B0，尚非adopt/go**。只允许§2.4的server私有副本改动；先B0可编译/ABI及有限性审查，再P1。不能用源码下载成功当ABI/安全/性能通过。 |
| 至多一个备选：python-snap7 **3.2.1** sdist `python_snap7-3.2.1.tar.gz`，295424B，SHA `15748f8423e3726457f6c4d0202aabde4ad65f2b809c2c1e7ee4f2f776509c2b` | 本轮[PyPI元数据](https://pypi.org/pypi/python-snap7/3.2.1/json)与其sdist的SHA吻合；[版本化API](https://python-snap7.readthedocs.io/en/3.2.1/API/server.html#snap7.server.Server.set_rw_area_callback)及冻结源码均显示rw callback为stub。`_handle_write_area`直接改registered memory并构造单item成功，stop先报STOPPED再有限join/清列表；源码尚无本合同的多item/完整预算/释放保证。 | **该精确备选no_go，不进入构建或运行**。修成合格服务端需改写超出小adapter的处理面，本r2不授权。首选失败后无自动合格备选；回PM决定新Revision，不偷偷改Python/DAA或自研协议栈。 |

官方项目当前[1.4.3说明](https://sourceforge.net/projects/snap7/files/1.4.3/)指向[官方GitHub](https://github.com/davenardella/snap7)，其可变main/新版本不在本r2选用面；未来换版须新Revision。官方[resourceless](https://snap7.sourceforge.net/res_servers.html)、[server规格](https://snap7.sourceforge.net/snap7_server.html)与[API](https://snap7.sourceforge.net/snap7_api_ref.html)仅辅助说明；实际决策以本节冻结1.4.2源码为准。

许可材料：原生源头声明LGPL-3.0-or-later，包内`lgpl-3.0.txt` SHA `ea7d049c7705dc13afc202dd18e1827f3484f8212fd3fa7b82fc4a0c363432c9`、`gpl.txt` SHA `0b383d5a63da644f628d99c33976ea6487ed89aaa59f0b3257992deac1171e6b`；Python包LICENSE为MIT、SHA `3c88a113fc8ffbc81cf9f7fd8a4bd040f39ad1b88e099e8173eea1dc6df14544`。DAA所用rust-snap7包manifest声明MulanPSL-2.0（LICENSE SHA `89591a592b25a07a294c67c0767bb2b061a60e544d76f4bbc438192882f34e92`），其build.rs头另写GPL-3.0-or-later、native另有LGPL，B0保留全部原许可/源材料及链接清单，不据顶层单一license字段作分发许可结论。本G0仅owned本地实验，不发布/再分发。

以下为官方包内**必须保持原始起点指纹**的关键源码；整个包SHA固定其余文件，B0另生成全source manifest及有限patch的before/after/diff，不能只交这些摘要。`src/`以下路径相对`source/upstream/snap7-full-1.4.2/`。

| 相对原生路径 | SHA-256 |
| --- | --- |
| `src/core/s7_server.h` | `ebfe5f185c904624cc74b10419c454001c27b37a3ffbec7b0232ae2c494c1ecc` |
| `src/core/s7_server.cpp` | `e1007486fbf2c738e01628dd4e394de32af08a772227f3e3d07dc4437b128ad3` |
| `src/core/s7_types.h` | `feb97ffb241494f13db231e39fcb48a879efda74e7e240caddcb07139a92f300` |
| `src/core/s7_isotcp.h` | `313c5167f3769367b38073c62da6d1a1c49b63a7016016caf3743666639a2c5f` |
| `src/core/s7_isotcp.cpp` | `7c06fa33f0e34afe88962322c5fa946f3072ceeb1a0cc5d2cbdb71c7ac43e6b7` |
| `src/sys/snap_platform.h` | `d7f4e9dc2e5af523258437ae22c6109c98aa5b263881db16479fa5dfed884b47` |
| `src/sys/snap_msgsock.h` | `570f97d27da11dcc08650897a5dd27bc939a53598dc15d45c85b64366ca1e0c3` |
| `src/sys/snap_msgsock.cpp` | `bded0cc9e642aaff22b8a16e0bfae5f5eca7e346769ec6f8ba582b00bae9ba51` |
| `src/sys/snap_tcpsrvr.h` | `0a2d8d354b2d78a3155633b5e4bcd7b4f88937aa8ed7afe3a1d832995feafba4` |
| `src/sys/snap_tcpsrvr.cpp` | `b6365fddff816d4c3faf6b7d40c56e394e8ca0aa7c2bca16b3431d12d11eb747` |
| `src/lib/snap7_libmain.cpp` | `3e4a186471b41ead3a80e2d6ce94cec1e7ccc17920b6936a07ead14b274bd643` |
| `release/Wrappers/c-cpp/snap7.h` | `3e2a4edd86b5adfa4a73f64c81d0e0f1316df1da54785fa61dd293f728c4c401` |

Python关键文件`snap7/server/__init__.py` SHA `d17a8c1a5a9b96154d9882d3fc3766fb2c53c35af5f5b7c5aebf95b8f2c40e72`只作no_go证据，不是未来改动路径。

### 2.3 原生C ABI、提交时序与尚未通过项

冻结头`s7_server.h`定义`extern "C"`内的`int (S7API *)(void *usrPtr, int Sender, int Operation, PS7Tag PTag, void *pUsrData)`；macOS的`S7API`为空，按目标C调用约定，Windows分支`__stdcall`不在本次验证。`s7_types.h`在`#pragma pack(1)`内定义TS7Tag五个int：Area/DBNumber/Start/Size/WordLen；目标**待B0实测**的sizeof(int)=4、Tag size20/align1、offset0/4/8/12/16、pointer8。OperationRead=0/Write=1。C++harness直接使用原native头和**返回int**的callback，不手写另一套FFI布局；任何不符即blocked/no_go，不能调整探针期望掩盖ABI差异。

已核1.4.2源码链为`TIsoTcpWorker::ExecuteRecv -> TS7Worker::IsoPerformCommand -> PerformPDURequest -> PerformFunctionWrite -> WriteArea -> TSnap7Server::DoWriteArea -> OnRWArea(...) == 0`。resourceless下callback返回0才使WriteArea生成0xFF item成功，非0走`WA_NotFound/Code7ResItemNotAvailable` item失败；PerformFunctionWrite逐item填结果，再isoSendBuffer响应。**callback非0不能精确映射自定义权限错误细分码**，G0接受真实item失败而非假成功；W06仍要求逐item部分成功。read链使用DoReadArea/callback填worker响应stage再编码；RegisterArea路径会直接mask/memcpy共享区，G0必须禁止注册image/裸指针。events是在处理之后，不能当拒写入口。

Tag是callback栈对象，pUsrData为该worker的请求/响应buffer借用，均只在同步callback返回前有效；写数据必须在预算内复制成owner请求，不把Tag/原指针交给异步队列；读快照复制回原stage后才返回。usrPtr及hook上下文存活到所有callback归零且worker已join；异常不得跨C边界，失败返回非0，不能在commit后因日志失败改回失败。Sender来源是peer地址/ClientHandle，**不是连接唯一ID**；同loopback多连接必须用accept分配的connection ID、worker上下文及受控TLS item/PDU关联，不按IP或Sender授权/计数。

rust-snap7 **1.142.2**固定crate SHA `8c4d43b3a99825abd300d57a0888eda7b625b7cdbf56ee7766bd02331ac58243`已从现有cache完整包计算，与冻结DAA Cargo.lock checksum相同；关键native server/type/socket文件与官方包相同。其`src/server.rs` SHA `e46c5f1400e1e36a65dcfff9810e39f338cf959f85675145041225ae5dbd9ee2`中的FnMut/trampoline及`src/ffi.rs` SHA `3b64e4ea1aa470ad6f37e9672c070a96fb1f60bda76d964f6b1636e406a0f465`的pfn_RWAreaCallBack返回void，不能传回native所需int。**不采用该高层server、不在DAA依赖内修FFI**；该crate只用于原DAA真实client。crate缓存完整性与冻结项目锁相符，独立crates.io元数据获取403，未声称已获第二注册表证明或已可构建；该限制保留，B0仅可用匹配既有锁的包，不能联网换版本。

### 2.4 未修改上游的缺口及有限扩展提案

原样native虽有写前int链，但公开MaxClients只数TCP worker（0还代表无限），DoReadArea/DoWriteArea的全局CSRWHook包住callback；ISO连接默认回CC、S7协商原样echo AMQ，系统分支会处理CPU/clock/SZL等；SendPacket一次send/RecvPacket分段超时不能提供本合同绝对期限；TerminateAll超时会KillAll并清ClientsCount，Stop随后直接报stopped。因此**原样native no_go**，不能靠set_param/一个写callback进入P1。以下只是可审查的有限扩展提案，尚未实施或证明足够。

未来只在`source/patched/snap7-full-1.4.2/`修改表中八个原生文件；调用点附近增加guard/hook及server限定IO/生命周期修复，不改wire format、S7 item编解码或建立另一处理循环。全PDU descriptor/typed准入/公平在独立harness中完成，native原有解析/编码继续复用。**若实际需要迁移/替换ISO/S7主循环、修改本表外原生文件/DAA crate、重写TSnapThread框架或自行补完整协议栈，该候选停止no_go/blocked，回PM新Revision；不得以“adapter”称呼掩盖重构。**B0先出完整diff/调用图/控制点覆盖，未能证明有限性不得开始协议运行。

| 精确文件与原有函数/位置 | 最小必要改动及可审查结果 | B0/P1以后仍须证明 |
| --- | --- | --- |
| `src/core/s7_server.{h,cpp}`：TIsoTcpWorker::ExecuteRecv；TS7Worker::IsoPerformCommand/PerformPDURequest/PerformPDUUsrData/PerformFunctionNegotiate | 在原路径前加入受控server hooks：COTP CR的calling/called TSAP检查后才CC；S7 setup前C/H转换容量检查及AMQ=1、PDU≤480；只白名单setup/read/write及有界disconnect，其他系统分支拒绝/关闭且不调用原处理函数。 | 握手真实C提升时机、错TSAP、所有系统请求均到guard，不能以函数名称或CC已发当会话成功。 |
| 同两文件：TS7Worker::IsoPerformCommand/PerformFunctionRead/PerformFunctionWrite，TSnap7Server::DoReadArea/DoWriteArea | 第一item前对整个PDU做边界/最多4items/最坏响应检查与原子预留，再让原item循环调用hook；item上下文记录connection/PDU/index。仅G0受控resourceless分支不持CSRWHook等待owner；配置callback只在封闭gate，native非G0行为不变。 | 预留失败item0也未提交；逐item结果/内部顺序及跨连接公平；所有byte仍只由owner提交，callback解除外锁不制造并发image写。 |
| `src/core/s7_isotcp.{h,cpp}`：TIsoTcpSocket::isoRecvPDU/isoRecvFragment/IsoConfirmConnection/isoSendBuffer | 透传server限定的frame/PDU绝对deadline与剩余额度；每frame≤512、重组总量≤480，分片不重置起点；暴露完整COTP参数给guard，不另写ISO解析/确认循环。 | 畸形/滴流、多个fragment、输入预算及错TSAP；若必须重写这些函数的协议处理算法即越界停止。 |
| `src/sys/snap_msgsock.{h,cpp}`：TMsgSocket::SendPacket/RecvPacket/WaitForData及server上下文 | server专用有界部分send/recv循环，monotonic绝对期限、停止唤醒/非阻塞剩余等待，首byte/首次send尝试采样；socket buffers设定并读回。client/default分支不改。 | 真慢接收send阻塞、短IO、断连、首次发送2s deadline；不能只设置SO_RCVTIMEO/每次调用相对timeout。 |
| `src/sys/snap_tcpsrvr.{h,cpp}`：TMsgListenerThread::Execute，TCustomMsgServer::CanAccept/Incoming/CreateWorkerSocket/Delete/TerminateAll/Stop，TMsgWorkerThread构造/Execute | 在原listener现有loop的SckAccept之前先预留H/TCP及全局额度；accept失败/准入关闭/创建worker失败均归还一次，不重写loop；成功后分配唯一ID并转交Incoming。受控worker保持FreeOnTerminate=false，在Execute内同步记录本线程pthread_self；reaper等其完成通知后，以该ID执行真实pthread_join，返回后才销毁worker/socket/回调上下文和归还名额；新增字段/方法仅在本行已列两文件内。stop先封准入和cancel未提交，已入段单item完成，唤醒网络并有期限退出；受控分支禁KillAll/提前清零/无条件stopped。 | macOS原创建分支为joinable，但TSnapThread的WaitFor/Closed仅为状态等待，不能作为join或释放证明，不读取unix_threads.h私有th、不改线程框架。真实pthread_join返回后才归还；超时保留stopping/failed/closing及所有权，B继续；重复close幂等。无法在这八文件边界完成即B0阻断，不把断连event/移出表当线程已退出。 |

预留公式在此固定：对PDU p，`Q(p)=I(p)+D(p)+S(p)+K(p)+O(p)`；I为保留输入（≤480B），D为每item固定描述符（最多4×64B，无隐藏动态成员），S为typed stage（总≤480B），K为额外payload复制（总≤480B），O为最坏响应frame预留（≤512B，含失败码/填充，成功与失败取较大者），即每PDU显式池上限2208B，第一item前全额原子预留。若native实额要求额外副本/descriptor超64B，必须增加实际charge且仍满足原上限，不能沿用2208隐藏存储。每连接Bconn=未完frame实际capacity+native固定/临时protocol storage+Σ已预留Q+其他实际副本且≤64KiB；native源已有4096B IsoPayload和4096B Answer，不能只按协商480B计。socket实际SO_RCVBUF/SO_SNDBUF另作受限OS资源预留/观测并在C04均≤16KiB，线程stack另列RSS。实例/全局等待预算分别为全部queued PDU的Q及其未完/暂存实际持有bytes之和（1MiB/4MiB及64/256PDU、实例1024items）；同一backing跨阶段只转归属一次，新增副本新增charge。活动native buffer、OS socket与等待池分类列账，不能互相漏记。B0必须以sizeof/capacity/调用点核表并给活动+等待合计峰值，协议阶段再按真实socket读回/阶段事件核对；超限即阻断，不伪造尚未发生的实测值。

内存owner不能等待网络/磁盘；worker等待owner也不能持库global hook/list锁。每连接最多1个native执行PDU，可不启用额外等待PDU（上限2不是必须填满），OS未读bytes/socket buffer仍实计；不能用该实现选择减少r1 offered吞吐/公平目标。控制点缺失、预算无法观察或大范围改动都是阻断，不以测得最终值相同替代。

### 2.5 真实DAA模块的最小隔离消费

DAA package为`aiis-data-acquisition-agent`0.1.0。以下源直接从本仓库**按SHA校验后原样复制**到隔离harness同名module tree，不能近似重写domain/Plc、改cfg或运行原模块的cargo test。未来执行前若仓内任一源已漂移，先blocked并回PM核Revision，不追着并发修改自动取新版。

| 仓内只读来源（前缀automation-world/data-acquisition-agent/src-tauri/） | SHA-256 / 最小实际依赖 |
| --- | --- |
| `src/infrastructure/managed_s7.rs` | `4ce9a9bfbe81c63453a6444d9b8e719fce6afa8e72ea84e0ca561dda8b48ca0e`；crate::domain::local_configuration::{LocalResult,Plc}及rust_snap7::S7Client。 |
| `src/domain/local_configuration.rs` | `4fde04ad55ca50553706a9d61e5bb0147f26e0286b48ec99c3478db0736e0ad9`；serde/serde_json/uuid及super::local_sample::digest，不能换stub类型。 |
| `src/domain/local_sample.rs` | `a30a1909bd7b50ae26aa0cde27e9b193c82760ad7f940457107c31688f44f06a`；local_configuration::{id,Point}、serde/serde_json/sha2/chrono；两个domain module互相引用，必须同时消费。 |
| `Cargo.toml` / `Cargo.lock`（只读锁定依据，不构建整个DAA） | `38dab0b0b39d6b01150aa28ca8aaca4852aba713fe98f5923b6ce828b3cddbd2` / `fe840bec96fd9348f9230e67368b72f6971827cd3f888ef4173b4e7f0b0ebefc`。 |

独立binary crate的main声明同crate的`domain::{local_configuration,local_sample}`与`infrastructure::managed_s7`，pub(crate)可在同crate调用；这从源码可行，**尚未编译证明**。harness feature `rust-snap7-driver=[dep:rust-snap7]`开启，`local-validation=[]`声明但必须关闭，`cfg(test)`关闭；因此只走原ManagedS7生产driver分支，原文件内测试不会编入/运行。直接调用原Transport::connect/read/read_bounded/disconnect/connected及Drop，不引入LocalEngine/LocalRuntime、Tauri、SQLite/SeaORM、bootstrap/importer、上传/Backend/API模块。独立入口若仍无法编译/安全消费则blocked，不擅改DAA。

已核调用链：ManagedS7先set_param(RemotePort=Plc.port U16、PingTimeout=1000ms、SendTimeout/RecvTimeout=500ms)，再S7Client::connect_to -> Cli_ConnectTo -> TSnap7MicroClient::ConnectTo；其默认PG ConnectionType=1、SrcTSap=0x0100，DstTSap=(ConnectionType<<8)+(rack*0x20)+slot。A指定rack0/slot1→called0x0101，B rack0/slot2→0x0102；calling期望0x0100，由未来raw COTP核对，不能用静态公式冒充wire证明。read进入db_read；read_bounded把remaining/2截为1–500ms设置两socket timeout后走原read；disconnect/Drop仍为原代码，不改重连或错误语义。

D01每连接每轮先原read(57,0,64)，再原read_bounded(41,该实例hold槽起点,8,400ms remaining)，因此60s×2连接×2读=240次db_read，未增加原请求总数；实际调用/超时设置及wire分别保存。

隔离参数仅显式内存Plc，host强校验127.0.0.1、端口见§3.2，enabled=true、随机id仅本run、deadline_ms=5000；无配置自动发现。profile只存公开合成marker/limit/manifest，不是DAA业务profile、不建DB。新进程用白名单env（DS_G0_RUN_ROOT、显式TMPDIR/CARGO_HOME、绝对工具链/locale/PATH），不改HOME或CODEX_HOME，不读真实.env/default profile，不继承DAA_MODE/LOCAL_VALIDATION、BACKEND、DATABASE、MYSQL、授权/上传等业务变量；不存在上传模块/HTTP client，不仅依赖“upload=false”。不调用DAA真实应用启动、不停止它已有进程、不访问102端口。

### 2.6 语言、工具链、直接和传递依赖冻结

推荐服务核心是**C++17 standalone G0 harness + 官方native私有副本**，不是由Tauri锁定Rust；真实DAA互操作小入口用Rust2021，二者不同进程，Rust crate内native client保持原样。C++只用SDK libc++/libSystem/pthread及原生源码，不加第三方JSON/队列/DB包；公开合成证据由简单固定字段JSONL和stdlib collector生成，typed image/调度不是通用框架。Python3.9.6 stdlib只编排/哈希/数据生成，不作为S7server或近似DAA客户端。

Rust直接依赖全部精确`=`：rust-snap7=1.142.2（optional、仅driver feature）、serde=1.0.228（derive）、serde_json=1.0.150、uuid=1.23.3（v4）、sha2=0.10.9、chrono=0.4.45（default-features=false/clock；rust-snap7自身chrono默认feature的统一结果必须在B0记录）。crate build.rs固定SHA `62aa125e5ecf01b3d2690bd3360b39aa83e525836d7f7d93bddff20b08ed00f7`，用cc编译包内native/*.cpp，不下载另一二进制。server使用独立动态库，DAA client由该crate静态编native，不能把两者的链接/ABI证明混为一谈。

从冻结DAA lock对上述六根做**静态依赖全闭包**得到以下66个精确package（含未必在macOS/所选features启用的目标分支）；全部66个现有`.crate`包本轮SHA与该锁相应checksum相同。该事实仅是cache完整性，不是依赖能解析/编译/许可全部适用的证明。每个checksum以本节锁文件的SHA固定，B0复制该锁作种子，仅在隔离root离线生成harness自己的锁；生成后全部{name,version,source,checksum}必须为此精确集合子集，缺包/新增/换版或MSRV不符即blocked，禁止联网更新/安装补救。实际激活closure与feature树由B0冻结并记录，不能把静态66包说成实际链接66包。

| 静态闭包分组（全部名称+精确版本） |
| --- |
| aho-corasick=1.1.4；android_system_properties=0.1.5；anyhow=1.0.102；autocfg=1.5.1；block-buffer=0.10.4；bumpalo=3.20.3 |
| cc=1.2.65；cfg-if=1.0.4；chrono=0.4.45；const-oid=0.9.6；core-foundation-sys=0.8.7；cpufeatures=0.2.17 |
| crypto-common=0.1.7；digest=0.10.7；find-msvc-tools=0.1.9；futures-core=0.3.32；futures-io=0.3.32；futures-macro=0.3.32 |
| futures-sink=0.3.32；futures-task=0.3.32；futures-util=0.3.32；generic-array=0.14.7；getrandom=0.4.3；iana-time-zone=0.1.65 |
| iana-time-zone-haiku=0.1.2；itoa=1.0.18；js-sys=0.3.102；libc=0.2.186；libm=0.2.16；log=0.4.33 |
| memchr=2.8.2；num-traits=0.2.19；once_cell=1.21.4；pin-project-lite=0.2.17；proc-macro2=1.0.106；quote=1.0.46 |
| r-efi=6.0.0；regex=1.12.4；regex-automata=0.4.14；regex-syntax=0.8.11；rust-snap7=1.142.2；rustversion=1.0.22 |
| serde=1.0.228；serde_core=1.0.228；serde_derive=1.0.228；serde_json=1.0.150；sha2=0.10.9；shlex=2.0.1 |
| slab=0.4.12；subtle=2.6.1；syn=2.0.118；typenum=1.20.1；unicode-ident=1.0.24；uuid=1.23.3 |
| version_check=0.9.5；wasm-bindgen=0.2.125；wasm-bindgen-macro=0.2.125；wasm-bindgen-macro-support=0.2.125；wasm-bindgen-shared=0.2.125；windows-core=0.62.2 |
| windows-implement=0.60.2；windows-interface=0.59.3；windows-link=0.2.1；windows-result=0.4.1；windows-strings=0.5.1；zmij=1.0.21 |

未来CARGO_HOME只拷贝已匹配的cache/source/index为隔离副本，不修改~/.cargo、项目Cargo文件或全局toolchain；`--offline`始终生效，首次离线lock派生后`--locked`。若可复现解析仍失败，保留错误/graph并blocked，不将“已有cache”改写为B0已通过。所有依赖材料、source及license清单交接，当前未运行cargo metadata/tree/build或任何build.rs。

## 3. 当前写入边界与拟批准执行面

### 3.1 当前五个仓库路径与角色

当前只授权P0只读/PM修订；以下五路径仍为文档边界，**PM只写第一项**，主协调在PM最终handoff后机械同步四根索引本任务行并保留DAA等并发变化。

| 精确路径 | 当前允许内容/责任 |
| --- | --- |
| `plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md` | PM/Human Owner；本r2 draft、来源/精确执行提案、r1批准和完整历史。 |
| `PLAN.md` | 主协调；仅ARCH-AW-005行Revision/r2 draft/下一Owner gate。 |
| `PLAN.zh-CN.md` | 主协调；同一行中文对应。 |
| `plans/README.md` | 主协调；同一task目录行，只链接实际已存在角色文件。 |
| `plans/README.zh-CN.md` | 主协调；同一目录行中文对应。 |

本轮私有证据root为`/private/tmp/arch-aw-005-r2-p0-_ap0y325/`，PM可在其`pm/`保存只读下载/提取的原文、来源快照、stdlib文档检查、delta及receipt；不是原型源码或未来执行许可。旧004/005证据、receipts不变。不得创建下列未来文件或运行其动作。

### 3.2 固定owned端口与进程边界

| 用途 | 精确endpoint及身份 | 未来动作/负例 |
| --- | --- | --- |
| A | `127.0.0.1:30102`；rack0/slot1/called0x0101、calling0x0100 | 唯一受控A listener；冲突case先由本run owned conflict socket占同址，再启动后来A，必须失败且不影响占用者/B。禁SO_REUSEPORT分流隐藏冲突。 |
| B | `127.0.0.1:30103`；rack0/slot2/called0x0102、calling0x0100 | B listener；A参数误指B仍带0x0101，必须拒绝，marker不同。 |
| 无listener负例 | `127.0.0.1:30104` | 不创建listener；仅三次受控client连接失败负例，禁止回退/扫描/换口。 |

`lsof -nP -iTCP:30102 -iTCP:30103 -iTCP:30104 -sTCP:LISTEN`在2026-10-19 10:46:25 +08:00为exit1且空stdout/stderr，**仅本次未观察listener，不是预约、可bind证明或全用户可见性保证**。三口位于r1建议20000–59999区间；内核动态段未核。未来每次run前同查，任一非本run占用即fail/block，不能kill占用者或自动换端口；不bind0/wildcard、不用102/真实设备。

推荐一个standalone `ds-g0-server`主进程在进程内承载A/B两个instance、各自owner；每accepted native连接一个worker，额外listener/owner/reaper/control/采样设施逐项列入≤64线程/≤1024句柄，而非先承诺固定线程数。A16+B≤1的实际组合必须实测，不推128容量。reference client、DAA harness、Python控制/采样进程另列资源与PID，不混进DS核心CPU/RSS分母。**无产品sidecar/每实例子进程**，故X02父子产品分支not_applicable且必须解释；实验控制脚本spawn standalone主程序不是Tauri生命周期实现，仍登记PID/退出与清理。native硬崩会终止A+B，风险明确保留，不声称进程崩溃隔离。

### 3.3 未来文件精确清单（仅r2批准后）

未来owned root固定为`/private/tmp/arch-aw-005-r2-exec/`（以下记E），创建前必须确认不存在或确属本task且无未知内容；冲突即blocked，不删除/覆盖别人目录。E不在仓库，不成为DS产品工程。DEV/QA分别用`evidence/dev-run-0001/`、`evidence/qa-run-0001/`保存第一轮；重跑只能追加同角色0002、0003等目录并记录原因，不能覆盖旧证据。QA只读已handoff的source/patch/lock，独立写E/build/qa/、E/deps/qa-cargo-home/及E/profile/qa/的下表同类受限派生产物；DEV使用E/build/下非qa路径、E/deps/cargo-home/及E/profile/dev/。两角色串行复用固定30102–30104，只有先前run的PID/socket确认退出和释放后，才fresh绑定并记录新的归属，不新增端口。文件表按角色及产物种类限制，目录前缀不授予任意新增程序权限。

| 精确文件/受限输出 | 责任与允许内容 |
| --- | --- |
| 仓内`plans/ARCH-AW-005-ds-g0-prototype-validation/tasks.md` | 只有r2明确获批后实际Development新建，记录B0/实现/自检/失败与精确handoff；本轮禁止。 |
| 仓内同目录`checklist.md` | 只有精确developer_handoff后新fresh-context Verification创建，独立重现/QA verdict/Owner最终接受；本轮禁止。 |
| E`/deps/snap7-full-1.4.2.7z`、`rust-snap7-1.142.2.crate`；E`/source/upstream/snap7-full-1.4.2/{src/**,release/Wrappers/c-cpp/snap7.h,gpl.txt,lgpl-3.0.txt}` | DEV按已冻结SHA复制/提取包内原始文件为只读；`src/**`仅允许该原包原有源码/header文件，禁止发布二进制/任意新文件；源码包SHA是封闭文件集边界。 |
| E`/source/patched/snap7-full-1.4.2/`相同原包文件集 | DEV只可改§2.4八个文件，其余逐字保持；不改upstream原件/DAA crate；输出`native-g0.patch`供审查。 |
| E`/source/harness/CMakeLists.txt`；`server/main.cpp`、`server/owner.hpp`、`server/owner.cpp`、`server/protocol_hooks.hpp`、`server/protocol_hooks.cpp`、`server/resource_sample.cpp` | DEV最小受控入口、fixture内存、typed准入/六来源/单owner/轮转、native hooks及自采样；无产品UI/DB/通用协议栈。 |
| E`/source/harness/client/reference_main.cpp`、`client/wire_cases.hpp`、`client/wire_cases.cpp`、`native_abi_probe.cpp` | DEV普通请求复用原生client API；有界raw vectors仅生成/独立解码所列19case、COTP/恶意长度/逐item结果；ABI probe无端口。不是新增通用S7协议库。 |
| E`/source/daa-harness/Cargo.toml`、`Cargo.lock`、`src/main.rs`、`src/domain/mod.rs`、`src/infrastructure/mod.rs` | DEV六根精确依赖/features/模块声明与调用驱动；无Tauri/build.rs/应用启动。 |
| E`/source/daa-harness/src/domain/{local_configuration.rs,local_sample.rs}`、`src/infrastructure/managed_s7.rs` | DEV只复制§2.5三份原字节，任一不符blocked；不能编辑。 |
| E`/source/scripts/prepare_data.py`、`run_cases.py`、`collect_evidence.py`、`verify_evidence.py` | DEV Python3.9.6 stdlib；生成合成数据、仅owned启动/调用/停止及证据核算；无下载/包管理/默认env/后台service。QA可审查复用并独立核raw，不能把脚本汇总当QA。 |
| E`/profile/{dev,qa}/limits.tsv`、`points.tsv`、`fixture-a.bin`、`fixture-b.bin`、`manifest.json` | DEV/QA各自生成同一冻结键/整数/来源表及合成初值，来源与§5相同；除role/run ID/输出路径外配置与fixture字节必须一致。manifest含SHA/端口/features/seed/配置与预留公式；不是真DAA profile/正式schema。 |
| E`/deps/{cargo-home,qa-cargo-home}/{registry/cache,registry/src,registry/index}/` | DEV/QA各自仅复制§2.6封闭66包及其既有registry索引，包SHA逐项校验；派生解包checksum清单/Cargo cache记录仅由Cargo在E对应角色副本写。禁止共享cache写入/联网新增包。 |
| E`/build/{native,daa,cmake}/`及E`/build/qa/{native,daa,cmake}/`、E`/tmp/{dev,qa}/` | DEV/QA独立构建器受限派生文件（.o/.a/.dylib/.d、CMake/Cargo记录/manifest/二进制/锁、编译临时）；不是可编辑新实现面。命名产物为`libds_g0_snap7.dylib`、`libds_g0_reference.dylib`、`ds-g0-server`、`ds-g0-reference`、`ds-g0-abi-probe`、`ds-g0-daa`；B0只允许加载/运行无端口ABI probe，闭合前不得运行协议。 |
| E`/evidence/{dev-run-NNNN,qa-run-NNNN}/`内`commands.jsonl`、`source-manifest.json`、`native-g0.patch`、`dependency-graph.json`、`build-manifest.json`、`abi.json`、`limits.json`、`fixture-manifest.json`、`events.jsonl`、`wire.jsonl`、`results.jsonl`、`resources.jsonl`、`processes.jsonl`、`summary.json`、`cleanup.json`、`stdout.txt`、`stderr.txt`及`images/{case}-{step}-{instance}-{epoch}.bin` | DEV/QA各自产生真实附属证据；原始item/时序/字节/错误/资源/生成摘要均可关联。不得覆盖、拿mock/文档检查填运行pass或只在tmp写权威结论；DEV/QA摘要分别回其角色文档。 |

### 3.4 B0构建/ABI生成门槛与允许动作

以下是**待批准的计划，不是本轮已运行命令**。只在Owner批准精确r2后由DEV建立tasks并做B0；B0不能绕过有限扩展审查。构建失败或ABI不符不进入端口/协议。普通派生产物SHA在生成时记录，是执行此冻结source/动作的结果，不另造“下一轮再选版本”。

1. **输入和依赖**：校验本spec包、关键source、三DAA模块/锁/feature及宿主工具链；复制至E，生成全manifest；§2.4有限diff/调用图逐项证明所有guard都可达、未替换协议主循环、没有裸注册image及锁下等待。越界即no_go/blocked，不尝试靠运行掩盖。
2. **C++构建**：用CMake4.0.2 `-S E/source/harness -B E/build/cmake -G "Unix Makefiles" -DCMAKE_MAKE_PROGRAM=/usr/bin/make -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_OSX_SYSROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk -DCMAKE_CXX_COMPILER=/usr/bin/clang++`，再`cmake --build E/build/cmake --parallel 2`；C++17、`-O2 -g -fno-omit-frame-pointer`、libc++/pthread，CMake显式将命名native产物输出E/build/native/。显式原生12个translation units为`src/sys/{snap_msgsock,snap_sysutils,snap_tcpsrvr,snap_threads}.cpp`、`src/core/{s7_client,s7_isotcp,s7_partner,s7_peer,s7_server,s7_text,s7_micro_client}.cpp`、`src/lib/snap7_libmain.cpp`（与原common.mk清单对应）。server动态库用patched集，reference动态库用原upstream集；只编译，不调用make install、不写系统库或DAA工程。最终命令行/SDK/flags/dylib install-name与`@loader_path`相对rpath必须在manifest核实，不能偷偷依赖全局DYLD路径。QA使用同命令参数但-B E/build/qa/cmake、输出E/build/qa/native，不改只读source。
3. **Rust最小client构建**：直接使用冻结stable工具链cargo/rustc，E内CARGO_HOME、CARGO_TARGET_DIR、TMPDIR及SDK/C/CXX显式固定；复制冻结DAA锁作种子，在E/source/daa-harness执行`cargo generate-lockfile --offline`，生成锁的所有条目须为66包封闭集合且checksum相同；保留派生diff，再`cargo tree --offline --locked --features rust-snap7-driver -e features`与`cargo build --offline --locked --release --target aarch64-apple-darwin --no-default-features --features rust-snap7-driver --bin ds-g0-daa`。DEV target为E/build/daa，QA只读该派生锁、用E/deps/qa-cargo-home与E/build/qa/daa及E/tmp/qa，不重新生成/编辑共享锁。不得`--all-features`、test、local-validation或整个DAA构建。依赖解析/MSRV失败则blocked，不自动安装/升降版本。
4. **构建事实/B0 ABI**：在任何协议运行前先计算所有命名产物SHA，保存`file`/`otool -L`/`nm`及实际编译/链接日志，区分server改动库、reference原库、Rust静态client。只运行不bind的`ds-g0-abi-probe`，确认目标arm64、Tag布局/offset/calling convention、int callback的0/非0传回及无异常跨界；测各native固定buffer/worker大小和实际allocator副本，计算`input frame+native buffer+完整PDU+descriptor/stage/copies+worst response`逐阶段预留；socket buffers等需协议阶段读回的字段先标not_run，未补齐前不能该case pass。ABI探针不替代真实item失败/写前拒写。
5. **实际协议**：B0全部闭合后只在上述三端口与owned进程按W→C→D/X矩阵运行。`run_cases.py --case <本spec19case之一> --root E --role dev/qa`只接受显式配置，Python stdlib读取对应E/profile/{dev,qa}/manifest.json校验路径/hash，再调用`ds-g0-server --limits <该角色limits.tsv> --points <该角色points.tsv> --fixture-a <该角色fixture-a.bin> --fixture-b <该角色fixture-b.bin> --port-a 30102 --port-b 30103`；裸入口只显示帮助。server拒绝未列键/越界值，不新增通用JSON parser、不读env或默认输入。control走owned stdin/stdout，不新增控制端口/API。握手白名单、真实C/H/TCP与send期限实证仍是P1/P2，不因B0过关而提前go。

资源自采样为owned进程内Mach/libproc/getrusage与明确关闭的自查询对象，外部ps/lsof交叉核对；CPU=CPU时间增量/墙钟，RSS字节，线程数，FD及Mach port等句柄分项均记录，不能把仅FD数伪称全部句柄。采样失败/权限不足/计数口径不全使对应case blocked，不升级权限或降低≤64/≤1024。B0依赖已加载、image/sink/采样稳定时测资源基线；不以“空进程启动前”当B0。

### 3.5 执行、故障与清理边界

未来DEV负责其owned server/reference/DAA/collector PID、开始时间、可执行SHA和子进程登记；QA使用同E内§3.3精确的独立build/cache/profile/run/evidence路径，source/patch/lock只读，自己负责其启动资源；主协调最终资源收尾。只允许矩阵内timeout/半关闭/断线/接收停滞/预算和提交屏障/丢ack、正常close/stop/reset/start重试及owned port冲突，不操作别的DAA/数据库/API/现场PLC。无产品sidecar时不为了X02引入额外常驻父子服务。

正常退出严格按R11，不可取消item边界不破坏；stop超时先如实记录failed/stopping/closing和unknown，保留当时dump/OS计数。只有明确本run PID且不再可能作为可继续的原型时，允许任务控制脚本SIGTERM，5s后仍不退可SIGKILL作**失败实验清理**并记录信号/退出码，不能将强杀说成正常stopped或通过资源释放；不得按进程名批量kill。控制脚本异常残留由主协调核PID/start/hash后处理，不宣称无orphan已实证。

成功或失败都保留source/patch、锁、构建manifest、raw证据及错误；确认无运行占用后才可删除本次可再生build/tmp/cache副本，不删除角色证据、原始source或旧004/005目录。任何未列实现/依赖/端口/操作、修DAA、完整产品、OS扩展均停止回PM新Revision，不能由tasks自行放宽。

## 4. 编号需求


### R1. 保持G0交付小范围

只交候选决策、最小统一内存/准入harness及真实S7/DAA模块互操作、资源原始证据与限制。所有以下“运行/测试”均指未来获批执行；本轮不执行。沿用004目标，不实现产品UI、DB/UDT导入、SQLite保存/apply、完整规则引擎或完整DAA采集应用。规则、普通UI、一次性维护、init/reset可由标明来源的harness触发；它们验证受控入口，不宣称产品页面/IPC已实现。

### R2. P0来源冻结、B0构建/ABI与执行面

本r2的精确来源、工具链、文件/动作面以§2/§3为准；进入协议运行前须完成B0并有可审查的manifest：候选库精确版本/commit或发布包SHA、完整源码manifest与本地改动patch、native二进制SHA/动态静态链接/编译flags/ABI/目标架构；client版本/源与编译feature；OS/build、CPU物理核/逻辑线程、RAM、背景负载与采样工具口径；主/子进程资源模型、所有写入口/系统dispatch/阻塞点；第3节源码与依赖/输出/端口/动作精确表。参考主机至少4物理核、16GiB RAM、SSD，仅报告本次一个明确OS/架构结果，不外推三平台。

G0建议固定classic S7 PDU上限480B、单frame上限512B、单item应用payload≤256B、每PDU≤4items且实际请求/响应均可装入协商PDU；COTP分片累计重组也限480B且绝对期限不重置。协商AMQ、最大错误响应、描述符/stage/copy及系统socket buffer实额须从冻结实现计算，列完整最坏输入+输出预留公式。数值只是这个G0有限profile，不缩改004产品容量合同；不能静默降PDU/请求或用不可控库内队列冒充有界。无法控制/观察者在对应gate blocked或判候选不满足，先回PM决定。

### R3. 先证明可拒写再选语言与库

按第2节逐候选给证据支持的adopt/reject/blocked及原因，核回调时机、错误传播、线程/ABI/指针生命周期及未列操作。写前入口必须能阻止image更新并让客户端收到真实S7 item失败；无入口即淘汰，不得降为写后报警/回滚、tick修复或仅UI禁用。本r2只提出§2.4的有限原生扩展及C++服务端harness，尚待Owner批准；不采用Rust高层server或Python sidecar。B0未证ABI与有限扩展可行性前不进行协议运行。

### R4. 单owner、提交事件与拒写证明

每实例唯一image owner，所有读复制、来源准入、coverage/type/CAS复核和单item提交可追踪。非法写的静默测试先暂停规则并封其他合法写/排空在途，在同一epoch、同一已确认布局下保存**全部可能触达DB的完整bytes/hash、全image hash、instance seq、点版本/来源/更新时间**；失败后逐字节相同，客户端有真实失败。未知DB/越界/未列系统操作还核所有已分配DB，不能只看第一个点。

仅最终读回相同不足以证明写前拒绝：同时给冻结源码调用链与`request_received -> admission/type/owner_decision -> rejected(no commit) -> item_response`事件顺序；合法路径为`accepted -> commit_begin -> committed(seq) -> response`。在实际mutation入口计数/记录写前写后，证明拒绝item无任何commit/裸buffer写，再无“恢复旧值”动作。并发测试另按item/result ID、触达点版本与获准写范围对账，允许其他合法提交改变实例seq/hash，不能要求规则运行时全image绝对不变。观测本身不能改内存。

### R5. 原始bit/byte、typed包及item结果

覆盖BOOL邻位与整byte、全触达跨权限、部分标量、边界/长度/transport-size/count、有限REAL、大端整数、STRING完整包/长度头/ASCII与多item部分成功。每write item原子，失败全item不变；读item来自单epoch/seq复制，多item按内部顺序逐项并允许连接/规则交错。不同PDU/DB/实例无全局原子承诺。未列非DB区/CPU控制/clock/块操作/任意SZL不可绕过入口或映射为DS控制；必要最小握手元数据按P0白名单逐项列出，不接受库默认“成功但无作用”当拒绝。

### R6. 六种写来源收口与权限/CAS

client、rule、普通UI、一次性ui_maintenance、initialize、reset均从harness进入同一owner或同锁封闭maintenance模式。普通UI仅ui-owner；一次性维护只对显式允许的client/none hold，默认关，不改变持续owner，后续合法client可覆盖；rule暂停仍不让权。UI/维护带expected loaded revision/epoch/point last_seq，在提交边界CAS，冲突不写/不自动重试。init/reset仅封闭gate/stopped，非法运行中调用拒绝；reset为新epoch/初始化，stop-start保值。这里只验证入口合同，不新增持久apply/保留算法或租约。

### R7. 16会话与C/H/TCP/closing计数

一个PLC=一个server实例，C为**已建立S7 sessions**，非进程/IP/TCP accept数量。沿用默认C16、整数1–64（>16未验证）、H4整数1–16、accepted TCP=C+H默认20；closing直到socket/callback/worker真释放仍占先前C或H和TCP。全局C/H/TCP128/32/160、全树≤64线程/≤1024句柄均为硬预算，启用实例配置和不得超预算，0/负/小数/无限拒绝，修改只stopped显式载入；G0仅运行单实例16及两实例各少量兼容连接，不跑2×16/8×16。配置域边界/全局加总可由无端口的harness校验，不冒充64/128会话容量。

满额拒后来者、不抢占老连接、不重置hold、不提前虚减closing，不在同socket阶段转换重复计数。库MaxClients参数不能替代真实C/H/TCP各阶段准入及计数，短命超额accept句柄也须列入实际OS资源，不隐去。连接快照须有instance/connection ID、peer、阶段、建立与最近收发完成时间、执行/等待/bytes、拒绝/超时/关闭原因；无需产品面板，但独立QA能核逐连接事实。全局上限不代表与线程/CPU预算能同时打满；每连接一线程候选不得由本次16会话外推128或静默提高64线程预算。

### R8. 期限与有限队列/输入输出预算

沿用握手5s（accept起算）、半frame2s（首byte起算）、待提交2s（完整PDU准入/等待起算且commit复核）、send2s（响应开始发送起算）；滴流不续期，正常idle踢出默认关闭。每连接≤1执行+2等待PDU及64KiB全部协议bytes；实例等待≤64PDU/1024items及1MiB；全局等待≤256PDU及4MiB；UI等待4、普通控制8、每规则待tick1。bytes包含未完frame、执行/等待、描述符、stage/copy及最坏响应预留，转阶段不重计、复制新增计、closing仍计。

整个PDU输入/输出先原子预留，再执行第一item；预算不足真实失败或关闭该连接，无item已提交。单个写callback不能替代整PDU入队/最坏响应预留或逐item结果/内部顺序；P0若无法观察控制这些阶段，须判不满足或回PM改方案，不默许重写协议栈。PDU/item超协商/超限、send阻塞、未完握手和半报文均有明确结果。G0对未能由16会话/480B profile触达的实例/全局大上限，以**标明test-only的更小预算或确定的reservation故障注入**验证相同准入控制点及归还，不声称填满4MiB/1024items；正常profile硬上限不提高。协商AMQ较小时如实列实际可达状态，不伪称已实测1+2并行。网络收发/解析/编码、磁盘及证据写入均在owner临界区外。

### R9. 公平、规则合并与控制可达

沿用协议→规则→UI非空类轮转，协议内连接round-robin每次最多1item，同PDU保序；规则按point轮转且每规则最多1待tick、合并计missed/coalesced。用F洪峰、A/B低频、8规则及UI维护同时存在的60s场景验证。已经准入且持续可调度的F/A/B三连接，每次protocol类轮转至多3次dispatch让各方一次；三个工作类持续非空时每3次工作类dispatch各获一次。保存调度轨迹/资格时刻，不能把库锁外看不见的等待从统计中删掉。

正常低频请求p99≤250ms，无连续1s完全不服务的已准入A/B；规则与1Hz UI请求可达。过载可真实拒绝，但已预留工作/stop不能饿死；恢复基准5s内等待队列回零或稳定基准，无无界补跑。stop走及时通道，先关准入/accept，取消未进不可取消段者，当前已进段单item完成一次；不得等完整PDU或长积压提交完才处理stop。

### R10. 真实DAA自定义端口兼容

未来必证使用固定版本DAA **真实ManagedS7::connect/read/read_bounded/disconnect**，`rust-snap7-driver`开启、`local-validation`关闭，不以Python参考client、FixtureTransport或origin标签替代。推荐最小隔离harness消费**字节相同的ManagedS7及所需DAA domain依赖快照**，保留原RemotePort/rack/slot/超时调用；精确源清单/依赖/编译入口及feature见§2.5/§2.6及§3，r2批准后按B0核验。若私有API/feature/安全profile无法这样消费，结果blocked，回协调申请独立DAA范围，不能修改原DAA/改成重写近似client后声称兼容。

G0证明层级为真实DAA客户端模块对候选server的S7互操作，不覆盖完整DAA GUI/SQLite采集/历史/上传/native窗口。推荐harness不创建DAA业务库，不读任何env或默认profile，只从批准的owned内存Plc参数调用；若实际入口必须创建隔离DAA profile/数据库，其路径/动作须先另列获批执行面，禁止擅自走生产启动。明确禁上传、Backend/direct DB/授权服务/旧采集/auto-start；连接/读取仅两个owned endpoints。

### R11. 关闭、资源释放与未知回执

单连接close与全实例stop都先关相应准入，取消未进入不可取消段者，让已进段单item完成一次，然后join回调/worker、关socket/listener、停timer/清队列并幂等释放。正常单连接close/stop≤2s，故意积压/慢连接stop≤5s；超时保留closing/stopping/failed及实际名额，不假报stopped或释放仍被callback使用的buffer。未提交超时/取消=拒绝不变；已提交但回执丢失=结果未知，无回滚/自动重试/exactly-once。

记录全进程树CPU/RSS/线程/句柄及分项socket/listener/callback/timer/队列bytes/输出预留；client进程单列，不藏入或混同DS指标。检查同端口重绑、20次start-stop、16连接各10轮重连、重复关闭通知。若选sidecar，父进程正常退出/崩溃、子进程异常退出与A/B隔离必须实测，5s内无owned孤儿和占用端口；G0管理harness不等于Tauri原生退出。进程内native硬崩溃可能波及全进程须如实给隔离风险，不能靠逻辑instance ID宣称崩溃隔离。

### R12. 证据、统计与可复现交接

原始JSONL按run/candidate/build/instance/connection/request/item/result/epoch/seq及monotonic时刻关联；保存raw协议item结果/有界报文、完整合成fixture前后bytes/hash、决策/commit/response顺序、错误与预算变化、版本摘要、资源1Hz采样及状态转换采样、复现命令/退出码/环境。raw payload仅限本任务公开合成数据，不采集真实私有报文。报告offered/accepted/completed/rejected/timeout/unknown分母，逐连接p50/p95/p99/max和队列等待，不能删失败或用聚合平均掩盖饥饿。

证据文件是显式临时输出，不是产品日志/正式schema；证据丢失或关联不全不能判pass/go。沿用004纯日志故障降级原则：可选sink失败不把已提交成功改失败/回放；记录observability_degraded/丢弃，并将该段无法证明的case标blocked后另做新run，不把缺证据当内存已回滚。不要为G0增加强持久审计/SQLite journal。

### R13. 分阶段go/no-go及状态诚实

r2获批且B0通过后，按P1写前拒绝/全来源及item→P2连接/队列/公平/释放→P3真实DAA及最终全矩阵独立复现顺序推进；不能先建产品以待补保护。场景状态为pass/fail/blocked/not_run/deferred，以及严格条件项的not_applicable：pass有实际证据；fail为已运行不符；blocked为必要来源/环境/接口/证据不能取得；not_run为尚未执行或被早期淘汰阻断；deferred只限本spec明确排除的后续阶段；not_applicable仅用于未选sidecar时X02的父子进程专属分支，须给实际进程模型理由，不免除共通stop/资源释放及进程内native风险说明。必证项不能为凑go改deferred或not_applicable。

候选只有全部适用必证case通过、无未解除blocker、清理证据完整才可go；失败候选的后续case可not_run并给停止原因，不冒充通过。可信no_go是允许的研究结论，须指出不满足的实际控制点和复现证据；它阻止后续采纳该候选，不强迫实现完整协议栈。QA独立审核方法/复现和结论，原case fail不得被改pass；即使研究报告被Owner接受，也不代表候选能力通过。更换未列候选、放宽保护/16会话/预算/阈值、增源码/依赖/端口/DAA动作、扩OS/长负载均回PM新Revision和Owner批准。

### R14. 保留工作树与角色权威

本轮PM仅修订本spec；004十保护文档及旧证据保持。主协调只机械同步四根索引本任务既有行，保留DAA/CU等并发修改。后续Development只写获批执行面和tasks，精确handoff后新的fresh-context Verification只验证并写checklist，Owner保留最终接受与风险例外。当前profile为contract_only，串行角色/diff审计是合同控制，不宣称ACL、自动路由或团队激活。本draft文档自检不作G0、QA或Owner接受。

## 5. P1写入/协议场景矩阵

以下仅定义未来输入/动作/预期。**DEV逐行实现harness/自检与保存E证据；fresh QA从固定handoff自行执行并独立解码item/比较bytes，不调用DEV总结冒充复现**。每个确定性向量至少独立重置后重复3次；BOOL竞争另为100轮。失败静默测试按R4关其他写并排空；并发单列，不能混用不变口径。

冻结合成fixture定义（B0生成raw manifest，不建正式schema）：每实例测试DB41长1024B、DB57长64B，后者为实例身份只读marker；DB号/两个DB仅夹具，不是产品固定拓扑。DB41 byte0.bit0=client BOOL、bit1=rule fixed TRUE、其余reserved；byte1八个client BOOL；offset2 INT、4 REAL；64处STRING[8]全10B、128处STRING[254]全256B；512起16个8B client hold槽（每槽两DINT）。普通ui-owner DINT在48、显式维护client-hold DINT在56；规则为400起6个动态DINT及1个fixed DINT，加byte0.bit1共8规则。未列空位reserved/read-zero/write-denied；A/B初值marker不同、image独立。规则参数仅够触发入口，不实现通用引擎。

W02的未确认coverage负例固定为既有DB41 offset56的4B client-hold DINT：在同一已确认布局/epoch、规则和其他合法写均经屏障排空后，harness仅对该范围启用test-only admission overlay，使owner coverage复核返回unconfirmed，再由真实client写完整4B，必须在commit前失败。它不改变已加载布局/owner/bytes/seq，不承诺产品允许未确认布局启动。保存overlay开启/拒绝/关闭事件与完整不变证据后，先撤掉overlay再解除屏障；不靠reset或回写旧bytes“恢复”。overlay只限本W02负例，不出现在C/D正常profile或默认准入策略。

| Case / 需求 | 输入与动作 | 可判定预期与必须保存证据 |
| --- | --- | --- |
| W01 · R3/R4/R5 | 真实client向自己8B槽写两个完整DINT的非旧值，raw读回；再读64B marker。 | item成功、逐字节/typed值一致，唯一commit且seq+1；raw请求/回执/读回、owner trace及完整前后image。不能只看client函数无异常。 |
| W02 · R4/R5 | 静默屏障下依次向rule字段、reserved、越权bit、未确认coverage、未知DB写；未确认coverage固定采用本节DB41 offset56的test-only overlay及撤除边界。 | 每item真实失败；全部可能触达范围bytes/hash/点版本及全image/seq不变，拒绝前无commit/裸指针写，回调/dispatch顺序可复查。自动字段即使rules_paused仍拒绝。 |
| W03 · R5/R6 | byte0.bit0合法bit写；向同byte整byte写（含rule/reserved，即使相应值没变）；byte1两个不同client位由双连接同步竞争100轮；byte1合法整byte写。 | bit写只改mask、邻位保留；byte0整byte失败且不变；byte1两位更新均保留，无RMW丢失，合法整byte成功。保存各轮item/seq与目标byte前后，不拿不同并发顺序当失败。 |
| W04 · R4/R5/R8 | 部分INT/REAL、越过client槽末端触及reserved、末端1023+2、0长度、count溢出/transport单位不符/短payload、NaN/Inf REAL及超frame/PDU；合法大端有符号/有限REAL对照。 | 非法输入在提交前失败/无可编码item时关该连接；无越界/分配爆量/其他实例变化，合法typed值可读回。保存每向量原始长度/规范化触达、错误码、全范围bytes及预算变化；格式错误与权限item失败分开。 |
| W05 · R5 | STRING[8]写完整`08 03 41 42 43`加5零字节；STRING[254]完整256B对照；错误max头、actual>max、非ASCII、只写头/截断包/部分包。 | 合法包精确读回；其余整item失败、整个STRING包及全触达字段不变，不截断后报成功。保存原始包/布局、item返回、typed解码与hash。 |
| W06 · R4/R5/R9 | 单PDU顺序3items：合法8B、禁止rule写、合法STRING；其间允许另一已准入连接/规则插入，另做静默对照。 | 真实逐item成功/失败/成功、内部顺序保留，成功各提交一次，失败范围不变；无全PDU回滚/全成功伪造。保存原PDU/result数组与逐item调度/seq，混合结果按触达范围对账。 |
| W07 · R4/R6 | 六写来源各一合法及一非法/陈旧操作：rule对hold/paused/旧epoch，UI及维护CAS冲突，维护默认关和rule即使暂停，运行中init/reset；合法维护后client再次写。 | 全部进入同owner/maintenance模式；非法无commit，合法来源和seq正确。维护不改持续owner/初值、后续client可覆盖；reset仅stopped换epoch，stop-start保值。保存源入口调用图、每操作结果与revision/epoch/point seq，harness不等于UI。 |
| W08 · R3/R5 | 对owned server发非DB区、CPU start/stop、clock、块上传下载、非白名单SZL/未知功能各一请求。 | 明确协议拒绝或有界关闭，无image/DS状态/宿主时钟变化，不能以库默认成功空操作通过。记录dispatch白名单、原请求/结果/前后状态；若库自动处理无法阻止，候选no_go。 |
| W09 · R3/R4/R11 | 在precommit及不可取消提交段用确定harness屏障分别触发timeout/stop/close；另在commit后故意丢回执；复查callback指针引用/注销顺序。 | precommit取消不变；已入段item完成一次，后项取消，已提交丢ack为unknown且不自动重试；旧epoch不能触达新image。保存call/commit/return/close/join/释放时序、引用计数及wire可达结果；禁止释放仍使用buffer。注入屏障是实验工具，不可带入产品owner等待逻辑。 |

## 6. P2连接、队列、公平与资源短程profile

每个数值均为r1已批准且本r2不降低的G0目标，不是实测支持。每个最终候选DEV完整运行一轮，独立QA从新run/profile/端口依同一冻结输入重现一轮；静态早期淘汰者不强行跑后续。不得将这些短程结果替代004 L1–L5。

| Case / 需求 | 有界输入、次数/时长 | 判据及证据 |
| --- | --- | --- |
| C01 · R7/R8/R12 | 单实例16已建立S7 sessions；预热30s后300s。各连接1轮/s，每轮2请求、各1item：DB57读64B+自己DB41槽写8B；8规则=6动态+2fixed，100ms到期。 | 32请求/s=16读+16写，应用payload1152B/s；测量段共9600请求=4800读+4800写、345600B，不含协议头；每连接600请求。按offered全量核完成，非故意错误/错写/越权/BOOL丢更新=0；每连接p95≤100ms/p99≤250ms，排队p99≤100ms，规则missed≤1%（24000到期机会，动态/fixed分列，无变化fixed不虚增commit）。 |
| C02 · R7/R11 | C01的16会话仍读写时，第17个S7连接尝试20次，间隔100ms；再关闭一条并重连，重复close通知。 | 新来者被拒，不抢占/重置原16；关闭直到真释放才腾C/TCP，重连新ID。逐时C/H/TCP/closing/实际established及OS socket、原会话成功item、拒绝阶段/原因均对账，无负计数/重复归还。 |
| C03 · R7/R8 | 另有16已建立时保持4个未完成握手TCP，第5未完成握手尝试20次；随后半frame每500ms滴一byte；另一session idle30s后正常读。每种绝对期限试3次。 | C16/H4/TCP20不超，5th握手无额外持久对象；握手accept后≤5.5s、半frame首byte后≤2.5s完成关闭/清理（含≤0.5s观察裕量，不延长配置期限）。老会话继续；idle不误踢。保存时间起点、阶段、bytes/名额/句柄释放。 |
| C04 · R8/R9 | 单连接超协商in-flight及1执行/2等待边界；另用P0声明的小预算/确定reservation故障触发每连接、实例、全局输入+最大输出预留失败；恢复后重试。慢读peer的实际收/发socket buffer各≤16KiB，20次/s发256B读取且不消费响应，最多30s，须实际观察send阻塞。 | 超额完整PDU在第一item前失败/关该连接、无commit；所有阶段数量/bytes含预留不超实额，幂等归还。发生阻塞的该响应从首次发送尝试起≤2.5s关闭（2s配置期限加≤0.5s观察裕量，不从阻塞时重置），其他连接/规则/stop继续。若只触发队列拒绝而没观察send阻塞，该subcase仍not_run/blocked，不能算send期限pass；不能以注入替代所有真实socket证据。 |
| C05 · R9/R11/R12 | 同实例F/A/B3个活跃连接、其余13个idle：F20 PDU/s、每PDU4个64B read items，A/B各用C01每连接profile；8规则100ms、UI维护1次/s，持续60s。再用小预算制造积压并从及时通道stop，3次；恢复基准观察5s。 | F offered80items/s，A/B合4items/s，规则80次到期/s，UI1次/s；PDU数与item数分别计。正常60s段A/B各60轮=120请求全部按offered完成，60次合法UI维护均有成功结果，不得把低频工作拒于准入外绕过公平；F的完成/拒绝/超时单列。仅随后明确小预算故障积压段允许按真实结果计低频拒绝。按R9轮转/时限判，保存各连接/类资格、dispatch、等待/完成/拒绝、missed/coalesced和stop各阶段；F大PDU不独占、普通控制不饿死业务，过载stop≤5s，恢复队列回落。 |
| C06 · R7/R11 | 16条连接各10轮断开/重连，共160次；每轮含一次正常close、半关闭或异常之一，轮转+100–1000ms固定seed抖动；随后20次start-stop，每次建立16session并各读/写1次，stop后等10s采样。显式reset另3次。 | 正常close/stop≤2s、故意积压stop≤5s，所有owned listener/socket/callback/工作timer/队列PDU/item/bytes/输出预留回0；stopped保留image/值不算泄漏，reset独立初始化。停止后同owned端口可重新bind，无隐形worker/旧epoch写。保留完整cycle序列，不把10轮写成004 L4每连接100次。 |

C01及上述所有阶段分别保存全DS核心/管理器/sidecar进程树的平均CPU、RSS峰值/净增、线程/句柄及分类；**client/采样进程单列**。G0目标：平均CPU≤单逻辑核100%（CPU时间/墙钟，不除主机核数）、RSS≤512MiB、线程≤64、句柄≤1024；C01测量段RSS净增≤16MiB。这是短程可行性阈值，不声称004的60min增长或长稳定性已满足。

C06资源基线为依赖已加载、image已分配、证据sink/采样器已启动但无listener/连接的稳定stopped状态B0；首轮热身后固定B0。每次stopped10s时owned transport/callback/工作timer/queue/reserve=0，线程/句柄按分项回B0；明确保留的单一库全局设施须P0计入B0，不能逐cycle追加。RSS允许allocator保留但每次≤B0+16MiB，最后5次中位数相对最先5次≤8MiB；若出现连续4组（每5次一组）严格增长且总增>8MiB则失败。原始曲线与峰值均交付，这些口径不能证明永不泄漏。

两个实例仅为端口/故障隔离对照：A16会话场景时B至多1参考会话；真实DAA场景各1。该组合ΣC默认配置32、ΣH8、ΣTCP40，仍受128/32/160及64线程/1024句柄联合预算；不能用名额配置推断2×16吞吐。>16实际会话、8×16、全局极限、大布局以及完整L1/L2的5min预热+60min和L4/L5长故障均明确deferred到D4或另批扩展任务，不在G0凑齐。

## 7. P3真实DAA与退出边界矩阵

责任同第5节：DEV提供精确非fixture入口与原证据，fresh QA独立运行、核source/feature、协议和OS状态。r2执行面未批准及B0未闭合前以下均不执行。

| Case / 需求 | 输入与动作 | 预期与证据 |
| --- | --- | --- |
| D01 · R2/R10 | 两个owned非102端口、A/B各自固定called TSAP/rack/slot和不同DB marker；字节冻结的真实ManagedS7各持1会话，60s、每连接1轮/s，每轮读取两个DB各1次；参考client改变允许hold值后再DAA读取。 | 两模块累计240次真实db_read，连接复用，能按marker/bytes/变化值区分实例，RemotePort实值与COTP/S7协商、调用trace相符。提交源/feature/native摘要、raw字节/DAA结果及server connection ID；fixture/标签/截图不能替代。只证明模块级S7，不证明完整DAA采集或GUI。 |
| D02 · R7/R10 | 错rack/slot产生错误called TSAP、owned无listener端口、A参数误指B端口；每负例3次；另用owned冲突listener阻止A启动，重复start。 | 错TSAP明确失败，不能同端口隐式复用/接受任意身份；错端口不回退102/扫描其他地址；冲突只使后来A failed、占用者和B继续、无第二listener。每次记录真实COTP、RemotePort、失败阶段/错误与名额释放；若候选默认接受错TSAP，必须先取得可控adapter证据或判不满足。 |
| X01 · R4/R11 | A/B均在服务时只关闭A一条连接；另在W09屏障处stop A，B持续读；超时注入后再观察实际清理及同端口重绑。 | 关闭只影响指定对象；未提交取消/已入段完成/已提交丢ack未知分开，B不变。正常2s/故障5s，超时不报stopped；只有callback/socket/worker真实归零后才释放/重绑。保存进程/OS/库计数和owner事件关联。 |
| X02 · R2/R11 | 若选择sidecar/每实例进程：父管理harness正常退出、父异常终止、A子进程异常退出，各3次；同时观察B，随后新run重开。 | 正常有序stop；异常时≤5s无owned孤儿/残留listener，A子崩不误报clean且B继续；重开只初始化fixture、停机，不恢复旧连接/未知写。完整进程树/PID起止/退出码/socket证据。未选sidecar则明确not_applicable理由，不宣称该能力；进程内native硬崩风险单列，完整Tauri退出与三平台发布仍deferred。 |

资源/异常测试只操作获批本任务owned进程和loopback socket；不停止DAA原生会话、不修改其profile、不向任何真实设备或生产DB/API发动作。若不能在准确进程树中区分归属，先blocked，不批量kill或清理未知资源。

## 8. AC与可审阅覆盖

下表是未来**研究交付及选型判断**的验收口径，非本轮结果。每一行均须有DEV原始证据和fresh QA独立观察；候选go必须满足对应功能预期。充分证明的no_go可以交Owner作为研究结论，但失败case原样保留，不能写成“所有功能通过”；必要项无证据仍为blocked/not_run。

| AC | 对应需求/场景 | 可核验标准 |
| --- | --- | --- |
| AC1 | R1/R14、§1/§3 | 独立namespace/Task ID/Capability/接受链、draft及五路径准确；004文档接受不移作G0批准；当前只spec，无空tasks/checklist/工程/执行。 |
| AC2 | R2/R3、P0 | §2/§3的精确source/package/hash、工具链、依赖、入口、端口与动作取得r2批准后才创建/构建；B0记录生成binary SHA、实际链接/ABI、完整预算公式后才进行协议运行。未齐或漂移则blocked，不编造当前binary hash、不自动更新依赖。 |
| AC3 | R3/R13、§2 | 候选比较与推荐顺序有primary/冻结源码依据；明确Rust wrapper/Python stub、系统dispatch及资源控制不足，给可复现adopt/reject/blocked及最终go/no_go；不自写完整协议栈或放宽保护。 |
| AC4 | R4/R5、W01 | 合法真实写成功、唯一commit/seq及原始bytes/typed读回一致；独立QA可从raw item和image核实。 |
| AC5 | R3/R4、W02/W09 | 静默/屏障下全触达bytes/hash/seq/版本/时间不变，真实失败且调用/提交顺序证明无先写后恢复；并发另按合法item范围和点版本对账，不要求全局hash冻结。 |
| AC6 | R4/R6、W07 | 六来源全部收口，普通UI/一次性维护范围及CAS、rule暂停不让权、init/reset停机权限/旧epoch均实证；harness与产品UI/持久功能边界准确。 |
| AC7 | R5、W03 | 合法bit邻位保留、100轮同byte两bit无丢失、合法全byte与含禁bit整byte拒绝均可重现。 |
| AC8 | R5/R8、W04 | 部分标量、跨权限/边界/长度/transport/count/载荷与REAL负例逐项真实失败，不越界/无隐藏分配；合法大端/有限REAL对照可读回。 |
| AC9 | R5、W05 | STRING[8]/[254]全包成功及头/长度/ASCII/截断负例不变，raw包、item结果及完整包hash齐全。 |
| AC10 | R3/R5、W06/W08 | 多item部分成功/保序、失败范围不变且非PDU全原子；非白名单系统操作明确拒绝/关闭、无DS/宿主副作用，不接受“成功空操作”替代。 |
| AC11 | R7、C01/C02 | 16真实S7会话同时读写、第17条20次拒绝不抢占；计数从TCP/H到C/closing/释放逐态对账；1–64/>16未测及全局128/32/160与64线程关系准确。 |
| AC12 | R7/R8、C03/C04 | H满/握手、绝对半报文、正常idle、真实慢接收send及释放期限均有起算和原证据；未实际触发send不报通过。 |
| AC13 | R8、C04 | per-connection/instance/global数量和所有阶段bytes/最坏输出预留先准入，超限无item执行且归还一次；小预算/故障注入与实际大上限未触达准确分层，owner无网络/磁盘等待。 |
| AC14 | R9、C05 | 连接与工作类按item轮转/保序、规则合并、A/B低频及UI/普通控制/stop可达；正常60s内A/B各120请求全完成、60次合法UI全成功，不能靠准入外全拒绕过公平。有资格和调度轨迹、逐连接分位数/拒绝分母及恢复回落，不能仅总吞吐。 |
| AC15 | R2/R10、D01 | 精确DAA ManagedS7真实feature、RemotePort/rack/slot/COTP/读链与240次db_read可定位；不改DAA、不读真实env/profile、上传关闭；模块级与完整产品界限清楚。 |
| AC16 | R7/R10、D02 | 错TSAP/端口、双端口身份隔离/端口冲突/重复start负例均可复现，不回退102/抢占/隐式复用；私有API/feature不满足时blocked而非换fixture。 |
| AC17 | R4/R9/R11、W09/X01 | stop/单close先封准入取消未入段，仅当前不可取消item完成；未知回执与确定拒绝分开，无回滚/自动重试，超时不假stopped，其他连接/实例继续。 |
| AC18 | R7/R11/R12、C06 | 160重连、20启停、3reset有原始序列；socket/callback/worker/timer/队列/预留回B0且可同端口重绑，重复释放幂等，RSS/线程/句柄按定义无超额增长，保值/初始化语义不混同。 |
| AC19 | R2/R11、X02 | 若选sidecar则父子正常/异常退出与A/B崩溃隔离3轮证据满足5s边界；不选时理由与进程内native风险可审阅，不把G0管理harness当Tauri原生/三平台证明。 |
| AC20 | R2/R12、全矩阵 | 每run source/ABI/环境、raw item/bytes/事件/错误、1Hz资源和状态转换可关联，offered全分母、逐连接p50/p95/p99/max、CPU/RSS/线程句柄/队列/规则missed/stop均报告；C01/C05算术正确，证据缺口不算pass。 |
| AC21 | R1/R13/R14、§9/§10 | go/no_go与case/QA/Owner层次分开，fail/blocked/not_run/deferred真实；候选失败或改范围回PM，不把004/G0/文档检查当产品批准；既有文档/并行dirty/旧receipts保护，DEV与新fresh QA逐角色真实建立。 |

## 9. 风险、回退与明确排除

| 风险/未决gate | 处置与Owner需审阅的取舍 |
| --- | --- |
| native回调、ABI或默认系统命令不满足 | §2已完成只读筛选；有限扩展先经B0审查/ABI，未闭合不开始协议。返回值/内存入口/拒绝不可控即淘汰，不以回写或成功空操作豁免。 |
| native hook锁/线程/缓冲隐藏，16能连但不公平/不能退出 | C/H/queue/资源可控点是必证；任何不能有界释放/观测的关键面阻止go。通过16也不证明>16或L1–L5。 |
| DAA真实入口与fixture隔离机制不兼容 | 推荐固定真实模块的隔离消费，不改当前DAA；无法安全调用则blocked并申请独立DAA范围。不能利用默认env/生产profile或同名重写client消除blocker。 |
| 原生库/sidecar崩溃影响其他实例 | 先明确实际进程边界；选sidecar须X02，进程内硬崩风险保留并由Owner决定后续隔离。不能用逻辑隔离作OS崩溃隔离。 |
| 静默拒写试验被规则/合法并发污染，或先写后恢复伪通过 | 屏障、不变基线、mutation入口事件及源码链同时使用；并发按item/范围对账，证据无顺序或丢失则blocked重做新run。 |
| 单OS/短程和缓存包被当跨平台/长期能力 | 本轮包/源码已按§2只读校验，构建/ABI实测仍not_run。G0只报告冻结OS与有限profile，目标平台/发布及长负载另批。 |
| 选型趋向大规模协议重写/依赖升级/产品实现 | 当前draft不实施；未来超小adapter/两候选/指定矩阵的工作回PM新Revision，不继续扩写。no_go可以是可信交付。 |

回退只处理本任务明确delta或未来获批owned实验资源；本轮仅spec可逆修订，不reset/覆盖已有工作树。未来实验失败先封准入、按真实提交边界退出、保留错误与原证据；只清理已确认归属且不再承担证据/后续依赖的资源，由主协调收尾，QA不回收。端口冲突不碰占用者；旧004/DAA证据不得删除或改写。

排除完整DS工程/Tauri壳/CU页面/安装包、导入器/点位编辑/配置SQLite/schema/迁移/持久apply/运行值保留九场景、完整DAA采集/历史/上传及DAA修改、Backend/SMA/CA/真实PLC/现场网络、生产数据库/API/上传、Modbus/完整PLC执行或协议栈、长期服务/后台守护、完整L1–L5/8×16扩展、三平台native/发布部署、Git refs/提交/推送、外部消息。G0可用合成内存fixture证明init/reset/stop保值路径；不能把它扩成配置恢复实施。

## 10. 角色交接、批准历史与未决gate

实际PM按aiis/project-governance整理本r2；未来Rust ManagedS7/client/FFI与资源证据由Development消费`rust-runtime`，PLC地址/BOOL/STRING/coverage由`plc-point-mapping`；若将临时harness另立tools工程须新范围并用`project-tooling`。当前不触达Tauri壳，`desktop-tauri`仅在独立获批桌面/native集成时加载；没有UI/i18n、DB/backend/Celery范围。C++仍遵aiis跨端/资源与日志边界，不因Rust skill更换已说明的语言或代实现。profile为contract_only；串行角色、精确handoff与diff审计是合同控制，不宣称平台ACL。

| 日期/阶段 | 精确事实与下一gate |
| --- | --- |
| 2026-10-18 r1 draft | Owner只要求整理G0范围；PM形成283行r1。原gate、自检及完整原文在附录A，作为当时记录。 |
| 2026-10-19 r1 owner_approved | Owner按§1原话明确批准SHA `00171a46325c1b28359e77b3d2a42434e1ad43ac825b16cdb84f1708695c4c84`的r1，并授权P0只读与r2修订；不是r2原型许可。 |
| 2026-10-19 r2 draft / P0 read-only | PM核官方包、C ABI/分发/控制缺口、DAA原模块闭包、依赖、宿主与端口快照，形成§2/§3精确提案；未构建/加载/运行；没有DEV或QA verdict。 |

**P0已知决策**：原样native1.4.2不满足、Python3.2.1备选no_go；推荐仅审阅native1.4.2的有限扩展试验，不代表已采纳。来源/源码/工具链/精确动作在本r2冻结，独立registry元数据403、SSD/内核动态段未核已注明；ABI实测/arm64可构建性、有限patch是否足够、全PDU/连接/stop可控性及全部运行证据仍not_run。若B0发现必须改协议主循环/线程框架或越表，可信no_go并回PM；本r2不承诺必定得到合格server。

1. 当前PM正式handoff本r2及receipt到唯一协调，由协调向Human Owner审阅**精确r2执行范围/风险**；PM停写，不启动其他角色。
2. Owner明确批准本r2后，实际Development才建tasks并先执行B0；来源/工具链/依赖漂移或有限扩展越界先停止，不能在未闭合B0时bind/联调。
3. B0后按P1→P2→P3推进，保存早期失败、全部未运行项和限制；完成精确developer_handoff后，实际新fresh-context Verification（fork_turns=none）新建checklist，独立复现/解码/核字节与资源，不复用DEV结论当证据。
4. QA可独立确认研究交付方法/可复现no_go，不能把fail改pass；Owner最终接受G0研究结论，不自动授权004产品实施、长负载、发布/设备或DAA改动。

Human Owner scope approval of exact ARCH-AW-005 r1: **approved, 2026-10-19**（§1原话与指纹）。

Human Owner approval of exact ARCH-AW-005 r2 execution surface / finite native changes / risks: **pending**。

B0 source-to-binary / ABI / finite-change gate: **not_run; execution approval pending**。

P1/P2/P3 19 cases / Development handoff / independent Verification: **not_run / not_started**。

Human Owner final acceptance of ARCH-AW-005: **pending**。

## 11. 本轮PM文档自检与交付限制

已消费根/最近AGENTS、README/PLAN双语、docs/plans索引、canonical workflow、实际pm TOML、完整r1与004 bundle和DS设计；仅以PM修订所属spec。起点`/private/tmp/arch-aw-005-r2-p0-_ap0y325/baseline-manifest.json`/before及`pm/role-start.json`；DAA取一次source-snapshot，不持续追逐并发状态。tmp附件补充来源/检查，正式事实和可执行范围已写本spec。

本轮真实动作仅OS/工具链/端口占用的只读查询、读取仓内及cache源码、官方下载原始source为数据并提取/哈希、stdlib文档/算术/范围检查。sandbox默认curl DNS失败exit6后，获准只读下载官方原文成功；crates.io独立metadata返回403/exit56，不掩盖该限制。`/usr/bin/python3`3.9.6不含tomllib，首次静态lock闭包脚本exit1；改用Codex bundled Python标准库tomllib后exit0，未安装包、修改项目依赖或执行Cargo/build.rs。按冻结锁得66包，cache全部hash相符；未因此称能编译。

必要文档自检命令`/usr/bin/python3 /private/tmp/arch-aw-005-r2-p0-_ap0y325/pm/check-spec.py`为exit0：active R1–R14、AC1–AC21全覆盖，19个case及对应AC完整；24个本地链接（含历史，10个带锚点）、active 14张表、2个历史围栏marker及全文件尾空白通过；C01/C05/C06/D01、名额/fixture及2208B预留算术一致。附录可恢复283行/50843B原r1且SHA与获批输入一致；10保护文档与本轮起点逐字相同，tasks/checklist及未来原型root仍不存在。`git diff --check -- plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md`为exit0；`git diff --no-index --check /dev/null plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md`为exit1且stdout/stderr空，表示untracked文件有差异而无空白诊断。全仓起点delta按PM单spec、共享四索引变化、foreign并行变化分别记录；不将后两类归PM、不回退。最终SHA、命令退出码、保护摘要和delta见本轮`pm/document-self-check.json`与`pm/receipt.json`，均为PM文档自检，不是运行/独立QA。

本轮未创建工程/实现/测试/依赖/lock/profile/tasks/checklist；未安装/构建/加载native、跑任何项目/原型/ABI/协议/负载、bind/connect、访问DB/API/真实设备。没有本轮新增运行进程/listener/session/tab/worktree或需退出的服务。只写本spec及本轮owned tmp文档研究附件；10保护文档及旧证据/receipts字节保持。主协调仅在正式handoff后机械同步四根索引本task行并保留其余变化；PM不认领共享文件或DAA等foreign delta。

## 附录A. r1完整原文与恢复规则

以下text围栏内283行是r1 SHA `00171a46325c1b28359e77b3d2a42434e1ad43ac825b16cdb84f1708695c4c84`的原字节快照，UTF-8/LF且含末尾换行，50843B。直接提取围栏内字节即可恢复；旧Status=draft、待批准、DAA读时状态、未冻结及自检均是当时事实。2026-10-19批准记录和当前r2 gate见正文，不以历史覆盖当前权限；附录不是第二active spec或新bundle。

<!-- BEGIN R1 EXACT SNAPSHOT -->
````text
Task ID: ARCH-AW-005
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM draft to Human Owner for exact r1 scope review; prototype execution remains blocked until explicit approval and a separately approved exact P0 execution surface; no Development or Verification activated
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS G0 服务端可行性、写前拒写、16会话、真实DAA端口兼容及资源释放的有界技术原型验证
Owner: Automation World
Acceptance Chain Reference: aiis-ics-arch::ARCH-AW-005 r1 draft -> Human Owner exact scope approval -> P0 execution-surface freeze and approval -> Development prototype handoff -> new fresh-context Verification -> Human Owner final acceptance
Depends On: aiis-ics-arch::ARCH-AW-004 r2 accepted detailed-design baseline
Related Task: aiis-ics-arch::ARCH-AW-002; aiis-ics-arch::ARCH-AW-003; aiis-ics-arch::DAA-002

# DS G0 技术原型验证规格 r1

## 1. 目标、身份与当前 gate

本任务为独立的 `aiis-ics-arch::ARCH-AW-005`，不是 ARCH-AW-004 的新Revision或继承子任务。Capability从“详细设计文档”变为“有界技术原型验证”，接受链独立，故Classification为root、无Parent Task ID；Related/Depends On只提供依据，不转移批准、QA、验收或写权限。

2026-10-18（Asia/Shanghai），Human Owner在唯一主协调会话`01a14e52-eeb4-7c82-bade-bc0a237fa2ff`直接要求：

> 接下来先整理 DS 的 G0 技术原型验证 spec，明确服务端选型、写前拒写、16 条连接、DAA 自定义端口兼容和资源释放的验证范围与验收口径，先不改代码。

此句授权PM形成可审阅草案，**不是对尚未形成的精确r1范围、数值、风险或原型执行面的批准**。当前只创建本spec；不创建tasks/checklist空壳、不启动后续角色。本spec定义将来必须取得的证据，所有运行场景当前均`not_run`，数值为待审阅的G0目标。

交付目标是一个可信的服务端选型 **go / no_go**：能否在既有单owner/单item合同下，真实拒绝非法写、承载单实例16个S7会话、让真实DAA模块读非102端口并有界退出。应先做最小阻断验证，失败停止该候选；不为得到go扩写完整PLC协议栈。go只为后续实施提供选型依据，不授权D1–D4产品开发、发布或真实设备动作。

本r1尚不能作为可开工的原型实施spec：精确源码文件、依赖来源/版本与ABI、执行入口、DAA消费方式及私有输出/端口尚须P0定版。r1范围审阅通过后，可先在另行授权的只读准备中补齐P0清单；**新增源码/依赖/运行面必须由PM写入同任务新Revision并取得Human Owner明确批准，再由Development创建tasks并执行**。不能用未来tasks自行扩大本节及第3节的五路径。

## 2. 基准、一次读时事实与候选顺序

### 2.1 既有设计和本次来源快照

[ARCH-AW-004 r2 spec](../ARCH-AW-004-ds-detailed-design/spec.md)、[Development](../ARCH-AW-004-ds-detailed-design/tasks.md)及[Owner接受记录](../ARCH-AW-004-ds-detailed-design/checklist.md#owner-acceptance-r2)已完整阅读。接受正文[DS详细设计](../../docs/AIIS_DS_Detailed_Design.md)为497行，SHA-256 `0eb3c149bf7093bbdce2f0b7a07af71e769fe24cb04a542c7f4dc43e6979eecb`。本任务只引用、不重开或修改004及AW/DAA/SMA正文；004的文档QA与终验不是本G0运行证据。

| 已验收设计定位 | G0直接继承的行为约束与验证边界 |
| --- | --- |
| [§5.2/§5.4](../../docs/AIIS_DS_Detailed_Design.md#lifecycle) | C/H/TCP/closing及期限、stop取消与不可取消单item、真实释放后才stopped。 |
| [§7/§8](../../docs/AIIS_DS_Detailed_Design.md#protocol-memory) | 全触达bit准入、typed stage、单item原子、多item部分成功、普通UI/一次性维护/init/reset收口；网络/磁盘不在owner等待。 |
| [§10](../../docs/AIIS_DS_Detailed_Design.md#selection) | 先证写前拒写再选语言/库；未列系统操作不绕入口，不能用事后回写替代。 |
| [§11](../../docs/AIIS_DS_Detailed_Design.md#verification-stages) | G0只解除选型可行性gate；L1/L2及L4/L5长负载属后续D4，L3需另批扩展profile。 |

本轮DAA来源快照固定为 **2026-10-18 21:18:33 +08:00**，之后不追逐并发进展。该快照的DAA owning PLAN/checklist为`qa_failed`，tasks为`implementation_in_progress`：QA2已闭F-001/F-002，F-003维护失败持久日志返工尚在继续，Owner终验待续。这里只记录当时状态，不宣称当前或未来DAA已通过；G0执行前重新冻结具体输入。来源摘要及副本保存在本轮私有`pm/source-snapshot.json`和`pm/read-snapshot/`，关键事实如下。

| 真实路径/符号（DAA前缀为automation-world/data-acquisition-agent/） | 已读事实、限制及后续用途 |
| --- | --- |
| [src-tauri/src/infrastructure/managed_s7.rs](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/managed_s7.rs)：ManagedS7::connect/read/read_bounded/disconnect/Drop | connect先set_param(RemotePort、PingTimeout、SendTimeout、RecvTimeout)，再connect_to(host,rack,slot)，read调用db_read；本模块SHA `4ce9a9bfbe81c63453a6444d9b8e719fce6afa8e72ea84e0ca561dda8b48ca0e`。只有`rust-snap7-driver`且未启`local-validation`才走真实S7，其余分支driver_unavailable；现有owned tests只是源码，本轮未运行。 |
| [services/local_supervisor.rs](../../automation-world/data-acquisition-agent/src-tauri/src/services/local_supervisor.rs)：LocalEngine::transport；[config/local_bootstrap.rs](../../automation-world/data-acquisition-agent/src-tauri/src/config/local_bootstrap.rs) | 非fixture工厂选ManagedS7；local-validation为debug fixture专用，不是安全的真实S7联调入口。默认本地模式、独立profile、读取门禁和legacy冲突检查均须按冻结版本保留；G0不能改factory绕门禁。 |
| [Cargo.toml](../../automation-world/data-acquisition-agent/src-tauri/Cargo.toml)及[Cargo.lock](../../automation-world/data-acquisition-agent/src-tauri/Cargo.lock) | 声明可选rust-snap7 1.142.2，lock记录该版本和package checksum `8c4d43b3a99825abd300d57a0888eda7b625b7cdbf56ee7766bd02331ac58243`；这是声明，不是本轮已校验安装包/二进制或ABI。 |
| 当前缓存rust-snap7-1.142.2的src/client.rs与native/s7_micro_client.cpp | connect_to进入Cli_ConnectTo/ConnectTo；缓存代码按connection type、rack、slot组合remote TSAP，默认PG。当前DAA未显式提供任意TSAP setter；P0须冻结实际COTP calling/called TSAP并由wire证据核对，不能把rack/slot当真实CPU身份。 |
| 当前缓存src/server.rs::set_rw_area_callback/call_rw_area_closure、src/ffi.rs::pfn_RWAreaCallBack与native/s7_server.h/.cpp | 本地高层回调及FFI未声明int返回；native头声明int，并由DoWriteArea据返回值决定成功/失败。这是源码/ABI风险，不能把该Rust高层server直接当可拒写候选。缓存来源完整性尚未独立校验，P0必须从可信来源验证；本轮不导入、构建、运行或修复DAA依赖。 |
| [仓内runtime.py](../../tools/plc/s7-virtual-plc/src-python/core/runtime.py)、[strict_server.py](../../tools/plc/s7-virtual-plc/src-python/core/strict_server.py)、[tools/pyproject.toml](../../tools/pyproject.toml) | refresh_areas逐tick写值；strict只校called TSAP后复用_process_request；依赖区间python-snap7>=3.0,<4不是DS锁版。该工具仅参考，不能作写前拒写、写入保持或16会话证明。 |

### 2.2 primary资料与推荐评估顺序

2026-10-18只读读取官方[native resourceless说明](https://snap7.sourceforge.net/res_servers.html)、[Server规格](https://snap7.sourceforge.net/snap7_server.html)和[API reference](https://snap7.sourceforge.net/snap7_api_ref.html)：native有按请求回调方向，但系统请求仍可能由库处理，且文档描述每接入连接创建worker线程。仅有callback名或max-clients参数不能证明本合同。版本化[python-snap7 3.2.1 Server API](https://python-snap7.readthedocs.io/en/3.2.1/API/server.html#snap7.server.Server.set_rw_area_callback)将同名回调标为兼容stub。上述仅为筛选证据，均无本任务运行验证。

| 候选方向/顺序 | 推荐评估及通过前提 | 立即淘汰/返回条件 |
| --- | --- | --- |
| 1. native Snap7真实C ABI + 最小受控adapter/harness | 先静态核写前回调、int错误传播、buffer所有权、所有操作dispatch、连接/线程/队列及退出控制点；再做P1。C/C++最小harness或正确ABI绑定均可，之后才选Rust核心/进程边界。 | 高层wrapper丢失拒绝返回、全局hook锁使连接公平不可控、系统命令不可拒或隐藏资源不可限时，不能直接采用。只有能在精确获批小adapter内解决才继续，不能假定upstream/native天然合格。 |
| 2. Python受控server/sidecar | 只有冻结源码证明在request提交前接管全部写及item失败编码，才进入P1；可借strict TSAP流程，不能继承其_process_request写入。sidecar须满足父子进程关闭证据。 | 3.2.1兼容stub本身不合格；不能用规则回写、monkey-patch未固定版本或注册裸共享区绕过。需大幅重写协议时停止，回PM。 |
| 3. 其他可维护S7服务端 | 当前未确认具体可用库；仅作为前两方向不满足后的只读候选调查，须同样冻结源码/版本、许可、ABI和控制点。 | 不把未确认库写成已支持，不以Tauri锁Rust，不在本范围偷偷自研完整S7/PLC协议栈。 |

建议先静态淘汰明显不满足者，**至多两套合格候选进入运行原型**；最终推荐候选必须取得全部适用必证场景。native二进制分发/许可证材料只做可行性清单，不在本任务发布或给法律结论；无法取得来源/许可/目标OS可用材料则blocked，不升级DAA依赖补救。

## 3. 当前精确allowlist与未来执行冻结

当前仅以下**五个仓库文件**，PM只写第一项；主协调在正式PM交接后只新增/机械同步004以外的本任务唯一行。共享文件已有DAA等并行delta须保留，路径入表不等于认领整文件。

| 精确路径 | 当前归属、时点与允许内容 |
| --- | --- |
| `plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md` | PM / Human Owner；本次唯一PM仓库写入，r1 draft范围、验收、风险、真实批准历史。 |
| `PLAN.md` | 主协调；PM交接后新增ARCH-AW-005唯一行，draft/下一批准gate，不改其他行。 |
| `PLAN.zh-CN.md` | 主协调；同一行中文对应。 |
| `plans/README.md` | 主协调；新增本任务目录行，只链接已存在spec，DEV/QA写待后续gate。 |
| `plans/README.zh-CN.md` | 主协调；同一目录行中文对应。 |

**当前不允许创建或写入**任务tasks/checklist、任何原型源码/测试、DS工程、依赖/锁文件、构建配置、schema/SQLite/env/profile或运行输出；不安装/构建/监听/连接/跑协议或负载。PM必要Markdown/哈希/算术检查只用stdlib，在`/private/tmp/arch-aw-005-r1-spec-oono_1zh/pm/`保存辅助证据，不使用项目依赖。本任务不能清理004三个旧证据目录、旧receipts、DAA或未知资源。

P0尚需固定并由PM纳入**新Revision的精确allowlist/动作表**：每个原型源码/fixture/依赖清单及lock/入口文件、所消费只读DAA源清单、必要角色tasks/checklist、文档结果位置；选用的隔离依赖/构建cache路径；私有run root及其中source/deps/build/DAA-profile/output/evidence职责；owned loopback两个endpoint和冲突测试socket；允许的编译/启动/连接/故障注入/清理动作及责任。不能先创建文件再补批准，不能只写“允许某目录全部”或靠tasks放宽。

最终原型只使用显式owned系统tmp工作区和`127.0.0.1`非102高位端口（建议从20000–59999选择两个经占用核对的端口，具体值待P0批准）。不得读真实.env、默认DAA profile、客户资料、真实PLC/Backend/API；不绑定wildcard/非loopback、申请管理员或修改系统服务。端口竞争时明确失败，不扫描/抢占/kill占用者、不随机换端口掩盖结果；之后在获批端口表内重新核对再开始新run。

## 4. 编号需求

### R1. 保持G0交付小范围

只交候选决策、最小统一内存/准入harness及真实S7/DAA模块互操作、资源原始证据与限制。所有以下“运行/测试”均指未来获批执行；本轮不执行。沿用004目标，不实现产品UI、DB/UDT导入、SQLite保存/apply、完整规则引擎或完整DAA采集应用。规则、普通UI、一次性维护、init/reset可由标明来源的harness触发；它们验证受控入口，不宣称产品页面/IPC已实现。

### R2. P0冻结环境、来源和执行面

进入任何原型运行前须有可审查的P0 manifest：候选库精确版本/commit或发布包SHA、完整源码manifest与本地改动patch、native二进制SHA/动态静态链接/编译flags/ABI/目标架构；client版本/源与编译feature；OS/build、CPU物理核/逻辑线程、RAM、背景负载与采样工具口径；主/子进程资源模型、所有写入口/系统dispatch/阻塞点；第3节源码与依赖/输出/端口/动作精确表。参考主机至少4物理核、16GiB RAM、SSD，仅报告本次一个明确OS/架构结果，不外推三平台。

G0建议固定classic S7 PDU上限480B、单frame上限512B、单item应用payload≤256B、每PDU≤4items且实际请求/响应均可装入协商PDU；COTP分片累计重组也限480B且绝对期限不重置。协商AMQ、最大错误响应、描述符/stage/copy及系统socket buffer实额须从冻结实现计算，列完整最坏输入+输出预留公式。数值只是这个G0有限profile，不缩改004产品容量合同；不能静默降PDU/请求或用不可控库内队列冒充有界。无法控制/观察者在对应gate blocked或判候选不满足，先回PM决定。

### R3. 先证明可拒写再选语言与库

按第2节逐候选给证据支持的adopt/reject/blocked及原因，核回调时机、错误传播、线程/ABI/指针生命周期及未列操作。写前入口必须能阻止image更新并让客户端收到真实S7 item失败；无入口即淘汰，不得降为写后报警/回滚、tick修复或仅UI禁用。正确FFI、小adapter和受控sidecar的精确实现面尚待批准；P0来源/ABI不明时不执行不安全回调。

### R4. 单owner、提交事件与拒写证明

每实例唯一image owner，所有读复制、来源准入、coverage/type/CAS复核和单item提交可追踪。非法写的静默测试先暂停规则并封其他合法写/排空在途，在同一epoch、同一已确认布局下保存**全部可能触达DB的完整bytes/hash、全image hash、instance seq、点版本/来源/更新时间**；失败后逐字节相同，客户端有真实失败。未知DB/越界/未列系统操作还核所有已分配DB，不能只看第一个点。

仅最终读回相同不足以证明写前拒绝：同时给冻结源码调用链与`request_received -> admission/type/owner_decision -> rejected(no commit) -> item_response`事件顺序；合法路径为`accepted -> commit_begin -> committed(seq) -> response`。在实际mutation入口计数/记录写前写后，证明拒绝item无任何commit/裸buffer写，再无“恢复旧值”动作。并发测试另按item/result ID、触达点版本与获准写范围对账，允许其他合法提交改变实例seq/hash，不能要求规则运行时全image绝对不变。观测本身不能改内存。

### R5. 原始bit/byte、typed包及item结果

覆盖BOOL邻位与整byte、全触达跨权限、部分标量、边界/长度/transport-size/count、有限REAL、大端整数、STRING完整包/长度头/ASCII与多item部分成功。每write item原子，失败全item不变；读item来自单epoch/seq复制，多item按内部顺序逐项并允许连接/规则交错。不同PDU/DB/实例无全局原子承诺。未列非DB区/CPU控制/clock/块操作/任意SZL不可绕过入口或映射为DS控制；必要最小握手元数据按P0白名单逐项列出，不接受库默认“成功但无作用”当拒绝。

### R6. 六种写来源收口与权限/CAS

client、rule、普通UI、一次性ui_maintenance、initialize、reset均从harness进入同一owner或同锁封闭maintenance模式。普通UI仅ui-owner；一次性维护只对显式允许的client/none hold，默认关，不改变持续owner，后续合法client可覆盖；rule暂停仍不让权。UI/维护带expected loaded revision/epoch/point last_seq，在提交边界CAS，冲突不写/不自动重试。init/reset仅封闭gate/stopped，非法运行中调用拒绝；reset为新epoch/初始化，stop-start保值。这里只验证入口合同，不新增持久apply/保留算法或租约。

### R7. 16会话与C/H/TCP/closing计数

一个PLC=一个server实例，C为**已建立S7 sessions**，非进程/IP/TCP accept数量。沿用默认C16、整数1–64（>16未验证）、H4整数1–16、accepted TCP=C+H默认20；closing直到socket/callback/worker真释放仍占先前C或H和TCP。全局C/H/TCP128/32/160、全树≤64线程/≤1024句柄均为硬预算，启用实例配置和不得超预算，0/负/小数/无限拒绝，修改只stopped显式载入；G0仅运行单实例16及两实例各少量兼容连接，不跑2×16/8×16。配置域边界/全局加总可由无端口的harness校验，不冒充64/128会话容量。

满额拒后来者、不抢占老连接、不重置hold、不提前虚减closing，不在同socket阶段转换重复计数。库MaxClients参数不能替代真实C/H/TCP各阶段准入及计数，短命超额accept句柄也须列入实际OS资源，不隐去。连接快照须有instance/connection ID、peer、阶段、建立与最近收发完成时间、执行/等待/bytes、拒绝/超时/关闭原因；无需产品面板，但独立QA能核逐连接事实。全局上限不代表与线程/CPU预算能同时打满；每连接一线程候选不得由本次16会话外推128或静默提高64线程预算。

### R8. 期限与有限队列/输入输出预算

沿用握手5s（accept起算）、半frame2s（首byte起算）、待提交2s（完整PDU准入/等待起算且commit复核）、send2s（响应开始发送起算）；滴流不续期，正常idle踢出默认关闭。每连接≤1执行+2等待PDU及64KiB全部协议bytes；实例等待≤64PDU/1024items及1MiB；全局等待≤256PDU及4MiB；UI等待4、普通控制8、每规则待tick1。bytes包含未完frame、执行/等待、描述符、stage/copy及最坏响应预留，转阶段不重计、复制新增计、closing仍计。

整个PDU输入/输出先原子预留，再执行第一item；预算不足真实失败或关闭该连接，无item已提交。单个写callback不能替代整PDU入队/最坏响应预留或逐item结果/内部顺序；P0若无法观察控制这些阶段，须判不满足或回PM改方案，不默许重写协议栈。PDU/item超协商/超限、send阻塞、未完握手和半报文均有明确结果。G0对未能由16会话/480B profile触达的实例/全局大上限，以**标明test-only的更小预算或确定的reservation故障注入**验证相同准入控制点及归还，不声称填满4MiB/1024items；正常profile硬上限不提高。协商AMQ较小时如实列实际可达状态，不伪称已实测1+2并行。网络收发/解析/编码、磁盘及证据写入均在owner临界区外。

### R9. 公平、规则合并与控制可达

沿用协议→规则→UI非空类轮转，协议内连接round-robin每次最多1item，同PDU保序；规则按point轮转且每规则最多1待tick、合并计missed/coalesced。用F洪峰、A/B低频、8规则及UI维护同时存在的60s场景验证。已经准入且持续可调度的F/A/B三连接，每次protocol类轮转至多3次dispatch让各方一次；三个工作类持续非空时每3次工作类dispatch各获一次。保存调度轨迹/资格时刻，不能把库锁外看不见的等待从统计中删掉。

正常低频请求p99≤250ms，无连续1s完全不服务的已准入A/B；规则与1Hz UI请求可达。过载可真实拒绝，但已预留工作/stop不能饿死；恢复基准5s内等待队列回零或稳定基准，无无界补跑。stop走及时通道，先关准入/accept，取消未进不可取消段者，当前已进段单item完成一次；不得等完整PDU或长积压提交完才处理stop。

### R10. 真实DAA自定义端口兼容

未来必证使用固定版本DAA **真实ManagedS7::connect/read/read_bounded/disconnect**，`rust-snap7-driver`开启、`local-validation`关闭，不以Python参考client、FixtureTransport或origin标签替代。推荐最小隔离harness消费**字节相同的ManagedS7及所需DAA domain依赖快照**，保留原RemotePort/rack/slot/超时调用；精确源清单/依赖/编译入口及feature由P0审查批准。若私有API/feature/安全profile无法这样消费，结果blocked，回协调申请独立DAA范围，不能修改原DAA/改成重写近似client后声称兼容。

G0证明层级为真实DAA客户端模块对候选server的S7互操作，不覆盖完整DAA GUI/SQLite采集/历史/上传/native窗口。推荐harness不创建DAA业务库，不读任何env或默认profile，只从批准的owned内存Plc参数调用；若实际入口必须创建隔离DAA profile/数据库，其路径/动作须先另列获批执行面，禁止擅自走生产启动。明确禁上传、Backend/direct DB/授权服务/旧采集/auto-start；连接/读取仅两个owned endpoints。

### R11. 关闭、资源释放与未知回执

单连接close与全实例stop都先关相应准入，取消未进入不可取消段者，让已进段单item完成一次，然后join回调/worker、关socket/listener、停timer/清队列并幂等释放。正常单连接close/stop≤2s，故意积压/慢连接stop≤5s；超时保留closing/stopping/failed及实际名额，不假报stopped或释放仍被callback使用的buffer。未提交超时/取消=拒绝不变；已提交但回执丢失=结果未知，无回滚/自动重试/exactly-once。

记录全进程树CPU/RSS/线程/句柄及分项socket/listener/callback/timer/队列bytes/输出预留；client进程单列，不藏入或混同DS指标。检查同端口重绑、20次start-stop、16连接各10轮重连、重复关闭通知。若选sidecar，父进程正常退出/崩溃、子进程异常退出与A/B隔离必须实测，5s内无owned孤儿和占用端口；G0管理harness不等于Tauri原生退出。进程内native硬崩溃可能波及全进程须如实给隔离风险，不能靠逻辑instance ID宣称崩溃隔离。

### R12. 证据、统计与可复现交接

原始JSONL按run/candidate/build/instance/connection/request/item/result/epoch/seq及monotonic时刻关联；保存raw协议item结果/有界报文、完整合成fixture前后bytes/hash、决策/commit/response顺序、错误与预算变化、版本摘要、资源1Hz采样及状态转换采样、复现命令/退出码/环境。raw payload仅限本任务公开合成数据，不采集真实私有报文。报告offered/accepted/completed/rejected/timeout/unknown分母，逐连接p50/p95/p99/max和队列等待，不能删失败或用聚合平均掩盖饥饿。

证据文件是显式临时输出，不是产品日志/正式schema；证据丢失或关联不全不能判pass/go。沿用004纯日志故障降级原则：可选sink失败不把已提交成功改失败/回放；记录observability_degraded/丢弃，并将该段无法证明的case标blocked后另做新run，不把缺证据当内存已回滚。不要为G0增加强持久审计/SQLite journal。

### R13. 分阶段go/no-go及状态诚实

P0通过冻结/批准gate后，按P1写前拒绝/全来源及item→P2连接/队列/公平/释放→P3真实DAA及最终全矩阵独立复现顺序推进；不能先建产品以待补保护。场景状态为pass/fail/blocked/not_run/deferred，以及严格条件项的not_applicable：pass有实际证据；fail为已运行不符；blocked为必要来源/环境/接口/证据不能取得；not_run为尚未执行或被早期淘汰阻断；deferred只限本spec明确排除的后续阶段；not_applicable仅用于未选sidecar时X02的父子进程专属分支，须给实际进程模型理由，不免除共通stop/资源释放及进程内native风险说明。必证项不能为凑go改deferred或not_applicable。

候选只有全部适用必证case通过、无未解除blocker、清理证据完整才可go；失败候选的后续case可not_run并给停止原因，不冒充通过。可信no_go是允许的研究结论，须指出不满足的实际控制点和复现证据；它阻止后续采纳该候选，不强迫实现完整协议栈。QA独立审核方法/复现和结论，原case fail不得被改pass；即使研究报告被Owner接受，也不代表候选能力通过。更换未列候选、放宽保护/16会话/预算/阈值、增源码/依赖/端口/DAA动作、扩OS/长负载均回PM新Revision和Owner批准。

### R14. 保留工作树与角色权威

本轮PM仅本spec；004十保护文档及旧证据保持。主协调只插入四根索引本任务行，保留DAA/CU等并发修改。后续Development只写获批执行面和tasks，精确handoff后新的fresh-context Verification只验证并写checklist，Owner保留最终接受与风险例外。当前profile为contract_only，串行角色/diff审计是合同控制，不宣称ACL、自动路由或团队激活。本draft文档自检不作G0、QA或Owner接受。

## 5. P1写入/协议场景矩阵

以下仅定义未来输入/动作/预期。**DEV逐行实现harness/自检与保存E证据；fresh QA从固定handoff自行执行并独立解码item/比较bytes，不调用DEV总结冒充复现**。每个确定性向量至少独立重置后重复3次；BOOL竞争另为100轮。失败静默测试按R4关其他写并排空；并发单列，不能混用不变口径。

建议合成fixture（P0固定其raw manifest，不建正式schema）：每实例测试DB41长1024B、DB57长64B，后者为实例身份只读marker；DB号/两个DB仅夹具，不是产品固定拓扑。DB41 byte0.bit0=client BOOL、bit1=rule fixed TRUE、其余reserved；byte1八个client BOOL；offset2 INT、4 REAL；64处STRING[8]全10B、128处STRING[254]全256B；512起16个8B client hold槽（每槽两DINT）。普通ui-owner DINT在48、显式维护client-hold DINT在56；规则为400起6个动态DINT及1个fixed DINT，加byte0.bit1共8规则。未列空位reserved/read-zero/write-denied；A/B初值marker不同、image独立。规则参数仅够触发入口，不实现通用引擎。

| Case / 需求 | 输入与动作 | 可判定预期与必须保存证据 |
| --- | --- | --- |
| W01 · R3/R4/R5 | 真实client向自己8B槽写两个完整DINT的非旧值，raw读回；再读64B marker。 | item成功、逐字节/typed值一致，唯一commit且seq+1；raw请求/回执/读回、owner trace及完整前后image。不能只看client函数无异常。 |
| W02 · R4/R5 | 静默屏障下依次向rule字段、reserved、越权bit、未确认coverage、未知DB写；未确认fixture须在P0声明为故意负例。 | 每item真实失败；全部可能触达范围bytes/hash/点版本及全image/seq不变，拒绝前无commit/裸指针写，回调/dispatch顺序可复查。自动字段即使rules_paused仍拒绝。 |
| W03 · R5/R6 | byte0.bit0合法bit写；向同byte整byte写（含rule/reserved，即使相应值没变）；byte1两个不同client位由双连接同步竞争100轮；byte1合法整byte写。 | bit写只改mask、邻位保留；byte0整byte失败且不变；byte1两位更新均保留，无RMW丢失，合法整byte成功。保存各轮item/seq与目标byte前后，不拿不同并发顺序当失败。 |
| W04 · R4/R5/R8 | 部分INT/REAL、越过client槽末端触及reserved、末端1023+2、0长度、count溢出/transport单位不符/短payload、NaN/Inf REAL及超frame/PDU；合法大端有符号/有限REAL对照。 | 非法输入在提交前失败/无可编码item时关该连接；无越界/分配爆量/其他实例变化，合法typed值可读回。保存每向量原始长度/规范化触达、错误码、全范围bytes及预算变化；格式错误与权限item失败分开。 |
| W05 · R5 | STRING[8]写完整`08 03 41 42 43`加5零字节；STRING[254]完整256B对照；错误max头、actual>max、非ASCII、只写头/截断包/部分包。 | 合法包精确读回；其余整item失败、整个STRING包及全触达字段不变，不截断后报成功。保存原始包/布局、item返回、typed解码与hash。 |
| W06 · R4/R5/R9 | 单PDU顺序3items：合法8B、禁止rule写、合法STRING；其间允许另一已准入连接/规则插入，另做静默对照。 | 真实逐item成功/失败/成功、内部顺序保留，成功各提交一次，失败范围不变；无全PDU回滚/全成功伪造。保存原PDU/result数组与逐item调度/seq，混合结果按触达范围对账。 |
| W07 · R4/R6 | 六写来源各一合法及一非法/陈旧操作：rule对hold/paused/旧epoch，UI及维护CAS冲突，维护默认关和rule即使暂停，运行中init/reset；合法维护后client再次写。 | 全部进入同owner/maintenance模式；非法无commit，合法来源和seq正确。维护不改持续owner/初值、后续client可覆盖；reset仅stopped换epoch，stop-start保值。保存源入口调用图、每操作结果与revision/epoch/point seq，harness不等于UI。 |
| W08 · R3/R5 | 对owned server发非DB区、CPU start/stop、clock、块上传下载、非白名单SZL/未知功能各一请求。 | 明确协议拒绝或有界关闭，无image/DS状态/宿主时钟变化，不能以库默认成功空操作通过。记录dispatch白名单、原请求/结果/前后状态；若库自动处理无法阻止，候选no_go。 |
| W09 · R3/R4/R11 | 在precommit及不可取消提交段用确定harness屏障分别触发timeout/stop/close；另在commit后故意丢回执；复查callback指针引用/注销顺序。 | precommit取消不变；已入段item完成一次，后项取消，已提交丢ack为unknown且不自动重试；旧epoch不能触达新image。保存call/commit/return/close/join/释放时序、引用计数及wire可达结果；禁止释放仍使用buffer。注入屏障是实验工具，不可带入产品owner等待逻辑。 |

## 6. P2连接、队列、公平与资源短程profile

每个数值均为本draft待审阅G0口径，不是实测支持。每个最终候选DEV完整运行一轮，独立QA从新run/profile/端口依同一冻结输入重现一轮；静态早期淘汰者不强行跑后续。不得将这些短程结果替代004 L1–L5。

| Case / 需求 | 有界输入、次数/时长 | 判据及证据 |
| --- | --- | --- |
| C01 · R7/R8/R12 | 单实例16已建立S7 sessions；预热30s后300s。各连接1轮/s，每轮2请求、各1item：DB57读64B+自己DB41槽写8B；8规则=6动态+2fixed，100ms到期。 | 32请求/s=16读+16写，应用payload1152B/s；测量段共9600请求=4800读+4800写、345600B，不含协议头；每连接600请求。按offered全量核完成，非故意错误/错写/越权/BOOL丢更新=0；每连接p95≤100ms/p99≤250ms，排队p99≤100ms，规则missed≤1%（24000到期机会，动态/fixed分列，无变化fixed不虚增commit）。 |
| C02 · R7/R11 | C01的16会话仍读写时，第17个S7连接尝试20次，间隔100ms；再关闭一条并重连，重复close通知。 | 新来者被拒，不抢占/重置原16；关闭直到真释放才腾C/TCP，重连新ID。逐时C/H/TCP/closing/实际established及OS socket、原会话成功item、拒绝阶段/原因均对账，无负计数/重复归还。 |
| C03 · R7/R8 | 另有16已建立时保持4个未完成握手TCP，第5未完成握手尝试20次；随后半frame每500ms滴一byte；另一session idle30s后正常读。每种绝对期限试3次。 | C16/H4/TCP20不超，5th握手无额外持久对象；握手accept后≤5.5s、半frame首byte后≤2.5s完成关闭/清理（含≤0.5s观察裕量，不延长配置期限）。老会话继续；idle不误踢。保存时间起点、阶段、bytes/名额/句柄释放。 |
| C04 · R8/R9 | 单连接超协商in-flight及1执行/2等待边界；另用P0声明的小预算/确定reservation故障触发每连接、实例、全局输入+最大输出预留失败；恢复后重试。慢读peer的实际收/发socket buffer各≤16KiB，20次/s发256B读取且不消费响应，最多30s，须实际观察send阻塞。 | 超额完整PDU在第一item前失败/关该连接、无commit；所有阶段数量/bytes含预留不超实额，幂等归还。发生阻塞的该响应从首次发送尝试起≤2.5s关闭（2s配置期限加≤0.5s观察裕量，不从阻塞时重置），其他连接/规则/stop继续。若只触发队列拒绝而没观察send阻塞，该subcase仍not_run/blocked，不能算send期限pass；不能以注入替代所有真实socket证据。 |
| C05 · R9/R11/R12 | 同实例F/A/B3个活跃连接、其余13个idle：F20 PDU/s、每PDU4个64B read items，A/B各用C01每连接profile；8规则100ms、UI维护1次/s，持续60s。再用小预算制造积压并从及时通道stop，3次；恢复基准观察5s。 | F offered80items/s，A/B合4items/s，规则80次到期/s，UI1次/s；PDU数与item数分别计。正常60s段A/B各60轮=120请求全部按offered完成，60次合法UI维护均有成功结果，不得把低频工作拒于准入外绕过公平；F的完成/拒绝/超时单列。仅随后明确小预算故障积压段允许按真实结果计低频拒绝。按R9轮转/时限判，保存各连接/类资格、dispatch、等待/完成/拒绝、missed/coalesced和stop各阶段；F大PDU不独占、普通控制不饿死业务，过载stop≤5s，恢复队列回落。 |
| C06 · R7/R11 | 16条连接各10轮断开/重连，共160次；每轮含一次正常close、半关闭或异常之一，轮转+100–1000ms固定seed抖动；随后20次start-stop，每次建立16session并各读/写1次，stop后等10s采样。显式reset另3次。 | 正常close/stop≤2s、故意积压stop≤5s，所有owned listener/socket/callback/工作timer/队列PDU/item/bytes/输出预留回0；stopped保留image/值不算泄漏，reset独立初始化。停止后同owned端口可重新bind，无隐形worker/旧epoch写。保留完整cycle序列，不把10轮写成004 L4每连接100次。 |

C01及上述所有阶段分别保存全DS核心/管理器/sidecar进程树的平均CPU、RSS峰值/净增、线程/句柄及分类；**client/采样进程单列**。G0目标：平均CPU≤单逻辑核100%（CPU时间/墙钟，不除主机核数）、RSS≤512MiB、线程≤64、句柄≤1024；C01测量段RSS净增≤16MiB。这是短程可行性阈值，不声称004的60min增长或长稳定性已满足。

C06资源基线为依赖已加载、image已分配、证据sink/采样器已启动但无listener/连接的稳定stopped状态B0；首轮热身后固定B0。每次stopped10s时owned transport/callback/工作timer/queue/reserve=0，线程/句柄按分项回B0；明确保留的单一库全局设施须P0计入B0，不能逐cycle追加。RSS允许allocator保留但每次≤B0+16MiB，最后5次中位数相对最先5次≤8MiB；若出现连续4组（每5次一组）严格增长且总增>8MiB则失败。原始曲线与峰值均交付，这些口径不能证明永不泄漏。

两个实例仅为端口/故障隔离对照：A16会话场景时B至多1参考会话；真实DAA场景各1。该组合ΣC默认配置32、ΣH8、ΣTCP40，仍受128/32/160及64线程/1024句柄联合预算；不能用名额配置推断2×16吞吐。>16实际会话、8×16、全局极限、大布局以及完整L1/L2的5min预热+60min和L4/L5长故障均明确deferred到D4或另批扩展任务，不在G0凑齐。

## 7. P3真实DAA与退出边界矩阵

责任同第5节：DEV提供精确非fixture入口与原证据，fresh QA独立运行、核source/feature、协议和OS状态。P0执行面未批准前以下均不执行。

| Case / 需求 | 输入与动作 | 预期与证据 |
| --- | --- | --- |
| D01 · R2/R10 | 两个owned非102端口、A/B各自固定called TSAP/rack/slot和不同DB marker；字节冻结的真实ManagedS7各持1会话，60s、每连接1轮/s，每轮读取两个DB各1次；参考client改变允许hold值后再DAA读取。 | 两模块累计240次真实db_read，连接复用，能按marker/bytes/变化值区分实例，RemotePort实值与COTP/S7协商、调用trace相符。提交源/feature/native摘要、raw字节/DAA结果及server connection ID；fixture/标签/截图不能替代。只证明模块级S7，不证明完整DAA采集或GUI。 |
| D02 · R7/R10 | 错rack/slot产生错误called TSAP、owned无listener端口、A参数误指B端口；每负例3次；另用owned冲突listener阻止A启动，重复start。 | 错TSAP明确失败，不能同端口隐式复用/接受任意身份；错端口不回退102/扫描其他地址；冲突只使后来A failed、占用者和B继续、无第二listener。每次记录真实COTP、RemotePort、失败阶段/错误与名额释放；若候选默认接受错TSAP，必须先取得可控adapter证据或判不满足。 |
| X01 · R4/R11 | A/B均在服务时只关闭A一条连接；另在W09屏障处stop A，B持续读；超时注入后再观察实际清理及同端口重绑。 | 关闭只影响指定对象；未提交取消/已入段完成/已提交丢ack未知分开，B不变。正常2s/故障5s，超时不报stopped；只有callback/socket/worker真实归零后才释放/重绑。保存进程/OS/库计数和owner事件关联。 |
| X02 · R2/R11 | 若选择sidecar/每实例进程：父管理harness正常退出、父异常终止、A子进程异常退出，各3次；同时观察B，随后新run重开。 | 正常有序stop；异常时≤5s无owned孤儿/残留listener，A子崩不误报clean且B继续；重开只初始化fixture、停机，不恢复旧连接/未知写。完整进程树/PID起止/退出码/socket证据。未选sidecar则明确not_applicable理由，不宣称该能力；进程内native硬崩风险单列，完整Tauri退出与三平台发布仍deferred。 |

资源/异常测试只操作获批本任务owned进程和loopback socket；不停止DAA原生会话、不修改其profile、不向任何真实设备或生产DB/API发动作。若不能在准确进程树中区分归属，先blocked，不批量kill或清理未知资源。

## 8. AC与可审阅覆盖

下表是未来**研究交付及选型判断**的验收口径，非本轮结果。每一行均须有DEV原始证据和fresh QA独立观察；候选go必须满足对应功能预期。充分证明的no_go可以交Owner作为研究结论，但失败case原样保留，不能写成“所有功能通过”；必要项无证据仍为blocked/not_run。

| AC | 对应需求/场景 | 可核验标准 |
| --- | --- | --- |
| AC1 | R1/R14、§1/§3 | 独立namespace/Task ID/Capability/接受链、draft及五路径准确；004文档接受不移作G0批准；当前只spec，无空tasks/checklist/工程/执行。 |
| AC2 | R2/R3、P0 | 全部源码/版本/包与二进制SHA/ABI/OS/feature/client/资源模型/预算公式/端口/profile/精确动作表已冻结并取得执行Revision批准，才进入运行；未齐则blocked且不开工。 |
| AC3 | R3/R13、§2 | 候选比较与推荐顺序有primary/冻结源码依据；明确Rust wrapper/Python stub、系统dispatch及资源控制不足，给可复现adopt/reject/blocked及最终go/no_go；不自写完整协议栈或放宽保护。 |
| AC4 | R4/R5、W01 | 合法真实写成功、唯一commit/seq及原始bytes/typed读回一致；独立QA可从raw item和image核实。 |
| AC5 | R3/R4、W02/W09 | 静默/屏障下全触达bytes/hash/seq/版本/时间不变，真实失败且调用/提交顺序证明无先写后恢复；并发另按合法item范围和点版本对账，不要求全局hash冻结。 |
| AC6 | R4/R6、W07 | 六来源全部收口，普通UI/一次性维护范围及CAS、rule暂停不让权、init/reset停机权限/旧epoch均实证；harness与产品UI/持久功能边界准确。 |
| AC7 | R5、W03 | 合法bit邻位保留、100轮同byte两bit无丢失、合法全byte与含禁bit整byte拒绝均可重现。 |
| AC8 | R5/R8、W04 | 部分标量、跨权限/边界/长度/transport/count/载荷与REAL负例逐项真实失败，不越界/无隐藏分配；合法大端/有限REAL对照可读回。 |
| AC9 | R5、W05 | STRING[8]/[254]全包成功及头/长度/ASCII/截断负例不变，raw包、item结果及完整包hash齐全。 |
| AC10 | R3/R5、W06/W08 | 多item部分成功/保序、失败范围不变且非PDU全原子；非白名单系统操作明确拒绝/关闭、无DS/宿主副作用，不接受“成功空操作”替代。 |
| AC11 | R7、C01/C02 | 16真实S7会话同时读写、第17条20次拒绝不抢占；计数从TCP/H到C/closing/释放逐态对账；1–64/>16未测及全局128/32/160与64线程关系准确。 |
| AC12 | R7/R8、C03/C04 | H满/握手、绝对半报文、正常idle、真实慢接收send及释放期限均有起算和原证据；未实际触发send不报通过。 |
| AC13 | R8、C04 | per-connection/instance/global数量和所有阶段bytes/最坏输出预留先准入，超限无item执行且归还一次；小预算/故障注入与实际大上限未触达准确分层，owner无网络/磁盘等待。 |
| AC14 | R9、C05 | 连接与工作类按item轮转/保序、规则合并、A/B低频及UI/普通控制/stop可达；正常60s内A/B各120请求全完成、60次合法UI全成功，不能靠准入外全拒绕过公平。有资格和调度轨迹、逐连接分位数/拒绝分母及恢复回落，不能仅总吞吐。 |
| AC15 | R2/R10、D01 | 精确DAA ManagedS7真实feature、RemotePort/rack/slot/COTP/读链与240次db_read可定位；不改DAA、不读真实env/profile、上传关闭；模块级与完整产品界限清楚。 |
| AC16 | R7/R10、D02 | 错TSAP/端口、双端口身份隔离/端口冲突/重复start负例均可复现，不回退102/抢占/隐式复用；私有API/feature不满足时blocked而非换fixture。 |
| AC17 | R4/R9/R11、W09/X01 | stop/单close先封准入取消未入段，仅当前不可取消item完成；未知回执与确定拒绝分开，无回滚/自动重试，超时不假stopped，其他连接/实例继续。 |
| AC18 | R7/R11/R12、C06 | 160重连、20启停、3reset有原始序列；socket/callback/worker/timer/队列/预留回B0且可同端口重绑，重复释放幂等，RSS/线程/句柄按定义无超额增长，保值/初始化语义不混同。 |
| AC19 | R2/R11、X02 | 若选sidecar则父子正常/异常退出与A/B崩溃隔离3轮证据满足5s边界；不选时理由与进程内native风险可审阅，不把G0管理harness当Tauri原生/三平台证明。 |
| AC20 | R2/R12、全矩阵 | 每run source/ABI/环境、raw item/bytes/事件/错误、1Hz资源和状态转换可关联，offered全分母、逐连接p50/p95/p99/max、CPU/RSS/线程句柄/队列/规则missed/stop均报告；C01/C05算术正确，证据缺口不算pass。 |
| AC21 | R1/R13/R14、§9/§10 | go/no_go与case/QA/Owner层次分开，fail/blocked/not_run/deferred真实；候选失败或改范围回PM，不把004/G0/文档检查当产品批准；既有文档/并行dirty/旧receipts保护，DEV与新fresh QA逐角色真实建立。 |

## 9. 风险、回退与明确排除

| 风险/未决gate | 处置与Owner需审阅的取舍 |
| --- | --- |
| native回调、ABI或默认系统命令不满足 | 先只读P0筛选；有可审计小adapter才提执行Revision。返回值/内存入口/拒绝不可控即淘汰，不以回写或成功空操作豁免。 |
| native hook锁/线程/缓冲隐藏，16能连但不公平/不能退出 | C/H/queue/资源可控点是必证；任何不能有界释放/观测的关键面阻止go。通过16也不证明>16或L1–L5。 |
| DAA真实入口与fixture隔离机制不兼容 | 推荐固定真实模块的隔离消费，不改当前DAA；无法安全调用则blocked并申请独立DAA范围。不能利用默认env/生产profile或同名重写client消除blocker。 |
| 原生库/sidecar崩溃影响其他实例 | 先明确实际进程边界；选sidecar须X02，进程内硬崩风险保留并由Owner决定后续隔离。不能用逻辑隔离作OS崩溃隔离。 |
| 静默拒写试验被规则/合法并发污染，或先写后恢复伪通过 | 屏障、不变基线、mutation入口事件及源码链同时使用；并发按item/范围对账，证据无顺序或丢失则blocked重做新run。 |
| 单OS/短程和缓存包被当跨平台/长期能力 | 本轮缓存源码仅事实观察、非包来源验证；P0校来源/ABI。G0只报告冻结OS与有限profile，目标平台/发布及长负载另批。 |
| 选型趋向大规模协议重写/依赖升级/产品实现 | 当前draft不实施；未来超小adapter/两候选/指定矩阵的工作回PM新Revision，不继续扩写。no_go可以是可信交付。 |

回退只处理本任务明确delta或未来获批owned实验资源；本轮只有新增spec可逆修订，不reset/覆盖已有工作树。未来实验失败先封准入、按真实提交边界退出、保留错误与原证据；只清理已确认归属且不再承担证据/后续依赖的资源，由主协调收尾，QA不回收。端口冲突不碰占用者；旧004/DAA证据不得删除或改写。

排除完整DS工程/Tauri壳/CU页面/安装包、导入器/点位编辑/配置SQLite/schema/迁移/持久apply/运行值保留九场景、完整DAA采集/历史/上传及DAA修改、Backend/SMA/CA/真实PLC/现场网络、生产数据库/API/上传、Modbus/完整PLC执行或协议栈、长期服务/后台守护、完整L1–L5/8×16扩展、三平台native/发布部署、Git refs/提交/推送、外部消息。G0可用合成内存fixture证明init/reset/stop保值路径；不能把它扩成配置恢复实施。

## 10. 角色交接、skill路由与批准记录

1. **当前PM → Human Owner**：只交本r1 draft及第3节五路径/必要自检，等待精确Task ID/Revision范围审阅；不将用户“先整理”记owner_approved。主协调唯一、其他会话不并行编辑本任务。
2. **未来P0 → PM/Owner执行冻结**：按R2只读补齐具体候选/源码/依赖/ABI/DAA安全入口/输出/端口与动作。当前缺少精确实施allowlist，不宣称可开工；需新Revision明确批准。不能先创建原型或tasks等批准。
3. **获批执行Revision → Development**：真实命名development消费完整当时bundle/起点/来源，才建立本任务tasks，写批准的最小harness并按P0–P3自检。读`aiis`、`project-governance`、aiis资源归因/运行日志参考；Rust核心/ManagedS7/FFI/sidecar用`rust-runtime`，PLC地址/类型用`plc-point-mapping`；若独立工具形态落tools用`project-tooling`；只有触达Tauri壳才加`desktop-tauri`，本G0不默认引入。Python/C++仍遵语言无关边界，不因Rust skill改换语言；UI/locale不是本范围。
4. **精确developer_handoff → 新fresh-context Verification**：实际命名verification且`fork_turns=none`，独立核source/feature/ABI、raw协议/bytes/计数/资源/失败与未运行项，按获批spec新建checklist；不得以DEV self-check、004文档QA或别的DAA测试替代。对no_go独立重现最早阻断case并核其余not_run原因，保留候选fail；对go完整重现所有适用必证case。输入变化须重新精确handoff，不继承旧结论。
5. **QA → Human Owner**：报告研究交付的独立verdict、候选go/no_go、证据限制/风险与未来D1–D4/L1–L5 gates。最终Owner可接受可复现的否定选型结论；不自动给失败候选通过、允许部署/设备/产品实现或修改004。

| 日期 | Revision/阶段 | 真实记录 |
| --- | --- | --- |
| 2026-10-18 | ARCH-AW-005 r1 draft | Human Owner要求先整理G0 spec、先不改代码；主协调核未占用后分配独立Task ID，实际PM形成范围与验收草案。当前无精确范围批准、执行面冻结/批准、Development、G0运行、独立QA或Owner终验。 |

Human Owner scope approval of exact ARCH-AW-005 r1: **pending**。

P0 exact execution Revision / source / dependency / owned ports approval: **pending**。

Human Owner final acceptance of ARCH-AW-005: **pending**。

## 11. 本轮PM文档自检与交付限制

PM已读根AGENTS/README/PLAN双语、docs/plans索引、canonical workflow、实际pm TOML、完整004 spec/tasks/checklist与497行DS正文，以及G0涉及的AW/DAA/tool最近说明、源码/声明依赖和primary资料；使用aiis/project-governance及跨端合同、资源归因/运行日志参考。具体技术skill留未来对应角色按已批准执行面加载，本轮没有代Development做技术实现。

起点为`/private/tmp/arch-aw-005-r1-spec-oono_1zh/`主协调baseline/before及本角色`pm/role-start.json`；其中10份004/既有正文与四共享索引单独保护，其他dirty保持。PM仅做Markdown本地链接/锚点/表格/围栏/空白、R/AC覆盖、G0算术、单文件delta与保护摘要自检，实际命令/结果在完成检查后记录于本节及`pm/receipt.json`；tmp附件不是唯一范围权威。

实际必要自检：`/usr/bin/python3 /private/tmp/arch-aw-005-r1-spec-oono_1zh/pm/check-spec.py`为exit0；R1–R14、AC1–AC21全部覆盖，19个case与AC对应，当前精确五路径、仅spec阶段结构、16个本地链接（5含锚点）、10表、0围栏及尾空白通过，C01/C05/C06/D01与名额/夹具算术一致；10保护文档与起点原字节相同。`git diff --check -- plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md`为exit0；`git diff --no-index --check /dev/null plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md`为exit1、stdout/stderr空，代表新增文件有差异且无空白诊断。共享根索引尚待主协调新增本任务行，其既有DAA等并发delta不归PM、不回退。来源采集辅助脚本初次因缓存无可选`.cargo-checksum.json`返回exit1，仅写tmp副本；据已保存副本生成来源摘要后exit0，如实保留“包完整性未独立验证”，未放宽P0。以上均为文档/来源自检，不是原型运行或独立QA。

本轮所有G0场景未执行；没有创建程序/测试/依赖/配置/schema/SQLite/profile、构建/安装/运行项目、监听/连接/负载/设备或Tauri实验，也无服务/端口/tab/数据库/分支/worktree占用。只新增本spec和当前私有tmp文档检查/来源附件，旧004三目录与所有receipts保持；PM正式handoff后停止写入，由主协调机械新增四索引行。
````
<!-- END R1 EXACT SNAPSHOT -->
`````
<!-- END R2 EXACT SNAPSHOT -->
``````
<!-- END R3 EXACT SNAPSHOT -->
```````
<!-- END R4 EXACT SNAPSHOT -->

## 附录B. 2026-10-22 已批准的操作手册与截图文档增量（当前文档gate）

本附录是同一ARCH-AW-005 r5在Owner终验前的明确文档补全授权，不创建新Revision或Task。其前全部原文保持原字节；原批准spec SHA `67155fe4fca3068ef8e616dcf0ade69a5cdc614e7175a2f1ef4c6bf98f935419`不被倒称已覆盖以下新增成员。2026-10-22（Asia/Shanghai），本协调会话Human Owner消息`01a1622f-337a-7741-a830-68321d8da01f`逐字原话：

> 可以，按这个方案补齐 DS 完整操作手册，先手工建点跑通，再演示多 DB/UDT 导入。每一步写清页面、按钮、填写示例和预期结果，关键步骤配截图，同步 README 和 docs 对应的 DS 文档。只改文档，不改代码、不重跑整套协议测试；DAA–DS SQLite 联调另批，阶段 C 暂不开展。

当前产品候选`306a09d5317931482a59f45da5eafcb9d3ee739199799f475ade1891fb0b00b4`已由独立Verification记录qa_passed，Owner最终验收仍待完成。本附录登记授权，不把原产品QA改写成本次文档/截图已验；当前gate为Development完成下述文档增量，再由fresh-context Verification仅核本增量，Owner最终接受链不变。

### B.1 精确文档面与案例

沿用§5的D/T5/A5定义；下列路径均相对于D=`automation-world/device-simulator`，作为本次已获明确授权的新增allowlist，原技术R/AC、原allowlist及完整r4/r3/r2/r1历史不改。

| 精确新增成员 | 用途 |
| --- | --- |
| `USER_GUIDE.md`、`USER_GUIDE.zh-CN.md` | 完整双语操作手册，按真实页面/按钮/输入示例/确认动作/预期结果及常见阻断组织。 |
| `docs/user-guide/images/README.md`、`docs/user-guide/images/README.zh-CN.md` | 原生截图来源、步骤、脱敏/合成输入、原件哈希与事实边界索引。 |
| `docs/user-guide/images/01-workbench.png`、`docs/user-guide/images/02-instance-editor.png`、`docs/user-guide/images/03-manual-point.png`、`docs/user-guide/images/04-manual-layout.png`、`docs/user-guide/images/05-policy.png` | 工作台、实例、手工点、布局及策略关键步骤的真实原生截图。 |
| `docs/user-guide/images/06-apply-preview.png`、`docs/user-guide/images/07-online-values.png`、`docs/user-guide/images/08-import-bindings.png`、`docs/user-guide/images/09-import-names.png`、`docs/user-guide/images/10-reopen-stopped.png` | 应用预览、在线值、导入绑定/命名、重开stopped的真实原生截图。 |

既有D的README双语仅补快捷入口/手册链接，BUILD双语仅在必要时澄清启动及pnpm提示；`docs/AIIS_DS_Detailed_Design.md`及`docs/README.md`、`docs/README.zh-CN.md`同步操作说明/入口事实。D的PLAN双语和根PLAN双语、plans/README双语仅同步文档导航/真实状态；主协调机械同步根四索引。Development只更新自身tasks事实，fresh Verification只更新自身checklist，PM仍只写本spec。

手册先写普通`pnpm tauri dev`启动与提示，以及`pnpm dev`的浏览器边界，再依次讲实例/手工DB/点位、地址与名称确认、初值/策略/规则、保存与停机apply/start、在线值和受控维护写、连接关闭、pause/resume/stop/reset、保值与保存重开/错误处理；每步给页面→按钮→填写→确认→预期结果，按当前已实现UI记录，不增加产品动作。

两个顺序案例：先手工DB31，长度8，`BOOL 0.0`、`INT 2`、`REAL 4`；再使用冻结DAA `src-tauri/tests/fixtures/source-import-multi-db/multi.db`与`types.udt`，仅选Alpha/Beta，分别映射DB71/88，显式选择Measure闭包。两文件完整仓库前缀为`automation-world/data-acquisition-agent/`，SHA分别为`456ad00f264f0f5e9b9a0fd8e9960928b9e81b1cf535b273a3a0f996e1ed3b61`与`f594c7c4748b2d9b6c7d1d81f9235b1980e729cf1c4115e29a5084a08b4044fb`。参数只是操作案例，不固定产品拓扑；不改样例、共享core 0.1.0/v1或golden expected，不将TIA初值/RETAIN当作DS初值或跨进程保值。

### B.2 原生取图与辅助资源边界

仅使用已验收同字节productDesktop二进制及其冻结native库，在独立合成`DS_PROFILE_DIR=T5/profile/dev/user-guide-20261022`完成一次文档操作/取图，原始截图及辅助输入放`T5/tmp/dev/user-guide-20261022`。冻结产品源码/二进制/库及只读输入指纹，新文档/图片指纹单列。可按案例运行既有本地DS动作，沿用受限loopback及既有资源规则；不连接真实PLC/DAA应用、不作新协议/吞吐结论、不重跑整套协议矩阵、不让Owner反复关窗，不接触用户真实profile。

现有A5三张浏览器布局预览不能冒充原生操作图。当前CUA无DS条目、旧no-bundle Mach-O按名称/路径/bundle ID绑定失败，是取图可用性事实。为本次明确授权的原生取图，若必要，允许在`T5/tmp/dev/user-guide-20261022/DS-User-Guide-Capture.app`用原字节二进制/库副本（保持所需相对布局）和最薄Info.plist组成一次性识别载体；这是文档辅助资源，不是产品包交付。不得修改/重编译产品源或二进制、重写链接、签名、安装、调用lsregister、修改系统设置/权限或依赖。记录载体成员/Info.plist、原二进制/库SHA和实际绑定结果；若仍不能绑定原生窗口，先报告事实与最小取图办法，不造图或用浏览器预览代替。

截图标明真实日期、页面/动作、合成profile、对应原件SHA与来源，公开图片仅含合成示例。完成后正常关闭并核实本次自有进程/listener释放；TERM不记为正常退出。原件、来源与载体清单按既有A5持久证据规则留档后，只回收无运行/证据依赖的自有载体及临时资源，不清未知资源或用户数据。

### B.3 验证与交接

本次只验步骤与当前UI/源码的一致性、双语对应、链接/图片存在和原件来源、合成案例、原产品及只读输入指纹未变；必要单次操作/取图不替代或改写已完成产品QA。不得安装依赖、修改Node/Cargo/锁、业务源码、schema或真实配置，不新增协议测试/性能结论，不开展DAA–DS SQLite联调或阶段C。若操作遇到真实产品阻断，如实记录并回主协调，不借文档授权修业务代码。

Development交接文档差异、命令/操作事实及截图来源；fresh Verification仅核新增文档/截图/链接及源码未变，保留原协议证据和结论。旧产品指纹、原批准正文与历史不重算为“新文档已验证”；新文档指纹及本增量核验单列，最终仍交Human Owner接受。

## 附录C. Human Owner最终验收与本轮收尾（2026-10-27）

本协调会话Human Owner明确确认“DS 当前版本验收通过，更新 DS-001 和 ARCH-AW-005 r5 的状态并完成收尾，不再追加功能或重跑整套 QA”，同时明确DAA–DS读取至SQLite联调另批、阶段C暂不开展。完整原话、接受边界及资源收尾见[owning checklist的Owner验收记录](checklist.md#owner-acceptance-r5)。据真实决定，本任务聚合状态为**owner_accepted**，本spec范围状态仍为owner_approved。

原独立QA4只证明其精确306a09d5候选和当时适用矩阵；r4、QA1–QA3、DEV N285失败及其它历史均保持原字节/来源，不倒填为当时已验收。附录B后续纯文字手册和初值输入问题由本地[DS-001 r1](../../automation-world/device-simulator/plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001)接续；Owner已取消新增截图及该易用性任务的独立QA轮次，并在本次接受当前版本。本会话另批DIRECT时间/版本/表格整改保持各自的自检与交付边界，不把它们重标为旧QA4已独立运行。

本次仅登记最终接受、同步文档/紧凑证据摘要的验收字段并核资源。原tasks和全部技术结果不重写，不再追加功能、构建、原生操作或协议/整套QA；DS可作为后续另批联调的协议基线，DAA–DS应用读取至SQLite、阶段B整体验收、阶段C、真实设备、长稳和跨平台交付仍各有其边界。
