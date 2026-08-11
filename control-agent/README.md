# AIIS ICS Control Agent

`control-agent/` is the optional Rust/Tauri field runtime and local operations
console paired with the AIIS ICS Architecture backend. It owns PLC collection
and the backend-owned raw/latest snapshot contract; it is not a second web
backend and it does not replace the backend module registry.

## Public baseline

- `src/` contains the Tauri console and module-local translations.
- `src-tauri/` contains the Rust runtime, read-only PLC contract adapters and
  the explicit database snapshot writer.
- `config/plc_points.yaml` and `config/plc_snapshot_policy.yaml` are sanitized
  shape examples only.
- `.env.example` disables PLC, database and endpoint-probe gates by default.

The default configuration contains no customer endpoint, point table, secret,
or database URL. A site must provide a separately reviewed configuration before
enabling an external I/O gate. PostgreSQL/MSSQL selection, YAML upload and a
settings screen are future work under `CA-CONFIG-001`; they are not part of this
baseline.

## Local checks

```bash
pnpm install
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo test --manifest-path src-tauri/Cargo.toml
```

The commands above are local source checks. They do not start Docker, connect to
a real PLC or database, or publish an artifact. Build output and dependency
directories stay untracked.

## Runtime boundary

The backend may expose collector and snapshot status through its Core API. PLC
reads remain in the resident Control Agent. Database writes require explicit
local gates and a reviewed site contract. No web request is allowed to become a
PLC polling loop.
