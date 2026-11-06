# Automation World Plan

[中文](PLAN.zh-CN.md)

| Task ID | Status | Spec | Latest fact / next gate |
| --- | --- | --- | --- |
| SMA-001 | draft | [r2 overall spec](semantic-mapping-agent/plans/SMA-001-cu-integration-and-scope-cleanup/spec.md) | SMA-002/SMA-003 are owner-accepted. SMA-004 r1 independently passed QA2 after rework and awaits final Owner acceptance. Normal delivery remains closed; see the [SMA PLAN](semantic-mapping-agent/PLAN.md). |
| ARCH-AW-007 | owner_accepted | [r2](../plans/ARCH-AW-007-general-agent-fleet-roadmap/spec.md) | Human Owner accepted exact r2 documents on 2026-10-21 after independent AC01–AC14 QA. DAA, tabular SMA, general CA/internal connectors and future all-kind health remain distinct; first version has no login. Full r1 history/QA retained; evidence archived, two owned temporary roots/49 files cleaned. No code changes or additional tests. |
| ARCH-AW-006 | owner_approved | [r2](../plans/ARCH-AW-006-unified-flow-agent-design/spec.md) | Exact r2 design approved: bulk DAA, tabular SMA/workbench and CA node orchestration/version/context/extensions; first version has no login. Complete r1 retained; 007 r2 owns document implementation, software separately scoped. |
| ARCH-AW-001 | owner_accepted | [r1](../plans/ARCH-AW-001-agent-foundation/spec.md) | CA relocated/frozen; DAA/SMA build and start independently; focused review passed; Human Owner accepted r1 on 2026-10-14; no further tests added. UI and SQLite work remain future tasks. |

CA retains the frozen compatibility baseline; DAA owns continuing acquisition development. Independent facts/business providers passed isolated QA; DAA upload and SMA execution/business integration remain separate. Shared CU and app-local SQLite progress are recorded in the owning plans below. See the [task catalog](plans/README.md).

## Subproject plans

AW tracks overall stages and cross-project dependencies. Each subproject PLAN owns its implementation tasks and links its unique local bundles; historical root bundles remain in place.

[DAA-007 r2](data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) — Human Owner accepted r2 and Stage B within this controlled DS joint-test scope on 2026-10-30 after AC01–AC22 QA and the complete 8590-sample/4295-round reopen comparison. Missing historical checkpoints and unexplained 15:27 actions remain tracked. Configuration/history and original joint profiles are retained; Stage C, automatic-start policy and field validation are separate.

[DAA-006 r3](data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/checklist.md#owner-acceptance-r3) was accepted by the Human Owner on 2026-10-20. Independent AC01–AC20 QA and separate DIRECT UI confirmation remain distinct; prior blocked history and native limits are retained. Accepted source hashes are pinned and task resources archived/cleaned; this acceptance closeout added no tests. Subsequent controlled Stage B acceptance is recorded under DAA-007; earlier DS acceptance remains independent and Stage C separate.

| Project | Owning plan | Current stage |
| --- | --- | --- |
| Semantic Mapping Agent | [SMA PLAN](semantic-mapping-agent/PLAN.md) | SMA-002/SMA-003 accepted; SMA-004 r1 local configuration/pure preview passed independent QA2, final Owner acceptance pending. Three QA1 failures were repaired and independently closed, with history retained. Backend/GET-to-POST and DAA integration remain future work; SMA-001 r2 is draft. |
| Console UI | [CU PLAN](console-ui/PLAN.md) | CU-001–CU-008 are owner-accepted, including grouped/second-level navigation. DAA and SMA adopted CU under their separate accepted tasks; new CA integration remains future work. |
| Device Simulator | [DS PLAN](device-simulator/PLAN.md) | DS-001 r1 and ARCH-AW-005 r5 are owner_accepted as of 2026-10-27. The 2026-10-27 DS/guide/corrections are accepted; the 2026-10-29 draft/version DIRECT increment has DEV self-check and manual confirmation pending; historical QA4 and all failures remain. Independent QA was waived only for DS-001. Acceptance/resource closeout recorded, no added functionality or full QA; Controlled DAA–DS SQLite validation is separately accepted under DAA-007; Stage C remains separate. |
| Data Acquisition Agent | [DAA PLAN](data-acquisition-agent/PLAN.md) | [DAA-002 r2](data-acquisition-agent/plans/DAA-002-local-acquisition-loop/checklist.md#owner-acceptance-r2); [DAA-003 r1](data-acquisition-agent/plans/DAA-003-sqlite-only-startup/checklist.md#owner-acceptance-r1); [DAA-004 r1](data-acquisition-agent/plans/DAA-004-migration-notice-and-source-import-validation/checklist.md#owner-acceptance-r1); [DAA-007 r2](data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) were finally accepted on 2026-10-30; earlier DAA-001/005/006 acceptance remains. Stage B is complete only within this controlled DS joint scope; failures, evidence-availability limits and unexplained actions stay recorded. SQLite startup no longer imports YAML. Configuration/history and joint profiles are retained; Stage C, automatic-start policy and real-field work are separate. |

Backend dependency: [BE-009](../plans/ARCH-BE-009-backend-facts-integration/spec.md) facts and [BE-010](../plans/ARCH-BE-010-anonymous-business-integration/spec.md) typed business providers passed isolated A+B QA. Owner acceptance, actual schema/time adoption, DAA uploader and SMA execution wiring remain separate. Backend-first/DAA-later is the chosen implementation order.
