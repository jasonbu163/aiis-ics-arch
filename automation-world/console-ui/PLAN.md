# Console UI Plan

[中文](PLAN.zh-CN.md)

This PLAN owns CU implementation tasks. The [AW PLAN](../PLAN.md) owns overall stages and cross-project dependencies.

| Task ID | Status | Spec | Latest fact / next gate |
| --- | --- | --- | --- |
| CU-001 | owner_accepted | [r1](plans/CU-001-workbench-foundation/spec.md) | Workbench and public UI exports delivered; focused verification passed. Human Owner accepted r1 on 2026-10-15; this closeout updates CU status only, with no additional tests. |
| CU-002 | owner_accepted | [r1](plans/CU-002-topbar-utility-controls/spec.md) | Human Owner accepted r1 on 2026-10-16; original independent QA evidence retained. CU-only status closeout, no additional tests. |
| CU-003 | owner_accepted | [r1](plans/CU-003-topbar-height-alignment/spec.md) | Human Owner accepted r1 on 2026-10-16; BACKFILL height alignment and self-check retained, without independent QA. Status closeout only, no additional tests. |
| CU-004 | owner_accepted | [r1](plans/CU-004-page-design-samples/spec.md) | Human Owner accepted r1 on 2026-10-16; original independent QA evidence retained. Status closeout only, no additional tests. |
| CU-005 | owner_accepted | [r1](plans/CU-005-design-profile-editor/spec.md) | Human Owner accepted r1 on 2026-10-16; original independent QA evidence for editing, local drafts and public JSON/CSS generation retained. CU-only status closeout, no additional tests. |
| CU-006 | owner_accepted | [r1](plans/CU-006-live-design-preview/spec.md) | Human Owner accepted r1 on 2026-10-16; original independent QA evidence for color controls and side-by-side live preview retained. CU-only status closeout, no additional tests. |
| CU-007 | owner_accepted | [r1](plans/CU-007-apply-shared-design-profile/spec.md) | Human Owner accepted r1 on 2026-10-16 after confirming shared-style application persists across restart. Original independent QA retained; user-applied card padding of 18 preserved. Status closeout only, no additional application tests. |

CU now contains a lightweight Tauri design workbench and public UI source exports. The old acquisition execution chain has been removed; actual Agent integration remains a separate task.

See the [CU task catalog](plans/README.md). Each task has one CU-owned bundle; historical root task bundles stay in place.
