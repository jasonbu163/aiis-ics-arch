Contract ID: automation-world-facts-integration
Version: demand-r1
Status: proposed
Consumer: DAA, SMA and other selected HTTP consumers
Provider: Backend facts owner and individual business modules
Owner Task: ARCH-AW-008 r1

# AW anonymous facts integration and reliable business delivery demand

[中文](automation-world-facts-integration.zh-CN.md)

## 1. Authority, current baseline and responsibilities

This demand implements the approved document scope of [ARCH-AW-008 r1](../../plans/ARCH-AW-008-stage-c-facts-contract/spec.md). `proposed` describes a consumer demand, not a Backend provider commitment, implementation or verification. A separately approved Backend specification must freeze the executable schema, parameters and algorithms, aligning its published contract with Pydantic/OpenAPI and Model/Alembic. This Markdown is not an executable schema and authorizes no software, database, device or live integration operation.

[DAA Stage B](../../automation-world/data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) is accepted within the controlled DS scope. DAA currently persists locally; fact upload is not connected. Backend has [raw/latest models](../../backend/app/monitor/models/monitor.py) and an [authenticated latest GET](../../backend/app/monitor/api/realtime.py), which do not establish the new receiver or safe cursor. The old CA direct writer is a frozen compatibility reference. SMA keeps its TSS-derived, Backend-held configuration baseline; this demand does not require immediate SQLite migration.

```text
DS/PLC -> DAA complete local commit -> anonymous facts API -> raw/latest
                                                            |
                                                   safe history/latest
                                                            |
                                                           SMA -> module typed ingest -> business commit
                                                                                              |
                                                                                 authenticated frontend reads
```

DAA fact acknowledgement and SMA business acknowledgement are separate durable boundaries. A fact ACK does not prove business persistence. Each module API/Service owns business validation and transactions; SMA accesses neither PLC nor business SQL.

<a id="routes"></a>
## 2. Candidate routes and anonymous boundary

| Method / candidate path | Purpose | Current-stage access requirement |
| --- | --- | --- |
| POST /api/v1/integration/plc-facts/batches | Bounded DAA batches containing multiple PLC/DB samples | No login, JWT, API key or role authorization |
| GET /api/v1/integration/plc-facts/latest | Current results and derived point directory | Same |
| GET /api/v1/integration/plc-facts/history | Time-range or continuous incremental history | Same |
| POST /api/v1/integration/{module}/{resource} | Future module-owned typed business ingestion pattern | Anonymous integration target; each module separately approved |
| Existing frontend display, management and business routes | Existing uses | Preserve their authentication, permission groups, data scope and business contracts |

All paths are candidates, not callable implemented endpoints. Authentication is a route property; User-Agent, a self-claimed DAA/SMA identity or a frontend origin must not bypass an existing guard. Do not add an implicit allowlist, token or identity platform as a prerequisite. Anonymous input still undergoes version, required-field, type, size, time, idempotency, order and retention checks. It is not a table-name/arbitrary-column SQL writer; maintenance, accounts, DDL and device control are excluded.

instanceId, producerId, plcId and sourceGeneration are client declarations, not authenticated identity or device ownership. A reachable client can impersonate a declaration: this is the explicit current-stage tradeoff. Source eligibility and handover are protocol/configuration constraints, not an authentication guarantee. The existing [temperature POST](../../backend/app/equipment/api/temperature_samples.py), its full schema and [actor-scoped idempotency](../../backend/app/equipment/services/async_temperature_sample.py) require a separate module adaptation; never invent an admin/user actor to reuse them.

<a id="identity"></a>
## 3. Identity, types and lossless local-v2 compatibility

| Object | Stable meaning and rule |
| --- | --- |
| pointId | Binding and point-result identity; name, IP and DB name are not keys; movement between groups preserves identity |
| sampleId | DB-package/fixed-part identity fixed at first persistence; same identity/content is a duplicate, different content is a conflict |
| cycleId / manifest | A group acquisition and its expected packages/parts; the members present in one HTTP request do not prove cycle completeness |
| batchId | Identity and fixed coverage of a frozen delivery; retry preserves members and content |
| sourceGeneration + sourceSeq | Durable order within one effective generation of one PLC; examples use decimal strings without precision loss; never compare across PLCs |
| configRevision / definition signature | Interpretation at observation time; opaque strings do not establish order and rollback does not rewrite history |

