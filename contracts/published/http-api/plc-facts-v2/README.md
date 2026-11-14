# PLC facts v2 source contract

[简体中文](README.zh-CN.md)

`POST /api/v1/integration/plc-facts/samples` accepts raw PLC data from DAA, third-party producers and backup collectors. A synthetic sample can exercise backend ingestion, deduplication, latest values and history independently of a collector.

The sample POST and all five GETs require no Bearer credential in the current development stage. Each POST submits one complete DB sample from one instance and PLC, with 1–512 points and up to 524288 bytes of UTF-8 `application/json`. Submit each DB separately and track its receipt separately when a collection round covers multiple DBs. [Development OpenAPI](openapi-acquisition-dev-r4.json) · [Request schema](schema-acquisition-r2.json) · [DAA request and receipt vectors](vectors-acquisition-r2.json)

## Source registration

The backend matches only `plcId`, `instanceId` and `sourceGeneration` against the current `plc_source_registry` row. Each PLC has those three identifiers and a display-only `sourceType`; DB is supplied with the sample and is not part of registration. Web copies the three identifiers from the saved row. Committed registration changes take effect immediately. Management requires admin login; sample POST and GET retain the development no-Bearer contract. A takeover needs a new generation for that PLC and reconciliation of the old queue. The backend labels history using `sourceType` from that PLC's registration row; the label is not used for admission or sample validation. A request containing `sourceType` returns `422`. [Management API](openapi-acquisition-sources-r4.json) · [Source registration](../../../../backend/app/plc_facts/README.md)

An administrator may confirm deletion of a source. Later uploads using it, including retries, return `403`; existing unexpired history remains readable. Deletion also removes the row's retired-generation list. If corresponding facts and latest values no longer exist, an old generation may not be detectable. Register the PLC again with a never-used generation and retain frozen samples with their original identity.

## Request fields and purpose

### Sample fields

| Field | Requirement | Purpose |
| --- | --- | --- |
| `contractVersion` | Required. Use `plc-facts/v2`. | Declares the body protocol the backend validates. |
| `instanceId` | Required. Use the registered producer instance ID. | Identifies the producer, matches registration with the PLC ID and generation, and scopes sample ID deduplication. |
| `sampleId` | Required and unique within the instance. Reuse it on retries. | Identifies the DB sample for deduplication and matching receipts. |
| `plcId` | Required. Use the registered PLC ID. | Identifies the device for source admission, latest values and history. |
| `dbNumber` | Required. Use a JSON integer from 1 to 65535. | Identifies the DB as the unit of submission and confirmation. |
| `sourceGeneration` | Required. Use the active generation registered for the PLC. | Distinguishes sampling streams across a source takeover or resequencing and lets the backend reject an older generation after a switch. |
| `sourceSeq` | Required. Use a decimal string without leading zeros in the range 1–9223372036854775806. | Advances in sampling order within the same instance, PLC, DB and generation. An older sequence can fill history. A higher sequence wins for an existing latest point. The string preserves integer precision. |
| `points` | Required. Include the complete set of reported points for this DB under the sampling configuration. | Submits the values and quality from one collection together so history can return the complete sample. |
| `groupId` | All senders may omit it, send `null` or supply a valid identifier. | Records the group that collected the sample. |
| `configRevision` | All senders may omit it, send `null` or supply a valid identifier. | Records the configuration revision in effect at collection for later lookup of the point map. |

Identifiers match by exact bytes and use 1–128 UTF-8 bytes. They start and end with a non-whitespace character and exclude ASCII control characters. An empty string for `groupId` or `configRevision` returns `422`.

### Point fields

