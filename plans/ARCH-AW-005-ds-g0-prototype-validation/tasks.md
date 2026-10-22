Task ID: ARCH-AW-005
Revision: r5
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: F-r5-003 repair delivered; candidate306a09d5/core34/B0/ordinary/N283-284-286/full original protocol passed DEV; failed N285 and QA1-3 history retained; new fresh QA/Owner pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DS G0 有界技术原型、正式源码交付及有限S7基线
Owner: Automation World
Acceptance Chain Reference: exact ARCH-AW-005 r5 approved 2026-10-21 -> Development -> new fresh-context Verification -> Human Owner final acceptance; r4/r3 stopped and validation histories retained

# ARCH-AW-005 r3 Development

## 1. 批准与边界

Human Owner于2026-10-20明确批准精确r3；来源/原话归spec §1。批准后spec SHA `7ec38de52749257b61cc9eb23db25733cd52d0f82657efa8e88110c741012a81`。按独立S7 PLC模拟器定位，AW是工程归属，不依赖DAA/SMA/Backend运行。G0模块级ManagedS7互操作不等于完整DAA应用S7→SQLite，后者另批，C排除。004完整bundle不改、不倒记新设计/实现验收。

实际Development角色及五skills aiis/project-governance/rust-runtime/plc-point-mapping/code-document-indexer，按跨语言/运行日志与资源基线执行；不引入Tauri/UI/SQLite工程。profile为contract_only，串行角色与diff审计为合同控制，不宣称ACL。主协调负责四根索引、通知与后续fresh Verification；DEV不给QA或Owner结论。

## 2. 计划与检查顺序

1. 完整消费当前根/AW/最近说明、批准spec和角色、固定输入；创建本记录及独立before/hash，保留他任务dirty。
2. 先同步canonical DS设计§2.7与双语DS条目，标004接受快照和005增补效力；只增实际G0源码索引。
3. 正式S建立受限harness及八文件native副本；B0先核61输入、包/源/锁、完整八文件patch/调用图、工具链/构建/ABI/buffer预算，未闭合禁止监听。
4. B0闭合后按W→C→D/X实证，所有case真实记录pass/fail/blocked/not_run/条件N/A，不改阈值/分母，不扩文件/依赖/端口；真正超范围阻断回主协调。
5. T raw逐SHA持久化A、P仅五类索引；核正式source/binary/入口闭环、资源清理和保护范围，形成精确developer_handoff交新的fresh QA。

## 3. 起点及资源

协调1724文件起点与10份before：`/private/tmp/arch-aw-005-r3-refresh-ii4zqye9/execution-coordinator/protected-start.json`。S=`automation-world/device-simulator/g0`；T=`/private/tmp/arch-aw-005-r3-exec`起点不存在；A为spec固定本线程持久证据root，P仅spec五文件。旧005 P0/r1/r2、004及DAA证据不修改。后续实际命令、来源、结果与限制持续追加。

## 4. 2026-10-20 Owner 路线纠正与 r3 行政停点

本节是已发生事实的行政补记，保留上文 r3 起点计划及批准历史。主协调收到 Human Owner 以下两条原话后，明确要求停止 C++ 路线的新增实现、构建及一切协议运行；Development 已执行暂停。以下引文依发生顺序逐字保留，第二条的“保存”为原字：

> 搞什么，为什么ds是用cpp写的？你其实可以直接先复制daa过来，然后把不是ds需求的删掉就好了啊？

> s7服务端不能用rust实现吗？我想保存runtime用rust来搞，如果你引用的snap7库或者组件是c或者别的，这个我不关心。

主协调据此澄清的新路线约束是 **runtime 必须使用 Rust，底层组件语言不限**；DAA 派生壳、Rust 作为唯一 image/六来源/规则/队列/控制 owner、native 仅承载协议属于正在由 PM 拟定的 r4 方向。本节不替代新 Revision 的精确规格或 Human Owner 批准，不据此开展 r4 实现。`revision_required` 表示 r3 执行停点；代码继续须先取得精确新 Revision 的批准。

### 4.1 暂停时已核实事实

- **B0 未 closed**。正式 S 的 native/Rust 编译及无端口 ABI、配置输入诊断已经完成；最终 source-inputs、build/source 交付清单和证据封存尚未完成。这些局部结果不表示完整 B0 通过。
- **19 项 W/C/D/X case 均为 `not_run`**。从未发送 `start` 控制、启动 listener 或发起协议连接。已执行的 server 诊断仅为裸入口帮助、显式无端口 ABI probe，以及显式配置输入后 stdin EOF 的无监听检查；未运行完整 DAA/Tauri/UI/SQLite/Backend 或真实 PLC。
- 暂停安全核对时，`lsof` 对 `127.0.0.1:30102/30103/30104` 的 LISTEN 查询退出码为 **1**，输出为空，未观察到监听。默认 sandbox 的 `ps` 因权限被拒；随后获准的精确只读进程筛选退出码为 **1**，输出为空，未发现 owned G0 进程/PID。这里的退出码 1 表示未匹配，不作为功能失败；无需执行 stop/kill，未终止他人进程。
- 正式 S=`automation-world/device-simulator/g0/` 的 **99 个文件均已落盘并保留**；最新已记录 `native-g0.patch` SHA-256 为 `ad005efefd08a22dabe222fd55605b293254e1eb73778ba055c3b19d78b5c653`。所有实现均为尚未完成完整 G0 验证的中间候选，不能据此称候选 `no_go` 或已通过。
- T=`/private/tmp/arch-aw-005-r3-exec/` 下 `runs/dev-0001/`、`runs/dev-0002/` 及构建、隔离缓存、profile 原件均保留；这两轮包含中间编译与无端口诊断材料，尚未封存。正式源码、T 资源、既有 S/T/A 相关资源以及旧 004 bundle 均未删除、回退或清理。
- P=`plans/ARCH-AW-005-ds-g0-prototype-validation/evidence/` 与 A=`/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r3-evidence/` 在停点时**尚未创建**；不存在已完成的 P 索引或 A 持久封存。`S/source-inputs.json` 亦未生成。
- 停工前发现 **跨语言 clock 原点尚未统一**：C++ `std::chrono::steady_clock` 与 `/usr/bin/python3` 3.9.6 的 `time.monotonic()` 实测原点不同（当次样值约 `622905.187705` 与 `0.009766125`）。当前 runner 的跨语言绝对时间筛选/屏障不能直接比较，该问题尚未修正；不得据此产出可靠的协议时序结论。

### 4.2 保留资源、后续 gate 与本次记录边界

S/T 及未封存证据暂保留，原因是 Owner 路线复审、PM 新 Revision 和后续可追溯审阅仍依赖这些材料。尚无回收授权；由主协调在新路线明确且确认不再承担实现、验证或证据依赖后另行盘点。未重新构建、监听、连接或运行 case，也未为本次行政记录新跑技术/文档检查。

本次仅更新本 `tasks.md` 的状态、Handoff 和本追加节，辅助 receipt 写入主协调指定的 `execution-coordinator/owner-route-review/development-stop-record/`。未改 spec、checklist、S、DS 正文、P、索引、依赖或原始证据。保留 r3 原计划不等于继续执行其未完成步骤。

**当前交接对象是正在拟定 r4 的 PM 与主协调。没有填写 `developer_handoff`，没有 QA 或 Human Owner final verdict，也没有宣称候选通过或 `no_go`。** 后续实现必须等待精确新 Revision 获批。

## 5. r4 实施起点（2026-10-20）

Human Owner逐字批准：“可以，批准 ARCH-AW-005 r4 spec。接着同步 DS 详细设计，从 DAA 派生精简工程，runtime 保持 Rust，底层使用 Snap7，完成 G0 实现、验证和独立核验，形成可供联调的协议基线；DAA–DS 读取至 SQLite 联调另批，阶段 C 暂不开展。”批准后spec SHA `4f1b03ec618bd0a40295bf273339538bc1491f8082380a009449f681ef56c2fc`。r3上述停点事实完整保留，不把旧构建/诊断计作r4通过。

本轮按归档→设计/DAA白名单派生→Rust唯一runtime/native桥→B0/clock→骨架build/native三次启动与只读IPC→原19case→DEV自检/持久证据→developer_handoff顺序实施。B0未闭合不开listener；DAA/CU/core/004与并行006/007保持只读。主协调负责四根索引，后续fresh Verification另行串行启动。Owner明确跳过邮件。

T4=`/private/tmp/arch-aw-005-r4-exec/`；A4=`/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r4-evidence/`。归档命令在修改原S前核37DAA/17CU/99旧S全部原SHA、r3批准spec/tasks/正文/停点与10份诊断，复制到`A4/r3-stop-snapshot/`后逐成员再核SHA；inventory含113成员，旧99源码inventory digest仍为`6fa308482bf4e1d771613b57fec0dfd3be42025817e29f7cf06832c766c211e8`。归档清单排除自身，旧T3原件/构建缓存均保留；此归档只证明旧字节保护，不代表B0/G0通过。

### 5.1 设计/骨架/Rust 与无端口中点事实

canonical DS已同步005 r4：Rust唯一image/六来源/规则/逐item公平/准入预算；Tauri薄壳与Rust headless同库、native只协议/IO/join；共享core及004历史保留。37DAA白名单派生最小骨架、CU17只读复用，6旧C++业务源在113成员持久归档后退役。实际源码索引与D/R/S说明已同步，产品配置SQLite/导入/完整页面仍未实施。

T4/runs/dev-0001记录native/Rust构建/探针和限定tests；dev-0002记录离线前端与首次Tauri构建。native构建曾因上游头将CLOCK_MONOTONIC宏定义为0及本桥局部index名字冲突返回exit2；仅在获批受控文件/桥使用macOS原_CLOCK_MONOTONIC枚举并改名后native build exit0。无端口C probe实际int返回0/37、Tag20/align1/实际offsetof、callbacks104/align8；Rust probe100同源夹点通过。Rust首次两次编译exit101分别为libc缺mach_port_deallocate绑定、Mach packed字段引用；补本地extern及值复制后build exit0。R三个限定test文件共5测exit0，后续源码收口会按最终候选重建/复核，不把中点产物当最终通过。

隔离cache核包SHA后复制冻结548 registry bank；runtime离线锁54 registry、desktop430 registry逐项为该bank子集，未联网/换版。真实ManagedS7五模块/core独立harness已以原driver feature离线重建exit0，原未用符号warning保留，不改DAA。Node22.19.0/pnpm11.11.0已核，owned pnpm-store复制既有cache后离线frozen安装76包、downloaded0；pnpm build及首次tauri build --no-bundle均exit0。native骨架启动尚未执行，协议19case仍not_run。

统一CLOCK_MONOTONIC已覆盖native server IO/lifecycle与Rust；Python runner正改用Rust纳秒/phase窗口与ID关联，独立Python原点只保留elapsed/夹点校准，不直接绝对比较。Rust新增连接/Job/FFI backing另计；Rust/日志基线线程比旧C++路径多，当前联合accepted worker保守上限53用于给固定控制/日志/两个listener/reaper/同时stop线程留11名额，保持全树64硬预算，不改变C16/H4正常profile或推断>16容量。尚未B0 closed，也未启动listener。

### 5.2 r4 B0 当前闭合（协议/原生启动仍未运行）

当前候选180个source成员SHA `6fbd97c874019bf3978368872e00c345f4d8012c519f2fad5c0fff84322dfe68`，role=dev B0入口T4/runs/dev-0006/build-manifest.json。D/source-inputs与P/input/delivery清单形成无环指纹；34 upstream原字节不变、controlled严格8文件差异、2文件桥无业务image/调度器。全部原生/参考/Rust server/probe/真实ManagedS7/desktop实测SHA、file/otool/nm、feature图/锁与真实dep-info均已记录。C/Rust以真实RW五参数签名传packed Tag/有效data指针并回传0/37，Tag20B/align1/offset0/4/8/12/16及callbacks104B/align8/14字段offsetof一致，100同源clock夹点通过。Rust连接352B/Job640B/descriptor64B；协议连接保守上界18420B（含worker8736、thread64、独立函数Answer4096、Q2208及额外Rust/FFI栈/节点额度），固定实例上界66592B；原64KiB/1MiB/4MiB与64线程阈值保持。实际socket buffer/负载/释放尚待wire。

Rust headless/desktop正式树重新build exit0；profile JSON已显式读取验证，headless增加--profile-json，Tauri显式owned profile不变。10项当前C/H无端口诊断按预期退出（合法exit0、0/负/小数/越域exit2），未发start；限定3 test文件5测及新C/Rust ABI/clock复核通过。macOS15.7.7/24G720、arm64、Mac16,12、物理/逻辑CPU10/10、RAM34359738368B、内置SSD已核；SDK26.1/clang17与固定Rust/Node/pnpm，18:07背景load2.63/2.74/2.79。磁盘只读默认sandbox child exit1，精确只读escalation exit0确认SSD，非server失败。

中间cc9db...候选在profile JSON读取/CLI缺口发现后、任何窗口/listener前撤回修正；原始材料持久A4/dev-run-0001，inventory SHA `4c6a49671294bb5730e3e544f1318c051cac3bd171c4b3e1da733e1e67711830`，summary明确superseded_before_any_listener，不计最终或wire通过。dev-0002/0003/0004/0005/0007保留骨架构建（含一次日志退出生命周期编译错误及修复）真实输出，最终重建exit0。补记辅助Python首次因缺UTF-8声明在解析时exit1、未写入；同shell后续prepare exit0使外层命令exit0，不能掩盖前者，已加声明重做。本B0只解除后续执行前置，仍无native窗口/listener/19case或QA/Owner结论。

### 5.3 原生骨架首轮环境停点及无 GUI 静态核对

2026-10-20 18:28 +08，按显式三个DS路径键及owned marker启动当前desktop binary，SHA `e5c6f29214835f8808a6c59a24b3730923fb90b6b3a9b335367314c04b74134e`，owned PID `91699`，诊断run `T4/runs/dev-0008`。默认sandbox下进程仍在stopped装配阶段，stdout仅资源事件，尚无`readonly_ipc`；stderr有hiservices-xpcservice Connection Invalid。CUA首次target inventory明确报告Mac locked、automatic unlock failed，要求用户手动解锁；未尝试绕过锁屏或重复轮询。主协调已向Owner请求解锁，恢复条件为Owner解锁后真实窗口/IPC/正常退出核验。此轮不能计三次骨架成功，协议19case仍全部not_run、从未listener。

默认sandbox `ps`被拒，随后精确owned PID只读escalation成功：ps exit0确认PID91699属于本DS binary；该PID网络lsof、直属子进程pgrep均exit1空，三固定端口LISTEN lsof exit1空。保留该自有停止态进程/日志等待解锁，不触及foreign；若需TERM，仅记中断诊断，不记正常GUI退出。骨架gate未闭合前不执行W/C/D/X。

无GUI依赖文档静态检查`/usr/bin/python3 -B T4/tmp/dev/doc_check.py` exit0：15份责任面Markdown、108相对链接/anchors、27表和围栏/尾空白，三组i18n键对称；docs README pair相对本轮before均仅第16行DS条目变化。原始结果写dev-0008/results.jsonl；本静态检查不代替原生或协议验证。

### 5.4 锁屏环境 needs_input 收尾（非 developer_handoff）

主协调已向Owner提出手动解锁请求，并于本工具边界要求安全结束当前实验、封存后停写。清理前再次以精确PID与当前desktop SHA核归属，仅向owned PID91699发送TERM；约0.0018s后ps无匹配，**未使用KILL**。随后ps/直属子进程pgrep/三固定端口LISTEN lsof均exit1空，清理脚本exit0；没有foreign进程操作。原launcher已退出，无法取得waitpid原退出状态，不伪造exit0；此次TERM只记中断实验，不记正常GUI退出。原生3次可见启动、两个真实只读IPC、正常UI退出均未完成；19case全not_run，fresh QA未启动。

T4/runs/dev-0008的11项raw经正式collect_evidence.py逐SHA复制到A4/dev-run-0008，inventory SHA `4aec3bee41ea494f01d0525fd612cce2a0cbfe1c70089510c17a8e5c1d4fbad3`；含source/build清单、stdout/stderr、原生scaffold、进程/清理和静态核对事实。当前B0 dev-0006的12项raw亦持久A4/dev-run-0006，inventory SHA `296672f171a64d50744e4ac1fc11235618228e55612276a2cd69d1d789fd21ec`。原失败/中间build dev-0002/3/4/5/7已各自原SHA封存；dev-0001撤回历史不改。全部复制命令exit0，P/evidence-index已逐run索引，A目录不可再追加覆盖。

额外已执行的git空白诊断如实保留：tracked responsibility paths `git diff --check` exit0；对179个untracked候选逐text作no-index检查，合计脚本exit1，63个vendor成员出现exit3 CRLF/上游既有空白诊断，均位于固定upstream/controlled副本。没有为“通过”重格式化任何冻结vendor字节，不把这项全量raw检查写成全通过；非vendor无诊断。纯Markdown前述检查exit0。无GUI完整性复核exit0：180 source、8个bin/dylib、288个固定input逐SHA一致；1822起点中的foreign架构文档/四索引/批准登记差异列原始results，不认领不回退。

当前正式候选仍为`6fbd97c874019bf3978368872e00c345f4d8012c519f2fad5c0fff84322dfe68`；精确r4 spec保持`4f1b03ec618bd0a40295bf273339538bc1491f8082380a009449f681ef56c2fc`。本事实面保持implementation_in_progress，由主协调结束当前窗口为needs_input；不是developer_handoff、QA或Owner final verdict，不能称协议baseline已可联调或候选no_go。P目前仅input/delivery/evidence三清单；protocol-baseline/resource-closeout尚未生成终稿，避免填未来结论。

T4的隔离cache/build/profile/raw/helper、D源码与忽略依赖/generated schema、A4全部归档和T3原件保留，供解锁后同r4继续及后续fresh QA；当前无owned运行PID/listener。Tauri曾尝试启动且不排除系统内部启动缓存；未读取/清理未知用户目录，实际WebView路径/三次启动资源仍待成功native阶段核实。恢复条件仅为Owner手动解锁Mac；**同一精确源码/依赖边界不变无需重复批准r4**。新窗口先复核固定输入/候选binary与三端口，按必要权限重新启动当前骨架，完成3次可见窗口/两真实只读IPC/正常退出后才W01–W09→C01–C06→D01/D02/X01/X02。不得覆写已封存run；后续变化另新run并刷新B0/候选指纹。Development现停止写入，待主协调恢复指令。