Preserve points dictionary keys byte-for-byte. The current [common serializer](../../backend/common/response.py) recursively converts keys, so the future adapter must distinguish field names from data identities. Managed points retain existing ASCII technical naming and sourcePath retains original paths/Chinese text. Unconverted legacy names and historical definitions travel losslessly; do not rename them for upload or execute names as Rust identifiers, SQL identifiers or scripts.

Values retain JSON number/boolean types. Bad-quality results retain definition, original time, missing value and reason; do not replace them with zero/old success or omit expected failures. The provider must freeze the PLC-to-JSON type, range, non-finite float, integer precision and null matrix. The concise definition in these examples is not the entire current Point structure and permits no loss of other original definition fields.

The [local v2 types](../../automation-world/data-acquisition-agent/src-tauri/src/domain/local_sample.rs) and [persistence writer](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs) map as follows. A transport projection may have its own version; stored payload/manifest/context bytes remain unchanged.

| Local-v2 field / evidence | Transport responsibility |
| --- | --- |
| schemaVersion=2, sampleId, cycleId, instanceId, plcId | Preserve source identity; outer contractVersion is not a database schemaVersion |
| sourceGeneration, sourceSeq, groupId, revision, dbNumber | Preserve order and interpretation; examples call revision configRevision, with final aliases frozen by the provider |
| points[pointId].definition/value/observedAt/quality/reason | Interpret losslessly; name is not identity and failures/original times must survive |
| startedAt, finishedAt, savedAt, origin and source configuration context | Preserve distinct read, local-save and origin semantics; omission from a concise example is not permission to discard them; final schema states carriage or verifiable association |
| CycleManifest.expectedPointIds/samples/reads | Preserve expected points, DB samples and read timings; HTTP splitting does not redefine expected membership |
| ManifestSample.sha256 and original sample sha256 | SHA-256 of original UTF-8 bytes; illustrative sourceSha256 is an original-byte association, not a transport digest |

There are three digest responsibilities: original payload/manifest/context byte SHA-256; versioned transport contentDigest; frozen requestDigest. Reformatting/parsing/reserializing JSON does not preserve original bytes. Before coding, the provider freezes algorithms, included/excluded fields, character encoding, ordering, time/number normalization and test vectors, including exclusion of self-referential request-digest fields. Original-text delivery must preserve verifiable bytes; projected delivery must distinguish projection identity/digest from original evidence.

<a id="request"></a>
## 4. Requests, cycles, fragments and failure examples

Every JSON block below is a syntactically valid **semantic placeholder**, not an implemented callable schema or a promise to pass a future validator. IDs, digests, field and part encodings are illustrative and never generate or rewrite local history. The main batch contains three packages: A DB71/DB88 share fast cycle142; B DB71 belongs to independent slow cycle27. Equal DB numbers do not collide. A's failed ready result is still an expected member, so complete reception and good acquisition quality are distinct.

