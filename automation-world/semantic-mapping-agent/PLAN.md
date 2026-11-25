# Semantic Mapping Agent Plan

[中文](PLAN.zh-CN.md)

This PLAN owns SMA task tracking. The [AW PLAN](../PLAN.md) tracks cross-project dependencies; historical ARCH-AW-001 evidence stays at the repository root.

| Task ID | Status | Spec | Latest fact / next gate |
| --- | --- | --- | --- |
| SMA-001 | qa_blocked | [r3 overall implementation](plans/SMA-001-cu-integration-and-scope-cleanup/spec.md) | [QA3 verified 14 isolated criteria for rework-2](plans/SMA-001-cu-integration-and-scope-cleanup/checklist.md#qa3--rework-2-独立复验). AC14 and final acceptance await the Owner. |
| SMA-002 | owner_accepted | [r1 scope cleanup](plans/SMA-002-scope-cleanup/spec.md) | [Independent Verification and Owner closeout](plans/SMA-002-scope-cleanup/checklist.md) fixed candidate af7140357f2a81fa6a2870aed1c2d092dfe4e64ab7795dbf472cf62cdbcff6e2, confirmed no drift and closed B1 after Owner accepted its disclosed impact and limits. QA passed; conditional cleanup acceptance is effective only for that candidate. Incident history and future profile protection remain. |
| SMA-003 | owner_accepted | [r1 CU integration](plans/SMA-003-cu-integration/spec.md) | [Independent Verification and Owner acceptance](plans/SMA-003-cu-integration/checklist.md#owner-acceptance-r1) fixed candidate ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf: QA passed, N1/N2 closed and the Human Owner accepted this CU stage on 2026-11-04. Historical failures and native cross-process persistence limits remain. API/DAA integration and overall SMA completion are separate. |
| SMA-004 | owner_accepted | [r1 local configuration](plans/SMA-004-local-configuration/spec.md) | [Owner accepted on 2026-11-14](plans/SMA-004-local-configuration/checklist.md#owner-acceptance-r1) the candidate that passed independent QA2 for local SQLite configuration, backup/restore and pure preview. Normal delivery remains disabled. |
| SMA-005 | qa_blocked | [r1 page interactions, first batch](plans/SMA-005-page-interaction/spec.md) | The read-only OpenAPI test (#4) and delivery availability (#6) passed independent offline checks. The [verification checklist](plans/SMA-005-page-interaction/checklist.md) awaits Human Owner's GET-only native evidence. |
| SMA-006 | draft | [r1 dialog interactions, first batch](plans/SMA-006-dialog-interaction/spec.md) | Form feedback (#7), draft protection (#8) and scrolling in long dialogs (#9). |
| SMA-007 | qa_passed | [r1 development profile paths](plans/SMA-007-dev-profile-path/spec.md) | [Independent verification](plans/SMA-007-dev-profile-path/checklist.md) passed for the relative and absolute path rules. Human Owner acceptance is pending. |
| SMA-008 | qa_blocked | [r3 manual acquisition round trip](plans/SMA-008-acquisition-data-get/spec.md) | [QA2](plans/SMA-008-acquisition-data-get/checklist.md) passed software and fixture checks for rework-1. Owner-operated dev POST, receipt and history readback remain for AC04. |
| SMA-009 | qa_passed | [r1 workspace and manual loopback UI](plans/SMA-009-workspace-and-loopback-ui/spec.md) | [Independent QA2](plans/SMA-009-workspace-and-loopback-ui/checklist.md) passed first-slice rework-1. Human Owner acceptance is pending. |
| SMA-010 | draft | [r2 one-shot furnace temperature to performance](plans/SMA-010-single-performance-mapping/spec.md) | Earlier one-shot draft. Its furnace-to-performance scenario is an overall acceptance case in SMA-001 r3. |

Implementation order: **SMA-002 → SMA-003 → SMA-004**. All three stages are owner-accepted. The r3 draft defines the proposed overall implementation and acceptance scope.

See the [task catalog](plans/README.md) for the existing role documents and pending stages.
