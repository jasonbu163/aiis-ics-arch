# AIIS Semantic Mapping Agent

[中文](README.zh-CN.md)

Source: DTB TSS a87c107c10e8d9d9d3e389e357b50d203d2aebf7. Lifecycle belongs to [AW PLAN](../PLAN.md); scope and current evidence are in root [ARCH-AW-001](../../plans/ARCH-AW-001-agent-foundation/tasks.md).

SMA retains generic HTTP facts/materials/targets/mapping logic and the applicable TSS UI. Customer/SQL/legacy IPC and cross-DTB help generation are excluded. Existing /api/tss/v1 and collection-facts HTTP contracts remain unchanged; no backend is bundled.

```bash
pnpm install --frozen-lockfile
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo test --manifest-path src-tauri/Cargo.toml --locked
pnpm tauri dev
```

See [AW README](../README.md) for identity, ports, config discovery and isolated profiles. External I/O defaults off. Local engineering verification does not establish real PLC/DB/Target operation or a business chain. SQLite configuration/mapping storage requires a later spec.
