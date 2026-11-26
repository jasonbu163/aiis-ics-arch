# Energy prices

[中文版本](README.zh-CN.md)

The enabled `energy` module owns price definitions and actual changes by project and hour. See the [public pricing API](../../../contracts/published/http-api/energy-pricing-v1/README.md) and [ARCH-ENERGY-001 r2](../../../plans/ARCH-ENERGY-001-configurable-hourly-pricing/spec.md).

- `energy_price_items` defines project keys, labels, units, ordering and availability. The migration adds the three built-ins. A deployment with no hourly price history starts with empty prices.
- `energy_price_item_hours` stores actual project updates, one exact `DECIMAL(10,4)` amount per project and canonical Shanghai civil hour. An omitted project stays as recorded. Writes hold locks on the submitted items and the hour, and commit once.
- `energy_price_hour_meta` holds the hour remark and the stable ID, actor and timestamps for the legacy view. Old and new writes use the same item-hour facts. The legacy view inherits each value from its latest applicable hour and only returns complete triples. Custom-only updates can change a legacy hour remark when explicitly supplied.

All new business timestamps are fixed `+08:00` `DATETIME(6)`. The hour is determined in IANA `Asia/Shanghai` with fold 0, then stored as the corresponding instant at fixed `+08:00`. The event, creation and modification timestamps retain their separate meanings. The date bounds use IANA local midnight before conversion. GET dates filter the legacy view by observed time and the new history by canonical hour.

## Adopting revision `7cb6e40f3d19`

1. Verify the exact predecessor `af6d8b2c4e90`, schema and server UUID, and confirm all four legacy hourly timestamps use the accepted UTC storage convention. Verify both clocks and check that the existing equipment, process and energy-sample readers work against the target. Resolve ambiguous or manually imported time data before scheduling migration.
2. Through a separately approved operation, verify a recoverable database and application backup, drain all legacy and new writers, and capture counts, IDs and representative legacy API responses. Keep writers drained through final reconciliation and service cutover. Example preflight queries include `SELECT @@server_uuid, DATABASE()`, `SELECT version_num FROM alembic_version` and `SELECT COUNT(*), MIN(id), MAX(id) FROM energy_price_hours`.
3. Set `ENERGY_PRICING_EXPECTED_SCHEMA`, `ENERGY_PRICING_EXPECTED_SERVER_UUID` and `ENERGY_PRICING_WRITE_WINDOW` to the confirmed schema, UUID and `<schema>:<server-uuid>:UTC`. From the configured backend run `uv run alembic upgrade 7cb6e40f3d19` against that explicit target. This is an online MySQL migration. It imports each source hour's three prices and preserves the old ID. `energy_prices` and `energy_price_hours` remain available as conversion sources.
4. Check the revision, source row counts, three item-hour rows per source hour and the exact legacy GET projection. The migration checks all imported metadata, numeric values, remarks and converted timestamps against the source and serializes migration attempts through an advisory lock. Check the observation readers and API/DB clocks again before resuming writes. Later unrelated database revisions do not gate ordinary pricing traffic.

MySQL may have already committed DDL when the migration fails. Keep writers drained and inspect `alembic_version`, staged table definitions and row counts. A repeated explicit upgrade accepts a stage whose definitions match and whose tables are empty or reconcile entirely. The import and revision change are transactional after DDL. For divergent rows or definitions, retain a backup and reconcile the staged data in a restore copy before deciding on recovery. Do not stamp an incomplete adoption.

### Rollback and data preservation

Keep writes paused and back up all three new tables, both source tables and the current application configuration. With an untouched post-migration stage, the explicitly approved `uv run alembic downgrade af6d8b2c4e90` under the same target guard verifies exact equivalence to the predecessor and removes the three reproducible tables. It rejects additive or changed data. If a downgrade stops after a DDL step, keep writers paused and inspect the remaining stage before repeating the guarded command.

With post-cutover writes, retain the entire new schema and its verified backup first. Export all pages of legacy GET in one maintenance window. In a separate restore copy, build an old-format hourly table from the complete projected rows. Keep `id`, three prices, per-price and top-level remarks and operator, and convert all four wire timestamps back to UTC by parsing their offsets. Reconcile all exported rows, distinct IDs and hour keys with that copy and advance its auto-increment above the largest copied ID. New-only single-item hours, omitted values and custom items remain in the full backup because the old format cannot represent them. A service rollback, choice of projected restore data and any eventual cleanup require an independent operational decision.

## Historical reference for the BE004 append-to-hour conversion

The historical SQL below documents the predecessor conversion. The r2 migration imports the UTC hourly table and leaves the older append archive intact.

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
