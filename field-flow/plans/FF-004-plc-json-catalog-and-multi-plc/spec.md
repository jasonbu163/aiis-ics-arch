Task ID: FF-004
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Development; Human Owner explicitly approved FF-004 r2 A on 2026-11-04 (Asia/Shanghai); fresh-context Verification follows actual developer_handoff; Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: 每PLC独立JSON合同、Rust首切片的S7 int16目录加载与多PLC点位调用、Modbus结构校验及DS导出边界
Owner: Field Flow
Acceptance Chain Reference: FF-004 r2 exact A scope approval -> Development -> fresh-context QA / Verification -> Human Owner final acceptance
Related Task: FF-001 r4; FF-002 r1; FF-003 r1; FF-005 r1 A; ARCH-TOOL-001 r2; device-simulator::DS-002 r1

# FF-004：每PLC一个JSON与多PLC调用 r2

## 1. 当前授权、Revision差异与批准面

### 最新有效决定：FF-004 r2 A范围批准

2026-11-04（Asia/Shanghai），Human Owner明确原话：“批准 FF-004 r2 A，按方案开始开发，完成后按 STD 进入独立 QA。”本PM据此登记`Status: owner_approved`，交接`PM -> Development`；批准对象为已交付草案SHA256=`52760234a3349eed38dcbe0877ff5ba25ce95e1be93ed1cd93e36c8713870452`的精确**FF-004 r2 A**。Revision保持r2，本文A范围、§3有限allowlist、R01–R10、AC01–AC14、风险与排除项全部不变，§16完整r1继续原字节保留。

当前gate已由等待范围批准进入Development：主协调实际调用Development，Development才创建本bundle的tasks.md并实施A；真实`developer_handoff`后，另启`verification`、`fork_turns="none"`的fresh-context独立QA，再交Human Owner最终验收。本次仅登记明确范围批准和PM交接，不表示Development已执行、QA通过或Owner最终验收；B/C及原排除项继续独立gate。

下文P0“当前只修订本spec”“r2 draft”“未批准”“当前不启动Development/QA”等草案语句及§15原批准点均保留其批准前历史时点；当前状态与后续gate以本最新明确决定为准，不能用旧语句撤销本次A批准，也不能据此扩大原合同。

