Task ID: FF-005
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved exact FF-005 r1 slice A on 2026-11-04; PM -> Development within the unchanged scope; fresh-context Verification follows developer_handoff and Human Owner final acceptance remains pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 独立 Rust/Python 基础案例库、真实合成运行与教学验收，以及按实际能力进入的进阶和 C# 案例路线
Owner: Field Flow
Acceptance Chain Reference: FF-005 r1 exact scope approval -> Development of slice A -> fresh-context QA / Verification -> Human Owner final acceptance
Related Task: FF-001 r4; FF-002 r1; FF-003 r1; FF-004 r1; ARCH-TOOL-001 r2

# FF-005：基础与进阶案例库 r1

## 1. 当前授权、目标与批准对象

**当前批准状态：FF-005 r1 `owner_approved`，仅首切片A。** 2026-11-04（Asia/Shanghai），Human Owner在主协调刚交付本r1（三个基础case、首切片A、AC01–AC12）之后紧邻回复原话“批准”。主协调转交该真实决定并现场核对原审稿SHA256=`fa4d1daab23c8b810da2696a51b618c957843baf9db7dac4999a959b10c8a8dc`；批准对象据该相邻上下文绑定为FF-005 r1 A，不是FF-004或B/C。

本次仅登记范围批准与PM -> Development交接，Revision仍r1，原需求、allowlist、AC和风险不变。下文原draft/P0/“尚未批准”“当前不启动”等文字保留其起草时点事实；A的精确范围批准条件现已满足，由主协调实际选择Development实施，之后仍需新的fresh-context Verification及Human Owner最终验收。此批准不表示实施完成、QA通过或最终验收，也不扩大外部动作权限。

2026-11-04（Asia/Shanghai），Human Owner要求：“可以，案例库单独立项为 FF-005，按 STD 先让 PM 整理 spec，不扩大 FF-004 r1 的范围。Rust/Python 先做基础案例，进阶案例和 C# 按能力分阶段补齐，暂不改代码。”当前仅授权P0，**本r1为draft，尚未批准软件实施**。起草前检查FF及根任务索引，未发现FF-005或重复的正式案例库bundle。

FF可能长期作为现场runtime；案例库应让学习者能复制工程、看到真实app、启动合成服务、观察条件与副作用。FF-002已提供通用使用/新增案例教程；本任务增加正式可运行案例和对应证据，新增说明围绕实际案例，不再复制一套通用手册。

| 阶段 | 本r1的范围与效力 |
| --- | --- |
| P0：当前 | PM只创建本spec；主协调仅同步§7列出的四份FF导航。无tasks/checklist、源码、配置、schema、依赖准备、编译、测试、初始化、监听或项目运行。 |
| A：精确r1获批后 | Rust/Python各自交付三个基础case：复用demo01，新增PLC条件后GET→INT及GET值多条件→INT；必要显式kind/dispatch接线、两份YAML、自有有界真实CLI测试与双语案例说明。仅现有GET、标准DB INT、Owner.read和Execution能力，无新依赖/协议/状态schema。 |
| B：后续能力gate | 进阶案例先列业务目标；相应底层能力实际实现并完成适当验收后，另以新Revision或独立任务冻结范围，才能实施和标为runnable。A不隐含B。 |
| C：后续语言gate | C#先独立形成可用runtime及对应能力，再补同一case ID/业务验收集合；FF-003草案不能当现有底座。本r1不创建C#工程或案例。 |

若Human Owner明确批准“FF-005 r1”，批准对象为A及其有界合成验证、§7未来allowlist和AC01–AC12；普通接线不另设批准gate。原请求、方向同意、其他任务批准或沉默均不是该批准。当前不启动Development/Verification。

本任务是独立`root`，无Parent Task ID。
FF-001/002本地QA通过、Owner终验待定与本任务分开；FF-003/004仍draft。
全部既有bundle及历史保留。
FF-004 r1保持原字节，读时SHA256=`e33aae41d18ba7faad19cb1ed563a19375996bc0f5d23ee7c646d62b2f7b0dc4`，不借案例库加入或提前实施其JSON/点位句柄方案。

## 2. 源码依据与当前能力

已按序读取根AGENTS、README/PLAN双语、[canonical workflow](../../../.codex/workflows/development-lifecycle-workflow.md)、实际pm角色配置，FF及两工程最近README/PLAN/catalog、FF-002完整现有三文件、两工程中英USER_GUIDE的方法/teaching01教程、FF-004完整r1和FF-003当前范围。
无更近AGENTS；FF-005目录及C#工程此前不存在。
下表为本轮只读核对，不是新的运行证据。

