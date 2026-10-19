Task ID: DAA-003
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved exact DAA-003 r1 on 2026-10-19; hand the unchanged approved scope to actual Development through coordinator /root, then new fresh-context Verification and Human Owner final acceptance; DAA-002 final acceptance remains pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA 普通原生启动直接进入唯一 SQLite 配置与采集界面，并将旧 YAML 的有效配置一次性迁入停用草稿
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: aiis-ics-arch::DAA-003 r1 exact scope approval -> Development -> new fresh-context QA / Verification -> Human Owner final acceptance
Related Task: aiis-ics-arch::DAA-002 r2; aiis-ics-arch::DAA-001 r1; aiis-ics-arch::ARCH-AW-003 r3

# DAA SQLite 唯一入口与旧配置一次性迁入

## 1. 当前效力与审批对象

**最新批准与当前效力（2026-10-19，Asia/Shanghai）：** Human Owner 已明确批准精确 DAA-003 r1，获批 draft SHA-256 为 `790563fb4cbd58690f4a63510d02d7148c19928649c7e65073e8509b1a906bf4`。原话由唯一 active lifecycle coordinator `/root` 真实传递：

> 可以，批准 DAA-003 r1，按 spec 完成 SQLite 唯一入口、旧 YAML 一次性迁入机制和独立核验。已有 SQLite 配置和历史不要覆盖；阶段 C、后端和 SMA 暂不做，真实配置迁入、真实 PLC、生产数据库/API 和现场切换不在本次范围。

当前状态为 `owner_approved`，G0 范围批准已满足。本次只补状态、批准原话和当前 handoff，R01–R12、AC01–AC12、61 个实现路径、10 个协调索引及全部技术/风险/排除条款逐字保持。下文起草时的 `draft`、待审阅/待批准、§6 G0 的“当前 pending”及旧 handoff 原文是历史时点，批准状态以本段和文首为准；不改变技术合同或串行顺序。实际 Development/tasks/实施/self-check/developer_handoff、新 fresh-context Verification 及 Human Owner 最终验收在此 PM 批准记录时均未发生。DAA-002 终验仍独立 pending，本批准不提供其终验、阶段 C、真实配置/PLC/生产库/API 或现场切换权限。

2026-10-19（Asia/Shanghai），Human Owner 先要求：

> 那就让 DAA 用 pnpm tauri dev 默认进入新版 local_sqlite 模式，旧模式保留为可选兼容，不用每次手动切换配置。先出调整 spec，批准后再改代码。

在任何新 spec 形成之前，最新指示改为：

> 旧的不要了吧，基于yaml的模式不要了，不过yaml里面如果有东西你就提取出来存，没有就算了。

后一决定覆盖“保留可选兼容”；“先 spec、批准后实施”继续有效。本 r1 只有一个方案：**普通 `pnpm tauri dev` 直接进入现有新版 SQLite 界面；DAA 不再提供可选择的 `legacy_snapshot` / YAML 运行模式。已有 SQLite 优先；旧 YAML 仅作首次空实例的一次性迁入来源。迁入不激活、不连接、不启采。**

本文件为 `draft`，Human Owner 尚未批准本 Task ID / Revision。当前 PM 唯一仓内写入是本文件；没有创建 tasks/checklist、改产品/配置、执行构建/测试/SQL/PLC/API、启动或操作窗口。唯一 active lifecycle coordinator 为 `/root`，实际命名 PM 为 `/root/daa_sqlite_only_pm`。消费 `.codex/agents/pm.toml` 的 `gpt-6.1-sol / max` 仅是配置证据；profile 为 `contract_only`，不宣称平台 ACL、强制路由或额外运行遥测。

本任务是独立 `root`，没有 Parent Task ID。DAA-002 r2 当前为 `qa_passed`、Human Owner 最终验收 **pending**；本次新方向不是其最终验收，不改写其 spec、失败原文、QA 或 76 份原样本。DAA-003 使用它的当前源码和原始证据作技术基线，拥有独立批准链；无需凭空等待 DAA-002 的终验才提交本新范围，也不能继承其范围批准或 QA。

需 Human Owner 一并审阅的具体取舍：

1. 退出旧运行模式及旧直库/health/授权自检路径；旧 headless 和旧 CLI 只保留明确拒绝的退役入口，本任务不开发 SQLite headless 宿主。
2. 旧 `.env` 文件内的 `DAA_RUNTIME_MODE=legacy_snapshot` 作为旧模板残留忽略并提示；**进程环境显式指定该值则非零拒绝**并说明移除该变量、使用普通入口。这样旧模板不阻挡日常启动，明确要求旧模式也不会静默转成另一模式。
3. 迁入全部可表示的 PLC/DB/点/组；旧地址未确认，PLC/组/点全部停用。旧 raw/latest 策略只归档说明，不转成新采样或上报规则。
4. 不升级 SQLite/ORM/依赖，不改双库 schema。使用现有配置库中的有界私有迁入记录；已有非空本地实例完全不读取或覆盖 YAML。失败后只显式重试，成功或空来源跳过后不在每次重启重读。

## 2. 已消费依据与当前源码事实

PM 已读取根 AGENTS、README/PLAN 双语、canonical lifecycle workflow、实际 pm TOML；AW/DAA 的 README/PLAN 双语、DAA `src/app/README.*`、`local_store/README.*`，及 DAA-002 已形成完整三文件。作用域检索无更近 AGENTS。使用 `aiis`（BLUEPRINT/CONTRACTS/运行日志基线）和 `project-governance`；只读核对入口、旧 YAML 合同、现行单 PLC 导入、SQLite/前端接线及 DAA 详细设计的配置、分阶段边界。本轮不重新联网评估 SQLite，不把旧评估写成新的运行结论。

入口：[根契约](../../../../AGENTS.md)、[canonical workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)、[DAA 说明](../../README.zh-CN.md)、[DAA 计划](../../PLAN.zh-CN.md)、[DAA 详细设计](../../../../docs/AIIS_DAA_Detailed_Design.md)、DAA-002 的 [spec](../DAA-002-local-acquisition-loop/spec.md) / [tasks](../DAA-002-local-acquisition-loop/tasks.md) / [checklist](../DAA-002-local-acquisition-loop/checklist.md)。尚未形成的本任务后续角色文档不提前建链接。

当前 HEAD 是 `f85bea8bbf36b491968c3dc9a839518a1ed434a8`，仓内存在大量先前 dirty/untracked。实际交付起点是当前字节，不能以 HEAD 代替。主协调基线为 `/private/tmp/daa-003-spec-p8k4220b/baseline.json`：1663 个路径，当前只允许新 spec 与主协调的 10 个索引；PM 辅助审计只写其 `pm/` 子目录。Development 获批后须固定自己的完整 before/after，不恢复、不认领外来改动。

