# Field Flow Rust

[中文](README.zh-CN.md)

Independent handwritten demo01 runtime: HTTP GET → strict synthetic command → two-byte DB INT write. Each PLC has one resident supervised driver process/session; flows run independently, with no overlapping iteration of one flow. Parent-owned SQLite intent and audit prevent automatic resend of confirmed/unknown commands. Unknown physical ranges block new writes and require a separately approved reconciliation procedure.

Requires Rust/Cargo 1.89+, a native C++ compiler and the committed Cargo.lock. Validated platform and precise results belong to FF-001 tasks; r4 retains the R14 adapter/lock and includes the QA1 Rust FIFO deadline, clock-anchor and actual-started repairs. Ready/queue waiting has its own limits; IO is timed from dispatch and remains clamped to original source expiry. Current DEV, independent QA verdict and Human Owner gates are recorded in the unique task. Build/run directly in this directory, or copy this directory alone. No sibling source, manifest, environment, writable state or service is required. The repository task links are documentation navigation only.

```bash
cargo build --locked --bins --features test-fixture
cargo test --locked --test s7_int_pdu
cargo test --locked --features test-fixture -- --test-threads=1
cargo run --locked --bin field-flow -- --help
cargo run --locked --bin field-flow -- --lang zh-CN --help
```

No arguments/help perform no configuration, network or state IO. Initialize a new private synthetic directory explicitly; its parent must exist and the directory must not exist. Normal run never creates/migrates schema. No reset/retry-unknown command exists.

```bash
cargo run --locked --bin field-flow -- state init --synthetic --mode dry_run --state-dir /private/tmp/ff-001-r1-my-run/dry --instance-id ff-rust-demo01
cargo run --locked --bin field-flow -- state init --synthetic --mode execute --state-dir /private/tmp/ff-001-r1-my-run/execute --instance-id ff-rust-demo01
cargo run --locked --features test-fixture --bin ff-fixture -- --config config/loopback.yaml --evidence-dir /private/tmp/ff-001-r1-my-run/fixture
# In a separate terminal; Ctrl-C stops the runtime. Press ENTER to stop the fixture.
cargo run --locked --bin field-flow -- run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-my-run/dry
cargo run --locked --bin field-flow -- run --config config/loopback.yaml --state-dir /private/tmp/ff-001-r1-my-run/execute --execute
cargo run --locked --bin field-flow -- state inspect --state-dir /private/tmp/ff-001-r1-my-run/execute
```

The checked example targets only this project's 127.0.0.1 synthetic S7 proxy/server (31102/31103) and HTTP (31880). Fixture conflicts fail without selecting another port or killing an occupant. INT uses signed big-endian -32768..32767. Source identity and original UTC expiry are immutable; dry_run and execute stores cannot be interchanged. SQLite is local execution state, not a Backend business database.

Runtime stdout and state-dir runtime.jsonl contain structured events. Logs rotate before full lines exceed 5 MiB, with at most four backups; necessary state history remains in append-only command_events. Default logical caps are 10000 commands/90000 admission events, with database/disk backpressure. Audit failure prevents new effects; confirmed history is retained. Stop closes the start gate, joins flows/owners, naturally closes children, then closes SQLite/audit within one global deadline. Forced termination is fault_cleanup/exit1, never graceful success. Parent loss ends its own driver and retains the inherited instance lock until that child ends.

`src/infrastructure/s7_int_pdu.rs` exclusively encodes one-item/two-byte DB INT payloads through the pinned public ISO API and validates exact ACK structure/reference. It uses a 4096-byte initialized FFI buffer and retires a bad session; it is not a general S7 stack. Test-only fault hooks require the test-fixture feature. No arbitrary raw product entry is exposed.

[Structure](CODE_INDEX.md), [task index](PLAN.md), [component notices](THIRD_PARTY_NOTICES.md). Source checks and finite loopback tests do not establish production/device readiness, long soak, cross-platform packaging, deployment or Human Owner acceptance.