## 6. r4 解锁后继续（2026-10-20）

Owner逐字恢复：“已解锁，继续 ARCH-AW-005 r4 的原生桌面验证、G0 协议测试和独立核验，形成可供联调的协议基线；DAA–DS 读取至 SQLite 联调另批，阶段 C 暂不开展。”协调新保护基线1910成员位于`execution-coordinator/r4-resume-002/`，旧sealed A run不改。本次继续沿既有skills/角色/批准面；邮件仍跳过。

恢复preflight exit0，180源码、288固定inputs、8bin/dylib及spec/tasks停点SHA全部匹配，source-inputs仍`7cd5a79dc05dde469aa0041e086c95976fc761b86f91a9570410fcef2a9d9e9f`，三固定端口LISTEN lsof exit1空。复用dev-0006 B0/source6fbd97，不重跑无关已通过测试。

21:00前后按精确desktop SHA/显式owned profile并经require_escalated启动dev-0009 cycle1，owned PID53559；当前stderr空，两个真实`readonly_ipc`事件ds_get_bootstrap/ds_get_runtime_snapshot已由WebView触发。CUA实际inventory成功证明锁屏障碍已解除，但listApps不列裸Mach-O；对当前binary绝对路径、进程名aiis-device-simulator、已批准identifier com.aiis.aw.devicesimulator三种已文档getApp入口均返回Invalid app。尚无可视/点击/正常退出证据，不据IPC日志单独称三次骨架gate通过；已向主协调报告工具绑定限制，未新建.app、修改系统权限或改用其他UI自动化。协议仍not_run、从未listener。

### 6.1 no-bundle macOS metadata 普通修正

只读核当前binary无`__TEXT,__info_plist`；固定tauri-codegen2.6.3仅dev模式自动嵌入，而生产no-bundle缺OS身份。tauri2.11.3已reexport锁内embed_plist1.2.2，无新依赖需求。经主协调/PM同scope咨询确认（本会话2026-10-20，PM仅只读意见，不改spec），仅在已批src-tauri/src/main.rs为macOS且not(dev)嵌入固定DS identifier/name/executable/version plist，避免Tauri dev重复嵌入；无.app、注册/签名、权限或依赖变化，原AC31不减。该修正是否解除CUA绑定须新候选实际验证。

旧PID53559精确核归属后TERM，0.059s后ps空，未KILL；原native_cycle launcher确实wait得到child=-15、launcher exit241，清理脚本exit0/端口lsof exit1空，明确不算正常UI退出。dev-0009中间事实和两个真实IPC原证据持久A4/dev-run-0009，11成员inventory SHA `bd857998a442421422d9d08d449c1bd07d2d56512d0b43db0a889eda80eb15fe`。旧6fbd97 B0保留为修正前候选，新metadata编译/正式前端与tauri no-bundle重建记dev-0010/0011，未跑协议。

### 6.2 metadata 修正后的真实绑定结果

正式build_skeleton.py dev-0011离线安装/前端build/tauri build --no-bundle均exit0；dev-0010另保留一次直接Cargo中间编译（含局部custom_protocol cfg，exit0但不作正式启动入口），最终启动只采用正式脚本重建产物。otool确认新binary含`__TEXT,__info_plist`，100同源clock/int/布局probe及正式source/locks/links重新记录，当前B0 dev-0010 closed，source=`5dda0f28444c4a4b1a8dd8e170a0aaa1c5a63ca54b5dd7c90dd2cf5591397522`，desktop SHA=`68b83cce0b9fa6e19d8cc34266d0fc66f38ec3461b7354f0832a36c7092f5acd`。其它业务/原生保护未变，P/input/delivery已刷新，历史索引保留。

随后新dev-0012 cycle1以显式原profile启动owned PID59243，仍default stopped且不监听；CUA清单不含裸app，已知bundle ID及产品名AIIS Device Simulator各一次绑定均Invalid app。元数据修正真实存在但未解决当前CUA接入限制，不能反复猜入口。主协调已收到精确结果并安排必要人工作证；三轮真实可见窗口/标题/语言主题/无DAA菜单/真实IPC/正常退出5s清理不可减少，协议仍全not_run。

### 6.3 正式三轮人工辅助入口与退出客观时限

主协调/PM同scope咨询持久说明：`/private/tmp/arch-aw-005-r3-refresh-ii4zqye9/execution-coordinator/r4-resume-002/native-binding-scope-consultation.md`。按该r4既有验证面，lib.rs仅增加只读desktop_exit_requested起点及desktop_shutdown_joined/pending结果事件；不增加控制IPC、默认start或改变shutdown。正式获批S/scripts/build_skeleton.py新增显式--native-cycles/--b0-run，同role source/bin校SHA后启动三次固定owned native，人工实际操作界面，脚本不合成UI输入。每轮两个真实IPC ready后等待正常退出，wait得到code0、对应shutdown joined、PID/已见children/三固定端口均空才进入下一轮；必要日志缺失即失败，无自动TERM冒充正常退出。

计时由stdlib ctypes实际调用`/usr/lib/libSystem.B.dylib::clock_gettime(6)`，Darwin SDK _CLOCK_MONOTONIC=6且与Python time.CLOCK_MONOTONIC常量核一致；Rust/native clock_id同为darwin-clock-monotonic-ns。保留原始spawn/ready/ExitRequested/joined/wait返回双采样/清理末ns，以清理末ns减Rust ExitRequested作保守≤5s上界，未将Python3.9 time.monotonic绝对值混比。Owner事后回复时间不参与5s计算。

正式dev-0014重建全exit0，当前B0 dev-0013 source=`7d7180bb6293a4c27431151ef6c2122ce5e218369ad4e8703f264af8a43615e2`，desktop SHA=`71f9b9600a555b3e329897655cbf58a640e282863442a90c32a59b0c1da2446a`。dev-0012旧PID59243仅TERM/-15退出、未KILL，不计正常界面退出，已持久A12；A10/A11保留中间构建。当前dev-0015第一轮PID62133两个IPC就绪/端口空，主协调已向Owner发三轮真实窗口/版本/停止态/零连接/无DAA菜单/主题语言/刷新/正常退出请求。必须等三轮客观结果与人工观察确认两者齐全才关闭AC31前置；当前协议从未listener、19case全not_run。

### 6.4 Owner 壳反馈后的只读停点

主协调转述Owner指出原生壳顶栏/中英切换不符合预期，提议保留已有Rust实现并直接由DAA工程改造精简；主协调interrupt当前退出日志修正，要求只读差异/资源交接，等待PM判断同r4纠偏。未将第一轮人工操作记作AC31通过，没有继续三轮或协议。

dev-0015第一轮PID62133实际wait code0、instance_cleanup A/B=true及三对只读IPC；但ExitRequested/desktop_shutdown_joined关键日志缺失，shutdown_upper_ns=null，正式launcher因此clean=false/exit1且未启动cycle2/3。原始processes/scaffold/commands/stdout/stderr仍完整保留T4/runs/dev-0015，未retrofit通过；本轮尚未封存A，不覆盖旧sealed A。Exit fallback修正仅分析，**没有落盘**。

Owner反馈后精确只读ps筛选exit0空，未见owned DS/build/launcher；三固定端口LISTEN lsof exit1空。正式180 source相对B0 dev-0013/source `7d7180bb6293a4c27431151ef6c2122ce5e218369ad4e8703f264af8a43615e2`逐项无delta，**不存在新未B0实现变更**。R/native与全部D/T4/A4/P、旧T3证据保留，未回退、删除或重写。当前19case仍not_run、从未listener、QA未启动。

窄比较仅说明：DS Layout/Topbar/RuntimeStatusCapsule与固定DAA同源，props/events和locale/theme链无静态可证断裂；入口显式CSS顺序同为ElementPlus→CU→宿主。明确装配差异为DS全量ElementPlus注册、App另写且两状态均传StoppedG0、locale初始化忽略navigator、短标签/tooltip变化及DAA业务CSS残留。不得据静态比较断言已找到真实语言失效根因。若协调确认同scope修正，最小候选为已批准的main.ts、App.vue、locales/index.ts、common.json中英pair、styles/app.css六文件直接按冻结DAA派生，只保留DS单概览/两IPC/stopped和ds.*隔离，不复制DAA bootstrap/采集/SQLite/旧IPC；Layout/Topbar等无需为复制而重写。此处只记录建议，尚未实施，spec/checklist/P/索引与实现均未因此修改。

### 6.5 按冻结 DAA 壳纠偏与真正关闭请求观测

主协调/PM确认属于已批准r4普通纠偏，无新Revision：main/App/locales index/双语common/styles六文件直接按冻结DAA适用装配恢复；保留DS单概览/两IPC/stopped及ds.*隔离，未复制DAA采集bootstrap/SQLite/历史/上传或旧IPC。main用同源显式El组件注册，App恢复可维护分层和明确props/events，locale采用DAA模块自动组装、浏览器首选与本地偏好。公共Layout/Topbar/语言主题保持CU复用，仅将DS内部backendStatusText更名ipcStatusText；顶栏分开实际运行态与桌面只读快照，移除伪Backend/重复Stopped标签。中/EN与完整切换提示逐值沿DAA，DS宿主CSS仅留reset/内容grid，无业务selector。simulator/common/navigation双语界面去审批/内部阶段术语，banner只解释本页可查看状态/连接数、无启停/配置操作；范围合同仍归docs/tasks。

退出源码链只读定位：冻结tauri-runtime-wry2.11.3中LoopDestroyed直接映射RunEvent::Exit，而窗口CloseRequested经on_close_requested/Destroyed才到ExitRequested。新增薄壳WindowEvent::CloseRequested只读事件，明确这是用户正常关闭请求起点；Exit fallback另记desktop_exit_fallback，不能冒充UI操作起点。ExitRequested与Exit都记录真实shutdown结果，最终Exit再stop_logs。日志sink存在take之后/finish检查之前入环事件可能遗留的竞态，最小修正为收到finish后再drain已入环事件并join；业务owner/native协议保护未改。正式三轮脚本只接受最早真实CloseRequested/ExitRequested到wait+进程/端口清理末的≤5s保守上界；只有Exit fallback仍失败。本轮引导使用原生窗口正常关闭按钮，未合成UI动作、未增加控制IPC。

A4/dev-run-0015保存旧失败与Owner拒收原证据，inventory SHA `18aa13d8533bd72f664de9a5b526a33f746327b6db58aa2d46f712f185c5064c`（9成员），未倒填pass；A13/A14保留上一候选B0/构建，旧所有sealed raw不改。新dev-0017及0018记录正式前端/vue-tsc/Tauri no-bundle重建exit0，dev-0016独立runtime build exit0；后一次locale可见文案修改后正式0018再次重建，不沿用前一嵌入产物。静态必要核对exit0：三组i18n键对称、common actions逐值与冻结DAA相同、旧Backend prop消除、产品JSON无审批/任务/阶段术语；没有据全量ElementPlus注册差异断言它是已证明的根因。

当前B0 dev-0016 source=`06a5a85261a28a2416521caa036f2f2d1843cb3025fdeeaa44516f31189821f9`，desktop SHA=`86c28e7c9729c44db77bf18ab54e5f2b066dc2ff96de2901452b553e94c638be`；180source/288input与实际bin/新clock/ABI已重录。native controlled/upstream/bridge、真实DAA/client与R owner/policy/image/scheduler/lifecycle均保持先前SHA，R仅logging最终排空改变。当前dev-0019第一轮owned PID72407两真实IPC就绪、三口空，协调已收到ready供Owner实际看并三轮正常关闭。人工作证及客观三轮未齐前不标AC31通过、不运行19wire；当前仍从未listener、QA未启动。

### 6.6 纠偏候选等待人工动作的非终态交接

2026-10-20 21:34 +08附近最新客观状态：dev-0019完成**0轮**，仍第一窗口；owned native PID72407、顺序launcher PID72335/session39727均仍运行。精确ps exit0确认本任务路径；直属children pgrep exit1空，30102/30103/30104 LISTEN lsof exit1空。初始两个真实只读IPC已就绪，尚无关闭请求或退出事件，不能用等待时间或事后回复替代退出5s证据。最近单列骨架采样RSS81838080B、threads18、fd45、Mach ports263；未拿它套独立server C01阈值或宣称WebView资源回收通过。实际本机WebView路径仍未取得，不猜测或清理用户目录。

当前B0/source/binary未改：dev-0016/source `06a5a85261a28a2416521caa036f2f2d1843cb3025fdeeaa44516f31189821f9`、desktop `86c28e7c9729c44db77bf18ab54e5f2b066dc2ff96de2901452b553e94c638be`。A16持久当前B0、A17中间build、A18当前纠偏build均经正式collect逐成员SHA核复制，P已补非终态索引；dev-0019仍活跃，**尚未封存A**，不能把滚动原件复制后标不可变或未来pass。T4 raw/显式profile、A全部sealed历史、正式源码/ignore依赖与旧T3继续保留，当前窗口不因本次收尾TERM。精确live资源事实归`T4/tmp/dev/corrected-shell-needs-input-live.json`。

解除条件：Owner实际查看当前DS窗口，核标题/版本、A/B停止/连接0、无DAA菜单；切中/EN和主题、刷新，然后用正常窗口关闭按钮退出。launcher只有真实CloseRequested/ExitRequested起点、shutdown joined、code0、≤5s且PID/已见children/三口均空后才出下一窗，共三轮；人工观察确认与客观三轮两者齐全才允许后续W/C/D/X，不会自动启动协议。当前仍19case全部not_run、QA未开始、无可联调baseline go/Owner接受结论。协调可以needs_input结束当前窗口，Owner操作完成后同r4新窗口继续，无须重复批准同一范围；Development暂停写入但保留本次owned停止态窗口/顺序launcher供人工操作。

## 7. 原生 gate 实际闭合后进入 G0（2026-10-20）

Owner实际回复“三轮界面与切换均正常，已关闭”，观察人Human Owner；协调原问题覆盖标题/版本、顶栏、中/EN选中与切换、主题、仅DS概览、A/B stopped/连接0、刷新及红色正常关闭。原话与归因文件`execution-coordinator/r4-resume-003/owner-native-observation.json`已引用SHA存入scaffold，不将其写成G0最终接受。Development实际接回session39727得launcher exit0，三轮PID72407/78719/78898均code0/clean=true、真实WindowCloseRequested与shutdown joined、保守清理上界185616000/169756000/175049000ns（均<5s）；再核三PID和launcher72335 ps均exit1空，三固定端口lsof exit1空。180source/288inputs/8bin逐SHA仍与dev0016/source06a5一致，复用B0不重建。

AC31本轮DEV原生前置实际闭合，A4/dev-run-0019已逐SHA封存，P补真实非终态索引；所有旧失败轮次仍保留。此为实际人工观察+客观事件的Development自证，不是fresh QA或Owner协议baseline终验。当前可以按原W→C→D/X顺序开始19case，不向真实设备/数据库/API或完整DAA应用联调；StageC继续排除，邮件仍跳过。

### 7.1 首批真实协议结果与 raw reader 缺证据修正

06a5候选W01在dev20/21/22三次独立进程/fixture重置通过；W02在dev23/24/25三次通过，真实item拒绝及完整DB/image/hash/seq/点来源更新时间不变。dev26 W03完成100轮BOOL竞争且clean退出，但文件4388事件、stdout只1906，故按原判据blocked（非pass），原始差异完整持久A26 inventory `9acbe3b792d3084737f7e3810539e9a23aaadeeec64054c588ad64682c130a16`。旧通过/blocked不重标，也不以文件最终值替代事件完整性。

定位为Python raw reader每条事件open/close记录文件拖慢pipe排空，Rust有界非阻塞stdout在快速竞争时未完整捕获；只在正式run_cases.py改为每reader持有64KiB有界buffer并在close前flush，原stdout/file数量、JSON完整/丢弃判据不减，DS日志/预算/控制不改。新B0 dev27/source `e5ae5a49554ca920820674cf23726bcbc34f230c6da283850193c34d18b61878`；180source仍只该Python脚本不同，8bin/dylib逐SHA与dev16完全相同，所以实际A19原生3轮/Owner观察按相同desktop/runtime/native字节精确引用，不虚构新增人工轮次。

新dev28 W03实测pass，stdout/file均4388且无丢弃、clean退出，验证读取修正有效。按spec确定性向量至少三次独立重置的要求，随后每W case以独立正式runner/fixture进程重复三次；BOOL竞争每次100轮，具体case↔candidate↔run映射最终统一列P，原门槛不降低。当前e5ae候选P1继续执行，不把中点写成19项全通过或QA。

### 7.2 W09异步关联与stdout损失的再次实测

e5ae候选dev29–51完成W01/W02/W04–W08各三次独立运行；W03在dev28/35/36三次通过。dev52 W09因runner在异步accepted事件尚未被消费时索引列表失败（IndexError），原raw/clean退出不改为pass。正式runner改为按reference真实local_port匹配native accepted(instance,peer_port)，再固定该Rust connection ID并等待established；不按最后事件猜测。新B0 dev53/source `de72cde084668adbd069c8106d6e7ce785b2aadd4e24ec2038d4d41f44cd8d1c`，八个binary与dev16相同。dev54 W09实际pass；dev55–60 W01/02各三次pass，dev61/62 W03 pass，dev63 W03完成100轮竞争但stdout4330/file4388，仍blocked/evidence_incomplete，clean退出。全部dev27–63已逐成员SHA持久A对应run，不覆盖失败。

§7.1的reader拖慢为当时初步推断，buffer改善并未消除偶发缺行；不能据此认定完整根因或称所有sink损失已被计数。当前源码核实原logging.rs忽略stdout.write_all返回，stdout实际错误/部分写不具计数。后续最小修正仅该Rust日志适配和正式Python采集器：stdout单次非阻塞write按实际返回统计错误/部分写/丢行及字节，独立file通道记录observability_degraded；普通raw文件直接承接server stdout，tail只消费完整行并在退出后排空，不补造事件。真实非排空pipe单元测试已观察partial和EAGAIN且计数断言通过（dev64 cargo test --lib exit0）。仍须重建Rust server/probe/desktop、新B0及受影响的三轮正常启动/IPC/退出；前端与UI退出路径未改，旧Owner视觉观察只按逐SHA不变项引用。当前不进入长负载、不判19项通过，QA尚未开始。

