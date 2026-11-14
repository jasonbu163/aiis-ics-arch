# 本地采集与事实投递双库

两个软件启动开关保存在现有配置 SQLite 的受保护私有记录中，记录不存在时均关闭。保存事务不修改草稿版本或 DDL，也不重写样本和回执；记录损坏时自动启动停止，手动操作仍可用。配置清理会保留该记录；旧二进制重新打开变更后的 profile 尚未作为回退路径验证。

逐 PLC 上报开关保存在现有运行库的 `reporting_disabled` 表中，既有绑定默认开启。通过锁和完整检查的 runtime4 profile 按原凭据暂存流程增加该表，不重写样本、冻结请求或回执。关闭时采集仍记录原上报身份；队列在选样和最终派发前核对开关，已派发请求可继续结算。未绑定时采集的样本仍只保存在本地。

本适配层拥有本地 SQLite schema 与 SQL。DAA-010 候选新建 config2/runtime4，独立保存 v2 样本投递和历史 v1 账本；既有冷态 runtime2/3 保持原 schema 与本地行为，退役 v1 派发。当前自检与保留的 r1 hot-journal 原失败见[DAA-008](../../../../plans/DAA-008-reliable-facts-upload/tasks.md)，历史本地证据仍归 DAA-002/007。

| 库 | 表与责任 |
| --- | --- |
| `config.sqlite` | `schema_migrations`、`instance_metadata`、内容去重 `source_documents`、CAS `configuration_draft`、不可变 `configuration_revisions`、`active_selection`、可恢复 `activation_intents` |
| `runtime.sqlite` | `schema_migrations`、`runtime_metadata`、稳定 `plc_sources`、不可变 `configuration_contexts`、`activation_journal`、完整 `collection_cycles`、自描述 `samples`、独立 `sample_delivery` / `sample_references`、有限 `runtime_events` |

新库只在空 local-acquisition-v1 同时建立 config2/runtime4，身份/时间合同匹配并核完整性。已知冷态 runtime2/3 不原地转换；缺库、未知/损坏/schema/身份不符、链接或 WAL/SHM 均拒绝。`Stores::open` 持原父 profile OS 锁直到双库 SQLite 连接关闭；进程内路径/目录身份占用登记避免 raw FD close 破坏同进程另一活跃库的锁。产品 locator 仍为显式 profile/local-acquisition-v1；历史 private p/store 调用共用同一工厂，不是恢复旁路。不删 journal、不用 immutable 绕过；runtime4 的 r2 候选兼容路径见下。

ARCH-ACQ-004 r2 候选在通过原凭据、原 DDL 指纹及全量账本检查后，持锁在同一 runtime4 原位新增 `reporting_identity`、`reporting_bindings`、`reporting_generations`、`reporting_cycles`。原样本、上下文、冻结正文和回执不重编码；旧轮无 marker 沿用原身份，新轮按开始时的绑定保存，空 marker 是仅本地记录。上报代次记录约束复用，不能用另一本机 PLC 或实例重置同一代次的序号。完整且无引用的过期仅本地轮按保留期回收，已进入队列但未确认的样本继续受保护。

Unix 新指纹凭据先以 staging 写入并同步，同目录 DDL 使用原 DELETE/EXTRA 连接及事务；提交后复核新结构与旧账本，再替换凭据并同步目录。中断时保留 staging 或凭据/结构不匹配会拒绝打开；保留整个目录、原数据库、journal、sentinel 与 staging，留待独立核对和获批恢复，不手动删除 marker 或用新目录覆盖。本段是候选设计及合成验证范围，未证明真实 profile 或 Windows 采用。

`profile_contract.rs` 负责原字节严格凭据、canonical Unix 文件身份、sentinel/staging no-replace 封存与唯一原生回滚例外；`schema.rs` 负责已知 DDL 指纹和有界完整账本后检（稳定索引每页≤100 key，一次一份 body/response）；`capacity.rs` 仅用 metadata 统计辅助分配。初始化 256KiB 子预算位于既有额外 32MiB 内：实际 auxiliary allocated 加入已用物理量，同时从剩余预留等额扣减。本地 Configuration/context 沿用本地有效性边界；provider wire 限额只核冻结投递材料，不将合法未冻结/blocked 原轮判成整个 profile 损坏。

