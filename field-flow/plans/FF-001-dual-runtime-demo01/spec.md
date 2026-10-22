Task ID: FF-001
Revision: r3
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: pending exact Human Owner scope approval of FF-001 r3 bounded Rust S7 INT PDU adapter; r2 dev_blocked evidence retained; no Development continuation or QA
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 两个独立语言基础运行时及 demo01 HTTP GET 到 S7 INT 写入的本地合成闭环
Owner: Field Flow
Acceptance Chain Reference: FF-001 r3 精确范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
Related Task: ARCH-TOOL-001

# FF-001：双语言基础运行时与 demo01 本地闭环

## 1. 当前授权、目标与事实

当前为 **FF-001 r3 draft**，精确Human Owner范围批准pending。Human Owner于2026-10-21真实批准“批准 ff001 r2”；批准后完整r2文件107258字节、SHA256=`1bd11a1dd3ef1dd69ac67943c2a74d0c446f525d4a2378c8cbbb2f05a846a522`，包括其原r1全文、批准及自检历史，全部无损封存在[文末r2历史](#r2-approved-history)。r1/r2批准不覆盖本r3新增的Rust S7请求编码、原始响应校验及FFI缓冲责任。

当前[Development tasks](tasks.md)为r2/`dev_blocked`，PM只读时SHA256=`ce9dfe615dbfc69c2e0dccf00178d7bcb8856ea51458e4e2d405c3a55389d0e9`。真实[有限复核](evidence/r2-dev/stale-reference-review.md)、[报文与运行结果](evidence/r2-dev/stale-reference-evidence.json)、[状态三表导出](evidence/r2-dev/stale-reference-state-export.json)已持久化；它们证明当前高层driver不能满足原T3，不是QA或实施完成：

- 真实ReadVar请求reference为0100，native响应0100，代理只改TPKT绝对byte12后实发0101；driver仍返回good/-23131。
- 同会话WriteVar请求0200，native正ACK0200，实发0201；业务iteration返回Ok且SQLite confirmed=1。actualWriteVar=1、native内存42、停止后独立读回002A且邻接A5。失败是未匹配ACK被确认为成功；IPC request_id/generation匹配不能代替S7关联。
- `stale_reference_probe`实际exit101；driver PID11963自然结束、父wait/reap，fixture自然exit0及线程join，31102/31103/31880真实rebind。状态/日志如实保留，不能用正常资源退出抵消业务失败。

r2 Rust已真实编译/build成功，部分INT、去重、三流同会话和慢HTTP并发成立；split/slow由父约4617ms实际回收driver属于fault_cleanup。完整AC01–AC14、独立复制、父/子崩溃/queued-stop/审计容量等仍有未验项，Python目录尚未创建；逐项缺口仅以tasks为准，不把局部成功汇总成全AC通过。原24份r1证据/manifest保持，manifest SHA256仍为`d046e373c875c236ef1ad9678e1ba6dd9141d5667c92be2bd66ed70acbbd8770`；r1预算失败、r2平台中断和所有失败日志不覆盖。

**r3具体选择：保留精确rust-snap7=1.142.2及python-snap7=3.0.0、原driver子进程和fixture；仅Rust运行时两个字节DB INT ReadVar/WriteVar改经公开iso_exchange_buffer，由小型私有adapter构造请求并严格验证原始S7 ACK。** R14冻结边界、错误语义及批准后首个有界预检。无vendor/第三方补丁、新库试装或生产监听代理；Python不主动换库/改栈。原业务、预算、队列、状态、unknown、正常/故障退出合同继续成立，AC01–AC14原文保留，新增AC15验证关联缺口。

本轮仅PM规格及协调器机械导航，不续Development。当前源码和失败状态保留；r3精确批准前不实现/运行新adapter。r2批准真实有效但不授权本次新增低层协议责任，不能先试做后补批准。

关联[ARCH-TOOL-001 r2](../ARCH-TOOL-001-field-flow-runner/spec.md)是独立讨论基线，Classification仍root，无Parent Task ID；全文件SHA256=`049574ad8fb9e43fcf7073aa217410b28cc21da7100500a28f9887510aac64ae`不变。根AGENTS、双语README/PLAN、FF导航、pm.toml及canonical workflow继续适用。

## 2. 两阶段写入边界

### 2.1 本轮PM r3 draft

- PM唯一写入`field-flow/plans/FF-001-dual-runtime-demo01/spec.md`；完整批准后r2及其中r1历史在同文件无损归档，不创建第二bundle。
- 主协调器只机械同步必要FF/根导航，区分r3 draft与真实r2 dev_blocked。tasks、checklist、源码、锁、依赖、fixture和状态均不归本轮PM写入。
- PM只读当前bundle/官方registry原包源码和文档，做文档断言；不安装候选、编译/执行项目代码、运行协议、建库/schema或创建监听器。
- r3批准后原Development在同bundle先执行R14预检gate，再续完整Rust矩阵和Python同例；如实保留r1/r2历史和证据。未获批准不更新tasks为r3，未developer_handoff不创建Verification/checklist。

### 2.2 精确 r3 获批后的 Development allowlist

| 面 | 允许路径与限制 |
| --- | --- |
| Rust 独立工程 | `field-flow/field-flow-rust/**`：自身 `Cargo.toml`/`Cargo.lock`、少量源码、typed YAML 示例、测试/fixture、locale、`.gitignore`、README/PLAN/catalog 双语与自身 `CODE_INDEX.md`。不得有指向父级/兄弟源码的 path dependency、运行配置或必需服务。 |
| Python 独立工程 | `field-flow/field-flow-python/**`：自身 `pyproject.toml`/`uv.lock`、包入口和源码、typed YAML 示例、测试/fixture、locale、`.gitignore`、README/PLAN/catalog 双语与自身 `CODE_INDEX.md`；自身 `.venv` 和状态/日志均不提交。 |
| 本任务角色事实 | Development 仅创建/维护 `field-flow/plans/FF-001-dual-runtime-demo01/tasks.md`；fresh-context Verification 在 `developer_handoff` 后仅创建/维护 `checklist.md`；有真实证据时才增加本 bundle 的 `evidence/` 附件。PM 继续独占本 spec。 |
| 必要导航 | 上述 FF 六份导航，以及根 `README.md`/`README.zh-CN.md`、`PLAN.md`/`PLAN.zh-CN.md`、`plans/README.md`/`plans/README.zh-CN.md`、`CODE_INDEX.md`，仅 FF 实际入口、真实结构、聚合状态与下一 gate；由主协调器机械同步，不重写其他任务事实。 |
| 私有临时资源 | 未来本任务自建的 `/private/tmp/ff-001-r1-<run-id>/`：语言分开的复制验证目录、私有合成 SQLite、日志、报告；仅显式命令创建，不覆盖既有目录。资源清单与清理触发条件写入 tasks/checklist。 |

R14新增文件限Rust工程内`src/infrastructure/s7_int_pdu.rs`（或同职责单个文件）、`tests/s7_int_pdu.rs`及自身说明/索引；配套仅修改现有`src/driver_process.rs`、`src/infrastructure/mod.rs`、`src/services/execution.rs`、`tests/local_protocol.rs`、`tests/support/mod.rs`、`src/fixture.rs`所需接线、ACK proof及故障注入。已有测试文件可在tasks记录后沿用，不增加公共协议crate或产品入口。仍在上表Rust `**`内；不需要新增运行依赖或更换S7锁版本，不授权[patch.crates-io]、build.rs/registry缓存修改或vendor。原r2未完成的运行时/文档工作仍按上表继续，不构成全目录重构许可。

实现子目录的 PLAN/catalog 只导航到 FF 唯一任务 bundle，不复制三文件或创建子任务正文。上述 `**` 仍只允许本 spec 所需少量文件，不能扩成平台建设。构建产物、数据库、运行日志、真实配置、缓存不得提交。

排除根 AGENTS/ROADMAP、关联 ARCH-TOOL-001 全文件、backend/frontend、AW/DAA/DS/SMA/CA、现有 tools、其他任务及其配置/清单/锁；不安装全局依赖，不改项目外工具链或共享 skill。无 Git refs、commit/push、发布/部署、Docker 操作、真实数据库/PLC/第三方 HTTP 或 PLC 工程修改。保留所有任务外 dirty；不能通过清工作树取得“干净”证据。

## 3. 路由、依赖与验证平台

PM 使用 `aiis`、`project-governance` 固定边界和身份。后续 Development/Verification 按实际表面使用 `rust-runtime`（运行时/本地 IO）、`plc-point-mapping`（标准 DB 点位/INT）、`backend-arch`（仅本地执行状态、事务与稳定 key）、`i18n-workflow`（CLI 人类文案）、`code-document-indexer`（关键源码头/真实索引）。不套用 FastAPI/ORM/Celery 模板，不引入 Redis、Python Worker、GUI 或通用 DSL。

本地合成状态明确使用 SQLite，属于本 r3 的私有轻量执行验证；不更改 backend 主业务数据库，也不把它升级为现场生产默认库。结构变更以本任务显式 schema 版本/维护入口管理，不能借此批准业务库 migration。

| 项目 | 首轮选择依据与边界 |
| --- | --- |
| Rust | Cargo 独立 binary/library；edition 2021，声明 `rust-version = "1.89"`，首选当前宿主已有 Rust/Cargo 1.89.0。Tokio 1.x、reqwest 0.13.x、serde/serde_json 1.x、serde_yaml 0.9.x、tracing 0.1.x、tracing-subscriber 0.3.x；持久日志可用 tracing-appender 0.2.x，但不能吞掉审计写失败。小型 CLI 可用 clap 4.x。 |
| Rust S7/状态 | 保留精确 `rust-snap7 = 1.142.2`、`rusqlite = 0.32.1`（bundled SQLite），均见现有 DAA 清单/锁；不依赖/复制 DAA/Tauri。已读 registry 缓存的官方 crate manifest/build.rs/client/server 接口：native C++ 编译，提供 DB read/write、client timeout/RemotePort 与 server LocalPort/start_to/register_area。源码接口存在不能证明本工程构建、超时或资源释放。 |
| Python | 独立 uv 工程，Python `>=3.11,<3.14`，自身 `.python-version` 固定 `3.11`，首轮所有锁/构建/运行验证显式选3.11并禁用自动下载；实际已安装解释器缺失则报告，不新增全局安装。asyncio、dataclass/Enum/typing、sqlite3、logging/argparse 可用标准库，HTTP 用 httpx 0.28.x，YAML 用 PyYAML 6.x；严格解析为 typed 对象，不靠隐式类型转换。Python build backend可用hatchling 1.x并锁定实际版本；测试用pytest 8.x或9.x中与Python 3.11兼容的已锁版本。 |
| Python S7 | 保留候选精确 `python-snap7 = 3.0.0`，自身uv锁/环境，不借tools。r1已证实公开Client参数不能约束整体connect/IO期限，故只能在第6节专属driver进程内调用，由父监督器实施整体deadline与真实进程回收；不再把set_param/get_param当有效硬预算。仍须记录有限stale接收及actual WriteVar次数。不得monkeypatch、重装内部transport、私有协商或静默换版本。 |
| 夹具 | Rust 采用自身工程内 test-only Rust binary，包装 `rust-snap7::S7Server`/native server 和 Rust HTTP server；Python 采用自身测试包内 python-snap7 Server 与标准库 HTTP server。各自有本语言 TCP 代理做计数、延迟、断连/丢响应，不能把兄弟版本、DS、backend、Docker 或 Python 桥接作为 Rust 必需服务。 |

进程/匿名IPC/父存活观察优先使用各语言标准库及已有Tokio；Rust如需POSIX FD、signal或本机文件锁封装，仅允许小范围libc 0.2.x，精确版本/用途由Development入本工程锁和tasks。它只服务本任务子进程生命周期。除R14明确允许的Rust单item DB INT S7 payload adapter外，不新增协议实现、service manager或通用执行器。Python不增加Rust/native桥接依赖，2.1.0候选及第三方源码修补均未纳入r3。

其余精确 patch/传递依赖由 Development 在本工程锁中解析并记录来源、checksum、MSRV/解释器兼容；只能在上表候选 family 内择兼容版本，不用 latest URL 冒充冻结。新增相同职责的少量辅助 crate/dev dependency 须先在 tasks 说明必要性；替换 S7 实现、修改第三方源码/协议栈、扩大技术栈或改变验收合同必须返回 PM 新 Revision。锁解析/下载只属于未来获批 Development，不等于构建成功。r1/r2已执行局部事实见第1节与tasks；本r3新adapter的构建/协议/拒绝矩阵及完整runtime验收均`not_run`，当前编译成功仅属于r2候选。

2026-10-21 只读宿主版本：macOS 15.7.7（24G720）、arm64、rustc/cargo 1.89.0、uv 0.7.8、Apple clang 17.0.0。该宿主是首轮本地验收平台；Python 3.11 实际 patch、SQLite 实际版本和所有依赖锁由 Development 记录。缺少匹配工具时先报告，不全局升级/安装。Windows/Linux、现场 OS/架构及安装包交付另 gate。

官方依据只用于选择与约束：[rust-snap7 官方仓库](https://github.com/bruceunx/snap7-rs)、[r1所读API页面（不替代冻结1.142.2原包证明）](https://docs.rs/rust-snap7/latest/rust_snap7/)、[python-snap7 3.0.0 发布与制品 hash](https://pypi.org/project/python-snap7/3.0.0/)、[3.0.0 client 源码](https://raw.githubusercontent.com/gijzelaerr/python-snap7/3.0.0/snap7/client.py)。非版本化文档只作方向参考，不当作已锁版本 API/构建证明。

### 3.1 Rust受限S7 INT adapter（R14，本r3唯一实质增量）

| 方案 | 只读核查与选择 |
| --- | --- |
| 高层db_read/db_write或callback补校验 | Result不暴露原ACK/reference，callback仅op/result；无公开关联验证入口。继续用Ok附IPC身份不能修复，不选。 |
| 原库有限native Sequence补丁 | 需要维护C++ fork/vendor、构建/许可差异和回归；可以单独立项，本轮不授权。 |
| **公开raw ISO交换+本工程INT codec** | **选定。** 已追踪原请求发送、原S7响应及Size回传；保留同一连接/子进程，只生成两个固定payload并验证ACK，不改第三方。 |
| 替换Rust栈/完整自有协议 | 尚无本任务互操作证明，并扩大连接、分片、依赖迁移。宣传或API名称不证明ref校验；不安装、不连续试候选，不选。 |

**来源及可核查事实。** 仍为[官方registry 1.142.2制品](https://static.crates.io/crates/rust-snap7/rust-snap7-1.142.2.crate)，现有Cargo.lock checksum及本机原crate SHA256均为`8c4d43b3a99825abd300d57a0888eda7b625b7cdbf56ee7766bd02331ac58243`。PM只读公开方法和直达native链，未执行新源码：

| 原包文件/位置 | 静态事实 / SHA256 |
| --- | --- |
| src/client.rs:1654 | 公开iso_exchange_buffer(&mut [u8], &mut i32)直接调用Cli_IsoExchangeBuffer；`d8bfd14f61b9e4bb1dced40f468608605829e418264571e0ac34b1700dccebab` |
| native/snap7_libmain.cpp:499 | 公开ABI原样转交Data/Size至同client的isoExchangeBuffer；`3e4a186471b41ead3a80e2d6ce94cec1e7ccc17920b6936a07ead14b274bd643` |
| native/s7_isotcp.cpp:284–308、368–488 | isoSendBuffer封TPKT/COTP；isoRecvBuffer成功后复制原S7 payload回用户Data，并回传实际payload Size；无S7 ref比对。`7c06fa33f0e34afe88962322c5fa946f3072ceeb1a0cc5d2cbdb71c7ac43e6b7` |
| native/s7_isotcp.h:38及接收路径 | IsoPayload_Size=4096；按剩余容量检查每片，Offset+Received形成最终长度。`313c5167f3769367b38073c62da6d1a1c49b63a7016016caf3743666639a2c5f`。这是冻结版本的缓冲设计边界，不是完整native内存安全证明。 |

r3不复制上游实现/改第三方，自有codec按仓库现有MIT归属编写。原包Cargo/LICENSE及Rust包装声明MulanPSL-2.0，native保留LGPL-3.0-or-later声明，build.rs另有GPL-3.0-or-later头；自身说明记录组件来源、链接方式及这些差异，保留原许可，不把包级字段或自有MIT扩展为全组件许可。无新工件发布授权；后续分发/静态链接合规及现场包另gate。

**职责和固定请求。** 仅在原driver子进程唯一IO线程持有原S7Client，公开connect_to/参数/断开继续由原库承担。本adapter只生成S7 job payload（不含TPKT/COTP），单item、DB区0x84、Byte请求transport=0x02、element count=2、R07配置DB/offset（offset*8以24-bit大端表示）；ReadVar function0x04、WriteVar0x05。请求头10字节、parameter14字节；Read无data，总24字节；Write data=00/04/0010/两个INT字节（6字节），总30字节。header声明长度与实际一致，INT保持R07大端补码。不编写socket、TPKT/COTP、连接协商、multi-item/跨PDU切片、其他数据类型/区域、CPU命令或通用raw用户入口。

runtime的INT读写不得回落高层db_read/db_write的Ok；fixture仍用自身原native server。停止后的独立读回用独立连接及匹配校验，可复用codec，不以旧高层Ok冒充关联证据。原生connect协商仍属原库，本修复不宣称已重写或验证其全部路径。

**FFI和身份。** 每次独占固定初始化4096字节工作缓冲；Size输入只用合法请求长度24/30，不是容量，禁止负数/任意用户长度。不能把2字节INT buffer交给无capacity参数的FFI。成功返回先验证Size非负、<=4096及下述精确长度，再索引有效slice；不读旧尾部，错误返回不解析buffer。足容缓冲依据是上述冻结native接收上界，不以Rust安全方法签名证明底层安全；native错误/崩溃仍由原子进程、总deadline和unknown处理，不修改native。

子进程为当前S7 session持有非零u16递增ref和唯一在途job，编码大端且按两个原始字节比较；发送前保存session epoch、expected_ref/op、IPC request_id/generation。同session不复用ref；耗尽65535前在无未结job时正常关连接，再按原owner预算恢复新连接、重置counter，不重发已派发命令或重建command身份。test-only近上界种子验证，不引入产品配置/65535轮长测。AC06普通窗口不触发该维护，仍持续同PID、一个session；错误后旧会话退役也不增加writer。

**唯一正响应（先全部验证，再取值/T3）。** 协议ID=0x32、ROSCTR=0x03 ACK_DATA、reserved两字节=0、ref等于expected_ref、global error class/code均0；parameter length=2，function等于本次04/05，item count=1。Read data length=6、总payload20、唯一item return=FF、transport04、bit length16、恰好两个数据字节；Write data length=1、总payload15、唯一item return=FF且无多余数据。header长度/实际Size完全一致。空/短/超长/附加字节、错误type/function/count/transport/位长/error/status/ref均不能作为正ACK。

验证后才产生私有typed ValidatedRead/ValidatedWriteAck；父service仍须核对IPC request_id/generation，并仅在该次ValidatedWriteAck后走原T3。不增加schema，不从上层传入任意validated=true绕过解析。脱敏trace记录session/ref/op及校验结果，不逐tick无限转储。

**失败/迟到。** 每job至多一次iso_exchange_buffer/一次WriteVar发送；不能为等待正确ACK再调用raw exchange重发。Rust首个坏ref/坏响应立即返回稳定错误（至少s7_reference_mismatch、s7_invalid_response、s7_remote_error），退出ready，在原整体期限内关闭/回收该连接后才恢复；不在坏会话派发下一job，不接受后续正确/旧generation ACK补成功。读失败无good sample或旧值。写一旦可能进入交换，所有无法证明成功的错误（含负global/item ACK）沿R09保守unknown、dispatch_count=1；10次重复/新ID/重启不重发，不以回读核实。证明调用前未执行者仍按原expired/canceled。解析、断开和必要TERM/KILL/wait计入原3000/5000+500、400ms内预留；不添加清理宽限，正常/forced语义不变。

Python保持3.0.0及原公开路径，不要求复制Rust codec/换库。已有有限receive过滤可在同次请求和原deadline内等匹配ACK，前提是无WriteVar重发，坏响应不能直接good/confirmed；AC15公共语义仍须真实验证。若Python公开路径无法满足，停止回PM，不自动授权Python raw实现/monkeypatch/其他候选。

**批准后首个gate。** Development先只接入本codec，完成固定报文、逐长度截断及拒绝单元矩阵，再用原31102/31103/31880和新私有synthetic库验证：正常Read/Write、仅改ref的Read拒绝、已应用Write但错误ref得到unknown/confirmed=0/actualWriteVar=1、短响应拒绝及真实回收。每fault case用独立新私有库；同case的重复/重启必须沿原库/身份。整个gate的自有harness上限120秒，单操作仍原预算；超限实际清理自有child/fixture并记失败，不能pass。保留请求/native响应/实发响应三份hex/ref、state/events只读导出、退出码/PID/端口。gate通过才继续完整Rust AC01–AC15及Python；失败dev_blocked，若公开API/FFI不可实现则回PM，不连装候选、加运行代理或改native。

本方案仅静态可行；r3代码、gate及完整矩阵not_run，r2编译/局部通过不证明本方案通过。

## 4. 有边界的结构与职责（R01）

每版只建立真实需要的模块，建议如下；允许语言惯用的少量拆分，不要求逐文件镜像。

```text
field-flow-rust/                 field-flow-python/
  Cargo.toml / Cargo.lock          pyproject.toml / uv.lock
  src/main.rs / lib.rs             src/field_flow/__main__.py / cli.py
  src/commands.rs                 src/field_flow/config.py / domain.py
  src/config.rs / domain.rs        src/field_flow/runtime.py
  src/runtime.rs                  src/field_flow/services/
  src/driver_process.rs            src/field_flow/driver_process.py
  src/services/                   src/field_flow/app/demo01.py
  src/app/demo01.rs                src/field_flow/infrastructure/
  src/infrastructure/              tests/fixtures/ + tests/
  src/bin/ff-fixture.rs            config/loopback.yaml
  tests/support/ + tests/          locales/zh-CN.json / en-US.json
  config/loopback.yaml             README.* / PLAN.* / plans/README.*
  locales/ + README/PLAN/catalog   CODE_INDEX.md / .gitignore
```

入口/CLI 只解析参数、装配、调用 service/runtime；runtime 只调度、监督、取消和退出。infrastructure 封装 HTTP、PLC、SQLite、文件/日志 IO及私有driver IPC；service 拥有父进程执行状态与事务边界；domain 保留 typed 输入/状态/错误；`app/demo01` 只手写一次有界业务迭代，不能持有无限 while、原始 socket 或 SQL。禁止万能 core、表达式语言、脚本执行、插件框架和预建节点平台。

driver_process只是本工程私有子进程bootstrap/监督封装：Rust由同一可执行文件的隐藏内部模式启动，Python由自身环境中的同包模块启动；仅接受父进程继承的专用控制通道，不接收shell脚本、任意程序或业务插件，不新增用户flow/监听端口。同步driver只在子进程唯一执行线程创建/持有；HTTP、SQLite、业务service和必要持久审计仍在父进程。辅助父存活/stop观察线程不能执行PLC IO。

公开示例 YAML 是小份人工审阅的运行配置；JSON 是 locale/机器报告，SQLite 是本地执行事实，JSONL 是日志/证据，四者不互相冒充真相源。不新增 XLSX/TIA/UDT 导入或客户点表。

## 5. 启动与 typed 配置（R02）

无参和 `--help` 仅显示帮助、exit 0，不读配置、不联网、不创建日志/状态；错误命令非零。支持 `--lang zh-CN|en-US`，CLI 帮助/错误摘要来自对称 locale key，稳定日志和状态 key 不翻译。`run` 必须显式 `--config`、`--state-dir`，默认 dry-run；只有 `--execute` 才允许 PLC write，运行中不能自动切换模式。

schema 初始化独立于 run：`state init --synthetic --mode dry_run|execute --state-dir <new-private-path> --instance-id <id>` 只为本任务新建私有合成库。新目录必须不存在；有任意文件/库、软链接或路径冲突则拒绝，不覆盖、不迁移、不清表。`state inspect --state-dir ...` 只读。普通 run 只打开已经初始化、schema_version/implementation/mode/instance_id 匹配的库，缺失/未知/更高 schema 版本均非零退出；不自动执行 DDL。r3 不提供清空、重置、重发 unknown 或状态跨语言迁移命令。

每版独立示例具有同一形状，端口和私有路径可不同。不得读取父目录/backend/tools 的 `.env`、自动发现 endpoint 或导入兄弟配置。

```yaml
schema_version: 1
instance_id: ff-rust-demo01       # Python 示例为 ff-python-demo01
plcs:
  - id: plc_demo
    host: 127.0.0.1
    port: 31102                  # Python 示例为 32102
    rack: 0
    slot: 1
    connect_timeout_ms: 3000
    io_timeout_ms: 5000
    queue_capacity: 16
    queue_wait_ms: 2000
    ready_wait_ms: 3000
flows:
  - id: demo01
    kind: demo01
    business_name: synthetic_command_to_int
    interval_ms: 500
    source_id: demo01-feed
    get_url: http://127.0.0.1:31880/demo01/command
    target: {plc_id: plc_demo, db_number: 1, db_size_bytes: 16, byte_offset: 0, type: INT}
    input_max_age_ms: 10000
http: {connect_timeout_ms: 500, total_timeout_ms: 1500, pool_wait_ms: 500, max_connections: 8, max_body_bytes: 4096}
shutdown_timeout_ms: 15000
```

`id/source_id` 使用 `[A-Za-z0-9_-]{1,64}`；最多 4 个 PLC、8 条注册 flow；重复 ID、同 endpoint 的多个 PLC 定义、未知字段/kind、缺失字段、隐式字符串/数字转换均启动前拒绝。同一进程不能让多个 flow 写重叠的 endpoint/DB/字节范围，即使不同 plc_id 也不能绕过。r3 公开用户流只注册 demo01；并发读能力由测试流验证，不注册 demo02。

PLC host/port、rack/slot、DB/offset都从typed配置读取；r3的PLC host只接受literal IPv4，不做DNS或地址扫描，公开配置只有loopback和synthetic值。测试/fixture命令只可连接下文列明的127.0.0.1端口。一般配置支持能力不提供对实际目标的联网授权；任何真实地址/第三方调用都留在后续gate。

本 r3 默认值如上且必须全部有限；允许配置区间：interval 100..10000 ms，HTTP total 100..5000 ms/connect/pool 各100..1500 ms，PLC connect 500..3000 ms（默认与hard cap均3000）、IO 500..5000 ms（默认与hard cap均5000）、queue/ready wait 100..5000 ms、queue capacity 1..16，shutdown 5000..20000 ms；测试降低逻辑容量阈值不能超过第9节上限。run前必须满足`http.connect_timeout_ms <= http.total_timeout_ms`、`http.pool_wait_ms <= http.total_timeout_ms`，以及`shutdown_timeout_ms >= max(全部PLC的connect_timeout_ms、io_timeout_ms、http.total_timeout_ms) + 1500 + 4000`。其中1500ms为状态提交1000ms加调度误差500ms，4000ms为取消、断开、join及日志flush的退出余量；默认5000+1500+4000=10500ms，默认shutdown15000ms符合，关系不满足则启动前拒绝。先同时通知全部owner停止新工作，不逐个等待完IO才通知下一个。ready等待、queue等待、HTTP/PLC调用均有自身配置期限；涉及命令时再取原输入剩余有效期/monotonic deadline的较小值。超时返回不能冒充同步driver已终止，预算内未真实释放仍按R05报告失败。

## 6. 调度、持久PLC会话、进程故障隔离与退出（R03–R05）

**R03 调度。** 每个 flow 独立异步任务/监督状态；一次迭代结束后再等待 interval，同 flow 最大在途迭代为 1，无历史 tick 队列和追赶补跑。HTTP 等待、timer 和业务判断都在 PLC 请求之外，不占 PLC 的队列位置/执行锁。某 flow 的 HTTP 超时、输入拒绝或 recoverable 错误不停止独立 flow；全局状态/审计不可写则暂停所有新副作用，读流/健康可以继续。

**R04 PLC owner与driver进程。** 每个配置PLC由父runtime一个监督owner管理一条FIFO有界队列、一个当前driver子进程及其代次generation；最多4个PLC/4个driver子进程，不按flow/请求创建进程。子进程唯一执行线程创建、持有、调用和关闭一个同步S7 client；正常长期运行保持同一PID/generation及一个S7 session，不逐tick重建。主runtime事件循环不执行同步driver，也不以to_thread/spawn_blocking无限后台调用替代隔离。HTTP/timer不占PLC位置；同点多flow各自采样、无共享缓存/订阅/快照的语义保持。

所有PLC读写只经父队列派发；子进程无第二工作队列、无业务状态库/重试器，最多一个driver call在途。每flow至多一个待完成请求；request_id/flow_id/generation、typed INT目标/值、操作和剩余期限通过私有匿名pipe或继承的socketpair传递，不新增网络监听器。单消息<=4096 bytes、每方向累计缓冲<=16KiB；读写/解析有截止时间和长度校验，不能无限等换行、阻塞pipe或等待未消费stdout。只接收匹配当前generation/request_id且期限内的结果；IPC坏帧、断开、子进程异常退出或迟到结果不能映射成成功。子进程日志经独立有界通道归父记录，不污染结果通道，也不允许日志阻塞绕过driver总期限。

owner状态仍为`disconnected -> connecting -> ready -> recovering`及`stopping/stopped`。依赖PLC的操作等待同一owner ready，有限ready等待超时不下发，不各自连接。连接/读错误由owner统一退避，一个周期最多5次connect，间隔250/500/1000/2000ms，失败后cooldown10000ms；ready后成功IO才清连续失败计数。更换子进程也是这条有界恢复路径；旧进程真实退出/回收且IPC关闭前不得启动替身，不在重连或child恢复中重放write。

**整体预算保持原值，改变的是可验证的执行隔离边界。** 每次connect操作从spawn/IPC bootstrap开始计时，读写从本次dispatch开始计时，包含IPC和故障terminate/kill/wait回收。父监督器以monotonic deadline为权威，使用配置与原输入剩余有效期的较小预算；connect hard cap3000ms、IO hard cap5000ms及最多500ms调度误差均不变。内部固定预留400ms故障回收预算：正常工作及IPC须在整体期限前400ms结束；未结束即向仍属本owner的child发送TERM，最多等待200ms，必要时KILL并在剩余200ms内实际wait/reap。若剩余有效期不足400ms，不进入driver调用，按expired/unavailable拒绝，不追加宽限。正常结果提前返回不需耗尽预留；不能把native每阶段timeout、正常分片次数或参数/2当所有错误/析构路径上界。

实测整体结束必须同时包括driver进程真实停止（故障时）及匹配结果/明确失败；不能只返回timeout而留下活driver。400ms在原3000/5000ms预算内，500ms只是原有调度误差，不叠加另一段清理宽限。到总期限+500ms仍未实际回收，标`driver_cleanup_incomplete`、阻塞该PLC并报告失败；不得返回“有界成功”、宣称资源已释放或启动替身。native/Python调用可能不能自行返回这一事实如实保留；硬边界来自OS进程隔离，不宣称第三方库已被修好。写permit可能已交付后出现这些错误均按R09进入unknown，late ACK/回读不能升级它。

跨进程开始下发闸门与stop必须有同一有界串行顺序：父stop先关闭新接纳/派发，再与child的调用前stop/TTL/permit检查协调闭闸。SQLite仍须按R08在T2/prepermit先持久化保守in_flight；它不证明物理调用已开始。只有消费start permit且越过实际调用开始闸门的请求，才可记运行时driver_call_started/正在执行统计。仍在父队列或已交IPC但未过开始闸门的请求必须取消，能证明未执行时按R09记expired/canceled；不能把SQLite in_flight或IPC已交付当实际开始证据绕过queued-stop。测试需在child调用前设置屏障，stop闭闸后证明零下发；不能证明是否已开始的个案保守unknown，并实际回收child。此闸门只保护本实例，不扩成跨主机fencing。

子进程还须观察父专用存活通道：父异常死亡/控制EOF时，child不得继续收工作或成为孤儿writer；若同步driver卡住，存活观察路径须在500ms内实际结束自身进程，明确属于parent_lost故障中止，不假称正常join。child生命周期持有本实例排他锁的继承份额或等效本地占用，重启父进程不得在旧child仍可能执行时取得同实例writer；只有确认旧代次结束才放行。正常父进程必须wait/reap其child；父被杀时由独立测试harness观测child PID/连接确已消失及旧实例锁释放，不能伪造已死父进程的wait。不得扫描/杀进程名、端口占用者或归属不明PID；此机制不增加服务安装、后台托管或跨实例接管。

连接复用仍仅进程内这组父/子实例；IO串行不提供command去重或业务效果排他。Rust/Python依次执行夹具；真实现场同资源单一writer、停旧再交接和跨主机排他另gate，不因失联自动接管。driver子进程被终止不能撤销已经送到PLC的写或保证物理动作停止，unknown保守阻断保持。

**R05 正常退出与故障清理分开。** SIGINT/SIGTERM先按上述闸门停止新接纳/下发并取消未开始队列，所有owner同时进入stopping。在途IO、disconnect/析构和child自然退出共用一个有界stop期限，不为每个阶段重新加整段预算：该期限至多为stop时刻加本配置max(connect_timeout_ms,io_timeout_ms)，且不晚于剩余global shutdown期限。只能在原500ms误差内完成必要故障回收。正常路径须child自行关闭client、辅助线程真实join、exit0，父真实wait/reap；父随后关闭HTTP/SQLite/日志并await/join全部自有任务/线程，才可记正常`resources_released`/`shutdown_complete`。默认15000ms总shutdown预算及R02判断式不变，进程回收已计入原预算，不能另加宽限。

任何deadline、崩溃、parent_lost或stop超时导致的TERM/KILL/强制process exit都记录`forced_driver_stop`及故障原因/退出状态；只有实际结束/回收才可记`driver_process_reaped`，result必须是fault_cleanup，不使用正常shutdown_complete遮蔽。停止后排队请求不下发；可能已发送写为unknown，confirmed不得倒退。该次运行发生强制中止，最终exit1并保留had_forced_driver_stop；即使读流随后有界恢复，也不改写故障历史。未回收报`shutdown_incomplete`/非零、无释放成功声明。正常成功停止exit0，配置/状态错误exit2，运行/不完整退出exit1；unknown/持久化故障明确非健康。强制中止是本r3继续保留的已批r2故障隔离行为，绝不等同于正常优雅退出或现场物理回滚。

## 7. demo01 输入与 INT 合同（R06–R07）

**R06 synthetic GET。** 每轮至多一次 GET，复用 HTTP client/pool；不重定向、不用环境代理、不自动应用层重试，不执行 POST。只有 HTTP 200、JSON content type、UTF-8、体积 <=4096 bytes、完整严格 schema 的响应才进入业务规则。错误码、坏 schema、缺失、stale、idle 和正常命令分别有稳定结果 key；不得用默认值、上轮值或缓存值触发写入。

响应是两个 typed 变体，字段名称/含义仅属本地 fixture，不能说第三方/Backend 已实现：

```json
{"schema_version":1,"source_id":"demo01-feed","ready":false,"command_id":null,"value":null,"issued_at_ms":null,"expires_at_ms":null}
{"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":"cmd-001","value":42,"issued_at_ms":1792531200000,"expires_at_ms":1792531230000}
```

时间仅为形状示例，fixture 每个新 ID 用当前 UTC 生成，重复 ID 的字段保持不变。`ready` 必须真 bool；ready=true 时 ID 非空且符合上述 ID 规则，value 必须为 JSON 整数，Python bool/浮点/字符串均拒绝；source_id 必须等于 flow 配置，unknown 字段拒绝。

`issued_at_ms/expires_at_ms` 为来源 UTC Unix 毫秒整数，是源命令发行/失效时间，不能拿接收时刻代替。命令需满足 `0 < expires-issued <= 60000 ms`、issued 不晚于本机 UTC+1000 ms、未到 expires、且源年龄 <= input_max_age_ms（默认10000，上限60000）。接收时校验一次，真正 driver call 前再次校验；ready/queue等待不能延长原有效期。接收时把剩余有效期绑定到 monotonic deadline，之后同时检查 UTC 与 monotonic，重启仍沿原来源时间；时钟跳变超过1000 ms 时暂停新写并暴露 clock_invalid，不能靠倒拨时钟让旧命令复活。synthetic 来源与运行时使用同机时钟；真实来源时间可信度、同步/签名/TTL/撤销合同另 gate。

身份是稳定 `(source_id, command_id)`，不含 run_id、重试号或模式。首次合法 ready 命令把 flow_id、目标资源、值、来源时间/有效期、schema版本固定成规范 typed 摘要及 SHA256。相同 ID 同摘要复用原状态；相同 ID 不同值、时效、flow/目标或其他语义字段是 `identity_conflict`，保留原意图，不覆盖/不再次下发，并暂停该写 flow。刷新同 ID 时间不能当新命令；idle 不创建执行命令。

**R07 INT。** 首轮能力仅标准 DB 绝对地址的有符号 16-bit INT 读写，范围 -32768..32767，严格两个字节、大端二进制补码；-1=FFFF、0=0000、42=002A、上下界须有证据。DB号1..65535、声明的db_size_bytes为2..65536、byte_offset0..65534，须满足offset+2<=db_size_bytes，并在fixture注册的实际块内检查完整范围；配置声明不证明真实PLC块大小。不隐式截断或扩大为整块写。读回带sample/request身份、质量和时间，不把旧值作为好值。BOOL/位写、DINT/REAL、I/Q/M、CPU操作、下载和PLC安全设置均后续另立范围。

## 8. 本地 SQLite 意图、状态与恢复（R08–R10）

### R08 最小 schema 与事务

以下是将来由独立 `state init --synthetic` 创建的 schema 合同，不是本轮可执行 DDL。每版各有自己的 SQLite 文件；本实例排他占用自身state-dir锁，另一实例的writer失败；父进程是唯一DB writer，child仅持有R04所述锁生命周期份额，不开DB、不写状态。不共享可写库，不复制现有业务库。字段使用稳定英文 key；schema_version=1。

| 表 | 最小字段/约束 |
| --- | --- |
| `store_meta` | 单行，schema_version、implementation=`rust|python`、mode=`dry_run|execute`、instance_id、store_uuid、created_at。模式/实现不匹配拒绝使用。 |
| `commands` | PK `(source_id,command_id)`；flow_id、target_key、config_identity_hash、payload_hash、value_i16（CHECK范围）、issued_at_ms、expires_at_ms、state、dispatch_count（0或1）、run_id、request_id（可空）、last_error_key（可空）、ack_kind（可空）、created_at、updated_at；身份和意图字段插入后不可变。 |
| `command_events` | 单调主键 seq；命令复合FK、run_id/request_id、from_state/to_state、reason_key、必要的脱敏摘要与 created_at；只追加、不覆盖。 |

`target_key`只表示规范化物理写资源：literal IPv4 endpoint/port、rack/slot、DB、offset、INT长度，不含flow_id、source_id、plc_id别名、run_id或配置文件名。flow_id单独记录命令归属，config_identity_hash另行固定该归属、source绑定和影响命令含义的配置。启动恢复及每次接纳/派发新命令时，必须查原库所有unknown（包括刚由in_flight恢复者）的物理endpoint/DB/字节区间；与目标重叠就阻止写，不能靠换flow_id、source_id、plc_id、配置别名或command_id绕过。原库与原身份必须保留；换库/删库不属于恢复办法。本合同只覆盖本实例及其原私有库，不宣称跨库/跨主机fencing。时间约定：来源字段明确保存外部UTC Unix ms；created_at/updated_at为SQLite UTC数据库时间表达式，操作超时用monotonic，不写入宿主本地时区。原始body、token、URL query不进库/日志。

SQLite 单 owner/串行状态 executor，不能堵事件循环；busy_timeout 500 ms，事务 deadline 1000 ms，短事务内无外部 IO。首轮 `journal_mode=DELETE`、`synchronous=FULL`、foreign_keys=ON；固定page_size4096、主文件max_page_count16384（64MiB），不使用共享 WAL、网络文件系统或任意自动 schema migration。

T1：同一事务查身份/冲突，插入 pending 意图与对应 command_event，commit成功后才可准备外部动作。T2：确认mode/TTL/ready/容量/stop/必要审计健康并取得有界队列位置后，以CAS将 pending->in_flight、dispatch_count0->1并追加event，commit后才能把唯一 dispatch permit交给监督owner，经跨进程开始闸门调用一次写入；提交失败不下发。队列交接不得在事务失败后遗留可执行请求。T3：仅在匹配请求的正 S7 write ack 后，同事务 in_flight->confirmed、ack_kind=`s7_protocol`并追加event。确认持久化失败时保留in_flight/unknown事实、暂停新副作用，不回到pending重发。

父进程是唯一SQLite/command_events和必要持久审计owner；driver child不打开状态库、不自行保存/重试命令。T2必须在任何可能下发的IPC start permit之前commit；child generation/退出事实进入现有脱敏event上下文，不新增业务状态schema。child崩溃、IPC结果丢失或强制结束不能生成新command身份；只读恢复与unknown写阻断仍按原物理资源范围执行。

### R09 状态含义与转换

| 状态 | 精确定义与恢复 |
| --- | --- |
| `pending` | 意图已持久，但没有发出过 dispatch permit，dispatch_count=0。重复请求不建新身份；重启后只有当前 GET 再次给出同摘要且原有效期仍有效、配置/目标一致才可继续；不能仅凭库存意图离线重放。 |
| `in_flight` | dispatch_count=1、下发许可已持久，外部调用可能未开始/进行中/已生效；不是成功。重启在任何连接/新下发前统一转 unknown并追加恢复event，即使可能是发送前崩溃也保守处理。 |
| `confirmed` | 收到该请求的正S7协议ack且本地确认事务已commit。重复/重启永不再次写同身份；不代表PLC逻辑接受、工艺完成或物理exactly-once。 |
| `unknown` | 进入driver调用后发生超时/断连/响应丢失/崩溃，或ack/确认持久化无法完整证明。保留原身份/意图/证据，阻止此flow/目标后续写（包括新ID）；重连/下一tick/重启不能自动重发或转confirmed。 |
| `expired` / `canceled` | 可证明未开始driver写：pending过期或停机前取消，或permit交接被owner明确拒绝且未执行。保留记录，不自动重建身份重发。不能证明未发送则unknown。 |
| `simulated` | 仅dry_run库中的would_write观察，dispatch_count=0、ack_kind为空，不入真实执行confirmed；绝不能导入execute库。 |

合法路径是 pending->in_flight->confirmed/unknown，pending->expired/canceled，以及明确未执行的 in_flight->expired/canceled；后者不得重置dispatch_count再重试。dry_run只记录simulated。坏schema/stale在接纳意图前拒绝；进入pending后的到期沿上述路径留痕。首轮不提供unknown的自动查询/人工改状态CLI；需要核对的工作保持阻塞，另批目标方握手/人工处置方案。

writer/owner/库恢复和flow健康相互区分：某目标unknown不应停止不相关读流；相同写目标新命令不得绕过。已confirmed之后的日志/后续故障不得把它降回可下发；本轮无结果POST/补投步骤。未来若加回报，只能补报原身份，不能倒退到PLC写。

### R10 dry-run、失败与能力限度

dry-run可对获批loopback做GET和S7 read，但PLC写计数必须为0；默认只记录would_write/simulated。初始化时mode固定，dry_run/execute使用两个独立state-dir，交叉打开非零失败。两模式使用同一来源身份语义；dry-run不能占用、确认、复制或重置execute进度，也不能靠切模式消除unknown。

必须覆盖：T1前失败、T1后发送前重启、T2后调用前崩溃的保守unknown、server已应用但ack丢失、server已应用且进程崩溃、收到ack但T3失败、confirmed重启不重发。所有可能已发送错误保守unknown；库/日志持久化不能与PLC原子提交，S7 ack、SQLite事务或回读同值均不能核实原命令工艺完成或升级unknown为confirmed。回读只作协议数据正确性证据。

## 9. 日志、健康与容量（R11–R12）

**R11 可观测性。** stdout与自身state-dir下持久文件均为JSON Lines；最低字段：UTC timestamp、event、implementation、run_id、instance_id、flow_id/target_id、command_id/request_id（适用时）、state/old/new、result、duration_ms/error_key。最低事件包括process/config/state init、owner连接/退避/恢复、flow健康变化、intent/dispatch/ack/unknown/冲突、容量暂停、stop/join/资源释放。普通读不逐tick刷日志，用每5秒progress/health聚合计数；测试专用协议采样trace单独有界保存。

日志按大小轮转：写入完整JSON行前按大小检查，单文件不超过5MiB、最多4个backup；单行<=4KiB，总文件上限25MiB，既有日志不因启动截断。Rust tracing持久sink必须有实际失败回传；不能用默认忽略IO错误/有损异步队列冒充必要审计。副作用前的意图/dispatch审计须在SQLite事务和持久日志均成功落盘（flush/sync有回执），否则阻止下发；stdout/持久sink故障均停止新副作用并报告health。副作用后审计失败不能抹除或重放已确认动作；保持最后持久in_flight/confirmed并可见报告。审计不依赖可轮转普通日志唯一保存，command_events保留必要状态链。

健康快照由监督器拥有，至少含每flow的starting/running/recovering/blocked/stopping/stopped、最近迭代/成功、连续错误、owner状态/队列深度/在途数、pending/unknown计数、容量和日志可写性；通过每5秒JSONL及正常退出摘要观察，不新增health HTTP监听器或GUI。idle/无新命令不算失败，进程仍在运行不能冒充flow健康。

新增必要事件为driver spawn/ready/generation、IPC拒绝、deadline、forced_driver_stop、driver_process_reaped、parent_lost与stop闸门闭合；正常与forced退出分别记录。不得仅看到child.stop返回或PID字段就写资源已释放，父审计失败仍阻止新副作用。

**R12 容量。** 默认command上限10000条、command_events100000条；接纳新身份前若event>=90000、库主文件>=48MiB、可用磁盘<256MiB或command达上限，则暂停新副作用，保留恢复写余量。主库硬上限64MiB，含rollback journal的state占用上限128MiB；到硬边界失败即阻止新副作用，不能删除pending/unknown/confirmed身份腾空间。读恢复/健康仍有界；不建自动清理、淘汰去重ID或无限离线命令队列。测试可把计数上限降低为10/100或模拟IO错误验证，不需要真实写满磁盘。日志轮转删除旧普通日志前，必要审计已留在command_events；本轮不提供生产归档/保留年限承诺。

## 10. 本地协议夹具与批准后的拟执行命令（R13）

以下是沿用的拟执行命令合同；r2已执行子集及结果仅见tasks，未完成命令和全部r3验证均`not_run`。须先批准精确r3，再由Development按R14预检顺序续接；批准仅覆盖本任务新建私有状态库与loopback，不泛化成真实DB/设备权限。

| 实现 | 固定端口 |
| --- | --- |
| Rust | S7 client入口/proxy `127.0.0.1:31102`；native S7 server `127.0.0.1:31103`；synthetic HTTP `127.0.0.1:31880` |
| Python | S7 client入口/proxy `127.0.0.1:32102`；自身S7 server `127.0.0.1:32103`；synthetic HTTP `127.0.0.1:32880` |

每套fixture独立启停，不能绑定wildcard/102、杀占用者或自动换端口；冲突报告并停止该验证。TCP proxy只转发有界TPKT并识别读/写及匹配响应做计数/故障注入，不重写通用S7栈。普通运行一个runtime到该PLC的会话，proxy前后两段TCP属于同一透传S7会话，证据应分别标记，不能把它记为两个独立客户端。server注册内存必须活到fixture真正退出；停止不能提前释放native仍可能使用的buffer。上游native stop返回不是线程join证明，fixture宜进程隔离；父harness等待子进程正常退出并确认端口释放后才算结束，强杀另记失败清理。

fixture必须能固定同ID响应、发新ID/坏schema/stale/冲突、延迟指定GET、断开/恢复S7、在server已应用写并产生匹配ack后丢弃/扣留该ack、确认实际写计数/字节、在此屏障时终止测试runtime再重启原库。丢包只发生在TCP传输层，不能用mock函数返回unknown替代。正常路径也要真实GET、S7协商、WriteVar和独立协议读回；独立读回安排在runtime停止后，避免污染“正常运行只有一个会话”计数。轻量单元测试补边界，不承担全部协议证据。

私有driver入口由runtime自身启动，不新增人工运行helper的产品步骤。正式local_protocol测试须增加第11节所列整体deadline、未开始屏障stop、child/parent崩溃与真实回收场景；阻塞测试只针对本任务loopback/自有进程，且父harness有外层回收界限，不能故意留下无限挂死程序。r1已有native分段失败/Purge可达性证据用于定义场景，不冒充r3 adapter或完整进程隔离矩阵已通过。

从Rust工程目录，r3批准后先执行（本轮均not_run；真实协议gate由自有harness在120秒内连同资源回收结束）：

```bash
cargo test --locked --test s7_int_pdu
cargo test --locked --features test-fixture --test local_protocol matched_ack_preflight -- --test-threads=1 --nocapture
```

上述test target/filter是本r3拟提供的精确入口，尚未创建/运行。gate通过后再运行原完整命令及`cargo test --locked --features test-fixture --test process_lifecycle -- --test-threads=1`；不能只跑filter就交付。

从Rust工程目录，沿用：

```bash
cargo fmt --check
cargo check --locked --all-targets --features test-fixture
cargo build --locked --bins --features test-fixture
cargo test --locked --lib
cargo test --locked --features test-fixture --test local_protocol -- --test-threads=1
cargo run --locked --bin field-flow --
cargo run --locked --bin field-flow -- state init --synthetic --mode dry_run --state-dir /private/tmp/ff-001-r1-<run-id>/rust/dry --instance-id ff-rust-demo01
cargo run --locked --bin field-flow -- state init --synthetic --mode execute --state-dir /private/tmp/ff-001-r1-<run-id>/rust/execute --instance-id ff-rust-demo01
cargo run --locked --features test-fixture --bin ff-fixture -- --config config/loopback.yaml --evidence-dir /private/tmp/ff-001-r1-<run-id>/rust/fixture
cargo run --locked --bin field-flow -- run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-<run-id>/rust/dry
cargo run --locked --bin field-flow -- run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-<run-id>/rust/execute --execute
```

从Python工程目录，拟提供：

```bash
uv lock --check --python 3.11 --no-python-downloads
uv sync --locked --python 3.11 --no-python-downloads
uv build --python 3.11 --no-python-downloads
uv run --locked --python 3.11 --no-python-downloads python -m compileall -q src tests
uv run --locked --python 3.11 --no-python-downloads pytest -q tests/unit
uv run --locked --python 3.11 --no-python-downloads pytest -q tests/test_local_protocol.py
uv run --locked --python 3.11 --no-python-downloads field-flow
uv run --locked --python 3.11 --no-python-downloads field-flow state init --synthetic --mode dry_run --state-dir /private/tmp/ff-001-r1-<run-id>/python/dry --instance-id ff-python-demo01
uv run --locked --python 3.11 --no-python-downloads field-flow state init --synthetic --mode execute --state-dir /private/tmp/ff-001-r1-<run-id>/python/execute --instance-id ff-python-demo01
uv run --locked --python 3.11 --no-python-downloads python -m tests.fixtures --config config/loopback.yaml --evidence-dir /private/tmp/ff-001-r1-<run-id>/python/fixture
uv run --locked --python 3.11 --no-python-downloads field-flow run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-<run-id>/python/dry
uv run --locked --python 3.11 --no-python-downloads field-flow run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-<run-id>/python/execute --execute
```

`<run-id>`是待执行者生成的唯一目录名，不可照抄尖括号到shell；上述是分终端/由harness顺序运行的命令，fixture需先就绪。首个锁生成在获批Development时显式执行`cargo generate-lockfile`/`uv lock --python 3.11 --no-python-downloads`，之后使用locked命令；本轮不运行。Python自身`.python-version`也为3.11，不能让uv静默选择3.12/3.13或自动下载解释器冒充本平台首轮证据。Development需把最终可复制命令、fixture退出方式、实际命令/退出码/解释器patch/版本/路径和AC证据写入tasks，不能把本节future命令当执行记录。

还须分别把单个工程复制到本任务新建私有目录，排除target/.venv/dist/状态/日志，隐藏或缺少父/兄弟工程仍按自身README锁定依赖、build/start/test；可以使用正常公共package缓存，不能借另一个工程的源码/可写库/运行fixture。所有有效源码最终在约定交付工作树，复制品的结果不能替代交付树一致性核对。

## 11. 验收标准

以下AC每版分别给结果；Rust先完成AC01–AC14及新增AC15的DEV证据，Python再按同一业务矩阵跟进，最终统一fresh-context Verification。技术风险/依赖blocker不能用一版通过替另一版通过，也不能把not_run改为deferred complete。

| AC | 可观察验收 / 对应需求 |
| --- | --- |
| AC01 | 两版各自独立复制、锁解析、构建、无参/help、显式初始化、启动和测试成功，记录当前平台/工具/锁；私有driver child来自自身可执行文件/同包同环境，随本工程复制构建启动，无父清单/兄弟源码或fixture/环境/可写SQLite依赖；正式交付树与候选一致。（R01/R02/R13） |
| AC02 | 入口分层、typed配置和中英CLI成立；无参无IO；未知/缺失字段、重复ID/endpoint、写范围冲突、非法预算/状态版本/模式拒绝；init不覆盖既有目录，普通run不建schema。（R01/R02/R08/R10） |
| AC03 | 两版demo01有真实GET->S7 INT写->停止后独立S7读回的完整协议证据；INT -32768/-1/0/42/32767正确，越界/float/bool/string及块越界拒绝，邻接字节保持。（R06/R07/R13） |
| AC04 | idle、非200、超体积、坏JSON/schema/source、过期/未来时间/过长TTL均零新写；入队后过期与时钟倒拨不放行，重复ID不刷新时效。输入拒绝与通信故障可区分。（R02/R06） |
| AC05 | 相同命令连续至少10轮、child故障恢复及父进程重启原execute库只产生1次实际写；同ID不同payload/time/target触发冲突且原记录不变；新合法ID才可能产生新写，也不能绕过unknown。同一父SQLite身份不因driver generation变化而重建。（R06/R08/R09） |
| AC06 | 同一PLC下至少3个独立测试读流读同一INT，每流至少20个独立sample/request；正常阶段同一child PID/generation持续复用、S7协商session总数1、driver最大在途1、协议请求串行、每结果归回正确flow。读值不同时间可不同，不伪称共享快照；不逐请求spawn。（R03/R04） |
| AC07 | 一个测试流GET延迟1200ms，另一个读流按100ms间隔在8秒窗口完成至少20轮、最大相邻成功间隔<=500ms；慢流最大在途迭代1，HTTP等待不占PLC执行位置，无补跑tick。（R03/R04） |
| AC08 | server未启动/主动断连时仅owner按原有界策略重连；ready前无IO，恢复后读流继续，坏配置不触发无限重连，独立无关flow继续。两版均在真实静默COTP、分段/慢字节/stale响应、错误恢复或disconnect不响应场景验证整体deadline：含spawn/IPC及必要TERM/KILL/wait回收，connect<=配置且不超3000+500ms、IO不超5000+500ms。真实reap/连接释放前不换child；未回收明确失败，无有界成功或正常优雅退出假象。不能只检查异步waiter返回。（R03–R05） |
| AC09 | T1后发送前重启沿原身份/原TTL处理；T2后不明发送点恢复unknown；真实server已写但ack被丢弃得到unknown，至少再GET10轮和重启后实际写计数仍1。改变flow/source/plc别名、新ID或重叠目标范围都不能绕过原库unknown，读流仍能推进。（R08–R10/R13） |
| AC10 | server写已生效、ack扣留时分别终止driver child及父runtime，原库恢复unknown且不再次下发；父死亡后child在500ms内实际结束，独立harness证明无孤儿PID/连接、原实例锁在旧child结束前阻止重启writer。ack后确认持久化失败也不重发；confirmed不因进程/日志故障倒退，回读同值不能将unknown升级confirmed。（R04/R05/R08–R10/R13） |
| AC11 | dry-run实际GET/read可见、真实write计数0，持久状态仅simulated，confirmed数0；dry_run/execute库交叉打开失败，dry观察不影响execute身份/进度。（R02/R10） |
| AC12 | stdout/持久文件逐行JSON可解析且脱敏，真实轮转边界成立；通过降低计数阈值/注入磁盘/审计失败证明暂停新副作用、保留pending/unknown/confirmed，不需真实填满磁盘；健康能区分recovering/blocked/仍运行。（R11/R12） |
| AC13 | 父队列及child调用前屏障都有待执行请求时正常stop，闭闸后这些请求零下发；默认15秒内正常child exit0/父wait、父任务与owner/观察线程真实join、客户端/库/日志关闭，fixture自然退出且端口/PID释放。另以自有故障child证明deadline强制终止在整体预算内真实回收、operation/该次运行如实失败并记录fault_cleanup，绝不正常shutdown_complete。强制未回收须blocked/incomplete，端口冲突不杀占用者/换端口。（R04/R05/R13） |
| AC14 | 两版README/PLAN/catalog/locale/索引与实际相符，tasks记录逐AC命令、退出码、实际资源和未验gate；fresh-context命名Verification独立出checklist verdict；Human Owner最终验收仍单独待决定。（R01–R13） |
| AC15 | 第11.1节真实S7关联/拒绝矩阵完整成立，Rust R14预检gate先通过；两版均不把坏/迟到响应当good或confirmed，unknown不重发。原AC01–AC14仍独立给证据。（R14/R04/R08–R10/R13） |

“测试流”只为验证同点独立采样与调度，可在tests内实现，不能冒充demo02用户流或引入长期共享采集服务。协议测试依赖真实loopback请求/服务端计数，单元mock不能替代AC03/06–10/13。窗口是有界开发故障验证，长期浸泡/容量/现场运行资格均未覆盖。

### 11.1 新增AC15：S7关联与拒绝矩阵（R14，补充AC03/08/09/10）

AC01–AC14逐行保留。Rust先完成下表全部正/负单元向量，真实协议每行至少一例；原错误ref复现含读及已应用写，header字段逐项单独改变。逐长度截断可用单元向量，真实协议至少短header/短data各一例。请求/native响应/实发响应和实际下发次数必须保存；不能用mock返回或IPC关联替代。任何必需行未执行/失败，AC15不通过。

| 观察/故障 | 必须结果 |
| --- | --- |
| 正常Read/Write和INT五个值 | 匹配ref及完整结构/status，当前good读；写一次且仅匹配正ACK可T3，邻接字节保持，与AC03联合验证。 |
| ref第一/第二字节、旧ref/另一操作ref | Rust首坏即拒绝。两版对仅坏ref且期限内无正确ACK的读无good、写unknown/confirmed=0；actualWriteVar=1。Python若过滤须证明有限、不重发、不刷新总deadline。 |
| ID/ROSCTR/reserved/function/item count各错 | Rust逐字段真实拒绝；父无good/confirmed，不把其他操作ACK当本次ACK。Python原路径也不能接受无关/错误操作成功，否则blocked。 |
| 非零global error或item非FF | 不是正ACK；已进入写保守unknown、不重发，读错误与好值可区分。 |
| parameter/data length不符、短/空/附加/超长 | Rust按Size交叉校验，短包不索引越界/读取旧尾部；4096/4097边界有限loopback注入证明native error或child failure及父实际回收，不声称native安全已修复。 |
| Read transport非04/bit length非16/非2字节；Write多item/多字节 | Rust拒绝，不截断/容忍其他类型；原INT/块边界保留。 |
| 坏ref后紧跟正确ACK；失败/超时后迟到ACK | Rust已失败请求不补T3，旧会话退役、迟到包不归下一job；两版期限后/旧generation不升级unknown。10次GET和原库重启，实际写仍1。 |
| ref近上界/连接恢复/同点并发 | Rust test-only近65535证明同session不复用ref，维护重连不重放；普通AC06窗口仍单持久session/PID、串行归回。 |
| 分段/慢字节/native不返回及stop | 延续AC08/13整体预算，含解析/关闭及真实回收；正常与forced分列，不只waiter返回。 |

精确payload形状/FFI/counter是Rust新增责任；两版公共业务要求仍为匹配正ACK才confirmed、错误/迟到不变好值、unknown不重发。Python原接口若不足，另报精确blocker，不删AC或静默迁移。

## 12. 排除项、风险、回退与外部 gate

排除demo02“PLC上升沿->POST”、通用流程平台/GUI/CA/AI、共享快照/缓存/订阅、第三方API/Backend接入、跨语言状态互换、自动unknown核实/重发、双活热备、服务安装/托管/开机自启、离线安装包/签名/三平台打包、长期浸泡/压力/全型号/真实现场验证；不能因创建runtime就扩大这些范围。

| 风险/未决 | 当前处理与后续 gate |
| --- | --- |
| 已证实driver阶段预算缺口及native未受控Purge | 保留r1失败与源码可达性证据，不称第三方已修好。r3保留r2专属进程总期限；r2已有split/slow局部回收事实，完整IPC、故障回收和parentdeath矩阵仍须证明；不能做到则blocked/QA不通过，不降低预算或转为任意换库/补丁。 |
| 原高层driver缺S7关联；自有codec/FFI新增责任 | Rust只走R14冻结公开API/2字节形状；先预检再全矩阵。长度/ref/错误解析或FFI假设失败即blocked，不放宽T3、不试装其他driver，不把子进程隔离当正确性证明。 |
| 16-bit ref无认证能力及保守断会话 | 严格比较当前session/ref及形状，耗尽前正常换会话；不证明对端身份、抗伪造或工艺完成。真实设备协议变体/安全及兼容性另gate。 |
| 新增进程/IPC/强制故障中止风险 | 增加有限child/控制通道和本地实例锁责任；主/子崩溃、迟到ACK、僵尸/孤儿与IPC背压必须实证。强制中止可能跳过库析构，只能记fault_cleanup，不能撤销PLC已接收写；正常退出仍须自然结束/真实join。首轮仍仅macOS arm64 loopback，不升级为服务托管或跨平台资格。 |
| 本地SQLite与外部写无法原子提交，unknown会保守阻塞 | 保留意图/身份/审计且不重发；r3不提供绕过。真正接收方的幂等、命令寄存器/序号、确认/工艺握手和人工处置另批。 |
| 来源命令时间与真实接口未定 | synthetic同机UTC/TTL完成本地任务即可；真实API路径/鉴权/schema/时钟/命令身份/撤销另gate，不阻塞当前合成任务。 |
| 现场OS/CPU/固件/通信权限/DB优化/工艺互锁未定 | 本轮只验证macOS arm64 loopback；现场PLC型号、PUT/GET/非优化DB条件、点位写归属与目标动作授权另gate，不修改PLC项目或安全设置。 |
| 本机库锁/会话复用不提供跨实例writer排他 | 夹具逐版串行，配置拒绝进程内冲突；实地切换须停止旧writer、核对pending/in_flight/unknown及已确认进度，明确唯一有效写归属后再启新端，不共享库。 |
| 日志/状态容量有限，运行长时后可能停止新写 | 首轮明示上限、背压和保留策略；不靠清库继续，生产归档/保留/备份、资源趋势及托管长稳另gate。 |

回退限本任务源码/diff，不能覆盖其他dirty。已经confirmed或unknown的外部写没有自动反向写回；先停新下发、保留原库/日志/身份再核对。r3不升级既有schema；以后新schema/二进制回退必须先核对兼容，不能删除状态库重新跑。r2错误ref实验库及confirmed记录是失败原始证据，只读保留，不自动修成unknown/抹去失败，也不作为正确确认基线续写。r3仅按原init入口在新任务私有目录创建合成库复验，不推广成现场换库、清库或跳过unknown。回退r2源码只供只读比对，不能重新启用已知不能证明ACK的execute路径；新adapter失败则停写并保留新旧证据。自有临时资源在交接列明，QA仍需的保留；最终验收后由协调器核对归属/占用/证据归档再安全清理，不清理其他任务资源，关键结论不能只存在/tmp。

## 13. 精确delta、批准、交接与PM自检

本r3只增加Rust公开raw ISO入口上的单item DB INT请求/响应adapter、FFI边界/关联证明、受限ref生命周期和AC15。r2全部AC01–AC14原文、YAML/SQLite schema、数值预算、队列/重连、unknown/审计/退出合同保持；细节中只把当前Revision指称更新为r3。依赖版本、原生源码和fixture server不替换，不新增监听端口或现场操作。

r2明确把“不是新增协议实现”和协议边界变更回PM列为限制；此次自行编码/解析原S7 payload并负责FFI及ACK proof是新增实质责任，不能仅称驱动接线自由。故交付具体r3而非请Owner批准抽象选项。Human Owner需精确批准 **FF-001 r3** 的R14/AC15、有限文件与首个预检gate、FFI/许可风险、错误会话退役/unknown和失败回PM规则。r1/r2批准不继承为r3批准，当前仍draft。

PM -> Human Owner：本r3待审；未经精确批准，Development不续。批准后原Development在同bundle更新tasks到r3、保留完整r1/r2历史与证据，先预检gate、再全部Rust矩阵与独立复制、最后Python同例。现有r2 tasks保持dev_blocked是实际阶段，不为checker改成r3/owner_approved。真正developer_handoff后，由协调器实际调用`agent_type="verification", fork_turns="none"`，读取完整bundle/源码/diff/固定manifest/全部证据，逐AC01–AC15出checklist verdict；QA不等于最终Owner验收或发布/现场授权。

主协调器负责实际角色调用、机械导航、窗口/资源收尾；PM只写spec，contract_only，不声称平台ACL或路由强制。原r2资源30个tmp根/50确切PID已absent的记录继续归tasks/resources-checkpoint，PM不重跑或清理；必要证据持久在bundle，不以tmp作唯一事实源。r1/r2批准文件保护副本继续由协调器按复核依赖/最终验收后核对回收。

| 日期 | Revision | 真实阶段 |
| --- | --- | --- |
| 2026-10-21 | r1/r2 | 两次真实批准、起草/自检及失败背景全部保留在下方完整r2归档；Development实测事实继续归tasks/evidence，不重写成完成。 |
| 2026-10-21 | r3 | PM据错误ref被good/confirmed的真实阻塞起草受限公开API adapter；Human Owner精确范围批准pending，未实施r3、无QA/最终验收。 |

本轮PM只读根/FF规则、完整当前bundle、冻结官方crate及直达调用链；当前r2 spec与保护原件一致后才归档。技术选型依据是已锁registry原制品/hash；网络检索与未能读取的版本化Docs页面不充当锁定API或构建证明。未安装候选、执行项目代码/fixture、建库/schema、创建进程/监听器、修改源码/tasks/checklist或写导航。新增adapter、预检及完整AC15均not_run。

PM文档自检（2026-10-21）：个人辅助只读断言exit0；完整r2还原107258字节且与批准后保护原件逐字节一致，嵌套r1还原47049字节及两份SHA256均保持；FF-001/r3/draft元数据唯一、原14条AC逐行一致，原allowlist表/YAML/SQLite schema与状态/审计/数值预算、R03–R10业务合同保持。6个活动本地链接/锚点可解析，本文件无尾随空白；r2 tasks、原24份evidence/manifest、ARCH-TOOL-001完整文件hash未变，Python目录/checklist未创建。主协调器指出并已修正活动allowlist重复标题，原归档不改。此为PM文档自检，不是Development自检、独立QA或全仓治理通过；r3运行验证仍not_run。

协调器文档检查（2026-10-21，PM按主协调器实际回报转录，执行者为协调器）：13份导航机械同步完成，399个本地链接路径/空白检查exit0；根7份导航去除FF行后与批准前baseline完全一致，4份保护hash未变。只读治理脚本exit1、共322行；318条任务外既有诊断多重集保持，FF仅4条：r3 draft与真实r2 tasks的Revision mismatch、要求tasks对应owner_approved各重复2次。此为保留真实历史的已知checker兼容限制；未改tasks、未伪造r3批准或创建checklist，不宣称全仓通过、QA或实施完成。

<a id="r2-approved-history"></a>

## 14. r2完整历史（含原r1归档，无损保留）

以下为批准后r2完整107258字节，SHA256=`1bd11a1dd3ef1dd69ac67943c2a74d0c446f525d4a2378c8cbbb2f05a846a522`。它包括原r1全文/真实批准、r2精确批准、起草/检查/资源历史；所有历史元数据和当时待批描述不作为当前r3状态。外层五反引号block内每个原物理行（含空行）只增加一次`r2|`；去一次前缀并保留其余UTF-8字节/换行，即逐字节还原完整r2。再按其中既有r1规则可还原47049字节、SHA256=13ed64444c5c4df5916adbf8c5f6ae0b668c7c32ef1747b95e560eb1b99bbc70的批准后r1。

<!-- BEGIN FF001 R2 ORIGINAL BYTES -->
`````markdown
r2|Task ID: FF-001
r2|Revision: r2
r2|Status: owner_approved
r2|Owner Role: PM
r2|Allowed Writers: PM, Human Owner
r2|Handoff: Human Owner approved FF-001 r2 on 2026-10-21; handoff to Development in the same bundle; r1 driver blocker/evidence retained; Verification not started
r2|Workflow Mode: STD
r2|Execution Mode: agent_team_same_session
r2|Task Namespace: aiis-ics-arch
r2|Classification: root
r2|Capability: 两个独立语言基础运行时及 demo01 HTTP GET 到 S7 INT 写入的本地合成闭环
r2|Owner: Field Flow
r2|Acceptance Chain Reference: FF-001 r2 精确范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
r2|Related Task: ARCH-TOOL-001
r2|
r2|# FF-001：双语言基础运行时与 demo01 本地闭环
r2|
r2|## 1. 当前授权、目标与事实
r2|
r2|当前为 **FF-001 r2 owner_approved**。Human Owner于2026-10-21明确回复“批准 ff001 r2”，精确批准待审文件SHA256=`d1b48be6c377e72da1dbfd9c925b3b095803432e24bd1b9ba4dbe7e63a113d6a`；主协调器已核对原字节一致，现交接Development在同bundle续接。r1曾于2026-10-21获明确回复“批准 ff001 r1”；批准后完整文件SHA256为`13ed64444c5c4df5916adbf8c5f6ae0b668c7c32ef1747b95e560eb1b99bbc70`。其全文、真实批准与起草/自检原字节封存在[文末r1历史](#r1-approved-history)。r1批准不覆盖本r2新增的driver进程隔离、异常终止及回收边界；本次r2授权来自上述新的精确范围批准，不代表实施完成、QA或最终验收。
r2|
r2|r1 Development已停止正式实现，当前tasks Status为`dev_blocked`；原`blocked_dependency`保留为依赖阻塞原因及历史，不是developer_handoff完成或QA。完整[公开API/源码核查与命令](evidence/driver_api_review.md)、[r1 tasks](tasks.md)、24份真实[证据manifest](evidence/manifest.sha256)均保留。PM首次读取的历史快照tasks SHA256=`de3916c31ab684e3f6eca87398ec462099504b62ade5636de3f1c8f7a998a341`；其后Development依据只读治理检查规范化当前Status并补真实Handoff，Revision仍r1，当前tasks SHA256=`d68e3e01be185ce124dff1387bed5784bf65ecbc9a0510022f066f9a203fbcc3`。manifest SHA256仍为`d046e373c875c236ef1ad9678e1ba6dd9141d5667c92be2bd66ed70acbbd8770`；这些是r1 Development记录，不是PM重跑或独立QA：
r2|
r2|- Python3.0.0公开Client构造/connect没有有效timeout/transport注入；set_param只存储，Client会重建连接并用默认5.0秒。500ms配置的真实静默COTP connect为5003ms；真实WriteVar/ReadVar响应分段3+3秒时分别6019/6018ms，超原R04预算。匹配正ACK、实际write=1、002A与邻接A5保持，不把预算失败误说成重复写。
r2|- Rust1.142.2静默COTP500ms预检通过；正常native协议connect3ms/write1ms/read1ms通过，但5000ms底层参数下真实分段ACK写调用6020ms成功，预算断言exit101。公开参数降为10ms的一条路径write/read各10ms错误返回，server仍已写42；只证明该路径及时失败，不能升级为完整预算通过。
r2|- native源码审计发现可达`Purge()`的raw recv循环无deadline/次数上限，且包括接收失败、disconnect/析构路径；64片/128次正常阶段上界不能封闭所有错误路径。这是源码可达性结论，未实际运行无限挂死场景。已测proxy/thread真实join、server自然exit0和31102/31103/32102/32103释放，分别只属于已执行的局部预检。
r2|
r2|r2选择最小工程方案A：**保留Rust `rust-snap7==1.142.2` 与Python `python-snap7==3.0.0`；每PLC使用一个受监督的独立driver子进程，正常保持一个持久会话，父runtime持有队列、执行状态与总deadline。** 超期限时必须实际终止/等待回收该子进程，不只停止waiter。可能已发送的写仍为unknown；强制终止明确为故障结果及清理，不是正常优雅退出。不采用仅换Python2.1.0、第三方补丁/vendor重构、通用driver平台或现场托管。
r2|
r2|除这一执行隔离边界及对应验收/风险外，两独立工程、先Rust后Python、demo01/INT、业务/时效/状态/日志/队列、原数值预算、allowlist、排除范围均保持。源码、schema、r2新子进程/IPC/强制终止测试在本次批准记录时均未执行；精确r2范围批准gate现已满足，下一步由主协调器实际调用原Development在同bundle续接并保留r1历史。此次PM仅记录批准，不代写tasks或实施。
r2|
r2|本任务与[ARCH-TOOL-001 r2](../ARCH-TOOL-001-field-flow-runner/spec.md)相关，仍是独立能力和批准链，Classification: root，不设Parent Task ID。关联文档及完整历史SHA256继续为`049574ad8fb9e43fcf7073aa217410b28cc21da7100500a28f9887510aac64ae`，本轮不修改。根AGENTS、README/PLAN双语、FF治理文档、实际pm.toml及canonical workflow继续适用。
r2|
r2|## 2. 两阶段写入边界
r2|
r2|### 2.1 PM r2 draft阶段（历史，已完成）
r2|
r2|以下为批准前r2起草阶段的写入边界与当时状态记录；当前已取得精确r2批准并交接Development，后续写入仍严格遵守第2.2节allowlist和角色分工。
r2|
r2|- PM唯一写入路径仍为`field-flow/plans/FF-001-dual-runtime-demo01/spec.md`；完整r1无损封存于本文件，不另建任务或第二事实源。
r2|- 主协调器只机械同步原10份FF/根导航，区分r2 draft/待批与r1驱动预检阻塞；不覆盖r1 tasks或伪造后续角色状态。
r2|- PM只读官方资料及原r1 tasks/evidence、做文档断言；不创建driver/IPC源码、执行子进程/fixture、建库/schema或创建checklist。原r1已执行预检与r2未运行项分别记录。
r2|- 本bundle的r1 tasks/evidence继续保留；r2批准后由原Development在同bundle续接/更新自身Revision，并保留原停止/失败历史。PM不代写tasks，r2 draft不提前把r1记录改为r2。Verification仍在真正developer_handoff之后fresh context执行。
r2|
r2|### 2.2 精确 r2 获批后的 Development allowlist
r2|
r2|| 面 | 允许路径与限制 |
r2|| --- | --- |
r2|| Rust 独立工程 | `field-flow/field-flow-rust/**`：自身 `Cargo.toml`/`Cargo.lock`、少量源码、typed YAML 示例、测试/fixture、locale、`.gitignore`、README/PLAN/catalog 双语与自身 `CODE_INDEX.md`。不得有指向父级/兄弟源码的 path dependency、运行配置或必需服务。 |
r2|| Python 独立工程 | `field-flow/field-flow-python/**`：自身 `pyproject.toml`/`uv.lock`、包入口和源码、typed YAML 示例、测试/fixture、locale、`.gitignore`、README/PLAN/catalog 双语与自身 `CODE_INDEX.md`；自身 `.venv` 和状态/日志均不提交。 |
r2|| 本任务角色事实 | Development 仅创建/维护 `field-flow/plans/FF-001-dual-runtime-demo01/tasks.md`；fresh-context Verification 在 `developer_handoff` 后仅创建/维护 `checklist.md`；有真实证据时才增加本 bundle 的 `evidence/` 附件。PM 继续独占本 spec。 |
r2|| 必要导航 | 上述 FF 六份导航，以及根 `README.md`/`README.zh-CN.md`、`PLAN.md`/`PLAN.zh-CN.md`、`plans/README.md`/`plans/README.zh-CN.md`、`CODE_INDEX.md`，仅 FF 实际入口、真实结构、聚合状态与下一 gate；由主协调器机械同步，不重写其他任务事实。 |
r2|| 私有临时资源 | 未来本任务自建的 `/private/tmp/ff-001-r1-<run-id>/`：语言分开的复制验证目录、私有合成 SQLite、日志、报告；仅显式命令创建，不覆盖既有目录。资源清单与清理触发条件写入 tasks/checklist。 |
r2|
r2|实现子目录的 PLAN/catalog 只导航到 FF 唯一任务 bundle，不复制三文件或创建子任务正文。上述 `**` 仍只允许本 spec 所需少量文件，不能扩成平台建设。构建产物、数据库、运行日志、真实配置、缓存不得提交。
r2|
r2|排除根 AGENTS/ROADMAP、关联 ARCH-TOOL-001 全文件、backend/frontend、AW/DAA/DS/SMA/CA、现有 tools、其他任务及其配置/清单/锁；不安装全局依赖，不改项目外工具链或共享 skill。无 Git refs、commit/push、发布/部署、Docker 操作、真实数据库/PLC/第三方 HTTP 或 PLC 工程修改。保留所有任务外 dirty；不能通过清工作树取得“干净”证据。
r2|
r2|## 3. 路由、依赖与验证平台
r2|
r2|PM 使用 `aiis`、`project-governance` 固定边界和身份。后续 Development/Verification 按实际表面使用 `rust-runtime`（运行时/本地 IO）、`plc-point-mapping`（标准 DB 点位/INT）、`backend-arch`（仅本地执行状态、事务与稳定 key）、`i18n-workflow`（CLI 人类文案）、`code-document-indexer`（关键源码头/真实索引）。不套用 FastAPI/ORM/Celery 模板，不引入 Redis、Python Worker、GUI 或通用 DSL。
r2|
r2|本地合成状态明确使用 SQLite，属于本 r2 的私有轻量执行验证；不更改 backend 主业务数据库，也不把它升级为现场生产默认库。结构变更以本任务显式 schema 版本/维护入口管理，不能借此批准业务库 migration。
r2|
r2|| 项目 | 首轮选择依据与边界 |
r2|| --- | --- |
r2|| Rust | Cargo 独立 binary/library；edition 2021，声明 `rust-version = "1.89"`，首选当前宿主已有 Rust/Cargo 1.89.0。Tokio 1.x、reqwest 0.13.x、serde/serde_json 1.x、serde_yaml 0.9.x、tracing 0.1.x、tracing-subscriber 0.3.x；持久日志可用 tracing-appender 0.2.x，但不能吞掉审计写失败。小型 CLI 可用 clap 4.x。 |
r2|| Rust S7/状态 | 首轮候选精确 `rust-snap7 = 1.142.2`、`rusqlite = 0.32.1`（bundled SQLite），均见现有 DAA 清单/锁；不依赖/复制 DAA/Tauri。已读 registry 缓存的官方 crate manifest/build.rs/client/server 接口：native C++ 编译，提供 DB read/write、client timeout/RemotePort 与 server LocalPort/start_to/register_area。源码接口存在不能证明本工程构建、超时或资源释放。 |
r2|| Python | 独立 uv 工程，Python `>=3.11,<3.14`，自身 `.python-version` 固定 `3.11`，首轮所有锁/构建/运行验证显式选3.11并禁用自动下载；实际已安装解释器缺失则报告，不新增全局安装。asyncio、dataclass/Enum/typing、sqlite3、logging/argparse 可用标准库，HTTP 用 httpx 0.28.x，YAML 用 PyYAML 6.x；严格解析为 typed 对象，不靠隐式类型转换。Python build backend可用hatchling 1.x并锁定实际版本；测试用pytest 8.x或9.x中与Python 3.11兼容的已锁版本。 |
r2|| Python S7 | 保留候选精确 `python-snap7 = 3.0.0`，自身uv锁/环境，不借tools。r1已证实公开Client参数不能约束整体connect/IO期限，故只能在第6节专属driver进程内调用，由父监督器实施整体deadline与真实进程回收；不再把set_param/get_param当有效硬预算。仍须记录有限stale接收及actual WriteVar次数。不得monkeypatch、重装内部transport、私有协商或静默换版本。 |
r2|| 夹具 | Rust 采用自身工程内 test-only Rust binary，包装 `rust-snap7::S7Server`/native server 和 Rust HTTP server；Python 采用自身测试包内 python-snap7 Server 与标准库 HTTP server。各自有本语言 TCP 代理做计数、延迟、断连/丢响应，不能把兄弟版本、DS、backend、Docker 或 Python 桥接作为 Rust 必需服务。 |
r2|
r2|进程/匿名IPC/父存活观察优先使用各语言标准库及已有Tokio；Rust如需POSIX FD、signal或本机文件锁封装，仅允许小范围libc 0.2.x，精确版本/用途由Development入本工程锁和tasks。它只服务本任务子进程生命周期，不是新增协议实现、service manager或通用执行器。Python不增加Rust/native桥接依赖，2.1.0候选及第三方源码修补均未纳入r2。
r2|
r2|其余精确 patch/传递依赖由 Development 在本工程锁中解析并记录来源、checksum、MSRV/解释器兼容；只能在上表候选 family 内择兼容版本，不用 latest URL 冒充冻结。新增相同职责的少量辅助 crate/dev dependency 须先在 tasks 说明必要性；替换 S7 实现、修改第三方源码/协议栈、扩大技术栈或改变验收合同必须返回 PM 新 Revision。锁解析/下载只属于未来获批 Development，不等于构建成功。r1局部预检已执行事实见第1节与原tasks；本轮r2的新进程隔离、兼容/构建/fixture和完整runtime验收均`not_run`。
r2|
r2|2026-10-21 只读宿主版本：macOS 15.7.7（24G720）、arm64、rustc/cargo 1.89.0、uv 0.7.8、Apple clang 17.0.0。该宿主是首轮本地验收平台；Python 3.11 实际 patch、SQLite 实际版本和所有依赖锁由 Development 记录。缺少匹配工具时先报告，不全局升级/安装。Windows/Linux、现场 OS/架构及安装包交付另 gate。
r2|
r2|官方依据只用于选择与约束：[rust-snap7 官方仓库](https://github.com/bruceunx/snap7-rs)、[已读 latest API 页面（当前显示 1.142.3，不能替代候选 1.142.2）](https://docs.rs/rust-snap7/latest/rust_snap7/)、[python-snap7 3.0.0 发布与制品 hash](https://pypi.org/project/python-snap7/3.0.0/)、[3.0.0 client 源码](https://raw.githubusercontent.com/gijzelaerr/python-snap7/3.0.0/snap7/client.py)。非版本化文档只作方向参考，不当作已锁版本 API/构建证明。
r2|
r2|## 4. 有边界的结构与职责（R01）
r2|
r2|每版只建立真实需要的模块，建议如下；允许语言惯用的少量拆分，不要求逐文件镜像。
r2|
r2|```text
r2|field-flow-rust/                 field-flow-python/
r2|  Cargo.toml / Cargo.lock          pyproject.toml / uv.lock
r2|  src/main.rs / lib.rs             src/field_flow/__main__.py / cli.py
r2|  src/commands.rs                 src/field_flow/config.py / domain.py
r2|  src/config.rs / domain.rs        src/field_flow/runtime.py
r2|  src/runtime.rs                  src/field_flow/services/
r2|  src/driver_process.rs            src/field_flow/driver_process.py
r2|  src/services/                   src/field_flow/app/demo01.py
r2|  src/app/demo01.rs                src/field_flow/infrastructure/
r2|  src/infrastructure/              tests/fixtures/ + tests/
r2|  src/bin/ff-fixture.rs            config/loopback.yaml
r2|  tests/support/ + tests/          locales/zh-CN.json / en-US.json
r2|  config/loopback.yaml             README.* / PLAN.* / plans/README.*
r2|  locales/ + README/PLAN/catalog   CODE_INDEX.md / .gitignore
r2|```
r2|
r2|入口/CLI 只解析参数、装配、调用 service/runtime；runtime 只调度、监督、取消和退出。infrastructure 封装 HTTP、PLC、SQLite、文件/日志 IO及私有driver IPC；service 拥有父进程执行状态与事务边界；domain 保留 typed 输入/状态/错误；`app/demo01` 只手写一次有界业务迭代，不能持有无限 while、原始 socket 或 SQL。禁止万能 core、表达式语言、脚本执行、插件框架和预建节点平台。
r2|
r2|driver_process只是本工程私有子进程bootstrap/监督封装：Rust由同一可执行文件的隐藏内部模式启动，Python由自身环境中的同包模块启动；仅接受父进程继承的专用控制通道，不接收shell脚本、任意程序或业务插件，不新增用户flow/监听端口。同步driver只在子进程唯一执行线程创建/持有；HTTP、SQLite、业务service和必要持久审计仍在父进程。辅助父存活/stop观察线程不能执行PLC IO。
r2|
r2|公开示例 YAML 是小份人工审阅的运行配置；JSON 是 locale/机器报告，SQLite 是本地执行事实，JSONL 是日志/证据，四者不互相冒充真相源。不新增 XLSX/TIA/UDT 导入或客户点表。
r2|
r2|## 5. 启动与 typed 配置（R02）
r2|
r2|无参和 `--help` 仅显示帮助、exit 0，不读配置、不联网、不创建日志/状态；错误命令非零。支持 `--lang zh-CN|en-US`，CLI 帮助/错误摘要来自对称 locale key，稳定日志和状态 key 不翻译。`run` 必须显式 `--config`、`--state-dir`，默认 dry-run；只有 `--execute` 才允许 PLC write，运行中不能自动切换模式。
r2|
r2|schema 初始化独立于 run：`state init --synthetic --mode dry_run|execute --state-dir <new-private-path> --instance-id <id>` 只为本任务新建私有合成库。新目录必须不存在；有任意文件/库、软链接或路径冲突则拒绝，不覆盖、不迁移、不清表。`state inspect --state-dir ...` 只读。普通 run 只打开已经初始化、schema_version/implementation/mode/instance_id 匹配的库，缺失/未知/更高 schema 版本均非零退出；不自动执行 DDL。r2 不提供清空、重置、重发 unknown 或状态跨语言迁移命令。
r2|
r2|每版独立示例具有同一形状，端口和私有路径可不同。不得读取父目录/backend/tools 的 `.env`、自动发现 endpoint 或导入兄弟配置。
r2|
r2|```yaml
r2|schema_version: 1
r2|instance_id: ff-rust-demo01       # Python 示例为 ff-python-demo01
r2|plcs:
r2|  - id: plc_demo
r2|    host: 127.0.0.1
r2|    port: 31102                  # Python 示例为 32102
r2|    rack: 0
r2|    slot: 1
r2|    connect_timeout_ms: 3000
r2|    io_timeout_ms: 5000
r2|    queue_capacity: 16
r2|    queue_wait_ms: 2000
r2|    ready_wait_ms: 3000
r2|flows:
r2|  - id: demo01
r2|    kind: demo01
r2|    business_name: synthetic_command_to_int
r2|    interval_ms: 500
r2|    source_id: demo01-feed
r2|    get_url: http://127.0.0.1:31880/demo01/command
r2|    target: {plc_id: plc_demo, db_number: 1, db_size_bytes: 16, byte_offset: 0, type: INT}
r2|    input_max_age_ms: 10000
r2|http: {connect_timeout_ms: 500, total_timeout_ms: 1500, pool_wait_ms: 500, max_connections: 8, max_body_bytes: 4096}
r2|shutdown_timeout_ms: 15000
r2|```
r2|
r2|`id/source_id` 使用 `[A-Za-z0-9_-]{1,64}`；最多 4 个 PLC、8 条注册 flow；重复 ID、同 endpoint 的多个 PLC 定义、未知字段/kind、缺失字段、隐式字符串/数字转换均启动前拒绝。同一进程不能让多个 flow 写重叠的 endpoint/DB/字节范围，即使不同 plc_id 也不能绕过。r2 公开用户流只注册 demo01；并发读能力由测试流验证，不注册 demo02。
r2|
r2|PLC host/port、rack/slot、DB/offset都从typed配置读取；r2的PLC host只接受literal IPv4，不做DNS或地址扫描，公开配置只有loopback和synthetic值。测试/fixture命令只可连接下文列明的127.0.0.1端口。一般配置支持能力不提供对实际目标的联网授权；任何真实地址/第三方调用都留在后续gate。
r2|
r2|本 r2 默认值如上且必须全部有限；允许配置区间：interval 100..10000 ms，HTTP total 100..5000 ms/connect/pool 各100..1500 ms，PLC connect 500..3000 ms（默认与hard cap均3000）、IO 500..5000 ms（默认与hard cap均5000）、queue/ready wait 100..5000 ms、queue capacity 1..16，shutdown 5000..20000 ms；测试降低逻辑容量阈值不能超过第9节上限。run前必须满足`http.connect_timeout_ms <= http.total_timeout_ms`、`http.pool_wait_ms <= http.total_timeout_ms`，以及`shutdown_timeout_ms >= max(全部PLC的connect_timeout_ms、io_timeout_ms、http.total_timeout_ms) + 1500 + 4000`。其中1500ms为状态提交1000ms加调度误差500ms，4000ms为取消、断开、join及日志flush的退出余量；默认5000+1500+4000=10500ms，默认shutdown15000ms符合，关系不满足则启动前拒绝。先同时通知全部owner停止新工作，不逐个等待完IO才通知下一个。ready等待、queue等待、HTTP/PLC调用均有自身配置期限；涉及命令时再取原输入剩余有效期/monotonic deadline的较小值。超时返回不能冒充同步driver已终止，预算内未真实释放仍按R05报告失败。
r2|
r2|## 6. 调度、持久PLC会话、进程故障隔离与退出（R03–R05）
r2|
r2|**R03 调度。** 每个 flow 独立异步任务/监督状态；一次迭代结束后再等待 interval，同 flow 最大在途迭代为 1，无历史 tick 队列和追赶补跑。HTTP 等待、timer 和业务判断都在 PLC 请求之外，不占 PLC 的队列位置/执行锁。某 flow 的 HTTP 超时、输入拒绝或 recoverable 错误不停止独立 flow；全局状态/审计不可写则暂停所有新副作用，读流/健康可以继续。
r2|
r2|**R04 PLC owner与driver进程。** 每个配置PLC由父runtime一个监督owner管理一条FIFO有界队列、一个当前driver子进程及其代次generation；最多4个PLC/4个driver子进程，不按flow/请求创建进程。子进程唯一执行线程创建、持有、调用和关闭一个同步S7 client；正常长期运行保持同一PID/generation及一个S7 session，不逐tick重建。主runtime事件循环不执行同步driver，也不以to_thread/spawn_blocking无限后台调用替代隔离。HTTP/timer不占PLC位置；同点多flow各自采样、无共享缓存/订阅/快照的语义保持。
r2|
r2|所有PLC读写只经父队列派发；子进程无第二工作队列、无业务状态库/重试器，最多一个driver call在途。每flow至多一个待完成请求；request_id/flow_id/generation、typed INT目标/值、操作和剩余期限通过私有匿名pipe或继承的socketpair传递，不新增网络监听器。单消息<=4096 bytes、每方向累计缓冲<=16KiB；读写/解析有截止时间和长度校验，不能无限等换行、阻塞pipe或等待未消费stdout。只接收匹配当前generation/request_id且期限内的结果；IPC坏帧、断开、子进程异常退出或迟到结果不能映射成成功。子进程日志经独立有界通道归父记录，不污染结果通道，也不允许日志阻塞绕过driver总期限。
r2|
r2|owner状态仍为`disconnected -> connecting -> ready -> recovering`及`stopping/stopped`。依赖PLC的操作等待同一owner ready，有限ready等待超时不下发，不各自连接。连接/读错误由owner统一退避，一个周期最多5次connect，间隔250/500/1000/2000ms，失败后cooldown10000ms；ready后成功IO才清连续失败计数。更换子进程也是这条有界恢复路径；旧进程真实退出/回收且IPC关闭前不得启动替身，不在重连或child恢复中重放write。
r2|
r2|**整体预算保持原值，改变的是可验证的执行隔离边界。** 每次connect操作从spawn/IPC bootstrap开始计时，读写从本次dispatch开始计时，包含IPC和故障terminate/kill/wait回收。父监督器以monotonic deadline为权威，使用配置与原输入剩余有效期的较小预算；connect hard cap3000ms、IO hard cap5000ms及最多500ms调度误差均不变。内部固定预留400ms故障回收预算：正常工作及IPC须在整体期限前400ms结束；未结束即向仍属本owner的child发送TERM，最多等待200ms，必要时KILL并在剩余200ms内实际wait/reap。若剩余有效期不足400ms，不进入driver调用，按expired/unavailable拒绝，不追加宽限。正常结果提前返回不需耗尽预留；不能把native每阶段timeout、正常分片次数或参数/2当所有错误/析构路径上界。
r2|
r2|实测整体结束必须同时包括driver进程真实停止（故障时）及匹配结果/明确失败；不能只返回timeout而留下活driver。400ms在原3000/5000ms预算内，500ms只是原有调度误差，不叠加另一段清理宽限。到总期限+500ms仍未实际回收，标`driver_cleanup_incomplete`、阻塞该PLC并报告失败；不得返回“有界成功”、宣称资源已释放或启动替身。native/Python调用可能不能自行返回这一事实如实保留；硬边界来自OS进程隔离，不宣称第三方库已被修好。写permit可能已交付后出现这些错误均按R09进入unknown，late ACK/回读不能升级它。
r2|
r2|跨进程开始下发闸门与stop必须有同一有界串行顺序：父stop先关闭新接纳/派发，再与child的调用前stop/TTL/permit检查协调闭闸。SQLite仍须按R08在T2/prepermit先持久化保守in_flight；它不证明物理调用已开始。只有消费start permit且越过实际调用开始闸门的请求，才可记运行时driver_call_started/正在执行统计。仍在父队列或已交IPC但未过开始闸门的请求必须取消，能证明未执行时按R09记expired/canceled；不能把SQLite in_flight或IPC已交付当实际开始证据绕过queued-stop。测试需在child调用前设置屏障，stop闭闸后证明零下发；不能证明是否已开始的个案保守unknown，并实际回收child。此闸门只保护本实例，不扩成跨主机fencing。
r2|
r2|子进程还须观察父专用存活通道：父异常死亡/控制EOF时，child不得继续收工作或成为孤儿writer；若同步driver卡住，存活观察路径须在500ms内实际结束自身进程，明确属于parent_lost故障中止，不假称正常join。child生命周期持有本实例排他锁的继承份额或等效本地占用，重启父进程不得在旧child仍可能执行时取得同实例writer；只有确认旧代次结束才放行。正常父进程必须wait/reap其child；父被杀时由独立测试harness观测child PID/连接确已消失及旧实例锁释放，不能伪造已死父进程的wait。不得扫描/杀进程名、端口占用者或归属不明PID；此机制不增加服务安装、后台托管或跨实例接管。
r2|
r2|连接复用仍仅进程内这组父/子实例；IO串行不提供command去重或业务效果排他。Rust/Python依次执行夹具；真实现场同资源单一writer、停旧再交接和跨主机排他另gate，不因失联自动接管。driver子进程被终止不能撤销已经送到PLC的写或保证物理动作停止，unknown保守阻断保持。
r2|
r2|**R05 正常退出与故障清理分开。** SIGINT/SIGTERM先按上述闸门停止新接纳/下发并取消未开始队列，所有owner同时进入stopping。在途IO、disconnect/析构和child自然退出共用一个有界stop期限，不为每个阶段重新加整段预算：该期限至多为stop时刻加本配置max(connect_timeout_ms,io_timeout_ms)，且不晚于剩余global shutdown期限。只能在原500ms误差内完成必要故障回收。正常路径须child自行关闭client、辅助线程真实join、exit0，父真实wait/reap；父随后关闭HTTP/SQLite/日志并await/join全部自有任务/线程，才可记正常`resources_released`/`shutdown_complete`。默认15000ms总shutdown预算及R02判断式不变，进程回收已计入原预算，不能另加宽限。
r2|
r2|任何deadline、崩溃、parent_lost或stop超时导致的TERM/KILL/强制process exit都记录`forced_driver_stop`及故障原因/退出状态；只有实际结束/回收才可记`driver_process_reaped`，result必须是fault_cleanup，不使用正常shutdown_complete遮蔽。停止后排队请求不下发；可能已发送写为unknown，confirmed不得倒退。该次运行发生强制中止，最终exit1并保留had_forced_driver_stop；即使读流随后有界恢复，也不改写故障历史。未回收报`shutdown_incomplete`/非零、无释放成功声明。正常成功停止exit0，配置/状态错误exit2，运行/不完整退出exit1；unknown/持久化故障明确非健康。强制中止是本r2拟授权的故障隔离行为，绝不等同于正常优雅退出或现场物理回滚。
r2|
r2|## 7. demo01 输入与 INT 合同（R06–R07）
r2|
r2|**R06 synthetic GET。** 每轮至多一次 GET，复用 HTTP client/pool；不重定向、不用环境代理、不自动应用层重试，不执行 POST。只有 HTTP 200、JSON content type、UTF-8、体积 <=4096 bytes、完整严格 schema 的响应才进入业务规则。错误码、坏 schema、缺失、stale、idle 和正常命令分别有稳定结果 key；不得用默认值、上轮值或缓存值触发写入。
r2|
r2|响应是两个 typed 变体，字段名称/含义仅属本地 fixture，不能说第三方/Backend 已实现：
r2|
r2|```json
r2|{"schema_version":1,"source_id":"demo01-feed","ready":false,"command_id":null,"value":null,"issued_at_ms":null,"expires_at_ms":null}
r2|{"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":"cmd-001","value":42,"issued_at_ms":1792531200000,"expires_at_ms":1792531230000}
r2|```
r2|
r2|时间仅为形状示例，fixture 每个新 ID 用当前 UTC 生成，重复 ID 的字段保持不变。`ready` 必须真 bool；ready=true 时 ID 非空且符合上述 ID 规则，value 必须为 JSON 整数，Python bool/浮点/字符串均拒绝；source_id 必须等于 flow 配置，unknown 字段拒绝。
r2|
r2|`issued_at_ms/expires_at_ms` 为来源 UTC Unix 毫秒整数，是源命令发行/失效时间，不能拿接收时刻代替。命令需满足 `0 < expires-issued <= 60000 ms`、issued 不晚于本机 UTC+1000 ms、未到 expires、且源年龄 <= input_max_age_ms（默认10000，上限60000）。接收时校验一次，真正 driver call 前再次校验；ready/queue等待不能延长原有效期。接收时把剩余有效期绑定到 monotonic deadline，之后同时检查 UTC 与 monotonic，重启仍沿原来源时间；时钟跳变超过1000 ms 时暂停新写并暴露 clock_invalid，不能靠倒拨时钟让旧命令复活。synthetic 来源与运行时使用同机时钟；真实来源时间可信度、同步/签名/TTL/撤销合同另 gate。
r2|
r2|身份是稳定 `(source_id, command_id)`，不含 run_id、重试号或模式。首次合法 ready 命令把 flow_id、目标资源、值、来源时间/有效期、schema版本固定成规范 typed 摘要及 SHA256。相同 ID 同摘要复用原状态；相同 ID 不同值、时效、flow/目标或其他语义字段是 `identity_conflict`，保留原意图，不覆盖/不再次下发，并暂停该写 flow。刷新同 ID 时间不能当新命令；idle 不创建执行命令。
r2|
r2|**R07 INT。** 首轮能力仅标准 DB 绝对地址的有符号 16-bit INT 读写，范围 -32768..32767，严格两个字节、大端二进制补码；-1=FFFF、0=0000、42=002A、上下界须有证据。DB号1..65535、声明的db_size_bytes为2..65536、byte_offset0..65534，须满足offset+2<=db_size_bytes，并在fixture注册的实际块内检查完整范围；配置声明不证明真实PLC块大小。不隐式截断或扩大为整块写。读回带sample/request身份、质量和时间，不把旧值作为好值。BOOL/位写、DINT/REAL、I/Q/M、CPU操作、下载和PLC安全设置均后续另立范围。
r2|
r2|## 8. 本地 SQLite 意图、状态与恢复（R08–R10）
r2|
r2|### R08 最小 schema 与事务
r2|
r2|以下是将来由独立 `state init --synthetic` 创建的 schema 合同，不是本轮可执行 DDL。每版各有自己的 SQLite 文件；本实例排他占用自身state-dir锁，另一实例的writer失败；父进程是唯一DB writer，child仅持有R04所述锁生命周期份额，不开DB、不写状态。不共享可写库，不复制现有业务库。字段使用稳定英文 key；schema_version=1。
r2|
r2|| 表 | 最小字段/约束 |
r2|| --- | --- |
r2|| `store_meta` | 单行，schema_version、implementation=`rust|python`、mode=`dry_run|execute`、instance_id、store_uuid、created_at。模式/实现不匹配拒绝使用。 |
r2|| `commands` | PK `(source_id,command_id)`；flow_id、target_key、config_identity_hash、payload_hash、value_i16（CHECK范围）、issued_at_ms、expires_at_ms、state、dispatch_count（0或1）、run_id、request_id（可空）、last_error_key（可空）、ack_kind（可空）、created_at、updated_at；身份和意图字段插入后不可变。 |
r2|| `command_events` | 单调主键 seq；命令复合FK、run_id/request_id、from_state/to_state、reason_key、必要的脱敏摘要与 created_at；只追加、不覆盖。 |
r2|
r2|`target_key`只表示规范化物理写资源：literal IPv4 endpoint/port、rack/slot、DB、offset、INT长度，不含flow_id、source_id、plc_id别名、run_id或配置文件名。flow_id单独记录命令归属，config_identity_hash另行固定该归属、source绑定和影响命令含义的配置。启动恢复及每次接纳/派发新命令时，必须查原库所有unknown（包括刚由in_flight恢复者）的物理endpoint/DB/字节区间；与目标重叠就阻止写，不能靠换flow_id、source_id、plc_id、配置别名或command_id绕过。原库与原身份必须保留；换库/删库不属于恢复办法。本合同只覆盖本实例及其原私有库，不宣称跨库/跨主机fencing。时间约定：来源字段明确保存外部UTC Unix ms；created_at/updated_at为SQLite UTC数据库时间表达式，操作超时用monotonic，不写入宿主本地时区。原始body、token、URL query不进库/日志。
r2|
r2|SQLite 单 owner/串行状态 executor，不能堵事件循环；busy_timeout 500 ms，事务 deadline 1000 ms，短事务内无外部 IO。首轮 `journal_mode=DELETE`、`synchronous=FULL`、foreign_keys=ON；固定page_size4096、主文件max_page_count16384（64MiB），不使用共享 WAL、网络文件系统或任意自动 schema migration。
r2|
r2|T1：同一事务查身份/冲突，插入 pending 意图与对应 command_event，commit成功后才可准备外部动作。T2：确认mode/TTL/ready/容量/stop/必要审计健康并取得有界队列位置后，以CAS将 pending->in_flight、dispatch_count0->1并追加event，commit后才能把唯一 dispatch permit交给监督owner，经跨进程开始闸门调用一次写入；提交失败不下发。队列交接不得在事务失败后遗留可执行请求。T3：仅在匹配请求的正 S7 write ack 后，同事务 in_flight->confirmed、ack_kind=`s7_protocol`并追加event。确认持久化失败时保留in_flight/unknown事实、暂停新副作用，不回到pending重发。
r2|
r2|父进程是唯一SQLite/command_events和必要持久审计owner；driver child不打开状态库、不自行保存/重试命令。T2必须在任何可能下发的IPC start permit之前commit；child generation/退出事实进入现有脱敏event上下文，不新增业务状态schema。child崩溃、IPC结果丢失或强制结束不能生成新command身份；只读恢复与unknown写阻断仍按原物理资源范围执行。
r2|
r2|### R09 状态含义与转换
r2|
r2|| 状态 | 精确定义与恢复 |
r2|| --- | --- |
r2|| `pending` | 意图已持久，但没有发出过 dispatch permit，dispatch_count=0。重复请求不建新身份；重启后只有当前 GET 再次给出同摘要且原有效期仍有效、配置/目标一致才可继续；不能仅凭库存意图离线重放。 |
r2|| `in_flight` | dispatch_count=1、下发许可已持久，外部调用可能未开始/进行中/已生效；不是成功。重启在任何连接/新下发前统一转 unknown并追加恢复event，即使可能是发送前崩溃也保守处理。 |
r2|| `confirmed` | 收到该请求的正S7协议ack且本地确认事务已commit。重复/重启永不再次写同身份；不代表PLC逻辑接受、工艺完成或物理exactly-once。 |
r2|| `unknown` | 进入driver调用后发生超时/断连/响应丢失/崩溃，或ack/确认持久化无法完整证明。保留原身份/意图/证据，阻止此flow/目标后续写（包括新ID）；重连/下一tick/重启不能自动重发或转confirmed。 |
r2|| `expired` / `canceled` | 可证明未开始driver写：pending过期或停机前取消，或permit交接被owner明确拒绝且未执行。保留记录，不自动重建身份重发。不能证明未发送则unknown。 |
r2|| `simulated` | 仅dry_run库中的would_write观察，dispatch_count=0、ack_kind为空，不入真实执行confirmed；绝不能导入execute库。 |
r2|
r2|合法路径是 pending->in_flight->confirmed/unknown，pending->expired/canceled，以及明确未执行的 in_flight->expired/canceled；后者不得重置dispatch_count再重试。dry_run只记录simulated。坏schema/stale在接纳意图前拒绝；进入pending后的到期沿上述路径留痕。首轮不提供unknown的自动查询/人工改状态CLI；需要核对的工作保持阻塞，另批目标方握手/人工处置方案。
r2|
r2|writer/owner/库恢复和flow健康相互区分：某目标unknown不应停止不相关读流；相同写目标新命令不得绕过。已confirmed之后的日志/后续故障不得把它降回可下发；本轮无结果POST/补投步骤。未来若加回报，只能补报原身份，不能倒退到PLC写。
r2|
r2|### R10 dry-run、失败与能力限度
r2|
r2|dry-run可对获批loopback做GET和S7 read，但PLC写计数必须为0；默认只记录would_write/simulated。初始化时mode固定，dry_run/execute使用两个独立state-dir，交叉打开非零失败。两模式使用同一来源身份语义；dry-run不能占用、确认、复制或重置execute进度，也不能靠切模式消除unknown。
r2|
r2|必须覆盖：T1前失败、T1后发送前重启、T2后调用前崩溃的保守unknown、server已应用但ack丢失、server已应用且进程崩溃、收到ack但T3失败、confirmed重启不重发。所有可能已发送错误保守unknown；库/日志持久化不能与PLC原子提交，S7 ack、SQLite事务或回读同值均不能核实原命令工艺完成或升级unknown为confirmed。回读只作协议数据正确性证据。
r2|
r2|## 9. 日志、健康与容量（R11–R12）
r2|
r2|**R11 可观测性。** stdout与自身state-dir下持久文件均为JSON Lines；最低字段：UTC timestamp、event、implementation、run_id、instance_id、flow_id/target_id、command_id/request_id（适用时）、state/old/new、result、duration_ms/error_key。最低事件包括process/config/state init、owner连接/退避/恢复、flow健康变化、intent/dispatch/ack/unknown/冲突、容量暂停、stop/join/资源释放。普通读不逐tick刷日志，用每5秒progress/health聚合计数；测试专用协议采样trace单独有界保存。
r2|
r2|日志按大小轮转：写入完整JSON行前按大小检查，单文件不超过5MiB、最多4个backup；单行<=4KiB，总文件上限25MiB，既有日志不因启动截断。Rust tracing持久sink必须有实际失败回传；不能用默认忽略IO错误/有损异步队列冒充必要审计。副作用前的意图/dispatch审计须在SQLite事务和持久日志均成功落盘（flush/sync有回执），否则阻止下发；stdout/持久sink故障均停止新副作用并报告health。副作用后审计失败不能抹除或重放已确认动作；保持最后持久in_flight/confirmed并可见报告。审计不依赖可轮转普通日志唯一保存，command_events保留必要状态链。
r2|
r2|健康快照由监督器拥有，至少含每flow的starting/running/recovering/blocked/stopping/stopped、最近迭代/成功、连续错误、owner状态/队列深度/在途数、pending/unknown计数、容量和日志可写性；通过每5秒JSONL及正常退出摘要观察，不新增health HTTP监听器或GUI。idle/无新命令不算失败，进程仍在运行不能冒充flow健康。
r2|
r2|新增必要事件为driver spawn/ready/generation、IPC拒绝、deadline、forced_driver_stop、driver_process_reaped、parent_lost与stop闸门闭合；正常与forced退出分别记录。不得仅看到child.stop返回或PID字段就写资源已释放，父审计失败仍阻止新副作用。
r2|
r2|**R12 容量。** 默认command上限10000条、command_events100000条；接纳新身份前若event>=90000、库主文件>=48MiB、可用磁盘<256MiB或command达上限，则暂停新副作用，保留恢复写余量。主库硬上限64MiB，含rollback journal的state占用上限128MiB；到硬边界失败即阻止新副作用，不能删除pending/unknown/confirmed身份腾空间。读恢复/健康仍有界；不建自动清理、淘汰去重ID或无限离线命令队列。测试可把计数上限降低为10/100或模拟IO错误验证，不需要真实写满磁盘。日志轮转删除旧普通日志前，必要审计已留在command_events；本轮不提供生产归档/保留年限承诺。
r2|
r2|## 10. 本地协议夹具与批准后的拟执行命令（R13）
r2|
r2|以下全部是未来命令合同，当前均 `not_run`。批准精确r2才允许Development创建工程、解析其锁、构建/启动和执行这些合成验证；批准仅覆盖本任务新建私有状态库与loopback，不泛化成真实DB/设备权限。
r2|
r2|| 实现 | 固定端口 |
r2|| --- | --- |
r2|| Rust | S7 client入口/proxy `127.0.0.1:31102`；native S7 server `127.0.0.1:31103`；synthetic HTTP `127.0.0.1:31880` |
r2|| Python | S7 client入口/proxy `127.0.0.1:32102`；自身S7 server `127.0.0.1:32103`；synthetic HTTP `127.0.0.1:32880` |
r2|
r2|每套fixture独立启停，不能绑定wildcard/102、杀占用者或自动换端口；冲突报告并停止该验证。TCP proxy只转发有界TPKT并识别读/写及匹配响应做计数/故障注入，不重写通用S7栈。普通运行一个runtime到该PLC的会话，proxy前后两段TCP属于同一透传S7会话，证据应分别标记，不能把它记为两个独立客户端。server注册内存必须活到fixture真正退出；停止不能提前释放native仍可能使用的buffer。上游native stop返回不是线程join证明，fixture宜进程隔离；父harness等待子进程正常退出并确认端口释放后才算结束，强杀另记失败清理。
r2|
r2|fixture必须能固定同ID响应、发新ID/坏schema/stale/冲突、延迟指定GET、断开/恢复S7、在server已应用写并产生匹配ack后丢弃/扣留该ack、确认实际写计数/字节、在此屏障时终止测试runtime再重启原库。丢包只发生在TCP传输层，不能用mock函数返回unknown替代。正常路径也要真实GET、S7协商、WriteVar和独立协议读回；独立读回安排在runtime停止后，避免污染“正常运行只有一个会话”计数。轻量单元测试补边界，不承担全部协议证据。
r2|
r2|私有driver入口由runtime自身启动，不新增人工运行helper的产品步骤。正式local_protocol测试须增加第11节所列整体deadline、未开始屏障stop、child/parent崩溃与真实回收场景；阻塞测试只针对本任务loopback/自有进程，且父harness有外层回收界限，不能故意留下无限挂死程序。r1已有native分段失败/Purge可达性证据用于定义场景，不冒充r2进程隔离测试已执行。
r2|
r2|从Rust工程目录，拟提供：
r2|
r2|```bash
r2|cargo fmt --check
r2|cargo check --locked --all-targets --features test-fixture
r2|cargo build --locked --bins --features test-fixture
r2|cargo test --locked --lib
r2|cargo test --locked --features test-fixture --test local_protocol -- --test-threads=1
r2|cargo run --locked --bin field-flow --
r2|cargo run --locked --bin field-flow -- state init --synthetic --mode dry_run --state-dir /private/tmp/ff-001-r1-<run-id>/rust/dry --instance-id ff-rust-demo01
r2|cargo run --locked --bin field-flow -- state init --synthetic --mode execute --state-dir /private/tmp/ff-001-r1-<run-id>/rust/execute --instance-id ff-rust-demo01
r2|cargo run --locked --features test-fixture --bin ff-fixture -- --config config/loopback.yaml --evidence-dir /private/tmp/ff-001-r1-<run-id>/rust/fixture
r2|cargo run --locked --bin field-flow -- run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-<run-id>/rust/dry
r2|cargo run --locked --bin field-flow -- run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-<run-id>/rust/execute --execute
r2|```
r2|
r2|从Python工程目录，拟提供：
r2|
r2|```bash
r2|uv lock --check --python 3.11 --no-python-downloads
r2|uv sync --locked --python 3.11 --no-python-downloads
r2|uv build --python 3.11 --no-python-downloads
r2|uv run --locked --python 3.11 --no-python-downloads python -m compileall -q src tests
r2|uv run --locked --python 3.11 --no-python-downloads pytest -q tests/unit
r2|uv run --locked --python 3.11 --no-python-downloads pytest -q tests/test_local_protocol.py
r2|uv run --locked --python 3.11 --no-python-downloads field-flow
r2|uv run --locked --python 3.11 --no-python-downloads field-flow state init --synthetic --mode dry_run --state-dir /private/tmp/ff-001-r1-<run-id>/python/dry --instance-id ff-python-demo01
r2|uv run --locked --python 3.11 --no-python-downloads field-flow state init --synthetic --mode execute --state-dir /private/tmp/ff-001-r1-<run-id>/python/execute --instance-id ff-python-demo01
r2|uv run --locked --python 3.11 --no-python-downloads python -m tests.fixtures --config config/loopback.yaml --evidence-dir /private/tmp/ff-001-r1-<run-id>/python/fixture
r2|uv run --locked --python 3.11 --no-python-downloads field-flow run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-<run-id>/python/dry
r2|uv run --locked --python 3.11 --no-python-downloads field-flow run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-<run-id>/python/execute --execute
r2|```
r2|
r2|`<run-id>`是待执行者生成的唯一目录名，不可照抄尖括号到shell；上述是分终端/由harness顺序运行的命令，fixture需先就绪。首个锁生成在获批Development时显式执行`cargo generate-lockfile`/`uv lock --python 3.11 --no-python-downloads`，之后使用locked命令；本轮不运行。Python自身`.python-version`也为3.11，不能让uv静默选择3.12/3.13或自动下载解释器冒充本平台首轮证据。Development需把最终可复制命令、fixture退出方式、实际命令/退出码/解释器patch/版本/路径和AC证据写入tasks，不能把本节future命令当执行记录。
r2|
r2|还须分别把单个工程复制到本任务新建私有目录，排除target/.venv/dist/状态/日志，隐藏或缺少父/兄弟工程仍按自身README锁定依赖、build/start/test；可以使用正常公共package缓存，不能借另一个工程的源码/可写库/运行fixture。所有有效源码最终在约定交付工作树，复制品的结果不能替代交付树一致性核对。
r2|
r2|## 11. 验收标准
r2|
r2|以下AC每版分别给结果；Rust先完成AC01–AC14的DEV证据，Python再按同一业务矩阵跟进，最终统一fresh-context Verification。技术风险/依赖blocker不能用一版通过替另一版通过，也不能把not_run改为deferred complete。
r2|
r2|| AC | 可观察验收 / 对应需求 |
r2|| --- | --- |
r2|| AC01 | 两版各自独立复制、锁解析、构建、无参/help、显式初始化、启动和测试成功，记录当前平台/工具/锁；私有driver child来自自身可执行文件/同包同环境，随本工程复制构建启动，无父清单/兄弟源码或fixture/环境/可写SQLite依赖；正式交付树与候选一致。（R01/R02/R13） |
r2|| AC02 | 入口分层、typed配置和中英CLI成立；无参无IO；未知/缺失字段、重复ID/endpoint、写范围冲突、非法预算/状态版本/模式拒绝；init不覆盖既有目录，普通run不建schema。（R01/R02/R08/R10） |
r2|| AC03 | 两版demo01有真实GET->S7 INT写->停止后独立S7读回的完整协议证据；INT -32768/-1/0/42/32767正确，越界/float/bool/string及块越界拒绝，邻接字节保持。（R06/R07/R13） |
r2|| AC04 | idle、非200、超体积、坏JSON/schema/source、过期/未来时间/过长TTL均零新写；入队后过期与时钟倒拨不放行，重复ID不刷新时效。输入拒绝与通信故障可区分。（R02/R06） |
r2|| AC05 | 相同命令连续至少10轮、child故障恢复及父进程重启原execute库只产生1次实际写；同ID不同payload/time/target触发冲突且原记录不变；新合法ID才可能产生新写，也不能绕过unknown。同一父SQLite身份不因driver generation变化而重建。（R06/R08/R09） |
r2|| AC06 | 同一PLC下至少3个独立测试读流读同一INT，每流至少20个独立sample/request；正常阶段同一child PID/generation持续复用、S7协商session总数1、driver最大在途1、协议请求串行、每结果归回正确flow。读值不同时间可不同，不伪称共享快照；不逐请求spawn。（R03/R04） |
r2|| AC07 | 一个测试流GET延迟1200ms，另一个读流按100ms间隔在8秒窗口完成至少20轮、最大相邻成功间隔<=500ms；慢流最大在途迭代1，HTTP等待不占PLC执行位置，无补跑tick。（R03/R04） |
r2|| AC08 | server未启动/主动断连时仅owner按原有界策略重连；ready前无IO，恢复后读流继续，坏配置不触发无限重连，独立无关flow继续。两版均在真实静默COTP、分段/慢字节/stale响应、错误恢复或disconnect不响应场景验证整体deadline：含spawn/IPC及必要TERM/KILL/wait回收，connect<=配置且不超3000+500ms、IO不超5000+500ms。真实reap/连接释放前不换child；未回收明确失败，无有界成功或正常优雅退出假象。不能只检查异步waiter返回。（R03–R05） |
r2|| AC09 | T1后发送前重启沿原身份/原TTL处理；T2后不明发送点恢复unknown；真实server已写但ack被丢弃得到unknown，至少再GET10轮和重启后实际写计数仍1。改变flow/source/plc别名、新ID或重叠目标范围都不能绕过原库unknown，读流仍能推进。（R08–R10/R13） |
r2|| AC10 | server写已生效、ack扣留时分别终止driver child及父runtime，原库恢复unknown且不再次下发；父死亡后child在500ms内实际结束，独立harness证明无孤儿PID/连接、原实例锁在旧child结束前阻止重启writer。ack后确认持久化失败也不重发；confirmed不因进程/日志故障倒退，回读同值不能将unknown升级confirmed。（R04/R05/R08–R10/R13） |
r2|| AC11 | dry-run实际GET/read可见、真实write计数0，持久状态仅simulated，confirmed数0；dry_run/execute库交叉打开失败，dry观察不影响execute身份/进度。（R02/R10） |
r2|| AC12 | stdout/持久文件逐行JSON可解析且脱敏，真实轮转边界成立；通过降低计数阈值/注入磁盘/审计失败证明暂停新副作用、保留pending/unknown/confirmed，不需真实填满磁盘；健康能区分recovering/blocked/仍运行。（R11/R12） |
r2|| AC13 | 父队列及child调用前屏障都有待执行请求时正常stop，闭闸后这些请求零下发；默认15秒内正常child exit0/父wait、父任务与owner/观察线程真实join、客户端/库/日志关闭，fixture自然退出且端口/PID释放。另以自有故障child证明deadline强制终止在整体预算内真实回收、operation/该次运行如实失败并记录fault_cleanup，绝不正常shutdown_complete。强制未回收须blocked/incomplete，端口冲突不杀占用者/换端口。（R04/R05/R13） |
r2|| AC14 | 两版README/PLAN/catalog/locale/索引与实际相符，tasks记录逐AC命令、退出码、实际资源和未验gate；fresh-context命名Verification独立出checklist verdict；Human Owner最终验收仍单独待决定。（R01–R13） |
r2|
r2|“测试流”只为验证同点独立采样与调度，可在tests内实现，不能冒充demo02用户流或引入长期共享采集服务。协议测试依赖真实loopback请求/服务端计数，单元mock不能替代AC03/06–10/13。窗口是有界开发故障验证，长期浸泡/容量/现场运行资格均未覆盖。
r2|
r2|## 12. 排除项、风险、回退与外部 gate
r2|
r2|排除demo02“PLC上升沿->POST”、通用流程平台/GUI/CA/AI、共享快照/缓存/订阅、第三方API/Backend接入、跨语言状态互换、自动unknown核实/重发、双活热备、服务安装/托管/开机自启、离线安装包/签名/三平台打包、长期浸泡/压力/全型号/真实现场验证；不能因创建runtime就扩大这些范围。
r2|
r2|| 风险/未决 | 当前处理与后续 gate |
r2|| --- | --- |
r2|| 已证实driver阶段预算缺口及native未受控Purge | 保留r1失败与源码可达性证据，不称第三方已修好。r2拟以专属进程实施总期限，必须在批准后实际证明IPC、故障终止/回收和parentdeath路径；不能做到则blocked/QA不通过，不降低预算或转为任意换库/补丁。 |
r2|| 新增进程/IPC/强制故障中止风险 | 增加有限child/控制通道和本地实例锁责任；主/子崩溃、迟到ACK、僵尸/孤儿与IPC背压必须实证。强制中止可能跳过库析构，只能记fault_cleanup，不能撤销PLC已接收写；正常退出仍须自然结束/真实join。首轮仍仅macOS arm64 loopback，不升级为服务托管或跨平台资格。 |
r2|| 本地SQLite与外部写无法原子提交，unknown会保守阻塞 | 保留意图/身份/审计且不重发；r2不提供绕过。真正接收方的幂等、命令寄存器/序号、确认/工艺握手和人工处置另批。 |
r2|| 来源命令时间与真实接口未定 | synthetic同机UTC/TTL完成本地任务即可；真实API路径/鉴权/schema/时钟/命令身份/撤销另gate，不阻塞当前合成任务。 |
r2|| 现场OS/CPU/固件/通信权限/DB优化/工艺互锁未定 | 本轮只验证macOS arm64 loopback；现场PLC型号、PUT/GET/非优化DB条件、点位写归属与目标动作授权另gate，不修改PLC项目或安全设置。 |
r2|| 本机库锁/会话复用不提供跨实例writer排他 | 夹具逐版串行，配置拒绝进程内冲突；实地切换须停止旧writer、核对pending/in_flight/unknown及已确认进度，明确唯一有效写归属后再启新端，不共享库。 |
r2|| 日志/状态容量有限，运行长时后可能停止新写 | 首轮明示上限、背压和保留策略；不靠清库继续，生产归档/保留/备份、资源趋势及托管长稳另gate。 |
r2|
r2|回退限本任务源码/diff，不能覆盖其他dirty。已经confirmed或unknown的外部写没有自动反向写回；先停新下发、保留原库/日志/身份再核对。r2不升级既有schema；以后新schema/二进制回退必须先核对兼容，不能删除状态库重新跑。自有临时资源在交接列明，QA仍需的保留；最终验收后由协调器核对归属/占用/证据归档再安全清理，不清理其他任务资源，关键结论不能只存在/tmp。
r2|
r2|## 13. 精确delta、批准与交接
r2|
r2|r2相对r1的实质delta仅为：保留两原候选，PLC同步IO由同进程专用线程改为每PLC受监督的常驻driver子进程；父owner新增有界私有IPC、整体预算内预留回收、正常退出/强制故障清理分列、parentdeath/原实例锁及跨进程start-stop闸门。对应R01/R04/R05/R08/R11/R13及AC01/05/06/08/10/13补充这些可观察证据；原业务、INT/来源时效/身份、SQLite schema/unknown/审计、队列/重连、全部数值预算与allowlist/排除项不降标。AC02/03/04/07/09/11/12/14保持原文。新helper不成为业务平台或现场后台服务，不授权第三方源码patch/vendor、2.1.0替换或真实目标操作。
r2|
r2|Human Owner于2026-10-21明确回复“批准 ff001 r2”，精确批准 **FF-001 r2**：上述新增进程/IPC及异常TERM/KILL/回收风险、整体deadline的执行定义、normal与fault退出语义、父死亡/锁/queued-stop验收。本次比r1改变了执行与故障边界，已取得独立的r2精确批准；r1的“批准 ff001 r1”及其已测局部成功不构成r2授权。批准对象为第1节SHA256对应的完整待审稿；本次仅增加真实批准和交接事实，不修改Revision、范围、需求、AC、allowlist、预算或风险。
r2|
r2|PM -> Development：精确FF-001 r2已获Human Owner范围批准，由主协调器实际调用Development在同bundle继续，更新自己tasks到精确r2并保留r1 blocked_dependency、24份证据/manifest和未运行项，不重建任务、不覆盖失败历史。本次批准记录时现有tasks仍是r1的Development事实；由Development如实续接，不由PM伪造同步或实施结果。实际developer_handoff完成后，主协调器才以`agent_type="verification", fork_turns="none"`启动独立Verification读取完整bundle/实现/diff/证据，形成checklist verdict；qa_passed仍只进入Human Owner最终验收，不授权现场/发布/部署/推送。
r2|
r2|主协调器负责角色实际调用、串行handoff与机械导航，PM只写spec；profile为contract_only，不宣称平台ACL或强制路由。范围、allowlist、验收或风险实质变化继续回PM新Revision及Human Owner精确批准。
r2|
r2|| 日期 | Revision | 范围/批准事实 |
r2|| --- | --- | --- |
r2|| 2026-10-21 | r1 | 起草、Human Owner明确批准“批准 ff001 r1”、PM/协调器自检原文完整保留于第14节；r1 Development局部预检及blocked_dependency仍归原tasks/evidence。 |
r2|| 2026-10-21 | r2 | PM根据两版预算预检及native Purge可达性提出常驻driver子进程隔离draft；起草时精确Human Owner范围批准pending。未运行r2实现、项目测试/fixture、schema或新故障终止实验；无QA/最终验收。 |
r2|| 2026-10-21 | r2 | Human Owner明确回复“批准 ff001 r2”，精确批准待审SHA256为d1b48be6c377e72da1dbfd9c925b3b095803432e24bd1b9ba4dbe7e63a113d6a的FF-001 r2；Status改为owner_approved并交接Development。仅记录批准/阶段事实，完整合同及r1归档不变；尚无r2实施完成、QA或最终验收。 |
r2|
r2|PM本轮只读消费r1 tasks和24份真实evidence，并做本文件的身份/链接/保留范围/原r1还原断言；不代替Development执行技术验证。r2进程隔离的安装/构建/运行、整体期限、IPC/父死亡/正常及强制回收、完整AC均not_run。r1局部probe已执行不写成r2已通过；当源码可达性仍有风险，不以未实测的定制保证填补。
r2|
r2|2026-10-21 PM起草阶段文档自检（历史）：只读文档断言exit0，该次FF-001/r2/draft元数据唯一、AC01–AC14齐全；5个当时本地链接/锚点可解析，原allowlist/YAML/预算判断式及AC02/03/04/07/09/11/12/14保持。r1归档还原47049字节，与批准后原文件逐字节一致且SHA256仍为13ed64444c5c4df5916adbf8c5f6ae0b668c7c32ef1747b95e560eb1b99bbc70；该次自检中r1 tasks与首次读取快照一致，后续元数据规范化及读取时hash见第1节；manifest及其24份evidence、关联ARCH-TOOL-001完整文件hash未变。未创建实现目录或checklist，未发现本文件尾随空白。此为PM文档自检，不是Development自检、独立QA、全仓治理检查通过或最终验收；本次批准记录时r2所有运行验证仍not_run。
r2|
r2|协调器起草阶段文档检查（历史，2026-10-21，PM按主协调器实际回报转录，执行者为协调器）：405个local links及空白检查exit0；11份机械导航的根入口改动仅FF行，AGENTS/ROADMAP双语/ARCH-TOOL-001保护hash不变；当时正式源码目录和checklist仍无。只读check-governance的root-only运行exit1、有318条任务外诊断；root+field-flow运行exit1、有322条，额外4条仅为旧checker对“r2 draft与真实r1 tasks保留”的Revision mismatch及要求owner_approved各重复2条。两次非FF诊断多重集完全相同；缺Handoff、不合法Status及PLAN link问题已实际修正。未为通过checker伪造r2批准、改写r1实施历史或创建checklist。此为文档阶段已知checker兼容限制，不宣称全仓检查通过、独立QA或实施完成。
r2|
r2|协调器私有资源`/private/tmp/ff-001-r1-coordinator-5f_w4ntt`用于批准后r1原字节/保护hash、导航差异与只读治理日志；起草时为r2待审保留，批准后继续供后续复核，不运行进程。关键事实已在本spec/任务evidence持久化，不以该tmp为唯一证据；Owner最终验收或不再需要复核时，由协调器核对占用后回收。Development私有资源清单及保留条件仍归r1 tasks，不在此改写。
r2|
r2|<a id="r1-approved-history"></a>
r2|
r2|## 14. r1完整历史（批准后原字节无损封存）
r2|
r2|本节是2026-10-21批准后FF-001 r1的完整文件，包括原draft叙述、真实批准和PM/协调器自检；不是当前r2元数据或新执行授权。原文件47049字节，SHA256=`13ed64444c5c4df5916adbf8c5f6ae0b668c7c32ef1747b95e560eb1b99bbc70`。下方fenced block内每个原始物理行（含空行）增加且只增加一个`r1|`前缀；去此前缀并原样保留其余UTF-8字节/换行，应逐字节还原原文件，包括末尾换行。原相对链接按同一bundle历史解释，不作为r2新证据。
r2|
r2|<!-- BEGIN FF001 R1 ORIGINAL BYTES -->
r2|````markdown
r2|r1|Task ID: FF-001
r2|r1|Revision: r1
r2|r1|Status: owner_approved
r2|r1|Owner Role: PM
r2|r1|Allowed Writers: PM, Human Owner
r2|r1|Handoff: Human Owner approved FF-001 r1 on 2026-10-21; handoff to Development for planning and implementation; Verification not started
r2|r1|Workflow Mode: STD
r2|r1|Execution Mode: agent_team_same_session
r2|r1|Task Namespace: aiis-ics-arch
r2|r1|Classification: root
r2|r1|Capability: 两个独立语言基础运行时及 demo01 HTTP GET 到 S7 INT 写入的本地合成闭环
r2|r1|Owner: Field Flow
r2|r1|Acceptance Chain Reference: FF-001 r1 精确范围批准 -> Development -> fresh-context QA / Verification -> Human Owner 最终验收
r2|r1|Related Task: ARCH-TOOL-001
r2|r1|
r2|r1|# FF-001：双语言基础运行时与 demo01 本地闭环
r2|r1|
r2|r1|## 1. 当前授权、目标与事实
r2|r1|
r2|r1|Human Owner于2026-10-21明确回复“批准 ff001 r1”，批准精确任务 **FF-001 r1**；批准前交付文件SHA256为`fb2477e66954aea20adc3b463ef9c62871371a26a9c5265ff755aab495884d00`，主协调器已核对与待批准版本一致。当前状态为`owner_approved`，进入Development计划/实施交接；角色实际调用与导航同步由主协调器负责。此次仅记录真实范围批准，不代表Development已完成、QA通过、最终验收或任何范围外动作授权。
r2|r1|
r2|r1|以下四段保留为批准前的PM起草历史，其中“本轮”“当前”“后续批准”均指起草时点：
r2|r1|
r2|r1|本轮只创建这份中文优先的 PM 实施规格，由主协调器机械同步必要双语导航，然后交 Human Owner 审阅精确 `FF-001 r1`。当前是 `draft`；尚无本任务范围批准、Development 计划/实现、自检、独立 QA 或最终验收。不提前创建 `tasks.md`、`checklist.md`、两个实现子目录、依赖清单、数据库或监听器。
r2|r1|
r2|r1|目标是在后续精确批准后，先完成 Rust 的一个可独立复制、构建、启动、测试的本地闭环，再用 Python 完成同一业务和故障验收。两者均为独立工程，不将 Python 降为参考脚本，也不以双实现表示双活或热备。首轮只交付手写 `demo01`，验证基础运行时和恢复合同；它是未来现场能力的本地合成开发基线，不能宣称生产资格。
r2|r1|
r2|r1|本任务与 [ARCH-TOOL-001 r2](../ARCH-TOOL-001-field-flow-runner/spec.md) 相关，但交付能力和批准链独立，故 `Classification: root`，不设 `Parent Task ID`。该文档基线及其完整 r1 历史逐字节不变；起草前全文件 SHA256 为 `049574ad8fb9e43fcf7073aa217410b28cc21da7100500a28f9887510aac64ae`。关联不继承其任何批准、状态、验收、写权限或未来案例。
r2|r1|
r2|r1|已读取根 [AGENTS.md](../../../AGENTS.md)、README/PLAN 双语、FF README/PLAN/catalog 双语、完整关联 spec、实际 `.codex/agents/pm.toml` 与 [canonical workflow](../../../.codex/workflows/development-lifecycle-workflow.md)。起草前根 `plans/` 与 FF `plans/` 未发现 FF-001，目标目录不存在。导航是索引，范围以本文件为准。
r2|r1|
r2|r1|## 2. 两阶段写入边界
r2|r1|
r2|r1|### 2.1 PM draft阶段（历史，已完成）
r2|r1|
r2|r1|本小节保留起草阶段边界；2026-10-21精确r1已获Human Owner批准，当前Development交接按第2.2节及第13节执行。本次PM仍只更新本spec批准记录，不创建其他角色文件或实现。
r2|r1|
r2|r1|- PM 唯一写入路径：`field-flow/plans/FF-001-dual-runtime-demo01/spec.md`。
r2|r1|- 主协调器只机械同步 `field-flow/README.md`、`README.zh-CN.md`、`PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`，以及根 `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md` 中 FF 导航；只表达 r1 draft、下一批准 gate 和不存在的后续角色文档。
r2|r1|- 本轮不运行项目程序、项目测试、fixture、schema 或任何初始化命令；只读官方资料、现有清单/锁及系统工具版本，允许个人辅助文档断言与差异/链接检查。
r2|r1|
r2|r1|### 2.2 精确 r1 获批后的 Development allowlist
r2|r1|
r2|r1|| 面 | 允许路径与限制 |
r2|r1|| --- | --- |
r2|r1|| Rust 独立工程 | `field-flow/field-flow-rust/**`：自身 `Cargo.toml`/`Cargo.lock`、少量源码、typed YAML 示例、测试/fixture、locale、`.gitignore`、README/PLAN/catalog 双语与自身 `CODE_INDEX.md`。不得有指向父级/兄弟源码的 path dependency、运行配置或必需服务。 |
r2|r1|| Python 独立工程 | `field-flow/field-flow-python/**`：自身 `pyproject.toml`/`uv.lock`、包入口和源码、typed YAML 示例、测试/fixture、locale、`.gitignore`、README/PLAN/catalog 双语与自身 `CODE_INDEX.md`；自身 `.venv` 和状态/日志均不提交。 |
r2|r1|| 本任务角色事实 | Development 仅创建/维护 `field-flow/plans/FF-001-dual-runtime-demo01/tasks.md`；fresh-context Verification 在 `developer_handoff` 后仅创建/维护 `checklist.md`；有真实证据时才增加本 bundle 的 `evidence/` 附件。PM 继续独占本 spec。 |
r2|r1|| 必要导航 | 上述 FF 六份导航，以及根 `README.md`/`README.zh-CN.md`、`PLAN.md`/`PLAN.zh-CN.md`、`plans/README.md`/`plans/README.zh-CN.md`、`CODE_INDEX.md`，仅 FF 实际入口、真实结构、聚合状态与下一 gate；由主协调器机械同步，不重写其他任务事实。 |
r2|r1|| 私有临时资源 | 未来本任务自建的 `/private/tmp/ff-001-r1-<run-id>/`：语言分开的复制验证目录、私有合成 SQLite、日志、报告；仅显式命令创建，不覆盖既有目录。资源清单与清理触发条件写入 tasks/checklist。 |
r2|r1|
r2|r1|实现子目录的 PLAN/catalog 只导航到 FF 唯一任务 bundle，不复制三文件或创建子任务正文。上述 `**` 仍只允许本 spec 所需少量文件，不能扩成平台建设。构建产物、数据库、运行日志、真实配置、缓存不得提交。
r2|r1|
r2|r1|排除根 AGENTS/ROADMAP、关联 ARCH-TOOL-001 全文件、backend/frontend、AW/DAA/DS/SMA/CA、现有 tools、其他任务及其配置/清单/锁；不安装全局依赖，不改项目外工具链或共享 skill。无 Git refs、commit/push、发布/部署、Docker 操作、真实数据库/PLC/第三方 HTTP 或 PLC 工程修改。保留所有任务外 dirty；不能通过清工作树取得“干净”证据。
r2|r1|
r2|r1|## 3. 路由、依赖与验证平台
r2|r1|
r2|r1|PM 使用 `aiis`、`project-governance` 固定边界和身份。后续 Development/Verification 按实际表面使用 `rust-runtime`（运行时/本地 IO）、`plc-point-mapping`（标准 DB 点位/INT）、`backend-arch`（仅本地执行状态、事务与稳定 key）、`i18n-workflow`（CLI 人类文案）、`code-document-indexer`（关键源码头/真实索引）。不套用 FastAPI/ORM/Celery 模板，不引入 Redis、Python Worker、GUI 或通用 DSL。
r2|r1|
r2|r1|本地合成状态明确使用 SQLite，属于本 r1 的私有轻量执行验证；不更改 backend 主业务数据库，也不把它升级为现场生产默认库。结构变更以本任务显式 schema 版本/维护入口管理，不能借此批准业务库 migration。
r2|r1|
r2|r1|| 项目 | 首轮选择依据与边界 |
r2|r1|| --- | --- |
r2|r1|| Rust | Cargo 独立 binary/library；edition 2021，声明 `rust-version = "1.89"`，首选当前宿主已有 Rust/Cargo 1.89.0。Tokio 1.x、reqwest 0.13.x、serde/serde_json 1.x、serde_yaml 0.9.x、tracing 0.1.x、tracing-subscriber 0.3.x；持久日志可用 tracing-appender 0.2.x，但不能吞掉审计写失败。小型 CLI 可用 clap 4.x。 |
r2|r1|| Rust S7/状态 | 首轮候选精确 `rust-snap7 = 1.142.2`、`rusqlite = 0.32.1`（bundled SQLite），均见现有 DAA 清单/锁；不依赖/复制 DAA/Tauri。已读 registry 缓存的官方 crate manifest/build.rs/client/server 接口：native C++ 编译，提供 DB read/write、client timeout/RemotePort 与 server LocalPort/start_to/register_area。源码接口存在不能证明本工程构建、超时或资源释放。 |
r2|r1|| Python | 独立 uv 工程，Python `>=3.11,<3.14`，自身 `.python-version` 固定 `3.11`，首轮所有锁/构建/运行验证显式选3.11并禁用自动下载；实际已安装解释器缺失则报告，不新增全局安装。asyncio、dataclass/Enum/typing、sqlite3、logging/argparse 可用标准库，HTTP 用 httpx 0.28.x，YAML 用 PyYAML 6.x；严格解析为 typed 对象，不靠隐式类型转换。Python build backend可用hatchling 1.x并锁定实际版本；测试用pytest 8.x或9.x中与Python 3.11兼容的已锁版本。 |
r2|r1|| Python S7 | 首轮候选精确 `python-snap7 = 3.0.0`，与 tools 当前锁及官方版本发布摘要一致，为纯 Python 协议实现；不借 tools 环境。其版本化 client 源码虽有 timeout 参数存储，但不能仅凭 `set_param()` 名称推断 connect/底层 socket 已执行同一预算；Development 必须验证实际调用链、有限 stale 接收次数及无重复 write。不能满足本合同则报告 blocker，不静默保留无效 timeout。 |
r2|r1|| 夹具 | Rust 采用自身工程内 test-only Rust binary，包装 `rust-snap7::S7Server`/native server 和 Rust HTTP server；Python 采用自身测试包内 python-snap7 Server 与标准库 HTTP server。各自有本语言 TCP 代理做计数、延迟、断连/丢响应，不能把兄弟版本、DS、backend、Docker 或 Python 桥接作为 Rust 必需服务。 |
r2|r1|
r2|r1|其余精确 patch/传递依赖由 Development 在本工程锁中解析并记录来源、checksum、MSRV/解释器兼容；只能在上表候选 family 内择兼容版本，不用 latest URL 冒充冻结。新增相同职责的少量辅助 crate/dev dependency 须先在 tasks 说明必要性；替换 S7 实现、修改第三方源码/协议栈、扩大技术栈或改变验收合同必须返回 PM 新 Revision。锁解析/下载只属于未来获批 Development，不等于构建成功。本轮上述兼容、安装、构建与 fixture 均 `not_run`。
r2|r1|
r2|r1|2026-10-21 只读宿主版本：macOS 15.7.7（24G720）、arm64、rustc/cargo 1.89.0、uv 0.7.8、Apple clang 17.0.0。该宿主是首轮本地验收平台；Python 3.11 实际 patch、SQLite 实际版本和所有依赖锁由 Development 记录。缺少匹配工具时先报告，不全局升级/安装。Windows/Linux、现场 OS/架构及安装包交付另 gate。
r2|r1|
r2|r1|官方依据只用于选择与约束：[rust-snap7 官方仓库](https://github.com/bruceunx/snap7-rs)、[已读 latest API 页面（当前显示 1.142.3，不能替代候选 1.142.2）](https://docs.rs/rust-snap7/latest/rust_snap7/)、[python-snap7 3.0.0 发布与制品 hash](https://pypi.org/project/python-snap7/3.0.0/)、[3.0.0 client 源码](https://raw.githubusercontent.com/gijzelaerr/python-snap7/3.0.0/snap7/client.py)。非版本化文档只作方向参考，不当作已锁版本 API/构建证明。
r2|r1|
r2|r1|## 4. 有边界的结构与职责（R01）
r2|r1|
r2|r1|每版只建立真实需要的模块，建议如下；允许语言惯用的少量拆分，不要求逐文件镜像。
r2|r1|
r2|r1|```text
r2|r1|field-flow-rust/                 field-flow-python/
r2|r1|  Cargo.toml / Cargo.lock          pyproject.toml / uv.lock
r2|r1|  src/main.rs / lib.rs             src/field_flow/__main__.py / cli.py
r2|r1|  src/commands.rs                 src/field_flow/config.py / domain.py
r2|r1|  src/config.rs / domain.rs        src/field_flow/runtime.py
r2|r1|  src/runtime.rs                  src/field_flow/services/
r2|r1|  src/services/                   src/field_flow/app/demo01.py
r2|r1|  src/app/demo01.rs                src/field_flow/infrastructure/
r2|r1|  src/infrastructure/              tests/fixtures/ + tests/
r2|r1|  src/bin/ff-fixture.rs            config/loopback.yaml
r2|r1|  tests/support/ + tests/          locales/zh-CN.json / en-US.json
r2|r1|  config/loopback.yaml             README.* / PLAN.* / plans/README.*
r2|r1|  locales/ + README/PLAN/catalog   CODE_INDEX.md / .gitignore
r2|r1|```
r2|r1|
r2|r1|入口/CLI 只解析参数、装配、调用 service/runtime；runtime 只调度、监督、取消和退出。infrastructure 封装 HTTP、PLC、SQLite、文件/日志 IO；service 拥有执行状态与事务边界；domain 保留 typed 输入/状态/错误；`app/demo01` 只手写一次有界业务迭代，不能持有无限 while、原始 socket 或 SQL。禁止万能 core、表达式语言、脚本执行、插件框架和预建节点平台。
r2|r1|
r2|r1|公开示例 YAML 是小份人工审阅的运行配置；JSON 是 locale/机器报告，SQLite 是本地执行事实，JSONL 是日志/证据，四者不互相冒充真相源。不新增 XLSX/TIA/UDT 导入或客户点表。
r2|r1|
r2|r1|## 5. 启动与 typed 配置（R02）
r2|r1|
r2|r1|无参和 `--help` 仅显示帮助、exit 0，不读配置、不联网、不创建日志/状态；错误命令非零。支持 `--lang zh-CN|en-US`，CLI 帮助/错误摘要来自对称 locale key，稳定日志和状态 key 不翻译。`run` 必须显式 `--config`、`--state-dir`，默认 dry-run；只有 `--execute` 才允许 PLC write，运行中不能自动切换模式。
r2|r1|
r2|r1|schema 初始化独立于 run：`state init --synthetic --mode dry_run|execute --state-dir <new-private-path> --instance-id <id>` 只为本任务新建私有合成库。新目录必须不存在；有任意文件/库、软链接或路径冲突则拒绝，不覆盖、不迁移、不清表。`state inspect --state-dir ...` 只读。普通 run 只打开已经初始化、schema_version/implementation/mode/instance_id 匹配的库，缺失/未知/更高 schema 版本均非零退出；不自动执行 DDL。r1 不提供清空、重置、重发 unknown 或状态跨语言迁移命令。
r2|r1|
r2|r1|每版独立示例具有同一形状，端口和私有路径可不同。不得读取父目录/backend/tools 的 `.env`、自动发现 endpoint 或导入兄弟配置。
r2|r1|
r2|r1|```yaml
r2|r1|schema_version: 1
r2|r1|instance_id: ff-rust-demo01       # Python 示例为 ff-python-demo01
r2|r1|plcs:
r2|r1|  - id: plc_demo
r2|r1|    host: 127.0.0.1
r2|r1|    port: 31102                  # Python 示例为 32102
r2|r1|    rack: 0
r2|r1|    slot: 1
r2|r1|    connect_timeout_ms: 3000
r2|r1|    io_timeout_ms: 5000
r2|r1|    queue_capacity: 16
r2|r1|    queue_wait_ms: 2000
r2|r1|    ready_wait_ms: 3000
r2|r1|flows:
r2|r1|  - id: demo01
r2|r1|    kind: demo01
r2|r1|    business_name: synthetic_command_to_int
r2|r1|    interval_ms: 500
r2|r1|    source_id: demo01-feed
r2|r1|    get_url: http://127.0.0.1:31880/demo01/command
r2|r1|    target: {plc_id: plc_demo, db_number: 1, db_size_bytes: 16, byte_offset: 0, type: INT}
r2|r1|    input_max_age_ms: 10000
r2|r1|http: {connect_timeout_ms: 500, total_timeout_ms: 1500, pool_wait_ms: 500, max_connections: 8, max_body_bytes: 4096}
r2|r1|shutdown_timeout_ms: 15000
r2|r1|```
r2|r1|
r2|r1|`id/source_id` 使用 `[A-Za-z0-9_-]{1,64}`；最多 4 个 PLC、8 条注册 flow；重复 ID、同 endpoint 的多个 PLC 定义、未知字段/kind、缺失字段、隐式字符串/数字转换均启动前拒绝。同一进程不能让多个 flow 写重叠的 endpoint/DB/字节范围，即使不同 plc_id 也不能绕过。r1 公开用户流只注册 demo01；并发读能力由测试流验证，不注册 demo02。
r2|r1|
r2|r1|PLC host/port、rack/slot、DB/offset都从typed配置读取；r1的PLC host只接受literal IPv4，不做DNS或地址扫描，公开配置只有loopback和synthetic值。测试/fixture命令只可连接下文列明的127.0.0.1端口。一般配置支持能力不提供对实际目标的联网授权；任何真实地址/第三方调用都留在后续gate。
r2|r1|
r2|r1|本 r1 默认值如上且必须全部有限；允许配置区间：interval 100..10000 ms，HTTP total 100..5000 ms/connect/pool 各100..1500 ms，PLC connect 500..3000 ms（默认与hard cap均3000）、IO 500..5000 ms（默认与hard cap均5000）、queue/ready wait 100..5000 ms、queue capacity 1..16，shutdown 5000..20000 ms；测试降低逻辑容量阈值不能超过第9节上限。run前必须满足`http.connect_timeout_ms <= http.total_timeout_ms`、`http.pool_wait_ms <= http.total_timeout_ms`，以及`shutdown_timeout_ms >= max(全部PLC的connect_timeout_ms、io_timeout_ms、http.total_timeout_ms) + 1500 + 4000`。其中1500ms为状态提交1000ms加调度误差500ms，4000ms为取消、断开、join及日志flush的退出余量；默认5000+1500+4000=10500ms，默认shutdown15000ms符合，关系不满足则启动前拒绝。先同时通知全部owner停止新工作，不逐个等待完IO才通知下一个。ready等待、queue等待、HTTP/PLC调用均有自身配置期限；涉及命令时再取原输入剩余有效期/monotonic deadline的较小值。超时返回不能冒充同步driver已终止，预算内未真实释放仍按R05报告失败。
r2|r1|
r2|r1|## 6. 调度、持久 PLC 会话与退出（R03–R05）
r2|r1|
r2|r1|**R03 调度。** 每个 flow 独立异步任务/监督状态；一次迭代结束后再等待 interval，同 flow 最大在途迭代为 1，无历史 tick 队列和追赶补跑。HTTP 等待、timer 和业务判断都在 PLC 请求之外，不占 PLC 的队列位置/执行锁。某 flow 的 HTTP 超时、输入拒绝或 recoverable 错误不停止独立 flow；全局状态/审计不可写则暂停所有新副作用，读流/健康可以继续。
r2|r1|
r2|r1|**R04 PLC owner。** 每个配置 PLC 在进程内只有一个持久 client 和一条专用 owner 线程；同步 driver 必须在线程内创建、持有、调用和断开，不直接跑在 Tokio/asyncio 调度线程，也不用每次 to_thread/spawn_blocking 创建短 client。所有读写经同一 FIFO 有界队列串行执行，最多 1 个 driver call 在途；每请求有 request_id、flow_id、目标、operation、deadline、独立结果通道。调用方只获得自己的结果，取消/过期请求不能复用返回值。最多每 flow 一个待完成 PLC 请求，不建无界 side queue。
r2|r1|
r2|r1|owner 状态为 `disconnected -> connecting -> ready -> recovering`，终止为 `stopping/stopped`。依赖 PLC 的操作先等待同一 owner ready；等待有限，超时返回 unavailable，本轮不下发，不单独发起连接。正常无故障运行只协商一个 S7 session，不逐 tick 重连。连接/读 IO 出错由该 owner 统一断开及退避：一个周期最多 5 次 connect，总尝试间隔为 250/500/1000/2000 ms；5 次都失败后 cooldown 10000 ms 再开新周期，backoff/cooldown 可取消。ready 后成功 IO 才清连续失败计数。不能每个 flow 各开 retry/reconnect 回路，不能在重连中重放 write。
r2|r1|
r2|r1|同步 adapter 必须把 connect/send/receive 与接收重试限制落实到底层 socket/native 参数；首轮有效 connect 上限 3000 ms、单次 driver IO 上限 5000 ms，允许调度误差 500 ms，不能仅 timeout 异步 waiter 后留下无限 driver 调用。实现无法满足即 blocker/QA 不通过，不临时放宽。写调用一旦可能开始，所有不确定错误按第 8 节处理。
r2|r1|
r2|r1|多个 flow 读同一点各发独立协议采样，各有采样/完成身份；不自动成为同一快照，不合并请求、批采集、缓存或订阅。连接复用仅进程内；IO 串行化不提供 command 去重、业务互斥或跨进程 fencing。测试中 Rust/Python writer 依次运行；真正现场同资源/业务效果的单一 writer、停旧再交接和跨主机排他另 gate，不因另一个进程失联自动接管。
r2|r1|
r2|r1|**R05 退出。** SIGINT/SIGTERM 先线性化停止新请求/新副作用；owner 在开始 driver call 前复核 stop、取消、deadline 与 dispatch permit，已排队但尚未开始的请求必须取消，停止后不得下发。已开始 IO 有限等待真实完成，按结果/unknown 持久化；关闭 HTTP/SQLite/日志，断开 client，实际 await/join 自有任务/工作线程后才能记录 `resources_released`/`shutdown_complete`。不能用 abort、取消 waiter、native stop 返回或等待标志代替 join。默认 15000 ms 到时仍未释放，报告 `shutdown_incomplete` 与非零结果，绝不能伪称释放；强杀只属失败场景清理。运行成功停止 exit 0，配置/状态错误 exit 2，运行或不完整退出 exit 1；unknown/持久化故障反映为非健康且不得以正常成功摘要遮蔽。
r2|r1|
r2|r1|## 7. demo01 输入与 INT 合同（R06–R07）
r2|r1|
r2|r1|**R06 synthetic GET。** 每轮至多一次 GET，复用 HTTP client/pool；不重定向、不用环境代理、不自动应用层重试，不执行 POST。只有 HTTP 200、JSON content type、UTF-8、体积 <=4096 bytes、完整严格 schema 的响应才进入业务规则。错误码、坏 schema、缺失、stale、idle 和正常命令分别有稳定结果 key；不得用默认值、上轮值或缓存值触发写入。
r2|r1|
r2|r1|响应是两个 typed 变体，字段名称/含义仅属本地 fixture，不能说第三方/Backend 已实现：
r2|r1|
r2|r1|```json
r2|r1|{"schema_version":1,"source_id":"demo01-feed","ready":false,"command_id":null,"value":null,"issued_at_ms":null,"expires_at_ms":null}
r2|r1|{"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":"cmd-001","value":42,"issued_at_ms":1792531200000,"expires_at_ms":1792531230000}
r2|r1|```
r2|r1|
r2|r1|时间仅为形状示例，fixture 每个新 ID 用当前 UTC 生成，重复 ID 的字段保持不变。`ready` 必须真 bool；ready=true 时 ID 非空且符合上述 ID 规则，value 必须为 JSON 整数，Python bool/浮点/字符串均拒绝；source_id 必须等于 flow 配置，unknown 字段拒绝。
r2|r1|
r2|r1|`issued_at_ms/expires_at_ms` 为来源 UTC Unix 毫秒整数，是源命令发行/失效时间，不能拿接收时刻代替。命令需满足 `0 < expires-issued <= 60000 ms`、issued 不晚于本机 UTC+1000 ms、未到 expires、且源年龄 <= input_max_age_ms（默认10000，上限60000）。接收时校验一次，真正 driver call 前再次校验；ready/queue等待不能延长原有效期。接收时把剩余有效期绑定到 monotonic deadline，之后同时检查 UTC 与 monotonic，重启仍沿原来源时间；时钟跳变超过1000 ms 时暂停新写并暴露 clock_invalid，不能靠倒拨时钟让旧命令复活。synthetic 来源与运行时使用同机时钟；真实来源时间可信度、同步/签名/TTL/撤销合同另 gate。
r2|r1|
r2|r1|身份是稳定 `(source_id, command_id)`，不含 run_id、重试号或模式。首次合法 ready 命令把 flow_id、目标资源、值、来源时间/有效期、schema版本固定成规范 typed 摘要及 SHA256。相同 ID 同摘要复用原状态；相同 ID 不同值、时效、flow/目标或其他语义字段是 `identity_conflict`，保留原意图，不覆盖/不再次下发，并暂停该写 flow。刷新同 ID 时间不能当新命令；idle 不创建执行命令。
r2|r1|
r2|r1|**R07 INT。** 首轮能力仅标准 DB 绝对地址的有符号 16-bit INT 读写，范围 -32768..32767，严格两个字节、大端二进制补码；-1=FFFF、0=0000、42=002A、上下界须有证据。DB号1..65535、声明的db_size_bytes为2..65536、byte_offset0..65534，须满足offset+2<=db_size_bytes，并在fixture注册的实际块内检查完整范围；配置声明不证明真实PLC块大小。不隐式截断或扩大为整块写。读回带sample/request身份、质量和时间，不把旧值作为好值。BOOL/位写、DINT/REAL、I/Q/M、CPU操作、下载和PLC安全设置均后续另立范围。
r2|r1|
r2|r1|## 8. 本地 SQLite 意图、状态与恢复（R08–R10）
r2|r1|
r2|r1|### R08 最小 schema 与事务
r2|r1|
r2|r1|以下是将来由独立 `state init --synthetic` 创建的 schema 合同，不是本轮可执行 DDL。每版各有自己的 SQLite 文件；单进程独占自身 state-dir 文件锁，第二写进程失败；不共享可写库，不复制现有业务库。字段使用稳定英文 key；schema_version=1。
r2|r1|
r2|r1|| 表 | 最小字段/约束 |
r2|r1|| --- | --- |
r2|r1|| `store_meta` | 单行，schema_version、implementation=`rust|python`、mode=`dry_run|execute`、instance_id、store_uuid、created_at。模式/实现不匹配拒绝使用。 |
r2|r1|| `commands` | PK `(source_id,command_id)`；flow_id、target_key、config_identity_hash、payload_hash、value_i16（CHECK范围）、issued_at_ms、expires_at_ms、state、dispatch_count（0或1）、run_id、request_id（可空）、last_error_key（可空）、ack_kind（可空）、created_at、updated_at；身份和意图字段插入后不可变。 |
r2|r1|| `command_events` | 单调主键 seq；命令复合FK、run_id/request_id、from_state/to_state、reason_key、必要的脱敏摘要与 created_at；只追加、不覆盖。 |
r2|r1|
r2|r1|`target_key`只表示规范化物理写资源：literal IPv4 endpoint/port、rack/slot、DB、offset、INT长度，不含flow_id、source_id、plc_id别名、run_id或配置文件名。flow_id单独记录命令归属，config_identity_hash另行固定该归属、source绑定和影响命令含义的配置。启动恢复及每次接纳/派发新命令时，必须查原库所有unknown（包括刚由in_flight恢复者）的物理endpoint/DB/字节区间；与目标重叠就阻止写，不能靠换flow_id、source_id、plc_id、配置别名或command_id绕过。原库与原身份必须保留；换库/删库不属于恢复办法。本合同只覆盖本进程及其原私有库，不宣称跨库/跨主机fencing。时间约定：来源字段明确保存外部UTC Unix ms；created_at/updated_at为SQLite UTC数据库时间表达式，操作超时用monotonic，不写入宿主本地时区。原始body、token、URL query不进库/日志。
r2|r1|
r2|r1|SQLite 单 owner/串行状态 executor，不能堵事件循环；busy_timeout 500 ms，事务 deadline 1000 ms，短事务内无外部 IO。首轮 `journal_mode=DELETE`、`synchronous=FULL`、foreign_keys=ON；固定page_size4096、主文件max_page_count16384（64MiB），不使用共享 WAL、网络文件系统或任意自动 schema migration。
r2|r1|
r2|r1|T1：同一事务查身份/冲突，插入 pending 意图与对应 command_event，commit成功后才可准备外部动作。T2：确认mode/TTL/ready/容量/stop/必要审计健康并取得有界队列位置后，以CAS将 pending->in_flight、dispatch_count0->1并追加event，commit后才能把唯一 dispatch permit交给owner调用一次写入；提交失败不下发。队列交接不得在事务失败后遗留可执行请求。T3：仅在匹配请求的正 S7 write ack 后，同事务 in_flight->confirmed、ack_kind=`s7_protocol`并追加event。确认持久化失败时保留in_flight/unknown事实、暂停新副作用，不回到pending重发。
r2|r1|
r2|r1|### R09 状态含义与转换
r2|r1|
r2|r1|| 状态 | 精确定义与恢复 |
r2|r1|| --- | --- |
r2|r1|| `pending` | 意图已持久，但没有发出过 dispatch permit，dispatch_count=0。重复请求不建新身份；重启后只有当前 GET 再次给出同摘要且原有效期仍有效、配置/目标一致才可继续；不能仅凭库存意图离线重放。 |
r2|r1|| `in_flight` | dispatch_count=1、下发许可已持久，外部调用可能未开始/进行中/已生效；不是成功。重启在任何连接/新下发前统一转 unknown并追加恢复event，即使可能是发送前崩溃也保守处理。 |
r2|r1|| `confirmed` | 收到该请求的正S7协议ack且本地确认事务已commit。重复/重启永不再次写同身份；不代表PLC逻辑接受、工艺完成或物理exactly-once。 |
r2|r1|| `unknown` | 进入driver调用后发生超时/断连/响应丢失/崩溃，或ack/确认持久化无法完整证明。保留原身份/意图/证据，阻止此flow/目标后续写（包括新ID）；重连/下一tick/重启不能自动重发或转confirmed。 |
r2|r1|| `expired` / `canceled` | 可证明未开始driver写：pending过期或停机前取消，或permit交接被owner明确拒绝且未执行。保留记录，不自动重建身份重发。不能证明未发送则unknown。 |
r2|r1|| `simulated` | 仅dry_run库中的would_write观察，dispatch_count=0、ack_kind为空，不入真实执行confirmed；绝不能导入execute库。 |
r2|r1|
r2|r1|合法路径是 pending->in_flight->confirmed/unknown，pending->expired/canceled，以及明确未执行的 in_flight->expired/canceled；后者不得重置dispatch_count再重试。dry_run只记录simulated。坏schema/stale在接纳意图前拒绝；进入pending后的到期沿上述路径留痕。首轮不提供unknown的自动查询/人工改状态CLI；需要核对的工作保持阻塞，另批目标方握手/人工处置方案。
r2|r1|
r2|r1|writer/owner/库恢复和flow健康相互区分：某目标unknown不应停止不相关读流；相同写目标新命令不得绕过。已confirmed之后的日志/后续故障不得把它降回可下发；本轮无结果POST/补投步骤。未来若加回报，只能补报原身份，不能倒退到PLC写。
r2|r1|
r2|r1|### R10 dry-run、失败与能力限度
r2|r1|
r2|r1|dry-run可对获批loopback做GET和S7 read，但PLC写计数必须为0；默认只记录would_write/simulated。初始化时mode固定，dry_run/execute使用两个独立state-dir，交叉打开非零失败。两模式使用同一来源身份语义；dry-run不能占用、确认、复制或重置execute进度，也不能靠切模式消除unknown。
r2|r1|
r2|r1|必须覆盖：T1前失败、T1后发送前重启、T2后调用前崩溃的保守unknown、server已应用但ack丢失、server已应用且进程崩溃、收到ack但T3失败、confirmed重启不重发。所有可能已发送错误保守unknown；库/日志持久化不能与PLC原子提交，S7 ack、SQLite事务或回读同值均不能核实原命令工艺完成或升级unknown为confirmed。回读只作协议数据正确性证据。
r2|r1|
r2|r1|## 9. 日志、健康与容量（R11–R12）
r2|r1|
r2|r1|**R11 可观测性。** stdout与自身state-dir下持久文件均为JSON Lines；最低字段：UTC timestamp、event、implementation、run_id、instance_id、flow_id/target_id、command_id/request_id（适用时）、state/old/new、result、duration_ms/error_key。最低事件包括process/config/state init、owner连接/退避/恢复、flow健康变化、intent/dispatch/ack/unknown/冲突、容量暂停、stop/join/资源释放。普通读不逐tick刷日志，用每5秒progress/health聚合计数；测试专用协议采样trace单独有界保存。
r2|r1|
r2|r1|日志按大小轮转：写入完整JSON行前按大小检查，单文件不超过5MiB、最多4个backup；单行<=4KiB，总文件上限25MiB，既有日志不因启动截断。Rust tracing持久sink必须有实际失败回传；不能用默认忽略IO错误/有损异步队列冒充必要审计。副作用前的意图/dispatch审计须在SQLite事务和持久日志均成功落盘（flush/sync有回执），否则阻止下发；stdout/持久sink故障均停止新副作用并报告health。副作用后审计失败不能抹除或重放已确认动作；保持最后持久in_flight/confirmed并可见报告。审计不依赖可轮转普通日志唯一保存，command_events保留必要状态链。
r2|r1|
r2|r1|健康快照由监督器拥有，至少含每flow的starting/running/recovering/blocked/stopping/stopped、最近迭代/成功、连续错误、owner状态/队列深度/在途数、pending/unknown计数、容量和日志可写性；通过每5秒JSONL及正常退出摘要观察，不新增health HTTP监听器或GUI。idle/无新命令不算失败，进程仍在运行不能冒充flow健康。
r2|r1|
r2|r1|**R12 容量。** 默认command上限10000条、command_events100000条；接纳新身份前若event>=90000、库主文件>=48MiB、可用磁盘<256MiB或command达上限，则暂停新副作用，保留恢复写余量。主库硬上限64MiB，含rollback journal的state占用上限128MiB；到硬边界失败即阻止新副作用，不能删除pending/unknown/confirmed身份腾空间。读恢复/健康仍有界；不建自动清理、淘汰去重ID或无限离线命令队列。测试可把计数上限降低为10/100或模拟IO错误验证，不需要真实写满磁盘。日志轮转删除旧普通日志前，必要审计已留在command_events；本轮不提供生产归档/保留年限承诺。
r2|r1|
r2|r1|## 10. 本地协议夹具与批准后的拟执行命令（R13）
r2|r1|
r2|r1|以下全部是未来命令合同，当前均 `not_run`。批准精确r1才允许Development创建工程、解析其锁、构建/启动和执行这些合成验证；批准仅覆盖本任务新建私有状态库与loopback，不泛化成真实DB/设备权限。
r2|r1|
r2|r1|| 实现 | 固定端口 |
r2|r1|| --- | --- |
r2|r1|| Rust | S7 client入口/proxy `127.0.0.1:31102`；native S7 server `127.0.0.1:31103`；synthetic HTTP `127.0.0.1:31880` |
r2|r1|| Python | S7 client入口/proxy `127.0.0.1:32102`；自身S7 server `127.0.0.1:32103`；synthetic HTTP `127.0.0.1:32880` |
r2|r1|
r2|r1|每套fixture独立启停，不能绑定wildcard/102、杀占用者或自动换端口；冲突报告并停止该验证。TCP proxy只转发有界TPKT并识别读/写及匹配响应做计数/故障注入，不重写通用S7栈。普通运行一个runtime到该PLC的会话，proxy前后两段TCP属于同一透传S7会话，证据应分别标记，不能把它记为两个独立客户端。server注册内存必须活到fixture真正退出；停止不能提前释放native仍可能使用的buffer。上游native stop返回不是线程join证明，fixture宜进程隔离；父harness等待子进程正常退出并确认端口释放后才算结束，强杀另记失败清理。
r2|r1|
r2|r1|fixture必须能固定同ID响应、发新ID/坏schema/stale/冲突、延迟指定GET、断开/恢复S7、在server已应用写并产生匹配ack后丢弃/扣留该ack、确认实际写计数/字节、在此屏障时终止测试runtime再重启原库。丢包只发生在TCP传输层，不能用mock函数返回unknown替代。正常路径也要真实GET、S7协商、WriteVar和独立协议读回；独立读回安排在runtime停止后，避免污染“正常运行只有一个会话”计数。轻量单元测试补边界，不承担全部协议证据。
r2|r1|
r2|r1|从Rust工程目录，拟提供：
r2|r1|
r2|r1|```bash
r2|r1|cargo fmt --check
r2|r1|cargo check --locked --all-targets --features test-fixture
r2|r1|cargo build --locked --bins --features test-fixture
r2|r1|cargo test --locked --lib
r2|r1|cargo test --locked --features test-fixture --test local_protocol -- --test-threads=1
r2|r1|cargo run --locked --bin field-flow --
r2|r1|cargo run --locked --bin field-flow -- state init --synthetic --mode dry_run --state-dir /private/tmp/ff-001-r1-<run-id>/rust/dry --instance-id ff-rust-demo01
r2|r1|cargo run --locked --bin field-flow -- state init --synthetic --mode execute --state-dir /private/tmp/ff-001-r1-<run-id>/rust/execute --instance-id ff-rust-demo01
r2|r1|cargo run --locked --features test-fixture --bin ff-fixture -- --config config/loopback.yaml --evidence-dir /private/tmp/ff-001-r1-<run-id>/rust/fixture
r2|r1|cargo run --locked --bin field-flow -- run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-<run-id>/rust/dry
r2|r1|cargo run --locked --bin field-flow -- run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-<run-id>/rust/execute --execute
r2|r1|```
r2|r1|
r2|r1|从Python工程目录，拟提供：
r2|r1|
r2|r1|```bash
r2|r1|uv lock --check --python 3.11 --no-python-downloads
r2|r1|uv sync --locked --python 3.11 --no-python-downloads
r2|r1|uv build --python 3.11 --no-python-downloads
r2|r1|uv run --locked --python 3.11 --no-python-downloads python -m compileall -q src tests
r2|r1|uv run --locked --python 3.11 --no-python-downloads pytest -q tests/unit
r2|r1|uv run --locked --python 3.11 --no-python-downloads pytest -q tests/test_local_protocol.py
r2|r1|uv run --locked --python 3.11 --no-python-downloads field-flow
r2|r1|uv run --locked --python 3.11 --no-python-downloads field-flow state init --synthetic --mode dry_run --state-dir /private/tmp/ff-001-r1-<run-id>/python/dry --instance-id ff-python-demo01
r2|r1|uv run --locked --python 3.11 --no-python-downloads field-flow state init --synthetic --mode execute --state-dir /private/tmp/ff-001-r1-<run-id>/python/execute --instance-id ff-python-demo01
r2|r1|uv run --locked --python 3.11 --no-python-downloads python -m tests.fixtures --config config/loopback.yaml --evidence-dir /private/tmp/ff-001-r1-<run-id>/python/fixture
r2|r1|uv run --locked --python 3.11 --no-python-downloads field-flow run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-<run-id>/python/dry
r2|r1|uv run --locked --python 3.11 --no-python-downloads field-flow run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-<run-id>/python/execute --execute
r2|r1|```
r2|r1|
r2|r1|`<run-id>`是待执行者生成的唯一目录名，不可照抄尖括号到shell；上述是分终端/由harness顺序运行的命令，fixture需先就绪。首个锁生成在获批Development时显式执行`cargo generate-lockfile`/`uv lock --python 3.11 --no-python-downloads`，之后使用locked命令；本轮不运行。Python自身`.python-version`也为3.11，不能让uv静默选择3.12/3.13或自动下载解释器冒充本平台首轮证据。Development需把最终可复制命令、fixture退出方式、实际命令/退出码/解释器patch/版本/路径和AC证据写入tasks，不能把本节future命令当执行记录。
r2|r1|
r2|r1|还须分别把单个工程复制到本任务新建私有目录，排除target/.venv/dist/状态/日志，隐藏或缺少父/兄弟工程仍按自身README锁定依赖、build/start/test；可以使用正常公共package缓存，不能借另一个工程的源码/可写库/运行fixture。所有有效源码最终在约定交付工作树，复制品的结果不能替代交付树一致性核对。
r2|r1|
r2|r1|## 11. 验收标准
r2|r1|
r2|r1|以下AC每版分别给结果；Rust先完成AC01–AC14的DEV证据，Python再按同一业务矩阵跟进，最终统一fresh-context Verification。技术风险/依赖blocker不能用一版通过替另一版通过，也不能把not_run改为deferred complete。
r2|r1|
r2|r1|| AC | 可观察验收 / 对应需求 |
r2|r1|| --- | --- |
r2|r1|| AC01 | 两版各自独立复制、锁解析、构建、无参/help、显式初始化、启动和测试成功，记录当前平台/工具/锁；无父清单/兄弟源码或fixture/环境/可写SQLite依赖；正式交付树与候选一致。（R01/R02/R13） |
r2|r1|| AC02 | 入口分层、typed配置和中英CLI成立；无参无IO；未知/缺失字段、重复ID/endpoint、写范围冲突、非法预算/状态版本/模式拒绝；init不覆盖既有目录，普通run不建schema。（R01/R02/R08/R10） |
r2|r1|| AC03 | 两版demo01有真实GET->S7 INT写->停止后独立S7读回的完整协议证据；INT -32768/-1/0/42/32767正确，越界/float/bool/string及块越界拒绝，邻接字节保持。（R06/R07/R13） |
r2|r1|| AC04 | idle、非200、超体积、坏JSON/schema/source、过期/未来时间/过长TTL均零新写；入队后过期与时钟倒拨不放行，重复ID不刷新时效。输入拒绝与通信故障可区分。（R02/R06） |
r2|r1|| AC05 | 相同命令连续至少10轮及重启原execute库只产生1次实际写；同ID不同payload/time/target触发冲突且原记录不变；新合法ID才可能产生新写。（R06/R08/R09） |
r2|r1|| AC06 | 同一PLC下至少3个独立测试读流读同一INT，每流至少20个独立sample/request；正常阶段S7协商session总数1、driver最大在途1、协议请求串行、每结果归回正确flow。读值不同时间可不同，不伪称共享快照。（R03/R04） |
r2|r1|| AC07 | 一个测试流GET延迟1200ms，另一个读流按100ms间隔在8秒窗口完成至少20轮、最大相邻成功间隔<=500ms；慢流最大在途迭代1，HTTP等待不占PLC执行位置，无补跑tick。（R03/R04） |
r2|r1|| AC08 | server未启动/主动断连时仅owner按有界策略重连；ready前无IO，恢复后读流继续，坏配置不触发无限重连，独立无关flow继续；实际connect/IO等待和错误处理符合预算。（R03/R04） |
r2|r1|| AC09 | T1后发送前重启沿原身份/原TTL处理；T2后不明发送点恢复unknown；真实server已写但ack被丢弃得到unknown，至少再GET10轮和重启后实际写计数仍1。改变flow/source/plc别名、新ID或重叠目标范围都不能绕过原库unknown，读流仍能推进。（R08–R10/R13） |
r2|r1|| AC10 | 在server写已生效、ack被扣留屏障杀掉测试runtime，原库重启变unknown且不再次下发；ack后确认持久化失败也不重发；confirmed不因重启/日志故障倒退。回读值相同不能将unknown升级confirmed。（R08–R10/R13） |
r2|r1|| AC11 | dry-run实际GET/read可见、真实write计数0，持久状态仅simulated，confirmed数0；dry_run/execute库交叉打开失败，dry观察不影响execute身份/进度。（R02/R10） |
r2|r1|| AC12 | stdout/持久文件逐行JSON可解析且脱敏，真实轮转边界成立；通过降低计数阈值/注入磁盘/审计失败证明暂停新副作用、保留pending/unknown/confirmed，不需真实填满磁盘；健康能区分recovering/blocked/仍运行。（R11/R12） |
r2|r1|| AC13 | 有在途及排队请求时触发正常停止，排队未执行请求零下发；15秒默认预算内真实join任务/owner线程、关闭客户端和库/日志、fixture自然退出，独立观测socket/端口/自有进程释放；超时/强杀如实失败，端口冲突不杀占用者/换端口。（R04/R05/R13） |
r2|r1|| AC14 | 两版README/PLAN/catalog/locale/索引与实际相符，tasks记录逐AC命令、退出码、实际资源和未验gate；fresh-context命名Verification独立出checklist verdict；Human Owner最终验收仍单独待决定。（R01–R13） |
r2|r1|
r2|r1|“测试流”只为验证同点独立采样与调度，可在tests内实现，不能冒充demo02用户流或引入长期共享采集服务。协议测试依赖真实loopback请求/服务端计数，单元mock不能替代AC03/06–10/13。窗口是有界开发故障验证，长期浸泡/容量/现场运行资格均未覆盖。
r2|r1|
r2|r1|## 12. 排除项、风险、回退与外部 gate
r2|r1|
r2|r1|排除demo02“PLC上升沿->POST”、通用流程平台/GUI/CA/AI、共享快照/缓存/订阅、第三方API/Backend接入、跨语言状态互换、自动unknown核实/重发、双活热备、服务安装/托管/开机自启、离线安装包/签名/三平台打包、长期浸泡/压力/全型号/真实现场验证；不能因创建runtime就扩大这些范围。
r2|r1|
r2|r1|| 风险/未决 | 当前处理与后续 gate |
r2|r1|| --- | --- |
r2|r1|| native/Python协议库的实际timeout、线程终止与版本兼容未实测 | 作为本地Development必要实证；不能做到时阻塞相应AC并回PM决定，不能降低标准或引入兄弟桥接。官方源码/API研究不能写成构建成功。 |
r2|r1|| 本地SQLite与外部写无法原子提交，unknown会保守阻塞 | 保留意图/身份/审计且不重发；r1不提供绕过。真正接收方的幂等、命令寄存器/序号、确认/工艺握手和人工处置另批。 |
r2|r1|| 来源命令时间与真实接口未定 | synthetic同机UTC/TTL完成本地任务即可；真实API路径/鉴权/schema/时钟/命令身份/撤销另gate，不阻塞当前合成任务。 |
r2|r1|| 现场OS/CPU/固件/通信权限/DB优化/工艺互锁未定 | 本轮只验证macOS arm64 loopback；现场PLC型号、PUT/GET/非优化DB条件、点位写归属与目标动作授权另gate，不修改PLC项目或安全设置。 |
r2|r1|| 本机库锁/会话复用不提供跨实例writer排他 | 夹具逐版串行，配置拒绝进程内冲突；实地切换须停止旧writer、核对pending/in_flight/unknown及已确认进度，明确唯一有效写归属后再启新端，不共享库。 |
r2|r1|| 日志/状态容量有限，运行长时后可能停止新写 | 首轮明示上限、背压和保留策略；不靠清库继续，生产归档/保留/备份、资源趋势及托管长稳另gate。 |
r2|r1|
r2|r1|回退限本任务源码/diff，不能覆盖其他dirty。已经confirmed或unknown的外部写没有自动反向写回；先停新下发、保留原库/日志/身份再核对。r1不升级既有schema；以后新schema/二进制回退必须先核对兼容，不能删除状态库重新跑。自有临时资源在交接列明，QA仍需的保留；最终验收后由协调器核对归属/占用/证据归档再安全清理，不清理其他任务资源，关键结论不能只存在/tmp。
r2|r1|
r2|r1|## 13. 批准与交接
r2|r1|
r2|r1|Human Owner于2026-10-21明确回复“批准 ff001 r1”，本次精确批准的是 **FF-001 r1** 的两版独立实现、先Rust后Python、仅demo01/INT、本地synthetic状态schema显式初始化、列明loopback端口/协议故障注入、依赖和allowlist、AC01–AC14及unknown保守阻塞/容量限制。批准对象为上述SHA256对应的待批准稿；本次记录不修改已批准范围或Revision。Development现在可在主协调器实际调用后创建tasks并按此范围实施。
r2|r1|
r2|r1|PM -> Development：精确FF-001 r1已获Human Owner范围批准，下一阶段为Development计划/实施与自检；本次PM未创建tasks或执行实现。原起草/自检记录保留为历史，不据此推断DEV/QA结果。Development -> Verification：精确r1、交付工作树/diff/锁、修改文件、逐AC自检命令/退出码、失败与限制、临时资源；Verification使用`agent_type="verification", fork_turns="none"`读取完整bundle/实现/证据独立验证，不继承DEV推理、不修实现。`qa_passed`只进入Human Owner最终验收，不授权现场/发布/部署/推送。
r2|r1|
r2|r1|主协调器负责角色调用、串行handoff和机械导航，不代写三角色事实；profile为contract_only，不宣称平台ACL、强制路由或团队已激活。任何范围、allowlist、验收、风险或模式实质变化，停止该未授权部分，回PM新Revision并重新批准。
r2|r1|
r2|r1|| 日期 | Revision | 范围/批准事实 |
r2|r1|| --- | --- | --- |
r2|r1|| 2026-10-21 | r1 | PM按用户要求建立首轮独立实施draft；精确Human Owner范围批准pending。关联r2及历史不变；DEV/QA/最终验收未开始。 |
r2|r1|| 2026-10-21 | r1 | Human Owner明确回复“批准 ff001 r1”，精确批准待审FF-001 r1（交付SHA256见第1节）；Status改为owner_approved，PM交接Development。仅增加批准事实，原范围、需求、AC、依赖/参数/allowlist/风险/排除项不变；尚无DEV完成、QA或最终验收。 |
r2|r1|
r2|r1|PM文档自检（2026-10-21）：个人辅助Python只读断言exit0，检查唯一元数据/独立身份、AC01–AC14、3个本地链接、fence/空白、原r2全文件SHA256不变，以及源码目录/tasks/checklist尚不存在；`rg`核对FF-001仅本spec一份，exit0。`git diff --no-index --check /dev/null <本spec>` exit1且零诊断，为未跟踪新文件存在差异，不宣称全仓治理通过。只读`sw_vers`/`uname -m`/工具`--version`及uv的`lock/sync/build/run --help`核对首轮平台和未来Python选择参数，未执行lock/sync/build/run。这不是独立Verification。
r2|r1|
r2|r1|协调器文档检查（2026-10-21，PM按主协调器实际回报转录）：8份FF Markdown及根新增FF-001入口共42个本地链接/锚点解析通过；3对FF双语导航结构一致；唯一FF-001/r1/draft元数据与AC01–AC14完整，FF仅新增本spec，无source/tasks/checklist。10份导航对写入前快照仅FF-001行变化；9份保护文件hash均未变，包括原r2完整文件、根AGENTS/README双语/CODE_INDEX/ROADMAP双语及AW-006/AW-007。`git diff --check -- field-flow README.md README.zh-CN.md PLAN.md PLAN.zh-CN.md plans/README.md plans/README.zh-CN.md CODE_INDEX.md` exit0。实际`bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch field-flow` exit1，会前后318行诊断完全相同，FF诊断0、新增0；只证明未新增既有诊断，不能标为全仓治理通过。以上是PM/协调器文档自检，未构成独立QA或任何实施验收；暂存检查文件由协调器在必要结论持久化后核对回收。
r2|r1|
r2|r1|本轮所有安装、构建、程序/项目测试、schema、fixture、监听器和真实外部动作均`not_run`，没有创建临时源码副本、状态库或服务；本记录不是Development自检、独立QA或最终验收。
r2|````
r2|<!-- END FF001 R1 ORIGINAL BYTES -->
`````
<!-- END FF001 R2 ORIGINAL BYTES -->
