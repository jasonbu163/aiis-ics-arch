# Data Acquisition Agent code index

This index identifies the DAA catalog-import and catalog-export slices and their related boundaries. The [README](README.md) and [local-store guide](src-tauri/src/infrastructure/local_store/README.md) describe the wider application.

| File | Responsibility |
| --- | --- |
| [plc_catalog.rs](src-tauri/src/domain/plc_catalog.rs) | Strict single-PLC JSON parsing, complete S7 layout checks and catalog source / point binding verification. |
| [catalog_import.rs](src-tauri/src/services/catalog_import.rs) | One-new-PLC planning, source SHA and target / ETag-bound preview and confirmation. |
| [catalog_export.rs service](src-tauri/src/services/catalog_export.rs) | Saved-draft / active-revision PLC previews, source and binding validation, and atomic non-overwriting file export. |
| [local_configuration.rs](src-tauri/src/domain/local_configuration.rs) | Local configuration and runtime eligibility, including the validated catalog branch. |
| [local_configuration.rs service](src-tauri/src/services/local_configuration.rs) | Draft CAS and protection of catalog-derived facts against ordinary edits. |
| [local_point_naming.rs](src-tauri/src/services/local_point_naming.rs) | Existing name-preview flow, with unchanged catalog addresses and restricted catalog edits. |
| [configuration.rs](src-tauri/src/infrastructure/local_store/configuration.rs) | Configuration and archive transactions, historical identity checks and catalog archive verification. |
| [local_acquisition.rs](src-tauri/src/commands/local_acquisition.rs) | Named local Tauri IPC adapters; no direct database or device access. |
| [catalog_export.rs command](src-tauri/src/commands/catalog_export.rs) | Export IPC adapters and native directory selection bound to the preview token. |
| [CatalogImportDialog.vue](src/app/plc/components/CatalogImportDialog.vue) | File selection, complete catalog preview and explicit target confirmation. |
| [CatalogExportDialog.vue](src/app/plc/components/CatalogExportDialog.vue) | Saved-version and PLC selection, export preview, directory confirmation and per-instance results. |
| [useLocalAcquisitionConsole.ts](src/console/composables/useLocalAcquisitionConsole.ts) | Shared draft / preview state, local IPC and unknown-result recovery. |
| [catalog_import_tests.rs](src-tauri/src/infrastructure/local_store/catalog_import_tests.rs) | Synthetic SQLite import, CAS, conflict, rollback, activation and editor checks. |
| [catalog_export_tests.rs](src-tauri/src/infrastructure/local_store/catalog_export_tests.rs) | Synthetic SQLite export, conflict, active-version and historical sample / queue isolation checks. |
| [local_delivery_tests.rs](src-tauri/src/services/local_delivery_tests.rs) | Captured simulated v2 transport and existing delivery regressions; no real POST. |
| [plc-catalog-import.test.mjs](tests/plc-catalog-import.test.mjs) | In-memory frontend state and bilingual key checks, without a native app. |
| [plc-catalog-export.test.mjs](tests/plc-catalog-export.test.mjs) | Export-dialog state, directory cancellation and per-instance results with in-memory IPC. |
