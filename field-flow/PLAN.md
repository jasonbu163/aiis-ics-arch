# Field Flow Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

This directory owns FF task details and source. The repository plan provides cross-project navigation; it does not duplicate the FF task authority.

| Task ID | Aggregate status | Scope | Latest fact / next gate |
| --- | --- | --- | --- |
| FF-005 | `owner_accepted` (r1) | [Basic and advanced example library](plans/FF-005-basic-and-advanced-examples/spec.md) | Human Owner accepted exact r1 A on 2026-11-04 after QA2 passed AC01–AC12. QA1 history and the old hold_ack limit remain; generated resources were closed out and original evidence retained. Later capability and field gates stay separate. [Development](plans/FF-005-basic-and-advanced-examples/tasks.md); [Verification](plans/FF-005-basic-and-advanced-examples/checklist.md). FF-004 r1 unchanged. |
| FF-004 | `qa_passed` (r2 A) | [Per-PLC JSON catalog and multi-PLC calls](plans/FF-004-plc-json-catalog-and-multi-plc/spec.md) | New fresh-context QA passed AC01–AC14 for exact r2 A. Known driver limits and failure history remain recorded. Human Owner final acceptance is pending; later capabilities and field gates stay separate. [Development](plans/FF-004-plc-json-catalog-and-multi-plc/tasks.md); [Verification](plans/FF-004-plc-json-catalog-and-multi-plc/checklist.md). |
| FF-003 | `draft` (r1) | [C# runtime and demo01](plans/FF-003-csharp-runtime-demo01/spec.md) | Actual PM drafted r1 for an independent C# project, local demo01 loop, private SDK preparation and bilingual use/publish guides; exact Human Owner scope approval is pending, with no implementation or QA yet. |
| FF-002 | `qa_passed` (r1) | [User guides and runtime positioning](plans/FF-002-user-guide-and-runtime-positioning/spec.md) | New independent Verification passed the corrected guides and bounded local tutorials; QA1 failure is retained. Human Owner final acceptance is pending; Windows porting, Linux validation, field hosting and long soak remain separate. |
| FF-001 | `qa_passed` (r4) | [r4 Python response validation and dual runtimes](plans/FF-001-dual-runtime-demo01/spec.md) | Actual fresh QA2 passed both versions' local AC01–AC15 and independently closed three Rust QA1 defects; formal/isolated Rust full18 passed. Unchanged Python48 has verified QA1 full evidence plus fresh build/unit/gate/CLI checks. QA1 qa_failed/history retained; Human Owner final acceptance, field and long-running validation pending. |
| ARCH-TOOL-001 | `draft` | [r2 discussion baseline](plans/ARCH-TOOL-001-field-flow-runner/spec.md) | PM documents the independent implementations, long-running requirements and CA relationship; complete r1 retained. The baseline remains unchanged; implementation status belongs to the [FF-001 bundle](plans/FF-001-dual-runtime-demo01/spec.md). |

See the [task catalog](plans/README.md) for existing role documents. Local driver prechecks are recorded separately from full runtime build/startup, field, long-running and deployment acceptance.
