# AIIS Data Acquisition Agent

[中文](README.zh-CN.md)

DAA uses the CU public shell and one local SQLite runtime. Ordinary `pnpm tauri dev` opens Workbench, PLC configuration, Points and collection groups, and Reporting and storage. No mode or storage flag is required. `pnpm tauri:dev` and `pnpm tauri:dev:snap7` explicitly compile the optional Snap7 driver; ordinary startup does not. Missing driver returns `driver_unavailable` on an explicit connection request.

```bash
pnpm install --frozen-lockfile
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml -- --check
pnpm tauri dev
```

Source came from the CA freeze receipt; [DAA PLAN](PLAN.md) owns implementation, [AW PLAN](../PLAN.md) cross-project stages. [DAA-003 r1](plans/DAA-003-sqlite-only-startup/spec.md) owns SQLite-only startup and migration. [DAA-002 r2](plans/DAA-002-local-acquisition-loop/spec.md) owns the existing local acquisition baseline; its QA and Human Owner acceptance remain separate task facts. These documents do not authorize field switching, publication or deployment.

## Configuration authority and startup

Only this app's root `.env` or an explicit absolute process `DAA_ENV_FILE` is selected. `DAA_PROFILE_DIR`, when present, must be absolute; otherwise the app's independent local-data directory is used. There is no cwd/parent/CA/env search. SQLite in `local-acquisition-v1/config.sqlite` and `runtime.sqlite` owns PLCs, groups, points, storage and history. `DAA_PLC_READ_ALLOWED` defaults false; true never connects or starts collection on boot.

The old YAML runtime, direct database writer, Backend health probe and authorization self-test are retired. Old IPC commands are unregistered. `--ca-*` and the inherited runtime binary return structured `legacy_entry_retired` / exit2 before configuration or locking; no SQLite headless replacement is provided. Remove obsolete scripts from your operational workflow. A selected env-file `DAA_RUNTIME_MODE=legacy_snapshot` is ignored once with a key-name notice. An explicit process override with that value is rejected with `legacy_runtime_retired` / exit2; remove it and start normally. Empty/local_sqlite values are accepted; other values fail. Other old DB/write/autostart/endpoint/Backend/log-path values have no business effect and their values are not consumed. `.env` is never rewritten. Vite uses `envDir:false` and no old `VITE_DAA_*` business input.

## One-time legacy YAML migration

After the profile OS lock and dual-store identity/integrity/recovery, a first empty instance checks exactly `DAA_PLC_CONFIG_PATH` and `DAA_PLC_SNAPSHOT_POLICY_PATH`: nonempty process override, then selected env-file value, then own `config/plc_points.yaml` / `config/plc_snapshot_policy.yaml`. Relative paths anchor to DAA's root. Symlinks/directories/non-UTF8/changes during reading fail; no parent scanning or URL loading occurs. Actual site files are not authorized validation inputs for this task.

Existing draft objects/sources, a changed storage policy, revisions/active/previous/tokens, runtime source identities, contexts, samples or delivery/reference rows preserve SQLite without reading or hashing YAML. Only lifecycle events do not disqualify an empty instance. A persisted migration receipt also prevents automatic rescanning, even after files change or a user clears the draft.

All representable PLCs, DBs, groups and points migrate together as disabled candidates. Every address is unconfirmed; every DB is incomplete and non-flat, without a fabricated tree. Original read windows/counts/access flags, unsupported types and raw/latest policy choices are retained as bounded whitelist source descriptions/diagnostics. They never become enabled, write permissions, sampling policy, upload/ACK or direct database rules. Unknown fields are diagnosed without saving their values; credentials are excluded. The original files remain untouched. Default source files are sanitized examples and remain disabled candidates.

