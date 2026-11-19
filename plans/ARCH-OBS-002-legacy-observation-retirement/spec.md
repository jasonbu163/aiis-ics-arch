# ARCH-OBS-002：一次性清退旧设备与过程监控链路

Task ID: ARCH-OBS-002
Revision: r1
Status: owner_approved
Workflow Mode: STD
Execution Mode: agent_team_same_session
Owner: Human Owner
日期：2026-11-18（Asia/Shanghai）

## 1. 目的与当前状态

Human Owner 要求一次清退过程／实时旧机制，保留最新机制，相关手动实验已暂停。该表述不是本草案精确 Revision 的范围批准，也不表示所有调用方、数据库写入方或用户服务已经停止。本任务先确定源码、接口、数据表、权限和切换范围；未获精确批准前只形成本规格，不创建 Development 或 Verification 记录，不修改应用、数据库、真实配置或服务。

原有 [ARCH-OBS-001](../ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md) 的 r10 保全式迁移、r11 隔离恢复验证与 r12 手册按各自时点保留。它的独立 QA 和 Owner 终验状态不由本草案改写。用户随后要求只保留最新机制；本任务若获批，将在本次交付源码和已授权目标中**有意终止**旧 r8 归档查询、v1 已确认事件重放和依赖归档的旧恢复路径。历史规格、原始合同和证据继续保留，不假称旧能力从未存在。

[ARCH-TASK-001 r3](../ARCH-TASK-001-generic-plan-performance/tasks.md) 的当前交接及并行 Verification 为独立工作；该任务先前约定继续提供的三条旧设备及一条旧监控业务集成入口，由本任务拟单独退役。本任务不改写其规格、handoff、验收结论，也不恢复该任务已退役的四条旧实绩集成入口。保留并回归其当前通用计划／实绩机制及既有数据。开始改动交集文件前须与其当前协调者核对交接／验证是否仍依赖该精确文件版本；冲突时停止相应切换并协调，不覆盖并行工作。

2026-11-18 的只读快照：指定 dev 为 `127.0.0.1:3307 / industrial_level_2_system`，MySQL `8.4.6`，唯一 Alembic revision `ae20b4d6f831`；§2 所列 18 张候选表和 `metric_ingest_receipts` 均为 0 行。`equipment_metric_groups` 1 行、`equipment_metric_configs` 2 行；`energy_prices` 1 行、`energy_price_hours` 3 行。它们是用户／既有任务数据，必须保护。该快照不证明现在仍为空、不证明外部无调用，也不是迁移授权。

## 2. 唯一清退集合

### 2.1 数据库：18 张旧表

以下集合完整且不可扩大。只允许清退**执行前重新核实为空**的这些表，且必须同时满足 §5 的目标、依赖、锁、回执与写入方条件；不因某表含数据而自动复制、清空、跳过后继续或删除行。

| 类别 | 精确表名 |
| --- | --- |
| r8 归档，6 张 | `equipment_status_r8_archive`、`process_monitor_r8_archive`、`equipment_metric_configs_r8_archive`、`equipment_metric_slot_bindings_r8_archive`、`equipment_card_configs_r8_archive`、`monitor_curve_group_configs_r8_archive` |
| 旧设备业务与回执，7 张 | `equipment_drive`、`equipment_temperature`、`equipment_production_parameters`、`equipment_temperature_samples`、`equipment_temperature_sample_receipts`、`equipment_mapping_receipts`、`equipment_integration_receipts` |
| 旧过程／旧能耗／采集器兼容，5 张 | `monitor_history_process_curves`、`monitor_history_energy_consumptions`、`monitor_mapping_receipts`、`monitor_integration_receipts`、`monitor_collector_states` |

后两张旧业务历史表同时供旧能耗页面使用；将旧能耗页面及旧 `/monitor/energy` 一并退役，唯一的能耗统计保留现有新表计页面，不迁移旧数值、不修改新统计口径、不把能耗移到辅助管理。能源单价属于独立业务，`energy_prices`、`energy_price_hours`、现有价格页面及 API 保留。

