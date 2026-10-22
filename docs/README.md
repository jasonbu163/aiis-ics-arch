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
| [DS Detailed Design](AIIS_DS_Detailed_Design.md) | Accepted ARCH-AW-004 r2 history with approved ARCH-AW-005 r5 product MVP design: DAA-derived six-page UI, one Rust runtime, typed import/configuration/apply, DS SQLite and automated validation; DEV implementation/evidence and current independent QA/Owner status are recorded in the owning tasks/checklist; DAA-to-SQLite integration is separately gated. |


## Authority Boundaries

- [`contracts/`](../contracts/) remains the root Core contract hub; contracts are not relocated into `docs/`.
- [`plans/`](../plans/) owns task scope, Development evidence, Verification records, and Human Owner acceptance history.
- Root or module README files and `INITIALIZATION*.md` own stable runtime and initialization guidance. The current task `tasks.md` is the sole copyable command and dynamic evidence surface for a release operation.
- Changes to this directory are tracked by the root PLAN. Do not create `docs/PLAN*.md` or `docs/plans/`.
