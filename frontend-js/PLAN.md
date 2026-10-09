# Frontend JavaScript Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

## Current baseline

- Core pages: login, system/user and system/dict.
- Route, navigation, default entry and locale assembly share the normalized module Registry.
- ARCH-FE-002 adds the approved dashboard/plan pilot with page IDs `dashboard.home` and `plan.list`; remaining business modules require the subsequent 003 migration task.
- [ARCH-FE-001 r3](../plans/ARCH-FE-001-frontend-module-auto-assembly/spec.md): `developer_handoff`; first QA findings reworked, 15 contract test groups and isolated production build passed. Fresh-context re-verification and Human Owner acceptance remain pending; release version is deferred.
- [ARCH-FE-002 r4](../plans/ARCH-FE-002-project-role-access-and-module-pilot/spec.md): `owner_accepted`; r2/r3 QA history is retained. Shared Logo/alignment/glow and host grants for current pages passed independent checks; Human Owner accepted r4 on 2026-10-09. Remaining modules are reserved for 003.
- [ARCH-FE-004 r1](../plans/ARCH-FE-004-system-name-env-configuration/spec.md): `draft`; bilingual build-time system names share `common.systemTitle` across login, Logo alt and browser title. Exact Human Owner Revision approval pending.

Detailed UI work requires a separate approved task. This index does not carry a project business backlog.
