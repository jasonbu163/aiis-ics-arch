# Equipment observation ingest API v1

[中文](README.zh-CN.md) · [OpenAPI](openapi.json) · [Synthetic vectors](vectors.json) · [r8 specification](../../../../plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md#r8-dev-integration)

The SMA and external writers use the same machine Bearer authentication and three routes. The private server profile binds writer kind and grants for device, group, target and metric keys; a request body never grants authority. This is a source contract, not evidence of field SMA/DAA integration or production deployment.

| Method and route | Purpose |
| --- | --- |
| `GET /api/v1/integration/metric-definitions?equipmentId=line-01&groupKey=temperature&target=latest` | Discover enabled, granted keys, types and optional units. `history` also intersects the history whitelist. All three query parameters are required. Stored values and internal slots are not returned. |
| `POST /api/v1/integration/equipment/latest-snapshots` | Replace the device/task/group snapshot; an older sample returns `stale`. |
| `POST /api/v1/integration/monitor/history-samples` | Append an eligible sample, deduplicated by source. |

Both POSTs accept `application/json` of at most 65536 bytes. `values` uses the case-sensitive registered metric keys and original JSON number, string or Boolean type. Omit a missing item; `null` values are invalid, while `0`, `false` and string leading zeroes are preserved. Titles and units come from configuration. Timestamps include an offset and are converted once to Shanghai time. Stored task-point evidence must prove `taskNo` for the sampled time; it is not inferred from the current UI selection.

| Field | External | SMA |
| --- | --- | --- |
| `sourceRefs` | One `external_event` with a stable `sourceEventId`; the bound `sourceId` can be omitted. | `plc_fact` references to one stored v2 sample, including the bound task point and mapped points. |
| `data.taskNo`, `data.sampledAt`, `data.values` | Required every request. | Required every request. |
| `data.equipmentId`, `data.groupKey` | Omit only when the identity is fixed to one device/group. | Required every request. |
| `data.quality` | Latest may omit or use `null` (`unknown`); history explicitly requires `good`. | Required; history requires `good`. |
| `contractVersion`, `producerId`, `mappingId`, `mappingRevision` | May be omitted and filled from the profile; omit or provide the mapping pair together. | Required every request; fixed values can be configured once in the sender. |
| `eventId` | May be omitted and deterministically generated from source and target. | Required and stable per target and retry. |

Omission is not equivalent to `null`, except for external latest quality. Retry each target with its original event and identical content; a duplicate returns its original receipt, while changed content for the same event returns `409`. The same historical source with another valid event can return `already_stored`. Retain and retry the original event after `503` because commit outcome may be unknown. The sender selects historical samples by original sample time; display configuration is independent. The receipt persists the verified task evidence. Source quality is separate from an administrator review mark.

Typical status codes are `401` unauthenticated, `403` disabled/out of scope, `409` event/sample/task-evidence conflict, `413` oversized, `415` wrong media type, `422` invalid input/type/quality or metric, and `503` unavailable or unknown commit result. Domain errors have `errorCode`; framework validation may use the standard FastAPI 422 shape. See the [approved specification](../../../../plans/ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md#5-sma-指标发现和写入接口) for the complete conditions.

[vectors.json](vectors.json) includes two distinct synthetic v2 samples, discovery, the external minimum requests, the full synthetic SMA envelope for both targets, and illustrative receipts. Each writer uses one common source for its own two targets. Fixed times and record IDs are illustrative: generate fresh identities and timestamps inside the task evidence window when rerunning. `walkthrough.py` is a loopback-only synthetic client; it requires an already provisioned isolated database, authenticated user, private profiles and separate machine credentials.

The script uses fixed synthetic PLC, device, task and metric identifiers. Run it only against a confirmed dedicated disposable fixture, **never an existing dev database**; the acknowledgement does not verify database identity. First register `plc-01/daa-fixture/generation-1` in acquisition sources and configure a dedicated OBS profile and accounts. Set `OBS_DEMO_ADMIN_USER`, `OBS_DEMO_ADMIN_PASS`, `OBS_DEMO_EXTERNAL_TOKEN` and `OBS_DEMO_SMA_TOKEN`, then run `python walkthrough.py --base-url http://127.0.0.1:18395 --fixture-ack DISPOSABLE-OBS-FIXTURE`. It writes data and does not automatically clean it. Keep real credentials out of the repository. Configure positive per-device/group `staleAfterSeconds` independently of task-point age, and the separate historical whitelist and interval.

[Example private profile shape](example-profile.json) uses fake hashes and a non-runnable UUID: replace them with independent secret-token SHA-256 digests and the verified target; put the resulting file outside the repository. PLC facts v2 uses a separate target-only profile and the current source registry.

The current acquisition development GET/POST follows its own contract and does not use the observation Bearer or legacy `readScopes`. The observation machine routes retain their separate grants. Product execution and field integration remain governed by their respective tasks and the current acquisition contract.
