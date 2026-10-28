# Field Flow — Python / Rust comparison

[中文](USER_GUIDE.zh-CN.md)

Python is for learning, practice and rapid prototypes; this task does not package it. Rust is the main direction for future long-running deployment runtimes. Future production flows are not required to be implemented in both languages. Existing Python code, functionality, tests and FF-001 evidence are preserved. Neither language choice nor this guide establishes production readiness.

## Reader route

1. Read this comparison, then choose ONE project’s complete local guide.
2. [Python USER_GUIDE](field-flow-python/USER_GUIDE.md) — source environment, CLI, two lessons, actual method contracts and teaching01 wiring.
3. [Rust USER_GUIDE](field-flow-rust/USER_GUIDE.md) / [BUILD](field-flow-rust/BUILD.md) — release/fixture preparation, independent runtime lessons and native/platform limits.

Each project can be copied alone, with its own manifest/lock, source, config, locale, fixture and state. No parent guide, sibling environment/executable/service or Backend/DS is necessary to follow its complete tutorial. Parent task links are optional governance references.

| Responsibility | Rust | Python |
| --- | --- | --- |
| Entry / environment | `src/main.rs → commands.rs; Cargo.toml/Cargo.lock; Rust ≥1.89` | `src/field_flow/__main__.py → cli.py; pyproject.toml/uv.lock; existing CPython3.11 / uv` |
| One bounded app round | `src/app/demo01.rs::iteration(&Flow,&Plc,&Http,&Owner,&State,&Stop,&mut Clock)` | `src/field_flow/app/demo01.py::once(http,flow,plc,execution)` |
| Configuration | `src/config.rs::Config/Flow/Plc/Target/Http` | `src/field_flow/config.py dataclasses; parse/load` |
| HTTP / command conversion | `services::Http::get → domain::Input::intent` | `HttpClient.get → domain.parse_input` |
| Durable execution | `Execution {owner,state,stop}.apply(intent,clock) → Result<()>` | `Execution(state,owner,clock).apply(intent) → status string` |
| PLC read / ownership | `runtime::Owner::read(flow,db,offset) → Sample` | `owner.Owner.read(flow,db=1,offset=0) → Sample` |
| Dispatch / lifecycle | `src/runtime.rs::Runtime::launch_flows/shutdown` | `src/field_flow/runtime.py::Runtime._flow/close` |
| Registration | `app/mod.rs + config.rs kind check + runtime.rs dispatch` | `runtime.py import+dispatch + config.py kind check; app/__init__.py stays thin` |
| Manual fixture | `test-fixture ff-fixture; ENTER; protocol.json` | `python -m tests.fixtures; SIGINT/SIGTERM; report.json` |
| Fixed loopback ports | `proxy31102 / native server31103 / HTTP31880` | `proxy32102 / server32103 / HTTP32880` |
| Command identity | `cmd-001 / demo01-feed / value42` | `fixture-UUID / first-flow source / value42` |
| Runtime locale | `locales/*.json compiled with include_str!` | `own installed locale files or project locales fallback` |
| Long-term direction | `deployment-runtime development; platform/field/hosting gates remain` | `learning/prototype source usage; no packaging in FF-002` |

The Python signatures are actual duck-typed object contracts, not an already typed SDK. Internal layouts and error keys differ; keep semantics aligned without assuming a line-for-line API.

## One iteration, step by step

1. Runtime gives one app round its Flow/Plc and shared HTTP client, PLC owner and durable state. It maintains the original per-flow Clock.
2. Rust checks clock then awaits http.get(&f.get_url); Python once awaits http.get(flow.get_url), and Execution checks its Clock before admission. HTTP awaits do not occupy a PLC queue.
3. Rust input.intent(f,p)? and Python parse_input(incoming,flow,plc) strictly validate the seven-key ready command. None means idle; invalid values are errors, not defaults.
4. Rust constructs Execution {owner,state,stop}.apply(intent,clock).await?; Python awaits execution.apply(intent). Both persist identity/state before a permitted write. App code never calls raw driver writes.
5. A matching S7 INT ACK plus local T3 commit makes confirmed; no proof after a possible send is unknown. This is not physical process completion.
6. Return to runtime, then await interval_ms. Different flow tasks remain concurrent; each flow does not overlap itself or catch up missed ticks. One PLC session serializes its own IO only.

Both complete guides include the full equivalent teaching01 app, YAML, exact module/import/kind/dispatch edits and build/import plus CLI validation. The delivered code still accepts only demo01; files are not automatically discovered. teaching01 is the same GET→INT capability with a different flow/business identity, not demo02. POST/auth, BOOL/DINT/REAL and rising-edge flows are not implemented. Writes must pass through Execution.apply.

## Fixture, state and evidence boundaries

Each manual fixture owns a synthetic HTTP source, transparent TCP proxy and a real S7 server over 16-byte DB1 memory; proxy legs are not separate business clients. Rust has a native server child; Python spawns its own server child with server threads. It is not DS. Automated tests can mutate internal feed/faults, but manual CLIs have no continuous command generator or control panel. Commands have one issuance time and expiry (Rust 60 seconds, Python 30 seconds); default input_max_age_ms=10000 allows only ten seconds after startup. Finish dependencies/build/init first, then start a fixture and immediately run one mode. dry-run and execute use separate fresh teaching scenes, not the same ten-second window.

state init --synthetic explicitly creates a new schema1 directory; normal run never creates schema. Default run is dry_run, --execute requires a separately initialized execute store. implementation/mode/instance/schema must match. Inspect is read-only; health is JSONL, not an HTTP endpoint. Persisted identities and physical unknown-overlap blocking survive restart. Restart the original execution scene with its original state and identities; never delete/reset/copy running databases, refresh same-ID timestamps or switch IDs to force replay. Rust/Python writable state is not interchangeable. Writer transfer requires stopping the old writer and reconciling unresolved/confirmed progress; cross-host fencing is absent.

Source Unix milliseconds and monotonic durations retain their meanings. Existing SQLite calendar metadata and JSONL timestamps are UTC, unlike the current root Asia/Shanghai calendar-storage contract. This documentation reports that limitation without rewriting implementation, schema or history. Platform ports, time-data migration, field endpoints, DS/Backend integration, service management, backup/upgrade, long-soak/capacity and distribution require separate approval and evidence.

FF-001 r4 passed independent local QA2 but awaits Human Owner final acceptance. FF-002 documents and bounded rehearsals have their own [spec](plans/FF-002-user-guide-and-runtime-positioning/spec.md) and [Development record](plans/FF-002-user-guide-and-runtime-positioning/tasks.md); Development self-check is not independent QA. [FF PLAN](PLAN.md) indexes the next gate.