| 来源 | 当前事实/约束 |
| --- | --- |
| [Rust app](../../field-flow-rust/src/app/demo01.rs)、[Python app](../../field-flow-python/src/field_flow/app/demo01.py) | 正式app均只有demo01；GET→严格typed输入→Execution。FF-002的teaching01仅为文档/临时副本接线教程，不是正式案例库。 |
| [Rust config](../../field-flow-rust/src/config.rs)、[Python config](../../field-flow-python/src/field_flow/config.py) | YAML schema_version=1，Flow有get_url/source_id/target等完整字段，仅接受kind=demo01；最多4 PLC/8 flow、INT物理目标冲突校验。没有按kind分型的读流配置或JSON目录。 |
| [Rust runtime](../../field-flow-rust/src/runtime.rs)、[Python runtime](../../field-flow-python/src/field_flow/runtime.py) | 显式直接调用demo01，无自动发现；独立flow任务，同流一轮结束后等待interval，每PLC持久owner/driver和有界串行IO。Rust iteration返回Result<()>且FlowHealth无业务result；Python已有health.result。 |
| [Rust domain](../../field-flow-rust/src/domain.rs)、[Python domain](../../field-flow-python/src/field_flow/domain.py) | 七键输入、INT值及源时间校验、既有Intent摘要/物理Resource；配置kind/flow等属于效果身份，不能假装跨case共用旧命令状态。 |
| [Rust Execution](../../field-flow-rust/src/services/execution.rs)、[Python Execution](../../field-flow-python/src/field_flow/services/execution.py) | 唯一应用写路径；dry_run接纳simulated不写PLC，execute按既有身份/TTL/ACK/unknown保护。不能在案例里调用raw writer或直接改执行表。 |
| [Rust fixture](../../field-flow-rust/src/fixture.rs)、[人工入口](../../field-flow-rust/src/bin/ff-fixture.rs) | 自有HTTP/proxy/native S7，DB1/16字节初值全A5（offset0 INT=-23131）；CLI固定cmd-001/value42，ENTER关闭；测试API有command/body和计数。 |
| [Python fixture](../../field-flow-python/tests/fixtures/runtime.py)、[人工入口](../../field-flow-python/tests/fixtures/__main__.py) | 自有HTTP/proxy/S7子进程，同样A5初值；CLI固定本次生成身份/value42、取首flow source，SIGINT/SIGTERM关闭；测试可设置command/body。 |

现有方法按真实对象组合：Rust `Owner::read(&self, flow:&str, db:u16, offset:u32)->Result<Sample>`、`Http::get`、`Input::intent`、`Execution::apply`；Python `await owner.read(flow.id, db, offset)`、`HttpClient.get`、`parse_input`和`execution.apply`。
Python新读案例由runtime显式传入已有owner，不将Execution内部对象包装成稳定SDK。
不存在已实现的`devices[id].read(point_id)`、HTTP POST、Modbus、BOOL/REAL或自动注册。

## 3. 案例矩阵与能力版本（R01）

case ID是教学/验收身份，与flow.id、kind、source/command身份分别说明。Rust/Python使用相同case ID和业务判断；API形状遵循各语言，不要求逐行同构，也不要求所有未来生产flow三份同步。