| 仓根相对依据 | 本轮核实的 SHA-256 / 事实 |
| --- | --- |
| `automation-world/data-acquisition-agent/plans/DAA-002-local-acquisition-loop/spec.md` | `681b912b9920fa9ecc8ff6c22c23d2e9fb9a4aa31a761589ee1290173846681a`；已批 r2，原默认 legacy 合同是历史范围，不反改。 |
| 同 bundle `tasks.md` | `d5847fb57ded32e2419e508d0c47e74ccd3f06a11e7e8e920b19fa5e704a69a6`；最新文档交接及所有返工历史。 |
| 同 bundle `checklist.md` | `6427e2c3030d33b255bc005625b03651a4fdfc5618721ee946228e1dc731ca37`；QA4 AC01–AC20 通过，F-001–F-004 解除，Owner 终验 pending。 |
| `docs/AIIS_DAA_Detailed_Design.md` | `20071f25c374f40ee4600bffda4aef13f37bb86a82c2a6cd1f19e2580370a576`；完整源、配置/激活和 B/C 分界继续作为依据；本文不改其正文。 |
| DAA `src-tauri/src/config/local_bootstrap.rs` | `f5a711e1eb4eccb267e037532d61b4b0d86843f7dad7e81731fbb0f55ee533a8`；缺省 legacy；local 需额外 storage=true，且旧 env 门禁/endpoint 可令其拒绝。 |
| DAA `src-tauri/src/lib.rs` | `50c98ad70c9be213ce35283f284c6716457ed74e86c5e4fccc2cd78cbe907041`；新旧服务共同注册，旧 autostart、CLI/headless 分支仍存在。 |
| DAA `src/services/localAcquisition.ts` | `131f73f98d77b55c4e48e362938d08840d35c7f471b317e6622b7445f1c6af78`；浏览器 bootstrap 回落 legacy。 |
| DAA `src-tauri/src/infrastructure/tia_source.rs` | `3a596853246d1fa79b96e57ca8cfafe448fe9212c49a160ef729ed1fb6727cc6`；现 YAML helper 只接收恰好一台 PLC，未建组、DB 不完整、地址未确认。 |
| DAA `src-tauri/src/infrastructure/local_store/configuration.rs` | `0d2bf849446c0958744d7a7da8dec863a6482be2e789b0e422c3b458ac75a9e1`；已有 CAS 与 source_documents，裁剪会删除未引用 source，迁入记录必须显式保护。 |
| DAA `src-tauri/Cargo.toml` / `Cargo.lock` | `38dab0b0b39d6b01150aa28ca8aaca4852aba713fe98f5923b6ce828b3cddbd2` / `fe840bec96fd9348f9230e67368b72f6971827cd3f888ef4173b4e7f0b0ebefc`；default feature 空，Snap7 仍需显式 feature。 |

真实旧合同不是一组已选采样点摘要：

- `config/plc_points.yaml` 是顶层 PLC key 的 mapping；每台含 `ip/port/rack/slot`、`point_count`、多个 `groups`；组含 `name/db_number/start/size/point_count/points`；点含 `name/type/offset/bit/length/desc/readable/writable` 的适用字段。同一 PLC 可有多个 DB/组。没有完整 TIA DB/UDT 声明，`start/size` 是旧读取窗口，不是整个 DB 长度证明。
- `config/plc_snapshot_policy.yaml` 是同形 v2 mapping；含 `snapshot_policy_version=2`、`groups` 的 `name` 或 `group_name`、`db_number`、点 `name/raw_enabled/raw_policy/latest_enabled`。旧策略接受 `every_sample/on_change/hourly`，不等同 B 的全结果 pending 合同。
- 旧 `plc_points.rs` 有扫描/样本 limit/全局 endpoint override；旧反序列化模型会忽略部分字段；现 `tia_source::legacy` 会拒绝多 PLC、按组重建点、把 DB 长度设为 65536 且不完整。**这些函数不能直接承担无损的自动迁入合同。**
- 当前 `App.vue` 同时实例化 local owner 与禁用的旧 owner，借旧 owner 提供导航/偏好；四页有双分支，Layout/Sidebar 依赖旧 RuntimeSnapshot。仅更改两行 env 不能完成本任务。

## 3. 包含与排除范围

包含普通原生启动统一、旧入口退役、有限 YAML 发现/严格解析/全部候选转换、一次性迁入与诊断、复用 schema 的受保护记录、四页 local owner 和无桥浏览器状态、必要双语说明及定向验证。

不实施 C 上传/ACK/Backend/SMA/DS 或跨端合同，不增加 PLC 写入、现场校核、TIA 完整编译/复杂结构推算、通用迁移框架、备份恢复产品、系统凭据库、自动服务/headless 新宿主、长期负载/跨平台签名打包。CA 冻结、CU 公共源码、SMA/backend/frontend-js/tools、已验收设计及其他 bundle 均保持。

批准本 r1 后允许的执行环境仅为新建、明确归属的系统 tmp env/profile/YAML 夹具/SQLite 与本机开发启动；**真实 YAML/.env/profile 的读取迁入、实际生产库/API/PLC、来源切换、Docker、Git 提交/refs/推送、发布、部署或回滚仍需另行授权。** 产品可实现未来的自动迁入行为，但本任务不得拿用户当前实际配置或运行窗口演练。DAA-002 Owned Validation 窗口、profile、fixture 与 76 样本不作为本任务可写/可迁入目标。

## 4. 编号需求

### R01. 独立批准、字节基线和最小实施

精确 DAA-003 r1 获批前只起草本 spec；批准后实际 Development 才创建自己的 tasks。固定批准 SHA、当前源码/依赖/保护面和 DAA-002 三文件 SHA；技术基线是其 QA4 当前字节及原始行为证据，不重新申请阶段 B 范围批准或重复全部 B0–B6。只交本任务实际增量，遇 allowlist/需求/风险变化回 PM 新 Revision。DAA-002 终验仍独立 pending。

### R02. 普通入口与旧 env 的确定行为

普通 `pnpm tauri dev`、普通主二进制及 `pnpm tauri:dev` 均只装配本地 SQLite；不要求设置 runtime mode 或 storage 开关。`local_sqlite` 可继续作为只读 bootstrap 标识，不保留双模式 enum/切换器。启动定位仍只消费自身根 `.env` 或显式绝对 `DAA_ENV_FILE`，不搜索 cwd/父目录/仓根；profile 仍为既有 DAA 独立目录或显式绝对 `DAA_PROFILE_DIR`。保留当前定位优先级，补充来源标识用于下表，不借此重写 dotenv。

| 输入 | 新行为 |
| --- | --- |
| 未设置 mode/storage；env 不存在 | 默认 SQLite，正常初始化或打开本地库，不报缺少配置。 |
| 选定 env 文件内 `DAA_RUNTIME_MODE=legacy_snapshot` | 识别为旧模板残留，忽略该退役值、一次提示，进入 SQLite；不修改文件。 |
| 当前进程环境明确 `DAA_RUNTIME_MODE=legacy_snapshot` | 启动前返回 `legacy_runtime_retired`、exit2；说明删除该环境覆盖后普通启动，YAML 由首次迁入处理；不转入旧运行路径。 |
| mode 缺省/空/`local_sqlite` | SQLite；其他非空值明确 `runtime_mode_invalid`，无静默 fallback。进程环境高于选定 env 文件。 |
| `DAA_LOCAL_STORAGE_ENABLED=false/true` 或旧 DB/write/autostart/endpoint/authorization/Backend/日志输出路径键残留 | 均失去业务作用，按退役键名汇总一次提示；不阻挡普通 SQLite 启动，不读取连接串/口令值、不建立外部连接，不覆盖 SQLite。 |
| `DAA_PLC_READ_ALLOWED` | 唯一保留的现场读取总门禁，缺省 false；存在时仍按现有优先级。即使 true 也不触发启动连接/启采。 |

