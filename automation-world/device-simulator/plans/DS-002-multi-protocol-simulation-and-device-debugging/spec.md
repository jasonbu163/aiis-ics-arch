Task ID: DS-002
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM design draft -> Human Owner review of exact DS-002 r1; no Development or Verification handoff, implementation permission or acceptance is inferred
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: device-simulator
Classification: root
Capability: 同一DS产品的S7/Modbus TCP设备模拟与隔离设备读写调试设计、分阶段实施边界及DS点位文件可导出性反馈
Owner: Device Simulator
Acceptance Chain Reference: DS-002 r1 PM design -> Human Owner exact design approval; any implementation requires a separately approved precise phase/revision -> Development -> fresh-context Verification -> Human Owner final acceptance
Related Task: device-simulator::DS-001 r1; aiis-ics-arch::ARCH-AW-004 r2; aiis-ics-arch::ARCH-AW-005 r5; aiis-ics-arch::DAA-007 r2

# DS多协议设备模拟与设备读写调试设计 r1

## 1. 当前效力、唯一归属与可审阅交付

2026-11-02（Asia/Shanghai），Human Owner要求在独立DS会话研究“增加Modbus、配置中心区分协议、连接S7/Modbus设备进行手工单点及范围读写调试”，本轮**只形成设计/spec及必要双语导航，不进入源码实施**。本文件是新能力的唯一范围入口，归[DS PLAN](../../PLAN.md)及[任务目录](../README.md)管理；没有Parent Task ID，不继承旧任务批准、QA、例外或验收。

**当前为`draft / r1`，等待Human Owner审阅精确设计。** 本轮不创建`tasks.md`或`checklist.md`。对r1的设计批准只固定本文的产品边界、建议和分期，不授权任何代码、依赖安装、迁移实验、协议监听、调试连接或真实设备写入。以后选择具体实施阶段时，PM须将其精确文件、依赖版本、实验资源、验收和风险固化为新的获批Revision/独立实施范围，再由实际Development创建tasks；真实developer_handoff后才启动fresh-context Verification并创建checklist。

当前仓库写面恰为下列五文件。PM只写第一件，主协调仅在后三类既有导航表中新增DS-002行，其余字节及并行修改保留：

| 本轮精确路径（仓根相对） | 责任与内容 |
| --- | --- |
| `automation-world/device-simulator/plans/DS-002-multi-protocol-simulation-and-device-debugging/spec.md` | 实际PM；本r1设计草案。 |
| `automation-world/device-simulator/PLAN.md` | 主协调；draft、spec入口与下一gate。 |
| `automation-world/device-simulator/PLAN.zh-CN.md` | 同一任务的中文对应。 |
| `automation-world/device-simulator/plans/README.md` | 主协调；只链接已存在的spec，诚实标记后续文档未创建。 |
| `automation-world/device-simulator/plans/README.zh-CN.md` | 同一目录行的中文对应。 |

