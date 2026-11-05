# Automation World

[中文](README.zh-CN.md)

AW owns the field-acquisition and semantic-mapping desktop engineering surfaces.

| App | Current responsibility | Maintenance direction |
| --- | --- | --- |
| [CA](control-agent/README.md) | Relocated Control Agent, retaining the raw/latest database-snapshot compatibility contract | Frozen after relocation validation; exact provenance is in the task receipt |
| [DAA](data-acquisition-agent/README.md) | SQLite-owned configuration, acquisition, decoding and diagnostics; inherited headless retired | Continuing acquisition development; new AW APIs are not connected |
| [SMA](semantic-mapping-agent/README.md) | Read-only HTTP facts, API materials, targets, value rules, mapping preview and runtime diagnostics | Consumes CU public UI source; requires compatible Backend HTTP contracts; delivery status belongs to the SMA PLAN |

CA freezing does not stop an existing deployment or switch the production chain. Original DTB TSS remains intact. New apps do not depend on CA/TSS checkout or dependency directories, and copies are not continuously overwritten. SMA excludes customer device/scene pages, SQL/legacy Projection IPC and cross-repository help generation.

## Independent projects and configuration

In each app directory run `pnpm install --frozen-lockfile`, `pnpm build`, `cargo test --manifest-path src-tauri/Cargo.toml --locked`, and `pnpm tauri dev`. DAA also retains `pnpm tauri:dev` with its optional inherited driver; runtime gates still control external access. Rebuild dependencies and targets after relocating source; cached absolute paths are not startup evidence.

| App | Identifier | Dev / preview | Env / localStorage |
| --- | --- | --- | --- |
| CA | com.aiis.ics.controlagent | 15190 / 14190 | Original CONTROL_AGENT_* / original keys |
| DAA | com.aiis.aw.dataacquisitionagent | 15191 / 14191 | DAA_* / daa.* |
| SMA | com.aiis.aw.semanticmappingagent | 15192 / 14192 | SMA_* / sma.* |

DAA/SMA read only their own root `.env` or explicit absolute `DAA_ENV_FILE` / `SMA_ENV_FILE`; they never discover cwd/parent/root env files. Relative DAA YAML paths anchor to its own root; logs/outputs use the independent identifier's local data directory. SMA startup JSON uses its own app-data. Explicit absolute `DAA_PROFILE_DIR` / `SMA_PROFILE_DIR` support isolated validation. Real config, logs and output remain untracked. SMA starts with an empty Backend and HTTP off. Simulation/Mapping auto-start defaults false and does not migrate CA/TSS preferences. DAA YAML is only a one-time source; DAA SQLite configuration and local history are described below. JSON retains the existing SMA technical startup-preference duties; SMA mapping storage remains outside this change.

## Evolution and evidence

This is the S2 engineering prerequisite. S1 configuration/fact/mapping-receipt and business API contracts, new AW fact upload, the business chain, the later shared UI/integration targets require independent tasks. Startup does not establish those integrations. See [PLAN](PLAN.md) and the unique root [ARCH-AW-001 bundle](../plans/ARCH-AW-001-agent-foundation/spec.md).

Use `pnpm preview --strictPort` for CA preview so port 14190 conflicts fail while preserving frozen CA source. DAA/SMA dev/preview enforce strictPort in their own Vite configuration.

DAA enters the SQLite application with ordinary `pnpm tauri dev`. [Final acceptance on 2026-10-30](data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) completes Stage B within this controlled DS joint-test scope. DAA-003 one-time YAML migration is historical; DAA-007 retires ordinary migration, keeps empty profiles empty and preserves private receipts/history. UI + SQLite own business configuration. See the [DAA README](data-acquisition-agent/README.md) and [joint guide](data-acquisition-agent/JOINT_TEST_GUIDE.md). Historical evidence limits and unexplained actions remain tracked; Stage C, automatic-start policy, Backend/SMA and real-field work are separate.