`monitor_collector_states` 及 Core `/monitor/collector/status` 曾被 ARCH-ACQ-002 明确保留；本任务拟有意识地终止该兼容能力。冻结 `automation-world/control-agent` 的数据库实体和服务仍读写该表，清退后它不能再依赖本新 schema 的此表运行；不修改、启动、停止或迁移该冻结 runtime，其兼容目标不在本任务内。DAA 源内也有旧直库引用，但当前 [services/mod.rs](../../automation-world/data-acquisition-agent/src-tauri/src/services/mod.rs) 未注册该旧执行图，[lib.rs](../../automation-world/data-acquisition-agent/src-tauri/src/lib.rs) 在配置和 I/O 前拒绝旧 `--ca-*` 入口；这不是对所有旧制品或现场进程的证明。DAA 现行 SQLite 采集和 PLC Facts v2 必须保持，不得据此操作用户正在运行的 DAA、CA 或设备。

### 2.2 HTTP：退出的旧操作

下列路径均以 `/api/v1` 为前缀，方法为精确合同。清退后从实际注册和 OpenAPI 消失，已认证或匿名直接访问不得执行旧行为。实施前须核查项目配置、已知调用方及用户确认的外部使用方；空表和未在新 UI 中引用不能证明无人调用。

| 操作 | 路径 |
| --- | --- |
| GET | `/equipment/admin/r8-archive`、`/equipment/admin/r8-archive/config`、`/monitor/admin/r8-archive` |
| GET | `/equipment/drive`、`/equipment/temperature-control`、`/equipment/production-parameters` |
| GET、POST | `/equipment/temperature-samples`、`/equipment/drive-samples`、`/equipment/production-parameter-samples` |
| GET | `/equipment/temperature-sample-dashboard` |
| POST | `/integration/equipment/temperature-samples`、`/integration/equipment/drive-samples`、`/integration/equipment/production-parameter-samples` |
| GET | `/monitor/temperature`、`/monitor/energy`、`/monitor/collector/status` |
| GET、POST | `/monitor/process-curve-samples` |
| POST | `/integration/monitor/process-curve-samples` |

其中四条 `/integration/equipment/*`／`/integration/monitor/*` 旧 POST 是 [business-integration-v1](../../contracts/published/http-api/business-integration-v1/README.zh-CN.md) 原八路中的设备／过程四路；其余四路实绩旧入口按 ARCH-TASK-001 当前事实已退役，本任务不得恢复。保留该历史 OpenAPI、样例、散列和旧任务证据；在现行索引及使用说明明确本任务退出的操作和替代机制，不伪造原合同数据或静默改变历史。

**保持** `POST /integration/equipment/latest-snapshots`、`POST /integration/monitor/history-samples` 的 v2 行为和路径，以及 `GET /integration/metric-definitions`；两 POST 对旧 `aiis.metric-ingest/v1` 请求仅明确拒绝，不再重放旧回执。先执行现有身份／权限保护，不因版本拒绝泄露回执。保持全部新 `/energy/consumption/*`、`/energy/metric-configs*`、`/energy/admin/consumption-samples*` 与 `/integration/energy/*`。不改性能／计划当前 API、PLC Facts API 或能源价格 API。

### 2.3 当前 UI、权限和文档

