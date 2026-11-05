# Field Flow Rust — User guide

[中文](USER_GUIDE.zh-CN.md)

Rust is the main direction for future long-running deployment runtimes. FF-001 r4 implemented the local demo01 loop; independent QA2 passed, while Human Owner final acceptance remains pending. This guide does not establish field, hosting, capacity, long-soak or production readiness. Future production flows are not required to have two language implementations. Existing Python functionality/tests and historical evidence remain valid.

## 1. Independent project and prerequisites

Copy this entire project, excluding target, .venv, dist, caches, state directories, gate/lock runtime files and logs. Preserve Cargo.lock (the dependency lock is source). Use its own sources, config, locales and fixture; no parent/sibling process, executable or environment is required. Parent task links in README are optional governance navigation.

```text
src/main.rs → commands.rs → runtime.rs
src/app/demo01.rs → services/execution.rs
src/domain.rs, config.rs; infrastructure/{http,state,audit,s7_int_pdu,posix}.rs
src/driver_process.rs; src/bin/ff-fixture.rs, src/fixture.rs
Cargo.toml, Cargo.lock, config/loopback.yaml, locales/, tests/
```
These commands use the repository checkout below. For a standalone copy, first change to its real absolute project directory instead. Terminal A remains at that project root throughout preparation. Missing tools are a prerequisite failure; do not install interpreters, targets or system toolchains automatically.

```bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/field-flow/field-flow-rust
FF_PROJECT=$(pwd -P)
FF_LESSON=$(mktemp -d /private/tmp/ff-002-r1-rust-XXXXXX)
printf "%s\n" "$FF_PROJECT" "$FF_LESSON"
rustc -Vv
cargo -V
clang++ --version
cargo build --locked --release --no-default-features --bin field-flow --target-dir "$FF_LESSON/target-product"
cargo build --locked --release --features test-fixture --bin ff-fixture --target-dir "$FF_LESSON/target-fixture"
FF_BIN="$FF_LESSON/target-product/release/field-flow"
mkdir "$FF_LESSON/empty" "$FF_LESSON/dry-lesson" "$FF_LESSON/execute-lesson"
(cd "$FF_LESSON/empty" && "$FF_BIN" && "$FF_BIN" --lang en-US --help && "$FF_BIN" --lang zh-CN --help)
ls -A "$FF_LESSON/empty"
"$FF_BIN" state init --synthetic --mode dry_run --state-dir "$FF_LESSON/dry-lesson/state" --instance-id ff-rust-demo01
"$FF_BIN" state init --synthetic --mode execute --state-dir "$FF_LESSON/execute-lesson/state" --instance-id ff-rust-demo01
```
The empty directory must stay empty, and help exits 0 without config/network/state IO. All builds, dependency preparation and both explicit initializations happen before starting any fixture. State init creates a new child directory and refuses an existing directory; its parent must exist. Normal run never creates schema.

See this project’s [BUILD](BUILD.md) for native dependencies and platform gates.

## 2. What the fixture actually starts

| Component | Address / responsibility |
| --- | --- |
| HTTP | `127.0.0.1:31880/demo01/command` — one synthetic GET command |
| S7 proxy | `127.0.0.1:31102` — transparent frame forwarding, counts/trace, test-only faults |
| S7 server | `127.0.0.1:31103` — real S7 service over registered 16-byte DB1 memory |

The fixture parent owns HTTP/proxy threads and starts a native server child using its own executable. The runtime is a separate process; each PLC owner starts one persistent driver child/session. Two proxy TCP legs do not mean two business PLC clients. This bounded protocol fixture is not the Device Simulator (DS) product; DS, Backend, Docker and the other language are unnecessary.

The legacy YAML v1 fixture CLI emits no fixture_ready line: confirm that it stays alive and all three listeners belong to this exercise. It supplies source demo01-feed, cmd-001 and value 42. Command timestamps are generated once (expiry = issuance + 60000 ms). Repeated GET never refreshes them. The default input_max_age_ms=10000 gives only 10 seconds to start the runtime after fixture startup, even though expiry is 60 seconds. Prepare Terminal B’s command before starting Terminal A’s fixture. Stale input is expected once age exceeds 10 seconds.

Automated tests can mutate feed/faults internally; the manual CLI has no control panel, management API, continuous command generator, arbitrary point table or interactive fault editing. This guide uses DB1 size16 offset0; this native fixture does not derive arbitrary feed/DB layout from config. Use only the published loopback sample here; configurable DB/address ranges do not enlarge fixture capabilities. The native server fixture does not prove real PLC write protection or actual field block size.

## 3. Two separate, bounded teaching runs

Before each fixture, check all three ports read-only. If any listener exists, stop this exercise and report the conflict. Do not kill occupants or change ports. lsof exit 1 with no output means no matching listeners.

```bash
lsof -nP -iTCP:31102 -iTCP:31103 -iTCP:31880 -sTCP:LISTEN
```
Terminal B: explicitly read the real absolute project and lesson paths printed by A (paste each path as one line, no quotes). Shell variables are not shared. Keep this shell for run/inspect.

```bash
read -r FF_PROJECT
read -r FF_LESSON
cd "$FF_PROJECT"
FF_BIN="$FF_LESSON/target-product/release/field-flow"
```
### Dry-run lesson

