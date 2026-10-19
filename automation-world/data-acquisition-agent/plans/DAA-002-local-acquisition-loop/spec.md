Task ID: DAA-002
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner approved exact DAA-002 r2 on 2026-10-17; Development may append r2 facts and rerun only the approved B0 dependency/native SQLite gate first; B1–B6 await B0 closure, then new fresh-context Verification and Human Owner final acceptance; r1 dev_blocked history is retained
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: DAA 阶段 B 的可配置本地 S7 采集、全结果持久队列与容量和重启恢复
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: aiis-ics-arch::DAA-002 r2 exact scope approval (owner_approved by the latest Human Owner decision; independent of r1) -> Development / new B0 gate -> new fresh-context QA / Verification -> Human Owner final acceptance
Depends On: aiis-ics-arch::DAA-001 r1 owner_accepted; aiis-ics-arch::ARCH-AW-003 r3 accepted design baseline
Related Task: aiis-ics-arch::CU-008 r1; aiis-ics-arch::ARCH-AW-001

# DAA 阶段 B：本地采集闭环实施规格

## 1. 当前效力、目标与需审阅的选择

2026-10-17（Asia/Shanghai），Human Owner 原话由主协调传递：

> 可以，验收 DAA-001 r1。接下来先出阶段 B 的实施 spec，明确范围、实施顺序和验收标准，批准后再改代码。

该决定在起草时只授权**起草本 spec**，不是批准当时尚未形成的 DAA-002 r1。PM 当时提交 `draft`，没有实施、安装依赖、构建、项目测试、启动、设备或数据库操作；当时 Development 尚不得创建 tasks 或写实现，Verification 尚不得创建 checklist。唯一 bundle 为 `automation-world/data-acquisition-agent/plans/DAA-002-local-acquisition-loop/`，由 DAA PLAN 管理；不另建根 bundle。

PM 提交的精确 r1 draft SHA-256 为 `4077ec3f908c7860db74abf9ae3f3ba54ede25fcbbdd408535d5b5542c1e9002`。2026-10-17（Asia/Shanghai），Human Owner 对该精确 DAA-002 r1 明确批准，原话由唯一 active lifecycle coordinator `/root` 传递：

> 可以，批准 DAA-002 r1，按 spec 完成阶段 B 本地采集闭环和独立核验。阶段 C 可靠上传暂不做，后端和 SMA 的具体开发仍留各自会话；真实 PLC、生产数据库/API 和现场切换不在本次范围。

PM提交的精确r2 draft SHA-256为 `41c65ef12e5431a1321d86e3b6c613a9cccbba0507e88790581597c601bba5ac`。2026-10-17（Asia/Shanghai），Human Owner明确批准该精确DAA-002 r2，最新原话由唯一active lifecycle coordinator `/root` 传递：

> 可以，批准 DAA-002 r2，按 spec 先重过 B0，再完成阶段 B 本地采集闭环和独立核验。阶段 C 可靠上传暂不做，后端和 SMA 的具体开发仍留各自会话；真实 PLC、生产数据库/API 和现场切换不在本次范围。

**最新有效状态为r2 `owner_approved`，精确范围批准G0已满足；新B0尚未执行/通过，B1–B6、独立QA与最终验收尚未发生。** 本次只记录真实批准及当前交接，r2 R01–R20、AC01–AC20、工程参数、全部有限allowlist、风险、B0停止条件和§11历史逐字保持。Development可保留r1失败历史并在其tasks追加r2事实，先进行R03所定最小依赖解析/仓外SQLite新探针；B0全部门槛通过前不得进入产品实现，失败继续blocked并回PM，不自动扩大范围。此批准不是SQLite安全结论、QA通过或Human Owner最终验收，也不授权C、Backend/SMA具体开发、真实PLC、生产数据库/API或现场切换。PM本轮不运行探针/构建/项目测试，不写tasks/checklist/索引/产品，不启动团队或执行窗口。

**时间效力说明：** 下列§1两段及§3/§5/§6/§10保留的“r2 draft／尚未批准／待批／G0当前pending”等，是r2起草/提交时的原文历史；仅其批准状态/当前handoff由本段及§10末段的最新决定覆盖，技术合同及先B0后B1–B6的顺序不变。r1批准和B0失败仍为真实历史，r2批准不使旧WAL probe成为DELETE+EXTRA验证。

**当前为 r2 `draft`；r1 已获精确范围批准，但其 B0 已真实 `dev_blocked`，r2 尚未批准。** r1 批准记录后的 spec SHA-256 为 `88859d45093d010cf7f1214d5f5975b93e5ffabde2ef0f69574bc7440247c819`。实际 Development 仅完成受限依赖解析/仓外原生 SQLite 探针并按原 R03 停止；没有开始 B1–B6，87 个产品路径未改，没有项目构建、native 闭环、developer_handoff、QA checklist 或最终验收。当前 [tasks.md](tasks.md) 是 **r1 `dev_blocked` 历史**，不改成 r2，也不为凑齐 bundle 建 checklist；关键事实/指纹见§2.1。

本次仅授权 PM 起草本 r2 spec，不继承或重解释 r1 批准。**待 Human Owner 精确批准 DAA-002 r2 后**，Development 才可在原有限路径内更新自己的事实记录并重过 B0；B0 之前仍只准最小依赖解析/仓外 SQLite 探针，失败即停，不自动升级 ORM/SQLx、补原生源码、换架构或降低验收。本文§1–10为 r2 待批合同；§11保留被替换的 r1 原条款及原 SHA，其他业务段落/路径明确沿用。本轮 PM 仅写本文件并做文档/证据只读核对，不运行新参数探针、构建、项目测试或运行时。C、Backend/SMA 具体开发、真实 PLC、生产数据库/API、真实 profile/现场切换始终排除。

本任务是独立 `root`，无 Parent Task ID。ARCH-AW-003 的文档验收、DAA-001 的阶段 A 验收、CU-008 的公共组件验收只提供输入，不转移范围批准、QA 或最终验收。角色为 `contract_only`，以真实角色调用、完整 bundle、串行 handoff 和差异审计控制；不宣称平台 ACL、强制路由或团队激活。

以下六项为 r2 待审工程取舍；第1–4及6项原文沿用 r1。**只修订第5项的本地日志/同步模式、精确兼容依赖选择及其必要 gate、容量/恢复/读写并发验证**，不缩减本地闭环或20项AC。全部数值是待精确批准的准入上限/默认值，不是已测现场能力：

1. 首版最多 **4 PLC、每 PLC 8 组、每 PLC 4096 个完整结构叶、每组 256 个启用点**，最低组周期 **500ms**，默认 1000ms。超限拒绝激活；周期不保证等时完成，过载记录跳过的调度机会，不补造样本。
2. 完整导入、保存和展开无环 Struct/UDT 及一维常量数组；**辅助偏移推算仅支持完整平铺、标准非优化 DB 内的受支持标量**。嵌套结构/UDT/数组及 STRING 的叶地址需人工输入和确认后才能采集；不宣称完整 UDT 自动推算或全 TIA 语言支持。
3. 新 `local_sqlite` 与原 `legacy_snapshot` 为启动时互斥模式。默认保持旧模式；B 不静默迁移真实 YAML/profile、旧库或生产来源。新模式不使用旧 raw/latest writer、不探测 Backend health、不启动旧 headless/autostart。
4. B 没有上传器。所有实际采样均进入本地 `pending`，**不能假 ACK、按天删未确认数据或靠清队列持续运行**；因此持续采样最终会达到容量暂停。ACK/保护清理分支只在私有隔离测试种子中验证，没有产品 markUploaded/markAck 入口。
5. 双 SQLite 提议改为 **rollback `journal_mode=DELETE` + `synchronous=EXTRA(3)`**，不再承诺 WAL/checkpoint；固定兼容 `rusqlite=0.32.1` bundled / `libsqlite3-sys=0.30.1`，旧 SeaORM/SQLx/Tauri/Snap7 不升级。**EXTRA 比候选 DELETE+FULL 多一次日志删除后的目录同步**，用于保持 COMMIT 后的耐久目标；代价是提交 I/O 与读写互斥，需重过 B0。3.46.0 未获 WAL 修复，本方案仅移除该缺陷的 WAL 前提，不宣称版本已修复或全面安全。实际新参数、短读/锁、hot journal恢复、容量预算及当前已知问题适用性尚未验证；失败只阻塞实施。
6. 重启先恢复配置、原样本、待传及源序号，再要求人工恢复连接/采集；不启动后台托管或自动连接。B 必须取得**真实原生 IPC → Rust → SQLite** 的隔离 GUI 证据；仅浏览器假桥不满足本地闭环验收。

目标是让使用者在现有四页完成“保存 PLC 草稿 → 导入完整结构并确认地址/组 → 激活 → 明确连接/启采 → 查看持久历史与待传 → 停采/重启后核对恢复”。本地闭环是 B 的必需交付，不拆成只有表单或脚手架的终态；B0–B6 是同一批准范围内的串行里程碑，不代表额外任务已完成或各自可代替整项验收。

## 2. 消费依据、真实前置与现状

r1 起草时 PM 已读根 AGENTS、README/PLAN 双语、canonical lifecycle workflow、实际 pm TOML，AW/DAA 最近 README/PLAN 和 DAA `src/app/README.*`，ARCH-AW-003、DAA-001、CU-008 完整已形成 bundle，以及 774 行 [DAA 详细设计](../../../../docs/AIIS_DAA_Detailed_Design.md)；使用 `aiis`（含 BLUEPRINT/CONTRACTS）和 `project-governance`。作用域检索无更近 AGENTS。只读检查 DAA Rust/前端/依赖与 `tools/plc/point-mapping` 解析/结构校验参考，当时未联网。r2 再读当前治理/完整 bundle、DEV receipt/resolver/probe 文本，并联网核对下列 SQLite 官方说明；不读取真实 env、用户 profile/数据库，不启动项目或访问项目 API/设备。

DAA-001 最新 [checklist](../DAA-001-cu-layout-migration/checklist.md) 已真实记录 `owner_accepted` 和上方原话，QA2 `qa_passed`、F-001/F-002 关闭及 QA1 失败原文保留。CU-008 r1 也有真实 owner_accepted。旧设计正文的“当前未接 CU/二级导航未实现”等描述是设计修订当时事实；本 spec 以阶段 A 后的实际源码为起点，不反改已验收设计/历史。

HEAD 上下文为 `f85bea8bbf36b491968c3dc9a839518a1ed434a8`，实际交付起点是已有并发 dirty/untracked 的工作树；HEAD 不替代实际字节。下表 SHA-256 为本轮只读快照，Development 写前重新核对并固定自己的起点：

| 依据/源码（仓根相对） | SHA-256 / 已核实事实 |
| --- | --- |
| `docs/AIIS_DAA_Detailed_Design.md` | `20071f25c374f40ee4600bffda4aef13f37bb86a82c2a6cd1f19e2580370a576`；§16 的 B/C 边界为设计依据。 |
| `automation-world/data-acquisition-agent/plans/DAA-001-cu-layout-migration/spec.md` | `ce9887b1c1d054384db2f03bac2bb9ddcbc78d480c6469510306feae2ae0c0e4`；已批准 r1。 |
| 同 bundle `tasks.md` | `64665ac5570b9654ffcef57a6c82eec244fb2792d79ec3ac13be1d976b5060ff`；§7 为当前返工交接，§1–6 为旧 handoff。 |
| 同 bundle `checklist.md` | `a2826adad5303beab3e7a04b9d4f055fab2e4fc188284d6862496fbc26440889`；真实终验；不是原 QA2 尚待终验的 SHA。 |
| `automation-world/console-ui/plans/CU-008-grouped-sidebar-navigation/checklist.md` | `7e8790d6f215df4c871d6157aec0babf98259671165441d1153547c5713f9199`；已验收公共源码消费输入。 |
| DAA `src-tauri/Cargo.toml` | `f49f5436b29e676239766ad3ab8b81f96a3dd629bfef6e8f67258ace8bc5e3d6`；SeaORM 当前启 MySQL；无本地配置/采样 SQLite 实现。 |
| DAA `src-tauri/Cargo.lock` | `32198f09c15dd227ad929bc1715cea8dfd03c70d5fbbf9e40f76cc2ec1f238f8`；rust-snap7=1.142.2；出现 sqlx-sqlite/libsqlite3-sys 的锁记录不证明本地库或安全版本已启用。 |
| DAA `src-tauri/src/infrastructure/rust_snap7_adapter.rs` | `604041cf2c01b25dfddb948120a0376257b427ae5eff44fd18abec819b35c764`；设置 RemotePort/超时，但 DB 读为 create/connect/read/disconnect。 |
| DAA `src-tauri/src/domain/plc.rs` | `08345f685d1ef2aaf516e95b47fe861686ad49dddd5e31d81dd6744385ec5980`；旧 group 只含一个 db_number/start/size，无稳定新 ID/跨 DB 组。 |
| DAA `src-tauri/src/services/plc_collection.rs` | `c2901540c7e0d036936fc52db5f74b0600546cdf772b1a861ff802d2f683a45e`；统一 env 周期、按 PLC worker，旧 write_snapshot 直库。 |
| DAA `src-tauri/src/infrastructure/plc_decode.rs` | `fd3b9defd49b520bd780787e6790d65508bbc9f98b0269e883411e1187c24961`；诊断字符串解码，REAL 格式化三位；不能直接充当无损新事实类型合同。 |
| DAA `src/services/runtimeSnapshot.ts` | `5c764dfb0e3ce04e3b7ed0bbb5284ac3768b81c96aa4d97cb350ff1a7d2cfa63`；旧 IPC/fallback/health GET，不能用于新模式的安全本地快照。 |
| DAA `src/App.vue` | `a8037a9f2321a0794e69257a5eb9cbccf5900d6a40d8ba8ea3ec81c5d4e0bc9f`；已消费 CU 四叶页，只有一个旧运行状态 owner；没有新配置保存服务。 |
| `tools/plc/point-mapping/src-python/source_parser/tia.py` | `d6f6e801d781e462be807ceea884e680e4404654dcd2b77176bd2176cbbde9db`；离线 Python 结构参考，不是已验证 Rust 解析器/偏移算法；B 不导入其依赖或改工具。 |