迁入定位用旧的两个 YAML 路径键，含义限 R04，不是长期运行配置。其它业务参数、endpoint、周期、保留/额度均以 SQLite 为权威。`.env.example` 只说明必要定位、读取门禁和一次性迁入路径；移去退役业务开关，不复制/改写真实 `.env`。前端普通 Vite 配置设 `envDir:false`，不再将旧 `VITE_DAA_*` 当运行来源；端口/alias/CU 输入保持。

### R03. 旧执行图退役

`lib.rs` 只构造 LocalEngine、local 日志/退出与具名 local IPC；移除旧 autostart/快照/DB/授权服务的装配。旧 PLC collection/read/persistence、diagnostic snapshot 和 `get_runtime_snapshot` 不再注册，调用由 Tauri 明确 unknown-command 拒绝；文档列出新配置/迁入入口，不设置兼容转发。

`--ca-*` 主程序参数及现有独立 runtime 二进制在加载 AgentConfig、获取 profile 锁或调用旧服务之前，以结构化 `legacy_entry_retired`/exit2 拒绝，给出普通桌面入口和 YAML 迁入说明。既有 `plc:collect-*` / `plc:runtime` 脚本可沿用到这些拒绝入口；它们不再提供采集。没有自动替换成新的后台宿主。

具体退役方式见 §5：Rust 旧 command/service/domain/infrastructure 模块从 registries 去注册，源码原样留存但无产品可达路径；**不启用新的 legacy feature**。旧 frontend owner、旧 IPC/health facade 和旧授权 view/PLC picker 删除；四页移除旧分支。纯 CU 适配、主题/语言、`.db/.udt` 解析、local decode/layout/managed_s7、local ledger/容量/日志继续复用。YAML 解析代码只存在于一次性迁入 adapter；`tia_source` 的单 PLC YAML helper 退下，正常源导入只接 `.db/.udt`。

### R04. 一次性发现与“已有 SQLite 优先”

顺序必须是：参数/定位检查 → profile OS 独占锁 → 当前双库身份/完整性与恢复 → 判断迁入资格 → 必要的一次性解析/事务 → 读取草稿/active → 安装 stopped actors → GUI。所有判断在同一 owner 下，第二进程不得先读源/生成候选再等待锁。

自动迁入只对首次空实例执行。“空”同时要求：草稿对象/来源全空且存储策略仍为初始默认；没有任何不可变配置版本、active/previous/应用中 token、plc_sources、配置解释、cycle/sample/delivery/reference。仅生命周期事件/初始 metadata 不使实例非空。用户保存过的不同存储策略也算已有配置。非空实例先返回 `existing_sqlite_preserved`，不读取/计算 YAML hash、不改 draft ETag 或原始数据；正常 stopped 启动及原生命周期记录仍可发生。

首次空实例的发现固定为：继承进程内对应非空 `DAA_PLC_CONFIG_PATH` / `DAA_PLC_SNAPSHOT_POLICY_PATH` → 选定 env 文件同名非空值 → 自身根 `config/plc_points.yaml` / `config/plc_snapshot_policy.yaml`。相对路径锚定 DAA 自身根，不锚定 profile/env 所在目录；显式绝对路径可用。一次只读取这两个文件，不扫描 CA/父目录/其他 YAML，不解释 URL，不读取 `.env` 为迁入内容。拒绝 symlink、目录、非 UTF-8、读权限/变化竞态，给出诊断且不覆盖源。读前后校文件身份/长度/修改事实，来源变更则整次失败，不混合两个时点的文件。

缺失文件、零字节、仅空白/注释或 YAML null/空 mapping/空 sequence，归为 `skipped_empty`。有 PLC 连接/合法条目即有配置，不能因无点或无 enabled 点当空；字段拼错、非空错误根形、语法错、unsupported、超限不能记空。空/缺失结果持久记录后不在重启重扫；后来新增/修复文件使用 R06 的显式重试。policy 单独存在且合法时只归档，不凭策略制造 PLC/点。

### R05. 多 PLC、点/组与旧策略转换

使用严格 schema-aware 解析，核全部顶层 PLC、全部组/DB/点、重复 key/标识、类型/数值范围、结构限额；不调用旧样本扫描/limit，不只取首台 PLC。每个输入项都必须有“已转候选 / 只保留为旧语义 / 明确阻断”的归属及计数，不能过滤掉不可读/未启用/未选点后报完整成功。

| 旧内容 | SQLite 中保存与边界 |
| --- | --- |
| PLC key、ip/port/rack/slot | 全部生成稳定 plcId、显示名与候选连接值；缺少 port/rack/slot 时只使用现有 local 表单默认 102/0/1 并明确标为缺失待核，不冒称旧文件已配置。无效/缺失必需地址保留诊断，不猜主机或取旧全局 endpoint 覆盖。 |
| 组名、db_number、start/size、point_count | 每旧组有稳定 groupId，建立实际点归属，组 disabled，周期使用 local 默认 1000ms。start/size/计数保留在来源说明中，核不一致并提示；不把窗口设为完整 DB 长度。 |
| 同一 PLC 的多个 DB/组/点 | 按 PLC+DB 号建立候选 DB；点通过来源 PLC/组/序号/名称路径标识，保留跨组同名的来源，歧义不合并。重复同一语义点/组或无法唯一映射则阻断整份候选，不任选其一。 |
| type、offset/bit/length、desc/name | 保留类型/说明/原地址与旧长度作为候选及来源。受支持类型按明确大小写映射；旧 Date_And_Time、不足长度的 String 等本地不支持者完整保留为 disabled 点和诊断，不伪造支持。 |
| readable/writable/旧 enabled | 只作旧语义说明；全部 PLC/组/点 `enabled=false`。任何 writable、旧自动启动或旧勾选均不产生权限；不得导入写入能力。 |
| 完整 DB/UDT 不存在 | DB `complete=false`、`flat=false`，不制造结构树/平铺证明。地址全部 `confirmed=false`、来源为旧配置待核，不能辅助推算或采集。DB 窗口边界只供比对；后续使用既有 `.db/.udt` 编辑导入、差异与地址确认流程。 |
| snapshot policy v2 | 全部 raw/latest 选择、every_sample/on_change/hourly 及与点匹配结果作为退役策略归档/诊断；不转成点 enabled、第二套上报选项、丢帧策略、ACK、保留规则或直库 writer。 |
| 旧额外业务开关、未知字段或 credentials | 不执行、不复制 `.env`/凭据。未知字段给出位置和“未转换”诊断，不保存其值；原文件原样保留。非空未知根形/错误类型/非法策略版本/不明确映射阻断候选提交，不能宽松忽略后报迁入成功。 |

各 PLC/组/DB/点/源的 UUIDv4 在成功事务中一次固定，receipt 保存来源路径到 ID 的映射；改名/重启不重分配。不会伪造完整 DB、自动激活或打开一个连接。已有 DAA-002 的完整 TIA 解析/推算支持矩阵不扩大；后续编辑导入若不能唯一对上旧候选，显示差异并显式处理，不按同名静默认领 ID。

多 PLC 候选受现行上限：4 PLC、每 PLC 8 组/32 DB/4096 叶、配置 16MiB。超过任一上限，**整份候选不写草稿**，报告实际数量/上限/来源路径；不取前四台或前 N 点。语法/结构无法转换时同样保持空草稿可编辑。合法但不支持采集的点可完整停用保存，必须明确 `imported_with_diagnostics`，不等于可以激活采集。