1. 设备状态四页和过程温度／传动／清洗页继续使用现有配置驱动组件；清理只由旧页面使用的 equipment 三页、monitor 旧温度／实时 HMI／旧能耗页面及其专属调用、mock 和未复用组件。不能删除新页面、公共组件或当前领域共用的函数。
2. 唯一能耗页面继续使用当前新版组件和 URL `/monitor/consumption`。移除旧页面路由 `/monitor/energy`，不保留旧 URL alias；原深链接将失效。旧能耗页面的菜单、来自新版页的旧页面链接、已停用 dashboard 的旧快捷地址及文档同步清理或指向新版页，不恢复已停用 dashboard。
3. 为避免改动目前 dev 两个角色已持有的 pageId，将唯一新版能耗页的 `pageId` 由 `monitor.consumption` 改为 `monitor.energy`。这会使原来持有 `monitor.energy` 的角色看到**新版页面入口**，是本草案明确提出的权限语义变化；并不自动授予后端 `energy-consumption-read`、任何表计范围或管理权限。dev 磁盘配置只读检查显示 supervisor/operator 均有 `monitor.energy`、均无 `monitor.consumption`，且两角色均无新能耗读权限；实际进程环境可能覆盖磁盘文件，切换前仍须复查。其他环境若已配置 `monitor.consumption`，必须由其负责人审查并明确授权迁移为 `monitor.energy` 后才能切换，不能静默改权限或把未知键当作有效授权。
4. 移除旧 `monitor` collector 权限及旧设备／过程专属权限声明后，需核对现有角色数组；dev 磁盘配置两角色均含 `monitor`。拟在**另获明确授权时**只从本机 `backend/.env` 的 supervisor/operator 活动数组删除已退役的 `monitor`，保留其他成员与顺序、角色子集和所有其他配置；如进程环境覆盖或真实配置格式与预期不符则停止。不得添加新能耗 API 权限、表计范围或重写其他环境。若 Owner 选择由自己修改，则开发方提供精确差异和验证方法，不代操作。
5. 公开 example、双语文案、README、操作手册、合同索引与真实活动行为一致；历史任务 bundle、冻结合同和既有结果留存。已有设备观察值、采集数据及价格记录不因本任务更改。

## 3. 必须保护的当前机制

- `equipment_status_main`、`process_monitor_main`、`energy_consumption_main`、`metric_ingest_receipts`；区域、指标、槽位、卡片、曲线、能耗指标的当前配置表及其已有行、标记、顺序和绑定。快照仍按设备＋任务较新整包覆盖，历史仍按真实 `observed_at` 追加及排序；0／false、缺测、权限、去重、重试和任务号语义保持。
- 只调整 `metric_ingest_receipts` 的新写入版本默认值为 v2／r10 以免继续默认为 v1／r8；保留其字段、现有 v2 回执行和 FK 引用。若实际存在旧版本回执、未知版本或结果指向旧归档，停止，不迁移或清除回执。
- 保持 `plc_source_registry`、`plc_facts_latest`、`plc_facts_history` 和已有采集来源／数据；保持最新设备观察、能耗、价格、计划与实绩及用户、权限相关数据。不得清空表、重置自增、覆盖原始数据或篡改已存在证据。
- 保持既有独立人工读权限、机器 Bearer、设备／表计范围、历史白名单和时间合同；不得通过扩大 scope、默认设备、模拟值、跳过验证或改变时区来使测试通过。后台真实业务数据／实绩记录不因新测试被改写。
- 不修改 DAA、SMA、冻结 CA、PLC、Field Flow、真实设备或其配置；不声明 SMA→业务写入或现场全链已接通。旧 collector 兼容退出对冻结 CA 的影响见 §2.1。

## 4. 允许修改的交付面

以下仅在本 Revision 经 Human Owner 精确批准后用于对应职责。范围指目录不意味着可顺手重构；所有修改必须直接对应 §2–3、验收和必要的既有依赖适配。发现新增模块、数据表、契约、文件范围或实质行为须先回 PM 修订。

