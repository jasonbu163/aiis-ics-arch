Task ID: FF-004
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Development rework2 -> new fresh-context QA3 / Verification; exact r2 A candidate frozen after navigation/document fingerprint sync; Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 每PLC独立JSON合同、Rust首切片的S7 int16目录加载与多PLC点位调用、Modbus结构校验及DS导出边界
Owner: Field Flow
Acceptance Chain Reference: FF-004 r2 exact A scope approval -> Development -> fresh-context QA / Verification -> Human Owner final acceptance

# FF-004 r2 A Development

批准：Human Owner于2026-11-04明确批准FF-004 r2 A；当前spec SHA256=a7418cfe8f34515719beb50d9d901f42d7a283e2b33c61a2a57b129104a7870e。实际Development为`/root/ff004_development_r2`，由协调者用development角色启动；读取`.codex/agents/development.toml`仅证明配置，不把其model/effort值当独立运行遥测。唯一协调者保留通知window。

正式树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD基线8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b；并行dirty保留。协调基线`/private/tmp/ff-004-r2-coordinator-6ejzumcp/baseline.json`提供808个FF既有文件hash/38实现文件枚举和12导航清单；12导航由协调者同步。

独占资源根：`/private/tmp/ff-004-r2-dev-IVyzcc`。本任务build/copy/状态/报告均归该根；旧回归硬编码新增目录另按差集登记，不清理未知资源。证据持久写本bundle真实附件，临时资源保留至独立QA/Owner终验后协调者核依赖回收。无Git动作/真实PLC/真实DB/API/DS改动；Python not_run。

环境：rustc1.89.0(29483883e)、cargo1.89.0(c24e10642)、Apple clang17.0.0、Darwin24.6 arm64；现有Cargo锁与清单冻结。优先locked/offline。

实施顺序：
1. R01–05/AC02–04：严格JSON/YAML v2、版本装配与只读validate；验证负例/零副作用和v1兼容。
2. R06–07/AC05–10：只读句柄/单轮app/有界观察接线，复用原Owner和Execution；验证真实CLI/协议/状态。
3. R10/AC01、11–14：新catalog夹具/串行矩阵、完整旧回归、独立copy和双语教程复演；真实资源关闭/源码hash后交接。

所有检查目前pending；此文是Development事实面，不含QA verdict或Owner终验。

## Development checkpoint 1（实施中，非handoff）

实际命令cwd除特别注明均为正式Rust工程。全部输出归独占资源根`D=/private/tmp/ff-004-r2-dev-IVyzcc`：

| 命令/结果 | 真实输出与限制 |
| --- | --- |
| `cargo check --locked --offline --target-dir D/test`（首轮由仓库根以--manifest-path指定自身清单）exit0 | `check-1.txt`，27.30s；仅编译检查，无协议结论。 |
| 同命令加`--features test-fixture` exit0 | `check-2.txt`，1.68s。 |
| `cargo build --locked --offline --release --no-default-features --bin field-flow --target-dir D/product` exit0 | `product-build-1.txt`，122s，普通产品与fixture构建分开。后续源码变化仍需最终增量重建。 |
| `cargo build --locked --offline --release --features test-fixture --bin ff-fixture --target-dir D/fixture` exit0 | `fixture-build-1.txt`，57.37s；此首次构建先于fixture blocking修正，不能作为最终候选运行证据。 |
| `cargo test --locked --offline --features test-fixture --target-dir D/test --no-run` 两轮exit0 | `test-build-1.txt`、`test-build-2.txt`，第二轮4.46s，含全部旧/新测试编译；旧support未用项warning保留，不修改旧测试。 |
| 新catalog四test目标的首轮实际运行exit101 | `catalog-first.txt`：sandbox固定五口bind被PermissionDenied拒绝，两个兼容性函数未进入协议；不记产品通过或端口冲突。随后工具取得本规格已批准loopback执行权限，未改端口/杀占用者。 |
| 取得权限后的第二轮exit101 | `catalog-second.txt`：新fixture在macOS accept继承nonblocking，COTP后等待Setup时返回WouldBlock并关闭，导致两个原driver连接重置；产品/fixture均真实回收。原driver/owner未改，已在新fixture显式set_nonblocking(false)修正。 |
| 第三轮exit101 | `catalog-third.txt`：辅助文本编辑误用Rust cwd下仓库相对路径、FileNotFoundError，测试因此仍是修正前fixture，保留失败；不是新的产品缺陷。之后按正式路径落修正。 |
| 第四轮exit101（部分通过） | `catalog-fourth.txt`：旧typed/confirmed续跑及in_flight→unknown两函数通过8.33s；Modbus preflight通过；三flow服务身份/connecting检查通过。CLI dry通过，execute已写1/confirmed1，但5秒汇总恰逢新轮in_progress，harness等待complete超时。协议完整读轮已存在，未调整采样/TTL/原producer；新harness改为同时核原始完整读轮与实际CLI五秒汇总。 |
| 第五轮exit101（部分通过） | `catalog-fifth-project.txt`：兼容2/Modbus1/服务身份1继续通过；CLI dry/execute各自通过、写0/1和邻A5成立。三读流CLI汇总分行写入时harness看到首行便继续，其他两行还未读到；改为逐条件等待三flow各≥20，不以sleep作为通过条件。 |
| 辅助cwd调用两次exit101 | `catalog-fifth.txt`为仓库根无Cargo.toml；`catalog-sixth.txt`由--manifest-path运行但cwd仍仓库根，旧相对config读取失败。均不算项目验收；之后测试统一显式cwd=Rust工程。 |

新增源码已按指定rustfmt仅格式化新文件；catalog588行、runtime_v2 331行、fixture459行。catalog负责有限闭合DTO验证/严格解析，超过500行已作结构评审：同一配置责任、无IO运行循环/平台抽象；受§3有限小模块限制，不擅增第六文件或重构旧owner。最终还需静态检查与本任务局部diff审计。

当前第七轮只运行新multi_plc/plc_catalog目标，尚在执行；全套旧回归、独立copy、教学手动路径、双语/最大边界最终证据仍pending。所有已失败报告和原输出保留，不将局部通过写成整体通过。

## Development checkpoint 2（仍实施中）

