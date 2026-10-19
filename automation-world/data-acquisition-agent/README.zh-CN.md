# AIIS Data Acquisition Agent

[English](README.md)

DAA 复用 CU 公共壳，只有一个本地 SQLite runtime。普通 `pnpm tauri dev` 直接打开工作台、PLC 配置、点位与采集组、上报与存储四页，无需 mode/storage 开关。`pnpm tauri:dev` / `pnpm tauri:dev:snap7` 显式编译可选 Snap7 驱动；普通启动不编驱动，显式连接时缺驱动仍返回 `driver_unavailable`。

```bash
pnpm install --frozen-lockfile
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml -- --check
pnpm tauri dev
```

来源为 CA 冻结 receipt；[DAA PLAN](PLAN.zh-CN.md) 管实施，[AW PLAN](../PLAN.zh-CN.md) 管跨工程阶段。[DAA-003 r1](plans/DAA-003-sqlite-only-startup/spec.md) 管 SQLite 唯一入口和迁入；[DAA-002 r2](plans/DAA-002-local-acquisition-loop/spec.md) 管既有本地采集基线，其 QA 与 Human Owner 最终验收仍是独立任务事实。这些说明不授权现场切换、发布或部署。

## 配置权威与启动

只选自身根 `.env` 或进程显式绝对 `DAA_ENV_FILE`；`DAA_PROFILE_DIR` 存在时必须绝对，否则使用独立应用本机 data 目录。不搜索 cwd/父目录/CA 的配置。`local-acquisition-v1/config.sqlite` / `runtime.sqlite` 是 PLC、组、点、存储及历史权威。`DAA_PLC_READ_ALLOWED` 缺省 false，即使 true 也不在启动时连接或启采。

旧 YAML 运行模式、直库 writer、Backend health、授权自检已退役，旧 IPC 不再注册。`--ca-*` 与原 runtime 二进制在配置/锁之前返回结构化 `legacy_entry_retired` / exit2，不提供新的 SQLite headless 宿主；运维流程须去掉旧脚本。所选 env 文件的 `DAA_RUNTIME_MODE=legacy_snapshot` 作为旧残留忽略并一次提示键名；进程显式该值返回 `legacy_runtime_retired` / exit2，请删除覆盖后普通启动。空值/local_sqlite 接受，其余非空值拒绝。其它旧 DB/write/autostart/endpoint/Backend/log-path 值不再消费或决定业务，真实 `.env` 不改写。Vite 使用 `envDir:false`，不消费旧 `VITE_DAA_*` 业务输入。

## 旧 YAML 一次性迁入

先取得 profile OS 锁并完成双库身份/完整性/恢复，再对首次空实例发现固定两个来源：`DAA_PLC_CONFIG_PATH` / `DAA_PLC_SNAPSHOT_POLICY_PATH` 的进程非空覆盖→所选 env 同名非空值→自身 `config/plc_points.yaml` / `config/plc_snapshot_policy.yaml`。相对路径锚定 DAA 根；符号链接/目录/非 UTF-8/读取期间变化明确失败，不扫父目录、不加载 URL。本任务验证不读取真实现场文件。

已有草稿对象/来源、不同存储策略、版本/active/previous/token、运行来源身份、解释、样本/投递/引用，均保留 SQLite，连 YAML 内容及 hash 也不读取；仅生命周期事件不使实例非空。持久迁入 receipt 也阻止每次重扫，后来改/删源或用户清空草稿都不会自动再迁。

全部可表示的 PLC/DB/组/点同次迁入为停用候选；地址全部未确认，DB 全部不完整/non-flat、无伪造结构树。旧读取窗口/计数/访问标志、不支持类型和 raw/latest 策略只保留为有界白名单来源说明/诊断，不转成 enabled、写权限、采样规则、上传/ACK 或直库规则。未知字段有诊断但不保存其值，不导入凭据；源文件原样保留。默认来源为仓内脱敏示例，同样停用。