| 表面 | 阶段 A 后当前事实 | B 必须新增的结果 |
| --- | --- | --- |
| 四页/CU/主题语言 | 公共源码消费已验收；页面以 YAML/env/旧直库为真相 | 四页继续复用，local 模式显示自己的配置/历史/容量实态 |
| 配置/点位 | 只读摘要及所选 PLC 一次读取；无真实保存/激活 | 本地草稿、完整结构、受限地址校验、稳定身份和版本激活 |
| 采集 | 旧按 DB 短连接、统一周期、旧 writer | 每 PLC 一个串行会话、跨 DB 组独立时钟、全结果单库事务 |
| 本地数据 | 无新双库、持久 pending/ACK/恢复合同 | 原样本、解释版本、序号、pending、容量停采和恢复 |
| 上传/Backend/SMA | 新合同/链路未实现 | B 只保留待传和只读本地包预览；C 才实现正式上传 |

### 2.1. r1 B0 的真实失败与证据

2026-10-17（Asia/Shanghai），实际 Development `/root/daa_stage_b_development` 在固定旧 SeaORM=1.1.20、SQLx=0.8.6、Tauri=2.11.3、tauri-build=2.6.3、rust-snap7=1.142.2 和原锁后取得以下结果；PM 只读复核原输出/源码/指纹，没有重跑：

| 输入与已发生动作 | 结果；不能据此推断的结论 |
| --- | --- |
| 仓外复制原依赖/锁，新增 `rusqlite=0.40.2` bundled，精确固定旧链路 | 最终 `cargo metadata` exit101；rusqlite→libsqlite3-sys^0.38.2 与 sqlx-sqlite0.8.6→^0.30.1 违反同一 `links=sqlite3` 规则；不是产品可链接组合。 |
| 同样约束，改 `rusqlite=0.32.1` bundled、uuid=1.23.3+v4、sha2=0.10.9、fs2=0.4.3 | metadata exit0，新增7包；所有旧 registry 版本/checksum保持，原libsys仅增cc build依赖，sqlx-core的hashlink只补版本消歧。没有升级 ORM/SQLx/Tauri/Snap7。 |
| 仓外 probe 的 libsys版本/依赖/features 与完整解析图逐字段相同 | run exit0，实际静态 bundled **SQLite3.46.0**；source ID `2024-05-23 13:25:27 96c92aba00c8375bc32fafcdf12429c58bd8aabfcadab6683e35bbb9cdebf19e`，两连接 WAL/FULL/其余PRAGMA读回正确、1行读回、integrity_check=ok。只证明该候选和旧参数可运行；不满足 r1 官方修复 gate，也未验证 DELETE/EXTRA。 |

永久事实面是本 spec 的历史摘要和 r1 [Development记录](tasks.md)；临时附件是可复核补充，不能代替这些事实：

| 证据（`/private/tmp/daa-002-r1-gvbvdzx3/dev/` 下，除注明者） | SHA-256 |
| --- | --- |
| 本 bundle `tasks.md`（r1 dev_blocked） | `7ffdc1600534efe4605ff7a022d9c8bc16a7f68d19748ccb0590cff759d607ef` |
| `blocked-handoff-receipt.json` | `9ad952a353ba4642d1a75ee858fc618136b1bfbfb6fe84db3a624379ed6dce2a` |
| `development.patch`（仅新增 tasks 全文） | `1e72c28a63d328e77df26316143a8607038bf778ec31f500b4fff3df3227aac5` |
| `resolver-current-pinned-final.stderr` / `.result.json` | `c33db541c86939ddaf8346358455c9d91da9693a2b5626f5d3d6c8b814625768` / `82a138db0888241f8c1b1fd9461047a563fa1c5951fcdd12ff5eb62af81119c4` |
| `resolver-compatible-pinned.result.json` / `resolution-audit.json` | `dd9beaa4e13c3521772c5c1425020f2836ce0440a6061870278f955fddf7d2fd` / `3276afa60a82f43fa411f57b713582738d2e12d7a251250e37baa93c18a65e7d` |
| `native-provenance.json` / `sqlite-probe-matched-run.stdout` | `a02731709dd53e7800a59743abbb87331d1bad48477018f7911af1381701d1fc` / `6b84b500e9f53e64b7da21c0395d7621a51c65ee944ff74429a0ad8043bbabf3` |
| `final-scope-audit.json` | `ac811329039c25e051d5699b193ddd6309a7e0e81bf29e09cdff8c53ad83b0ac`；12项变更=PM批准spec+主协调10索引+DEV tasks，1559保护/87产品路径/HEAD保持 |

实际amalgamation SHA为 `c01235302fe80da901fb70c7622c39147e29d9f29b7f6eb746b23517f320c90d`；probe仅动态链接libSystem而非系统SQLite。该证据没有产品构建/GUI/现场或独立QA含义。r1原R03要求不含修复即停、不得关闭WAL或以单writer豁免；Development遵照停止，原文见§11。r2改变这一合同必须重新批准。

### 2.2. r2 最小修订的依据与候选比较

PM于2026-10-17只读核对官方材料后的**设计推论**如下；不是新的运行验证：

