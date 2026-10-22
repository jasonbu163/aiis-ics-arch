# Product Validation

The [approved r5 spec](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md) defines all thresholds and the exact source/dependency closure. [Tasks](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/tasks.md) distinguish actual DEV runs from independent Verification and acceptance. Tests use synthetic owned profiles, not DAA application databases or real PLCs.

From the DS directory, the formal Python 3.9 stdlib entry points require explicit roots and role:

```sh
/usr/bin/python3 -B scripts/run_validation.py --project-root "$PWD" --run-root /private/tmp/arch-aw-005-r5-exec --role dev --suite all
/usr/bin/python3 -B scripts/build_native.py --project-root "$PWD" --run-root /private/tmp/arch-aw-005-r5-exec --role dev
/usr/bin/python3 -B scripts/run_protocol.py --project-root "$PWD" --run-root /private/tmp/arch-aw-005-r5-exec --role dev --case W01
```

Use `qa` only for the fresh independent role with its own stage/cache/build/tmp/profile/runs. Copy only frozen package contents into its cache; never reuse DEV targets or require QA binaries to have DEV Mach-O hashes. No install, package update or alternate dependency is implicit. An absent argument prints help and starts nothing. The role's closed B0 manifest checks its source, fixed inputs and generated binaries before any protocol listener; stale B0 or occupied fixed ports reject the run.

`all` runs ordinary `pnpm tauri dev`, Rust/core/SQLite contracts and a real two-process profile-lock check, product/test release builds, new B0, fixed native N1–N3, then the generic K07 topology and original protocol matrix. W01–W09 each run three independent profiles/resets, including 100 BOOL competitions per W03. C01 retains its 16 sessions for C02; C03–C06 keep original durations, rates and resource limits. D01 consumes actual frozen ManagedS7 modules; X01 repeats three times and X02 is conditionally inapplicable for the single-process adapter. A failure stops the aggregate sequence; remaining work is not inferred successful.

The non-default native driver uses fixed DOM events, File/DataTransfer and normal 16-command IPC. Its bounded report command records assertions; it is not a generic eval/SQL/raw-control endpoint. N1 saves configuration through real forms, N2 reopens selected/stopped and exercises real S7, typed writes, stale snapshot recovery and selection isolation, N3 proves runtime values are not persisted, single connection close, dirty Cancel and Discard. All close through `Window.close` and the normal save/discard/cancel flow. TERM/KILL is failure cleanup only, never normal lifecycle proof. No repeated manual window closure is required.

[Fixtures](fixtures/README.md) separate original DB41/57 regression bytes from generic product topology and shared v1 naming/layout oracles. Rust tests exercise actual consumer services, independent typed bytes, single-owner rejection, retention, real SQLite transactions and non-default one-shot per-store fault points. Fault injection is identified as such; it does not claim power-loss safety or physical disk exhaustion. Native lifecycle metrics distinguish the main process, observed children, clients and observer; unknown OS service attribution is not zero cost.

Raw commands, stdout/stderr, file events, wire bytes, images, process/resources, SQLite copies and status are saved under the role's T5 run then copied member-for-member to persistent A5 with a second SHA/byte check. Public P5 contains exactly five compact manifests/indexes, no raw DB, logs or binaries. `collect_evidence.py` seals new runs; `verify_evidence.py` verifies an explicit archive or same-role B0 without writing P5. `retire_g0.py` first creates a per-file plan, verifies persistent originals and requires current full product validation before exact-file removal; it never deletes unknown build/profile/system data.

Native resource attribution combines actual POSIX children, the exact owned WebKit store and fixed read-only PID getters on the current WKWebView, only in the non-default test build. The macOS Private SPI is runtime-guarded and not a supported product API; unsupported or unattributed costs remain unknown. Per-PID observations, terminal unavailable samples and shared XPC lifetime are reported separately; no system service is killed.
