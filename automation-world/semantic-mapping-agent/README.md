# AIIS Semantic Mapping Agent

[中文](README.zh-CN.md)

Source: DTB TSS a87c107c10e8d9d9d3e389e357b50d203d2aebf7. Current delivery gates belong to the [SMA PLAN](PLAN.md) and the [SMA-004 bundle](plans/SMA-004-local-configuration/spec.md); the [AW PLAN](../PLAN.md) tracks cross-project dependencies. Software checks, independent QA and Human Owner acceptance are separate facts.

SMA owns local connection, OpenAPI catalog/selection, target APIs, value rules, mappings and minimal read-only source metadata. Fact authoring, Simulation, built-in Help, customer pages and legacy SQL IPC remain retired. Local configuration and pure preview remain available. The Fact Table includes an explicit manual acquisition loopback. **The older mapping execution entry points for manual delivery, start, resume and auto-start return `SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE` before HTTP-client construction, remote configuration reads or spawning**, including when HTTP is enabled or old startup preferences are true. Pause, stop and status remain available.

## Configuration and files

Rust is the only business-configuration writer. `<SMA profile>/configuration.sqlite3` uses SMA-owned bundled rusqlite `=0.32.1`, schema v1 and one complete singleton document with monotonic revision and Shanghai `updatedAt`. A write validates the merged graph and compares the observed revision in one short transaction. A stale form or preview requires reload/preview again. Referenced materials, targets and rules cannot be deleted; invalidating a mapping rejects the whole change. Disabled configuration retains its references.

A nonblank process `SMA_PROFILE_DIR` takes precedence over the value in the selected SMA `.env`. When both are blank or unset, SMA uses its existing app-data directory. The profile contains `configuration.sqlite3`, `logs/` and `runtime-startup.json`. An invalid selection, corrupt database or unknown schema stops without falling back to another directory or rebuilding the database. No TSS configuration or old localStorage connection is automatically imported. An environment Backend URL is not saved configuration.

Open **Connection** to explicitly save the one Backend address. Saving sends nothing. **API Materials** first loads the local catalog and selection. Import a local OpenAPI JSON file, review the candidate operations, explicitly apply the catalog, then save selection. Network catalog refresh is explicit and uses the existing HTTP gate; catalog changes do not replace derived targets. Targets can also be maintained manually. The existing JSON wrappers and single-sheet XLSX templates for `targetApis`, `mappingValueRules` and `mappings` remain supported, including legacy nine-column targets defaulting to POST. Preview never writes; apply uses the same content and revision. Duplicate keys, invalid references, formulas, macros and limits reject the whole import.

The existing configuration workspaces provide complete JSON backup and restore. Backups use `format: aiis.sma.configuration`, `schemaVersion: 1` and a complete `document`. Restore previews whole-document replacements and deletions and requires explicit confirmation; it does not roll back local revision. It excludes `.env`, HTTP gate, UI/startup preferences, fact values and runtime records. Use JSON export rather than copying an open SQLite file. Input payloads and the actual UTF-8 pretty-printed backup envelope are limited to 10 MiB; each final collection is limited to 10,000 items, including after repeated small saves.

**Source Facts** remains an explicitly gated read-only HTTP inspector. Offline bindings use `sourceKey + factName`; unknown references can be saved as unverified without inventing facts or values. Minimal source metadata records its evidence source and original definition version. Read values remain in session memory. The editor draft preview is separate from the saved-row preview: saved preview asks Rust to read the current local revision and reuse the existing pure mapping algorithm without claims or delivery. Missing required facts produce diagnostics and no complete request. Saving does not report target business success.

`runtime-startup.json` remains schema v1 and independent of business revision. Loading preserves bytes; explicit preference saving preserves inert legacy sections. New profiles default false. These preferences cannot authorize delivery in this stage. Non-terminal runtime state rejects all configuration writes until an explicit stop reaches a terminal state. Old HTTP/lease/audit algorithms remain available only as explicit compatibility fixture entrypoints, with their regressions; the application has no legacy execution-mode switch.

## Manual acquisition loopback against dev