```json
{
  "contractVersion": "plc-facts/v1",
  "batchId": "batch-demo-1",
  "instanceId": "daa-demo",
  "requestDigest": "illustrative-frozen-request-digest",
  "cycles": [
    {
      "plcId": "plc-a",
      "cycleId": "cycle-a-142",
      "sourceGeneration": "generation-a",
      "sourceSeq": "142",
      "groupId": "group-fast",
      "expectedPointIds": [
        "point-a-temperature",
        "point-a-ready",
        "point-a-value"
      ],
      "manifest": [
        {
          "sampleId": "sample-a71",
          "dbNumber": 71,
          "part": 1,
          "parts": 1,
          "contentDigest": "illustrative-transfer-sample-a71"
        },
        {
          "sampleId": "sample-a88",
          "dbNumber": 88,
          "part": 1,
          "parts": 1,
          "contentDigest": "illustrative-transfer-sample-a88"
        }
      ]
    },
    {
      "plcId": "plc-b",
      "cycleId": "cycle-b-27",
      "sourceGeneration": "generation-b",
      "sourceSeq": "27",
      "groupId": "group-slow",
      "expectedPointIds": [
        "point-b-count"
      ],
      "manifest": [
        {
          "sampleId": "sample-b71",
          "dbNumber": 71,
          "part": 1,
          "parts": 1,
          "contentDigest": "illustrative-transfer-sample-b71"
        }
      ]
    }
  ],
  "samples": [
    {
      "sampleId": "sample-a71",
      "cycleId": "cycle-a-142",
      "plcId": "plc-a",
      "sourceGeneration": "generation-a",
      "sourceSeq": "142",
      "groupId": "group-fast",
      "configRevision": "config-a3",
      "dbNumber": 71,
      "sourceSha256": "illustrative-original-sample-a71",
      "points": {
        "point-a-temperature": {
          "definition": {
            "name": "DB71_temperature_Int",
            "sourcePath": "temperature",
            "address": {
              "offset": 2,
              "bit": null
            },
            "dataType": "INT"
          },
          "value": 202,
          "quality": "good",
          "reason": null,
          "observedAt": "2026-11-04T10:00:00.123+08:00"
        },
        "point-a-ready": {
          "definition": {
            "name": "DB71_ready_Bool",
            "sourcePath": "ready",
            "address": {
              "offset": 0,
              "bit": 0
            },
            "dataType": "BOOL"
          },
          "value": null,
          "quality": "bad",
          "reason": "read_timeout",
          "observedAt": "2026-11-04T10:00:00.123+08:00"
        }
      }
    },
    {
      "sampleId": "sample-a88",
      "cycleId": "cycle-a-142",
      "plcId": "plc-a",
      "sourceGeneration": "generation-a",
      "sourceSeq": "142",
      "groupId": "group-fast",
      "configRevision": "config-a3",
      "dbNumber": 88,
      "sourceSha256": "illustrative-original-sample-a88",
      "points": {
        "point-a-value": {
          "definition": {
            "name": "DB88_unit_value_Real",
            "sourcePath": "unit.value",
            "address": {
              "offset": 2,
              "bit": null
            },
            "dataType": "REAL"
          },
          "value": 12.5,
          "quality": "good",
          "reason": null,
          "observedAt": "2026-11-04T10:00:00.123+08:00"
        }
      }
    },
    {
      "sampleId": "sample-b71",
      "cycleId": "cycle-b-27",
      "plcId": "plc-b",
      "sourceGeneration": "generation-b",
      "sourceSeq": "27",
      "groupId": "group-slow",
      "configRevision": "config-b3",
      "dbNumber": 71,
      "sourceSha256": "illustrative-original-sample-b71",
      "points": {
        "point-b-count": {
          "definition": {
            "name": "DB71_count_Int",
            "sourcePath": "count",
            "address": {
              "offset": 2,
              "bit": null
            },
            "dataType": "INT"
          },
          "value": 101,
          "quality": "good",
          "reason": null,
          "observedAt": "2026-11-04T10:00:00.123+08:00"
        }
      }
    }
  ]
}
```

Another slow group of PLC A may acquire point-a-pressure in DB71 as cycle143. That independent cycle/sequence updates only its own point; latest combines it with fast-group points instead of replacing the whole DB or inventing a synchronized frame. Different PLC/DB reads retain their own observation times.

Current local v2 packages by DB; it does not establish fixed-fragment support. The following scenario is not a wire schema: freeze parts, identities, digests and expected point sets before splitting. Receipt of part1 can acknowledge that part only; the cycle is incomplete until part2 is durably verified.

