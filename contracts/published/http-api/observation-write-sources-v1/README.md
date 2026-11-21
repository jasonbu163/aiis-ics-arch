# Registered observation writes and latest values

[中文](README.zh-CN.md) · [OpenAPI](openapi.json) · [Synthetic vectors](vectors.json) · [User guide](../../../../docs/equipment-status-process-monitoring-guide.md#registered-write-sources)

Configure the database target and private observation profile before using these endpoints. The profile must identify the MySQL 8.4 server, schema and revision `e9f3b5d7c021`. Use `OBSERVATION_ENABLED=true` and an external `OBSERVATION_PROFILE_FILE`. A registered source needs no profile device or producer. The profile's `devices` and `producers` arrays can be empty. The [v2 machine contract](../equipment-observation-v2/README.md) retains its Bearer token, scope checks and original receipt semantics.

`sourceKey` is a case-sensitive name, 1–64 ASCII letters, digits, underscores, periods or hyphens. Use a stable key for each sender. The key can be copied and does not establish identity. Deploy the token-free endpoints within an access-controlled network.

## Administration

User JWT and admin role are required. `GET /api/v1/equipment/write-sources` returns non-deleted registrations. POST accepts `sourceKey`, optional name (1–128 characters or null), and `enabled` (defaults to true). PATCH on `/api/v1/equipment/write-sources/{sourceKey}` accepts at least one of `name` or `enabled`. The key is immutable. DELETE on the same path stops writes, hides the source, retains samples and receipts, and permanently reserves the key. Disabling is reversible. Duplicate or conflicting keys return 409, missing or deleted keys return 404 for PATCH/DELETE, and invalid input returns 422. For the literal keys `.` and `..`, use the path segments `%252E` and `%252E%252E` in browser clients to survive URL normalization.

Equipment and process readers can view all non-deleted registered sources, regardless of write status. Older devices keep their configured read scopes. Administrators can find deleted-source records under Data Management.

## Third-party API

`POST /api/v1/integration/observations` accepts up to 65,536 bytes of UTF-8 JSON. Send exactly `sourceKey`, `target` (`latest` or `history`), `taskNo`, `observedAt` and `items`. The service trims and uppercases ASCII task numbers and converts offset-bearing observation time to +08:00 with six fractional digits. Provide at least one metric. Each submitted region and each metric's slot for the selected target must be enabled. Types are checked against metric configuration. Zero, false and the empty string are values. Null is invalid. The server records quality as `unknown`.

Latest replaces the complete snapshot for that source and task when the observation is more recent. An older unseen sample gets a `stale` receipt with the current snapshot ID. History appends each accepted sample. Time more than 30 seconds ahead of the verified database clock is rejected. Cards mark existing values older than 60 seconds stale. Charts render saved historical values and show gaps for absent metrics.

An identical source, target, normalized task, normalized time and canonical content replays the original receipt while the source is enabled, even if a slot was later disabled. Different content for that identity returns 409. Use the original body and sampling time to retry a 503, including `equipment_observation.commit_unknown`. An unregistered, disabled or deleted source returns 403 `equipment_observation.source_not_enabled` on write. Other errors include 413 for excess bytes, 415 for unsupported media, 422 for invalid fields or configuration, and 503 for an unavailable or invalid target.

`GET /api/v1/integration/observations/latest?sourceKey=sma-demo-1&target=history&taskNo=000042` returns only the saved metrics of a single row. Omit `taskNo` to choose by observation time descending, task ascending, then record ID descending. An existing source with no matching row returns `data: null`. Disabled sources remain readable. Unknown and deleted sources return 404. Responses use the project's success envelope and omit internal storage and receipt identities from the GET result.
