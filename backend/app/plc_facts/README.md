# PLC facts owner

## v2 sample endpoint

`ARCH-BE-012 r4` adds one PLC/DB sample write, per-point latest values, history and detail. `PLC_FACTS_V2_ENABLED` defaults to `False` and `PLC_FACTS_V2_PROFILE_FILE` defaults to an empty value. Before enablement, place a private JSON file outside the repository and set its path in the process environment or backend runtime configuration. This synthetic structure uses a placeholder digest.

```json
{
  "target": {"alias": "dev-example", "serverUuid": "00000000-0000-4000-8000-000000000001", "schema": "fixture_schema", "schemaRevision": "4e6a8b0d2f14"},
  "instances": [{"instanceId": "daa-a", "sourceType": "daa"}],
  "credentials": [{"instanceId": "daa-a", "tokenSha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}],
  "sources": [{"plcId": "PLC-A", "instanceId": "daa-a", "sourceGeneration": "gen-a", "dbNumbers": [21]}],
  "readScopes": {"admin": [{"plcId": "PLC-A", "dbNumbers": [21]}]}
}
```

Each registered instance has source type `daa` or `external` and a separate random credential. The file stores only the lowercase SHA-256 digest. Removing a credential revokes writes while retaining the instance and active source permits authorized latest queries. A DAA must supply group and configuration revision; an external producer may omit either or send null. Historical source type is stored at ingestion; older, unverified sources remain null. Read scopes are configured per role, including admin. Non-admin roles also need `plc-facts-read`. Reload every backend process during a coordinated source or configuration change. See the [v2 contract](../../../contracts/published/http-api/plc-facts-v2/README.md).

To preserve the original decimal precision, both v2 JSON value fields internally store a `good` REAL as validated numeric text. Reads validate it by `dataType` and emit a JSON number. Other point types retain their JSON types. This representation preserves negative zero and scientific notation without expanding very small exponents.

`2c4e6a8b0d12` introduced the tables; `4e6a8b0d2f14` is the new exact head and retains one complete sample per row in `plc_facts_history` and one latest point per row in `plc_facts_latest`. The profile and database revision must match exactly. The [v1 contract](../../../contracts/published/http-api/plc-facts-v1/README.md) remains historical; its routes, seven tables and maintenance commands are retired. BE-010 credentials remain separately scoped and must match their target revision. See [ARCH-ACQ-003](../../../plans/ARCH-ACQ-003-acquisition-data-optional-filters/spec.md) and [v2 maintenance](../../scripts/plc_facts_maintenance/README.md). Source changes do not prove deployment or adoption.