### R06. 有界 receipt、事务、重试与幂等

不新增表、索引、DDL、user_version 或 configuration/sample schema。使用现有 config.sqlite `source_documents` 的**单个服务私有记录**保存 `yamlMigrationVersion=1` 的归档/receipt；名称使用固定保留前缀 `__daa_yaml_migration_v1__`，行 ID 仍是 UUIDv4，content 为版本化 JSON、sha256 覆盖其规范字节。私有记录不进入可编辑 Configuration.sources；普通 save/import 不能创建/改写该前缀。所有 SQL 仅在新的局部 repository 文件，服务/command 不构造 SQL。配置 source 裁剪显式保留这条记录，不借保留记录更改历史 source。

该记录只保存旧配置的白名单投影、原文件 SHA-256/字节数/发现来源、状态、诊断摘要、attemptId、固定 ID 映射、提交 ETag/时间。**不归档真实 `.env`、密码/token/连接串或未知字段的值**；原 YAML 始终保留，归档不是原文件备份。物化的逐 PLC 来源文本来自同一白名单投影，保留原文件 SHA 关联，不把重编码文本 SHA 冒称原文件 SHA。客户端只获得有界摘要/定位信息，不返回完整源正文或秘密值。

硬限额：每 YAML ≤1MiB，合计 ≤2MiB；解析深度≤16、总节点≤100000，拒绝 alias/tag/多文档等不需要的展开形式。receipt 及白名单归档规范编码合计≤8MiB，摘要/诊断/ID map 计入其中；单次诊断详情最多200项并明确总数和省略计数，不截断配置来满足限制。文件超限不整份读入，记录 size 与 `hashUnavailable=source_limit`，不伪造 SHA。只保留一个最新失败/空结果及最终成功记录，不建立无界迁移历史；重试结果替换私有记录，成功后不再替换成功归档。既有有界日志保留尝试摘要。

候选、必要来源行、私有 receipt、draft 新 ETag **同一个 config.sqlite 短事务**提交；事务开始后再次核“空资格”、expectedEtag、expectedAttemptId，profile 锁不能代替 CAS。写前计入现有 64MiB 配置与 journal/系统余量预算；失败全回滚，不显示已迁入。runtime.sqlite 不写来源身份/样本/active，不跨双库承诺整体原子。

状态至少有 `imported`、`imported_with_diagnostics`、`archived_policy_only`、`skipped_empty`、`failed`；非空实例的 `existing_sqlite_preserved` 可只读计算，无需为了状态给旧实例新增记录。坏语法/不支持根形/超限/读写失败均明确 failed；不能吞成 empty。receipt 成功后重启不再访问 YAML，即使源已被改/删也以 SQLite 为准；用户后来清空草稿不触发自动重新迁入。

GUI 增加具名 `daa_get_yaml_migration`（有界只读摘要）与 `daa_retry_yaml_migration`（只针对 failed/skipped_empty/archived_policy_only、仍为空的实例，带 expectedEtag/expectedAttemptId）。重试从相同 bootstrap 发现的两个固定路径重新读取，界面不接受任意磁盘路径、不覆盖已有配置、不刷新编辑基线以绕过冲突。已成功迁入/非空实例重试明确拒绝；有未保存编辑先处理，不静默覆盖。修复后显式重试，不开轮询文件监视器。

成功 COMMIT 前崩溃只能留下旧完整状态；重开回滚后仍为空时可重新尝试，未提交的随机 ID 不是已分配事实。COMMIT 后崩溃重开必须读原 receipt/ID/ETag，不重建第二套对象。source_documents 唯一 hash 冲突、私有记录多行/损坏或 digest 不符不得忽略：停止本次迁入并显示诊断，不删除或任选记录。仅迁入失败不阻断可用 SQLite 编辑界面；若数据库本身损坏/身份不符/缺库/日志健康故障，仍遵循原 B 的 fail-closed，不伪称空配置可安全继续写。

解析类失败可以单独提交有界 failed receipt；若连失败 receipt 也因存储故障不能持久化，显示 `statusPersistence=unknown`，不声称已记住跳过。此时只读界面与原 B 的故障准入保持；修复/重开后因没有成功提交的候选/ID，允许按首次空实例重新判断，而不是伪造“已迁入”或依赖内存标记。

### R07. 既有 profile 与双库不变量

保持 `local-acquisition-v1/`、双库 application_id/user_version=1、DELETE/EXTRA、锁/完整性/hot-journal/异常 WAL 拒绝、CAS/激活/恢复、seq/pending/引用保护、容量/维护与日志故障锁存合同。已有非空草稿、active/previous、样本/manifest/context 原字节、稳定 ID/generation/seq/delivery 原值全部保持；不把旧 YAML 或本任务 tmp 迁到正式 profile。

本 r1 **没有 schema-maintenance 执行内容**，因为方案不改 DDL；只允许获批后在新/受控 tmp v1 库做普通配置 DML。若实现发现需要新增表/列/版本、自动升级真实 v1 profile、修改现有 ledger 编码或提升依赖，停止该部分并回 PM 修订，不能用“迁入”二字泛授权。旧二进制打开新私有记录的保留/裁剪兼容也不能当作已承诺回滚路线。

### R08. 唯一前端 owner 与无桥预览

App 只实例化 `useLocalAcquisitionConsole`；纯 shell composable 只持有当前叶、主题/语言与导航，无 runtimeSnapshot/fetch/IPC。保留四叶和 CU 公共壳，不重新设计整体信息架构。Layout/Sidebar 直接消费本地 bootstrap 的身份/版本展示；五个既有 view（含工作台内 status）只留 local 分支，去除旧 prop/事件/类型链，不能让禁用旧 owner 继续隐式承担偏好或刷新。

浏览器无 Tauri 桥时显示“桌面预览，SQLite/PLC 操作不可用”，保留导航/主题/语言；不创建假空库/假保存，不调用旧 runtime IPC、health GET 或任何后端探测。启动 IPC 失败与无桥状态分开：失败显示 bootstrap 错误，不静默回 legacy；首次未加载用“尚未加载”，有成功快照后失败保留旧值与陈旧提示。写入动作不可用，busy/错误可以结束，最多一个本地 1Hz 刷新来源。

### R09. 现场与验证能力不扩权

普通 `pnpm tauri dev` 不自动添加 `rust-snap7-driver`；可编辑/保存本地配置，未编驱动的连接请求继续返回 `driver_unavailable`。`pnpm tauri:dev` / `tauri:dev:snap7` 的既有显式驱动编译合同保持；读取总 gate、有效 active、人工连接和另行启采等仍由 Rust 校验。旧 env 的 enabled/autostart/write/endpoint 不能绕过它们。导航、迁入、保存、恢复、历史和连接测试以外的查询不启动 PLC I/O；迁入自身也不运行连接测试。

`local-validation` 继续为非默认 debug、固定 fixture-only、严格绝对 tmp 路径/marker、继承环境拒绝和 release 编译拒绝；不向其 factory 放开任意 YAML 路径或真实来源。其启动不从源码根自动发现 YAML；迁入测试在 cfg(test) 的受控输入或普通入口的 tmp env/profile 中执行。不会用 fixture feature/假 invoke 来充普通默认入口证明，不改旧 DAA-002 marker/样本/窗口。