```json
{
  "scenario": "fixed-fragments-not-a-wire-schema",
  "plcId": "plc-a",
  "cycleId": "cycle-a-144",
  "sourceSeq": "144",
  "manifest": [
    {
      "sampleId": "sample-a90-part1",
      "dbNumber": 90,
      "part": 1,
      "parts": 2,
      "pointIds": [
        "point-x"
      ],
      "contentDigest": "illustrative-part1"
    },
    {
      "sampleId": "sample-a90-part2",
      "dbNumber": 90,
      "part": 2,
      "parts": 2,
      "pointIds": [
        "point-y"
      ],
      "contentDigest": "illustrative-part2"
    }
  ],
  "receivedSampleIds": [
    "sample-a90-part1"
  ],
  "cycleComplete": false
}
```

Missing definitions or limits do not permit JSON truncation. A retry must not drop points or renumber parts under the same batchId. Logical DB packaging does not restrict HTTP to one package; the first-version uploader uses bounded batches and one in-flight request per instance, while Backend still needs concurrency safety.

<a id="receipts"></a>
## 5. Durable receipts, retry and mixed-batch matrix

First-version reception is bounded and batch-atomic: validate -> identity/content deduplicate -> insert/confirm raw -> atomically advance eligible latest -> reception/completeness/safe-publication records -> durable commit -> receipt. A cross-storage implementation must first specify an equivalent durable reception ledger; volatile enqueue is not committed reception.