A, project cwd; start fixture in a never-existing report directory:

```bash
"$FF_LESSON/target-fixture/release/ff-fixture" --config "$FF_PROJECT/config/loopback.yaml" --evidence-dir "$FF_LESSON/dry-lesson/fixture"
```
B, same project cwd: start immediately, run for two seconds, signal only its recorded PID, and actually wait.

```bash
"$FF_BIN" run --config "$FF_PROJECT/config/loopback.yaml" --state-dir "$FF_LESSON/dry-lesson/state" > "$FF_LESSON/dry-lesson/stdout.jsonl" 2> "$FF_LESSON/dry-lesson/stderr.txt" &
FF_PID=$!
printf "runtime PID=%s\n" "$FF_PID"
sleep 2
kill -INT "$FF_PID"
wait "$FF_PID"
FF_EXIT=$?
printf "runtime exit=%s\n" "$FF_EXIT"
"$FF_BIN" state inspect --state-dir "$FF_LESSON/dry-lesson/state"
```
A: press ENTER and wait for the fixture foreground command to return; expect protocol.json. Immediately record the fixture exit code in A:

```bash
FF_FIXTURE_EXIT=$?
printf "fixture exit=%s\n" "$FF_FIXTURE_EXIT"
```

Switch back to the same Terminal B retained from section3 (project cwd), then run the report, port and runtime/driver/server PID checks below. Only B assigned FF_PID from this run’s $!; A does not use it. Verify the printed PID is the original positive integer for this run; stop on an empty or wrong PID. For a valid PID, ps exit1 means absent only when both stdout and stderr are empty; invalid-argument or permission diagnostics are check failures.


```bash
cat "$FF_LESSON/dry-lesson/fixture/protocol.json"
cat "$FF_LESSON/dry-lesson/stderr.txt"
lsof -nP -iTCP:31102 -iTCP:31103 -iTCP:31880 -sTCP:LISTEN
printf "checking runtime PID=%s\n" "$FF_PID"
ps -p "$FF_PID" -o pid=,stat=,command=
```
Expected: inspect counts simulated=1, fixture writes/applied=0. Normal runtime and fixture exit 0; no listener and recorded runtime PID absent. Also extract driver_ready PID from stdout.jsonl (Rust context is a JSON string) and native_pid from Rust protocol.json; use ps -p on each exact PID and require absence.  Sending SIGINT alone is not release evidence.

### Execute lesson

A, project cwd; start fixture in a never-existing report directory:

```bash
"$FF_LESSON/target-fixture/release/ff-fixture" --config "$FF_PROJECT/config/loopback.yaml" --evidence-dir "$FF_LESSON/execute-lesson/fixture"
```
B, same project cwd: start immediately, run for two seconds, signal only its recorded PID, and actually wait.

```bash
"$FF_BIN" run --config "$FF_PROJECT/config/loopback.yaml" --state-dir "$FF_LESSON/execute-lesson/state" --execute > "$FF_LESSON/execute-lesson/stdout.jsonl" 2> "$FF_LESSON/execute-lesson/stderr.txt" &
FF_PID=$!
printf "runtime PID=%s\n" "$FF_PID"
sleep 2
kill -INT "$FF_PID"
wait "$FF_PID"
FF_EXIT=$?
printf "runtime exit=%s\n" "$FF_EXIT"
"$FF_BIN" state inspect --state-dir "$FF_LESSON/execute-lesson/state"
```
A: press ENTER and wait for the fixture foreground command to return; expect protocol.json. Immediately record the fixture exit code in A:

```bash
FF_FIXTURE_EXIT=$?
printf "fixture exit=%s\n" "$FF_FIXTURE_EXIT"
```

Switch back to the same Terminal B retained from section3 (project cwd), then run the report, port and runtime/driver/server PID checks below. Only B assigned FF_PID from this run’s $!; A does not use it. Verify the printed PID is the original positive integer for this run; stop on an empty or wrong PID. For a valid PID, ps exit1 means absent only when both stdout and stderr are empty; invalid-argument or permission diagnostics are check failures.


```bash
cat "$FF_LESSON/execute-lesson/fixture/protocol.json"
cat "$FF_LESSON/execute-lesson/stderr.txt"
lsof -nP -iTCP:31102 -iTCP:31103 -iTCP:31880 -sTCP:LISTEN
printf "checking runtime PID=%s\n" "$FF_PID"
ps -p "$FF_PID" -o pid=,stat=,command=
```
Expected: inspect counts confirmed=1, fixture writes/applied=1 and value bytes 00 2a at DB1 offset 0. Normal runtime and fixture exit 0; no listener and recorded runtime PID absent. Also extract driver_ready PID from stdout.jsonl (Rust context is a JSON string) and native_pid from Rust protocol.json; use ps -p on each exact PID and require absence.  Sending SIGINT alone is not release evidence.

Only this brand-new synthetic lesson starts with fresh directories; this is not incident recovery. Restart an existing execute scene with exactly its original state/config/instance/source/command identity; do not rerun init, delete state, replace the fixture to refresh cmd-001, edit timestamps or invent new IDs to evade deduplication/unknown. A stale input produces no new write; duplicates with unchanged identity are suppressed, changed immutable content produces identity_conflict. New independent lessons must never be used to conceal results from an old scene.