- 第七轮`catalog-seventh.txt` exit0：multi_plc的2个函数（含7个CLI scene与一个服务身份场景）46.87s；plc_catalog的2函数0.15s。新normal scene均exit0/零forced、五口rebind；B-off单列exit1，forced owner_backoff归B，A正常回收。最大ID/计数/16项的4块实际Audit行均≤4096B。该轮不是最终全范围验收。
- 第一轮完整Rust：`FF004_EVIDENCE_ROOT=D/full-catalog-1 FF005_EVIDENCE_ROOT=D/full-legacy-basic-1 cargo test --locked --offline --features test-fixture --target-dir D/test -- --nocapture --test-threads=1`，cwd=正式Rust，实际exit0（已取回session完成码）；`full-1.txt`记录29个非零test项=受保护21（原18+FF005三个函数/37CLI场景）+新8个函数。所有旧测试原字节保留；原故障向量与本新正常场景分开。
- 正式产品增量无feature locked/offline release `product-build-2.txt` exit0/16.60s；独立74文件单Rust copy位于`D/copy`，使用自身manifest/lock/source/config/locale/tests/docs，无兄弟/父runtime；自身无feature release `copy-product-build-1.txt` exit0/60s。`copy-initial-hashes.json`保留复制时指纹；此后新fixture/test/文档增强须最终同步并重建，当前不冒称最终candidate一致。
- 第一轮全量通过后增强必要边界：新fixture启动ready改为有界3秒；仅新catalog模块增加有限单次截断ACK，证明实际写42后unknown在重启/读回42后不确认、不再写；S5追加同原body的真实CLI语义变更identity_conflict；Modbus preflight库改为原State API形成合法in_flight，验证拒绝连恢复写都没有；容量/禁用/越权/DS来源形状等负例补齐；空round尚未开始时不输出伪造空状态。未改受保护driver/Execution/旧测试。
- 第二轮完整Rust已用新`D/full-catalog-2`与`D/full-legacy-basic-2`实际启动，输出`full-2.txt`，完成码pending。源码冻结待反馈；接下来只补双语/静态和自有副本/教程/真实手动入口验证。

本次DS来源向量仅合成结构声明（synthetic-shape-only及零hash占位），不作真实DS导出成功或来源真值证明。Python本轮仍not_run。

## Development checkpoint 3（最终候选检查中）

- `full-2.txt`实际exit101，停于catalog_compatibility：新增截断ACK/真实写42→unknown→原库restart→读42不解除unknown及CLI语义变更identity_conflict已通过；原State API形成in_flight的场景仍用CLI五秒完整轮条件，恰遇in_progress超时。统一改为原始有序完整读轮+实际CLI阻写/汇总证据，不改产品五秒节奏/原TTL。
- `full-3.txt`实际exit0：30项=受保护21+新9，新增catalog_compatibility3（含读42保留unknown）、multi_plc3、plc_catalog2、modbus_catalog1。每个旧组及doc组均完成。scope审计exit0/unexpected=[]，spec/FF005/3隐藏保护文件不变。
- 正式无feature release及独立fixture双终端手册复演`manual-formal.txt` exit0：dry10.602s/simulated1/写0，execute5.494s/confirmed1/A写1B0。两个A/B分别赋真实路径，A一次issue/空行关闭，B持有自己的$!/SIGINT/wait，产品/fixture/A/B正常0，实际精确PID消失/五口rebind。每scene报告位于`D/manual-formal/manual-report.json`，按手册literal poll/stop块执行；有限辅助同步不刷新原body时间。
- `static.json`：135本地链接、6双语pair、USER_GUIDE各33代码块及BUILD各1块完全对应、locale键4项对称，无失败；`git diff --check`本范围exit0。teaching01已从现英文指南逐字提取完整Rust/YAML/精确断言脚本到独立`D/teaching`，接线exit0，产品/fixture各locked/offline release构建exit0（121/120秒）；尚待实际两模式复演。
- 收尾静态核对发现同组S7非默认TSAP加Modbus时，应优先报整组unsupported_protocol。已仅在Loaded.capability增加该有限优先判断并补向量；这是原AC04，不改变合同/allowlist。最终`full-4.txt`已开始全量重验，产品/副本/教学与fixture已增量重建，最终candidate以本次结果及后续封存为准。

## 最终 Development self-check 与 developer_handoff（r2 A）

**当前权威交接：Development -> 新的fresh-context Verification，`developer_handoff`；不是QA verdict或Human Owner终验。** 工作树仍为本节开头正式树/HEAD，无commit/push/Git refs。批准spec保持SHA256=`a7418cfe8f34515719beb50d9d901f42d7a283e2b33c61a2a57b129104a7870e`。源码已冻结；此后只有主协调12导航机械同步及本节所述副本/文档hash封存。精确最终tasks/候选hash由附件`handoff.json`在导航同步后生成，避免将本文件自身hash写入自身造成循环。

### 实际实现面

38件实施allowlist中实际变更37件；未使用`src/lib.rs`写面。完整逐文件hash/changed_files见[implementation-manifest.json](evidence/r2-development/implementation-manifest.json)，相对协调者原dirty基线的真实逐字节diff见[implementation-diff.patch](evidence/r2-development/implementation-diff.patch)。不是相对HEAD把FF-005既有dirty归本任务。

- 配置：`config/catalog.rs`严格有限JSON/来源/协议/点声明，`config/runtime_v2.rs`版本装配、旧typed规范化与只读validate；现有config.rs仅声明两个子模块，原Config/Flow/Target/Plc/Http定义/序列化/validate及公开签名保留。
- 只读：`services/devices.rs`绑定flow依赖子集与enabled点，单轮`app/read_points.rs`；`runtime/catalog.rs`负责独立读流与有限五秒分块。原Runtime只加有限观察容器/接线，旧owner/driver/Execution/HTTP/state算法保持。新received_at来自原Owner.sampled_at_ms的真实响应完成时刻，统一转换+08；observed_at为真实汇总时刻，旧UTC producer/schema保持。
- CLI/夹具：commands先完整Loaded/capability再State.open；单文件/主配置validate输出稳定JSON，结构有效但不兼容exit0，run能力错误exit2。新bin分派catalog/private native模式；fixture.rs原主体原字节保留，仅末尾模块声明。catalog fixture固定两PLC/五口/直接种值、严格idle/一次issue、独立raw trace、有限故障/延迟、真实Child.wait/线程join；B观察为Weak，不持有State/owner生命周期。
- 新测试：plc_catalog/multi_plc/catalog_compatibility/modbus_catalog及catalog_support五件；全部既有test/support、FF005三个案例/YAML/app、domain、driver、infrastructure、Execution、清单/锁原字节保持。
- 合成配置/说明：catalog-demo.yaml/三个plcs JSON及双语plcs README；config README增补v2，Rust README/USER_GUIDE/BUILD/CODE_INDEX、locale对称增补；父USER_GUIDE仅版本区分和入口。最终校正旧手册段落明确为v1（包括旧fixture无fixture_ready），新v2教程与旧v1事实不混用；原teaching01锚点未改。

