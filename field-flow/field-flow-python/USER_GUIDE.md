# Field Flow Python — User guide

[中文](USER_GUIDE.zh-CN.md)

Python is for learning, practice and rapid prototypes; this task does not package Python. FF-001 r4 implemented the local demo01 loop; independent QA2 passed, while Human Owner final acceptance remains pending. This guide does not establish field, hosting, capacity, long-soak or production readiness. Future production flows are not required to have two language implementations. Existing Python functionality/tests and historical evidence remain valid.

## 1. Independent project and prerequisites

Copy this entire project, excluding target, .venv, dist, caches, state directories, gate/lock runtime files and logs. Preserve uv.lock (the dependency lock is source). Use its own sources, config, locales and fixture; no parent/sibling process, executable or environment is required. Parent task links in README are optional governance navigation.

```text
src/field_flow/__main__.py → cli.py → runtime.py
src/field_flow/app/demo01.py → services/execution.py
src/field_flow/{config,domain,owner,driver_process}.py
src/field_flow/infrastructure/{http,state,audit,s7_int_pdu}.py
pyproject.toml, uv.lock, .python-version, config/loopback.yaml, locales/, tests/fixtures/
```
These commands use the repository checkout below. For a standalone copy, first change to its real absolute project directory instead. Terminal A remains at that project root throughout preparation. Missing tools are a prerequisite failure; do not install interpreters, targets or system toolchains automatically.

```bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch/field-flow/field-flow-python
FF_PROJECT=$(pwd -P)
FF_LESSON=$(mktemp -d /private/tmp/ff-002-r1-python-XXXXXX)
printf "%s\n" "$FF_PROJECT" "$FF_LESSON"
uv --version
uv lock --check --python 3.11 --no-python-downloads
uv sync --locked --python 3.11 --no-python-downloads
uv run --locked --python 3.11 --no-python-downloads python --version
FF_BIN="$FF_PROJECT/.venv/bin/field-flow"
mkdir "$FF_LESSON/empty" "$FF_LESSON/dry-lesson" "$FF_LESSON/execute-lesson"
(cd "$FF_LESSON/empty" && "$FF_BIN" && "$FF_BIN" --lang en-US --help && "$FF_BIN" --lang zh-CN --help)
ls -A "$FF_LESSON/empty"
"$FF_BIN" state init --synthetic --mode dry_run --state-dir "$FF_LESSON/dry-lesson/state" --instance-id ff-python-demo01
"$FF_BIN" state init --synthetic --mode execute --state-dir "$FF_LESSON/execute-lesson/state" --instance-id ff-python-demo01
```
The empty directory must stay empty, and help exits 0 without config/network/state IO. All builds, dependency preparation and both explicit initializations happen before starting any fixture. State init creates a new child directory and refuses an existing directory; its parent must exist. Normal run never creates schema.

Use existing CPython 3.11 and uv with this uv.lock; never borrow a sibling .venv. The shell may lack a python3.11 command while uv can locate an existing 3.11 interpreter. A cache/network failure must be reported; an existing normal package cache is permitted. This is source usage, not exe/wheel/sdist, PyInstaller/Nuitka, offline distribution or installer delivery. Keep the existing build backend and historical build evidence. Python uses fcntl/Unix lifecycle operations; Windows readiness is not established.

## 2. What the fixture actually starts

| Component | Address / responsibility |
| --- | --- |
| HTTP | `127.0.0.1:32880/demo01/command` — one synthetic GET command |
| S7 proxy | `127.0.0.1:32102` — transparent frame forwarding, counts/trace, test-only faults |
| S7 server | `127.0.0.1:32103` — real S7 service over registered 16-byte DB1 memory |

The fixture parent owns HTTP/proxy threads and spawns a Python S7 server child, which owns registered IntMemory bytearray and its server threads (tests/fixtures/runtime.py::server_child). The runtime is a separate process; each PLC owner starts one persistent driver child/session. Two proxy TCP legs do not mean two business PLC clients. This bounded protocol fixture is not the Device Simulator (DS) product; DS, Backend, Docker and the other language are unnecessary.

Wait for {"event":"fixture_ready","implementation":"python"}; it supplies fixture-UUID, value 42 and source_id from the first configured flow. Command timestamps are generated once (expiry = issuance + 30000 ms). Repeated GET never refreshes them. The default input_max_age_ms=10000 gives only 10 seconds to start the runtime after fixture startup, even though expiry is 30 seconds. Prepare Terminal B’s command before starting Terminal A’s fixture. Stale input is expected once age exceeds 10 seconds.