### R10. 用户诊断、日志与启动场景

PLC 配置页的一处迁入摘要显示结果、PLC/DB/组/点计数、未确认/不完整原因、源定位与安全诊断、下一动作；失败或空来源可见重试，成功/已有 SQLite 不显示可覆盖按钮。工作台仍显示 stopped，上传区域只显示现有“本地保存，上传未接入”。说明文件角色：YAML 是一次性来源，SQLite 是配置权威，`.db/.udt` 是编辑时源结构导入。

迁入开始/跳过/提交/失败/显式重试/旧键忽略及旧入口拒绝产出稳定 JSON Lines；开始运行后复用现有有界产品日志与 stdout，字段包括 event/process/resource/result/error_code/attemptId、可用时 source SHA、数量和 duration。启动拒绝在没有 profile owner 时只输出结构化 stderr，不为日志加载旧配置或触磁盘。日志不输出 YAML 全文、真实地址/凭据/`.env` 值；不每次快照重复告警。日志写失败沿用 B 的 unknown-interval 锁存，不将 receipt 或 UI 内存当作成功日志。

| 场景 | 用户可见结果 / 启动副作用 |
| --- | --- |
| 新装、无/空 YAML | 新版四页、空配置；一次跳过、无失败弹屏；无连接/采集/health。 |
| 新装带仓内脱敏示例 YAML | 作为有内容的一次性候选迁入，清楚标为示例来源，全部停用/未确认；没有特殊示例自动启用。 |
| 已有本地 SQLite | 原配置/历史保留，来源为 SQLite，旧 YAML 无论内容/mtime 是否变化均不读。 |
| 仅合法旧 YAML，多 PLC/DB/组/点 | 全量受限候选及旧策略说明、稳定 ID/receipt；无 active、连接或样本。 |
| 只有合法 snapshot policy | 有界归档说明，空配置可编辑；不制造 PLC 或业务规则。 |
| 坏 YAML/错误类型/未知根形/超限/文件不可读 | 明确失败原因、来源位置/上限与重试；空界面可继续手工配置，源不改、草稿不部分提交。 |
| 旧 `.env` legacy/storage=false/直库/endpoint 残留 | 按 R02 处理并摘要提示，普通入口不被旧模板卡住，无旧 I/O。进程显式 legacy 则清楚拒绝。 |
| 重启、源变更或重复点击 | SQLite 与既存 receipt 为准；不自动重新导入，CAS/幂等拒绝重复或覆盖。 |
| 无桥浏览器 / bootstrap 失败 / fixture 验证 | 分别为无桥只读预览、真实启动错误、显著 fixture 来源；均不回旧界面或假装普通原生成功。 |

### R11. 增量验证与普通原生证据

批准后只做与增量匹配的检查：启动/退役入口和固定发现优先级、迁入全部对象/策略/失败边界、事务/崩溃/重复/锁/CAS、已有本地状态保持、单 owner/无桥无外发、新旧文案及说明。新增迁入私有测试使用 tmp 和固定期望，不安装测试框架、不扩产品 ACK/SQL/fixture 后门。配置库 DML 沿用现有 SQL/VFS 适用约束，检查实际新增查询，无 ORM/锁文件升级或重复 B0 gate。

**必须取得一次普通原生路径证据**：移除继承业务覆盖，仅设置本任务绝对 tmp `DAA_ENV_FILE` / `DAA_PROFILE_DIR`，env 不含 mode/storage，读取 gate=false；从 DAA cwd 执行普通 `pnpm tauri dev`，不带 local-validation/fixture flag。使用受控 YAML 证明新版首启/全部停用、真实 bootstrap/IPC/SQLite 草稿与 receipt 对应；一次保存/重读、正常退出重开证明已有 SQLite 优先及 ID/ETag 保持、无连接/采样/health。无需启采、DS、真实驱动或重新采出 76 样本。若 15191 被用户窗口占用，仅允许本任务临时 Tauri override 调整自己的 frontend/devUrl 端口；不动产品固定端口或停止他人窗口，并记录与普通配置的唯一差别。

原生工具可用时由角色取得；必要时接受 R19 同类的实际 Owner 操作与同库证据，但不预设多轮新人工验收清单。工具不具备所需证据时如实记录 blocker，不用 browser 假桥/fixture 模式替代。既有未变 B 功能按当前 hash 和原始输出核用，**不重复整套采样/解析/Snap7/激活/容量/长时间/native 手工矩阵**；只在新变更/新失败/未消除疑点时扩大对应检查。

### R12. 文档、角色交接与结束

Development 更新 §5 允许的当前稳定 README pair、YAML 示例的说明注释、i18n 与 CODE_INDEX 的 DAA 条目；旧任务/设计正文不改。记录实际修改/删除/去注册文件、全 diff（含 untracked 全文）、新命令与退出码、失败/重试、保留/已退出资源、R↔AC 证据、批准 SHA 和精确 developer_handoff。main/docs 只写 current facts，不提前称完成/最终验收。

之后由唯一主协调启动新的实际 Verification、fresh context（工具支持时 `fork_turns="none"`），只验证和写 checklist；失败回 Development，实质 scope 变化回 PM。`qa_passed` 后交 Human Owner 最终验收；不自动等于 DAA-002 终验、C 批准、现场切换或发布。当前 PM 完成 draft/自检后停止写入，不启动 Development/QA、automation 或通知执行窗口。

## 5. 封闭 allowlist 与角色权威

**本轮 PM 只能新增本 spec。** 下列实现面仅在 Human Owner 精确批准 r1 后才交 Development。路径相对 `automation-world/data-acquisition-agent/`，仓根路径另标。每行一个精确文件，无目录通配。M=既有最小修改；N=新文件；D=删除。未使用的 M 不必修改；M 不授权删/移，N 已存在或需任何额外路径先回 PM。Rust 旧实现只去注册，不借本次清理全仓或删除旧实体树。

