# PLC facts owner

## ARCH-ACQ-004 r3 source management

The runtime profile contains only `target`, with `schemaRevision` `7b9d1f3a5c7e`. An active administrator registers one row per PLC with `plcId`, `instanceId`, `sourceGeneration` and the display label `sourceType`. Samples match only the three identifiers; DB is supplied with each sample. Realtime reads require current registration; unexpired history remains readable independently. [Management OpenAPI](../../../contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r4.json) · [Migration and recovery](../../scripts/plc_facts_maintenance/README.md#r3-single-table-migration-and-recovery)

The sample POST and five GETs require no Bearer in development; management requires an active administrator. Registration is not device authentication. Web copies the three identifiers from the saved row. A takeover needs version checking, explicit confirmation and a new generation for that PLC. Reconcile the old queue first; history is not rewritten.

Confirmed deletion removes the source row and stops its uploads without deleting history. It also removes that row's retired-generation list; after facts and latest values disappear, an old generation may no longer be detectable. Use a never-used generation when registering the PLC again.

## v2 sample endpoint

`ARCH-BE-012 r4` adds one PLC/DB sample write, per-point latest values, history and detail. `PLC_FACTS_V2_ENABLED` defaults to `False` and `PLC_FACTS_V2_PROFILE_FILE` defaults to empty. The following is the historical `5f7a9c1e3b25` predecessor format, used only as explicit import input by frozen r2 tooling before r3 migration.

```json
{
  "target": {"alias": "dev-example", "serverUuid": "00000000-0000-4000-8000-000000000001", "schema": "fixture_schema", "schemaRevision": "5f7a9c1e3b25"},
  "instances": [{"instanceId": "external-a", "sourceType": "external"}],
  "sources": [{"plcId": "PLC-A", "instanceId": "external-a", "sourceGeneration": "gen-a", "dbNumbers": [21]}],
  "readScopes": {"admin": [{"plcId": "PLC-A", "dbNumbers": [21]}]}
}
```

The predecessor used `instances` and `sources`; r3 checks the three identifiers against the database. Any sender may omit group and configuration revision or send null. The backend stores historical source type at ingestion. Older rows with unverified source type use null.

The predecessor's `readScopes` is retained as pre-migration reconciliation material. See the [v2 contract](../../../contracts/published/http-api/plc-facts-v2/README.md).

To preserve the original decimal precision, both v2 JSON value fields internally store a `good` REAL as validated numeric text. Reads validate it by `dataType` and emit a JSON number. Other point types retain their JSON types. This representation preserves negative zero and scientific notation without expanding very small exponents.

`2c4e6a8b0d12` introduced the tables, and `4e6a8b0d2f14` named them. The r3 head is `7b9d1f3a5c7e`. Each `plc_facts_history` row stores one complete sample and each `plc_facts_latest` row stores one latest point. The profile and database revision must match exactly. The [v1 contract](../../../contracts/published/http-api/plc-facts-v1/README.md) documents the retired routes, seven tables and maintenance commands. BE-010 credentials use their own scope and must match their target revision. See [ARCH-ACQ-003](../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/spec.md) and [v2 maintenance](../../scripts/plc_facts_maintenance/README.md).