### 最终命令、退出与持久证据

以下cwd均为正式Rust，除明确copy/teaching。`D=/private/tmp/ff-004-r2-dev-IVyzcc`；原始文本保留D供QA/Owner，路径/sha见[raw-output-index.json](evidence/r2-development/raw-output-index.json)，不把二进制/target/SQLite拷入仓库。

| 最终检查 | 真实结果 |
| --- | --- |
| `FF004_EVIDENCE_ROOT=D/full-catalog-final FF005_EVIDENCE_ROOT=D/full-legacy-basic-final cargo test --locked --offline --features test-fixture --target-dir D/test -- --nocapture --test-threads=1` | `full-final.txt`实际exit0（已取回session完成码）；**30个非零test项=受保护21+新增9**；lib/bin/doc的0-case不计。旧basic_examples三个函数内37真实CLI scene保留，不将其混为37 test函数。逐组耗时见[test-summary.json](evidence/r2-development/test-summary.json)。 |
| 新catalog四目标合计 | catalog_compatibility3/4.65s、modbus_catalog1/0.12s、multi_plc3/52.37s、plc_catalog2/0.21s；合计57.35s，低于600s。含11个新CLI scene与2个服务观察scene；每件CLI含回收<45s，两个服务单独真实计时2.334/3.234s，见[timed-services.json](evidence/r2-development/timed-services.json)。 |
| 正式无feature产品与独立feature fixture | `cargo build --locked --offline --release --no-default-features --bin field-flow --target-dir D/product` exit0/25.73s；fixture最终`--features test-fixture --bin ff-fixture --target-dir D/fixture` exit0，最终observer版输出fixture-sealed-build.txt。无feature与测试feature产物分开，普通产品不依赖fixture部署。 |
| 独立copy build/test | D/copy自身74文件、manifest/lock源码与正式相同；无feature release exit0/25.77s，自身feature fixture sealed build exit0；`FF004_EVIDENCE_ROOT=D/copy-test-final cargo test --locked --offline --release --features test-fixture --target-dir D/copy-fixture --test plc_catalog -- --nocapture --test-threads=1` exit0/2项/0.64s。后续只同步导航/文字并更新全部copy hash。 |
| teaching01逐字教程 | D/teaching按原指南完整app/YAML/精确assert脚本接线exit0；自己的无feature/feature release先完整121/120s，最终增量产品25.64s、fixture sealed build exit0；正式树仍拒teaching01。 |
| 最终sealed手工/独立copy/教程 | 串行run_sealed_manuals.py实际exit0，四job（服务计时/正式/copy/teaching）均0；两shell各自真实变量、前台fixture、B的$!/SIGINT/wait、A空行/退出，PID/八口按场景核验。报告见下表和附件；辅助Python只编辑/计时/只读核查，项目行为全部是真Rust二进制。 |
| 静态 | 仅新增11个Rust文件rustfmt --edition2021 --check exit0；本范围git diff --check exit0；135本地链接、6双语pair、指南各33代码块/BUILD各1块对应、locale4键对称无失败，[static.json](evidence/r2-development/static.json)。Mac arm64 otool仅五个系统库，不宣称全静态/跨平台。 |
| 范围保护 | [protected-audit.json](evidence/r2-development/protected-audit.json)：776件非本实施/导航/spec既有文件逐字节相同，另3隐藏保护文件不变；spec匹配已批准hash；FF005 bundle保持。主协调scope audit exit0/unexpected=[]。 |

全部新协议/手工场景串行。首次sandbox bind失败与辅助cwd/编辑错误不算产品pass；完整失败历史见checkpoint1–3，原输出保留。`full-4.txt`本身30项exit0，但**其中slow_setup仅5.32s，未满足AC08八秒量化窗口**；不能拿该轮代替最终AC08。最后`full-final.txt`的slow_setup=8.332s，并额外在A完整响应的原始trace记录真实B Owner=connecting，A完成序号先于B最终Setup/ready；此最后轮替代此前不足，未放宽connect/IO/TTL或改旧driver。

### 逐场景与资源分类

[final-scenes.json](evidence/r2-development/final-scenes.json)及[scenes/](evidence/r2-development/scenes/)保存11报告的精确协议、原body、时间、状态、PID、退出和关闭；其中正常/故障分别记，不把exit0当命令成功。

| scene | 秒（含回收） | 写/状态/资源实际事实 |
| --- | ---: | --- |
| S1 dry | 5.414 | 初始[12,1,56,34]后一次issue；同原body≥10 GET，simulated1，A/B写0，原值/邻A5保持，正常0/真实join。 |
| S1 execute | 5.418 | 同阶段；confirmed1，A写1/B0，只有A.value=42，ready/result/B和邻A5保持，匹配raw ACK/T3，正常0。 |
| S2 three_readers | 5.414 | A147个真实ReadVar、单session；三flow各≥20，另有60个独立原request/flow样本表及generation1；真实FIFO/同PLC单在途，正常0。 |
| S3 B-off | 8.199 | A87/B0 ReadVar、A/B写0；A独立流继续。**预期B bootstrap forced/exit1**，B owner_backoff与child connect错误/PID链单列，A正常reaped且无forced；所有PID消失/五口重绑，不称正常全程或零forced。 |
| S3 slow_setup | 8.332 | 1200ms门上限由A真实完整响应释放，A完成<B最终Setup，服务观察记录当刻B真实connecting、随后ready；A独立推进，正常0/零forced。 |
| S3 parallel_io | 5.410 | A/B各23个ReadVar，独立两owner实际在途区间重叠；各PLC至多1/原单队列，写0、正常0。 |
| S4 slow_http | 8.336 | 真实HTTP进入/1200ms等待/完成期间A读继续；A78个ReadVar、写0，正常0。A原始响应最大间隔及CLI a_only累计成功分别保存，不把总计数当共享采样去重。 |
| S5 confirmed compatibility | 1.731 | v1实际confirmed后原库等价v2≥10轮总写1；原body时间不变、整体age<8s；第三次同原body真实语义变更identity_conflict且原confirmed保留，各次正常0。 |
| S6 State API same / alias | 0.518 / 0.570 | 原合法T1/T2后v2恢复unknown；同身份及point/flow等别名/new command物理重叠拒写，独立读继续，两场写0；schema/trigger/原意图不变，正常资源0不表示命令成功。 |
| S6 actual42 readback | 1.637 | native实际写42一次、有限截断ACK无有效证明，原State=unknown；首协议故障exit1/无forced，原库restart读42仍unknown/阻写且总写1，重启正常资源exit0；未用完整hold_ack取正常关闭证据。 |

