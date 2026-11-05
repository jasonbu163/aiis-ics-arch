# AIIS Semantic Mapping Agent

[中文](README.zh-CN.md)

Source: DTB TSS a87c107c10e8d9d9d3e389e357b50d203d2aebf7. Current delivery gates belong to the [SMA PLAN](PLAN.md) and the [SMA-004 bundle](plans/SMA-004-local-configuration/spec.md); the [AW PLAN](../PLAN.md) tracks cross-project dependencies. Software checks, independent QA and Human Owner acceptance are separate facts.

SMA owns local connection, OpenAPI catalog/selection, target APIs, value rules, mappings and minimal read-only source metadata. Fact authoring, Simulation, built-in Help, customer pages and legacy SQL IPC remain retired. This stage provides configuration maintenance and pure previews. **Normal manual delivery, start, resume and auto-start return `SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE` before HTTP-client construction, remote configuration reads or spawning**, including when HTTP is enabled or old startup preferences are true. Pause, stop and status remain available.

## Configuration and files

Rust is the only business-configuration writer. `<SMA profile>/configuration.sqlite3` uses SMA-owned bundled rusqlite `=0.32.1`, schema v1 and one complete singleton document with monotonic revision and Shanghai `updatedAt`. A write validates the merged graph and compares the observed revision in one short transaction. A stale form or preview requires reload/preview again. Referenced materials, targets and rules cannot be deleted; invalidating a mapping rejects the whole change. Disabled configuration retains its references.

The profile is the explicit absolute `SMA_PROFILE_DIR`, or the application's own app-data directory for an authorized normal adoption. An invalid explicit override, corrupt database or unknown schema fails without a default-directory fallback or delete/rebuild. This task authorizes disposable-profile verification only; adoption or migration of real/default profiles needs a separate decision. No TSS configuration or old localStorage connection is automatically imported or used as fallback. An environment Backend URL is not saved configuration.

Open **Connection** to explicitly save the one Backend address. Saving sends nothing. **API Materials** first loads the local catalog and selection. Import a local OpenAPI JSON file, review the candidate operations, explicitly apply the catalog, then save selection. Network catalog refresh is explicit and uses the existing HTTP gate; catalog changes do not replace derived targets. Targets can also be maintained manually. The existing JSON wrappers and single-sheet XLSX templates for `targetApis`, `mappingValueRules` and `mappings` remain supported, including legacy nine-column targets defaulting to POST. Preview never writes; apply uses the same content and revision. Duplicate keys, invalid references, formulas, macros and limits reject the whole import.

The existing configuration workspaces provide complete JSON backup and restore. Backups use `format: aiis.sma.configuration`, `schemaVersion: 1` and a complete `document`. Restore previews whole-document replacements and deletions and requires explicit confirmation; it does not roll back local revision. It excludes `.env`, HTTP gate, UI/startup preferences, fact values and runtime records. Use JSON export rather than copying an open SQLite file. Input payloads and the actual UTF-8 pretty-printed backup envelope are limited to 10 MiB; each final collection is limited to 10,000 items, including after repeated small saves.

**Source Facts** remains an explicitly gated read-only HTTP inspector. Offline bindings use `sourceKey + factName`; unknown references can be saved as unverified without inventing facts or values. Minimal source metadata records its evidence source and original definition version. Read values remain in session memory. The editor draft preview is separate from the saved-row preview: saved preview asks Rust to read the current local revision and reuse the existing pure mapping algorithm without claims or delivery. Missing required facts produce diagnostics and no complete request. Saving does not report target business success.

`runtime-startup.json` remains schema v1 and independent of business revision. Loading preserves bytes; explicit preference saving preserves inert legacy sections. New profiles default false. These preferences cannot authorize delivery in this stage. Non-terminal runtime state rejects all configuration writes until an explicit stop reaches a terminal state. Old HTTP/lease/audit algorithms remain available only as explicit compatibility fixture entrypoints, with their regressions; the application has no legacy execution-mode switch.

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

Ordinary startup stays `pnpm tauri dev`, identity `com.aiis.aw.semanticmappingagent`, dev/preview strict ports 15192/14192. Before disposable runtime verification provide absolute task-owned `SMA_ENV_FILE` / `SMA_PROFILE_DIR`, empty `SMA_BACKEND_BASE_URL` and `SMA_HTTP_ENABLED=false`. The profile isolates Rust files, **not WKWebView storage**; native tests must use a supported temporary incognito overlay. Such a test does not prove native cross-process UI-preference persistence.

SMA compiles CU's public `src/ui/index.ts` and `src/ui/styles/index.css` with its own dependencies. Built applications need no CU process or CU node_modules. Five navigation groups and seven stable leaves remain. Theme/language and the themed Element Plus overlay preserve mounted workspaces. UI preferences stay under `sma.*` localStorage and are excluded from business backups. Ordinary tables share stable-ID column resizing, persistence and per-table reset; special action/selection columns may stay fixed. Calendar display uses Asia/Shanghai to seconds while retaining underlying precision and showing a missing state for absent/ambiguous time.

A configurable GET source, local delivery runtime, history/outbox, reliable recovery, DAA/Backend end-to-end integration and real operation remain later approved stages. See the [detailed design](../../docs/AIIS_SMA_Detailed_Design.md); it is not evidence that these stages have shipped.
