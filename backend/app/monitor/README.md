# Monitor facts and business history

[中文版本](README.zh-CN.md)

Core collector/status and realtime/latest retain the original three Models and `monitor` permission. `app.monitor.models:PlcDbBlockRawSnapshot` is a public read-only Model export for explicit model_requires consumers; this exposes no collector writer or new API.

The separate `/monitor/temperature` and `/monitor/energy` GETs require `monitor-business-read`. Neither key grants the other surface. These queries read the two business history tables and never persist diagnostic samples, including when business mock configuration is enabled. Empty curves remain empty. The process-curve synchronous Projection descriptor is local and caller-transaction owned; discovery never starts it or publishes mapping.

Only HistoryProcessCurve and HistoryEnergyConsumption supplement the three Core Models; the twelve former HMI/deprecated/alarm/tracking Models are excluded. See the [public contract](../MODULE_CONTRACT.md). The explicit schema successor and source checks require separate MySQL/runtime gates before adoption; no CA/PLC operations are implied.


## External process curves

POST/GET `/monitor/process-curve-samples` uses the independent `monitor-curve-ingest/read` permissions and
`MONITOR_MAPPING_INGEST_ID` scope. POST appends immutable source samples, at least one of the existing 33
measurements; twelve temperatures are signed integers, twenty-one values are FLOAT measurements. coilNumber is
optional. Same source millisecond with different content or field presence returns 409; accepted curves are not
overwritten. This does not write energy summaries or create performance parents.

GET requires equipmentId and exact YYYY-MM-DD in Asia/Shanghai; UTC sampled_at is filtered by that natural day.
Optional recordId and limit 1–1000 (default 1000) select the latest samples, returned ascending as complete items,
trends and latest. Empty results are [], [] and {}. All four charts preserve missing values as gaps/missing symbols.
The curve page persists legacy/http source and equipment in the URL; HTTP scope/data failures never fall back.
The old temperature endpoint reads only NULL equipment rows using its existing created_at date semantics.
Collector/raw/latest and energy surfaces keep their original source and permissions.


## Anonymous business integration preparation

[ARCH-BE-010 r1 A0](../../../plans/ARCH-BE-010-anonymous-business-integration/spec.md) adds eight typed anonymous POST routes below `/integration/` and finite [public primitives](../MODULE_CONTRACT.md#anonymous-integration-primitives). Existing authenticated APIs and permissions retain their behavior. All three module switches default off, device/producer scopes default empty, and storage profiles default `unadopted`. Disabled/out-of-scope requests return 403; admitted A0 requests return 503 before any database dependency or business access. No profile value enables business writing in this preparation slice. Module `enabled=False` removes its entire new/old route group after recomposition.

The four new Model declarations describe three module-owned permanent minimal receipts and the production observation-event index. They do not apply DDL or establish a migrated schema. Shared-table Shanghai time adoption, exact Alembic chain, business wiring and disposable MySQL verification remain separate gates. Anonymous producer/source declarations can be impersonated; scopes are admission policy, not authentication. The [task record](../../../plans/ARCH-BE-010-anonymous-business-integration/tasks.md) contains the pending source-based time/migration proposal.


## Bounded business integration (r2)

The anonymous integration Service/CRUD is implemented against this owner's existing business tables, with permanent minimal receipts and typed [provider](../../../contracts/published/http-api/business-integration-v1/README.md). Defaults stay disabled/empty/unadopted. A valid external adoption manifest and a matching transaction-local UUID/schema/revision/DB-clock probe are required; the shared schema successor is BE010 1b3 after BE009 0a2. Legacy HTTP and Projection time adaptation is finite and owner-local; unadopted retains the original path. Real historical conversion/target adoption and database/Docker/B remain separately approved; no raw/latest retention or PLC writer changes are implied.

The existing curve created_at field combines system and Projection source timestamps without a reliable per-row wire-basis discriminator. This bounded implementation rejects monitor adoption if legacyNaive differs from systemWire; NULL equipment/device values cannot authorize an inferred basis. More detailed source tags/cohorts require separate scope.