Automated tests can mutate feed/faults internally; the manual CLI has no control panel, management API, continuous command generator, arbitrary point table or interactive fault editing. This guide uses DB1 size16 offset0; this fixture validates DB1/16 and in-bounds offsets, with one loopback PLC endpoint. Use only the published loopback sample here; configurable DB/address ranges do not enlarge fixture capabilities. Python’s guarded 2-byte IntMemory is a fixture boundary, not proof of real PLC write protection; tests.python_api_preflight intentionally preserves a historical upstream API failure and is not a normal green path.

## 3. Two separate, bounded teaching runs

Before each fixture, check all three ports read-only. If any listener exists, stop this exercise and report the conflict. Do not kill occupants or change ports. lsof exit 1 with no output means no matching listeners.

```bash
lsof -nP -iTCP:32102 -iTCP:32103 -iTCP:32880 -sTCP:LISTEN
```
Terminal B: explicitly read the real absolute project and lesson paths printed by A (paste each path as one line, no quotes). Shell variables are not shared. Keep this shell for run/inspect.

```bash
read -r FF_PROJECT
read -r FF_LESSON
cd "$FF_PROJECT"
FF_BIN="$FF_PROJECT/.venv/bin/field-flow"
```
The fixture commands below invoke this project’s prepared .venv/bin/python directly (equivalent to uv run --locked --python 3.11 --no-python-downloads python -m tests.fixtures after sync). This makes the foreground fixture the actual process receiving Ctrl-C; if scripting, signal its exact PID and wait, rather than signaling only a uv wrapper.

### Dry-run lesson

A, project cwd; start fixture in a never-existing report directory:

```bash
"$FF_PROJECT/.venv/bin/python" -m tests.fixtures --config "$FF_PROJECT/config/loopback.yaml" --evidence-dir "$FF_LESSON/dry-lesson/fixture"
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
A: press Ctrl-C (SIGINT) and wait for the fixture foreground command to return; expect report.json. SIGTERM is also handled. Immediately record the fixture exit code in A:

```bash
FF_FIXTURE_EXIT=$?
printf "fixture exit=%s\n" "$FF_FIXTURE_EXIT"
```

Switch back to the same Terminal B retained from section3 (project cwd), then run the report, port and runtime/driver/server PID checks below. Only B assigned FF_PID from this run’s $!; A does not use it. Verify the printed PID is the original positive integer for this run; stop on an empty or wrong PID. For a valid PID, ps exit1 means absent only when both stdout and stderr are empty; invalid-argument or permission diagnostics are check failures.


```bash
cat "$FF_LESSON/dry-lesson/fixture/report.json"
cat "$FF_LESSON/dry-lesson/stderr.txt"
lsof -nP -iTCP:32102 -iTCP:32103 -iTCP:32880 -sTCP:LISTEN
printf "checking runtime PID=%s\n" "$FF_PID"
ps -p "$FF_PID" -o pid=,stat=,command=
```
Expected: inspect counts simulated=1, fixture writes=0. Normal runtime and fixture exit 0; no listener and recorded runtime PID absent. Also extract the driver_ready pid from stdout.jsonl and server_pid from fixture/report.json; use ps -p on each exact PID and require absence. Fixture server_exit/server_close.exit_code must be 0, server_close.remaining_threads empty, and report ports_rebound must contain all three Python ports. Sending SIGINT alone is not release evidence.

### Execute lesson

A, project cwd; start fixture in a never-existing report directory:

```bash
"$FF_PROJECT/.venv/bin/python" -m tests.fixtures --config "$FF_PROJECT/config/loopback.yaml" --evidence-dir "$FF_LESSON/execute-lesson/fixture"
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
A: press Ctrl-C (SIGINT) and wait for the fixture foreground command to return; expect report.json. SIGTERM is also handled. Immediately record the fixture exit code in A:

```bash
FF_FIXTURE_EXIT=$?
printf "fixture exit=%s\n" "$FF_FIXTURE_EXIT"
```

Switch back to the same Terminal B retained from section3 (project cwd), then run the report, port and runtime/driver/server PID checks below. Only B assigned FF_PID from this run’s $!; A does not use it. Verify the printed PID is the original positive integer for this run; stop on an empty or wrong PID. For a valid PID, ps exit1 means absent only when both stdout and stderr are empty; invalid-argument or permission diagnostics are check failures.