| 类别 | 精确路径 | 限定用途 |
| --- | --- | --- |
| M | `src-tauri/src/main.rs` | 普通 SQLite、旧参数提前拒绝。 |
| M | `src-tauri/src/lib.rs` | 唯一本地装配、去旧 invoke/autostart/headless dispatch。 |
| M | `src-tauri/src/bin/aiis-data-acquisition-agent-runtime.rs` | 无配置/锁/I/O 的退役拒绝入口。 |
| M | `src-tauri/src/config/mod.rs` | 既有定位优先级与来源标识，不输出 env 内容。 |
| M | `src-tauri/src/config/local_bootstrap.rs` | R02 默认/退役键、固定迁入路径、安全验证区分。 |
| M | `src-tauri/src/domain/mod.rs` | 去注册旧模型，注册迁入 DTO。 |
| N | `src-tauri/src/domain/yaml_migration.rs` | 有界状态/计数/安全诊断/receipt 类型。 |
| M | `src-tauri/src/services/mod.rs` | 去旧服务注册，仅注册新迁入服务。 |
| N | `src-tauri/src/services/local_yaml_migration.rs` | 首启/显式重试的有限用例编排。 |
| M | `src-tauri/src/services/local_recovery.rs` | 将迁入用例接入安全启动。 |
| M | `src-tauri/src/services/local_supervisor.rs` | 锁后/读取草稿和 actor 前接迁入服务；不改调度算法。 |
| M | `src-tauri/src/services/local_configuration.rs` | 正常源导入不接受 YAML、保护私有来源，保 CAS/derived proof。 |
| M | `src-tauri/src/infrastructure/mod.rs` | 去旧 I/O 模块注册、注册专用迁入 adapter。 |
| N | `src-tauri/src/infrastructure/yaml_migration.rs` | 固定两源有界读取/严格解析/多对象转换，不含网络。 |
| N | `src-tauri/src/infrastructure/yaml_migration_tests.rs` | cfg(test) 精确输入/输出、失败/幂等/崩溃与现存数据保护；不进入产品。 |
| M | `src-tauri/src/infrastructure/local_store/mod.rs` | 注册局部 repository，复用现有 owner/worker/日志。 |
| N | `src-tauri/src/infrastructure/local_store/yaml_migration.rs` | 现有表 DML、原子草稿/receipt/CAS，无 DDL。 |
| M | `src-tauri/src/infrastructure/local_store/configuration.rs` | 私有迁入来源保留/冲突保护，原历史正文不改。 |
| M | `src-tauri/src/infrastructure/local_store/tests.rs` | 仅受影响旧 YAML helper 用例替换及定向回归接线。 |
| M | `src-tauri/src/infrastructure/local_profile_lock.rs` | 保留唯一 profile 锁，退下旧全局 legacy owner。 |
| M | `src-tauri/src/infrastructure/tia_source.rs` | 移除 YAML 分支/单 PLC helper；保 .db/.udt 算法。 |
| M | `src-tauri/src/commands/mod.rs` | 去旧命令注册，只保 local/validation。 |
| M | `src-tauri/src/commands/local_acquisition.rs` | 有界迁入状态/重试 IPC 与唯一 bootstrap。 |
| M | `src/App.vue` | 单 local owner 与纯 shell，去旧 view/prop/event 分支。 |
| M | `src/main.ts` | bootstrap 错误/无桥状态，保持现有组件与样式。 |
| M | `src/services/localAcquisition.ts` | 单一原生/无桥 bootstrap 和迁入 DTO/facade。 |
| D | `src/services/runtimeSnapshot.ts` | 删除旧 IPC、fallback 与 Backend health facade。 |
| D | `src/console/composables/useControlAgentConsole.ts` | 删除旧运行 owner。 |
| N | `src/console/composables/useAgentConsoleShell.ts` | 纯导航/既有主题语言组合，无 runtime/I/O。 |
| M | `src/console/composables/useLocalAcquisitionConsole.ts` | 唯一 owner、迁入摘要/显式重试/无桥拒写。 |
| M | `src/layouts/AgentLayout.vue` | 去 RuntimeSnapshot 依赖、只收本地展示。 |
| M | `src/components/shell/AgentSidebar.vue` | 身份/版本改取安全 bootstrap。 |
| D | `src/components/console/PlcRuntimeUnitPicker.vue` | 删除仅供旧 RuntimeSnapshot 的选取组件。 |
| N | `src/components/console/YamlMigrationNotice.vue` | 一处有界迁入结果/下一动作，保现视觉系统。 |
| M | `src/app/runtime/views/overview/index.vue` | 只保 local 摘要，移除 legacy 部分。 |
| M | `src/app/collection/views/status/index.vue` | 只保 local 控制/日志，移除 legacy 部分。 |
| M | `src/app/plc/views/diagnostics/index.vue` | 只保 local PLC 配置，呈现迁入摘要。 |
| M | `src/app/plc/views/points/index.vue` | 只保 local、编辑源限 .db/.udt。 |
| M | `src/app/collection/views/storage/index.vue` | 只保本地存储/历史及 C 说明。 |
| D | `src/app/gates/views/authorization/index.vue` | 删除旧授权自检界面，不保访问入口。 |
| M | `src/locales/zh-CN/common.json` | 新启动/迁入/预览/退役稳定码与说明。 |
| M | `src/locales/en-US/common.json` | 对称英文。 |
| M | `src/app/runtime/locales/zh-CN.json` | 删除分支涉及文案的必要同步。 |
| M | `src/app/runtime/locales/en-US.json` | 对称英文。 |
| M | `src/app/plc/locales/zh-CN.json` | 迁入/地址/导入限制。 |
| M | `src/app/plc/locales/en-US.json` | 对称英文。 |
| M | `src/app/collection/locales/zh-CN.json` | 本地/退役策略说明。 |
| M | `src/app/collection/locales/en-US.json` | 对称英文。 |
| M | `vite.config.ts` | 仅 envDir:false，端口/alias/依赖不变。 |
| M | `.env.example` | 必要定位/只读门禁与迁入说明，退役键移除。 |
| M | `config/plc_points.yaml` | 仅注释改为一次性脱敏迁入示例，不改点值。 |
| M | `config/plc_snapshot_policy.yaml` | 仅注释改为退役策略迁入示例。 |
| M | `README.md` | 唯一入口/场景/能力及限制。 |
| M | `README.zh-CN.md` | 对称中文。 |
| M | `src/app/README.md` | 唯一 owner、无桥、正常导入与迁入分离。 |
| M | `src/app/README.zh-CN.md` | 对称中文。 |
| M | `src-tauri/src/infrastructure/local_store/README.md` | 同 schema 私有来源/事务/保护/恢复说明。 |
| M | `src-tauri/src/infrastructure/local_store/README.zh-CN.md` | 对称中文。 |
| M | 仓根 `CODE_INDEX.md` | 仅 DAA 实际结构/退役条目。 |
| M | 仓根 `automation-world/README.md` | 仅 DAA 当前入口/配置权威/退役摘要，CA/SMA 不改。 |
| M | 仓根 `automation-world/README.zh-CN.md` | 对称 DAA 摘要。 |

去注册的精确 Rust 模块：commands 的 `headless_runtime.rs`、`plc_collection.rs`、`plc_diagnostics.rs`、`runtime_snapshot.rs`；services 的 `authorization_gate.rs`、`plc_collection.rs`、`plc_diagnostics.rs`、`runtime_snapshot.rs`；domain 的 `authorization.rs`、`headless_runtime.rs`、`plc.rs`、`plc_collection.rs`、`runtime.rs`；infrastructure 的 `database.rs`（及其未注册子树）、`logging.rs`、`minimal_s7_adapter.rs`、`plc_client.rs`、`plc_decode.rs`、`plc_points.rs`、`plc_s7.rs`、`plc_snapshot_policy.rs`、`rust_snap7_adapter.rs`。这些文件**本体不在写入 allowlist**，只通过上表四个 mod.rs 和 lib.rs 断开产品编译/执行图；没有附加 feature 或反射入口。必要类型由新迁入 DTO 在新 adapter 内定义，不能重新挂回旧 I/O graph。保留 SeaORM/旧锁但不使用不等于直库仍可执行，不为删依赖扩大锁变更。