最终手册sealed场景均产品/fixture/A/B正常0，所有确切PID在结束时真实消失，各自端口实际重bind；finite issue不刷新原body/time。实际报告保留可定位的产品/fixture路径与产品sha。

| 自身源码/产物 | dry / execute秒 | inspect / wire |
| --- | --- | --- |
| 正式树release | 11.011 / 5.486 | simulated1/A0B0；confirmed1/A1B0；[报告](evidence/r2-development/manual-sealed-formal.json)。 |
| 独立copy release | 10.601 / 10.466 | 同上，来源为copy自身清单/锁/源码；[报告](evidence/r2-development/manual-sealed-copy.json)。 |
| 独立teaching01 release | 2.623 / 2.301 | v1原三口，simulated1/0写、confirmed1/1写；[报告](evidence/r2-development/manual-sealed-teaching.json)。 |

### AC01–AC14 Development映射（仅自检）

| AC | 实际证据/边界 |
| --- | --- |
| AC01 | 正式与74文件copy自身锁定无feature build/实际start成立；正式30项、copy2项非零测试，源码hash一致，清单/锁不变。无父/兄弟/DS运行依赖。 |
| AC02 | plc_catalog/modbus_catalog严格字段/重复key/整数词法/null/UTF/BOM/深度/容量/codec/functions负例；v1三kind/typed定义不变；v2仅demo01/read_points，其他kind拒2。 |
| AC03 | 路径/缺项/重复/穿越/symlink/换cwd、跨DB点ID、地址重叠、disabled/依赖/未引用文件与预算完整preflight；启动摘要冻结实际hash。 |
| AC04 | Modbus format_valid=true/runtime_compatible=false/exit0；未引用/disabled仍整体拒2；含合法in_flight旧合成库/日志前后hash完全不变、无恢复写；非默认TSAP拒2，同组Modbus优先整体unsupported_protocol。 |
| AC05 | S1两模式、独立COTP C1=0100/C2=0101及S7 raw头/参数/DB/offset/长度/PDU-ref/ACK/value断言、直接native种值、全邻A5；旧五INT向量完整回归。 |
| AC06 | 私有绑定devices依赖子集，read_points顺序/首错/不拼旧值；failure快照明确success/error/not_attempted且错误/未尝试无sample；max16/总128静态装配边界，最大ID/计数4块真实Audit≤4096B。 |
| AC07 | S2真实CLI+60独立request/sample表，generation/session复用、raw单PLC在途和跨PLC重叠；原Owner单FIFO/独立flow outer-await算法未改。 |
| AC08 | 最后八秒B-off/slow_setup/slowHTTP场景、A-only成功累计与原始A响应间隔、B真实connecting当刻及A完成<B Setup、HTTP进入/完成内真实A读；各计数/样本/序列分别持久，不将B-off误归正常。 |
| AC09 | 原TTL/queue/clock/started/stop/ACK回归；新normal全实际join/wait/零forced/15秒预算内回收，B-off精确旧故障分类；紧凑/空白/转义context/真实bool/非零退出判定向量通过。旧完整hold_ack限制保留。 |
| AC10 | typed v1/v2 hash/Resource相同、重命名/字段顺序/display/source不新造效果；同原有效body变旧语义真实CLI conflict，DB/offset/size/business原admit冲突保持原行。 |
| AC11 | S5原confirmed续跑；S6合法in_flight恢复unknown、物理别名/new identity阻写；真实42读回不确认/不重发；原schema/trigger不改。 |
| AC12 | 默认dry simulated1/写0，显式execute只有A一次ACK+confirmed；B0写/原body时间不刷新；所有写仍唯一Execution。 |
| AC13 | 中英版本/kind/API/DS saved/selected/loaded/来源/TSAP/缺口说明，真实A/B手册和teaching01双模式复演；locale对称/validate无副作用。Python字节保持且本轮not_run。 |
| AC14 | 精确角色/Revision/dirty基线diff/37文件/命令/失败/逐scene/资源持久；本节真实handoff后协调者另启fresh Verification，Development未创建checklist/QA verdict/Owner接受。 |

### 资源与限制

[resources-final.json](evidence/r2-development/resources-final.json)：本任务已记录的**1144个确切PID当前全部不存在**、无重用/外部占用项；八口lsof各exit1空输出且逐一实际bind/close。所有测试/构建/手工命令已结束；未留下本任务运行进程。旧测试沿用硬编码FF001前缀，在本轮首次完整测试前后按精确目录差集登记334个新路径，不按前缀批删或触碰既有资源。

D约3.6GiB，保留自有copy/teaching、七个target、所有新合成状态/原始输出/失败报告及便利软链接，供fresh QA/Owner复核；C为协调者资源，不代清理。关键结论/报告/diff/hash已入本bundle，不依赖临时路径唯一存在。未删任何自有或他人资源；Owner终验后由active coordinator按占用/归属/证据及后续依赖决定回收，不借终验授权Git/DB/设备动作。

仅macOS arm64 synthetic/固定loopback S7 int16。Python不改不运行；Modbus无通信/codec、C#/DS exporter/公开schema均后续gate；无真实PLC/业务HTTP/DB、Windows/Linux原生、长稳、容量上线、安装/发布/部署或Git动作。旧UTC producer、已有FF005完整hold_ack及Driver bootstrap force故障分类诚实保留。配置主文件/JSON不是跨文件系统原子快照，停止编辑后启动；JSON/source hash不替执行hash。未知结果保持unknown，不提供清库/改ID/读回确认入口。DEV自检不替独立QA或Owner最终验收。

## r2 A rework1（当前，QA1失败历史保留）

2026-11-04，实际fresh Verification QA1真实qa_failed，checklist SHA256=`dc363a4675802ce710d08d10e108562a2efb96e4f6bfacf1dcf50b65e55fa00c`。上文初轮developer_handoff与自检表均为QA1消费的历史候选，不抵消F-QA1-001/002/003。spec仍a7418cfe.../r2 A，38允许文件及14AC不变，不开新PM Revision。当前实际Development继续返工，root独占12导航及通知窗口；不写spec/checklist、无QA verdict或Owner终验。