```bash
cat "$FF_LESSON/execute-lesson/fixture/report.json"
cat "$FF_LESSON/execute-lesson/stderr.txt"
lsof -nP -iTCP:32102 -iTCP:32103 -iTCP:32880 -sTCP:LISTEN
printf "checking runtime PID=%s\n" "$FF_PID"
ps -p "$FF_PID" -o pid=,stat=,command=
```
Expected: inspect counts confirmed=1, fixture writes=1 and report memory_hex starts with 00 2a at DB1 offset 0. Normal runtime and fixture exit 0; no listener and recorded runtime PID absent. Also extract the driver_ready pid from stdout.jsonl and server_pid from fixture/report.json; use ps -p on each exact PID and require absence. Fixture server_exit/server_close.exit_code must be 0, server_close.remaining_threads empty, and report ports_rebound must contain all three Python ports. Sending SIGINT alone is not release evidence.

Only this brand-new synthetic lesson starts with fresh directories; this is not incident recovery. Restart an existing execute scene with exactly its original state/config/instance/source/command identity; do not rerun init, delete state, replace the fixture to refresh cmd-001, edit timestamps or invent new IDs to evade deduplication/unknown. A stale input produces no new write; duplicates with unchanged identity are suppressed, changed immutable content produces identity_conflict. New independent lessons must never be used to conceal results from an old scene.

Normal native/Python server disconnect can print “Expected COTP DT, got 0x80” to fixture stderr when the client disconnects. Preserve it and verify exit0, no remaining server threads, joined proxy threads and released ports; that line alone is not a forced-cleanup verdict.

## 4. Configuration and input contract

config/loopback.yaml is the complete runnable sample. Objects are Config → Plc[], Flow[] → Target, Http. Unknown/missing fields and implicit string/boolean-to-integer conversions are rejected. IDs use ASCII A–Z/a–z/0–9/_/- with length 1–64. flow.id selects identity; kind selects explicit app dispatch; business_name describes the rule; source_id must match the feed. They are different roles.

| Field | Accepted value / relation |
| --- | --- |
| `schema_version / instance_id` | 1 / valid_id; must match state |
| `plcs / flows` | 1–4 / 1–8; unique IDs, unique PLC host:port |
| `plc.host / port / rack / slot` | literal IPv4 / 1–65535 / 0–7 / 0–31 |
| `connect_timeout_ms / io_timeout_ms` | PLC: 500–3000 / 500–5000 |
| `queue_capacity / queue_wait_ms / ready_wait_ms` | 1–16 / 100–5000 / 100–5000 |
| `flow.kind / interval_ms / input_max_age_ms` | demo01 only before tutorial / 100–10000 / 1–60000 |
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

One iteration awaits GET → validates input → returns on idle → admits intent and awaits Execution.apply. The runtime owns the outer loop: finish one iteration, then wait interval_ms; no same-flow overlap or catch-up ticks. Different flows are async tasks. One reused HTTP client serves the runtime; HTTP/interval waits do not hold the PLC FIFO. Each PLC owner reuses one child/session, serializing only its own IO. Each read creates independent request/sample identities; no shared snapshot or business mutual exclusion. See this project’s tests/test_local_protocol.py::test_three_read_flows_and_slow_http. These tests call services directly; the manual CLI still accepts only registered kinds.

Ready waiting, FIFO capacity/queue waiting and actual dispatch connect/IO have separate budgets. Connect/IO total deadlines include IPC and actual fault reaping; the 400ms cleanup reserve stays inside the original budget and never refreshes source time. Expiry/clock/gates are checked again at queue/dequeue/true start. T2=in_flight means a durable dispatch permit, not that a native call has started; owner health in_flight uses the actual started event. Failed connections use bounded 250/500/1000/2000ms backoff and a 10-second cooldown per cycle; unknown writes are not replayed, and independent flows/HTTP may continue.

T1 persists source/command identity, immutable payload/config/physical target and pending (or simulated in dry_run). T2 persists dispatch_count=1 and in_flight before a permitted external call. T3 persists confirmed only after a matching typed S7 ACK. confirmed proves protocol ACK plus local commit, not machine/process completion. No ACK proof after a possible send becomes unknown; restart recovers in_flight to unknown. expired/canceled mean a classified failure before or at a guarded phase; they do not undo an already applied write. Unknown physical overlaps block writes despite aliases/new identities/readback. There is no unknown-resolution/retry/clear-state CLI. Preserve original state/logs and stop the writer for review.

