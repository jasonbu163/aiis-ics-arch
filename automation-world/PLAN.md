# Automation World Plan

[中文](PLAN.zh-CN.md)

| Task ID | Status | Spec | Latest fact / next gate |
| --- | --- | --- | --- |
| ARCH-AW-001 | owner_accepted | [r1](../plans/ARCH-AW-001-agent-foundation/spec.md) | CA relocated/frozen; DAA/SMA build and start independently; focused review passed; Human Owner accepted r1 on 2026-10-14; no further tests added. UI and SQLite work remain future tasks. |

CA retains the frozen compatibility baseline; DAA owns continuing acquisition development. S1 APIs, AW fact upload, the business chain, shared UI and SQLite configuration/mapping storage require separate specs. See the [task catalog](plans/README.md).

## Subproject plans

AW tracks overall stages and cross-project dependencies. Each subproject PLAN owns its implementation tasks and links its unique local bundles; historical root bundles remain in place.

| Project | Owning plan | Current stage |
| --- | --- | --- |
| Console UI | [CU PLAN](console-ui/PLAN.md) | CU-001–CU-007 are owner-accepted; public source currently has a flat sidebar. Nested navigation remains a separately scoped CU prerequisite; DAA integration is separate. |
| Data Acquisition Agent | [DAA PLAN](data-acquisition-agent/PLAN.md) | [DAA-001 r1](data-acquisition-agent/plans/DAA-001-cu-layout-migration/spec.md) is owner_accepted as of 2026-10-17. [DAA-002 r2](data-acquisition-agent/plans/DAA-002-local-acquisition-loop/spec.md) is qa_passed. Independent QA4 passed AC01–AC20 for controlled Stage B; F-001–F-004 are closed, with all failure history and 76 original samples retained. Its Human Owner final acceptance remains pending. [DAA-003 r1](data-acquisition-agent/plans/DAA-003-sqlite-only-startup/spec.md) is qa_passed: new independent QA2 confirms F-001/F-002 closed in [checklist](data-acquisition-agent/plans/DAA-003-sqlite-only-startup/checklist.md), with QA1 failure history retained. Ordinary pnpm tauri dev now uses SQLite-only startup; YAML migrates once into a disabled draft only for an empty instance, while existing SQLite configuration/history take precedence. Necessary incremental checks and the controlled ordinary native save/reopen evidence are verified. Owned test processes/15191 are released and evidence retained; Human Owner final acceptance is pending. Stage C/Backend/SMA/DS and real configuration/PLC/production DB/API/field actions remain excluded. [DAA-004 r1](data-acquisition-agent/plans/DAA-004-migration-notice-and-source-import-validation/spec.md) New independent Verification passed AC01–AC08 for the bounded README/UI adjustment and controlled three-point DB/UDT import loop. Operator variation and observation limits are retained; existing configuration/history and the SQLite migration receipt remain protected. Human Owner final acceptance is pending; Stage C and actual TIA/PLC integration remain outside this task. [checklist](data-acquisition-agent/plans/DAA-004-migration-notice-and-source-import-validation/checklist.md). [DAA-005 r1](data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md) owner_accepted; Human Owner accepted exact DAA-005 r1 on 2026-10-19 after independent QA2 passed AC01–AC13. Acceptance-only closeout preserves original failures and native evidence; no additional tests or implementation changes. [checklist](data-acquisition-agent/plans/DAA-005-multi-db-source-import-and-nested-offsets/checklist.md). |
