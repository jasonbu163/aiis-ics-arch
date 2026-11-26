# 能源单价

[English](README.md)

启用的 `energy` 模块统一维护单价项目及每项目每小时的实际变更。[公开单价 API](../../../contracts/published/http-api/energy-pricing-v1/README.zh-CN.md) · [ARCH-ENERGY-001 r2](../../../plans/ARCH-ENERGY-001-configurable-hourly-pricing/spec.md)

- `energy_price_items` 存项目键、名称、单位、排序和启用状态。迁移初始化原三个内置项目。没有旧小时历史的环境从空价格开始。
- `energy_price_item_hours` 以项目和规范上海民用小时为唯一键，金额精度为 `DECIMAL(10,4)`。未提交项目保留原记录。写入锁定涉及的项目和小时，并在一个事务提交。
- `energy_price_hour_meta` 保存小时总备注及旧视图的稳定 ID、操作者和时间。新旧写入统一使用项目小时记录。旧视图按各项最近的适用小时组成完整三价。仅写入自定义项目时，显式提交的总备注可以更新已有兼容小时。

新业务时间保存为固定 `+08:00` 的 `DATETIME(6)`。按 IANA `Asia/Shanghai` 及 fold 0 确定小时身份，转换至固定 `+08:00` 后存储。记录、创建和实际修改各自保留事实语义。自然日先计算 IANA 本地零点边界，再转为固定偏移。旧历史按事件时间筛选，新历史按规范小时筛选。

## 采用修订 `7cb6e40f3d19`

1. 核对前驱 `af6d8b2c4e90`、schema 与服务器 UUID，确认原小时表四个时间字段遵循已验收的 UTC 存储约定。核对服务与数据库时钟，以及设备实时、过程曲线、能耗样本读链路。来源时区不确定或有人工导入记录时，先查清数据语义。
2. 在独立批准的操作中核对可恢复的数据库与应用备份，停止所有新旧写入，保存来源行数、ID 和代表性旧 API 响应。直到完成对账和服务切换才恢复写入。可执行 `SELECT @@server_uuid, DATABASE()`、`SELECT version_num FROM alembic_version`、`SELECT COUNT(*), MIN(id), MAX(id) FROM energy_price_hours`。
3. 设置 `ENERGY_PRICING_EXPECTED_SCHEMA`、`ENERGY_PRICING_EXPECTED_SERVER_UUID`、`ENERGY_PRICING_WRITE_WINDOW` 为已确认的 schema、UUID 和 `<schema>:<server-uuid>:UTC`。在已配置的 backend 对显式目标执行 `uv run alembic upgrade 7cb6e40f3d19`。这个后继需要在线 MySQL。逐项导入既有小时三价并保留其旧 ID。`energy_prices` 和 `energy_price_hours` 继续保留为转换来源。
4. 核对修订号、来源行数、每个来源小时的三条项目记录及旧 GET 完整投影。迁移脚本逐行核对金额、备注、操作者、ID 与转换后的时间，并通过 MySQL advisory lock 串行化迁移。切换后再次核对观测读链路和时钟，再恢复写入。无关的全库后继不影响日常价格读写。

失败时 MySQL 可能已经提交 DDL。继续保持停写，检查 `alembic_version`、暂存表结构和行数。结构一致且数据为空或能够逐行与来源对账时，可重跑同一显式升级。DDL 之后的导入与 revision 变更同事务。如果结构或内容不符，保留备份并在恢复副本上核查，再确定修复办法。未导入完成的数据库不得手工 stamp 为已采用。

### 回退与数据保护

先停写并备份三个新表、两个来源表和应用配置。切换后数据保持迁移原状时，在同一目标校验条件下经另行批准可运行 `uv run alembic downgrade af6d8b2c4e90`。回退在移除可重建的新表之前逐行确认其与原来源等价，发现数据增加或变化会拒绝。若回退在 DDL 后中断，保持停写并检查剩余结构，再重跑同一受控命令。

切换后已有写入时，先保留完整新表和可恢复备份。在写入暂停期间导出旧 GET 的全部分页，在独立恢复副本将完整兼容行投影为旧小时格式。保留 ID、三价、各项及总备注、操作者，把带偏移的四个输出时间解析还原为 UTC。逐行核对投影、ID 与小时键，调整恢复副本的自增值，使其高于导入最大 ID。旧三列无法表达的自定义价格、缺项的小时及部分录入原貌继续留在完整备份。切换旧程序、决定采用哪个恢复副本及后续清理，均由独立操作审批。

## BE004 旧追加表归并历史参考

以下 SQL 记录前驱的历史操作。r2 导入 UTC 小时表，保留更早的追加归档。