DS本地目录目前仅有DS-001，没有同题或DS-002现有bundle；根ARCH-AW-004/005中的Modbus是当时明确延期项，不是可复用的Modbus实施授权。本轮不改根/AW索引、旧bundle、长期详细设计正文、FF、DAA、CA、SMA、Backend、共享core、应用配置、真实.env/profile/SQLite、源码、测试、依赖或锁。当前正式交付树为`/Users/jason/Desktop/DreamCode/aiis-ics-arch`，读时HEAD=`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，已有大量dirty并行修改；HEAD不代表本次读取源码全部已提交，不reset、不切换/新建工作树、不清他人资源。

## 2. 已核现状与历史效力

以下是2026-11-02的源码/记录读取事实。源路径均在本仓；行号只定位本次读时快照，后续实施重新冻结实际输入。

| 表面与定位 | 当前事实、复用与改造风险 |
| --- | --- |
| [配置值对象](../../runtime/src/domain/configuration.rs)，PointConfig约136、DbConfig179、InstanceConfig201、Workspace231、validate248行 | `Workspace.schema_version=1`；InstanceConfig有host/port/rack/slot/calling_tsap/dbs，DbConfig有DB号/字节长度，点有byte/bit和TIA来源。serde拒未知字段，校验仅接收S7/loopback模型。不存在Modbus四表、寄存器地址或协议分型。只加下拉框不足以实现多协议。 |
| [layout](../../runtime/src/domain/layout.rs)、[image](../../runtime/src/domain/image.rs)、[request](../../runtime/src/domain/request.rs)、[owner](../../runtime/src/services/owner.rs) | 编译、coverage、image和请求均按S7 DB/byte/bit工作；Request载荷固定256B。现有唯一写owner、权限、CAS、规则/控制可借鉴，不能把Modbus表塞入DB map或沿用S7 STRING编码。 |
| [配置解码](../../runtime/src/infrastructure/config_store/queries.rs)5–11行、[schema检查](../../runtime/src/infrastructure/config_store/schema.rs) | payload先验原字节SHA再按Workspace解码；库appID/user_version、migration SHA及sqlite_master SQL均严格核对。新增payload分型、SQL表变动和旧版兼容是不同问题，不能靠删除字段/忽略校验处理。 |
| [configuration](../../runtime/src/services/configuration.rs)、[apply](../../runtime/src/services/apply.rs)、[versions](../../runtime/src/services/versions.rs) | 来源只读、布局/初值/策略确认、草稿CAS、不可变版本、selected/实际loaded、停机加载及引用保护已有完整业务。改造必须覆盖所有读写和版本路径，保留同版加载不重置、回退引用及预览保护。 |
| [native构建](../../native/CMakeLists.txt)、[Rust FFI](../../runtime/src/infrastructure/native_ffi.rs)、[bridge](../../native/bridge/ds_s7_bridge.h) | 当前CMake已编译上游client/micro-client源码，但产品Rust FFI/bridge仅有模拟server的create/start/stop/close/destroy等入口；没有产品调试client facade及其任务生命周期。构建硬限制macOS arm64，不能称已有三平台客户端。 |
| [前端facade](../../src/services/deviceSimulator.ts)、[宿主状态](../../src/console/composables/useDeviceSimulator.ts)、[导航](../../src/console/sections.ts)、[桌面入口](../../src-tauri/src/lib.rs) | 六页面为本地模拟业务；dirty草稿与runtime快照分开。没有远端调试会话；现有`ds_write_point`写本地模拟image，不能用于远端PLC写入。 |
| [source DTO](../../runtime/src/domain/source.rs)、[命名服务](../../runtime/src/services/naming.rs) | 稳定point UUID、技术name、display_name、结构化segments/source_path、DB绑定与不可变source_versions可导出。原始名称来自绑定tree/结构化段，不应靠拆字符串猜；手工点可没有TIA来源。Modbus对应模型尚不存在。 |

历史只链接原件，不复制完整多轮规格或重开旧任务：

- [ARCH-AW-004 r2](../../../../plans/ARCH-AW-004-ds-detailed-design/spec.md)及其[tasks](../../../../plans/ARCH-AW-004-ds-detailed-design/tasks.md)、[checklist](../../../../plans/ARCH-AW-004-ds-detailed-design/checklist.md#owner-acceptance-r2)：2026-10-18接受的是S7设计，Modbus/响应模拟延期；设计数字不自动成为实测能力。
- [ARCH-AW-005 r5](../../../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md)及其[tasks](../../../../plans/ARCH-AW-005-ds-g0-prototype-validation/tasks.md)、[QA4及Owner接受](../../../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5)：2026-10-27接受有限S7产品/既有G0退役。原306a09d5候选、34核心测试、16会话/第17条拒绝及macOS原生矩阵保持原证据边界；r4不完整、QA1–3失败、F-r5-001/002/003及后续关闭事实全部留原处。不能把后来代码重标成原QA4。
- [DS-001 r1](../DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001)及其[tasks](../DS-001-policy-table-and-usability/tasks.md)：2026-10-27接受当前DS，独立QA豁免只对DS-001有效；没有checklist是旧任务明确例外，本任务仍按STD独立核验。
- [DAA-007 r2 spec](../../../data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/spec.md)、[tasks](../../../data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/tasks.md)、[Owner接受](../../../data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2)：2026-10-30接受受控DS S7→SQLite联调及阶段B的该有限范围；8590样本/4295轮完整重开比较保留。早期checkpoint缺失、15:27来源未明事件仍跟踪，阶段C/自动启动/真实现场未启动。它不代验新DS版本/Modbus/调试客户端。
- DS [当前README](../../README.zh-CN.md)的2026-10-29 DIRECT草稿/版本管理增量仍标为DEV自检交付、待Owner按手册确认。新设计以当前源码评估兼容性，不将该增量倒记为旧接受或本轮QA。

PM读取当前有效Revision、批准/失败/交接/收尾段及源码，历史重复引文按原件定位去重；不重新核算旧持久原始协议证据，不声称本轮复验旧产品。

## 3. R01：同一产品、协议维度与两种运行角色

推荐继续同一个DS应用，协议为`s7`、`modbus_tcp`；品牌/型号/固件是可选资料，不能参与选择驱动或推导地址。“西门子版/汇川版”会复制草稿/版本/生命周期/UI维护，不采用。RTU需串口参数、设备/端口占用和不同帧/时序合同，列后续，不在TCP方案中隐含支持。

汇川目标目前只有“好像是EVO800”。CPU、固件、通信模块、Modbus Server启用方式、Unit ID、端口、寄存器映射和点表均未核实；不套EVO700/H5U/AM600地址，不宣称EVO800兼容。没有这些资料仍可完成通用协议设计和合成验证；真实目标适配另批。

| 维度 | 设备模拟：本地模拟服务 | 设备读写调试：连接远端设备 |
| --- | --- | --- |
| 目标/配置 | 持久模拟草稿、不可变版本、selected/loaded；监听端点 | 手工连接参数及会话内请求；首增量不持久化调试目标/运行意图，不进入模拟版本 |
| 数据所有者 | 每个模拟实例自己的内存、规则、版本与写入准入 | 远端设备拥有实际值；DS只保存有界结果/采样事实，不能成为本地image |
| 任务/连接 | 监听器、已接入客户端、模拟tick | 主动连接、串行请求、一次读/有界轮询 |
| 停止/权限 | 单实例stop关闭其server与接入连接，按旧合同保值 | 停止轮询/关闭调试连接只影响该调试session；独立远端写入开关/确认 |
| 状态/日志 | `role=simulator`、instance_id、loaded_revision、epoch | `role=debugger`、session_id、generation、request_id/chunk |

两角色可以在同一进程并存，但共用进程资源总预算。连接调试不调用simulator start，停止模拟不隐式停止独立远端会话；应用退出由组合根按共同期限分别关闭两类资源。用户可明确把正在运行的本地模拟器作为一个调试目标，仍须走真实协议socket，不回退为内存短路，连接本身不会帮它启动。

```text
模拟页面 -> 薄IPC -> 模拟配置/版本服务 -> S7实例或Modbus实例 -> 本地协议server
调试页面 -> 独立薄IPC -> 调试会话/有界请求服务 -> S7或Modbus client -> 远端设备
                    复用适用的纯类型/规则辅助、日志设施和通用表格
