# Automation World

[中文](README.zh-CN.md)

AW owns the field-acquisition and semantic-mapping desktop engineering surfaces.

| App | Current responsibility | Maintenance direction |
| --- | --- | --- |
| [CA](control-agent/README.md) | Relocated Control Agent, retaining the raw/latest database-snapshot compatibility contract | Frozen after relocation validation; exact provenance is in the task receipt |
| [DAA](data-acquisition-agent/README.md) | Acquisition, decoding, diagnostics and the existing headless entry inherited from frozen CA | Continuing acquisition development; new AW APIs are not connected |
| [SMA](semantic-mapping-agent/README.md) | Filtered TSS HTTP facts, API materials, targets, value rules, mapping preview and runtime diagnostics | Retained applicable TSS UI; requires compatible Backend HTTP contracts |

CA freezing does not stop an existing deployment or switch the production chain. Original DTB TSS remains intact. New apps do not depend on CA/TSS checkout or dependency directories, and copies are not continuously overwritten. SMA excludes customer device/scene pages, SQL/legacy Projection IPC and cross-repository help generation.

## Independent projects and configuration

In each app directory run `pnpm install --frozen-lockfile`, `pnpm build`, `cargo test --manifest-path src-tauri/Cargo.toml --locked`, and `pnpm tauri dev`. DAA also retains `pnpm tauri:dev` with its optional inherited driver; runtime gates still control external access. Rebuild dependencies and targets after relocating source; cached absolute paths are not startup evidence.

| App | Identifier | Dev / preview | Env / localStorage |
| --- | --- | --- | --- |
| CA | com.aiis.ics.controlagent | 15190 / 14190 | Original CONTROL_AGENT_* / original keys |
| DAA | com.aiis.aw.dataacquisitionagent | 15191 / 14191 | DAA_* / daa.* |
| SMA | com.aiis.aw.semanticmappingagent | 15192 / 14192 | SMA_* / sma.* |

DAA/SMA read only their own root `.env` or explicit absolute `DAA_ENV_FILE` / `SMA_ENV_FILE`; they never discover cwd/parent/root env files. Relative DAA YAML paths anchor to its own root; logs/outputs use the independent identifier's local data directory. SMA startup JSON uses its own app-data. Explicit absolute `DAA_PROFILE_DIR` / `SMA_PROFILE_DIR` support isolated validation. Real config, logs and output remain untracked. SMA starts with an empty Backend and HTTP off. Simulation/Mapping auto-start defaults false and does not migrate CA/TSS preferences. YAML remains sanitized runtime configuration; JSON retains technical startup-preference duties. SQLite configuration/mapping storage is not included.

## Evolution and evidence

This is the S2 engineering prerequisite. S1 configuration/fact/mapping-receipt and business API contracts, new AW fact upload, the business chain, a CA-style shared UI and SQLite configuration storage require later independent tasks. Startup does not establish those integrations. See [PLAN](PLAN.md) and the unique root [ARCH-AW-001 bundle](../plans/ARCH-AW-001-agent-foundation/spec.md).

Use `pnpm preview --strictPort` for CA preview so port 14190 conflicts fail while preserving frozen CA source. DAA/SMA dev/preview enforce strictPort in their own Vite configuration.