```sql
-- OPERATIONAL GATE ONLY. Confirm source/target DB, backups, paused writers, time source.
-- Replace only after confirming original timestamps; mixed or ambiguous sources mean STOP.
SET @legacy_offset = NULL;
SELECT COUNT(*) AS source_rows FROM energy_prices;
SELECT COUNT(*) AS target_rows_must_be_zero FROM energy_price_hours;
CHECKSUM TABLE energy_prices;
-- Any NULL/invalid conversion or target_rows > 0 means STOP / ROLLBACK.
WITH raw_times AS (
  SELECT energy_prices.*,
    CONVERT_TZ(created_at, @legacy_offset, '+00:00') AS event_utc,
    CONVERT_TZ(updated_at, @legacy_offset, '+00:00') AS modified_utc,
    DATE_FORMAT(CONVERT_TZ(created_at, @legacy_offset, 'Asia/Shanghai'),
      '%Y-%m-%d %H:00:00') AS civil_hour
  FROM energy_prices
), guessed AS (
  SELECT *, CONVERT_TZ(civil_hour, 'Asia/Shanghai', '+00:00') AS hour_guess
  FROM raw_times
), normalized AS (
  -- Shanghai's repeated DST hour has two instants. Choose the earliest (fold=0).
  SELECT *, CASE WHEN CONVERT_TZ(hour_guess - INTERVAL 1 HOUR, '+00:00', 'Asia/Shanghai') = civil_hour
    THEN hour_guess - INTERVAL 1 HOUR ELSE hour_guess END AS hour_start
  FROM guessed
)
SELECT COUNT(*) AS rows_seen, COUNT(DISTINCT hour_start) AS hour_groups,
  SUM(event_utc IS NULL OR modified_utc IS NULL OR hour_start IS NULL
      OR YEAR(event_utc) < 1000 OR YEAR(modified_utc) < 1000
      OR CONVERT_TZ(hour_start, '+00:00', 'Asia/Shanghai') <> civil_hour) AS invalid_rows
FROM normalized;
-- Verify timezone data yields fold=0: civil 1991-09-15 01:00 => UTC 1991-09-14 16:00.
-- Conflict groups and selected old ids are local audit artifacts; never commit them.
WITH raw_times AS (
  SELECT energy_prices.*,
    CONVERT_TZ(created_at, @legacy_offset, '+00:00') AS event_utc,
    CONVERT_TZ(updated_at, @legacy_offset, '+00:00') AS modified_utc,
    DATE_FORMAT(CONVERT_TZ(created_at, @legacy_offset, 'Asia/Shanghai'),
      '%Y-%m-%d %H:00:00') AS civil_hour
  FROM energy_prices
), guessed AS (
  SELECT *, CONVERT_TZ(civil_hour, 'Asia/Shanghai', '+00:00') AS hour_guess
  FROM raw_times
), normalized AS (
  -- Shanghai's repeated DST hour has two instants. Choose the earliest (fold=0).
  SELECT *, CASE WHEN CONVERT_TZ(hour_guess - INTERVAL 1 HOUR, '+00:00', 'Asia/Shanghai') = civil_hour
    THEN hour_guess - INTERVAL 1 HOUR ELSE hour_guess END AS hour_start
  FROM guessed
), ranked AS (
  SELECT *, COUNT(*) OVER (PARTITION BY hour_start) AS group_size,
    ROW_NUMBER() OVER (PARTITION BY hour_start ORDER BY created_at DESC, id DESC) AS rn
  FROM normalized
)
SELECT hour_start, id AS selected_old_id, group_size,
  SUM(group_size > 1) OVER () AS conflict_groups
FROM ranked WHERE rn=1 ORDER BY hour_start;
-- Only execute after all gates pass, with all old/new writers paused.
START TRANSACTION;
SELECT COUNT(*) AS target_rows_must_be_zero FROM energy_price_hours;
INSERT INTO energy_price_hours
  (electric_price, hydrogen_price, argon_price, electric_remark, hydrogen_remark,
   argon_remark, remark, operator, observed_at, hour_start, created_at, updated_at)
WITH raw_times AS (
  SELECT energy_prices.*,
    CONVERT_TZ(created_at, @legacy_offset, '+00:00') AS event_utc,
    CONVERT_TZ(updated_at, @legacy_offset, '+00:00') AS modified_utc,
    DATE_FORMAT(CONVERT_TZ(created_at, @legacy_offset, 'Asia/Shanghai'),
      '%Y-%m-%d %H:00:00') AS civil_hour
  FROM energy_prices
), guessed AS (
  SELECT *, CONVERT_TZ(civil_hour, 'Asia/Shanghai', '+00:00') AS hour_guess
  FROM raw_times
), normalized AS (
  -- Shanghai's repeated DST hour has two instants. Choose the earliest (fold=0).
  SELECT *, CASE WHEN CONVERT_TZ(hour_guess - INTERVAL 1 HOUR, '+00:00', 'Asia/Shanghai') = civil_hour
    THEN hour_guess - INTERVAL 1 HOUR ELSE hour_guess END AS hour_start
  FROM guessed
), ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY hour_start ORDER BY created_at DESC, id DESC) AS rn
  FROM normalized
)
SELECT electric_price, hydrogen_price, argon_price, electric_remark, hydrogen_remark,
  argon_remark, remark, operator, event_utc, hour_start, event_utc, modified_utc
FROM ranked WHERE rn=1;
SELECT COUNT(*) AS imported_hours FROM energy_price_hours;
CHECKSUM TABLE energy_prices;
-- Compare counts, whole groups and times with the selected-old-id manifest.
-- COMMIT only after review; default example explicitly rolls back.
ROLLBACK;
```