### 7.3 真实stdout失败计数回归与新B0（22:07）

最小回归在现有logging.rs测试模块实际建非阻塞pipe：1,048,576B请求真实写65,536B，partial_writes1/dropped983,040B；pipe满后实际Sink写189B返回EAGAIN(35)，独立file真实记录observability_degraded(stdout)、write_errors1/dropped_lines1/dropped_bytes189/written0。真实file worker flush/join后读取断言，耗时617,416ns，cargo test --lib -- --nocapture exit0；输出与计数原值记dev64/stdout.txt，原探针file保留T4/tmp/dev/ds-g0-stdout-loss-91298.jsonl。stdout仅单次非阻塞syscall，无重试/owner锁内IO；setup fcntl失败显式返回错误，事件入环及file channel丢弃原计数仍保留。Rust编译器release与正式no-bundle desktop重建exit0；dev65是先前中间build，最终用dev66。

新B0 dev64/source `41611d47448afd78761430092db948eb409f3f9040efc4797fa1522e9b986cd7`，180源码/288固定inputs、8bin清单、100同源clock/真实int callback/ABI/budget复核exit0；connection_upper仍18,420B，native八文件patch/业务owner未改。desktop新SHA `931b1ab402ce6f8eaee8c5233245db92db7c8ffe9c21855aeaba09a81c670b30`。与dev16源逐SHA只差logging.rs和run_cases.py，34项前端/UI/配置/退出路径及CU原字节相同，精确对账dev64/results。依主协调/PM同scope受影响项复测说明，旧A19视觉/语言主题/刷新仅按旧候选身份引用；新二进制仍需三轮真实可见启动/两IPC/正常关闭5s/PID/port实测与Owner确认，不称旧desktop证明新版全部通过。

正式dev67 launcher(session37465)当前cycle1 PID92487，两个只读IPC已ready，stopped/三固定端口无listener，等待Owner连续正常关闭三窗。禁止以超时、TERM或旧人工确认替代本轮；wire尚未在新候选执行。dev64–66已按闭集逐SHA持久A，dev67待真实结束后封存；当前仍implementation_in_progress，无developer_handoff/QA/Owner终验。

### 7.4 新日志候选原生待正常关闭的保留停点（22:11）

主协调已发新版三窗可见/正常红色关闭请求，当前尚无本次Owner确认。正式dev67仍cycle1 ready、completed_normal_cycles=0；实际ps核owned DS PID92487（parent92484）及正式Python3.9 launcher PID92484/session37465均存活，精确binary为新desktop931b1ab4…。固定30102/30103/30104 LISTEN lsof exit1、stdout/stderr空；本实例保持stopped，未开启任何S7 listener。只读行政资源核对exit0，原ps/lsof返回码/原命令写dev67/commands与T4/tmp/dev/native67-wait-resource.json。没有TERM/KILL、OS权限/锁屏更改或新增构建/协议。

为保留Owner可直接完成的具体窗口，T4 dev67 active raw与三轮launcher保持，不封存可变目录/不覆盖A；三轮完成并实际wait退出后再逐成员封存A67。独立stdout失败probe原508B已逐字节复制为dev68/stdout.txt并持久A68（不新增test case），原SHA `eacab7ea09105c1a8e7cd647a0ff190fbeec07f54ad1d9eae40a79cb33a57cb2`；与A64的真实测试exit0/partial/EAGAIN断言输出共同证明，不以正常运行零错误替代失败路径。P保持input/delivery/evidence三类非终态清单，未创建go protocol-baseline或最终resource-closeout。

当前41611d新候选19case均not_run，受日志改动影响的新版三轮启动/两只读IPC/正常退出5s/资源与Owner可见确认齐全前不进入wire；既有e5ae W01–W08、de72 W09实际通过及旧失败/blocked原证据仅保留其精确候选/run身份，不转记为新候选通过。旧A19视觉/语言主题/刷新仅关联未变的34项UI/退出路径/CU配置，主协调/PM受影响项复用说明见execution-coordinator/r4-resume-003/affected-native-retest.md。

主协调可结束本自主窗口为needs_input；tasks仍implementation_in_progress，非developer_handoff/QA/Owner终验、非候选no_go。实现/构建/协议现暂停，不清理D/R/S、T3/T4隔离cache/build/profile/raw/helpers/忽略依赖、全部A历史，它们供同r4恢复与fresh Verification/后续联调依赖。恢复条件是Owner完成当前新三次正常可见关闭且launcher三轮客观clean，届时同一精确r4无需新范围批准；先回接session37465、核source180/inputs288/8bin和三固定端口不变，再记录本次观察人/来源/封存A67并执行原完整矩阵，不降低任何阈值。此停点后Development停止写入，待协调明确恢复。

### 7.5 新日志候选原生gate实际闭合与恢复协议（22:52）

Owner本次原话“ 三个窗口均可见，已正常关闭 ”（引文正文不含两侧排版空格），由主协调持久execution-coordinator/r4-resume-004/owner-native-close-observation.json，观察人为Human Owner；本次仅对应dev67/source41611d/desktop931b1ab4新三窗可见及正常关闭。A19旧主题/语言/刷新观察仍独立只按未变UI来源引用。已真实回接session37465得到launcher exit0；PIDs92487/12083/12110三轮均code0、两真实只读IPC及CloseRequested/ExitRequested/shutdown_joined，clean=true，保守退出上界220,683,000/183,823,000/185,876,000ns。实际ps核launcher92484及三child均exit1空，三固定端口lsof exit1空；180源码/288固定inputs/8bin逐SHA匹配B0dev64。新三轮原生DEV前置现闭合，不替代协议或独立QA。

恢复不改source/依赖/B0、不重复旧UI细项测试；dev67已按闭集封存A67并逐SHA校核。接着当前41611d完整矩阵：W各向量独立重置至少三轮，C01/C02同16sessions及P2原时长/阈值，真实ManagedS7 D01/D02，X01独立重置三轮及X02进程内模型严格N/A。每次保留真实失败/缺证据、同scope修源需新candidate/B0/受影响gate，绝不把历史通过转记当前候选。当前implementation_in_progress，非developer_handoff/QA/终验；邮件继续按Owner要求跳过。

### 7.6 当前候选P1完整DEV结果

source41611d/B0dev64：W03 dev69/70/71；W01 dev72/73/74；W02 dev75/76/77；W04 dev78/79/80；W05 dev81/82/83；W06 dev84/85/86；W07 dev87/88/89；W08 dev90/91/92；W09 dev93/94/95。九case各三次独立正式runner/fixture重置，27次命令均exit0/pass，实际cleanup均clean/evidence_complete、stdout/file条数相同且无降级，完整原始请求/逐item回执/images/点seq来源/日志按case保留。W03每次100轮并发，非降低采样；W09各阶段采用真实关联connectionID，不以未知回执推定未提交。各run逐成员SHA持久A69–95并用正式verify_evidence.verify作JSONL/bytes/hash核验exit0，完整映射写P索引。原失败/blocked历史不变。P2现从dev96执行C01 30s预热+300s测量，C02将沿用同16sessions；尚不将P2/P3、QA或总baseline记为通过。

### 7.7 C01完整诊断与独立资源分类收口

dev96原candidate41611d完成30s预热+300s测量及同16会话C02，runner原summary pass/duration336.005572083s，cleanup clean/exit0/无listener，stdout/file253,466条一致无降级。仍因Python采集器及部分独立客户端资源未统一单列，**该run仅作为协议/DS阈值诊断，不认作最终完整资源验收**，原summary/实际原证据保留A96。为阻止自动进入C03，只对已核T编排helper14527 SIGSTOP（C01 runner15351/server15352继续运行），完整case及server正常退出后才TERM+CONT helper，session21315 exit143；没有中断300s或kill server/case。行政信号原因与结果随原raw保存，不把编排停止伪装成正常case退出。

仅正式run_cases.py补1Hz只读ProcessSampler，按server/reference/managed_s7/observer_sampler分别记录PID/角色、CPU/RSS/threads/实际FD，ManagedS7原Popen/退出及stdout/stderr完整落原raw；server阈值仍用自身完整Mach/CPU/RSS原采样，不把外部client/observer计入DS tree或省略其自身采样。使用系统libproc PROC_PIDTASKINFO4的96B struct、PROC_PIDLISTFDS1实际8B records；首个辅助探针误把CPU ticks当ns而assert exit1，真实值核SDK mach_timebase转换后与getrusage校准exit0。正式sampler每run保留raw ticks、numer/denom及真实own校准；资源时间实际clock_gettime(6)，无Python3.9绝对原点混比。没有跨进程Mach task权限请求，外部样本mach_ports明确null/原因，DS/reference自身原Mach计数保留；不声称未知项为0。live采样错误/未join令evidence_complete失败，不改任何业务提交/负载/阈值。

新B0 dev97/source `1b3f16988c6b410e96ab7b93da01207b5b5c7a48d7bf7f8261f12e39883c2d6e`，180源码/288固定inputs/八binary逐SHA核，唯一源差异为Python runner，8bin与dev64逐字节相同。依据主协调/PM既有受影响面原则精确复用A67/source41611d/desktop931b的新三轮正常可见关闭与本次Owner回复，不重复请求关闭；旧A19主题/语言/刷新仍仅对应34项未变UI来源。100clock/ABI/int/budget静态B0 exit0，A97已封存。完整新矩阵session47194从dev98重新执行，当前W03三独立100轮已pass、observer sampler完整，后续P1/P2/P3按原顺序阈值继续，未判baseline go或QA。

### 7.8 资源分类候选的P1重跑结果

当前1b3f/B0dev97：W03 dev98/99/100；W01 dev101/102/103；W02 dev104/105/106；W04 dev107/108/109；W05 dev110/111/112；W06 dev113/114/115；W07 dev116/117/118；W08 dev119/120/121；W09 dev122/123/124。27命令exit0/pass，cleanup clean/evidence_complete/sampler_complete，实际新独立observer/client/DS角色采样完整；不是继承旧candidate通过。各run已逐成员SHA持久A98–124并正式verify JSONL/bytes/hash exit0。当前dev125执行C01/C02原完整时长，server/reference/observer_sampler实际1Hz分列、暂无采样错误；协议/资源总结果、P3与QA仍pending。

### 7.9 C01/C02与C03实证、C04实际socket缺口诊断

1b3f的dev125完整C01/C02 exit0/pass：9,600请求/345,600B、每连接600次；从raw重新算逐连接p95最大0.394125ms、p99最大1.9195ms，queue p99=0.066ms；A规则due24,000/missed0；DS平均0.0891204单核，RSS采样峰6,717,440B/净-311,296B、线程峰25、FD+Mach峰83。cleanup clean/exit0/无listener、stdout=file253,353，无降级/采样错误；外部server/reference37PID（含20拒绝及replacement）/observer采样分列。短于1秒负例单样本只报告观测值，CPU均值null/不可评估、不称全寿命峰；主协调PM只读澄清收据execution-coordinator/r4-resume-004/pm-short-lived-client-sampling-clarification.json确认此口径符合原R12，不新增lifetime硬门槛。dev125原完整证据A125 inventory b80fa2b1…；dev126 C03原三次握手/半帧期限及30s idle真实pass，A126封存。

C04 dev127实际fail（不是no_go）：真实slow cid9完成533次256B read/281B响应，无send EAGAIN/op3，不能证明发送绝对期限；offered固定sleep(.05)实际约17.7/s，且只在connect前读回8KiB。只在正式runner改绝对20Hz/600cap/最多30s并新增实际SO/TCP_CONNECTION_INFO/FIONREAD逐阶段原值。dev128 B0/source0307677…后dev129仍fail：connect后实际RCVBUF326640/SNDBUF65328，handshake约326600/65328，窗口约326600，未消费字节真实增长，因此原≤16KiB输入根本未成立，不判send通过。

同scope peer收口：dev130/source20fb4c6…连接后重设SO8KiB，dev131实际RCVBUF269504/发送8192仍超界，在业务发送前即fail；dev132/source28f6df…connect前TCP_MAXSEG512被连接过程覆盖，dev133实际MSS16332/缓冲269504而fail；dev134/sourcefab0ed…在connect后再设MSS512，dev135确为512、初始SO8192/handshake16384，41请求后实际RCVBUF24576，严格断言仍fail。所有中间B0/failed run完整封存A127–135、不覆盖、不把buffer不合格场景写pass；native/R/8bin一直未改。

2026-10-20只读Apple公开[XNU tcp_subr.c](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/netinet/tcp_subr.c) tcp_sbrcv_grow_rwin说明应用固定接收缓冲也可能按16×t_maxseg增大；[tcp_usrreq.c](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/netinet/tcp_usrreq.c) TCP_MAXSEG仅设置当前t_maxseg。公开可变main只是诊断线索，不当本机kernel同版证明；实际SO/TCP raw是依据。当前dev136 B0/source `cd7c8173d2fc5debb513094213cda829a56752d252e80ae78ed08b00fd37d839`，peer connect前后标准TCP_MAXSEG256、原SO8KiB读回、绝对20Hz/256B/600cap/30s/2.5s全保持，dev137针对C04实际验证中。另恢复A规则并让同实例健康连接在真实阻塞区间读，原要求的其他连接/规则进度必须有真实trace，不能以注入替代。

只读核C05原已用start+(i+1)*.05绝对F日程及A/B/UI绝对1Hz，不存在已证C04固定sleep偏差，未改C01/C05。当前仅runner方法修正，八binary不变，A67原生三轮和A19 UI细项按已述精确身份复用；稳定后完整最终19原矩阵仍待执行，不把这些历史候选通过转记最终。WebView仅按精确identifier只读stat已观察到/Users/jason/Library/WebKit/com.aiis.aw.devicesimulator/WebsiteData与/Users/jason/Library/Caches/com.aiis.aw.devicesimulator/WebKit，元数据保留A125/results，和显式DS_PROFILE_DIR区分；未推定全部本任务新建/可删除，供QA继续保留。

### 7.10 稳定候选前的慢接收、退出与隔离诊断收口

C04 dev137仍真实fail：MSS256、SO实际峰16,384/8,192B合格，但连接最初广告credit326,600B，600请求/29.954s后未读168,600B仍未零窗口，未触发真实send阻塞。只在owned slow peer用标准TCP_NOOPT(0x08)于connect前禁用窗口扩展、原MSS256/实际SO读回与20Hz/256B/600cap/30s不变；未改native/R/系统网络设置。dev138 B0后dev139实际pass19.316s：初始credit65,535B、SO采样峰16,384/8,192B、FIONREAD65,486B分别保留，真实op3/EAGAIN起点至pthread_join返回2,004.191ms，阻塞区间其他A连接实际回复及A规则进度存在；cleanup clean、日志完整、sampler无错误。原dev127/129/131/133/135/137失败不回填。

主协调取得PM只读方法澄清（execution-coordinator/r4-resume-004/pm-slow-peer-buffer-clarification.json）：原C04的≤16KiB核实际有效SO_RCVBUF/SO_SNDBUF读回，原文未另设FIONREAD/历史广告credit/peer未读队列≤16KiB硬限；65KiB未读必须分列，不能据SO宣称kernel物理内存硬限16KiB。标准peer选项及原负载/期限/端口/native/R/依赖不变属于同r4方法，非新Revision；真实send时间链和DS核心全预算仍必证，该澄清不替代技术通过。资源单样本澄清同样只允许短命负例PID CPU均值null/不可评估，RSS/线程/FD仅称实际采样峰；逐PID角色/起止/退出仍完整，长存活漏采或日志/sampler错误不允许pass（参§7.9）。

只在runner补X01原必证缺口：每次在A单连接close/屏障/stop/rebind期间由独立真实B连接以100ms周期持续读DB57并逐次保存wire、连接ID、结果；不是新增产品功能。dev140/source42530cfb…后dev141 C05 pass77.276s：60s洪峰实际1,200PDU/4,800items、A/B各120请求、UI60次成功与3次16backlog stop/recovery；dev142 C06 pass224.163s：160重连、20启停及3reset，完整资源回落/阈值assert；dev143 D01 pass61.723s：真实冻结ManagedS7、两自定义端口与240次60s读取，无DAA应用/SQL。

D02 dev144真实fail：完成A stop后Python冲突fixture首次bind报EADDRINUSE，原raw保留A144，不把地址错误算server no_go。最小修正只在runner：先复核stopped及C/H/TCP=0，再精确lsof LISTEN、netstat的30102记录，owned conflict socket设SO_REUSEADDR而SO_REUSEPORT保持0。新B0 dev145/source `ba08e83eb3c13ece431c87b304c8bdc2d0e1f8122e24c2477acc2ea9863b9b3e`；dev146实际lsof exit1空、netstat exit0仅本次server50195对应TIME_WAIT，无foreign监听；REUSEADDR实际读回4（非零）、REUSEPORT0，冲突拒绝/释放恢复/B不受影响全部pass6.119s，不抢占/隐藏复用/换端口。dev147/148/149 X01三次独立重置实际pass3.926/3.978/3.933s且持续B读；dev150 X02按单Rust进程内native无sidecar严格not_applicable，明确native硬崩溃可同时影响A/B，共同退出/资源清理仍完成。

上述B0/诊断A136–150已逐成员SHA持久化并正式verify exit0，未覆盖任何旧run。B0dev145的180源码/288固定inputs、八bin均核定；自dev64只改Python runner，八bin与dev64逐字节一致，因此精确复用A67/desktop931b的新三轮正常可见启动/IPC/关闭以及独立A19未变34项视觉细项，不把旧desktop当新构建。当前稳定候选完整原19矩阵从dev151重新执行，W各三次独立reset、原P2时长/阈值及P3不变；C02仍嵌于C01同16会话。历史诊断不转记最终候选通过，最终DEV矩阵、fresh QA及Owner终验仍待后续事实。

## 8. r4最终稳定候选与Development handoff

### 8.1 精确交付及DEV层次