自有新根`/private/tmp/ff-004-r2-dev-IVyzcc/rework1`；仅复用自身Cargo构建缓存，新合成状态/场景/报告不覆盖初轮。QA1 Q=`/private/tmp/ff-004-r2-qa-vy1d8rsr`只读。完整初轮evidence/r2-development已逐文件hash封存于本轮baseline，整体保持不改；新附件只写evidence/r2-development-rework1。旧tasks原文副本已存自有根，后续保留历史。

返工顺序：1) 复现YAML绕过/误拒及等价controls，最小修复真实scalar边界并增加定向回归；2) 双语指南用真实stdout路径提PID，区分首health演示与S1十次原body验收，实际双shell复演；3) 完整旧/新Rust回归、正式/自身copy锁定构建/启动及必要教程，全部输出结束后生成新准确raw索引；4) 逐文件/资源/保护审计、真实handoff后新的fresh QA2。所有项目行为目前本轮not_run。

### rework1 checkpoint：真实复现与定向结果

- 使用自己原无feature release，复制QA1五个最小输入/两个S7 JSON至R1/repro，只读validate：绕过输入SHA999018...实际0（预期2），合法误拒SHA5de4ed...实际2（预期0）；quoted/no-apostrophe controls分别2/2/0，见R1/repro-before.json。不是只读转述QA。
- F001 source gate只识别真正node起点的quoted scalar，保留plain scalar内部单双引号，并覆盖flow分隔、注释、多行plain/quoted、literal/folded和标准tag属性。serde_yaml仍负责完整YAML语法/语义；原v1解析/三kind/旧typed与锁不变。新增plc_catalog函数核双方向、真实source syntax、serde AST等价controls及alias拒绝前无state副作用。
- 定向`FF004_EVIDENCE_ROOT=R1/targeted cargo test --locked --offline --features test-fixture --target-dir D/test --test plc_catalog -- --nocapture --test-threads=1`实际exit0，3项/0.96s；新增向量报告在targeted/yaml_scalar_boundaries/vectors.json。辅助简化测试文本的第一次exact-anchor未命中（ValueError）未改代码，随后按实际源码修正；一次build cwd误用仓库根exit101保留product-build.txt，不算产品结果。
- 新无feature release增量构建product-build2.txt实际exit0；同五输入同SHA CLI复测repro-after.json全部预期：2/2/2/0/0。没有网络、状态或日志IO。
- F002双语已使用实际$FF_RUN_ROOT/$FF_SCENE.stdout.jsonl，新增逐driver/native PID的可执行ps检查；首health人工路径明确只作演示，不称≥10 GET的S1。S1定量入口使用原catalog_cli_matrix，其实际十次同body条件及原TTL不变。指南代码块中英保持对称，teaching01原锚点不改。
- R1/full.txt的完整旧/新测试已实际启动；正式/copy/teaching自身产品与fixture分别locked/offline增量build，并在R1新建74文件copy与教程副本，不覆盖旧副本/状态。scope rework1 exit0，33初轮附件与QA1 checklist原hash保持。
- 静态辅助脚本初次复用写到了D/static.json便利副本，已从未变的初轮持久static.json恢复原字节；现在使用R1独立脚本/输出。没有改初轮33持久附件或59项原raw文本。F003新索引仅在所有输出生产者结束后创建，不重写旧错误索引。

### rework1 最终 developer_handoff（当前有效）

Development已完成同一已批准r2 A三项返工，交给root实际启动新的fresh-context Verification QA2；QA1的qa_failed/checklist和初轮33附件保持原字节，本节不授予QA verdict或Owner终验。正式树/HEAD仍为原工作树/8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b，无Git动作。源码已冻结，后续仅root机械导航同步和自有copy文档/hash刷新。

相对QA1仅四件实施文件实际变化：`src/config/catalog.rs`、`tests/plc_catalog.rs`、Rust `USER_GUIDE.md`/`USER_GUIDE.zh-CN.md`。父手册、旧v1/driver/owner/domain/Execution/infrastructure/旧tests/清单/锁及任务外dirty保留；没有新增依赖/格式版本/协议或放宽原14AC。旧33附件仍位于evidence/r2-development，本轮只新增[evidence/r2-development-rework1](evidence/r2-development-rework1/)；精确源码diff和保护结果见[rework1-diff.patch](evidence/r2-development-rework1/rework1-diff.patch)、[protection.json](evidence/r2-development-rework1/protection.json)。

| finding / 自检 | 实际修复与验证（DEV self-check） |
| --- | --- |
| F-QA1-001 / AC02 | 同SHA复现绕过999018...由旧actual0到新expected2；合法5de4ed...由旧actual2到新expected0，五原输入/controls全部2/2/2/0/0。[before](evidence/r2-development-rework1/repro-before.json)/[after](evidence/r2-development-rework1/repro-after.json)保留完整SHA/argv语义/输出。node边界source gate不把plain scalar引号当quoted开头，覆盖多行/flow/注释/块scalar；标准!!str保持接受、原custom tag边界不扩大。新[YAML向量](evidence/r2-development-rework1/yaml-source-vectors.json)核source syntax与AST等价，整主配置typed等价、真alias启动前2且不建state。 |
| F-QA1-002 / AC13 | 两指南改为真实$FF_RUN_ROOT/$FF_SCENE.stdout.jsonl，新增可逐字执行PID代码。正式/copy四个B shell都按此代码实际提取两driver+两native PID，ps均1且stdout/stderr空；资源正常退出0。指南明确首health操作演示不是定量S1，提供原catalog_cli_matrix量化入口；本轮完整矩阵S1每模式≥10同body且原TTL内，人工演示GET实际数量单列，不将9称为10。原teaching01精确脚本从新指南再次提取/接线并两模式运行。 |
| F-QA1-003 / AC14 | [旧错误勘误](evidence/r2-development-rework1/qa1-raw-index-correction.json)：初轮旧索引仍0B/空SHA；真正完成文件736B、SHA8f3015b63f4bb099078e9dd0d446b154f70655f13c0e872640b7966da4e0c069。旧索引及QA1不改。所有本轮输出生产者结束后，生成[新raw索引](evidence/r2-development-rework1/raw-output-index.json)，23项逐件重新核对大小/SHA全相同，[验证](evidence/r2-development-rework1/raw-index-verification.json)无不匹配；生成器stdout未重定向进被索引集合。 |