- 缺失/空白/注释/null/空 YAML 持久记录 `skipped_empty`；仅策略存在时只归档，不制造 PLC。
- 坏语法/根形/字段类型/重复语义对象/策略映射歧义/超限整份拒绝，空 SQLite 界面仍可手工编辑；失败不会吞成空成功。
- 限额：每 YAML 1MiB、合计2MiB，深度16、节点100000，拒 alias/tag/多文档；沿用4 PLC、每PLC8组/32DB/4096点、配置16MiB。规范 receipt/白名单归档≤8MiB，诊断最多200条并说明省略数，只读摘要≤256KiB。
- 迁入历史与安全重试位于配置栏既有、默认折叠的“运行配置与版本详情”内。折叠区外仅在持久状态 unknown 或迁入失败且 Rust 返回 `retryAllowed=true` 时显示紧凑入口；不再可重试的持久失败只留作历史。失败/空/仅策略仅在 Rust 仍允许时带草稿 ETag/attemptId 双 CAS 显式重试，先保存或取消编辑。成功/已有 SQLite 没有覆盖动作。unknown 不能宣称已持久记住，须检查存储/日志并重开。计数、诊断及停用/未确认/不完整说明均为迁入时记录，不描述后续编辑状态。

文件角色：YAML 仅为一次性来源，SQLite 是业务配置权威，`.db/.udt` 是编辑时显式结构导入。普通导入不接收 YAML。复用差异预览、地址确认、组配置，随后另行显式激活、连接和启采。


### 仓内默认示例

下表是 [`config/plc_points.yaml`](config/plc_points.yaml) 的默认脱敏内容，退役策略见 [`config/plc_snapshot_policy.yaml`](config/plc_snapshot_policy.yaml)。进程/env 文件的路径覆盖可以选其他来源，因此不是任何当前用户 profile 的实际迁入清单。

| 默认示例 | 值 |
| --- | --- |
| PLC / 连接候选 | `PLC_1`，`127.0.0.1:102`，rack 0 / slot 1 |
| DB / 组 / 旧读取窗口 | DB1，`example_group`，start 0 / size 12，3 点；窗口不是完整 DB 长度证明 |
| 点 1 | `example_value`，旧类型 `Real`，offset 0 |
| 点 2 | `example_status`，旧类型 `Bool`，offset 4 / bit 0 |
| 点 3 | `example_counter`，旧类型 `DInt`，offset 8 |
| 3 点的退役策略 | raw/latest=true，raw_policy=`every_sample`；仅白名单归档，不转成新采样/上报/直库规则 |

文件没有采样值或历史。首次空实例仅迁入停用、地址未确认、DB 不完整的候选；已有 SQLite 配置/历史优先，成功/空结果私有 receipt 阻止自动重复扫描，源 YAML 不改。编辑导入仍显式使用 `.db/.udt` 结构来源，经完整源预览、地址审阅与采集组配置后，另行执行运行操作。[最小 DB/UDT 对](src-tauri/tests/fixtures/source-import-minimal/README.zh-CN.md) 是显式 DB21、三叶的手写受控导入清单，不证明实际 TIA 导出兼容或真实 PLC 地址。

## 本地采集与恢复

四页只有 `useLocalAcquisitionConsole` 一个 owner；纯 shell 只管导航/主题/语言（`daa.theme` / `daa.locale`）。浏览器无桥预览不假保存、不请求 Backend/health；bootstrap 失败单独显示。首次快照失败为尚未加载；后续失败保留最近成功值并显示陈旧；仅一个 1Hz 刷新源。

既有双 SQLite v1、DELETE/EXTRA、实例身份/profile 独占锁、CAS/激活恢复、每PLC唯一串行 actor、完整轮 sample/manifest/seq/pending 同事务、有界原字节历史、容量预留与保护维护保持。启动连接/采集意图总为 stopped。缺库、损坏、身份不符、非预期WAL材料仍 fail-closed。receipt 复用 source_documents；没有 DDL、ledger 或依赖升级，见[局部存储说明](src-tauri/src/infrastructure/local_store/README.zh-CN.md)。

限额仍为4PLC、每PLC8组/32DB/4096叶、每组256启用点、周期≥500ms，是准入限额而非现场吞吐承诺。每PLC一个会话复用采集/测试/诊断。产品不能ACK或清pending，上报只留阶段C说明“本地保存，上传未接入”。为journal/系统余量可早于90%停采，保留天数不会删除pending。日志写失败锁存未知区间，修复并重启后才恢复，history/Stop/断开/退出仍可用。SQLite3.46.0 DELETE/EXTRA是有限存储合同，不是WAL修复或硬件断电保证。