本轮精确 `ARCH-AW-005 r4`，spec SHA `4f1b03ec618bd0a40295bf273339538bc1491f8082380a009449f681ef56c2fc`；正式工作树HEAD仍`0af5b91177f3bca63f9f3c2bef9f14004ea49944`，不是仅凭HEAD可恢复的交付。未创建commit/branch/tag、未push。当前产品源码候选 `ba08e83eb3c13ece431c87b304c8bdc2d0e1f8122e24c2477acc2ea9863b9b3e`，B0 dev-0145/A145 inventory `a147b57eef133508247c51a67a5482216ca6deb19274a1cba4ae2e6b906ea7cb`。180项正式D/R/S源及108项只读来源共288项，详见[完整交付源码清单](evidence/delivery-source-manifest.json)和D/source-inputs.json SHA `1e1ae973328b7a4f1d8611d2596ccb64bd1289c75f4bb8a2c767d59521349c80`；受控native patch SHA `3c3fa385e760f4f9549b14d70545962f0ebebe121d0c4d7401048840fc850ed9`。所有适用原case已完成DEV自检，但新fresh Verification及Human Owner最终接受仍pending，protocol工件仍candidate，不能宣称已获正式联调放行。

自日志修复dev64以来只改正式Python runner；八binary与dev64逐字节相同。A67/desktop931b三次真实可见/两只读IPC/正常关闭及本次Owner“ 三个窗口均可见，已正常关闭 ”回复作为当前binary的原生证据；A19旧主题/中EN/刷新仅按34项不变UI来源复用，旧source06a5/desktop86c2身份不混称新binary通过。r3、dev15/26/52/63及慢接收/fixture失败均保留原状态/原raw，不倒填。

| 产物（均在T4/build/dev下） | 当前SHA-256 |
| --- | --- |
| native/libds_g0_native.dylib | `e6e03de8227629dc6e8f4344b1f419ac89804b07ce54989c0a1c1a0ec51e5b08` |
| native/libds_g0_reference.dylib | `33221aa62be3e35759017df557985e63b2945587d436a00a778288427173d07d` |
| native/ds-g0-reference | `9e308caac3a20c2daf8281f15cf21c3b2fe9cf30d38c2d97afc022507b90be4d` |
| native/ds-g0-native-abi-probe | `09699696674711e22303d26e5c35ff25aacfbfa8493ca5a67ca750086397b06e` |
| runtime/aarch64-apple-darwin/release/ds-g0-server | `694d5e82bf4a8b2487df78c52821ad7ca7996ab98ad289119e2743df12b3dd62` |
| runtime/aarch64-apple-darwin/release/ds-g0-abi-probe | `7f0b0849025caa3f5cc2cbba9aaa1f0f7e36fc430f484cb204bb81074ade7c05` |
| daa/aarch64-apple-darwin/release/ds-g0-daa | `2693af25bb281853583c849129f2519a9bc118a8e65d1665a79e348920d9a729` |
| desktop/aarch64-apple-darwin/release/aiis-device-simulator | `931b1ab402ce6f8eaee8c5233245db92db7c8ffe9c21855aeaba09a81c670b30` |

实际锁图：runtime54 registry、desktop430 registry均为冻结548 bank子集；真实DAA client解析60 registry+path core，为原静态66 registry allowlist子集，未强行激活optional边。锁SHA分别`399d6d5e4d780a64f13e69d0b32d662da9776d93e9ea94438894747ef9d65a79`、`2b1dd4f579c9d6ee8674c82fd030842b32f0f5b38d4108a5b272c9a34dd043f6`、`96d0e596e7896c377d8aaf68b6378a1506112befe0aa4b37c039434b3272e5c8`。固定DAA37/CU17/core0.1/v1和五真实模块未改；accepted清单是60/61原字节+已批准CODE_INDEX导航例外，不写成61/61。

### 8.2 同一候选最终原19矩阵

最终pipeline session77459 exit0，共38个正式runner命令：W九项各三次独立fixture重置（每次W03含100轮），C02沿用C01同16会话，X01三次独立重置。下表仅DEV实际结果；逐项raw/完整命令/逐item回执/images/seq/来源/时钟/资源/cleanup与inventory逐SHA见[证据索引](evidence/evidence-index.json) current_case_runs，全部适用项pass、X02条件N/A。所有run clean/server_exit0/evidence_complete/sampler_complete，stdout/file一致无降级、三固定监听空，A151–188全部已持久校SHA且正式verify exit0。

| Case | 本候选实际run | DEV事实 |
| --- | --- | --- |
| W01 | dev-0154, dev-0155, dev-0156 | pass |
| W02 | dev-0157, dev-0158, dev-0159 | pass |
| W03 | dev-0151, dev-0152, dev-0153 | pass |
| W04 | dev-0160, dev-0161, dev-0162 | pass |
| W05 | dev-0163, dev-0164, dev-0165 | pass |
| W06 | dev-0166, dev-0167, dev-0168 | pass |
| W07 | dev-0169, dev-0170, dev-0171 | pass |
| W08 | dev-0172, dev-0173, dev-0174 | pass |
| W09 | dev-0175, dev-0176, dev-0177 | pass |
| C01 | dev-0178 | pass |
| C02 | dev-0178 | pass；C01同16会话内20次额外会话拒绝及替换验证 |
| C03 | dev-0179 | pass |
| C04 | dev-0180 | pass |
| C05 | dev-0181 | pass |
| C06 | dev-0182 | pass |
| D01 | dev-0183 | pass |
| D02 | dev-0184 | pass |
| X01 | dev-0185, dev-0186, dev-0187 | pass |
| X02 | dev-0188 | not_applicable：无sidecar，进程内native硬崩可能影响A/B；共同cleanup完成 |

C01/C02 dev178 duration335.971s：30s预热+原300s测量、9,600请求/345,600应用payload B、每连接600次；逐连接p95最大0.362458ms、p99最大5.08117ms，queue p99=0.05ms；A规则due24,000/missed0。DS均值0.0844686单核，RSS采样峰6,782,976B/净-491,520B、线程25、FD+Mach83，未除主机10核。DS server独立全树含两instance，不含Tauri/WebView；外部observer/server/reference37PID的原样本、起止和CPU不可评估项分列，不能把外部费用算0或混进DS。A178 inventory `b1694c0be5eefc5b31ae27f81be68d2a11f12e02dcbe66cb061715274013a3c1`。

C03 dev179 55.707s；C04 dev180 19.345s，slow cid9真实op3 started649151684042000到pthread_join_return649153689299000为2,005.257ms；应用握手后不读，实际304次请求后期限关闭（600为上限、30s为最大窗口，未伪报600完成），SO与未读/广告credit原值分列。C05 dev181 77.309s：原60s F1,200PDU/4,800items、A/B各120请求、UI60成功、3次真实16backlog stop与5s恢复；C06 dev182 224.074s：160重连、20次启停及每次10s停机观测、3reset，资源/趋势原断言通过。D01 dev183 61.348s真实ManagedS7两端口/240次60s读取；D02 dev184 6.040s；X01 dev185–187约3.98s/轮，连续100ms B读与A关闭/stop/rebind真实并存。

### 8.3 DEV self-check、变更面与证据

变更文件精确逐path/SHA由180源清单、288 source-inputs及最终external receipt列示：DAA白名单派生的D工程和最小壳、R唯一Rust业务库/三个测试、S有限native桥/独立reference/真实DAA client/五stdlib脚本/合成模板与vendor派生manifest；先归档r3原99源后仅退役六个旧S/server业务文件。docs DS正文仅r4语言/共享/设计边界增补、docs README双语仅DS第16行，CODE_INDEX仅真实DS结构，本tasks与P恰五类紧凑工件。未改spec/checklist/四根索引/DAA/CU/core/004。approval保护基线下另13路径为006/007架构文档/bundle及AW索引foreign；根四索引和spec批准登记归协调/PM，不认领整树dirty，不回退。最终receipt固定当前工作树角色delta与各文档SHA。

实际构建/测试原命令和真实退出码见各A commands/stdout/stderr：正式CMake/clang、Rust offline/locked runtime/DAA、pnpm offline frozen及vue-tsc/Vite/Tauri no-bundle均exit0；前述内存/FFI/时钟合同测试及dev64真实stdout partial/EAGAIN回归pass，日志修复后无R/native/UI变化，不再重复无关测试。A145新B0无端口100同clock夹点、int0/37、Tag20/align1/offsets、callback版本/大小/预算、file/otool/nm及冻结feature图均exit0，先于本候选协议运行。新probe508B原降级file已持久A68，SHA eacab7ea09105c1a8e7cd647a0ff190fbeec07f54ad1d9eae40a79cb33a57cb2，不只留tmp。

最终Markdown检查覆盖15文件/113相对链接（含anchors）/29表格、围栏/尾空白、双语唯一DS行与i18n键对称；git diff --check tracked面exit0；untracked logging.rs/run_cases.py 的git diff --no-index --check exit1且输出空，意为文件有差异而无空白诊断。此前vendor63个CRLF/原空白诊断为冻结官方原字节继承，未为格式检查改包。辅助scope检查初次误把r3 inventory列表当dict而exit1，修helper后原113成员全SHA核定exit0，无产品/原件变动。默认sandbox只读sysctl被拒exit1，精确require_escalated读核数/内存exit0，未改系统设置。新增case表分隔行初次少一列导致静态exit1，修正该行后复核通过；仅文档格式修正，不改产品候选。最终必要检查原输出另归A189（同闭集commands/results/cleanup），不当QA verdict。

R1–R21/AC1–AC32的可定位DEV证据映射详见[有限协议候选](evidence/protocol-baseline.json) coverage_evidence；AC23–25只对应canonical §13设计增补，不冒充产品import/SQLite实现。完整r3历史、失败/blocked/中间候选、源代次/对应A inventory保留于本tasks和P索引；不按最终值相同替代真实wire或把历史expected当当前证据。

### 8.4 运行入口、独立复现及资源保留

正式入口/角色路径与命令参数归[G0 README](../../automation-world/device-simulator/g0/README.md)、spec §3.3及protocol-baseline build_and_run_contract。固定绝对Rust1.89、Node22.19/pnpm11.11、CMake4.0.2/clang17/SDK26.1，macOS15.7.7/24G720 arm64，实际主机10逻辑核/32GiB；只用T4隔离cache和冻结锁。QA在build/cache/tmp/profile/runs的qa角色路径独立重建、获得自身8bin及B0/ABI/limits/100clock记录，然后用正式verify_evidence.py --record-b0与run_cases.py --b0-run指向自身qa run；其binary SHA可因Mach-O路径/UUID不同而异，不要求改P或假定可重复同SHA。原生profile须显式owned marker，prepare_data复制五模板；native3轮、两IPC/真实可见与正常关闭和协议原矩阵仍须独立取证。QA不修改实现/P，若失败回Development新handoff。DEV不自行启动Verification。

当前最终只读资源核260已知PID无匹配owned runtime，session77459已exit0，无30102/30103/30104 LISTEN；两精确DS identifier WebView路径当前lsof exit1空，非倒填A67五秒证据。全部raw/资源/退出账见[resource-closeout](evidence/resource-closeout.json)。显式DS_PROFILE_DIR=T4/profile/dev/native；另观察到/Users/jason/Library/WebKit/com.aiis.aw.devicesimulator/WebsiteData与/Users/jason/Library/Caches/com.aiis.aw.devicesimulator/WebKit，实际stat元数据已保留，不能从名字/uid推定全为本任务新建、独占或可删。

D内忽略node_modules及src-tauri/gen/schemas、T3原诊断/build/cache、T4 dev build/cache/profile/helpers/raw、全部A与r3-stop-snapshot均保留供fresh QA及后续另批DAA联调依赖，不清理源码/原始证据/未知系统数据。清理触发是QA/Owner终验及后续联合验收依赖结束后，由协调核归属/占用、A完整持久和明确清理决定；当前未删目录/缓存，未杀foreign/换端口/用SO_REUSEPORT。

已知限制：仅合成DB41/57和有限PDU/item/类型/权限白名单，>16容量/三平台/完整PLC未证；单进程native硬崩可影响A/B；短命PID单样本CPU不可评估且外部Mach计数未知，采样峰非全寿命峰；C04 SO读回不等同kernel物理内存硬限；有限buffer/日志可降级，真实丢失必须计数且本case不放行。G0不实现产品配置SQLite、完整导入/布局消费者/UI、真实PLC、DAA应用S7→SQLite、Backend/API/上传/Stage C、发布/安装器/系统注册/权限修改或Git refs。独立QA、Owner终验和联合验证均未替代。

### 8.5 精确Developer handoff

Development将以上精确r4、正式工作树source ba08e83…、B0dev145、同八产物/A67原生与最终dev151–188矩阵/P五工件/持久A/资源账交唯一主协调。完整最终tasks及P/文档/source/bin/patch/lock/工作树指纹记录在T4/tmp/dev/developer-handoff-receipt.json；receipt是末次行政输出，不与自身/本tasks循环内容哈希。主协调核receipt后再启动**新的实际Verification，fork_turns=none**，独立复现并独占checklist；Development到此停写。当前仅developer_handoff，不授予QA verdict、Human Owner最终接受或生产/联调放行。



## 9. r5实施起点、来源保护与执行计划

### 9.1 批准、角色与原件先行

实际Development承接唯一获批ARCH-AW-005 r5，Owner精确原话见spec §10.1；批准前draft SHA e8e4462a6be3b0b23c4f28c074b0c7ab98cc61d51aed151b51fb8e5d34db2522，批准登记后spec SHA 67155fe4fca3068ef8e616dcf0ade69a5cdc614e7175a2f1ef4c6bf98f935419。只写§5精确实现面和本tasks；spec/checklist/四根索引/DAA/CU/core/004/其它任务只读，主协调独占索引与fresh QA调度；多人dirty保留，不reset/覆盖他任务，不自行给QA/Owner结论。邮件按Owner要求跳过，无新的人工三窗gate。

第一次产品源码改动前已将r4的180正式源码+108只读输入原字节（3,416,737B）、原r4spec/tasks、最新checklist2ba72…和较早checkpoint771eb…分别保存、P4原五工件与DS正文停点保存到A5/r4-stop-snapshot。A4原199份inventory及其全部必要raw成员逐SHA核定，inventory副本及原位保留路径关联入A5，原A4/r3归档不动。snapshot共499成员，inventory SHA f3b033fdfa134c74743f9c92045da6bebaffdb445c9e041d03b2d0bfdd8e12a0，持久后再次逐成员SHA/bytes复核通过；此时未改产品source、未删G0。首次辅助封存命令exit1：base/r4-checklist.md实际是771eb较早checkpoint，不是批准pin2ba72；改为保留该原件并从owning当前checklist读取已核准的2ba72最新原字节，第二次封存命令exit0。不是重算expected或覆盖历史。receipt=T5/tmp/dev/r4-archive-receipt.json，角色起点/5份before=T5/tmp/dev/role-start.json和before/。

r4三组DEV/QA正常关闭事实均保留，独立AC31已闭合；r4全部独立协议QA仍未完成、不转成r5通过。原r4 tasks全文已持久；本文件§1–8历史正文保留，只有当前metadata接续r5，本节以下记录新实施事实。

### 9.2 按批准合同串行实施与验证

| 阶段 | 实施内容 | 必要退出证据 |
| --- | --- | --- |
| 1 来源/正常入口 | 冻结196 DAA源码隔离暂存，完整copy/adapt/new/kept清单；保留R单owner/5图标/CU装配；迁native到正式N，R自动CMake和DEP/rpath，native-s7显式Tauri features、空DS profile/新本地SQLite。 | 来源pin/普通pnpm tauri dev实际feature及真实native/SQLite/IPC/无自启；K01/K02，产品/test构建各自hash；不借旧target或G0环境当启动必需。 |
| 2 通用业务 | UUID实例/DB map/完整typed codec/policy/5规则；单SQLite v1/锁/CAS/revisions，真实core导入/手工建模/布局命名/重导；停机apply九保值场景和恢复。 | 无端口Rust/真实ownedSQLite/core v1消费者与K02–K07，移路径后ABI/int/100clock/实际预算B0闭合，之后才S7。 |
| 3 页面/风险验证 | DAA适用六页/编辑确认组件/16IPC闭环；test-automation非default+owned manifest/真实WebView DOM→正常IPC/Window.close及N1–3；同产品R测试宿主原19协议case。 | K01–K10及N1–3和W/C/D/X全部适用项，原次数/时长/阈值/分母，失败保留；UI自动化不冒充物理鼠标/全视觉判断，不再人工反复关窗。 |
| 4 退役/交接 | 有效产品验证/原件持久/引用迁移后按每文件map退役废弃G0；清后构建/受影响回归、双语文档/CODE_INDEX、P5恰五JSON、raw逐成员SHA持久A5。 | 清后正式source/lock/bin/case/evidence/资源精确receipt，必要DEV自检真实exit，developer_handoff后主协调启动新fresh Verification；Owner最终接受仍单独。 |

T5=/private/tmp/arch-aw-005-r5-exec，A5=/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r5-evidence，P5=evidence/r5，仅dev角色stage/build/cache/tmp/profile/runs空间。固定30102/30103/30104与实际需要的15194/14194使用前实时核冲突，不抢占/换口/扫设备。DS自有配置SQLite属于已批MVP，DAA应用→SQLite联合验证、Stage C、Backend/真实设备/发布/Git refs仍排除。当前产品/K/N/协议验证均尚未执行，不预填pass。所有普通同scope问题继续解决，实质超allowlist/依赖/验收/风险才回协调/PM。

### 9.3 正式迁移与首批真实无端口验证

196 DAA原字节已由正式scripts/derive_daa.py隔离暂存T5/stage/dev/daa-source，pin digest 4751262a5c68aa28f037f9214b43d980587059663e762de096f9b5462bf855e9，未运行/改写DAA。先迁原native34成员到N upstream/controlled，只有批准八文件改内部G0符号前缀，原线程框架不改；bridge为ds_s7有限协议适配。旧G0仍完整保留，未触发条件退役。R/build.rs已自动CMake→OUT_DIR/native并输出DEP metadata，desktop消费rpath，tauri.conf显式native-s7；R离线锁87 registry均是548冻结bank子集，Cargo.lock SHA bdb170c99a5e863bfd7010032739c37bcbd19234de25c47da868b62c9b8bfaab。2026-10-21普通库cargo check离线/locked/目标arm64 exit0、无需DS_G0键，只证明当前库/native构建，**不等于正常桌面入口/B0或产品通过**；desktop/bootstrap仍在接续改造。

