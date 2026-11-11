# PLC facts维护CLI

## v2 到期清理

`cleanup-v2` 需要显式选择 `--plan` 或 `--apply`，并提供目标 alias、schema、server UUID、revision、操作批准引用及确认人。目标必须与仓库外 v2 私有配置和实际数据库一致。预览示例使用合成目标。

```bash
uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py cleanup-v2 --plan --target-alias dev-example --schema fixture_schema --expected-server-uuid 00000000-0000-4000-8000-000000000001 --expected-schema-revision 4e6a8b0d2f14 --operation-approval fixture-approval --confirmed-by fixture-operator
```

清理字节预算包括可空的历史 `source_type`；`plc_facts_history` 按整份样本删除，`plc_facts_latest` 清除值并保留顺序水位。

执行时设置 `PLC_FACTS_MAINTENANCE_ENABLED=True`，将 `--plan` 换为 `--apply`，并提供 `--confirm APPLY:cleanup-v2:<alias>:<schema>:<server-uuid>:<revision>`。计划和执行输出 JSON Lines，结果含行数、字节、最早积压及完成时刻。每事务最多 200 行和 2 MiB，每次最多 2000 行、20 MiB 和 2 秒处理预算。外部调度每分钟调用，按完成时刻与最早积压配置告警。历史整行删除，latest 保留实例、代次和序号水位。

每个事务在目标锁探针前设置有界行锁和元数据锁等待。若预算耗尽而未完成积压查询，结果中的 `oldestKnown` 为 `false`，监控应将该次积压状态视为未知。完成时刻使用无表锁的数据库时钟查询，连接读写也有超时。

使用现有项目环境：`uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py`只显示帮助，不加载settings/数据库。`--help`同样无副作用。本工具无默认输入目录、输出文件、目标、seed、DDL、调度器或打包产物。

旧 v1 `status`、`adopt` 和 `cleanup` 命令已退役。实际清理仍需单独授权并限定目标。
