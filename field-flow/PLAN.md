# Field Flow Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

This directory owns FF task details and source. The repository plan provides cross-project navigation; it does not duplicate the FF task authority.

| Task ID | Aggregate status | Scope | Latest fact / next gate |
| --- | --- | --- | --- |
| FF-001 | `qa_passed` (r4) | [r4 Python response validation and dual runtimes](plans/FF-001-dual-runtime-demo01/spec.md) | Actual fresh QA2 passed both versions' local AC01–AC15 and independently closed three Rust QA1 defects; formal/isolated Rust full18 passed. Unchanged Python48 has verified QA1 full evidence plus fresh build/unit/gate/CLI checks. QA1 qa_failed/history retained; Human Owner final acceptance, field and long-running validation pending. |
| ARCH-TOOL-001 | `draft` | [r2 discussion baseline](plans/ARCH-TOOL-001-field-flow-runner/spec.md) | PM documents the independent implementations, long-running requirements and CA relationship; complete r1 retained. The baseline remains unchanged; implementation status belongs to the [FF-001 bundle](plans/FF-001-dual-runtime-demo01/spec.md). |

See the [task catalog](plans/README.md) for existing role documents. Local driver prechecks are recorded separately from full runtime build/startup, field, long-running and deployment acceptance.