| 角色 / gate | 仓根相对精确路径 | 归属 |
| --- | --- | --- |
| PM / Human Owner | `automation-world/data-acquisition-agent/plans/DAA-003-sqlite-only-startup/spec.md` | 当前唯一 PM 写入；以后只真实批准/Revision 记录。 |
| Development，批准后 N | `automation-world/data-acquisition-agent/plans/DAA-003-sqlite-only-startup/tasks.md` | 实施/DEV self-check/精确交接，不写 QA verdict。 |
| 新 fresh-context Verification，handoff 后 N | `automation-world/data-acquisition-agent/plans/DAA-003-sqlite-only-startup/checklist.md` | 独立结果/失败/verdict 与真实 Owner 最终验收。 |
| 主协调 M | `automation-world/data-acquisition-agent/PLAN.md` | DAA-003 新行和实际 gate，保 DAA-002 原链。 |
| 主协调 M | `automation-world/data-acquisition-agent/PLAN.zh-CN.md` | 对称。 |
| 主协调 M | `automation-world/data-acquisition-agent/plans/README.md` | 仅新 catalog 行，角色文件存在后才链接。 |
| 主协调 M | `automation-world/data-acquisition-agent/plans/README.zh-CN.md` | 对称。 |
| 主协调 M | `automation-world/PLAN.md` | 仅 DAA 子工程阶段摘要。 |
| 主协调 M | `automation-world/PLAN.zh-CN.md` | 对称。 |
| 主协调 M | `PLAN.md` | DAA-003 唯一 spec 指针/摘要，不建根重复 bundle。 |
| 主协调 M | `PLAN.zh-CN.md` | 对称。 |
| 主协调 M | `plans/README.md` | 指向唯一 DAA 本地 bundle。 |
| 主协调 M | `plans/README.zh-CN.md` | 对称。 |

其余文件均保护，特别是 DAA-002/DAA-001 全 bundle、真实 `.env`/YAML/profile/数据库/原样本、Cargo.toml/Cargo.lock、package.json/pnpm-lock/workspace、local schema.rs/ledger/调度/managed_s7/既有验证 factory marker、产品 Tauri 配置/capabilities/icon、CU 全部公共/私有源码、CA/SMA/backend/frontend-js/tools、根治理/角色/workflow/skills/ROADMAP/contracts 与设计正文。关键源码中文头部遵循既有风格；辅助脚本/夹具生成/产物只写本任务系统 tmp，不借索引生成器改其它文件。

## 6. 串行阶段与 R / AC 对照

| 阶段 | 完成条件 | R / AC |
| --- | --- | --- |
| G0 | Human Owner 精确批准 DAA-003 r1；当前 pending，未过不创建 tasks/实施。 | R01；AC01 |
| S1 | 固定当前 before/保护面 → 单 SQLite bootstrap/env → 旧入口/执行图去注册；先证明无旧 I/O。 | R01–R03/R09；AC01–AC03/AC09 |
| S2 | 固定发现/空资格 → 严格全对象转换 → 同 schema receipt/事务/CAS/容量/失败恢复。 | R04–R07；AC04–AC07 |
| S3 | 单 local owner/纯 shell/无桥状态与迁入摘要/双语诊断；不重新设计四页。 | R08/R10；AC08/AC10 |
| S4 | 定向失败/回归、普通原生默认启动/保存重开、文档/完整差异/原 B 源 hash 与 raw 核用 → developer_handoff。 | R11–R12及前述；AC01–AC12 |
| G1 | 主协调调入新的实际 Verification/fresh context，独立检查最新交接；失败返工后新 fresh QA。 | R12；AC12 |
| G2 | qa_passed 后 Human Owner 决定 DAA-003 最终验收；DAA-002 自己的终验仍独立。 | R01/R12；AC01/AC12 |

## 7. 验收标准与定向证据

以下是批准后的义务，当前无 Development/QA 执行或通过事实。同号 R ↔ AC；阶段在 §6，未改 B 能力按源/hash/raw 核用，不复制旧 verdict 当新 QA。

| AC | 可核完成条件 | 必要证据 |
| --- | --- | --- |
| AC01 | 精确批准后实际实施、独立 root 链、旧 DAA-002 三文件/失败/终验状态保持，只有本范围增量。 | 批准 SHA、当前 before/after/新增全文/删除 diff、角色与保护归属审计。 |
| AC02 | 普通入口不设 mode/storage 直接 SQLite；旧 env 残留与进程显式 legacy 按 R02 区分，优先级和提示可操作；无真实 env 改写。 | 受控 env 缺省/旧模板/进程覆盖/非法值/退役 true gate/endpoint 表驱动场景，实际 bootstrap/exit2/无 I/O 轨迹。 |
| AC03 | 旧 IPC 不注册、CLI/headless 在配置/锁/I/O 前退役；旧 frontend owner/health 删除，无旧 writer/授权外发/自检可达。 | 新二进制/源码执行图与命令注册核对，全部旧名反例；旧 CLI 各入口非零且 profile 不建/不变；无 GET/SQL/PLC 调用。 |
| AC04 | 首空只发现固定两个路径/正确优先级，已有 SQLite 不读源，缺失/空诚实跳过；无父目录/CA/URL/symlink 扫描。 | 受控两套路径/冲突覆盖/不存在与不可读源、改变源后重开、非空库原值及无读取探针。 |
| AC05 | 多 PLC/多 DB/组/全部点完整转换或明确阻断，稳定 ID；旧策略仅归档，未确认/不完整/disabled，无 fake DB proof。 | 至少2PLC、每台多个组且跨DB的独立预期清单/计数/值；同名/重复/不支持类型/String/非法策略/超4台或组数反例；不只首 PLC/前N点。 |
| AC06 | receipt/来源/草稿单 config 事务、额度有界、CAS与独占锁、成功/空后不重读、修复后显式重试；崩溃不半份/不重复 ID。 | COMMIT 前/后两个定向断点重开；重复请求/重试冲突/两进程/写预算或 I/O 失败/record hash冲突；新库对账同 ETag/ID/source hash，未知/凭据值未进入库/日志。 |
| AC07 | 无 DDL/schema/依赖变更，已有本地草稿/active/history/seq/pending 原值保持，原 fail-closed 未被迁入吞错。 | 新 tmp v1 和受控非空 v1 全配置/原样本字节 before/after；源错误与库损坏区别反例；schema/user_version/锁文件精确 hash。不得使用 DAA-002 live76 profile。 |
| AC08 | 四页只装一个 local owner，纯 shell 保偏好/导航；无桥、未加载、陈旧和真实 bootstrap失败有别，无假保存/health。 | 真实页面组件/调用数/1Hz owner核对、代表导航/语言主题/无桥与失败路径；浏览器网络/IPC计数，旧 RuntimeSnapshot 引用清零。 |
| AC09 | 驱动默认/读 gate/人工激活连接启采边界保持，local-validation 不扫描源码源、无真实 I/O或新增后门。 | 默认feature/未编驱动拒绝、read=false及迁入/重启无连接；现有默认/release拒绝原输出结合未变源hash，受影响 guard 定向反例。 |
| AC10 | 每个启动场景给诚实来源、结果/数量/下一步；失败界面仍可编辑，日志有界且不泄密/不伪报 persisted。 | R10场景矩阵、产品 JSONL/安全摘要/200诊断计数边界、一次告警与重试行为；普通日志故障沿原锁存证据核用。 |
| AC11 | 普通无fixture原生默认入口确实显示新版、真实 IPC/SQLite 保存并重开保持/不重迁；未要求重做 B 全套或现场。 | 一次本任务 tmp 原生链、相同配置/receipt/ID/ETag和 stopped 事实、真实命令/退出/限制；普通与端口override差别明确，browser/fixture不代证。 |
| AC12 | README/i18n/头部/CODE_INDEX与新行为一致、范围/资源可审计，DEV handoff→新 fresh QA→Owner最终验收分层。 | 双语语义/键/占位符/本地链接、完整diff/有限allowlist、新角色文档/真实verdict；原 DAA-002状态不升格。 |