| 文件／目录 | 允许的目的 |
| --- | --- |
| `backend/app/equipment/**`、`backend/app/monitor/**` | 撤除本任务旧路由、模型、服务、注册及其专用代码；保留历史说明／任务链接，双语 README/PLAN 只同步退役状态，不删除历史任务记录。不得借此改其他业务模块。 |
| `backend/app/equipment_observation/api/routes.py`、`services/ingest.py`、`services/ingest_v2.py`、`schemas.py`、`models/records.py`、`manifest.py`、`error_codes.py`、`profile.py`、`README.md`、`README.zh-CN.md` | 撤 r8/v1 专用读取和重放；保留 v2、新能耗和回执事实；同步新 revision 守卫及文档。仅在实际引用需要时修改所列文件。 |
| `backend/app/module_contract.py`、`backend/alembic/env.py` | 移除退役模块／collector 的运行注册与显式模型引用；保持其他模块注册和 metadata。 |
| `backend/app/plc_facts/v2_config.py`、`backend/common/integration/storage.py` | 只补新 schema revision 的目标兼容，保持采集和其他业务的原有版本、身份及时间约束。`equipment_observation/profile.py` 须让清退后源码只接受新 revision，避免在旧 schema 上加载不兼容实现，并延续 r10 设备时序参数必填。 |
| `backend/scripts/business_time_adoption/main.py`、`backend/scripts/business_time_adoption/README.md`、`backend/scripts/business_time_adoption/README.zh-CN.md`；必要时新增 `backend/scripts/observation_retirement/**` | 旧 equipment／monitor 的业务时间采用 CLI 入口随其 owner 退出，不能继续作为活动功能或连接不存在的表；其他 module 路径保持原状，不宣称既有 performance 路径已可用。新增诊断入口只为本任务守卫和对账，裸调用只显示帮助，不读取默认配置或产生副作用。 |
| `backend/alembic/versions/20261118_1645_c9e1a3b5d720_retire_legacy_observation.py` | 新增唯一后继 `c9e1a3b5d720`，`down_revision = ae20b4d6f831`；不得修改旧 revision。实施前如唯一源码 head 或 dev 前驱已变化，停止并回 PM 修订，不制造分叉。 |
| `backend/tests/**`、`backend/tests_mysql/**` | 仅更新受退役操作、当前模型、前向迁移和版本守卫影响的测试或新增定向测试；不能删除无关测试或以跳过代替验证。历史迁移基线测试继续检查历史迁移，不把旧 metadata 写成当前业务能力。 |
| `frontend-js/src/app/equipment/**`、`frontend-js/src/app/monitor/**`、`frontend-js/src/app/dashboard/views/home/index.vue` | 仅处理 §2.3 的旧页面、调用、导航、pageId、旧链接及双语；新版组件、当前指标列宽和管理功能保持。dashboard 仍为关闭。 |
| `frontend-js/tests/module-registry/**`、相关 equipment／monitor 局部测试 | 只更新直接受影响的路由、页面授权、文案和回归测试。 |
| `README.md`、`README.zh-CN.md`、`backend/README.md`、`backend/README.zh-CN.md`、`frontend-js/README.md`、`frontend-js/README.zh-CN.md`、`backend/.env.example`、`backend/.env.docker.dev.example`、`backend/.env.docker.prod.example` | 仅修正本任务直接影响的当前接口、collector／权限、旧能耗和版本说明；历史记录不倒写，真实 `.env` 不作为源码提交。 |
| `contracts/README.md`、`contracts/README.zh-CN.md`、`contracts/PLAN.md`、`contracts/PLAN.zh-CN.md`、`contracts/published/http-api/equipment-observation-v2/README.md`、`contracts/published/http-api/equipment-observation-v2/README.zh-CN.md` | 只说明本 Revision 的新活动范围与 v1 重放退出；保留已发布历史 OpenAPI、向量和可核对证据。不得改其他合同历史工件。 |
| `docs/equipment-status-process-monitoring.md`、`docs/equipment-status-process-monitoring.zh-CN.md`、`docs/equipment-status-process-monitoring-guide.md`、`docs/equipment-status-process-monitoring-guide.zh-CN.md` | 顶部当前说明及操作入口与清退一致；r6–r12 历史内容原样保留并明确其时点。 |
| `CODE_INDEX.md` | 只随本次实际源码结构变化更新。 |
| `plans/ARCH-OBS-002-legacy-observation-retirement/tasks.md` | 由实际 Development 在批准后创建并记录事实、自检与 handoff。 |
| `plans/ARCH-OBS-002-legacy-observation-retirement/checklist.md` | 仅由 fresh-context Verification 在 handoff 后创建并记录独立结论。 |
| 根 `PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md` | 仅由协调者在相应角色事实已存在后做机械状态索引；保留并行任务行和他人未提交内容。 |

