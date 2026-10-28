# AIIS Data Acquisition Agent

[English](README.md)

DAA 复用 CU 公共壳，只有一个本地 SQLite runtime。普通 `pnpm tauri dev` 直接打开工作台、PLC 配置、点位与采集组、上报与存储四页，无需 mode/storage 开关。应用Tauri配置统一传递已有 `rust-snap7-driver`，普通命令已包含S7驱动。Snap7是S7通信实现的编译能力，不是选择DS或真实PLC的运行参数；启动仍停止。

```bash
pnpm install --frozen-lockfile
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml -- --check
pnpm tauri dev
```

来源为 CA 冻结 receipt；[DAA PLAN](PLAN.zh-CN.md) 管实施，[AW PLAN](../PLAN.zh-CN.md) 管跨工程阶段。[DAA-003 r1](plans/DAA-003-sqlite-only-startup/spec.md) 管 SQLite 唯一入口和迁入；[DAA-002 r2](plans/DAA-002-local-acquisition-loop/spec.md) 管既有本地采集基线，其 QA 与 Human Owner 最终验收仍是独立任务事实。这些说明不授权现场切换、发布或部署。

## 配置权威与启动

源码开发只读取本应用根 `.env`，高级进程绝对 `DAA_ENV_FILE` 可改选一个可读UTF-8普通文件；显式错误立即拒绝，不回退。`DAA_PROFILE_DIR`按非空进程 > 所选.env非空值 > 原独立应用本地数据目录选择；空白表示未设置。路径须绝对、无父目录穿越及既有symlink，不展开`~`、`$VAR`/`${VAR}`或执行shell，不扫描cwd/父目录/CA/其他应用。相同键首项生效。Vite不加载.env，Rust不转储其正文。

手工在 `automation-world/data-acquisition-agent/` 将 `.env.example` 复制为 `.env`（已有文件不覆盖，由Owner核对），只按需填 `DAA_PROFILE_DIR`。随后每次仅执行 `pnpm tauri dev`；具体联调路径见[手册](JOINT_TEST_GUIDE.zh-CN.md)。dev/build不会自动隔离数据，空键不等于新空目录；安装包.env发现与分发不在本合同内。旧UTC/未知profile仍写前拒绝，保留原件，迁移另批。

`local-acquisition-v1/config.sqlite` / `runtime.sqlite`拥有PLC端点、点位/组/周期、存储与历史，均经UI配置。连接、启采、暂停与断开走工作台显式动作；保存/激活/启动/重开均不自动连接或启采，瞬时connected与运行意图不恢复。普通native无需.env读授权。所选.env的旧 `DAA_PLC_READ_ALLOWED` 无论true/false均忽略，可由Owner一次删除；高级同名进程键确实缺失才默认允许后续UI动作，合法true仅不额外禁止，false、空/空白、非法、不可解码均禁止读取。进程deny不被文件true覆盖，其余启用/地址/激活/容量/日志/时间保护保持，没有新增SQLite全局读取开关。

旧 YAML 运行模式、直库 writer、Backend health、授权自检已退役，旧 IPC 不再注册。`--ca-*` 与原 runtime 二进制在配置/锁之前返回结构化 `legacy_entry_retired` / exit2，不提供新的 SQLite headless 宿主；运维流程须去掉旧脚本。所选 env 文件的 `DAA_RUNTIME_MODE=legacy_snapshot` 作为旧残留忽略并一次提示键名；进程显式该值返回 `legacy_runtime_retired` / exit2，请删除覆盖后普通启动。空值/local_sqlite 接受，其余非空值拒绝。其它旧 DB/write/autostart/endpoint/Backend/log-path 值不再消费或决定业务，真实 `.env` 不改写。Vite 使用 `envDir:false`，不消费旧 `VITE_DAA_*` 业务输入。

## YAML常驻迁入退役

DAA-007 r2将已完成的迁入退出普通bootstrap、engine、reload和保存链。旧 `DAA_PLC_CONFIG_PATH` / `DAA_PLC_SNAPSHOT_POLICY_PATH` 只按残留键名忽略，不构造locator、不探测/读取/散列YAML，也不再为新空profile迁入 `PLC_1` 或写receipt/ETag。正常四页无迁入故障入口、弹窗或重试。旧YAML样例和算法仅作为历史材料/测试保留，不再是活动配置。

既有SQLite私有receipt、source archive及保留前缀继续受保护，不清理或重编码。具名兼容摘要仅在显式调用时只读本profile SQLite，返回真实历史状态且 `retryAllowed=false`；兼容retry写前返回 `yaml_retry_forbidden`。业务配置权威仍是UI+SQLite，普通编辑导入仅显式接受 `.db/.udt`，经结构/地址审阅和分组后另行激活、连接与启采。[最小DB/UDT样例](src-tauri/tests/fixtures/source-import-minimal/README.zh-CN.md)仍是手写受控清单，不证明真实TIA/PLC兼容。

### 历史仓内示例（已退出普通启动链）

