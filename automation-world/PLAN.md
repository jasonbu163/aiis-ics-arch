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
| Console UI | [CU PLAN](console-ui/PLAN.md) | [CU-001 r1](console-ui/plans/CU-001-workbench-foundation/spec.md) is draft; lightweight workbench and public UI source exports await exact scope approval |
