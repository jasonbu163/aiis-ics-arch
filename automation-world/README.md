# Automation World

[中文](README.zh-CN.md)

AW owns the field-acquisition and semantic-mapping desktop engineering surfaces.

| App | Current responsibility | Maintenance direction |
| --- | --- | --- |
| [CA](control-agent/README.md) | Relocated Control Agent, retaining the raw/latest database-snapshot compatibility contract | Frozen after relocation validation; exact provenance is in the task receipt |
| [DAA](data-acquisition-agent/README.md) | SQLite-owned configuration, acquisition, decoding and diagnostics; inherited headless retired | Continuing acquisition development; new AW APIs are not connected |
| [SMA](semantic-mapping-agent/README.md) | local connection/material/target/rule/mapping configuration and pure previews, plus gated read-only facts inspection | Consumes CU shared source; normal delivery is disabled in the current local-configuration stage |

CA freezing does not stop an existing deployment or switch the production chain. Original DTB TSS remains intact. New apps do not depend on CA/TSS checkout or dependency directories, and copies are not continuously overwritten. SMA excludes customer device/scene pages, SQL/legacy Projection IPC and cross-repository help generation.

## Independent projects and configuration

In each app directory run `pnpm install --frozen-lockfile`, `pnpm build`, `cargo test --manifest-path src-tauri/Cargo.toml --locked`, and `pnpm tauri dev`. Ordinary `pnpm tauri dev` obtains DAA driver features from its Tauri configuration; startup remains stopped. Rebuild dependencies and targets after relocating source; cached absolute paths are not startup evidence.

| App | Identifier | Dev / preview | Env / localStorage |
| --- | --- | --- | --- |
| CA | com.aiis.ics.controlagent | 15190 / 14190 | Original CONTROL_AGENT_* / original keys |
| DAA | com.aiis.aw.dataacquisitionagent | 15191 / 14191 | DAA_* / daa.* |
| SMA | com.aiis.aw.semanticmappingagent | 15192 / 14192 | SMA_* / sma.* |

DAA/SMA read only their application-root `.env` or explicit absolute `DAA_ENV_FILE` / `SMA_ENV_FILE`, without searching parent directories. Absolute `DAA_PROFILE_DIR` / `SMA_PROFILE_DIR` select independent local data. DAA UI/Rust owns `config.sqlite` / `runtime.sqlite`; ordinary YAML runtime/import and direct-database writing are retired, with historical private receipts protected. SMA Rust owns `configuration.sqlite3`, a single complete configuration document with revision/CAS; its technical startup JSON and `sma.*` UI preferences are separate and cannot authorize delivery. Simulation, facts production and built-in help are retired. Normal manual/start/resume/auto-start delivery is rejected before HTTP/spawn, even when old preferences or the HTTP gate are enabled. Configuration/pure-preview work is offline; explicit read-only HTTP inspection still uses its gate. Real configuration and logs are not committed.

## Evolution and evidence

As of 2026-11-05, DAA controlled local Stage B and SMA cleanup/CU are owner-accepted; SMA local configuration/pure preview passed QA2, awaiting final acceptance. [Facts provider](../contracts/published/http-api/plc-facts-v1/README.md) and [typed business provider](../contracts/published/http-api/business-integration-v1/README.md) passed isolated MySQL A+B verification, with Owner final acceptance and real adoption pending. DAA upload/ACK and SMA local GET→POST execution/reliable delivery remain unconnected. Current tasks and next gates are in [PLAN](PLAN.md); [ARCH-AW-001](../plans/ARCH-AW-001-agent-foundation/spec.md) owns only historical initialization, not all later work.

Use `pnpm preview --strictPort` for CA preview so port 14190 conflicts fail while preserving frozen CA source. DAA/SMA dev/preview enforce strictPort in their own Vite configuration.

DAA enters the SQLite application with ordinary `pnpm tauri dev`. [Final acceptance on 2026-10-30](data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) completes Stage B within this controlled DS joint-test scope. DAA-003 one-time YAML migration is historical; DAA-007 retires ordinary migration, keeps empty profiles empty and preserves private receipts/history. UI + SQLite own business configuration. See the [DAA README](data-acquisition-agent/README.md) and [joint guide](data-acquisition-agent/JOINT_TEST_GUIDE.md). Historical evidence limits and unexplained actions remain tracked; Stage C, automatic-start policy, Backend/SMA and real-field work are separate.