建议实际命令在 Development tasks 落定并记录 cwd/工具链/退出码，不把此处当已执行：

- `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check`；`cargo check --manifest-path src-tauri/Cargo.toml --locked --no-default-features --all-targets`；迁入/启动过滤的 `cargo test --manifest-path src-tauri/Cargo.toml --locked <actual-filter> -- --test-threads=1`。先审查外发边界，target/故障库归 tmp，不运行旧现场测试或 ignored 外部动作。
- 默认 binary 的旧参数/headless 反例；迁入私有 tmp 事务/COMMIT断点与 bounded failure，不填满宿主盘、不手删 journal。受影响的 CAS/derived proof/打开恢复/原始历史与维护记录保护做定向回归，其余核原 QA4 raw/hash。
- `pnpm build --config vite.validation.config.ts --outDir <abs-tmp-dist> --emptyOutDir` 及普通 Vite envDir=false 接线检查；一次 R11 的普通 `pnpm tauri dev` 原生链。只在这次增量确需时执行驱动静态 check，不重启现有 Owned 窗口或模拟器。
- 文档本地链接/双语 JSON keys 与 placeholder/literal-key、头部与 CODE_INDEX 的 DAA 局部差异检查；before/after 原文与受保护字节审计。辅助工具不安装进项目依赖。

## 8. 失败、恢复、风险与 deferred

| 风险/失败 | 必须处理 |
| --- | --- |
| 旧模板被误当模式选择、旧 true gate 激活外部能力 | 来源区分/退役键汇总；旧执行图断开；进程显式 legacy 清楚拒绝。真实 env 不自动重写。 |
| 多 PLC/重复/不支持点被悄悄丢弃 | 全量计数/路径归属、原源保持；不能完整物化则整份候选拒绝，空界面可继续配置。 |
| 缺完整 DB 被误当地址可信 | 全 disabled/不完整/未确认，完整源另导入；不能在迁入后直接采集。 |
| 配置写失败/COMMIT间崩溃/重复请求 | 单库事务/CAS/receipt，原值回滚或完整恢复；不假成功、不重编号。库自身异常仍按原 fail-closed。 |
| receipt 被裁剪、伪造或无限增长 | 私有命名域/写权限、digest/唯一记录核对、8MiB总上限、普通save与source裁剪保护；故障留诊断。 |
| 原 YAML 含无关字段/秘密 | 白名单投影，不复制凭据/未知值；日志只安全摘要，原文件保留，不声称已备份完整源。 |
| 不变 B 证据被当成重新跑过或新普通启动 | 按源/hash/raw对应核用；新入口必须自己取得普通原生证据，未执行不记pass。 |
| 去注册触及额外依赖/旧类型闭包 | 在有限mod/view内收敛；必需额外路径/DDL/依赖变化回 PM，不全仓重构/升级。 |

恢复先停止本任务实例新增工作，保留 SQLite/journal/receipt 和原 YAML；不删 pending、不降 seq、不复制 B 的 tmp profile、不回写源文件。语法/权限/超限修好后只在空实例显式重试；非空实例在既有编辑流程手工处理，不增覆盖/合并工具。二进制回退须先证明同 schema/private record 的兼容，不提供旧 YAML 模式作为本应用可选回滚开关；真实现场回退/切换另行批准。

延期且不阻断本次受控交付：真实 YAML/env/profile 的实际迁入；PLC/TIA/DS 协议与负载；Backend/SMA/Stage C 可靠上传/ACK/回执；通用迁移/备份恢复/自动源映射；后台/headless 新宿主；多平台打包签名；数据库/现场来源切换；Docker/Git/发布/部署。默认启动、数据保持、事务/幂等、退役无外发及本次普通 native 证据不能作为 deferred 假通过。

## 9. Skill 路由、PM 自检与 handoff

| 后续实际表面 | Development / Verification 必需按需消费 |
| --- | --- |
| Rust 启动/本地 SQLite DML/锁/日志/恢复与旧执行图 | `rust-runtime`，其适用日志/结构规则；不引入 Backend/Celery。 |
| Tauri 入口/IPC/原生默认启动与验证隔离 | `desktop-tauri` + `rust-runtime`。 |
| 旧 PLC YAML/点位类型/地址/结构完整性边界 | `plc-point-mapping`；不修改 tools 或扩大偏移算法。 |
| Vue 单 owner/四页/纯 shell/失败状态 | `frontend-ui` 的既有 DESIGN/FRAMEWORK适用部分。 |
| 用户可见迁入/预览/退役文案与稳定码 | `i18n-workflow` 与 `frontend-ui`。 |
| 关键新源码头/真实结构索引与说明 pair | `code-document-indexer`，仅 DAA 允许面。 |
| 工业角色/独立任务/3MD与机械索引 | `aiis` + `project-governance`。 |

PM 文档自检只核：必需元数据/独立 root身份、引用与当前基线SHA、精确 M/N/D和10索引分权、R01–R12 ↔ AC01–AC12 ↔ G0/S1–S4/G1/G2、全部边界/链接及仅新spec增量。结果/命令/最终SHA由交接消息及 `/private/tmp/daa-003-spec-p8k4220b/pm/`附件提供，不在正文存自身SHA。这不是 Development self-check 或独立 Verification。

修订/批准历史：

- 2026-10-19，r1 draft：先前“保留旧可选模式”在成稿前由最新 Human Owner 方向覆盖；未形成另一获批 Revision，不虚构 r0/r1 批准历史。
- 2026-10-19，r1 owner_approved：Human Owner 按 §1 最新原话批准 draft SHA-256 `790563fb4cbd58690f4a63510d02d7148c19928649c7e65073e8509b1a906bf4`；本次仅补批准事实，不重开 scope，不改变任何技术、验收、路径、风险或排除条款。
- Development / tasks / 产品实施 / self-check / developer_handoff：**未发生**。
- 新 fresh-context Verification / checklist / verdict：**未发生**。
- Human Owner 对 DAA-003 的最终验收：**pending**；DAA-002 的终验也仍 pending。

当前仅交唯一 coordinator `/root` 转 Human Owner 审阅精确 DAA-003 r1 及 §1 四项取舍。批准后才按本文件有限面交实际 Development，形成精确 handoff 后再由 coordinator 启动新的 fresh-context Verification，最后由 Human Owner 决定终验。root 可在 PM 事实存在后机械同步10索引；PM 不写索引或任何后续角色文件。

**最新 handoff（覆盖上一段起草时待审阅交接）：** 精确 r1 已获批准，交唯一 coordinator `/root` 调用实际 Development，消费本 spec、完整已形成 bundle、批准前后 SHA 和当前工作树 before，按 §6 在原有限面完成 SQLite 唯一入口与一次性迁入、定向自检和精确 developer_handoff。之后由 coordinator 调用新的 fresh-context Verification；QA 通过后再交 Human Owner 最终验收。无需再次申请本 r1 范围批准，也不因批准自行标记实施/QA/最终验收通过。PM 完成本次批准记录及技术原文不变自检后停止全部写入；不写 tasks/checklist/索引/产品、不执行产品验证或操作窗口。
