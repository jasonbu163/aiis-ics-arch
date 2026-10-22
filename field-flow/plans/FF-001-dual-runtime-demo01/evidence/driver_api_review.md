# FF-001 r1 候选驱动预检：Development 事实

日期：2026-10-21。此附件是 Development 预检及 blocker 证据，不是 runtime 实施、自检完成或 QA verdict。只使用批准的固定 loopback 与新建私有环境，未修改第三方代码。

## Python 3.0.0 公开配置入口

实际安装：`python-snap7==3.0.0`，CPython 3.11.12，独立环境 `/private/tmp/ff-001-r1-20261021-dev/python-preflight-venv/`。源码 SHA256：

- `snap7/client.py`：`0d4ca7c3f178fe3484b8282b61635c14d2edf1ef925b1761e2f5b2865251c2ff`
- `snap7/connection.py`：`fd0f1dde0786bb66709bdec4f46d5f63bb1562b47893feb97056a824a5e62b8b`

按当前安装制品读取的调用链及行号：

| 入口/调用点 | 核查事实 |
| --- | --- |
| `Client.__init__(lib_location=None, **kwargs)`，client.py:59–109 | 构造说明将 lib_location/kwargs 定义为兼容忽略项，没有 timeout/transport 注入处理。实际传入 timeout=0.5、connection_timeout=0.5，连接后 socket timeout 仍为 5.0 秒。 |
| `Client.connect(address, rack, slot, tcp_port=102)`，client.py:152–199 | 无 timeout/connection/transport 参数；179 行重新创建 ISOTCPConnection，183 行无参调用其 connect()，然后调用私有 `_setup_communication()`。预先配置 `Client.connection` 会被替换。 |
| `Client.set_connection_params(address, local_tsap, remote_tsap)`，client.py:1774–1785 | 只设置地址与 TSAP，无 timeout/transport。 |
| `Client.set_param(param,value)`，client.py:1847–1868 | 除 RemotePort 已连接限制、PDURequest 特判，写入 `_params` 并返回；没有将 PingTimeout/SendTimeout/RecvTimeout 传给 socket 的调用点。get_param 的成功回读不代表参数生效。 |
| `ISOTCPConnection.connect(timeout=5.0)`，connection.py:96–120 | 此低层方法本身暴露 timeout；但 Client 无配置接入点且总是重建对象、无参调用。自己装配 transport 并重做 Client 初始化/协商需要触及私有方法/内部连接构造或自行编排协议；本次未执行，不将它当成批准范围内的公开 Client 适配。 |
| `ISOTCPConnection._tcp_connect()`，connection.py:198–207 | 实际 socket.settimeout(self.timeout)；来自上述无参 connect 的5.0，而非 Client 参数。 |
| `_recv_exact()`，connection.py:386–415 | 每次 recv 使用 socket 超时，分段接收循环没有共享 monotonic 总 deadline；单个帧的 header/body 又分别调用该函数。 |
| `Client._send_receive(request,max_stale_retries=3)`，client.py:117–150 | request 只 send 一次；随后最多4次 receive/parse/序号校验。stale 重试是 receive，不是再次发送 WriteVar；各次接收没有同一总 deadline。 |
| `Client.write_area()`，client.py:389–447 | 两字节 INT 小于 PDU 容量，只创建一次请求并进入 _send_receive，之后检查正写响应。大块分包不属于本 r1 INT 能力。 |

结论：已核查公开 Client 构造、connect、set_param、set_connection_params 与低层连接入口，未发现无需修改/替换候选或使用内部构造即可让该 Client 满足 r1 整体同步 connect/IO deadline 的公开配置。该结论不声称所有可能定制都不可能；它明确排除把自建连接/私有协商/猴补当作现有公开配置路径。替换候选或授权额外适配方式须由 PM 决定新 Revision，不由 Development 降低预算。

## 可复现协议证据

全部通过显式获批 sandbox escalation 执行固定 loopback，非真实 PLC。