仅原始 `SqliteFailure.extended_code=776`、新 sealed 有效凭据、未漂移的已知头/身份/SHA 候选、单个对应 journal、完整核过的同伴库及真实锁同时成立，才一次 READ_WRITE|NO_MUTEX、无 CREATE 打开；固定 `PRAGMA schema_version` 让默认 SQLite 执行自己的 rollback。raw DB/journal FD 全在 SQLite 前关闭。检查 native 连接 close 后，先全量 RO 核 integrity/FK/DDL/原文/activation/冻结请求/ACK，再进入原正常恢复、业务日志和 actor。sealed cold 同等级全检。native 失败提示恢复写可能发生；native 后检失败明确已恢复写而业务准入拒绝。准入前只有 stdout 诊断，采集/上传仍停态。

sentinel/staging 存在即拒绝，坏凭据不降级；末次目录 fsync 失败当次拒绝，下次完整可见凭据且无 marker 可以独立 sealed cold 全检，不追认前次同步成功。三个辅助文件全无且无 hot 的合法 v2/unsealed v3 保持 r1 cold 且不补封；格式不能识别启动前外部彻底删 marker 的历史，运维仍禁止删除降级。路径/inode 替换或复制/移动拒绝自动重绑；SHA/inode 不是针对恶意原地编辑或伪造 journal 的认证。非 Unix 保持 unsealed cold 并拒绝 Unix 凭据；macOS A1 不证明 Linux/Windows 或掉电耐久。回退用原兼容 profile/版本，不用旧二进制打开新 sealed 数据。

逐连接回读验证 `page_size=4096`、增量 auto-vacuum、`journal_mode=DELETE`、`synchronous=EXTRA(3)`、`foreign_keys=ON`、`busy_timeout=1000`；另设 `mmap_size=0`、trusted_schema 关闭。使用本机默认 VFS。hot journal 由 SQLite 恢复，应用不删 journal、不转换异常 WAL。硬件和文件系统行为仍影响耐久性。

`configuration.rs` 分开处理准备不可变 revision、runtime 解释上下文、config CAS 选择、actor 实际载入和 applied 确认。恢复幂等，先恢复选择再读取 active；启动安装恢复版本且连接/采集意图停止，随后确认 token。active、loaded、最后 used 分开；安全裁剪配置版本后完整 runtime context 保留。

统一串行 worker 最多接纳 4 个写入、1 个执行及 4 个排队短查询。查询 deadline 从入队前开始，过期未执行工作不再运行；执行中的 watchdog 按剩余 1000 ms 预算 interrupt，并在复用连接前 join。超时不保证能取消阻塞的 OS 磁盘 I/O。每 PLC actor 等完整轮提交结果才开始下一轮，全部读取/排队/提交在途最多 4 轮；最多 4 个连续写任务后给短查询机会。

完整轮事务先核不可变 context 及精确预期成员，分配一个 cycle ID/每 DB 一个 sample ID，写入所有成功/失败/null 质量、原时刻、排序 point-ID 字典、完整 manifest、pending 和下一个源序号，并原子更新 used revision。序号以整数持久化、十进制字符串输出，组筛选自然跳号。mutable ACK 不进入样本/manifest 摘要。runtime2 无上传器，runtime3 保留 v1 证据且不派发；runtime4 的匹配 v2 回执与样本状态在独立账本事务内提交，不伪造 v1 样本/分片/回执。无人工 ACK 或清空队列入口。

编码是 UTF-8 紧凑 serde JSON、固定 struct 字段顺序、BTreeMap 点字典与稳定 UUID key；有限 REAL 保留实际 f32 解码值的 f64 表示。新业务日历时刻统一固定上海毫秒`+08:00`，保存时间由SQLite在同轮事务内生成一次；不是PLC事件时间或精确COMMIT后时刻。SHA-256 覆盖原 payload 字节；历史不重新生成值。元数据每页最多 100 行。较大完整 context 通过同一 `daa_get_sample.contextOffset` 按 UTF-8 边界分段，每段最多 64KiB，带原 SHA、总字节数及 next offset；GUI 重组原上下文。跨调用不保留 statement/读事务。

物理准入包括运行主库/journal、配置主库/journal、日志、卷余量和预留。旧页 journal 保守边界含记录/头/扇区；4 个在途轮按 16 倍 B-tree/索引增长并加 32MiB 维护预留，分别采用旧版 512KiB 或 runtime4 的 4MiB 轮上限。准备 context 另加编码大小 3 倍；配置写入保守核旧镜像/新正文低于 64MiB。80/90/70% 告警/停采/恢复，并要求 512MiB 卷余量及预留；不使用 max_page_count 设额度。普通存储故障暂停采集，须有界写健康探针成功且容量恢复后才继续；这不解除下述日志故障锁存。

