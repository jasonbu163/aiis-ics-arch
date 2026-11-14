# PLC facts maintenance CLI

## r3 single-table migration and recovery

Run only against an explicitly approved target. Pause registration, sample writes and cleanup; retain a restorable backup and the old private JSON. Read-only preflight MySQL 8.4, Shanghai clock, UUID, schema, sole predecessor `6a8c0e2b4d16`, the six legacy tables and initialization status. Record read-only PLCs without active bindings and DBs newly readable after adoption. Stop if the state or material cannot be reconciled.

For initialized r2, the database is authoritative: export its registry and generations using the **frozen r2 source**. If the old JSON remains the source, preview, import and reconcile it with the frozen r2 tool before migrating. If all six tables are empty and an empty start is explicitly confirmed, set `ACQ_REGISTRY_R3_EMPTY_CONFIRMED=1`; no r2 empty initialization is needed. The current r3 import/export commands refuse execution; the historical examples below are for frozen r2 tooling only.

Set the approved target's `ACQ_REGISTRY_EXPECTED_SERVER_UUID` and `ACQ_REGISTRY_EXPECTED_SCHEMA`; from the backend directory run `alembic upgrade 7b9d1f3a5c7e` in the locked environment. The migration checks the target, merges current and retired identities, and compares the identity bytes, revisions and times. Before dropping the old tables, it scans both `plc_facts_history` and `plc_facts_latest` twice and compares schema, row counts and SHA-256 of every row, including original samples and latest sequence watermarks. Preserve the printed digests. Two full scans may take substantial time and resources on large tables; allow for them in the write pause. Stop on a mismatch or interruption.

MySQL DDL is non-transactional. Preserve and inspect actual objects, contents and revision after a failure; do not stamp or delete tables to force a retry. Restore a verified predecessor backup or repair forward from a known state, reconciling registry, facts and watermarks. If r3 has accepted new data, preserve and reconcile those changes before deciding; where they cannot be replayed without loss, keep the state and repair forward. Update the private runtime revision, cleanup and known-revision checks after migration, and verify registrations, matching receipts and reads before resuming. Existing targets continue to follow their original contract until switched.

## r2 candidate: migration, import and recovery (frozen predecessor tooling)

These steps apply only to a separately approved synthetic target; source readiness does not mean dev or production has migrated. Pause registration, collection writes and cleanup for that target; retain a verified predecessor backup and old source file. Check MySQL 8.4, Shanghai database time, UUID, schema and single predecessor `5f7a9c1e3b25`. With a dedicated migration account, set `ACQ_REGISTRY_EXPECTED_SERVER_UUID` and `ACQ_REGISTRY_EXPECTED_SCHEMA` and run `alembic upgrade 6a8c0e2b4d16`. MySQL DDL is not transactional. On interruption or existing partial objects, stop, record the actual objects and revision, and restore a verified predecessor backup to an independent target. Do not stamp or delete tables to force a rerun. Complete import and reconciliation before switching all backend processes to the candidate and a target-only private profile.

Explicitly initialize even an empty registry using an external private predecessor JSON. Supply the approved alias, schema, UUID, operator and approval reference:

```text
uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py import-sources --plan --target-alias <alias> --schema <schema> --expected-server-uuid <uuid> --expected-schema-revision 6a8c0e2b4d16 --operation-approval <approval-ref> --confirmed-by <operator> --source-file /private/approved/old-profile.json
```

Compare counts, `logicalSha256` and `sourceSha256`. For application set `PLC_FACTS_MAINTENANCE_ENABLED=True`, replace `--plan` with `--apply`, and add `--expected-source-sha256 <sha>` and `--confirm IMPORT:<alias>:<schema>:<uuid>:<sha>`. One transaction commits registry data and its initialization marker. Repeating the same input verifies the marker without overwriting later Web changes. On `import_commit_unknown`, rerun `--plan` with the same input and inspect the marker, original digest, current digest and counts before deciding what to do.

For recovery, pause the target, record both fact-table watermarks and take a backup. Export the complete current registry to a new private file, specifying the independent predecessor restore target:

```text
uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py export-sources --target-alias <alias> --schema <schema> --expected-server-uuid <uuid> --expected-schema-revision 6a8c0e2b4d16 --operation-approval <approval-ref> --confirmed-by <operator> --restore-alias <restore-alias> --restore-schema <restore-schema> --restore-server-uuid <restore-uuid> --output-file /private/approved/source-export.json
```

The exclusively created file contains `legacyProfile`, all `generations`, registration revisions and a summary. Preserve it and the printed SHA; write `legacyProfile` unchanged to a separate private JSON whose target matches the actual restore UUID/schema. Restore the exact predecessor backup into an independent schema and copy the necessary post-cutover `plc_facts_history` and `plc_facts_latest` rows. Compare primary keys, payloads, hashes, times and watermarks row by row. Only when each destination fact table is empty, its columns match and the operation is authorized may `INSERT INTO <restore>.<table> SELECT * FROM <source>.<table>` be used. For nonempty tables, reconcile every key first; stop on conflicting values or unverifiable conservation. Verify that the predecessor parses the profile and that every active write grant, independent read grant and fact is preserved before considering adoption.

For a later r2 adoption, pass the complete export as `--generation-file <source-export.json>` with the predecessor `--source-file`. Preview and verify `generationFileSha256` and the preserved count; append `:<generation-file-sha>` to the apply confirmation. Conflicting source, instance type or target is rejected. The export does not replace fact backups or switch services. [Candidate specification](../../../plans/ARCH-ACQ-004-acquisition-source-registry/spec.md)

## v2 expiry cleanup

`cleanup-v2` requires an explicit `--plan` or `--apply`, target alias, schema, server UUID, revision, operation approval reference and confirmer. The target must match the private v2 profile and the live database. This preview uses synthetic target values.

```bash
uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py cleanup-v2 --plan --target-alias dev-example --schema fixture_schema --expected-server-uuid 00000000-0000-4000-8000-000000000001 --expected-schema-revision 7b9d1f3a5c7e --operation-approval fixture-approval --confirmed-by fixture-operator
```

The cleanup byte budget includes the nullable history `source_type`; history cleanup removes whole samples from `plc_facts_history`, while latest cleanup clears values and preserves the ordering watermark in `plc_facts_latest`.

For execution, set `PLC_FACTS_MAINTENANCE_ENABLED=True`, replace `--plan` with `--apply`, and provide `--confirm APPLY:cleanup-v2:<alias>:<schema>:<server-uuid>:<revision>`. Plan and apply emit JSON Lines with row and byte counts, oldest backlog and completion time. Each transaction processes at most 200 rows and 2 MiB. Each tick processes at most 2000 rows and 20 MiB with a two-second processing budget. An external scheduler invokes the command every minute and monitors completion and backlog. History rows are deleted while latest rows retain their instance, generation and sequence watermark.

Each transaction sets bounded row-lock and metadata-lock waits before the target lock probe. If the budget prevents a backlog query, `oldestKnown` is `false` and monitoring should treat that backlog state as unknown. Completion time comes from a database clock query without table locks, and connection reads and writes have timeouts.

Use the existing project environment: `uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py` prints help before settings/database imports, as does `--help`. There is no default input/output file, target, seed, DDL, scheduler or packaged artifact.

The old v1 `status`, `adopt` and `cleanup` commands are retired. Actual cleanup remains separately authorized and target-scoped.