以下是保留的[plc_points.yaml](config/plc_points.yaml)及[旧policy](config/plc_snapshot_policy.yaml)三点脱敏示例说明，文件没有采样值或历史。DAA-007 r2普通启动不构造locator、不读取/散列/迁入这些文件，真正空profile保持空业务配置；旧YAML键不改变该行为。

| 默认示例 | 值 |
| --- | --- |
| PLC / 连接候选 | `PLC_1`，`127.0.0.1:102`，rack 0 / slot 1 |
| DB / 组 / 旧读取窗口 | DB1，`example_group`，start 0 / size 12，3 点；窗口不是完整 DB 长度证明 |
| 点 1 | `example_value`，旧类型 `Real`，offset 0 |
| 点 2 | `example_status`，旧类型 `Bool`，offset 4 / bit 0 |
| 点 3 | `example_counter`，旧类型 `DInt`，offset 8 |
| 3 点的退役策略 | raw/latest=true，raw_policy=`every_sample`；仅白名单归档，不转成新采样/上报/直库规则 |

## 本地采集与恢复

四页只有 `useLocalAcquisitionConsole` 一个 owner；纯 shell 只管导航/主题/语言（`daa.theme` / `daa.locale`）。浏览器无桥预览不假保存、不请求 Backend/health；bootstrap 失败单独显示。首次快照失败为尚未加载；后续失败保留最近成功值并显示陈旧；仅一个 1Hz 刷新源。

新空profile使用双 SQLite v2；DELETE/EXTRA、实例身份/profile 独占锁、CAS/激活恢复、每PLC唯一串行 actor、完整轮 sample/manifest/seq/pending 同事务、有界原字节历史、容量预留与保护维护保持。启动连接/采集意图总为 stopped。缺库、损坏、身份不符、非预期WAL材料仍 fail-closed。receipt 仍复用 source_documents；DAA-007仅对新空库创建v2 schema/ledger，无旧库DDL/迁移和依赖升级，见[局部存储说明](src-tauri/src/infrastructure/local_store/README.zh-CN.md)。

限额仍为4PLC、每PLC8组/32DB/4096叶、每组256启用点、周期≥500ms，是准入限额而非现场吞吐承诺。每PLC一个会话复用采集/测试/诊断。产品不能ACK或清pending，上报只留阶段C说明“本地保存，上传未接入”。为journal/系统余量可早于90%停采，保留天数不会删除pending。日志写失败锁存未知区间，修复并重启后才恢复，history/Stop/断开/退出仍可用。SQLite3.46.0 DELETE/EXTRA是有限存储合同，不是WAL修复或硬件断电保证。

## 隔离验证边界

`pnpm build --config vite.validation.config.ts --outDir <绝对临时dist> --emptyOutDir` 继续隔离 env。非默认 debug `local-validation` 保留原固定fixture、绝对tmp路径/owner marker/继承env拒绝/release编译拒绝；不会自动发现源码根 YAML。原CLI/二进制及必需参数保持，不能真实传输、执行任意SQL或ACK。DAA-003历史原生迁入/保存重开证据使用其自有tmp env/profile和read gate=false；r2已退役普通迁入，browser/fixture不替代它。真实PLC/实际profile和YAML迁入、Backend/SMA/DS、C阶段、生产DB/API、现场来源切换、Docker/Git/发布/部署及跨平台签名另行批准。

## 多 DB 源码编辑与标准偏移

在点位与采集组页先保存或取消当前编辑，选择PLC后选取`.db/.udt`。Rust自动识别声明，原区域逐DB显示勾选和实际编号（1–65535）；新编号为空，不从名称/日期猜号。UDT仅作依赖摘要，不填编号。10/20/50分页保持跨页勾选/编号。源正文有变时显式选择原已有目标；仅文件名相同不构成更新身份。

预览弹窗展示完整所选差异、定位诊断、人工配置保留和默认折叠的结构树。关闭零写并保留文件选择；一次显式确认仅把所选完整块作为草稿原子保存，不启用点、不激活、不采集。任一所选致命问题阻断整次提交，可取消局部错误块后导入合法子集；文件边界不安全则整文件阻断。编辑/映射变化、重载、旧ETag或过期/不匹配预览token均需重新预览。

有界语法包括UTF-8/BOM、LF/CRLF原字节保留、多命名DATA_BLOCK/TYPE、VERSION、NON_RETAIN/RETAIN、白名单布尔S7_SetPoint字段属性、STRUCT、无环UDT及一维常量数组（允许负/非零下界）。未知语法/属性/类型、字段歧义、依赖缺失/循环/重复、嵌套/多维数组及超限均拒绝。初值/BEGIN不执行、不作为采样值；不是完整TIA编译器。

重导保留稳定DB/point ID、用户名/备注、组、开关、人工地址值/理由；无变化保留ETag。增叶、类型/顺序/布局依赖变化使整个所选DB的既有地址确认失效。删叶/改叶名、改块名、已有DB改号均阻断并保留原配置。来源为不可变逻辑版本，逐DB冻结UDT闭包；未选DB和其他PLC保留原来源/树/地址。相同字节可跨逻辑source/PLC复用物理归档，不覆盖原归档元数据。既有SQLite历史、active版本及私有YAML回执保持。

