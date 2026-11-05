# SMA app modules

[中文](README.zh-CN.md)

`connection` owns the one local Backend connection and explicit gated OpenAPI inspection. `twin-facts` owns read-only source inspection, local materials/targets/rules/mappings, file exchange and runtime diagnostics. Fact production, Simulation and Help remain retired. The root registry and locale merge are explicit; there is no automatic menu-generation claim.

Business flow is component → module store → `twin-facts/api/localConfiguration.ts` → thin Tauri commands → Rust service/domain → SMA-owned SQLite singleton. UI caches are observed snapshots and unsaved forms. Editors retain their loaded revision; resource/file previews retain their normalized content and revision. Save must not fetch a newer revision to conceal a stale draft. Historical `*FromBackend` configuration facade names now delegate only to local IPC. Only explicit source-fact/OpenAPI refresh performs gated HTTP, with no TSS configuration/audit fallback.

The material workspace supports local OpenAPI JSON preview/apply before selection. Existing resource JSON/XLSX helpers stay pure file adapters. Whole-document backup/restore belongs to the existing configuration operations area, with visible replacement/deletion review and confirmation. Saved mapping preview uses Rust's current saved revision and never receives editor bindings. Source identity is `sourceKey + factName`; minimal metadata records evidence without values. Missing values remain missing.

To add a view, create module-owned components and symmetric locale keys, then explicitly update manifest/registry and locale assembly. When copying, rename owner/id/imports/keys without carrying customer resources. No permanent mock API is shipped. Run `pnpm check/test/build` and matching Rust regressions. Module delivery gates belong to the SMA PLAN and task bundle.

`store/mappingStartup.ts` preserves Mapping-only technical preferences and inert v1 disk compatibility. Native admission rejects all normal delivery in this stage. `src/console/tableWidths.ts` owns stable-ID local column preferences and per-table reset; `src/console/time.ts` formats explicit calendar timestamps in Shanghai. Theme, language and widths never change business revision or enter backups.

CU composition stays in App.vue; components import only public `@aw-ui`. Keep the themed overlay host available before mounting ElDialog. Native SQLite verification, in-memory IPC tests and browser UI checks are separate evidence layers.