维护以有限批次前进游标扫描，保护 pending/不完整/有引用轮，后面的合格轮不会被旧 pending 饿死。实际每 60 秒 worker 分支在每个合格 DELETE 事务前，重核当前物理占用/卷余量、完整旧页 journal 上界、4 轮在途、维护和系统预留。cleanup 后，在独立的增量 vacuum 事务前再次读取预算；预算不足则延期，不将两个阶段宣称为整体原子。每批最多扫描 8 个候选 cycle、回收 64 页；失败或 busy 事务通过 rollback/drop 释放。私有 cfg(test) 覆盖交叠引用/不完整轮、两处预算边界、真实文件大小限制 I/O 失败和有效维护 hot journal 的 SIGKILL/重开；这些 hook 和 ACK 种子不进入产品/validation 构建。

事件保留 500 行，文件日志在 32MiB 内轮转。Engine 与串行 worker 共享同一个 Arc 日志对象和轮转 mutex，写入相同 profile 下的有界产品 JSONL；维护失败/延期同时输出结构化 stdout，字段为稳定的 event/process/resource/result/error_code，不递归提交 storage job。日志持久化失败报告 `local_log_failed/unknown_interval`，并锁存 `log_io_unknown_interval`；须修复日志并重启才能解除，不能靠普通存储健康探针恢复。此时停止新增存储写入和采集意图，后续维护写入也延期；只读历史/config/capacity、显式 Stop/disconnect 和正常 shutdown 仍可用，快照 PLC 错误及日志查询会反馈故障。这些日志是诊断记录，不能代替账本持久化。

## SQLite 3.46.0 适用性

v3 的 `delivery_settings`、`delivery_cycles`、`delivery_parts`、`delivery_batches`、`delivery_receipts`、`delivery_events` 保留为 v1 历史。runtime4 新增 `sample_upload_settings`、`sample_uploads`、`sample_upload_source_blocks`、`sample_upload_attempts` 和 `sample_upload_rebindings`；每条 v2 冻结记录保留目标、原 UTF-8 正文、摘要及请求身份。匹配有效回执与 v2 状态同事务提交；unknown 和需处理记录持续受保护。单 worker 有界交替选择最老与最新样本；暂停阻止新派发，在途响应可继续收尾。请求、回执、元数据及 journal 计入物理预算，另保留 32 MiB ACK 恢复空间。provider/MySQL 故障矩阵及完整恢复检查仍按 DAA-010 待完成。

下面的历史适用性说明不证明 r1 的 hot-journal 恢复；本次真实 ACK 崩溃在 RO preflight 失败，继续作为独立阻碍保留。

获批固定 bundled 依赖为 rusqlite 0.32.1 / libsqlite3-sys 0.30.1，source ID 为 `2024-05-23 13:25:27 96c92aba00c8375bc32fafcdf12429c58bd8aabfcadab6683e35bbb9cdebf19e`。此版本未包含全部后续修复。