新增通用Workspace/UUID/DB/typed值/策略/稀疏coverage编译及规则纯领域，避免把64KiB DB扩成逐bit版本数组。IPv4使用真实parse+is_loopback校验，网络实验仍只批准127.0.0.1。typed/rule黄金测试首轮确实发现REAL默认JSON整数0与解码0.0不等、sine绝对整周期浮点残差，两测exit101；A5/dev-run-0001持久保留失败时源码/原输出，inventory 0470d4ed5b74a01f2f72b04e81b755b8d15630bef5792b4f03f523daeaa8b5a0。修正REAL默认0.0与周期取模后两测exit0。

独立DS profile OS锁、SQLite v1迁移/身份校验/固定SQL、1执行+4等待worker、draft/source/revision同事务CAS、selected CAS已落正式R；进度回调使用每job绝对1s截止、busy_timeout最多剩余1s，SQL不持image owner锁。磁盘系统调用不可被宣称硬实时抢占，IPC超时记unknown、保留worker/锁直到真实关闭；拒绝未知/坏库/WAL/SHM/symlink，不删除修复原件。configuration_store两测exit0：真实新库/重复profile锁、unchanged/CAS冲突、原BOM/CRLF bytes、source immutable rollback、selected重开、未知库/坏库/空半库/符号链接/WAL原件保护。库schema包含七张合同表，无运行值持久化；数据库仅T5/profile/dev/normal自有合成路径。

真实配置服务保护来源/布局/初值/策略证明，导入以共享core scan一次catalog→显式expand闭包→稳定结构段ID；布局/命名独立预览确认，票据≤8/300s且绑定ETag/candidate hash。layout_naming通过真实DS导入/布局服务消费原四个daa005-layout-oracle，并消费原names.db/.udt核路径/数组地址兜底及STRING整DB拒推，两测exit0；初次测试include相对路径少一级导致compile exit101，修正式测试路径后通过，未改原fixture/oracle。当前仍是中间库事实，尚未完成所有重导/保值/K/N及原19矩阵；没有S7监听或新原生窗口。

首批原命令/真实exit、源码快照和输出持久A5/dev-run-0002；此前官方构建依据为Tauri features配置https://v2.tauri.app/reference/config/#features 与Cargo links metadata https://doc.rust-lang.org/cargo/reference/build-scripts.html#the-links-manifest-key，版本执行仍以锁内Tauri2.11.3和实际新产物为准。下一步将这些服务接入同一Rust image owner/UUID manager，再形成普通入口和自动化门槛，不把旧固定A/B壳当本轮MVP。

### 9.4 通用owner、停机保值与六页首轮构建

正式Image已改为UUID实例内多DB map/逐点元数据与稀疏coverage；BOOL/完整typed值及每来源权限在唯一提交前核全触达，padding读零/禁写。Owner继续每item三类/连接轮转，规则不变值不增seq/time；模拟时钟暂停/启停冻结保留。native bridge仅把固定G0两端口/127.0.0.1参数改为显式IPv4 loopback/1–65535产品参数（实验仍只批准127.0.0.1的固定端口），没有新协议主循环。全runtime线程准入已去旧53常量，保守固定12名额+实际owner数+active listener与stop reaper各2+worker≤64，同时原C/H/global/byte边界保留；8实例不外推8×16容量。shutdown先全实例封准入/请求stop，共用4秒轮询，留SQL/log收尾预算；未真join不还名额。

停机apply以typed快照/epoch/seq/generation/值摘要构建并复核，SQL在owner锁外；保留失败明确拒绝而不静默初始化。正常stop绕过跨SQL的instance.control，能使预览generation失效。配置删除先纯prepare/ETag/CAS真实保存，才清理对应已stopped runtime；真实SQLite写锁失败和stale ETag不丢原owner/hold值。回执外层已按分段事实：already_loaded/unchanged committed=false，selected已提交而安装失败承认committed=true并给selected事实；unknown只匹配精确receipt/commit未知类别，不把optimized_access_unknown普通拒绝误分类。

最新Rust实际整组12测试exit0（owner2、apply/receipt3、store2、layout/naming3、typed/rules2）：含九保值场景、真实配置服务→selected→同profile重开初值/stopped、already_loaded不改epoch、start/stop后stale快照拒绝、删除保存失败保hold44、成功删除清selected/owner，以及持控制锁时stop独立返回。原expected-v1全部独立case经DS命名服务消费、原四layout oracle/实际DB UDT导入均通过。新增完整v1用例初稿错误地把不同前置条件合并并漏DB60/47，实际exit101与失败测试源已保留，改为每个原向量独立完整namespace后通过；oracle未改。上述Owner start仅Rust线程控制，未调用S7监听。

Tauri默认产品bootstrap已改用实际app_local_data_dir/可选绝对DS_PROFILE_DIR，16项严格IPC薄命令接同R服务。独立profile的持久UUID将用于非零WKWebView data_store_identifier，避免仅隔离SQLite却复用旧DS WebsiteData；未读写原系统路径用户内容、未删除原系统目录，此刻仍未native启动，实际新路径待运行观察。desktop cargo check/native-s7真实exit0；初次异步State命令未返回Result导致编译exit101，修薄封装后通过。desktop锁441 registry、runtime87均精确是冻结548 bank子集；desktop Cargo.lock SHA cd2854503e8bd0ddc26bffea91cd931e740588210abd9610147dfd14a8b0c8b5，未升级/增加集合外包。

DAA冻结暂存的8个适用公共内容组件已直接复用，主壳/语言/主题/五图标保留适用血缘；新增DS六页和8业务组件/16项IPC facade已首轮接线。宿主唯一≤1Hz可见快照轮询，编辑草稿与saved/selected/loaded分列；stale错误保旧完整DTO，切实例/页的过期响应丢弃，维护写unknown不自动重试。规则mode互切最终rule.kind随新mode；dirty关闭通过真实CloseRequested与保存/丢弃/取消意图，不提前shutdown。当前前端vue-tsc与pnpm build真实exit0：Vite1685模块、产物T5/build/dev/frontend；这只是编译，不称正常入口、真实DOM/原生或产品验收通过。

pnpm初次离线缺包exit1是v11 store使用index.db、首次复制漏该索引；复制旧已冻结DEV index.db到新owned cache、逐SHA核后76包全部离线复用。随后pnpm exec角色cache/globalVirtualStore设置不一致触发自动install，曾尝试registry metadata读取且网络失败/非TTY退出；保留原输出，未下载/升级。读取当前锁内pnpm实现后统一pnpm_config_offline=true、verify_deps_before_run=error、enable_global_virtual_store=false和owned store，停止自动安装/更新查询，真实类型/产物构建通过。Vue日志script换行及递归JSON类型首次exit2均已修并保留失败输出；辅助命令一次相对cwd错误exit1未改目标文件，后续用绝对路径修正，不影响批准源。

本阶段A5/dev-run-0003含原commands/stdout/stderr、失败测试源、当前源码快照、lock bank核验与UI/cache血缘记录并二次核inventory。普通pnpm tauri dev、新ABI/clock/B0、test-only宿主/原19矩阵、完整K/N自动化及G0条件清理仍未执行；旧G0原件继续保留，未交QA/Owner终验。

### 9.5 普通pnpm入口实际闭合（2026-10-21）

正式scripts/run_validation.py显式角色/根路径/冻结196+108输入核对后执行普通`pnpm tauri dev`；dev-0005默认sandbox真实拒绝pgrep(sysmon)/127.0.0.1:15194监听EPERM，未启动native。已精确escalation只读核PID15882退出、15194空，失败保留A5/dev-run-0005（inventory 8bafa770d6684fbf665e614ec9b789e97670b282e85c52b6819574e4b33b0663）；修runner在任何启动前验证进程查询权限，清理不再被查询异常跳过。

dev-0006在已批准精确原生/loopback权限下运行同正式命令，实际Tauri argv为`cargo run --no-default-features --features native-s7`，自动R build.rs/CMake/DEP/rpath，无DS_G0键、无预建库路径。真实native PID17326，bootstrap/configuration/runtime_snapshot三IPC均result=ok、committed=false；新owned profile `T5/profile/dev/normal/dev-0006`，SQLite appID=0x44535631/user_version1/七张合同表；空配置不自动S7监听。实际Vite15194仅本轮node17270，结束五个固定端口全空、所有已观测owned PID退出。desktop debug SHA74f0c07abf29f8ae2ae63b3c94f88879f2b53132dadafeab3da55700d75abe02，otool和真实原输出保留A5/dev-run-0006（inventory aa8bdfb558312438175ca2ae2a4184812f14315ce44c6e762d11b18ff90b0881）。普通watcher收尾使用owned进程组SIGINT，不算正常Window.close/N场景通过。

该profile持久UUID/WK data_store_identifier为97484979-7b80-4ffb-922a-4c9a294d3810，在WebView创建前设置；仍需记录系统实际新store路径，不能把DS_PROFILE_DIR或ID本身当路径/所有系统数据归属证明。默认用户目录仅同代码路径解析，未对真实默认用户profile作native写入。此时自动test-only宿主/DOM流程、新ABI/clock/预算B0、原19和完整K/N仍未执行；无S7 listener、未清G0、未developer_handoff。

### 9.6 ABI/clock/预算与首轮自动原生失败（非最终候选）

普通入口的实际独立 WK store 已按精确 UUID 元数据只读定位为 `/Users/jason/Library/WebKit/aiis-device-simulator/WebsiteDataStore/97484979-7b80-4ffb-922a-4c9a294d3810`，新建时间与dev0006一致；旧DS标识两路径仅元数据核对，未读用户内容/删除目录。该路径属于本轮观察到的store，不推定所有系统进程费用为零，也不据profile变量宣称全部WebKit系统缓存已清理。

无端口实际测试扩展至typed黄金向量、core全部命名向量、真实重导、32DB/4096叶/8实例边界与manifest逃逸等；整组22测曾21通过、1处测试将REAL解码后的f32与JSON十进制解析所得f64直接比较而失败。保留失败，改为按独立IEEE f32位值核定，typed三测随后exit0；正式整组复核仍待最终源。固定stdout partial/EAGAIN、日志ring溢出、轮转与真实只读FD失败probe已执行，不将仅正常零错误当降级路径证明。

B0 dev0007真实blocked：完整snapshot单event超初始64KiB内部上限，evidence_lost=2；未启动listener。未截断snapshot，改为128KiB单event、pending/history各8MiB、独立file队列16MiB及批/序列化临时副本保守日志总额44MiB+128KiB，纳入既有总预算；各计数/实际heap容量峰另记原件。dev0008是对应中间源的B0 closed，不转作后来候选证明。dev0010对source `e129a0cbe5366f9c49bd811837eb3633e141c0d39c9df4af65ec604aa74bb789`完成真实int0/37、Tag布局、100次同CLOCK_MONOTONIC夹点、native/DB/队列实际预算及freeze审计，B0 closed，完整正式源码原字节随run保存；没有先开端口替代B0。

dev0009完成普通产品release与非default test-automation release两次真实构建，随后dev0011实际N1通过ready/UI偏好、创建实例、多文件DB+UDT导入取消/确认、完整布局命名与跨页确认、手工DB73/UiValue。Ramp→Sine→Random三次策略真实保存成功；最后UiValue权限/初值保存被拒，driver仅录到泛化错误文案，旧回执日志无errorCode，不能倒填精确拒绝码。持久草稿仍为旧UiValue继承策略，未提交失败编辑。现场目标控件显示clientWrite Allow/uiWrite Inherit，与脚本Deny/Allow动作不符；全页面匹配同名下拉选项会选到仍在退出动画的前一列表，修为当前combobox aria-controls列表内选择并核选中值。产品owner/权限校验保持，后续新回执增加errorCode/receiptState以实际复现核分类。

dev0011失败实验已明确TERM中断（exit -15），owned PID85636已退出/端口释放；不能算正常Window.close或N1通过。N2/N3、原19协议仍not_run，无r5 S7 listener；旧G0未清理。A5/dev-run-0007–0011均已逐成员持久封存并二次核SHA，inventory依次b21eb7c6…/f3ddaefc…/31f7557b…/7cd0664d…/4be2a94f…；失败源/诊断原样保留。新源同时收口同名声明的文件名/声明序号显示、校验问题的实例/DB/点定位及双语说明，当前新build/B0/N自动流程执行中，未预填通过。一次忘传run-root只显示帮助exit0、一次误传T5/runs而非T5导致路径门拒绝exit1，随后正确显式T5继续；均没有启动副作用。

### 9.7 正式core/自动原生/通用拓扑与首轮协议事实

source874b2461…/B0dev0013之后，N1–N3 dev0014–0016实际全部功能/正常关闭通过，分别code0、正常关闭保守上界77.434/154.312/104.734ms，保存→重开selected/stopped/初值12、普通42/维护9、规则进度、真实独立S7读取、单连接关闭及dirty Save/Cancel/Discard均走正常DOM→IPC→同Rust owner→Window.close。aria-controls归属选择修复后UiValue策略保存成功，确认旧N1是driver串选，不放宽产品owner。A12–16原件已二次核SHA；N1初次失败A11保持失败。没有人工关窗前置。

后续真实K02故障回归发现SQLite OPEN_READ_WRITE仍可能fallback为只读连接；已加实际Connection::is_readonly拒绝并保持原文件，回归通过。非默认test-automation增加逐SQLite worker、一次性、固定白名单故障点，不进入正常产品接口：保存/selected提交前rollback、提交后真实commit但ack丢失、selected已提交安装失败/旧image禁止start、安装成功后ack未知均以真实ownedSQLite/owner/重开读回区分；不自动retry，不声称磁盘断电原子。真实并发CAS一成一conflict、源/revision原件、未知version/appID/schema hash、只读库及稀疏自有文件触发容量拒绝均通过；未物理耗尽主机磁盘，free-space门的实际值仍按真实filesystem读取，不用上述稀疏测试冒充物理ENOSPC。

正式core dev0019及dev0022 exit0，含日志降级/轮转、typed规则、九保值/混合变更/保留失败显式initialize_all、core原v1全命名和四layout oracle、真实重导/缺UDT/循环/未知类型/优化/多维/超array及同名UDT显式闭包、拓扑/manifest边界；另真实双进程争同profile：第二进程profile_in_use退出、不改配置bytes，第一进程正常quit/SQLite exclusive可重开。一次新增测试漏Workspace.schema_version编译exit101、一次把core已在preview拒绝optimized_access误当可到compile的测试期望exit101均保留并修测试；REAL规则f32端点假设经实际回归通过，未据假设改codec。dev0018格式check仅logging一处换行exit1，格式化该DS文件后正式core通过；不格式化DAA/core。

source248410be…/B0dev0024，普通dev0021和扩展N25–27功能/正常关闭通过，上界67.714/50.961/166.887ms。N2真实外部ownedSQLite BEGIN EXCLUSIVE使正常快照IPC失败，UI标stale且保留UiValue42；释放后真实快照恢复，显式pause成功；A→未加载B→A时无A值跨实例串入B。DB/byte/bit/loadedRevision来自实际owner快照，字段/继承来源双语显示；校验条按实例/DB/点定位，导入声明按文件名和序号区分。K07 dev0029实际使用A DB71/88/109、B DB94/130，整数/finiteREAL/完整STRING wire读写、A reset/stop/保存新revision/apply保hold52同时B每100ms继续读，六次真实B读均成功，原件持久A29。

原协议首轮W01–W06各三轮通过，W07前两轮通过，第三轮dev0050正确blocked：serverstdout403=file403，无degraded，真实code0/队列与端口全清；独立sampler在server退出瞬间proc_pidinfo返回ESRCH、Popen.poll尚未确认，sampler_complete=false。A50原失败保留，不改pass。仅正式runner修正为ESRCH后最多100ms真实wait确认exit并保留错误/起止/exit_code/空sample；未确认exit仍真实采样错误，不补0、不改变任何分母/阈值。新同范围候选重新B0/原矩阵执行中，C/D/X尚未由本节预填通过。

原生资源目前可确证desktop主进程、已观察POSIX children、独立reference/observer及新WK store路径/UUID。macOS XPC/WK服务未必是其POSIX子进程；未归属费用不记0，以上N功能/正常关闭结果不等于完整WebView全树覆盖。按spec §4.3，下一次必要自动native轮次补精确owned store的lsof→已定位PID ps/资源/前后核对，XPC与children分列；无法证明的关联保持unknown并交根核，不扫描其它应用、不杀系统服务。该缺口不阻断独立headless矩阵，G0清理及最终handoff前仍须明确收口。

条件退役计划现102个精确旧成员、尚未执行。首轮A5/r4-stop-snapshot的180编译源清单未包含旧vendor两manifest与native-g0.patch三份元数据；这三份在第一次删除前另逐SHA核本轮coordinator/before基线（patch亦与P4 native_patch_sha相同），原字节封存A17并二次核inventory58c69eaf…。没有改写原r4-stop-snapshot；退役脚本必须同时核该补充原件和当前完整产品验证，不能仅拿临时备份授权删除。R有效owner/native均保留演进，不将G0命名视为任意删除权。

### 9.8 完整快照容量、宿主准入与当前重新验证

source13a855e4…/B0dev0055的P1 dev0061–0087共27轮全部通过，W03每轮仍100向量；C01/C02 dev0088完成30秒预热+300秒测量，16会话共9600/9600请求、345600B应用payload，每连接600请求，最大连接p95/p99分别0.539334/4.38158ms，原件保留。随后C03 dev0089真实blocked：必要完整snapshot递归heap131387B超过当时128KiB单event，evidence_lost=1；stdout3825=file3825、sampler完整及正常清理仍不能弥补丢事件，未记pass。

