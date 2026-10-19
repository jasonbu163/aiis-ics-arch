# Data Acquisition Agent Plan

[中文](PLAN.zh-CN.md)

This PLAN owns DAA implementation tasks. The [AW PLAN](../PLAN.md) owns cross-project stages and dependencies. Historical foundation and accepted design bundles remain at their existing root paths.

| Task ID | Status | Spec | Latest fact / next gate |
| --- | --- | --- | --- |
| DAA-001 | owner_accepted | [r1](plans/DAA-001-cu-layout-migration/spec.md) | Human Owner accepted r1 on 2026-10-17 after new fresh Verification passed; F-001/F-002 closed, prior failure history retained. Acceptance covers Stage A layout and existing behavior only; B/C require separate implementation approval. |
| DAA-002 | qa_passed | [r2](plans/DAA-002-local-acquisition-loop/spec.md) | Independent QA4 passed AC01–AC20 for controlled Stage B; F-001–F-004 are closed, with all failure history and 76 original samples retained. Human Owner final acceptance is pending. Default legacy mode remains; Stage C, Backend/SMA, DS integration and real field actions remain excluded. |
| DAA-003 | qa_passed | [r1](plans/DAA-003-sqlite-only-startup/spec.md) | New independent QA2 passed; [checklist](plans/DAA-003-sqlite-only-startup/checklist.md) closes F-001/F-002 and retains QA1 failure history. Ordinary startup uses SQLite only; YAML migrates once to a disabled draft for an empty instance, preserving existing configuration/history. Necessary incremental checks and controlled native save/reopen evidence are verified. Owned test processes/15191 are released, evidence retained; Human Owner final acceptance pending. |
| DAA-004 | qa_passed | [r1](plans/DAA-004-migration-notice-and-source-import-validation/spec.md) | New independent Verification passed AC01–AC08 for the bounded README/UI adjustment and controlled three-point DB/UDT import loop. Operator variation and observation limits are retained; existing configuration/history and the SQLite migration receipt remain protected. Human Owner final acceptance is pending; Stage C and actual TIA/PLC integration remain outside this task. [checklist](plans/DAA-004-migration-notice-and-source-import-validation/checklist.md) |
| DAA-005 | owner_accepted | [r1](plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md) | Human Owner accepted exact DAA-005 r1 on 2026-10-19 after independent QA2 passed AC01–AC13. Acceptance-only closeout preserves original failures and native evidence; no additional tests or implementation changes. [checklist](plans/DAA-005-multi-db-source-import-and-nested-offsets/checklist.md). |

See the [DAA task catalog](plans/README.md). The [ARCH-AW-003 r3 design](../../docs/AIIS_DAA_Detailed_Design.md) is owner-accepted; its design acceptance does not approve implementation. Local acquisition and reliable fact upload remain later independently scoped stages.