| Case ID | 目标/正式入口 | Rust/Python当前状态 | r1 A后状态/前置能力 |
| --- | --- | --- | --- |
| basic01 | GET→严格命令→INT；复用`app/demo01`、kind=demo01、`config/loopback.yaml` | 已有实现；原QA归FF-001/002 | 纳入案例目录/新证据，源码与原配置不拷贝重造；能力基线为现有schema v1/FF-001 r4。 |
| basic02 | 先读target；负值才GET→严格命令→INT；kind=`plc_guard_get_int` | 尚无正式case | 新app模块及`config/basic02.yaml`；只用原Owner.read/Target及Execution。 |
| basic03 | GET→严格命令→正数且不超过100→INT；kind=`get_value_guard_int` | 尚无正式case | 新app模块及`config/basic03.yaml`；额外条件是业务规则，不能放宽原typed输入。 |
| advanced01 | 单PLC多流共读同点、连接复用及独立采样对照 | 底层有相关测试，未有正式教学case | B另批：先冻结无副作用读流的配置/注册与可观察入口，避免假HTTP字段；不宣称缓存共读/原子快照。 |
| advanced02 | 单PLC多DB/多点条件 | 无正式case；FF-004是候选能力 | B另批：各目标语言真实多点配置/API/夹具及逐点失败语义可用，不能仅凭Rust草案推及Python。 |
| advanced03 | 多PLC独立推进/慢设备隔离 | 原配置可列多PLC，教学接线/夹具未交付 | B另批：真实多owner注入/跨设备调用及独立合成服务；不先实现FF-004。 |
| advanced04 | S7+Modbus混合 | Modbus通信不存在 | B另批：协议adapter/类型/Unit寻址/会话期限/unknown及独立oracle均有适当证据；格式校验不是通信验收。 |
| advanced05 | PLC多点条件→HTTP POST | POST/可靠事件投递不存在 | B另批：稳定event identity、业务确认、重复触发、持久投递及unknown核实合同；不把HTTP200当业务完成。 |
| advanced06 | 故障恢复、原状态重启与正常退出演练 | 底层已有部分测试，未有完整教学case | B另批：复用实际能力、冻结故障/状态/资源验收，不借教学实现新恢复或unknown处置工具。 |

C阶段按可用能力补相同basic/advanced ID，逐项标记`planned / capability_missing / runnable`及实际能力版本/证据。
`runnable`只表示精确候选具备实际可启动/运行证据；DEV自检、独立QA和Human Owner最终验收分别记录，不因A交付或case可运行便自动标为已验收。
当前C#全部planned；未来没有对应能力的case保持不可运行说明，不放伪代码冒充实现。
未来可以拆小Revision，不为“案例齐全”先造所有能力。

## 4. 三个基础案例的精确业务合同（R02）

**basic01**：直接复用原demo01，不修改源码、七键输入、loopback配置或常规人工夹具行为。
说明ready=false是idle，ready=true/value42才交Execution。
案例目录给出明确复用路径及独立运行命令；不另建一份demo01或将teaching01转为第四案例。

**basic02**：一轮读取`flow.target.db_number/byte_offset`的INT；sample.value≥0正常提前返回，不GET、不创建命令、不写PLC。
sample.value<0才进行一次GET、原parser；idle正常返回，合法Intent才交Execution。
读失败传播原错误，不用0/上轮值代替。
采用同一个target作条件与写目标，避免增加读点配置字段。

默认合成DB1 offset0是A5A5，即-23131；首次允许写42后，后续轮次读42并提前返回。
dry_run不改PLC，故后续仍读负值/GET，相同原命令只simulated一次。
这种先读后写是顺序通信，**不是PLC侧原子比较写、工艺互锁或跨点一致快照**；真正互锁仍由PLC/业务合同承担。

**basic03**：一轮GET并先用原parser严格验证；idle结束本轮；合法Intent先判断value≤0则正常提前返回，再判断value>100则正常提前返回，只有1..100交Execution。
不得先把非法/过期输入归为业务false；不得添加配置阈值、修改输入schema或复制另一套解析/执行逻辑。

正反向量：basic01为ready=true/42与严格ready=false；basic02为初始-23131允许、execute后42跳过，纯条件边界补-1/0；basic03为-1/0/1/42/100/101（均先符合七键INT合同），其中1/42/100允许，其余正常跳过。
各语言有独立数据/夹具与新场景，不使用兄弟工程服务；边界纯规则检查不能替代真实CLI正反链路。

`return`只结束本轮，runtime继续按interval调度，不自动停流或积压补跑。
业务false是正常skip；health.running/last_success或Rust Ok不表示工艺完成。
Python可以使用现有result表达guard_false；Rust保持Result<()>，通过真实计数和有界结果报告证明分支，不为了对齐新增持久业务状态/health schema。

## 5. 每案例交付、运行与观察合同（R03–R05）