同范围修正统一单event/file line上限256KiB并保留pending/history/drain各8MiB、file队列16MiB、序列化/parsed临时副本4MiB与active message256KiB，总保守46,399,488B（44MiB+256KiB），纳入原288MiB配置/SQL/preview/log预算。新增无端口真实最大快照回归：通过实际配置服务和owner创建完整63点/DB41+57，用真实Context的16 established+4 handshaking连接元数据、长UUID/u64最大序列值构造快照，实际Evidence→stdout普通文件与独立RollingFile两sink。dev0092测得event heap133387B、parsed heap134136B、serialized line26500B，临时String/Vec容量分别32768B；两sink字节相同、完整image/点/连接和lost=0，未截断或补造事件。连接元数据probe无socket，不转成16真实会话证明。dev0092的B0 closed，原ABI/int/100clock/预算及五个DAA真实模块dep-info均保留；C03 dev0093按原场景定向重证55.81140525秒pass，旧A89保持blocked。

通用组合根现headless固定12、desktop固定40名额（替代而非相加），包含本进程main/SQL/log/resource/control，实际owner+每active listener/reaper两名额+TCP worker另计，联合≤64；真实不足拒绝准入。desktop空壳约28线程、既有单owner/listener/worker场景峰36，扣除另计线程后保守预留40，测试固定额度边界归还一次；不把8实例配置上限当8×16容量。外部WK/XPC不塞入40常数，完整资源另报，未知不计零。全体关闭仍先封所有入口、共享绝对期限再真实join/SQL/log/锁释放。

dev0091/0094整组无端口30测试通过：在原九场景纯清单之外，新增真实SQL revision→地址/命名/策略确认→同owner install、混合变更/rollback/旧epoch拒绝与重开初始化逐场景核对；源数量128/+1、批4MiB/+1、单源1MiB/+1、深度8等边界均由真实core消费者执行。最新一次性test-only insufficient_space故障把一次实际free-space观察替换为0，走正常512MiB门并核SQLite bytes/草稿不变；这是容量门确定性回归，不是物理填满主机磁盘或真实ENOSPC声称。

当前新冻结all dev0095已启动，串行普通入口→core→新B0→自动N1–3/WK归属→原19。dev0096普通入口实际编译并启动owned PID59842、固定desktop40、新store acf95779-818c-4abd-92eb-dca5add3a0a2；等待三IPC期间，单次CUA getState明确返回Mac locked，未尝试解锁或改系统安全。已告唯一协调，保留900秒有界等待和正常watcher失败清理，锁屏不记产品功能fail。尚未进入这代native/WK采样或协议，不预填通过；C/D/X完整最终矩阵、条件G0退役、独立QA及Owner最终接受均尚未替代。

### 9.9 锁屏中断、同源headless接续与迁移核对

随后按唯一协调指令不再空等900秒：保存精确PID/argv与锁屏原文，在owned Python59624发送SIGINT，由既有normal_dev finally对watcher进程组作正常实验清理。launcher59667 exit0，已观测59682/59721/59746/59782/59790/59842/59847/59890全部退出、五个固定端口为空；未TERM foreign或将清理记成Window.close通过。dev0095/0096原状态fail保留，独立locked-environment-interruption.json明确environment_blocked_mac_locked，属于执行环境中断，不倒填产品功能fail/pass。两run已封存，原Mac安全状态未改变，协调另行请求解锁。

当前冻结候选为aa6a97d4e18db2fff22e41a070301bbd5a9513f257e5df2f7d74a5f155c784e7。无GUI依赖的core dev0097仍30测exit0，新增free-space确定性门回归通过；B0 dev0098 closed（inventory 5ca1d39f…），相同source、真实构建/ABI/100clock/预算、原模块dep-info可核。实际新配置编译→apply→owner的DB41+57 stopped快照与持久旧fixture-a/b.bin各1088B逐字节相同，SHA分别1dd31156…/cc17168f…、差异0；证明原绝对布局/bytes已迁移，非把expected样本当运行结果。receipt在持久A97/r4-fixture-actual-byte-equivalence.json（A97 inventory62a96e93…）。dev0090–0094亦均独立封存，旧失败证据不覆盖。

同候选正式protocol phase dev0099继续K07→W各3轮→原C/D/X，不依赖被锁桌面。K07 dev0100通过（A DB71/88/109、B DB94/130、B每100ms共6次成功读）；W01–W09 dev0101–0127全部27轮通过。C01/C02 dev0128按完整预热/测量执行中，本节不提前记结果。normal/native/WK仍需解锁后实际闭合，不机械重复未受影响同源同binary的已完成协议事实；最终逐phase/run/candidate明确，不拼接不同产物。

19份当前DS活动Markdown的92个相对链接/anchors与5对围栏、三组354/17/7双语键及插值对称检查exit0；第一次辅助slug检查把中文顿号误当anchor字符，exit1原输出保留，修辅助checker后通过，未为消checker错误改历史正文。完整literal-i18n核查另发现ConfigRevisionBar.vue的simulator.point不存在，现有simulator.levels.point可用；已向协调登记，将在当前冻结协议phase结束后作纯UI修正并重做受影响前端/native，未在录制中改源。196输入lineage逐SHA核定为40适配/7直接复制/10保留同字节/139仅参考不携入，明细随A99封存；新R/native/tests不伪称DAA复制品。

### 9.10 文件队列真实突发丢失与有界修正

dev0128完整336.346247667秒运行结束后按证据完整性判blocked：stdout253548/file253463，file worker实际丢85条，4条observability_degraded累计9/10/80/85；sampler与file mirror均完整、正常code0/所有监听与owned进程清理，但完整stdout不能弥补file通道缺行。原A128 inventory2d6d3f8d…保留，未改pass；该phase dev0099停止，余C/D/X没有伪填结果。

定位为file worker数量128先满，非256KiB单event再超限。修正为8192条（可容两批每批至多4096条Evidence drain）、仍受原16MiB byte门限制；保持lossy/nonblocking，数量或bytes先满真实丢弃计数、owner不等IO。另为冻结tracing-appender Msg(Vec)/crossbeam slot及控制分配、pending/history/drain VecDeque/Vec未用容量保守预留2MiB，总日志现46MiB+256KiB=48,496,640B，纳入原288MiB预留；不是把日志总额/线程/RSS验收阈值提高。真实peak另记，不把估计当allocator实测。

无端口B0 dev0129/source57db81c71a5264cbb3b76c97ae8ca923f7e0fdea5c5b1ef077cbdb00890c1f5f已closed，新增实际sink probe：4096条真实突发+绝对1ms节拍2048条，两sink6144条逐字节相同、无drop、真实drain；另以有界测试HeldWriter占住实际appender worker后精确填8192等待槽，再一条触发实际drop1，健康计数与queue bytes归还0、worker释放/guard收尾。该测试阻塞只在#[test] writer，不进入产品owner或native。完整C16/H4快照/降级/轮转/partial等现有probe仍全部执行，ABI/100clock/预算和模块源再次核定；未省略B0先监听门。

同一修正窗口只把ConfigRevisionBar定位标签改用现成simulator.levels.point，双语值原已存在；前端/native将按实际新产物重测，不把旧窗口证据标成新binary通过。按协调建议先定向执行尚未完成的后半段以定位真实问题：C04 dev0130实际pass19.565480833秒，原真实send阻塞/绝对期限/预算/清理判据不变；C05→C06→D01/D02→X01三轮→X02继续。最终稳定候选完整适用矩阵、解锁后normal/native/WK与条件G0退役仍待实际闭合；无developer_handoff或QA/Owner结论。

### 9.11 队列取证字段回归及后半段实际闭合

C05 dev0131先完成正常60秒段，随后积压子段在runner读取protocol_waiting时KeyError，整项fail保留，不记完整C05通过。该代stdout=file50426、无degraded、sampler完整/正常退出，说明新file数量门在真实压力下未丢行；不能据此豁免积压证明。定位为r5 test_snapshot迁移遗漏队列字段，调度队列本身仍存在；现有#[cfg(test-automation)] owner::test_snapshot在同一owner锁内输出真实protocol_waiting/rule_waiting/ui_waiting，不添加产品IPC或虚构队列。

按原runner C06/D/X消费者核owner/transport/DB点与resource字段，新增无端口契约测试使用实际协议fixture配置→同owner/Context快照，核类型/完整bytes/点/空队列；资源sample经正常Evidence加clock。首次测试误在raw resource_sample阶段要求monotonic_ns而exit101，dev0134原失败保留；修为实际管线后dev0135完整33测试exit0（A135 inventory670aaf86…）。该probe没有socket/伪backlog，真实积压仍由wire case证明。B0 dev0136/source87755d133b1f00cf903c1c1b0107a6a71e3996edf70d1a24e3eba73267b778ca closed，A136 inventorybcff2951…；34上游/8文件diff/ABI/int/100clock/日志预算等仍实际重核。

| 定向case/run | 实际DEV结果及原口径 |
| --- | --- |
| C05 / dev0137 | pass77.602660334秒；F1200 PDU/4800items全成功，A/B各120请求、UI60成功；3次16连接实际积压各15项/预留35328B，stop与恢复通过。stdout=file57404，无degraded，采样完整/clean/code0。 |
| C06 / dev0138 | pass224.585319792秒；160重连、20×16会话启停及每次stop后10秒采样、3reset与原资源回落/趋势阈值全部保留。 |
| D01 / dev0139 | pass61.900243459秒；真实五DAA模块/ManagedS7两个端口60秒共240次db_read，marker/允许hold变化读回和端口/TSAP证据保留。无DAA应用或联合SQLite。 |
| D02 / dev0140 | pass6.208566125秒；原错误身份/空端口/误端点负例及owned顺序冲突listener/重复start、B继续和A恢复，未换端口/杀foreign。 |
| X01 / dev0141–0143 | 三次pass4.080864375/4.098196958/4.13893525秒；A连接/屏障/stop时B真实每100ms继续读、原释放与重绑判据不变。 |
| X02 / dev0144 | not_applicable；唯一Rust进程+进程内native，无每实例子进程，不证明硬崩隔离，normal/stop/资源要求未豁免。 |

以上逐case原件均已封存，命令/退出码和定向聚合另A145 inventory83c12026…。随后同冻结source87755d…启动正式完整protocol phase dev0146，K07 dev0147及W01–09 dev0148–0174全部27轮已通过，C01/C02 dev0175正在完整原窗口；后半段定向结果不冒称已完成最终完整phase。

解锁后的下一必要native还将补已知POSIX children的逐PID归属/1Hz真实资源采样，现有PID/退出清单不冒充资源样本；child与owned store关联XPC同PID须去重，短命/未知费用保持null而不记0，不扫描其它应用或杀系统服务。该collector缺口在本轮冻结protocol结束后于既有run_validation.py收口，按实际R/native/client/协议代码与bin SHA界定受影响面；独立QA结论仍归后续fresh角色。当前普通/native/WK gate与G0退役未闭合。

本轮资源方法保留原1Hz逐PID角色/起止/退出/实际样本。存活不足1秒的负例client可能只有一个真实样本：CPU均值null/不可评估，不补0或删尝试，RSS/线程/FD只称实际观测或采样峰，不称全寿命峰；仍存活却漏采、sampler错误、DS核心覆盖不足或日志丢失不能据此豁免。C04的≤16KiB指双方实际有效SO_RCVBUF/SO_SNDBUF读回，peer FIONREAD/未读队列、TCP历史广告credit和实际发送进度另列；SO值不宣称kernel物理内存或过去信用硬限，不能隐去更大的未读数。该口径是原spec/PM只读方法澄清，不是降低原20Hz/最多600请求/30秒/256B/实际send阻塞及≤2.5秒真join门槛。当前所有进程与客户端均为owned合成loopback，不改全局sysctl/网络接口/MTU/系统权限。

### 9.12 完整协议结果、最后无GUI候选与环境停点（2026-10-21）

正式完整protocol phase dev0146已实际结束为pass，原冻结source `87755d133b1f00cf903c1c1b0107a6a71e3996edf70d1a24e3eba73267b778ca`、B0 dev0136。原矩阵38条case-run，另K07 dev0147；W01–09各独立reset三轮dev0148–0174（W03每轮100次竞争）、C01 dev0175同一30秒预热/300秒测量窗口内覆盖C02、C03–06 dev0176–0179、D01/D02 dev0180/0181、X01三轮dev0182–0184、X02 dev0185严格single-process not_applicable。未选sidecar，不证明native硬崩隔离；C02没有另造第二窗口或减少其20次拒绝/原会话读写要求。

C01/C02实际336.288743375秒、测量300000000000ns、9600请求/345600应用payload B，stdout=file253540、lost0、采样完整/clean/code0；C03–06分别56.008603542/19.581944625/77.599271667/224.349289750秒，D01/D02为61.512056250/6.207366125秒，X01为4.159152833/4.129822583/4.130879084秒。C05原F1200PDU/4800items、A/B各120请求/UI60与三次积压stop全部保留，C06原160重连/20启停/3reset/10秒回落采样不缩。完整原件逐成员封存A146 inventory `7f49c1de125fc84ccda190260561a0ce4f96ac316e9033916396580385156fe8`，243成员及38个child inventory；协调另外核SHA仅属完整性观察，不是QA。

本phase结束后只修改三个已批文件：`scripts/run_validation.py`为POSIX child与精确owned WK store关联PID的逐PID/1Hz去重资源采样与归属报告；`SourceImportPanel.vue`在文件行和DB/UDT声明选项使用同一批内序号+现有短inputId，消除同basename/同声明名歧义；`tests/ui/native_driver.js`用两个同basename NativePair UDT真实File并明确选择对应来源。没有改R/native/client/协议runner、阈值或依赖。最新source `7c969c29873f7a15d6caf7f40730b683e76a531a8c6fe912169729a9d3eeabc5`；dev0186前端build exit0，dev0187 B0 closed，136→187源清单精确三路径且5个headless实际bin/dylib SHA逐字节相同。差异patch/组件影响和各产物SHA见A187/component-impact.json；A146证据始终保留旧source归因，不倒标新候选，按未受影响组件/同产物引用。

A186/A187 inventory分别 `9d21cdc97e55dfe4aedb6b6606f54f838bf6f18cd49f2c53f6261d135270f5ae` / `ca1cda13907f5a7ee09c00a0911e3a572ba92cebba9597a7af911f1c3d028121`。新collector已实现但尚未在解锁native中执行：POSIX child与store关联XPC分列、同PID去重、短命/未知CPU费用null，未采到或无法归属不称0/完整覆盖，不把仅PID清单当样本。

K08无bridge已用现有IAB实际浏览器DOM完成：概览无实例/ready=false/无bridge提示；实例创建和保存禁用，正常“重新读取”确认后真实desktop_unavailable错误且未生成假配置；源文件选择/扫描禁用；策略/值/日志页均ready=false、真实空行/未知值，不用mock桥；960×640时document/body宽均960、提示与日志页仍可见，viewport恢复、临时tab关闭。console error/warn查询为空。两次CUA locator诊断（确认框尚开/退出动画后Cancel已不存在）按实际重新读DOM处理，不称产品失败。观察由实际CUA输出转录于A188/browser-observation.json；preview helper在300秒截止自动SIGINT清理先于观察文件落盘，原status=incomplete原样保留，不倒填helper pass。launcher8404及已观测8423/8429退出、五端口空，绝不拿watcher清理当native Window.close。A188 inventory `1a17e42d5f8f50fc6c9929e7bc4197fed590447dc44d55d6515e3871202a05c4`。

最后独立无窗口构建dev0189，沿正式native()相同两条pnpm no-bundle命令，普通与非default test-automation构建均exit0；普通产品带测试参数明确exit2。product SHA `54709f1ec2265d3293397ade6f0cd6bcfa484e9073b257ac6dc4d471a4f6ab70`，validation SHA `77700b47c29c31de171ee8811166b9c318c9f9b5d462368e8ea7668c0532b239`；各实际native dylib、file/otool/feature参数/锁及完整stdout/stderr见A189，inventory `7fcfcaac7287aea6dc23cd5079b3c30edafa3c6ae29385edabc3ddc5f5fc67a3`。没有启动窗口、SQLite或S7 listener，不把build当native行为通过。

静态文档/locale核验exit0：19活动文档/94链接与anchors/5围栏、354+17+7双语键和123个literal i18n键；表格检查30表无列数错误；196来源lineage仍40适配/7同字节复制/10同字节保留/139只读不携入。102个精确G0成员的退役plan只读生成、execute=false，无删除。45AC逐项与K01–K10实际证据/缺口映射及P5恰五JSON非终态草稿在T5/tmp/dev/p5-draft，副本与上述静态原件持久A190 inventory `413fc22357c2e0a3fce2f4310837e08c555ddbf45193d44a56cb02e6431eb7f9`；public evidence/r5尚未创建，不称最终交付manifest/baseline go。草稿区分core33实际通过、完整headless通过、旧N56–58历史与最新native未运行，不把旧binary的native成功搬给新binary。

**当前真实阻塞及恢复**：最近一次允许的实际桌面可用性观察仍为Mac locked（原件A146/post-protocol-desktop-availability.json），唯一协调已请求Owner手动解锁，尚未收到恢复消息；不再轮询/尝试解锁或改安全设置。当前无owned app/launcher/protocol监听，源/T5角色缓存/构建/数据库profile/DAA暂存及A5必要原件保留供恢复与QA；DS node_modules和src-tauri/gen仍有构建依赖。旧r4两DS identifier系统WK目录及本轮normal profile的独立UUID store均保留，未知历史归属不授权删除；最新完整WK/XPC全树资源费用仍待真实采样，不能据headless512MiB或desktop40线程预留冒称覆盖外部WebKit。

解锁后无新范围批准需求：先核当前source/196+108固定inputs/锁/实际bin及五端口；在正式D用 `/usr/bin/python3 -B scripts/run_validation.py --project-root /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator --run-root /private/tmp/arch-aw-005-r5-exec --role dev --suite build` 运行普通pnpm tauri dev真实三IPC/独立空profile/stopped入口；随后同参数 `--suite native` 自动N1–N3（新同basename来源选择/保存重开/正常Window.close/5秒/锁/全树资源），不要求人工关窗。最新B0已closed，同R/native/client/实际5bin的A146 headless事实按精确影响引用，不机械重跑无关长负载。必要native/资源门真实闭合后，才汇总产品完整验证→102逐文件退役→清后build/受影响检查→正式P5与developer_handoff→主协调启动新fresh QA。

