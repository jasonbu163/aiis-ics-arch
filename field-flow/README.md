# Field Flow

Chinese version: [README.zh-CN.md](README.zh-CN.md)

Field Flow (FF) is the home for independently maintained, handwritten field-flow runtimes that may work with Backend for an extended period while AW develops. This directory owns FF planning and source; it is separate from the offline tools collection.

The exact [FF-001 r4](plans/FF-001-dual-runtime-demo01/spec.md) [dual-version Development handoff](plans/FF-001-dual-runtime-demo01/tasks.md) passed fresh-context [QA2](plans/FF-001-dual-runtime-demo01/checklist.md), covering local AC01–AC15 for both projects. Rust queued IO deadlines, pre-call clock guards and actual started statistics were independently verified after repair; formal/isolated full18 passed. Python48 is unchanged, with verified QA1 complete independent evidence and fresh build/unit/gate/CLI checks. All earlier failures/candidates remain. Human Owner final acceptance, field validation and long-running acceptance are pending.

Python is for learning, practice and rapid prototypes, with no packaging in this task. Rust is the main direction for future long-running deployment runtimes. Existing Python functionality/tests and QA remain; future production flows need not be duplicated in both languages. Target-platform, field, hosting, capacity and long-soak acceptance remain separate gates.

See [USER_GUIDE](USER_GUIDE.md) for comparison and reader routes, the complete standalone [Rust guide](field-flow-rust/USER_GUIDE.md), [Python guide](field-flow-python/USER_GUIDE.md) and [Rust BUILD](field-flow-rust/BUILD.md).

## Independent implementations

| Project | Own engineering surface |
| --- | --- |
| `field-flow-rust/` | Cargo manifest/lock, Rust source, configuration examples, tests and runtime data |
| `field-flow-python/` | Python project/uv lock, Python source, configuration examples, tests and runtime data |

Each implementation must be independently copyable, buildable and runnable. Neither depends on its sibling's source, executable, fixture process, virtual environment or writable state, or on a parent runtime manifest. The current comparison shares equivalent behavior and acceptance scenarios; future work need not duplicate every flow, and layouts may follow each language.

The [Rust project guide](field-flow-rust/README.md) and [Python project guide](field-flow-python/README.md) provide each project's independent build/start/validation commands. Both implement demo01's local HTTP GET → PLC INT loop and passed independent local QA. Field validation and long-running acceptance remain later stages.

## Handwritten flows

Each application flow module represents one logical flow. A stable flow ID and business name identify its trigger, steps, typed inputs/outputs, cross-round state and failure behavior. The runtime owns scheduling and lifecycle; infrastructure adapters own PLC/HTTP communication.

demo01 is HTTP GET -> condition -> S7 DB INT write; both Rust and Python candidates have local DEV evidence. demo02, S7 DB rising edge -> HTTP POST, belongs to the next increment.

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
- [First implementation scope](plans/FF-001-dual-runtime-demo01/spec.md) defines the independent runtimes and demo01 local loop; exact r4 is owner-approved, with complete approved r3/r2/r1 history retained.
- [Repository contract](../AGENTS.md) and [development workflow](../.codex/workflows/development-lifecycle-workflow.md) continue to apply.