| Field | Requirement | Purpose |
| --- | --- | --- |
| `pointId` | Required. Use a stable identifier unique within the sample. | Locates the point within a PLC and DB for exact latest-value reads. |
| `dataType` | Required. Examples include `INT`, `BOOL` and `REAL`. | Declares the PLC value type for JSON type and range validation. |
| `value` | Required. Send a matching raw value for `good` and `null` for `bad`. | Carries the raw observation. Use a JSON number for `INT` and a JSON boolean for `BOOL`. |
| `quality` | Required. Use `good` or `bad`. | Tells readers whether the value is valid so they can distinguish real zero or `false` from a failed read. |
| `observedAt` | Required. Separate date and time with `T`, include `+08:00` and use up to microsecond precision. | Records the original observation time for history and retention. Backfill retains this time. |
| `name` | Optional. Up to 100 UTF-8 bytes. | Supplies a point name for display. |
| `reason` | Required and nonempty for `bad`, up to 128 UTF-8 bytes. Omit it or send `null` for `good`. | Describes a failed or missing observation, such as `missing`. |

## Commit and retry

The complete sample is stored in `plc_facts_history` and the latest point values in `plc_facts_latest`. Both commit in one transaction before HTTP `200` with `data.status=committed`. The first commit returns `data.outcome=created`. Within the effective retention window, if `plcId`, `instanceId` and `sourceGeneration` still match the current PLC registration, retrying the same instance and sample ID with the same body bytes returns `duplicate` and keeps a single history record. After a takeover, a retry using the old identity can return `403 plc_facts_v2.scope_rejected` even when the body is unchanged.

Retain the sample ID, sequence, original observation time and the exact UTF-8 body sent. After a timeout, lost receipt or `503 plc_facts_v2.commit_outcome_unknown`, keep the sample pending and resend the original bytes. On receipt of `committed`, check that `contractVersion`, `instanceId` and `sampleId` match before recording confirmation.

Reordering keys, changing whitespace or replacing an omission with `null` changes the body. Use the HTTP status and `errorCode` to interpret failures.

| HTTP | `errorCode` | Meaning |
| --- | --- | --- |
| `403` | `plc_facts_v2.scope_rejected` | The upload source does not match registration or the explicitly queried realtime PLC is not registered. |
| `404` | `plc_facts_v2.not_found` | The history detail is missing or expired. |
| `409` | `plc_facts_v2.sample_content_conflict` | With current admission and an unexpired sample, the body changed for the same identity or another sample uses the sequence within the stream. |
| `410` | `plc_facts_v2.expired_unconfirmed` | The sample reached its effective cutoff. |
| `413` | `plc_facts_v2.payload_too_large` | The request body exceeds the byte limit. |
| `415` | `plc_facts_v2.media_type` | The media type, character set or content encoding is invalid. |
| `422` | `plc_facts_v2.invalid_request` | The body or query is invalid. Examples include a missing required field, more than 512 points or an observation more than five minutes ahead of backend time. |
| `503` | `plc_facts_v2.not_ready` or `plc_facts_v2.commit_outcome_unknown` | The service or target is unavailable, or the commit result is uncertain. |

## Read operations

The paths below start with `/api/v1/acquisition-data`. Realtime reads use the current source registration. History reads all unexpired facts independently of registration, including PLCs with no current registration. The development GETs require no Bearer, so those facts are also visible through the API. Consumers such as SMA, CA and FF can use these GETs to read raw values.

| Operation | Parameters and result |
| --- | --- |
| `GET /options` | Returns registered PLCs and their valid history/current latest DB numbers; use `?view=history` for all unexpired history PLC/DB options. |
| `GET /latest` | Requires `plcId` and `dbNumber`. Omit `pointId` for all valid latest points in the DB or supply an exact ID for at most one item in `data.items`. |
| `GET /latest/browse` | Supports optional `plcId`, `dbNumber` and `pointSearch`. Paginates within the read scope. |
| `GET /history` | Requires `from` and `to`. `plcId` and `dbNumber` are optional. Queries sample summaries by sample time and returns the history `id` in each `data.items` entry. |
| `GET /history/{id}` | Takes a decimal string `id` and returns the complete sample with its points in `data.points`. |