A receipt binds contractVersion, batchId, requestDigest and every acknowledged sample/part contentDigest; distinguish created/duplicate from cycle completeness. Here B is an equal-content duplicate and A has bad quality with complete membership. ACK does not prove latest advanced or that every earlier cycle is complete.

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "contractVersion": "plc-facts/v1",
    "batchId": "batch-demo-1",
    "requestDigest": "illustrative-frozen-request-digest",
    "status": "committed",
    "results": [
      {
        "sampleId": "sample-a71",
        "contentDigest": "illustrative-transfer-sample-a71",
        "outcome": "created"
      },
      {
        "sampleId": "sample-a88",
        "contentDigest": "illustrative-transfer-sample-a88",
        "outcome": "created"
      },
      {
        "sampleId": "sample-b71",
        "contentDigest": "illustrative-transfer-sample-b71",
        "outcome": "duplicate"
      }
    ],
    "cycles": [
      {
        "cycleId": "cycle-a-142",
        "complete": true
      },
      {
        "cycleId": "cycle-b-27",
        "complete": true
      }
    ]
  }
}
```

DAA validates and monotonically persists member ACKs/batch outcomes in a short local transaction before showing uploaded. HTTP200/202, sent bytes, logs or merely durable queue acceptance do not prove complete fact/business commit. Lost replies and failed local ACK writes recover using the original batch/sample/content; client timeout does not prove server cancellation.

| Known batch state | Confirmable scope | Next action and protected material |
| --- | --- | --- |
| Entire batch durably committed | Receipt-bound members only; verify manifest separately | Persist ACK; other batch timeout never reverses it |
| Same identity and content | Original members covered by valid historical commit proof | Equivalent receipt; no new raw or latest regression |
| Same identity, different content | No new commit by this rejection; prior commits are not denied | Reject new batch writes, preserve/quarantine; no replacement identity to hide conflict |
| Unknown commit/lost reply | Neither infer a new ACK nor infer no commit | Recover original frozen result; no derived regrouping or reference release until resolved |
| Proven no new commit, mixed valid/expired members | Diagnostics are not partial ACK; verify earlier proofs separately | Persist original rejection/needs-action; only after provider-authorized retirement create a new batch referencing original valid sample identities/content, parentBatchId/rejection proof; rejected members remain protected |
| Members acknowledged elsewhere, old batch nonterminal | Member ACK monotonic; old batch still frozen | Retain original request material; release only if contract proves no separate batch side effect, complete evidence and permitted retirement |
| Expired sample with still-valid historical commit proof | Explicit historical confirmation, not currently readable value | Do not restore raw/latest; record only proven historical scope |
| Expired sample without commit proof | Nonretryable rejection; no fabricated ACK | Protect original sample/rejection; expiry is not local-delete permission; other legal batches retain fair scheduling |

This is a responsibility/durability matrix, not an implemented retirement state machine. Before coding, Backend/DAA freeze rejection proof, original-batch termination, derived association, mixed duplicate/expiry, explicit accepted gaps and finite proof retention. Fairness/latest priority cannot bypass reference safety to free disk; exhausted safe capacity must pause explicitly.

The following examples correspond to HTTP409/410/503; business error keys remain candidates. not_committed means no new commit by this request, not that earlier requests never committed. unknown does not mean rollback. The provider fixes remaining format/type/limit HTTP and business errors. Integration routes respect HTTP semantics; clients use status/code/errorCode/structured outcomes, not message wording.

```json
{
  "code": 409,
  "message": "conflict",
  "errorCode": "facts.sample_content_conflict",
  "data": {
    "batchId": "batch-conflict",
    "retryable": false,
    "persistence": "not_committed",
    "sampleIds": [
      "sample-a71"
    ]
  }
}
```

```json
{
  "code": 410,
  "message": "expired",
  "errorCode": "facts.sample_expired",
  "data": {
    "batchId": "batch-expired",
    "retryable": false,
    "persistence": "not_committed",
    "sampleIds": [
      "sample-old"
    ]
  }
}
```

```json
{
  "code": 503,
  "message": "temporarily_unavailable",
  "errorCode": "facts.commit_outcome_unknown",
  "data": {
    "batchId": "batch-unknown",
    "retryable": true,
    "persistence": "unknown"
  }
}
```

<a id="latest"></a>
## 6. Latest results, definitions and source order

Raw is deduplicated append history. Latest is maintained independently by stable PLC/point identity and aggregated by DB on read. Per-point physical latest is recommended; table names, indexes, auxiliary ledgers and compatibility with the current PLC/DB/group table belong to Backend. Two core storage roles do not imply exactly two physical tables.

Advancement requires the effective source generation, effective definition/membership, a higher sequence for that point and an unexpired result, enforced with atomic database conditions or equivalent concurrency control. Read-then-unconditional-write is insufficient. HTTP/receipt time, rewindable clocks and lexical ordering of opaque generation/revision strings are not source order. One point's high sequence cannot suppress another point's legal lower sequence; absent points in a package are not deletion.

The provider freezes initial adoption, conflicting sources, old-generation cutoff/new baseline and definition activation in its software spec. Normal restart, period changes and group movement do not reset durable sequence. Old generations may backfill raw under eligibility rules without gaining latest ownership. Anonymous source selection remains a declaration/configuration constraint, not device-ownership authentication.

Latest means most recent result: a newer bad result carries new observedAt, quality, reason and missing value; an old good value may only be separately labeled with original identity/time. Explicit disable/retirement/definition updates may use bounded membership metadata on the same fact route, with final encoding deferred. Without a declaration and without new samples, report stale/expired rather than immediate disable. Old history cannot reactivate old membership or roll back address/type.

asOf below is query time; observedAt is fact observation time. SMA checks its own quality/max-age policy: retained does not mean fresh. The directory is projected from effective reported definitions; never persist a second editable value-free pointCatalog.

Each aggregated point must retain its original sampleId and effective generation/sequence/definition association so SMA can construct stable sourceRefs. The source object below is illustrative; its final encoding is a provider-spec decision, and definitionVersion is not a new claim about current local v2 fields.

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "asOf": "2026-11-04T10:00:01.000+08:00",
    "items": [
      {
        "plcId": "plc-a",
        "dbNumber": 71,
        "points": {
          "point-a-temperature": {
            "definition": {
              "name": "DB71_temperature_Int",
              "sourcePath": "temperature",
              "address": {
                "offset": 2,
                "bit": null
              },
              "dataType": "INT"
            },
            "value": 202,
            "quality": "good",
            "reason": null,
            "observedAt": "2026-11-04T10:00:00.123+08:00",
            "source": {
              "sampleId": "sample-a71",
              "cycleId": "cycle-a-142",
              "groupId": "group-fast",
              "sourceGeneration": "generation-a",
              "sourceSeq": "142",
              "configRevision": "config-a3",
              "definitionVersion": "illustrative-definition-a3"
            }
          },
          "point-a-ready": {
            "definition": {
              "name": "DB71_ready_Bool",
              "sourcePath": "ready",
              "address": {
                "offset": 0,
                "bit": 0
              },
              "dataType": "BOOL"
            },
            "value": null,
            "quality": "bad",
            "reason": "read_timeout",
            "observedAt": "2026-11-04T10:00:00.123+08:00",
            "source": {
              "sampleId": "sample-a71",
              "cycleId": "cycle-a-142",
              "groupId": "group-fast",
              "sourceGeneration": "generation-a",
              "sourceSeq": "142",
              "configRevision": "config-a3",
              "definitionVersion": "illustrative-definition-a3"
            }
          }
        }
      }
    ]
  }
}
```

