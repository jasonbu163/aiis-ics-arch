# AIIS Semantic Mapping Agent

[中文](README.zh-CN.md)

SMA reads configured HTTP GET sources and forwards the latest selected values to HTTP POST targets. The workbench controls collection and reporting separately. See the [SMA-001 r3 specification](plans/SMA-001-cu-integration-and-scope-cleanup/spec.md), the [SMA plan](PLAN.md), and the [Automation World plan](../PLAN.md).

## Configure and run

1. Save the optional base address on **Connection**. Review OpenAPI operations there, or enter a source or target URL manually. Saving configuration and opening the app send no requests. Set `SMA_HTTP_ENABLED=true` for explicit network testing and runtime start.
2. In **Fact sources**, save a GET source, polling interval and timeout in milliseconds. Use **Test GET** to inspect the response and selected points without publishing it. Source paths are JSON Pointers. For a point array, the selector locates the stable point ID before applying the value, quality, time and sample ID paths to that item. For example, with response root `/data`, use array `/points`, identity `/pointId` and value `/value` for a history detail whose contract contains those fields. Use the actual deployment's OpenAPI and acquisition options to confirm the PLC, DB and history detail.
3. In **Target API configuration**, define POST parameters in the path, query, header and JSON body. A full URL takes precedence over the saved connection and relative target path. Set a receipt condition such as JSON pointer `/code` with numeric expected value `200` only when the target contract defines it. Generic HTTP success and configured business acceptance have separate results.
4. Create a **Value rule** when a field needs an allowed-value list. In **Mapping configuration**, bind each parameter to a source point or a constant and set the interval and maximum snapshot age. Fields such as `taskNo` use the same configuration as any other parameter. Required failures block that run. Optional failures omit the parameter, including values in its body or URL template.
5. Use **Mapping execution** to start collection. **Fact points** displays the latest committed values and any read error. Start reporting separately when the enabled mappings are ready. The runtime shows each lane's actual in-flight HTTP, queue, limits, peaks and errors, including per-target POST concurrency. Stopping a lane clears its queue and lets admitted HTTP finish within its timeout. For a manual test, review the frozen request and source versions, then confirm once. A different configuration revision or referenced snapshot requires a new preview. To hold the same input during review, stop collection and preview while the last snapshot is still within its age limit.

SMA keeps each source's points and collection time in one SQLite commit. A failed GET or failed SQLite write preserves the last committed snapshot. `collectedAt` is when SMA successfully collected the response. The upstream point's `observedAt`, quality and sample ID retain their own meanings. Combining two sources in one POST does not establish a single physical sample. An interrupted POST may have been applied by the target. SMA reports unknown outcomes separately and schedules later cycles as separate runs.

For the real **furnace temperature → performance** case, use the dedicated test task chosen by the Human Owner. Before confirming, verify the actual OpenAPI, writable fields, history-detail sample, task number, and matching plan. After the Human Owner manually sends once, compare the response and `planSync` with target readback using the task number, temperature and `lastObservedAt`. See the [acceptance conditions](plans/SMA-001-cu-integration-and-scope-cleanup/spec.md#8-整体验收标准).

## Local configuration and exchange

Rust writes `<SMA profile>/configuration.sqlite3`. The existing schema-v1 configuration document retains its revision and Shanghai `updatedAt`. New source and limit fields are optional for v1 compatibility. A separate `http_source_latest` table is created on the first successful collection and written independently from configuration. Reopening the profile displays retained data with its original time. `runtime-startup.json` remains readable. Every launch starts with collection and reporting stopped.

**Configuration management** exports versioned JSON and XLSX packages with selected rows and their dependencies. Include the saved connection only when needed. Inspect import changes and explicitly confirm them against the preview revision. Source points merge by ID within each source. The legacy complete v1 JSON backup and older single-collection JSON/XLSX files remain available through the configuration management entry. A complete backup refuses export when it detects credential data. Use the portable export to inspect credential exclusions and re-enter omitted values after import. Neither export carries runtime snapshots, receipts, logs or UI preferences. The limit for native configuration and its complete JSON backup is 10 MiB, with up to 10,000 records per collection.

## Development and UI

```bash
pnpm install --frozen-lockfile
pnpm check
pnpm test
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo test --manifest-path src-tauri/Cargo.toml --locked
pnpm tauri dev
```

For source development, inspect the SMA project's `.env` if it already exists. If absent, copy `.env.example` to `.env`. To select a project-local profile, use this assignment.

```dotenv
SMA_PROFILE_DIR=./.local/dev
```

`.local/dev` and `./.local/dev` both select the `.local/dev` directory under the selected `.env` directory, independently of the terminal's current directory. To select an existing absolute profile, replace the following example with that directory's path.

```dotenv
SMA_PROFILE_DIR=/absolute/path/to/sma-profile
```

The optional process `SMA_ENV_FILE` selects a different absolute, readable regular file. Relative profile values from either the process or that file use its parent directory. Profile paths reject `..`, `~`, variables, placeholders, existing symlinks and non-directory components. Check the reported key and reason if startup rejects the selection. A previously exported nonblank process `SMA_PROFILE_DIR` overrides the file.

Ordinary startup stays `pnpm tauri dev`, identity `com.aiis.aw.semanticmappingagent`, dev/preview strict ports 15192/14192. Before disposable runtime verification provide task-owned `SMA_ENV_FILE` / `SMA_PROFILE_DIR`, empty `SMA_BACKEND_BASE_URL` and `SMA_HTTP_ENABLED=false`. The profile isolates Rust files. WKWebView storage is shared across application launches, so native tests use a supported temporary incognito overlay. That overlay does not establish native cross-process UI-preference persistence.

SMA compiles CU's public UI and styles with its own dependencies. The eight workspace pages share the CU shell, locale, themes and table column preferences. Calendar display uses Asia/Shanghai to seconds and preserves underlying precision.

An invalid profile path, corrupt database, or unknown schema returns an error. SMA does not recreate the profile or automatically activate old runtime preferences. Historical replay and target-specific safe retries require their own delivery contract. See the [detailed design](../../docs/AIIS_SMA_Detailed_Design.md) for earlier design context.
