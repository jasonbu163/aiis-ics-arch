# Project Documentation

[中文](README.zh-CN.md)

`docs/` is README-only structural support for durable cross-repository and process documentation. Its lifecycle and status are owned by the root [PLAN](../PLAN.md); this directory does not carry a separate PLAN or task registry.

## Index

| Document | Purpose |
| --- | --- |
| [Multi-Project Development Guide](multi-project-pm.md) | Durable boundaries and governance guidance for Core, reusable modules, and project repositories. |
| [AW Whitepaper and Roadmap](AIIS_AW_Whitepaper_Roadmap_v0.4.md) | Roles and phased direction; ARCH-AW-008 aligns the facts-to-business lifecycle without authorizing software. |
| [AW Runtime Principles and Design](AIIS_AW_Runtime_Design.md) | Acquisition, configuration and execution boundaries; anonymous facts integration and separate business acknowledgements; Chinese design text. |
| [DAA Detailed Design](AIIS_DAA_Detailed_Design.md) | Accepted controlled Stage B baseline; Stage C target for immutable dual-SQLite facts, bounded latest-first upload, durable receipts and Backend read/retention requirements. |
| [SMA Detailed Design](AIIS_SMA_Detailed_Design.md) | Current Backend-held configuration and staged HTTP mapping; future binding checks, safe history consumption and reliable typed business delivery; no immediate local-store migration. |
| [AW facts integration demand](../contracts/demands/automation-world-facts-integration.md) · [中文](../contracts/demands/automation-world-facts-integration.zh-CN.md) | Proposed common requirements for one anonymous write/two reads, JSON and receipts, per-point latest, safe history, three Shanghai calendar months and permanent business data; not a provider implementation. |
| [DS Detailed Design](AIIS_DS_Detailed_Design.md) · [User guide](../automation-world/device-simulator/USER_GUIDE.md) · [Quick flow](../automation-world/device-simulator/USER_GUIDE.md#quick-start) | Create instances/points → confirm → Save draft → Save as version → stopped load → Start, plus [switching/rollback](../automation-world/device-simulator/USER_GUIDE.md#switch-version), single/batch deletion, multi-DB/UDT import and policy editing. The 2026-10-27 DS-001 r1/ARCH-AW-005 r5 acceptance and original DEV/QA history retain their scope; independent QA was waived only for DS-001. DAA-to-SQLite integration is separately gated; Stage C remains deferred. |


## Authority Boundaries

- [`contracts/`](../contracts/) remains the root Core contract hub; contracts are not relocated into `docs/`.
- [`plans/`](../plans/) owns task scope, Development evidence, Verification records, and Human Owner acceptance history.
- Root or module README files and `INITIALIZATION*.md` own stable runtime and initialization guidance. The current task `tasks.md` is the sole copyable command and dynamic evidence surface for a release operation.
- Changes to this directory are tracked by the root PLAN. Do not create `docs/PLAN*.md` or `docs/plans/`.