Each state directory has state.sqlite (schema1 store_meta/commands/command_events), instance.lock, transient gate-* and runtime.jsonl plus .1… .4. SQLite is local execution truth, not the Backend business DB. state inspect is read-only and reports meta and counts; runtime health is JSONL, not a listening API. Relative CLI paths resolve from cwd; use the printed absolute paths. Do not share or interchange Rust/Python writable databases or dry_run/execute stores. A writer handoff must stop the old side and reconcile pending/unknown and confirmed progress. Local inherited locks/start gates are not cross-host fencing.

Capacity: 10000 command identities; admission pauses at 90000 events, DB ≥48 MiB or free disk <256 MiB; DB hard cap64 MiB and DB+journal cap128 MiB. No automatic identity/event eviction. JSONL line ≤4096 bytes; file ≤5 MiB with four backups (25 MiB total). Required audit persist/flush/sync/stdout failure closes new write gates; confirmed does not regress after a later sink failure. Recognize identity_conflict, target_unknown, clock_invalid, audit_unhealthy/audit_* and capacity_paused from stderr/health/state; stop and preserve evidence, do not increase limits or clear history as recovery.

Useful event keys: `process_start, driver_spawn, driver_ready, intent, in_flight, ack, flow_health, progress, stop_joined, resources_released, shutdown_complete`. Some state events use more specific event names; inspect the actual JSONL.

Normal SIGINT/SIGTERM closes all start gates, cancels queued/unstarted work, classifies in-flight results conservatively, joins flows/owners, closes HTTP and waits/reaps child processes and state/audit thread within one shutdown budget. A forced kill, forced_driver_stop, fault_cleanup or shutdown_incomplete is not normal success. Do not kill by process name/port. Exit0 means normal completion; Rust CLI/config/state-prefixed errors exit2 and other runtime errors exit1. Python argument/config/state startup failures normally exit2, close fault/unknown exits1 (shutdown_incomplete is1); not every Python runtime failure maps to1. Read the actual error key and logs.

Current time limitation: source issued/expires/sampled/health *_ms are Unix milliseconds, while durations/deadlines use monotonic time; do not add eight hours to numeric epochs. Current SQLite calendar metadata uses UTC Z strftime; Python JSONL explicitly uses UTC +00:00 and Rust tracing timestamps use UTC. This differs from the root Asia/Shanghai calendar-storage contract. FF-002 reports it without migrating schema/history/logs; future implementation/data compatibility work requires its own approved scope.

## 6. Methods available to app code

These are source-level contracts, not a versioned public SDK. The current functions lack full annotations: contracts below describe actual objects; Failure carries a stable string key. await asynchronous methods and let the runtime classify Failure; do not blanket-retry writes.

