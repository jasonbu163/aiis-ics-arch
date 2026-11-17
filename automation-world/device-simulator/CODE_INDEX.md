# Device Simulator code index

This index covers the bounded DS editing, version-management, table preference and calendar-time helpers and self-checks. Existing runtime and IPC ownership remain documented in [README](README.md).

| File | Responsibility |
| --- | --- |
| [policyEditing.ts](src/app/simulator/policyEditing.ts) | Current draft inheritance/type display, stable point selection, scalar parsing, three-state candidate prevalidation and confirmation invalidation. No rule execution or IPC. |
| [PolicyBatchDialog.vue](src/app/simulator/components/PolicyBatchDialog.vue) | Tri-state form, explicit mode links, per-point impact preview, cancellation and one local-draft commit. |
| [policy-editing.test.mjs](tests/policy-editing.test.mjs) | Seven minimal Node assertions through existing TypeScript transpilation, without GUI/profile/protocol operations. |
| [time.ts](src/console/time.ts) | Explicit-offset calendar values formatted once in Asia/Shanghai to seconds; original precision and monotonic counters remain separate. |
| [clock.rs](runtime/src/infrastructure/clock.rs) | Existing monotonic scheduling clock plus Shanghai RFC3339 timestamps for logs and recorded point updates; no protocol timing conversion. |
| [revisions.ts](src/console/revisions.ts) | Actual saved-sequence labels with honest short-ID fallback for older revisions outside the current list. |
| [RevisionStatus.vue](src/components/console/RevisionStatus.vue) | Compact version/alignment summary; question-mark help retains saved/selected/loaded identities. |
| [ConsoleFieldHelp.vue](src/components/console/ConsoleFieldHelp.vue) | Element Plus question-mark help for hover/focus, translated labels and existing theme tokens. |
| [presentation.test.mjs](tests/presentation.test.mjs) | Three focused date/sequence display checks, without GUI/profile/protocol operations. |
| [ConsoleDataTable.vue](src/components/console/ConsoleDataTable.vue) | Native Element Plus page and version/preview tables: original column slots/events, scoped width restoration/reset, CU density, overflow and scrolling. |
| [tableWidths.ts](src/console/tableWidths.ts) | Local-only stable table/field width keys, minimum validation, obsolete-field fallback and per-table reset; no business storage or IPC. |
| [table-widths.test.mjs](tests/table-widths.test.mjs) | Four focused width persistence, schema fallback, isolated reset and unavailable-storage checks using synthetic Storage. |
| [versions.rs](runtime/src/services/versions.rs) | Whole-workspace list, all-instance usage protection, rollback-only release acknowledgment, single/batch deletion and latest5 plus protected retention. |
| [transactions.rs](runtime/src/infrastructure/config_store/transactions.rs) | Draft CAS/publication, atomic CAS-checked rollback release plus batch deletion, and preserving previous on same-version reload, without schema migration. |
| [RevisionOperationDialog.vue](src/app/simulator/components/RevisionOperationDialog.vue) | Shared publication/single/batch deletion list, all rollback instances and explicit release acknowledgment; no automatic load/start. |
| [useDeviceSimulator.ts](src/console/composables/useDeviceSimulator.ts) | Separate editor/runtime state; unknown draft-save freeze, non-destructive readback and ETag recheck; revision refresh and idempotent preview release. |
| [version-previews.test.mjs](tests/version-previews.test.mjs) | Two incremental Vue-state checks for preserving unsaved edits/CAS, late-list rejection and cancellation refresh without native windows or profiles. |
| [versions.rs tests](runtime/tests/versions.rs) | Five real-SQLite checks for draft/reopen/dedup, usage/preview protection, confirmed batch release/deletion, repeated load, rollback and unknown receipts using new synthetic profiles. |
| [point_display_names.rs](runtime/tests/point_display_names.rs) | Synthetic bilingual configuration, reimport and history checks plus a controlled committed-save unknown-receipt fixture. |
| [point-display-names.test.mjs](tests/point-display-names.test.mjs) | In-memory Vue editor, point display and fault-receipt recovery checks, including local edits, ETag races and independent runtime outcomes. |
| [plc_catalog.rs](runtime/src/domain/plc_catalog.rs) | Validate the complete saved-instance exchange declaration, including disabled DBs/points, source confirmation, bilingual text and S7 layout. |
| [catalog_export.rs](runtime/src/services/catalog_export.rs) | Short-lived saved-revision previews, native-selected directory binding and individually reported exclusive file creation. |
| [catalog_export.rs bridge](src-tauri/src/commands/catalog_export.rs) | Thin Tauri commands and native directory selection; the frontend supplies no filesystem path. |
| [CatalogExportDialog.vue](src/app/simulator/components/CatalogExportDialog.vue) | Revision, instance, client target and complete point preview, native directory choice and individual export receipts. |
| [plc_catalog_export.rs tests](runtime/tests/plc_catalog_export.rs) | Synthetic SQLite, saved-byte hash, disabled points, conflicts, stale revisions and concurrent confirmation checks. |
| [plc-catalog-export.test.mjs](tests/plc-catalog-export.test.mjs) | In-memory Vue checks for saved revision, explicit confirmations, cancellation and unknown receipt handling. |