- Missing/blank/comments/null/empty YAML records `skipped_empty`. Policy-only input archives policy without creating PLCs.
- Bad syntax/root/types/duplicate semantic objects/ambiguous policy mapping or limits rejects the whole candidate; an empty SQLite editing UI remains usable. Failure is explicit, never empty success.
- Hard limits: each YAML 1MiB, pair 2MiB, depth16, 100000 nodes; aliases/tags/multiple documents rejected. Existing limits remain 4 PLCs, 8 groups/32 DBs/4096 points per PLC and 16MiB configuration. The canonical private receipt/archive is at most 8MiB; only 200 diagnostics are returned with omitted counts, summary at most256KiB.
- Migration history and safe retry are inside the existing, initially collapsed **Runtime configuration and versions** details in the configuration bar. Only unknown persistence or a failed result with Rust `retryAllowed=true` adds a compact prompt outside it. A remembered failure that is no longer retryable stays historical. Failed/empty/policy-only results can be explicitly retried only while Rust still allows it, with draft ETag and attempt-ID CAS; Save or cancel edits first. Success or an existing SQLite instance offers no overwrite action. Unknown persistence cannot be claimed as remembered; repair storage/logging and reopen. Counts, diagnostics and disabled/unconfirmed/incomplete descriptions record the migration time, not subsequent edits.

YAML is a one-time source; SQLite owns saved business configuration; `.db/.udt` are explicit structure imports during editing. Normal source import rejects YAML. Use the existing difference preview, address review and group configuration workflow before explicit activation, connection and collection.


### Repository default example

The following is the sanitized default in [`config/plc_points.yaml`](config/plc_points.yaml), with the retired policy in [`config/plc_snapshot_policy.yaml`](config/plc_snapshot_policy.yaml). Process/env-file path overrides can select different sources, so this is not an inventory of any current user profile.

| Default example | Value |
| --- | --- |
| PLC / connection candidate | `PLC_1`, `127.0.0.1:102`, rack 0 / slot 1 |
| DB / group / old read window | DB1, `example_group`, start 0 / size 12, 3 points; the window does not prove full DB length |
| Point 1 | `example_value`, old type `Real`, offset 0 |
| Point 2 | `example_status`, old type `Bool`, offset 4 / bit 0 |
| Point 3 | `example_counter`, old type `DInt`, offset 8 |
| Retired policy for all 3 points | raw/latest=true, raw_policy=`every_sample`; whitelist archive only, never new sampling/reporting/direct-database rules |

There are no sampled values or history in these files. A first empty instance imports disabled candidates with unconfirmed addresses and incomplete DBs only. Existing SQLite configuration/history take precedence, and private success/empty receipts prevent automatic duplicate scans; the source YAML stays unchanged. Editing imports remain explicit `.db/.udt` structure inputs, with full-source preview, address review and collection-group setup before separate runtime actions. The [minimal DB/UDT pair](src-tauri/tests/fixtures/source-import-minimal/README.md) provides a handwritten three-leaf controlled import checklist with explicit DB number 21; it does not establish actual TIA export compatibility or live PLC addresses.

## Local acquisition and recovery

Four pages use one `useLocalAcquisitionConsole`; a pure shell owns navigation/theme/language (`daa.theme`/`daa.locale`). Browser preview has no SQLite bridge or fake save and performs no Backend/health requests. Bootstrap failure is distinct from preview. The first failed snapshot is not loaded; later failure retains the last good snapshot with a stale notice. Only one 1Hz runtime refresh runs.

The existing dual SQLite v1, DELETE/EXTRA, instance identity, exclusive profile lock, CAS/activation/recovery, unique serial PLC actors, complete-round sample/manifest/sequence/pending transaction, bounded original-byte history, capacity reserves and protected maintenance remain. Startup always has stopped connection/collection intentions. Missing/corrupt/mismatched stores or unexpected WAL material fail closed. The migration receipt uses the existing source_documents table; no schema/ledger or dependency upgrade occurs. See [local store notes](src-tauri/src/infrastructure/local_store/README.md).

Limits remain 4 PLCs, 8 groups/32 DBs/4096 leaves per PLC, 256 enabled points per group, periods >=500ms. These are admission limits, not field throughput promises. Each PLC shares one connection for collection/test/diagnostics. Pending rows cannot be ACKed or cleared by the product. Upload is Stage C; the UI says local save only, upload unavailable. Capacity may pause before90% to preserve journal/system reserves; pending is never deleted by retention alone. A log write failure latches an unknown interval until repair and restart; history/Stop/disconnect/shutdown remain available. SQLite3.46.0 DELETE/EXTRA is a narrow storage contract, not a WAL fix or hardware power-loss guarantee.

## Isolated validation boundary

