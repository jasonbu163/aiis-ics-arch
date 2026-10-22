# Field Flow

Chinese version: [README.zh-CN.md](README.zh-CN.md)

Field Flow (FF) is the home for independently maintained, handwritten field-flow runtimes that may work with Backend for an extended period while AW develops. This directory owns FF planning and future source; it is separate from the offline tools collection.

The partial Rust candidate compiles and has local protocol evidence, but r2 Development is blocked: the high-level S7 driver accepts an unmatched acknowledgement as success. [Development records and failure evidence](plans/FF-001-dual-runtime-demo01/tasks.md) are retained. The [r3 proposal](plans/FF-001-dual-runtime-demo01/spec.md) keeps the same libraries and adds a restricted INT request/response adapter through the public raw ISO exchange API; exact Human Owner approval is pending. Python has not started, and complete runtime acceptance and QA remain pending.

## Independent implementations

| Project | Own engineering surface |
| --- | --- |
| `field-flow-rust/` | Cargo manifest/lock, Rust source, configuration examples, tests and runtime data |
| `field-flow-python/` | Python project/uv lock, Python source, configuration examples, tests and runtime data |

Each implementation must be independently copyable, buildable and runnable. Neither depends on its sibling's source, executable, fixture process, virtual environment or writable state, or on a parent runtime manifest. Equivalent flow behavior and acceptance scenarios are shared; file and function layouts may follow each language.

The Rust directory contains a partial, blocked implementation; the Python directory is still planned. Full build/start instructions will accompany completed implementation and verification evidence.

## Handwritten flows

Each application flow module represents one logical flow. A stable flow ID and business name identify its trigger, steps, typed inputs/outputs, cross-round state and failure behavior. The runtime owns scheduling and lifecycle; infrastructure adapters own PLC/HTTP communication.

Initial scenarios are HTTP GET -> condition -> S7 DB write, and S7 DB read -> condition/rising edge -> HTTP POST. These describe intended scenarios, not implemented connectors or successful field tests.

## Backend and long-running operation

Backend retains business validation and business-data ownership. FF integrates through explicitly agreed APIs; API routes, acknowledgement and idempotency contracts still require confirmation. Site configuration and customer-specific rules belong to consuming projects.

The design target includes isolated flow supervision, bounded communication/reconnection, durable event and delivery state, unknown-result reconciliation, persistent rotating logs, health/progress reporting and orderly shutdown. Each implementation owns its local recovery data. Installation, schema creation, background hosting and field operations require separately defined implementation and validation scope.

One effective writer owns each conflicting flow/resource/business effect. Switching between Rust, Python or a future CA implementation must reconcile pending/unknown work and confirmed progress before transferring execution; independently managed databases are not implicitly interchangeable.

## Future CA relationship

FF remains independently maintainable. Its documented flows and validated scenarios may later inform CA node flows; AI-assisted source migration produces a candidate draft and requires behavior checks. CA editing, AI Chat and DeepSeek integration belong to the separate CA workstream.

The [CA follow-up prompt](plans/ARCH-TOOL-001-field-flow-runner/spec.md#ca-handoff-prompt) captures the proposed handoff. It has not been sent to the CA chat and does not authorize changes there.

## Documentation entrypoints

- [PLAN.md](PLAN.md) tracks FF-owned work and the next gate.
- [Task catalog](plans/README.md) links only role documents that exist.
- [Discussion baseline](plans/ARCH-TOOL-001-field-flow-runner/spec.md) owns detailed scope, decisions, staged acceptance and recoverable r1 history.
- [First implementation scope](plans/FF-001-dual-runtime-demo01/spec.md) defines the independent runtimes and demo01 local loop; r3 is a draft, with the complete approved r2/r1 history retained.
- [Repository contract](../AGENTS.md) and [development workflow](../.codex/workflows/development-lifecycle-workflow.md) continue to apply.