## 4. Configuration and input contract

config/loopback.yaml is the complete YAML v1 runnable sample. Objects are Config → Plc[], Flow[] → Target, Http. Unknown/missing fields and implicit string/boolean-to-integer conversions are rejected. IDs use ASCII A–Z/a–z/0–9/_/- with length 1–64. flow.id selects identity; kind selects explicit app dispatch; business_name describes the rule; source_id must match the feed. They are different roles.

| Field | Accepted value / relation |
| --- | --- |
| `schema_version / instance_id` | 1 / valid_id; must match state |
| `plcs / flows` | 1–4 / 1–8; unique IDs, unique PLC host:port |
| `plc.host / port / rack / slot` | literal IPv4 / 1–65535 / 0–7 / 0–31 |
| `connect_timeout_ms / io_timeout_ms` | PLC: 500–3000 / 500–5000 |
| `queue_capacity / queue_wait_ms / ready_wait_ms` | 1–16 / 100–5000 / 100–5000 |
| `flow.kind / interval_ms / input_max_age_ms` | demo01 / plc_guard_get_int / get_value_guard_int / 100–10000 / 1–60000 |
| `get_url` | http(s), host, no credentials/fragment; no proxy/redirect/retry |
| `target.plc_id / db_number` | existing PLC / 1–65535 |
| `db_size_bytes / byte_offset / type` | 2–65536 / 0–65534 / INT; offset+2 ≤ size |
| `target overlap` | same physical host/port/rack/slot/DB 2-byte overlap rejected |
| `http.connect_timeout_ms / pool_wait_ms` | 100–1500 each, both ≤ total_timeout_ms |
| `http.total_timeout_ms / max_connections / max_body_bytes` | 100–5000 / 1–8 / 1–4096 |
| `shutdown_timeout_ms` | 5000–20000 and ≥ max(HTTP total, every PLC connect/IO)+5500 |
| `config bytes` | ≤65536; relative paths resolve from command cwd |

A standard non-optimized DB INT is two signed bytes, big-endian, range -32768…32767. DB number/declared size/offset are explicit configuration, not a field DB1 convention or proof of the actual PLC block size. BOOL/DINT/REAL, optimized symbolic DB access, POST, authentication and demo02 are not implemented.

```json
{"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":"example-001","value":42,"issued_at_ms":1792742400000,"expires_at_ms":1792742460000}
```
The JSON is a shape example with deliberately historical timestamps, not a live command to submit. Require exactly these seven keys, JSON Content-Type and HTTP 200. ready=false requires command_id/value/issued_at_ms/expires_at_ms all null. ready=true requires valid command_id, strict integer INT and signed 64-bit integer Unix milliseconds. Require 0 < expires−issued ≤60000, issued ≤now+1000, now <expires and now−issued ≤input_max_age_ms. The original wall/monotonic anchor rejects drift >1000 ms without resetting at queue/dequeue/driver start. Do not change the host clock for a test.

## 5. One iteration, state and lifecycle

One iteration awaits GET → validates input → returns on idle → admits intent and awaits Execution.apply. The runtime owns the outer loop: finish one iteration, then wait interval_ms; no same-flow overlap or catch-up ticks. Different flows are async tasks. One reused HTTP client serves the runtime; HTTP/interval waits do not hold the PLC FIFO. Each PLC owner reuses one child/session, serializing only its own IO. Each read creates independent request/sample identities; no shared snapshot or business mutual exclusion. See this project’s tests/local_protocol.rs (three independent readers, slow GET) and tests/runtime_regressions.rs. These tests call services directly; the manual CLI still accepts only registered kinds.

Ready waiting, FIFO capacity/queue waiting and actual dispatch connect/IO have separate budgets. Connect/IO total deadlines include IPC and actual fault reaping; the 400ms cleanup reserve stays inside the original budget and never refreshes source time. Expiry/clock/gates are checked again at queue/dequeue/true start. T2=in_flight means a durable dispatch permit, not that a native call has started; owner health in_flight uses the actual started event. Failed connections use bounded 250/500/1000/2000ms backoff and a 10-second cooldown per cycle; unknown writes are not replayed, and independent flows/HTTP may continue.

T1 persists source/command identity, immutable payload/config/physical target and pending (or simulated in dry_run). T2 persists dispatch_count=1 and in_flight before a permitted external call. T3 persists confirmed only after a matching typed S7 ACK. confirmed proves protocol ACK plus local commit, not machine/process completion. No ACK proof after a possible send becomes unknown; restart recovers in_flight to unknown. expired/canceled mean a classified failure before or at a guarded phase; they do not undo an already applied write. Unknown physical overlaps block writes despite aliases/new identities/readback. There is no unknown-resolution/retry/clear-state CLI. Preserve original state/logs and stop the writer for review.

Each state directory has state.sqlite (schema1 store_meta/commands/command_events), instance.lock, transient gate-* and runtime.jsonl plus .1… .4. SQLite is local execution truth, not the Backend business DB. state inspect is read-only and reports meta and counts; runtime health is JSONL, not a listening API. Relative CLI paths resolve from cwd; use the printed absolute paths. Do not share or interchange Rust/Python writable databases or dry_run/execute stores. A writer handoff must stop the old side and reconcile pending/unknown and confirmed progress. Local inherited locks/start gates are not cross-host fencing.