```

不建立插件平台、通用工作流引擎、中央调度服务、Backend代理或新共享可写数据库。

## 4. R02–R03：协议分型、存储兼容与模拟业务边界

### 4.1 R02：模型建议

持久配置采用明确的版本化payload入口。候选v2只共享稳定id/name、可选brand/model资料、公共策略和版本事实；协议内容为可辨识联合：

| 分型 | 协议专属内容 |
| --- | --- |
| `s7` | listen.host/port、rack/slot/calling_tsap、S7 DB（id/number/length/points/byte/bit/来源/确认），保留现有语义 |
| `modbus_tcp` | listen.host/port、显式Unit ID、四种table的有界areas、points及register codec；没有rack/slot/DB |

一个已保存模拟实例的protocol不可直接翻转；用户新增另一协议实例并显式配置，避免同UUID的DB历史被解释为寄存器。Modbus `Area`有稳定id、table、零基start_address、quantity；bit表按bit计数，register表按16-bit register计数，区间不重叠且起点+长度不溢出65536。point引用area及绝对PDU地址，type占用范围必须完全位于area内；首版拒绝相互重叠的typed point/别名，禁止多寄存器标量被半写。

S7继续由其已验证owner/image/native adapter处理；新增Modbus模型、image和adapter有自己的寻址，不把S7 `Request.db/start/data[256]`改名后冒称公共协议请求。实例manager只用小型枚举分派公共start/pause/stop/reset/snapshot；共享纯值规则/校验工具须有实际两处消费者，S7 codec和Modbus register codec分开。协议adapter负责帧/连接/协议异常映射，共享模拟业务负责初值、唯一写方、规则、版本、提交和观测；adapter不持第二份权威业务内存。

### 4.2 R03：兼容、迁移与回退建议

推荐先评估**保持SQLite v1表结构，新增payload schema_version=2及版本化读取**，避免首增量同时重写SQL模型。SQLite `user_version`/format标识描述容器结构，payload版本描述业务内容，不能混为同一个版本号；也不能因为DDL没变就说不存在数据迁移风险。

1. v1 payload继续按原字节hash/原DTO验证，再在内存映射为S7分型；不重写旧revision/source BLOB、原hash、UUID、saved_seq、selected/previous或历史UTC。旧S7初值/策略/布局确认不能因加protocol字段无故丢失，也不能将归一化后摘要冒充原slice_sha256；版本化摘要规则须可验证。
2. 普通startup/read/reopen不迁移、发布或裁剪。首次持久化v2是显式数据格式维护：另立获批schema-maintenance/迁移范围，应用已停止且profile独占，先保全可恢复的完整已关闭库和身份，再用CAS/短事务写新草稿；不可变旧版本原样保留，新版本只由显式“保存为版本”生成。先证明合成库故障/恢复，再决定是否授权用户profile操作。
3. 新二进制须能读取v1/v2历史并按各自原版本编译/加载；旧二进制遇v2不支持时明确拒绝，不能降级忽略Modbus或清空草稿。旧loader可能遍历多份revision，仅把selected切回v1不保证旧程序能打开混有v2的库。回退须显式停止应用，使用迁移前完整profile/库备份或独立保留profile，保全新库且不得静默抛弃迁移后新增记录；不能让旧程序写含v2的新库，不作原库原位自动降级。迁移后配置的保全与恢复选择须由Owner明确。
4. saved/latest、每实例selected、实际loaded、pending预览和previous回退保留继续分别记事实；草稿保存不加载，加载不启动。运行中只编辑草稿，结构/协议内容变化停机预览后加载；换版兼容保值、reset、stop-start、重开初始化并停止按现有S7合同回归。
5. profile锁、`DS_PROFILE_DIR`优先级、自有.env边界、空配置、只读/坏库拒绝和正常关闭保护保持。新增日历字段按`Asia/Shanghai`/`+08:00`，显示到秒；旧`*_utc`/payload时间不批量加八小时，单调计数仍只用于耗时/排序。

如果实际实现证明必须增表/列、改变appID/user_version、迁移ledger或目录定位，停止该设计路径，PM新Revision明确DDL、备份/恢复、旧版拒绝和批准点；本r1不给SQL/schema/数据写入权限。

## 5. R04：Modbus TCP模拟的首增量合同

四表为`coils`、`discrete_inputs`、`holding_registers`、`input_registers`。配置和协议使用零基PDU地址0..65535；常见0xxxx/1xxxx/3xxxx/4xxxx编号仅可作为明确基准的辅助显示，用户不能输入40001后由系统默默猜成地址0。bit值为BOOL，寄存器按16位值传输。四表及PDU寻址依据[Modbus官方V1.1b3 §4.2–4.4](https://www.modbus.org/file/secure/modbusprotocolspecification.pdf)。

| 首增量建议 | 模拟server及调试client的范围 |
| --- | --- |
| FC01/02 | coils/discrete_inputs读取，协议每次1..2000 bits；实际设备或产品预算可更低 |
| FC03/04 | holding/input registers读取，协议每次1..125 registers；设备下限优先 |
| FC05 | 单coil写；值编码、地址、写方、权限先校验，拒绝不改变image |
| FC06 | 单holding register写；只允许完整16-bit目标，不拆写32-bit值 |
| 其余功能码 | 明确unsupported/协议异常；FC15/16/22/23、广播、网关路由、诊断/文件传输另定范围 |

上述协议数量上限来自[官方§6.1–6.6](https://www.modbus.org/file/secure/modbusprotocolspecification.pdf)，不是EVO800或其他设备能力证明。首增量一个模拟实例监听一个TCP端点、接受一个显式Unit ID；建议产品允许1..255、默认1并拒绝0，属于待批准产品域，不承诺广播/网关。不同Unit ID不能落到同一内存而假成功；同端口多Unit设备模拟列后续。监听首轮继续IPv4 loopback、用户可配置高位端口，不开放wildcard/远端监听或申请102/502特权端口。

建议首轮typed点：bit表BOOL；register表U16/I16/U32/I32/F32（有限f32），32-bit占两个连续register。寄存器内wire字节按网络大端；跨寄存器word_order明确`high_word_first`/`low_word_first`，不由品牌猜。UI同时显示原始16-bit register和typed值；不支持的字节交换、64-bit、字符串、BCD、厂家缩放/地址映射另批。32-bit点可由本地规则/UI生成并被读取，但其协议写在未批准FC16的阶段默认禁用；不能把一个FLOAT拆成两次FC06后声称单点写成功。

配置只分配显式area，建议每实例最多16 area、4096 typed点，四表总原始image不超过256KiB；沿既有最多8模拟实例及全进程预算，所有数字是设计预算，非已测容量。未映射地址/越界/空洞按真实协议异常拒绝，不自动创建全地址空间。规则沿hold/fixed/ramp/sine/random/toggle的适用类型，初值只在初始化/显式reset生效，pause不让出rule写权；discrete_inputs/input_registers在协议上始终只读，不能用模拟策略打开远端写。所有协议/UI/rule/init/reset写经该实例唯一受控提交入口，权限冲突在提交前拒绝，失败无值/seq变化；FC05/06只承诺该单操作提交粒度，不宣称跨请求原子。

## 6. R05–R07：手工调试、范围采样与受控单点写

### 6.1 R05：直接手工输入

首次使用无需先创建模拟实例、发布版本、导出文件或启DAA。选择协议后手工填写连接参数，显式连接一次，随后复用该连接多次请求：

| 操作表单 | 必填事实与反馈 |
| --- | --- |
| S7连接 | 目标host/port、rack/slot，必要的TSAP选择须显式可见；首轮建议IPv4字面地址，DNS/IPv6另批准。不同设备的非优化DB/访问许可由实际目标资料确认，不能把连接成功当任意DB可读写。 |
| S7单点 | DB号、byte offset、BOOL bit（如适用）、明确type；STRING须声明最大长度/编码；显示实际请求字节数。 |
| S7范围 | DB号、起始byte、byte长度，先显示将读取的区间/分块；raw hex/byte为事实，typed解码按用户声明的offset/type附加展示。 |
| Modbus连接 | 目标host/port、显式Unit ID；Unit ID改变视为目标变更，先结束旧代次。 |
| Modbus单点/范围 | table、零基PDU起点、quantity（bit或register），type/word_order；读取功能码由table确定且可见，不能选择不匹配功能码。 |

连接/协议拒绝、超时、解码失败分别显示；不能把缺值填0/false，不能使用上次成功值冒充本次值。连接成功只说明握手/transport事实；单点成功不代表整段或其他表成功。

### 6.2 R06：有界读取与逐块事实

支持“读取一次”和显式“开始轮询/停止轮询”。每个逻辑请求有request_id，每块有chunk_index、目标generation、真实地址/数量、DS本机请求开始/响应完成的观测时间`+08:00`、耗时、raw结果或错误。这些时间不等于设备内部采样或事件发生时刻；只有设备实际提供事件时间时才另列该事实及其来源，不能从请求时间推算。整体给complete/partial/failed/cancelled及成功块/总块数；某块失败保留已完成块，本轮后续块默认停止，未读块标not_attempted，不补上轮值。协议异常可保留同一干净连接供下一次显式请求；transport超时/帧关联异常则走§7恢复。

分块上限取协议、协商PDU、用户已确认设备限制和产品硬预算的最小值。S7建议单块≤256B且必须适配实际协商PDU与目标限制；Modbus取FC01/02≤2000bit、FC03/04≤125register并允许更小设备上限。规划前检查起点+数量溢出、类型完整性及总块数，拒绝跨DB/跨table隐式拼接。

多块只构成先后采样，**不是跨块原子快照**；即使底层库返回一份大数组，也须揭示其分块事实。[Snap7官方client说明](https://snap7.sourceforge.net/snap7_client.html)的大请求可能内部拆PDU，候选adapter须按受控块调用并确认没有隐藏更小拆分，无法获得块级证据时不得宣称已逐块取证。typed值尽量完整落在一个块；跨块/缺字节时标incomplete，若允许组合则明确多时刻来源，不伪装同刻值。STRING头/长度、signed范围、NaN/Inf及非法编码按声明解码并保留raw，不静默转型。

### 6.3 R07：远端写入独立、默认一次

调试首阶段只读；后续受控写增量独立批准。远端写开关默认关闭、只在当前目标generation有效，切目标/断线/重开即失效。模拟器的client_write/ui_maintenance、TIA可写资料、点位文件或品牌字段均不授予调试写权限。

单点写预览必须列出协议/目标/端口/Unit ID或rack-slot、DB/table、地址、type、编码后的精确范围和值；用户确认后默认只执行一次，不轮询写、不自动重发、不自动“读全块→覆盖全块”。最近读到的值只是样本，不是远端CAS条件；读回核对另记新采样，不能反推此前unknown请求的执行结果。

- S7首增量只考虑明确完整标量及受限STRING写：沿已支持BOOL/BYTE/WORD/INT/DINT/REAL等类型逐项冻结；STRING仅ASCII、最大长度1..254、实际长度≤最大值、完整头及载荷，未明确最大长度不发写。BOOL必须使用能证明邻位保持的位写；若候选只有整byte读改写，首增量拒绝该位写，不能隐式覆盖并发邻位。多字节单点在候选/设备不能证明一次受控操作时缩小支持集。
- Modbus先FC05 BOOL与FC06 U16/I16单register；input/discrete表拒写，32-bit单点写在FC16单独批准前拒绝。FC16“一个typed点占多个register”与“批量/整段写”是不同范围，仍须另行定义完整准入、回执和设备边界。
- 请求未发送可确定cancelled；发出后缺可靠应答为`unknown`，即使UI取消、socket关闭或超时也不声称没写/已回滚。明确协议异常与已确认成功分别记录。协议write ACK只代表该协议请求结果，不代表设备工艺动作完成。
- 批量、整块、读改写、掩码写、命令握手、自动恢复写列后续；须定义每操作/每块的部分成功、unknown及停止点，不能以一个布尔总成功隐藏前面已执行的写。

## 7. R08–R09：连接复用、有界排队、取消与观测

### 7.1 R08：会话和期限

每个调试连接由一个会话owner拥有client/context/socket与在途请求；首增量建议全应用最多1个调试session，不建立连接池。一个连接支持多次单点/范围/轮询请求，底层始终最多1个wire在途操作；UI操作、轮询和恢复共用同一有界入口，不能每次点击开新线程/新连接，也不能多个`&mut client`跨任务并发使用。

推荐预算供后续精确阶段批准；以下均未实测，既有S7模拟容量不能当这些数字的证明：

| 项目 | 首轮建议上限/行为 |
| --- | --- |
| 调试会话/队列 | 1会话，1在途块+16待处理逻辑请求，排队描述/待发载荷总≤64KiB；超额明确busy，不丢旧写换新写 |
| 单次范围 | S7≤16KiB；Modbus≤4096register或8192bit；最多128块；一项超限就在发包前拒绝 |
| 轮询 | 每session最多1任务，间隔≥250ms，单次启动最多10分钟或1000轮，先到即停止；每次仅保留一个待执行轮次，慢轮跳过/合并，记missed/coalesced，不追赶堆积 |
| 时间预算 | connect建议3s；单块IO建议2s；排队上限2s；逻辑范围总期限30s（含排队）；超总期限返回已完成块及剩余not_attempted，写仍按发送事实判unknown |
| 结果/刷新 | 当前结果与最近100个逻辑结果总≤4MiB，过限淘汰最旧并显示截断；UI可见刷新≤1Hz，不每tick追加无限DOM |
| 关闭 | 共同关闭目标≤5s；先封准入/取消未发项，结束在途IO并等待实际task/worker join；超时保持closing/fault，不能假报disconnected或归还资源 |

范围分块间给手工请求执行机会，轮询只占有限轮次；公平单位为有界wire块，单个范围不永久占住连接。排队期限/取消在真正发送前再次核对，过期写绝不补发；控制不排到普通请求队尾。轮询参数来自当前手工表单的冻结副本，编辑表单不悄悄改变已启动任务。

状态至少为disconnected→connecting→connected，错误进入fault，关闭进入closing→disconnected。连接目标和协议指纹绑定generation；切目标先停止轮询、封旧队列、关闭并释放旧连接，再建立新代次；旧请求结果只归旧上下文，不能写入新目标表格。用户单次请求取消移除其未发块；若在途取消无法安全保持帧对齐，结束整个transport并换generation，不能只取消前端Promise。停止轮询不必断开健康连接，但必须等该任务已无待发/在途轮次再报告stopped；若中止在途IO需关闭transport，显示实际断开原因。

transport超时、晚到响应或关联不明后，建议废弃旧context，清理/join后由用户显式重连，不自动恢复原逻辑请求；保留unknown写且从不重放。若以后自动只读重连，需另定有界退避和恢复范围，不能先写一个通用无限retry。候选库公开API不保证取消安全：[tokio-modbus client](https://docs.rs/tokio-modbus/0.17.0/tokio_modbus/client/trait.Client.html)与[上游超时问题报告#324](https://github.com/slowtec/tokio-modbus/issues/324)只能支持进一步审查，问题报告不是本地已复现事实。

候选S7阻塞FFI由专用有限worker承担，必须有底层connect/send/recv期限及安全中断/完成后join；不能用每请求`spawn_blocking`加外层timeout冒充可取消，[Tokio官方说明](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html)明确已开始的blocking任务不能abort。Modbus server/client采用Tokio时也须跟踪全部child tasks；[server serve/serve_until](https://docs.rs/tokio-modbus/0.17.0/tokio_modbus/server/tcp/struct.Server.html)的每连接task及任意await中止边界不自动满足业务提交/关闭合同。任何候选不能证明真实结束/释放就否决或返PM，不用无界线程、强杀进程或仅丢JoinHandle兜底。

### 7.2 R09：真实状态、日志和资源证据

调试连接/断开/恢复、轮询启停、准入拒绝、手动请求终结、写确认/发送/ACK/unknown、错误及资源关闭须有必要的可关联事件；日志包含role/session_id/generation/request_id及适用chunk、目标指纹/协议、地址/数量、错误分类、已发送/应答事实及时间。普通成功轮询结果（包括各chunk）只进入有界结果环，不逐轮/逐块写持久JSON Lines；轮询持久事件限启停、异常/状态变化及有界节流汇总，重复异常可聚合并保留首末时刻和计数，汇总窗口/条数预算由实施阶段冻结。持久JSON Lines和有界内存环复用现有设施，日志不得把模拟instance_id与远端session混为一项。业务日历为`+08:00`，耗时/期限用单调时钟；UI刷新不是请求/响应观测或设备事件时间。默认不持久化整段raw值、用户敏感载荷或凭据；写值可在当前确认/结果界面核对，持久日志保存必要摘要/长度及结果，公开证据脱敏。

后续验收同时观察会话owner/在途数/队列/轮询任务、socket/线程/句柄和实际join。包括无应答、半帧、断连、取消、切目标、重复关闭和应用退出；必须看到自有任务结束与资源回落，再报告释放。Stop按钮变灰、页面隐藏、连接对象析构、listener不在均不能单独证明已释放。模拟/调试并发要核全进程预算和互不误停，既有native硬崩可能影响整个进程的边界继续保留，不承诺进程级故障隔离。

## 8. R10：界面与手工输入效率

同一应用提供清楚的“设备模拟 / 本地模拟服务”和“设备读写调试 / 连接远端设备”入口。配置中心的协议标识同时出现在实例行、详情、监听/启动确认和日志筛选中；选S7才显示DB/TSAP/导入，选Modbus显示四表/area/PDU地址/word_order。品牌/型号是资料区，未核实资料可标unverified，不能出现“已兼容汇川”产品文案。

调试页面顺序为连接参数→单点/范围表单→读取一次/开始或停止轮询→raw与typed结果；写入是独立默认关闭入口。支持键盘Tab、正常数值键入、保留未完成/非法输入及准确单位提示，常用连接参数在当前会话复用；切目标确认后清空旧结果/写准入。首轮不强加保存连接库、版本发布或点表导入步骤；可有清除表单，不自动发现/扫描设备。

结果表显示协议地址、raw/typed值、质量/错误、DS本机请求开始/响应完成的观测时间与块编号；设备实际提供的采样/事件时间及来源另列，缺失时不推断。历史结果标明目标和代次，partial/unknown直接可见。新普通列消费公共列宽工具：可拖拽、有合理min width/横滚、按应用/稳定表ID/字段键本机持久化及每表恢复默认；特殊操作列可固定，不用翻译标题作存储键。新增文案进入中英对称locale，不写死在Vue/Rust错误串；Rust返回稳定错误key，UI翻译。只扩当前DS页面及新调试模块，不重做CU、其它AW应用或整套导航系统。

## 9. R11：向FF的JSON字段映射与可导出性反馈

FF主会话的统一JSON设备点位清单仍是**未批准、未落地提案**；本节只反馈DS可提供的事实与缺口，不创建合同/schema/示例文件、不修改FF加载器或其文档/源码，也不把JSON定位争论变成当前任务依赖。建议共同骨架`schema_version / source / devices[]`；正式schema_version值、required字段和type枚举必须由后续双方合同范围确定，本文不抢占版本号。

| 提议字段 | DS当前S7来源 / Modbus所需来源 | 交接约束 |
| --- | --- | --- |
| `schema_version` | DS自身Workspace版本不能直接当跨应用合同版本 | 独立合同版本，未定；不能写“FF已支持” |
| `source` | 选定不可变revision的id/saved_seq/原payload SHA，导出模式和`generated_at(+08:00)` | 记录工具/合同版本及来源，不嵌SQLite文件、原源码全文/私有路径 |
| `devices[].id / protocol` | InstanceConfig.id；当前v1明确映射`s7`，v2来自分型 | 保留稳定UUID；品牌/型号另列metadata，不根据品牌猜协议 |
| `connection`端点 | host/port是server listen配置，不天然等于客户端可达端点 | 用户明确提供/确认client host和目标端口，禁止wildcard；loopback仅同机有效。debug target不反向默认取模拟listen并自动启动 |
| S7 TSAP方向 | `calling_tsap`是server期待的client calling TSAP；server的`called_tsap()`由rack/slot导出，lifecycle分别校验两者 | 以client视角，local/calling候选对应server期待的calling，remote/called候选对应server的called；必须核候选SDK参数语义及真实COTP方向后映射，不能直接改名移植，也不由listen端点推断TSAP或可达host |
| 设备来源/运行摘要 | 指定saved revision切片；selected与实际loaded由各自事实查询 | 显示export_mode及每设备saved/selected/actual_loaded id、seq/hash、观察时刻；实际loaded可为空、可不同版本，不把latest当loaded |
| S7 DB列表 | DbConfig.id/number/length/enabled与地址确认 | 导出实际DB号/长度，不能从name或顺序猜；不导出不存在的DB |
| `points[].id / name / display_name` | PointConfig.id/name/display_name | id是身份，name可经明确命名变化；地址变更不重建ID；稳定身份不代表地址合同不变 |
| 来源名称/路径 | 绑定tree及结构化segments/source_path/source_versions | 保留原名/路径和来源版本/hash；手工点可无source_name，不把display_name或拆字符串猜值当TIA原名 |
| `data_type / enabled` | data_type/enabled；BYTE/USINT/WORD/INT/DINT/REAL/BOOL/STRING等需显式字典映射 | 保留native type及STRING最大长度/ASCII约束；跨语言规范类型后续确认，不能大小写替换充当转换 |
| S7地址 | DbConfig.number及point.byte/bit | BOOL带bit，完整长度由已验证type推导；缺地址/确认失败给问题，不导出可执行假地址 |
| Modbus地址/读取功能码 | 未来table/area/start_address/quantity、type width/word_order、Unit ID | 四表和零基PDU是主事实，FC01/02/03/04由table派生；写功能码资料不是写授权；目前无模型可供真实导出 |

推荐导出入口首先选择**一个不可变saved revision**；同文件所有点取自该冻结配置，附各实例当时actual_loaded摘要及不一致提示，不混入未保存草稿或在线值。若另提供“按各实例actual_loaded导出”，则逐实例从其真正loaded的不可变版本取点/DB/来源，允许不同版本并明确其观测时间；它是独立后续增量，不能用selected代替，也不宣称跨实例瞬间原子一致。

只导出已声明、确认且类型受支持的点；未类型化raw区域/空洞不是自动生成的FF点。默认全部问题先列清单且不生成文件，若未来允许排除需用户明确选择并输出omitted摘要，禁止静默遗漏。模拟initial/rule/client_write/ui_maintenance不转成FF写权限；运行值、用户.env/凭据、SQLite可写路径不进入清单。DS通过自身服务生成文件，FF只消费人工选择的文件，不共享或直接修改DS SQLite。后续导出测试要验证schema/未知版本、稳定ID/重复ID、地址/类型边界、来源版本/hash、reachable host、selected≠loaded、缺确认与失败无半文件；只有正式合同获批后才能称“合同验证通过”。

DS导出可独立阶段实施，先给S7提供文件；无需等Modbus模拟或调试全部完成。FF可以先手写/维护其自身获批格式的JSON，不以DS导出为其前置依赖。本会话不发送跨会话消息或变更FF任务归属。

## 10. R12：候选技术栈、分阶段建议和技术gate

继续Tauri v2 + Vue/TypeScript + Rust runtime +现有SQLite/CU/Element Plus设施，普通启动继续`pnpm tauri dev`，所需features由Tauri配置承担；不复制新“品牌版”工程，不引Python sidecar/Backend/Celery。新增依赖须在实施spec中冻结版本/feature/lock及许可证/平台影响，本轮不安装、不解析Cargo新锁、不编译/启动。

| 能力 | 候选与必须证明的gate |
| --- | --- |
| Modbus TCP | [slowtec/tokio-modbus官方项目](https://github.com/slowtec/tokio-modbus)及[0.17.0 TCP server API](https://docs.rs/tokio-modbus/0.17.0/tokio_modbus/server/tcp/index.html)是候选，TCP client/server分feature收敛，不启RTU。须核MBAP/事务/长度校验、异常回执、提交前拒写、child task归属、连接/帧/输出预算和真实关闭；API存在不表示这些都已满足。 |
| S7调试client | 优先评估已纳native构建的Snap7 client经独立薄bridge暴露，[官方API](https://snap7.sourceforge.net/snap7_api_ref.html)仅作能力资料；也可评估独立Rust client，不能修改/依赖DAA私有runtime或拿其旧读证据代验本client。须先证端口/TSAP、受控分块、位写/STRING、期限及join；不能停就回选型。 |
| 共享业务 | 原S7 adapter/owner优先保持，新增Modbus专属image/codec及小型枚举分派；只抽已被两侧消费的纯规则/结果辅助，不预建驱动注册平台。 |
| 合成独立协议验证 | Modbus server用独立raw-wire或另一实现的client核协议，不只server/client同库自测；调试client再对独立合成server验证延迟/异常/晚到/断连。S7回归保持其原协议与资源向量，模拟profile不操作用户库。 |

建议阶段如下；它们是路线建议，全部尚未授权。一个阶段验收不自动启动下一阶段，数字/文件/依赖有实质变更须PM重新冻结：

| 阶段 | 有界交付与进入条件 | 验收/后续批准 |
| --- | --- | --- |
| D0（本轮） | r1设计、字段映射和五文件导航；只读源码/官方资料与静态文档核对 | Human Owner审阅精确r1；没有产品/独立QA结果 |
| A0 | 单独获批的Modbus adapter可行性及payload兼容合成验证；不接用户profile | 先证写前拒绝/异常/资源关闭、v1原字节保护/新payload拒绝和恢复；失败返回PM，不先改全部UI |
| A1 | 按新的精确scope将Modbus TCP模拟接配置/版本/有限UI，保留S7原路径 | 双协议隔离、FC01–06的批准子集、规则/权限、S7回归及正常退出；用户profile迁移仍另批准 |
| B1 | 独立设备调试只读：手工S7/Modbus连接、单点/范围/有界轮询、队列/取消/释放 | 合成目标验证，无需先建模拟配置；证明重用/超时/晚到/切目标和真实资源下降 |
| B2 | 再批准受控单点写：S7受支持类型、Modbus FC05/06 | 默认关闭/目标确认、拒绝/ACK/unknown/no-replay、位邻居/STRING；不含批量或FC16 |
| C | 文件导出，可在A/B之前独立做S7切片 | 先与FF owning范围明确正式文件合同；仅DS导出/验证，不改FF源码；不是FF手写JSON的依赖 |
| D | Windows/Linux、安装分发、RTU、FC16/批量写、远端监听及真实EVO目标 | 各自先核资料/精确spec/资源授权/平台证据；本r1不授予任何真实设备连接/写入 |

当前可推荐先做A0→A1，再做B1→B2；如果近期工作重点是手工排查，B1也可独立优先，不需要先完成A。Owner选优先级时决定下一精确实施spec，不把本轮建议默认为下一阶段授权。

## 11. 候选精确文件集合（仅估算、不是当前allowlist）

下列前缀`D`均为`automation-world/device-simulator/`。花括号仅列出有限明确成员，不是目录递归/通配权限；`planned`表示当前不存在。本轮一律不写。实施Revision须从中选择真正需要的文件，补齐实验/依赖精确版本和验收；未列路径或拆分改名需重新评审，不能用本表自动扩scope。

| 后续候选 | 文件与责任 |
| --- | --- |
| A：协议分型/兼容 | 既有`D/runtime/src/domain/{configuration.rs,layout.rs,mod.rs}`、`D/runtime/src/services/{configuration.rs,source_import.rs,layout.rs,naming.rs,apply.rs,versions.rs,queries.rs,mod.rs}`、`D/runtime/src/infrastructure/config_store/{queries.rs,transactions.rs,schema.rs,mod.rs}`、`D/runtime/src/app.rs`；新增`D/runtime/src/domain/{device_configuration.rs,modbus.rs}`（planned）。保留旧DTO/hash语义并显式分派，schema.rs只调整版本化校验所需部分，DDL不在本建议内。 |
| A：Modbus运行/接线 | 新`D/runtime/src/services/{modbus_owner.rs,modbus_lifecycle.rs}`、`D/runtime/src/infrastructure/modbus_tcp.rs`（planned）；既有`D/runtime/src/infrastructure/mod.rs`、`D/runtime/{Cargo.toml,Cargo.lock}`、`D/src-tauri/{Cargo.toml,Cargo.lock,tauri.conf.json}`。既有S7 `owner.rs/lifecycle.rs/native_ffi.rs`不是Modbus重写面；若实需共同预算的小改，须在下一scope逐项加入。 |
| A：模拟UI | 既有`D/src/services/deviceSimulator.ts`、`D/src/console/composables/useDeviceSimulator.ts`、`D/src/app/simulator/views/{instances,points,policies,values,overview}/index.vue`、`D/src/app/simulator/components/{ApplyPreviewDialog.vue,PolicyEditor.vue,PolicyBatchDialog.vue}`；新`D/src/app/simulator/components/ModbusAreaEditor.vue`（planned）。源导入仍S7专属，不能伪装Modbus导入。 |
| A：合成验证 | 新`D/runtime/tests/{workspace_compatibility.rs,modbus_model.rs,modbus_protocol.rs}`、`D/tests/protocol/modbus_cases.py`（planned）；既有`D/runtime/tests/{configuration_store.rs,apply_retention.rs,source_import.rs,versions.rs}`只为真实受影响回归；既有S7协议fixtures/oracle保持，不随新实现重写expected。 |
| B：调试运行/IPC | 新`D/runtime/src/domain/debugging.rs`、`D/runtime/src/services/{debugging.rs,debug_polling.rs}`、`D/runtime/src/infrastructure/device_clients/{mod.rs,s7.rs,modbus_tcp.rs}`、`D/src-tauri/src/commands/debugging.rs`（planned）；既有`D/runtime/src/{domain,services,infrastructure}/mod.rs`、`D/src-tauri/src/{app.rs,lib.rs,commands/mod.rs}`。S7 client若采用native bridge，新`D/native/bridge/{ds_s7_client.h,ds_s7_client.cpp}`（planned）及既有`D/native/CMakeLists.txt`须在B scope明确；不默认修改controlled上游。 |
| B：调试UI | 新`D/src/app/debugger/{manifest.ts,api/deviceDebugger.ts,views/device-debug/index.vue,components/TargetConnectionForm.vue,components/DebugReadForm.vue,components/DebugWriteDialog.vue,components/DebugResultsTable.vue,locales/zh-CN.json,locales/en-US.json}`（planned）；既有`D/src/console/{sections.ts,types.ts}`、`D/src/App.vue`、`D/src/styles/app.css`。独立facade/state，不把远端调用加进本地模拟写操作。 |
| B：合成验证 | 新`D/runtime/tests/{debug_sessions.rs,debug_reads.rs,debug_writes.rs,debug_shutdown.rs}`、`D/tests/debug-input.test.mjs`、`D/tests/protocol/debug_target.py`（planned）；必要真实原生流程在既有`D/tests/ui/{native_driver.js,scenarios.json}`按批准子集增加，不重建通用测试平台。 |
| C：导出切片 | 新`D/runtime/src/domain/point_manifest.rs`、`D/runtime/src/services/point_export.rs`、`D/src-tauri/src/commands/export.rs`、`D/src/app/simulator/components/PointExportDialog.vue`、`D/runtime/tests/point_export.rs`、`D/tests/point-export.test.mjs`（planned）；既有对应三个`mod.rs`、`D/src-tauri/src/lib.rs`、`D/src/services/deviceSimulator.ts`及实例页。正式合同/schema的存放、文件名和归属须双方范围先明确，本表不授权root contracts或FF写入。 |
| A/B/C各自必要文档/文案 | 既有`D/src/app/simulator/locales/{zh-CN.json,en-US.json}`、`D/{README.md,README.zh-CN.md,USER_GUIDE.md,USER_GUIDE.zh-CN.md,BUILD.md,BUILD.zh-CN.md,CODE_INDEX.md}`、`D/runtime/{README.md,README.zh-CN.md}`、`D/src/app/{README.md,README.zh-CN.md}`、`D/tests/{README.md,README.zh-CN.md}`只按实际触达同步。当前导航仍仅§1四件，源码结构未变不更新CODE_INDEX。 |

任何阶段都不以目录级授权覆盖用户真实配置/SQLite/日志或历史证据；不改FF/Backend/DAA/CA/SMA/CU/shared core，不新造根或第二DS bundle。未来若需要跨owner公共提取/正式合同变化，另立相应独立范围。

## 12. 可核验的设计验收与后续行为矩阵

下列AC是**r1设计完整性标准**，供Owner审阅及以后文档Verification使用；不是当前QA pass，也不是代码验收。D0只有PM/协调必要静态自检，不预建checklist。A/B/C实施必须把对应行为矩阵转为其精确获批AC、DEV命令及fresh Verification输入。

| AC | 对应需求 | 可审阅结果 |
| --- | --- | --- |
| AC01 | §1–2 | 唯一本地Task ID/r1/draft、五文件写面、历史/当前时点和角色gate明确；不继承DS-001例外或旧验收。 |
| AC02 | R01 | 同产品按S7/Modbus TCP分协议、品牌型号独立、EVO800资料未核、RTU延期。 |
| AC03 | R01 | 模拟/调试配置、连接、任务、内存、状态、日志、权限和停止范围隔离，连接不会启模拟。 |
| AC04 | R02 | 准确定位InstanceConfig/DbConfig/image/owner/FFI的S7耦合，明确Modbus四表/area/typed范围及adapter/业务边界。 |
| AC05 | R03 | v1原BLOB/hash/ID/确认/版本引用保留、内存归一化和持久迁移区分，普通startup不迁移，备份/恢复与旧二进制拒绝有gate。 |
| AC06 | R03 | 草稿/saved/selected/actual_loaded、预览/回退保护、停机加载/独立启动、同版幂等、stop保值/重开初始化/profile/时间保留明确。 |
| AC07 | R04 | 四表、零基PDU、FC01–06有限子集、协议/设备上限、Unit ID/分配预算、网络大端/word_order及拒半写完整。 |
| AC08 | R05 | 无模拟配置前置的手工S7/Modbus单点、范围连接/地址/type/数量表单及真实错误态明确。 |
| AC09 | R06 | 受控分块、每块采样/错误/partial、hidden split gate、typed不完整和非跨块原子约束可推演。 |
| AC10 | R07 | 默认只读、独立单点写确认、BOOL邻位/STRING/FC06限制、ACK≠工艺、unknown/no-replay及批量延期明确。 |
| AC11 | R08 | 同连接多请求、1在途/有界队列、轮询上限/合并、公平和期限包含排队；generation防串目标。 |
| AC12 | R08–R09 | 取消未发/已发区别，真实socket/task/worker join和释放/closing失败边界、两角色并发及退出总期限明确。 |
| AC13 | R09–R10 | 日志上下文/JSONL/有界环与+08时间语义、手工输入效率、对称i18n及公共列宽要求明确。 |
| AC14 | R11 | JSON骨架只是提案；字段逐项有DS来源/缺口，稳定ID/来源版本/实际loaded/可达host/权限隔离明确，不共享SQLite或修改FF。 |
| AC15 | R11–R12 | S7导出可独立、FF可先手写；模拟/只读调试/单点写/导出/平台分期，阶段批准点明确。 |
| AC16 | R12/§11 | 候选技术有一手资料和否决gate；当前与未来文件集合分开，planned与既有路径可核对，无目录通配实施权限。 |
| AC17 | §12–13 | S7回归、独立Modbus协议、调试合成目标/故障资源、JSON合同、三平台/真实目标证据界限及回退风险齐备。 |
| AC18 | 全文 | Markdown元数据/本地引用/围栏/表格及双语导航一致；实际执行检查和未运行项诚实记录，无源码/schema/监听器/依赖/设备动作。 |

未来行为矩阵（当前全部not_run，不把设计推演当已测）：

| 编号 / 阶段 | 必需场景与证据 |
| --- | --- |
| V01 / A | 旧S7合成v1草稿/多份不可变revision/selected/previous读写兼容；原BLOB/hash/ID前后相同，迁移前后备份/失败恢复、坏库/未知版本拒绝、同版加载不重置、预览/删除保护。 |
| V02 / A | 两协议实例隔离/同端口冲突/独立暂停停止/重新绑定；S7 DB/BOOL/STRING/六来源拒写、保值/换版/重开及原受影响协议资源向量回归，不能只测Modbus新路径。 |
| V03 / A | 独立wire client核四表/Unit ID/FC01–06批准子集、0/末地址/越界/空洞/非法数量/MBAP长度/异常码；写前拒绝比对完整值/seq不变，word_order/跨register类型/半写拒绝。 |
| V04 / B1 | 独立合成S7/Modbus目标，单次连接连续多次单点/范围读取；类型及raw一致，范围按设备小上限分块，单块错误/partial及采样时间正确。 |
| V05 / B1 | 轮询慢目标/队列满/过期/停止/切目标/迟到响应；块间公平、generation拒旧结果，轮询无追赶积压，无暗中自动重连或新连接风暴。 |
| V06 / B1–B2 | 无应答/半帧/断连/取消/重复关闭/应用退出，核实际socket、任务、线程/句柄、join及重新绑定；至少连续20次连接关闭/轮询启停的有界资源趋势，单次成功不替代释放证明。 |
| V07 / B2 | 默认写关/目标变化失效；发送前取消不写，合成目标已接收但丢ACK导致unknown且不重发，明确ACK成功、协议异常、写后另读；S7 BOOL邻位和STRING/边界、Modbus32-bit写拒绝。 |
| V08 / A+B | 本地模拟持续运行时远端调试fault/关闭不误停模拟；模拟stop不误关独立远端session；应用退出共同deadline，完整进程资源预算而非各自局部计数。 |
| V09 / C | 正式获批JSON schema与静态golden文件，S7/未来Modbus映射、稳定point ID/重名/地址/类型/来源hash、saved≠loaded/未loaded、wildcard拒绝、缺确认和失败无半文件；无运行值/写权/SQLite共享。 |
| V10 / A/B/C | `pnpm build`/类型和i18n对称/真实UI表单普通键入、错误/partial/unknown、列宽持久与reset、浏览器无bridge不假成功；构建只证明编译，不替原生/协议。 |

环境证据必须分别记录：当前历史S7只证明对应macOS arm64候选；未来macOS实施需自己的锁/feature/正常`pnpm tauri dev`、真实native/协议/退出证据。Windows和Linux目前未验证，native/CMake的硬限制仍在；Modbus Rust库可跨平台不等于整DS已能构建/打包/释放资源。三平台可编译、原生功能、协议、安装器/签名、现场与长稳分列，未跑记not_run/deferred，无“支持三平台”概括通过。真实EVO/S7设备需核资料后逐目标独立授权，合成目标不代替实机。

## 13. 风险、开放项与回退

| 风险 | 控制与回退 |
| --- | --- |
| S7模型被假泛化而破坏旧协议/版本 | 旧DTO/owner/native保留、分型入口、原字节兼容向量和受影响S7回归；失败停新协议准入，恢复已保护候选，不reset并行工作。 |
| payload升级使旧程序打不开或引用hash失真 | 明确数据格式迁移/版本化hash与旧版拒绝；合成证明/完整备份先行，用户数据另授权；不能改原revision“修复hash”。 |
| Modbus地址/word_order误解 | 零基PDU/单位/功能码同屏；raw与typed同时可核；无厂家地址推断、不静默字节交换，真实点表另核。 |
| 写入时序和unknown造成重复动作 | 会话目标确认、一次写、不盲重试/不回滚声明；已发送与ACK分开，批量/FC16另定合同。 |
| 超时只结束外层等待，底层阻塞/任务泄漏 | 候选先过可中断/有界完成及join gate；真正释放前不归还预算，不用无限worker或强杀代替正常关闭。 |
| 双角色资源相互影响 | 分别计数及总预算，既有S7容量不外推，合成并行/取消/退出验证；native硬崩仍可能全进程影响。 |
| 导出混用最新/selected/loaded或被当写权限 | 冻结来源/每设备事实/可达host确认；文件只描述点位，FF权限独立；不共享可写库。 |

待Owner或后续阶段确认的产品选择有建议缺省，不阻止本轮设计审阅：下一优先做A还是B1；真实目标CPU/固件/Server配置/点表；是否需要RTU；是否需要32-bit写从而单独开FC16；是否需要跨机器模拟监听；调试目标是否未来持久化；JSON正式版本/规范类型与导出模式。首轮按TCP、只读先行、单点写有限子集、loopback模拟、单调试session、会话参数不持久化；这些是推荐，尚未形成实施权限。

本轮仅文档可回退：保留其他任务内容，移除本次新增spec和导航行须按Owner实际决定处理；不回滚代码、数据库、已有运行窗口或历史。未创建临时源码副本、worktree、profile、数据库、listener或构建产物；协调自有静态审计临时材料在完成差异核对且无证据依赖后按workflow回收，关键结论留本spec/交付记录。

## 14. Skill路由、PM自检与批准记录

实际PM按[pm角色](../../../../.codex/agents/pm.toml)和[canonical workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)形成本草案，使用`aiis`、`project-governance`、`plc-point-mapping`及适用跨端/资源/日志合同；没有用新项目模板或治理initializer重建既有工程。后续Rust协议/队列/存储用`rust-runtime`；Tauri壳/feature/退出用`desktop-tauri`并组合Rust；Vue/表格/输入用`frontend-ui`，文案用`i18n-workflow`，实际源码结构/文件头用`code-document-indexer`；点位/导出用`plc-point-mapping`。不因存在候选阶段就装依赖、写UI/Rust、改共享skill或执行Backend任务。

本轮允许的自检为`rg/cat/sed/nl`读取、实际路径存在性、元数据/需求AC/Markdown本地链接与围栏/表格、有限导航差异及`git diff --check`。这些是PM/协调静态自检，不是Development self-check或独立QA。未运行Cargo/pnpm构建/项目测试、schema、应用、协议server/client、DS/DAA、真实PLC/第三方接口；未读写用户.env/profile/数据库，未发送其他会话消息、邮件，未commit/push/tag/release/部署。官方协议/库页面只作为2026-11-02的只读资料，不是本地验证结果。

| 日期 | Revision / 真实决定 | 下一gate |
| --- | --- | --- |
| 2026-11-02（Asia/Shanghai） | Human Owner授权独立DS设计会话；实际PM形成DS-002 r1 draft，只设计/spec和必要导航 | 等待Human Owner审阅精确r1；本轮没有范围批准、Development、Verification或最终验收 |

**批准点：请审阅DS-002 r1的同产品双协议/双角色边界、v1保护与迁移建议、有限功能码/写入边界、分阶段路线及JSON映射反馈。** 若同意，只记录设计批准；下一实施阶段仍须PM给出精确获批范围后才进入Development。本文件保持draft，沉默、方向认可或其他任务接受均不等于本r1批准。