SMA definition signatures include name/address/type/validity, excluding value/quality/time/sampleId/sourceSeq. A real definition change pauses only affected bindings; unrelated revision changes do not stop everything. Interpret history with its original definition and approved mapping version. JSON alone cannot detect a PLC program change that DAA has not reported.

<a id="history"></a>
## 7. Range and changes modes of one history interface

| Mode | Candidate query parameters and selection | Pagination and use |
| --- | --- | --- |
| range | mode=range, PLC/DB/point filters, from, to, limit, pageCursor | Original point observedAt; candidate half-open[from,to), +08 times, fixed sort/snapshot boundary, nextPageCursor; manual/history recalculation |
| changes | mode=changes, fixed filters, cursor, limit | Backend durable publication position; nextCursor/hasMore with source/sample/completeness; continuous input including late backfill |

The provider freezes parameter names, filters, snapshot bounds and limits. A range-page cursor is not a changes receive cursor. Both bind mode, contract version and filters; changing PLC/filter requires a new selection/baseline. An initial changes start explicitly chooses the earliest recoverable position or an audited new baseline, never silently the tail while claiming complete input.

A nonempty page reuses section4's semantic sample, not original byte text. This package may commit after sourceSeq145 while still being covered by the safe cursor.

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "mode": "changes",
    "items": [
      {
        "sampleId": "sample-a71",
        "cycleId": "cycle-a-142",
        "plcId": "plc-a",
        "sourceGeneration": "generation-a",
        "sourceSeq": "142",
        "groupId": "group-fast",
        "configRevision": "config-a3",
        "dbNumber": 71,
        "sourceSha256": "illustrative-original-sample-a71",
        "points": {
          "point-a-temperature": {
            "definition": {
              "name": "DB71_temperature_Int",
              "sourcePath": "temperature",
              "address": {
                "offset": 2,
                "bit": null
              },
              "dataType": "INT"
            },
            "value": 202,
            "quality": "good",
            "reason": null,
            "observedAt": "2026-11-04T10:00:00.123+08:00"
          },
          "point-a-ready": {
            "definition": {
              "name": "DB71_ready_Bool",
              "sourcePath": "ready",
              "address": {
                "offset": 0,
                "bit": 0
              },
              "dataType": "BOOL"
            },
            "value": null,
            "quality": "bad",
            "reason": "read_timeout",
            "observedAt": "2026-11-04T10:00:00.123+08:00"
          }
        }
      }
    ],
    "nextCursor": "opaque-commit-safe-cursor-example",
    "hasMore": true
  }
}
```

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "mode": "changes",
    "items": [],
    "nextCursor": "opaque-commit-safe-cursor-example",
    "hasMore": false
  }
}
```

An empty page/hasMore=false describes only the current deliverable page. It does not prove no in-flight transaction, no acquisition gap or a complete sequence prefix. A sample observed10:05 but committed10:20 must remain discoverable by subsequent changes pages; max observation time would lose it.

Backend must prove deliverable commits before its cursor cannot appear later. A smaller auto-increment raw ID may be allocated first but commit last. Unproven max(raw.id), sourceSeq or query time is not a safe cursor. Backend selects and verifies commit-ordered publication, gap-aware scanning or an equivalent algorithm. Natural filtered sequence gaps differ from missing inputs; complete cycle prefixes, maximum seen sequence and receive cursor have separate meanings.