Capacity: 10000 command identities; admission pauses at 90000 events, DB ≥48 MiB or free disk <256 MiB; DB hard cap64 MiB and DB+journal cap128 MiB. No automatic identity/event eviction. JSONL line ≤4096 bytes; file ≤5 MiB with four backups (25 MiB total). Required audit persist/flush/sync/stdout failure closes new write gates; confirmed does not regress after a later sink failure. Recognize identity_conflict, target_unknown, clock_invalid, audit_unhealthy/audit_* and capacity_paused from stderr/health/state; stop and preserve evidence, do not increase limits or clear history as recovery.

Useful event keys: `process_start, driver_spawn, driver_ready, driver_call_started, intent, in_flight, ack, health, flow_health, stop_gate_closed, driver_process_reaped, runtime_tasks_joined, resources_released, shutdown_complete`. Some state events use more specific event names; inspect the actual JSONL.

Normal SIGINT/SIGTERM closes all start gates, cancels queued/unstarted work, classifies in-flight results conservatively, joins flows/owners, closes HTTP and waits/reaps child processes and state/audit thread within one shutdown budget. A forced kill, forced_driver_stop, fault_cleanup or shutdown_incomplete is not normal success. Do not kill by process name/port. Exit0 means normal completion; Rust CLI/config/state-prefixed errors exit2 and other runtime errors exit1. Python argument/config/state startup failures normally exit2, close fault/unknown exits1 (shutdown_incomplete is1); not every Python runtime failure maps to1. Read the actual error key and logs.

Current time limitation: source issued/expires/sampled/health *_ms are Unix milliseconds, while durations/deadlines use monotonic time; do not add eight hours to numeric epochs. Current SQLite calendar metadata uses UTC Z strftime; Python JSONL explicitly uses UTC +00:00 and Rust tracing timestamps use UTC. This differs from the root Asia/Shanghai calendar-storage contract. FF-002 reports it without migrating schema/history/logs; future implementation/data compatibility work requires its own approved scope.

## 6. Methods available to app code

These are source-level contracts, not a versioned public SDK. Result<T> is Result<T,String>; await and propagate error keys with ?.

| Path / owner | Actual signature | Usage / result / errors |
| --- | --- | --- |
| `src/app/demo01.rs` | `iteration(f:&Flow,p:&Plc,http:&Http,owner:&Owner,state:&State,stop:&Stop,clock:&mut Clock) -> Result<()>` | async; one GET/validation/apply; runtime owns arguments/clock |
| `src/infrastructure/http.rs (re-export services::Http)` | `Http::new(&config::Http)->Result<Http>; get(&self,url:&str)->Result<Input>` | new sync at composition root, cloned client reused; get async; http_config/http_pool_timeout/http_communication/http_status/input_content_type/input_body_size/input_schema/http_timeout |
| `src/domain.rs` | `Input::intent(self,&Flow,&Plc)->Result<Option<Intent>>` | sync; None idle, Some intent; input_schema/input_stale |
| `src/domain.rs` | `Intent::validate_time(&self,now:i64)->Result<()>; deadline(&self)->std::time::Instant` | sync; validates original issuance/expiry; input_stale |
| `src/domain.rs` | `Clock::default(); check(&mut self,wall:i64)->Result<()>` | sync; per-flow original anchor; clock_invalid |
| `src/services/execution.rs` | `Execution { owner:&Owner,state:&State,stop:&Stop }.apply(Intent,&mut Clock)->Result<()>` | async; only app write route; duplicate/simulated may return Ok without IO; target_unknown/identity_conflict/clock_invalid/capacity_paused and IO/audit failures |
| `src/runtime.rs` | `Owner::read(&self,flow:&str,db:u16,offset:u32)->Result<Sample>; health(&self)->OwnerHealth` | read async with independent request; health sync snapshot; plc_unavailable/queue_timeout/expired/canceled/driver or s7_* errors |
| `src/config.rs` | `Config::load(p:&Path)->Result<Config>; validate(&self)->Result<()>` | sync at composition root; Flow/Plc/Target/Http fields in section4; config_read/config_size/config_schema/config_* |
| `src/domain.rs` | `Clock::anchor(&self)->ClockAnchor; ClockAnchor::check(&self,wall:i64)->Result<()>` | sync; clone of original wall/monotonic anchor for internal IPC, clock_invalid; app uses Clock::check, never resets anchor to hide drift |
| `src/runtime.rs` | `Stop::close(&self)->Result<()>; wait(&self); stopped:Arc<AtomicBool>` | close sync, wait async; runtime owns close/gate lifecycle, app can check stopped.load(Ordering::Acquire); gate_* errors; do not construct/close gates per round |
| `src/infrastructure/state.rs` | `inspect(dir:&Path)->Result<Value>; State::snapshot(&self)->Result<Value>` | inspect sync CLI read-only meta/counts; snapshot async internal health {commands,log_writable,capacity}; state_io/state_schema/state_deadline; state owner thread |
| `src/infrastructure/state.rs` | `State::log(&self,event:&str,c:serde_json::Value)->Result<()>` | async internal observation via state/audit actor, e.g. state.log("observation",json!({"result":"ok"})).await?; audit_* / state_* failures propagate; not a substitute for state transitions |