1. 每工程新增一个`examples/README.md`/`README.zh-CN.md` pair，作为其上层PLAN管理的README-only案例目录；给稳定case ID、目的、能力版本/状态、真实app/config/注册/测试路径。
原demo01明确复用，另两例必须有完整正式app与完整YAML；不以文档大段伪代码代替源码。
2. 每例说明哪些底层方法可用、参数/async返回及主要错误、哪些业务条件/合成值可改、哪些identity/物理target/状态不能随意改。新配置仍为人工可审阅YAML v1；JSON仅作有限报告，不引入PLC JSON、公共schema、DSL、Excel或数据库配置平台。
3. 自身指南含准备→构建/环境→显式init→fixture→dry_run/execute→观察→停止→验证的完整可复制命令。写明cwd、绝对路径、每终端变量、匹配instance、报告/状态目录。必要命令不依赖父/兄弟手册；通用概念可链接自身USER_GUIDE，不重新复制FF-002全文。
4. 手工入口继续使用各自原fixture，正向42可演示三个case；反向/边界由新增有界测试harness调用既有Fixture.command/body完成。
不得假称人工CLI已有value/ready/fault参数或控制面板。
harness调用正式产品CLI及正式配置，不能只直接调用app取得通过。
5. harness在构建/init后才启动合成fixture并一次生成本场景command，立即启动产品；自动验证每case两模式、正反向量、计数/状态/停止，产生有限JSON结果和原输出。
Rust新integration test函数名分别含`basic01_cli/basic02_cli/basic03_cli`，Python测试同名，便于单case筛选；复用原工程fixture而非新服务框架。
6. 预期观察同时列HTTP GET、PLC ReadVar/WriteVar、状态counts与目标值/邻接A5。计数窗口区分准备/产品/停止后独立核验；额外读回不能污染产品会话/计数结论。skip的证据用输入与实际请求/状态，不逐tick持久刷普通false日志，不扩观测平台。
7. 三个case单独启动；同一配置不能把它们并列写同一物理target，既有冲突校验继续拒绝。保持多流独立并发、同流不重叠、每PLC长期会话/有界串行IO；HTTP/timer不占PLC队列/执行位，重复读是独立采样，不是缓存或去重采样。
8. 所有应用写仍经Execution；ready一直true也保留同一原command ID/issued/expires/TTL，不能反复制造新身份或刷新原时间。
unknown保留、禁止盲重发/回读升级confirmed/清库；confirmed仅为协议ACK与本地持久确认，不是机器动作或业务完成。
9. 每个全新教学场景可显式init独立synthetic状态，dry/execute及各语言分库；原场景重启保留原库/配置/身份。不得把换case/kind/flow/库当恢复；新case的效果hash自然不同，不提供跨case/跨语言状态迁移。
10. 正常停止沿现有闭闸/取消/在途分类及默认15秒全局预算；产品、driver、fixture子进程与线程实际wait/join，记录精确PID及端口释放/rebind。强杀/超时/forced cleanup是失败，不能当正常通过；只能处置确切自有PID，不杀端口占用者。

## 6. 配置、接线与兼容（R06）

两份新YAML分别单flow：flow.id为`basic02`或`basic03`，kind如§3；business_name分别为`negative_target_get_to_int`、`positive_bounded_command_to_int`；Rust instance分别为`ff-rust-basic02`、`ff-rust-basic03`，Python分别为`ff-python-basic02`、`ff-python-basic03`。
source仍`demo01-feed`，get_url仍本工程`/demo01/command`，target仍`plc_demo/DB1/16/offset0/INT`，interval=500ms、input_max_age=10000ms，其余沿原loopback有限预算。
HTTP字段在两例均有真实用途，不为纯只读流程强塞字段或重写Flow分型。

Rust只在app/mod声明两模块、config放行两个精确kind、runtime显式match派发；Python在runtime显式import/dispatch，config放行对应kind，basic02由runtime传入其目标已有owner。
app只写一轮条件/步骤，core继续持有会话/队列/调度/状态/退出。
未知kind仍启动前失败，不扫描目录、不增加插件注册平台。
新增case可按现有语言签名最小适配，不改demo01签名与行为。

保留原Flow/Target序列化、Intent hash算法、物理Resource、Execution、owner/driver/HTTP/state/audit实现及所有安全语义。
注册其他kind不能改变demo01旧输入/摘要/状态，原config/loopback.yaml保持字节。
新配置与旧fixture均需被实际产品load，编译/导入不能替代运行配置验收。

FF-002原手册的teaching01精确接线脚本会因kind/dispatch锚点变化而失效；A仅修必要接线锚点、已注册kind事实与新案例入口，继续只在教程副本新增teaching01，并做两语言最小复演。
保留其定位/限制及历史bundle/证据，不将teaching01注册为正式第四例。
P0不修改这些手册。

