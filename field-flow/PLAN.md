# Field Flow Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

This directory owns FF task details and source. The repository plan provides cross-project navigation; it does not duplicate the FF task authority.

| Task ID | Aggregate status | Scope | Latest fact / next gate |
| --- | --- | --- | --- |
| FF-005 | `owner_accepted` (r1) | [Basic and advanced example library](plans/FF-005-basic-and-advanced-examples/spec.md) | Human Owner accepted exact r1 A on 2026-11-04 after QA2 passed AC01–AC12. QA1 history and the old hold_ack limit remain; generated resources were closed out and original evidence retained. Later capability and field gates stay separate. [Development](plans/FF-005-basic-and-advanced-examples/tasks.md); [Verification](plans/FF-005-basic-and-advanced-examples/checklist.md). This preserves the FF-005 acceptance scope; FF-004 has since advanced independently to r2 A, as indexed below. |
| FF-004 | `owner_accepted` (r2 A) | [Per-PLC JSON catalog and multi-PLC calls](plans/FF-004-plc-json-catalog-and-multi-plc/spec.md) | The Human Owner accepted exact r2 A on 2026-11-10 after QA3 passed AC01–AC14 on macOS arm64 loopback. Driver limits and earlier QA failures remain recorded. Field validation is a separate gate. [Development](plans/FF-004-plc-json-catalog-and-multi-plc/tasks.md); [Verification](plans/FF-004-plc-json-catalog-and-multi-plc/checklist.md). |
| FF-003 | `dev_blocked` (r2) | [C# runtime and demo01](plans/FF-003-csharp-runtime-demo01/spec.md) | The C# source and macOS arm64 Development checks are complete. The final tree and independent copy each passed 21 tests, and five loopback process scenarios passed. Native Win10 x64 verification awaits a lab host. [Development](plans/FF-003-csharp-runtime-demo01/tasks.md). |
| FF-002 | `qa_passed` (r1) | [User guides and runtime positioning](plans/FF-002-user-guide-and-runtime-positioning/spec.md) | New independent Verification passed the corrected guides and bounded local tutorials; QA1 failure is retained. Human Owner final acceptance is pending; Windows porting, Linux validation, field hosting and long soak remain separate. |
| FF-001 | `qa_passed` (r4) | [r4 Python response validation and dual runtimes](plans/FF-001-dual-runtime-demo01/spec.md) | Actual fresh QA2 passed both versions' local AC01–AC15 and independently closed three Rust QA1 defects; formal/isolated Rust full18 passed. Unchanged Python48 has verified QA1 full evidence plus fresh build/unit/gate/CLI checks. QA1 qa_failed/history retained; Human Owner final acceptance, field and long-running validation pending. |
| ARCH-TOOL-001 | `draft` | [r2 discussion baseline](plans/ARCH-TOOL-001-field-flow-runner/spec.md) | PM documents the independent implementations, long-running requirements and CA relationship; complete r1 retained. The baseline remains unchanged; implementation status belongs to the [FF-001 bundle](plans/FF-001-dual-runtime-demo01/spec.md). |

See the [task catalog](plans/README.md) for existing role documents. Local driver prechecks are recorded separately from full runtime build/startup, field, long-running and deployment acceptance.