Expired cursor, changed filters/contract or deleted material return explicit reason, recoverable start/range, affected gaps and a resynchronization procedure, never a silent tail jump. Resync preserves processing/business confirmations and does not create a new eventId for the same re-read input. A receive cursor is not a processing checkpoint; stateful/window rules need source order, completeness, lateness and gap policies.

<a id="retention"></a>
## 8. Shanghai time, three natural months and bounded proof

Fact timestamps and new API/IPC use Asia/Shanghai RFC3339 with +08:00 and original precision; UI defaults to 24-hour seconds. Observation, read start/end, local save, Backend commit and UI refresh are distinct. Convert external zones once at the boundary. This does not authorize migration of UTC/unknown profiles, adding eight hours blindly or rewriting historical bytes.

Raw/latest default to and are capped at three natural months, optionally shorter. Per-point maximum deadline is original observedAt plus three calendar months, clamping a missing target day to month-end at the same Shanghai wall time. At the deadline the fact is unavailable, not after90 days. Upload/read/ACK/other-point updates never renew TTL. Future clock anomalies are rejected/quarantined under the provider tolerance, not rewritten to reception time.

| Original observedAt | Maximum deadline |
| --- | --- |
| 2026-01-31T12:00:00.123+08:00 | 2026-04-30T12:00:00.123+08:00 |
| 2023-11-30T06:00:00.000+08:00 | 2024-02-29T06:00:00.000+08:00 |
| 2024-11-30T06:00:00.000+08:00 | 2025-02-28T06:00:00.000+08:00 |

For a package with differing observedAt values, immutable whole-original reads conservatively expire at the earliest member deadline; latest expires per point. An equivalent projection/storage strategy must prove no expired value is returned, distinguish original/projection digests and prevent whole-original access from exposing an expired member. Immutability does not authorize reading values beyond retention.

Logical unreadability, bounded physical deletion, disk reclamation and backup/replica responsibilities are distinct. Backend fixes cleanup SLA, batch/lock/load budget and failure observability; do not claim instantaneous destruction of every copy. Minimal idempotency/historical-receipt/completeness digests may have separate finite retention, not permanent original values. Expired retries must never resurrect raw/latest; missing evidence must never fabricate a historical ACK.

Stale latest and its directory eventually expire. Backend does not extend fact lifetime because DAA/SMA still need confirmation. Local pending/incomplete/frozen references stay protected; rejection does not authorize local deletion. Finite disk and long outages can cause explicit capacity pause or genuine gaps, not unlimited replay.

<a id="business"></a>
## 9. SMA mapping, business receipts and permanent records

SMA uses latest for state/preview and history for per-sample/history computation. It selects points and validates definitions/quality/age, then maps OpenAPI or manual target fields into module-owned typed data. One DAA package need not yield one business request; cross-PLC/DB objects retain all input identities/times and declared skew limits, not invented synchronous snapshots.

This future single-temperature example is not the existing full-temperature POST body. producerId/eventId identifies one logical delivery, mappingRevision freezes transformation semantics, sourceRefs identify input. Repeated polling of the same processed input does not create a new output identity. Different real samples/windows/approved corrections may have their own events under the module rule.