时间沿原来源Unix毫秒/monotonic语义。新增案例不引入日历字段/时间producer；已知旧JSONL/SQLite日历UTC与根+08合同差异仍如实标记，不宣称整改完成。本r1不触达其生成/存储链路、不迁schema或历史；若实现必须触达，回PM明确新Revision及时间整改边界。

## 7. 精确文件allowlist

正式交付树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；已有大量并行dirty，不得reset/覆盖。
P0总写面只有五文件：PM为`field-flow/plans/FF-005-basic-and-advanced-examples/spec.md`；主协调为`field-flow/PLAN.md`、`field-flow/PLAN.zh-CN.md`、`field-flow/plans/README.md`、`field-flow/plans/README.zh-CN.md`。
导航仅新增draft/下一gate及存在的spec链接，不改其他任务行。
根文档、FF README及全部USER_GUIDE当前不写。

**下表只有精确r1批准后才成为A的写面。** R=`field-flow/field-flow-rust/`，P=`field-flow/field-flow-python/`；花括号是有限枚举，不是目录递归授权。无须修改的文件保持。

| A owner/职责 | 有限文件集合/限制 |
| --- | --- |
| Rust app/接线 | 新`R/src/app/{plc_guard_get_int.rs,get_value_guard_int.rs}`；改`R/src/app/mod.rs`、`R/src/config.rs`、`R/src/runtime.rs`，仅新kind/显式派发，不重构runtime/Flow。 |
| Python app/接线 | 新`P/src/field_flow/app/{plc_guard_get_int.py,get_value_guard_int.py}`；改`P/src/field_flow/{config.py,runtime.py}`，仅上述注册和owner参数；initializer保持无副作用。 |
| 配置/实际验收 | 新`R/config/{basic02.yaml,basic03.yaml}`、`P/config/{basic02.yaml,basic03.yaml}`；新`R/tests/basic_examples.rs`、`P/tests/test_basic_examples.py`，内部有界harness复用自身既有fixture，不修改旧fixture/test/support。 |
| 自身说明/索引 | 新R/P各`examples/{README.md,README.zh-CN.md}`、`config/{README.md,README.zh-CN.md}`；改R/P各`{README.md,README.zh-CN.md,USER_GUIDE.md,USER_GUIDE.zh-CN.md,CODE_INDEX.md}`，只作新入口、实际方法/注册事实及旧teaching01必要兼容。 |
| FF总入口 | `field-flow/{README.md,README.zh-CN.md,USER_GUIDE.md,USER_GUIDE.zh-CN.md}`仅案例入口/真实能力对照，不重写原指南；P0四导航及R/P各`{PLAN.md,PLAN.zh-CN.md,plans/README.md,plans/README.zh-CN.md}`由主协调机械同步唯一bundle状态。根文档仍排除。 |
| 文案 | R/P各`locales/{zh-CN.json,en-US.json}`只在确有新可见文案时对称增加；稳定case/error key不翻译，无新文案则不改locale。 |
| 角色事实/资源 | 获批Development创建本bundle的tasks.md；真实developer_handoff后fresh Verification创建checklist.md；仅真实附件才建evidence/。各执行者可新建独占`/private/tmp/ff-005-r1-<unique>/`存副本/环境/构建/新synthetic状态及报告，记录归属/保留条件。 |

禁止修改demo01源码/loopback、两工程domain/Execution/owner/driver/HTTP/state/audit、Cargo/pyproject/uv清单与锁、.python-version、第三方源码、BUILD、旧测试/fixture、FF-001/002/003/004/ARCH全部bundle。
无C#、DS/AW/DAA/SMA/CA、Backend、frontend、tools、根contracts、shared skills/AGENTS/workflow/角色、真实配置/.env/旧SQLite/历史日志写入。
若最小案例仍需突破上述边界，停该部分并回PM新Revision，不借目录通配扩面。

## 8. 工具链、端口与拟验证命令（R07–R08）

PM使用`aiis`、`project-governance`、`plc-point-mapping`（仅合成标准DB INT/offset合同）。
Development/Verification使用这些，并按实际面加载`rust-runtime`、`code-document-indexer`、`i18n-workflow`；Python遵循AIIS语言中立分层/日志/资源合同，本地执行状态仅消费原API，不套FastAPI/ORM/Celery/Tauri/打包模板。
专门实现及测试由相应实际角色执行，PM只定scope/AC。