真实 `backend/.env`、前端 `.env` 和外部私有 profile 不是源码 allowlist：唯一拟议 dev 配置动作见 §5.3，须对精确目标和操作另行明确授权，且只在维护窗口执行。Git、其他项目、历史 Alembic、其他任务 bundle、数据备份与生产制品均不在本任务默认写入面。

## 5. 实施、迁移与恢复方案

### 5.1 候选和隔离验证先行

1. 以当前正式交付工作树为事实，记录需触达文件及并行修改的 preimage；不覆盖其他任务。因当前后端可能从正式源码热更新，先在 `/private/tmp/arch-obs-002-r1-*` 自有目录制作排除真实 `.env`、私有 profile、数据库、密钥和构建产物的候选；须包含当前必要的未提交前驱迁移并核对候选与将来整合的内容一致。项目依赖沿用现有 `uv`／锁文件和 `pnpm`，不安装仅供 Agent 使用的项目依赖。
2. 在候选上完成静态检查、后端定向测试、前端构建与模块／授权检查，准备显式迁移和设备／过程／能耗合成测试。不得连接 3307 进行破坏性实验。候选仅是临时验证来源，最终必须整合至正式交付工作树并验证实际启动入口。
3. 拟请求仅为本任务各自创建、使用和回收两个隔离 MySQL：Development `arch-obs-002-r1-dev` 绑定 `127.0.0.1:13318`，Verification `arch-obs-002-r1-qa` 绑定 `127.0.0.1:13319`；仅使用本机已存在 `mysql:8.4.6` 镜像 `sha256:869218921e61d6c3c89820955d63cca42971f0e3e6c1e2792247bbd944ebc6e9`，不拉取镜像。2026-11-18 只读盘点该镜像为 arm64，两个端口当时无监听；创建前重查容器名、端口、镜像 ID、架构及目录，不符则停止，不复用或替换现有资源。容器和数据库只含本任务合成 schema、独立身份和任务私有临时数据；连接前后核对 container ID、server UUID、端口、schema、revision。停止／删除只针对本任务实际创建且已核对归属的容器与目录，不使用 Docker Compose up/down/build 或触及其他容器、volume。
4. 真实数据库、Docker 生命周期、私有配置或服务切换不由本草案自动授权；Owner 可在批准精确 r1 时或后续单独明确批准上述目标、操作和资源。无对应授权时，相关执行停止并如实记录，不使用其他数据库替代。

### 5.2 前向迁移及失败防护

- 新 revision 只接受 MySQL 8.4 和唯一精确前驱 `ae20b4d6f831`；校验连接实际 UUID、schema、时区与获得授权的目标一致，迁移使用显式目标参数，不依赖默认 `.env` 猜测。离线 SQL 不执行清退、不作为执行凭据；新源码对旧 revision 的设备观察请求 fail closed。
- 维护窗口须确认本任务所有相关应用／外部写入方静默，检查现有连接、锁、外键、视图、触发器、例程、事件以及已知调用方；账户无法完整查看依赖、存在未知引用、目标表不全／已部分删除或无法确认外部写入时停止。暂停手工实验不等于此条件成立。
- 18 表均为预期 InnoDB，逐表查空；`metric_ingest_receipts` 若存在 `contract_version != aiis.metric-ingest/v2`、`result_version != r10` 或指向旧归档／其他未知身份的记录则停止。合法 v2 回执可存在且必须保留。迁移前后核验受保护对象及所有入向／出向 FK，按子表先于父表的安全顺序处理内部关系；以有界锁和同连接复核消除查空到 DDL 的竞态，隔离 MySQL 上以竞争写入测试证明实际行为。不得使用 `FOREIGN_KEY_CHECKS=0`、`TRUNCATE`、全库清理、盲目 `stamp` 或绕过守卫。
- 只允许删除 §2.1 的 18 张空表和更新 §3 所述两个回执默认值；禁止删除任何业务记录。MySQL DDL 可能隐式提交或发生部分切换，实施前为旧空表记录可复建 DDL、版本和依赖，记录受保护数据的行数／可复核摘要及现有可用恢复材料。实际失败或提交结果未知时立即停止写入／重试，记录当前 revision、存在表、约束、默认值及原始错误，先核对真实执行状态，再由 Owner 另行决定恢复；不得自动猜测补删、降级或登记 revision。
- 本次前向清退后，旧 r8 的原恢复程序不能被默认视为仍可用；不得以重建空表声称恢复过旧数据。隔离验证应证明已记录 DDL 足以重建空表结构并能识别未登记或部分 DDL 状态。真实恢复及版本回退仍需单独明确授权。

