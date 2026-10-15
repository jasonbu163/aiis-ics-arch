# Project Documentation

[中文](README.zh-CN.md)

`docs/` is README-only structural support for durable cross-repository and process documentation. Its lifecycle and status are owned by the root [PLAN](../PLAN.md); this directory does not carry a separate PLAN or task registry.

## Index

| Document | Purpose |
| --- | --- |
| [Multi-Project Development Guide](multi-project-pm.md) | Durable boundaries and governance guidance for Core, reusable modules, and project repositories. |
| [AW Whitepaper and Roadmap](AIIS_AW_Whitepaper_Roadmap_v0.4.md) | CAF/CU/DAA/SMA/CA roles, near-term local configuration and long-term direction; Chinese design text. |
| [AW Runtime Principles and Design](AIIS_AW_Runtime_Design.md) | SQLite, S7 points, APIs, shared Flow Core and device execution/recovery design; no implementation claim. |


## Authority Boundaries

- [`contracts/`](../contracts/) remains the root Core contract hub; contracts are not relocated into `docs/`.
- [`plans/`](../plans/) owns task scope, Development evidence, Verification records, and Human Owner acceptance history.
- Root or module README files and `INITIALIZATION*.md` own stable runtime and initialization guidance. The current task `tasks.md` is the sole copyable command and dynamic evidence surface for a release operation.
- Changes to this directory are tracked by the root PLAN. Do not create `docs/PLAN*.md` or `docs/plans/`.
