# Semantic Mapping Agent Plan

[中文](PLAN.zh-CN.md)

This PLAN owns SMA task tracking. The [AW PLAN](../PLAN.md) tracks cross-project dependencies; historical ARCH-AW-001 evidence stays at the repository root.

| Task ID | Status | Spec | Latest fact / next gate |
| --- | --- | --- | --- |
| SMA-001 | draft | [r2 overall spec](plans/SMA-001-cu-integration-and-scope-cleanup/spec.md) | SMA-002/SMA-003 are owner-accepted. SMA-004 r1 passed independent QA2 after bounded rework and awaits final Owner acceptance. Later stages have goals only; the overall spec remains draft. |
| SMA-002 | owner_accepted | [r1 scope cleanup](plans/SMA-002-scope-cleanup/spec.md) | [Independent Verification and Owner closeout](plans/SMA-002-scope-cleanup/checklist.md) fixed candidate af7140357f2a81fa6a2870aed1c2d092dfe4e64ab7795dbf472cf62cdbcff6e2, confirmed no drift and closed B1 after Owner accepted its disclosed impact and limits. QA passed; conditional cleanup acceptance is effective only for that candidate. Incident history and future profile protection remain. |
| SMA-003 | owner_accepted | [r1 CU integration](plans/SMA-003-cu-integration/spec.md) | [Independent Verification and Owner acceptance](plans/SMA-003-cu-integration/checklist.md#owner-acceptance-r1) fixed candidate ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf: QA passed, N1/N2 closed and the Human Owner accepted this CU stage on 2026-11-04. Historical failures and native cross-process persistence limits remain. API/DAA integration and overall SMA completion are separate. |
| SMA-004 | qa_passed | [r1 local configuration](plans/SMA-004-local-configuration/spec.md) | [Independent QA2](plans/SMA-004-local-configuration/checklist.md#qa2-r1) verified 53-file candidate 9d514bc4c71ae3ebb0b634118c86c6f409835f5d8d933b3fab5bccc51fc93676 and closed F-QA1-001/002/003. Native Save As, real-product backup/restore and localized controls passed; unchanged storage/reopen/Rust evidence was rechecked. QA1 failures and proof limits remain. Normal delivery stays closed; final Owner acceptance pending. |

Implementation order: **SMA-002 → SMA-003 → SMA-004**. The first two stages are accepted; SMA-004 passed QA2 and awaits final Owner acceptance. Stages 4–6 remain goals/dependencies only, with no future bundles. These children do not establish overall SMA completion.

See the [task catalog](plans/README.md) for the existing role documents and pending stages.