1. Enable `SMA_HTTP_ENABLED=true` in the SMA development profile and launch with `pnpm tauri dev`. Save the already-running backend in **Connection**. The current local example is `http://127.0.0.1:8000`. In **API Materials**, select and save `GET /api/v1/acquisition-data/latest`.
2. In **Fact Table → Acquisition API loopback** select that material, load the PLC and DB choices, and load the available points. The current dev external source example is `PLC-BE012-DEV-441247C3`, DB `21`. Select one, several, or all points and click **Test GET**.
3. Find one sample in **History and source sample**. For known history ID `1`, query `2026-11-10 21:55:00` to `2026-11-10 22:00:00` in Shanghai time and select `be012-dev-441247c3-102`. Latest points may span samples. The preview uses one history detail only.
4. Use a registered external test destination and dedicated DB. The existing manual-test example is the same PLC with DB `61421`, instance `be012-dev-smoke-441247c3`, and generation `be012-dev-gen-441247c3`. You can rename point IDs and names or add optional group and configuration revision constants. Enter a sequence that you have verified is unused in the target stream. Save the configuration and review the URL, sample identity, sequence, and values in **Preview POST request**.
5. The operator clicks **Test POST** once, checks the matching HTTP `200` and `committed/created` or `committed/duplicate` receipt, and clicks **Read back target sample**. On an unknown outcome, check target history or retry the identical request within that session. After closing the app, reconcile using the sample ID and original observation time. Values, previews, sequences, and receipts stay out of local configuration and backups.

This entry uses the existing development acquisition API without a token. Old v1 SQLite documents and backups can still be read. Restore a new backup containing `acquisitionLoopback` only in a version that supports the field. Older versions reject unknown fields.

## Development and UI

```bash
pnpm install --frozen-lockfile
pnpm check
pnpm test
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo test --manifest-path src-tauri/Cargo.toml --locked
pnpm tauri dev
```

For source development, inspect the SMA project's `.env` if it already exists. If absent, copy `.env.example` to `.env`. To select a project-local profile, use this assignment.

```dotenv
SMA_PROFILE_DIR=./.local/dev
```

`.local/dev` and `./.local/dev` both select the `.local/dev` directory under the selected `.env` directory, independently of the terminal's current directory. To select an existing absolute profile, replace the following example with that directory's path.

```dotenv
SMA_PROFILE_DIR=/absolute/path/to/sma-profile
```

The optional process `SMA_ENV_FILE` selects a different absolute, readable regular file. Relative profile values from either the process or that file use its parent directory. Profile paths reject `..`, `~`, variables, placeholders, existing symlinks and non-directory components. Check the reported key and reason if startup rejects the selection. A previously exported nonblank process `SMA_PROFILE_DIR` overrides the file.

Ordinary startup stays `pnpm tauri dev`, identity `com.aiis.aw.semanticmappingagent`, dev/preview strict ports 15192/14192. Before disposable runtime verification provide task-owned `SMA_ENV_FILE` / `SMA_PROFILE_DIR`, empty `SMA_BACKEND_BASE_URL` and `SMA_HTTP_ENABLED=false`. The profile isolates Rust files. WKWebView storage is shared across application launches, so native tests use a supported temporary incognito overlay. That overlay does not establish native cross-process UI-preference persistence.

SMA compiles CU's public `src/ui/index.ts` and `src/ui/styles/index.css` with its own dependencies. Built applications need no CU process or CU node_modules. Five navigation groups and seven stable leaves remain. Theme/language and the themed Element Plus overlay preserve mounted workspaces. UI preferences stay under `sma.*` localStorage and are excluded from business backups. Ordinary tables share stable-ID column resizing, persistence and per-table reset; special action/selection columns may stay fixed. Calendar display uses Asia/Shanghai to seconds while retaining underlying precision and showing a missing state for absent/ambiguous time.

The seven workspace pages use CU compact typography and icons for both navigation levels. Card headers carry main actions and contextual help, the header shows one complete priority status and reveals the full list on hover or activation when more statuses exist, and refresh stays last when present, and table operations use 24 px buttons. Local configuration remains shared by API Materials, Target API Configuration, Value Rules and Mapping Configuration. The card body shows the last saved time as a read-only field.

Continuous delivery, reliable continuation, restart recovery and real business targets remain later stages. See the [detailed design](../../docs/AIIS_SMA_Detailed_Design.md); it is not evidence that these stages have shipped.
