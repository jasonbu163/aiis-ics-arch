# Device Simulator code index

This index covers the bounded DS editing, table preference and calendar-time helpers and self-checks. Existing runtime and IPC ownership remain documented in [README](README.md).

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
| [ConsoleDataTable.vue](src/components/console/ConsoleDataTable.vue) | All 13 native Element Plus table surfaces: original column slots/events, scoped width restoration/reset, CU density, overflow and scrolling. |
| [tableWidths.ts](src/console/tableWidths.ts) | Local-only stable table/field width keys, minimum validation, obsolete-field fallback and per-table reset; no business storage or IPC. |
| [table-widths.test.mjs](tests/table-widths.test.mjs) | Four focused width persistence, schema fallback, isolated reset and unavailable-storage checks using synthetic Storage. |
