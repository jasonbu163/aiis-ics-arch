# PLC facts owner

This API-only owner provides `POST /api/v1/integration/plc-facts/batches` and GET `latest`/`history`, using `plc-facts/v1`, `daa-local/v2` and `pf-json/v1`. Anonymous source declarations can be impersonated; PLC scope is admission policy.

Default-off/empty-scope/unadopted/keyless requests fail before the DB dependency. Eligible requests still require explicit MySQL 8.4 schema, Shanghai clock and source adoption; no request creates tables or adopts a source. Disabling the manifest removes only these routes after composition. Seven tables follow f6→0a2; BE010 separately owns the 1b3 successor. Both known runtime profiles require the same F7 and explicit schema-only revalidation after upgrade.

Original UTF-8 v2 payload/manifest/context and their SHA values remain intact. Fixed greedy parts, complete expected membership and content/cycle/request digests are checked independently. The Service owns transactions and allocates publication serials under the singleton lock. Success is sent after commit and complete yield-dependency exit. Stable original outcomes replay first; finite receipt/parent rejection proofs expire after 120 days without renewal. Uncertain commits return unknown.

Latest compares sourceSeq per point within the current sourceEpoch; bad replaces good. Source switching removes previous latest; unchanged definitions preserve valid results across context/revision changes. Changes scans publication positions; range freezes H and filters original observedAt using half-open bounds. Filtered projections carry separate digests and expired values produce gaps. Cursor TTLs are 24 hours/15 minutes/30 seconds; key rotation requires an explicit new baseline.

Values default to three natural months, optionally one or two, from original point observation with nanoseconds preserved. Every read checks expiry. Original payload expires conservatively at its earliest point; latest expires per point. No scheduler is created. The [maintenance CLI](../../scripts/plc_facts_maintenance/README.md) performs bounded ticks against seven tables only; physical cleanup requires separately approved runtime verification. No business records cascade from raw/proof cleanup.

See the [machine contract](../../../contracts/published/http-api/plc-facts-v1/README.md) and [approved spec](../../../plans/ARCH-BE-009-backend-facts-integration/spec.md). Source implementation does not establish provider readiness, adoption, DAA upload or deployment. A runs no database, Docker or migration operations; runtime gates and actual evidence belong to the task bundle.
