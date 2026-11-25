# Energy registered batch ingest v1

[中文](README.zh-CN.md) · [OpenAPI](openapi.json) · [Synthetic request and response](examples/batch.json) · [Approved specification](../../../../plans/ARCH-OBS-010-energy-registered-batch-ingest/spec.md)

## Register a sender

An administrator uses **Energy Management → Configuration → Write registration**, or the user Bearer API below. The source key is case-sensitive and accepts 1–64 ASCII letters, digits, dots, underscores or hyphens. The name is optional and accepts up to 128 characters. New sources are enabled by default. The key cannot be edited or reused after deletion. Use the same two-level path encoding as [equipment registration](../observation-write-sources-v1/README.md#administration): the literal keys `.` and `..` become `%252E` and `%252E%252E`.

| Method | Path relative to `/api/v1` | Body |
| --- | --- | --- |
| GET | `/energy/write-sources` | Lists active and disabled registrations |
| POST | `/energy/write-sources` | `sourceKey`, optional `name` and `enabled` |
| PATCH | `/energy/write-sources/{sourceKey}` | `name` and/or `enabled` |
| DELETE | `/energy/write-sources/{sourceKey}` | Retires the key and preserves existing samples and receipts |

Administrators separately configure meter metrics. Existing meter configuration and role-based meter reads continue to apply. No producer token or per-source meter assignment is required. The existing [Bearer v2 API](../equipment-observation-v2/README.md) retains its separate producer permissions.

## Send a batch

Use `POST /api/v1/integration/energy/registered-samples` on the approved internal network with `Content-Type: application/json`. The service does not use the `Authorization` header. The request has a 65,536-byte UTF-8 JSON limit.

- Send one batch per enabled source and actual capture time. Include `sourceKey`, `target: "energy"`, `observedAt` and `items`. Inside `items`, use meter keys, then group keys, then a nonempty `values` map of enabled configured metric keys and finite numbers. Zero is valid.
- Supply actual offset timestamps with no nonzero digits beyond microseconds. A group containing any interval metric needs both `intervalStartAt` and `intervalEndAt`, in increasing order. Groups with only cumulative and instantaneous metrics omit them. Omit `quality` or send null for `unknown`. Explicit options are `good`, `bad` and `unknown`.
- A successful response contains one string `receiptId` and one string `recordId` per meter/group, ordered by UTF-8 meter and group keys. The whole batch commits in one transaction. Dates are returned in Shanghai time with six fractional digits.

Keep the original batch for retry. Equivalent numeric representations, offset timestamps, object order and default quality produce the same receipt and ordered records. A different body at the same source and capture time returns HTTP 409 `equipment_observation.event_conflict`. HTTP 403 `equipment_observation.source_not_enabled` covers unknown, disabled and deleted sources, including retries. HTTP 422 reports invalid fields or meter configuration, 413 reports size, and 415 reports the wrong media type. Retry HTTP 503 with the original batch, including `equipment_observation.commit_unknown`.

## Storage and compatibility

The dedicated `energy_write_sources` table keeps retired keys and an internal identity separate from legacy producers. Each new batch occupies one `energy_ingest_receipts` row. Its ordered records are saved in `result_detail`; the existing `energy_consumption_main` rows all reference that receipt. The application continues to verify the configured MySQL server and schema identity. Routine operation follows the energy tables and does not depend on the global Alembic revision. No task or equipment/process records are required.

Revision `b52e9c416a07` follows `a1c307f8d2e4` and requires explicit matching `ENERGY_WRITE_EXPECTED_SCHEMA` and `ENERGY_WRITE_EXPECTED_SERVER_UUID`. Keep the registration, samples and receipts when reverting application code. The migration refuses downgrade to protect stored facts. Actual target migration and service switch require separate authorization.

[Routes](../../../../backend/app/equipment_observation/api/routes.py) · [Batch transaction](../../../../backend/app/equipment_observation/services/energy_registered_ingest.py) · [Migration](../../../../backend/alembic/versions/20261124_2300_b52e9c416a07_energy_write_sources.py)
