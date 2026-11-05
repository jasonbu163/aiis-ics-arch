# SMA Task Catalog

[中文](README.zh-CN.md)

The [SMA PLAN](../PLAN.md) is the current dashboard. Each row below links one authoritative task bundle; role documents are created at their actual lifecycle gates.

| Task ID | Unique spec / relationship | Implementation | Independent verification |
| --- | --- | --- | --- |
| SMA-001 | [r2 overall spec](SMA-001-cu-integration-and-scope-cleanup/spec.md); draft root, SMA-002/SMA-003 accepted and SMA-004 separately approved | Not created; implementation proceeds through approved children | Not created; no overall QA verdict or acceptance |
| SMA-002 | [r1 scope cleanup](SMA-002-scope-cleanup/spec.md); approved child of SMA-001 | [tasks](SMA-002-scope-cleanup/tasks.md); developer_handoff for exact candidate af7140357f2a81fa6a2870aed1c2d092dfe4e64ab7795dbf472cf62cdbcff6e2 | [checklist](SMA-002-scope-cleanup/checklist.md); qa_passed and owner_accepted only for the unchanged candidate; B1 Owner handling and incident history retained |
| SMA-003 | [r1 CU integration](SMA-003-cu-integration/spec.md); exact CU stage accepted on 2026-11-04 | [tasks](SMA-003-cu-integration/tasks.md); developer_handoff, candidate ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf | [checklist](SMA-003-cu-integration/checklist.md#owner-acceptance-r1); owner_accepted / qa_passed, N1/N2 closed; historical failures, verification limits and resource-retention boundaries preserved |
| SMA-004 | [r1 local configuration](SMA-004-local-configuration/spec.md); owner_approved, SMA-003 accepted | [tasks](SMA-004-local-configuration/tasks.md); rework-1 developer_handoff, 53-file 9d514bc4 candidate and six-file delta | [checklist](SMA-004-local-configuration/checklist.md#qa2-r1); QA2 qa_passed, F-QA1-001/002/003 closed; full QA1 failure history and proof limits retained, final Owner acceptance pending |

Parent context does not transfer scope approval, verification or acceptance. Stages after SMA-004 remain goals/dependencies in the overall spec, with no empty bundles. The original unimplemented r1 draft is preserved as a [historical snapshot](SMA-001-cu-integration-and-scope-cleanup/evidence/r1-before-task-split/spec.md), not a second active specification.