A使用现有Rust edition2021/rust-version1.89与Cargo.lock，Python已有CPython3.11、uv及自身uv.lock/.venv；不新增/升级crate或包，不改锁/manifest，不下载解释器、Rust target、编译器/SDK或安装全局工具。
获批后可按冻结锁准备缺失公共依赖到自有环境/cache，缺环境/网络则记具体blocker，不换栈。

仅绑定自身既有loopback三口，逐工程/模式/场景串行：Rust proxy/server/HTTP=`31102/31103/31880`，Python=`32102/32103/32880`。
不新增端口、不用102/wildcard，不依赖DS/Backend/兄弟工程。
冲突即停并报告，不杀占用者或自动换端口。

以下为A获批后的命令合同，当前全部not_run。分别从各工程根运行并输出真实FF_PROJECT/FF_RUN_ROOT，状态/产物在新私有根；Python环境准备在其独立任务副本完成。辅助文本解释器不能冒充项目验证。

```bash
FF_PROJECT=$(pwd -P)
FF_RUN_ROOT=$(mktemp -d /private/tmp/ff-005-r1-XXXXXX)
printf '%s\n' "$FF_PROJECT" "$FF_RUN_ROOT"
```

Rust工程：

```bash
rustfmt --edition 2021 --check src/app/plc_guard_get_int.rs src/app/get_value_guard_int.rs tests/basic_examples.rs
cargo build --locked --release --no-default-features --bin field-flow --target-dir "$FF_RUN_ROOT/product"
cargo build --locked --release --features test-fixture --bin ff-fixture --target-dir "$FF_RUN_ROOT/fixture"
FF005_EVIDENCE_ROOT="$FF_RUN_ROOT/evidence" cargo test --locked --features test-fixture --target-dir "$FF_RUN_ROOT/test" -- --nocapture --test-threads=1
```

Python工程/自身独立副本（先确认已有3.11）：

```bash
uv sync --locked --python 3.11 --no-python-downloads --cache-dir "$FF_RUN_ROOT/uv-cache"
uv run --locked --python 3.11 --no-python-downloads --cache-dir "$FF_RUN_ROOT/uv-cache" python -m compileall -q src tests
FF005_EVIDENCE_ROOT="$FF_RUN_ROOT/evidence" uv run --locked --python 3.11 --no-python-downloads --cache-dir "$FF_RUN_ROOT/uv-cache" pytest -q -s
```

FF005_EVIDENCE_ROOT仅供新增harness选择不存在/空的新证据目录，不改变产品配置或旧测试。
运行中先将新场景状态/路径准备好再生成fixture命令；每场景外层≤45秒含回收，新增case矩阵总≤600秒。
超时保留失败并仅收自有资源，不放大TTL/删除负例取绿。
旧测试仍运行必要安全回归，旧失败证据不抹除。

既有回归测试有硬编码的旧任务临时路径前缀；本轮实际新建的目录按确切路径登记为FF-005测试资源，不凭前缀冒称旧任务证据或清理旧资源。执行前已存在的目录一律保留；不得为改前缀修改旧测试/fixture。新增harness的状态/报告必须归本轮FF005_EVIDENCE_ROOT。

案例指南必须落实相同的手工路径：Rust产品为`$FF_RUN_ROOT/product/release/field-flow`、夹具为`$FF_RUN_ROOT/fixture/release/ff-fixture`；Python为自身`.venv/bin/field-flow`及`.venv/bin/python -m tests.fixtures`。
先各自`state init --synthetic --mode dry_run|execute --state-dir <new-scene/state> --instance-id <对应配置>`，父目录先建；fixture显式`--config <本case.yaml> --evidence-dir <new-fixture-dir>`，再`run --config ... --state-dir ... [--execute]`，最后`state inspect --state-dir ...`。
这里的占位路径在交付指南必须替换为可赋值的真实变量和逐步完整命令。

手工10秒input_max_age窗口：先build/sync/init、准备好第二终端，再起fixture立即运行；dry/execute分两个新场景，不在一个窗口内串做。
Rust原CLI无fixture_ready，按自身listener/PID确认；Python有fixture_ready。
harness直接管理Fixture对象、生成一次命令后及时run，不虚构Rust已就绪事件，不刷新同ID源时间。

分终端时显式复制真实绝对路径，记录PID的shell负责wait与后续检查；Rust fixture用ENTER，Python向其确切PID发SIGINT/TERM，返回后在所属shell立即记录退出码。
真实正常退出后inspect、报告、精确PID、线程/子进程join及端口rebind齐备才通过；非法/空PID、权限错误不能当不存在。