| 探针 | 实际过程/结果 | exit |
| --- | --- | --- |
| `python_timeout_probe.py` | Client 的三个 timeout 参数设为500 ms；32102 静默 peer 实收22字节COTP。connect 5003 ms 后 S7TimeoutError，超3000+500 ms；peer thread 真 join，32102可重新bind/listen。 | 1：合同预算断言失败 |
| `python_io_probe.py`（默认 segmented_ack） | 32103 自身 python-snap7 Server，32102透传TPKT。Server已产生正ACK后，仅把原ACK分成header/body各延迟3秒送出。db_write 6019 ms 返回0；请求/ACK PDU ref均0002，header error0000、WriteVar status FF，实际write_requests=1；server内存只从offset4写入002A，邻接A5保持。 | 1：5000+500 ms硬预算断言失败 |
| `python_io_probe.py segmented_read` | 一次正常写后，对真实读响应作同样3+3秒分段。db_read 6018 ms 返回002A；实际write_requests=1/read_requests=1。输出中 `ack_status_hex=2a` 在此模式是原读响应最后一个数据字节，不是WriteVar状态；不得误作协议状态判定。 | 1：5000+500 ms硬预算断言失败 |
| `python_io_probe.py stale_ack` | 对一次真实WriteVar，先转发3个先前真实Setup响应，再转发匹配写ACK；不改帧字节。client记录3次stale receive，174 ms完成，write_requests=1、session=1、内存002A。 | 0：有限接收重试、不重复发送的这条路径成立；不等于总期限成立 |
| Rust `ff001-driver-preflight` | 自身Cargo锁、native rust-snap71.142.2实际构建。31102静默peer实收22字节COTP；参数500ms时connect实际500ms返回错误。peer thread真join、31102重bind成功。 | 0：仅此连接预检成立 |

Python三次S7协议测试均实际 join proxy thread；server子进程自然 exit0，退出前 remaining_threads=[]，父进程 join 后32102/32103均可bind/listen。原样stderr保留：Server在Client正常COTP disconnect时打印`Expected COTP DT, got 0x80`，未隐去该库诊断；它没有阻止本次自然退出。未使用强杀、未换端口、未杀占用者。

Rust尚未做读写ACK、native server退出或完整runtime验证；Python尚未安装其他候选。不能用Rust此项预检替Python，也不能用Python的Server作为Rust依赖。

## 命令与环境

从交付仓库根执行（本附件中的Python为任务独立3.11环境）：

```bash
UV_CACHE_DIR=/private/tmp/ff-001-r1-20261021-dev/uv-cache uv venv --python 3.11 --no-python-downloads /private/tmp/ff-001-r1-20261021-dev/python-preflight-venv
UV_CACHE_DIR=/private/tmp/ff-001-r1-20261021-dev/uv-cache uv pip install --python /private/tmp/ff-001-r1-20261021-dev/python-preflight-venv/bin/python python-snap7==3.0.0
/private/tmp/ff-001-r1-20261021-dev/python-preflight-venv/bin/python field-flow/plans/FF-001-dual-runtime-demo01/evidence/python_timeout_probe.py
/private/tmp/ff-001-r1-20261021-dev/python-preflight-venv/bin/python field-flow/plans/FF-001-dual-runtime-demo01/evidence/python_io_probe.py
/private/tmp/ff-001-r1-20261021-dev/python-preflight-venv/bin/python field-flow/plans/FF-001-dual-runtime-demo01/evidence/python_io_probe.py segmented_read
/private/tmp/ff-001-r1-20261021-dev/python-preflight-venv/bin/python field-flow/plans/FF-001-dual-runtime-demo01/evidence/python_io_probe.py stale_ack
cargo generate-lockfile --offline --manifest-path /private/tmp/ff-001-r1-20261021-dev/rust-driver-preflight/Cargo.toml
cargo build --locked --offline --manifest-path /private/tmp/ff-001-r1-20261021-dev/rust-driver-preflight/Cargo.toml
/private/tmp/ff-001-r1-20261021-dev/rust-driver-preflight/target/debug/ff001-driver-preflight
```

首次 pip 下载在 sandbox 因 DNS 失败，获准 escalation 后下载/安装 exit0；没有全局安装。首次32102绑定在 sandbox PermissionError exit1，获准 escalation 后才完成真实测试；该权限失败不是驱动能力结果。现有Python定位在任务私有UV_CACHE_DIR下成功，解释器为 `/Users/jason/.local/share/uv/python/cpython-3.11.12-macos-aarch64-none/bin/python3.11`；未下载/切换解释器。Rust1.89.0/Cargo1.89.0，独立probe锁解析43包，cargo build exit0；不表示正式runtime锁或完整工程已创建。