#### 真实命令与退出

R1=`/private/tmp/ff-004-r2-dev-IVyzcc/rework1`，D为原自有父根。除明确copy/teaching，cwd均正式Rust；原始输出保留R1，已结束文件的精确SHA归新索引，永久关键结论/必要复现输入/报告归新附件。复用自身D下target缓存不等于借用旧二进制：以下均由当前源码实际Cargo Compiling并产生新产品/fixture，普通产品和feature fixture分开。

- `cargo build --locked --offline --release --no-default-features --bin field-flow --target-dir D/product`实际exit0/9.57s；正式feature fixture、copy自身产品/fixture、teaching自身产品/fixture均实际exit0（copy/teaching产品29.89/29.74s）。首次根cwd的辅助build101保留，不算产品pass。
- `FF004_EVIDENCE_ROOT=R1/full-catalog FF005_EVIDENCE_ROOT=R1/full-legacy-basic cargo test --locked --offline --features test-fixture --target-dir D/test -- --nocapture --test-threads=1`实际session86459返回**exit0，31项=原21+新10**；0-case lib/bin/doc不计。新catalog四目标57.27s<600s，旧FF005三函数内37CLI保持；[逐组](evidence/r2-development-rework1/test-summary.json)、[11场景秒数/写数/退出](evidence/r2-development-rework1/scenes.json)。正常scene零forced/真实join；B-off仍只归B原bootstrap失败链/exit1，A正常、实际回收，不称全进程正常。
- copy：`FF004_EVIDENCE_ROOT=R1/copy-test cargo test --locked --offline --release --features test-fixture --target-dir D/copy-fixture --test plc_catalog -- --nocapture --test-threads=1`实际exit0，3项/0.75s。自身74文件源码/清单/锁/配置/locale，最终仅导航文字同步后重新hash。
- `python3 R1/run_manuals.py`实际exit0，正式/copy/teaching三个串行job均0；执行的都是各自当前Rust release与fixture。辅助Python仅编排/只读报告，非Field Flow Python验证。每scene<45s，SIGINT/wait、fixture空行/成功Child/线程结束、确切PID及端口重绑均核；新增指南PID代码的实际B stdout保留R1/manual-*/，四场各输出absent_driver_and_native_pids四个正整数。
- rustfmt仅触达两Rust文件check exit0；局部diff --check exit0；135本地链接、6双语pair、GUIDE各35代码块及locale4键对称，无失败，[静态](evidence/r2-development-rework1/static.json)。原teaching01接线锚点和完整代码不变。

| 当前无feature/自身产物复演 | dry / execute秒 | 实际结果/GET边界 |
| --- | --- | --- |
| 正式树 | 10.763 / 10.471 | simulated1/A0B0、confirmed1/A1B0，normal0；人工原body GET=10/9，只作首health演示。[报告](evidence/r2-development-rework1/manual-formal.json)。 |
| 独立copy | 10.639 / 5.602 | 同样状态/写数/normal0；人工原body GET=9/9，不称S1量化通过。[报告](evidence/r2-development-rework1/manual-copy.json)。 |
| 独立teaching01 | 2.669 / 2.359 | 原v1三口，simulated1/写0、confirmed1/写1，normal0；正式源码仍拒teaching01。[报告](evidence/r2-development-rework1/manual-teaching.json)。 |

本轮S1≥10定量证据来自实际完整新矩阵的冻结body条件和CLI/trace/状态，指南另明确提供该原矩阵入口；人工首次health的9 GET不再被混作验收。原命令时间/身份/TTL不刷新或扩大。

#### 范围、资源与下一gate

[本轮资源](evidence/r2-development-rework1/resources-final.json)：318个本轮已记录的确切PID全部不存在，无重用/不明项；八口lsof均1/空，逐一实际bind/close。完整旧harness前后精确目录差集新增76个FF001前缀根，保留清单，不按前缀批删。所有构建/测试/手册进程已结束，无运行自有资源。

R1保留新copy/teaching、状态/报告/脚本/原始失败与绿结果，D缓存与原334路径仍按前轮归属保留；Q1只读。没有清理原始证据/资源，Owner终验后仅由active coordinator核归属/占用/依赖回收。原33附件和QA1 checklist dc363a...严格保持；root scope rework1 exit0，不把根PLAN其他BE并行行归FF004。

AC01/03–12的本轮完整回归与既有独立QA1真实通过事实分开记录，不由Development授予QA2结论。限制仍仅macOS arm64、自有固定loopback S7 int16；Python/C#不运行不修改，Modbus仅校验，DS无导出，旧UTC/schema/driver bootstrap force/完整hold_ack边界保留。无真实PLC/API/DB、安装/迁移/部署/发布/Git写。当前handoff只进入新的fresh Verification，Human Owner终验仍pending。最终tasks/candidate/handoff精确hash由导航同步后新handoff.json固定，不修改初轮附件。

## r2 A rework2（当前；QA1/QA2失败与此前交接均保留）

实际fresh Verification QA2已qa_failed并停止写入，checklist SHA256=`ed3468e0bb68ed9da056d1553a3f1c2468a77a3a57c2fcf3e06b868ec00f01a7`。上文rework1交接为历史候选，不能抵消F-QA2-001/002。当前仍精确已批准r2 A/spec a7418cfe...，38 allowlist/14AC不变，无新PM Revision或Owner gate。实际Development仅返工source YAML gate及已有plc_catalog回归；不改已关闭的指南或旧索引，不写spec/checklist，不授予QA verdict或Owner终验。

新自有根`/private/tmp/ff-004-r2-dev-IVyzcc/rework2`（R2），构建缓存仍仅复用D自有target；新状态/报告不覆盖前两轮。QA2 Q2=/private/tmp/ff-004-r2-qa2-2jnzhw3m只读；两旧证据目录共60附件与当前QA2 checklist逐件封存，新增附件仅evidence/r2-development-rework2。顺序：原候选实际复现六换行及flow quoted-key边界；最小修复并核真实AST/合法等价controls；新普通无feature release黑盒/完整旧新Rust/单Rust copy自身build非零test及实际启动；结束后准确新索引/资源/范围/hash封存交新的fresh QA3。未变指南/teaching/v1/runtime额外手工路径本轮不机械重跑，核字节及已有独立QA2事实，明确历史边界。

### rework2 checkpoint：复现与最小修复

