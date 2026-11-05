# PLC facts维护CLI

使用现有项目环境：`uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py`只显示帮助，不加载settings/数据库。`--help`同样无副作用。本工具无默认输入目录、输出文件、目标、seed、DDL、调度器或打包产物。

显式命令为`status`、`adopt --plan/--apply`、`cleanup --plan/--apply`；全部DB访问包括status/plan需要另批G-B目标。必须指定target-alias、schema、expected-schema-revision、expected-storage-epoch、operation-approval、confirmed-by；apply还需`PLC_FACTS_MAINTENANCE_ENABLED=True`及`--confirm APPLY:<action>:<target-alias>:<schema>:<storageEpoch>`。

adopt选来源时明确plc/instance/generation/config、context-file及SHA、expected-binding-revision/new seq-from；切换须old-seq-through、窗口最多8。`adopt --revalidate-schema-only`只核已知0a2/1b3/F7并CAS更新采用凭据，禁止同时传source参数。已有控制行需expected-adoption-id及原epoch；不改变历史proof或TTL。

配置优先级CLI > OS env > 本工具.env > backend.env > 安全默认。示例开关关闭，不提交实际配置或凭据。默认stdout为start/dry-run/commit/failed/complete JSON Lines；显式`--output-log`才写文件，失败非零且脱敏。cleanup每事务200行/2MiB/100ms、每tick10事务/2000行/20MiB/2s，锁NOWAIT，正常写优先；不清业务/非owner数据。运行频率和24小时物理SLA须独立安排及验证，A未运行。
