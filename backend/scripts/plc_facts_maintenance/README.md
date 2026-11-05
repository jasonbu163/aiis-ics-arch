# PLC facts maintenance CLI

Use the existing project environment: `uv run --offline --frozen --no-sync python scripts/plc_facts_maintenance/main.py` prints help before settings/database imports, as does `--help`. There is no default input/output file, target, seed, DDL, scheduler or packaged artifact.

Commands are `status`, `adopt --plan/--apply`, and `cleanup --plan/--apply`. Every DB operation, including status/plan, requires separate G-B target approval. Explicit target-alias, schema, expected-schema-revision, expected-storage-epoch, operation-approval and confirmed-by are required. Apply also requires `PLC_FACTS_MAINTENANCE_ENABLED=True` and `--confirm APPLY:<action>:<target-alias>:<schema>:<storageEpoch>`.

Source adoption specifies PLC/instance/generation/config, context-file/SHA, expected-binding-revision and new seq-from. Switching requires old-seq-through and at most eight windows. `adopt --revalidate-schema-only` checks only known 0a2/1b3/F7 and CAS-refreshes credentials; source arguments are forbidden. Existing state requires its expected-adoption-id and original epoch; proofs and TTLs remain intact.

Precedence is CLI > OS environment > tool .env > backend .env > safe defaults. The example flag is off; never commit credentials. Stdout emits start/dry-run/commit/failed/complete JSON Lines; only explicit `--output-log` writes a file. Errors are redacted and nonzero. Cleanup limits each transaction to 200 rows/2 MiB/100 ms and each tick to ten transactions/2000 rows/20 MiB/two seconds, using NOWAIT locks. It touches no business/other-owner data. Scheduling and the conditional 24-hour physical SLA require separate adoption and verification; A has not run them.