Rust Sample returns request_id/flow_id/generation/pid/value:i16/quality/sampled_at_ms and optional write_ack. Read Sample.write_ack is None; write ACK proof belongs to Execution.


Read example inside a bounded app iteration (use a distinct flow request label):

```rust
let sample = owner.read("teaching-read", f.target.db_number, f.target.byte_offset).await?;
let value: i16 = sample.value;
```
This legacy snippet does not register a flow; see the YAML v2 read_points entry below. Read quality good means a validated protocol sample at sampled_at_ms, not physical completion.

Composition/lifecycle only: Config::load/validate, Runtime::start/launch_flows/health/shutdown, State::open/finalize and StateTask::join. State.admit/dispatch/finish and Owner.write are infrastructure used by Execution; do not call them to bypass durable execution. Driver.spawn/call/close, raw iso_exchange, S7 codec, gate/lock, SQL and fixture mutation hooks are internal/test surfaces. No public method for HTTP POST/auth, BOOL/REAL or automatic case discovery exists. The full demo01 code in section7 shows the shortest supported write route.

## 7. Add teaching01 with the same capability

Do this only in a new independent tutorial source copy, never as incident recovery or as an unapproved edit to the delivered runtime. teaching01 deliberately repeats GET→INT; it is not demo02/rising-edge/POST. Adding a file or YAML alone does not register a kind. First finish/stop section3. Preserve old state. Use a fresh copy with its own environment/targets; no sibling imports.

Terminal A still has FF_PROJECT from section1. Copy the tutorial source to a new project (no state/environment/target), then edit only that copy:

```bash
FF_TUTORIAL=$(mktemp -d /private/tmp/ff-002-r1-teaching-rust-XXXXXX)
python3 - "$FF_PROJECT" "$FF_TUTORIAL/project" <<'PY'
from pathlib import Path
import shutil, sys
shutil.copytree(Path(sys.argv[1]), Path(sys.argv[2]),
    ignore=shutil.ignore_patterns("target*", ".venv", "dist", "__pycache__", ".pytest_cache", "*.pyc", "runtime.jsonl*", "state.sqlite*", "instance.lock", "gate-*"))
PY
FF_PROJECT="$FF_TUTORIAL/project"
FF_LESSON="$FF_TUTORIAL/run"
mkdir "$FF_LESSON"
cd "$FF_PROJECT"
printf "%s\n" "$FF_PROJECT" "$FF_LESSON"
```

Create the complete file `src/app/teaching01.rs`:

```rust
//! 文件：src/app/teaching01.rs；教学案例：手写单轮GET→typed条件→执行服务，无循环、SQL或协议IO。
use crate::{
    config::{Flow, Plc},
    domain::{now_ms, Clock},
    infrastructure::state::State,
    runtime::{Owner, Stop},
    services::{execution::Execution, Http},
    Result,
};
pub async fn iteration(
    f: &Flow,
    p: &Plc,
    http: &Http,
    owner: &Owner,
    state: &State,
    stop: &Stop,
    clock: &mut Clock,
) -> Result<()> {
    clock.check(now_ms())?;
    let input = http.get(&f.get_url).await?;
    if let Some(intent) = input.intent(f, p)? {
        Execution { owner, state, stop }
            .apply(intent, clock)
            .await?;
    }
    Ok(())
}
```
Wire each existing file in the copy. src/app/mod.rs declares the module; config.rs must accept the new kind; runtime.rs must explicitly select it. The following small edit script has exact-match assertions; stop if the baseline changed instead of guessing. Run from the tutorial project root using an existing helper Python, which only edits text:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path("src/app/mod.rs")
s = p.read_text()
assert "pub mod teaching01;" not in s
p.write_text(s + "\npub mod teaching01;\n")
p = Path("src/config.rs")
s = p.read_text()
old = '"demo01" | "plc_guard_get_int" | "get_value_guard_int"'
assert s.count(old) == 1
p.write_text(s.replace(old, old + ' | "teaching01"'))
p = Path("src/runtime.rs")
s = p.read_text()
old = '"demo01"=>crate::app::demo01::iteration(&f,&plc,&http,&owner,&state,&stop,&mut clock).await,'
new = old + '"teaching01"=>crate::app::teaching01::iteration(&f,&plc,&http,&owner,&state,&stop,&mut clock).await,'
assert s.count(old) == 1
p.write_text(s.replace(old, new))
PY
```
Create config/teaching01.yaml in this copy, complete contents:

```yaml
# FF-001 synthetic loopback；不是现场目标授权。
schema_version: 1
instance_id: ff-rust-teaching01
plcs:
  - id: plc_demo
    host: 127.0.0.1
    port: 31102
    rack: 0
    slot: 1
    connect_timeout_ms: 3000
    io_timeout_ms: 5000
    queue_capacity: 16
    queue_wait_ms: 2000
    ready_wait_ms: 3000
flows:
  - id: teaching01
    kind: teaching01
    business_name: teaching_command_to_int
    interval_ms: 500
    source_id: demo01-feed
    get_url: http://127.0.0.1:31880/demo01/command
    target: {plc_id: plc_demo, db_number: 1, db_size_bytes: 16, byte_offset: 0, type: INT}
    input_max_age_ms: 10000
