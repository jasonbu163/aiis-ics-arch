# Field Flow Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

This directory owns FF task details and future source. The repository plan provides cross-project navigation; it does not duplicate the FF task authority.

| Task ID | Aggregate status | Scope | Latest fact / next gate |
| --- | --- | --- | --- |
| FF-001 | `draft` (r3); r2 `dev_blocked` | [r3 dual runtimes and demo01](plans/FF-001-dual-runtime-demo01/spec.md) | Approved r2 compiled Rust and produced local protocol evidence, but an unmatched S7 write ACK was accepted and committed confirmed. PM proposes a restricted INT adapter using the same library's public raw ISO exchange API. Exact r3 approval is pending; all source/history/evidence remain, Python has not started, and there is no completed handoff or QA. |
| ARCH-TOOL-001 | `draft` | [r2 discussion baseline](plans/ARCH-TOOL-001-field-flow-runner/spec.md) | PM documents two independent implementations, long-running operation requirements and the CA relationship; complete r1 retained. The discussion baseline remains unchanged; the approved first implementation belongs to FF-001 r2. |

See the [task catalog](plans/README.md) for existing role documents. Local driver prechecks are recorded separately from full runtime build/startup, field, long-running and deployment acceptance.
