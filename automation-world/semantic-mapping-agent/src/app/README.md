# SMA app modules

[中文](README.zh-CN.md)

`connection` maintains the saved Backend address and OpenAPI catalog. `http-mapping` exposes the GET source and point pages, target and mapping operations, and independent collection and reporting controls. `configuration-management` owns the local file-exchange surface. `App.vue` assembles the eight workspace pages and their localized navigation.

Configuration editors retain the revision they loaded. A save or confirmed import must match that revision. The `twin-facts/api/localConfiguration.ts` facade delegates to native Rust configuration commands. HTTP source tests, snapshots and POST previews use the HTTP mapping commands. The saved request and source versions stay native until the operator confirms the preview. The legacy read-only acquisition adapters remain available for acquisition options and history inspection.

Use the static CU UI entry points and the SMA table-width preferences in `src/console/tableWidths.ts`. UI preferences and latest facts are separate from configuration exchange. User-facing strings use matching English and Chinese keys.