http: {connect_timeout_ms: 500, total_timeout_ms: 1500, pool_wait_ms: 500, max_connections: 8, max_body_bytes: 4096}
shutdown_timeout_ms: 15000
```
flow ID/business/instance changed; source demo01-feed and DB1/16/offset0 remain because the manual fixture is fixed. Run only this one flow, never alongside demo01 on its overlapping physical target. Config overlap checks reject an accidental combined configuration. No new locale keys or CLI text were added, so neither locales/en-US.json nor zh-CN.json changes. In your consuming tutorial copy add teaching01 to CODE_INDEX.md and link its local instructions from README; do not claim the delivered source already includes it.

```bash
cargo build --locked --release --no-default-features --bin field-flow --target-dir "$FF_LESSON/target-product"
cargo build --locked --release --features test-fixture --bin ff-fixture --target-dir "$FF_LESSON/target-fixture"
```
Complete both modes below in the new copy. FF_PROJECT/FF_LESSON refer to the new printed paths; do not cd back to the original checkout. Initialize first, then start one fixture at a time.

```bash
FF_BIN="$FF_LESSON/target-product/release/field-flow"
mkdir "$FF_LESSON/dry-lesson" "$FF_LESSON/execute-lesson"
"$FF_BIN" state init --synthetic --mode dry_run --state-dir "$FF_LESSON/dry-lesson/state" --instance-id ff-rust-teaching01
"$FF_BIN" state init --synthetic --mode execute --state-dir "$FF_LESSON/execute-lesson/state" --instance-id ff-rust-teaching01
```

In Terminal B repeat section3’s two read -r lines with the new project/lesson paths, cd and set FF_BIN again. Check free ports with the section3 lsof command first.

**dry — A**

```bash
"$FF_LESSON/target-fixture/release/ff-fixture" --config "$FF_PROJECT/config/teaching01.yaml" --evidence-dir "$FF_LESSON/dry-lesson/fixture"
```
B immediately (within the original 10-second input age):

```bash
"$FF_BIN" run --config "$FF_PROJECT/config/teaching01.yaml" --state-dir "$FF_LESSON/dry-lesson/state" > "$FF_LESSON/dry-lesson/stdout.jsonl" 2> "$FF_LESSON/dry-lesson/stderr.txt" &
FF_PID=$!
sleep 2
kill -INT "$FF_PID"
wait "$FF_PID"
printf "runtime exit=%s\n" "$?"
"$FF_BIN" state inspect --state-dir "$FF_LESSON/dry-lesson/state"
```
A: press ENTER to close the fixture and immediately record FF_FIXTURE_EXIT in A as in section3. Then switch back to B, which retained this run’s FF_PID, to check reports, valid exact PIDs and port release before the next mode. A does not use B’s FF_PID.

**execute — A**

```bash
"$FF_LESSON/target-fixture/release/ff-fixture" --config "$FF_PROJECT/config/teaching01.yaml" --evidence-dir "$FF_LESSON/execute-lesson/fixture"
```
B immediately (within the original 10-second input age):

```bash
"$FF_BIN" run --config "$FF_PROJECT/config/teaching01.yaml" --state-dir "$FF_LESSON/execute-lesson/state" --execute > "$FF_LESSON/execute-lesson/stdout.jsonl" 2> "$FF_LESSON/execute-lesson/stderr.txt" &
FF_PID=$!
sleep 2
kill -INT "$FF_PID"
wait "$FF_PID"
printf "runtime exit=%s\n" "$?"
"$FF_BIN" state inspect --state-dir "$FF_LESSON/execute-lesson/state"
```
A: press ENTER to close the fixture and immediately record FF_FIXTURE_EXIT in A as in section3. Then switch back to B, which retained this run’s FF_PID, to check reports, valid exact PIDs and port release before the next mode. A does not use B’s FF_PID.

Expect simulated1/write0 in dry-run, confirmed1/write1 in execute, and inspect meta.instance_id=ff-rust-teaching01. Fixture load and product startup validate kind; Rust compilation alone does not validate YAML. Preserve old state; no schema/driver/API change is required.

## 8. Verification and limits

The bounded FF-002 rehearsal uses the actual product CLI in independent macOS arm64 copies, separate new synthetic dry/execute scenes and both wired tutorial cases; evidence and failures belong to the FF-002 tasks bundle. It is Development self-check until fresh Verification records its own verdict. No FF-001 full fault matrix rerun, real endpoint/PLC, DS joint validation, production hosting, platform port, long soak or distribution compliance is claimed. Preserve report/PID/exit/port evidence before any eventual task-owned resource cleanup.

Local navigation: [README](README.md), [CODE_INDEX](CODE_INDEX.md), [notices](THIRD_PARTY_NOTICES.md).

## Basic examples

Three registered cases and complete commands: [examples](examples/README.md); YAML contracts: [config](config/README.md). teaching01 remains a tutorial-copy exercise.

<a id="catalog-v2"></a>

## Rust catalog configuration v2

YAML v1 preserves demo01/plc_guard_get_int/get_value_guard_int and the three original YAML files. Rust YAML v2 supports demo01/read_points only, loading one ff.plc JSON v1 per PLC from the explicit plc_files list. Paths resolve from the main file directory; no scanning/hot reload. Modbus supports structural validate only; run rejects the whole group before state/log/network IO, including unreferenced or disabled Modbus. Python/C# loading and DS export are not implemented.

The read-only source API is devices.get(device_id)?.read(point_id).await. Composition binds flow_id and injects only the device_ids subset and enabled points; the app receives no raw addresses/writer/SQL/owner map. A sample retains request_id/flow_id/generation, typed int16/quality and local response-completion received_at(+08:00), not device event time. Each read_points iteration awaits reads in order and ends at the first error, leaving later items not_attempted without a sample/value. New rounds clear the previous items. Owners/queues/sessions are reused; independent flows perform independent samples, without deduplication or atomic snapshots.

points_health uses the existing five-second cadence. Only the latest round is held: at most16 items/flow and128 total. Chunks have at most4 items and JSONL lines at most4096 bytes including the audit envelope/escaped context. round_id/chunk_index/chunk_count identify chunks, without an atomic cross-chunk snapshot. in_progress can contain partial success; completed_rounds/successful_reads/errors are saturating counters. New observed_at/received_at use +08; original UTC log envelopes/state producers are unchanged.

Terminal A: finish all builds and both initializations before any fixture. Give B both printed absolute paths, one pasted per line. An occupied port stops the exercise: do not kill occupants or change ports. Empty lsof exit1 only means no matching listener.

```bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/field-flow/field-flow-rust
FF_PROJECT=$(pwd -P)
FF_RUN_ROOT=$(mktemp -d /private/tmp/ff-004-r2-manual-XXXXXX)
printf '%s\n' "$FF_PROJECT" "$FF_RUN_ROOT"
cargo build --locked --release --no-default-features --bin field-flow --target-dir "$FF_RUN_ROOT/product"
cargo build --locked --release --features test-fixture --bin ff-fixture --target-dir "$FF_RUN_ROOT/fixture"
"$FF_RUN_ROOT/product/release/field-flow" config validate --config "$FF_PROJECT/config/catalog-demo.yaml"
"$FF_RUN_ROOT/product/release/field-flow" config validate --plc-file "$FF_PROJECT/config/plcs/modbus-example.json"
"$FF_RUN_ROOT/product/release/field-flow" state init --synthetic --mode dry_run --state-dir "$FF_RUN_ROOT/dry-state" --instance-id ff-rust-catalog-demo
"$FF_RUN_ROOT/product/release/field-flow" state init --synthetic --mode execute --state-dir "$FF_RUN_ROOT/execute-state" --instance-id ff-rust-catalog-demo
lsof -nP -iTCP:34102 -iTCP:34103 -iTCP:34112 -iTCP:34113 -iTCP:34880 -sTCP:LISTEN
```


A starts a new dry fixture and waits for fixture_ready, which is still idle:

```bash
"$FF_RUN_ROOT/fixture/release/ff-fixture" --catalog-demo --evidence-dir "$FF_RUN_ROOT/dry-fixture"
```

B sets its own variables in its own shell, then starts the product:

```bash
read -r FF_PROJECT
read -r FF_RUN_ROOT
cd "$FF_PROJECT"
FF_BIN="$FF_RUN_ROOT/product/release/field-flow"
FF_SCENE=dry
"$FF_BIN" run --config "$FF_PROJECT/config/catalog-demo.yaml" --state-dir "$FF_RUN_ROOT/dry-state" > "$FF_RUN_ROOT/$FF_SCENE.stdout.jsonl" 2> "$FF_RUN_ROOT/$FF_SCENE.stderr" &
FF_PID=$!
printf 'runtime PID=%s\n' "$FF_PID"
```


B checks the initial complete [12,1,56,34] round with this bounded, read-only check. This manual walkthrough demonstrates the first health/state result and normal closure; it does not establish S1's at-least-ten identical post-issue GETs. Stop and preserve a deadline failure; do not refresh identity or enlarge TTL.

```bash
python3 - "$FF_RUN_ROOT/$FF_SCENE.stdout.jsonl" initial <<'PY_CHECK'
import json, pathlib, sys, time
p, stage = pathlib.Path(sys.argv[1]), sys.argv[2]
end = time.monotonic() + (15 if stage == "initial" else 8)
while time.monotonic() < end:
    for line in p.read_text().splitlines():
        try:
            v = json.loads(line)
            c = v.get("context", {})
            if isinstance(c, str): c = json.loads(c)
        except ValueError:
            continue
        if stage == "initial":
            ok = v.get("event") == "points_health" and c.get("flow_id") == "read_pair" and c.get("status") == "complete" and [i.get("sample", {}).get("value") for i in c.get("items", [])] == [12, 1, 56, 34]
        else:
            ok = v.get("event") == "health" and any(c.get("store", {}).get("commands", {}).get(k) == 1 for k in ["simulated", "confirmed"])
        if ok:
            print(json.dumps(c, ensure_ascii=False)); sys.exit(0)
    time.sleep(0.05)