本次只是environment_blocked非终态停点，未developer_handoff、未启动QA、未退役G0、未授Owner最终接受。还未完成：最新normal dev、N1–N3及WK全树归属、G0条件退役/清后复核、最终P5和独立QA。DAA应用→DS→SQLite仍另批，Stage C/真实设备/发布/Git refs排除。最终停点tasks/source/产物/资源与恢复命令收据归T5/tmp/dev/environment-blocked-receipt.json并持久新run；后续按同r5接续，不抹本次环境中断和旧失败记录。

### 9.13 Owner解锁后接续普通入口与自动原生

Owner明确解锁并继续精确r5，逐字原话由唯一协调传达：“已解锁，继续 ARCH-AW-005 r5 的原生桌面验证，验证后清理废弃 G0 并完成独立核验，形成可供联调的协议基线。测试自动完成，不要再让我反复关窗口。DAA–DS SQLite 联调另批，阶段 C 暂不开展。”不重做PM/重复批准；本次CUA getState实际无locked错误，保留已批准自动关窗方案。

dev0194真实preflight核spec67155f…、232source/7c969c…、196+108只读inputs/锁及9实际产物逐SHA无漂移，五端口空。dev0195普通pnpm tauri dev真实pass：新owned profile、独立store a366919a-8f63-4ee6-98fa-a89a323f624d，空SQLite v1/appID/七表、ds_get_bootstrap/ds_get_configuration/ds_get_runtime_snapshot真实正常IPC，S7三口全无listener，debug binary SHA6a2d82e8bdfa2d4fe64bc9f57967306c71476c9af339fe4b6ad069caef324ab7。正常入口smoke的watcher组SIGINT清理仍不是Window.close证明；launcher56112 exit0、已观测children全部退出、五端口空。A194/A195分别持久inventory b74ed65e… / 1bdb4f89…。

随后同候选正式--suite native正在串行执行普通/非default测试build→新B0→N1–N3；所有操作由固定DOM driver/正常IPC完成，正常Window.close与WK/POSIX/XPC全树报告按实际结果另记，不预填通过。旧环境停点A193及helper incomplete/失败历史原样保留，不把此次解锁倒改旧结果。


dev0196当前source7c969c…自动native suite实际pass，B0 dev0197在首个S7前再次closed；N1/N2/N3 dev0198/0199/0200全部code0、正常Window.close→CloseRequested/最终确认→ExitRequested/shutdown_joined/Exit，退出保守上界82.977/167.921/87.865ms，SQLite exclusive重开/锁释放、五口空、无剩余owned PID，samplerComplete=true。同basename NativePair两源的可见批序/inputId不同、明确选中第二源；多DB导入取消/确认/命名布局初值、策略互切、真实值普通/维护写、stale保旧/A-B切换、single-close与dirty保存/取消/丢弃均由真实DOM→正常IPC执行。普通/validation实际二进制仍分别54709f1e…/77700b47…，未用旧r4或旧r5产物替代。

本次WK资源归属有真实局限，不能把上述功能/退出pass当完整WebView全树覆盖pass。精确owned store lsof关联到Networking XPC PID58198/59403/59908（PPID1，非POSIX child），分别29/11/5个1Hz真实libproc样本、无采样/关联错误；WebContent/GPU未通过POSIX descendants或该store open-file路径建立归属，completeExpectedComponentAttribution=false，未归属费用null。逐PID ps/lstart/起止/来源、CPU/RSS/线程/FD/Mach ports样本与正常退出后lsof都在各run，不扫描其他应用或杀XPC；该覆盖限制已报协调，尚不越权据此删G0。A196–200 inventory分别f30fd734…/122ad079…/78817cd7…/b83d6d17…/4b5b41b6…；原件持久二次核SHA。


### 9.14 全树固定PID补证、严格终止门及阶段汇总

在已批既有测试面补充固定资源probe：本机SDK26.1公开WKWebView/ProcessPool头不提供PID getter；官方WebKit WKWebViewPrivate.h与WKWebView.mm的只读pid_t _webProcessIdentifier/_gpuProcessIdentifier返回当前page关联进程，非公开稳定API。Tauri2.11.3 with_webview主线程闭包内即借即用，respondsToSelector先核支持性，裸WKWebView指针不缓存/跨线程传递，普通product不编测试模块；Python只消费该Rust固定事件PID，与精确owned store/POSIX children按PID/时段union去重，无其他应用扫描/系统权限/杀XPC。官方URL/语义与本地SDK header SHA持久A202/resource-probe-source-notes.json。本机macOS15.7.7实际两个selector支持且返回真实WebContent/GPU，Networking另由owned store关联；不据上游main推定已安装实现版本。

首个probe test build A202 exit1（未直接链接serde_json），保留原失败；改为现有runtime value序列化接口，无依赖增量。A203/B0204的新N205–207功能与正常退出均pass，WebContent/GPU/Networking全部有逐PID真实样本；N207在desktop_exit后约66ms、Popen最终wait观察前对刚消失的PID采样得ESRCH，原complete=false/errors保留。A208/B0209再跑N210–212：三轮code0、正常关闭89.866/177.817/161.096ms，三类均已实际归属，N210/211无error/terminal；N212原collector对3次ESRCH按当次精确ps不存在记录terminal null样本，没有补0资源。该较宽实现随后集中收口为最终严格门：仅已记录正常close/desktop_exit、实际host code0及有界100ms内精确已关联PID不存在，才能终止分类；运行中意外消失/未确认仍error。另补逐PID正常关闭后ps元数据报告，不把共享系统XPC误称自有孤儿。

最终严格collector候选fcc051c532b24a67dd0f445f3b911f7d5f7f6d1bbb0b018ca0604eacac5f31be/B0214已closed；N215开始后桌面再次锁屏，实际CUA一次明确Mac locked，随后driver失败→原finally TERM PID75989 exit-15，五口空/无剩余owned PID。A213/215保留raw fail并另列environment_blocked，不写产品fail或正常close；没有S7 listener。唯一协调获Owner“已解锁，允许临时保持唤醒（推荐）”后管理一次caffeinate PID88421，最多60分钟、最迟2026-10-21 15:10:54+08结束，DEV不重复启动/终止该协调进程、不改持久配置。

A216对既有A210–212原始观测离线核验，绝不重标原run或称最新collector重跑成功：A212 closeConfirmed700071720182000→desktop_exit700071818967000→ESRCH700071858423000/866427000/871760000→当次ps exit1空→实际host code0 wait700071881278000，首ESRCH至host确认22.855ms，其余14.851/9.518ms，均≤100ms；原ps-before-hostwait与最终代码wait-then-ps顺序差异明示。原stdout/status/resources/association/commands各SHA和实际时间差全列A217，晚些精确已关联PID检查另列，不冒充当次5秒XPC退出。A216 inventory b1600f26…；A217 inventory84c8a31c…将普通dev195、core135完整33测试、native208/210–212+A216资源离线核验、protocol146按真实phase/source/组件影响汇总为当前DEV产品门；不称新--suite all命令。source差异仅test-only probe/collector，5headless+普通/validation及两desktop native共9相关产物逐SHA不变；R/native/core执行源相同，普通Mach-O不含native_webview_processes/ds_test_report，validation包含固定测试入口。产品/QA/Owner结论仍分层。

### 9.15 精确G0退役与清后验证

A217包含102旧成员详细迁移map：逐一核持久原件及当前旧源SHA，具体新成员SHA/consumer符号和验证证据，68项同字节迁入、34项适配/合并。原二image样本经A97实际新owner bytes等价，不拿expected伪造；vendor逐成员、受控8-file patch/ABI、client真实wire、五DAA模块、重写脚本/stdio/ABI probe均指具体consumer。retire_g0.py在核A217当前产品门、原r4-stop-snapshot及补充A17后，实际--execute退出0，精确删除102个已枚举旧成员、仅rmdir相应空目录。未删除历史plans/P4/A4/A5/失败原件、必要cache/build/profile或系统WebKit/用户/其他任务资源。

清后source成员由232降227（g0目录原即排除source candidate，另5个未注册旧runtime源退役）；正式Rust业务owner/配置SQLite/native adapter/fixtures/tests仍保留。dev0218清后cargo fmt/test exit0，完整33测试及真实双进程profile锁负例通过；dev0219普通pnpm tauri dev真实3IPC/新空v1库/独立store7647ad27-4cfa-4068-b842-bbb6ce1f32db/stopped无S7通过，debug6a2d82e8…与195同字节，watcher正常实验清理后五口空/无PID。随后清后最终native220正在自动build/B0/N1–N3，严格collector将实际执行；不提前记新三轮结果，也不要求Owner关窗。活动双语DS文档/CODE_INDEX说明已退役事实，历史§13/旧task引用保持原文。


### 9.16 清后严格原生实际通过及Owner布局纠偏

清后最终候选44500f2d0bac2061fe635ef85f4366c37d0a348b21a364beb09daf7962ee80e0/B0 dev0221，N1–N3 dev0222–0224全部实际pass，code0/正常关闭43.186、152.460、77.610ms，五口空/无剩余owned PID。三轮均实际归属并采样WebContent/GPU/Networking、completeExpectedComponentAttribution=true、errors0；N224实际3次ESRCH按最终严格门核正常close/desktop_exit→host wait code0→精确ps exit1空，保留原错误/时间与null末样本，不补0。A218–224均逐成员封存；5headless实际bin与A136/A146完全同SHA、普通product54709f1e…/validation134d2cc4…亦不因未注册旧文件退役而改变。cleanup dev0225实际pass、obsoletePresent=[]、五口空；该run已结束尚待最终封存。

在最终P5/handoff冻结前，Owner直接要求：“我看到ds的ui界面排布好像有的不合理，视觉上有些组件间隔都没有的。这里顺便整体调整一下。”唯一协调与PM只读核定属于既有r5 R27/K08/AC40/§5.1现有UI缺陷修复，无新Revision、功能、依赖或IPC。DEV保持唯一实现writer，DAA/CU只读；协调正在固定14194纯preview作实际六页视觉/DOM review，DEV暂不构建/监听或改源，待集中视觉清单后一次实施/受影响构建与自动native。上述清后原件及协议结果保留其候选标签，未提前写developer_handoff/QA或Owner接受；public P5尚未创建，不把旧UI证据当后续改版通过。

### 9.17 Owner 六页面布局修复与受影响验证

Owner明确要求“我看到ds的ui界面排布好像有的不合理，视觉上有些组件间隔都没有的。这里顺便整体调整一下。”主协调实际六页review及PM只读确认属于现r5 R27/K08/AC40/§5.1，未改spec/依赖/IPC/功能。集中修复DS自有ConsoleCard内容gap、自适应选择栏、值/连接完整技术列的表内横滚、日志筛选/事实分组、紧凑空态、同密度指标、弹窗表体/页脚、切页workspace滚动重置与主题token提示。DAA/CU/shared保持只读，原Rust业务owner/native/client未改。

- dev0226/B0227/N228：构建与B0通过；N1在instance_created后未取得错误收据，240s driver timeout，失败清理无残留，不计正常退出。原有按字符截取可能超UTF-8字节上限，新增异常辅助函数作用域又导致catch报告失败；这是DEV测试实现缺陷，后续以有界内联catch修正，原失败完整保留。
- dev0229/B0230/N231：原候选保留，明确owned PID28818按TERM失败收尾；exit-15、缺正常生命周期，不计Window.close通过。
- dev0232/B0233/N234：真实错误为import-cancel前dialog outside viewport。修正最大高度与默认底部margin叠加为完整margin:16px auto，保留断言并输出实际rect。
- dev0235/B0236/N237：完整走过导入/配置/布局命名/规则/应用/第二实例，先前viewport断言通过；dirty-close-save前真实footer gap失败。该App级弹窗在CuLayout外，缺主题作用域，已最小补aw-ui/data-aw-theme，关闭/dirty行为不变。dev0238起新候选受影响构建/B0/自动N，未提前计通过。

原生外窗960×640（实际WebView内容960×612），几何断言读真实DOM，不读Vue内部或mock IPC。浏览器preview像素另列来源，不冒充原生行为。228/231/234/237原件及新构建均逐成员SHA持久A5；不改旧run status/source标签。

- dev0238/B0239/N240–242：N1/N2实际正常关闭通过（40.142/91.861ms）；N3在dirty-cancel进入动画期间rect top=-1.4417px触发几何失败，未计通过。dev0243普通pnpm tauri dev真实空profile/SQLite/native/3IPC通过，watcher清理与正常Window.close分列。
- dev0244/B0245/N246–248：候选422ca7b8实际三轮通过，正常关闭上界63.240/146.482/71.602ms，三类WK组件均有真实归属/样本、resource errors0、PID/五端口清理。浏览器dev0249实际六页960×640，所有card gap12px/rootWidth960/切页scroll0，浅色概览/暗色中文策略/暗色英文日志JPEG原像素与NoBridge状态独立保存，preview SIGINT仅watcher清理。
- 根协调三张像素复核要求保留error/warning严重性；仅标题/边框消费既有danger/warning token。dev0252/B0253/N254在preview-confirm又观测到进入动画top=-3.9999px，原getAnimations子树枚举在WK未充分等待，原失败保留。现有test-only click改为全部可见dialog完整位于视口且连续两次真实rect稳定再操作；稳定越界仍超时失败，原阈值不变。dev0255起新候选受影响重证。

P5五文件此前仅候选草稿（dev0251完整原件已封存），最终UI重证完成前不视为developer_handoff。最终scope相对resume-003观察到ARCH-TOOL-001 spec缺失（前SHA71db7a41f089d0f7f5147a198b873a3eedd3a076ee96a666cf36f7ba6d0f6b0a），来源未确认foreign；DS未触达/恢复/认领，不改变DS pins。plans README pair为协调机械DS索引。

### 9.18 最终 Developer handoff（2026-10-21）

批准spec仍为67155fe4fca3068ef8e616dcf0ade69a5cdc614e7175a2f1ef4c6bf98f935419；最终正式227源码候选4d0c3ab8d614a8b0031bfd4e4a3dbc38f48892ecd07f7ddc97d3af773e0e70f0。最终B0 dev0256、native总run dev0255；N257/N258/N259实际通过，正常关闭上界67.580/124.716/116.385ms，全部真实Window.close/dirty确认/exit0/shutdown join、两类只读及产品IPC、三类WK组件实际归属与样本、resource errors0、owned PID与五端口无残留。getAnimations子树方法的N254失败保留；最终driver等待全部可见dialog矩形完整在视口且两次采样稳定，稳定越界仍有界失败，原几何阈值不改。

普通pnpm tauri dev dev0260在最终相同源上实际通过：新owned profile/store UUID、空本地SQLite v1七表、native加载、bootstrap/configuration/snapshot三真实IPC；watcher SIGINT清理不作为正常Window.close证明。生产release与非默认validation产物分别构建，普通产物拒测试参数exit2为预期；native三轮正常退出另证。dev0261实际browser/no-bridge双语主题960×640像素明确info与error标题/边框不同（暗色error rgb224/109/97），不再抹去严重性；preview原launcher exit-2为SIGINT清理，五端口/PID清空，不记原生证明。前版dev0249六页DOM gap12px/root960/scroll0与原像素保留原来源。

最终产品release SHA4f4ae7c24447466c649834bc8891f008798caa76e9ccd7fa1f5a55933d88ecd0；validation SHA171e74ff2b8ab56c72bc516d4c858b7a5108291958bca141e049b91e4f778eaf；普通debug SHA6a2d82e8bdfa2d4fe64bc9f57967306c71476c9af339fe4b6ad069caef324ab7。五个headless/client/native bin与A146协议候选87755d13原字节逐SHA一致，R业务/native/client源码未受UI/collector补丁影响；component-impact精确保留各run原source，未将A146改标签，也未声称重新执行新all CLI。原19矩阵38条case-run（W各三次reset，C02由C01同一原窗口覆盖，X01三次，X02严格同进程条件N/A），另K07 dev0147；core清后dev0218共33测通过。最终45AC与K01–K10 DEV覆盖映射在P5/evidence-index及A262；AC21独立QA/Owner最终验收仍待后续。

DEV命令/退出：各正式run的commands.jsonl保留pnpm build/tauri build、Cargo locked offline/CMake/ABI/clock/预算、源/锁/feature/file/otool/nm原结果；最终native与ordinary CLI exit0，正常生产拒测试参数exit2预期，原失败run exit1/-15等原样保留。文档/i18n静态检查exit0（19文档/94相对链接/123literal键及354+17+7双语键）、表格/围栏检查exit0、git diff --check exit0；git status对untracked真实输出归档，git diff --no-index /dev/null exit1代表预期真实差异而非验证失败。辅助最终清单首次dev0250因误假设dylib邻接路径exit1，按真实Cargo OUT_DIR修正，未改产品；一次内联Python缺UTF-8声明exit1在执行前失败，补声明后exit0。无应用/协议门被这些辅助错误倒填。

G0逐102成员已在持久原件/二次SHA与实际产品门后退役；A217原gate/逐文件map、实际unlink记录、A218/A219及后续清后B0/native均保留。最终map为每旧成员指定实际新consumer/path/symbol/验证证据，68原字节复制与34适配/合并，刷新当前target SHA且保留pre-retirement SHA。未删plans/P4/A4/A5/失败原件、DAA/CU/core或未知系统/用户资源。D内node_modules/gen及T5 role cache/build/profile/raw继续供fresh QA/后续另批联调；历史T3/T4/P0原包仍有审计依赖保留。新WebKit store按profile持久UUID隔离，实际路径/精确PID/采样在各N raw；旧默认DS WebKit路径归属未知，不删除。Private SPI只test-only macOS15.7.7资源取证，非公开稳定产品API；跨PID Mach/null、短命单样本CPU不可评估、采样峰非全寿命峰值、共享XPC不计owned orphan，均保留限制。C04 SO真实读回与FIONREAD/历史credit分列，不声称kernel物理16KiB硬限。协调caffeinate PID88421已到授权期限消失，DEV未续时；其后本轮原生实际通过，不推定未来桌面可用。

