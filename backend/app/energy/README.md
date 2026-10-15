# Energy prices

[中文版本](README.zh-CN.md)

Energy is the unique owner of the two price tables, three routes and read/manage permissions. This reusable module owns hourly whole-group energy prices. Customer-specific rules and data belong to consuming projects. [backend PLAN](../../PLAN.md) indexes work; [ARCH-BE-004 r2](../../../plans/ARCH-BE-004-energy-price-hourly-history/spec.md) defines the current contract. [BE002](../../../plans/ARCH-BE-002-energy-price-api/spec.md) remains the accepted append-only historical baseline.

## API and time contract

The enabled manifest retains exactly GET `/energy/current`, GET `/energy` and POST `/energy` under the configured prefix. GET requires `energy-price-read`, POST `energy-price-manage`; neither implies the other and frontend visibility grants neither. Existing admin / supervisor / operator guards remain.

Three required prices use Decimal / Numeric(10,4), 0..999999.9999, at most four effective decimal places. Raw JSON decimals are parsed exactly before validation; decimal strings are accepted and output prices are JSON numbers. Zero is valid. Electric units are CNY/kWh; gas units CNY/Nm³. Per-price remarks allow 500 characters, remark 2000; empty strings become null. Actor comes from authenticated username. No implicit DDL, defaults or seed exist.

POST accepts optional / null `observedAt`; the API captures aware UTC now once for fallback and future validation. Explicit input must be an offset-bearing ISO datetime within MySQL DATETIME and Shanghai conversion bounds; invalid, empty, naive or future inputs return 422. The event is converted using fixed `Asia/Shanghai` and floored to its hour. MySQL unique key `uq_energy_price_hours_hour_start` and atomic upsert replace all prices, remarks, observedAt and operator together; id/hourStart/createdAt remain. Service commits/rolls back; CRUD never does. Each new HTTP request captures a new now. No request retries or hourly jobs are introduced.

`energy_price_hours` stores observed_at/hour_start and DB-created/updated timestamps as UTC DATETIME(6); DB expressions use UTC_TIMESTAMP(6) without changing global connection timezone. Outputs `observedAt`, `hourStart`, `createdAt`, `updatedAt` carry Shanghai offsets. hourStart identifies a final hourly snapshot, not minute-by-minute effective pricing; updatedAt means actual modification time.

Current selects observed_at <= request now ordered by observed_at DESC,id DESC, returns null if none and carries the latest price across missing days. Backfilling an earlier hour cannot win by updatedAt. GET history retains `{items,total,page,pageSize}` (1/20, size 1..100); optional single strict `date=YYYY-MM-DD` filters the Shanghai observedAt day. Sorting is observed_at DESC,id DESC; total is filtered, empty/out-of-range pages have no items, boundary dates are safe. No empty hours are created. The UI requests page 1/size 24, displays readonly current cards, and adds whole groups via a datetime picker interpreted in Shanghai; null means server now. Saving an existing hour overwrites it. Successful save switches history to the response event day and refreshes both GETs; historical POST results are never assigned directly to current.

The business hour identity is the Shanghai civil date/hour. A repeated DST hour uses fold=0 (its earliest instant) for the UTC hour_start key; observed_at retains the actual event instant, so the day still has at most 24 rows. Nonexistent picker civil times fail validation. Wire timestamps use fixed +08:00 to preserve the instant in a browser-compatible format, while display and picker resolution use IANA Asia/Shanghai, including historical rules.

## Explicit schema and legacy conversion gate

The immutable fourteen-table `d4e6f8a0b2c4` root and BE002 `a6c8e0f2b4d6` remain unchanged. BE004 successor `b8d0f2a4c6e8` only creates the hours table, forming the protected sixteen-table baseline. BE005 successor `d2f4a6b8c0e2` adds 42 other business tables; this task's F composition has 58 tables. Every original energy_prices row and its Model remain intact. Registry, startup and ordinary requests never import legacy data.

Before runtime adoption, independently approve exact source/target database, the original naive timestamp source, verified recoverable backups, a paused-writing window, commands and rollback owner. Never infer the old timezone. Verify MySQL named timezone tables (Asia/Shanghai) and both service/DB clocks. Mixed/ambiguous legacy time sources or invalid conversions require resolution before import. Preflight records source rows, hour groups, conflict group count, invalid rows and each selected old id in controlled local artifacts. A nonempty target or any invalid/unexplained time means stop; do not merge over existing hours. The SQL below requires human review between the preflight and transaction; it is not an unattended script.

Select each hour's last complete row by `(created_at DESC, id DESC)`, preserve its whole group, event time and original created/updated meaning after timezone conversion. New ids are independent. Compare imported hours and every price/remark/operator/time with the selected-id manifest; compare original row count and checksum before/after. Commit only after these checks, then switch application. An unimported new table returning null does not mean the old business lacked prices.

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

The default SQL ends with ROLLBACK. Real import/COMMIT requires the separate operational gate. Source/static tests use only synthetic rows; they do not prove live MySQL concurrency or backup recovery.

## Rollback and validation

Stop new writes and back up the hours table first. The old append archive lacks all post-switch writes; reverting the application does not recover them. Converting new hourly snapshots back into append format requires separate approval and reconciliation. Downgrading b8d0f2a4c6e8 drops only energy_price_hours and loses all its data; actual downgrade/deletion/replay is separately approved. Overwritten within-hour versions are not retained and billing recalculation is outside scope.

Use the task's public isolated fixtures and existing uv/pnpm dependencies for complete no_db tests, compileall, offline Alembic SQL and frontend module checks/tests/build. Real persistence, unique-key competition, historical import/restore, clock checks and runtime integration remain deferred operational gates. Source checks do not establish deployment. [API tests](../../tests/test_energy_price_api.py).