- 自己原无feature产品对24个QA2同SHA输入实际复现：19符合；CR/NEL/LS/PS四alias及flow quoted-key紧邻冒号共5件错误actual0（预期2）。新R2/repro-before.json保留逐argv/输入hash/输出；QA1五向量仍2/2/2/0/0。
- catalog.rs仅将六换行转换到私有扫描视图，原字节仍交原serde_yaml反序列化及摘要；注释/quoted/plain/block行状态识别对应实际parser支持集。flow引号scalar闭合后，冒号可建立合法JSON式value节点边界；plain内部冒号、引号及&/*/!沿原文字语义。
- 新plc_catalog函数比较真实serde_yaml AST、literal/alias展开等价及完整Loaded typed值；六换行覆盖注释、多行plain/quoted、literal/folded/显式缩进。保留标准!!str与customtag边界，真实alias启动前exit2且无state目录。
- targeted.txt首次cargo根cwd错误101；targeted2编译成功但新增辅助多行key输入被真实parser拒绝，3pass/1fail，保留失败。移除该无效自造向量（不修改parser或放宽合同）后，正确Rust cwd targeted3实际exit0、4项/1.07s。两finding原最小输入均保留，不用该无效语法冒充合法绕过。
- 两源码已冻结并复制到新74文件单Rust工程；新普通无feature/feature fixture与自身copy两种产物分别locked/offline实际构建。八固定端口lsof全1空且逐一实际bind/close成功后，R2/full.txt完整旧新Rust串行回归已启动。未触指南/teaching及其既有独立QA2通过事实。

### rework2 checkpoint：当前候选release与完整回归

四份当前源码锁定release构建均实际exit0：正式普通产品125.274s/fixture125.161s，copy自身产品127.083s/fixture126.214s。重用了自有target但本轮确实重新编译锁定native/产品；不借旧二进制证明当前修复。构建尚未结束时一次提前调用after helper实际仍命中旧产品，19/24并assert失败，报告已独立保留R2/repro-premature-build.json；该结果不计当前候选pass。真正取回四构建exit后，repro-after命令实际exit0，24/24同输入SHA、结构化error_key/format_valid/compatibility符合预期，原QA1五输入仍2/2/2/0/0。源文件冻结后无新增修改，当前full.txt完整回归与copy-tests.txt继续运行；未覆写任何旧轮原始输出。

### rework2 最终 developer_handoff（当前有效）

实际Development已完成同一已批准r2 A的F-QA2-001/002返工及DEV自检，交给root启动全新fresh-context Verification QA3。正式树仍`/Users/jason/Desktop/DreamCode/aiis-ics-arch`/HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`；无Git写。当前源文件冻结，相对QA2只改`field-flow/field-flow-rust/src/config/catalog.rs`与`tests/plc_catalog.rs`；原38允许集合/14AC/依赖锁不变。root的12导航同步另记，其他任务dirty不归本任务。

旧QA1/QA2的qa_failed与全部正文、两个旧Development目录共60附件均保持原hash/file set；F-QA1-002/003由独立QA2关闭的事实保留。新证据只在[evidence/r2-development-rework2](evidence/r2-development-rework2/)，本节不改写初轮或rework1通过/失败历史，不授予QA3 verdict或Owner最终验收。

| finding | 实际修复/DEV self-check |
| --- | --- |
| F-QA2-001 / R01/AC02 | 扫描视图对应真实锁定parser支持的LF/CRLF/CR/NEL/LS/PS，注释/多行plain/quoted/literal/folded状态均按该边界处理；真正反序列化和原字节摘要不归一化。六换行无alias合法controls全0，六alias全2/config_yaml_alias。同SHA CR ed6934...从旧0变新2，其余非LF同族同样关闭开发复现。 |
| F-QA2-002 / R01/AC02 | flow mapping quoted scalar闭合后建立合法紧邻冒号的value节点边界，含单双引号key；plain scalar内部冒号/引号/&/*/!继续作为文字。完整947B输入d380c5...从旧0变新2；有空白alias2，flow literal0，block quoted-key有空白alias/literal2/0；block无空白仍由原parser拒绝，不扩为合法语法。 |
| 等价与旧边界 | [88条新向量](evidence/r2-development-rework2/yaml-source-vectors.json)比较真实serde_yaml AST、alias展开与显式literal等价和完整Loaded typed值；多行scalar直接对其各自原始AST核，不假定LS/PS折叠值总等于LF。原QA1五SHA向量仍2/2/2/0/0，标准!!str接受/customtag原schema拒绝；v1三kind、typed旧序列化和原runtime/Execution/driver/state完全未改。 |
| 黑盒 | [before](evidence/r2-development-rework2/repro-before.json)实际19/24，五错误0保留；[after](evidence/r2-development-rework2/repro-after.json)新普通无feature产品实际24/24，输入字节/SHA与before逐件相同，按真实JSON布尔和error_key核对。输入原字节及两PLC JSON均持久附在repro/，未借旧二进制证明修复。 |

#### 真实命令、退出及当前启动

R2=`/private/tmp/ff-004-r2-dev-IVyzcc/rework2`，D为原自有父根；cwd/精确argv/实际退出/单调耗时见[commands.json](evidence/r2-development-rework2/commands.json)。仅系统Python做文本、编排和报告解析，不是Field Flow Python验证。Rust工具链仍1.89.0、锁定依赖/clang17/macOS arm64；全部Cargo `--locked --offline`，未装依赖/SDK/target或改环境。