```json
{
  "producerId": "sma-demo",
  "eventId": "delivery-demo-1",
  "mappingId": "mapping-temperature",
  "mappingRevision": "mapping-v3",
  "sourceRefs": [
    {
      "plcId": "plc-a",
      "sampleId": "sample-a71",
      "pointId": "point-a-temperature",
      "sourceGeneration": "generation-a",
      "sourceSeq": "142",
      "configRevision": "config-a3",
      "definitionVersion": "illustrative-definition-a3"
    }
  ],
  "data": {
    "equipmentId": "equipment-demo",
    "sampledAt": "2026-11-04T10:00:00.123+08:00",
    "temperature": 202
  }
}
```

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "producerId": "sma-demo",
    "eventId": "delivery-demo-1",
    "requestDigest": "illustrative-business-request-digest",
    "recordId": "business-record-demo",
    "outcome": "created",
    "persistence": "committed"
  }
}
```

Targets validate module-required fields/ranges/equipment/business natural keys and define idempotency scope/window. Equal producer/event/content returns an equivalent committed result; different content conflicts. An existing sampleId-based target must define an equivalent eventId mapping instead of two ambiguous identities. SMA freezes requests durably, verifies the post-commit receipt and persists it before reporting delivered. HTTP200/202 or enqueue alone is not permanent business persistence.

Receive cursor, processing checkpoint, frozen outbox and per-target acknowledgements are independent. If A is confirmed and B is not, recover B only. Lost replies recover using the same eventId; no blind replacement key. unknown or a target without idempotency/result verification needs explicit handling, not an arbitrary exactly-once side-effect promise.

Reliably confirmed business records default to permanent retention: no automatic TTL deletion; correction/deletion follows explicit module business rules. Business tables retain actual business values, event time and necessary source/definition/mapping evidence, interpretable after raw expiry, not only a raw foreign key. Raw/latest cleanup never cascades into business records, unfinished outbox or still-valid minimal proof. Traceability is not a permanent copy of every raw original.

If SMA durably captured sufficient input/output before source expiry, it may continue under its own capacity/retention and target contract. Missing/uncaptured expired inputs or parts produce a genuine gap, pause affected rules and require explicit resync. Permanent business retention cannot recreate never-persisted records. SMA input/outbox remains bounded, with storage location/migration owned by its own task.

<a id="implementation"></a>
## 10. Subsequent tasks, dependencies and acceptance material

After independent document review and Owner document acceptance, the Backend provider separately scopes and approves its executable contract/version/algorithms/limits and published contract. DAA consumes that fixed version. Independently approved implementations may proceed in parallel; actual HTTP integration waits for a fixed Backend-ready candidate. Material shared-semantic changes require revised specs and exact approval.

| Future owner / candidate task | Required incremental capability and acceptance material |
| --- | --- |
| Backend / tentative ARCH-BE-009 | B01 anonymous strict one-write/two-read routes; B02 explicit schema migration and old CA/Projection compatibility; B03 transactions/duplicates/conflicts/unknown/mixed receipts; B04 per-point concurrent latest/definitions/sources; B05 safe cursor/late commits; B06 time/expiry/cleanup/finite proof; B07 separately authorized isolated DB checks and fresh QA; B08 fixed contract/source/schema/fingerprints/limits/errors/test material and honest readiness handoff |
| DAA / tentative DAA-008 | D01 single target/period and SQLite configuration; D02 Rust bounded single-flight scheduling; D03 frozen identities and local ACK recovery; D04 latest priority/fair history; D05 independent acquisition/upload controls/capacity/stopped startup; D06 truthful workbench/logging/CU; D07 explicit delivery metadata upgrades/history protection; D08 bilingual guide, necessary Owner native increments, same-store reconciliation and fresh QA |
| SMA / business modules | Separately approved consumption/mapping/durable business delivery and anonymous typed module endpoints; not prerequisites for DAA Stage C and not authorized by this demand |

Full B01–B08/D01–D08 conditions are in [approved spec section8](../../plans/ARCH-AW-008-stage-c-facts-contract/spec.md#8-后续软件任务依赖与验收标准). These candidate IDs are not created by this task. Software/schema/live integration has not been executed. DAA Stage C requires Backend readiness, upload/recovery evidence, cross-end reconciliation and an Owner decision. Automatic startup, background hosting, real sites, production migrations and cross-platform packaging are separate gates.

Before coding, the respective software specs must freeze the PLC/JSON and missing-value matrix, part encoding, three digest profiles, first-source/handover/definition activation, cursor algorithm/time bounds/filters, clock tolerance, request/rate/fairness/timeout budgets, mixed-batch retirement, cleanup SLA and minimal-proof retention. Placeholder examples select no library, physical schema or runtime parameter implicitly.