每工程独立复制验证只含自身source/manifest/lock/config/locales/tests/docs，排除环境、target、状态、日志和真实配置。
使用自身新环境/target/state/fixture完成必要构建及case运行；正式交付树、候选、复制品源码hash一致，正式启动入口实际核对。
不能把有效变更只留临时副本，或以副本结果代替交付一致性。

## 9. A的逐案例验收矩阵

下面每项均为将来A必须完成的FF-005自身验收；P0只静态审稿，不创建QA文件。计数指产品窗口，停止后独立核验单列；`state counts为空`指没有创建command记录，不代表未打开本场景状态库。

| AC/需求 | 必须观察的结果（Rust/Python各自） |
| --- | --- |
| AC01 / R01,R07 | 精确r1身份/批准链与未来阶段诚实；正式树/独立单工程副本锁定构建、实际非零数量测试、启动成立，清单/锁与受保护源未变，无父/兄弟/DS/Backend运行依赖。 |
| AC02 / R02,R06 | 三case真实注册/配置可load；只有两个新增kind，未知kind/非法目标/重叠写仍拒绝。旧demo01源码/loopback、七键解析、Flow/Intent摘要算法及状态/owner/driver/执行安全实现原字节不变，必要既有回归通过。 |
| AC03 basic01 | 新场景合法42：dry为simulated1/WriteVar0，execute为confirmed1/WriteVar1且目标002a、邻接14字节A5；同原身份至少10次GET/轮次不增加写。严格ready=false另场景GET>0、command0/写0，非错误。 |
| AC04 basic02 | 初始A5A5负数真实ReadVar后才GET；execute首次GET1/WriteVar1/confirmed1，随后至少10轮读42，GET/写/command不再增加。dry至少10轮独立读/GET，simulated1/写0且仍A5；-1/0条件边界有明确结果，读错误不替旧值。 |
| AC05 basic03 | -1/0/101合法命令正常skip：GET>0、command0/WriteVar0；1/42/100各独立场景dry simulated1/写0，execute confirmed1/写1且精确INT值、邻接A5不变。42同ID至少10轮仍仅一次执行；不靠换ID消除重复。 |
| AC06 / R02,R04 | 新case各有ready=false及至少一种typed非法/过期输入验证：零新增写；非法/过期是原错误而非guard_false。business false只结束本轮、后续轮次继续，错误计数不因普通skip增长，不以Ok/health.running宣称工艺完成。 |
| AC07 / R03,R05 | 所有写可追溯到Execution；原命令身份/时间不刷新，旧TTL/ACK/unknown/时钟/排队安全回归仍过。新kind不提供旁路或自动unknown处置；basic02写后guard_false不能掩盖已有unknown，原库/未决状态仍保留并显示。 |
| AC08 / R04,R06 | 新case一轮无循环/自建连接/SQL/重试；显式使用目标既有owner。原并发/同流不重叠/每PLC串行/慢HTTP不占IO位回归成立；计数报告不把独立读说成共享采样、条件读写不说成原子互锁。 |
| AC09 / R03,R08 | 两工程各自examples双语pair具备逐case源码/配置/入口/准备/两模式/观察/停止/失败/可修改点；人工入口实际可照做，反向向量用正式CLI有限harness；不依赖猜测变量/不存在参数/FF-004 API。 |
| AC10 / R06 | 两语言旧teaching01教程经最小锚点修正后在独立副本仍可接线、编译/导入并各跑一次dry/execute；正式产品不注册teaching01。FF-002历史三文件/原证据及FF-004 r1完整hash不变。 |
| AC11 / R05,R08 | 每个新场景正常stop为产品/fixture退出0，任务/线程/child真wait/join，原精确PID不在、各三口实际释放/rebind；每case≤45秒场景与总600秒上限成立。强制清理如实失败，空cwd帮助零副作用，init拒覆盖、run不建schema、inspect只读。 |
| AC12 / 全文 | tasks记录逐AC真实命令/cwd/版本/退出码/失败/candidate/资源，新的fresh-context Verification独立checklist/verdict；关键证据持久、不提交SQLite/环境/产物/秘密。qa_passed仅进入Owner终验，B/C/平台/现场/长稳/部署无资格外推。 |

## 10. 风险、回退与后续gate