### 5.3 实际 dev 的拟议动作（待额外明确授权）

目标仅限 `127.0.0.1:3307 / industrial_level_2_system`。候选隔离验证通过且并行任务冲突解除后，操作者先与 Human Owner 协调维护窗口，由用户自行暂停／恢复其服务，除非另行明确授权执行者操作具体进程。再次核对 UUID、schema、版本、外部客户端、活动事务及 18 表状态；任何非空、未知消费者、目标或版本变化均停止并报告。

经批准后，把精确候选整合至正式工作树；按指定前向迁移在该 dev 执行一次 DDL；核对受保护对象数据、索引、约束、价格和采集来源不变。只更新被实际采用的 PLC Facts 和设备观察私有 profile 中目标 `schemaRevision`，由 `ae20b4d6f831` 改为 `c9e1a3b5d720`；其他字段、授权范围、UUID 和文件权限保持。实际 profile 路径、属主、内容及旧摘要在私有渠道核对，不输出凭据，不创建真实设备或 producer。`backend/.env` 的已退役 `monitor` 成员按 §2.3 第 4 点另行授权后定点处理；前端 dev `.env` 不应因本次 pageId 方案而改写。若找到其他被采用且要求精确 schema revision 的 profile，记录并停止该部分切换，需明确授权后适配。

窗口内按用户确认顺序恢复或由用户自行恢复应用，确认实际运行版本与 DB/profile 一致；仅使用只读 GET、OpenAPI、数据库元数据和已有页面配置做 dev 核验，不在 dev 新增合成业务值。任一步失败或未知即停止并报告。原 3307 的 Docker 数据库不得停止、重建或切换；不触及其他目标。

### 5.4 资源与角色

Development 在 `tasks.md` 记录精确代码／迁移、检查命令、目标、pre/post 差异、权限处理、已知风险、临时目录与容器并提交 `developer_handoff`。之后命名 Verification 使用 `fork_turns="none"`，读取规格、交接与当前 diff，独立使用自身隔离目标验证，且对 dev 仅只读复核；它只写 checklist，不修实现或清理资源。协调者核对资源归属与证据持久化后回收本任务自有容器／临时文件；保留项写原因和触发条件。Owner 最终验收是独立 gate。

## 6. 验收标准

