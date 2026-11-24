# SMA Task Catalog

[中文](README.zh-CN.md)

The [SMA PLAN](../PLAN.md) is the current dashboard. Each row below links one authoritative task bundle; role documents are created at their actual lifecycle gates.

| Task ID | Unique spec / relationship | Implementation | Independent verification |
| --- | --- | --- | --- |
| SMA-001 | [r2 overall spec](SMA-001-cu-integration-and-scope-cleanup/spec.md), draft | Root tasks pending. Implementation proceeds through approved children. | Root checklist pending. SMA-002, SMA-003 and SMA-004 r1 are owner-accepted. |
| SMA-002 | [r1 scope cleanup](SMA-002-scope-cleanup/spec.md); approved child of SMA-001 | [tasks](SMA-002-scope-cleanup/tasks.md); developer_handoff for exact candidate af7140357f2a81fa6a2870aed1c2d092dfe4e64ab7795dbf472cf62cdbcff6e2 | [checklist](SMA-002-scope-cleanup/checklist.md); qa_passed and owner_accepted only for the unchanged candidate; B1 Owner handling and incident history retained |
| SMA-003 | [r1 CU integration](SMA-003-cu-integration/spec.md); exact CU stage accepted on 2026-11-04 | [tasks](SMA-003-cu-integration/tasks.md); developer_handoff, candidate ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf | [checklist](SMA-003-cu-integration/checklist.md#owner-acceptance-r1); owner_accepted / qa_passed, N1/N2 closed; historical failures, verification limits and resource-retention boundaries preserved |
| SMA-004 | [r1 local configuration](SMA-004-local-configuration/spec.md), owner_approved | [tasks](SMA-004-local-configuration/tasks.md), rework-1 developer_handoff, 53-file 9d514bc4 candidate | [Checklist](SMA-004-local-configuration/checklist.md) records independent QA2 and Owner acceptance on 2026-11-14, along with the QA1 history and evidence limits. |
| SMA-005 | [r1 page interactions, first batch](SMA-005-page-interaction/spec.md), approved child of SMA-001 | [tasks](SMA-005-page-interaction/tasks.md), developer_handoff for #4 and #6 | [Checklist](SMA-005-page-interaction/checklist.md), qa_blocked pending Human Owner's GET-only native evidence. Independent offline checks passed. |
| SMA-006 | [r1 dialog interactions, first batch](SMA-006-dialog-interaction/spec.md), draft child of SMA-001 | Pending scope approval | Pending Development handoff |
| SMA-007 | [r1 development profile paths](SMA-007-dev-profile-path/spec.md), approved child of SMA-001 | [tasks](SMA-007-dev-profile-path/tasks.md#developer_handoff-rework-2), rework-2 handoff | [Checklist](SMA-007-dev-profile-path/checklist.md), qa_passed for rework-2. Human Owner acceptance is pending. |
| SMA-008 | [r3 manual acquisition round trip](SMA-008-acquisition-data-get/spec.md), approved child of SMA-001 | [Development handoff](SMA-008-acquisition-data-get/tasks.md), rework-1 | [Independent QA2](SMA-008-acquisition-data-get/checklist.md), qa_blocked pending Owner-operated dev POST, receipt and history readback (AC04) |
| SMA-009 | [r1 workspace and manual loopback UI](SMA-009-workspace-and-loopback-ui/spec.md), approved child of SMA-001 | [Development handoff](SMA-009-workspace-and-loopback-ui/tasks.md), rework-1 | [Independent QA2](SMA-009-workspace-and-loopback-ui/checklist.md), qa_passed; Human Owner acceptance pending |

Each child has its own scope approval, verification and acceptance. The overall spec lists goals and dependencies for execution stages 4–6. The original r1 draft survives as a [historical snapshot](SMA-001-cu-integration-and-scope-cleanup/evidence/r1-before-task-split/spec.md).