raise SystemExit("observation deadline")
PY_CHECK
```


Before issue, HTTP is strict seven-key idle, command0 and writes=[0,0]. A now types `issue` once into the fixture stdin and presses ENTER. It freezes that scene's original body/identity/time; a second issue or invalid input is rejected without mutation. B immediately reruns the check above, replacing its single `initial` argument with `issued`. Expect simulated1 within8 seconds; original input_max_age remains10 seconds. After success, B signals only its recorded product PID and actually waits:

```bash
kill -INT "$FF_PID"
wait "$FF_PID"
FF_EXIT=$?
printf 'runtime exit=%s\n' "$FF_EXIT"
"$FF_BIN" state inspect --state-dir "$FF_RUN_ROOT/$FF_SCENE-state"
```


A enters an empty line to stop its foreground fixture. Immediately after return, A records its own exit:

```bash
FF_FIXTURE_EXIT=$?
printf 'fixture exit=%s\n' "$FF_FIXTURE_EXIT"
```

B retains FF_PID and checks the report, stderr, exact PID and ports. Normal runtime and fixture exit0. final_memory is A.DB1=000c0001+12 A5 bytes, A.DB2=0038+14 A5 bytes, B.DB1=0022+14 A5 bytes; writes=[0,0]. Extract both driver PIDs from `$FF_RUN_ROOT/$FF_SCENE.stdout.jsonl` driver_ready.context (parse the string as JSON) and both native server PIDs from `$FF_RUN_ROOT/$FF_SCENE-fixture/protocol.json` native_pids. The bounded check below runs ps -p on each exact positive PID and requires absence. Invalid arguments/permission errors are not absence.

```bash
cat "$FF_RUN_ROOT/$FF_SCENE-fixture/protocol.json"
cat "$FF_RUN_ROOT/$FF_SCENE.stderr"
ps -p "$FF_PID" -o pid=,stat=,command=
lsof -nP -iTCP:34102 -iTCP:34103 -iTCP:34112 -iTCP:34113 -iTCP:34880 -sTCP:LISTEN
```

```bash
python3 - "$FF_RUN_ROOT/$FF_SCENE.stdout.jsonl" "$FF_RUN_ROOT/$FF_SCENE-fixture/protocol.json" <<'PY_PIDS'
import json, pathlib, subprocess, sys
pids = set()
for line in pathlib.Path(sys.argv[1]).read_text().splitlines():
    row = json.loads(line)
    context = row.get("context", {})
    if isinstance(context, str): context = json.loads(context)
    if row.get("event") == "driver_ready": pids.add(context["pid"])
