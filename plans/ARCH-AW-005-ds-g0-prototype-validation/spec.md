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
