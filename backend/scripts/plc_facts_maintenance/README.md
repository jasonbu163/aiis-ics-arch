# PLC facts maintenance CLI

## v2 expiry cleanup

`cleanup-v2` requires an explicit `--plan` or `--apply`, target alias, schema, server UUID, revision, operation approval reference and confirmer. The target must match the private v2 profile and the live database. This preview uses synthetic target values.

```bash
uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py cleanup-v2 --plan --target-alias dev-example --schema fixture_schema --expected-server-uuid 00000000-0000-4000-8000-000000000001 --expected-schema-revision 4e6a8b0d2f14 --operation-approval fixture-approval --confirmed-by fixture-operator
```

The cleanup byte budget includes the nullable history `source_type`; history cleanup removes whole samples from `plc_facts_history`, while latest cleanup clears values and preserves the ordering watermark in `plc_facts_latest`.

For execution, set `PLC_FACTS_MAINTENANCE_ENABLED=True`, replace `--plan` with `--apply`, and provide `--confirm APPLY:cleanup-v2:<alias>:<schema>:<server-uuid>:<revision>`. Plan and apply emit JSON Lines with row and byte counts, oldest backlog and completion time. Each transaction processes at most 200 rows and 2 MiB. Each tick processes at most 2000 rows and 20 MiB with a two-second processing budget. An external scheduler invokes the command every minute and monitors completion and backlog. History rows are deleted while latest rows retain their instance, generation and sequence watermark.

Each transaction sets bounded row-lock and metadata-lock waits before the target lock probe. If the budget prevents a backlog query, `oldestKnown` is `false` and monitoring should treat that backlog state as unknown. Completion time comes from a database clock query without table locks, and connection reads and writes have timeouts.

Use the existing project environment: `uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py` prints help before settings/database imports, as does `--help`. There is no default input/output file, target, seed, DDL, scheduler or packaged artifact.

The old v1 `status`, `adopt` and `cleanup` commands are retired. Actual cleanup remains separately authorized and target-scoped.