P5正式恰五JSON：input-manifest、delivery-source-manifest、protocol-baseline、evidence-index、resource-closeout；raw逐成员二次SHA持久A5，最终审计A262与独立receipt归档。唯一精确交接收据为T5/tmp/dev/developer-handoff-receipt.json，含工作树HEAD、全部实际source/lock/bin/P5/tasks/patch指纹与可直接运行命令。scope中ARCH-TOOL-001 spec缺失前SHA71db7a41…属来源未确认foreign并行差异，主协调已另只读定位；DS未恢复/认领/改pins。其余保护面未发现DEV越界修改，root/plans索引由协调/foreign记录，不归DEV。

Development现停止写入，交主协调启动新的fresh-context Verification。未写checklist/QA verdict或Owner验收；不包含DAA应用→SQLite联调、阶段C、真实设备、发布、安装器、系统注册/签名、Git refs/提交/推送或跨平台/L1–L5/8×16容量证明。

### 9.19 r5 QA1 F-r5-001 返工起点（纯交接材料）

独立Verification checklist SHA6010a27858b414b8d75d69abd04209dccfc4757e2f71110eec77a38130b1e0eb、A5/qa-run-0008 receipt SHA25fea17ad26c5baebb6e249c45605d175f80af1283dab5385d530d956778a674明确qa_failed：P5 delivery的nativeStage直接等于A255完整status，公开嵌入N257–259原始DOM步骤、WK probe与ps/资源观察，违反spec§5.2/R12/AC28，并阻断AC45交接。该结论不是产品功能失败，也不是完整产品QA通过。QA普通入口qa5独立build/startup通过；qa6 core/all被中断exit130，完整core结果、B0/N/协议均未完成，后续必须新fresh QA。完整r4与本次QA失败历史均保留。

旧97433e…handoff、原五P5字节、旧tasks及QA权威输入已在修改前持久封存并二次核SHA；本次仅P5五JSON与本tasks，不修改产品UI/Rust/native/协议/测试/配置/锁、spec或checklist，不构建/启窗/监听/重跑长矩阵。计划：逐对象审计→显式字段生成紧凑summary与A5 inventory/member SHA引用→全P5无raw/引用/45AC与10K/源码9bin保护静态检查→新精确handoff。正式227source/candidate4d0c3ab8及9实际bin起点逐SHA匹配。

### 9.20 F-r5-001 材料返工 Developer handoff

本次实际写面为P5原五JSON和本tasks；无产品UI/runtime/native/协议/测试/依赖/锁变更，也没有构建、窗口、S7监听或长矩阵运行。227源码/candidate4d0c3ab8d614a8b0031bfd4e4a3dbc38f48892ecd07f7ddc97d3af773e0e70f0、9个DEV实际binary/dylib、spec及QA checklist逐SHA保持。原QA1 qa_failed/F-r5-001与旧97433e…handoff及五P5 SHA身份不改写，均由A263修改前全字节快照和A262/QA8原件继续定位；此前DEV与QA结果不倒填成修后QA通过。

公开delivery/nativeStage改为显式字段projection：3轮result/exit、正常关闭上限、30个DOM断言步骤计数、50个资源probe计数、组件成功/不可用样本数量、错误/释放统计；每轮指向A255/A257–259 inventory及status member SHA。原始steps/details/DOM全文、WK原事件、PID/ps/1Hz记录均只留A5。protocol保留原38条case-run结果/时长和summary引用，C02与C01同窗口、X02条件N/A及K07单列；evidence-index保留45AC/10K DEV映射，latestNative改成公开summary JSON Pointer与原件引用。resource-closeout仅保留必要采样/资源归属总结、限制和原件引用，完成时点明确，不把旧关闭观察当返工时新观测。五对象全部审计，不仅删除单个nativeStage字段。

实际新生成helper为T5/tmp/dev/rebuild-compact-p5.py（完整源码随A265保存），从raw读取但只按显式允许字段生成公开对象；替代先前whole-status的私有prepare-final/finish helper，不新增repo脚本、依赖或测试框架。一次辅助生成在写P5前因协议原件实际为summary.json而非status.json退出1，A264保留失败helper及结果；按真实成员修正后exit0，无产品变化/原件修改。

DEV self-check：verify-compact-p5.py实际exit0，五文件精确集合/顶层schema、67个inventory/member SHA引用、2个公开JSON Pointer、45AC/10K、38case-run和所有映射run原件存在均核对。三个仅私有内存的负向projection（whole nativeStatus、latestNative原probe、resource原ps）全部被schema/raw字段检查拒绝，未写公开P5。文档/i18n静态实际exit0；git diff --check及JSON roundtrip/scope/hash检查均按真实命令保存。新材料收据与P5 SHA在T5/tmp/dev/developer-handoff-receipt.json及A265；旧97433e…输入和QA8 25fea…receipt、checklist6010…均保留精确身份。

两个patch明确命名：正式native/vendor/snap7-1.4.2/native.patch SHA7fafa44ddff8e14ee41c26252855a1b1aca40cf4dcb812db3d52080a53fff3d1；A256/vendor-computed-diff.patch SHA763ae1ed359139f7451dd0d84e1df5136561afa6b397a2283248c92b5729493b。QA1已独立确认八文件hunk同字节，差异仅排列/头路径；本次不修改任一patch或源码。

QA1普通入口qa5独立通过、qa6 core/all中断exit130且未完成结果、B0/N/协议not_run均继续有效；本次只交材料修正DEV自检，没有补做或替代任何独立QA。下一步由主协调启动新的fresh-context Verification；Owner final acceptance仍pending。历史原件、P4/A4/A5、G0退役事实及foreign Tool/Field Flow并行差异均未回退/删除。无新进程/端口/awake/邮件；原有T/A/cache/profile继续按既有依赖保留，DAA→SQLite联调另批、阶段C不开展。Development至此停止写入。

### 9.21 QA2 F-r5-002 返工起点

QA2 checklist SHA6d28825b59be65761a056a783dc73b4bcc44278a69ba1a7a82ab6aadfa1b4b5f、A14 receipt SHA3b2eb3f47ea05ef0c22c37b57f0a974ac0d5103998bbb0bd3ad71307f8ecb957明确qa_failed；F-r5-001已独立关闭（仅材料子项，不等于整版QA通过）。新F-r5-002为lifecycle_protocol.rs测试正例将role/runId固定dev，但正式QA core的DS_TEST_RUN_ROOT在profile/qa/normal/qa-0010；Manifest正确拒绝跨角色路径。QA fmt0，cargo test101（23pass/1fail，后续测试和跨进程锁未运行），B0/N/协议等仍未运行。原失败/QA1/r4历史不改写。

修改前已逐SHA核227source/candidate4d0c3ab8及九实际bin、旧a911d999…receipt/P5身份，持久保存旧测试/tasks/receipt/P5与QA2输入。本次仅该测试的角色中立样例构造，保留合法正例/parent escape/symlink/opposite-role负例；Manifest保护、产品/协议/依赖/锁均不改。按实际DEV owned profile运行正式完整core，记录全部测试与跨进程锁；仅测试变化不重开窗口或重跑长协议。Mac锁屏不解锁、不启/续awake；源变化形成新candidate，原native/协议来源不重标。

### 9.22 F-r5-002 测试修复 Developer handoff

唯一源码变化为runtime/tests/lifecycle_protocol.rs内该Manifest用例：从实际DS_TEST_RUN_ROOT相对于固定owned profile根的首层取得dev/qa角色，合法role/runId据此构造；profile parent-escape使用该实际root拼接，跨角色负例明确切为opposite role。Manifest::read生产/测试保护函数原字节未动，原合法正例、路径ParentDir、profile ParentDir、symlink、role mismatch及未打开store断言均保留，没有skip/ignore/降门槛。相同测试相关用法搜索没有另一处固定dev正例；DEV未写QA路径或使用QA target，QA分支本轮只作源码审查，必须由新fresh QA实际执行。

修后正式命令为/usr/bin/python3 -B scripts/run_validation.py --project-root <正式D> --run-root <T5> --role dev --suite core（dev0268），实际外层exit0：cargo fmt --check0、cargo test --offline --locked --features native-s7,test-automation --lib --tests0，共33测（logging5/apply5/clock1/store4/FFI2/layout3/lifecycle4/owner3/source2/typed4），0failed/ignored。随后正式core自带debug ds-test-host构建及真实双进程profile锁验证成功：第一owner正常quit/exit0，第二owner被profile_in_use拒绝exit1且DB字节不变，独占读回成功，五固定端口均空。第二owner的exit1是预期负例，不混为失败。角色自有profile/cache/target路径、原commands/stdout/stderr/lock资源在A268，未触DAA/SQLite联调或GUI。

一次辅助patch因cwd已为D而使用重复路径前缀退出1、未写源码，file-only rustfmt同样路径错误exit1；随后dev0267是修前DEV-role完整core baseline通过，不能作为修复证明。修正实际文件路径后仅对该文件rustfmt，dev0268为修后真实33测/锁证据。A266先保存旧a911…receipt/P5/tasks/测试与QA2输入，A267/268原run及A269组件/diff/残留负例manifest原件均持久封存。私有P5 helper曾误以为QA14含checklist而exit1，写公开前发生，A270保留；实际checklist在QA13且SHA6d288…，修正引用后exit0。所有辅助失败原样保留，不改产品expected或QA结论。

最终227source候选9f2f4f7c299d93fdb9f2950e4be7979ca43c3ec21f1fd0ea011de9ac06edfd42；其余226源码、22文档、3锁、9交付binary/dylib逐SHA同旧4d0c3ab8交接。core仅编译必要测试/debug宿主；未重建九个未受影响交付产物。A269/component-impact明确单测试before/after SHA及九bin实际字节，原A146协议87755d13、N257–259/普通入口的4d0c3ab8等原始source标签不重标。P5当前source manifest更新测试hash；旧B0明确属于4d0c3ab8，仅按组件影响保留，未声称运行新B0/窗口/长协议。G0102成员已退役事实/原件/旧迁移map不变，没有再删除。

P5仍恰五紧凑JSON，F-r5-001机制与QA2独立关闭结论保持；新core只放结果/33计数及A268成员引用，单测组件变化及QA2失败历史由A269/QA13/QA14引用定位，不嵌DOM/PID/ps/原日志。45AC/10K、38case摘要及C02同C01窗口/X02条件N/A/K07单列保持原DEV证据，更新当前测试相关映射。静态紧凑schema/raw注入负例/原件member+inventory SHA/公开Pointer/编号集合/文档i18n与diff保护检查均真实exit0，命令与helper源码随A271保存。精确新receipt仍为T5/tmp/dev/developer-handoff-receipt.json，固定新source/tasks/P5/原九bin/两个明确patch对象、A269影响及旧输入身份。

QA2的qa_failed/F-r5-002、23pass/1fail及后续not_run原事实继续保留；F-r5-001仅材料子项closed，不扩成整版QA通过。DEV core成功不代替QA实际role、独立B0/全部协议/native/Owner验收。Mac锁屏期间本轮未开窗口、解锁或启/续caffeinate，没有新监听/外发邮件/提交推送；DEV正常profile锁进程已退出，cache/build/profile/raw依旧供后续核验保留，未知/foreign任务不回退。Development完成本精确交接后停止写入，由主协调启动全新的fresh Verification；Owner final acceptance pending，DAA–DS SQLite另批、阶段C排除。

### 9.23 QA3 F-r5-003 返工起点

QA3 checklist b1d6d7c4…及A55 receipt e3019ab7…明确qa_failed，F1/F2已独立关闭；新F3为真实同源同UUID重导DB71→72后，未重新confirm_points仍compile/apply成功。A54包含真实helper/SQLite/八revision/资源原件，未start监听。QA3 C01/C02中断exit130不继承通过，完整QA与Owner终验仍pending。修改前已核227source/candidate9f2f4f7c、九交付产物与spec，并持久保存本轮起点/P5/旧交接/QA3输入。

本次仅修Rust配置/导入链物理语义变化的初值和策略确认失效，保留稳定身份/候选值及未改DB确认；增加实际导入—布局命名—compile/apply回归，完整core及必要普通/native/B0/原协议矩阵按新候选重证。无新UI、依赖、schema、Manifest放宽或额外像素循环；旧失败和原source标签不改。

- 首轮冻结candidate078611c3b2cbcd9babcbf6eda027666515e2e5e5c362f0ce0f10bc5180e4e097，仅configuration.rs及既有source_import.rs测试变更。按DB号/长度/有序点UUID、类型、结构路径、manual与byte/bit一次比较物理上下文，普通prepare恢复旧stamp前及统一preview保存票据前均清受影响DB的点确认；来源版本/注释/显示名不参与物理比较。既有初值/策略有效签名继续检查，无schema或自动转换。
- dev0273正式完整core实际exit0，fmt0/cargo test0，共34测试（新增真实App/import/layout/naming/compile/apply回归）；跨进程profile锁第一owner exit0，第二owner预期profile_in_use/exit1、DB字节不变、五口空。新增回归实证DB71→72后未confirm_points则compile及apply preview拒绝、原owner仍71，显式确认后装载72；同源同绑定unchanged、显示兼容、长度/byte地址/新增结构失效与未选DB完整保持均通过。原类型变化回归继续通过。A273逐234成员SHA持久封存。
- dev0274实际两种desktop构建成功，普通产品拒测试参数exit2预期；B0 dev0275新候选closed后，自动N1 dev0276真实正常关闭通过。N2/N3及普通dev/完整原协议矩阵仍按本轮实际进度继续，不以旧源冒充。

### 9.24 F-r5-003 最小修复 Developer handoff

最终227source候选306a09d5317931482a59f45da5eafcb9d3ee739199799f475ade1891fb0b00b4，只改runtime/src/services/configuration.rs及既有runtime/tests/source_import.rs。每DB一次比较号/长度/有序点UUID、类型、结构路径、manual、byte/bit：普通prepare恢复stamp前、import/layout编辑预览生成票据前清受影响DB点的初值/策略确认，保留UUID/旧候选值；未改DB与显示/来源元数据兼容。既有typed、有效初值/策略签名、布局、Manifest保护不放宽，无schema/依赖/UI/native/protocol变更。apply仍消费完整compile过的不可变历史revision；不能把当前draft的物理差异当作对历史revision重新编辑。

新增一条实际App服务回归覆盖导入→布局/命名→确认→真实apply DB71，再同字节/lineage/UUID重导72：未confirm_points时compile及apply preview阻断，owner仍71；显式确认后加载72。另核普通保存的号/长度/byte地址变化、结构新增叶、原有类型变化、未选DB全值保持、同源同绑定unchanged及显示兼容；最后真实回滚已确认旧revision到DB71成功。所有root取DS_TEST_RUN_ROOT，不固定DEV角色。冻结前发现apply也用通用preview，已将失效限定编辑入口并补回滚回归；中间078611c3/A273–279原件保留，不作为最终候选验证。A279在后续改源前已结束，未混入源代次。

最终dev0280正式core exit0：fmt0/test0共34测、0failed/ignored，真实profile锁owner exit0/第二owner预期exit1且DB不变/独占读回。dev0281构建普通和非默认validation桌面、普通拒测试参数exit2预期；新B0 dev0282 closed，实际ABI/0与37返回/clock/预算原件完整，之后才监听。N1 dev0283、N2 dev0284通过；N3 dev0285在dirty-cancel成功后既有dialog rect稳定等待超时，失败TERM收尾，不算正常关闭。相同source/binary/profile、无改UI/driver/断言的定向重试N3 dev0286通过。三实际通过轮正常关闭上界56.380/50.576/94.788ms，真实Window.close/IPC/SQLite/S7及完整WK归属/资源样本、join/owned PID/五口释放见各raw；不是三次连续无失败，也未声称已定位285超时根因。未追加像素/主题循环，未改前端/CU/i18n/图标逐SHA关联原A261像素。

普通pnpm tauri dev dev0287实际exit0，隔离空owned SQLite v1/持久WebView UUID store/三只读IPC/native，watcher清理不冒充正常Window.close。最终协议总run dev0288保持相同306a source/实际新产物，K07 dev0289真实通用五DB与A/B隔离通过；原19项共38条case-run全部实际完成（W01–09每例3次独立reset；C02同C01原16会话30s预热+300s测量窗口；X01三次；X02严格同进程分支条件N/A）。C/D/X原时长/offered/阈值、真实ManagedS7/拒写/公平/资源与退出保持，未降样或以旧源/binary代测。完整逐case结果与summary SHA见P5 protocol-baseline，原commands/wire/events/1Hz/日志/成员inventory持久A5，QA3 C01/C02 exit130历史仍不计pass。

组件/九实际bin/三锁/234只读固定输入与两文件patch逐SHA在本轮component-impact及精确receipt。其余225源码和22文档原字节不变；四根DS索引由协调机械写，foreign并行差异只记scope，不回退/恢复。实际self-check为正式core/build/native/protocol、P5 exact5/紧凑schema与原件SHA/45AC10K映射/JSON指针/源码锁bin保护、git diff --check。git diff --no-index两补丁exit1是预期有差异；旧失败及285失败原样保留。私有封存helper首次重复seal已有immutable archive被保护拒绝exit1，在公开写前发生；核既有inventory后完成，失败helper/结果随A328保留，原件不改。P5只显式summary与A5 inventory/member SHA引用，无raw DOM/PID/ps/原事件嵌套；原F1机制与QA独立关闭不重开。未变文档/i18n/像素不机械重复测试。

旧948dd826…receipt/P5与QA3 checklist b1d6d7c4…/A55 e3019ab7…及A54真实F3原件都保留身份。F1/F2独立closed、QA1/2/3 qa_failed历史不改，DEV修复结果不授QA或Owner验收。新精确receipt仍为T5/tmp/dev/developer-handoff-receipt.json，固定source/九bin/tasks/P5/patch/实际run来源及限制；本轮生成/静态检查helper和原命令随最终DEV archive保存。

收尾无owned DEV产品/test/reference/launcher、五固定端口空；T5 role cache/build/profile/raw、新owned WK store、历史T3/T4/P0与A4/A5保留供fresh QA/另批联调，不删未知系统/共享资源。旧协调caffeinate已到期，DEV未启/续awake或改系统设置；实际本轮桌面可用，不推定以后环境。G0已退役102成员历史不再删除/重写。Development至此停止写入，交唯一主协调启动全新fresh Verification；Owner final acceptance pending，DAA→SQLite另批，StageC/真实设备/安装发布/Git提交推送不开展。
