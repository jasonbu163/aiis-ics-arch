# Control Agent Plan

## Current baseline

The Control Agent is an optional companion runtime for AIIS ICS Architecture.
The current source baseline keeps the Tauri console, the Rust supervisor, the
read-only PLC point/policy adapters, and the backend-owned snapshot contract.

The public examples are sanitized and all external gates are disabled. No
production PLC, database, customer configuration, or build artifact belongs in
this repository.

## Boundaries

1. PLC reads belong to the resident Rust runtime.
2. Snapshot writes require explicit local database gates and a reviewed site
   contract.
3. The backend remains the Web/API boundary and owns snapshot tables.
4. Settings for database engines and YAML upload are deferred to `CA-CONFIG-001`.
5. Release packaging and deployment are separate from this source baseline.

## Verification entry points

Run `pnpm build`, `cargo fmt --manifest-path src-tauri/Cargo.toml --check`, and
`cargo test --manifest-path src-tauri/Cargo.toml` in an environment with the
declared dependencies. These checks must remain no-PLC/no-database checks.