| Path / owner | Actual signature | Usage / result / errors |
| --- | --- | --- |
| `src/field_flow/app/demo01.py` | `async once(http,flow,plc,execution)` | HttpClient, Flow, Plc, Execution; returns idle or apply status; runtime owns objects |
| `src/field_flow/infrastructure/http.py` | `HttpClient(config); async get(url); async close()` | config=Http; get returns parsed JSON dict; http_status/http_content_type/http_body_size/http_deadline/http_error/input_schema; close by runtime |
| `src/field_flow/domain.py` | `parse_input(body,flow,plc)` | sync; body=dict → Intent or None; strict input_schema/input_stale; config dataclasses supplied by runtime |
| `src/field_flow/domain.py` | `Intent.validate_time(wall=None); deadline()` | sync; None return validation or Failure(input_stale); deadline float monotonic seconds |
| `src/field_flow/domain.py` | `Clock(); check(wall=None)` | sync; None or Failure(clock_invalid), original per-flow anchor |
| `src/field_flow/services/execution.py` | `Execution(state,owner,clock); async apply(intent)` | State/Owner/Clock; status string simulated/confirmed or existing terminal state; target_unknown/command_in_flight/identity_conflict/audit_unhealthy/clock_invalid plus IO errors |
| `src/field_flow/owner.py` | `async Owner.read(flow,db=1,offset=0); snapshot()` | read → Sample dataclass (value, quality, request_id, flow_id, generation, sampled_at_ms, reference); snapshot sync dict; owner_unavailable/queue_unavailable/expired/canceled/flow_inflight/s7_* |
| `src/field_flow/config.py` | `load(path); parse(data)` | sync, path→Config or dict→Config; immutable Flow/Plc/Target/Http dataclasses in section4; config_schema/config_*; composition root owns load |
| `src/field_flow/domain.py` | `Clock.wall / Clock.mono / Clock.invalid; check(wall=None)` | original wall milliseconds / monotonic seconds / latched bool. Python has no public anchor() method; owner/driver maintain their own internal clock checks. Do not invent a Rust-shaped SDK |
| `src/field_flow/runtime.py; owner.py` | `Runtime.stop:asyncio.Event; Owner.stopped:asyncio.Event; Owner.stop(); async Runtime.close()` | runtime lifecycle owns set/close; app can inspect execution.owner.stopped.is_set(); close→(normal:bool,summary:dict), or Failure(shutdown_incomplete); do not stop the whole runtime per round |
| `src/field_flow/infrastructure/state.py` | `inspect(directory,tables=False); async State.snapshot()` | inspect sync CLI read-only meta/counts (CLI does not expose tables=True); snapshot async health dict {commands,log_writable,capacity}; state_read/state_*; state owner thread |
| `src/field_flow/infrastructure/state.py` | `async State.event(event,**fields)` | internal observation through state/audit owner; e.g. await execution.state.event("observation", result="ok"); audit_persist/state_* Failure; not a direct SQL/transition route |

Log observation is best done using the existing runtime events in section5; an app must not create a second Audit writer or close shared HTTP/state services.


Read example inside a bounded app iteration (use a distinct flow request label):

```python
sample = await execution.owner.read("teaching-read", flow.target.db_number, flow.target.byte_offset)
value = sample.value
```
This does not add a registered read flow. Read quality good means a validated protocol sample at sampled_at_ms, not physical completion.

Composition/lifecycle only: config.load/parse, Runtime.open/snapshot/close, State.open/close. State.admit/dispatch/finish and Owner.submit("write",...) are infrastructure used by Execution; do not call them to bypass durable execution. Driver.spawn/call/close, raw iso_exchange, S7 codec, gate/lock, SQL and fixture mutation hooks are internal/test surfaces. No public method for HTTP POST/auth, BOOL/REAL or automatic case discovery exists. The full demo01 code in section7 shows the shortest supported write route.

## 7. Add teaching01 with the same capability

Do this only in a new independent tutorial source copy, never as incident recovery or as an unapproved edit to the delivered runtime. teaching01 deliberately repeats GET→INT; it is not demo02/rising-edge/POST. Adding a file or YAML alone does not register a kind. First finish/stop section3. Preserve old state. Use a fresh copy with its own environment/targets; no sibling imports.

Terminal A still has FF_PROJECT from section1. Copy the tutorial source to a new project (no state/environment/target), then edit only that copy:

```bash
FF_TUTORIAL=$(mktemp -d /private/tmp/ff-002-r1-teaching-python-XXXXXX)
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

Create the complete file `src/field_flow/app/teaching01.py`:

```python
"""teaching01教学：单轮GET→严格typed条件→执行服务；无调度、SQL或PLC协议调用。"""
from field_flow.domain import parse_input


async def once(http, flow, plc, execution):
    incoming = await http.get(flow.get_url)
    intent = parse_input(incoming, flow, plc)
    return "idle" if intent is None else await execution.apply(intent)
```
Wire each existing file in the copy. The actual import lives in runtime.py, not app/__init__.py. Keep that initializer side-effect-free; config.py accepts the new kind and runtime.py explicitly dispatches it. The following small edit script has exact-match assertions; stop if the baseline changed instead of guessing. Run from the tutorial project root using an existing helper Python, which only edits text:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path("src/field_flow/config.py")
s = p.read_text()
old = 'f.kind == "demo01"'
assert s.count(old) == 1
p.write_text(s.replace(old, 'f.kind in ("demo01", "teaching01")'))
p = Path("src/field_flow/runtime.py")
s = p.read_text()
assert s.count('from field_flow.app import demo01') == 1
s = s.replace('from field_flow.app import demo01', 'from field_flow.app import demo01, teaching01')
old = 'result = await demo01.once(self.http, flow, plc, execution)'
new = 'case = {"demo01": demo01.once, "teaching01": teaching01.once}[flow.kind]\n                result = await case(self.http, flow, plc, execution)'
assert s.count(old) == 1
p.write_text(s.replace(old, new))
PY
```
Create config/teaching01.yaml in this copy, complete contents:

```yaml
# FF-001 synthetic loopback；不是现场目标授权。
schema_version: 1
instance_id: ff-python-teaching01
plcs:
  - id: plc_demo
    host: 127.0.0.1
    port: 32102
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
    get_url: http://127.0.0.1:32880/demo01/command
    target: {plc_id: plc_demo, db_number: 1, db_size_bytes: 16, byte_offset: 0, type: INT}
    input_max_age_ms: 10000
http: {connect_timeout_ms: 500, total_timeout_ms: 1500, pool_wait_ms: 500, max_connections: 8, max_body_bytes: 4096}
shutdown_timeout_ms: 15000
```
flow ID/business/instance changed; source demo01-feed and DB1/16/offset0 remain because the manual fixture is fixed. Run only this one flow, never alongside demo01 on its overlapping physical target. Config overlap checks reject an accidental combined configuration. No new locale keys or CLI text were added, so neither locales/en-US.json nor zh-CN.json changes. In your consuming tutorial copy add teaching01 to CODE_INDEX.md and link its local instructions from README; do not claim the delivered source already includes it.

```bash
uv sync --locked --python 3.11 --no-python-downloads
uv run --locked --python 3.11 --no-python-downloads python -m compileall -q src
uv run --locked --python 3.11 --no-python-downloads python -c 'from field_flow.config import load; from field_flow.app import teaching01; c=load("config/teaching01.yaml"); assert c.flows[0].kind == "teaching01"; assert callable(teaching01.once)'
```
Complete both modes below in the new copy. FF_PROJECT/FF_LESSON refer to the new printed paths; do not cd back to the original checkout. Initialize first, then start one fixture at a time.

```bash
FF_BIN="$FF_PROJECT/.venv/bin/field-flow"
mkdir "$FF_LESSON/dry-lesson" "$FF_LESSON/execute-lesson"
"$FF_BIN" state init --synthetic --mode dry_run --state-dir "$FF_LESSON/dry-lesson/state" --instance-id ff-python-teaching01
"$FF_BIN" state init --synthetic --mode execute --state-dir "$FF_LESSON/execute-lesson/state" --instance-id ff-python-teaching01
```

In Terminal B repeat section3’s two read -r lines with the new project/lesson paths, cd and set FF_BIN again. Check free ports with the section3 lsof command first.

**dry — A**

```bash
"$FF_PROJECT/.venv/bin/python" -m tests.fixtures --config "$FF_PROJECT/config/teaching01.yaml" --evidence-dir "$FF_LESSON/dry-lesson/fixture"
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
A: press Ctrl-C to close the fixture and immediately record FF_FIXTURE_EXIT in A as in section3. Then switch back to B, which retained this run’s FF_PID, to check reports, valid exact PIDs and port release before the next mode. A does not use B’s FF_PID.

**execute — A**

```bash
"$FF_PROJECT/.venv/bin/python" -m tests.fixtures --config "$FF_PROJECT/config/teaching01.yaml" --evidence-dir "$FF_LESSON/execute-lesson/fixture"
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
A: press Ctrl-C to close the fixture and immediately record FF_FIXTURE_EXIT in A as in section3. Then switch back to B, which retained this run’s FF_PID, to check reports, valid exact PIDs and port release before the next mode. A does not use B’s FF_PID.

Expect simulated1/write0 in dry-run, confirmed1/write1 in execute, and inspect meta.instance_id=ff-python-teaching01. Fixture load and product startup validate kind; Rust compilation alone does not validate YAML. Preserve old state; no schema/driver/API change is required.

## 8. Verification and limits

The bounded FF-002 rehearsal uses the actual product CLI in independent macOS arm64 copies, separate new synthetic dry/execute scenes and both wired tutorial cases; evidence and failures belong to the FF-002 tasks bundle. It is Development self-check until fresh Verification records its own verdict. No FF-001 full fault matrix rerun, real endpoint/PLC, DS joint validation, production hosting, platform port, long soak or distribution compliance is claimed. Preserve report/PID/exit/port evidence before any eventual task-owned resource cleanup.

Local navigation: [README](README.md), [CODE_INDEX](CODE_INDEX.md), [notices](THIRD_PARTY_NOTICES.md).
