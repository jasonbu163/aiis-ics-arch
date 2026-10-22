# Field Flow Python

[中文](README.zh-CN.md)

Independent handwritten Python runtime for FF-001 r4. It owns configuration, HTTP, a FIFO owner and persistent S7 driver process for each PLC, SQLite execution state, JSONL audit, CLI and its own synthetic protocol fixtures. It requires no sibling source, executable, fixture, environment or writable state. Current DEV evidence and the exact QA gate belong to the [unique task](../plans/FF-001-dual-runtime-demo01/tasks.md); independent Verification and Human Owner acceptance remain separate.

Use existing CPython 3.11 (first platform: 3.11.12, macOS arm64), uv, this project's uv.lock and its own .venv. No interpreter download or global installation is needed:

```bash
uv lock --check --python 3.11 --no-python-downloads
uv sync --locked --python 3.11 --no-python-downloads
uv build --python 3.11 --no-python-downloads
uv run --locked --python 3.11 --no-python-downloads field-flow
uv run --locked --python 3.11 --no-python-downloads field-flow --lang zh-CN --help
```

No arguments/help only read the packaged locale; they create no state/log or connection. `run` requires explicit config/state paths and defaults to dry-run. `state init --synthetic` requires a new directory, creates schema1 explicitly, and never overwrites existing data. Normal run does no DDL; metadata/implementation/mode/instance mismatch fails. Inspect is read-only.

For the local synthetic example, create a new parent once and retain its path for the separate terminals:

```bash
FF_RUN_ROOT=$(mktemp -d /private/tmp/ff-001-r1-python-XXXXXX)
uv run --locked --python 3.11 --no-python-downloads field-flow state init --synthetic --mode dry_run --state-dir "$FF_RUN_ROOT/dry" --instance-id ff-python-demo01
uv run --locked --python 3.11 --no-python-downloads field-flow state init --synthetic --mode execute --state-dir "$FF_RUN_ROOT/execute" --instance-id ff-python-demo01
uv run --locked --python 3.11 --no-python-downloads python -m tests.fixtures --config config/loopback.yaml --evidence-dir "$FF_RUN_ROOT/fixture"
```

The fixture binds only 127.0.0.1:32102 (transparent S7 proxy), 32103 (its Python Server) and 32880 (synthetic GET). A port conflict fails without killing the owner or choosing another port. It serves one fresh fixed identity/value42; original source times remain unchanged, so it becomes stale after the configured max age. In another terminal, run either mode against the initialized corresponding directory:

```bash
uv run --locked --python 3.11 --no-python-downloads field-flow run --config config/loopback.yaml --state-dir "$FF_RUN_ROOT/dry"
uv run --locked --python 3.11 --no-python-downloads field-flow run --config config/loopback.yaml --state-dir "$FF_RUN_ROOT/execute" --execute
```

Stop each process with SIGINT/SIGTERM before proceeding. Run modes in sequence; dry-run records simulated only, execute allows one write per source/command identity. Inspect with `field-flow state inspect --state-dir PATH`. Full automated init/fixture/start/stop evidence uses `uv run --locked --python 3.11 --no-python-downloads python -m tests.fixtures.cli_smoke`.

Each demo01 round performs one bounded GET, strict typed/time validation and one execution-service call. Independent flow tasks do not overlap themselves or queue missed ticks. HTTP waits do not occupy the PLC FIFO. A single driver PID/session serializes all calls for that PLC; independent read test flows get separate sample/request identities. Health is emitted every5 seconds, with state/owner/flow counts and writable/capacity status; there is no health listener.

The child uses pinned python-snap73.0.0 public connect and exactly one public iso_exchange_buffer per job. The finite codec only encodes one-item/two-byte DB INT and validates the complete current reference/function/status/length before typed success. Raw refs2..65535 belong to each new Client (Setup uses1); exhaustion retires that session without replay. 4096 bytes is a cap **after** library receive; the original single-frame payload bound is65528, with possible temporary copies. Raw bodies never enter parent IPC or runtime logs. First bad response retires the old session; it never waits by resending.

The parent alone owns SQLite/audit, durable T1/T2/T3, original source identity and physical-range unknown blocking. A positive matching S7 ACK plus committed T3 means confirmed; it is not process/physical completion. A possibly sent write with an error becomes unknown and is never retried, including after restart/new ID/aliases or readback. The runtime offers no reset/replay/unknown reconciliation command.

Connect/IO total budgets include IPC and actual fault reap, with400ms reserved inside the original budget. The parent inherits the instance-lock share into its driver; loss of the parent aborts that child within500ms. Calling stop closes all start gates first; unstarted work is canceled. Flow/owner/HTTP/SQLite/audit cleanup uses one global shutdown deadline. Natural exit0 is separate from forced cleanup/unknown/audit failure exit1; invalid arguments/config/state exit2. A forced stop cannot undo an applied PLC write.

SQLite limits:10000 identities, admission pause at90000 events/48MiB main DB/256MiB free disk,64MiB main hard cap and128MiB including journal. Identity/events are never evicted. JSONL lines<=4096 bytes, files<=5MiB,4 backups,25MiB total; persisted audit flush/sync or stdout failure closes new-effect gates. Reads may continue. Confirmed progress is retained after later sink failure.

The fixture registers its own `IntMemory` bytearray through public Server.register_area and accepts only complete two-byte slices within its16-byte DB1. The original unmodified Server can partially assign an out-of-range write before returning an error; that real failed test remains in task evidence. The owned synthetic memory boundary is not a third-party fix or a real-PLC protection/block-size proof. Runtime config validates declared bounds separately. The historical high-level API failure remains reproducible by the explicitly failing `tests.python_api_preflight` module; it is not the production IO path or a passing test target.

Validation from this project only:

```bash
uv run --locked --python 3.11 --no-python-downloads python -m compileall -q src tests
uv run --locked --python 3.11 --no-python-downloads pytest -q tests/unit
uv run --locked --python 3.11 --no-python-downloads pytest -q tests/test_matched_ack_gate.py
uv run --locked --python 3.11 --no-python-downloads pytest -q tests/test_local_protocol.py
```

Gate uses reusable production state/owner/driver/execution, an inner110-second deadline and a120-second DEV harness including actual resource release. Full tests preserve three protocol frames, real counts/memory, three-table exports, PIDs, joins and rebinds in new `/private/tmp/ff-001-r1-r4-python-*` roots; tasks persist the key reports. Copy this whole directory excluding .venv/dist/cache/state/logs, then sync/build/start/test independently. The host package cache may be reused; a sibling environment may not.

Field endpoints, real operations, long soak, hosting, deployment, three-platform installers and physical exactly-once are outside this local candidate. [PLAN](PLAN.md), [code index](CODE_INDEX.md), [component notices](THIRD_PARTY_NOTICES.md).
