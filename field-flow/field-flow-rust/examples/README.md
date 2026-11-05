# Field Flow Rust basic examples

[中文](README.zh-CN.md)

This README-only directory is owned by the project PLAN. The three cases use YAML v1 and the existing FF-001 r4 typed INT / Execution capability. Runnable source, DEV self-check, independent QA and Owner acceptance are separate facts; exact evidence belongs to the FF-005 task bundle. Run one case at a time.

| Case ID | Purpose and entry | Config / kind | Status / capability version |
| --- | --- | --- | --- |
| basic01 | Reuse existing [src/app/demo01.rs](../src/app/demo01.rs) | [loopback.yaml](../config/loopback.yaml) / demo01 | runnable / FF-001 r4 |
| basic02 | Read target INT; only a negative sample permits GET and execution: [src/app/plc_guard_get_int.rs](../src/app/plc_guard_get_int.rs) | [basic02.yaml](../config/basic02.yaml) / plc_guard_get_int | runnable / FF-005 r1 A, YAML v1 |
| basic03 | GET and original typed parser, then return for value≤0 and value>100: [src/app/get_value_guard_int.rs](../src/app/get_value_guard_int.rs) | [basic03.yaml](../config/basic03.yaml) / get_value_guard_int | runnable / FF-005 r1 A, YAML v1 |


case ID is the teaching identity; flow.id identifies a flow; kind selects explicit dispatch; source_id / command_id identify the command. basic01 reuses demo01 without copying it. basic02 reads the same target it may write: DB1 offset0 initially contains A5A5=-23131, permitting 42. After execute writes 42, at least ten further independent reads skip GET/write. dry_run leaves memory negative, so reads/GET continue while the original command is simulated once. basic03 permits only 1..100. A false rule ends this iteration and the runtime continues, without per-tick false logs. Read failures propagate; no zero/previous-sample substitution. ready=false is strict idle with four null command fields. Invalid/stale inputs fail the original parser before business rules.

Each flow waits 500ms after completing a round, without overlap; different flows progress concurrently. Each existing PLC owner/driver reuses its session and serializes its own IO. HTTP/timer waits hold no PLC execution slot. Repeated reads are independent samples, not caching or sampling deduplication. Read-then-write is not a PLC atomic compare/write, process interlock or cross-point consistent snapshot.

All writes use Execution. confirmed proves a protocol ACK and local commit, not machine action or business completion. If PLC memory becomes 42 but the ACK is lost, basic02 may later return guard_false/health.running. Inspect unknown in the original `state inspect` and health.store/state; skip does not resolve unknown. The new harness demonstrates retained unknown after an invalid truncated ACK. A completely withheld ACK (hold_ack) triggered forced driver cleanup in earlier runs; those failed resource checks are retained and do not prove normal cleanup for complete ACK loss. Never promote a readback to confirmed, clear state or blindly resend. Restart with the original database/config/instance/source/command/issued/expires; changing case/kind/database cannot serve as recovery or evade TTL/deduplication/unknown. No cross-case/language state migration exists.

The new apps add no time fields. Source Unix milliseconds and monotonic durations retain their semantics. Existing JSONL/SQLite UTC calendar values still differ from the root +08 contract; this slice does not migrate history or change the host clock.

| Method | Actual contract / errors |
| --- | --- |
| `Owner::read(&self, flow:&str, db:u16, offset:u32).await -> Result<Sample>` | `Sample.value:i16`, quality/request identity; ready/queue/IO/deadline/protocol errors propagate. |
| `Http::get(&url).await -> Result<Input>` | Existing bounded GET; HTTP status/type/body/schema errors. |
| `Input::intent(&Flow,&Plc) -> Result<Option<Intent>>` | None=idle; strict source/INT/time errors precede guards. |
| `Execution { owner,state,stop }.apply(intent,&mut Clock).await -> Result<()>` | Only write route; existing TTL, duplicate, identity_conflict, target_unknown, clock/audit/queue errors. |
| `iteration(...).await -> Result<()>` | Ok includes idle/guard false; use counts/state for effects. |


Explicit registration: src/app/mod.rs, src/config.rs and src/runtime.rs.

## Preparation (terminal A)

The interactive commands below target the macOS arm64 / zsh environment validated here; for an independent copy, replace the project path with its actual absolute path.

```bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/field-flow/field-flow-rust
FF_PROJECT=$(pwd -P)
FF_RUN_ROOT=$(mktemp -d /private/tmp/ff-005-r1-manual-rust-XXXXXX)
printf '%s\n' "$FF_PROJECT" "$FF_RUN_ROOT"
rustc --version
cargo --version
cargo build --locked --release --no-default-features --bin field-flow --target-dir "$FF_RUN_ROOT/product"
cargo build --locked --release --features test-fixture --bin ff-fixture --target-dir "$FF_RUN_ROOT/fixture"
FF_BIN="$FF_RUN_ROOT/product/release/field-flow"
FF_FIXTURE="$FF_RUN_ROOT/fixture/release/ff-fixture"
# Choose exactly one of basic01/basic02/basic03; do not edit YAML or source timestamps.
FF_CASE=basic02
case "$FF_CASE" in
  basic01) FF_CONFIG="$FF_PROJECT/config/loopback.yaml"; FF_INSTANCE=ff-rust-demo01 ;;
  basic02|basic03) FF_CONFIG="$FF_PROJECT/config/$FF_CASE.yaml"; FF_INSTANCE="ff-rust-$FF_CASE" ;;
esac
mkdir "$FF_RUN_ROOT/dry_run" "$FF_RUN_ROOT/execute"
"$FF_BIN" state init --synthetic --mode dry_run --state-dir "$FF_RUN_ROOT/dry_run/state" --instance-id "$FF_INSTANCE"
"$FF_BIN" state init --synthetic --mode execute --state-dir "$FF_RUN_ROOT/execute/state" --instance-id "$FF_INSTANCE"
printf 'PROJECT=%s\nRUN_ROOT=%s\nCASE=%s\n' "$FF_PROJECT" "$FF_RUN_ROOT" "$FF_CASE"
```


Confirm the tools already exist; stop if a tool/interpreter is missing, without downloading an SDK/interpreter or installing Agent helpers. For an independent copy replace cd with its real absolute path. Finish build/sync and both init commands before fixture command generation. init rejects overwrite; run never creates schema; inspect is read-only. Each mode has a separate database. For each new case repeat preparation with a new root; never rebuild an old incident database.

Terminals A and B do not share variables. Run the following assignment block separately in each terminal, pasting the actual absolute paths and case printed above. Start with FF_MODE=dry_run; after completely stopping that scene, set execute in both terminals and repeat their subsequent blocks. Do not squeeze both modes into one ten-second input-age window.

```bash
read 'FF_PROJECT?Paste PROJECT absolute path: '
read 'FF_RUN_ROOT?Paste RUN_ROOT absolute path: '
read 'FF_CASE?Paste CASE (basic01/basic02/basic03): '
FF_MODE=dry_run
FF_SCENE="$FF_RUN_ROOT/$FF_MODE"
FF_CONFIG="$FF_PROJECT/config/$FF_CASE.yaml"
if [ "$FF_CASE" = basic01 ]; then FF_CONFIG="$FF_PROJECT/config/loopback.yaml"; fi
FF_BIN="$FF_RUN_ROOT/product/release/field-flow"
cd "$FF_PROJECT"
```


## Start, observe and stop

Prepare terminal B first. Once A starts the fixture, immediately run B (the ten-second input_max_age is never refreshed). Stop on a port conflict; do not kill an occupant or change ports.

Terminal A

```bash
"$FF_RUN_ROOT/fixture/release/ff-fixture" --config "$FF_CONFIG" --evidence-dir "$FF_SCENE/fixture"
FF_FIXTURE_EXIT=$?
printf 'fixture exit=%s\n' "$FF_FIXTURE_EXIT"
```


Rust has no fixture_ready event; B checks listeners. After B stops the product, press ENTER in A; the foreground call really waits and records exit0.

Terminal B

```bash
lsof -nP -iTCP:31102 -iTCP:31103 -iTCP:31880 -sTCP:LISTEN
FF_ARGS=()
if [ "$FF_MODE" = execute ]; then FF_ARGS=(--execute); fi
"$FF_BIN" run --config "$FF_CONFIG" --state-dir "$FF_SCENE/state" "${FF_ARGS[@]}" > "$FF_SCENE/product.jsonl" 2> "$FF_SCENE/product.stderr" &
FF_PID=$!
sleep 6
kill -INT "$FF_PID"
wait "$FF_PID"
FF_RUNTIME_EXIT=$?
printf 'runtime PID=%s exit=%s\n' "$FF_PID" "$FF_RUNTIME_EXIT"
"$FF_BIN" state inspect --state-dir "$FF_SCENE/state"
cat "$FF_SCENE/product.stderr"
```


After A records fixture exit=0, run in the same B that owns FF_PID:

```bash
cat "$FF_SCENE/fixture/protocol.json"
ps -p "$FF_PID" -o pid=,stat=,command=
lsof -nP -iTCP:31102 -iTCP:31103 -iTCP:31880 -sTCP:LISTEN
python3 - <<'PYBIND'
import socket
peers = []
try:
    for port in (31102, 31103, 31880):
        peer = socket.socket()
        peer.bind(("127.0.0.1", port)); peer.listen(1); peers.append(peer)
    print("ports_rebound")
finally:
    for peer in peers: peer.close()
PYBIND
```


Normal scenes require runtime/fixture exit0. ps for the original positive PID has no output/exit1 (invalid PIDs or permission failures do not prove release), lsof has no listeners and all three ports rebind. Product JSONL includes normal join/reap and shutdown_complete. Extract original driver/server PIDs from product JSONL and the fixture report and check each with `ps -p PID`. A forced stop, forced_driver_stop, timeout or fault_cleanup is not normal success. The small Python block only checks resource release; it does not validate the product.

Separate preparation, product and post-stop verification count windows. The manual fixture fixes value42 (Python generates a scene identity; Rust uses cmd-001). It has no value/ready/fault flags or control panel. dry_run: simulated1, WriteVar0 and all sixteen A5 bytes. execute: confirmed1, WriteVar1 and 002a plus fourteen A5 bytes. basic01/basic03 obtain at least ten GETs in six seconds and execute only once. basic02 execute has GET1 and at least eleven ReadVars (one trigger plus ten skipped rounds); dry has at least ten independent reads/GETs. Extra independent readback changes session/ReadVar counts and belongs outside the product window. The harness verifies all sixteen bytes only after stopping the product. The manual Rust report contains protocol trace, not a complete memory snapshot.

Stale/invalid input retains the original error and causes no new write. A false business rule creates no command/write and the next round continues without growing error counts. On failure preserve original state/logs/PIDs. Do not edit timestamps/identity/TTL or re-init old state. Stop only exact self-owned processes.

## Bounded negative/boundary matrix

```bash
FF005_EVIDENCE_ROOT="$FF_RUN_ROOT/matrix" cargo test --locked --features test-fixture --target-dir "$FF_RUN_ROOT/test" --test basic_examples -- --nocapture --test-threads=1
# Single case:
FF005_EVIDENCE_ROOT="$FF_RUN_ROOT/basic02-only" cargo test --locked --features test-fixture --target-dir "$FF_RUN_ROOT/test" --test basic_examples basic02_cli -- --nocapture --test-threads=1
```


Own [tests/basic_examples.rs](../tests/basic_examples.rs) starts the formal CLI with formal YAML; Fixture.command/body generate identity/time once, only inside tests. FF005_EVIDENCE_ROOT must be absent or empty; use a new path per run. Build/init finish before command generation. Each scene is bounded to 45 seconds including cleanup and the language matrix to 600 seconds. Each scene retains report.json, original init/inspect output, product.jsonl/stderr, separate preparation/product/readback windows, counts/memory/PIDs/exit codes, actual thread/child joins and three-port rebind.

basic01 covers both modes with 42/idle. basic02 covers negative input, post-write42, -1/0, idle, invalid, stale, read errors in both modes and execute with an invalid truncated ACK retaining unknown. basic03 covers both modes at -1/0/1/42/100/101 plus idle/invalid/stale. Read-error/unknown scenes explicitly retain expected fault outcomes and original state; they do not count as normal stop. Normal scenes require exit0 with no forced cleanup. unknown reporting offers no repair/resend tool.

## Editable business rules and future capabilities

In a consuming source copy you may change business predicates or synthetic input values. basic03 thresholds are source constants, not configuration parameters; rebuild and revalidate changes. The target supports explicit standard DB INT only; physical-target changes require conflict/authorization review. Renaming case/kind/flow/source/instance/state is not recovery. Never change immutable command fields, validity or Execution to make tests green. Unknown kinds, invalid targets and overlapping physical targets remain startup rejections.

Advanced roadmap: advanced01 same-point concurrent flows, advanced02 multiple DBs/points, advanced03 multiple PLCs, advanced04 mixed protocols, advanced05 conditional POST and advanced06 recovery/shutdown remain planned. Each needs its language capability and separate approval. Modbus, POST, JSON point APIs and C# are not current example capabilities; all C# cases are planned. teaching01 remains an independent-copy exercise in [this project USER_GUIDE](../USER_GUIDE.md), not a fourth formal case.