“预览标准布局偏移”→“确认非人工偏移”是独立两步草稿操作，弹窗展示路径、旧/建议地址、计算/当前DB长度和人工冲突。Siemens STEP7 V20标准word profile要求完整、明确非优化、闭包来源重证；支持BOOL、BYTE/USINT/CHAR、INT/UINT/WORD、DINT/UDINT/DWORD/REAL、嵌套STRUCT/UDT及一维标量/STRUCT/UDT数组。STRING仍可导入/人工地址，但整DB不推算；优化/未知/不完整布局亦整块拒绝。完整树校核容器/数组padding与DB边界；人工地址不改变理论游标、不批量覆盖，理由保留。仅无人工地址且完整非人工集合确认时更新DB长度。真实PLC地址仍需另行现场校核。

[手写多DB样例与先行布局oracle](src-tauri/tests/fixtures/source-import-multi-db/README.zh-CN.md)记录有限profile。新增可选JSON lineage/binding不需DDL，读取旧v1不会自动写回；新程序读旧数据不等于旧binary能读新元数据，降级另核。来源版本仍计入128来源、16MiB配置及物理写预算，不删除未选来源腾空间。

DAA机器身份仍是opaque `point.id`，历史样本字典亦按ID。`name`现为ASCII技术名称，`sourcePath`保留原路径及中文。无可选JSON `nameMode`的存量仍是legacy，只有明确选中才转换；读取/重启/无关保存不转换。新合法结构路径立即成名；中文、数组、标点及超长路径停用/pending且name为空，既有地址确认在同一草稿事务中生成地址名。manual为显式ASCII人工改名；完整PLC namespace包含停用/legacy/manual，最终冲突整次拒绝。enabled pending阻断激活，停用pending和未选legacy保持原准入边界。

点位页按稳定ID勾选，跨页保留（10/20/50），预览旧→新和冲突后显式确认；取消零写、保留选择。原编辑器预览有限用户字段patch并与派生名一起保存；原偏移确认同时成名，无第三次确认。token300秒过期并绑定输入/ETag。None/manual在重导、无关地址/类型变化后保名；直接受影响的managed遵循固定profile。旧历史/receipt/active版本原bytes不改，新元数据的旧binary降级需另证。

[共享导入核心](../shared/tia-import-core/README.zh-CN.md)只保留一套纯parser/展开/布局/命名，DAA保留不可变源证明、闭包、ID及SQLite/CAS。没有DDL/第二技术key或YAML运行模式。共享不等于DS已实现或阶段B完成；还需DS独立接受的协议基线、另批DAA–DS读取至SQLite联调后，才整体接受B并推进C。

普通`pnpm tauri dev`使用本仓package→Tauri beforeDevCommand→Vite15191与`src/main.ts`及本仓`src-tauri`入口。验收不自动复制临时代码或更新安装包。旧`yaml_migration_*`日志仅属于历史迁入；r2普通启动不再产生迁入事件。`runtime_started` stopped和`runtime_stopped` clean描述启动意图和正常关闭，不表示失败。

## 阶段 B 联调操作手册（试行）

[试行版手册](JOINT_TEST_GUIDE.zh-CN.md)与[DAA-007 r2 spec](plans/DAA-007-ds-joint-validation-and-time-contract/spec.md)明确本次有限DS采用基线、隔离启动及M01–M09。r2已精确获批，保留r1时间与门禁整改，新增启动/profile与YAML退役增量；DEV定向验证记录见[tasks](plans/DAA-007-ds-joint-validation-and-time-contract/tasks.md)。Owner原生联调、闭库对账、新fresh Verification与最终验收仍分别待发生，阶段C继续另批。

新版仅初始化新空profile：两库user_version/metadata/schema_migrations=2，time_profile=`asia-shanghai-rfc3339-ms-v1`；样本及manifest=2，配置/context及IPC envelope仍为1。日历时间固定上海毫秒`+08:00`，savedAt为同轮持久化事务内生成时间；stdout保留纳秒、文件日志保留毫秒。旧UTC v1、未知/缺失合同、单库或身份异常在profile锁、RW连接、恢复、迁入及持久日志之前只读拒绝；合格v2/新空才取得锁并复核，漂移拒绝可能已留下锁文件，但未RW业务库。拒绝诊断壳给出`time_profile_unsupported`，业务动作不可用。原配置/历史不迁移、不旁建替代库；旧profile继续使用原兼容版本，迁移与降级另批。

历史、陈旧快照和最老待传时间按上海`YYYY-MM-DD HH:mm:ss`显示。历史筛选以上海墙上时间解释，终止秒包含`.999`，原详情JSON/SHA保持。仅历史表提供普通列拖拽、最小宽、横滚、本机应用/表/稳定字段隔离偏好和恢复默认，不写SQLite业务配置。联调沿用手册原Owner合成profile，由Owner一次手工填写应用根.env，之后正常短命令启动；默认profile不属于本次操作范围。
