# AIIS Data Acquisition Agent

[中文](README.zh-CN.md)

Source: CA freeze receipt. Lifecycle belongs to [AW PLAN](../PLAN.md); scope and current evidence are in root [ARCH-AW-001](../../plans/ARCH-AW-001-agent-foundation/tasks.md).

DAA retains the old raw/latest snapshot implementation; new AW fact/configuration APIs are not connected.

```bash
pnpm install --frozen-lockfile
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo test --manifest-path src-tauri/Cargo.toml --locked
pnpm tauri dev
```

See [AW README](../README.md) for identity, ports, config discovery and isolated profiles. External I/O defaults off. Local engineering verification does not establish real PLC/DB/Target operation or a business chain. SQLite configuration/mapping storage requires a later spec.