## 隔离验证边界

`pnpm build --config vite.validation.config.ts --outDir <绝对临时dist> --emptyOutDir` 继续隔离 env。非默认 debug `local-validation` 保留原固定fixture、绝对tmp路径/owner marker/继承env拒绝/release编译拒绝；不会自动发现源码根 YAML。原CLI/二进制及必需参数保持，不能真实传输、执行任意SQL或ACK。DAA-003普通原生迁入/保存重开证据使用新建归属清楚的tmp env/profile和read gate=false；browser/fixture不替代它。真实PLC/实际profile和YAML迁入、Backend/SMA/DS、C阶段、生产DB/API、现场来源切换、Docker/Git/发布/部署及跨平台签名另行批准。

## 多 DB 源码编辑与标准偏移

在点位与采集组页先保存或取消当前编辑，选择PLC后选取`.db/.udt`。Rust自动识别声明，原区域逐DB显示勾选和实际编号（1–65535）；新编号为空，不从名称/日期猜号。UDT仅作依赖摘要，不填编号。10/20/50分页保持跨页勾选/编号。源正文有变时显式选择原已有目标；仅文件名相同不构成更新身份。

预览弹窗展示完整所选差异、定位诊断、人工配置保留和默认折叠的结构树。关闭零写并保留文件选择；一次显式确认仅把所选完整块作为草稿原子保存，不启用点、不激活、不采集。任一所选致命问题阻断整次提交，可取消局部错误块后导入合法子集；文件边界不安全则整文件阻断。编辑/映射变化、重载、旧ETag或过期/不匹配预览token均需重新预览。

有界语法包括UTF-8/BOM、LF/CRLF原字节保留、多命名DATA_BLOCK/TYPE、VERSION、NON_RETAIN/RETAIN、白名单布尔S7_SetPoint字段属性、STRUCT、无环UDT及一维常量数组（允许负/非零下界）。未知语法/属性/类型、字段歧义、依赖缺失/循环/重复、嵌套/多维数组及超限均拒绝。初值/BEGIN不执行、不作为采样值；不是完整TIA编译器。

重导保留稳定DB/point ID、用户名/备注、组、开关、人工地址值/理由；无变化保留ETag。增叶、类型/顺序/布局依赖变化使整个所选DB的既有地址确认失效。删叶/改叶名、改块名、已有DB改号均阻断并保留原配置。来源为不可变逻辑版本，逐DB冻结UDT闭包；未选DB和其他PLC保留原来源/树/地址。相同字节可跨逻辑source/PLC复用物理归档，不覆盖原归档元数据。既有SQLite历史、active版本及私有YAML回执保持。

“预览标准布局偏移”→“确认非人工偏移”是独立两步草稿操作，弹窗展示路径、旧/建议地址、计算/当前DB长度和人工冲突。Siemens STEP7 V20标准word profile要求完整、明确非优化、闭包来源重证；支持BOOL、BYTE/USINT/CHAR、INT/UINT/WORD、DINT/UDINT/DWORD/REAL、嵌套STRUCT/UDT及一维标量/STRUCT/UDT数组。STRING仍可导入/人工地址，但整DB不推算；优化/未知/不完整布局亦整块拒绝。完整树校核容器/数组padding与DB边界；人工地址不改变理论游标、不批量覆盖，理由保留。仅无人工地址且完整非人工集合确认时更新DB长度。真实PLC地址仍需另行现场校核。

[手写多DB样例与先行布局oracle](src-tauri/tests/fixtures/source-import-multi-db/README.zh-CN.md)记录有限profile。新增可选JSON lineage/binding不需DDL，读取旧v1不会自动写回；新程序读旧数据不等于旧binary能读新元数据，降级另核。来源版本仍计入128来源、16MiB配置及物理写预算，不删除未选来源腾空间。

DAA的机器身份是opaque `point.id`（样本字典也按此ID），`sourcePath`保留PLC原始路径及中文，`name`是可编辑显示名。旧YAML工具的`name`承担运行时key，故不直接移植其ASCII/地址兜底；新导入地址为null。未来面向集成的人可读ASCII key需另定合同。
