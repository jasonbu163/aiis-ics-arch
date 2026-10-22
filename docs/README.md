# Project Documentation

[中文](README.zh-CN.md)

`docs/` is README-only structural support for durable cross-repository and process documentation. Its lifecycle and status are owned by the root [PLAN](../PLAN.md); this directory does not carry a separate PLAN or task registry.

## Index

| Document | Purpose |
| --- | --- |
| [Multi-Project Development Guide](multi-project-pm.md) | Durable boundaries and governance guidance for Core, reusable modules, and project repositories. |
| [AW Whitepaper and Roadmap](AIIS_AW_Whitepaper_Roadmap_v0.4.md) | CAF/CU/DAA/SMA/CA roles, near-term local configuration and long-term direction; Chinese design text. |
| [AW Runtime Principles and Design](AIIS_AW_Runtime_Design.md) | SQLite, S7 points, APIs, shared Flow Core and device execution/recovery design; no implementation claim. |
| [DAA Detailed Design](AIIS_DAA_Detailed_Design.md) | Chinese target design for multi-PLC acquisition, dual SQLite, bounded latest-first replay and a maximum three-calendar-month Backend window; includes CU consumption, workspace/configuration pages, runtime data flows, DB-packet/batch examples and phased implementation; no implementation authorization. |
| [SMA Detailed Design](AIIS_SMA_Detailed_Design.md) | Chinese target design for local form-based bindings, API materials/manual targets, definition checks, transformations, persistent progress/outbox and reliable business API delivery; no implementation authorization. |
| [DS Detailed Design](AIIS_DS_Detailed_Design.md) · [User guide](../automation-world/device-simulator/USER_GUIDE.md) | 004 accepted history and r5 product design; step-by-step manual DB31 then Alpha/Beta import, native images and startup/store guidance. Current custom initial/fixed-value typing issue is disclosed; document verification and Owner acceptance are separate from prior technical QA. DAA-to-SQLite integration remains separately gated. |


## Authority Boundaries

- [`contracts/`](../contracts/) remains the root Core contract hub; contracts are not relocated into `docs/`.
- [`plans/`](../plans/) owns task scope, Development evidence, Verification records, and Human Owner acceptance history.
- Root or module README files and `INITIALIZATION*.md` own stable runtime and initialization guidance. The current task `tasks.md` is the sole copyable command and dynamic evidence surface for a release operation.
- Changes to this directory are tracked by the root PLAN. Do not create `docs/PLAN*.md` or `docs/plans/`.