- [WAL-reset 缺陷](https://sqlite.org/wal.html#the_wal_reset_bug)仍未修复；DELETE 和拒绝 WAL/SHM 移除了其 WAL 前提。
- [3.46.1 covering-index 复现](https://sqlite.org/forum/forumpost/e60e4c295d22f8ce)涉及 WITHOUT ROWID、partial UNIQUE 和 UPDATE。实际 schema 使用普通 rowid 表/普通整列索引，稳定 ID 不更新；定向测试对照 covering index、全扫描、独立预期数量及真实计划/opcode。
- [3.47.0 hot-journal 修复](https://sqlite.org/releaselog/3_47_0.html)针对 unix-dotfile；实际为 unix 默认 VFS。产品 SQL 事务在私有 fixture cache-flush 后生成有效 hot journal 并被 SIGKILL；Rust 重开保持原完整账本。SIGABRT 激活/提交断点另记，不混称 kill。
- 后续 UNIQUE-PK-IN 查询问题与静态 `CHECK(state IN ('pending','acknowledged'))` 不同；实际无 IN 子查询、view、outer join 或 expression/partial index。[AND 投影问题](https://sqlite.org/forum/forumpost/f4878de3e7dd4764)所需布尔聚合投影不存在，WHERE 为简单参数条件，并有结果对照。
- 无扩展、FTS、SQL JSON 函数、WASM/OPFS、自定义 VFS 或任意用户 SQL。物理 meter 只读 metadata，不在 owner 进程直接开关额外 DB 文件描述符；额度不降低 max_page_count，不接近默认页上限。

任务记录官方资料日期、依赖/原生来源、保留失败及有限适用性证据；这不等于 SQLite 全面安全结论。


## 历史 YAML receipt 保留

DAA-007 r2不再在普通bootstrap/engine读取YAML或执行迁入，新的空v2库保持空业务配置且不制造receipt/ETag。旧算法、mutator及历史边界测试仅cfg(test)编译，不提供常驻执行路径。没有新DDL/迁移或记录格式变化。

source_documents内的私有`__daa_yaml_migration_v1__` UUID行、规范JSON v1原字节/SHA及白名单archive/ID继续保留，不进入可编辑Configuration.sources。普通save/import拒绝保留前缀，source裁剪保护私有记录；不清理/重编码历史。具名兼容summary显式调用时只读SQLite，保留真实历史字段，返回视图强制retryAllowed=false；无receipt按实际返回not_attempted或existing_sqlite_preserved。retry在storage写任务、配置变化和文件读取前返回yaml_retry_forbidden。

## v1内的不可变来源版本

源导入继续使用原DDL和双库身份。可选`SourceDocument.lineageId`、`Db.importBinding`（块key、lineage、UDT来源版本闭包）仅位于配置JSON；字段缺失解码为None且缺省省略，配置/revision/历史读取不保存或重编码旧payload。旧deny_unknown_fields binary可能拒绝新增元数据，降级兼容另立gate。

Configuration的source ID是按PLC的逻辑版本，`source_documents.sha256`则是全库唯一物理正文归档。不同逻辑ID/名称/PLC的完全相同字节复用原归档行，不改其id/name/diagnostics/content；同ID异正文或hash/content不符使整事务拒绝。只准备所选目标delta，新source、草稿和新ETag在原表同一短事务提交，CAS/失败均回滚；无变化草稿保留原ETag。全部保留版本计入来源/JSON/写预算，未选来源及私有迁入receipt受保护。active/revision/runtime context/sample/manifest/generation/seq/pending/delivery/reference不属导入变更面。

Point.name为ASCII技术名，sourcePath原路径与稳定ID分开；唯一可选JSON nameMode为缺失legacy或pending/auto_path/auto_address/manual。legacy读取零写回，转换需明确勾选及预览。pending为空且停用，既有地址确认原子成名。唯一owner持有选择/预览/token，私有分页PointNamePreviewDialog及原编辑/offset弹窗展示差异；无第二owner/DDL/key。普通save不能去除/伪造mode或绕过改名预览。历史JSON/receipt原bytes保持，旧binary降级另核。

## DAA-007 新空时间合同

DAA-007 基线只对新空 profile 完整 CREATE v2，schema_migrations 当时记录 version2 及上海 applied_at；不运行旧库 ALTER/UPDATE/ledger 回填。基线 instance_metadata/runtime_metadata 均 schema_version=2；time_profile 固定 `asia-shanghai-rfc3339-ms-v1`，samples/样本 payload/manifest=2，configuration_revisions/contexts 与其 JSON=1，history/raw 等 IPC envelope 保持 1。目录名 local-acquisition-v1 只作定位。

此历史 v2 规则继续用于 unsealed profile：preflight 只探测本次显式 profile 的头/WAL、RO 元数据、身份/时间与原文件摘要，不使用 immutable。旧 UTC/未知/缺失/不匹配在业务写入前拒绝；锁后拒绝可留锁文件。r2 唯一新增的新 sealed 精确776例外与完整后检见上文，不授权旧 profile 恢复或补封。

business_time统一now/外部RFC3339规范化/SQLite时间表达式/滚动days cutoff。查询先转同一上海毫秒串，再比较闭区间，非法或逆序拒绝；retention、配置created_at排序、事件和receipt沿同合同，pending/incomplete/reference与资源预算保护保持。历史返回原UTF-8字节/SHA，不重写旧UTC数据。stdout的FormatTime使用上海纳秒，JSONL文件at保留毫秒，轮转/锁/失败锁存/level不变。定向DEV自检不是Owner原生或阶段B/C接受。
