# TIA Import Core Plan

[中文](PLAN.zh-CN.md)

The [DAA PLAN](../../data-acquisition-agent/PLAN.md) owns this crate's implementation. The [AW PLAN](../../PLAN.md) owns cross-project dependencies. This directory links to the existing DAA task bundle; it does not create a second task or approval chain.

| Task ID | Status | Spec | Latest fact / next gate |
| --- | --- | --- | --- |
| DAA-006 | owner_accepted | [r3](../../data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/spec.md) | Human Owner accepted r3 and the separate DIRECT UI adjustment on 2026-10-20 after independent AC01–AC20 QA. Original blocked history/native limits remain recorded. Accepted source is pinned and temporary resources archived/cleaned; overall B, DS and Stage C gates remain. |

The [README](README.md) describes the actual API, profiles and consumer responsibilities. DS integration and DAA–DS protocol validation require separate approved tasks; this crate's implementation does not close overall DAA Stage B or authorize Stage C.

See the [task catalog](plans/README.md).
