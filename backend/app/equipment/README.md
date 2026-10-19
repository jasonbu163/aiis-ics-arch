# Equipment

[中文版本](README.zh-CN.md)

Equipment owns the existing drive, temperature-control and production dashboard GETs and their three legacy tables. The eight existing local Projection descriptors across the repository and their caller-owned business/cursor/audit transactions remain separate from the new HTTP sample receiver.

## Complete temperature samples

`POST /api/v1/equipment/temperature-samples` accepts one immutable complete observation: `equipmentId`, stable `sampleId`, timezone-qualified `sampledAt`, `quality="good"` and all ten `zone1Set/zone1Act` through `zone5Set/zone5Act` JSON numbers in °C. Set values are observed settings, not control commands. Zero is valid; missing/null/bool/string/nonfinite values, unknown/duplicate fields and snake_case substitutes fail with HTTP422. The prefix follows `API_V1_PREFIX`.

Temperature values use exact `NUMERIC(30,10)`: absolute value below 10^20, at most ten fractional decimal places. Fractional values must also round trip through JSON number serialization without changing the decimal value; larger precision is rejected, never rounded. This technical domain is not a physical temperature limit. Raw JSON decimals are parsed before float conversion. Equivalent 1/1.0 and 0/-0 values share a SHA256 fingerprint.

`sampledAt` is normalized to UTC and stored as `DATETIME(3)`; nonzero submillisecond digits and invalid timezone offsets are rejected. UTC years 1000 through 9999 are supported. Output is `YYYY-MM-DDTHH:mm:ss.sssZ`; database-created timestamps use `UTC_TIMESTAMP(3)` independently of source time. No engine/session timezone is changed.

HTTP200 returns `{recordId,equipmentId,sampleId,sampledAt,outcome}` inside the shared success envelope. First creation is `created`; a replay or equivalent existing observation is `duplicate`. One sample is unique by `(equipment_id,sampled_at)`, one delivery receipt by `(actor_user_id,equipment_id,sample_id)`. Keys are case-sensitive (`utf8mb4_bin`); identifiers are 1–128 characters without control characters or leading/trailing whitespace. Fingerprints exclude actor/sampleId/token/arrival time. Changed payload for the same delivery is HTTP409 `equipment.temperature_sample_id_conflict`; changed content for the same source instant is `equipment.temperature_sample_time_conflict`. Delivery conflicts take precedence. Samples are never overwritten; new equivalent deliveries add only a receipt.

The async Service owns one transaction for sample and receipt/actor audit, and commits before success. CRUD only queries/adds/flushes. Only MySQL1062 on the actual named sample/delivery constraint permits rollback and at most two retries in fresh transaction snapshots. Other integrity failures are not duplicates. Unavailable/unknown commit outcomes return503; retry with the same sampleId. A committed response/log failure returns a sanitized500 and the same-key retry restores the committed record. Receipts reference the sample and equipment together by composite FK; no user FK changes account deletion behavior.

`GET /api/v1/equipment/temperature-samples` uses optional `equipmentId` (the configured key by default), positive `recordId` and `limit` (100 default, 1–1000). SQL applies device scope before record ID, then `sampled_at DESC,id DESC` and the actual limit. It returns `{equipmentId,items}` with recordId, source time, quality, all ten values and database createdAt; no actor, receipt or sampleId is exposed. Missing IDs return an empty list. Different instants within one hour and late samples remain separate. `limit=1` identifies the latest accepted source time in the new table; it is not a physical-current guarantee.

## Permissions and configuration

POST requires existing active-user authentication, admin role and `equipment-temperature-ingest`. GET requires `equipment-temperature-read`; admin is invariantly permitted and supervisor/operator need explicit grants. Unknown roles fail. Neither permission grants the other or the old `equipment` APIs. Public role grants remain empty.

All callers, including admin, require one exact module-local `EQUIPMENT_TEMPERATURE_PILOT_ID`. Empty/invalid scope denies both new APIs with403, while old GETs keep their behavior. Public examples use an empty value; synthetic documentation/tests use `temperature-pilot-01`. The local `BaseSettings` dependency lazily uses public `settings.resolve_env_file()`: source backend/.env, packaged executable-directory .env, and existing Docker /app/.env. Explicit configuration overrides process environment, which overrides dotenv; tests use `_env_file=None` or a synthetic file. Each application lazily freezes its own first configuration instance; no cross-application cache exists. Later dotenv/process changes require restart to be adopted. `manifest.enabled=False` removes old and new equipment routers after recomposition/restart.

Only the new two routes use local HTTP401/403/409/422/500/503 adaptation and stable `equipment.temperature_*` errors. DEBUG responses omit SQL, secrets and input contents. Existing global business-error HTTP200 and old APIs remain unchanged. JSON Lines events carry controlled actor/object/outcome fields, never full sample payloads or credentials.

## Persistence and adoption gates

Explicit successor [e4f6a8b0c2d4](../../alembic/versions/20261016_1600_e4f6a8b0c2d4_add_equipment_temperature_samples.py) follows d2f4a6b8c0e2 and adds only `equipment_temperature_samples` and `equipment_temperature_sample_receipts` (complete fixture 60 tables; the old 58 remain protected). Imports, GETs and startup do not run DDL/seed. Downgrade removes receipts then samples and loses new observations; it is only a separately approved disposable rehearsal, not the default adopted-data rollback.

The old `GET /equipment/temperature-control` still reads `equipment_temperature`, including its existing limit behavior. Existing frontend pages keep that old data source and do not display new HTTP observations automatically. There is no union, dual-write, old-row migration, writer shutdown or PLC provenance fabrication. Frontend/writer unification, retention, aggregation and field adoption need separate tasks.

A source/no-DB checks and offline DDL do not prove MySQL persistence, constraints, precision or concurrency. The independent [MySQL entry](../../tests_mysql/test_equipment_temperature.py) runs only after explicit disposable target/actions approval, outside shared destructive conftest. Database (including SQLite), Docker, deployment and real-device actions remain separate gates. See the root [task spec](../../../plans/ARCH-BE-003-mapping-service-api-pilot/spec.md), [Development](../../../plans/ARCH-BE-003-mapping-service-api-pilot/tasks.md), and local [plan](PLAN.md).


## HTTP dashboard sources

New POST/GET `/equipment/drive-samples` and `/equipment/production-parameter-samples` use the HTTP domain above.
Drive accepts at least one of twenty measurements; production parameters require exact coilNo and at least one
of grade/entryTime/thickness/width/totalTime/weight/speed. processSteps is never writable. Same equipment/business
key/source millisecond only fills existing NULL measurements; conflicting populated values return 409 atomically.
GET requires equipmentId, optional positive recordId and limit 1–1000 (default 100), returning items and a dashboard
from the same selected source row. Missing metrics never produce a zero deviation or normal status.

GET `/equipment/temperature-sample-dashboard` reads only BE003 complete samples and retains its temperature
read/scope rules; original temperature POST/GET remain unchanged. Dashboard histories retain recordId and full
source time. The three equipment pages keep `dataSource=legacy|http` and `equipmentId` in the URL. Default legacy
reads the old tables; external reporting requires a business equipment key and never falls back to legacy/mock.
Switching sources clears the old data and ignores late responses. Legacy rows cannot be filtered by guessed PLC
identity. TV/KM units remain unspecified; set values are observations, never control commands.