Paginated reads default to 50 items with a maximum of 100 per page. History uses the Shanghai interval `[from, to)` with a maximum span of seven days. Historical `sourceType`, `groupId` and `configRevision` may be `null`. Each raw value stays readable until three calendar months after observation minus 24 hours. The complete sample uses the earliest point cutoff. REAL uses validated decimal numeric text inside the database JSON fields. Reads restore a JSON number, retaining input precision, negative zero and scientific notation. [Maintenance CLI](../../../../backend/scripts/plc_facts_maintenance/README.md)

## Manual test in Swagger

1. Open `/docs` on the development backend and expand `plc-facts-v2`. Use a registered synthetic `external` source; after the first sample, verify its PLC and DB with `GET /api/v1/acquisition-data/options`. The example matches the synthetic source in the backend documentation. When using an existing development source, replace the three identifiers with the registered values and use the DB number being sampled. [Local Swagger](http://127.0.0.1:8000/docs) · [Synthetic source configuration](../../../../backend/app/plc_facts/README.md#v2-sample-endpoint)
2. Open `POST /api/v1/integration/plc-facts/samples`, select `Try it out`, paste the minimal request below and select `Execute`. For a new synthetic sample, give it a new `sampleId`, the next unused increasing `sourceSeq` in that stream and the current Shanghai time for `observedAt`. The example sequence `"1"` suits a new synthetic stream. Expect HTTP `200` and the `created` receipt below.
3. While the three identifiers still match the current registration and the sample remains valid, select `Execute` again with the same body. Expect HTTP `200`, `committed` and an `outcome` of `duplicate`. To check conflict handling under the same conditions, change `value` to `43` with the original ID and sequence and expect `409`.
4. Call `GET /api/v1/acquisition-data/latest` with the submitted `plcId`, `dbNumber` and `pointId=demo_counter`. Check `value=42`, `quality=good`, the sample ID and `sourceType=external` in `data.items[0]`.
5. Call `GET /api/v1/acquisition-data/history` with the same PLC and DB and a `from` and `to` that include `observedAt`. For the example timestamp, use `2026-11-11T16:59:00+08:00` to `2026-11-11T17:01:00+08:00`. Find the single summary with the submitted `sampleId`, pass its `id` to `GET /api/v1/acquisition-data/history/{id}`, and check the original value in `data.points` and `null` for `groupId` and `configRevision`.

The minimal external request below has one good point. A sender registered as `daa` uses the same rules and may omit or supply the original `groupId` and `configRevision`. [Complete DAA example](vectors-acquisition-r2.json)

```json
{
  "contractVersion": "plc-facts/v2",
  "instanceId": "external-a",
  "sampleId": "swagger-external-001",
  "plcId": "PLC-A",
  "dbNumber": 21,
  "sourceGeneration": "gen-a",
  "sourceSeq": "1",
  "points": [
    {
      "pointId": "demo_counter",
      "dataType": "INT",
      "value": 42,
      "quality": "good",
      "observedAt": "2026-11-11T17:00:00+08:00"
    }
  ]
}
```

The first successful commit returns this receipt.

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "contractVersion": "plc-facts/v2",
    "instanceId": "external-a",
    "sampleId": "swagger-external-001",
    "status": "committed",
    "outcome": "created"
  }
}
```

## Contract artifacts and source

The module registry declares internal names under `plc_facts.v2.*`. HTTP `errorCode` values use `plc_facts_v2.*`. [HTTP routes](../../../../backend/app/plc_facts/api/v2.py) · [Request and response models](../../../../backend/app/plc_facts/schemas/v2.py) · [Raw-value validation](../../../../backend/app/plc_facts/v2_domain.py)

Historical machine contracts preserve the earlier baselines. [Original OpenAPI](openapi.json) · [Original request schema](schema.json) · [Original vectors](vectors.json) · [r2 OpenAPI](openapi-acquisition-r2.json) · [ARCH-BE-012 r4 development](../../../../plans/ARCH-BE-012-simplified-plc-facts/tasks.md) · [ARCH-ACQ-003 r2 acceptance](../../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/checklist.md#human-owner-最终验收)