- [WAL §11](https://sqlite.org/wal.html#the_wal_reset_bug) 将已知 WAL-reset 的前提限定为 WAL、多连接及写入/checkpoint竞态，修复列为3.51.3+或3.44.6/3.50.7回补。3.46.0不含修复；**强制新库一直DELETE且拒绝WAL，不是以单writer免除WAL缺陷**，只是该特定前提不成立。不能据此豁免其他适用问题。
- [Atomic Commit](https://sqlite.org/atomiccommit.html) 说明先保留旧页并同步journal、再更新/同步主库、以删除journal完成单库提交；[locking/hot journal](https://sqlite.org/lockingv3.html#hot_journals) 要求读取前恢复未完成事务，读锁会阻塞提交。故保留同库全结果事务、双库token协议；采用串行写/有界短读，不承诺WAL式读写并行。
- [synchronous 官方合同](https://sqlite.org/pragma.html#pragma_synchronous) 明确 DELETE+FULL 在某些文件系统上紧接提交断电仍可能丢最后事务，EXTRA增加journal删除后的目录同步。为保持原耐久目标，**r2选DELETE+EXTRA，而非直接沿用候选FULL**；依赖OS/VFS/存储正确同步的限制仍存在，强杀测试不能当真实断电证明。
- [后续修复记录](https://sqlite.org/changes.html) 也列有3.46.1覆盖索引预测修复、3.47.0的unix-dotfile hot-journal修复等，不能把“非WAL”写成“3.46全部已知问题已排除”。本方案只用内建默认本机VFS、受控schema/参数化SQL和JSON文本payload，不用unix-dotfile/自定义VFS、WASM/OPFS、扩展加载或任意用户SQL。B0须核实际VFS与拟用SQL/索引的适用条件；B1落定SQL后再次核验。可达正确性问题或无法证明关键恢复条件时仍blocked，不以用例恰好通过替代适用性判断。

| 候选 | 影响与当前证据 | r2决定 |
| --- | --- | --- |
| 保留旧依赖；兼容rusqlite0.32.1 bundled，DELETE+EXTRA | 已有兼容解析/原生来源依据，但新日志/同步、读写锁和恢复/容量尚需新B0及后续AC验证；提交更慢、读写互斥 | **推荐的最小待批修订**；只改本地存储机制及其必要合同/验证，现有限路径可承载 |
| 升级SeaORM/SQLx闭包以链接含WAL修复的新SQLite | 没有已解析/构建证据；扩大旧MySQL兼容链和回归范围，不止本地双库 | 不纳入r2，不以本次批准暗含升级；若最小方案失败再回PM |
| 自定义SQLite backport/vendor或改系统原生库 | 没有可复核补丁/构建；新增原生源码来源、补丁与持续维护责任 | 不纳入r2，禁止偷偷patch/vendor/替换；需另一个明确修订和批准 |

已验收 [ARCH-AW-003设计](../../../../docs/AIIS_DAA_Detailed_Design.md) 把SQLite参数留给实施spec；本次不修订设计。全部多PLC/完整结构/受限offset/稳定身份/全结果/pending/容量停采/恢复/四页/native真IPC与20项AC保持。新风险在本spec显式批准，不能从r1的WAL条款推断新实现权限。

## 3. 精确范围、排除项与工程参数

包括新模式的本地 schema-maintenance、草稿和激活、完整 DB/UDT 导入、受限推算/人工地址、分组、只读 S7 会话、调度、原子本地事实/待传、容量/恢复、真实四页操作、最小历史浏览和隔离验证。旧 YAML 可由用户**显式选择文件**导入候选草稿做对照，不能据仅含已选点的 YAML 推断完整结构；本任务不迁移旧历史数据。

排除 Backend/SMA/CA/CU/tools 源码或配置变更、正式跨端事实 API/contracts/鉴权/回执/来源交接、上传器/冻结 HTTP 批次/最新优先补传、业务 SQL/Projection、PLC 写入/控制命令、优化 DB/符号访问、全 TIA 编译器、流程画布/任意 JSON 编辑、Excel 工具集成、配置备份恢复产品、系统凭据库、中央配置、Celery/Redis、开机/后台托管、跨平台原生交付/签名打包、真实 PLC/TIA/远程数据库/API、生产切换/回滚/迁移、Docker、Git refs/提交/推送/发布。配置保存、本地采集不要求 Backend 或 SMA 完成。

| 项 | r2 待精确批准的工程准入/默认值（除SQLite及短读相关项外沿用r1） |
| --- | --- |
| 规模 | 实例 ≤4 PLC；每 PLC ≤8 组、≤32 DB、≤4096 展开叶；每组 ≤256 启用点；跨 DB 可用，超过拒绝激活 |
| 输入结构 | UTF-8/UTF-8 BOM `.db/.udt` 文本，每文件 ≤1MiB、一次导入总计 ≤4MiB；展开深度 ≤8；每个一维数组 ≤1024 元素；整个配置 JSON ≤16MiB |
| 周期 | 组 500–3,600,000ms，默认 1000ms；使用单调时钟；不是现场最低可达时延或实时保证 |
| S7 | 仅 `rust_snap7` 及现有 `rust-snap7-driver` feature；IPv4、port 1–65535（默认102）、rack 0–7/slot 0–31；不做 DNS、自动发现或 silent driver fallback；自定义端口须由受控驱动测试证明 |
| 读取 | 按 DB 合并重叠/直接相邻范围，不跨空洞合并；每段 ≤200 字节，段边界可拼回单点；每组 ≤32 段、原始读取预算 ≤6400 字节；不以一次 DB 调用等同一次网络包 |
| 超时/重连 | connect 1000ms、send/recv 各500ms；组 deadline 5000ms；重连 1/2/4/8/16/30s 上限并加0–20%正抖动；成功后重置；参数由 SQLite 版本控制，不能由旧 env 覆盖 |
| 有界工作 | 每 PLC 一个 actor/拥有客户端的线程、一个在执行轮次；每 PLC 诊断排队 ≤4、执行频率 ≤1次/秒；写入结果队列 ≤4 轮、单轮自描述编码 ≤512KiB |
| SQLite | 内建默认本机VFS，page_size=4096、建库前 auto_vacuum=INCREMENTAL、journal_mode=DELETE、synchronous=EXTRA(3)、foreign_keys=ON、busy_timeout=1000ms；逐连接核实际值，禁止WAL/checkpoint/自动日志模式转换 |
| 存储短读 | 每库单写；实例统一串行写调度，页/单包查询有界，最多一条执行中的查询、最多4条查询排队；页≤100条、原包≤512KiB，查询软deadline1000ms；释放statement/读事务后才回复或等待UI，超时中断并如实报pending/失败，不声称能硬中断文件系统I/O |
| 容量 | runtime 默认1GiB，可配置128MiB–64GiB；预警80%、停新轮90%、恢复70%；安全维护预留32MiB且计入准入；系统最低空闲512MiB；配置库预算64MiB、持久日志合计32MiB，均另占系统余量 |
| 保留/查询 | 已确认历史默认7天、可设1–30天，仅对具备清理资格者；草稿1份、保留最近8个完整配置版本（active/previous/应用中版本保护）；历史分页默认50、最大100，日志单次最大200、UI内存最大500条；快照轮询最多1Hz |

这些上限在服务端执行。没有满足读取/编码/维护预算的配置不得激活，不截断成员、不静默放宽周期/限额。用于压力/时钟/空间状态机的测试可用更小私有限额和虚拟时钟；测试值不得写成产品默认或现场容量实测。高低水位同时满足实际字节、在途保留和系统空闲条件，不能只按记录条数判断。

## 4. 编号需求与本地合同

### R01. 批准与起点

精确 r2 批准前不恢复Development；r1 tasks/dev_blocked原文作为历史保留。批准后Development才追加r2事实记录，固定r2批准spec SHA、当前源码/锁文件/17项CU公共源摘要、dirty起点及受保护面；从DAA-001当前QA2字节继续。只把本任务实际增量交接，不reset/restore他人工作或r1失败证据。新的B0未过不能开始B1–B6或把旧probe当新参数通过。

### R02. 模式、启动与旧路径互斥

增加启动键 `DAA_RUNTIME_MODE=legacy_snapshot|local_sqlite`，缺省为 legacy_snapshot；非法值 fail closed。新模式必须显式启用 `DAA_LOCAL_STORAGE_ENABLED=true`，使用 profile 下独立 `local-acquisition-v1/` 目录并取得 profile 独占 OS 文件锁；GUI 与旧 headless/第二进程不能同时持有同一 profile。进程内模式不可热切换；改模式须停止并重新启动。

local 模式只消费启动定位、只读 PLC 总 gate、日志定位及本模式必要键；业务 endpoint/周期/分组/地址权威归 SQLite。旧 DB enabled/write/autostart/全局 endpoint override 与 local 模式冲突时显式拒绝，不复用旧 env 覆盖业务配置。新采集总 gate 为 `DAA_PLC_READ_ALLOWED`，默认 false；本地采样持久化不能被旧 `DAA_PLC_WRITE_ALLOWED` 或数据库 gate 替代，也不提供“采了但不保存”的正式运行开关。

local 模式下旧快照/诊断/collection IPC、旧 `--ca-*` CLI 和旧 headless runtime 入口都应在调用旧服务之前返回 `wrong_runtime_mode`；不会调用旧 writer、旧授权外发、自检副作用、Backend health 或旧 autostart。legacy 模式保持原配置/命令/旧界面语义，新 IPC 拒绝跨模式写入。新启动只装载本地配置与安全快照，连接和采集均 stopped；点击导航、选择 PLC、主题/语言、查看历史不连接/读取 PLC。profile 锁不宣称能阻止其他应用/不同 profile 的现场双采；真实来源切换仍另批。

### R03. B0 依赖与 SQLite 技术 gate

本地repository固定 `rusqlite = "=0.32.1"`、`features=["bundled"]`，统一 `libsqlite3-sys=0.30.1`；`uuid=1.23.3`+v4、`sha2=0.10.9`、`fs2=0.4.3` 是允许的最小直接依赖。旧锁中的SeaORM1.1.20/SQLx0.8.6/Tauri2.11.3/tauri-build2.6.3/Snap7=1.142.2及其既有features不升级。沿用已成功解析的兼容候选，不启用第二套本地ORM；仅新增依赖必需闭包、根package记录、bundled引入cc及hashlink版本消歧可改Cargo.lock，所有旧registry版本/checksum保持。不得全量cargo update、改pnpm依赖/锁、引入系统SQLite覆盖或vendor/backport；若额外feature/依赖不可避免，先回PM，不靠r2概括授权扩张。

**新B0必须在r2精确批准后、B1前完成，先限于仓外复制依赖/锁的解析与一次性临时SQLite探针：**

1. 重核旧registry版本/checksum与精确pin、Cargo links/feature闭包；记录应用同一解析图下实际SQLite/source ID、compile_options、amalgamation SHA/链接来源。旧3.46.0证据可作对照，不能跳过r2来源/选项复核。
2. 新建双临时库与至少两连接，逐连接设置/重读DELETE、EXTRA=3及§3其他PRAGMA；新库不产生WAL/SHM，不调用checkpoint。只接收r2新目录/自身已标记DELETE库，发现既有WAL/SHM或不符日志模式则停，不自动切换/删除材料。记录默认VFS；不选unix-dotfile或自定义VFS，不加载扩展/任意SQL。此gate不读取真实profile。
3. 按§2.2官方资料重核当下明确问题的版本、触发前提及拟用SQL/schema/VFS；保留WAL-reset未修复事实，逐条说明为何本DELETE路径不触发，不能写“SQLite全面安全”。3.46.1覆盖索引等后续正确性修复与代表查询对照；关键适用性不清或已知可达缺陷未解决，仍blocked。B1落定实际SQL/索引后更新同一核验，不能靠B0代表查询免除后续审查。
4. 仓外probe验证DELETE事务提交/另一连接读回/完整性，受控读锁阻塞提交→busy/释放→原子重试，以及未提交且已形成hot journal时强杀→重新打开由SQLite恢复；不手工删journal。核对所有已提交/回滚行与seq/pending等价代表记录无半组。演练只是原生参数/机制gate，不伪称断电或项目实现完成。
5. probe记录代表事务主库增长和-journal实际峰值；注入受控空间meter/写失败，验证回滚/重开不删journal且无假提交，并验证有界短读、busy/软deadline中断后释放锁、后续提交可推进。不得真的填满宿主磁盘。此为新模式基本可行性gate；B1–B4还须按最终SQL/schema、全部在途/维护预算及实际结果验证AC04/AC12/AC15/AC16，原生真IPC仍必做，不能把代表probe当产品容量和闭环通过。

**任一解析/来源/逐连接参数/锁或恢复/已知问题适用性门槛未满足，或必须升级旧链路/增加allowlist/降同步强度时，记B0 blocked并停止B1–B6，回PM新Revision。** 不允许回FULL/NORMAL/OFF、用MEMORY/PERSIST/WAL替代、以单writer/低概率/测试未复现豁免，或继续产品实现再补gate。DELETE+EXTRA未在本PM轮次probe；其同步仍依赖OS/VFS/硬件正确实现，不承诺绝对硬件耐久。

### R04. 显式双库 schema-maintenance

本任务明确授权**后续在新模式的新本地目录**创建和验证 config.sqlite/runtime.sqlite schema v1，属于本地 schema-maintenance；不是 Backend Alembic 或真实数据库迁移授权。各库有独立 application_id/user_version、迁移记录和完整性核对；空目录才可初始化两库，事务性建表失败不报告初始化成功。已有任一库而另一库丢失、版本更高、身份不符或损坏时保持停采，不自动重建、降级或拼接。

物理合同如下，逻辑字段/唯一约束原样沿用r1；SQL/编码实现归r2批准后Development，在以下局部模型内落定并写tasks，不发布为Backend DDL：

| 库/表 | 最小内容与约束 |
| --- | --- |
| config: `instance_metadata` | 单实例身份、local schema版本；与 runtime 身份匹配；IP/名称不是 ID |
| config: `source_documents` | 明确导入的源内容、文件名、SHA、编码/解析诊断；按内容去重，有大小/引用限制 |
| config: `configuration_draft` | 单份完整候选、draft etag、source 引用及校验问题；CAS 保存，不悄悄 last-write-wins |
| config: `configuration_revisions` | 不可变 revision ID、local configuration schema版本、规范内容/摘要、创建时间 |
| config: `active_selection` / `activation_intents` | 唯一 active/previous；token、预期旧/新 revision、可恢复 phase；最多一个应用中意图 |
| runtime: `runtime_metadata` / `plc_sources` | 实例绑定、每 PLC sourceGeneration/next sourceSeq，唯一 `(plcId,generation)` |
| runtime: `configuration_contexts` / `activation_journal` | 不可变解释摘要/当时成员/类型地址、revision摘要、激活token/阶段；不是第二可编辑配置源 |
| runtime: `collection_cycles` | cycleId、PLC/代次/seq/group/revision、完整预期成员manifest、实际起止/保存时间、质量/摘要；唯一 `(plcId,generation,sourceSeq)` |
| runtime: `samples` | 不可变 sampleId、cycle、DB逻辑包、自描述points、local sample schema版本/内容摘要；唯一 `(cycleId,dbNumber)`，r1 本地不分片 |
| runtime: `sample_delivery` / `sample_references` | 每sample一条pending/ack账本及独立保护引用；B产品只创建pending，ack字段空；引用保护供局部清理/测试，未实现HTTP批次 |
| runtime: `runtime_events` | 有界必要状态变化、恢复/停采区间/不能确认的缺口；不可用日志替代样本账本 |

每库单写协调，实例统一串行执行写事务；SQL/文件/驱动细节归infrastructure，command/service不构造SQL。事务内不等待PLC/网络/UI，两库不使用ATTACH或跨库SQL原子承诺。历史查询限§3队列/页/包/deadline，参数化索引游标，列表只取有界元数据、原包按详情单独取，不跨页/跨IPC持有statement或读事务；读写竞争如实返回storage_busy/timeout并保留最近快照，不能拖长读锁或无限重试。写入有界队列/背压优先，查询不能饿死提交；持续写入也须给短查询有限机会。查询中断未确认结束时不复用连接开始下一数据库工作，不把软deadline说成能取消磁盘阻塞。

配置库仅安全回收非active/previous/应用中且已不需编辑引用的旧完整版本/源；历史所需解释内容已可靠保存在runtime.sqlite的configuration_contexts才可释放旧配置正文。不能借版本保留删除历史解释。只用本任务控制的普通表/索引/参数化SQL及原JSON文本payload；不启用扩展、任意用户SQL、FTS/自定义VFS来扩大存储面。

### R05. 配置草稿、稳定身份与并发修改

GUI 可新增/编辑/停用 PLC，导入/编辑完整点位与组，保存草稿、重新读取、校验并应用。PLC/group/point/DB source 身份为稳定 opaque ID；点名、IP、所属组、周期变化不自动换 pointId。重导入必须预览身份匹配、增删改和旧人工地址；只对有明确来源/结构路径映射的项保留 ID，歧义由用户逐项确认，不能按同名自动复用。删除/重建默认新 ID，历史不级联删。

草稿 etag 与 expected active revision 防并发覆盖；过期请求返回冲突和当前版本，不能报告已保存。保存和读取在 Rust/SQLite 完成后才反馈“草稿已保存”，不以 localStorage 或页面内对象当权威。新建点默认 disabled/未分组，导入不自动启用。一个点只有一个 enabled 与可选 groupId，没有第二套上报勾选。

### R06. 完整源解析与明确拒绝

实现 Rust 本地文本解析，保留完整声明顺序、注释/路径、Struct/UDT 引用、数组上下界和 source SHA，完整结构与采集选择分开。支持 DATA_BLOCK/TYPE、命名字段、嵌套 Struct、无环 UDT、多级引用以及一维常量范围 `ARRAY[a..b] OF 标量/UDT/Struct`（a≤b，可负起点）；展开每个叶并保留结构节点。不执行 PLC 初始化表达式/源代码。

缺 UDT、循环引用、重复符号、语法不完整、超限、优化访问标记为 true/未知、动态/多维/嵌套数组、unsupported类型、AT/指针/VARIANT/FB实例等必须定位文件/行/结构路径，不能像宽松扫描器一样忽略无法识别的字段后宣称完整。源可保留为有问题草稿，但相关 DB 不可启用采集或推算；其他已验证 DB 的边界不得被跳过字段破坏。legacy YAML 仅显式导入候选字段/连接/旧分组对照，标记结构不完整；不回写文件、不覆盖 active，也不据此辅助推算。

### R07. 类型、地址、受限推算与解码

只读支持 BOOL、BYTE/USINT、CHAR、INT/UINT/WORD、DINT/UDINT/DWORD、REAL、显式 `STRING[n]`（1≤n≤254）。BOOL 必须有 bit 0–7；其余无 bit；byte offset非负，叶读段不得越过配置DB长度或65536字节界；整数按有/无符号及大端解码，WORD/DWORD输出整数，REAL保实际有限数值而非格式化三位；CHAR/STRING首版仅ASCII，STRING含两字节头并校验声明最大/当前长度和容量。非有限REAL/非法编码/长度产生 null+明确质量/原因，不填旧值或0。TIME/DATE/LREAL/64位整数/宽字符及其他类型不启用；UI显示支持限制。

辅助推算只对**整个 DB 已证明完整且平铺、标准非优化、无 Struct/UDT/数组/STRING 等不支持推算节点**的上述8/16/32位标量运行：BOOL按连续bit游标打包；遇非BOOL结束bit域；8位按下一字节，16/32位先对齐偶数字节，再按类型宽度前进；DB末端取偶数字节。必须有独立预期offset夹具和官方布局依据，无法证明某布局即拒绝推算，不以递归猜stride代替。

每次手动触发先返回旧/新地址与影响列表，确认后写**草稿**。人工覆盖记录来源/原因，重算不静默覆盖。复杂结构、UDT、数组和STRING可完整导入/展开，逐叶输入显式地址/长度并由用户确认后校验/采集；不猜数组stride或隐藏padding。重导入涉及类型/结构变化时受影响地址需再次确认；人工地址只证明用户已确认，不证明与真实TIA/PLC一致。激活校验读范围、bit、重叠/冲突、类型长度及全部启用叶；B不做现场校核。

### R08. 跨 DB 组与准入

每组仅属一个PLC，可引用该PLC多个DB的部分叶；同点最多归一组，跨PLC引用/重复归属/不存在的点均拒绝。只有PLC/组/点同时enabled且已分组/地址确认者形成采样成员，未分组明确不采。保留“整个DB建组”快捷选择，但仍受单点单组和读取/编码预算校验。变更成员先进入新revision，不修改在途轮次。停用点/组保留完整结构、历史、待传和身份。

### R09. 可恢复激活屏障

按 [详细设计 §5](../../../../docs/AIIS_DAA_Detailed_Design.md#storage) 实施实例级屏障：关闭新轮次 → 当前有界轮次结束/提交 → config准备不可变R/tokenA与expected旧active → runtime幂等写R解释及准备记录 → config CAS切active/previous → 加载内存R并写runtime应用记录 → 三者一致才解屏障。失败保持明确阶段与停止准入，不宣称两个独立SQLite库整体原子；DELETE不替代原token协议。

界面分别显示 draft保存、持久active、运行loaded和首轮used revision。active已提交但内存加载失败时不得旧内存继续采样却标新R；重启先关采样并按token/摘要幂等核对。激活连接参数变化在轮次边界释放旧会话；仅原连接意图仍为connected者才重连。回退previous也走新激活token/校验，不删样本、倒退seq/ack或恢复旧来源实时资格。

### R10. 唯一会话、控制与诊断

local模式每PLC一个拥有S7Client的actor，连接、读取、诊断、重连都经同一串行队列，不跨线程共享不可证明安全的客户端，不为诊断另开TCP探针。保留现 rust-snap7 feature；未编译驱动明确 `driver_unavailable`，不退回 minimal_s7。按当前adapter RemotePort设置实现并以受控自定义端口测试核对；失败则阻塞，不忽略port偷偷访问102。

稳定plcId不能绕过物理连接唯一性：对IPv4数值地址及数值port/rack/slot规范化，以 `(IPv4, port, rack, slot)` 为本实例endpoint键；重复endpoint即使plcId不同也拒绝配置激活，不各开一条连接。相同IP/port而rack/slot不同视为显式不同S7端点，不推断网关后物理CPU身份；无设备发现/跨主机锁服务，也不声称全网唯一。

连接与采集意图分离；提供逐台/勾选/全选的连接、断开、启动/暂停采集，批量请求固定ID集合并逐对象反馈/部分成功，不暗中扩大目标。启动采集要求已连接、active有效、存在合法成员和存储准入；不隐式连接。暂停采集保留会话；人工断开取消重连并结束/标记在途结果，保留采集期望但显示disconnected准入；再次显式连接后才可按仍有效意图继续。意外断线仅该PLC退避，其他PLC不被全局锁拖住。

连接测试与单点诊断复用active配置和同一actor；连接测试由专用 `daa_test_connection` 服务操作承载，未连接时明确请求临时受管理会话，成功/失败/超时后都恢复原人工连接意图，不改采集意图/seq/pending。已经连接时复用现有会话，不重建第二连接；恢复释放尚未完成时如实反馈pending/失败，不声称已恢复实态。UI不得自行组合connect/disconnect模拟测试。单点诊断只能指定已配置pointId/revision，不能输入任意地址；返回实际时间/质量，不进生产样本/seq/pending。队列满/超频拒绝，不长时间压住采集。停止/断开在安全边界完成前显示stopping/pending，不能只因按钮点击报stopped。

### R11. 独立组调度、deadline与跳帧

Rust拥有组单调时钟；同PLC按最早到期/稳定轮转处理，一组一次待执行机会，不重入、不无限积压旧tick。到期采集至少在每次诊断之间获得机会；持续到期组间不能饿死慢组。跨PLC独立，SQLite writer只串行短提交。

逐段记录读取起止/耗时和组deadline；到deadline后不再发后续段，未读成员给 `bad_timeout`，保留已成功结果。阻塞驱动调用采用已设置socket超时，不能靠抛弃线程后另开第二客户端“取消”；若调用未返回，显示driver_unresponsive/stopping并保持该PLC隔离，不谎报释放。须在受控黑洞/慢响应下证明所选驱动超时可工作，无法取得有界行为证据则阻塞交接。deadline是本轮停止追加工作准则，不冒充硬实时中断原生调用。

上一轮/队列等待超过周期时计算missed ticks，推进到下一个未来到期，不连续追读过去；调度遗漏、进程停机和容量暂停另报缺口，不给不存在的轮次分配sourceSeq。跨DB/不同段保原实际观察时间，不称物理同时帧；轮询不保证捕获短脉冲。

### R12. 全结果单库提交

一次已开始组轮次固定revision和预期成员，有界收集全部成功结果及失败/null+原因；部分DB失败保其他成功值，全失败也形成明确结果。按DB生成本地单片逻辑包，包含points字典（键为原pointId、每点一份定义/地址/类型/值/原时间/质量），并生成完整cycle manifest；本地不实现HTTP分片或batch。

`cycle + 全部samples + manifest + config context引用 + PLC seq + pending账本` 在runtime.sqlite**同一个短事务**提交，任一失败全部回滚。不得按显示刷新、只保latest、on_change或上传选择丢中间样本。提交成功前不显示已保存/可上传；队列/磁盘失败不得继续读并无限堆内存。持久保证从COMMIT开始，读取后落盘前崩溃不能复造；下次启动记录可证实的未知区间。诊断不走此事实事务。

### R13. 本地身份、编码与历史解释

实例/PLC/group/point/revision/cycle/sample ID采用持久UUIDv4等价不透明身份；不以IP、名称或时间生成身份。每PLC/sourceGeneration的seq为正i64，在上述事务分配并递增，回滚不产生空事实；接近上限停止并报错，不回绕。JSON/IPC中的seq使用十进制字符串，避免JS整数精度丢失。正常重启、周期/组变化、配置回退均不清零；跨PLC不比较裸seq。

新profile初次生成generation，只表示本地代次区分，不能证明Backend实时来源资格/新旧顺序。runtime丢失/恢复旧快照不自动生成新代次续采，按R04/R16停止；重建/替换和Backend登记留独立gate。

本地配置/sample/manifest都带各自schema版本1。内容按固定字段/稳定排序pointId及无歧义UTF-8 JSON编码（有限数值、原样mapping key、固定时间精度），保存原payload和SHA-256，不随查询/预览重渲染；mutable ack不进入不可变样本摘要。cycle manifest引用固定sampleId/DB/摘要与完整预期点，样本不反向包含manifest摘要造成循环。实现记录编码规范及golden fixture；此为**版本化本地合同**，不是抢先冻结Backend wire。C须显式适配版本/身份而非改写历史样本。

### R14. 待传与ACK保护

每个采样COMMIT同时建pending条目；B无发送/批次/ACK处理器，所有实际样本始终pending，界面显示“本地已保存，上传未接入”，不显示可靠上报成功。没有产品IPC/CLI/fixture feature的markAck、删除未确认、手工清队列或改写样本通道。只读原包预览不外发、不换ID/时间，不构造正式HTTP请求。

保留独立样本确认账本和引用清理条件，`pending -> acknowledged` 单调语义供C后续正式回执接入。ACK/交叠引用/未完整cycle清理分支由 `cfg(test)` 私有repository种子在一次性数据库内验证，fixture GUI与validation CLI也不能把样本改ACK。测试需覆盖已确认但仍被引用/所属单位未完整的保留；不得据测试种子声称已有接收API或真实确认。

### R15. 容量、保留与日志

容量计runtime主文件与其 `-journal` 的实际物理字节，包含索引/解释/确认/保护引用/事件，另报页数/可复用页、未确认字节/数量/最旧时刻、配置库/其journal与日志预算、系统空闲。正常DELETE不应产生WAL/SHM；发现时计入实际占用并停止，不能忽略、checkpoint或删除。指标/界面如实显示rollback journal字节及读写busy/耗时，不再提供WAL增长/checkpoint指标或控制。

准入预留全部在途/队列最坏编码、主库页/索引增长、rollback旧页/journal头和同步/恢复/维护所需余量；**512KiB样本编码和32MiB最低维护预留不等于journal最大尺寸**。写入/清理/增量回收均须按实际schema/SQL触页给出保守上界并用临时库测量，不能仅按payload或记录条数估算；无法证明上界时按对应主库页总量预留或拒绝该维护。配置journal另计系统余量；双库事务不叠加执行也须计崩溃遗留材料。预算不够则比90%更早停止，不能借固定水位超额开轮。默认参数其余沿用§3，不假设压缩收益；本PM轮未取得新模式容量实测。

达90%或不足维护/系统余量时全实例暂停新增轮次，保留原人工意图；在途用预留尽力完整提交，失败如实报未持久。存储故障进入故障准入；低于70%、空闲/预算和写入健康检查均通过才恢复仍希望运行且已连接的对象，人工已停对象不重启。80%预警；没有可释放数据也不删pending。B所有真实样本pending，因此保留天数**不会释放它们**，容量可通过停止新增、显式扩大合法额度/增加可用空间恢复，不能期待不存在的上传器清积压。

只有已可靠确认、所属cycle完整且无引用/保护的样本才可按天数/压力清理，小批事务；配置/仍需历史解释不随采样清除。确认种子仅测试。SQL DELETE后的可复用页、正常COMMIT由SQLite删除rollback journal、主文件实际缩小分别显示，不把任何一种冒称pending已释放；不做checkpoint，不在热路径整库VACUUM。增量回收/截断也需journal与维护预算、短读边界和失败恢复证据；不直接操作数据库/journal文件清空间。

启动、模式/版本、配置保存/激活/恢复、连接/重连转态、采样/存储失败、过载摘要、容量暂停/恢复/缺口产生JSON Lines stdout及有界持久日志；正常每轮点值不在info重复打印。磁盘日志总额≤32MiB、轮转/清理只限自有log，不把不可用日志当账本。UI日志/事件/订阅均有界，敏感endpoint细节/内容按场景脱敏，不输出凭据；存储无法记录时反馈未知区间，不能伪造精确开始时刻。

local模式持久日志固定归本模式profile子目录的 `logs/`，使用独立有界日志适配，不沿用可能指向外部路径的旧DAA_LOG_DIR；验证模式所有文件均限制在其受控临时profile内。

### R16. 重启、退出与回退恢复

每次启动先锁profile，保留并配对两库和各自-journal；确认r2日志模式/身份边界，在无PLC连接时由SQLite完成必要hot-journal回滚，再核双库版本/身份/完整性及active/token/context后加载。不手工删/改名journal，不把存在journal本身当损坏或直接重建；空间/锁/恢复失败保持停采并保留材料，不能删journal腾空间。持久样本/manifest/digest/seq/pending与历史按原值恢复，未提交事务不成为事实。异常退出后人工确认恢复连接/采集；正常暂停后重启也不自动连接。容量状态/最近意图可恢复供显示，不能作为自动执行授权。

进程显式退出/窗口关闭采用停止新增→结束有界轮次/提交→关闭会话→关闭writer/释放锁；B不承诺窗口隐藏、进程退出后继续采集或系统托管。配置回退走R09；二进制/schema回退先验证兼容，旧二进制不准打开新schema写入。不提供runtime备份回灌、丢库自动重建或旧模式读新库的“回退”捷径；真实恢复/来源切换仍另批。

### R17. 四页真实操作与最小历史

沿用工作台、PLC配置、点位与采集组、上报与存储四叶及已验收CU公共入口/样式，保留daa.theme/daa.locale、两种语言和显式弹层作用域，不改CU。新模式页面必须可用，不能铺大量无效高级按钮：

| 页面 | B实际交付 |
| --- | --- |
| 工作台 | 每PLC连接/采集意图、实态/准入/逐对象操作与批量结果；组周期/实际耗时/错过次数；已提交量/pending/容量/暂停原因；有界采集日志，上传区一处明确尚未接入 |
| PLC配置 | PLC新增/编辑/停用、IPv4/port/rack/slot、草稿保存/重新读取/校验/应用及共享会话连接测试；保存不触发连接 |
| 点位与采集组 | 完整源导入/错误定位/完整树与叶表；手动推算差异确认、人工地址来源/确认、唯一enabled/分组/组周期/跨DB校验、单点诊断；草稿/active/loaded/used分开 |
| 上报与存储 | 可保存的本地保留/额度/余量；实际文件与保护积压；按PLC/组/时间/质量过滤的分页历史及sample详情/原包只读预览，能核ID/seq/revision/manifest/质量/pending；上传只留C边界说明，无API表单/启用/测试或假成功 |

首次允许先完成PLC/点位/存储再到工作台明确连接/启采；从未保存到已保存、冲突/校验失败、active待加载、无样本、部分失败、满额/恢复均有真实状态。最小历史不要求图表/全库导出/任意SQL。页面重建不拥有采样时钟；切页/主题/语言不改变运行意图或清空持久状态，失败保留最近成功快照并准确区分未加载/陈旧，保留DAA-001 F-001/F-002修复语义。

### R18. 内部IPC、快照与运行状态

新增局部IPC版本1，不改名伪装旧直库命令；所有请求由Rust再校验mode、ID集合、expected版本、限额及外部只读gate。用camelCase DTO（Rust serde统一序列化），pointId字典键原样，稳定英文状态/错误码由宿主i18n映射；不借用Backend HTTP响应信封或发布跨端合同。

| command | 请求/结果的最小合同 |
| --- | --- |
| `daa_get_bootstrap` | 只读已选mode/schema/validation来源/可用能力，不探测PLC/DB/health；UI先据此选择一个状态owner，不能先挂旧owner再切local |
| `daa_get_configuration` / `daa_save_draft` | 草稿/active/previous/etag/校验；save带expectedEtag，返回已提交etag或conflict，不靠UI内存成功 |
| `daa_import_sources` / `daa_preview_offsets` / `daa_confirm_offsets` | 显式源文本及名称/类型、expectedEtag/目标DB；完整诊断/差异，确认只写草稿；无任意服务器路径读取 |
| `daa_activate_configuration` | expectedActiveRevision/expectedEtag，返回token/phase及loaded/used；可pending，之后快照收敛，不能把accepted等同已激活 |
| `daa_set_connection` / `daa_set_collection` | 显式PLC ID列表+desired状态+expected revision；逐对象requested/applied/blocked/failed和原因；重复相同意图幂等，不增第二会话 |
| `daa_test_connection` | 单plcId/expectedActiveRevision；同一actor串行有界测试，返回testId/operationId、testedAt、连接测试结果/原因、原连接意图与恢复phase/实态；不改采集意图/seq/pending，成功/失败/超时都由服务恢复原连接意图，UI不组合connect/disconnect |
| `daa_diagnose_point` | 单PLC/point/revision，通过同一actor，返回诊断ID/实际值时间质量；不写采样账本 |
| `daa_get_local_snapshot` | 只读本地cached/runtime状态、版本/组/容量/pending/最近operation；无PLC读取或旧health；根最多1Hz一次订阅/刷新，切页不重复开时钟 |
| `daa_list_history` / `daa_get_sample` | 有限过滤、稳定游标（保存顺序+ID），最多100条；详情返回原持久sample/manifest/context及mutable pending状态，不重新生成值/身份 |
| `daa_get_logs` | 有限cursor/最多200条；日志cursor过期明确重新取快照，不影响seq或pending |

配置应用/连接慢操作可返回operationId/pending，快照报告完成/失败；operation内存保留≤64项，重启后的运行事实以持久库重建，不让它成为第二任务平台。IPC reject/超时必须释放UI busy并准确反馈；不提供上传/ACK/删库/任意JSON执行入口。浏览器无原生桥时写操作不可用，明确来源，不用长期产品mock模拟成功。

### R19. 可执行受控验证与原生隔离

仅当Human Owner精确批准r2后，才授权源码构建、下文一次性临时profile/SQLite、确定性fixture及自有loopback协议夹具和本机原生开发启动，且B0先于后续产品工作；**仅此类隔离资源**，不授权真实设备/数据库/API。所有项目验证先处理继承环境优先级，显式绝对env/profile，全部旧DB/授权/自动启动gate关闭；Vite验证配置 `envDir:false`，不加载真实root `.env`。不能先启动App再补外发拦截。

可构建路径定为：

1. Rust domain/repository/scheduler的 `#[cfg(test)]` 测试用临时双库、虚拟时钟和私有fixture/故障点；不依赖桌面或网络。ACK种子仅此层存在；同一测试边界验证原子提交、引用保护、容量和恢复。
2. `rust-snap7-driver` 构建及受控owned loopback协议测试核对会话复用/RemotePort/断连/超时，禁扫现有端口或访问真实PLC。其余正常Cargo测试先审查忽略/外发条件；不能因命令叫test就信任默认配置。
3. 非默认 `local-validation` feature + `daa-local-validation` binary 使用**同一Rust服务/仓库/调度**，提供受限JSON Lines配置/运行/查询驱动以做进程kill/restart故障验证；裸执行只显示帮助。它只接受明确 `--env-file/--profile-dir/--fixture-file` 绝对路径，profile必须是本次新建的系统临时目录（校验canonical path、owner marker、拒symlink/真实app-data）；没有默认env/profile回落。feature构建只装fixture transport，不能打开真实S7、旧DB/HTTP或原授权外发；没有markAck/任意SQL/外部endpoint命令。
4. 原生GUI同样以 `pnpm tauri dev --features local-validation --config <本轮临时Tauri覆盖JSON> -- --daa-local-validation --env-file <绝对临时env> --profile-dir <绝对临时profile> --fixture-file <绝对夹具>` 启动。临时覆盖JSON显式更换beforeDevCommand为 `pnpm dev:local-validation -- --port <自有空闲端口>`、匹配devUrl；新增 `vite.validation.config.ts` 复用既有公共alias但 `envDir:false`。启动factory在任何旧AgentConfig/headless入口之前识别验证参数，缺项/混合legacy参数即拒绝。feature禁止release构建；默认发布构建不编入fixture/failpoint/validation命令实现。不能靠可见按钮或环境字符串给普通发布包接通fixture。
5. 用可用原生UI自动化或Human Owner实际操作记录原生四页保存/重读/激活/两PLC采样/历史/退出重开；真实Tauri IPC调用Rust和SQLite，不注入假invoke。同步核对数据库/结构化结果中的相同ID/revision/seq/payload/pending。源/构建/库来自同一冻结交接；仅浏览器渲染证据可补充布局/i18n，不能替代原生闭环。

默认发布构建无fixture入口和错误feature/参数拒绝须有编译/调用证据。验证profile内的样本标记 `origin=fixture`，不能当真实PLC事实或C的可上传来源。停自己的服务器/进程，保留关键日志/断点结果/指纹；不清其他任务/A阶段证据。无法准备/控制原生GUI、不能证明factory隔离或缺少真实IPC持久证据时，明确 `qa_blocked` 与解除条件，不沿用A的可选native延期来判B通过。

### R20. 文档与交接

Development只更新allowlist内DAA稳定入口/局部schema说明、双语i18n与CODE_INDEX的DAA条目，记录完整差异/新增全文、B0实际选型/版本、命令/退出码/失败/资源、需求-AC证据及精确developer_handoff。之后主协调显式启动新的实际Verification、fresh context（支持时fork_turns="none"）；QA只验证/写checklist，不修代码，不用DEV自检/旧A QA代替结论。Human Owner最终验收另行决定，qa_passed不提供发布、生产/现场或C阶段权限。

## 5. 未来精确 allowlist 与角色归属

**本轮仅允许PM写本spec。** 下表是r2待精确批准的有限实现面；全部路径原样沿用r1，无新增路径。87个产品实现路径+Development的tasks=88个DEV路径；加PM spec、Verification checklist及10个主协调路径共100个唯一允许路径，角色归属不变。r2未获批不能用r1批准继续实现；未用到的路径不必改。路径相对 `automation-world/data-acquisition-agent/`，另行注明者除外。`M`既有最小修改，`N`新增；不授权删/移既有源码或建立第二工程。有限目录行明确列出全部可用文件，没有递归/全工程通配；需要额外文件、依赖或实质变更先回PM新Revision。

| M/N | 精确路径或封闭文件集合 | 限定用途 |
| --- | --- | --- |
| M | `src-tauri/Cargo.toml` | R03最小依赖、local-validation feature/required-features；原依赖保护 |
| M | `src-tauri/Cargo.lock` | 仅新增依赖必需闭包与解析冲突核验，不全量升级 |
| M | `src-tauri/src/main.rs` | 验证参数/模式在旧headless dispatch前处理 |
| M | `src-tauri/src/lib.rs` | 新模式composition、managed state/IPC/有序退出、legacy互斥；不堆业务实现 |
| M | `src-tauri/src/config/mod.rs` | R02启动模式/显式定位与验证无回落入口，保旧发现语义 |
| N | `src-tauri/src/config/local_bootstrap.rs` | 有界新启动配置、绝对临时路径和验证factory校验 |
| M | `src-tauri/src/domain/mod.rs` | 仅注册以下本地模型 |
| N | `src-tauri/src/domain/local_configuration.rs` | 配置/完整结构/ID/etag/组/校验与支持矩阵 |
| N | `src-tauri/src/domain/local_sample.rs` | 版本化样本/cycle/manifest/质量/编码与身份 |
| N | `src-tauri/src/domain/local_runtime.rs` | 连接/采集/准入/操作/容量/IPC DTO |
| M | `src-tauri/src/services/mod.rs` | 仅注册以下新服务 |
| N | `src-tauri/src/services/local_configuration.rs` | 草稿/CAS/导入/差异确认与服务校验 |
| N | `src-tauri/src/services/local_activation.rs` | 实例屏障、token/双库激活/previous回退 |
| N | `src-tauri/src/services/local_supervisor.rs` | 每PLC唯一actor、意图/批量控制、同队列诊断 |
| N | `src-tauri/src/services/local_scheduler.rs` | 单调时钟、公平/非重入/deadline/跳tick |
| N | `src-tauri/src/services/local_storage.rs` | 有界单写协调与全轮事务调用 |
| N | `src-tauri/src/services/local_queries.rs` | 快照/历史/日志分页，不执行PLC/旧DB I/O |
| N | `src-tauri/src/services/local_recovery.rs` | 启动一致性/故障恢复/停止和恢复准入 |
| M | `src-tauri/src/infrastructure/mod.rs` | 仅注册新增适配 |
| N | `src-tauri/src/infrastructure/local_store/`，仅 `mod.rs`、`schema.rs`、`configuration.rs`、`runtime.rs`、`capacity.rs`、`tests.rs`、`README.md`、`README.zh-CN.md` | SQLite/schema v1/事务/容量；封闭8文件，不建新PLAN/独立bundle |
| N | `src-tauri/src/infrastructure/tia_source.rs` | 完整受限解析/诊断，非Python依赖 |
| N | `src-tauri/src/infrastructure/plc_layout.rs` | R07受限推算/人工地址校验 |
| N | `src-tauri/src/infrastructure/local_decode.rs` | 新类型化解码，不改旧字符串语义 |
| N | `src-tauri/src/infrastructure/managed_s7.rs` | 持久客户端/RemotePort/timeout；不走旧短连接函数 |
| N | `src-tauri/src/infrastructure/local_profile_lock.rs` | OS独占锁和本模式目录/身份边界 |
| N | `src-tauri/src/infrastructure/local_logging.rs` | 本地有界JSON Lines日志/轮转，独立profile子目录 |
| N | `src-tauri/src/infrastructure/local_fixture.rs` | 仅cfg(test)/local-validation编译的内存transport/failpoint，不能真实传输/ACK |
| M | `src-tauri/src/commands/mod.rs` | 仅注册新薄IPC adapter |
| N | `src-tauri/src/commands/local_acquisition.rs` | R18薄命令/DTO，不含SQL/调度实现 |
| M | `src-tauri/src/commands/plc_collection.rs` | 仅入口mode guard，旧参数/行为不重写 |
| M | `src-tauri/src/commands/plc_diagnostics.rs` | 仅入口mode guard |
| M | `src-tauri/src/commands/runtime_snapshot.rs` | 仅入口mode guard，避免local触旧快照 |
| M | `src-tauri/src/commands/headless_runtime.rs` | 仅旧headless启动/dispatch的mode拒绝，不改旧协议 |
| N | `src-tauri/src/commands/local_validation.rs` | 非默认debug验证adapter，有限配置/运行/查询/退出，不能ACK |
| N | `src-tauri/src/bin/daa-local-validation.rs` | required-features验证入口/裸帮助 |
| N | `src-tauri/tests/fixtures/local-acquisition/`，仅 `README.md`、`README.zh-CN.md`、`flat.db`、`nested.db`、`nested.udt`、`invalid.db`、`offsets.json`、`transport.json`、`empty.env` | 脱敏文本/golden，封闭9文件；无真实地址/数据或输出 |
| M | `src/App.vue` | 先选单一mode owner，四页本地/legacy组合、弹层与真实反馈 |
| M | `src/main.ts` | 安全bootstrap、必要既有EP注册，保持CSS顺序 |
| M | `src/layouts/AgentLayout.vue` | 本地mode/状态展示，保公共壳层/导航 |
| M | `src/components/shell/AgentTopbar.vue` | 本地mode状态，local不显示旧health为链路成功 |
| M | `src/console/types.ts` | 新模式展示类型，保四叶ID |
| M | `src/console/composables/useControlAgentConsole.ts` | 仅legacy owner挂载准入/隔离，保A行为/修复 |
| N | `src/console/composables/useLocalAcquisitionConsole.ts` | 唯一本地状态owner/IPC状态/有界刷新与页状态 |
| N | `src/services/localAcquisition.ts` | 局部IPC v1 DTO/facade/bootstrap，无浏览器假保存 |
| M | `src/services/runtimeSnapshot.ts` | 仅wrong-mode防护/legacy调用准入，保原wire/诊断合同 |
| N | `src/components/console/ConfigRevisionBar.vue` | 草稿/active/loaded/used/冲突反馈 |
| N | `src/components/console/LocalHistoryPanel.vue` | 有界历史/原包只读详情 |
| N | `src/components/console/LocalLogPanel.vue` | 有界日志与来源/失败反馈 |
| M | `src/app/runtime/views/overview/index.vue` | 本地摘要/持久结果或legacy既有摘要 |
| M | `src/app/collection/views/status/index.vue` | 本地PLC控制/准入/组反馈与legacy分开 |
| M | `src/app/plc/views/diagnostics/index.vue` | 本地PLC表单/保存/应用/共享连接测试 |
| M | `src/app/plc/views/points/index.vue` | 完整导入/地址/组/诊断真实流程 |
| M | `src/app/collection/views/storage/index.vue` | 本地存储策略/容量/历史，C说明集中 |
| M | `src/styles/app.css` | 必要宿主业务布局/表单/历史，不覆盖公共样式 |
| M | `src/locales/zh-CN/common.json` | 真实模式/全局反馈/可访问性 |
| M | `src/locales/en-US/common.json` | 对称英文 |
| M | `src/app/runtime/locales/zh-CN.json` | 本地工作台文案 |
| M | `src/app/runtime/locales/en-US.json` | 对称英文 |
| M | `src/app/plc/locales/zh-CN.json` | 配置/结构/地址/组/诊断文案 |
| M | `src/app/plc/locales/en-US.json` | 对称英文 |
| M | `src/app/collection/locales/zh-CN.json` | 本地存储/历史/容量/待传文案，保护原gateDetails对象 |
| M | `src/app/collection/locales/en-US.json` | 对称英文，保护原gateDetails对象 |
| M | `package.json` | 仅新增dev:local-validation脚本，不改依赖/工具版本/既有脚本 |
| N | `vite.validation.config.ts` | 复用公共接线、envDir:false，仅验证开发/构建 |
| M | `.env.example` | 新启动mode/本地gate占位及旧模式分区，所有外部gate默认关 |
| M | `README.md` | 两模式/四页/B能力/限制/受控运行入口 |
| M | `README.zh-CN.md` | 对称中文 |
| M | `src/app/README.md` | 真实页面归属/owner/IPC边界 |
| M | `src/app/README.zh-CN.md` | 对称中文 |
| M | 仓根 `CODE_INDEX.md` | 仅DAA条目，新增关键源码中文头部按既有风格 |
| M | 仓根 `automation-world/README.md` | 仅DAA模式/本地能力与以后C边界，保CA/SMA内容 |
| M | 仓根 `automation-world/README.zh-CN.md` | 对称DAA局部说明 |

| 角色/gate | 仓根相对精确路径 | 写入边界 |
| --- | --- | --- |
| PM/Human Owner | `automation-world/data-acquisition-agent/plans/DAA-002-local-acquisition-loop/spec.md` | 当前PM唯一写入；以后只真实批准/Revision历史 |
| Development，r2批准后M | `automation-world/data-acquisition-agent/plans/DAA-002-local-acquisition-loop/tasks.md` | 保留r1 dev_blocked历史，批准后追加r2实施/真实证据/新B0/完整handoff，不记QA verdict |
| 新fresh-context Verification，handoff后N | `automation-world/data-acquisition-agent/plans/DAA-002-local-acquisition-loop/checklist.md` | 独立结果/verdict/验收审计及真实Owner最终验收 |
| 主协调 | `automation-world/data-acquisition-agent/PLAN.md`、`automation-world/data-acquisition-agent/PLAN.zh-CN.md` | 仅DAA-002新行/真实gate |
| 主协调 | `automation-world/data-acquisition-agent/plans/README.md`、`automation-world/data-acquisition-agent/plans/README.zh-CN.md` | 仅新catalog行，存在后才链接角色文件 |
| 主协调 | `automation-world/PLAN.md`、`automation-world/PLAN.zh-CN.md` | 仅DAA子工程阶段摘要，保A验收历史 |
| 主协调 | `PLAN.md`、`PLAN.zh-CN.md` | 仅DAA-002指针/摘要，保其他任务 |
| 主协调 | `plans/README.md`、`plans/README.zh-CN.md` | 仅指向唯一DAA本地bundle，不建根副本 |

其余均保护，特别是旧 `services/plc_collection.rs`/短连接adapter/decoder/数据库entities与writer、所有实际env/YAML/profile/采样数据、pnpm-lock/workspace、普通vite/tsconfig、Tauri配置/capabilities/icons、locale loader、CU公共/私有源/方案（当前18）、CA/SMA/backend/frontend-js/tools、已验收设计与DAA-001/CU-008等历史bundle、AGENTS/角色/workflow/skills/ROADMAP/contracts。新业务另建本地服务而非重构旧庞大Service；若发现入口guard无法在此范围保证互斥，停止并报告，不绕过保护。测试/验证辅助和产物放本任务 `/private/tmp`，不把真实数据或输出提交进fixtures。

## 6. 依赖与串行实施顺序

| 阶段 | 必需先后关系与完成条件 | 需求 / 验收映射 |
| --- | --- | --- |
| G0 | Human Owner精确批准DAA-002 r2及日志/同步/gate风险；当前pending，r1批准不转移。未过只PM spec/机械索引，r1 tasks保持dev_blocked | R01；AC01 |
| B0 | 新G0后固定起点/保护面 → mode/隔离核对 → 固定兼容依赖解析、实际SQLite/DELETE+EXTRA/锁/hot-journal探针及官方适用性核验；失败停止B1–B6回PM，不能复用r1的旧参数成功项宣称通过 | R01–R03/R19；AC01–AC03/AC19 |
| B1 | B0通过后建独立schema v1/repository、ID/CAS草稿、完整解析、类型/地址/组校验及golden；先证明保存重读/拒绝路径 | R04–R08；AC04–AC08 |
| B2 | 实现激活屏障、版本解释、全结果事务、身份编码和pending，先用私有transport测原子/断点；不造上传器 | R09/R12–R14；AC09/AC12–AC14 |
| B3 | 接入唯一S7会话/共享诊断和独立组调度，证明自定义port/超时/公平/停止与本地事务接通 | R10–R13；AC10–AC13 |
| B4 | 实际文件容量/在途预算/安全保留、重启/退出/故障恢复；先完成低水位/人工意图和丢库拒绝 | R15–R16；AC15–AC16 |
| B5 | 四页通过新IPC接真实服务；配置保存/激活/诊断/运行/历史/容量可用。可在B1–B4按已稳定合同递增接入，但不能先用假保存完成页面 | R17–R18；AC17–AC18 |
| B6 | 冻结实现与指纹，定向构建/受控Rust/loopback/原生真IPC验证、文档/i18n/保护审计，真实tasks developer_handoff | R19–R20及前述全部；AC01–AC20 |
| G1/G2 | 主协调随后新的实际Verification/fresh context独立核验；qa_passed后Human Owner最终验收，当前均pending | R20；AC20 |

DAA-001 r1、CU-008 r1、ARCH-AW-003 r3 已提供真实前置事实。Backend正式合同可由其会话并行收敛，但不是B前置；B也不替后端或SMA立项、发消息或实施。B内部任一必需项未完成不得将整阶段记qa_passed/owner_accepted；实质范围/allowlist/风险/验收变化回PM新Revision并重新批准。

## 7. 验收标准与可重做证据

以下为**r2精确批准后的要求**；当前r1只有B0失败证据，r2无Development/QA通过事实。20项AC编号和业务义务全部保留，存储相关项仅改为新日志/同步/gate及必要证据，不通过删AC规避失败。每项对应同号R，阶段见§6；关键场景必须有实际行为与数据对账，关键词/截图/DEV pass不能替代。

| AC | 独立可核对的完成标准 | 验证方法 |
| --- | --- | --- |
| AC01 | 精确批准后实施、起点/dirty/CU输入及保护字节有据，A历史不改；仅本任务增量 | 批准SHA、before/after/新增全文diff、角色/时间与精确路径审计 |
| AC02 | mode/旧新入口互斥、profile单writer、错误模式/旧headless/不完整验证参数fail closed；保存/切页不建PLC/触旧DB/health | 两模式与二次实例受控测试，IPC/CLI调用轨迹、factory/外发审计；legacy定向命令/gate兼容 |
| AC03 | 固定兼容依赖可解析，旧registry版本/checksum保持；实际SQLite/source ID/VFS/DELETE+EXTRA/PRAGMA及官方问题适用性新B0通过，未越界升级 | 新B0真实解析/probe、两连接参数/锁竞争/hot journal恢复及官方逐项记录；B1实际SQL/索引与后续应用同闭包复核，未过即blocked，不宣称3.46已修复 |
| AC04 | 新临时双库v1/约束/DELETE+EXTRA短事务正确，有界短读/串行写及busy/超时不留锁或饿死提交；身份/版本/模式不符、缺一库/损坏拒绝，不动旧库 | schema/约束、第二writer、读锁/查询超时释放与写背压测试；丢库/高版本/损坏/WAL材料反例和真实库对读 |
| AC05 | PLC/点/组草稿真实保存重读，CAS冲突拒绝，稳定ID和人工地址重导入差异不静默覆盖 | Rust持久测试+原生GUI保存/重开；改名/移组/endpoint变更ID对照、重复/歧义反例 |
| AC06 | 完整支持矩阵结构/叶/来源保存，未选字段不丢；缺UDT/循环/优化/非法数组等定位拒绝且不影响active | flat/nested/数组/缺定义等脱敏输入与独立预期树/叶数逐项核对；legacy YAML标不完整 |
| AC07 | 首版标量推算边界准确，复杂结构手工地址可校验采样；类型解码/字符串/REAL错误质量真实 | 独立offset golden、bit/边界/无效编码/NaN/INT符号夹具；真实GUI差异确认与人工覆盖保护 |
| AC08 | 单PLC跨DB组、单点单组、唯一enabled/未分组不采、规模/周期/读预算越界拒绝 | 两PLC/三DB多组配置及重复归属/跨PLC/500ms边界/超限反例，无截断成员 |
| AC09 | 各激活断点可恢复，active/loaded/used分开，失败屏障停采；previous回退不倒退数据 | token准备前/后、runtime准备后、active后、内存安装后、首样本前后逐断点kill/restart，对账两库/首样本revision |
| AC10 | 每PLC一个连接供采集/测试/单点诊断，重复规范endpoint拒绝；连接测试服务在成功/失败/超时后恢复原意图，不改采集意图/seq/pending；人工断开不重连、异常仅该PLC退避、批量部分成功 | counting fixture+实际Snap7 loopback自定义port/断连轨迹；两个plcId同endpoint拒绝，无第二会话/独立探针；原已连/未连的测试及恢复phase对账，UI不组合连接控制 |
| AC11 | 两独立组周期、非重入/公平/deadline/跳tick及停止实态正确，故障不拖其他PLC | 虚拟时钟覆盖500/1000ms组、慢读/黑洞/持续诊断；受控实际时钟短运行核调用/延迟/错过数，无追读伪样本 |
| AC12 | 跨DB部分/全失败仍保全成员质量；单事务全结果/seq/pending；无半轮或读后未提交假保存 | 成功/坏DB/解码失败/commit前后故障注入，事务行数/manifest/内容对账，写满/队列背压停止 |
| AC13 | ID/seq/本地schema/摘要稳定，原点键/数值/时间保留，重启/回退不重编号 | golden编码、读回SHA、组过滤自然跳号/不同PLC同seq、正常/异常重启与配置回退数据比较 |
| AC14 | 所有实际样本pending、无假ACK/删除后门；保护清理与引用条件可证 | 原生采样/重启pending全对账；默认及validation接口枚举/拒绝调用；仅cfg(test)种子测ACK单调/已确认钉住/不完整单位 |
| AC15 | 主库/-journal/配置/日志/余量计量与在途/维护预留有界；无checkpoint承诺，满额或journal预算不足停新增不删pending，低水位仅恢复原意图 | 实际临时DELETE库/journal峰值、写/清理/增量回收预算与小额度/空间meter；pending/hash前后一致；人工停止一PLC后恢复另一PLC；期限/引用清理私有测试，无手删journal |
| AC16 | 配置/历史/queue/seq在正常退出及hot-journal回滚后原值恢复；丢库拒绝、退出释放锁、重启不自动连接 | 同临时DELETE profile正常退出、commit前形成journal/commit后分别强杀重开，对账已提交事实/未提交回滚/完整性与锁；无手删journal/无外发；旧二进制或高schema拒写；强杀不当断电证明 |
| AC17 | 四页走通真实保存/应用/连接/采样/历史/容量流程，C缺口集中说明、无不可用表单海；F-001/F-002无回归 | 原生GUI实际操作+同profile数据对账，中英明暗/代表窄窗/冲突错误状态定向观察，不全量视觉矩阵 |
| AC18 | IPC v1字段/错误/状态正确，pointId原样，只有一个本地owner/有界刷新；查询/切页不驱动PLC或health | DTO契约与命令次数/参数、busy/pending/实际完成、分页稳定性及事件/刷新上限检查；browser无桥拒写 |
| AC19 | 受控Rust、Snap7 loopback和native真IPC证据成立；fixture默认发布包不可用/无法真实外发或ACK；构建通过 | §8命令与环境/退出码、编译条件反例、native轨迹/库对账；缺原生或隔离证据记qa_blocked |
| AC20 | 文档/i18n/头部/索引与实现一致，准确范围/资源/失败/DEV handoff、新fresh QA及Owner gate分层 | 本地链接/JSON键与占位符/动态状态键、完整diff保护审计；真实角色记录与验收审计，不继承A/CU QA |

## 8. 批准后执行/验证口径

Development须在tasks写出实际脚本/命令及绝对临时路径，不把下面占位命令当已运行结果。项目Cargo/pnpm遵循锁文件；Agent辅助包不得安装进项目。依赖获取仅限R03闭包，技术官方资料核对不调用项目API。r2新B0先按R03在仓外执行，严禁提前产品构建；B0通过后将同样的DELETE+EXTRA/短读/锁/hot journal/实际容量条件接入以下产品验证。历史查询原包/分页有界、commit前后及回滚/维护阶段强杀均要对账，保留journal材料，不能把SQL错误后的未提交半轮当已保存；不新增整仓/上游源码回归。例行验证收敛为：

- `cargo fmt --manifest-path src-tauri/Cargo.toml --check`；对本地新模块、mode guard/旧headless兼容、解码的定向 `cargo test --manifest-path src-tauri/Cargo.toml --locked <实际过滤>`。固定临时env/profile且先审查旧测试是否外发；必要全体默认测试在确认隔离后执行，不运行标注现场/外部依赖的ignored测试。
- `cargo check --manifest-path src-tauri/Cargo.toml --locked --features rust-snap7-driver`；对应owned loopback transport test核真实驱动；失败/未编译不能写“驱动通过”。不启动现有tools或他人模拟器，不把fixtures成功当硬件CPU兼容证明。
- `cargo run --manifest-path src-tauri/Cargo.toml --locked --features local-validation --bin daa-local-validation -- --env-file <abs> --profile-dir <abs> --fixture-file <abs>`；JSON Lines有限操作和逐断点独立进程重启。fixture文件在启动前冻结，UI无动态加载任意驱动能力。
- `pnpm build --config vite.validation.config.ts --outDir <abs/tmp/dist> --emptyOutDir`，保留vue-tsc/实际宿主源码和CU消费检查，验证配置禁止真实env读取；原生按R19的临时Tauri覆盖启动。端口先核归属，冲突只换自己的临时覆盖，不停他人进程或改产品15191/14191。
- 正常默认构建不含local-validation、`--release --features local-validation`被明确拒绝、无feature传验证flag被拒绝，必须有相应编译/入口证据；不需要为此打包、签名、分发。真实原生GUI用feature debug构建和真实IPC，浏览器假桥仅可作为额外UI反馈用例。

完整性/激活/容量属于本任务关键正确性，要求必要自动化及故障验证；不追加无关整仓/业务/跨平台/长稳回归。源/锁/依赖变更后运行相关最终检查；通过后只有新变更/失败/疑点才重复。记录实际cwd/版本/命令/退出码、stdout/库状态/指纹、失败重试和限制；未执行项不记pass。临时数据、截图/报告只做附件，tasks/checklist保留足够的输入/结果/证据摘要，不以可能消失的临时路径为唯一事实。

## 9. 风险、回退与deferred gates

| 风险 | 处理/停止条件 |
| --- | --- |
| SQLite3.46未获WAL修复；DELETE+EXTRA仍有版本/VFS/SQL及同步假设 | 新B0核精确闭包、实际参数/来源、已知问题触发适用性；不能把去掉WAL当全面安全，任何可达缺陷/关键未知均停，不升级旧链路或偷偷补源码 |
| rollback读写互斥、EXTRA同步成本与journal峰值 | 有界短读/队列/deadline/串行写/背压及实际峰值预算，允许更早容量停采和透明跳tick；不降同步、不删pending、不承诺500ms吞吐；未满足AC即blocked |
| 字段解析/地址推算被误认为TIA完整编译 | 支持/拒绝矩阵、完整结构保存、平铺限定和人工确认显著显示；独立golden，真实TIA校核仍另批 |
| 500ms/4PLC被误当性能承诺 | 作为准入限额，实际耗时/跳tick/过载透明；受控fixture证明调度，不证明现场吞吐/短脉冲捕获 |
| 双库部分激活、写满或原生驱动不可取消 | token屏障/逐断点/在途预算，未提交不报保存；停止状态待实际完成，无第二worker绕过；缺有界证据阻塞交接 |
| B无上传导致pending持续积累 | 所有未确认保护，满额停采；用户需审阅有限磁盘下无法无限连续采集，不能通过假ACK/按天删规避 |
| 新旧模式、profile和真实数据混用 | 显式模式/独占锁/独立子目录/旧入口guard，禁止启动时迁移；不同应用/主机现场双采仍需来源切换任务 |
| 验证feature成为产品后门 | 默认/发布不编入、debug feature必须临时profile+fixture且不含真实transport，不存在ACK/任意SQL/endpoint控制；反例验证 |
| GUI假桥/设计QA被当运行证据 | native真IPC+库状态为必需；缺失记blocked；DEV、fresh QA与Owner决定分别记录 |

回退先停止本实例新工作、保留两库及各自-journal等恢复材料和日志；发现非预期WAL/SHM也保留并停写，不做自动日志模式迁移，再核对当前归属只处理本任务已确认源码增量；不reset整仓、不删样本/配置/来源身份、不倒退seq/ack。配置回退使用previous激活协议；二进制回退只有已验证schema/编码兼容才可打开同profile，否则保留数据并保持停止。B验收不授权实际生产回滚；导回旧YAML/旧库或把旧runtime备份灌回均不属于本任务。

以下延期不阻塞**已批准的B受控本地交付**，也不被其QA或最终验收授权：真实PLC/TIA地址/CPU/长期负载验证；后台/开机托管、目标多平台生命周期、原生打包签名分发；真实profile schema升级/迁移/备份恢复和设备来源切换；Backend正式wire/身份代次/回执/三自然月/限额/安全feed/旧标量适配；C上传器/可靠ACK/冻结批次/最新优先补传/跨端联调；SMA语义处理/业务投递/单writer切换；Docker、部署/发布/Git动作。B0、安全隔离、必需native、本地闭环AC不属于可延期通过项。

## 10. 技术skill、PM文档自检与当前handoff

| 实际表面 | 对应角色批准后必须按需加载 |
| --- | --- |
| Rust长运行时/SQLite/驱动/调度/日志/恢复 | Development / Verification：`rust-runtime`及其适用配置/日志/结构依据；仅局部本地schema，不引入Backend或Celery |
| Tauri startup/IPC/managed state/退出及native隔离验证 | `desktop-tauri` + `rust-runtime`，不把浏览器证据等同原生 |
| 完整DB/UDT/数组/地址/受限推算与人工校核 | `plc-point-mapping`；tools仅只读参考，不把Python辅助依赖加入DAA |
| 四页/表单/状态/公共CU消费与错误流程 | `frontend-ui`（既有DESIGN/FRAMEWORK适用部分）+ `i18n-workflow`；Rust IPC归Rust/Tauri，不为本任务引入Backend API |
| 新关键源码头/真实结构索引 | `code-document-indexer`，只DAA允许面/条目，不全仓生成 |
| bundle/索引/工业边界 | `project-governance` + `aiis`；PM/DEV/QA各守归属 |

PM仅做本文档元数据、完整bundle/引用/事实指纹、100个有限路径、R01–R20 ↔ AC01–AC20 ↔ B0–B6/G0–G2映射、新旧条款/边界/链接和单文件差异自检；不是新SQLite参数probe、Development self-check或独立QA。核验官方文档是设计依据，不能记成新的运行通过。命令/文档检查结果和最终SHA由PM交接消息提供，避免本文存自身SHA。

修订/批准/失败历史（时间为Asia/Shanghai）：

- 2026-10-17，r1 draft：依据Human Owner先出阶段B spec原话形成范围/有限路径/20AC；当时未批准。精确draft SHA-256 `4077ec3f908c7860db74abf9ae3f3ba54ede25fcbbdd408535d5b5542c1e9002`。
- 2026-10-17，r1 owner_approved：Human Owner按§1原话精确批准上述draft；PM仅补批准记录，原R/AC/参数/风险不变，形成批准spec SHA-256 `88859d45093d010cf7f1214d5f5975b93e5ffabde2ef0f69574bc7440247c819`。该批准只属于r1，不是最终验收。
- 2026-10-17，r1 dev_blocked：实际Development仅执行已批B0，确认links冲突/兼容3.46.0未含WAL修复并停止。tasks/receipt/全文diff及实际输出见§2.1，B1–B6未开始，产品87路径/HEAD保持；没有developer_handoff、独立QA或Owner终验。该失败历史不被r2抹除或补成通过。
- 2026-10-17，r2 draft：实际PM仅修订新本地存储为DELETE+EXTRA、固定兼容依赖及必要锁/容量/恢复/已知问题gate/风险；无新增路径、无旧链路升级、无业务或20AC删减。r1被替换的原文在§11，其他沿用段保持字节。r2未批准、无实施/探针/构建/项目测试或QA事实。

**当前只交Human Owner审阅精确DAA-002 r2：是否接受DELETE+EXTRA代替WAL/FULL、兼容3.46.0仍未修复而仅排除WAL前提、新gate与提交/短读/容量权衡。** Human Owner尚未作此决定，r1不能授权继续。PM成稿后停止写入；唯一主协调 `/root` 可据真实状态机械同步原10索引，不能代角色改tasks/checklist。精确r2批准后才交真实Development重过B0，失败再回PM；完整developer_handoff后由主协调显式启动新的实际fresh-context Verification，独立qa_passed后再由Human Owner最终验收。C、后端/SMA、真实PLC/生产数据库/API/现场切换仍待各自明确授权。


**最新批准历史与当前handoff（2026-10-17，Asia/Shanghai）：** Human Owner按§1最新原话精确批准draft SHA-256 `41c65ef12e5431a1321d86e3b6c613a9cccbba0507e88790581597c601bba5ac` 对应的DAA-002 r2。PM仅补记Status/Handoff/acceptance-chain元数据和§1/§10批准/时间效力，范围合同逐字不变；此前r2 draft待批交接及r1批准/B0失败原文保留，当前效力以此最新批准为准。新B0、r2产品实施/DEV self-check/developer_handoff、新fresh-context Verification及Human Owner最终验收仍pending，不将范围批准写成任何运行或QA通过。

当前交唯一主协调 `/root` 接续实际Development：消费精确已批准 `aiis-ics-arch::DAA-002 r2`、完整已形成bundle及写前基线，先保留r1 dev_blocked历史、追加r2事实并重过R03/B0；B0通过前仅准该最小依赖解析/仓外探针，失败即停并回PM，B0通过后才依§6完成全部B1–B6。精确developer_handoff后才由主协调显式启动新的实际fresh-context Verification，独立qa_passed后再交Human Owner最终验收。主协调可据真实批准机械同步原10索引；PM未修改它们或后续角色文件，没有启动团队/执行窗口，批准记录和文档自检后停止写入，供真实Development接续。

## 11. r1 已批准条款的原文历史（非 r2 当前合同）

r1 draft及批准后全文SHA见§1/§10。以下逐项保留r2替换的r1原文字节片段；新增§2.1–2.2在r1的位置原来只有下一节标题。**除本节列明片段外，§1–10其他正文（包括完整业务R/AC、87产品路径、10协调路径、3角色文档路径）均逐字沿用r1；只是其中存储相关条款被下列明确修订替代。** 文首状态/当前handoff与历史事实随Revision更新，不构成r1批准撤销或r2批准。可结合r2对应位置与这些原文还原并核对批准r1全文SHA；不依赖/tmp保留唯一历史，不另建平行bundle。

下列围栏仅为审查原文，不是当前可执行要求或待重复的编号需求；r2以§1–10为准。各片段位置/对应改动见标题；r2完整差异及机械还原检查另作PM临时自检附件。

### H01. 文首 Revision

```text
Revision: r1
```

### H02. 文首 Status

```text
Status: owner_approved
```

### H03. 文首 Handoff

```text
Handoff: Human Owner approved exact DAA-002 r1 on 2026-10-17; Development may create tasks and begin only the approved B0 minimal dependency resolution and external SQLite probe; subsequent product implementation awaits B0 closure, then new fresh-context Verification and Human Owner final acceptance
```

### H04. 文首独立 acceptance chain

```text
Acceptance Chain Reference: aiis-ics-arch::DAA-002 r1 scope approval -> Development -> new fresh-context QA / Verification -> Human Owner final acceptance
```

### H05. §1 当前时间效力及 handoff

```text
**当前为 r1 `owner_approved`，精确范围批准 gate G0 已满足；B0 尚未通过。** 本次 PM 仅记录真实批准与当前交接，不修订 R01–R20、工程参数、87 个未来实现路径、10 个协调路径、3 份角色文档、AC01–AC20、风险或 B0 阻塞条件。Development 可创建 tasks，先按 R03/B0 进行已批准的最小依赖解析和仓外一次性 SQLite 探针；B0 通过前不得推进后续产品实现。第6节 G0 的“当前pending”保留为 draft 起草时的状态原文，当前时间效力以本段的真实批准为准，不改变该节先后关系。B0、Development 交付、新 fresh-context Verification 和 Human Owner 最终验收均未发生；本次批准不等于 QA 或终验，不授权 C、Backend/SMA 具体开发、真实 PLC、生产数据库/API 或现场切换。本轮 PM 仍只写本文件，不创建 tasks/checklist、修改索引/源码或运行项目验证。
```

### H06. §1 六项选择的效力说明

```text
以下六项是 r1 draft 提交审批时的工程取舍，六项原文保留；数值已作为本 r1 的**准入上限/默认值**获批，不是已经测得的现场能力：
```

### H07. §1 工程选择第5项

```text
5. 双 SQLite 使用下文 WAL/FULL 与容量方案；`rusqlite` bundled 的可解析版本、实际链接 SQLite/source ID 和官方 WAL 已知缺陷/修复须先通过 B0 技术 gate。PM 本轮未联网或运行探针，不能据 crate 版本宣称安全。失败只阻塞实现，不自动换架构、升级范围或降验收。
```

### H08. §2 依据核对的时间范围

```text
PM 已读根 AGENTS、README/PLAN 双语、canonical lifecycle workflow、实际 pm TOML，AW/DAA 最近 README/PLAN 和 DAA `src/app/README.*`，ARCH-AW-003、DAA-001、CU-008 完整已形成 bundle，以及 774 行 [DAA 详细设计](../../../../docs/AIIS_DAA_Detailed_Design.md)；使用 `aiis`（含 BLUEPRINT/CONTRACTS）和 `project-governance`。作用域检索无更近 AGENTS。只读检查 DAA Rust/前端/依赖与 `tools/plc/point-mapping` 解析/结构校验参考；没有读取真实 env、用户 profile、设备、数据库或项目 API，没有网络请求。
```

### H09. §2 末新增 B0 事实与 r2 候选比较（r1此处无新增段）

```text
## 3. 精确范围、排除项与工程参数
```

### H10. §3 参数表标题

```text
| 项 | r1 定稿的工程准入/默认值 |
```

### H11. §3 SQLite参数行

```text
| SQLite | 本机文件系统，page_size=4096、建库前 auto_vacuum=INCREMENTAL、journal_mode=WAL、synchronous=FULL、foreign_keys=ON、busy_timeout=1000ms、wal_autocheckpoint=256页；逐连接核对实际值 |
```

### H12. R01 Revision门槛

```text
精确 r1 批准后，Development 才创建 tasks，固定批准 spec SHA、当前源码/锁文件/17项 CU 公共源摘要、dirty 起点及受保护面；从 DAA-001 当前 QA2 字节继续。只把本任务实际增量交接，不 reset/restore 他人工作或旧失败证据。B0 门槛未过时不能把后续实施写成已开始/通过。
```

### H13. R03 完整依赖和SQLite gate

```text
本地 repository 采用 `rusqlite` bundled，避免依赖用户系统 SQLite；允许增加 `uuid`（v4）、`sha2` 和 `fs2` 的最小直接依赖。旧 SeaORM/MySQL、Tauri、Snap7 版本和功能不升级。现锁含可选 sqlx-sqlite/libsqlite3-sys；先核 Cargo `links`/feature 解析兼容，不启用第二套本地 ORM，不借解决依赖全量更新锁。仅新增依赖及其必需传递闭包可改 Cargo.lock；pnpm 依赖/锁不变。

B0 在批准范围内先做受限依赖解析及仓外一次性 SQLite 探针，记录候选 crate 精确 pin、应用同一解析闭包下 `sqlite_version()`、`sqlite_source_id()`、compile_options、实际 PRAGMA 和 native 库来源，并对照当时 SQLite 官方 WAL 已知问题/修复范围（含 WAL-reset）；记录来源、核验日期及适用条件。PM 未核定具体新版本，Development 在既定适配/安全条件内选可验证版本并精确锁定，不把版本选择当新架构授权。

**未证明实际链接版本满足已知修复要求、发生无法解决的 links 冲突、或需升级旧 ORM/Tauri/Snap7/改出 allowlist时，记录 B0 blocked，停止后续产品实现并回 PM；不得关闭 WAL、弱化 FULL、偷偷改系统库或以“单 writer”豁免缺陷。** 通过探针不代替本任务后续崩溃/并发/容量验证，FULL 不承诺硬件级绝对耐久。
```

### H14. R04 物理合同效力

```text
建议物理合同如下，逻辑字段/唯一约束是 r1 要求；SQL/编码实现归批准后 Development，在以下局部模型内落定并写 tasks，不发布为 Backend DDL：
```

### H15. R04 串行写与有界短读合同

```text
每库单写协调、短事务；SQL/文件/驱动细节归 infrastructure，command/service 不构造 SQL。历史查询使用有界短读，不在等待网络/PLC/UI时持有写事务。配置库仅安全回收非 active/previous/应用中且已不需编辑引用的旧完整版本/源；历史所需解释内容已可靠保存在 runtime.sqlite 的 configuration_contexts 才可释放旧配置正文。不能借版本保留删除历史解释。
```

### H16. R09 双库原子性文字

```text
失败保持明确阶段与停止准入，不宣称两个WAL库整体原子。
```

### H17. R15 物理容量和在途journal预算

```text
容量计runtime主文件/WAL/SHM、索引/解释/确认/保护引用/事件等实际文件字节，另报页数/可复用页、未确认字节/数量/最旧时刻、配置/日志预算及系统空闲。准入预留全部在途/队列最坏编码及WAL增长/维护余量；以保守预算拒绝下一轮，而非到满盘后才处理。默认参数见§3；必须用实际夹具落盘量核对预算，不假设压缩收益。
```

### H18. R15 清理与文件缩小语义

```text
只有已可靠确认、所属cycle完整且无引用/保护的样本才可按天数/压力清理，小批事务；配置/仍需历史解释不随采样清除。确认种子仅测试。DELETE页复用、checkpoint与实际文件缩小分别显示；不在热路径整库VACUUM，增量回收/截断有维护预算和短读边界。
```

### H19. R16 启动恢复顺序

```text
每次启动先锁profile、核双库版本/身份/完整性、核active/token/context再加载；在此之前不建PLC连接。持久样本/manifest/digest/seq/pending与历史按原值恢复，未提交事务不成为事实。异常退出后人工确认恢复连接/采集；正常暂停后重启也不自动连接。容量状态/最近意图可恢复供显示，不能作为自动执行授权。
```

### H20. R19 授权时间效力

```text
批准r1同时授权源码构建、下文一次性临时profile/SQLite、确定性fixture及自有loopback协议夹具和本机原生开发启动；**仅此类隔离资源**，不授权真实设备/数据库/API。
```

### H21. §5 allowlist批准时间

```text
**本轮仅允许PM写本spec。** 下表只是以后精确r1获批的实现批准面；未用到的路径不必改。
```

### H22. §5 Development角色文件现状

```text
| Development，批准后N | `automation-world/data-acquisition-agent/plans/DAA-002-local-acquisition-loop/tasks.md` | 实施顺序/真实证据/B0/完整handoff，不记QA verdict |
```

### H23. §6 G0

```text
| G0 | Human Owner精确批准DAA-002 r1及本文边界；当前pending。未过只PM spec/机械索引 | R01；AC01 |
```

### H24. §6 B0

```text
| B0 | G0后固定起点/保护面 → mode/验证隔离方案核对 → 最小依赖解析和实际SQLite探针/官方WAL修复核验；失败停止其后实现 | R01–R03/R19；AC01–AC03/AC19 |
```

### H25. §7 AC时间效力

```text
以下为**批准后的要求**，当前无B Development/QA通过事实。每项对应同号R，阶段见§6；关键场景必须有实际行为与数据对账，关键词/截图/DEV pass不能替代。
```

### H26. AC03 新技术gate

```text
| AC03 | rusqlite选型可解析，实际链接SQLite/source ID/PRAGMA及官方已知修复核验通过；未越界升级 | B0真实probe/cargo解析输出与官方核验记录，后续应用同一闭包复核；未过即blocked |
```

### H27. AC04 短读互斥

```text
| AC04 | 新临时双库v1初始化/约束/短事务正确，身份/版本不符、缺一库、损坏拒绝，不动旧库 | schema/约束测试、第二writer拒绝及丢库/更高版本/损坏注入，真实库状态对读 |
```

### H28. AC15 journal容量证据

```text
| AC15 | 文件/WAL/日志/余量计量与预留有界，满额停新增不删pending，低水位仅恢复原意图 | 实际临时库/WAL增长+小额度/空间meter夹具；pending/hash前后一致；人工停止一PLC后恢复另一PLC；期限/引用清理私有测试 |
```

### H29. AC16 hot journal恢复证据

```text
| AC16 | 配置/历史/queue/seq重启恢复、丢库拒绝、退出释放锁，重启不自动连接 | 同临时profile正常退出和强杀重开，查询持久对账/进程与锁释放/无启动外发；旧二进制或高schema拒写 |
```

### H30. §8 批准后验证补充

```text
例行验证收敛为：
```

### H31. §9 SQLite风险行

```text
| SQLite实际native链接与WAL已知缺陷不符，或links冲突 | B0必过；无证据停止，不以新版本号/单writer豁免，不自动换库/架构或升级旧链路 |
```

### H32. §9 保留数据材料

```text
回退先停止本实例新工作、保留两库/WAL相关持久材料及日志
```

### H33. §10 文档自检和真实修订/批准/失败历史

```text
PM仅做本文档的元数据、路径/链接、R01–R20 ↔ AC01–AC20 ↔ B0–B6/G0–G2映射、编号/表格/围栏、明确边界和自有单文件差异自检；不是技术探针、Development self-check或独立QA。自检命令/最终SHA由PM交接消息提供，避免在本文存自身SHA。起草阶段未取得实施批准；现已取得第1节的精确范围批准，本次仅补记该事实并核对范围原文不变。尚未创建tasks/checklist，也没有B0、Development、QA或Human Owner最终验收结论。

修订/批准历史：

- 2026-10-17，r1 draft：依据Human Owner先出阶段B spec的原话，由实际PM起草本文件，冻结本地闭环范围、首版支持/限制、顺序、未来allowlist及20项AC；当时范围批准pending。精确draft SHA-256为 `4077ec3f908c7860db74abf9ae3f3ba54ede25fcbbdd408535d5b5542c1e9002`。
- 2026-10-17，r1 owner_approved：Human Owner按第1节原话明确批准上述精确draft；PM仅补记Status/Handoff、§1/§10批准历史及时间效力。R01–R20、工程参数、87个未来实现路径/10个协调路径/3份角色文档、AC01–AC20、风险和B0阻塞条件保持原文；本次未实施或创建后续角色证据。
- Human Owner对精确DAA-002 r1的范围批准：**已满足**；不等于Human Owner最终验收。
- Development/B0/实施/self-check/developer_handoff：**pending**。
- 新fresh-context Verification与Human Owner最终验收：**pending**。

当前交实际Development消费精确已批准 `aiis-ics-arch::DAA-002 r1`、完整已形成bundle和写前基线；Development可创建tasks，先按§6/R03只进行B0最小依赖解析和仓外一次性SQLite探针。B0通过前保持后续产品实现停止，失败按原阻塞条件回PM，不自动扩大范围；通过后才推进完整本地闭环。精确developer_handoff后由唯一主协调 `/root` 显式启动新的实际fresh-context Verification，QA通过后再由Human Owner最终验收。主协调据真实批准机械同步本任务索引；PM本次没有写索引或后续角色文件，完成批准记录后停止写入，供真实Development接续。
```