assert len(pids) == 2, pids
report = json.loads(pathlib.Path(sys.argv[2]).read_text())
assert len(report["native_pids"]) == 2
pids.update(report["native_pids"])
for pid in sorted(pids):
    assert isinstance(pid, int) and pid > 0
    check = subprocess.run(["ps", "-p", str(pid), "-o", "pid=,stat=,command="], capture_output=True, text=True)
    assert check.returncode == 1 and not check.stdout and not check.stderr, (pid, check.stdout, check.stderr)
print(json.dumps({"absent_driver_and_native_pids": sorted(pids)}))
PY_PIDS
```


Execute is a separate new scene. A keeps its own variables, rechecks the five free ports, then starts:

```bash
"$FF_RUN_ROOT/fixture/release/ff-fixture" --catalog-demo --evidence-dir "$FF_RUN_ROOT/execute-fixture"
```

B keeps the same shell and starts explicitly:

```bash
FF_SCENE=execute
"$FF_BIN" run --config "$FF_PROJECT/config/catalog-demo.yaml" --state-dir "$FF_RUN_ROOT/execute-state" --execute > "$FF_RUN_ROOT/$FF_SCENE.stdout.jsonl" 2> "$FF_RUN_ROOT/$FF_SCENE.stderr" &
FF_PID=$!
printf 'runtime PID=%s\n' "$FF_PID"
```

Repeat initial check, one issue in A, issued check in B, B SIGINT/wait/inspect, A empty-line/exit, B report/PID/port checks. Expect confirmed1, exactly one A WriteVar and zero B writes. Only A.DB1 first INT changes to002a; ready/result/B and all neighboring A5 bytes remain. ACK plus local confirmed is not process completion. Preserve original state/logs/identities; do not reinitialize, change IDs or switch stores to evade unknown. An old confirmed store can use v2 only when all original typed semantics match. Paths/display/source hashes are not the effect hash; actual address/declared-size/business-name changes conflict. Replacing an old PLC id with a DS UUID does not promise seamless state inheritance.

The existing teaching01 exact wiring anchors remain valid for v1 in an independent tutorial copy; delivered source rejects teaching01. The original FF-005 complete hold_ack forced-stop limitation remains. This slice's B-off is the known bootstrap-force/nonzero fault class, not normal closure; ordinary/slow-connect scenes require real join/reap and zero forced stops. No Modbus transport, DS export, POST, real-device, Windows/Linux or deployment proof is claimed.

For quantitative S1 acceptance, first stop both manual scenes and confirm the five ports are free, then run this bounded CLI matrix from FF_PROJECT. It includes S1 dry/execute and the other catalog isolation cases, checks at least ten identical post-issue body GETs within the original input age, and records the expected B-off failure separately. Use a new evidence directory; a first health result or nine GETs is not S1 acceptance.

```bash
FF004_EVIDENCE_ROOT="$FF_RUN_ROOT/s1-acceptance" cargo test --locked --features test-fixture --target-dir "$FF_RUN_ROOT/acceptance-target" --test multi_plc catalog_cli_matrix -- --nocapture --test-threads=1
```