2026-11-03（Asia/Shanghai），Human Owner要求：“可以，就按一台PLC一个JSON的方案，先把S7/Modbus配置格式、多PLC调用方式和DS导出关系整理进FF的实施spec，按STD先走PM，暂不改代码。”原r1为draft，完整42739字节、SHA256=`e33aae41d18ba7faad19cb1ed563a19375996bc0f5d23ee7c646d62b2f7b0dc4`，可从[§16封存](#r1-original)无损还原，未曾取得精确实施批准。

2026-11-04，FF-005 r1 A已由Owner最终验收；主协调提出优先继续FF-004的Rust/S7切片后，Owner回复“好的”。该上下文支持继续本任务PM复核，**不是FF-004 r1或r2实施批准**。当前只修订本spec；同一[FF PLAN](../../PLAN.md)和[任务目录](../README.md)仍指向此唯一bundle，无Parent Task ID，不继承相关任务的批准、QA、终验或外部动作权限。

本次实质调整allowlist、兼容与可观察验收，故形成**r2 draft**，不沿用r1承载新合同；不是单因新会话机械升版。

| r2相对r1的最小变化 | 原因与效力 |
| --- | --- |
| v1保留三个正式kind；v2仅demo01/read_points | FF-005已交付basic02/basic03；本A不迁移它们，不增加第四个正式教学case。 |
| 补`src/bin/ff-fixture.rs`、小型`src/runtime/catalog.rs`及新测试helper；收回domain/demo01和旧测试写面 | 真实fixture入口固定旧参数，必须明确接新模式；版本装配不能逼迫改旧摘要或重写既有owner。 |
| `config/README.*`改为增补现有文档；增补父对照手册两件必要兼容说明 | 这些文件现已存在，旧三案例、教程锚点和能力声明需要被明确保护或按事实最小更新。 |
| catalog夹具先idle、观察初值后一次issue；补有界样本观察/结构化资源判定 | 避免读12与写42的竞态、原10秒input age失效及紧凑JSON漏检；不放宽TTL/timeout。 |
| 逐场景冻结已confirmed/unknown兼容和正常/故障关闭 | 状态身份与真实退出证据分开；FF-005旧hold_ack限制保留，不把它写成已修。 |
| 显式列B-off的既有force/失败退出，增加1200ms限内慢connect正常子场景 | 本轮源码发现Driver::spawn连接失败会force；r2对风险/AC的实质修订须由Owner审阅。B-off只验A隔离、B未发读写零下发、实际有界回收，不能提供正常关闭/零forced证据。 |

| 层次 | 本r2定义的交付与效力 |
| --- | --- |
| P0：当前 | PM只写本spec，主协调在真实handoff后机械同步§3八导航；无tasks/checklist、源码、配置、schema或项目运行。 |
| A：精确r2批准后 | 仅现有Rust：严格单PLC JSON、主YAML v2、稳定只读点句柄、S7标准DB int16、公开read_points、demo01点引用、v1三kind与旧状态身份兼容、自有有限夹具/测试/双语说明。Modbus仅结构校验，run整体拒绝。无新依赖、driver或状态schema变更。 |
| B：独立协议gate | Modbus TCP client/owner、wire codec/事务/迟到隔离、真实读写及共享网关策略；另行精确批准，本A不实施。 |
| C：独立owner/gate | Python加载、FF-003后C#加载、DS导出及根contracts公开schema，各有后续精确批准；FF可先手写JSON，不等待DS UI。 |

Human Owner若明确批准“FF-004 r2 A”，批准对象为本文A的需求、§3文件边界、有界合成验证及AC01–AC14；A内普通接线/类名不另设批准。实质改变范围、allowlist、AC或风险仍回PM。当前不启动Development/QA，不提前创建角色证据。

## 2. 本轮只读核查与现状

已按序读取根AGENTS/README/PLAN双语、[canonical workflow](../../../.codex/workflows/development-lifecycle-workflow.md)、[实际pm.toml](../../../.codex/agents/pm.toml)，FF及Rust/Python最近README/PLAN/catalog，完整原FF-004 r1、FF-005当前三文件与其实际app/config/runtime/CLI/fixture/teaching01接线，FF-001/002/003有效事实；另读AW/DS README/PLAN、完整[DS-002 r1](../../../automation-world/device-simulator/plans/DS-002-multi-protocol-simulation-and-device-debugging/spec.md)及DS配置/来源/版本/lifecycle源码。未发现更近AGENTS或重复FF-004 bundle。本目录只有spec；以下是源码/既有记录核对，**全部本轮项目行为验证not_run**。

| 来源 | 当前事实及约束 |
| --- | --- |
| [Rust config](../../field-flow-rust/src/config.rs)、[app](../../field-flow-rust/src/app/mod.rs)、[runtime](../../field-flow-rust/src/runtime.rs)；[Python config](../../field-flow-python/src/field_flow/config.py)/[runtime](../../field-flow-python/src/field_flow/runtime.py) | v1正式接受demo01、plc_guard_get_int、get_value_guard_int，内嵌plcs/物理target；没有JSON目录或Modbus。teaching01只在教程副本接线。已有最多4 PLC/8 flow与物理写冲突校验。 |
| [Rust fixture入口](../../field-flow-rust/src/bin/ff-fixture.rs)/[主体](../../field-flow-rust/src/fixture.rs) | 入口只接受旧`--config/--evidence-dir`，内部native模式固定DB1/31103；旧CLI无fixture_ready，固定cmd-001/42。新catalog模式必须显式接入口，不能靠不改入口绕实现。 |
| [domain](../../field-flow-rust/src/domain.rs)、[Execution](../../field-flow-rust/src/services/execution.rs)、[state](../../field-flow-rust/src/infrastructure/state.rs) | 旧摘要为完整Flow/Target和端点的typed序列化；unknown按原库全部物理Resource重叠阻写；Driver::spawn连接失败沿既有force/故障分类。schema1、不可变trigger和UTC日历producer保留；不需把读流伪造成旧写Flow。 |
| [FF-005 spec](../FF-005-basic-and-advanced-examples/spec.md)/[tasks](../FF-005-basic-and-advanced-examples/tasks.md)/[checklist](../FF-005-basic-and-advanced-examples/checklist.md) | r1 A为owner_accepted，当前checklist SHA256=`f321278afe23fc106ea25101332c5a29a5f893abbfe687b5f6220d6a0428833c`；QA1失败、紧凑JSON漏检及完整hold_ack强收限制保留。FF-001 r4/FF-002 r1仍qa_passed、Owner终验pending；FF-003仍draft，无C#底座。 |
| [DS配置](../../../automation-world/device-simulator/runtime/src/domain/configuration.rs)、[source](../../../automation-world/device-simulator/runtime/src/domain/source.rs)、[queries](../../../automation-world/device-simulator/runtime/src/infrastructure/config_store/queries.rs)、[versions](../../../automation-world/device-simulator/runtime/src/services/versions.rs) | 有S7实例/DB/点UUID、监听参数、长度/byte/bit、绑定树/原来源、不可变revision原payload SHA，以及独立selected/loaded查询。无协议分型、brand/model/firmware字段、Modbus表模型或FF exporter；不能把S7模型/DS-002提案当实现。 |

本轮只读核对锁定rust-snap7=1.142.2的原native `s7_micro_client.cpp/.h`与`s7_isotcp.cpp`：默认calling/local=0x0100、PG type=1、remote/called=0x0100+rack×32+slot，C1为source、C2为destination；仓内driver未覆写。该结论是精确源码推断，不是本轮wire实测；A仍须显式C1/C2断言，产品不依赖本机缓存绝对路径。

本轮重开[Modbus官方V1.1b3](https://www.modbus.org/file/secure/modbusprotocolspecification.pdf)与[官方TCP指南V1.0b](https://www.modbus.org/file/secure/messagingimplementationguide.pdf)核对四表/零基PDU/功能码及MBAP/Unit/连接资料。§6保持r1有限配置选择，不因此承诺Modbus通信或设备兼容。汇川EVO目标仍缺CPU/固件/点表/transport事实，本文只用合成地址。

## 3. 精确文件边界与保护

正式交付树=`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，已有并行dirty全部保留，不reset、覆盖或清理。P0只有PM写本spec；主协调在handoff后仅改原FF-004行/入口的Revision、draft及下一gate，不更改其他任务的历史事实。

| P0责任 | 有限allowlist |
| --- | --- |
| PM | `field-flow/plans/FF-004-plc-json-catalog-and-multi-plc/spec.md`，此目录已存在。 |
| 主协调FF导航 | `field-flow/{README.md,README.zh-CN.md,PLAN.md,PLAN.zh-CN.md,plans/README.md,plans/README.zh-CN.md}`六件。 |
| 主协调跨工程导航 | 根`PLAN.md`、`PLAN.zh-CN.md`两件；根README、根plans catalog及根CODE_INDEX排除。 |

**以下仅在精确r2 A批准后成为实现allowlist。** R=`field-flow/field-flow-rust/`；花括号仅有限枚举，不是递归授权，未实际需要的路径不改。

| A责任 | 精确集合与限制 |
| --- | --- |
| 既有接线 | `R/src/{config.rs,commands.rs,runtime.rs,lib.rs}`、`R/src/services/mod.rs`、`R/src/app/mod.rs`；仅版本入口、句柄装配、read_points注册/监督/有界观测，保留v1三kind派发。 |
| 新小模块 | `R/src/config/{catalog.rs,runtime_v2.rs}`、`R/src/services/devices.rs`、`R/src/app/read_points.rs`、`R/src/runtime/catalog.rs`；DTO/严格校验、规范化、只读服务和新流装配分层，不重构旧owner/driver或建插件平台。 |
| 夹具入口/新模式 | `R/src/bin/ff-fixture.rs`增加精确catalog及其私有native分派；`R/src/fixture.rs`仅增加catalog_demo模块声明/导出，旧Fixture/Behavior/native_server主体原字节保留；新`R/src/fixture/catalog_demo.rs`负责固定两PLC模式、控制、trace及真实关闭。 |
| 新验收代码 | 新`R/tests/{plc_catalog.rs,multi_plc.rs,catalog_compatibility.rs,modbus_catalog.rs}`及`R/tests/catalog_support/mod.rs`；新helper复用可读既有API，不修改任何旧test/support/expected。配置负例在内存或自有tmp生成。 |
| 合成配置 | 新`R/config/catalog-demo.yaml`、`R/config/plcs/{s7-a.json,s7-b.json,modbus-example.json,README.md,README.zh-CN.md}`；既有`R/config/{README.md,README.zh-CN.md}`只增补v2说明，旧三YAML行/身份/命令保持。 |
| 双语说明 | `R/{README.md,README.zh-CN.md,USER_GUIDE.md,USER_GUIDE.zh-CN.md,BUILD.md,BUILD.zh-CN.md,CODE_INDEX.md}`；父`field-flow/{USER_GUIDE.md,USER_GUIDE.zh-CN.md}`只补Rust v2/旧v1区分与入口，不重写Python指南或FF-005案例。Rust自身PLAN/catalog四件及P0八导航仍由主协调机械同步本bundle事实。 |
| 文案/角色/资源 | `R/locales/{zh-CN.json,en-US.json}`仅确有新可见文案时对称增补。获批Development才创建本bundle tasks，真实handoff后fresh Verification才创建checklist；只为真实附件建evidence。获批执行者使用新独占`/private/tmp/ff-004-r2-<unique>/`存build/copy/新合成状态/报告，列归属与保留条件。 |

r2相对r1新增必需入口`src/bin/ff-fixture.rs`，新增职责小模块`src/runtime/catalog.rs`/新test helper，新增父对照指南两件有限兼容说明；将config README从“新建”纠正为“增补既有”。r1允许的`src/domain.rs`、`src/app/demo01.rs`及`tests/{support/mod.rs,cli_contract.rs,runtime_regressions.rs,local_protocol.rs}`从写面收回；这些新行为可经外部装配与新测试实现，不用重写旧安全实现。

受保护集合包括：全部FF-001/002/003/005/ARCH bundle及历史/附件；全部Python工程；Rust `Cargo.toml/Cargo.lock`、`src/{main.rs,domain.rs,driver_process.rs}`、`src/infrastructure/{state.rs,audit.rs,s7_int_pdu.rs,http.rs,posix.rs,mod.rs}`、`src/services/execution.rs`、`src/app/{demo01.rs,plc_guard_get_int.rs,get_value_guard_int.rs}`、`config/{loopback.yaml,basic02.yaml,basic03.yaml}`、全部既有tests及`examples/README.*`。FF-005新增app/test/YAML/示例与行为不得迁移或顺手修；共享config/runtime只做本任务最小接线，其既有三kind/原Flow/Target序列化保持。

禁止写C#、DS/AW/DAA/SMA/CA、Backend/tools、根contracts、shared skills、AGENTS/workflow/角色、真实配置/.env/既有SQLite/历史日志、Git refs或他人资源。若确证受保护driver/状态/HTTP/摘要必须改，停止相应部分并回PM新Revision；不得静默放开allowlist或删必需AC。

## 4. R01：格式、版本与严格加载

Human Owner明确选择JSON作为每PLC可审阅配置；主运行配置继续YAML，SQLite只存各工程自己的执行事实。此选择覆盖skill的通常YAML偏好。三种语言可以各自实现同一语言中立格式，**不表示三工程当前都能加载**；配置副本、锁、状态与可写目录各自独立，不共享DS SQLite。跨运行时公开schema将来归根`contracts/`，本轮仅spec代码块，A也不在根contracts另造合同中心。

| 对象 | 版本/精确规则 |
| --- | --- |
| 单PLC JSON | 顶层对象，`format="ff.plc"`、`schema_version=1`；它与主YAML的版本号及SQLite schema版本互相独立。 |
| 主YAML | v1继续原读取合同；v2只允许`plc_files`，禁止同时出现内嵌`plcs`或原物理target。版本未知/缺失不猜测、不降级。 |
| 新格式解析 | 以下严格规则只适用于JSON v1/主YAML v2：UTF-8、无BOM；拒重复key、未知字段、null冒充缺省、数字字符串/bool隐式转换及超范围值；integer须整数词法，拒1.0/1e0。YAML v2拒alias/merge/重复key。所有对象递归闭合；无自由extensions兜底。旧YAML v1保留当前解析及限制，不批量收紧其既有行为。 |
| 容量 | 主文件≤64KiB；1..4 PLC文件，每件≤1MiB、总≤4MiB、嵌套≤16层；每PLC≤64 DB或≤4 table、总点≤4096；1..8 flow。先限量再分配/解析，超限整体失败。 |
| 文件路径 | `plc_files`为1..4唯一相对路径（每项1..255 UTF-8字节），以主配置实际所在目录为基准；允许`plcs/s7-a.json`，拒绝空路径、绝对路径、`..`、反斜线、URL/glob、变量/`~`展开及symlink。主文件、引用文件与中间层均拒symlink，末端须UTF-8普通文件；不接受空路径段或以`.`/`..`作段。改cwd不改变解析，文件名不决定协议或身份。 |
| 加载原子性 | 只读显式列表，启动一次读取并冻结全部原字节/hash，完整解析/交叉校验/能力校验后才装配。任一坏文件/重复身份/不支持能力整体拒绝；无自动扫描、热加载、后台重读或部分启动。多个文件不是文件系统原子快照，部署时应停止编辑后重启，启动报告列实际读取的各hash。 |

所有ID为ASCII`[A-Za-z0-9_-]{1,64}`，兼容DS UUID。下表标“可选”的字段缺省才可省略；显式null只在特意允许处合法。人类说明字符串按UTF-8字节计限长，不作为索引或驱动判断。

## 5. R02：单PLC公共字段与S7合同

| 字段 | 必填/类型/范围/语义 |
| --- | --- |
| `format/schema_version/id/protocol` | 必填；固定字符串/整数1/稳定设备ID/精确枚举`s7|modbus_tcp`。id与文件名、IP、显示名分离；重命名文件/改显示名不重建ID。 |
| `name/display_name/description` | 可选非空字符串，分别≤128/256/1024字节；只作技术核对/显示/说明，不参与查点或效果身份。 |
| `metadata` | 可选闭合对象，仅可含`brand/model/firmware`非空字符串各≤128字节；资料不选择协议、地址或字序。 |
| `source` | 必填闭合分型；手写恰为`kind:"manual"`及可选`note`≤512字节；DS分型见§11。不允许原始源码、运行值、模拟规则、凭据或SQLite路径。 |
| `connection` | 必填协议专属对象；host为规范IPv4字面量，禁止wildcard/0.0.0.0、广播/组播，port整数1..65535；无DNS/扫描。当前实际联网授权仅§13合成loopback端口。 |
| `dbs` / `tables` | 按protocol恰有其中一项且非空；禁止把另一协议字段塞入或从文件名推断。 |
| 点公共说明 | `name/display_name/source_name/source_path/source_native_type`可选非空字符串，分别≤128/256/256/1024/32字节；保留来源原名，不靠显示名或拆字符串伪造TIA原名。 |

S7：`connection`必填host/port/rack整数0..7/slot整数0..31；可选`local_tsap/remote_tsap`为整数1..65535，省略分别表示0x0100、0x0100+rack×32+slot。结构校验保留声明；**A的run只接受与该默认能力完全相等的值**，其他值报`unsupported_connection`，不得忽略DS的calling TSAP或扩driver接口。

`dbs[]`必填`number`整数1..65535、`size_bytes`整数2..65536、非空`points[]`，可选`enabled`为bool且缺省true。DB号在单PLC内唯一；点从父级继承DB号，点内禁止重复声明db_number。点必填`id`、`data_type:"int16"`、`byte_offset`整数0..65534，可选enabled同上；须offset+2≤size_bytes。单点是两个字节、有符号16位、大端补码，范围-32768..32767。声明大小不证明真实PLC布局或可写性。

S7 JSON v1只接收int16；BOOL/REAL/DINT/STRING等是后续扩展，不能当前成功加载后忽略。将来BOOL合同必须显式bit0..7及邻位保持/位写gate，不能仅给byte_offset声称支持；本版禁止`bit`、scale和word_order。DS的INT明确归一化成int16，其他原生类型不靠改大小写假支持。

完整合成文件`config/plcs/s7-a.json`（当前只是代码块）：

```json
{
  "format": "ff.plc",
  "schema_version": 1,
  "id": "s7_a",
  "display_name": "Synthetic S7 A",
  "protocol": "s7",
  "source": {"kind": "manual"},
  "connection": {"host": "127.0.0.1", "port": 34102, "rack": 0, "slot": 1, "local_tsap": 256, "remote_tsap": 257},
  "dbs": [
    {"number": 1, "size_bytes": 16, "points": [{"id": "value", "data_type": "int16", "byte_offset": 0}, {"id": "ready", "data_type": "int16", "byte_offset": 2}]},
    {"number": 2, "size_bytes": 16, "points": [{"id": "result", "data_type": "int16", "byte_offset": 0}]}
  ]
}
```

完整第二文件`config/plcs/s7-b.json`：

```json
{
  "format": "ff.plc",
  "schema_version": 1,
  "id": "s7_b",
  "protocol": "s7",
  "source": {"kind": "manual"},
  "connection": {"host": "127.0.0.1", "port": 34112, "rack": 0, "slot": 1},
  "dbs": [{"number": 1, "size_bytes": 16, "points": [{"id": "value", "data_type": "int16", "byte_offset": 0}]}]
}
```

## 6. R03：Modbus TCP文件合同与支持边界

`connection`恰为host/port/`unit_id`整数1..255，禁止0/广播、rack/slot/TSAP/串口字段。`tables[]`每项必填`table`四类枚举及非空`points`，可选enabled同S7；table在单PLC内不重复，地址空间相互独立。点必填id、`pdu_address`整数0..65535、data_type、`functions`，可选enabled/公共说明及下表适用codec声明。地址统一0-based，不接40001等手册编号自动减基址。RTU后续另定transport/串口/帧时序，不能当TCP的配置别名。

| table / data_type | 宽度与functions的严格组合 |
| --- | --- |
| `coils` / `bool` | 1 bit；functions恰为`{"read":1,"write":null}`或write=5。 |
| `discrete_inputs` / `bool` | 1 bit；read=2、write必须null。 |
| `holding_registers` / `int16|uint16` | 1个16-bit register；read=3，write为null或6。 |
| `input_registers` / `int16|uint16` | 1 register；read=4，write必须null。 |
| 上述两种register表 / `int32|uint32|float32` | 2个连续register；read分别3/4，write必须null；`word_order`必填`high_word_first|low_word_first`。 |

functions.read/write键均必填，值为精确整数或允许的null；不匹配表/类型即拒绝。宽度由上表推导，禁止另写quantity/width造成歧义；末地址须满足pdu_address+宽度≤65536。同一register内wire字节为网络大端，多register字序不得按厂家猜；16位及bool禁止word_order。int/uint按精确位宽补码/无符号解释，float32为IEEE754且只接受有限值；不支持byte-swap、字符串、BCD、64位及FC15/16等扩展。

register点可选`scale:{"factor":number,"offset":number}`，两键必填、有限值且绝对值≤1e9，factor≠0；省略等于factor1/offset0。工程值=解码原值×factor+offset；超出有限范围是解码错误，不截断/填0。bool禁止scale。将来写入须先逆变换、整数精确性/范围/编码核对，不能四舍五入盲写；A无此写实现。functions.write只描述所选协议操作，不授予FF写权限，DS策略和厂家“可写”资料也不授予权限。

完整结构示例`config/plcs/modbus-example.json`：

```json
{
  "format": "ff.plc",
  "schema_version": 1,
  "id": "modbus_station",
  "protocol": "modbus_tcp",
  "source": {"kind": "manual", "note": "Synthetic addresses only"},
  "connection": {"host": "127.0.0.1", "port": 34502, "unit_id": 1},
  "tables": [
    {"table": "coils", "points": [{"id": "request", "data_type": "bool", "pdu_address": 0, "functions": {"read": 1, "write": 5}}]},
    {"table": "discrete_inputs", "points": [{"id": "ready", "data_type": "bool", "pdu_address": 0, "functions": {"read": 2, "write": null}}]},
    {"table": "holding_registers", "points": [{"id": "counter", "data_type": "int16", "pdu_address": 0, "functions": {"read": 3, "write": 6}}]},
    {"table": "input_registers", "points": [{"id": "temperature", "data_type": "float32", "pdu_address": 10, "word_order": "high_word_first", "scale": {"factor": 0.1, "offset": 0}, "functions": {"read": 4, "write": null}}]}
  ]
}
```

**A的`config validate`可检查该完整结构、类型宽度/字序/scale声明，不能称协议可用。A没有Modbus连接、wire codec或读写。只要run的plc_files选中任何Modbus文件，即使没有flow引用或点被disabled，均须在State::open、状态恢复写、日志文件、owner/flow创建及任何连接之前整体报`unsupported_protocol`、exit2。** 不得过滤掉Modbus后启动S7。34502只作结构样例，不属于A允许连接/监听的端口。

## 7. R04：身份、重名、物理重叠与共享链路

1. 一个文件恰有一个逻辑PLC；重复device ID、重复规范路径，即使内容相同也失败。点ID在**单PLC全部DB/table内唯一**，包括disabled项；不能只在DB内去重或后写覆盖。同名显示/技术名可以存在，查找只认device_id+point_id。
2. DB/table范围内typed点不得物理重叠，包括只读和disabled声明；S7按字节区间，Modbus按同table的bit/register区间核对。重复地址不通过新增point ID作别名；业务角色绑定只引用既有身份，不改物理点身份或地址。
3. 规范IPv4+port在整组文件内唯一，跨协议也不允许重复。S7即使rack/slot不同也拒同endpoint；Modbus同TCP网关不同Unit ID首切片报`shared_transport_unsupported`，不能一文件盲建一会话。unit_id是逻辑寻址，host/port是链路，两者不得混为去重键。以后共享网关必须另定共享owner/串行队列和Unit路由gate。
4. 启动另核写目标物理重叠，不能以device/point别名绕过。独立读取同一点仍是多次采样；连接复用没有去重、共同快照、跨PLC事务或跨库writer fencing保证。

## 8. R05：版本装配、主YAML v2与CLI

v1继续原`Config::load/validate`、`Config/Flow/Target/Plc/Http`字段/序列化和全部三kind；其公开函数签名及旧测试调用可继续使用。新版本入口先辨明版本：v1交原解析，v2交独立严格DTO和装配；缺失/未知版本不猜测。不要将新解析规则反向套到v1，也不要替read_points填写假source/get_url/target。

| 主配置 / kind | A的支持与拒绝 |
| --- | --- |
| v1 demo01 / plc_guard_get_int / get_value_guard_int | 按当前原语义、YAML与旧app执行；旧basic02/basic03继续v1，无point API迁移。 |
| v1 read_points / teaching01 / 其他kind | 启动前按原配置错误拒绝；正式不注册teaching01。 |
| v2 demo01 | 解析点引用后装配原Flow/Target/Plc，调用原demo01及Execution；无需改app或摘要。 |
| v2 read_points | 独立只读DTO/单轮app，注入依赖设备子集，不进入Intent或commands表。 |
| v2 plc_guard_get_int / get_value_guard_int / teaching01 / 其他kind | 启动前`config_flow_kind_unsupported`、exit2；不降级成demo01，也不借本A迁移FF-005。 |

v2恰有schema_version=2、instance_id、plc_files、plc_runtime、flows、http、shutdown_timeout_ms。plc_runtime每项恰有device_id及五个预算字段，与全部文件ID一一对应，无重复/缺项/多项。沿旧区间：connect500..3000ms、IO500..5000ms、queue_capacity1..16、queue/ready_wait100..5000ms；interval100..10000ms、input_max_age1..60000ms。HTTP connect/pool各100..1500ms、total100..5000ms、connections1..8、body1..4096B；connect/pool不得大于total。shutdown5000..20000ms，且≥max(全部PLC connect/IO与HTTP total)+5500ms；默认15000ms。不因文件拆分扩大原预算。

flow共同必填id/kind/business_name/interval_ms/device_ids；id与business_name仍用既有valid_id，device_ids为1..4唯一已声明ID。demo01另必填source_id/get_url/input_max_age_ms/target，source_id仍valid_id，URL沿原http(s)/host/无凭据及fragment合同；target恰为device_id/point_id，必须属于依赖子集且是enabled的S7 int16。read_points另必填reads（1..16唯一device_id/point_id引用），全部属于依赖子集且enabled；禁止demo01专属字段。每文件/DB/point都校验，包括未引用/disabled项；无流引用不代表文件可以不支持。

完整`R/config/catalog-demo.yaml`与§5两JSON共同落实为A的正式合成样例：

```yaml
schema_version: 2
instance_id: ff-rust-catalog-demo
plc_files: [plcs/s7-a.json, plcs/s7-b.json]
plc_runtime:
  - {device_id: s7_a, connect_timeout_ms: 3000, io_timeout_ms: 5000, queue_capacity: 16, queue_wait_ms: 2000, ready_wait_ms: 3000}
  - {device_id: s7_b, connect_timeout_ms: 3000, io_timeout_ms: 5000, queue_capacity: 16, queue_wait_ms: 2000, ready_wait_ms: 3000}
flows:
  - id: read_pair
    kind: read_points
    business_name: synthetic_pair_samples
    interval_ms: 200
    device_ids: [s7_a, s7_b]
    reads: [{device_id: s7_a, point_id: value}, {device_id: s7_a, point_id: ready}, {device_id: s7_a, point_id: result}, {device_id: s7_b, point_id: value}]
  - id: demo01
    kind: demo01
    business_name: synthetic_command_to_int
    interval_ms: 500
    device_ids: [s7_a]
    source_id: demo01-feed
    get_url: http://127.0.0.1:34880/demo01/command
    input_max_age_ms: 10000
    target: {device_id: s7_a, point_id: value}
http: {connect_timeout_ms: 500, total_timeout_ms: 1500, pool_wait_ms: 500, max_connections: 8, max_body_bytes: 4096}
shutdown_timeout_ms: 15000
```

新CLI恰为`config validate --config <main.yaml>`或互斥`config validate --plc-file <one.json>`，只读，不开状态库/锁/日志/网络。stdout单个JSON结果含scope、format_valid、runtime_compatible、files（实际path/id/protocol/sha256适用项）和issues（稳定error_key/字段路径，至多32项并显式issues_truncated）；不回显配置全文/运行值。结构有效exit0，即使runtime_compatible=false；坏结构exit2。单文件结构通过不能证明整组依赖/端点/写冲突有效。v1主配置校验如实标为legacy范围，不凭空给它JSON来源hash。

run仍显式--config/--state-dir、默认dry_run、显式--execute；先完整结构/交叉/能力preflight，再`State::open`。有效组含任何Modbus（未引用或disabled也算）整体`unsupported_protocol`/exit2；非默认TSAP为`unsupported_connection`/exit2；共享Modbus端点为`shared_transport_unsupported`/exit2。新稳定能力错误须在commands明确映射为配置类exit2，不能落入现有“其他错误exit1”。结构错误先报告结构问题；不先启动S7或恢复原in_flight，再发现另一文件不支持。

## 9. R06：只读句柄、独立flow与有界观测

A的新增目标接口是`devices[device_id].read(point_id).await`；Rust可用安全get/Result表达。它由注入上下文绑定flow_id，只暴露device_ids子集及enabled点，不向app暴露全局owner map、raw client、DB/offset、SQL或raw write。每个点引用启动时解析到冻结的物理地址及既有Owner；读取只委托原`Owner::read`，不增加driver、第二队列、连接池、每请求线程或新的设备锁/锁文件。demo01写继续只经原Execution。混合S7/Modbus的同形调用只是B以后的接口目标，A含Modbus配置不能运行。

read_points每轮按reads列表顺序await；首个失败结束该轮。每轮有round_id，状态in_progress/complete/failed/canceled；每项success/error/not_attempted。成功样本含device_id/point_id、原flow_id/request_id、generation、typed int16值、quality=good及响应完成时的`received_at`（RFC3339 +08:00，保留毫秒）。它来自该次真实Owner样本完成时刻，不是设备事件时间或health刷新时间。失败不填0/false/旧值，未读项无sample/value；新轮清理旧轮可见项，不拼接跨轮“完整结果”。

每flow仅保留最近一轮≤16项，8flow总≤128项；只作内存观测，不写commands或新SQLite表。新观察沿既有5秒health节奏，增加有限`points_health` JSONL：同一round_id每块至多4项，含chunk_index/chunk_count及各自sample/error事实，最多4块/读flow/5秒；跨块不是原子快照。保持单行≤4096B（含旧Audit外层和转义context），不把全部128项塞入旧health单行，不带自由描述/原payload；最大ID/错误边界须实际校验。已有health字段/UTC外层timestamp保持原producer；新上下文的observed_at/received_at按+08语义。成功普通读不逐tick/逐点持久刷日志。

配置启动摘要在preflight成功、已有audit打开后记录每文件的id/protocol/实际hash，最多4件、分行有界；不记录JSON全文，来源hash不作为执行hash。失败/恢复沿既有flow健康转变事件；没有新health监听器、查询CLI、遥测平台或永久样本历史。测试可经新模块的有限快照读取当前轮，真实CLI仍须验证points_health与协议trace，不能只直接调用app取得通过。

各flow独立异步推进；同一flow上一轮结束后再等interval，在途迭代≤1，无积压补跑。每PLC长期owner/child/client/FIFO沿旧实现，真实driver IO≤1；不同PLC独立，HTTP/timer不占PLC队列/执行位。同点多流是独立sample/request，不是缓存去重/共同快照。配置校验是静态gate，**无所有PLC ready屏障**；B未就绪只阻塞依赖B的操作，顺序read_pair可等B，独立A流继续。

ready/queue/dispatch IO预算、原ClockAnchor/来源TTL、400ms内部回收预留、stop闸门/unknown全部沿FF-001 r4，装配不更改owner/driver算法。观察内存只短时复制，不持同步保护跨await/IO，不增加全局IO锁。停止先同时封全部owner准入/dispatch，取消未发项；默认15秒单一全局预算内真实join/reap后才报告资源关闭。forced、超时或未释放仍为故障，不能以丢JoinHandle/仅PID消失冒充正常。

## 10. R07：效果身份、旧状态与回退

旧`Config/Flow/Target`序列化、Input/Intent摘要算法、Resource和Execution原字节保留。v2 demo01先解析点引用，规范化为旧全部Flow字段：id/kind/business_name/interval_ms/source_id/get_url/input_max_age_ms与target.plc_id/DB号/声明大小/offset/type=INT；Plc取JSON id/endpoint/rack/slot和主配置预算。只有这些旧语义逐项等价，才调用原摘要得到相同config_identity_hash；不得改算法、删旧字段或直接hash新DTO。read_points走独立DTO，无虚构Target/Intent，也无状态表中的command。

JSON路径/字段顺序/source/export时间/display资料不进入旧效果摘要；其原字节hash和DS原payload SHA只作来源。改实际DB/offset/type/声明大小/业务名等旧语义必须改变旧摘要，原相同source/command触发identity_conflict，保留原记录；新JSON字段不能掩盖真实变更。两个不同point ID解析到相同原地址不能消除unknown。主v2不同点别名仍受§7重复/物理重叠校验。

JSON id规范化为旧plc_id，point ID不取代物理Resource。手写ID换DS UUID可能改变旧plc_id，A不提供别名/状态迁移；应保留稳定ID或另批人工writer交接，不能宣传自动无缝继承。原库全部unknown（包括启动从in_flight恢复者）按endpoint/rack-slot/DB/字节重叠阻止新写，改flow/source/point/command身份不能绕过；独立读仍可运行，读回42不升级unknown。

本A不改DDL/store_meta schema1/trigger，不清进度、不重写旧不可变行/历史、不改UTC日历producer。允许的旧状态变化仅原API已有的正常接纳、派发/确认和启动in_flight→unknown恢复及其追加event；不把“schema兼容”误写成运行库逐字节不变。**不支持配置的preflight拒绝**则必须连这些恢复写也没有，原库/日志/目录前后hash不变。

新增received_at/observed_at是明确本机观测，使用现有chrono统一+08转换；原Unix ms/monotonic/SQLite时间字段保持原含义。旧UTC日志/SQLite差异已识别，本轮不触达原producer或声称时间整改完成；若必须改该链路，停写并回PM明确时间/schema维护范围，禁止混存或盲加八小时。

正常资源关闭exit0与存在unknown是不同事实：Rust预存unknown导致写flow blocked时，既有关闭路径可能仍正常exit0；必须同时检查inspect/阻写，不能把它写成命令成功或强改旧退出语义。真实协议错误场景按原owner_had_errors/runtime_fault非零分类，强收不当正常通过。run仍要求已初始化、implementation=rust/mode/instance匹配的原库；dry_run只simulated且写0，execute分库。

回退先停writer，核pending/in_flight/unknown/confirmed并保全新配置、原库/日志，再由明确授权决定恢复本任务归属diff/旧二进制+v1；目标/语义不一致不能自动切换。不得删库、清进度、反向写PLC或复用新库绕过unknown。独立副本/跨语言切换不授予共享物理资源执行权，仍需唯一有效writer交接。

## 11. R08：DS来源映射与导出关系

以下只定义FF接受文件所需事实，交接DS owner；不授权DS源码/UI/SQLite写入。FF可先手写且不需要DS在线。DS-002导出阶段仍须独立批准；根contracts公开schema也须另批，不能用本spec要求另一个会话自动执行。

| DS现有来源 | FF字段/明确处理 |
| --- | --- |
| InstanceConfig.id/name | 保留UUID为id、实例name可作FF name/display_name核对资料；与既有FF手写ID不同须按§10核对，不自动换身份。 |
| host/port/rack/slot/calling_tsap/called_tsap() | host/port原为server bind，导出必须明确确认FF可达connect host/port；calling→client local，called→client remote，方向经SDK/真实COTP核对。wildcard不可直接导出；A拒绝不可表达TSAP。 |
| DbConfig.number/length/enabled、PointConfig.id/name/display_name/byte/bit/enabled及address/names确认 | 映射dbs.number/size_bytes/enabled、point id/说明/byte_offset/enabled；仅INT→int16，DS长度1字节等不可表达布局也拒绝。缺地址/布局/命名确认或不支持类型先列全问题，不生成执行假地址或静默丢点。 |
| 绑定tree、segments/source_path、source_versions | 原source_name/path/native_type有事实才带；由结构化来源读取，不从display_name/拼接字符串猜。手工点没有TIA原名可省略。 |
| configuration_revisions revision_id/saved_seq/原payload sha256 | 必须选择真实不可变saved revision，source绑定其原始身份/指纹；Workspace.schema_version不是FF文件版本。草稿、latest saved、selected与actual_loaded分别记录，不能互相冒充。 |
| initial/rule/client_write/ui_maintenance、在线值 | 不进入FF执行合同，不转成FF写权限；没有Modbus现有模型可真实导出。 |

当前DS没有protocol/brand/model/firmware/exporter_version的持久字段：既有v1来源只能明确映射s7；可选metadata缺事实就省略，不由实例名称推厂家/型号，exporter_version与generated_at由未来真正导出器产生。DB/点确认由DS现有layout/命名签名核对；bit或非INT点即使disabled也不能伪装int16或静默丢弃。表中可映射不等于当前已交付exporter。DS-002仍draft，FF本合同不构成其Owner接受。

DS来源分型`source.kind="device_simulator"`须恰有：`export_mode:"saved_revision"`、`instance_id`（等于设备id）、`revision`、`exporter_version`（非空≤64字节）、`generated_at`（真实RFC3339 +08:00）。revision恰有id（规范小写UUID）、saved_seq（整数1..9007199254740991）、payload_sha256（64位小写hex原payload SHA）。可选`runtime_observation`恰有observed_at（真实+08时间）、selected_revision、loaded_revision；后二者为同形revision或null，null明确表示没有该事实。缺事实省略整个观测，不用latest填loaded。

首导出模式只接受一个明确saved revision的该实例切片，不混未保存draft/运行值；观测loaded不同可明确提示，文件并不证明模拟器已加载/启动。导出来源内部的DB/点/来源版本关联须由DS验证；FF只能校验声明/格式与文件hash，不证明DS库或真实PLC事实。未来“按actual_loaded导出”允许逐实例不同版本但需单独mode/gate，本v1禁止。DS完整问题列表、失败无半文件、显式可达端点确认及来源原SHA测试归DS阶段；本轮不编造DS导出成功样本/hash或替其批准。

## 12. R09：角色、工具链与文档handoff

PM用`aiis`、`project-governance`、`plc-point-mapping`。A的实际Development/Verification按范围继续用这些，并加载`rust-runtime`（配置/owner/资源）、`i18n-workflow`（新CLI文案）和`code-document-indexer`（新关键文件/自身索引）。不加载Tauri/Web/Celery模板，不由PM代写技术实现或授予QA结论；若必须触达状态producer/schema先回PM，再按需路由专门skill。

沿现有Cargo工程：edition2021、rust-version1.89、锁定rust-snap7=1.142.2/native链。`Cargo.toml` SHA256=`d28d9068b6804afe0f2605bdc5d90976a45e2e055881c771e26e7203291e8ea8`，`Cargo.lock`=`13404c36665fa46f50f40291e111bcb11e99b9ee8c13d29130004c9ef3d74fc6`，交付字节不变。serde/serde_json/serde_yaml/sha2/chrono沿现有锁；无新crate、Modbus包、driver/native替换或SDK/target/解释器下载。获批后可按冻结锁准备缺失公共构建缓存，不能解析新锁、安装Agent辅助依赖进项目或改全局工具/profile。

执行者记录实际rustc/cargo/clang/OS/CPU，首验只macOS arm64 synthetic。当前Rust有UnixStream/继承FD/POSIX锁/Unix signal，Python也有fcntl依赖；Windows交付不是本A能力，Linux原生也未在本轮证明。无现场、三平台、服务托管/安装、长稳或部署资格外推。

文档须按版本说清：v1三正式kind保持，v2 Rust仅demo01/read_points，Modbus只校验；Python/C#未加载新格式、DS未导出。`config/README.*`已有三YAML表，不覆盖旧表/命令；增补本catalog入口及DS字段/缺口说明。Rust USER_GUIDE新增最短可运行点引用/观测/阶段发布教程，原teaching01仍只在独立教程副本接线；config/runtime的精确编辑锚点如受接线影响，只修真实必要锚点，中英对称并复演。父USER_GUIDE仅补版本区分和Rust新入口，FF-005 examples与Python自身指南不改、不把advanced教学计划提前改成runnable。

新小模块保持纯配置/装配/服务/单轮app分层，既有入口只分派；避免把已较大的runtime.rs继续堆成大文件，新增catalog逻辑归有限runtime/catalog模块，不顺手拆旧owner或建立通用注册平台。Development在tasks记录需求/AC→真实文件/命令/退出/限制/资源与精确candidate；真实developer_handoff后交新的fresh-context Verification，QA通过只进入Owner终验。

## 13. R10：获批后的命令、夹具阶段与证据

以下全部**拟执行、当前not_run**。先在Rust工程根建立实际绝对FF_PROJECT及全新独占FF_RUN_ROOT；每命令分别记录cwd、argv/版本、退出码及原输出。系统文本解释器只可做文档/报告核查，不能冒充项目Rust验证。正式树与独立单工程副本均须按自身source/manifest/lock/config/locales/tests/docs构建/运行，不借FF-005已回收环境、兄弟/父runtime或DS服务。

```bash
FF_PROJECT=$(pwd -P)
FF_RUN_ROOT=$(mktemp -d /private/tmp/ff-004-r2-XXXXXX)
printf '%s\n' "$FF_PROJECT" "$FF_RUN_ROOT"
rustc --version
cargo --version
rustfmt --edition 2021 --check src/config/catalog.rs src/config/runtime_v2.rs src/services/devices.rs src/app/read_points.rs src/runtime/catalog.rs src/fixture/catalog_demo.rs tests/plc_catalog.rs tests/multi_plc.rs tests/catalog_compatibility.rs tests/modbus_catalog.rs tests/catalog_support/mod.rs
cargo build --locked --release --no-default-features --bin field-flow --target-dir "$FF_RUN_ROOT/product"
cargo build --locked --release --features test-fixture --bin ff-fixture --target-dir "$FF_RUN_ROOT/fixture"
FF004_EVIDENCE_ROOT="$FF_RUN_ROOT/catalog-evidence" FF005_EVIDENCE_ROOT="$FF_RUN_ROOT/legacy-basic" cargo test --locked --features test-fixture --target-dir "$FF_RUN_ROOT/test" -- --nocapture --test-threads=1
"$FF_RUN_ROOT/product/release/field-flow" config validate --config "$FF_PROJECT/config/catalog-demo.yaml"
"$FF_RUN_ROOT/product/release/field-flow" config validate --plc-file "$FF_PROJECT/config/plcs/modbus-example.json"
"$FF_RUN_ROOT/product/release/field-flow" state init --synthetic --mode dry_run --state-dir "$FF_RUN_ROOT/dry-state" --instance-id ff-rust-catalog-demo
"$FF_RUN_ROOT/product/release/field-flow" state init --synthetic --mode execute --state-dir "$FF_RUN_ROOT/execute-state" --instance-id ff-rust-catalog-demo
```

FF004_EVIDENCE_ROOT只控制新harness证据目录，须不存在或空；FF005_EVIDENCE_ROOT仅给受保护旧basic_examples提供本任务新目录，不改它的测试逻辑/原预期。其他旧回归仍可能产生硬编码FF-001前缀的自有新目录：运行前后以确切路径差集登记本轮资源，不按前缀清理或冒称旧任务新增证据。既有格式基线不作为整树格式化授权；旧文件只核本任务新增行/局部diff，不能为了cargo fmt全绿重排旧源码。

### 13.1 固定catalog模式与确定性发布

新增test-fixture入口只为`ff-fixture --catalog-demo --evidence-dir <new-path>`，由真实bin入口分派新模块；旧`--config/--evidence-dir`及`__native_fixture`模式/端口/42/停止行为保持。新模式固定A proxy/native=`127.0.0.1:34102/34103`、B=`34112/34113`、HTTP=`34880`，不接任意点表、DS、34502/RTU或新控制端口。所需私有native子模式仅服务上述A/B，不成为产品API。

A DB1/DB2各16B：DB1 value@0=12、ready@2=1，DB2 result@0=56；B DB1/16B value@0=34。除这些完整两字节区间外全部A5。native初始化直接种值，无客户端准备写；独立准备/事后读回也单列计数窗口，产品稳定窗口不混入额外oracle连接。新fixture的协议trace独立按raw请求/响应核DB、offset、长度、COTP C1/C2、wire值与在途区间，不调用产品codec生成“预期正确帧”。每PLC最多2000条trace、两台合计≤4MiB，达到上界显式标截断/该证据不完整，不能静默截断后判通过。

启动后输出结构化`fixture_ready`，HTTP初始是严格七键idle（ready=false及四个null），无command时间或写许可。手工只增加一项有限stdin命令`issue`；收到后生成本场景唯一command_id、issued=当前Unix ms、expires=issued+60000、source=demo01-feed、value42，并从此返回完全相同原body。第二次issue/非法输入明确拒绝且不改原身份/时间；空行或EOF按旧ENTER习惯关闭新模式。测试调用同一新模块的issue-once方法，不另建管理API。fixture_ready不代表已发布命令。

严格时序为：build/init完成→fixture_ready→启动产品→先验证完整初始读轮与idle→一次issue→等待状态/计数/后值。所有等待是带实际条件与截止的轮询/通知，固定sleep不作为通过依据。命令发布后的必需观察须在原10秒input_max_age内完成；不得改配置放大年龄、刷新原时间或重发新身份掩盖过期。未及时满足则保留失败，不碰运气重试取绿。

```bash
"$FF_RUN_ROOT/fixture/release/ff-fixture" --catalog-demo --evidence-dir "$FF_RUN_ROOT/dry-fixture"
"$FF_RUN_ROOT/product/release/field-flow" run --config "$FF_PROJECT/config/catalog-demo.yaml" --state-dir "$FF_RUN_ROOT/dry-state"
"$FF_RUN_ROOT/product/release/field-flow" state inspect --state-dir "$FF_RUN_ROOT/dry-state"
```

这三条分别属于fixture前台终端A、产品终端B、产品停止后的inspect，不是同一shell顺序阻塞执行。交付指南必须给完整A/B赋值、实际绝对路径、启动/观察/issue/停止/报告步骤：两终端分别输入真实FF_PROJECT/FF_RUN_ROOT，不假设共享变量；B记录自己的产品PID并SIGINT/TERM/wait，A保留自己的fixture进程并ENTER/wait。execute另起新fixture/evidence且用独立execute-state，产品显式--execute；不把dry库当execute库或复用一条已过时命令。

### 13.2 有界场景与精确前后观察

| 场景（新harness内存/tmp变体，不增加正式案例YAML） | 确定性前后条件与计数 |
| --- | --- |
| S1 catalog dry / execute，各独立新场景 | issue前read_pair至少1完整轮按顺序`[12,1,56,34]`、GET≥1且严格idle、command0、两PLC写0。issue后同body至少10次GET，须在10秒内：dry simulated1/总写0、值仍`[12,1,56,34]`；execute confirmed1、A WriteVar=1且仅DB1@0写42，B写0，后完整读轮`[42,1,56,34]`。全部未触区间A5保持。窗口计数明确分pre-issue/post-issue/事后独立核验。 |
| S2 三流共读 | 主v2仅三个独立read_points，各interval100ms、各读A.value；HTTP保持idle。每流≥20个成功独立request/sample、同flow迭代≤1；稳定窗口A一PID/generation/session、driver真实在途≤1，FIFO容量/顺序有界。公开CLI真实load/调度及5秒汇总须成立；可补新句柄服务级样本收集证明身份，不以直接调用app替代CLI。 |
| S3 B缺席/慢connect与多PLC并行 | 自有fixture内部固定B-off变体不启动B端口（CLI正常模式仍两台）；配置保留read_pair，并增加仅依赖A的100ms读流。A首ready起8秒内≥20成功、最大相邻成功间隔≤500ms；read_pair到B处明确失败/后项not_attempted，A独立流继续。正常慢connect子场景使用catalog内部B-Setup回应门（最多1200ms）：至少一笔A完整成功ReadVar及匹配响应实际完成时，B仍connecting且其最终Setup回应尚未发出；用夹具同一单调时钟/事件序号记录A完成<B最终Setup发出，另用实际Owner状态/既有ready事件核对B当时connecting、随后才ready；不跨时钟混算，未观察到因果顺序即失败。门由真实A完整响应完成条件释放，1200ms仅作失败上限，不以任意sleep取得通过。8秒≥20/maxgap500只是持续性辅证，不能单独证明无ready屏障。另以两台限内IO延迟证明两owner可同时各在途1而单owner≤1；不增加外部控制端口/平台。真正B-off按当前Driver::spawn失败会走force并标forced_driver_stop/非零，必须原样记录失败退出；这是明确预期旧故障分类。仍须A独立成功、B未发ReadVar/WriteVar均0、实际有界reap/全局预算与资源回收，不冒称全进程正常/零forced。预期故障只限有实际trace/PID/source证据精确归属B bootstrap/连接失败的driver/错误链，不按场景名全局豁免forced。A owner/driver及flow/state/fixture仍须相应真实正常join/退出、无forced；A被阻塞/强收、无法归属的forced、孤儿或超预算必须qa_failed回报，不由S3故障预期豁免。不虚构现有日志没有的关联/退出字段。 |
| S4 慢HTTP | 一个demo01 GET延迟1200ms（HTTP total仍1500）且返回idle，独立A读流100ms在8秒内≥20成功/maxgap≤500ms；所有写0、同flow≤1且不补跑。使用请求进入/完成及ReadVar时序证明HTTP等待无PLC占位，不只看总耗时。 |
| S5 v1→v2 confirmed兼容 | 新合成旧schema1库，先用等价v1/旧app实际完成同命令一次confirmed；立即正常停旧产品，同fixture原body/ID/issued/expires不变，启动逐项等价v2、原库继续≥10轮仍写总1/原confirmed1。此专用等价对照两侧interval100ms，整体来源年龄≤8秒，避免两次500ms×10轮越过10秒；不改正式catalog-demo配置/TTL。 |
| S6 旧in_flight/unknown保护 | 用原State API在新合成v1库形成合法T1/T2（未伪造ACK），关闭后v2启动先恢复unknown；同身份及显式point别名/flow/source/新command的重叠写均拒绝，实际WriteVar0，独立非冲突读取继续。每个新命令只生成一次时间，unknown原意图/dispatch保留；读取42不会确认它。schema/trigger/不可变字段不变，只有原合法恢复event/状态变化。检查写blocked与资源关闭分别给结论，不把exit0说成unknown解除。 |
| S7 摘要/来源与拒绝 | 同typed v1/v2及改文件名/字段顺序/display/source观测仍同旧hash/Resource；同原source/command改DB/offset/声明大小/旧语义触发identity_conflict且原行不变。保证命令在有效期内测试冲突，不能让stale先挡住而误报身份检查通过。坏文件/不支持能力则在State::open前退出2，缺状态目录仍缺，既有合成库/日志字节不变。 |
| S8 原安全与文档回归 | 完整受保护Rust测试含FF-001队列/Clock/started/TTL/ACK/unknown/stop和FF-005原basic_examples均实际运行；结果/数量/失败如实记录。Rust teaching01仅独立副本按现指南精确锚点接线并各跑一次dry/execute，正式teaching01拒绝；Python不运行/不改，不声称本QA重验Python或旧hold_ack已修。 |

S2/S3/S4的新read_points快照另外保留累计completed_rounds/successful_reads及错误数等固定整数（饱和不溢出）；随5秒分块汇总，样本仍只留最近一轮，不建请求历史队列。harness按原request/flow身份、原始trace及有界成功时刻表对照计数；记录至少所需20样本的时间/身份在测试报告，不把业务假定计数当实际协议计数。

新场景每件≤45秒含回收、新catalog矩阵≤600秒，构建不计入该场景窗口；超过即失败并保留证据。原测试有自己的既有故障/forced期望，不混入本新场景的无forced结论，也不删旧负例。新增正常场景必须产品/fixture退出0、runtime_tasks_joined/shutdown_complete、所有child/线程真实join/wait、确切PID消失与五口实际重新bind；预期故障按其旧非零语义单列，仍核自有fixture自然关闭与资源事实。

新harness逐行解析JSONL，按event、真实bool与适用退出/信号/线程结果判定；Rust Audit的context是JSON字符串时再解析一层。正常场景拒绝event=forced_driver_stop、结构化error_key以forced_driver_stop开头、had_forced_driver_stop=true、未join/非零正常child或强制收尾；S3 B-off仅按前述有证据归属B bootstrap/连接失败的错误链预期单列，必须证明旧force实际完成reap/未开始B读写，A与flow/state/fixture正常join无forced，不把该结果记正常或全局容许forced。不能用空白敏感substring/仅无PID推断成功。Rust现有reaped事件不含独立exit_code，不虚构该字段；以既有Driver::close实际ExitStatus成功检查、owner任务join及正常事件共同核实，fixture新模块实际记录自己Child.wait/线程join结果。对紧凑/带空格JSON、bool false/true及非零退出的必要判定向量纳入新测试，不修改旧FF-005 harness。

另一个已核旧限制是Driver::spawn在bootstrap/连接失败时调用force后返回forced_driver_stop；B-off不可能仅靠装配变成全程无forced。该负向场景只验A隔离及故障分类/实际回收，限内慢connect场景才要求零forced。FF-005已知完整`hold_ack`扣留ACK曾触发强收，旧driver/native均未因此修复；本A不以该向量宣称正常关闭或新增通信恢复能力。需要新协议错/unknown观测时限新catalog内有限截断ACK或原State API的保守in_flight恢复，明确区分“无有效ACK”和“完整ACK整包丢失”。若本A自己的必需正常关闭失败，不转deferred或改旧driver取绿，回报精确证据/范围问题。

另验空cwd产品/fixture help零副作用，换cwd用相同绝对主YAML解析同一组文件，端口冲突即停（不杀占用者/不自动换端口）。正式树与独立copy候选hash/实际启动入口一致；临时源码/target/新状态均列精确路径/用途/保留条件。必要证据先持久入tasks/checklist，Owner终验后仅由active coordinator核占用/归属/后续及证据依赖再决定回收，不清理旧任务资源。

## 14. A的验收矩阵

以下仅为精确r2 A批准后Development与fresh Verification的必需验收；P0没有执行其中任何产品命令，不创建QA文件。必要协议/状态/资源事实不能只靠mock/schema/编译通过。

| AC / 需求 | 可观察通过标准 |
| --- | --- |
| AC01 / R01/R09 | 正式Rust与独立单工程copy locked build/非零测试/真实启动成立；manifest/lock不变，无父/兄弟/DS运行依赖，源码交付一致。 |
| AC02 / R01–03 | 三JSON及主YAML v2严格加载；未知/重复字段、整数词法/null/隐式类型、容量/深度、协议互斥、类型/codec/functions错误整体拒绝；v1原规则/三kind/Flow序列化保持，v2仅demo01/read_points，其余kind启动前exit2。 |
| AC03 / R01/R04/R05 | 缺文件/路径重复/穿越/symlink/错cwd、重复设备/跨DB点ID、越界/重叠、未引用坏文件和disabled坏结构均完整preflight拒绝；所有文件同冻结加载摘要，无部分启动。 |
| AC04 / R03/R05/R07 | Modbus单文件format_valid=true/runtime_compatible=false/exit0；有效组含Modbus含未引用/disabled，run整体unsupported_protocol/exit2，零owner/flow/连接/状态恢复写/日志/锁。非默认TSAP同样拒绝；既有合成库/日志前后hash相同。 |
| AC05 / R02/R06/R10 | S1以实际CLI/固定多DB夹具先读`[12,1,56,34]`再issue42，后dry不变/execute仅A.value42，ready/result/B及A5全保持；匹配WriteVar ACK/T3与C1=0100/C2=0101独立raw断言；五个INT边界原回归继续。 |
| AC06 / R05/R06 | 公开read_points真实一流两PLC，只有依赖子集可见，缺/禁用/越权点和错target启动前拒绝；success/error/not_attempted与原sample身份/typed值/响应观测时间可核，无旧值填充；最近≤128，5秒分块/单行≤4KiB和最大ID边界成立。 |
| AC07 / R06/R10 | S2三流各≥20独立成功request/sample，一PLC长期1 PID/generation/session、真实IO≤1/FIFO有界；不同PLC可各在途1，同flow≤1且不补跑，无新的连接/队列/全局IO锁。 |
| AC08 / R06/R10 | S3 B缺席/1200ms限内慢connect与S4 HTTP1200ms各自8秒窗口，A100ms读流≥20成功/maxgap≤500ms；正常慢connect另证至少一次A成功ReadVar/匹配响应完成先于B最终Setup回应/ready，此时B仍connecting；read_pair受B影响不冻结A，HTTP不占PLC位，无全PLC ready屏障；B-off的既有force/非零预期单列，A不得被强收，所有资源仍真实回收。 |
| AC09 / R06/R10 | 原ready/queue/dispatch预算和真实底层结束/queued-stop零下发回归；新正常场景全局默认15秒内真实join/reap/Child.wait/五口rebind，无forced/未释放假成功；S3 B-off按旧force预期故障单列，不混入正常通过。结构化JSON/转义context/退出与线程判定不受空白影响；旧hold_ack限制诚实保留。 |
| AC10 / R07 | v1与等价v2旧typed摘要/Resource一致，改路径/顺序/导出观测/display无新效果，真实地址/旧语义改动在有效TTL内冲突且保原意图；DS UUID换ID不宣称无缝兼容。 |
| AC11 / R07/R10 | S5原confirmed库接v2≥10轮仍总写1；S6原in_flight→unknown、新身份/别名/重叠写0而不相关读继续；inspect原unknown不因读42/正常资源退出改变。旧schema/trigger/不可变身份保留，无DDL/清库/时间迁移，仅原合法状态恢复与追加event。 |
| AC12 / R05/R07/R10 | S1默认dry simulated1/写0；显式execute仅A一次匹配ACK+持久confirmed、B写0；原命令时间不刷新，TTL/unknown/唯一Execution路径保持；无raw write快捷口或读回确认。 |
| AC13 / R08/R09/R10 | 双语版本/kind/API/DS缺口与saved/selected/loaded/端点/TSAP真实，不称DS已导出或Modbus/三语言已实现；新fixture真实入口/阶段命令可照做，旧basic02/03与teaching01兼容，CLI locale对称/validate零副作用。受保护Rust基础测试和教程必要复演通过，Python字节不变且本轮not_run。 |
| AC14 / 全文 | tasks逐AC列真实候选/命令/数量/失败/资源，新的fresh-context Verification独立checklist/verdict；旧bundle/任务外dirty/FF-005证据保护hash成立。P0静态检查不冒充DEV/QA；qa_passed只进入Owner终验，B/C/Windows/现场/长稳/部署另gate。 |

B未来spec仍须冻结client精确版本/锁、四表FC子集、codec golden、transaction ID/Unit/function/长度关联、超时废旧连接与迟到隔离、有界owner/关闭、unknown/no-replay、共享网关及独立oracle；A结构校验通过不跨过这些gate。

## 15. 风险、排除项、PM静态自检与批准记录

| 风险 | 控制/回退 |
| --- | --- |
| 新DTO/文件变动改变旧写身份 | 旧domain/app/Execution原字节，v2装配为旧typed对象；有效TTL内做hash/原库对照，不删库或新造ID。 |
| 先读12与写42竞态、过时命令掩盖验收 | 新catalog初始idle，先观察完整读轮再issue一次；时间只生成一次，状态兼容使用有界快速等价变体，不增TTL。 |
| Modbus格式或DS来源被当运行支持 | preflight整体unsupported；DS来源事实/缺失明确，DS/Modbus各有独立gate，不仿造接受或导出结果。 |
| 新观测膨胀Audit单行/最近轮被当历史 | 每flow≤16/总128，5秒最多4项一块、≤4096B；sample时刻不重取，不做永久点历史或高频日志。 |
| 结构化false positive、强收当正常资源 | 逐JSON字段/原context解析、正常wait/join/退出/PID/端口多证据；旧hold_ack失败保留，必需新场景失败不可降级。 |
| B-off触发现有Driver::spawn的force/失败退出 | r2提交Owner审阅的是负向分类/隔离验收方法，运行仍记失败退出，不作正常或零forced证据；A进展、B未发零下发、实际reap/端口释放及全局预算仍必需。A阻塞/被强收、无法归属的forced、孤儿/资源未释放/超预算须qa_failed，driver与hold_ack限制未修。 |
| 并行dirty/文档锚点或旧教学回归被覆盖 | 精确allowlist/保护hash及原脚本断言，现有config README增补；正式交付树/copy一致，旧测试/FF-005 bundle不改。 |

排除Modbus实际通信/RTU/EVO或其它厂家实机映射、S7其他类型、basic02/03的v2迁移、FF-005进阶库交付、POST/demo02/事件DSL、DS UI/导出实现、Python/C#加载、自动扫描/热加载、缓存共读/原子快照/跨PLC事务、writer fencing/接管、状态/历史时间迁移、Windows/Linux移植、现场/托管/容量/长稳、安装/服务/发布/部署、真实PLC/API/数据库、Git/GitHub动作及资源删除。当前P0不装依赖、不运行工程/测试/编译/schema或任何协议监听/连接。

本轮P0仅文本/路径/hash/Markdown检查；真实命令与退出由PM handoff给出，不称DEV自检、独立QA或全仓治理通过。原r1记录的全仓checker旧历史metadata/catalog诊断是历史事实，本次不重跑项目checker或改旧bundle取绿。PM自有`/private/tmp/ff-004-pm-adrva2hd`只存原r1/文本草稿/静态审计材料，未创建项目环境/产物/状态/服务；保留供主协调复核原r1和精确diff，关键合同与原r1均在本spec，不以tmp作唯一事实源。主协调完成文本审计且无后续/证据依赖后再按其归属决定回收，本PM不清他人资源。

| 日期 | Revision / 真实决定 | 下一gate |
| --- | --- | --- |
| 2026-11-03（Asia/Shanghai） | 实际命名PM形成r1 draft，原全文/原SHA保留；只有PM阶段授权，无实施批准 | 原r1已由本r2范围草案取代，历史不抹除。 |
| 2026-11-04（Asia/Shanghai） | 实际命名PM基于FF-005验收后的当前源码完成r2 draft；“好的”只支持继续PM，未登记owner_approved | 主协调审计唯一spec/保护hash并机械同步原八导航，提交精确r2路径/SHA及A批准点给Owner。 |
| 2026-11-04（Asia/Shanghai） | Human Owner明确批准精确FF-004 r2 A，原话与批准前草案SHA见§1最新有效决定；PM据此登记owner_approved，原A范围/allowlist/14AC/风险/排除项不变 | PM -> Development；由主协调实际调用Development，真实developer_handoff后进入新的fresh-context独立Verification，随后Human Owner最终验收；当前未产生DEV或QA结论。 |

**PM -> Human Owner精确批准点：FF-004 r2 A。** 包含每PLC JSON v1/主YAML v2、仅Rust S7 int16与read_points/demo01点引用、v1三kind及原状态身份兼容、Modbus严格只校验/运行前整体拒绝、§3有限文件与无新依赖/driver/schema边界、确定性catalog阶段及AC01–AC14，以及B-off既有force/失败退出的负向分类与限内慢connect正常子场景。两个旧driver限制均未修，本轮均未执行。批准后由主协调实际调用Development创建tasks/实施A；真实developer_handoff后另启verification、fork_turns="none"独立checklist，再由Owner最终验收。当前到此停止PM写入，不启动后续角色；B/C或实质变更重新回PM/Owner。

本profile为contract_only；精确角色、主会话、完整bundle与diff审计仍是必要控制，不宣称平台ACL、强制路由或团队自动激活。

<a id="r1-original"></a>
## 16. r1完整历史（无损封存、非当前执行合同）

下方每行仅增加ASCII前缀`r1|`；移除前缀后必须得到原42739字节、SHA256=`e33aae41d18ba7faad19cb1ed563a19375996bc0f5d23ee7c646d62b2f7b0dc4`。包含原元数据/授权/allowlist/全部代码块/AC/历史，自身仍是未获实施批准的r1 draft；本r2当前条款优先，不能按封存文字开启r1或另建第二bundle。

仅文本校验的还原示例（不运行项目、不写文件）：

```python
from pathlib import Path
import hashlib
p = Path("field-flow/plans/FF-004-plc-json-catalog-and-multi-plc/spec.md")
b = p.read_bytes()
start = b"<!-- FF004_R1_ORIGINAL_BEGIN -->\n"
end = b"<!-- FF004_R1_ORIGINAL_END -->"
payload = b.split(start, 1)[1].split(end, 1)[0]
assert all(line.startswith(b"r1|") for line in payload.splitlines(keepends=True))
original = b"".join(line[3:] for line in payload.splitlines(keepends=True))
assert len(original) == 42739
assert hashlib.sha256(original).hexdigest() == "e33aae41d18ba7faad19cb1ed563a19375996bc0f5d23ee7c646d62b2f7b0dc4"
```

````text
<!-- FF004_R1_ORIGINAL_BEGIN -->
r1|Task ID: FF-004
r1|Revision: r1
r1|Status: draft
r1|Owner Role: PM
r1|Allowed Writers: PM, Human Owner
r1|Handoff: PM -> Human Owner exact FF-004 r1 scope approval pending; no Development or Verification handoff has occurred
r1|Workflow Mode: STD
r1|Execution Mode: agent_team_same_session
r1|Task Namespace: aiis-ics-arch
r1|Classification: root
r1|Capability: 每PLC独立JSON合同、Rust首切片的S7 int16目录加载与多PLC点位调用、Modbus结构校验及DS导出边界
r1|Owner: Field Flow
r1|Acceptance Chain Reference: FF-004 r1 exact scope approval -> Development -> fresh-context QA / Verification -> Human Owner final acceptance
r1|Related Task: FF-001 r4; FF-002 r1; FF-003 r1; ARCH-TOOL-001 r2; device-simulator::DS-002 r1
r1|
r1|# FF-004：每PLC一个JSON与多PLC调用 r1
r1|
r1|## 1. 当前授权与精确批准面
r1|
r1|2026-11-03（Asia/Shanghai），Human Owner要求：“可以，就按一台PLC一个JSON的方案，先把S7/Modbus配置格式、多PLC调用方式和DS导出关系整理进FF的实施spec，按STD先走PM，暂不改代码。”本轮只授权PM草案及必要导航；**本r1仍为draft，尚无精确实施批准**。本任务独立归[FF PLAN](../../PLAN.md)及[任务目录](../README.md)，无Parent Task ID，不继承其他任务的批准、实现、QA或验收。
r1|
r1|本规格给出可以直接批准的最小软件切片A。若Human Owner明确批准“FF-004 r1”，将批准下面A的全部有界交付及其合成验证，然后实际调用Development；无需为A内常规接线再立Revision。Modbus真实通信、Python/C#跟进及DS导出实现不在A内，须各自精确新Revision或独立任务。只认可方案方向、批准PM写spec或沉默均不构成该批准。
r1|
r1|| 层次 | 本r1定义的交付与效力 |
r1|| --- | --- |
r1|| P0：当前 | 只写本spec与§3的八份机械导航；不创建tasks/checklist、源码、schema或配置文件。 |
r1|| A：精确r1批准后 | 仅现有Rust工程：严格单PLC JSON加载、主YAML v2、稳定点位句柄、S7标准DB int16、一个新增公开只读`read_points` kind、demo01点位引用与旧YAML v1兼容；Modbus只做文件结构/类型约束校验；自身夹具、测试和双语说明。无新增依赖、无状态schema迁移。 |
r1|| B：独立协议gate | Modbus TCP实际client/owner、wire codec、事务关联、取消/晚到隔离和受控读写；须先另行冻结技术栈、精确版本/文件/协议及验收，A不授权实施。 |
r1|| C：独立owner/gate | Python同格式加载；FF-003之后的C#接入；DS导出；根contracts公开schema提升；均不附带批准。 |
r1|
r1|保留[ARCH-TOOL-001 r2](../ARCH-TOOL-001-field-flow-runner/spec.md)、[FF-001 r4](../FF-001-dual-runtime-demo01/spec.md)、[FF-002 r1](../FF-002-user-guide-and-runtime-positioning/spec.md)、[FF-003 r1](../FF-003-csharp-runtime-demo01/spec.md)及全部历史原字节。FF-001/002独立本地QA通过与Owner终验待定分开；FF-003仍是待批准、无源码的C#首轮草案，本任务不扩展、替代或假定它已成为底座。
r1|
r1|## 2. 已核现状与来源
r1|
r1|本轮按序消费根AGENTS、README/PLAN双语、[canonical workflow](../../../.codex/workflows/development-lifecycle-workflow.md)、[pm角色](../../../.codex/agents/pm.toml)，FF最近README/PLAN/catalog双语及相关任务当前有效段，Rust工程README/PLAN、配置/运行/状态源码，DS README/PLAN和完整[DS-002 r1](../../../automation-world/device-simulator/plans/DS-002-multi-protocol-simulation-and-device-debugging/spec.md)。本任务目录此前不存在，未发现同能力任务。以下是源码读取事实，不是本轮运行验证：
r1|
r1|| 来源 | 当前事实及对本任务的约束 |
r1|| --- | --- |
r1|| [Rust config](../../field-flow-rust/src/config.rs)、[Python config](../../field-flow-python/src/field_flow/config.py) | 主YAML schema_version=1，内嵌plcs与物理target；最多4 PLC/8 flow，host为IPv4字面量，host/port全局不重复；只支持S7标准DB两字节INT。没有JSON目录或Modbus adapter。 |
r1|| [Rust runtime](../../field-flow-rust/src/runtime.rs)、[demo01](../../field-flow-rust/src/app/demo01.rs) | 已有每PLC长期owner/driver子进程和有界串行IO、独立flow任务；没有全PLC ready屏障，但每流目前仅取得target.plc_id对应的一个owner。demo01是GET→严格输入→Execution。 |
r1|| [Rust domain](../../field-flow-rust/src/domain.rs)、[state](../../field-flow-rust/src/infrastructure/state.rs) | config_identity_hash包含完整旧Flow/Target和端点；物理Resource及unknown阻断已存在。直接hash新文件、导出时间或路径会错误改变命令语义。现有SQLite schema=1及旧UTC日历字段不能顺手重写。 |
r1|| [DS配置](../../../automation-world/device-simulator/runtime/src/domain/configuration.rs)、[来源](../../../automation-world/device-simulator/runtime/src/domain/source.rs)、[版本读取](../../../automation-world/device-simulator/runtime/src/infrastructure/config_store/queries.rs) | 有实例/DB/点UUID、监听端点、DB号/长度、byte/bit、技术名/显示名、来源tree/segments和不可变revision/payload SHA；当前模型是S7，无Modbus模型或FF导出。 |
r1|| DS-002 §9/R11 | source/devices[]是尚未批准、未占正式合同版本的候选。本任务将其进一步收敛为单PLC文件，作为FF提案交接，不声称DS已接受，不修改DS-002。 |
r1|
r1|协调者只读核对精确rust-snap7 1.142.2上游缓存源码：默认client calling/local TSAP为0x0100，PG connection type=1，ConnectTo的called/remote为0x0100+rack×32+slot；仓内driver没有覆写。它只支持默认值推断，不是实际COTP方向实测；A必须补显式C1/C2协议断言，不依赖本机缓存路径运行。
r1|
r1|Modbus四表、0-based PDU与功能码依据[官方V1.1b3 §4/§6](https://www.modbus.org/file/secure/modbusprotocolspecification.pdf)；Unit ID、MBAP与长期TCP连接依据[官方TCP实现指南V1.0b](https://www.modbus.org/file/secure/messagingimplementationguide.pdf)。资料由协调者本轮只读核验，不能替代本地协议证据。汇川“好像EVO800”尚无确切CPU/固件/点表/transport资料，本文只用合成地址，不生成任何汇川映射。
r1|
r1|## 3. 分阶段文件边界
r1|
r1|路径均相对仓库根。当前正式交付树为`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，存在并行dirty；不得覆盖、回退或清理他人修改。PM唯一写面是本spec。主协调在spec真实形成后只新增draft入口，不重写旧任务行。
r1|
r1|| 当前P0责任 | 精确allowlist |
r1|| --- | --- |
r1|| PM | `field-flow/plans/FF-004-plc-json-catalog-and-multi-plc/spec.md`及必要父目录。 |
r1|| 主协调：FF导航 | `field-flow/README.md`、`field-flow/README.zh-CN.md`、`field-flow/PLAN.md`、`field-flow/PLAN.zh-CN.md`、`field-flow/plans/README.md`、`field-flow/plans/README.zh-CN.md`。 |
r1|| 主协调：跨工程导航 | 根`PLAN.md`、`PLAN.zh-CN.md`，各加一行。根README、根plans catalog、CODE_INDEX本轮不改。 |
r1|
r1|**下表仅在精确r1批准后成为A的实现allowlist。** R表示`field-flow/field-flow-rust/`；花括号是有限列举，不是递归授权，未实际需要的文件不改。常规小文件拆分须仍在相同职责内，并先由PM明确加入allowlist；不借目录通配扩面。
r1|
r1|| A责任 | 有限文件集合与限制 |
r1|| --- | --- |
r1|| 既有接线 | `R/src/{config.rs,commands.rs,runtime.rs,lib.rs,domain.rs}`、`R/src/services/mod.rs`、`R/src/app/{mod.rs,demo01.rs}`；仅版本化配置、句柄注入、legacy规范化与read_points注册。不得改变旧Intent摘要算法、物理Resource、TTL/ACK/unknown安全语义。 |
r1|| 新小模块 | `R/src/config/{catalog.rs,runtime_v2.rs}`、`R/src/services/devices.rs`、`R/src/app/read_points.rs`；配置/纯校验、点位解析与实际IO分层，无插件/扫描/DSL。 |
r1|| 自有有限夹具/测试 | 既有`R/src/fixture.rs`、`R/tests/{support/mod.rs,cli_contract.rs,runtime_regressions.rs,local_protocol.rs}`；新增`R/src/fixture/catalog_demo.rs`、`R/tests/{plc_catalog.rs,multi_plc.rs,catalog_compatibility.rs,modbus_catalog.rs}`。保留旧expected/失败证据；坏配置用测试内存变体，不复制大量夹具文件。 |
r1|| 合成示例 | 新`R/config/catalog-demo.yaml`、`R/config/plcs/{s7-a.json,s7-b.json,modbus-example.json}`、`R/config/{README.md,README.zh-CN.md}`、`R/config/plcs/{README.md,README.zh-CN.md}`；示例内容由§5–8落实，原`config/loopback.yaml`字节保持。 |
r1|| 文案/自身说明 | `R/locales/{zh-CN.json,en-US.json}`、`R/{README.md,README.zh-CN.md,USER_GUIDE.md,USER_GUIDE.zh-CN.md,BUILD.md,BUILD.zh-CN.md,CODE_INDEX.md}`；Rust自身PLAN/catalog四件与P0八导航由协调者仅机械同步事实。 |
r1|| 角色文档/私有资源 | Development批准后创建本bundle的`tasks.md`；真实handoff后fresh Verification创建`checklist.md`，各自真实附件才建`evidence/`。获批执行者可创建独占`/private/tmp/ff-004-r1-<unique>/`作build/copy/合成状态/报告，列归属与保留条件。 |
r1|
r1|`Cargo.toml`/`Cargo.lock`、`src/driver_process.rs`、`src/infrastructure/{state.rs,audit.rs,s7_int_pdu.rs}`不属于A写面；保持现有依赖、状态schema、旧日历字段与协议安全实现。若证明这些必须改变才能满足A，停该部分、保留证据，PM新Revision后再实施。禁止写Python/C#、DS/AW/DAA/SMA/CA、Backend、tools、根contracts、shared skills、AGENTS/workflow/角色文件、其他bundle和真实配置/SQLite/.env。
r1|
r1|## 4. R01：格式、版本与严格加载
r1|
r1|Human Owner明确选择JSON作为每PLC可审阅配置；主运行配置继续YAML，SQLite只存各工程自己的执行事实。此选择覆盖skill的通常YAML偏好。三种语言可以各自实现同一语言中立格式，**不表示三工程当前都能加载**；配置副本、锁、状态与可写目录各自独立，不共享DS SQLite。跨运行时公开schema将来归根`contracts/`，本轮仅spec代码块，A也不在根contracts另造合同中心。
r1|
r1|| 对象 | 版本/精确规则 |
r1|| --- | --- |
r1|| 单PLC JSON | 顶层对象，`format="ff.plc"`、`schema_version=1`；它与主YAML的版本号及SQLite schema版本互相独立。 |
r1|| 主YAML | v1继续原读取合同；v2只允许`plc_files`，禁止同时出现内嵌`plcs`或原物理target。版本未知/缺失不猜测、不降级。 |
r1|| 新格式解析 | 以下严格规则只适用于JSON v1/主YAML v2：UTF-8、无BOM；拒重复key、未知字段、null冒充缺省、数字字符串/bool隐式转换及超范围值；integer须整数词法，拒1.0/1e0。YAML v2拒alias/merge/重复key。所有对象递归闭合；无自由extensions兜底。旧YAML v1保留当前解析及限制，不批量收紧其既有行为。 |
r1|| 容量 | 主文件≤64KiB；1..4 PLC文件，每件≤1MiB、总≤4MiB、嵌套≤16层；每PLC≤64 DB或≤4 table、总点≤4096；1..8 flow。先限量再分配/解析，超限整体失败。 |
r1|| 文件路径 | `plc_files`为1..4唯一相对路径，以主配置实际所在目录为基准；允许`plcs/s7-a.json`，拒绝空路径、绝对路径、`..`、反斜线、URL/glob、变量/`~`展开及symlink。改cwd不改变解析，文件名不决定协议或身份。 |
r1|| 加载原子性 | 只读显式列表，启动一次读取并冻结全部原字节/hash，完整解析/交叉校验/能力校验后才装配。任一坏文件/重复身份/不支持能力整体拒绝；无自动扫描、热加载、后台重读或部分启动。多个文件不是文件系统原子快照，部署时应停止编辑后重启，启动报告列实际读取的各hash。 |
r1|
r1|所有ID为ASCII`[A-Za-z0-9_-]{1,64}`，兼容DS UUID。下表标“可选”的字段缺省才可省略；显式null只在特意允许处合法。人类说明字符串按UTF-8字节计限长，不作为索引或驱动判断。
r1|
r1|## 5. R02：单PLC公共字段与S7合同
r1|
r1|| 字段 | 必填/类型/范围/语义 |
r1|| --- | --- |
r1|| `format/schema_version/id/protocol` | 必填；固定字符串/整数1/稳定设备ID/精确枚举`s7|modbus_tcp`。id与文件名、IP、显示名分离；重命名文件/改显示名不重建ID。 |
r1|| `name/display_name/description` | 可选非空字符串，分别≤128/256/1024字节；只作技术核对/显示/说明，不参与查点或效果身份。 |
r1|| `metadata` | 可选闭合对象，仅可含`brand/model/firmware`非空字符串各≤128字节；资料不选择协议、地址或字序。 |
r1|| `source` | 必填闭合分型；手写恰为`kind:"manual"`及可选`note`≤512字节；DS分型见§11。不允许原始源码、运行值、模拟规则、凭据或SQLite路径。 |
r1|| `connection` | 必填协议专属对象；host为规范IPv4字面量，禁止wildcard/0.0.0.0、广播/组播，port整数1..65535；无DNS/扫描。当前实际联网授权仅§13合成loopback端口。 |
r1|| `dbs` / `tables` | 按protocol恰有其中一项且非空；禁止把另一协议字段塞入或从文件名推断。 |
r1|| 点公共说明 | `name/display_name/source_name/source_path/source_native_type`可选非空字符串，分别≤128/256/256/1024/32字节；保留来源原名，不靠显示名或拆字符串伪造TIA原名。 |
r1|
r1|S7：`connection`必填host/port/rack整数0..7/slot整数0..31；可选`local_tsap/remote_tsap`为整数1..65535，省略分别表示0x0100、0x0100+rack×32+slot。结构校验保留声明；**A的run只接受与该默认能力完全相等的值**，其他值报`unsupported_connection`，不得忽略DS的calling TSAP或扩driver接口。
r1|
r1|`dbs[]`必填`number`整数1..65535、`size_bytes`整数2..65536、非空`points[]`，可选`enabled`为bool且缺省true。DB号在单PLC内唯一；点从父级继承DB号，点内禁止重复声明db_number。点必填`id`、`data_type:"int16"`、`byte_offset`整数0..65534，可选enabled同上；须offset+2≤size_bytes。单点是两个字节、有符号16位、大端补码，范围-32768..32767。声明大小不证明真实PLC布局或可写性。
r1|
r1|S7 JSON v1只接收int16；BOOL/REAL/DINT/STRING等是后续扩展，不能当前成功加载后忽略。将来BOOL合同必须显式bit0..7及邻位保持/位写gate，不能仅给byte_offset声称支持；本版禁止`bit`、scale和word_order。DS的INT明确归一化成int16，其他原生类型不靠改大小写假支持。
r1|
r1|完整合成文件`config/plcs/s7-a.json`（当前只是代码块）：
r1|
r1|```json
r1|{
r1|  "format": "ff.plc",
r1|  "schema_version": 1,
r1|  "id": "s7_a",
r1|  "display_name": "Synthetic S7 A",
r1|  "protocol": "s7",
r1|  "source": {"kind": "manual"},
r1|  "connection": {"host": "127.0.0.1", "port": 34102, "rack": 0, "slot": 1, "local_tsap": 256, "remote_tsap": 257},
r1|  "dbs": [
r1|    {"number": 1, "size_bytes": 16, "points": [{"id": "value", "data_type": "int16", "byte_offset": 0}, {"id": "ready", "data_type": "int16", "byte_offset": 2}]},
r1|    {"number": 2, "size_bytes": 16, "points": [{"id": "result", "data_type": "int16", "byte_offset": 0}]}
r1|  ]
r1|}
r1|```
r1|
r1|完整第二文件`config/plcs/s7-b.json`：
r1|
r1|```json
r1|{
r1|  "format": "ff.plc",
r1|  "schema_version": 1,
r1|  "id": "s7_b",
r1|  "protocol": "s7",
r1|  "source": {"kind": "manual"},
r1|  "connection": {"host": "127.0.0.1", "port": 34112, "rack": 0, "slot": 1},
r1|  "dbs": [{"number": 1, "size_bytes": 16, "points": [{"id": "value", "data_type": "int16", "byte_offset": 0}]}]
r1|}
r1|```
r1|
r1|## 6. R03：Modbus TCP文件合同与支持边界
r1|
r1|`connection`恰为host/port/`unit_id`整数1..255，禁止0/广播、rack/slot/TSAP/串口字段。`tables[]`每项必填`table`四类枚举及非空`points`，可选enabled同S7；table在单PLC内不重复，地址空间相互独立。点必填id、`pdu_address`整数0..65535、data_type、`functions`，可选enabled/公共说明及下表适用codec声明。地址统一0-based，不接40001等手册编号自动减基址。RTU后续另定transport/串口/帧时序，不能当TCP的配置别名。
r1|
r1|| table / data_type | 宽度与functions的严格组合 |
r1|| --- | --- |
r1|| `coils` / `bool` | 1 bit；functions恰为`{"read":1,"write":null}`或write=5。 |
r1|| `discrete_inputs` / `bool` | 1 bit；read=2、write必须null。 |
r1|| `holding_registers` / `int16|uint16` | 1个16-bit register；read=3，write为null或6。 |
r1|| `input_registers` / `int16|uint16` | 1 register；read=4，write必须null。 |
r1|| 上述两种register表 / `int32|uint32|float32` | 2个连续register；read分别3/4，write必须null；`word_order`必填`high_word_first|low_word_first`。 |
r1|
r1|functions.read/write键均必填，值为精确整数或允许的null；不匹配表/类型即拒绝。宽度由上表推导，禁止另写quantity/width造成歧义；末地址须满足pdu_address+宽度≤65536。同一register内wire字节为网络大端，多register字序不得按厂家猜；16位及bool禁止word_order。int/uint按精确位宽补码/无符号解释，float32为IEEE754且只接受有限值；不支持byte-swap、字符串、BCD、64位及FC15/16等扩展。
r1|
r1|register点可选`scale:{"factor":number,"offset":number}`，两键必填、有限值且绝对值≤1e9，factor≠0；省略等于factor1/offset0。工程值=解码原值×factor+offset；超出有限范围是解码错误，不截断/填0。bool禁止scale。将来写入须先逆变换、整数精确性/范围/编码核对，不能四舍五入盲写；A无此写实现。functions.write只描述所选协议操作，不授予FF写权限，DS策略和厂家“可写”资料也不授予权限。
r1|
r1|完整结构示例`config/plcs/modbus-example.json`：
r1|
r1|```json
r1|{
r1|  "format": "ff.plc",
r1|  "schema_version": 1,
r1|  "id": "modbus_station",
r1|  "protocol": "modbus_tcp",
r1|  "source": {"kind": "manual", "note": "Synthetic addresses only"},
r1|  "connection": {"host": "127.0.0.1", "port": 34502, "unit_id": 1},
r1|  "tables": [
r1|    {"table": "coils", "points": [{"id": "request", "data_type": "bool", "pdu_address": 0, "functions": {"read": 1, "write": 5}}]},
r1|    {"table": "discrete_inputs", "points": [{"id": "ready", "data_type": "bool", "pdu_address": 0, "functions": {"read": 2, "write": null}}]},
r1|    {"table": "holding_registers", "points": [{"id": "counter", "data_type": "int16", "pdu_address": 0, "functions": {"read": 3, "write": 6}}]},
r1|    {"table": "input_registers", "points": [{"id": "temperature", "data_type": "float32", "pdu_address": 10, "word_order": "high_word_first", "scale": {"factor": 0.1, "offset": 0}, "functions": {"read": 4, "write": null}}]}
r1|  ]
r1|}
r1|```
r1|
r1|**A的`config validate`可检查该完整结构、类型宽度/字序/scale声明，不能称协议可用。A没有Modbus连接、wire codec或读写。只要run的plc_files选中任何Modbus文件，即使没有flow引用或点被disabled，均须在State::open、状态恢复写、日志文件、owner/flow创建及任何连接之前整体报`unsupported_protocol`、exit2。** 不得过滤掉Modbus后启动S7。34502只作结构样例，不属于A允许连接/监听的端口。
r1|
r1|## 7. R04：身份、重名、物理重叠与共享链路
r1|
r1|1. 一个文件恰有一个逻辑PLC；重复device ID、重复规范路径，即使内容相同也失败。点ID在**单PLC全部DB/table内唯一**，包括disabled项；不能只在DB内去重或后写覆盖。同名显示/技术名可以存在，查找只认device_id+point_id。
r1|2. DB/table范围内typed点不得物理重叠，包括只读和disabled声明；S7按字节区间，Modbus按同table的bit/register区间核对。重复地址不通过新增point ID作别名；业务角色绑定只引用既有身份，不改物理点身份或地址。
r1|3. 规范IPv4+port在整组文件内唯一，跨协议也不允许重复。S7即使rack/slot不同也拒同endpoint；Modbus同TCP网关不同Unit ID首切片报`shared_transport_unsupported`，不能一文件盲建一会话。unit_id是逻辑寻址，host/port是链路，两者不得混为去重键。以后共享网关必须另定共享owner/串行队列和Unit路由gate。
r1|4. 启动另核写目标物理重叠，不能以device/point别名绕过。独立读取同一点仍是多次采样；连接复用没有去重、共同快照、跨PLC事务或跨库writer fencing保证。
r1|
r1|## 8. R05：主YAML v2与首切片两PLC示例
r1|
r1|v2必填schema_version=2、instance_id、plc_files、plc_runtime、flows、http、shutdown_timeout_ms；无其他顶层键。plc_runtime每个对象恰有device_id及以下五个预算字段，必须与所有文件ID一一对应，无重复/漏项/多项。预算沿FF-001：connect500..3000ms、IO500..5000ms、queue_capacity1..16、queue/ready_wait100..5000ms；interval100..10000ms，HTTP及shutdown范围/关系沿旧合同，不因分文件扩大。
r1|
r1|flow分型：共同必填id/kind/business_name/interval_ms/device_ids；device_ids是1..4唯一ID，明确注入依赖子集。demo01另必填source_id/get_url/input_max_age_ms/target，target恰为device_id/point_id且属于依赖子集、指向enabled的S7 int16。`read_points`另必填reads（1..16唯一device_id/point_id引用），所有引用属于依赖子集并enabled；禁止demo01专属字段，不持久化command、不写PLC。缺点/禁用点/未知kind/无效URL均在启动前拒绝。
r1|
r1|完整`config/catalog-demo.yaml`，与§5两文件合起来是A应交付可运行样例，覆盖单PLC多DB、单DB多点及一流多PLC：
r1|
r1|```yaml
r1|schema_version: 2
r1|instance_id: ff-rust-catalog-demo
r1|plc_files: [plcs/s7-a.json, plcs/s7-b.json]
r1|plc_runtime:
r1|  - {device_id: s7_a, connect_timeout_ms: 3000, io_timeout_ms: 5000, queue_capacity: 16, queue_wait_ms: 2000, ready_wait_ms: 3000}
r1|  - {device_id: s7_b, connect_timeout_ms: 3000, io_timeout_ms: 5000, queue_capacity: 16, queue_wait_ms: 2000, ready_wait_ms: 3000}
r1|flows:
r1|  - id: read_pair
r1|    kind: read_points
r1|    business_name: synthetic_pair_samples
r1|    interval_ms: 200
r1|    device_ids: [s7_a, s7_b]
r1|    reads: [{device_id: s7_a, point_id: value}, {device_id: s7_a, point_id: ready}, {device_id: s7_a, point_id: result}, {device_id: s7_b, point_id: value}]
r1|  - id: demo01
r1|    kind: demo01
r1|    business_name: synthetic_command_to_int
r1|    interval_ms: 500
r1|    device_ids: [s7_a]
r1|    source_id: demo01-feed
r1|    get_url: http://127.0.0.1:34880/demo01/command
r1|    input_max_age_ms: 10000
r1|    target: {device_id: s7_a, point_id: value}
r1|http: {connect_timeout_ms: 500, total_timeout_ms: 1500, pool_wait_ms: 500, max_connections: 8, max_body_bytes: 4096}
r1|shutdown_timeout_ms: 15000
r1|```
r1|
r1|新CLI只有`config validate --config <main.yaml>`或互斥`config validate --plc-file <one.json>`：只读、不联网/建库/写日志，输出单个JSON结果含scope、format_valid、runtime_compatible、所读文件hash及结构/能力问题；exit0表示结构有效，**runtime_compatible=false不表示可run**；坏结构exit2。单文件校验不能证明整组端点/依赖/写冲突有效。run沿用显式--config/--state-dir、默认dry_run、显式--execute，但必须经过完整结构及runtime能力preflight后才打开原状态库。
r1|
r1|## 9. R06：点位句柄、调度、期限与停止
r1|
r1|目标应用接口为`devices[device_id].read(point_id)`；Rust可表达为`ctx.devices["s7_a"].read("value").await?`，flow_id由注入上下文绑定，不能由app伪造。注入只包含device_ids子集；app不拿全局owner map/raw client/SQL，不写DB号、功能码或protocol分支。写继续经已有Execution服务，新增read句柄不暴露原始write快捷口。
r1|
r1|完整混合协议调用概念如下；这是B以后接口目标，**A不能运行含Modbus的这段**。没有额外虚构is_good/时效API，读取失败通过Result终止本轮：
r1|
r1|```rust
r1|async fn once(ctx: &FlowContext) -> Result<()> {
r1|    let first = ctx.devices["s7_a"].read("value").await?;
r1|    if first.value != PointValue::Int16(42) {
r1|        return Ok(());
r1|    }
r1|    let _next = ctx.devices["modbus_station"].read("counter").await?;
r1|    Ok(())
r1|}
r1|```
r1|
r1|A实际read_points每轮按reads列表顺序await，首个失败结束本轮并记录该失败；没有完成的后续项为not_attempted，不回填上一轮。成功Sample必须带device_id/point_id、flow/request、session generation、typed int16、quality=good及本机响应完成观测`received_at(+08:00)`；它不是设备事件发生时刻。失败是明确error，不返回0/false/旧值冒充本次成功。每flow只保留最近一轮≤16项，8flow总≤128项，普通成功不逐点持久刷日志，沿5秒health汇总。
r1|
r1|各flow独立并发；同flow一轮完成后等待interval，重叠≤1，无积压补跑。`return`只结束本轮，不用“done自动停流”假语义。每PLC复用现有长期owner/driver与有界FIFO，最多1次真实IO；多PLC独立推进。HTTP/timer不占PLC队列位；完整文件校验是启动前静态gate，**不增加所有PLC ready的全局屏障**。连接就绪只阻塞调用该设备的操作；同一顺序读流等待B时，该流尚未完成，但其他只依赖A的流继续。
r1|
r1|沿用FF-001 r4的ready/queue/dispatch IO分别计时、原来源TTL/ClockAnchor复核、进程回收预算、stop闸门与unknown，不复制另一套重试器。新句柄只能委托原owner；不得新增队列、每请求连接/线程或旁路IO。停机先同时封全部owner接纳/dispatch，取消未发项，剩余工作共用原15秒默认全局预算，真实join/reap后才报释放；forced cleanup仍为故障/非零，不把中止等同PLC回滚。
r1|
r1|## 10. R07：旧YAML、效果身份、状态与回退
r1|
r1|v1加载、原loopback样例、原Flow/Target序列化及Intent摘要算法保持。v2 demo01先解析点引用，**规范化成旧的全部Flow/Target字段**：id/kind/business_name/interval/source_id/get_url/input_max_age、target.plc_id/DB号/声明大小/offset/type=INT，以及旧Plc端点/rack/slot。仅这些逐项等价时，调用原摘要算法得到原config_identity_hash；新file/source/point/display字段不直接参与摘要。
r1|
r1|JSON原字节hash及source原payload SHA用于来源/审计，不能代替效果hash；改路径、字段顺序、导出时间、显示名不产生新command或重复写。改真正DB/offset/type/语义旧字段必须改变效果摘要/物理资源并触发既有身份冲突，不保留旧hash假装相同。旧business_name/plc_id等已在旧摘要内，不能悄悄把它们变成可随意改的显示字段。相同point ID地址变化不是无风险更新。
r1|
r1|手写ID换成DS UUID可能改变旧plc_id；应明确保留稳定ID并核对，而非宣称自动无缝继承。A不提供手写ID→DS UUID的别名/状态迁移工具；无法保留原ID时，另定人工核对与writer交接，不在本合同塞隐式映射。不能无歧义规范化则拒绝/identity_conflict，保留原意图并暂停相关写。point ID变化不允许借此新造command ID或消除unknown。启动恢复及新派发继续按原库全部unknown的物理endpoint/rack-slot/DB/字节重叠阻写；读回/换配置/重连/重启不升级unknown。
r1|
r1|本A不改DDL、store_meta schema=1、时间字段/旧记录/immutability trigger，不做状态转换工具、自动迁移、跨语言导入或清库。新观测字段按+08，Unix/monotonic按原语义；既有状态UTC与日志基线是已识别的历史范围，原producer本次不触达，不将其写成已完成时间整改。若实现必须触达其生产/存储链路，先回PM明确时间及schema维护范围，不混存或批量加八小时。
r1|
r1|run仍要求已初始化、implementation=rust、mode/instance匹配的原库；默认dry-run仅simulated/零写，execute使用独立匹配库。回退时先停writer、核pending/in_flight/unknown/confirmed，保存新配置及原库/日志，再用旧二进制+原v1配置；v1/v2物理目标及语义不一致时不能自动切换。不得删库/清进度/反向写PLC来“回退”。独立工程副本不构成共享资源的执行授权，Rust/Python/C#切换仍需唯一有效writer交接。
r1|
r1|## 11. R08：DS来源映射与导出关系
r1|
r1|以下只定义FF接受文件所需事实，交接DS owner；不授权DS源码/UI/SQLite写入。FF可先手写且不需要DS在线。DS-002导出阶段仍须独立批准；根contracts公开schema也须另批，不能用本spec要求另一个会话自动执行。
r1|
r1|| DS现有来源 | FF字段/明确处理 |
r1|| --- | --- |
r1|| InstanceConfig.id/name | 保留UUID为id、name/display_name为核对资料；与既有FF手写ID不同须按§10核对，不自动换身份。 |
r1|| host/port/rack/slot/calling_tsap/called_tsap() | host/port原为server bind，导出必须明确确认FF可达connect host/port；calling→client local，called→client remote，方向经SDK/真实COTP核对。wildcard不可直接导出；A拒绝不可表达TSAP。 |
r1|| DbConfig.number/length/enabled、PointConfig.id/name/display_name/byte/bit/enabled | 映射dbs.number/size_bytes/enabled、point id/说明/byte_offset/enabled；仅INT→int16。缺地址/布局/命名确认或不支持类型先列全问题，不生成执行假地址或静默丢点。 |
r1|| 绑定tree、segments/source_path、source_versions | 原source_name/path/native_type有事实才带；由结构化来源读取，不从display_name/拼接字符串猜。手工点没有TIA原名可省略。 |
r1|| configuration_revisions revision_id/saved_seq/原payload sha256 | 必须选择真实不可变saved revision，source绑定其原始身份/指纹；Workspace.schema_version不是FF文件版本。草稿、latest saved、selected与actual_loaded分别记录，不能互相冒充。 |
r1|| initial/rule/client_write/ui_maintenance、在线值 | 不进入FF执行合同，不转成FF写权限；没有Modbus现有模型可真实导出。 |
r1|
r1|DS来源分型`source.kind="device_simulator"`须恰有：`export_mode:"saved_revision"`、`instance_id`（等于设备id）、`revision`、`exporter_version`（非空≤64字节）、`generated_at`（真实RFC3339 +08:00）。revision恰有id（UUID）、saved_seq（整数1..9007199254740991）、payload_sha256（64位小写hex原payload SHA）。可选`runtime_observation`恰有observed_at（真实+08时间）、selected_revision、loaded_revision；后二者为同形revision或null，null明确表示没有该事实。缺事实省略整个观测，不用latest填loaded。
r1|
r1|首导出模式只接受一个明确saved revision的该实例切片，不混未保存draft/运行值；观测loaded不同可明确提示，文件并不证明模拟器已加载/启动。导出来源内部的DB/点/来源版本关联须由DS验证；FF只能校验声明/格式与文件hash，不证明DS库或真实PLC事实。未来“按actual_loaded导出”允许逐实例不同版本但需单独mode/gate，本v1禁止。DS完整问题列表、失败无半文件、显式可达端点确认及来源原SHA测试归DS阶段；本轮不编造DS导出成功样本/hash或替其批准。
r1|
r1|## 12. R09：工具链、依赖及分层handoff
r1|
r1|PM使用`aiis`、`project-governance`、`plc-point-mapping`。A的Development/Verification继续用这些，并加载`rust-runtime`（owner/配置/资源）、`i18n-workflow`（CLI对称文案）、`code-document-indexer`（关键源码头/自身结构）；本地状态如需实质改动须先PM新Revision并按需`backend-arch`。不加载Tauri/Web/Celery模板，不替Development执行技术工作。
r1|
r1|A沿现有Cargo工程、edition2021、rust-version1.89、现有锁与native S7链；Development记录真实rustc/cargo/clang/OS/CPU，首验macOS arm64，缺工具报blocker，不安装全局依赖或改shell profile。无新crate、无Modbus包、无更换S7/native源码；现有serde/serde_json/serde_yaml/sha2/chrono足以承担严格DTO/摘要/观测时间。Cargo manifest读时SHA256=`d28d9068b6804afe0f2605bdc5d90976a45e2e055881c771e26e7203291e8ea8`，lock=`13404c36665fa46f50f40291e111bcb11e99b9ee8c13d29130004c9ef3d74fc6`，要求交付不变。获批后可按锁准备缺失公共构建缓存，不解析新锁；配置验证使用项目Rust，不把Agent helper环境当项目验证。
r1|
r1|旧config对象/Intent/Resource保留为兼容边界，新目录DTO与版本装配分小模块，入口只解析/装配，read_points只写一轮；不用复制多语言底座、通用驱动注册平台或单文件大模块。新CLI与source/schema错误用稳定key和中英对称locale，用户自填设备名称不翻译。Development在tasks列需求→任务/命令/实际文件/结果/限制/资源，handoff给fresh-context Verification；PM只定规格，不作DEV完成或QA结论。
r1|
r1|## 13. R10：获批后的命令与合成验证
r1|
r1|以下均为**拟执行**，当前全部not_run。从Rust工程根运行，下列命令建立FF_PROJECT绝对路径和全新独占FF_RUN_ROOT；输出/新合成状态只在该根，不能使用已有用户profile/库。每条命令独立记录cwd/退出码/输出，不用辅助解释器冒充项目测试。
r1|
r1|```bash
r1|FF_PROJECT=$(pwd -P)
r1|FF_RUN_ROOT=$(mktemp -d /private/tmp/ff-004-r1-XXXXXX)
r1|printf '%s\n' "$FF_PROJECT" "$FF_RUN_ROOT"
r1|cargo fmt -- --check
r1|cargo build --locked --no-default-features --bin field-flow --target-dir "$FF_RUN_ROOT/product"
r1|cargo build --locked --features test-fixture --bin ff-fixture --target-dir "$FF_RUN_ROOT/fixture"
r1|cargo test --locked --features test-fixture --target-dir "$FF_RUN_ROOT/test" -- --test-threads=1
r1|"$FF_RUN_ROOT/product/debug/field-flow" config validate --config "$FF_PROJECT/config/catalog-demo.yaml"
r1|"$FF_RUN_ROOT/product/debug/field-flow" config validate --plc-file "$FF_PROJECT/config/plcs/modbus-example.json"
r1|"$FF_RUN_ROOT/product/debug/field-flow" state init --synthetic --mode dry_run --state-dir "$FF_RUN_ROOT/dry-state" --instance-id ff-rust-catalog-demo
r1|"$FF_RUN_ROOT/product/debug/field-flow" state init --synthetic --mode execute --state-dir "$FF_RUN_ROOT/execute-state" --instance-id ff-rust-catalog-demo
r1|```
r1|
r1|增加test-fixture二进制的有界`--catalog-demo --evidence-dir <new-path>`模式，只启动两台固定S7合成服务：A proxy/server=127.0.0.1:34102/34103，B=34112/34113；HTTP=127.0.0.1:34880。A注册DB1/DB2各16字节，DB1的value@0=12、ready@2=1，DB2的result@0=56；B注册DB1/16字节，value@0=34；除上述完整INT区间外均为A5。read_points顺序读A.value/A.ready/A.result/B.value，demo01只写A.value42，ready/result/B及其余A5字节必须保持。HTTP沿既有七键严格合同给固定source=demo01-feed、value42、单次生成的command_id/issued/expires，不刷新重复身份。新模式输出fixture_ready后才run；不是任意点表/DS模拟器，无34502/RTU监听。既有fixture模式/端口继续用于原回归。
r1|
r1|```bash
r1|"$FF_RUN_ROOT/fixture/debug/ff-fixture" --catalog-demo --evidence-dir "$FF_RUN_ROOT/dry-fixture"
r1|"$FF_RUN_ROOT/product/debug/field-flow" run --config "$FF_PROJECT/config/catalog-demo.yaml" --state-dir "$FF_RUN_ROOT/dry-state"
r1|"$FF_RUN_ROOT/product/debug/field-flow" state inspect --state-dir "$FF_RUN_ROOT/dry-state"
r1|```
r1|
r1|fixture与run分终端或由自有harness编排；分终端时须把上方实际输出的FF_PROJECT/FF_RUN_ROOT绝对路径分别带入各自shell，不假设变量共享。先完成build/init再开fixture，避免10秒input age已过。execute使用另一个新夹具场景及原execute-state，run显式加--execute。Ctrl-C/TERM后实际wait/reap本任务确切PID、核五端口可重新绑定，正常退出0与forced故障分开。端口冲突停下报告，不杀占用者、不自动换端口。配置样例与fixture须在正式工作树可运行，不能仅临时副本有效。
r1|
r1|必须另验：空cwd help零副作用；从不同cwd用同一绝对主配置解析相同文件；单工程独立copy仅含自身source/manifest/lock/config/locales/tests/docs，无父/兄弟/DS服务，独立target及state重建必要检查。原FF-001 Rust测试和已修队列/调用前时钟/真实started检查全部保留通过；不重复Python验收或声称新QA覆盖旧历史。
r1|
r1|## 14. 验收矩阵
r1|
r1|P0仅做静态文档自检，不创建QA文件；下列是精确r1批准后A必须交付并由fresh Verification核验的AC。必要真实协议/状态场景不能只靠mock或schema pass。B/C的协议能力不在本矩阵冒充已验收。
r1|
r1|| AC | 可观察通过标准 |
r1|| --- | --- |
r1|| AC01 / R01 | 正式Rust树与独立副本locked build/test成立，manifest/lock不变；v1原样例及已有Rust安全回归通过；无其他工程源码/环境/fixture依赖。 |
r1|| AC02 / R01–03 | 三个JSON v1样例及主YAML v2可解析；新格式版本、重复/未知key、整数词法、null、越界/超限/深度、协议字段互斥、bool类型、word_order/scale/functions不匹配均整体拒绝；S7非int16拒绝。旧YAML v1按原解析/限制回归，不因新格式规则收紧。 |
r1|| AC03 / R01/R04 | 缺文件、重复路径/设备/跨DB点ID、越界/物理重叠、未引用坏文件、disabled坏结构、相同endpoint/多Unit ID、symlink/路径穿越均启动前拒绝；改cwd/文件名不误绑身份。 |
r1|| AC04 / R03/R05 | Modbus单文件结构校验明确format_valid=true/runtime_compatible=false；包含Modbus的完整run（含未引用/disabled）exit2 unsupported_protocol，零owner/flow/网络/状态恢复写/日志文件，原库字节保持；不支持TSAP同样启动前拒绝。 |
r1|| AC05 / R02/R06 | 真实S7 loopback一流按点ID依次读A.DB1.value12、A.DB1.ready1、A.DB2.result56、B.DB1.value34；execute后仅A.value变42，ready/result/B及其余A5字节保持。独立wire断言C1=0100/C2=0101，INT五边值/邻接A5保持，不借库调用成功推断协议正确。 |
r1|| AC06 / R05/R06 | 新public read_points一流引用两PLC，只有依赖子集可见；缺点/disabled/越权引用/错target启动前失败。sample身份/typed值/本机观测时间明确，失败/未读项不补旧值；最近轮次容量≤128。 |
r1|| AC07 / R06 | 同PLC≥3独立读流各≥20请求，稳定窗口只有1 session/driver、真实IO并发≤1，FIFO有界；两PLC独立并发且慢HTTP不占PLC位，同flow迭代不重叠/补跑。 |
r1|| AC08 / R06 | B缺席/慢connect时，仅依赖A的100ms读流在8秒内≥20成功且相邻成功≤500ms；顺序读流可等B而不冻结A独立流；没有全PLC ready屏障或隐藏全局锁。 |
r1|| AC09 / R06 | 原ready/queue/IO期限含真实底层结束，队列满/超时/停机未发项零下发；默认15秒全局stop内自有flow/owner/child/fixture退出并真join/reap/端口rebind；forced或未释放不报正常成功。 |
r1|| AC10 / R07 | v1与逐项等价v2产生相同旧typed摘要/物理Resource；改文件名/顺序/导出时间/显示名无新写；改真实地址/旧语义字段冲突并保原意图。手写→DS UUID不被无条件视为兼容。 |
r1|| AC11 / R07 | 合成原v1 confirmed在v2重复≥10轮/原库重启零再写；原in_flight恢复unknown，换point/flow/source/新command仍按物理重叠阻写，不相关读继续；原schema/trigger/历史行不重写，无DDL/时间迁移/清进度。 |
r1|| AC12 / R05/R07 | demo01默认dry_run为simulated/WriteVar0；显式execute对A仅一次匹配ACK+持久确认，B零写；TTL/身份/unknown与旧Execution一致，无新增write旁路或“读回即确认”。 |
r1|| AC13 / R08/R09 | DS映射/缺口、saved/selected/loaded、可达地址与TSAP方向、纯来源hash不进效果hash、DS权限不外推均在双语说明明确；CLI帮助/错误对称、validate不碰库/网络，未宣称DS已导出或三语言已实现。 |
r1|| AC14 / 全文 | tasks列精确candidate/逐AC真实命令/失败/资源，fresh-context Verification独立checklist/verdict；保护旧bundle、Python/C#、DS及任务外dirty；QA通过只进入Owner终验，现场/平台/托管/长稳/发布另gate。 |
r1|
r1|B的进入条件须在其新spec明确：候选client精确版本/锁、四表FC子集、寄存器codec golden、每请求transaction ID+Unit/function/长度关联、超时废弃旧连接与迟到隔离、有界owner/关闭及unknown/no-replay、共享网关策略、独立协议oracle。不能由A结构校验通过跳过这些gate；不在A临时手写一套Modbus栈取绿。
r1|
r1|## 15. 风险、排除项与批准记录
r1|
r1|| 风险 | 控制与回退 |
r1|| --- | --- |
r1|| 新文件与老执行身份不等价导致重复效果 | 先规范化并沿旧摘要/Resource；真实语义变化报冲突，保留原库/unknown，不生成新command或清进度。 |
r1|| Modbus“配置有效”被当作协议已可用 | validate分format/runtime能力；run preflight整体拒绝，不部分启动。B另行冻结技术与协议证据。 |
r1|| 同网关/别名产生多owner并发 | 全组host/port唯一、多Unit ID明确拒绝；未来共享链路单独设计，不盲以文件数建会话。 |
r1|| DS导出丢来源/TSAP/可达地址或混draft/loaded | 源字段逐项映射、选真实不可变版本、不可表达值拒绝，FF不读取DS库、不借模拟策略授权写。 |
r1|| 脏工作树/副本/资源造成误交付 | 精确allowlist、保护哈希、整合到正式源码树并核独立副本；证据先持久化，Owner终验后协调者核占用/依赖再收自有临时资源。 |
r1|
r1|明确排除：Modbus实际连接/写、RTU、EVO800或其他厂家实机映射、S7其他类型、demo02/POST可靠交付/事件触发DSL、DS客户端GUI或导出实现、三语言同步实现、自动发现/扫描/热更新、缓存共读/快照/跨PLC事务、全局writer fencing/接管、旧状态schema/历史时间迁移、Windows/Linux现场适配与长稳、安装器/服务/发布/部署、真实PLC/API/数据库操作、Git/GitHub动作。本任务只用自身合成loopback资源，不安装依赖或启动任何项目程序于当前P0。
r1|
r1|当前文档静态自检由PM/协调完成，具体命令/结果在handoff报告；它不是DEV自检或独立QA。协调者已报告全仓governance checker基线exit1，包含旧bundle重复历史元数据/既有catalog正则不匹配；本轮不改旧行迎合checker，不宣称全仓通过。对FF-004单独核元数据、JSON代码块、链接、围栏、allowlist及保护哈希。
r1|
r1|| 日期 | Revision / 真实决定 | 下一gate |
r1|| --- | --- | --- |
r1|| 2026-11-03（Asia/Shanghai） | 实际命名PM形成FF-004 r1 draft；Human Owner仅授权PM阶段，未批准本新r1实施 | 主协调提交精确路径/SHA256与A范围供Owner审阅；待明确批准后才实际调用Development。 |
r1|
r1|**PM -> Human Owner批准点：** FF-004 r1的单PLC JSON v1、主YAML v2、Rust S7 int16首切片及新增public read_points、旧状态身份兼容、严格Modbus只校验/运行拒绝、§3精确文件/无新依赖边界和AC01–AC14。若批准，进入A的Development→fresh-context Verification→Owner终验；B/C及任何实质范围/allowlist/验收/风险变更重新回PM。当前不创建tasks/checklist，不进行代码/配置/schema/构建/协议/真实设备/API工作。角色profile是contract_only，主会话、bundle及diff审计仍必要，不宣称平台ACL、强制路由或团队自动激活。
<!-- FF004_R1_ORIGINAL_END -->
````