| 风险/取舍 | 处理 |
| --- | --- |
| 为教学引入配置引擎/假API | 两个新case均有GET用途，沿原完整Flow；无纯读分型、JSON加载、POST/新协议。未来point-id版本须该语言对应能力真实可用后另批升级。 |
| 条件跳过看似无事发生或被当异常 | 用输入/GET/ReadVar/WriteVar/状态有限报告证明；普通false不刷日志，不把运行健康当业务完成。 |
| 先读后写被用于现场互锁 | 明示采样时刻和非原子边界；Execution幂等/TTL/unknown继续独立生效，案例不授予实际设备动作。 |
| 固定42/10秒窗口掩盖反向条件或鼓励重置 | 反向由自有有限harness生成；先准备后fixture，原ID/时间不变。新教学不是旧场景恢复，不删库/清历史。 |
| A改变原教程锚点或误碰并行dirty | 精确有限接线/文档兼容及hash/diff审计；旧bundle完整保护，禁止整树格式化、reset或修历史checker。 |

回退仅规划本任务归属diff：先停writer/核对pending、in_flight、unknown、confirmed并保留原库/日志/身份，再由明确授权决定恢复本任务源码/配置差异；不得反写PLC或覆盖他人修改。
新增case与旧case语义/身份不同，不能自动切换充当恢复。
本r1无schema迁移、状态互换或部署回滚权限。

排除新类型/协议/POST/auth、自动注册/GUI/DSL、进阶实现、C#、DS导出/联调、业务API、真实PLC/第三方HTTP/数据库、历史时间/状态迁移、Windows/Linux移植、现场托管/容量/长稳、服务/安装器/发布/部署、Git/GitHub和跨chat动作。
当前P0不准备依赖、不编译/执行源码或测试、不建状态库/监听器。
底层缺口超出allowlist则回PM新Revision；不能降低必需AC当deferred。

Development交接必须列所有自建临时资源/用途/确切路径和证据依赖。QA只核验，不修实现或清资源。Owner终验后active coordinator核对归属、占用和后续依赖再回收自有临时物；关键结论先持久化，不操作旧任务资源。

## 11. 批准记录与PM handoff

| 日期 | Revision/真实阶段 | 下一gate |
| --- | --- | --- |
| 2026-11-04（Asia/Shanghai） | 实际命名PM形成FF-005 r1 draft；仅P0授权，无新r1实施批准、DEV完成、独立QA或Owner终验 | 主协调提交本路径/SHA256及A范围，等待Human Owner对精确r1决定。 |
| 2026-11-04（Asia/Shanghai） | Human Owner在精确FF-005 r1交付后紧邻回复“批准”；按上下文批准原审稿SHA256=`fa4d1daab23c8b810da2696a51b618c957843baf9db7dac4999a959b10c8a8dc`的首切片A，Status登记为owner_approved；原draft记录及范围保持 | 主协调实际调用Development实施A并创建tasks；真实developer_handoff后另启fresh-context Verification，Owner终验仍待。 |

**PM -> Development 当前交接：** 精确FF-005 r1的A范围已获Human Owner批准。由主协调实际选择`development`，读取本spec及当前完整bundle，按原三个基础case、§7有限allowlist、R01–R08及AC01–AC12实施、自检并创建/维护tasks；真实developer_handoff后另启`verification`（fork_turns="none"），独立形成checklist/verdict。PM本次只登记批准，不写导航/tasks/checklist/源码，不执行项目；以下原PM审阅请求及起草记录保留，不覆盖本当前交接。

**PM -> Human Owner：** 请审阅精确FF-005 r1的三个基础case（一个复用、两个新增）、必要kind/显式dispatch、YAML v1/既有方法/无新依赖边界、§7有限allowlist、自有loopback有界验证、AC01–AC12及B/C独立gate。
批准后仅进入A，FF-004 r1不变。

精确批准后主协调实际调用development创建tasks、实施A与必要自检；真实developer_handoff后另启verification（fork_turns="none"），以approved spec、完整bundle、正式树/diff/锁/真实输出独立形成checklist。
其后仍由Human Owner最终验收。
范围/allowlist/验收/风险/模式实质变化回PM新Revision及重新批准。

本profile为contract_only，主会话、bundle与diff审计是必要控制，不宣称平台ACL、强制路由或团队自动激活。
P0静态自检及最终SHA256在handoff报告中给出；它不是DEV自检、运行验证、独立QA或全仓治理通过。
不得为已知旧checker诊断改写历史任务或提前创建tasks/checklist。
