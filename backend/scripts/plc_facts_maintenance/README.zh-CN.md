# PLC facts维护CLI

## r3 单表迁移与恢复

仅在目标操作获明确批准后执行。先停止该目标的来源登记、样本上报及清理，保留可恢复备份和旧私有 JSON。只读核对 MySQL 8.4、上海时钟、UUID、schema、单一前驱 `6a8c0e2b4d16`、六张旧表及初始化状态；记录无活跃绑定的只读 PLC 和采用后新可读取的 DB。状态未知、资料不齐或核对不符时停止。

r2 已初始化则以数据库为准，用**冻结 r2 源码**的 `export-sources` 保存登记和代次。仅建表而旧登记在 JSON 时，以冻结 r2 工具预览、导入并对账，再执行后继迁移。六表均为空且明确确认从空登记开始时，设置 `ACQ_REGISTRY_R3_EMPTY_CONFIRMED=1`，无需先执行 r2 空初始化。当前 r3 的旧 import/export 命令直接拒绝，不能在 r3 表上运行；下方 r2 示例仅供冻结前驱工具参考。

对已获准目标设置 `ACQ_REGISTRY_EXPECTED_SERVER_UUID` 和 `ACQ_REGISTRY_EXPECTED_SCHEMA`，在后端项目目录执行锁定环境中的 `alembic upgrade 7b9d1f3a5c7e`。迁移校验目标、归并登记及退役代次，核对标识字节、版本与时间；在删除六旧表前两次扫描完整的 `plc_facts_history` 和 `plc_facts_latest`，比较表结构、行数和全部行的 SHA-256（含原样本和最新序号水位），输出摘要供保存。大表两次全表扫描可能耗时较长，需为停写窗口、资源和日志留足时间。比较不符或迁移中断立即停止。

MySQL DDL 非事务，失败时先保全现场并核查实际表、内容及 revision，不 stamp、不删表盲目重跑。以可验证的前驱备份恢复，或根据已知状态进行前向修复；逐项对账旧登记、两事实表和水位。若 r3 已有新提交，先保全这些登记和事实并评估是否能无损重放；不能无损表达时保留现场并采用前向修复。完成迁移后更新仓外运行目标 revision、清理工具与已知 revision 校验；核对登记、样本回执及读回后再恢复服务。旧有前驱环境未切换前继续遵循其原合同。

## r2 候选：迁移、导入与恢复（冻结前驱工具）

这些步骤只适用于已批准的独立合成目标；源码就绪不代表 dev 或生产已迁移。先暂停该目标登记、采集写入和清理，保存可验证的前驱备份及旧来源文件。迁移前核对 MySQL 8.4、上海数据库时钟、目标 UUID、schema、单一前驱 `5f7a9c1e3b25`。使用专用迁移账号设置 `ACQ_REGISTRY_EXPECTED_SERVER_UUID` 和 `ACQ_REGISTRY_EXPECTED_SCHEMA` 后执行 `alembic upgrade 6a8c0e2b4d16`。MySQL DDL 非事务：中断或目标已有部分对象时停止，记录实际对象与 revision，以核对过的前驱备份恢复到独立目标；不要 stamp、删表后盲目重跑。所有后端切换到新候选和只含 target 的私有运行配置之前必须完成导入及对账。

导入需提供旧 JSON 的仓外绝对路径、原目标及单次操作批准引用。空目标也要以合法空配置显式初始化。以下占位符均须替换为本次获准的值：

```text
uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py import-sources --plan --target-alias <alias> --schema <schema> --expected-server-uuid <uuid> --expected-schema-revision 6a8c0e2b4d16 --operation-approval <approval-ref> --confirmed-by <operator> --source-file /private/approved/old-profile.json
```

核对预览的来源、读写对计数与 `logicalSha256`、`sourceSha256`。执行时启用 `PLC_FACTS_MAINTENANCE_ENABLED=True`，改为 `--apply`，加 `--expected-source-sha256 <sha>` 和 `--confirm IMPORT:<alias>:<schema>:<uuid>:<sha>`。一次事务写入登记和初始化记录；相同来源再次执行只核对，不覆盖后来登记。若出现 `import_commit_unknown`，用同一文件重新 `--plan`，对照初始化标记、原摘要、当前摘要和数量，再决定处理；不能把异常视为成功或盲目重播。

回退前记录两张事实表水位并备份，保全 Web 增量、读写范围和代次。完成暂停后执行只读导出（`<restore-*>` 是独立恢复目标的身份）：

```text
uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py export-sources --target-alias <alias> --schema <schema> --expected-server-uuid <uuid> --expected-schema-revision 6a8c0e2b4d16 --operation-approval <approval-ref> --confirmed-by <operator> --restore-alias <restore-alias> --restore-schema <restore-schema> --restore-server-uuid <restore-uuid> --output-file /private/approved/source-export.json
```

