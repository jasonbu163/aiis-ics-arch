# Project Documentation

[中文](README.zh-CN.md)

`docs/` is README-only structural support for durable cross-repository and process documentation. Its lifecycle and status are owned by the root [PLAN](../PLAN.md); this directory does not carry a separate PLAN or task registry.

## Index

| Document | Purpose |
| --- | --- |
| [Multi-Project Development Guide](multi-project-pm.md) | Durable boundaries and governance guidance for Core, reusable modules, and project repositories. |
| [Acquisition data module guide](acquisition-data-guide.zh-CN.md) | Chinese guide to source registration, sample reporting, backend storage and reads for DAA and third parties. |
| [Generic Plan/Performance task workflow discussion](generic-task-workflow-discussion.md) · [中文](generic-task-workflow-discussion.zh-CN.md) | Discussion baseline, proposals and open questions for MES → CA/FF → PLC → DAA → SMA → Performance → Plan, with workflow/state/ER-style diagrams, project-agreed PLC eligibility, fields, pages and API examples; not an implementation spec or published contract. |
| [Equipment Status and Process Monitoring Discussion](equipment-status-process-monitoring.md) · [中文](equipment-status-process-monitoring.zh-CN.md) | ARCH-OBS-001 r6 review guide to the two value tables and the flow from SMA or third-party submission to storage and display, including [which fields can be omitted or null](equipment-status-process-monitoring.md#third-party-ingest). |
| [AW Whitepaper and Roadmap](AIIS_AW_Whitepaper_Roadmap_v0.4.md) | Roles and phased direction; ARCH-AW-008 aligns the facts-to-business lifecycle without authorizing software. |
| [AW Runtime Principles and Design](AIIS_AW_Runtime_Design.md) | Acquisition, configuration and execution boundaries; anonymous facts integration and separate business acknowledgements; Chinese design text. |
| [DAA Detailed Design](AIIS_DAA_Detailed_Design.md) | Accepted controlled Stage B baseline; Stage C target for immutable dual-SQLite facts, bounded latest-first upload, durable receipts and Backend read/retention requirements. |
| [SMA Detailed Design](AIIS_SMA_Detailed_Design.md) | Current Rust-owned SQLite configuration/pure-preview stage; normal delivery disabled. Cleanup/CU accepted, local configuration QA2 passed pending Owner; GET→POST/history/outbox remain separately scoped. |
| [AW facts integration demand](../contracts/demands/automation-world-facts-integration.md) · [中文](../contracts/demands/automation-world-facts-integration.zh-CN.md) | Proposed common requirements for one anonymous write/two reads, JSON and receipts, per-point latest, safe history, three Shanghai calendar months and permanent business data; demand status remains separate from the implemented providers and their isolated QA. |
| [DS Detailed Design](AIIS_DS_Detailed_Design.md) · [User guide](../automation-world/device-simulator/USER_GUIDE.md) · [Quick flow](../automation-world/device-simulator/USER_GUIDE.md#quick-start) | Create instances/points → confirm → Save draft → Save as version → stopped load → Start, plus [switching/rollback](../automation-world/device-simulator/USER_GUIDE.md#switch-version), single/batch deletion, multi-DB/UDT import and policy editing. The 2026-10-27 DS-001 r1/ARCH-AW-005 r5 acceptance and original DEV/QA history retain their scope; independent QA was waived only for DS-001. Controlled DAA–DS S7→SQLite integration was separately accepted on 2026-10-30; the 2026-10-29 DS draft/version increment retains its DEV/manual-confirmation boundary. Stage C remains separate. |
| [Facts provider](../contracts/published/http-api/plc-facts-v1/README.md) / [business provider](../contracts/published/http-api/business-integration-v1/README.md) | Fixed source contracts and independently passed isolated MySQL A+B scopes; Owner final acceptance, real adoption and DAA/SMA integration pending. |


## Authority Boundaries

- [`contracts/`](../contracts/) remains the root Core contract hub; contracts are not relocated into `docs/`.
- [`plans/`](../plans/) owns task scope, Development evidence, Verification records, and Human Owner acceptance history.
- Root or module README files and `INITIALIZATION*.md` own stable runtime and initialization guidance. The current task `tasks.md` is the sole copyable command and dynamic evidence surface for a release operation.
- Changes to this directory are tracked by the root PLAN. Do not create `docs/PLAN*.md` or `docs/plans/`.