证据脚本、Cargo probe清单/锁/源码、真实stdout/stderr均保存在本目录。源码和证据manifest固定于交接时；临时环境只用于复现并可在PM决定后由协调器审计回收。

## 协调器追加要求：Rust 原生分段 ACK 有限预检

在上文初次结论之后，主协调器因Python分段接收已突破总预算，明确要求核查Rust/native同类风险。本次仅扩展原临时probe，不创建正式runtime：

| 命令参数 | 真实结果 | exit |
| --- | --- | --- |
| `ff001-driver-preflight native_standard` | 自身Rust native S7Server子进程31103 + 自身TPKT proxy31102；connect3ms、write1ms、read1ms，单次WriteVar匹配ACK `pdu_ref=0100/header_error=0000/status=FF`，内存offset4为002A、其余A5。 | 0 |
| `ff001-driver-preflight native_split` | connect3ms；SendTimeout/RecvTimeout均5000ms，原生Server先已产生完整正ACK。proxy将原ACK的7字节TPKT+COTP header延迟3s发送，再等3s发送余下body。db_write6020ms仍返回成功、actualWriteVar=1，随后read1ms返回正确16字节。预算断言在资源释放后真实失败。 | 101 |

两次proxy thread均实际join；Client disconnect后请求native server退出，父进程wait得到exit0；注册buffer保持到native Server drop完成，再输出真实内存、退出。31102/31103均重新bind成功。没有强杀、兄弟语言服务或端口切换。

实际native调用链（rust-snap71.142.2自身native源码）：`s7_isotcp.cpp:368–415` 的isoRecvFragment先RecvPacket(header7)，再RecvPacket(data)；`snap_msgsock.cpp:580–600` 每个RecvPacket重新WaitForData(Size,RecvTimeout)，`238–264` 每次重建Elapsed。因此将某个底层参数直接设为整次IO预算不能保证总预算。`s7_isotcp.h:37` 默认MaxIsoFragments=64，isoRecvPDU还有分片循环；不能只因本次单帧有两段就未经审计将参数简单除2作为完整证明。

这项结果不证明native全部公开适配都不可行；更保守地划分底层阶段预算，需先确定connect/send/recv/fragment所有有限调用上界并验证真实错误/终止，不能用异步waiter取消代替driver终止。当前没有实现这种适配或宣称它满足合同；交给PM决定后续精确范围。仅更换Python候选为同类native包装，并不能自动消除这里实测的问题。

复现源码：把`rust_native_probe.rs`作为临时crate的`src/main.rs`，`rust_native_silent.rs`作为`src/silent.rs`，本目录`rust_probe.Cargo.toml/lock`分别作为`Cargo.toml/lock`，按上文locked build执行上述参数。原先独立`rust_timeout_probe.rs`仍保存最初静默COTP预检源码，不覆盖历史。新增probe执行前已`cargo fmt`、`cargo build --locked --offline` exit0；随后`cargo fmt --check` exit0。

最终只读资源盘点：Python环境964K、uv-cache480K、Rust临时probe97M（`du -sh`的当前磁盘占用，缓存硬链接会影响合计）；无本任务listener。保留原因：失败复核、后续PM/Owner gate与可复现环境；不把临时环境作为唯一证据。重要源码/锁/stdout/stderr已持久保存。

## 再次追加：仅公开参数的保守阶段预算是否足够

主协调器明确要求：不能把整次call budget等值映射到每个内部阶段，也不能机械除2；需只读审计严格次数上界，并做最小公开参数分配观测。本次没有修改任何第三方、协议栈或candidate版本。

### 有限的正常阶段与未受控路径