导出文件以独占新建方式保存私有材料，包含 `legacyProfile`、全部 `generations`、登记版本和摘要；保留完整文件及终端文件 SHA。将 `legacyProfile` 原样写成单独私有 JSON，前驱解析时目标须与恢复库实际 UUID/schema 一致。独立恢复库从精确前驱备份建立；复制切换后的 `plc_facts_history` 和 `plc_facts_latest` 全部必要行，并逐行核对主键、正文、摘要、时间和水位。只有恢复库相应事实表为空、列结构一致且已获准时，才可按表使用 `INSERT INTO <restore>.<table> SELECT * FROM <source>.<table>`；非空时先逐键对账，冲突不得覆盖，不能证明守恒则停止并采用另批前向修复。再用前驱程序解析恢复 profile、核对全部活跃写范围、独立读范围及事实后才考虑采用。

以后再次采用 r2 时，导入上述完整导出文件的 `generations`：`import-sources --plan ... --source-file <前驱profile> --generation-file <source-export.json>`，核对 `generationFileSha256` 和保留代次数；执行确认串在原 source SHA 后加 `:<generation-file-sha>`。若实例类型、PLC 或目标与保留资料不符，工具拒绝导入。导出不替代事实备份，不自动切换服务。[候选规格](../../../plans/ARCH-ACQ-004-acquisition-source-registry/spec.md)

## v2 到期清理

`cleanup-v2` 需要显式选择 `--plan` 或 `--apply`，并提供目标 alias、schema、server UUID、revision、操作批准引用及确认人。alias、库名和实例 UUID 须匹配仓库外 v2 私有配置，传入 revision 须精确匹配数据库实际版本。清理要求九表结构已启用消费。预览示例使用合成目标。

```bash
uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py cleanup-v2 --plan --target-alias dev-example --schema fixture_schema --expected-server-uuid 00000000-0000-4000-8000-000000000001 --expected-schema-revision a1c307f8d2e4 --operation-approval fixture-approval --confirmed-by fixture-operator
```

清理字节预算包括可空的历史 `source_type`；`acq_plc_facts_history` 按整份样本删除，`acq_plc_facts_latest` 清除值并保留顺序水位。

执行时设置 `PLC_FACTS_MAINTENANCE_ENABLED=True`，将 `--plan` 换为 `--apply`，并提供 `--confirm APPLY:cleanup-v2:<alias>:<schema>:<server-uuid>:<revision>`。计划和执行输出 JSON Lines，结果含行数、字节、最早积压及完成时刻。每事务最多 200 行和 2 MiB，每次最多 2000 行、20 MiB 和 2 秒处理预算。外部调度每分钟调用，按完成时刻与最早积压配置告警。历史整行删除，latest 保留实例、代次和序号水位。

每个事务在目标锁探针前设置有界行锁和元数据锁等待。若预算耗尽而未完成积压查询，结果中的 `oldestKnown` 为 `false`，监控应将该次积压状态视为未知。完成时刻使用无表锁的数据库时钟查询，连接读写也有超时。

使用现有项目环境：`uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py`只显示帮助，不加载settings/数据库。`--help`同样无副作用。本工具无默认输入目录、输出文件、目标、seed、DDL、调度器或打包产物。

旧 v1 `status`、`adopt` 和 `cleanup` 命令已退役。实际清理仍需单独授权并限定目标。

## ARCH-ACQ-007 表名切换

前向迁移 `a1c307f8d2e4` 的单一前驱是质量迁移 `f0a2b4c6d8e1`。对实际 MySQL UUID、库名和前驱取得操作批准。保留可恢复备份及九表基线，包含键、行数、latest 水位和现有消费者证据。暂停来源变更、样本写入、消费者、清理和直库写入，等待在途事务结束。整个窗口内停止新旧进程。

由目标 Owner 审查表级授权、SQL 工具、报表，以及视图、外键、存储程序、定时事件和其他触发器正文。迁移拒绝维护账号可见的已知外键及视图引用。确认窗口前由目标 Owner 核对权限可见范围以外的引用。MySQL 旧表名的表级授权不随表名迁移，采用前核对已有库级访问权或取得单独授权。维护账号须能读取三个 history 触发器并执行改名。在线账号无需查看触发器元数据。

仅在明确批准的窗口内设置 `ACQ_TABLE_NAMES_EXPECTED_SCHEMA`、`ACQ_TABLE_NAMES_EXPECTED_SERVER_UUID` 和 `ACQ_TABLE_NAMES_WINDOW_CONFIRMED=<schema>:<uuid>:f0a2b4c6d8e1`，从 `backend/` 运行 `uv run --offline --frozen --no-sync alembic upgrade a1c307f8d2e4`。恢复前确认新版本、九表及其行与键证据、三个 history 触发器定义和行为，并核对在线账号能访问新表名及其他共库模块能否接受新版本。缺少追加事件时，写入和重复回执均不得成功。在线账号无法察觉窗口外特权账号对不可变或到期守卫的修改。

三张表在同库的一条语句中更名。MySQL DDL 提交与 Alembic 版本更新分离。出错时保持停写，记录实际表名、键约束、触发器定义、消费状态和 revision。前驱版本下已更名或部分更名时，重跑会拒绝。将现场状态和已提交事实与备份核对后，另行批准前向修复或恢复。禁止盲目 stamp、删表和覆盖不可安全重放的事实。