| 编号 | 可验证结果 |
| --- | --- |
| AC01 清退集合 | 源码 app registry、OpenAPI、实际受测数据库和前端 registry 按 §2 精确退出 18 表及 22 个旧 HTTP 方法；新版三路机器接口、发现、页面读取与管理继续注册；历史合同文件及任务证据存在。 |
| AC02 新版语义 | 合成同一设备／任务多区域整包分别写实时、历史，验证覆盖／缺测、晚到、同事件重试、不同正文冲突、权限和 `observedAt`；表计独立写入及统计与迁移前一致。旧 v1 请求被认证／鉴权后明确拒绝，不重放。 |
| AC03 前端与权限 | 四设备卡片、三过程曲线、配置／记录管理和新版能耗页可从菜单及当前 URL 到达；旧能耗页面和旧直链退出。两语言对称；`monitor.energy` 对应新版唯一页面，`monitor.consumption` 配置被显式识别为待迁移，角色、设备／表计 API scope 未自动扩大。验证管理员、supervisor、operator 和未授权用户的真实路由与 API 边界。 |
| AC04 迁移与保护 | 使用真实 MySQL 8.4 在独立合成库验证实际前驱到新 head，18 表退出且保护对象的值／约束／行数一致，v2 回执及价格保留，默认版本正确；检查采集、计划／实绩与观察 profile 匹配和旧 revision 拒绝。 |
| AC05 拒绝与恢复 | 分别构造旧表非空、旧或未知回执、外部 FK／可见对象引用、身份／schema／前驱不符、写入方未静默和锁竞争；迁移在删除前拒绝或竞争写入无法造成数据丢失。注入 DDL 中断／提交未知并证明不会自动跳过、盲目重跑、stamp 或删除受保护数据；证明空表 DDL 恢复材料可用。 |
| AC06 真实目标 | 仅在获得精确目标授权后，对 dev 记录实际迁移、配置动作、版本、18 表前后和所有保护数据对账，确认刚有的区域／指标、价格和采集历史仍在；检查新注册、旧操作退出和页面权限。无授权时准确记录为待办，不以隔离验证替代。 |
| AC07 交接与边界 | 旧 equipment／monitor 业务时间采用工具入口明确退出且不隐式连接；其他工具能力不得被静默改写。Development 实际自检、fresh-context Verification 独立结果、测试资源收尾和 Owner 最终验收分开记录；不宣称真实 SMA、DAA、PLC、生产部署或冻结 CA 在新 schema 兼容。 |

Development 使用 `backend-arch`、`frontend-ui`、`i18n-workflow`、`code-document-indexer` 和 `interface-lineage-audit`；涉及一次性 Docker 及 MySQL 诊断时按 `docker-expert`、`docker-project-ops`、`backend-script-tooling` 处理。仅验证静态代码或 SQLite 不能替代 MySQL DDL、权限、FK 和并发证据。

## 7. 待 Human Owner 决定

本 r1 是**待审草案**，不是已实施或已批准。请审阅：① 18 表和 22 个旧 HTTP 方法、旧 v1 重放及 collector 兼容的一次退出；② 旧能耗页退出、新能耗 URL 与复用 `monitor.energy` pageId 的权限含义；③ 仅旧表为空及依赖确认后执行；④ 是否明确授权 §5.1 的两个隔离容器，以及 §5.3 的精确 dev 迁移、私有 profile 和 backend `.env` 定点修改，服务由谁暂停与恢复。

## 8. Human Owner 精确批准与 Development 交接

2026-11-18（Asia/Shanghai），协调者就本规格精确 `ARCH-OBS-002 r1` 的开发和 §5.1 两个一次性隔离 MySQL 验证提出审批；Human Owner 的答复原文为：

> 批准 r1 和隔离验证

批准前规格 SHA-256 为 `7fdd51dc418da2acc5ac74213cb97dd79cb93bf254fc368759529c214461e881`。本次批准覆盖 r1 所列源码清退范围、验收和开发流程，以及 §5.1 明确列出的任务专属 Development／Verification 隔离容器、镜像、端口、合成数据库及其受控生命周期；执行前仍须核对精确资源身份、前提和工作树并行冲突。§1 和 §7 中“待审”“未批准”等措辞保留为批准前历史，上方 `Status` 与本节记录是本次范围批准的事实。

**本次批准不包含**对 `127.0.0.1:3307 / industrial_level_2_system` 的真实 dev 迁移或其他数据库写入、不包含真实私有 profile 或 `backend/.env`／前端 `.env` 修改，也不包含停止、启动或重载用户已有服务。§5.3 的这些动作仍须取得 Human Owner 对精确目标与操作的单独明确授权；用户暂停手动实验不等于其他写入方或服务已停。生产部署、发布、真实设备、DAA／SMA 和冻结 CA 操作仍在范围外。

协调者可按 canonical workflow 交接给实际命名 Development，在已批准边界内先准备候选、必要测试和自检。该批准不表示实现、隔离验证或 dev 切换已经执行，也不等于独立 QA 通过或 Human Owner 最终验收。必须完成实际 `developer_handoff` 后，才能启动新的 fresh-context Verification；若需越过上述 dev 门槛或扩大范围，先取得相应批准。