`pnpm build --config vite.validation.config.ts --outDir <absolute-tmp-dist> --emptyOutDir` remains env-isolated. Nondefault debug `local-validation` remains fixed-fixture only with its existing absolute tmp paths/owner marker/inherited-env rejection and release compile rejection. It does not automatically discover source YAML. Its CLI/binary and required arguments are unchanged; it cannot access real transport, arbitrary SQL or ACK. Use ordinary startup with newly owned tmp env/profile and read gate=false for DAA-003's native migration/save/reopen proof. Browser or fixture evidence does not replace that proof. Real PLCs, actual profile/YAML migration, Backend/SMA/DS, Stage C, production DB/API, source switching, Docker/Git/release/deployment and cross-platform signing require separate approval.

## Multi-DB source editing and standard offsets

In Points and collection groups, save or cancel current edits, select a PLC, then choose `.db/.udt` files. Rust automatically identifies declarations; the same region shows each DB with its own checkbox and actual number (1–65535). New numbers are blank, never inferred from a name or date. UDTs are a dependency summary with no number. Pagination (10/20/50) preserves selections and numbers across pages. For changed source text, explicitly choose the original existing target; a filename alone does not establish an update identity.

Preview opens a dialog with the complete selected delta, located diagnostics, preserved manual settings and collapsed structure trees. Closing writes nothing and keeps file choices. One explicit confirmation atomically saves only the selected complete blocks as a draft; it neither enables points nor activates or starts acquisition. A selected fatal issue blocks the whole set; deselect a localized problem block to import a valid subset. Unsafe file boundaries block the whole file. Edits, mapping changes, reload, stale ETag or expired/mismatched preview tokens require a new preview.

Bounded syntax includes UTF-8/BOM and LF/CRLF without byte normalization, multiple named DATA_BLOCK/TYPE declarations, VERSION, NON_RETAIN/RETAIN, Boolean S7_SetPoint field attributes, STRUCT, acyclic UDTs and one-dimensional constant arrays (including negative/nonzero bounds). Unknown syntax/attributes/types, ambiguous fields, missing/cyclic/duplicate dependencies, nested or multidimensional arrays and resource excess are rejected. Initial expressions/BEGIN are never executed or sampled. This is not a general TIA compiler.

Reimport preserves stable DB/point IDs, user names/comments, grouping, switches and manual address values/reasons. Unchanged imports preserve the ETag. Added leaves, type/order/layout dependency changes invalidate every existing address confirmation in that selected DB. Removed/renamed leaves, renamed blocks and existing DB renumbering are blocked; original configuration remains. Sources are immutable logical versions with per-DB frozen UDT closures. Unselected DBs and other PLCs keep their previous source/tree/address state. Equal bytes may share one physical archive across logical sources/PLCs without overwriting its original metadata. Existing SQLite history, active revisions and the private YAML receipt remain intact.

**Preview standard-layout offsets** then **Confirm non-manual offsets** is a separate two-step draft operation. The dialog shows paths, old/proposed addresses, calculated/current DB length and manual conflicts. The Siemens STEP7 V20 standard-word profile requires a complete explicitly non-optimized source with a verified dependency closure. It covers BOOL, BYTE/USINT/CHAR, INT/UINT/WORD, DINT/UDINT/DWORD/REAL, nested STRUCT/UDT and one-dimensional scalar/STRUCT/UDT arrays. STRING remains importable/manual but rejects inference for the entire DB, as do optimized/unknown/incomplete layouts. Container/array padding and DB bounds are checked across the whole tree. Manual addresses never redirect the theoretical cursor or receive batch overwrite; their reasons survive. The DB length changes only when the complete non-manual set is confirmed with no manual address. Actual PLC addresses require separate site verification.

The handwritten [multi-DB fixtures and prior layout oracle](src-tauri/tests/fixtures/source-import-multi-db/README.md) document the limited profile. New optional JSON lineage/binding fields require no DDL and old v1 JSON reads do not write back. This new-binary/old-data compatibility does not promise old binaries can read new metadata; downgrade requires separate proof. Source versions still count toward 128 sources and the 16MiB configuration/write budget; no unselected source is deleted to make room.

DAA machine identity is the opaque `point.id` (including sample dictionaries); `sourcePath` retains the original PLC path, including Chinese, and `name` is an editable display label. The older YAML tool uses its `name` as a runtime key, so its ASCII/address fallback is not transplanted here. Newly imported addresses are null; any future human-readable ASCII integration key requires a separate contract.
