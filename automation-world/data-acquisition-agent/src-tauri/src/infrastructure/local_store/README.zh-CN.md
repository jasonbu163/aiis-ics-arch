# 本地采集双库 v2

本适配层拥有 DAA-002 的本地 SQLite schema 与 SQL；不是 Backend DDL 或上传协议。实际实现/证据状态见 [任务](../../../../plans/DAA-002-local-acquisition-loop/tasks.md)。

| 库 | 表与责任 |
| --- | --- |
| `config.sqlite` | `schema_migrations`、`instance_metadata`、内容去重 `source_documents`、CAS `configuration_draft`、不可变 `configuration_revisions`、`active_selection`、可恢复 `activation_intents` |
| `runtime.sqlite` | `schema_migrations`、`runtime_metadata`、稳定 `plc_sources`、不可变 `configuration_contexts`、`activation_journal`、完整 `collection_cycles`、自描述 `samples`、独立 `sample_delivery` / `sample_references`、有限 `runtime_events` |

仅在空 `local-acquisition-v1/` 同时初始化双库，设置 application ID、user_version=2、相同 instance ID与time_profile 并核完整性。缺任一库、schema/身份不符、损坏、symlink 或异常 WAL/SHM 材料即拒绝，不自动修补或替换。profile 级 OS 锁覆盖 DAA 新旧 GUI/headless；不宣称不同 profile/主机之间的设备排他。

逐连接回读验证 `page_size=4096`、增量 auto-vacuum、`journal_mode=DELETE`、`synchronous=EXTRA(3)`、`foreign_keys=ON`、`busy_timeout=1000`；另设 `mmap_size=0`、trusted_schema 关闭。使用本机默认 VFS。hot journal 由 SQLite 恢复，应用不删 journal、不转换异常 WAL。硬件和文件系统行为仍影响耐久性。

`configuration.rs` 分开处理准备不可变 revision、runtime 解释上下文、config CAS 选择、actor 实际载入和 applied 确认。恢复幂等，先恢复选择再读取 active；启动安装恢复版本且连接/采集意图停止，随后确认 token。active、loaded、最后 used 分开；安全裁剪配置版本后完整 runtime context 保留。

统一串行 worker 最多接纳 4 个写入、1 个执行及 4 个排队短查询。查询 deadline 从入队前开始，过期未执行工作不再运行；执行中的 watchdog 按剩余 1000 ms 预算 interrupt，并在复用连接前 join。超时不保证能取消阻塞的 OS 磁盘 I/O。每 PLC actor 等完整轮提交结果才开始下一轮，全部读取/排队/提交在途最多 4 轮；最多 4 个连续写任务后给短查询机会。

完整轮事务先核不可变 context 及精确预期成员，分配一个 cycle ID/每 DB 一个 sample ID，写入所有成功/失败/null 质量、原时刻、排序 point-ID 字典、完整 manifest、pending 和下一个源序号，并原子更新 used revision。序号以整数持久化、十进制字符串输出，组筛选自然跳号。mutable ACK 不进入样本/manifest 摘要。产品无 ACK mutator/上传器/清队列；已确认种子仅在 `#[cfg(test)]`。

编码是 UTF-8 紧凑 serde JSON、固定 struct 字段顺序、BTreeMap 点字典与稳定 UUID key；有限 REAL 保留实际 f32 解码值的 f64 表示。新业务日历时刻统一固定上海毫秒`+08:00`，保存时间由SQLite在同轮事务内生成一次；不是PLC事件时间或精确COMMIT后时刻。SHA-256 覆盖原 payload 字节；历史不重新生成值。元数据每页最多 100 行。较大完整 context 通过同一 `daa_get_sample.contextOffset` 按 UTF-8 边界分段，每段最多 64KiB，带原 SHA、总字节数及 next offset；GUI 重组原上下文。跨调用不保留 statement/读事务。

物理准入包括运行主库/journal、配置主库/journal、日志、卷余量和预留。旧页 journal 保守边界含记录/头/扇区；4 个 512KiB 轮按 16 倍 B-tree/索引增长并加 32MiB 维护预留。准备 context 另加编码大小 3 倍；配置写入保守核旧镜像/新正文低于 64MiB。80/90/70% 告警/停采/恢复，并要求 512MiB 卷余量及预留；不使用 max_page_count 设额度。普通存储故障暂停采集，须有界写健康探针成功且容量恢复后才继续；这不解除下述日志故障锁存。

维护以有限批次前进游标扫描，保护 pending/不完整/有引用轮，后面的合格轮不会被旧 pending 饿死。实际每 60 秒 worker 分支在每个合格 DELETE 事务前，重核当前物理占用/卷余量、完整旧页 journal 上界、4 轮在途、维护和系统预留。cleanup 后，在独立的增量 vacuum 事务前再次读取预算；预算不足则延期，不将两个阶段宣称为整体原子。每批最多扫描 8 个候选 cycle、回收 64 页；失败或 busy 事务通过 rollback/drop 释放。私有 cfg(test) 覆盖交叠引用/不完整轮、两处预算边界、真实文件大小限制 I/O 失败和有效维护 hot journal 的 SIGKILL/重开；这些 hook 和 ACK 种子不进入产品/validation 构建。

事件保留 500 行，文件日志在 32MiB 内轮转。Engine 与串行 worker 共享同一个 Arc 日志对象和轮转 mutex，写入相同 profile 下的有界产品 JSONL；维护失败/延期同时输出结构化 stdout，字段为稳定的 event/process/resource/result/error_code，不递归提交 storage job。日志持久化失败报告 `local_log_failed/unknown_interval`，并锁存 `log_io_unknown_interval`；须修复日志并重启才能解除，不能靠普通存储健康探针恢复。此时停止新增存储写入和采集意图，后续维护写入也延期；只读历史/config/capacity、显式 Stop/disconnect 和正常 shutdown 仍可用，快照 PLC 错误及日志查询会反馈故障。这些日志是诊断记录，不能代替账本持久化。

## SQLite 3.46.0 适用性

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

只对新空profile完整CREATE v2，schema_migrations直接记录version2及上海applied_at；不运行旧库ALTER/UPDATE/ledger回填。instance_metadata/runtime_metadata均schema_version=2且time_profile固定`asia-shanghai-rfc3339-ms-v1`；samples/样本payload/manifest=2，configuration_revisions/contexts与其JSON=1，history/raw等IPC envelope保持1。目录名local-acquisition-v1只作定位。

锁前preflight仅探测本次显式profile：SQLite头部/WAL材料、RO元数据与双库身份、时间合同及原文件摘要。RO不使用immutable，也不进行hot-journal恢复；无法无写读取则拒绝。合格v2或新空才取原锁，再在任何RW前复核。旧UTC/未知/缺失/不匹配直接`time_profile_unsupported`且不创建锁/日志/旁库；锁后漂移分支允许已有锁文件，业务库未RW。原有合格v2的SQLite普通恢复仍在准入通过后进行。

business_time统一now/外部RFC3339规范化/SQLite时间表达式/滚动days cutoff。查询先转同一上海毫秒串，再比较闭区间，非法或逆序拒绝；retention、配置created_at排序、事件和receipt沿同合同，pending/incomplete/reference与资源预算保护保持。历史返回原UTF-8字节/SHA，不重写旧UTC数据。stdout的FormatTime使用上海纳秒，JSONL文件at保留毫秒，轮转/锁/失败锁存/level不变。定向DEV自检不是Owner原生或阶段B/C接受。