| 路径 | 只读界定 |
| --- | --- |
| macOS/POSIX TCP connect | snap_msgsock.cpp:340–425采用非阻塞connect + select(PingTimeout)，成功的EINPROGRESS路径在382行恢复原flags；无0超时。不能把PingTimeout当整个S7连接预算。 |
| COTP连接握手 | s7_isotcp.cpp:180–247一次SendPacket、两个RecvPacket（TPKT4及剩余COTP）。 |
| S7协商 | s7_peer.cpp:109–122中isoConnect后还执行一次NegotiatePDULength；其中一次isoExchangeBuffer。 |
| INT一次读/写 | s7_micro_client.cpp:51–157/159–约290：在正常协商容量足够时2字节只有一次slice，一次isoExchangeBuffer。不能将任意不可信/异常PDULength默认当作正常容量；这次probe使用真实native server协商。 |
| 一次isoExchangeBuffer | 一次SendPacket和一次isoRecvPDU；isoRecvPDU最多64个COTP片段，每片最多header7/data两个RecvPacket，正常有限接收阶段最多128次。不是仅两个阶段。 |
| RecvPacket本体 | snap_msgsock.cpp:580–600调用WaitForData(Size,RecvTimeout)，后者238–264以自己的Elapsed等待完整Size；recv本身没有partial重收循环。超时会转入Purge。 |
| **Purge未受控循环** | **snap_msgsock.cpp:160–174：CanRead(0)后do recv(512) while(Read==512)，无deadline、无次数上限。** 当恰读512字节且peer保持连接不再发字节，恢复blocking的socket的下一recv可以阻塞；即使socket仍非阻塞，peer持续供应512字节也没有有限次数界。 |
| Purge可达位置 | RecvPacket超时595行、PeekPacket错误618行、isoRecvPDU失败486行、isoConnect失败约238行、DestroySocket在211行调用。它包括错误恢复和disconnect/析构，不只额外诊断函数。 |
| socket系统超时 | CreateSocket/SetSocketOptions只设TCP_NODELAY/SO_KEEPALIVE；源码没有SO_RCVTIMEO或SO_SNDTIMEO。Ping/Send/Recv参数不会给Purge内raw recv加总期限。SendPacket还在CanWrite(SendTimeout)后直接send，未提供独立系统调用总deadline。 |

例如在普通有限阶段中，按64片/128次接收给每阶段更小值，理论上可为正常路径分配预算（单次IO一个send+128recv）。但所有这些求和都不能覆盖无界Purge，因此不能把正常阶段数之和作为整个driver/退出的严格上界。实际错误路径未被公开参数封闭；这不是因为本次probe的配置数值选择太大才成立。

本结论是源码可达性审计，不假称已经实际执行一个永不返回的Purge场景。本轮没有创建故意挂死且需强杀的额外server/进程，也没有以异步waiter超时冒充同步调用终止。

### 最小公开参数分配实测

`ff001-driver-preflight native_split_budgeted`：保持同一真实native server/proxy及3s+3s分段正ACK，只将Client公开SendTimeout/RecvTimeout从5000改为10ms。connect仍用先前3000ms参数（正常3ms），本probe没有宣称connect全路径已适配。

真实结果：write10ms错误返回、后续read10ms错误返回；Server已经实际应用42且产生匹配正ACK，actualWriteVar=1。等待proxy自然结束、Client断开、native server自然exit0并父wait、31102/31103重bind成功。probe exit0只断言这一条路径在较小参数下及时失败，**不是完整R04通过**。未将失败写调用当confirmed；尚无runtime/SQLite状态实现。原native_split的6020ms/exit101仍保留。

第三方native文件SHA256：

- snap_msgsock.cpp：`bded0cc9e642aaff22b8a16e0bfae5f5eca7e346769ec6f8ba582b00bae9ba51`
- s7_isotcp.cpp：`7c06fa33f0e34afe88962322c5fa946f3072ceeb1a0cc5d2cbdb71c7ac43e6b7`
- s7_isotcp.h：`313c5167f3769367b38073c62da6d1a1c49b63a7016016caf3743666639a2c5f`
- s7_micro_client.cpp：`e00ff916ce42660a5b8137bc681471b7b966370dbb3d71f701f7ee03a8b5c141`

Development结论：对当前锁定rust-snap71.142.2，仅公开Ping/Send/Recv参数不能证明完整同步call及断开/析构总期限。已有正常协议/失败观测，且找到明确未受控循环；不据此自行修第三方/换库/隔离进程改owner合同。PM下一Revision需要同时处理Rust native和Python候选的预算实现方案，不能只换Python就称全部解决。