- 正式Rust：`cargo build --locked --offline --release --no-default-features --bin field-flow --target-dir D/product`及独立`--features test-fixture --bin ff-fixture --target-dir D/fixture`各实际exit0，125.274/125.161s。copy自身同两命令、目标D/copy-product及D/copy-fixture各exit0，127.083/126.214s；自身清单/锁/源码/配置/locale完整74文件，无父/兄弟/DS运行依赖。
- 正式完整：`FF004_EVIDENCE_ROOT=R2/full-catalog FF005_EVIDENCE_ROOT=R2/full-legacy-basic cargo test --locked --offline --features test-fixture --target-dir D/test -- --nocapture --test-threads=1`实际session78700返回**exit0，263.300s含构建，32非零函数=旧21+新11**；旧basic_examples三函数内37 CLI保持，lib/bin/doc零用例不计。新catalog四目标共57.19s<600s，11场均<45s。[逐组](evidence/r2-development-rework2/test-summary.json)/[场景事实](evidence/r2-development-rework2/scenes.json)。
- copy自身：`FF004_EVIDENCE_ROOT=R2/copy-tests cargo test --locked --offline --release --features test-fixture --target-dir D/copy-fixture --test plc_catalog -- --nocapture --test-threads=1`实际exit0，4非零项，含编译4.668s；新88向量及原3项同候选通过。
- `python3 R2/manuals.py`经R2/run.py实际exit0，42.953s；正式/copy各自当前普通产品与feature fixture串行dry/execute。四scene产品/B shell/fixture均0、真实SIGINT/wait/Child成功状态/线程结束、正常零forced、确切PID消失和五口重绑；每scene<45s。正式dry/execute10.753/10.516s、copy10.495/10.582s；分别simulated1/写[A0,B0]、confirmed1/写[A1,B0]。照现有指南块运行仍只作首health操作演示，完整S1≥10原body GET据本轮完整矩阵；不将人工总GET混作post-issue定量窗口。
- rustfmt仅两触达Rust文件check及局部git diff --check均exit0，原README/guide/teaching锚点/锁/runtime与QA2逐字节相同。额外teaching01教程本轮**未重跑**：相关未变字节及QA2真实独立两模式证据作为历史辅证，不冒称当前全量复演。[静态/版本/保护](evidence/r2-development-rework2/static.json)。

失败尝试完整保留：[failed-attempts.json](evidence/r2-development-rework2/failed-attempts.json)及R2原输出，含错误cwd101、无效新增多行key向量导致3pass/1fail、构建未完成而提前验证旧产品的19/24辅助失败；真正后续当前候选通过单列，不覆盖失败。所有生产输出结束后才创建[raw-output-index.json](evidence/r2-development-rework2/raw-output-index.json)，13个完成文件逐件核大小/SHA无不匹配；生成器stdout不重定向入索引集合，guide输入片段明确排除。旧索引及F003历史勘误原样保持。

#### AC01–AC14 Development自检映射（非QA verdict）

| AC | 当前事实与明确边界 |
| --- | --- |
| AC01 | 正式/copy自身锁定产品/fixture分离构建、32+4非零测试及当前release双模式；74文件源码一致，原清单锁不变。 |
| AC02 | 两finding已按同SHA黑盒24/24及88 AST/source/typed向量验证；v1三kind/旧序列化、严格字段/整数/null/容量/协议负例完整回归。 |
| AC03 | 当前plc_catalog/modbus_catalog缺路径/重复/穿越/symlink/错cwd/重叠/disabled/依赖等preflight负例及冻结原字节来源规则保持；无部分启动。 |
| AC04 | 当前Modbus结构validate0但不兼容，run整组拒2/零state恢复与网络；非默认TSAP及优先错误原回归，未改该代码。 |
| AC05 | 当前S1 dry/execute5.411/5.410s，先完整[12,1,56,34]/idle后一次issue，post-issue≥10原body GET，写0/仅A.value42一次，邻A5/原ACK/TSAP断言保持。 |
| AC06 | 最新16/总128、分块≤4/4096B、真实sample/+08时间/首错error/not_attempted当前新服务及最大Audit测试通过；未加永久历史。 |
| AC07 | 当前three_readers5.408s、parallel_io5.419s；原独立request/单PLC串行/跨PLC并行断言通过，Owner/FIFO/outer-await无改。 |
| AC08 | 当前B-off8.211s/slow_setup8.324s/slowHTTP8.330s，原8秒窗口/计数/gap、A完成先于B Setup且B真实connecting、HTTP等待期间A推进断言通过；B-off仍仅原B bootstrap失败分类。 |
| AC09 | 新正常scene真实join/wait/零forced/全局预算/五口回收；B-off产品exit1只由证据精确归B旧bootstrap链，A正常/写0，不称全进程正常。旧故障回归forced与完整hold_ack限制不混作新正常证据。 |
| AC10 | 当前compatibility3函数含旧typed v1/v2 hash/Resource及来源/重命名不造效果、真实语义变更在TTL内conflict保持原行；算法未改。 |
| AC11 | 当前confirmed1.708s、unknown same/alias0.416/0.497s、实42/截断ACK1.617s均通过原断言；最后正常退出不解除unknown，原首次协议故障非零单列；不读回确认/改ID重放或DDL。 |
| AC12 | 完整矩阵及普通release各自dry simulated1/A0B0，execute confirmed1/A1B0；唯一Execution、原body时间/TTL不刷新，B不写。 |
| AC13 | 原QA2关闭的指南/新PID块/teaching事实与未变字节保留；本轮当前catalog正式/copy双模式/PID实际核验，额外teaching未重跑。Python字节保持且not_run；Modbus通信/DS exporter/C#仍无交付。 |
| AC14 | 实际Development角色、唯一r2/spec/HEAD/两文件diff/32+4数量/失败/资源与新准确索引持久；60旧附件/QA2 checklist保护不变。root随后另启fresh QA3，Owner终验pending。 |

#### 资源、限制与下一gate

[resources-final.json](evidence/r2-development-rework2/resources-final.json)：本轮376个已记录的确切PID全部不存在，无存活/复用/不明项；八口lsof各exit1空且逐一实际bind/close成功。所有构建、full/copy tests、正式/copy shell/fixture均实际结束；无自有运行残余。旧harness本轮76个FF001前缀根按运行前后确切目录差集和原输出/PID登记，不按前缀删除。R2新copy、合成状态/报告/raw/脚本以及D自有构建缓存、前两轮资源继续保留供QA3/Owner，未删除任何资源；仅active coordinator在后续gate后核占用/归属/证据及后续依赖决定回收。

范围[scope](evidence/r2-development-rework2/scope.json)/[保护](evidence/r2-development-rework2/protection.json)均保持spec、QA2 checklist及60旧附件原hash；776旧FF文件与3隐藏保护由root范围helper继续守护，unexpected=[]/FF005 bundle不变。当前仅macOS arm64 synthetic固定loopback S7 int16；Python/C#未运行/修改，Modbus仅结构校验、DS无导出，原UTC/schema/driver bootstrap force/完整hold_ack边界保留。无真实PLC/API/DB、安装/迁移/发布/部署/Docker/Git动作；无Owner终验/现场资格外推。

本节为真实developer_handoff：root先机械同步12导航，然后Development只刷新copy相应导航文档与最终文件指纹，不因纯文字同步重跑已通过构建/行为。最终精确tasks/candidate/copy/handoff SHA归本E2的handoff.json；冻结后停止写入，下一步由root实际启动全新fresh-context Verification QA3。
