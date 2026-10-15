# SMA app modules

[中文](README.zh-CN.md)

connection owns generic Backend bootstrap/OpenAPI; twin-facts owns HTTP facts, materials, targets, value rules, mapping and Simulation helpers; help reads local bilingual guidance only. Registry assembly and root locale merging are explicit, without automatic menu/route generation claims.

Add views/components and symmetric locale keys in the owning module, then explicitly update manifests/registry and locale assembly. When copying a module, rename owner/id/imports/keys without carrying customer resources or changing backend contracts. API facades own gated external calls; do not add a permanent mock API. Run pnpm build, pnpm test and relevant Rust regressions. AW PLAN owns the lifecycle.
