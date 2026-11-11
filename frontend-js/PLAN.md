# Frontend JavaScript Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

## Current baseline

- [ARCH-ACQ-003 r2](../plans/ARCH-ACQ-003-acquisition-data-optional-filters/spec.md): `owner_accepted`. Both dev pages load authorized lists by default, with optional filters and PLC, DB and source columns. Human Owner accepted the verified r2 dev scope on 2026-11-11.

- [ARCH-BE-004 r2](../plans/ARCH-BE-004-energy-price-hourly-history/spec.md): `owner_accepted`; observedAt hourly upsert, daily history and add dialog independently verified, F-001 closed; Human Owner accepted on 2026-10-13 after successful manual use, live data migration separately gated.

- Core pages include login and `system/user`. ARCH-ACQ-002 retired the mapping settings page at `system/dict`. [QA record](../plans/ARCH-ACQ-002-legacy-projection-retirement/checklist.md)
- ARCH-FE-005 r2 adds a top-level Acquisition Data menu with Realtime Data and Acquisition History. QA5 verified both pages' filter alignment after PLC selection, title help and dev reads. Human Owner acceptance is pending. [QA record](../plans/ARCH-FE-005-acquisition-data-module/checklist.md)
- Route, navigation, default entry and locale assembly share the normalized module Registry.
- ARCH-FE-002 adds the approved dashboard/plan pilot with page IDs `dashboard.home` and `plan.list`; remaining business modules require the subsequent 003 migration task.
- [ARCH-FE-001 r3](../plans/ARCH-FE-001-frontend-module-auto-assembly/spec.md): `qa_passed`; the second fresh-context Verification passed r3 and independently closed the first-round findings, with history retained. Human Owner final acceptance and a separate release-version decision remain pending.
- [ARCH-FE-002 r4](../plans/ARCH-FE-002-project-role-access-and-module-pilot/spec.md): `owner_accepted`; r2/r3 QA history is retained. Shared Logo/alignment/glow and host grants for current pages passed independent checks; Human Owner accepted r4 on 2026-10-09. Remaining modules are reserved for 003.
- [ARCH-FE-003 r2](../plans/ARCH-FE-003-remaining-module-manifest-adaptation/spec.md): `owner_accepted`; price page calls auxiliary APIs with local state; checker, 36 tests and isolated build passed independent verification. Human Owner accepted r2 on 2026-10-12 and reported successful env page-access testing; r1 history retained.
- [ARCH-FE-004 r3](../plans/ARCH-FE-004-system-name-env-configuration/spec.md): `owner_accepted`; after independent static verification, Human Owner reported successful testing and accepted the system name/subtitle configuration on 2026-10-10. r1/r2 history and original verification evidence retained.

Detailed UI work requires a separate approved task. This index does not carry a project business backlog.
